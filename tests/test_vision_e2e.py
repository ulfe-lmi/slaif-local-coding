"""Focused, fake-upstream tests for the repository-only vision acceptance support."""

from __future__ import annotations

import json
import os
import tempfile
import threading
import time
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from dataclasses import asdict, replace
from pathlib import Path
from typing import Any, Literal

import httpx
import pytest
import uvicorn

from slaif_local_coding.app import create_app
from slaif_local_coding.config import load_settings
from tests.helpers import vision_e2e_support as vision


def _catalog(path: Path) -> None:
    path.write_text(
        json.dumps(
            {
                "models": [
                    {
                        "slug": vision.VISION_MODEL,
                        "input_modalities": ["text", "image"],
                        "supports_image_detail_original": False,
                        "context_window": 100_000,
                        "max_context_window": 100_000,
                        "supports_parallel_tool_calls": False,
                    }
                ]
            }
        ),
        encoding="utf-8",
    )


def _passing_turn(turn: Literal[1, 2]) -> vision.VisionTurnFacts:
    return vision.VisionTurnFacts(
        turn=turn,
        exit_status=0,
        timed_out=False,
        event_bytes=128,
        event_type_counts={"thread.started": 1, "item.completed": 1},
        tool_calls=1,
        sentinel_passed=True,
        response_success=True,
        resumed_command=turn == 2,
        normalized_argv=("<codex>", "--dangerously-bypass-approvals-and-sandbox"),
    )


def _passing_outbound(turn: Literal[1, 2]) -> vision.VisionBoundaryEvidence:
    label = vision.VISION_FULL_LABEL if turn == 1 else vision.VISION_CROP_LABEL
    return vision.VisionBoundaryEvidence(
        endpoint="/v1/responses",
        turn=turn,
        image_types=("input_image",),
        outgoing_images_seen=1,
        forwarded_labels=(label,),
        forwarded_lengths=(4,),
        forwarded_sha256=("a" * 64,),
        exactly_one_expected_image=True,
        no_unexpected_image=True,
        expected_fixture_match=True,
        body_parsed=True,
        non_image_content_preserved=True,
        governance_content_preserved=True,
        tool_content_preserved=True,
    )


def _passing_facts() -> vision.VisionSessionFacts:
    return vision.VisionSessionFacts(
        first=_passing_turn(1),
        second=_passing_turn(2),
        same_session=True,
        catalog_image_capability=True,
        catalog_detail_original_disabled=True,
        catalog_context_window=100_000,
        catalog_parallel_tools_disabled=True,
        metric_deltas=vision.VisionMetricDeltas(
            turn1_seen=1,
            turn1_removed=0,
            turn2_seen=2,
            turn2_removed=1,
            invocation_1_requests=1,
            invocation_2_requests=1,
        ),
        outbound_facts=(_passing_outbound(1), _passing_outbound(2)),
    )


def _replace_turn(
    facts: vision.VisionSessionFacts, turn: Literal[1, 2], **changes: Any
) -> vision.VisionSessionFacts:
    if turn == 1:
        return replace(facts, first=replace(facts.first, **changes))
    return replace(facts, second=replace(facts.second, **changes))


def _scaled_metric_mismatch(facts: vision.VisionSessionFacts) -> vision.VisionSessionFacts:
    assert facts.metric_deltas is not None
    return replace(
        facts,
        metric_deltas=replace(facts.metric_deltas, turn1_seen=0),
    )


def _invalid_outbound_request(facts: vision.VisionSessionFacts) -> vision.VisionSessionFacts:
    first = replace(facts.outbound_facts[0], expected_fixture_match=False)
    return replace(facts, outbound_facts=(first, facts.outbound_facts[1]))


def _fake_codex(
    path: Path, fixture: vision.VisionFixturePaths, *, final_message: str | None = None
) -> Path:
    token = fixture.sentinel_token
    argv_log = fixture.codex_home / "argv-log.jsonl"
    path.write_text(
        "#!/usr/bin/env python3\n"
        "import json\n"
        "import pathlib\n"
        "import sys\n"
        f"log = pathlib.Path({str(argv_log)!r})\n"
        "if '--version' in sys.argv:\n"
        "    print('codex-cli 0.149.0')\n"
        "    raise SystemExit(0)\n"
        "args = sys.argv[1:]\n"
        "log.open('a', encoding='utf-8').write(json.dumps(args) + '\\n')\n"
        "if '--dangerously-bypass-approvals-and-sandbox' not in args:\n"
        "    raise SystemExit(21)\n"
        "if 'resume' in args:\n"
        "    if '--last' not in args or '--image' not in args:\n"
        "        raise SystemExit(22)\n"
        "else:\n"
        "    if args[args.index('--image') + 1] != "
        f"{str(fixture.full_image.path)!r}:\n"
        "        raise SystemExit(23)\n"
        "output_index = args.index('--output-last-message') + 1\n"
        f"final_message = {final_message!r}\n"
        "if final_message is None:\n"
        f"    final_message = 'SENTINEL-ACK:{token}'\n"
        "pathlib.Path(args[output_index]).write_text(final_message, encoding='utf-8')\n"
        "events = [\n"
        " {'type': 'thread.started', 'thread_id': 'synthetic-session'},\n"
        " {'type': 'item.completed', 'item': {'type': 'command_execution'}},\n"
        f" {{'type': 'item.completed', 'item': {{'type': 'agent_message', "
        "'text': final_message}},\n"
        "]\n"
        "for event in events:\n"
        "    print(json.dumps(event))\n",
        encoding="utf-8",
    )
    path.chmod(0o700)
    return path


def test_vision_fixture_is_deterministic_private_and_catalog_contract_is_exact(
    tmp_path: Path,
    monkeypatch: Any,
) -> None:
    fixture = vision.write_vision_fixture(
        tmp_path, base_url="http://127.0.0.1:18031/v1", api_key_env="UNUSED"
    )
    assert fixture.full_image.sha256 != fixture.crop_image.sha256
    assert fixture.full_image.path.stat().st_mode & 0o777 == 0o600
    assert fixture.crop_image.path.stat().st_mode & 0o777 == 0o600
    assert fixture.adapter_config.stat().st_mode & 0o777 == 0o600

    def fake_catalog(_codex_bin: object, destination: Path, *, model: str) -> None:
        assert model == vision.VISION_MODEL
        destination.write_text(
            json.dumps({"models": [{"slug": model, "input_modalities": ["text"]}]}),
            encoding="utf-8",
        )

    monkeypatch.setattr(vision, "write_local_model_catalog", fake_catalog)
    vision.write_vision_model_catalog("unused", fixture.model_catalog)
    assert vision._catalog_facts(fixture.model_catalog) == (True, True, 100_000, True)
    assert fixture.sentinel_token not in fixture.codex_config.read_text(encoding="utf-8")
    dependency = (fixture.repository / "GOVERNANCE-DEPENDENCY.md").read_text(encoding="utf-8")
    assert "Output only the prescribed sentinel bytes." in dependency
    assert "Do not add quotes, backticks, Markdown, code fences, punctuation, spaces," in dependency
    assert fixture.sentinel_token in dependency
    assert fixture.sentinel_token not in vision._vision_prompt(1)
    assert fixture.sentinel_token not in fixture.model_catalog.read_text(encoding="utf-8")


@pytest.mark.asyncio
async def test_outbound_recorder_is_wired_to_create_app_and_proves_newest_crop(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    fixture = vision.write_vision_fixture(
        tmp_path, base_url="http://127.0.0.1:18031/v1", api_key_env="UNUSED"
    )
    monkeypatch.setenv("UNUSED", "test-only-secret")
    monkeypatch.setenv("QWEN3090_API_KEY", "test-only-secret")
    settings = load_settings(fixture.adapter_config)
    full = vision._data_url(fixture.full_image.path)
    crop = vision._data_url(fixture.crop_image.path)
    governance = {
        "type": "input_text",
        "text": "GOVERNANCE-DEPENDENCY.md FINAL_RESPONSE_EXACTLY",
    }
    tool_definition = {"type": "function", "name": "read", "parameters": {}}
    tool_call = {"type": "function_call", "call_id": "fixed", "name": "read"}
    tool_output = {"type": "function_call_output", "call_id": "fixed", "output": "fixed"}
    turn_one = {
        "model": vision.VISION_MODEL,
        "input": [
            {
                "role": "user",
                "content": [governance, {"type": "input_image", "image_url": full}],
            }
        ],
        "tools": [tool_definition],
    }
    turn_two = {
        "model": vision.VISION_MODEL,
        "input": [
            {"role": "user", "content": [governance, {"type": "input_image", "image_url": full}]},
            {"role": "user", "content": [{"type": "input_image", "image_url": crop}]},
            tool_call,
            tool_output,
        ],
        "tools": [tool_definition],
    }

    upstream_calls = 0
    compiler_calls = 0

    async def upstream(request: httpx.Request) -> httpx.Response:
        nonlocal upstream_calls, compiler_calls
        if request.url.path == "/v1/chat/completions":
            compiler_calls += 1
            return httpx.Response(500)
        assert request.url.path == "/v1/responses"
        upstream_calls += 1
        body = json.loads(await request.aread())
        assert body["model"] == vision.VISION_MODEL
        assert "GOVERNANCE-DEPENDENCY.md" in json.dumps(body)
        assert any(item.get("type") == "function" for item in body["tools"])
        return httpx.Response(200, json={"id": "fake-upstream"})

    recorder = vision.VisionOutboundRecorder(fixture, httpx.MockTransport(upstream))
    recorder.expect_preserved_content(1, turn_one)
    recorder.expect_preserved_content(1, turn_one)
    recorder.expect_preserved_content(2, turn_two)
    recorder.expect_preserved_content(2, turn_two)
    app = create_app(settings, recorder)
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://adapter.test"
    ) as client:
        before = (await client.get("/metrics")).text
        compiler_response = await recorder.handle_async_request(
            httpx.Request(
                "POST",
                "http://upstream.test/v1/chat/completions",
                json={"model": vision.VISION_MODEL, "messages": []},
            )
        )
        assert compiler_response.status_code == 500
        recorder.begin_phase(1)
        first_response = await client.post("/v1/responses", json=turn_one)
        first_repeat_response = await client.post("/v1/responses", json=turn_one)
        first_facts = recorder.end_phase(1)
        between = (await client.get("/metrics")).text
        recorder.begin_phase(2)
        second_response = await client.post("/v1/responses", json=turn_two)
        second_repeat_response = await client.post("/v1/responses", json=turn_two)
        second_facts = recorder.end_phase(2)
        after = (await client.get("/metrics")).text

    assert (
        first_response.status_code
        == first_repeat_response.status_code
        == second_response.status_code
        == second_repeat_response.status_code
        == 200
    )
    assert upstream_calls == 4
    assert compiler_calls == 1
    facts = recorder.facts
    assert len(facts) == 4
    assert first_facts == facts[:2]
    assert second_facts == facts[2:]
    assert tuple(fact.turn for fact in facts) == (1, 1, 2, 2)
    assert all(fact.endpoint == "/v1/responses" for fact in facts)
    assert all(fact.image_types == ("input_image",) for fact in facts)
    assert all(fact.outgoing_images_seen == 1 for fact in facts)
    assert all(fact.forwarded_labels == ("full_scene",) for fact in first_facts)
    assert all(fact.forwarded_labels == ("right_crop",) for fact in second_facts)
    assert all(fact.forwarded_lengths == (fixture.full_image.byte_length,) for fact in first_facts)
    assert all(fact.forwarded_lengths == (fixture.crop_image.byte_length,) for fact in second_facts)
    assert all(fact.forwarded_sha256 == (fixture.full_image.sha256,) for fact in first_facts)
    assert all(fact.forwarded_sha256 == (fixture.crop_image.sha256,) for fact in second_facts)
    assert all(fact.accepted for fact in facts)
    assert all("data:image/png" not in json.dumps(asdict(fact)) for fact in facts)
    metric_deltas = vision.vision_metric_deltas(before, between, after, phase_counts=(2, 2))
    assert (metric_deltas.turn1_seen, metric_deltas.turn1_removed) == (2, 0)
    assert (metric_deltas.turn2_seen, metric_deltas.turn2_removed) == (4, 2)
    assert metric_deltas.exact


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "case",
    ["zero", "duplicate", "unknown", "wrong_order", "wrong_type", "mismatched"],
)
async def test_outbound_recorder_rejects_invalid_image_evidence(tmp_path: Path, case: str) -> None:
    fixture = vision.write_vision_fixture(
        tmp_path, base_url="http://127.0.0.1:18031/v1", api_key_env="UNUSED"
    )
    full = vision._data_url(fixture.full_image.path)
    crop = vision._data_url(fixture.crop_image.path)
    items: list[dict[str, Any]] = []
    if case == "duplicate":
        items = [
            {"type": "input_image", "image_url": full},
            {"type": "input_image", "image_url": crop},
        ]
    elif case == "unknown":
        items = [{"type": "input_image", "image_url": "data:image/png;base64,AAAA"}]
    elif case == "wrong_order":
        items = [{"type": "input_image", "image_url": crop}]
    elif case == "wrong_type":
        items = [{"type": "image_url", "image_url": {"url": full}}]
    elif case == "mismatched":
        items = [{"type": "input_image", "image_url": "data:image/png;base64,AAEC"}]

    async def upstream(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={})

    recorder = vision.VisionOutboundRecorder(fixture, httpx.MockTransport(upstream))
    request = httpx.Request(
        "POST",
        "http://upstream.test/v1/responses",
        json={"model": vision.VISION_MODEL, "input": items},
    )
    recorder.begin_phase(1)
    response = await recorder.handle_async_request(request)
    recorder.end_phase(1)
    assert response.status_code == 200
    assert len(recorder.facts) == 1
    assert not recorder.facts[0].accepted


@pytest.mark.asyncio
async def test_outbound_recorder_rejects_unattributed_reordered_empty_and_bounded_groups(
    tmp_path: Path,
) -> None:
    fixture = vision.write_vision_fixture(
        tmp_path, base_url="http://127.0.0.1:18031/v1", api_key_env="UNUSED"
    )
    full = vision._data_url(fixture.full_image.path)
    crop = vision._data_url(fixture.crop_image.path)

    async def upstream(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={})

    def request(image: str) -> httpx.Request:
        return httpx.Request(
            "POST",
            "http://upstream.test/v1/responses",
            json={
                "model": vision.VISION_MODEL,
                "input": [{"type": "input_image", "image_url": image}],
            },
        )

    def recorder() -> vision.VisionOutboundRecorder:
        return vision.VisionOutboundRecorder(fixture, httpx.MockTransport(upstream))

    outside = recorder()
    with pytest.raises(ValueError, match="outside_phase"):
        await outside.handle_async_request(request(full))

    empty = recorder()
    with pytest.raises(ValueError, match="empty"):
        empty.begin_phase(1)
        empty.end_phase(1)

    reordered = recorder()
    with pytest.raises(ValueError, match="reordered"):
        reordered.begin_phase(2)
    reordered.begin_phase(1)
    with pytest.raises(ValueError, match="overlap"):
        reordered.begin_phase(2)
    with pytest.raises(ValueError, match="not_active"):
        reordered.end_phase(2)
    await reordered.handle_async_request(request(full))
    reordered.end_phase(1)
    reordered.begin_phase(2)
    with pytest.raises(ValueError, match="empty"):
        reordered.end_phase(2)
    assert reordered.phase_counts is None

    bounded = recorder()
    bounded.begin_phase(1)
    for _ in range(vision.VISION_MAX_MAIN_REQUESTS_PER_INVOCATION):
        await bounded.handle_async_request(request(full))
    with pytest.raises(ValueError, match="bound_exceeded"):
        await bounded.handle_async_request(request(full))
    with pytest.raises(ValueError, match="bound_exceeded"):
        bounded.end_phase(1)

    partial = recorder()
    partial.begin_phase(1)
    await partial.handle_async_request(request(full))
    await partial.handle_async_request(request(crop))
    partial.end_phase(1)
    assert len(partial.phase_facts(1)) == 2
    assert not all(fact.accepted for fact in partial.phase_facts(1))
    assert partial.phase_counts is None


def test_vision_runner_uses_global_yolo_exec_resume_and_exact_model_facts(tmp_path: Path) -> None:
    fixture = vision.write_vision_fixture(
        tmp_path, base_url="http://127.0.0.1:18031/v1", api_key_env="UNUSED"
    )
    _catalog(fixture.model_catalog)
    codex = _fake_codex(tmp_path / "codex", fixture)
    metrics = iter(
        [
            "# TYPE slaif_image_items_total counter\n"
            'slaif_image_items_total{route="qwen38-vision-codex",result="seen"} 0\n'
            'slaif_image_items_total{route="qwen38-vision-codex",result="removed"} 0\n',
            "# TYPE slaif_image_items_total counter\n"
            'slaif_image_items_total{route="qwen38-vision-codex",result="seen"} 1\n'
            'slaif_image_items_total{route="qwen38-vision-codex",result="removed"} 0\n',
            "# TYPE slaif_image_items_total counter\n"
            'slaif_image_items_total{route="qwen38-vision-codex",result="seen"} 3\n'
            'slaif_image_items_total{route="qwen38-vision-codex",result="removed"} 1\n',
        ]
    )
    facts = vision.run_vision_e2e(codex, fixture, metrics_sampler=lambda: next(metrics))
    assert facts.same_session
    assert facts.first.resumed_command is False
    assert facts.second.resumed_command is True
    assert facts.first.normalized_argv[:3] == (
        "<codex>",
        "--dangerously-bypass-approvals-and-sandbox",
        "exec",
    )
    assert facts.second.normalized_argv[3:6] == ("resume", "--last", "--json")
    assert "--ephemeral" not in facts.first.normalized_argv
    assert "--ephemeral" not in facts.second.normalized_argv
    assert facts.metric_deltas is not None and not facts.metric_deltas.exact
    assert fixture.sentinel_token not in json.dumps(asdict(facts))
    vision_turns: tuple[Literal[1, 2], ...] = (1, 2)
    assert all(
        marker not in vision._vision_prompt(turn)
        for marker in ("FULL-SCENE-PROCESSED", "CROP-PROCESSED")
        for turn in vision_turns
    )
    assert all(
        marker not in json.dumps(asdict(facts))
        for marker in ("FULL-SCENE-PROCESSED", "CROP-PROCESSED")
    )
    log = (fixture.codex_home / "argv-log.jsonl").read_text(encoding="utf-8").splitlines()
    assert len(log) == 2
    assert "resume" in log[1] and "--last" in log[1]


@pytest.mark.parametrize(
    ("payload", "expected"),
    [
        ({"tools": [{"type": "function"}]}, True),
        ({"tools": [{"type": "custom"}]}, True),
        ({"tools": [{"type": "tool_search"}]}, True),
        ({"tools": [{"type": "web_search"}]}, True),
        ({"tools": [{"type": "local_shell"}]}, False),
        (
            {
                "tools": [
                    {"type": "function"},
                    {"type": "custom"},
                    {"type": "tool_search"},
                    {"type": "web_search"},
                ]
            },
            True,
        ),
        ({"tools": [{"type": "function", "name": "synthetic", "parameters": {}}]}, True),
        ({"input": [{"type": "function_call"}]}, True),
        ({"input": [{"type": "function_call_output"}]}, True),
        ({"input": [{"type": "custom_tool_call"}]}, True),
        ({"input": [{"type": "custom_tool_call_output"}]}, True),
        ({"input": [{"type": "local_shell_call"}]}, True),
        ({"input": [{"type": "local_shell_call_output"}]}, True),
        ({"input": [{"type": "command_execution"}]}, True),
        ({"input": [{"type": "exec_command"}]}, True),
        ({"input": [{"content": [{"type": "custom_tool_call"}]}]}, True),
        ({"tools": []}, False),
        ({"tools": [{"type": "function_call"}]}, False),
        ({"tools": [{"type": "function"}, {}]}, False),
        ({"tools": [{"type": "custom"}, {"type": "unknown"}]}, False),
        ({"tools": [{"type": "function"}] * 17}, False),
        ({"input": [{"type": "unknown"}]}, False),
        ({"metadata": {"type": "function_call"}}, False),
        ({"input": [{"arguments": {"type": "function_call"}}]}, False),
        ({"input": [{"type": "function_call"}, {"type": "unknown"}]}, True),
        ({"tools": {"type": "function"}}, False),
    ],
)
def test_tool_content_requires_supported_top_level_definitions_or_items(
    payload: dict[str, Any], expected: bool
) -> None:
    assert vision._has_tool_content(payload) is expected


def test_tool_shape_diagnostics_use_fixed_categories_and_bound_nested_scans() -> None:
    payload: dict[str, Any] = {
        "tools": [
            {"type": "function"},
            {"type": "custom"},
            {"type": "tool_search"},
            {"type": "web_search"},
        ],
        "input": [
            {"type": "function_call"},
            {"type": "custom_tool_call_output"},
            {"type": "local_shell_call"},
            {"type": "command_execution"},
            {"type": "exec_command"},
            {"type": "spoofed_unknown"},
        ],
    }
    diagnostics = vision._tool_shape_diagnostics(payload)
    assert diagnostics.has_recognized_content
    assert diagnostics.definition_type_counts == (1, 1, 1, 1, 0, 0)
    assert diagnostics.item_type_counts == (1, 0, 0, 1, 1, 0, 1, 1, 1)

    nested: object = {"content": {"content": {"type": "exec_command"}}}
    for _ in range(vision._MAX_TOOL_SCAN_DEPTH + 1):
        nested = {"content": nested}
    assert not vision._has_tool_content({"input": [nested]})

    serialized = json.dumps(vision.vision_diagnostic_summary(_passing_facts()), sort_keys=True)
    assert "tool_definition_type_counts" in serialized
    assert "tool_item_type_counts" in serialized
    assert "unexpected" in serialized
    for forbidden in ("synthetic", "spoofed_unknown", "arguments"):
        assert forbidden not in serialized


@pytest.mark.parametrize(
    ("content", "accepted", "surrounding_only"),
    [
        ("EXPECTED-ACK", True, False),
        ("EXPECTED-ACK\r", True, True),
        ("EXPECTED-ACK\n", True, True),
        ("EXPECTED-ACK\r\n", True, True),
        ("\r\nEXPECTED-ACK", True, True),
        ("\n\nEXPECTED-ACK", True, True),
        ("\r\nEXPECTED-ACK\n\r", True, True),
        ("\r\nEXPECTED-ACK\r\n", True, True),
        ("EXPECTED-ACK\r\n\n\r", True, True),
        ("EXPECTED-AC\nK", False, False),
        ("EXPECTED-ACK ", False, False),
        ("EXPECTED-ACK\t", False, False),
        ("\u2003EXPECTED-ACK", False, False),
        ("prefix EXPECTED-ACK", False, False),
        ("EXPECTED-ACK suffix", False, False),
        ("```EXPECTED-ACK```", False, False),
        ("MARKER EXPECTED-ACK", False, False),
    ],
)
def test_final_binding_accepts_only_exact_or_surrounding_crlf(
    tmp_path: Path, content: str, accepted: bool, surrounding_only: bool
) -> None:
    expected = "EXPECTED-ACK"
    event = vision._message_evidence(content.encode("utf-8"), expected)
    output = tmp_path / "last-message"
    output.write_bytes(content.encode("utf-8"))
    file = vision._file_final_message_evidence(output, expected)
    assert event.accepted is accepted
    assert file.accepted is accepted
    assert event.surrounding_crlf_only is surrounding_only
    assert file.surrounding_crlf_only is surrounding_only
    assert event.non_whitespace_mismatch is (not accepted and not surrounding_only)
    assert file.non_whitespace_mismatch is (not accepted and not surrounding_only)
    assert (
        event.wrapper_classification
        == file.wrapper_classification
        == ("none" if accepted or surrounding_only else "other_mismatch")
    )
    assert event.sha256 == file.sha256
    assert event.byte_exact_format is (content == "EXPECTED-ACK")
    assert event.binding_effective is accepted
    assert "EXPECTED-ACK" not in repr(event)
    assert "EXPECTED-ACK" not in repr(file)


def test_final_binding_requires_the_last_completed_agent_message(tmp_path: Path) -> None:
    expected = "EXPECTED-ACK"
    stream = iter(
        [
            json.dumps(
                {"type": "item.completed", "item": {"type": "agent_message", "text": expected}}
            ).encode()
            + b"\n",
            json.dumps(
                {
                    "type": "item.completed",
                    "item": {"type": "agent_message", "text": "wrong"},
                }
            ).encode()
            + b"\n",
        ]
    )
    parsed = vision._parse_vision_events(stream, expected=expected)
    event = parsed[4]
    assert event.present
    assert not event.exact_expected
    assert not event.surrounding_crlf_only
    assert event.non_whitespace_mismatch
    assert vision._final_binding_provenance(event, vision._missing_message()) == "mismatch"

    missing = vision._file_final_message_evidence(tmp_path / "missing", expected)
    assert not missing.present
    assert vision._final_binding_provenance(vision._missing_message(), missing) == "missing"


@pytest.mark.parametrize(
    ("event_content", "file_content", "provenance"),
    [
        (b"EXPECTED-ACK", b"mismatch", "event_exact"),
        (b"\n\nEXPECTED-ACK", b"mismatch", "event_surrounding_crlf"),
        (b"mismatch", b"EXPECTED-ACK", "file_exact"),
        (b"mismatch", b"\r\nEXPECTED-ACK\r\n", "file_surrounding_crlf"),
        (b"mismatch", b"other", "mismatch"),
        (None, None, "missing"),
    ],
)
def test_final_binding_provenance_is_event_first_then_file(
    tmp_path: Path,
    event_content: bytes | None,
    file_content: bytes | None,
    provenance: str,
) -> None:
    event = vision._message_evidence(event_content, "EXPECTED-ACK")
    output = tmp_path / "last-message"
    if file_content is not None:
        output.write_bytes(file_content)
    file = vision._file_final_message_evidence(output, "EXPECTED-ACK")
    assert vision._final_binding_provenance(event, file) == provenance


@pytest.mark.parametrize(
    ("content", "wrapper"),
    [
        ("`EXPECTED-ACK`", "inline_backticks"),
        ('"EXPECTED-ACK"', "double_quotes"),
        ("'EXPECTED-ACK'", "single_quotes"),
        ("*EXPECTED-ACK*", "asterisk_wrapper"),
        ("EXPECTED-ACK.", "period_suffix"),
        ("EXPECTED-ACK.\r\n", "period_then_crlf"),
        ("EXPECTED-ACX", "other_mismatch"),
    ],
)
def test_fixed_final_message_wrappers_are_diagnostic_only(content: str, wrapper: str) -> None:
    evidence = vision._message_evidence(content.encode("utf-8"), "EXPECTED-ACK")
    assert evidence.wrapper_classification == wrapper
    assert evidence.accepted is False
    assert evidence.non_whitespace_mismatch is True

    summary = vision._safe_final_message_summary(evidence)
    assert summary["wrapper_classification"] == wrapper
    assert summary["exact_expected"] is False
    assert summary["surrounding_crlf_only"] is False
    assert summary["byte_exact_format"] is False
    assert summary["binding_effective"] is False


@pytest.mark.parametrize(
    ("content", "contains", "offset", "prefix", "suffix", "leading", "trailing"),
    [
        ("EXPECTED-ACK", True, 0, 12, 12, 0, 0),
        ("xxEXPECTED-ACK", True, 2, 0, 12, 2, 0),
        ("EXPECTED-ACKyy", True, 0, 12, 0, 0, 2),
        ("xxEXPECTED-ACKyy", True, 2, 0, 0, 2, 2),
        ("EXPECTED-ACKEXPECTED-ACK", True, None, 12, 12, None, None),
        ("UNRELATED-XX", False, None, 0, 0, None, None),
        ("EXPECTED-ACK.", True, 0, 12, 0, 0, 1),
    ],
)
def test_final_message_relationship_facts_are_bounded_and_diagnostic_only(
    content: str,
    contains: bool,
    offset: int | None,
    prefix: int,
    suffix: int,
    leading: int | None,
    trailing: int | None,
) -> None:
    evidence = vision._message_evidence(content.encode("utf-8"), "EXPECTED-ACK")
    assert evidence.contains_expected is contains
    assert evidence.expected_offset == offset
    assert evidence.common_prefix_bytes == prefix
    assert evidence.common_suffix_bytes == suffix
    assert evidence.leading_extra_bytes == leading
    assert evidence.trailing_extra_bytes == trailing
    assert evidence.accepted is (content == "EXPECTED-ACK")


def test_final_message_relationship_summary_cannot_reconstruct_content() -> None:
    evidence = vision._message_evidence(b"xxEXPECTED-ACKyy", "EXPECTED-ACK")
    summary = vision._safe_final_message_summary(evidence)
    serialized = json.dumps(summary, sort_keys=True)
    assert "EXPECTED-ACK" not in repr(evidence)
    assert "EXPECTED-ACK" not in serialized
    assert summary["contains_expected"] is True
    assert summary["expected_offset"] == 2
    assert summary["leading_extra_bytes"] == 2
    assert summary["trailing_extra_bytes"] == 2
    assert summary["exact_expected"] is False


@pytest.mark.parametrize(
    ("prefix_classification", "content"),
    [
        ("none", b"EXPECTED-ACK"),
        ("leading_crlf", b"\r\nEXPECTED-ACK"),
        ("leading_lf_lf", b"\n\nEXPECTED-ACK"),
        ("leading_cr_cr", b"\r\rEXPECTED-ACK"),
        ("leading_space_space", b"  EXPECTED-ACK"),
        ("leading_tab_tab", b"\t\tEXPECTED-ACK"),
        ("leading_dash_space", b"- EXPECTED-ACK"),
        ("leading_gt_space", b"> EXPECTED-ACK"),
        ("leading_hash_space", b"# EXPECTED-ACK"),
        ("leading_double_asterisk", b"**EXPECTED-ACK"),
        ("leading_double_backtick", b"``EXPECTED-ACK"),
        ("leading_double_quote", b'""EXPECTED-ACK'),
        ("leading_open_paren_space", b"( EXPECTED-ACK"),
        ("other_two_byte_prefix", b"!?EXPECTED-ACK"),
    ],
)
def test_two_byte_prefix_classification_is_closed_and_event_file_parity(
    tmp_path: Path, prefix_classification: str, content: bytes
) -> None:
    expected = "EXPECTED-ACK"
    event = vision._message_evidence(content, expected)
    output = tmp_path / "last-message"
    output.write_bytes(content)
    file = vision._file_final_message_evidence(output, expected)

    assert event.prefix_classification == file.prefix_classification == prefix_classification
    assert event.contains_expected and event.expected_offset in {0, 2}
    assert event.trailing_extra_bytes == 0
    assert event.accepted is (
        prefix_classification in {"none", "leading_crlf", "leading_lf_lf", "leading_cr_cr"}
    )
    assert file.accepted is event.accepted
    assert event.byte_exact_format is (prefix_classification == "none")
    assert event.prefix_classification in vision._FINAL_MESSAGE_PREFIXES
    assert file.prefix_classification in vision._FINAL_MESSAGE_PREFIXES
    assert "EXPECTED-ACK" not in repr(event)
    assert "EXPECTED-ACK" not in repr(file)
    serialized = json.dumps(vision._safe_final_message_summary(event), sort_keys=True)
    assert "EXPECTED-ACK" not in serialized
    assert "!?" not in serialized


@pytest.mark.parametrize(
    "content",
    [
        None,
        b"EXPECTED-ACK\r\n",
        b"xEXPECTED-ACK",
        b"xxEXPECTED-ACKyy",
        b"EXPECTED-ACKE XPECTED-ACK",
        b"UNRELATED-XX",
    ],
)
def test_two_byte_prefix_classification_is_not_applicable_without_exact_relation(
    tmp_path: Path, content: bytes | None
) -> None:
    expected = "EXPECTED-ACK"
    event = vision._message_evidence(content, expected)
    output = tmp_path / "last-message"
    if content is not None:
        output.write_bytes(content)
    file = vision._file_final_message_evidence(output, expected)

    assert event.prefix_classification == file.prefix_classification == "not_applicable"
    assert event.accepted is (event.exact_expected or event.surrounding_crlf_only)
    assert file.accepted is (file.exact_expected or file.surrounding_crlf_only)
    assert event.prefix_classification in vision._FINAL_MESSAGE_PREFIXES
    assert file.prefix_classification in vision._FINAL_MESSAGE_PREFIXES


def test_two_byte_prefix_classification_summary_is_fixed_shape_and_private() -> None:
    assert set(vision._FINAL_MESSAGE_PREFIXES) == {
        "none",
        "leading_crlf",
        "leading_lf_lf",
        "leading_cr_cr",
        "leading_space_space",
        "leading_tab_tab",
        "leading_dash_space",
        "leading_gt_space",
        "leading_hash_space",
        "leading_double_asterisk",
        "leading_double_backtick",
        "leading_double_quote",
        "leading_open_paren_space",
        "other_two_byte_prefix",
        "not_applicable",
    }
    evidence = vision._message_evidence(b"!?EXPECTED-ACK", "EXPECTED-ACK")
    summary = vision._safe_final_message_summary(evidence)
    serialized = json.dumps(summary, sort_keys=True)
    assert summary["prefix_classification"] == "other_two_byte_prefix"
    assert "EXPECTED-ACK" not in serialized
    assert "!?" not in serialized
    assert "prefix" in serialized


@pytest.mark.parametrize("include_sentinel", [False, True])
def test_marker_like_or_marker_plus_sentinel_output_cannot_pass_exact_binding(
    tmp_path: Path, include_sentinel: bool
) -> None:
    fixture = vision.write_vision_fixture(
        tmp_path, base_url="http://127.0.0.1:18031/v1", api_key_env="UNUSED"
    )
    _catalog(fixture.model_catalog)
    final_message = "FULL-SCENE-PROCESSED"
    if include_sentinel:
        final_message += f" SENTINEL-ACK:{fixture.sentinel_token}"
    codex = _fake_codex(tmp_path / "codex", fixture, final_message=final_message)
    facts = vision.run_vision_e2e(codex, fixture)
    assert facts.first.sentinel_passed is False
    assert facts.second.sentinel_passed is False
    assert facts.first.response_success is False
    assert facts.second.response_success is False


@pytest.mark.parametrize(
    ("label", "mutate"),
    [
        ("session_mismatch", lambda facts: replace(facts, same_session=False)),
        (
            "catalog_image_capability",
            lambda facts: replace(facts, catalog_image_capability=False),
        ),
        (
            "catalog_detail_original",
            lambda facts: replace(facts, catalog_detail_original_disabled=False),
        ),
        (
            "catalog_context_window",
            lambda facts: replace(facts, catalog_context_window=None),
        ),
        (
            "catalog_parallel_tools",
            lambda facts: replace(facts, catalog_parallel_tools_disabled=False),
        ),
        (
            "turn1_exit",
            lambda facts: _replace_turn(facts, 1, exit_status=1, response_success=False),
        ),
        (
            "turn1_timeout",
            lambda facts: _replace_turn(facts, 1, timed_out=True, response_success=False),
        ),
        (
            "turn1_events",
            lambda facts: _replace_turn(facts, 1, event_bytes=0, response_success=False),
        ),
        (
            "turn1_tool",
            lambda facts: _replace_turn(facts, 1, tool_calls=0, response_success=False),
        ),
        (
            "turn1_binding_effective",
            lambda facts: _replace_turn(facts, 1, sentinel_passed=False, response_success=False),
        ),
        (
            "turn2_exit",
            lambda facts: _replace_turn(facts, 2, exit_status=1, response_success=False),
        ),
        (
            "turn2_timeout",
            lambda facts: _replace_turn(facts, 2, timed_out=True, response_success=False),
        ),
        (
            "turn2_events",
            lambda facts: _replace_turn(facts, 2, event_bytes=0, response_success=False),
        ),
        (
            "turn2_tool",
            lambda facts: _replace_turn(facts, 2, tool_calls=0, response_success=False),
        ),
        (
            "turn2_binding_effective",
            lambda facts: _replace_turn(facts, 2, sentinel_passed=False, response_success=False),
        ),
        ("metrics_missing", lambda facts: replace(facts, metric_deltas=None)),
        ("metrics_scaled_mismatch", _scaled_metric_mismatch),
        (
            "outbound_phase_grouping",
            lambda facts: replace(facts, outbound_facts=tuple(reversed(facts.outbound_facts))),
        ),
        ("outbound_request_invalid", _invalid_outbound_request),
    ],
)
def test_vision_failure_reasons_cover_each_predicate(
    label: str, mutate: Callable[[vision.VisionSessionFacts], vision.VisionSessionFacts]
) -> None:
    baseline = _passing_facts()
    assert vision.vision_failure_reasons(baseline) == ()
    assert baseline.successful and baseline.outbound_successful

    altered = mutate(baseline)
    reasons = vision.vision_failure_reasons(altered)
    assert label in reasons
    assert all(reason in vision.VISION_REASON_LABELS for reason in reasons)
    assert reasons == tuple(reason for reason in vision.VISION_REASON_LABELS if reason in reasons)
    assert (not reasons) == (altered.successful and altered.outbound_successful)


def test_vision_diagnostic_summary_excludes_ephemeral_and_raw_values() -> None:
    baseline = _passing_facts()
    unsafe_first = replace(
        baseline.first,
        normalized_argv=(
            "https://private.example/secret",
            "prompt text",
            "source text",
            "tool output",
            "Bearer credential-value",
            "SENTINEL-ACK:ephemeral-sentinel",
        ),
        event_type_counts={"thread.started": 1, "raw-response-content": 1},
    )
    unsafe_outbound = replace(
        baseline.outbound_facts[0],
        image_types=("data:image/png;base64,raw-image",),
        forwarded_labels=("prompt/source/tool text",),
        forwarded_lengths=(99_999_999_999,),
        forwarded_sha256=("not-a-sha256",),
    )
    facts = replace(
        baseline,
        first=unsafe_first,
        outbound_facts=(unsafe_outbound, baseline.outbound_facts[1]),
    )

    summary = vision.vision_diagnostic_summary(facts)
    serialized = json.dumps(summary, sort_keys=True)
    for forbidden in (
        "private.example",
        "prompt text",
        "source text",
        "tool output",
        "Bearer credential-value",
        "ephemeral-sentinel",
        "raw-response-content",
        "data:image/png;base64,raw-image",
        "prompt/source/tool text",
        "not-a-sha256",
    ):
        assert forbidden not in serialized
    assert "unexpected" in serialized
    assert summary["reasons"] == ("outbound_request_invalid",)


def test_vision_metric_deltas_are_exact_and_bounded() -> None:
    before = (
        "# TYPE slaif_image_items_total counter\n"
        'slaif_image_items_total{route="qwen38-vision-codex",result="seen"} 4\n'
        'slaif_image_items_total{route="qwen38-vision-codex",result="removed"} 2\n'
    )
    between = before.replace('result="seen"} 4', 'result="seen"} 5')
    after = between.replace('result="seen"} 5', 'result="seen"} 7').replace(
        'result="removed"} 2', 'result="removed"} 3'
    )
    deltas = vision.vision_metric_deltas(before, between, after, phase_counts=(1, 1))
    assert deltas.exact


@contextmanager
def _running_wired_candidate(
    fixture: vision.VisionFixturePaths, recorder: vision.VisionOutboundRecorder
) -> Iterator[None]:
    """Run the real app with the acceptance recorder on repository port 18031."""
    settings = load_settings(fixture.adapter_config)
    app = create_app(settings, recorder)
    server = uvicorn.Server(
        uvicorn.Config(
            app,
            host="127.0.0.1",
            port=18031,
            log_level="warning",
            access_log=False,
        )
    )
    thread = threading.Thread(target=server.run, name="vision-acceptance-candidate", daemon=True)
    thread.start()
    try:
        with httpx.Client(base_url="http://127.0.0.1:18031", timeout=5) as client:
            for _ in range(60):
                if not thread.is_alive():
                    raise AssertionError("candidate_adapter_exited")
                try:
                    if client.get("/healthz").status_code == 200:
                        break
                except httpx.HTTPError:
                    pass
                time.sleep(0.25)
            else:
                raise AssertionError("candidate_adapter_not_ready")
        yield
    finally:
        server.should_exit = True
        thread.join(timeout=15)
        if thread.is_alive():
            server.force_exit = True
            thread.join(timeout=5)
        if thread.is_alive():
            raise AssertionError("candidate_adapter_did_not_stop")


@pytest.mark.skipif(
    os.getenv("SLAIF_VISION_ACCEPTANCE") != "1",
    reason="human must activate the mutually exclusive protected vision fixture",
)
def test_live_vision_exec_resume_acceptance() -> None:
    """Run only after the human-approved vision unit is active on protected 18020."""
    codex_bin = os.environ.get("CODEX_BIN", "codex")
    with tempfile.TemporaryDirectory(prefix="slaif-vision-acceptance-") as temporary:
        fixture = vision.write_vision_fixture(
            Path(temporary), base_url="http://127.0.0.1:18031/v1", api_key_env="QWEN3090_API_KEY"
        )
        vision.write_vision_model_catalog(codex_bin, fixture.model_catalog)
        recorder = vision.VisionOutboundRecorder(fixture, httpx.AsyncHTTPTransport(retries=0))
        with _running_wired_candidate(fixture, recorder):
            with httpx.Client(base_url="http://127.0.0.1:18031", timeout=5) as client:
                facts = vision.run_vision_e2e(
                    codex_bin,
                    fixture,
                    metrics_sampler=lambda: client.get("/metrics").text,
                    outbound_recorder=recorder,
                )
        assert vision.vision_failure_reasons(facts) == (), json.dumps(
            vision.vision_diagnostic_summary(facts), sort_keys=True
        )
        assert len(recorder.facts) == sum(recorder.phase_counts or ())
        assert recorder.phase_counts is not None
        assert all(
            1 <= count <= vision.VISION_MAX_MAIN_REQUESTS_PER_INVOCATION
            for count in recorder.phase_counts
        )
        with httpx.Client(base_url="http://127.0.0.1:18031", timeout=1) as client:
            with pytest.raises(httpx.HTTPError):
                client.get("/healthz")

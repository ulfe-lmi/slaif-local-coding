"""Focused, fake-upstream tests for the repository-only vision acceptance support."""

from __future__ import annotations

import json
import os
import tempfile
import threading
import time
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import asdict
from pathlib import Path
from typing import Any

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


def _fake_codex(path: Path, fixture: vision.VisionFixturePaths) -> Path:
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
        f"    marker = 'CROP-PROCESSED'\n"
        "else:\n"
        "    if args[args.index('--image') + 1] != "
        f"{str(fixture.full_image.path)!r}:\n"
        "        raise SystemExit(23)\n"
        f"    marker = 'FULL-SCENE-PROCESSED'\n"
        "output_index = args.index('--output-last-message') + 1\n"
        f"pathlib.Path(args[output_index]).write_text('SENTINEL-ACK:{token}', encoding='utf-8')\n"
        "events = [\n"
        " {'type': 'thread.started', 'thread_id': 'synthetic-session'},\n"
        " {'type': 'item.completed', 'item': {'type': 'command_execution'}},\n"
        " {'type': 'item.completed', 'item': {'type': 'agent_message', 'text': marker}},\n"
        f" {{'type': 'item.completed', 'item': {{'type': 'agent_message', "
        f"'text': 'SENTINEL-ACK:{token}'}}}},\n"
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
        "tools": [tool_call],
    }
    turn_two = {
        "model": vision.VISION_MODEL,
        "input": [
            {"role": "user", "content": [governance, {"type": "input_image", "image_url": full}]},
            {"role": "user", "content": [{"type": "input_image", "image_url": crop}]},
            tool_output,
        ],
        "tools": [tool_call],
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
        assert any(item.get("type") == "function_call" for item in body["tools"])
        return httpx.Response(200, json={"id": "fake-upstream"})

    recorder = vision.VisionOutboundRecorder(fixture, httpx.MockTransport(upstream))
    recorder.expect_preserved_content(1, turn_one)
    recorder.expect_preserved_content(2, turn_two)
    app = create_app(settings, recorder)
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://adapter.test"
    ) as client:
        before = (await client.get("/metrics")).text
        first_response = await client.post("/v1/responses", json=turn_one)
        between = (await client.get("/metrics")).text
        second_response = await client.post("/v1/responses", json=turn_two)
        after = (await client.get("/metrics")).text

    assert first_response.status_code == second_response.status_code == 200
    assert upstream_calls == 2
    assert compiler_calls == 0
    facts = recorder.facts
    assert len(facts) == 2
    first, second = facts
    assert first.endpoint == second.endpoint == "/v1/responses"
    assert first.turn == 1 and second.turn == 2
    assert first.image_types == second.image_types == ("input_image",)
    assert first.outgoing_images_seen == second.outgoing_images_seen == 1
    assert first.forwarded_labels == ("full_scene",)
    assert second.forwarded_labels == ("right_crop",)
    assert first.forwarded_lengths == (fixture.full_image.byte_length,)
    assert second.forwarded_lengths == (fixture.crop_image.byte_length,)
    assert first.forwarded_sha256 == (fixture.full_image.sha256,)
    assert second.forwarded_sha256 == (fixture.crop_image.sha256,)
    assert first.accepted and second.accepted
    assert "data:image/png" not in json.dumps(asdict(first))
    assert "data:image/png" not in json.dumps(asdict(second))
    metric_deltas = vision.vision_metric_deltas(before, between, after)
    assert (metric_deltas.turn1_seen, metric_deltas.turn1_removed) == (1, 0)
    assert (metric_deltas.turn2_seen, metric_deltas.turn2_removed) == (2, 1)
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
    response = await recorder.handle_async_request(request)
    assert response.status_code == 200
    assert len(recorder.facts) == 1
    assert not recorder.facts[0].accepted


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
    assert facts.successful
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
    assert facts.metric_deltas is not None and facts.metric_deltas.exact
    assert fixture.sentinel_token not in json.dumps(asdict(facts))
    log = (fixture.codex_home / "argv-log.jsonl").read_text(encoding="utf-8").splitlines()
    assert len(log) == 2
    assert "resume" in log[1] and "--last" in log[1]


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
    deltas = vision.vision_metric_deltas(before, between, after)
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
        assert facts.successful
        assert facts.outbound_successful
        assert len(recorder.facts) == 2
        with httpx.Client(base_url="http://127.0.0.1:18031", timeout=1) as client:
            with pytest.raises(httpx.HTTPError):
                client.get("/healthz")

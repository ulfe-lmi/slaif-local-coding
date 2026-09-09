"""Pure tests for the bounded composed stream evidence contract."""

from __future__ import annotations

import json
import threading
from typing import Any

import httpx
import pytest

from scripts.gateway_accounting_rehearsal import (
    CODEX_FIXTURE_SHA256,
    CODEX_VERSION,
    GATEWAY_APP_TREE_SHA256,
    LOCAL_ROUTE_POLICY,
    OBSERVATION_VERSION,
    _FakeQwenServer,
    _local_implementation_sha,
    _validate_fake_gate,
)
from scripts.local_qwen_provider_differential import SSEFacts
from tests.helpers.acceptance_harness import (
    ACCEPTANCE_MANIFEST,
    FAKE_RESULT_SCHEMA_KEYS,
    build_obligation_gate,
    make_result,
    projection_for,
    projection_table_safe_dict,
)
from tests.helpers.gateway_accounting_rehearsal import (
    GATEWAY_MAIN_SHA,
    STREAM_FAILURE_ORDER,
    ComposedStreamFacts,
    build_composed_stream_facts,
)


def _event(payload: dict[str, object]) -> bytes:
    return b"data: " + json.dumps(payload, separators=(",", ":")).encode() + b"\n\n"


def _created(response_id: str = "response-1") -> bytes:
    return _event({"type": "response.created", "response": {"id": response_id}})


def _completed(
    *,
    response_id: str = "response-1",
    status: str = "completed",
    output: object = None,
    usage: object = None,
) -> bytes:
    if output is None:
        output = []
    if usage is None:
        usage = {"input_tokens": 3, "output_tokens": 2, "total_tokens": 5}
    return _event(
        {
            "type": "response.completed",
            "response": {
                "id": response_id,
                "status": status,
                "output": output,
                "usage": usage,
            },
        }
    )


def _parsed(chunks: tuple[bytes, ...], *, finish: bool = True) -> SSEFacts:
    facts = SSEFacts()
    for chunk in chunks:
        facts.consume(chunk)
    if finish:
        facts.finish()
    return facts


def _valid_sse(*, finish: bool = True) -> SSEFacts:
    stream = _created() + _event({"type": "response.reasoning_text.delta"}) + _completed()
    return _parsed(
        tuple(stream[index : index + 7] for index in range(0, len(stream), 7)), finish=finish
    )


def _facts(
    *,
    sse: SSEFacts | None = None,
    status: int | None = 200,
    content_type: str | None = "text/event-stream",
    timing: dict[str, str] | None = None,
    **kwargs: Any,
) -> ComposedStreamFacts:
    options: dict[str, Any] = {
        "status": status,
        "content_type": content_type,
        "timing": (
            {
                "response_headers": "0-9ms",
                "first_sse_bytes": "10-49ms",
                "terminal_completion": "50-99ms",
                "normal_close": "100-249ms",
            }
            if timing is None
            else timing
        ),
        "sse": sse or _valid_sse(),
        "chunk_count": 3,
        "local_request_delta": 1,
        "local_stream_duration_delta": 1,
        "local_failure_delta": 0,
        "local_upstream_status_class": "2xx",
        "local_stream_duration_bucket": "100-249ms",
        "local_failure_class": "none",
        "local_terminal_observed": True,
        "gateway_reservation_terminal": True,
        "gateway_ledger_terminal": True,
        "provider_boundary_observed": True,
        "provider_lifecycle_valid": True,
        "provider_terminal": True,
        "provider_call_count": 1,
    }
    options.update(kwargs)
    return build_composed_stream_facts(**options)


@pytest.mark.parametrize(
    ("name", "expected", "kwargs"),
    (
        ("status", "http_status_non_2xx", {"status": 503}),
        ("content", "content_type_not_sse", {"content_type": "application/json"}),
        ("headers", "response_headers_timing_missing", {"timing": {}}),
        ("bytes", "first_bytes_missing", {"sse": _parsed((), finish=True)}),
        (
            "parse",
            "sse_unparseable",
            {"sse": _parsed((b"data: not-json\n\n",), finish=True)},
        ),
        (
            "vocabulary",
            "event_vocabulary_unrecognized",
            {"sse": _parsed((_event({"type": "response.unknown"}),), finish=True)},
        ),
        (
            "gateway-error",
            "gateway_error_event",
            {"sse": _parsed((_event({"type": "error"}),), finish=True)},
        ),
        (
            "created-missing",
            "response_created_missing_or_duplicate",
            {"sse": _parsed((_completed(),), finish=True)},
        ),
        (
            "created-duplicate",
            "response_created_missing_or_duplicate",
            {"sse": _parsed((_created() + _created() + _completed(),), finish=True)},
        ),
        (
            "completed-missing",
            "response_completed_missing_or_duplicate",
            {"sse": _parsed((_created(),), finish=True)},
        ),
        (
            "completed-duplicate",
            "response_completed_missing_or_duplicate",
            {"sse": _parsed((_created() + _completed() + _completed(),), finish=True)},
        ),
        (
            "terminal-status",
            "terminal_status_or_output_invalid",
            {"sse": _parsed((_created() + _completed(status="failed"),), finish=True)},
        ),
        (
            "terminal-output",
            "terminal_status_or_output_invalid",
            {"sse": _parsed((_created() + _completed(output={}),), finish=True)},
        ),
        (
            "terminal-usage",
            "terminal_usage_invalid",
            {"sse": _parsed((_created() + _completed(usage={"input_tokens": 1}),), finish=True)},
        ),
        (
            "id",
            "response_id_mismatch",
            {"sse": _parsed((_created() + _completed(response_id="response-2"),), finish=True)},
        ),
        (
            "close",
            "normal_close_false",
            {"sse": _valid_sse(finish=False)},
        ),
        (
            "timing",
            "terminal_or_close_timing_missing",
            {"timing": {"response_headers": "0-9ms", "first_sse_bytes": "10-49ms"}},
        ),
        (
            "local",
            "local_upstream_non_2xx_or_failure",
            {"local_upstream_status_class": "5xx", "local_terminal_observed": False},
        ),
        (
            "provider-boundary",
            "provider_boundary_unobserved",
            {"provider_boundary_observed": False},
        ),
        (
            "provider-lifecycle",
            "provider_lifecycle_invalid",
            {"provider_lifecycle_valid": False},
        ),
        (
            "accounting",
            "gateway_accounting_nonterminal",
            {"gateway_ledger_terminal": False},
        ),
        ("pass", "stream_contract_passed", {}),
    ),
)
def test_first_failure_evaluation_is_total_and_ordered(
    name: str, expected: str, kwargs: dict[str, Any]
) -> None:
    _ = name
    facts = _facts(**kwargs)
    assert facts.first_failure == expected
    assert facts.first_failure in STREAM_FAILURE_ORDER


def test_shared_parser_retains_full_reasoning_vocabulary_without_buffering_events() -> None:
    parser = _valid_sse()
    facts = _facts(sse=parser)

    assert facts.first_failure == "stream_contract_passed"
    assert facts.created_count_class == "1"
    assert facts.completed_count_class == "1"
    assert facts.chunk_count_class == "3"
    assert facts.error_field_names == ()


def test_error_projection_is_fixed_and_never_exposes_error_values() -> None:
    parser = _parsed(
        (
            _event(
                {
                    "type": "error",
                    "error": {
                        "code": "private-error-value",
                        "message": "private-message-value",
                        "private_field": "private-field-value",
                    },
                }
            ),
        ),
        finish=True,
    )
    facts = _facts(sse=parser)
    serialized = json.dumps(facts.__dict__, sort_keys=True)

    assert facts.error_field_names == ("code", "message", "type")
    assert facts.error_code_class == "unknown"
    assert "private-error-value" not in serialized
    assert "private-message-value" not in serialized
    assert "private-field-value" not in serialized


def test_owner_mapping_requires_independent_provider_and_validator_facts() -> None:
    gateway_owned = _facts(
        sse=_parsed((_event({"type": "error"}),), finish=True),
        local_terminal_observed=True,
    )
    assert gateway_owned.owner == "gateway_rejected_stream_owner_unresolved"

    gateway_defect = _facts(
        sse=_parsed((_event({"type": "error"}),), finish=True),
        local_terminal_observed=True,
        gateway_validator_contract_valid=True,
        gateway_rejection_code_class="known_conflict",
        gateway_rejection_stage="provider_event_validation",
    )
    assert gateway_defect.owner == "gateway_product_defect"

    local_owned = _facts(local_upstream_status_class="5xx", local_terminal_observed=False)
    assert local_owned.owner == "local_or_provider_owned"

    harness_owned = _facts(
        timing={
            "response_headers": "0-9ms",
            "first_sse_bytes": "10-49ms",
        },
        driver_observation_failure=True,
    )
    assert harness_owned.owner == "acceptance_harness_owned"

    unresolved = _facts(
        sse=_parsed((_event({"type": "response.created"}),), finish=True),
        provider_lifecycle_valid=False,
    )
    assert unresolved.owner == "unresolved"


def test_circular_ledger_or_local_success_cannot_prove_gateway_defect() -> None:
    facts = _facts(
        sse=_parsed((_event({"type": "error"}),), finish=True),
        gateway_validator_contract_valid=False,
        gateway_rejection_code_class="known_conflict",
        gateway_rejection_stage="provider_event_validation",
    )
    assert facts.owner == "gateway_rejected_stream_owner_unresolved"
    assert "gateway_stream_owned" not in facts.owner


def test_owner_vocabulary_is_closed() -> None:
    from tests.helpers.gateway_accounting_rehearsal import STREAM_OWNER_CLASSES

    assert set(STREAM_OWNER_CLASSES) == {
        "stream_contract_passed",
        "gateway_product_defect",
        "gateway_rejected_stream_owner_unresolved",
        "local_or_provider_owned",
        "acceptance_harness_owned",
        "unresolved",
    }


def test_005o_bounded_snapshot_is_unresolved_without_provider_lifecycle() -> None:
    parser = _parsed(
        (
            _event(
                {
                    "type": "error",
                    "error": {"type": "invalid_request_error", "code": "unknown-code"},
                }
            ),
        ),
        finish=True,
    )
    facts = _facts(
        sse=parser,
        local_upstream_status_class="2xx",
        local_failure_class="none",
        local_terminal_observed=True,
        provider_boundary_observed=False,
        provider_lifecycle_valid=False,
        provider_terminal=False,
        gateway_reservation_terminal=True,
        gateway_ledger_terminal=False,
    )
    assert facts.first_failure == "gateway_error_event"
    assert facts.owner == "gateway_rejected_stream_owner_unresolved"
    assert facts.error_field_names == ("code", "type")
    assert facts.error_code_class == "unknown"


def test_strict_fake_function_stream_works_through_loopback_http() -> None:
    server = _FakeQwenServer("synthetic-http-token")
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        url = f"http://127.0.0.1:{server.server_address[1]}/v1/responses"
        initial = {
            "model": "qwen3.8-27b",
            "stream": True,
            "input": [{"type": "message", "role": "user", "content": []}],
            "tools": [{"type": "function", "name": "shell_command"}],
        }
        continuation = {
            "model": "qwen3.8-27b",
            "stream": True,
            "input": [
                {
                    "type": "function_call_output",
                    "call_id": "call_synthetic",
                    "output": "synthetic-result",
                }
            ],
        }
        with httpx.Client(timeout=5) as client:
            first = client.post(
                url, json=initial, headers={"Authorization": "Bearer synthetic-http-token"}
            )
            second = client.post(
                url, json=continuation, headers={"Authorization": "Bearer synthetic-http-token"}
            )
            identified_continuation = dict(continuation)
            identified_continuation["input"] = [
                {
                    "type": "function_call_output",
                    "id": "parser_function_1",
                    "call_id": "call_synthetic",
                    "output": "synthetic-result",
                }
            ]
            identified = client.post(
                url,
                json=identified_continuation,
                headers={"Authorization": "Bearer synthetic-http-token"},
            )
            malformed = dict(continuation)
            malformed["input"] = [
                {
                    "type": "function_call_output",
                    "call_id": "wrong-call",
                    "output": "synthetic-result",
                }
            ]
            rejected = client.post(
                url, json=malformed, headers={"Authorization": "Bearer synthetic-http-token"}
            )
        assert first.status_code == 200
        assert second.status_code == 200
        assert identified.status_code == 200
        assert rejected.status_code == 502
        for response in (first, second, identified):
            frames = response.content.split(b"\n\n")
            assert frames[-1] == b""
            frames = frames[:-1]
            lines = [line for frame in frames for line in frame.splitlines()]
            assert len(lines) == len(frames) * 2
            event_types = [
                lines[index][len(b"event: ") :].decode("ascii") for index in range(0, len(lines), 2)
            ]
            payloads = [
                json.loads(lines[index + 1][len(b"data: ") :]) for index in range(0, len(lines), 2)
            ]
            assert all(lines[index].startswith(b"event: ") for index in range(0, len(lines), 2))
            assert all(lines[index + 1].startswith(b"data: ") for index in range(0, len(lines), 2))
            assert event_types[-1] == "response.completed"
            assert [payload["sequence_number"] for payload in payloads] == list(
                range(len(payloads))
            )
        snapshot = server.snapshot()
        boundary = snapshot["provider_boundary"]
        assert isinstance(boundary, dict)
        assert snapshot["inference_calls"] == 3
        assert boundary["lifecycle_valid"] is True
        assert boundary["function_result_adjacent"] is True
        assert "function_initial" in boundary["request_class_classes"]
        assert "function_continuation" in boundary["request_class_classes"]
        assert "omitted" in boundary["item_id_presence_classes"]
        assert "matching" in boundary["call_id_relation_classes"]
        assert boundary["terminality_valid"] is True
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def test_strict_fake_resume_image_history_starts_a_new_function_turn() -> None:
    server = _FakeQwenServer("synthetic-vision-token")
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        url = f"http://127.0.0.1:{server.server_address[1]}/v1/responses"
        headers = {"Authorization": "Bearer synthetic-vision-token"}
        history_input: list[dict[str, object]] = [
            {"type": "input_image", "image_url": "synthetic-full"},
            {"type": "input_image", "image_url": "synthetic-crop"},
            {
                "type": "function_call_output",
                "call_id": "call_synthetic",
                "output": "synthetic-result",
            },
        ]
        history = {
            "model": "qwen3.8-27b",
            "stream": True,
            "input": history_input,
            "tools": [{"type": "function", "name": "shell_command"}],
        }
        continuation = dict(history)
        continuation["input"] = [
            *history_input,
            {
                "type": "function_call_output",
                "call_id": "call_synthetic",
                "output": "synthetic-result-2",
            },
        ]
        with httpx.Client(timeout=5) as client:
            first = client.post(url, json=history, headers=headers)
            second = client.post(url, json=continuation, headers=headers)
        assert first.status_code == 200
        assert second.status_code == 200
        assert b'"type":"function_call"' in first.content
        assert b'"type":"message"' in second.content
        assert server.snapshot()["inference_calls"] == 2
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def test_protected_mode_requires_complete_same_pin_fake_gate(tmp_path: Any) -> None:
    incomplete = {
        "status": "COMPLETE",
        "provider_target": "fake",
        "gateway_sha": GATEWAY_MAIN_SHA,
        "acceptance_gate": {
            "passed": True,
            "missing": [],
            "first_failure": None,
            "retry_count": 0,
            "results": [{"status": "PASSED"}],
        },
    }
    path = tmp_path / "fake-result.json"
    with pytest.raises(RuntimeError, match="protected_fake_gate_not_complete"):
        path.write_text(json.dumps(incomplete), encoding="utf-8")
        _validate_fake_gate(path)


def test_protected_gate_accepts_only_complete_projected_current_fake_result(
    tmp_path: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        "scripts.gateway_accounting_rehearsal._tested_source_still_valid", lambda _sha: True
    )
    results = [
        make_result(
            item.obligation_id,
            status="PASSED",
            observed=True,
            relationship=projection_for(item.obligation_id).relationship,
            count=2,
            version=CODEX_VERSION if item.obligation_id.startswith("C1") else None,
        )
        for item in ACCEPTANCE_MANIFEST
        if item.mode in {"both", "fake"}
    ]
    gate = build_obligation_gate("fake", results).safe_dict()
    observations = {key: True for key in FAKE_RESULT_SCHEMA_KEYS}
    gate["projection_table"] = projection_table_safe_dict(
        observations, {item.obligation_id: "PASSED" for item in results}
    )
    gate["observation_schema_keys"] = FAKE_RESULT_SCHEMA_KEYS
    payload = {
        "status": "COMPLETE",
        "provider_target": "fake",
        "gateway_sha": GATEWAY_MAIN_SHA,
        "candidate_provenance": {
            "implementation_sha": _local_implementation_sha(),
            "tested_worktree_clean": True,
            "local_source": "src/slaif_local_coding",
            "harness_source": "scripts/gateway_accounting_rehearsal.py",
            "route_policy": LOCAL_ROUTE_POLICY,
            "gateway_sha": GATEWAY_MAIN_SHA,
            "gateway_app_tree_sha256": GATEWAY_APP_TREE_SHA256,
            "codex_version": CODEX_VERSION,
            "codex_binary_sha256": CODEX_FIXTURE_SHA256,
            "run_provenance": "fresh_fake_direct_httpx_loopback",
            "observer_version": OBSERVATION_VERSION,
        },
        "runtime_observations": observations,
        "transport_observation": {
            "observer_version": OBSERVATION_VERSION,
            "ready": True,
            "matches_fake_provider": True,
            "inference_attempted_count_class": "2",
            "inference_terminal_valid_count_class": "2",
        },
        "acceptance_gate": gate,
    }
    path = tmp_path / "fake-result.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    _validate_fake_gate(path)

    payload["acceptance_gate"]["results"][1]["obligation_id"] = "C1.1"  # type: ignore[index]
    path.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(RuntimeError, match="protected_fake_gate"):
        _validate_fake_gate(path)

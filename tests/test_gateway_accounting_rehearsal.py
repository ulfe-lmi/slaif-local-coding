"""Pure tests for the bounded composed stream evidence contract."""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import subprocess
import threading
from collections.abc import AsyncIterator
from pathlib import Path
from typing import Any, cast

import httpx
import pytest

from scripts.gateway_accounting_rehearsal import (
    CODEX_FIXTURE_SHA256,
    CODEX_VERSION,
    GATEWAY_APP_TREE_SHA256,
    LOCAL_ROUTE_POLICY,
    OBSERVATION_VERSION,
    ProtectedRuntimeHooks,
    _acceptance_gate,
    _FakeQwenServer,
    _idless_companion_observation,
    _local_implementation_sha,
    _protected_provider_observation,
    _protected_provider_preflight,
    _provider_request_observation,
    _ReturnedCallIDCapture,
    _runtime_observations,
    _select_protected_runtime,
    _tested_source_still_valid,
    _validate_fake_gate,
    run_actual_protected_mode_conformance,
)
from scripts.local_qwen_provider_differential import SSEFacts
from tests.helpers.acceptance_harness import (
    ACCEPTANCE_MANIFEST,
    FAKE_RESULT_SCHEMA_KEYS,
    PROTECTED_MANIFEST_IDS,
    PROTECTED_RESULT_SCHEMA_KEYS,
    BudgetController,
    OperationDispatchPlan,
    PublicRequestBudget,
    RehearsalBudget,
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
from tests.helpers.transport_observer import DirectTransportObserver


def _event(payload: dict[str, object]) -> bytes:
    return b"data: " + json.dumps(payload, separators=(",", ":")).encode() + b"\n\n"


class _ObserverValidator:
    def validate(self, payload: object) -> bool:
        return isinstance(payload, dict) and payload.get("type") in {
            "response.created",
            "response.completed",
        }


def _observer_validator(_request: httpx.Request) -> _ObserverValidator:
    return _ObserverValidator()


class _ObserverStream(httpx.AsyncByteStream):
    def __init__(self, payload: bytes) -> None:
        self.payload = payload

    async def __aiter__(self) -> AsyncIterator[bytes]:
        yield self.payload

    async def aclose(self) -> None:
        return


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


def _observer_frame(event_type: str, payload: dict[str, object]) -> bytes:
    return (
        b"event: "
        + event_type.encode("ascii")
        + b"\n"
        + b"data: "
        + json.dumps(payload, separators=(",", ":")).encode("utf-8")
        + b"\n\n"
    )


def _observer_response(*, call_id: str | None = None) -> bytes:
    output = (
        [{"type": "function_call", "id": "item-real", "call_id": call_id}]
        if call_id is not None
        else [{"type": "message", "id": "item-message"}]
    )
    return b"".join(
        (
            _observer_frame(
                "response.created",
                {
                    "type": "response.created",
                    "response": {"id": "response-real", "status": "in_progress"},
                },
            ),
            _observer_frame(
                "response.completed",
                {
                    "type": "response.completed",
                    "response": {
                        "id": "response-real",
                        "status": "completed",
                        "output": output,
                        "usage": {"input_tokens": 1, "output_tokens": 1, "total_tokens": 2},
                    },
                },
            ),
        )
    )


@pytest.mark.asyncio
async def test_direct_observer_correlates_actual_returned_call_to_idless_continuation() -> None:
    dispatch_plan = (
        OperationDispatchPlan("codex_turn_1", "codex", 1, (("inference", 1),)),
        OperationDispatchPlan("codex_turn_2", "codex", 2, (("inference", 1),)),
    )
    budget = BudgetController(
        RehearsalBudget(
            operation_limits=(
                PublicRequestBudget(1, "codex_turn_1"),
                PublicRequestBudget(2, "codex_turn_2"),
            ),
            dispatch_plan=dispatch_plan,
        )
    )
    assert budget.admit("codex_turn_1", phase="codex", ordinal=1, lifetime_id="codex")
    assert budget.admit("codex_turn_2", phase="codex", ordinal=2, lifetime_id="codex")
    assert budget.activate_operation("codex_turn_1", phase="codex", ordinal=1, lifetime_id="codex")
    responses = iter((_observer_response(call_id="call-real-a"), _observer_response()))

    def transition(
        kind: str, operation: str, _phase: str, _ordinal: int | None, terminal_valid: bool
    ) -> None:
        if kind == "inference" and operation == "codex_turn_1" and terminal_valid:
            assert budget.activate_operation(
                "codex_turn_2", phase="codex", ordinal=2, lifetime_id="codex"
            )

    observer = DirectTransportObserver(
        httpx.MockTransport(
            lambda _request: httpx.Response(
                200,
                headers={"content-type": "text/event-stream"},
                stream=_ObserverStream(next(responses)),
            )
        ),
        validator_factory=_observer_validator,
        validator_source="test",
        budget_controller=budget,
        dispatch_context=budget.dispatch_context,
        request_classifier=_provider_request_observation,
        response_complete_hook=transition,
    )
    metadata = {"session_id": "session-real-a"}
    initial = {
        "model": "synthetic",
        "stream": True,
        "client_metadata": metadata,
        "input": [{"type": "message", "role": "user", "content": []}],
        "tools": [{"type": "function", "name": "non_fixture_tool"}],
    }
    continuation = {
        "model": "synthetic",
        "stream": True,
        "client_metadata": metadata,
        "input": [
            {
                "type": "function_call_output",
                "call_id": "call-real-a",
                "output": "synthetic-result",
            }
        ],
    }
    async with httpx.AsyncClient(transport=observer) as client:
        first = await client.post("http://fake.test/v1/responses", json=initial)
        await first.aread()
        second = await client.post("http://fake.test/v1/responses", json=continuation)
        await second.aread()
    boundary = observer.snapshot()["provider_boundary"]
    assert isinstance(boundary, dict)
    assert boundary["lifecycle_valid"] is True
    assert boundary["function_result_adjacent"] is True
    assert "matching" in boundary["call_id_relation_classes"]
    assert "omitted" in boundary["item_id_presence_classes"]
    assert "initial_owned" in boundary["call_id_relation_classes"]


@pytest.mark.parametrize("chunk_size", (1, 4096))
def test_returned_call_capture_handles_split_and_coalesced_sse(chunk_size: int) -> None:
    payload = {
        "type": "response.completed",
        "response": {
            "id": "response-real",
            "status": "completed",
            "output": [{"type": "function_call", "id": "item-real", "call_id": "call-real"}],
        },
    }
    frame = (
        b"event: response.completed\n"
        + b"data: "
        + json.dumps(payload, separators=(",", ":")).encode()
        + b"\n\n"
    )
    capture = _ReturnedCallIDCapture()
    for offset in range(0, len(frame), chunk_size):
        capture.consume(frame[offset : offset + chunk_size])
    capture.finish()
    assert capture.value == "call-real"


def _companion_records(
    *, item_id_presence: str = "omitted", call_id_relation: str = "matching"
) -> tuple[dict[str, object], ...]:
    context = {
        "dispatch_operation": "identity_replay",
        "dispatch_phase": "codex",
        "dispatch_ordinal": 5,
        "dispatch_lifetime": "identity",
        "dispatched": True,
        "responded": True,
        "completed": True,
        "terminal_valid": True,
        "normal_close": True,
    }
    return (
        {"kind": "inference", "request_class": "function_initial", **context},
        {
            "kind": "inference",
            "request_class": "function_continuation",
            "item_id_presence": item_id_presence,
            "call_id_relation": call_id_relation,
            **context,
        },
    )


@pytest.mark.parametrize(
    ("item_id_presence", "call_id_relation"),
    (
        ("omitted", "matching"),
        ("present", "matching"),
        ("omitted", "mismatched"),
        ("omitted", "missing"),
    ),
)
def test_idless_companion_requires_omission_and_same_call_relationship(
    item_id_presence: str, call_id_relation: str
) -> None:
    before = {"records": ()}
    after = {
        "records": _companion_records(
            item_id_presence=item_id_presence, call_id_relation=call_id_relation
        )
    }
    facts = _idless_companion_observation(
        before,
        after,
        initial_status=200,
        initial_sse_valid=True,
        returned_call_id_present=True,
        continuation_status=200,
        continuation_json_valid=True,
        accounting={
            "two_terminal_reservations": True,
            "zero_pending": True,
            "zero_duplicate_request_ids": True,
        },
    )
    assert facts["passed"] is (item_id_presence == "omitted" and call_id_relation == "matching")


def test_present_only_runtime_facts_do_not_pass_c14() -> None:
    boundary = {
        "call_count_class": "2",
        "lifecycle_valid": True,
        "terminality_valid": True,
        "request_class_classes": ("function_initial", "function_continuation"),
        "call_id_relation_classes": ("matching",),
        "function_result_adjacent": True,
        "independent_from_ledger": True,
    }
    result: dict[str, object] = {
        "provider_target": "protected",
        "provider_observation": {"provider_boundary": boundary},
        "transport_observation": {"provider_boundary_observed": True},
        "codex": {
            "status": "PASSED",
            "provider_inference_call_count": 2,
            "provider_turns_expected": 2,
            "exit_status": 0,
            "command_lifecycle": "success",
            "call_id_same_hmac": True,
            "scope_no_downgrade": True,
        },
    }
    observations = _runtime_observations(result)
    assert observations["provider.idless_continuation_supported"] is False
    gate, _gaps = _acceptance_gate(result)
    rows = cast(list[dict[str, object]], gate["results"])
    c14 = next(row for row in rows if row["obligation_id"] == "C1.4")
    assert c14["status"] == "FAILED"


def test_request_classifier_ignores_type_names_in_ordinary_text() -> None:
    request = httpx.Request(
        "POST",
        "http://provider.test/v1/responses",
        content=json.dumps(
            {
                "input": [
                    {
                        "type": "message",
                        "content": [{"type": "input_text", "text": "function_call_output"}],
                    }
                ]
            }
        ).encode("utf-8"),
    )
    facts = _provider_request_observation(request)
    assert facts["request_class"] == "message"
    assert facts["call_id_relation"] == "unknown"
    assert facts["_function_output_call_id_digests"] == ()


def test_shared_protected_preflight_stops_before_models_after_health_failure() -> None:
    calls: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request.url.path)
        return httpx.Response(503 if request.url.path == "/health" else 200, json={})

    observer = DirectTransportObserver(httpx.MockTransport(handler))
    statuses = asyncio.run(
        _protected_provider_preflight(
            observer,
            "http://provider.test",
            "synthetic-key",
            lambda endpoint: None,
        )
    )
    assert statuses == (503, None)
    assert calls == ["/health"]
    assert observer.snapshot()["other_dispatched_count"] == 1


def test_shared_protected_preflight_counts_both_probe_endpoints() -> None:
    calls: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request.url.path)
        return httpx.Response(200, json={})

    observer = DirectTransportObserver(httpx.MockTransport(handler))
    statuses = asyncio.run(
        _protected_provider_preflight(
            observer,
            "http://provider.test",
            "synthetic-key",
            lambda endpoint: None,
        )
    )
    assert statuses == (200, 200)
    assert calls == ["/health", "/v1/models"]
    assert observer.snapshot()["other_dispatched_count"] == 2


def test_shared_protected_preflight_stops_after_observer_failure() -> None:
    calls: list[str] = []
    observer: DirectTransportObserver

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request.url.path)
        observer.mark_unready()
        return httpx.Response(200, json={})

    observer = DirectTransportObserver(httpx.MockTransport(handler))
    statuses = asyncio.run(
        _protected_provider_preflight(
            observer,
            "http://provider.test",
            "synthetic-key",
            lambda endpoint: None,
        )
    )
    assert statuses == (200, None)
    assert calls == ["/health"]


def test_protected_projection_is_direct_observer_shaped_for_all_runtime_modes() -> None:
    snapshot = {"provider_boundary": {"call_count_class": "2", "lifecycle_valid": True}}
    assert _protected_provider_observation(snapshot) == {
        "provider_boundary": snapshot["provider_boundary"],
        "source": "direct_transport_observer",
        "fake_oracle": "unavailable",
    }


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


def test_protected_acceptance_gate_retains_c54_and_unknown_primary_facts() -> None:
    result: dict[str, object] = {
        "provider_target": "protected",
        "protected_unchanged": {
            "pid": True,
            "start": True,
            "listener": True,
            "worktree_count": True,
        },
        "transport_observation": {
            "ready": False,
            "failure_class": "manual_unready",
            "inference_attempted_count": 2,
            "inference_dispatched_count": 1,
            "inference_responded_count": 0,
            "inference_completed_count": 0,
        },
    }
    observations = _runtime_observations(result)
    assert tuple(observations) == PROTECTED_RESULT_SCHEMA_KEYS
    gate, _gaps = _acceptance_gate(result)
    rows = cast(list[dict[str, object]], gate["results"])
    assert tuple(row["obligation_id"] for row in rows) == PROTECTED_MANIFEST_IDS
    assert rows[-1]["obligation_id"] == "C5.4"
    assert rows[-1]["status"] == "PASSED"
    assert gate["first_failure"] == "C1.1"
    projection_rows = cast(list[dict[str, object]], gate["projection_table"])
    assert tuple(row["obligation_id"] for row in projection_rows) == PROTECTED_MANIFEST_IDS


def test_actual_protected_conformance_requires_explicit_synthetic_dependencies() -> None:
    args = argparse.Namespace(
        provider_target="fake",
        gateway_root=Path("/synthetic/gateway"),
        gateway_python=Path("/synthetic/python"),
        codex=Path("/synthetic/codex"),
        fake_result=None,
    )
    result = run_actual_protected_mode_conformance(
        args, preflight={"ready": True}, dependencies=None
    )
    assert result["status"] == "FAILED"
    assert result["protected_acceptance"] is False
    assert result["protected_conformance"]["real_protected_access"] is False  # type: ignore[index]
    assert len(result["acceptance_gate"]["results"]) == len(PROTECTED_MANIFEST_IDS)  # type: ignore[index]


def test_actual_shared_runner_protected_preflight_failure_serializes_all_rows_without_access() -> (
    None
):
    accesses: list[str] = []
    args = argparse.Namespace(
        provider_target="fake",
        gateway_root=Path("/synthetic/gateway"),
        gateway_python=Path("/synthetic/python"),
        codex=Path("/synthetic/codex"),
        fake_result=None,
    )

    def host_preflight() -> dict[str, object]:
        accesses.append("host")
        return {"ready": True}

    def main_pid() -> str:
        accesses.append("pid")
        return "synthetic-pid"

    def credential_source(_pid: str) -> str:
        accesses.append("credential")
        return "synthetic-key"

    dependencies = ProtectedRuntimeHooks(
        host_preflight=host_preflight,
        main_pid=main_pid,
        credential_source=credential_source,
        failure_phase="preflight",
    )
    result = run_actual_protected_mode_conformance(
        args, preflight={"ready": True}, dependencies=dependencies
    )
    assert result["status"] == "BLOCKED"
    assert result["protected_acceptance"] is False
    assert accesses == []
    conformance = result["protected_conformance"]
    assert conformance["selected_result_count"] == len(PROTECTED_MANIFEST_IDS)  # type: ignore[index]
    assert conformance["selected_result_disposition_count"] == len(PROTECTED_MANIFEST_IDS)  # type: ignore[index]
    assert conformance["all_selected_rows_serialized"] is True  # type: ignore[index]
    assert conformance["real_protected_access"] is False  # type: ignore[index]


def test_actual_shared_runner_mapping_failure_precedes_credentials_and_provider() -> None:
    accesses: list[str] = []
    args = argparse.Namespace(
        provider_target="fake",
        gateway_root=Path("/synthetic/gateway"),
        gateway_python=Path("/synthetic/python"),
        codex=Path("/synthetic/codex"),
        fake_result=None,
    )

    def credential_source(_pid: str) -> str:
        accesses.append("credential")
        return "synthetic-key"

    def host_preflight() -> dict[str, object]:
        accesses.append("host")
        return {}

    def main_pid() -> str:
        accesses.append("pid")
        return "synthetic-pid"

    result = run_actual_protected_mode_conformance(
        args,
        preflight={"ready": True},
        dependencies=ProtectedRuntimeHooks(
            host_preflight=host_preflight,
            main_pid=main_pid,
            credential_source=credential_source,
            mapping_dependency_check=lambda: False,
        ),
    )
    assert result["status"] == "BLOCKED"
    assert result["protected_acceptance"] is False
    assert result["preflight_mapping_validation"] == "FAILED"
    assert result["credential_hook_calls"] == 0
    assert result["provider_dispatches"] == 0
    assert accesses == []
    accumulator = result["run_accumulator"]
    assert isinstance(accumulator, dict)
    assert accumulator["first_failure"] == "preflight_mapping_dependency_invalid"
    assert all(value == 0 for value in accumulator["counts"].values())
    gate = result["acceptance_gate"]
    assert isinstance(gate, dict)
    assert len(gate["results"]) == len(PROTECTED_MANIFEST_IDS)
    assert result["protected_conformance"]["all_selected_rows_serialized"] is True  # type: ignore[index]


def test_protected_fake_provider_oracle_can_be_disabled() -> None:
    server = _FakeQwenServer("synthetic-no-oracle", oracle_enabled=False)
    snapshot = server.snapshot()
    assert snapshot["provider_oracle_available"] is False
    assert snapshot["provider_boundary"] == {}


def test_actual_protected_selector_uses_explicit_synthetic_boundaries(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[str] = []
    baseline = {
        "vision_active": True,
        "has_18020": True,
        "vision_pid": "23961",
        "vision_start_wall": "Sun 2026-09-06 18:57:26 CEST",
        "vision_restarts": "0",
        "worktree_count": 7,
        "text_inactive": True,
        "has_18021": False,
    }

    def host_preflight() -> dict[str, object]:
        calls.append("host")
        return baseline

    def main_pid() -> str:
        calls.append("pid")
        return "23961"

    def credential_source(_pid: str) -> str:
        calls.append("credential")
        return "synthetic-key"

    monkeypatch.delenv("QWEN3090_API_KEY", raising=False)
    selected, pid, key = _select_protected_runtime(
        ProtectedRuntimeHooks(
            host_preflight=host_preflight,
            main_pid=main_pid,
            credential_source=credential_source,
        )
    )
    assert selected == baseline
    assert pid == "23961"
    assert key == "synthetic-key"
    assert calls == ["host", "pid", "credential"]


def _fixture_git(repo: Path, *arguments: str, input_text: str | None = None) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo), *arguments],
        input=input_text,
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip()


def _source_reuse_fixture(tmp_path: Path) -> tuple[Path, str]:
    repo = tmp_path / "source-reuse"
    repo.mkdir()
    _fixture_git(repo, "init", "--quiet", "--initial-branch=main")
    _fixture_git(repo, "config", "user.email", "synthetic@example.invalid")
    _fixture_git(repo, "config", "user.name", "synthetic")
    (repo / "src").mkdir()
    (repo / "src" / "module.py").write_text("value = 1\n", encoding="utf-8")
    _fixture_git(repo, "add", "src/module.py")
    _fixture_git(repo, "commit", "--quiet", "-m", "implementation")
    tested = _fixture_git(repo, "rev-parse", "HEAD")
    return repo, tested


def _commit_fixture_report(
    repo: Path,
    tested: str,
    *,
    path: str = "oap/reports/other-round.md",
    backticked: bool = False,
) -> str:
    report = repo / path
    report.parent.mkdir(parents=True, exist_ok=True)
    marker = f"`{tested}`" if backticked else tested
    report.write_text(
        f"- Implementation head SHA: {marker}\n- Report publication commit: SELF\n",
        encoding="utf-8",
    )
    _fixture_git(repo, "add", path)
    _fixture_git(repo, "commit", "--quiet", "-m", "oap: publish fixture report")
    return _fixture_git(repo, "rev-parse", "HEAD")


def test_tested_source_reuse_accepts_verified_round_neutral_report_child(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import scripts.gateway_accounting_rehearsal as rehearsal

    repo, tested = _source_reuse_fixture(tmp_path)
    _commit_fixture_report(repo, tested)
    monkeypatch.setattr(rehearsal, "REPO_ROOT", repo)
    assert _tested_source_still_valid(tested) is True


def test_tested_source_reuse_accepts_markdown_backticked_sha_marker(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import scripts.gateway_accounting_rehearsal as rehearsal

    repo, tested = _source_reuse_fixture(tmp_path)
    _commit_fixture_report(repo, tested, backticked=True)
    monkeypatch.setattr(rehearsal, "REPO_ROOT", repo)
    assert _tested_source_still_valid(tested) is True


def test_tested_source_reuse_rejects_dirty_relevant_source(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import scripts.gateway_accounting_rehearsal as rehearsal

    repo, tested = _source_reuse_fixture(tmp_path)
    _commit_fixture_report(repo, tested)
    (repo / "src" / "module.py").write_text("value = 2\n", encoding="utf-8")
    monkeypatch.setattr(rehearsal, "REPO_ROOT", repo)
    assert _tested_source_still_valid(tested) is False


def test_tested_source_reuse_rejects_changed_production_after_report(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import scripts.gateway_accounting_rehearsal as rehearsal

    repo, tested = _source_reuse_fixture(tmp_path)
    _commit_fixture_report(repo, tested)
    (repo / "src" / "module.py").write_text("value = 2\n", encoding="utf-8")
    _fixture_git(repo, "add", "src/module.py")
    _fixture_git(repo, "commit", "--quiet", "-m", "production change")
    monkeypatch.setattr(rehearsal, "REPO_ROOT", repo)
    assert _tested_source_still_valid(tested) is False


def test_tested_source_reuse_rejects_unverified_report_commit_shapes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import scripts.gateway_accounting_rehearsal as rehearsal

    repo, tested = _source_reuse_fixture(tmp_path)
    report = repo / "oap" / "reports" / "round.md"
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(f"Implementation head SHA: {tested}\n", encoding="utf-8")
    (repo / "notes.md").write_text("not a report\n", encoding="utf-8")
    _fixture_git(repo, "add", "oap/reports/round.md", "notes.md")
    _fixture_git(repo, "commit", "--quiet", "-m", "oap: publish malformed report")
    monkeypatch.setattr(rehearsal, "REPO_ROOT", repo)
    assert _tested_source_still_valid(tested) is False

    wrong = repo / "oap" / "reports" / "wrong.md"
    wrong.write_text(
        "- Implementation head SHA: " + "0" * 40 + "\n- Report publication commit: SELF\n",
        encoding="utf-8",
    )
    _fixture_git(repo, "add", "oap/reports/wrong.md")
    _fixture_git(repo, "commit", "--quiet", "-m", "oap: publish wrong marker")
    assert _tested_source_still_valid(tested) is False

    duplicate = repo / "oap" / "reports" / "duplicate.md"
    duplicate.write_text(
        f"- Implementation head SHA: `{tested}`\n"
        f"- Implementation head SHA: {tested}\n"
        "- Report publication commit: SELF\n",
        encoding="utf-8",
    )
    _fixture_git(repo, "add", "oap/reports/duplicate.md")
    _fixture_git(repo, "commit", "--quiet", "-m", "oap: publish duplicate marker")
    assert _tested_source_still_valid(tested) is False

    valid_report_commit = _commit_fixture_report(repo, tested, path="oap/reports/second.md")
    tree = _fixture_git(repo, "rev-parse", f"{valid_report_commit}^{{tree}}")
    merge = subprocess.run(
        ["git", "-C", str(repo), "commit-tree", tree, "-p", tested, "-p", valid_report_commit],
        input="oap: publish merge report\n",
        capture_output=True,
        text=True,
        check=True,
        env={
            **os.environ,
            "GIT_AUTHOR_NAME": "synthetic",
            "GIT_AUTHOR_EMAIL": "synthetic@example.invalid",
            "GIT_COMMITTER_NAME": "synthetic",
            "GIT_COMMITTER_EMAIL": "synthetic@example.invalid",
        },
    ).stdout.strip()
    _fixture_git(repo, "update-ref", "HEAD", merge)
    assert _tested_source_still_valid(tested) is False


def _complete_fake_payload() -> dict[str, object]:
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
    gate_results = cast(list[dict[str, object]], gate["results"])
    gate["results"] = list(gate_results)
    observations = {key: True for key in FAKE_RESULT_SCHEMA_KEYS}
    gate["projection_table"] = projection_table_safe_dict(
        observations, {item.obligation_id: "PASSED" for item in results}
    )
    gate["projection_table"] = list(cast(tuple[dict[str, object], ...], gate["projection_table"]))
    gate["observation_schema_keys"] = FAKE_RESULT_SCHEMA_KEYS
    return {
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
            "provider_boundary_observed": True,
            "inference_attempted_count": 2,
            "inference_terminal_valid_count": 2,
            "inference_attempted_count_class": "2",
            "inference_terminal_valid_count_class": "2",
        },
        "acceptance_gate": gate,
    }


def test_protected_gate_accepts_only_complete_projected_current_fake_result(
    tmp_path: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        "scripts.gateway_accounting_rehearsal._tested_source_still_valid", lambda _sha: True
    )
    payload = _complete_fake_payload()
    path = tmp_path / "fake-result.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    _validate_fake_gate(path)

    payload["acceptance_gate"]["results"][1]["obligation_id"] = "C1.1"  # type: ignore[index]
    path.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(RuntimeError, match="protected_fake_gate"):
        _validate_fake_gate(path)


@pytest.mark.parametrize(
    "mutation",
    (
        lambda payload: payload["acceptance_gate"]["results"].pop(),
        lambda payload: payload["acceptance_gate"]["results"].__setitem__(
            1, payload["acceptance_gate"]["results"][0]
        ),
        lambda payload: payload["acceptance_gate"]["results"].reverse(),
        lambda payload: payload["acceptance_gate"]["results"].append(
            payload["acceptance_gate"]["results"][0]
        ),
        lambda payload: payload["runtime_observations"].__setitem__(
            FAKE_RESULT_SCHEMA_KEYS[0], False
        ),
        lambda payload: payload["runtime_observations"].pop(FAKE_RESULT_SCHEMA_KEYS[0]),
        lambda payload: payload["acceptance_gate"]["results"][0].__setitem__(
            "relationship", "other"
        ),
        lambda payload: payload["acceptance_gate"]["projection_table"].__setitem__(
            0, {**payload["acceptance_gate"]["projection_table"][0], "execution_status": "FAILED"}
        ),
        lambda payload: payload["acceptance_gate"].__setitem__("retry_count", 1),
        lambda payload: payload["candidate_provenance"].__setitem__("gateway_sha", "0" * 40),
        lambda payload: payload["candidate_provenance"].__setitem__("codex_version", "0.148.0"),
        lambda payload: payload["candidate_provenance"].__setitem__(
            "observer_version", "direct-httpx-v1"
        ),
        lambda payload: payload["transport_observation"].__setitem__(
            "inference_terminal_valid_count", 1
        ),
        lambda payload: payload["acceptance_gate"].__setitem__("passed", False),
    ),
)
def test_protected_gate_rejects_independent_negative_evidence(
    tmp_path: Any, monkeypatch: pytest.MonkeyPatch, mutation: Any
) -> None:
    monkeypatch.setattr(
        "scripts.gateway_accounting_rehearsal._tested_source_still_valid", lambda _sha: True
    )
    payload = _complete_fake_payload()
    mutation(payload)
    path = tmp_path / "fake-result.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(RuntimeError, match="protected_fake_gate"):
        _validate_fake_gate(path)


def test_protected_gate_enforces_cap_before_reading(tmp_path: Any) -> None:
    path = tmp_path / "oversized-result.json"
    with path.open("wb") as handle:
        handle.truncate(2 * 1024 * 1024 + 1)
    with pytest.raises(RuntimeError, match="protected_fake_gate_too_large"):
        _validate_fake_gate(path)


def test_protected_gate_rejects_duplicate_and_nonfinite_json(tmp_path: Any) -> None:
    duplicate = tmp_path / "duplicate-result.json"
    duplicate.write_text('{"status":"COMPLETE","status":"COMPLETE"}\n', encoding="utf-8")
    with pytest.raises(RuntimeError, match="protected_fake_gate_invalid"):
        _validate_fake_gate(duplicate)
    nonfinite = tmp_path / "nonfinite-result.json"
    nonfinite.write_text('{"status":"COMPLETE","value":NaN}\n', encoding="utf-8")
    with pytest.raises(RuntimeError, match="protected_fake_gate_invalid"):
        _validate_fake_gate(nonfinite)

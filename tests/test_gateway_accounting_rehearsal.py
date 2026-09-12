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

import scripts.gateway_accounting_rehearsal as rehearsal
from scripts.gateway_accounting_rehearsal import (
    CODEX_FIXTURE_SHA256,
    CODEX_VERSION,
    FAKE_MAX_EVENT_BYTES,
    GATEWAY_APP_TREE_SHA256,
    LOCAL_ROUTE_POLICY,
    OBSERVATION_VERSION,
    ProtectedRuntimeHooks,
    _acceptance_gate,
    _candidate_only_observation,
    _candidate_provenance,
    _FakeQwenServer,
    _identity_companion_tools,
    _identity_replay_target_gate,
    _idless_companion_continuation_body,
    _idless_companion_initial_body,
    _idless_companion_observation,
    _local_implementation_sha,
    _protected_provider_observation,
    _protected_provider_preflight,
    _provider_request_observation,
    _replay_ownership_negative_observation,
    _request_observation,
    _ReturnedCallIDCapture,
    _run_fake_idless_http_regression,
    _runtime_observations,
    _runtime_privacy_fact,
    _select_protected_runtime,
    _source_identity,
    _start_threaded_server,
    _stop_threaded_server,
    _target_execution_plan,
    _target_response_failure_facts,
    _target_semantic_preflight,
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
    RunAccumulator,
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
    def __init__(self) -> None:
        self._candidates: list[object] = []

    def validate(self, payload: object) -> bool:
        if not isinstance(payload, dict) or payload.get("type") not in {
            "response.created",
            "response.output_item.done",
            "response.completed",
        }:
            return False
        if payload.get("type") == "response.output_item.done":
            item = payload.get("item")
            if not isinstance(item, dict):
                return False
            if item.get("type") == "function_call":
                self._candidates.append(
                    type(
                        "_Candidate",
                        (),
                        {
                            "item_kind": item.get("type"),
                            "item_id": item.get("id"),
                            "call_id": item.get("call_id"),
                        },
                    )()
                )
        return True

    def take_replay_reference_candidates(self) -> tuple[object, ...]:
        candidates = tuple(self._candidates)
        self._candidates.clear()
        return candidates


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
            returned_call = server.take_returned_call()
            assert returned_call is not None
            legal_call = dict(returned_call)
            legal_call.pop("id", None)
            legal = dict(continuation)
            legal["input"] = [
                legal_call,
                {
                    "type": "function_call_output",
                    "call_id": returned_call["call_id"],
                    "output": "synthetic-result",
                },
            ]
            orphan = client.post(
                url, json=continuation, headers={"Authorization": "Bearer synthetic-http-token"}
            )
            second = client.post(
                url,
                json=legal,
                headers={"Authorization": "Bearer synthetic-http-token"},
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
        assert orphan.status_code == 502
        assert identified.status_code == 502
        assert rejected.status_code == 502
        for response in (first, second):
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
        assert snapshot["inference_calls"] == 2
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
        initial = {
            "model": "qwen3.8-27b",
            "stream": True,
            "input": [
                {"type": "input_image", "image_url": "synthetic-full"},
                {"type": "input_image", "image_url": "synthetic-crop"},
            ],
            "tools": [{"type": "function", "name": "shell_command"}],
        }
        continuation_prefix: list[dict[str, object]] = [
            {"type": "input_image", "image_url": "synthetic-crop"},
        ]
        with httpx.Client(timeout=5) as client:
            first = client.post(url, json=initial, headers=headers)
            returned_call = server.take_returned_call()
            assert returned_call is not None
            replay_call = dict(returned_call)
            replay_call.pop("id", None)
            continuation = dict(initial)
            continuation["input"] = [
                *continuation_prefix,
                replay_call,
                {
                    "type": "function_call_output",
                    "call_id": returned_call["call_id"],
                    "output": "synthetic-result-2",
                },
            ]
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


def _observer_response(*, call_id: str | None = None, summary_call_id: str | None = None) -> bytes:
    if summary_call_id is None:
        summary_call_id = call_id
    output = (
        [{"type": "function_call", "id": "item-summary", "call_id": summary_call_id}]
        if call_id is not None
        else [{"type": "message", "id": "item-message"}]
    )
    canonical_item = (
        {
            "type": "function_call",
            "id": "item-canonical",
            "call_id": call_id,
            "name": "local_lookup",
            "arguments": '{"path":"GOVERNANCE-DEPENDENCY.md"}',
            "status": "completed",
        }
        if call_id is not None
        else {"type": "message", "id": "item-message"}
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
                "response.output_item.done",
                {
                    "type": "response.output_item.done",
                    "item": canonical_item,
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
    responses = iter(
        (
            _observer_response(call_id="call-real-a", summary_call_id="call-summary-alias"),
            _observer_response(),
        )
    )

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
                "type": "function_call",
                "call_id": "call-real-a",
                "name": "local_lookup",
                "arguments": '{"path":"GOVERNANCE-DEPENDENCY.md"}',
                "status": "completed",
            },
            {
                "type": "function_call_output",
                "call_id": "call-real-a",
                "output": "synthetic-result",
            },
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
    assert boundary["canonical_summary_relation_classes"] == ("different",)


@pytest.mark.asyncio
async def test_direct_observer_does_not_promote_terminal_summary_alias() -> None:
    responses = iter(
        (
            _observer_response(call_id="call-canonical", summary_call_id="call-summary-alias"),
            _observer_response(),
        )
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
        request_classifier=_provider_request_observation,
    )
    metadata = {"session_id": "session-summary-alias"}
    initial = {
        "model": "synthetic",
        "stream": True,
        "client_metadata": metadata,
        "input": [{"type": "message", "role": "user", "content": []}],
        "tools": [{"type": "function", "name": "non_fixture_tool"}],
    }
    alias_continuation = {
        "model": "synthetic",
        "stream": True,
        "client_metadata": metadata,
        "input": [
            {
                "type": "function_call",
                "call_id": "call-canonical",
                "name": "local_lookup",
                "arguments": '{"path":"GOVERNANCE-DEPENDENCY.md"}',
                "status": "completed",
            },
            {
                "type": "function_call_output",
                "call_id": "call-summary-alias",
                "output": "synthetic-result",
            },
        ],
    }
    async with httpx.AsyncClient(transport=observer) as client:
        first = await client.post("http://fake.test/v1/responses", json=initial)
        await first.aread()
        second = await client.post("http://fake.test/v1/responses", json=alias_continuation)
        await second.aread()
    records = observer.snapshot()["records"]
    assert isinstance(records, (list, tuple))
    continuation = cast(dict[str, object], records[1])
    assert continuation["call_id_relation"] == "mismatched"
    assert continuation["function_result_adjacent"] is False


@pytest.mark.parametrize("chunk_size", (1, 4096))
@pytest.mark.parametrize("with_event_name", (False, True))
def test_returned_call_capture_handles_split_and_coalesced_sse(
    chunk_size: int, with_event_name: bool
) -> None:
    event_line = b"event: response.completed\n" if with_event_name else b""
    frames = (
        b"data: "
        + json.dumps(
            {"type": "response.created", "response": {"id": "response-real"}},
            separators=(",", ":"),
        ).encode()
        + b"\n\n",
        b"data: "
        + json.dumps(
            {
                "type": "response.output_item.done",
                "item": {
                    "type": "function_call",
                    "id": "item-real",
                    "call_id": "call-real",
                    "name": "lookup_target",
                    "arguments": '{"path":"varied.md"}',
                    "status": "completed",
                    "namespace": "companion",
                },
            },
            separators=(",", ":"),
        ).encode()
        + b"\n\n",
        event_line
        + b"data: "
        + json.dumps(
            {
                "type": "response.completed",
                "response": {
                    "id": "response-real",
                    "status": "completed",
                    "output": [
                        {
                            "type": "function_call",
                            "id": "item-summary",
                            "call_id": "summary-alias",
                        }
                    ],
                },
            },
            separators=(",", ":"),
        ).encode()
        + b"\n\n",
    )
    frame = b"".join(frames)
    capture = _ReturnedCallIDCapture(validator=_ObserverValidator())
    for offset in range(0, len(frame), chunk_size):
        capture.consume(frame[offset : offset + chunk_size])
    capture.finish(stream_valid=True)
    assert capture.value == "call-real"
    returned_call = capture.take_function_call()
    assert returned_call == {
        "type": "function_call",
        "id": "item-real",
        "call_id": "call-real",
        "name": "lookup_target",
        "arguments": '{"path":"varied.md"}',
        "status": "completed",
        "namespace": "companion",
    }
    assert capture.take_function_call() is None
    assert capture.safe_facts() == {
        "canonical_candidate_availability": "available",
        "canonical_candidate_count_class": "1",
        "canonical_summary_relation": "different",
    }


def test_returned_call_capture_rejects_summary_only_identity() -> None:
    frame = (
        b"data: "
        + json.dumps(
            {
                "type": "response.completed",
                "response": {
                    "id": "response-real",
                    "status": "completed",
                    "output": [
                        {
                            "type": "function_call",
                            "id": "item-summary",
                            "call_id": "summary-alias",
                        }
                    ],
                },
            },
            separators=(",", ":"),
        ).encode()
        + b"\n\n"
    )
    capture = _ReturnedCallIDCapture(validator=_ObserverValidator())
    capture.consume(frame)
    capture.finish(stream_valid=True)
    assert capture.value is None
    assert capture.safe_facts()["canonical_candidate_availability"] == "none"


def test_returned_call_capture_distinguishes_validator_and_candidate_stages() -> None:
    validator_rejection = _event(
        {"type": "response.failed", "response": {"id": "response-real", "status": "failed"}}
    )
    capture = _ReturnedCallIDCapture(validator=_ObserverValidator())
    capture.consume(validator_rejection)
    capture.finish(stream_valid=True)
    assert capture.safe_facts()["validation_stage"] == "gateway_validator"

    malformed_candidate = _event(
        {
            "type": "response.output_item.done",
            "item": {"type": "function_call", "call_id": "call-real"},
        }
    )
    capture = _ReturnedCallIDCapture(validator=_ObserverValidator())
    capture.consume(malformed_candidate)
    capture.finish(stream_valid=True)
    assert capture.safe_facts()["validation_stage"] == "replay_candidate"


def test_idless_companion_initial_request_forces_the_declared_function() -> None:
    tools: list[dict[str, object]] = [{"type": "function", "name": "local_lookup"}]
    body = _idless_companion_initial_body("session-a", tools)
    assert body["tool_choice"] == {"type": "function", "name": "local_lookup"}
    assert body["max_output_tokens"] == 32
    assert body["chat_template_kwargs"] == {"enable_thinking": False}
    assert body["input"][0]["content"][0]["text"] == "Call local_lookup with no arguments."  # type: ignore[index]


def test_identity_companion_declares_exact_zero_argument_schema() -> None:
    tools = _identity_companion_tools()
    local_lookup = next(
        tool
        for tool in tools
        if tool.get("type") == "function" and tool.get("name") == "local_lookup"
    )
    assert local_lookup["parameters"] == {
        "type": "object",
        "properties": {},
        "additionalProperties": False,
    }


def test_fake_identity_companion_emits_legal_zero_argument_reply() -> None:
    server = _FakeQwenServer("synthetic-zero-argument-token")
    thread = _start_threaded_server(server)
    tools = _identity_companion_tools()
    initial = _idless_companion_initial_body("session-a", tools)
    try:
        with httpx.Client(timeout=10, follow_redirects=False) as client:
            response = client.post(
                f"http://127.0.0.1:{server.server_address[1]}/v1/responses",
                json=initial,
                headers={"Authorization": f"Bearer {server.token}"},
            )
        returned_call = server.take_returned_call()
        assert response.status_code == 200
        assert b"response.function_call_arguments" not in response.content
        assert isinstance(returned_call, dict)
        assert returned_call.get("name") == "local_lookup"
        assert returned_call.get("arguments") == ""
    finally:
        _stop_threaded_server(server, thread)


def test_target_semantic_preflight_binds_the_checked_request_body(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    tools = _identity_companion_tools()
    body = _idless_companion_initial_body("session-a", tools)
    observed_content: list[bytes] = []

    class Profile:
        zero_argument_function_names = frozenset({"local_lookup"})

    class Validator:
        profile = Profile()

    def helper(_gateway_root: Path, _body: dict[str, object]) -> frozenset[str]:
        return frozenset({"local_lookup"})

    def factory(request: httpx.Request) -> Validator:
        content = request.content
        assert isinstance(content, bytes)
        observed_content.append(content)
        return Validator()

    monkeypatch.setattr(rehearsal, "_gateway_zero_argument_function_names", helper)
    request_content, facts = _target_semantic_preflight(
        Path("/tmp/slaif-gateway-005-ao"), body, validator_factory=factory
    )

    assert observed_content == [request_content]
    assert facts == {
        "helper_expected": True,
        "validator_profile_expected": True,
        "helper_profile_equal": True,
        "request_body_bound": True,
    }


@pytest.mark.parametrize(
    ("helper_names", "profile_names"),
    (
        (frozenset(), frozenset()),
        (frozenset({"local_lookup"}), frozenset()),
    ),
)
def test_target_semantic_preflight_rejects_ineligible_helper_or_profile(
    monkeypatch: pytest.MonkeyPatch,
    helper_names: frozenset[str],
    profile_names: frozenset[str],
) -> None:
    body = _idless_companion_initial_body("session-a", _identity_companion_tools())

    class Profile:
        zero_argument_function_names = profile_names

    class Validator:
        profile = Profile()

    monkeypatch.setattr(
        rehearsal,
        "_gateway_zero_argument_function_names",
        lambda _gateway_root, _body: helper_names,
    )
    with pytest.raises(RuntimeError, match="target_zero_argument_semantic_preflight_failed"):
        _target_semantic_preflight(
            Path("/tmp/slaif-gateway-005-ao"),
            body,
            validator_factory=lambda _request: Validator(),
        )


def test_target_semantic_preflight_failure_precedes_protected_selection(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    gateway_root = Path("/tmp/slaif-gateway-005-ao")
    codex = Path(
        "/synology/homes/janezp/.codex/packages/standalone/releases/"
        "0.149.0-x86_64-unknown-linux-musl/bin/codex"
    )
    if not gateway_root.is_dir() or not codex.is_file():
        pytest.skip("pinned target qualification dependencies are unavailable")
    selection_calls: list[str] = []

    monkeypatch.setattr(rehearsal, "_validate_fake_gate", lambda _path: None)

    def validator_factory(_root: Path, **_kwargs: object) -> Any:
        return lambda _request: object()

    monkeypatch.setattr(rehearsal, "_gateway_stream_validator_factory", validator_factory)

    def fail_gate(*_args: object, **_kwargs: object) -> tuple[bytes, dict[str, object]]:
        raise RuntimeError("target_zero_argument_semantic_preflight_failed")

    monkeypatch.setattr(rehearsal, "_target_semantic_preflight", fail_gate)

    def select_runtime(*_args: object, **_kwargs: object) -> tuple[dict[str, object], str, str]:
        selection_calls.append("selected")
        raise AssertionError("protected runtime selected before semantic gate")

    monkeypatch.setattr(rehearsal, "_select_protected_runtime", select_runtime)
    args = argparse.Namespace(
        provider_target="protected",
        target="identity_replay",
        gateway_root=gateway_root,
        gateway_python=Path("/tmp/slaif-gateway-venv-005-an.THUKHt/bin/python"),
        codex=codex,
        fake_result=None,
    )
    with pytest.raises(RuntimeError, match="target_zero_argument_semantic_preflight_failed"):
        rehearsal._run_direct_composed_rehearsal_impl(
            args, preflight={"gateway_policy": "ACCEPTED"}, accumulator=RunAccumulator("protected")
        )
    assert selection_calls == []


def test_target_response_failure_facts_keep_only_safe_error_and_event_classes() -> None:
    sse = SSEFacts(error_event=True, error_field_names={"code", "message", "param"})
    sse.error_code_class = "provider"
    sse.error_type_class = "provider"
    facts = _target_response_failure_facts(
        {"records": ()},
        {
            "records": (
                {
                    "kind": "inference",
                    "request_class": "function_initial",
                    "validation_stage": "event_class",
                    "failure_event_class": "error",
                    "exception_class": "stream_validation_invalid",
                },
            )
        },
        request_class="function_initial",
        status=502,
        sse=sse,
        capture_facts={"failure_class": "validator", "validation_stage": "gateway_validator"},
    )
    assert facts == {
        "status": 502,
        "error": {
            "event": True,
            "field_names": ("code", "message", "param"),
            "code_class": "provider",
            "type_class": "provider",
            "param_present": True,
        },
        "validator": {
            "failure_class": "validator",
            "validation_stage": "event_class",
            "failed_event_class": "error",
        },
    }


def test_target_response_failure_facts_retain_original_provider_error_classes() -> None:
    facts = _target_response_failure_facts(
        {"records": ()},
        {
            "records": (
                {
                    "kind": "inference",
                    "request_class": "function_continuation",
                    "provider_error": {
                        "http_status": 400,
                        "body_class": "error_object",
                        "type_class": "BadRequestError",
                        "code_class": "bad_request",
                        "param_class": "null",
                        "field_states": (("code", "integer"), ("param", "null")),
                    },
                },
            )
        },
        request_class="function_continuation",
        status=400,
        sse=SSEFacts(),
        capture_facts={},
    )
    error = cast(dict[str, object], facts["error"])
    provider = cast(dict[str, object], error["provider"])
    assert provider["http_status"] == 400
    assert provider["type_class"] == "BadRequestError"
    assert provider["code_class"] == "bad_request"
    assert provider["param_class"] == "null"


def test_idless_companion_replays_actual_call_and_omits_only_optional_id() -> None:
    returned_call = {
        "type": "function_call",
        "id": "actual-item",
        "call_id": "actual-call",
        "namespace": "companion",
        "name": "lookup_target",
        "arguments": '{"path":"varied.md"}',
        "status": "completed",
    }
    initial = _idless_companion_initial_body(
        "session-a", [{"type": "function", "name": "lookup_target"}]
    )
    body = _idless_companion_continuation_body(
        "session-a",
        returned_call,
        tools=[{"type": "function", "name": "lookup_target"}],
        initial_body=initial,
    )
    history = body["input"]
    assert isinstance(history, list)
    user = history[0]
    call = history[1]
    output = history[2]
    assert isinstance(user, dict) and isinstance(call, dict) and isinstance(output, dict)
    initial_input = cast(list[object], initial["input"])
    assert user == initial_input[0]
    assert "id" not in call
    assert call["name"] == returned_call["name"]
    assert call["arguments"] == returned_call["arguments"]
    assert call["namespace"] == returned_call["namespace"]
    assert call["status"] == "completed"
    assert call["call_id"] == "actual-call"
    assert output["call_id"] == "actual-call"


def test_request_observation_uses_function_call_id_not_output_id() -> None:
    legal = {
        "input": [
            {
                "type": "function_call",
                "call_id": "call-a",
                "name": "lookup_target",
                "arguments": '{"path":"varied.md"}',
                "status": "completed",
            },
            {
                "type": "function_call_output",
                "call_id": "call-a",
                "id": "output-id",
                "output": "ok",
            },
        ]
    }
    orphan = {"input": [{"type": "function_call_output", "call_id": "call-a", "output": "ok"}]}
    assert _request_observation(legal)["item_id_presence"] == "omitted"
    assert _request_observation(orphan)["item_id_presence"] == "unknown"


def test_fake_idless_regression_rejects_orphans_before_and_after_seed() -> None:
    facts = _run_fake_idless_http_regression()
    assert facts["passed"] is True
    assert facts["orphan_after_initial_rejected"] is True
    assert facts["orphan_fresh_rejected"] is True


def test_identity_target_selector_excludes_unrelated_phases() -> None:
    plan = _target_execution_plan("identity_replay")
    assert plan == {
        "target": "identity_replay",
        "allowed_operations": ("identity_replay",),
        "max_inference_dispatches": 2,
        "max_compiler_dispatches": 0,
        "runs_codex": False,
        "runs_vision": False,
        "runs_other_identity": False,
        "runs_full_protected_matrix": False,
    }


def _target_gate_facts() -> dict[str, object]:
    return {
        "provider_target": "protected",
        "target": "identity_replay",
        "target_plan": _target_execution_plan("identity_replay"),
        "idless_composed_companion": {"passed": True},
        "target_dispatch_counts": {
            "inference_dispatched": 2,
            "compiler_dispatched": 0,
            "other_dispatched": 0,
        },
        "target_accounting": {
            "reservation_count_consistent": True,
            "reservation_terminal": True,
            "ledger_count_consistent": True,
            "ledger_terminal": True,
            "zero_pending": True,
            "zero_duplicate_request_ids": True,
        },
        "protected_later_inference": False,
        "full_protected_matrix": False,
        "logs_secret_free": True,
        "cleanup_observation": {
            "processes": True,
            "listeners": True,
            "database": True,
            "cache": True,
            "codex_home": True,
        },
        "protected_unchanged": {
            "pid": True,
            "start": True,
            "listener": True,
            "worktree_count": True,
            "text_inactive": True,
            "no_18021": True,
            "no_18031": True,
        },
    }


@pytest.mark.parametrize(
    "mutation",
    (
        lambda facts: facts["target_accounting"].update({"ledger_terminal": False}),
        lambda facts: facts["target_accounting"].update({"ledger_count_consistent": False}),
        lambda facts: facts["protected_unchanged"].update({"pid": False}),
        lambda facts: facts["protected_unchanged"].update({"start": None}),
    ),
)
def test_identity_target_gate_rejects_nonterminal_ledger_or_unknown_fixture(
    mutation: Any,
) -> None:
    facts = _target_gate_facts()
    mutation(facts)
    assert _identity_replay_target_gate(facts)["passed"] is False


def test_returned_call_capture_retains_frame_buffer_overflow_facts() -> None:
    capture = _ReturnedCallIDCapture(validator=_ObserverValidator())
    capture.consume(b"x" * (FAKE_MAX_EVENT_BYTES + 5))
    capture.finish(stream_valid=False)
    assert capture.value is None
    assert capture.safe_facts() == {
        "canonical_candidate_availability": "unknown",
        "canonical_candidate_count_class": "0",
        "canonical_summary_relation": "unknown",
        "failure_class": "overflow",
        "overflow_subtype": "frame_buffer_bytes",
        "overflow_observed": FAKE_MAX_EVENT_BYTES + 5,
        "overflow_bound": FAKE_MAX_EVENT_BYTES + 4,
    }


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
        canonical_replay_evidence={
            "canonical_candidate_availability": "available",
            "canonical_candidate_count_class": "1",
            "canonical_summary_relation": "different",
        },
    )
    assert facts["passed"] is (item_id_presence == "omitted" and call_id_relation == "matching")


def test_idless_companion_accepts_same_canonical_and_summary_identity() -> None:
    facts = _idless_companion_observation(
        {"records": ()},
        {"records": _companion_records()},
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
        canonical_replay_evidence={
            "canonical_candidate_availability": "available",
            "canonical_candidate_count_class": "1",
            "canonical_summary_relation": "same",
        },
    )
    assert facts["canonical_replay_authority"] is True
    assert facts["passed"] is True


@pytest.mark.parametrize(
    "canonical_replay_evidence",
    (
        {
            "canonical_candidate_availability": "none",
            "canonical_candidate_count_class": "0",
            "canonical_summary_relation": "different",
        },
        {
            "canonical_candidate_availability": "available",
            "canonical_candidate_count_class": "0",
            "canonical_summary_relation": "same",
        },
        {
            "canonical_candidate_availability": "unknown",
            "canonical_candidate_count_class": "unknown",
            "canonical_summary_relation": "unknown",
        },
    ),
)
def test_idless_companion_rejects_missing_canonical_authority(
    canonical_replay_evidence: dict[str, object],
) -> None:
    facts = _idless_companion_observation(
        {"records": ()},
        {"records": _companion_records()},
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
        canonical_replay_evidence=canonical_replay_evidence,
    )
    assert facts["canonical_replay_authority"] is False
    assert facts["passed"] is False


@pytest.mark.parametrize(
    ("provider_target", "synthetic_protected", "execution_mode", "run_provenance"),
    (
        ("fake", False, "fake", "fresh_fake_direct_httpx_loopback"),
        (
            "protected",
            True,
            "synthetic-protected",
            "fresh_synthetic_protected_direct_httpx_loopback",
        ),
        ("protected", False, "real-protected", "fresh_real_protected_direct_httpx_qwen"),
    ),
)
def test_candidate_provenance_records_actual_execution_mode(
    provider_target: str,
    synthetic_protected: bool,
    execution_mode: str,
    run_provenance: str,
) -> None:
    provenance = _candidate_provenance(
        "a" * 40,
        "b" * 32,
        provider_target=provider_target,
        synthetic_protected=synthetic_protected,
    )
    assert provenance["execution_mode"] == execution_mode
    assert provenance["run_provenance"] == run_provenance


def test_candidate_only_observation_keeps_readiness_separate_from_totals() -> None:
    candidate = _candidate_only_observation(
        {
            "ready": True,
            "other_attempted_count": 2,
            "other_dispatched_count": 2,
            "other_responded_count": 2,
            "other_completed_count": 2,
            "other_terminal_valid_count": 2,
            "compiler_attempted_count": 0,
            "compiler_dispatched_count": 0,
            "inference_attempted_count": 0,
            "inference_dispatched_count": 0,
        }
    )
    assert candidate["lifetime_id"] == "candidate"
    assert candidate["ready"] is True
    assert candidate["counts"] == {
        "other_attempted": 2,
        "other_dispatched": 2,
        "other_responded": 2,
        "other_completed": 2,
        "other_terminal_valid": 2,
        "compiler_attempted": 0,
        "compiler_dispatched": 0,
        "inference_attempted": 0,
        "inference_dispatched": 0,
    }


def test_replay_ownership_negatives_require_gateway_denial_and_no_side_effects() -> None:
    before = {
        "reservation_count": 2,
        "finalized_reservation_count": 2,
        "pending_reservation_count": 0,
        "ledger_count": 2,
        "finalized_ledger_count": 2,
        "failed_ledger_count": 0,
        "duplicate_request_id_count": 0,
        "provider_usage_rows": 2,
        "key_requests_used": 2,
        "key_tokens_used": 4,
        "ledger_total_tokens": 4,
        "ledger_total_cost_eur": "0.000004",
    }
    facts = _replay_ownership_negative_observation(
        {
            "missing_call_id": 422,
            "mismatched_call_id": 404,
            "wrong_key": 404,
        },
        provider_calls_before=3,
        provider_calls_after=3,
        primary_rows_before=before,
        primary_rows_after=dict(before),
        second_rows_before=before,
        second_rows_after=dict(before),
    )
    assert facts["passed"] is True
    assert facts["all_denied"] is True
    assert facts["provider_calls_unchanged"] is True
    assert facts["primary_accounting_unchanged"] is True
    assert facts["second_key_accounting_unchanged"] is True
    assert facts["zero_pending"] is True
    assert facts["zero_duplicate_request_ids"] is True


@pytest.mark.parametrize(
    ("statuses", "provider_after", "primary_after"),
    (
        ({"missing_call_id": 200, "mismatched_call_id": 404, "wrong_key": 404}, 3, None),
        ({"missing_call_id": 422, "mismatched_call_id": 404, "wrong_key": 404}, 4, None),
        ({"missing_call_id": 422, "mismatched_call_id": 404, "wrong_key": 404}, 3, 3),
    ),
)
def test_replay_ownership_negative_projection_fails_on_acceptance_or_side_effect(
    statuses: dict[str, int], provider_after: int, primary_after: int | None
) -> None:
    before = {
        "reservation_count": 1,
        "finalized_reservation_count": 1,
        "pending_reservation_count": 0,
        "ledger_count": 1,
        "finalized_ledger_count": 1,
        "failed_ledger_count": 0,
        "duplicate_request_id_count": 0,
        "provider_usage_rows": 1,
        "key_requests_used": 1,
        "key_tokens_used": 2,
        "ledger_total_tokens": 2,
        "ledger_total_cost_eur": "0.000002",
    }
    after = dict(before)
    if primary_after is not None:
        after["ledger_count"] = primary_after
    facts = _replay_ownership_negative_observation(
        statuses,
        provider_calls_before=3,
        provider_calls_after=provider_after,
        primary_rows_before=before,
        primary_rows_after=after,
        second_rows_before=before,
        second_rows_after=dict(before),
    )
    assert facts["passed"] is False


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


def test_runtime_privacy_projection_requires_retained_boolean_evidence() -> None:
    cases: tuple[tuple[bool, object, bool | None, str], ...] = (
        (True, True, True, "PASSED"),
        (True, False, False, "FAILED"),
        (False, None, None, "NOT RUN"),
        (True, "true", None, "NOT RUN"),
    )
    for present, value, expected_fact, expected_status in cases:
        result: dict[str, object] = {"provider_target": "fake"}
        if present:
            result["logs_secret_free"] = value
        assert _runtime_privacy_fact(result) is expected_fact
        observations = _runtime_observations(result)
        assert observations["privacy.no_raw_canaries"] is expected_fact
        assert observations["privacy.no_raw_bodies"] is expected_fact
        assert observations["privacy.no_credentials"] is expected_fact
        gate, _gaps = _acceptance_gate(result)
        rows = {row["obligation_id"]: row for row in cast(list[dict[str, object]], gate["results"])}
        assert rows["C5.2"]["status"] == expected_status
        assert rows["C5.2"]["observed"] is (expected_fact is not None)


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


def test_acceptance_gate_projects_completed_codex_before_later_runtime_stop() -> None:
    boundary = {
        "call_count_class": "2",
        "lifecycle_valid": True,
        "terminality_valid": True,
        "request_class_classes": ("function_continuation", "function_initial"),
        "function_result_adjacent": True,
        "call_id_relation_classes": ("matching",),
        "independent_from_ledger": True,
    }
    result: dict[str, object] = {
        "provider_target": "fake",
        "run_accumulator": {
            "first_failure": "observer_readiness_lost",
            "first_failure_context": {
                "kind": "inference",
                "operation": "vision_full",
                "phase": "vision",
                "ordinal": 3,
                "lifetime_id": "vision",
            },
        },
        "phase_checkpoints": (
            {
                "phase": "codex",
                "lifetime_id": "codex",
                "evidence_kind": "semantic",
                "phase_facts": {"codex": {"status": "PASSED"}},
            },
        ),
        "codex": {
            "status": "PASSED",
            "provider_inference_call_count": 2,
            "provider_turns_expected": 2,
            "exit_status": 0,
            "command_lifecycle": "success",
            "sentinel_passed": True,
            "tool_call_count_class": "1",
            "call_id_same_hmac": False,
            "scope_no_downgrade": True,
        },
        "provider_observation": {"provider_boundary": boundary},
        "transport_observation": {"provider_boundary_observed": True},
        "accounting": {
            "two_terminal_reservations": True,
            "zero_pending": True,
            "zero_duplicate_request_ids": True,
        },
    }
    gate, _gaps = _acceptance_gate(result)
    rows = {row["obligation_id"]: row for row in cast(list[dict[str, object]], gate["results"])}
    assert rows["C1.1"]["status"] == "PASSED"
    assert rows["C1.2"]["status"] == "PASSED"
    assert rows["C1.3"]["status"] == "PASSED"
    assert rows["C1.5"]["status"] == "PASSED"
    assert rows["C1.6"]["status"] == "PASSED"
    assert rows["C1.4"]["status"] == "NOT RUN"
    assert rows["C2.1"]["status"] == "NOT RUN"
    assert rows["C5.2"]["status"] == "NOT RUN"
    projection_rows = {
        row["obligation_id"]: row for row in cast(list[dict[str, object]], gate["projection_table"])
    }
    assert projection_rows["C5.2"]["execution_status"] == "NOT RUN"
    assert gate["first_failure"] == "C1.4"
    assert gate["runtime_failure"]["class"] == "observer_readiness_lost"  # type: ignore[index]


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


def test_tested_source_reuse_accepts_evidence_only_child(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import scripts.gateway_accounting_rehearsal as rehearsal

    repo, tested = _source_reuse_fixture(tmp_path)
    evidence = repo / "oap" / "evidence" / "005-aj" / "index.json"
    evidence.parent.mkdir(parents=True, exist_ok=True)
    evidence.write_text('{"tested_implementation_sha":"' + tested + '"}\n', encoding="utf-8")
    _fixture_git(repo, "add", "oap/evidence/005-aj/index.json")
    _fixture_git(repo, "commit", "--quiet", "-m", "oap: publish evidence")
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
    gate["runtime_failure"] = None
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
            "execution_mode": "fake",
            "run_provenance": "fresh_fake_direct_httpx_loopback",
            "run_id": "0" * 32,
            "observer_version": OBSERVATION_VERSION,
            "source_identity": _source_identity(),
        },
        "runtime_observations": observations,
        "transport_observation": {
            "observer_version": OBSERVATION_VERSION,
            "ready": True,
            "matches_fake_provider": True,
            "provider_boundary_observed": True,
            "inference_attempted_count": 2,
            "inference_dispatched_count": 2,
            "inference_responded_count": 2,
            "inference_completed_count": 2,
            "inference_terminal_valid_count": 2,
            "inference_attempted_count_class": "2",
            "inference_terminal_valid_count_class": "2",
            "records": [
                {
                    "kind": "inference",
                    "dispatched": True,
                    "responded": True,
                    "completed": True,
                    "terminal_valid": True,
                    "normal_close": True,
                },
                {
                    "kind": "inference",
                    "dispatched": True,
                    "responded": True,
                    "completed": True,
                    "terminal_valid": True,
                    "normal_close": True,
                },
            ],
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
        lambda payload: payload["candidate_provenance"].__setitem__("run_id", "0" * 31),
        lambda payload: payload["candidate_provenance"]["source_identity"]["sha256"].__setitem__(
            "runner", "0" * 64
        ),
        lambda payload: payload["transport_observation"].__setitem__(
            "inference_terminal_valid_count", 1
        ),
        lambda payload: payload["transport_observation"]["records"].pop(),
        lambda payload: payload["acceptance_gate"]["projection_table"][0].__setitem__(
            "observed_field_count_class", "1"
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

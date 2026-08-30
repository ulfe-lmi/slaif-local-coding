"""Pure tests for the bounded composed stream evidence contract."""

from __future__ import annotations

import json
from typing import Any

import pytest

from scripts.local_qwen_provider_differential import SSEFacts
from tests.helpers.gateway_accounting_rehearsal import (
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
        "local_terminal_bytes": True,
        "gateway_reservation_terminal": True,
        "gateway_ledger_terminal": True,
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
            {"local_upstream_status_class": "5xx", "local_terminal_bytes": False},
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


def test_owner_mapping_uses_direct_local_and_gateway_facts() -> None:
    gateway_owned = _facts(
        sse=_parsed((_event({"type": "error"}),), finish=True),
        local_terminal_bytes=True,
    )
    assert gateway_owned.owner == "gateway_stream_owned"

    local_owned = _facts(local_upstream_status_class="5xx", local_terminal_bytes=False)
    assert local_owned.owner == "local_or_provider_owned"

    harness_owned = _facts(
        timing={
            "response_headers": "0-9ms",
            "first_sse_bytes": "10-49ms",
        },
        driver_observation_failure=True,
    )
    assert harness_owned.owner == "acceptance_harness_owned"

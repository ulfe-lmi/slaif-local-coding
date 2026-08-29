"""Pure tests for the bounded Objective-005j protected-boundary support."""

from __future__ import annotations

import json

from scripts import local_qwen_provider_differential as differential
from scripts.local_qwen_provider_differential import (
    KNOWN_EVENT_TYPES,
    MAX_EVENT_BYTES,
    MAX_STREAM_BYTES,
    SSEFacts,
    StageResult,
    _expected_body,
    _forwarded,
    _through_h,
    request_shape,
)


def _event(payload: dict[str, object]) -> bytes:
    return b"data: " + json.dumps(payload, separators=(",", ":")).encode() + b"\n\n"


def _created() -> bytes:
    return _event({"type": "response.created", "response": {"id": "response-1"}})


def _completed() -> bytes:
    return _event(
        {
            "type": "response.completed",
            "response": {
                "id": "response-1",
                "status": "completed",
                "output": [],
                "usage": {
                    "input_tokens": 3,
                    "output_tokens": 2,
                    "total_tokens": 5,
                },
            },
        }
    )


def _valid_stream() -> bytes:
    return _created() + _completed()


def _facts(
    stream: bytes, *, status: int = 200, content_type: str = "text/event-stream"
) -> StageResult:
    facts = StageResult(
        dispatch_started=True,
        dispatch_count=1,
        response_status=status,
        response_content_type=content_type,
    )
    facts.sse.consume(stream)
    facts.sse.finish()
    return facts


def test_expected_provider_shape_is_the_pinned_post_gateway_shape() -> None:
    body = _expected_body()
    shape = request_shape(body, expected_body=body)

    assert shape["body_equal"] is True
    assert shape["top_level_fields"] == ["input", "max_output_tokens", "model", "stream"]
    assert shape["model_matches"] is True
    assert shape["stream"] is True
    assert shape["tool_count"] == 0
    assert shape["image_count"] == 0
    assert shape["output_limit"] == "integer"
    assert shape["reasoning"] == "absent"


def test_sse_parser_handles_one_large_incremental_chunk_and_reasoning_events() -> None:
    padding = b": bounded keepalive\n\n" * 20_000
    stream = padding + b"".join(
        (
            _event({"type": "response.created", "id": "response-1"}),
            _event({"type": "response.reasoning_part.added"}),
            _event({"type": "response.reasoning_part.done"}),
            _event({"type": "response.reasoning_text.delta", "delta": "synthetic"}),
            _event(
                {
                    "type": "response.completed",
                    "response": {
                        "id": "response-1",
                        "status": "completed",
                        "output": [],
                        "usage": {
                            "input_tokens": 3,
                            "output_tokens": 2,
                            "total_tokens": 5,
                        },
                    },
                }
            ),
        )
    )
    facts = SSEFacts()
    facts.consume(stream)
    facts.finish()

    summary = facts.summary(status=200, content_type="text/event-stream")
    assert len(stream) > 262_144
    assert summary["parseable"] is True
    assert summary["recognized_events"] is True
    assert summary["created"] is True
    assert summary["completed_valid"] is True
    assert summary["normal_close"] is True


def test_sse_parser_handles_arbitrary_chunk_boundaries() -> None:
    stream = _valid_stream() + _event({"type": "response.reasoning_text.delta", "delta": "x"})
    whole = SSEFacts()
    whole.consume(stream)
    whole.finish()

    split = SSEFacts()
    offset = 0
    sizes = (1, 7, 2, 19, 3, 41)
    for size in sizes * 4:
        if offset >= len(stream):
            break
        split.consume(stream[offset : offset + size])
        offset += size
    if offset < len(stream):
        split.consume(stream[offset:])
    split.finish()

    assert split.summary(status=200, content_type="text/event-stream") == whole.summary(
        status=200, content_type="text/event-stream"
    )


def test_sse_parser_enforces_per_line_and_total_stream_bounds() -> None:
    oversized_line = SSEFacts()
    oversized_line.consume(b"data: " + b"x" * MAX_EVENT_BYTES + b"\n\n")
    oversized_line.finish()
    assert oversized_line.parseable is False

    valid = _valid_stream()
    padding_length = MAX_STREAM_BYTES - len(valid)
    assert padding_length > 0
    exact = (b":\n\n" * (padding_length // 3)) + (b"\n" * (padding_length % 3)) + valid
    assert len(exact) == MAX_STREAM_BYTES
    at_limit = SSEFacts()
    at_limit.consume(exact)
    at_limit.finish()
    assert at_limit.parseable is True
    assert at_limit.byte_count == MAX_STREAM_BYTES

    over_limit = SSEFacts()
    over_limit.consume(exact)
    over_limit.consume(b"\n")
    over_limit.finish()
    assert over_limit.parseable is False
    assert over_limit.byte_count == MAX_STREAM_BYTES + 1


def test_sse_parser_rejects_incomplete_and_malformed_events() -> None:
    incomplete = SSEFacts()
    incomplete.consume(_created() + _completed().rstrip(b"\n"))
    incomplete.finish()
    assert incomplete.parseable is False

    malformed = SSEFacts()
    malformed.consume(b"data: not-json\n\n")
    malformed.finish()
    assert malformed.parseable is False


def test_sse_parser_rejects_duplicate_terminal_and_error_events() -> None:
    duplicate = SSEFacts()
    duplicate.consume(_valid_stream() + _completed())
    duplicate.finish()
    assert duplicate.duplicates is True
    assert _through_h(_facts(_valid_stream() + _completed())) is False

    error = SSEFacts()
    error.consume(_created() + _event({"type": "error"}))
    error.finish()
    assert error.error_event is True
    assert error.summary(status=200, content_type="text/event-stream")["recognized_events"] is True
    assert _through_h(_facts(_created() + _event({"type": "error"}))) is False


def test_sse_parser_distinguishes_normal_and_abnormal_close() -> None:
    normal = SSEFacts()
    normal.consume(_valid_stream())
    normal.finish()
    assert normal.normal_close is True

    abnormal = SSEFacts()
    abnormal.consume(_valid_stream())
    assert abnormal.normal_close is False


def test_fixed_vocabulary_matches_gateway_codex_contract_and_rejects_unknowns() -> None:
    expected = {
        "response.created",
        "response.in_progress",
        "response.completed",
        "response.output_item.added",
        "response.output_item.done",
        "response.content_part.added",
        "response.content_part.done",
        "response.output_text.delta",
        "response.output_text.done",
        "response.reasoning_summary_part.added",
        "response.reasoning_summary_text.delta",
        "response.reasoning_summary_text.done",
        "response.reasoning_text.delta",
        "response.reasoning_text.done",
        "response.reasoning_part.added",
        "response.reasoning_part.done",
        "response.function_call_arguments.delta",
        "response.custom_tool_call_input.delta",
        "response.failed",
        "response.incomplete",
        "error",
    }
    assert KNOWN_EVENT_TYPES == expected
    assert KNOWN_EVENT_TYPES == differential.KNOWN_EVENT_TYPES

    unknown = SSEFacts()
    unknown.consume(_event({"type": "response.not_in_contract"}))
    unknown.finish()
    assert unknown.unknown_events is True
    assert (
        unknown.summary(status=200, content_type="text/event-stream")["recognized_events"] is False
    )


def test_forwarding_requires_independent_status_type_terminal_and_byte_equality() -> None:
    stream = _valid_stream()
    facts = _facts(stream)
    facts.downstream_status = 200
    facts.downstream_content_type = "text/event-stream"
    facts.downstream_sse.consume(stream)
    facts.downstream_sse.finish()
    assert _forwarded(facts) is True

    different = _facts(stream)
    different.downstream_status = 200
    different.downstream_content_type = "text/event-stream"
    different.downstream_sse.consume(stream + b": changed\n\n")
    different.downstream_sse.finish()
    assert _forwarded(different) is False

    incomplete_downstream = _facts(stream)
    incomplete_downstream.downstream_status = 200
    incomplete_downstream.downstream_content_type = "text/event-stream"
    incomplete_downstream.downstream_sse.consume(_created())
    incomplete_downstream.downstream_sse.finish()
    assert _forwarded(incomplete_downstream) is False

    wrong_status = _facts(stream, status=400)
    wrong_status.downstream_status = 200
    wrong_status.downstream_content_type = "text/event-stream"
    wrong_status.downstream_sse.consume(stream)
    wrong_status.downstream_sse.finish()
    assert _forwarded(wrong_status) is False

    wrong_type = _facts(stream)
    wrong_type.downstream_status = 200
    wrong_type.downstream_content_type = "application/json"
    wrong_type.downstream_sse.consume(stream)
    wrong_type.downstream_sse.finish()
    assert _forwarded(wrong_type) is False


def test_corrected_runner_has_no_direct_provider_control() -> None:
    source = differential.__file__
    assert source is not None
    text = open(source, encoding="utf-8").read()
    assert "async def _direct_call" not in text
    assert "await _direct_call" not in text

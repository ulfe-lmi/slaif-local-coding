"""Pure tests for the bounded Objective-005i differential evidence support."""

from __future__ import annotations

import json

from scripts.local_qwen_provider_differential import (
    SSEFacts,
    _expected_body,
    request_shape,
)


def _event(payload: dict[str, object]) -> bytes:
    return b"data: " + json.dumps(payload, separators=(",", ":")).encode() + b"\n\n"


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

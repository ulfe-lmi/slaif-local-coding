from __future__ import annotations

import asyncio
import json
from collections.abc import AsyncIterator, Mapping
from typing import cast

import httpx
import pytest

from tests.helpers.transport_observer import (
    MAX_EVENT_BYTES,
    MAX_STREAM_BYTES,
    DirectTransportObserver,
    merge_observer_snapshots,
    observer_dispatch_matches_fake,
)

KNOWN_EVENTS = {
    "response.created",
    "response.in_progress",
    "response.output_text.delta",
    "response.completed",
}


class _AcceptingValidator:
    def validate(self, payload: Mapping[str, object] | None) -> bool:
        return isinstance(payload, Mapping) and payload.get("type") in KNOWN_EVENTS


def _validator(_request: httpx.Request) -> _AcceptingValidator:
    return _AcceptingValidator()


def _frame(event_type: str, payload: dict[str, object], ending: bytes = b"\n\n") -> bytes:
    return (
        f"event: {event_type}\n".encode()
        + b"data: "
        + json.dumps(payload, separators=(",", ":")).encode()
        + ending
    )


def _stream_bytes(
    *,
    ending: bytes = b"\n\n",
    response_id: str = "response-1",
    completed_id: str | None = None,
    completed_status: str = "completed",
    output: object = None,
    usage: object = None,
    event_type: str = "response.output_text.delta",
) -> bytes:
    if completed_id is None:
        completed_id = response_id
    if output is None:
        output = [{"type": "message"}]
    if usage is None:
        usage = {"input_tokens": 1, "output_tokens": 1, "total_tokens": 2}
    return b"".join(
        (
            _frame(
                "response.created",
                {
                    "type": "response.created",
                    "sequence_number": 0,
                    "response": {"id": response_id, "status": "in_progress", "model": "synthetic"},
                },
                ending,
            ),
            _frame(
                event_type,
                {"type": event_type, "sequence_number": 1, "delta": "x"},
                ending,
            ),
            _frame(
                "response.completed",
                {
                    "type": "response.completed",
                    "sequence_number": 2,
                    "response": {
                        "id": completed_id,
                        "status": completed_status,
                        "output": output,
                        "usage": usage,
                    },
                },
                ending,
            ),
        )
    )


class _ChunkStream(httpx.AsyncByteStream):
    def __init__(self, chunks: tuple[bytes, ...]) -> None:
        self._chunks = chunks
        self.closed = False

    async def __aiter__(self) -> AsyncIterator[bytes]:
        for chunk in self._chunks:
            await asyncio.sleep(0)
            yield chunk

    async def aclose(self) -> None:
        self.closed = True


@pytest.mark.asyncio
async def test_direct_observer_preserves_stream_and_validates_crlf_chunking() -> None:
    expected = _stream_bytes(ending=b"\r\n\r\n")

    def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            headers={"content-type": "text/event-stream"},
            stream=_ChunkStream(
                tuple(expected[index : index + 1] for index in range(len(expected)))
            ),
        )

    observer = DirectTransportObserver(
        httpx.MockTransport(handler), validator_factory=_validator, validator_source="test"
    )
    async with httpx.AsyncClient(transport=observer) as client:
        response = await client.post("http://fake.test/v1/responses", content=b"synthetic")
        received = b"".join([chunk async for chunk in response.aiter_bytes()])
    assert received == expected
    snapshot = observer.snapshot()
    assert snapshot["inference_attempted_count"] == 1
    assert snapshot["inference_terminal_valid_count"] == 1
    assert snapshot["inference_first_byte_count"] == 1
    assert snapshot["inference_normal_close_count"] == 1
    assert snapshot["records"][0]["completed"] is True  # type: ignore[index]


@pytest.mark.asyncio
async def test_coalesced_frames_do_not_trigger_event_cap() -> None:
    expected = _stream_bytes()

    def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            headers={"content-type": "text/event-stream"},
            stream=_ChunkStream((expected,)),
        )

    observer = DirectTransportObserver(
        httpx.MockTransport(handler), validator_factory=_validator, validator_source="test"
    )
    async with httpx.AsyncClient(transport=observer) as client:
        response = await client.post("http://fake.test/v1/responses", content=b"synthetic")
        await response.aread()
    assert observer.snapshot()["inference_terminal_valid_count"] == 1


@pytest.mark.asyncio
async def test_observer_separates_compiler_and_inference_without_buffering_payloads() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/v1/chat/completions":
            return httpx.Response(
                200,
                headers={"content-type": "application/json"},
                stream=_ChunkStream((b'{"choices":[]}',)),
            )
        return httpx.Response(
            200,
            headers={"content-type": "text/event-stream"},
            stream=_ChunkStream((_stream_bytes(),)),
        )

    observer = DirectTransportObserver(
        httpx.MockTransport(handler), validator_factory=_validator, validator_source="test"
    )
    async with httpx.AsyncClient(transport=observer) as client:
        await client.post("http://fake.test/v1/chat/completions", content=b"compiler")
        response = await client.post("http://fake.test/v1/responses", content=b"inference")
        await response.aread()
    snapshot = observer.snapshot()
    assert snapshot["compiler_attempted_count"] == 1
    assert snapshot["inference_attempted_count"] == 1
    assert snapshot["compiler_completed_count"] == 1
    assert snapshot["inference_terminal_valid_count"] == 1
    assert snapshot["validator_source"] == "test"
    serialized = json.dumps(snapshot, sort_keys=True)
    assert "/v1/" not in serialized


@pytest.mark.asyncio
async def test_semantic_negatives_latch_and_retain_only_closed_classes() -> None:
    cases = (
        _stream_bytes(completed_id="response-2"),
        _stream_bytes(completed_status="failed"),
        _stream_bytes(usage={"input_tokens": 1}),
        _stream_bytes(output=[]),
        _stream_bytes(event_type="response.unknown"),
    )
    for payload in cases:
        observer = DirectTransportObserver(
            httpx.MockTransport(
                lambda _request, payload=payload: httpx.Response(
                    200,
                    headers={"content-type": "text/event-stream"},
                    stream=_ChunkStream((payload,)),
                )
            ),
            validator_factory=_validator,
            validator_source="test",
        )
        async with httpx.AsyncClient(transport=observer) as client:
            response = await client.post("http://fake.test/v1/responses", content=b"synthetic")
            await response.aread()
        snapshot = observer.snapshot()
        assert snapshot["ready"] is False
        assert snapshot["inference_terminal_valid_count"] == 0
        serialized = json.dumps(snapshot, sort_keys=True)
        assert "response-2" not in serialized
        assert "unknown" not in serialized
        assert all(
            event
            in {
                "response.created",
                "response.in_progress",
                "response.output_text.delta",
                "response.completed",
                "error",
                "other",
            }
            for event in snapshot["records"][0]["event_type_classes"]  # type: ignore[index]
        )


@pytest.mark.asyncio
async def test_malformed_or_overflow_stream_latches_before_later_dispatch() -> None:
    calls = 0
    malformed = b"event: response.created\ndata: not-json\n\n"

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        payload = malformed if calls == 1 else _stream_bytes()
        if request.url.path == "/v1/chat/completions":
            return httpx.Response(200, content=b"ok")
        return httpx.Response(
            200,
            headers={"content-type": "text/event-stream"},
            stream=_ChunkStream((payload, b"x" * (MAX_STREAM_BYTES + 1))),
        )

    observer = DirectTransportObserver(
        httpx.MockTransport(handler), validator_factory=_validator, validator_source="test"
    )
    async with httpx.AsyncClient(transport=observer) as client:
        response = await client.post("http://fake.test/v1/responses", content=b"first")
        await response.aread()
        with pytest.raises(RuntimeError, match="transport_observer_not_ready"):
            await client.post("http://fake.test/v1/responses", content=b"second")
    assert calls == 1
    assert observer.snapshot()["failure_class"] in {
        "stream_framing_invalid",
        "stream_overflow",
    }


@pytest.mark.asyncio
async def test_delegate_error_is_fixed_class_and_stops_dispatch() -> None:
    calls = 0

    def handler(_request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        raise ValueError("private-error-value")

    observer = DirectTransportObserver(httpx.MockTransport(handler))
    async with httpx.AsyncClient(transport=observer) as client:
        with pytest.raises(ValueError, match="private-error-value"):
            await client.post("http://private.invalid/v1/responses", content=b"synthetic")
        with pytest.raises(RuntimeError, match="transport_observer_not_ready"):
            await client.post("http://private.invalid/v1/responses", content=b"synthetic")
    record = observer.snapshot()["records"][0]  # type: ignore[index]
    assert record["exception_class"] == "delegate_error"
    assert "private-error-value" not in json.dumps(observer.snapshot())
    assert calls == 1


def test_exact_counts_reject_bucket_collisions() -> None:
    snapshot = {
        "compiler_attempted_count": 5,
        "compiler_dispatched_count": 5,
        "inference_attempted_count": 5,
        "inference_dispatched_count": 5,
        "inference_terminal_valid_count": 5,
        "compiler_attempted_count_class": "5+",
        "inference_attempted_count_class": "5+",
        "inference_terminal_valid_count_class": "5+",
    }
    assert observer_dispatch_matches_fake(snapshot, compiler_calls=5, inference_calls=5)
    assert not observer_dispatch_matches_fake(snapshot, compiler_calls=50, inference_calls=50)


def test_merge_assigns_global_ordinals_and_preserves_failed_lifetime() -> None:
    first: dict[str, object] = {
        "ready": False,
        "failure_class": "stream_validation_invalid",
        "records": ({"ordinal": 1, "kind": "inference", "terminal_valid": False},),
    }
    second: dict[str, object] = {
        "ready": True,
        "failure_class": None,
        "records": ({"ordinal": 1, "kind": "inference", "terminal_valid": True},),
    }
    merged = merge_observer_snapshots(first, second)
    records = cast(tuple[dict[str, object], ...], merged["records"])
    assert merged["ready"] is False
    assert [record["ordinal"] for record in records] == [1, 2]
    assert [record["lifetime_ordinal"] for record in records] == [1, 1]


def test_merge_rejects_missing_or_duplicate_lifetime_ordinals() -> None:
    with pytest.raises(ValueError, match="observer_ordinal_collision"):
        merge_observer_snapshots({"ready": True, "records": ({"ordinal": 2, "kind": "inference"},)})


def test_stream_caps_are_bounded_constants() -> None:
    assert MAX_EVENT_BYTES == 16 * 1024
    assert MAX_STREAM_BYTES == 128 * 1024

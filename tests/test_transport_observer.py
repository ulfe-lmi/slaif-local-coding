from __future__ import annotations

import asyncio
import json
from collections.abc import AsyncIterator

import httpx
import pytest

from tests.helpers.transport_observer import DirectTransportObserver


def _frame(event_type: str, payload: dict[str, object]) -> bytes:
    return (
        f"event: {event_type}\n".encode()
        + b"data: "
        + json.dumps(payload, separators=(",", ":")).encode()
        + b"\n\n"
    )


def _stream_bytes() -> bytes:
    return b"".join(
        (
            _frame("response.created", {"response": {"status": "in_progress"}}),
            _frame("response.reasoning_text.delta", {"delta": "x"}),
            _frame(
                "response.completed",
                {
                    "response": {
                        "status": "completed",
                        "usage": {"input_tokens": 1, "output_tokens": 1, "total_tokens": 2},
                    }
                },
            ),
        )
    )


class _ChunkStream(httpx.AsyncByteStream):
    def __init__(self, chunks: tuple[bytes, ...]) -> None:
        self._chunks = chunks

    async def __aiter__(self) -> AsyncIterator[bytes]:
        for chunk in self._chunks:
            await asyncio.sleep(0)
            yield chunk

    async def aclose(self) -> None:
        return


@pytest.mark.asyncio
async def test_direct_observer_preserves_stream_and_records_terminal_facts() -> None:
    expected = _stream_bytes()

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/v1/responses"
        return httpx.Response(
            200,
            headers={"content-type": "text/event-stream"},
            stream=_ChunkStream((expected[:11], expected[11:])),
        )

    observer = DirectTransportObserver(httpx.MockTransport(handler))
    async with httpx.AsyncClient(transport=observer) as client:
        response = await client.post("http://fake.test/v1/responses", content=b"synthetic")
        received = b"".join([chunk async for chunk in response.aiter_bytes()])
    assert received == expected
    snapshot = observer.snapshot()
    assert snapshot["attempted_count_class"] == "1"
    assert snapshot["inference_terminal_valid_count_class"] == "1"
    assert snapshot["inference_first_byte_count_class"] == "1"
    assert snapshot["inference_normal_close_count_class"] == "1"
    assert snapshot["records"][0]["completed"] is True  # type: ignore[index]


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

    observer = DirectTransportObserver(httpx.MockTransport(handler))
    async with httpx.AsyncClient(transport=observer) as client:
        await client.post("http://fake.test/v1/chat/completions", content=b"compiler")
        response = await client.post("http://fake.test/v1/responses", content=b"inference")
        await response.aread()
    snapshot = observer.snapshot()
    assert snapshot["compiler_attempted_count_class"] == "1"
    assert snapshot["inference_attempted_count_class"] == "1"
    assert snapshot["compiler_completed_count_class"] == "1"
    assert snapshot["inference_terminal_valid_count_class"] == "1"
    serialized = json.dumps(snapshot, sort_keys=True)
    assert "compiler" not in serialized or '"kind": "compiler"' in serialized
    assert "inference" not in serialized or '"kind": "inference"' in serialized


@pytest.mark.asyncio
async def test_observer_stops_dispatch_after_readiness_loss() -> None:
    calls = 0

    def handler(_request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        return httpx.Response(200, content=b"ok")

    observer = DirectTransportObserver(httpx.MockTransport(handler))
    observer.mark_unready()
    async with httpx.AsyncClient(transport=observer) as client:
        with pytest.raises(RuntimeError, match="observer_request_bound|observer_not_ready"):
            await client.post("http://fake.test/v1/responses", content=b"blocked")
    assert calls == 0
    assert observer.snapshot()["attempted_count_class"] == "0"


@pytest.mark.asyncio
async def test_malformed_or_overflow_stream_never_becomes_terminal_valid() -> None:
    malformed = b"event: response.created\ndata: not-json\n\n"

    def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            headers={"content-type": "text/event-stream"},
            stream=_ChunkStream((malformed, b"x" * (128 * 1024 + 1))),
        )

    observer = DirectTransportObserver(httpx.MockTransport(handler))
    async with httpx.AsyncClient(transport=observer) as client:
        response = await client.post("http://fake.test/v1/responses", content=b"synthetic")
        await response.aread()
    assert observer.snapshot()["inference_terminal_valid_count_class"] == "0"

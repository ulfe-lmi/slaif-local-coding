from __future__ import annotations

import asyncio
import json
from collections.abc import AsyncIterator, Callable, Mapping
from contextlib import suppress
from pathlib import Path
from typing import cast

import httpx
import pytest

from tests.helpers.acceptance_harness import BudgetController, RehearsalBudget
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


class _CountingChunkStream(_ChunkStream):
    def __init__(self, chunks: tuple[bytes, ...]) -> None:
        super().__init__(chunks)
        self.close_calls = 0

    async def aclose(self) -> None:
        self.close_calls += 1
        await super().aclose()


class _ErrorStream(_CountingChunkStream):
    async def __aiter__(self) -> AsyncIterator[bytes]:
        yield b"partial"
        raise RuntimeError("synthetic-stream-error")


class _CloseErrorStream(_CountingChunkStream):
    async def __aiter__(self) -> AsyncIterator[bytes]:
        yield b"partial"
        raise RuntimeError("synthetic-stream-error")

    async def aclose(self) -> None:
        self.close_calls += 1
        raise RuntimeError("synthetic-close-error")


class _BlockingStream(_CountingChunkStream):
    def __init__(self) -> None:
        super().__init__((b"partial",))
        self.started = asyncio.Event()
        self.release = asyncio.Event()

    async def __aiter__(self) -> AsyncIterator[bytes]:
        yield b"partial"
        self.started.set()
        await self.release.wait()


class _AdvancingChunkStream(_CountingChunkStream):
    def __init__(self, chunks: tuple[bytes, ...], advance: Callable[[], None]) -> None:
        super().__init__(chunks)
        self._advance = advance

    async def __aiter__(self) -> AsyncIterator[bytes]:
        for chunk in self._chunks:
            yield chunk
            self._advance()


class _BlockingTransport(httpx.AsyncBaseTransport):
    def __init__(self) -> None:
        self.calls = 0
        self.started = asyncio.Event()
        self.release = asyncio.Event()

    async def handle_async_request(self, _request: httpx.Request) -> httpx.Response:
        self.calls += 1
        self.started.set()
        await self.release.wait()
        return httpx.Response(200, content=b'{"choices":[]}')

    async def aclose(self) -> None:
        return


class _WrappingAsyncTransport(httpx.AsyncBaseTransport):
    """Wrap real AsyncHTTPTransport responses to count delegate stream closure."""

    def __init__(self) -> None:
        self.inner = httpx.AsyncHTTPTransport(retries=0)
        self.dispatches = 0
        self.close_calls = 0

    async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
        self.dispatches += 1
        response = await self.inner.handle_async_request(request)
        response.stream = _CountingNetworkStream(cast(httpx.AsyncByteStream, response.stream), self)
        return response

    async def aclose(self) -> None:
        await self.inner.aclose()


class _CountingNetworkStream(httpx.AsyncByteStream):
    def __init__(self, stream: httpx.AsyncByteStream, owner: _WrappingAsyncTransport) -> None:
        self.stream = stream
        self.owner = owner

    async def __aiter__(self) -> AsyncIterator[bytes]:
        async for chunk in self.stream:
            yield chunk

    async def aclose(self) -> None:
        self.owner.close_calls += 1
        await self.stream.aclose()


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
@pytest.mark.parametrize("path", ("/v1/chat/completions", "/v1/responses"))
async def test_normal_exhaustion_closes_json_and_sse_delegate_once(path: str) -> None:
    is_sse = path == "/v1/responses"
    stream = _CountingChunkStream((_stream_bytes() if is_sse else b'{"choices":[]}',))

    def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            headers={"content-type": "text/event-stream" if is_sse else "application/json"},
            stream=stream,
        )

    observer = DirectTransportObserver(
        httpx.MockTransport(handler), validator_factory=_validator, validator_source="test"
    )
    async with httpx.AsyncClient(transport=observer) as client:
        request = client.build_request("POST", f"http://fake.test{path}", content=b"synthetic")
        response = await client.send(request, stream=True)
        await response.aread()
        await response.aclose()
        await response.aclose()
    assert stream.close_calls == 1
    assert observer.snapshot()["records"][0]["completed"] is True  # type: ignore[index]


@pytest.mark.asyncio
async def test_real_async_http_transport_preserves_first_chunk_and_closes_connection() -> None:
    expected = _stream_bytes()
    separator = expected.index(b"\n\n") + 2
    first = expected[:separator]
    remainder = expected[separator:]
    release_terminal = asyncio.Event()
    first_written = asyncio.Event()
    server_done = asyncio.Event()
    terminal_written = False

    async def handler(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        nonlocal terminal_written
        try:
            headers = await reader.readuntil(b"\r\n\r\n")
            content_length = next(
                (
                    int(line.split(b":", 1)[1].strip())
                    for line in headers.split(b"\r\n")
                    if line.lower().startswith(b"content-length:")
                ),
                0,
            )
            if content_length:
                await reader.readexactly(content_length)
            writer.write(
                b"HTTP/1.1 200 OK\r\n"
                b"Content-Type: text/event-stream\r\n"
                b"X-Observer-Test: loopback\r\n"
                b"Connection: close\r\n\r\n" + first
            )
            await writer.drain()
            first_written.set()
            await release_terminal.wait()
            terminal_written = True
            writer.write(remainder)
            await writer.drain()
        finally:
            writer.close()
            await writer.wait_closed()
            server_done.set()

    server = await asyncio.start_server(handler, "127.0.0.1", 0)
    serve_task = asyncio.create_task(server.serve_forever())
    delegate = _WrappingAsyncTransport()
    observer = DirectTransportObserver(
        delegate, validator_factory=_validator, validator_source="test"
    )
    received: list[bytes] = []
    try:
        async with httpx.AsyncClient(transport=observer, timeout=5) as client:
            async with client.stream(
                "POST",
                f"http://127.0.0.1:{server.sockets[0].getsockname()[1]}/v1/responses",
                content=b"synthetic",
            ) as response:
                assert response.status_code == 200
                assert response.headers["x-observer-test"] == "loopback"
                async for chunk in response.aiter_raw():
                    received.append(chunk)
                    if len(received) == 1:
                        await asyncio.wait_for(first_written.wait(), timeout=1)
                        assert terminal_written is False
                        release_terminal.set()
    finally:
        release_terminal.set()
        await asyncio.wait_for(server_done.wait(), timeout=1)
        server.close()
        await server.wait_closed()
        serve_task.cancel()
        with suppress(asyncio.CancelledError):
            await serve_task

    assert b"".join(received) == expected
    assert delegate.dispatches == 1
    assert delegate.close_calls == 1
    snapshot = observer.snapshot()
    assert snapshot["inference_attempted_count"] == 1
    assert snapshot["inference_terminal_valid_count"] == 1


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
async def test_early_close_is_idempotent_and_closes_delegate_once() -> None:
    stream = _CountingChunkStream((b"partial",))
    observer = DirectTransportObserver(
        httpx.MockTransport(
            lambda _request: httpx.Response(
                200, headers={"content-type": "application/json"}, stream=stream
            )
        )
    )
    async with httpx.AsyncClient(transport=observer) as client:
        request = client.build_request("POST", "http://fake.test/v1/chat/completions")
        response = await client.send(request, stream=True)
        await response.aclose()
        await response.aclose()
    assert stream.close_calls == 1
    record = observer.snapshot()["records"][0]  # type: ignore[index]
    assert record["terminal_valid"] is False
    assert observer.ready is False


@pytest.mark.asyncio
async def test_cancelled_stream_closes_delegate_once_and_preserves_cancellation() -> None:
    stream = _BlockingStream()
    observer = DirectTransportObserver(
        httpx.MockTransport(
            lambda _request: httpx.Response(
                200, headers={"content-type": "application/json"}, stream=stream
            )
        )
    )
    async with httpx.AsyncClient(transport=observer) as client:
        request = client.build_request("POST", "http://fake.test/v1/chat/completions")
        response = await client.send(request, stream=True)
        read_task = asyncio.create_task(response.aread())
        await asyncio.wait_for(stream.started.wait(), timeout=1)
        read_task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await read_task
        await response.aclose()
    assert stream.close_calls == 1
    assert observer.snapshot()["records"][0]["exception_class"] == "cancelled"  # type: ignore[index]


@pytest.mark.asyncio
async def test_timeout_stream_closes_delegate_once() -> None:
    stream = _BlockingStream()
    observer = DirectTransportObserver(
        httpx.MockTransport(
            lambda _request: httpx.Response(
                200, headers={"content-type": "application/json"}, stream=stream
            )
        )
    )
    async with httpx.AsyncClient(transport=observer) as client:
        request = client.build_request("POST", "http://fake.test/v1/chat/completions")
        response = await client.send(request, stream=True)
        with pytest.raises(asyncio.TimeoutError):
            await asyncio.wait_for(response.aread(), timeout=0.05)
        await response.aclose()
    assert stream.close_calls == 1
    assert observer.snapshot()["records"][0]["terminal_valid"] is False  # type: ignore[index]


@pytest.mark.asyncio
async def test_truncated_stream_closes_delegate_once_and_is_not_terminal_valid() -> None:
    stream = _CountingChunkStream((_stream_bytes()[:-2],))
    observer = DirectTransportObserver(
        httpx.MockTransport(
            lambda _request: httpx.Response(
                200, headers={"content-type": "text/event-stream"}, stream=stream
            )
        ),
        validator_factory=_validator,
        validator_source="test",
    )
    async with httpx.AsyncClient(transport=observer) as client:
        response = await client.post("http://fake.test/v1/responses", content=b"synthetic")
        await response.aread()
        await response.aclose()
    assert stream.close_calls == 1
    record = observer.snapshot()["records"][0]  # type: ignore[index]
    assert record["normal_close"] is True
    assert record["terminal_valid"] is False
    assert observer.ready is False


@pytest.mark.asyncio
async def test_stream_exception_preserves_original_error_and_closes_once() -> None:
    stream = _ErrorStream((b"partial",))
    observer = DirectTransportObserver(
        httpx.MockTransport(
            lambda _request: httpx.Response(
                200, headers={"content-type": "application/json"}, stream=stream
            )
        )
    )
    async with httpx.AsyncClient(transport=observer) as client:
        request = client.build_request("POST", "http://fake.test/v1/chat/completions")
        response = await client.send(request, stream=True)
        with pytest.raises(RuntimeError, match="synthetic-stream-error"):
            await response.aread()
        await response.aclose()
    assert stream.close_calls == 1
    assert observer.snapshot()["records"][0]["exception_class"] == "stream_error"  # type: ignore[index]


@pytest.mark.asyncio
async def test_close_error_does_not_replace_original_stream_error() -> None:
    stream = _CloseErrorStream((b"partial",))

    observer = DirectTransportObserver(
        httpx.MockTransport(
            lambda _request: httpx.Response(
                200, headers={"content-type": "application/json"}, stream=stream
            )
        )
    )
    async with httpx.AsyncClient(transport=observer) as client:
        request = client.build_request("POST", "http://fake.test/v1/chat/completions")
        response = await client.send(request, stream=True)
        with pytest.raises(RuntimeError, match="synthetic-stream-error"):
            await response.aread()
    assert stream.close_calls == 1


@pytest.mark.asyncio
@pytest.mark.parametrize("factory_kind", ("missing", "raising", "invalid"))
async def test_validator_profile_preflight_blocks_inference_before_delegate(
    factory_kind: str,
) -> None:
    calls = 0

    def handler(_request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        return httpx.Response(200, content=b"should-not-dispatch")

    def raising_factory(_request: httpx.Request) -> _AcceptingValidator:
        raise ValueError("synthetic-profile-error")

    def invalid_factory(_request: httpx.Request) -> object:
        return object()

    factory = {
        "missing": None,
        "raising": raising_factory,
        "invalid": invalid_factory,
    }[factory_kind]
    observer = DirectTransportObserver(
        httpx.MockTransport(handler),
        validator_factory=factory,  # type: ignore[arg-type]
        validator_source="test",
    )
    assert observer.ready is True
    async with httpx.AsyncClient(transport=observer) as client:
        with pytest.raises(RuntimeError, match="transport_observer_validator_unavailable"):
            await client.post("http://fake.test/v1/responses", content=b"invalid-profile")
        with pytest.raises(RuntimeError, match="transport_observer_not_ready"):
            await client.post("http://fake.test/v1/responses", content=b"second")
    assert calls == 0
    snapshot = observer.snapshot()
    assert snapshot["ready"] is False
    assert snapshot["inference_dispatched_count"] == 0
    record = snapshot["records"][0]  # type: ignore[index]
    assert record["attempted"] is True
    assert record["dispatched"] is False
    assert record["exception_class"] == "validator_error"


def test_candidate_preflight_reports_missing_inference_capability(tmp_path: Path) -> None:
    from scripts.gateway_accounting_rehearsal import _build_observed_candidate

    observer = DirectTransportObserver(httpx.MockTransport(lambda _request: httpx.Response(200)))
    with pytest.raises(RuntimeError, match="candidate_observer_capability_unavailable"):
        _build_observed_candidate(tmp_path, observer=observer)


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
            await client.post("http://private.invalid/v1/chat/completions", content=b"synthetic")
        with pytest.raises(RuntimeError, match="transport_observer_not_ready"):
            await client.post("http://private.invalid/v1/chat/completions", content=b"synthetic")
    record = observer.snapshot()["records"][0]  # type: ignore[index]
    assert record["exception_class"] == "delegate_error"
    assert "private-error-value" not in json.dumps(observer.snapshot())
    assert calls == 1


@pytest.mark.asyncio
async def test_run_budget_admits_each_actual_dispatch_and_attributes_context() -> None:
    now = [0.0]
    budget = BudgetController(
        RehearsalBudget(wall_seconds=5, max_dispatches=1), clock=lambda: now[0]
    )
    budget.set_dispatch_context("vision", 4)
    calls = 0

    def handler(_request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        return httpx.Response(
            200,
            headers={"content-type": "text/event-stream"},
            stream=_ChunkStream((_stream_bytes(),)),
        )

    observer = DirectTransportObserver(
        httpx.MockTransport(handler),
        validator_factory=_validator,
        validator_source="test",
        budget_controller=budget,
        dispatch_context=budget.dispatch_context,
    )
    async with httpx.AsyncClient(transport=observer) as client:
        response = await client.post("http://fake.test/v1/responses", content=b"synthetic")
        await response.aread()
        with pytest.raises(RuntimeError, match="budget_not_admitted"):
            await client.post("http://fake.test/v1/responses", content=b"synthetic")
    assert calls == 1
    record = observer.snapshot()["records"][0]  # type: ignore[index]
    assert record["dispatch_phase"] == "vision"
    assert record["dispatch_ordinal"] == 4
    assert record["dispatch_admitted"] is True
    assert budget.safe_dict()["dispatch_admitted_count"] == 1
    assert observer.snapshot()["records"][1]["dispatched"] is False  # type: ignore[index]


@pytest.mark.asyncio
async def test_run_budget_deadline_is_checked_between_stream_chunks() -> None:
    now = [0.0]
    budget = BudgetController(RehearsalBudget(wall_seconds=5), clock=lambda: now[0])
    expected = _stream_bytes()
    separator = expected.index(b"\n\n") + 2
    stream = _AdvancingChunkStream(
        (expected[:separator], expected[separator:]), lambda: now.__setitem__(0, 5.0)
    )
    observer = DirectTransportObserver(
        httpx.MockTransport(
            lambda _request: httpx.Response(
                200, headers={"content-type": "text/event-stream"}, stream=stream
            )
        ),
        validator_factory=_validator,
        validator_source="test",
        budget_controller=budget,
        dispatch_context=lambda: ("codex", 2),
    )
    async with httpx.AsyncClient(transport=observer) as client:
        with pytest.raises(RuntimeError, match="budget_exhausted"):
            await client.post("http://fake.test/v1/responses", content=b"synthetic")
    assert observer.snapshot()["failure_class"] == "budget_deadline_exhausted"
    assert observer.snapshot()["records"][0]["terminal_valid"] is False  # type: ignore[index]
    assert stream.close_calls == 1


@pytest.mark.asyncio
async def test_run_budget_rejects_event_overflow_without_second_delegate_call() -> None:
    budget = BudgetController(
        RehearsalBudget(max_event_bytes=4, max_stream_bytes=32, max_dispatches=2)
    )
    calls = 0

    def handler(_request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        return httpx.Response(
            200, headers={"content-type": "application/json"}, stream=_ChunkStream((b"12345",))
        )

    observer = DirectTransportObserver(
        httpx.MockTransport(handler),
        budget_controller=budget,
        dispatch_context=lambda: ("codex", 1),
    )
    async with httpx.AsyncClient(transport=observer) as client:
        with pytest.raises(RuntimeError, match="budget_exhausted"):
            await client.post("http://fake.test/v1/chat/completions", content=b"synthetic")
        with pytest.raises(RuntimeError, match="observer_not_ready"):
            await client.post("http://fake.test/v1/chat/completions", content=b"synthetic")
    assert calls == 1
    assert budget.failure == "budget_event_limit_exhausted"


@pytest.mark.asyncio
async def test_run_budget_holds_concurrency_until_stream_lifetime_ends() -> None:
    budget = BudgetController(RehearsalBudget(max_dispatches=4))
    delegate = _BlockingTransport()
    observer = DirectTransportObserver(
        delegate,
        budget_controller=budget,
        dispatch_context=lambda: ("codex", 1),
    )
    async with httpx.AsyncClient(transport=observer) as client:
        first_task = asyncio.create_task(
            client.post("http://fake.test/v1/chat/completions", content=b"first")
        )
        await asyncio.wait_for(delegate.started.wait(), timeout=1)
        with pytest.raises(RuntimeError, match="budget_not_admitted"):
            await client.post("http://fake.test/v1/chat/completions", content=b"second")
        delegate.release.set()
        with suppress(RuntimeError):
            await first_task
    assert delegate.calls == 1
    assert budget.failure == "budget_concurrency_limit_exhausted"


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

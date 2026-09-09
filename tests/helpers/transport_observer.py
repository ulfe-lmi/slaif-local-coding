"""Acceptance-only direct HTTPX transport observation.

The observer sits inside the disposable Local candidate.  It delegates the
same ``httpx.Request`` and response stream to the real network transport while
retaining only bounded, fixed-class facts.  It is deliberately not a relay,
production middleware, or provider instrumentation.
"""

from __future__ import annotations

import asyncio
import json
import time
from collections.abc import AsyncIterator
from dataclasses import dataclass, field
from typing import cast

import httpx

MAX_OBSERVED_REQUESTS = 64
MAX_EVENT_BYTES = 16 * 1024
MAX_STREAM_BYTES = 128 * 1024
MAX_EVENT_TYPES = 32


def _status_class(status: int) -> str:
    return f"{status // 100}xx" if 100 <= status <= 599 else "unknown"


def _count_class(value: int) -> str:
    if value < 0:
        return "unknown"
    if value == 0:
        return "0"
    if value == 1:
        return "1"
    if value == 2:
        return "2"
    if value <= 4:
        return "3-4"
    return "5+"


@dataclass
class _StreamState:
    content_type: str
    started: float
    buffer: bytes = b""
    byte_count: int = 0
    event_types: list[str] = field(default_factory=list)
    created_count: int = 0
    completed_count: int = 0
    error_event: bool = False
    malformed: bool = False
    overflow: bool = False
    terminal_status_valid: bool = False
    terminal_usage_valid: bool = False
    first_byte: bool = False
    terminal_event: bool = False
    normal_close: bool = False

    def consume(self, chunk: bytes) -> None:
        if not chunk:
            return
        if not self.first_byte:
            self.first_byte = True
        self.byte_count += len(chunk)
        if self.byte_count > MAX_STREAM_BYTES:
            self.overflow = True
            return
        self.buffer += chunk
        if len(self.buffer) > MAX_EVENT_BYTES:
            self.overflow = True
            self.buffer = b""
            return
        while b"\n\n" in self.buffer:
            frame, self.buffer = self.buffer.split(b"\n\n", 1)
            self._consume_frame(frame)

    def _consume_frame(self, frame: bytes) -> None:
        if not frame or len(frame) > MAX_EVENT_BYTES:
            self.malformed = True
            return
        event_name: str | None = None
        data_parts: list[bytes] = []
        for line in frame.replace(b"\r\n", b"\n").split(b"\n"):
            if line.startswith(b"event:"):
                try:
                    event_name = line[6:].strip().decode("ascii")
                except UnicodeDecodeError:
                    self.malformed = True
            elif line.startswith(b"data:"):
                data_parts.append(line[5:].lstrip())
            elif line.startswith(b":") or not line:
                continue
            else:
                self.malformed = True
        if event_name is None or len(data_parts) != 1:
            self.malformed = True
            return
        if len(data_parts[0]) > MAX_EVENT_BYTES:
            self.overflow = True
            return
        if len(self.event_types) < MAX_EVENT_TYPES:
            self.event_types.append(event_name)
        else:
            self.overflow = True
        try:
            payload = json.loads(data_parts[0])
        except (UnicodeDecodeError, json.JSONDecodeError, TypeError, ValueError):
            self.malformed = True
            return
        if not isinstance(payload, dict) or not isinstance(event_name, str):
            self.malformed = True
            return
        if event_name == "error":
            self.error_event = True
            return
        if event_name == "response.unknown":
            self.malformed = True
        elif not event_name.startswith("response."):
            self.malformed = True
        if event_name == "response.created":
            self.created_count += 1
        elif event_name == "response.completed":
            self.completed_count += 1
            self.terminal_event = True
            response = payload.get("response")
            if isinstance(response, dict):
                self.terminal_status_valid = response.get("status") == "completed"
                usage = response.get("usage")
                self.terminal_usage_valid = isinstance(usage, dict) and all(
                    isinstance(usage.get(name), int)
                    and not isinstance(usage.get(name), bool)
                    and usage.get(name, 0) > 0
                    for name in ("input_tokens", "output_tokens", "total_tokens")
                )

    def finish(self) -> None:
        if self.buffer:
            self.malformed = True
        self.normal_close = True

    @property
    def terminal_valid(self) -> bool:
        return (
            self.normal_close
            and self.first_byte
            and not self.malformed
            and not self.overflow
            and not self.error_event
            and self.created_count == 1
            and self.completed_count == 1
            and self.event_types[-1:] == ["response.completed"]
            and self.terminal_status_valid
            and self.terminal_usage_valid
        )


@dataclass
class _RequestObservation:
    ordinal: int
    kind: str
    path: str
    attempted: bool = True
    dispatched: bool = True
    responded: bool = False
    completed: bool = False
    status_class: str = "unknown"
    content_type_class: str = "unknown"
    first_byte: bool = False
    terminal_valid: bool = False
    normal_close: bool = False
    stream_bytes_class: str = "0"
    event_count_class: str = "0"
    event_type_classes: tuple[str, ...] = ()
    exception_class: str | None = None

    def safe_dict(self) -> dict[str, object]:
        return {
            "ordinal": self.ordinal,
            "kind": self.kind,
            "path": self.path,
            "attempted": self.attempted,
            "dispatched": self.dispatched,
            "responded": self.responded,
            "completed": self.completed,
            "status_class": self.status_class,
            "content_type_class": self.content_type_class,
            "first_byte": self.first_byte,
            "terminal_valid": self.terminal_valid,
            "normal_close": self.normal_close,
            "stream_bytes_class": self.stream_bytes_class,
            "event_count_class": self.event_count_class,
            "event_type_classes": self.event_type_classes,
            "exception_class": self.exception_class,
        }


class _ObservedStream(httpx.AsyncByteStream):
    def __init__(
        self,
        stream: httpx.AsyncByteStream,
        owner: DirectTransportObserver,
        record: _RequestObservation,
        state: _StreamState,
    ) -> None:
        self._stream = stream
        self._owner = owner
        self._record = record
        self._state = state

    async def __aiter__(self) -> AsyncIterator[bytes]:
        try:
            async for chunk in self._stream:
                self._state.consume(chunk)
                yield chunk
            self._state.finish()
            self._owner._finish_stream(self._record, self._state)
        except asyncio.CancelledError:
            raise
        except BaseException as exc:
            self._record.exception_class = type(exc).__name__
            self._record.completed = False
            raise

    async def aclose(self) -> None:
        await self._stream.aclose()


class DirectTransportObserver(httpx.AsyncBaseTransport):
    """Observe real Local-to-upstream transport dispatch without a relay."""

    def __init__(self, delegate: httpx.AsyncBaseTransport) -> None:
        self._delegate = delegate
        self._records: list[_RequestObservation] = []
        self._started = time.monotonic()
        self._ready = True

    @property
    def ready(self) -> bool:
        return self._ready and len(self._records) < MAX_OBSERVED_REQUESTS

    def mark_unready(self) -> None:
        """Stop later dispatches after an observer-side readiness failure."""
        self._ready = False

    @property
    def records(self) -> tuple[dict[str, object], ...]:
        return tuple(record.safe_dict() for record in self._records)

    def snapshot(self) -> dict[str, object]:
        records = tuple(self._records)
        compiler = tuple(record for record in records if record.kind == "compiler")
        inference = tuple(record for record in records if record.kind == "inference")
        return {
            "observer_version": "direct-httpx-v1",
            "ready": self.ready,
            "attempted_count_class": _count_class(len(records)),
            "dispatched_count_class": _count_class(sum(record.dispatched for record in records)),
            "responded_count_class": _count_class(sum(record.responded for record in records)),
            "completed_count_class": _count_class(sum(record.completed for record in records)),
            "compiler_attempted_count_class": _count_class(len(compiler)),
            "compiler_completed_count_class": _count_class(
                sum(record.completed for record in compiler)
            ),
            "inference_attempted_count_class": _count_class(len(inference)),
            "inference_completed_count_class": _count_class(
                sum(record.completed for record in inference)
            ),
            "inference_terminal_valid_count_class": _count_class(
                sum(record.terminal_valid for record in inference)
            ),
            "inference_first_byte_count_class": _count_class(
                sum(record.first_byte for record in inference)
            ),
            "inference_normal_close_count_class": _count_class(
                sum(record.normal_close for record in inference)
            ),
            "records": tuple(record.safe_dict() for record in records),
            "elapsed_class": "unknown" if time.monotonic() < self._started else "bounded",
        }

    async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
        if not self._ready:
            raise RuntimeError("transport_observer_not_ready")
        if len(self._records) >= MAX_OBSERVED_REQUESTS:
            self._ready = False
            raise RuntimeError("transport_observer_request_bound_exceeded")
        path = request.url.path
        kind = (
            "compiler"
            if path == "/v1/chat/completions"
            else "inference"
            if path == "/v1/responses"
            else "other"
        )
        record = _RequestObservation(len(self._records) + 1, kind, path)
        self._records.append(record)
        try:
            response = await self._delegate.handle_async_request(request)
        except asyncio.CancelledError:
            raise
        except BaseException as exc:
            record.exception_class = type(exc).__name__
            raise
        record.responded = True
        record.status_class = _status_class(response.status_code)
        content_type = response.headers.get("content-type", "")
        record.content_type_class = (
            "sse"
            if "text/event-stream" in content_type
            else "json"
            if "json" in content_type
            else "other"
        )
        state = _StreamState(record.content_type_class, time.monotonic())
        response.stream = _ObservedStream(
            cast(httpx.AsyncByteStream, response.stream), self, record, state
        )
        return response

    def _finish_stream(self, record: _RequestObservation, state: _StreamState) -> None:
        record.completed = True
        record.first_byte = state.first_byte
        record.terminal_valid = (
            state.terminal_valid
            if record.kind == "inference" and record.content_type_class == "sse"
            else state.normal_close and not state.overflow and not state.malformed
        )
        record.normal_close = state.normal_close
        record.stream_bytes_class = _count_class(state.byte_count)
        record.event_count_class = _count_class(len(state.event_types))
        record.event_type_classes = tuple(sorted(set(state.event_types)))

    async def aclose(self) -> None:
        await self._delegate.aclose()


def observer_dispatch_matches_fake(
    snapshot: dict[str, object], *, compiler_calls: int, inference_calls: int
) -> bool:
    """Compare independent transport dispatch counts with fake-server counts."""
    return (
        snapshot.get("compiler_attempted_count_class") == _count_class(compiler_calls)
        and snapshot.get("inference_attempted_count_class") == _count_class(inference_calls)
        and snapshot.get("inference_terminal_valid_count_class") == _count_class(inference_calls)
    )


def merge_observer_snapshots(*snapshots: dict[str, object]) -> dict[str, object]:
    """Merge sequential candidate lifetimes without retaining raw transport data."""
    records: list[dict[str, object]] = []
    ready = True
    for snapshot in snapshots:
        ready = ready and snapshot.get("ready") is True
        values = snapshot.get("records", ())
        if isinstance(values, (list, tuple)):
            records.extend(value for value in values if isinstance(value, dict))
    compiler = [record for record in records if record.get("kind") == "compiler"]
    inference = [record for record in records if record.get("kind") == "inference"]
    return {
        "observer_version": "direct-httpx-v1",
        "ready": ready,
        "attempted_count_class": _count_class(len(records)),
        "dispatched_count_class": _count_class(
            sum(record.get("dispatched") is True for record in records)
        ),
        "responded_count_class": _count_class(
            sum(record.get("responded") is True for record in records)
        ),
        "completed_count_class": _count_class(
            sum(record.get("completed") is True for record in records)
        ),
        "compiler_attempted_count_class": _count_class(len(compiler)),
        "compiler_completed_count_class": _count_class(
            sum(record.get("completed") is True for record in compiler)
        ),
        "inference_attempted_count_class": _count_class(len(inference)),
        "inference_completed_count_class": _count_class(
            sum(record.get("completed") is True for record in inference)
        ),
        "inference_terminal_valid_count_class": _count_class(
            sum(record.get("terminal_valid") is True for record in inference)
        ),
        "inference_first_byte_count_class": _count_class(
            sum(record.get("first_byte") is True for record in inference)
        ),
        "inference_normal_close_count_class": _count_class(
            sum(record.get("normal_close") is True for record in inference)
        ),
        "records": tuple(records),
        "elapsed_class": "bounded",
    }

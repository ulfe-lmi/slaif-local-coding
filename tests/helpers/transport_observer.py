"""Acceptance-only direct HTTPX transport observation.

The observer sits inside the disposable Local candidate.  It delegates the
same ``httpx.Request`` and response stream to the real network transport while
retaining only bounded, fixed-class facts.  It is deliberately not a relay,
production middleware, or provider instrumentation.

Responses SSE semantics are supplied by the accepted Gateway validator through
``validator_factory``.  This module owns framing, boundedness, and safe
observation; it does not copy Gateway event policy.
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import time
from collections.abc import AsyncIterator, Callable, Mapping
from dataclasses import dataclass, field
from typing import Protocol, cast

import httpx

from tests.helpers.acceptance_harness import DispatchContext

MAX_OBSERVED_REQUESTS = 64
MAX_EVENT_BYTES = 16 * 1024
MAX_STREAM_BYTES = 128 * 1024
MAX_EVENT_TYPES = 32

_RESPONSE_ID_EVENTS = frozenset({"response.created", "response.in_progress", "response.completed"})
_EVENT_CLASSES = {
    "response.created": "response.created",
    "response.in_progress": "response.in_progress",
    "response.output_text.delta": "response.output_text.delta",
    "response.output_text.done": "response.output_text.done",
    "response.output_item.added": "response.output_item.added",
    "response.output_item.done": "response.output_item.done",
    "response.function_call_arguments.delta": "response.function_call_arguments.delta",
    "response.function_call_arguments.done": "response.function_call_arguments.done",
    "response.custom_tool_call_input.delta": "response.custom_tool_call_input.delta",
    "response.reasoning_summary_part.added": "response.reasoning_summary_part.added",
    "response.reasoning_summary_text.delta": "response.reasoning_summary_text.delta",
    "response.reasoning_summary_text.done": "response.reasoning_summary_text.done",
    "response.reasoning_text.delta": "response.reasoning_text.delta",
    "response.reasoning_text.done": "response.reasoning_text.done",
    "response.reasoning_part.added": "response.reasoning_part.added",
    "response.reasoning_part.done": "response.reasoning_part.done",
    "response.content_part.added": "response.content_part.added",
    "response.content_part.done": "response.content_part.done",
    "response.completed": "response.completed",
    "response.failed": "error",
    "response.incomplete": "error",
    "error": "error",
}


class StreamEventValidator(Protocol):
    """Minimal interface implemented by the exact Gateway validator."""

    def validate(self, payload: Mapping[str, object] | None) -> bool: ...


ValidatorFactory = Callable[[httpx.Request], StreamEventValidator]
ResponseCompleteHook = Callable[[str, str, str, int | None, bool], None]


class DispatchBudget(Protocol):
    """Small seam for the run-owned budget controller."""

    @property
    def failure(self) -> str | None: ...

    def admit_dispatch(self, kind: str, *, context: DispatchContext | None = None) -> bool: ...

    def release_dispatch(self) -> None: ...

    def observe_chunk(self, size: int) -> bool: ...

    def observe_frame(self, size: int) -> bool: ...

    def safe_dict(self) -> dict[str, object]: ...


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


def _endpoint_class(path: str) -> str:
    return {
        "/v1/responses": "responses",
        "/v1/chat/completions": "chat_completions",
        "/health": "health",
        "/v1/models": "models",
    }.get(path, "other")


def _exception_class(kind: str) -> str:
    return {
        "cancelled": "cancelled",
        "delegate": "delegate_error",
        "stream": "stream_error",
        "validator": "validator_error",
        "not_ready": "observer_not_ready",
        "bound": "observer_bound_exceeded",
        "framing": "stream_framing_invalid",
        "validation": "stream_validation_invalid",
        "overflow": "stream_overflow",
        "closure": "stream_closure_invalid",
        "contract": "stream_contract_invalid",
        "manual": "manual_unready",
        "budget": "observer_budget_not_admitted",
        "lifetime": "observer_lifetime_mismatch",
        "readiness": "readiness_non_health",
    }.get(kind, "other")


def _safe_json_loads(value: bytes) -> object:
    def reject_constant(_value: str) -> None:
        raise ValueError("non_finite_json")

    return json.loads(value, parse_constant=reject_constant)


@dataclass
class _StreamState:
    content_type: str
    started: float
    validator: StreamEventValidator | None = None
    buffer: bytearray = field(default_factory=bytearray)
    byte_count: int = 0
    event_count: int = 0
    event_types: list[str] = field(default_factory=list)
    created_count: int = 0
    completed_count: int = 0
    error_event: bool = False
    malformed: bool = False
    validation_failed: bool = False
    overflow: bool = False
    terminal_status_valid: bool = False
    terminal_output_valid: bool = False
    terminal_usage_valid: bool = False
    first_byte: bool = False
    terminal_event: bool = False
    normal_close: bool = False
    _response_id_digest: bytes | None = field(default=None, repr=False)
    failure_kind: str | None = field(default=None, repr=False)
    frame_observer: Callable[[int], bool] | None = field(default=None, repr=False)

    def _fail(self, kind: str) -> None:
        self.validation_failed = True
        if self.failure_kind is None:
            self.failure_kind = kind

    def _append_event_class(self, event_name: str) -> None:
        self.event_count += 1
        event_class = _EVENT_CLASSES.get(event_name, "other")
        if len(self.event_types) >= MAX_EVENT_TYPES:
            self.overflow = True
            self._fail("overflow")
            return
        self.event_types.append(event_class)

    def _consume_frame(self, frame: bytes) -> None:
        if self.frame_observer is not None and not self.frame_observer(len(frame)):
            self.overflow = True
            self._fail("budget")
            return
        if not frame or len(frame) > MAX_EVENT_BYTES:
            self.malformed = True
            self._fail("framing")
            return

        event_name: str | None = None
        data_parts: list[bytes] = []
        for line in frame.replace(b"\r\n", b"\n").split(b"\n"):
            if line.startswith(b"event:"):
                if event_name is not None:
                    self.malformed = True
                    self._fail("framing")
                    continue
                try:
                    event_name = line[6:].strip().decode("ascii")
                except UnicodeDecodeError:
                    self.malformed = True
                    self._fail("framing")
            elif line.startswith(b"data:"):
                data_parts.append(line[5:].lstrip())
            elif line.startswith(b":") or not line:
                continue
            else:
                self.malformed = True
                self._fail("framing")

        # A comment-only SSE frame is valid and carries no event.  Data frames
        # without an explicit event are not part of the reviewed Gateway wire.
        if event_name is None and not data_parts:
            return
        if event_name is None or not data_parts or len(data_parts) > MAX_EVENT_TYPES:
            self.malformed = True
            self._fail("framing")
            return
        self._append_event_class(event_name)
        data = b"\n".join(data_parts)
        if len(data) > MAX_EVENT_BYTES:
            self.overflow = True
            self._fail("overflow")
            return
        try:
            payload = _safe_json_loads(data)
        except (UnicodeDecodeError, json.JSONDecodeError, TypeError, ValueError):
            self.malformed = True
            self._fail("framing")
            return
        if not isinstance(payload, dict):
            self.malformed = True
            self._fail("validation")
            return
        if payload.get("type") != event_name:
            self._fail("validation")
        if event_name == "error":
            self.error_event = True

        if event_name in _RESPONSE_ID_EVENTS:
            response = payload.get("response")
            response_id = response.get("id") if isinstance(response, Mapping) else None
            if not isinstance(response_id, str) or not response_id:
                self._fail("validation")
            else:
                response_id_digest = hashlib.sha256(response_id.encode("utf-8")).digest()
                if self._response_id_digest is None:
                    self._response_id_digest = response_id_digest
                elif response_id_digest != self._response_id_digest:
                    self._fail("validation")

        try:
            valid = self.validator is not None and self.validator.validate(
                cast(Mapping[str, object], payload)
            )
        except BaseException:
            valid = False
            self._fail("validator")
        if not valid:
            self._fail("validation" if self.failure_kind != "validator" else "validator")

        if event_name == "response.created":
            self.created_count += 1
        elif event_name == "response.completed":
            self.completed_count += 1
            self.terminal_event = True
            response = payload.get("response")
            if isinstance(response, Mapping):
                self.terminal_status_valid = response.get("status") == "completed"
                output = response.get("output")
                self.terminal_output_valid = isinstance(output, list) and bool(output)
                usage = response.get("usage")
                self.terminal_usage_valid = isinstance(usage, Mapping) and all(
                    type(usage.get(name)) is int and usage.get(name, 0) >= 0
                    for name in ("input_tokens", "output_tokens", "total_tokens")
                )

    def consume(self, chunk: bytes) -> None:
        if not chunk or self.overflow:
            return
        if not self.first_byte:
            self.first_byte = True
        if self.content_type != "sse":
            self.byte_count += len(chunk)
            if self.byte_count > MAX_STREAM_BYTES:
                self.byte_count = MAX_STREAM_BYTES + 1
                self.overflow = True
                self._fail("overflow")
            return
        for value in chunk:
            if self.byte_count >= MAX_STREAM_BYTES:
                self.byte_count = MAX_STREAM_BYTES + 1
                self.overflow = True
                self._fail("overflow")
                self.buffer.clear()
                return
            self.byte_count += 1
            self.buffer.append(value)
            delimiter_length = 0
            if self.buffer.endswith(b"\n\n"):
                delimiter_length = 2
            elif self.buffer.endswith(b"\r\n\r\n"):
                delimiter_length = 4
            if delimiter_length:
                frame_length = len(self.buffer) - delimiter_length
                frame = bytes(self.buffer[:frame_length])
                del self.buffer[:]
                self._consume_frame(frame)
                if self.failure_kind == "budget":
                    return
            elif len(self.buffer) > MAX_EVENT_BYTES + 4:
                self.overflow = True
                self._fail("overflow")
                self.buffer.clear()
                return

    def finish(self) -> None:
        if self.buffer:
            self.malformed = True
            self._fail("framing")
            self.buffer.clear()
        self.normal_close = True

    def abnormal_close(self, kind: str = "closure") -> None:
        self.buffer.clear()
        self.normal_close = False
        self._fail(kind)

    @property
    def terminal_valid(self) -> bool:
        return (
            self.normal_close
            and self.first_byte
            and self.validator is not None
            and not self.malformed
            and not self.validation_failed
            and not self.overflow
            and not self.error_event
            and self.created_count == 1
            and self.completed_count == 1
            and self.event_types[-1:] == ["response.completed"]
            and self.terminal_status_valid
            and self.terminal_output_valid
            and self.terminal_usage_valid
        )


@dataclass
class _RequestObservation:
    ordinal: int
    kind: str
    endpoint_class: str
    attempted: bool = True
    dispatched: bool = False
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
    dispatch_operation: str = "unknown"
    dispatch_phase: str = "unknown"
    dispatch_ordinal: int | None = None
    dispatch_lifetime: str | None = None
    dispatch_admitted: bool = False
    dispatch_active: bool = field(default=False, repr=False)

    def safe_dict(self) -> dict[str, object]:
        result: dict[str, object] = {
            "ordinal": self.ordinal,
            "kind": self.kind,
            "endpoint_class": self.endpoint_class,
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
        if (
            self.dispatch_admitted
            or self.dispatch_operation != "unknown"
            or self.dispatch_phase != "unknown"
            or self.dispatch_ordinal is not None
            or self.dispatch_lifetime is not None
        ):
            result.update(
                {
                    "dispatch_operation": self.dispatch_operation,
                    "dispatch_phase": self.dispatch_phase,
                    "dispatch_ordinal": self.dispatch_ordinal,
                    "dispatch_lifetime": self.dispatch_lifetime,
                    "dispatch_admitted": self.dispatch_admitted,
                }
            )
        return result


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
        self._observation_finished = False
        self._delegate_close_task: asyncio.Task[None] | None = None

    async def __aiter__(self) -> AsyncIterator[bytes]:
        try:
            async for chunk in self._stream:
                if not self._owner._observe_chunk(self._state, len(chunk)):
                    self._state.abnormal_close("budget")
                    raise RuntimeError("transport_observer_budget_exhausted")
                self._state.consume(chunk)
                self._owner._latch_state_failure(self._state)
                if self._state.failure_kind == "budget":
                    self._state.abnormal_close("budget")
                    raise RuntimeError("transport_observer_budget_exhausted")
                yield chunk
            self._state.finish()
            self._owner._finish_stream(self._record, self._state)
            self._owner._run_response_complete_hook(self._record)
            self._observation_finished = True
        except asyncio.CancelledError:
            self._record.exception_class = _exception_class("cancelled")
            self._state.abnormal_close("cancelled")
            self._owner._finish_abnormal(self._record, self._state)
            self._observation_finished = True
            try:
                await self._close_delegate(suppress_error=True)
            finally:
                self._owner._release_dispatch(self._record)
            raise
        except BaseException:
            self._record.exception_class = _exception_class("stream")
            self._state.abnormal_close("stream")
            self._owner._finish_abnormal(self._record, self._state)
            self._observation_finished = True
            try:
                await self._close_delegate(suppress_error=True)
            finally:
                self._owner._release_dispatch(self._record)
            raise
        try:
            await self._close_delegate(suppress_error=False)
        except BaseException:
            self._state.abnormal_close("closure")
            self._owner._finish_delegate_close_failure(self._record, self._state)
            self._owner._release_dispatch(self._record)
            raise
        self._owner._release_dispatch(self._record)

    async def _close_delegate(self, *, suppress_error: bool) -> None:
        if self._delegate_close_task is None:
            self._delegate_close_task = asyncio.create_task(self._stream.aclose())
        try:
            await asyncio.shield(self._delegate_close_task)
        except asyncio.CancelledError:
            try:
                await self._delegate_close_task
            except BaseException:
                pass
            if not suppress_error:
                raise
        except BaseException:
            if not suppress_error:
                raise
            # The caller's original cancellation/stream error is authoritative.

    async def aclose(self) -> None:
        if not self._observation_finished:
            self._state.abnormal_close("closure")
            self._owner._finish_abnormal(self._record, self._state)
            self._observation_finished = True
        try:
            await self._close_delegate(suppress_error=False)
        finally:
            self._owner._release_dispatch(self._record)


class DirectTransportObserver(httpx.AsyncBaseTransport):
    """Observe real Local-to-upstream transport dispatch without a relay."""

    def __init__(
        self,
        delegate: httpx.AsyncBaseTransport,
        *,
        validator_factory: ValidatorFactory | None = None,
        validator_source: str = "unavailable",
        budget_controller: DispatchBudget | None = None,
        dispatch_context: Callable[[], DispatchContext | None] | None = None,
        dispatch_hook: Callable[[str, str, int | None], None] | None = None,
        dispatch_complete_hook: Callable[[str, str, int | None], None] | None = None,
        response_complete_hook: ResponseCompleteHook | None = None,
        allowed_lifetime_ids: tuple[str, ...] | None = None,
        expected_lifetime_id: str | None = None,
    ) -> None:
        self._delegate = delegate
        self._validator_factory = validator_factory
        self._validator_source = (
            validator_source if validator_factory is not None else "unavailable"
        )
        self._budget_controller = budget_controller
        self._dispatch_context = dispatch_context
        self._dispatch_hook = dispatch_hook
        self._dispatch_complete_hook = dispatch_complete_hook
        self._response_complete_hook = response_complete_hook
        self._allowed_lifetime_ids = (
            allowed_lifetime_ids
            if allowed_lifetime_ids is not None
            else ((expected_lifetime_id,) if expected_lifetime_id is not None else None)
        )
        self._records: list[_RequestObservation] = []
        self._started = time.monotonic()
        self._ready = True
        self._failure_class: str | None = None

    @property
    def ready(self) -> bool:
        return self._ready and len(self._records) < MAX_OBSERVED_REQUESTS

    @property
    def inference_capability_ready(self) -> bool:
        """Whether Responses admission can construct its required validator."""
        return self._validator_factory is not None

    @property
    def budget_controller(self) -> DispatchBudget | None:
        return self._budget_controller

    def _latch_failure(self, kind: str) -> None:
        self._ready = False
        if self._failure_class is None:
            self._failure_class = (
                kind
                if kind.startswith("budget_") or kind == "observer_budget_not_admitted"
                else _exception_class(kind)
            )

    def _latch_budget_failure(self) -> None:
        failure = getattr(self._budget_controller, "failure", None)
        self._latch_failure(
            failure if isinstance(failure, str) and failure.startswith("budget_") else "budget"
        )

    def _latch_state_failure(self, state: _StreamState) -> None:
        if state.failure_kind is not None:
            if state.failure_kind == "budget":
                self._latch_budget_failure()
            else:
                self._latch_failure(state.failure_kind)

    def mark_unready(self) -> None:
        """Stop later dispatches after an observer-side readiness failure."""
        self._latch_failure("manual")

    @property
    def records(self) -> tuple[dict[str, object], ...]:
        return tuple(record.safe_dict() for record in self._records)

    @staticmethod
    def _counts(records: tuple[_RequestObservation, ...]) -> dict[str, int]:
        compiler = tuple(record for record in records if record.kind == "compiler")
        inference = tuple(record for record in records if record.kind == "inference")
        return {
            "attempted_count": len(records),
            "dispatched_count": sum(record.dispatched for record in records),
            "responded_count": sum(record.responded for record in records),
            "completed_count": sum(record.completed for record in records),
            "terminal_valid_count": sum(record.terminal_valid for record in records),
            "compiler_attempted_count": len(compiler),
            "compiler_dispatched_count": sum(record.dispatched for record in compiler),
            "compiler_responded_count": sum(record.responded for record in compiler),
            "compiler_completed_count": sum(record.completed for record in compiler),
            "other_attempted_count": sum(record.kind == "other" for record in records),
            "other_dispatched_count": sum(
                record.dispatched for record in records if record.kind == "other"
            ),
            "other_responded_count": sum(
                record.responded for record in records if record.kind == "other"
            ),
            "other_completed_count": sum(
                record.completed for record in records if record.kind == "other"
            ),
            "inference_attempted_count": len(inference),
            "inference_dispatched_count": sum(record.dispatched for record in inference),
            "inference_responded_count": sum(record.responded for record in inference),
            "inference_completed_count": sum(record.completed for record in inference),
            "inference_terminal_valid_count": sum(record.terminal_valid for record in inference),
            "inference_first_byte_count": sum(record.first_byte for record in inference),
            "inference_normal_close_count": sum(record.normal_close for record in inference),
        }

    def snapshot(self) -> dict[str, object]:
        records = tuple(self._records)
        counts = self._counts(records)
        return {
            "observer_version": "direct-httpx-v2",
            "validator_source": self._validator_source,
            "ready": self.ready,
            "failure_class": self._failure_class,
            **counts,
            **{f"{name}_class": _count_class(value) for name, value in counts.items()},
            "records": tuple(record.safe_dict() for record in records),
            "elapsed_class": "unknown" if time.monotonic() < self._started else "bounded",
            "dispatch_budget": (
                self._budget_controller.safe_dict()
                if self._budget_controller is not None
                and callable(getattr(self._budget_controller, "safe_dict", None))
                else None
            ),
        }

    def _observe_chunk(self, state: _StreamState, size: int) -> bool:
        if self._budget_controller is None:
            return True
        try:
            permitted = self._budget_controller.observe_chunk(size)
        except BaseException:
            permitted = False
        if not permitted:
            self._latch_budget_failure()
        return permitted

    def _observe_frame(self, size: int) -> bool:
        if self._budget_controller is None:
            return True
        try:
            permitted = self._budget_controller.observe_frame(size)
        except BaseException:
            permitted = False
        if not permitted:
            self._latch_budget_failure()
        return permitted

    def _release_dispatch(self, record: _RequestObservation) -> None:
        if not record.dispatch_active:
            return
        record.dispatch_active = False
        if self._budget_controller is not None:
            self._budget_controller.release_dispatch()

    def _run_response_complete_hook(self, record: _RequestObservation) -> None:
        if self._response_complete_hook is None:
            return
        try:
            self._response_complete_hook(
                record.kind,
                record.dispatch_operation,
                record.dispatch_phase,
                record.dispatch_ordinal,
                record.terminal_valid,
            )
        except asyncio.CancelledError:
            record.exception_class = _exception_class("cancelled")
            self._latch_failure("cancelled")
        except BaseException:
            record.exception_class = "observer_response_complete_hook_error"
            self._latch_failure("dispatch_hook")

    async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
        if not self._ready:
            raise RuntimeError("transport_observer_not_ready")
        if len(self._records) >= MAX_OBSERVED_REQUESTS:
            self._latch_failure("bound")
            raise RuntimeError("transport_observer_request_bound_exceeded")
        endpoint_class = _endpoint_class(request.url.path)
        kind = (
            "compiler"
            if endpoint_class == "chat_completions"
            else "inference"
            if endpoint_class == "responses"
            else "other"
        )
        record = _RequestObservation(len(self._records) + 1, kind, endpoint_class)
        self._records.append(record)
        validator: StreamEventValidator | None = None
        if kind == "inference":
            if self._validator_factory is None:
                record.exception_class = _exception_class("validator")
                self._latch_failure("validator")
                raise RuntimeError("transport_observer_validator_unavailable")
            try:
                candidate = self._validator_factory(request)
                validate = getattr(candidate, "validate", None)
                if not callable(validate):
                    raise ValueError("validator_profile_invalid")
                validator = candidate
            except asyncio.CancelledError:
                record.exception_class = _exception_class("cancelled")
                self._latch_failure("cancelled")
                raise
            except BaseException:
                record.exception_class = _exception_class("validator")
                self._latch_failure("validator")
                raise RuntimeError("transport_observer_validator_unavailable") from None
        if self._budget_controller is not None:
            try:
                context = self._dispatch_context() if self._dispatch_context is not None else None
                if not isinstance(context, DispatchContext):
                    context = None
                record.dispatch_operation = context.operation if context is not None else "unknown"
                record.dispatch_phase = context.phase if context is not None else "unknown"
                record.dispatch_ordinal = context.ordinal if context is not None else None
                record.dispatch_lifetime = context.lifetime_id if context is not None else None
                if context is None:
                    record.exception_class = _exception_class("budget")
                    self._latch_failure("budget")
                    raise RuntimeError("transport_observer_dispatch_context_missing")
                if self._allowed_lifetime_ids is not None and (
                    context is None or context.lifetime_id not in self._allowed_lifetime_ids
                ):
                    record.exception_class = _exception_class("lifetime")
                    self._latch_failure("lifetime")
                    raise RuntimeError("transport_observer_lifetime_mismatch")
                if context is not None and context.operation == "readiness_probe":
                    if endpoint_class != "health":
                        record.exception_class = _exception_class("readiness")
                        self._latch_failure("readiness")
                        raise RuntimeError("transport_observer_readiness_not_health")
                admitted = self._budget_controller.admit_dispatch(
                    kind,
                    context=context,
                )
            except BaseException:
                admitted = False
            if not admitted:
                if record.exception_class is None:
                    record.exception_class = _exception_class("budget")
                self._latch_budget_failure()
                raise RuntimeError("transport_observer_budget_not_admitted")
            record.dispatch_admitted = True
            record.dispatch_active = True
            if self._dispatch_hook is not None:
                try:
                    self._dispatch_hook(kind, record.dispatch_phase, record.dispatch_ordinal)
                except BaseException:
                    record.exception_class = "observer_dispatch_hook_error"
                    self._release_dispatch(record)
                    self._latch_failure("dispatch_hook")
                    raise RuntimeError("transport_observer_dispatch_hook_failed") from None
        record.dispatched = True
        try:
            response = await self._delegate.handle_async_request(request)
        except asyncio.CancelledError:
            record.exception_class = _exception_class("cancelled")
            self._latch_failure("cancelled")
            self._release_dispatch(record)
            raise
        except BaseException:
            record.exception_class = _exception_class("delegate")
            self._latch_failure("delegate")
            self._release_dispatch(record)
            raise
        record.responded = True
        record.status_class = _status_class(response.status_code)
        content_type = response.headers.get("content-type", "")
        content_type_lower = content_type.lower()
        record.content_type_class = (
            "sse"
            if "text/event-stream" in content_type_lower
            else "json"
            if "json" in content_type_lower
            else "other"
        )
        if self._dispatch_complete_hook is not None:
            try:
                self._dispatch_complete_hook(kind, record.dispatch_phase, record.dispatch_ordinal)
            except asyncio.CancelledError:
                record.exception_class = _exception_class("cancelled")
                self._latch_failure("cancelled")
                try:
                    await response.aclose()
                except BaseException:
                    pass
                self._release_dispatch(record)
                raise
            except BaseException:
                record.exception_class = "observer_dispatch_complete_hook_error"
                self._latch_failure("dispatch_hook")
                try:
                    await response.aclose()
                except BaseException:
                    pass
                self._release_dispatch(record)
                self._latch_failure("dispatch_hook")
                raise RuntimeError("transport_observer_dispatch_complete_hook_failed") from None
        state = _StreamState(
            record.content_type_class,
            time.monotonic(),
            validator,
            frame_observer=self._observe_frame if record.content_type_class == "sse" else None,
        )
        response.stream = _ObservedStream(
            cast(httpx.AsyncByteStream, response.stream), self, record, state
        )
        return response

    def _finish_stream(self, record: _RequestObservation, state: _StreamState) -> None:
        if record.completed:
            return
        record.completed = True
        record.first_byte = state.first_byte
        is_inference_sse = record.kind == "inference" and record.content_type_class == "sse"
        record.terminal_valid = (
            state.terminal_valid
            if is_inference_sse
            else state.normal_close and not state.overflow and not state.malformed
        )
        record.normal_close = state.normal_close
        record.stream_bytes_class = _count_class(state.byte_count)
        record.event_count_class = _count_class(state.event_count)
        record.event_type_classes = tuple(sorted(set(state.event_types)))
        if is_inference_sse and not record.terminal_valid:
            self._latch_failure(state.failure_kind or "contract")

    def _finish_abnormal(self, record: _RequestObservation, state: _StreamState) -> None:
        if record.completed:
            return
        record.completed = False
        record.first_byte = state.first_byte
        record.terminal_valid = False
        record.normal_close = False
        record.stream_bytes_class = _count_class(state.byte_count)
        record.event_count_class = _count_class(state.event_count)
        record.event_type_classes = tuple(sorted(set(state.event_types)))
        self._latch_state_failure(state)
        self._latch_failure(state.failure_kind or "closure")

    def _finish_delegate_close_failure(
        self, record: _RequestObservation, state: _StreamState
    ) -> None:
        """Invalidate a semantically finalized stream whose delegate did not close."""
        record.completed = False
        record.terminal_valid = False
        record.normal_close = False
        record.exception_class = _exception_class("closure")
        record.stream_bytes_class = _count_class(state.byte_count)
        record.event_count_class = _count_class(state.event_count)
        record.event_type_classes = tuple(sorted(set(state.event_types)))
        self._latch_state_failure(state)
        self._latch_failure("closure")

    async def aclose(self) -> None:
        await self._delegate.aclose()


def observer_dispatch_matches_fake(
    snapshot: dict[str, object], *, compiler_calls: int, inference_calls: int
) -> bool:
    """Compare exact independent dispatch counts with fake-server counts."""
    return (
        snapshot.get("compiler_attempted_count") == compiler_calls
        and snapshot.get("compiler_dispatched_count") == compiler_calls
        and snapshot.get("inference_attempted_count") == inference_calls
        and snapshot.get("inference_dispatched_count") == inference_calls
        and snapshot.get("inference_terminal_valid_count") == inference_calls
    )


def merge_observer_snapshots(*snapshots: dict[str, object]) -> dict[str, object]:
    """Merge sequential lifetimes while preserving unique global ordinals."""
    records: list[dict[str, object]] = []
    ready = True
    global_ordinal = 0
    for snapshot in snapshots:
        ready = ready and snapshot.get("ready") is True
        values = snapshot.get("records", ())
        if not isinstance(values, (list, tuple)):
            raise ValueError("observer_records_schema")
        expected_ordinal = 1
        for value in values:
            if not isinstance(value, dict) or value.get("ordinal") != expected_ordinal:
                raise ValueError("observer_ordinal_collision")
            expected_ordinal += 1
            global_ordinal += 1
            record = dict(value)
            record["lifetime_ordinal"] = record["ordinal"]
            record["ordinal"] = global_ordinal
            records.append(record)
    compiler = [record for record in records if record.get("kind") == "compiler"]
    inference = [record for record in records if record.get("kind") == "inference"]
    counts = {
        "attempted_count": len(records),
        "dispatched_count": sum(record.get("dispatched") is True for record in records),
        "responded_count": sum(record.get("responded") is True for record in records),
        "completed_count": sum(record.get("completed") is True for record in records),
        "terminal_valid_count": sum(record.get("terminal_valid") is True for record in records),
        "compiler_attempted_count": len(compiler),
        "compiler_dispatched_count": sum(record.get("dispatched") is True for record in compiler),
        "compiler_responded_count": sum(record.get("responded") is True for record in compiler),
        "compiler_completed_count": sum(record.get("completed") is True for record in compiler),
        "other_attempted_count": sum(record.get("kind") == "other" for record in records),
        "other_dispatched_count": sum(
            record.get("dispatched") is True for record in records if record.get("kind") == "other"
        ),
        "other_responded_count": sum(
            record.get("responded") is True for record in records if record.get("kind") == "other"
        ),
        "other_completed_count": sum(
            record.get("completed") is True for record in records if record.get("kind") == "other"
        ),
        "inference_attempted_count": len(inference),
        "inference_dispatched_count": sum(record.get("dispatched") is True for record in inference),
        "inference_responded_count": sum(record.get("responded") is True for record in inference),
        "inference_completed_count": sum(record.get("completed") is True for record in inference),
        "inference_terminal_valid_count": sum(
            record.get("terminal_valid") is True for record in inference
        ),
        "inference_first_byte_count": sum(record.get("first_byte") is True for record in inference),
        "inference_normal_close_count": sum(
            record.get("normal_close") is True for record in inference
        ),
    }
    return {
        "observer_version": "direct-httpx-v2",
        "validator_source": "gateway_responses_stream_validator",
        "ready": ready,
        "failure_class": next(
            (
                snapshot.get("failure_class")
                for snapshot in snapshots
                if snapshot.get("failure_class") is not None
            ),
            None,
        ),
        **counts,
        **{f"{name}_class": _count_class(value) for name, value in counts.items()},
        "records": tuple(records),
        "elapsed_class": "bounded",
    }

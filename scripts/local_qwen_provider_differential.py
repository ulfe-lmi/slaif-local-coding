#!/usr/bin/env python3
"""Run the single bounded Local Coding -> protected Qwen verification.

This is repository-only evidence support for OAP 005-j. It emits fixed
transport/SSE facts and never prints request, response, credential, identity,
endpoint, or model-content values.
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import os
import secrets
import sys
import tempfile
import time
from collections.abc import AsyncIterator, Mapping
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, cast

import httpx
from fastapi import FastAPI

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)
    sys.path.insert(0, os.path.join(REPO_ROOT, "src"))

from slaif_local_coding.app import create_app  # noqa: E402  # type: ignore[import-untyped]
from slaif_local_coding.config import (  # noqa: E402  # type: ignore[import-untyped]
    CacheConfig,
    CompilerConfig,
    ConstitutionIntegrationConfig,
    GatewayIngressConfig,
    RehydrationConfig,
    RouteConfig,
    ServerConfig,
    Settings,
    UpstreamConfig,
)
from slaif_local_coding.gateway_identity import (  # noqa: E402  # type: ignore[import-untyped]
    canonical_identity_bytes,
    expected_signature,
)

MODEL = "qwen3.8-27b"
ROUTE = "qwen38-vision-codex"
QWEN_KEY_ENV = "OAP_005J_QWEN_KEY"
SERVICE_TOKEN_ENV = "OAP_005J_SERVICE_TOKEN"
SIGNING_SECRET_ENV = "OAP_005J_SIGNING_SECRET"
UPSTREAM_ORIGIN = "http://127.0.0.1:18020"
REQUEST_PATH = "/v1/responses"
MAX_STREAM_BYTES = 1_048_576
MAX_EVENT_BYTES = 262_144
KNOWN_EVENT_TYPES = frozenset(
    {
        "response.created",
        "response.in_progress",
        "response.completed",
        "response.failed",
        "response.incomplete",
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
        "response.function_call_arguments.delta",
        "response.reasoning_part.added",
        "response.reasoning_part.done",
        "response.custom_tool_call_input.delta",
        "error",
    }
)
PROVIDER_FAILURE_EVENT_TYPES = frozenset({"response.failed", "response.incomplete", "error"})


def _status_class(status: int | None) -> str:
    if status is None:
        return "unknown"
    if 200 <= status < 300:
        return "2xx"
    if 400 <= status < 500:
        return "4xx"
    if 500 <= status < 600:
        return "5xx"
    return "other"


def _content_type_class(value: str | None) -> str:
    lowered = (value or "").lower()
    if "text/event-stream" in lowered:
        return "sse"
    if "json" in lowered:
        return "json"
    return "other" if lowered else "unknown"


def _exception_class(exc: BaseException) -> str:
    allowed = {
        "ConnectError",
        "ConnectTimeout",
        "ReadError",
        "ReadTimeout",
        "RemoteProtocolError",
        "WriteError",
        "WriteTimeout",
        "PoolTimeout",
        "TimeoutException",
        "NetworkError",
        "ProtocolError",
        "LocalProtocolError",
    }
    name = type(exc).__name__
    return name if name in allowed else "other_transport_error"


def _bounded_class(value: object) -> str:
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, int):
        return "integer"
    if isinstance(value, float):
        return "number"
    if isinstance(value, str):
        return "string"
    if isinstance(value, list):
        return "array"
    if isinstance(value, Mapping):
        return "object"
    if value is None:
        return "null"
    return "other"


def _count_images(value: object) -> int:
    count = 0
    pending = [value]
    visited = 0
    while pending:
        current = pending.pop()
        visited += 1
        if visited > 16_384:
            return -1
        if isinstance(current, list):
            pending.extend(current)
        elif isinstance(current, Mapping):
            if current.get("type") in {"input_image", "image_url"}:
                count += 1
            pending.extend(current.values())
    return count


def _input_shape(value: object) -> dict[str, object]:
    if not isinstance(value, list):
        return {"class": _bounded_class(value), "item_count": 0, "content_count": 0}
    content_count = 0
    for item in value:
        if isinstance(item, Mapping) and isinstance(item.get("content"), list):
            content_count += len(item["content"])
    return {"class": "array", "item_count": len(value), "content_count": content_count}


def request_shape(body: bytes, *, expected_body: bytes | None = None) -> dict[str, object]:
    """Return only the structural classes authorized by the work order."""
    try:
        value = json.loads(body)
    except (UnicodeDecodeError, json.JSONDecodeError):
        return {
            "json": False,
            "byte_length": len(body),
            "top_level_fields": [],
            "model_matches": False,
            "stream": False,
            "input": {"class": "invalid", "item_count": 0, "content_count": 0},
            "tool_count": 0,
            "image_count": -1,
            "output_limit": "invalid",
            "reasoning": "invalid",
            "body_equal": False,
        }
    if not isinstance(value, Mapping):
        return {
            "json": False,
            "byte_length": len(body),
            "top_level_fields": [],
            "model_matches": False,
            "stream": False,
            "input": {"class": _bounded_class(value), "item_count": 0, "content_count": 0},
            "tool_count": 0,
            "image_count": -1,
            "output_limit": "invalid",
            "reasoning": "invalid",
            "body_equal": False,
        }
    tools = value.get("tools")
    return {
        "json": True,
        "byte_length": len(body),
        "top_level_fields": sorted(str(key) for key in value),
        "model_matches": value.get("model") == MODEL,
        "stream": value.get("stream") is True,
        "input": _input_shape(value.get("input")),
        "tool_count": len(tools) if isinstance(tools, list) else 0,
        "image_count": _count_images(value),
        "output_limit": (
            "absent"
            if "max_output_tokens" not in value
            else "integer"
            if type(value["max_output_tokens"]) is int
            else _bounded_class(value["max_output_tokens"])
        ),
        "reasoning": ("absent" if "reasoning" not in value else _bounded_class(value["reasoning"])),
        "body_equal": expected_body is not None and body == expected_body,
    }


def _header_classes(headers: httpx.Headers) -> tuple[str, ...]:
    known = {
        "accept",
        "accept-encoding",
        "authorization",
        "content-type",
        "x-request-id",
    }
    classes = {name.lower() if name.lower() in known else "other" for name in headers}
    return tuple(sorted(classes))


@dataclass
class SSEFacts:
    byte_count: int = 0
    digest: Any = field(default_factory=hashlib.sha256)
    first_bytes: bool = False
    parseable: bool = True
    normal_close: bool = False
    event_counts: dict[str, int] = field(default_factory=dict)
    unknown_events: bool = False
    error_event: bool = False
    duplicates: bool = False
    created: bool = False
    completed: bool = False
    completed_valid: bool = False
    completed_output_empty: bool = False
    created_id: str | None = None
    completed_id: str | None = None
    _line_buffer: bytearray = field(default_factory=bytearray)
    _data_lines: list[bytes] = field(default_factory=list)
    _event_bytes: int = 0

    def consume(self, chunk: bytes) -> None:
        if not chunk:
            return
        self.first_bytes = True
        self.byte_count += len(chunk)
        self.digest.update(chunk)
        if self.byte_count > MAX_STREAM_BYTES:
            self.parseable = False
            return
        self._line_buffer.extend(chunk)
        while b"\n" in self._line_buffer:
            line, _, remainder = self._line_buffer.partition(b"\n")
            self._line_buffer = bytearray(remainder)
            self._consume_line(bytes(line.rstrip(b"\r")))
        if len(self._line_buffer) > MAX_EVENT_BYTES:
            self.parseable = False
            self._line_buffer.clear()

    def _consume_line(self, line: bytes) -> None:
        if len(line) > MAX_EVENT_BYTES:
            self.parseable = False
            return
        if line == b"":
            self._finish_event()
        elif line.startswith(b"data:"):
            data = line[5:]
            if data.startswith(b" "):
                data = data[1:]
            self._event_bytes += len(data)
            if self._event_bytes > MAX_EVENT_BYTES:
                self.parseable = False
            else:
                self._data_lines.append(data)

    def _finish_event(self) -> None:
        if not self._data_lines:
            self._event_bytes = 0
            return
        raw = b"\n".join(self._data_lines)
        self._data_lines.clear()
        self._event_bytes = 0
        if raw == b"[DONE]":
            self.event_counts["done"] = self.event_counts.get("done", 0) + 1
            return
        try:
            payload = json.loads(raw)
        except (UnicodeDecodeError, json.JSONDecodeError):
            self.parseable = False
            return
        if not isinstance(payload, Mapping) or not isinstance(payload.get("type"), str):
            self.parseable = False
            return
        event_type = payload["type"]
        self.event_counts[event_type] = self.event_counts.get(event_type, 0) + 1
        if event_type not in KNOWN_EVENT_TYPES:
            self.unknown_events = True
        if event_type in PROVIDER_FAILURE_EVENT_TYPES:
            self.error_event = True
        if event_type == "response.created":
            if self.created:
                self.duplicates = True
            self.created = True
            response = payload.get("response")
            if isinstance(response, Mapping) and isinstance(response.get("id"), str):
                self.created_id = response["id"]
            elif isinstance(payload.get("id"), str):
                self.created_id = payload["id"]
        if event_type == "response.completed":
            if self.completed:
                self.duplicates = True
            self.completed = True
            response = payload.get("response")
            if isinstance(response, Mapping):
                self.completed_id = (
                    response.get("id") if isinstance(response.get("id"), str) else None
                )
                usage = response.get("usage")
                status = response.get("status")
                output = response.get("output")
            else:
                usage = payload.get("usage")
                status = payload.get("status")
                output = payload.get("output")
            usage_valid = (
                isinstance(usage, Mapping)
                and all(
                    type(usage.get(key)) is int and usage[key] >= 0
                    for key in ("input_tokens", "output_tokens", "total_tokens")
                )
                and usage["total_tokens"] == usage["input_tokens"] + usage["output_tokens"]
            )
            ids_valid = self.created_id is None or self.completed_id in {None, self.created_id}
            self.completed_output_empty = isinstance(output, list) and len(output) == 0
            self.completed_valid = status == "completed" and usage_valid and ids_valid

    def finish(self) -> None:
        if self._line_buffer:
            self._consume_line(bytes(self._line_buffer).rstrip(b"\r"))
            self._line_buffer.clear()
        if self._data_lines:
            self.parseable = False
            self._data_lines.clear()
        self.normal_close = True

    def summary(self, *, status: int | None, content_type: str | None) -> dict[str, object]:
        recognized = self.parseable and not self.unknown_events
        return {
            "status_class": _status_class(status),
            "content_type_class": _content_type_class(content_type),
            "byte_count": self.byte_count,
            "first_bytes": self.first_bytes,
            "parseable": self.parseable,
            "recognized_events": recognized,
            "error_event": self.error_event,
            "duplicates": self.duplicates,
            "event_counts": dict(sorted(self.event_counts.items())),
            "created": self.created,
            "completed": self.completed,
            "completed_valid": self.completed_valid,
            "completed_output_empty": self.completed_output_empty,
            "normal_close": self.normal_close,
            "response_id_relation": self.created_id is None
            or self.completed_id in {None, self.created_id},
        }


@dataclass
class StageResult:
    dispatch_started: bool = False
    dispatch_count: int = 0
    response_status: int | None = None
    response_content_type: str | None = None
    response_headers: tuple[str, ...] = ()
    request_body: bytes = b""
    request_method: str | None = None
    request_path: str | None = None
    request_headers: tuple[str, ...] = ()
    request_exception: str | None = None
    response_exception: str | None = None
    sse: SSEFacts = field(default_factory=SSEFacts)
    downstream_status: int | None = None
    downstream_content_type: str | None = None
    downstream_sse: SSEFacts = field(default_factory=SSEFacts)

    def stages(self, *, forwarded: bool | None = None) -> dict[str, str]:
        has_response = self.response_status is not None
        has_headers = has_response
        status_ok = self.response_status is not None and 200 <= self.response_status < 300
        content_type_ok = _content_type_class(self.response_content_type) == "sse"
        has_body = self.sse.first_bytes
        framing = (
            "PASSED" if has_body and self.sse.parseable else "FAILED" if has_body else "NOT_REACHED"
        )
        recognized = (
            "PASSED"
            if has_body
            and self.sse.parseable
            and not self.sse.unknown_events
            and not self.sse.error_event
            and not self.sse.duplicates
            else "FAILED"
            if has_body
            else "NOT_REACHED"
        )
        completed = (
            "PASSED"
            if (
                status_ok
                and content_type_ok
                and self.sse.completed_valid
                and self.sse.event_counts.get("response.created") == 1
                and self.sse.event_counts.get("response.completed") == 1
                and not self.sse.error_event
                and not self.sse.duplicates
                and self.sse.normal_close
            )
            else "FAILED"
            if self.sse.completed
            else "NOT_REACHED"
        )
        forwarded_stage = (
            "PASSED" if forwarded is True else "FAILED" if forwarded is False else "NOT_REACHED"
        )
        return {
            "A": "PASSED" if self.dispatch_started else "NOT_REACHED",
            "B": (
                "PASSED"
                if status_ok
                else "FAILED"
                if has_response or self.request_exception
                else "NOT_REACHED"
            ),
            "C": "PASSED" if has_headers else "NOT_REACHED",
            "D": "PASSED" if has_body else "FAILED" if has_response else "NOT_REACHED",
            "E": framing,
            "F": recognized,
            "G": "PASSED" if self.sse.created else "FAILED" if has_body else "NOT_REACHED",
            "H": completed,
            "I": forwarded_stage,
        }

    def summary(self, *, expected_body: bytes, forwarded: bool | None = None) -> dict[str, object]:
        return {
            "stages": self.stages(forwarded=forwarded),
            "request": request_shape(self.request_body, expected_body=expected_body)
            if self.request_body
            else request_shape(b"", expected_body=expected_body),
            "request_method": self.request_method,
            "dispatch_count": self.dispatch_count,
            "request_path_class": (
                "v1_responses" if self.request_path == REQUEST_PATH else "other"
            ),
            "request_header_name_classes": list(self.request_headers),
            "response_header_name_classes": list(self.response_headers),
            "request_exception_class": self.request_exception,
            "response_exception_class": self.response_exception,
            "stream": self.sse.summary(
                status=self.response_status,
                content_type=self.response_content_type,
            ),
            "downstream": (
                self.downstream_sse.summary(
                    status=self.downstream_status,
                    content_type=self.downstream_content_type,
                )
                if self.downstream_status is not None
                else "NOT_REACHED"
            ),
        }


class RecordingStream(httpx.AsyncByteStream):
    def __init__(self, stream: httpx.AsyncByteStream, facts: StageResult) -> None:
        self._stream = stream
        self._facts = facts

    async def __aiter__(self) -> AsyncIterator[bytes]:
        try:
            async for chunk in self._stream:
                self._facts.sse.consume(chunk)
                yield chunk
            self._facts.sse.finish()
        except BaseException as exc:
            if isinstance(exc, asyncio.CancelledError):
                raise
            self._facts.response_exception = _exception_class(exc)
            raise

    async def aclose(self) -> None:
        await self._stream.aclose()


class RecordingTransport(httpx.AsyncBaseTransport):
    def __init__(self, delegate: httpx.AsyncBaseTransport, facts: StageResult) -> None:
        self._delegate = delegate
        self.facts = facts

    async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
        self.facts.dispatch_started = True
        self.facts.dispatch_count += 1
        self.facts.request_method = request.method
        self.facts.request_path = request.url.path
        self.facts.request_headers = _header_classes(request.headers)
        try:
            self.facts.request_body = request.content
        except (RuntimeError, TypeError):
            self.facts.request_body = b""
        try:
            response = await self._delegate.handle_async_request(request)
        except BaseException as exc:
            if isinstance(exc, asyncio.CancelledError):
                raise
            self.facts.request_exception = _exception_class(exc)
            raise
        self.facts.response_status = response.status_code
        self.facts.response_content_type = response.headers.get("content-type")
        self.facts.response_headers = _header_classes(response.headers)
        response.stream = RecordingStream(cast(httpx.AsyncByteStream, response.stream), self.facts)
        return response

    async def aclose(self) -> None:
        await self._delegate.aclose()


def _expected_body() -> bytes:
    # This is the provider-bound shape after the pinned Gateway drops its
    # transient client_metadata and applies the observed route output default.
    value = {
        "input": [
            {
                "content": [{"text": "bounded differential", "type": "input_text"}],
                "role": "user",
                "type": "message",
            }
        ],
        "max_output_tokens": 4096,
        "model": MODEL,
        "stream": True,
    }
    return json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode()


def _settings(cache_root: Path) -> Settings:
    return Settings(
        server=ServerConfig(listen_host="127.0.0.1", listen_port=18031),
        gateway_ingress=GatewayIngressConfig(
            mode="service_bearer_signed_identity_v1",
            service_token_env=SERVICE_TOKEN_ENV,
            signing_secret_env=SIGNING_SECRET_ENV,
        ),
        upstream=UpstreamConfig(
            base_url=f"{UPSTREAM_ORIGIN}/v1",
            api_key_env=QWEN_KEY_ENV,
            model=MODEL,
            connect_timeout_seconds=10,
            request_timeout_seconds=300,
            write_timeout_seconds=30,
            pool_timeout_seconds=10,
        ),
        routes=[
            RouteConfig(
                name=ROUTE,
                model=MODEL,
                max_images_per_request=1,
                image_overflow_policy="retain_newest",
                responses_tool_policy="drop_disabled_codex_search",
                observation_enabled=True,
                constitution_enabled=True,
            )
        ],
        compiler=CompilerConfig(enabled=True, api_key_env=QWEN_KEY_ENV, max_attempts=1),
        cache=CacheConfig(root=cache_root, fallback_root=cache_root / "fallback"),
        constitution=ConstitutionIntegrationConfig(
            enabled=True,
            identity_source="signed_request",
            rehydration=RehydrationConfig(enabled=True),
        ),
    )


def _signed_headers(body: bytes) -> dict[str, str]:
    timestamp = str(int(time.time()))
    nonce = secrets.token_urlsafe(24)
    principal = "005i-owner"
    session = "005i-session"
    repository = "005i-repository"
    canonical = canonical_identity_bytes(
        method="POST",
        path=REQUEST_PATH,
        raw_query=b"",
        body=body,
        principal=principal,
        session=session,
        repository=repository,
        route=ROUTE,
        timestamp=timestamp,
        nonce=nonce,
    )
    secret = os.environ[SIGNING_SECRET_ENV].encode("ascii")
    return {
        "Authorization": f"Bearer {os.environ[SERVICE_TOKEN_ENV]}",
        "Accept": "text/event-stream",
        "Content-Type": "application/json",
        "X-SLAIF-Identity-Version": "v1",
        "X-SLAIF-Principal": principal,
        "X-SLAIF-Session": session,
        "X-SLAIF-Repository": repository,
        "X-SLAIF-Route": ROUTE,
        "X-SLAIF-Timestamp": timestamp,
        "X-SLAIF-Nonce": nonce,
        "X-SLAIF-Signature": expected_signature(secret=secret, canonical=canonical),
    }


async def _consume_response(
    response: httpx.Response,
    facts: StageResult,
    stream: SSEFacts,
    *,
    record_response: bool = True,
) -> None:
    if record_response:
        facts.response_status = response.status_code
        facts.response_content_type = response.headers.get("content-type")
        facts.response_headers = _header_classes(response.headers)
    try:
        async for chunk in response.aiter_raw():
            stream.consume(chunk)
        stream.finish()
    except BaseException as exc:
        if isinstance(exc, asyncio.CancelledError):
            raise
        facts.response_exception = _exception_class(exc)
        raise


async def _local_call(
    app: FastAPI, body: bytes, headers: dict[str, str], facts: StageResult
) -> None:
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://adapter.test") as client:
        try:
            async with client.stream(
                "POST", REQUEST_PATH, content=body, headers=headers
            ) as response:
                facts.downstream_status = response.status_code
                facts.downstream_content_type = response.headers.get("content-type")
                await _consume_response(
                    response, facts, facts.downstream_sse, record_response=False
                )
        except BaseException as exc:
            if isinstance(exc, asyncio.CancelledError):
                raise
            if facts.response_exception is None:
                facts.response_exception = _exception_class(exc)


def _through_h(facts: StageResult) -> bool:
    stages = facts.stages()
    return facts.dispatch_count == 1 and all(stages[key] == "PASSED" for key in "ABCDEFGH")


def _forwarded(facts: StageResult) -> bool | None:
    if facts.response_status is None:
        return None
    if not 200 <= facts.response_status < 300:
        return False
    if _content_type_class(facts.response_content_type) != "sse":
        return False
    if facts.downstream_status is None:
        return False
    if not 200 <= facts.downstream_status < 300:
        return False
    if _content_type_class(facts.downstream_content_type) != "sse":
        return False
    if not facts.sse.first_bytes or not facts.downstream_sse.first_bytes:
        return False
    if not _through_h(facts):
        return False
    return (
        facts.sse.byte_count == facts.downstream_sse.byte_count
        and facts.sse.digest.digest() == facts.downstream_sse.digest.digest()
        and facts.downstream_sse.parseable
        and not facts.downstream_sse.unknown_events
        and not facts.downstream_sse.error_event
        and not facts.downstream_sse.duplicates
        and facts.downstream_sse.event_counts.get("response.created") == 1
        and facts.downstream_sse.event_counts.get("response.completed") == 1
        and facts.downstream_sse.completed_valid
        and facts.downstream_sse.normal_close
    )


async def run() -> dict[str, object]:
    qwen_key = os.environ.get(QWEN_KEY_ENV)
    if not qwen_key:
        return {"status": "BLOCKED", "reason": "protected_credential_unavailable"}
    previous_service_token = os.environ.get(SERVICE_TOKEN_ENV)
    previous_signing_secret = os.environ.get(SIGNING_SECRET_ENV)
    os.environ[SERVICE_TOKEN_ENV] = "synthetic-005i-service-token"
    os.environ[SIGNING_SECRET_ENV] = "synthetic-005i-signing-secret-0123456789"
    body = _expected_body()
    signed_headers = _signed_headers(body)
    local_facts = StageResult()
    try:
        with tempfile.TemporaryDirectory(prefix="slaif-005j-differential-") as temp_dir:
            recording = RecordingTransport(httpx.AsyncHTTPTransport(retries=0), local_facts)
            app = create_app(_settings(Path(temp_dir) / "cache"), transport=recording)
            async with app.router.lifespan_context(app):
                await _local_call(app, body, signed_headers, local_facts)
        local_forwarded = _forwarded(local_facts)
        local_passed = _through_h(local_facts) and local_forwarded is True
        local_summary = local_facts.summary(expected_body=body, forwarded=local_forwarded)
        return {
            "status": "PASSED" if local_passed else "FAILED",
            "decision": "boundary_green" if local_passed else "local_boundary_evidence",
            "expected_request": request_shape(body, expected_body=body),
            "local": local_summary,
            "direct_control": "NOT_AUTHORIZED",
            "compiler_attempts": 0,
        }
    finally:
        if previous_service_token is None:
            os.environ.pop(SERVICE_TOKEN_ENV, None)
        else:
            os.environ[SERVICE_TOKEN_ENV] = previous_service_token
        if previous_signing_secret is None:
            os.environ.pop(SIGNING_SECRET_ENV, None)
        else:
            os.environ[SIGNING_SECRET_ENV] = previous_signing_secret


def main() -> int:
    try:
        result = asyncio.run(run())
    except (OSError, RuntimeError, ValueError):
        result = {"status": "FAILED", "decision": "diagnostic_runner_error"}
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))
    return 0 if result.get("status") in {"PASSED", "FAILED", "BLOCKED"} else 1


if __name__ == "__main__":
    raise SystemExit(main())

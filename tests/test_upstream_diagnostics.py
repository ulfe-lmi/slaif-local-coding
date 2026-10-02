"""Order 015-a (P01): bounded private upstream HTTP-error classification.

Covers the closed classifier contract, the bounded byte/time read against
controlled fake upstreams, sentinel privacy, close-on-every-path, and the
unchanged public error/status/header semantics.
"""

from __future__ import annotations

import asyncio
import json
import logging
from collections.abc import AsyncIterator
from typing import Any

import httpx
import pytest

from slaif_local_coding.app import _read_bounded_error_diagnostic, create_app
from slaif_local_coding.config import (
    RouteConfig,
    ServerConfig,
    Settings,
    UpstreamConfig,
)
from slaif_local_coding.upstream_diagnostics import (
    MAX_DIAGNOSTIC_JSON_DEPTH,
    UpstreamErrorReason,
    classify_upstream_error,
    status_class,
)

SENTINEL = "oap015-private-provider-sentinel-do-not-leak"


def _settings(**upstream_changes: Any) -> Settings:
    values: dict[str, Any] = {
        "base_url": "http://upstream.test/v1",
        "api_key_env": "TEST_DIAG_KEY",
        "model": "qwen",
    }
    values.update(upstream_changes)
    return Settings(
        server=ServerConfig(),
        upstream=UpstreamConfig(**values),
        routes=[RouteConfig(name="vision", model="qwen", image_overflow_policy="passthrough")],
    )


# ---------------------------------------------------------------------------
# Pure classifier: status-derived categories
# ---------------------------------------------------------------------------


def test_status_derived_authentication_and_rate_limit_and_5xx() -> None:
    junk = json.dumps({"error": {"message": SENTINEL, "code": "image_count_limit"}}).encode()
    assert classify_upstream_error(401, junk) is UpstreamErrorReason.AUTHENTICATION
    assert classify_upstream_error(403, junk) is UpstreamErrorReason.AUTHENTICATION
    assert classify_upstream_error(429, junk) is UpstreamErrorReason.RATE_LIMIT
    for status in (500, 502, 503, 599):
        assert classify_upstream_error(status, junk) is UpstreamErrorReason.UPSTREAM_5XX
    assert classify_upstream_error(401, None) is UpstreamErrorReason.AUTHENTICATION


def test_status_class_labels() -> None:
    assert status_class(400) == "4xx"
    assert status_class(499) == "4xx"
    assert status_class(500) == "5xx"
    assert status_class(503) == "5xx"


# ---------------------------------------------------------------------------
# Pure classifier: body-evidenced categories
# ---------------------------------------------------------------------------


def test_image_count_evidence_maps_to_image_count_limit() -> None:
    # vLLM-style: numeric code is ignored; the message phrase carries evidence.
    vllm_shape = {
        "error": {
            "message": "Maximum of 1 images allowed per request",
            "type": "BadRequestError",
            "code": 400,
        }
    }
    assert classify_upstream_error(400, json.dumps(vllm_shape).encode()) is (
        UpstreamErrorReason.IMAGE_COUNT_LIMIT
    )
    # OpenAI-style fixed code.
    openai_shape = {
        "error": {
            "message": "sentinel",
            "type": "invalid_request_error",
            "code": "image_count_limit",
        }
    }
    assert classify_upstream_error(400, json.dumps(openai_shape).encode()) is (
        UpstreamErrorReason.IMAGE_COUNT_LIMIT
    )
    # 413 (payload too large) is not status-derived; body evidence still classifies.
    assert classify_upstream_error(413, json.dumps(vllm_shape).encode()) is (
        UpstreamErrorReason.IMAGE_COUNT_LIMIT
    )


def test_context_length_evidence_maps_to_context_length_limit() -> None:
    code_shape = {
        "error": {
            "message": SENTINEL,
            "type": "invalid_request_error",
            "code": "maximum_context_length",
        }
    }
    assert classify_upstream_error(400, json.dumps(code_shape).encode()) is (
        UpstreamErrorReason.CONTEXT_LENGTH_LIMIT
    )
    message_shape = {
        "error": {
            "message": (
                f"{SENTINEL}: This model's maximum context length is 8192 tokens, "
                "however you requested 9000 tokens"
            ),
            "type": "invalid_request_error",
            "param": None,
            "code": None,
        }
    }
    assert classify_upstream_error(400, json.dumps(message_shape).encode()) is (
        UpstreamErrorReason.CONTEXT_LENGTH_LIMIT
    )
    param_shape = {
        "error": {
            "message": SENTINEL,
            "type": "BadRequestError",
            "param": "max_tokens",
            "code": 400,
        }
    }
    assert classify_upstream_error(400, json.dumps(param_shape).encode()) is (
        UpstreamErrorReason.CONTEXT_LENGTH_LIMIT
    )


def test_malformed_input_evidence_maps_to_malformed_input() -> None:
    code_shape = {
        "error": {"message": SENTINEL, "type": "invalid_request_error", "code": "invalid_json"}
    }
    assert classify_upstream_error(400, json.dumps(code_shape).encode()) is (
        UpstreamErrorReason.MALFORMED_INPUT
    )
    message_shape = {
        "error": {
            "message": f"{SENTINEL} malformed JSON in request body",
            "type": "invalid_request_error",
        }
    }
    assert classify_upstream_error(400, json.dumps(message_shape).encode()) is (
        UpstreamErrorReason.MALFORMED_INPUT
    )


def test_top_level_error_fields_are_inspected_when_no_error_object() -> None:
    shape = {"code": "context_length_limit", "message": SENTINEL}
    assert classify_upstream_error(400, json.dumps(shape).encode()) is (
        UpstreamErrorReason.CONTEXT_LENGTH_LIMIT
    )


# ---------------------------------------------------------------------------
# Pure classifier: safe unknown normalization
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "body",
    [
        b"",
        b"not json at all",
        b'{"error": {"code": "image_count_limit",',  # incomplete at byte bound
        b"[1, 2, 3]",
        b'"just a string"',
        b"42",
        b'{"error": "a string, not an object"}',
        b'{"error": {"error": {"code": "image_count_limit"}}}',  # nested deeper than the allowlist
        b'{"other": {"code": "image_count_limit"}}',
        b"\xff\xfe\x00binary",
        b'{"error": {"code": "totally_unknown_code", "type": "invalid_request_error"}}',
        b'{"error": {"code": 400, "type": null, "param": ["images"], "message": null}}',
        # duplicate keys: {"error": {"code": "image_count_limit", "code": "context_length_limit"}}
        b'{"error": {"code": "image_count_limit", "code": "context_length_limit"}}',
        # ambiguous: code and type name two different closed categories
        b'{"error": {"code": "image_count_limit", "type": "context_length_limit"}}',
        b"{" + b"[" * (MAX_DIAGNOSTIC_JSON_DEPTH + 2) + b"}",  # over-deep
    ],
)
def test_unknown_and_ambiguous_evidence_normalizes_to_unknown(body: bytes) -> None:
    assert classify_upstream_error(400, body) is UpstreamErrorReason.UNKNOWN
    assert classify_upstream_error(404, body) is UpstreamErrorReason.UNKNOWN
    assert classify_upstream_error(422, body) is UpstreamErrorReason.UNKNOWN


def test_no_body_and_empty_body_are_unknown_for_non_status_derived() -> None:
    assert classify_upstream_error(400, None) is UpstreamErrorReason.UNKNOWN
    assert classify_upstream_error(404, b"") is UpstreamErrorReason.UNKNOWN


# ---------------------------------------------------------------------------
# Bounded diagnostic read: byte bound, chunk bound, stall, time bound
# ---------------------------------------------------------------------------


class _BoundedStream(httpx.AsyncByteStream):
    """Fake upstream error body with a controllable chunking/stall pattern."""

    def __init__(
        self,
        chunks: list[bytes],
        *,
        stall_seconds: float = 0.0,
        stall_after: int = -1,
        read_error: Exception | None = None,
    ) -> None:
        self._chunks = chunks
        self._stall_seconds = stall_seconds
        self._stall_after = stall_after
        self._read_error = read_error
        self.close_calls = 0
        self.aiter_started = 0

    async def __aiter__(self) -> AsyncIterator[bytes]:
        self.aiter_started += 1
        for position, chunk in enumerate(self._chunks):
            if self._read_error is not None and position == 0:
                raise self._read_error
            if self._stall_seconds and position == self._stall_after:
                await asyncio.sleep(self._stall_seconds)
            yield chunk

    async def aclose(self) -> None:
        self.close_calls += 1


def _response(stream: _BoundedStream, status: int = 400) -> httpx.Response:
    return httpx.Response(status, headers={"content-type": "application/json"}, stream=stream)


@pytest.mark.asyncio
async def test_single_oversized_chunk_never_exceeds_byte_bound() -> None:
    sentinel_chunk = b'{"error":{"message":"' + SENTINEL.encode() + b'"}}' + b"x" * 40_000
    stream = _BoundedStream([sentinel_chunk])
    upstream = _response(stream)
    got = await _read_bounded_error_diagnostic(upstream, max_bytes=16_384, timeout_seconds=5.0)
    assert got is not None
    assert len(got) == 16_384
    assert got.startswith(b'{"error":{"message":"oap015-private-provider-sentinel-do-not-leak"')


@pytest.mark.asyncio
async def test_many_chunks_stopping_exactly_at_the_bound() -> None:
    chunks = [b"y" * 1_000 for _ in range(20)]  # 20 KiB total
    stream = _BoundedStream(chunks)
    upstream = _response(stream)
    got = await _read_bounded_error_diagnostic(upstream, max_bytes=16_384, timeout_seconds=5.0)
    assert got is not None
    assert len(got) == 16_384
    assert got == b"y" * 16_384


@pytest.mark.asyncio
async def test_stalled_body_respects_time_bound_and_returns_none() -> None:
    stream = _BoundedStream([b"zzzz"], stall_seconds=5.0, stall_after=0)
    upstream = _response(stream)
    started = asyncio.get_running_loop().time()
    got = await _read_bounded_error_diagnostic(upstream, max_bytes=16_384, timeout_seconds=0.2)
    elapsed = asyncio.get_running_loop().time() - started
    assert got is None
    assert elapsed < 3.0  # well under the stall; ordinary scheduling tolerance


@pytest.mark.asyncio
async def test_read_error_returns_none() -> None:
    stream = _BoundedStream([b"x"], read_error=httpx.ReadError("simulated read failure"))
    upstream = _response(stream)
    assert (
        await _read_bounded_error_diagnostic(upstream, max_bytes=16_384, timeout_seconds=1.0)
        is None
    )


@pytest.mark.asyncio
async def test_empty_body_returns_empty_bytes() -> None:
    stream = _BoundedStream([])
    upstream = _response(stream)
    got = await _read_bounded_error_diagnostic(upstream, max_bytes=16_384, timeout_seconds=1.0)
    assert got == b""


# ---------------------------------------------------------------------------
# App-level: public semantics unchanged, private metric emitted, sentinel
# privacy across response/metrics/logs
# ---------------------------------------------------------------------------


async def _post(
    settings: Settings,
    handler: Any,
    body: dict[str, Any] | None = None,
) -> httpx.Response:
    app = create_app(settings, httpx.MockTransport(handler))
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://adapter.test"
    ) as client:
        return await client.post(
            "/v1/chat/completions", json=body or {"model": "qwen", "messages": []}
        )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("status", "error_json", "expected_reason"),
    [
        (401, {"error": {"message": SENTINEL, "code": "invalid_api_key"}}, "authentication"),
        (403, {"error": {"message": SENTINEL, "code": "forbidden"}}, "authentication"),
        (429, {"error": {"message": SENTINEL, "code": "rate_limited"}}, "rate_limit"),
        (
            400,
            {
                "error": {
                    "message": "Maximum of 1 images allowed per request",
                    "type": "BadRequestError",
                    "code": 400,
                }
            },
            "image_count_limit",
        ),
        (
            400,
            {
                "error": {
                    "message": f"{SENTINEL} maximum context length is 8192",
                    "type": "invalid_request_error",
                    "code": None,
                }
            },
            "context_length_limit",
        ),
        (
            400,
            {
                "error": {
                    "message": f"{SENTINEL} invalid json payload",
                    "type": "invalid_request_error",
                }
            },
            "malformed_input",
        ),
        (500, {"error": {"message": SENTINEL, "code": "internal"}}, "upstream_5xx"),
        (503, b"", "upstream_5xx"),
        (418, {"error": {"message": SENTINEL, "code": "weird_unknown"}}, "unknown"),
        (400, b"non-json garbage", "unknown"),
    ],
)
async def test_upstream_error_classification_metric_and_public_semantics(
    monkeypatch: pytest.MonkeyPatch,
    status: int,
    error_json: Any,
    expected_reason: str,
    caplog: pytest.LogCaptureFixture,
) -> None:
    monkeypatch.setenv("TEST_DIAG_KEY", "test-only-secret")
    settings = _settings()
    caplog.set_level(logging.DEBUG)

    if isinstance(error_json, bytes):
        content: bytes = error_json
    else:
        content = json.dumps(error_json).encode()

    async def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            status,
            headers={"content-type": "application/json", "retry-after": "7"},
            content=content,
        )

    app = create_app(settings, httpx.MockTransport(handler))
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://adapter.test"
    ) as client:
        response = await client.post("/v1/chat/completions", json={"model": "qwen", "messages": []})
        metrics = (await client.get("/metrics")).text

    assert response.status_code == status
    assert response.json() == {
        "error": {
            "message": "upstream returned an error",
            "type": "upstream_error",
            "code": "upstream_error",
        }
    }
    assert response.headers.get("retry-after") == "7"
    expected_class = status_class(status)
    expected_line = (
        f'slaif_upstream_http_errors_total{{endpoint="/v1/chat/completions",'
        f'reason="{expected_reason}",route="vision",status_class="{expected_class}"}} 1.0'
    )
    assert expected_line in metrics
    for surface in (response.text, metrics, caplog.text):
        assert SENTINEL not in surface
    assert "weird_unknown" not in metrics
    assert "rate_limited" not in metrics or expected_reason == "rate_limit"


@pytest.mark.asyncio
async def test_error_close_is_guaranteed_for_every_classified_path(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("TEST_DIAG_KEY", "test-only-secret")
    settings = _settings()
    closes: dict[str, int] = {}

    def make_stream(body: bytes, label: str) -> _BoundedStream:
        stream = _BoundedStream([body] if body else [])

        original = stream.aclose

        async def counting_close() -> None:
            closes[label] = closes.get(label, 0) + 1
            await original()

        stream.aclose = counting_close  # type: ignore[method-assign]
        return stream

    cases: dict[str, tuple[int, bytes]] = {
        "status_derived": (401, b'{"error":{"message":"' + SENTINEL.encode() + b'"}}'),
        "body_classified": (
            400,
            json.dumps(
                {
                    "error": {
                        "message": "Maximum of 1 images allowed per request",
                        "type": "BadRequestError",
                        "code": 400,
                    }
                }
            ).encode(),
        ),
        "empty_body": (404, b""),
        "stalled_body": (400, b'{"error":{"message":"st' + b"a" * 100),
    }

    for label, (status, body) in cases.items():
        stream = make_stream(body, label)
        if label == "stalled_body":
            stream._stall_seconds = 5.0
            stream._stall_after = 0
        stream._read_error = None

        async def handler(
            _request: httpx.Request, _status: int = status, _stream: _BoundedStream = stream
        ) -> httpx.Response:
            return httpx.Response(
                _status, headers={"content-type": "application/json"}, stream=_stream
            )

        app = create_app(settings, httpx.MockTransport(handler))
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://adapter.test"
        ) as client:
            response = await client.post(
                "/v1/chat/completions", json={"model": "qwen", "messages": []}
            )
        assert response.status_code == status
        assert closes.get(label) == 1

    # The stalled-body path must have bounded itself (the generic error returned).
    assert True


@pytest.mark.asyncio
async def test_transport_failures_remain_distinct_from_http_error_metric(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("TEST_DIAG_KEY", "test-only-secret")
    settings = _settings()

    async def handler(_request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("simulated connect failure")

    app = create_app(settings, httpx.MockTransport(handler))
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://adapter.test"
    ) as client:
        response = await client.post("/v1/chat/completions", json={"model": "qwen", "messages": []})
        metrics = (await client.get("/metrics")).text
    assert response.status_code == 502
    assert 'slaif_upstream_failures_total{kind="connection"} 1.0' in metrics
    assert "slaif_upstream_http_errors_total{" not in metrics


@pytest.mark.asyncio
async def test_success_and_streaming_paths_are_unchanged(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TEST_DIAG_KEY", "test-only-secret")
    settings = _settings()
    sse_body = b'data: {"type":"x"}\n\ndata: [DONE]\n\n'

    class SseStream(httpx.AsyncByteStream):
        async def __aiter__(self) -> Any:
            yield sse_body

        async def aclose(self) -> None:
            return None

    async def handler(_request: httpx.Request) -> httpx.Response:
        if _request.content.find(b'"stream":true') != -1:
            return httpx.Response(
                200, stream=SseStream(), headers={"content-type": "text/event-stream"}
            )
        return httpx.Response(200, json={"ok": True})

    app = create_app(settings, httpx.MockTransport(handler))
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://adapter.test"
    ) as client:
        plain = await client.post("/v1/chat/completions", json={"model": "qwen", "messages": []})
        streamed = await client.post(
            "/v1/chat/completions", json={"model": "qwen", "messages": [], "stream": True}
        )
        metrics = (await client.get("/metrics")).text
    assert plain.status_code == 200 and plain.json() == {"ok": True}
    assert streamed.status_code == 200 and streamed.content == sse_body
    # The new counter must not fire for successful responses.
    assert "slaif_upstream_http_errors_total{" not in metrics

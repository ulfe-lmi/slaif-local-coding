"""CPU-only asynchronous OpenAI-compatible adapter."""

from __future__ import annotations

import asyncio
import json
import logging
import time
import uuid
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

import httpx
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, Response, StreamingResponse
from prometheus_client import CollectorRegistry, Counter, Gauge, Histogram, generate_latest

from .config import RouteConfig, Settings
from .image_policy import AmbiguousImageShape, apply_retain_newest, count_images

LOGGER = logging.getLogger("slaif.adapter")
HOP_BY_HOP = frozenset(
    {
        "connection",
        "keep-alive",
        "proxy-authenticate",
        "proxy-authorization",
        "te",
        "trailer",
        "trailers",
        "transfer-encoding",
        "upgrade",
        "content-length",
        "host",
    }
)
SPOOFED_INTERNAL = frozenset(
    {
        "x-slaif-principal",
        "x-slaif-session",
        "x-slaif-route",
        "x-slaif-compiler-bypass",
        "x-debug",
        "x-internal-debug",
    }
)
FORWARDED_RESPONSE_HEADERS = frozenset(
    {
        "content-type",
        "content-encoding",
        "cache-control",
        "openai-processing-ms",
        "retry-after",
        "x-request-id",
    }
)
PROXY_PATHS = frozenset({"/health", "/v1/models", "/v1/responses", "/v1/chat/completions"})


def _error(status: int, message: str, code: str) -> JSONResponse:
    return JSONResponse(
        status_code=status,
        content={"error": {"message": message, "type": "invalid_request_error", "code": code}},
    )


def _connection_tokens(headers: httpx.Headers | Any) -> set[str]:
    value = headers.get("connection", "")
    return {token.strip().lower() for token in value.split(",") if token.strip()}


async def _bounded_body(request: Request, maximum: int) -> bytes | None:
    content_length = request.headers.get("content-length")
    if content_length is not None:
        try:
            if int(content_length) > maximum:
                return None
        except ValueError:
            pass
    chunks: list[bytes] = []
    size = 0
    async for chunk in request.stream():
        size += len(chunk)
        if size > maximum:
            return None
        chunks.append(chunk)
    return b"".join(chunks)


def create_app(settings: Settings, transport: httpx.AsyncBaseTransport | None = None) -> FastAPI:
    timeout = httpx.Timeout(
        connect=settings.upstream.connect_timeout_seconds,
        read=settings.upstream.request_timeout_seconds,
        write=settings.upstream.write_timeout_seconds,
        pool=settings.upstream.pool_timeout_seconds,
    )
    client = httpx.AsyncClient(
        base_url=settings.upstream.origin(), timeout=timeout, transport=transport
    )
    registry = CollectorRegistry()
    request_count = Counter(
        "slaif_requests_total",
        "Adapter requests",
        ["endpoint", "route", "status", "stream"],
        registry=registry,
    )
    request_latency = Histogram(
        "slaif_response_header_duration_seconds",
        "Time until a local result or upstream response headers are available",
        ["endpoint", "route"],
        registry=registry,
    )
    stream_duration = Histogram(
        "slaif_stream_duration_seconds",
        "Total downstream streaming response duration",
        ["endpoint", "route", "status"],
        registry=registry,
    )
    image_count = Counter(
        "slaif_image_items_total", "Image policy counts", ["route", "result"], registry=registry
    )
    upstream_failures = Counter(
        "slaif_upstream_failures_total", "Sanitized upstream failures", ["kind"], registry=registry
    )
    readiness = Gauge(
        "slaif_readiness_state",
        "Last readiness result (1 ready, 0 not ready)",
        registry=registry,
    )

    @asynccontextmanager
    async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
        try:
            settings.upstream.api_key()
        except ValueError:
            LOGGER.warning("upstream credential is unavailable")
        yield
        await client.aclose()

    app = FastAPI(lifespan=lifespan)

    def route_for(endpoint: str, model: str) -> RouteConfig | None:
        matches = [
            route for route in settings.routes if route.model == model and route.enables(endpoint)
        ]
        return matches[0] if len(matches) == 1 else None

    @app.get("/healthz")
    async def healthz() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/readyz")
    async def readyz() -> Response:
        try:
            key = settings.upstream.api_key()
            response = await client.get("/health", headers={"authorization": f"Bearer {key}"})
            if not response.is_success:
                readiness.set(0)
                return _error(503, "upstream is not ready", "upstream_unavailable")
        except (ValueError, httpx.HTTPError):
            readiness.set(0)
            return _error(503, "upstream is not ready", "upstream_unavailable")
        readiness.set(1)
        return JSONResponse({"status": "ready"})

    @app.get("/metrics")
    async def metrics() -> Response:
        return Response(generate_latest(registry), media_type="text/plain; version=0.0.4")

    @app.api_route("/{path:path}", methods=["GET", "POST"])
    async def proxy(request: Request, path: str) -> Response:
        endpoint = "/" + path
        metric_endpoint = endpoint if endpoint in PROXY_PATHS else "unsupported"
        started = time.monotonic()
        route_name = "passthrough"
        stream = False

        def local_error(status: int, message: str, code: str) -> JSONResponse:
            request_count.labels(
                metric_endpoint, route_name, str(status), str(stream).lower()
            ).inc()
            request_latency.labels(metric_endpoint, route_name).observe(time.monotonic() - started)
            return _error(status, message, code)

        if endpoint not in PROXY_PATHS:
            return local_error(404, "unsupported endpoint", "unsupported_endpoint")
        body = await _bounded_body(request, settings.server.request_body_max_bytes)
        if body is None:
            return local_error(413, "request body exceeds configured limit", "request_too_large")

        if request.method == "POST":
            try:
                payload: Any = json.loads(body)
            except (UnicodeDecodeError, json.JSONDecodeError):
                return local_error(400, "request body must be valid JSON", "invalid_json")
            if not isinstance(payload, dict):
                return local_error(400, "request body must be a JSON object", "invalid_json")
            model = payload.get("model")
            if not isinstance(model, str):
                return local_error(400, "model is required", "missing_model")
            route = route_for(endpoint, model)
            if route is None:
                return local_error(
                    422, "no explicit route policy matches model and endpoint", "unknown_route"
                )
            route_name = route.name
            stream = payload.get("stream") is True
            try:
                seen = count_images(payload)
            except AmbiguousImageShape:
                return local_error(422, "ambiguous image content shape", "ambiguous_image_shape")
            maximum = route.max_images_per_request
            removed = 0
            if maximum is not None and seen > maximum:
                if route.image_overflow_policy == "reject":
                    image_count.labels(route_name, "rejected").inc(seen)
                    return local_error(
                        422, "request exceeds route image limit", "image_limit_exceeded"
                    )
                if route.image_overflow_policy == "retain_newest":
                    result = apply_retain_newest(payload, maximum)
                    payload, removed = result.value, result.removed
                    if count_images(payload) > maximum:
                        return local_error(
                            422, "image policy could not enforce route limit", "image_policy_failed"
                        )
                    body = json.dumps(payload, separators=(",", ":"), ensure_ascii=False).encode()
            image_count.labels(route_name, "seen").inc(seen)
            image_count.labels(route_name, "removed").inc(removed)

        try:
            key = settings.upstream.api_key()
        except ValueError:
            return local_error(503, "upstream credential is unavailable", "upstream_unavailable")
        request_connection_tokens = _connection_tokens(request.headers)
        headers = {
            name: value
            for name, value in request.headers.items()
            if name.lower()
            not in HOP_BY_HOP
            | SPOOFED_INTERNAL
            | request_connection_tokens
            | {"authorization", "accept-encoding"}
        }
        headers["authorization"] = f"Bearer {key}"
        headers["accept-encoding"] = "identity"
        headers["x-request-id"] = uuid.uuid4().hex
        query = request.scope.get("query_string", b"")
        target = httpx.URL(path=endpoint, query=query)
        upstream_request = client.build_request(
            request.method, target, headers=headers, content=body
        )
        try:
            upstream = await client.send(upstream_request, stream=True)
        except httpx.TimeoutException:
            upstream_failures.labels("timeout").inc()
            return local_error(503, "upstream timed out", "upstream_timeout")
        except httpx.HTTPError:
            upstream_failures.labels("connection").inc()
            return local_error(502, "upstream request failed", "upstream_error")

        response_connection_tokens = _connection_tokens(upstream.headers)
        response_headers = {
            k: v
            for k, v in upstream.headers.items()
            if k.lower() in FORWARDED_RESPONSE_HEADERS
            and k.lower() not in HOP_BY_HOP | response_connection_tokens
        }
        request_count.labels(
            endpoint, route_name, str(upstream.status_code), str(stream).lower()
        ).inc()
        request_latency.labels(endpoint, route_name).observe(time.monotonic() - started)

        if stream:

            async def chunks() -> AsyncIterator[bytes]:
                try:
                    async for chunk in upstream.aiter_raw():
                        yield chunk
                except asyncio.CancelledError:
                    upstream_failures.labels("disconnect").inc()
                    raise
                finally:
                    await upstream.aclose()
                    stream_duration.labels(endpoint, route_name, str(upstream.status_code)).observe(
                        time.monotonic() - started
                    )

            return StreamingResponse(
                chunks(), status_code=upstream.status_code, headers=response_headers
            )
        try:
            content = (
                upstream.content
                if upstream.is_stream_consumed
                else b"".join([chunk async for chunk in upstream.aiter_raw()])
            )
        finally:
            await upstream.aclose()
        return Response(content, status_code=upstream.status_code, headers=response_headers)

    return app

"""CPU-only asynchronous OpenAI-compatible adapter."""

from __future__ import annotations

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
from prometheus_client import CollectorRegistry, Counter, Histogram, generate_latest

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
    {"content-type", "cache-control", "openai-processing-ms", "x-request-id"}
)
PROXY_PATHS = frozenset({"/health", "/v1/models", "/v1/responses", "/v1/chat/completions"})


def _error(status: int, message: str, code: str) -> JSONResponse:
    return JSONResponse(
        status_code=status,
        content={"error": {"message": message, "type": "invalid_request_error", "code": code}},
    )


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
        "slaif_request_duration_seconds",
        "Adapter request latency",
        ["endpoint", "route"],
        registry=registry,
    )
    image_count = Counter(
        "slaif_image_items_total", "Image policy counts", ["route", "result"], registry=registry
    )
    upstream_failures = Counter(
        "slaif_upstream_failures_total", "Sanitized upstream failures", ["kind"], registry=registry
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
                return _error(503, "upstream is not ready", "upstream_unavailable")
        except (ValueError, httpx.HTTPError):
            return _error(503, "upstream is not ready", "upstream_unavailable")
        return JSONResponse({"status": "ready"})

    @app.get("/metrics")
    async def metrics() -> Response:
        return Response(generate_latest(registry), media_type="text/plain; version=0.0.4")

    @app.api_route("/{path:path}", methods=["GET", "POST"])
    async def proxy(request: Request, path: str) -> Response:
        endpoint = "/" + path
        if endpoint not in PROXY_PATHS:
            return _error(404, "unsupported endpoint", "unsupported_endpoint")
        started = time.monotonic()
        body = await request.body()
        if len(body) > settings.server.request_body_max_bytes:
            return _error(413, "request body exceeds configured limit", "request_too_large")

        route_name = "passthrough"
        stream = False
        if request.method == "POST":
            try:
                payload: Any = json.loads(body)
            except (UnicodeDecodeError, json.JSONDecodeError):
                return _error(400, "request body must be valid JSON", "invalid_json")
            if not isinstance(payload, dict):
                return _error(400, "request body must be a JSON object", "invalid_json")
            model = payload.get("model")
            if not isinstance(model, str):
                return _error(400, "model is required", "missing_model")
            route = route_for(endpoint, model)
            if route is None:
                return _error(
                    422, "no explicit route policy matches model and endpoint", "unknown_route"
                )
            route_name = route.name
            stream = payload.get("stream") is True
            try:
                seen = count_images(payload)
            except AmbiguousImageShape:
                return _error(422, "ambiguous image content shape", "ambiguous_image_shape")
            maximum = route.max_images_per_request
            removed = 0
            if maximum is not None and seen > maximum:
                if route.image_overflow_policy == "reject":
                    image_count.labels(route_name, "rejected").inc(seen)
                    return _error(422, "request exceeds route image limit", "image_limit_exceeded")
                if route.image_overflow_policy == "retain_newest":
                    result = apply_retain_newest(payload, maximum)
                    payload, removed = result.value, result.removed
                    if count_images(payload) > maximum:
                        return _error(
                            422, "image policy could not enforce route limit", "image_policy_failed"
                        )
                    body = json.dumps(payload, separators=(",", ":"), ensure_ascii=False).encode()
            image_count.labels(route_name, "seen").inc(seen)
            image_count.labels(route_name, "removed").inc(removed)

        try:
            key = settings.upstream.api_key()
        except ValueError:
            return _error(503, "upstream credential is unavailable", "upstream_unavailable")
        headers = {
            name: value
            for name, value in request.headers.items()
            if name.lower() not in HOP_BY_HOP | SPOOFED_INTERNAL | {"authorization"}
        }
        headers["authorization"] = f"Bearer {key}"
        headers["x-request-id"] = uuid.uuid4().hex
        upstream_request = client.build_request(
            request.method, endpoint, headers=headers, content=body
        )
        try:
            upstream = await client.send(upstream_request, stream=True)
        except httpx.TimeoutException:
            upstream_failures.labels("timeout").inc()
            return _error(503, "upstream timed out", "upstream_timeout")
        except httpx.HTTPError:
            upstream_failures.labels("connection").inc()
            return _error(502, "upstream request failed", "upstream_error")

        response_headers = {
            k: v for k, v in upstream.headers.items() if k.lower() in FORWARDED_RESPONSE_HEADERS
        }
        request_count.labels(
            endpoint, route_name, str(upstream.status_code), str(stream).lower()
        ).inc()
        request_latency.labels(endpoint, route_name).observe(time.monotonic() - started)

        if stream:

            async def chunks() -> AsyncIterator[bytes]:
                try:
                    async for chunk in upstream.aiter_raw():
                        if await request.is_disconnected():
                            upstream_failures.labels("disconnect").inc()
                            break
                        yield chunk
                finally:
                    await upstream.aclose()

            return StreamingResponse(
                chunks(), status_code=upstream.status_code, headers=response_headers
            )
        try:
            content = await upstream.aread()
        finally:
            await upstream.aclose()
        return Response(content, status_code=upstream.status_code, headers=response_headers)

    return app

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
from .constitution import (
    ObservationContext,
    observe_request_for_pipeline,
)
from .constitution.cache import CachePolicy
from .constitution.compiler import CompilerSettings
from .constitution.models import IncompleteReason, ObservationResult, TrustClass
from .constitution.pipeline import ConstitutionInjectionRejected, ConstitutionPipeline
from .image_policy import AmbiguousImageShape, apply_retain_newest, count_images
from .json_structure import JsonNestingTooDeep, enforce_json_nesting

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
SENSITIVE_REQUEST_HEADERS = frozenset(
    {
        "authorization",
        "cookie",
        "proxy-connection",
        "set-cookie",
        "x-forwarded-for",
        "x-forwarded-host",
        "x-forwarded-port",
        "x-forwarded-proto",
        "forwarded",
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


def _forward_request_header(name: str, connection_tokens: set[str]) -> bool:
    lowered = name.lower()
    return not (
        lowered in HOP_BY_HOP | SPOOFED_INTERNAL | SENSITIVE_REQUEST_HEADERS | connection_tokens
        or lowered.startswith("x-slaif-")
        or lowered.startswith("x-internal-")
    )


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
    LOGGER.setLevel(settings.observability.log_level)
    constitution_pipeline: ConstitutionPipeline | None = None
    if settings.constitution.enabled:
        compiler_settings = CompilerSettings(
            base_url=settings.upstream.base_url.rstrip("/"),
            api_key_env=settings.compiler.api_key_env,
            model=settings.upstream.model,
            timeout_seconds=settings.compiler.timeout_seconds,
            max_attempts=settings.compiler.max_attempts,
            max_concurrency=settings.compiler.max_parallel_calls,
            max_source_bytes=settings.compiler.max_source_bytes,
            max_candidates=settings.compiler.max_candidates,
            max_output_tokens=settings.compiler.max_output_tokens,
            max_prompt_bytes=settings.compiler.max_prompt_bytes,
            max_output_bytes=settings.compiler.max_output_bytes,
            max_json_depth=settings.compiler.max_json_depth,
        )
        cache_policy = CachePolicy(
            root=settings.cache.root,
            fallback_root=settings.cache.fallback_root,
            max_total_bytes=settings.cache.max_total_bytes,
            max_entry_bytes=settings.cache.max_entry_bytes,
            max_pinned_bytes=settings.cache.max_pinned_bytes,
            max_entries=settings.cache.max_entries,
            ttl_seconds=settings.cache.ttl_seconds,
            max_scan_entries=settings.cache.max_scan_entries,
        )
        constitution_pipeline = ConstitutionPipeline(
            constitution=settings.constitution,
            compiler=compiler_settings,
            cache_policy=cache_policy,
            registry=registry,
            client=client,
        )
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
    readiness_components = Gauge(
        "slaif_readiness_component_state",
        "Last readiness state by fixed component (1 available, 0 unavailable)",
        ["component"],
        registry=registry,
    )
    observed_roots = Counter(
        "slaif_constitution_roots_total",
        "Observed constitutional roots by fixed evidence class",
        ["endpoint", "route", "evidence_type"],
        registry=registry,
    )
    observed_candidates = Counter(
        "slaif_constitution_candidates_total",
        "Syntactically accepted candidate references",
        ["endpoint", "route"],
        registry=registry,
    )
    observed_rejections = Counter(
        "slaif_constitution_candidate_rejections_total",
        "Rejected candidate tokens by fixed safe reason",
        ["endpoint", "route", "reason"],
        registry=registry,
    )
    observation_status = Counter(
        "slaif_constitution_observations_total",
        "Request-only observation outcomes",
        ["endpoint", "route", "status", "reason"],
        registry=registry,
    )
    observation_duration = Histogram(
        "slaif_constitution_observation_duration_seconds",
        "Bounded request-only observation time",
        ["endpoint", "route", "status"],
        registry=registry,
    )
    dependency_observations = Counter(
        "slaif_constitution_dependency_observations_total",
        "Request-only constitutional dependency observation outcomes",
        ["endpoint", "route", "state"],
        registry=registry,
    )

    @asynccontextmanager
    async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
        try:
            settings.upstream.api_key()
        except ValueError:
            LOGGER.warning("upstream credential is unavailable")
        try:
            yield
        finally:
            if constitution_pipeline is not None:
                await constitution_pipeline.aclose()
            await client.aclose()

    app = FastAPI(lifespan=lifespan)
    app.state.constitution_pipeline = constitution_pipeline

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
        cache_state = "disabled"
        compiler_state = "disabled"
        if constitution_pipeline is not None:
            cache_state = (
                "ready"
                if (
                    constitution_pipeline.cache.available
                    and not constitution_pipeline.cache.degraded
                )
                else ("degraded" if constitution_pipeline.cache.available else "unavailable")
            )
            try:
                constitution_pipeline.compiler.settings.api_key()
                compiler_state = "ready"
            except ValueError:
                compiler_state = "unavailable"
        try:
            key = settings.upstream.api_key()
            response = await client.get("/health", headers={"authorization": f"Bearer {key}"})
            if not response.is_success:
                raise RuntimeError("upstream unavailable")
        except (ValueError, httpx.HTTPError):
            upstream_state = "unavailable"
        except RuntimeError:
            upstream_state = "unavailable"
        else:
            upstream_state = "ready"
        readiness_components.labels("upstream").set(upstream_state == "ready")
        readiness_components.labels("compiler").set(compiler_state != "unavailable")
        readiness_components.labels("cache").set(cache_state != "unavailable")
        if upstream_state != "ready" or compiler_state == "unavailable":
            readiness.set(0)
            return JSONResponse(
                status_code=503,
                content={
                    "status": "not_ready",
                    "config": "valid",
                    "upstream": upstream_state,
                    "compiler": compiler_state,
                    "cache": cache_state,
                },
            )
        readiness.set(1)
        return JSONResponse(
            content={
                "status": "ready",
                "config": "valid",
                "upstream": upstream_state,
                "compiler": compiler_state,
                "cache": cache_state,
            }
        )

    @app.get("/metrics")
    async def metrics() -> Response:
        if not settings.observability.metrics_enabled:
            return _error(404, "metrics are disabled", "metrics_disabled")
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
                enforce_json_nesting(body, settings.server.json_max_nesting_depth)
                payload: Any = json.loads(body)
            except JsonNestingTooDeep:
                return local_error(
                    400,
                    "request JSON exceeds configured nesting limit",
                    "json_nesting_too_deep",
                )
            except (UnicodeDecodeError, json.JSONDecodeError, ValueError):
                return local_error(400, "request body must be valid JSON", "invalid_json")
            except RecursionError:
                return local_error(
                    400,
                    "request JSON exceeds configured nesting limit",
                    "json_nesting_too_deep",
                )
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
            except RecursionError:
                return local_error(
                    400,
                    "request JSON exceeds configured nesting limit",
                    "json_nesting_too_deep",
                )
            maximum = route.max_images_per_request
            removed = 0
            if maximum is not None and seen > maximum:
                if route.image_overflow_policy == "reject":
                    image_count.labels(route_name, "rejected").inc(seen)
                    return local_error(
                        422, "request exceeds route image limit", "image_limit_exceeded"
                    )
                if route.image_overflow_policy == "retain_newest":
                    try:
                        result = apply_retain_newest(payload, maximum)
                        payload, removed = result.value, result.removed
                        if count_images(payload) > maximum:
                            return local_error(
                                422,
                                "image policy could not enforce route limit",
                                "image_policy_failed",
                            )
                        body = json.dumps(
                            payload, separators=(",", ":"), ensure_ascii=True
                        ).encode()
                    except (RecursionError, TypeError, ValueError, UnicodeError):
                        return local_error(
                            400,
                            "request body must be valid JSON",
                            "invalid_json",
                        )
            image_count.labels(route_name, "seen").inc(seen)
            image_count.labels(route_name, "removed").inc(removed)
            post_image_body = body
            observation: ObservationResult | None = None
            observation_sources: dict[tuple[str, str], bytes] = {}
            observation_dependencies: dict[str, bytes] = {}
            if route.observation_enabled:
                observation_started = time.monotonic()
                try:
                    observed_result, source_bytes, dependency_bytes = observe_request_for_pipeline(
                        payload,
                        ObservationContext(
                            endpoint=endpoint,
                            route_id=route_name,
                            model=model,
                            streaming=stream,
                            # Client hints are intentionally neither trusted nor copied.
                            discriminator_trust=TrustClass.ABSENT,
                        ),
                        settings.observation,
                    )
                    observation = observed_result
                    observation_sources = source_bytes
                    observation_dependencies = dependency_bytes
                    for root in observation.roots:
                        for evidence_type in {item.type for item in root.evidence}:
                            observed_roots.labels(endpoint, route_name, evidence_type.value).inc()
                    observed_candidates.labels(endpoint, route_name).inc(
                        observation.accepted_candidates
                    )
                    for rejection in observation.rejection_counts:
                        observed_rejections.labels(
                            endpoint, route_name, rejection.reason.value
                        ).inc(rejection.count)

                    dependency_observations.labels(endpoint, route_name, "observed").inc(
                        len(observation.dependencies)
                    )
                    for dependency_rejection in observation.dependency_rejections:
                        dependency_observations.labels(
                            endpoint, route_name, dependency_rejection.reason.value
                        ).inc(dependency_rejection.count)
                    status = "complete" if observation.complete else "incomplete"
                    reasons = observation.incomplete_reasons or (None,)
                    for reason in reasons:
                        label = reason.value if isinstance(reason, IncompleteReason) else "none"
                        observation_status.labels(endpoint, route_name, status, label).inc()
                except Exception:  # observation is optional and semantics-preserving
                    status = "error"
                    observation_status.labels(
                        endpoint, route_name, status, IncompleteReason.PARSING_ERROR.value
                    ).inc()
                observation_duration.labels(endpoint, route_name, status).observe(
                    time.monotonic() - observation_started
                )

            if constitution_pipeline is not None and route.constitution_enabled:
                if observation is None:
                    pipeline_result = constitution_pipeline.preserve_unobserved(
                        payload=payload,
                        body=post_image_body,
                        endpoint=endpoint,
                        route_name=route_name,
                    )
                else:
                    try:
                        pipeline_result = await constitution_pipeline.process(
                            payload=payload,
                            observation=observation,
                            source_bytes_by_root=observation_sources,
                            source_bytes_by_dependency=observation_dependencies,
                            observation_policy=settings.observation,
                            route=route,
                            endpoint=endpoint,
                            post_image_body=post_image_body,
                            model=model,
                        )
                    except ConstitutionInjectionRejected as exc:
                        return local_error(
                            422,
                            "constitutional injection failed",
                            f"constitution_{exc.reason}",
                        )
                payload, body = pipeline_result.payload, pipeline_result.body

        try:
            key = settings.upstream.api_key()
        except ValueError:
            return local_error(503, "upstream credential is unavailable", "upstream_unavailable")
        request_connection_tokens = _connection_tokens(request.headers)
        headers = {
            name: value
            for name, value in request.headers.items()
            if _forward_request_header(name, request_connection_tokens)
            and name.lower() != "accept-encoding"
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

        if upstream.status_code >= 400:
            error_headers = {
                key: value
                for key, value in response_headers.items()
                if key.lower()
                in {"cache-control", "openai-processing-ms", "retry-after", "x-request-id"}
            }
            await upstream.aclose()
            return JSONResponse(
                status_code=upstream.status_code,
                content={
                    "error": {
                        "message": "upstream returned an error",
                        "type": "upstream_error",
                        "code": "upstream_error",
                    }
                },
                headers=error_headers,
            )

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
            if upstream.is_stream_consumed:
                content = upstream.content
                if len(content) > settings.server.response_body_max_bytes:
                    upstream_failures.labels("response_too_large").inc()
                    return local_error(
                        502,
                        "upstream response exceeds configured limit",
                        "upstream_response_too_large",
                    )
            else:
                response_chunks: list[bytes] = []
                size = 0
                async for chunk in upstream.aiter_raw():
                    size += len(chunk)
                    if size > settings.server.response_body_max_bytes:
                        upstream_failures.labels("response_too_large").inc()
                        return local_error(
                            502,
                            "upstream response exceeds configured limit",
                            "upstream_response_too_large",
                        )
                    response_chunks.append(chunk)
                content = b"".join(response_chunks)
        except httpx.HTTPError:
            upstream_failures.labels("response_read").inc()
            return local_error(502, "upstream response failed", "upstream_error")
        finally:
            await upstream.aclose()
        return Response(content, status_code=upstream.status_code, headers=response_headers)

    return app

"""CPU-only asynchronous OpenAI-compatible adapter."""

from __future__ import annotations

import asyncio
import json
import logging
import secrets
import time
import uuid
from collections.abc import AsyncIterator, Callable
from contextlib import asynccontextmanager
from typing import Any

import httpx
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, Response, StreamingResponse
from prometheus_client import CollectorRegistry, Counter, Gauge, Histogram, generate_latest

from .config import V1_PROFILE, RouteConfig, Settings, validate_service_token
from .constitution import (
    ObservationContext,
    observe_request_for_pipeline,
)
from .constitution.bundles.observation_models import PathContext
from .constitution.bundles.observe import observe_request
from .constitution.bundles.v1_application import (
    V1IssuanceContext,
    V1RequestRefusal,
    V1SessionTable,
    advance_v1_session,
    build_session_address,
    establish_v1_session,
    prepare_replay_shadow,
    prepare_v1_transaction,
)
from .constitution.bundles.v1_runtime import (
    V1Runtime,
    build_v1_runtime,
)

# Explicit re-export of the fixed typed v1 startup failure (the 022-a
# public entry-point surface; the definition lives with the component).
from .constitution.bundles.v1_runtime import V1RuntimeUnavailableError as V1RuntimeUnavailableError
from .constitution.bundles.v1_telemetry import (
    V1Stage,
    V1StageEvent,
    V1StageRecorder,
)
from .constitution.cache import CachePolicy, RequestIdentity
from .constitution.compiler import CompilerSettings
from .constitution.models import IncompleteReason, ObservationResult, TrustClass
from .constitution.pipeline import ConstitutionInjectionRejected, ConstitutionPipeline
from .gateway_identity import ReplayProtector, SignedIdentityError, verify_signed_identity
from .image_policy import AmbiguousImageShape, apply_retain_newest, count_images
from .json_structure import JsonNestingTooDeep, enforce_json_nesting
from .tool_policy import ResponsesToolPolicyError, apply_responses_tool_policy
from .upstream_diagnostics import classify_upstream_error, status_class

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
MAX_AUTHORIZATION_HEADER_BYTES = 8192


def _error(status: int, message: str, code: str) -> JSONResponse:
    return JSONResponse(
        status_code=status,
        content={"error": {"message": message, "type": "invalid_request_error", "code": code}},
    )


def _authorization_failure(status: int, *, challenge: bool) -> JSONResponse:
    headers = {"WWW-Authenticate": "Bearer"} if challenge else None
    return JSONResponse(
        status_code=status,
        content={
            "error": {
                "message": "invalid service authorization"
                if status == 401
                else "service authorization denied",
                "type": "invalid_request_error",
                "code": "invalid_service_authorization"
                if status == 401
                else "service_authorization_denied",
            }
        },
        headers=headers,
    )


def _authenticate_service_request(request: Request, settings: Settings) -> Response | None:
    """Authenticate only the private gateway ingress; never return token data."""
    if not settings.gateway_ingress.enabled:
        return None

    authorization_values = request.headers.getlist("authorization")
    if len(authorization_values) != 1:
        return _authorization_failure(401, challenge=True)
    authorization = authorization_values[0]
    try:
        authorization_bytes = authorization.encode("utf-8")
    except UnicodeEncodeError:
        return _authorization_failure(401, challenge=True)
    if len(authorization_bytes) > MAX_AUTHORIZATION_HEADER_BYTES:
        return _authorization_failure(401, challenge=True)
    parts = authorization.split(" ")
    if len(parts) != 2 or parts[0].lower() != "bearer" or not parts[1]:
        return _authorization_failure(401, challenge=True)
    supplied_token = parts[1]
    try:
        validate_service_token(supplied_token)
    except ValueError:
        return _authorization_failure(401, challenge=True)
    try:
        expected_token = settings.gateway_ingress.service_token()
    except ValueError:
        return _error(503, "service authentication is unavailable", "service_auth_unavailable")
    if not secrets.compare_digest(supplied_token, expected_token):
        return _authorization_failure(403, challenge=False)
    return None


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


async def _read_bounded_error_diagnostic(
    upstream: httpx.Response,
    *,
    max_bytes: int,
    timeout_seconds: float,
) -> bytes | None:
    """Read at most ``max_bytes`` of an upstream error body within the bound.

    Order 015-a (P01): streaming iteration appends only the remaining
    permitted slice, so a single oversized chunk never causes retained bytes
    to exceed the allowance.  The read stops at the byte bound, the time
    bound, or the end of the body.  Timeout, cancellation, malformed
    framing, or read errors return ``None`` (the caller still closes the
    response and returns the generic public error).  Bytes returned here are
    consumed only by the closed classifier and are never forwarded, logged,
    or persisted.
    """
    if upstream.is_stream_consumed:
        # Non-streaming transport (e.g. mock): the body is already fully in
        # memory.  Honor the byte bound by taking the permitted slice only.
        return upstream.content[:max_bytes]
    chunks: list[bytes] = []
    state = {"remaining": max_bytes}

    async def _read() -> bytes:
        async for chunk in upstream.aiter_raw():
            if state["remaining"] <= 0:
                break
            piece = chunk[: state["remaining"]]
            state["remaining"] -= len(piece)
            if piece:
                chunks.append(piece)
        return b"".join(chunks)

    try:
        return await asyncio.wait_for(_read(), timeout=timeout_seconds)
    except asyncio.CancelledError:
        raise
    except (TimeoutError, httpx.HTTPError, OSError, ValueError):
        return None


def create_app(
    settings: Settings,
    transport: httpx.AsyncBaseTransport | None = None,
    signed_identity_clock: Callable[[], float] | None = None,
    v1_stage_observer: Callable[[V1StageRecorder], None] | None = None,
) -> FastAPI:
    # 023-a: the explicit test-only stage observer (content-free):
    # it receives each governed request's owning-stage recorder
    # (closed stage/outcome facts and bounded counts only).  It is
    # constructor-injected, default-off, carries no HTTP surface,
    # and never sees a raw byte (the protected synthetic evidence
    # is assembled by the test harness from its own fake-upstream
    # and compiler captures plus these content-free facts).
    v1_runtime: V1Runtime | None = None
    if settings.context_cache.profile == V1_PROFILE:
        # 022-c: the runnable v1 profile.  The closed construction order
        # verifies the recovery capability and the pinned tokenizer
        # BEFORE any HTTP client exists, so the fixed typed startup
        # failure leaves no network component and no legacy pipeline
        # behind; v1 governed routes never instantiate or use the
        # legacy cache/compiler/rehydration.
        v1_runtime = build_v1_runtime(settings, compiler_transport=transport)
    # The process-owned live v1 session table (one worker, one
    # process; the closed registry identity join over the actual
    # registered namespace records).
    v1_sessions: V1SessionTable | None = V1SessionTable() if v1_runtime is not None else None
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
    replay_protector = (
        ReplayProtector(
            ttl_seconds=settings.gateway_ingress.replay_ttl_seconds,
            max_entries=settings.gateway_ingress.max_replay_entries,
        )
        if settings.gateway_ingress.signed
        else None
    )
    if settings.constitution.enabled and v1_runtime is None:
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
            max_output_tokens_ceiling=settings.compiler.max_output_tokens_ceiling,
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
    upstream_http_errors = Counter(
        "slaif_upstream_http_errors_total",
        "Upstream HTTP rejections by bounded status class and closed private reason",
        ["endpoint", "route", "status_class", "reason"],
        registry=registry,
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
    response_tool_items = Counter(
        "slaif_responses_tool_policy_items_total",
        "Bounded Responses tool declaration counts",
        ["route", "kind"],
        registry=registry,
    )
    response_tool_policy = Counter(
        "slaif_responses_tool_policy_total",
        "Route-scoped Responses tool policy outcomes",
        ["route", "outcome", "reason"],
        registry=registry,
    )
    # 023-a: the governed v1 stage telemetry (fixed stage/outcome
    # enums, low-cardinality content-free labels; the backend
    # provider usage ledger is independent of any client-reported
    # cumulative usage, and the internal compiler dispatch is
    # metered apart from the main upstream).
    v1_stage_total = Counter(
        "slaif_v1_stage_total",
        "Governed v1 stage outcomes at the owning stage",
        ["route", "stage", "outcome"],
        registry=registry,
    )
    v1_stage_duration = Histogram(
        "slaif_v1_stage_duration_seconds",
        "Governed v1 stage durations at the owning stage",
        ["route", "stage", "outcome"],
        registry=registry,
    )
    v1_refusals = Counter(
        "slaif_v1_refusals_total",
        "Closed governed v1 refusals at the owning stage",
        ["route", "reason"],
        registry=registry,
    )
    v1_compiler_dispatch = Counter(
        "slaif_v1_compiler_dispatch_total",
        "Actual internal compiler dispatches (the direct tool-free channel)",
        ["route"],
        registry=registry,
    )
    v1_replacement_edits = Counter(
        "slaif_v1_replacement_edits_total",
        "Committed v1 source edits",
        ["route"],
        registry=registry,
    )
    v1_markers = Counter(
        "slaif_v1_markers_total",
        "Committed v1 source markers",
        ["route", "kind"],
        registry=registry,
    )
    v1_reuse_class = Counter(
        "slaif_v1_reuse_class_total",
        "Closed four-way v1 cache distinction facts",
        ["route", "reuse_class"],
        registry=registry,
    )
    v1_main_forward = Counter(
        "slaif_v1_main_forward_total",
        "Actual governed v1 main upstream forwards",
        ["route"],
        registry=registry,
    )
    v1_provider_usage = Counter(
        "slaif_v1_provider_usage_tokens_total",
        "Backend provider usage of the direct main response",
        ["route", "kind"],
        registry=registry,
    )
    # The content-free owning-stage measurement families (objective
    # 023-a, handoff section 15): the closed acquisition / graph /
    # admission counts are published under fixed kind labels (the
    # closed detail names -- revision / epoch evidence stays out of
    # metric labels), and the actual final-envelope injection token
    # measurements are published as histogram samples (the value is
    # the sample, never a label); the configured aggregate limit is
    # the fixed per-route gauge.
    v1_acquisition_facts = Counter(
        "slaif_v1_acquisition_facts_total",
        "Content-free content-acquisition facts at the owning stage",
        ["route", "kind"],
        registry=registry,
    )
    v1_graph_facts = Counter(
        "slaif_v1_graph_facts_total",
        "Content-free current-graph facts at the owning stage",
        ["route", "kind"],
        registry=registry,
    )
    v1_admission_facts = Counter(
        "slaif_v1_admission_facts_total",
        "Content-free admission facts at the owning stage",
        ["route", "kind"],
        registry=registry,
    )
    v1_injection_tokens = Histogram(
        "slaif_v1_injection_tokens",
        "Actual final-envelope injection token measurements at the owning stage",
        ["route", "kind"],
        registry=registry,
    )
    v1_injection_aggregate_limit = Gauge(
        "slaif_v1_injection_aggregate_limit_tokens",
        "Configured aggregate injection limit of the governed route",
        ["route"],
        registry=registry,
    )
    # The configured aggregate limit of each governed v1 route
    # (the fixed budget fact the actual final-injection token
    # measurements are bounded by): set once at construction from
    # the ACTUAL budget plan, content-free.
    if v1_runtime is not None:
        for _governed_route in v1_runtime.governed_routes:
            v1_injection_aggregate_limit.labels(_governed_route).set(
                float(v1_runtime.budget_plan.aggregate)
            )

    def _v1_emit(route_name: str, event: V1StageEvent) -> None:
        """The owning-stage metric emit: the closed stage/outcome
        pair and the bounded numeric details the stage exposed
        (no content, no identifiers, no digests, no paths)."""
        v1_stage_total.labels(route_name, event.stage.value, event.outcome).inc()
        if event.duration > 0.0:
            v1_stage_duration.labels(route_name, event.stage.value, event.outcome).observe(
                event.duration
            )
        if event.stage is V1Stage.COMPILATION:
            for name, value in event.details:
                if name == "invocations":
                    # The ACTUAL internal compiler dispatch count
                    # (independent of the main upstream ledger).
                    v1_compiler_dispatch.labels(route_name).inc(value)
        elif event.stage is V1Stage.ACQUISITION:
            # The content-free acquisition facts under their
            # closed detail names (the revision stays a detail
            # value, never a metric label).
            for name, value in event.details:
                if name != "revision":
                    v1_acquisition_facts.labels(route_name, name).inc(value)
        elif event.stage is V1Stage.GRAPH:
            for name, value in event.details:
                v1_graph_facts.labels(route_name, name).inc(value)
        elif event.stage is V1Stage.ADMISSION:
            for name, value in event.details:
                v1_admission_facts.labels(route_name, name).inc(value)
        elif event.stage is V1Stage.INJECTION:
            # The actual final-envelope token measurements are
            # histogram samples (bounded counts; the configured
            # aggregate limit itself is the fixed per-route gauge,
            # never a per-request sample).
            for name, value in event.details:
                if name == "governance_tokens":
                    v1_injection_tokens.labels(route_name, "governance").observe(value)
                elif name == "request_tokens":
                    v1_injection_tokens.labels(route_name, "request").observe(value)
        elif event.stage is V1Stage.REPLACEMENT:
            for name, value in event.details:
                if name == "edits":
                    v1_replacement_edits.labels(route_name).inc(value)
                elif name == "markers_emitted":
                    v1_markers.labels(route_name, "emitted").inc(value)
                elif name == "markers_replayed":
                    v1_markers.labels(route_name, "replayed").inc(value)
        elif event.stage is V1Stage.REUSE_CLASS:
            v1_reuse_class.labels(route_name, event.outcome).inc()

    @asynccontextmanager
    async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
        if settings.gateway_ingress.enabled:
            try:
                settings.gateway_ingress.service_token()
            except ValueError:
                LOGGER.warning("gateway ingress service credential is unavailable")
            if settings.gateway_ingress.signed:
                try:
                    settings.gateway_ingress.signing_secret()
                except ValueError:
                    LOGGER.warning("gateway signed identity secret is unavailable")
        try:
            settings.upstream.api_key()
        except ValueError:
            LOGGER.warning("upstream credential is unavailable")
        try:
            yield
        finally:
            if v1_runtime is not None:
                if v1_sessions is not None:
                    # Explicit process teardown: fence and release
                    # every live v1 owner through the accepted 020
                    # composed path (the owned IO drains, the work
                    # plane and the RAM ownership release in the
                    # accepted order, and the exclusive writer
                    # session closes only after the store owner is
                    # gone).
                    for session in v1_sessions.sessions():
                        if session.session_owner is not None:
                            await session.session_owner.teardown()
                        else:
                            session.owner.teardown(session.namespace)
                    v1_sessions.clear()
                await v1_runtime.aclose()
            if constitution_pipeline is not None:
                await constitution_pipeline.aclose()
            await client.aclose()

    app = FastAPI(lifespan=lifespan)
    app.state.constitution_pipeline = constitution_pipeline
    app.state.signed_identity_replay = replay_protector
    app.state.v1_runtime = v1_runtime
    app.state.v1_sessions = v1_sessions

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
        ingress_state = "disabled"
        if settings.gateway_ingress.enabled:
            try:
                settings.gateway_ingress.service_token()
            except ValueError:
                ingress_state = "unavailable"
            else:
                if settings.gateway_ingress.signed:
                    try:
                        settings.gateway_ingress.signing_secret()
                    except ValueError:
                        ingress_state = "unavailable"
                    else:
                        ingress_state = "ready"
                else:
                    ingress_state = "ready"
        cache_state = "disabled"
        compiler_state = "disabled"
        if v1_runtime is not None:
            # The v1 runtime is process-owned: the recovery store root
            # was verified at startup (ready) and the bounded compiler
            # is ready when its protected credential reference resolves.
            cache_state = "ready"
            try:
                v1_runtime.compiler.config.api_key()
                compiler_state = "ready"
            except ValueError:
                compiler_state = "unavailable"
        elif constitution_pipeline is not None:
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
        readiness_components.labels("gateway_ingress").set(ingress_state != "unavailable")
        if (
            upstream_state != "ready"
            or compiler_state == "unavailable"
            or ingress_state == "unavailable"
        ):
            readiness.set(0)
            return JSONResponse(
                status_code=503,
                content={
                    "status": "not_ready",
                    "config": "valid",
                    "upstream": upstream_state,
                    "gateway_ingress": ingress_state,
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
                "gateway_ingress": ingress_state,
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
        authentication_error = _authenticate_service_request(request, settings)
        if authentication_error is not None:
            request_count.labels(
                metric_endpoint,
                route_name,
                str(authentication_error.status_code),
                str(stream).lower(),
            ).inc()
            request_latency.labels(metric_endpoint, route_name).observe(time.monotonic() - started)
            return authentication_error
        body = await _bounded_body(request, settings.server.request_body_max_bytes)
        if body is None:
            return local_error(413, "request body exceeds configured limit", "request_too_large")

        v1_issuance: V1IssuanceContext | None = None
        v1_recorder: V1StageRecorder | None = None
        verified_identity = None
        if settings.gateway_ingress.signed:
            assert replay_protector is not None
            try:
                verified_identity = verify_signed_identity(
                    request,
                    body,
                    settings.gateway_ingress,
                    replay_protector,
                    now=(signed_identity_clock or time.time)(),
                )
            except SignedIdentityError as exc:
                return local_error(exc.status_code, "signed identity rejected", exc.code)
            if request.method == "GET":
                if not any(route.name == verified_identity.route for route in settings.routes):
                    return local_error(
                        403,
                        "signed identity route is not configured",
                        "signed_identity_route_mismatch",
                    )
                route_name = verified_identity.route

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
            if verified_identity is not None and verified_identity.route != route.name:
                return local_error(
                    403,
                    "signed identity route mismatch",
                    "signed_identity_route_mismatch",
                )
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
            if endpoint == "/v1/responses":
                try:
                    tool_result = apply_responses_tool_policy(payload, route.responses_tool_policy)
                except ResponsesToolPolicyError as exc:
                    response_tool_items.labels(route_name, "observed").inc(exc.observed_count)
                    response_tool_policy.labels(route_name, "rejected", exc.reason).inc()
                    return local_error(422, exc.message, exc.code)
                response_tool_items.labels(route_name, "observed").inc(tool_result.observed_count)
                response_tool_items.labels(route_name, "removed").inc(tool_result.removed_count)
                response_tool_policy.labels(
                    route_name, tool_result.outcome, tool_result.reason
                ).inc()
                if tool_result.changed:
                    payload = tool_result.payload
                    body = json.dumps(payload, separators=(",", ":"), ensure_ascii=True).encode()
            post_image_body = body
            # 022-c: the governed v1 request path.  Ordered after the
            # request guard / auth / route match / image policy and the
            # Responses tool policy (the closed pipeline order) and
            # before the legacy observation: a v1 governed route never
            # instantiates or touches the legacy cache / compiler /
            # rehydration, and no caller assertion of scope / session /
            # compiler bypass / trusted issuance is used (the verified
            # signed identity or the configured trusted static one).
            if v1_runtime is not None and v1_sessions is not None and route.constitution_enabled:
                contract = v1_runtime.governed_routes.get(route.name)
                if contract is not None:
                    v1_endpoint = "responses" if endpoint == "/v1/responses" else "chat"
                    if verified_identity is not None:
                        v1_identity: RequestIdentity = verified_identity
                    else:
                        # The existing explicitly configured trusted
                        # static identity (the v1 settings closure
                        # requires the enabled constitution with the
                        # complete static identity).
                        assert (
                            settings.constitution.principal is not None
                            and settings.constitution.session is not None
                            and settings.constitution.repository is not None
                        )
                        v1_identity = RequestIdentity(
                            principal=settings.constitution.principal,
                            route=route.name,
                            session=settings.constitution.session,
                            repository=settings.constitution.repository,
                        )
                    address = build_session_address(v1_runtime, v1_identity, route, contract)
                    # 023-a: the per-request owning-stage recorder
                    # (content-free; emitted to the private metrics
                    # at each owning stage, handed to the explicit
                    # test-only stage observer when enabled).
                    v1_recorder = V1StageRecorder(
                        route=route.name,
                        endpoint=v1_endpoint,
                        emit=lambda event: _v1_emit(route.name, event),
                    )
                    if v1_stage_observer is not None:
                        v1_stage_observer(v1_recorder)
                    v1_recognition_started = V1StageRecorder.begin()
                    v1_observation = observe_request(payload, endpoint=v1_endpoint)
                    # The recognition stage counts the ACTUAL
                    # observed root occurrences (fixed evidence
                    # classes, closed outcomes; never a request
                    # field or a response code).
                    root_occurrences = [
                        occurrence
                        for occurrence in v1_observation.roots.occurrences
                        if occurrence.kind.value == "root"
                    ]
                    root_ok = sum(
                        1 for occurrence in root_occurrences if occurrence.status.value == "ok"
                    )
                    if root_ok > 0:
                        recognition_outcome = "root"
                    elif root_occurrences:
                        recognition_outcome = "root_rejected"
                    else:
                        recognition_outcome = "rootless"
                    v1_recorder.record(
                        V1Stage.RECOGNITION,
                        recognition_outcome,
                        v1_recognition_started,
                        root_occurrences=len(root_occurrences),
                        root_ok=root_ok,
                    )
                    established = await establish_v1_session(
                        v1_runtime,
                        v1_sessions,
                        address=address,
                        identity=v1_identity,
                        route=route,
                        contract=contract,
                        observation=v1_observation,
                        payload=payload,
                        endpoint=v1_endpoint,
                        telemetry=v1_recorder,
                    )
                    if isinstance(established, V1RequestRefusal):
                        v1_refusals.labels(route.name, established.reason.value).inc()
                        return local_error(
                            established.status_code,
                            "governed v1 request refused",
                            established.code,
                        )
                    if established is not None:
                        # The workspace is the legitimate observed scope
                        # (cold) or the verified resumed scope (resume);
                        # the transaction geometry is re-observed under
                        # it before the final replay scan.
                        scoped_observation = observe_request(
                            payload,
                            context=PathContext(workspace=established.namespace.workspace),
                            endpoint=v1_endpoint,
                        )
                        # The marker-shaped source replay is detected
                        # and authenticated BEFORE the transition's
                        # raw acquisition (022-c section 1/2): the
                        # shadow the transition observes, or the fixed
                        # typed marker-side refusal (no raw state
                        # committed over marker bytes).
                        shadow, precheck_refusal = await prepare_replay_shadow(
                            established,
                            v1_runtime,
                            payload=payload,
                            endpoint=v1_endpoint,
                            observation=scoped_observation,
                            telemetry=v1_recorder,
                        )
                        if precheck_refusal is not None:
                            v1_refusals.labels(route.name, precheck_refusal.reason.value).inc()
                            return local_error(
                                precheck_refusal.status_code,
                                "governed v1 request refused",
                                precheck_refusal.code,
                            )
                        assert shadow is not None
                        proof, advance_refusal = advance_v1_session(
                            established,
                            v1_runtime,
                            payload=shadow,
                            endpoint=v1_endpoint,
                            observation=scoped_observation,
                            telemetry=v1_recorder,
                        )
                        if advance_refusal is not None:
                            v1_refusals.labels(route.name, advance_refusal.reason.value).inc()
                            return local_error(
                                advance_refusal.status_code,
                                "governed v1 request refused",
                                advance_refusal.code,
                            )
                        assert proof is not None
                        transaction = await prepare_v1_transaction(
                            established,
                            v1_runtime,
                            payload=payload,
                            endpoint=v1_endpoint,
                            observation=scoped_observation,
                            proof=proof,
                            telemetry=v1_recorder,
                        )
                        if isinstance(transaction, V1RequestRefusal):
                            v1_refusals.labels(route.name, transaction.reason.value).inc()
                            return local_error(
                                transaction.status_code,
                                "governed v1 request refused",
                                transaction.code,
                            )
                        # The single outgoing body of the one main
                        # upstream forward (the transformed payload on
                        # OK, the unchanged original payload on
                        # NO_REPLACEMENT).
                        body = transaction.body
                        # The post-forward trusted-issuance context of
                        # THIS committed request (022-c section 3):
                        # the actual direct main upstream response
                        # observed through it earns 018 issuances
                        # under the committed-state CAS (never
                        # compiler traffic; the frozen frontier is
                        # THIS request's actual represented
                        # completed-fact frontier, never the retained
                        # state as a whole, and never rebased).
                        v1_issuance = V1IssuanceContext(
                            session=established,
                            namespace=established.namespace,
                            state=proof.snapshot.state,
                            frontier=transaction.represented_frontier,
                            endpoint=v1_endpoint,
                        )
            observation: ObservationResult | None = None
            observation_sources: dict[tuple[str, str], bytes] = {}
            observation_dependencies: dict[str, bytes] = {}
            if route.observation_enabled and v1_runtime is None:
                # Legacy observation surface: inert under the v1
                # profile (v1 governed routes run the accepted 017
                # composition at their own slice; legacy labels must
                # not record v1 traffic).
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
                            request_identity=verified_identity,
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
        v1_main_send_started = V1StageRecorder.begin()
        try:
            upstream = await client.send(upstream_request, stream=True)
        except asyncio.CancelledError:
            if v1_issuance is not None:
                # Cancellation while waiting for headers: the ONE
                # main send was issued at the call boundary (the
                # actual forward fact, elapsed from the pre-send
                # timestamp) and the closed cancellation outcome
                # is kept distinct; the cancellation propagates
                # unchanged.
                assert v1_recorder is not None
                v1_main_forward.labels(route_name).inc()
                v1_recorder.record(V1Stage.MAIN_UPSTREAM, "forwarded", v1_main_send_started)
                v1_recorder.record(V1Stage.MAIN_UPSTREAM, "cancelled", V1StageRecorder.begin())
            raise
        except httpx.TimeoutException:
            upstream_failures.labels("timeout").inc()
            if v1_issuance is not None:
                # The ONE main send was issued at the call boundary
                # and then timed out: the actual forward fact
                # (elapsed from the pre-send timestamp) with the
                # closed transport outcome kept distinct.
                assert v1_recorder is not None
                v1_main_forward.labels(route_name).inc()
                v1_recorder.record(V1Stage.MAIN_UPSTREAM, "forwarded", v1_main_send_started)
                v1_recorder.record(V1Stage.MAIN_UPSTREAM, "timeout", V1StageRecorder.begin())
            return local_error(503, "upstream timed out", "upstream_timeout")
        except httpx.HTTPError:
            upstream_failures.labels("connection").inc()
            if v1_issuance is not None:
                assert v1_recorder is not None
                v1_main_forward.labels(route_name).inc()
                v1_recorder.record(V1Stage.MAIN_UPSTREAM, "forwarded", v1_main_send_started)
                v1_recorder.record(
                    V1Stage.MAIN_UPSTREAM, "connection_error", V1StageRecorder.begin()
                )
            return local_error(502, "upstream request failed", "upstream_error")
        if v1_issuance is not None:
            assert v1_recorder is not None
            # The ACTUAL main forward: the ONE send the adapter
            # issued at the call boundary (elapsed from the
            # pre-send timestamp to the provider's header answer),
            # distinct from the v1 preparation stages, which
            # already ran and are counted at their owning stages.
            v1_main_forward.labels(route_name).inc()
            v1_recorder.record(V1Stage.MAIN_UPSTREAM, "forwarded", v1_main_send_started)

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
            # Order 015-a (P01): bounded private cause classification before
            # the response is closed.  Status-derived categories need no
            # body; every other status reads at most the configured
            # diagnostic slice within the configured duration.  The read
            # always ends with the response closed and the same generic
            # public error returned below; provider text never crosses the
            # API boundary, logs, or metrics labels.
            if upstream.status_code in (401, 403, 429) or upstream.status_code >= 500:
                http_reason = classify_upstream_error(upstream.status_code, None)
            else:
                diagnostic = await _read_bounded_error_diagnostic(
                    upstream,
                    max_bytes=settings.upstream.upstream_error_diagnostic_max_bytes,
                    timeout_seconds=settings.upstream.upstream_error_diagnostic_timeout_seconds,
                )
                http_reason = classify_upstream_error(upstream.status_code, diagnostic)
            upstream_http_errors.labels(
                metric_endpoint,
                route_name,
                status_class(upstream.status_code),
                http_reason.value,
            ).inc()
            if v1_issuance is not None:
                # Provider acceptance is distinct from transport
                # errors: the provider answered and REFUSED.
                assert v1_recorder is not None
                v1_recorder.record(
                    V1Stage.MAIN_UPSTREAM, "provider_rejected", V1StageRecorder.begin()
                )
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

        if v1_issuance is not None and 200 <= upstream.status_code < 300:
            # The provider ACCEPTED the committed forward (an
            # actual 2xx header answer); a non-2xx response earns
            # no acceptance, and a later cancellation is a
            # distinct closed outcome of the same stage.
            assert v1_recorder is not None
            v1_recorder.record(V1Stage.MAIN_UPSTREAM, "provider_accepted", V1StageRecorder.begin())

        if stream:
            issuance = (
                v1_issuance
                if v1_issuance is not None and 200 <= upstream.status_code < 400
                else None
            )

            async def chunks() -> AsyncIterator[bytes]:
                try:
                    async for chunk in upstream.aiter_raw():
                        if issuance is not None:
                            issuance.observe_stream_chunk(chunk)
                        yield chunk
                except asyncio.CancelledError:
                    upstream_failures.labels("disconnect").inc()
                    if issuance is not None:
                        # The stream was cancelled mid-forward: the
                        # closed cancellation outcome (the provider
                        # acceptance above stays a distinct fact).
                        assert v1_recorder is not None
                        v1_recorder.record(
                            V1Stage.MAIN_UPSTREAM, "cancelled", V1StageRecorder.begin()
                        )
                    raise
                finally:
                    await upstream.aclose()
                    stream_duration.labels(endpoint, route_name, str(upstream.status_code)).observe(
                        time.monotonic() - started
                    )
                    if issuance is not None and issuance.usage_tokens is not None:
                        # The ACTUAL backend provider usage of the
                        # direct main response (the independent
                        # backend ledger, closed token counts only).
                        v1_provider_usage.labels(route_name, "input").inc(issuance.usage_tokens[0])
                        v1_provider_usage.labels(route_name, "output").inc(issuance.usage_tokens[1])

            return StreamingResponse(
                chunks(), status_code=upstream.status_code, headers=response_headers
            )
        try:
            if upstream.is_stream_consumed:
                content = upstream.content
                if len(content) > settings.server.response_body_max_bytes:
                    upstream_failures.labels("response_too_large").inc()
                    if v1_issuance is not None:
                        assert v1_recorder is not None
                        v1_recorder.record(
                            V1Stage.MAIN_UPSTREAM, "response_too_large", V1StageRecorder.begin()
                        )
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
                        if v1_issuance is not None:
                            assert v1_recorder is not None
                            v1_recorder.record(
                                V1Stage.MAIN_UPSTREAM,
                                "response_too_large",
                                V1StageRecorder.begin(),
                            )
                        return local_error(
                            502,
                            "upstream response exceeds configured limit",
                            "upstream_response_too_large",
                        )
                    response_chunks.append(chunk)
                content = b"".join(response_chunks)
        except httpx.HTTPError:
            upstream_failures.labels("response_read").inc()
            if v1_issuance is not None:
                assert v1_recorder is not None
                v1_recorder.record(
                    V1Stage.MAIN_UPSTREAM, "response_read_error", V1StageRecorder.begin()
                )
            return local_error(502, "upstream response failed", "upstream_error")
        finally:
            await upstream.aclose()
        if v1_issuance is not None and 200 <= upstream.status_code < 400:
            v1_issuance.observe_nonstream(content)
            if v1_issuance.usage_tokens is not None:
                # The ACTUAL backend provider usage of the direct
                # main response (the independent backend ledger,
                # closed token counts only).
                v1_provider_usage.labels(route_name, "input").inc(v1_issuance.usage_tokens[0])
                v1_provider_usage.labels(route_name, "output").inc(v1_issuance.usage_tokens[1])
        return Response(content, status_code=upstream.status_code, headers=response_headers)

    return app

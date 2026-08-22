"""Explicit one-root constitutional request pipeline."""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass
from typing import Any, NoReturn

import httpx
from prometheus_client import CollectorRegistry, Counter, Histogram

from ..config import ConstitutionIntegrationConfig, RouteConfig
from .cache import CacheIdentity, CachePolicy, DerivedIndexCache
from .compiler import CompilerSettings, ConstitutionalCompiler, ObservedSourceMetadata
from .injection import (
    ConstitutionInjectionError,
    inject_chat_completions,
    inject_responses,
)
from .models import ObservationResult
from .working_set import (
    WorkingSetMetadata,
    WorkingSetPolicy,
    WorkingSetSelectionError,
    select_working_set,
)


@dataclass(frozen=True)
class PipelineResult:
    """A transformed request or an explicit safe preservation decision."""

    payload: dict[str, Any]
    body: bytes
    injected: bool
    state: str
    reason: str


class ConstitutionInjectionRejected(Exception):
    """Fail-closed injection rejection carrying only a fixed safe reason."""

    def __init__(self, reason: str) -> None:
        super().__init__(reason)
        self.reason = reason


class ConstitutionPipeline:
    """Owns optional direct compiler/cache/selection/injection execution."""

    def __init__(
        self,
        *,
        constitution: ConstitutionIntegrationConfig,
        compiler: CompilerSettings,
        cache_policy: CachePolicy,
        registry: CollectorRegistry,
        client: httpx.AsyncClient,
    ) -> None:
        self.constitution = constitution
        self.cache = DerivedIndexCache(cache_policy, registry=registry)
        self.compiler = ConstitutionalCompiler(
            compiler, cache=self.cache, registry=registry, client=client
        )
        self.requests = Counter(
            "slaif_constitution_pipeline_requests_total",
            "Constitutional pipeline outcomes by fixed safe state and reason",
            ["endpoint", "route", "state", "reason"],
            registry=registry,
        )
        self.selection_failures = Counter(
            "slaif_constitution_selection_failures_total",
            "Typed working-set selection failures by fixed reason",
            ["endpoint", "route", "reason"],
            registry=registry,
        )
        self.injection_outcomes = Counter(
            "slaif_constitution_injection_total",
            "Endpoint-specific injection outcomes by fixed result",
            ["endpoint", "route", "outcome"],
            registry=registry,
        )
        self.injection_failures = Counter(
            "slaif_constitution_injection_failures_total",
            "Fail-closed injection rejections by fixed reason",
            ["endpoint", "route", "reason"],
            registry=registry,
        )
        self.duration = Histogram(
            "slaif_constitution_pipeline_duration_seconds",
            "Enabled pipeline duration through serialization or rejection",
            ["endpoint", "route", "state"],
            registry=registry,
        )

    async def aclose(self) -> None:
        await self.compiler.aclose()

    def _identity(self, route_name: str) -> CacheIdentity:
        # Settings validation guarantees these opaque static appliance labels.
        assert self.constitution.principal is not None
        assert self.constitution.session is not None
        assert self.constitution.repository is not None
        return CacheIdentity(
            principal=self.constitution.principal,
            route=route_name,
            session=self.constitution.session,
            repository=self.constitution.repository,
        )

    def _preserve(
        self,
        payload: dict[str, Any],
        body: bytes,
        *,
        endpoint: str,
        route_name: str,
        reason: str,
    ) -> PipelineResult:
        return PipelineResult(
            payload=payload, body=body, injected=False, state="degraded", reason=reason
        )

    def _reject(self, *, endpoint: str, route_name: str, reason: str) -> NoReturn:
        self.requests.labels(endpoint, route_name, "rejected", reason).inc()
        self.duration.labels(endpoint, route_name, "rejected").observe(0.0)
        raise ConstitutionInjectionRejected(reason)

    def preserve_unobserved(
        self,
        *,
        payload: dict[str, Any],
        body: bytes,
        endpoint: str,
        route_name: str,
    ) -> PipelineResult:
        """Record an enabled request skipped because deterministic observation failed."""
        self.requests.labels(endpoint, route_name, "skipped", "observation_failed").inc()
        self.duration.labels(endpoint, route_name, "skipped").observe(0.0)
        return PipelineResult(
            payload=payload,
            body=body,
            injected=False,
            state="skipped",
            reason="observation_failed",
        )

    async def process(
        self,
        *,
        payload: dict[str, Any],
        observation: ObservationResult,
        source_bytes_by_root: dict[tuple[str, str], bytes],
        route: RouteConfig,
        endpoint: str,
        post_image_body: bytes,
    ) -> PipelineResult:
        """Compile/cache/select/inject exactly one complete observed source."""
        started = time.monotonic()
        route_name = route.name
        roots = observation.roots

        def complete(state: str, reason: str, result: PipelineResult) -> PipelineResult:
            self.requests.labels(endpoint, route_name, state, reason).inc()
            self.duration.labels(endpoint, route_name, state).observe(time.monotonic() - started)
            return result

        if len(roots) != 1 or not roots[0].complete:
            reason = "ambiguous_root" if len(roots) != 1 else "incomplete_root"
            preserved = self._preserve(
                payload,
                post_image_body,
                endpoint=endpoint,
                route_name=route_name,
                reason=reason,
            )
            return complete("skipped", reason, preserved)

        root = roots[0]
        key = (root.logical_path, root.content_sha256)
        source = source_bytes_by_root.get(key)
        if (
            source is None
            or len(source) != root.byte_length
            or hashlib.sha256(source).hexdigest() != root.content_sha256
        ):
            preserved = self._preserve(
                payload,
                post_image_body,
                endpoint=endpoint,
                route_name=route_name,
                reason="source_unavailable",
            )
            return complete("skipped", "source_unavailable", preserved)

        identity = self._identity(route_name)
        compiled = await self.compiler.compile(
            source,
            root.logical_path,
            ObservedSourceMetadata(
                logical_path=root.logical_path,
                content_sha256=root.content_sha256,
                byte_length=root.byte_length,
            ),
            root.candidates,
            identity,
        )
        index = compiled.index
        if compiled.failure is not None or index is None:
            reason = compiled.failure.reason.value if compiled.failure else "invalid_input"
            preserved = self._preserve(
                payload,
                post_image_body,
                endpoint=endpoint,
                route_name=route_name,
                reason=f"compiler_{reason}",
            )
            return complete("degraded", f"compiler_{reason}", preserved)

        working_set_policy = WorkingSetPolicy(
            max_rendered_bytes=self.constitution.max_injected_bytes,
            max_dependencies=self.constitution.candidate_max_count,
            max_entries=self.constitution.working_set_max_entries,
            max_acquisition_instructions=self.constitution.acquisition_max_count,
            max_entry_bytes=self.constitution.entry_render_max_bytes,
        )
        try:
            working_set = select_working_set(
                index,
                {},
                policy=working_set_policy,
                metadata=WorkingSetMetadata(
                    policy_version=self.constitution.working_set_policy_version
                ),
            )
        except WorkingSetSelectionError as exc:
            reason = exc.failure.reason.value
            self.selection_failures.labels(endpoint, route_name, reason).inc()
            preserved = self._preserve(
                payload,
                post_image_body,
                endpoint=endpoint,
                route_name=route_name,
                reason=f"selection_{reason}",
            )
            return complete("degraded", f"selection_{reason}", preserved)

        try:
            if endpoint == "/v1/responses":
                transformed, injection = inject_responses(
                    payload,
                    working_set,
                    max_depth=self.constitution.injection_max_depth,
                    max_nodes=self.constitution.injection_max_nodes,
                )
            elif endpoint == "/v1/chat/completions":
                transformed, injection = inject_chat_completions(
                    payload,
                    working_set,
                    max_depth=self.constitution.injection_max_depth,
                    max_nodes=self.constitution.injection_max_nodes,
                )
            else:
                self._reject(endpoint=endpoint, route_name=route_name, reason="unsupported_shape")
        except ConstitutionInjectionError as exc:
            reason = exc.reason.value
            self.injection_failures.labels(endpoint, route_name, reason).inc()
            self.requests.labels(endpoint, route_name, "rejected", f"injection_{reason}").inc()
            self.duration.labels(endpoint, route_name, "rejected").observe(
                time.monotonic() - started
            )
            raise ConstitutionInjectionRejected(reason) from None

        body = json.dumps(transformed, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
        self.injection_outcomes.labels(endpoint, route_name, injection.outcome.value).inc()
        return complete(
            "injected",
            injection.outcome.value,
            PipelineResult(
                payload=transformed,
                body=body,
                injected=True,
                state="injected",
                reason=injection.outcome.value,
            ),
        )

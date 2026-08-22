"""Explicit one-root constitutional request pipeline with process-local rehydration."""

from __future__ import annotations

import hashlib
import json
import math
import threading
import time
from collections import OrderedDict
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, NoReturn

import httpx
from prometheus_client import CollectorRegistry, Counter, Gauge, Histogram
from pydantic import BaseModel, ConfigDict, Field

from ..config import ConstitutionIntegrationConfig, ObservationPolicy, RouteConfig
from .cache import CacheIdentity, CachePolicy, DerivedIndexCache
from .compiler import CompilerSettings, ConstitutionalCompiler, ObservedSourceMetadata
from .compiler_models import (
    COMPILER_VERSION,
    INDEX_SCHEMA_VERSION,
    PROMPT_POLICY_VERSION,
    CompiledIndex,
)
from .injection import (
    ConstitutionInjectionError,
    InjectionResult,
    inject_chat_completions,
    inject_responses,
)
from .models import ConstitutionSourceObservation, ObservationResult
from .references import extract_references
from .working_set import (
    WorkingSetMetadata,
    WorkingSetPolicy,
    WorkingSetSelectionError,
    WorkingSetSuccess,
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


class RehydrationKey(BaseModel):
    """Complete static identity for one process-local rehydration entry."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    principal: str = Field(min_length=1, max_length=256)
    route: str = Field(min_length=1, max_length=64)
    session: str = Field(min_length=1, max_length=256)
    repository: str = Field(min_length=1, max_length=256)
    model: str = Field(min_length=1, max_length=128)
    root_logical_path: str = Field(min_length=1, max_length=512)
    root_source_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    index_schema_version: str = Field(min_length=1, max_length=64)
    compiler_version: str = Field(min_length=1, max_length=64)
    prompt_policy_version: str = Field(min_length=1, max_length=64)
    reasoning_effort: str = Field(min_length=1, max_length=64)
    max_source_bytes: int = Field(gt=0)
    max_prompt_bytes: int = Field(gt=0)
    max_output_tokens: int = Field(gt=0)
    max_output_bytes: int = Field(gt=0)
    max_candidates: int = Field(ge=0)
    max_json_depth: int = Field(gt=0)
    observation_schema_version: str = Field(min_length=1, max_length=64)
    observation_policy_version: str = Field(min_length=1, max_length=64)
    observation_max_source_bytes: int = Field(gt=0)
    observation_max_candidates: int = Field(gt=0)
    observation_max_evidence_per_candidate: int = Field(gt=0)
    observation_max_total_evidence: int = Field(gt=0)
    observation_max_path_bytes: int = Field(gt=0)
    selector_schema_version: str = Field(min_length=1, max_length=64)
    render_version: str = Field(min_length=1, max_length=64)
    working_set_policy_version: str = Field(min_length=1, max_length=64)
    max_injected_bytes: int = Field(gt=0)
    candidate_max_count: int = Field(gt=0)
    working_set_max_entries: int = Field(gt=0)
    acquisition_max_count: int = Field(gt=0)
    max_dependency_acquisitions: int = Field(gt=0)
    entry_render_max_bytes: int = Field(gt=0)
    injection_max_depth: int = Field(gt=0)
    injection_max_nodes: int = Field(gt=0)


@dataclass(frozen=True)
class _RehydrationEntry:
    created_at: float
    bytes: int
    root: CompiledIndex
    dependencies: Mapping[str, CompiledIndex]
    inclusion_metadata: WorkingSetSuccess


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
        self.compiler_settings = compiler
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
        self.dependency_outcomes = Counter(
            "slaif_constitution_dependency_acquisitions_total",
            "Bounded request-derived dependency acquisition outcomes",
            ["endpoint", "route", "outcome"],
            registry=registry,
        )
        self.selection_inclusions = Counter(
            "slaif_constitution_dependency_selection_inclusions_total",
            "Validated dependencies included in rendered working sets",
            ["endpoint", "route"],
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
        self.rehydration_outcomes = Counter(
            "slaif_constitution_rehydration_total",
            "Process-local rehydration outcomes by fixed state and reason",
            ["endpoint", "route", "state", "reason"],
            registry=registry,
        )
        self.rehydration_entries = Gauge(
            "slaif_constitution_rehydration_entries",
            "Current process-local rehydration entries",
            registry=registry,
        )
        self.rehydration_bytes = Gauge(
            "slaif_constitution_rehydration_bytes",
            "Current process-local rehydration occupancy",
            registry=registry,
        )
        self.duration = Histogram(
            "slaif_constitution_pipeline_duration_seconds",
            "Enabled pipeline duration through serialization or rejection",
            ["endpoint", "route", "state"],
            registry=registry,
        )
        self._rehydration: OrderedDict[RehydrationKey, _RehydrationEntry] = OrderedDict()
        self._rehydration_bytes = 0
        self._rehydration_lock = threading.RLock()

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

    def _rehydration_identity(
        self,
        *,
        route_name: str,
        model: str,
        logical_path: str,
        source_sha256: str,
        observation_policy: ObservationPolicy,
    ) -> RehydrationKey:
        assert self.constitution.principal is not None
        assert self.constitution.session is not None
        assert self.constitution.repository is not None
        return RehydrationKey(
            principal=self.constitution.principal,
            route=route_name,
            session=self.constitution.session,
            repository=self.constitution.repository,
            model=model,
            root_logical_path=logical_path,
            root_source_sha256=source_sha256,
            index_schema_version=INDEX_SCHEMA_VERSION,
            compiler_version=COMPILER_VERSION,
            prompt_policy_version=PROMPT_POLICY_VERSION,
            reasoning_effort=self.compiler_settings.reasoning_effort,
            max_source_bytes=self.compiler_settings.max_source_bytes,
            max_prompt_bytes=self.compiler_settings.max_prompt_bytes,
            max_output_tokens=self.compiler_settings.max_output_tokens,
            max_output_bytes=self.compiler_settings.max_output_bytes,
            max_candidates=self.compiler_settings.max_candidates,
            max_json_depth=self.compiler_settings.max_json_depth,
            observation_schema_version=observation_policy.schema_version,
            observation_policy_version=observation_policy.policy_version,
            observation_max_source_bytes=observation_policy.max_source_bytes,
            observation_max_candidates=observation_policy.max_candidates,
            observation_max_evidence_per_candidate=observation_policy.max_evidence_per_candidate,
            observation_max_total_evidence=observation_policy.max_total_evidence,
            observation_max_path_bytes=observation_policy.max_path_bytes,
            selector_schema_version=self.constitution.selector_schema_version,
            render_version=self.constitution.render_version,
            working_set_policy_version=self.constitution.working_set_policy_version,
            max_injected_bytes=self.constitution.max_injected_bytes,
            candidate_max_count=self.constitution.candidate_max_count,
            working_set_max_entries=self.constitution.working_set_max_entries,
            acquisition_max_count=self.constitution.acquisition_max_count,
            max_dependency_acquisitions=self.constitution.max_dependency_acquisitions,
            entry_render_max_bytes=self.constitution.entry_render_max_bytes,
            injection_max_depth=self.constitution.injection_max_depth,
            injection_max_nodes=self.constitution.injection_max_nodes,
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

    def _rehydration_metric(
        self, *, endpoint: str, route_name: str, state: str, reason: str
    ) -> None:
        self.rehydration_outcomes.labels(endpoint, route_name, state, reason).inc()

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
        self._rehydration_metric(
            endpoint=endpoint,
            route_name=route_name,
            state="skipped",
            reason="observation_failed",
        )
        return PipelineResult(
            payload=payload,
            body=body,
            injected=False,
            state="skipped",
            reason="observation_failed",
        )

    async def _compile_dependencies(
        self,
        *,
        root_index: CompiledIndex,
        source_bytes_by_dependency: dict[str, bytes],
        observation_policy: ObservationPolicy,
        identity: CacheIdentity,
        endpoint: str,
        route_name: str,
    ) -> dict[str, CompiledIndex]:
        """Compile at most the configured number of uniquely observed dependencies."""
        declarations = {item.path: item for item in root_index.dependencies}
        acquired: dict[str, CompiledIndex] = {}
        budget = self.constitution.max_dependency_acquisitions
        for declaration in root_index.dependencies:
            path = declaration.path
            if path not in source_bytes_by_dependency:
                continue
            if len(acquired) >= budget:
                self.dependency_outcomes.labels(endpoint, route_name, "budget_exceeded").inc()
                continue
            source = source_bytes_by_dependency[path]
            digest = hashlib.sha256(source).hexdigest()
            try:
                extraction = extract_references(source.decode("utf-8"), observation_policy)
            except (UnicodeError, RecursionError):
                self.dependency_outcomes.labels(endpoint, route_name, "invalid").inc()
                continue

            def invalidate() -> None:
                self.dependency_outcomes.labels(endpoint, route_name, "invalid").inc()

            compiled = await self.compiler.compile(
                source,
                path,
                ObservedSourceMetadata(
                    logical_path=path,
                    content_sha256=digest,
                    byte_length=len(source),
                ),
                extraction.candidates,
                identity,
            )
            index = compiled.index
            if (
                compiled.failure is not None
                or index is None
                or index.source_logical_path != path
                or index.source_sha256 != digest
                or index.source_byte_length != len(source)
                or [item.path for item in index.dependencies]
                != [item.path for item in extraction.candidates]
            ):
                invalidate()
                continue
            acquired[path] = index
            outcome = "cache_hit" if compiled.cache_outcome == "hit" else "cache_miss"
            self.dependency_outcomes.labels(endpoint, route_name, outcome).inc()
        # Unknown/mismatched observation keys are rejected without exposing their values.
        for path in source_bytes_by_dependency:
            if path not in declarations:
                self.dependency_outcomes.labels(endpoint, route_name, "invalid").inc()
        return acquired

    @staticmethod
    def _entry_bytes(
        root: CompiledIndex,
        dependencies: Mapping[str, CompiledIndex],
        metadata: WorkingSetSuccess,
    ) -> int:
        value = {
            "dependencies": [
                [path, dependencies[path].model_dump(mode="json")] for path in sorted(dependencies)
            ],
            "inclusion_metadata": metadata.model_dump(mode="json"),
            "root": root.model_dump(mode="json"),
        }
        return len(
            json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode(
                "utf-8"
            )
        )

    def _valid_rehydration_entry(
        self, key: RehydrationKey, endpoint: str, route_name: str
    ) -> _RehydrationEntry | None:
        policy = self.constitution.rehydration

        def discard(state: str, reason: str) -> None:
            entry = self._rehydration.pop(key, None)
            if (
                isinstance(entry, _RehydrationEntry)
                and isinstance(entry.bytes, int)
                and not isinstance(entry.bytes, bool)
            ):
                self._rehydration_bytes -= entry.bytes
            self._sync_rehydration_occupancy()
            self._rehydration_metric(
                endpoint=endpoint, route_name=route_name, state=state, reason=reason
            )

        with self._rehydration_lock:
            entry = self._rehydration.get(key)
            if entry is None:
                self._rehydration_metric(
                    endpoint=endpoint,
                    route_name=route_name,
                    state="isolated_miss",
                    reason="entry_absent",
                )
                return None
            structurally_valid = (
                isinstance(entry, _RehydrationEntry)
                and isinstance(entry.created_at, (int, float))
                and not isinstance(entry.created_at, bool)
                and math.isfinite(entry.created_at)
                and isinstance(entry.root, CompiledIndex)
                and isinstance(entry.inclusion_metadata, WorkingSetSuccess)
                and isinstance(entry.dependencies, dict)
                and all(
                    isinstance(path, str) and isinstance(index, CompiledIndex)
                    for path, index in entry.dependencies.items()
                )
                and isinstance(entry.bytes, int)
                and not isinstance(entry.bytes, bool)
                and 0 < entry.bytes <= policy.max_entry_bytes
            )
            consistent = False
            if structurally_valid:
                root = entry.root
                metadata = entry.inclusion_metadata
                declarations = {item.path for item in root.dependencies}
                consistent = (
                    root.schema_version == key.index_schema_version
                    and root.compiler_version == key.compiler_version
                    and root.prompt_policy_version == key.prompt_policy_version
                    and root.model == key.model
                    and root.source_logical_path == key.root_logical_path
                    and root.source_sha256 == key.root_source_sha256
                    and set(entry.dependencies) <= declarations
                    and all(
                        index.schema_version == key.index_schema_version
                        and index.compiler_version == key.compiler_version
                        and index.prompt_policy_version == key.prompt_policy_version
                        and index.model == key.model
                        and index.source_logical_path == path
                        for path, index in entry.dependencies.items()
                    )
                    and metadata.schema_version == key.selector_schema_version
                    and metadata.render_version == key.render_version
                    and metadata.policy_version == key.working_set_policy_version
                    and metadata.root_logical_path == key.root_logical_path
                    and metadata.root_source_sha256 == key.root_source_sha256
                    and metadata.root_index_version == key.index_schema_version
                )
            invalid = (
                not structurally_valid
                or not consistent
                or entry.bytes
                != self._entry_bytes(
                    entry.root,
                    entry.dependencies,
                    entry.inclusion_metadata,
                )
            )
            if invalid:
                discard("failure", "corrupt_or_oversized")
                return None
            if time.monotonic() - entry.created_at > policy.ttl_seconds:
                discard("stale_expired", "ttl_expired")
                return None
            self._rehydration.move_to_end(key)
            return entry

    def _sync_rehydration_occupancy(self) -> None:
        self.rehydration_entries.set(len(self._rehydration))
        self.rehydration_bytes.set(self._rehydration_bytes)

    def _matching_rehydration_key(
        self,
        *,
        route_name: str,
        model: str,
        observation_policy: ObservationPolicy,
    ) -> RehydrationKey | None:
        probe = self._rehydration_identity(
            route_name=route_name,
            model=model,
            logical_path="AGENTS.md",
            source_sha256="0" * 64,
            observation_policy=observation_policy,
        )
        excluded = {"root_logical_path", "root_source_sha256"}
        expected = probe.model_dump(exclude=excluded)
        with self._rehydration_lock:
            for key in reversed(self._rehydration):
                if key.model_dump(exclude=excluded) == expected:
                    return key
        return None

    def _store_rehydration(
        self,
        *,
        key: RehydrationKey,
        root: CompiledIndex,
        dependencies: Mapping[str, CompiledIndex],
        metadata: WorkingSetSuccess,
        endpoint: str,
        route_name: str,
    ) -> None:
        """Store only after successful validated injection; failure preserves the result."""
        policy = self.constitution.rehydration
        previous: _RehydrationEntry | None = None
        try:
            size = self._entry_bytes(root, dependencies, metadata)
            if size > policy.max_entry_bytes:
                raise ValueError("entry too large")
            entry = _RehydrationEntry(
                created_at=time.monotonic(),
                bytes=size,
                root=root,
                dependencies=dict(dependencies),
                inclusion_metadata=metadata,
            )
            with self._rehydration_lock:
                previous = self._rehydration.pop(key, None)
                if previous is not None:
                    self._rehydration_bytes -= previous.bytes
                while self._rehydration and (
                    len(self._rehydration) + 1 > policy.max_entries
                    or self._rehydration_bytes + size > policy.max_total_bytes
                ):
                    _, evicted = self._rehydration.popitem(last=False)
                    self._rehydration_bytes -= evicted.bytes
                if size > policy.max_total_bytes:
                    raise ValueError("entry exceeds total budget")
                self._rehydration[key] = entry
                self._rehydration_bytes += size
                self._sync_rehydration_occupancy()
            self._rehydration_metric(
                endpoint=endpoint, route_name=route_name, state="populated", reason="injected"
            )
        except (TypeError, ValueError):
            with self._rehydration_lock:
                # A failed replacement restores the prior valid entry when possible.
                if key not in self._rehydration and previous is not None:
                    self._rehydration[key] = previous
                    self._rehydration_bytes += previous.bytes
                    self._sync_rehydration_occupancy()
            self._rehydration_metric(
                endpoint=endpoint,
                route_name=route_name,
                state="failure",
                reason="store_bounds",
            )

    def _select_and_inject(
        self,
        *,
        payload: dict[str, Any],
        root: CompiledIndex,
        dependencies: Mapping[str, CompiledIndex],
        endpoint: str,
        route_name: str,
    ) -> tuple[dict[str, Any], WorkingSetSuccess, InjectionResult]:
        working_set_policy = WorkingSetPolicy(
            max_rendered_bytes=self.constitution.max_injected_bytes,
            max_dependencies=self.constitution.candidate_max_count,
            max_entries=self.constitution.working_set_max_entries,
            max_acquisition_instructions=self.constitution.acquisition_max_count,
            max_entry_bytes=self.constitution.entry_render_max_bytes,
        )
        working_set = select_working_set(
            root,
            dependencies,
            policy=working_set_policy,
            metadata=WorkingSetMetadata(
                policy_version=self.constitution.working_set_policy_version
            ),
        )
        self.selection_inclusions.labels(endpoint, route_name).inc(
            sum(item.status.value == "included" for item in working_set.dependencies)
        )
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
        self.injection_outcomes.labels(endpoint, route_name, injection.outcome.value).inc()
        return transformed, working_set, injection

    def _injection_failure(
        self, exc: ConstitutionInjectionError, *, endpoint: str, route_name: str
    ) -> NoReturn:
        reason = exc.reason.value
        self.injection_failures.labels(endpoint, route_name, reason).inc()
        self.requests.labels(endpoint, route_name, "rejected", f"injection_{reason}").inc()
        raise ConstitutionInjectionRejected(reason) from None

    async def process(
        self,
        *,
        payload: dict[str, Any],
        observation: ObservationResult,
        source_bytes_by_root: dict[tuple[str, str], bytes],
        source_bytes_by_dependency: dict[str, bytes],
        observation_policy: ObservationPolicy,
        route: RouteConfig,
        endpoint: str,
        post_image_body: bytes,
        model: str,
    ) -> PipelineResult:
        """Compile/cache/select/inject one root or rehydrate the last valid set."""
        started = time.monotonic()
        route_name = route.name
        roots = observation.roots

        def complete(state: str, reason: str, result: PipelineResult) -> PipelineResult:
            self.requests.labels(endpoint, route_name, state, reason).inc()
            self.duration.labels(endpoint, route_name, state).observe(time.monotonic() - started)
            return result

        if len(roots) == 1 and roots[0].complete:
            return await self._process_observed_root(
                payload=payload,
                root=roots[0],
                source_bytes_by_root=source_bytes_by_root,
                source_bytes_by_dependency=source_bytes_by_dependency,
                observation_policy=observation_policy,
                route=route,
                endpoint=endpoint,
                post_image_body=post_image_body,
                model=model,
                started=started,
            )

        if len(roots) == 0:
            # A zero-root request is the simulated/new-context rehydration boundary.
            key = self._matching_rehydration_key(
                route_name=route_name,
                model=model,
                observation_policy=observation_policy,
            )
            if key is None:
                preserved = self._preserve(
                    payload,
                    post_image_body,
                    endpoint=endpoint,
                    route_name=route_name,
                    reason="rehydration_unavailable",
                )
                self._rehydration_metric(
                    endpoint=endpoint,
                    route_name=route_name,
                    state="isolated_miss",
                    reason="identity_isolated",
                )
                return complete("skipped", "rehydration_unavailable", preserved)
            entry = (
                None if key is None else self._valid_rehydration_entry(key, endpoint, route_name)
            )
            if entry is None:
                preserved = self._preserve(
                    payload,
                    post_image_body,
                    endpoint=endpoint,
                    route_name=route_name,
                    reason="rehydration_unavailable",
                )
                return complete("skipped", "rehydration_unavailable", preserved)
            try:
                transformed, working_set, injection = self._select_and_inject(
                    payload=payload,
                    root=entry.root,
                    dependencies=entry.dependencies,
                    endpoint=endpoint,
                    route_name=route_name,
                )
            except WorkingSetSelectionError as exc:
                reason = exc.failure.reason.value
                self.selection_failures.labels(endpoint, route_name, reason).inc()
                self._rehydration_metric(
                    endpoint=endpoint,
                    route_name=route_name,
                    state="failure",
                    reason=f"selection_{reason}",
                )
                preserved = self._preserve(
                    payload,
                    post_image_body,
                    endpoint=endpoint,
                    route_name=route_name,
                    reason=f"selection_{reason}",
                )
                return complete("degraded", f"selection_{reason}", preserved)
            except ConstitutionInjectionError as exc:
                self._rehydration_metric(
                    endpoint=endpoint,
                    route_name=route_name,
                    state="failure",
                    reason=f"injection_{exc.reason.value}",
                )
                self._injection_failure(exc, endpoint=endpoint, route_name=route_name)
            body = json.dumps(transformed, separators=(",", ":"), ensure_ascii=False).encode(
                "utf-8"
            )
            self._rehydration_metric(
                endpoint=endpoint, route_name=route_name, state="hit", reason="zero_root"
            )
            self._rehydration_metric(
                endpoint=endpoint, route_name=route_name, state="injected", reason="rehydrated"
            )
            return complete(
                "injected",
                f"rehydration_{injection.outcome.value}",
                PipelineResult(
                    payload=transformed,
                    body=body,
                    injected=True,
                    state="injected",
                    reason=f"rehydration_{injection.outcome.value}",
                ),
            )

        reason = "ambiguous_root" if len(roots) > 1 else "incomplete_root"
        preserved = self._preserve(
            payload,
            post_image_body,
            endpoint=endpoint,
            route_name=route_name,
            reason=reason,
        )
        return complete("skipped", reason, preserved)

    async def _process_observed_root(
        self,
        *,
        payload: dict[str, Any],
        root: ConstitutionSourceObservation,
        source_bytes_by_root: dict[tuple[str, str], bytes],
        source_bytes_by_dependency: dict[str, bytes],
        observation_policy: ObservationPolicy,
        route: RouteConfig,
        endpoint: str,
        post_image_body: bytes,
        model: str,
        started: float,
    ) -> PipelineResult:
        route_name = route.name

        def complete(state: str, reason: str, result: PipelineResult) -> PipelineResult:
            self.requests.labels(endpoint, route_name, state, reason).inc()
            self.duration.labels(endpoint, route_name, state).observe(time.monotonic() - started)
            return result

        key_pair = (root.logical_path, root.content_sha256)
        source = source_bytes_by_root.get(key_pair)
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

        acquired_dependencies = await self._compile_dependencies(
            root_index=index,
            source_bytes_by_dependency=source_bytes_by_dependency,
            observation_policy=observation_policy,
            identity=identity,
            endpoint=endpoint,
            route_name=route_name,
        )
        try:
            transformed, working_set, injection = self._select_and_inject(
                payload=payload,
                root=index,
                dependencies=acquired_dependencies,
                endpoint=endpoint,
                route_name=route_name,
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
        except ConstitutionInjectionError as exc:
            self._injection_failure(exc, endpoint=endpoint, route_name=route_name)

        body = json.dumps(transformed, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
        self._store_rehydration(
            key=self._rehydration_identity(
                route_name=route_name,
                model=model,
                logical_path=index.source_logical_path,
                source_sha256=index.source_sha256,
                observation_policy=observation_policy,
            ),
            root=index,
            dependencies=acquired_dependencies,
            metadata=working_set,
            endpoint=endpoint,
            route_name=route_name,
        )
        self._rehydration_metric(
            endpoint=endpoint, route_name=route_name, state="injected", reason="observed_root"
        )
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

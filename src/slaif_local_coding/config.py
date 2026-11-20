"""Validated, deterministic adapter configuration."""

from __future__ import annotations

import ipaddress
import os
import tomllib
from pathlib import Path
from typing import Any, Literal
from urllib.parse import urlsplit

from pydantic import BaseModel, ConfigDict, Field, model_validator

from .constitution.bundles.bundle_budget import (
    BUDGET_CONTEXT_MAX,
    BUDGET_CONTEXT_MIN,
    BundleBudgetConfig,
)
from .constitution.bundles.bundle_compiler import BundleCompilerConfig
from .constitution.bundles.bundle_tokenizer import (
    BUNDLE_TOKENIZER_RENDER_POLICY_VERSION,
    PINNED_TOKENIZER_REVISION,
    PINNED_TOKENIZER_UPSTREAM,
)
from .constitution.bundles.ram_state_models import RamStateBounds

MAX_SERVICE_TOKEN_BYTES = 4096
MIN_SIGNING_SECRET_BYTES = 32
MAX_SIGNING_SECRET_BYTES = 4096
SIGNED_IDENTITY_VERSION = "v1"
SIGNED_IDENTITY_POLICY_VERSION = "signed-identity-v1"


def validate_service_token(value: str) -> str:
    """Validate one configured or supplied service Bearer token."""
    if not isinstance(value, str) or not value:
        raise ValueError("service credential is invalid")
    try:
        encoded = value.encode("utf-8")
    except UnicodeEncodeError as exc:
        raise ValueError("service credential is invalid") from exc
    if len(encoded) > MAX_SERVICE_TOKEN_BYTES or any(not 0x21 <= byte <= 0x7E for byte in encoded):
        raise ValueError("service credential is invalid")
    return value


def validate_signing_secret(value: str) -> bytes:
    """Validate the selected visible-ASCII HMAC secret encoding."""
    if not isinstance(value, str):
        raise ValueError("gateway signing secret is invalid")
    try:
        encoded = value.encode("ascii")
    except UnicodeEncodeError as exc:
        raise ValueError("gateway signing secret is invalid") from exc
    if not MIN_SIGNING_SECRET_BYTES <= len(encoded) <= MAX_SIGNING_SECRET_BYTES:
        raise ValueError("gateway signing secret is invalid")
    if any(not 0x21 <= byte <= 0x7E for byte in encoded):
        raise ValueError("gateway signing secret is invalid")
    return encoded


# Objective-011 binding law (strategic decision D1, human-mandated): the
# always-accepted loopback literals, the all-interfaces literals, and bare
# IPv4/IPv6 literals are the only syntactically valid bind addresses. A
# non-loopback bind is additionally permitted only under the full accepted
# signed ingress contract (enforced by the Settings-level cross-validator
# ``binding_law``); loopback remains the default and the only permitted bind
# when ingress is disabled or static.
LOOPBACK_BIND_LITERALS: frozenset[str] = frozenset({"127.0.0.1", "::1", "localhost"})
ALL_INTERFACES_BIND_LITERALS: frozenset[str] = frozenset({"0.0.0.0", "::"})


def is_loopback_bind_literal(value: str) -> bool:
    """True for the always-accepted loopback bind literals (D1)."""
    return value in LOOPBACK_BIND_LITERALS


class ServerConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")
    listen_host: str = "127.0.0.1"
    listen_port: int = Field(default=18031, ge=1, le=65535)
    request_body_max_bytes: int = Field(default=67_108_864, gt=0, le=268_435_456)
    response_body_max_bytes: int = Field(default=67_108_864, gt=0, le=268_435_456)
    json_max_nesting_depth: int = Field(default=128, ge=1, le=256)

    @model_validator(mode="after")
    def validated_bind_host(self) -> ServerConfig:
        # Syntactic law (D1): loopback literals always; bare IPv4/IPv6
        # literals and the all-interfaces literals only (cross-mode law is
        # enforced at the Settings level by ``binding_law``). Hostnames,
        # schemes, ports, and malformed values are rejected here.
        value = self.listen_host
        if value in LOOPBACK_BIND_LITERALS or value in ALL_INTERFACES_BIND_LITERALS:
            return self
        try:
            ipaddress.ip_address(value)
        except ValueError:
            raise ValueError(
                "listen_host must be a loopback literal, a bare IPv4/IPv6 "
                "literal, or the all-interfaces literal"
            ) from None
        return self


class GatewayIngressConfig(BaseModel):
    """Optional private gateway-to-adapter authentication boundary."""

    model_config = ConfigDict(extra="forbid")
    mode: Literal[
        "disabled",
        "service_bearer_static_identity",
        "service_bearer_signed_identity_v1",
    ] = "disabled"
    service_token_env: str | None = Field(
        default=None,
        max_length=256,
        pattern=r"^[A-Za-z_][A-Za-z0-9_]*$",
    )
    signing_secret_env: str | None = Field(
        default=None,
        max_length=256,
        pattern=r"^[A-Za-z_][A-Za-z0-9_]*$",
    )
    identity_version: Literal["v1"] = "v1"
    policy_version: Literal["signed-identity-v1"] = "signed-identity-v1"
    clock_skew_seconds: int = Field(default=60, strict=True, ge=1, le=300)
    replay_ttl_seconds: int = Field(default=60, strict=True, ge=1, le=86_400)
    max_replay_entries: int = Field(default=4096, strict=True, ge=1, le=1_000_000)
    nonce_min_length: int = Field(default=16, strict=True, ge=1, le=128)
    nonce_max_length: int = Field(default=128, strict=True, ge=1, le=256)

    @model_validator(mode="after")
    def require_token_env_for_mode(self) -> GatewayIngressConfig:
        signed_only_configured = (
            self.signing_secret_env is not None
            or self.identity_version != SIGNED_IDENTITY_VERSION
            or self.policy_version != SIGNED_IDENTITY_POLICY_VERSION
            or self.clock_skew_seconds != 60
            or self.replay_ttl_seconds != 60
            or self.max_replay_entries != 4096
            or self.nonce_min_length != 16
            or self.nonce_max_length != 128
        )
        if (
            self.mode
            in {
                "service_bearer_static_identity",
                "service_bearer_signed_identity_v1",
            }
            and not self.service_token_env
        ):
            raise ValueError("service bearer ingress requires service_token_env")
        if self.mode != "service_bearer_signed_identity_v1" and signed_only_configured:
            raise ValueError("signed identity settings require signed gateway ingress mode")
        if self.mode == "service_bearer_signed_identity_v1" and not self.signing_secret_env:
            raise ValueError("signed identity ingress requires signing_secret_env")
        if self.replay_ttl_seconds < self.clock_skew_seconds:
            raise ValueError("signed identity replay TTL must cover clock skew")
        if self.nonce_min_length > self.nonce_max_length:
            raise ValueError("signed identity nonce bounds are invalid")
        if self.mode == "disabled" and self.service_token_env is not None:
            raise ValueError("disabled gateway ingress cannot configure service_token_env")
        return self

    @property
    def enabled(self) -> bool:
        return self.mode != "disabled"

    @property
    def signed(self) -> bool:
        return self.mode == "service_bearer_signed_identity_v1"

    def service_token(self) -> str:
        if not self.enabled or self.service_token_env is None:
            raise ValueError("gateway ingress service authentication is disabled")
        value = os.environ.get(self.service_token_env)
        if not value:
            raise ValueError("gateway ingress service credential is unavailable")
        return validate_service_token(value)

    def signing_secret(self) -> bytes:
        if not self.signed or self.signing_secret_env is None:
            raise ValueError("signed gateway identity is disabled")
        value = os.environ.get(self.signing_secret_env)
        if value is None:
            raise ValueError("gateway signing secret is unavailable")
        return validate_signing_secret(value)


class UpstreamConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")
    base_url: str = Field(min_length=1, max_length=2048)
    api_key_env: str = Field(min_length=1, pattern=r"^[A-Za-z_][A-Za-z0-9_]*$")
    model: str = Field(min_length=1, max_length=128)
    connect_timeout_seconds: float = Field(default=10, gt=0, le=300)
    request_timeout_seconds: float = Field(default=300, gt=0, le=3600)
    write_timeout_seconds: float = Field(default=30, gt=0, le=3600)
    pool_timeout_seconds: float = Field(default=10, gt=0, le=300)
    # Order 015-a (P01): hard bounds for the private bounded read of an
    # upstream HTTP-error body.  The diagnostic slice is used only by the
    # closed classifier in ``upstream_diagnostics`` and never forwarded,
    # logged, or persisted.  Positive finite ceilings.
    upstream_error_diagnostic_max_bytes: int = Field(default=16_384, ge=1, le=65_536)
    upstream_error_diagnostic_timeout_seconds: float = Field(default=1.0, gt=0, le=5.0)

    @model_validator(mode="after")
    def supported_base_path(self) -> UpstreamConfig:
        try:
            parsed = urlsplit(self.base_url)
            hostname = parsed.hostname
            _ = parsed.port
        except ValueError as exc:
            raise ValueError("upstream base_url must be a valid HTTP(S) URL") from exc
        if parsed.scheme not in {"http", "https"} or not parsed.netloc or not hostname:
            raise ValueError("upstream base_url must be HTTP(S)")
        if parsed.username is not None or parsed.password is not None:
            raise ValueError("upstream base_url must not contain credentials")
        if parsed.path.rstrip("/") not in {"", "/v1"} or parsed.query or parsed.fragment:
            raise ValueError("upstream base_url path must be empty or /v1")
        return self

    def origin(self) -> str:
        parsed = urlsplit(self.base_url)
        return f"{parsed.scheme}://{parsed.netloc}"

    def api_key(self) -> str:
        value = os.environ.get(self.api_key_env)
        if not value:
            raise ValueError(
                f"upstream credential environment variable is unset: {self.api_key_env}"
            )
        return value


class ObservationPolicy(BaseModel):
    """Finite request-only limits for constitutional observation."""

    model_config = ConfigDict(extra="forbid")
    schema_version: str = Field(default="observation-v1", min_length=1, max_length=64)
    policy_version: str = Field(default="references-v1", min_length=1, max_length=64)
    max_roots: int = Field(default=8, ge=1, le=64)
    max_source_bytes: int = Field(default=262_144, ge=1, le=4_194_304)
    max_candidates: int = Field(default=128, ge=1, le=4096)
    max_evidence_per_candidate: int = Field(default=16, ge=1, le=128)
    max_total_evidence: int = Field(default=1024, ge=1, le=16384)
    max_path_bytes: int = Field(default=512, ge=1, le=4096)


class CompilerConfig(BaseModel):
    """Bounded direct compiler settings for the explicitly enabled pipeline."""

    model_config = ConfigDict(extra="forbid")
    enabled: bool = False
    schema_version: str = Field(default="constitution-index-v1", min_length=1, max_length=64)
    prompt_policy_version: str = Field(
        default="constitutional-rank-v2", min_length=1, max_length=64
    )
    api_key_env: str = Field(
        default="QWEN3090_API_KEY", min_length=1, pattern=r"^[A-Za-z_][A-Za-z0-9_]*$"
    )
    reasoning_effort: Literal["low"] = "low"
    timeout_seconds: float = Field(default=45, gt=0, le=300)
    max_attempts: int = Field(default=2, ge=1, le=4)
    max_parallel_calls: int = Field(default=1, ge=1, le=1)
    max_output_tokens: int = Field(default=3000, ge=128, le=16000)
    # Order 015-a (P02): ceiling for the bounded adaptive token allowance.
    # After an explicit length completion the next permitted attempt uses
    # min(previous * 2, ceiling); the ceiling must stay at least the initial
    # allowance and within the legal maximum.
    max_output_tokens_ceiling: int = Field(default=8000, ge=128, le=16000)
    max_output_bytes: int = Field(default=256000, ge=1024, le=4194304)
    max_prompt_bytes: int = Field(default=384000, ge=1024, le=4194304)
    max_source_bytes: int = Field(default=262_144, ge=1, le=4_194_304)
    max_candidates: int = Field(default=128, ge=1, le=4096)
    max_json_depth: int = Field(default=24, ge=1, le=128)

    @model_validator(mode="after")
    def ceiling_covers_initial_allowance(self) -> CompilerConfig:
        if self.max_output_tokens_ceiling < self.max_output_tokens:
            raise ValueError("max_output_tokens_ceiling must be at least max_output_tokens")
        return self


class CacheConfig(BaseModel):
    """Private disposable filesystem-cache bounds for validated indexes only."""

    model_config = ConfigDict(extra="forbid")
    backend: Literal["filesystem"] = "filesystem"
    root: Path = Path("/dev/shm/slaif-local-coding")
    fallback_root: Path | None = Field(
        default_factory=lambda: (
            Path(os.environ.get("XDG_CACHE_HOME") or Path.home() / ".cache") / "slaif-local-coding"
        )
    )
    max_total_bytes: int = Field(default=67_108_864, ge=1024, le=1_073_741_824)
    max_entry_bytes: int = Field(default=65_536, ge=256, le=268_435_456)
    max_pinned_bytes: int = Field(default=8_388_608, ge=256, le=268_435_456)
    max_entries: int = Field(default=4096, ge=1, le=1_000_000)
    ttl_seconds: float = Field(default=604800, gt=0)
    max_scan_entries: int = Field(default=4096, ge=1, le=1_000_000)

    @model_validator(mode="after")
    def bounded(self) -> CacheConfig:
        for label, path in (("root", self.root), ("fallback_root", self.fallback_root)):
            if path is not None and (
                not path.is_absolute() or any(part == ".." for part in path.parts)
            ):
                raise ValueError(f"cache {label} must be an absolute normalized path")
        if self.max_entry_bytes > self.max_total_bytes:
            raise ValueError("cache entry budget cannot exceed total budget")
        if self.max_pinned_bytes > self.max_total_bytes:
            raise ValueError("cache pinned budget cannot exceed total budget")
        return self


class RehydrationConfig(BaseModel):
    """Process-local rehydration bounds; no persistent or cross-process state."""

    model_config = ConfigDict(extra="forbid")
    enabled: bool = True
    ttl_seconds: float = Field(default=3600, gt=0, le=86400)
    max_entries: int = Field(default=64, ge=1, le=1024)
    max_entry_bytes: int = Field(default=262_144, ge=1024)
    max_total_bytes: int = Field(default=1_048_576, ge=1024)

    @model_validator(mode="after")
    def bounded(self) -> RehydrationConfig:
        if self.max_entry_bytes > self.max_total_bytes:
            raise ValueError("rehydration entry budget cannot exceed total budget")
        return self


class ConstitutionIntegrationConfig(BaseModel):
    """Explicit working-set/injection policy and identity source.

    Static identity fields are configured appliance labels for the private MVP.
    Signed-request mode intentionally leaves them unset; verified request
    identity is supplied explicitly by the ingress boundary.
    """

    model_config = ConfigDict(extra="forbid")
    enabled: bool = False
    identity_source: Literal["static", "signed_request"] = "static"
    principal: str | None = Field(default=None, min_length=1, max_length=256)
    session: str | None = Field(default=None, min_length=1, max_length=256)
    repository: str | None = Field(default=None, min_length=1, max_length=256)
    max_injected_bytes: int = Field(default=16384, ge=256)
    candidate_max_count: int = Field(default=128, ge=1, le=4096)
    compile_failure_policy: Literal["preserve_original"] = "preserve_original"
    selector_schema_version: Literal["working-set-v1"] = "working-set-v1"
    render_version: Literal["constitution-render-v1"] = "constitution-render-v1"
    working_set_policy_version: str = Field(default="foundation-v1", min_length=1, max_length=64)
    working_set_max_entries: int = Field(default=128, ge=1, le=4096)
    acquisition_max_count: int = Field(default=128, ge=1, le=4096)
    max_dependency_acquisitions: int = Field(default=4, ge=1, le=16)
    entry_render_max_bytes: int = Field(default=8192, ge=128, le=1048576)
    injection_max_depth: int = Field(default=64, ge=1, le=256)
    injection_max_nodes: int = Field(default=16384, ge=1, le=1048576)
    rehydration: RehydrationConfig = Field(default_factory=lambda: RehydrationConfig())

    @model_validator(mode="after")
    def bounded(self) -> ConstitutionIntegrationConfig:
        static_identity_present = any((self.principal, self.session, self.repository))
        if (
            self.identity_source == "static"
            and self.enabled
            and not all((self.principal, self.session, self.repository))
        ):
            raise ValueError("enabled constitution integration requires static local identity")
        if self.identity_source == "signed_request" and static_identity_present:
            raise ValueError("signed-request constitution identity forbids static identity")
        if not self.enabled and self.identity_source != "static":
            raise ValueError("signed-request identity requires enabled constitution integration")
        if self.entry_render_max_bytes > self.max_injected_bytes:
            raise ValueError("entry render budget cannot exceed injected-byte budget")
        if self.working_set_max_entries > self.candidate_max_count:
            raise ValueError("working-set entries cannot exceed candidate bound")
        if self.acquisition_max_count > self.candidate_max_count:
            raise ValueError("acquisitions cannot exceed candidate bound")
        return self


# ---------------------------------------------------------------------------
# 022-a: explicit cache profile selector and closed v1 configuration
# ---------------------------------------------------------------------------

#: Constitution fields common to both cache profiles (022-a): enablement and
#: the validated identity source/labels. The route observation/constitution
#: flags live on the route itself. Every other constitution field is a
#: legacy byte-injection or selector policy.
COMMON_CONSTITUTION_FIELDS: frozenset[str] = frozenset(
    {"enabled", "identity_source", "principal", "session", "repository"}
)

V1_PROFILE = "dependency-bundles-v1"

V1_LEGACY_CACHE_CONFLICT = (
    "the dependency-bundles-v1 profile cannot be combined with an "
    "explicitly supplied legacy filesystem cache policy"
)
V1_LEGACY_COMPILER_CONFLICT = (
    "the dependency-bundles-v1 profile cannot be combined with an "
    "explicitly supplied legacy compiler policy"
)
V1_LEGACY_REHYDRATION_CONFLICT = (
    "the dependency-bundles-v1 profile cannot be combined with an "
    "explicitly supplied legacy derived-rehydration policy"
)
V1_LEGACY_POLICY_CONFLICT = (
    "the dependency-bundles-v1 profile cannot be combined with an "
    "explicitly supplied legacy byte-injection or selector policy"
)

V1_ROUTE_CONTRACT_MISSING = "each governed v1 route requires an explicit route model contract"
V1_ROUTE_CONTRACT_ORPHAN = "route model contracts may only declare governed v1 routes"
V1_ROUTE_CONTRACT_MODEL_MISMATCH = "the route model contract must declare the route's model"
V1_ROUTE_CONTRACT_CONTEXT_MISMATCH = (
    "the route model contract must declare the configured effective context"
)
V1_CAPABILITY_NOT_PINNED = (
    "the route model contract must declare the pinned tokenizer and render capability"
)


def _section_provided(value: object, default: BaseModel | None) -> bool:
    """Whether an operator explicitly supplied one configuration section.

    A raw block with no keys and a pure materialized default do not count;
    an explicitly supplied value at its default still counts as supplied
    (022-a migration law).
    """
    if value is None:
        return False
    if isinstance(value, dict):
        return bool(value)
    if isinstance(value, BaseModel):
        if value.model_fields_set:
            return True
        return default is not None and value.model_dump() != default.model_dump()
    return True


def _constitution_legacy_conflict(value: object) -> str | None:
    """Fixed conflict message for a supplied legacy constitution policy.

    Returns None when only the common enablement/identity fields (or an
    empty policy block) are supplied.
    """
    if value is None:
        return None
    if isinstance(value, dict):
        for key, sub in value.items():
            if key == "rehydration":
                if _section_provided(sub, RehydrationConfig()):
                    return V1_LEGACY_REHYDRATION_CONFLICT
                continue
            if key not in COMMON_CONSTITUTION_FIELDS:
                return V1_LEGACY_POLICY_CONFLICT
        return None
    if isinstance(value, ConstitutionIntegrationConfig):
        # An explicitly supplied section counts as supplied even when every
        # value equals its default (022-a migration law); a materialized
        # default (nothing supplied) or an empty policy block does not.
        if _section_provided(value.rehydration, RehydrationConfig()):
            return V1_LEGACY_REHYDRATION_CONFLICT
        for field in value.model_fields_set:
            if field not in COMMON_CONSTITUTION_FIELDS and field != "rehydration":
                return V1_LEGACY_POLICY_CONFLICT
        return None
    return V1_LEGACY_POLICY_CONFLICT


class ContextCacheRouteContract(BaseModel):
    """Explicit v1 model-contract declaration for one governed route (022-a).

    Binds the route's declared model to the pinned tokenizer/render
    capability and the configured effective context C. The tokenizer
    capability is the closed pinned artifact declaration (the reference
    upstream revision) and the render policy is the pinned bundle render
    policy: any deviation from the pinned facts fails closed. Pure
    configuration validation: no tokenizer loading, no store IO, no
    upstream calls.
    """

    # Privacy law: validation errors never echo the raw validation input.
    model_config = ConfigDict(extra="forbid", hide_input_in_errors=True)
    model: str = Field(min_length=1, max_length=128)
    context_tokens: int = Field(ge=BUDGET_CONTEXT_MIN, le=BUDGET_CONTEXT_MAX)
    tokenizer_upstream: str = Field(default=PINNED_TOKENIZER_UPSTREAM, min_length=1, max_length=256)
    tokenizer_revision: str = Field(default=PINNED_TOKENIZER_REVISION, pattern=r"^[0-9a-f]{40}$")
    render_policy_version: str = Field(
        default=BUNDLE_TOKENIZER_RENDER_POLICY_VERSION, min_length=1, max_length=64
    )

    @model_validator(mode="after")
    def pinned_capability(self) -> ContextCacheRouteContract:
        if (
            self.tokenizer_upstream != PINNED_TOKENIZER_UPSTREAM
            or self.tokenizer_revision != PINNED_TOKENIZER_REVISION
            or self.render_policy_version != BUNDLE_TOKENIZER_RENDER_POLICY_VERSION
        ):
            raise ValueError(V1_CAPABILITY_NOT_PINNED)
        return self


class ContextCacheRecoveryConfig(BaseModel):
    """Explicit v1 protected per-session recovery opt-in (typed; no IO).

    Configuration validation never opens, creates, enumerates or probes the
    recovery store, never resolves a request workspace, never reads
    credentials and never calls an upstream. The operator-prepared
    directory, retention, deletion and encryption obligations are the
    SECURITY.md protected-source-recovery contract.
    """

    # Privacy law: validation errors never echo the raw validation input,
    # and the operator's private recovery root never appears in reprs.
    model_config = ConfigDict(extra="forbid", hide_input_in_errors=True)
    enabled: bool = False
    root: Path | None = Field(default=None, repr=False)

    @model_validator(mode="after")
    def bounded(self) -> ContextCacheRecoveryConfig:
        if self.root is not None and (
            not self.root.is_absolute() or any(part == ".." for part in self.root.parts)
        ):
            raise ValueError("v1 recovery root must be an absolute normalized path")
        return self


class ContextCacheConfig(BaseModel):
    """Explicit cache profile selector and the closed v1 configuration.

    Omission (or an explicit ``legacy``) keeps the existing legacy behavior.
    ``dependency-bundles-v1`` is accepted only with its closed typed
    configuration (021 budget/compiler, 019 RAM bounds, protected recovery
    opt-in). The v1 runtime itself remains unavailable in this build:
    ``create_app`` refuses a selected v1 profile at startup, and a settings
    model or a refused app does not establish v1 readiness, source
    replacement, native-format, streaming or recovery qualification.
    """

    # Privacy law: validation errors never echo the raw validation input.
    model_config = ConfigDict(extra="forbid", hide_input_in_errors=True)
    profile: Literal["legacy", "dependency-bundles-v1"] = "legacy"
    # The existing one-worker policy (019 RAM-state law): exactly one service
    # worker and one live owner per session; multi-worker configuration is
    # unsupported and fails closed. Strictly one worker: any other value is
    # a configuration error. Strict integer type: booleans, floats (even
    # whole-valued) and strings never coerce into the worker count.
    workers: int = Field(default=1, ge=1, le=1, strict=True)
    # Admission defaults to lean; greedy must be explicit (v1 only).
    admission_mode: Literal["lean", "greedy"] = "lean"
    budget: BundleBudgetConfig | None = None
    compiler: BundleCompilerConfig | None = None
    ram: RamStateBounds | None = None
    recovery: ContextCacheRecoveryConfig = Field(default_factory=ContextCacheRecoveryConfig)
    # Each governed route's explicit model-contract declaration (v1 only):
    # the route name binds its declared model to the pinned tokenizer/render
    # capability and the configured effective C (022-a).
    route_contracts: dict[str, ContextCacheRouteContract] = Field(default_factory=dict)
    # The distinct application-owned private marker key material (022-c):
    # a PROTECTED ENVIRONMENT REFERENCE (the name of the environment
    # variable holding the key bytes), never the key itself.  The value
    # is resolved once at v1 runtime construction, stays in process
    # memory (repr-suppressed) and never crosses Git, logs, refs,
    # response fields, test captures or operational reprs.  It is never
    # a gateway / service credential and never a public digest; the
    # stable authenticated session binding is the MAC-bound trusted
    # namespace key (stable across recovery).
    marker_key_env: str | None = Field(
        default=None,
        pattern=r"^[A-Za-z_][A-Za-z0-9_]*$",
        repr=False,
    )

    @model_validator(mode="after")
    def profile_closure(self) -> ContextCacheConfig:
        provided = self.model_fields_set
        if self.profile == V1_PROFILE:
            if "budget" not in provided or self.budget is None:
                raise ValueError(
                    "the dependency-bundles-v1 profile requires the "
                    "explicit effective-context budget"
                )
            if "compiler" not in provided or self.compiler is None:
                raise ValueError(
                    "the dependency-bundles-v1 profile requires the "
                    "explicit bounded compiler policy"
                )
            if "ram" not in provided or self.ram is None:
                raise ValueError(
                    "the dependency-bundles-v1 profile requires the explicit RAM ownership bounds"
                )
            if not self.recovery.enabled:
                raise ValueError(
                    "the dependency-bundles-v1 profile requires the "
                    "explicit protected-recovery opt-in"
                )
            if self.recovery.root is None:
                raise ValueError(
                    "the dependency-bundles-v1 profile requires the configured recovery root"
                )
            if "marker_key_env" not in provided or self.marker_key_env is None:
                raise ValueError(
                    "the dependency-bundles-v1 profile requires the explicit "
                    "application-owned marker key reference"
                )
            return self
        for field in ("budget", "compiler", "ram"):
            if field in provided and getattr(self, field) is not None:
                raise ValueError(
                    "the v1 context-cache settings require the dependency-bundles-v1 profile"
                )
        if "marker_key_env" in provided and self.marker_key_env is not None:
            raise ValueError(
                "the v1 context-cache settings require the dependency-bundles-v1 profile"
            )
        if "recovery" in provided and _section_provided(
            self.recovery, ContextCacheRecoveryConfig()
        ):
            raise ValueError(
                "the v1 context-cache settings require the dependency-bundles-v1 profile"
            )
        if "admission_mode" in provided and self.admission_mode != "lean":
            raise ValueError(
                "the v1 context-cache settings require the dependency-bundles-v1 profile"
            )
        if self.route_contracts:
            raise ValueError(
                "the v1 context-cache settings require the dependency-bundles-v1 profile"
            )
        return self


class RouteConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str = Field(pattern=r"^[a-z0-9][a-z0-9_-]{0,63}$")
    model: str = Field(min_length=1, max_length=128)
    max_images_per_request: int | None = Field(default=None, ge=0)
    image_overflow_policy: Literal["retain_newest", "reject", "passthrough"]
    responses_tool_policy: Literal["passthrough", "drop_disabled_codex_search"] = "passthrough"
    enable_responses: bool = True
    enable_chat_completions: bool = True
    observation_enabled: bool = False
    constitution_enabled: bool = False

    @model_validator(mode="after")
    def image_policy_requires_limit(self) -> RouteConfig:
        if self.image_overflow_policy in {"retain_newest", "reject"} and (
            self.max_images_per_request is None
        ):
            raise ValueError("image overflow policy requires max_images_per_request")
        if self.image_overflow_policy == "passthrough" and self.max_images_per_request is not None:
            raise ValueError("passthrough image policy cannot declare an enforced image limit")
        return self

    def enables(self, endpoint: str) -> bool:
        return (endpoint == "/v1/responses" and self.enable_responses) or (
            endpoint == "/v1/chat/completions" and self.enable_chat_completions
        )


class ObservabilityConfig(BaseModel):
    """Safe operator controls; raw payload logging is never configurable."""

    model_config = ConfigDict(extra="forbid")
    log_level: Literal["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"] = "INFO"
    log_raw_payloads: Literal[False] = False
    metrics_enabled: bool = True
    metrics_host: Literal["127.0.0.1", "::1", "localhost"] = "127.0.0.1"


class Settings(BaseModel):
    # Privacy law: validation errors never echo the raw validation input
    # (private paths, credential environment names).
    model_config = ConfigDict(extra="forbid", hide_input_in_errors=True)
    server: ServerConfig
    gateway_ingress: GatewayIngressConfig = Field(default_factory=lambda: GatewayIngressConfig())
    upstream: UpstreamConfig
    routes: list[RouteConfig] = Field(min_length=1)
    observation: ObservationPolicy = Field(default_factory=lambda: ObservationPolicy())
    compiler: CompilerConfig = Field(default_factory=lambda: CompilerConfig())
    cache: CacheConfig = Field(default_factory=lambda: CacheConfig())
    constitution: ConstitutionIntegrationConfig = Field(
        default_factory=lambda: ConstitutionIntegrationConfig()
    )
    context_cache: ContextCacheConfig = Field(default_factory=lambda: ContextCacheConfig())
    observability: ObservabilityConfig = Field(default_factory=lambda: ObservabilityConfig())

    @model_validator(mode="before")
    @classmethod
    def v1_legacy_conflict_law(cls, data: Any) -> Any:
        # 022-a migration law: under the selected v1 profile, an explicitly
        # supplied legacy cache/TTL/LRU, derived-rehydration, compiler or
        # byte-injection/selector policy is a configuration error, even at
        # its default value. A materialized default or an empty policy block
        # alone does not conflict.
        if not isinstance(data, dict):
            return data
        context_cache = data.get("context_cache")
        if isinstance(context_cache, ContextCacheConfig):
            profile = context_cache.profile
        elif isinstance(context_cache, dict):
            profile = context_cache.get("profile", "legacy")
        else:
            profile = "legacy"
        if profile != V1_PROFILE:
            return data
        if _section_provided(data.get("cache"), CacheConfig()):
            raise ValueError(V1_LEGACY_CACHE_CONFLICT)
        if _section_provided(data.get("compiler"), CompilerConfig()):
            raise ValueError(V1_LEGACY_COMPILER_CONFLICT)
        constitution_conflict = _constitution_legacy_conflict(data.get("constitution"))
        if constitution_conflict is not None:
            raise ValueError(constitution_conflict)
        return data

    @model_validator(mode="after")
    def v1_route_contract_law(self) -> Settings:
        # 022-a: each governed v1 route binds its declared model contract
        # to the pinned tokenizer/render capability and the configured
        # effective C through the explicit route model contract. Orphan
        # contracts (unknown or non-governed routes) fail closed first:
        # this law runs before the legacy integration law and the v1
        # profile law so a misplaced contract is the reported failure.
        if self.context_cache.profile != V1_PROFILE:
            return self
        contracts = self.context_cache.route_contracts
        governed = {route.name for route in self.routes if route.constitution_enabled}
        if set(contracts) != governed:
            if any(name not in governed for name in contracts):
                raise ValueError(V1_ROUTE_CONTRACT_ORPHAN)
            raise ValueError(V1_ROUTE_CONTRACT_MISSING)
        budget = self.context_cache.budget
        if budget is not None:
            for route in self.routes:
                if not route.constitution_enabled:
                    continue
                contract = contracts[route.name]
                if contract.model != route.model:
                    raise ValueError(V1_ROUTE_CONTRACT_MODEL_MISMATCH)
                if contract.context_tokens != budget.context_tokens:
                    raise ValueError(V1_ROUTE_CONTRACT_CONTEXT_MISMATCH)
        return self

    @model_validator(mode="after")
    def safe_integration(self) -> Settings:
        v1 = self.context_cache.profile == V1_PROFILE
        if self.gateway_ingress.signed:
            compiler_ready = (
                self.context_cache.compiler is not None if v1 else self.compiler.enabled
            )
            if not self.constitution.enabled or not compiler_ready:
                raise ValueError(
                    "signed identity ingress requires enabled compiler and constitution integration"
                )
            if self.constitution.identity_source != "signed_request":
                raise ValueError(
                    "signed identity ingress requires signed-request constitution identity"
                )
            if any(
                (
                    self.constitution.principal,
                    self.constitution.session,
                    self.constitution.repository,
                )
            ):
                raise ValueError("signed identity ingress forbids static constitution identity")
        elif self.constitution.identity_source != "static":
            raise ValueError("signed-request constitution identity requires signed ingress")
        if self.gateway_ingress.mode == "service_bearer_static_identity" and not (
            self.constitution.enabled
            and self.constitution.principal
            and self.constitution.session
            and self.constitution.repository
        ):
            raise ValueError(
                "service bearer ingress requires complete enabled static constitution identity"
            )
        if not v1 and self.constitution.enabled and not self.compiler.enabled:
            raise ValueError("constitution integration requires direct compiler enablement")
        if (
            not v1
            and self.constitution.enabled
            and (urlsplit(self.upstream.base_url).path.rstrip("/") != "/v1")
        ):
            raise ValueError("constitution integration requires an upstream /v1 base path")
        if (
            not v1
            and self.constitution.enabled
            and (
                self.compiler.schema_version != "constitution-index-v1"
                or self.constitution.selector_schema_version != "working-set-v1"
                or self.constitution.render_version != "constitution-render-v1"
            )
        ):
            raise ValueError("constitution integration requires supported schema versions")
        if self.constitution.enabled and not any(
            route.constitution_enabled for route in self.routes
        ):
            raise ValueError("global constitution integration requires an enabled route")
        for route in self.routes:
            if route.constitution_enabled and not (
                self.constitution.enabled and route.observation_enabled
            ):
                raise ValueError(
                    "route constitution integration requires global enablement and observation"
                )
        return self

    @model_validator(mode="after")
    def v1_profile_law(self) -> Settings:
        # 022-a: validate the explicit effective context and the existing
        # 021 budget bounds against each enabled v1 route's declared
        # model/vision contract. The same contract may serve compatible
        # routes that explicitly share it; mixed vision declarations cannot.
        if self.context_cache.profile != V1_PROFILE:
            return self
        budget = self.context_cache.budget
        if budget is None:
            return self  # the v1 closure above already refused
        if not self.constitution.enabled:
            raise ValueError(
                "the dependency-bundles-v1 profile requires enabled constitution integration"
            )
        if not any(route.constitution_enabled for route in self.routes):
            raise ValueError("the dependency-bundles-v1 profile requires an enabled route")
        declared: bool | None = None
        for route in self.routes:
            if not route.constitution_enabled:
                continue
            if route.max_images_per_request is None:
                # An image-passthrough route declares no enforced image
                # limit and forwards images unchanged: it neither declares
                # nor denies the vision contract and may use the explicitly
                # declared v1 vision contract.
                continue
            route_vision = route.max_images_per_request >= 1
            if declared is None:
                declared = route_vision
            elif route_vision != declared:
                raise ValueError(
                    "one v1 context contract cannot serve both vision and text-only routes"
                )
            if route_vision and budget.max_retained_images < route.max_images_per_request:
                raise ValueError(
                    "the v1 budget retained-image capacity cannot cover the route image limit"
                )
        if declared is not None and budget.vision_enabled != declared:
            raise ValueError(
                "the v1 budget vision contract does not match the enabled route image policy"
            )
        return self

    @model_validator(mode="after")
    def binding_law(self) -> Settings:
        # D1 cross-mode rule: a non-loopback bind is legal if and only if the
        # full accepted signed ingress contract is active; loopback stays
        # legal (and is the only legal bind) without it.
        if not is_loopback_bind_literal(self.server.listen_host) and not (
            self.gateway_ingress.mode == "service_bearer_signed_identity_v1"
        ):
            raise ValueError(
                "non-loopback listen_host requires "
                "gateway_ingress mode service_bearer_signed_identity_v1"
            )
        return self

    @model_validator(mode="after")
    def distinct_secret_role_env_names(self) -> Settings:
        # C2 (order 010-a): the three Local-side secret roles must use
        # distinct environment names so one value can never silently fill
        # two roles (upstream credential, Gateway service credential,
        # Gateway signing secret). The v1 compiler credential is a
        # protected reference to the same private upstream channel: it may
        # share the private upstream environment name but must never take a
        # Gateway credential's environment name (022-a).
        roles: dict[str, str] = {"upstream": self.upstream.api_key_env}
        if self.gateway_ingress.service_token_env is not None:
            roles["gateway_service"] = self.gateway_ingress.service_token_env
        if self.gateway_ingress.signing_secret_env is not None:
            roles["gateway_signing"] = self.gateway_ingress.signing_secret_env
        names = list(roles.items())
        for i, (label_a, name_a) in enumerate(names):
            for label_b, name_b in names[i + 1 :]:
                if name_a == name_b:
                    raise ValueError(
                        f"secret roles {label_a} and {label_b} cannot share one environment name"
                    )
        if self.context_cache.profile == V1_PROFILE and self.context_cache.compiler is not None:
            for label in ("gateway_service", "gateway_signing"):
                if label in roles and roles[label] == self.context_cache.compiler.api_key_env:
                    raise ValueError(
                        f"secret roles v1_compiler and {label} cannot share one environment name"
                    )
        return self

    @model_validator(mode="after")
    def unique_routes(self) -> Settings:
        names = [route.name for route in self.routes]
        if len(names) != len(set(names)):
            raise ValueError("route names must be unique")
        matches: set[tuple[str, str]] = set()
        for route in self.routes:
            for endpoint in ("/v1/responses", "/v1/chat/completions"):
                if not route.enables(endpoint):
                    continue
                match = (route.model, endpoint)
                if match in matches:
                    raise ValueError("routes must uniquely match each (model, endpoint) pair")
                matches.add(match)
        return self


def load_settings(path: Path) -> Settings:
    """Load a TOML file and reject unknown or invalid configuration."""
    with path.open("rb") as stream:
        raw = tomllib.load(stream)
    # 022-b migration-boundary law: under a selected v1 profile the legacy
    # conflict-target sections (filesystem cache, legacy compiler,
    # constitution byte-injection/selector and derived-rehydration policy)
    # must not pass through standalone nested validation before the fixed
    # migration refusal: a malformed explicitly supplied legacy field must
    # reject at that intended boundary with its fixed message, never
    # echoing its value. They are therefore handed to Settings raw, whose
    # before-validator applies the closed conflict law first. The legacy
    # profile keeps the existing standalone materialization (existing
    # legacy loading is unchanged).
    context_cache_raw = raw.get("context_cache")
    v1_selected = (
        isinstance(context_cache_raw, dict) and context_cache_raw.get("profile") == V1_PROFILE
    )
    # Sections are materialized only when explicitly present so that a
    # materialized default never counts as an operator-supplied setting
    # (022-a migration law). Bounded section validation happens here;
    # cross-feature safety is enforced by Settings itself.
    explicit: dict[str, Any] = {}
    if "gateway_ingress" in raw:
        explicit["gateway_ingress"] = GatewayIngressConfig.model_validate(
            raw.pop("gateway_ingress")
        )
    if "compiler" in raw:
        if not v1_selected:
            explicit["compiler"] = CompilerConfig.model_validate(raw.pop("compiler"))
    if "cache" in raw:
        if not v1_selected:
            explicit["cache"] = CacheConfig.model_validate(raw.pop("cache"))
    if "constitution" in raw:
        if not v1_selected:
            explicit["constitution"] = ConstitutionIntegrationConfig.model_validate(
                raw.pop("constitution")
            )
    if "context_cache" in raw:
        explicit["context_cache"] = ContextCacheConfig.model_validate(raw.pop("context_cache"))
    if "observability" in raw:
        explicit["observability"] = ObservabilityConfig.model_validate(raw.pop("observability"))
    return Settings.model_validate({**raw, **explicit})

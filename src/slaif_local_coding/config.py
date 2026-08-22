"""Validated, deterministic adapter configuration."""

from __future__ import annotations

import os
import tomllib
from pathlib import Path
from typing import Literal
from urllib.parse import urlsplit

from pydantic import BaseModel, ConfigDict, Field, model_validator


class ServerConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")
    listen_host: str = "127.0.0.1"
    listen_port: int = Field(default=18031, ge=1, le=65535)
    request_body_max_bytes: int = Field(default=67_108_864, gt=0)
    json_max_nesting_depth: int = Field(default=128, ge=1, le=256)

    @model_validator(mode="after")
    def loopback_only(self) -> ServerConfig:
        if self.listen_host not in {"127.0.0.1", "::1", "localhost"}:
            raise ValueError("objective-000 adapter must bind to loopback")
        return self


class UpstreamConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")
    base_url: str
    api_key_env: str = Field(min_length=1)
    model: str = Field(min_length=1)
    connect_timeout_seconds: float = Field(default=10, gt=0)
    request_timeout_seconds: float = Field(default=300, gt=0)
    write_timeout_seconds: float = Field(default=30, gt=0)
    pool_timeout_seconds: float = Field(default=10, gt=0)

    @model_validator(mode="after")
    def supported_base_path(self) -> UpstreamConfig:
        parsed = urlsplit(self.base_url)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise ValueError("upstream base_url must be HTTP(S)")
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
    api_key_env: str = Field(default="QWEN3090_API_KEY", min_length=1)
    reasoning_effort: Literal["low"] = "low"
    timeout_seconds: float = Field(default=45, gt=0, le=300)
    max_attempts: int = Field(default=2, ge=1, le=4)
    max_parallel_calls: int = Field(default=1, ge=1, le=1)
    max_output_tokens: int = Field(default=3000, ge=128, le=16000)
    max_output_bytes: int = Field(default=256000, ge=1024, le=4194304)
    max_prompt_bytes: int = Field(default=384000, ge=1024, le=4194304)
    max_source_bytes: int = Field(default=262_144, ge=1, le=4_194_304)
    max_candidates: int = Field(default=128, ge=1, le=4096)
    max_json_depth: int = Field(default=24, ge=1, le=128)


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
    max_total_bytes: int = Field(default=67_108_864, ge=1024)
    max_entry_bytes: int = Field(default=65_536, ge=256)
    max_pinned_bytes: int = Field(default=8_388_608, ge=256)
    max_entries: int = Field(default=4096, ge=1)
    ttl_seconds: float = Field(default=604800, gt=0)
    max_scan_entries: int = Field(default=4096, ge=1, le=1_000_000)

    @model_validator(mode="after")
    def bounded(self) -> CacheConfig:
        if self.max_entry_bytes > self.max_total_bytes:
            raise ValueError("cache entry budget cannot exceed total budget")
        if self.max_pinned_bytes > self.max_total_bytes:
            raise ValueError("cache pinned budget cannot exceed total budget")
        return self


class ConstitutionIntegrationConfig(BaseModel):
    """Explicit local single-user working-set/injection policy.

    Identity fields are configured static appliance labels for the private MVP.
    They are never taken from caller headers, bodies, models, or source content,
    and they do not provide signed multi-user production isolation.
    """

    model_config = ConfigDict(extra="forbid")
    enabled: bool = False
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

    @model_validator(mode="after")
    def bounded(self) -> ConstitutionIntegrationConfig:
        if self.enabled and not all((self.principal, self.session, self.repository)):
            raise ValueError("enabled constitution integration requires static local identity")
        if self.entry_render_max_bytes > self.max_injected_bytes:
            raise ValueError("entry render budget cannot exceed injected-byte budget")
        if self.working_set_max_entries > self.candidate_max_count:
            raise ValueError("working-set entries cannot exceed candidate bound")
        if self.acquisition_max_count > self.candidate_max_count:
            raise ValueError("acquisitions cannot exceed candidate bound")
        return self


class RouteConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str = Field(pattern=r"^[a-z0-9][a-z0-9_-]{0,63}$")
    model: str
    max_images_per_request: int | None = Field(default=None, ge=0)
    image_overflow_policy: Literal["retain_newest", "reject", "passthrough"]
    enable_responses: bool = True
    enable_chat_completions: bool = True
    observation_enabled: bool = False
    constitution_enabled: bool = False

    def enables(self, endpoint: str) -> bool:
        return (endpoint == "/v1/responses" and self.enable_responses) or (
            endpoint == "/v1/chat/completions" and self.enable_chat_completions
        )


class Settings(BaseModel):
    model_config = ConfigDict(extra="forbid")
    server: ServerConfig
    upstream: UpstreamConfig
    routes: list[RouteConfig] = Field(min_length=1)
    observation: ObservationPolicy = Field(default_factory=lambda: ObservationPolicy())
    compiler: CompilerConfig = Field(default_factory=lambda: CompilerConfig())
    cache: CacheConfig = Field(default_factory=lambda: CacheConfig())
    constitution: ConstitutionIntegrationConfig = Field(
        default_factory=lambda: ConstitutionIntegrationConfig()
    )

    @model_validator(mode="after")
    def safe_integration(self) -> Settings:
        if self.constitution.enabled and not self.compiler.enabled:
            raise ValueError("constitution integration requires direct compiler enablement")
        if self.constitution.enabled and (
            self.compiler.schema_version != "constitution-index-v1"
            or self.constitution.selector_schema_version != "working-set-v1"
            or self.constitution.render_version != "constitution-render-v1"
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
    # Objective-003 modules validate bounded settings before app construction;
    # cross-feature safety is enforced by Settings itself.
    compiler_raw = raw.pop("compiler", {})
    cache_raw = raw.pop("cache", {})
    constitution_raw = raw.pop("constitution", {})
    compiler_config = CompilerConfig.model_validate(compiler_raw)
    cache_config = CacheConfig.model_validate(cache_raw)
    constitution_config = ConstitutionIntegrationConfig.model_validate(constitution_raw)
    observability = raw.pop("observability", {})
    if observability.get("log_raw_payloads") is not False:
        raise ValueError("raw payload logging must be explicitly disabled")
    return Settings.model_validate(
        {
            **raw,
            "compiler": compiler_config,
            "cache": cache_config,
            "constitution": constitution_config,
        }
    )

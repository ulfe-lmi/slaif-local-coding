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
    """Library-only objective-002 compiler settings.

    ``enabled`` is deliberately false-only: public request handlers must not
    invoke compilation or injection until a later ordered integration slice.
    """

    model_config = ConfigDict(extra="forbid")
    enabled: Literal[False] = False
    schema_version: str = Field(default="constitution-index-v1", min_length=1, max_length=64)
    prompt_policy_version: str = Field(
        default="constitutional-rank-v1", min_length=1, max_length=64
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
    """Objective-002 keeps injection/acquisition/rehydration explicitly off."""

    model_config = ConfigDict(extra="forbid")
    enabled: Literal[False] = False
    max_injected_bytes: int = Field(default=16384, ge=256)
    candidate_max_count: int = Field(default=128, ge=1, le=4096)
    compile_failure_policy: Literal["preserve_original"] = "preserve_original"


class RouteConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str = Field(pattern=r"^[a-z0-9][a-z0-9_-]{0,63}$")
    model: str
    max_images_per_request: int | None = Field(default=None, ge=0)
    image_overflow_policy: Literal["retain_newest", "reject", "passthrough"]
    enable_responses: bool = True
    enable_chat_completions: bool = True
    observation_enabled: bool = False

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
    # Objective-002 modules are callable as a library, but public request
    # integration remains explicitly disabled. Validate these bounded settings
    # now so configuration errors fail at startup rather than during later work.
    compiler_raw = raw.pop("compiler", {})
    cache_raw = raw.pop("cache", {})
    constitution_raw = raw.pop("constitution", {})
    compiler_config = CompilerConfig.model_validate(compiler_raw)
    cache_config = CacheConfig.model_validate(cache_raw)
    constitution_config = ConstitutionIntegrationConfig.model_validate(constitution_raw)
    if compiler_config.enabled or constitution_config.enabled:
        raise ValueError("public compiler/injection integration is disabled in objective 002")
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

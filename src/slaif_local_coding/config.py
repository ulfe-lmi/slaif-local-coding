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


class RouteConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str = Field(pattern=r"^[a-z0-9][a-z0-9_-]{0,63}$")
    model: str
    max_images_per_request: int | None = Field(default=None, ge=0)
    image_overflow_policy: Literal["retain_newest", "reject", "passthrough"]
    enable_responses: bool = True
    enable_chat_completions: bool = True

    def enables(self, endpoint: str) -> bool:
        return (endpoint == "/v1/responses" and self.enable_responses) or (
            endpoint == "/v1/chat/completions" and self.enable_chat_completions
        )


class Settings(BaseModel):
    model_config = ConfigDict(extra="forbid")
    server: ServerConfig
    upstream: UpstreamConfig
    routes: list[RouteConfig] = Field(min_length=1)

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
    # Future-objective sections are inert only when explicitly disabled.
    for section in ("compiler", "constitution"):
        future = raw.pop(section, {})
        if future.get("enabled") is not False:
            raise ValueError(f"{section} must be explicitly disabled in objective 000")
    raw.pop("cache", None)
    observability = raw.pop("observability", {})
    if observability.get("log_raw_payloads") is not False:
        raise ValueError("raw payload logging must be explicitly disabled")
    return Settings.model_validate(raw)

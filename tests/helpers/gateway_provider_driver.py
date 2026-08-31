"""Content-free facts and assertions for the pinned gateway provider driver."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

GATEWAY_MAIN_SHA = "2527030f5bbb90a7f0f354eb5347caee333ce4a7"
UPSTREAM_MODEL = "qwen3.8-27b"


@dataclass(frozen=True)
class ProviderDriverFacts:
    """Safe facts emitted by one direct provider-adapter execution."""

    gateway_sha: str
    adapter_class: str
    provider_request_class: str
    nonstream_status: int
    nonstream_upstream_model: str
    nonstream_usage_total: int | None
    stream_status: int
    stream_event_types: tuple[str, ...]
    stream_event_count: int
    candidate_auth_ok: bool
    upstream_auth_ok: bool
    upstream_service_token_not_forwarded: bool
    rewritten_model_ok: bool
    client_key_filtered: bool
    identity_headers_filtered: bool
    metrics_secret_free: bool
    provider_only_no_accounting: bool


def provider_request_field_names(request: Any) -> frozenset[str]:
    """Return dataclass field names without serializing request content."""
    return frozenset(request.__dataclass_fields__)


def assert_provider_driver_facts(facts: ProviderDriverFacts) -> None:
    """Validate the bounded contract without network access or raw payloads."""
    assert facts.gateway_sha == GATEWAY_MAIN_SHA
    assert facts.adapter_class == "OpenAICompatibleProviderAdapter"
    assert facts.provider_request_class == "ProviderRequest"
    assert facts.nonstream_status == 200
    assert facts.nonstream_upstream_model == UPSTREAM_MODEL
    assert facts.nonstream_usage_total == 5
    assert facts.stream_status == 200
    assert facts.stream_event_types == (
        "response.created",
        "response.output_text.delta",
        "response.completed",
    )
    assert facts.stream_event_count == 3
    assert facts.candidate_auth_ok
    assert facts.upstream_auth_ok
    assert facts.upstream_service_token_not_forwarded
    assert facts.rewritten_model_ok
    assert facts.client_key_filtered
    assert facts.identity_headers_filtered
    assert facts.metrics_secret_free
    assert facts.provider_only_no_accounting


def safe_provider_request_body() -> Mapping[str, object]:
    """Synthetic request body used by the executable driver."""
    return {"model": "client-requested-model", "input": "driver", "store": False}

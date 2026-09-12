"""Hermetic tests for the repository-only gateway driver seam."""

from __future__ import annotations

from dataclasses import replace

import pytest

from tests.helpers.gateway_provider_driver import (
    GATEWAY_MAIN_SHA,
    ProviderDriverFacts,
    assert_provider_driver_facts,
    provider_request_field_names,
    safe_provider_request_body,
)


def _facts() -> ProviderDriverFacts:
    return ProviderDriverFacts(
        gateway_sha=GATEWAY_MAIN_SHA,
        adapter_class="OpenAICompatibleProviderAdapter",
        provider_request_class="ProviderRequest",
        nonstream_status=200,
        nonstream_upstream_model="qwen3.8-27b",
        nonstream_usage_total=5,
        stream_status=200,
        stream_event_types=(
            "response.created",
            "response.output_text.delta",
            "response.completed",
        ),
        stream_event_count=3,
        candidate_auth_ok=True,
        upstream_auth_ok=True,
        upstream_service_token_not_forwarded=True,
        rewritten_model_ok=True,
        client_key_filtered=True,
        identity_headers_filtered=True,
        metrics_secret_free=True,
        provider_only_no_accounting=True,
    )


def test_driver_facts_are_content_free_and_strict() -> None:
    assert_provider_driver_facts(_facts())
    with pytest.raises(AssertionError):
        assert_provider_driver_facts(replace(_facts(), stream_event_count=2))


def test_driver_helpers_do_not_require_gateway_checkout_or_network() -> None:
    assert safe_provider_request_body() == {
        "model": "client-requested-model",
        "input": "driver",
        "store": False,
    }

    class SyntheticRequest:
        __dataclass_fields__ = {"body": object(), "endpoint": object()}

    assert provider_request_field_names(SyntheticRequest()) == {"body", "endpoint"}

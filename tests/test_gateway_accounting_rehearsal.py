"""Hermetic contract tests for the disposable gateway rehearsal facts."""

from __future__ import annotations

from dataclasses import replace

import pytest

from tests.helpers.gateway_accounting_rehearsal import (
    GATEWAY_MAIN_SHA,
    GatewayRehearsalFacts,
    assert_gateway_rehearsal_facts,
)


def _passing_facts() -> GatewayRehearsalFacts:
    return GatewayRehearsalFacts(
        gateway_sha=GATEWAY_MAIN_SHA,
        gateway_checkout_clean_before=True,
        gateway_checkout_clean_after=True,
        postgres_image_preexisted=False,
        postgres_image_pulled=True,
        postgres_image_removed=True,
        postgres_tmpfs_only=True,
        gateway_health_status=200,
        gateway_ready_status=200,
        candidate_health_status=200,
        candidate_ready_status=200,
        models_status=200,
        models_visible_count=1,
        models_visible_expected=True,
        text_status=200,
        text_usage_total=10,
        stream_status=200,
        stream_event_types=("response.created", "response.output_text.delta", "response.completed"),
        stream_completed_usage=True,
        image_status=200,
        image_seen_delta=1,
        image_removed_delta=0,
        codex_version="0.149.0",
        codex_exit_status=0,
        codex_tool_calls=1,
        codex_dependency_reads=1,
        codex_sentinel_passed=True,
        codex_effective_governance=True,
        codex_public_request_count=2,
        compiler_attempt_delta=1,
        compiler_success_delta=1,
        compiler_added_gateway_rows=0,
        unauthorized_status=401,
        unauthorized_candidate_request_delta=0,
        over_quota_status=429,
        over_quota_candidate_request_delta=0,
        reservation_count=5,
        finalized_reservation_count=5,
        pending_reservation_count=0,
        ledger_count=5,
        finalized_ledger_count=5,
        failed_ledger_count=0,
        duplicate_request_id_count=0,
        provider_usage_rows=5,
        key_requests_used=5,
        key_requests_reserved=0,
        key_tokens_used=50,
        key_tokens_reserved=0,
        key_cost_used_eur="0.5",
        key_cost_reserved_eur="0",
        ledger_total_tokens=50,
        ledger_total_cost_eur="0.5",
        route_metadata_ok=True,
        gateway_key_not_forwarded=True,
        adapter_service_token_not_forwarded=True,
        qwen_credential_boundary_ok=True,
        compiler_not_accounted_as_public=True,
        gateway_logs_secret_free=True,
        candidate_logs_secret_free=True,
        candidate_listener_removed=True,
        gateway_listener_removed=True,
        postgres_container_removed=True,
        temporary_state_removed=True,
        protected_vision_pid_unchanged=True,
        protected_vision_start_unchanged=True,
        protected_vision_listener_unchanged=True,
        text_service_still_inactive=True,
        no_18021_listener=True,
        no_18031_listener=True,
    )


def test_rehearsal_contract_accepts_only_complete_content_free_facts() -> None:
    assert_gateway_rehearsal_facts(_passing_facts())
    with pytest.raises(AssertionError):
        assert_gateway_rehearsal_facts(replace(_passing_facts(), compiler_added_gateway_rows=1))


def test_rehearsal_contract_rejects_missing_stream_usage() -> None:
    with pytest.raises(AssertionError):
        assert_gateway_rehearsal_facts(replace(_passing_facts(), stream_completed_usage=False))

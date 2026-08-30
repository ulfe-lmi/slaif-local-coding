"""Content-free facts for the disposable Objective-005 gateway rehearsal."""

from __future__ import annotations

from dataclasses import dataclass

GATEWAY_MAIN_SHA = "306ecb186b5c12db991a684e7c04e5c9f174eba2"
PUBLIC_MODEL = "qwen3.8-27b"
UPSTREAM_MODEL = "qwen3.8-27b"
PROVIDER = "local-coding"
RESPONSES_ENDPOINT = "/v1/responses"


@dataclass(frozen=True)
class GatewayRehearsalFacts:
    """Safe facts retained from one full disposable boundary run."""

    gateway_sha: str
    gateway_checkout_clean_before: bool
    gateway_checkout_clean_after: bool
    postgres_image_preexisted: bool
    postgres_image_pulled: bool
    postgres_image_removed: bool
    postgres_tmpfs_only: bool
    gateway_health_status: int
    gateway_ready_status: int
    candidate_health_status: int
    candidate_ready_status: int
    models_status: int
    models_visible_count: int
    models_visible_expected: bool
    text_status: int
    text_usage_total: int
    stream_status: int
    stream_event_types: tuple[str, ...]
    stream_completed_usage: bool
    image_status: int
    image_seen_delta: int
    image_removed_delta: int
    codex_version: str
    codex_exit_status: int | None
    codex_tool_calls: int
    codex_dependency_reads: int
    codex_sentinel_passed: bool
    codex_effective_governance: bool
    codex_public_request_count: int
    compiler_attempt_delta: int
    compiler_success_delta: int
    compiler_added_gateway_rows: int
    unauthorized_status: int
    unauthorized_candidate_request_delta: int
    over_quota_status: int
    over_quota_candidate_request_delta: int
    reservation_count: int
    finalized_reservation_count: int
    pending_reservation_count: int
    ledger_count: int
    finalized_ledger_count: int
    failed_ledger_count: int
    duplicate_request_id_count: int
    provider_usage_rows: int
    key_requests_used: int
    key_requests_reserved: int
    key_tokens_used: int
    key_tokens_reserved: int
    key_cost_used_eur: str
    key_cost_reserved_eur: str
    ledger_total_tokens: int
    ledger_total_cost_eur: str
    route_metadata_ok: bool
    gateway_key_not_forwarded: bool
    adapter_service_token_not_forwarded: bool
    qwen_credential_boundary_ok: bool
    compiler_not_accounted_as_public: bool
    gateway_logs_secret_free: bool
    candidate_logs_secret_free: bool
    candidate_listener_removed: bool
    gateway_listener_removed: bool
    postgres_container_removed: bool
    temporary_state_removed: bool
    protected_vision_pid_unchanged: bool
    protected_vision_start_unchanged: bool
    protected_vision_listener_unchanged: bool
    text_service_still_inactive: bool
    no_18021_listener: bool
    no_18031_listener: bool


def assert_gateway_rehearsal_facts(facts: GatewayRehearsalFacts) -> None:
    """Assert the full bounded contract without inspecting raw payloads."""

    assert facts.gateway_sha == GATEWAY_MAIN_SHA
    assert facts.gateway_checkout_clean_before
    assert facts.gateway_checkout_clean_after
    assert not facts.postgres_image_preexisted
    assert facts.postgres_image_pulled
    assert facts.postgres_image_removed
    assert facts.postgres_tmpfs_only
    assert facts.gateway_health_status == 200
    assert facts.gateway_ready_status == 200
    assert facts.candidate_health_status == 200
    assert facts.candidate_ready_status == 200
    assert facts.models_status == 200
    assert facts.models_visible_count == 1
    assert facts.models_visible_expected
    assert facts.text_status == 200
    assert facts.text_usage_total > 0
    assert facts.stream_status == 200
    assert facts.stream_event_types
    assert facts.stream_event_types[-1] == "response.completed"
    assert facts.stream_completed_usage
    assert facts.image_status == 200
    assert facts.image_seen_delta == 1
    assert facts.image_removed_delta == 0
    assert facts.codex_version == "0.149.0"
    assert facts.codex_exit_status == 0
    assert facts.codex_tool_calls >= 1
    assert facts.codex_dependency_reads == 1
    assert facts.codex_sentinel_passed
    assert facts.codex_effective_governance
    assert facts.codex_public_request_count >= 1
    assert facts.compiler_attempt_delta > 0
    assert facts.compiler_success_delta >= 0
    assert facts.compiler_added_gateway_rows == 0
    assert facts.unauthorized_status in {401, 403}
    assert facts.unauthorized_candidate_request_delta == 0
    assert facts.over_quota_status in {402, 429}
    assert facts.over_quota_candidate_request_delta == 0
    assert facts.reservation_count == facts.ledger_count
    assert facts.finalized_reservation_count == facts.reservation_count
    assert facts.pending_reservation_count == 0
    assert facts.finalized_ledger_count == facts.ledger_count
    assert facts.failed_ledger_count == 0
    assert facts.duplicate_request_id_count == 0
    assert facts.provider_usage_rows == facts.ledger_count
    assert facts.key_requests_used == facts.ledger_count
    assert facts.key_requests_reserved == 0
    assert facts.key_tokens_used == facts.ledger_total_tokens
    assert facts.key_tokens_reserved == 0
    assert facts.key_cost_reserved_eur == "0"
    assert facts.ledger_total_tokens > 0
    assert facts.ledger_total_cost_eur != "0"
    assert facts.route_metadata_ok
    assert facts.gateway_key_not_forwarded
    assert facts.adapter_service_token_not_forwarded
    assert facts.qwen_credential_boundary_ok
    assert facts.compiler_not_accounted_as_public
    assert facts.gateway_logs_secret_free
    assert facts.candidate_logs_secret_free
    assert facts.candidate_listener_removed
    assert facts.gateway_listener_removed
    assert facts.postgres_container_removed
    assert facts.temporary_state_removed
    assert facts.protected_vision_pid_unchanged
    assert facts.protected_vision_start_unchanged
    assert facts.protected_vision_listener_unchanged
    assert facts.text_service_still_inactive
    assert facts.no_18021_listener
    assert facts.no_18031_listener

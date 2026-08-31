"""Content-free facts for the disposable Objective-005 gateway rehearsal."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

from scripts.local_qwen_provider_differential import (
    SSEFacts,
    _content_type_class,
    _status_class,
)

GATEWAY_MAIN_SHA = "2527030f5bbb90a7f0f354eb5347caee333ce4a7"
PUBLIC_MODEL = "qwen3.8-27b"
UPSTREAM_MODEL = "qwen3.8-27b"
PROVIDER = "local-coding"
RESPONSES_ENDPOINT = "/v1/responses"

STREAM_FAILURE_ORDER = (
    "http_status_non_2xx",
    "content_type_not_sse",
    "response_headers_timing_missing",
    "first_bytes_missing",
    "sse_unparseable",
    "event_vocabulary_unrecognized",
    "gateway_error_event",
    "response_created_missing_or_duplicate",
    "response_completed_missing_or_duplicate",
    "terminal_status_or_output_invalid",
    "terminal_usage_invalid",
    "response_id_mismatch",
    "normal_close_false",
    "terminal_or_close_timing_missing",
    "local_upstream_non_2xx_or_failure",
    "gateway_accounting_nonterminal",
    "stream_contract_passed",
)


def _count_class(value: int) -> str:
    if value < 0:
        return "unknown"
    if value <= 4:
        return str(value)
    if value <= 16:
        return "5-16"
    if value <= 64:
        return "17-64"
    return "65+"


def _byte_count_class(value: int) -> str:
    if value < 0:
        return "unknown"
    if value == 0:
        return "0"
    if value <= 128:
        return "1-128"
    if value <= 4_096:
        return "129-4096"
    if value <= 65_536:
        return "4097-65536"
    if value <= 1_048_576:
        return "65537-1048576"
    return "over_limit"


def _timing_value(timing: Mapping[str, str], name: str) -> str | None:
    value = timing.get(name)
    return value if isinstance(value, str) and value else None


@dataclass(frozen=True)
class ComposedStreamFacts:
    """Fixed-shape, content-free facts for one public composed stream."""

    status_class: str
    content_type_class: str
    response_headers_timing: str | None
    first_bytes_timing: str | None
    terminal_timing: str | None
    normal_close_timing: str | None
    byte_count_class: str
    chunk_count_class: str
    normal_close: bool
    parseable: bool
    recognized_vocabulary: bool
    error_event: bool
    gateway_error_event: bool
    duplicate_terminal: bool
    created_count_class: str
    completed_count_class: str
    response_id_relation: bool
    terminal_status_valid: bool
    terminal_output_valid: bool
    terminal_usage_valid: bool
    error_field_names: tuple[str, ...]
    error_code_class: str
    error_type_class: str
    local_request_delta: int
    local_stream_duration_delta: int
    local_failure_delta: int
    local_upstream_status_class: str
    local_stream_duration_bucket: str | None
    local_failure_class: str
    local_terminal_bytes: bool
    gateway_reservation_terminal: bool
    gateway_ledger_terminal: bool
    provider_call_count_class: str
    first_failure: str
    owner: str


def _first_failure(
    *,
    status_class: str,
    content_type_class: str,
    response_headers_timing: str | None,
    first_bytes: bool,
    parseable: bool,
    recognized_vocabulary: bool,
    gateway_error_event: bool,
    created_count: int,
    completed_count: int,
    terminal_status_valid: bool,
    terminal_output_valid: bool,
    terminal_usage_valid: bool,
    response_id_relation: bool,
    normal_close: bool,
    terminal_timing: str | None,
    normal_close_timing: str | None,
    local_upstream_status_class: str,
    local_failure_class: str,
    gateway_reservation_terminal: bool,
    gateway_ledger_terminal: bool,
) -> str:
    """Evaluate the ordered stream contract without collapsing failures."""
    if status_class != "2xx":
        return "http_status_non_2xx"
    if content_type_class != "sse":
        return "content_type_not_sse"
    if response_headers_timing is None:
        return "response_headers_timing_missing"
    if not first_bytes:
        return "first_bytes_missing"
    if not parseable:
        return "sse_unparseable"
    if not recognized_vocabulary:
        return "event_vocabulary_unrecognized"
    if gateway_error_event:
        return "gateway_error_event"
    if created_count != 1:
        return "response_created_missing_or_duplicate"
    if completed_count != 1:
        return "response_completed_missing_or_duplicate"
    if not terminal_status_valid or not terminal_output_valid:
        return "terminal_status_or_output_invalid"
    if not terminal_usage_valid:
        return "terminal_usage_invalid"
    if not response_id_relation:
        return "response_id_mismatch"
    if not normal_close:
        return "normal_close_false"
    if terminal_timing is None or normal_close_timing is None:
        return "terminal_or_close_timing_missing"
    if local_upstream_status_class != "2xx" or local_failure_class != "none":
        return "local_upstream_non_2xx_or_failure"
    if not gateway_reservation_terminal or not gateway_ledger_terminal:
        return "gateway_accounting_nonterminal"
    return "stream_contract_passed"


def _owner_for_failure(
    *,
    first_failure: str,
    status_class: str,
    local_upstream_status_class: str,
    local_failure_class: str,
    local_terminal_bytes: bool,
    driver_observation_failure: bool,
) -> str:
    if first_failure == "stream_contract_passed":
        return "stream_contract_passed"
    if driver_observation_failure and status_class == "2xx":
        return "acceptance_harness_owned"
    if (
        status_class == "2xx"
        and local_upstream_status_class == "2xx"
        and local_failure_class == "none"
        and local_terminal_bytes
        and first_failure
        in {
            "gateway_error_event",
            "response_created_missing_or_duplicate",
            "response_completed_missing_or_duplicate",
            "terminal_status_or_output_invalid",
            "terminal_usage_invalid",
            "response_id_mismatch",
            "normal_close_false",
            "terminal_or_close_timing_missing",
            "gateway_accounting_nonterminal",
        }
    ):
        return "gateway_stream_owned"
    if local_upstream_status_class != "2xx" or local_failure_class != "none":
        return "local_or_provider_owned"
    return "unresolved"


def build_composed_stream_facts(
    *,
    status: int | None,
    content_type: str | None,
    timing: Mapping[str, str],
    sse: SSEFacts,
    chunk_count: int,
    local_request_delta: int = 0,
    local_stream_duration_delta: int = 0,
    local_failure_delta: int = 0,
    local_upstream_status_class: str = "unknown",
    local_stream_duration_bucket: str | None = None,
    local_failure_class: str = "none",
    local_terminal_bytes: bool = False,
    gateway_reservation_terminal: bool = False,
    gateway_ledger_terminal: bool = False,
    provider_call_count: int = -1,
    driver_observation_failure: bool = False,
) -> ComposedStreamFacts:
    """Project the shared 005-j :class:`SSEFacts` into safe composed facts."""
    status_class = _status_class(status)
    content_type_class = _content_type_class(content_type)
    response_headers_timing = _timing_value(timing, "response_headers")
    first_bytes_timing = _timing_value(timing, "first_sse_bytes")
    terminal_timing = _timing_value(timing, "terminal_completion")
    normal_close_timing = _timing_value(timing, "normal_close")
    recognized_vocabulary = sse.parseable and not sse.unknown_events
    gateway_error_event = sse.event_counts.get("error", 0) > 0
    created_count = sse.event_counts.get("response.created", 0)
    completed_count = sse.event_counts.get("response.completed", 0)
    first_failure = _first_failure(
        status_class=status_class,
        content_type_class=content_type_class,
        response_headers_timing=response_headers_timing,
        first_bytes=sse.first_bytes,
        parseable=sse.parseable,
        recognized_vocabulary=recognized_vocabulary,
        gateway_error_event=gateway_error_event,
        created_count=created_count,
        completed_count=completed_count,
        terminal_status_valid=sse.completed_status_valid,
        terminal_output_valid=sse.completed_output_valid,
        terminal_usage_valid=sse.completed_usage_valid,
        response_id_relation=sse.response_id_relation,
        normal_close=sse.normal_close,
        terminal_timing=terminal_timing,
        normal_close_timing=normal_close_timing,
        local_upstream_status_class=local_upstream_status_class,
        local_failure_class=local_failure_class,
        gateway_reservation_terminal=gateway_reservation_terminal,
        gateway_ledger_terminal=gateway_ledger_terminal,
    )
    owner = _owner_for_failure(
        first_failure=first_failure,
        status_class=status_class,
        local_upstream_status_class=local_upstream_status_class,
        local_failure_class=local_failure_class,
        local_terminal_bytes=local_terminal_bytes,
        driver_observation_failure=driver_observation_failure,
    )
    return ComposedStreamFacts(
        status_class=status_class,
        content_type_class=content_type_class,
        response_headers_timing=response_headers_timing,
        first_bytes_timing=first_bytes_timing,
        terminal_timing=terminal_timing,
        normal_close_timing=normal_close_timing,
        byte_count_class=_byte_count_class(sse.byte_count),
        chunk_count_class=_count_class(chunk_count),
        normal_close=sse.normal_close,
        parseable=sse.parseable,
        recognized_vocabulary=recognized_vocabulary,
        error_event=sse.error_event,
        gateway_error_event=gateway_error_event,
        duplicate_terminal=sse.duplicates,
        created_count_class=_count_class(created_count),
        completed_count_class=_count_class(completed_count),
        response_id_relation=sse.response_id_relation,
        terminal_status_valid=sse.completed_status_valid,
        terminal_output_valid=sse.completed_output_valid,
        terminal_usage_valid=sse.completed_usage_valid,
        error_field_names=tuple(sorted(sse.error_field_names)),
        error_code_class=sse.error_code_class,
        error_type_class=sse.error_type_class,
        local_request_delta=max(0, local_request_delta),
        local_stream_duration_delta=max(0, local_stream_duration_delta),
        local_failure_delta=max(0, local_failure_delta),
        local_upstream_status_class=local_upstream_status_class,
        local_stream_duration_bucket=local_stream_duration_bucket,
        local_failure_class=local_failure_class,
        local_terminal_bytes=local_terminal_bytes,
        gateway_reservation_terminal=gateway_reservation_terminal,
        gateway_ledger_terminal=gateway_ledger_terminal,
        provider_call_count_class=_count_class(provider_call_count),
        first_failure=first_failure,
        owner=owner,
    )

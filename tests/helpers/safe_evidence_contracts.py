"""Explicit closed schemas for the sanitized Objective-005 acceptance results.

Every role schema in this module is defined from committed repository source
contracts: the runner literals and projection helpers in
``scripts/gateway_accounting_rehearsal.py`` (the Objective-005 tested source
``a71d61f0507911cb2b4bf4a76da431102da7f9c8`` and the AP37 implementation
``934388057af267b3bf39b2a2d1b56d34dfbd042f``),
``tests/helpers/transport_observer.py``,
``tests/helpers/acceptance_harness.py``,
``tests/helpers/vision_e2e_support.py``,
``tests/helpers/gateway_accounting_rehearsal.py`` and
``scripts/qwen_offline_replay_differential.py``.  Vocabulary sets are quoted
from those sources; shared constants are imported from
:mod:`tests.helpers.acceptance_harness` rather than re-declared, so the safe
evidence machinery keeps exactly one meaning of the acceptance vocabularies.

The module is large because it closes three distinct result families and
the 008-a post-hoc manifest, each with its own producer history:

* ``protected_target`` / ``fake_target`` — the identity-replay target
  result of the 005-ar implementation ``a71d61f...``: the runner's
  identity branch returns a 29-key document from inside the runner's
  ``try`` block.  Because Python executes ``finally`` during ``return``,
  the ``finally`` tail finalization runs before that return completes: it
  records the full nine-key ``cleanup_observation`` (so ``record_cleanup``
  is always called for committed target documents), records the listener
  and temporary-state cleanup facts (``gateway_listener_removed``,
  ``candidate_listener_removed``, ``temporary_state_removed``,
  ``logs_secret_free``) and, for protected runs, the protected-fixture
  invariance facts (``protected_unchanged``), then invokes
  ``finalize_result()`` through the ``early_return`` flag, which attaches
  ``aq_preflight``, ``runtime_observations``, ``target_gate``, the
  target-mode ``acceptance_gate``, and ``gap_inventory`` and rewrites the
  terminal ``status``.  The runner wrapper then attaches the accumulator
  evidence (``run_accumulator``, ``phase_checkpoints``,
  ``all_lifetime_counts``).  The committed document therefore carries
  exactly 43 top-level keys for both fake and protected runs (the fake
  document carries the ``NOT RUN`` preflight placeholders and the
  ``NOT_APPLICABLE_FAKE`` fixture fact).  Any key outside the closed 43 is
  an unknown-key rejection.  The closed ``aq_preflight`` sub-shapes are
  themselves source-derived: the protected document carries the real
  offline-replay, classifier, and nested fake-target qualification
  results; the fake document carries the ``NOT RUN`` placeholders.
* ``manifest`` — the 008-a post-hoc durable-preservation manifest.

The AP37 fake machine-gate result (63 top-level keys, implementation
``934388057af267b3bf39b2a2d1b56d34dfbd042f``) is *not* a supported export
role: its nested synthetic protected-case tree is not modeled by the closed
target schemas, and the material fake chain is durably preserved by the
005-ai 37/37 fake-machine-gate evidence, the immutable 005-ar report, and
the final isolated fake target.  The 008-a manifest therefore records the
AP37 authority as an existing optional source not retained under one fixed
content-free classification, and the historical audit classifies its exact
path by bounded stat-only preflight without reading or hashing its content.
``FULL_FAKE_GATE_SPEC`` remains defined only as a closed reference shape for
that artifact family; no export or audit path validates against it.

No schema, vocabulary, or bound in this module is derived from the historical
artifact values.  Candidate bytes may only be processed by the fail-closed
validator, which emits ``PASS`` or a fixed rejection class.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from tests.helpers.acceptance_harness import (
    _SAFE_ACCUMULATOR_FAILURES,
    _SAFE_OVERFLOW_SUBTYPES,
    FAKE_RESULT_SCHEMA_KEYS,
    PROTECTED_RESULT_SCHEMA_KEYS,
    SAFE_COUNT_CLASSES,
    SAFE_RELATIONSHIPS,
    SAFE_STATUSES,
    SAFE_TIMINGS,
    VALIDATION_STAGES,
)
from tests.helpers.safe_evidence import (
    MAX_SAFE_EVIDENCE_BYTES,
    BoolSpec,
    DictSpec,
    FloatSpec,
    IntSpec,
    ListSpec,
    NullSpec,
    OpenDictSpec,
    OpenValueSpec,
    PositionalListSpec,
    Spec,
    StrSpec,
    UnionSpec,
    _reject,
    dict_spec,
)

__all__ = [
    "ACCUMULATOR_FAILURE_CLASSES",
    "AP_FAKE_IMPLEMENTATION_SHA",
    "AP_FAKE_SOURCE_IDENTITY",
    "TARGET_RESULT_SCHEMA_NAME",
    "FULL_GATE_RESULT_SCHEMA_NAME",
    "CLASSIFIER_QUALIFICATION_PASSED_SPEC",
    "MANIFEST_SCHEMA",
    "OFFLINE_REPLAY_PASSED_SPEC",
    "PROTECTED_UNCHANGED_FACTS_SPEC",
    "PROTECTED_UNCHANGED_FAKE_LITERAL",
    "ROLES",
    "TARGET_GATE_SPEC",
    "ROLE_SCHEMAS",
    "RUNTIME_OBSERVATIONS_SPECS",
    "PREFLIGHT_SPEC",
    "MANIFEST_ACCEPTED_RELATIVE_PATHS",
    "MANIFEST_AUTHORITY_POSITIONS",
    "MANIFEST_AUTHORITY_ROLE_ORDER",
    "MANIFEST_HISTORICAL_AUTHORITY_SPEC",
    "MANIFEST_NOT_RETAINED_REASON",
    "MANIFEST_OPTIONAL_NOT_RETAINED",
    "MANIFEST_REJECTED_REJECTION_CLASSES",
    "MANIFEST_UNAVAILABLE_REJECTION",
    "CLEANUP_OBSERVATION_SPEC",
    "LIFETIME_IDS",
    "MANIFEST_REJECTION_CLASSES",
    "FULL_FAKE_GATE_SPEC",
    "build_runtime_observations_spec",
    "materialize_sample",
    "preflight_spec_for_role",
    "result_spec_for_role",
]

# --------------------------------------------------------------------------
# Pinned source constants
# --------------------------------------------------------------------------

GATEWAY_MAIN_SHA: str = "5ea38325ef3a3ebc69524b4679b795fab0c52935"
CODEX_VERSION: str = "0.149.0"
CODEX_FIXTURE_SHA256: str = "bbc3341e44c9ead340ed9570c17be936e37870f570751a941699ffd04d672827"
GATEWAY_APP_TREE_SHA256: str = "a7b64d35650b61fbba3558ddb519c6e52a627ec9"
LOCAL_ROUTE_POLICY: str = "qwen38-vision-codex/retain_newest/signed_identity_v1"
OBSERVATION_VERSION: str = "direct-httpx-v2"
LOCAL_SOURCE: str = "src/slaif_local_coding"
HARNESS_SOURCE: str = "scripts/gateway_accounting_rehearsal.py"
TARGET_IDENTITY_REPLAY: str = "identity_replay"
TARGET_FULL: str = "full"
AP_FAKE_IMPLEMENTATION_SHA: str = "934388057af267b3bf39b2a2d1b56d34dfbd042f"

#: The reviewed AP37 fake-authority source identity pinned by the current
#: runner (``AP_FAKE_SOURCE_IDENTITY``).
AP_FAKE_SOURCE_IDENTITY: Mapping[str, Mapping[str, str]] = {
    "paths": {
        "runner": "scripts/gateway_accounting_rehearsal.py",
        "observer": "tests/helpers/transport_observer.py",
        "projection": "tests/helpers/acceptance_harness.py",
        "provider_sse": "scripts/local_qwen_provider_differential.py",
    },
    "sha256": {
        "runner": "26855a5bf6e63e9aab1d32271949c20f1860bf78e07d391df1d338b69ffd7893",
        "observer": "75632bd850750d8a02a6a862cce8dd0e59d53c8e5c7d9a79b8acbdbf788dbec9",
        "projection": "62aa151ec2b7da973954aa8ff0f0d14f24f42ac99389e051888b71e0e7e12317",
        "provider_sse": "5b232d55b62723d1c706300fb240dbd23af687955930db2239cb7d82b2b681b0",
    },
    "loaded_module_paths": {
        "tests.helpers.acceptance_harness": "tests/helpers/acceptance_harness.py",
        "tests.helpers.transport_observer": "tests/helpers/transport_observer.py",
        "scripts.local_qwen_provider_differential": ("scripts/local_qwen_provider_differential.py"),
    },
    "loaded_module_sha256": {
        "tests.helpers.acceptance_harness": (
            "62aa151ec2b7da973954aa8ff0f0d14f24f42ac99389e051888b71e0e7e12317"
        ),
        "tests.helpers.transport_observer": (
            "75632bd850750d8a02a6a862cce8dd0e59d53c8e5c7d9a79b8acbdbf788dbec9"
        ),
        "scripts.local_qwen_provider_differential": (
            "5b232d55b62723d1c706300fb240dbd23af687955930db2239cb7d82b2b681b0"
        ),
    },
}

TARGET_RESULT_SCHEMA_NAME = "oap-safe-target-identity-replay-v1"
FULL_GATE_RESULT_SCHEMA_NAME = "oap-safe-full-fake-gate-v1"
MANIFEST_SCHEMA = "oap-008-a-durable-evidence-manifest-v1"

# --------------------------------------------------------------------------
# Fixed identifier patterns (source-derived shapes, not values)
# --------------------------------------------------------------------------

HEX40 = r"[0-9a-f]{40}"
HEX64 = r"[0-9a-f]{64}"
RUN_ID = r"[0-9a-f]{32}"
SYMBOL = r"[a-z0-9_]{1,64}"

#: Grammar class for top-level Codex CLI JSONL event type names emitted by
#: the pinned 0.149.0 fixture (e.g. ``thread.started``,
#: ``turn.completed``): dotted lowercase identifiers, 2-4 segments.  The
#: codex runner commits the raw sorted event-type names
#: (``tuple(sorted(run.event_type_counts))``), so the closed class here is
#: this grammar plus a bounded element count; free text, whitespace, and
#: path-like values never match.
CODEX_EVENT_TYPE = r"[a-z][a-z0-9_]*(\.[a-z][a-z0-9_]*){1,3}"
PHASE = r"[a-z0-9_]{1,32}"
PROVIDER_ERROR_PARAMS_PATTERN = None  # vocabulary below instead
DECIMAL_TEXT = r"[+-]?[0-9]+(\.[0-9]+)?"

# --------------------------------------------------------------------------
# Vocabularies (quoted from committed source)
# --------------------------------------------------------------------------

COUNT_CLASS: frozenset[str] = SAFE_COUNT_CLASSES
TIMING: frozenset[str] = SAFE_TIMINGS
STATUS: frozenset[str] = SAFE_STATUSES
RELATIONSHIP: frozenset[str] = SAFE_RELATIONSHIPS
ACCUMULATOR_FAILURE_CLASSES: frozenset[str] = _SAFE_ACCUMULATOR_FAILURES
OVERFLOW_SUBTYPES: frozenset[str] = _SAFE_OVERFLOW_SUBTYPES
VALIDATION_STAGE: frozenset[str] = VALIDATION_STAGES

OBS_STATUS_CLASS = frozenset({"1xx", "2xx", "3xx", "4xx", "5xx", "unknown"})
TARGET_STATUS_CLASS = frozenset({"unknown", "2xx", "4xx", "5xx", "other"})
CONTENT_TYPE_CLASS = frozenset({"sse", "json", "other", "unknown"})
CHUNK_COUNT_CLASS = frozenset({"0", "1", "2", "3", "4", "5-16", "17-64", "65+", "unknown"})
BYTE_COUNT_CLASS = frozenset(
    {"unknown", "0", "1-128", "129-4096", "4097-65536", "65537-1048576", "over_limit"}
)

EVENT_CLASSES: frozenset[str] = frozenset(
    {
        "response.created",
        "response.in_progress",
        "response.output_text.delta",
        "response.output_text.done",
        "response.output_item.added",
        "response.output_item.done",
        "response.function_call_arguments.delta",
        "response.function_call_arguments.done",
        "response.custom_tool_call_input.delta",
        "response.reasoning_summary_part.added",
        "response.reasoning_summary_text.delta",
        "response.reasoning_summary_text.done",
        "response.reasoning_text.delta",
        "response.reasoning_text.done",
        "response.reasoning_part.added",
        "response.reasoning_part.done",
        "response.content_part.added",
        "response.content_part.done",
        "response.completed",
        "error",
        "other",
    }
)

TARGET_EVENT_CLASSES: frozenset[str] = frozenset(
    {
        "response.created",
        "response.in_progress",
        "response.completed",
        "response.output_item.added",
        "response.output_item.done",
        "response.content_part.added",
        "response.content_part.done",
        "response.output_text.delta",
        "response.output_text.done",
        "response.reasoning_part.added",
        "response.reasoning_part.done",
        "response.reasoning_text.delta",
        "response.reasoning_text.done",
        "response.function_call_arguments.delta",
        "response.function_call_arguments.done",
        "error",
        "other",
    }
)

OBSERVER_EXCEPTION_CLASSES: frozenset[str] = frozenset(
    {
        "cancelled",
        "delegate_error",
        "stream_error",
        "validator_error",
        "observer_not_ready",
        "observer_bound_exceeded",
        "stream_framing_invalid",
        "stream_validation_invalid",
        "stream_overflow",
        "stream_closure_invalid",
        "stream_contract_invalid",
        "manual_unready",
        "observer_budget_not_admitted",
        "observer_lifetime_mismatch",
        "readiness_non_health",
        "provider_probe_endpoint_mismatch",
        "observer_dispatch_hook_error",
        "other",
    }
)

SNAPSHOT_FAILURE_CLASSES: frozenset[str] = (
    OBSERVER_EXCEPTION_CLASSES
    | {"observer_response_complete_hook_error"}
    | {name for name in _SAFE_ACCUMULATOR_FAILURES if name.startswith("budget_")}
)

TARGET_CAPTURE_FAILURE_CLASSES = frozenset({"framing", "validator", "validation", "overflow"})
TARGET_OBSERVER_EXCEPTION_CLASSES: frozenset[str] = frozenset(
    {
        "observer_budget_not_admitted",
        "observer_dispatch_hook_error",
        "observer_lifetime_mismatch",
        "observer_not_ready",
        "observer_bound_exceeded",
        "other_transport_error",
        "stream_closure_invalid",
        "stream_contract_invalid",
        "stream_error",
        "stream_framing_invalid",
        "stream_overflow",
        "stream_validation_invalid",
    }
)

ERROR_FIELD_NAMES = frozenset({"code", "message", "param", "request_id", "status", "type"})
ERROR_OWNER_CLASSES = frozenset({"unknown", "provider", "local", "gateway"})

ENDPOINT_CLASS = frozenset({"responses", "chat_completions", "health", "models", "other"})
REQUEST_CLASS = frozenset(
    {"function_initial", "function_continuation", "message", "image", "compiler", "unknown"}
)
TOOL_CLASS = frozenset({"function", "custom", "mixed", "none", "unknown"})
TOOL_TYPE_CLASSES = frozenset(
    {"function", "custom", "namespace", "tool_search", "web_search", "unknown"}
)
ITEM_ID_PRESENCE = frozenset({"present", "omitted", "unknown"})
#: ``image_hash_class`` of one fake-provider request observation, closed by
#: the producer's ``"present" if image_hashes else "none"``.
IMAGE_HASH_CLASS = frozenset({"present", "none"})
#: Closed fake-provider tool-name classes: the known local tool names plus
#: the fixed ``unknown``/``none`` sentinels of ``_request_observation``.
FAKE_TOOL_NAME_CLASSES = frozenset(
    {"shell_command", "exec_command", "local_shell", "local_lookup", "unknown", "none"}
)
CALL_ID_RELATION = frozenset({"initial_owned", "matching", "mismatched", "missing", "unknown"})
CANONICAL_AVAILABILITY = frozenset({"available", "none", "unknown"})
CANONICAL_SUMMARY = frozenset({"same", "different", "unknown"})
PENDING_SCOPE = frozenset({"available", "unavailable", "unknown"})
RECORD_KIND = frozenset({"compiler", "inference", "other"})

PROVIDER_ERROR_BODY_CLASSES = frozenset(
    {
        "complete",
        "empty",
        "malformed_json",
        "oversized",
        "top_level_not_object",
        "error_missing",
        "error_null",
        "error_wrong_type",
        "error_object",
        "read_error",
        "cancelled",
    }
)
PROVIDER_ERROR_TYPES = frozenset(
    {
        "invalid_request_error",
        "BadRequestError",
        "UnprocessableEntityError",
        "NotFoundError",
        "NotImplementedError",
        "InternalServerError",
        "Bad Request",
        "Unprocessable Entity",
        "Not Found",
        "Not Implemented",
        "Internal Server Error",
        "missing",
        "null",
        "unrecognized",
    }
)
PROVIDER_ERROR_CODES = frozenset(
    {
        "bad_request",
        "not_found",
        "unprocessable_entity",
        "too_many_requests",
        "internal_server_error",
        "not_implemented",
        "bad_gateway",
        "service_unavailable",
        "gateway_timeout",
        "integer_unrecognized",
        "missing",
        "null",
        "string_unrecognized",
        "boolean_unrecognized",
        "number_unrecognized",
        "array_unrecognized",
        "object_unrecognized",
    }
)
PROVIDER_ERROR_PARAMS = frozenset(
    {
        "background",
        "chat_template",
        "input",
        "logprobs",
        "max_output_tokens",
        "messages",
        "model",
        "previous_response_id",
        "prompt",
        "stream",
        "tool_choice",
        "tool_calls",
        "tools",
        "missing",
        "null",
        "string_unrecognized",
        "boolean_unrecognized",
        "integer_unrecognized",
        "number_unrecognized",
        "array_unrecognized",
        "object_unrecognized",
    }
)
PROVIDER_ERROR_FIELD_STATE_CLASSES = frozenset(
    {"missing", "null", "boolean", "integer", "number", "string", "array", "object", "other"}
)
PROVIDER_ERROR_RELATION = frozenset({"matching", "mismatched", "not_comparable"})

STREAM_FAILURE_ORDER: frozenset[str] = frozenset(
    {
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
        "provider_boundary_unobserved",
        "provider_lifecycle_invalid",
        "local_upstream_non_2xx_or_failure",
        "gateway_accounting_nonterminal",
        "stream_contract_passed",
    }
)
STREAM_OWNER_CLASSES = frozenset(
    {
        "stream_contract_passed",
        "gateway_product_defect",
        "gateway_rejected_stream_owner_unresolved",
        "local_or_provider_owned",
        "acceptance_harness_owned",
        "unresolved",
    }
)
GATEWAY_REJECTION_CODE_CLASS = frozenset({"unknown", "known_conflict"})
GATEWAY_REJECTION_STAGE = frozenset({"unknown", "provider_event_validation"})
LOCAL_FAILURE_CLASS = frozenset({"none", "upstream_error", "stream_error", "unavailable"})

TERMINAL_STATUS_CLASS = frozenset(
    {"null", "completed", "incomplete", "in_progress", "queued", "other"}
)
TERMINAL_INCOMPLETE_REASON_CLASS = frozenset(
    {"null", "max_output_tokens", "content_filter", "tool_error", "stop", "missing", "other"}
)
TERMINAL_OUTPUT_KIND_CLASSES = frozenset({"function_call", "message", "reasoning", "other"})
TERMINAL_ARGUMENT_CLASS = frozenset({"missing", "empty", "object", "other"})
TERMINAL_INTEGER_CLASS = COUNT_CLASS | {"invalid"}
TERMINAL_USAGE_FIELDS = frozenset(
    {
        "input_tokens",
        "input_tokens_details",
        "output_tokens",
        "output_tokens_details",
        "total_tokens",
    }
)
TERMINAL_OUTPUT_DETAILS_FIELDS = frozenset(
    {
        "reasoning_tokens",
        "tool_output_tokens",
        "output_tokens_per_turn",
        "tool_output_tokens_per_turn",
    }
)
TERMINAL_TRACE_FUNCTIONS = frozenset(
    {
        "validate",
        "_validate_codex_response_event",
        "_validate_response_completed_event",
        "_validate_completed_usage",
        "_validate_codex_completed_output",
        "_validate_codex_completed_output_item",
        "_accept_strict_sequence",
    }
)
TERMINAL_RETURN_CLASS = frozenset({"true", "false", "non_boolean"})

TARGET_FAILURE_CLASSES = frozenset(
    {
        "initial_http_non_2xx",
        "initial_stream_contract_failed",
        "continuation_http_non_2xx",
        "continuation_response_invalid",
        "identity_replay_predicate_failed",
    }
)

EXECUTION_MODES = frozenset({"fake", "synthetic-protected", "real-protected"})
RUN_PROVENANCE = frozenset(
    {
        "fresh_fake_direct_httpx_loopback",
        "fresh_synthetic_protected_direct_httpx_loopback",
        "fresh_real_protected_direct_httpx_qwen",
    }
)
SOURCE_IDENTITY_NAMES = frozenset({"runner", "observer", "projection", "provider_sse"})
LOADED_MODULE_NAMES = frozenset(
    {
        "tests.helpers.acceptance_harness",
        "tests.helpers.transport_observer",
        "scripts.local_qwen_provider_differential",
    }
)

SNAPSHOT_COUNT_NAMES = (
    "attempted_count",
    "dispatched_count",
    "responded_count",
    "completed_count",
    "terminal_valid_count",
    "compiler_attempted_count",
    "compiler_dispatched_count",
    "compiler_responded_count",
    "compiler_completed_count",
    "other_attempted_count",
    "other_dispatched_count",
    "other_responded_count",
    "other_completed_count",
    "other_terminal_valid_count",
    "inference_attempted_count",
    "inference_dispatched_count",
    "inference_responded_count",
    "inference_completed_count",
    "inference_terminal_valid_count",
    "inference_first_byte_count",
    "inference_normal_close_count",
)

ACCUMULATOR_COUNT_NAMES = (
    "compiler_attempted",
    "compiler_dispatched",
    "compiler_responded",
    "compiler_completed",
    "inference_attempted",
    "inference_dispatched",
    "inference_responded",
    "inference_completed",
    "compiler_terminal_valid",
    "inference_terminal_valid",
    "other_attempted",
    "other_dispatched",
    "other_responded",
    "other_completed",
    "other_terminal_valid",
)

CLEANUP_KEYS = (
    "processes",
    "listeners",
    "database",
    "cache",
    "codex_home",
    "failure_replay",
    "failure_cache",
    "failure_identity",
    "failure_provider",
)

CUTOVER_OBSERVATION_KEYS: tuple[str, ...] = (
    "cutover.capture_existence",
    "cutover.capture_hash",
    "cutover.capture_mode",
    "cutover.capture_owner",
    "cutover.capture_structure",
    "cutover.backup_0700",
    "cutover.backup_files_0600",
    "cutover.refuse_occupied_port",
    "cutover.refuse_collision",
    "cutover.refuse_unsafe_owner",
    "cutover.refuse_unsafe_mode",
    "cutover.refuse_overlap",
    "cutover.refuse_incomplete_backup",
    "cutover.refuse_unprovable_rollback",
    "cutover.local_18031",
    "cutover.gateway_18030",
    "cutover.protected_env",
    "cutover.signed_identity",
    "cutover.private_postgres",
    "cutover.hardened_unit",
    "cutover.profile_add_only",
    "cutover.active_profile_unchanged",
    "cutover.global_default_unchanged",
    "cutover.rollback_bytes",
    "cutover.rollback_mode",
    "cutover.rollback_owner",
    "cutover.rollback_hash",
    "cutover.rollback_absence",
    "cutover.absence_ports",
    "cutover.absence_processes",
    "cutover.absence_units",
    "cutover.absence_profile",
    "cutover.absence_cache",
    "cutover.absence_database",
    "cutover.absence_qwen",
    "cutover.absence_network",
    "cutover.failure_each_phase",
    "cutover.failure_exact_cleanup",
    "cutover.failure_rollback_incomplete",
    "cutover.checklist_tool_loop",
    "cutover.checklist_governance",
    "cutover.checklist_vision",
    "cutover.checklist_isolation",
    "cutover.checklist_quota",
    "cutover.checklist_no_bypass",
)
# Closed list of the exact observation facts emitted by the AP37 cutover
# projection; any other key is rejected.
assert len(CUTOVER_OBSERVATION_KEYS) == 45  # noqa: S101

VISION_REASON_LABELS: frozenset[str] = frozenset(
    {
        "session_mismatch",
        "catalog_image_capability",
        "catalog_detail_original",
        "catalog_context_window",
        "catalog_parallel_tools",
        "turn1_exit",
        "turn1_timeout",
        "turn1_events",
        "turn1_tool",
        "turn1_binding_effective",
        "turn2_exit",
        "turn2_timeout",
        "turn2_events",
        "turn2_tool",
        "turn2_binding_effective",
        "metrics_missing",
        "metrics_scaled_mismatch",
        "outbound_phase_grouping",
        "outbound_request_invalid",
    }
)
SAFE_EVENT_TYPES = frozenset({"thread.started", "item.completed", "other"})
SAFE_IMAGE_TYPES = frozenset({"input_image", "image_url", "unexpected"})
SAFE_OUTBOUND_LABELS = frozenset({"full_scene", "right_crop", "unexpected"})
TOOL_DEFINITION_TYPE_CATEGORIES = (
    "function",
    "custom",
    "tool_search",
    "web_search",
    "local_shell",
    "unexpected",
)
TOOL_ITEM_TYPE_CATEGORIES = (
    "function_call",
    "function_call_output",
    "custom_tool_call",
    "custom_tool_call_output",
    "local_shell_call",
    "local_shell_call_output",
    "command_execution",
    "exec_command",
    "unexpected",
)
FINAL_BINDING_PROVENANCE = frozenset(
    {
        "event_exact",
        "event_surrounding_crlf",
        "file_exact",
        "file_surrounding_crlf",
        "mismatch",
        "missing",
    }
)
FINAL_MESSAGE_WRAPPERS = frozenset(
    {
        "none",
        "inline_backticks",
        "double_quotes",
        "single_quotes",
        "asterisk_wrapper",
        "period_suffix",
        "period_then_crlf",
        "other_mismatch",
    }
)
FINAL_MESSAGE_PREFIXES = frozenset(
    {
        "none",
        "leading_crlf",
        "leading_lf_lf",
        "leading_cr_cr",
        "leading_space_space",
        "leading_tab_tab",
        "leading_dash_space",
        "leading_gt_space",
        "leading_hash_space",
        "leading_double_asterisk",
        "leading_double_backtick",
        "leading_double_quote",
        "leading_open_paren_space",
        "other_two_byte_prefix",
        "not_applicable",
    }
)

CODEX_FAILURE_REASONS = frozenset(
    {
        "unknown",
        "timeout",
        "empty_event_stream",
        "success",
        "process_boundary_error",
        "ordinary_tool_missing",
        "sentinel_missing",
        "command_failed",
        "command_incomplete",
    }
)
CODEX_FAILURE_ORIGINS = frozenset(
    {
        "unresolved_with_fixed_evidence",
        "model_wrong_command",
        "codex_command_execution",
        "wrapper_exit_translation",
        "success",
        "tool_unavailable",
        "event_parser",
        "codex_startup",
        "model_no_shell_call",
    }
)
CODEX_COMMAND_LIFECYCLE = frozenset({"success", "failed", "incomplete"})
CODEX_DIAGNOSTIC_CLASSES = frozenset(
    {
        "success",
        "not_found",
        "permission_denied",
        "sandbox_denied",
        "schema_invalid",
        "argv_unsupported",
        "signal",
        "timeout",
        "unknown_nonzero",
        "unavailable",
    }
)
#: ``stderr_class`` is the first-line diagnostic class of the pinned
#: Codex run: the closed ``DiagnosticFailureClass`` set of
#: ``tests/helpers/e2e_support.py`` (identical to
#: ``CODEX_DIAGNOSTIC_CLASSES``), or ``unavailable`` when the stream
#: facts are absent.
CODEX_STDERR_CLASS = frozenset(CODEX_DIAGNOSTIC_CLASSES)
CODEX_STDERR_SUBCLASS = frozenset(
    {"empty", "permission", "not_found", "argument", "configuration", "schema", "timeout", "other"}
)
CODEX_ERROR_MESSAGE_CLASSES = frozenset(
    {
        "none",
        "schema",
        "stream",
        "item",
        "response",
        "hosted_tool",
        "tool",
        "model",
        "configuration",
        "invalid_request",
        "unknown",
    }
)

PHASE_VOCAB = frozenset(
    {"preflight", "candidate", "codex", "vision", "identity", "cleanup", "finalize", "unknown"}
)

#: Closed lifetime identifiers the runner passes explicitly to every
#: ``capture_observer`` / ``record_phase_facts`` call in both producer
#: versions; derived ``phase:ordinal`` lifetimes are never used by the
#: committed runners.
LIFETIME_IDS: frozenset[str] = frozenset(
    {
        "preflight",
        "provider_preflight",
        "candidate",
        "identity",
        "codex",
        "vision",
        "post_vision",
        "merged",
    }
)
LIFETIME_ID = "|".join(sorted(LIFETIME_IDS))
TERMINAL_CLASSES = frozenset(
    {"terminal_valid", "terminal_invalid", "terminal_incomplete", "unknown"}
)
EVIDENCE_KIND = frozenset({"semantic", "transport", "unknown"})
SYNTHETIC_CASE_NAMES = (
    "healthy",
    "observer_failure_after_dispatch",
    "observer_projection_cleanup_failure",
    "predispatch_mapping_dependency_failure",
    "vision_failure_after_codex",
    "vision_failure_projection_cleanup",
)
DISPATCH_KINDS = frozenset({"compiler", "inference", "other", "readiness", "provider_probe"})
GAP_IDS = frozenset(
    {
        "direct_stream_before_codex",
        "provider_calls_from_ledger",
        "terminality_from_status_metrics",
        "fake_codex_not_run",
        "second_owner_literal",
        "replay_not_run",
        "incomplete_tamper_matrix",
        "missing_cutover_manifest",
        "passthrough_success_gate",
        "missing_rollback_failure_injection",
    }
)
OBLIGATION_PHASES = frozenset({"C1", "C2", "C3", "C4", "C5", "D"})
OBLIGATION_ID = r"[CD][0-9](\.[0-9])?"

# --------------------------------------------------------------------------
# Reusable spec helpers
# --------------------------------------------------------------------------

_BOOL = BoolSpec()
_NULL = NullSpec()


def _vocab(values: frozenset[str]) -> StrSpec:
    return StrSpec(vocabulary=values)


def _pattern(pattern: str) -> StrSpec:
    return StrSpec(pattern=pattern)


def _int(minimum: int = 0, maximum: int = 1_000_000) -> IntSpec:
    return IntSpec(minimum=minimum, maximum=maximum)


def _status_int() -> Spec:
    return UnionSpec((_int(100, 599), _NULL))


# --------------------------------------------------------------------------
# Provider error (main-era transport observer; additive after AP37)
# --------------------------------------------------------------------------

_FIELD_STATE_NAMES = frozenset({"code", "message", "param", "type"})

#: One fixed [field-name, json-value-class] pair.  The source emits the four
#: pairs in the fixed order (code, message, param, type); the closed
#: vocabularies constrain names and classes, and the bounded list length
#: constrains cardinality.
_FIELD_STATE_PAIR: ListSpec = ListSpec(
    UnionSpec((_vocab(_FIELD_STATE_NAMES), _vocab(PROVIDER_ERROR_FIELD_STATE_CLASSES))), 2
)

PROVIDER_ERROR_FIELD_STATES: Spec = UnionSpec((_NULL, ListSpec(_FIELD_STATE_PAIR, 4)))

PROVIDER_ERROR_SPEC: DictSpec = dict_spec(
    required=(
        ("http_status", _status_int()),
        ("body_class", _vocab(PROVIDER_ERROR_BODY_CLASSES)),
        ("received_bytes", _int()),
        ("accepted_bytes", _int()),
        ("rejected_bytes", _int()),
        ("rejected_chunk_count", _int()),
        ("field_states", PROVIDER_ERROR_FIELD_STATES),
        ("type_class", _vocab(PROVIDER_ERROR_TYPES)),
        ("code_class", _vocab(PROVIDER_ERROR_CODES)),
        ("param_class", _vocab(PROVIDER_ERROR_PARAMS)),
        ("code_status_relation", _vocab(PROVIDER_ERROR_RELATION)),
    ),
)

# --------------------------------------------------------------------------
# Transport observer record and provider boundary
# --------------------------------------------------------------------------

_REQUEST_FACTS_KEYS: tuple[tuple[str, Spec], ...] = (
    ("request_class", _vocab(REQUEST_CLASS)),
    ("tool_class", _vocab(TOOL_CLASS)),
    ("function_result_adjacent", _BOOL),
    ("item_id_presence", _vocab(ITEM_ID_PRESENCE)),
    ("call_id_relation", _vocab(CALL_ID_RELATION)),
    ("canonical_candidate_count_class", _vocab(COUNT_CLASS)),
    ("canonical_candidate_availability", _vocab(CANONICAL_AVAILABILITY)),
    ("canonical_summary_relation", _vocab(CANONICAL_SUMMARY)),
    ("pending_scope_available", _vocab(PENDING_SCOPE)),
    ("image_count_class", _vocab(COUNT_CLASS)),
    ("image_hashes", ListSpec(_pattern(HEX64), 8)),
    ("tool_type_classes", ListSpec(_vocab(TOOL_TYPE_CLASSES), 6)),
)

_DISPATCH_FACTS_KEYS: tuple[tuple[str, Spec], ...] = (
    ("dispatch_operation", _pattern(SYMBOL)),
    ("dispatch_phase", _pattern(SYMBOL)),
    ("dispatch_ordinal", UnionSpec((_int(), _NULL))),
    ("dispatch_lifetime", UnionSpec((_pattern(SYMBOL), _NULL))),
    ("dispatch_admitted", _BOOL),
)

RECORD_REQUIRED: tuple[tuple[str, Spec], ...] = (
    ("ordinal", _int(1, 1_000_000)),
    ("kind", _vocab(RECORD_KIND)),
    ("endpoint_class", _vocab(ENDPOINT_CLASS)),
    ("attempted", _BOOL),
    ("dispatched", _BOOL),
    ("responded", _BOOL),
    ("completed", _BOOL),
    ("status_class", _vocab(OBS_STATUS_CLASS)),
    ("content_type_class", _vocab(CONTENT_TYPE_CLASS)),
    ("first_byte", _BOOL),
    ("terminal_valid", _BOOL),
    ("normal_close", _BOOL),
    ("stream_bytes_class", _vocab(COUNT_CLASS)),
    ("response_received_bytes", _int()),
    ("response_accepted_bytes", _int()),
    ("response_rejected_bytes", _int()),
    ("response_rejected_chunk_count", _int()),
    ("event_count_class", _vocab(COUNT_CLASS)),
    ("event_type_classes", ListSpec(_vocab(EVENT_CLASSES), 32)),
    ("overflow_subtype", UnionSpec((_NULL, _vocab(OVERFLOW_SUBTYPES)))),
    ("overflow_observed", UnionSpec((_NULL, _int()))),
    ("overflow_bound", UnionSpec((_NULL, _int()))),
    (
        "exception_class",
        UnionSpec(
            (_NULL, _vocab(OBSERVER_EXCEPTION_CLASSES | {"observer_response_complete_hook_error"}))
        ),
    ),
)

RECORD_OPTIONAL: tuple[tuple[str, Spec], ...] = (
    (
        ("validation_stage", UnionSpec((_NULL, _vocab(VALIDATION_STAGE)))),
        ("failure_event_class", UnionSpec((_NULL, _vocab(EVENT_CLASSES)))),
        ("provider_error", UnionSpec((_NULL, PROVIDER_ERROR_SPEC))),
        ("lifetime_ordinal", _int(1, 1_000_000)),
    )
    + _REQUEST_FACTS_KEYS
    + _DISPATCH_FACTS_KEYS
)


def _record_spec(require_lifetime_ordinal: bool) -> DictSpec:
    if require_lifetime_ordinal:
        required = RECORD_REQUIRED + (("lifetime_ordinal", _int(1, 1_000_000)),)
        optional = tuple(item for item in RECORD_OPTIONAL if item[0] != "lifetime_ordinal")
    else:
        required = RECORD_REQUIRED
        optional = RECORD_OPTIONAL
    return dict_spec(required=required, optional=optional)


RECORD_SPEC: DictSpec = _record_spec(require_lifetime_ordinal=False)
MERGED_RECORD_SPEC: DictSpec = _record_spec(require_lifetime_ordinal=True)

PROVIDER_BOUNDARY_19: tuple[tuple[str, Spec], ...] = (
    ("call_count_class", _vocab(COUNT_CLASS)),
    ("lifecycle_valid", _BOOL),
    ("terminal_count_class", _vocab(COUNT_CLASS)),
    ("terminal", _BOOL),
    ("image_count_classes", ListSpec(_vocab(COUNT_CLASS), 64)),
    ("image_hash_count_class", _vocab(COUNT_CLASS)),
    ("all_image_requests_single", _BOOL),
    ("image_hashes_observed", _BOOL),
    ("tool_type_classes", ListSpec(_vocab(TOOL_TYPE_CLASSES), 6)),
    ("direct_gateway_rows", _int()),
    ("independent_from_ledger", _BOOL),
    ("request_class_classes", ListSpec(_vocab(REQUEST_CLASS), 6)),
    ("tool_class_classes", ListSpec(_vocab(TOOL_CLASS), 5)),
    ("function_result_adjacent", _BOOL),
    ("item_id_presence_classes", ListSpec(_vocab(ITEM_ID_PRESENCE), 3)),
    ("call_id_relation_classes", ListSpec(_vocab(CALL_ID_RELATION), 5)),
    (
        "compiler_inference_classes",
        ListSpec(_vocab(frozenset({"compiler", "inference"})), 2),
    ),
    ("normal_close_count_class", _vocab(COUNT_CLASS)),
    ("terminality_valid", _BOOL),
)

_CANONICAL_EXTRA_KEYS: tuple[tuple[str, Spec], ...] = (
    (
        "canonical_candidate_availability_classes",
        ListSpec(_vocab(CANONICAL_AVAILABILITY), 3),
    ),
    ("canonical_candidate_count_classes", ListSpec(_vocab(COUNT_CLASS), 64)),
    ("canonical_summary_relation_classes", ListSpec(_vocab(CANONICAL_SUMMARY), 3)),
    ("pending_scope_availability_classes", ListSpec(_vocab(PENDING_SCOPE), 3)),
    ("continuation_count_class", _vocab(COUNT_CLASS)),
)

PROVIDER_BOUNDARY_SPEC: DictSpec = dict_spec(required=PROVIDER_BOUNDARY_19)
#: Full observer boundary.  ``direct_gateway_rows`` is emitted by the
#: current observer projection and by the a71d61f committed documents but
#: is absent from the AP37-era boundary projection, so it is optional in
#: the closed shape; every other key is required.
PROVIDER_BOUNDARY_FULL_SPEC: DictSpec = dict_spec(
    required=tuple(
        item
        for item in PROVIDER_BOUNDARY_19 + _CANONICAL_EXTRA_KEYS
        if item[0] != "direct_gateway_rows"
    ),
    optional=(("direct_gateway_rows", _int()),),
)

# --------------------------------------------------------------------------
# Failure context and dispatch budget
# --------------------------------------------------------------------------

FAILURE_CONTEXT_SPEC: DictSpec = dict_spec(
    required=(
        ("kind", _pattern(SYMBOL)),
        ("operation", UnionSpec((_pattern(SYMBOL), _NULL))),
        ("phase", UnionSpec((_pattern(SYMBOL), _NULL))),
        ("ordinal", UnionSpec((_int(), _NULL))),
        ("lifetime_id", UnionSpec((_pattern(SYMBOL), _NULL))),
        ("cause", _vocab(SNAPSHOT_FAILURE_CLASSES)),
    ),
    optional=(
        ("overflow_subtype", _vocab(OVERFLOW_SUBTYPES)),
        ("overflow_observed", _int()),
        ("overflow_bound", _int()),
        ("validation_stage", _vocab(VALIDATION_STAGE)),
    ),
)

#: ``PUBLIC_REQUEST_BUDGET``: every public operation has maximum exactly
#: one logical attempt.
_OPERATION_LIMITS: DictSpec = dict_spec(
    required=tuple(
        (operation, _int(1, 1))
        for operation in (
            "codex_turn_1",
            "codex_turn_2",
            "vision_full",
            "vision_crop_history",
            "identity_replay",
            "identity_concurrent_replay",
            "identity_tamper_matrix",
            "authorization_matrix",
            "controlled_failure",
        )
    ),
)

#: The closed nine-operation public dispatch plan
#: (``PUBLIC_DISPATCH_PLAN``, tests/helpers/acceptance_harness.py),
#: including each operation's finite transport slots and its
#: ``phases()`` projection.  The budget controller always carries this
#: exact plan, so the committed shape is positional and fully pinned.
_DISPATCH_PLAN_PINNED: tuple[
    tuple[str, str, int, tuple[tuple[str, int], ...], tuple[str, ...]], ...
] = (
    ("codex_turn_1", "codex", 1, (("compiler", 2), ("inference", 1)), ("codex",)),
    ("codex_turn_2", "codex", 2, (("inference", 1),), ("codex",)),
    ("vision_full", "vision", 3, (("compiler", 2), ("inference", 2)), ("vision",)),
    ("vision_crop_history", "vision", 4, (("inference", 2),), ("vision",)),
    (
        "identity_replay",
        "codex",
        5,
        (("inference", 2), ("other", 5)),
        ("codex", "identity"),
    ),
    (
        "identity_concurrent_replay",
        "identity",
        6,
        (("compiler", 2), ("inference", 5)),
        ("identity",),
    ),
    ("identity_tamper_matrix", "identity", 7, (), ("identity",)),
    ("authorization_matrix", "identity", 8, (), ("identity",)),
    ("controlled_failure", "identity", 9, (("inference", 1),), ("identity",)),
)


def _dispatch_plan_entry_spec(
    operation: str,
    phase: str,
    ordinal: int,
    limits: tuple[tuple[str, int], ...],
    phases: tuple[str, ...],
) -> DictSpec:
    return dict_spec(
        required=(
            ("operation", StrSpec(vocabulary=frozenset({operation}))),
            ("phase", StrSpec(vocabulary=frozenset({phase}))),
            ("ordinal", _int(ordinal, ordinal)),
            (
                "dispatch_limits",
                dict_spec(
                    required=tuple((kind, _int(value, value)) for kind, value in limits),
                ),
            ),
            (
                "allowed_phases",
                PositionalListSpec(tuple(StrSpec(vocabulary=frozenset({name})) for name in phases)),
            ),
        )
    )


_DISPATCH_PLAN_SPEC: PositionalListSpec = PositionalListSpec(
    tuple(
        _dispatch_plan_entry_spec(operation, phase, ordinal, limits, phases)
        for operation, phase, ordinal, limits, phases in _DISPATCH_PLAN_PINNED
    )
)

_RESPONSE_BYTE_LIFETIME_ENTRY: DictSpec = dict_spec(
    required=(
        ("response_ordinal", _int()),
        ("received_bytes", _int()),
        ("accepted_bytes", _int()),
        ("rejected_bytes", _int()),
        ("rejected_chunk_count", _int()),
        ("configured_limit", _int()),
    ),
)

_DISPATCH_COUNTS_INNER: DictSpec = dict_spec(
    required=(
        ("attempted", _int()),
        ("admitted", _int()),
    ),
)

#: Closed admission kinds: the budget controller admits dispatches only for
#: these three kinds; any other kind is a budget failure, never a committed
#: record (tests/helpers/acceptance_harness.py ``admit_dispatch``).
DISPATCH_ADMISSION_KINDS: frozenset[str] = frozenset({"compiler", "inference", "other"})

#: Closed provider-probe endpoint/method pair; the controller reserves a
#: probe only for exactly this pair (``admit_provider_probe``).
PROVIDER_PROBE_ENDPOINTS: frozenset[str] = frozenset({"/health", "/v1/models"})
PROVIDER_PROBE_METHODS: frozenset[str] = frozenset({"GET"})

#: Closed dispatch-record operation names: the nine plan operations plus
#: the fixed probe/unknown operation names the controller records.
DISPATCH_RECORD_OPERATIONS: frozenset[str] = frozenset(
    {name for name, _phase, _ordinal, _limits, _phases in _DISPATCH_PLAN_PINNED}
    | {"unknown", "readiness_probe", "provider_probe"}
)

#: One budget dispatch record.  Base records carry kind/phase/ordinal/
#: admitted; admitted readiness, provider-probe, and operation records add
#: operation/lifetime_id, and provider-probe records additionally carry the
#: closed endpoint/method pair.  ``phase`` is the closed request-phase
#: vocabulary (``PHASE_VOCAB``); ``kind`` and ``operation`` are closed as
#: documented above.
_DISPATCH_RECORD_SPEC: DictSpec = dict_spec(
    required=(
        ("kind", _vocab(DISPATCH_ADMISSION_KINDS)),
        ("phase", _vocab(PHASE_VOCAB)),
        ("ordinal", UnionSpec((_int(), _NULL))),
        ("admitted", _BOOL),
    ),
    optional=(
        ("operation", _vocab(DISPATCH_RECORD_OPERATIONS)),
        ("lifetime_id", _pattern(LIFETIME_ID)),
        ("endpoint", _vocab(PROVIDER_PROBE_ENDPOINTS)),
        ("method", _vocab(PROVIDER_PROBE_METHODS)),
    ),
)

#: ``dispatch_counts`` maps the closed admission-kind set to
#: {attempted, admitted}: the controller commits exactly the kinds at
#: least attempted once (``sorted(self._dispatch_counts.items())``), so
#: each kind is optional and no other key is admissible.
_DISPATCH_COUNTS_SPEC: DictSpec = dict_spec(
    required=(),
    optional=tuple((kind, _DISPATCH_COUNTS_INNER) for kind in ("compiler", "inference", "other")),
)

BUDGET_SPEC: DictSpec = dict_spec(
    required=(
        ("wall_seconds", FloatSpec(minimum=0.0, maximum=1_000_000.0)),
        ("max_event_bytes", _int()),
        ("max_stream_bytes", _int()),
        ("max_concurrency", _int()),
        ("max_dispatches", _int()),
        ("max_readiness_probes", _int()),
        ("max_provider_preflight_probes", _int()),
        ("operation_limits", _OPERATION_LIMITS),
        ("dispatch_plan", _DISPATCH_PLAN_SPEC),
        ("wall_seconds_class", StrSpec(vocabulary=frozenset({"bounded"}))),
        ("operation_admitted_count_class", _vocab(COUNT_CLASS)),
        ("event_bytes_class", _vocab(COUNT_CLASS)),
        ("stream_bytes_class", _vocab(COUNT_CLASS)),
        ("stream_bytes_total", _int()),
        ("stream_bytes_total_class", _vocab(COUNT_CLASS)),
        ("response_received_bytes_total", _int()),
        ("response_accepted_bytes_total", _int()),
        ("response_rejected_bytes_total", _int()),
        ("response_rejected_chunks_total", _int()),
        ("response_active", _BOOL),
        ("response_byte_lifetimes", ListSpec(_RESPONSE_BYTE_LIFETIME_ENTRY, 16)),
        ("current_response_bytes", UnionSpec((_NULL, _RESPONSE_BYTE_LIFETIME_ENTRY))),
        ("active_concurrency_class", _vocab(COUNT_CLASS)),
        ("active_dispatch_class", _vocab(COUNT_CLASS)),
        ("dispatch_attempted_count", _int()),
        ("dispatch_admitted_count", _int()),
        (
            "active_context",
            UnionSpec(
                (
                    _NULL,
                    dict_spec(
                        required=(
                            ("operation", _pattern(SYMBOL)),
                            ("phase", _pattern(SYMBOL)),
                            ("ordinal", UnionSpec((_int(), _NULL))),
                            ("lifetime_id", UnionSpec((_pattern(SYMBOL), _NULL))),
                        ),
                        optional=(
                            ("endpoint", _vocab(PROVIDER_PROBE_ENDPOINTS)),
                            ("method", _vocab(PROVIDER_PROBE_METHODS)),
                        ),
                    ),
                )
            ),
        ),
        ("dispatch_attempted_count_class", _vocab(COUNT_CLASS)),
        ("dispatch_admitted_count_class", _vocab(COUNT_CLASS)),
        ("dispatch_counts", _DISPATCH_COUNTS_SPEC),
        ("dispatch_records", ListSpec(_DISPATCH_RECORD_SPEC, 128)),
        ("pending_permission_count", _int()),
        ("readiness_admitted_count", _int()),
        ("readiness_consumed_count", _int()),
        ("readiness_pending", _BOOL),
        ("provider_probe_admitted_count", _int()),
        ("provider_probe_consumed_count", _int()),
        ("provider_probe_pending", _BOOL),
        ("failure_class", UnionSpec((_NULL, _vocab(ACCUMULATOR_FAILURE_CLASSES)))),
        ("exhausted", _BOOL),
    ),
)

# --------------------------------------------------------------------------
# Observer snapshots (unmerged single lifetime; merged multi lifetime)
# --------------------------------------------------------------------------


def _snapshot_count_keys() -> tuple[tuple[str, Spec], ...]:
    counts = tuple((name, _int()) for name in SNAPSHOT_COUNT_NAMES)
    classes = tuple((f"{name}_class", _vocab(COUNT_CLASS)) for name in SNAPSHOT_COUNT_NAMES)
    return counts + classes


_SNAPSHOT_BASE: tuple[tuple[str, Spec], ...] = (
    (
        ("observer_version", StrSpec(vocabulary=frozenset({OBSERVATION_VERSION}))),
        (
            "validator_source",
            StrSpec(vocabulary=frozenset({"gateway_responses_stream_validator", "unavailable"})),
        ),
        ("ready", _BOOL),
        ("failure_class", UnionSpec((_NULL, _vocab(SNAPSHOT_FAILURE_CLASSES)))),
    )
    + _snapshot_count_keys()
    + (
        ("records", ListSpec(RECORD_SPEC, 64)),
        ("provider_boundary", PROVIDER_BOUNDARY_FULL_SPEC),
        ("elapsed_class", StrSpec(vocabulary=frozenset({"unknown", "bounded"}))),
    )
)

#: Unmerged single-lifetime snapshot (target-flow ``transport_observation``,
#: provider-preflight observer).  ``failure_context`` and ``dispatch_budget``
#: are present (possibly null) in the unmerged shape.
SNAPSHOT_SPEC: DictSpec = dict_spec(
    required=_SNAPSHOT_BASE
    + (
        ("failure_context", UnionSpec((_NULL, FAILURE_CONTEXT_SPEC))),
        ("dispatch_budget", UnionSpec((_NULL, BUDGET_SPEC))),
    )
)

#: Merged multi-lifetime snapshot (AP37 full-gate ``transport_observation``).
#: No ``failure_context`` / ``dispatch_budget``; records carry
#: ``lifetime_ordinal``; the runner adds five correlation facts on top.
MERGED_SNAPSHOT_SPEC: DictSpec = dict_spec(
    required=tuple(
        item
        for item in _SNAPSHOT_BASE
        if item[0] not in {"records", "provider_boundary", "elapsed_class"}
    )
    + (
        ("records", ListSpec(MERGED_RECORD_SPEC, 64)),
        ("provider_boundary", PROVIDER_BOUNDARY_FULL_SPEC),
        ("elapsed_class", StrSpec(vocabulary=frozenset({"bounded"}))),
    )
)

MERGED_TRANSPORT_EXTRA: tuple[tuple[str, Spec], ...] = (
    ("matches_fake_provider", _BOOL),
    ("provider_boundary_observed", _BOOL),
    (
        "phase_observations",
        ListSpec(
            dict_spec(
                required=(
                    ("attempted_count_class", _vocab(COUNT_CLASS)),
                    ("compiler_attempted_count_class", _vocab(COUNT_CLASS)),
                    ("inference_attempted_count_class", _vocab(COUNT_CLASS)),
                    (
                        "inference_terminal_valid_count_class",
                        _vocab(COUNT_CLASS),
                    ),
                    ("ready", _BOOL),
                ),
            ),
            16,
        ),
    ),
    ("fake_compiler_delta_class", _vocab(COUNT_CLASS)),
    ("fake_inference_delta_class", _vocab(COUNT_CLASS)),
)

MERGED_TRANSPORT_SPEC: DictSpec = dict_spec(
    required=MERGED_SNAPSHOT_SPEC.required + MERGED_TRANSPORT_EXTRA
)

# --------------------------------------------------------------------------
# Run accumulator
# --------------------------------------------------------------------------

_ACCUMULATOR_COUNTS_SPEC: DictSpec = dict_spec(
    required=tuple((name, UnionSpec((_NULL, _int()))) for name in ACCUMULATOR_COUNT_NAMES),
)

#: Per-lifetime count tables.  The producer
#: (``RunAccumulator.capture_observer``,
#: ``tests/helpers/acceptance_harness.py``) assigns
#: ``lifetime_counts[name]`` only when the observer snapshot provides
#: ``{name}_count`` as a non-negative integer, so every closed count name is
#: an observed (optional) key and, when present, carries the observed
#: non-negative integer.  This differs from ``counts`` /
#: ``all_lifetime_counts``, which the producer initializes with every closed
#: name and therefore carry all of them (null until observed).
_LIFETIME_COUNTS_SPEC: DictSpec = dict_spec(
    required=(),
    optional=tuple((name, _int()) for name in ACCUMULATOR_COUNT_NAMES),
)

_SNAPSHOT_ENTRY_SPEC: DictSpec = dict_spec(
    required=(
        ("lifetime_id", _pattern(LIFETIME_ID)),
        ("phase", _vocab(PHASE_VOCAB)),
        ("ordinal", UnionSpec((_int(), _NULL))),
        ("ready", _BOOL),
        ("failure_class", UnionSpec((_NULL, _vocab(ACCUMULATOR_FAILURE_CLASSES)))),
        ("failure_context", UnionSpec((_NULL, FAILURE_CONTEXT_SPEC))),
        ("completed", _BOOL),
        (
            "compiler_attempted_count",
            UnionSpec((_NULL, _int())),
        ),
        ("compiler_dispatched_count", UnionSpec((_NULL, _int()))),
        ("compiler_responded_count", UnionSpec((_NULL, _int()))),
        ("compiler_completed_count", UnionSpec((_NULL, _int()))),
        ("inference_attempted_count", UnionSpec((_NULL, _int()))),
        ("inference_dispatched_count", UnionSpec((_NULL, _int()))),
        ("inference_responded_count", UnionSpec((_NULL, _int()))),
        ("inference_completed_count", UnionSpec((_NULL, _int()))),
        ("compiler_terminal_valid_count", UnionSpec((_NULL, _int()))),
        ("inference_terminal_valid_count", UnionSpec((_NULL, _int()))),
    ),
)

_RESPONSE_BYTE_EVIDENCE_RESPONSE: DictSpec = dict_spec(
    required=(
        ("ordinal", UnionSpec((_int(), _NULL))),
        ("kind", _vocab(RECORD_KIND | {"unknown"})),
        ("received_bytes", _int()),
        ("accepted_bytes", _int()),
        ("rejected_bytes", _int()),
        ("rejected_chunk_count", _int()),
    ),
)

_RESPONSE_BYTE_EVIDENCE_SPEC: DictSpec = dict_spec(
    required=(
        ("lifetime_id", _pattern(LIFETIME_ID)),
        ("phase", _vocab(PHASE_VOCAB)),
        ("ordinal", UnionSpec((_int(), _NULL))),
        ("responses", ListSpec(_RESPONSE_BYTE_EVIDENCE_RESPONSE, 128)),
        (
            "all_lifetime",
            dict_spec(
                required=(),
                optional=tuple(
                    (
                        name,
                        _int(),
                    )
                    for name in (
                        "max_stream_bytes",
                        "response_received_bytes_total",
                        "response_accepted_bytes_total",
                        "response_rejected_bytes_total",
                        "response_rejected_chunks_total",
                        "stream_bytes_total",
                    )
                ),
            ),
        ),
    ),
)

_TERMINAL_OBSERVATION_SPEC: DictSpec = dict_spec(
    required=(
        ("lifetime", _pattern(SYMBOL)),
        ("ordinal", UnionSpec((_int(), _NULL))),
        ("terminal_class", _vocab(TERMINAL_CLASSES)),
        ("terminal_valid", UnionSpec((_BOOL, _NULL))),
    ),
)

#: Checkpoint ``counts`` carries only the lifetime count names actually
#: observed for that lifetime, each an observed count or ``null``.
CHECKPOINT_COUNTS_SPEC: DictSpec = dict_spec(
    required=(),
    optional=tuple((name, UnionSpec((_NULL, _int()))) for name in ACCUMULATOR_COUNT_NAMES),
)

#: Exact closed list of provider-boundary keys the runner may copy into a
#: phase checkpoint (``_CHECKPOINT_BOUNDARY_KEYS`` in
#: ``scripts/gateway_accounting_rehearsal.py``); each key is optional because
#: the projection copies only the keys present in the source snapshot.
_CHECKPOINT_BOUNDARY_OPTIONAL: tuple[tuple[str, Spec], ...] = (
    ("call_count_class", _vocab(COUNT_CLASS)),
    ("lifecycle_valid", _BOOL),
    ("terminal_count_class", _vocab(COUNT_CLASS)),
    ("terminal", _BOOL),
    ("image_count_classes", ListSpec(_vocab(COUNT_CLASS), 64)),
    ("image_hash_count_class", _vocab(COUNT_CLASS)),
    ("all_image_requests_single", _BOOL),
    ("image_hashes_observed", _BOOL),
    ("tool_type_classes", ListSpec(_vocab(TOOL_TYPE_CLASSES), 6)),
    ("independent_from_ledger", _BOOL),
    ("request_class_classes", ListSpec(_vocab(REQUEST_CLASS), 6)),
    ("tool_class_classes", ListSpec(_vocab(TOOL_CLASS), 5)),
    ("function_result_adjacent", _BOOL),
    ("item_id_presence_classes", ListSpec(_vocab(ITEM_ID_PRESENCE), 3)),
    ("call_id_relation_classes", ListSpec(_vocab(CALL_ID_RELATION), 5)),
    ("compiler_inference_classes", ListSpec(_vocab(frozenset({"compiler", "inference"})), 2)),
    ("normal_close_count_class", _vocab(COUNT_CLASS)),
    ("terminality_valid", _BOOL),
    ("canonical_candidate_availability_classes", ListSpec(_vocab(CANONICAL_AVAILABILITY), 3)),
    ("canonical_candidate_count_classes", ListSpec(_vocab(COUNT_CLASS), 64)),
    ("canonical_summary_relation_classes", ListSpec(_vocab(CANONICAL_SUMMARY), 3)),
    ("pending_scope_availability_classes", ListSpec(_vocab(PENDING_SCOPE), 3)),
    ("continuation_count_class", _vocab(COUNT_CLASS)),
)

CHECKPOINT_PROVIDER_BOUNDARY_SPEC: DictSpec = dict_spec(
    required=(), optional=_CHECKPOINT_BOUNDARY_OPTIONAL
)

#: Explicit closed projection of the runner's ``_codex_phase_checkpoint``
#: (``scripts/gateway_accounting_rehearsal.py``), as bounded by the
#: ``_safe_checkpoint_value`` serialization guard.  Sub-dictionaries that the
#: projection builds from optional source keys carry optional entries; the
#: projection itself always emits the six top-level keys.
_CODEX_PHASE_CLIENT_VERIFICATION_SPEC: DictSpec = dict_spec(
    required=(),
    optional=(
        ("status", _vocab(frozenset({"PASSED", "FAILED"}))),
        ("exit_status", _int()),
        ("failure_origin", _vocab(CODEX_FAILURE_ORIGINS)),
        ("sentinel_passed", _BOOL),
        ("command_lifecycle", _vocab(CODEX_COMMAND_LIFECYCLE)),
    ),
)

_CODEX_PHASE_ACCOUNTING_KEYS: tuple[str, ...] = (
    "two_terminal_reservations",
    "zero_pending",
    "zero_duplicate_request_ids",
    "request",
    "usage",
    "tokens",
    "cost",
)

PHASE_FACTS_SPEC: DictSpec = dict_spec(
    required=(
        ("evidence_kind", _vocab(EVIDENCE_KIND)),
        (
            "codex",
            dict_spec(
                required=(
                    ("status", _vocab(frozenset({"PASSED", "FAILED", "unknown"}))),
                    ("client_verification", _CODEX_PHASE_CLIENT_VERIFICATION_SPEC),
                    ("provider_inference_call_count", UnionSpec((_NULL, _int()))),
                    ("provider_turns_expected", UnionSpec((_NULL, _int()))),
                    ("exit_status", UnionSpec((_NULL, _int()))),
                    ("command_lifecycle", UnionSpec((_NULL, _vocab(CODEX_COMMAND_LIFECYCLE)))),
                    ("sentinel_passed", UnionSpec((_NULL, _BOOL))),
                    ("tool_call_count_class", UnionSpec((_NULL, _vocab(COUNT_CLASS)))),
                    ("dependency_hash_equal", UnionSpec((_NULL, _BOOL))),
                    ("dependency_length_equal", UnionSpec((_NULL, _BOOL))),
                    ("call_id_same_hmac", UnionSpec((_NULL, _BOOL))),
                    ("scope_no_downgrade", UnionSpec((_NULL, _BOOL))),
                ),
            ),
        ),
        (
            "provider_observation",
            dict_spec(
                required=(
                    ("provider_boundary", CHECKPOINT_PROVIDER_BOUNDARY_SPEC),
                    ("source", StrSpec(vocabulary=frozenset({"direct_transport_observer"}))),
                    ("fake_oracle", StrSpec(vocabulary=frozenset({"unavailable"}))),
                ),
            ),
        ),
        (
            "transport_observation",
            dict_spec(
                required=(
                    ("provider_boundary_observed", _BOOL),
                    ("matches_fake_provider", UnionSpec((_NULL, _BOOL))),
                ),
            ),
        ),
        (
            "accounting",
            dict_spec(
                required=(),
                optional=tuple(
                    (name, UnionSpec((_NULL, _BOOL))) for name in _CODEX_PHASE_ACCOUNTING_KEYS
                ),
            ),
        ),
        (
            "governance",
            dict_spec(
                required=(
                    ("dependency_one_equal", UnionSpec((_NULL, _BOOL))),
                    ("acquisition_before_completion", _BOOL),
                ),
            ),
        ),
    ),
)

CHECKPOINT_SPEC: DictSpec = dict_spec(
    required=(
        ("lifetime_id", _pattern(LIFETIME_ID)),
        ("phase", _vocab(PHASE_VOCAB)),
        ("ordinal", UnionSpec((_int(), _NULL))),
        ("completed", _BOOL),
        ("ready", _BOOL),
        ("failure_class", UnionSpec((_NULL, _vocab(ACCUMULATOR_FAILURE_CLASSES)))),
        ("counts", CHECKPOINT_COUNTS_SPEC),
        ("response_count", _int()),
    ),
    optional=(
        ("evidence_kind", _vocab(EVIDENCE_KIND)),
        ("phase_facts", PHASE_FACTS_SPEC),
    ),
)

RUN_ACCUMULATOR_SPEC: DictSpec = dict_spec(
    required=(
        ("mode", StrSpec(vocabulary=frozenset({"fake", "protected"}))),
        ("candidate_sha", UnionSpec((_NULL, _pattern(HEX40)))),
        ("gateway_sha", UnionSpec((_NULL, _pattern(HEX40)))),
        ("phase", _vocab(PHASE_VOCAB)),
        ("ordinal", UnionSpec((_int(), _NULL))),
        ("first_failure", UnionSpec((_NULL, _vocab(ACCUMULATOR_FAILURE_CLASSES)))),
        (
            "first_failure_context",
            UnionSpec((_NULL, FAILURE_CONTEXT_SPEC)),
        ),
        ("secondary_failures", ListSpec(_vocab(ACCUMULATOR_FAILURE_CLASSES), 4)),
        ("counts", _ACCUMULATOR_COUNTS_SPEC),
        ("all_lifetime_counts", _ACCUMULATOR_COUNTS_SPEC),
        (
            "lifetime_counts",
            OpenDictSpec(
                key_pattern=LIFETIME_ID,
                value=_LIFETIME_COUNTS_SPEC,
                maximum_keys=32,
            ),
        ),
        ("budget", BUDGET_SPEC),
        ("observer_failure_classes", ListSpec(_vocab(ACCUMULATOR_FAILURE_CLASSES), 16)),
        ("terminal_classes", ListSpec(_vocab(TERMINAL_CLASSES), 128)),
        ("terminal_observations", ListSpec(_TERMINAL_OBSERVATION_SPEC, 128)),
        ("phase_checkpoints", ListSpec(CHECKPOINT_SPEC, 64)),
        ("completed_phases", ListSpec(CHECKPOINT_SPEC, 64)),
        ("response_byte_evidence", ListSpec(_RESPONSE_BYTE_EVIDENCE_SPEC, 32)),
        ("snapshots", ListSpec(_SNAPSHOT_ENTRY_SPEC, 16)),
        (
            "cleanup",
            OpenDictSpec(
                key_pattern=(
                    "processes|listeners|database|cache|codex_home"
                    "|failure_replay|failure_cache|failure_identity|failure_provider"
                ),
                value=_BOOL,
                maximum_keys=9,
            ),
        ),
    ),
)

# --------------------------------------------------------------------------
# Terminal validation diagnostic (target flow)
# --------------------------------------------------------------------------

_TERMINAL_ARGUMENT_SPEC: DictSpec = dict_spec(
    required=(
        ("class", _vocab(TERMINAL_ARGUMENT_CLASS)),
        ("length_class", _vocab(COUNT_CLASS)),
    ),
)

_TERMINAL_SHAPE_SPEC: DictSpec = dict_spec(
    required=(
        ("status_class", _vocab(TERMINAL_STATUS_CLASS)),
        ("incomplete_reason_class", _vocab(TERMINAL_INCOMPLETE_REASON_CLASS)),
        ("output_shape", StrSpec(vocabulary=frozenset({"array", "not_array"}))),
        ("output_item_count_class", _vocab(COUNT_CLASS)),
        ("output_item_kind_classes", ListSpec(_vocab(TERMINAL_OUTPUT_KIND_CLASSES), 4)),
        ("function_item_count_class", _vocab(COUNT_CLASS)),
        ("function_item_id_present", _BOOL),
        ("function_call_id_matches", _BOOL),
        ("function_name_matches", _BOOL),
        ("function_arguments", _TERMINAL_ARGUMENT_SPEC),
        ("stream_arguments", _TERMINAL_ARGUMENT_SPEC),
        ("function_arguments_empty", _BOOL),
        ("function_arguments_matches", _BOOL),
        ("function_item_id_matches", _BOOL),
        ("usage_shape", StrSpec(vocabulary=frozenset({"object", "not_object"}))),
        ("usage_field_presence", ListSpec(_vocab(TERMINAL_USAGE_FIELDS), 5)),
        ("usage_required_integers", _BOOL),
        ("usage_output_token_count_class", _vocab(TERMINAL_INTEGER_CLASS)),
        ("usage_total_consistent", _BOOL),
        (
            "usage_output_details_fields",
            ListSpec(_vocab(TERMINAL_OUTPUT_DETAILS_FIELDS), 4),
        ),
        ("usage_output_per_turn_count_class", _vocab(COUNT_CLASS)),
        ("usage_tool_output_per_turn_count_class", _vocab(COUNT_CLASS)),
        ("usage_output_per_turn_lengths_equal", _BOOL),
        ("active_item_count_class", _vocab(COUNT_CLASS)),
        ("function_output_done_count_class", _vocab(COUNT_CLASS)),
        ("sequence_valid_before_call", _BOOL),
    ),
)

_TERMINAL_TRACE_SITE: DictSpec = dict_spec(
    required=(
        ("function", _vocab(TERMINAL_TRACE_FUNCTIONS)),
        ("return_line", _int()),
        ("return_class", _vocab(TERMINAL_RETURN_CLASS)),
    ),
)

_TERMINAL_INVOCATION: DictSpec = dict_spec(
    required=(
        ("shape_before", _TERMINAL_SHAPE_SPEC),
        ("shape_after", _TERMINAL_SHAPE_SPEC),
        ("validator_result_class", _vocab(TERMINAL_RETURN_CLASS)),
        (
            "exception_class",
            UnionSpec((_NULL, StrSpec(vocabulary=frozenset({"validator_exception"})))),
        ),
        ("trace_overflow", _BOOL),
        ("return_sites", ListSpec(_TERMINAL_TRACE_SITE, 256)),
    ),
)

TERMINAL_DIAGNOSTIC_SPEC: DictSpec = dict_spec(
    required=(
        ("enabled", _BOOL),
        ("invocation_count_class", _vocab(COUNT_CLASS)),
        ("invocations", ListSpec(_TERMINAL_INVOCATION, 32)),
    ),
)

NOT_RUN_SPEC: DictSpec = dict_spec(
    required=(("status", StrSpec(vocabulary=frozenset({"NOT RUN"}))),),
)

# --------------------------------------------------------------------------
# Target response facts, gate, companion, provenance
# --------------------------------------------------------------------------

_RESPONSE_ERROR_SPEC: DictSpec = dict_spec(
    required=(
        ("event", _BOOL),
        ("field_names", ListSpec(_vocab(ERROR_FIELD_NAMES), 6)),
        ("code_class", _vocab(ERROR_OWNER_CLASSES)),
        ("type_class", _vocab(ERROR_OWNER_CLASSES)),
        ("param_present", _BOOL),
    ),
    optional=(("provider", PROVIDER_ERROR_SPEC),),
)

_RESPONSE_VALIDATOR_SPEC: DictSpec = dict_spec(
    required=(
        (
            "failure_class",
            UnionSpec(
                (
                    _NULL,
                    _vocab(TARGET_CAPTURE_FAILURE_CLASSES | TARGET_OBSERVER_EXCEPTION_CLASSES),
                )
            ),
        ),
        ("validation_stage", UnionSpec((_NULL, _vocab(VALIDATION_STAGE)))),
        ("failed_event_class", UnionSpec((_NULL, _vocab(TARGET_EVENT_CLASSES)))),
    ),
)

RESPONSE_FACTS_SPEC: DictSpec = dict_spec(
    required=(
        ("status", _status_int()),
        ("error", _RESPONSE_ERROR_SPEC),
        ("validator", _RESPONSE_VALIDATOR_SPEC),
    ),
)

COMPANION_SPEC: DictSpec = dict_spec(
    required=(
        ("passed", _BOOL),
        ("operation", StrSpec(vocabulary=frozenset({TARGET_IDENTITY_REPLAY}))),
        ("phase", StrSpec(vocabulary=frozenset({"codex"}))),
        ("ordinal", _int(5, 5)),
        ("lifetime", StrSpec(vocabulary=frozenset({"identity"}))),
        ("request_count_class", _vocab(COUNT_CLASS)),
        (
            "initial_response_shape",
            StrSpec(vocabulary=frozenset({"stream_sse"})),
        ),
        (
            "continuation_response_shape",
            StrSpec(vocabulary=frozenset({"stream_sse"})),
        ),
        ("initial_status_class", _vocab(OBS_STATUS_CLASS)),
        ("continuation_status_class", _vocab(OBS_STATUS_CLASS)),
        ("returned_call_id_present", _BOOL),
        ("optional_item_id_omitted", _BOOL),
        ("mandatory_call_id_matching", _BOOL),
        ("canonical_replay_authority", _BOOL),
        ("canonical_candidate_availability", _vocab(CANONICAL_AVAILABILITY)),
        ("canonical_candidate_count_class", _vocab(COUNT_CLASS)),
        ("canonical_summary_relation", _vocab(CANONICAL_SUMMARY)),
        ("same_admitted_relationship", _BOOL),
        ("initial_terminal_valid", _BOOL),
        ("continuation_terminal_valid", _BOOL),
        ("accounting_terminal", _BOOL),
        ("natural_codex_shape_separate", _BOOL),
        ("gateway_call_id_same_hmac", _BOOL),
        ("scope_no_downgrade", _BOOL),
    ),
)

TARGET_ACCOUNTING_SPEC: DictSpec = dict_spec(
    required=(
        ("reservation_count_delta", _int()),
        ("finalized_reservation_count_delta", _int()),
        ("ledger_count_delta", _int()),
        ("finalized_ledger_count_delta", _int()),
        ("failed_ledger_count_delta", _int()),
        ("reservation_count_consistent", _BOOL),
        ("reservation_terminal", _BOOL),
        ("ledger_count_consistent", _BOOL),
        ("ledger_terminal", _BOOL),
        ("two_terminal_reservations", _BOOL),
        ("zero_pending", _BOOL),
        ("zero_duplicate_request_ids", _BOOL),
    ),
)

SOURCE_IDENTITY_SPEC: DictSpec = dict_spec(
    required=(
        (
            "paths",
            dict_spec(
                required=(
                    ("runner", _pattern("scripts/[a-z0-9_/]+\\.py")),
                    ("observer", _pattern("tests/helpers/[a-z0-9_]+\\.py")),
                    ("projection", _pattern("tests/helpers/[a-z0-9_]+\\.py")),
                    ("provider_sse", _pattern("scripts/[a-z0-9_/]+\\.py")),
                ),
            ),
        ),
        (
            "sha256",
            dict_spec(
                required=tuple(
                    (name, _pattern(HEX64))
                    for name in ("runner", "observer", "projection", "provider_sse")
                ),
            ),
        ),
        (
            "loaded_module_paths",
            dict_spec(
                required=tuple(
                    (name, _pattern("tests/helpers/[a-z0-9_]+\\.py"))
                    for name in sorted(LOADED_MODULE_NAMES)
                    if name.startswith("tests")
                )
                + (
                    (
                        "scripts.local_qwen_provider_differential",
                        _pattern("scripts/[a-z0-9_/]+\\.py"),
                    ),
                ),
            ),
        ),
        (
            "loaded_module_sha256",
            dict_spec(
                required=tuple((name, _pattern(HEX64)) for name in sorted(LOADED_MODULE_NAMES)),
            ),
        ),
    ),
)

CANDIDATE_PROVENANCE_SPEC: DictSpec = dict_spec(
    required=(
        ("implementation_sha", _pattern(HEX40)),
        ("tested_worktree_clean", _BOOL),
        ("local_source", StrSpec(vocabulary=frozenset({LOCAL_SOURCE}))),
        ("harness_source", StrSpec(vocabulary=frozenset({HARNESS_SOURCE}))),
        ("route_policy", StrSpec(vocabulary=frozenset({LOCAL_ROUTE_POLICY}))),
        ("gateway_sha", StrSpec(vocabulary=frozenset({GATEWAY_MAIN_SHA}))),
        (
            "gateway_app_tree_sha256",
            StrSpec(vocabulary=frozenset({GATEWAY_APP_TREE_SHA256})),
        ),
        ("codex_version", StrSpec(vocabulary=frozenset({CODEX_VERSION}))),
        (
            "codex_binary_sha256",
            StrSpec(vocabulary=frozenset({CODEX_FIXTURE_SHA256})),
        ),
        ("execution_mode", _vocab(EXECUTION_MODES)),
        ("run_provenance", _vocab(RUN_PROVENANCE)),
        ("run_id", _pattern(RUN_ID)),
        (
            "observer_version",
            StrSpec(vocabulary=frozenset({OBSERVATION_VERSION})),
        ),
        ("source_identity", SOURCE_IDENTITY_SPEC),
    ),
)

_FAKE_PROVIDER_OBSERVATION: DictSpec = dict_spec(
    required=(
        ("calls", _int()),
        ("inbound_inference_calls", _int()),
        ("inbound_compiler_calls", _int()),
        (
            "inbound_observations",
            ListSpec(
                dict_spec(
                    required=(
                        ("streaming", _BOOL),
                        ("image_count_class", _vocab(COUNT_CLASS)),
                        ("image_hash_class", _vocab(IMAGE_HASH_CLASS)),
                    ),
                    optional=(
                        ("request_class", _vocab(REQUEST_CLASS)),
                        ("tool_class", _vocab(TOOL_CLASS)),
                        ("tool_name_class", _vocab(FAKE_TOOL_NAME_CLASSES)),
                        ("item_id_presence", _vocab(ITEM_ID_PRESENCE)),
                        ("call_id_relation", _vocab(CALL_ID_RELATION)),
                    ),
                ),
                64,
            ),
        ),
        ("compiler_calls", _int()),
        ("inference_calls", _int()),
        ("stream_calls", _int()),
        ("tool_types", ListSpec(_vocab(TOOL_TYPE_CLASSES | frozenset({"unknown"})), 6)),
        ("tool_name_classes", ListSpec(_vocab(FAKE_TOOL_NAME_CLASSES), 6)),
        ("bad_auth", _BOOL),
        ("provider_oracle_available", _BOOL),
        ("provider_boundary", UnionSpec((_NULL, PROVIDER_BOUNDARY_SPEC))),
    ),
)

PROVIDER_OBSERVATION_SPEC: DictSpec = dict_spec(
    required=(
        ("provider_boundary", PROVIDER_BOUNDARY_FULL_SPEC),
        (
            "source",
            StrSpec(vocabulary=frozenset({"direct_transport_observer"})),
        ),
        (
            "fake_oracle",
            StrSpec(vocabulary=frozenset({"unavailable"})),
        ),
    ),
)

PROVIDER_PREFLIGHT_SPEC: DictSpec = dict_spec(
    required=(
        ("health_status", _status_int()),
        ("models_status", _status_int()),
        ("observer", UnionSpec((_NULL, SNAPSHOT_SPEC))),
        ("oracle_available", UnionSpec((_BOOL, _NULL))),
    ),
)

#: Final-manifest cleanup observation.  The runner records every cleanup
#: key in the ``finally`` tail that runs before any committed result is
#: returned — including the identity-replay early return (Python executes
#: ``finally`` during ``return``) — so every committed target and
#: full-gate document carries the complete nine-key observation.
CLEANUP_OBSERVATION_SPEC: DictSpec = dict_spec(
    required=tuple((name, _BOOL) for name in CLEANUP_KEYS),
)

CANDIDATE_ONLY_OBSERVATION_SPEC: DictSpec = dict_spec(
    required=(
        ("lifetime_id", StrSpec(vocabulary=frozenset({"candidate"}))),
        ("ready", _BOOL),
        ("failure_class", UnionSpec((_NULL, _vocab(SNAPSHOT_FAILURE_CLASSES)))),
        (
            "counts",
            dict_spec(
                required=tuple(
                    (name, UnionSpec((_NULL, _int())))
                    for name in (
                        "other_attempted",
                        "other_dispatched",
                        "other_responded",
                        "other_completed",
                        "other_terminal_valid",
                        "compiler_attempted",
                        "compiler_dispatched",
                        "inference_attempted",
                        "inference_dispatched",
                    )
                ),
            ),
        ),
    ),
)

TOPOLOGY_OBSERVATION_SPEC: DictSpec = dict_spec(
    required=(
        ("codex_gateway_local_provider", _BOOL),
        ("no_direct_route", _BOOL),
    ),
)

# --------------------------------------------------------------------------
# Role schemas: closed exports
#
# The role specs below compose only the source-grounded component specs
# defined earlier in this module plus the closed key sets re-imported from
# :mod:`tests.helpers.acceptance_harness` (``FAKE_RESULT_SCHEMA_KEYS`` and
# ``PROTECTED_RESULT_SCHEMA_KEYS``, used only for the exact
# runtime-observation dictionaries).  Every role schema is closed: an
# unknown top-level or nested key is a rejection, and a missing required
# key is a rejection.  ``materialize_sample`` produces fully valid
# synthetic documents for the closed schemas only; it never reads or
# derives values from historical artifacts.
#
# The identity-replay role specs close the exact 36-key document the
# a71d61f runner persists (module docstring); the full fake gate spec
# closes the 63-key AP37 document.  Every key outside these closed sets
# is a rejection.
# --------------------------------------------------------------------------

ROLES: frozenset[str] = frozenset({"protected_target", "fake_target", "manifest"})

ROLE_SCHEMAS: Mapping[str, str] = {
    "protected_target": TARGET_RESULT_SCHEMA_NAME,
    "fake_target": TARGET_RESULT_SCHEMA_NAME,
    "manifest": MANIFEST_SCHEMA,
}


def build_runtime_observations_spec(keys: Sequence[str]) -> DictSpec:
    """Closed spec for the exact runtime-observation dict.

    The producer (``_runtime_observations``) starts every closed key at
    ``None`` and only replaces it with a boolean when the underlying fact
    was observed (``put``), so each value is closed to bool-or-null.
    """
    if not keys or len(keys) != len(set(keys)):
        raise ValueError("runtime_observations_keys_invalid")
    return dict_spec(required=tuple((key, UnionSpec((_NULL, BoolSpec()))) for key in keys))


RUNTIME_OBSERVATIONS_SPECS: Mapping[str, DictSpec] = {
    "protected_target": build_runtime_observations_spec(PROTECTED_RESULT_SCHEMA_KEYS),
    "fake_target": build_runtime_observations_spec(FAKE_RESULT_SCHEMA_KEYS),
}

# --------------------------------------------------------------------------
# Preflight line (exact closed shape of the runner's PREFLIGHT line)
# --------------------------------------------------------------------------

PREFLIGHT_POLICY = frozenset({"ACCEPTED", "REJECTED"})
PREFLIGHT_TOOLS = frozenset({"NOT RUN_TARGET_SDK", "PRESENT", "UNKNOWN"})
PREFLIGHT_HOSTED = frozenset({"NOT RUN_TARGET_SDK", "ADAPTER_MANAGED", "PRESENT_OR_UNRESOLVED"})
TIMING_NAMES = frozenset(
    {"response_headers", "first_sse_bytes", "terminal_completion", "normal_close"}
)

PREFLIGHT_SPEC: DictSpec = dict_spec(
    required=(
        ("status", StrSpec(vocabulary=frozenset({"PREFLIGHT"}))),
        ("gateway_policy", _vocab(PREFLIGHT_POLICY)),
        ("ordinary_local_tools", _vocab(PREFLIGHT_TOOLS)),
        ("hosted_search_tools", _vocab(PREFLIGHT_HOSTED)),
        ("variant", _pattern(SYMBOL)),
        ("feature_flags", ListSpec(_pattern(SYMBOL), 16)),
        ("ignore_user_config", _BOOL),
        ("catalog_search_disabled", _BOOL),
        ("capture_count", _int()),
    ),
    optional=(
        ("ordinary_codex_execution", _BOOL),
        ("target", StrSpec(vocabulary=frozenset({TARGET_IDENTITY_REPLAY}))),
    ),
)


def preflight_spec_for_role(role: str) -> Spec | None:
    """Exact closed preflight-line spec for one role (manifest has none)."""
    if role not in ROLES:
        _reject("role_unknown")
    if role == "manifest":
        return None
    return PREFLIGHT_SPEC


# --------------------------------------------------------------------------
# Durable evidence manifest (Objective 008-a section B)
# --------------------------------------------------------------------------

MANIFEST_AUTHORITY_ROLES: frozenset[str] = frozenset(
    {
        "protected_final_1024_success",
        "protected_32_token_diagnostic",
        "fake_isolated_target",
        "fake_ap37_gate_authority",
    }
)
MANIFEST_AVAILABILITY: frozenset[str] = frozenset(
    {"accepted", "unavailable", "rejected", "optional_not_retained"}
)
MANIFEST_UNAVAILABLE_REJECTION: str = "historical_temp_artifact_unavailable_on_this_host"
#: Fixed content-free classification for the AP37 authority: the artifact
#: exists and passed the bounded stat-only preflight, but it is not retained
#: because the durable 005-ai 37/37 fake-machine-gate evidence, the immutable
#: 005-ar report, and the final isolated fake target already preserve the
#: material fake chain.  No hash, size, or content fact is recorded.
MANIFEST_OPTIONAL_NOT_RETAINED: str = "optional_not_retained"
#: Closed single-literal reason for the non-retention above.
MANIFEST_NOT_RETAINED_REASON: str = "redundant_with_durable_fake_chain_authorities"
#: The four closed authority roles in the exact manifest entry order.  A
#: manifest must carry exactly these four entries, one per role, each
#: under exactly one availability state (unique closed roles).
MANIFEST_AUTHORITY_ROLE_ORDER: tuple[str, ...] = (
    "protected_final_1024_success",
    "protected_32_token_diagnostic",
    "fake_isolated_target",
    "fake_ap37_gate_authority",
)
assert set(MANIFEST_AUTHORITY_ROLE_ORDER) == MANIFEST_AUTHORITY_ROLES
#: The exact repository-relative evidence destination each accepted
#: authority may claim.  Pinned literals: traversal, absolute, ``.`` and
#: ``..`` relative paths are rejected because they differ from the closed
#: literal.
MANIFEST_ACCEPTED_RELATIVE_PATHS: Mapping[str, str] = {
    "protected_final_1024_success": "005-ar/protected_final_1024_success.json",
    "protected_32_token_diagnostic": "005-ar/protected_32_token_diagnostic.json",
    "fake_isolated_target": "005-ar/fake_isolated_target_1024.json",
    "fake_ap37_gate_authority": "005-ar/fake_ap37_gate_authority.json",
}
assert set(MANIFEST_ACCEPTED_RELATIVE_PATHS) == MANIFEST_AUTHORITY_ROLES
#: Closed superset of every fixed rejection class the safe-evidence
#: machinery (``safe_evidence.py``) can emit, plus the availability class,
#: so the manifest can truthfully record any audit outcome.  Kept in sync
#: with the helper by ``tests/test_safe_evidence_export.py``.
MANIFEST_REJECTION_CLASSES: frozenset[str] = frozenset(
    {
        # availability
        "historical_temp_artifact_unavailable_on_this_host",
        # bounded source read
        "unsafe_path_relative",
        "unsafe_path_lexical",
        "unsafe_path_missing",
        "unsafe_path_unreadable",
        "unsafe_path_symlink",
        "unsafe_path_not_regular",
        "unsafe_path_foreign_owner",
        "unsafe_path_nlink",
        "unsafe_path_mode",
        "unsafe_path_size",
        "unsafe_path_component_type",
        # decoding
        "decode_duplicate_key",
        "decode_non_finite",
        "decode_invalid_json",
        "decode_not_object",
        "decode_empty",
        "decode_extra_lines",
        "decode_unvalidated_preflight_line",
        # privacy byte scan
        "privacy_pattern_bearer",
        "privacy_pattern_authorization",
        "privacy_pattern_api_key_prefix",
        "privacy_pattern_secret_field",
        "privacy_pattern_data_url",
        "privacy_pattern_private_url",
        "privacy_pattern_private_ip",
        "privacy_pattern_long_base64",
        "privacy_pattern_env_dump",
        "privacy_pattern_signature_nonce",
        # closed-shape validation
        "shape_type",
        "shape_int_range",
        "shape_float_finite",
        "shape_float_range",
        "shape_bool_value",
        "shape_string_value",
        "shape_key_unknown",
        "shape_key_missing",
        "shape_list_length",
        "shape_union",
        "shape_unsupported_spec",
        "open_dict_keys",
        "open_dict_key",
        "open_depth",
        "open_int_range",
        "open_float_range",
        "open_string_length",
        "open_string_grammar",
        "open_list_length",
        "open_type",
        "open_key_class_denied",
        # size
        "evidence_size_exceeded",
        # destination resolution
        "destination_empty",
        "destination_absolute",
        "destination_unsafe_path",
        "destination_traversal",
        "destination_component_count",
        "destination_component_name",
        "destination_root_missing",
        "destination_missing",
        "destination_unreadable",
        "destination_component_symlink",
        "destination_component_type",
        "destination_component_owner",
        "destination_component_writable",
        "destination_exists",
        "destination_symlink",
        # atomic write
        "destination_reservation_failed",
        "destination_temp_failed",
        "write_failed",
        "write_verification_failed",
        # export contract
        "role_unknown",
        "export_schema_mismatch",
        "export_mode_unknown",
        "export_spec_mismatch",
        "export_preflight_mismatch",
    }
)

#: Closed rejection classes for ``rejected`` manifest entries: every fixed
#: class the safe-evidence machinery can emit except the availability
#: class, which belongs exclusively to ``unavailable`` entries.
MANIFEST_REJECTED_REJECTION_CLASSES: frozenset[str] = MANIFEST_REJECTION_CLASSES - {
    MANIFEST_UNAVAILABLE_REJECTION
}


def _manifest_entry_accepted(role: str) -> DictSpec:
    """Accepted entry: non-null pinned path, both hashes, positive
    bounded byte count, null rejection class."""
    return dict_spec(
        required=(
            ("role", StrSpec(vocabulary=frozenset({role}))),
            ("availability", StrSpec(vocabulary=frozenset({"accepted"}))),
            ("rejection_class", _NULL),
            (
                "relative_path",
                StrSpec(vocabulary=frozenset({MANIFEST_ACCEPTED_RELATIVE_PATHS[role]})),
            ),
            ("original_sha256", _pattern(HEX64)),
            ("committed_sha256", _pattern(HEX64)),
            ("byte_count", _int(1, MAX_SAFE_EVIDENCE_BYTES)),
        )
    )


def _manifest_entry_unavailable(role: str) -> DictSpec:
    """Unavailable entry: null path/hashes/count, exact availability
    class."""
    return dict_spec(
        required=(
            ("role", StrSpec(vocabulary=frozenset({role}))),
            ("availability", StrSpec(vocabulary=frozenset({"unavailable"}))),
            (
                "rejection_class",
                StrSpec(vocabulary=frozenset({MANIFEST_UNAVAILABLE_REJECTION})),
            ),
            ("relative_path", _NULL),
            ("original_sha256", _NULL),
            ("committed_sha256", _NULL),
            ("byte_count", _NULL),
        )
    )


def _manifest_entry_rejected(role: str) -> DictSpec:
    """Rejected entry: null path/hashes/count, non-null closed rejection
    class."""
    return dict_spec(
        required=(
            ("role", StrSpec(vocabulary=frozenset({role}))),
            ("availability", StrSpec(vocabulary=frozenset({"rejected"}))),
            ("rejection_class", _vocab(MANIFEST_REJECTED_REJECTION_CLASSES)),
            ("relative_path", _NULL),
            ("original_sha256", _NULL),
            ("committed_sha256", _NULL),
            ("byte_count", _NULL),
        )
    )


def _manifest_entry_optional_not_retained(role: str) -> DictSpec:
    """Optional-not-retained entry: exact fixed classification, null
    path/hashes/count (no artifact hash or content fact is recorded)."""
    return dict_spec(
        required=(
            ("role", StrSpec(vocabulary=frozenset({role}))),
            (
                "availability",
                StrSpec(vocabulary=frozenset({MANIFEST_OPTIONAL_NOT_RETAINED})),
            ),
            ("rejection_class", _NULL),
            ("relative_path", _NULL),
            ("original_sha256", _NULL),
            ("committed_sha256", _NULL),
            ("byte_count", _NULL),
        )
    )


def _manifest_authority_position(role: str) -> UnionSpec:
    if role == "fake_ap37_gate_authority":
        # The AP37 authority is never accepted: no closed export schema
        # models its full synthetic protected-case tree, so the accepted
        # state is not part of its closed availability union.
        return UnionSpec(
            (
                _manifest_entry_unavailable(role),
                _manifest_entry_rejected(role),
                _manifest_entry_optional_not_retained(role),
            )
        )
    return UnionSpec(
        (
            _manifest_entry_accepted(role),
            _manifest_entry_unavailable(role),
            _manifest_entry_rejected(role),
        )
    )


#: Exactly four unique closed authority roles in fixed positions: one
#: entry per closed role, each under exactly one availability state.
MANIFEST_AUTHORITY_POSITIONS: PositionalListSpec = PositionalListSpec(
    tuple(_manifest_authority_position(role) for role in MANIFEST_AUTHORITY_ROLE_ORDER)
)

OBJECTIVE_005_MERGED_LOCAL_SHA: str = "e3f10e93c1ea84bf4021fd15d566bf577d5a9dcf"
OBJECTIVE_005_TESTED_LOCAL_SHA: str = "a71d61f0507911cb2b4bf4a76da431102da7f9c8"
OBJECTIVE_005_IMPLEMENTATION_PARENT_SHA: str = "c6519e35f9ee8e49681f7bec63ce122bf1118c8f"
OBJECTIVE_005_IMMUTABLE_REPORT_PATH: str = (
    "oap/reports/005-ar-terminal-stream-repair-and-closure.md"
)
OBJECTIVE_005_IMMUTABLE_REPORT_SHA: str = "e9829d84cc4116f749ddc8bc97b08fa37231e77f"

MANIFEST_HISTORICAL_AUTHORITY_SPEC: DictSpec = dict_spec(
    required=(
        (
            "objective_005_merged_local_sha",
            StrSpec(vocabulary=frozenset({OBJECTIVE_005_MERGED_LOCAL_SHA})),
        ),
        (
            "objective_005_tested_local_sha",
            StrSpec(vocabulary=frozenset({OBJECTIVE_005_TESTED_LOCAL_SHA})),
        ),
        (
            "objective_005_implementation_parent_sha",
            StrSpec(vocabulary=frozenset({OBJECTIVE_005_IMPLEMENTATION_PARENT_SHA})),
        ),
        (
            "objective_005_immutable_report_path",
            StrSpec(vocabulary=frozenset({OBJECTIVE_005_IMMUTABLE_REPORT_PATH})),
        ),
        (
            "objective_005_immutable_report_sha",
            StrSpec(vocabulary=frozenset({OBJECTIVE_005_IMMUTABLE_REPORT_SHA})),
        ),
        ("historical_gateway_sha", StrSpec(vocabulary=frozenset({GATEWAY_MAIN_SHA}))),
    ),
)

MANIFEST_SPEC: DictSpec = dict_spec(
    required=(
        ("schema", StrSpec(vocabulary=frozenset({MANIFEST_SCHEMA}))),
        (
            "classification",
            StrSpec(vocabulary=frozenset({"post_hoc_durable_preservation"})),
        ),
        ("preserved_during_objective_005", BoolSpec(False)),
        ("authorities", MANIFEST_AUTHORITY_POSITIONS),
        ("historical_authority", MANIFEST_HISTORICAL_AUTHORITY_SPEC),
        (
            "optional_not_retained",
            dict_spec(
                required=(
                    (
                        "role",
                        StrSpec(vocabulary=frozenset({"fake_ap37_gate_authority"})),
                    ),
                    (
                        "classification",
                        StrSpec(vocabulary=frozenset({MANIFEST_OPTIONAL_NOT_RETAINED})),
                    ),
                    (
                        "reason",
                        StrSpec(vocabulary=frozenset({MANIFEST_NOT_RETAINED_REASON})),
                    ),
                ),
            ),
        ),
        (
            "acceptance_relationship",
            dict_spec(
                required=(
                    (
                        "objective_005_acceptance",
                        StrSpec(vocabulary=frozenset({"accepted"})),
                    ),
                    (
                        "pr7_strategic_correction",
                        StrSpec(vocabulary=frozenset({"cited_not_rewritten"})),
                    ),
                ),
            ),
        ),
    ),
)
# --------------------------------------------------------------------------
# Full-gate sub-observations (source-grounded component shapes)
# --------------------------------------------------------------------------

#: Stream timing values are the closed timing-bucket vocabulary
#: (``SAFE_TIMINGS``), possibly null before the phase was observed.
_COMPOSED_STREAM_TIMING = UnionSpec((_NULL, _vocab(SAFE_TIMINGS)))

COMPOSED_STREAM_FACTS_SPEC: DictSpec = dict_spec(
    required=(
        ("status_class", _vocab(OBS_STATUS_CLASS)),
        ("content_type_class", _vocab(CONTENT_TYPE_CLASS)),
        ("response_headers_timing", _COMPOSED_STREAM_TIMING),
        ("first_bytes_timing", _COMPOSED_STREAM_TIMING),
        ("terminal_timing", _COMPOSED_STREAM_TIMING),
        ("normal_close_timing", _COMPOSED_STREAM_TIMING),
        ("byte_count_class", _vocab(BYTE_COUNT_CLASS)),
        ("chunk_count_class", _vocab(CHUNK_COUNT_CLASS)),
        ("normal_close", _BOOL),
        ("parseable", _BOOL),
        ("recognized_vocabulary", _BOOL),
        ("error_event", _BOOL),
        ("gateway_error_event", _BOOL),
        ("duplicate_terminal", _BOOL),
        ("created_count_class", _vocab(COUNT_CLASS)),
        ("completed_count_class", _vocab(COUNT_CLASS)),
        ("response_id_relation", _BOOL),
        ("terminal_status_valid", _BOOL),
        ("terminal_output_valid", _BOOL),
        ("terminal_usage_valid", _BOOL),
        ("error_field_names", ListSpec(_vocab(ERROR_FIELD_NAMES), 6)),
        ("error_code_class", _vocab(ERROR_OWNER_CLASSES)),
        ("error_type_class", _vocab(ERROR_OWNER_CLASSES)),
        ("local_request_delta", _int()),
        ("local_stream_duration_delta", _int()),
        ("local_failure_delta", _int()),
        ("local_upstream_status_class", _vocab(TARGET_STATUS_CLASS)),
        ("local_stream_duration_bucket", _COMPOSED_STREAM_TIMING),
        ("local_failure_class", _vocab(LOCAL_FAILURE_CLASS)),
        ("local_terminal_observed", _BOOL),
        ("gateway_reservation_terminal", _BOOL),
        ("gateway_ledger_terminal", _BOOL),
        ("provider_boundary_observed", _BOOL),
        ("provider_lifecycle_valid", _BOOL),
        ("provider_terminal", _BOOL),
        ("gateway_validator_contract_valid", _BOOL),
        ("gateway_rejection_code_class", _vocab(GATEWAY_REJECTION_CODE_CLASS)),
        ("gateway_rejection_stage", _vocab(GATEWAY_REJECTION_STAGE)),
        ("provider_call_count_class", _vocab(COUNT_CLASS)),
        ("first_failure", _vocab(STREAM_FAILURE_ORDER)),
        ("owner", _vocab(STREAM_OWNER_CLASSES)),
    ),
)

_CLIENT_VERIFICATION_SPEC: DictSpec = dict_spec(
    required=(
        ("status", StrSpec(vocabulary=frozenset({"PASSED", "FAILED"}))),
        ("exit_status", _int()),
        ("failure_origin", _vocab(CODEX_FAILURE_ORIGINS)),
        ("failure_reason", _vocab(CODEX_FAILURE_REASONS)),
        ("sentinel_passed", _BOOL),
        ("command_lifecycle", _vocab(CODEX_COMMAND_LIFECYCLE)),
    ),
)

#: One ``ConstitutionMetricsSnapshot`` projection
#: (``tests/helpers/e2e_support.py``): exactly the twelve fixed Prometheus
#: counter reads, each a non-negative finite float.
CONSTITUTION_METRIC_SNAPSHOT_SPEC: DictSpec = dict_spec(
    required=tuple(
        (name, FloatSpec(minimum=0.0, maximum=1_000_000.0))
        for name in (
            "root_observations",
            "dependency_observations",
            "dependency_cache_misses",
            "dependency_cache_hits",
            "dependency_invalid",
            "dependency_budget_exceeded",
            "compiler_calls",
            "compiler_attempts",
            "injected_requests",
            "working_set_included",
            "working_set_missing",
            "working_set_omitted",
        )
    ),
)

#: ``constitution_metrics``: the before/after snapshot pair the AP37
#: producer attaches to the codex facts.
CONSTITUTION_METRICS_SPEC: DictSpec = dict_spec(
    required=(
        ("before", CONSTITUTION_METRIC_SNAPSHOT_SPEC),
        ("after", CONSTITUTION_METRIC_SNAPSHOT_SPEC),
    ),
)

#: Gateway accounting deltas the AP37 producer attaches to the codex facts
#: (``codex_rows_after`` vs ``codex_rows_before`` comparisons).
CODEX_ACCOUNTING_SPEC: DictSpec = dict_spec(
    required=tuple(
        (name, _BOOL)
        for name in (
            "two_terminal_reservations",
            "zero_pending",
            "zero_duplicate_request_ids",
            "request",
            "usage",
            "tokens",
            "cost",
        )
    ),
)

#: The committed codex facts.  The base facts come from the pinned Codex
#: run projection; the eight keys after ``dependency_length_equal`` are the
#: fixed ``codex_facts.update`` additions of the AP37 producer
#: (``provider_inference_call_count``, ``transport_observation``,
#: ``transport_dispatch_matches_fake``, ``call_id_same_hmac``,
#: ``scope_no_downgrade``, ``constitution_metrics``, ``accounting``,
#: ``local_observation_status``) and are always present in a committed
#: full-gate document.  ``event_type_classes`` carries the raw sorted
#: top-level event type names (grammar-closed); ``error_code_class`` is the
#: closed ``parse_codex_error_facts`` code family (identical to
#: ``CODEX_ERROR_MESSAGE_CLASSES``); ``stderr_class`` is the closed
#: first-line diagnostic class.
CODEX_FACTS_SPEC: DictSpec = dict_spec(
    required=(
        ("status", StrSpec(vocabulary=frozenset({"PASSED", "FAILED"}))),
        ("client_verification", _CLIENT_VERIFICATION_SPEC),
        ("version", StrSpec(vocabulary=frozenset({CODEX_VERSION}))),
        ("binary_sha256", StrSpec(vocabulary=frozenset({CODEX_FIXTURE_SHA256}))),
        ("exit_status", _int()),
        ("tool_call_count_class", _vocab(COUNT_CLASS)),
        ("dependency_read_count_class", _vocab(COUNT_CLASS)),
        ("sentinel_passed", _BOOL),
        ("command_lifecycle", _vocab(CODEX_COMMAND_LIFECYCLE)),
        ("failure_reason", _vocab(CODEX_FAILURE_REASONS)),
        ("failure_origin", _vocab(CODEX_FAILURE_ORIGINS)),
        ("diagnostic_class", _vocab(CODEX_DIAGNOSTIC_CLASSES)),
        ("stderr_class", _vocab(CODEX_STDERR_CLASS)),
        ("stderr_subclass", _vocab(CODEX_STDERR_SUBCLASS)),
        ("event_count_class", _vocab(COUNT_CLASS)),
        ("event_type_classes", ListSpec(_pattern(CODEX_EVENT_TYPE), 16)),
        ("parser_recognized_event_count_class", _vocab(COUNT_CLASS)),
        ("error_field_names", ListSpec(_vocab(ERROR_FIELD_NAMES), 6)),
        ("error_code_class", _vocab(CODEX_ERROR_MESSAGE_CLASSES)),
        ("error_message_classes", ListSpec(_vocab(CODEX_ERROR_MESSAGE_CLASSES), 8)),
        ("provider_turns_expected", _int()),
        ("retry_count", _int()),
        ("dependency_hash_equal", _BOOL),
        ("dependency_length_equal", _BOOL),
        ("provider_inference_call_count", _int()),
        ("transport_observation", SNAPSHOT_SPEC),
        ("transport_dispatch_matches_fake", _BOOL),
        ("call_id_same_hmac", _BOOL),
        ("scope_no_downgrade", _BOOL),
        ("constitution_metrics", CONSTITUTION_METRICS_SPEC),
        ("accounting", CODEX_ACCOUNTING_SPEC),
        ("local_observation_status", StrSpec(vocabulary=frozenset({"PASSED", "FAILED"}))),
    ),
)

_CUTOVER_REFUSAL_FACTS_SPEC: DictSpec = dict_spec(
    required=tuple(
        (name, _BOOL)
        for name in (
            "occupied_port",
            "collision",
            "unsafe_owner",
            "unsafe_mode",
            "overlap",
            "incomplete_backup",
            "rollback_unprovable",
        )
    ),
)

CUTOVER_RUNNER_FACTS_SPEC: DictSpec = dict_spec(
    required=(
        ("local_port", _int()),
        ("gateway_port", _int()),
        ("private_bind", _BOOL),
        ("signed_identity", _BOOL),
        ("protected_env_reference", _BOOL),
        ("private_postgres", _BOOL),
        ("hardened_units", _BOOL),
        ("dedicated_profile", _BOOL),
        ("active_profile_unchanged", _BOOL),
        ("global_default_unchanged", _BOOL),
        ("backup_mode", StrSpec(vocabulary=frozenset({"0700"}))),
        ("backup_file_mode", StrSpec(vocabulary=frozenset({"0600"}))),
        ("installed", _BOOL),
        ("captured", _BOOL),
        ("rollback_incomplete", _BOOL),
        ("event_count_class", _vocab(COUNT_CLASS)),
        ("refusal_facts", _CUTOVER_REFUSAL_FACTS_SPEC),
    ),
)

CUTOVER_OBSERVATIONS_SPEC: DictSpec = dict_spec(
    required=tuple((name, _BOOL) for name in CUTOVER_OBSERVATION_KEYS),
)

CUTOVER_FACTS_SPEC: DictSpec = dict_spec(
    required=(
        ("passed", _BOOL),
        ("injected_failure_count_class", _vocab(COUNT_CLASS)),
        ("runner", CUTOVER_RUNNER_FACTS_SPEC),
        ("observations", CUTOVER_OBSERVATIONS_SPEC),
    ),
)

CONSTITUTION_OBSERVATION_SPEC: DictSpec = dict_spec(
    required=tuple(
        (name, _BOOL)
        for name in (
            "root_observed",
            "dependency_one_equal",
            "acquisition_before_completion",
            "candidates_observed",
            "compiler_miss",
            "validated_cache",
            "injection_observed",
            "zero_root",
            "cache_reuse",
            "no_compiler",
            "compiler_public_rows_unchanged",
        )
    ),
)

IDENTITY_MATRIX_SPEC: DictSpec = dict_spec(
    required=tuple(
        (name, _BOOL)
        for name in (
            "every_admission_verified",
            "same_session",
            "different_session",
            "different_owner",
            "different_repository",
            "replay_one_accept",
            "replay_no_provider_duplicate",
            "replay_no_accounting_duplicate",
            "tamper_body",
            "tamper_query",
            "tamper_path",
            "tamper_route",
            "tamper_signature",
            "tamper_timestamp",
            "tamper_nonce",
            "tamper_ambiguous",
            "tamper_missing",
            "concurrent_one_accept",
            "pre_provider",
        )
    ),
)

ISOLATION_OBSERVATION_SPEC: DictSpec = dict_spec(
    required=tuple(
        (f"{dimension}_{qualifier}", _BOOL)
        for dimension in ("session", "owner", "repository")
        for qualifier in ("negative", "distinct")
    ),
)

GATEWAY_REJECTS_SPEC: DictSpec = dict_spec(
    required=tuple(
        (name, _BOOL)
        for name in ("invalid_key", "hosted_choice", "dropped_tool", "over_quota", "pre_provider")
    ),
)

FAILURE_OBSERVATION_SPEC: DictSpec = dict_spec(
    required=tuple(
        (name, _BOOL) for name in ("one_provider_call", "terminal_accounting", "no_unrelated_call")
    ),
)

COMPILER_OBSERVATION_SPEC: DictSpec = dict_spec(
    required=tuple(
        (name, _BOOL) for name in ("zero_public_rows", "zero_public_fees", "zero_public_fence")
    ),
)

FAKE_IDLESS_HTTP_REGRESSION_SPEC: DictSpec = dict_spec(
    required=(
        ("passed", _BOOL),
        ("request_count_class", _vocab(COUNT_CLASS)),
        ("status_classes", ListSpec(_vocab(OBS_STATUS_CLASS), 8)),
        ("orphan_after_initial_rejected", _BOOL),
        ("orphan_fresh_rejected", _BOOL),
        ("idless_item_observed", _BOOL),
        ("matching_call_id_observed", _BOOL),
        ("lifecycle_valid", _BOOL),
        ("terminality_valid", _BOOL),
    ),
)

REPLAY_OWNERSHIP_NEGATIVE_SPEC: DictSpec = dict_spec(
    required=(
        ("passed", _BOOL),
        ("scope", StrSpec(vocabulary=frozenset({"gateway_responses_companion"}))),
        ("request_count_class", _vocab(COUNT_CLASS)),
        ("missing_call_id_status_class", _vocab(OBS_STATUS_CLASS)),
        ("mismatched_call_id_status_class", _vocab(OBS_STATUS_CLASS)),
        ("wrong_key_status_class", _vocab(OBS_STATUS_CLASS)),
        ("all_denied", _BOOL),
        ("provider_calls_unchanged", _BOOL),
        ("primary_accounting_unchanged", _BOOL),
        ("second_key_accounting_unchanged", _BOOL),
        ("zero_pending", _BOOL),
        ("zero_duplicate_request_ids", _BOOL),
    ),
)

_DECIMAL_TEXT = UnionSpec((_pattern(DECIMAL_TEXT), StrSpec(vocabulary=frozenset({"missing"}))))

DB_SNAPSHOT_ROW_SPEC: DictSpec = dict_spec(
    required=(
        ("reservation_count", _int()),
        ("finalized_reservation_count", _int()),
        ("pending_reservation_count", _int()),
        ("ledger_count", _int()),
        ("finalized_ledger_count", _int()),
        ("failed_ledger_count", _int()),
        ("duplicate_request_id_count", _int()),
        ("provider_usage_rows", _int()),
        ("key_requests_used", _int(minimum=-1)),
        ("key_requests_reserved", _int(minimum=-1)),
        ("key_tokens_used", _int(minimum=-1)),
        ("key_tokens_reserved", _int(minimum=-1)),
        ("key_cost_used_eur", _DECIMAL_TEXT),
        ("key_cost_reserved_eur", _DECIMAL_TEXT),
        ("ledger_total_tokens", _int()),
        ("ledger_total_cost_eur", _DECIMAL_TEXT),
        ("route_metadata_ok", _BOOL),
    ),
)

ACCOUNTING_LEDGER_SPEC: DictSpec = dict_spec(
    required=(
        ("main", DB_SNAPSHOT_ROW_SPEC),
        ("second", DB_SNAPSHOT_ROW_SPEC),
        ("failure", DB_SNAPSHOT_ROW_SPEC),
        ("all_terminal", _BOOL),
    ),
)

FINAL_MESSAGE_SUMMARY_SPEC: DictSpec = dict_spec(
    required=(
        ("present", _BOOL),
        ("byte_length", UnionSpec((_int(), _NULL))),
        ("sha256", UnionSpec((_pattern(HEX64), _NULL))),
        ("exact_expected", _BOOL),
        ("byte_exact_format", _BOOL),
        ("surrounding_crlf_only", _BOOL),
        ("binding_effective", _BOOL),
        ("non_whitespace_mismatch", _BOOL),
        ("contains_expected", _BOOL),
        ("expected_offset", UnionSpec((_int(), _NULL))),
        ("common_prefix_bytes", UnionSpec((_int(), _NULL))),
        ("common_suffix_bytes", UnionSpec((_int(), _NULL))),
        ("leading_extra_bytes", UnionSpec((_int(), _NULL))),
        ("trailing_extra_bytes", UnionSpec((_int(), _NULL))),
        ("wrapper_classification", _vocab(FINAL_MESSAGE_WRAPPERS)),
        ("prefix_classification", _vocab(FINAL_MESSAGE_PREFIXES)),
    ),
)

VISION_EVENT_TYPE_COUNTS_SPEC: DictSpec = dict_spec(
    required=tuple((name, _int()) for name in sorted(SAFE_EVENT_TYPES)),
)

VISION_TURN_SUMMARY_SPEC: DictSpec = dict_spec(
    required=(
        ("turn", UnionSpec((_int(1, 2), _NULL))),
        ("exit_status", _int()),
        ("timed_out", _BOOL),
        ("event_bytes", _int()),
        ("event_type_counts", VISION_EVENT_TYPE_COUNTS_SPEC),
        ("tool_calls", _int()),
        ("sentinel_passed", _BOOL),
        ("binding_effective", _BOOL),
        ("response_success", _BOOL),
        ("resumed_command", _BOOL),
        ("event_final_message", FINAL_MESSAGE_SUMMARY_SPEC),
        ("file_final_message", FINAL_MESSAGE_SUMMARY_SPEC),
        ("final_binding_provenance", _vocab(FINAL_BINDING_PROVENANCE)),
    ),
)

VISION_OUTBOUND_SUMMARY_SPEC: DictSpec = dict_spec(
    required=(
        ("turn", UnionSpec((_int(1, 2), _NULL))),
        ("accepted", _BOOL),
        ("image_types", ListSpec(_vocab(SAFE_IMAGE_TYPES), 6)),
        ("images_seen", _int()),
        ("forwarded_labels", ListSpec(_vocab(SAFE_OUTBOUND_LABELS), 6)),
        ("forwarded_lengths", ListSpec(_int(), 6)),
        ("forwarded_sha256", ListSpec(_pattern(HEX64), 6)),
        ("expected_fixture_match", _BOOL),
        ("body_parsed", _BOOL),
        ("non_image_content_preserved", _BOOL),
        ("governance_content_preserved", _BOOL),
        ("tool_content_preserved", _BOOL),
        (
            "tool_definition_type_counts",
            dict_spec(
                required=tuple((name, _int()) for name in TOOL_DEFINITION_TYPE_CATEGORIES),
            ),
        ),
        (
            "tool_item_type_counts",
            dict_spec(required=tuple((name, _int()) for name in TOOL_ITEM_TYPE_CATEGORIES)),
        ),
    ),
)

VISION_METRICS_SPEC: DictSpec = dict_spec(
    required=(
        ("turn1_seen", _int()),
        ("turn1_removed", _int()),
        ("turn2_seen", _int()),
        ("turn2_removed", _int()),
        ("invocation_1_requests", _int()),
        ("invocation_2_requests", _int()),
        ("exact", _BOOL),
    ),
)

VISION_DIAGNOSTIC_SPEC: DictSpec = dict_spec(
    required=(
        ("reasons", ListSpec(_vocab(VISION_REASON_LABELS), 16)),
        ("session_matches", _BOOL),
        ("catalog_image_capability", _BOOL),
        ("catalog_detail_original_disabled", _BOOL),
        ("catalog_context_window", _int()),
        ("catalog_parallel_tools_disabled", _BOOL),
        ("turns", ListSpec(VISION_TURN_SUMMARY_SPEC, 2)),
        ("metrics", UnionSpec((_NULL, VISION_METRICS_SPEC))),
        ("phase_counts", UnionSpec((_NULL, ListSpec(_int(), 2)))),
        ("outbound", ListSpec(VISION_OUTBOUND_SUMMARY_SPEC, 8)),
    ),
)

VISION_RESULT_SPEC: DictSpec = dict_spec(
    required=(
        ("status", StrSpec(vocabulary=frozenset({"PASSED", "FAILED"}))),
        ("turn_count_class", StrSpec(vocabulary=frozenset({"2"}))),
        ("same_session", _BOOL),
        ("history_turn", _BOOL),
        ("local_history_multiplicity", _BOOL),
        ("local_history_removal", _BOOL),
        ("governance_both_turns", _BOOL),
        ("two_terminal_turns", _BOOL),
        ("diagnostic", VISION_DIAGNOSTIC_SPEC),
    ),
)

TAMPER_MATRIX_SPEC: DictSpec = dict_spec(
    required=(
        ("status", StrSpec(vocabulary=frozenset({"NOT RUN"}))),
        ("case_count_class", _vocab(COUNT_CLASS)),
    ),
)

# --------------------------------------------------------------------------
# Acceptance gate / gap inventory (full manifest flow)
# --------------------------------------------------------------------------

ACCEPTANCE_GATE_RESULT_ROW_SPEC: DictSpec = dict_spec(
    required=(
        ("obligation_id", _pattern(OBLIGATION_ID)),
        ("status", _vocab(SAFE_STATUSES)),
        ("observed", _BOOL),
        ("relationship", _vocab(SAFE_RELATIONSHIPS)),
        ("count_class", _vocab(COUNT_CLASS)),
        ("timing", _vocab(SAFE_TIMINGS)),
        ("fixture_hash", UnionSpec((_NULL, _pattern(HEX64)))),
        ("version", UnionSpec((_NULL, StrSpec(vocabulary=frozenset({CODEX_VERSION}))))),
    ),
)

_OBSERVATION_KEY_PATTERN = r"[a-z0-9_]+(?:\.[a-z0-9_]+)*"

ACCEPTANCE_GATE_PROJECTION_ROW_SPEC: DictSpec = dict_spec(
    required=(
        ("obligation_id", _pattern(OBLIGATION_ID)),
        ("source_observation_keys", ListSpec(_pattern(_OBSERVATION_KEY_PATTERN), 64)),
        ("producer", _pattern(r"[A-Za-z0-9_ .+-]{1,128}")),
        ("proving_test_node_ids", ListSpec(_pattern(SYMBOL), 8)),
        ("execution_status", _vocab(SAFE_STATUSES)),
        ("observed_field_count_class", _vocab(COUNT_CLASS)),
    ),
)

RUNTIME_FAILURE_SPEC: DictSpec = dict_spec(
    required=(
        ("class", _vocab(ACCUMULATOR_FAILURE_CLASSES)),
        ("context", UnionSpec((_NULL, FAILURE_CONTEXT_SPEC))),
    ),
)

ACCEPTANCE_GATE_SPEC: DictSpec = dict_spec(
    required=(
        ("mode", StrSpec(vocabulary=frozenset({"fake", "protected"}))),
        ("missing", ListSpec(_pattern(OBLIGATION_ID), 64)),
        ("first_failure", UnionSpec((_NULL, _pattern(OBLIGATION_ID)))),
        ("retry_count", _int()),
        ("passed", _BOOL),
        ("result_count_class", _vocab(COUNT_CLASS)),
        ("results", ListSpec(ACCEPTANCE_GATE_RESULT_ROW_SPEC, 64)),
        ("projection_table", ListSpec(ACCEPTANCE_GATE_PROJECTION_ROW_SPEC, 64)),
        (
            "observation_schema_keys",
            ListSpec(StrSpec(vocabulary=frozenset(FAKE_RESULT_SCHEMA_KEYS)), 256),
        ),
        ("runtime_failure", UnionSpec((_NULL, RUNTIME_FAILURE_SPEC))),
    ),
)

TARGET_ACCEPTANCE_GATE_SPEC: DictSpec = dict_spec(
    required=(
        ("mode", StrSpec(vocabulary=frozenset({"target_identity_replay"}))),
        ("scope", StrSpec(vocabulary=frozenset({TARGET_IDENTITY_REPLAY}))),
        ("passed", _BOOL),
        ("full_manifest_executed", _BOOL),
        ("results", ListSpec(ACCEPTANCE_GATE_RESULT_ROW_SPEC, 0)),
    ),
)

GAP_INVENTORY_ENTRY_SPEC: DictSpec = dict_spec(
    required=(
        ("gap_id", _vocab(GAP_IDS)),
        ("resolved", _BOOL),
    ),
)

GAP_INVENTORY_SPEC: ListSpec = ListSpec(GAP_INVENTORY_ENTRY_SPEC, 10)

# ``aq_preflight`` is one level deep in practice: CLI fake executions carry
# the NOT_RUN placeholders, while CLI protected executions carry the real
# offline-replay/classifier facts plus one nested fake-target child whose
# own ``aq_preflight`` is the all-NOT_RUN placeholder.
AQ_PREFLIGHT_FAKE_SPEC: DictSpec = dict_spec(
    required=(
        ("offline_replay", NOT_RUN_SPEC),
        ("classifier", NOT_RUN_SPEC),
        ("fake_target", NOT_RUN_SPEC),
    ),
)


# --------------------------------------------------------------------------
# Target (identity-replay) family sub-shapes

# --------------------------------------------------------------------------

TARGET_PLAN_SPEC: DictSpec = dict_spec(
    required=(
        ("target", _vocab(frozenset({TARGET_IDENTITY_REPLAY, TARGET_FULL}))),
        ("allowed_operations", ListSpec(_pattern(SYMBOL), 8)),
        ("max_inference_dispatches", _int()),
        ("max_compiler_dispatches", _int()),
        ("runs_codex", _BOOL),
        ("runs_vision", _BOOL),
        ("runs_other_identity", _BOOL),
        ("runs_full_protected_matrix", _BOOL),
    ),
)

TARGET_SEMANTIC_PREFLIGHT_SPEC: DictSpec = dict_spec(
    required=(
        ("helper_expected", _BOOL),
        ("validator_profile_expected", _BOOL),
        ("helper_profile_equal", _BOOL),
        ("request_body_bound", _BOOL),
    ),
)

TARGET_INITIAL_SPEC: DictSpec = dict_spec(
    required=(
        ("status", _status_int()),
        ("status_class", _vocab(TARGET_STATUS_CLASS)),
        ("sse_valid", _BOOL),
        ("chunk_count_class", _vocab(COUNT_CLASS)),
        ("timing_buckets", ListSpec(_vocab(TIMING_NAMES), 4)),
        ("response_facts", RESPONSE_FACTS_SPEC),
    ),
)

TARGET_CONTINUATION_SPEC: DictSpec = dict_spec(
    required=(
        ("status", _status_int()),
        ("status_class", _vocab(TARGET_STATUS_CLASS)),
        ("json_valid", _BOOL),
        ("usage_valid", _BOOL),
        # The runner initializes the continuation evidence to the empty
        # dictionary and only fills it when the continuation was actually
        # dispatched (the decisive max-output-token diagnostic never
        # dispatches one), so the closed shape is exactly that union.
        ("response_facts", UnionSpec((dict_spec(required=()), RESPONSE_FACTS_SPEC))),
    ),
)

TARGET_DISPATCH_COUNTS_SPEC: DictSpec = dict_spec(
    required=tuple(
        (name, _int())
        for name in (
            "inference_attempted",
            "inference_dispatched",
            "inference_completed",
            "compiler_dispatched",
            "other_dispatched",
        )
    ),
)

TARGET_FAKE_DELTA_SPEC: DictSpec = dict_spec(
    required=(("inference_calls", _int()),),
)

# --------------------------------------------------------------------------
# Finalization facts (runner ``finally`` tail + ``finalize_result``)
# --------------------------------------------------------------------------
#
# These sub-schemas close the keys the ``a71d61f`` runner attaches in the
# ``finally`` tail that runs during the identity branch's early ``return``
# (Python executes ``finally`` during ``return``) and in
# ``finalize_result()`` (invoked through the ``early_return`` flag).  Every
# shape below is quoted from the runner/offline-replay/classifier source,
# including the invariants the runner's own preflight gates enforce before
# a protected target run may proceed.

#: One preparation case row of the offline replay differential
#: (``scripts/qwen_offline_replay_differential.py``, ``_prepare``).
_OFFLINE_REPLAY_FAILURE_CLASSES: frozenset[str] = frozenset(
    {
        "template_no_user_query",
        "request_or_preparation_parse_failure",
        "request_preparation_failure",
    }
)

#: The ten fixed companion bodies, in fixed order.
_OFFLINE_REPLAY_CASE_NAMES: tuple[str, ...] = (
    "current_companion_omits_original_user",
    "current_companion_preserves_original_user",
    "arguments_empty_preserves_original_user",
    "arguments_object_preserves_original_user",
    "namespace_omitted_preserves_original_user",
    "namespace_null_preserves_original_user",
    "namespace_legal_preserves_original_user",
    "status_omitted_preserves_original_user",
    "status_completed_preserves_original_user",
    "known_good_nonzero_control",
)

#: Message roles the pinned vLLM renderer can emit for the companion
#: bodies (``function_call`` maps to the assistant role,
#: ``function_call_output`` to the tool role).
_OFFLINE_REPLAY_ROLES: frozenset[str] = frozenset({"user", "assistant", "tool"})


def _offline_replay_case_spec(name: str, *, prepared: bool) -> DictSpec:
    if prepared:
        return dict_spec(
            required=(
                ("case", StrSpec(vocabulary=frozenset({name}))),
                ("parsed", BoolSpec(True)),
                ("prepared", BoolSpec(True)),
                ("message_count", _int()),
                ("message_roles", ListSpec(_vocab(_OFFLINE_REPLAY_ROLES), 32)),
                ("engine_input_count", _int()),
                ("prompt_token_count", UnionSpec((_int(), _NULL))),
            )
        )
    return dict_spec(
        required=(
            ("case", StrSpec(vocabulary=frozenset({name}))),
            ("parsed", BoolSpec(True)),
            ("prepared", BoolSpec(False)),
            ("failure_class", StrSpec(vocabulary=frozenset({"template_no_user_query"}))),
        ),
        optional=(
            ("message_count", _int()),
            ("message_roles", ListSpec(_vocab(_OFFLINE_REPLAY_ROLES), 32)),
        ),
    )


#: The offline replay qualification result as persisted in a protected
#: target document.  The runner admits it only when the exact PASSED
#: invariants hold (``_run_offline_replay_qualification``), so the closed
#: shape pins those invariants: ``status == PASSED`` implies the pinned
#: reason, the four pinned vLLM source hashes, all eight predicate facts
#: true, and the isolated first-case failure.
OFFLINE_REPLAY_PASSED_SPEC: DictSpec = dict_spec(
    required=(
        ("status", StrSpec(vocabulary=frozenset({"PASSED"}))),
        ("execution", StrSpec(vocabulary=frozenset({"offline_cpu_metadata_only"}))),
        ("protected_requests", _int(0, 0)),
        ("credential_resolution", BoolSpec(False)),
        ("source_pins_match", BoolSpec(True)),
        (
            "source_hashes",
            dict_spec(
                required=(
                    ("protocol.py", _pattern(HEX64)),
                    ("utils.py", _pattern(HEX64)),
                    ("serving.py", _pattern(HEX64)),
                    ("chat_utils.py", UnionSpec((_pattern(HEX64), _NULL))),
                    ("chat_template.jinja", _pattern(HEX64)),
                )
            ),
        ),
        ("vllm_python", StrSpec(pattern=r"[A-Za-z0-9._+-]{1,64}")),
        ("model_metadata_path_present", BoolSpec(True)),
        ("fixed_no_user_query_predicate_present", BoolSpec(True)),
        (
            "reason",
            StrSpec(vocabulary=frozenset({"offline_preparation_differential_complete"})),
        ),
        (
            "cases",
            PositionalListSpec(
                (
                    _offline_replay_case_spec(_OFFLINE_REPLAY_CASE_NAMES[0], prepared=False),
                    *(
                        _offline_replay_case_spec(name, prepared=True)
                        for name in _OFFLINE_REPLAY_CASE_NAMES[1:]
                    ),
                )
            ),
        ),
        ("zero_argument_schema_exact", BoolSpec(True)),
        ("no_user_query_failure_isolated", BoolSpec(True)),
        ("corrected_preparation_passed", BoolSpec(True)),
    )
)

#: The provider-error classifier qualification result as persisted in a
#: protected target document.  The runner admits it only with
#: ``status == PASSED``, which the producer sets only when every predicate
#: is true.
CLASSIFIER_QUALIFICATION_PASSED_SPEC: DictSpec = dict_spec(
    required=(
        ("status", StrSpec(vocabulary=frozenset({"PASSED"}))),
        ("normal_error", BoolSpec(True)),
        ("streamed_oversized", BoolSpec(True)),
        ("cancelled_early_close", BoolSpec(True)),
    )
)

#: ``aq_preflight`` placeholder entries of the fake target document (the
#: runner initializes all three to this exact shape and only the protected
#: run overwrites them).
AQ_PREFLIGHT_NOT_RUN_SPEC: DictSpec = dict_spec(
    required=(("status", StrSpec(vocabulary=frozenset({"NOT RUN"}))),)
)

#: ``target_gate``: the bounded identity-replay target gate of
#: ``_identity_replay_target_gate`` (15 fixed keys).
TARGET_GATE_SPEC: DictSpec = dict_spec(
    required=(
        ("target", StrSpec(vocabulary=frozenset({TARGET_IDENTITY_REPLAY}))),
        ("passed", _BOOL),
        ("full_manifest_executed", BoolSpec(False)),
        ("full_protected_matrix", BoolSpec(False)),
        ("ordinary_codex_executed", BoolSpec(False)),
        ("vision_executed", BoolSpec(False)),
        ("other_identity_operations_executed", BoolSpec(False)),
        ("compiler_dispatches", _int()),
        ("inference_dispatches", _int()),
        ("provider_preflight_dispatches", _int()),
        ("companion_passed", _BOOL),
        ("accounting_passed", _BOOL),
        ("cleanup_passed", _BOOL),
        ("privacy_passed", _BOOL),
        ("protected_fixture_unchanged", _BOOL),
    )
)

#: Protected-fixture invariance facts recorded by the ``finally`` tail for
#: protected runs (``_protected_snapshot`` comparison).
PROTECTED_UNCHANGED_FACTS_SPEC: DictSpec = dict_spec(
    required=tuple(
        (name, _BOOL)
        for name in (
            "pid",
            "start",
            "listener",
            "worktree_count",
            "text_inactive",
            "no_18021",
            "no_18031",
        )
    )
)

#: Fake runs record the fixed placeholder string instead of the fact
#: dictionary.
PROTECTED_UNCHANGED_FAKE_LITERAL: StrSpec = StrSpec(vocabulary=frozenset({"NOT_APPLICABLE_FAKE"}))

# --------------------------------------------------------------------------
# Role result schemas (closed)
# --------------------------------------------------------------------------


def _target_result_tuple(
    *,
    provider_target: frozenset[str],
    runtime_observations: Spec,
    aq_preflight: Spec,
    protected_unchanged: Spec,
) -> tuple[tuple[str, Spec], ...]:
    """The exact 43-key committed identity-replay target result.

    Source: the ``a71d61f`` runner's identity branch returns a 29-key
    document from inside the runner's ``try`` block.  Python executes
    ``finally`` during ``return``, so before that return completes the
    ``finally`` tail records the full nine-key ``cleanup_observation``
    (``record_cleanup`` is therefore always called for committed target
    documents), the listener/temporary-state cleanup facts, and (protected
    runs) the ``protected_unchanged`` fixture facts, and then invokes
    ``finalize_result()`` through the ``early_return`` flag, which
    attaches ``aq_preflight``, ``runtime_observations``, ``target_gate``,
    the target-mode ``acceptance_gate``, and ``gap_inventory`` and rewrites
    the terminal ``status``.  The wrapper
    ``_run_direct_composed_rehearsal`` then attaches ``run_accumulator``,
    ``phase_checkpoints``, and ``all_lifetime_counts``.  Fake documents
    carry the ``NOT RUN`` preflight placeholders and the
    ``NOT_APPLICABLE_FAKE`` fixture fact; protected documents carry the
    real qualification results (including the nested full fake target
    document).
    """
    return (
        ("status", StrSpec(vocabulary=frozenset({"COMPLETE", "BLOCKED"}))),
        ("provider_target", _vocab(provider_target)),
        ("target", StrSpec(vocabulary=frozenset({TARGET_IDENTITY_REPLAY}))),
        ("target_plan", TARGET_PLAN_SPEC),
        ("full_protected_matrix", _BOOL),
        ("gateway_sha", StrSpec(vocabulary=frozenset({GATEWAY_MAIN_SHA}))),
        ("candidate_provenance", CANDIDATE_PROVENANCE_SPEC),
        ("gateway_health_status", _status_int()),
        ("gateway_ready_status", _status_int()),
        ("candidate_health_status", _status_int()),
        ("candidate_ready_status", _status_int()),
        ("protected_health_status", _status_int()),
        ("protected_models_status", _status_int()),
        ("target_semantic_preflight", TARGET_SEMANTIC_PREFLIGHT_SPEC),
        ("target_initial", TARGET_INITIAL_SPEC),
        ("target_continuation", TARGET_CONTINUATION_SPEC),
        (
            "terminal_validation_diagnostic",
            UnionSpec((TERMINAL_DIAGNOSTIC_SPEC, NOT_RUN_SPEC)),
        ),
        ("target_first_failure", UnionSpec((_NULL, _vocab(TARGET_FAILURE_CLASSES)))),
        ("target_dispatch_counts", TARGET_DISPATCH_COUNTS_SPEC),
        ("target_provider_boundary", PROVIDER_BOUNDARY_FULL_SPEC),
        ("idless_composed_companion", COMPANION_SPEC),
        ("target_accounting", TARGET_ACCOUNTING_SPEC),
        ("transport_observation", SNAPSHOT_SPEC),
        ("provider_observation", UnionSpec((PROVIDER_OBSERVATION_SPEC, _NULL))),
        ("fake_provider", UnionSpec((_FAKE_PROVIDER_OBSERVATION, _NULL))),
        ("target_fake_delta", UnionSpec((TARGET_FAKE_DELTA_SPEC, _NULL))),
        ("protected_later_inference", _BOOL),
        ("topology_observation", TOPOLOGY_OBSERVATION_SPEC),
        (
            "candidate_only_observation",
            UnionSpec((CANDIDATE_ONLY_OBSERVATION_SPEC, NOT_RUN_SPEC)),
        ),
        ("aq_preflight", aq_preflight),
        ("target_gate", TARGET_GATE_SPEC),
        ("protected_unchanged", protected_unchanged),
        ("gateway_listener_removed", _BOOL),
        ("candidate_listener_removed", _BOOL),
        ("temporary_state_removed", _BOOL),
        ("logs_secret_free", _BOOL),
        ("runtime_observations", runtime_observations),
        ("acceptance_gate", TARGET_ACCEPTANCE_GATE_SPEC),
        ("gap_inventory", GAP_INVENTORY_SPEC),
        ("run_accumulator", RUN_ACCUMULATOR_SPEC),
        ("phase_checkpoints", ListSpec(CHECKPOINT_SPEC, 64)),
        ("cleanup_observation", CLEANUP_OBSERVATION_SPEC),
        ("all_lifetime_counts", _ACCUMULATOR_COUNTS_SPEC),
    )


#: ``aq_preflight`` of the fake target document: the three preflights are
#: never executed in fake mode, so the closed shape is exactly the three
#: ``NOT RUN`` placeholders.
_FAKE_AQ_PREFLIGHT_SPEC: DictSpec = dict_spec(
    required=(
        ("offline_replay", AQ_PREFLIGHT_NOT_RUN_SPEC),
        ("classifier", AQ_PREFLIGHT_NOT_RUN_SPEC),
        ("fake_target", AQ_PREFLIGHT_NOT_RUN_SPEC),
    )
)

#: Closed family spec for the fake_target role (identity replay).
_FAKE_TARGET_RESULT_SPEC: DictSpec = dict_spec(
    required=_target_result_tuple(
        provider_target=frozenset({"fake"}),
        runtime_observations=RUNTIME_OBSERVATIONS_SPECS["fake_target"],
        aq_preflight=_FAKE_AQ_PREFLIGHT_SPEC,
        protected_unchanged=PROTECTED_UNCHANGED_FAKE_LITERAL,
    ),
)

#: ``aq_preflight`` of the protected target document: the runner executes
#: all three preflights before the first protected dispatch and admits
#: them only under their PASSED invariants, so the closed shape is the
#: three real qualification results (the nested ``fake_target`` is the
#: complete fake target document).
_PROTECTED_AQ_PREFLIGHT_SPEC: DictSpec = dict_spec(
    required=(
        ("offline_replay", OFFLINE_REPLAY_PASSED_SPEC),
        ("classifier", CLASSIFIER_QUALIFICATION_PASSED_SPEC),
        ("fake_target", _FAKE_TARGET_RESULT_SPEC),
    )
)

#: Closed family spec for the protected_target role (identity replay).
_PROTECTED_TARGET_RESULT_SPEC: DictSpec = dict_spec(
    required=_target_result_tuple(
        provider_target=frozenset({"protected"}),
        runtime_observations=RUNTIME_OBSERVATIONS_SPECS["protected_target"],
        aq_preflight=_PROTECTED_AQ_PREFLIGHT_SPEC,
        protected_unchanged=PROTECTED_UNCHANGED_FACTS_SPEC,
    ),
)

_FULL_GATE_REQUIRED: tuple[tuple[str, Spec], ...] = (
    (
        "status",
        StrSpec(vocabulary=frozenset({"PASSED", "FAILED", "COMPLETE", "BLOCKED"})),
    ),
    ("provider_target", StrSpec(vocabulary=frozenset({"fake"}))),
    ("gateway_sha", StrSpec(vocabulary=frozenset({GATEWAY_MAIN_SHA}))),
    ("candidate_provenance", CANDIDATE_PROVENANCE_SPEC),
    ("gateway_health_status", _status_int()),
    ("gateway_ready_status", _status_int()),
    ("candidate_health_status", _status_int()),
    ("candidate_ready_status", _status_int()),
    ("protected_health_status", _status_int()),
    ("protected_models_status", _status_int()),
    ("provider_preflight", PROVIDER_PREFLIGHT_SPEC),
    ("models_visible_expected", _BOOL),
    ("text_status", _status_int()),
    ("text_usage_present", _BOOL),
    ("stream", COMPOSED_STREAM_FACTS_SPEC),
    ("image_status", _status_int()),
    ("image_seen", _int()),
    ("image_removed", _int()),
    ("codex", CODEX_FACTS_SPEC),
    ("vision", VISION_RESULT_SPEC),
    ("cutover", CUTOVER_FACTS_SPEC),
    ("cutover_observations", CUTOVER_OBSERVATIONS_SPEC),
    ("constitution", CONSTITUTION_OBSERVATION_SPEC),
    ("identity_matrix", IDENTITY_MATRIX_SPEC),
    ("isolation", ISOLATION_OBSERVATION_SPEC),
    ("gateway_rejects", GATEWAY_REJECTS_SPEC),
    ("failure_observation", FAILURE_OBSERVATION_SPEC),
    ("compiler_observation", COMPILER_OBSERVATION_SPEC),
    ("transport_observation", MERGED_TRANSPORT_SPEC),
    ("topology_observation", TOPOLOGY_OBSERVATION_SPEC),
    ("compiler_attempt_delta", _int()),
    ("cache_hits", _int()),
    ("rehydration_hits", _int()),
    ("second_owner_isolated", _BOOL),
    ("invalid_public_key_status", _status_int()),
    ("over_quota_status", _status_int()),
    ("hosted_tool_choice_status", _status_int()),
    ("controlled_failure_status", _status_int()),
    ("failure_provider_calls", _int()),
    ("tamper_matrix", TAMPER_MATRIX_SPEC),
    ("provider_url_class", StrSpec(vocabulary=frozenset({"fake_loopback"}))),
    ("fake_provider", UnionSpec((_FAKE_PROVIDER_OBSERVATION, _NULL))),
    ("provider_observation", UnionSpec((PROVIDER_OBSERVATION_SPEC, _NULL))),
    ("fake_idless_http_regression", FAKE_IDLESS_HTTP_REGRESSION_SPEC),
    ("idless_composed_companion", COMPANION_SPEC),
    (
        "candidate_only_observation",
        UnionSpec((CANDIDATE_ONLY_OBSERVATION_SPEC, NOT_RUN_SPEC)),
    ),
    ("accounting", ACCOUNTING_LEDGER_SPEC),
    ("replay_ownership_negative", REPLAY_OWNERSHIP_NEGATIVE_SPEC),
    ("postgres_tmpfs_only", _BOOL),
    ("protected_mode_synthetic", NOT_RUN_SPEC),
    ("protected_mode_synthetic_cases", dict_spec(required=())),
    ("gateway_listener_removed", _BOOL),
    ("candidate_listener_removed", _BOOL),
    ("temporary_state_removed", _BOOL),
    ("protected_unchanged", PROTECTED_UNCHANGED_FAKE_LITERAL),
    ("run_accumulator", RUN_ACCUMULATOR_SPEC),
    ("phase_checkpoints", ListSpec(CHECKPOINT_SPEC, 64)),
    ("cleanup_observation", CLEANUP_OBSERVATION_SPEC),
    ("all_lifetime_counts", _ACCUMULATOR_COUNTS_SPEC),
    ("logs_secret_free", _BOOL),
    (
        "runtime_observations",
        build_runtime_observations_spec(FAKE_RESULT_SCHEMA_KEYS),
    ),
    ("acceptance_gate", ACCEPTANCE_GATE_SPEC),
    ("gap_inventory", GAP_INVENTORY_SPEC),
)

#: Closed spec for the AP37/current full fake machine-gate family.
#: ``aq_preflight`` is optional: the key post-dates AP37, so the AP37
#: artifact carries it not at all while current runs carry the all-NOT_RUN
#: placeholder.
FULL_FAKE_GATE_SPEC: DictSpec = dict_spec(
    required=_FULL_GATE_REQUIRED,
    optional=(
        ("aq_preflight", AQ_PREFLIGHT_FAKE_SPEC),
        ("error_type", StrSpec(vocabulary=frozenset({"preflight_incomplete"}))),
    ),
)


def result_spec_for_role(role: str) -> DictSpec:
    """Exact closed result schema for one role; fail closed on unknown roles."""
    if role == "protected_target":
        return _PROTECTED_TARGET_RESULT_SPEC
    if role == "fake_target":
        return _FAKE_TARGET_RESULT_SPEC
    if role == "manifest":
        return MANIFEST_SPEC
    _reject("role_unknown")


# --------------------------------------------------------------------------
# Deterministic synthetic samples (tests only; no artifact values)
# --------------------------------------------------------------------------
#
# Samples are *derived from the closed specs themselves* (one generic
# synthetic value per spec node) instead of being hand-written documents.
# This keeps the synthetic fixtures and the schema definitions in one
# place, guarantees they always agree, and makes every sampled value an
# obviously synthetic identifier (all-zero hashes, first vocabulary
# member, small non-negative integers) rather than an aspirational copy
# of a historical artifact.  ``materialize_sample`` never reads or derives
# values from historical artifacts.


def _render_class(segment: str, index: int) -> tuple[str, int]:
    """First matching character of a ``[...]`` class starting at ``index``."""
    j = index + 1
    negated = False
    if j < len(segment) and segment[j] == "^":
        negated = True
        j += 1
    if j < len(segment) and segment[j] == "]":
        j += 1  # a leading "]" is a literal member
    close = segment.index("]", j)
    body = segment[j:close]
    chars: list[str] = []
    k = 0
    while k < len(body):
        if body[k] == "\\" and k + 1 < len(body):
            chars.append(body[k + 1])
            k += 2
            continue
        if k + 1 < len(body) and body[k + 1] == "-" and k + 2 < len(body):
            chars.append(body[k])
            k += 3
            continue
        chars.append(body[k])
        k += 1
    if negated:
        for candidate in ("!", "~", "@", " "):
            if candidate not in chars:
                return candidate, close + 1
        raise ValueError("negated_class_unmaterializable")
    return (chars[0] if chars else "a"), close + 1


def _render_group(segment: str, index: int) -> tuple[str, int]:
    """Token for a balanced ``( ... )`` group: the shortest alternative."""
    depth = 0
    j = index
    alternatives: list[str] = []
    start = index + 1
    while j < len(segment):
        current = segment[j]
        if current == "\\":
            j += 2
            continue
        if current == "(":
            depth += 1
        elif current == ")":
            depth -= 1
            if depth == 0:
                break
        elif current == "|" and depth == 0:
            alternatives.append(segment[start:j])
            start = j + 1
        j += 1
    alternatives.append(segment[start:j])
    non_empty = [alternative for alternative in alternatives if alternative]
    chosen = min(non_empty, key=len) if non_empty else ""
    token = _render_sequence(chosen) if chosen else ""
    return token, j + 1


def _render_sequence(segment: str) -> str:
    """One deterministic token for one quantified sequence segment."""
    out: list[str] = []
    i = 0
    while i < len(segment):
        current = segment[i]
        if current == "\\":
            i += 1
            token = segment[i]
            i += 1
        elif current == "[":
            token, i = _render_class(segment, i)
        elif current == "(":
            token, i = _render_group(segment, i)
        else:
            token, i = current, i + 1
        if i < len(segment) and segment[i] in "+*?":
            quantifier = segment[i]
            i += 1
            if quantifier == "+":
                out.append(token)  # one occurrence
            # "*" and "?" contribute zero occurrences
        elif i < len(segment) and segment[i] == "{":
            close = segment.index("}", i)
            bound = segment[i + 1 : close]
            minimum = int(bound.split(",")[0])
            i = close + 1
            out.extend(token * minimum)
        else:
            out.append(token)
    return "".join(out)


def _pattern_token(pattern: str) -> str:
    """One deterministic string that matches one closed identifier pattern.

    The token renders the shortest top-level alternative of the pattern:
    classes contribute their first member, groups their shortest
    alternative, ``+`` one occurrence, ``*``/``?`` zero, and ``{n}``/
    ``{n,m}`` the minimum bound.
    """
    depth = 0
    top: list[str] = []
    start = 0
    i = 0
    while i < len(pattern):
        current = pattern[i]
        if current == "\\":
            i += 2
            continue
        if current == "(":
            depth += 1
        elif current == ")":
            depth -= 1
        elif current == "|" and depth == 0:
            top.append(pattern[start:i])
            start = i + 1
        i += 1
    top.append(pattern[start:])
    non_empty = [part for part in top if part]
    chosen = min(non_empty, key=len) if non_empty else ""
    if not chosen:
        return "a"
    result = _render_sequence(chosen)
    return result if result else "a"


def _materialize_spec(spec: Spec) -> Any:
    """Derive one deterministic synthetic value from one closed spec node."""
    if isinstance(spec, BoolSpec):
        return True if spec.value is None else spec.value
    if isinstance(spec, NullSpec):
        return None
    if isinstance(spec, IntSpec):
        return max(0, spec.minimum)
    if isinstance(spec, FloatSpec):
        if spec.minimum is None or spec.minimum == 0.0:
            return 0.0
        return spec.minimum
    if isinstance(spec, StrSpec):
        if spec.vocabulary:
            return sorted(spec.vocabulary)[0]
        assert spec.pattern is not None
        return _pattern_token(spec.pattern)
    if isinstance(spec, ListSpec):
        if spec.maximum_length == 0:
            return []
        return [_materialize_spec(spec.element)]
    if isinstance(spec, PositionalListSpec):
        return [_materialize_spec(position) for position in spec.positions]
    if isinstance(spec, UnionSpec):
        non_null = [
            alternative
            for alternative in spec.alternatives
            if not isinstance(alternative, NullSpec)
        ]
        pool = non_null or list(spec.alternatives)
        for alternative in pool:
            try:
                return _materialize_spec(alternative)
            except ValueError:
                continue
        return None
    if isinstance(spec, DictSpec):
        return {name: _materialize_spec(child) for name, child in spec.required}
    if isinstance(spec, OpenDictSpec):
        return {}
    if isinstance(spec, OpenValueSpec):
        return {}
    raise ValueError("unsupported_spec")


def materialize_sample(
    role: str,
) -> tuple[dict[str, object], dict[str, object] | None]:
    """Deterministic synthetic ``(document, preflight_line)`` for one role.

    Every value is derived from the closed role spec (one generic synthetic
    value per spec node); nothing here is read from, or derived from, a
    historical artifact.
    """
    document = _materialize_spec(result_spec_for_role(role))
    preflight_spec = preflight_spec_for_role(role)
    preflight = _materialize_spec(preflight_spec) if preflight_spec is not None else None
    return document, preflight

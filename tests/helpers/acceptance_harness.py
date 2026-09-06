"""Permanent, bounded contracts for the Objective-005 acceptance runner.

This module is repository-only support.  It contains no gateway policy and no
production adapter code.  It turns the 005-p obligations into a closed
machine-readable contract, keeps provider-boundary observations independent
from gateway accounting, and provides an injectable cutover dry-run model.
Raw request, response, source, image, credential, and endpoint values are
never retained by these helpers.
"""

from __future__ import annotations

import ast
import hashlib
import json
import os
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

Status = Literal["PASSED", "FAILED", "SKIPPED", "NOT RUN", "BLOCKED", "MISSING"]
Mode = Literal["fake", "protected"]
Relationship = Literal["equal", "distinct", "subset", "independent", "not_applicable", "other"]
CountClass = Literal["0", "1", "2", "3-4", "5+", "unknown"]
TimingBucket = Literal[
    "0-9ms", "10-49ms", "50-99ms", "100-249ms", "250-999ms", "1000ms+", "unknown"
]

SAFE_STATUSES: frozenset[str] = frozenset(
    {"PASSED", "FAILED", "SKIPPED", "NOT RUN", "BLOCKED", "MISSING"}
)
SAFE_RELATIONSHIPS: frozenset[str] = frozenset(
    {"equal", "distinct", "subset", "independent", "not_applicable", "other"}
)
SAFE_COUNT_CLASSES: frozenset[str] = frozenset({"0", "1", "2", "3-4", "5+", "unknown"})
SAFE_TIMINGS: frozenset[str] = frozenset(
    {"0-9ms", "10-49ms", "50-99ms", "100-249ms", "250-999ms", "1000ms+", "unknown"}
)


@dataclass(frozen=True)
class AcceptanceObligation:
    """One finite acceptance obligation and its dependency boundary."""

    obligation_id: str
    phase: Literal["C1", "C2", "C3", "C4", "C5", "D"]
    operation: str
    expected_observations: tuple[str, ...]
    stop_dependency: str
    evidence_key: str
    mode: Literal["both", "fake", "protected"] = "both"


@dataclass(frozen=True)
class PublicRequestBudget:
    ordinal: int
    operation: str
    maximum: int = 1
    retries: int = 0


PUBLIC_REQUEST_BUDGET: tuple[PublicRequestBudget, ...] = (
    PublicRequestBudget(1, "codex_turn_1"),
    PublicRequestBudget(2, "codex_turn_2"),
    PublicRequestBudget(3, "vision_full"),
    PublicRequestBudget(4, "vision_crop_history"),
    PublicRequestBudget(5, "identity_replay"),
    PublicRequestBudget(6, "identity_concurrent_replay"),
    PublicRequestBudget(7, "identity_tamper_matrix"),
    PublicRequestBudget(8, "authorization_matrix"),
    PublicRequestBudget(9, "controlled_failure"),
)


def _obligation(
    obligation_id: str,
    phase: Literal["C1", "C2", "C3", "C4", "C5", "D"],
    operation: str,
    expected: tuple[str, ...],
    stop: str,
    evidence: str,
    mode: Literal["both", "fake", "protected"] = "both",
) -> AcceptanceObligation:
    return AcceptanceObligation(obligation_id, phase, operation, expected, stop, evidence, mode)


# Ordered IDs are part of the report contract.  Do not derive order from a
# mapping, filesystem order, or test collection order.
ACCEPTANCE_MANIFEST: tuple[AcceptanceObligation, ...] = (
    _obligation(
        "C1.1", "C1", "codex_two_public_turns", ("two_admitted_turns",), "preflight", "codex.turns"
    ),
    _obligation(
        "C1.2",
        "C1",
        "independent_provider_calls",
        ("one_call_per_turn", "provider_boundary"),
        "C1.1",
        "provider.calls",
    ),
    _obligation(
        "C1.3",
        "C1",
        "natural_function_lifecycle",
        ("function_call", "local_tool", "matching_result"),
        "C1.1",
        "codex.tool_lifecycle",
    ),
    _obligation(
        "C1.4",
        "C1",
        "idless_call_id_continuation",
        ("mandatory_call_id", "same_key_hmac", "no_scope_downgrade"),
        "C1.3",
        "gateway.call_id",
    ),
    _obligation(
        "C1.5",
        "C1",
        "reviewed_responses_lifecycle",
        ("reasoning", "function", "message", "terminal_usage"),
        "C1.1",
        "provider.lifecycle",
    ),
    _obligation(
        "C1.6",
        "C1",
        "terminal_accounting",
        ("two_terminal_reservations", "zero_pending", "zero_duplicates"),
        "C1.2",
        "gateway.accounting",
    ),
    _obligation(
        "C2.1",
        "C2",
        "governance_dependency_acquisition",
        ("root_observed", "one_equal_dependency", "before_completion"),
        "C1.1",
        "constitution.acquisition",
    ),
    _obligation(
        "C2.2",
        "C2",
        "constitution_compile_cache_injection",
        ("candidates", "compiler_miss", "validated_cache", "injection"),
        "C2.1",
        "constitution.compile",
    ),
    _obligation(
        "C2.3",
        "C2",
        "same_session_rehydration",
        ("zero_root", "cache_reuse", "no_compiler"),
        "C2.2",
        "constitution.rehydration",
    ),
    _obligation(
        "C2.4",
        "C2",
        "session_isolation",
        ("negative_sentinel", "distinct_session"),
        "C2.2",
        "isolation.session",
    ),
    _obligation(
        "C2.5",
        "C2",
        "owner_isolation",
        ("negative_sentinel", "distinct_owner"),
        "C2.2",
        "isolation.owner",
    ),
    _obligation(
        "C2.6",
        "C2",
        "repository_isolation",
        ("negative_sentinel", "distinct_repository"),
        "C2.2",
        "isolation.repository",
    ),
    _obligation(
        "C3.1", "C3", "full_image_then_crop", ("two_turns", "history_turn"), "C1.1", "vision.turns"
    ),
    _obligation(
        "C3.2",
        "C3",
        "fake_provider_image_observation",
        ("newest_single_image", "fixture_hashes"),
        "C3.1",
        "vision.provider_images",
    ),
    _obligation(
        "C3.3",
        "C3",
        "local_history_image_observation",
        ("multiplicity", "removal"),
        "C3.1",
        "vision.local_history",
    ),
    _obligation(
        "C3.4",
        "C3",
        "vision_governance_and_terminality",
        ("governance", "two_terminal_turns"),
        "C3.1",
        "vision.terminal",
    ),
    _obligation(
        "C4.1",
        "C4",
        "signed_identity_each_request",
        ("verified_each_admission",),
        "C1.1",
        "identity.admissions",
    ),
    _obligation(
        "C4.2",
        "C4",
        "identity_continuity_and_isolation",
        ("same_session", "different_session", "different_owner", "different_repository"),
        "C4.1",
        "identity.isolation",
    ),
    _obligation(
        "C4.3",
        "C4",
        "replay_and_concurrent_replay",
        ("one_accept", "no_duplicate_provider", "no_duplicate_accounting"),
        "C4.1",
        "identity.replay",
    ),
    _obligation(
        "C4.4",
        "C4",
        "tamper_matrix",
        ("body", "query", "path", "route", "signature", "timestamp", "nonce"),
        "C4.1",
        "identity.tamper",
    ),
    _obligation(
        "C4.5",
        "C4",
        "authorization_and_quota_gates",
        ("invalid_key", "hosted_choice", "dropped_tool", "over_quota", "pre_provider"),
        "C4.1",
        "gateway.rejects",
    ),
    _obligation(
        "C4.6",
        "C4",
        "controlled_provider_failure",
        ("one_failure", "terminal_failure_accounting", "no_unrelated_call"),
        "C1.2",
        "provider.failure",
    ),
    _obligation(
        "C4.7",
        "C4",
        "accounting_consistency",
        ("request", "usage", "token", "cost", "zero_pending", "zero_duplicate"),
        "C1.6",
        "gateway.counters",
    ),
    _obligation(
        "C4.8",
        "C4",
        "compiler_bypass_accounting",
        ("zero_public_rows", "zero_fees", "zero_fence"),
        "C2.2",
        "compiler.bypass",
    ),
    _obligation(
        "C4.9",
        "C4",
        "failure_cleanup",
        ("replay", "cache", "identity", "provider"),
        "C4.3",
        "cleanup.failure",
    ),
    _obligation(
        "C5.1",
        "C5",
        "topology_no_bypass",
        ("codex_gateway_local_provider", "no_direct_route"),
        "C1.1",
        "topology.chain",
    ),
    _obligation(
        "C5.2",
        "C5",
        "privacy_containment",
        ("no_raw_canaries", "no_raw_bodies", "no_credentials"),
        "preflight",
        "privacy.scan",
    ),
    _obligation(
        "C5.3",
        "C5",
        "task_cleanup",
        ("processes", "listeners", "database", "cache", "codex_home"),
        "C1.1",
        "cleanup.task",
    ),
    _obligation(
        "C5.4",
        "C5",
        "protected_fixture_unchanged",
        ("pid", "start", "listener", "worktree_count"),
        "preflight",
        "protected.fixture",
        "protected",
    ),
    _obligation(
        "D1",
        "D",
        "capture_allowlisted_targets",
        ("existence", "hash", "mode", "owner", "safe_structure"),
        "preflight",
        "cutover.capture",
        "fake",
    ),
    _obligation(
        "D2",
        "D",
        "private_backup_permissions",
        ("backup_0700", "files_0600"),
        "D1",
        "cutover.backup",
        "fake",
    ),
    _obligation(
        "D3",
        "D",
        "refuse_unsafe_install",
        (
            "occupied_port",
            "collision",
            "unsafe_owner",
            "unsafe_mode",
            "overlap",
            "incomplete_backup",
            "rollback_unprovable",
        ),
        "D1",
        "cutover.refusal",
        "fake",
    ),
    _obligation(
        "D4",
        "D",
        "candidate_specifications",
        (
            "local_18031",
            "gateway_18030",
            "protected_env",
            "signed_identity",
            "private_postgres",
            "hardened_unit",
        ),
        "D1",
        "cutover.spec",
        "fake",
    ),
    _obligation(
        "D5",
        "D",
        "dedicated_profile_isolation",
        ("add_only", "active_unchanged", "global_default_unchanged"),
        "D4",
        "cutover.profile",
        "fake",
    ),
    _obligation(
        "D6",
        "D",
        "post_install_checklist",
        ("tool_loop", "governance", "vision", "isolation", "quota", "no_bypass"),
        "D4",
        "cutover.checklist",
        "fake",
    ),
    _obligation(
        "D7",
        "D",
        "reverse_order_restore",
        ("bytes", "mode", "owner", "hash", "absence"),
        "D6",
        "cutover.rollback",
        "fake",
    ),
    _obligation(
        "D8",
        "D",
        "post_rollback_absence",
        ("ports", "processes", "units", "profile", "cache", "database", "qwen", "network"),
        "D7",
        "cutover.absence",
        "fake",
    ),
    _obligation(
        "D9",
        "D",
        "injected_failure_cleanup",
        ("each_phase", "exact_cleanup", "rollback_incomplete"),
        "D7",
        "cutover.failure_injection",
        "fake",
    ),
)


@dataclass(frozen=True)
class ObligationResult:
    obligation_id: str
    status: Status
    observed: bool
    relationship: Relationship
    count_class: CountClass
    timing: TimingBucket
    fixture_hash: str | None
    version: str | None


@dataclass(frozen=True)
class ObligationGate:
    mode: Mode
    missing: tuple[str, ...]
    first_failure: str | None
    retry_count: int
    results: tuple[ObligationResult, ...]

    @property
    def passed(self) -> bool:
        return (
            not self.missing
            and self.first_failure is None
            and self.retry_count == 0
            and all(item.status == "PASSED" and item.observed for item in self.results)
        )

    def safe_dict(self) -> dict[str, object]:
        return {
            "mode": self.mode,
            "missing": list(self.missing),
            "first_failure": self.first_failure,
            "retry_count": self.retry_count,
            "passed": self.passed,
            "result_count_class": count_class(len(self.results)),
        }


def count_class(value: int) -> CountClass:
    if value < 0:
        return "unknown"
    if value == 0:
        return "0"
    if value == 1:
        return "1"
    if value == 2:
        return "2"
    if value <= 4:
        return "3-4"
    return "5+"


def fixture_hash(value: bytes) -> str:
    """Return only a digest for synthetic fixture bytes."""
    return hashlib.sha256(value).hexdigest()


def make_result(
    obligation_id: str,
    *,
    status: Status,
    observed: bool,
    relationship: Relationship = "independent",
    count: int = 1,
    timing: TimingBucket = "unknown",
    fixture: bytes | None = None,
    version: str | None = None,
) -> ObligationResult:
    if status not in SAFE_STATUSES or relationship not in SAFE_RELATIONSHIPS:
        raise ValueError("unsafe_obligation_fact")
    if timing not in SAFE_TIMINGS:
        raise ValueError("unsafe_timing_fact")
    return ObligationResult(
        obligation_id=obligation_id,
        status=status,
        observed=observed,
        relationship=relationship,
        count_class=count_class(count),
        timing=timing,
        fixture_hash=fixture_hash(fixture) if fixture is not None else None,
        version=version if version is None or len(version) <= 64 else "other",
    )


def build_obligation_gate(
    mode: Mode,
    results: Iterable[ObligationResult],
    *,
    first_failure: str | None = None,
    retry_count: int = 0,
) -> ObligationGate:
    """Validate complete coverage and fail closed on skips or duplicates."""
    by_id: dict[str, ObligationResult] = {}
    for result in results:
        if result.obligation_id in by_id:
            raise ValueError("duplicate_obligation_result")
        by_id[result.obligation_id] = result
    expected = tuple(
        item.obligation_id for item in ACCEPTANCE_MANIFEST if item.mode in {"both", mode}
    )
    missing = tuple(item for item in expected if item not in by_id)
    selected = tuple(by_id[item] for item in expected if item in by_id)
    if retry_count != 0:
        first_failure = first_failure or "retry_count_nonzero"
    if first_failure is not None:
        selected = tuple(
            result
            for result in selected
            if result.obligation_id == first_failure or result.status != "PASSED"
        )
    return ObligationGate(mode, missing, first_failure, retry_count, selected)


@dataclass(frozen=True)
class GapObservation:
    gap_id: str
    signal: str
    present_after_fix: bool


HISTORICAL_GAP_INVENTORY: tuple[tuple[str, str], ...] = (
    ("direct_stream_before_codex", "ordinary stream"),
    ("provider_calls_from_ledger", "provider_call_count = ledger_delta"),
    ("terminality_from_status_metrics", "local_terminal_bytes"),
    ("fake_codex_not_run", '"status": "NOT_RUN"'),
    ("second_owner_literal", '"second_owner_isolated": True'),
    ("replay_not_run", "NOT_RUN_NO_REQUEST_RELAY"),
    ("incomplete_tamper_matrix", "replay_tamper"),
    ("missing_cutover_manifest", "ACCEPTANCE_MANIFEST"),
    ("passthrough_success_gate", '"status": "PASSED"'),
    ("missing_rollback_failure_injection", "rollback_incomplete"),
)


def derive_gap_inventory(source: str) -> tuple[GapObservation, ...]:
    """Derive the historical gap signals from source/AST, without execution."""
    try:
        tree = ast.parse(source)
        literals = {
            node.value
            for node in ast.walk(tree)
            if isinstance(node, ast.Constant) and isinstance(node.value, str)
        }
    except SyntaxError:
        literals = set()
    conditions = {
        "missing_cutover_manifest": "ACCEPTANCE_MANIFEST" not in source,
        "passthrough_success_gate": "build_obligation_gate" not in source,
        "missing_rollback_failure_injection": not (
            "FakeCutoverRunner" in source and "injected_failures" in source
        ),
    }
    return tuple(
        GapObservation(
            gap_id,
            signal,
            conditions.get(gap_id, signal in source or signal in literals),
        )
        for gap_id, signal in HISTORICAL_GAP_INVENTORY
    )


@dataclass(frozen=True)
class ProviderBoundaryObservation:
    """Independent fake-provider facts; no gateway ledger field is accepted."""

    call_count: int
    lifecycle_valid: bool
    terminal_count: int
    image_counts: tuple[int, ...]
    image_hashes: tuple[str, ...]
    tool_type_classes: tuple[str, ...]
    direct_gateway_rows: int

    @property
    def terminal(self) -> bool:
        return self.terminal_count == self.call_count and self.call_count > 0

    def safe_dict(self) -> dict[str, object]:
        return {
            "call_count_class": count_class(self.call_count),
            "lifecycle_valid": self.lifecycle_valid,
            "terminal_count_class": count_class(self.terminal_count),
            "terminal": self.terminal,
            "image_count_classes": tuple(count_class(value) for value in self.image_counts),
            "image_hash_count_class": count_class(len(self.image_hashes)),
            "tool_type_classes": self.tool_type_classes,
            "direct_gateway_rows": self.direct_gateway_rows,
            "independent_from_ledger": True,
        }


class StrictFakeQwenObservation:
    """Bounded observation ledger for the strict fake Qwen boundary."""

    def __init__(self) -> None:
        self._calls = 0
        self._terminal = 0
        self._lifecycle_valid = True
        self._image_counts: list[int] = []
        self._image_hashes: list[str] = []
        self._tool_types: set[str] = set()
        self._identity_fingerprints: set[str] = set()
        self._state_fingerprints: set[str] = set()

    @staticmethod
    def _walk(value: object) -> Iterable[Mapping[str, object]]:
        if isinstance(value, Mapping):
            yield value
            for child in value.values():
                yield from StrictFakeQwenObservation._walk(child)
        elif isinstance(value, list):
            for child in value:
                yield from StrictFakeQwenObservation._walk(child)

    def record(self, payload: Mapping[str, object], *, lifecycle_valid: bool = True) -> None:
        self._calls += 1
        if lifecycle_valid:
            self._terminal += 1
        else:
            self._lifecycle_valid = False
        images = [
            item for item in self._walk(payload) if item.get("type") in {"input_image", "image_url"}
        ]
        self._image_counts.append(len(images))
        for image in images:
            value = image.get("image_url")
            if isinstance(value, str):
                self._image_hashes.append(fixture_hash(value.encode("utf-8")))
        self._tool_types.update(
            str(item["type"])
            for item in self._walk(payload)
            if isinstance(item.get("type"), str)
            and item.get("type") in {"function", "custom", "tool_search", "web_search"}
        )
        metadata = payload.get("client_metadata")
        if isinstance(metadata, Mapping):
            identity = {
                key: metadata[key]
                for key in ("session_id", "thread_id", "owner_id", "repository_id")
                if key in metadata
            }
            encoded = json.dumps(identity, sort_keys=True, separators=(",", ":"))
            self._identity_fingerprints.add(fixture_hash(encoded.encode("utf-8")))
        input_value = payload.get("input")
        if input_value is not None:
            encoded_input = json.dumps(input_value, sort_keys=True, separators=(",", ":"))
            self._state_fingerprints.add(fixture_hash(encoded_input.encode("utf-8")))

    def snapshot(self) -> ProviderBoundaryObservation:
        return ProviderBoundaryObservation(
            call_count=self._calls,
            lifecycle_valid=self._lifecycle_valid,
            terminal_count=self._terminal,
            image_counts=tuple(self._image_counts),
            image_hashes=tuple(self._image_hashes),
            tool_type_classes=tuple(sorted(self._tool_types)),
            direct_gateway_rows=0,
        )

    def identity_fingerprint_count(self) -> int:
        return len(self._identity_fingerprints)

    def isolation_negative_observed(self) -> bool:
        return len(self._identity_fingerprints) >= 2 and len(self._state_fingerprints) >= 2


TAMPER_CASES: tuple[str, ...] = (
    "body",
    "query",
    "path",
    "route",
    "signature",
    "timestamp",
    "nonce",
    "ambiguous_identity",
    "missing_identity",
)


@dataclass(frozen=True)
class TamperMatrixFacts:
    case_count: int
    rejected_count: int
    pre_provider: bool
    no_duplicate_accounting: bool

    @property
    def complete(self) -> bool:
        return (
            self.case_count == len(TAMPER_CASES)
            and self.rejected_count == self.case_count
            and self.pre_provider
            and self.no_duplicate_accounting
        )


def evaluate_tamper_matrix(
    observations: Mapping[str, bool],
    *,
    provider_delta: int,
    accounting_delta: int,
) -> TamperMatrixFacts:
    """Evaluate only fixed rejection observations, never request values."""
    known = tuple(case for case in TAMPER_CASES if observations.get(case) is True)
    return TamperMatrixFacts(
        case_count=len(TAMPER_CASES),
        rejected_count=len(known),
        pre_provider=provider_delta == 0,
        no_duplicate_accounting=accounting_delta == 0,
    )


@dataclass(frozen=True)
class CutoverTarget:
    path_class: Literal[
        "allowlisted_config",
        "allowlisted_unit",
        "allowlisted_env",
        "allowlisted_cache",
        "allowlisted_runtime",
        "allowlisted_profile",
    ]
    existed: bool
    content_hash: str | None
    mode: int
    owner_class: Literal["task_user", "other", "unknown"]


@dataclass(frozen=True)
class CutoverSpecification:
    local_port: int = 18031
    gateway_port: int = 18030
    private_bind: bool = True
    signed_identity: bool = True
    protected_env_reference: bool = True
    private_postgres: bool = True
    hardened_units: bool = True
    dedicated_profile: bool = True


class FakeCutoverRunner:
    """Injectable filesystem/service runner for installation and rollback tests."""

    PHASES: tuple[str, ...] = ("capture", "backup", "install", "profile", "verify")

    def __init__(self, root: Path, *, occupied_ports: Iterable[int] = ()) -> None:
        self.root = root
        self.occupied_ports = frozenset(occupied_ports)
        self.spec = CutoverSpecification()
        self.events: list[str] = []
        self.installed = False
        self.rollback_incomplete = False

    def install(self, *, failure_phase: str | None = None) -> bool:
        if (
            self.spec.local_port in self.occupied_ports
            or self.spec.gateway_port in self.occupied_ports
        ):
            self.events.append("refused_occupied_port")
            return False
        for phase in self.PHASES:
            self.events.append(phase)
            if failure_phase == phase:
                self.rollback_incomplete = not self.rollback()
                return False
        backup = self.root / "backup"
        backup.mkdir(mode=0o700, parents=True, exist_ok=True)
        os.chmod(backup, 0o700)
        marker = backup / "manifest"
        marker.write_bytes(b"synthetic-cutover-manifest")
        os.chmod(marker, 0o600)
        self.installed = True
        return True

    def rollback(self) -> bool:
        self.events.append("rollback")
        self.installed = False
        return True

    def safe_facts(self) -> dict[str, object]:
        return {
            "local_port": self.spec.local_port,
            "gateway_port": self.spec.gateway_port,
            "private_bind": self.spec.private_bind,
            "signed_identity": self.spec.signed_identity,
            "backup_mode": "0700",
            "backup_file_mode": "0600",
            "installed": self.installed,
            "rollback_incomplete": self.rollback_incomplete,
            "event_count_class": count_class(len(self.events)),
        }

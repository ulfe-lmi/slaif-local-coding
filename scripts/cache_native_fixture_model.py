"""Typed phase/budget/closed-schema model for the serial right-pane native
fixture prerequisite (objective 017-r).

Stdlib only.  This module is the reviewable core of the fixture:

* an explicit finite phase machine
  (prepared -> measured -> synthetic-scenario -> quiesced ->
  frozen-snapshot -> teardown-verified -> published) whose every
  transition is dispatched to the EXACT semantic validator of the
  closed record schema the target phase requires; readiness is
  DERIVED from actual closed measurements only — a user-authored
  ready file, flag or JSON never advances a phase;
* a non-resettable budget ledger (requests / attempts / connections /
  threads / output bytes) plus a finite set-once lifetime deadline
  anchored to a real monotonic clock.  Changing an output directory
  or phase never resets budgets: there is no reset API by
  construction;
* exact closed record schemas.  Every record must carry the exact
  schema tag, the exact field set, and exact enum / digest /
  constant values.  Unknown tags, unknown fields, and open-ended
  string values are rejected.  Errors are fixed strings and never
  reflect an offending value, target or path back;
* the exact-issued call registry: runtime-issued call
  family / name / ID / argument identity and causal request
  position, immutable per ID, bounded by the global call budget,
  and kept distinct from numeric native process/session IDs (a
  numeric value is never inferred as a process ID from a call ID,
  and arbitrary inbound progress never issues the next call);
* a bounded metadata diagnostic that inspects ONLY the
  schema-evidenced tools region of an actual-shaped request,
  retains only closed tool-family / name-count / required-field-
  presence metadata, and represents unknown offered modes as fixed
  states — never copying source values;
* the closed quiesce, selected-snapshot, teardown and publish
  records that make socket/handler/process closure,
  export-before-teardown and teardown-before-publication
  machine-checkable.  A daemon or query failure is a distinct
  unverified state, never proof of absence.

No repository product code is imported; the fixture is not wired
into the adapter request path.  Nothing here claims a native format
or collector result: actual native capture is NOT RUN in this round.
"""

from __future__ import annotations

import enum
import hashlib
import json
import math
import time
from collections.abc import Callable
from dataclasses import dataclass

# -- closed record schema tags -------------------------------------------
SCHEMA_ARTIFACT = "slaif-fixture-artifact-v1"
SCHEMA_EXEC_MEASUREMENT = "slaif-fixture-exec-measurement-v1"
SCHEMA_METADATA_DIAGNOSTIC = "slaif-fixture-metadata-diagnostic-v1"
SCHEMA_QUIESCE = "slaif-fixture-quiesce-v1"
SCHEMA_SNAPSHOT = "slaif-fixture-selected-snapshot-v1"
SCHEMA_TEARDOWN = "slaif-fixture-teardown-v1"
SCHEMA_PUBLISH = "slaif-fixture-publish-v1"
SCHEMA_PROFILE = "slaif-fixture-profile-v1"
SCHEMA_CI_SUMMARY = "slaif-cache-native-fixture-ci-summary-v1"

# -- finite fixture limits (order 017-r initial fixture recommendation) ---
MEMORY_LIMIT_BYTES = 1024 * 1024 * 1024  # 1 GiB
SWAP_LIMIT_BYTES = 0  # zero swap is the required supported value
CPU_LIMIT = 1
PIDS_LIMIT = 96
TMPFS_BUDGET_TOTAL_MAX_BYTES = 192 * 1024 * 1024  # distinct budgets, sum cap
# (mount, size_bytes, uid, gid): controller private root, subject private
# root, bounded shared scratch.
DEFAULT_TMPFS_BUDGETS: tuple[tuple[str, int, int, int], ...] = (
    ("/run/slaif-ctl", 64 * 1024 * 1024, 21001, 21001),
    ("/run/slaif-subj", 64 * 1024 * 1024, 21002, 21002),
    ("/tmp", 64 * 1024 * 1024, 21002, 21002),
)
CONTROLLER_UID = 21001
SUBJECT_UID = 21002
# The daemon's default shared-memory mount (/dev/shm) is subject-
# writable, so it is part of the RECONCILED writable-data surface:
# the runner bounds it explicitly (--shm-size) instead of relying on
# the daemon default, and the subject measures it back from its own
# mount table.  Standard kernel virtual/device filesystems are a
# distinct class and never count as writable data.
SHM_MOUNT = "/dev/shm"
SHM_SIZE_BYTES = 64 * 1024 * 1024
SHM_OWNER = (0, 0)
SHM_MODE = 0o1777
# Reconciled effective writable-data storage bound: the three
# configured budgets (192 MiB cap) plus the explicitly bounded
# /dev/shm (64 MiB).
WRITABLE_DATA_TOTAL_MAX_BYTES = TMPFS_BUDGET_TOTAL_MAX_BYTES + SHM_SIZE_BYTES
# The fixed seeded original count: shared by the controller seeder,
# the snapshot record, the export client's closed proof and the host
# runner's independent revalidation (one closed constant, one fact).
ORIGINALS_COUNT = 3
# Controller-private mounts admit no other access at all; subject-owned
# mounts may use the conventional shared scratch mode in addition.
CONTROLLER_MOUNT_MODES = (0o700,)
SUBJECT_MOUNT_MODES = (0o700, 0o1777)

# Bounded diagnostic traversal limits (tools region only).
DIAGNOSTIC_MAX_DEPTH = 4
DIAGNOSTIC_MAX_TOOL_NAMES = 256
DIAGNOSTIC_MAX_BYTES = 256 * 1024

# -- public pinned artifact identities (researched public release metadata;
# the archive is fetched and statically hashed in CI — never executed) ----
ARTIFACT_TAG = "rust-v0.164.0"
ARTIFACT_COMMIT = "6aaac694803004a63c6f393d153c96d22521a6b9"
ARTIFACT_ARCHIVE_URL = (
    "https://github.com/openai/codex/releases/download/"
    + ARTIFACT_TAG
    + "/codex-x86_64-unknown-linux-musl.tar.gz"
)
ARTIFACT_ARCHIVE_SIZE = 114979035
ARTIFACT_ARCHIVE_SHA256 = "90dd0b03b28afcb7fa733a4f73b413db2916a47347efd43fb669cc1c774ee8e4"
ARTIFACT_BINARY_NAME = "codex-x86_64-unknown-linux-musl"
# Explicit finite reviewed bound for the EXTRACTED regular executable.
# The compressed archive size does not establish the extracted size;
# the ACTUAL 0.164.0 musl archive (size/digest verified above)
# contains a single member measuring 308,139,304 bytes extracted;
# this finite bound (with reviewed headroom over that measured
# fact) is the fail-closed ceiling CI enforces while extracting.
ARTIFACT_BINARY_MAX_BYTES = 320 * 1024 * 1024
ARTIFACT_LICENSE = "Apache-2.0"
# The public license text at the exact pinned commit (the archive
# carries no license member; the runner fetches and bounds it).
ARTIFACT_LICENSE_URL = (
    "https://raw.githubusercontent.com/openai/codex/" + ARTIFACT_COMMIT + "/LICENSE"
)
# Closed identity markers of the Apache-2.0 license text (the
# runner verifies both before the file enters the build context).
ARTIFACT_LICENSE_MARKERS = (
    "Apache License",
    "Version 2.0, January 2004",
)
# Pinned public LICENSE byte identity at the exact pinned commit
# (10926 bytes; the runner verifies size, markers AND digest before
# the file enters the build context).
ARTIFACT_LICENSE_SIZE = 10926
ARTIFACT_LICENSE_SHA256 = "d17f227e4df5da1600391338865ce0f3055211760a36688f816941d58232d8dc"
# The pinned commit's public NOTICE (242 bytes): it credits the
# included Ratatui-derived code under the MIT license.  R section 3
# requires the license/NOTICE requirements to be preserved, so the
# runner fetches it with bounded reads, verifies the byte identity,
# and installs it immutably alongside the license (never claimed
# preserved when the implementation only retains the LICENSE).
ARTIFACT_NOTICE = "MIT (Ratatui-derived code notice)"
ARTIFACT_NOTICE_URL = (
    "https://raw.githubusercontent.com/openai/codex/" + ARTIFACT_COMMIT + "/NOTICE"
)
ARTIFACT_NOTICE_SIZE = 242
ARTIFACT_NOTICE_SHA256 = "9d71575ecfd9a843fc1677b0efb08053c6ba9fd686a0de1a6f5382fd3c220915"
# Closed identity markers of the pinned public NOTICE text.
ARTIFACT_NOTICE_MARKERS = (
    "Ratatui",
    "MIT license",
)
SIGNATURE_VERIFICATION = "not-run"  # never asserted by the archive hash

# -- closed value enums -----------------------------------------------------
SWAP_SOURCE_ENUM = ("v2-swap-max", "v1-memsw-combined")
KEYRING_ERRNO = 1  # EPERM: policy denial before any lookup
KEYRING_PROBES = ("add_key", "request_key", "keyctl")
CAPABILITY_SETS = ("ambient", "bounding", "effective", "inheritable", "permitted")
NAMESPACE_FACTS = (
    "pid_private",
    "mount_private",
    "ipc_private",
    "uts_private",
    "net_private",
    "user_shared",
)
DENIED_TARGETS = (
    "controller_socket_dir",
    "issued_registry",
    "controller_originals",
    "controller_sentinel",
    "controller_proc",
    "exporter_socket",
)
SUBJECT_DENIAL_STATES = ("eacces", "eperm", "enoent")
TOOL_FAMILY_OBSERVED = ("function", "custom")
TOOL_FAMILY_ISSUABLE = ("function",)
UNKNOWN_MODE_KINDS = (
    "tools-not-list",
    "tool-not-object",
    "unknown-tool-type",
    "missing-function-name",
    "function-name-not-closed",
    "custom-name-not-closed",
)
ABSENCE_STATES = ("absent-verified", "query-failed-unverified", "present-unexpected")
ABSENCE_VERIFIED = "absent-verified"
SCENARIO_NAMES = (
    "controller-measurement",
    "exec-21002-measurement",
    "pty-attach",
    "synthetic-success",
    "synthetic-fail",
    "synthetic-hang",
    "synthetic-output-cap",
    "export-fail",
    "quiesce-fail",
    "controller-crash",
)
SCENARIO_STATES = (
    "completed",
    "failed-as-designed",
    "timed-out-as-designed",
    "cap-hit-as-designed",
    "crashed-as-designed",
)
DEFAULT_MAX_ISSUED_CALLS = 512  # defaults to the ledger request bound

# Bounded allowlist of PUBLIC native exec-family tool names researched
# from the 0.164.0 source, with their closed argument-field kinds.  The
# diagnostic retains ONLY these closed names/fields as presence
# metadata; any other name is an unknown count, never reflected text.
KNOWN_TOOL_NAMES: dict[str, tuple[str, ...]] = {
    "exec_command": ("cmd",),
    "write_stdin": ("session_id", "chars"),
}
FIELD_STATE_ENUM = ("required", "present", "absent")
DIAGNOSTIC_MAX_REQUIRED_FIELDS = 32

# The runner's declared required scenario matrix: the single source of
# truth the final CI summary must match exactly (name -> required
# state).  A deliberate fail/hang outcome is success only for that
# specifically declared scenario.
REQUIRED_SCENARIOS: tuple[tuple[str, str], ...] = (
    ("controller-measurement", "completed"),
    ("exec-21002-measurement", "completed"),
    ("pty-attach", "completed"),
    ("synthetic-success", "completed"),
    ("synthetic-fail", "failed-as-designed"),
    ("synthetic-hang", "timed-out-as-designed"),
    ("synthetic-output-cap", "cap-hit-as-designed"),
    ("export-fail", "failed-as-designed"),
    ("quiesce-fail", "failed-as-designed"),
    ("controller-crash", "crashed-as-designed"),
)


class FixtureError(ValueError):
    """Fail-closed fixture model error (fixed message, no raw content)."""


class BudgetExceeded(FixtureError):
    """A finite budget bound was exceeded (fixed state, never a reset)."""


class FixturePhase(enum.StrEnum):
    PREPARED = "prepared"
    MEASURED = "measured"
    SYNTHETIC_SCENARIO = "synthetic-scenario"
    QUIESCED = "quiesced"
    FROZEN_SNAPSHOT = "frozen-snapshot"
    TEARDOWN_VERIFIED = "teardown-verified"
    PUBLISHED = "published"


PHASE_ORDER: tuple[FixturePhase, ...] = (
    FixturePhase.PREPARED,
    FixturePhase.MEASURED,
    FixturePhase.SYNTHETIC_SCENARIO,
    FixturePhase.QUIESCED,
    FixturePhase.FROZEN_SNAPSHOT,
    FixturePhase.TEARDOWN_VERIFIED,
    FixturePhase.PUBLISHED,
)

# Each phase requires its exact closed record schema.  Quiesce and
# teardown need their own closure/removal evidence and cannot reuse a
# generic diagnostic tag.
PHASE_REQUIRED_RECORD: dict[FixturePhase, str] = {
    FixturePhase.PREPARED: SCHEMA_ARTIFACT,
    FixturePhase.MEASURED: SCHEMA_EXEC_MEASUREMENT,
    FixturePhase.SYNTHETIC_SCENARIO: SCHEMA_METADATA_DIAGNOSTIC,
    FixturePhase.QUIESCED: SCHEMA_QUIESCE,
    FixturePhase.FROZEN_SNAPSHOT: SCHEMA_SNAPSHOT,
    FixturePhase.TEARDOWN_VERIFIED: SCHEMA_TEARDOWN,
    FixturePhase.PUBLISHED: SCHEMA_PUBLISH,
}


# -- exact closed-value helpers (fixed, non-echoing errors) ----------------
def _int_field(record: dict, key: str) -> int:
    value = record[key]
    if not isinstance(value, int) or isinstance(value, bool):
        raise FixtureError(f"closed record field type invalid: {key}")
    return value


def _bool_field(record: dict, key: str, expected: bool) -> None:
    if record[key] is not expected:
        raise FixtureError(f"closed record field state invalid: {key}")


def _enum_field(record: dict, key: str, allowed: tuple[str, ...]) -> str:
    value = record[key]
    if not isinstance(value, str) or value not in allowed:
        raise FixtureError(f"closed record field enum invalid: {key}")
    return value


def _const_field(record: dict, key: str, expected: object) -> None:
    if record[key] != expected:
        raise FixtureError(f"closed record field identity invalid: {key}")


def _is_sha256(value: object) -> bool:
    return (
        isinstance(value, str) and len(value) == 64 and all(c in "0123456789abcdef" for c in value)
    )


def _sha256_field(record: dict, key: str) -> str:
    if not _is_sha256(record[key]):
        raise FixtureError(f"closed record digest invalid: {key}")
    return record[key]  # type: ignore[return-value]


def _opaque_id(value: object) -> bool:
    """Bounded opaque identifier: 1..128 chars from [A-Za-z0-9._-].

    Deliberately separate from the fixed exported enum schemas: native
    opaque IDs may contain uppercase, so the identity vocabulary is not
    silently narrowed, while slashes, whitespace and unbounded lengths
    stay out of the closed records.
    """
    if not isinstance(value, str) or not value or len(value) > 128:
        return False
    return all("a" <= c <= "z" or "A" <= c <= "Z" or "0" <= c <= "9" or c in "._-" for c in value)


def _expect_tag(record: object, schema: str) -> None:
    if not isinstance(record, dict):
        raise FixtureError("closed record must be an object")
    if record.get("record") != schema:
        raise FixtureError("closed record schema tag mismatch")


def _expect_field_set(record: dict, fields: frozenset[str]) -> None:
    body = set(record) - {"record"}
    if body != fields:
        # Fixed message: the offending key(s) are never reflected back.
        raise FixtureError("closed record field set mismatch")


# -- budgets ----------------------------------------------------------------
@dataclass(frozen=True)
class FixtureBudgets:
    """Explicit finite fixture limits (order 017-r recommendation)."""

    memory_limit_bytes: int = MEMORY_LIMIT_BYTES
    swap_limit_bytes: int = SWAP_LIMIT_BYTES
    cpu_limit: int = CPU_LIMIT
    pids_limit: int = PIDS_LIMIT
    tmpfs_budgets: tuple[tuple[str, int, int, int], ...] = DEFAULT_TMPFS_BUDGETS
    output_cap_bytes: int = 64 * 1024 * 1024
    max_requests: int = 512
    max_attempts: int = 64
    max_connections: int = 128
    max_threads: int = 16
    lifetime_seconds: int = 1800
    max_export_bytes: int = 16 * 1024 * 1024

    def validate(self) -> None:
        for name in (
            "memory_limit_bytes",
            "cpu_limit",
            "pids_limit",
            "output_cap_bytes",
            "max_requests",
            "max_attempts",
            "max_connections",
            "max_threads",
            "lifetime_seconds",
            "max_export_bytes",
        ):
            value = getattr(self, name)
            if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
                raise FixtureError(f"budget field must be a positive finite integer: {name}")
        swap = self.swap_limit_bytes
        # Zero swap is the required supported value; booleans, negatives
        # and missing values (caught by dataclass construction failing to
        # satisfy validate) are not.
        if not isinstance(swap, int) or isinstance(swap, bool) or swap < 0:
            raise FixtureError(
                "budget field must be a finite nonnegative integer: swap_limit_bytes"
            )
        if swap > self.memory_limit_bytes:
            raise FixtureError("swap budget exceeds memory budget")
        if not isinstance(self.tmpfs_budgets, tuple) or len(self.tmpfs_budgets) == 0:
            raise FixtureError("tmpfs budgets must be a nonempty finite tuple")
        total = 0
        seen: set[str] = set()
        for entry in self.tmpfs_budgets:
            if not isinstance(entry, tuple) or len(entry) != 4:
                raise FixtureError("tmpfs budget entry shape invalid")
            mount, size, uid, gid = entry
            if not isinstance(mount, str) or not mount.startswith("/") or mount in seen:
                raise FixtureError("tmpfs mount path invalid or duplicated")
            seen.add(mount)
            for v in (size, uid, gid):
                if not isinstance(v, int) or isinstance(v, bool) or v <= 0:
                    raise FixtureError("tmpfs budget entry field invalid")
            total += size
        if total > TMPFS_BUDGET_TOTAL_MAX_BYTES:
            raise FixtureError("tmpfs budgets exceed the finite total cap")


# -- non-resettable ledger + phase machine ----------------------------------
class FixtureLedger:
    """Non-resettable attempt/request/output/deadline ledger.

    One ledger covers the whole fixture run INCLUDING diagnostics:
    changing an output directory or phase never resets budgets.  The
    lifetime deadline is set once, anchored to a real monotonic clock,
    and is checked on every phase transition.
    """

    def __init__(
        self,
        budgets: FixtureBudgets | None = None,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        self.budgets = budgets or FixtureBudgets()
        self.budgets.validate()
        self._clock = clock
        # Fresh: no phase reached yet.  Entering PREPARED itself is
        # evidence-gated (the artifact identity record), so readiness
        # for every phase is derived, never assumed at construction.
        self.phase: FixturePhase | None = None
        self.requests = 0
        self.attempts = 0
        self.connections = 0
        self.threads = 0
        self.output_bytes = 0
        self.deadline_seconds: float | None = None
        self._deadline_monotonic: float | None = None
        self.history: list[str] = []

    # -- budget accounting (fail closed, non-resettable) -----------------
    def _count(self, name: str, bound_name: str) -> int:
        self.require_within_deadline()
        current = getattr(self, name)
        bound = getattr(self.budgets, bound_name)
        if current + 1 > bound:
            raise BudgetExceeded(f"budget bound exceeded: {name}")
        setattr(self, name, current + 1)
        return current + 1

    def record_request(self) -> int:
        return self._count("requests", "max_requests")

    def record_attempt(self) -> int:
        return self._count("attempts", "max_attempts")

    def record_connection(self) -> int:
        return self._count("connections", "max_connections")

    def record_thread(self) -> int:
        return self._count("threads", "max_threads")

    def record_output(self, n_bytes: int) -> int:
        self.require_within_deadline()
        if not isinstance(n_bytes, int) or isinstance(n_bytes, bool) or n_bytes < 0:
            raise FixtureError("output accounting requires a nonnegative integer")
        if self.output_bytes + n_bytes > self.budgets.output_cap_bytes:
            raise BudgetExceeded("budget bound exceeded: output_bytes")
        self.output_bytes += n_bytes
        return self.output_bytes

    # -- finite set-once lifetime deadline (real monotonic expiry) -------
    def set_deadline(self, seconds: float) -> None:
        if self.deadline_monotonic() is not None:
            raise FixtureError("deadline is set once; it never resets")
        if not isinstance(seconds, (int, float)) or isinstance(seconds, bool):
            raise FixtureError("deadline must be a finite positive number")
        if not math.isfinite(seconds) or seconds <= 0:
            raise FixtureError("deadline must be a finite positive number")
        if seconds > self.budgets.lifetime_seconds:
            raise BudgetExceeded("budget bound exceeded: lifetime_seconds")
        self.deadline_seconds = float(seconds)
        self._deadline_monotonic = self._clock() + seconds

    def deadline_monotonic(self) -> float | None:
        return self._deadline_monotonic

    def deadline_expired(self) -> bool:
        limit = self._deadline_monotonic
        return limit is not None and self._clock() >= limit

    def remaining_seconds(self) -> float | None:
        limit = self._deadline_monotonic
        if limit is None:
            return None
        return max(0.0, limit - self._clock())

    def require_within_deadline(self) -> None:
        if self.deadline_expired():
            raise BudgetExceeded("budget bound exceeded: lifetime deadline")

    # -- phase machine (ordered, evidence-gated) --------------------------
    def transition(self, target: FixturePhase, record: dict) -> FixturePhase:
        try:
            target = FixturePhase(target)
        except ValueError as exc:
            raise FixtureError("unknown fixture phase") from exc
        current = -1 if self.phase is None else PHASE_ORDER.index(self.phase)
        if PHASE_ORDER.index(target) != current + 1:
            raise FixtureError(
                "phase transition is not the next finite phase (no skipping, no backward, no reset)"
            )
        self.require_within_deadline()
        validator = _SCHEMA_VALIDATORS[PHASE_REQUIRED_RECORD[target]]
        _run_schema_validator(validator, record, self.budgets)
        self.phase = target
        self.history.append(target.value)
        return target

    def require_phase(self, phase: FixturePhase) -> None:
        if self.phase is None or PHASE_ORDER.index(self.phase) < PHASE_ORDER.index(phase):
            raise FixtureError("fixture phase not yet reached")


# -- exact closed record schemas --------------------------------------------
_ARTIFACT_FIELDS = frozenset(
    {
        "tag",
        "commit",
        "archive_sha256",
        "archive_size",
        "binary_name",
        "binary_sha256",
        "binary_size",
        "license",
        "license_sha256",
        "notice",
        "notice_sha256",
        "signature_verification",
    }
)
HOST_ISOLATION_FACTS = (
    "parent_proc_visible",
    "host_sentinel_visible",
    "host_listener_reachable",
)
_EXEC_FIELDS = frozenset(
    {
        "uid",
        "gid",
        "groups",
        "capabilities",
        "no_new_privs",
        "seccomp_filter_mode",
        "namespaces",
        "loopback_only",
        "keyring_errno",
        "memory_limit_bytes",
        "swap_limit_bytes",
        "swap_source",
        "cpu_limit",
        "pids_limit",
        "writable_mounts",
        "rootfs_readonly",
        "controller_pid1_uid",
        "private_pid1_exempt",
        "denied",
        "host_isolation",
        "mounts_scanned",
    }
)
_DIAGNOSTIC_FIELDS = frozenset(
    {
        "endpoint",
        "tool_families",
        "function_name_count",
        "known_names",
        "unknown_name_count",
        "argument_field_presence",
        "traversal_depth",
        "required_fields",
        "unknown_modes",
        "response_kind",
        "raw_content_retained",
    }
)
_QUIESCE_FIELDS = frozenset(
    {
        "provider_sockets_closed",
        "handlers_stopped",
        "owned_subject_stopped",
        "owned_tools_stopped",
        "active_connections",
        "residual_writers",
    }
)
_SNAPSHOT_FIELDS = frozenset(
    {
        "synthetic",
        "issued_calls",
        "originals_bytes",
        "originals_sha256",
        "exporter_uid",
        "exported_before_teardown",
        "controller_ledger",
    }
)
_TEARDOWN_FIELDS = frozenset(
    {
        "cid",
        "container_present_before",
        "container_inspect_after",
        "image_present_before",
        "image_inspect_after",
        "descendants_before",
        "descendants_after",
        "sentinel_survived",
        "export_completed_before_teardown",
    }
)
_PUBLISH_FIELDS = frozenset(
    {
        "publish_dir_mode",
        "artifact_file_mode",
        "artifact_sha256",
        "snapshot_digest_match",
        "api_requests",
        "api_attempts",
        "requests_admitted",
        "requests_refused",
        "healthz_attempts",
        "docker_admissions",
        "docker_refusals",
        "bytes_drained",
        "bytes_retained",
        "deadline_expired",
    }
)
_PROFILE_FIELDS = frozenset(
    {
        "codex_home_mode",
        "codex_home_uid",
        "base_config_sha256",
        "base_config_mode",
        "profile_file",
        "profile_sha256",
        "profile_mode",
        "profile_table_used",
        "credential_file_mode",
        "credential_sha256",
        "env_key_name",
        "loopback_only",
    }
)
_PROFILE_ENV_KEY = "SLAIF_SYNTHETIC_API_KEY"
_PROFILE_NAME = "early-beta.config.toml"
_CI_SUMMARY_FIELDS = frozenset(
    {
        "scenarios",
        "container_removal",
        "image_removal",
        "export_sha256",
        "codex_invoked",
        "api_requests",
        "api_attempts",
        "requests_admitted",
        "requests_refused",
        "healthz_attempts",
        "docker_admissions",
        "docker_refusals",
        "bytes_drained",
        "bytes_retained",
        "deadline_expired",
        "writable_mounts",
        "writable_data_total_bytes",
    }
)


def validate_artifact_record(record: dict) -> None:
    """Exact public artifact identity record.

    ``binary_sha256``/``binary_size`` are the MEASURED extracted regular
    executable facts (recorded by CI after bounded extraction); the
    compressed archive size is not treated as the extracted size.
    Static binary identity is never claimed before CI extraction proves
    it; signature verification not actually performed stays not-run.
    """
    _expect_tag(record, SCHEMA_ARTIFACT)
    _expect_field_set(record, _ARTIFACT_FIELDS)
    _const_field(record, "tag", ARTIFACT_TAG)
    _const_field(record, "commit", ARTIFACT_COMMIT)
    _const_field(record, "archive_sha256", ARTIFACT_ARCHIVE_SHA256)
    if _int_field(record, "archive_size") != ARTIFACT_ARCHIVE_SIZE:
        raise FixtureError("closed record field identity invalid: archive_size")
    _const_field(record, "binary_name", ARTIFACT_BINARY_NAME)
    _sha256_field(record, "binary_sha256")
    size = _int_field(record, "binary_size")
    if size <= 0 or size > ARTIFACT_BINARY_MAX_BYTES:
        raise FixtureError("closed record field bound invalid: binary_size")
    _const_field(record, "license", ARTIFACT_LICENSE)
    if _sha256_field(record, "license_sha256") != ARTIFACT_LICENSE_SHA256:
        raise FixtureError("closed record field identity invalid: license_sha256")
    _const_field(record, "notice", ARTIFACT_NOTICE)
    if _sha256_field(record, "notice_sha256") != ARTIFACT_NOTICE_SHA256:
        raise FixtureError("closed record field identity invalid: notice_sha256")
    _const_field(record, "signature_verification", SIGNATURE_VERIFICATION)


def validate_exec_measurement(record: dict, budgets: FixtureBudgets) -> None:
    """Closed 21002 exec measurement record.

    The exec child proves its OWN identity (Container Config.User 21001
    is not proof for 21002): complete actual facts are required — all
    five capability sets, measured cpu/memory/swap/pids, the exact
    configured writable-mount identities, and controller-private
    denial proofs where the controller-owned existence of each protected
    target is established first (ENOENT alone is not protection proof).
    """
    _expect_tag(record, SCHEMA_EXEC_MEASUREMENT)
    _expect_field_set(record, _EXEC_FIELDS)
    if _int_field(record, "uid") != SUBJECT_UID:
        raise FixtureError("closed record field identity invalid: uid")
    if _int_field(record, "gid") != SUBJECT_UID:
        raise FixtureError("closed record field identity invalid: gid")
    groups = record["groups"]
    if not isinstance(groups, list) or len(groups) != 0:
        raise FixtureError("closed record field state invalid: groups")
    caps = record["capabilities"]
    if not isinstance(caps, dict) or set(caps) != set(CAPABILITY_SETS):
        raise FixtureError("closed record field set invalid: capabilities")
    for name in CAPABILITY_SETS:
        if _int_field(caps, name) != 0:
            raise FixtureError("closed record field state invalid: capabilities")
    _bool_field(record, "no_new_privs", True)
    if _int_field(record, "seccomp_filter_mode") != 2:
        raise FixtureError("closed record field state invalid: seccomp_filter_mode")
    ns = record["namespaces"]
    if not isinstance(ns, dict) or set(ns) != set(NAMESPACE_FACTS):
        raise FixtureError("closed record field set invalid: namespaces")
    for name in NAMESPACE_FACTS:
        _bool_field(ns, name, True)
    _bool_field(record, "loopback_only", True)
    kr = record["keyring_errno"]
    if not isinstance(kr, dict) or set(kr) != set(KEYRING_PROBES):
        raise FixtureError("closed record field set invalid: keyring_errno")
    for name in KEYRING_PROBES:
        if _int_field(kr, name) != KEYRING_ERRNO:
            raise FixtureError("closed record field state invalid: keyring_errno")
    if _int_field(record, "memory_limit_bytes") != budgets.memory_limit_bytes:
        raise FixtureError("closed record field identity invalid: memory_limit_bytes")
    # Measured swap must be present and exactly zero (no default-0 rescue).
    if _int_field(record, "swap_limit_bytes") != 0:
        raise FixtureError("closed record field state invalid: swap_limit_bytes")
    _enum_field(record, "swap_source", SWAP_SOURCE_ENUM)
    if _int_field(record, "cpu_limit") != budgets.cpu_limit:
        raise FixtureError("closed record field identity invalid: cpu_limit")
    if _int_field(record, "pids_limit") != budgets.pids_limit:
        raise FixtureError("closed record field identity invalid: pids_limit")
    # The closed writable-data surface: the configured tmpfs budgets
    # PLUS the daemon's explicitly bounded /dev/shm.  An unlisted
    # writable data mount can never appear (the subject scan is
    # fail-closed) and a missing documented root fails the identity
    # check below.
    configured = {mount: (size, uid, gid) for mount, size, uid, gid in budgets.tmpfs_budgets}
    configured[SHM_MOUNT] = (SHM_SIZE_BYTES, *SHM_OWNER)
    if _int_field(record, "mounts_scanned") < 1:
        raise FixtureError("closed record field state invalid: mounts_scanned")
    mounts = record["writable_mounts"]
    if not isinstance(mounts, list) or len(mounts) == 0:
        raise FixtureError("closed record field state invalid: writable_mounts")
    seen_roots: set[str] = set()
    for entry in mounts:
        if not isinstance(entry, dict) or set(entry) != {
            "root",
            "size_bytes",
            "uid",
            "gid",
            "mode",
        }:
            raise FixtureError("closed record field set invalid: writable_mounts")
        root = entry["root"]
        if (
            not isinstance(root, str)
            or not root.startswith("/")
            or root not in configured
            or root in seen_roots
        ):
            raise FixtureError("closed record field identity invalid: writable_mounts")
        seen_roots.add(root)
        size, uid, gid = configured[root]
        measured = _int_field(entry, "size_bytes")
        if measured < 1:
            raise FixtureError("closed record field state invalid: writable_mounts")
        if root == SHM_MOUNT:
            # The daemon mounts /dev/shm at the explicitly bounded
            # size (HostConfig.ShmSize is separately verified on the
            # runner side); the measured value must stay inside it.
            if measured > size:
                raise FixtureError("closed record field identity invalid: writable_mounts")
        elif measured != size:
            raise FixtureError("closed record field identity invalid: writable_mounts")
        if _int_field(entry, "uid") != uid or _int_field(entry, "gid") != gid:
            raise FixtureError("closed record field identity invalid: writable_mounts")
        if root == SHM_MOUNT:
            allowed_modes = (SHM_MODE,)
        else:
            allowed_modes = CONTROLLER_MOUNT_MODES if uid == CONTROLLER_UID else SUBJECT_MOUNT_MODES
        if _int_field(entry, "mode") not in allowed_modes:
            raise FixtureError("closed record field state invalid: writable_mounts")
    if seen_roots != set(configured):
        raise FixtureError("closed record field state invalid: writable_mounts")
    data_total = sum(_int_field(entry, "size_bytes") for entry in mounts)
    if data_total > WRITABLE_DATA_TOTAL_MAX_BYTES:
        raise FixtureError("closed record field state invalid: writable_mounts")
    _bool_field(record, "rootfs_readonly", True)
    if _int_field(record, "controller_pid1_uid") != CONTROLLER_UID:
        raise FixtureError("closed record field identity invalid: controller_pid1_uid")
    _bool_field(record, "private_pid1_exempt", True)
    # Host parent isolation measured FROM the 21002 exec identity: the
    # disposable parent's proc entry, sentinel and listener must be
    # absent/unreachable inside the private namespaces.  Controller probe
    # facts alone are not proof for a different exec identity.
    hi = record["host_isolation"]
    if not isinstance(hi, dict) or set(hi) != set(HOST_ISOLATION_FACTS):
        raise FixtureError("closed record field set invalid: host_isolation")
    for name in HOST_ISOLATION_FACTS:
        _bool_field(hi, name, False)
    denied = record["denied"]
    if not isinstance(denied, dict) or set(denied) != set(DENIED_TARGETS):
        raise FixtureError("closed record field set invalid: denied")
    for target in DENIED_TARGETS:
        entry = denied[target]
        if not isinstance(entry, dict) or set(entry) != {"present_21001", "subject"}:
            raise FixtureError("closed record field set invalid: denied")
        # The controller-owned existence is proven first; only then is the
        # subject denial actual evidence rather than ENOENT fiction.
        _bool_field(entry, "present_21001", True)
        _enum_field(entry, "subject", SUBJECT_DENIAL_STATES)


def validate_metadata_diagnostic(record: dict) -> None:
    """Closed bounded metadata diagnostic record.

    An empty family list is valid ONLY as a typed-unsupported outcome
    (unknown modes or an empty tools region); it is never a silent
    native-family success claim.  The closed count identity
    function_name_count == known + unknown must hold.
    """
    _expect_tag(record, SCHEMA_METADATA_DIAGNOSTIC)
    _expect_field_set(record, _DIAGNOSTIC_FIELDS)
    _enum_field(record, "endpoint", ("responses", "chat"))
    families = record["tool_families"]
    if not isinstance(families, list):
        raise FixtureError("closed record field type invalid: tool_families")
    if any(not isinstance(f, str) or f not in TOOL_FAMILY_OBSERVED for f in families):
        raise FixtureError("closed record field enum invalid: tool_families")
    if len(set(families)) != len(families):
        raise FixtureError("closed record field state invalid: tool_families")
    count = _int_field(record, "function_name_count")
    if count < 0 or count > DIAGNOSTIC_MAX_TOOL_NAMES:
        raise FixtureError("closed record field bound invalid: function_name_count")
    known = record["known_names"]
    if not isinstance(known, list):
        raise FixtureError("closed record field type invalid: known_names")
    if any(not isinstance(n, str) or n not in KNOWN_TOOL_NAMES for n in known):
        raise FixtureError("closed record field enum invalid: known_names")
    if len(set(known)) != len(known):
        raise FixtureError("closed record field state invalid: known_names")
    if known and "function" not in families:
        raise FixtureError("closed record field state invalid: known_names")
    unknown_count = _int_field(record, "unknown_name_count")
    if unknown_count < 0 or unknown_count > DIAGNOSTIC_MAX_TOOL_NAMES:
        raise FixtureError("closed record field bound invalid: unknown_name_count")
    if count != len(known) + unknown_count:
        raise FixtureError("closed record field state invalid: name-count-identity")
    presence = record["argument_field_presence"]
    if not isinstance(presence, dict) or set(presence) != set(known):
        raise FixtureError("closed record field set invalid: argument_field_presence")
    for name in known:
        fields = presence[name]
        if not isinstance(fields, dict) or set(fields) != set(KNOWN_TOOL_NAMES[name]):
            raise FixtureError("closed record field set invalid: argument_field_presence")
        for field in KNOWN_TOOL_NAMES[name]:
            _enum_field(fields, field, FIELD_STATE_ENUM)
    depth = _int_field(record, "traversal_depth")
    if depth < 0 or depth > DIAGNOSTIC_MAX_DEPTH:
        raise FixtureError("closed record field bound invalid: traversal_depth")
    req = record["required_fields"]
    if not isinstance(req, dict) or set(req) != {"input", "tools"}:
        raise FixtureError("closed record field set invalid: required_fields")
    for key in ("input", "tools"):
        if not isinstance(req[key], bool):
            raise FixtureError("closed record field type invalid: required_fields")
    unknown = record["unknown_modes"]
    if not isinstance(unknown, list):
        raise FixtureError("closed record field type invalid: unknown_modes")
    for entry in unknown:
        if not isinstance(entry, dict) or set(entry) != {"kind", "state"}:
            raise FixtureError("closed record field set invalid: unknown_modes")
        _enum_field(entry, "kind", UNKNOWN_MODE_KINDS)
        _const_field(entry, "state", "unsupported")
    _const_field(record, "response_kind", "fixed-final-text-no-tools")
    _bool_field(record, "raw_content_retained", False)


def validate_quiesce_record(record: dict) -> None:
    """Closed provider/handler/subject closure evidence.

    Quiesce is not a diagnostic tag: actual socket, handler and owned
    process closure facts are required.
    """
    _expect_tag(record, SCHEMA_QUIESCE)
    _expect_field_set(record, _QUIESCE_FIELDS)
    _bool_field(record, "provider_sockets_closed", True)
    _bool_field(record, "handlers_stopped", True)
    _bool_field(record, "owned_subject_stopped", True)
    _bool_field(record, "owned_tools_stopped", True)
    if _int_field(record, "active_connections") != 0:
        raise FixtureError("closed record field state invalid: active_connections")
    if _int_field(record, "residual_writers") != 0:
        raise FixtureError("closed record field state invalid: residual_writers")


def validate_snapshot_record(record: dict) -> None:
    """Closed selected-snapshot record (all fixture snapshots synthetic)."""
    _expect_tag(record, SCHEMA_SNAPSHOT)
    _expect_field_set(record, _SNAPSHOT_FIELDS)
    _bool_field(record, "synthetic", True)
    calls = record["issued_calls"]
    if not isinstance(calls, list):
        raise FixtureError("closed record field type invalid: issued_calls")
    for call in calls:
        if not isinstance(call, dict) or set(call) != {
            "family",
            "name",
            "call_id",
            "position",
            "arguments_sha256",
        }:
            raise FixtureError("closed record field set invalid: issued_calls")
        _enum_field(call, "family", TOOL_FAMILY_ISSUABLE)
        if not _opaque_id(call["name"]) or not _opaque_id(call["call_id"]):
            raise FixtureError("closed record field enum invalid: issued_calls")
        if _int_field(call, "position") < 0:
            raise FixtureError("closed record field bound invalid: issued_calls")
        digest = call["arguments_sha256"]
        if digest is not None and not _is_sha256(digest):
            raise FixtureError("closed record digest invalid: issued_calls")
    if _int_field(record, "originals_bytes") <= 0:
        raise FixtureError("closed record field bound invalid: originals_bytes")
    _sha256_field(record, "originals_sha256")
    if _int_field(record, "exporter_uid") != CONTROLLER_UID:
        raise FixtureError("closed record field identity invalid: exporter_uid")
    _bool_field(record, "exported_before_teardown", True)
    # The controller's OWN ledger totals at export time (trusted
    # observation, independently of the stand-in's client-side
    # record): requests counted by the controller for every POST
    # /v1/responses and every exporter command, and the wire output
    # bytes the controller accounted before emission.
    ctl = record["controller_ledger"]
    if not isinstance(ctl, dict) or set(ctl) != {"requests", "output_bytes"}:
        raise FixtureError("closed record field set invalid: controller_ledger")
    budgets = FixtureBudgets()
    if (
        _int_field(ctl, "requests") < 0
        or _int_field(ctl, "requests") > budgets.max_requests
        or _int_field(ctl, "output_bytes") < 0
        or _int_field(ctl, "output_bytes") > budgets.output_cap_bytes
    ):
        raise FixtureError("closed record field bound invalid: controller_ledger")


def validate_teardown_record(record: dict) -> None:
    """Closed exact CID/image/descendant teardown verification.

    Positive-before/negative-after with an authoritative inspect state:
    a daemon or query failure is the distinct unverified state, never
    proof that an object is absent.
    """
    _expect_tag(record, SCHEMA_TEARDOWN)
    _expect_field_set(record, _TEARDOWN_FIELDS)
    _sha256_field(record, "cid")
    _bool_field(record, "container_present_before", True)
    _enum_field(record, "container_inspect_after", ABSENCE_STATES)
    if record["container_inspect_after"] != ABSENCE_VERIFIED:
        raise FixtureError("closed record field state invalid: container_inspect_after")
    _bool_field(record, "image_present_before", True)
    _enum_field(record, "image_inspect_after", ABSENCE_STATES)
    if record["image_inspect_after"] != ABSENCE_VERIFIED:
        raise FixtureError("closed record field state invalid: image_inspect_after")
    if _int_field(record, "descendants_before") < 1:
        raise FixtureError("closed record field bound invalid: descendants_before")
    if _int_field(record, "descendants_after") != 0:
        raise FixtureError("closed record field state invalid: descendants_after")
    _bool_field(record, "sentinel_survived", True)
    _bool_field(record, "export_completed_before_teardown", True)


def validate_publish_record(record: dict, budgets: FixtureBudgets) -> None:
    """Closed publication evidence (only after verified teardown).

    The distinct measured quantities are published as DISTINCT
    fields (documented closed scopes, see
    docs/CACHE-OBSERVATION-CONTRACT.md): api_requests are the
    provider API requests that received a response (a refused call
    is a request), api_attempts the client-side wire attempts
    (superset), requests_admitted/requests_refused the response
    outcomes, healthz_attempts the separately bounded readiness
    polling, and docker_admissions/docker_refusals the host command
    allowlist accounting (charged before work / never executed).
    bytes_drained and bytes_retained stay distinct."""
    _expect_tag(record, SCHEMA_PUBLISH)
    _expect_field_set(record, _PUBLISH_FIELDS)
    if _int_field(record, "publish_dir_mode") != 0o700:
        raise FixtureError("closed record field state invalid: publish_dir_mode")
    if _int_field(record, "artifact_file_mode") != 0o600:
        raise FixtureError("closed record field state invalid: artifact_file_mode")
    _sha256_field(record, "artifact_sha256")
    _bool_field(record, "snapshot_digest_match", True)
    api_requests = _int_field(record, "api_requests")
    if api_requests < 0 or api_requests > budgets.max_requests:
        raise FixtureError("closed record field bound invalid: api_requests")
    api_attempts = _int_field(record, "api_attempts")
    if api_attempts < 0 or api_attempts > budgets.max_attempts:
        raise FixtureError("closed record field bound invalid: api_attempts")
    if api_requests > api_attempts:
        raise FixtureError("closed record field state invalid: api_identity")
    admitted = _int_field(record, "requests_admitted")
    if admitted < 0:
        raise FixtureError("closed record field bound invalid: requests_admitted")
    refused = _int_field(record, "requests_refused")
    if refused < 0:
        raise FixtureError("closed record field bound invalid: requests_refused")
    if admitted + refused != api_requests:
        raise FixtureError("closed record field state invalid: outcome_identity")
    healthz = _int_field(record, "healthz_attempts")
    if healthz < 0:
        raise FixtureError("closed record field bound invalid: healthz_attempts")
    if _int_field(record, "docker_admissions") < 0:
        raise FixtureError("closed record field bound invalid: docker_admissions")
    if _int_field(record, "docker_refusals") < 0:
        raise FixtureError("closed record field bound invalid: docker_refusals")
    bytes_drained = _int_field(record, "bytes_drained")
    if bytes_drained < 0 or bytes_drained > budgets.output_cap_bytes:
        raise FixtureError("closed record field bound invalid: bytes_drained")
    bytes_retained = _int_field(record, "bytes_retained")
    if bytes_retained < 0:
        raise FixtureError("closed record field bound invalid: bytes_retained")
    if bytes_retained > bytes_drained:
        raise FixtureError("closed record field state invalid: bytes_identity")
    _bool_field(record, "deadline_expired", False)


def validate_profile_record(record: dict) -> None:
    """Closed synthetic CODEX_HOME + separate profile-file record.

    The profile is a SEPARATE file (official 0.164.0 docs: --profile
    NAME overlays CODEX_HOME/NAME.config.toml; a [profiles.NAME]
    table is explicitly not used), the credential is a restricted
    0600 file referenced by env_key (never a profile value), and all
    facts are measured closed identities (digests/modes/uid).
    """
    _expect_tag(record, SCHEMA_PROFILE)
    _expect_field_set(record, _PROFILE_FIELDS)
    if _int_field(record, "codex_home_mode") != 0o700:
        raise FixtureError("closed record field state invalid: codex_home_mode")
    if _int_field(record, "codex_home_uid") != SUBJECT_UID:
        raise FixtureError("closed record field identity invalid: codex_home_uid")
    _sha256_field(record, "base_config_sha256")
    if _int_field(record, "base_config_mode") != 0o600:
        raise FixtureError("closed record field state invalid: base_config_mode")
    _const_field(record, "profile_file", _PROFILE_NAME)
    _sha256_field(record, "profile_sha256")
    if _int_field(record, "profile_mode") != 0o600:
        raise FixtureError("closed record field state invalid: profile_mode")
    _bool_field(record, "profile_table_used", False)
    if _int_field(record, "credential_file_mode") != 0o600:
        raise FixtureError("closed record field state invalid: credential_file_mode")
    _sha256_field(record, "credential_sha256")
    _const_field(record, "env_key_name", _PROFILE_ENV_KEY)
    _bool_field(record, "loopback_only", True)


def validate_ci_summary(record: dict) -> None:
    """Closed host-runner summary (sanitized; no raw content)."""
    _expect_tag(record, SCHEMA_CI_SUMMARY)
    _expect_field_set(record, _CI_SUMMARY_FIELDS)
    # The declared required matrix is the single source of truth: the
    # summary must contain exactly it, with the exact required state per
    # scenario.  Subsets, extras, and wrong outcomes all fail.
    required = dict(REQUIRED_SCENARIOS)
    scenarios = record["scenarios"]
    if not isinstance(scenarios, list) or len(scenarios) != len(required):
        raise FixtureError("closed record field state invalid: scenarios")
    seen: set[str] = set()
    for entry in scenarios:
        if not isinstance(entry, dict) or set(entry) != {"name", "state"}:
            raise FixtureError("closed record field set invalid: scenarios")
        name = entry["name"]
        if not isinstance(name, str) or name not in required:
            raise FixtureError("closed record field enum invalid: scenarios")
        if entry["state"] != required[name]:
            raise FixtureError("closed record field state invalid: scenarios")
        if name in seen:
            raise FixtureError("closed record field state invalid: scenarios")
        seen.add(name)
    if seen != set(required):
        raise FixtureError("closed record field state invalid: scenarios")
    _enum_field(record, "container_removal", ABSENCE_STATES)
    if record["container_removal"] != ABSENCE_VERIFIED:
        raise FixtureError("closed record field state invalid: container_removal")
    _enum_field(record, "image_removal", ABSENCE_STATES)
    if record["image_removal"] != ABSENCE_VERIFIED:
        raise FixtureError("closed record field state invalid: image_removal")
    _sha256_field(record, "export_sha256")
    _bool_field(record, "codex_invoked", False)
    api_requests = _int_field(record, "api_requests")
    if api_requests < 0:
        raise FixtureError("closed record field bound invalid: api_requests")
    api_attempts = _int_field(record, "api_attempts")
    if api_attempts < 0:
        raise FixtureError("closed record field bound invalid: api_attempts")
    if api_requests > api_attempts:
        raise FixtureError("closed record field state invalid: api_identity")
    admitted = _int_field(record, "requests_admitted")
    if admitted < 0:
        raise FixtureError("closed record field bound invalid: requests_admitted")
    refused = _int_field(record, "requests_refused")
    if refused < 0:
        raise FixtureError("closed record field bound invalid: requests_refused")
    if admitted + refused != api_requests:
        raise FixtureError("closed record field state invalid: outcome_identity")
    if _int_field(record, "healthz_attempts") < 0:
        raise FixtureError("closed record field bound invalid: healthz_attempts")
    if _int_field(record, "docker_admissions") < 0:
        raise FixtureError("closed record field bound invalid: docker_admissions")
    if _int_field(record, "docker_refusals") < 0:
        raise FixtureError("closed record field bound invalid: docker_refusals")
    if _int_field(record, "bytes_drained") < 0:
        raise FixtureError("closed record field bound invalid: bytes_drained")
    if _int_field(record, "bytes_retained") < 0:
        raise FixtureError("closed record field bound invalid: bytes_retained")
    if _int_field(record, "bytes_retained") > _int_field(record, "bytes_drained"):
        raise FixtureError("closed record field state invalid: bytes_identity")
    # Reconciled writable-data facts carried from the VALIDATED 21002
    # measurement (measured, never re-derived here): exactly the
    # documented data roots, the effective total inside the
    # reconciled finite bound, and the total identity against the
    # entries.
    mounts = record["writable_mounts"]
    if not isinstance(mounts, list):
        raise FixtureError("closed record field type invalid: writable_mounts")
    documented_roots = {mount for mount, _s, _u, _g in DEFAULT_TMPFS_BUDGETS}
    documented_roots.add(SHM_MOUNT)
    seen_roots: set[str] = set()
    for entry in mounts:
        if not isinstance(entry, dict) or set(entry) != {
            "root",
            "size_bytes",
            "uid",
            "gid",
            "mode",
        }:
            raise FixtureError("closed record field set invalid: writable_mounts")
        root = entry["root"]
        if not isinstance(root, str) or root not in documented_roots or root in seen_roots:
            raise FixtureError("closed record field identity invalid: writable_mounts")
        seen_roots.add(root)
        if _int_field(entry, "size_bytes") < 1:
            raise FixtureError("closed record field state invalid: writable_mounts")
    if seen_roots != documented_roots:
        raise FixtureError("closed record field state invalid: writable_mounts")
    data_total = _int_field(record, "writable_data_total_bytes")
    if data_total != sum(_int_field(entry, "size_bytes") for entry in mounts):
        raise FixtureError("closed record field state invalid: writable_data_total_bytes")
    if data_total > WRITABLE_DATA_TOTAL_MAX_BYTES:
        raise FixtureError("closed record field bound invalid: writable_data_total_bytes")
    _bool_field(record, "deadline_expired", False)


_SCHEMA_VALIDATORS: dict[str, Callable[..., None]] = {
    SCHEMA_ARTIFACT: validate_artifact_record,
    SCHEMA_EXEC_MEASUREMENT: validate_exec_measurement,
    SCHEMA_METADATA_DIAGNOSTIC: validate_metadata_diagnostic,
    SCHEMA_QUIESCE: validate_quiesce_record,
    SCHEMA_SNAPSHOT: validate_snapshot_record,
    SCHEMA_PROFILE: validate_profile_record,
    SCHEMA_TEARDOWN: validate_teardown_record,
    SCHEMA_PUBLISH: validate_publish_record,
    SCHEMA_CI_SUMMARY: validate_ci_summary,
}
_BUDGETED_SCHEMAS = frozenset({SCHEMA_EXEC_MEASUREMENT, SCHEMA_PUBLISH})


def _run_schema_validator(
    validator: Callable[..., None], record: object, budgets: FixtureBudgets
) -> None:
    if validator in (validate_exec_measurement, validate_publish_record):
        validator(record, budgets)  # type: ignore[arg-type]
    else:
        validator(record)  # type: ignore[arg-type]


def _validate_closed_record(record: object) -> None:
    """Entry point for any closed fixture record: exact tag dispatch to
    the exact field-set and value validators (default budgets for the
    budgeted schemas when called standalone).  Unknown tags and fields
    are rejected without reflection."""
    tag = record.get("record") if isinstance(record, dict) else None
    if not isinstance(tag, str):
        raise FixtureError("closed record schema tag unknown")
    validator = _SCHEMA_VALIDATORS.get(tag)
    if validator is None:
        raise FixtureError("closed record schema tag unknown")
    _run_schema_validator(validator, record, FixtureBudgets())


# -- exact-issued call registry ---------------------------------------------
class IssuedRegistry:
    """Exact-issued call identity, distinct from numeric native IDs.

    Runtime-issued exact call family / name / ID / argument identity
    and causal request position are separate from numeric native
    process/session IDs: a numeric value is never inferred as a process
    ID from a call ID, and arbitrary inbound progress never issues the
    next call.  Issued identity is immutable per ID (conflicting
    reissue is a failure), and issuance is bounded by the global call
    budget (bound to the ledger request bound by the runner).
    """

    def __init__(self, max_calls: int = DEFAULT_MAX_ISSUED_CALLS) -> None:
        if not isinstance(max_calls, int) or isinstance(max_calls, bool) or max_calls <= 0:
            raise FixtureError("issued call bound must be a positive integer")
        self._max_calls = max_calls
        self._issued: dict[tuple[str, str, str], dict] = {}
        # Call IDs are inventoried independently of tool-name eligibility:
        # one registry per fixture run/endpoint, a call ID is globally
        # unique inside it, and a same-ID collision under another
        # family/name is rejected rather than overwritten.
        self._ids: dict[str, tuple[str, str]] = {}
        self._seq = 0

    def issue(
        self,
        family: str,
        name: str,
        call_id: str,
        arguments_sha256: str | None,
        request_position: int,
    ) -> dict:
        if family not in TOOL_FAMILY_ISSUABLE:
            raise FixtureError("call family is not a supported closed enum")
        if not _opaque_id(name) or not _opaque_id(call_id):
            raise FixtureError("issued call identity is not a closed bounded id")
        if (
            not isinstance(request_position, int)
            or isinstance(request_position, bool)
            or request_position < 0
        ):
            raise FixtureError("causal request position must be a nonnegative int")
        if arguments_sha256 is not None and not _is_sha256(arguments_sha256):
            raise FixtureError("issued arguments digest must be a sha256 hex")
        if len(self._issued) >= self._max_calls:
            raise BudgetExceeded("budget bound exceeded: issued_calls")
        if call_id in self._ids:
            raise FixtureError("call id already issued; identity is immutable")
        key = (family, name, call_id)
        if key in self._issued:
            raise FixtureError("call identity already issued; identity is immutable")
        self._seq += 1
        self._ids[call_id] = (family, name)
        entry = {
            "issue_seq": self._seq,
            "family": family,
            "name": name,
            "call_id": call_id,
            "arguments_sha256": arguments_sha256,
            "request_position": request_position,
        }
        self._issued[key] = entry
        return dict(entry)

    def match(
        self,
        family: str,
        name: str,
        call_id: str,
        arguments_sha256: str | None,
        request_position: int,
    ) -> tuple[str, dict]:
        """Returns (state, closed entry-or-limitation).  Typed states:
        exact_issued / unissued / mismatched / unsupported.  Never
        invents or infers an identity."""
        if family not in TOOL_FAMILY_ISSUABLE:
            return ("unsupported", {"reason": "family-not-supported"})
        if not _opaque_id(name) or not _opaque_id(call_id):
            return ("unsupported", {"reason": "identity-not-closed"})
        if (
            not isinstance(request_position, int)
            or isinstance(request_position, bool)
            or request_position < 0
        ):
            return ("unsupported", {"reason": "position-not-closed"})
        if arguments_sha256 is not None and not _is_sha256(arguments_sha256):
            return ("unsupported", {"reason": "digest-not-closed"})
        entry = self._issued.get((family, name, call_id))
        if entry is None:
            return ("unissued", {"reason": "not-runtime-issued"})
        if entry["arguments_sha256"] != arguments_sha256:
            return ("mismatched", {"reason": "arguments-digest"})
        if request_position != entry["request_position"]:
            return ("mismatched", {"reason": "causal-position"})
        return ("exact_issued", dict(entry))

    def lookup(self, call_id: str) -> tuple[str, dict]:
        """Validate a client reference against the exact-issued
        inventory by call ID only (the native function_call_output
        wire carries the call id; the family/name/argument binding
        stays with the registry's immutable entry)."""
        if not _opaque_id(call_id):
            return ("unsupported", {"reason": "identity-not-closed"})
        binding = self._ids.get(call_id)
        if binding is None:
            return ("unissued", {"reason": "not-runtime-issued"})
        entry = self._issued[binding + (call_id,)]
        return ("exact_issued", dict(entry))

    def entries(self) -> list[dict]:
        """Closed immutable export of every issued identity (the
        selected snapshot's issued_calls source)."""
        return [dict(self._issued[key]) for key in sorted(self._issued)]

    def count(self) -> int:
        return len(self._issued)


# -- closed helpers -----------------------------------------------------------
def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_bytes(record: dict) -> bytes:
    return json.dumps(record, sort_keys=True, separators=(",", ":")).encode()


def _argument_field_presence(params: object, fields: tuple[str, ...]) -> dict[str, str]:
    """Closed required-field presence metadata for a known tool.

    Inspects ONLY the fixed allowlisted fields using bounded
    membership against the schema-evidenced ``required`` list (finite
    cap) and ``properties`` object: unrelated property names are never
    copied or retained, so a huge schema cannot inflate diagnostic
    work.  A ``required`` list over the finite cap is a fail-closed
    inspection bound, never a silently complete presence claim.
    """
    presence = {field: "absent" for field in fields}
    if not isinstance(params, dict):
        return presence
    required = params.get("required")
    required_bounded = (
        isinstance(required, list) and len(required) <= DIAGNOSTIC_MAX_REQUIRED_FIELDS
    )
    props = params.get("properties")
    for field in fields:
        if required_bounded and field in required:
            presence[field] = "required"
        elif isinstance(props, dict) and field in props:
            presence[field] = "present"
    return presence


def bounds_diagnostic(payload: object) -> dict:
    """Bounded metadata traversal of an actual-shaped request.

    Inspects ONLY the schema-evidenced tools region (top-level
    ``tools`` list, each entry's closed ``type``, the function name —
    top-level or chat-shaped under ``function`` — and the bounded
    ``required``/``properties`` presence of the allowlisted argument
    fields for known public native names).  Retains only closed
    family / known-name / unknown-count / field-presence /
    required-field-presence / measured-depth metadata.  Unknown
    offered modes and names become fixed states or counts; source
    values are never copied into the record.  Other body regions
    (input, messages, instructions, text) are never walked, so
    unrelated content changes leave the tool diagnostic equal.  A
    tools list over the finite bound fails closed instead of emitting
    a silently truncated complete-looking record.

    Depth convention (routing depth, not arbitrary JSON-schema
    traversal): envelope 0, tools list 1, tool entry 2, chat-shaped
    ``function`` block 3, ``parameters`` object 3 for the flat
    responses shape or 4 for the wrapped shape; the reported
    ``traversal_depth`` is the actual inspected maximum.  A known
    tool's overbound ``required`` list fails closed (a presence
    claim would be incomplete), never labeled complete.
    """
    if not isinstance(payload, dict):
        raise FixtureError("diagnostic input must be an actual-shaped envelope")
    unknown: list[dict] = []
    families: set[str] = set()
    name_count = 0
    known_names: set[str] = set()
    unknown_name_count = 0
    field_presence: dict[str, dict[str, str]] = {}
    depth = 0
    tools = payload.get("tools")
    if tools is not None:
        depth = 1
        if not isinstance(tools, list):
            unknown.append({"kind": "tools-not-list", "state": "unsupported"})
        elif len(tools) > DIAGNOSTIC_MAX_TOOL_NAMES:
            raise FixtureError("tools list exceeds the finite traversal bound")
        else:
            for entry in tools:
                if not isinstance(entry, dict):
                    unknown.append({"kind": "tool-not-object", "state": "unsupported"})
                    continue
                depth = max(depth, 2)
                fn_block = entry.get("function")
                if not isinstance(fn_block, dict):
                    fn_block = None
                if fn_block is not None:
                    depth = max(depth, 3)
                t = entry.get("type")
                if isinstance(t, str) and t in TOOL_FAMILY_OBSERVED:
                    families.add(t)
                else:
                    unknown.append({"kind": "unknown-tool-type", "state": "unsupported"})
                if t == "function":
                    n = entry.get("name")
                    if not isinstance(n, str) and fn_block is not None:
                        inner = fn_block.get("name")
                        n = inner if isinstance(inner, str) else None
                    if not isinstance(n, str):
                        unknown.append({"kind": "missing-function-name", "state": "unsupported"})
                    elif not _opaque_id(n):
                        unknown.append({"kind": "function-name-not-closed", "state": "unsupported"})
                    else:
                        name_count += 1
                        if n in KNOWN_TOOL_NAMES:
                            known_names.add(n)
                            params = entry.get("parameters")
                            if not isinstance(params, dict) and fn_block is not None:
                                inner = fn_block.get("parameters")
                                if isinstance(inner, dict):
                                    params = inner
                            if isinstance(params, dict):
                                required = params.get("required")
                                if (
                                    isinstance(required, list)
                                    and len(required) > DIAGNOSTIC_MAX_REQUIRED_FIELDS
                                ):
                                    raise FixtureError(
                                        "required field list exceeds the finite inspection bound"
                                    )
                                # flat parameters sit at depth 3; the
                                # wrapped chat shape adds the function
                                # block (3) before parameters (4)
                                depth = max(depth, 4 if fn_block is not None else 3)
                                field_presence[n] = _argument_field_presence(
                                    params, KNOWN_TOOL_NAMES[n]
                                )
                            else:
                                field_presence[n] = _argument_field_presence(
                                    None, KNOWN_TOOL_NAMES[n]
                                )
                        else:
                            unknown_name_count += 1
                elif t == "custom":
                    n = entry.get("name")
                    if not isinstance(n, str) or not _opaque_id(n):
                        unknown.append({"kind": "custom-name-not-closed", "state": "unsupported"})
    record = {
        "record": SCHEMA_METADATA_DIAGNOSTIC,
        "endpoint": "responses",
        "tool_families": sorted(families),
        "function_name_count": name_count,
        "known_names": sorted(known_names),
        "unknown_name_count": unknown_name_count,
        "argument_field_presence": {name: field_presence[name] for name in sorted(field_presence)},
        "traversal_depth": depth,
        "required_fields": {
            "input": "input" in payload,
            "tools": tools is not None,
        },
        "unknown_modes": unknown,
        "response_kind": "fixed-final-text-no-tools",
        "raw_content_retained": False,
    }
    if len(canonical_bytes(record)) > DIAGNOSTIC_MAX_BYTES:
        raise FixtureError("retained diagnostic exceeds the finite byte bound")
    return record

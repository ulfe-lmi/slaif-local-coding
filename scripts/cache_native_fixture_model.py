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
import re
import time
from collections.abc import Callable
from dataclasses import dataclass

# -- closed record schema tags -------------------------------------------
SCHEMA_ARTIFACT = "slaif-fixture-artifact-v1"
SCHEMA_EXEC_MEASUREMENT = "slaif-fixture-exec-measurement-v1"
SCHEMA_METADATA_DIAGNOSTIC = "slaif-fixture-metadata-diagnostic-v1"
SCHEMA_QUIESCE = "slaif-fixture-quiesce-v1"
SCHEMA_SNAPSHOT = "slaif-fixture-selected-snapshot-v1"
# The DISTINCT closed selected format-capture snapshot of the
# canonical 017-aj entry's format scenario (017-ai software,
# INERT): the SAME closed issued-identity law PLUS the four
# serial case frames strictly verified against the immutable
# pre-launch seed identity.  It is a separate closed record:
# the original selected snapshot keeps its exact historical
# field set and law byte-for-byte (never widened), and a
# format-tagged snapshot is never relabeled as the original.
SCHEMA_FORMAT_SNAPSHOT = "slaif-fixture-format-capture-snapshot-v1"
# The DISTINCT selected format-capture EXPORT payload tag
# (the closed controller-to-host transport record: the quiesce
# record plus the format snapshot ONLY — the original selected
# payload's exact historical field set and law are unchanged,
# and the outer identity metadata (binding/identity/CID) is
# added by the owner and bounded by the same TOTAL at the
# consumer/producer/export seams).
SCHEMA_FORMAT_EXPORT = "slaif-fixture-format-export-v1"
# The DISTINCT closed safe PARTIAL selected format-capture
# snapshot (017-ai software, INERT): the closed issued-registry
# PREFIX plus the issued-case prefix in closed table order —
# every entry before the last a complete verified case record,
# at most ONE pending case (the last) carrying only its retained
# verified frames.  The honest pending state: the ACTUAL non-done
# final state and the closed not-qualified fact, with NO
# completion/exit/verified/truncation placeholder in the form, so
# a non-complete scenario is safely exportable and retainable and
# can coexist with honest native-ready facts; unknown or
# unverified selection is not in the record at all and never
# becomes capture-ready or a minted pass.  The complete format
# snapshot keeps its exact historical field set and law.
SCHEMA_FORMAT_SNAPSHOT_PARTIAL = "slaif-fixture-format-capture-snapshot-partial-v1"
# The DISTINCT safe PARTIAL selected format-capture EXPORT
# payload tag (the closed controller-to-host transport record:
# the quiesce record plus the PARTIAL snapshot ONLY).  The
# complete format export tag, the complete format snapshot law
# and the original selected payload's exact historical field set
# are all unchanged.
SCHEMA_FORMAT_EXPORT_PARTIAL = "slaif-fixture-format-export-partial-v1"
# the closed qualification fact of the safe partial form: an
# honest non-qualified state, never a minted pass
FORMAT_QUALIFICATION_NOT_QUALIFIED = "not-qualified"
SCHEMA_TEARDOWN = "slaif-fixture-teardown-v1"
SCHEMA_PUBLISH = "slaif-fixture-publish-v1"
SCHEMA_PROFILE = "slaif-fixture-profile-v1"
# The owner-UID variant tags: the SAME closed facts measured under
# the frozen owner-profile subject (UID and GID independent).  Each
# v2 tag refuses its v1 counterpart and vice versa; the v1 records
# and their fixed-21002 consumers stay byte-for-byte unchanged.
SCHEMA_EXEC_MEASUREMENT_V2 = "slaif-fixture-exec-measurement-v2"
SCHEMA_PROFILE_V2 = "slaif-fixture-profile-v2"
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
# The closed mount-table record cap: the stand-in scanner rejects a
# mountinfo table with more complete records than this, so a measured
# ``mounts_scanned`` can never exceed it, and the documented data
# mounts plus the masked /dev/null aliases are a subset of the
# scanned records.
MOUNTINFO_SCANNER_MAX_RECORDS = 512
# The fixed seeded original count: shared by the controller seeder,
# the snapshot record, the export client's closed proof and the host
# runner's independent revalidation (one closed constant, one fact).
ORIGINALS_COUNT = 3
# -- the closed native format-capture scenario law (017-ai) -------------
# The IMMUTABLE pre-launch seed set: exact code-defined originals
# (at most 8 files / 128 KiB total, asserted in _format_seed_law).
# The seed identity comes from THESE pre-launch bytes, never from
# any final child-writable file; the subject-readable mirror copies
# published into the fixture seam are byte-identical and read-only.
# The closed case table, the offered truncation budget, the poll
# plan and the step budgets are code-defined BEFORE actual
# qualification; the native transport's delivery grouping, wall
# times, chunk ids and session identity are OBSERVED facts verified
# against this law, never declared by it.  One stream piece carries
# literal CRLF line endings so CRLF preservation is actually
# exercised by the raw-byte verification.
FORMAT_SEED_FILES: tuple[tuple[str, bytes], ...] = (
    ("read-0", b"slaif-format-read-0-017aj\n" * 19),
    ("stream-piece-0", b"slaif-format-piece-0-017aj\n" * 16),
    ("stream-piece-1", b"slaif-format-piece-1-017aj\r\n" * 16),
    (
        "stream-piece-2",
        "slaif-format-piece-2-017aj-\u00fc\u00f1\u00ef\u00e7\u00f8d\u00e9\n".encode("utf-8") * 16,
    ),
    ("trunc-0", b"slaif-format-trunc-0-017aj\n" * 32),
)
FORMAT_SEED_MAX_FILES = 8
FORMAT_SEED_MAX_TOTAL_BYTES = 128 * 1024
# the subject-readable mirror seam (the existing subject-owned /tmp
# shared scratch): read-only controller-published copies under a
# controller-owned mode-0555 directory (the sticky bit keeps the
# subject from unlinking foreign-owned entries)
FORMAT_SEED_DIR = "/tmp/slaif-format-seed"
FORMAT_SEED_DIR_MODE = 0o555
FORMAT_SEED_FILE_MODE = 0o444
# the closed transport byte law: the nested exec tool streams the
# process's raw bytes (the pinned default tty=false path); strict
# verification requires the observed full output to byte-match the
# immutable expected content.  The outer attach PTY line discipline
# establishes NO transformation of nested tool output, and an
# observed byte form that differs from the immutable seed is an
# honest source-byte mismatch (a closed truthful partial), never an
# inferred transformation
# the OFFERED max_output_tokens of the deliberate bounded
# truncation case: the ACTUAL exec argument.  The native policy
# takes the smaller of this offer and its own exec truncation
# policy (pinned model_output_policy), so the strict verification
# recovers the EFFECTIVE budget by unique formatter match against
# the immutable seed — never an assumed byte cut
FORMAT_TRUNCATED_MAX_OUTPUT_TOKENS = 24
# the EXPLICIT initial yield of the stream case: within the pinned
# clamp range [250, 30000] ms and strictly below the first bounded
# inter-piece sleep, so the initial result is a running frame
# (the pinned 10000 ms default yield would ordinarily complete the
# 4 s workload inside the initial exec; the closed plan never
# depends on lucky scheduling).  The other cases complete within
# their default yield and declare single-final.
FORMAT_STREAM_YIELD_TIME_MS = 500
# the closed per-result observed-output bound (transport) and the
# hard bound on one wrapper before any parsing
FORMAT_RESULT_MAX_BYTES = 4096
FORMAT_WRAPPER_MAX_BYTES = 16 * 1024
# the finite step budgets: at most 16 issued semantic calls (the
# four exec cases plus at most 12 empty-stdin polls across the ONE
# running process), at most 20 model POSTs; the stream case's
# inter-piece sleeps stay at most 5 s total and are FORMAT ONLY
# (never a newly earned read family)
FORMAT_MAX_ISSUED = 16
FORMAT_MAX_POLLS = 12
FORMAT_MAX_POSTS = 20
FORMAT_MAX_SLEEP_SECONDS = 5
# the 256 KiB TOTAL SERIALIZED selected record bound (intersects,
# never replaces, the existing owner ledger/END bounds)
FORMAT_SNAPSHOT_MAX_BYTES = 256 * 1024
# the pinned wrapper bound for the wall-time section (the scenario
# runs inside the original owner END; a far larger observed wall
# time is a closed refusal, not a parse)
FORMAT_WALL_TIME_MAX_SECONDS = 2048
# the closed serial case table (code-defined before actual
# qualification): exact command, kind, seed binding, the offered
# truncation budget, the explicit yield and the closed declared
# result chain.  The commands are bounded literal forms (a single
# literal cat, the bounded literal && chain of literal cats with
# the bounded inter-piece sleeps, and the closed no-output
# literal) — no arbitrary shell, stdin or code evaluation.
# single-final declares one completed result;
# initial-running-poll-final declares the ONE running process: the
# initial running result plus at most FORMAT_MAX_POLLS empty-stdin
# polls, the LAST of which is the completion poll.
FORMAT_CASES: tuple[dict, ...] = (
    {
        "case": "read-complete",
        "kind": "read",
        "seed_files": ("read-0",),
        "command": f"cat {FORMAT_SEED_DIR}/read-0",
        "sleep_seconds": 0,
        "max_output_tokens": None,
        "yield_time_ms": None,
        "chain": "single-final",
    },
    {
        "case": "running-chunks",
        "kind": "stream",
        "seed_files": ("stream-piece-0", "stream-piece-1", "stream-piece-2"),
        "command": (
            f"cat {FORMAT_SEED_DIR}/stream-piece-0 && sleep 2"
            f" && cat {FORMAT_SEED_DIR}/stream-piece-1 && sleep 2"
            f" && cat {FORMAT_SEED_DIR}/stream-piece-2"
        ),
        "sleep_seconds": 4,
        "max_output_tokens": None,
        "yield_time_ms": FORMAT_STREAM_YIELD_TIME_MS,
        "chain": "initial-running-poll-final",
    },
    {
        "case": "empty-output",
        "kind": "empty",
        "seed_files": (),
        "command": "true",
        "sleep_seconds": 0,
        "max_output_tokens": None,
        "yield_time_ms": None,
        "chain": "single-final",
    },
    {
        "case": "bounded-truncated",
        "kind": "truncated",
        "seed_files": ("trunc-0",),
        "command": f"cat {FORMAT_SEED_DIR}/trunc-0",
        "sleep_seconds": 0,
        "max_output_tokens": FORMAT_TRUNCATED_MAX_OUTPUT_TOKENS,
        "yield_time_ms": None,
        "chain": "single-final",
    },
)
# The closed ISSUED argument shapes of the scenario (the exact
# schema-evidenced native tool names observed at the AH round:
# exec_command with required cmd; write_stdin with required
# session_id and present chars): a bounded literal command plus,
# per closed spec, the explicit initial yield and/or the closed
# offered token budget, and the empty-stdin poll bound to the
# observed session identity of THIS run's validated initial
# running result — never callID, never a guessed 0.
FORMAT_EXEC_TOOL = "exec_command"
FORMAT_POLL_TOOL = "write_stdin"
# the pinned native wrapper section labels (official pinned source,
# core/src/tools/context.rs ExecCommandToolOutput::response_header):
# the optional sections appear in exactly this order, joined by LF,
# and the complete wrapper is the header plus LF plus the output
# section — the Output: line is followed by LF even when the
# output is empty (pinned format(header + LF + output))
_FORMAT_SECTION_CHUNK = "Chunk ID: "
_FORMAT_SECTION_WALL = "Wall time: "
_FORMAT_SECTION_EXIT = "Process exited with code "
_FORMAT_SECTION_RUNNING = "Process running with session ID "
_FORMAT_SECTION_TOKENS = "Original token count: "
_FORMAT_OUTPUT_DELIMITER = "Output:"
_FORMAT_OMISSION_MARKER_RE = re.compile(r"\.\.\. \d+ bytes omitted \.\.\.")
_FORMAT_CHUNK_ID_RE = re.compile(r"^[0-9a-f]{6}$")
_FORMAT_WALL_NUM_RE = re.compile(r"^[0-9]{1,4}\.[0-9]{4}$")
_FORMAT_I32_TOKEN_RE = re.compile(r"^-?[0-9]{1,10}$")
_FORMAT_UINT_TOKEN_RE = re.compile(r"^[0-9]{1,10}$")
_FORMAT_I32_MIN = -(2**31)
_FORMAT_I32_MAX = 2**31 - 1
# finite pre-conversion bound for the optional original-token-count
# section (far above any scenario value; an overlong or out-of-
# range token is a closed refusal, never a pathological int)
_FORMAT_MAX_HEADER_TOKENS = 10_000_000
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

    def set_deadline_absolute(self, anchor: float) -> None:
        """Set the deadline to the ABSOLUTE monotonic anchor
        itself (the SAME original owner END transported by the
        trusted config channel): the ledger expires AT the
        anchor, never at a later clock reading plus a relative
        remainder (``clock() + (anchor - earlier_clock())``
        would extend the original END by the elapsed time
        between the two reads).  Set-once, finite, in the
        future, and within the ledger's own lifetime bound."""
        if self.deadline_monotonic() is not None:
            raise FixtureError("deadline is set once; it never resets")
        if not isinstance(anchor, (int, float)) or isinstance(anchor, bool):
            raise FixtureError("deadline anchor must be a finite positive number")
        if not math.isfinite(anchor) or anchor <= 0:
            raise FixtureError("deadline anchor must be a finite positive number")
        remaining = anchor - self._clock()
        if remaining <= 0:
            raise FixtureError("deadline anchor is already past")
        if remaining > self.budgets.lifetime_seconds:
            raise BudgetExceeded("budget bound exceeded: lifetime_seconds")
        self.deadline_seconds = float(remaining)
        self._deadline_monotonic = float(anchor)

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
        "masked_null_aliases",
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

# Closed universe of the field vocabulary the fixed-format
# validation messages may reference: the union of EVERY closed
# record field set plus the fixed identity-check labels used in
# identity/bound message text.  The host runner's diagnostic
# channel admits a model validation message ONLY when its field is
# a member of this universe (finite, explicit — no arbitrary
# field text).
VALIDATION_FIELD_UNIVERSE = frozenset(
    _ARTIFACT_FIELDS
    | _EXEC_FIELDS
    | _DIAGNOSTIC_FIELDS
    | _QUIESCE_FIELDS
    | _SNAPSHOT_FIELDS
    | _TEARDOWN_FIELDS
    | _PUBLISH_FIELDS
    | _PROFILE_FIELDS
    | _CI_SUMMARY_FIELDS
    | {
        "api_identity",
        "bytes_identity",
        "name-count-identity",
        "outcome_identity",
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
    The fixed-21002 subject law stays byte-for-byte the original: the
    closed core's identity checks refuse the v2 tag and any other
    subject, and the v2 validator refuses this v1 tag.
    """
    _expect_tag(record, SCHEMA_EXEC_MEASUREMENT)
    _expect_field_set(record, _EXEC_FIELDS)
    _validate_exec_measurement_core(record, budgets, SUBJECT_UID, SUBJECT_UID)


def _validate_exec_measurement_core(
    record: dict,
    budgets: FixtureBudgets,
    subject_uid: int,
    subject_gid: int,
) -> None:
    """Shared closed structural core of the exec-measurement
    record: the SAME complete facts and error law for the
    fixed-21002 v1 record and the owner-UID v2 record; only the
    expected subject identity differs (UID and GID INDEPENDENT,
    never assumed equal)."""
    if _int_field(record, "uid") != subject_uid:
        raise FixtureError("closed record field identity invalid: uid")
    if _int_field(record, "gid") != subject_gid:
        raise FixtureError("closed record field identity invalid: gid")
    groups = record["groups"]
    # Measured group membership: on Linux getgroups() MAY include
    # the effective gid (the actual array is measured, not assumed),
    # so the ONLY group sets that add no privilege for the confined
    # subject are the empty list and the subject's own primary gid
    # ALONE.  Elements must be exact integers (bool and numeric
    # float equality are not gids); root, foreign, mixed, duplicate,
    # float, bool, string or negative entries all fail closed (two
    # finite variants — no arbitrary nonempty-group waiver).
    if (
        not isinstance(groups, list)
        or any(isinstance(g, bool) or not isinstance(g, int) for g in groups)
        or groups not in ([], [subject_gid])
    ):
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
    # Masked /dev/null file aliases (runc maskPaths): the strictly
    # evidenced device-surface count — counted, never writable data.
    if _int_field(record, "masked_null_aliases") < 0:
        raise FixtureError("closed record field state invalid: masked_null_aliases")
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
    # Coherent finite table relation: the documented data mounts and
    # the masked /dev/null aliases are distinct records WITHIN the
    # scanned mount table, and the table itself is bounded by the
    # stand-in scanner's closed record cap.
    if (
        len(mounts) + _int_field(record, "masked_null_aliases")
        > _int_field(record, "mounts_scanned")
        or _int_field(record, "mounts_scanned") > MOUNTINFO_SCANNER_MAX_RECORDS
    ):
        raise FixtureError("closed record field state invalid: mounts_scanned")
    _bool_field(record, "rootfs_readonly", True)
    if _int_field(record, "controller_pid1_uid") != CONTROLLER_UID:
        raise FixtureError("closed record field identity invalid: controller_pid1_uid")
    _bool_field(record, "private_pid1_exempt", True)
    # Host parent isolation measured FROM the subject exec identity:
    # the
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


def _check_v2_subject_id(value: object, name: str) -> None:
    """Closed v2 subject-ID expectation law: the expected UID/GID
    arrive from the VERIFIED owner state (never from a caller
    record); they must be strict nonroot integers inside the
    finite Linux id range and must be DISTINCT from the reserved
    controller identity (21001 — the same ID for the fixed
    controller UID and GID).  A malformed or colliding
    expectation is a fixed non-echoing refusal."""
    if (
        isinstance(value, bool)
        or not isinstance(value, int)
        or not (1 <= value <= 4294967294)
        or value == CONTROLLER_UID
    ):
        raise FixtureError(f"closed record field identity invalid: {name}")


def validate_exec_measurement_v2(
    record: dict, budgets: FixtureBudgets, subject_uid: int, subject_gid: int
) -> None:
    """Closed owner-UID exec measurement record (v2).

    The SAME complete actual facts as the v1 record, measured under
    the frozen owner-profile subject (UID and GID INDEPENDENT; the
    exec user is never assumed ``uid:uid``).  The v2 tag and the v1
    fixed-21002 tag refuse each other; the measured identity must
    equal the verified owner expectation, and the controller
    identity (21001) plus every other confinement fact stay
    fixed."""
    _check_v2_subject_id(subject_uid, "subject_uid")
    _check_v2_subject_id(subject_gid, "subject_gid")
    _expect_tag(record, SCHEMA_EXEC_MEASUREMENT_V2)
    _expect_field_set(record, _EXEC_FIELDS)
    _validate_exec_measurement_core(record, budgets, subject_uid, subject_gid)


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


# -- the strict pinned native wrapper parser -----------------------------
def _parse_header_i32(token: str) -> int:
    """Finite ASCII decimal signed-32 conversion: the pinned exit /
    process ID sections are i32; a non-ASCII digit, an overlong or
    an out-of-range token is a fixed typed refusal (no offending
    value is echoed)."""
    if not _FORMAT_I32_TOKEN_RE.fullmatch(token):
        raise FixtureError("format-wrapper-section")
    value = int(token)
    if not _FORMAT_I32_MIN <= value <= _FORMAT_I32_MAX:
        raise FixtureError("format-wrapper-section")
    return value


def parse_native_tool_wrapper(text: object) -> dict:
    """Strict parser for the pinned native exec tool wrapper.

    The complete wrapper is the header plus LF plus the output
    section (pinned ExecCommandToolOutput::response_text:
    format(header + LF + output)) — the Output: line is followed by
    LF even when the output is empty.  The header is the pinned
    section order joined by LF: the optional Chunk ID (the pinned
    6-lowercase-hex generator form), the wall time with FOUR
    decimals, the optional exit / running / original token count
    sections.  The output section is everything after the
    delimiter, byte-exact.  Returns a closed fact dict; every
    grammar or encoding violation is a fixed typed refusal."""
    if not isinstance(text, str):
        raise FixtureError("format-wrapper-type")
    try:
        encoded = text.encode("utf-8")
    except UnicodeEncodeError:
        # a lone surrogate (or other non-encodable content) is
        # malformed Unicode, refused before any parsing
        raise FixtureError("format-wrapper-encoding") from None
    if len(encoded) > FORMAT_WRAPPER_MAX_BYTES:
        raise FixtureError("format-wrapper-bound")
    delimiter = "\n" + _FORMAT_OUTPUT_DELIMITER + "\n"
    index = text.find(delimiter)
    if index < 0:
        raise FixtureError("format-wrapper-delimiter")
    header = text[:index]
    output = text[index + len(delimiter) :]
    sections = header.split("\n")
    if not 1 <= len(sections) <= 5:
        raise FixtureError("format-wrapper-sections")
    facts: dict = {
        "chunk_id": None,
        "wall_time": None,
        "exit_code": None,
        "session_id": None,
        "original_token_count": None,
        "output": output,
    }
    i = 0
    if sections[i].startswith(_FORMAT_SECTION_CHUNK):
        chunk = sections[i][len(_FORMAT_SECTION_CHUNK) :]
        if not _FORMAT_CHUNK_ID_RE.fullmatch(chunk):
            raise FixtureError("format-wrapper-section")
        facts["chunk_id"] = chunk
        i += 1
    if i >= len(sections) or not sections[i].startswith(_FORMAT_SECTION_WALL):
        raise FixtureError("format-wrapper-section")
    wall = sections[i][len(_FORMAT_SECTION_WALL) :]
    if not wall.endswith(" seconds"):
        raise FixtureError("format-wrapper-section")
    number = wall[: -len(" seconds")]
    if not _FORMAT_WALL_NUM_RE.fullmatch(number):
        raise FixtureError("format-wrapper-section")
    if float(number) > FORMAT_WALL_TIME_MAX_SECONDS:
        raise FixtureError("format-wrapper-bound")
    facts["wall_time"] = number
    i += 1
    if i < len(sections) and sections[i].startswith(_FORMAT_SECTION_EXIT):
        facts["exit_code"] = _parse_header_i32(sections[i][len(_FORMAT_SECTION_EXIT) :])
        i += 1
    if i < len(sections) and sections[i].startswith(_FORMAT_SECTION_RUNNING):
        facts["session_id"] = _parse_header_i32(sections[i][len(_FORMAT_SECTION_RUNNING) :])
        i += 1
    if i < len(sections) and sections[i].startswith(_FORMAT_SECTION_TOKENS):
        token = sections[i][len(_FORMAT_SECTION_TOKENS) :]
        if not _FORMAT_UINT_TOKEN_RE.fullmatch(token):
            raise FixtureError("format-wrapper-section")
        value = int(token)
        if value > _FORMAT_MAX_HEADER_TOKENS:
            raise FixtureError("format-wrapper-section")
        facts["original_token_count"] = value
        i += 1
    if i != len(sections):
        raise FixtureError("format-wrapper-sections")
    return facts


# -- the pinned truncation formatter mirror -------------------------------
# Strict mirrors of the pinned official source (utils/string
# truncate.rs and utils/output-truncation lib.rs at the pinned
# revision): the 4-bytes-per-token approximation, the floor/ceil
# UTF-8 BYTE-boundary split at half the byte budget, the head/tail
# retention with the pinned marker, and the formatted warning over
# the approximate original token count and total output lines
# (Rust str::lines semantics: LF or CRLF breaks, a final break
# ignored, a lone CR never breaks).  This is the native
# output-format heuristic — verification, not acquisition.
_FORMAT_APPROX_BYTES_PER_TOKEN = 4


def _approx_token_count_bytes(n_bytes: int) -> int:
    return (n_bytes + _FORMAT_APPROX_BYTES_PER_TOKEN - 1) // _FORMAT_APPROX_BYTES_PER_TOKEN


def _floor_char_boundary(text: str, n: int) -> int:
    """The largest UTF-8 char-boundary BYTE index <= n (pinned
    str::floor_char_boundary semantics)."""
    total = len(text.encode("utf-8"))
    n = min(max(n, 0), total)
    index = 0
    for char in text:
        next_index = index + len(char.encode("utf-8"))
        if next_index <= n:
            index = next_index
        else:
            break
    return index


def _ceil_char_boundary(text: str, n: int) -> int:
    """The smallest UTF-8 char-boundary BYTE index >= n (pinned
    str::ceil_char_boundary semantics)."""
    total = len(text.encode("utf-8"))
    n = min(max(n, 0), total)
    if n == 0:
        return 0
    index = 0
    for char in text:
        index += len(char.encode("utf-8"))
        if index >= n:
            return index
    return total


def _plan_token_truncation(text: str, max_tokens: int):
    """Pinned plan_token_truncation mirror: None when the text
    already fits the 4-byte-per-token budget (including the
    empty-text zero-budget case), otherwise the closed
    (start, end, marker) removal plan at BYTE indices — a zero
    budget over nonempty text truncates to the marker alone, as
    pinned."""
    max_bytes = max_tokens * _FORMAT_APPROX_BYTES_PER_TOKEN
    size = len(text.encode("utf-8"))
    if size <= max_bytes:
        return None
    left_budget = max_bytes // 2
    right_budget = max_bytes - left_budget
    start = _floor_char_boundary(text, left_budget)
    end = _ceil_char_boundary(text, size - right_budget)
    removed_tokens = _approx_token_count_bytes(size - max_bytes)
    return start, end, f"\u2026{removed_tokens} tokens truncated\u2026"


def truncate_middle_with_token_budget(text: str, max_tokens: int) -> str:
    """Pinned truncate_middle_with_token_budget mirror (result
    text): head + marker + tail.  The pinned source slices the
    UTF-8 encoding at BYTE indices, so the mirror slices the
    encoding at the same indices, never the character sequence."""
    plan = _plan_token_truncation(text, max_tokens)
    if plan is None:
        return text
    start, end, marker = plan
    data = text.encode("utf-8")
    return data[:start].decode("utf-8") + marker + data[end:].decode("utf-8")


def _rust_lines_count(text: str) -> int:
    """Pinned Rust str::lines count: LF or CRLF breaks, break
    characters excluded, a final break ignored, a lone CR never
    breaks, an empty string has zero lines."""
    if not text:
        return 0
    count = text.count("\n")
    if not text.endswith("\n"):
        count += 1
    return count


def format_truncate_text(text: str, max_tokens: int) -> str:
    """Pinned formatted_truncate_text mirror for the Tokens
    policy: unchanged within the 4-byte-per-token budget,
    otherwise the pinned two-line warning (approximate original
    token count, total output lines, blank line) over the UTF-8
    head/tail truncation with the pinned marker."""
    size = len(text.encode("utf-8"))
    if size <= max_tokens * _FORMAT_APPROX_BYTES_PER_TOKEN:
        return text
    truncated = truncate_middle_with_token_budget(text, max_tokens)
    return (
        "Warning: truncated output (original token count: "
        f"{_approx_token_count_bytes(size)})\n"
        f"Total output lines: {_rust_lines_count(text)}\n\n{truncated}"
    )


_FORMAT_SNAPSHOT_FIELDS = frozenset(
    {
        "synthetic",
        "issued_calls",
        "cases",
        "seed",
        "seed_total_bytes",
        "originals_bytes",
        "originals_sha256",
        "exporter_uid",
        "exported_before_teardown",
        "model_posts",
        "controller_ledger",
        "polls",
        "final_state",
    }
)
# the DISTINCT safe partial snapshot field set: the complete
# form's closed facts plus the explicit honest qualification
# fact (the complete form's own closed law is unchanged and
# separate)
_FORMAT_SNAPSHOT_PARTIAL_FIELDS = _FORMAT_SNAPSHOT_FIELDS | frozenset({"qualification"})
# the closed PENDING case descriptor: the exact closed case
# binding plus ONLY the retained verified frames (the dual
# numeric coordinates, the exact received wrapper text) and the
# retained poll count.  NO exit/verified/output-aggregate/
# truncation/completion field exists in the pending form, so a
# placeholder can never be minted as an observed fact
_FORMAT_CASE_PENDING_FIELDS = frozenset(
    {
        "case",
        "kind",
        "seed_files",
        "command",
        "call_id",
        "call_position",
        "arguments_sha256",
        "status",
        "results",
        "polls",
    }
)
_FORMAT_CASE_FIELDS = frozenset(
    {
        "case",
        "kind",
        "seed_files",
        "command",
        "call_id",
        "call_position",
        "arguments_sha256",
        "status",
        "exit",
        "session_id",
        "results",
        "output_bytes",
        "output_sha256",
        "nonempty_pieces",
        "polls",
        "truncated",
        "truncated_effective_tokens",
        "crlf",
        "non_ascii",
        "verified",
    }
)
# the closed per-result retained frame: the EXACT received wrapper
# text (byte-verified) bound to the issued call that produced it —
# the exact call ID and the numeric causal request position of
# that issue (a result without this association, or with a foreign
# or duplicated one, never enters the record)
_FORMAT_RESULT_FIELDS = frozenset({"call_id", "issued_position", "result_position", "wrapper"})


def _format_seed_law() -> tuple[tuple[str, bytes], ...]:
    """The closed seed set law: at most 8 files / 128 KiB total,
    nonempty unique names, the closed case table's sleeps within
    the total budget, the truncated case's offered budget
    positive, and the explicit stream yield within the pinned
    clamp range (re-derived on every use)."""
    for spec in FORMAT_CASES:
        if (
            spec["kind"] == "stream"
            and not (
                isinstance(spec["yield_time_ms"], int)
                and not isinstance(spec["yield_time_ms"], bool)
                and 250 <= spec["yield_time_ms"] <= 30_000
            )
        ) or (spec["kind"] != "stream" and spec["yield_time_ms"] is not None):
            raise FixtureError("format-seed-law")
    if (
        len(FORMAT_SEED_FILES) > FORMAT_SEED_MAX_FILES
        or sum(len(b) for _n, b in FORMAT_SEED_FILES) > FORMAT_SEED_MAX_TOTAL_BYTES
        or any(not isinstance(n, str) or not n for n, _b in FORMAT_SEED_FILES)
        or len({n for n, _b in FORMAT_SEED_FILES}) != len(FORMAT_SEED_FILES)
        or sum(spec["sleep_seconds"] for spec in FORMAT_CASES) > FORMAT_MAX_SLEEP_SECONDS
        or len(FORMAT_CASES) != 4
        or any(
            spec["sleep_seconds"] < 0
            or (
                spec["kind"] == "truncated"
                and (
                    not isinstance(spec["max_output_tokens"], int)
                    or isinstance(spec["max_output_tokens"], bool)
                    or spec["max_output_tokens"] <= 0
                )
            )
            or (spec["kind"] != "truncated" and spec["max_output_tokens"] is not None)
            for spec in FORMAT_CASES
        )
    ):
        raise FixtureError("format-seed-law")
    return FORMAT_SEED_FILES


def _format_expected_bytes(spec: dict) -> bytes:
    """The immutable expected FULL pre-truncation output of the
    case: the concatenated closed seed pieces (raw process bytes;
    the empty case is the empty content)."""
    seed = {name: data for name, data in FORMAT_SEED_FILES}
    return b"".join(seed[name] for name in spec["seed_files"])


def _format_exec_arguments(spec: dict) -> dict:
    """The exact closed issued arguments of the case's exec call:
    the bounded literal command plus, per closed spec, the
    explicit initial yield (stream case only) and/or the closed
    offered token budget (truncated case only)."""
    arguments: dict = {"cmd": spec["command"]}
    if spec["yield_time_ms"] is not None:
        arguments["yield_time_ms"] = spec["yield_time_ms"]
    if spec["max_output_tokens"] is not None:
        arguments["max_output_tokens"] = spec["max_output_tokens"]
    return arguments


def _format_poll_arguments(session_id: int) -> dict:
    """The exact closed issued arguments of the empty-stdin poll:
    the observed positive session ID of THIS run's validated
    initial running result (an exact non-bool int — never a
    guessed 0, never a coerced bool or float) and the closed
    empty chars literal."""
    if not isinstance(session_id, int) or isinstance(session_id, bool) or session_id <= 0:
        raise FixtureError("format-poll-arguments")
    return {"session_id": session_id, "chars": ""}


def format_arguments_exact(arguments: object, expected: dict) -> bool:
    """Typed-strict identity of ONE closed issued argument shape:
    the EXACT key set, the EXACT Python type per key, and the
    exact value.  Python dict equality is NOT exact identity —
    ``True == 1`` and ``1.0 == 1`` — so a bool or float standing
    in for a required integer, or any other type deviation,
    would pass loose comparison and mint a wrong issued
    argument identity.  The receiver never coerces: any
    deviation is a non-match the caller refuses with its closed
    token.  The same exact argument identity law applies at the
    consumer's snapshot re-validation AND the controller's
    historical replay verification."""
    if not isinstance(arguments, dict) or set(arguments) != set(expected):
        return False
    for key, expected_value in expected.items():
        value = arguments[key]
        if type(value) is not type(expected_value) or value != expected_value:
            return False
    return True


def format_frame_output_facts(wrapper_text: object) -> tuple[dict, bytes]:
    """The strict pinned wrapper parse plus the closed
    per-result transport law at the wire seam: the wrapper
    byte bound, the pinned grammar, the per-result
    observed-output bound and the omission-marker refusal.
    Returns (the closed fact dict, the EXACT observed output
    bytes); every violation is a fixed typed refusal.  The
    case-law layer re-verifies the retained wrappers through
    the SAME parser (a copied or replayed wrapper never mints
    facts)."""
    facts = parse_native_tool_wrapper(wrapper_text)
    output = facts["output"]
    data = output.encode("utf-8")
    if len(data) > FORMAT_RESULT_MAX_BYTES:
        raise FixtureError("format-result-output-bound")
    if _FORMAT_OMISSION_MARKER_RE.search(output):
        raise FixtureError("format-result-omission")
    return facts, data


def format_expected_exec_arguments(spec: dict) -> dict:
    """Public exact closed issued exec-argument shape of ONE
    closed case spec (the controller's historical replay
    verification compares against THIS typed shape)."""
    return _format_exec_arguments(spec)


def format_expected_poll_arguments(session_id: object) -> dict:
    """Public exact closed issued poll-argument shape bound to
    the validated positive stream session ID (see
    ``_format_poll_arguments``)."""
    return _format_poll_arguments(session_id)


_FORMAT_OFFERED_REQUIRED_CORE = {
    FORMAT_EXEC_TOOL: "cmd",
    FORMAT_POLL_TOOL: "session_id",
}
# the finite closed property-key universe: the exact type, the
# harmless documentation key and the scalar constraints that can
# be checked against ONE closed value without a general
# JSON-schema engine.  Every other keyword (allOf/anyOf/oneOf/
# not/pattern/$ref/items/additionalProperties/dependent*/...) is
# unsupported and refuses.
_FORMAT_OFFERED_PROPERTY_KEYS = frozenset(
    {
        "type",
        "description",
        "const",
        "enum",
        "minLength",
        "maxLength",
        "minimum",
        "maximum",
        "exclusiveMinimum",
        "exclusiveMaximum",
        "multipleOf",
    }
)


def _format_offered_property_ok(prop: object, value: object) -> bool:
    """Bounded closed check of ONE offered property against ONE
    closed argument value: the EXACT JSON type of the closed
    value plus only the finite closed scalar constraints, each
    verified NOT to exclude the closed value (a contradicting
    bound, const or enum member is a refusal).  For a strict
    integer closed value the pinned native advertises the JSON
    schema type ``number`` (validly admitting integers) and
    ``integer`` stays supported.  Unsupported keywords refuse;
    an EXPLICIT null constraint value is malformed and refuses
    (key presence, never .get() absence); length bounds are
    nonnegative non-bool integers (a fractional float bound is
    malformed, never a compatible rounding); numeric bounds
    must be finite and stay in their JSON type (ints are never
    float-widened, so a huge integer cannot leak
    OverflowError out of a closed check); the enum list is
    bounded before any scan.  No general JSON-schema engine, no
    nested evaluation and nothing is retained."""
    if not isinstance(prop, dict):
        return False
    for key in prop:
        if key not in _FORMAT_OFFERED_PROPERTY_KEYS:
            return False
    if "description" in prop and not isinstance(prop["description"], str):
        return False

    def _closed_number(bound: object) -> int | float | None:
        # a closed numeric constraint: a non-bool finite
        # scalar kept in its JSON type.  Ints are finite by
        # construction and are never float-widened (a huge
        # JSON integer must refuse/compare as a closed check,
        # never leak OverflowError through a conversion);
        # floats must be finite (NaN/Infinity are malformed
        # schema, not bounds).
        if isinstance(bound, bool):
            return None
        if isinstance(bound, int):
            return bound
        if isinstance(bound, float) and math.isfinite(bound):
            return bound
        return None

    if isinstance(value, str):
        if prop.get("type") != "string":
            return False
        length = len(value)
        for bound_key in ("minLength", "maxLength"):
            if bound_key not in prop:
                continue
            bound = prop[bound_key]
            # a length bound is a nonnegative non-bool
            # INTEGER: a fractional float bound is malformed
            # schema, never a compatible rounding of a length
            if type(bound) is not int or bound < 0:
                return False
            if bound_key == "minLength" and bound > length:
                return False
            if bound_key == "maxLength" and bound < length:
                return False
    elif isinstance(value, int) and not isinstance(value, bool):
        # the pinned native advertises its numeric arguments as
        # JSON schema ``number``; ``number`` validly admits the
        # strict integer closed values and ``integer`` stays
        # supported (the emitted/echoed arguments remain strict
        # actual integers either way)
        if prop.get("type") not in ("integer", "number"):
            return False
        for bound_key in (
            "minimum",
            "maximum",
            "exclusiveMinimum",
            "exclusiveMaximum",
        ):
            if bound_key not in prop:
                continue
            bound = _closed_number(prop[bound_key])
            if bound is None:
                return False
            exclusive = bound_key.startswith("exclusive")
            if bound_key in ("minimum", "exclusiveMinimum"):
                if value < bound or (exclusive and value == bound):
                    return False
            elif value > bound or (exclusive and value == bound):
                return False
        if "multipleOf" in prop:
            multiple = _closed_number(prop["multipleOf"])
            if multiple is None or multiple <= 0:
                return False
            if value % multiple != 0:
                return False
    else:
        return False
    if "const" in prop:
        const = prop["const"]
        if const is None or type(const) is not type(value) or const != value:
            return False
    if "enum" in prop:
        enum = prop["enum"]
        if (
            not isinstance(enum, list)
            or len(enum) > DIAGNOSTIC_MAX_REQUIRED_FIELDS
            or not any(type(member) is type(value) and member == value for member in enum)
        ):
            return False
    return True


def format_offered_tool_available(tools: object, tool_name: str, expected_arguments: dict) -> bool:
    """Bounded in-memory validation that the CURRENTLY OFFERED
    tools region actually offers ``tool_name`` in the closed
    Responses function shape that can express the closed argument
    shape about to be issued — decided BEFORE any registry
    issuance or scenario state adoption.  The closed law:

    - ONLY the two closed native tool names are decided (an
      unknown name fails closed);
    - ``tools`` is a list within the existing finite traversal
      bound; exactly ONE entry offers the exact closed name as a
      ``function`` tool (absent or duplicated entries are
      ambiguous, never alias-resolved or guessed);
    - that entry's ``parameters`` (the only accepted key; no
      aliases) is a JSON-schema object of type ``object``;
    - ``properties`` declares EVERY closed argument key, and each
      closed property keeps the exact closed value under the
      finite closed constraint law (``_format_offered_property_
      ok``): the exact JSON type, and no contradicting or
      unsupported constraint;
    - ``required`` is a plain unique string list within the
      existing finite bound; it must demand the KNOWN closed
      required argument (``cmd`` / ``session_id``) and nothing
      the closed shape cannot send (every required name is one of
      the closed keys).

    Returns a plain boolean; the raw schema is never copied or
    retained (capability decision only, no raw schema facts)."""
    core = _FORMAT_OFFERED_REQUIRED_CORE.get(tool_name)
    if core is None:
        return False
    if not isinstance(tools, list) or len(tools) > DIAGNOSTIC_MAX_TOOL_NAMES:
        return False
    matching: list[dict] = []
    for entry in tools:
        if (
            isinstance(entry, dict)
            and entry.get("type") == "function"
            and entry.get("name") == tool_name
        ):
            matching.append(entry)
    if len(matching) != 1:
        return False
    params = matching[0].get("parameters")
    if not isinstance(params, dict) or params.get("type") != "object":
        return False
    # the parent object schema is closed to the small declared
    # subset: the object type, the properties, the known-
    # required list, the harmless description key and the
    # pinned small boolean additionalProperties form (the
    # pinned built-in advertises false; either boolean value
    # can exclude none of the EXACTLY declared closed keys,
    # and every emitted key must still be declared).  Every
    # other parent validation keyword (not/allOf/anyOf/oneOf/
    # $ref/dependentRequired/maxProperties/patternProperties/
    # ...) is unsupported and refuses — it could exclude the
    # closed call without any property-level trace
    if set(params) - {
        "type",
        "properties",
        "required",
        "description",
        "additionalProperties",
    }:
        return False
    if "description" in params and not isinstance(params["description"], str):
        return False
    if "additionalProperties" in params and not isinstance(params["additionalProperties"], bool):
        return False
    properties = params.get("properties")
    if not isinstance(properties, dict):
        return False
    required = params.get("required")
    if not isinstance(required, list) or len(required) > DIAGNOSTIC_MAX_REQUIRED_FIELDS:
        return False
    seen_required: set[str] = set()
    for name in required:
        if not isinstance(name, str) or name in seen_required:
            return False
        seen_required.add(name)
        if name not in expected_arguments:
            return False
    if core not in seen_required:
        return False
    for key, value in expected_arguments.items():
        if not _format_offered_property_ok(properties.get(key), value):
            return False
    return True


def _format_reject_duplicate_keys(pairs: list[tuple[str, object]]) -> dict:
    """Strict JSON object decode for the closed history
    re-verification: a duplicated key in a re-sent argument
    object is a malformed re-issue (the silent last-wins
    decode would hide a changed argument), never a valid
    typed identity."""
    out: dict[str, object] = {}
    for key, value in pairs:
        if key in out:
            raise ValueError("duplicate key in closed arguments")
        out[key] = value
    return out


def _format_case_frame(case: dict, spec: dict) -> tuple[list[dict], list[dict], bytes]:
    """Strict-parse the case's retained frames in the OBSERVED
    result order (every wrapper re-verified from the retained
    exact text) and return the retained frames, the per-frame
    facts and the concatenated observed output bytes."""
    results = case["results"]
    if not isinstance(results, list) or not results or len(results) > 1 + FORMAT_MAX_POLLS:
        raise FixtureError("format-case-results")
    entries: list[dict] = []
    facts_list: list[dict] = []
    pieces: list[bytes] = []
    seen_call_ids: set[str] = set()
    for entry in results:
        if not isinstance(entry, dict) or set(entry) != _FORMAT_RESULT_FIELDS:
            raise FixtureError("format-case-results")
        if not _opaque_id(entry["call_id"]):
            raise FixtureError("format-case-results")
        if _int_field(entry, "issued_position") < 0:
            raise FixtureError("format-case-results")
        # the ACTUAL numeric position of the request that carried
        # the result, retained separately from (and strictly after)
        # the issuance position — never relabeled
        if _int_field(entry, "result_position") < 0:
            raise FixtureError("format-case-results")
        if entry["call_id"] in seen_call_ids:
            raise FixtureError("format-case-duplicate")
        seen_call_ids.add(entry["call_id"])
        facts = parse_native_tool_wrapper(entry["wrapper"])
        output = facts["output"]
        data = output.encode("utf-8")
        if len(data) > FORMAT_RESULT_MAX_BYTES:
            raise FixtureError("format-case-output-bound")
        # the closed scenario's outputs stay far below the native
        # collection cap; an observed omission marker is an
        # out-of-scenario fact, never a verified frame
        if _FORMAT_OMISSION_MARKER_RE.search(output):
            raise FixtureError("format-case-omission")
        entries.append(entry)
        facts_list.append(facts)
        pieces.append(data)
    return entries, facts_list, b"".join(pieces)


def _validate_format_case_facts(
    case: dict, spec: dict, entries: list[dict], facts_list: list[dict], output: bytes
) -> int:
    """The shared per-case closed facts over the observed output;
    returns the case's poll count."""
    if case["status"] != "completed" or case["verified"] is not True:
        raise FixtureError("format-case-state")
    if _int_field(case, "exit") != 0:
        raise FixtureError("format-case-state")
    if case["truncated"] is not (spec["kind"] == "truncated"):
        raise FixtureError("format-case-state")
    if not _is_sha256(case["output_sha256"]):
        raise FixtureError("format-case-digest")
    if not isinstance(case["crlf"], bool) or not isinstance(case["non_ascii"], bool):
        raise FixtureError("format-case-fields")
    if _int_field(case, "output_bytes") != len(output):
        raise FixtureError("format-case-output")
    if len(output) > FORMAT_RESULT_MAX_BYTES:
        raise FixtureError("format-case-output-bound")
    if sha256_bytes(output) != case["output_sha256"]:
        raise FixtureError("format-case-digest")
    nonempty = sum(1 for facts in facts_list if facts["output"] != "")
    if _int_field(case, "nonempty_pieces") != nonempty:
        raise FixtureError("format-case-state")
    if case["crlf"] is not (b"\r\n" in output):
        raise FixtureError("format-case-state")
    if case["non_ascii"] is not any(byte >= 0x80 for byte in output):
        raise FixtureError("format-case-state")
    # the optional original-token-count section is PER collected
    # chunk (pinned process_manager builds it from THAT result's
    # collected output), never the full eventual command output:
    # each frame is checked against its own observed bytes, and
    # the deliberately truncated frame against the frame's
    # original (pre-truncation) seed bytes
    seed_full = _format_expected_bytes(spec)
    for facts in facts_list:
        count = facts["original_token_count"]
        if count is None:
            continue
        if spec["kind"] == "truncated":
            expected_count = _approx_token_count_bytes(len(seed_full))
        else:
            expected_count = _approx_token_count_bytes(len(facts["output"].encode("utf-8")))
        if count != expected_count:
            raise FixtureError("format-case-token-count")
    if spec["chain"] == "single-final":
        if len(facts_list) != 1:
            raise FixtureError("format-case-chain")
        if facts_list[0]["exit_code"] != 0:
            raise FixtureError("format-case-chain")
        if _int_field(case, "polls") != 0:
            raise FixtureError("format-case-chain")
        if case["session_id"] is not None:
            raise FixtureError("format-case-chain")
        return 0
    # initial-running-poll-final: the ONE running process — the
    # initial exec result plus at most FORMAT_MAX_POLLS empty-
    # stdin polls, the LAST poll being the completion
    if not 2 <= len(facts_list) <= 1 + FORMAT_MAX_POLLS:
        raise FixtureError("format-case-chain")
    polls = len(facts_list) - 1
    if _int_field(case, "polls") != polls:
        raise FixtureError("format-case-chain")
    session = case["session_id"]
    if not isinstance(session, int) or isinstance(session, bool) or session <= 0:
        raise FixtureError("format-case-chain")
    first = facts_list[0]
    if first["exit_code"] is not None or first["session_id"] != session:
        raise FixtureError("format-case-chain")
    for facts in facts_list[1:-1]:
        if facts["exit_code"] is not None or facts["session_id"] != session:
            raise FixtureError("format-case-chain")
    last = facts_list[-1]
    if last["exit_code"] != 0:
        raise FixtureError("format-case-chain")
    # the completion poll may omit the session ID (pinned:
    # completion can omit it); a present one must be the same
    if last["session_id"] is not None and last["session_id"] != session:
        raise FixtureError("format-case-chain")
    # the multi-chunk qualification: at least TWO nonempty
    # observed output pieces across the verified exec/poll
    # results — an initial empty running result plus one final
    # full-output poll does NOT qualify
    if nonempty < 2:
        raise FixtureError("format-case-multichunk")
    return polls


def _validate_format_case(case: dict, spec: dict) -> int:
    """The closed per-case law: the exact closed case binding, the
    strictly verified frames against the immutable pre-launch
    seed identity, and the declared chain.  Returns the case's
    poll count."""
    if (
        case["case"] != spec["case"]
        or case["kind"] != spec["kind"]
        or not isinstance(case["seed_files"], list)
        or tuple(case["seed_files"]) != spec["seed_files"]
        or case["command"] != spec["command"]
        or not _opaque_id(case["call_id"])
        or not _is_sha256(case["arguments_sha256"])
        or _int_field(case, "call_position") < 0
    ):
        raise FixtureError("format-case-binding")
    entries, facts_list, output = _format_case_frame(case, spec)
    if spec["kind"] == "truncated":
        # the deliberate bounded truncation: the observed output
        # must be the PINNED formatter applied to the immutable
        # seed under exactly ONE effective token budget within
        # the offered budget (the native policy takes the smaller
        # of the offer and its own exec policy, so the effective
        # budget is recovered by unique match, never assumed);
        # non-acquiring by construction
        effective = case["truncated_effective_tokens"]
        if (
            not isinstance(effective, int)
            or isinstance(effective, bool)
            or effective < 1
            or effective > FORMAT_TRUNCATED_MAX_OUTPUT_TOKENS
        ):
            raise FixtureError("format-case-truncation")
        seed_text = _format_expected_bytes(spec).decode("utf-8")
        matches = [
            tokens
            for tokens in range(1, FORMAT_TRUNCATED_MAX_OUTPUT_TOKENS + 1)
            if format_truncate_text(seed_text, tokens).encode("utf-8") == output
        ]
        if len(matches) != 1 or effective != matches[0]:
            raise FixtureError("format-case-truncation")
    else:
        if case["truncated_effective_tokens"] is not None:
            raise FixtureError("format-case-truncation")
        # the closed transport byte law: the observed full output
        # is the immutable expected content byte-for-byte (the
        # pinned raw tty=false path); an observed byte form that
        # differs is an honest source-byte mismatch
        if output != _format_expected_bytes(spec):
            raise FixtureError("format-case-source-mismatch")
    return _validate_format_case_facts(case, spec, entries, facts_list, output)


def _validate_format_issued_calls(record: dict, cases: list[dict]) -> None:
    """The closed issued-identity law: at most the finite budget,
    globally unique issued call IDs across the complete registry,
    strictly increasing causal positions, ONLY the two closed
    native tools, the exact closed argument shapes verified by
    TYPED-STRICT identity (a bool or float standing in for a
    required integer is refused, never coerced), the digest
    bound to the canonical bytes of the TYPED EXPECTED shape
    (not the provided arguments' own bytes), the serial
    binding of the four exec calls (in the
    closed case order), and the per-result association: the first
    retained result of each case is its issued exec result, and
    every later stream result is the result of the corresponding
    issued empty-stdin poll in order (one result per issue; a
    swapped, foreign, duplicated or missing association is a
    closed refusal).  Each retained result keeps its ACTUAL
    numeric request position distinctly from the issued call's
    own position: verified strictly after its own issuance, and
    over the complete ordered registry (one outstanding call at
    a time) never after the NEXT issued call's position - the
    same POST may validate the prior result and issue the next
    call at that very position."""
    calls = record["issued_calls"]
    if not isinstance(calls, list) or len(calls) > FORMAT_MAX_ISSUED:
        raise FixtureError("format-issued-bound")
    stream_session = cases[1]["session_id"]
    entries: list[tuple[int, dict]] = []
    seen_call_ids: set[str] = set()
    last_position = -1
    for call in calls:
        if not isinstance(call, dict) or set(call) != {
            "family",
            "name",
            "call_id",
            "position",
            "arguments_sha256",
            "arguments",
        }:
            raise FixtureError("format-issued-fields")
        _enum_field(call, "family", TOOL_FAMILY_ISSUABLE)
        if not _opaque_id(call["name"]) or not _opaque_id(call["call_id"]):
            raise FixtureError("format-issued-fields")
        # the registry issues each call ID at most once for the
        # whole run: a reused ID under another family/name or
        # with changed arguments is a closed conflict, never a
        # silent rebind
        if call["call_id"] in seen_call_ids:
            raise FixtureError("format-issued-duplicate")
        seen_call_ids.add(call["call_id"])
        position = _int_field(call, "position")
        if position <= last_position:
            raise FixtureError("format-issued-position")
        last_position = position
        arguments = call["arguments"]
        if call["name"] == FORMAT_EXEC_TOOL:
            # the EXACT closed issued shape, verified by
            # typed-strict identity (Python dict equality
            # alone is not identity: True == 1 and 1.0 == 1
            # would mint a coerced argument identity)
            matched = None
            for spec in FORMAT_CASES:
                if format_arguments_exact(arguments, _format_exec_arguments(spec)):
                    matched = spec
                    break
            if matched is None:
                raise FixtureError("format-issued-arguments")
            expected_arguments = _format_exec_arguments(matched)
        elif call["name"] == FORMAT_POLL_TOOL:
            expected_arguments = _format_poll_arguments(stream_session)
            if not format_arguments_exact(arguments, expected_arguments):
                raise FixtureError("format-issued-arguments")
        else:
            raise FixtureError("format-issued-name")
        # the digest binds the TYPED EXPECTED closed shape
        # itself (the canonical bytes of the expected
        # arguments): the provided arguments' own digest alone
        # would be self-consistent under a coerced shape
        if call["arguments_sha256"] != sha256_bytes(canonical_bytes(expected_arguments)):
            raise FixtureError("format-issued-digest")
        entries.append((position, call))
    exec_entries = [
        (position, call) for position, call in entries if call["name"] == FORMAT_EXEC_TOOL
    ]
    poll_entries = [
        (position, call) for position, call in entries if call["name"] == FORMAT_POLL_TOOL
    ]
    if len(exec_entries) != len(FORMAT_CASES):
        raise FixtureError("format-issued-exec")
    for (position, call), case, spec in zip(exec_entries, cases, FORMAT_CASES, strict=True):
        if (
            case["arguments_sha256"] != sha256_bytes(canonical_bytes(_format_exec_arguments(spec)))
            or case["arguments_sha256"] != call["arguments_sha256"]
            or case["call_id"] != call["call_id"]
            or case["call_position"] != position
        ):
            raise FixtureError("format-issued-binding")
    if cases[1]["polls"] != len(poll_entries):
        raise FixtureError("format-issued-polls")
    # per-result association (one result per corresponding
    # issue): the first retained result of each case is its
    # issued exec result and every later stream result is the
    # result of the corresponding issued empty-stdin poll in
    # order.  Each retained result keeps BOTH coordinates
    # distinctly: issued_position is the bound issued call's own
    # position, result_position the ACTUAL numeric position of
    # the request that carried the result - verified strictly
    # after its own issuance; a historical replay keeps the
    # original accepted position, never relabeled to the issue
    case_by_call_id = {case["call_id"]: case for case in cases}
    stream_results = cases[1]["results"][1:]
    if len(stream_results) != len(poll_entries):
        raise FixtureError("format-result-association")
    paired: list[tuple[int, int]] = []
    poll_index = 0
    for position, call in entries:
        if call["name"] == FORMAT_EXEC_TOOL:
            case = case_by_call_id.get(call["call_id"])
            if case is None or not case["results"]:
                raise FixtureError("format-result-association")
            result = case["results"][0]
        else:
            if poll_index >= len(stream_results):
                raise FixtureError("format-result-association")
            result = stream_results[poll_index]
            poll_index += 1
        if (
            result["call_id"] != call["call_id"]
            or _int_field(result, "issued_position") != position
        ):
            raise FixtureError("format-result-association")
        result_position = _int_field(result, "result_position")
        if result_position <= position:
            raise FixtureError("format-result-causality")
        paired.append((position, result_position))
    # serial chain causality over the COMPLETE ordered registry
    # (one outstanding call at a time): the prior result arrived
    # strictly after its own issuance and never after the NEXT
    # issued call's position - the same POST may validate the
    # prior result and issue the next call at that very
    # position, so equality is legal
    for (_issued, result_position), (next_position, _call) in zip(
        paired, entries[1:], strict=False
    ):
        if result_position > next_position:
            raise FixtureError("format-result-causality")
    if poll_entries:
        stream_position = cases[1]["call_position"]
        next_position = cases[2]["call_position"]
        for position, _call in poll_entries:
            if not stream_position < position < next_position:
                raise FixtureError("format-issued-polls")


def validate_format_snapshot_record(record: dict) -> None:
    """Closed selected format-capture snapshot (017-ai, the
    canonical 017-aj entry's format scenario).  The issued-
    identity law binds the EXACT closed issued argument shapes
    and the per-result association; the cases are the EXACT
    closed case table (fixed order, fixed command/kind/seed
    binding) with the EXACT retained verified wrappers strictly
    re-verified against the immutable pre-launch seed identity:
    the closed transport byte law, the declared chains, the
    per-chunk token-count metadata, the multi-chunk nonempty-
    piece qualification, and the pinned formatter truncation
    match.  The seed identity is the closed pre-launch seed set,
    the serialized SNAPSHOT record stays within the 256 KiB
    bound (the TOTAL selected-capture bound INCLUDING the outer
    identity metadata is enforced at the record consumer,
    producer and export seams, not here), and this is a
    DISTINCT closed record: the original selected
    snapshot keeps its exact historical field set and law.
    The truthful count/coordinate law is closed: model_posts
    is the model-POST count (every POST accepted or refused,
    within the finite POST bound) and the ledger request
    count is exactly model_posts plus the exporter's two
    closed charged commands; every recorded numeric position
    stays strictly below model_posts."""
    _expect_tag(record, SCHEMA_FORMAT_SNAPSHOT)
    _expect_field_set(record, _FORMAT_SNAPSHOT_FIELDS)
    _bool_field(record, "synthetic", True)
    _format_seed_law()
    cases = record["cases"]
    if not isinstance(cases, list) or len(cases) != len(FORMAT_CASES):
        raise FixtureError("format-cases-count")
    polls_total = 0
    last_position = -1
    for case, spec in zip(cases, FORMAT_CASES, strict=True):
        if not isinstance(case, dict) or set(case) != _FORMAT_CASE_FIELDS:
            raise FixtureError("format-cases-fields")
        polls_total += _validate_format_case(case, spec)
        if _int_field(case, "call_position") <= last_position:
            raise FixtureError("format-cases-position")
        last_position = _int_field(case, "call_position")
    _validate_format_issued_calls(record, cases)
    if _int_field(record, "polls") != polls_total or polls_total > FORMAT_MAX_POLLS:
        raise FixtureError("format-polls")
    seed = record["seed"]
    if (
        not isinstance(seed, list)
        or len(seed) != len(FORMAT_SEED_FILES)
        or any(
            not isinstance(entry, list)
            or len(entry) != 3
            or entry[0] != name
            or not _is_sha256(entry[1])
            or not isinstance(entry[2], int)
            or isinstance(entry[2], bool)
            or entry[2] != len(data)
            or entry[1] != sha256_bytes(data)
            for entry, (name, data) in zip(seed, FORMAT_SEED_FILES, strict=True)
        )
    ):
        raise FixtureError("format-seed")
    seed_total = _int_field(record, "seed_total_bytes")
    if seed_total != sum(entry[2] for entry in seed) or seed_total > FORMAT_SEED_MAX_TOTAL_BYTES:
        raise FixtureError("format-seed-bound")
    if _int_field(record, "originals_bytes") != seed_total:
        raise FixtureError("format-seed-state")
    if _sha256_field(record, "originals_sha256") != sha256_bytes(
        b"".join(data for _name, data in FORMAT_SEED_FILES)
    ):
        raise FixtureError("format-seed-digest")
    if _int_field(record, "exporter_uid") != CONTROLLER_UID:
        raise FixtureError("format-exporter-uid")
    _bool_field(record, "exported_before_teardown", True)
    ctl = record["controller_ledger"]
    if not isinstance(ctl, dict) or set(ctl) != {"requests", "output_bytes"}:
        raise FixtureError("format-ledger-fields")
    budgets = FixtureBudgets()
    # the truthful COUNT law: the ledger's request count is the
    # ACCOUNTED total — every model POST to the fixture (accepted
    # or refused) PLUS the exporter's closed ordered commands
    # (quiesce and export, each charged exactly once, both
    # required for exported_before_teardown).  The model POST
    # count is carried as its OWN closed field: conflating the
    # two ledgers would let a legitimate at-bound model-POST run
    # read its own codec bound off a different counter, and a
    # spaced synthetic request count could pose as the trace of
    # those POSTs.
    model_posts = _int_field(record, "model_posts")
    if (
        model_posts < 1
        or model_posts > min(FORMAT_MAX_POSTS, budgets.max_requests)
        or _int_field(ctl, "output_bytes") < 0
        or _int_field(ctl, "output_bytes") > budgets.output_cap_bytes
    ):
        raise FixtureError("format-ledger-bound")
    requests = _int_field(ctl, "requests")
    if requests != model_posts + 2:
        raise FixtureError("format-ledger-count")
    # the truthful coordinate law: every recorded numeric position
    # (each issued call, each case, each retained result) is the
    # 0-based index of an ACTUAL accounted model POST, so it must
    # stay strictly below the model POST count — the exporter's
    # closed commands carry no recorded positions, and spaced
    # synthetic ordinals can never pose as a POST-counter trace
    for call in record["issued_calls"]:
        if _int_field(call, "position") >= model_posts:
            raise FixtureError("format-coordinate-truth")
    for case in cases:
        if _int_field(case, "call_position") >= model_posts:
            raise FixtureError("format-coordinate-truth")
        for entry in case["results"]:
            if _int_field(entry, "result_position") >= model_posts:
                raise FixtureError("format-coordinate-truth")
    if record["final_state"] != "done":
        raise FixtureError("format-final-state")
    if len(canonical_bytes(record)) > FORMAT_SNAPSHOT_MAX_BYTES:
        raise FixtureError("format-serialized-bound")


def _validate_format_case_pending(case: dict, spec: dict) -> tuple[int, int | None]:
    """The closed PENDING case law (the safe partial form): the
    exact closed case binding, then ONLY the retained verified
    frames, each re-parsed and re-verified against the immutable
    pre-launch seed identity (the pinned wrapper grammar, the
    per-result output bound, the omission-marker refusal, the
    per-chunk token-count metadata).  The pending byte and
    session facts are RE-DERIVED from those frames: every
    retained stream frame is RUNNING, all bound to ONE positive
    session (re-derived, never caller-supplied), and the
    concatenated retained output is a verified prefix of the
    immutable expected content — the WHOLE source may already be
    observed under actual running wrappers while process
    completion has NOT been observed (byte equality does not
    prove completion); a non-prefix observed byte form is an
    honest source-byte mismatch.  The pending form
    carries NO completion facts: no exit, no verified flag, no
    output aggregates, no truncation qualification — those are
    committed by the complete case record only.  Returns (the
    retained poll count, the re-derived stream session or
    None)."""
    if (
        case["case"] != spec["case"]
        or case["kind"] != spec["kind"]
        or not isinstance(case["seed_files"], list)
        or tuple(case["seed_files"]) != spec["seed_files"]
        or case["command"] != spec["command"]
        or not _opaque_id(case["call_id"])
        or not _is_sha256(case["arguments_sha256"])
        or _int_field(case, "call_position") < 0
    ):
        raise FixtureError("format-case-binding")
    _enum_field(case, "status", ("pending",))
    results = case["results"]
    if not isinstance(results, list):
        raise FixtureError("format-case-results")
    if spec["kind"] != "stream":
        # a non-stream case finalizes on its one result: a
        # pending non-stream case has retained nothing and no
        # poll can exist (the poll target comes only from the
        # validated result of this run's actually issued exec)
        if results or _int_field(case, "polls") != 0:
            raise FixtureError("format-case-pending")
        return 0, None
    # stream: a just-issued exec has ZERO retained results (no
    # measured session, no poll target — never invented); with
    # retained frames, every frame is RUNNING (a retained
    # completion would have finalized the case), all bound to
    # ONE positive session (re-derived), at most the poll budget
    if not 0 <= len(results) <= FORMAT_MAX_POLLS:
        raise FixtureError("format-case-results")
    if _int_field(case, "polls") != (len(results) - 1 if results else 0):
        raise FixtureError("format-case-pending")
    if not results:
        return 0, None
    _entries, facts_list, output = _format_case_frame(case, spec)
    first = facts_list[0]
    if first["exit_code"] is not None:
        raise FixtureError("format-case-chain")
    session = first["session_id"]
    if not isinstance(session, int) or isinstance(session, bool) or session <= 0:
        raise FixtureError("format-case-chain")
    for facts in facts_list:
        if facts["exit_code"] is not None or facts["session_id"] != session:
            raise FixtureError("format-case-chain")
    # the per-chunk original-token-count law: each running frame
    # is checked against its OWN observed bytes
    for facts in facts_list:
        count = facts["original_token_count"]
        if count is None:
            continue
        if count != _approx_token_count_bytes(len(facts["output"].encode("utf-8"))):
            raise FixtureError("format-case-token-count")
    # the partial byte law: the concatenated retained output is a
    # verified prefix of the immutable expected content — the
    # WHOLE source may already be observed under actual running
    # wrappers while process completion has NOT been observed
    # (byte equality does not prove completion); a non-prefix
    # observed byte form is an honest source-byte mismatch
    expected = _format_expected_bytes(spec)
    if not expected.startswith(output):
        raise FixtureError("format-case-source-mismatch")
    return len(results) - 1, session


def _validate_format_issued_calls_partial(
    record: dict, cases: list[dict], stream_session: int | None
) -> int:
    """The closed issued-identity PREFIX law of the safe partial
    form: at most the finite budget, globally unique issued call
    IDs across the prefix, strictly increasing causal positions,
    ONLY the two closed native tools, the exact closed argument
    shapes verified by TYPED-STRICT identity (a bool or float
    standing in for a required integer is refused, never
    coerced), the digest bound to the canonical bytes of the
    TYPED EXPECTED shape, the serial binding of the issued exec
    calls to the issued-case prefix (in the closed case order),
    the stream polls placed strictly after the stream exec —
    bounded by the next case's exec when the stream case is
    complete, or, for the pending final stream case, fixed
    EXACTLY by the transactional FSM (it stages/commits the NEXT
    call with every accepted running result): zero retained
    results has zero issued polls, and at least one retained
    result has exactly as many issued polls as retained results
    (ONE outstanding poll, the final registry entry only) — and
    the per-result association: the first retained result of
    each case is its issued exec result, every retained stream
    result is the result of the corresponding issued empty-stdin
    poll in order, each with its ACTUAL numeric request position
    strictly after its own issuance and never after the NEXT
    issued call's position (the same POST may validate the prior
    result and issue the next call at that very position).  An
    issued poll without a retained result is legal ONLY as that
    single final outstanding entry of the pending final stream
    case.  Returns the ACTUAL issued poll count."""
    calls = record["issued_calls"]
    if not isinstance(calls, list) or len(calls) > FORMAT_MAX_ISSUED:
        raise FixtureError("format-issued-bound")
    entries: list[tuple[int, dict]] = []
    seen_call_ids: set[str] = set()
    last_position = -1
    for call in calls:
        if not isinstance(call, dict) or set(call) != {
            "family",
            "name",
            "call_id",
            "position",
            "arguments_sha256",
            "arguments",
        }:
            raise FixtureError("format-issued-fields")
        _enum_field(call, "family", TOOL_FAMILY_ISSUABLE)
        if not _opaque_id(call["name"]) or not _opaque_id(call["call_id"]):
            raise FixtureError("format-issued-fields")
        # the closed native tool identity: any name outside the
        # exact pair is refused BEFORE classification or case
        # indexing (an unknown name never enters the poll or exec
        # association)
        if call["name"] not in (FORMAT_EXEC_TOOL, FORMAT_POLL_TOOL):
            raise FixtureError("format-issued-name")
        # the registry issues each call ID at most once for the
        # whole run: a reused ID under another family/name or
        # with changed arguments is a closed conflict, never a
        # silent rebind
        if call["call_id"] in seen_call_ids:
            raise FixtureError("format-issued-duplicate")
        seen_call_ids.add(call["call_id"])
        position = _int_field(call, "position")
        if position <= last_position:
            raise FixtureError("format-issued-position")
        last_position = position
        entries.append((position, call))
    exec_entries = [
        (position, call) for position, call in entries if call["name"] == FORMAT_EXEC_TOOL
    ]
    poll_entries = [
        (position, call) for position, call in entries if call["name"] == FORMAT_POLL_TOOL
    ]
    if len(exec_entries) != len(cases):
        raise FixtureError("format-issued-exec")
    # the count equality was verified above: the i-th issued
    # exec pairs with the i-th case of the closed table prefix
    # (a strict zip against the FULL four-case table would raise
    # a builtin error on any valid shorter prefix)
    for (position, call), case, spec in zip(exec_entries, cases, FORMAT_CASES, strict=False):
        # the i-th issued exec is the i-th closed case's exact
        # TYPED argument shape (order binding: a swapped or
        # foreign case command is a refusal)
        expected_arguments = _format_exec_arguments(spec)
        if not format_arguments_exact(call["arguments"], expected_arguments):
            raise FixtureError("format-issued-arguments")
        if call["arguments_sha256"] != sha256_bytes(canonical_bytes(expected_arguments)):
            raise FixtureError("format-issued-digest")
        if (
            case["arguments_sha256"] != call["arguments_sha256"]
            or case["call_id"] != call["call_id"]
            or _int_field(case, "call_position") != position
        ):
            raise FixtureError("format-issued-binding")
    # the stream session was re-derived by the case law (None
    # when the stream case was never issued or its exec result
    # was never retained): no poll argument can be bound to
    # anything else
    if poll_entries and stream_session is None:
        raise FixtureError("format-issued-polls")
    for _position, call in poll_entries:
        expected_arguments = _format_poll_arguments(stream_session)
        if not format_arguments_exact(call["arguments"], expected_arguments):
            raise FixtureError("format-issued-arguments")
        if call["arguments_sha256"] != sha256_bytes(canonical_bytes(expected_arguments)):
            raise FixtureError("format-issued-digest")
    if len(cases) < 2:
        # no stream exec was issued: no poll target can exist
        if poll_entries:
            raise FixtureError("format-issued-polls")
    elif len(cases) >= 3:
        # the stream case is complete: its polls are strictly
        # between its exec and the next case's exec, exactly as
        # many as the complete case record carries
        stream_position = _int_field(cases[1], "call_position")
        next_position = _int_field(cases[2], "call_position")
        if len(poll_entries) != _int_field(cases[1], "polls"):
            raise FixtureError("format-issued-polls")
        for position, _call in poll_entries:
            if not stream_position < position < next_position:
                raise FixtureError("format-issued-polls")
    else:
        # the pending final stream case: its polls are strictly
        # after its exec, and the transactional FSM fixes the
        # issued count EXACTLY — it stages/commits the NEXT call
        # with every accepted running result: zero retained
        # results (the issued exec itself outstanding) has zero
        # polls, and at least one retained result has exactly as
        # many issued polls as retained results (ONE outstanding
        # poll, which must be the final registry entry).  An
        # orphaned retained result, a missing outstanding poll,
        # or an extra issued poll is a closed refusal
        stream_position = _int_field(cases[1], "call_position")
        retained_results = len(cases[1]["results"])
        if retained_results == 0:
            if poll_entries:
                raise FixtureError("format-issued-polls")
        else:
            if len(poll_entries) != retained_results:
                raise FixtureError("format-issued-polls")
            for position, _call in poll_entries:
                if position <= stream_position:
                    raise FixtureError("format-issued-polls")
            if entries[-1][1]["name"] != FORMAT_POLL_TOOL:
                raise FixtureError("format-issued-polls")
    # the per-result association over the retained frames (one
    # result per corresponding issue; a swapped, foreign,
    # duplicated or missing association is a closed refusal)
    exec_index = 0
    poll_index = 0
    for index, (position, call) in enumerate(entries):
        next_position = entries[index + 1][0] if index + 1 < len(entries) else None
        if call["name"] == FORMAT_EXEC_TOOL:
            case = cases[exec_index]
            exec_index += 1
            if not case["results"]:
                # the issued exec's result not yet retained: the
                # exec must be the final registry entry (a later
                # case's exec could only be issued after this
                # case's verified result)
                if next_position is not None:
                    raise FixtureError("format-result-association")
                continue
            result = case["results"][0]
        else:
            poll_index += 1
            stream_results = cases[1]["results"]
            if poll_index >= len(stream_results):
                # the outstanding poll: legal ONLY as the final
                # registry entry of the pending final stream
                # case
                if next_position is not None:
                    raise FixtureError("format-result-association")
                continue
            result = stream_results[poll_index]
        if (
            result["call_id"] != call["call_id"]
            or _int_field(result, "issued_position") != position
        ):
            raise FixtureError("format-result-association")
        result_position = _int_field(result, "result_position")
        if result_position <= position:
            raise FixtureError("format-result-causality")
        if next_position is not None and result_position > next_position:
            raise FixtureError("format-result-causality")
    return len(poll_entries)


def validate_format_snapshot_record_partial(record: dict) -> None:
    """The DISTINCT closed safe PARTIAL format-capture snapshot
    (017-ai, the canonical 017-aj entry's format scenario,
    non-complete state): the ordered issued-registry PREFIX
    (typed closed argument shapes), the issued-case prefix in
    closed table order — every entry before the last a COMPLETE
    verified case record, at most ONE pending case and it the
    LAST — carrying only its retained verified frames, the
    immutable pre-launch seed identity, the controller's own
    ledger totals, the ACTUAL issued poll count (the
    non-resettable issued counter; the per-case pending retained
    poll counts are explicitly separate), the ACTUAL non-done
    final state and the closed not-qualified fact.  The pending
    byte/session facts
    are re-derived from the retained frames; NO completion,
    exit, verified or truncation placeholder exists in the form
    (a placeholder can never be minted as an observed fact), so
    the record is safely exportable and retainable, can coexist
    with honest native-ready facts, and never mints a format
    qualification: unknown or unverified selection is not in the
    record at all.  The truthful count/coordinate law is closed:
    model_posts is the model-POST count (0 legal for the empty
    form) within the finite POST bound, the ledger request count
    is exactly model_posts plus the exporter's two closed
    charged commands, and every recorded numeric position stays
    strictly below model_posts.  The serialized record stays
    within the 256 KiB bound (the TOTAL selected-capture bound
    INCLUDING the outer identity metadata is enforced at the
    record consumer, producer and export seams, not here)."""
    _expect_tag(record, SCHEMA_FORMAT_SNAPSHOT_PARTIAL)
    _expect_field_set(record, _FORMAT_SNAPSHOT_PARTIAL_FIELDS)
    _bool_field(record, "synthetic", True)
    _enum_field(record, "qualification", (FORMAT_QUALIFICATION_NOT_QUALIFIED,))
    _format_seed_law()
    cases = record["cases"]
    if not isinstance(cases, list) or len(cases) > len(FORMAT_CASES):
        raise FixtureError("format-cases-count")
    # the closed issued-case prefix law: every entry before the
    # last is a COMPLETE case record (a completed case implies
    # its successor was issued in the same commit), at most ONE
    # pending case, and it the LAST entry
    last_position = -1
    # the re-derived stream session: measured from the complete
    # stream case record, or from the pending stream's retained
    # frames — a later pending non-stream case never overwrites
    # the measured session
    stream_session: int | None = None
    for index, (case, spec) in enumerate(zip(cases, FORMAT_CASES, strict=False)):
        if not isinstance(case, dict):
            raise FixtureError("format-cases-fields")
        if index == len(cases) - 1:
            if set(case) != _FORMAT_CASE_PENDING_FIELDS:
                raise FixtureError("format-cases-fields")
            if spec["kind"] == "stream":
                stream_session = _validate_format_case_pending(case, spec)[1]
            else:
                _validate_format_case_pending(case, spec)
        else:
            if set(case) != _FORMAT_CASE_FIELDS:
                raise FixtureError("format-cases-fields")
            _validate_format_case(case, spec)
            if spec["kind"] == "stream":
                stream_session = case["session_id"]
        if _int_field(case, "call_position") <= last_position:
            raise FixtureError("format-cases-position")
        last_position = _int_field(case, "call_position")
    # the honest final-state law: 0 issued cases is the empty
    # awaiting-first-post form; at least one issued case is
    # awaiting-result; "done" is the DISTINCT complete form
    if record["final_state"] != ("awaiting-first-post" if not cases else "awaiting-result"):
        raise FixtureError("format-final-state")
    # the truthful global polls law: the record's polls is the
    # ACTUAL issued poll count (the controller's non-resettable
    # issued counter, re-derived from the issued registry) — the
    # per-case pending retained poll counts are explicitly
    # separate and never relabel it
    issued_polls = _validate_format_issued_calls_partial(record, cases, stream_session)
    if _int_field(record, "polls") != issued_polls or issued_polls > FORMAT_MAX_POLLS:
        raise FixtureError("format-polls")
    seed = record["seed"]
    if (
        not isinstance(seed, list)
        or len(seed) != len(FORMAT_SEED_FILES)
        or any(
            not isinstance(entry, list)
            or len(entry) != 3
            or entry[0] != name
            or not _is_sha256(entry[1])
            or not isinstance(entry[2], int)
            or isinstance(entry[2], bool)
            or entry[2] != len(data)
            or entry[1] != sha256_bytes(data)
            for entry, (name, data) in zip(seed, FORMAT_SEED_FILES, strict=True)
        )
    ):
        raise FixtureError("format-seed")
    seed_total = _int_field(record, "seed_total_bytes")
    if seed_total != sum(entry[2] for entry in seed) or seed_total > FORMAT_SEED_MAX_TOTAL_BYTES:
        raise FixtureError("format-seed-bound")
    if _int_field(record, "originals_bytes") != seed_total:
        raise FixtureError("format-seed-state")
    if _sha256_field(record, "originals_sha256") != sha256_bytes(
        b"".join(data for _name, data in FORMAT_SEED_FILES)
    ):
        raise FixtureError("format-seed-digest")
    if _int_field(record, "exporter_uid") != CONTROLLER_UID:
        raise FixtureError("format-exporter-uid")
    _bool_field(record, "exported_before_teardown", True)
    ctl = record["controller_ledger"]
    if not isinstance(ctl, dict) or set(ctl) != {"requests", "output_bytes"}:
        raise FixtureError("format-ledger-fields")
    budgets = FixtureBudgets()
    # the truthful COUNT law: the ledger's request count is the
    # ACCOUNTED total — every model POST to the fixture (accepted
    # or refused) PLUS the exporter's closed ordered commands
    # (quiesce and export, each charged exactly once, both
    # required for exported_before_teardown).  model_posts is
    # carried as its OWN closed field; the empty partial form
    # may honestly carry zero model POSTs
    model_posts = _int_field(record, "model_posts")
    if (
        model_posts < 0
        or model_posts > min(FORMAT_MAX_POSTS, budgets.max_requests)
        or _int_field(ctl, "output_bytes") < 0
        or _int_field(ctl, "output_bytes") > budgets.output_cap_bytes
    ):
        raise FixtureError("format-ledger-bound")
    if _int_field(ctl, "requests") != model_posts + 2:
        raise FixtureError("format-ledger-count")
    # the truthful coordinate law: every recorded numeric
    # position is the 0-based index of an ACTUAL accounted model
    # POST, so it must stay strictly below the model POST count
    for call in record["issued_calls"]:
        if _int_field(call, "position") >= model_posts:
            raise FixtureError("format-coordinate-truth")
    for case in cases:
        if _int_field(case, "call_position") >= model_posts:
            raise FixtureError("format-coordinate-truth")
        for entry in case["results"]:
            if _int_field(entry, "result_position") >= model_posts:
                raise FixtureError("format-coordinate-truth")
    if len(canonical_bytes(record)) > FORMAT_SNAPSHOT_MAX_BYTES:
        raise FixtureError("format-serialized-bound")


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
    The fixed-21002 CODEX_HOME subject law stays byte-for-byte the
    original; the v2 tag and the v1 tag refuse each other.
    """
    _expect_tag(record, SCHEMA_PROFILE)
    _expect_field_set(record, _PROFILE_FIELDS)
    _validate_profile_record_core(record, SUBJECT_UID)


def _validate_profile_record_core(record: dict, subject_uid: int) -> None:
    """Shared closed structural core of the synthetic-profile
    record: identical facts and error law for the fixed-21002 v1
    record and the owner-UID v2 record; only the expected
    CODEX_HOME subject uid differs."""
    if _int_field(record, "codex_home_mode") != 0o700:
        raise FixtureError("closed record field state invalid: codex_home_mode")
    if _int_field(record, "codex_home_uid") != subject_uid:
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


def validate_profile_record_v2(record: dict, subject_uid: int) -> None:
    """Closed owner-UID synthetic-profile record (v2).

    The SAME closed synthetic CODEX_HOME + separate profile-file
    facts as the v1 record, measured under the frozen
    owner-profile subject (the CODEX_HOME owner must equal the
    verified owner expectation).  The v2 tag and the v1
    fixed-21002 tag refuse each other."""
    _check_v2_subject_id(subject_uid, "subject_uid")
    _expect_tag(record, SCHEMA_PROFILE_V2)
    _expect_field_set(record, _PROFILE_FIELDS)
    _validate_profile_record_core(record, subject_uid)


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
    SCHEMA_FORMAT_SNAPSHOT: validate_format_snapshot_record,
    SCHEMA_FORMAT_SNAPSHOT_PARTIAL: validate_format_snapshot_record_partial,
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

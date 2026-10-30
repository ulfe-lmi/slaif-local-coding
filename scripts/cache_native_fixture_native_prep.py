#!/usr/bin/env python3
"""Versioned native-handoff preparation/evidence contract (order 017-t, section 3).

The small READ-ONLY collection/validation surface for the LATER,
separately activated RIGHT-pane native handoff.  This round (T)
implements and tests the seams with fakes and tiny exact-owned
Python children only; it performs NO native execution, NO
worker stop, NO host signal of any kind and NO Docker
operation.  Native startup remains the later separately
activated manual foreground boundary, never a Python
subprocess launch.

Contract (closed, versioned ``slaif-native-handoff-prep-v1``):

- fixture-owner facts and external-native facts stay SEPARATE:
  the owner's retained evidence (its own closed record: exact
  CID, verified teardown, sentinel survival, publication, and
  its codex_invoked/worker_stopped/native_* flags — the
  closed safety facts of the WHOLE historical 017-s
  rehearsal run, a full-rehearsal-scope statement, NOT an
  owner-processes-only claim; the new native schema is
  separate, never an owner-only reinterpretation of those
  flags) is parsed into a typed OwnerFinalFacts under the
  historical S schema; the native subject is a distinct
  measured SubjectIdentity; the handoff verdict is composed
  from both, plus independently measured same-job
  restoration, AFTER the owner's own export/teardown finished
  (teardown-before-restore ordering; nothing keeps the
  container alive until restoration, nothing deadlocks finish
  on the stopped worker).  No record can therefore claim
  "Codex was never invoked" while a foreground native subject
  actually ran.
- a later native PASS depends on ACTUALLY collected facts
  bound to the same order/source/run/CID and the exact pinned
  binary and argv; unknown, unobserved or incomplete facts can
  never be ready/pass;
- a caller-authored ready/status/flag JSON is NOT
  measurement: the composer and the workflow accept only the
  typed records (or an explicit None), and anything else is a
  closed refusal;
- the native-owner record is PRODUCED by an explicit public
  producer (``produce_native_owner_record``) invoked on the
  real owned measurement adapter (``OwnedOwnerMeasurement``,
  over the completed R/S owner's finish/export/teardown
  state; the platform operations are faked in T and never
  invoked here): it validates the FULL measured export
  payload with the ACTUAL shared export validator (the same
  closed quiesce/snapshot/diagnostic/originals law the R/S
  finish path applies — a recomputed digest proves framing
  integrity only, never payload validity), recomputes the
  export digest from the measured payload bytes ITSELF (a
  supplied digest is never trusted), binds the
  measurement's exposed ``measured_context`` EXACTLY to the
  expected immutable order/run binding (a caller
  order/source/CID/image string is never an observed
  identity; the real owned adapter always exposes the
  context, and an incomplete or contradicting one is a
  closed refusal, never a silent skip to the caller
  strings), validates the closed teardown facts, and only
  then emits the closed versioned record — a parser or a
  preassembled caller map is NOT a producer, an unmeasured,
  invalid or contradictory fact is a closed refusal with no
  partial record, and the emitted record must round-trip
  the closed consumer validation;
- subject identity separates MEASURED facts (pid, uid/gid/
  groups, argv, tty, start_time, and the executable's sha when
  the registered-CID channel measures it through the kernel
  exe link) from BOUND context: the cid/run/binary
  expectations are the registered binding supplied from the
  verified owner record (attestation
  ``registered-owner-record``) or a plain expectation
  (``expectation-only``) — they are never stamped as
  observations of the process, and no expectation value is
  claimed as a measurement; a host UID/name-only process or a
  caller-supplied bare PID is never proof, and this round (T)
  is INERT: no container-membership proof is possible or
  claimed, a measured mismatch with the registered binary is a
  closed refusal, and an unmeasured binary is not native-ready;
  the channel's ACTUALLY bound CID must equal the
  expectation's registered CID before any read is recorded
  (a channel observing a different container can never
  establish same-context membership), and the current
  executable is re-verified through a fresh magic-link open
  AFTER the hash — an exec in the same process with an
  unchanged PID/birth is a closed refusal, never a stale
  verified identity;
- the public prepare/observe/finalize workflow invokes the
  collectors itself before recording measured state: a
  constructor or manually prepopulated record is not workflow
  evidence.  The workflow retains a bounded IMMUTABLE RECEIPT
  of the pre-teardown subject identity (the last identity
  measured while alive), records the worker stop as a
  SEPARATE measured event, and finalize composes the historical
  receipt with the separately verified post-teardown ABSENCE,
  the owner teardown and the same-job restoration — it never
  re-collects and replaces the receipt, never adopts a reused
  PID, and never infers a missing first observation;
- restoration is the RUNNING phase after a separately
  RECORDED stop of the same worker (pid, birth, group G,
  session, TTY): the tty foreground is read from the worker's
  own stat tpgid and cross-checked against the caller's
  observed foreground — a caller argument can never mint a
  foreground the process metadata does not show, a worker
  still observed stopped is the STOPPED phase (reported as
  such), and a single current snapshot without a recorded stop
  is never a restoration;
- malformed, mismatched, vanished, reused/incomparable or
  unreadable identities yield closed non-echoing
  refusals/unknowns — no host signal fallback, and no raw
  cmdline, environment, API/schema/body/TUI/history is ever
  logged or exported.
- the historical S evidence flags keep their ORIGINAL meaning:
  they are the closed safety facts of the 017-s rehearsal run
  as a whole (never invoked Codex, never stopped the worker,
  never started/was-ready native for that run), preserved
  unchanged and kept separate from the external-native facts;
  they are never relabeled as owner-launched-process flags and
  never re-asserted about the host or a later native run — a
  later native-owner record must carry its own explicit
  versioned producer/schema, and deriving the limited
  historical subset does not make contradictory S/native
  facts compatible.

Platform injection (a fake ProcTable) is for trusted fake
tests only; the module exposes no CLI entry that accepts
fabricated collector results, and the runtime default is the
bounded real /proc reader.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
import stat
import sys
import time
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cache_native_fixture_binding as binding  # noqa: E402
import cache_native_fixture_ci as ci  # noqa: E402
import cache_native_fixture_identity as fidentity  # noqa: E402
import cache_native_fixture_model as fmodel  # noqa: E402
import cache_native_fixture_runtime_profile as rprofile  # noqa: E402

FixtureError = ci.FixtureError
OrderRunBinding = binding.OrderRunBinding  # typed alias for the public seam

NATIVE_PREP_SCHEMA = "slaif-native-handoff-prep-v1"
# The DISTINCT identity-bearing prep-snapshot tag of the
# canonical FUTURE 017-ad native handoff (INERT in this
# round): the SAME closed W/B birth/group/session/TTY
# baseline and measured subject facts as the original tag,
# PLUS the frozen owner-identity substructure the real
# owner collected and derived — and the strict law that the
# subject of an AD-bound snapshot satisfies the frozen
# owner-UID identity (never the fixed 21002 law, and never
# a caller assertion).  The original tag keeps its exact
# historical fixed-21002 meaning byte-for-byte and refuses
# BOTH the identity key and any 017-ad binding (the tags are
# separate closed records, never a widened grammar —
# including for equal-numeric identities).
AD_NATIVE_PREP_SCHEMA = "slaif-017ad-native-handoff-prep-v1"
# The DISTINCT identity-bearing prep-snapshot tag of the
# canonical FUTURE 017-af native-PTY qualification entry
# (INERT in 017-ae: software only): the SAME closed W/B
# birth/group/session/TTY baseline and measured subject facts
# as the AD tag PLUS the frozen owner-identity substructure
# (the identical owner-UID identity law — the tags are
# separate closed records per entry, never a widened
# grammar).  The original tag keeps its exact historical
# fixed-21002 meaning byte-for-byte and refuses BOTH the
# identity key and any 017-ad / 017-af binding.
AF_NATIVE_PREP_SCHEMA = "slaif-017af-native-handoff-prep-v1"
# The DISTINCT identity-bearing prep snapshot tag of the
# canonical FUTURE 017-ah requalification entry (INERT in
# 017-ag): the SAME closed group/binding/subject facts plus
# the frozen owner-identity substructure under the AH
# entry's own tag-pair law (the AF tag remains AF-only, even
# for equal-numeric identities).
AH_NATIVE_PREP_SCHEMA = "slaif-017ah-native-handoff-prep-v1"
# The DISTINCT identity-bearing prep snapshot tag of the
# canonical FUTURE 017-aj native-process format
# qualification entry (INERT in 017-ai): the SAME closed
# group/binding/subject facts plus the frozen owner-identity
# substructure under the AJ entry's own tag-pair law (the AH
# tag remains AH-only, even for equal-numeric identities).
AJ_NATIVE_PREP_SCHEMA = "slaif-017aj-native-handoff-prep-v1"
OWNER_FACTS_SCHEMA = "slaif-native-handoff-owner-facts-v1"
# The owner's retained evidence schema (017-s record).  Its
# meaning is preserved unchanged: its safety flags describe the
# OWNER's own processes, never the host.
_S_EVIDENCE_SCHEMA = "slaif-017s-local-evidence-v1"
SUBJECT_ARGV: tuple[str, ...] = ("codex", "--yolo", "--profile", "early-beta")
SUBJECT_UID = ci.SUBJECT_UID  # 21002
SUBJECT_GID = ci.SUBJECT_UID  # 21002
# The closed group law measured in R/S: the subject's own
# primary gid (adds no privilege) or no groups.
SUBJECT_GROUP_VARIANTS: tuple[tuple[int, ...], ...] = ((), (SUBJECT_UID,))
NATIVE_SOURCE = "cid-registered"  # the ONLY accepted subject source
# The producer/scope binding of the historical evidence: this
# parser accepts ONLY the 017-s rehearsal record for its own
# order.  A later native-owner record must carry its own
# explicit versioned producer/schema and is refused here —
# deriving the limited historical subset never relabels or
# makes compatible contradictory S/native facts.
_S_ORDER_ID = "017-s"

_PROC_STAT_MAX = 8192
_CMDLINE_MAX = 4096
_STATUS_MAX = 8192
_COMM_MAX = 64
_PROC_LIST_MAX = 4096
_MEMBERSHIP_MAX = 256
_STATE_CHARS = frozenset("RSDZTtIXxKWPI")
_STAT_TAIL_FIELDS = 50
_RUNNING_STATES = frozenset(("R", "S", "D"))
_RUN_ID_RE = re.compile(r"^[0-9a-f]{32}$")
_CID_RE = re.compile(r"^[0-9a-f]{64}$")
_SHA_RE = re.compile(r"^[0-9a-f]{64}$")
_HEAD_RE = re.compile(r"^[0-9a-f]{40}$")
# the resolver's own active-read cap: the closed bound of a
# typed binding's raw active bytes at the AJ consumer seam
# (bounded handling BEFORE any hashing at to_record)
_ACTIVE_BYTES_MAX = binding._ACTIVE_READ_CAP
# The closed image-identity forms: the bare 64-hex digest or
# the ACTUAL measured Docker identity form used by R/S
# (``sha256:<digest>`` — the form the owner's own discovery
# measures).  The typed fact is always the NORMALIZED bare
# digest; the record retains the declared/measured form.
_IMAGE_ID_PREFIX = "sha256:"
_IMAGE_ID_RE = re.compile(r"^(?:sha256:)?[0-9a-f]{64}$")


def _normalize_image_id(image_id: str) -> str:
    if image_id.startswith(_IMAGE_ID_PREFIX):
        return image_id[len(_IMAGE_ID_PREFIX) :]
    return image_id


# -- closed failure-reason vocabulary ------------------------------------------
PREP_REASONS = frozenset(
    {
        "prep-binding-invalid",
        "prep-group-incomplete",
        "prep-proc-overbound",
        "prep-proc-unreadable",
        "prep-stat-malformed",
        "prep-cmdline-malformed",
        "prep-status-malformed",
        "prep-worker-invalid",
        "prep-worker-vanished",
        "prep-bash-invalid",
        "prep-bash-vanished",
        "prep-subject-invalid",
        "prep-subject-vanished",
        "prep-expectation-invalid",
        "prep-cid-invalid",
        "prep-uid-invalid",
        "prep-gid-invalid",
        "prep-groups-invalid",
        "prep-argv-invalid",
        "prep-binary-invalid",
        "prep-source-invalid",
        "prep-tty-invalid",
        "prep-start-unbound",
        "prep-record-malformed",
        "prep-owner-record-malformed",
        "prep-owner-run-mismatch",
        "prep-owner-order-mismatch",
        "prep-owner-head-mismatch",
        "prep-owner-schema-mismatch",
        "prep-owner-identity-mismatch",
        "prep-subject-run-mismatch",
        "prep-not-prepared",
        "prep-subject-registered",
        "prep-stop-not-recorded",
        "prep-verdict-input-invalid",
        "prep-stop-unobserved",
        "prep-exe-unreadable",
        "prep-exe-timeout",
        "prep-exe-changed",
        "prep-channel-no-enumeration",
        "prep-channel-cid-mismatch",
        "prep-export-overbound",
        "prep-export-invalid",
        "prep-native-owner-record-malformed",
        "prep-native-owner-context-mismatch",
        "prep-frozen-identity-invalid",
        "prep-frozen-identity-root",
        "prep-frozen-identity-range",
        "prep-frozen-identity-controller",
        "prep-frozen-identity-groups",
        "prep-channel-end-invalid",
        # the AF native attach-binding pure core (017-ae)
        "prep-devpts-record-malformed",
        "prep-devpts-output-overbound",
        "prep-devpts-uid-invalid",
        "prep-devpts-namespace-invalid",
        "prep-devpts-policy-invalid",
        "prep-devpts-not-isolated",
        "prep-devpts-rows-overbound",
        "prep-devpts-row-malformed",
        "prep-devpts-node-policy",
        "prep-devpts-device-invalid",
        "prep-devpts-namespace-mismatch",
        "prep-devpts-policy-mismatch",
        "prep-devpts-churn",
        "prep-devpts-allocation-none",
        "prep-devpts-allocation-ambiguous",
        "prep-devpts-inode-reuse",
        "prep-devpts-owner-mismatch",
        "prep-devpts-encoding-unrepresentable",
        "prep-devpts-allocation-malformed",
        "prep-devpts-cid-invalid",
        "prep-devpts-identity-invalid",
        "prep-devpts-allocation-mismatch",
        "prep-devpts-binding-invalid",
        "prep-attach-binding-malformed",
        "prep-attach-binding-mismatch",
        # the AJ selected native format-capture consumer (017-ai)
        "prep-format-capture-malformed",
        "prep-format-capture-mismatch",
        "prep-format-capture-bound",
    }
)

# The closed cid-provenance law: where the subject's cid/run
# binding came from.  ``registered-owner-record`` only when the
# expectation was built from a parsed, verified owner final
# facts record (expectation_from_owner); plain caller
# expectations stay ``expectation-only`` and can never claim a
# registered attestation.
_CID_ATTESTATIONS = ("expectation-only", "registered-owner-record")


def _is_pid(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and 0 < value < (1 << 31)


def _is_obs_group(value: object) -> bool:
    """The OBSERVATION-only pgrp/session domain of one
    well-formed /proc/<pid>/stat line: 0 is legal observation
    data (e.g. kernel threads report pgrp 0 / session 0) and
    the original finite upper bound is preserved.  This is NOT
    an identity or authority validator: every authority-
    bearing consumer (worker/Bash group and session facts,
    stop receipts, scoped subject frames, restoration
    verdicts) enforces strict positivity itself, and a zero
    observation can never become a signal target, handoff,
    receipt, registered subject or restored verdict."""
    return isinstance(value, int) and not isinstance(value, bool) and 0 <= value < (1 << 31)


def _is_strict_int(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value >= 0


# -- pure /proc parsers ----------------------------------------------------------


@dataclass(frozen=True)
class ProcStat:
    """The closed fixed fields parsed from one /proc/<pid>/stat
    line, INCLUDING the tty foreground group (tpgid, kernel
    field 8) — the process-metadata half of the restoration
    foreground cross-check.  Nothing else (in particular no raw
    argv or environment) is retained or exported."""

    pid: int
    comm: str
    state: str
    ppid: int
    pgrp: int
    session: int
    tty: int
    tpgid: int
    start_time: int


def parse_proc_stat(raw: str) -> ProcStat:
    """Parse one /proc/<pid>/stat line.  The comm field is
    parenthesized and may itself contain spaces and
    parentheses, so the OUTER parens are bound exactly (first
    ``(`` to last ``)``).  Every mismatch is a fixed closed
    refusal; nothing is echoed."""
    if not isinstance(raw, str) or not raw or len(raw) > _PROC_STAT_MAX:
        raise FixtureError("prep-stat-malformed")
    space = raw.find(" ")
    if space < 1:
        raise FixtureError("prep-stat-malformed")
    head, rest = raw[:space], raw[space + 1 :]
    if not head.isdigit():
        raise FixtureError("prep-stat-malformed")
    pid = int(head)
    if not _is_pid(pid):
        raise FixtureError("prep-stat-malformed")
    if not rest.startswith("("):
        raise FixtureError("prep-stat-malformed")
    close = rest.rfind(")")
    if close < 2:
        raise FixtureError("prep-stat-malformed")
    comm = rest[1:close]
    if not (1 <= len(comm) <= _COMM_MAX) or "\x00" in comm:
        raise FixtureError("prep-stat-malformed")
    fields = rest[close + 1 :].lstrip(" ").split(" ")
    # kernel fields after comm: 3 state, 4 ppid, 5 pgrp, 6
    # session, 7 tty_nr, 8 tpgid, ..., 22 start_time
    # the documented /proc/<pid>/stat carries exactly 50 fields
    # after comm (kernel fields 3..52); any other count is a
    # truncated or foreign line, not a measurement
    if len(fields) != _STAT_TAIL_FIELDS:
        raise FixtureError("prep-stat-malformed")
    state = fields[0]
    if len(state) != 1 or state not in _STATE_CHARS:
        raise FixtureError("prep-stat-malformed")
    try:
        ppid, pgrp, session, tty, tpgid = (int(fields[i]) for i in (1, 2, 3, 4, 5))
        start_time = int(fields[19])
    except ValueError:
        raise FixtureError("prep-stat-malformed") from None
    # ppid may be 0 (init); pgrp/session are real group ids —
    # but a well-formed line may report ZERO pgrp/session as
    # observation data (e.g. kernel threads): the parser is the
    # closed observation boundary only, and every authority-
    # bearing consumer enforces strict positivity itself (a
    # zero group/session is never a signal target, handoff,
    # stop receipt, subject frame or restoration authority).
    # Negative, overflow or truncated forms stay refused.
    # tpgid may legitimately be -1 for a process WITHOUT a
    # controlling terminal: the explicit unavailable-foreground
    # state is preserved as such — never a valid foreground,
    # never malformed metadata
    if (
        not _is_strict_int(ppid)
        or not _is_obs_group(pgrp)
        or not _is_obs_group(session)
        or not _is_strict_int(tty)
        or (tpgid != -1 and not _is_strict_int(tpgid))
        or not _is_strict_int(start_time)
    ):
        raise FixtureError("prep-stat-malformed")
    return ProcStat(pid, comm, state, ppid, pgrp, session, tty, tpgid, start_time)


def parse_proc_cmdline(raw: bytes) -> tuple[str, ...]:
    """Parse /proc/<pid>/cmdline (NUL-separated).  The exact
    argv is retained ONLY where this contract requires the
    exact pinned argv; every mismatch is a fixed closed
    refusal; an empty cmdline (zombie) is the closed empty
    tuple."""
    if not isinstance(raw, (bytes, bytearray)):
        raise FixtureError("prep-cmdline-malformed")
    raw = bytes(raw)
    if len(raw) > _CMDLINE_MAX:
        raise FixtureError("prep-cmdline-malformed")
    if not raw:
        return ()
    if not raw.endswith(b"\0"):
        raise FixtureError("prep-cmdline-malformed")
    parts = raw.split(b"\0")
    if parts and parts[-1] == b"":
        parts = parts[:-1]
    out: list[str] = []
    for part in parts:
        try:
            arg = part.decode("ascii")
        except UnicodeDecodeError:
            raise FixtureError("prep-cmdline-malformed") from None
        if not arg:
            raise FixtureError("prep-cmdline-malformed")
        out.append(arg)
    if not out:
        raise FixtureError("prep-cmdline-malformed")
    return tuple(out)


def parse_proc_status(raw: bytes) -> tuple[int, int, tuple[int, ...]]:
    """The closed Uid/Gid/Groups fields of one
    /proc/<pid>/status.  No other line is retained."""
    if not isinstance(raw, (bytes, bytearray)) or len(raw) > _STATUS_MAX:
        raise FixtureError("prep-status-malformed")
    uid: int | None = None
    gid: int | None = None
    groups: tuple[int, ...] | None = None
    try:
        for line in bytes(raw).decode("ascii").splitlines():
            if line.startswith("Uid:"):
                uid = int(line.split(":", 1)[1].split()[0])
            elif line.startswith("Gid:"):
                gid = int(line.split(":", 1)[1].split()[0])
            elif line.startswith("Groups:"):
                groups = tuple(int(x) for x in line.split(":", 1)[1].split())
    except (ValueError, IndexError):
        raise FixtureError("prep-status-malformed") from None
    if uid is None or gid is None or groups is None:
        raise FixtureError("prep-status-malformed")
    if not _is_strict_int(uid) or not _is_strict_int(gid):
        raise FixtureError("prep-status-malformed")
    if any(not _is_strict_int(g) for g in groups):
        raise FixtureError("prep-status-malformed")
    return uid, gid, groups


# -- the ProcTable seam ------------------------------------------------------------


class ProcTable(Protocol):
    """The READ-ONLY process-table seam.  The runtime default is
    the bounded real /proc reader; trusted fake tests inject a
    scripted table.  No method may mutate the host, signal a
    process or launch anything."""

    def stat(self, pid: int) -> bytes | None:
        """The /proc/<pid>/stat bytes, or None when absent."""

    def cmdline(self, pid: int) -> bytes | None:
        """The /proc/<pid>/cmdline bytes, or None when absent."""

    def status(self, pid: int) -> bytes | None:
        """The /proc/<pid>/status bytes, or None when absent."""

    def list_pids(self) -> list[int]:
        """The bounded pid listing (capped enumeration)."""


class RealProcTable:
    """The bounded READ-ONLY /proc collector: lstat-checked
    regular non-symlink files with hard caps (an over-bound
    entry is a closed refusal, never silently truncated),
    capped enumeration, no follow, no write, no signal."""

    def __init__(self, root: Path = Path("/proc")) -> None:
        self._root = root

    def _read(self, name: str, pid: int, cap: int) -> bytes | None:
        path = self._root / str(pid) / name
        try:
            st = os.lstat(path)
        except OSError:
            return None
        if not stat.S_ISREG(st.st_mode):
            return None
        if st.st_size > cap:
            raise FixtureError("prep-proc-overbound")
        try:
            fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
        except OSError:
            return None
        try:
            data = os.read(fd, cap + 1)
        except OSError:
            raise FixtureError("prep-proc-unreadable") from None
        finally:
            try:
                os.close(fd)
            except OSError:
                pass
        if len(data) > cap:
            raise FixtureError("prep-proc-overbound")
        return data

    def stat(self, pid: int) -> bytes | None:
        if not _is_pid(pid):
            raise FixtureError("prep-worker-invalid")
        return self._read("stat", pid, _PROC_STAT_MAX)

    def cmdline(self, pid: int) -> bytes | None:
        if not _is_pid(pid):
            raise FixtureError("prep-subject-invalid")
        return self._read("cmdline", pid, _CMDLINE_MAX)

    def status(self, pid: int) -> bytes | None:
        if not _is_pid(pid):
            raise FixtureError("prep-subject-invalid")
        return self._read("status", pid, _STATUS_MAX)

    def list_pids(self) -> list[int]:
        """Bounded LAZY enumeration: the directory is walked
        entry by entry (no full listing materialized first) and
        the refusal fires at the cap+1 numeric entry, so an
        over-bound root cannot pin memory or hide the refusal
        behind an unbounded allocation."""
        pids: list[int] = []
        try:
            it = os.scandir(self._root)
        except OSError:
            raise FixtureError("prep-proc-unreadable") from None
        try:
            for entry in it:
                name = entry.name
                if len(name) > 10 or not name.isdigit():
                    continue
                pids.append(int(name))
                if len(pids) > _PROC_LIST_MAX:
                    raise FixtureError("prep-proc-overbound")
        finally:
            it.close()
        return pids

    def pid_present(self, pid: int) -> bool | None:
        """The verified-absence primitive: True when the pid
        entry itself is gone (lstat ENOENT), False when the
        entry exists, None when its state is unreadable — an
        unreadable entry is an unknown, never a verified
        absence."""
        if not _is_pid(pid):
            raise FixtureError("prep-subject-invalid")
        try:
            os.lstat(self._root / str(pid))
        except FileNotFoundError:
            return True
        except OSError:
            return None
        # the entry exists: PRESENT (False).  Only a proven
        # missing entry is a verified absence (True); present
        # and missing can never both be True
        return False


# -- worker / Bash group facts -----------------------------------------------------


@dataclass(frozen=True)
class GroupMember:
    pid: int
    state: str
    tty: int


_TOOL_PROVENANCE = ("worker-descendant", "owned", "unknown")


@dataclass(frozen=True)
class ToolSessionMember:
    """A separately grouped tool-session member with its CLOSED
    provenance: ``worker-descendant`` (bounded ppid walk
    actually reaches the worker) or ``owned`` (a SEPARATELY
    REGISTERED exact pid+birth entry for this member); same
    uid alone is NOT provenance — a member with neither
    measured ancestry nor registered exact identity is
    ``unknown`` (retained as unknown, never adopted as
    owned)."""

    pid: int
    state: str
    tty: int
    provenance: str


def _is_worker_descendant(
    table: ProcTable, pid: int, worker_pid: int, max_depth: int = 16, max_hops: int = 256
) -> bool:
    """Bounded, cycle-safe ppid walk: True only when the
    member's ancestor chain actually reaches the worker.  Any
    vanished/malformed ancestor, cycle or depth exhaustion is
    the honest False (the caller keeps the member UNKNOWN,
    never assumes descent)."""
    seen = {pid}
    current = pid
    hops = 0
    for _ in range(max_depth):
        raw = table.stat(current)
        if raw is None:
            return False
        try:
            ancestor = parse_proc_stat(raw.decode("ascii", "replace"))
        except FixtureError:
            return False
        if ancestor.ppid == worker_pid:
            return True
        if not _is_pid(ancestor.ppid) or ancestor.ppid in seen:
            return False
        seen.add(ancestor.ppid)
        current = ancestor.ppid
        hops += 1
        if hops > max_hops:
            return False
    return False


@dataclass(frozen=True)
class WorkerGroupFacts:
    """The READ-ONLY handoff group facts: worker W, its parent
    Bash B (verified: bash executable, W's parent, same
    session and TTY, birth recorded), pgrp G, session/TTY/
    foreground relation, complete bounded G membership, and the
    separately grouped tool-session inventory with each
    member's CLOSED provenance — measured worker-descendant,
    registered exact pid+birth owned, or unknown: same-
    session members are always retained (unknowns as unknown,
    never adopted), worker descendants in NEW sessions
    (setsid) are inventoried independently of SID, unknown
    unrelated processes elsewhere are neither adopted nor
    recorded; not a mere count of arbitrary groups.  The
    actual Bash job J is
    NEVER guessed (no field for it); the tty foreground pgrp is
    a read-only observation supplied by the later authorized
    collector (None = unobserved, never assumed)."""

    worker_pid: int
    worker_state: str
    worker_pgrp: int
    worker_session: int
    worker_tty: int
    worker_start_time: int
    bash_pid: int
    bash_state: str
    bash_pgrp: int
    bash_session: int
    bash_tty: int
    bash_start_time: int
    same_job: bool
    same_tty: bool
    foreground_pgrp: int | None
    members: tuple[GroupMember, ...]
    session_other_groups: tuple[tuple[int, int], ...]
    tool_sessions: tuple[tuple[int, tuple[ToolSessionMember, ...]], ...]


def collect_worker_group(
    table: ProcTable,
    worker_pid: object,
    bash_pid: object | None = None,
    foreground_pgrp: int | None = None,
    *,
    registered_owners: Mapping[int, int] | None = None,
) -> WorkerGroupFacts:
    """Collect the group facts READ-ONLY (no signal of any
    kind).  Vanished processes and W/B relation violations are
    closed refusals: B must be a verified bash with W as its
    direct child in the same session on the same TTY, with
    birth recorded for both.  The bounded listing is tri-
    stated row by row: only an independently VERIFIED-gone
    entry may be ignored (bounded churn law); an unreadable
    still-existing or unprovable entry cannot be classified
    as a non-member, so the inventory is a closed
    ``prep-group-incomplete`` refusal, never a silently
    skipped row.  Tool-session provenance comes only from
    MEASURED worker ancestry or a separately registered exact
    pid+birth mapping (``registered_owners``); membership and
    tool-session enumeration are bounded."""
    if not _is_pid(worker_pid):
        raise FixtureError("prep-worker-invalid")
    if foreground_pgrp is not None and not _is_pid(foreground_pgrp):
        raise FixtureError("prep-worker-invalid")
    if registered_owners is not None:
        if (
            not isinstance(registered_owners, Mapping)
            or len(registered_owners) > _MEMBERSHIP_MAX
            or any(
                not _is_pid(pid) or not _is_strict_int(birth)
                for pid, birth in registered_owners.items()
            )
        ):
            raise FixtureError("prep-worker-invalid")
    w_raw = table.stat(worker_pid)
    if w_raw is None:
        raise FixtureError("prep-worker-vanished")
    w = parse_proc_stat(w_raw.decode("ascii", "replace"))
    # the handoff group facts carry AUTHORITY: the worker's
    # group and session are strictly positive finite identity
    # (a well-formed ZERO pgrp/session observation — e.g. a
    # kernel-thread-like row — is never a handoff group)
    if not _is_pid(w.pgrp) or not _is_pid(w.session):
        raise FixtureError("prep-worker-invalid")
    bp = w.ppid if bash_pid is None else bash_pid
    if not _is_pid(bp):
        raise FixtureError("prep-bash-invalid")
    b_raw = table.stat(bp)
    if b_raw is None:
        raise FixtureError("prep-bash-vanished")
    b = parse_proc_stat(b_raw.decode("ascii", "replace"))
    if not _is_pid(b.pgrp) or not _is_pid(b.session):
        raise FixtureError("prep-bash-invalid")
    if bash_pid is not None and b.pid != bp:
        raise FixtureError("prep-bash-invalid")
    # W/B relation checks: parent, session, TTY
    if w.ppid != b.pid:
        raise FixtureError("prep-worker-invalid")
    if w.session != b.session:
        raise FixtureError("prep-worker-invalid")
    if not (w.tty != 0 and w.tty == b.tty):
        raise FixtureError("prep-worker-invalid")
    # B must actually be a bash (comm or argv[0] basename)
    b_cmd_raw = table.cmdline(bp)
    if b_cmd_raw is None:
        raise FixtureError("prep-bash-invalid")
    b_argv = parse_proc_cmdline(b_cmd_raw)
    b_exec = b_argv[0].rsplit("/", 1)[-1] if b_argv else ""
    if b.comm != "bash" and b_exec != "bash":
        raise FixtureError("prep-bash-invalid")
    group = w.pgrp
    members: list[GroupMember] = []
    other: dict[int, int] = {}
    tool: dict[int, list[ToolSessionMember]] = {}
    tool_members = 0
    for pid in table.list_pids():
        raw = table.stat(pid)
        if raw is None:
            # A None stat does NOT prove the entry is gone:
            # tri-state it through the bounded absence seam.
            # Only an independently VERIFIED-gone entry may
            # be ignored (bounded churn law); an unreadable
            # still-existing or unprovable entry cannot
            # establish nonmembership, so the inventory
            # cannot claim completeness — a closed non-
            # echoing refusal, never a silently skipped row.
            if _verified_absence(table, pid) is not True:
                raise FixtureError("prep-group-incomplete")
            continue
        entry = parse_proc_stat(raw.decode("ascii", "replace"))
        if entry.pgrp == group:
            members.append(GroupMember(entry.pid, entry.state, entry.tty))
            if len(members) > _MEMBERSHIP_MAX:
                raise FixtureError("prep-proc-overbound")
            continue
        if entry.session == b.session:
            other[entry.pgrp] = other.get(entry.pgrp, 0) + 1
            if len(other) > _MEMBERSHIP_MAX:
                raise FixtureError("prep-proc-overbound")
        # separately grouped tool sessions with CLOSED
        # provenance: MEASURED worker ancestry (bounded ppid
        # walk) or a separately REGISTERED exact pid+birth
        # entry; same uid alone is NOT provenance.  Same-
        # session members are always retained (unknowns as
        # unknown, never adopted as owned); a worker
        # descendant in a NEW session (setsid) is inventoried
        # independently of SID; unknown unrelated processes in
        # other sessions are neither adopted nor recorded
        provenance = "unknown"
        if entry.pid != w.pid and _is_worker_descendant(table, entry.pid, w.pid):
            provenance = "worker-descendant"
        elif (
            registered_owners is not None
            and entry.pid in registered_owners
            and registered_owners[entry.pid] == entry.start_time
        ):
            provenance = "owned"
        if provenance != "unknown" or entry.session == b.session:
            bucket = tool.setdefault(entry.pgrp, [])
            bucket.append(ToolSessionMember(entry.pid, entry.state, entry.tty, provenance))
            tool_members += 1
            if tool_members > _MEMBERSHIP_MAX:
                raise FixtureError("prep-proc-overbound")
    members.sort(key=lambda m: m.pid)
    return WorkerGroupFacts(
        worker_pid=w.pid,
        worker_state=w.state,
        worker_pgrp=w.pgrp,
        worker_session=w.session,
        worker_tty=w.tty,
        worker_start_time=w.start_time,
        bash_pid=b.pid,
        bash_state=b.state,
        bash_pgrp=b.pgrp,
        bash_session=b.session,
        bash_tty=b.tty,
        bash_start_time=b.start_time,
        same_job=(w.pgrp == b.pgrp),
        same_tty=(w.tty != 0 and w.tty == b.tty),
        foreground_pgrp=foreground_pgrp,
        members=tuple(members),
        session_other_groups=tuple(sorted(other.items())),
        tool_sessions=tuple(
            (g, tuple(sorted(ms, key=lambda m: m.pid))) for g, ms in sorted(tool.items())
        ),
    )


# -- subject identity -------------------------------------------------------------


@dataclass(frozen=True)
class SubjectExpectation:
    """What the LATER native subject MUST be, from the exact
    registered run binding — never from the subject process
    itself: the registered CID, the pinned binary identity, the
    run id, the birth bound (clock ticks measured at run
    admission; None = unobserved, and an unobserved bound NEVER
    becomes a claimed bound), and the expected PTY (None =
    unobserved).  ``attestation`` records WHERE this binding
    came from (closed set): ``registered-owner-record`` when
    built via expectation_from_owner from a parsed verified
    owner record, ``expectation-only`` for a plain caller
    expectation."""

    cid: str
    binary_sha256: str
    run_id: str
    min_start_time: int | None = None
    expected_tty: int | None = None
    attestation: str = "expectation-only"


@dataclass(frozen=True)
class SubjectIdentity:
    """The native subject identity.  MEASURED facts (from the
    read-only table and, when a bridge is supplied, the
    executable): pid, uid/gid/groups, argv (+ digest), tty,
    start_time — and ``binary_sha256`` only when the exe
    bridge actually measured it (None = unmeasured, with
    ``binary_verified`` false; a measured mismatch with the
    registered expectation is a closed refusal, never a
    fallback to the expectation value).  BOUND context (the
    registered binding, with its provenance): ``cid``/``run_id``
    under ``cid_attestation``, the registered ``binary_sha256``
    expectation, the exact pinned argv, the closed uid/gid/
    group law and the birth bound.  No bound value is stamped
    as an observation."""

    source: str
    cid: str
    pid: int
    uid: int
    gid: int
    groups: tuple[int, ...]
    argv: tuple[str, ...]
    argv_sha256: str
    binary_sha256: str | None
    binary_verified: bool
    cid_attestation: str
    cid_membership: str
    tty: int
    start_time: int
    start_bound: bool
    run_id: str
    # the expected-PTY provenance: True ONLY when the
    # expectation's PTY was actually bound (a strict
    # NONZERO int) and the measured tty equals it — an
    # unobserved expected PTY (None) or a measured tty0
    # subject is False, never ready-by-default
    pty_matched: bool


def _validate_expectation(expectation: object) -> SubjectExpectation:
    if not isinstance(expectation, SubjectExpectation):
        raise FixtureError("prep-expectation-invalid")
    if (
        not isinstance(expectation.cid, str)
        or _CID_RE.fullmatch(expectation.cid) is None
        or not isinstance(expectation.binary_sha256, str)
        or _SHA_RE.fullmatch(expectation.binary_sha256) is None
        or not isinstance(expectation.run_id, str)
        or _RUN_ID_RE.fullmatch(expectation.run_id) is None
        or (
            expectation.min_start_time is not None
            and not _is_strict_int(expectation.min_start_time)
        )
        or (expectation.expected_tty is not None and not _is_strict_int(expectation.expected_tty))
        or expectation.attestation not in _CID_ATTESTATIONS
    ):
        raise FixtureError("prep-expectation-invalid")
    return expectation


def argv_digest(argv: Sequence[str]) -> str:
    return hashlib.sha256(b"\0".join(a.encode("ascii") for a in argv) + b"\0").hexdigest()


def _check_identity_fields(
    uid: object,
    gid: object,
    groups: object,
    argv: object,
    tty: int,
    subject_identity: tuple[int, int, tuple[int, ...]] | None = None,
) -> None:
    """The closed identity law, shared by the collector and the
    retained-record validator: every mismatch is a fixed closed
    refusal; nothing is echoed."""
    if subject_identity is None:
        # the ORIGINAL fixed-21002 law, byte-for-byte the
        # historical one (no frozen identity supplied)
        exp_uid = SUBJECT_UID
        exp_gid = SUBJECT_GID
        exp_group_variants = SUBJECT_GROUP_VARIANTS
    else:
        # the FROZEN owner-UID subject identity (the future
        # 017-ad native handoff): the measured subject must be
        # EXACTLY this closed triple — the fixed native argv and
        # tty laws are unchanged; the triple itself was already
        # closed-validated at workflow construction (this is
        # data, never a per-read re-derivation)
        exp_uid, exp_gid, frozen_groups = subject_identity
        exp_group_variants = ((), frozen_groups)
    if not _is_strict_int(uid) or uid != exp_uid:
        raise FixtureError("prep-uid-invalid")
    if not _is_strict_int(gid) or gid != exp_gid:
        raise FixtureError("prep-gid-invalid")
    if (
        not isinstance(groups, (list, tuple))
        or any(not _is_strict_int(g) for g in groups)
        or tuple(groups) not in exp_group_variants
    ):
        raise FixtureError("prep-groups-invalid")
    if not isinstance(argv, (list, tuple)) or tuple(argv) != SUBJECT_ARGV:
        raise FixtureError("prep-argv-invalid")
    if not _is_strict_int(tty):
        raise FixtureError("prep-tty-invalid")


def _validate_frozen_subject_identity(identity: object) -> tuple[int, int, tuple[int, ...]]:
    """The closed law of the FROZEN owner-UID subject identity a
    017-ad native workflow may apply in place of the original
    fixed 21002: strict finite non-root Linux IDs (the Z
    eligible-ID law — 1..4294967294, never 0, distinct from the
    controller identity 21001) and groups EXACTLY the
    one-element primary-GID vector (never host supplementary
    groups, never an empty vector).  The frozen triple is DATA
    (collected and derived by the real owner's own bounded OS
    identity collection — never caller authority); this check
    is data validation, not measured authority.  The original
    workflow (no frozen identity) keeps the fixed-21002 law
    byte-for-byte."""
    if not isinstance(identity, tuple) or len(identity) != 3:
        raise FixtureError("prep-frozen-identity-invalid")
    uid, gid, groups = identity
    for value in (uid, gid):
        if not _is_strict_int(value):
            raise FixtureError("prep-frozen-identity-invalid")
        if value == 0:
            raise FixtureError("prep-frozen-identity-root")
        if value < 1 or value > 4294967294:
            raise FixtureError("prep-frozen-identity-range")
        if value == fidentity.CONTROLLER_UID or value == fidentity.CONTROLLER_GID:
            raise FixtureError("prep-frozen-identity-controller")
    if (
        not isinstance(groups, tuple)
        or len(groups) != 1
        or not _is_strict_int(groups[0])
        or groups[0] != gid
    ):
        raise FixtureError("prep-frozen-identity-groups")
    return (uid, gid, groups)


_CGROUP_MAX = 8192
_CGROUP_SCOPE_MAX = 256


def _cgroup_docker_scope(line: str, cid: str) -> str | None:
    """The CLOSED docker-scope grammar of one cgroup line:
    the exact registered 64-hex CID as the final scope token
    (cgroup-v2 systemd scope ``docker-<cid>.scope``) or as the
    final path component under ``/docker/`` (v1 form).  Any
    other host is not the registered container and yields
    None — never a fuzzy match."""
    if line.count(":") < 2:
        return None
    path = line.rsplit(":", 1)[1]
    if not path.startswith("/"):
        return None
    scope = path.rsplit("/", 1)[-1]
    if scope == f"docker-{cid}.scope":
        return f"docker-{cid}.scope"
    if path == f"/docker/{cid}" or path.endswith(f"/docker/{cid}"):
        return f"docker/{cid}"
    return None


@dataclass(frozen=True)
class DevptsSlaveMetadata:
    """The CLOSED per-subject devpts slave metadata fact
    (017-ae software), measured READ-ONLY through the
    subject's OWN mount view — Linux documents
    ``/proc/<pid>/root`` as the process's filesystem and
    mount view, so ``/proc/<pid>/root/dev/pts`` is the
    subject's devpts mount root and the selected slave node
    beneath it.  The (pid, birth) identity is bound before
    AND after the reads and the registered-CID scope gates
    the read: no ptrace/prctl, no privilege change, no new
    transport, no host ``/dev/pts`` enumeration.  Access
    denial or any unbound frame is a typed unknown (the
    channel returns None), never an assumption."""

    root_dev: int  # st_dev of the subject's devpts mount root (the namespace)
    root_ino: int  # st_ino of the subject's devpts mount root (the namespace)
    slave_dev: int  # st_dev of the selected slave node (MUST be the
    # measured devpts root's filesystem — a node from another
    # filesystem can carry equal inodes/modes/owners)
    slave_ino: int  # st_ino of the selected slave node
    slave_mode: int  # the FULL measured st_mode of the selected
    # slave node (file-type bits included — the real seam keeps
    # its S_ISCHR check; the closed consumer normalizes the
    # permission bits before comparing them to the allocation)
    slave_uid: int  # owner UID of the selected slave node
    slave_gid: int  # owner GID of the selected slave node
    major: int  # the slave device major (from st_rdev)
    minor: int  # the slave device minor (from st_rdev)


class CidScopedTable(Protocol):
    """The narrow READ-ONLY collection channel bound to the
    registered CID and immutable image.  EVERY subject read is
    scoped: a process not observed in the registered
    container's cgroup scope (or with an unreadable scope) does
    not exist on this channel — a host process table plus a
    matching expected CID/run string is NOT this channel, and a
    process in another container with matching UID/argv/binary
    can never appear here.  The executable is measured through
    the kernel's /proc/<pid>/exe magic link (resolved by the
    kernel in the process's own context — never by re-opening
    the target string as a host path), with descriptor
    identity, birth binding before AND after, bounds on total
    bytes and time while reading, and a POST-HASH re-open of
    the magic link whose file identity must still match the
    hashed descriptor (an exec in the same process with an
    unchanged PID/birth is a closed refusal).  The runtime
    default is the bounded real reader; trusted fake tests
    inject a scripted channel."""

    @property
    def cid(self) -> str:
        """The exact 64-hex CID this channel is bound to —
        the identity EVERY scoped read and the measured
        executable are checked against before recording: a
        channel bound to a different CID than the subject
        expectation can never record a ``cid-scoped``
        identity, no matter what its process metadata says."""

    def cgroup_scope(self, pid: int) -> str | None:
        """The registered-container scope observed in the host
        cgroup view of ``pid``, or None when absent/unreadable
        — a read-only observation, never assumed."""

    def stat(self, pid: int) -> bytes | None:
        """The scoped /proc/<pid>/stat bytes, or None when the
        process is absent from the registered container."""

    def cmdline(self, pid: int) -> bytes | None:
        """The scoped /proc/<pid>/cmdline bytes, or None."""

    def status(self, pid: int) -> bytes | None:
        """The scoped /proc/<pid>/status bytes, or None."""

    def exe_sha256(self, pid: int, birth: int) -> str | None:
        """The sha256 of the ACTUAL running executable of the
        (pid, birth) process, measured through the kernel exe
        link with birth binding and byte/time bounds; None when
        absent/unmeasurable, closed refusal when over-bound,
        timed out, or the identity is not bound."""

    def devpts_slave_metadata(self, pid: int, birth: int, name: int) -> DevptsSlaveMetadata | None:
        """The narrow READ-ONLY per-subject devpts slave
        metadata (017-ae software): the fixed node facts of
        ``/proc/<pid>/root/dev/pts`` and its selected slave
        ``<name>`` in the subject's OWN mount view, with the
        registered-CID scope gate and (pid, birth) identity
        binding before AND after — the closed frames that
        make a per-subject tty namespace claim.  None when the
        subject is out of scope, the identity is not bound,
        or the path is denied/unreadable (a typed unknown,
        never assumed); an invalid argument is a closed
        refusal."""


class RealCidScopedTable:
    """The bounded READ-ONLY real channel: cgroup-scope reads
    (closed docker grammar) gate every proc read; the exe hash
    opens the magic link itself, re-checks the process birth
    before and after, fstat-verifies descriptor identity, and
    bounds TOTAL bytes and time — a growing file or an
    exec-reused PID is a closed refusal, never a silent mix."""

    def __init__(
        self,
        cid: str,
        root: Path = Path("/proc"),
        max_exe_bytes: int = 1 << 30,
        exe_deadline: float = 60.0,
        exe_end: float | None = None,
        metadata_deadline: float = 5.0,
    ) -> None:
        if not isinstance(cid, str) or _CID_RE.fullmatch(cid) is None:
            raise FixtureError("prep-cid-invalid")
        if exe_end is not None and (
            not isinstance(exe_end, (int, float))
            or isinstance(exe_end, bool)
            or not math.isfinite(exe_end)
        ):
            raise FixtureError("prep-channel-end-invalid")
        if (
            not isinstance(metadata_deadline, (int, float))
            or isinstance(metadata_deadline, bool)
            or not math.isfinite(metadata_deadline)
            or metadata_deadline <= 0
        ):
            raise FixtureError("prep-channel-end-invalid")
        self._cid = cid
        self._root = root
        self._max_exe_bytes = max_exe_bytes
        self._exe_deadline = exe_deadline
        # the ABSOLUTE owner-END clamp (017-ad): when bound, the
        # effective deadline of EVERY actual exe read/return is
        # further clamped to this SAME absolute anchor — a
        # channel reused later can never refresh the window
        # (a relative captured duration is a per-measurement
        # cap only, never an extended budget)
        self._exe_end = None if exe_end is None else float(exe_end)
        # the AF per-subject metadata-operation bound (017-ae
        # software): a FINITE operation cap for the devpts
        # slave metadata seam ONLY (the original executable
        # bounds stay byte-for-byte unchanged), further
        # clamped to the SAME absolute owner END anchor this
        # channel carries — no cleanup grace, no fresh window,
        # no deadline reset
        self._metadata_deadline = float(metadata_deadline)

    @property
    def cid(self) -> str:
        return self._cid

    def _read_file(self, pid: int, name: str, cap: int) -> bytes | None:
        path = self._root / str(pid) / name
        try:
            st = os.lstat(path)
        except OSError:
            return None
        if not stat.S_ISREG(st.st_mode) or st.st_size > cap:
            return None
        try:
            fd = os.open(path, os.O_RDONLY | os.O_NONBLOCK | os.O_NOFOLLOW)
        except OSError:
            return None
        data = b""
        try:
            while len(data) <= cap:
                chunk = os.read(fd, min(65536, cap + 1 - len(data)))
                if not chunk:
                    break
                data += chunk
        except OSError:
            return None
        finally:
            try:
                os.close(fd)
            except OSError:
                pass
        if len(data) > cap:
            return None
        return data

    def cgroup_scope(self, pid: int) -> str | None:
        if not _is_pid(pid):
            raise FixtureError("prep-subject-invalid")
        raw = self._read_file(pid, "cgroup", _CGROUP_MAX)
        if raw is None:
            return None
        seen = 0
        for line in raw.decode("ascii", "replace").splitlines():
            seen += 1
            if seen > _CGROUP_SCOPE_MAX:
                return None  # over-bound cgroup view: unreadable
            scope = _cgroup_docker_scope(line, self._cid)
            if scope is not None:
                return scope
        return None

    def _scoped(self, pid: int, name: str, cap: int) -> bytes | None:
        if not _is_pid(pid):
            raise FixtureError("prep-subject-invalid")
        if self.cgroup_scope(pid) is None:
            return None
        return self._read_file(pid, name, cap)

    def stat(self, pid: int) -> bytes | None:
        return self._scoped(pid, "stat", _PROC_STAT_MAX)

    def cmdline(self, pid: int) -> bytes | None:
        return self._scoped(pid, "cmdline", _CMDLINE_MAX)

    def status(self, pid: int) -> bytes | None:
        return self._scoped(pid, "status", _STATUS_MAX)

    def list_pids(self) -> list[int]:
        # the channel NEVER enumerates the host: membership is
        # per-pid scope verification, not a host listing
        raise FixtureError("prep-channel-no-enumeration")

    def pid_present(self, pid: int) -> bool | None:
        """The scoped verified-absence primitive: True when
        the pid entry itself is gone; False when the entry
        exists AND the registered CID's scope is still
        readable (a process is still observed in the
        registered container); None when the entry exists
        but the scope is unreadable or no longer the
        registered container — an unprovable entry is an
        unknown, never a verified absence."""
        if not _is_pid(pid):
            raise FixtureError("prep-subject-invalid")
        try:
            os.lstat(self._root / str(pid))
        except FileNotFoundError:
            return True
        except OSError:
            return None
        if self.cgroup_scope(pid) is None:
            # the entry exists but the scope is unreadable:
            # unknown, never a verified absence
            return None
        # the entry exists and the registered container is
        # still observed at this pid: PRESENT (False)
        return False

    def _birth(self, pid: int) -> int | None:
        raw = self._read_file(pid, "stat", _PROC_STAT_MAX)
        if raw is None:
            return None
        try:
            ps = parse_proc_stat(raw.decode("ascii", "replace"))
        except FixtureError:
            return None
        # LIFETIME AUTHORITY: the parser now accepts a well-formed
        # ZERO pgrp/session row as observation data, but a
        # lifetime fact can never be minted from such a row —
        # the old parser's positive prerequisite is preserved at
        # this consumer boundary (unknown, never a birth)
        if not _is_pid(ps.pgrp) or not _is_pid(ps.session):
            return None
        return ps.start_time

    def exe_sha256(self, pid: int, birth: int) -> str | None:
        if not _is_pid(pid) or not _is_strict_int(birth):
            raise FixtureError("prep-subject-invalid")
        if self.cgroup_scope(pid) is None:
            return None
        # identity binding BEFORE the measurement: the (pid,
        # birth) pair must be the live process now
        if self._birth(pid) != birth:
            raise FixtureError("prep-subject-invalid")
        exe = self._root / str(pid) / "exe"
        try:
            fd = os.open(exe, os.O_RDONLY)
        except OSError:
            return None
        digest = hashlib.sha256()
        total = 0
        deadline = time.monotonic() + self._exe_deadline
        # the ABSOLUTE owner-END clamp (017-ad): the effective
        # deadline is the EARLIER of the relative
        # per-measurement cap and the SAME absolute anchor —
        # re-checked at EVERY actual read/return below, so a
        # channel registered earlier and reused later can never
        # refresh its window (no captured phase duration, no
        # fresh budget, no cleanup-grace measurement)
        if self._exe_end is not None:
            deadline = min(deadline, self._exe_end)
        first = None
        try:
            first = os.fstat(fd)
            if not stat.S_ISREG(first.st_mode):
                raise FixtureError("prep-exe-unreadable")
            # first-fstat size rejection: a regular file that
            # ALREADY exceeds the byte cap is refused before any
            # byte is read — a finite cap never authorizes a
            # whole unrelated chunk
            if first.st_size > self._max_exe_bytes:
                raise FixtureError("prep-proc-overbound")
            while True:
                if time.monotonic() > deadline:
                    raise FixtureError("prep-exe-timeout")
                # remaining-cap read clamp: at most the cap plus
                # ONE EOF sentinel byte is ever requested, so a
                # file that grows past the cap between the fstat
                # and a later read is refused after at most
                # cap+1 actual bytes (never a proportional copy)
                remaining = self._max_exe_bytes + 1 - total
                chunk = os.read(fd, min(1 << 20, remaining))
                if not chunk:
                    break
                total += len(chunk)
                if total > self._max_exe_bytes:
                    raise FixtureError("prep-proc-overbound")
                digest.update(chunk)
            # return-time expiry: an EOF read that returned
            # after the deadline crossed can never yield a
            # qualifying digest
            if time.monotonic() > deadline:
                raise FixtureError("prep-exe-timeout")
            last = os.fstat(fd)
            if last.st_dev != first.st_dev or last.st_ino != first.st_ino:
                raise FixtureError("prep-exe-unreadable")
            # final-frame return-time expiry
            if time.monotonic() > deadline:
                raise FixtureError("prep-exe-timeout")
        except FixtureError:
            raise
        except OSError:
            raise FixtureError("prep-exe-unreadable") from None
        finally:
            try:
                os.close(fd)
            except OSError:
                pass
        if first is None:
            raise FixtureError("prep-exe-unreadable")
        # current-executable re-verification: a FRESH open of
        # the kernel magic link re-resolves the process's
        # CURRENT executable — same-descriptor fstat and an
        # unchanged birth alone cannot detect an exec in the
        # same process, so a different file identity means the
        # hashed bytes are stale; closed refusal, never a
        # stale verified identity
        try:
            check_fd = os.open(exe, os.O_RDONLY)
        except OSError:
            raise FixtureError("prep-exe-unreadable") from None
        try:
            check = os.fstat(check_fd)
            if (
                not stat.S_ISREG(check.st_mode)
                or check.st_dev != first.st_dev
                or check.st_ino != first.st_ino
            ):
                raise FixtureError("prep-exe-changed")
        except OSError:
            raise FixtureError("prep-exe-unreadable") from None
        finally:
            try:
                os.close(check_fd)
            except OSError:
                pass
        # re-open frame return-time expiry
        if time.monotonic() > deadline:
            raise FixtureError("prep-exe-timeout")
        # identity binding AFTER the measurement: a PID/exec
        # reused mid-hash is not the measured process
        if self._birth(pid) != birth:
            raise FixtureError("prep-subject-invalid")
        # post-measurement identity read return-time expiry:
        # an expired context never returns a qualifying digest
        if time.monotonic() > deadline:
            raise FixtureError("prep-exe-timeout")
        return digest.hexdigest()

    def devpts_slave_metadata(self, pid: int, birth: int, name: int) -> DevptsSlaveMetadata | None:
        """The bounded real seam: lstat the subject's devpts
        mount root and the selected slave node through
        ``/proc/<pid>/root`` (the kernel exposes the subject's
        filesystem and mount view there — never a host
        ``/dev/pts`` enumeration).  The work is clamped to the
        finite metadata-operation bound AND to the SAME
        absolute owner END anchor this channel carries (no
        cleanup grace, no fresh window, no deadline reset),
        checked at USE (after the scope gate, after the
        birth binding, after EACH blocking lstat) and at
        RETURN (after the FINAL scope/identity frame).  The
        registered-CID scope and (pid, birth) identity are
        bound/re-checked as coherent frames before AND after;
        the root must be a directory and the slave a
        character device.  EVERY unbound, expired, raced or
        unreadable frame (denied access, vanished process,
        reused PID, drifted scope, non-directory root,
        non-character slave) is the typed unknown None — a
        denial or race is never a measurement."""
        if (
            not _is_pid(pid)
            or not _is_strict_int(birth)
            or not _is_strict_int(name)
            or name > _DEVPTS_MINOR_MAX
        ):
            raise FixtureError("prep-subject-invalid")
        # the finite operation bound clamped to the SAME
        # absolute owner END anchor (owner END only — never a
        # captured duration, never the cleanup grace).  The
        # closed end is CHECKED BEFORE the first scope/file
        # read: an already-expired owner END (or one exactly
        # at the boundary) never opens the seam
        deadline = time.monotonic() + self._metadata_deadline
        if self._exe_end is not None:
            deadline = min(deadline, self._exe_end)

        def _expired() -> bool:
            # the end is CLOSED: at the boundary the work is
            # already expired (no read at or past the end)
            return time.monotonic() >= deadline

        if _expired():
            return None
        if self.cgroup_scope(pid) is None:
            return None
        if _expired():
            return None
        # identity binding BEFORE the measurement: the (pid,
        # birth) pair must be the live process now
        if self._birth(pid) != birth:
            return None
        if _expired():
            return None
        root = self._root / str(pid) / "root" / "dev" / "pts"
        slave = root / str(name)
        try:
            root_st = os.lstat(root)
            if _expired():
                return None
            slave_st = os.lstat(slave)
        except OSError:
            return None
        if _expired():
            return None
        if not stat.S_ISDIR(root_st.st_mode) or not stat.S_ISCHR(slave_st.st_mode):
            return None
        # the FINAL coherent frames at return: the ACTUAL
        # scope and identity must still be bound (a raced
        # frame is a typed unknown, never a measurement) and
        # the bound must still hold — EACH step is expiry-
        # checked, as at entry (a proc read is never opened
        # at or past the closed end, even after the final
        # scope read crossed it)
        if self.cgroup_scope(pid) is None:
            return None
        if _expired():
            return None
        if self._birth(pid) != birth:
            return None
        if _expired():
            return None
        return DevptsSlaveMetadata(
            root_dev=root_st.st_dev,
            root_ino=root_st.st_ino,
            slave_dev=slave_st.st_dev,
            slave_ino=slave_st.st_ino,
            slave_mode=slave_st.st_mode,
            slave_uid=slave_st.st_uid,
            slave_gid=slave_st.st_gid,
            major=os.major(slave_st.st_rdev),
            minor=os.minor(slave_st.st_rdev),
        )


# The closed cid-membership law of a subject record:
# ``cid-scoped`` only when EVERY read went through the
# registered-CID channel (a process outside the registered
# container can never appear there); ``host-unscoped`` for a
# raw host-table observation, which a matching CID/run string
# can never upgrade — the verdict never composes an unscoped
# subject as native-ready.
CID_MEMBERSHIP = ("cid-scoped", "host-unscoped")


def collect_subject_identity(
    table: ProcTable,
    subject_pid: object,
    expectation: object,
    *,
    channel: CidScopedTable | None = None,
    subject_identity: tuple[int, int, tuple[int, ...]] | None = None,
) -> SubjectIdentity:
    """Collect and validate the native subject identity
    READ-ONLY.  The runtime subject view: when the registered
    CID channel is supplied, ALL reads (stat/cmdline/status
    and the executable) go through it — the channel scopes
    every read to the registered container and measures the
    ACTUAL running executable through the kernel exe link
    with birth binding and byte/time bounds — and the subject
    is recorded ``cid-scoped``.  Without a channel the
    measurement happens on the raw host table and the subject
    stays ``host-unscoped``: a host observation plus a
    matching CID/run string is NOT membership, and the
    verdict never composes an unscoped subject as ready.
    Measured: pid, uid/gid/groups, argv, tty, start_time —
    and the executable's sha256 via the channel (absent link =
    unmeasured, never assumed; a measured sha that
    CONTRADICTS the registered expectation is a closed
    refusal, never a fallback to the expectation value).
    Bound context: cid/run_id/binary expectation under the
    expectation's closed attestation — registered binding,
    never stamped as an observation.  An unobserved birth
    bound (min_start_time None) stays unproven: ``start_bound``
    is False, never True-by-default.  Vanished/unreadable is a
    closed refusal."""
    # the frozen owner-UID subject identity (017-ad): closed-
    # validated ONCE here (the same law the workflow applies at
    # construction); None keeps the original fixed-21002 law
    # byte-for-byte
    subject_identity = (
        _validate_frozen_subject_identity(subject_identity)
        if subject_identity is not None
        else None
    )
    exp = _validate_expectation(expectation)
    if not _is_pid(subject_pid):
        raise FixtureError("prep-subject-invalid")
    if channel is not None and channel.cid != exp.cid:
        # the channel's actually bound CID must equal the
        # expectation's registered CID BEFORE any read is
        # recorded: a channel observing a different container
        # can never establish same-context membership, no
        # matter what its process metadata says
        raise FixtureError("prep-channel-cid-mismatch")
    reader: ProcTable = channel if channel is not None else table
    raw_stat = reader.stat(subject_pid)
    raw_cmdline = reader.cmdline(subject_pid)
    raw_status = reader.status(subject_pid)
    if raw_stat is None or raw_cmdline is None or raw_status is None:
        raise FixtureError("prep-subject-vanished")
    ps = parse_proc_stat(raw_stat.decode("ascii", "replace"))
    argv = parse_proc_cmdline(raw_cmdline)
    uid, gid, groups = parse_proc_status(raw_status)
    # the scoped SUBJECT frame carries AUTHORITY: a registered
    # subject is a real job process, so its group and session
    # are strictly positive finite identity — a well-formed
    # ZERO pgrp/session observation (however the tty/birth/UID
    # match) is never a usable subject receipt
    if not _is_pid(ps.pgrp) or not _is_pid(ps.session):
        raise FixtureError("prep-subject-invalid")
    if exp.expected_tty is not None and ps.tty != exp.expected_tty:
        raise FixtureError("prep-tty-invalid")
    if exp.min_start_time is not None and ps.start_time < exp.min_start_time:
        raise FixtureError("prep-start-unbound")
    _check_identity_fields(uid, gid, groups, argv, ps.tty, subject_identity=subject_identity)
    measured_binary: str | None = None
    if channel is not None:
        measured_binary = channel.exe_sha256(subject_pid, ps.start_time)
    if measured_binary is not None and measured_binary != exp.binary_sha256:
        # a measured fact contradicts the registered binding:
        # closed refusal, never silently re-bound
        raise FixtureError("prep-binary-invalid")
    if channel is not None:
        # frame coherence across the executable measurement:
        # the recorded frame must still be the SAME process
        # (pid, birth) with the SAME argv/UID/TTY when the
        # identity is composed — a contradictory later read
        # is never stamped onto the measured binary
        raw_stat2 = reader.stat(subject_pid)
        raw_cmdline2 = reader.cmdline(subject_pid)
        raw_status2 = reader.status(subject_pid)
        if raw_stat2 is None or raw_cmdline2 is None or raw_status2 is None:
            raise FixtureError("prep-subject-vanished")
        try:
            ps2 = parse_proc_stat(raw_stat2.decode("ascii", "replace"))
            argv2 = parse_proc_cmdline(raw_cmdline2)
            uid2, gid2, groups2 = parse_proc_status(raw_status2)
        except FixtureError:
            raise FixtureError("prep-subject-invalid") from None
        # the POST-EXECUTABLE frame is the SAME authority: the
        # current group/session must still be strictly positive
        # finite identity when the identity is composed
        if not _is_pid(ps2.pgrp) or not _is_pid(ps2.session):
            raise FixtureError("prep-subject-invalid")
        if (
            ps2.pid != ps.pid
            or ps2.start_time != ps.start_time
            or ps2.tty != ps.tty
            or argv2 != argv
            or (uid2, gid2, groups2) != (uid, gid, groups)
        ):
            raise FixtureError("prep-subject-invalid")
    start_bound = exp.min_start_time is not None
    pty_matched = (
        exp.expected_tty is not None and exp.expected_tty > 0 and ps.tty == exp.expected_tty
    )
    cid_membership = "cid-scoped" if channel is not None else "host-unscoped"
    return SubjectIdentity(
        source=NATIVE_SOURCE,
        cid=exp.cid,
        pid=subject_pid,
        uid=uid,
        gid=gid,
        groups=tuple(groups),
        argv=tuple(argv),
        argv_sha256=argv_digest(argv),
        binary_sha256=measured_binary,
        binary_verified=measured_binary is not None,
        cid_attestation=exp.attestation,
        cid_membership=cid_membership,
        tty=ps.tty,
        start_time=ps.start_time,
        start_bound=start_bound,
        run_id=exp.run_id,
        pty_matched=pty_matched,
    )


_SUBJECT_KEYS = frozenset(
    {
        "source",
        "cid",
        "pid",
        "uid",
        "gid",
        "groups",
        "argv",
        "argv_sha256",
        "binary_sha256",
        "binary_verified",
        "cid_attestation",
        "cid_membership",
        "tty",
        "start_time",
        "start_bound",
        "run_id",
        "pty_matched",
    }
)


def validate_subject_identity(
    record: object,
    expectation: object,
    subject_identity: tuple[int, int, tuple[int, ...]] | None = None,
) -> SubjectIdentity:
    """Validate a RETAINED (serialized) subject-identity record
    against the expectation: exact closed keys and strict
    types, the closed identity law, the recomputed argv digest
    and the run/cid/binary binding, with the measured/bound
    split intact: an unmeasured binary (None) is only valid
    with ``binary_verified`` false, a ``host-unscoped``
    membership is only valid unmeasured, and the cid
    attestation stays in its closed set.  A record is never
    trusted by flag: a forged or drifted record is a closed
    non-echoing refusal.  An unbound birth (``start_bound``
    false with no min bound to reprove) is incomplete, not
    ready — the verdict composes it as not-ready."""
    subject_identity = (
        _validate_frozen_subject_identity(subject_identity)
        if subject_identity is not None
        else None
    )
    exp = _validate_expectation(expectation)
    if not isinstance(record, Mapping) or set(record) != _SUBJECT_KEYS:
        raise FixtureError("prep-record-malformed")
    values: dict[str, object] = dict(record)
    for key in ("source", "cid", "argv_sha256", "run_id", "cid_attestation", "cid_membership"):
        if not isinstance(values[key], str):
            raise FixtureError("prep-record-malformed")
    binary_sha = values["binary_sha256"]
    if binary_sha is not None and not isinstance(binary_sha, str):
        raise FixtureError("prep-record-malformed")
    if values["cid_attestation"] not in _CID_ATTESTATIONS:
        raise FixtureError("prep-source-invalid")
    if values["cid_membership"] not in CID_MEMBERSHIP:
        raise FixtureError("prep-record-malformed")
    binary_verified = values["binary_verified"] is True
    if isinstance(binary_sha, str):
        # a measured binary is a measured fact: it must match
        # the registered binding AND be marked verified
        if binary_sha != exp.binary_sha256 or not binary_verified:
            raise FixtureError("prep-binary-invalid")
    elif binary_verified:
        raise FixtureError("prep-binary-invalid")
    if values["cid_membership"] == "host-unscoped" and (binary_verified or binary_sha is not None):
        # a raw host-table observation never carries a
        # measured/verified binary or an upgraded membership
        raise FixtureError("prep-record-malformed")
    for key in ("pid", "uid", "gid", "tty", "start_time"):
        if not _is_strict_int(values[key]):
            raise FixtureError("prep-record-malformed")
    if not isinstance(values["groups"], list) or not _is_strict_int_check_list(values["groups"]):
        raise FixtureError("prep-record-malformed")
    if not isinstance(values["argv"], list) or not all(isinstance(a, str) for a in values["argv"]):
        raise FixtureError("prep-record-malformed")
    start_bound = values["start_bound"] is True
    if not start_bound and exp.min_start_time is not None:
        if values["start_time"] < exp.min_start_time:
            raise FixtureError("prep-start-unbound")
    if not isinstance(values["pty_matched"], bool):
        raise FixtureError("prep-record-malformed")
    pty_matched = values["pty_matched"] is True
    if pty_matched and (exp.expected_tty is None or exp.expected_tty <= 0):
        # a forged matched PTY provenance with no actually
        # bound nonzero expected PTY is a closed refusal
        raise FixtureError("prep-record-malformed")
    if values["source"] != NATIVE_SOURCE:
        raise FixtureError("prep-source-invalid")
    if values["cid"] != exp.cid:
        raise FixtureError("prep-cid-invalid")
    if values["run_id"] != exp.run_id:
        raise FixtureError("prep-record-malformed")
    if argv_digest(tuple(values["argv"])) != values["argv_sha256"]:
        raise FixtureError("prep-record-malformed")
    if exp.expected_tty is not None and values["tty"] != exp.expected_tty:
        raise FixtureError("prep-tty-invalid")
    _check_identity_fields(
        values["uid"],
        values["gid"],
        tuple(values["groups"]),
        values["argv"],
        values["tty"],
        subject_identity=subject_identity,
    )
    return SubjectIdentity(
        source=NATIVE_SOURCE,
        cid=values["cid"],
        pid=values["pid"],
        uid=values["uid"],
        gid=values["gid"],
        groups=tuple(values["groups"]),
        argv=tuple(values["argv"]),
        argv_sha256=values["argv_sha256"],
        binary_sha256=binary_sha if isinstance(binary_sha, str) else None,
        binary_verified=binary_verified,
        cid_attestation=values["cid_attestation"],
        cid_membership=values["cid_membership"],
        tty=values["tty"],
        start_time=values["start_time"],
        start_bound=start_bound,
        run_id=values["run_id"],
        pty_matched=pty_matched,
    )


def _is_strict_int_check_list(values: list) -> bool:
    return all(_is_strict_int(v) for v in values)


# -- restoration facts -------------------------------------------------------------


@dataclass(frozen=True)
class RestorationFacts:
    """The READ-ONLY same-job phase facts, measured
    INDEPENDENTLY of the fixture owner (teardown-before-restore
    ordering): the worker's CURRENT state (``worker_stopped`` =
    the STOPPED phase is currently observed), the Bash state,
    the worker's own stat tpgid (process metadata) and the
    caller's observed tty foreground, with ``stop_recorded``
    saying whether a separately measured stop receipt was
    supplied.  ``restored`` is a measured boolean holding ONLY
    for the RUNNING phase after a recorded stop: the same
    worker (pid, birth, group G, session, TTY) running again,
    its stat tpgid on G, AND the caller's observed foreground
    cross-checked on G — a caller argument can never mint a
    foreground the process metadata does not show.  A worker
    still stopped, an unobserved or contradicting foreground,
    or a missing recorded stop is never restored."""

    worker_pid: int
    worker_state: str | None
    worker_tpgid: int | None
    worker_stopped: bool
    stop_recorded: bool
    bash_pid: int
    bash_state: str | None
    bash_pgrp: int | None
    tty_foreground_pgrp: int | None
    restored: bool


@dataclass(frozen=True)
class StopReceipt:
    """A separately RECORDED, measured worker-stop observation:
    the exact worker (pid, birth, pgrp G, session, TTY)
    observed in the STOPPED state (T) while its parent Bash
    runs and HAS RECLAIMED the tty foreground (runbook 11c
    step 2: in the STABLE stopped phase every intended G
    member is T, G differs from B's group, and the foreground
    observed on the worker's own stat tpgid is B.pgrp — G does
    NOT hold the foreground while stopped).  A stop is a
    recorded EVENT, not a re-derived flag: restoration is
    measured AGAINST such a receipt — a single current
    snapshot can never prove a past stop."""

    worker_pid: int
    worker_start_time: int
    worker_pgrp: int
    worker_session: int
    worker_tty: int
    worker_tpgid: int
    bash_pid: int
    bash_state: str
    bash_pgrp: int


def collect_stop_observation(table: ProcTable, worker_pid: object, bash_pid: object) -> StopReceipt:
    """Collect the separately recorded stop observation
    READ-ONLY (no signal of any kind — the stop itself is
    performed later by the separately authorized operator).
    The STABLE stopped phase is measured exactly: the worker
    OBSERVED stopped (state T), its parent bash RUNNING, G
    differing from B's group, and the tty foreground OBSERVED
    (on the worker's own stat tpgid) back on B's group — Bash
    has reclaimed the TTY; requiring G to still hold the
    foreground during the stopped phase is a different (and
    not the runbook's) phase and is refused.  Anything else is
    a closed refusal: a stop is recorded when it is actually
    observed, never assumed or inferred from a later state."""
    if not _is_pid(worker_pid):
        raise FixtureError("prep-worker-invalid")
    if not _is_pid(bash_pid):
        raise FixtureError("prep-bash-invalid")
    w = _try_parse_stat(table, worker_pid)
    if w is None:
        raise FixtureError("prep-worker-vanished")
    if w.state != "T":
        raise FixtureError("prep-stop-unobserved")
    b = _try_parse_stat(table, bash_pid)
    if b is None:
        raise FixtureError("prep-bash-vanished")
    if b.state not in _RUNNING_STATES:
        raise FixtureError("prep-stop-unobserved")
    # a stop receipt carries AUTHORITY: the observed worker
    # group/session and the Bash group/session are strictly
    # positive finite identity (a well-formed ZERO pgrp/session
    # observation is never a stop receipt, never a foreground-
    # reclaim target)
    if not _is_pid(w.pgrp) or not _is_pid(w.session):
        raise FixtureError("prep-stop-unobserved")
    if not _is_pid(b.pgrp) or not _is_pid(b.session):
        raise FixtureError("prep-stop-unobserved")
    if w.ppid != b.pid:
        raise FixtureError("prep-stop-unobserved")
    if b.pgrp == w.pgrp:
        # runbook 11c: G differs from B's group in the
        # right-pane job layout
        raise FixtureError("prep-stop-unobserved")
    if w.tpgid != b.pgrp:
        # the foreground is observed back on B's group (Bash
        # reclaimed the TTY); any other foreground is a
        # different phase
        raise FixtureError("prep-stop-unobserved")
    # the COMPLETE stop: every other observed member of G is
    # stopped too (an unstopped G member is a partial stop,
    # not the recorded stable phase); a listed entry with a
    # None stat is tri-stated through the bounded absence
    # seam — only an independently VERIFIED-gone entry may be
    # ignored (bounded churn law); an unreadable still-
    # existing or unprovable entry cannot establish
    # nonmembership or a complete G; a malformed G-member row
    # is not an established stop
    for pid in table.list_pids():
        if pid == w.pid:
            continue  # verified T above
        raw = table.stat(pid)
        if raw is None:
            if _verified_absence(table, pid) is not True:
                raise FixtureError("prep-stop-unobserved")
            continue
        try:
            entry = parse_proc_stat(raw.decode("ascii", "replace"))
        except FixtureError:
            raise FixtureError("prep-stop-unobserved") from None
        if entry.pgrp == w.pgrp and entry.state != "T":
            raise FixtureError("prep-stop-unobserved")
    return StopReceipt(
        worker_pid=w.pid,
        worker_start_time=w.start_time,
        worker_pgrp=w.pgrp,
        worker_session=w.session,
        worker_tty=w.tty,
        worker_tpgid=w.tpgid,
        bash_pid=b.pid,
        bash_state=b.state,
        bash_pgrp=b.pgrp,
    )


def collect_restoration(
    table: ProcTable,
    worker_pid: object,
    bash_pid: object,
    foreground_pgrp: int | None = None,
    *,
    stop_receipt: StopReceipt | None = None,
) -> RestorationFacts:
    """Collect the same-job phase facts READ-ONLY.  Vanished
    processes are honest unknowns (state None), never
    assumptions.  A worker currently observed in state T is
    the STOPPED phase — reported as such, never as restored.
    ``restored`` holds only for the RUNNING phase after a
    separately recorded stop of the same worker (pid, birth,
    group G, session, TTY), with the foreground read from the
    worker's own stat tpgid AND cross-checked against the
    caller's observed foreground — a caller argument can never
    mint a foreground the process metadata does not show; an
    unobserved or contradicting foreground is not restored."""
    if not _is_pid(worker_pid):
        raise FixtureError("prep-worker-invalid")
    if not _is_pid(bash_pid):
        raise FixtureError("prep-bash-invalid")
    if foreground_pgrp is not None and not _is_pid(foreground_pgrp):
        raise FixtureError("prep-worker-invalid")
    if stop_receipt is not None and not isinstance(stop_receipt, StopReceipt):
        raise FixtureError("prep-verdict-input-invalid")
    w = _try_parse_stat(table, worker_pid)
    b = _try_parse_stat(table, bash_pid)
    worker_stopped = w is not None and w.state == "T"
    restored = bool(
        w is not None
        and b is not None
        and w.state in _RUNNING_STATES
        and b.state in _RUNNING_STATES
        and stop_receipt is not None
        and stop_receipt.worker_pid == w.pid
        and stop_receipt.worker_start_time == w.start_time
        and stop_receipt.worker_pgrp == w.pgrp
        and stop_receipt.worker_session == w.session
        and stop_receipt.worker_tty == w.tty
        # the restored verdict carries AUTHORITY: the CURRENT
        # worker AND Bash group/session frames are strictly
        # positive finite identity, independent of the supplied
        # receipt fields (a well-formed ZERO pgrp/session
        # observation can never earn a restored or native-ready
        # verdict, however the supplied receipt or the other
        # measurements match)
        and _is_pid(w.pgrp)
        and _is_pid(w.session)
        and _is_pid(b.pgrp)
        and _is_pid(b.session)
        and w.tpgid == w.pgrp
        and foreground_pgrp is not None
        and foreground_pgrp == w.pgrp
    )
    return RestorationFacts(
        worker_pid=worker_pid,
        worker_state=w.state if w is not None else None,
        worker_tpgid=w.tpgid if w is not None else None,
        worker_stopped=worker_stopped,
        stop_recorded=stop_receipt is not None,
        bash_pid=bash_pid,
        bash_state=b.state if b is not None else None,
        bash_pgrp=b.pgrp if b is not None else None,
        tty_foreground_pgrp=foreground_pgrp,
        restored=restored,
    )


def _try_parse_stat(table: ProcTable, pid: int) -> ProcStat | None:
    raw = table.stat(pid)
    if raw is None:
        return None
    return parse_proc_stat(raw.decode("ascii", "replace"))


# -- owner final facts ---------------------------------------------------------------


@dataclass(frozen=True)
class OwnerFinalFacts:
    """The fixture owner's OWN final facts, parsed from its
    retained evidence record (the 017-s closed schema,
    unchanged in meaning and bound to its producer: the
    historical 017-s rehearsal record for order 017-s only).
    The safety flags keep their ORIGINAL meaning: the closed
    safety facts of that rehearsal run as a whole — never
    relabeled as owner-launched-process flags, kept separate
    from the external-native facts, and never re-asserted
    about the host or a later native run by the verdict.
    ``binary_sha256`` is the pinned executable identity from
    the run's artifact facts: the registered binding the
    later subject's MEASURED exe identity must match (a
    measured mismatch is a refusal, an unmeasured one stays
    unmeasured)."""

    schema: str
    status: str
    run_id: str
    cid: str
    export_sha256: str
    binary_sha256: str
    teardown_verified: bool
    sentinel_survived: bool
    descendants_after: int
    codex_invoked: bool
    worker_stopped: bool
    native_started: bool
    native_ready: bool


def parse_owner_final_facts(record: object) -> OwnerFinalFacts:
    """Parse the owner's retained evidence into the typed
    final facts.  Closed schema, closed subset, strict types:
    the exact CID, verified teardown (positive-before /
    negative-after on the exact CID and image, zero
    descendants), sentinel survival, the exported sha, and the
    owner's own safety flags at their closed S values.  The
    record is BOUND to its producer: ``record`` and ``order``
    must both be exactly the historical 017-s values — a
    later native-owner producer must carry its own explicit
    versioned schema and is refused, never reinterpreted.  A
    malformed, drifted, non-pass or foreign-producer record
    is a closed non-echoing refusal — a retained record that
    does not parse is not evidence."""
    if not isinstance(record, Mapping):
        raise FixtureError("prep-owner-record-malformed")
    if record.get("record") != _S_EVIDENCE_SCHEMA:
        raise FixtureError("prep-owner-record-malformed")
    if record.get("order") != _S_ORDER_ID:
        raise FixtureError("prep-owner-record-malformed")
    try:
        status = record["status"]
        run_id = record["run_id"]
        prepared = record["prepared"]
        cid = prepared["cid"]
        export = record["export"]
        export_sha = export["sha256"]
        artifact = record["artifact"]
        binary_sha = artifact["binary_sha256"]
        teardown = record["teardown"]
        container_present_before = teardown["container_present_before"]
        container_removal = teardown["container_removal"]
        image_removal = teardown["image_removal"]
        descendants_after = teardown["descendants_after"]
        sentinel_survived = teardown["sentinel_survived"]
        codex_invoked = record["codex_invoked"]
        worker_stopped = record["worker_stopped"]
        native_started = record["native_started"]
        native_ready = record["native_ready"]
    except (KeyError, TypeError):
        raise FixtureError("prep-owner-record-malformed") from None
    if (
        status != "pass"
        or not isinstance(run_id, str)
        or _RUN_ID_RE.fullmatch(run_id) is None
        or not isinstance(cid, str)
        or _CID_RE.fullmatch(cid) is None
        or not isinstance(export_sha, str)
        or _SHA_RE.fullmatch(export_sha) is None
        or not isinstance(binary_sha, str)
        or _SHA_RE.fullmatch(binary_sha) is None
        or not isinstance(prepared, Mapping)
        or container_present_before is not True
        or container_removal != "absent-verified"
        or image_removal != "absent-verified"
        or not isinstance(descendants_after, int)
        or isinstance(descendants_after, bool)
        or descendants_after != 0
        or sentinel_survived is not True
        or codex_invoked is not False
        or worker_stopped is not False
        or native_started is not False
        or native_ready is not False
    ):
        raise FixtureError("prep-owner-record-malformed")
    teardown_verified = (
        container_present_before is True
        and container_removal == "absent-verified"
        and image_removal == "absent-verified"
        and descendants_after == 0
    )
    return OwnerFinalFacts(
        schema=OWNER_FACTS_SCHEMA,
        status=status,
        run_id=run_id,
        cid=cid,
        export_sha256=export_sha,
        binary_sha256=binary_sha,
        teardown_verified=teardown_verified,
        sentinel_survived=sentinel_survived,
        descendants_after=descendants_after,
        codex_invoked=codex_invoked,
        worker_stopped=worker_stopped,
        native_started=native_started,
        native_ready=native_ready,
    )


def expectation_from_owner(
    owner: object,
    *,
    min_start_time: int | None,
    expected_tty: int | None,
) -> SubjectExpectation:
    """The narrow registered-CID-aware bridge: build the
    REGISTERED subject expectation from the parsed, verified
    owner final facts (cid and run from the owner record, the
    pinned binary sha from the owner's artifact facts).  The
    attestation string records this provenance only — it is
    NOT a measurement: the subject's process identity is still
    measured by the collectors (and the exe bridge) against
    this registered binding, and unknown/unmeasured facts
    stay unknown."""
    if not isinstance(owner, (OwnerFinalFacts, NativeOwnerFacts)):
        raise FixtureError("prep-owner-record-malformed")
    return SubjectExpectation(
        cid=owner.cid,
        binary_sha256=owner.binary_sha256,
        run_id=owner.run_id,
        min_start_time=min_start_time,
        expected_tty=expected_tty,
        attestation="registered-owner-record",
    )


# -- AF native attach-binding pure core (017-ae software) ------------------------
# The independent fixture-namespace PTY producer of the
# canonical FUTURE 017-af entry (INERT in 017-ae: software
# only — NO actual fixture, admission, Docker, native or
# client operation).  The measured devpts facts come from the
# owner's ONE bounded NON-PTY probe (the closed record); this
# pure core is the measurement-to-facts boundary: strict
# non-echoing parsing of the closed record (the measured
# devpts POLICY fact included — the permitted node GID/MODE
# and filesystem type bound to the SAME measured namespace
# root, never assumed from the process identity), the
# PRIMARY-SOURCE-VERIFIED proc tty_nr encoding
# (``new_encode_dev`` — distinct from the kernel-internal
# MKDEV layout, never a makedev convenience), the closed
# allocation derivation (the UNIQUE fresh owned slave
# between two same-namespace observations) and the DISTINCT
# identity-bearing attach-binding record with its tag-pair
# law.  The expected PTY is derived ONLY from the owned
# allocation, never from the subject itself, and the node
# GID of an allocation is a MEASURED fact (legal to differ
# from the process GID), never an assumption.
_DEVPTS_MAJOR_MAX = 4095  # the 12-bit major field
_DEVPTS_MINOR_MAX = 1048575  # the 20-bit minor field (MINORBITS 20)
_TTY_NR_MAX = 2**31 - 1  # strict positive signed 32-bit tty_nr
_DEVPTS_FAIL_KEYS = frozenset({"record", "status", "reason"})
_DEVPTS_INVENTORY_TOP_KEYS = frozenset(
    {"record", "status", "uid", "namespace", "policy", "isolation", "slave_rows"}
)
_DEVPTS_POLICY_KEYS = frozenset({"fstype", "gid", "mode"})
_ATTACH_ALLOCATION_KEYS = frozenset({"name", "major", "minor", "inode", "mode", "uid", "gid"})


def new_encode_dev(major: object, minor: object) -> int:
    """The proc tty_nr encoding, PRIMARY-SOURCE-VERIFIED:
    ``(minor & 0xff) | (major << 8) | ((minor & ~0xff) << 12)``.
    This is the /proc/PID/stat ``tty_nr`` representation —
    distinct from the kernel-internal MKDEV layout and never a
    udev makedev convenience.  Strict non-bool integers in the
    closed 12-bit major / 20-bit minor domains; out-of-domain
    or non-integer input is a closed non-echoing refusal."""
    if (
        isinstance(major, bool)
        or not isinstance(major, int)
        or isinstance(minor, bool)
        or not isinstance(minor, int)
        or major < 0
        or major > _DEVPTS_MAJOR_MAX
        or minor < 0
        or minor > _DEVPTS_MINOR_MAX
    ):
        raise FixtureError("prep-devpts-device-invalid")
    return (minor & 0xFF) | (major << 8) | ((minor & ~0xFF) << 12)


def expected_tty_nr_qualifies(value: object) -> bool:
    """The closed qualification of a DERIVED expected proc
    tty_nr: a strict positive signed 32-bit integer
    (``0 < v <= 2**31-1``).  Zero (no controlling terminal),
    out-of-domain values and non-strict values are NOT
    qualified — never ready-by-casting."""
    return isinstance(value, int) and not isinstance(value, bool) and 0 < value <= _TTY_NR_MAX


@dataclass(frozen=True)
class DevptsInventory:
    """ONE measured fixture-namespace devpts snapshot (typed):
    the measured namespace root ``(st_dev, st_ino)``, the
    bounded measured devpts POLICY fact (the filesystem type,
    permitted node GID and node MODE of the single mountinfo
    entry binding that root to /dev/pts — measured, never
    assumed), the closed measured isolation flags
    ``(site, startup)``, the measured probe uid, and the
    closed slave-row vector (each row: name, major, minor,
    inode, mode, uid, gid — the name is the canonical decimal
    value, equal to the minor).  Rows are measured facts;
    their GID/MODE are validated against the measured policy
    at parse, never against the process identity."""

    namespace: tuple[int, int]
    policy: tuple[str, int, int]
    isolation: tuple[bool, bool]
    uid: int
    slave_rows: tuple[tuple[int, int, int, int, int, int, int], ...]


@dataclass(frozen=True)
class DevptsObservation:
    """The owner-level bounded observation: the closed probe
    record (the exact retained bytes, parse-validated)
    together with its typed inventory facts.  The record is
    what the attach-binding receipt embeds; the typed facts
    are the derivation inputs."""

    record: bytes
    inventory: DevptsInventory


def _parse_devpts_inventory_object(obj: object) -> DevptsInventory:
    """The closed OBJECT-LEVEL law of the AF devpts inventory
    (017-ae software), shared by the bytes consumer and the
    attach-binding record consumer (an embedded mapping is
    validated DIRECTLY against this grammar — never
    re-serialized merely to discover a bound): the closed
    record tag; the fail form (exact three keys, a closed
    reason) propagated as the typed ``local-<reason>``
    refusal (a failed query is never absence); the pass form
    (exact seven keys) strict throughout — the measured uid,
    the measured namespace root (a zero inode is not a
    measured valid root), the measured POLICY fact
    (filesystem type, node GID, node MODE), the measured
    isolation flags (a non-isolated probe is a closed
    refusal), and the slave rows (bounded, canonical, domain-
    strict, node GID/MODE equal to the MEASURED policy —
    never assumed from the process identity, never blindly
    accepted, no duplicate names).  The closed domains apply
    to the EMPTY baseline case exactly as to a populated one.
    Anything else is a closed non-echoing refusal."""
    if not isinstance(obj, dict) or obj.get("record") != ci.DEVPTS_PROBE_RECORD:
        raise FixtureError("prep-devpts-record-malformed")
    if set(obj) == _DEVPTS_FAIL_KEYS:
        status = obj.get("status")
        reason = obj.get("reason")
        if status != "fail" or not isinstance(reason, str) or reason not in ci.DEVPTS_FAIL_REASONS:
            raise FixtureError("prep-devpts-record-malformed")
        raise FixtureError("local-" + reason)
    if set(obj) != _DEVPTS_INVENTORY_TOP_KEYS or obj.get("status") != "pass":
        raise FixtureError("prep-devpts-record-malformed")
    uid = obj.get("uid")
    if (
        isinstance(uid, bool)
        or not isinstance(uid, int)
        or not (1 <= uid <= fidentity.LINUX_ID_MAX)
    ):
        raise FixtureError("prep-devpts-uid-invalid")
    namespace = obj.get("namespace")
    if (
        not isinstance(namespace, list)
        or len(namespace) != 2
        or any(isinstance(v, bool) or not isinstance(v, int) or v < 0 for v in namespace)
        # a zero inode is not a measured valid root
        or namespace[1] <= 0
    ):
        raise FixtureError("prep-devpts-namespace-invalid")
    policy = obj.get("policy")
    if (
        not isinstance(policy, dict)
        or set(policy) != _DEVPTS_POLICY_KEYS
        or policy.get("fstype") != "devpts"
        or isinstance(policy.get("gid"), bool)
        or not isinstance(policy.get("gid"), int)
        or not (0 <= policy["gid"] <= fidentity.LINUX_ID_MAX)
        or isinstance(policy.get("mode"), bool)
        or not isinstance(policy.get("mode"), int)
        or not (0 <= policy["mode"] <= 0o7777)
    ):
        raise FixtureError("prep-devpts-policy-invalid")
    isolation = obj.get("isolation")
    if (
        not isinstance(isolation, dict)
        or set(isolation) != {"site", "startup"}
        or not isinstance(isolation.get("site"), bool)
        or not isinstance(isolation.get("startup"), bool)
        or isolation["site"] is not False
        or isolation["startup"] is not False
    ):
        raise FixtureError("prep-devpts-not-isolated")
    rows_raw = obj.get("slave_rows")
    if not isinstance(rows_raw, list) or len(rows_raw) > ci.DEVPTS_MAX_SLAVE_ROWS:
        raise FixtureError("prep-devpts-rows-overbound")
    policy_gid = policy["gid"]
    policy_mode = policy["mode"]
    rows: list[tuple[int, int, int, int, int, int, int]] = []
    seen: set[int] = set()
    for row in rows_raw:
        if (
            not isinstance(row, list)
            or len(row) != 7
            or not isinstance(row[0], str)
            # ASCII DECIMAL canonical name: bounded before any
            # conversion (a superscript digit or a long digit
            # string is a row refusal, never a raw error)
            or not row[0].isascii()
            or not row[0].isdigit()
            or len(row[0]) > 7
            or row[0] != str(int(row[0]))
        ):
            raise FixtureError("prep-devpts-row-malformed")
        name = int(row[0])
        major, minor, inode, mode, ruid, rgid = row[1], row[2], row[3], row[4], row[5], row[6]
        if (
            name != minor
            or name in seen
            or isinstance(major, bool)
            or not isinstance(major, int)
            or not (0 <= major <= _DEVPTS_MAJOR_MAX)
            or isinstance(minor, bool)
            or not isinstance(minor, int)
            or not (0 <= minor <= _DEVPTS_MINOR_MAX)
            or isinstance(inode, bool)
            or not isinstance(inode, int)
            or inode <= 0
            or isinstance(mode, bool)
            or not isinstance(mode, int)
            or not (0 <= mode <= 0o7777)
            or isinstance(ruid, bool)
            or not isinstance(ruid, int)
            or not (0 <= ruid <= fidentity.LINUX_ID_MAX)
            or isinstance(rgid, bool)
            or not isinstance(rgid, int)
            or not (0 <= rgid <= fidentity.LINUX_ID_MAX)
        ):
            raise FixtureError("prep-devpts-row-malformed")
        # the measured policy law: the node GID/MODE must equal
        # the MEASURED devpts policy fact (bound to the same
        # measured namespace root) — never assumed from the
        # process identity, never blindly accepted
        if rgid != policy_gid or mode != policy_mode:
            raise FixtureError("prep-devpts-node-policy")
        seen.add(name)
        rows.append((name, major, minor, inode, mode, ruid, rgid))
    return DevptsInventory(
        namespace=(namespace[0], namespace[1]),
        policy=("devpts", policy_gid, policy_mode),
        isolation=(isolation["site"], isolation["startup"]),
        uid=uid,
        slave_rows=tuple(rows),
    )


def parse_devpts_inventory_record(raw: object) -> DevptsObservation:
    """The closed pure consumer of the AF devpts probe record
    (017-ae software): a bounded single-line ASCII JSON
    document, duplicate keys refused at every nesting level,
    validated through the shared closed object-level law and
    retained together with its typed inventory facts.  The
    size is checked BEFORE any copy (an oversized bytearray
    is refused, never copied first).  Anything else is a
    closed non-echoing refusal."""
    if not isinstance(raw, (bytes, bytearray)):
        raise FixtureError("prep-devpts-record-malformed")
    if len(raw) > ci.DEVPTS_OUTPUT_MAX:
        raise FixtureError("prep-devpts-output-overbound")
    raw = bytes(raw)
    body = raw[:-1] if raw.endswith(b"\n") else raw
    if not body or b"\n" in body or b"\r" in body:
        raise FixtureError("prep-devpts-record-malformed")

    def _no_duplicate_pairs(pairs: list) -> dict:
        # duplicate keys are a closed refusal at EVERY nesting
        # level (json.loads silently keeps the last one — a
        # shadowed value is never a measured fact)
        seen = set()
        for key, _value in pairs:
            if key in seen:
                raise ValueError("duplicate-key")
            seen.add(key)
        return dict(pairs)

    try:
        obj = json.loads(body.decode("ascii"), object_pairs_hook=_no_duplicate_pairs)
    except (UnicodeDecodeError, ValueError, RecursionError):
        # a deeply nested document under the byte cap is the
        # SAME malformed record (the parser's recursion
        # exhaustion is normalized to the fixed typed refusal,
        # never a raw escape — the caller's consumed failed
        # phase can retain it)
        raise FixtureError("prep-devpts-record-malformed") from None
    inventory = _parse_devpts_inventory_object(obj)
    return DevptsObservation(record=raw, inventory=inventory)


@dataclass(frozen=True)
class DevptsAllocation:
    """The UNIQUE fresh owned slave allocation between two
    same-namespace observations (derived, never caller-
    asserted): the measured node identity, its MEASURED uid
    (required to equal the subject uid) and its MEASURED gid
    (a measured fact validated against the policy at parse —
    legal to differ from the process GID), and the DERIVED
    expected proc tty_nr (the encoding of the owned device —
    never copied from the subject)."""

    name: int
    major: int
    minor: int
    inode: int
    mode: int
    uid: int
    gid: int
    expected_tty_nr: int


def derive_attach_allocation(
    baseline: DevptsInventory,
    observation: DevptsInventory,
    *,
    subject_uid: object,
) -> DevptsAllocation:
    """The closed allocation derivation: the two observations
    must be the SAME measured namespace carrying the SAME
    measured policy; every baseline row must persist
    UNCHANGED (removals and metadata drift are churn, never
    tolerated); EXACTLY ONE fresh slave (a new name with a
    fresh inode, owned by the subject uid — the node GID is a
    measured fact, NEVER assumed to equal the process GID) is
    the allocation; its expected proc tty_nr is DERIVED
    through ``new_encode_dev`` and must qualify (a device the
    kernel cannot represent as a positive signed tty_nr is
    refused, never truncated).  Every mismatch is a closed
    non-echoing refusal."""
    if not isinstance(baseline, DevptsInventory) or not isinstance(observation, DevptsInventory):
        raise FixtureError("prep-devpts-record-malformed")
    if baseline.namespace != observation.namespace:
        raise FixtureError("prep-devpts-namespace-mismatch")
    if baseline.policy != observation.policy:
        raise FixtureError("prep-devpts-policy-mismatch")
    if isinstance(subject_uid, bool) or not isinstance(subject_uid, int) or subject_uid <= 0:
        raise FixtureError("prep-devpts-owner-mismatch")
    base_rows = {row[0]: row for row in baseline.slave_rows}
    obs_rows = {row[0]: row for row in observation.slave_rows}
    for name, base_row in base_rows.items():
        if obs_rows.get(name) != base_row:
            raise FixtureError("prep-devpts-churn")
    added = [obs_rows[name] for name in obs_rows if name not in base_rows]
    if not added:
        raise FixtureError("prep-devpts-allocation-none")
    if len(added) > 1:
        raise FixtureError("prep-devpts-allocation-ambiguous")
    name, major, minor, inode, mode, ruid, rgid = added[0]
    if inode in {row[3] for row in baseline.slave_rows}:
        raise FixtureError("prep-devpts-inode-reuse")
    if ruid != subject_uid:
        raise FixtureError("prep-devpts-owner-mismatch")
    try:
        expected = new_encode_dev(major, minor)
    except FixtureError:
        raise FixtureError("prep-devpts-encoding-unrepresentable") from None
    if not expected_tty_nr_qualifies(expected):
        raise FixtureError("prep-devpts-encoding-unrepresentable")
    return DevptsAllocation(
        name=name,
        major=major,
        minor=minor,
        inode=inode,
        mode=mode,
        uid=ruid,
        gid=rgid,
        expected_tty_nr=expected,
    )


AF_ATTACH_RECORD_KEYS = frozenset(
    {
        "record",
        "baseline",
        "observation",
        "allocation",
        "expected_tty_nr",
        "encoding",
        "binding",
        "cid",
        "namespace",
        "phase",
        "identity",
    }
)
AF_ATTACH_ENCODING = "linux-proc-new-encode-dev-v1"
AF_ATTACH_PHASE = "attach-bound"
# the binding record's closed schema literal (module-level
# alias: the attach consumer's parameter is named after the
# binding and must never shadow the module access)
BINDING_RECORD_SCHEMA = binding.BINDING_RECORD_SCHEMA
_BINDING_RECORD_KEYS = frozenset(
    {
        "record",
        "order_id",
        "order_path",
        "order_sha256",
        "active_sha256",
        "source_head",
        "repo_identity",
        "run_id",
    }
)


def _validate_binding_record(value: object) -> dict:
    """The FULL closed key/type/hash grammar of a supplied
    binding record (the same law the outer native-run
    consumer applies): the exact key set, the closed schema
    literal, the OAP order id, the non-empty order path, the
    two sha256 digests, the literal 40-hex source head, the
    non-empty repository identity and the 32-hex run id.
    A public pure consumer never assumes a caller has
    already validated its input; accepting retained data is
    DATA validation only — never a measured run authority."""
    if not isinstance(value, dict) or set(value) != _BINDING_RECORD_KEYS:
        raise FixtureError("prep-attach-binding-malformed")
    if (
        value.get("record") != BINDING_RECORD_SCHEMA
        or not isinstance(value.get("order_id"), str)
        or re.fullmatch(r"^[0-9]{3}-[a-z]{1,2}$", value["order_id"]) is None
        or not isinstance(value.get("order_path"), str)
        or not value["order_path"]
        or not isinstance(value.get("order_sha256"), str)
        or _SHA_RE.fullmatch(value["order_sha256"]) is None
        or not isinstance(value.get("active_sha256"), str)
        or _SHA_RE.fullmatch(value["active_sha256"]) is None
        or not isinstance(value.get("source_head"), str)
        or _HEAD_RE.fullmatch(value["source_head"]) is None
        or not isinstance(value.get("repo_identity"), str)
        or not value["repo_identity"]
        or not isinstance(value.get("run_id"), str)
        or _RUN_ID_RE.fullmatch(value["run_id"]) is None
    ):
        raise FixtureError("prep-attach-binding-malformed")
    return value


def attach_binding_record(
    *,
    baseline: DevptsObservation,
    observation: DevptsObservation,
    allocation: DevptsAllocation,
    binding: OrderRunBinding,
    identity: dict,
    cid: str,
) -> dict[str, object]:
    """The producer of the DISTINCT identity-bearing AF
    attach-binding record (017-ae software): the two closed
    inventory records (embedded EXACTLY as measured — the
    producer re-parses both and refuses a non-closed record),
    the allocation INDEPENDENTLY RE-DERIVED from the two
    inventories and required to equal the supplied one field
    by field (a caller-asserted allocation is never trusted),
    the derived expected tty_nr re-checked, the workflow's
    OWN immutable binding (``to_record``, never caller
    strings), the owner's MEASURED CID (64-hex), the measured
    namespace, the closed phase/encoding literals, and the
    owner's frozen identity substructure (closed-validated
    through the production codec — never caller-authored).
    A malformed or contradictory fact emits no record; the
    produced record must round-trip the closed consumer
    before it is returned."""
    if not isinstance(baseline, DevptsObservation) or not isinstance(
        observation, DevptsObservation
    ):
        raise FixtureError("prep-devpts-record-malformed")
    if not isinstance(allocation, DevptsAllocation):
        raise FixtureError("prep-devpts-allocation-malformed")
    if not isinstance(binding, OrderRunBinding):
        raise FixtureError("prep-devpts-binding-invalid")
    if not isinstance(cid, str) or _CID_RE.fullmatch(cid) is None:
        raise FixtureError("prep-devpts-cid-invalid")
    identity_law = _ad_identity_substructure_law(identity)
    if identity_law is None:
        raise FixtureError("prep-devpts-identity-invalid")
    # the DISTINCT record tag of the binding's OWN canonical
    # entry (the AF tag is AF-only, the AH tag AH-only and the
    # AJ tag AJ-only, even for equal-numeric identities): any
    # other entry's binding can never mint an attach-binding
    # record
    if binding.order_id == rprofile.AF_ORDER_ID:
        record_tag = AF_ATTACH_BINDING_SCHEMA
    elif binding.order_id == rprofile.AH_ORDER_ID:
        record_tag = AH_ATTACH_BINDING_SCHEMA
    elif binding.order_id == rprofile.AJ_ORDER_ID:
        record_tag = AJ_ATTACH_BINDING_SCHEMA
    else:
        raise FixtureError("prep-devpts-binding-invalid")
    rederived = derive_attach_allocation(
        baseline.inventory, observation.inventory, subject_uid=identity_law[0]
    )
    if rederived != allocation:
        raise FixtureError("prep-devpts-allocation-mismatch")
    if not expected_tty_nr_qualifies(allocation.expected_tty_nr):
        raise FixtureError("prep-devpts-encoding-unrepresentable")

    def _embed(obs: DevptsObservation) -> dict[str, object]:
        # The retained record is re-parsed through the closed
        # consumer and required to agree with its typed
        # inventory (a caller-built DevptsObservation is
        # ordinary data — never embedded by faith)
        reobs = parse_devpts_inventory_record(obs.record)
        if reobs.inventory != obs.inventory:
            raise FixtureError("prep-devpts-record-malformed")
        body = reobs.record[:-1] if reobs.record.endswith(b"\n") else reobs.record
        return json.loads(body.decode("ascii"))

    record: dict[str, object] = {
        "record": record_tag,
        "baseline": _embed(baseline),
        "observation": _embed(observation),
        "allocation": {
            "name": allocation.name,
            "major": allocation.major,
            "minor": allocation.minor,
            "inode": allocation.inode,
            "mode": allocation.mode,
            "uid": allocation.uid,
            "gid": allocation.gid,
        },
        "expected_tty_nr": allocation.expected_tty_nr,
        "encoding": AF_ATTACH_ENCODING,
        "binding": binding.to_record(),
        "cid": cid,
        "namespace": list(observation.inventory.namespace),
        "phase": AF_ATTACH_PHASE,
        "identity": identity,
    }
    # producer/consumer agreement: the produced record must
    # pass the closed consumer validation before it is
    # returned — a drift between the two is a refusal, never
    # a silently shipped record
    parse_attach_binding_record(record, binding)
    return record


def parse_attach_binding_record(record: object, binding: object) -> DevptsAllocation:
    """The closed consumer of the attach-binding record:
    the exact closed key set, the distinct tag, the closed
    phase/encoding literals, the workflow's OWN immutable
    binding EXACTLY — an ``OrderRunBinding`` object is
    compared through its own closed ``to_record``, or a
    supplied binding record dict is FIRST validated by the
    full closed key/type/hash grammar of this public pure
    consumer (never assumed caller-validated) and then
    compared by exact equality — a foreign or
    contradicted binding is a refusal — the
    exact tag-pair law (each tag is the record of ITS OWN
    canonical entry ONLY: the AF tag with the AF order at its
    canonical path, the AH tag with the AH order at its
    canonical path — the AF tag stays AF-only and the AH tag
    AH-only, even for equal-numeric identities), the owner's
    frozen identity substructure (production-codec
    closed-validated),
    the 64-hex CID, the closed namespace, and the two
    embedded inventory records validated DIRECTLY by the
    closed inventory consumer (each must carry the record's
    namespace); the allocation is INDEPENDENTLY RE-DERIVED
    from the two inventories through the frozen subject uid
    and compared field by field (a retained allocation is
    re-derived, never trusted), and the expected tty_nr re-
    checked.  Returns the re-derived allocation; anything
    else is a closed non-echoing refusal."""
    if not isinstance(record, dict) or set(record) != AF_ATTACH_RECORD_KEYS:
        raise FixtureError("prep-attach-binding-malformed")
    if (
        record.get("record")
        not in (AF_ATTACH_BINDING_SCHEMA, AH_ATTACH_BINDING_SCHEMA, AJ_ATTACH_BINDING_SCHEMA)
        or record.get("phase") != AF_ATTACH_PHASE
        or record.get("encoding") != AF_ATTACH_ENCODING
    ):
        raise FixtureError("prep-attach-binding-malformed")
    if isinstance(binding, OrderRunBinding):
        outer = binding.to_record()
    elif isinstance(binding, dict):
        # a supplied binding dict is validated by the FULL
        # closed key/type/hash grammar here — this public
        # pure consumer never assumes the caller has already
        # validated it
        outer = _validate_binding_record(binding)
    else:
        raise FixtureError("prep-attach-binding-malformed")
    if (
        not isinstance(outer, dict)
        or outer.get("record") != BINDING_RECORD_SCHEMA
        or record.get("binding") != outer
    ):
        raise FixtureError("prep-attach-binding-mismatch")
    # the EXACT tag-pair law: each attach-binding tag is the
    # record of ITS OWN canonical entry ONLY (the AF tag is
    # AF-only, the AH tag AH-only and the AJ tag AJ-only, even
    # for equal-numeric identities)
    expected_order, expected_path = {
        AF_ATTACH_BINDING_SCHEMA: (rprofile.AF_ORDER_ID, rprofile.AF_ORDER_PATH),
        AH_ATTACH_BINDING_SCHEMA: (rprofile.AH_ORDER_ID, rprofile.AH_ORDER_PATH),
        AJ_ATTACH_BINDING_SCHEMA: (rprofile.AJ_ORDER_ID, rprofile.AJ_ORDER_PATH),
    }[record["record"]]
    if outer.get("order_id") != expected_order or outer.get("order_path") != expected_path:
        raise FixtureError("prep-attach-binding-mismatch")
    identity_law = _ad_identity_substructure_law(record.get("identity"))
    if identity_law is None:
        raise FixtureError("prep-attach-binding-malformed")
    cid = record.get("cid")
    if not isinstance(cid, str) or _CID_RE.fullmatch(cid) is None:
        raise FixtureError("prep-attach-binding-malformed")
    namespace = record.get("namespace")
    if (
        not isinstance(namespace, list)
        or len(namespace) != 2
        or any(isinstance(v, bool) or not isinstance(v, int) or v < 0 for v in namespace)
    ):
        raise FixtureError("prep-attach-binding-malformed")
    observations: dict[str, DevptsInventory] = {}
    for key in ("baseline", "observation"):
        embedded = record.get(key)
        if not isinstance(embedded, dict):
            raise FixtureError("prep-attach-binding-malformed")
        # the embedded inventory is validated DIRECTLY
        # against the shared closed object-level grammar
        # (no re-serialization: a huge or non-closed caller
        # mapping is refused before any copy)
        try:
            inv = _parse_devpts_inventory_object(embedded)
        except FixtureError:
            raise FixtureError("prep-attach-binding-malformed") from None
        if list(inv.namespace) != namespace:
            raise FixtureError("prep-attach-binding-mismatch")
        observations[key] = inv
    allocation_raw = record.get("allocation")
    if (
        not isinstance(allocation_raw, dict)
        or set(allocation_raw) != _ATTACH_ALLOCATION_KEYS
        or any(
            isinstance(allocation_raw[k], bool) or not isinstance(allocation_raw[k], int)
            for k in _ATTACH_ALLOCATION_KEYS
        )
    ):
        raise FixtureError("prep-attach-binding-malformed")
    try:
        rederived = derive_attach_allocation(
            observations["baseline"],
            observations["observation"],
            subject_uid=identity_law[0],
        )
    except FixtureError:
        raise FixtureError("prep-attach-binding-mismatch") from None
    rederived_raw = {
        "name": rederived.name,
        "major": rederived.major,
        "minor": rederived.minor,
        "inode": rederived.inode,
        "mode": rederived.mode,
        "uid": rederived.uid,
        "gid": rederived.gid,
    }
    if allocation_raw != rederived_raw:
        raise FixtureError("prep-attach-binding-mismatch")
    expected = record.get("expected_tty_nr")
    if (
        isinstance(expected, bool)
        or not isinstance(expected, int)
        or expected != rederived.expected_tty_nr
        or not expected_tty_nr_qualifies(expected)
    ):
        raise FixtureError("prep-attach-binding-malformed")
    return rederived


def parse_format_capture_record(record: object, binding: object) -> dict:
    """The closed consumer of the AJ selected native
    format-capture record: the exact closed key set, the
    AJ-only tag, the workflow's OWN immutable binding EXACTLY
    (an ``OrderRunBinding`` object is compared through its own
    closed ``to_record``, or a supplied binding record dict is
    FIRST validated by the full closed key/type/hash grammar of
    this public pure consumer (never assumed caller-validated)
    and then compared by exact equality — a foreign or
    contradicted binding is a refusal), the exact tag-pair law
    (the AJ format-capture tag is the record of the AJ
    canonical entry ONLY — never AF/AH or any other order, even
    for equal-numeric identities), the owner's frozen identity
    substructure (production-codec closed-validated), the
    64-hex CID, and the nested selected format snapshot
    RE-VALIDATED by the DISTINCT closed format-snapshot law
    dispatched on the snapshot's own record tag (strict full
    snapshot: the strict pinned wrapper re-parse, the immutable
    seed identity, the closed chains and issued-identity law;
    safe partial snapshot: only verified selected frames and
    explicit not-qualified; every other tag refused — a copied
    or replayed snapshot never mints authority).  The WHOLE record
    is then bounded at the 256 KiB TOTAL SERIALIZED
    selected-capture bound: the nested snapshot's own bound is
    necessary but is NOT the total — the outer tag, the
    workflow's immutable binding, the frozen identity and the
    measured CID are part of the captured record and are
    bounded here at the consumer seam (the producer and the
    integrated export apply the same total at their own
    seams).  Returns the validated snapshot; anything else is a
    closed non-echoing refusal."""
    if not isinstance(record, dict) or set(record) != _FORMAT_CAPTURE_RECORD_KEYS:
        raise FixtureError("prep-format-capture-malformed")
    if record.get("record") != AJ_FORMAT_CAPTURE_SCHEMA:
        raise FixtureError("prep-format-capture-malformed")
    if isinstance(binding, OrderRunBinding):
        # bounded pre-hash handling of the typed object's raw
        # active bytes: the resolver's own active-read cap is
        # the closed bound of this field; an over-bound or
        # non-bytes value is refused BEFORE any hashing work
        raw_active = binding.active_bytes
        if not isinstance(raw_active, (bytes, bytearray)) or len(raw_active) > _ACTIVE_BYTES_MAX:
            raise FixtureError("prep-format-capture-malformed")
        try:
            # the typed representation is held to the SAME
            # closed binding-record grammar as a supplied
            # dict: the dataclass carries no __post_init__
            # validation, so a directly constructed value with
            # a malformed head/hash/run id is refused — the
            # to_record output is never trusted, and the active
            # bytes are hashed only after the bounded field
            # checks above
            outer = _validate_binding_record(binding.to_record())
        except (FixtureError, ValueError, TypeError):
            raise FixtureError("prep-format-capture-malformed") from None
    elif isinstance(binding, dict):
        # a supplied binding dict is validated by the FULL
        # closed key/type/hash grammar here — this public
        # pure consumer never assumes the caller has already
        # validated it
        outer = _validate_binding_record(binding)
    else:
        raise FixtureError("prep-format-capture-malformed")
    if (
        not isinstance(outer, dict)
        or outer.get("record") != BINDING_RECORD_SCHEMA
        or record.get("binding") != outer
    ):
        raise FixtureError("prep-format-capture-mismatch")
    # the EXACT tag-pair law: the AJ format-capture tag is the
    # record of the AJ canonical entry ONLY (never AF/AH or any
    # other order, even for equal-numeric identities)
    if (
        outer.get("order_id") != rprofile.AJ_ORDER_ID
        or outer.get("order_path") != rprofile.AJ_ORDER_PATH
    ):
        raise FixtureError("prep-format-capture-mismatch")
    identity_law = _ad_identity_substructure_law(record.get("identity"))
    if identity_law is None:
        raise FixtureError("prep-format-capture-malformed")
    cid = record.get("cid")
    if not isinstance(cid, str) or _CID_RE.fullmatch(cid) is None:
        raise FixtureError("prep-format-capture-malformed")
    snapshot = record.get("snapshot")
    if not isinstance(snapshot, dict):
        raise FixtureError("prep-format-capture-malformed")
    # strict DISTINCT dispatch on the nested snapshot's own
    # record tag: the strict full snapshot passes the closed
    # four-case validator; the safe PARTIAL snapshot (only
    # verified selected frames, qualification explicitly
    # not-qualified) passes the DISTINCT partial validator;
    # every other tag — including untagged or legacy tags — is
    # a closed refusal.  The two validators are never widened
    # into one another.
    nested_tag = snapshot.get("record")
    if nested_tag == fmodel.SCHEMA_FORMAT_SNAPSHOT:
        _validate_nested = fmodel.validate_format_snapshot_record
    elif nested_tag == fmodel.SCHEMA_FORMAT_SNAPSHOT_PARTIAL:
        _validate_nested = fmodel.validate_format_snapshot_record_partial
    else:
        _validate_nested = None
    try:
        if _validate_nested is None:
            raise fmodel.FixtureError("format-snapshot-tag")
        _validate_nested(snapshot)
    # the model validator raises ITS OWN closed error class
    # (model.FixtureError, a ValueError) — DISTINCT from this
    # module's FixtureError alias (ci.FixtureError, a
    # RuntimeError): catching only this alias would let a
    # malformed nested snapshot escape the promised prep
    # refusal token and the native-run consumer conversion
    except fmodel.FixtureError:
        raise FixtureError("prep-format-capture-malformed") from None
    # the 256 KiB TOTAL SERIALIZED selected capture bound: the
    # WHOLE record — outer tag, the workflow's immutable
    # binding, the frozen owner-identity substructure, the
    # measured 64-hex CID and the nested snapshot — serialized
    # canonically.  The nested snapshot's own bound is
    # necessary but is NOT the total: the outer identity
    # metadata is part of the selected capture and is bounded
    # here at the consumer seam.
    if len(fmodel.canonical_bytes(record)) > fmodel.FORMAT_SNAPSHOT_MAX_BYTES:
        raise FixtureError("prep-format-capture-bound")
    return snapshot


# -- native-owner producer (explicit versioned scope) ------------------------------
# The historical 017-s schema remains the S rehearsal record
# and is NEVER relabeled as native evidence.  A native-owner
# run uses its OWN explicit versioned producer/schema below;
# deriving the limited S subset never makes the two scopes
# compatible.
NATIVE_OWNER_SCHEMA = "slaif-native-owner-evidence-v1"
NATIVE_OWNER_PRODUCER = "native-owner"
# The DISTINCT identity-bearing native-owner evidence tag of
# the future 017-ad native handoff (INERT in this round): the
# SAME closed native-scope measured facts as the original tag
# PLUS the frozen owner-identity substructure the real owner
# collected and derived (never caller-authored).  The original
# tag keeps its exact historical key set and refuses any
# identity key — the two tags are separate closed records,
# never a widened grammar.
AD_NATIVE_OWNER_SCHEMA = "slaif-017ad-native-owner-evidence-v1"
# The DISTINCT identity-bearing native-owner evidence tag of
# the canonical FUTURE 017-af entry (INERT in 017-ae:
# software only): the SAME closed native-scope measured facts
# as the AD tag PLUS the frozen owner-identity substructure
# (the identical owner-UID identity law).  The original tag
# keeps its exact historical key set and refuses BOTH the
# identity key and any 017-ad / 017-af binding — separate
# closed records per entry, never a widened grammar,
# including for equal-numeric identities.
AF_NATIVE_OWNER_SCHEMA = "slaif-017af-native-owner-evidence-v1"
# The DISTINCT identity-bearing native-owner evidence tag of
# the canonical FUTURE 017-ah entry (INERT in 017-ag:
# software only): the SAME closed native-scope measured facts
# as the AD/AF tags PLUS the frozen owner-identity
# substructure (the identical owner-UID identity law).  The
# original tag keeps its exact historical key set and refuses
# the identity key and every identity-bearing entry —
# separate closed records per entry, never a widened
# grammar, including for equal-numeric identities.
AH_NATIVE_OWNER_SCHEMA = "slaif-017ah-native-owner-evidence-v1"
# The DISTINCT identity-bearing native-owner evidence tag of
# the canonical FUTURE 017-aj entry (INERT in 017-ai:
# software only): the SAME closed native-scope measured facts
# as the AD/AF/AH tags PLUS the frozen owner-identity
# substructure (the identical owner-UID identity law).  The
# original tag keeps its exact historical key set and refuses
# the identity key and every identity-bearing entry —
# separate closed records per entry, never a widened
# grammar, including for equal-numeric identities.
AJ_NATIVE_OWNER_SCHEMA = "slaif-017aj-native-owner-evidence-v1"
# The DISTINCT identity-bearing attach-binding record tag of
# the AF entry's native attach-binding phase (the measured
# fixture-namespace devpts baseline, the second bounded
# observation, the unique fresh owned allocation and the
# independently derived expected proc tty_nr).  The record is
# bound to the AF entry's exact order in its own tag-pair law;
# the attach-binding facts live in this distinct honest
# version, never widened into an old consumer.
AF_ATTACH_BINDING_SCHEMA = rprofile.AF_NATIVE_ATTACH_BINDING_SCHEMA
# The DISTINCT identity-bearing attach-binding record tag of
# the canonical FUTURE 017-ah entry (INERT in 017-ag): the
# SAME closed structural core as the AF record under the AH
# entry's own tag-pair law (the AF tag remains AF-only, even
# for equal-numeric identities).
AH_ATTACH_BINDING_SCHEMA = rprofile.AH_NATIVE_ATTACH_BINDING_SCHEMA
# The DISTINCT identity-bearing attach-binding record tag of
# the canonical FUTURE 017-aj entry (INERT in 017-ai): the
# SAME closed structural core as the AF record under the AJ
# entry's own tag-pair law (the AH tag remains AH-only, even
# for equal-numeric identities).
AJ_ATTACH_BINDING_SCHEMA = rprofile.AJ_NATIVE_ATTACH_BINDING_SCHEMA
# The DISTINCT identity-bearing selected native format-capture
# record tag of the canonical FUTURE 017-aj entry (INERT in
# 017-ai: software only): the closed selected-format snapshot
# bound to the AJ entry's exact order in its own tag-pair law,
# with the owner's frozen identity substructure and the
# measured CID.  The format facts live in this distinct honest
# version, never widened into an old consumer.
AJ_FORMAT_CAPTURE_SCHEMA = rprofile.AJ_NATIVE_FORMAT_CAPTURE_SCHEMA
_FORMAT_CAPTURE_RECORD_KEYS = frozenset({"record", "binding", "identity", "cid", "snapshot"})
# the CLOSED native-owner record grammar: the exact top-level
# key set and the exact nested object key sets.  Anything else
# (unknown, missing, or non-mapping nested keys) is a closed
# non-echoing refusal.
_NATIVE_OWNER_TOP_KEYS = frozenset(
    {
        "record",
        "producer",
        "status",
        "order",
        "source_head",
        "run_id",
        "prepared",
        "image",
        "artifact",
        "export",
        "teardown",
        "native_started",
        "native_ready",
    }
)
_NATIVE_OWNER_NESTED_KEYS = (
    ("prepared", frozenset({"cid"})),
    ("image", frozenset({"image_id"})),
    ("artifact", frozenset({"binary_sha256"})),
    ("export", frozenset({"bytes", "sha256"})),
    (
        "teardown",
        frozenset(
            {
                "container_present_before",
                "container_removal",
                "image_removal",
                "descendants_after",
                "sentinel_survived",
            }
        ),
    ),
)


@dataclass(frozen=True)
class NativeOwnerFacts:
    """Typed final facts of a NATIVE-OWNER run (its own
    versioned producer/scope): full owner/export/payload/
    digest/teardown validation, and the order/source/run/CID/
    image context every later receipt must equal.  The
    executable identity (``binary_sha256``) is the measured
    half of the immutable image binding: the later subject's
    MEASURED exe identity must match it."""

    # the frozen owner-identity substructure of the DISTINCT
    # 017-ad identity-bearing record (closed data integrity —
    # never a measured-authority claim); None for the original
    # tag, which carries no identity key at all
    identity: tuple[int, int, tuple[int, ...]] | None

    schema: str
    producer: str
    status: str
    order: str
    source_head: str
    run_id: str
    cid: str
    # the immutable image id, NORMALIZED to the bare digest
    # (the record may carry the actual measured
    # sha256:<digest> form)
    image_id: str
    binary_sha256: str
    export_sha256: str
    export_bytes: int
    teardown_verified: bool
    sentinel_survived: bool
    descendants_after: int
    native_started: bool
    native_ready: bool


def _ad_identity_substructure_law(
    identity: object,
) -> tuple[int, int, tuple[int, ...]] | None:
    """The closed structural law of the 017-ad record's frozen
    owner-identity substructure: the exact six keys, the
    canonical owner-UID profile name, strict nonroot finite
    Linux IDs distinct from the controller, the one-element
    primary-GID group vector, and the 64-hex canonical
    fingerprint and profile-DATA digest — with the production
    codec re-deriving the canonical record from the retained
    IDs (controller fixed 21001/21001) and BOTH digests
    verified against it.  Returns the frozen ``(uid, gid,
    groups)`` or None (the public consumer keeps its own fixed
    refusal token).  This is closed data integrity — never a
    measured-authority claim (a caller-authored valid
    substructure is still only data)."""
    if not isinstance(identity, dict) or set(identity) != {
        "profile",
        "fingerprint",
        "subject_uid",
        "subject_gid",
        "subject_groups",
        "profile_data_sha256",
    }:
        return None
    profile = identity["profile"]
    fingerprint = identity["fingerprint"]
    subject_uid = identity["subject_uid"]
    subject_gid = identity["subject_gid"]
    subject_groups = identity["subject_groups"]
    profile_data_sha256 = identity["profile_data_sha256"]
    if (
        profile != fidentity.PROFILE_OWNER_UID
        or not isinstance(fingerprint, str)
        or re.fullmatch(r"[0-9a-f]{64}", fingerprint) is None
        or isinstance(subject_uid, bool)
        or not isinstance(subject_uid, int)
        or isinstance(subject_gid, bool)
        or not isinstance(subject_gid, int)
        or not (fidentity.LINUX_ID_MIN <= subject_uid <= fidentity.LINUX_ID_MAX)
        or not (fidentity.LINUX_ID_MIN <= subject_gid <= fidentity.LINUX_ID_MAX)
        or not isinstance(subject_groups, list)
        or len(subject_groups) != 1
        or isinstance(subject_groups[0], bool)
        or not isinstance(subject_groups[0], int)
        or subject_groups[0] != subject_gid
        or not isinstance(profile_data_sha256, str)
        or re.fullmatch(r"[0-9a-f]{64}", profile_data_sha256) is None
    ):
        return None
    try:
        description = fidentity.FixtureIdentityDescription(
            profile=profile,
            controller_uid=fidentity.CONTROLLER_UID,
            controller_gid=fidentity.CONTROLLER_GID,
            subject_uid=subject_uid,
            subject_gid=subject_gid,
            subject_groups=(subject_gid,),
        )
    except fidentity.FixtureIdentityError:
        return None
    if (
        fidentity.fingerprint_description(description) != fingerprint
        or hashlib.sha256(fidentity.encode_description(description)).hexdigest()
        != profile_data_sha256
    ):
        return None
    return (subject_uid, subject_gid, (subject_gid,))


def _ad_identity_substructure_from_triple(
    identity: tuple[int, int, tuple[int, ...]],
) -> dict[str, object]:
    """The DISTINCT 017-ad identity-bearing record's frozen
    owner-identity substructure DERIVED from the workflow's
    frozen subject triple through the production codec: the
    canonical owner-UID profile name (the controller identity
    fixed 21001/21001), the canonical description fingerprint
    and the profile-DATA sha256.  The description is fully
    determined by the closed triple, so this derivation is
    deterministic — the retained substructure re-derives to
    the identical canonical record and digests (closed data
    integrity, never a measured-authority claim)."""
    uid, gid, groups = _validate_frozen_subject_identity(identity)
    description = fidentity.FixtureIdentityDescription(
        profile=fidentity.PROFILE_OWNER_UID,
        controller_uid=fidentity.CONTROLLER_UID,
        controller_gid=fidentity.CONTROLLER_GID,
        subject_uid=uid,
        subject_gid=gid,
        subject_groups=(gid,),
    )
    return {
        "profile": fidentity.PROFILE_OWNER_UID,
        "fingerprint": fidentity.fingerprint_description(description),
        "subject_uid": uid,
        "subject_gid": gid,
        "subject_groups": [gid],
        "profile_data_sha256": hashlib.sha256(
            fidentity.encode_description(description)
        ).hexdigest(),
    }


def parse_native_owner_facts(record: object) -> NativeOwnerFacts:
    """Parse a NATIVE-OWNER evidence record into typed final
    facts.  Closed versioned schema, explicit producer,
    strict types throughout: the order (OAP id), literal
    source head, run id, exact CID, the immutable image id
    (either closed form: the bare digest or the actual
    measured ``sha256:<digest>`` form — the typed fact is
    the NORMALIZED bare digest), pinned binary sha, the
    exported payload size and digest, and the verified
    teardown (positive-before / negative-after on the exact
    CID and image, zero descendants, sentinel survival).
    ``native_started`` must be True — a run that never
    started native is not this producer's scope (it would
    be the historical S scope).  A malformed, drifted,
    foreign-scope or non-pass record is a closed non-echoing
    refusal."""
    # The DISTINCT closed tag law (017-ad): the original tag
    # keeps its exact historical key set (no identity key);
    # the identity-bearing 017-ad tag carries the SAME closed
    # native-scope facts PLUS the frozen owner-identity
    # substructure, and is the record of the canonical 017-ad
    # entry ONLY (an AD-tagged record of any other order id is
    # a closed refusal — the original tag is never widened).
    tag = record.get("record") if isinstance(record, Mapping) else None
    if tag not in (
        NATIVE_OWNER_SCHEMA,
        AD_NATIVE_OWNER_SCHEMA,
        AF_NATIVE_OWNER_SCHEMA,
        AH_NATIVE_OWNER_SCHEMA,
        AJ_NATIVE_OWNER_SCHEMA,
    ):
        raise FixtureError("prep-native-owner-record-malformed")
    expected_keys = (
        _NATIVE_OWNER_TOP_KEYS | {"identity"}
        if tag
        in (
            AD_NATIVE_OWNER_SCHEMA,
            AF_NATIVE_OWNER_SCHEMA,
            AH_NATIVE_OWNER_SCHEMA,
            AJ_NATIVE_OWNER_SCHEMA,
        )
        else _NATIVE_OWNER_TOP_KEYS
    )
    if not isinstance(record, Mapping):
        raise FixtureError("prep-native-owner-record-malformed")
    if record.get("producer") != NATIVE_OWNER_PRODUCER:
        raise FixtureError("prep-native-owner-record-malformed")
    # the CLOSED key sets (top level and nested objects):
    # unknown or missing fields are a closed non-echoing
    # refusal before anything is used — a value is never
    # retained or echoed
    if set(record) != expected_keys:
        raise FixtureError("prep-native-owner-record-malformed")
    for key, keys in _NATIVE_OWNER_NESTED_KEYS:
        nested = record[key]
        if not isinstance(nested, Mapping) or set(nested) != keys:
            raise FixtureError("prep-native-owner-record-malformed")
    try:
        status = record["status"]
        order = record["order"]
        source_head = record["source_head"]
        run_id = record["run_id"]
        cid = record["prepared"]["cid"]
        image_id = record["image"]["image_id"]
        binary_sha = record["artifact"]["binary_sha256"]
        export_bytes = record["export"]["bytes"]
        export_sha = record["export"]["sha256"]
        container_present_before = record["teardown"]["container_present_before"]
        container_removal = record["teardown"]["container_removal"]
        image_removal = record["teardown"]["image_removal"]
        descendants_after = record["teardown"]["descendants_after"]
        sentinel_survived = record["teardown"]["sentinel_survived"]
        native_started = record["native_started"]
        native_ready = record["native_ready"]
        identity_raw = record.get("identity")
    except (KeyError, TypeError):
        raise FixtureError("prep-native-owner-record-malformed") from None
    # the frozen owner-identity substructure: closed data
    # integrity via the production codec (re-derived canonical
    # record, both digests verified) — the identity-bearing
    # AD / AF / AH records only
    identity = None
    if tag in (
        AD_NATIVE_OWNER_SCHEMA,
        AF_NATIVE_OWNER_SCHEMA,
        AH_NATIVE_OWNER_SCHEMA,
        AJ_NATIVE_OWNER_SCHEMA,
    ):
        identity = _ad_identity_substructure_law(identity_raw)
        if identity is None:
            raise FixtureError("prep-native-owner-record-malformed")
    if (
        status != "pass"
        or not isinstance(order, str)
        or not re.fullmatch(r"^[0-9]{3}-[a-z]{1,2}$", order)
        or (tag == AD_NATIVE_OWNER_SCHEMA and order != rprofile.AD_ORDER_ID)
        or (tag == AF_NATIVE_OWNER_SCHEMA and order != rprofile.AF_ORDER_ID)
        or (tag == AH_NATIVE_OWNER_SCHEMA and order != rprofile.AH_ORDER_ID)
        or (tag == AJ_NATIVE_OWNER_SCHEMA and order != rprofile.AJ_ORDER_ID)
        # the EXACT tag-pair law: the original tag carries the
        # historical (non-AD) entries ONLY — the canonical
        # 017-ad / 017-af / 017-ah / 017-aj entries are
        # representable by their DISTINCT identity-bearing
        # tags alone, so an original-tag record of any of them
        # is a closed refusal (the historical orders of the
        # original tag are unchanged)
        or (
            tag == NATIVE_OWNER_SCHEMA
            and order
            in (
                rprofile.AD_ORDER_ID,
                rprofile.AF_ORDER_ID,
                rprofile.AH_ORDER_ID,
                rprofile.AJ_ORDER_ID,
            )
        )
        or not isinstance(source_head, str)
        or _HEAD_RE.fullmatch(source_head) is None
        or not isinstance(run_id, str)
        or _RUN_ID_RE.fullmatch(run_id) is None
        or not isinstance(cid, str)
        or _CID_RE.fullmatch(cid) is None
        or not isinstance(image_id, str)
        or _IMAGE_ID_RE.fullmatch(image_id) is None
        or not isinstance(binary_sha, str)
        or _SHA_RE.fullmatch(binary_sha) is None
        or not isinstance(export_bytes, int)
        or isinstance(export_bytes, bool)
        or export_bytes <= 0
        or not isinstance(export_sha, str)
        or _SHA_RE.fullmatch(export_sha) is None
        or container_present_before is not True
        or container_removal != "absent-verified"
        or image_removal != "absent-verified"
        or not isinstance(descendants_after, int)
        or isinstance(descendants_after, bool)
        or descendants_after != 0
        or sentinel_survived is not True
        or native_started is not True
        or not isinstance(native_ready, bool)
    ):
        raise FixtureError("prep-native-owner-record-malformed")
    return NativeOwnerFacts(
        identity=identity,
        schema=tag,
        producer=NATIVE_OWNER_PRODUCER,
        status=status,
        order=order,
        source_head=source_head,
        run_id=run_id,
        cid=cid,
        image_id=_normalize_image_id(image_id),
        binary_sha256=binary_sha,
        export_sha256=export_sha,
        export_bytes=export_bytes,
        teardown_verified=True,
        sentinel_survived=sentinel_survived,
        descendants_after=descendants_after,
        native_started=native_started,
        native_ready=native_ready,
    )


# -- native-owner producer (the measurement-to-record boundary) -------------------


class NativeOwnerMeasurement(Protocol):
    """The bounded READ-ONLY measurement path of the
    completed owner's OWN finish/export/teardown.  The later,
    separately activated native flow implements this against
    the actual container state; T exercises it only with
    fakes (the real backend is never invoked here).  Every
    method is a MEASUREMENT, never a claim: None means
    unmeasured/unreadable and is a closed refusal at the
    producer, never a filled-in default."""

    def export_payload(self) -> bytes | None:
        """The exact exported payload bytes (bounded read),
        or None when unmeasured."""

    def container_present_before(self) -> bool | None:
        """Whether the exact CID was present before teardown
        was attempted, or None when unmeasured."""

    def container_absent_after(self) -> bool | None:
        """Whether the exact CID is verified ABSENT after
        teardown, or None when unmeasured."""

    def image_absent_after(self) -> bool | None:
        """Whether the immutable image is verified ABSENT
        after teardown, or None when unmeasured."""

    def descendants_after(self) -> int | None:
        """The measured descendant count after teardown, or
        None when unmeasured."""

    def sentinel_survived(self) -> bool | None:
        """Whether the sentinel survived teardown, or None
        when unmeasured."""

    def native_started(self) -> bool | None:
        """Whether native actually started for this run, or
        None when unmeasured."""

    def native_ready(self) -> bool | None:
        """The run's own native-ready fact, or None when
        unmeasured."""


_SEAM_METHODS = (
    "export_payload",
    "container_present_before",
    "container_absent_after",
    "image_absent_after",
    "descendants_after",
    "sentinel_survived",
    "native_started",
    "native_ready",
)

# The closed resource-binding context a measurement may
# expose: the resources the measured teardown actually
# belonged to, derived from the measured owner state.  A
# measurement that exposes this attribute must bind it
# EXACTLY to the producer's expected immutable order/run
# binding; a measurement without the attribute is opaque
# (the bare record-boundary law only).
_MEASURED_CONTEXT_KEYS = frozenset(
    {"order", "source_head", "run_id", "cid", "image_id", "binary_sha256"}
)


class CompletedOwnerState(Protocol):
    """The read-only measured state of a COMPLETED fixture
    owner, exactly as recorded by its own finish/export/
    teardown path.  The real implementation is the
    reviewed R/S ``LocalFixtureOwner``; the attribute set
    is the closed seam the adapter reads — nothing else is
    observed, and no platform operation is re-invoked."""

    export_payload: bytes | None
    descendants_before: int
    teardown_container_absent: bool | None
    image_removed: bool
    teardown_descendants_after: int | None
    sentinel_survived: bool
    target_cid: str | None
    image_id: str | None
    run_id: str
    optin: Mapping[str, str]
    artifact: dict[str, object] | None


class OwnedOwnerMeasurement:
    """The REAL owned finish/export/teardown measurement
    adapter (order 017-t, section 3): the concrete
    implementation of the producer's measurement seam over
    a COMPLETED fixture owner.  It performs NO mutation
    and NO new platform call: every value is a read of
    state the owner's own finish/export/teardown path
    already measured and verified — the bounded retained
    export bytes, the positive-before descendant count,
    the verified absent-after facts on the exact CID and
    image, sentinel survival — and the run's OWN native
    facts are derived from the PUBLIC workflow's measured
    subject receipt (the pre-teardown identity the
    collectors actually measured; a caller flag write
    never mints them: a run with no measured subject
    receipt has no measured native start, and the
    historical S scope therefore can never mint this
    record).  ``measured_context`` is derived from the
    owner's OWN order/run/head/CID/image/binary
    registration — never from a caller — and is None
    when any component is unmeasured, which the producer
    refuses.  T exercises this adapter with a fake
    completed owner state (the backend operations are
    faked); the real backend is never invoked in this
    round."""

    def __init__(
        self,
        owner: CompletedOwnerState,
        subject: SubjectIdentity | None = None,
    ) -> None:
        self._owner = owner
        # The PUBLIC workflow's retained pre-teardown
        # subject identity (the collectors' measured
        # output) — the ONLY source of this run's native
        # started/ready facts.
        self._subject = subject

    def _export_measured(self) -> bytes | None:
        payload = getattr(self._owner, "export_payload", None)
        if isinstance(payload, (bytes, bytearray)) and payload:
            return bytes(payload)
        return None

    def export_payload(self) -> bytes | None:
        """The exact bounded exported payload bytes the
        owner's finish path retained, or None when
        unmeasured."""
        return self._export_measured()

    def container_present_before(self) -> bool | None:
        """The positive-before measurement: the exact CID
        still had descendant processes before teardown was
        attempted, or None when unmeasured."""
        if self._export_measured() is None:
            return None
        count = getattr(self._owner, "descendants_before", None)
        if not isinstance(count, int) or isinstance(count, bool):
            return None
        return count > 0

    def container_absent_after(self) -> bool | None:
        """The verified ABSENCE of the exact CID after
        teardown, or None when unmeasured."""
        if self._export_measured() is None:
            return None
        value = getattr(self._owner, "teardown_container_absent", None)
        return value if isinstance(value, bool) else None

    def image_absent_after(self) -> bool | None:
        """The verified ABSENCE of the immutable image
        after teardown, or None when unmeasured."""
        if self._export_measured() is None:
            return None
        value = getattr(self._owner, "image_removed", None)
        return value if isinstance(value, bool) else None

    def descendants_after(self) -> int | None:
        """The measured zero descendant count after
        teardown, or None when unmeasured."""
        if self._export_measured() is None:
            return None
        value = getattr(self._owner, "teardown_descendants_after", None)
        if isinstance(value, int) and not isinstance(value, bool):
            return value
        return None

    def sentinel_survived(self) -> bool | None:
        """The unrelated parent sentinel survival fact, or
        None when unmeasured."""
        if self._export_measured() is None:
            return None
        value = getattr(self._owner, "sentinel_survived", None)
        return value if isinstance(value, bool) else None

    def native_started(self) -> bool | None:
        """The run's OWN measured native-started fact: the
        PUBLIC collectors actually measured the native
        subject alive (the retained pre-teardown receipt
        exists).  None when unmeasured — a run with no
        measured subject (the historical S scope) can
        therefore never mint this record, and a caller
        flag never mints one either."""
        if self._export_measured() is None:
            return None
        if self._subject is None:
            return None
        return True

    def native_ready(self) -> bool | None:
        """The run's OWN measured native-ready fact: the
        measured subject reached the closed ready
        qualification — cid-scoped membership in the
        exact registered CID, the executable identity
        actually MEASURED and verified, and the birth
        bound established.  A measured-but-unqualified
        subject is honestly False (started, not
        ready); None when unmeasured."""
        if self._export_measured() is None:
            return None
        subject = self._subject
        if subject is None:
            return None
        # a visible native handoff subject must be bound to
        # an actually bound, matched, NONZERO expected PTY:
        # an unobserved expected PTY or a measured tty0
        # subject can never qualify (started, not ready)
        if subject.pty_matched is not True:
            return False
        # the measured executable identity must agree with
        # the owner's OWN registered artifact binding (the
        # expectation alone is not the owner's
        # registration): a measured mismatch is honestly
        # started-but-not-ready, never a silent adoption
        artifact = getattr(self._owner, "artifact", None)
        owner_binary = artifact.get("binary_sha256") if isinstance(artifact, Mapping) else None
        if subject.binary_sha256 is not None and (
            not isinstance(owner_binary, str) or owner_binary != subject.binary_sha256
        ):
            return False
        return (
            subject.cid_membership == "cid-scoped"
            and subject.binary_verified is True
            and subject.start_bound is True
        )

    @property
    def measured_context(self) -> dict[str, str] | None:
        """The resources this owner's teardown actually
        belonged to, derived from the owner's OWN
        registration/measured state (never from a
        caller): its opted-in order, the literal bound
        source head, its own run id, the exact CID and
        immutable image it operated on, and the pinned
        binary.  None when any component is unmeasured —
        the producer refuses: a native-owner record must
        bind the measured teardown to the exact expected
        resources, and an incomplete binding is an
        unknown, never a silent skip."""
        owner = self._owner
        optin = getattr(owner, "optin", None)
        artifact = getattr(owner, "artifact", None)
        values: dict[str, object] = {
            "order": optin.get("order") if isinstance(optin, Mapping) else None,
            "source_head": optin.get("bind_head") if isinstance(optin, Mapping) else None,
            "run_id": getattr(owner, "run_id", None),
            "cid": getattr(owner, "target_cid", None),
            "image_id": getattr(owner, "image_id", None),
            "binary_sha256": artifact.get("binary_sha256")
            if isinstance(artifact, Mapping)
            else None,
        }
        if not all(isinstance(v, str) and v for v in values.values()):
            return None
        return {key: str(value) for key, value in values.items()}


def produce_native_owner_record(
    measurement: object,
    *,
    order: str,
    source_head: str,
    run_id: str,
    cid: str,
    image_id: str,
    binary_sha256: str,
    max_export_bytes: int = 16 << 20,
    identity: dict | None = None,
) -> dict[str, object]:
    """The explicit NATIVE-OWNER PRODUCER (order 017-t,
    section 3): the measurement-to-record boundary.  It
    INVOKES the owned finish/export/teardown measurement
    path, validates the FULL measured export payload with
    the ACTUAL shared export validator (the same closed
    quiesce/snapshot/diagnostic/originals law the R/S
    finish path applies to its host revalidation — a
    recomputed digest alone proves framing integrity,
    never payload validity).  The canonical 017-aj entry
    validates the DISTINCT selected format-capture payload
    through the closed tag dispatcher instead (the full or
    the safe partial form; the untagged six-field legacy
    form is drift under AJ and is refused, never
    relabelled), recomputes the export digest
    from the measured payload bytes ITSELF (a supplied
    digest is never trusted), and only then PRODUCES the
    closed ``slaif-native-owner-evidence-v1`` record from
    the closed teardown facts (present-before /
    absent-after on the exact CID and image, zero
    descendants, sentinel survival, native started).  A
    measurement that exposes ``measured_context`` (the
    real owned adapter always does) is additionally
    BOUND: the measured resources must equal the expected
    immutable order/run binding exactly — a caller
    order/source/CID/image string is never an observed
    identity, and an incomplete (None) or contradicting
    context is a closed non-echoing refusal, never a
    silent skip to the caller strings.  The historical S
    record is never relabeled or derived into this scope.
    An unmeasured, over-bound, invalid or contradictory
    fact is a closed non-echoing refusal — the producer
    emits no partial record — and the produced record must
    round-trip the closed consumer validation: producer
    and consumer agreement is enforced, never assumed."""
    # the DISTINCT 017-ad identity-bearing form: the SAME
    # closed measured facts PLUS the frozen owner-identity
    # substructure (the real owner's own collected/derived
    # identity, closed-validated here against the production
    # codec — a malformed or inconsistent substructure is a
    # closed refusal; it is data integrity, never measured
    # authority).  None keeps the original tag byte-for-byte.
    if identity is not None and _ad_identity_substructure_law(identity) is None:
        raise FixtureError("prep-native-owner-record-malformed")
    if not isinstance(order, str) or re.fullmatch(r"^[0-9]{3}-[a-z]{1,2}$", order) is None:
        raise FixtureError("prep-native-owner-record-malformed")
    if not isinstance(source_head, str) or _HEAD_RE.fullmatch(source_head) is None:
        raise FixtureError("prep-native-owner-record-malformed")
    if not isinstance(run_id, str) or _RUN_ID_RE.fullmatch(run_id) is None:
        raise FixtureError("prep-native-owner-record-malformed")
    if not isinstance(cid, str) or _CID_RE.fullmatch(cid) is None:
        raise FixtureError("prep-native-owner-record-malformed")
    if not isinstance(image_id, str) or _IMAGE_ID_RE.fullmatch(image_id) is None:
        raise FixtureError("prep-native-owner-record-malformed")
    if not isinstance(binary_sha256, str) or _SHA_RE.fullmatch(binary_sha256) is None:
        raise FixtureError("prep-native-owner-record-malformed")
    for name in _SEAM_METHODS:
        if not callable(getattr(measurement, name, None)):
            raise FixtureError("prep-native-owner-record-malformed")
    payload = measurement.export_payload()
    if not isinstance(payload, (bytes, bytearray)) or not payload:
        raise FixtureError("prep-native-owner-record-malformed")
    export_bytes = len(payload)
    if export_bytes > max_export_bytes:
        raise FixtureError("prep-export-overbound")
    # FULL shared closed-object validation of the measured
    # payload BEFORE any record is produced: the ACTUAL
    # shared validator (exact top-level field set,
    # model-validated quiesce and snapshot records, closed
    # diagnostic/position consistency, originals whose
    # DECODED bytes bind to the snapshot bytes AND sha) —
    # a rehash of arbitrary bytes would prove framing
    # integrity only
    # The canonical 017-aj entry's closed format-capture
    # scenario carries the DISTINCT three-field selected
    # format payload: the closed record tag selects the
    # full or the safe partial format law, and the
    # untagged six-field legacy form is drift under AJ,
    # refused, never relabelled (the SAME closed form law
    # the AJ owner finish applies at its export seam).
    # Every historical entry keeps the original six-field
    # payload law byte-for-byte (a selected format payload
    # there is refused by the original validator's exact
    # field set).
    try:
        if order == rprofile.AJ_ORDER_ID:
            selected = ci.fixture_export.validate_selected_payload(bytes(payload))
            if selected.get("record") not in (
                fmodel.SCHEMA_FORMAT_EXPORT,
                fmodel.SCHEMA_FORMAT_EXPORT_PARTIAL,
            ):
                raise ValueError("format-payload-tag")
        else:
            ci.fixture_export.validate_payload(bytes(payload))
    except ValueError:
        raise FixtureError("prep-export-invalid") from None
    export_sha = hashlib.sha256(bytes(payload)).hexdigest()
    present_before = measurement.container_present_before()
    cid_absent = measurement.container_absent_after()
    image_absent = measurement.image_absent_after()
    descendants = measurement.descendants_after()
    sentinel = measurement.sentinel_survived()
    native_started = measurement.native_started()
    native_ready = measurement.native_ready()
    if (
        present_before is not True
        or cid_absent is not True
        or image_absent is not True
        or not isinstance(descendants, int)
        or isinstance(descendants, bool)
        or descendants != 0
        or sentinel is not True
        or native_started is not True
        or not isinstance(native_ready, bool)
    ):
        raise FixtureError("prep-native-owner-record-malformed")
    # measured-context binding: a measurement that
    # exposes the resources it measured must bind them
    # EXACTLY to the expected immutable order/run
    # binding — the real owned adapter always exposes
    # it, and an incomplete (None) or contradicting
    # context is a closed refusal, never a silent skip
    # to the caller strings
    _no_context = object()
    context = getattr(measurement, "measured_context", _no_context)
    if context is not _no_context:
        if not isinstance(context, Mapping) or set(context) != _MEASURED_CONTEXT_KEYS:
            raise FixtureError("prep-native-owner-context-mismatch")
        expected: dict[str, str] = {
            "order": order,
            "source_head": source_head,
            "run_id": run_id,
            "cid": cid,
            "image_id": image_id,
            "binary_sha256": binary_sha256,
        }
        for key, value in expected.items():
            if context.get(key) != value:
                raise FixtureError("prep-native-owner-context-mismatch")
    record: dict[str, object] = {
        "record": NATIVE_OWNER_SCHEMA,
        "producer": NATIVE_OWNER_PRODUCER,
        "status": "pass",
        "order": order,
        "source_head": source_head,
        "run_id": run_id,
        "prepared": {"cid": cid},
        "image": {"image_id": image_id},
        "artifact": {"binary_sha256": binary_sha256},
        "export": {"bytes": export_bytes, "sha256": export_sha},
        "teardown": {
            "container_present_before": True,
            "container_removal": "absent-verified",
            "image_removal": "absent-verified",
            "descendants_after": 0,
            "sentinel_survived": True,
        },
        "native_started": True,
        "native_ready": native_ready,
    }
    if identity is not None:
        # the DISTINCT identity-bearing tag of THIS entry's
        # OWN form: the identity substructure is bound to the
        # entry's exact order (a foreign order id can never
        # carry the identity-bearing form)
        if order == rprofile.AD_ORDER_ID:
            record["record"] = AD_NATIVE_OWNER_SCHEMA
        elif order == rprofile.AF_ORDER_ID:
            record["record"] = AF_NATIVE_OWNER_SCHEMA
        elif order == rprofile.AH_ORDER_ID:
            record["record"] = AH_NATIVE_OWNER_SCHEMA
        elif order == rprofile.AJ_ORDER_ID:
            record["record"] = AJ_NATIVE_OWNER_SCHEMA
        else:
            raise FixtureError("prep-native-owner-record-malformed")
        record["identity"] = identity
    # producer/consumer agreement: the produced record must
    # pass the closed consumer validation before it is
    # returned — a drift between the two is a refusal, never
    # a silently shipped record
    parse_native_owner_facts(record)
    return record


# -- verdict composition ---------------------------------------------------------------


@dataclass(frozen=True)
class HandoffVerdict:
    """The composed native-handoff verdict.  ``ready`` is a
    measured composition, never a caller flag: it holds only
    when the owner's verified export/teardown, the complete
    measured native subject identity and the independently
    measured native subject identity (bound to the SAME
    cid/run as the owner, birth-bound, binary MEASURED, and
    separately verified absent after teardown) and the
    independently measured same-job restoration (after a
    recorded stop) all exist.  The closed ``reasons`` say
    exactly what is missing."""

    ready: bool
    reasons: tuple[str, ...]


_VERDICT_REASONS = frozenset(
    {
        "no-owner-final",
        "owner-teardown-unverified",
        "owner-subject-context-mismatch",
        "owner-subject-binary-mismatch",
        "owner-native-unready",
        "owner-scope-not-native",
        "no-native-identity",
        "subject-start-unbound",
        "subject-pty-unmatched",
        "subject-cid-unscoped",
        "subject-binary-unmeasured",
        "subject-absence-unverified",
        "no-restoration",
        "worker-stop-unmeasured",
        "same-job-restore-unmeasured",
    }
)


def compose_handoff_verdict(
    owner: OwnerFinalFacts | NativeOwnerFacts | None,
    subject: SubjectIdentity | None,
    restoration: RestorationFacts | None,
    *,
    subject_absent: bool | None = None,
) -> HandoffVerdict:
    """Compose the overall verdict AFTER the owner's own
    export/teardown finished (teardown-before-restore).  The
    inputs are the typed records or explicit None — a
    caller-authored ready/status/flag JSON is a closed
    refusal, not a measurement.  The owner's own safety flags
    are NOT re-asserted about the host: the verdict is
    independent of them by construction.  ``subject_absent``
    is the SEPARATELY verified post-teardown absence of the
    subject receipt (True = measured absent, False = still
    present, None = not verified): the historical receipt is
    composed, its absence is checked on its own — neither
    replaces the other."""
    if not isinstance(owner, (OwnerFinalFacts, NativeOwnerFacts, type(None))):
        raise FixtureError("prep-verdict-input-invalid")
    if not isinstance(subject, (SubjectIdentity, type(None))):
        raise FixtureError("prep-verdict-input-invalid")
    if not isinstance(restoration, (RestorationFacts, type(None))):
        raise FixtureError("prep-verdict-input-invalid")
    if not isinstance(subject_absent, (bool, type(None))):
        raise FixtureError("prep-verdict-input-invalid")
    reasons: list[str] = []
    if owner is None:
        reasons.append("no-owner-final")
    elif not owner.teardown_verified:
        reasons.append("owner-teardown-unverified")
    elif isinstance(owner, NativeOwnerFacts) and owner.native_ready is not True:
        # a native-owner run that honestly measured
        # started-but-NOT-ready can never qualify a
        # native-ready composition: the truthful negative
        # is preserved, never relabeled
        reasons.append("owner-native-unready")
    if isinstance(owner, OwnerFinalFacts):
        # the historical S scope decodes and validates as
        # its own scope, but it can NEVER qualify a
        # native-ready composition: its closed flags keep
        # their S meaning and are never relabeled as
        # native facts
        reasons.append("owner-scope-not-native")
    if subject is None:
        reasons.append("no-native-identity")
    else:
        if owner is not None and (owner.cid != subject.cid or owner.run_id != subject.run_id):
            # the registered context must be the owner's
            # verified cid/run: a subject measured under a
            # foreign or unlinked cid/run is not this
            # handoff's identity
            reasons.append("owner-subject-context-mismatch")
        if (
            owner is not None
            and subject.binary_sha256 is not None
            and owner.binary_sha256 != subject.binary_sha256
        ):
            # the retained measured subject's executable
            # identity must agree with the owner's
            # registered artifact: same CID/run strings
            # cannot substitute for exact executable
            # agreement
            reasons.append("owner-subject-binary-mismatch")
        if not subject.start_bound:
            reasons.append("subject-start-unbound")
        if subject.pty_matched is not True:
            # the visible native handoff subject must be
            # bound to an actually bound, matched, nonzero
            # expected PTY: an unobserved expected PTY or a
            # measured tty0 subject can never qualify
            reasons.append("subject-pty-unmatched")
        if subject.cid_membership != "cid-scoped":
            # a raw host-table observation is never membership
            # in the registered container: a matching
            # UID/argv/binary in another container must not
            # pass
            reasons.append("subject-cid-unscoped")
        if not subject.binary_verified:
            reasons.append("subject-binary-unmeasured")
        if subject_absent is not True:
            reasons.append("subject-absence-unverified")
    if restoration is None:
        reasons.append("no-restoration")
    elif not restoration.stop_recorded:
        # no separately recorded stop: a single snapshot is
        # not a restoration
        reasons.append("worker-stop-unmeasured")
    elif not restoration.restored:
        reasons.append("same-job-restore-unmeasured")
    assert all(r in _VERDICT_REASONS for r in reasons)
    return HandoffVerdict(ready=not reasons, reasons=tuple(reasons))


# -- the public workflow ---------------------------------------------------------------


def _verified_absence(table: ProcTable, pid: int) -> bool | None:
    """The post-teardown absence check for a retained subject
    receipt: True ONLY when the table proves the pid entry
    itself is gone; an unreadable, unprovable or
    capability-less read is an honest unknown (None), never a
    verified absence — absence is a measurement, and an
    unreadable stat cannot be one."""
    probe = getattr(table, "pid_present", None)
    if not callable(probe):
        return None
    result = probe(pid)
    if result is True or result is False:
        return result is True
    return None


def _parse_owner_record(record: Mapping | None) -> OwnerFinalFacts | NativeOwnerFacts | None:
    """Dispatch the owner's retained record to its typed
    parser by the record's OWN versioned schema: the
    historical 017-s rehearsal record or the explicit
    native-owner producer record.  An explicit None is the
    closed "not yet finished" value; anything else that is
    not one of the closed versioned owner schemas is a closed
    non-echoing refusal — the record's own declared scope
    decides which closed law applies, and the S flags are
    never reinterpreted as native facts (or vice versa)."""
    if record is None:
        return None
    if not isinstance(record, Mapping):
        raise FixtureError("prep-owner-record-malformed")
    kind = record.get("record")
    if kind == _S_EVIDENCE_SCHEMA:
        return parse_owner_final_facts(record)
    if kind in (NATIVE_OWNER_SCHEMA, AD_NATIVE_OWNER_SCHEMA):
        # both native-owner tags share the SAME closed consumer
        # law; the tag selects its own exact key set inside
        # (the identity-bearing 017-ad form carries the frozen
        # identity substructure, the original tag never does)
        return parse_native_owner_facts(record)
    if kind == AF_NATIVE_OWNER_SCHEMA:
        # the identity-bearing 017-af form: the SAME closed
        # consumer law, its own exact key set and tag-pair
        return parse_native_owner_facts(record)
    if kind == AH_NATIVE_OWNER_SCHEMA:
        # the identity-bearing 017-ah form: the SAME closed
        # consumer law, its own exact key set and tag-pair
        return parse_native_owner_facts(record)
    if kind == AJ_NATIVE_OWNER_SCHEMA:
        # the identity-bearing 017-aj form: the SAME closed
        # consumer law, its own exact key set and tag-pair
        return parse_native_owner_facts(record)
    raise FixtureError("prep-owner-record-malformed")


class NativeHandoffWorkflow:
    """The public prepare / observe / finalize surface for the
    later native handoff.  The constructor takes only the
    binding, the (optional) table seam, the (optional)
    registered-CID channel and configuration pids — it NEVER
    takes a prepopulated facts record (a constructor or
    manually prepopulated record is not workflow evidence).
    prepare() and finalize() invoke the collectors themselves
    and only then record/measure state; observe() re-collects
    non-consuming.  The actual LATER native subject is
    registered through the public staged entry
    register_subject() AFTER prepare (the constructor carries
    no predicted native PID): the registration invokes the
    collectors itself before committing any identity, and the
    expected PTY/binary/CID/run arrive from the operator's
    owned attach registration (the expectation), never copied
    from the candidate's own unchecked fields.  The workflow
    retains a bounded IMMUTABLE
    RECEIPT of the pre-teardown subject identity (the last
    identity measured while alive) and records the worker
    stop as a SEPARATE measured event (record_stop):
    finalize composes the historical receipt with the
    separately verified post-teardown ABSENCE, the owner
    teardown and the same-job restoration — it never
    re-collects and replaces the receipt, never adopts a
    reused PID, and never infers a missing first
    observation.  There is no CLI entry: the runtime CLI
    cannot accept a fabricated collector result, and
    injection exists only in-process for trusted fake
    tests."""

    def __init__(
        self,
        binding: object,
        table: ProcTable | None = None,
        *,
        worker_pid: int | None = None,
        bash_pid: int | None = None,
        subject_pid: int | None = None,
        expectation: SubjectExpectation | None = None,
        owner_run_id: str | None = None,
        tty_foreground_pgrp: int | None = None,
        channel: CidScopedTable | None = None,
        registered_owners: Mapping[int, int] | None = None,
        subject_identity: tuple[int, int, tuple[int, ...]] | None = None,
    ) -> None:
        if not isinstance(binding, OrderRunBinding):
            raise FixtureError("prep-binding-invalid")
        # the FROZEN owner-UID subject identity (the future
        # 017-ad native handoff): closed-validated ONCE at
        # construction (the Z eligible-ID law, groups exactly
        # the primary GID) and applied to EVERY subject
        # observation of this workflow (prepare/observe and the
        # staged registration); None keeps the original
        # fixed-21002 law byte-for-byte.  The triple is data
        # (the real owner's own frozen identity), never a
        # per-read re-derivation and never measured authority.
        self._subject_identity = (
            _validate_frozen_subject_identity(subject_identity)
            if subject_identity is not None
            else None
        )
        if owner_run_id is not None and (
            not isinstance(owner_run_id, str) or _RUN_ID_RE.fullmatch(owner_run_id) is None
        ):
            raise FixtureError("prep-binding-invalid")
        self._binding: OrderRunBinding = binding
        self._table: ProcTable = table if table is not None else RealProcTable()
        self._channel = channel
        self._registered_owners = registered_owners
        self._worker_pid = worker_pid
        self._bash_pid = bash_pid
        self._subject_pid = subject_pid
        self._expectation = expectation
        self._owner_run_id = owner_run_id
        self._foreground = tty_foreground_pgrp
        self._prepared = False
        self._group: WorkerGroupFacts | None = None
        # the FROZEN first-prepare W/B baseline: every later
        # observation, stop and restoration is bound to this
        # exact worker job; repeated prepare/observe never
        # reset or replace it
        self._baseline: WorkerGroupFacts | None = None
        self._subject: SubjectIdentity | None = None
        # bounded IMMUTABLE pre-teardown receipts: the last
        # subject identity measured while alive and the
        # separately recorded stop event — neither is ever
        # re-collected, replaced or re-measured later
        self._subject_receipt: SubjectIdentity | None = None
        self._stop_receipt: StopReceipt | None = None

    @property
    def binding(self) -> OrderRunBinding:
        return self._binding

    @property
    def stop_receipt(self) -> StopReceipt | None:
        """The separately measured worker-stop event, or
        None when no stop was recorded (a recorded event is
        never re-measured or replaced)."""
        return self._stop_receipt

    @property
    def subject_receipt(self) -> SubjectIdentity | None:
        """The retained bounded IMMUTABLE pre-teardown
        subject identity (the last identity the public
        collectors measured while alive), or None when the
        subject was never observed.  This is the ONLY
        source of a native-owner run's native
        started/ready facts: the producer's measurement
        seam binds them to this measured receipt, never to
        a caller flag."""
        return self._subject_receipt

    @property
    def subject_identity(self) -> tuple[int, int, tuple[int, ...]] | None:
        """The frozen owner-UID subject identity this
        workflow's subject law applies (017-ad), or None for
        the original fixed-21002 law (byte-for-byte)."""
        return self._subject_identity

    def _collect_subject(self) -> SubjectIdentity | None:
        if self._subject_pid is None and self._expectation is None:
            return None
        if self._subject_pid is None or self._expectation is None:
            raise FixtureError("prep-expectation-invalid")
        return collect_subject_identity(
            self._table,
            self._subject_pid,
            self._expectation,
            channel=self._channel,
            subject_identity=self._subject_identity,
        )

    def _collect_group(self) -> WorkerGroupFacts:
        if self._worker_pid is None:
            raise FixtureError("prep-worker-invalid")
        return collect_worker_group(
            self._table,
            self._worker_pid,
            self._bash_pid,
            self._foreground,
            registered_owners=self._registered_owners,
        )

    def prepare(self) -> dict[str, object]:
        """Invoke the collectors themselves, THEN record the
        measured state (registration collects before
        recording).  A vanished subject is recorded as
        unobserved, not invented.  The FIRST prepare freezes
        the immutable W/B baseline, and the first measured
        subject becomes the bounded IMMUTABLE pre-teardown
        receipt; a repeated prepare re-measures the current
        view but must still be the same worker job and the
        same subject process — it never resets the frozen
        baseline or the receipt."""
        group = self._collect_group()
        if self._baseline is None:
            # the FIRST prepare freezes the immutable W/B
            # baseline: every later observation, stop and
            # restoration is bound to THIS worker job; a
            # repeated prepare must not reset it
            self._baseline = group
        else:
            self._check_group_continuity(group)
        try:
            subject = self._collect_subject()
        except FixtureError as exc:
            if str(exc) != "prep-subject-vanished":
                raise
            subject = None
        self._register_subject(subject)
        self._group = group
        self._subject = subject
        self._prepared = True
        return self._snapshot()

    def observe(self) -> dict[str, object]:
        """The bounded non-consuming re-observation: re-collect
        the same read-only facts, no state advancement, no
        consumption.  The FIRST measured subject identity is
        retained as the bounded IMMUTABLE pre-teardown
        receipt; a later re-measurement must be the SAME
        process (pid, birth) with the SAME context (cid/run)
        or it is a reused/substituted identity — refused,
        never adopted."""
        if not self._prepared:
            raise FixtureError("prep-not-prepared")
        group = self._collect_group()
        # verify against the FROZEN first-prepare baseline
        # BEFORE updating the observation: a substituted
        # worker/bash is a closed refusal, never a silently
        # adopted baseline
        self._check_group_continuity(group)
        try:
            subject = self._collect_subject()
        except FixtureError as exc:
            if str(exc) != "prep-subject-vanished":
                raise
            subject = None
        self._register_subject(subject)
        self._group = group
        self._subject = subject
        return self._snapshot()

    def register_subject(
        self,
        subject_pid: object,
        expectation: object,
        *,
        channel: CidScopedTable | None = None,
        pre_commit_check: Callable[[SubjectIdentity], None] | None = None,
    ) -> dict[str, object]:
        """The PUBLIC staged registration of the actual
        native subject that appears later (order 017-v,
        section 4).  The constructor carries no predicted
        native PID; this is the operator entry.  The
        registration invokes the collectors ITSELF against
        the read-only table (and, when the operator supplies
        the owned attach channel, against that CID-scoped
        channel) BEFORE committing any identity —
        registration collects before recording, exactly as
        prepare.  The expected PTY, binary, CID and run come
        from the operator's OWNED attach registration
        (the expectation) and are independently correlated
        with the measured subject by the collector: copying
        the candidate's own unchecked tty field (or an
        earlier stand-in's PTY) is not proof, and a channel
        bound to another CID refuses before any read.  A
        REFUSED registration commits nothing — no baseline
        replacement, no receipt, no stop — and may be
        retried with corrected parameters.  A conflicting
        SECOND registration of an already-registered subject
        is a closed refusal; the retained receipt stays the
        first measured identity."""
        if self._subject_pid is not None or self._expectation is not None:
            raise FixtureError("prep-subject-registered")
        if not self._prepared:
            raise FixtureError("prep-not-prepared")
        # the STAGED law (order 017-v, section 4): the actual
        # native subject is registered only AFTER the same
        # worker's stop has been separately measured — a
        # pre-stop registration cannot mint a receipt
        if self._stop_receipt is None:
            raise FixtureError("prep-stop-not-recorded")
        # the FROZEN first-prepare W/B baseline must still be
        # the same worker job: a substituted worker/bash (PID
        # reuse, changed birth) after the stop is a closed
        # refusal, never a silently adopted baseline
        self._verify_baseline()
        base = self._baseline
        if base is None:
            raise FixtureError("prep-not-prepared")
        # the CURRENT bounded stable-stop predicate must still
        # hold at registration: the retained stop receipt is
        # the immutable HISTORICAL record (never replaced or
        # re-measured into), but the phase it recorded must be
        # the phase the world is in NOW — a resumed worker, a
        # newly running group member, a changed foreground, or
        # a newly unreadable positively-existing listed entry
        # (tri-state law) means the staged registration is no
        # longer in its stable stopped phase: a closed
        # refusal BEFORE any identity commit.  The
        # re-measurement is predicate-only; its receipt is
        # discarded, never adopted.
        collect_stop_observation(self._table, base.worker_pid, base.bash_pid)
        if not _is_pid(subject_pid):
            raise FixtureError("prep-subject-invalid")
        expectation = _validate_expectation(expectation)
        if expectation.run_id != self._binding.run_id:
            # the registered run identity is immutable: a
            # foreign expectation run can never register into
            # this workflow
            raise FixtureError("prep-subject-run-mismatch")
        ch = self._channel if channel is None else channel
        subject = collect_subject_identity(
            self._table,
            subject_pid,
            expectation,
            channel=ch,
            subject_identity=self._subject_identity,
        )
        # the AF COLLECT-BEFORE-COMMIT boundary (017-ae
        # software): the composition's FINAL measured frames
        # (the collected subject's own tty, the re-read devpts
        # namespace/device, the frozen owner identity, the
        # current stable-stop phase, the SAME absolute owner
        # END) run HERE — after the possibly-long executable
        # measurement and BEFORE ANY subject/baseline/stop
        # commit.  A refused check commits nothing (the
        # staged law: no baseline replacement, no receipt,
        # no stop change) and a later corrected registration
        # within the same still-valid phase remains possible.
        # The original/AD entries pass no check: their
        # behavior stays byte-for-byte.
        if pre_commit_check is not None:
            pre_commit_check(subject)
        # commit ONLY after a successful collection
        self._subject_pid = subject.pid
        self._expectation = expectation
        self._channel = ch
        self._register_subject(subject)
        self._subject = subject
        return self._snapshot()

    def _register_subject(self, subject: SubjectIdentity | None) -> None:
        """Retain the bounded IMMUTABLE pre-teardown receipt:
        the FIRST measured subject identity is kept; a later
        measurement must be the SAME process (pid, birth)
        with the SAME context (cid/run) or it is a
        reused/substituted identity — refused, never
        adopted."""
        if subject is None:
            return
        receipt = self._subject_receipt
        if receipt is None:
            # the first measured identity: retained as the
            # bounded IMMUTABLE pre-teardown receipt
            self._subject_receipt = subject
        elif (
            subject.pid != receipt.pid
            or subject.start_time != receipt.start_time
            or subject.cid != receipt.cid
            or subject.run_id != receipt.run_id
        ):
            # a different process at the same subject pid
            # (reused PID or substituted identity) is a
            # closed refusal, never adopted into the receipt
            raise FixtureError("prep-subject-invalid")

    def _check_group_continuity(self, group: WorkerGroupFacts) -> None:
        """A re-measured group must be the SAME worker job as
        the frozen first-prepare baseline (W: pid, birth,
        group, session, TTY; B: pid, birth): a substituted
        worker or bash is a closed refusal, never a silently
        adopted baseline."""
        base = self._baseline
        if base is None:
            raise FixtureError("prep-not-prepared")
        if (
            group.worker_pid != base.worker_pid
            or group.worker_start_time != base.worker_start_time
            or group.worker_pgrp != base.worker_pgrp
            or group.worker_session != base.worker_session
            or group.worker_tty != base.worker_tty
        ):
            raise FixtureError("prep-worker-invalid")
        if group.bash_pid != base.bash_pid or group.bash_start_time != base.bash_start_time:
            raise FixtureError("prep-bash-invalid")

    def _verify_baseline(self) -> None:
        """Bind the currently measured W and B to the prepare
        baseline (pid, birth, group, session, TTY): PID reuse
        or substitution after prepare is a closed refusal,
        and a baseline process that is unreadable or gone is
        a refusal, never an unknown the workflow continues
        over — the stop and the restoration are facts about
        THIS worker job, not about whatever now occupies the
        pids."""
        base = self._baseline
        if base is None:
            raise FixtureError("prep-not-prepared")
        w = _try_parse_stat(self._table, base.worker_pid)
        if w is None:
            raise FixtureError("prep-worker-vanished")
        if (
            w.start_time != base.worker_start_time
            or w.pgrp != base.worker_pgrp
            or w.session != base.worker_session
            or w.tty != base.worker_tty
        ):
            raise FixtureError("prep-worker-invalid")
        b = _try_parse_stat(self._table, base.bash_pid)
        if b is None:
            raise FixtureError("prep-bash-vanished")
        if b.start_time != base.bash_start_time:
            raise FixtureError("prep-bash-invalid")

    def record_stop(self) -> StopReceipt:
        """Record the separately measured worker-stop event
        READ-ONLY (no signal of any kind — the stop itself is
        performed later by the separately authorized
        operator).  A stop is a recorded EVENT, not a
        re-derived flag: the first measurement is retained; a
        later call returns the SAME receipt — the event is
        never re-measured or replaced, and a single current
        snapshot can never mint a past stop.  The stop is
        bound to the prepare baseline W and B: a stop
        observed on a substituted worker/bash is a closed
        refusal."""
        if self._stop_receipt is not None:
            return self._stop_receipt
        if not self._prepared:
            raise FixtureError("prep-not-prepared")
        if self._worker_pid is None:
            raise FixtureError("prep-worker-invalid")
        self._verify_baseline()
        base = self._baseline
        if base is None:
            raise FixtureError("prep-not-prepared")
        receipt = collect_stop_observation(self._table, base.worker_pid, base.bash_pid)
        self._stop_receipt = receipt
        return receipt

    def verify_stable_stop_phase(self) -> None:
        """The CURRENT bounded stable-stop predicate re-check
        for an ALREADY recorded stop (the AF attach phase and
        any later phase that must prove the world is still in
        the recorded phase): the FROZEN first-prepare W/B
        baseline must still be the same worker job (PID reuse
        or substitution is a closed refusal), and the stop
        phase recorded by the retained receipt must be the
        phase the world is in NOW (a resumed worker, a newly
        running group member, a changed foreground, or a
        newly unreadable positively-existing listed entry —
        the tri-state law — is a closed refusal).  The
        re-measurement is predicate-only: the retained stop
        receipt is the immutable historical record — it is
        re-verified, never replaced or re-measured into."""
        if self._stop_receipt is None:
            raise FixtureError("prep-stop-not-recorded")
        self._verify_baseline()
        base = self._baseline
        if base is None:
            raise FixtureError("prep-not-prepared")
        collect_stop_observation(self._table, base.worker_pid, base.bash_pid)

    def _snapshot(self) -> dict[str, object]:
        assert self._group is not None
        group = self._group
        snapshot: dict[str, object] = {
            "record": NATIVE_PREP_SCHEMA,
            "binding": self._binding.to_record(),
            "group": {
                "worker": {
                    "pid": group.worker_pid,
                    "state": group.worker_state,
                    "pgrp": group.worker_pgrp,
                    "session": group.worker_session,
                    "tty": group.worker_tty,
                    "start_time": group.worker_start_time,
                },
                "bash": {
                    "pid": group.bash_pid,
                    "state": group.bash_state,
                    "pgrp": group.bash_pgrp,
                    "session": group.bash_session,
                    "tty": group.bash_tty,
                    "start_time": group.bash_start_time,
                },
                "same_job": group.same_job,
                "same_tty": group.same_tty,
                "foreground_pgrp": group.foreground_pgrp,
                "members": [[m.pid, m.state, m.tty] for m in group.members],
                "session_other_groups": [[p, c] for p, c in group.session_other_groups],
                "tool_sessions": [
                    [pgrp, [[m.pid, m.state, m.tty, m.provenance] for m in ms]]
                    for pgrp, ms in group.tool_sessions
                ],
            },
            "subject": _subject_record(self._subject),
        }
        if self._subject_identity is not None:
            # the DISTINCT identity-bearing form of THIS entry
            # (the 017-ad or the 017-af tag): the SAME closed
            # measured facts PLUS the frozen owner-identity
            # substructure derived through the production codec
            # (the original fixed-21002 workflow keeps the
            # historical tag byte-for-byte, no identity key).
            # A frozen subject identity under any other entry
            # is a contradiction — a closed refusal, never a
            # silent relabel.
            if self._binding.order_id == rprofile.AD_ORDER_ID:
                snapshot["record"] = AD_NATIVE_PREP_SCHEMA
            elif self._binding.order_id == rprofile.AF_ORDER_ID:
                snapshot["record"] = AF_NATIVE_PREP_SCHEMA
            elif self._binding.order_id == rprofile.AH_ORDER_ID:
                snapshot["record"] = AH_NATIVE_PREP_SCHEMA
            elif self._binding.order_id == rprofile.AJ_ORDER_ID:
                snapshot["record"] = AJ_NATIVE_PREP_SCHEMA
            else:
                raise FixtureError("prep-record-malformed")
            snapshot["identity"] = _ad_identity_substructure_from_triple(self._subject_identity)
        return snapshot

    def finalize(self, owner_record: Mapping | None) -> HandoffVerdict:
        """Compose the verdict AFTER the owner's own
        export/teardown finished (teardown-before-restore).
        The owner's retained record is parsed by its OWN
        versioned schema (or explicit None = not yet
        finished) and its run id is bound to the workflow's
        registered run; a native-owner record is
        additionally bound to the immutable workflow
        binding's order, literal source head, and run, and
        the retained subject receipt is bound to that same
        run; the subject is the retained IMMUTABLE
        pre-teardown receipt (never re-collected, never
        replaced), whose post-teardown ABSENCE is verified
        separately on the read-only table (an unreadable
        entry is an unknown, never a verified absence; no
        signal, no inference); the restoration is ALWAYS
        collected by the workflow itself — with the recorded
        stop receipt and bound to the prepare baseline W and
        B — a caller-supplied restoration fact is not a
        measurement and has no entry here.  The owner facts
        describe a finished export/teardown, and the
        restoration is measured independently after."""
        if not self._prepared:
            raise FixtureError("prep-not-prepared")
        owner = _parse_owner_record(owner_record)
        if (
            owner is not None
            and self._owner_run_id is not None
            and owner.run_id != self._owner_run_id
        ):
            raise FixtureError("prep-owner-run-mismatch")
        if isinstance(owner, NativeOwnerFacts):
            # a native-owner record claims ownership of
            # THIS handoff's immutable binding: its order,
            # literal source head, and registered run must
            # each equal the bound values — CID/run alone
            # is insufficient, and a mismatch is a closed
            # refusal, never a silent composition
            if owner.order != self._binding.order_id:
                raise FixtureError("prep-owner-order-mismatch")
            if owner.source_head != self._binding.source_head:
                raise FixtureError("prep-owner-head-mismatch")
            if owner.run_id != self._binding.run_id:
                raise FixtureError("prep-owner-run-mismatch")
            if self._binding.order_id in (
                rprofile.AD_ORDER_ID,
                rprofile.AF_ORDER_ID,
                rprofile.AH_ORDER_ID,
                rprofile.AJ_ORDER_ID,
            ):
                # the canonical 017-ad / 017-af / 017-ah /
                # 017-aj entry's record must be the entry's
                # OWN DISTINCT identity-bearing tag and must
                # carry the SAME frozen owner-identity
                # substructure as this workflow's ORIGINAL
                # frozen subject law (compared, never
                # adopted): a relabeled original-tag record
                # (or the OTHER entry's tag) cannot
                # represent this entry, and a valid foreign
                # frozen identity can never become ready here
                expected_owner_schema = {
                    rprofile.AD_ORDER_ID: AD_NATIVE_OWNER_SCHEMA,
                    rprofile.AF_ORDER_ID: AF_NATIVE_OWNER_SCHEMA,
                    rprofile.AH_ORDER_ID: AH_NATIVE_OWNER_SCHEMA,
                    rprofile.AJ_ORDER_ID: AJ_NATIVE_OWNER_SCHEMA,
                }[self._binding.order_id]
                if owner.schema != expected_owner_schema:
                    raise FixtureError("prep-owner-schema-mismatch")
                if owner.identity != self._subject_identity:
                    raise FixtureError("prep-owner-identity-mismatch")
        subject = self._subject_receipt
        if subject is not None and subject.run_id != self._binding.run_id:
            # the retained pre-teardown receipt is part of
            # the composition: the advertised single bound
            # run must stay coherent across the registered
            # owner, the measured subject, and the immutable
            # binding
            raise FixtureError("prep-subject-run-mismatch")
        subject_absent: bool | None = None
        if subject is not None:
            # the SEPARATE post-teardown absence verification
            # of the retained receipt: verified absence only
            # when the table proves the pid entry is gone;
            # an unreadable or unprovable entry is an honest
            # unknown (None), never a verified absence
            subject_absent = _verified_absence(self._table, subject.pid)
        restoration: RestorationFacts | None = None
        if self._worker_pid is not None:
            self._verify_baseline()
            base = self._baseline
            if base is None:
                raise FixtureError("prep-not-prepared")
            restoration = collect_restoration(
                self._table,
                base.worker_pid,
                base.bash_pid,
                self._foreground,
                stop_receipt=self._stop_receipt,
            )
        return compose_handoff_verdict(owner, subject, restoration, subject_absent=subject_absent)


def _subject_record(subject: SubjectIdentity | None) -> dict[str, object] | None:
    if subject is None:
        return None
    return {
        "source": subject.source,
        "cid": subject.cid,
        "pid": subject.pid,
        "uid": subject.uid,
        "gid": subject.gid,
        "groups": list(subject.groups),
        "argv": list(subject.argv),
        "argv_sha256": subject.argv_sha256,
        "binary_sha256": subject.binary_sha256,
        "binary_verified": subject.binary_verified,
        "cid_attestation": subject.cid_attestation,
        "cid_membership": subject.cid_membership,
        "tty": subject.tty,
        "start_time": subject.start_time,
        "start_bound": subject.start_bound,
        "run_id": subject.run_id,
        "pty_matched": subject.pty_matched,
    }


def validate_prep_snapshot(record: object) -> None:
    """Closed structural validation of a retained workflow
    snapshot (the exact keys the workflow emits; no raw host
    content).  Used by the later flow to revalidate a retained
    record without trusting it by flag.

    The entry-aware closed tag law: the original tag
    (``slaif-native-handoff-prep-v1``) keeps its EXACT
    historical meaning — the fixed-21002 subject law, never an
    identity key, and never the record of the canonical 017-ad
    or 017-af / 017-ah entry (the equal-numeric cross-profile
    case: a fixed-21002 subject bound to any of them is still
    an identity-bearing record and belongs to the entry's OWN
    tag) — while the DISTINCT identity-bearing 017-ad / 017-af
    / 017-ah tags
    (``slaif-017ad-native-handoff-prep-v1`` /
    ``slaif-017af-native-handoff-prep-v1`` /
    ``slaif-017ah-native-handoff-prep-v1``) carry the SAME
    closed group/binding/subject facts PLUS the frozen owner-
    identity substructure, are the records of the canonical
    017-ad / 017-af / 017-ah entries ONLY, and their subject
    (when present) must satisfy the frozen owner-UID identity
    derived from that substructure (the fixed-21002 law never
    applies to them, and the frozen law never to the original
    tag)."""
    if not isinstance(record, Mapping):
        raise FixtureError("prep-record-malformed")
    tag = record.get("record")
    if tag == AD_NATIVE_PREP_SCHEMA:
        expected_keys = {"record", "binding", "group", "subject", "identity"}
    elif tag == AF_NATIVE_PREP_SCHEMA:
        expected_keys = {"record", "binding", "group", "subject", "identity"}
    elif tag == AH_NATIVE_PREP_SCHEMA:
        expected_keys = {"record", "binding", "group", "subject", "identity"}
    elif tag == AJ_NATIVE_PREP_SCHEMA:
        expected_keys = {"record", "binding", "group", "subject", "identity"}
    elif tag == NATIVE_PREP_SCHEMA:
        expected_keys = {"record", "binding", "group", "subject"}
    else:
        raise FixtureError("prep-record-malformed")
    if set(record) != expected_keys:
        raise FixtureError("prep-record-malformed")
    b = record["binding"]
    if (
        not isinstance(b, Mapping)
        or set(b)
        != {
            "record",
            "order_id",
            "order_path",
            "order_sha256",
            "active_sha256",
            "source_head",
            "repo_identity",
            "run_id",
        }
        or b["record"] != binding.BINDING_RECORD_SCHEMA
    ):
        raise FixtureError("prep-record-malformed")
    # The entry-aware closed ORDER binding: each tag is the
    # record of its OWN canonical entry only — the tags are
    # separate closed records, never a widened grammar
    # (including for equal-numeric identities).  The original
    # tag is the historical entries' record ONLY and refuses
    # the 017-ad, 017-af and 017-ah bindings.
    if tag == AD_NATIVE_PREP_SCHEMA:
        if b.get("order_id") != rprofile.AD_ORDER_ID:
            raise FixtureError("prep-record-malformed")
        # the fixed canonical 017-ad entry is bound to its OWN
        # unique committed order path (a foreign path can never
        # carry the identity-bearing AD form)
        if b.get("order_path") != rprofile.AD_ORDER_PATH:
            raise FixtureError("prep-record-malformed")
    elif tag == AF_NATIVE_PREP_SCHEMA:
        if b.get("order_id") != rprofile.AF_ORDER_ID:
            raise FixtureError("prep-record-malformed")
        # the fixed canonical 017-af entry is bound to its OWN
        # unique committed order path (a foreign path can never
        # carry the identity-bearing AF form)
        if b.get("order_path") != rprofile.AF_ORDER_PATH:
            raise FixtureError("prep-record-malformed")
    elif tag == AH_NATIVE_PREP_SCHEMA:
        if b.get("order_id") != rprofile.AH_ORDER_ID:
            raise FixtureError("prep-record-malformed")
        # the fixed canonical 017-ah entry is bound to its OWN
        # unique committed order path (a foreign path can never
        # carry the identity-bearing AH form)
        if b.get("order_path") != rprofile.AH_ORDER_PATH:
            raise FixtureError("prep-record-malformed")
    elif tag == AJ_NATIVE_PREP_SCHEMA:
        if b.get("order_id") != rprofile.AJ_ORDER_ID:
            raise FixtureError("prep-record-malformed")
        # the fixed canonical 017-aj entry is bound to its OWN
        # unique committed order path (a foreign path can never
        # carry the identity-bearing AJ form)
        if b.get("order_path") != rprofile.AJ_ORDER_PATH:
            raise FixtureError("prep-record-malformed")
    elif b.get("order_id") in (
        rprofile.AD_ORDER_ID,
        rprofile.AF_ORDER_ID,
        rprofile.AH_ORDER_ID,
        rprofile.AJ_ORDER_ID,
    ):
        raise FixtureError("prep-record-malformed")
    if tag in (
        AD_NATIVE_PREP_SCHEMA,
        AF_NATIVE_PREP_SCHEMA,
        AH_NATIVE_PREP_SCHEMA,
        AJ_NATIVE_PREP_SCHEMA,
    ):
        identity = _ad_identity_substructure_law(record["identity"])
        if identity is None:
            raise FixtureError("prep-record-malformed")
    else:
        identity = None
    g = record["group"]
    if not isinstance(g, Mapping) or set(g) != {
        "worker",
        "bash",
        "same_job",
        "same_tty",
        "foreground_pgrp",
        "members",
        "session_other_groups",
        "tool_sessions",
    }:
        raise FixtureError("prep-record-malformed")
    for part in ("worker", "bash"):
        p = g[part]
        if not isinstance(p, Mapping) or set(p) != {
            "pid",
            "state",
            "pgrp",
            "session",
            "tty",
            "start_time",
        }:
            raise FixtureError("prep-record-malformed")
        if not all(_is_strict_int(p[k]) for k in ("pid", "pgrp", "session", "tty", "start_time")):
            raise FixtureError("prep-record-malformed")
        if not isinstance(p["state"], str) or len(p["state"]) != 1:
            raise FixtureError("prep-record-malformed")
    if not isinstance(g["members"], list) or len(g["members"]) > _MEMBERSHIP_MAX:
        raise FixtureError("prep-record-malformed")
    for m in g["members"]:
        if (
            not isinstance(m, list)
            or len(m) != 3
            or not all(_is_strict_int(x) for x in (m[0], m[2]))
            or not isinstance(m[1], str)
            or len(m[1]) != 1
        ):
            raise FixtureError("prep-record-malformed")
    if (
        not isinstance(g["session_other_groups"], list)
        or len(g["session_other_groups"]) > _MEMBERSHIP_MAX
    ):
        raise FixtureError("prep-record-malformed")
    for pair in g["session_other_groups"]:
        if not isinstance(pair, list) or len(pair) != 2 or not all(_is_strict_int(x) for x in pair):
            raise FixtureError("prep-record-malformed")
    if not isinstance(g["tool_sessions"], list) or len(g["tool_sessions"]) > _MEMBERSHIP_MAX:
        raise FixtureError("prep-record-malformed")
    for entry in g["tool_sessions"]:
        if (
            not isinstance(entry, list)
            or len(entry) != 2
            or not _is_strict_int(entry[0])
            or not isinstance(entry[1], list)
            or len(entry[1]) > _MEMBERSHIP_MAX
        ):
            raise FixtureError("prep-record-malformed")
        for member in entry[1]:
            if (
                not isinstance(member, list)
                or len(member) != 4
                or not _is_strict_int(member[0])
                or not _is_strict_int(member[2])
                or not isinstance(member[1], str)
                or len(member[1]) != 1
                or member[3] not in _TOOL_PROVENANCE
            ):
                raise FixtureError("prep-record-malformed")
    s = record["subject"]
    if s is not None:
        if not isinstance(s, Mapping) or set(s) != {
            "source",
            "cid",
            "pid",
            "uid",
            "gid",
            "groups",
            "argv",
            "argv_sha256",
            "binary_sha256",
            "binary_verified",
            "cid_attestation",
            "cid_membership",
            "tty",
            "start_time",
            "start_bound",
            "run_id",
            "pty_matched",
        }:
            raise FixtureError("prep-record-malformed")
        if not isinstance(s["binary_verified"], bool):
            raise FixtureError("prep-record-malformed")
        if not isinstance(s["pty_matched"], bool):
            raise FixtureError("prep-record-malformed")
        if s["cid_attestation"] not in _CID_ATTESTATIONS:
            raise FixtureError("prep-source-invalid")
        if s["cid_membership"] not in CID_MEMBERSHIP:
            raise FixtureError("prep-record-malformed")
        if s["binary_sha256"] is not None and not isinstance(s["binary_sha256"], str):
            raise FixtureError("prep-record-malformed")
        # The STRICT subject identity law of THIS tag (the
        # snapshot consumer is entry-aware, not flag-trusting):
        # the original tag applies the fixed-21002 law
        # byte-for-byte (an owner-UID subject is a closed
        # refusal under it), and the 017-ad tag applies the
        # FROZEN owner-UID law derived from its own validated
        # identity substructure (the fixed-21002 law never
        # applies to it — the frozen triple is data, not a
        # caller flag).
        try:
            _check_identity_fields(
                s["uid"],
                s["gid"],
                tuple(s["groups"]),
                s["argv"],
                s["tty"],
                subject_identity=identity,
            )
        except (FixtureError, KeyError, TypeError):
            raise FixtureError("prep-record-malformed") from None


__all__ = [
    "NATIVE_PREP_SCHEMA",
    "AD_NATIVE_PREP_SCHEMA",
    "AF_NATIVE_PREP_SCHEMA",
    "AH_NATIVE_PREP_SCHEMA",
    "AJ_NATIVE_PREP_SCHEMA",
    "NATIVE_OWNER_PRODUCER",
    "NATIVE_OWNER_SCHEMA",
    "AD_NATIVE_OWNER_SCHEMA",
    "AF_NATIVE_OWNER_SCHEMA",
    "AH_NATIVE_OWNER_SCHEMA",
    "AJ_NATIVE_OWNER_SCHEMA",
    "AF_ATTACH_BINDING_SCHEMA",
    "AH_ATTACH_BINDING_SCHEMA",
    "AJ_ATTACH_BINDING_SCHEMA",
    "AJ_FORMAT_CAPTURE_SCHEMA",
    "parse_format_capture_record",
    "AF_ATTACH_RECORD_KEYS",
    "AF_ATTACH_ENCODING",
    "AF_ATTACH_PHASE",
    "NATIVE_SOURCE",
    "OWNER_FACTS_SCHEMA",
    "CID_MEMBERSHIP",
    "_TOOL_PROVENANCE",
    "PREP_REASONS",
    "SUBJECT_ARGV",
    "SUBJECT_GID",
    "SUBJECT_GROUP_VARIANTS",
    "SUBJECT_UID",
    "FixtureError",
    "CidScopedTable",
    "DevptsSlaveMetadata",
    "RealCidScopedTable",
    "GroupMember",
    "DevptsAllocation",
    "DevptsInventory",
    "DevptsObservation",
    "HandoffVerdict",
    "NativeHandoffWorkflow",
    "NativeOwnerFacts",
    "NativeOwnerMeasurement",
    "CompletedOwnerState",
    "OwnedOwnerMeasurement",
    "OwnerFinalFacts",
    "attach_binding_record",
    "ProcStat",
    "ProcTable",
    "RealProcTable",
    "RestorationFacts",
    "StopReceipt",
    "ToolSessionMember",
    "SubjectExpectation",
    "SubjectIdentity",
    "WorkerGroupFacts",
    "argv_digest",
    "collect_stop_observation",
    "derive_attach_allocation",
    "collect_restoration",
    "collect_subject_identity",
    "collect_worker_group",
    "compose_handoff_verdict",
    "expectation_from_owner",
    "expected_tty_nr_qualifies",
    "parse_native_owner_facts",
    "parse_attach_binding_record",
    "parse_devpts_inventory_record",
    "parse_owner_final_facts",
    "parse_proc_cmdline",
    "parse_proc_stat",
    "parse_proc_status",
    "produce_native_owner_record",
    "new_encode_dev",
    "validate_prep_snapshot",
    "validate_subject_identity",
]

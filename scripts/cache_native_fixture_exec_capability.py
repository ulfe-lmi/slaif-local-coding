#!/usr/bin/env python3
"""The sealed-entry Python executable capability driver.

Each SEALED entry is ONE bounded outcome for ONE exact order
namespace.  The historical 017-x entry (the live Python executable
capability, already CONSUMED by its one actual attempt) and the
017-y entry (the closed readiness diagnosis plus the ONE separately
bound Python-only capability attempt of order 017-y) share the SAME
reviewed owner, ledger, END, discovery, measurement and terminal
publication law — no second orchestration stack, no copied
lifecycle.  A measured unknown/refusal is a useful diagnostic
result — never a native-ready or whole-017 success claim.

Closed scope:

- SEALED-launches the one bound owner (exact closed argv; the
  owner IS the supervisor — no second watchdog, no caller launch
  argv) and drives ITS protected interface prepare -> hold ->
  finish in order (the SAME run, ledger, attempt and END — no
  direct-call simulation).  The SEALED CHILD owns
  resolve+admit ONCE before any external work (the
  module-minted run identity is admitted in the child's process);
  the driver only VERIFIES the child's closed protected outputs —
  the published owner state and the stable admission record — and
  never re-resolves, re-mints, adopts or replaces any run id.
- The capability start is the owner's ONE closed detached stand-in
  hold exec (subject uid 21002 on the held prepared exact CID,
  issued 32-hex run marker on argv); ONE subject start in this
  order INCLUDING failed starts.
- The host-side discovery is the bounded exact-CID process
  inventory: the AUTHORITATIVE member list comes from the owner's
  OWN guarded ``top`` command (every query charges the SAME
  ledger/deadline).  The host /proc is NEVER enumerated for
  membership — the host view is consulted per attested pid only,
  and every attested member is verified IN-SCOPE through the
  registered-CID channel before it may be a row (churn counts as
  absent only when the channel INDEPENDENTLY verifies the pid
  gone; an existing-but-unreadable or raced member is a closed
  refusal, never a silent skip; a host pid outside the attested
  list is never a candidate).  At most the fixture pids limit of
  rows; overflow/ambiguous/degraded are closed refusals.  The
  subject is then the issued-marker
  kernel-cmdline correlation (the exact closed hold form, FRESH
  against the pre-launch inventory — a previous attachment is
  never adopted).
- The measurement is the channel's scoped current-executable read
  (at most 16 MiB and at most 10 s, further clamped at MEASUREMENT
  time against the SAME remaining owner END — cleanup grace is
  convergence, not fresh measurement — and the issued hold's own
  finite lifetime; birth binding) with PID/birth/CID/UID/GID
  frame checks BEFORE AND AFTER.  The observed PID/birth/CID/
  UID/GID capability and the executable capability are DISTINCT
  closed fields; one readable field does not prove the other.
- The subject then exits 0 naturally (its own finite hold) and the
  driver polls the channel's tri-state verified-absence primitive
  on a bounded window (no signal, no kill, no watchdog: the
  owner's exact-CID cleanup is the removal path on every
  outcome).  A verified-gone observation proves ABSENCE, not an
  exit code or a natural termination cause: the closed label is
  ``verified-gone`` (``still-present`` / ``unknown`` are distinct
  — a presence is never relabeled as a termination).
- A capability-phase failure before the finish is converged
  through the owner's OWN bounded ``abort`` terminal command over
  the protected interface (the exact-owner convergence — never a
  host signal; the terminal command is ISSUED FIRST, the owner
  then settles and its output is reaped within the SAME budget,
  and the actual issuance is tracked, never derived); the
  owner's retained terminal evidence is then validated with the
  reviewed closed validator BOUND to this exact attempt (order,
  head, run and prepared CID — a valid foreign record is not
  this run's evidence).
- The driver's whole command/wait/measurement budget is the
  owner's OWN published END anchor plus the owner's own single
  allowed cleanup grace — the approved ONE END+grace anchor (an
  expired budget refuses before any blocking wait, and the
  already-exited distinction never authorizes a pass over
  missing or unverified evidence).
- The capability-record destination is checked READ-ONLY
  before anything else: a --record-out at or under the
  disposable work root is a closed refusal (the retained record
  must outlive the scratch root — it must not be destroyed with
  it, nor recreate it after the owner's teardown).
- On a verified owner PASS the driver finalizes the bound
  attempt's terminal pass with the W publication ordering: the
  validated protected owner evidence first, then the driver's
  own protected capability-record retention (the actual
  qualification retains its record — a refusal closes the
  returned record as fail with NO journal pass and NO fresh-path
  retry), and only then the verified same-attempt terminal
  finalization (an unverified token never returns a qualified
  success).  The journal is evidence, not a gate on cleanup.
- The driver's own closed result record is the capability scope
  and is retained at a protected destination (the reviewed
  protected-path/atomic-no-overwrite retention: ancestors
  validated as given, fresh 0600 same-directory temporary,
  digest-verified, atomic link commit, temp-only cleanup).

The driver NEVER signals the owner or the subject.  A driver death
leaves the independently running owner to its own finite END.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
import stat as stat_mod
import subprocess
import sys
import threading
import time
from collections.abc import Callable
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cache_native_fixture_binding as oap_binding  # noqa: E402
import cache_native_fixture_ci as ci  # noqa: E402
import cache_native_fixture_local as flocal  # noqa: E402
import cache_native_fixture_model as model  # noqa: E402
import cache_native_fixture_native_prep as fp  # noqa: E402
import cache_native_fixture_runtime_profile as rprofile  # noqa: E402
import cache_native_fixture_standin as standin  # noqa: E402

FixtureError = ci.FixtureError

ORDER_ID = "017-x"
ORDER_PATH = "oap/orders/017-x-live-python-executable-capability.md"
DRIVER_RECORD = "slaif-017x-exec-capability-driver-v1"


class _SealedEntry:
    """ONE explicit sealed entry: the exact order id, the unique
    committed order path at the bound head and the DISTINCT closed
    driver-record tag.  A record is paired ONLY with its entry's
    order (the validator checks both); Y evidence is never labeled
    X and a foreign record is never adopted as this run."""

    __slots__ = ("order_id", "order_path", "record_tag")

    def __init__(self, order_id: str, order_path: str, record_tag: str) -> None:
        self.order_id = order_id
        self.order_path = order_path
        self.record_tag = record_tag


# The explicit sealed entries (historical S and X semantics are
# unchanged; 017-y is the ONE new entry of its order).
_SEALED_ENTRIES: dict[str, _SealedEntry] = {
    "017-x": _SealedEntry("017-x", ORDER_PATH, DRIVER_RECORD),
    "017-y": _SealedEntry(
        "017-y",
        "oap/orders/017-y-readiness-diagnosis-and-executable-capability.md",
        "slaif-017y-exec-capability-driver-v1",
    ),
    # The canonical INACTIVE future entry (017-aa order): a
    # distinct driver-record tag selecting ONLY the owner-UID
    # profile.  Registering it is NOT activating it: under the
    # current active order the real repository-context validation
    # refuses 017-ab before external fixture work or admission;
    # the hermetic synthetic repositories are the only contexts
    # where the AB entry resolves.
    "017-ab": _SealedEntry(
        rprofile.AB_ORDER_ID,
        rprofile.AB_ORDER_PATH,
        rprofile.AB_DRIVER_RECORD,
    ),
}

#: The default entry (the historical 017-x path) — every pre-017-y
#: call site keeps its original X meaning byte-for-byte.
_ENTRY_X = _SEALED_ENTRIES["017-x"]

#: The CLOSED canonical sealed-entry triples the record/admission
#: CONSUMERS trust.  A caller may construct arbitrary _SealedEntry
#: fixtures (tests do), but a consumer — record validation,
#: admission verification, terminal journal finalization — must be
#: byte-equal to one of these known (order id, order path, record
#: tag) triples: retention/qualification never accepts a
#: caller-created pair expectation, and a retained record is valid
#: only under its canonical entry.
_CANONICAL_SEALED_TRIPLES: frozenset[tuple[str, str, str]] = frozenset(
    (e.order_id, e.order_path, e.record_tag) for e in _SEALED_ENTRIES.values()
)


def _require_canonical_entry(entry: _SealedEntry) -> _SealedEntry:
    """The closed consumer gate: the entry descriptor must be
    byte-equal to a known canonical sealed entry; a caller-created
    pair (any other order id, path or record tag, including a
    known order paired with the WRONG tag) is refused."""
    if (entry.order_id, entry.order_path, entry.record_tag) not in _CANONICAL_SEALED_TRIPLES:
        raise FixtureError("cap-sealed-entry")
    return entry


#: The subject identity (the reviewed container uid/gid).
SUBJECT_UID = model.SUBJECT_UID  # 21002

#: The scoped current-executable read bounds (order 017-x): at
#: most 16 MiB and at most 10 s, further capped by the SAME
#: remaining owner budget at channel construction.
EXE_MAX_BYTES = 16 * 1024 * 1024
EXE_DEADLINE_SECONDS = 10.0

#: The closed inventory bound (order 017-x): at most the fixture
#: pids limit of rows.  The authoritative member list is the
#: OWNER's guarded ``docker top`` attestation — the host /proc is
#: never enumerated for membership; the host view is consulted
#: PER ATTESTED PID only (the channel's scoped reads and the
#: tri-state verified-absence primitive).
INVENTORY_ROWS_MAX = model.PIDS_LIMIT  # 96

#: The bounded host-side windows (all charged against the SAME
#: owner END+grace anchor; none is a fresh phase budget): the
#: dispatched subject must APPEAR within the scan window, and the
#: natural-exit wait is the subject's own 20 s hold bound plus one
#: closed margin.
SUBJECT_SCAN_WINDOW_SECONDS = 10.0
SUBJECT_POLL_SECONDS = 0.25
EXIT_WAIT_MARGIN_SECONDS = 5.0
#: The subject's own finite hold bound (the reviewed stand-in
#: constant — the ONE source of truth for the issued hold's
#: lifetime, used to clamp the executable read and the natural-
#: exit observation; never a driver-minted second budget).
STANDIN_HOLD_MAX_SECONDS = standin.HOLD_MAX_SECONDS
#: The bounded race re-attestation: a RACE-class discovery fault
#: (unverified churn/membership or a degraded scoped read) is
#: re-queried ONCE through the owner's authoritative inventory
#: before the closed refusal stands (stable malformed/invalid
#: states are never retried).
INVENTORY_RACE_REASONS = ("cap-inventory-unverified", "cap-proc-scan-degraded")

#: The closed capability vocabularies (distinct capabilities):
#: ``measured`` — every scoped read of that capability succeeded
#: and was frame-coherent; ``unknown`` — the scoped observation
#: was unreadable/absent (an unprovable fact, never a verified
#: negative); ``refused`` — a closed refusal (identity mismatch,
#: frame race, over-bound, timed out, vanished);
#: ``not-measured`` — the phase was never reached.
PROCESS_IDENTITY_STATES = ("measured", "unknown", "refused", "not-measured")
EXECUTABLE_STATES = ("measured", "unknown", "refused", "not-measured")
# The subject-exit vocabulary: ``verified-gone`` is the channel's
# tri-state VERIFIED ABSENCE (the pid entry itself is gone) — it
# proves absence, never an exit code or a natural termination
# cause (there is no separately measured exit provenance here);
# ``still-present`` and ``unknown`` are distinct closed states,
# and ``not-observed`` marks a subject that never appeared.
SUBJECT_EXIT_STATES = ("verified-gone", "still-present", "unknown", "not-observed")

#: The exact closed kernel-cmdline form of the hold subject (the
#: correlation identity; the issued marker is the final element).
_HOLD_FORM_HEAD = ("python3", ci.STANDIN_PATH, "--mode", "hold", "--hold-token")


# -- bounded exact-CID discovery ---------------------------------------------------
def discover_inventory(
    channel: fp.CidScopedTable,
    proc_root: Path,
    attested_pids: list[int],
    *,
    token: str | None,
) -> list[dict[str, object]]:
    """The bounded measured process inventory of the EXACT owned
    CID, cross-checked against the OWNER's authoritative
    attestation (the guarded ``top`` member list — every query
    charged the SAME owner ledger/deadline):

    - the attested list IS the closed membership authority
      (distinct positive pids, at most the fixture pids limit) —
      the host /proc is NEVER enumerated for membership and no
      host pid outside the attestation is consulted;
    - EVERY attested member is verified IN-SCOPE through the
      registered-CID channel before it may be a row (a host pid
      plus a matching string is NOT membership); its scoped reads
      (stat/cmdline/status) compose the row;
    - an attested member whose pid entry is gone counts as ABSENT
      only when the channel INDEPENDENTLY verifies the pid gone
      (the tri-state verified-absence primitive); a member that
      exists on the host but is no longer in the registered scope
      (raced membership / pid reuse), or whose scoped reads are
      unreadable (degraded scan), is a closed refusal — never a
      silent skip;
    - a race-class refusal (unverified churn/membership or a
      degraded scoped read) may be re-attested ONCE by the caller
      (a fresh authoritative inventory + fresh scoped reads); a
      stable malformed/invalid state is never retried.

    The closed row summary retains NO raw content: pid, immutable
    birth, uid/gid/groups, and whether the exact closed hold form
    (with THIS token) is the entire cmdline."""
    if not isinstance(attested_pids, list) or not (1 <= len(attested_pids) <= INVENTORY_ROWS_MAX):
        raise FixtureError("cap-inventory-attestation-invalid")
    if len(set(attested_pids)) != len(attested_pids) or any(
        not isinstance(p, int) or isinstance(p, bool) or p <= 0 for p in attested_pids
    ):
        raise FixtureError("cap-inventory-attestation-invalid")
    attested = set(attested_pids)
    rows: list[dict[str, object]] = []
    for pid in sorted(attested):
        try:
            os.lstat(proc_root / str(pid))
        except FileNotFoundError:
            # churn candidate: ABSENT only when the channel
            # INDEPENDENTLY verifies the pid gone (True); an
            # unreadable or still-scoped entry is never absent.
            if channel.pid_present(pid) is not True:
                raise FixtureError("cap-inventory-unverified") from None
            continue
        except OSError:
            raise FixtureError("cap-proc-scan-degraded") from None
        if channel.cgroup_scope(pid) is None:
            # the entry exists on the host but the registered
            # scope is unreadable or no longer ours: raced
            # membership (pid reuse/escape) — a closed refusal.
            raise FixtureError("cap-inventory-unverified") from None
        raw_stat = channel.stat(pid)
        raw_cmdline = channel.cmdline(pid)
        raw_status = channel.status(pid)
        if raw_stat is None or raw_cmdline is None or raw_status is None:
            # the entry exists and is in scope, yet its scoped
            # reads are unreadable: a degraded scan — a closed
            # refusal, never a silent skip.
            raise FixtureError("cap-proc-scan-degraded") from None
        try:
            ps = fp.parse_proc_stat(raw_stat.decode("ascii", "replace"))
            argv = fp.parse_proc_cmdline(raw_cmdline)
            uid, gid, groups = fp.parse_proc_status(raw_status)
        except FixtureError:
            raise FixtureError("cap-proc-scan-malformed") from None
        if ps.pid != pid:
            raise FixtureError("cap-proc-scan-malformed")
        closed_form = bool(
            token is not None
            and len(argv) == len(_HOLD_FORM_HEAD) + 1
            and argv[: len(_HOLD_FORM_HEAD)] == _HOLD_FORM_HEAD
            and re.fullmatch(r"[0-9a-f]{32}", argv[-1]) is not None
            and argv[-1] == token
        )
        rows.append(
            {
                "pid": pid,
                "birth": ps.start_time,
                "uid": uid,
                "gid": gid,
                "groups": list(groups),
                "closed_hold_form": closed_form,
            }
        )
    return rows


def correlate_subject(
    pre_rows: list[dict[str, object]],
    post_rows: list[dict[str, object]],
    token: str,
    *,
    expected_subject: tuple[int, int, tuple[int, ...]] | None = None,
) -> tuple[dict[str, object] | None, str]:
    """The issued-marker correlation: the subject is the EXACTLY
    ONE post row in the exact closed hold form (this token) that
    is FRESH — absent from the pre-launch inventory (a previous
    attachment's pid is never adopted).  Zero candidates is
    ``not-observed`` (retry within the bounded window); more than
    one is ``ambiguous`` (a closed refusal — the driver never
    silently selects the first candidate); a candidate that does
    not carry the subject identity law is a closed refusal.

    ``expected_subject`` carries the FROZEN owner identity the
    canonical 017-ab entry adopted from the owner's own
    protected state (the closed structural law — never
    caller-authored): ``(uid, gid, groups)`` where the third
    member is the expected EFFECTIVE groups (the structural law
    fixes it to exactly the primary GID).  The raw measured
    supplementary vector law is independent of that: the closed
    subject form carries either the EMPTY supplementary vector
    or exactly the primary GID — a foreign, duplicate or other
    vector is refused.  The default (``None``) keeps the
    historical fixed-21002 law byte-for-byte for the X/Y
    entries; the physical owner-UID facts are validated as-is,
    NEVER normalized to 21002."""
    if not re.fullmatch(r"[0-9a-f]{32}", token):
        raise FixtureError("cap-token-invalid")
    if expected_subject is None:
        expected_uid, expected_gid = SUBJECT_UID, SUBJECT_UID
    else:
        expected_uid, expected_gid, _expected_groups = expected_subject
    group_law = ((), (expected_gid,))
    pre_pids = {row["pid"] for row in pre_rows}
    candidates = [
        row for row in post_rows if row["closed_hold_form"] is True and row["pid"] not in pre_pids
    ]
    if not candidates:
        return None, "not-observed"
    if len(candidates) > 1:
        return None, "ambiguous"
    row = candidates[0]
    if row["uid"] != expected_uid or row["gid"] != expected_gid:
        return None, "identity-mismatch"
    if tuple(row["groups"]) not in group_law:
        return None, "groups-law"
    return row, "correlated"


# -- the scoped live measurement ----------------------------------------------------
def _scoped_identity(
    channel: fp.CidScopedTable, pid: int
) -> tuple[fp.ProcStat, tuple[str, ...], int, int, tuple[int, ...]]:
    raw_stat = channel.stat(pid)
    raw_cmdline = channel.cmdline(pid)
    raw_status = channel.status(pid)
    if raw_stat is None or raw_cmdline is None or raw_status is None:
        raise FixtureError("cap-subject-vanished")
    try:
        ps = fp.parse_proc_stat(raw_stat.decode("ascii", "replace"))
        argv = fp.parse_proc_cmdline(raw_cmdline)
        uid, gid, groups = fp.parse_proc_status(raw_status)
    except FixtureError:
        raise FixtureError("cap-subject-malformed") from None
    if ps.pid != pid:
        raise FixtureError("cap-subject-malformed")
    return ps, argv, uid, gid, groups


def measure_live_subject(
    channel: fp.CidScopedTable,
    pid: int,
    discovered_birth: int,
    *,
    token: str,
    expected_subject: tuple[int, int, tuple[int, ...]] | None = None,
) -> dict[str, object]:
    """The scoped current-executable measurement with the frame
    law: BEFORE and AFTER the executable read, the (pid, birth)
    identity, the exact closed hold cmdline (this token) and the
    UID/GID/group law must still hold — a contradictory later
    read is never stamped onto the measured digest.  The two
    capabilities stay DISTINCT: a vanished or mismatched frame is
    a process-identity refusal (and stops the proof — the
    executable is then never earned), while an unreadable/absent
    exe link with a COHERENT frame is an executable UNKNOWN with
    the process identity still measured.  The channel's bounded
    read budget (at most 16 MiB and at most 10 s, further capped
    by the SAME remaining owner budget at construction) applies
    to the executable read itself.

    ``expected_subject`` threads the FROZEN 017-ab owner
    identity (the closed structural law from the owner's own
    protected state) into the pre- and post-read frame law; the
    default keeps the historical fixed-21002 law byte-for-byte
    (the owner-UID facts are validated as-is, never normalized
    to 21002).  The raw supplementary vector law is the SAME
    closed form as the correlation: the empty vector or exactly
    the primary GID (the third member of the frozen tuple is the
    expected EFFECTIVE groups — exactly the primary GID by the
    structural law — and is not itself the set of allowed raw
    vectors)."""
    if expected_subject is None:
        expected_uid, expected_gid = SUBJECT_UID, SUBJECT_UID
    else:
        expected_uid, expected_gid, _expected_groups = expected_subject
    group_law = ((), (expected_gid,))
    try:
        ps, argv, uid, gid, groups = _scoped_identity(channel, pid)
    except FixtureError:
        return {
            "process_identity": "refused",
            "executable": "not-measured",
            "executable_sha256": None,
        }
    if (
        ps.start_time != discovered_birth
        or uid != expected_uid
        or gid != expected_gid
        or tuple(groups) not in group_law
        or len(argv) != len(_HOLD_FORM_HEAD) + 1
        or argv[: len(_HOLD_FORM_HEAD)] != _HOLD_FORM_HEAD
        or argv[-1] != token
    ):
        return {
            "process_identity": "refused",
            "executable": "not-measured",
            "executable_sha256": None,
        }
    try:
        digest = channel.exe_sha256(pid, ps.start_time)
    except FixtureError:
        digest = None
    executable: str
    if digest is None:
        # The exe link is absent/unmeasurable: a closed UNKNOWN,
        # never a verified negative and never an earned digest —
        # the executable capability proof stops here (the process
        # identity, measured on a coherent frame, stands apart).
        executable = "unknown"
    else:
        executable = "measured"
    try:
        ps2, argv2, uid2, gid2, groups2 = _scoped_identity(channel, pid)
    except FixtureError:
        # The frame raced AFTER the measurement: the recorded
        # identity is no longer the measured process; the digest
        # is never stamped on a contradicting frame.
        return {
            "process_identity": "refused",
            "executable": "not-measured",
            "executable_sha256": None,
        }
    if (
        ps2.pid != pid
        or ps2.start_time != ps.start_time
        or argv2 != argv
        or (uid2, gid2, groups2) != (uid, gid, tuple(groups))
    ):
        return {
            "process_identity": "refused",
            "executable": "not-measured",
            "executable_sha256": None,
        }
    return {
        "process_identity": "measured",
        "executable": executable,
        "executable_sha256": digest,
    }


def wait_natural_exit(channel: fp.CidScopedTable, pid: int, *, bound: float) -> str:
    """The bounded natural-exit observation: poll the channel's
    tri-state verified-absence primitive (True = the entry is
    VERIFIED gone; False = still present in the registered
    container; None = the entry exists but is unreadable — an
    unknown, never a verified absence).  No signal, no kill, no
    watchdog: the subject exits on its own finite hold and the
    owner's exact-CID cleanup is the removal path on every
    outcome.  The closed result is HONEST about what was
    observed: a verified absence is ``verified-gone`` (absence
    only — no exit code or natural-termination provenance is
    claimed), a last observed presence is ``still-present``, a
    last observed unknown entry is ``unknown``.  The bound is the
    subject's own 20 s hold bound plus one closed margin, capped
    by the SAME remaining owner budget; an expired window reports
    what was last observed, honestly."""
    if (
        not isinstance(bound, (int, float))
        or isinstance(bound, bool)
        or not math.isfinite(bound)
        or bound < 0
    ):
        raise FixtureError("cap-exit-bound-invalid")
    deadline = time.monotonic() + float(bound)
    last: bool | None = None
    while True:
        last = channel.pid_present(pid)
        if last is True:
            return "verified-gone"
        if time.monotonic() >= deadline:
            return "unknown" if last is None else "still-present"
        time.sleep(min(SUBJECT_POLL_SECONDS, max(0.0, deadline - time.monotonic())))


# -- the public driver ----------------------------------------------------------------
def _driver_record(
    status: str,
    reason: str | None,
    *,
    bind_head: str,
    run_id: str | None = None,
    owner_exit: int | None = None,
    evidence_sha256: str | None = None,
    capability: dict[str, object] | None = None,
    identity: dict[str, object] | None = None,
    entry: _SealedEntry = _ENTRY_X,
) -> dict[str, object]:
    """The driver's CLOSED result record.  The terminal composition
    adds the separate cleanup/exit/evidence/finalization FACTS
    (the ``terminal_command`` / ``evidence_state`` / ``reader_state``
    / ``finalize`` / ``retention`` keys) without ever overwriting
    the PRIMARY phase ``reason``; the closed validator below
    accepts exactly this shape.  The record tag and order are
    paired to the entry (the historical X call sites keep the X
    entry by default, byte-for-byte).  ``identity`` carries the
    FROZEN owner identity the canonical 017-ab entry adopted from
    the owner's own protected state (the SAME closed substructure
    the AB state/evidence carry — None for the X/Y entries, which
    never carry it; a retained AB record binds its measured
    subject to this retained identity, never to a caller-authored
    expectation)."""
    record = {
        "record": entry.record_tag,
        "status": status,
        "reason": reason,
        "order": entry.order_id,
        "bind_head": bind_head,
        "run_id": run_id,
        "owner_exit": owner_exit,
        "evidence_sha256": evidence_sha256,
        "capability": capability,
        "terminal_command": "none",
        "evidence_state": "not-verified",
        "reader_state": "not-observed",
        "capture_state": "not-observed",
        "finalize": "not-attempted",
        "retention": "not-requested",
    }
    # The DISTINCT closed key sets per entry: the X/Y entries
    # keep the historical key set byte-for-byte (a caller attempt
    # to attach an owner identity to an X/Y record is a closed
    # producer refusal — the old grammar is never widened); the
    # canonical AB entry carries the historical keys PLUS the
    # identity (None BEFORE the owner state is adopted — a useful
    # closed fact on startup failures — and the frozen substructure
    # after).
    if entry.order_id == rprofile.AB_ORDER_ID:
        record["identity"] = identity
    elif identity is not None:
        raise FixtureError("cap-record-identity")
    return record


def _validate_capability_record(record: object, entry: _SealedEntry = _ENTRY_X) -> None:
    """The closed capability-record grammar (the retained record is
    closed, not free-form): the exact key set, the fixed tags and
    grammars, and the process/executable STATE COHERENCE (a
    ``measured`` executable is a measured 64-hex digest and nothing
    else; any non-measured state carries NO digest; a measured
    process identity implies an observed subject).  Retention
    refuses any record outside this grammar — never a weaker
    schema."""
    # the CLOSED consumer gate FIRST: a caller-created entry
    # descriptor (any non-canonical order/path/tag triple) is
    # refused before any field is trusted
    _require_canonical_entry(entry)
    if not isinstance(record, dict):
        raise FixtureError("cap-record-schema")
    expected = {
        "record",
        "status",
        "reason",
        "order",
        "bind_head",
        "run_id",
        "owner_exit",
        "evidence_sha256",
        "capability",
        "terminal_command",
        "evidence_state",
        "reader_state",
        "capture_state",
        "finalize",
        "retention",
    }
    if (
        set(record)
        != (expected | {"identity"} if entry.order_id == rprofile.AB_ORDER_ID else expected)
        or record["record"] != entry.record_tag
        or record["status"] not in ("pass", "fail")
        or record["order"] != entry.order_id
        or not isinstance(record["bind_head"], str)
        or re.fullmatch(r"[0-9a-f]{40}", record["bind_head"]) is None
        or (
            record["run_id"] is not None
            and (
                not isinstance(record["run_id"], str)
                or re.fullmatch(r"[0-9a-f]{32}", record["run_id"]) is None
            )
        )
        or (
            record["reason"] is not None
            and (not isinstance(record["reason"], str) or not record["reason"])
        )
        or (record["status"] == "pass" and record["reason"] is not None)
        or (
            record["owner_exit"] is not None
            and (
                not isinstance(record["owner_exit"], int) or isinstance(record["owner_exit"], bool)
            )
        )
        or (
            record["evidence_sha256"] is not None
            and (
                not isinstance(record["evidence_sha256"], str)
                or re.fullmatch(r"[0-9a-f]{64}", record["evidence_sha256"]) is None
            )
        )
        or record["terminal_command"] not in ("none", "abort", "finish")
        or record["evidence_state"]
        not in (
            "not-verified",
            "verified-pass",
            "verified-fail",
            "invalid",
            "missing",
        )
        or record["reader_state"] not in ("drained", "held", "not-observed")
        or record["capture_state"] not in ("not-observed", "drained", "cap", "read-error")
        or record["finalize"]
        not in (
            "not-attempted",
            "finalized",
            "terminal-preserved",
            "not-running",
            "record-unreadable",
            "failed",
        )
        or record["retention"] not in ("not-requested", "retained", "refused")
    ):
        raise FixtureError("cap-record-schema")
    # the entry-aware frozen-identity law: the closed key sets
    # above already keep the X/Y records byte-for-byte the
    # historical form (no identity key at all — the old grammar
    # is never widened); the canonical AB entry carries the SAME
    # closed substructure its state/evidence carry, closed-
    # validated here by the shared structural core (None before
    # the owner state is adopted; a valid caller-authored copy is
    # still only data — the driver's adoption from the owner's
    # own protected state is what binds it, and the terminal
    # cross-checks the owner's retained evidence identity against
    # it).
    identity = record.get("identity")
    if (
        entry.order_id == rprofile.AB_ORDER_ID
        and identity is not None
        and flocal._identity_substructure_law(identity) is None
    ):
        raise FixtureError("cap-record-schema")
    cap = record["capability"]
    # the AB pass coherence: a RETAINED AB pass is the qualified
    # determination of the canonical entry — it must carry the
    # ADOPTED frozen identity AND the actual capability result
    # (an unknown current executable is still a valid useful
    # result; a missing capability or identity is not).  The
    # pre-state startup FAIL may honestly carry both unknowns
    # (the refusal happened before any adoption or measurement).
    if (
        entry.order_id == rprofile.AB_ORDER_ID
        and record["status"] == "pass"
        and (identity is None or cap is None)
    ):
        raise FixtureError("cap-record-state")
    if cap is None:
        return
    if (
        not isinstance(cap, dict)
        or set(cap)
        != {
            "cid",
            "subject",
            "process_identity",
            "executable",
            "executable_sha256",
            "pre_inventory_rows",
            "post_inventory_rows",
            "inventory_rows_max",
            "subject_exit",
        }
        or (
            cap["cid"] is not None
            and (
                not isinstance(cap["cid"], str) or re.fullmatch(r"[0-9a-f]{64}", cap["cid"]) is None
            )
        )
        or cap["process_identity"] not in PROCESS_IDENTITY_STATES
        or cap["executable"] not in EXECUTABLE_STATES
        or (
            cap["executable_sha256"] is not None
            and (
                not isinstance(cap["executable_sha256"], str)
                or re.fullmatch(r"[0-9a-f]{64}", cap["executable_sha256"]) is None
            )
        )
        or (
            not isinstance(cap["pre_inventory_rows"], int)
            or isinstance(cap["pre_inventory_rows"], bool)
            or cap["pre_inventory_rows"] < 0
        )
        or (
            cap["post_inventory_rows"] is not None
            and (
                not isinstance(cap["post_inventory_rows"], int)
                or isinstance(cap["post_inventory_rows"], bool)
                or cap["post_inventory_rows"] < 0
            )
        )
        or cap["inventory_rows_max"] != INVENTORY_ROWS_MAX
        or cap["subject_exit"] not in SUBJECT_EXIT_STATES
    ):
        raise FixtureError("cap-record-schema")
    subject = cap["subject"]
    if subject is not None and (
        not isinstance(subject, dict)
        or set(subject) != {"pid", "birth", "uid", "gid", "groups"}
        or any(
            not isinstance(subject[k], int) or isinstance(subject[k], bool)
            for k in ("pid", "birth", "uid", "gid")
        )
        or not isinstance(subject["groups"], list)
        or not all(isinstance(g, int) and not isinstance(g, bool) for g in subject["groups"])
    ):
        raise FixtureError("cap-record-schema")
    # the state coherence: the digest grammar agrees with the
    # measured executable state (a measured digest implies the
    # process identity was measured AND an observed subject), the
    # ENTRY-AWARE subject identity law (the X/Y entries keep the
    # fixed 21002 uid/gid byte-for-byte; the AB entry binds the
    # measured subject to the RETAINED frozen identity — the
    # physical 1001-class facts are validated as-is, never
    # normalized to 21002 — with the SAME raw supplementary
    # vector law: the empty vector or exactly the primary GID; an
    # AB record without the retained identity can never carry a
    # measured subject), positive pid, non-negative birth, the
    # registered CID bound) and the inventory bounds (at most 96
    # rows; an observed subject implies a non-empty post
    # inventory).
    ab_entry = entry.order_id == rprofile.AB_ORDER_ID
    if ab_entry and identity is None and subject is not None:
        raise FixtureError("cap-record-state")
    if (
        (cap["executable"] == "measured") != (cap["executable_sha256"] is not None)
        or (cap["executable"] == "measured" and cap["process_identity"] != "measured")
        or (cap["process_identity"] == "measured" and subject is None)
        or (subject is not None and cap["cid"] is None)
        or (
            subject is not None
            and (
                subject["pid"] <= 0
                or subject["birth"] < 0
                or (
                    ab_entry
                    and (
                        subject["uid"] != identity["subject_uid"]
                        or subject["gid"] != identity["subject_gid"]
                        or tuple(subject["groups"])
                        not in ((), (identity["subject_gid"],))
                    )
                )
                or (
                    not ab_entry
                    and (
                        subject["uid"] != SUBJECT_UID
                        or subject["gid"] != SUBJECT_UID
                        or tuple(subject["groups"]) not in ((), (SUBJECT_UID,))
                    )
                )
            )
        )
        or (
            cap["pre_inventory_rows"] > INVENTORY_ROWS_MAX
            or (
                cap["post_inventory_rows"] is not None
                and cap["post_inventory_rows"] > INVENTORY_ROWS_MAX
            )
        )
        or (
            subject is not None
            and (
                cap["post_inventory_rows"] is None
                or cap["post_inventory_rows"] < 1
                or cap["subject_exit"] == "not-observed"
            )
        )
    ):
        raise FixtureError("cap-record-state")


def build_channel(cid: str, remaining: float) -> fp.CidScopedTable:
    """The REAL scoped measurement channel bound to the exact
    registered CID with the 017-x executable bounds: at most 16
    MiB and at most 10 s, further capped by the SAME remaining
    owner budget (never a fresh phase deadline).  The caller must
    pass the budget clamped at USE time — for the executable read
    that is the remaining owner END (cleanup grace is convergence,
    not fresh measurement) intersected with the issued hold's own
    finite lifetime."""
    if (
        not isinstance(remaining, (int, float))
        or isinstance(remaining, bool)
        or not math.isfinite(remaining)
        or remaining <= 0
    ):
        raise FixtureError("cap-channel-budget-invalid")
    return fp.RealCidScopedTable(
        cid,
        max_exe_bytes=EXE_MAX_BYTES,
        exe_deadline=min(EXE_DEADLINE_SECONDS, float(remaining)),
    )


def _retain_record(
    record: dict[str, object], record_out: Path, entry: _SealedEntry = _ENTRY_X
) -> None:
    """The protected capability-record retention for the SEALED
    entry: the closed
    record grammar is validated FIRST, then the reviewed
    protected-path/atomic-no-overwrite publisher is REUSED as the
    single implementation (ancestors validated as given — no
    traversal, no link alias, no untrusted or group/other-writable
    intermediate; fresh 0700 components for a missing parent
    chain; the 0600 leaf; the complete byte/digest checks BEFORE
    the atomic same-directory link commit; a pre-existing
    destination or a raced appearance is a closed refusal, never
    an overwrite; a failed step removes only this invocation's own
    temporary, so the final path is either absent or the verified
    committed file).  The retention refusal is closed and honest:
    the caller reports it, never silently drops the record, and
    never retries a fresh path.  The disposable work root is NOT
    a destination of this retention: the driver's read-only
    preflight refuses a record destination at or under it BEFORE
    any launch (the retained record must outlive the scratch
    root), so the publisher here sees only destinations outside
    the work root."""
    # the record's tag/order are validated AGAINST the entry
    # (the gate refuses a caller-created descriptor FIRST); the
    # historical X call sites keep the X entry by default
    _validate_capability_record(record, entry)
    payload = (json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n").encode("ascii")
    digest = hashlib.sha256(payload).hexdigest()
    ci._retain_evidence(record_out, payload, digest)


def _verify_bound_admission(
    repo: Path, bind_head: str, run_id: str, entry: _SealedEntry = _ENTRY_X
) -> None:
    """The driver's binding verification (VERIFICATION, never
    adoption): the sealed child owns resolve+admit — the
    driver's closed protected reads must agree that the owner's
    published run id is EXACTLY the ONE attempt of this order,
    at this literal head, still running.  Any other shape —
    missing, foreign, terminal, or an extra attempt — is a
    closed refusal: an arbitrary running journal entry is never
    adopted, no run id is replaced, and no admission is weakened."""
    _require_canonical_entry(entry)
    record = oap_binding.read_admission_record(repo, entry.order_id)
    attempts = record["attempts"]
    if (
        len(attempts) != 1
        or attempts[0]["head"] != bind_head
        or attempts[0]["status"] != "running"
        or attempts[0]["run_id"] != run_id
    ):
        raise FixtureError("cap-binding-mismatch")


def run_exec_capability(
    repo,
    bind_head: str,
    work,
    control_dir,
    evidence_out,
    *,
    channel_factory: Callable[[str, float], fp.CidScopedTable] | None = None,
    proc_root: Path | None = None,
    record_out: Path | None = None,
    entry: _SealedEntry = _ENTRY_X,
) -> dict[str, object]:
    """The ONE bounded capability experiment of the sealed entry
    (the historical 017-x entry by default; 017-y under its own
    entry): SEALED-launch
    the bound owner (the child owns resolve+admit of the order's
    ONE attempt), verify the closed protected outputs, then drive
    prepare -> hold -> finish with the host-side bounded exact-CID
    discovery and the scoped live measurement BETWEEN the hold
    start and the finish.  The driver's pass means the bounded
    experiment completed to a closed TRUTHFUL conclusion (the
    ``capability`` fields carry the actual determination — a
    measured unknown/refusal is a useful diagnostic, never a
    readiness claim); a workflow fault is a closed fail record.
    The driver never signals the owner or the subject; a driver
    death leaves the owner to its own finite END."""
    repo = Path(repo)
    work = Path(work)
    control_dir = Path(control_dir)
    evidence_out = Path(evidence_out)
    root = Path(proc_root) if proc_root is not None else Path("/proc")
    factory = channel_factory if channel_factory is not None else build_channel
    # the CLOSED consumer gate at the public entry: a caller-created
    # pair expectation is refused BEFORE any launch, command or
    # mutation (the factory may construct fixtures; the driver never
    # adopts them)
    _require_canonical_entry(entry)

    # -- the capability-record destination (read-only preflight) --
    # The retained record must OUTLIVE the disposable work root: a
    # destination at or under it would be destroyed with the scratch
    # (or worse, recreate the destroyed root after the owner's
    # teardown) and reported retained dishonestly.  The refusal is
    # closed and read-only, BEFORE any launch, command or mutation.
    # This preflight is the driver's enforcement of the work-root
    # boundary for its own record: both paths are normalized to
    # absolute LEXICAL paths with the same cwd convention as the
    # publisher (no symlink or alias resolution), so a relative
    # work and/or destination cannot bypass the comparison.  The
    # standalone retention contract of the publisher (explicitly
    # owned destinations, no work root known to the caller) is
    # unchanged.
    if record_out is not None:
        _dest = Path(record_out)
        if not _dest.is_absolute():
            _dest = Path(os.getcwd()) / _dest
        _work = work if work.is_absolute() else Path(os.getcwd()) / work
        try:
            _dest.relative_to(_work)
        except ValueError:
            pass
        else:
            return _driver_record(
                "fail", "record-out-inside-work", bind_head=bind_head, entry=entry
            )

    # -- the fresh protected bootstrap (startup authority, layer 1) --
    # The control root is owned by THIS run's sealed child: the
    # owner creates it fresh at serve start.  A pre-existing root is
    # a prior/foreign owner's terminal/control surface — it is
    # never adopted: no child is launched, no command is issued,
    # no journal entry is mutated.
    if control_dir.exists() or control_dir.is_symlink():
        return _driver_record("fail", "local-control-exists", bind_head=bind_head, entry=entry)

    # -- the sealed owner launch (the same independence law) ------------------
    argv = flocal._owner_argv(
        str(Path(flocal.__file__).resolve()),
        bind_head,
        repo,
        work,
        control_dir,
        evidence_out,
        # The SEALED entry's order id: the historical 017-x entry
        # keeps the 017-x sealed child; 017-y admits in its OWN
        # distinct namespace (no adoption of the consumed X one).
        order=entry.order_id,
    )
    captured: bytearray = bytearray()
    captured_total = 0
    # The ACTUAL capture state (a shared live holder — the terminal
    # decision reads it AFTER the reader is drained, so a cap hit or
    # pipe read error discovered during the final drain is visible;
    # either fault is a closed driver fault, never a silently
    # drained capture):
    capture_state_box: list[str] = ["drained"]
    try:
        proc = subprocess.Popen(
            argv,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
    except OSError:
        return _driver_record("fail", "local-driver-launch", bind_head=bind_head, entry=entry)

    def _capture() -> None:
        nonlocal captured_total
        assert proc.stdout is not None
        try:
            try:
                while captured_total < flocal._DRIVER_CAPTURE_MAX:
                    chunk = proc.stdout.read(
                        min(65536, flocal._DRIVER_CAPTURE_MAX - captured_total)
                    )
                    if not chunk:
                        break
                    captured_total += len(chunk)
                    if len(captured) < 16384:
                        captured.extend(chunk[: 16384 - len(captured)])
                else:
                    capture_state_box[0] = "cap"
            except OSError:
                capture_state_box[0] = "read-error"
        finally:
            try:
                proc.stdout.close()
            except OSError:
                pass

    reader = threading.Thread(target=_capture, daemon=True)
    reader.start()

    def _settled() -> bool:
        reader.join(5.0)
        return not reader.is_alive()

    def _reap_bounded() -> int | None:
        try:
            return proc.wait(timeout=flocal._DRIVER_STARTUP_REAP_SECONDS)
        except subprocess.TimeoutExpired:
            return proc.returncode

    def _startup_record(reason: str, owner_exit: int | None) -> dict[str, object]:
        settled = _settled()
        record = _driver_record(
            "fail",
            reason,
            bind_head=bind_head,
            run_id=None,
            owner_exit=owner_exit,
            entry=entry,
        )
        # the ACTUAL reader state (the bounded settle did drain the
        # output when the child exited; a still-running child leaves
        # the reader holding the pipe)
        record["reader_state"] = "drained" if settled else "held"
        return record

    run_id: str | None = None
    end = time.monotonic() + flocal._CONTROL_STARTUP_TIMEOUT
    while time.monotonic() < end:
        if proc.poll() is not None:
            break
        state = flocal._state_record(control_dir, entry_order=entry.order_id)
        if state is not None:
            run_id = str(state["run_id"])
            break
        time.sleep(0.2)
    if run_id is None:
        # No verified owner state: the bounded reap observes the
        # already-exited owner (a still-running child is left to
        # its own finite END, never signalled); the startup line
        # (when closed) carries the child's own refusal reason.
        owner_exit = _reap_bounded()
        # the output reader is drained BEFORE the closed startup
        # line is read (a line not yet observed is not a closed
        # line; the bounded join settles it after the exit)
        _settled()
        reason = "local-driver-startup"
        try:
            lines = bytes(captured).decode("ascii", "replace").strip().splitlines()
            startup = json.loads(lines[-1])
            if (
                isinstance(startup, dict)
                and startup.get("record") == flocal.CONTROL_RECORD
                and startup.get("stage") == "startup"
                and isinstance(startup.get("reason"), str)
                and startup["reason"] in flocal._FAILURE_REASONS
            ):
                reason = startup["reason"]
        except (ValueError, IndexError):
            pass
        return _startup_record(reason, owner_exit)
    state = flocal._state_record(control_dir, entry_order=entry.order_id)
    if state is None:
        return _startup_record("local-driver-startup", _reap_bounded())
    # -- startup authority (layer 2): bind the published state to the
    # ACTUAL still-live sealed child of THIS launch.  The fresh
    # bootstrap means the root can only have been created by this
    # child; the published pid must be this child's own pid, and the
    # child must still be alive when the state is adopted.  A prior
    # or foreign owner's state — even one carrying the same bound run
    # id and head — is never adopted: no command is issued, no abort
    # is sent, and the journal is never mutated for it.
    if proc.poll() is not None:
        return _startup_record("local-driver-startup", proc.poll())
    published_pid = state.get("pid")
    if (
        not isinstance(published_pid, int)
        or isinstance(published_pid, bool)
        or published_pid != proc.pid
    ):
        # non-blocking: this child is our own sealed process — it is
        # left to its own finite END (never waited on, never
        # signalled); only its current observed state is recorded
        return _startup_record("local-owner-foreign-state", proc.poll())
    # The binding verification: the published run id must be
    # EXACTLY the one admitted attempt of this order at this head
    # (the sealed child minted and admitted it; the driver only
    # verifies the closed protected outputs).
    try:
        _verify_bound_admission(repo, bind_head, run_id, entry)
    except FixtureError as exc:
        return _startup_record(str(exc), _reap_bounded())
    if proc.poll() is None:
        try:
            independent = os.getsid(proc.pid) != os.getsid(os.getpid())
        except (OSError, ValueError, TypeError):
            independent = False
        if not independent:
            return _startup_record("local-driver-independence", proc.poll())

    # -- the entry's frozen subject expectation -------------------------------
    # The X/Y entries keep the historical fixed-21002 law (their
    # state is the strict 12-key v1 form — no identity exists to
    # adopt, and the reader's tag law already refused any other
    # form).  The canonical 017-ab entry adopts the FROZEN owner
    # identity from the owner's OWN protected AB state (the closed
    # structural law re-applied here — the reader's validation is
    # not this consumer's trust), and the state's full ORIGINAL
    # binding must agree with THIS driver's launch and admission:
    # the canonical entry, the literal bound head, the admitted run
    # (verified above).  A mismatch is a closed startup refusal —
    # no command is issued, no abort is sent, and the journal is
    # never mutated for a foreign or drifted state.  The adopted
    # expectation is preserved through the capability phase, the
    # retained record and the terminal composition (the terminal
    # cross-checks the owner's retained evidence identity against
    # it).
    ab_identity: dict[str, object] | None = None
    expected_subject: tuple[int, int, tuple[int, ...]] | None = None
    if entry.order_id == rprofile.AB_ORDER_ID:
        if (
            state.get("order") != entry.order_id
            or state.get("bind_head") != bind_head
        ):
            return _startup_record("local-driver-state-binding", _reap_bounded())
        law = flocal._identity_substructure_law(state.get("identity"))
        if law is None:
            return _startup_record("local-driver-state-identity", _reap_bounded())
        expected_subject = law[:3]
        ab_identity = state["identity"]

    # The driver's WHOLE command/wait/measurement budget is the
    # owner's OWN published END anchor plus the owner's own single
    # allowed cleanup grace — the approved ONE END+grace anchor.
    # The EXECUTABLE read is further clamped against the remaining
    # END (grace is convergence, never fresh measurement) and the
    # issued hold's own finite lifetime.
    end_abs = float(state["end_anchor"])
    patience_abs = end_abs + flocal.CLEANUP_GRACE_SECONDS

    def _remaining() -> float:
        return patience_abs - time.monotonic()

    def _bounded_inventory(token: str | None) -> list[dict[str, object]]:
        """One bounded exact-CID inventory observation: the
        OWNER's authoritative guarded ``top`` attestation (the
        SAME ledger/deadline) plus the per-attested-pid scoped
        verification.  A RACE-class fault (unverified
        churn/membership, degraded scoped read) is re-attested ONCE
        with a fresh authoritative inventory; a stable malformed or
        invalid state is never retried (closed refusal)."""
        rows: list[dict[str, object]] | None = None
        for attempt in (1, 2):
            if _remaining() <= 0:
                raise FixtureError("local-driver-patience")
            top = flocal._control_client(control_dir, "top", run_id, _remaining())
            if not top["ok"]:
                raise FixtureError(top["reason"] or "local-driver-protocol")
            attested = list(top["detail"]["pids"])
            try:
                rows = discover_inventory(channel, root, attested, token=token)
                return rows
            except FixtureError as exc:
                if attempt == 1 and str(exc) in INVENTORY_RACE_REASONS:
                    continue
                raise
        assert rows is not None
        return rows

    def _capability(
        cid: str | None,
        subject: dict[str, object] | None,
        process_identity: str,
        executable: str,
        executable_sha256: str | None,
        pre_rows: int,
        post_rows: int | None,
        subject_exit: str,
    ) -> dict[str, object]:
        return {
            "cid": cid,
            "subject": subject,
            "process_identity": process_identity,
            "executable": executable,
            "executable_sha256": executable_sha256,
            "pre_inventory_rows": pre_rows,
            "post_inventory_rows": post_rows,
            "inventory_rows_max": INVENTORY_ROWS_MAX,
            "subject_exit": subject_exit,
        }

    capability: dict[str, object] | None = None
    cid: str | None = None
    hold_token: str | None = None
    hold_issued_at: float | None = None
    finish_issued = False
    pre_rows: list[dict[str, object]] = []
    post_rows: list[dict[str, object]] = []
    channel: fp.CidScopedTable
    try:
        # -- prepare: the held prepared exact CID -----------------------------
        if _remaining() <= 0:
            raise FixtureError("local-driver-patience")
        prepared = flocal._control_client(control_dir, "prepare", run_id, _remaining())
        if not prepared["ok"]:
            raise FixtureError(prepared["reason"] or "local-driver-protocol")
        cid = str(prepared["detail"]["cid"])
        channel = factory(cid, _remaining())

        # -- pre-launch bounded exact-CID inventory ---------------------------
        pre_rows = _bounded_inventory(None)

        # -- hold: the ONE detached capability start --------------------------
        if _remaining() <= 0:
            raise FixtureError("local-driver-patience")
        # The issued hold's finite lifetime is anchored
        # CONSERVATIVELY BEFORE the dispatch: the RPC latency is
        # part of the clamped measurement window (never a fresh
        # hold/read budget).
        hold_issued_at = time.monotonic()
        held = flocal._control_client(control_dir, "hold", run_id, _remaining())
        if not held["ok"]:
            # The one start was refused or failed (the attempt is
            # consumed either way): the experiment's closed
            # conclusion is the refusal — the capability is never
            # measured on this run (the refusal reason is the
            # record's primary reason).
            capability = _capability(
                cid,
                None,
                "not-measured",
                "not-measured",
                None,
                len(pre_rows),
                None,
                "not-observed",
            )
            raise FixtureError(held["reason"] or "local-driver-protocol")
        # The issued marker is the closed STRING grammar (the
        # client's validator already closed it; the driver keeps
        # its own type check — a numeric marker is never coerced).
        token = held["detail"]["hold_token"]
        if not isinstance(token, str) or re.fullmatch(r"[0-9a-f]{32}", token) is None:
            raise FixtureError("local-driver-protocol")
        hold_token = token

        # -- bounded scan window: the dispatched subject must appear ----------
        subject: dict[str, object] | None = None
        scan_end = time.monotonic() + SUBJECT_SCAN_WINDOW_SECONDS
        correlation_state = "not-observed"
        while True:
            post_rows = _bounded_inventory(hold_token)
            subject, correlation_state = correlate_subject(
                pre_rows, post_rows, hold_token, expected_subject=expected_subject
            )
            if subject is not None or correlation_state == "ambiguous":
                break
            if time.monotonic() >= scan_end:
                break
            time.sleep(SUBJECT_POLL_SECONDS)
        if subject is None:
            process_identity = (
                "refused"
                if correlation_state in ("ambiguous", "identity-mismatch", "groups-law")
                else "not-measured"
            )
            capability = _capability(
                cid,
                None,
                process_identity,
                "not-measured",
                None,
                len(pre_rows),
                len(post_rows),
                "not-observed",
            )
            raise FixtureError(f"cap-correlation-{correlation_state}")

        # -- the scoped live measurement (the subject is ALIVE now) -----------
        # The executable channel is clamped at MEASUREMENT time:
        # the SAME remaining owner END (never END+grace) intersected
        # with the issued hold's own finite lifetime (a stale
        # pre-launch allowance is never reused for the read).
        measure_remaining = min(
            end_abs - time.monotonic(),
            (hold_issued_at or time.monotonic()) + STANDIN_HOLD_MAX_SECONDS - time.monotonic(),
        )
        if measure_remaining <= 0:
            raise FixtureError("local-driver-patience")
        measure_channel = factory(cid, measure_remaining)
        measured = measure_live_subject(
            measure_channel,
            int(subject["pid"]),
            int(subject["birth"]),
            token=hold_token,
            expected_subject=expected_subject,
        )
        # -- bounded natural-exit observation ---------------------------------
        subject_exit = wait_natural_exit(
            channel,
            int(subject["pid"]),
            bound=min(STANDIN_HOLD_MAX_SECONDS + EXIT_WAIT_MARGIN_SECONDS, _remaining()),
        )
        capability = _capability(
            cid,
            {
                "pid": subject["pid"],
                "birth": subject["birth"],
                "uid": subject["uid"],
                "gid": subject["gid"],
                "groups": subject["groups"],
            },
            str(measured["process_identity"]),
            str(measured["executable"]),
            measured["executable_sha256"],
            len(pre_rows),
            len(post_rows),
            subject_exit,
        )
        # -- finish: the prep-only honest unready convergence -----------------
        if _remaining() <= 0:
            raise FixtureError("local-driver-patience")
        final = flocal._control_client(control_dir, "finish", run_id, _remaining())
        if not final["ok"]:
            raise FixtureError(final["reason"] or "local-driver-protocol")
        # the terminal command was ACTUALLY issued (tracked, never
        # derived from a capability field)
        finish_issued = True
    except FixtureError as exc:
        reason = str(exc)
        record = _driver_record(
            "fail",
            reason,
            bind_head=bind_head,
            run_id=run_id,
            capability=capability,
            identity=ab_identity,
            entry=entry,
        )
        # The owner's OWN bounded terminal command (never a host
        # signal): a capability-phase failure before the finish
        # converges the held run through the exact-owner abort so
        # the retained terminal evidence exists; after the finish
        # was issued the owner already converged.
        return _terminal(
            repo,
            proc,
            reader,
            control_dir,
            run_id,
            patience_abs,
            evidence_out,
            record,
            record_out,
            abort=not finish_issued,
            finalize_pass=False,
            capture_state=lambda: capture_state_box[0],
            entry=entry,
        )

    # -- the truthful closed conclusion (determination in ``capability``) -----
    record = _driver_record(
        "pass",
        None,
        bind_head=bind_head,
        run_id=run_id,
        capability=capability,
        identity=ab_identity,
        entry=entry,
    )
    return _terminal(
        repo,
        proc,
        reader,
        control_dir,
        run_id,
        patience_abs,
        evidence_out,
        record,
        record_out,
        abort=False,
        finalize_pass=True,
        capture_state=lambda: capture_state_box[0],
        entry=entry,
    )


def _terminal(
    repo: Path,
    proc: subprocess.Popen,
    reader: threading.Thread,
    control_dir: Path,
    run_id: str,
    patience_abs: float,
    evidence_out: Path,
    record: dict[str, object],
    record_out: Path | None,
    *,
    abort: bool,
    finalize_pass: bool,
    capture_state: str | Callable[[], str] = "drained",
    entry: _SealedEntry = _ENTRY_X,
) -> dict[str, object]:
    """The driver's terminal composition on the SAME one END+grace
    anchor, as ONE coherent ordered transition:

    1. the terminal command is ISSUED FIRST while budget remains
       (a capability-phase failure before the finish sends the
       owner's OWN bounded ``abort`` over the protected interface
       — never a host signal; the actual issuance is tracked in
       the record, never derived from a capability field; an
       owner that already converged simply refuses the command);
    2. the owner then settles within the SAME budget: an EXPIRED
       remaining budget refuses BEFORE any blocking wait (no fresh
       positive floor, no post-window wait; only an ALREADY-EXITED
       owner is distinguished by a non-blocking poll);
    3. the output reader is reaped with the SAME remaining budget
       (a held reader is a separate closed fact, never the
       primary phase reason; the ACTUAL capture state — a TOTAL
       cap hit or a pipe read error, including a fault discovered
       during the final drain — is a closed driver fault that
       gates off a qualified pass exactly as the S rehearsal
       driver's capture law);
    4. the retained owner evidence is validated with the reviewed
       closed validator and BOUND to this exact attempt (the
       native-scope record, this order, this run, this head, and
       the prepared CID where the record carries it — a valid
       foreign or S-scope record is not this run's evidence);
    5. the closed decision: the PRIMARY phase reason is never
       overwritten — secondary exit/evidence faults surface as
       separate facts, and a pass-shaped record takes its first
       primary failure from the owner's own CLOSED failure (the
       verified-fail evidence carries the owner's reason — a
       failed owner exits non-zero by construction, so the bare
       exit code never masks a closed reason), then exit,
       evidence or reader state.  A
       qualified pass then follows the W publication ordering:
       the validated protected evidence first, the driver's own
       protected capability-record retention second (the actual
       qualification RETAINS its record — a refusal closes the
       returned record as fail with NO journal pass and NO
       fresh-path retry), and only then the verified same-attempt
       terminal finalization (an unverified token never returns a
       qualified success).  An already-exited distinction never
       authorizes a pass over missing or unverified evidence."""
    # the CLOSED consumer gate BEFORE any terminal journal write:
    # finalization/retention never accepts a caller-created pair
    # expectation (a foreign order id would mint a foreign journal
    # entry)
    _require_canonical_entry(entry)
    # -- 1. the terminal command is issued FIRST (before any join) --
    terminal_command = "none"
    if abort and patience_abs - time.monotonic() > 0:
        try:
            flocal._control_client(control_dir, "abort", run_id, patience_abs - time.monotonic())
            terminal_command = "abort"
        except FixtureError:
            # the owner already converged (or refused): the facts
            # remain in its state and retained evidence; the
            # issuance (and its refusal) is tracked, the primary
            # phase reason is preserved.
            terminal_command = "abort"
    record["terminal_command"] = terminal_command
    # -- 2. the owner settles within the SAME budget ---------------
    owner_exit: int | None
    if patience_abs - time.monotonic() <= 0:
        # expired: NO blocking wait; the already-exited owner is
        # distinguished non-blockingly, a still-running owner is
        # left to its own END (never waited past the anchor).
        owner_exit = proc.poll()
    else:
        try:
            owner_exit = proc.wait(timeout=patience_abs - time.monotonic())
        except subprocess.TimeoutExpired:
            owner_exit = proc.poll()
    record["owner_exit"] = owner_exit
    # -- 3. the output is reaped with the SAME remaining budget ----
    if reader.is_alive():
        reader.join(max(0.0, patience_abs - time.monotonic()))
    record["reader_state"] = "drained" if not reader.is_alive() else "held"
    # the ACTUAL capture state is resolved AFTER the drain (a
    # shared live holder when the caller supplies one): a cap hit
    # or pipe read error discovered during the final drain is a
    # closed driver fault that gates off a qualified pass.
    captured = capture_state() if callable(capture_state) else capture_state
    if captured not in ("not-observed", "drained", "cap", "read-error"):
        captured = "read-error"
    record["capture_state"] = captured
    # -- 4. the retained owner evidence, BOUND to this attempt -----
    evidence: dict[str, object] | None = None
    raw: bytes | None = None
    try:
        raw = evidence_out.read_bytes()
        est = os.lstat(evidence_out)
        if (
            not stat_mod.S_ISREG(est.st_mode)
            or stat_mod.S_IMODE(est.st_mode) != 0o600
            or est.st_uid != os.getuid()
        ):
            raise FixtureError("local-evidence-untrusted")
        evidence = json.loads(raw.decode("ascii"))
    except (OSError, ValueError, UnicodeDecodeError, FixtureError):
        evidence = None
    evidence_state = "missing"
    if evidence is not None:
        cap = record.get("capability")
        try:
            if entry.order_id == rprofile.AB_ORDER_ID:
                # The DISTINCT AB owner-run evidence (the AB record
                # tag, the canonical AB order, the identity
                # substructure and the exact-CID teardown proof —
                # the shared measured substructures run the SAME
                # private structural core with the AB expectations
                # wired through, never normalized to 21002).
                if (
                    not isinstance(evidence, dict)
                    or evidence.get("record") != flocal.AB_OWNER_RUN_EVIDENCE_SCHEMA
                ):
                    raise FixtureError("local-driver-evidence")
                flocal.validate_ab_owner_run_evidence(evidence)
            else:
                # the historical native-scope law, byte-for-byte
                if (
                    not isinstance(evidence, dict)
                    or evidence.get("record") != flocal.NATIVE_OWNER_RUN_EVIDENCE_SCHEMA
                ):
                    raise FixtureError("local-driver-evidence")
                flocal.validate_native_owner_run_evidence(evidence)
            if (
                evidence.get("order") != entry.order_id
                or str(evidence.get("run_id")) != str(run_id)
                or evidence.get("bind_head") != record.get("bind_head")
            ):
                raise FixtureError("local-driver-evidence")
            if entry.order_id == rprofile.AB_ORDER_ID:
                # the SAME frozen context end-to-end: the owner's
                # RETAINED evidence identity must be the driver's
                # ADOPTED expectation byte-for-byte (a divergent
                # identity is not this run's evidence)
                adopted = record.get("identity")
                if adopted is None or evidence.get("identity") != adopted:
                    raise FixtureError("local-driver-evidence")
            if isinstance(cap, dict) and cap.get("cid") is not None:
                prepared = evidence.get("prepared")
                if isinstance(prepared, dict) and prepared.get("cid") != cap["cid"]:
                    raise FixtureError("local-driver-evidence")
            evidence_state = (
                "verified-pass" if evidence.get("status") == "pass" else "verified-fail"
            )
        except (FixtureError, AttributeError, KeyError, TypeError):
            evidence_state = "invalid"
    record["evidence_state"] = evidence_state
    if evidence_state in ("verified-pass", "verified-fail") and raw is not None:
        record["evidence_sha256"] = hashlib.sha256(raw).hexdigest()

    # -- 5. the closed terminal decision ----------------------------
    def _first_failure(reason: str) -> None:
        if record["reason"] is None:
            record["reason"] = reason
            record["status"] = "fail"

    # qualification is RECOMPUTED from the verified facts (never a
    # cached flag from before validation): a pass-shaped record
    # takes the owner's own CLOSED failure reason first (a failed
    # owner exits non-zero by construction — the bare exit code
    # never masks a closed reason), then its first primary
    # failure from exit, reader or evidence state.
    qualified = False
    if record["status"] == "pass":
        if owner_exit is None:
            _first_failure("local-driver-patience")
        elif evidence_state == "verified-fail":
            # the owner's OWN closed outcome (a failed owner exits
            # non-zero BY CONSTRUCTION): the driver reports the
            # owner's closed reason — never a pass over a failed
            # owner, never a bare exit code over a closed reason
            record["reason"] = str(evidence.get("reason")) or "local-driver-evidence"
            record["status"] = "fail"
        elif owner_exit != 0:
            _first_failure("local-driver-exit")
        elif record["reader_state"] == "held":
            _first_failure("local-driver-output")
        elif captured in ("cap", "read-error"):
            _first_failure("local-driver-output")
        elif evidence_state == "missing":
            _first_failure("local-driver-evidence")
        elif evidence_state == "invalid":
            _first_failure("local-driver-evidence")
        else:
            qualified = True
    if qualified and finalize_pass:
        # retention FIRST: the actual qualification retains its
        # capability record (a protected destination is required).
        if record_out is None:
            _first_failure("cap-record-missing")
            qualified = False
        else:
            try:
                _retain_record(record, record_out, entry)
                record["retention"] = "retained"
            except FixtureError:
                record["retention"] = "refused"
                _first_failure("cap-record-retention")
                qualified = False
        if qualified:
            try:
                token = oap_binding.record_order_attempt(repo, entry.order_id, run_id, "pass")
            except (FixtureError, OSError):
                token = "failed"
            record["finalize"] = token
            if token != "finalized":
                # a post-retention unverified or raced finalization
                # never returns a normal qualified success, and its
                # ACTUAL journal facts are preserved (no second
                # write, no fresh-path retry or reset).
                _first_failure("local-driver-finalize")
    # The closed failure: the SAME pending attempt is closed as
    # fail when this terminal decision is a fail (idempotent — a
    # terminal journal entry, such as the owner's own converged
    # terminal outcome or a foreign run id absent from the journal,
    # is preserved, never rewritten).  The post-retention
    # unverified-finalization exception above preserves its actual
    # facts instead (the capability record is already retained and
    # the real token recorded).  The closed fail record is then
    # retained best-effort at the requested protected destination
    # (its refusal is reported, never a silently dropped record,
    # never a fresh-path retry).
    post_retention_unverified = (
        record["retention"] == "retained" and record["finalize"] != "not-attempted"
    )
    if record["status"] == "fail" and not post_retention_unverified:
        try:
            token = oap_binding.record_order_attempt(repo, entry.order_id, run_id, "fail")
        except (FixtureError, OSError):
            token = "failed"
        if record["finalize"] == "not-attempted":
            record["finalize"] = token
    if (
        record["status"] == "fail"
        and record_out is not None
        and record["retention"] == "not-requested"
    ):
        try:
            _retain_record(record, record_out, entry)
            record["retention"] = "retained"
        except FixtureError:
            record["retention"] = "refused"
    return record


# -- the public entry (explicit opt-in, closed grammar) ---------------------------
def main(argv: list[str] | None = None) -> int:
    """The driver's THIN public entry: ONE closed subcommand
    (``capability``) with the EXPLICIT opt-in (the bound order id
    must be a SEALED ENTRY id — the historical ``017-x``, the new
    ``017-y`` or the canonical INACTIVE ``017-ab``), the exact
    active/order/literal-head binding and the closed result record
    printed as the single stdout line.  This is not a general
    command runner: no other subcommand, flag or value form is
    accepted."""
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("capability")
    p.add_argument(
        "--order",
        help="the bound order id (a sealed entry: 017-x, 017-y or 017-ab)",
    )
    p.add_argument("--bind-head", help="literal 40-hex source head")
    p.add_argument("--repo", help="repository checkout root")
    p.add_argument("--work", help="fresh owned disposable work root")
    p.add_argument("--control-dir", help="fresh protected control root")
    p.add_argument("--evidence-out", help="protected owner evidence destination")
    p.add_argument(
        "--record-out",
        help="protected capability-record destination (required: the ONE "
        "qualification attempt is never admitted without its retention "
        "destination)",
    )
    args = parser.parse_args(argv)
    entry = _SEALED_ENTRIES.get(args.order or "", _ENTRY_X)
    if (
        args.command != "capability"
        or args.order not in _SEALED_ENTRIES
        or not args.bind_head
        or not args.repo
        or not args.work
        or not args.control_dir
        or not args.evidence_out
        or not args.record_out
    ):
        print(
            json.dumps(
                _driver_record("fail", "local-args-invalid", bind_head="0" * 40, entry=entry),
                sort_keys=True,
            )
        )
        return 1
    try:
        summary = run_exec_capability(
            args.repo,
            args.bind_head,
            args.work,
            args.control_dir,
            args.evidence_out,
            record_out=Path(args.record_out),
            entry=entry,
        )
    except KeyboardInterrupt:
        summary = _driver_record("fail", "cancelled", bind_head=args.bind_head, entry=entry)
    except FixtureError as exc:
        summary = _driver_record("fail", str(exc), bind_head=args.bind_head, entry=entry)
    except Exception:
        summary = _driver_record("fail", "internal", bind_head=args.bind_head, entry=entry)
    print(json.dumps(summary, sort_keys=True))
    return 0 if summary["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())

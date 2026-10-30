#!/usr/bin/env python3
"""Versioned native-owner public lifecycle composition (order 017-v).

The small EXPLICIT operator API that connects the accepted
immutable order/run binding, the ACTUAL fixture-owner
construction/admission/lifecycle, and the public staged
native registration into one coherent run:

- the constructor accepts ONLY a verified immutable
  ``OrderRunBinding`` from the existing resolver, admits
  EXACTLY ONCE in that order's stable one-attempt namespace
  BEFORE any external mutation (the admission itself
  re-validates the actual repository/committed
  active/order/head/context), and then constructs the REAL
  ``LocalFixtureOwner`` with the binding's minted run
  identity — the owner's historical order-bound opt-in
  authority checks stay live, the S default path (fresh mint
  + stable 017-s admission) is unchanged, and a bare caller
  run id can never skip the order's one-attempt law (the
  owner constructor verifies the bound admission is live for
  that exact run before adopting it);
- ONE owner, ONE RAM run context, ONE absolute END anchor,
  ONE cumulative ledger and ONE bounded cleanup grace are
  shared across construction, prepare, held observation,
  finish/abort, evidence publication and attempt
  finalization — no second watchdog/owner/controller, no
  reset, no new budget, no hidden retry, no host signal;
- the public native workflow starts WITHOUT a predicted
  native PID: prepare freezes the measured W/B
  birth/group/session/TTY baseline, the separately measured
  stop is recorded, and the actual later subject is
  registered through the workflow's public staged entry
  (register_subject) with the operator's owned attach
  expectation/channel, retaining the same immutable
  baseline and run;
- a native-mode run publishes the EXPLICIT native schemas:
  the measured native-owner record through the existing
  producer/consumer where its measured prerequisites hold,
  and the closed native-run terminal record under its own
  distinct scope otherwise — preparation-only, not-started
  and failure outcomes are represented honestly, and the
  owner's historical S-scope record keeps its S meaning
  (it is never relabeled as native evidence);
- the HONEST ONE-SHOT publication transition: owner
  convergence measures/retains the DISTINCT owner-phase
  outcome (a terminal fail/aborted finalizes the bound
  attempt honestly at convergence; a converged pass keeps it
  RUNNING); once native publication for the COMPLETED owner
  begins, the ACTUAL bound journal state is read (never
  assumed from the outcome — the pass path requires the
  attempt still running), the protected native-run record is
  retained FIRST (its attempt field carries the ALREADY-KNOWN
  journal state, never a predicted finalize token), and ONLY
  THEN the same-order journal is finalized (the terminal pass
  admits only the real verified finalization).  Every
  boundary refusal — destination/writer refusal, unverified
  or raced finalization — terminalizes the qualified attempt:
  no fresh-path retry, no relabel, no journal reset, and an
  unverified post-retention finalization is a closed failure
  that preserves the retained bytes and the journal facts
  without returning a normal qualified success; the real
  finalize token is retained in RAM/result, never rewritten
  into the immutable evidence.

This round exercises the composition with injected FAKE
external operations (fake git/platform/process seams and
owned synthetic repositories) only: NO actual local Docker
operation, NO native launch (including help/version), NO
worker stop, NO TTY/job manipulation, NO real fixture
admission in the real checkout, NO host signal.  The real
backend code is imported and its real methods driven; the
platform operations are faked.  There is no CLI entry that
accepts a fabricated collector result.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
import sys
import threading
import time
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cache_native_fixture_binding as oap_binding  # noqa: E402
import cache_native_fixture_ci as ci  # noqa: E402
import cache_native_fixture_local as local  # noqa: E402
import cache_native_fixture_model as fmodel  # noqa: E402
import cache_native_fixture_native_prep as prep  # noqa: E402
import cache_native_fixture_runtime_profile as rprofile  # noqa: E402

FixtureError = ci.FixtureError
OrderRunBinding = oap_binding.OrderRunBinding

NATIVE_RUN_SCHEMA = "slaif-native-owner-run-v1"
NATIVE_RUN_SCOPE = "native-owner-run"
# The canonical FUTURE 017-ad native entry (INERT in this
# round: input-gated, unqualified — never activated, admitted
# or launched here) and its DISTINCT versioned identity-bearing
# native-run terminal tag: the SAME closed measured facts as
# the original tag PLUS the frozen owner-identity substructure
# the real owner collected and derived.  The original tag keeps
# its exact historical key set and refuses BOTH the identity
# key and any 017-ad binding (separate closed records, never a
# widened grammar — including for equal-numeric identities);
# the scope literal stays the profile-independent original.
AD_ORDER_ID = rprofile.AD_ORDER_ID
AD_NATIVE_RUN_SCHEMA = rprofile.AD_NATIVE_RUN_SCHEMA
# The canonical FUTURE 017-af native-PTY qualification entry
# (INERT in 017-ae: software only — never activated,
# admitted or launched here) and its DISTINCT versioned
# identity-bearing native-run terminal tag: the SAME closed
# measured facts as the AD tag PLUS the frozen owner-identity
# substructure AND the nested attach-binding record (or an
# honest None).  The original tag keeps its exact historical
# key set and refuses BOTH the identity key and any 017-ad /
# 017-af binding (separate closed records, never a widened
# grammar — including for equal-numeric identities); the
# scope literal stays the profile-independent original.
AF_ORDER_ID = rprofile.AF_ORDER_ID
AF_NATIVE_RUN_SCHEMA = rprofile.AF_NATIVE_RUN_SCHEMA
# The canonical FUTURE 017-ah native-PTY REQUALIFICATION
# entry (INERT in 017-ag: software only — never activated,
# admitted or launched here) and its DISTINCT versioned
# identity-bearing native-run terminal tag: the SAME closed
# measured facts as the AF tag PLUS the frozen owner-identity
# substructure AND the nested attach-binding record (or an
# honest None) under the AH entry's own tag-pair law (the AF
# tag remains AF-only, even for equal-numeric identities);
# the original tag refuses every identity-bearing binding.
AH_ORDER_ID = rprofile.AH_ORDER_ID
AH_NATIVE_RUN_SCHEMA = rprofile.AH_NATIVE_RUN_SCHEMA
# The canonical FUTURE 017-aj native-process format
# QUALIFICATION entry (INERT in 017-ai: software only —
# never activated, admitted or launched here) and its
# DISTINCT versioned identity-bearing native-run terminal
# tag: the SAME closed measured facts as the AH tag PLUS
# the frozen owner-identity substructure AND the nested
# attach-binding record (or an honest None) AND the nested
# selected native format-capture record (or an honest None)
# under the AJ entry's own tag-pair law (the AH tag remains
# AH-only, even for equal-numeric identities); the original
# tag refuses every identity-bearing binding.
AJ_ORDER_ID = rprofile.AJ_ORDER_ID
AJ_NATIVE_RUN_SCHEMA = rprofile.AJ_NATIVE_RUN_SCHEMA
# the owner's closed terminal outcomes (the attempt record
# vocabulary, never a caller boolean)
NATIVE_RUN_OUTCOMES = frozenset({"pass", "fail", "aborted"})
# the closed attempt-finalization tokens (record_order_attempt)
# plus the PENDING journal state a retained record honestly
# carries before the terminal pass finalization that follows a
# successful protected publication (never a predicted token)
NATIVE_RUN_ATTEMPT_TOKENS = frozenset(
    {"running", "finalized", "terminal-preserved", "not-running", "record-unreadable"}
)
# the closed owner-record binding representation
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
_NATIVE_RUN_KEYS = frozenset(
    {
        "record",
        "scope",
        "binding",
        "owner_outcome",
        "attempt",
        "subject_measured",
        "stop_recorded",
        "native_record",
        "native_refusal",
        "verdict",
    }
)
_VERDICT_KEYS = frozenset({"ready", "reasons"})

# the closed failure vocabulary of THIS module (the
# composition's own tokens; the owner/workflow/producer
# tokens propagate unchanged from their own closed sets)
NATIVE_OWNER_REASONS = frozenset(
    {
        "native-owner-binding-invalid",
        "native-owner-order-path-mismatch",
        "native-owner-not-started",
        "native-owner-startup",
        "native-owner-settle",
        "native-owner-patience",
        "native-owner-not-terminal",
        "native-owner-registration-unmeasured",
        "native-owner-subject-cid-mismatch",
        "native-owner-subject-binary-mismatch",
        "native-owner-identity-unmeasured",
        "native-owner-evidence-unretained",
        "native-owner-evidence-exists",
        "native-owner-evidence-env",
        "native-owner-journal-unverified",
        "native-owner-finalization-unverified",
        "native-owner-published",
        "native-owner-record-malformed",
        "native-owner-channel-budget-invalid",
        # the AF native attach-binding phase (017-ae software)
        "native-owner-attach-not-admitted",
        "native-owner-attach-stale-stop",
        "native-owner-attach-baseline-missing",
        "native-owner-attach-baseline-repeat",
        "native-owner-attach-binding-missing",
        "native-owner-attach-binding-repeat",
        "native-owner-attach-pty-mismatch",
        "native-owner-attach-context-invalid",
        "native-owner-attach-channel-invalid",
        "native-owner-attach-devpts-unreadable",
        "native-owner-attach-devpts-namespace-mismatch",
        "native-owner-attach-devpts-device-mismatch",
        "native-owner-attach-devpts-inode-mismatch",
        "native-owner-attach-devpts-mode-mismatch",
        "native-owner-attach-devpts-owner-mismatch",
        "native-owner-attach-identity-drift",
        "native-owner-format-capture-invalid",
        "internal",
    }
)

# the seam's disposable-work-root containment argument for a
# direct two-argument retention call (the probe form): a path
# that is never an ancestor; the composition ALWAYS passes the
# owner's real work root, which the seam enforces.
_NO_WORK_ROOT = Path(os.devnull)


def build_ad_native_channel(cid: str, end: float) -> prep.CidScopedTable:
    """The REAL scoped AD native-measurement channel bound to
    the exact registered CID with the 017-ad closed executable
    bounds: at most 320 MiB (335544320 bytes) and at most 10 s
    per measurement, further clamped to the SAME ABSOLUTE owner
    END anchor (``end``) at EVERY actual exe read/return —
    never a relative duration captured at construction and
    never including the cleanup grace (grace is convergence,
    not fresh measurement): once that absolute point has
    passed, EVERY later use of this channel is refused, no
    matter how often it is reused.  The original Python-entry
    bounds (16 MiB / 10 s) are a separate closed default and
    stay unchanged."""
    if not isinstance(end, (int, float)) or isinstance(end, bool) or not math.isfinite(end):
        raise FixtureError("native-owner-channel-budget-invalid")
    return prep.RealCidScopedTable(
        cid,
        max_exe_bytes=rprofile.AD_EXE_MAX_BYTES,
        exe_deadline=rprofile.AD_EXE_DEADLINE_SECONDS,
        exe_end=float(end),
    )


def _is_sha256(value: object) -> bool:
    return isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value) is not None


def parse_native_run_record(record: object) -> dict:
    """The closed consumer of the native-run terminal record:
    the exact top-level key set, the closed scope/outcome/
    attempt vocabularies (checked as CLOSED STRINGS first — a
    non-string or unhashable value is a typed refusal, never
    an untyped error), the exact owner-binding record in the
    binding module's own closed grammar (OAP order id,
    40-hex source head, 32-hex run id, sha256 digests), closed
    booleans, and — when present — a native_record that
    passes the ACTUAL native-owner consumer validation AND is
    bound to the OUTER binding (its measured order/head/run
    identity must equal the outer binding's — a foreign
    nested identity is a contradiction, never a valid context)
    and a closed verdict (ready boolean + reasons from the
    closed verdict vocabulary).  Cross-field consistency: an
    outer ready requires EVERY measured prerequisite (the
    owner's converged pass, the measured subject, the recorded
    stop, the measured native record with its own ready fact,
    no refusal); a refusal forbids a measured native record
    and any readiness.  Unknown, missing or non-mapping
    fields are closed non-echoing refusals; nothing is
    retained beyond the exact closed shape."""
    if not isinstance(record, dict):
        raise FixtureError("native-owner-record-malformed")
    tag = record.get("record")
    # the DISTINCT identity-bearing 017-ad / 017-af terminal
    # forms: the SAME closed measured facts PLUS the frozen
    # owner-identity substructure (the AF form ADDITIONALLY
    # carries the nested attach-binding record); the original
    # tag keeps its exact historical key set (no identity key
    # at all) — separate closed records, never a widened
    # grammar
    if tag == AD_NATIVE_RUN_SCHEMA:
        expected_keys = _NATIVE_RUN_KEYS | {"identity"}
    elif tag == AF_NATIVE_RUN_SCHEMA:
        expected_keys = _NATIVE_RUN_KEYS | {"identity", "attach_binding"}
    elif tag == AH_NATIVE_RUN_SCHEMA:
        expected_keys = _NATIVE_RUN_KEYS | {"identity", "attach_binding"}
    elif tag == AJ_NATIVE_RUN_SCHEMA:
        expected_keys = _NATIVE_RUN_KEYS | {"identity", "attach_binding", "format_capture"}
    elif tag == NATIVE_RUN_SCHEMA:
        expected_keys = _NATIVE_RUN_KEYS
    else:
        raise FixtureError("native-owner-record-malformed")
    if set(record) != expected_keys:
        raise FixtureError("native-owner-record-malformed")
    outcome = record["owner_outcome"]
    attempt = record["attempt"]
    if (
        record["scope"] != NATIVE_RUN_SCOPE
        or not isinstance(outcome, str)
        or outcome not in NATIVE_RUN_OUTCOMES
        or not isinstance(attempt, str)
        or attempt not in NATIVE_RUN_ATTEMPT_TOKENS
        or not isinstance(record["subject_measured"], bool)
        or not isinstance(record["stop_recorded"], bool)
    ):
        raise FixtureError("native-owner-record-malformed")
    binding = record["binding"]
    if (
        not isinstance(binding, dict)
        or set(binding) != _BINDING_RECORD_KEYS
        or binding.get("record") != oap_binding.BINDING_RECORD_SCHEMA
        or not isinstance(binding.get("order_id"), str)
        or oap_binding._ORDER_ID_RE.fullmatch(binding.get("order_id", "")) is None
        or not isinstance(binding.get("order_path"), str)
        or not _is_sha256(binding.get("order_sha256"))
        or not _is_sha256(binding.get("active_sha256"))
        or not isinstance(binding.get("source_head"), str)
        or oap_binding._HEAD_RE.fullmatch(binding.get("source_head", "")) is None
        or not isinstance(binding.get("repo_identity"), str)
        or not binding.get("repo_identity")
        or not isinstance(binding.get("run_id"), str)
        or oap_binding._RUN_ID_RE.fullmatch(binding.get("run_id", "")) is None
    ):
        raise FixtureError("native-owner-record-malformed")
    # The entry-aware closed ORDER binding: the original tag is
    # never the record of the canonical 017-ad / 017-af entry
    # (including the equal-numeric cross-profile case — a
    # fixed-21002 subject bound to any of them still belongs
    # to the entry's OWN tag), and each identity-bearing tag
    # is its OWN canonical entry's record only at its
    # canonical order path (its frozen identity substructure
    # is closed-validated by the shared structural core — data
    # integrity, never a measured-authority claim).
    identity_entry = tag in (
        AD_NATIVE_RUN_SCHEMA,
        AF_NATIVE_RUN_SCHEMA,
        AH_NATIVE_RUN_SCHEMA,
        AJ_NATIVE_RUN_SCHEMA,
    )
    identity_triple: tuple[int, int, tuple[int, ...]] | None = None
    if identity_entry:
        entry_order, entry_path = {
            AD_NATIVE_RUN_SCHEMA: (AD_ORDER_ID, rprofile.AD_ORDER_PATH),
            AF_NATIVE_RUN_SCHEMA: (AF_ORDER_ID, rprofile.AF_ORDER_PATH),
            AH_NATIVE_RUN_SCHEMA: (AH_ORDER_ID, rprofile.AH_ORDER_PATH),
            AJ_NATIVE_RUN_SCHEMA: (AJ_ORDER_ID, rprofile.AJ_ORDER_PATH),
        }[tag]
        if binding["order_id"] != entry_order or binding["order_path"] != entry_path:
            raise FixtureError("native-owner-record-malformed")
        law = local._identity_substructure_law(record["identity"])
        if law is None:
            raise FixtureError("native-owner-record-malformed")
        identity_triple = (law[0], law[1], law[2])
    elif binding["order_id"] in (AD_ORDER_ID, AF_ORDER_ID, AH_ORDER_ID, AJ_ORDER_ID):
        raise FixtureError("native-owner-record-malformed")
    native = record["native_record"]
    native_facts = None
    if native is not None:
        try:
            native_facts = prep.parse_native_owner_facts(native)
        except FixtureError:
            raise FixtureError("native-owner-record-malformed") from None
        if (
            native_facts.order != binding["order_id"]
            or native_facts.source_head != binding["source_head"]
            or native_facts.run_id != binding["run_id"]
        ):
            raise FixtureError("native-owner-record-malformed")
        # the AD form: the nested identity-bearing native record
        # must carry the SAME frozen identity as the outer
        # record (both halves of the retained record are
        # cross-bound to one frozen context)
        if identity_entry and native_facts.identity != identity_triple:
            raise FixtureError("native-owner-record-malformed")
    # The AF / AH entry's nested attach-binding record:
    # RE-DERIVED by the closed consumer against the OUTER
    # binding record (a copied or replayed record never mints
    # authority), cross-bound to the outer frozen identity and
    # — when a native record is present — to that record's
    # measured CID
    attach = None
    if tag in (AF_NATIVE_RUN_SCHEMA, AH_NATIVE_RUN_SCHEMA, AJ_NATIVE_RUN_SCHEMA):
        attach = record["attach_binding"]
        if attach is not None:
            try:
                prep.parse_attach_binding_record(attach, binding)
            except prep.FixtureError:
                raise FixtureError("native-owner-record-malformed") from None
            attach_law = local._identity_substructure_law(attach.get("identity"))
            if attach_law is None or (
                (attach_law[0], attach_law[1], attach_law[2]) != identity_triple
            ):
                raise FixtureError("native-owner-record-malformed")
            if native_facts is not None and attach.get("cid") != native_facts.cid:
                raise FixtureError("native-owner-record-malformed")
    # The AJ entry's nested selected native format-capture
    # record: RE-DERIVED by the closed consumer against the
    # OUTER binding record and the frozen identity (a copied
    # or replayed record never mints authority), cross-bound
    # to the measured CID when a native record is present.
    format_capture = None
    if tag == AJ_NATIVE_RUN_SCHEMA:
        format_capture = record["format_capture"]
        if format_capture is not None:
            try:
                prep.parse_format_capture_record(format_capture, binding)
            except prep.FixtureError:
                raise FixtureError("native-owner-record-malformed") from None
            if format_capture.get("identity") != record["identity"]:
                raise FixtureError("native-owner-record-malformed")
            if native_facts is not None and format_capture.get("cid") != native_facts.cid:
                raise FixtureError("native-owner-record-malformed")
    refusal = record["native_refusal"]
    if refusal is not None and (not isinstance(refusal, str) or refusal not in prep.PREP_REASONS):
        raise FixtureError("native-owner-record-malformed")
    verdict = record["verdict"]
    if (
        not isinstance(verdict, dict)
        or set(verdict) != _VERDICT_KEYS
        or not isinstance(verdict.get("ready"), bool)
        or not isinstance(verdict.get("reasons"), list)
        or any(not isinstance(r, str) or r not in prep._VERDICT_REASONS for r in verdict["reasons"])
        or verdict.get("ready") is True
        and verdict["reasons"] != []
    ):
        raise FixtureError("native-owner-record-malformed")
    if verdict["ready"] is True and (
        outcome != "pass"
        or record["subject_measured"] is not True
        or record["stop_recorded"] is not True
        or native is None
        or refusal is not None
        or native_facts.native_ready is not True
        # the AF / AH entry's ready verdict additionally
        # requires the measured attach binding (a missing
        # attach is an honest None, never a ready handoff)
        # the AJ entry keeps the SAME native handoff
        # readiness law: the format capture is a DISTINCT
        # ordered qualification fact carried in its own field
        # (never this verdict) — a measured native-ready
        # handoff with an unsupported or partial format
        # stays truthfully representable and retainable, with
        # the format NOT qualified and no final
        # qualification pass; the later qualification gate
        # reads BOTH facts explicitly
        or tag in (AF_NATIVE_RUN_SCHEMA, AH_NATIVE_RUN_SCHEMA, AJ_NATIVE_RUN_SCHEMA)
        and attach is None
    ):
        raise FixtureError("native-owner-record-malformed")
    if refusal is not None and (native is not None or verdict["ready"] is True):
        raise FixtureError("native-owner-record-malformed")
    return record


def _aj_format_capture_record(
    owner: local.LocalFixtureOwner,
    binding: OrderRunBinding,
    owner_identity: dict | None,
) -> dict | None:
    """The AJ entry's measured selected native format-capture
    record (017-ai software): the retained selected export
    payload of THIS SAME completed owner (the owner's OWN
    finish retained it — a caller can never supply one) is
    byte-bounded BEFORE any decode, validated in FULL by
    the ACTUAL shared selected-export dispatcher (the
    exact export key set, the closed quiesce record, the
    export-tag versus nested-tag coherence, the nested
    snapshot law) and admitted under the AJ entry's
    explicit full/partial-only law, then re-wrapped in the
    DISTINCT identity-bearing format-capture record (the
    workflow's OWN immutable binding, the owner's frozen
    identity substructure, the owner's measured CID) which
    is RE-VALIDATED by the closed consumer — including the
    256 KiB TOTAL SERIALIZED selected-capture bound over
    the WHOLE record.  An honest None (the finish
    retained no selected capture) is preserved; a
    malformed, untagged, invalid-quiesce, over-bound or
    non-snapshot payload is a closed non-echoing refusal
    (never a purported capture, never a partial laundered
    as full)."""
    if owner_identity is None:
        raise FixtureError("native-owner-identity-unmeasured")
    payload = owner.export_payload
    if payload is None:
        return None
    if not isinstance(payload, (bytes, bytearray)):
        raise FixtureError("native-owner-format-capture-invalid")
    # The existing shared export validators already cap
    # the ENTIRE raw export payload at the 256 KiB
    # selected-capture bound — that SAME existing bound is
    # enforced here on the original object's length
    # (O(1), no copy) before ANY conversion, decode or
    # parse allocation.
    if not payload or len(payload) > fmodel.FORMAT_SNAPSHOT_MAX_BYTES:
        raise FixtureError("native-owner-format-capture-invalid")
    raw = bytes(payload)
    # The FULL measured export is validated at this
    # producer seam by the ACTUAL shared selected-payload
    # dispatcher (exact export key set, closed quiesce
    # record, export-tag versus nested-snapshot-tag
    # coherence, the nested snapshot law) — never a raw
    # decode plus a tag peek.
    try:
        selected = ci.fixture_export.validate_selected_payload(raw)
    except (ValueError, TypeError):
        raise FixtureError("native-owner-format-capture-invalid") from None
    # The AJ entry's explicit closed law: the full and
    # the safe partial export tags ONLY — an untagged
    # legacy payload (which the dispatcher validates
    # under its historical six-field law) can never
    # masquerade as a format capture here.
    if not isinstance(selected, dict) or selected.get("record") not in (
        fmodel.SCHEMA_FORMAT_EXPORT,
        fmodel.SCHEMA_FORMAT_EXPORT_PARTIAL,
    ):
        raise FixtureError("native-owner-format-capture-invalid")
    snapshot = selected.get("snapshot")
    if not isinstance(snapshot, dict):
        raise FixtureError("native-owner-format-capture-invalid")
    outer: dict[str, object] = {
        "record": rprofile.AJ_NATIVE_FORMAT_CAPTURE_SCHEMA,
        "binding": binding.to_record(),
        "identity": owner_identity,
        "cid": owner.target_cid,
        "snapshot": snapshot,
    }
    try:
        prep.parse_format_capture_record(outer, binding)
    except (FixtureError, ValueError, TypeError):
        raise FixtureError("native-owner-format-capture-invalid") from None
    return outer


def _write_native_run_record(path: Path, record: dict, work: Path | None = None) -> None:
    """Protected 0600 retention of the closed native-run
    record, reusing the reviewed protected atomic
    no-overwrite retention seam (``ci._retain_evidence``):
    the destination and every ancestor are validated AS GIVEN
    (a link alias, a group/other-writable or untrusted
    ancestor, or a non-0700 parent is refused — no adoption,
    no chmod), the destination must not pre-exist (an
    existing object is refused, never overwritten; the commit
    is an atomic no-overwrite LINK, not a rename that could
    clobber a raced destination), the bytes are
    digest-verified before the commit, and the retained
    object is re-verified.  A pre-existing temporary file of
    this record's exact name is crashed/foreign state:
    refused — never unlinked, never adopted.  The
    disposable-work-root containment is the composition's own
    explicit refusal (the caller's evidence root must be
    outside the owner's work root); when a work root is given
    it is enforced by the seam as well."""
    path = Path(path)
    if path.exists() or path.is_symlink():
        raise FixtureError("native-owner-evidence-exists")
    tmp = path.with_name(path.name + ".tmp")
    if tmp.exists() or tmp.is_symlink():
        raise FixtureError("native-owner-evidence-exists")
    payload = (json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n").encode("ascii")
    digest = hashlib.sha256(payload).hexdigest()
    try:
        ci._retain_evidence(path, payload, digest, work if work is not None else _NO_WORK_ROOT)
    except FixtureError as exc:
        if str(exc) == "evidence-exists":
            raise FixtureError("native-owner-evidence-exists") from None
        raise FixtureError("native-owner-evidence-env") from None


class NativeOwnerRun:
    """The ONE bounded native-owner run: the verified
    immutable binding, the order-namespace admission, the
    REAL fixture owner (its protected interface), and the
    public staged native workflow — one shared RAM context,
    END anchor, ledger and cleanup grace.  The thin caller
    drives the bounded lifecycle: start -> prepare ->
    observe* -> record_stop -> register_subject -> observe*
    -> finish (or abort) -> publish_native.  Every terminal
    owner outcome is followed by the same-namespace attempt
    finalization inside publish_native."""

    def __init__(
        self,
        binding: object,
        repo: object,
        work: object,
        owner_evidence_out: object,
        control_dir: object,
        *,
        git_runner=None,
        executor=None,
        table=None,
        worker_pid: int | None = None,
        bash_pid: int | None = None,
        tty_foreground_pgrp: int | None = None,
        registered_owners=None,
        deadline_offset: float = 0.0,
        identity_reader=None,
        proc_root: Path | None = None,
    ) -> None:
        if not isinstance(binding, OrderRunBinding):
            raise FixtureError("native-owner-binding-invalid")
        # The fixed canonical 017-ad / 017-af / 017-aj entries resolve
        # ONLY at their unique committed order paths (the
        # resolver applies the same closed law): a directly-
        # constructed binding carrying the entry's order id at
        # a foreign path is refused BEFORE the admission or the
        # owner adoption.  Every other (generic) order keeps
        # the exact historical law.
        if binding.order_id == AD_ORDER_ID and binding.order_path != rprofile.AD_ORDER_PATH:
            raise FixtureError("native-owner-order-path-mismatch")
        if binding.order_id == AF_ORDER_ID and binding.order_path != rprofile.AF_ORDER_PATH:
            raise FixtureError("native-owner-order-path-mismatch")
        if binding.order_id == AH_ORDER_ID and binding.order_path != rprofile.AH_ORDER_PATH:
            raise FixtureError("native-owner-order-path-mismatch")
        if binding.order_id == AJ_ORDER_ID and binding.order_path != rprofile.AJ_ORDER_PATH:
            raise FixtureError("native-owner-order-path-mismatch")
        self._binding: OrderRunBinding = binding
        self._repo = Path(str(repo))
        self._git_runner = git_runner
        self._control_dir = Path(str(control_dir))
        self._run_id = binding.run_id
        self._owner: local.LocalFixtureOwner | None = None
        self._workflow: prep.NativeHandoffWorkflow | None = None
        self._thread: threading.Thread | None = None
        self._attempt_token: str | None = None
        self._outcome: str | None = None
        self._published = False
        # the AF native attach-binding phase state (017-ae
        # software): the frozen attach-baseline observation
        # (collected exactly ONCE) and the derived attach-
        # binding receipt (frozen on first success, never
        # resettable, never re-derived), the ONE-SHOT attempt
        # latches (consumed BEFORE each measurement) and the
        # retained failed-phase refusal (a refused
        # measurement forbids any later fresh baseline or
        # second observation) — all in THIS SAME owner RAM
        # context over the shared absolute END anchor and
        # ledger
        self._attach_baseline: prep.DevptsObservation | None = None
        self._attach_receipt: dict[str, object] | None = None
        self._attach_baseline_attempted = False
        self._attach_derive_attempted = False
        self._attach_failure: str | None = None
        # the completed owner's publication is a ONE-SHOT
        # terminal transition (order 017-w section 3): once it
        # begins, a refusal terminalizes the qualified attempt
        # and no later call may retry it on a fresh path
        self._publication_attempted = False
        # 1. EXACTLY ONCE in the order's stable one-attempt
        # namespace, BEFORE any external mutation: the
        # admission re-validates the ACTUAL repository,
        # committed active/order content, literal head and
        # repository identity against the frozen binding — a
        # stale, foreign or exhausted binding is a closed
        # refusal before the owner exists.
        oap_binding.admit_order_attempt(self._repo, binding.order_id, binding, git_runner)
        # 2. The REAL fixture owner: the order-bound authority
        # checks stay live (the historical S opt-in for the
        # 017-s binding, the distinct native authority path for
        # a new-order binding); the run identity is the
        # binding's minted one (verified live bound admission;
        # no second mint, no second admission); the protected
        # control root and the owner's own evidence destination
        # are the owner's, unchanged.
        # 3. The public native workflow: NO predicted native
        # PID/expectation at construction — the actual later
        # subject is registered through the public staged
        # entry after the separately measured stop.
        # A constructor failure AFTER winning the admission must
        # close THAT SAME run honestly (a terminal fail record —
        # never an orphan running claim); the primary closed
        # refusal propagates unchanged.
        try:
            self._owner = local.LocalFixtureOwner(
                self._repo,
                work,
                owner_evidence_out,
                binding.source_head,
                self._control_dir,
                git_runner=git_runner,
                executor=executor,
                deadline_offset=deadline_offset,
                binding=binding,
                identity_reader=identity_reader,
                # the owner's EXISTING narrow proc seam (the
                # same bounded lifetime readers; production
                # default the actual /proc, unchanged): the
                # coherent coupled fake process world projects
                # its container-member frames there
                proc_root=proc_root,
            )
            # the FROZEN owner-UID subject identity of the
            # canonical 017-ad / 017-af / 017-ah / 017-aj
            # entries: the SAME real owner's OWN bounded OS
            # identity collection (already frozen in the
            # owner's immutable context AFTER its original won
            # admission, BEFORE external work) is applied as
            # the workflow's subject law — these runs never
            # measure the fixed 21002 subject, and the original
            # entries never collect (their context stays None,
            # the workflow keeps the fixed-21002 law
            # byte-for-byte).  A canonical owner-UID entry
            # without a frozen context is a closed refusal,
            # never a silent fallback to the original profile.
            subject_identity: tuple[int, int, tuple[int, ...]] | None = None
            if binding.order_id in (
                AD_ORDER_ID,
                AF_ORDER_ID,
                AH_ORDER_ID,
                AJ_ORDER_ID,
            ):
                ctx = self._owner._owner_context
                if ctx is None:
                    raise FixtureError("native-owner-identity-unmeasured")
                subject_identity = (
                    ctx.subject_uid,
                    ctx.subject_gid,
                    tuple(ctx.subject_groups),
                )
            self._workflow = prep.NativeHandoffWorkflow(
                binding,
                table,
                worker_pid=worker_pid,
                bash_pid=bash_pid,
                owner_run_id=self._run_id,
                tty_foreground_pgrp=tty_foreground_pgrp,
                registered_owners=registered_owners,
                subject_identity=subject_identity,
            )
        except BaseException as primary:
            try:
                oap_binding.record_order_attempt(self._repo, binding.order_id, self._run_id, "fail")
            except FixtureError:
                pass
            raise primary

    @property
    def binding(self) -> OrderRunBinding:
        return self._binding

    @property
    def run_id(self) -> str:
        return self._run_id

    @property
    def owner(self) -> local.LocalFixtureOwner:
        return self._owner  # type: ignore[return-value]

    @property
    def workflow(self) -> prep.NativeHandoffWorkflow:
        return self._workflow  # type: ignore[return-value]

    # -- the protected owner interface (the thin-caller law) --
    def _budget_end(self) -> float:
        """The ONE absolute run budget: the owner's OWN
        published END anchor plus the owner's own single
        allowed cleanup grace.  Every composition wait
        consumes the REMAINDER of that budget — no fresh
        phase window, no reset, no second fixture budget."""
        return self._owner.deadline.anchor + local.CLEANUP_GRACE_SECONDS

    def start(self) -> str:
        """Launch the owner's protected serve loop (in-process
        operator API) and wait (bounded by the owner's OWN
        END anchor plus the allowed cleanup grace) for the
        initial protected state publication; the published
        run id MUST be the binding's — the owner and the
        workflow share the one minted identity.  An expired
        budget refuses BEFORE the launch."""
        if self._thread is not None:
            raise FixtureError("native-owner-not-started")
        if self._budget_end() - time.monotonic() <= 0:
            raise FixtureError("native-owner-patience")
        self._thread = threading.Thread(target=self._owner.serve, daemon=True)
        self._thread.start()
        end = self._budget_end()
        while time.monotonic() < end:
            # the entry-aware state tag: the canonical owner-UID
            # entries publish their OWN distinct identity-bearing
            # state form and read it back under their OWN entry
            # (the original entries keep the v1 tag byte-for-byte)
            state = local._state_record(self._control_dir, entry_order=self._binding.order_id)
            if state is not None:
                if state["run_id"] != self._run_id:
                    raise FixtureError("native-owner-binding-invalid")
                return str(state["run_id"])
            if self._thread is not None and not self._thread.is_alive():
                break
            time.sleep(0.05)
        raise FixtureError("native-owner-startup")

    def _command(self, command: str) -> dict:
        """ONE bounded command against the SAME owner run
        context over the protected interface: the budget is
        the owner's OWN published END anchor plus the owner's
        own single allowed cleanup grace (an expired
        anchor refuses BEFORE any IO — the budget is never
        refreshed).  A refusal response carries the owner's
        own closed token (propagated, never reworded)."""
        if self._thread is None:
            raise FixtureError("native-owner-not-started")
        state = local._state_record(self._control_dir, entry_order=self._binding.order_id)
        if state is None or state["run_id"] != self._run_id:
            raise FixtureError("native-owner-not-started")
        anchor = float(state["end_anchor"])
        remaining = anchor + local.CLEANUP_GRACE_SECONDS - time.monotonic()
        if remaining <= 0:
            raise FixtureError("native-owner-patience")
        # The FROZEN owner context (the owner's OWN verified
        # binding's closed entry, collected before any external
        # work) is the control-response entry authority: the
        # canonical owner-UID entries validate under their OWN
        # frozen entry (the AJ entry declares the closed
        # format-capture scenario), and the original entries
        # keep the historical generic default (None) — many
        # original orders are not in the owner-UID allowlist
        # and are never suddenly refused.
        frozen_entry = (
            self._owner._owner_context.order_id if self._owner._owner_context is not None else None
        )
        response = local._control_client(
            self._control_dir,
            command,
            self._run_id,
            min(local._CLIENT_TIMEOUT, remaining),
            entry_order=frozen_entry,
        )
        if isinstance(response, dict) and response.get("ok") is False:
            reason = response.get("reason")
            if isinstance(reason, str) and reason in local._FAILURE_REASONS:
                raise FixtureError(reason)
            raise FixtureError("internal")
        return response  # type: ignore[no-any-return]

    def _settle(self) -> None:
        """The owner converges its own exact-owned cleanup on
        its own budgets (the terminal command returns only
        after the convergence disposition); a bounded join
        reaps the serve loop within the REMAINDER of the
        owner's ONE absolute run budget (its END anchor plus
        the allowed cleanup grace — never a fresh phase
        window) — the owner is never signalled or killed by
        the composition."""
        if self._thread is not None:
            remaining = self._budget_end() - time.monotonic()
            if remaining <= 0:
                raise FixtureError("native-owner-settle")
            self._thread.join(remaining)
            if self._thread.is_alive():
                raise FixtureError("native-owner-settle")

    # -- the bounded public lifecycle --
    def prepare(self) -> dict:
        """Prepare the exact target CID (held, unconsumed)
        through the owner's REAL prepare path, THEN freeze
        the measured W/B birth/group/session/TTY baseline
        through the workflow — the native PID is NOT yet
        predicted (staged registration is the operator's
        later entry)."""
        self._command("prepare")
        return self._workflow.prepare()  # type: ignore[union-attr]

    def observe(self) -> dict:
        """The bounded NON-CONSUMING held observation: the
        owner's closed controller state (no model POST, no
        charge, no state change) and the workflow's
        re-collected read-only facts — repeated observation
        stays useful/idempotent (the retained receipt is
        never re-measured into)."""
        self._command("observe")
        return self._workflow.observe()  # type: ignore[union-attr]

    def register_subject(
        self,
        subject_pid: object,
        expectation: object,
        *,
        channel: prep.CidScopedTable | None = None,
    ) -> dict:
        """The PUBLIC staged registration of the actual
        later native subject.  BEFORE any staged receipt
        commit the operator's expectation is bound to THIS
        SAME prepared owner's measured registration (order
        017-w section 1): the owner's own registered CID and
        artifact binary must already be measured, and the
        expectation must equal them exactly — a caller's
        matching foreign expectation + foreign channel, or a
        matching foreign expected + measured binary, cannot
        redefine this owner's subject (the collector proves
        agreement with the expectation, never with the
        owner's registration); unknown or incomplete owner
        facts close.  A refused registration commits nothing
        (no baseline, receipt or stop change) and a later
        genuinely matching registration within the same
        still-valid measured phase remains possible; the
        workflow's public staged entry then applies its own
        gates: prepared, the separately measured stop
        recorded, the CURRENT stable stopped phase still
        holding, the frozen W/B baseline unchanged, the
        registered run immutable, the collectors invoked
        before any commit."""
        owner = self._owner
        workflow = self._workflow
        if owner is None or workflow is None:
            raise FixtureError("native-owner-not-started")
        # the FROZEN owner context is revalidated at THIS
        # identity-bound use site as well (the same bounded
        # current-ID coherence read as prepare/finish —
        # compared, never rebased): a host identity that
        # drifted after the measured stop cannot register a
        # subject on the frozen context (the original profile
        # keeps its context None and is a no-op, unchanged)
        owner._revalidate_identity_context()
        if isinstance(expectation, prep.SubjectExpectation):
            artifact = owner.artifact
            if (
                not isinstance(owner.target_cid, str)
                or not isinstance(artifact, dict)
                or not isinstance(artifact.get("binary_sha256"), str)
            ):
                # this owner's own registration is not
                # measured yet: no staged identity can be
                # bound to it (never a caller-chosen context)
                raise FixtureError("native-owner-registration-unmeasured")
            if expectation.cid != owner.target_cid:
                raise FixtureError("native-owner-subject-cid-mismatch")
            if expectation.binary_sha256 != artifact["binary_sha256"]:
                raise FixtureError("native-owner-subject-binary-mismatch")
        # The AF / AH / AJ entry's attach-binding gate
        # (017-ae; the AJ entry 017-ai): the
        # measured attach receipt must already exist (no
        # resampling at registration — the allocation is
        # measured ONCE in the attach phase), and the
        # expectation's expected PTY must equal the DERIVED
        # expected tty_nr exactly (the expected PTY comes
        # from the owned attach, never from the subject
        # itself; an unobserved or foreign expectation can
        # never bind the entry).  A refused registration
        # may retry CORRECTED parameters against the SAME
        # already-measured receipt (the workflow's staged
        # law), never a resampled allocation.
        if self._binding.order_id in (AF_ORDER_ID, AH_ORDER_ID, AJ_ORDER_ID):
            if self._attach_receipt is None:
                raise FixtureError("native-owner-attach-binding-missing")
            if not isinstance(expectation, prep.SubjectExpectation) or not (
                isinstance(expectation.expected_tty, int)
                and not isinstance(expectation.expected_tty, bool)
                and expectation.expected_tty == self._attach_receipt["expected_tty_nr"]
            ):
                raise FixtureError("native-owner-attach-pty-mismatch")
            # the DERIVED expected tty_nr is re-checked against
            # the allocation's OWN device identity (the closed
            # encoding of the owned device must equal the
            # derived value and qualify — a context
            # contradiction is a closed refusal, never a
            # silently re-derived expectation)
            allocation = self._attach_receipt["allocation"]
            try:
                encoded = prep.new_encode_dev(allocation["major"], allocation["minor"])
            except prep.FixtureError:
                raise FixtureError("native-owner-attach-context-invalid") from None
            if not (
                encoded == self._attach_receipt["expected_tty_nr"]
                and prep.expected_tty_nr_qualifies(encoded)
            ):
                raise FixtureError("native-owner-attach-context-invalid")
            # the ORIGINAL W/B baseline + CURRENT stable-stop
            # phase, the FROZEN owner identity and the SAME
            # absolute owner END are re-verified at this
            # actual PRE-COMMIT use site (the retained stop
            # receipt is re-verified, never replaced)
            self._verify_attach_phase()
            owner._revalidate_identity_context()
            if owner.deadline.anchor - time.monotonic() <= 0:
                raise FixtureError("native-owner-patience")
            # the AF / AH / AJ entry measures through its
            # OWN default exact registered-CID channel ONLY:
            # a caller-supplied channel is a closed refusal
            # (no bypass of the scoped/birth-bound reads)
            if channel is not None:
                raise FixtureError("native-owner-attach-channel-invalid")
        # The AD entry's closed native executable-measurement
        # bound: when the operator did not supply an owned
        # channel, the composition constructs the REAL scoped
        # channel bound to THIS owner's own registered CID with
        # the 017-ad bounds (exactly 320 MiB / 10 s per
        # measurement) clamped to the SAME ABSOLUTE owner END
        # anchor — the owner END ONLY (the cleanup grace is
        # convergence, never fresh measurement), checked at
        # EVERY actual read/return of the channel (a relative
        # captured duration could never refresh the window).
        # The original entries keep their historical channel
        # law byte-for-byte (an absent channel stays absent, no
        # AD default applies to them).
        if channel is None and self._binding.order_id in (
            AD_ORDER_ID,
            AF_ORDER_ID,
            AH_ORDER_ID,
            AJ_ORDER_ID,
        ):
            if not isinstance(owner.target_cid, str):
                raise FixtureError("native-owner-registration-unmeasured")
            end = self._owner.deadline.anchor
            if end - time.monotonic() <= 0:
                raise FixtureError("native-owner-patience")
            channel = build_ad_native_channel(owner.target_cid, end)
        if self._binding.order_id in (AF_ORDER_ID, AH_ORDER_ID, AJ_ORDER_ID):
            # the MEASURED native namespace/device frame: the
            # subject's own mount view compared against the
            # independently measured private allocation
            # context BEFORE the workflow's staged collection
            # (equal tty numbers alone are never sufficient)
            if channel is None:
                # unreachable: the AF branch above refused a
                # caller channel and the default block built
                # one — an internal contradiction, never a
                # silent host-unscoped measurement
                raise FixtureError("internal")
            af_channel = channel
            self._verify_af_devpts_namespace(subject_pid, af_channel)
            # the FINAL frames run at the workflow's OWN
            # collect-before-commit boundary (after the
            # possibly-long executable measurement, before ANY
            # subject/baseline/stop commit) — a change during
            # hashing or the last metadata frame refuses with
            # NO workflow change
            snapshot = workflow.register_subject(
                subject_pid,
                expectation,
                channel=af_channel,
                pre_commit_check=lambda subject: self._af_pre_commit_check(subject, af_channel),
            )
        else:
            snapshot = workflow.register_subject(subject_pid, expectation, channel=channel)
        return snapshot

    def record_stop(self) -> prep.StopReceipt:
        """Record the SEPARATELY MEASURED worker-stop event
        (read-only; the stop itself is performed later by
        the separately authorized operator) — a recorded
        event, never re-derived from a later snapshot."""
        return self._workflow.record_stop()  # type: ignore[union-attr]

    def _verify_attach_phase(self) -> None:
        """The AF attach-phase world-coherence re-check
        (017-ae software): the ORIGINAL W/B prepare baseline
        must still be the same worker job and the CURRENT
        bounded stable-stop predicate must still hold
        (predicate-only re-measurement — the retained stop
        receipt is re-verified, never replaced or
        re-measured into).  Applied BEFORE and AFTER each
        blocking inventory/derivation: a stale, resumed or
        substituted phase can never open an inventory or
        carry one out."""
        workflow = self._workflow
        if workflow is None:
            raise FixtureError("native-owner-attach-stale-stop")
        workflow.verify_stable_stop_phase()

    def _verify_af_devpts_namespace(
        self,
        subject_pid: object,
        channel: prep.CidScopedTable,
        *,
        birth: int | None = None,
    ) -> None:
        """The AF registration's MEASURED native devpts
        namespace/device frame (017-ae software): the
        subject's OWN mount view (``/proc/<pid>/root/dev/pts``
        and the selected slave — Linux documents
        ``/proc/<pid>/root`` as the subject's filesystem and
        mount view) is read READ-ONLY through the SAME
        scoped/birth-bound registered-CID channel (no new
        transport, no host ``/dev/pts`` enumeration) and
        compared against the independently measured private
        allocation context: the devpts mount root (the
        namespace), the device major/minor, the node inode,
        the node mode and the node owner.  Equal tty numbers
        alone are never sufficient: the SAME numeric tty in a
        FOREIGN devpts namespace is a closed refusal.  The
        metadata read is bound to an EXPLICIT birth: when the
        caller supplies one (the pre-commit path) it is the
        ORIGINAL collected subject's birth — a PID reused
        after collection can never re-bind itself to a fresh
        stat; when the caller supplies none (the pre-collection
        path, before any subject exists) the birth is derived
        from the ONE scoped stat read here and the read is
        still bound to it.  Access denial or an unbound frame
        is a typed unknown refusal, never an assumption;
        nothing here commits — a refused registration commits
        nothing and a later corrected registration within the
        same still-valid phase remains possible."""
        receipt = self._attach_receipt
        if receipt is None:
            raise FixtureError("native-owner-attach-binding-missing")
        allocation = receipt["allocation"]
        namespace = receipt["namespace"]
        if not prep._is_pid(subject_pid):
            raise FixtureError("native-owner-attach-devpts-unreadable")
        if birth is None:
            # pre-collection path: no subject exists yet, so the
            # birth is derived from the ONE scoped stat read
            # here (the metadata read is still bound to it)
            raw = channel.stat(subject_pid)
            if raw is None:
                raise FixtureError("native-owner-attach-devpts-unreadable")
            try:
                ps = prep.parse_proc_stat(raw.decode("ascii", "replace"))
            except prep.FixtureError:
                raise FixtureError("native-owner-attach-devpts-unreadable") from None
            # positive group/session prerequisite (zero is
            # observation data only — never the bound subject
            # of a metadata read)
            if not prep._is_pid(ps.pgrp) or not prep._is_pid(ps.session):
                raise FixtureError("native-owner-attach-devpts-unreadable")
            birth = ps.start_time
        elif not prep._is_strict_int(birth):
            raise FixtureError("native-owner-attach-devpts-unreadable")
        meta = channel.devpts_slave_metadata(subject_pid, birth, allocation["name"])
        if meta is None:
            raise FixtureError("native-owner-attach-devpts-unreadable")
        if (meta.root_dev, meta.root_ino) != (namespace[0], namespace[1]):
            raise FixtureError("native-owner-attach-devpts-namespace-mismatch")
        # the selected node must live on the SAME filesystem as
        # the measured devpts root: a node from a different
        # filesystem can carry an equal inode/mode/owner
        if meta.slave_dev != namespace[0]:
            raise FixtureError("native-owner-attach-devpts-namespace-mismatch")
        if (meta.major, meta.minor) != (allocation["major"], allocation["minor"]):
            raise FixtureError("native-owner-attach-devpts-device-mismatch")
        if meta.slave_ino != allocation["inode"]:
            raise FixtureError("native-owner-attach-devpts-inode-mismatch")
        # the measured fact is the FULL stat mode (file-type
        # bits included); the allocation carries the
        # PERMISSION BITS — normalize consistently
        if (meta.slave_mode & 0o7777) != allocation["mode"]:
            raise FixtureError("native-owner-attach-devpts-mode-mismatch")
        if (meta.slave_uid, meta.slave_gid) != (allocation["uid"], allocation["gid"]):
            raise FixtureError("native-owner-attach-devpts-owner-mismatch")

    def _af_pre_commit_check(
        self, subject: prep.SubjectIdentity, channel: prep.CidScopedTable
    ) -> None:
        """The FINAL measured AF frames at the workflow's
        collect-before-commit boundary (017-ae software): they
        run AFTER the possibly-long executable measurement and
        BEFORE any subject/baseline/stop commit — a
        namespace/device, identity, frozen-ID, current-stop or
        original-END change during hashing or the last
        metadata frame refuses with NO workflow subject/
        baseline/stop change (the staged law).  The frames:
        the CURRENT native-identity frame re-verified against
        the COLLECTED identity (a PID reused after collection,
        or a drifted UID/GID/groups/argv/tty, can never carry
        the final frames — a reused PID is never compared
        with itself via a fresh stat), the re-read devpts
        namespace/device BOUND TO THE ORIGINAL collected
        PID/birth, the current-executable race law (the ACTUAL
        running executable re-measured through the SAME
        scoped channel must still be the collected measured
        binary — an in-place exec with unchanged PID/birth is
        a closed refusal), the collected subject's OWN
        measured tty (the collector's own pty binding — a
        matching foreign expectation can never mint it), the
        frozen owner identity at this final use site, the
        CURRENT stable-stop phase (predicate-only — the
        retained receipt is re-verified, never replaced) and
        the SAME absolute owner END."""
        receipt = self._attach_receipt
        if receipt is None:
            raise FixtureError("native-owner-attach-binding-missing")
        owner = self._owner
        if owner is None:
            raise FixtureError("native-owner-not-started")
        # 0) the CURRENT native-identity frame must still be
        #    the COLLECTED identity (PID reuse / native ID /
        #    argv / tty drift after collection is a closed
        #    refusal BEFORE any final frame is trusted)
        self._verify_af_identity_frame(subject, channel)
        # 1) the FINAL devpts namespace/device frame, bound to
        #    the ORIGINAL collected PID/birth (never a fresh
        #    self-binding read)
        self._verify_af_devpts_namespace(subject.pid, channel, birth=subject.start_time)
        # 2) the current-executable race law across the final
        #    metadata phase: the ACTUAL running executable,
        #    re-measured through the SAME scoped/birth-bound
        #    channel, must still be the collected measured
        #    binary (an in-place exec with unchanged PID/birth
        #    is a closed refusal, never a stale verified
        #    identity)
        try:
            current_exe = channel.exe_sha256(subject.pid, subject.start_time)
        except FixtureError:
            raise FixtureError("native-owner-attach-identity-drift") from None
        if current_exe != subject.binary_sha256:
            raise FixtureError("native-owner-attach-identity-drift")
        # 3) the devpts frame is re-read AFTER the executable
        #    re-measurement as well: a namespace/device change
        #    DURING the final hash cannot leave the collected
        #    frame stale at commit (still bound to the
        #    ORIGINAL collected PID/birth)
        self._verify_af_devpts_namespace(subject.pid, channel, birth=subject.start_time)
        # 4) the identity frame is re-verified AFTER these
        #    blocking operations as well: a UID/GID/groups/
        #    argv/tty drift DURING the final metadata/hash
        #    cannot leave the collected frame stale at commit
        self._verify_af_identity_frame(subject, channel)
        # 5) the collected subject's own tty frame
        if subject.pty_matched is not True or subject.tty != receipt["expected_tty_nr"]:
            raise FixtureError("native-owner-attach-pty-mismatch")
        # 6) the frozen owner identity at THIS final use site
        owner._revalidate_identity_context()
        # 7) the CURRENT stable-stop phase
        self._verify_attach_phase()
        # 8) the SAME absolute owner END (never the cleanup
        #    grace, never a captured duration)
        if owner.deadline.anchor - time.monotonic() <= 0:
            raise FixtureError("native-owner-patience")

    def _verify_af_identity_frame(
        self, subject: prep.SubjectIdentity, channel: prep.CidScopedTable
    ) -> None:
        """The FINAL native-identity frame re-validation
        (017-ae software): the CURRENT scoped view of the
        subject (stat/cmdline/status through the SAME
        registered-CID channel) must still be the COLLECTED
        identity — the birth (a PID reused after collection
        has a different birth), the tty, the UID/GID/groups
        and the exact argv.  Any drifted or unreadable frame
        is a closed refusal: the final metadata frames run
        ONLY for the process that was collected, never for a
        successor at the same number."""
        raw_stat = channel.stat(subject.pid)
        raw_cmdline = channel.cmdline(subject.pid)
        raw_status = channel.status(subject.pid)
        if raw_stat is None or raw_cmdline is None or raw_status is None:
            raise FixtureError("native-owner-attach-identity-drift")
        try:
            ps = prep.parse_proc_stat(raw_stat.decode("ascii", "replace"))
            argv = prep.parse_proc_cmdline(raw_cmdline)
            uid, gid, groups = prep.parse_proc_status(raw_status)
        except prep.FixtureError:
            raise FixtureError("native-owner-attach-identity-drift") from None
        if (
            ps.start_time != subject.start_time
            or ps.tty != subject.tty
            # the POSITIVE pgrp/session prerequisite the parser
            # used to supply implicitly: a now-parseable zero
            # group/session frame is still not this subject
            # (zero observation data never carries the final
            # frame, however the other fields match)
            or not prep._is_pid(ps.pgrp)
            or not prep._is_pid(ps.session)
            or (uid, gid, tuple(groups)) != (subject.uid, subject.gid, subject.groups)
            or tuple(argv) != subject.argv
        ):
            raise FixtureError("native-owner-attach-identity-drift")

    def collect_attach_baseline(self) -> prep.DevptsObservation:
        """The AF / AH / AJ attach-baseline collection
        (017-ae software; the AJ entry 017-ai): after prepare
        and the separately measured
        stop, the owner's ONE bounded devpts inventory
        freezes the attach-baseline snapshot.  The phase is
        ONE-SHOT and NON-RESETTABLE: the attempt is consumed
        BEFORE the measurement (exactly one baseline per
        run), a refused measurement retains a failed phase
        that forbids ANY later fresh baseline or second
        observation (a resampled world could hide a churn or
        multiple-allocation refusal), and the baseline is
        never re-measured or replaced after success.  The
        original W/B baseline and the current stable stop are
        re-verified before AND after the blocking inventory;
        a pre-stop baseline is refused (the stop is the phase
        boundary — a stale stop is a closed refusal, never a
        valid baseline).  The frozen identity is revalidated
        at the owner's actual use site; the budget is the
        owner's OWN absolute END anchor (no grace, no fresh
        phase window)."""
        if self._binding.order_id not in (AF_ORDER_ID, AH_ORDER_ID, AJ_ORDER_ID):
            raise FixtureError("native-owner-attach-not-admitted")
        if (
            self._attach_baseline_attempted
            or self._attach_failure is not None
            or self._attach_baseline is not None
        ):
            raise FixtureError("native-owner-attach-baseline-repeat")
        owner = self._owner
        workflow = self._workflow
        if owner is None or workflow is None or self._thread is None:
            raise FixtureError("native-owner-not-started")
        if workflow.stop_receipt is None:
            raise FixtureError("native-owner-attach-stale-stop")
        if owner.deadline.anchor - time.monotonic() <= 0:
            raise FixtureError("native-owner-patience")
        self._verify_attach_phase()
        # the attempt is consumed BEFORE the measurement: a
        # refused inventory still closes the phase (no fresh
        # baseline, no second observation, ever).  The
        # observation stays TEMPORARY until every
        # post-measurement check passes; a post-measurement
        # refusal retains a failed phase and commits NO
        # usable baseline
        self._attach_baseline_attempted = True
        try:
            observation = owner.devpts_inventory()
            self._verify_attach_phase()
            # the final frozen-ID and END checks: a drifted
            # identity or a crossed END after the measurement
            # can never commit the baseline
            owner._revalidate_identity_context()
            if owner.deadline.anchor - time.monotonic() <= 0:
                raise FixtureError("native-owner-patience")
        except FixtureError as exc:
            self._attach_failure = str(exc)
            raise
        # commit ONLY after all post-measurement checks pass
        self._attach_baseline = observation
        return self._attach_baseline

    def derive_attach_expectation(self) -> dict[str, object]:
        """The AF / AH / AJ attach expectation derivation
        (017-ae software; the AJ entry 017-ai): ONE further
        bounded inventory observation after the frozen
        baseline; the unique fresh owned allocation is
        derived by the pure core
        and the DISTINCT identity-bearing attach-binding
        receipt is frozen (its expected proc tty_nr is the
        derived expected PTY — the provenance the later
        registration expectation must bind to).  The
        second observation is ONE-SHOT and NON-RESETTABLE:
        the attempt is consumed BEFORE the measurement, and
        a refused derivation retains a failed phase that
        forbids ANY later fresh baseline or second
        observation (a resampled world could hide a churn or
        multiple-allocation refusal — only a LATER
        registration may retry corrected parameters against
        the SAME already-measured receipt, never resampling
        allocations).  The receipt and the public copy are
        built INSIDE the failure-handled region and stay
        TEMPORARY: the ORIGINAL W/B baseline and the current
        stable stop are re-verified after the blocking
        observation, and the final frozen-owner-identity and
        END checks run in the same region; the private
        receipt is committed ONLY after every post-measurement
        check passes (a post-measurement refusal retains a
        failed phase and commits no usable receipt).  The
        retained receipt is private measured context: the
        returned value is a protected copy (caller mutation
        can never alter the retained evidence).  The frozen
        identity is revalidated at the owner's actual use
        site; the budget is the owner's OWN absolute END
        anchor."""
        if self._binding.order_id not in (AF_ORDER_ID, AH_ORDER_ID, AJ_ORDER_ID):
            raise FixtureError("native-owner-attach-not-admitted")
        owner = self._owner
        if owner is None or self._thread is None:
            raise FixtureError("native-owner-not-started")
        if self._attach_baseline is None:
            raise FixtureError("native-owner-attach-baseline-missing")
        if (
            self._attach_derive_attempted
            or self._attach_failure is not None
            or self._attach_receipt is not None
        ):
            raise FixtureError("native-owner-attach-binding-repeat")
        if owner.deadline.anchor - time.monotonic() <= 0:
            raise FixtureError("native-owner-patience")
        ctx = owner._owner_context
        if ctx is None:
            raise FixtureError("native-owner-identity-unmeasured")
        self._verify_attach_phase()
        # the attempt is consumed BEFORE the measurement: a
        # refused observation/derivation still closes the
        # phase (no resampling, ever)
        self._attach_derive_attempted = True
        receipt: dict[str, object] | None = None
        public_receipt: dict[str, object] | None = None
        try:
            observation = owner.devpts_inventory()
            allocation = prep.derive_attach_allocation(
                self._attach_baseline.inventory,
                observation.inventory,
                subject_uid=ctx.subject_uid,
            )
            identity = prep._ad_identity_substructure_from_triple(
                (ctx.subject_uid, ctx.subject_gid, tuple(ctx.subject_groups))
            )
            receipt = prep.attach_binding_record(
                baseline=self._attach_baseline,
                observation=observation,
                allocation=allocation,
                binding=self._binding,
                identity=identity,
                cid=owner.target_cid,
            )
            # the PUBLIC copy of the closed record is prepared
            # INSIDE the failure-handled region, BEFORE the
            # final post-measurement checks: a record that
            # cannot be copied leaves the consumed attempt
            # with a retained failed phase, exactly like any
            # other refusal in this region
            public_receipt = json.loads(json.dumps(receipt, sort_keys=True))
            # the ORIGINAL W/B baseline + CURRENT stable-stop
            # phase AFTER the observation (the retained stop
            # receipt is re-verified, never replaced); the
            # final frozen-owner-identity and END checks: a
            # resumed worker, a drifted identity or a crossed
            # END after the measurement can never commit the
            # receipt
            self._verify_attach_phase()
            owner._revalidate_identity_context()
            if owner.deadline.anchor - time.monotonic() <= 0:
                raise FixtureError("native-owner-patience")
        except (FixtureError, TypeError, ValueError) as exc:
            # EVERY refusal in this region — the measurement,
            # the copy preparation or a post-measurement
            # check — retains a failed phase and commits NO
            # usable receipt (the attempt stays consumed — no
            # resampling, ever)
            self._attach_failure = str(exc)
            raise
        # commit the private receipt ONLY after all
        # post-measurement checks pass; the returned value is
        # the prepared PUBLIC copy: the retained private
        # receipt is the measured context, and a
        # copied/caller/replayed record never mints authority
        assert receipt is not None and public_receipt is not None
        self._attach_receipt = receipt
        return public_receipt

    def finish(self) -> None:
        """FINISH the held instance through the owner's REAL
        finish/export/teardown path (always converges);
        the exact CID removal is what removes the native
        subject from the coupled process world (the fake
        side effect in this round, the measured teardown on
        the real backend)."""
        self._command("finish")
        self._settle()

    def abort(self) -> None:
        """The honest ABORT (converges now as a truthful
        abort; the attempt stays recorded)."""
        self._command("abort")
        self._settle()

    # -- the native-scope terminal record --
    def owner_outcome(self) -> str:
        """The owner's TERMINAL outcome, read from the SAME
        completed owner state (the owner's own convergence set
        it; pass/fail/aborted — the closed outcome
        vocabulary).  The same-order attempt journal is the
        durable record, NOT a prerequisite for deriving this
        outcome (no circular journal dependency); a
        non-converged or non-terminal owner is a closed
        refusal, never a guessed outcome."""
        owner = self._owner
        if owner is None:
            raise FixtureError("native-owner-not-started")
        outcome = owner.terminal_outcome
        if isinstance(outcome, str) and outcome in NATIVE_RUN_OUTCOMES:
            return outcome
        raise FixtureError("native-owner-not-terminal")

    def finalize_attempt(self) -> str:
        """The same-order journal finalization token
        (idempotent).  The terminal PASS is written ONLY
        after the protected native record is retained by
        publish_native; a terminal owner outcome (fail/
        aborted) was already honestly finalized at owner
        convergence (an idempotent no-op here).  Before a
        successful publication this can never admit a pass.
        The REAL returned token is retained in RAM/result —
        the immutable retained evidence is never rewritten."""
        if self._attempt_token is not None:
            return self._attempt_token
        if not self._published or self._outcome is None:
            raise FixtureError("native-owner-not-terminal")
        self._attempt_token = oap_binding.record_order_attempt(
            self._repo, self._binding.order_id, self._run_id, self._outcome
        )
        return self._attempt_token

    def _verify_journal_for_publication(self, outcome: str) -> str:
        """Read the ACTUAL bound journal state for this run
        (never a hardcoded assumption from the owner
        outcome) and return the honest ``attempt`` field the
        record about to be retained carries:

        - pass: the bound attempt must still be RUNNING —
          the terminal pass finalization follows the
          successful protected publication, so an early
          finalization, an already-terminal journal or an
          unreadable record cannot admit pass;
        - terminal owner outcome: the journal must already
          carry that SAME terminal outcome (recorded at
          convergence — carried as "terminal-preserved"), or
          still be running (finalized honestly NOW, the real
          returned token required to be "finalized"); a
          contradicting terminal state is a closed refusal.

        The returned value is the journal state itself,
        never a predicted finalize token."""
        try:
            record = oap_binding.read_admission_record(self._repo, self._binding.order_id)
        except FixtureError:
            raise FixtureError("native-owner-journal-unverified") from None
        state: str | None = None
        for entry in record["attempts"]:
            if entry.get("run_id") == self._run_id:
                state = entry.get("status")
                break
        if state is None:
            raise FixtureError("native-owner-journal-unverified")
        if outcome == "pass":
            if state != "running":
                raise FixtureError("native-owner-journal-unverified")
            return "running"
        if state == outcome:
            return "terminal-preserved"
        if state == "running":
            token = oap_binding.record_order_attempt(
                self._repo, self._binding.order_id, self._run_id, outcome
            )
            if token != "finalized":
                raise FixtureError("native-owner-finalization-unverified")
            return "finalized"
        raise FixtureError("native-owner-journal-unverified")

    def _close_attempt_on_publication_failure(self, outcome: str) -> None:
        """A publication failure at the completed-run boundary
        terminalizes the qualified attempt honestly: a
        still-pending bound attempt is closed — as a fail for
        an unpublished pass (a failed native publication never
        leaves an admitted pass), as the SAME honest terminal
        outcome for a terminal owner failure — and an
        already-terminal journal is preserved (never rewritten,
        never relabeled, never reset for a retry)."""
        status = "fail" if outcome == "pass" else outcome
        try:
            oap_binding.record_order_attempt(
                self._repo, self._binding.order_id, self._run_id, status
            )
        except FixtureError:
            pass

    def publish_native(self, native_evidence_out: object) -> dict:
        """Publish the EXPLICIT native-scope terminal record
        for this run (closed schema
        ``slaif-native-owner-run-v1``, 0600 under the
        caller's protected evidence root, OUTSIDE the owner's
        disposable work root) with the HONEST ONE-SHOT
        publication transition (order 017-w section 3):

        1. the owner's terminal outcome is read from the SAME
           completed owner state (no circular journal
           dependency);
        2. the record is built from that state and the
           MEASURED verdict; the measured native-owner record
           is produced through the EXISTING
           producer/consumer ONLY where its measured
           prerequisites hold (a pass-converged owner, the
           retained pre-teardown subject receipt, the
           recorded stop, and the owner's own registered
           CID/image/binary context) — the producer is never
           fed fabricated starts;
        3. the ACTUAL bound journal state for this run is
           read — never assumed from the outcome: the pass
           path requires the bound attempt still RUNNING
           (the terminal pass finalization follows the
           successful protected publication; an early,
           already-terminal or unreadable journal cannot
           admit pass); a terminal owner outcome requires
           that SAME terminal outcome already recorded
           (carried as "terminal-preserved") or a still-
           running attempt finalized honestly NOW with the
           real verified token;
        4. once the COMPLETED owner's terminal outcome is read
           the attempt is marked PUBLICATION-ATTEMPTED: from
           then on EVERY failure is terminal for this
           qualified attempt and no later call (fresh path or
           not) may create a new qualifying record, relabel
           the attempt or reset the journal.  A PRE-RETENTION
           failure (verdict measurement, record validation,
           serialization, a destination or writer refusal)
           additionally closes the still-pending attempt
           truthfully — the primary closed refusal propagates
           unchanged, and an unexpected serialization error
           surfaces as the module's own "internal" token;
        5. the protected native record is retained FIRST and
           ONLY THEN the same-order journal is finalized:
           the terminal pass admits ONLY the real returned
           token "finalized"; a terminal owner outcome
           accepts the honest idempotent tokens (already
           final, or just finalized above).  A POST-RETENTION
           unverified or raced finalization is a CLOSED
           failure that preserves the immutable retained
           bytes AND the actual journal facts as-is (the
           journal is never overwritten, relabeled or
           re-closed by this path) and never returns a
           normal qualified success.  The REAL returned
           finalize token is retained in RAM/result
           (finalize_attempt) — the immutable retained
           evidence is never rewritten to insert it.

        Preparation-only, not-started and failure outcomes
        are represented honestly under this distinct closed
        scope, and the owner's cleanup/export outcome stays
        DISTINCT from the full handoff/restoration verdict
        (the owner's own terminal record is the qualifying
        owner publication; this record is the composition's
        native-scope terminal record).  The verdict is
        composed AFTER the owner's teardown and the
        independently measured same-worker restoration (the
        operator restores the same job before publication),
        with the subject's post-teardown ABSENCE verified on
        the read-only table."""
        if self._published:
            raise FixtureError("native-owner-published")
        if self._publication_attempted:
            # the completed owner's publication is a ONE-SHOT
            # terminal transition: a failed or already
            # published attempt never retries on a fresh path
            # (no new qualifying record, no relabel, no
            # journal reset)
            raise FixtureError("native-owner-published")
        owner = self._owner
        workflow = self._workflow
        if owner is None or workflow is None or self._thread is None:
            raise FixtureError("native-owner-not-started")
        outcome = self.owner_outcome()
        self._outcome = outcome
        # The ONE-SHOT transition begins for the COMPLETED
        # owner (see the docstring): EVERY failure from here
        # — verdict measurement, record validation,
        # serialization, destination/writer refusal,
        # unverified or raced finalization — terminalizes
        # this qualified attempt truthfully and blocks any
        # fresh-path retry; the primary closed refusal
        # propagates unchanged.
        self._publication_attempted = True
        try:
            # The AJ owner-FIRST publication ordering (017-ai):
            # the protected selected native capture is the
            # SECOND publication and it requires the FIRST
            # owner evidence actually retained by this SAME
            # completed owner's own protected writer — the
            # owner's RAM retention receipt, set only after
            # the protected writer returned verified success
            # (independent of the cleanup/evidence status: a
            # cleanup-failed or aborted owner whose failure
            # evidence WAS retained keeps its representable
            # honest-failure publication, and a post-commit
            # unverified result never sets the receipt even
            # when the bytes reached the destination).  A
            # precomputed digest or a merely existing
            # matching file is not a retention receipt.  The
            # refusal is BEFORE any AJ native/capture
            # destination is created; the one-shot transition
            # is preserved (the refused attempt stays
            # terminal, no fresh-path retry) and the
            # historical entry behavior is unchanged.
            if self._binding.order_id == AJ_ORDER_ID and not owner._evidence_retained:
                raise FixtureError("native-owner-evidence-unretained")
            subject = workflow.subject_receipt
            stop_recorded = workflow.stop_receipt is not None
            native_record: dict | None = None
            native_refusal: str | None = None
            # The frozen owner identity substructure of the
            # DISTINCT 017-ad / 017-af / 017-ah / 017-aj
            # identity-bearing
            # records: derived from THIS owner's OWN immutable
            # context (the real owner's own bounded OS
            # identity collection and production-code
            # derivation — never caller-authored, never re-
            # frozen here); None for the original entries,
            # whose records keep their exact historical key
            # set (no identity key at all).
            owner_identity: dict | None = None
            if self._binding.order_id in (
                AD_ORDER_ID,
                AF_ORDER_ID,
                AH_ORDER_ID,
                AJ_ORDER_ID,
            ):
                ctx = owner._owner_context
                if ctx is None:
                    # an AD / AF / AH / AJ run without the frozen
                    # context can never mint an honest
                    # identity-bearing record: a closed
                    # refusal, never a fallback to the
                    # original fixed-21002 form
                    native_refusal = "native-owner-identity-unmeasured"
                else:
                    owner_identity = {
                        "profile": ctx.profile.profile,
                        "fingerprint": ctx.fingerprint,
                        "subject_uid": ctx.subject_uid,
                        "subject_gid": ctx.subject_gid,
                        "subject_groups": list(ctx.subject_groups),
                        "profile_data_sha256": ctx.profile_data_sha256,
                    }
            if (
                outcome == "pass"
                and subject is not None
                and stop_recorded
                and (
                    self._binding.order_id
                    not in (AD_ORDER_ID, AF_ORDER_ID, AH_ORDER_ID, AJ_ORDER_ID)
                    or owner_identity is not None
                )
            ):
                measurement = prep.OwnedOwnerMeasurement(owner, subject=subject)
                artifact = owner.artifact
                if (
                    owner.target_cid is None
                    or owner.image_id is None
                    or not isinstance(artifact, dict)
                    or not isinstance(artifact.get("binary_sha256"), str)
                ):
                    # the declared context is derived from
                    # the owner's OWN registration: an
                    # unmeasured component is a closed honest
                    # refusal, never a caller-chosen string
                    native_refusal = "prep-native-owner-context-mismatch"
                else:
                    try:
                        native_record = prep.produce_native_owner_record(
                            measurement,
                            order=self._binding.order_id,
                            source_head=self._binding.source_head,
                            run_id=self._run_id,
                            cid=owner.target_cid,
                            image_id=owner.image_id,
                            binary_sha256=artifact["binary_sha256"],
                            identity=owner_identity,
                        )
                    except FixtureError as exc:
                        # the producer's closed token,
                        # propagated, never reworded
                        native_refusal = str(exc)
            verdict = workflow.finalize(native_record)
            journal_state = self._verify_journal_for_publication(outcome)
            # The DISTINCT identity-bearing terminal tag of
            # the canonical 017-ad / 017-af / 017-ah /
            # 017-aj entries (the SAME closed measured facts
            # PLUS the frozen owner-identity substructure;
            # the AF / AH / AJ entries ADDITIONALLY carry the
            # nested
            # attach-binding record, or an honest None); the
            # original tag keeps its exact historical key set
            # for every other entry.
            identity_entry = self._binding.order_id in (
                AD_ORDER_ID,
                AF_ORDER_ID,
                AH_ORDER_ID,
                AJ_ORDER_ID,
            )
            record_tag = (
                AD_NATIVE_RUN_SCHEMA
                if self._binding.order_id == AD_ORDER_ID
                else AF_NATIVE_RUN_SCHEMA
                if self._binding.order_id == AF_ORDER_ID
                else AH_NATIVE_RUN_SCHEMA
                if self._binding.order_id == AH_ORDER_ID
                else AJ_NATIVE_RUN_SCHEMA
                if self._binding.order_id == AJ_ORDER_ID
                else NATIVE_RUN_SCHEMA
            )
            record: dict[str, object] = {
                "record": record_tag,
                "scope": NATIVE_RUN_SCOPE,
                "binding": self._binding.to_record(),
                "owner_outcome": outcome,
                "attempt": journal_state,
                "subject_measured": subject is not None,
                "stop_recorded": stop_recorded,
                "native_record": native_record,
                "native_refusal": native_refusal,
                "verdict": {"ready": verdict.ready, "reasons": list(verdict.reasons)},
            }
            if identity_entry:
                record["identity"] = owner_identity
            if self._binding.order_id in (AF_ORDER_ID, AH_ORDER_ID, AJ_ORDER_ID):
                # The nested attach-binding record of the AF /
                # AH / AJ entry: the retained measured receipt (the
                # frozen owner context is its authority — a
                # copied or replayed record never mints
                # authority) or an honest None (the attach
                # phase never bound — the closed consumer
                # refuses a ready verdict without it)
                record["attach_binding"] = self._attach_receipt
            format_capture = None
            if self._binding.order_id == AJ_ORDER_ID:
                # The AJ entry's nested selected native
                # format-capture record (017-ai software):
                # built from THIS owner's OWN retained
                # selected export payload and re-validated
                # by the closed consumer (256 KiB TOTAL
                # SERIALIZED bound); an honest None when
                # the finish retained no selected capture.
                format_capture = _aj_format_capture_record(owner, self._binding, owner_identity)
                record["format_capture"] = format_capture
            parse_native_run_record(record)
            _write_native_run_record(Path(str(native_evidence_out)), record, owner.work)
        except FixtureError:
            # a PRE-RETENTION refusal: the primary closed
            # refusal propagates unchanged; the still-pending
            # attempt is closed truthfully
            self._close_attempt_on_publication_failure(outcome)
            raise
        except (TypeError, ValueError):
            # an unexpected serialization/validation error
            # closes the attempt and surfaces as the
            # module's own closed token, never raw
            self._close_attempt_on_publication_failure(outcome)
            raise FixtureError("internal") from None
        # ONLY THEN finalize the same-order journal (see the
        # docstring ordering); the real token is retained in
        # RAM/result, never rewritten into the evidence.
        # A POST-RETENTION unverified or raced result is a
        # closed failure that preserves the retained bytes
        # AND the actual journal facts as-is (never a normal
        # qualified success, never an overwrite or retry).
        #
        # The AJ QUALIFICATION journal gate (017-ai): for
        # the canonical AJ entry the same journal's terminal
        # outcome is the qualification verdict, composed
        # from the DISTINCT ordered facts — the owner's
        # ACTUAL cleanup outcome, the native handoff
        # readiness verdict, the strict full four-case
        # format qualification (the safe partial tag is
        # explicitly not-qualified) and the successful
        # required protected retention (implicit: reached
        # post-retention).  A cleanup-pass / native-ready
        # owner with an unqualified or absent format
        # closes the AJ qualification journal terminal
        # FAIL — never pass — while the owner's actual
        # outcome and the native verdict stay preserved
        # unchanged in the retained record; the one-shot
        # journal can never be later upgraded by a cached
        # outcome or by finalize_attempt.
        journal_outcome = outcome
        if outcome == "pass" and self._binding.order_id == AJ_ORDER_ID:
            qualified = (
                verdict.ready is True
                and format_capture is not None
                and format_capture["snapshot"].get("record") == fmodel.SCHEMA_FORMAT_SNAPSHOT
            )
            if not qualified:
                journal_outcome = "fail"
        token = oap_binding.record_order_attempt(
            self._repo, self._binding.order_id, self._run_id, journal_outcome
        )
        if outcome == "pass":
            if token != "finalized":
                raise FixtureError("native-owner-finalization-unverified")
        elif token not in ("finalized", "terminal-preserved"):
            raise FixtureError("native-owner-finalization-unverified")
        # The composition's cached outcome is the ACTUAL
        # qualification-finalization outcome (the journal
        # gate's result — for the AJ entry that is the
        # qualification verdict, not merely the cleanup
        # outcome): a later finalize_attempt followup
        # requests the SAME terminal status and can never
        # request a pass for a partially qualified run,
        # while the retained record's owner_outcome field
        # and the owner's physical terminal state preserve
        # the ACTUAL cleanup outcome unchanged.
        self._outcome = journal_outcome
        self._attempt_token = token
        self._published = True
        return record


__all__ = [
    "NATIVE_OWNER_REASONS",
    "NATIVE_RUN_ATTEMPT_TOKENS",
    "NATIVE_RUN_OUTCOMES",
    "NATIVE_RUN_SCHEMA",
    "NATIVE_RUN_SCOPE",
    "AD_NATIVE_RUN_SCHEMA",
    "AD_ORDER_ID",
    "AF_NATIVE_RUN_SCHEMA",
    "AF_ORDER_ID",
    "build_ad_native_channel",
    "NativeOwnerRun",
    "parse_native_run_record",
]

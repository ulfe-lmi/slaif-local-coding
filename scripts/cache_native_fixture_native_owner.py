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
- the HONEST publication ordering: owner convergence
  measures/retains the DISTINCT owner-phase outcome (a
  terminal fail/aborted finalizes the bound attempt
  honestly at convergence; a converged pass keeps it
  RUNNING), publish_native retains the protected
  native-run record FIRST (its attempt field carries the
  ALREADY-KNOWN journal state, never a predicted finalize
  token), and ONLY THEN the terminal pass finalizes the
  same-order journal — a failed native publication never
  leaves an admitted pass; the real finalize token is
  retained in RAM/result, never rewritten into the
  immutable evidence.

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
import cache_native_fixture_native_prep as prep  # noqa: E402

FixtureError = ci.FixtureError
OrderRunBinding = oap_binding.OrderRunBinding

NATIVE_RUN_SCHEMA = "slaif-native-owner-run-v1"
NATIVE_RUN_SCOPE = "native-owner-run"
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
        "native-owner-not-started",
        "native-owner-startup",
        "native-owner-settle",
        "native-owner-patience",
        "native-owner-not-terminal",
        "native-owner-evidence-exists",
        "native-owner-evidence-env",
        "native-owner-published",
        "native-owner-record-malformed",
        "internal",
    }
)

# the seam's disposable-work-root containment argument for a
# direct two-argument retention call (the probe form): a path
# that is never an ancestor; the composition ALWAYS passes the
# owner's real work root, which the seam enforces.
_NO_WORK_ROOT = Path(os.devnull)


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
    if not isinstance(record, dict) or set(record) != _NATIVE_RUN_KEYS:
        raise FixtureError("native-owner-record-malformed")
    outcome = record["owner_outcome"]
    attempt = record["attempt"]
    if (
        record["record"] != NATIVE_RUN_SCHEMA
        or record["scope"] != NATIVE_RUN_SCOPE
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
    ):
        raise FixtureError("native-owner-record-malformed")
    if refusal is not None and (native is not None or verdict["ready"] is True):
        raise FixtureError("native-owner-record-malformed")
    return record


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
    ) -> None:
        if not isinstance(binding, OrderRunBinding):
            raise FixtureError("native-owner-binding-invalid")
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
            )
            self._workflow = prep.NativeHandoffWorkflow(
                binding,
                table,
                worker_pid=worker_pid,
                bash_pid=bash_pid,
                owner_run_id=self._run_id,
                tty_foreground_pgrp=tty_foreground_pgrp,
                registered_owners=registered_owners,
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
            state = local._state_record(self._control_dir)
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
        state = local._state_record(self._control_dir)
        if state is None or state["run_id"] != self._run_id:
            raise FixtureError("native-owner-not-started")
        anchor = float(state["end_anchor"])
        remaining = anchor + local.CLEANUP_GRACE_SECONDS - time.monotonic()
        if remaining <= 0:
            raise FixtureError("native-owner-patience")
        response = local._control_client(
            self._control_dir, command, self._run_id, min(local._CLIENT_TIMEOUT, remaining)
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
        later native subject (the workflow's own gates:
        prepared, the separately measured stop recorded, the
        CURRENT stable stopped phase still holding, the
        frozen W/B baseline unchanged, the registered run
        immutable, the collectors invoked before any commit)."""
        return self._workflow.register_subject(  # type: ignore[union-attr]
            subject_pid, expectation, channel=channel
        )

    def record_stop(self) -> prep.StopReceipt:
        """Record the SEPARATELY MEASURED worker-stop event
        (read-only; the stop itself is performed later by
        the separately authorized operator) — a recorded
        event, never re-derived from a later snapshot."""
        return self._workflow.record_stop()  # type: ignore[union-attr]

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

    def publish_native(self, native_evidence_out: object) -> dict:
        """Publish the EXPLICIT native-scope terminal record
        for this run (closed schema
        ``slaif-native-owner-run-v1``, 0600 under the
        caller's protected evidence root, OUTSIDE the owner's
        disposable work root) with the HONEST publication
        ordering:

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
        3. the ``attempt`` field carries the ALREADY-KNOWN
           journal state, never a predicted finalize token:
           the pass path records the PENDING "running" state
           (the terminal pass finalization follows the
           successful protected publication below); a
           terminal owner outcome is already final in the
           journal (recorded as "terminal-preserved");
        4. the protected native record is retained FIRST; a
           failed native publication must never leave an
           admitted pass, so the still-pending bound attempt
           is closed as a fail and the refusal propagates;
        5. ONLY THEN the same-order journal is finalized: the
           terminal pass on success, the terminal fail/
           aborted as an honest idempotent no-op.  The REAL
           returned finalize token is retained in RAM/result
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
        out = Path(str(native_evidence_out))
        if out.exists() or out.is_symlink():
            raise FixtureError("native-owner-evidence-exists")
        if self._published:
            raise FixtureError("native-owner-published")
        owner = self._owner
        workflow = self._workflow
        if owner is None or workflow is None or self._thread is None:
            raise FixtureError("native-owner-not-started")
        outcome = self.owner_outcome()
        self._outcome = outcome
        subject = workflow.subject_receipt
        stop_recorded = workflow.stop_receipt is not None
        native_record: dict | None = None
        native_refusal: str | None = None
        if outcome == "pass" and subject is not None and stop_recorded:
            measurement = prep.OwnedOwnerMeasurement(owner, subject=subject)
            artifact = owner.artifact
            if (
                owner.target_cid is None
                or owner.image_id is None
                or not isinstance(artifact, dict)
                or not isinstance(artifact.get("binary_sha256"), str)
            ):
                # the declared context is derived from the
                # owner's OWN registration: an unmeasured
                # component is a closed honest refusal,
                # never a caller-chosen string
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
                    )
                except FixtureError as exc:
                    # the producer's closed token,
                    # propagated, never reworded
                    native_refusal = str(exc)
        verdict = workflow.finalize(native_record)
        # The ALREADY-KNOWN journal state, never a predicted
        # finalize token (see the docstring ordering).
        if outcome == "pass":
            journal_state = "running"
        else:
            journal_state = "terminal-preserved"
        record = {
            "record": NATIVE_RUN_SCHEMA,
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
        parse_native_run_record(record)
        try:
            _write_native_run_record(out, record, owner.work)
        except FixtureError:
            # A failed native publication must never leave an
            # admitted pass: close the still-pending bound
            # attempt as a fail (a terminal owner outcome is
            # already final — the call is an honest no-op
            # then); the refusal propagates unchanged.
            try:
                oap_binding.record_order_attempt(
                    self._repo, self._binding.order_id, self._run_id, "fail"
                )
            except FixtureError:
                pass
            raise
        # ONLY THEN finalize the same-order journal (see the
        # docstring ordering); the real token is retained in
        # RAM/result, never rewritten into the evidence.
        self._attempt_token = oap_binding.record_order_attempt(
            self._repo, self._binding.order_id, self._run_id, outcome
        )
        self._published = True
        return record


__all__ = [
    "NATIVE_OWNER_REASONS",
    "NATIVE_RUN_ATTEMPT_TOKENS",
    "NATIVE_RUN_OUTCOMES",
    "NATIVE_RUN_SCHEMA",
    "NATIVE_RUN_SCOPE",
    "NativeOwnerRun",
    "parse_native_run_record",
]

# Protected session recovery contract (objective 020)

`RECOVERY_RECORD_CONTRACT_VERSION = "cache-recovery-record/v1"`.
`RECOVERY_RECORD_POLICY_VERSION = "recovery-record-policy/v1"`.
`RECOVERY_RESUME_CONTRACT_VERSION = "cache-recovery-resume/v1"`.
`RECOVERY_RESUME_POLICY_VERSION = "recovery-resume-policy/v1"`.

This contract binds the INERT whole-020 protected session recovery
component (`src/slaif_local_coding/constitution/bundles/`:
`recovery_models`, `recovery_codec`, `recovery_store`,
`recovery_resume`) over the ACTUAL accepted 018-p
state/namespace and 018-t `RootRegionAdmissionResult` records and the
accepted 019 RAM owner/work plane (`docs/CACHE-RAM-STATE-CONTRACT.md`,
`docs/CACHE-RAM-WORK-CONTRACT.md`). The 020-a round implements the WHOLE
020 component stage at the INERT recovery-component layer (
`tests/test_bundle_recovery_codec.py`,
`tests/test_bundle_recovery_store.py`,
`tests/test_bundle_recovery_resume.py`) and is PENDING strategic review at
that bounded inert scope. The stage closes nothing end to end: no
wire/HTTP integration (022), no actual compiler/tokenizer (021), no v1
runtime activation; the component is never active in the adapter request
execution path and qualifies no v1 runtime criterion.

## 1. Versioned closed recovery record

`RecoveryRecord` is ONE versioned closed record for ONE trusted session,
built from the ACTUAL admitted owner (`RecoveryRecord.from_owner`): the
complete trusted namespace and configuration binding, the retained
018-p state, the ACTUAL 018-t result, the exact extracted original
bundles (Unicode/CRLF/empty and ordered multi-file content) with
provenance and fingerprints, known/unknown ownership,
occurrence/causal/replay evidence, graph/currentness and conflict state,
the prior epoch and the closed resume reason
(`RecoveryResumeReason`: `restart` — the explicit NEW-EPOCH
compile-once exception, never an ordinary hit and never a silent
unquarantine — and `quarantine_fence` — the durable persistence of a
FAILED DURABLE FENCE, which must not resume old usable governance), and
the payload digest of the canonical payload (the digest EXCLUDES the
digest field itself). It retains necessary metadata only: never full
conversations, API envelopes, environment-context tails, images,
transport credentials, credential-bearing wrappers or unrelated tool
output.

The codec is plain closed JSON (no executable / pickle
deserialization): `encode_recovery_record(record, max_bytes)` /
`decode_recovery_record(data, max_bytes)` validate the bounded complete
record BEFORE usable/restorable state is returned — the bound argument
is validated as a positive non-bool int not above
`RECOVERY_RECORD_HARD_MAX_BYTES` before any byte work, the ACTUAL
decoded string/source values are credential-scanned (JSON escaping can
hide the same detectable credential from a raw-text regex; the fixed
private refusal logs no content and makes no complete-secret-detection
claim), and the payload digest is verified against the canonical
payload. Credentials are rejected BEFORE encode/store too
(`recovery_record_credential_scan`), so a detectable forbidden
credential refuses with the fixed private typed error on both sides.
A decoded record is "restorable" only after the REAL accepted
validation/derivation: the reconstructed actual P/D/namespace is
validated and the ACTUAL T is derived (field-law-only validation of a
causal-history state is NOT complete D validation); legitimate
non-READY / conflict histories stay restorable as unusable EVIDENCE,
and a malformed / foreign / unsupported source or proof state is a
fixed refusal distinct from honest resource / currentness outcomes.
`RecoveryRecord.with_epoch_binding(prior_epoch)` carries the durable
epoch binding (section 5).

## 2. Trusted resume address

`RecoverySessionAddress` is the trusted lookup address: the six
authenticated stable fields (principal, session, repository, route,
model identity, configuration fingerprint). It addresses EXACTLY ONE
record even when the first resumed request contains NO root, source or
surviving virtual reference: the lookup is the opaque per-session
directory derived from the COMPLETE address (`session_directory_name`,
the SHA-256 of the canonical sorted-key JSON — `recovery_address_key`
is the same derivation for the initial-load reservation). It never
requires the disappeared workspace/root as a lookup prerequisite, never
scans other sessions, and the opaque filename is not authentication:
after loading, the COMPLETE trusted namespace / configuration /
schema / integrity of the record is validated and joined before any
RAM publication.

## 3. Protected per-session store

`RecoveryStore(root, *, max_bytes=...)` requires the OPERATOR-PREPARED
existing 0700 current-owner root (it never creates it or its
ancestors; a missing root is a fixed error). Session directories are
created descriptor-relative (0700 even under a permissive umask) and
fsynced into the parent root before durable success; files are 0600.
Every untrusted path entry is validated on the SAME opened descriptor
(0600 / current-owner / regular file, nonblocking safe open so a FIFO
cannot block), symlinks and path escapes are refused with closed
limitations, and pointer `file_name` is bound to the exact generated
basename for its generation.

Writer ownership is the OS-held exclusive descriptor lock
(`flock(LOCK_EX | LOCK_NB)`): no live/stale PID guessing, a competing
live writer is refused with the fixed `writer_conflict`, and the lock
is released by the kernel on process death. Publication is the
expected-generation CAS: the checkpoint file is written O_EXCL 0600
and fsynced, the pointer is published atomically (temp + fsync +
rename + directory fsync, every step descriptor-relative to the owned
session directory), and generation serializes PUBLICATION, never
source freshness. Faults preserve the previous committed generation
or report the ACTUAL committed outcome explicitly (the post-rename
fault reports the actual observed generation — the rename may be
committed while directory durability is unconfirmed — and a caller
must assume neither the old nor the new state); `current_generation()`
distinguishes MISSING (0) from corrupt/invalid current (typed
refusal), so no load failure maps silently to 0. A crashed prior
attempt of the SAME generation may leave orphan checkpoint bytes; they
are reused only when they ARE exactly the new bytes, and only after
fsyncing them (idempotent re-publication) — anything else is a torn
checkpoint refused with the closed limitation, never mixed with new
metadata. The post-publication read-back fence (same-descriptor
validation, codec law, address join) stays the descriptor-level check;
the byte/record association is additionally re-proven BEFORE any
write (the supplied bytes must equal the canonical re-encoding under
the store bound, else `checkpoint_torn`). The pointer is bounded to
`POINTER_MAX_BYTES`; the store byte ceiling is the closed
`max_bytes` (positive non-bool int not above the hard record
ceiling). The closed `RecoveryStoreLimitation` vocabulary is the fixed
private refusal surface (no partially published RAM state on any
fault).

## 4. Bounded shared-RAM recovery reservations

Record size, read/write work and transient buffers are bounded BEFORE
retention / allocation against the SAME 019 process AND per-session
ceilings wherever owned RAM is retained / reserved (initial codec
record-byte ceiling `RECOVERY_RECORD_INITIAL_MAX_BYTES = 67108864`
(64 MiB), hard `RECOVERY_RECORD_HARD_MAX_BYTES = 268435456` (256
MiB); the bounded JSON worst case for the canonical encoding is 6x the
payload on ASCII control-character expansion, which the publication
reservation covers):

- COLD initial load (no live owner yet): the reservation
  `max(4 × committed_record_bytes, RECOVERY_TRANSIENT_FLOOR_BYTES
  (16384))` is taken against the trusted resume address
  (`reserve_recovery_transient_cold`, the address lineage key) BEFORE
  `session.load` / decode / full D validation / rebind, held through
  the load and released exactly once on EVERY outcome (the rebind
  transfers it to the validated namespace); a duplicate cold
  reservation while a live owner exists refuses before publication.
- LIVE bounded publication (checkpoint / fence / epoch binding): the
  reservation `max(24 × (owner.owned_bytes + 16384), 16384)` is taken
  on the event loop BEFORE the worker thread is dispatched
  (`reserve_recovery_transient`, the registered namespace joined by
  identity — a value-equal foreign copy is the fixed
  `RamStateInputError` — with the same-lock work-teardown fence
  refusal (section 7) BEFORE the capacity checks), held through all
  owned IO / read-back, and released exactly once.
- The session-reserved transient term is part of the SAME atomic 019
  sums: the synchronous `admit` session-ceiling check and the process
  ceiling see it, so simultaneous store / work allocations observe
  the session reservation; no separate process-only charge exists.
- Refusal under a ceiling is the fixed typed 503 contract preserving
  the retained state exactly; actual available RAM can refuse earlier;
  the accepted 018 source/history/work limits stay independently
  binding; no active-session TTL/LRU/entry eviction and no hidden
  disk hot lookup exist.

## 5. Durable epoch binding

Resume reconstructs a registered RAM owner in a DISTINCT live epoch
with the recorded recovery reason: `acquire_new_with_epoch_floor`
allocates exactly once under the registry lock with the epoch strictly
above the DURABLE prior (a duplicate live owner is refused
`owner_already_live`; the normal acquire / new_owner behavior is
preserved when no floor applies). The durable binding is
`record.with_epoch_binding(owner.epoch)` and is re-published on EVERY
resume at which it differs — so each resume commits generation + 1
and the prior epoch advances durably; within an epoch, usage NEVER
rewrites the checkpoint (work hits / preparation leave the committed
generation unchanged; the fresh post-teardown open still reports the
resume-time generation). A binding encode / publish failure exposes
nothing: the rebound transient is released BEFORE the owner teardown
(the direct-teardown guard would otherwise refuse
`recovery_in_flight` and leak a usable registered owner), the ACTUAL
observed generation is captured BEFORE the session closes and
reported, and the committed generation is unchanged (no partial
binding). A fresh same-registry resume then succeeds (a leaked owner
would be `owner_already_live`, a leaked writer `writer_conflict`).

## 6. Quarantine and fence durability

A VALIDATED capacity-refused candidate classified adverse (non-READY,
or READY withdrawing / rekeying retained current keys — the same
019 predicate; the check does not independently prove source
novelty) is fenced BEFORE the state transition that could make old
recovery unsafe is permitted: the fence record
(`from_owner(..., quarantine_fence=True)`) is published durably first.
An ACTUALLY capacity-quarantined owner can therefore never resume old
usable governance from its older stored bytes: the persisted fence
record refuses the unsafe continuation, and no automatic unquarantine,
retry or epoch reset clears it. Scope: when preflight is pure and no
admit / state mutation / quarantine occurred, a FAILED pre-transition
fence write leaves the prior committed generation valid (the
transformation is simply rejected — no permanent dirty / live-lease
poisoning of the last valid checkpoint); strictness holds for the
actually-quarantined owner and for the post-rename fault law
(section 3: the ACTUAL committed outcome, never a manufactured
rollback or clean-recovery verdict).

## 7. Owned bounded store IO

`checkpoint_current` / `checkpoint_current_async` / `admit_with_fence`
run over ONE process-wide owned store IO slot
(`owned_store_io_acquire` / `owned_store_io_release`, closed
constant 1): a second concurrent owned publication is refused typed
`write_in_flight` BEFORE any new thread starts (the store in-flight
law is the second fence). The async path runs the synchronous
publication in ONE owned worker thread (`asyncio.to_thread`) with the
bounded transient reserved on the loop BEFORE dispatch (section 4).
Cancellation / timeout / teardown cannot release ownership while an
owned write can still publish: a cancelled / timed-out CALLER drains
the owned write to its ACTUAL typed result (holding repeated
cancellations) BEFORE the cancellation or timeout propagates and
BEFORE the slot / reservation are released — no late old-epoch
publication, no orphan thread after a timeout. Teardown holds an
early admission fence honored by every sync / async checkpoint and
fenced-admit path across drain / close (covering already-running and
scheduled-not-yet-started IO), and direct store / work teardown is
refused with the fixed `recovery_in_flight` while recovery IO is
live at entry. The work-teardown reverse race is closed under the
SAME registry lock: `reserve_recovery_transient` checks the work
owner's EXISTING fenced / draining flag (`owner_teardown_fenced`,
AFTER the namespace identity join, BEFORE the capacity checks) and
refuses with `RamStateWorkTeardownFenceError`, so a draining work
teardown can never reach its later store release under live recovery
IO, and work teardown refuses `recovery_in_flight` while a recovery
reservation is held. The component contract documents an off-loop
integration for the synchronous primitives (the existing bounded
ownership / cancellation behavior applies; actual ASGI wiring is
022); a documented residual preemption micro-window (a publication
thread stalled between the entry check and the reserve while no live
work holds the drain) is preserved as a process qualification, not
tested.

## 8. Lazy rebuild and no hot reads

Needed current keys rebuild LAZILY through the ACTUAL 019 work plane
and bounded injected seam, once per key / new epoch under its
attempt policy (the honest first rebuild versus the RAM hit: one
invocation, then HIT with zero); there is no eager dormant-session
scan / recompile and no readiness while required preparation remains
unresolved. After successful resume / preparation, normal
hits / current selection / lifecycle use RAM only: recovery-content
reads are mechanically denied (a closed 24-facility filesystem trap
stays clean under resume, and the resume-section scan denial refuses
every `listdir` / `scandir`, including fd arguments — the trusted
address lookup needs no scan), repeated hits reuse payloads with zero
new seam invocations, and source originals are never sent to a main
model as a fallback. State retention / deletion is operator-owned and
explicit (no automatic timed deletion or silent capacity cleanup);
deployment encryption is a stated prerequisite, not a guarantee.

## 9. Teardown and writer retention

The recovery owner retains the EXCLUSIVE store writer for its live
lifetime (releasing it early would let another registry / process
resume the same session); `RecoverySessionOwner.teardown` performs the
ACTUAL 019-b async work teardown (fence, cancel, await) and the store
release in ONE composed path, draining the owned IO slot before the
writer is closed, and reports the composed outcome
(`RecoveryTeardownResult`: store / work / session-closed facts). A
cancelled teardown holds its cleanup until release (the 019-b drain
law) and propagates cancellation only after the owned cleanup
finishes — the session close is never skipped, so the writer lock
cannot leak.

## 10. Inert boundary and evidence

The component is inert: no wire / HTTP integration (022), no actual
compiler / tokenizer (021), no v1 runtime activation, no
configuration key, no adapter wiring, no live model / service /
Codex / client process (plain-Python subprocess restart tests are the
only process evidence and run the repository interpreter only). The
earned component-scope evidence (284-case battery at 020-a, native
pytest exit 0): exact original-byte / ordered-member / unknown-hash
round trips with real P/T derivation; real temporary-filesystem
ownership / mode / symlink / path-escape / foreign / oversized /
malformed / digest / schema / configuration-mismatch and credential
quarantine refusals with fixed private errors; fault / crash points
before / after write, fsync and atomic publication INCLUDING an
actual SIGKILL of a real publishing process at the post-rename
directory-fsync boundary (actual committed outcome verified, store
fully usable after kernel lock release); torn / missing / corrupt
checkpoint, stale / competing writers (in-process, cross-process
kernel release) and orphan exact-reuse; multiple dormant persisted
sessions with explicit resume of exactly ONE from its trusted address
alone in FRESH Python processes (distinct epoch strictly above the
durably bound prior, generation + 1 per resume, needed key prepared
once per epoch, RAM hit with zero invocations, zero recovery-content
reads and no scan of the store tree, committed generation unchanged
within an epoch); failed / cancelled writes, caller cancellation /
deadline with held IO draining to the actual outcome before
release, resume / owner / teardown / work-teardown races with
deterministic barriers and bounded aggregate pressure under FIXED
ceilings; and the denied-filesystem lifecycle proof. The v1 RUNTIME
and real-client halves of M01–M05 remain NOT RUN; a report is a claim
until strategic acceptance.

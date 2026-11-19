"""Resume coordination for the protected per-session recovery
store (objective 020, component scope).

This is the EXPLICIT authenticated single-session resume
boundary (CACHE-REWORK.md section 12.3; SECURITY.md narrow
exception): given the trusted resume ADDRESS (the
authenticated stable principal / session / repository /
route plus the configured model / policy context -- NO
root, source or surviving virtual reference is required to
locate the session) and the accepted 019 RAM registry, it

- opens the ONE protected session under the OS-held
  exclusive writer lock (a live writer -- foreign OR the
  recovery owner of this very process -- is a typed
  ``writer_conflict`` refusal, never a second owner, and
  the non-blocking lock acquisition is bounded, never an
  unbounded wait);
- loads the committed generation (every closed store
  limitation -- torn / corrupt / missing / oversized /
  foreign / credential / namespace -- is typed, never a
  raw error and never a partially published RAM state);
- preserves the DURABLE quarantine fence: a record
  carrying the bounded pre-accounted
  adverse-currentness quarantine (019-c) resumes NOTHING
  (no owner, no admit, no epoch reset, no silent
  unquarantine); only the explicit teardown of a live
  quarantined owner is the fence exit;
- restores the record through the ACTUAL codec law (the
  D cross-record integrity, the P reconstruction, the
  ACTUAL P lineage law and the ACTUAL accepted T
  derivation -- object construction is not authentication)
  before ANY RAM publication; and
- reconstructs the registered RAM owner in a DISTINCT
  live epoch STRICTLY ABOVE the record's ``prior_epoch``
  through the registry's strict recovery allocation
  (``acquire_new_with_epoch_floor``: ONE allocation under
  the registry critical section, no burn / re-acquire, a
  fresh process never reuses a recorded prior epoch),
  then admits the restored P/T record set under the
  mandatory ``expected_revision=0`` commit CAS, carrying
  the typed T outcome (a genuine non-READY T is
  admissible; a capacity refusal keeps the fresh owner
  and its actual quarantine state, typed), and BEFORE a
  successful owner is exposed the DURABLE epoch binding
  is published under the bound-generation CAS (the
  record's ``prior_epoch`` re-bound to the live epoch
  with every other field verbatim) so a crash after a
  successful resume never reuses that epoch in a later
  restart; a failed binding blocks the exposure (owner
  torn down, session closed, the ACTUAL observed
  post-attempt generation carried -- the rename may be
  committed while directory durability is unconfirmed, so
  neither the old nor the new state is assumed and no
  rollback is claimed).

The live resume returns a ``RecoverySessionOwner`` that
RETAINS the exclusive writer session for the WHOLE live
lifetime of the RAM owner: the lock is released only by
the explicit teardown, and only AFTER the store owner is
fenced / released (the work plane drained through the
ACTUAL 019-b async teardown when enabled).  No second
process can open / resume the same session while the
recovered owner is live, and a late old-epoch write
cannot publish after teardown (the handle is closed, the
store owner is fenced, and the next resume allocates a
strictly higher epoch).

The owner's P/T transitions run through
``admit_with_fence`` (requirement 5): a candidate the
019-c classifier marks ADVERSE against the retained
current rows (a non-READY result, or a READY result
withdrawing / rekeying a retained current key) makes the
older durable bytes unsafe if they survive a crash, so
the DURABLE fail-closed fence (the current retained
record set recorded quarantined) is published under the
bound-generation CAS BEFORE the transition is permitted --
only AFTER the accepted pre-charge fence law prefights
the candidate (a forged / copied / mismatched / stale
candidate refuses with the exact admit refusal and the
durable record untouched); a fence that cannot be
durably published BLOCKS the
unsafe continuation (no admit, typed
``fence_refused``): a fault BEFORE the pointer
publication leaves the prior committed generation
valid (no admit, no state mutation and no
quarantine occurred, so the retained current rows
stay usable and the bound generation unchanged),
while a fault AFTER the pointer rename may have
already committed the fence generation (the ACTUAL
observed generation is carried; the live owner
cannot overwrite it -- a later checkpoint is the
fixed generation-mismatch refusal, never a silent
unfence -- and the explicit teardown is the exit,
after which a restart fails closed on the committed
fence).  An admitted candidate advances the
durable binding to the new record set; a capacity
refusal that quarantines the owner RETAINS the fence
(durable and in-memory agree); any other refusal attempts
the unfence.  ``checkpoint_current`` is the durable
post-admission hook on the live session (no reopen); a
failed publication keeps the RAM state and reports the
actual committed outcome -- the checkpoint failure
prevents the transformation that newly relies on it (the
actual no-forward body proof is 022).

Rebuilding the needed current keys is LAZY through the
actual 019-b work plane (``registry.work.resolve``) --
once per key per new epoch under its ratified attempt
policy; this module performs NO eager dormant-session
scan, reads recovery content for nothing but the resumed
session, and sends no original to a main model as a
hidden fallback.  The bounded transient law
(record-byte ceiling before copy / parse, bounded
descriptor-relative reads, the SAME 019 process and
session ceilings for retained / reserved RAM) runs at
the named seams: the codec's byte ceiling, the
store's bounded descriptor-relative reads, and the
registry's recovery transient reservation -- the
COLD initial-load reservation under the trusted
resume address key BEFORE the first load / decode
(bound to the validated namespace's lineage key once
the record loads) plus the per-publication reserve
for every fence / advance / checkpoint and binding
write -- checked BEFORE the owning allocation /
retention begins.  Actual IO latency (kernel fsync)
is documented as unbounded by design.
The stage is INERT: no adapter wiring, no configuration
key, no v1 runtime activation.  All 018 / 019 public
signatures, schemas, defaults, version tags and refusal
laws stay intact.
"""

from __future__ import annotations

import asyncio
from collections.abc import Callable
from dataclasses import dataclass
from enum import StrEnum

from .ram_state import (
    RamStateCapacityError,
    RamStateDuplicateOwnerError,
    RamStateInputError,
    RamStateOwner,
    RamStateOwnerRegistry,
    RamStateWorkTeardownFenceError,
)
from .ram_state_models import (
    RamStateAdmissionResult,
    RamStateLimitation,
    RamStateOutcome,
    RamStateTeardownResult,
)
from .ram_work_models import (
    RamWorkLimitation,
    RamWorkOutcome,
    RamWorkTeardownResult,
)
from .recovery_codec import (
    RecoveryCodecIntegrityError,
    RecoveryCodecMalformedError,
    RecoveryCodecSizeError,
    RecoveryCredentialQuarantineError,
    encode_recovery_record,
    recovery_restore_record,
)
from .recovery_models import RecoveryError, RecoveryRecord, RecoverySessionAddress
from .recovery_store import (
    RecoveryPublishResult,
    RecoverySession,
    RecoveryStore,
    RecoveryStoreError,
    RecoveryStoreLimitation,
)
from .root_region_admission_result_models import RootRegionAdmissionResult
from .root_region_lineage_models import RootRegionLineageState

RECOVERY_RESUME_CONTRACT_VERSION = "cache-recovery-resume/v1"
RECOVERY_RESUME_POLICY_VERSION = "recovery-resume-policy/v1"
# The closed schema floor of the bounded recovery
# transient reservation (requirement 4): the minimum
# reserved restore / serialize transient for ANY
# bounded recovery write or resume, covering the
# schema / small-record overhead below the
# committed-size proportion.
RECOVERY_TRANSIENT_FLOOR_BYTES = 16384


class RecoveryResumeOutcome(StrEnum):
    """The closed resume-outcome vocabulary (fixed, typed,
    no content / path / identity echo)."""

    RESUMED = "resumed"
    QUARANTINE_PERSISTED = "quarantine_persisted"
    OWNER_ALREADY_LIVE = "owner_already_live"
    STORE_REFUSED = "store_refused"
    RECORD_NOT_RESTORABLE = "record_not_restorable"
    ADMIT_REFUSED = "admit_refused"
    ALLOCATION_REFUSED = "allocation_refused"


class RecoveryResumeLimitation(StrEnum):
    """The closed resume-boundary limitations that are not
    one of the carrying closed vocabularies (the store
    limitation on a store refusal and the 019-a owner
    limitation on an admit refusal are carried BY VALUE
    from their owning vocabulary)."""

    CODEC_INTEGRITY = "codec_integrity"
    CODEC_MALFORMED = "codec_malformed"


class RecoveryAdmitOutcome(StrEnum):
    """The closed fenced-admit outcome vocabulary (020):
    the accepted 019 admission result, or the blocked
    unsafe continuation (the durable fence could not be
    published, so NO transition was permitted)."""

    ADMITTED = "admitted"
    REFUSED = "refused"
    FENCE_REFUSED = "fence_refused"


class RecoveryTeardownOutcome(StrEnum):
    """The closed recovery-teardown outcome vocabulary."""

    TEARDOWN = "teardown"
    REFUSED = "refused"


@dataclass(frozen=True, slots=True)
class RecoveryResumeResult:
    """The typed result of ONE explicit resume attempt.

    ``limitation`` carries the closed limitation of the
    refusing boundary (the 020 store vocabulary, the
    closed resume codec vocabulary or the 019-a owner
    vocabulary) and is None on RESUMED / the fence /
    already-live outcomes.  ``recovery`` is the LIVE
    recovery owner (RESUMED, or the kept fresh owner on
    ADMIT_REFUSED): it retains the exclusive writer
    session for the owner's live lifetime, and every other
    outcome creates no owner and releases the session.
    ``t_result`` is the ACTUAL accepted T derivation of
    the restored record (present whenever the record was
    restorable)."""

    outcome: RecoveryResumeOutcome
    limitation: RecoveryStoreLimitation | RecoveryResumeLimitation | RamStateLimitation | None = (
        None
    )
    generation: int | None = None
    prior_epoch: int | None = None
    new_epoch: int | None = None
    owner: RamStateOwner | None = None
    t_result: RootRegionAdmissionResult | None = None
    owner_quarantined: bool = False
    recovery: RecoverySessionOwner | None = None


@dataclass(frozen=True, slots=True)
class RecoveryFencedAdmitResult:
    """The typed result of ONE fenced P/T transition of a
    live recovered owner.  ``fence`` is the pre-transition
    durable fail-closed publication (adverse candidates
    only); ``advance`` is the post-admission durable
    publication (an admitted candidate, or the unfence
    attempt after a non-quarantining refusal); a
    quarantining capacity refusal retains the fence with
    no advance.  ``bound_generation`` is the durable
    generation describing the owner's current retained
    record set after the operation."""

    outcome: RecoveryAdmitOutcome
    admitted: RamStateAdmissionResult | None = None
    fence: RecoveryPublishResult | None = None
    advance: RecoveryPublishResult | None = None
    owner_quarantined: bool = False
    bound_generation: int | None = None


@dataclass(frozen=True, slots=True)
class RecoveryTeardownResult:
    """The typed result of ONE explicit recovery teardown.

    ``TEARDOWN`` means the store owner is fenced /
    released (through the ACTUAL 019-b async work
    teardown when the registry enables the work plane,
    which releases store and work in ONE critical
    section; through the synchronous store teardown when
    work-disabled) AND the writer session is closed (the
    lock released only after the store owner is gone --
    no late old-epoch writer, no same-epoch reset
    window).  ``REFUSED`` carries the exact fence domain
    with the session still held (the recovery owner stays
    the writer; no partial release)."""

    outcome: RecoveryTeardownOutcome
    limitation: RamWorkLimitation | RamStateLimitation | None = None
    store: RamStateTeardownResult | None = None
    work: RamWorkTeardownResult | None = None
    session_closed: bool = False


class RecoverySessionOwner:
    """ONE live recovered session (020).

    Holds the exclusive writer session (the OS-held lock)
    for the WHOLE live lifetime of the RAM owner: resume
    returns it open, and only the explicit ``teardown``
    releases it -- after the store owner is fenced /
    released -- so no second process can open / resume the
    same session while the recovered owner is live (a live
    writer is a typed ``writer_conflict`` refusal), and a
    late old-epoch write cannot publish after teardown
    (the handle is closed and the next resume allocates a
    strictly higher epoch).  ``bound_generation`` is the
    generation whose durable record describes the owner's
    CURRENT retained record set; every durable
    publication (fence, advance, checkpoint) moves it
    under the expected-generation CAS."""

    _owned_publish: asyncio.Task[RecoveryPublishResult] | None
    _tearing_down: bool

    __slots__ = (
        "_registry",
        "_session",
        "_owner",
        "_address",
        "_bound",
        "_prior_epoch",
        "_new_epoch",
        "_closed",
        "_owned_publish",
        "_tearing_down",
    )

    def __init__(
        self,
        *,
        registry: RamStateOwnerRegistry,
        session: RecoverySession,
        owner: RamStateOwner,
        address: RecoverySessionAddress,
        bound_generation: int,
        prior_epoch: int,
        new_epoch: int,
    ) -> None:
        self._registry = registry
        self._session = session
        self._owner = owner
        self._address = address
        self._bound = bound_generation
        self._prior_epoch = prior_epoch
        self._new_epoch = new_epoch
        self._closed = False
        self._owned_publish = None
        self._tearing_down = False

    @property
    def owner(self) -> RamStateOwner:
        return self._owner

    @property
    def address(self) -> RecoverySessionAddress:
        return self._address

    @property
    def bound_generation(self) -> int:
        return self._bound

    @property
    def prior_epoch(self) -> int:
        return self._prior_epoch

    @property
    def new_epoch(self) -> int:
        return self._new_epoch

    @property
    def closed(self) -> bool:
        return self._closed

    @property
    def tearing_down(self) -> bool:
        """Whether teardown is in progress (the
        admission fence new checkpoint / fenced-
        admit calls honor while it is set)."""
        return self._tearing_down

    @property
    def session(self) -> RecoverySession:
        return self._session

    def _check_open(self) -> None:
        if self._closed:
            raise RecoveryError(
                "the recovery session owner is closed (teardown released the writer)"
            )

    def checkpoint_current(self) -> RecoveryPublishResult:
        """The durable post-admission hook (requirements
        3 / 6): publish the owner's CURRENT retained
        record set under the bound-generation CAS on the
        LIVE session (no reopen, no lock release).  An
        empty owner raises the fixed record error (nothing
        durable to checkpoint); a refused / faulted
        publication keeps the RAM owner and the bound
        generation untouched and reports the ACTUAL
        committed outcome.  A checkpoint failure prevents
        the transformation that newly relies on it (the
        actual no-forward body proof is 022)."""
        self._check_open()
        if self._tearing_down:
            # The teardown admission fence: no new
            # publication may start while teardown is
            # draining / closing (a late old-epoch
            # writer must not publish after the RAM
            # ownership is released).
            return RecoveryPublishResult(
                RecoveryStoreLimitation.WRITER_CONFLICT,
                None,
                None,
                self._session.observed_generation,
            )
        if not self._registry.owned_store_io_acquire():
            # The ONE process owned store IO slot is
            # held by another owned publication (the
            # typed busy refusal; no queue).
            return RecoveryPublishResult(
                RecoveryStoreLimitation.WRITE_IN_FLIGHT,
                None,
                None,
                self._session.observed_generation,
            )
        try:
            if not self._registry.recovery_op_begin(self._owner):
                # The closed 020-b preemption gap: the
                # exact live-owner join refused (the
                # owner is absent / fenced / replaced,
                # or its 019 work plane is already
                # draining and owns the release) -- a
                # clean typed refusal with NO cold
                # reservation and NO publication (the
                # established WRITER_CONFLICT result).
                return RecoveryPublishResult(
                    RecoveryStoreLimitation.WRITER_CONFLICT,
                    None,
                    None,
                    self._session.observed_generation,
                )
            try:
                return self.checkpoint_current_locked()
            finally:
                self._registry.recovery_op_end(self._owner)
        finally:
            self._registry.owned_store_io_release()

    def checkpoint_current_locked(self) -> RecoveryPublishResult:
        """The checkpoint body with the ONE process
        owned store IO slot already held by the
        caller (the fenced-admit path holds it
        across the whole operation)."""
        self._check_open()
        if self._tearing_down:
            return RecoveryPublishResult(
                RecoveryStoreLimitation.WRITER_CONFLICT,
                None,
                None,
                self._session.observed_generation,
            )
        # The record factory runs INSIDE the bounded
        # reservation (no construction before it).
        return self._publish_bounded(lambda: RecoveryRecord.from_owner(self._owner), self._bound)

    def _publish_bounded(
        self,
        record_factory: Callable[[], RecoveryRecord],
        expected_generation: int,
    ) -> RecoveryPublishResult:
        """The bounded durable publication (requirement
        4).  The CONSERVATIVE bounded transient
        reservation is taken BEFORE the record
        construction runs at all: ``record_factory``
        executes ONLY inside the reservation, so no
        model construction / model_dump /
        serialization allocation precedes it.  The
        bound is derived from the CURRENT bounded
        inputs, not the old disk size: the new
        record's encoding M is at most 6x the
        owner's charged retained occupancy
        (``owned_bytes``) -- every serialized
        source / metadata content byte is part of
        the charged retained occupancy (originals
        AND metadata, retained history included),
        and the closed UTF-8 -> JSON worst case is
        6 bytes per content byte (an ASCII control
        character encodes as the 6-byte backslash-u
        unicode escape; every other character
        encodes to at most 6 bytes per UTF-8 byte)
        -- plus the
        closed fixed-field envelope, which the
        closed schema floor subsumes -- and the
        operation PEAK is at most 4x M (the
        retained encoding output coexisting with
        the pre-write re-encode, the read-back raw
        bytes and the decoded record
        re-derivation).  So the reservation is
        ``max(24 x (owned_bytes + the closed
        schema floor), the closed schema floor)``,
        checked against the SAME 019 process and
        session ceilings
        (a crossing refuses with the fixed
        ``resource_exhausted`` limitation: no write,
        bound generation untouched), held through
        the construction, the encode, the write and
        the read-back (the store's in-flight law
        marks the whole publication), and released
        exactly once (on every outcome).  It is a
        closed conservative bound, not an
        exact-byte measurement; an earlier refusal
        is typed backpressure, never a state
        change.  A refused / faulted publication
        keeps the RAM owner and reports the ACTUAL
        committed outcome; the checkpoint failure
        prevents the transformation that newly
        relies on it (the actual no-forward body
        proof is 022)."""
        namespace = self._owner.namespace
        reserve = max(
            24 * (self._owner.owned_bytes + RECOVERY_TRANSIENT_FLOOR_BYTES),
            RECOVERY_TRANSIENT_FLOOR_BYTES,
        )
        try:
            self._registry.reserve_recovery_transient(namespace, reserve)
        except RamStateWorkTeardownFenceError:
            # The 020 work-teardown fence: no NEW recovery
            # publication may start while the owner's work
            # teardown is fenced / draining (the typed
            # writer conflict, the same result as the
            # owner's own teardown fence; no write, no
            # bound change).
            return RecoveryPublishResult(
                RecoveryStoreLimitation.WRITER_CONFLICT,
                None,
                None,
                self._session.observed_generation,
            )
        except RamStateCapacityError:
            return RecoveryPublishResult(
                RecoveryStoreLimitation.RESOURCE_EXHAUSTED,
                None,
                None,
                self._session.observed_generation,
            )
        return self._publish_bounded_held(reserve, record_factory, expected_generation)

    def _publish_bounded_held(
        self,
        reserve: int,
        record_factory: Callable[[], RecoveryRecord],
        expected_generation: int,
    ) -> RecoveryPublishResult:
        """The bounded publication body with the
        transient reservation ALREADY held by the
        caller (the async path reserves on the
        event loop BEFORE the worker thread is
        dispatched): the construction, the encode,
        the write and the read-back run under that
        held reservation, which is released exactly
        once here (on every outcome)."""
        namespace = self._owner.namespace
        try:
            try:
                record = record_factory()
                encoded = encode_recovery_record(record, max_bytes=self._session.max_bytes)
            except RecoveryCodecSizeError:
                return RecoveryPublishResult(
                    RecoveryStoreLimitation.OVERSIZED,
                    None,
                    None,
                    self._session.observed_generation,
                )
            except RecoveryCredentialQuarantineError:
                return RecoveryPublishResult(
                    RecoveryStoreLimitation.CREDENTIAL_QUARANTINE,
                    None,
                    None,
                    self._session.observed_generation,
                )
            result = self._session.publish_encoded(encoded, record, expected_generation)
        finally:
            self._registry.release_recovery_transient(namespace, reserve)
        if result.limitation is RecoveryStoreLimitation.OK and result.generation is not None:
            self._bound = result.generation
        return result

    async def checkpoint_current_async(self) -> RecoveryPublishResult:
        """The owned ASYNC bounded publication (requirement
        4): the synchronous ``checkpoint_current`` runs in
        ONE owned worker thread (``asyncio.to_thread``) as
        the owner's SINGLE owned store IO at a time -- a
        second concurrent owned publication is refused
        typed ``write_in_flight`` BEFORE any new thread
        starts (the store's in-flight law is the second
        fence).  If this awaiter is cancelled while the
        owned write is still live, the owned write DRAINS
        to its actual typed result -- holding every
        repeated cancellation -- BEFORE the cancellation
        propagates (the 019-b drain law): the bounded
        reservation, the store IO and the bound-generation
        update finish exactly once, so a late old-epoch
        writer can never publish through a live owner
        while teardown is draining, and the explicit
        teardown drains the SAME owned slot before the
        writer is released.  A refused / faulted
        publication keeps the RAM owner and reports the
        ACTUAL committed outcome exactly as the
        synchronous checkpoint."""
        self._check_open()
        if self._tearing_down:
            return RecoveryPublishResult(
                RecoveryStoreLimitation.WRITER_CONFLICT,
                None,
                None,
                self._session.observed_generation,
            )
        owned = self._owned_publish
        if owned is not None and not owned.done():
            return RecoveryPublishResult(
                RecoveryStoreLimitation.WRITE_IN_FLIGHT,
                None,
                None,
                self._session.observed_generation,
            )
        if not self._registry.owned_store_io_acquire():
            # The ONE process owned store IO slot is
            # held by another owned publication (the
            # typed busy refusal BEFORE any new
            # thread starts; no queue).
            return RecoveryPublishResult(
                RecoveryStoreLimitation.WRITE_IN_FLIGHT,
                None,
                None,
                self._session.observed_generation,
            )
        # The bounded transient reservation is taken
        # on the event loop BEFORE the worker thread
        # is dispatched (requirement 4: reservation
        # before task / thread dispatch), held
        # through the owned IO and released exactly
        # once by the publication body:
        reserve = max(
            24 * (self._owner.owned_bytes + RECOVERY_TRANSIENT_FLOOR_BYTES),
            RECOVERY_TRANSIENT_FLOOR_BYTES,
        )
        try:
            self._registry.reserve_recovery_transient(self._owner.namespace, reserve)
        except RamStateWorkTeardownFenceError:
            # The 020 work-teardown fence (the typed
            # writer conflict; the slot is released, no
            # worker thread is dispatched).
            self._registry.owned_store_io_release()
            return RecoveryPublishResult(
                RecoveryStoreLimitation.WRITER_CONFLICT,
                None,
                None,
                self._session.observed_generation,
            )
        except RamStateCapacityError:
            self._registry.owned_store_io_release()
            return RecoveryPublishResult(
                RecoveryStoreLimitation.RESOURCE_EXHAUSTED,
                None,
                None,
                self._session.observed_generation,
            )
        try:
            task = asyncio.create_task(
                asyncio.to_thread(
                    self._publish_bounded_held,
                    reserve,
                    lambda: RecoveryRecord.from_owner(self._owner),
                    self._bound,
                )
            )
        except BaseException:
            self._registry.release_recovery_transient(self._owner.namespace, reserve)
            self._registry.owned_store_io_release()
            raise
        self._owned_publish = task
        try:
            return await asyncio.shield(task)
        except asyncio.CancelledError:
            # The owned write is drained to its ACTUAL
            # typed result (holding repeated
            # cancellations) before the cancellation
            # propagates:
            await self._drain_owned_publish(task)
            raise
        finally:
            if self._owned_publish is task:
                self._owned_publish = None
            self._registry.owned_store_io_release()

    async def _drain_owned_publish(self, task: asyncio.Task[RecoveryPublishResult]) -> None:
        """Drain ONE owned publication task to ACTUAL
        completion while holding repeated cancellations
        (the 019-b drain law at this boundary): the
        fence / reservation / store IO finish before the
        cancellation propagates, and a HELD cancellation
        propagates only AFTER the owned write's actual
        outcome has been surfaced (a faulted owned write
        raises its actual exception instead).  A quiet
        completion without any held cancellation returns
        normally (the caller proceeds)."""
        cancelled = False
        while True:
            try:
                await asyncio.shield(task)
            except asyncio.CancelledError:
                cancelled = True
                if not task.done():
                    # The owned write is still live: this
                    # cancellation is HELD and the drain
                    # continues:
                    continue
                # The owned write finished (concurrently
                # with the held cancellation): surface its
                # actual outcome, then let the held
                # cancellation propagate AFTER the drain:
                task.result()
                raise
            if cancelled:
                # The owned write completed quietly while
                # a cancellation was held: the drain is
                # done and the held cancellation now
                # propagates:
                raise asyncio.CancelledError()
            return

    def admit_with_fence(
        self,
        state: RootRegionLineageState,
        t_result: RootRegionAdmissionResult,
        *,
        expected_revision: int,
    ) -> RecoveryFencedAdmitResult:
        """ONE fenced P/T transition of the live recovered
        owner (requirement 5).  A candidate the pure 019-c
        classifier marks ADVERSE against the retained
        current rows (a non-READY result, or a READY result
        withdrawing / rekeying a retained current key)
        makes the older durable bytes UNSAFE if they
        survive a crash, so the DURABLE fail-closed fence
        (the current retained record set recorded
        quarantined) is published under the
        bound-generation CAS BEFORE the transition is
        permitted; a fence that cannot be durably
        published BLOCKS the unsafe continuation (no
        admit, typed ``fence_refused``): a fault
        BEFORE the pointer publication leaves the
        prior committed generation valid (no admit,
        no state mutation and no quarantine
        occurred, so the retained current rows stay
        usable and the bound generation unchanged),
        while a fault AFTER the pointer rename may
        have already committed the fence generation
        (the ACTUAL observed generation is carried;
        the live owner cannot overwrite it -- a
        later checkpoint is the fixed generation-
        mismatch refusal, never a silent unfence --
        and the explicit teardown is the exit, after
        which a restart fails closed on the committed
        fence).
        After the fence: an admitted candidate advances
        the durable binding to the new record set (a
        failed advance keeps the RAM state and reports
        the actual committed outcome; the fence already
        makes crash recovery fail closed); a capacity
        refusal that quarantines the owner RETAINS the
        fence (durable and in-memory agree); any other
        refusal attempts the unfence (the old record set
        republished -- a failed unfence keeps the fence,
        fail closed).  A non-adverse candidate runs the
        accepted 019 law directly and advances the
        durable binding on admission.  No automatic epoch
        reset / retry / unquarantine exists on any
        path."""
        self._check_open()
        if self._tearing_down:
            return RecoveryFencedAdmitResult(
                RecoveryAdmitOutcome.REFUSED,
                fence=RecoveryPublishResult(
                    RecoveryStoreLimitation.WRITER_CONFLICT,
                    None,
                    None,
                    self._session.observed_generation,
                ),
                owner_quarantined=bool(self._owner.quarantined),
                bound_generation=self._bound,
            )
        if not self._registry.owned_store_io_acquire():
            return RecoveryFencedAdmitResult(
                RecoveryAdmitOutcome.REFUSED,
                fence=RecoveryPublishResult(
                    RecoveryStoreLimitation.WRITE_IN_FLIGHT,
                    None,
                    None,
                    self._session.observed_generation,
                ),
                owner_quarantined=bool(self._owner.quarantined),
                bound_generation=self._bound,
            )
        try:
            if not self._registry.recovery_op_begin(self._owner):
                # The closed 020-b preemption gap: the
                # exact live-owner join refused (the
                # owner is absent / fenced / replaced,
                # or its 019 work plane is already
                # draining and owns the release) -- a
                # clean typed refusal with NO cold
                # reservation and NO publication.  The
                # fenced case carries the ESTABLISHED
                # 020-a ``FENCE_REFUSED`` blocked-
                # continuation outcome (the durable
                # fence could not be published, so NO
                # transition is permitted -- the
                # accepted reverse-order result,
                # preserved) with the existing
                # ``WRITER_CONFLICT`` in the fence.
                return RecoveryFencedAdmitResult(
                    RecoveryAdmitOutcome.FENCE_REFUSED,
                    fence=RecoveryPublishResult(
                        RecoveryStoreLimitation.WRITER_CONFLICT,
                        None,
                        None,
                        self._session.observed_generation,
                    ),
                    owner_quarantined=bool(self._owner.quarantined),
                    bound_generation=self._bound,
                )
            try:
                return self._admit_with_fence_held(
                    state,
                    t_result,
                    expected_revision=expected_revision,
                )
            finally:
                self._registry.recovery_op_end(self._owner)
        finally:
            self._registry.owned_store_io_release()

    def _admit_with_fence_held(
        self,
        state: RootRegionLineageState,
        t_result: RootRegionAdmissionResult,
        *,
        expected_revision: int,
    ) -> RecoveryFencedAdmitResult:
        owner = self._owner
        namespace = owner.namespace
        advance: RecoveryPublishResult | None = None
        # The accepted pre-charge fence law runs BEFORE any
        # durable side effect (object class alone is not
        # authority): a forged / copied / mismatched /
        # stale candidate is refused with the EXACT admit
        # refusal and the durable record is untouched
        # (no fence can quarantine a valid session over a
        # candidate the accepted law rejects).
        preflight = owner.preflight_admission(
            state, t_result, namespace, expected_revision=expected_revision
        )
        if preflight is not None:
            return RecoveryFencedAdmitResult(
                RecoveryAdmitOutcome.REFUSED,
                admitted=preflight,
                owner_quarantined=bool(owner.quarantined),
                bound_generation=self._bound,
            )
        if not owner.would_quarantine(t_result):
            admitted = owner.admit(state, t_result, namespace, expected_revision=expected_revision)
            if admitted.outcome is not RamStateOutcome.ADMITTED:
                return RecoveryFencedAdmitResult(
                    RecoveryAdmitOutcome.REFUSED,
                    admitted=admitted,
                    owner_quarantined=bool(owner.quarantined),
                    bound_generation=self._bound,
                )
            advance = self.checkpoint_current_locked()
            return RecoveryFencedAdmitResult(
                RecoveryAdmitOutcome.ADMITTED,
                admitted=admitted,
                advance=advance,
                bound_generation=self._bound,
            )
        fence = self._publish_bounded(
            lambda: RecoveryRecord.from_owner(owner, quarantine_fence=True),
            self._bound,
        )
        if fence.limitation is not RecoveryStoreLimitation.OK or fence.generation is None:
            return RecoveryFencedAdmitResult(
                RecoveryAdmitOutcome.FENCE_REFUSED,
                fence=fence,
                owner_quarantined=bool(owner.quarantined),
                bound_generation=self._bound,
            )
        admitted = owner.admit(state, t_result, namespace, expected_revision=expected_revision)
        if admitted.outcome is not RamStateOutcome.ADMITTED:
            if not owner.quarantined:
                # The fence was published but the transition
                # was refused for a non-quarantining reason:
                # attempt the unfence (the old record set
                # republished under CAS); a failed unfence
                # keeps the fence (fail closed, safe).
                advance = self.checkpoint_current_locked()
            return RecoveryFencedAdmitResult(
                RecoveryAdmitOutcome.REFUSED,
                admitted=admitted,
                fence=fence,
                advance=advance,
                owner_quarantined=bool(owner.quarantined),
                bound_generation=self._bound,
            )
        advance = self.checkpoint_current_locked()
        return RecoveryFencedAdmitResult(
            RecoveryAdmitOutcome.ADMITTED,
            admitted=admitted,
            fence=fence,
            advance=advance,
            bound_generation=self._bound,
        )

    async def teardown(self) -> RecoveryTeardownResult:
        """The explicit recovery teardown (requirement 4):
        the work plane (when enabled) is drained through
        the ACTUAL 019-b async teardown (fence, cancel and
        await, then release the store owner AND the work
        occupancy in ONE critical section), or the store
        owner is torn down synchronously when the registry
        is work-disabled; only AFTER the store owner is
        fenced / released is the writer session closed and
        the lock released.  A refused teardown keeps the
        session held (no partial release).  The closed
        recovery owner refuses every further operation, so
        no late old-epoch write can publish through it,
        and a new resume of the session allocates a
        strictly higher epoch."""
        if self._closed:
            return RecoveryTeardownResult(RecoveryTeardownOutcome.REFUSED, None, None, None, False)
        self._tearing_down = True
        namespace = self._owner.namespace
        store_result: RamStateTeardownResult | None = None
        work_result: RamWorkTeardownResult | None = None
        try:
            # The owned ASYNC publication DRAINS first
            # (requirement 4): the owner's single owned
            # store IO completes (or faults) to its
            # actual typed result before anything else
            # can release -- a cancelled teardown holds
            # this drain (the 019-b drain law) and the
            # writer lock never leaks under
            # cancellation.
            owned = self._owned_publish
            if owned is not None and not owned.done():
                await self._drain_owned_publish(owned)
            if self._owned_publish is owned:
                self._owned_publish = None
            # Owned writes DRAIN before the writer is
            # released (requirement 4): an in-flight
            # checkpoint / fence / binding
            # publication completes (or faults) to
            # its typed result before the lock can be
            # released, so a late old-epoch write can
            # never publish after teardown.  The
            # claimed synchronous recovery operation
            # drains the SAME way (020-b, the closed
            # preemption gap): a write that won its
            # exact live-owner claim can still
            # reserve / publish, so the RAM
            # ownership is never fenced / released
            # and the session never closed until the
            # claim clears (a teardown that wins
            # instead retires the owner and the
            # claim refuses cleanly).  A cancelled
            # teardown keeps the session held (the
            # except path below closes only when the
            # store owner is ACTUALLY gone), so the
            # drain may be retried and the writer
            # lock never leaks under cancellation.
            while True:
                with self._registry._lock:
                    op_live = self._registry.recovery_op_live(namespace.lineage_key)
                if not op_live and self._session.in_flight == 0:
                    break
                await asyncio.sleep(0.01)
            work = self._registry.work
            if work is not None:
                work_result = await work.teardown_owner(namespace)
            else:
                store_result = self._owner.teardown(namespace)
        except BaseException:
            # The owned work teardown may finish its drain
            # / release and THEN propagate a cancellation
            # (the 019-b law: the drain completes before the
            # cancellation propagates).  Finish our own
            # cleanup BEFORE it propagates: the writer
            # session is closed only when the store owner
            # has ACTUALLY been released (the registry join
            # is the truth; a still-live owner keeps the
            # lock, and this teardown may be retried), so
            # the writer lock never leaks under
            # cancellation.
            if self._registry.get(namespace) is None:
                self._session.close()
                self._closed = True
            else:
                # The store owner is still live: nothing
                # was released, so lift the admission
                # fence (the owner stays usable and the
                # teardown is retryable).
                self._tearing_down = False
            raise
        if work_result is not None and work_result.outcome is not RamWorkOutcome.TEARDOWN:
            self._tearing_down = False
            return RecoveryTeardownResult(
                RecoveryTeardownOutcome.REFUSED,
                work_result.limitation,
                None,
                work_result,
                False,
            )
        if store_result is not None and store_result.outcome is not RamStateOutcome.TEARDOWN:
            self._tearing_down = False
            return RecoveryTeardownResult(
                RecoveryTeardownOutcome.REFUSED,
                store_result.limitation,
                store_result,
                None,
                False,
            )
        self._session.close()
        self._closed = True
        return RecoveryTeardownResult(
            RecoveryTeardownOutcome.TEARDOWN,
            None,
            store_result,
            work_result,
            True,
        )


def resume_session(
    registry: RamStateOwnerRegistry,
    store: RecoveryStore,
    address: RecoverySessionAddress,
) -> RecoveryResumeResult:
    """Resume EXACTLY ONE persisted session into the
    registry in a distinct live epoch strictly above the
    record's prior epoch.

    The writer session is opened for the call; on every
    outcome that creates no live owner it is released
    again, and on RESUMED / ADMIT_REFUSED it is RETAINED
    by the returned ``RecoverySessionOwner`` for the owner
    live lifetime (the explicit teardown is the only
    release).  A quarantined record, a store refusal, a
    non-restorable record, an already-live owner or a
    capacity-refused allocation is a typed outcome with
    NO new owner and NO partial RAM state published.  On
    RESUMED the durable epoch binding (the record's
    ``prior_epoch`` re-bound to the live epoch, all other
    fields verbatim) is published under the bound-
    generation CAS BEFORE the owner is exposed: a crash
    after a successful resume therefore never reuses that
    epoch in a later restart, and a failed binding is a
    typed ``store_refused`` carrying the ACTUAL observed
    post-attempt generation (the new binding may already
    be committed; no rollback is claimed, neither the old
    nor the new state assumed) with the owner torn down.
    The
    ADMIT_REFUSED owner retains nothing (no admitted
    record set), so its unrecorded epoch cannot
    resurrect state on a later restart."""
    if not registry.owned_store_io_acquire():
        # The ONE process owned store IO slot is
        # held by another owned publication (the
        # typed busy refusal BEFORE any session
        # open or IO; no queue, no partial state).
        return RecoveryResumeResult(
            RecoveryResumeOutcome.STORE_REFUSED,
            RecoveryStoreLimitation.WRITE_IN_FLIGHT,
        )
    try:
        return _resume_session_held(registry, store, address)
    finally:
        registry.owned_store_io_release()


def _resume_session_held(
    registry: RamStateOwnerRegistry,
    store: RecoveryStore,
    address: RecoverySessionAddress,
) -> RecoveryResumeResult:
    """The resume body with the ONE process owned
    store IO slot already held by ``resume_session``
    (the whole open / load / publish phase runs as
    bounded owned execution)."""
    try:
        session = store.open_session(address)
    except RecoveryStoreError as exc:
        return RecoveryResumeResult(RecoveryResumeOutcome.STORE_REFUSED, exc.limitation)
    # The COLD initial-load transient reservation
    # (requirement 4): reserved BEFORE the initial
    # load / decode runs -- ``session.load`` decodes
    # the committed record (the model / JSON objects
    # plus, below, the complete restore / T
    # derivation), so the reservation precedes that
    # FIRST allocation, under the TRUSTED resume
    # address key: the loaded full namespace does not
    # exist yet and must not be a lookup prerequisite
    # (requirement 2).  The bound is derived from the
    # CURRENT committed state: the record file's
    # committed byte size (the pointer's closed
    # ``record_bytes`` field, read by the bounded
    # pointer-only probe -- a closed fixed-shape
    # pre-reservation read that allocates no record
    # content) plus the closed schema floor; the
    # initial-load operation PEAK (the raw record
    # bytes, the decoded model objects and the
    # restore re-derivation coexisting) is at most 4x
    # the committed size, so the reservation is
    # ``max(4x committed, the closed schema floor)``.
    # It is checked against the SAME 019 process and
    # configured-session ceilings, BOUND to the
    # validated namespace's lineage key once the
    # record loads (the same atomic sums then see the
    # in-flight transient under the session's real
    # key), and released exactly once on every
    # outcome below.
    address_key = address.lineage_key
    committed = session.committed_record_bytes()
    reserve = max(4 * committed, RECOVERY_TRANSIENT_FLOOR_BYTES)
    try:
        registry.reserve_recovery_transient_cold(address_key, reserve)
    except RamStateCapacityError:
        # The initial load / decode transient cannot
        # be covered by the SAME 019 ceilings: nothing
        # is loaded, nothing is derived, no owner is
        # allocated, nothing is retained (typed
        # backpressure, no state change).
        session.close()
        return RecoveryResumeResult(
            RecoveryResumeOutcome.ALLOCATION_REFUSED,
            None,
            generation=session.observed_generation,
            prior_epoch=None,
        )
    except RamStateInputError:
        # A live registered owner under this
        # session's trusted key: the identity join
        # cannot be proven pre-load, and the
        # duplicate-live-owner law applies (the
        # registered owner stays untouched; no second
        # owner).
        session.close()
        return RecoveryResumeResult(
            RecoveryResumeOutcome.OWNER_ALREADY_LIVE,
            None,
            generation=session.observed_generation,
            prior_epoch=None,
        )
    reserved_key = address_key
    released = False
    try:
        # The initial load / decode now runs INSIDE the
        # reserved transient (the exclusive writer lock
        # makes the committed pointer stable between the
        # probe and this load).
        try:
            loaded = session.load()
        except RecoveryStoreError as exc:
            session.close()
            return RecoveryResumeResult(RecoveryResumeOutcome.STORE_REFUSED, exc.limitation)
        if (
            loaded.limitation is not RecoveryStoreLimitation.OK
            or loaded.record is None
            or loaded.pointer is None
        ):
            session.close()
            return RecoveryResumeResult(RecoveryResumeOutcome.STORE_REFUSED, loaded.limitation)
        record = loaded.record
        generation = loaded.pointer.generation
        prior_epoch = record.prior_epoch
        # The DURABLE quarantine fence: a record carrying the
        # bounded pre-accounted adverse-currentness
        # quarantine resumes NOTHING -- no owner, no admit, no
        # epoch reset, no silent unquarantine (the fence
        # persists through durability; only the explicit
        # teardown of a live quarantined owner is its exit).
        if record.quarantined:
            session.close()
            return RecoveryResumeResult(
                RecoveryResumeOutcome.QUARANTINE_PERSISTED,
                None,
                generation=generation,
                prior_epoch=prior_epoch,
            )
        namespace = record.namespace
        # The reservation is BOUND to the validated
        # loaded namespace (requirements 4 and 2): ONE
        # registry critical section moves the reserved
        # bytes from the trusted address key to the
        # namespace's lineage key (the SAME identity join
        # as ``get`` / ``acquire`` when a live owner
        # exists there -- the duplicate-live-owner case,
        # mapped to the closed outcome).
        try:
            registry.rebind_recovery_transient_cold(address_key, namespace)
        except RamStateInputError:
            session.close()
            return RecoveryResumeResult(
                RecoveryResumeOutcome.OWNER_ALREADY_LIVE,
                None,
                generation=generation,
                prior_epoch=prior_epoch,
            )
        reserved_key = namespace.lineage_key
        # The ACTUAL codec restore law (D integrity, P
        # reconstruction, P lineage law, ACTUAL T derivation)
        # runs BEFORE any RAM publication.
        try:
            state, t_result = recovery_restore_record(record)
        except RecoveryCodecIntegrityError:
            session.close()
            return RecoveryResumeResult(
                RecoveryResumeOutcome.RECORD_NOT_RESTORABLE,
                RecoveryResumeLimitation.CODEC_INTEGRITY,
                generation=generation,
                prior_epoch=prior_epoch,
            )
        except RecoveryCodecMalformedError:
            session.close()
            return RecoveryResumeResult(
                RecoveryResumeOutcome.RECORD_NOT_RESTORABLE,
                RecoveryResumeLimitation.CODEC_MALFORMED,
                generation=generation,
                prior_epoch=prior_epoch,
            )
        try:
            owner = registry.acquire_new_with_epoch_floor(namespace, floor=prior_epoch)
        except RamStateDuplicateOwnerError:
            # A live registered owner for this session already
            # exists in the registry (the strict allocation
            # refuses BEFORE any identity join, so the
            # value-equal decoded copy is handled safely and
            # the registered owner stays untouched).
            session.close()
            return RecoveryResumeResult(
                RecoveryResumeOutcome.OWNER_ALREADY_LIVE,
                None,
                generation=generation,
                prior_epoch=prior_epoch,
            )
        except RamStateCapacityError:
            # The owner base metadata cannot be covered by the
            # SAME 019 ceilings: no owner is allocated, nothing
            # is retained, and the refusal is typed (the
            # fixed 019-a atomic allocation law).
            session.close()
            return RecoveryResumeResult(
                RecoveryResumeOutcome.ALLOCATION_REFUSED,
                None,
                generation=generation,
                prior_epoch=prior_epoch,
            )
        # The restored P/T record set commits under the
        # MANDATORY expected-revision CAS (the fresh owner
        # binds zero).  A capacity refusal keeps the fresh
        # owner and its actual quarantine state, typed; the
        # durable checkpoint stays at the resumed generation
        # until an explicit fenced transition or checkpoint
        # moves it.
        admitted = owner.admit(state, t_result, namespace, expected_revision=0)
        if admitted.outcome is not RamStateOutcome.ADMITTED:
            return RecoveryResumeResult(
                RecoveryResumeOutcome.ADMIT_REFUSED,
                admitted.limitation,
                generation=generation,
                prior_epoch=prior_epoch,
                new_epoch=owner.epoch,
                owner=owner,
                t_result=t_result,
                owner_quarantined=bool(owner.quarantined),
                recovery=RecoverySessionOwner(
                    registry=registry,
                    session=session,
                    owner=owner,
                    address=address,
                    bound_generation=generation,
                    prior_epoch=prior_epoch,
                    new_epoch=owner.epoch,
                ),
            )
        # The DURABLE epoch binding (requirement 5): the
        # resumed incarnation's live epoch is recorded under
        # the bound-generation CAS BEFORE the owner is
        # exposed, so a crash after a successful resume never
        # reuses that epoch in a later restart (the next
        # resume -- same or fresh registry -- allocates
        # strictly above it).  The publication preserves every
        # other durable field verbatim (the exact original
        # bundles, provenance, the complete namespace
        # binding, the revision, the reason): it is restart
        # bookkeeping, never a usage-timestamp rewrite, and
        # the generation still serializes publication, never
        # source freshness.  A failed binding BLOCKS the
        # successful exposure: the owner is torn down, the
        # session closed, and the ACTUAL observed post-
        # attempt generation is carried (the rename may be
        # committed while directory durability is unconfirmed,
        # so neither state is assumed and no rollback is
        # claimed).
        bound = generation
        binding = record.with_epoch_binding(owner.epoch)
        if binding is not record:
            # The binding write runs under the SAME
            # reserved transient (no top-up: the binding
            # is a SAME-domain record, bounded ABOVE by
            # 4x the committed size plus the floor).
            try:
                encoded_binding = encode_recovery_record(binding, max_bytes=store.max_bytes)
            except RecoveryCodecSizeError:
                # Release the rebound transient BEFORE
                # tearing down the owner (the direct
                # teardown fence refuses RECOVERY_IN_FLIGHT
                # while it is still charged -- the leaked
                # usable-owner regression), then remove
                # the owner atomically.
                registry.release_recovery_transient_cold(reserved_key, reserve)
                released = True
                owner.teardown(namespace)
                # The ACTUAL observed generation is
                # captured BEFORE closing (a closed
                # session cannot observe its pointer).
                actual = session.observed_generation
                session.close()
                return RecoveryResumeResult(
                    RecoveryResumeOutcome.STORE_REFUSED,
                    RecoveryStoreLimitation.OVERSIZED,
                    generation=actual,
                    prior_epoch=prior_epoch,
                )
            except RecoveryCredentialQuarantineError:
                # Release the rebound transient BEFORE the
                # owner teardown (the same leak regression).
                registry.release_recovery_transient_cold(reserved_key, reserve)
                released = True
                owner.teardown(namespace)
                # The ACTUAL observed generation is
                # captured BEFORE closing (a closed
                # session cannot observe its pointer).
                actual = session.observed_generation
                session.close()
                return RecoveryResumeResult(
                    RecoveryResumeOutcome.STORE_REFUSED,
                    RecoveryStoreLimitation.CREDENTIAL_QUARANTINE,
                    generation=actual,
                    prior_epoch=prior_epoch,
                )
            published = session.publish_encoded(encoded_binding, binding, bound)
            if (
                published.limitation is not RecoveryStoreLimitation.OK
                or published.generation is None
            ):
                # Release the rebound transient BEFORE the
                # owner teardown (the same leak regression
                # as the encode faults above).
                registry.release_recovery_transient_cold(reserved_key, reserve)
                released = True
                owner.teardown(namespace)
                session.close()
                # Requirement 3 fault law at THIS boundary:
                # carry the ACTUAL observed post-attempt
                # generation (0 = no pointer committed, N =
                # that generation, None = a pointer exists
                # but is unreadable / corrupt) -- never an
                # assumption of the previous state.
                return RecoveryResumeResult(
                    RecoveryResumeOutcome.STORE_REFUSED,
                    published.limitation,
                    generation=published.actual_generation,
                    prior_epoch=prior_epoch,
                )
            bound = published.generation
        return RecoveryResumeResult(
            RecoveryResumeOutcome.RESUMED,
            None,
            generation=bound,
            prior_epoch=prior_epoch,
            new_epoch=owner.epoch,
            owner=owner,
            t_result=t_result,
            recovery=RecoverySessionOwner(
                registry=registry,
                session=session,
                owner=owner,
                address=address,
                bound_generation=bound,
                prior_epoch=prior_epoch,
                new_epoch=owner.epoch,
            ),
        )
    finally:
        if not released:
            registry.release_recovery_transient_cold(reserved_key, reserve)


__all__ = [
    "RECOVERY_RESUME_CONTRACT_VERSION",
    "RECOVERY_RESUME_POLICY_VERSION",
    "RECOVERY_TRANSIENT_FLOOR_BYTES",
    "RecoveryAdmitOutcome",
    "RecoveryFencedAdmitResult",
    "RecoveryResumeLimitation",
    "RecoveryResumeOutcome",
    "RecoveryResumeResult",
    "RecoverySessionOwner",
    "RecoveryTeardownOutcome",
    "RecoveryTeardownResult",
    "resume_session",
]

"""Bounded inert async single-flight and attempt ownership
(objective 019-b, second slice).

This component implements the ratified bounded async same-full-key
single-flight plane over the accepted 019-a RAM owner/store
foundation:

- ONE process-wide active leader (the closed constant
  ``RAM_WORK_ACTIVE_LEADERS``); the configurable positive non-bool
  bounds are the pending distinct-key queue, the waiters-per-key
  bound, the prepared-output size bound and the work time bound.
  The queue is bounded BEFORE any task / waiter / source
  reference is retained; a same-key join never consumes another
  distinct-key reservation, and unrelated admitted work proceeds
  when the active leader finishes or is cancelled.

- The ratified attempt policy: the full semantic content /
  configuration key joined to the genuine live cache epoch
  defines ONE admitted work attempt.  Before a claim, resource /
  concurrency queue admission may refuse (fixed typed 503, zero
  invocation, no attempt).  Once the bounded key reservation is
  accepted (including a queued reservation) the attempt is
  claimed; cancellation before dispatch still terminates that
  admitted attempt with zero actual invocations; there is no
  silent release-and-retry loophole.  Concurrent identical demand
  joins ONE shared operation / outcome; a single waiter
  cancellation detaches only that waiter; all waiters gone
  cancels AND awaits the owned work and leaves a terminal
  unsuccessful attempt.  A later request / nonce / revision /
  pressure never authorizes retry; a terminal failure is re-served
  to a later same-key / epoch request with the SAME fixed typed
  failure and zero new invocations (infrastructure / resource
  503, invalid / budget 422, currentness conflict 409); no raw
  exception content is retained.  A valid immutable payload
  survives supersession and is reused on a genuinely proven
  compatible revert without a new invocation; supersession and
  late completion never make obsolete content current.

- Every request / attempt / task / publication is bound to the
  ACTUAL registered trusted namespace record (the complete 018-p
  namespace law re-run at the registry boundary, identity join --
  a value-equal foreign copy cannot mint work), the ONE live
  owner, the explicit cache epoch and the ACTUAL currently
  admitted full key (current admissibility is resolved from the
  ACTUAL store state: the key must be among the owner's current
  admitted entry keys; strings alone cannot mint work).
  Publication re-checks the live owner / epoch and current
  source-key eligibility; a late completion for a superseded key
  cannot be published.

- The shared conservative occupancy: retained pending / active /
  terminal attempt metadata, historical successful payloads,
  task / waiter-owned references (covered by the documented
  closed fixed reservations) and indexes are charged BEFORE
  retention / publication on the ACTUAL measured recipe of the
  019-a store (identity-deduplicated referents) and aggregated
  atomically under the SAME process / session ceilings -- a
  synchronous admit and a work operation both honor the sums,
  and a crossing returns the fixed typed 503 backpressure
  contract with existing state preserved (no TTL / LRU /
  eviction / unbounded tombstones).  Terminal attempt records
  are a MANDATORY lifecycle retention (their absence would
  open a retry loophole): the bounded terminal reservation is
  charged BEFORE the claim is accepted (once per attempt, at
  the claimant's claim) and the attempt's terminal slot is
  PRE-ALLOCATED at the same claim (the terminal catalog's
  actual growth, charged into the same verified
  recomputation), so the mandatory terminalization -- the
  slot's reservation-to-actual record swap, or a queued
  cancellation -- is always non-positive in delta and can
  never cross either ceiling at a later resize boundary;
  there is no soft-cap exception for terminal metadata, and
  a terminal record is never evicted to retry.  No total-
  RSS promise.

- Explicit async session teardown (``teardown_owner``) fences the
  owner's work plane, cancels AND awaits its queued / active /
  shared work (every still-waiting waiter re-served the
  typed terminal) and then releases the store owner AND that
  owner's work occupancy in ONE critical section: the work
  plane stays fenced until the owner is actually torn down,
  so no same-epoch reset window can open (a later resolve
  finds no live owner, never a reset one), and every other
  session is preserved.  The synchronous owner teardown is
  refused with the fixed ``work_in_flight`` limitation while
  the work plane is fenced or still owns queued / active work
  -- including while the async work teardown is still
  draining its tasks (no silently orphaned work, no bypass of
  the live-task fence) -- and an IDLE work plane is released
  in the same critical section as the store release; a late
  completion after teardown is refused by the publication
  fence.

The component is INERT: the injected work seam is synthetic and
proves prepared-work orchestration only -- no actual
compiler / tokenizer semantic validation (021), no wire / HTTP
wiring (022), no recovery (020) and no v1 runtime activation.
No lock is held across await / model IO / SSE; the short
process-registry critical sections cover pure-memory
fence / charge / claim / commit / finalize sequences.  All
existing 018 and 019-a public signatures, defaults, schemas,
version tags, recipe bytes and behavior remain intact.
"""

from __future__ import annotations

import asyncio
import sys
from collections import deque
from collections.abc import Awaitable, Callable

from .ram_state import RamStateOwner, RamStateOwnerRegistry, _charge_object
from .ram_state_models import RamStateLimitation
from .ram_work_models import (
    RAM_WORK_TASK_RESERVATION_BYTES,
    RAM_WORK_TERMINAL_RESERVATION_BYTES,
    RAM_WORK_WAITER_RESERVATION_BYTES,
    RamWorkAttempt,
    RamWorkAttemptState,
    RamWorkBounds,
    RamWorkLimitation,
    RamWorkOutcome,
    RamWorkPayload,
    RamWorkRequestResult,
    RamWorkSeamReason,
    RamWorkTeardownResult,
    _content_key_shape_ok,
    ram_work_http_status,
)
from .root_region_admission_result_models import RootRegionAdmissionOutcome

WorkSeam = Callable[[], Awaitable[bytes]]


class RamWorkError(Exception):
    """Fixed typed RAM work boundary error base (019-b)."""


class RamWorkInputError(RamWorkError):
    """A malformed, detached or non-joined input record (or a
    malformed content-key / seam input) at the work component
    boundary: the operation is refused BEFORE any charge,
    traversal or claim work."""


class RamWorkSeamError(Exception):
    """The injected seam's TYPED failure declaration: the closed
    reason ``invalid`` (the seam declared its output invalid /
    unparseable) or ``truncated`` (the seam declared its output
    truncated).  Any other exception escaping the seam is the
    unclassified ``WORK_FAILED`` terminal; raw exception content
    is never retained."""

    def __init__(self, reason: object) -> None:
        if reason not in (RamWorkSeamReason.INVALID, RamWorkSeamReason.TRUNCATED):
            raise RamWorkInputError("the ram work seam reason must be the closed vocabulary")
        self.reason = reason


class _LiveAttempt:
    """ONE claimed (queued or active) attempt, mutable only
    inside the registry critical section (019-b).  ``waiters``
    are the retained waiter futures (each charged by the closed
    fixed waiter reservation); ``task`` is the dispatch task
    when this key owns the ONE active leader (charged by the
    closed fixed task reservation, committed BEFORE retention
    at dispatch); ``invocations`` is the ACTUAL injected work
    count (at most one -- no retry); ``claimant`` marks the
    waiter that claimed the attempt."""

    __slots__ = (
        "content_key",
        "epoch",
        "waiters",
        "task",
        "invocations",
        "work",
        "claimant",
        "terminal_before",
        "live_before",
    )

    def __init__(self, content_key: str, epoch: int, work: WorkSeam) -> None:
        self.content_key = content_key
        self.epoch = epoch
        self.waiters: list[asyncio.Future[RamWorkRequestResult]] = []
        self.task: asyncio.Task[None] | None = None
        self.invocations = 0
        self.work = work
        self.claimant: asyncio.Future[RamWorkRequestResult] | None = None
        # The terminal catalog container as it was BEFORE this
        # attempt's reserved slot was pre-allocated (restored on
        # a refused claim: deleting the slot would not shrink a
        # resized table, so the ORIGINAL container is the exact
        # pre-claim state); None when no slot was allocated.
        self.terminal_before: dict[tuple[int, str], RamWorkAttempt | None] | None = None
        # The owner live-attempt map as it was BEFORE this new
        # attempt was staged into a candidate copy (restored on
        # a refused claim for the same exact-preservation
        # reason); None when the claim joined an existing
        # attempt.
        self.live_before: dict[str, _LiveAttempt] | None = None


class _OwnerWork:
    """The retained work state of ONE live owner (019-b): the
    live (queued / active) attempts, the retained TERMINAL
    attempt records (never evicted; a terminal failure is
    re-served to a later same-key / epoch request), the retained
    immutable successful payloads (a supersession of the current
    key never destroys a valid payload) and the charged session
    work occupancy.  ``fenced`` marks the async work teardown
    (the drain still owns the live tasks until every finalizer
    has run).  Teardown ``freed_bytes`` report the work charge
    captured at fence time plus the store release -- the
    complete occupancy released by THIS teardown (the drain's
    finalizations commit part of that release while draining);
    prior normal finalizations are not teardown frees."""

    __slots__ = ("epoch", "live", "terminal", "payloads", "bytes", "fenced", "notified")

    def __init__(self, epoch: int) -> None:
        self.epoch = epoch
        self.live: dict[str, _LiveAttempt] = {}
        # Retained TERMINAL records plus RESERVED terminal
        # slots: a None value is the pre-allocated slot of ONE
        # claimed (still live) attempt.  Pre-allocating the
        # slot at claim time charges the terminal catalog's
        # actual growth (the tuple key plus any dict resize
        # step, which grows with catalog size) BEFORE the
        # claim is accepted, so the finalization's record
        # swap -- and a queued cancellation -- can never cross
        # a ceiling at a later resize boundary.
        self.terminal: dict[tuple[int, str], RamWorkAttempt | None] = {}
        self.payloads: dict[tuple[int, str], RamWorkPayload] = {}
        self.bytes = 0
        self.fenced = False
        self.notified = 0


class RamWorkCoordinator:
    """The bounded process-wide single-flight coordinator
    (019-b), created by an explicit registry
    ``work_bounds`` (the work plane is inert unless enabled;
    the 019-a default behavior is unchanged).

    ONE active leader (the closed constant), a bounded
    pending distinct-key FIFO, per-key bounded waiters.  All
    state mutation runs inside the short process-registry
    critical section (pure memory only -- no model IO or SSE);
    the dispatch tasks are asyncio tasks owned independently of
    any first waiter and cancelled / awaited by the all-waiters-
    gone law or the explicit async teardown."""

    __slots__ = ("_registry", "_bounds", "_owners", "_active_key", "_queue", "_pump_scheduled")

    def __init__(
        self, registry: RamStateOwnerRegistry, bounds: RamWorkBounds | None = None
    ) -> None:
        self._registry = registry
        self._bounds = bounds if bounds is not None else RamWorkBounds()
        self._owners: dict[str, _OwnerWork] = {}
        self._active_key: tuple[str, str] | None = None
        self._queue: deque[tuple[str, str]] = deque()
        self._pump_scheduled = False
        # The shared coordinator shell (the instance, its owner
        # map, its queue and the RETAINED work-bounds record)
        # is owned retained process metadata: charged into the
        # process occupancy once at construction under the
        # ACTUAL measured sizes (committed on top of the
        # registry shell charge, BEFORE any owner allocation
        # can be checked against the process ceiling).
        registry._commit_process_delta(
            sys.getsizeof(self)
            + sys.getsizeof(self._owners)
            + sys.getsizeof(self._queue)
            + _charge_object(self._bounds, set())
        )

    @property
    def bounds(self) -> RamWorkBounds:
        return self._bounds

    # -- occupancy recipe (documented closed reservation) --------

    def _owner_work_bytes(self, ow: _OwnerWork) -> int:
        """The conservative occupancy of ONE owner's retained
        work state: the retained terminal attempt records and
        successful payloads under the 019-a ACTUAL measured
        recipe (identity-deduplicated referents), the live map
        shell and each live attempt shell, the ACTUAL content-
        key strings, plus the closed fixed reservations for
        the runtime objects that cannot be safely measured
        (the live dispatch task reference -- including its
        retained work-closure reference -- and each retained
        waiter future), and the closed terminal reservation
        for each live attempt (charged ONCE per attempt, at
        the claimant's claim, BEFORE the claim is accepted:
        the finalizer's reservation-to-actual swap can
        therefore never cross a ceiling -- no soft-cap
        exception)."""
        seen: set[int] = set()
        total = sys.getsizeof(ow)
        total += _charge_object(ow.terminal, seen)
        total += _charge_object(ow.payloads, seen)
        total += sys.getsizeof(ow.live)
        for la in ow.live.values():
            total += sys.getsizeof(la)
            total += _charge_object(la.content_key, seen)
            total += RAM_WORK_TERMINAL_RESERVATION_BYTES
            if la.task is not None and not la.task.done():
                total += RAM_WORK_TASK_RESERVATION_BYTES
            total += len(la.waiters) * RAM_WORK_WAITER_RESERVATION_BYTES
        return total

    def session_bytes(self, lineage_key: str) -> int:
        """The owner's charged WORK occupancy (the synchronous
        admit's session ceiling check adds this to the store
        occupancy; the caller holds the registry lock)."""
        ow = self._owners.get(lineage_key)
        return ow.bytes if ow is not None else 0

    def owner_work_active(self, lineage_key: str) -> bool:
        """The synchronous-teardown work fence: True while the
        owner's work plane is FENCED (the async work teardown
        is draining its tasks) or still owns QUEUED / ACTIVE
        work.  The caller holds the registry lock."""
        ow = self._owners.get(lineage_key)
        return ow is not None and (ow.fenced or bool(ow.live))

    def release_idle_owner(self, lineage_key: str) -> int:
        """Release an IDLE work plane in the synchronous
        teardown's critical section: no live work, not fenced
        (the fenced / live cases are refused by the store
        BEFORE this is reached).  Commits the owner's charged
        work occupancy out and drops the state atomically with
        the store release the caller is performing; returns
        the released bytes (0 when the owner has no work
        state).  The caller holds the registry lock."""
        ow = self._owners.get(lineage_key)
        if ow is None or ow.fenced or ow.live:
            return 0
        freed = ow.bytes
        if freed:
            self._registry._commit_process_delta(-freed)
        self._owners.pop(lineage_key, None)
        ow.bytes = 0
        return freed

    # -- store-state resolution -----------------------------------

    @staticmethod
    def _current_keys_locked(owner: RamStateOwner) -> frozenset[str] | None:
        """The ACTUAL current admitted content keys of the
        owner (from the ACTUAL store state: the current
        snapshot's READY admission rows) or None when the owner
        has no current READY record set."""
        snap = owner.snapshot
        if snap is None:
            return None
        result = snap.result
        if result.outcome is not RootRegionAdmissionOutcome.READY:
            return None
        admission = result.admission
        if admission is None:
            return None
        return frozenset(
            (admission.root_entry.content_key, *(e.content_key for e in admission.entries))
        )

    # -- finalization (caller holds the registry lock) ------------

    def _finalize_attempt_locked(
        self,
        owner: RamStateOwner,
        ow: _OwnerWork,
        la: _LiveAttempt,
        outcome: RamWorkOutcome,
        limitation: RamWorkLimitation | RamStateLimitation | None,
        payload: RamWorkPayload | None,
    ) -> None:
        """Materialize the TERMINAL attempt record (a mandatory
        lifecycle retention: retained, charged, never evicted --
        its absence would open a retry loophole), release the
        live reservation, re-serve the typed outcome to every
        still-waiting waiter and clear the active slot.  The
        record replaces the attempt's PRE-ALLOCATED reserved
        slot (no terminal-catalog resize can happen here: the
        catalog's actual growth was charged at claim time),
        and the charge delta swaps the claimant's BOUNDED
        terminal reservation for the actual record charge:
        because the reservation is a documented upper bound on
        that charge, the swap is always non-positive and can
        never cross a ceiling -- there is no soft-cap
        exception for terminal metadata."""
        okey = owner.namespace.lineage_key
        record = RamWorkAttempt(
            content_key=la.content_key,
            epoch=la.epoch,
            state=RamWorkAttemptState.TERMINAL,
            outcome=outcome,
            limitation=limitation,
            invocations=la.invocations,
            payload=payload,
        )
        old = ow.bytes
        ow.terminal[(la.epoch, la.content_key)] = record
        if payload is not None:
            ow.payloads[(la.epoch, la.content_key)] = payload
        del ow.live[la.content_key]
        try:
            self._queue.remove((okey, la.content_key))
        except ValueError:
            pass
        ow.bytes = self._owner_work_bytes(ow)
        delta = ow.bytes - old
        self._registry._commit_process_delta(delta)
        pair = self._active_key
        if pair is not None and pair == (okey, la.content_key):
            self._active_key = None
        notified = 0
        for fut in la.waiters:
            if fut.done():
                continue
            if outcome is RamWorkOutcome.COMPLETED:
                req_outcome = (
                    RamWorkOutcome.COMPLETED if fut is la.claimant else RamWorkOutcome.JOINED
                )
                fut.set_result(
                    RamWorkRequestResult(
                        outcome=req_outcome,
                        limitation=None,
                        payload=payload,
                        invocations=1 if fut is la.claimant else 0,
                        attempt_invocations=la.invocations,
                        epoch=la.epoch,
                        http_status=None,
                    )
                )
            else:
                # The ORIGINAL claimant is credited with the ACTUAL
                # shared invocation when it ran (a FAILED terminal
                # of a dispatched attempt still consumed its one
                # invocation; a queued cancellation consumed none);
                # followers are always zero, and a later same-key
                # re-serve reports zero for its own request.
                fut.set_result(
                    RamWorkRequestResult(
                        outcome=RamWorkOutcome.FAILED,
                        limitation=limitation,
                        payload=None,
                        invocations=1 if fut is la.claimant and la.invocations == 1 else 0,
                        attempt_invocations=la.invocations,
                        epoch=la.epoch,
                        http_status=ram_work_http_status(limitation),
                    )
                )
            notified += 1
        ow.notified += notified
        la.waiters.clear()

    def _refused(
        self, limitation: RamWorkLimitation | RamStateLimitation, epoch: int
    ) -> RamWorkRequestResult:
        return RamWorkRequestResult(
            outcome=RamWorkOutcome.REFUSED,
            limitation=limitation,
            payload=None,
            invocations=0,
            attempt_invocations=0,
            epoch=epoch,
            http_status=ram_work_http_status(limitation),
        )

    # -- claim (caller holds the registry lock) -------------------

    def _claim_locked(
        self,
        loop: asyncio.AbstractEventLoop,
        owner: RamStateOwner,
        ow: _OwnerWork | None,
        content_key: str,
        work: WorkSeam,
    ) -> (
        tuple[asyncio.Future[RamWorkRequestResult], _OwnerWork, _LiveAttempt] | RamWorkRequestResult
    ):
        """The atomic claim / join decision (pure memory): the
        pre-claim queue / waiter capacity fences, the waiter
        future, the RESERVED terminal slot for a new attempt
        (the terminal catalog's actual growth, charged into the
        same recomputation), the BEFORE-retention occupancy
        charge and the SAME-ceiling checks (a crossing refuses
        with the fixed typed 503 and retains nothing: a
        freshly created work state / attempt is discarded
        without registration or commit; an existing state
        rolls the claim back to its exact pre-claim charge).
        A same-key join never allocates a second slot: the
        attempt's reserved slot was allocated by the
        claimant's claim."""
        okey = owner.namespace.lineage_key
        epoch = owner.epoch
        if ow is None:
            created_ow = True
            ow = _OwnerWork(epoch)
        else:
            created_ow = False
        la = ow.live.get(content_key)
        if la is None:
            distinct = (1 if self._active_key is not None else 0) + len(self._queue)
            if distinct >= self._bounds.max_pending_distinct_keys:
                return self._refused(RamWorkLimitation.PENDING_KEYS_OVER_BOUND, epoch)
            la = _LiveAttempt(content_key, epoch, work)
            # STAGE the new attempt into a candidate live map:
            # the ORIGINAL container is retained untouched for
            # exact restoration on a refused claim (an in-
            # place insert followed by a delete would not
            # shrink a resized table).
            la.live_before = ow.live
            ow.live = {**ow.live, content_key: la}
            self._queue.append((okey, content_key))
            created_la = True
        else:
            created_la = False
        if len(la.waiters) + 1 > self._bounds.max_waiters_per_key:
            if created_la:
                if la.live_before is not None:
                    ow.live = la.live_before
                self._queue.remove((okey, content_key))
            # A freshly created work state is discarded without
            # registration or commit; nothing was retained.
            return self._refused(RamWorkLimitation.WAITERS_PER_KEY_OVER_BOUND, epoch)
        fut: asyncio.Future[RamWorkRequestResult] = loop.create_future()
        old = ow.bytes
        la.waiters.append(fut)
        if la.claimant is None:
            la.claimant = fut
        if created_la:
            # Pre-allocate this attempt's reserved terminal
            # slot so the terminal catalog's ACTUAL growth
            # (tuple key plus any resize step) is charged into
            # the recomputation below and verified by BOTH
            # ceilings BEFORE the claim is accepted.  STAGE
            # the slot into a candidate copy: the ORIGINAL
            # container is retained untouched for exact
            # restoration on a refused claim (deleting the
            # slot would not shrink a resized table).
            la.terminal_before = ow.terminal
            ow.terminal = {**ow.terminal, (la.epoch, content_key): None}
        ow.bytes = self._owner_work_bytes(ow)
        delta = ow.bytes - old
        if owner.owned_bytes + ow.bytes > owner.session_max_owned_bytes:
            self._roll_back_waiter_locked(okey, ow, la, fut, created_la, created_ow)
            return self._refused(RamStateLimitation.SESSION_OWNED_BYTES_OVER_BOUND, epoch)
        if (
            self._registry.process_owned_bytes + delta
            > self._registry.bounds.process_max_owned_bytes
        ):
            self._roll_back_waiter_locked(okey, ow, la, fut, created_la, created_ow)
            return self._refused(RamStateLimitation.PROCESS_OWNED_BYTES_OVER_BOUND, epoch)
        if created_la:
            # The pre-staged rollback containers are needed
            # ONLY until the capacity decision: once the claim
            # is accepted, drop the references so they cannot
            # invisibly retain the pre-claim containers (and
            # what they reference) for the attempt's whole
            # queued / active lifetime (the refused-claim
            # restoration above is unchanged).
            la.live_before = None
            la.terminal_before = None
        if created_ow:
            self._owners[okey] = ow
        self._registry._commit_process_delta(delta)
        self._maybe_pump_locked(loop)
        return fut, ow, la

    def _roll_back_waiter_locked(
        self,
        okey: str,
        ow: _OwnerWork,
        la: _LiveAttempt,
        fut: asyncio.Future[RamWorkRequestResult],
        created_la: bool,
        created_ow: bool,
    ) -> None:
        """Undo a refused claim (retains nothing, restores the
        exact pre-claim charge): drop the waiter, and when the
        refused claim created the attempt with no other waiter,
        drop the attempt and its queue reservation too.  The
        pre-allocated terminal slot is undone by RESTORING the
        original catalog container (deleting the key would not
        shrink a resized table, so delete alone would not
        restore the exact pre-claim charge).  On an EXISTING
        work state the charged occupancy is RECOMPUTED after
        the drop, so a refused join to an existing live attempt
        restores ``ow.bytes`` exactly (the waiter reservation
        it added is undone); on a freshly created work state
        nothing was ever registered or committed, so its charge
        is simply abandoned (its pre-claim charge was zero)."""
        if fut in la.waiters:
            la.waiters.remove(fut)
        if la.claimant is fut:
            la.claimant = None
        if created_la and not la.waiters:
            del ow.live[la.content_key]
            try:
                self._queue.remove((okey, la.content_key))
            except ValueError:
                pass
        if created_la:
            if la.terminal_before is not None:
                ow.terminal = la.terminal_before
                la.terminal_before = None
        if created_ow:
            ow.bytes = 0  # abandoned: never registered / committed
        else:
            ow.bytes = self._owner_work_bytes(ow)

    # -- pump / dispatch (asyncio, on the event loop thread) -----

    def _maybe_pump_locked(self, loop: asyncio.AbstractEventLoop) -> None:
        if self._active_key is not None or self._pump_scheduled or not self._queue:
            return
        self._pump_scheduled = True
        loop.create_task(self._pump())

    async def _pump(self) -> None:
        """Advance the queue: dispatch the next eligible claim
        under the ONE active leader (the closed fixed task
        reservation is charged BEFORE the task is retained,
        under the SAME ceilings -- a crossing finalizes the
        claim with the fixed typed 503 and dispatches nothing),
        or finalize the fence-crossed queued claims (key no
        longer current, owner torn down / fenced, epoch
        changed) and continue."""
        with self._registry._lock:
            self._pump_scheduled = False
        loop = asyncio.get_running_loop()
        while True:
            with self._registry._lock:
                if self._active_key is not None:
                    return
                if not self._queue:
                    return
                okey, content_key = self._queue[0]
                owner = self._registry._owners.get(okey)
                ow = self._owners.get(okey)
                la = ow.live.get(content_key) if ow is not None else None
                keys = self._current_keys_locked(owner) if owner is not None else None
                if (
                    ow is None
                    or owner is None
                    or la is None
                    or ow.fenced
                    or owner.epoch_fenced
                    or la.epoch != owner.epoch
                    or keys is None
                    or content_key not in keys
                ):
                    self._queue.popleft()
                    if ow is not None and owner is not None and la is not None:
                        limitation = (
                            RamWorkLimitation.EPOCH_CHANGED
                            if la.epoch != owner.epoch
                            else RamWorkLimitation.OWNER_TORN_DOWN
                            if ow.fenced or owner.epoch_fenced
                            else RamWorkLimitation.KEY_NOT_CURRENT
                        )
                        self._finalize_attempt_locked(
                            owner, ow, la, RamWorkOutcome.CANCELLED, limitation, None
                        )
                    continue
                # The closed fixed task reservation is charged
                # BEFORE the dispatch task is retained, under
                # the SAME ceilings (the delta is exactly the
                # reservation: nothing else changes in this
                # critical section).
                delta = RAM_WORK_TASK_RESERVATION_BYTES
                if owner.owned_bytes + ow.bytes + delta > owner.session_max_owned_bytes:
                    self._queue.popleft()
                    self._finalize_attempt_locked(
                        owner,
                        ow,
                        la,
                        RamWorkOutcome.FAILED,
                        RamStateLimitation.SESSION_OWNED_BYTES_OVER_BOUND,
                        None,
                    )
                    continue
                if (
                    self._registry.process_owned_bytes + delta
                    > self._registry.bounds.process_max_owned_bytes
                ):
                    self._queue.popleft()
                    self._finalize_attempt_locked(
                        owner,
                        ow,
                        la,
                        RamWorkOutcome.FAILED,
                        RamStateLimitation.PROCESS_OWNED_BYTES_OVER_BOUND,
                        None,
                    )
                    continue
                self._queue.popleft()
                self._active_key = (okey, content_key)
                la.task = loop.create_task(self._run_work(okey, owner, ow, la))
                ow.bytes += delta
                self._registry._commit_process_delta(delta)
                return

    # -- dispatch / run (asyncio, on the event loop thread) ------

    async def _run_work(
        self, okey: str, owner: RamStateOwner, ow: _OwnerWork, la: _LiveAttempt
    ) -> None:
        """The ONE active leader dispatch for a claimed key:
        run the injected seam under the closed time bound,
        validate the bounded output shape, pass the ACTUAL
        publication fence (live owner / unchanged epoch /
        current key) and charge the payload BEFORE retention --
        or leave the terminal unsuccessful record (timeout,
        typed seam failure, unclassified failure, output shape,
        fence crossing, capacity crossing).  No raw exception
        content is retained.  Cancellation (all waiters gone or
        the async teardown) terminates the attempt and re-
        raises, so the owned work is cancelled AND (by the
        detaching waiter or the teardown) awaited."""
        finalized = False
        try:
            with self._registry._lock:
                if la.invocations == 0:
                    la.invocations = 1
            limitation: RamWorkLimitation | RamStateLimitation | None = None
            payload: RamWorkPayload | None = None
            try:
                raw = await asyncio.wait_for(la.work(), timeout=self._bounds.max_work_seconds)
            except TimeoutError:
                limitation = RamWorkLimitation.WORK_TIMEOUT
            except asyncio.CancelledError:
                with self._registry._lock:
                    self._finalize_attempt_locked(
                        owner,
                        ow,
                        la,
                        RamWorkOutcome.CANCELLED,
                        RamWorkLimitation.OWNER_TORN_DOWN
                        if ow.fenced
                        else RamWorkLimitation.ALL_WAITERS_DEPARTED,
                        None,
                    )
                    finalized = True
                raise
            except RamWorkSeamError as exc:
                limitation = (
                    RamWorkLimitation.INVALID_OUTPUT
                    if exc.reason is RamWorkSeamReason.INVALID
                    else RamWorkLimitation.TRUNCATED_OUTPUT
                )
            except Exception:
                limitation = RamWorkLimitation.WORK_FAILED
            else:
                if type(raw) is not bytes:
                    limitation = RamWorkLimitation.INVALID_OUTPUT
                elif len(raw) > self._bounds.max_output_bytes:
                    limitation = RamWorkLimitation.OUTPUT_OVER_BOUND
                else:
                    payload = RamWorkPayload(content_key=la.content_key, data=raw)
            if limitation is not None or payload is None:
                outcome = RamWorkOutcome.FAILED
            else:
                # The ACTUAL publication fence (live owner,
                # unchanged epoch, still-current key) plus the
                # BEFORE-retention payload charge under the SAME
                # ceilings: a late completion for a superseded
                # key (or a crossing payload) is terminal
                # unsuccessful and publishes nothing (the
                # tentatively set payload is released before
                # finalization).
                outcome = RamWorkOutcome.COMPLETED
                with self._registry._lock:
                    if ow.fenced or owner.epoch_fenced:
                        limitation = RamWorkLimitation.OWNER_TORN_DOWN
                        outcome = RamWorkOutcome.FAILED
                    elif owner.epoch != la.epoch:
                        limitation = RamWorkLimitation.EPOCH_CHANGED
                        outcome = RamWorkOutcome.FAILED
                    else:
                        keys = self._current_keys_locked(owner)
                        if keys is None or la.content_key not in keys:
                            limitation = RamWorkLimitation.KEY_NOT_CURRENT
                            outcome = RamWorkOutcome.FAILED
                        else:
                            old = ow.bytes
                            payloads_before = ow.payloads
                            # STAGE the payload into a candidate
                            # copy: the ORIGINAL container is
                            # retained untouched for exact
                            # restoration on a crossing (a
                            # delete would not shrink a resized
                            # table).
                            ow.payloads = {**ow.payloads, (la.epoch, la.content_key): payload}
                            ow.bytes = self._owner_work_bytes(ow)
                            p_delta = ow.bytes - old
                            if owner.owned_bytes + ow.bytes > owner.session_max_owned_bytes:
                                ow.payloads = payloads_before
                                ow.bytes = self._owner_work_bytes(ow)
                                limitation = RamStateLimitation.SESSION_OWNED_BYTES_OVER_BOUND
                                outcome = RamWorkOutcome.FAILED
                            elif (
                                self._registry.process_owned_bytes + p_delta
                                > self._registry.bounds.process_max_owned_bytes
                            ):
                                ow.payloads = payloads_before
                                ow.bytes = self._owner_work_bytes(ow)
                                limitation = RamStateLimitation.PROCESS_OWNED_BYTES_OVER_BOUND
                                outcome = RamWorkOutcome.FAILED
                            else:
                                self._registry._commit_process_delta(p_delta)
                                limitation = None
            if not finalized:
                with self._registry._lock:
                    self._finalize_attempt_locked(
                        owner,
                        ow,
                        la,
                        outcome,
                        limitation,
                        payload if limitation is None else None,
                    )
        finally:
            with self._registry._lock:
                if self._active_key is not None and self._active_key == (okey, la.content_key):
                    self._active_key = None
                self._maybe_pump_locked(asyncio.get_running_loop())

    # -- waiter detachment (caller holds the registry lock) ------

    def _detach_waiter_locked(
        self,
        owner: RamStateOwner,
        ow: _OwnerWork | None,
        la: _LiveAttempt | None,
        fut: asyncio.Future[RamWorkRequestResult],
        loop: asyncio.AbstractEventLoop,
        okey: str,
    ) -> asyncio.Task[None] | None:
        """Detach ONE cancelled waiter: it never cancels another
        live waiter's work.  When the last waiter departs, the
        owned work is cancelled -- or, before dispatch, the
        attempt is terminated with zero actual invocations --
        and the still-runnable cancelled dispatch task is
        RETURNED so the detaching waiter awaits the owned
        work's cleanup (the cancel-AND-await law) before
        re-raising.  When the dispatch task was already
        cancelled and processed BEFORE its first step (the
        in-task finalizer therefore never ran), the owner
        finalizes the attempt exactly once here instead of
        leaking the live attempt and the active slot."""
        if ow is None or la is None:
            return None
        if fut in la.waiters:
            la.waiters.remove(fut)
            if la.claimant is fut:
                la.claimant = None
        if not la.waiters:
            if la.task is None:
                self._finalize_attempt_locked(
                    owner,
                    ow,
                    la,
                    RamWorkOutcome.CANCELLED,
                    RamWorkLimitation.ALL_WAITERS_DEPARTED,
                    None,
                )
                return None
            if la.task.done():
                self._finalize_unrun_task_locked(
                    owner,
                    ow,
                    la,
                    okey,
                    RamWorkLimitation.ALL_WAITERS_DEPARTED,
                )
                self._maybe_pump_locked(loop)
                return None
            la.task.cancel()
            return la.task
        return None

    def _finalize_unrun_task_locked(
        self,
        owner: RamStateOwner,
        ow: _OwnerWork,
        la: _LiveAttempt,
        okey: str,
        limitation: RamWorkLimitation,
    ) -> None:
        """Owner-side EXACTLY-ONCE finalization for a dispatch
        task that was cancelled BEFORE it ever executed its
        first step: the task body (and therefore the in-task
        finalizer) never ran, so the live attempt, its
        reserved terminal slot, the active slot and the still-
        waiting waiters would otherwise stay live forever
        (zero actual seam invocations).  The guard is the live
        map itself: when the in-task finalizer already ran,
        the attempt is gone and this is a no-op.  The caller
        holds the registry lock and awaits the cancelled task
        BEFORE calling this."""
        if la.content_key not in ow.live:
            return
        self._finalize_attempt_locked(owner, ow, la, RamWorkOutcome.CANCELLED, limitation, None)

    # -- public surface -------------------------------------------

    async def resolve(
        self, namespace: object, content_key: object, work: WorkSeam
    ) -> RamWorkRequestResult:
        """Resolve ONE demand for the ACTUAL admitted full key:
        a retained valid payload of the same epoch is a RAM-only
        HIT (zero invocations); a retained terminal failure of
        the same key / epoch is re-served with the SAME fixed
        typed failure (zero invocations, no retry); otherwise
        the demand claims the key (or joins the shared attempt)
        under the bounded queue / waiter / capacity fences and
        awaits the shared outcome.  The entire claim decision
        runs in ONE short critical section (pure memory); the
        await is outside the lock.  A cancelled request task
        detaches that waiter only, and when it was the last
        waiter it awaits the cancelled owned work before
        re-raising."""
        if not callable(work):
            raise RamWorkInputError("the ram work seam must be a callable")
        owner = self._registry.get(namespace)
        if owner is None:
            return self._refused(RamWorkLimitation.OWNER_ABSENT, 0)
        if not _content_key_shape_ok(content_key):
            raise RamWorkInputError("the ram work content key is malformed")
        loop = asyncio.get_running_loop()
        ow: _OwnerWork | None = None
        la: _LiveAttempt | None = None
        fut: asyncio.Future[RamWorkRequestResult]
        with self._registry._lock:
            okey = owner.namespace.lineage_key
            ow = self._owners.get(okey)
            if ow is not None and ow.fenced:
                return self._refused(RamWorkLimitation.OWNER_TORN_DOWN, owner.epoch)
            keys = self._current_keys_locked(owner)
            if keys is None or content_key not in keys:
                return self._refused(RamWorkLimitation.KEY_NOT_CURRENT, owner.epoch)
            epoch = owner.epoch
            terminal = ow.terminal.get((epoch, content_key)) if ow is not None else None
            if terminal is not None and terminal.outcome is not RamWorkOutcome.COMPLETED:
                return RamWorkRequestResult(
                    outcome=RamWorkOutcome.FAILED,
                    limitation=terminal.limitation,
                    payload=None,
                    invocations=0,
                    attempt_invocations=terminal.invocations,
                    epoch=epoch,
                    http_status=ram_work_http_status(terminal.limitation),
                )
            payload = ow.payloads.get((epoch, content_key)) if ow is not None else None
            if payload is not None:
                return RamWorkRequestResult(
                    outcome=RamWorkOutcome.HIT,
                    limitation=None,
                    payload=payload,
                    invocations=0,
                    attempt_invocations=0,
                    epoch=epoch,
                    http_status=None,
                )
            claim = self._claim_locked(loop, owner, ow, content_key, work)
            if isinstance(claim, RamWorkRequestResult):
                return claim
            fut, ow, la = claim
        cancelled_task: asyncio.Task[None] | None = None
        try:
            return await fut
        except asyncio.CancelledError:
            with self._registry._lock:
                cancelled_task = self._detach_waiter_locked(owner, ow, la, fut, loop, okey)
            if cancelled_task is not None:
                # Cancel-AND-await the owned work (its
                # finalizer runs to completion) before
                # re-raising this waiter's cancellation.
                try:
                    await cancelled_task
                except (asyncio.CancelledError, Exception):
                    pass
                # The deterministic scheduling boundary: if
                # the task was cancelled BEFORE it executed
                # its first step, the in-task finalizer never
                # ran; the owner finalizes it exactly once
                # here (zero actual invocations) so the
                # attempt, the active slot and any queued
                # work all close instead of leaking.
                with self._registry._lock:
                    self._finalize_unrun_task_locked(
                        owner,
                        ow,
                        la,
                        okey,
                        RamWorkLimitation.ALL_WAITERS_DEPARTED,
                    )
                    self._maybe_pump_locked(asyncio.get_running_loop())
            raise

    async def teardown_owner(self, namespace: object) -> RamWorkTeardownResult:
        """The explicit async session teardown of the work
        plane: fence the owner's work plane, terminate its
        queued claims (zero invocations) and cancel AND await
        its active / shared work (every still-waiting waiter
        re-served the typed terminal), then release the store
        owner AND this owner's work occupancy in ONE
        critical section -- the work plane stays fenced until
        the owner is actually torn down, so no same-epoch
        reset window can open and a later resolve finds no
        live owner (a new epoch only comes from an explicit
        re-acquire / the 020 restart) -- preserving every
        other owner.  If this teardown task itself is
        cancelled during the drain, the fence is kept and the
        drain is completed before the cancellation propagates
        (no fence outliving the drain, no store released
        under live work, no silently orphaned work).
        A live store owner with NO work plane is still fully
        torn down: the store release happens in the same
        critical section.  Refuses with the fixed typed fence
        when there is no live owner or the work plane is
        already fenced.  ``freed_bytes`` is the process
        occupancy released by THIS teardown (store plus
        work: the work charge captured at fence time plus the
        store release); prior normal completions are not
        teardown frees."""
        owner = self._registry.get(namespace)
        if owner is None:
            return RamWorkTeardownResult(
                outcome=RamWorkOutcome.REFUSED,
                limitation=RamWorkLimitation.OWNER_ABSENT,
                freed_bytes=0,
                attempts_cancelled=0,
                waiters_notified=0,
                http_status=ram_work_http_status(RamWorkLimitation.OWNER_ABSENT),
            )
        okey = owner.namespace.lineage_key
        tasks: list[asyncio.Task[None]] = []
        task_las: list[_LiveAttempt] = []
        with self._registry._lock:
            ow = self._owners.get(okey)
            if ow is None:
                # No work plane for this live store owner:
                # the session teardown STILL releases the
                # store owner in this same critical section
                # (the atomic session-teardown contract);
                # freed_bytes reports only what THIS
                # teardown released.
                store_owner = self._registry._owners.get(okey)
                store_freed = store_owner._release_locked() if store_owner is owner else 0
                return RamWorkTeardownResult(
                    outcome=RamWorkOutcome.TEARDOWN,
                    limitation=None,
                    freed_bytes=store_freed,
                    attempts_cancelled=0,
                    waiters_notified=0,
                    http_status=None,
                )
            if ow.fenced:
                return RamWorkTeardownResult(
                    outcome=RamWorkOutcome.REFUSED,
                    limitation=RamWorkLimitation.OWNER_TORN_DOWN,
                    freed_bytes=0,
                    attempts_cancelled=0,
                    waiters_notified=0,
                    http_status=ram_work_http_status(RamWorkLimitation.OWNER_TORN_DOWN),
                )
            ow.fenced = True
            # The complete work release of THIS teardown is
            # this owner's work charge AT FENCE TIME (every
            # claimed reservation, live attempt and retained
            # terminal metadata); the drain's finalizations
            # commit part of that release to the process
            # counter while draining, the residual is
            # committed out in the final section below.
            work_at_fence = ow.bytes
            self._queue = deque(p for p in self._queue if p[0] != okey)
            for la in list(ow.live.values()):
                if la.task is None:
                    self._finalize_attempt_locked(
                        owner,
                        ow,
                        la,
                        RamWorkOutcome.CANCELLED,
                        RamWorkLimitation.OWNER_TORN_DOWN,
                        None,
                    )
                else:
                    tasks.append(la.task)
                    task_las.append(la)
                    la.task.cancel()
        # The drain (the cancel-AND-await law).  If THIS
        # teardown task is cancelled while awaiting, the fence
        # stays set and the loop re-awaits the (now
        # cancelled) child tasks until the drain genuinely
        # completes, so the atomic release below never runs
        # under live work and the fence never outlives the
        # drain.
        cancelled = False
        while True:
            try:
                if tasks:
                    await asyncio.gather(*tasks, return_exceptions=True)
                break
            except asyncio.CancelledError:
                cancelled = True
        with self._registry._lock:
            # The deterministic scheduling boundary: a
            # dispatch task cancelled before it ever executed
            # its first step never ran its in-task finalizer;
            # the owner finalizes it exactly once here (zero
            # actual invocations, the typed terminal re-served
            # to its waiters) so the drain genuinely completes
            # before the atomic release.
            for la in task_las:
                self._finalize_unrun_task_locked(
                    owner, ow, la, okey, RamWorkLimitation.OWNER_TORN_DOWN
                )
            # The ATOMIC composition: the store owner and the
            # work plane are released in the SAME critical
            # section (the drain guarantees no live work
            # remains), so no same-epoch reset window can
            # open between them.
            store_owner = self._registry._owners.get(okey)
            if store_owner is owner and self._owners.get(okey) is ow:
                store_freed = store_owner._release_locked()
                residual = ow.bytes
                if residual:
                    self._registry._commit_process_delta(-residual)
                self._owners.pop(okey, None)
                # The COMPLETE occupancy released by THIS
                # teardown: the work charge at fence time (the
                # drain already committed its finalization
                # deltas, the residual was committed out
                # above) plus the store release; prior normal
                # completions are not teardown frees.
                freed = store_freed + work_at_fence
            else:
                # Defensive (unreachable: the work fence
                # refuses the synchronous teardown while the
                # plane is fenced): the store owner is already
                # gone, so only the work state is released.
                residual = ow.bytes
                if residual:
                    self._registry._commit_process_delta(-residual)
                self._owners.pop(okey, None)
                freed = work_at_fence
            ow.bytes = 0
            ow.live = {}
            ow.terminal = {}
            ow.payloads = {}
            notified = ow.notified
        if cancelled:
            raise asyncio.CancelledError
        return RamWorkTeardownResult(
            outcome=RamWorkOutcome.TEARDOWN,
            limitation=None,
            freed_bytes=freed,
            attempts_cancelled=len(tasks),
            waiters_notified=notified,
            http_status=None,
        )

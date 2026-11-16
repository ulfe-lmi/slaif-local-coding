"""Permanent 019-b matrix for the bounded async single-flight
and attempt ownership plane (contract
``docs/CACHE-RAM-WORK-CONTRACT.md``).

Initial coherent batch over the ACTUAL 019-a registry/owners:
the genuine 018-p bootstrap composed through the ACTUAL 018-t
``derive_root_region_admission`` into a registered 019 owner,
the ONE process-wide leader over simultaneous identical misses
(ONE shared operation, the shared immutable payload, the later
same-key RAM-only hit) and the single-waiter cancellation law
(a cancelled follower detaches itself without cancelling the
surviving waiters' shared work).

The injected seam is synthetic: these cases prove prepared-work
orchestration only (actual compiler / tokenizer semantic
validation is 021).  The work plane stays inert.
"""

from __future__ import annotations

import asyncio
from asyncio import Task
from collections.abc import Callable, Coroutine
from typing import Any

import pytest
from pydantic import ValidationError

from slaif_local_coding.constitution.bundles.bundle_admission_models import (
    AdmissionMode,
)
from slaif_local_coding.constitution.bundles.causal_history_models import (
    CAUSAL_ROOT_FACT,
)
from slaif_local_coding.constitution.bundles.ram_state import (
    RamStateInputError,
    RamStateOwnerRegistry,
    _charge_object,
)
from slaif_local_coding.constitution.bundles.ram_state_models import (
    RamStateBounds,
    RamStateLimitation,
    RamStateOutcome,
)
from slaif_local_coding.constitution.bundles.ram_work import (
    RamWorkSeamError,
    WorkSeam,
    _LiveAttempt,
)
from slaif_local_coding.constitution.bundles.ram_work_models import (
    RAM_WORK_MAX_OUTPUT_BYTES_DEFAULT,
    RAM_WORK_MAX_PENDING_DISTINCT_KEYS_DEFAULT,
    RAM_WORK_MAX_WAITERS_PER_KEY_DEFAULT,
    RAM_WORK_MAX_WORK_SECONDS_DEFAULT,
    RAM_WORK_TASK_RESERVATION_BYTES,
    RAM_WORK_TERMINAL_RESERVATION_BYTES,
    RamWorkAttempt,
    RamWorkAttemptState,
    RamWorkBounds,
    RamWorkLimitation,
    RamWorkOutcome,
    RamWorkSeamReason,
    ram_work_bounds_shape_ok,
)
from slaif_local_coding.constitution.bundles.root_lineage_models import (
    RootLineageOutcome,
)
from slaif_local_coding.constitution.bundles.root_region_admission import (
    derive_root_region_admission,
)
from slaif_local_coding.constitution.bundles.root_region_admission_result_models import (
    RootRegionAdmissionOutcome,
    RootRegionAdmissionResult,
)
from slaif_local_coding.constitution.bundles.root_region_lineage_models import (
    RootRegionLineageNamespace,
    RootRegionLineageState,
)
from tests.test_bundle_ram_state import ROOT_AB, _ready_t, _root_key
from tests.test_causal_history import ENDPOINTS, MODES, read_request
from tests.test_root_region_lineage import (
    A_TEXT,
    B_TEXT,
    _host_io_facilities,
    r_bootstrap,
    r_issue,
    r_observe,
)

PAYLOAD = b"prepared-019b"

A2_TEXT = "Synthetic nonroot A v2.\n"


def _work_registry(
    bounds: RamWorkBounds | None = None,
) -> RamStateOwnerRegistry:
    """A registry with the 019-b work plane explicitly enabled
    (the 019-a default work-disabled behavior is unchanged)."""
    registry = RamStateOwnerRegistry(work_bounds=bounds if bounds is not None else RamWorkBounds())
    assert registry.work is not None
    return registry


class _PeakObservingRegistry(RamStateOwnerRegistry):
    """Test observer registry (test scope only; no product
    instrumentation): records the process total after every
    ``_commit_process_delta`` of ITS OWN instances (class-
    level record keyed by instance identity; ``__slots__ = ()``
    keeps the instance size -- and therefore the charged
    registry shell -- identical to the base class), so a test
    can read the ACTUAL maximum charged total across a whole
    operation (the true peak: the publication fence charges
    the prepared payload AFTER seam execution, while the task
    / waiter / terminal reservations still coexist)."""

    __slots__ = ()

    _peak_totals: dict[int, list[int]] = {}

    def __init__(
        self,
        bounds: RamStateBounds | None = None,
        work_bounds: object = None,
    ) -> None:
        # Register BEFORE super().__init__: the base
        # constructor already commits the work-plane shell
        # charge through this observer's override.
        _PeakObservingRegistry._peak_totals[id(self)] = []
        super().__init__(bounds=bounds, work_bounds=work_bounds)

    def _commit_process_delta(self, delta: int) -> None:
        super()._commit_process_delta(delta)
        _PeakObservingRegistry._peak_totals[id(self)].append(self.process_owned_bytes)

    @property
    def peak_totals(self) -> list[int]:
        return _PeakObservingRegistry._peak_totals[id(self)]


def make_seam(gate: asyncio.Event, calls: list[int]) -> WorkSeam:
    """The bounded synthetic work seam: one append per actual
    invocation, a deterministic gate before the bounded
    prepared output."""

    async def seam() -> bytes:
        calls.append(1)
        await gate.wait()
        return PAYLOAD

    return seam


async def _until(predicate: Callable[[], bool], turns: int = 1000) -> None:
    """A deterministic event-loop barrier: yield real turns
    (no wall-clock timing) until the predicate holds."""
    for _ in range(turns):
        if predicate():
            return
        await asyncio.sleep(0)
    assert predicate(), "deterministic barrier did not settle"


@pytest.mark.parametrize("mode", MODES)
async def test_a_concurrent_identical_miss_one_leader_shared_hit(mode: AdmissionMode) -> None:
    """Simultaneous identical misses join ONE shared operation:
    exactly ONE leader invocation, the shared immutable payload
    re-served to the joining request, the mandatory terminal
    record retained and charged, and the later same-key demand a
    RAM-only hit with zero new invocation."""
    ns, s0, result0 = _ready_t(mode, f"ram019w-a-{mode.value}")
    key = _root_key(result0)
    registry = _work_registry()
    work = registry.work
    assert work is not None
    owner = registry.acquire(ns)
    a0 = owner.admit(s0, result0, ns, expected_revision=0)
    assert a0.outcome is RamStateOutcome.ADMITTED
    baseline = registry.process_owned_bytes
    okey = owner.namespace.lineage_key

    gate = asyncio.Event()
    calls: list[int] = []
    seam = make_seam(gate, calls)

    def leader_dispatched() -> bool:
        ow = work._owners.get(okey)
        if ow is None:
            return False
        la = ow.live.get(key)
        return la is not None and la.task is not None and len(la.waiters) == 2

    first = asyncio.create_task(work.resolve(ns, key, seam))
    second = asyncio.create_task(work.resolve(ns, key, seam))
    await _until(leader_dispatched)
    gate.set()
    r_first, r_second = await asyncio.gather(first, second)

    assert {r_first.outcome, r_second.outcome} == {
        RamWorkOutcome.COMPLETED,
        RamWorkOutcome.JOINED,
    }
    if r_first.outcome is RamWorkOutcome.COMPLETED:
        lead, fol = r_first, r_second
    else:
        lead, fol = r_second, r_first
    assert lead.invocations == 1
    assert lead.attempt_invocations == 1
    assert fol.invocations == 0
    assert fol.attempt_invocations == 1
    assert lead.payload is not None
    assert fol.payload is lead.payload  # the SAME retained immutable payload
    assert lead.payload.data == PAYLOAD
    assert lead.payload.content_key == key
    assert lead.epoch == owner.epoch

    assert len(calls) == 1  # exactly ONE actual leader invocation
    ow = work._owners[okey]
    assert ow.live == {}
    record = ow.terminal[(owner.epoch, key)]
    assert record is not None
    assert record.state is RamWorkAttemptState.TERMINAL
    assert record.outcome is RamWorkOutcome.COMPLETED
    assert record.invocations == 1
    assert record.payload is lead.payload
    # The retained payload plus terminal metadata is charged.
    assert owner.owned_bytes + work.session_bytes(okey) > 0
    assert registry.process_owned_bytes > baseline

    # The later same-key demand is a RAM-only hit (zero new invocation).
    hit = await work.resolve(ns, key, seam)
    assert hit.outcome is RamWorkOutcome.HIT
    assert hit.invocations == 0
    assert hit.attempt_invocations == 0
    assert hit.payload is lead.payload
    assert len(calls) == 1


@pytest.mark.parametrize("mode", MODES)
async def test_b_cancelled_follower_surviving_waiters_complete(mode: AdmissionMode) -> None:
    """A single cancelled follower detaches only itself: the
    shared work of the surviving claimant/waiter proceeds to the
    shared payload with exactly one invocation, and the later
    same-key demand stays a RAM-only hit."""
    ns, s0, result0 = _ready_t(mode, f"ram019w-b-{mode.value}")
    key = _root_key(result0)
    registry = _work_registry()
    work = registry.work
    assert work is not None
    owner = registry.acquire(ns)
    a0 = owner.admit(s0, result0, ns, expected_revision=0)
    assert a0.outcome is RamStateOutcome.ADMITTED
    okey = owner.namespace.lineage_key

    gate = asyncio.Event()
    calls: list[int] = []
    seam = make_seam(gate, calls)

    def waiter_count() -> int:
        ow = work._owners.get(okey)
        if ow is None:
            return 0
        la = ow.live.get(key)
        return len(la.waiters) if la is not None else 0

    leader = asyncio.create_task(work.resolve(ns, key, seam))
    survivor = asyncio.create_task(work.resolve(ns, key, seam))
    cancelled = asyncio.create_task(work.resolve(ns, key, seam))
    await _until(lambda: waiter_count() == 3)
    cancelled.cancel()
    with pytest.raises(asyncio.CancelledError):
        await cancelled
    # The cancellation detached one waiter only.
    await _until(lambda: waiter_count() == 2)
    gate.set()
    r_lead, r_surv = await asyncio.gather(leader, survivor)

    assert {r_lead.outcome, r_surv.outcome} == {
        RamWorkOutcome.COMPLETED,
        RamWorkOutcome.JOINED,
    }
    if r_lead.outcome is RamWorkOutcome.COMPLETED:
        lead, fol = r_lead, r_surv
    else:
        lead, fol = r_surv, r_lead
    assert lead.invocations == 1
    assert fol.invocations == 0
    assert lead.payload is not None
    assert fol.payload is lead.payload
    assert lead.payload.data == PAYLOAD
    assert len(calls) == 1

    hit = await work.resolve(ns, key, seam)
    assert hit.outcome is RamWorkOutcome.HIT
    assert hit.invocations == 0
    assert hit.payload is lead.payload
    assert len(calls) == 1


# --- C. Pre-claim capacity fences ----------------------------------


@pytest.mark.parametrize("mode", MODES)
async def test_c_pending_keys_over_bound_pre_claim_refusal(mode: AdmissionMode) -> None:
    """With the pending distinct-key bound at ONE, a second
    DISTINCT current key refuses PRE-CLAIM (fixed 503, zero
    invocation, no attempt, no charge change) while the active
    leader's key stays admitted; the refusal retains nothing, so
    the second key claims fresh after the leader completes.
    (Root + FILE keys over the first endpoint shape; the endpoint
    does not affect the work-plane binding asserted here.)"""
    endpoint = ENDPOINTS[0]
    ns, s0 = r_bootstrap(mode, f"ram019w-c-{mode.value}", root_body=ROOT_AB)
    result0 = derive_root_region_admission(s0, ns)
    assert result0.outcome is RootRegionAdmissionOutcome.READY
    registry = RamStateOwnerRegistry(work_bounds=RamWorkBounds(max_pending_distinct_keys=1))
    work = registry.work
    assert work is not None
    owner = registry.acquire(ns)
    a0 = owner.admit(s0, result0, ns, expected_revision=0)
    assert a0.outcome is RamStateOutcome.ADMITTED
    # Genuine singleton A read: a second ACTUAL current key.
    t1 = r_issue(s0, ns, "b1", endpoint, (CAUSAL_ROOT_FACT,), "cat A.md")
    assert t1.outcome is RootLineageOutcome.ACCEPTED, t1.diagnostics
    t2 = r_observe(t1.state, ns, (read_request(endpoint, "b1", A_TEXT, "cat A.md"),))
    assert t2.outcome is RootLineageOutcome.ACCEPTED, t2.diagnostics
    s1 = t2.state
    result1 = derive_root_region_admission(s1, ns)
    assert result1.outcome is RootRegionAdmissionOutcome.READY, result1.diagnostics
    adm1 = result1.admission
    assert adm1 is not None
    key_a = next(row.content_keys[0] for row in adm1.path_associations if row.path == "A.md")
    a1 = owner.admit(s1, result1, ns, expected_revision=1)
    assert a1.outcome is RamStateOutcome.ADMITTED
    root_key = _root_key(result1)
    okey = owner.namespace.lineage_key

    gate = asyncio.Event()
    calls: list[int] = []
    seam = make_seam(gate, calls)

    leader = asyncio.create_task(work.resolve(ns, root_key, seam))
    await _until(lambda: work._active_key is not None and len(calls) == 1)
    # The leader's own claim/dispatch charges are legitimately
    # committed by now; the REFUSAL below must change nothing
    # against this pre-refusal baseline.
    proc_at_refusal = registry.process_owned_bytes
    sess_at_refusal = owner.owned_bytes + work.session_bytes(okey)
    refused = await work.resolve(ns, key_a, seam)
    assert refused.outcome is RamWorkOutcome.REFUSED
    assert refused.limitation is RamWorkLimitation.PENDING_KEYS_OVER_BOUND
    assert refused.http_status == 503
    assert refused.invocations == 0
    assert len(calls) == 1  # the refused claim did NOT invoke the seam
    ow = work._owners[okey]
    assert key_a not in ow.live
    assert (owner.epoch, key_a) not in ow.terminal
    # Nothing was retained or charged by the refusal.
    assert registry.process_owned_bytes == proc_at_refusal
    assert owner.owned_bytes + work.session_bytes(okey) == sess_at_refusal

    gate.set()
    r_lead = await leader
    assert r_lead.outcome is RamWorkOutcome.COMPLETED
    # The refusal retained nothing: the second key claims fresh now.
    calls.clear()
    r_a = await work.resolve(ns, key_a, seam)
    assert r_a.outcome is RamWorkOutcome.COMPLETED
    assert r_a.invocations == 1
    assert len(calls) == 1
    assert r_a.payload is not None
    assert r_a.payload.content_key == key_a


@pytest.mark.parametrize("mode", MODES)
async def test_d_waiters_over_bound_refused_join_exact_preservation(mode: AdmissionMode) -> None:
    """A same-key join beyond the waiter bound refuses with the
    fixed 503 and mutates NOTHING: the process counter and the
    owner's charged session sum stay byte-exact, the existing
    two waiters complete the shared payload with one invocation."""
    ns, s0, result0 = _ready_t(mode, f"ram019w-d-{mode.value}")
    key = _root_key(result0)
    registry = RamStateOwnerRegistry(work_bounds=RamWorkBounds(max_waiters_per_key=2))
    work = registry.work
    assert work is not None
    owner = registry.acquire(ns)
    a0 = owner.admit(s0, result0, ns, expected_revision=0)
    assert a0.outcome is RamStateOutcome.ADMITTED
    okey = owner.namespace.lineage_key

    def waiter_count() -> int:
        ow = work._owners.get(okey)
        if ow is None:
            return 0
        la = ow.live.get(key)
        return len(la.waiters) if la is not None else 0

    gate = asyncio.Event()
    calls: list[int] = []
    seam = make_seam(gate, calls)
    first = asyncio.create_task(work.resolve(ns, key, seam))
    await _until(lambda: work._active_key is not None)
    second = asyncio.create_task(work.resolve(ns, key, seam))
    await _until(lambda: waiter_count() == 2)
    proc_mid = registry.process_owned_bytes
    sess_mid = owner.owned_bytes + work.session_bytes(okey)

    refused = await work.resolve(ns, key, seam)
    assert refused.outcome is RamWorkOutcome.REFUSED
    assert refused.limitation is RamWorkLimitation.WAITERS_PER_KEY_OVER_BOUND
    assert refused.http_status == 503
    assert refused.invocations == 0
    assert len(calls) == 1
    # Exact preservation: the refused join retained no charge.
    assert registry.process_owned_bytes == proc_mid
    assert owner.owned_bytes + work.session_bytes(okey) == sess_mid
    assert waiter_count() == 2

    gate.set()
    r1, r2 = await asyncio.gather(first, second)
    assert {r1.outcome, r2.outcome} == {RamWorkOutcome.COMPLETED, RamWorkOutcome.JOINED}
    assert len(calls) == 1


@pytest.mark.parametrize("mode", MODES)
async def test_e_session_capacity_refused_first_claim_retains_nothing(mode: AdmissionMode) -> None:
    """An owner whose session ceiling is EXACTLY its store charge
    leaves zero room for work: the first work claim refuses with
    the fixed 503 capacity contract, the freshly created work
    state is abandoned WITHOUT registration (no owner-work state,
    zero work charge, process counter untouched), the store owner
    stays intact, and a larger-ceiling registry admits the same
    key with a genuine invocation."""
    ns, s0, result0 = _ready_t(mode, f"ram019w-e-{mode.value}")
    key = _root_key(result0)
    # Measure the ACTUAL store charge of this record set first.
    probe = RamStateOwnerRegistry()
    probe_owner = probe.acquire(ns)
    pa = probe_owner.admit(s0, result0, ns, expected_revision=0)
    assert pa.outcome is RamStateOutcome.ADMITTED
    store_charge = probe_owner.owned_bytes

    registry = _work_registry()
    work = registry.work
    assert work is not None
    owner = registry.new_owner(ns, session_max_owned_bytes=store_charge)
    a0 = owner.admit(s0, result0, ns, expected_revision=0)
    assert a0.outcome is RamStateOutcome.ADMITTED
    assert owner.owned_bytes == store_charge
    okey = owner.namespace.lineage_key
    proc_before = registry.process_owned_bytes

    gate = asyncio.Event()
    calls: list[int] = []
    seam = make_seam(gate, calls)
    refused = await work.resolve(ns, key, seam)
    assert refused.outcome is RamWorkOutcome.REFUSED
    assert refused.limitation is RamStateLimitation.SESSION_OWNED_BYTES_OVER_BOUND
    assert refused.http_status == 503
    assert refused.invocations == 0
    assert len(calls) == 0
    # The created-then-refused work state was abandoned: nothing
    # registered, nothing charged, nothing retained.
    assert work._owners.get(okey) is None
    assert work.session_bytes(okey) == 0
    assert registry.process_owned_bytes == proc_before
    # The store owner is untouched.
    hit = owner.lookup(key, ns)
    assert hit.outcome is RamStateOutcome.FOUND

    # The same key admits on a registry with room.
    registry2 = _work_registry()
    work2 = registry2.work
    assert work2 is not None
    owner2 = registry2.new_owner(ns, session_max_owned_bytes=store_charge + 1_048_576)
    a2 = owner2.admit(s0, result0, ns, expected_revision=0)
    assert a2.outcome is RamStateOutcome.ADMITTED
    gate.set()
    r2 = await work2.resolve(ns, key, seam)
    assert r2.outcome is RamWorkOutcome.COMPLETED
    assert r2.invocations == 1
    assert len(calls) == 1


# --- F. Bounds model, registry integration, terminal reservation ---


def test_f_ram_work_bounds_model() -> None:
    """The positive non-bool work bounds: defaults, stricter legal
    positives, and the closed raw fences (bool / float / string /
    zero / over-hard all refuse)."""
    b = RamWorkBounds()
    assert b.max_pending_distinct_keys == RAM_WORK_MAX_PENDING_DISTINCT_KEYS_DEFAULT
    assert b.max_waiters_per_key == RAM_WORK_MAX_WAITERS_PER_KEY_DEFAULT
    assert b.max_output_bytes == RAM_WORK_MAX_OUTPUT_BYTES_DEFAULT
    assert b.max_work_seconds == RAM_WORK_MAX_WORK_SECONDS_DEFAULT
    strict = RamWorkBounds(
        max_pending_distinct_keys=1,
        max_waiters_per_key=1,
        max_output_bytes=8,
        max_work_seconds=1,
    )
    assert strict.max_work_seconds == 1.0
    for bad in (True, 1.5, "8", 0, -1, RAM_WORK_MAX_PENDING_DISTINCT_KEYS_DEFAULT + 4096):
        with pytest.raises(ValidationError):
            RamWorkBounds(max_pending_distinct_keys=bad)  # type: ignore[arg-type]
    for bad in (True, "8", 0, 1025):
        with pytest.raises(ValidationError):
            RamWorkBounds(max_waiters_per_key=bad)  # type: ignore[arg-type]
    for bad in (True, 8.5, "8", 0, 67_108_865):
        with pytest.raises(ValidationError):
            RamWorkBounds(max_output_bytes=bad)  # type: ignore[arg-type]
    for bad in (True, "30", 0.0, -1.0, 600.5):
        with pytest.raises(ValidationError):
            RamWorkBounds(max_work_seconds=bad)  # type: ignore[arg-type]
    # The original-class closed fence: original instances pass,
    # shadow subclasses and bypass-constructed malformed copies
    # do not.
    assert ram_work_bounds_shape_ok(b)
    assert ram_work_bounds_shape_ok(strict)

    class _Shadow(RamWorkBounds):
        pass

    assert not ram_work_bounds_shape_ok(_Shadow())
    bad_constructed = RamWorkBounds.model_construct(max_pending_distinct_keys=-5)
    assert not ram_work_bounds_shape_ok(bad_constructed)


def test_f2_work_registry_integration() -> None:
    """The opt-in work plane: the combined shell base is charged
    into the process occupancy (the coordinator shell commits on
    top of the registry shell BEFORE any owner allocation is
    ceiling-checked), the work-disabled default is unchanged, and
    malformed work bounds refuse at the registry boundary with the
    fixed input error."""
    plain = RamStateOwnerRegistry().process_owned_bytes
    with_work = RamStateOwnerRegistry(work_bounds=RamWorkBounds()).process_owned_bytes
    assert with_work > plain
    assert RamStateOwnerRegistry(work_bounds=RamWorkBounds()).work is not None
    assert RamStateOwnerRegistry().work is None
    with pytest.raises(RamStateInputError):
        RamStateOwnerRegistry(work_bounds="nope")
    with pytest.raises(RamStateInputError):

        class _Shadow2(RamWorkBounds):
            pass

        RamStateOwnerRegistry(work_bounds=_Shadow2())
    bad2 = RamWorkBounds.model_construct(max_waiters_per_key=True)
    with pytest.raises(RamStateInputError):
        RamStateOwnerRegistry(work_bounds=bad2)


def test_f3_terminal_reservation_upper_bound() -> None:
    """The closed terminal reservation is an UPPER BOUND on the
    ACTUAL measured charge of the worst-case retained terminal
    record (longest closed key, largest legal epoch, every field
    set, one invocation)."""
    rec = RamWorkAttempt(
        content_key="a" * 64,
        epoch=2**63,
        state=RamWorkAttemptState.TERMINAL,
        outcome=RamWorkOutcome.FAILED,
        limitation=RamWorkLimitation.ALL_WAITERS_DEPARTED,
        invocations=1,
    )
    assert _charge_object(rec, set()) <= RAM_WORK_TERMINAL_RESERVATION_BYTES


# --- G/H/I. Cancellation lifecycle ---------------------------------


@pytest.mark.parametrize("mode", MODES)
async def test_g_all_waiters_departed_after_dispatch(mode: AdmissionMode) -> None:
    """The last (claimant) waiter cancels after dispatch: the
    owned work is cancelled AND awaited before the cancellation
    re-raises, the terminal CANCELLED record is retained with the
    honest first-step invocation count, and the later same-key
    demand re-serves the SAME fixed typed failure with zero new
    invocations."""
    ns, s0, result0 = _ready_t(mode, f"ram019w-g-{mode.value}")
    key = _root_key(result0)
    registry = _work_registry()
    work = registry.work
    assert work is not None
    owner = registry.acquire(ns)
    a0 = owner.admit(s0, result0, ns, expected_revision=0)
    assert a0.outcome is RamStateOutcome.ADMITTED
    okey = owner.namespace.lineage_key

    gate = asyncio.Event()
    calls: list[int] = []
    seam = make_seam(gate, calls)
    claimant = asyncio.create_task(work.resolve(ns, key, seam))
    await _until(lambda: work._active_key is not None and len(calls) == 1)
    claimant.cancel()
    with pytest.raises(asyncio.CancelledError):
        await claimant

    ow = work._owners[okey]
    assert ow.live == {}
    record = ow.terminal[(owner.epoch, key)]
    assert record is not None
    assert record.state is RamWorkAttemptState.TERMINAL
    assert record.outcome is RamWorkOutcome.CANCELLED
    assert record.limitation is RamWorkLimitation.ALL_WAITERS_DEPARTED
    assert record.invocations == 1  # honest: the dispatch ran its first step

    again = await work.resolve(ns, key, seam)
    assert again.outcome is RamWorkOutcome.FAILED
    assert again.limitation is RamWorkLimitation.ALL_WAITERS_DEPARTED
    assert again.http_status == 503
    assert again.invocations == 0
    assert again.attempt_invocations == 1
    assert len(calls) == 1  # no retry


@pytest.mark.parametrize("mode", MODES)
async def test_h_queued_claim_all_waiters_departed_before_dispatch(mode: AdmissionMode) -> None:
    """A QUEUED claimed-but-not-dispatched attempt whose sole
    waiter cancels: the attempt terminates with ZERO actual
    invocations (the claimed reservation is closed, never
    released-and-retried), the unrelated active leader still
    completes, and the later same-key demand re-serves the
    terminal failure."""
    endpoint = ENDPOINTS[0]
    ns, s0 = r_bootstrap(mode, f"ram019w-h-{mode.value}", root_body=ROOT_AB)
    result0 = derive_root_region_admission(s0, ns)
    assert result0.outcome is RootRegionAdmissionOutcome.READY
    registry = _work_registry()
    work = registry.work
    assert work is not None
    owner = registry.acquire(ns)
    a0 = owner.admit(s0, result0, ns, expected_revision=0)
    assert a0.outcome is RamStateOutcome.ADMITTED
    t1 = r_issue(s0, ns, "b1", endpoint, (CAUSAL_ROOT_FACT,), "cat A.md")
    assert t1.outcome is RootLineageOutcome.ACCEPTED, t1.diagnostics
    t2 = r_observe(t1.state, ns, (read_request(endpoint, "b1", A_TEXT, "cat A.md"),))
    assert t2.outcome is RootLineageOutcome.ACCEPTED, t2.diagnostics
    s1 = t2.state
    result1 = derive_root_region_admission(s1, ns)
    assert result1.outcome is RootRegionAdmissionOutcome.READY, result1.diagnostics
    adm1 = result1.admission
    assert adm1 is not None
    key_a = next(row.content_keys[0] for row in adm1.path_associations if row.path == "A.md")
    a1 = owner.admit(s1, result1, ns, expected_revision=1)
    assert a1.outcome is RamStateOutcome.ADMITTED
    root_key = _root_key(result1)
    okey = owner.namespace.lineage_key

    gate = asyncio.Event()
    calls: list[int] = []
    seam = make_seam(gate, calls)
    leader = asyncio.create_task(work.resolve(ns, root_key, seam))
    await _until(lambda: work._active_key is not None and len(calls) == 1)
    queued = asyncio.create_task(work.resolve(ns, key_a, seam))
    await _until(lambda: work._owners.get(okey) is not None and key_a in work._owners[okey].live)
    queued.cancel()
    with pytest.raises(asyncio.CancelledError):
        await queued

    ow = work._owners[okey]
    assert key_a not in ow.live
    record = ow.terminal[(owner.epoch, key_a)]
    assert record is not None
    assert record.outcome is RamWorkOutcome.CANCELLED
    assert record.limitation is RamWorkLimitation.ALL_WAITERS_DEPARTED
    assert record.invocations == 0  # never dispatched
    assert root_key in ow.live  # the unrelated active leader is untouched

    gate.set()
    r_lead = await leader
    assert r_lead.outcome is RamWorkOutcome.COMPLETED
    assert len(calls) == 1

    again = await work.resolve(ns, key_a, seam)
    assert again.outcome is RamWorkOutcome.FAILED
    assert again.limitation is RamWorkLimitation.ALL_WAITERS_DEPARTED
    assert again.http_status == 503
    assert again.invocations == 0
    assert again.attempt_invocations == 0
    assert len(calls) == 1


@pytest.mark.parametrize("mode", MODES)
async def test_i_unstarted_dispatch_tasks_finalize_zero_invocations(
    mode: AdmissionMode, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The deterministic scheduling boundary: a dispatch task
    cancelled by the loop BEFORE it executed its first step never
    runs its in-task finalizer; while its claimant still waits the
    claimed attempt stays live (no silent release), and when the
    last waiter departs the owner finalizes it EXACTLY ONCE with
    zero actual invocations, clears the active slot and advances
    the queue (the queued key's dispatch is likewise closed), so
    no live attempt or active slot leaks."""
    endpoint = ENDPOINTS[0]
    ns, s0 = r_bootstrap(mode, f"ram019w-i-{mode.value}", root_body=ROOT_AB)
    result0 = derive_root_region_admission(s0, ns)
    assert result0.outcome is RootRegionAdmissionOutcome.READY
    registry = _work_registry()
    work = registry.work
    assert work is not None
    owner = registry.acquire(ns)
    a0 = owner.admit(s0, result0, ns, expected_revision=0)
    assert a0.outcome is RamStateOutcome.ADMITTED
    t1 = r_issue(s0, ns, "b1", endpoint, (CAUSAL_ROOT_FACT,), "cat A.md")
    assert t1.outcome is RootLineageOutcome.ACCEPTED, t1.diagnostics
    t2 = r_observe(t1.state, ns, (read_request(endpoint, "b1", A_TEXT, "cat A.md"),))
    assert t2.outcome is RootLineageOutcome.ACCEPTED, t2.diagnostics
    s1 = t2.state
    result1 = derive_root_region_admission(s1, ns)
    assert result1.outcome is RootRegionAdmissionOutcome.READY, result1.diagnostics
    adm1 = result1.admission
    assert adm1 is not None
    key_a = next(row.content_keys[0] for row in adm1.path_associations if row.path == "A.md")
    a1 = owner.admit(s1, result1, ns, expected_revision=1)
    assert a1.outcome is RamStateOutcome.ADMITTED
    root_key = _root_key(result1)
    okey = owner.namespace.lineage_key

    # Deterministic seam kill: cancel every dispatch task in the
    # pump's own turn, before its first step.
    loop = asyncio.get_running_loop()
    orig_create = loop.create_task

    def spy(coro: Coroutine[Any, Any, Any], **kwargs: Any) -> Task[Any]:
        task = orig_create(coro, **kwargs)
        code = getattr(coro, "cr_code", None)
        if code is not None and code.co_name == "_run_work":
            task.cancel()
        return task

    monkeypatch.setattr(loop, "create_task", spy)

    def live_la(key: str) -> _LiveAttempt | None:
        ow = work._owners.get(okey)
        return ow.live.get(key) if ow is not None else None

    def root_dispatched_done() -> bool:
        la = live_la(root_key)
        return la is not None and la.task is not None and la.task.done()

    def queued_dispatched_done() -> bool:
        la = live_la(key_a)
        return la is not None and la.task is not None and la.task.done()

    gate = asyncio.Event()
    calls: list[int] = []
    seam = make_seam(gate, calls)
    leader = asyncio.create_task(work.resolve(ns, root_key, seam))
    queued = asyncio.create_task(work.resolve(ns, key_a, seam))
    await _until(root_dispatched_done)
    # While the claimant still waits, the attempt remains live
    # (nothing else is entitled to finalize it).
    assert root_key in (work._owners[okey].live if work._owners.get(okey) is not None else {})
    leader.cancel()
    with pytest.raises(asyncio.CancelledError):
        await leader
    ow = work._owners[okey]
    assert root_key not in ow.live
    record = ow.terminal[(owner.epoch, root_key)]
    assert record is not None
    assert record.outcome is RamWorkOutcome.CANCELLED
    assert record.limitation is RamWorkLimitation.ALL_WAITERS_DEPARTED
    assert record.invocations == 0
    # The queue advanced: the active slot MOVED to the queued key
    # (whose dispatch was likewise cancelled pre-start by the spy).
    assert work._active_key == (okey, key_a)
    await _until(queued_dispatched_done)
    queued.cancel()
    with pytest.raises(asyncio.CancelledError):
        await queued
    assert key_a not in ow.live
    record_a = ow.terminal[(owner.epoch, key_a)]
    assert record_a is not None
    assert record_a.outcome is RamWorkOutcome.CANCELLED
    assert record_a.limitation is RamWorkLimitation.ALL_WAITERS_DEPARTED
    assert record_a.invocations == 0
    assert len(calls) == 0  # zero actual invocations end to end

    again = await work.resolve(ns, root_key, seam)
    assert again.outcome is RamWorkOutcome.FAILED
    assert again.limitation is RamWorkLimitation.ALL_WAITERS_DEPARTED
    assert again.invocations == 0
    assert len(calls) == 0


# --- J. Seam failure terminals -------------------------------------

_NOT_BYTES = "not-bytes"


@pytest.mark.parametrize("mode", MODES)
async def test_j1_exception_and_timeout_terminals(mode: AdmissionMode) -> None:
    """Unclassified seam exception and the closed time bound leave
    the terminal FAILED record (fixed 503, one honest invocation,
    no raw exception content) and the later same-key demand
    re-serves the SAME fixed typed failure with zero new
    invocations."""
    ns, s0, result0 = _ready_t(mode, f"ram019w-j1-{mode.value}")
    key = _root_key(result0)

    async def exc_seam() -> bytes:
        raise RuntimeError("synthetic")

    registry = _work_registry()
    work = registry.work
    assert work is not None
    owner = registry.acquire(ns)
    a0 = owner.admit(s0, result0, ns, expected_revision=0)
    assert a0.outcome is RamStateOutcome.ADMITTED
    okey = owner.namespace.lineage_key

    r1 = await work.resolve(ns, key, exc_seam)
    assert r1.outcome is RamWorkOutcome.FAILED
    assert r1.limitation is RamWorkLimitation.WORK_FAILED
    assert r1.http_status == 503
    assert r1.invocations == 1  # the claimant's own actual invocation
    assert r1.attempt_invocations == 1
    assert r1.payload is None
    record = work._owners[okey].terminal[(owner.epoch, key)]
    assert record is not None
    assert record.outcome is RamWorkOutcome.FAILED
    assert record.limitation is RamWorkLimitation.WORK_FAILED
    assert record.invocations == 1
    assert record.payload is None

    again = await work.resolve(ns, key, exc_seam)
    assert again.outcome is RamWorkOutcome.FAILED
    assert again.limitation is RamWorkLimitation.WORK_FAILED
    assert again.http_status == 503
    assert again.invocations == 0
    assert again.attempt_invocations == 1

    # The closed time bound: a seam that exceeds max_work_seconds.
    registry2 = _work_registry(RamWorkBounds(max_work_seconds=0.05))
    work2 = registry2.work
    assert work2 is not None
    owner2 = registry2.acquire(ns)
    a2 = owner2.admit(s0, result0, ns, expected_revision=0)
    assert a2.outcome is RamStateOutcome.ADMITTED
    okey2 = owner2.namespace.lineage_key

    async def slow_seam() -> bytes:
        await asyncio.sleep(10)
        return PAYLOAD

    r2 = await work2.resolve(ns, key, slow_seam)
    assert r2.outcome is RamWorkOutcome.FAILED
    assert r2.limitation is RamWorkLimitation.WORK_TIMEOUT
    assert r2.http_status == 503
    assert r2.attempt_invocations == 1
    record2 = work2._owners[okey2].terminal[(owner2.epoch, key)]
    assert record2 is not None
    assert record2.limitation is RamWorkLimitation.WORK_TIMEOUT

    again2 = await work2.resolve(ns, key, slow_seam)
    assert again2.outcome is RamWorkOutcome.FAILED
    assert again2.limitation is RamWorkLimitation.WORK_TIMEOUT
    assert again2.invocations == 0


@pytest.mark.parametrize("mode", MODES)
async def test_j2_output_shape_terminals(mode: AdmissionMode) -> None:
    """The bounded-output shape refusals at this inert boundary:
    non-bytes output and the typed seam invalid / truncated
    reasons (fixed 422), and the closed output-size bound
    (fixed 422) -- each terminal is retained and re-served, and
    the size bound is proven at its exact edge: the at-limit
    output is a COMPLETED retained payload, one byte over fails."""
    ns, s0, result0 = _ready_t(mode, f"ram019w-j2-{mode.value}")
    key = _root_key(result0)

    async def str_seam() -> bytes:
        return _NOT_BYTES  # type: ignore[return-value]

    async def invalid_seam() -> bytes:
        raise RamWorkSeamError(RamWorkSeamReason.INVALID)

    async def truncated_seam() -> bytes:
        raise RamWorkSeamError(RamWorkSeamReason.TRUNCATED)

    async def big_seam() -> bytes:
        return b"x" * 64

    for seam, limitation in (
        (str_seam, RamWorkLimitation.INVALID_OUTPUT),
        (invalid_seam, RamWorkLimitation.INVALID_OUTPUT),
        (truncated_seam, RamWorkLimitation.TRUNCATED_OUTPUT),
    ):
        registry = _work_registry()
        work = registry.work
        assert work is not None
        owner = registry.acquire(ns)
        a0 = owner.admit(s0, result0, ns, expected_revision=0)
        assert a0.outcome is RamStateOutcome.ADMITTED
        r = await work.resolve(ns, key, seam)
        assert r.outcome is RamWorkOutcome.FAILED, (seam, r)
        assert r.limitation is limitation
        assert r.http_status == 422
        assert r.invocations == 1  # the claimant's own actual invocation
        assert r.attempt_invocations == 1
        assert r.payload is None
        again = await work.resolve(ns, key, seam)
        assert again.outcome is RamWorkOutcome.FAILED
        assert again.limitation is limitation
        assert again.invocations == 0

    registry = _work_registry(RamWorkBounds(max_output_bytes=8))
    work = registry.work
    assert work is not None
    owner = registry.acquire(ns)
    a0 = owner.admit(s0, result0, ns, expected_revision=0)
    assert a0.outcome is RamStateOutcome.ADMITTED
    r = await work.resolve(ns, key, big_seam)
    assert r.outcome is RamWorkOutcome.FAILED
    assert r.limitation is RamWorkLimitation.OUTPUT_OVER_BOUND
    assert r.http_status == 422
    again = await work.resolve(ns, key, big_seam)
    assert again.outcome is RamWorkOutcome.FAILED
    assert again.limitation is RamWorkLimitation.OUTPUT_OVER_BOUND
    assert again.invocations == 0

    # The closed output-size bound at its EXACT edge: the
    # at-limit output is a COMPLETED retained payload (the later
    # same-key demand a HIT), and one byte over is the fixed 422
    # OUTPUT_OVER_BOUND terminal -- proven on a FRESH owner,
    # because the completed at-limit payload would otherwise
    # short-circuit the same key to a HIT.
    registry8 = _work_registry(RamWorkBounds(max_output_bytes=8))
    work8 = registry8.work
    assert work8 is not None
    owner8 = registry8.acquire(ns)
    assert owner8.admit(s0, result0, ns, expected_revision=0).outcome is RamStateOutcome.ADMITTED

    async def exact_seam() -> bytes:
        return b"y" * 8

    r8 = await work8.resolve(ns, key, exact_seam)
    assert r8.outcome is RamWorkOutcome.COMPLETED
    assert r8.invocations == 1
    assert r8.payload is not None
    assert r8.payload.content_key == key
    assert r8.payload.data == b"y" * 8
    hit8 = await work8.resolve(ns, key, exact_seam)
    assert hit8.outcome is RamWorkOutcome.HIT
    assert hit8.payload is r8.payload
    assert hit8.invocations == 0

    registry9 = _work_registry(RamWorkBounds(max_output_bytes=8))
    work9 = registry9.work
    assert work9 is not None
    owner9 = registry9.acquire(ns)
    assert owner9.admit(s0, result0, ns, expected_revision=0).outcome is RamStateOutcome.ADMITTED

    async def over9_seam() -> bytes:
        return b"z" * 9

    r9 = await work9.resolve(ns, key, over9_seam)
    assert r9.outcome is RamWorkOutcome.FAILED
    assert r9.limitation is RamWorkLimitation.OUTPUT_OVER_BOUND
    assert r9.http_status == 422
    assert r9.payload is None
    assert r9.invocations == 1
    again9 = await work9.resolve(ns, key, over9_seam)
    assert again9.outcome is RamWorkOutcome.FAILED
    assert again9.limitation is RamWorkLimitation.OUTPUT_OVER_BOUND
    assert again9.invocations == 0


@pytest.mark.parametrize("mode", MODES)
async def test_j3_terminal_never_hit_unrelated_key_progresses(mode: AdmissionMode) -> None:
    """A terminal failure of one key never counts as a hit and
    never poisons an unrelated key: the failed root key re-serves
    its fixed typed failure while the genuinely distinct FILE key
    completes its OWN attempt, and its later demand is a HIT."""
    endpoint = ENDPOINTS[0]
    ns, s0 = r_bootstrap(mode, f"ram019w-j3-{mode.value}", root_body=ROOT_AB)
    result0 = derive_root_region_admission(s0, ns)
    assert result0.outcome is RootRegionAdmissionOutcome.READY
    registry = _work_registry()
    work = registry.work
    assert work is not None
    owner = registry.acquire(ns)
    a0 = owner.admit(s0, result0, ns, expected_revision=0)
    assert a0.outcome is RamStateOutcome.ADMITTED
    t1 = r_issue(s0, ns, "b1", endpoint, (CAUSAL_ROOT_FACT,), "cat A.md")
    assert t1.outcome is RootLineageOutcome.ACCEPTED, t1.diagnostics
    t2 = r_observe(t1.state, ns, (read_request(endpoint, "b1", A_TEXT, "cat A.md"),))
    assert t2.outcome is RootLineageOutcome.ACCEPTED, t2.diagnostics
    s1 = t2.state
    result1 = derive_root_region_admission(s1, ns)
    assert result1.outcome is RootRegionAdmissionOutcome.READY, result1.diagnostics
    adm1 = result1.admission
    assert adm1 is not None
    key_a = next(row.content_keys[0] for row in adm1.path_associations if row.path == "A.md")
    a1 = owner.admit(s1, result1, ns, expected_revision=1)
    assert a1.outcome is RamStateOutcome.ADMITTED
    root_key = _root_key(result1)
    okey = owner.namespace.lineage_key

    async def exc_seam() -> bytes:
        raise RuntimeError("synthetic")

    failed = await work.resolve(ns, root_key, exc_seam)
    assert failed.outcome is RamWorkOutcome.FAILED
    assert failed.limitation is RamWorkLimitation.WORK_FAILED
    assert failed.payload is None

    # The unrelated key completes its own attempt.
    async def ok_seam() -> bytes:
        return PAYLOAD

    r_a = await work.resolve(ns, key_a, ok_seam)
    assert r_a.outcome is RamWorkOutcome.COMPLETED
    assert r_a.invocations == 1
    assert r_a.payload is not None
    assert r_a.payload.content_key == key_a

    # The terminal record is never a hit; the unrelated key is.
    again = await work.resolve(ns, root_key, exc_seam)
    assert again.outcome is RamWorkOutcome.FAILED
    assert again.limitation is RamWorkLimitation.WORK_FAILED
    assert again.invocations == 0
    hit = await work.resolve(ns, key_a, ok_seam)
    assert hit.outcome is RamWorkOutcome.HIT
    assert hit.payload is r_a.payload
    # Both terminal / payload records are retained and charged.
    ow = work._owners[okey]
    assert (owner.epoch, root_key) in ow.terminal
    assert (owner.epoch, key_a) in ow.terminal
    assert (owner.epoch, key_a) in ow.payloads
    assert work.session_bytes(okey) > 0


# --- K/L. Teardown composition --------------------------------------


def _ready_t_ab(
    mode: AdmissionMode, lineage: str
) -> tuple[
    RootRegionLineageNamespace,
    RootRegionLineageState,
    RootRegionAdmissionResult,
    RootRegionLineageState,
    RootRegionAdmissionResult,
    str,
    str,
]:
    """Genuine bootstrap plus a singleton A read: TWO ACTUAL
    current keys (the root entry key and A's FILE key).  First
    endpoint shape (the asserted work-plane binding does not
    depend on the endpoint)."""
    endpoint = ENDPOINTS[0]
    ns, s0 = r_bootstrap(mode, lineage, root_body=ROOT_AB)
    result0 = derive_root_region_admission(s0, ns)
    assert result0.outcome is RootRegionAdmissionOutcome.READY
    t1 = r_issue(s0, ns, "b1", endpoint, (CAUSAL_ROOT_FACT,), "cat A.md")
    assert t1.outcome is RootLineageOutcome.ACCEPTED, t1.diagnostics
    t2 = r_observe(t1.state, ns, (read_request(endpoint, "b1", A_TEXT, "cat A.md"),))
    assert t2.outcome is RootLineageOutcome.ACCEPTED, t2.diagnostics
    s1 = t2.state
    result1 = derive_root_region_admission(s1, ns)
    assert result1.outcome is RootRegionAdmissionOutcome.READY, result1.diagnostics
    adm1 = result1.admission
    assert adm1 is not None
    key_a = next(row.content_keys[0] for row in adm1.path_associations if row.path == "A.md")
    return ns, s0, result0, s1, result1, key_a, _root_key(result1)


def _genuine_a2(
    s1: RootRegionLineageState, ns: RootRegionLineageNamespace, endpoint: str
) -> tuple[RootRegionLineageState, RootRegionAdmissionResult, str]:
    """Genuine A1 -> A2 supersession (first endpoint shape):
    a genuinely NEW A.md read carrying DIFFERENT bytes,
    descended from the A1 occurrence (a valid descendant
    issuance -- arrival, digests and revisions are never
    clocks)."""
    occ1 = next(o for o in s1.d_state.occurrences if o.call_id == "b1")
    t3 = r_issue(s1, ns, "b2", endpoint, (occ1.occurrence_id,), "cat A.md")
    assert t3.outcome is RootLineageOutcome.ACCEPTED, t3.diagnostics
    t4 = r_observe(t3.state, ns, (read_request(endpoint, "b2", A2_TEXT, "cat A.md"),))
    assert t4.outcome is RootLineageOutcome.ACCEPTED, t4.diagnostics
    s2 = t4.state
    result2 = derive_root_region_admission(s2, ns)
    assert result2.outcome is RootRegionAdmissionOutcome.READY, result2.diagnostics
    adm2 = result2.admission
    assert adm2 is not None
    key_a2 = next(row.content_keys[0] for row in adm2.path_associations if row.path == "A.md")
    return s2, result2, key_a2


def _genuine_a1_revert(
    s2: RootRegionLineageState, ns: RootRegionLineageNamespace, endpoint: str
) -> tuple[RootRegionLineageState, RootRegionAdmissionResult, str]:
    """Genuine A1 revert (first endpoint shape): a genuinely
    NEW A.md read carrying the OLD A1 bytes, descended from
    the A2 occurrence (a deliberate old-bytes descendant is a
    revert under the same frozen partial order)."""
    occ2 = next(o for o in s2.d_state.occurrences if o.call_id == "b2")
    t5 = r_issue(s2, ns, "b3", endpoint, (occ2.occurrence_id,), "cat A.md")
    assert t5.outcome is RootLineageOutcome.ACCEPTED, t5.diagnostics
    t6 = r_observe(t5.state, ns, (read_request(endpoint, "b3", A_TEXT, "cat A.md"),))
    assert t6.outcome is RootLineageOutcome.ACCEPTED, t6.diagnostics
    s3 = t6.state
    result3 = derive_root_region_admission(s3, ns)
    assert result3.outcome is RootRegionAdmissionOutcome.READY, result3.diagnostics
    adm3 = result3.admission
    assert adm3 is not None
    key_revert = next(row.content_keys[0] for row in adm3.path_associations if row.path == "A.md")
    return s3, result3, key_revert


@pytest.mark.parametrize("mode", MODES)
async def test_k_async_teardown_active_and_queued(mode: AdmissionMode) -> None:
    """Explicit async teardown over ACTIVE and QUEUED work: the
    plane is fenced, the active task is cancelled AND awaited,
    every still-waiting waiter is re-served the typed terminal,
    the synchronous teardown is refused with work_in_flight while
    the drain is live (store state preserved), and the store
    owner AND the work plane are released in ONE critical
    section -- no same-epoch reset window: a later resolve finds
    no live owner and mints no fresh attempt."""
    ns, s0, result0, s1, result1, key_a, root_key = _ready_t_ab(mode, f"ram019w-k-{mode.value}")
    registry = _work_registry()
    work = registry.work
    assert work is not None
    owner = registry.acquire(ns)
    a0 = owner.admit(s0, result0, ns, expected_revision=0)
    assert a0.outcome is RamStateOutcome.ADMITTED
    # Genuine supersession: the later A read advances the SAME
    # lineage, so the owner's current snapshot is s1 (revision
    # 1) with both current keys retained.
    a1 = owner.admit(s1, result1, ns, expected_revision=1)
    assert a1.outcome is RamStateOutcome.ADMITTED
    okey = owner.namespace.lineage_key

    gate = asyncio.Event()
    calls: list[int] = []
    seam = make_seam(gate, calls)
    leader = asyncio.create_task(work.resolve(ns, root_key, seam))
    await _until(lambda: work._active_key is not None and len(calls) == 1)
    queued = asyncio.create_task(work.resolve(ns, key_a, seam))
    await _until(lambda: work._owners.get(okey) is not None and key_a in work._owners[okey].live)

    # The baseline is IMMEDIATELY before the teardown, so the
    # freed delta covers every already-allocated work component
    # (the claimed reservations, the live attempts).
    proc_at_teardown = registry.process_owned_bytes
    td_task = asyncio.create_task(work.teardown_owner(ns))
    await _until(lambda: work._owners.get(okey) is not None and work._owners[okey].fenced)
    # While fenced (the drain still owns the active task), the
    # synchronous teardown refuses; the store state is preserved.
    t_ref = owner.teardown(ns)
    assert t_ref.outcome is RamStateOutcome.REFUSED
    assert t_ref.limitation is RamStateLimitation.WORK_IN_FLIGHT
    assert owner.lookup(root_key, ns).outcome is RamStateOutcome.FOUND

    td = await td_task
    assert td.outcome is RamWorkOutcome.TEARDOWN
    assert td.attempts_cancelled == 1  # the single ACTIVE dispatch task
    assert td.waiters_notified == 2  # both waiters re-served the typed terminal
    assert td.freed_bytes > 0
    assert td.freed_bytes == proc_at_teardown - registry.process_owned_bytes

    r_lead = await leader
    assert r_lead.outcome is RamWorkOutcome.FAILED
    assert r_lead.limitation is RamWorkLimitation.OWNER_TORN_DOWN
    assert r_lead.http_status == 503
    r_que = await queued
    assert r_que.outcome is RamWorkOutcome.FAILED
    assert r_que.limitation is RamWorkLimitation.OWNER_TORN_DOWN
    assert r_que.invocations == 0  # the queued attempt never dispatched

    # Store and work released atomically: no same-epoch reset window.
    assert registry.get(ns) is None
    assert work._owners.get(okey) is None
    again = await work.resolve(ns, root_key, seam)
    assert again.outcome is RamWorkOutcome.REFUSED
    assert again.limitation is RamWorkLimitation.OWNER_ABSENT
    assert work._owners == {}


@pytest.mark.parametrize("mode", MODES)
async def test_k2_async_teardown_before_any_work(mode: AdmissionMode) -> None:
    """An async teardown BEFORE any work attempt: a live store
    owner with NO work plane is still fully torn down -- the
    store owner is released in the SAME critical section --
    freed_bytes is exactly the store charge (the delta from
    the counter immediately before teardown), and every later
    operation refuses on the fenced owner."""
    ns, s0, result0 = _ready_t(mode, f"ram019w-k2-{mode.value}")
    registry = _work_registry()
    work = registry.work
    assert work is not None
    owner = registry.acquire(ns)
    a0 = owner.admit(s0, result0, ns, expected_revision=0)
    assert a0.outcome is RamStateOutcome.ADMITTED
    store_charge = owner.owned_bytes
    proc_at_teardown = registry.process_owned_bytes

    td = await work.teardown_owner(ns)
    assert td.outcome is RamWorkOutcome.TEARDOWN
    assert td.freed_bytes == store_charge
    assert td.freed_bytes == proc_at_teardown - registry.process_owned_bytes
    assert td.attempts_cancelled == 0
    assert td.waiters_notified == 0

    assert registry.get(ns) is None
    assert work._owners == {}
    gate = asyncio.Event()
    calls: list[int] = []
    seam = make_seam(gate, calls)
    again = await work.resolve(ns, _root_key(result0), seam)
    assert again.outcome is RamWorkOutcome.REFUSED
    assert again.limitation is RamWorkLimitation.OWNER_ABSENT
    assert calls == []
    t2 = owner.teardown(ns)
    assert t2.outcome is RamStateOutcome.REFUSED
    assert t2.limitation is RamStateLimitation.EPOCH_FENCED


@pytest.mark.parametrize("mode", MODES)
async def test_l_sync_teardown_idle_plane_and_owner_absent(mode: AdmissionMode) -> None:
    """An IDLE work plane (a COMPLETED attempt: payload retained,
    no live work) is released in the SAME critical section as the
    store owner by the synchronous teardown; the old epoch is
    fenced, every later operation refuses, and no fresh work is
    ever minted on the retained owner."""
    ns, s0, result0 = _ready_t(mode, f"ram019w-l-{mode.value}")
    key = _root_key(result0)
    registry = _work_registry()
    work = registry.work
    assert work is not None
    owner = registry.acquire(ns)
    a0 = owner.admit(s0, result0, ns, expected_revision=0)
    assert a0.outcome is RamStateOutcome.ADMITTED
    okey = owner.namespace.lineage_key

    async def ok_seam() -> bytes:
        return PAYLOAD

    done = await work.resolve(ns, key, ok_seam)
    assert done.outcome is RamWorkOutcome.COMPLETED
    hit0 = await work.resolve(ns, key, ok_seam)
    assert hit0.outcome is RamWorkOutcome.HIT

    # The baseline is IMMEDIATELY before the teardown, so the
    # freed delta covers every already-allocated work component
    # (the retained terminal record and the retained payload).
    proc_at_teardown = registry.process_owned_bytes
    t = owner.teardown(ns)
    assert t.outcome is RamStateOutcome.TEARDOWN
    assert t.freed_bytes == proc_at_teardown - registry.process_owned_bytes
    assert registry.get(ns) is None
    assert work._owners.get(okey) is None

    t2 = owner.teardown(ns)
    assert t2.outcome is RamStateOutcome.REFUSED
    assert t2.limitation is RamStateLimitation.EPOCH_FENCED
    again = await work.resolve(ns, key, ok_seam)
    assert again.outcome is RamWorkOutcome.REFUSED
    assert again.limitation is RamWorkLimitation.OWNER_ABSENT
    assert work._owners == {}


# --- M. Process capacity at the work boundary ------------------------


@pytest.mark.parametrize("mode", MODES)
async def test_m_process_capacity_exact_and_one_over(mode: AdmissionMode) -> None:
    """The work plane honors the SAME registry process ceiling:
    measured from a probe (the exact claim+dispatch delta and
    the ACTUAL peak charged occupancy of ONE genuine claim),
    a cap of EXACTLY that peak total admits and completes the
    claim with its peak exactly at the boundary (the final
    retained occupancy is lower than the peak while
    claim / task / waiter / terminal reservations coexist),
    while a cap ONE byte below the claim's pre-dispatch delta
    refuses PRE-CLAIM with the fixed 503 -- retaining nothing
    (the created work state is abandoned unregistered, the
    store owner stays intact)."""
    ns, s0, result0 = _ready_t(mode, f"ram019w-m-{mode.value}")
    key = _root_key(result0)

    # Probe 1: the registry base and the store charge of this record set.
    probe = RamStateOwnerRegistry(work_bounds=RamWorkBounds())
    p_owner = probe.acquire(ns)
    pa = p_owner.admit(s0, result0, ns, expected_revision=0)
    assert pa.outcome is RamStateOutcome.ADMITTED
    store_charge = p_owner.owned_bytes
    base_probe = probe.process_owned_bytes - store_charge

    # Probe 2: the exact claim+dispatch delta (gated seam).
    probe2 = RamStateOwnerRegistry(work_bounds=RamWorkBounds())
    p2_owner = probe2.acquire(ns)
    p2_owner.admit(s0, result0, ns, expected_revision=0)
    proc_claim0 = probe2.process_owned_bytes
    gate = asyncio.Event()
    calls: list[int] = []
    seam = make_seam(gate, calls)
    w2 = probe2.work
    assert w2 is not None
    t = asyncio.create_task(w2.resolve(ns, key, seam))
    await _until(lambda: w2._active_key is not None and len(calls) == 1)
    claim_plus_dispatch = probe2.process_owned_bytes - proc_claim0
    t.cancel()
    with pytest.raises(asyncio.CancelledError):
        await t

    # Probe 3: the ACTUAL PEAK charged occupancy of the full
    # completion (released gate).  The counter at seam
    # execution is NOT the peak: the publication fence
    # retains and charges the prepared payload AFTER the
    # seam, while the task / waiter / terminal reservations
    # still coexist.  Observe THIS probe registry's existing
    # _commit_process_delta transitions (test observer,
    # restored after) and take the maximum actual charged
    # total across the whole operation.
    probe3 = _PeakObservingRegistry(work_bounds=RamWorkBounds())
    p3_owner = probe3.acquire(ns)
    p3_owner.admit(s0, result0, ns, expected_revision=0)
    proc0 = probe3.process_owned_bytes
    gate3 = asyncio.Event()
    gate3.set()
    calls3: list[int] = []
    seam3 = make_seam(gate3, calls3)
    w3 = probe3.work
    assert w3 is not None
    r3 = await w3.resolve(ns, key, seam3)
    assert r3.outcome is RamWorkOutcome.COMPLETED
    assert len(calls3) == 1
    peaks3 = probe3.peak_totals
    assert peaks3
    peak_delta = max(peaks3) - proc0
    # The true peak is strictly above the final retained
    # occupancy (the finalization swap releases the claim /
    # task / waiter / terminal reservations).
    assert peak_delta > probe3.process_owned_bytes - proc0

    pre_dispatch_delta = claim_plus_dispatch - RAM_WORK_TASK_RESERVATION_BYTES
    cap_one_over = base_probe + store_charge + pre_dispatch_delta - 1
    # The positive cap is the ACTUAL maximum charged occupancy
    # across the whole operation (peak, not final residual):
    # the final retained occupancy is lower than the peak
    # while claim / task / waiter / terminal reservations
    # coexist.
    cap_full = base_probe + store_charge + peak_delta

    # DISTINCT equal-valued int objects for the two ceilings:
    # the occupancy recipe identity-deduplicates referents, so
    # one shared ceiling object would be charged once and skew
    # the measured registry base (the probe uses distinct
    # default int objects).
    proc_cap_one_over = cap_one_over + 0
    # Negative: one byte below the claim's pre-dispatch crossing.
    registry = RamStateOwnerRegistry(
        bounds=RamStateBounds(
            session_max_owned_bytes=cap_one_over,
            process_max_owned_bytes=proc_cap_one_over,
        ),
        work_bounds=RamWorkBounds(),
    )
    work = registry.work
    assert work is not None
    assert registry.process_owned_bytes == base_probe  # the recipe transfers
    owner = registry.acquire(ns)
    a0 = owner.admit(s0, result0, ns, expected_revision=0)
    assert a0.outcome is RamStateOutcome.ADMITTED
    proc_at_refusal = registry.process_owned_bytes
    refused = await work.resolve(ns, key, seam)
    assert refused.outcome is RamWorkOutcome.REFUSED
    assert refused.limitation is RamStateLimitation.PROCESS_OWNED_BYTES_OVER_BOUND
    assert refused.http_status == 503
    assert refused.invocations == 0
    assert len(calls) == 1  # only the probe invocation ever ran
    assert work._owners.get(owner.namespace.lineage_key) is None
    assert registry.process_owned_bytes == proc_at_refusal
    assert owner.lookup(key, ns).outcome is RamStateOutcome.FOUND

    # Positive: the cap of EXACTLY the actual PEAK total admits
    # and completes at the boundary (the operation's peak is
    # exactly the cap; the final retained occupancy is lower).
    registry2 = _PeakObservingRegistry(
        bounds=RamStateBounds(
            session_max_owned_bytes=cap_full,
            process_max_owned_bytes=cap_full + 0,
        ),
        work_bounds=RamWorkBounds(),
    )
    work2 = registry2.work
    assert work2 is not None
    owner2 = registry2.acquire(ns)
    a2 = owner2.admit(s0, result0, ns, expected_revision=0)
    assert a2.outcome is RamStateOutcome.ADMITTED
    gate2 = asyncio.Event()
    gate2.set()
    calls2: list[int] = []
    r2 = await work2.resolve(ns, key, make_seam(gate2, calls2))
    assert r2.outcome is RamWorkOutcome.COMPLETED
    assert r2.invocations == 1
    assert len(calls2) == 1
    peaks2 = registry2.peak_totals
    assert peaks2
    assert max(peaks2) == cap_full  # the operation peaks exactly at the cap
    assert registry2.process_owned_bytes <= cap_full
    assert owner2.namespace.lineage_key in work2._owners


# --- N. Supersession, revert, replay ----------------------------------


@pytest.mark.parametrize("mode", MODES)
async def test_n1_stale_completion_refused(mode: AdmissionMode) -> None:
    """A1 -> A2 supersession while A1's work is in flight: the
    late completion is terminal unsuccessful (the key ceased
    to be current -- fixed 409, the ACTUAL invocation is
    recorded, the payload is NOT published and never
    retained), the stale key is refused pre-claim, and the
    current superseding key earns its OWN genuine attempt."""
    ns, s0, result0, s1, result1, key_a, _root_key_a = _ready_t_ab(mode, f"ram019w-n1-{mode.value}")
    registry = _work_registry()
    work = registry.work
    assert work is not None
    owner = registry.acquire(ns)
    assert owner.admit(s0, result0, ns, expected_revision=0).outcome is RamStateOutcome.ADMITTED
    assert owner.admit(s1, result1, ns, expected_revision=1).outcome is RamStateOutcome.ADMITTED
    okey = owner.namespace.lineage_key

    gate = asyncio.Event()
    calls: list[int] = []
    seam = make_seam(gate, calls)
    lead = asyncio.create_task(work.resolve(ns, key_a, seam))
    await _until(lambda: work._active_key is not None and len(calls) == 1)

    # Genuine supersession: A2 becomes current, key_a stale.
    s2, result2, key_a2 = _genuine_a2(s1, ns, ENDPOINTS[0])
    assert key_a2 != key_a
    assert owner.admit(s2, result2, ns, expected_revision=2).outcome is RamStateOutcome.ADMITTED

    # The late completion is refused by the currentness fence.
    gate.set()
    r = await lead
    assert r.outcome is RamWorkOutcome.FAILED
    assert r.limitation is RamWorkLimitation.KEY_NOT_CURRENT
    assert r.http_status == 409
    assert r.invocations == 1  # the attempt actually consumed its invocation
    assert r.attempt_invocations == 1
    assert r.payload is None
    ow = work._owners.get(okey)
    assert ow is not None
    assert (owner.epoch, key_a) in ow.terminal
    assert (owner.epoch, key_a) not in ow.payloads
    assert owner.lookup(key_a, ns).outcome is RamStateOutcome.NOT_FOUND
    assert owner.lookup(key_a2, ns).outcome is RamStateOutcome.FOUND

    # The stale key is refused PRE-CLAIM (it is no longer
    # current; the terminal is not re-served for a stale key).
    r_stale = await work.resolve(ns, key_a, seam)
    assert r_stale.outcome is RamWorkOutcome.REFUSED
    assert r_stale.limitation is RamWorkLimitation.KEY_NOT_CURRENT
    assert r_stale.invocations == 0
    assert len(calls) == 1

    # The current superseding key earns its OWN genuine
    # attempt (one new invocation), then a RAM-only hit.
    gate2 = asyncio.Event()
    gate2.set()
    calls2: list[int] = []
    r_new = await work.resolve(ns, key_a2, make_seam(gate2, calls2))
    assert r_new.outcome is RamWorkOutcome.COMPLETED
    assert r_new.invocations == 1
    assert len(calls2) == 1
    hit_new = await work.resolve(ns, key_a2, make_seam(gate2, []))
    assert hit_new.outcome is RamWorkOutcome.HIT
    assert hit_new.payload is r_new.payload
    assert len(calls2) == 1


@pytest.mark.parametrize("mode", MODES)
async def test_n2_genuine_revert_reuses_retained_payload(mode: AdmissionMode) -> None:
    """Valid A1 -> A2 -> genuinely new A1 revert (OLD bytes):
    A2 earns its OWN genuine work attempt; an OLD retained P
    state replayed after A2 cannot reactivate A1; and the A1
    payload SURVIVES the supersession and is reused on the
    revert as a RAM-only HIT -- exactly TWO total invocations,
    no third."""
    ns, s0, result0, s1, result1, key_a, _root_key_a = _ready_t_ab(mode, f"ram019w-n2-{mode.value}")
    registry = _work_registry()
    work = registry.work
    assert work is not None
    owner = registry.acquire(ns)
    assert owner.admit(s0, result0, ns, expected_revision=0).outcome is RamStateOutcome.ADMITTED
    assert owner.admit(s1, result1, ns, expected_revision=1).outcome is RamStateOutcome.ADMITTED

    # A1 completes: the immutable payload is retained.
    gate1 = asyncio.Event()
    gate1.set()
    calls1: list[int] = []
    r1 = await work.resolve(ns, key_a, make_seam(gate1, calls1))
    assert r1.outcome is RamWorkOutcome.COMPLETED
    assert r1.invocations == 1
    assert r1.payload is not None
    assert len(calls1) == 1

    # A2 supersession (key_a is no longer current).
    s2, result2, key_a2 = _genuine_a2(s1, ns, ENDPOINTS[0])
    assert key_a2 != key_a
    assert owner.admit(s2, result2, ns, expected_revision=2).outcome is RamStateOutcome.ADMITTED
    # The retained A1 payload survived the supersession.
    ow = work._owners.get(owner.namespace.lineage_key)
    assert ow is not None
    assert ow.payloads.get((owner.epoch, key_a)) is r1.payload

    # A2 earns its OWN genuine work attempt (the second total
    # invocation of this test).
    gate2 = asyncio.Event()
    gate2.set()
    calls2: list[int] = []
    r2 = await work.resolve(ns, key_a2, make_seam(gate2, calls2))
    assert r2.outcome is RamWorkOutcome.COMPLETED
    assert r2.invocations == 1
    assert r2.payload is not None
    assert r2.payload.content_key == key_a2
    assert len(calls2) == 1

    # An OLD retained P state replayed AFTER A2 is the
    # lineage-rollback fence: it re-commits nothing and cannot
    # reactivate A1 (the stale key stays pre-claim refused).
    replay = owner.admit(s1, result1, ns, expected_revision=3)
    assert replay.outcome is RamStateOutcome.REFUSED
    assert replay.limitation is RamStateLimitation.STALE_STATE_REVISION
    assert replay.charged_bytes == 0
    assert replay.revision == 3
    assert replay.snapshot is not None
    assert replay.snapshot is owner.snapshot
    assert replay.snapshot.state is s2
    assert owner.revision == 3
    assert owner.lookup(key_a, ns).outcome is RamStateOutcome.NOT_FOUND
    r_stale = await work.resolve(ns, key_a, make_seam(gate2, calls2))
    assert r_stale.outcome is RamWorkOutcome.REFUSED
    assert r_stale.limitation is RamWorkLimitation.KEY_NOT_CURRENT
    assert r_stale.invocations == 0
    assert len(calls1) + len(calls2) == 2

    # Genuine A1 revert (OLD bytes): the A1 canonical key is
    # current again.
    s3, result3, key_revert = _genuine_a1_revert(s2, ns, ENDPOINTS[0])
    assert key_revert == key_a
    assert owner.admit(s3, result3, ns, expected_revision=3).outcome is RamStateOutcome.ADMITTED

    # The retained payload is reused: HIT, zero new invocations
    # (exactly TWO total invocations of this test, no third).
    r_hit = await work.resolve(ns, key_a, make_seam(gate1, calls1))
    assert r_hit.outcome is RamWorkOutcome.HIT
    assert r_hit.payload is r1.payload
    assert r_hit.invocations == 0
    assert len(calls1) + len(calls2) == 2


@pytest.mark.parametrize("mode", MODES)
async def test_q_unrelated_b_preserves_unchanged_a_hit(mode: AdmissionMode) -> None:
    """Requirement 7 work-plane case: the bootstrap root
    declares BOTH A.md and B.md; a genuine singleton A read is
    admitted and A's work completes; an UNRELATED genuine
    singleton B read in the SAME P lineage is admitted into the
    SAME owner and B earns its own work attempt.  Unchanged A
    keeps its exact stable semantic key: the later A demand is
    still a HIT on the SAME retained payload identity with zero
    new invocations (first endpoint shape)."""
    ns, s0, result0, s1, result1, key_a, _root_key_a = _ready_t_ab(mode, f"ram019w-q-{mode.value}")
    registry = _work_registry()
    work = registry.work
    assert work is not None
    owner = registry.acquire(ns)
    assert owner.admit(s0, result0, ns, expected_revision=0).outcome is RamStateOutcome.ADMITTED
    assert owner.admit(s1, result1, ns, expected_revision=1).outcome is RamStateOutcome.ADMITTED

    # A's work completes: the immutable payload is retained.
    gate1 = asyncio.Event()
    gate1.set()
    calls1: list[int] = []
    r_a = await work.resolve(ns, key_a, make_seam(gate1, calls1))
    assert r_a.outcome is RamWorkOutcome.COMPLETED
    assert r_a.invocations == 1
    assert r_a.payload is not None
    assert r_a.payload.content_key == key_a
    assert len(calls1) == 1

    # Unrelated genuine singleton B read in the SAME lineage.
    endpoint = ENDPOINTS[0]
    t3 = r_issue(s1, ns, "b2", endpoint, (CAUSAL_ROOT_FACT,), "cat B.md")
    assert t3.outcome is RootLineageOutcome.ACCEPTED, t3.diagnostics
    t4 = r_observe(t3.state, ns, (read_request(endpoint, "b2", B_TEXT, "cat B.md"),))
    assert t4.outcome is RootLineageOutcome.ACCEPTED, t4.diagnostics
    s2 = t4.state
    result2 = derive_root_region_admission(s2, ns)
    assert result2.outcome is RootRegionAdmissionOutcome.READY, result2.diagnostics
    adm2 = result2.admission
    assert adm2 is not None
    b_rows = [row for row in adm2.path_associations if row.path == "B.md"]
    assert len(b_rows) == 1
    key_b = b_rows[0].content_keys[0]
    assert key_b != key_a
    # Unchanged A keeps its exact stable semantic key in the new
    # derivation.
    a_rows = [row for row in adm2.path_associations if row.path == "A.md"]
    assert len(a_rows) == 1
    assert a_rows[0].content_keys == (key_a,)
    assert owner.admit(s2, result2, ns, expected_revision=2).outcome is RamStateOutcome.ADMITTED

    # B earns its OWN genuine work attempt.
    gate2 = asyncio.Event()
    gate2.set()
    calls2: list[int] = []
    r_b = await work.resolve(ns, key_b, make_seam(gate2, calls2))
    assert r_b.outcome is RamWorkOutcome.COMPLETED
    assert r_b.invocations == 1
    assert r_b.payload is not None
    assert r_b.payload.content_key == key_b
    assert len(calls2) == 1

    # Unchanged A after the unrelated B admission + B work: its
    # key is still lookup-eligible and its demand is a HIT on
    # the SAME retained payload identity (zero new invocations).
    assert owner.lookup(key_a, ns).outcome is RamStateOutcome.FOUND
    hit_a = await work.resolve(ns, key_a, make_seam(gate1, calls1))
    assert hit_a.outcome is RamWorkOutcome.HIT
    assert hit_a.payload is r_a.payload
    assert hit_a.invocations == 0
    assert len(calls1) == 1
    assert len(calls1) + len(calls2) == 2


@pytest.mark.parametrize("mode", MODES)
async def test_n3_failed_revert_still_terminal(mode: AdmissionMode) -> None:
    """FAILED A1 -> A2 -> genuinely new A1 revert in the SAME
    epoch: the original failed A1 attempt STILL applies -- a
    causal change alone (even a genuine old-bytes revert, an
    equal-byte witness) never resets the identical full
    key's attempt; the terminal is re-served with zero new
    invocations."""
    ns, s0, result0, s1, result1, key_a, _root_key_a = _ready_t_ab(mode, f"ram019w-n3-{mode.value}")
    registry = _work_registry()
    work = registry.work
    assert work is not None
    owner = registry.acquire(ns)
    assert owner.admit(s0, result0, ns, expected_revision=0).outcome is RamStateOutcome.ADMITTED
    assert owner.admit(s1, result1, ns, expected_revision=1).outcome is RamStateOutcome.ADMITTED

    # A1's work FAILS (bounded synthetic exception).
    calls1: list[int] = []

    async def fail_seam() -> bytes:
        calls1.append(1)
        raise RuntimeError("synthetic work failure")

    r1 = await work.resolve(ns, key_a, fail_seam)
    assert r1.outcome is RamWorkOutcome.FAILED
    assert r1.limitation is RamWorkLimitation.WORK_FAILED
    assert r1.http_status == 503
    assert r1.invocations == 1
    assert len(calls1) == 1

    # A2 supersession + genuine old-byte A1 revert.
    s2, result2, key_a2 = _genuine_a2(s1, ns, ENDPOINTS[0])
    assert key_a2 != key_a
    assert owner.admit(s2, result2, ns, expected_revision=2).outcome is RamStateOutcome.ADMITTED
    s3, result3, key_revert = _genuine_a1_revert(s2, ns, ENDPOINTS[0])
    assert key_revert == key_a
    assert owner.admit(s3, result3, ns, expected_revision=3).outcome is RamStateOutcome.ADMITTED

    # The failed attempt is re-served: no retry, no new
    # invocation, the healthy seam is never run.
    gate_ok = asyncio.Event()
    gate_ok.set()
    calls_ok: list[int] = []
    r2 = await work.resolve(ns, key_a, make_seam(gate_ok, calls_ok))
    assert r2.outcome is RamWorkOutcome.FAILED
    assert r2.limitation is RamWorkLimitation.WORK_FAILED
    assert r2.http_status == 503
    assert r2.invocations == 0
    assert r2.attempt_invocations == 1
    assert calls_ok == []
    assert len(calls1) == 1


# --- B2. Claimant cancellation -----------------------------------------


@pytest.mark.parametrize("mode", MODES)
async def test_b2_claimant_cancelled_follower_completes(mode: AdmissionMode) -> None:
    """The CLAIMANT (first waiter) cancelled: only that waiter
    detaches; the shared work of the surviving follower
    proceeds (the owned task is NOT cancelled), the follower
    receives the shared payload, the terminal record retains
    the single ACTUAL invocation, and the later same-key
    demand stays a RAM-only hit."""
    ns, s0, result0 = _ready_t(mode, f"ram019w-b2-{mode.value}")
    key = _root_key(result0)
    registry = _work_registry()
    work = registry.work
    assert work is not None
    owner = registry.acquire(ns)
    a0 = owner.admit(s0, result0, ns, expected_revision=0)
    assert a0.outcome is RamStateOutcome.ADMITTED
    okey = owner.namespace.lineage_key

    def waiter_count() -> int:
        ow = work._owners.get(okey)
        if ow is None:
            return 0
        la = ow.live.get(key)
        return len(la.waiters) if la is not None else 0

    gate = asyncio.Event()
    calls: list[int] = []
    seam = make_seam(gate, calls)
    claimant = asyncio.create_task(work.resolve(ns, key, seam))
    follower = asyncio.create_task(work.resolve(ns, key, seam))
    await _until(lambda: waiter_count() == 2)
    # The CLAIMANT cancels itself; the follower still waits.
    claimant.cancel()
    with pytest.raises(asyncio.CancelledError):
        await claimant
    await _until(lambda: waiter_count() == 1)
    # The owned work was NOT cancelled by the claimant's
    # departure: it proceeds to the shared payload.
    gate.set()
    r_follow = await follower
    assert r_follow.outcome is RamWorkOutcome.JOINED
    assert r_follow.invocations == 0
    assert r_follow.attempt_invocations == 1
    assert r_follow.payload is not None
    assert len(calls) == 1
    # The terminal record retained the single ACTUAL
    # invocation; the later same-key demand is a RAM-only HIT.
    ow = work._owners.get(okey)
    assert ow is not None
    term = ow.terminal.get((owner.epoch, key))
    assert term is not None
    assert term.outcome is RamWorkOutcome.COMPLETED
    assert term.invocations == 1
    hit = await work.resolve(ns, key, seam)
    assert hit.outcome is RamWorkOutcome.HIT
    assert hit.payload is r_follow.payload
    assert len(calls) == 1


# --- O. Namespace / epoch fences and other-owner survival --------------


@pytest.mark.parametrize("mode", MODES)
async def test_o1_foreign_namespace_and_epoch_fences(mode: AdmissionMode) -> None:
    """A value-equal FOREIGN namespace copy carrying the
    registered lineage key is refused at the REGISTRY (the
    fixed RamStateInputError) on every work-plane registry
    access (acquire / get / resolve / async teardown); the
    owner-level operations bind the registered trusted record
    by identity (owner_namespace_mismatch on lookup /
    teardown); after the real async teardown the fenced owner
    refuses EVERY operation including a fresh admit -- no
    same-epoch reset window, and the work plane mints no
    fresh attempt."""
    ns, s0, result0 = _ready_t(mode, f"ram019w-o1-{mode.value}")
    key = _root_key(result0)
    ns_copy = ns.model_copy()
    assert ns_copy is not ns
    assert ns_copy.lineage_key == ns.lineage_key
    registry = _work_registry()
    work = registry.work
    assert work is not None
    owner = registry.acquire(ns)
    a0 = owner.admit(s0, result0, ns, expected_revision=0)
    assert a0.outcome is RamStateOutcome.ADMITTED
    # Registry access with the value-equal FOREIGN copy now
    # that the lineage key is REGISTERED: the fixed input
    # error (the registered record is joined by identity).
    with pytest.raises(RamStateInputError):
        registry.acquire(ns_copy)
    with pytest.raises(RamStateInputError):
        registry.get(ns_copy)

    # Work-plane registry access (resolve / async teardown)
    # through the same fence.
    gate = asyncio.Event()
    calls: list[int] = []
    seam = make_seam(gate, calls)
    with pytest.raises(RamStateInputError):
        await work.resolve(ns_copy, key, seam)
    with pytest.raises(RamStateInputError):
        await work.teardown_owner(ns_copy)
    assert calls == []
    assert registry.get(ns) is owner  # the owner is untouched

    # Owner-level operations bind the registered record by
    # identity.
    cross = owner.lookup(key, ns_copy)
    assert cross.outcome is RamStateOutcome.NOT_FOUND
    assert cross.limitation is RamStateLimitation.OWNER_NAMESPACE_MISMATCH
    torn_cross = owner.teardown(ns_copy)
    assert torn_cross.outcome is RamStateOutcome.REFUSED
    assert torn_cross.limitation is RamStateLimitation.OWNER_NAMESPACE_MISMATCH

    # The real async teardown, then the fenced owner refuses
    # EVERY operation (including a fresh admit at the old
    # epoch): no same-epoch reset window.
    td = await work.teardown_owner(ns)
    assert td.outcome is RamWorkOutcome.TEARDOWN
    fenced_admit = owner.admit(s0, result0, ns, expected_revision=0)
    assert fenced_admit.outcome is RamStateOutcome.REFUSED
    assert fenced_admit.limitation is RamStateLimitation.EPOCH_FENCED
    fenced_lookup = owner.lookup(key, ns)
    assert fenced_lookup.outcome is RamStateOutcome.NOT_FOUND
    assert fenced_lookup.limitation is RamStateLimitation.EPOCH_FENCED
    again = await work.resolve(ns, key, seam)
    assert again.outcome is RamWorkOutcome.REFUSED
    assert again.limitation is RamWorkLimitation.OWNER_ABSENT
    assert calls == []


@pytest.mark.parametrize("mode", MODES)
async def test_o2_other_owner_survives_teardown(mode: AdmissionMode) -> None:
    """Teardown of ONE owner releases ONLY that namespace's
    occupancy: the other owner's snapshot, charge, lookup and
    work plane (the retained payload, the RAM-only hit, zero
    new invocations) survive intact; the process counter drops
    by exactly the torn-down owner's store charge."""
    ns_a, s0a, result0a = _ready_t(mode, f"ram019w-o2a-{mode.value}")
    ns_b, s0b, result0b = _ready_t(mode, f"ram019w-o2b-{mode.value}")
    assert ns_a.lineage_key != ns_b.lineage_key
    key_b = _root_key(result0b)
    registry = _work_registry()
    work = registry.work
    assert work is not None
    owner_a = registry.acquire(ns_a)
    owner_b = registry.acquire(ns_b)
    assert owner_a.admit(s0a, result0a, ns_a, expected_revision=0).outcome is (
        RamStateOutcome.ADMITTED
    )
    assert owner_b.admit(s0b, result0b, ns_b, expected_revision=0).outcome is (
        RamStateOutcome.ADMITTED
    )
    # Owner B's work plane: a retained payload (RAM-only HIT).
    gate = asyncio.Event()
    gate.set()
    calls: list[int] = []
    r_b = await work.resolve(ns_b, key_b, make_seam(gate, calls))
    assert r_b.outcome is RamWorkOutcome.COMPLETED
    assert r_b.invocations == 1
    assert len(calls) == 1

    charge_a = owner_a.owned_bytes
    charge_b = owner_b.owned_bytes
    snap_b = owner_b.snapshot
    proc_before = registry.process_owned_bytes

    # Tear down owner A (no work plane of its own).
    td = await work.teardown_owner(ns_a)
    assert td.outcome is RamWorkOutcome.TEARDOWN
    assert td.freed_bytes == charge_a
    assert registry.process_owned_bytes == proc_before - charge_a
    assert registry.get(ns_a) is None

    # Owner B survives completely (store AND work plane).
    assert registry.get(ns_b) is owner_b
    assert owner_b.snapshot is snap_b
    assert owner_b.owned_bytes == charge_b
    hit_b = await work.resolve(ns_b, key_b, make_seam(gate, []))
    assert hit_b.outcome is RamWorkOutcome.HIT
    assert hit_b.payload is r_b.payload
    assert hit_b.invocations == 0
    assert len(calls) == 1
    assert owner_b.lookup(key_b, ns_b).outcome is RamStateOutcome.FOUND
    assert registry.process_owned_bytes == proc_before - charge_a


# --- M2. Dispatch-time (pump) capacity crossing ------------------------


@pytest.mark.parametrize("mode", MODES)
async def test_m2_dispatch_capacity_crossing(mode: AdmissionMode) -> None:
    """The SAME ceilings bound the DISPATCH (pump) task
    reservation: with a process cap that the claim meets
    EXACTLY but the claim + task reservation crosses, the
    SESSION ceiling passes the dispatch session total (store
    + claim + task reservation) EXACTLY while the PROCESS
    ceiling (which includes the registry base, so session <=
    process is preserved) is ONE byte below the dispatch
    process total -- the queued claim is finalized FAILED
    process capacity with ZERO actual invocation and no
    dispatch (the seam is never run); the retained terminal
    metadata is charged, the store owner and lookup stay
    intact, the counter never crosses, and a later same-key
    demand re-serves the terminal without a dispatch."""
    ns, s0, result0 = _ready_t(mode, f"ram019w-m2-{mode.value}")
    key = _root_key(result0)

    # Probes (same shape as M): the claim-only (pre-dispatch)
    # delta of ONE genuine claim.
    probe = RamStateOwnerRegistry(work_bounds=RamWorkBounds())
    p_owner = probe.acquire(ns)
    assert p_owner.admit(s0, result0, ns, expected_revision=0).outcome is (RamStateOutcome.ADMITTED)
    store_charge = p_owner.owned_bytes
    base_probe = probe.process_owned_bytes - store_charge
    probe2 = RamStateOwnerRegistry(work_bounds=RamWorkBounds())
    p2_owner = probe2.acquire(ns)
    assert p2_owner.admit(s0, result0, ns, expected_revision=0).outcome is (
        RamStateOutcome.ADMITTED
    )
    proc_claim0 = probe2.process_owned_bytes
    gate = asyncio.Event()
    calls_p: list[int] = []
    seam_p = make_seam(gate, calls_p)
    w2 = probe2.work
    assert w2 is not None
    t = asyncio.create_task(w2.resolve(ns, key, seam_p))
    await _until(lambda: w2._active_key is not None and len(calls_p) == 1)
    claim_plus_dispatch = probe2.process_owned_bytes - proc_claim0
    t.cancel()
    with pytest.raises(asyncio.CancelledError):
        await t
    pre_dispatch_delta = claim_plus_dispatch - RAM_WORK_TASK_RESERVATION_BYTES

    # The SESSION ceiling passes the dispatch session total
    # (store + claim + task reservation) EXACTLY; the PROCESS
    # ceiling (which also carries the registry base, so the
    # session <= process law holds) is ONE byte below the
    # dispatch process total -- so ONLY the process ceiling
    # crosses, at dispatch.
    session_cap = store_charge + pre_dispatch_delta + RAM_WORK_TASK_RESERVATION_BYTES
    cap = base_probe + store_charge + pre_dispatch_delta + RAM_WORK_TASK_RESERVATION_BYTES - 1
    assert session_cap <= cap
    registry = RamStateOwnerRegistry(
        bounds=RamStateBounds(
            session_max_owned_bytes=session_cap,
            process_max_owned_bytes=cap,
        ),
        work_bounds=RamWorkBounds(),
    )
    work = registry.work
    assert work is not None
    assert registry.process_owned_bytes == base_probe  # the recipe transfers
    owner = registry.acquire(ns)
    assert owner.admit(s0, result0, ns, expected_revision=0).outcome is (RamStateOutcome.ADMITTED)
    calls: list[int] = []
    seam = make_seam(asyncio.Event(), calls)  # the gate never opens

    # The claim is accepted (it is 4095 bytes under the
    # process cap); the dispatch task reservation then
    # crosses the process ceiling -> the queued claim is
    # finalized FAILED capacity, zero invocation, no dispatch.
    refused = await work.resolve(ns, key, seam)
    assert refused.outcome is RamWorkOutcome.FAILED
    assert refused.limitation is RamStateLimitation.PROCESS_OWNED_BYTES_OVER_BOUND
    assert refused.http_status == 503
    assert refused.invocations == 0
    assert refused.attempt_invocations == 0
    assert calls == []  # the seam was never run
    # The retained terminal metadata stays (charged); the
    # store owner and lookup are intact; the counter never
    # crossed.
    proc_at = registry.process_owned_bytes
    assert registry.process_owned_bytes <= cap
    okey = owner.namespace.lineage_key
    ow = work._owners.get(okey)
    assert ow is not None
    assert (owner.epoch, key) in ow.terminal
    assert ow.live == {}
    assert owner.lookup(key, ns).outcome is RamStateOutcome.FOUND
    # A later same-key demand re-serves the terminal without a
    # dispatch (no queue, no invocation, no new charge).
    again = await work.resolve(ns, key, seam)
    assert again.outcome is RamWorkOutcome.FAILED
    assert again.limitation is RamStateLimitation.PROCESS_OWNED_BYTES_OVER_BOUND
    assert again.invocations == 0
    # The terminal record preserves the ACTUAL shared
    # invocation count: zero (the queued claim never
    # dispatched, the seam never ran).
    assert again.attempt_invocations == 0
    assert calls == []
    assert registry.process_owned_bytes == proc_at


# --- P. RAM-only hits with mechanically denied host IO -----------------


@pytest.mark.parametrize("mode", MODES)
async def test_p_hits_with_denied_host_io(
    mode: AdmissionMode, monkeypatch: pytest.MonkeyPatch
) -> None:
    """No host IO after setup (first endpoint shape): the
    closed 24-facility trap stays open across repeated
    RAM-only hits of the retained payload, the terminal
    failure re-serve, the retained terminal / payload /
    catalog / graph traversal and the lookups -- the work
    plane's normal hit / re-serve path is RAM-only."""
    ns, s0, result0, s1, result1, key_a, root_key = _ready_t_ab(mode, f"ram019w-p-{mode.value}")
    registry = _work_registry()
    work = registry.work
    assert work is not None
    owner = registry.acquire(ns)
    assert owner.admit(s0, result0, ns, expected_revision=0).outcome is RamStateOutcome.ADMITTED
    assert owner.admit(s1, result1, ns, expected_revision=1).outcome is RamStateOutcome.ADMITTED

    # A retained payload (key_a) and a terminal failure
    # (root_key): both BEFORE the trap is installed.
    gate = asyncio.Event()
    gate.set()
    calls: list[int] = []
    seam = make_seam(gate, calls)
    r_a = await work.resolve(ns, key_a, seam)
    assert r_a.outcome is RamWorkOutcome.COMPLETED
    assert r_a.payload is not None
    assert len(calls) == 1

    async def fail_seam() -> bytes:
        raise RuntimeError("synthetic work failure")

    r_r = await work.resolve(ns, root_key, fail_seam)
    assert r_r.outcome is RamWorkOutcome.FAILED
    assert r_r.limitation is RamWorkLimitation.WORK_FAILED

    io_calls: list[str] = []

    def trap(label: str) -> Callable[..., Any]:
        def refused(*trap_args: Any, **trap_kwargs: Any) -> Any:
            io_calls.append(label)
            raise AssertionError("forbidden host IO: " + label)

        return refused

    for module, name in _host_io_facilities():
        monkeypatch.setattr(module, name, trap(module.__name__ + "." + name))

    # Repeated actual RAM-only hits (the retained payload by
    # identity, zero new invocations).
    h1 = await work.resolve(ns, key_a, seam)
    assert h1.outcome is RamWorkOutcome.HIT
    h2 = await work.resolve(ns, key_a, seam)
    assert h2.outcome is RamWorkOutcome.HIT
    assert h1.payload is r_a.payload
    assert h2.payload is r_a.payload
    assert h1.invocations == 0
    assert len(calls) == 1
    # The terminal failure re-serve (zero new invocations, the
    # failing seam is never re-run).
    again = await work.resolve(ns, root_key, fail_seam)
    assert again.outcome is RamWorkOutcome.FAILED
    assert again.limitation is RamWorkLimitation.WORK_FAILED
    assert again.invocations == 0
    assert again.attempt_invocations == 1
    # Retained work-graph traversal (pure data access).
    okey = owner.namespace.lineage_key
    ow = work._owners.get(okey)
    assert ow is not None
    for record in ow.terminal.values():
        assert record is not None
        repr(record)
        str(record)
    for payload in ow.payloads.values():
        repr(payload)
        assert payload is r_a.payload
    for entry in owner.history:
        repr(entry)
    snap = owner.snapshot
    assert snap is not None
    rr = snap.result.r_result
    assert rr is not None
    fr = rr.f_result
    assert fr is not None
    overlay = fr.overlay
    assert overlay is not None
    for node in overlay.nodes:
        repr(node)
    for edge in overlay.edges:
        repr(edge)
    assert owner.lookup(key_a, ns).outcome is RamStateOutcome.FOUND
    assert owner.lookup(root_key, ns).outcome is RamStateOutcome.FOUND
    assert io_calls == []

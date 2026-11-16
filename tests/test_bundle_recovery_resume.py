"""020 protected session recovery: resume coordination, the
live recovery owner and the durable fail-closed fence
(whole020 component stage).

SAVED FIRST INCREMENT: the registry recovery-allocation
seam (``acquire_new_with_epoch_floor``) -- the strict
restart allocation used by the resume boundary: no
idempotent join, no burn / re-acquire, the allocated epoch
strictly above the recorded durable prior even in a fresh
process, the duplicate-live-owner refusal before any
identity join, and the preserved normal ``acquire`` /
``new_owner`` epoch law (epoch-allocation /
duplicate-owner evidence).

SAVED SECOND INCREMENT: the ACTUAL single-session resume
from its trusted address over the protected store --
multiple dormant persisted sessions, resume of exactly ONE
with no source / root / reference in the input, the
restored ACTUAL P/T in a live epoch strictly above the
durable prior, the retained writer while the owner is
live, lazy ACTUAL 019-b work-plane preparation (needed
keys only, once each), the denied-host-IO repeated RAM
hits and the composed teardown (writer released only
after the store owner is gone).  The fenced-transition
and quarantine / fault / race cases of this same suite
follow in this same file.

The stage stays inert: no adapter wiring, no configuration
key, no v1 runtime activation.
"""

from __future__ import annotations

import asyncio
import json
import os
import subprocess
import sys
import threading
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest

import slaif_local_coding.constitution.bundles.recovery_resume as recovery_resume_mod
from slaif_local_coding.constitution.bundles.graph_models import (
    ROOT_FILENAME,
)
from slaif_local_coding.constitution.bundles.ram_state import (
    RamStateCapacityError,
    RamStateDuplicateOwnerError,
    RamStateInputError,
    RamStateOwner,
    RamStateOwnerRegistry,
    ram_owner_base_charge,
)
from slaif_local_coding.constitution.bundles.ram_state_models import (
    RamStateBounds,
    RamStateLimitation,
    RamStateOutcome,
)
from slaif_local_coding.constitution.bundles.ram_work_models import (
    RamWorkLimitation,
    RamWorkOutcome,
)
from slaif_local_coding.constitution.bundles.recovery_codec import (
    RecoveryCodecSizeError,
)
from slaif_local_coding.constitution.bundles.recovery_models import (
    RecoveryError,
    RecoveryRecord,
    RecoverySessionAddress,
)
from slaif_local_coding.constitution.bundles.recovery_resume import (
    RECOVERY_TRANSIENT_FLOOR_BYTES,
    RecoveryAdmitOutcome,
    RecoveryResumeOutcome,
    RecoveryTeardownOutcome,
    resume_session,
)
from slaif_local_coding.constitution.bundles.recovery_store import (
    RecoveryPublishResult,
    RecoverySession,
    RecoveryStore,
    RecoveryStoreError,
    RecoveryStoreLimitation,
    session_directory_name,
)
from slaif_local_coding.constitution.bundles.root_region_admission import (
    derive_root_region_admission,
)
from slaif_local_coding.constitution.bundles.root_region_admission_result_models import (
    RootRegionAdmissionOutcome,
    RootRegionAdmissionResult,
)
from slaif_local_coding.constitution.cache import RequestIdentity
from tests.test_bundle_ram_lifecycle import (
    L1_LEGAL_STAGE,
    L1_V1,
    L4C2_ROOT,
    _l1_dep_read,
    _lifecycle_seam,
    _path_key,
)
from tests.test_bundle_ram_work import _work_registry
from tests.test_bundle_recovery_codec import _genuine_owner, _root_content_key
from tests.test_bundle_recovery_store import _prepared_root
from tests.test_causal_history import ENDPOINTS, MODES
from tests.test_root_region_lineage import _host_io_facilities, r_bootstrap


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_recovery_allocation_epoch_strictly_above_durable_prior(mode: Any, endpoint: str) -> None:
    """A fresh-process restart allocates ONE owner whose
    epoch is strictly above the recorded prior epoch (no
    burn / re-acquire), and a later re-acquire in the same
    registry stays strictly above BOTH the registry counter
    and a larger durable floor."""
    ns, _state, _result, _owner = _genuine_owner(mode, endpoint)
    registry = RamStateOwnerRegistry()
    owner = registry.acquire_new_with_epoch_floor(ns, floor=1)
    assert owner.epoch == 2  # max(0, 1) + 1: strictly above the prior
    owner.teardown(ns)
    owner2 = registry.acquire_new_with_epoch_floor(ns, floor=5)
    assert owner2.epoch == 6  # max(1, 5) + 1: strictly above BOTH
    # A value-equal foreign copy cannot mint a second live
    # owner while one is live (the duplicate refusal precedes
    # any identity join).
    with pytest.raises(RamStateDuplicateOwnerError):
        registry.acquire_new_with_epoch_floor(ns.model_copy(), floor=9)
    assert registry.get(ns) is owner2


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_recovery_allocation_refuses_duplicate_live_owner(mode: Any, endpoint: str) -> None:
    """A live registered owner for the identity refuses the
    strict recovery allocation (registered and value-equal
    forms alike); the registered owner stays untouched and
    the idempotent join law of ``acquire`` is preserved."""
    ns, _state, _result, _ = _genuine_owner(mode, endpoint)
    registry = RamStateOwnerRegistry()
    live = registry.acquire(ns)
    with pytest.raises(RamStateDuplicateOwnerError):
        registry.acquire_new_with_epoch_floor(ns, floor=live.epoch)
    with pytest.raises(RamStateDuplicateOwnerError):
        registry.acquire_new_with_epoch_floor(ns.model_copy(), floor=live.epoch)
    assert registry.get(ns) is live
    assert live.epoch == 1


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_normal_acquisition_epoch_law_unchanged(mode: Any, endpoint: str) -> None:
    """The normal ``acquire`` / ``new_owner`` allocation law
    (monotone distinct epochs, idempotent join) is preserved
    by the new seam, and the seam's floor / namespace
    boundaries refuse with the fixed typed errors."""
    ns, _state, _result, _owner = _genuine_owner(mode, endpoint)
    registry = RamStateOwnerRegistry()
    first = registry.acquire(ns)
    assert first.epoch == 1
    assert registry.acquire(ns) is first  # the idempotent join
    first.teardown(ns)
    second = registry.acquire(ns)
    assert second.epoch == 2  # DISTINCT, never reused
    with pytest.raises(RamStateInputError):
        registry.acquire_new_with_epoch_floor(ns, floor=0)
    with pytest.raises(RamStateInputError):
        registry.acquire_new_with_epoch_floor(ns, floor=True)
    with pytest.raises(RamStateInputError):
        registry.acquire_new_with_epoch_floor(ns.model_construct(), floor=2)
    assert registry.get(ns) is second


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_fresh_registry_restart_never_reuses_prior_epoch(mode: Any, endpoint: str) -> None:
    """The restart law across processes: a FRESH registry
    (the counter starts over) allocates strictly above the
    prior epoch carried by the durable record, never
    alternating or reusing recorded epochs."""
    ns, _state, _result, owner = _genuine_owner(mode, endpoint)
    prior = owner.epoch  # the epoch a checkpoint would record
    assert prior == 1
    fresh = RamStateOwnerRegistry()
    restarted = fresh.acquire_new_with_epoch_floor(ns, floor=prior)
    assert restarted.epoch == prior + 1
    assert restarted.epoch > prior


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_recovery_transient_cold_restore_bounded_by_configured_session_ceiling(
    mode: Any, endpoint: str
) -> None:
    """With NO live owner (the cold-restore case), the
    reservation is refused BEFORE allocation under the
    configured registry session ceiling (first-over
    boundary); a refusal leaves every counter
    unchanged; a fitting reservation is released
    exactly (no underflow, no double release); and a
    NEW owner's base must fit the SAME ceiling
    together with the session's pre-reserved
    transient (the allocation first-over boundary)."""
    ns, _s, _r, _o = _genuine_owner(mode, endpoint)
    registry = RamStateOwnerRegistry()
    baseline = registry.process_owned_bytes
    cap = registry.bounds.session_max_owned_bytes
    # First-over: the configured session ceiling + 1.
    with pytest.raises(RamStateCapacityError):
        registry.reserve_recovery_transient(ns, cap + 1)
    assert registry.process_owned_bytes == baseline
    # A fitting reservation commits; a second reservation
    # of the SAME session then crosses the session ceiling.
    registry.reserve_recovery_transient(ns, cap)
    assert registry.process_owned_bytes == baseline + cap
    with pytest.raises(RamStateCapacityError):
        registry.reserve_recovery_transient(ns, 1)
    assert registry.process_owned_bytes == baseline + cap
    registry.release_recovery_transient(ns, cap)
    assert registry.process_owned_bytes == baseline
    # No underflow: a double release refuses.
    with pytest.raises(RamStateInputError):
        registry.release_recovery_transient(ns, 1)
    # The NEW owner's base must fit the same ceiling
    # together with the pre-reserved transient.
    base_charge = ram_owner_base_charge(ns)
    assert base_charge >= 1
    # First-over at allocation: base + reserved = cap + 1.
    registry.reserve_recovery_transient(ns, cap - base_charge + 1)
    with pytest.raises(RamStateCapacityError):
        registry.acquire_new_with_epoch_floor(ns, floor=1)
    assert registry.get(ns) is None
    # The control: a reservation leaving exactly the base
    # headroom fits (base + reserved = cap).
    registry.release_recovery_transient(ns, cap - base_charge + 1)
    registry.reserve_recovery_transient(ns, cap - base_charge)
    allocated = registry.acquire_new_with_epoch_floor(ns, floor=1)
    # The refused attempt above consumed its epoch (the
    # allocation counter is never rolled back; epochs are
    # never reused), so this allocation continues the
    # sequence at 3.
    assert allocated.epoch == 3
    with_owner = registry.process_owned_bytes
    registry.release_recovery_transient(ns, cap - base_charge)
    assert registry.process_owned_bytes == with_owner - (cap - base_charge)
    allocated.teardown(ns)
    # The owner charge is released; the retained table
    # high-water stays (retained container metadata,
    # never released session state).
    assert registry.process_owned_bytes < with_owner
    assert registry.process_owned_bytes >= baseline


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_recovery_transient_live_owner_identity_join_and_session_boundary(
    mode: Any, endpoint: str
) -> None:
    """With a LIVE registered owner, the seam joins the
    registered namespace with the SAME identity law as
    ``get`` / ``acquire`` (a value-equal foreign copy
    carrying the registered lineage key is refused on
    reserve AND release), the bound owner's session
    ceiling bounds the reservation at the exact
    first-over boundary, and once the owner is
    fenced / retired the join no longer gates the
    session's reserve / release."""
    ns, _s, _r, _o = _genuine_owner(mode, endpoint)
    registry = RamStateOwnerRegistry()
    base = ram_owner_base_charge(ns)
    strict = registry.new_owner(ns, session_max_owned_bytes=base + 1024)
    foreign = ns.model_copy()
    # The identity join refuses the foreign copy.
    with pytest.raises(RamStateInputError):
        registry.reserve_recovery_transient(foreign, 1024)
    with pytest.raises(RamStateInputError):
        registry.release_recovery_transient(foreign, 1024)
    # Exact boundary: base + 1024 = the strict ceiling.
    before = registry.process_owned_bytes
    registry.reserve_recovery_transient(ns, 1024)
    assert registry.process_owned_bytes == before + 1024
    # First-over with the boundary already reserved.
    with pytest.raises(RamStateCapacityError):
        registry.reserve_recovery_transient(ns, 1)
    assert registry.process_owned_bytes == before + 1024
    registry.release_recovery_transient(ns, 1024)
    assert registry.process_owned_bytes == before
    # Once the owner is fenced / retired, the same
    # session's reserve / release is no longer gated by
    # the live-owner join.
    strict.teardown(ns)
    registry.reserve_recovery_transient(foreign, 1024)
    registry.release_recovery_transient(foreign, 1024)
    assert registry.get(ns) is None


def _session_chain(
    mode: Any,
    endpoint: str,
    identity: RequestIdentity,
    lineage: str,
    observation_bounds: Any = None,
) -> tuple[Any, Any, RootRegionAdmissionResult, Any, RecoveryRecord]:
    """The genuine accepted chain ending in ONE closed
    recovery record for a session with the given trusted
    identity: (ns, state, result, owner, record).  The
    explicit legal (NON-DEFAULT) 1048576 GraphBounds stage
    instance is the accepted 018-t stage configuration,
    labeled as such; an explicitly supplied legal
    (NON-DEFAULT) ObservationBounds setting is the
    accepted fixture configuration, labeled by the
    caller."""
    ns, s0 = r_bootstrap(
        mode,
        lineage,
        identity=identity,
        root_body=L1_V1,
        graph_bounds=L1_LEGAL_STAGE,
        observation_bounds=observation_bounds,
    )
    state = _l1_dep_read(s0, ns, "a", endpoint, "A.md", "Follow `X.md`.\n")
    state = _l1_dep_read(state, ns, "x", endpoint, "X.md", "Follow `Target.md`.\n")
    state = _l1_dep_read(state, ns, "t", endpoint, "Target.md", "Synthetic target governance.\n")
    result = derive_root_region_admission(state, ns)
    assert result.outcome is RootRegionAdmissionOutcome.READY, result.diagnostics
    registry = RamStateOwnerRegistry()
    owner = registry.acquire(ns)
    admitted = owner.admit(state, result, ns, expected_revision=0)
    assert admitted.outcome is RamStateOutcome.ADMITTED, admitted
    return ns, state, result, owner, RecoveryRecord.from_owner(owner)


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
async def test_resume_one_dormant_session_from_trusted_address(
    mode: Any, endpoint: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The ACTUAL resume over the protected store
    (requirement 5): TWO genuine sessions are persisted
    under DISTINCT trusted stable addresses; exactly ONE is
    resumed from its trusted address alone (the resume
    input is the registry, the store and the address -- no
    source, root or surviving virtual reference); the
    restored ACTUAL P/T is admitted in a live epoch
    strictly above the durable prior; the recovered owner
    keeps the exclusive writer for its WHOLE live
    lifetime; the needed current keys are prepared LAZILY
    through the ACTUAL 019-b work plane (needed keys only,
    once each, none eagerly); repeated RAM hits perform no
    host IO (the closed 24-facility trap); and the
    composed teardown releases the writer only AFTER the
    store owner is gone (a later resume allocates a
    strictly higher epoch).  The other session stays
    dormant: it is never resumed, never rebuilt and its
    committed generation is untouched."""
    identity_a = RequestIdentity(
        principal="resume-a-principal",
        session="resume-a-session",
        repository="resume-a-repo",
        route="resume-a-route",
    )
    identity_b = RequestIdentity(
        principal="resume-b-principal",
        session="resume-b-session",
        repository="resume-b-repo",
        route="resume-b-route",
    )
    ns_a, _st_a, res_a, _ow_a, rec_a = _session_chain(
        mode, endpoint, identity_a, "resume-lineage-a"
    )
    ns_b, _st_b, _res_b, _ow_b, rec_b = _session_chain(
        mode, endpoint, identity_b, "resume-lineage-b"
    )
    address_a = RecoverySessionAddress.from_namespace(ns_a)
    address_b = RecoverySessionAddress.from_namespace(ns_b)
    assert address_a != address_b
    assert session_directory_name(address_a) != session_directory_name(address_b)
    root = _prepared_root(tmp_path)
    store = RecoveryStore(root)
    # Persist BOTH sessions (dormant; no live owner anywhere):
    for address, record in ((address_a, rec_a), (address_b, rec_b)):
        sess = store.open_session(address)
        try:
            pub = sess.publish(record, expected_generation=0)
            assert pub.limitation is RecoveryStoreLimitation.OK
            assert pub.generation == 1
            assert sess.current_generation() == 1
        finally:
            sess.close()
    # Resume EXACTLY ONE, from the trusted address alone,
    # into a work-enabled registry:
    registry = _work_registry()
    resumed = resume_session(registry, store, address_a)
    assert resumed.outcome is RecoveryResumeOutcome.RESUMED
    assert resumed.prior_epoch == 1
    assert resumed.new_epoch == 2  # strictly above the durable prior
    # The DURABLE epoch binding was published under the
    # bound-generation CAS before the owner was exposed
    # (every other durable field verbatim):
    assert resumed.generation == 2
    owner = resumed.owner
    assert owner is not None
    assert owner.epoch == resumed.new_epoch
    t = resumed.t_result
    assert t is not None
    # The restored ACTUAL T equals the genuine one (the
    # P/D record set re-derived through the accepted law):
    assert t.outcome is RootRegionAdmissionOutcome.READY
    assert t.admission == res_a.admission
    k_root = _root_content_key(t)
    assert owner.lookup(k_root, owner.namespace).outcome is RamStateOutcome.FOUND
    # The live recovery owner retains the writer session:
    rec_owner = resumed.recovery
    assert rec_owner is not None
    assert rec_owner.owner is owner
    assert rec_owner.bound_generation == 2  # the epoch binding
    assert rec_owner.prior_epoch == 1
    assert rec_owner.new_epoch == 2
    assert rec_owner.closed is False
    # The other session stays dormant in the SAME registry:
    assert registry.get(ns_b) is None
    # While the recovered owner is live, the session keeps
    # its exclusive writer: any second open (even this
    # very process) is a typed conflict, never a second
    # owner:
    with pytest.raises(RecoveryStoreError) as exc_info:
        store.open_session(address_a)
    assert exc_info.value.limitation is RecoveryStoreLimitation.WRITER_CONFLICT
    # The needed current keys are prepared LAZILY through
    # the ACTUAL 019-b work plane: the resume itself
    # performed NO seam invocation, and each key is
    # prepared exactly once, only when demanded:
    work = registry.work
    assert work is not None
    calls: list[int] = []
    seam = _lifecycle_seam(calls)
    assert calls == []
    r0 = await work.resolve(owner.namespace, k_root, seam)
    assert r0.outcome is RamWorkOutcome.COMPLETED
    assert r0.payload is not None
    assert r0.invocations == 1
    assert len(calls) == 1
    k_a = _path_key(t, "A.md")
    r_a = await work.resolve(owner.namespace, k_a, seam)
    assert r_a.outcome is RamWorkOutcome.COMPLETED
    assert r_a.payload is not None
    assert r_a.payload is not r0.payload
    assert r_a.invocations == 1
    assert len(calls) == 2
    # Mechanically denied host IO: repeated usable owner
    # lookups and repeated RAM-only work hits of the
    # retained payloads run under the closed 24-facility
    # trap with ZERO content reads and ZERO new seam
    # invocations (the normal hit path is RAM-only; the
    # dormant session's files are never touched):
    io_calls: list[str] = []

    def trap(label: str) -> Callable[..., Any]:
        def refused(*trap_args: Any, **trap_kwargs: Any) -> Any:
            io_calls.append(label)
            raise AssertionError("forbidden host IO: " + label)

        return refused

    with monkeypatch.context() as scoped_patch:
        for module, name in _host_io_facilities():
            scoped_patch.setattr(module, name, trap(module.__name__ + "." + name))
        for key in (k_root, k_a):
            assert owner.lookup(key, owner.namespace).outcome is RamStateOutcome.FOUND
        h1 = await work.resolve(owner.namespace, k_root, seam)
        assert h1.outcome is RamWorkOutcome.HIT
        assert h1.payload is r0.payload
        assert h1.invocations == 0
        assert len(calls) == 2
        assert io_calls == []
    # The composed teardown: the work plane drains and
    # releases store + work in ONE critical section, and
    # the writer closes only AFTER the store owner is
    # gone:
    td = await rec_owner.teardown()
    assert td.outcome is RecoveryTeardownOutcome.TEARDOWN
    assert td.session_closed is True
    assert td.store is None
    assert td.work is not None
    assert td.work.outcome is RamWorkOutcome.TEARDOWN
    assert registry.get(owner.namespace) is None
    r_after = await work.resolve(owner.namespace, k_root, seam)
    assert r_after.outcome is RamWorkOutcome.REFUSED
    assert r_after.limitation is RamWorkLimitation.OWNER_ABSENT
    assert r_after.invocations == 0
    assert len(calls) == 2
    # The writer lock is released (the session opens
    # again) with the epoch binding committed (the work-
    # plane preparation never rewrote the checkpoint):
    sess = store.open_session(address_a)
    try:
        assert sess.current_generation() == 2
    finally:
        sess.close()
    # The FRESH-registry restart (the in-process component
    # equivalent of a fresh process): strictly above the
    # DURATION epoch binding, never reusing a torn-down
    # incarnation's epoch -- the same-registry counter
    # alone would mask a durable epoch reuse:
    fresh = _work_registry()
    again = resume_session(fresh, store, address_a)
    assert again.outcome is RecoveryResumeOutcome.RESUMED
    assert again.prior_epoch == 2
    assert again.new_epoch == 3
    assert again.owner is not None
    assert again.owner.epoch == 3
    assert again.generation == 3  # the next durable binding
    again_recovery = again.recovery
    assert again_recovery is not None
    td2 = await again_recovery.teardown()
    assert td2.outcome is RecoveryTeardownOutcome.TEARDOWN
    assert td2.session_closed is True


def _changed_root_candidate(
    state: Any, ns: Any, endpoint: str, root_body: str = L4C2_ROOT
) -> tuple[Any, RootRegionAdmissionResult]:
    """A genuine ADVERSE candidate: a NEW whole root read
    that REKEYS the retained current rows (READY yet
    withdrawing / rekeying them -- the 019-c adverse
    classifier; ``root_body`` is the legal whole-root
    source of that read (a legal root at its own byte
    length stays legal under the closed root-source
    byte domain)."""
    s_root2 = _l1_dep_read(state, ns, "root2", endpoint, ROOT_FILENAME, root_body)
    t2 = derive_root_region_admission(s_root2, ns)
    assert t2.outcome is RootRegionAdmissionOutcome.READY, t2.diagnostics
    return s_root2, t2


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
async def test_admit_with_fence_pre_pointer_fault_keeps_prior_generation_valid(
    mode: Any, endpoint: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Fence fault BEFORE pointer publication: the
    validated adverse candidate's durable fence fails at
    the checkpoint fsync (the first fsync of the fence
    publish); the transition is refused typed
    ``fence_refused`` and -- because NO admit, NO state
    mutation and NO quarantine occurred -- the prior
    committed generation remains valid: the retained
    current rows stay usable (lookup / work HIT, zero new
    invocations), the bound generation is unchanged and
    the ACTUAL observed generation (the untouched
    pointer) is carried, not assumed."""
    identity = RequestIdentity(
        principal="fence-pre-principal",
        session="fence-pre-session",
        repository="fence-pre-repo",
        route="fence-pre-route",
    )
    ns, state, result, _owner, record = _session_chain(
        mode, endpoint, identity, "fence-pre-lineage"
    )
    address = RecoverySessionAddress.from_namespace(ns)
    store = RecoveryStore(_prepared_root(tmp_path))
    sess = store.open_session(address)
    try:
        pub = sess.publish(record, expected_generation=0)
        assert pub.limitation is RecoveryStoreLimitation.OK
        assert pub.generation == 1
    finally:
        sess.close()
    registry = _work_registry()
    resumed = resume_session(registry, store, address)
    assert resumed.outcome is RecoveryResumeOutcome.RESUMED
    owner = resumed.owner
    assert owner is not None
    rec_owner = resumed.recovery
    assert rec_owner is not None
    assert rec_owner.bound_generation == 2
    work = registry.work
    assert work is not None
    t = resumed.t_result
    assert t is not None
    k_root = _root_content_key(t)
    k_a = _path_key(t, "A.md")
    calls: list[int] = []
    seam = _lifecycle_seam(calls)
    r0 = await work.resolve(owner.namespace, k_root, seam)
    assert r0.outcome is RamWorkOutcome.COMPLETED
    assert r0.payload is not None
    assert len(calls) == 1
    snap = owner.snapshot
    assert snap is not None
    s_root2, t2 = _changed_root_candidate(snap.state, owner.namespace, endpoint)
    admission2 = t2.admission
    assert admission2 is not None
    assert admission2.root_entry.content_key != k_root  # the candidate rekeys
    # The injected fault: the fence checkpoint's fsync
    # (the FIRST fsync of the fence publish) fails before
    # any pointer publication:
    fsync_seen: list[int] = []
    real_fsync = os.fsync

    def flaky_fsync(fd: int) -> None:
        fsync_seen.append(fd)
        if len(fsync_seen) == 1:
            raise OSError("injected fence checkpoint fsync failure")
        real_fsync(fd)

    with monkeypatch.context() as scoped_patch:
        scoped_patch.setattr(os, "fsync", flaky_fsync)
        fr = rec_owner.admit_with_fence(s_root2, t2, expected_revision=owner.revision)
    assert fr.outcome is RecoveryAdmitOutcome.FENCE_REFUSED
    assert fr.admitted is None
    assert fr.advance is None
    assert fr.fence is not None
    assert fr.fence.limitation is RecoveryStoreLimitation.IO_FAILURE
    assert fr.fence.actual_generation == 2  # ACTUAL observed: pointer untouched
    assert fr.bound_generation == 2
    assert fr.owner_quarantined is False
    # The prior committed generation remains valid: no
    # admit, no mutation, no quarantine -- the retained
    # current rows stay usable:
    assert owner.quarantined is False
    assert owner.revision == 1
    assert owner.lookup(k_root, owner.namespace).outcome is RamStateOutcome.FOUND
    assert owner.lookup(k_a, owner.namespace).outcome is RamStateOutcome.FOUND
    r_hit = await work.resolve(owner.namespace, k_root, seam)
    assert r_hit.outcome is RamWorkOutcome.HIT
    assert r_hit.payload is r0.payload
    assert r_hit.invocations == 0 and len(calls) == 1
    td = await rec_owner.teardown()
    assert td.outcome is RecoveryTeardownOutcome.TEARDOWN
    assert td.session_closed is True


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
async def test_admit_with_fence_post_rename_fault_fails_closed_on_restart(
    mode: Any, endpoint: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Fence fault AFTER the pointer rename: the fence
    generation may already be COMMITTED while directory
    durability is unconfirmed; the transition is refused
    typed ``fence_refused`` with the ACTUAL observed
    generation carried (the new fence generation, the old
    bound NOT assumed); no admit occurred, so the live
    current rows stay usable -- but the live owner cannot
    overwrite the committed fence (a later checkpoint is
    the fixed generation-mismatch refusal, never a silent
    unfence), the explicit teardown is the exit, and the
    restart fails closed on the committed fence (the old
    usable bytes never resume)."""
    identity = RequestIdentity(
        principal="fence-post-principal",
        session="fence-post-session",
        repository="fence-post-repo",
        route="fence-post-route",
    )
    ns, state, result, _owner, record = _session_chain(
        mode, endpoint, identity, "fence-post-lineage"
    )
    address = RecoverySessionAddress.from_namespace(ns)
    store = RecoveryStore(_prepared_root(tmp_path))
    sess = store.open_session(address)
    try:
        pub = sess.publish(record, expected_generation=0)
        assert pub.limitation is RecoveryStoreLimitation.OK
        assert pub.generation == 1
    finally:
        sess.close()
    registry = _work_registry()
    resumed = resume_session(registry, store, address)
    assert resumed.outcome is RecoveryResumeOutcome.RESUMED
    owner = resumed.owner
    assert owner is not None
    rec_owner = resumed.recovery
    assert rec_owner is not None
    assert rec_owner.bound_generation == 2
    work = registry.work
    assert work is not None
    t = resumed.t_result
    assert t is not None
    k_root = _root_content_key(t)
    calls: list[int] = []
    seam = _lifecycle_seam(calls)
    r0 = await work.resolve(owner.namespace, k_root, seam)
    assert r0.outcome is RamWorkOutcome.COMPLETED
    assert len(calls) == 1
    snap = owner.snapshot
    assert snap is not None
    s_root2, t2 = _changed_root_candidate(snap.state, owner.namespace, endpoint)
    admission2 = t2.admission
    assert admission2 is not None
    assert admission2.root_entry.content_key != k_root  # the candidate rekeys
    # The injected fault: the DIRECTORY fsync AFTER the
    # pointer rename fails (the third fsync of the fence
    # publish) -- the rename is already committed:
    fsync_seen: list[int] = []
    real_fsync = os.fsync

    def flaky_fsync(fd: int) -> None:
        fsync_seen.append(fd)
        if len(fsync_seen) == 3:
            raise OSError("injected fence directory fsync failure")
        real_fsync(fd)

    with monkeypatch.context() as scoped_patch:
        scoped_patch.setattr(os, "fsync", flaky_fsync)
        fr = rec_owner.admit_with_fence(s_root2, t2, expected_revision=owner.revision)
    assert fr.outcome is RecoveryAdmitOutcome.FENCE_REFUSED
    assert fr.admitted is None
    assert fr.advance is None
    assert fr.fence is not None
    assert fr.fence.limitation is RecoveryStoreLimitation.IO_FAILURE
    assert fr.fence.actual_generation == 3  # the COMMITTED fence generation, observed
    assert fr.bound_generation == 2  # the bound did not advance (publish not OK)
    # No admit occurred: the live current rows stay
    # usable...
    assert owner.quarantined is False
    assert owner.revision == 1
    assert owner.lookup(k_root, owner.namespace).outcome is RamStateOutcome.FOUND
    r_hit = await work.resolve(owner.namespace, k_root, seam)
    assert r_hit.outcome is RamWorkOutcome.HIT
    assert r_hit.invocations == 0 and len(calls) == 1
    # ...but the live owner cannot overwrite the committed
    # fence (never a silent unfence):
    ckpt = rec_owner.checkpoint_current()
    assert ckpt.limitation is RecoveryStoreLimitation.GENERATION_MISMATCH
    assert ckpt.actual_generation == 3
    # The explicit teardown is the exit; the restart then
    # fails closed on the committed fence:
    td = await rec_owner.teardown()
    assert td.outcome is RecoveryTeardownOutcome.TEARDOWN
    assert td.session_closed is True
    assert registry.get(owner.namespace) is None
    fresh = _work_registry()
    q = resume_session(fresh, store, address)
    assert q.outcome is RecoveryResumeOutcome.QUARANTINE_PERSISTED
    assert q.generation == 3
    assert q.prior_epoch == 2
    assert q.owner is None
    assert q.recovery is None


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
async def test_capacity_quarantine_fence_persists_through_durability(
    mode: Any, endpoint: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Requirement 5 strict path: the VALIDATED adverse
    candidate whose durable fence publishes OK but whose
    ADMISSION is capacity-refused QUARANTINES the owner
    (the 019-c adverse classifier) and RETAINS the durable
    fence (durable and in-memory agree).  The crossing is
    a genuine PROCESS-ceiling crossing under a fixed
    finite configured process ceiling, exercised with the
    019 aggregate-pressure pattern: the fence completes
    FIRST, then a deterministic competing OWNED
    reservation for another genuine namespace -- taken
    after the real fence publication and held only while
    the REAL admission decides -- exhausts the process
    headroom just short of the genuine candidate's delta,
    so the ACTUAL process capacity check refuses the
    candidate with the fixed typed 503.  The owner limit
    and every 018 source / observation bound stay at
    their accepted defaults (the baseline is the normal
    32768-byte fixture and the candidate the NORMAL small
    changed root).  The ceiling is configured from ONE
    throwaway resume incarnation over the SAME record:
    the ACTUAL resume-flow restored baseline, the ACTUAL
    in-flight pre-load transient at the committed size,
    the ACTUAL fence publication reserve at that baseline
    and the genuine candidate delta are all MEASURED, and
    the preconditions (baseline + in-flight transient fit
    and the measured gap below the candidate delta) are
    asserted on the measured values; the competing
    reservation is then chosen from the ACTUAL post-
    resume process counters (retained owner-map growth
    included) to leave exactly that gap.
    The proof then runs on the REAL resumed owner: its
    ACTUAL baseline fits, the ACTUAL process total at the
    decision (post-resume baseline + competing
    reservation) plus the candidate charge crosses the
    configured limit while the candidate alone does not,
    the old
    usable lookups refuse with the fixed typed
    currentness refusal, and the fence persists THROUGH
    durability -- after the explicit teardown (the only
    exit) a fresh registry resume of the session fails
    closed (QUARANTINE_PERSISTED): the older usable bytes
    never resume, no automatic unquarantine, no retry.
    The competing reservation is released in the finally
    around the real admission (the process total returns
    to shell + baseline)."""
    identity = RequestIdentity(
        principal="fence-cap-principal",
        session="fence-cap-session",
        repository="fence-cap-repo",
        route="fence-cap-route",
    )
    other_identity = RequestIdentity(
        principal="fence-cap-other-principal",
        session="fence-cap-other-session",
        repository="fence-cap-other-repo",
        route="fence-cap-other-route",
    )
    ns, _state, _result, _owner, record = _session_chain(
        mode, endpoint, identity, "fence-cap-lineage"
    )
    address = RecoverySessionAddress.from_namespace(ns)
    # Configuration estimation (NOT the proof): ONE
    # throwaway resume incarnation over the SAME record
    # measures the ACTUAL resume-flow restored baseline,
    # the ACTUAL in-flight pre-load transient at the
    # committed size, the ACTUAL fence publication
    # reserve at that baseline and the genuine candidate
    # delta on those same retained objects:
    (tmp_path / "probe").mkdir(mode=0o700)
    probe_store = RecoveryStore(_prepared_root(tmp_path / "probe"))
    psess = probe_store.open_session(address)
    try:
        ppub = psess.publish(record, expected_generation=0)
        assert ppub.limitation is RecoveryStoreLimitation.OK
        assert ppub.generation == 1
        # The ACTUAL committed record size (what the
        # live resume's pre-load probe reads; the live
        # store publishes the SAME record bytes):
        committed_p = psess.committed_record_bytes()
    finally:
        psess.close()
    assert committed_p > 0
    pre_reserve_p = max(4 * committed_p, RECOVERY_TRANSIENT_FLOOR_BYTES)
    probe = resume_session(RamStateOwnerRegistry(), probe_store, address)
    assert probe.outcome is RecoveryResumeOutcome.RESUMED
    p_owner = probe.owner
    assert p_owner is not None
    p_snap = p_owner.snapshot
    assert p_snap is not None
    charge_p = p_owner.owned_bytes
    # The genuine ADVERSE candidate: the NORMAL small
    # changed root (the retained delta is measured on the
    # probe owner, never sized to a bound):
    s_root2_p, cand_p = _changed_root_candidate(p_snap.state, p_owner.namespace, endpoint)
    p_adm = p_owner.admit(s_root2_p, cand_p, p_owner.namespace, expected_revision=1)
    assert p_adm.outcome is RamStateOutcome.ADMITTED
    delta_p = p_owner.owned_bytes - charge_p
    assert delta_p > 0
    p_recovery = probe.recovery
    assert p_recovery is not None
    p_td = await p_recovery.teardown()
    assert p_td.outcome is RecoveryTeardownOutcome.TEARDOWN
    # The genuinely configured finite PROCESS ceiling:
    # the measured registry shell plus the measured
    # baseline plus headroom above both; the headroom
    # covers the ACTUAL in-flight pre-load transient (the
    # epoch binding publishes under the SAME held
    # transient, no top-up) and the ACTUAL fence
    # publication reserve at that baseline (the closed
    # conservative 24x bound of the live publication
    # path), with margin:
    fence_reserve_p = max(
        24 * (charge_p + RECOVERY_TRANSIENT_FLOOR_BYTES),
        RECOVERY_TRANSIENT_FLOOR_BYTES,
    )
    headroom_p = max(pre_reserve_p, fence_reserve_p) + 262144
    # Preconditions on the MEASURED values: the resumed
    # baseline admit (and the epoch binding under the
    # SAME held transient) must fit, and the genuine
    # candidate delta must be real (the competing
    # reservation will leave LESS than it -- the ACTUAL
    # crossing):
    assert pre_reserve_p <= headroom_p
    gap_p = max(1, delta_p // 2)
    assert gap_p < delta_p
    # The FIXED finite ceiling (measured terms + margin;
    # the retained owner-map growth at the live
    # registry's allocation is covered by the margin):
    shell_p = RamStateOwnerRegistry().process_owned_bytes
    process_max = shell_p + charge_p + headroom_p
    (tmp_path / "live").mkdir(mode=0o700)
    store = RecoveryStore(_prepared_root(tmp_path / "live"))
    sess = store.open_session(address)
    try:
        pub = sess.publish(record, expected_generation=0)
        assert pub.limitation is RecoveryStoreLimitation.OK
        assert pub.generation == 1
    finally:
        sess.close()
    registry = RamStateOwnerRegistry(
        bounds=RamStateBounds(
            session_max_owned_bytes=process_max,
            process_max_owned_bytes=process_max,
        )
    )
    resumed = resume_session(registry, store, address)
    assert resumed.outcome is RecoveryResumeOutcome.RESUMED
    assert resumed.prior_epoch == 1
    assert resumed.new_epoch == 2
    assert resumed.generation == 2
    owner = resumed.owner
    assert owner is not None
    assert owner.owned_bytes == charge_p  # the ACTUAL measured baseline
    assert owner.owned_bytes < process_max  # the ACTUAL baseline fits
    rec_owner = resumed.recovery
    assert rec_owner is not None
    assert rec_owner.bound_generation == 2
    # The ACTUAL post-resume process total (retained
    # owner-map growth included) is the pressure
    # baseline; the competing reservation is chosen from
    # these ACTUAL counters to leave exactly the measured
    # gap (strictly below the candidate delta):
    baseline = registry.process_owned_bytes
    assert process_max - baseline > gap_p  # the ACTUAL headroom covers it
    competing_p = process_max - baseline - gap_p
    assert competing_p >= 1
    t = resumed.t_result
    assert t is not None
    k_root = _root_content_key(t)
    k_a = _path_key(t, "A.md")
    assert owner.lookup(k_root, owner.namespace).outcome is RamStateOutcome.FOUND
    assert owner.lookup(k_a, owner.namespace).outcome is RamStateOutcome.FOUND
    # The competing reservation's home: another genuine
    # accepted namespace (a real bootstrap scope for a
    # different session; the reservation seam joins it
    # under the complete namespace law):
    other_ns, _other_state = r_bootstrap(
        mode,
        "fence-cap-other-lineage",
        identity=other_identity,
        root_body=L1_V1,
        graph_bounds=L1_LEGAL_STAGE,
    )
    assert other_ns.lineage_key != ns.lineage_key
    # The genuine ADVERSE candidate, from the REAL
    # owner's retained originals (the NORMAL small
    # changed root):
    snap = owner.snapshot
    assert snap is not None
    s_root2, cand = _changed_root_candidate(snap.state, owner.namespace, endpoint)
    cand_admission = cand.admission
    assert cand_admission is not None
    assert cand_admission.root_entry.content_key != k_root  # the candidate rekeys
    # The deterministic 019 aggregate-pressure barrier:
    # the competing owned reservation for the other
    # genuine namespace is taken AFTER the real fence
    # publication and held only while the REAL
    # admission decides (released in the finally):
    original_admit = RamStateOwner.admit
    hook_events: list[tuple[str, int]] = []

    def competing_headroom_hook(
        self: RamStateOwner,
        state: Any,
        result: Any,
        namespace: Any,
        *,
        expected_revision: int,
    ) -> Any:
        # The barrier targets ONLY the resumed owner;
        # every other owner's admission is forwarded
        # unchanged:
        if self is not owner:
            return original_admit(
                self, state, result, namespace, expected_revision=expected_revision
            )
        try:
            registry.reserve_recovery_transient(other_ns, competing_p)
            hook_events.append(("reserved", registry.process_owned_bytes))
            return original_admit(
                self, state, result, namespace, expected_revision=expected_revision
            )
        finally:
            registry.release_recovery_transient(other_ns, competing_p)
            hook_events.append(("released", registry.process_owned_bytes))

    monkeypatch.setattr(RamStateOwner, "admit", competing_headroom_hook)
    # The fenced transition on the REAL owner: the fence
    # publishes, the admission is ACTUALLY
    # process-capacity-refused (the ACTUAL process total
    # at the decision crosses the configured limit) and
    # QUARANTINES, and the fence is RETAINED (durable and
    # in-memory agree):
    fr = rec_owner.admit_with_fence(s_root2, cand, expected_revision=owner.revision)
    assert fr.outcome is RecoveryAdmitOutcome.REFUSED
    assert fr.fence is not None
    assert fr.fence.limitation is RecoveryStoreLimitation.OK
    assert fr.fence.generation == 3
    assert fr.admitted is not None
    assert fr.admitted.outcome is RamStateOutcome.REFUSED
    assert fr.admitted.limitation is RamStateLimitation.PROCESS_OWNED_BYTES_OVER_BOUND
    assert fr.admitted.http_status == 503
    # The ACTUAL process crossing at the decision: the
    # carried process total (post-resume baseline + the
    # held competing reservation) plus the candidate
    # charge crosses the configured limit -- while the
    # same total WITHOUT the competing reservation does
    # not (the crossing is the pressure, not the
    # candidate size):
    assert fr.admitted.process_owned_bytes == baseline + competing_p
    assert (
        fr.admitted.process_owned_bytes + (fr.admitted.charged_bytes - owner.owned_bytes)
        > process_max
    )
    assert (
        fr.admitted.process_owned_bytes
        - competing_p
        + (fr.admitted.charged_bytes - owner.owned_bytes)
        <= process_max
    )
    assert fr.admitted.session_owned_bytes == owner.owned_bytes  # state unchanged
    assert fr.advance is None
    assert fr.owner_quarantined is True
    assert fr.bound_generation == 3
    # The competing reservation was held exactly once
    # around the real admission and released in the
    # finally (the process total returns to the ACTUAL
    # post-resume baseline):
    assert hook_events == [
        ("reserved", baseline + competing_p),
        ("released", baseline),
    ]
    assert registry.process_owned_bytes == baseline
    # The old usable lookups refuse (the 019-c currentness
    # refusal; the retained bytes stay charged):
    assert owner.quarantined is True
    for old in (k_root, k_a):
        lk = owner.lookup(old, owner.namespace)
        assert lk.outcome is RamStateOutcome.NOT_FOUND
        assert lk.limitation is RamStateLimitation.OWNER_QUARANTINED
    # The explicit teardown is the only fence exit:
    td = await rec_owner.teardown()
    assert td.outcome is RecoveryTeardownOutcome.TEARDOWN
    assert td.session_closed is True
    assert registry.get(owner.namespace) is None
    # The fence persists THROUGH durability: a fresh
    # registry resume fails closed -- the older usable
    # bytes never resume:
    fresh = RamStateOwnerRegistry()
    q = resume_session(fresh, store, address)
    assert q.outcome is RecoveryResumeOutcome.QUARANTINE_PERSISTED
    assert q.generation == 3
    assert q.prior_epoch == 2
    assert q.owner is None
    assert q.recovery is None


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
async def test_admit_with_fence_adverse_candidate_advances_and_restarts_from_new_state(
    mode: Any, endpoint: str, tmp_path: Path
) -> None:
    """Fenced ADVANCE positive (the default bounds fit both
    publications): the validated adverse candidate first
    publishes the DURABLE fail-closed fence, is then
    ADMITTED, and the durable binding ADVANCES to the new
    record set: the NEW root key is current (FOUND), the
    OLD rekeyed root key is no longer lookup-eligible
    (retained in the historical catalog only), and the
    accepted full-key law rekeys the FILE row under
    the changed governing root scope even with
    unchanged bytes (the NEW A key is current, the
    old A key is not); after the explicit teardown a
    FRESH registry resume of the
    session restores the NEW record set (a distinct epoch
    strictly above the recorded live epoch) -- the
    advanced record set is the durable baseline, never
    the fenced one."""
    identity = RequestIdentity(
        principal="fence-adv-principal",
        session="fence-adv-session",
        repository="fence-adv-repo",
        route="fence-adv-route",
    )
    ns, _state, _result, _owner, record = _session_chain(
        mode, endpoint, identity, "fence-adv-lineage"
    )
    address = RecoverySessionAddress.from_namespace(ns)
    store = RecoveryStore(_prepared_root(tmp_path))
    sess = store.open_session(address)
    try:
        pub = sess.publish(record, expected_generation=0)
        assert pub.limitation is RecoveryStoreLimitation.OK
        assert pub.generation == 1
    finally:
        sess.close()
    registry = RamStateOwnerRegistry()
    resumed = resume_session(registry, store, address)
    assert resumed.outcome is RecoveryResumeOutcome.RESUMED
    assert resumed.generation == 2
    owner = resumed.owner
    assert owner is not None
    rec_owner = resumed.recovery
    assert rec_owner is not None
    t = resumed.t_result
    assert t is not None
    k_root = _root_content_key(t)
    k_a = _path_key(t, "A.md")
    assert owner.lookup(k_root, owner.namespace).outcome is RamStateOutcome.FOUND
    old_admission = t.admission
    assert old_admission is not None
    old_root_entry = old_admission.root_entry
    snap = owner.snapshot
    assert snap is not None
    s_root2, t2 = _changed_root_candidate(snap.state, owner.namespace, endpoint)
    cand_admission = t2.admission
    assert cand_admission is not None
    new_root_key = cand_admission.root_entry.content_key
    assert new_root_key != k_root  # the candidate rekeys the retained root
    fr = rec_owner.admit_with_fence(s_root2, t2, expected_revision=owner.revision)
    assert fr.outcome is RecoveryAdmitOutcome.ADMITTED
    assert fr.fence is not None
    assert fr.fence.limitation is RecoveryStoreLimitation.OK
    assert fr.fence.generation == 3  # the pre-transition fence
    assert fr.admitted is not None
    assert fr.admitted.outcome is RamStateOutcome.ADMITTED
    assert fr.advance is not None
    assert fr.advance.limitation is RecoveryStoreLimitation.OK
    assert fr.advance.generation == 4  # the NEW record set
    assert fr.owner_quarantined is False
    assert fr.bound_generation == 4
    assert owner.quarantined is False
    assert owner.revision == 2
    # The accepted full-key law: the changed governing
    # root scope rekeys the FILE row even with
    # unchanged bytes -- the NEW root and NEW A keys
    # are current, the OLD root and OLD A keys not:
    k_a2 = _path_key(t2, "A.md")
    assert k_a2 != k_a  # the FILE row is rekeyed under the new root scope
    assert owner.lookup(new_root_key, owner.namespace).outcome is RamStateOutcome.FOUND
    assert owner.lookup(k_a2, owner.namespace).outcome is RamStateOutcome.FOUND
    assert owner.lookup(k_root, owner.namespace).outcome is RamStateOutcome.NOT_FOUND
    assert owner.lookup(k_a, owner.namespace).outcome is RamStateOutcome.NOT_FOUND
    # Supersession RETAINS the old root row in the
    # historical catalog (identity, never destroyed):
    assert old_root_entry in owner.history
    # The explicit teardown; a FRESH registry resume of
    # the session restores the NEW record set:
    td = await rec_owner.teardown()
    assert td.outcome is RecoveryTeardownOutcome.TEARDOWN
    assert td.session_closed is True
    assert registry.get(owner.namespace) is None
    fresh = RamStateOwnerRegistry()
    q = resume_session(fresh, store, address)
    assert q.outcome is RecoveryResumeOutcome.RESUMED
    assert q.generation == 5  # the next epoch binding
    assert q.prior_epoch == 2  # the advanced binding carried the live epoch
    assert q.new_epoch == 3  # a DISTINCT epoch, strictly above
    t3 = q.t_result
    assert t3 is not None
    new_admission3 = t3.admission
    assert new_admission3 is not None
    new_root_entry3 = new_admission3.root_entry
    assert new_root_entry3.content_key == new_root_key  # the NEW root is the baseline
    q_owner = q.owner
    assert q_owner is not None
    k_a3 = _path_key(t3, "A.md")
    assert k_a3 == k_a2  # deterministic re-derivation of the rekeyed row
    assert q_owner.lookup(new_root_key, q_owner.namespace).outcome is RamStateOutcome.FOUND
    assert q_owner.lookup(k_a3, q_owner.namespace).outcome is RamStateOutcome.FOUND
    assert q_owner.lookup(k_a, q_owner.namespace).outcome is RamStateOutcome.NOT_FOUND
    q_recovery = q.recovery
    assert q_recovery is not None
    td2 = await q_recovery.teardown()
    assert td2.outcome is RecoveryTeardownOutcome.TEARDOWN
    assert td2.session_closed is True


async def _wait_until(poll: Callable[[], bool], tries: int = 1000) -> bool:
    """Poll on the event loop until ``poll`` is true (or
    the bounded tries elapse); returns the final state."""
    for _ in range(tries):
        if poll():
            return True
        await asyncio.sleep(0.01)
    return poll()


def _held_fsync_barrier(
    monkeypatch: pytest.MonkeyPatch,
) -> tuple[threading.Event, threading.Event]:
    """A bounded global ``os.fsync`` barrier: the FIRST
    fsync after installation signals ``entered`` and
    blocks until ``release`` is set; after release every
    fsync (including the held one) completes for real.
    Returns ``(entered, release)``."""
    entered = threading.Event()
    release = threading.Event()
    real_fsync = os.fsync

    def held_fsync(fd: int) -> None:
        if not release.is_set():
            entered.set()
            release.wait(60)
        real_fsync(fd)

    monkeypatch.setattr(os, "fsync", held_fsync)
    return entered, release


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
async def test_teardown_drains_held_owned_write_before_releasing_writer(
    mode: Any, endpoint: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Teardown admission fence + owned-IO drain
    (requirement 4): a checkpoint held inside fsync keeps
    the teardown PENDING; while teardown is in flight the
    NEW sync / async checkpoint and fenced-admit calls are
    refused with the typed writer conflict (no late
    old-epoch writer can publish after the RAM ownership
    is released); after the held write completes to its
    ACTUAL outcome (generation 3) the teardown finishes
    and a fresh open observes the committed generation."""
    identity = RequestIdentity(
        principal="td-fence-principal",
        session="td-fence-session",
        repository="td-fence-repo",
        route="td-fence-route",
    )
    ns, state, result, _ow, rec = _session_chain(mode, endpoint, identity, "td-fence-lineage")
    address = RecoverySessionAddress.from_namespace(ns)
    root = _prepared_root(tmp_path)
    store = RecoveryStore(root)
    sess = store.open_session(address)
    try:
        pub = sess.publish(rec, expected_generation=0)
        assert pub.limitation is RecoveryStoreLimitation.OK
        assert pub.generation == 1
    finally:
        sess.close()
    registry = _work_registry()
    resumed = resume_session(registry, store, address)
    assert resumed.outcome is RecoveryResumeOutcome.RESUMED
    assert resumed.generation == 2
    owner = resumed.owner
    assert owner is not None
    rec_owner = resumed.recovery
    assert rec_owner is not None
    assert rec_owner.bound_generation == 2
    entered, release = _held_fsync_barrier(monkeypatch)
    cp_task = asyncio.create_task(rec_owner.checkpoint_current_async())
    try:
        assert await asyncio.to_thread(entered.wait, 30)
        td_task = asyncio.create_task(rec_owner.teardown())
        assert await _wait_until(lambda: rec_owner.tearing_down)
        # Teardown is PENDING: it is draining the held
        # owned write and must not finish while it is held:
        for _ in range(200):
            assert not td_task.done()
            await asyncio.sleep(0.01)
        assert not rec_owner.closed
        assert registry.get(owner.namespace) is not None
        # The admission fence refuses NEW operations with
        # the typed writer conflict (nothing starts, no IO,
        # the ACTUAL observed generation is carried):
        fence_sync = rec_owner.checkpoint_current()
        assert fence_sync.limitation is RecoveryStoreLimitation.WRITER_CONFLICT
        assert fence_sync.generation is None
        assert fence_sync.pointer is None
        assert fence_sync.actual_generation == 2
        fence_async = await rec_owner.checkpoint_current_async()
        assert fence_async.limitation is RecoveryStoreLimitation.WRITER_CONFLICT
        assert fence_async.generation is None
        fence_admit = rec_owner.admit_with_fence(state, result, expected_revision=owner.revision)
        assert fence_admit.outcome is RecoveryAdmitOutcome.REFUSED
        assert fence_admit.admitted is None
        assert fence_admit.advance is None
        assert fence_admit.fence is not None
        assert fence_admit.fence.limitation is (RecoveryStoreLimitation.WRITER_CONFLICT)
        assert fence_admit.owner_quarantined is False
        assert fence_admit.bound_generation == 2
        # The writer is still held: a second open is a
        # typed conflict (no fsync on the existing prepared
        # root, so the check is safe while the barrier is
        # held):
        with pytest.raises(RecoveryStoreError) as exc_info:
            store.open_session(address)
        assert exc_info.value.limitation is (RecoveryStoreLimitation.WRITER_CONFLICT)
        # Release the held write: the owned publication
        # completes to its ACTUAL outcome (generation 3)
        # and only then does the teardown finish:
        release.set()
        cp = await cp_task
        assert cp.limitation is RecoveryStoreLimitation.OK
        assert cp.generation == 3
        assert rec_owner.bound_generation == 3
        td = await td_task
        assert td.outcome is RecoveryTeardownOutcome.TEARDOWN
        assert td.session_closed is True
        assert rec_owner.closed is True
        assert registry.get(owner.namespace) is None
        fresh = store.open_session(address)
        try:
            assert fresh.current_generation() == 3
        finally:
            fresh.close()
    finally:
        release.set()


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
async def test_cancelled_teardown_holds_cancellation_until_held_write_completes(
    mode: Any, endpoint: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Repeated cancellation of the teardown task is HELD
    while its owned write is still live (the 019-b drain
    law at this boundary): nothing is released, the fence
    is LIFTED so the owner stays usable, the held write
    completes to its actual outcome, and the cancellation
    propagates only AFTER the drain; a later explicit
    teardown then completes cleanly."""
    identity = RequestIdentity(
        principal="td-hold-principal",
        session="td-hold-session",
        repository="td-hold-repo",
        route="td-hold-route",
    )
    ns, _state, _result, _ow, rec = _session_chain(mode, endpoint, identity, "td-hold-lineage")
    address = RecoverySessionAddress.from_namespace(ns)
    root = _prepared_root(tmp_path)
    store = RecoveryStore(root)
    sess = store.open_session(address)
    try:
        pub = sess.publish(rec, expected_generation=0)
        assert pub.limitation is RecoveryStoreLimitation.OK
        assert pub.generation == 1
    finally:
        sess.close()
    registry = _work_registry()
    resumed = resume_session(registry, store, address)
    assert resumed.outcome is RecoveryResumeOutcome.RESUMED
    assert resumed.generation == 2
    owner = resumed.owner
    assert owner is not None
    rec_owner = resumed.recovery
    assert rec_owner is not None
    entered, release = _held_fsync_barrier(monkeypatch)
    cp_task = asyncio.create_task(rec_owner.checkpoint_current_async())
    try:
        assert await asyncio.to_thread(entered.wait, 30)
        td_task = asyncio.create_task(rec_owner.teardown())
        assert await _wait_until(lambda: rec_owner.tearing_down)
        # Let the teardown reach its owned-write drain,
        # then cancel it REPEATEDLY while the write is
        # held: the drain must stay pending:
        await asyncio.sleep(0.05)
        for _ in range(3):
            td_task.cancel()
            await asyncio.sleep(0.05)
            assert not td_task.done()
        assert not rec_owner.closed
        assert registry.get(owner.namespace) is not None
        with pytest.raises(RecoveryStoreError) as exc_info:
            store.open_session(address)
        assert exc_info.value.limitation is (RecoveryStoreLimitation.WRITER_CONFLICT)
        # Release: the held write completes, and the held
        # cancellation propagates only AFTER the drain:
        release.set()
        with pytest.raises(asyncio.CancelledError):
            await td_task
        # The owner is NOT closed: nothing was released,
        # the fence was lifted and the ACTUAL owned write
        # completed (bound generation 3):
        assert rec_owner.closed is False
        assert rec_owner.tearing_down is False
        assert registry.get(owner.namespace) is not None
        assert rec_owner.bound_generation == 3
        cp = await cp_task
        assert cp.limitation is RecoveryStoreLimitation.OK
        assert cp.generation == 3
        # A later explicit teardown completes cleanly:
        td = await rec_owner.teardown()
        assert td.outcome is RecoveryTeardownOutcome.TEARDOWN
        assert rec_owner.closed is True
        assert registry.get(owner.namespace) is None
    finally:
        release.set()


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
async def test_late_writes_after_teardown_refused_typed(
    mode: Any, endpoint: str, tmp_path: Path
) -> None:
    """After teardown the closed recovery owner refuses
    every new operation (no late old-epoch writer), and
    the closed writer session refuses publication with
    the fixed session_closed limitation; the closed
    descriptor can no longer observe the pointer (never
    an assumption), so the ACTUAL committed generation is
    proven by a fresh open (2 = the durable epoch
    binding)."""
    identity = RequestIdentity(
        principal="late-write-principal",
        session="late-write-session",
        repository="late-write-repo",
        route="late-write-route",
    )
    ns, _state, _result, _ow, rec = _session_chain(mode, endpoint, identity, "late-write-lineage")
    address = RecoverySessionAddress.from_namespace(ns)
    root = _prepared_root(tmp_path)
    store = RecoveryStore(root)
    sess = store.open_session(address)
    try:
        pub = sess.publish(rec, expected_generation=0)
        assert pub.limitation is RecoveryStoreLimitation.OK
        assert pub.generation == 1
    finally:
        sess.close()
    registry = _work_registry()
    resumed = resume_session(registry, store, address)
    assert resumed.outcome is RecoveryResumeOutcome.RESUMED
    assert resumed.generation == 2
    rec_owner = resumed.recovery
    assert rec_owner is not None
    td = await rec_owner.teardown()
    assert td.outcome is RecoveryTeardownOutcome.TEARDOWN
    assert rec_owner.closed is True
    # New operations on the closed owner are refused:
    with pytest.raises(RecoveryError):
        rec_owner.checkpoint_current()
    with pytest.raises(RecoveryError):
        await rec_owner.checkpoint_current_async()
    # The closed writer session refuses publication with
    # the ACTUAL (unobservable) generation, never an
    # assumption:
    late = rec_owner.session.publish(rec, expected_generation=2)
    assert late.limitation is RecoveryStoreLimitation.SESSION_CLOSED
    assert late.generation is None
    assert late.pointer is None
    assert late.actual_generation is None
    fresh = store.open_session(address)
    try:
        assert fresh.current_generation() == 2
    finally:
        fresh.close()


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
async def test_work_teardown_refused_while_recovery_io_live_entry_order(
    mode: Any, endpoint: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Entry-order fence (requirement 4): while a recovery
    publication is LIVE (its transient reservation held
    inside a held fsync), BOTH direct teardown paths refuse
    with the typed RECOVERY_IN_FLIGHT before any release --
    the store teardown from its own entry check and the
    async work teardown from its entry check (no fence set,
    no drain, no release under live recovery IO); after the
    held write completes to generation 3 the composed
    teardown proceeds and a fresh open observes it."""
    identity = RequestIdentity(
        principal="wfence-entry-principal",
        session="wfence-entry-session",
        repository="wfence-entry-repo",
        route="wfence-entry-route",
    )
    ns, state, result, _ow, rec = _session_chain(mode, endpoint, identity, "wfence-entry-lineage")
    address = RecoverySessionAddress.from_namespace(ns)
    store = RecoveryStore(_prepared_root(tmp_path))
    sess = store.open_session(address)
    try:
        pub = sess.publish(rec, expected_generation=0)
        assert pub.limitation is RecoveryStoreLimitation.OK
        assert pub.generation == 1
    finally:
        sess.close()
    registry = _work_registry()
    work = registry.work
    assert work is not None
    resumed = resume_session(registry, store, address)
    assert resumed.outcome is RecoveryResumeOutcome.RESUMED
    assert resumed.generation == 2
    owner = resumed.owner
    assert owner is not None
    rec_owner = resumed.recovery
    assert rec_owner is not None
    assert rec_owner.bound_generation == 2
    entered, release = _held_fsync_barrier(monkeypatch)
    cp_task = asyncio.create_task(rec_owner.checkpoint_current_async())
    try:
        assert await asyncio.to_thread(entered.wait, 30)
        t_ref = owner.teardown(owner.namespace)
        assert t_ref.outcome is RamStateOutcome.REFUSED
        assert t_ref.limitation is RamStateLimitation.RECOVERY_IN_FLIGHT
        assert t_ref.freed_bytes == 0
        assert registry.get(owner.namespace) is not None
        wd_ref = await work.teardown_owner(owner.namespace)
        assert wd_ref.outcome is RamWorkOutcome.REFUSED
        assert wd_ref.limitation is RamWorkLimitation.RECOVERY_IN_FLIGHT
        assert wd_ref.freed_bytes == 0
        assert work._owners.get(owner.namespace.lineage_key) is None
        release.set()
        cp = await cp_task
        assert cp.limitation is RecoveryStoreLimitation.OK
        assert cp.generation == 3
        assert rec_owner.bound_generation == 3
        td = await rec_owner.teardown()
        assert td.outcome is RecoveryTeardownOutcome.TEARDOWN
        assert td.session_closed is True
        assert rec_owner.closed is True
        assert registry.get(owner.namespace) is None
        fresh = store.open_session(address)
        try:
            assert fresh.current_generation() == 3
        finally:
            fresh.close()
    finally:
        release.set()


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
async def test_store_teardown_refused_while_recovery_io_live_work_disabled(
    mode: Any, endpoint: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Store-side entry-order fence with the work plane
    DISABLED (requirement 4): a live recovery publication
    (its transient reservation held inside a held fsync)
    refuses the direct store teardown with the typed
    RECOVERY_IN_FLIGHT before any release; after the held
    write completes to generation 3 the composed teardown
    proceeds (the work-disabled store-only branch) and a
    fresh open observes the committed generation."""
    identity = RequestIdentity(
        principal="wfence-store-principal",
        session="wfence-store-session",
        repository="wfence-store-repo",
        route="wfence-store-route",
    )
    ns, state, result, _ow, rec = _session_chain(mode, endpoint, identity, "wfence-store-lineage")
    address = RecoverySessionAddress.from_namespace(ns)
    store = RecoveryStore(_prepared_root(tmp_path))
    sess = store.open_session(address)
    try:
        pub = sess.publish(rec, expected_generation=0)
        assert pub.limitation is RecoveryStoreLimitation.OK
        assert pub.generation == 1
    finally:
        sess.close()
    registry = RamStateOwnerRegistry()
    resumed = resume_session(registry, store, address)
    assert resumed.outcome is RecoveryResumeOutcome.RESUMED
    assert resumed.generation == 2
    owner = resumed.owner
    assert owner is not None
    rec_owner = resumed.recovery
    assert rec_owner is not None
    assert rec_owner.bound_generation == 2
    entered, release = _held_fsync_barrier(monkeypatch)
    cp_task = asyncio.create_task(asyncio.to_thread(rec_owner.checkpoint_current))
    try:
        assert await asyncio.to_thread(entered.wait, 30)
        t_ref = owner.teardown(owner.namespace)
        assert t_ref.outcome is RamStateOutcome.REFUSED
        assert t_ref.limitation is RamStateLimitation.RECOVERY_IN_FLIGHT
        assert t_ref.freed_bytes == 0
        assert registry.get(owner.namespace) is not None
        release.set()
        cp = await cp_task
        assert cp.limitation is RecoveryStoreLimitation.OK
        assert cp.generation == 3
        assert rec_owner.bound_generation == 3
        td = await rec_owner.teardown()
        assert td.outcome is RecoveryTeardownOutcome.TEARDOWN
        assert td.session_closed is True
        assert rec_owner.closed is True
        assert registry.get(owner.namespace) is None
        fresh = store.open_session(address)
        try:
            assert fresh.current_generation() == 3
        finally:
            fresh.close()
    finally:
        release.set()


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
async def test_work_teardown_fence_refuses_new_recovery_reservation_reverse_order(
    mode: Any, endpoint: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Reverse order (requirement 4): a work teardown that
    PASSED its entry check (no live recovery IO) fences the
    owner and drains its HELD live work; while fenced, every
    NEW recovery publication attempt (the sync checkpoint,
    the async checkpoint and the fenced admit of a genuine
    adverse candidate) is refused the transient reservation
    under the SAME registry lock -- typed WRITER_CONFLICT,
    no reservation charged (the process total is unchanged),
    no write, bound unchanged -- so the atomic work release
    can never run under a newly live recovery publication."""
    identity = RequestIdentity(
        principal="wfence-reverse-principal",
        session="wfence-reverse-session",
        repository="wfence-reverse-repo",
        route="wfence-reverse-route",
    )
    ns, state, result, _ow, rec = _session_chain(mode, endpoint, identity, "wfence-reverse-lineage")
    address = RecoverySessionAddress.from_namespace(ns)
    store = RecoveryStore(_prepared_root(tmp_path))
    sess = store.open_session(address)
    try:
        pub = sess.publish(rec, expected_generation=0)
        assert pub.limitation is RecoveryStoreLimitation.OK
        assert pub.generation == 1
    finally:
        sess.close()
    registry = _work_registry()
    work = registry.work
    assert work is not None
    resumed = resume_session(registry, store, address)
    assert resumed.outcome is RecoveryResumeOutcome.RESUMED
    assert resumed.generation == 2
    owner = resumed.owner
    assert owner is not None
    rec_owner = resumed.recovery
    assert rec_owner is not None
    assert rec_owner.bound_generation == 2
    # The REGISTERED (decoded) namespace and the RESTORED
    # records: every later registry / work-plane join uses
    # the actual retained objects (the accepted 019
    # identity law).
    t_result = resumed.t_result
    assert t_result is not None
    snap = owner.snapshot
    assert snap is not None
    ns = owner.namespace
    state = snap.state
    result = t_result
    okey = owner.namespace.lineage_key
    key = _root_content_key(result)
    gate = asyncio.Event()
    entered = asyncio.Event()
    cleaning = asyncio.Event()
    clean_release = asyncio.Event()
    calls: list[int] = []

    async def seam() -> bytes:
        calls.append(1)
        entered.set()
        try:
            await gate.wait()
        finally:
            cleaning.set()
            # The controlled cleanup barrier (the existing
            # 019 held-cleanup pattern): handles
            # cancellation at the barrier and stays LIVE
            # until explicitly released, so the teardown's
            # drain is genuinely PENDING (no release, no
            # fence drop) while the assertions run.
            while True:
                try:
                    await clean_release.wait()
                    break
                except asyncio.CancelledError:
                    continue
        return b"wfence-reverse-payload"

    leader = asyncio.create_task(work.resolve(ns, key, seam))
    await entered.wait()
    assert len(calls) == 1
    td_task = asyncio.create_task(work.teardown_owner(ns))
    # The owned cleanup is live at its barrier: the fence
    # is set and the drain is genuinely PENDING (the store
    # owner is still registered, the attempt unfinalized).
    assert await _wait_until(lambda: cleaning.is_set())
    assert not td_task.done()
    ow_td = work._owners.get(okey)
    assert ow_td is not None
    assert ow_td.fenced is True
    assert len(ow_td.live) == 1
    assert registry.get(owner.namespace) is not None
    proc_at_fence = registry.process_owned_bytes
    fence_sync = rec_owner.checkpoint_current()
    assert fence_sync.limitation is RecoveryStoreLimitation.WRITER_CONFLICT
    assert fence_sync.generation is None
    assert fence_sync.pointer is None
    assert fence_sync.actual_generation == 2
    fence_async = await rec_owner.checkpoint_current_async()
    assert fence_async.limitation is RecoveryStoreLimitation.WRITER_CONFLICT
    assert fence_async.generation is None
    s2, t2 = _changed_root_candidate(state, ns, endpoint)
    fence_admit = rec_owner.admit_with_fence(s2, t2, expected_revision=owner.revision)
    assert fence_admit.outcome is RecoveryAdmitOutcome.FENCE_REFUSED
    assert fence_admit.admitted is None
    assert fence_admit.advance is None
    assert fence_admit.fence is not None
    assert fence_admit.fence.limitation is RecoveryStoreLimitation.WRITER_CONFLICT
    assert fence_admit.owner_quarantined is False
    assert fence_admit.bound_generation == 2
    # No reservation landed: the process total is EXACTLY
    # unchanged by every refused attempt.
    assert registry.process_owned_bytes == proc_at_fence
    # The store owner is still live: the atomic release waits
    # for the drain (the fence is not lifted on a refusal).
    assert registry.get(owner.namespace) is not None
    # Release the controlled cleanup barrier: the drain
    # completes and only then does the atomic release
    # proceed.
    clean_release.set()
    td = await td_task
    assert td.outcome is RamWorkOutcome.TEARDOWN
    assert td.attempts_cancelled == 1
    assert td.freed_bytes > 0
    assert registry.get(owner.namespace) is None
    r_lead = await leader
    assert r_lead.outcome is RamWorkOutcome.FAILED
    assert r_lead.limitation is RamWorkLimitation.OWNER_TORN_DOWN
    assert r_lead.http_status == 503
    assert r_lead.invocations == 1
    # No recovery publication happened: the committed
    # generation is still 2 (the durable record remains for
    # restart).  Caller-level lifecycle cut: the work
    # teardown released the store owner, not the writer
    # session; the recovery owner's own composed teardown is
    # the normal path, and this dangling state is closed by
    # the caller.
    rec_owner.session.close()
    fresh = store.open_session(address)
    try:
        assert fresh.current_generation() == 2
    finally:
        fresh.close()


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
async def test_work_teardown_entry_fence_with_live_recovery_io_and_pending_drain(
    mode: Any, endpoint: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Entry order with a PENDING work drain (requirement 4):
    a live recovery publication (reservation held inside a
    held fsync) coexists with a live HELD work attempt (the
    work teardown's drain would await it) -- the work
    teardown's entry check refuses RECOVERY_IN_FLIGHT BEFORE
    fencing or draining (no fence set, the work attempt
    stays live, nothing released under live recovery IO);
    after the recovery write completes to generation 3 the
    SAME path proceeds: fence, cancel the held work, await
    the drain and release atomically."""
    identity = RequestIdentity(
        principal="wfence-compose-principal",
        session="wfence-compose-session",
        repository="wfence-compose-repo",
        route="wfence-compose-route",
    )
    ns, state, result, _ow, rec = _session_chain(mode, endpoint, identity, "wfence-compose-lineage")
    address = RecoverySessionAddress.from_namespace(ns)
    store = RecoveryStore(_prepared_root(tmp_path))
    sess = store.open_session(address)
    try:
        pub = sess.publish(rec, expected_generation=0)
        assert pub.limitation is RecoveryStoreLimitation.OK
        assert pub.generation == 1
    finally:
        sess.close()
    registry = _work_registry()
    work = registry.work
    assert work is not None
    resumed = resume_session(registry, store, address)
    assert resumed.outcome is RecoveryResumeOutcome.RESUMED
    assert resumed.generation == 2
    owner = resumed.owner
    assert owner is not None
    rec_owner = resumed.recovery
    assert rec_owner is not None
    assert rec_owner.bound_generation == 2
    # The REGISTERED (decoded) namespace and the RESTORED
    # admission record: every later registry / work-plane
    # join uses the actual retained objects (the accepted
    # 019 identity law).
    t_result = resumed.t_result
    assert t_result is not None
    ns = owner.namespace
    result = t_result
    okey = owner.namespace.lineage_key
    key = _root_content_key(result)
    gate = asyncio.Event()
    calls: list[int] = []

    async def seam() -> bytes:
        calls.append(1)
        await gate.wait()
        return b"wfence-compose-payload"

    leader = asyncio.create_task(work.resolve(ns, key, seam))
    assert await _wait_until(lambda: len(calls) == 1)
    entered, release = _held_fsync_barrier(monkeypatch)
    cp_task = asyncio.create_task(rec_owner.checkpoint_current_async())
    try:
        assert await asyncio.to_thread(entered.wait, 30)
        wd_ref = await asyncio.wait_for(work.teardown_owner(ns), 30)
        assert wd_ref.outcome is RamWorkOutcome.REFUSED
        assert wd_ref.limitation is RamWorkLimitation.RECOVERY_IN_FLIGHT
        assert wd_ref.freed_bytes == 0
        # No fence was set and the work attempt stayed live:
        assert work._owners.get(okey) is not None
        assert work._owners[okey].fenced is False
        assert len(calls) == 1
        assert registry.get(owner.namespace) is not None
        release.set()
        cp = await cp_task
        assert cp.limitation is RecoveryStoreLimitation.OK
        assert cp.generation == 3
        assert rec_owner.bound_generation == 3
        # Now the SAME path proceeds: fence, cancel the held
        # work, await the drain, release atomically.
        td = await work.teardown_owner(ns)
        assert td.outcome is RamWorkOutcome.TEARDOWN
        assert td.attempts_cancelled == 1
        assert td.freed_bytes > 0
        assert registry.get(owner.namespace) is None
    finally:
        release.set()
        gate.set()
    r_lead = await leader
    assert r_lead.outcome is RamWorkOutcome.FAILED
    assert r_lead.limitation is RamWorkLimitation.OWNER_TORN_DOWN
    assert r_lead.http_status == 503
    # Caller-level lifecycle cut as in the reverse-order
    # case: the durable record (generation 3) remains for
    # restart.
    rec_owner.session.close()
    fresh = store.open_session(address)
    try:
        assert fresh.current_generation() == 3
    finally:
        fresh.close()


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
async def test_resume_epoch_binding_encode_fault_releases_owner_and_writer(
    mode: Any, endpoint: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Epoch-binding ENCODE fault (order 3/4/5): a fault
    injected at the binding encode refuses the exposure
    typed STORE_REFUSED/OVERSIZED with the ACTUAL observed
    generation, and -- the leak regression -- the rebound
    transient is released BEFORE the owner teardown, so no
    usable registered owner, no residual reservation and no
    held writer survive (the retained registry high-water
    table charge is container metadata, so the process total
    may legitimately stay at or above the pre-resume
    baseline); a FRESH resume in the SAME registry succeeds
    (a leaked owner would be OWNER_ALREADY_LIVE, a leaked
    writer WRITER_CONFLICT)."""
    identity = RequestIdentity(
        principal="bindfault-enc-principal",
        session="bindfault-enc-session",
        repository="bindfault-enc-repo",
        route="bindfault-enc-route",
    )
    ns, state, result, _ow, rec = _session_chain(mode, endpoint, identity, "bindfault-enc-lineage")
    address = RecoverySessionAddress.from_namespace(ns)
    store = RecoveryStore(_prepared_root(tmp_path))
    sess = store.open_session(address)
    try:
        pub = sess.publish(rec, expected_generation=0)
        assert pub.limitation is RecoveryStoreLimitation.OK
        assert pub.generation == 1
    finally:
        sess.close()
    registry = _work_registry()
    proc_before = registry.process_owned_bytes

    def broken_encode(_record: RecoveryRecord, max_bytes: int) -> bytes:
        raise RecoveryCodecSizeError()

    with monkeypatch.context() as scoped:
        scoped.setattr(recovery_resume_mod, "encode_recovery_record", broken_encode)
        failed = resume_session(registry, store, address)
    assert failed.outcome is RecoveryResumeOutcome.STORE_REFUSED
    assert failed.limitation is RecoveryStoreLimitation.OVERSIZED
    assert failed.generation == 1
    assert failed.owner is None
    assert failed.recovery is None
    # The leak regression: no residual RESERVATION (the
    # rebound transient is released exactly once; the
    # retained registry high-water table charge is
    # container metadata, never session state, and may
    # legitimately keep the process total above the
    # pre-resume baseline).
    assert registry._recovery_session_transient.get(rec.namespace.lineage_key, 0) == 0
    assert registry.process_owned_bytes >= proc_before
    # A fresh resume in the SAME registry succeeds (it
    # would be OWNER_ALREADY_LIVE on a leaked owner and
    # WRITER_CONFLICT on a leaked writer).
    retry = resume_session(registry, store, address)
    assert retry.outcome is RecoveryResumeOutcome.RESUMED
    assert retry.generation == 2
    retry_owner = retry.owner
    assert retry_owner is not None
    assert registry.get(retry_owner.namespace) is retry_owner
    retry_recovery = retry.recovery
    assert retry_recovery is not None
    td = await retry_recovery.teardown()
    assert td.outcome is RecoveryTeardownOutcome.TEARDOWN
    assert registry.get(retry_owner.namespace) is None
    fresh = store.open_session(address)
    try:
        assert fresh.current_generation() == 2
    finally:
        fresh.close()


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
async def test_resume_epoch_binding_publish_fault_releases_owner_and_writer(
    mode: Any, endpoint: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Epoch-binding PUBLISH fault (order 3/4/5): a fault
    injected at the binding publication (a non-OK typed
    result carrying the ACTUAL observed generation) blocks
    the exposure exactly like the encode faults, and the
    leak regression is closed: the rebound transient is
    released before the owner teardown with no residual
    reservation (the retained registry high-water table
    charge is container metadata, so the process total may
    legitimately stay at or above the pre-resume baseline),
    no usable owner survives (a fresh SAME-registry resume
    succeeds, not OWNER_ALREADY_LIVE), the writer is
    released, and the committed generation is still 1 (no
    partial binding)."""
    identity = RequestIdentity(
        principal="bindfault-pub-principal",
        session="bindfault-pub-session",
        repository="bindfault-pub-repo",
        route="bindfault-pub-route",
    )
    ns, state, result, _ow, rec = _session_chain(mode, endpoint, identity, "bindfault-pub-lineage")
    address = RecoverySessionAddress.from_namespace(ns)
    store = RecoveryStore(_prepared_root(tmp_path))
    sess = store.open_session(address)
    try:
        pub = sess.publish(rec, expected_generation=0)
        assert pub.limitation is RecoveryStoreLimitation.OK
        assert pub.generation == 1
    finally:
        sess.close()
    registry = _work_registry()
    proc_before = registry.process_owned_bytes

    def broken_publish(
        self: RecoverySession,
        encoded: bytes,
        record: RecoveryRecord,
        expected_generation: int,
    ) -> RecoveryPublishResult:
        return RecoveryPublishResult(RecoveryStoreLimitation.IO_FAILURE, None, None, 1)

    with monkeypatch.context() as scoped:
        scoped.setattr(RecoverySession, "publish_encoded", broken_publish)
        failed = resume_session(registry, store, address)
    assert failed.outcome is RecoveryResumeOutcome.STORE_REFUSED
    assert failed.limitation is RecoveryStoreLimitation.IO_FAILURE
    assert failed.generation == 1
    assert failed.owner is None
    assert failed.recovery is None
    # The leak regression: no residual RESERVATION (the
    # rebound transient is released exactly once; the
    # retained registry high-water table charge is
    # container metadata, never session state, and may
    # legitimately keep the process total above the
    # pre-resume baseline).
    assert registry._recovery_session_transient.get(rec.namespace.lineage_key, 0) == 0
    assert registry.process_owned_bytes >= proc_before
    retry = resume_session(registry, store, address)
    assert retry.outcome is RecoveryResumeOutcome.RESUMED
    assert retry.generation == 2
    retry_owner = retry.owner
    assert retry_owner is not None
    assert registry.get(retry_owner.namespace) is retry_owner
    retry_recovery = retry.recovery
    assert retry_recovery is not None
    td = await retry_recovery.teardown()
    assert td.outcome is RecoveryTeardownOutcome.TEARDOWN
    assert registry.get(retry_owner.namespace) is None
    fresh = store.open_session(address)
    try:
        assert fresh.current_generation() == 2
    finally:
        fresh.close()


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
async def test_checkpoint_caller_cancellation_drains_owned_write(
    mode: Any, endpoint: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Checkpoint CALLER cancellation with held IO
    (requirement 4): a checkpoint held inside fsync is
    cancelled by its CALLER (repeatedly); the owned write
    must drain to its ACTUAL typed result while holding
    every cancellation BEFORE the cancellation propagates
    and BEFORE the slot / reservation are released -- the
    actual committed generation and ownership are preserved
    until the drain, and no second publication can pass
    mid-drain."""
    identity = RequestIdentity(
        principal="cp-cancel-principal",
        session="cp-cancel-session",
        repository="cp-cancel-repo",
        route="cp-cancel-route",
    )
    ns, state, result, _ow, rec = _session_chain(mode, endpoint, identity, "cp-cancel-lineage")
    address = RecoverySessionAddress.from_namespace(ns)
    store = RecoveryStore(_prepared_root(tmp_path))
    sess = store.open_session(address)
    try:
        pub = sess.publish(rec, expected_generation=0)
        assert pub.limitation is RecoveryStoreLimitation.OK
        assert pub.generation == 1
    finally:
        sess.close()
    registry = _work_registry()
    resumed = resume_session(registry, store, address)
    assert resumed.outcome is RecoveryResumeOutcome.RESUMED
    assert resumed.generation == 2
    owner = resumed.owner
    assert owner is not None
    rec_owner = resumed.recovery
    assert rec_owner is not None
    key = owner.namespace.lineage_key
    entered, release = _held_fsync_barrier(monkeypatch)
    cp_task = asyncio.create_task(rec_owner.checkpoint_current_async())
    try:
        assert await asyncio.to_thread(entered.wait, 30)
        # While the owned write is held: the slot is still
        # acquired (a second owned publication is refused
        # typed, no new thread), the reservation is held,
        # and the committed generation is unchanged.
        busy = await rec_owner.checkpoint_current_async()
        assert busy.limitation is RecoveryStoreLimitation.WRITE_IN_FLIGHT
        assert busy.actual_generation == 2
        assert registry._recovery_session_transient.get(key, 0) > 0
        # Cancel the CALLER (and cancel again): the owned
        # write is still live (held inside fsync), so the
        # task must stay PENDING -- the drain holds the
        # cancellation and ownership is not released early.
        cp_task.cancel()
        await asyncio.sleep(0.05)
        assert not cp_task.done()
        cp_task.cancel()
        await asyncio.sleep(0.05)
        assert not cp_task.done()
        busy2 = await rec_owner.checkpoint_current_async()
        assert busy2.limitation is RecoveryStoreLimitation.WRITE_IN_FLIGHT
        release.set()
        with pytest.raises(asyncio.CancelledError):
            await cp_task
    finally:
        release.set()
    # The drain completed the owned write to its ACTUAL
    # outcome (generation 3); the reservation is released
    # exactly once, the slot is free, and the owner is
    # still live and publishable.
    assert rec_owner.bound_generation == 3
    assert registry._recovery_session_transient.get(key, 0) == 0
    cp2 = await rec_owner.checkpoint_current_async()
    assert cp2.limitation is RecoveryStoreLimitation.OK
    assert cp2.generation == 4
    td = await rec_owner.teardown()
    assert td.outcome is RecoveryTeardownOutcome.TEARDOWN
    assert registry.get(owner.namespace) is None
    fresh = store.open_session(address)
    try:
        assert fresh.current_generation() == 4
    finally:
        fresh.close()


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
async def test_checkpoint_caller_deadline_drains_owned_write(
    mode: Any, endpoint: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Checkpoint CALLER deadline (timeout) with held IO
    (requirement 4): the caller's bounded deadline fires
    while the owned write is held inside fsync; the
    deadline must NOT release ownership before the owned
    write drains -- the await stays pending while the
    write is held (reservation and slot preserved), and
    only after the write completes to its ACTUAL outcome
    (generation 3) does the caller's timeout surface."""
    identity = RequestIdentity(
        principal="cp-deadline-principal",
        session="cp-deadline-session",
        repository="cp-deadline-repo",
        route="cp-deadline-route",
    )
    ns, state, result, _ow, rec = _session_chain(mode, endpoint, identity, "cp-deadline-lineage")
    address = RecoverySessionAddress.from_namespace(ns)
    store = RecoveryStore(_prepared_root(tmp_path))
    sess = store.open_session(address)
    try:
        pub = sess.publish(rec, expected_generation=0)
        assert pub.limitation is RecoveryStoreLimitation.OK
        assert pub.generation == 1
    finally:
        sess.close()
    registry = _work_registry()
    resumed = resume_session(registry, store, address)
    assert resumed.outcome is RecoveryResumeOutcome.RESUMED
    assert resumed.generation == 2
    owner = resumed.owner
    assert owner is not None
    rec_owner = resumed.recovery
    assert rec_owner is not None
    key = owner.namespace.lineage_key
    entered, release = _held_fsync_barrier(monkeypatch)
    deadline_task = asyncio.create_task(
        asyncio.wait_for(rec_owner.checkpoint_current_async(), timeout=1.0)
    )
    try:
        assert await asyncio.to_thread(entered.wait, 30)
        assert not deadline_task.done()
        # Let the deadline fire: the inner owned write is
        # still live (held), so the deadline await must
        # stay PENDING (drain in progress) with the
        # reservation and slot preserved.
        await asyncio.sleep(1.5)
        assert not deadline_task.done()
        assert registry._recovery_session_transient.get(key, 0) > 0
        busy = await rec_owner.checkpoint_current_async()
        assert busy.limitation is RecoveryStoreLimitation.WRITE_IN_FLIGHT
        release.set()
        with pytest.raises(TimeoutError):
            await deadline_task
    finally:
        release.set()
    # The drain completed the owned write to its ACTUAL
    # outcome (generation 3); the reservation is released
    # exactly once, the slot is free, and the owner is
    # still live and publishable.
    assert rec_owner.bound_generation == 3
    assert registry._recovery_session_transient.get(key, 0) == 0
    cp2 = await rec_owner.checkpoint_current_async()
    assert cp2.limitation is RecoveryStoreLimitation.OK
    assert cp2.generation == 4
    td = await rec_owner.teardown()
    assert td.outcome is RecoveryTeardownOutcome.TEARDOWN
    assert registry.get(owner.namespace) is None
    fresh = store.open_session(address)
    try:
        assert fresh.current_generation() == 4
    finally:
        fresh.close()


RESTART_CHILD_SOURCE = r"""
import asyncio
import builtins
import io
import json
import os
import socket
import subprocess as _sp
import sys


def _main() -> int:
    root = os.path.abspath(sys.argv[1])
    forbidden = os.path.abspath(sys.argv[2])
    address_fields = json.loads(sys.argv[3])
    b_dirname = sys.argv[4]
    hits: list[str] = []

    def _is_forbidden(value: object) -> bool:
        try:
            actual = os.path.abspath(os.fspath(value))
        except (TypeError, ValueError):
            actual = None
        if actual is not None and (
            actual == forbidden or actual.startswith(forbidden + os.sep)
        ):
            return True
        # The known relative B directory basename: the actual
        # descriptor-relative form os.open(B_basename,
        # dir_fd=root_fd) never normalizes to the forbidden
        # absolute path, so the known bare name is refused too.
        try:
            return os.path.basename(os.fspath(value)) == b_dirname
        except (TypeError, ValueError):
            return False

    def _check(label: str, args: tuple, kwargs: dict, log: list[str]) -> None:
        for a in args:
            if _is_forbidden(a):
                log.append(label)
                raise AssertionError('forbidden cross-session IO: ' + label)
        for k in ('path', 'file', 'name'):
            v = kwargs.get(k)
            if isinstance(v, (str, bytes, os.PathLike)) and _is_forbidden(v):
                log.append(label)
                raise AssertionError('forbidden cross-session IO: ' + label)

    def _wrap(module: object, name: str):
        real = getattr(module, name)

        def fn(*args, **kwargs):
            _check(name, args, kwargs, hits)
            return real(*args, **kwargs)

        return fn

    facilities = [
        (builtins, 'open'),
        (io, 'open'),
        (socket, 'socket'),
        (socket, 'create_connection'),
        (socket, 'getaddrinfo'),
        (_sp, 'Popen'),
        (asyncio, 'create_subprocess_exec'),
        (asyncio, 'create_subprocess_shell'),
    ]
    facilities.extend(
        (os, n)
        for n in (
            'open', 'stat', 'lstat', 'listdir', 'scandir', 'readlink',
            'access', 'unlink', 'replace', 'rename', 'mkdir', 'rmdir',
            'remove', 'system', 'fork', 'posix_spawn',
        )
        if hasattr(os, n)
    )
    for m, n in facilities:
        setattr(m, n, _wrap(m, n))

    # Trap self-test BEFORE the resume: exercise the ACTUAL
    # wrapped os.open in the descriptor-relative form
    # os.open(B_basename, dir_fd=root_fd) against a real root
    # fd and assert the refusal; then reset that expected
    # self-test hit so the resume trap_hits stay clean.
    root_fd = os.open(root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        try:
            os.open(
                b_dirname,
                os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
                dir_fd=root_fd,
            )
        except AssertionError:
            pass
        else:
            raise SystemExit('trap self-test failed to refuse the relative-B open')
    finally:
        os.close(root_fd)
    assert hits == ['open']
    hits.clear()

    from slaif_local_coding.constitution.bundles.ram_state import (
        RamStateOwnerRegistry,
    )
    from slaif_local_coding.constitution.bundles.ram_work_models import (
        RamWorkBounds,
    )
    from slaif_local_coding.constitution.bundles.recovery_models import (
        RecoverySessionAddress,
    )
    from slaif_local_coding.constitution.bundles.recovery_resume import (
        RecoveryResumeOutcome,
        resume_session,
    )
    from slaif_local_coding.constitution.bundles.recovery_store import (
        RecoveryStore,
    )

    # Resume-section scan denial: refuse EVERY listdir/scandir
    # call, irrespective of arguments (including fd arguments);
    # the trusted address lookup needs no scan. Installed after
    # the imports so import-time host use is out of scope for
    # this resume-section fence.
    def _scan_refuse(name: str):
        def fn(*args, **kwargs):
            hits.append(name)
            raise AssertionError('forbidden store-tree scan: ' + name)

        return fn

    os.listdir = _scan_refuse('listdir')
    os.scandir = _scan_refuse('scandir')

    store = RecoveryStore(root)
    address = RecoverySessionAddress(**address_fields)
    registry = RamStateOwnerRegistry(work_bounds=RamWorkBounds())
    work = registry.work
    assert work is not None
    resumed = resume_session(registry, store, address)
    assert resumed.outcome is RecoveryResumeOutcome.RESUMED, resumed
    assert resumed.generation is not None
    owner = resumed.owner
    assert owner is not None
    t_result = resumed.t_result
    assert t_result is not None
    recovery = resumed.recovery
    assert recovery is not None
    key = t_result.admission.root_entry.content_key
    calls: list[int] = []

    async def seam() -> bytes:
        calls.append(1)
        return b'restart-child-payload'

    async def go():
        r1 = await work.resolve(owner.namespace, key, seam)
        r2 = await work.resolve(owner.namespace, key, seam)
        td = await recovery.teardown()
        fresh = store.open_session(address)
        try:
            committed_after = fresh.current_generation()
        finally:
            fresh.close()
        return r1, r2, td, committed_after

    r1, r2, td, committed_after = asyncio.run(go())
    verdict = {
        'outcome': resumed.outcome.value,
        'generation': resumed.generation,
        'prior_epoch': resumed.prior_epoch,
        'new_epoch': resumed.new_epoch,
        'first': [r1.outcome.value, r1.invocations],
        'second': [r2.outcome.value, r2.invocations],
        'teardown': td.outcome.value,
        'committed_after': committed_after,
        'trap_hits': hits,
        'self_test': True,
    }
    print(json.dumps(verdict))
    return 0


sys.exit(_main())
"""


def _run_restart_child(
    script: Path, root: Path, forbidden: Path, address: RecoverySessionAddress
) -> dict[str, Any]:
    """Run ONE plain-Python restart child (no Codex /
    client processes anywhere) with a bounded wait and
    guaranteed cleanup of the owned child; returns the
    parsed bounded JSON verdict."""
    args = [
        sys.executable,
        str(script),
        str(root),
        str(forbidden),
        json.dumps(address.model_dump()),
        forbidden.name,
    ]
    repo_root = Path(__file__).resolve().parents[1]
    proc = subprocess.Popen(
        args,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=str(repo_root),
    )
    try:
        out, err = proc.communicate(timeout=240)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.communicate()
        raise
    assert proc.returncode == 0, (proc.returncode, err.decode("utf-8", "replace")[:2000])
    lines = out.decode("utf-8", "replace").strip().splitlines()
    assert lines, "no verdict line from the restart child"
    verdict: dict[str, Any] = json.loads(lines[-1])
    return verdict


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_subprocess_restart_one_dormant_session_address_only(
    mode: Any, endpoint: str, tmp_path: Path
) -> None:
    """Actual Python restart (order: subprocess restart
    tests allowed, no Codex / client processes anywhere):
    two dormant persisted sessions (A and B) under ONE
    protected root; a FRESH plain-Python process resumes
    EXACTLY ONE (A) from its trusted address ALONE -- no
    root, source or surviving virtual reference in the
    request context -- under a path-filtered trap that
    refuses ANY read of the other dormant session's
    directory (the trap must stay clean: only that
    session is read / rebuilt).  The needed current key
    is prepared through the ACTUAL 019 work plane once
    per new epoch (the honest first rebuild vs RAM hit:
    invocations 1, then HIT with 0).  A SECOND fresh
    process resumes the SAME address: the distinct epoch
    is strictly above the durably bound prior and the
    durable epoch binding is re-published, so the committed
    generation advances 2 -> 3; within each epoch the work
    hits do NOT rewrite the generation (the fresh
    post-teardown open still reports the resume-time
    committed generation), and the other session is still
    untouched."""
    identity_a = RequestIdentity(
        principal="restart-a-principal",
        session="restart-a-session",
        repository="restart-a-repo",
        route="restart-a-route",
    )
    ns_a, _state_a, _result_a, _ow_a, rec_a = _session_chain(
        mode, endpoint, identity_a, "restart-a-lineage"
    )
    identity_b = RequestIdentity(
        principal="restart-b-principal",
        session="restart-b-session",
        repository="restart-b-repo",
        route="restart-b-route",
    )
    ns_b, _state_b, _result_b, _ow_b, rec_b = _session_chain(
        mode, endpoint, identity_b, "restart-b-lineage"
    )
    root = _prepared_root(tmp_path)
    store = RecoveryStore(root)
    address_a = RecoverySessionAddress.from_namespace(ns_a)
    address_b = RecoverySessionAddress.from_namespace(ns_b)
    for address, rec in ((address_a, rec_a), (address_b, rec_b)):
        sess = store.open_session(address)
        try:
            pub = sess.publish(rec, expected_generation=0)
            assert pub.limitation is RecoveryStoreLimitation.OK
            assert pub.generation == 1
        finally:
            sess.close()
    script = tmp_path / "restart_child.py"
    script.write_text(RESTART_CHILD_SOURCE, encoding="utf-8")
    forbidden_b = root / session_directory_name(address_b)
    v1 = _run_restart_child(script, root, forbidden_b, address_a)
    assert v1["outcome"] == RecoveryResumeOutcome.RESUMED.value
    assert v1["generation"] == 2
    assert v1["prior_epoch"] == 1
    assert v1["new_epoch"] == 2
    assert v1["first"] == [RamWorkOutcome.COMPLETED.value, 1]
    assert v1["second"] == [RamWorkOutcome.HIT.value, 0]
    assert v1["teardown"] == RecoveryTeardownOutcome.TEARDOWN.value
    assert v1["trap_hits"] == []
    assert v1["self_test"] is True
    # No usage rewrite within an epoch: the work hits and the
    # teardown did not rewrite the checkpoint, so a fresh
    # post-teardown open still reports the resume-time
    # committed generation.
    assert v1["committed_after"] == v1["generation"]
    v2 = _run_restart_child(script, root, forbidden_b, address_a)
    assert v2["outcome"] == RecoveryResumeOutcome.RESUMED.value
    # Every resume re-publishes the durable epoch binding, so
    # the second resume commits a NEW generation (3) above the
    # first resume's committed generation (2): the distinct
    # epoch is strictly above the durably bound prior.
    assert v2["generation"] == 3
    assert v2["prior_epoch"] == v1["new_epoch"] == 2
    assert v2["new_epoch"] == 3
    assert v2["first"] == [RamWorkOutcome.COMPLETED.value, 1]
    assert v2["second"] == [RamWorkOutcome.HIT.value, 0]
    assert v2["teardown"] == RecoveryTeardownOutcome.TEARDOWN.value
    assert v2["trap_hits"] == []
    assert v2["self_test"] is True
    # No usage rewrite within an epoch: a fresh post-teardown
    # open still reports the resume-time committed generation.
    assert v2["committed_after"] == v2["generation"]

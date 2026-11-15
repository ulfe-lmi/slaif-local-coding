"""Permanent 019-a matrix for the bounded RAM owner and atomic
state storage (contract ``docs/CACHE-RAM-STATE-CONTRACT.md``).

The genuine 018-p bootstrap fixtures and the ACTUAL 018-t
``derive_root_region_admission`` compose the retained record
sets; the RAM store is exercised only through its public owner
/ registry surface.  Every targeted negative starts from a
genuine accepted positive, and the conservative occupancy
recipe is asserted on the ACTUAL retained graph (originals AND
metadata, the retained history and the retained snapshot
storage) -- never a total-RSS promise.

The module covers the root-only bootstrap record sets, the
strict bounds model, owner / epoch isolation, snapshot
occupancy, both ceiling refusals, explicit teardown, the
malformed-join battery, the commit CAS fence, the genuine
source/currentness transition matrix (the stable unchanged-A
key after an unrelated same-session B admission, the refused
update on a populated owner, the genuine distinct-binding
namespace isolation), the canonical-forge negatives at the
owner boundary, the mechanically denied host-IO battery and
the concurrent single-owner / single-commit / process-ceiling
races.
"""

import re
import threading
from collections.abc import Callable
from typing import Any

import pytest
from pydantic import ValidationError

from slaif_local_coding.constitution.bundles.bundle_admission_models import (
    AdmissionMode,
)
from slaif_local_coding.constitution.bundles.causal_history_models import (
    CAUSAL_ROOT_FACT,
)
from slaif_local_coding.constitution.bundles.current_admission_models import (
    _canonical_entry_key,
)
from slaif_local_coding.constitution.bundles.ram_state import (
    RamStateAccountingError,
    RamStateCapacityError,
    RamStateDuplicateOwnerError,
    RamStateInputError,
    RamStateOwner,
    RamStateOwnerRegistry,
    _charge_object,
    ram_owner_base_charge,
    ram_retained_owned_bytes,
)
from slaif_local_coding.constitution.bundles.ram_state_models import (
    RAM_HTTP_CAPACITY_STATUS,
    RAM_OWNED_BYTES_HARD_CEILING,
    RAM_PROCESS_MAX_OWNED_BYTES_DEFAULT,
    RAM_SESSION_MAX_OWNED_BYTES_DEFAULT,
    RamStateAdmissionResult,
    RamStateBounds,
    RamStateLimitation,
    RamStateOutcome,
    ram_state_bounds_shape_ok,
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
from slaif_local_coding.constitution.cache import RequestIdentity
from tests.test_causal_history import ENDPOINTS, MODES, ROOT_TEXT, read_request
from tests.test_root_lineage import occurrences
from tests.test_root_region_lineage import (
    A_TEXT,
    B_TEXT,
    MARK,
    MIX_CMD,
    V2,
    _host_io_facilities,
    _mixed_body,
    r_bootstrap,
    r_issue,
    r_observe,
)

V3 = "Read `A.md` for the diverging fork."
ROOT_AB = "Read `A.md` and `B.md` before changing code."


def _ready_t(
    mode: AdmissionMode, lineage: str
) -> tuple[
    RootRegionLineageNamespace,
    RootRegionLineageState,
    RootRegionAdmissionResult,
]:
    """A genuine READY root-only bootstrap record set (the
    positive anchor for every control in this module).  The
    bootstrap envelope is endpoint-independent: actual
    endpoint coverage is earned by the genuine read
    transitions in the later matrix batches."""
    ns, state = r_bootstrap(mode, lineage)
    result = derive_root_region_admission(state, ns)
    assert result.outcome is RootRegionAdmissionOutcome.READY
    return ns, state, result


def _root_key(result: RootRegionAdmissionResult) -> str:
    admission = result.admission
    assert admission is not None
    return admission.root_entry.content_key


def _fresh_shell() -> int:
    """The ACTUAL measured shared registry shell baseline."""
    return RamStateOwnerRegistry().process_owned_bytes


def _configured_baseline(session: int, process: int) -> int:
    """The ACTUAL measured baseline of a registry configured
    with these distinct large ceiling ints, read before any
    owner is acquired.  The at/one-over caps are derived from
    this measured baseline, never assumed from the default
    shell (one shared int object across both bound fields
    would identity-deduplicate and charge only once)."""
    return RamStateOwnerRegistry(
        bounds=RamStateBounds(
            session_max_owned_bytes=session,
            process_max_owned_bytes=process,
        )
    ).process_owned_bytes


def _measure_first_charge(
    registry: RamStateOwnerRegistry,
    ns: RootRegionLineageNamespace,
    state: RootRegionLineageState,
    result: RootRegionAdmissionResult,
) -> int:
    """The ACTUAL measured charge of ONE first admission of a
    genuine record set under this recipe."""
    owner = registry.acquire(ns)
    admit = owner.admit(state, result, ns, expected_revision=0)
    assert admit.outcome is RamStateOutcome.ADMITTED
    return admit.charged_bytes


def _run_parallel(workers: list[Callable[[], None]]) -> list[Exception]:
    """Run the workers behind ONE barrier; return the captured
    worker exceptions (empty on a clean race)."""
    errors: list[Exception] = []
    barrier = threading.Barrier(len(workers))
    lock = threading.Lock()

    def guarded(worker: Callable[[], None]) -> None:
        try:
            barrier.wait(timeout=30)
            worker()
        except Exception as exc:
            with lock:
                errors.append(exc)

    threads = [threading.Thread(target=guarded, args=(w,)) for w in workers]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=30)
    assert all(not thread.is_alive() for thread in threads)
    return errors


# --- m. Bounds model: strict raw integer ceilings ---------------------


def test_m_bounds_defaults_and_stricter_positive() -> None:
    defaults = RamStateBounds()
    assert defaults.session_max_owned_bytes == RAM_SESSION_MAX_OWNED_BYTES_DEFAULT
    assert defaults.process_max_owned_bytes == RAM_PROCESS_MAX_OWNED_BYTES_DEFAULT
    stricter = RamStateBounds(
        session_max_owned_bytes=1 << 20,
        process_max_owned_bytes=1 << 21,
    )
    assert stricter.session_max_owned_bytes == 1 << 20
    assert stricter.process_max_owned_bytes == 1 << 21
    equal = RamStateBounds(session_max_owned_bytes=1 << 16, process_max_owned_bytes=1 << 16)
    assert equal.session_max_owned_bytes == equal.process_max_owned_bytes


@pytest.mark.parametrize(
    "kwargs",
    [
        pytest.param({"session_max_owned_bytes": 0}, id="session-zero"),
        pytest.param({"session_max_owned_bytes": -1}, id="session-negative"),
        pytest.param({"session_max_owned_bytes": True}, id="session-bool"),
        pytest.param({"session_max_owned_bytes": 1.5}, id="session-float"),
        pytest.param({"session_max_owned_bytes": "5"}, id="session-str"),
        pytest.param(
            {"session_max_owned_bytes": RAM_OWNED_BYTES_HARD_CEILING + 1},
            id="session-above-hard",
        ),
        pytest.param({"process_max_owned_bytes": 0}, id="process-zero"),
        pytest.param({"process_max_owned_bytes": True}, id="process-bool"),
        pytest.param({"process_max_owned_bytes": "5"}, id="process-str"),
        pytest.param(
            {"process_max_owned_bytes": RAM_OWNED_BYTES_HARD_CEILING + 1},
            id="process-above-hard",
        ),
        pytest.param(
            {"session_max_owned_bytes": RAM_PROCESS_MAX_OWNED_BYTES_DEFAULT + 1},
            id="session-above-process",
        ),
        pytest.param(
            {
                "session_max_owned_bytes": 1 << 20,
                "process_max_owned_bytes": 1 << 19,
            },
            id="session-above-process2",
        ),
    ],
)
def test_m_bounds_refuse_malformed_ceiling_shapes(kwargs: dict[str, object]) -> None:
    with pytest.raises(ValidationError):
        RamStateBounds(**kwargs)  # type: ignore[arg-type]


def test_m_bounds_shape_ok_original_class_law() -> None:
    assert ram_state_bounds_shape_ok(RamStateBounds())
    assert ram_state_bounds_shape_ok(RamStateBounds(session_max_owned_bytes=1 << 10))

    class _ShadowBounds(RamStateBounds):
        pass

    assert not ram_state_bounds_shape_ok(_ShadowBounds())
    assert not ram_state_bounds_shape_ok({"session_max_owned_bytes": 1 << 10})
    assert not ram_state_bounds_shape_ok(None)


def test_m_registry_bounds_law() -> None:
    ns, _state, _result = _ready_t(MODES[0], "ram019m-reg")
    base = ram_owner_base_charge(ns)

    class _ShadowBounds(RamStateBounds):
        pass

    with pytest.raises(RamStateInputError):
        RamStateOwnerRegistry(bounds=_ShadowBounds())
    tight = RamStateOwnerRegistry(
        bounds=RamStateBounds(
            session_max_owned_bytes=base - 1,
            process_max_owned_bytes=base - 1,
        )
    )
    with pytest.raises(RamStateCapacityError):
        tight.new_owner(ns)
    with pytest.raises(RamStateCapacityError):
        tight.acquire(ns)
    with pytest.raises(RamStateCapacityError):
        RamStateOwnerRegistry().new_owner(ns, session_max_owned_bytes=1)
    with pytest.raises(RamStateInputError):
        RamStateOwnerRegistry().new_owner(
            ns,
            session_max_owned_bytes=RAM_PROCESS_MAX_OWNED_BYTES_DEFAULT + 1,
        )


# --- a. Genuine positive admission + independent owners ---------------


@pytest.mark.parametrize("mode", MODES)
def test_a_genuine_positive_admission(mode: AdmissionMode) -> None:
    ns, state, result = _ready_t(mode, f"ram019a-{mode.value}")
    registry = RamStateOwnerRegistry()
    shell = registry.process_owned_bytes
    assert shell > 0
    owner = registry.acquire(ns)
    base = ram_owner_base_charge(ns)
    assert owner.owned_bytes == base
    assert registry.process_owned_bytes == shell + base
    admit = owner.admit(state, result, ns, expected_revision=0)
    assert admit.outcome is RamStateOutcome.ADMITTED
    assert admit.limitation is None
    assert admit.revision == 1
    assert admit.http_status is None
    snapshot = admit.snapshot
    assert snapshot is not None
    assert snapshot.namespace is ns
    assert snapshot.state is state
    assert snapshot.result is result
    assert snapshot.revision == 1
    assert snapshot.epoch == owner.epoch
    assert snapshot.owned_bytes == owner.owned_bytes
    assert owner.owned_bytes == admit.session_owned_bytes
    assert admit.charged_bytes == owner.owned_bytes
    assert admit.charged_bytes == ram_retained_owned_bytes(
        ns, state, result, owner.history, snapshot
    )
    assert admit.charged_bytes > result.entry_source_bytes
    key = _root_key(result)
    found = owner.lookup(key, ns)
    assert found.outcome is RamStateOutcome.FOUND
    assert found.limitation is None
    admission = result.admission
    assert admission is not None
    assert found.entry is admission.root_entry
    assert found.revision == 1
    assert found.epoch == owner.epoch
    cross = owner.lookup(key, ns.model_copy())
    assert cross.outcome is RamStateOutcome.NOT_FOUND
    assert cross.limitation is RamStateLimitation.OWNER_NAMESPACE_MISMATCH
    with pytest.raises(RamStateInputError):
        owner.admit(state, result, ns.model_copy(), expected_revision=1)
    # An unrelated same-content lineage: its OWN actual charge
    # (the recipe is deterministic per retained graph, not equal
    # across distinct lineages), and the first owner untouched.
    ns2, state2, result2 = _ready_t(mode, f"ram019a2-{mode.value}")
    assert ns2.lineage_key != ns.lineage_key
    first_snapshot = owner.snapshot
    owner2 = registry.acquire(ns2)
    admit2 = owner2.admit(state2, result2, ns2, expected_revision=0)
    assert admit2.outcome is RamStateOutcome.ADMITTED
    assert admit2.charged_bytes > ram_owner_base_charge(ns2)
    assert registry.process_owned_bytes == (shell + admit.charged_bytes + admit2.charged_bytes)
    assert owner.snapshot is first_snapshot
    assert owner.lookup(key, ns).outcome is RamStateOutcome.FOUND
    assert owner2.lookup(key, ns).outcome is RamStateOutcome.NOT_FOUND
    # Same-object determinism: the SAME retained graph under a
    # fresh owner charges identically.
    replay_owner = RamStateOwnerRegistry().acquire(ns)
    replay = replay_owner.admit(state, result, ns, expected_revision=0)
    assert replay.outcome is RamStateOutcome.ADMITTED
    assert replay.charged_bytes == admit.charged_bytes


# --- b. Owner / epoch lifecycle and registry join law -----------------


def test_b_owner_epoch_lifecycle() -> None:
    ns, state, result = _ready_t(MODES[0], "ram019b")
    registry = RamStateOwnerRegistry()
    owner = registry.acquire(ns)
    assert registry.acquire(ns) is owner
    assert registry.get(ns) is owner
    message = re.escape(RamStateDuplicateOwnerError.MESSAGE)
    with pytest.raises(RamStateDuplicateOwnerError, match=message):
        registry.new_owner(ns)
    with pytest.raises(RamStateInputError):
        registry.acquire(ns.model_copy())
    with pytest.raises(RamStateInputError):
        registry.get(ns.model_copy())
    partial = RootRegionLineageNamespace.model_construct(lineage_key=ns.lineage_key)
    with pytest.raises(RamStateInputError):
        registry.acquire(partial)
    process_before = registry.process_owned_bytes
    no_fields = RootRegionLineageNamespace.model_construct()
    with pytest.raises(RamStateInputError):
        registry.acquire(no_fields)
    with pytest.raises(RamStateInputError):
        registry.new_owner(no_fields)
    with pytest.raises(RamStateInputError):
        registry.get(no_fields)
    assert registry.get(ns) is owner
    assert registry.process_owned_bytes == process_before
    unregistered = RamStateOwner(
        ns,
        session_max_owned_bytes=registry.bounds.session_max_owned_bytes,
        registry=registry,
    )
    with pytest.raises(RamStateInputError):
        unregistered.admit(state, result, ns, expected_revision=0)
    with pytest.raises(RamStateInputError):
        unregistered.lookup(_root_key(result), ns)
    with pytest.raises(RamStateInputError):
        unregistered.teardown(ns)
    admit = owner.admit(state, result, ns, expected_revision=0)
    assert admit.outcome is RamStateOutcome.ADMITTED
    key = _root_key(result)
    wrong_epoch = owner.lookup(key, ns, expected_epoch=owner.epoch + 5)
    assert wrong_epoch.outcome is RamStateOutcome.NOT_FOUND
    assert wrong_epoch.limitation is RamStateLimitation.EPOCH_FENCED
    wrong_teardown = owner.teardown(ns, expected_epoch=owner.epoch + 5)
    assert wrong_teardown.outcome is RamStateOutcome.REFUSED
    assert wrong_teardown.limitation is RamStateLimitation.EPOCH_FENCED
    assert owner.snapshot is not None
    old_epoch = owner.epoch
    torn = owner.teardown(ns)
    assert torn.outcome is RamStateOutcome.TEARDOWN
    assert torn.limitation is None
    successor = registry.acquire(ns)
    assert successor is not owner
    assert successor.epoch == old_epoch + 1
    stale_epoch = successor.lookup(key, ns, expected_epoch=old_epoch)
    assert stale_epoch.outcome is RamStateOutcome.NOT_FOUND
    assert stale_epoch.limitation is RamStateLimitation.EPOCH_FENCED
    empty = successor.lookup("0" * 64, ns)
    assert empty.outcome is RamStateOutcome.NOT_FOUND
    assert empty.limitation is None
    assert empty.revision == 0
    admit2 = successor.admit(state, result, ns, expected_revision=0)
    assert admit2.outcome is RamStateOutcome.ADMITTED
    joined = successor.lookup(key, ns, expected_epoch=successor.epoch)
    assert joined.outcome is RamStateOutcome.FOUND
    assert owner.epoch_fenced
    assert owner.snapshot is None
    fenced_admit = owner.admit(state, result, ns, expected_revision=0)
    assert fenced_admit.outcome is RamStateOutcome.REFUSED
    assert fenced_admit.limitation is RamStateLimitation.EPOCH_FENCED
    fenced_lookup = owner.lookup(key, ns)
    assert fenced_lookup.outcome is RamStateOutcome.NOT_FOUND
    assert fenced_lookup.limitation is RamStateLimitation.EPOCH_FENCED
    fenced_teardown = owner.teardown(ns)
    assert fenced_teardown.outcome is RamStateOutcome.REFUSED
    assert fenced_teardown.limitation is RamStateLimitation.EPOCH_FENCED
    assert registry.get(ns) is successor


# --- d. Atomic ceilings at / over both bounds -------------------------


def test_d_session_ceiling_at_and_over() -> None:
    ns, state, result = _ready_t(MODES[0], "ram019d-s")
    charge = _measure_first_charge(RamStateOwnerRegistry(), ns, state, result)
    at_owner = RamStateOwnerRegistry().new_owner(ns, session_max_owned_bytes=charge)
    at_admit = at_owner.admit(state, result, ns, expected_revision=0)
    assert at_admit.outcome is RamStateOutcome.ADMITTED
    assert at_admit.charged_bytes == charge
    assert at_admit.http_status is None
    assert at_admit.snapshot is not None
    assert at_admit.snapshot.owned_bytes == charge
    assert at_owner.owned_bytes == charge
    over_owner = RamStateOwnerRegistry().new_owner(ns, session_max_owned_bytes=charge - 1)
    over_admit = over_owner.admit(state, result, ns, expected_revision=0)
    assert over_admit.outcome is RamStateOutcome.REFUSED
    assert over_admit.limitation is RamStateLimitation.SESSION_OWNED_BYTES_OVER_BOUND
    assert over_admit.http_status == RAM_HTTP_CAPACITY_STATUS
    assert over_admit.charged_bytes == charge
    assert over_admit.snapshot is None
    assert over_admit.revision == 0
    assert over_owner.snapshot is None
    assert over_owner.revision == 0
    assert over_owner.owned_bytes == ram_owner_base_charge(ns)


def test_d_process_ceiling_at_and_over() -> None:
    ns_a, state_a, result_a = _ready_t(MODES[0], "ram019d-pa")
    ns_b, state_b, result_b = _ready_t(MODES[0], "ram019d-pb")
    probe = RamStateOwnerRegistry()
    charge_a = _measure_first_charge(probe, ns_a, state_a, result_a)
    charge_b = _measure_first_charge(probe, ns_b, state_b, result_b)
    # The ACTUAL measured baseline of a configured registry
    # (distinct large ceiling ints, read before any owner),
    # is the basis for REAL at/one-over caps.
    base = _configured_baseline(charge_a, charge_a + charge_b)
    # EXACTLY-AT: the process cap is exactly the measured
    # baseline plus the measured first charge; the session
    # ceiling is a legal DISTINCT value (itself exactly the
    # charge, so the session gate passes and the PROCESS gate
    # is the one under test).
    at = RamStateOwnerRegistry(
        bounds=RamStateBounds(
            session_max_owned_bytes=charge_a,
            process_max_owned_bytes=base + charge_a,
        )
    )
    assert at.process_owned_bytes == base
    at_owner = at.acquire(ns_a)
    at_admit = at_owner.admit(state_a, result_a, ns_a, expected_revision=0)
    assert at_admit.outcome is RamStateOutcome.ADMITTED
    assert at_admit.charged_bytes == charge_a
    assert at.process_owned_bytes == base + charge_a
    # ONE-OVER: admitting both owners would exceed the
    # process cap by exactly one measured unit, so the
    # second admission must refuse at the process gate.  The
    # session ceiling is a distinct legal value large enough
    # for each measured owner (the process gate is the
    # refuser).
    cap = base + charge_a + charge_b - 1
    s_over = base + charge_a
    over = RamStateOwnerRegistry(
        bounds=RamStateBounds(
            session_max_owned_bytes=s_over,
            process_max_owned_bytes=cap,
        )
    )
    assert over.process_owned_bytes == base
    over_a = over.acquire(ns_a)
    over_b = over.acquire(ns_b)
    over_admit_a = over_a.admit(state_a, result_a, ns_a, expected_revision=0)
    over_admit_b = over_b.admit(state_b, result_b, ns_b, expected_revision=0)
    assert over_admit_a.outcome is RamStateOutcome.ADMITTED
    assert over_admit_b.outcome is RamStateOutcome.REFUSED
    assert over_admit_b.limitation is RamStateLimitation.PROCESS_OWNED_BYTES_OVER_BOUND
    assert over_admit_b.http_status == RAM_HTTP_CAPACITY_STATUS
    assert over_admit_b.snapshot is None
    # The refused second owner still retains its OWN base
    # metadata: the process occupancy includes it.
    base_b = ram_owner_base_charge(ns_b)
    assert over.process_owned_bytes == base + charge_a + base_b
    assert over_a.owned_bytes == charge_a
    assert over_b.owned_bytes == base_b
    assert over_a.lookup(_root_key(result_a), ns_a).outcome is RamStateOutcome.FOUND
    assert over_b.lookup(_root_key(result_b), ns_b).outcome is RamStateOutcome.NOT_FOUND


def test_d_session_override_never_bypasses_process_ceiling() -> None:
    ns, state, result = _ready_t(MODES[0], "ram019d-by")
    charge = _measure_first_charge(RamStateOwnerRegistry(), ns, state, result)
    base = _configured_baseline(charge, charge * 2)
    # The owner session ceiling is LEGALLY overridden to
    # exactly the measured charge (the session gate passes),
    # while the process cap sits one measured unit below the
    # measured baseline plus charge: the process gate must
    # still refuse.  Both bound fields are DISTINCT ints.
    s_reg = base + charge - 1
    p_reg = base + charge - 1
    registry = RamStateOwnerRegistry(
        bounds=RamStateBounds(
            session_max_owned_bytes=s_reg,
            process_max_owned_bytes=p_reg,
        )
    )
    assert registry.process_owned_bytes == base
    owner = registry.new_owner(ns, session_max_owned_bytes=charge)
    admit = owner.admit(state, result, ns, expected_revision=0)
    assert admit.outcome is RamStateOutcome.REFUSED
    assert admit.limitation is RamStateLimitation.PROCESS_OWNED_BYTES_OVER_BOUND
    assert admit.http_status == RAM_HTTP_CAPACITY_STATUS


# --- h. Explicit teardown frees exactly this namespace ----------------


def test_h_teardown_frees_and_preserves_others() -> None:
    ns_a, state_a, result_a = _ready_t(MODES[0], "ram019h-a")
    ns_b, state_b, result_b = _ready_t(MODES[0], "ram019h-b")
    registry = RamStateOwnerRegistry()
    owner_a = registry.acquire(ns_a)
    owner_b = registry.acquire(ns_b)
    admit_a = owner_a.admit(state_a, result_a, ns_a, expected_revision=0)
    admit_b = owner_b.admit(state_b, result_b, ns_b, expected_revision=0)
    assert admit_a.outcome is RamStateOutcome.ADMITTED
    assert admit_b.outcome is RamStateOutcome.ADMITTED
    total = registry.process_owned_bytes
    torn = owner_a.teardown(ns_a)
    assert torn.outcome is RamStateOutcome.TEARDOWN
    assert torn.limitation is None
    assert torn.freed_bytes == admit_a.charged_bytes
    assert registry.process_owned_bytes == total - admit_a.charged_bytes
    assert owner_a.owned_bytes == 0
    assert owner_a.snapshot is None
    assert registry.get(ns_a) is None
    survivor = owner_b.lookup(_root_key(result_b), ns_b)
    assert survivor.outcome is RamStateOutcome.FOUND
    assert (
        owner_a.admit(state_a, result_a, ns_a, expected_revision=1).limitation
        is RamStateLimitation.EPOCH_FENCED
    )
    assert owner_a.lookup(_root_key(result_a), ns_a).limitation is RamStateLimitation.EPOCH_FENCED
    assert owner_a.teardown(ns_a).limitation is RamStateLimitation.EPOCH_FENCED


# --- j. Malformed joins refuse with fixed typed errors ----------------


def test_j_malformed_joins_refuse_before_commit() -> None:
    ns, state, result = _ready_t(MODES[0], "ram019j-1")
    _, state_other, _ = _ready_t(MODES[0], "ram019j-2")
    registry = RamStateOwnerRegistry()
    owner = registry.acquire(ns)
    with pytest.raises(RamStateInputError):
        owner.admit(ns, result, ns, expected_revision=0)
    with pytest.raises(RamStateInputError):
        owner.admit(state, ns, ns, expected_revision=0)
    non_ready = result.model_copy(update={"outcome": RootRegionAdmissionOutcome.REFUSED})
    assert non_ready.admission is not None
    with pytest.raises(RamStateInputError):
        owner.admit(state, non_ready, ns, expected_revision=0)
    carried = result.r_result
    assert carried is not None
    detached = result.model_copy(
        update={"r_result": carried.model_copy(update={"state": state_other})}
    )
    with pytest.raises(RamStateInputError):
        owner.admit(state, detached, ns, expected_revision=0)
    missing = RootRegionAdmissionResult.model_construct()
    with pytest.raises(RamStateInputError):
        owner.admit(state, missing, ns, expected_revision=0)
    assert owner.snapshot is None
    assert owner.revision == 0
    assert owner.owned_bytes == ram_owner_base_charge(ns)


def test_j_lookup_key_and_frozen_models() -> None:
    ns, state, result = _ready_t(MODES[0], "ram019j-3")
    registry = RamStateOwnerRegistry()
    owner = registry.acquire(ns)
    admit = owner.admit(state, result, ns, expected_revision=0)
    assert admit.outcome is RamStateOutcome.ADMITTED
    snapshot = admit.snapshot
    assert snapshot is not None
    with pytest.raises(RamStateInputError):
        owner.lookup(123, ns)
    assert owner.lookup(_root_key(result), ns).outcome is RamStateOutcome.FOUND
    with pytest.raises(ValidationError):
        snapshot.owned_bytes = snapshot.owned_bytes + 1
    with pytest.raises(ValidationError):
        admit.charged_bytes = 0


# --- k. Commit CAS fence and concurrent single commit -----------------


def test_k_commit_cas_fence() -> None:
    ns, state, result = _ready_t(MODES[0], "ram019k-1")
    registry = RamStateOwnerRegistry()
    owner = registry.acquire(ns)
    early = owner.admit(state, result, ns, expected_revision=5)
    assert early.outcome is RamStateOutcome.REFUSED
    assert early.limitation is RamStateLimitation.REVISION_MISMATCH
    assert early.snapshot is None
    assert early.revision == 0
    first = owner.admit(state, result, ns, expected_revision=0)
    assert first.outcome is RamStateOutcome.ADMITTED
    assert first.revision == 1
    stale = owner.admit(state, result, ns, expected_revision=0)
    assert stale.outcome is RamStateOutcome.REFUSED
    assert stale.limitation is RamStateLimitation.REVISION_MISMATCH
    assert stale.snapshot is first.snapshot
    second = owner.admit(state, result, ns, expected_revision=1)
    assert second.outcome is RamStateOutcome.ADMITTED
    assert second.revision == 2
    with pytest.raises(RamStateInputError):
        owner.admit(state, result, ns, expected_revision=-1)
    with pytest.raises(RamStateInputError):
        owner.admit(state, result, ns, expected_revision="1")  # type: ignore[arg-type]
    assert owner.revision == 2


def test_k_concurrent_admit_single_commit() -> None:
    ns, state, result = _ready_t(MODES[0], "ram019k-2")
    registry = RamStateOwnerRegistry()
    owner = registry.acquire(ns)
    outcomes: list[RamStateAdmissionResult] = []
    lock = threading.Lock()

    def worker() -> None:
        admit = owner.admit(state, result, ns, expected_revision=0)
        with lock:
            outcomes.append(admit)

    errors = _run_parallel([worker] * 4)
    assert not errors
    admitted = [a for a in outcomes if a.outcome is RamStateOutcome.ADMITTED]
    refused = [a for a in outcomes if a.outcome is RamStateOutcome.REFUSED]
    assert len(admitted) == 1
    assert len(refused) == 3
    assert all(a.limitation is RamStateLimitation.REVISION_MISMATCH for a in refused)
    assert owner.revision == 1


def test_k_concurrent_acquire_single_owner() -> None:
    ns, _state, _result = _ready_t(MODES[0], "ram019k-3")
    registry = RamStateOwnerRegistry()
    shell = registry.process_owned_bytes
    base = ram_owner_base_charge(ns)
    owners: list[RamStateOwner] = []
    lock = threading.Lock()

    def worker() -> None:
        owner = registry.acquire(ns)
        with lock:
            owners.append(owner)

    errors = _run_parallel([worker] * 8)
    assert not errors
    assert len(owners) == 8
    assert all(owner is owners[0] for owner in owners)
    assert registry.process_owned_bytes == shell + base
    assert owners[0].owned_bytes == base
    assert registry.get(ns) is owners[0]


# --- l. Occupancy recipe on the actual retained graph -----------------


def test_l_occupancy_recipe_law() -> None:
    ns, state, result = _ready_t(MODES[0], "ram019l-1")
    registry = RamStateOwnerRegistry()
    shell = registry.process_owned_bytes
    assert shell > 0
    owner = registry.acquire(ns)
    base = ram_owner_base_charge(ns)
    assert owner.owned_bytes == base
    assert registry.process_owned_bytes == shell + base
    admit = owner.admit(state, result, ns, expected_revision=0)
    assert admit.outcome is RamStateOutcome.ADMITTED
    charge = admit.charged_bytes
    assert charge > base
    assert charge > result.entry_source_bytes
    snapshot = admit.snapshot
    assert snapshot is not None
    assert snapshot.owned_bytes == charge
    assert charge == ram_retained_owned_bytes(ns, state, result, owner.history, snapshot)
    torn = owner.teardown(ns)
    assert torn.outcome is RamStateOutcome.TEARDOWN
    assert torn.freed_bytes == charge
    assert owner.owned_bytes == 0
    assert registry.process_owned_bytes == shell
    with pytest.raises(RamStateAccountingError):
        _charge_object(object(), set())


# --- f. Genuine P->T source/currentness transitions (2 x 2) -----------


def _region_transition(
    mode: AdmissionMode,
    endpoint: str,
    lineage: str,
    root_body: str = V2,
    call_id: str = "m1",
) -> tuple[
    RootRegionLineageNamespace,
    RootRegionLineageState,
    RootRegionAdmissionResult,
    RootRegionLineageState,
    RootRegionLineageState,
    RootRegionAdmissionResult,
]:
    """A genuine 018-p bootstrap plus a MIXED region read: the
    new root region acquires source AND authority without any
    independent singleton, and BOTH record sets are derived
    through the actual complete T consumer (the bootstrap,
    the issued intermediate state, the observed state and its
    READY derivation are all returned)."""
    ns, s0 = r_bootstrap(mode, lineage)
    result0 = derive_root_region_admission(s0, ns)
    assert result0.outcome is RootRegionAdmissionOutcome.READY
    t1 = r_issue(s0, ns, call_id, endpoint, (CAUSAL_ROOT_FACT,), MIX_CMD)
    assert t1.outcome is RootLineageOutcome.ACCEPTED, t1.diagnostics
    t2 = r_observe(
        t1.state,
        ns,
        (read_request(endpoint, call_id, _mixed_body(A_TEXT, MARK, root_body), MIX_CMD),),
    )
    assert t2.outcome is RootLineageOutcome.ACCEPTED, (
        t2.outcome,
        t2.diagnostics,
    )
    s2 = t2.state
    result2 = derive_root_region_admission(s2, ns)
    assert result2.outcome is RootRegionAdmissionOutcome.READY, result2.diagnostics
    return ns, s0, result0, t1.state, s2, result2


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_f_source_currentness_transitions(mode: AdmissionMode, endpoint: str) -> None:
    """Genuine P->T source/currentness transitions: the mixed
    region read selects a DISTINCT canonical root key, the
    superseded v1 entry object stays retained in the
    historical catalog, P observation replay is a no-op, an
    older genuine state is a refused rollback, a divergent
    sibling-P fork is refused at the SAME P revision, and a
    genuine revert restores the bootstrap canonical key with
    the retained v1 entry object surviving."""
    ns, s0, result0, s_issued, s2, result2 = _region_transition(
        mode, endpoint, f"ram019f-{endpoint}"
    )
    k0 = _root_key(result0)
    k1 = _root_key(result2)
    assert k1 != k0
    adm0 = result0.admission
    adm2 = result2.admission
    assert adm0 is not None and adm2 is not None
    e0 = adm0.root_entry
    e2 = adm2.root_entry
    # Selected-source vs bootstrap distinction retained on the
    # admission parent.
    assert e0.root_source is not None
    assert e2.root_source is not None
    assert e0.root_source.kind == "envelope"
    assert e2.root_source.kind == "read_region"
    registry = RamStateOwnerRegistry()
    owner = registry.acquire(ns)
    first = owner.admit(s0, result0, ns, expected_revision=0)
    assert first.outcome is RamStateOutcome.ADMITTED
    charge0 = first.charged_bytes
    second = owner.admit(s2, result2, ns, expected_revision=1)
    assert second.outcome is RamStateOutcome.ADMITTED
    assert second.revision == 2
    charge2 = second.charged_bytes
    # Catalog growth: the retained v1 entry plus the NEW
    # admitted content makes the transition charge strictly
    # larger than the bootstrap charge.
    assert charge2 > charge0
    # Supersession: the current row is the new key; the old
    # key is no longer lookup-eligible, but the v1 ENTRY
    # OBJECT is retained (historical catalog, never destroyed).
    hit = owner.lookup(k1, ns)
    assert hit.outcome is RamStateOutcome.FOUND
    assert hit.entry is e2
    miss = owner.lookup(k0, ns)
    assert miss.outcome is RamStateOutcome.NOT_FOUND
    assert any(item is e0 for item in owner.history)
    assert any(item is e2 for item in owner.history)
    # P-level observation replay is a no-op: the SAME original
    # retained occurrence, the SAME state, no revision advance;
    # the populated owner is untouched.
    snap2 = second.snapshot
    assert snap2 is not None
    t3 = r_observe(
        s2,
        ns,
        (read_request(endpoint, "m1", _mixed_body(A_TEXT, MARK, V2), MIX_CMD),),
    )
    assert t3.outcome is RootLineageOutcome.REPLAYED
    assert t3.state is s2
    assert t3.diagnostics == ()
    assert owner.snapshot is snap2
    assert owner.revision == 2
    assert owner.owned_bytes == charge2
    assert owner.lookup(k1, ns).outcome is RamStateOutcome.FOUND
    # Rollback: an OLDER genuine P state (issued, not yet
    # observed) at the current fence is refused without any
    # commit.
    result1 = derive_root_region_admission(s_issued, ns)
    assert result1.outcome is RootRegionAdmissionOutcome.READY
    back = owner.admit(s_issued, result1, ns, expected_revision=2)
    assert back.outcome is RamStateOutcome.REFUSED
    assert back.limitation is RamStateLimitation.STALE_STATE_REVISION
    assert owner.revision == 2
    assert owner.snapshot is snap2
    assert owner.owned_bytes == charge2
    assert owner.lookup(k1, ns).entry is e2
    # Divergent sibling-P fork: TWO genuine transitions from
    # the SAME prior state s0 give distinct legal states at
    # the SAME P revision; the second one is a fork at the
    # owner fence (not a replay).
    tf1 = r_issue(s0, ns, "fa", endpoint, (CAUSAL_ROOT_FACT,), MIX_CMD)
    assert tf1.outcome is RootLineageOutcome.ACCEPTED, tf1.diagnostics
    tf2 = r_observe(
        tf1.state,
        ns,
        (read_request(endpoint, "fa", _mixed_body(A_TEXT, MARK, V2), MIX_CMD),),
    )
    assert tf2.outcome is RootLineageOutcome.ACCEPTED, (
        tf2.outcome,
        tf2.diagnostics,
    )
    tg1 = r_issue(s0, ns, "fb", endpoint, (CAUSAL_ROOT_FACT,), MIX_CMD)
    assert tg1.outcome is RootLineageOutcome.ACCEPTED, tg1.diagnostics
    tg2 = r_observe(
        tg1.state,
        ns,
        (read_request(endpoint, "fb", _mixed_body(A_TEXT, MARK, V3), MIX_CMD),),
    )
    assert tg2.outcome is RootLineageOutcome.ACCEPTED, (
        tg2.outcome,
        tg2.diagnostics,
    )
    sfa, sfb = tf2.state, tg2.state
    assert sfa is not sfb
    assert sfa.revision == sfb.revision
    rfa = derive_root_region_admission(sfa, ns)
    rfb = derive_root_region_admission(sfb, ns)
    assert rfa.outcome is RootRegionAdmissionOutcome.READY
    assert rfb.outcome is RootRegionAdmissionOutcome.READY
    kfa, kfb = _root_key(rfa), _root_key(rfb)
    assert kfa != kfb
    fork_owner = RamStateOwnerRegistry().acquire(ns)
    f1 = fork_owner.admit(sfa, rfa, ns, expected_revision=0)
    assert f1.outcome is RamStateOutcome.ADMITTED
    f2 = fork_owner.admit(sfb, rfb, ns, expected_revision=1)
    assert f2.outcome is RamStateOutcome.REFUSED
    assert f2.limitation is RamStateLimitation.STALE_STATE_REVISION
    assert f2.snapshot is f1.snapshot
    assert fork_owner.revision == 1
    assert fork_owner.owned_bytes == f1.charged_bytes
    assert fork_owner.lookup(kfa, ns).outcome is RamStateOutcome.FOUND
    assert fork_owner.lookup(kfb, ns).outcome is RamStateOutcome.NOT_FOUND
    # Genuine revert: a genuinely NEW descendant carrying the
    # OLD bootstrap bytes restores the bootstrap canonical
    # key; the retained v1 entry object survives the cycle.
    frontier = (occurrences(s2, "m1")[0].occurrence_id,)
    tr1 = r_issue(s2, ns, "r1", endpoint, frontier, MIX_CMD)
    assert tr1.outcome is RootLineageOutcome.ACCEPTED, tr1.diagnostics
    tr2 = r_observe(
        tr1.state,
        ns,
        (read_request(endpoint, "r1", _mixed_body(A_TEXT, MARK, ROOT_TEXT), MIX_CMD),),
    )
    assert tr2.outcome is RootLineageOutcome.ACCEPTED, (
        tr2.outcome,
        tr2.diagnostics,
    )
    s3 = tr2.state
    result3 = derive_root_region_admission(s3, ns)
    assert result3.outcome is RootRegionAdmissionOutcome.READY, result3.diagnostics
    k2 = _root_key(result3)
    assert k2 == k0
    third = owner.admit(s3, result3, ns, expected_revision=2)
    assert third.outcome is RamStateOutcome.ADMITTED
    hit0 = owner.lookup(k0, ns)
    assert hit0.outcome is RamStateOutcome.FOUND
    adm3 = result3.admission
    assert adm3 is not None
    assert hit0.entry is adm3.root_entry
    assert any(item is e0 for item in owner.history)
    assert third.charged_bytes >= charge2


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_f_refused_update_preserves_populated_owner(mode: AdmissionMode, endpoint: str) -> None:
    """A refused UPDATE on an ALREADY POPULATED owner (session
    gate, process gate and CAS) leaves the owner snapshot,
    revision, catalog, occupancy and existing lookup exactly
    preserved -- not just an empty-owner refusal."""
    ns, s0, result0, _s_issued, s2, result2 = _region_transition(
        mode, endpoint, f"ram019fu-{endpoint}"
    )
    charge0 = _measure_first_charge(RamStateOwnerRegistry(), ns, s0, result0)
    # The TRUE s0->s2 UPDATE charge on a POPULATED owner: the
    # historical bootstrap entry/catalog is retained, so it
    # exceeds the empty-owner first charge of s2.  Measure it
    # on a genuine probe owner, not from an empty-owner first
    # admit.
    probe = RamStateOwnerRegistry()
    probe_owner = probe.acquire(ns)
    probe_first = probe_owner.admit(s0, result0, ns, expected_revision=0)
    assert probe_first.outcome is RamStateOutcome.ADMITTED
    probe_update = probe_owner.admit(s2, result2, ns, expected_revision=1)
    assert probe_update.outcome is RamStateOutcome.ADMITTED
    update_charge = probe_update.charged_bytes
    assert update_charge > charge0
    base = _configured_baseline(charge0, charge0 + update_charge)
    key0 = _root_key(result0)
    key1 = _root_key(result2)
    # SESSION-gate update refusal on a populated owner.
    reg_s = RamStateOwnerRegistry(
        bounds=RamStateBounds(
            session_max_owned_bytes=charge0,
            process_max_owned_bytes=RAM_PROCESS_MAX_OWNED_BYTES_DEFAULT,
        )
    )
    owner_s = reg_s.acquire(ns)
    first_s = owner_s.admit(s0, result0, ns, expected_revision=0)
    assert first_s.outcome is RamStateOutcome.ADMITTED
    snap_s = first_s.snapshot
    assert snap_s is not None
    hist_s = owner_s.history
    proc_before = reg_s.process_owned_bytes
    update_s = owner_s.admit(s2, result2, ns, expected_revision=1)
    assert update_s.outcome is RamStateOutcome.REFUSED
    assert update_s.limitation is RamStateLimitation.SESSION_OWNED_BYTES_OVER_BOUND
    assert update_s.http_status == RAM_HTTP_CAPACITY_STATUS
    assert owner_s.revision == 1
    assert owner_s.snapshot is snap_s
    assert owner_s.owned_bytes == charge0
    assert owner_s.history is hist_s
    assert reg_s.process_owned_bytes == proc_before
    assert owner_s.lookup(key0, ns).outcome is RamStateOutcome.FOUND
    assert owner_s.lookup(key1, ns).outcome is RamStateOutcome.NOT_FOUND
    # PROCESS-gate update refusal on a populated owner: the
    # session ceiling is large enough for the update, only the
    # measured process cap (one below the ACTUAL populated
    # update charge on top of the baseline) refuses.
    cap = base + update_charge - 1
    s_proc = base + update_charge - 1
    reg_p = RamStateOwnerRegistry(
        bounds=RamStateBounds(
            session_max_owned_bytes=s_proc,
            process_max_owned_bytes=cap,
        )
    )
    assert reg_p.process_owned_bytes == base
    owner_p = reg_p.acquire(ns)
    first_p = owner_p.admit(s0, result0, ns, expected_revision=0)
    assert first_p.outcome is RamStateOutcome.ADMITTED
    snap_p = first_p.snapshot
    assert snap_p is not None
    hist_p = owner_p.history
    proc_p_before = reg_p.process_owned_bytes
    update_p = owner_p.admit(s2, result2, ns, expected_revision=1)
    assert update_p.outcome is RamStateOutcome.REFUSED
    assert update_p.limitation is RamStateLimitation.PROCESS_OWNED_BYTES_OVER_BOUND
    assert update_p.http_status == RAM_HTTP_CAPACITY_STATUS
    assert owner_p.revision == 1
    assert owner_p.snapshot is snap_p
    assert owner_p.owned_bytes == charge0
    assert owner_p.history is hist_p
    assert reg_p.process_owned_bytes == proc_p_before
    assert owner_p.lookup(key0, ns).outcome is RamStateOutcome.FOUND
    # CAS refusal on a populated owner.
    stale_s = owner_s.admit(s2, result2, ns, expected_revision=9)
    assert stale_s.outcome is RamStateOutcome.REFUSED
    assert stale_s.limitation is RamStateLimitation.REVISION_MISMATCH
    assert owner_s.snapshot is snap_s
    assert owner_s.revision == 1
    assert owner_s.lookup(key0, ns).outcome is RamStateOutcome.FOUND


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_f_unrelated_b_preserves_a_key(mode: AdmissionMode, endpoint: str) -> None:
    """Requirement 7, same session: the bootstrap root declares
    BOTH A.md and B.md; a genuine singleton A read is admitted
    into ONE owner (its FILE semantic key and retained original
    proof are recorded); then an UNRELATED genuine singleton B
    read in the SAME P lineage and the SAME owner is admitted.
    B's admission must not change unchanged A's key: A's key
    stays lookup-eligible and valid, the first retained A entry
    object survives in the historical catalog, and the owner
    revision / occupancy may advance."""
    ns, s0 = r_bootstrap(mode, f"ram019ab-{mode.value}-{endpoint}", root_body=ROOT_AB)
    result0 = derive_root_region_admission(s0, ns)
    assert result0.outcome is RootRegionAdmissionOutcome.READY
    registry = RamStateOwnerRegistry()
    owner = registry.acquire(ns)
    a0 = owner.admit(s0, result0, ns, expected_revision=0)
    assert a0.outcome is RamStateOutcome.ADMITTED
    # Genuine singleton A read in the same lineage.
    t1 = r_issue(s0, ns, "b1", endpoint, (CAUSAL_ROOT_FACT,), "cat A.md")
    assert t1.outcome is RootLineageOutcome.ACCEPTED, t1.diagnostics
    t2 = r_observe(t1.state, ns, (read_request(endpoint, "b1", A_TEXT, "cat A.md"),))
    assert t2.outcome is RootLineageOutcome.ACCEPTED, t2.diagnostics
    s1 = t2.state
    result1 = derive_root_region_admission(s1, ns)
    assert result1.outcome is RootRegionAdmissionOutcome.READY, result1.diagnostics
    adm1 = result1.admission
    assert adm1 is not None
    a_rows1 = [row for row in adm1.path_associations if row.path == "A.md"]
    assert len(a_rows1) == 1
    assert len(a_rows1[0].content_keys) == 1
    key_a = a_rows1[0].content_keys[0]
    entry_a = next(e for e in adm1.entries if e.content_key == key_a)
    occ1 = next(o for o in s1.d_state.occurrences if o.call_id == "b1")
    assert entry_a.proof is occ1.proof
    a1 = owner.admit(s1, result1, ns, expected_revision=1)
    assert a1.outcome is RamStateOutcome.ADMITTED
    charge_a = a1.charged_bytes
    hit_a = owner.lookup(key_a, ns)
    assert hit_a.outcome is RamStateOutcome.FOUND
    # Unrelated genuine singleton B read in the SAME lineage/owner.
    t3 = r_issue(s1, ns, "b2", endpoint, (CAUSAL_ROOT_FACT,), "cat B.md")
    assert t3.outcome is RootLineageOutcome.ACCEPTED, t3.diagnostics
    t4 = r_observe(t3.state, ns, (read_request(endpoint, "b2", B_TEXT, "cat B.md"),))
    assert t4.outcome is RootLineageOutcome.ACCEPTED, t4.diagnostics
    s2 = t4.state
    result2 = derive_root_region_admission(s2, ns)
    assert result2.outcome is RootRegionAdmissionOutcome.READY, result2.diagnostics
    adm2 = result2.admission
    assert adm2 is not None
    b_rows2 = [row for row in adm2.path_associations if row.path == "B.md"]
    assert len(b_rows2) == 1
    key_b = b_rows2[0].content_keys[0]
    assert key_b != key_a
    # Unchanged A keeps its exact stable semantic key and the SAME
    # retained original proof by identity in the new derivation.
    a_rows2 = [row for row in adm2.path_associations if row.path == "A.md"]
    assert len(a_rows2) == 1
    assert a_rows2[0].content_keys == (key_a,)
    entry_a2 = next(e for e in adm2.entries if e.content_key == key_a)
    assert entry_a2.proof is entry_a.proof
    a2 = owner.admit(s2, result2, ns, expected_revision=2)
    assert a2.outcome is RamStateOutcome.ADMITTED
    # A's key is still valid after the unrelated B admission, and
    # B's own key is valid too.
    hit = owner.lookup(key_a, ns)
    assert hit.outcome is RamStateOutcome.FOUND
    hit_b = owner.lookup(key_b, ns)
    assert hit_b.outcome is RamStateOutcome.FOUND
    # The FIRST retained A entry object survives in the catalog.
    assert any(item is entry_a for item in owner.history)
    # The owner revision / occupancy may advance with the genuine
    # transition.
    assert owner.revision == 3
    assert owner.owned_bytes >= charge_a


# --- e. Genuine distinct-binding namespace isolation ------------------


@pytest.mark.parametrize("mode", MODES)
def test_e_namespace_isolation_genuine_bindings(mode: AdmissionMode) -> None:
    """Genuine distinct principal/session/config bindings (not
    merely a different lineage string): the SAME lineage label
    under distinct trusted identities yields distinct
    namespaces, owners and fully isolated operations."""
    id_a = RequestIdentity(
        principal="ram019e-principal-a",
        route="ram019e-route",
        session="ram019e-session-a",
        repository="ram019e-repo",
    )
    id_b = RequestIdentity(
        principal="ram019e-principal-b",
        route="ram019e-route",
        session="ram019e-session-b",
        repository="ram019e-repo",
    )
    ns_a, s_a = r_bootstrap(mode, "ram019e-shared", identity=id_a)
    ns_b, s_b = r_bootstrap(mode, "ram019e-shared", identity=id_b, model_identity="ram019e-model-b")
    assert ns_a.lineage_key != ns_b.lineage_key
    assert ns_a.principal != ns_b.principal
    assert ns_a.session != ns_b.session
    assert ns_a.model_identity != ns_b.model_identity
    r_a = derive_root_region_admission(s_a, ns_a)
    r_b = derive_root_region_admission(s_b, ns_b)
    assert r_a.outcome is RootRegionAdmissionOutcome.READY
    assert r_b.outcome is RootRegionAdmissionOutcome.READY
    registry = RamStateOwnerRegistry()
    owner_a = registry.acquire(ns_a)
    owner_b = registry.acquire(ns_b)
    a1 = owner_a.admit(s_a, r_a, ns_a, expected_revision=0)
    b1 = owner_b.admit(s_b, r_b, ns_b, expected_revision=0)
    assert a1.outcome is RamStateOutcome.ADMITTED
    assert b1.outcome is RamStateOutcome.ADMITTED
    key_a = _root_key(r_a)
    key_b = _root_key(r_b)
    # Cross-namespace lookups / commits / teardowns are
    # refused by the fixed typed boundary law; a foreign
    # namespace never reaches a foreign owner.
    cross = owner_a.lookup(key_b, ns_b)
    assert cross.outcome is RamStateOutcome.NOT_FOUND
    assert cross.limitation is RamStateLimitation.OWNER_NAMESPACE_MISMATCH
    cross_b = owner_b.lookup(key_a, ns_a)
    assert cross_b.outcome is RamStateOutcome.NOT_FOUND
    assert cross_b.limitation is RamStateLimitation.OWNER_NAMESPACE_MISMATCH
    with pytest.raises(RamStateInputError):
        owner_b.admit(s_a, r_a, ns_a, expected_revision=0)
    wrong_tear = owner_a.teardown(ns_b)
    assert wrong_tear.outcome is RamStateOutcome.REFUSED
    assert wrong_tear.limitation is RamStateLimitation.OWNER_NAMESPACE_MISMATCH
    assert wrong_tear.freed_bytes == 0
    assert owner_a.snapshot is not None
    torn = owner_a.teardown(ns_a)
    assert torn.outcome is RamStateOutcome.TEARDOWN
    assert owner_a.owned_bytes == 0
    # The other session survives the first teardown.
    assert owner_b.lookup(key_b, ns_b).outcome is RamStateOutcome.FOUND
    assert owner_b.owned_bytes == b1.charged_bytes
    assert registry.get(ns_a) is None


# --- j2. Canonical forges of the nested T law at the owner -------------


@pytest.mark.parametrize("mode", MODES)
def test_j_canonical_forge_negatives(mode: AdmissionMode) -> None:
    """The ACTUAL nested T law at the owner boundary: complete-
    copy forges (canonical leaf, rekeyed retained group,
    reverse row, retained count, stale scope key) are refused
    with the fixed sanitized input error, the owner stays
    exactly as committed, each through a genuine positive
    first."""
    ns, s0 = r_bootstrap(mode, f"ram019jf-{mode.value}")
    result = derive_root_region_admission(s0, ns)
    assert result.outcome is RootRegionAdmissionOutcome.READY
    adm = result.admission
    assert adm is not None
    root_entry = adm.root_entry
    kr = root_entry.key_record
    g0 = kr.ownership_groups[0]
    registry = RamStateOwnerRegistry()
    owner = registry.acquire(ns)
    first = owner.admit(s0, result, ns, expected_revision=0)
    assert first.outcome is RamStateOutcome.ADMITTED
    snap = first.snapshot
    assert snap is not None
    charge = first.charged_bytes
    hist = owner.history

    def _refuses(bad: RootRegionAdmissionResult) -> None:
        with pytest.raises(RamStateInputError):
            owner.admit(s0, bad, ns, expected_revision=1)
        assert owner.revision == 1
        assert owner.snapshot is snap
        assert owner.owned_bytes == charge
        assert owner.history is hist
        assert owner.lookup(_root_key(result), ns).outcome is RamStateOutcome.FOUND

    # 1. forged canonical leaf (single-field model_copy chain).
    _refuses(
        result.model_copy(
            update={
                "admission": adm.model_copy(
                    update={"root_entry": root_entry.model_copy(update={"content_key": "0" * 64})}
                )
            }
        )
    )
    # 2. forged retained group: digest changed AND canonically
    #    REKEYED so only the retained-content / group fence
    #    can fire.
    g_bad = g0.model_copy(update={"group_digest": "0" * 64})
    kr_bad = kr.model_copy(update={"ownership_groups": (g_bad, *kr.ownership_groups[1:])})
    _refuses(
        result.model_copy(
            update={
                "admission": adm.model_copy(
                    update={
                        "root_entry": root_entry.model_copy(
                            update={
                                "key_record": kr_bad,
                                "content_key": _canonical_entry_key(kr_bad),
                            }
                        )
                    }
                )
            }
        )
    )
    # 3. forged reverse-relation row.
    row = adm.path_associations[0]
    _refuses(
        result.model_copy(
            update={
                "admission": adm.model_copy(
                    update={
                        "path_associations": (row.model_copy(update={"content_keys": ("0" * 64,)}),)
                    }
                )
            }
        )
    )
    # 4. forged retained count.
    _refuses(
        result.model_copy(
            update={
                "admission": adm.model_copy(update={"entries_retained": adm.entries_retained + 7})
            }
        )
    )
    # 5. stale T scope key.
    _refuses(result.model_copy(update={"scope_key": "f" * 64}))


# --- i. No host IO after fixture/setup on operational paths -----------


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_i_no_host_io_after_setup(
    mode: AdmissionMode, endpoint: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    """No host IO after fixture/setup: the closed 24-facility
    trap is open across the populated owner's lookups (hit,
    miss and every retained row), catalog access, record
    rendering, a CAS refusal and the teardown."""
    ns, _s0, _result0, _s_issued, s2, result2 = _region_transition(
        mode, endpoint, f"ram019i-{endpoint}"
    )
    registry = RamStateOwnerRegistry()
    owner = registry.acquire(ns)
    admit = owner.admit(s2, result2, ns, expected_revision=0)
    assert admit.outcome is RamStateOutcome.ADMITTED
    snap = admit.snapshot
    assert snap is not None
    calls: list[str] = []

    def trap(label: str) -> Callable[..., Any]:
        def refused(*trap_args: Any, **trap_kwargs: Any) -> Any:
            calls.append(label)
            raise AssertionError("forbidden host IO: " + label)

        return refused

    for module, name in _host_io_facilities():
        monkeypatch.setattr(module, name, trap(module.__name__ + "." + name))
    # Repeated actual lookup / graph / index operations:
    assert owner.lookup(_root_key(result2), ns).outcome is RamStateOutcome.FOUND
    assert owner.lookup("0" * 64, ns).outcome is RamStateOutcome.NOT_FOUND
    admission = snap.result.admission
    assert admission is not None
    for entry in (admission.root_entry, *admission.entries):
        assert owner.lookup(entry.content_key, ns).outcome is RamStateOutcome.FOUND
    # Traversing the retained CURRENT GRAPH (the actual F overlay
    # nodes and edges), the reverse / path index and the key
    # record metadata (pure data access, no host IO):
    rr2 = snap.result.r_result
    assert rr2 is not None
    f2 = rr2.f_result
    assert f2 is not None
    overlay = f2.overlay
    assert overlay is not None
    for node in overlay.nodes:
        repr(node)
    for edge in overlay.edges:
        repr(edge)
    for row in admission.path_associations:
        repr(row)
        for row_key in row.content_keys:
            assert owner.lookup(row_key, ns).outcome is RamStateOutcome.FOUND
    for entry in (admission.root_entry, *admission.entries):
        for group in entry.key_record.ownership_groups:
            repr(group)
        for path in entry.key_record.member_occurrences:
            repr(path)
    for entry in owner.history:
        repr(entry)
        str(entry)
    for record in (snap, snap.result, snap.result.r_result, admission):
        repr(record)
        str(record)
    stale = owner.admit(s2, result2, ns, expected_revision=9)
    assert stale.outcome is RamStateOutcome.REFUSED
    assert stale.limitation is RamStateLimitation.REVISION_MISMATCH
    torn = owner.teardown(ns)
    assert torn.outcome is RamStateOutcome.TEARDOWN
    assert calls == []


# --- m2. Concurrency: process ceiling race + teardown/reacquire --------


def test_m_concurrent_process_ceiling_race() -> None:
    """Three owners racing the SAME registry process ceiling.
    Every owner's MEASURED base metadata stays charged (all
    THREE bases, including the refused owner's), and the cap
    fits EXACTLY the two LARGEST measured admission deltas on
    top of baseline + all three bases (never all three
    deltas), so exactly two admissions commit and one
    process-503 refusal returns, whatever the thread
    interleaving."""
    records: list[
        tuple[
            RootRegionLineageNamespace,
            RootRegionLineageState,
            RootRegionAdmissionResult,
        ]
    ] = []
    bases: list[int] = []
    deltas: list[int] = []
    # ONE shared probe registry: the probe owners are allocated
    # the SAME distinct epochs (1/2/3, in the same acquisition
    # order) as the race registry, so the measured bases/deltas
    # match the real registry's epoch allocation (a fresh
    # per-record registry would reset every probe owner to
    # epoch 1).
    probe = RamStateOwnerRegistry()
    for tag in ("ram019m-r1", "ram019m-r2", "ram019m-r3"):
        ns, state, result = _ready_t(MODES[0], tag)
        records.append((ns, state, result))
        probe_owner = probe.acquire(ns)
        base_i = probe_owner.owned_bytes
        admit = probe_owner.admit(state, result, ns, expected_revision=0)
        assert admit.outcome is RamStateOutcome.ADMITTED
        bases.append(base_i)
        deltas.append(admit.charged_bytes - base_i)
    _d_lo, d_mid, d_hi = sorted(deltas)
    base = _configured_baseline(d_hi, d_hi + d_mid)
    all_bases = sum(bases)
    cap = base + all_bases + d_mid + d_hi
    s_cap = base + all_bases + d_mid + d_hi
    registry = RamStateOwnerRegistry(
        bounds=RamStateBounds(
            session_max_owned_bytes=s_cap,
            process_max_owned_bytes=cap,
        )
    )
    assert registry.process_owned_bytes == base
    owners = [registry.acquire(ns) for ns, _s, _r in records]
    # The ACTUAL measured owner bases in THIS registry match
    # the probe measurements (base metadata is registry-
    # independent).
    assert [owner.owned_bytes for owner in owners] == bases
    outcomes: list[tuple[RamStateOwner, RamStateAdmissionResult]] = []
    lock = threading.Lock()

    def worker(
        owner: RamStateOwner,
        state: RootRegionLineageState,
        result: RootRegionAdmissionResult,
        ns: RootRegionLineageNamespace,
    ) -> None:
        admit = owner.admit(state, result, ns, expected_revision=0)
        with lock:
            outcomes.append((owner, admit))

    workers: list[Callable[[], None]] = []

    def make_worker(
        owner_i: RamStateOwner,
        state_i: RootRegionLineageState,
        result_i: RootRegionAdmissionResult,
        ns_i: RootRegionLineageNamespace,
    ) -> Callable[[], None]:
        def run() -> None:
            worker(owner_i, state_i, result_i, ns_i)

        return run

    for i in range(3):
        workers.append(make_worker(owners[i], records[i][1], records[i][2], records[i][0]))
    errors = _run_parallel(workers)
    assert not errors
    admitted = [(o, a) for o, a in outcomes if a.outcome is RamStateOutcome.ADMITTED]
    refused = [(o, a) for o, a in outcomes if a.outcome is RamStateOutcome.REFUSED]
    assert len(admitted) == 2
    assert len(refused) == 1
    base_by_owner = dict(zip(owners, bases, strict=True))
    admitted_delta_sum = 0
    for owner, admit in admitted:
        assert admit.http_status is None
        assert owner.owned_bytes == admit.charged_bytes
        admitted_delta_sum += admit.charged_bytes - base_by_owner[owner]
    for owner, admit in refused:
        assert admit.limitation is RamStateLimitation.PROCESS_OWNED_BYTES_OVER_BOUND
        assert admit.http_status == RAM_HTTP_CAPACITY_STATUS
        assert owner.snapshot is None
        assert owner.revision == 0
        assert owner.owned_bytes == base_by_owner[owner]
    # The refused owner's base stays charged in the total.
    total = base + all_bases + admitted_delta_sum
    assert registry.process_owned_bytes == total


def test_m_teardown_reacquire_race() -> None:
    """A teardown racing a registry re-acquire: serialized by
    the registry lock; the final invariant is that the old
    owner is fenced and fully free, and the registry NEVER
    holds it again (None or a DISTINCT successor with a
    newer epoch)."""
    ns, state, result = _ready_t(MODES[0], "ram019m-tr")
    registry = RamStateOwnerRegistry()
    owner = registry.acquire(ns)
    admit = owner.admit(state, result, ns, expected_revision=0)
    assert admit.outcome is RamStateOutcome.ADMITTED
    done: list[str] = []
    lock = threading.Lock()

    def tear_down() -> None:
        torn = owner.teardown(ns)
        with lock:
            done.append("teardown:" + torn.outcome.value)

    def reacquire() -> None:
        successor = registry.acquire(ns)
        with lock:
            done.append("acquire:" + ("same" if successor is owner else "successor"))

    errors = _run_parallel([tear_down, reacquire])
    assert not errors
    assert done.count("teardown:" + RamStateOutcome.TEARDOWN.value) == 1
    assert owner.epoch_fenced
    assert owner.owned_bytes == 0
    current = registry.get(ns)
    assert current is None or current is not owner
    if current is not None:
        assert current.epoch > owner.epoch

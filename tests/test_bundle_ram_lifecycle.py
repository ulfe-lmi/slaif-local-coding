"""Whole-019 lifecycle composition over the ACTUAL accepted
observation -> P -> T -> RAM owner / work plane (order 019-c
item 3).

L1: the substantial 32768-byte multi-dependency source with a
genuine root change and a deliberate old-bytes revert: the
complete observation -> P -> T chain is driven through the
ACTUAL registered RAM owner (mandatory CAS admissions) and the
injected bounded work seam, recording the actual source /
history sizes, the actual work-domain facts and the
retained-occupancy growth; the retained valid payloads survive
supersession and the genuine revert reuses the ORIGINAL
retained root payload without a new invocation.  The explicit
legal 1048576 GraphBounds stage instance is the accepted 018-t
NON-DEFAULT stage configuration, labeled as such (never default
readiness).

L2: the overlapping [A,B] / [A,C] bundle ownership: the work
plane's currentness follows the ACTUAL store keys through the
child-of-one withdrawal and the genuine both-lineage singleton
re-admission.

L3: the BOUNDARYLESS (opaque) [A,B] bundle: ONE work unit, the
standalone-observation conservative withdrawal (the retained
bundle payload is NOT re-served) and the genuine new-bundle
re-admission under the SAME canonical key with the retained
ORIGINAL payload reused.

L4: the adverse-currentness RAM boundary: a trusted complete
boundaryless root-bearing observation (unresolved maximal root
uncertainty) commits the ACTUAL non-READY result as the bounded
quarantine snapshot; the source-absent lookup/resolve cannot
revive the old usable state, an EXACT replay cannot unblock,
and the genuinely proven supported recovery restores usability
with the retained ORIGINAL payloads reused.  L4b: the ACTUAL
capacity-refusal path preserves the old usable snapshot
exactly.

The injected seam is synthetic (prepared-work orchestration
only; actual compiler / tokenizer semantic validation is 021).
The stage stays inert.
"""

from __future__ import annotations

import asyncio
from collections.abc import Callable
from typing import Any

import pytest

from slaif_local_coding.constitution.bundles.bundle_admission_models import (
    AdmissionMode,
    BoundaryClass,
)
from slaif_local_coding.constitution.bundles.causal_history_models import (
    CAUSAL_ROOT_FACT,
)
from slaif_local_coding.constitution.bundles.graph_models import (
    ROOT_FILENAME,
    GraphBounds,
)
from slaif_local_coding.constitution.bundles.ram_state_models import (
    RamStateLimitation,
    RamStateOutcome,
)
from slaif_local_coding.constitution.bundles.ram_work import (
    WorkSeam,
)
from slaif_local_coding.constitution.bundles.ram_work_models import (
    RAM_WORK_WAITER_RESERVATION_BYTES,
    RamWorkLimitation,
    RamWorkOutcome,
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
from slaif_local_coding.constitution.bundles.root_region_graph_models import (
    RootRegionGraphOutcome,
)
from slaif_local_coding.constitution.bundles.root_region_lineage_models import (
    RootRegionLineageNamespace,
    RootRegionLineageState,
)
from tests.test_bundle_ram_work import _work_registry
from tests.test_causal_history import (
    ENDPOINTS,
    MODES,
    frame,
    read_request,
    sha256_hex,
)
from tests.test_root_region_currentness import (
    BOUNDARYLESS_CMD,
    MARK,
    MIX_CMD,
    OPAQUE_BODY,
    mixed_body,
)
from tests.test_root_region_lineage import (
    _host_io_facilities,
    r_bootstrap,
    r_issue,
    r_observe,
)

L4_A = "Synthetic nonroot A.\n"
L4_V2_ROOT = "Second root."

L1_HEADER = "Follow `A.md` and `X.md`.\n"
L1_V1 = L1_HEADER + "x" * (32768 - len(L1_HEADER))
L1_V2_HEADER = L1_HEADER + "Version two.\n"
L1_V2 = L1_V2_HEADER + "x" * (32768 - len(L1_V2_HEADER))
assert len(L1_V1.encode("utf-8")) == 32768
assert len(L1_V2.encode("utf-8")) == 32768

# The LEGAL instance of the original admission stage-work domain
# (accepted in 018-t): an EXPLICIT non-default stage
# configuration, labeled as such -- never default readiness.
L1_LEGAL_STAGE = GraphBounds(max_work_units=1_048_576)

L1_A_BYTES = len("Follow `X.md`.\n")
L1_X_BYTES = len("Follow `Target.md`.\n")
L1_T_BYTES = len("Synthetic target governance.\n")
L1_FILE_BYTES = L1_A_BYTES + L1_X_BYTES + L1_T_BYTES
assert L1_FILE_BYTES == 64

LIFECYCLE_PAYLOAD = b"lifecycle-prepared-019c"


def _lifecycle_seam(calls: list[int]) -> WorkSeam:
    """The bounded synthetic lifecycle seam: one append per
    ACTUAL invocation, a deterministic prepared payload."""

    async def seam() -> bytes:
        calls.append(1)
        return LIFECYCLE_PAYLOAD

    return seam


def _l1_dep_read(
    state: RootRegionLineageState,
    ns: RootRegionLineageNamespace,
    cid: str,
    endpoint: str,
    path: str,
    body: str,
) -> RootRegionLineageState:
    issued = r_issue(state, ns, cid, endpoint, (CAUSAL_ROOT_FACT,), f"cat {path}")
    assert issued.outcome is RootLineageOutcome.ACCEPTED, issued.diagnostics
    obs = r_observe(issued.state, ns, (read_request(endpoint, cid, body, f"cat {path}"),))
    assert obs.outcome is RootLineageOutcome.ACCEPTED, obs.diagnostics
    state_out: RootRegionLineageState = obs.state
    return state_out


def _l1_states(
    mode: AdmissionMode, endpoint: str, lineage: str
) -> tuple[
    RootRegionLineageNamespace,
    RootRegionLineageState,
    RootRegionLineageState,
    RootRegionLineageState,
]:
    """The genuine 32768-byte multi-dependency lineage under the
    explicit legal (NON-DEFAULT) 1048576 stage instance:
    (ns, s_files, s_root2, s_revert) -- the A/X/Target reads,
    the genuinely NEW v2 whole-root read and the deliberate
    old-bytes revert read (a genuinely new descendant of the v2
    occurrence carrying the OLD v1 bytes)."""
    ns, s0 = r_bootstrap(mode, lineage, root_body=L1_V1, graph_bounds=L1_LEGAL_STAGE)
    s_files = _l1_dep_read(s0, ns, "a", endpoint, "A.md", "Follow `X.md`.\n")
    s_files = _l1_dep_read(s_files, ns, "x", endpoint, "X.md", "Follow `Target.md`.\n")
    s_files = _l1_dep_read(
        s_files, ns, "t", endpoint, "Target.md", "Synthetic target governance.\n"
    )
    s_root2 = _l1_dep_read(s_files, ns, "root2", endpoint, ROOT_FILENAME, L1_V2)
    occ_root2 = next(o for o in s_root2.d_state.occurrences if o.call_id == "root2")
    issued = r_issue(
        s_root2, ns, "root1b", endpoint, (occ_root2.occurrence_id,), f"cat {ROOT_FILENAME}"
    )
    assert issued.outcome is RootLineageOutcome.ACCEPTED, issued.diagnostics
    obs = r_observe(
        issued.state,
        ns,
        (read_request(endpoint, "root1b", L1_V1, f"cat {ROOT_FILENAME}"),),
    )
    assert obs.outcome is RootLineageOutcome.ACCEPTED, obs.diagnostics
    return ns, s_files, s_root2, obs.state


L3_ROOT = "Read `A.md` and `B.md` before work."
L3_X = "Synthetic shared member body.\n"
L3_CMD = "cat A.md && cat B.md"


def _l3_states(
    mode: AdmissionMode, endpoint: str, lineage: str
) -> tuple[
    RootRegionLineageNamespace,
    RootRegionLineageState,
    RootRegionLineageState,
    RootRegionLineageState,
]:
    """The genuine BOUNDARYLESS (opaque) [A,B] bundle lineage:
    (ns, s_bundle, s_singleton, s_bundle2) -- the boundaryless
    mixed read (ONE opaque group, no proven per-member digest),
    the genuinely NEW A.md singleton read (which conservatively
    stales the boundaryless bundle) and the genuinely NEW
    complete [A,B] bundle read descended from BOTH the bundle
    and the singleton occurrences (the SAME aggregate bytes: the
    opaque bundle re-admits under its OWN canonical key)."""
    ns, s0 = r_bootstrap(mode, lineage, root_body=L3_ROOT)
    t1 = r_issue(s0, ns, "m1", endpoint, (CAUSAL_ROOT_FACT,), L3_CMD)
    assert t1.outcome is RootLineageOutcome.ACCEPTED, t1.diagnostics
    t2 = r_observe(t1.state, ns, (read_request(endpoint, "m1", L3_X + L3_X, L3_CMD),))
    assert t2.outcome is RootLineageOutcome.ACCEPTED, t2.diagnostics
    s_bundle = t2.state
    m1_occ = next(o for o in s_bundle.d_state.occurrences if o.call_id == "m1")
    t3 = r_issue(s_bundle, ns, "a1", endpoint, (m1_occ.occurrence_id,), "cat A.md")
    assert t3.outcome is RootLineageOutcome.ACCEPTED, t3.diagnostics
    t4 = r_observe(t3.state, ns, (read_request(endpoint, "a1", L3_X, "cat A.md"),))
    assert t4.outcome is RootLineageOutcome.ACCEPTED, t4.diagnostics
    s_singleton = t4.state
    a1_occ = next(o for o in s_singleton.d_state.occurrences if o.call_id == "a1")
    t5 = r_issue(
        s_singleton,
        ns,
        "m2",
        endpoint,
        (m1_occ.occurrence_id, a1_occ.occurrence_id),
        L3_CMD,
    )
    assert t5.outcome is RootLineageOutcome.ACCEPTED, t5.diagnostics
    t6 = r_observe(t5.state, ns, (read_request(endpoint, "m2", L3_X + L3_X, L3_CMD),))
    assert t6.outcome is RootLineageOutcome.ACCEPTED, t6.diagnostics
    return ns, s_bundle, s_singleton, t6.state


def _path_key(result: RootRegionAdmissionResult, path: str) -> str:
    adm = result.admission
    assert adm is not None
    rows = [row for row in adm.path_associations if row.path == path]
    assert len(rows) == 1 and len(rows[0].content_keys) == 1
    return rows[0].content_keys[0]


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
async def test_l1_substantial_root_change_revert_lifecycle(
    mode: AdmissionMode, endpoint: str
) -> None:
    """L1: the substantial 32768-byte multi-dependency source
    through observation -> P -> T -> RAM -> injected work, both
    modes, BOTH representative endpoints: the genuine v2 root
    change rekeys the root entry AND the FILE rows under the new
    governing root digest (the accepted 018-c canonical law), the
    deliberate old-bytes revert RESTORES the original root and
    FILE keys and the retained ORIGINAL payloads are reused
    WITHOUT new invocations, the withdrawn old full keys are
    refused with the fixed currentness fence, and the committed
    occupancy grows with every genuine transition while every
    existing hit stays usable."""
    ns, s_files, s_root2, s_revert = _l1_states(
        mode, endpoint, f"ram019c-l1-{mode.value}-{endpoint}"
    )
    t1 = derive_root_region_admission(s_files, ns)
    t2 = derive_root_region_admission(s_root2, ns)
    t3 = derive_root_region_admission(s_revert, ns)
    for t in (t1, t2, t3):
        assert t.outcome is RootRegionAdmissionOutcome.READY, t.diagnostics
    # The explicit non-default stage configuration (labeled):
    assert ns.graph_bounds.max_work_units == 1_048_576
    # The ACTUAL recorded source / history sizes:
    for t, kind, digest in (
        (t1, "envelope", sha256_hex(L1_V1)),
        (t2, "read", sha256_hex(L1_V2)),
        (t3, "read", sha256_hex(L1_V1)),
    ):
        rr = t.r_result
        assert rr is not None
        resolved = rr.resolved_source
        assert resolved is not None
        assert resolved.kind == kind
        assert resolved.root_byte_length == 32768
        assert resolved.root_digest == digest
        # The actual work-domain facts (no refusal at this scale):
        assert 0 < t.r_work_units < t.work_units <= t.bounds.max_total_work_units
        assert 0 < t.g_work_units < t.work_units
        assert t.stage_work_units <= 1_048_576
    # The ACTUAL recorded entry-source sizes (the root row plus
    # the current FILE entries; the READ-acquired root path also
    # retains its own FILE entry under the governing digest):
    assert t1.entry_source_bytes == 32768 + L1_FILE_BYTES
    assert t2.entry_source_bytes == 2 * 32768 + L1_FILE_BYTES
    assert t3.entry_source_bytes == 2 * 32768 + L1_FILE_BYTES
    # The retained originals / history: the root change and the
    # revert retain EVERY original root fact (nothing erased),
    # and the D history retains every genuine occurrence:
    facts = s_revert.root_facts
    assert len(facts) == 3
    assert sorted(f.provenance.kind for f in facts) == ["envelope", "read", "read"]
    assert {f.source_digest for f in facts if f.provenance.kind == "read"} == {
        sha256_hex(L1_V1),
        sha256_hex(L1_V2),
    }
    assert {"a", "x", "t", "root2", "root1b"} <= {o.call_id for o in s_revert.d_state.occurrences}
    # All three FILE dependencies are admitted current rows:
    for path in ("A.md", "X.md", "Target.md"):
        _path_key(t1, path)

    registry = _work_registry()
    work = registry.work
    assert work is not None
    owner = registry.acquire(ns)
    a1 = owner.admit(s_files, t1, ns, expected_revision=0)
    assert a1.outcome is RamStateOutcome.ADMITTED
    base_process = registry.process_owned_bytes
    okey = owner.namespace.lineage_key
    store_after_1 = owner.owned_bytes

    calls: list[int] = []
    seam = _lifecycle_seam(calls)

    adm_t1 = t1.admission
    assert adm_t1 is not None
    k1 = adm_t1.root_entry.content_key
    ka = _path_key(t1, "A.md")
    kt = _path_key(t1, "Target.md")
    assert len({k1, ka, kt}) == 3

    # The root, A.md and the UNRELATED eligible document (Target.md)
    # each earn their own single-flight attempt:
    r_root1 = await work.resolve(ns, k1, seam)
    assert r_root1.outcome is RamWorkOutcome.COMPLETED
    assert r_root1.invocations == 1 and len(calls) == 1
    p_root1 = r_root1.payload
    assert p_root1 is not None and p_root1.data == LIFECYCLE_PAYLOAD
    r_a1 = await work.resolve(ns, ka, seam)
    assert r_a1.outcome is RamWorkOutcome.COMPLETED and len(calls) == 2
    p_a1 = r_a1.payload
    assert p_a1 is not None
    r_t1 = await work.resolve(ns, kt, seam)
    assert r_t1.outcome is RamWorkOutcome.COMPLETED and len(calls) == 3
    p_t1 = r_t1.payload
    assert p_t1 is not None
    # The later same-key demand is a RAM-only hit:
    r_a1b = await work.resolve(ns, ka, seam)
    assert r_a1b.outcome is RamWorkOutcome.HIT
    assert r_a1b.invocations == 0 and len(calls) == 3
    assert r_a1b.payload is p_a1

    # The genuine v2 ROOT CHANGE: the root entry AND the FILE rows
    # are REKEYED under the new governing root digest (the accepted
    # 018-c canonical law; the original proofs are retained).
    a2 = owner.admit(s_root2, t2, ns, expected_revision=1)
    assert a2.outcome is RamStateOutcome.ADMITTED
    store_after_2 = owner.owned_bytes
    adm_t2 = t2.admission
    assert adm_t2 is not None
    k2 = adm_t2.root_entry.content_key
    assert k2 != k1
    ka2 = _path_key(t2, "A.md")
    assert ka2 != ka
    r_root2 = await work.resolve(ns, k2, seam)
    assert r_root2.outcome is RamWorkOutcome.COMPLETED
    assert r_root2.invocations == 1 and len(calls) == 4
    p_root2 = r_root2.payload
    assert p_root2 is not None and p_root2 is not p_root1
    # The rekeyed A.md is a NEW full key: its own attempt.
    r_ka2 = await work.resolve(ns, ka2, seam)
    assert r_ka2.outcome is RamWorkOutcome.COMPLETED
    assert r_ka2.invocations == 1 and len(calls) == 5
    p_ka2 = r_ka2.payload
    assert p_ka2 is not None
    # The WITHDRAWN old full keys are no longer current rows and
    # are refused with the fixed currentness fence (zero
    # invocation):
    assert owner.lookup(ka, ns).outcome is RamStateOutcome.NOT_FOUND
    r_stale_a = await work.resolve(ns, ka, seam)
    assert r_stale_a.outcome is RamWorkOutcome.REFUSED
    assert r_stale_a.limitation is RamWorkLimitation.KEY_NOT_CURRENT
    assert r_stale_a.http_status == 409
    assert r_stale_a.invocations == 0 and len(calls) == 5
    assert owner.lookup(k1, ns).outcome is RamStateOutcome.NOT_FOUND
    r_stale = await work.resolve(ns, k1, seam)
    assert r_stale.outcome is RamWorkOutcome.REFUSED
    assert r_stale.limitation is RamWorkLimitation.KEY_NOT_CURRENT
    assert r_stale.http_status == 409
    assert r_stale.invocations == 0 and len(calls) == 5

    # The deliberate OLD-BYTES revert: the ORIGINAL root key and
    # the ORIGINAL FILE keys are restored, and the retained
    # ORIGINAL payloads are reused WITHOUT new invocations.
    a3 = owner.admit(s_revert, t3, ns, expected_revision=2)
    assert a3.outcome is RamStateOutcome.ADMITTED
    store_after_3 = owner.owned_bytes
    adm_t3 = t3.admission
    assert adm_t3 is not None
    k3 = adm_t3.root_entry.content_key
    assert k3 == k1
    assert _path_key(t3, "A.md") == ka
    assert _path_key(t3, "Target.md") == kt
    r_root3 = await work.resolve(ns, k3, seam)
    assert r_root3.outcome is RamWorkOutcome.HIT
    assert r_root3.invocations == 0 and len(calls) == 5
    assert r_root3.payload is p_root1

    # Committed retention grows with every genuine transition; the
    # same atomic sum is what the session ceiling sees.
    assert 0 < store_after_1 < store_after_2 < store_after_3
    assert registry.process_owned_bytes > base_process
    assert a3.session_owned_bytes == owner.owned_bytes + work.session_bytes(okey)
    # Every existing hit stays usable after all transitions:
    assert owner.lookup(ka, ns).outcome is RamStateOutcome.FOUND
    assert owner.lookup(kt, ns).outcome is RamStateOutcome.FOUND
    r_a3 = await work.resolve(ns, ka, seam)
    assert r_a3.outcome is RamWorkOutcome.HIT and len(calls) == 5
    assert r_a3.payload is p_a1
    r_t3b = await work.resolve(ns, kt, seam)
    assert r_t3b.outcome is RamWorkOutcome.HIT and len(calls) == 5
    assert r_t3b.payload is p_t1

    # The composed async teardown releases store plus work:
    proc_before = registry.process_owned_bytes
    td = await work.teardown_owner(ns)
    assert td.outcome is RamWorkOutcome.TEARDOWN
    assert td.freed_bytes > 0
    assert td.freed_bytes == proc_before - registry.process_owned_bytes
    assert registry.get(ns) is None


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
async def test_l2_overlapping_ownership_work_currentness(
    mode: AdmissionMode, endpoint: str
) -> None:
    """L2: the overlapping [A,B] / [A,C] bundle ownership through
    the RAM work plane, both modes, both representative
    endpoints: A.md maps to BOTH overlapping bundle keys; the
    child-of-one A version withdraws the OLD overlapping keys
    (the work plane refuses them with the fixed currentness
    fence, the retained old payload is NOT re-served) while the
    lean isolated eligible segments earn their own attempts; the
    genuine both-lineage A version re-admits A.md under its OWN
    distinct singleton key with its own attempt."""
    seg_a, seg_b, seg_c = "A part one.\n", "B part.\n", "C part.\n"
    mkr = "OVLMARK"
    root_body = "Read `A.md`, `B.md` and `C.md` before changing code."
    ns, s0 = r_bootstrap(mode, f"ram019c-l2-{mode.value}-{endpoint}", root_body=root_body)
    cmd_ab = f"cat A.md && echo '{mkr}' && cat B.md"
    t1 = r_issue(s0, ns, "p1", endpoint, (CAUSAL_ROOT_FACT,), cmd_ab)
    assert t1.outcome is RootLineageOutcome.ACCEPTED, t1.diagnostics
    t2 = r_observe(
        t1.state, ns, (read_request(endpoint, "p1", seg_a + mkr + "\n" + seg_b, cmd_ab),)
    )
    assert t2.outcome is RootLineageOutcome.ACCEPTED, t2.diagnostics
    s1 = t2.state
    p1_occ = next(o for o in s1.d_state.occurrences if o.call_id == "p1")
    cmd_ac = f"cat A.md && echo '{mkr}' && cat C.md"
    t3 = r_issue(s1, ns, "p2", endpoint, (p1_occ.occurrence_id, CAUSAL_ROOT_FACT), cmd_ac)
    assert t3.outcome is RootLineageOutcome.ACCEPTED, t3.diagnostics
    t4 = r_observe(
        t3.state, ns, (read_request(endpoint, "p2", seg_a + mkr + "\n" + seg_c, cmd_ac),)
    )
    assert t4.outcome is RootLineageOutcome.ACCEPTED, t4.diagnostics
    s2 = t4.state
    p2_occ = next(o for o in s2.d_state.occurrences if o.call_id == "p2")
    r1 = derive_root_region_admission(s2, ns)
    assert r1.outcome is RootRegionAdmissionOutcome.READY, r1.diagnostics
    adm1 = r1.admission
    assert adm1 is not None
    rows1 = {row.path: row for row in adm1.path_associations if row.content_keys}
    a_keys1 = rows1["A.md"].content_keys
    assert len(a_keys1) == 2  # the overlap: BOTH bundle keys
    rk0 = adm1.root_entry.content_key

    registry = _work_registry()
    work = registry.work
    assert work is not None
    owner = registry.acquire(ns)
    a1 = owner.admit(s2, r1, ns, expected_revision=0)
    assert a1.outcome is RamStateOutcome.ADMITTED
    calls: list[int] = []
    seam = _lifecycle_seam(calls)
    r_rk = await work.resolve(ns, rk0, seam)
    assert r_rk.outcome is RamWorkOutcome.COMPLETED and len(calls) == 1
    ka1 = a_keys1[0]
    r_ka1 = await work.resolve(ns, ka1, seam)
    assert r_ka1.outcome is RamWorkOutcome.COMPLETED and len(calls) == 2

    # The child-of-one A version: the OLD overlapping keys are
    # withdrawn from EVERY row.
    t5 = r_issue(s2, ns, "a2", endpoint, (p1_occ.occurrence_id,), "cat A.md")
    assert t5.outcome is RootLineageOutcome.ACCEPTED, t5.diagnostics
    t6 = r_observe(
        t5.state, ns, (read_request(endpoint, "a2", frame("A part two.\n"), "cat A.md"),)
    )
    assert t6.outcome is RootLineageOutcome.ACCEPTED, t6.diagnostics
    s3 = t6.state
    r2 = derive_root_region_admission(s3, ns)
    assert r2.outcome is RootRegionAdmissionOutcome.READY, r2.diagnostics
    adm2 = r2.admission
    assert adm2 is not None
    all_keys2 = {k for row in adm2.path_associations for k in row.content_keys}
    for old in a_keys1:
        assert old not in all_keys2
    a2adm = owner.admit(s3, r2, ns, expected_revision=1)
    assert a2adm.outcome is RamStateOutcome.ADMITTED
    r_stale = await work.resolve(ns, ka1, seam)
    assert r_stale.outcome is RamWorkOutcome.REFUSED
    assert r_stale.limitation is RamWorkLimitation.KEY_NOT_CURRENT
    assert r_stale.invocations == 0 and len(calls) == 2
    if mode is AdmissionMode.LEAN:
        # The isolated eligible B.md segment earns its own attempt
        # (its width-1 key is NEW: the bundle key is withdrawn).
        kb2 = _path_key(r2, "B.md")
        assert kb2 not in a_keys1
        r_kb2 = await work.resolve(ns, kb2, seam)
        assert r_kb2.outcome is RamWorkOutcome.COMPLETED and len(calls) == 3
    else:
        # Greedy: the staled bundles withdraw entirely; the
        # unchanged root stays a retained hit.
        assert adm2.entries == ()
        r_rk2 = await work.resolve(ns, rk0, seam)
        assert r_rk2.outcome is RamWorkOutcome.HIT and len(calls) == 2

    # The genuine BOTH-lineage A version: A.md is CURRENT under
    # its OWN distinct singleton key with its own attempt.
    a2_occ = next(o for o in s3.d_state.occurrences if o.call_id == "a2")
    t7 = r_issue(
        s3,
        ns,
        "a3",
        endpoint,
        (p1_occ.occurrence_id, p2_occ.occurrence_id, a2_occ.occurrence_id),
        "cat A.md",
    )
    assert t7.outcome is RootLineageOutcome.ACCEPTED, t7.diagnostics
    t8 = r_observe(
        t7.state, ns, (read_request(endpoint, "a3", frame("A part three.\n"), "cat A.md"),)
    )
    assert t8.outcome is RootLineageOutcome.ACCEPTED, t8.diagnostics
    s4 = t8.state
    r3 = derive_root_region_admission(s4, ns)
    assert r3.outcome is RootRegionAdmissionOutcome.READY, r3.diagnostics
    adm3 = r3.admission
    assert adm3 is not None
    a_entry3 = [e for e in adm3.entries if e.key_record.member_occurrences == ("A.md",)]
    assert len(a_entry3) == 1 and a_entry3[0].width == 1
    ka3 = a_entry3[0].content_key
    for old in a_keys1:
        assert old != ka3
    assert adm3.root_entry.content_key == rk0
    a3adm = owner.admit(s4, r3, ns, expected_revision=2)
    assert a3adm.outcome is RamStateOutcome.ADMITTED
    r_ka3 = await work.resolve(ns, ka3, seam)
    # Lean: the B.md isolated-segment attempt above already ran
    # (three calls total before this one); greedy: two.
    expected_final = 4 if mode is AdmissionMode.LEAN else 3
    assert r_ka3.outcome is RamWorkOutcome.COMPLETED and len(calls) == expected_final
    r_stale2 = await work.resolve(ns, ka1, seam)
    assert r_stale2.outcome is RamWorkOutcome.REFUSED
    assert r_stale2.limitation is RamWorkLimitation.KEY_NOT_CURRENT
    assert len(calls) == expected_final


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
async def test_l3_opaque_bundle_ownership_work_lifecycle(
    mode: AdmissionMode, endpoint: str
) -> None:
    """L3: the BOUNDARYLESS (opaque) [A,B] bundle ownership
    through the RAM work plane, both modes, both representative
    endpoints: the opaque bundle is ONE work unit (the single-
    file keys do not exist; the bundle key is the only FILE
    key); the genuine standalone A.md observation conservatively
    WITHDRAWS the opaque bundle (the work plane refuses the
    withdrawn bundle key and does NOT re-serve the retained
    payload; A.md earns its OWN proven singleton attempt); the
    genuinely NEW complete [A,B] read re-admits the opaque
    bundle under its OWN unchanged canonical key with the
    retained ORIGINAL bundle payload reused WITHOUT a new
    invocation (the singleton key is withdrawn again)."""
    ns, s_bundle, s_singleton, s_bundle2 = _l3_states(
        mode, endpoint, f"ram019c-l3-{mode.value}-{endpoint}"
    )
    r1 = derive_root_region_admission(s_bundle, ns)
    assert r1.outcome is RootRegionAdmissionOutcome.READY, r1.diagnostics
    adm1 = r1.admission
    assert adm1 is not None
    # The opaque bundle: ONE entry, the BOUNDARYLESS ownership
    # group, NO proven per-member digest:
    assert len(adm1.entries) == 1
    bundle1 = adm1.entries[0]
    assert bundle1.key_record.member_occurrences == ("A.md", "B.md")
    assert bundle1.width == 2
    g1 = bundle1.key_record.ownership_groups[0]
    assert g1.boundary_class is BoundaryClass.BOUNDARYLESS
    assert g1.group_digest == bundle1.key_record.aggregate_source_digest
    assert bundle1.proof is not None
    assert bundle1.proof.segments[0].member_digest is None
    kb1 = bundle1.content_key
    rows1 = {row.path: row for row in adm1.path_associations if row.content_keys}
    assert rows1["A.md"].content_keys == (kb1,)
    assert rows1["B.md"].content_keys == (kb1,)
    rk0 = adm1.root_entry.content_key

    registry = _work_registry()
    work = registry.work
    assert work is not None
    owner = registry.acquire(ns)
    a1 = owner.admit(s_bundle, r1, ns, expected_revision=0)
    assert a1.outcome is RamStateOutcome.ADMITTED
    calls: list[int] = []
    seam = _lifecycle_seam(calls)
    r_rk = await work.resolve(ns, rk0, seam)
    assert r_rk.outcome is RamWorkOutcome.COMPLETED and len(calls) == 1
    # The opaque bundle is ONE single-flight work unit:
    r_kb1 = await work.resolve(ns, kb1, seam)
    assert r_kb1.outcome is RamWorkOutcome.COMPLETED and len(calls) == 2
    p_kb1 = r_kb1.payload
    assert p_kb1 is not None and p_kb1.data == LIFECYCLE_PAYLOAD
    r_kb1b = await work.resolve(ns, kb1, seam)
    assert r_kb1b.outcome is RamWorkOutcome.HIT
    assert r_kb1b.invocations == 0 and len(calls) == 2
    assert r_kb1b.payload is p_kb1

    # The genuine standalone A.md observation conservatively
    # WITHDRAWS the boundaryless bundle:
    r2 = derive_root_region_admission(s_singleton, ns)
    assert r2.outcome is RootRegionAdmissionOutcome.READY, r2.diagnostics
    adm2 = r2.admission
    assert adm2 is not None
    assert len(adm2.entries) == 1
    single2 = adm2.entries[0]
    assert single2.key_record.member_occurrences == ("A.md",)
    assert single2.width == 1
    assert single2.key_record.ownership_groups[0].boundary_class is BoundaryClass.PROVEN
    ka2 = single2.content_key
    assert ka2 != kb1
    all_keys2 = {k for row in adm2.path_associations for k in row.content_keys}
    assert kb1 not in all_keys2  # the opaque bundle key is withdrawn
    a2 = owner.admit(s_singleton, r2, ns, expected_revision=1)
    assert a2.outcome is RamStateOutcome.ADMITTED
    r_kb1_stale = await work.resolve(ns, kb1, seam)
    assert r_kb1_stale.outcome is RamWorkOutcome.REFUSED
    assert r_kb1_stale.limitation is RamWorkLimitation.KEY_NOT_CURRENT
    assert r_kb1_stale.invocations == 0 and len(calls) == 2
    # A.md earns its OWN proven singleton attempt:
    r_ka2 = await work.resolve(ns, ka2, seam)
    assert r_ka2.outcome is RamWorkOutcome.COMPLETED and len(calls) == 3

    # The genuinely NEW complete [A,B] read re-admits the opaque
    # bundle under its OWN unchanged canonical key (the NEW
    # original proof, not the retained old one):
    r3 = derive_root_region_admission(s_bundle2, ns)
    assert r3.outcome is RootRegionAdmissionOutcome.READY, r3.diagnostics
    adm3 = r3.admission
    assert adm3 is not None
    bundle3 = next(e for e in adm3.entries if e.key_record.member_occurrences == ("A.md", "B.md"))
    assert bundle3.content_key == kb1
    assert bundle3.key_record.ownership_groups[0].boundary_class is (BoundaryClass.BOUNDARYLESS)
    m1_occ = next(o for o in s_bundle.d_state.occurrences if o.call_id == "m1")
    m2_occ = next(o for o in s_bundle2.d_state.occurrences if o.call_id == "m2")
    # The FIRST compatible original proof is retained by identity
    # (the genuine same-content re-read is a retained witness,
    # never a proof replacement):
    assert bundle3.proof is not None
    assert bundle3.proof is m1_occ.proof
    assert {m1_occ.occurrence_id, m2_occ.occurrence_id} <= {
        w.occurrence_id for w in bundle3.witnesses
    }
    all_keys3 = {k for row in adm3.path_associations for k in row.content_keys}
    assert ka2 not in all_keys3  # the singleton key is withdrawn again
    a3 = owner.admit(s_bundle2, r3, ns, expected_revision=2)
    assert a3.outcome is RamStateOutcome.ADMITTED
    # The retained ORIGINAL bundle payload is reused WITHOUT a
    # new invocation:
    r_kb2 = await work.resolve(ns, kb1, seam)
    assert r_kb2.outcome is RamWorkOutcome.HIT
    assert r_kb2.invocations == 0 and len(calls) == 3
    assert r_kb2.payload is p_kb1
    r_ka2_stale = await work.resolve(ns, ka2, seam)
    assert r_ka2_stale.outcome is RamWorkOutcome.REFUSED
    assert r_ka2_stale.limitation is RamWorkLimitation.KEY_NOT_CURRENT
    assert len(calls) == 3


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
async def test_l4_adverse_currentness_quarantine_and_recovery(
    mode: AdmissionMode, endpoint: str
) -> None:
    """L4: the adverse-currentness RAM boundary, both modes,
    both representative endpoints: the current usable root (the
    proven v2 root region) is QUARANTINED by a genuinely
    trusted complete boundaryless root-bearing observation
    (unresolved maximal root uncertainty -> the ACTUAL
    non-READY T result commits as the bounded owner snapshot);
    the source-absent lookup/resolve CANNOT revive the old
    usable state (the retained payloads stay charged but are
    never re-served); an EXACT replay of the adverse
    observation cannot unblock; the genuinely proven supported
    recovery (a new proven root read descended from the
    unresolved branch, dominating it) restores usability under
    the existing causal law with the retained ORIGINAL payloads
    reused WITHOUT new invocations (the dominated adverse
    witness stays retained)."""
    ns, s1 = r_bootstrap(mode, f"ram019c-l4-{mode.value}-{endpoint}", root_body="Initial root.")
    t1 = derive_root_region_admission(s1, ns)
    assert t1.outcome is RootRegionAdmissionOutcome.READY, t1.diagnostics
    # The proven mixed-only v2 root region:
    i2 = r_issue(s1, ns, "v2", endpoint, (CAUSAL_ROOT_FACT,), MIX_CMD)
    assert i2.outcome is RootLineageOutcome.ACCEPTED, i2.diagnostics
    o2 = r_observe(
        i2.state,
        ns,
        (read_request(endpoint, "v2", mixed_body(L4_A, MARK, L4_V2_ROOT), MIX_CMD),),
    )
    assert o2.outcome is RootLineageOutcome.ACCEPTED, o2.diagnostics
    s2 = o2.state
    t2 = derive_root_region_admission(s2, ns)
    assert t2.outcome is RootRegionAdmissionOutcome.READY, t2.diagnostics
    rr2 = t2.r_result
    assert rr2 is not None
    src2 = rr2.resolved_source
    assert src2 is not None
    assert src2.kind == "read_region"
    assert src2.root_digest == sha256_hex(L4_V2_ROOT)
    adm2 = t2.admission
    assert adm2 is not None
    k2 = adm2.root_entry.content_key
    # A.md is off-graph here (declared by no root): the
    # accepted admission law admits no FILE row for it, so
    # the current rows are the root rows only.

    registry = _work_registry()
    work = registry.work
    assert work is not None
    owner = registry.acquire(ns)
    a1 = owner.admit(s1, t1, ns, expected_revision=0)
    assert a1.outcome is RamStateOutcome.ADMITTED
    okey = owner.namespace.lineage_key
    calls: list[int] = []
    seam = _lifecycle_seam(calls)
    adm_l4 = t1.admission
    assert adm_l4 is not None
    k1 = adm_l4.root_entry.content_key
    r_k1 = await work.resolve(ns, k1, seam)
    assert r_k1.outcome is RamWorkOutcome.COMPLETED and len(calls) == 1
    p_k1 = r_k1.payload
    assert p_k1 is not None
    a2 = owner.admit(s2, t2, ns, expected_revision=1)
    assert a2.outcome is RamStateOutcome.ADMITTED
    assert k2 != k1  # the v2 governing digest rekeys the root
    r_k2 = await work.resolve(ns, k2, seam)
    assert r_k2.outcome is RamWorkOutcome.COMPLETED and len(calls) == 2
    p_k2 = r_k2.payload
    assert p_k2 is not None

    # The ADVERSE evidence: a genuinely trusted complete
    # BOUNDARYLESS root-bearing observation (an unresolved
    # maximal root uncertainty under the actual Q law):
    v2_occ = next(o for o in s2.d_state.occurrences if o.call_id == "v2")
    i3 = r_issue(s2, ns, "v3", endpoint, (v2_occ.occurrence_id,), BOUNDARYLESS_CMD)
    assert i3.outcome is RootLineageOutcome.ACCEPTED, i3.diagnostics
    o3 = r_observe(i3.state, ns, (read_request(endpoint, "v3", OPAQUE_BODY, BOUNDARYLESS_CMD),))
    assert o3.outcome is RootLineageOutcome.ACCEPTED, o3.diagnostics
    s3 = o3.state
    t3 = derive_root_region_admission(s3, ns)
    assert t3.outcome is RootRegionAdmissionOutcome.ROOT_CURRENTNESS_UNPROVEN
    assert t3.diagnostics == ()
    assert t3.g_limitation is None
    rr3 = t3.r_result
    assert rr3 is not None
    assert rr3.outcome is RootRegionGraphOutcome.ROOT_CURRENTNESS_UNPROVEN
    assert rr3.resolved_source is None and rr3.f_result is None
    assert t3.admission is None
    assert t3.state is s3 and t3.ns is ns
    assert t3.g_work_units == 0
    # The ACTUAL non-READY result commits as the bounded
    # quarantine snapshot (the retained metadata charged before
    # retention):
    a3 = owner.admit(s3, t3, ns, expected_revision=2)
    assert a3.outcome is RamStateOutcome.ADMITTED
    own_after_3 = owner.owned_bytes
    # The committed candidate charge is published exactly
    # (the retained metadata is charged before retention; a
    # non-READY result may own fewer derived rows, so no
    # monotonicity is assumed here):
    assert own_after_3 == a3.charged_bytes and own_after_3 > 0
    assert a3.revision == 3
    # The source-absent lookup/resolve CANNOT revive the old
    # usable state (zero new invocations):
    for old in (k1, k2):
        assert owner.lookup(old, ns).outcome is RamStateOutcome.NOT_FOUND
    for old in (k1, k2):
        r_stale = await work.resolve(ns, old, seam)
        assert r_stale.outcome is RamWorkOutcome.REFUSED
        assert r_stale.limitation is RamWorkLimitation.KEY_NOT_CURRENT
        assert r_stale.http_status == 409
        assert r_stale.invocations == 0
    assert len(calls) == 2
    # The retained payloads stay charged (never evicted, never
    # re-served while quarantined):
    assert work.session_bytes(okey) > 0

    # An EXACT replay of the adverse observation cannot
    # unblock: the P-level replay is a true no-op (the SAME
    # original retained state); the owner-level re-admit
    # re-commits the record set, so the snapshot / revision
    # scalar re-derive and the retained charge is the ACTUAL
    # post-admission one (not a byte-constant):
    o3r = r_observe(s3, ns, (read_request(endpoint, "v3", OPAQUE_BODY, BOUNDARYLESS_CMD),))
    assert o3r.outcome is RootLineageOutcome.REPLAYED
    assert o3r.state is s3
    a3r = owner.admit(o3r.state, t3, ns, expected_revision=3)
    assert a3r.outcome is RamStateOutcome.ADMITTED
    assert owner.owned_bytes == a3r.charged_bytes
    assert owner.snapshot is a3r.snapshot
    assert owner.revision == a3r.revision
    assert owner.lookup(k2, ns).outcome is RamStateOutcome.NOT_FOUND
    r_stale2 = await work.resolve(ns, k2, seam)
    assert r_stale2.outcome is RamWorkOutcome.REFUSED
    assert r_stale2.limitation is RamWorkLimitation.KEY_NOT_CURRENT
    assert len(calls) == 2

    # The genuinely proven supported recovery: a new proven root
    # read descended from the unresolved branch, carrying the
    # v2 bytes (the dominated uncertainty is retained, never
    # erased):
    v3_occ = next(o for o in s3.d_state.occurrences if o.call_id == "v3")
    i4 = r_issue(s3, ns, "v4", endpoint, (v3_occ.occurrence_id,), MIX_CMD)
    assert i4.outcome is RootLineageOutcome.ACCEPTED, i4.diagnostics
    o4 = r_observe(
        i4.state,
        ns,
        (read_request(endpoint, "v4", mixed_body(L4_A, MARK, L4_V2_ROOT), MIX_CMD),),
    )
    assert o4.outcome is RootLineageOutcome.ACCEPTED, o4.diagnostics
    s4 = o4.state
    t4 = derive_root_region_admission(s4, ns)
    assert t4.outcome is RootRegionAdmissionOutcome.READY, t4.diagnostics
    rr4 = t4.r_result
    assert rr4 is not None
    src4 = rr4.resolved_source
    assert src4 is not None
    assert src4.kind == "read_region"
    assert src4.root_digest == sha256_hex(L4_V2_ROOT)
    adm4 = t4.admission
    assert adm4 is not None
    assert adm4.root_entry.content_key == k2  # the original key restored
    q4 = rr4.q_result
    assert q4 is not None
    assert len(q4.uncertainty_witnesses) == 1
    assert q4.uncertainty_witnesses[0].occurrence is v3_occ
    a4 = owner.admit(s4, t4, ns, expected_revision=4)
    assert a4.outcome is RamStateOutcome.ADMITTED
    # Usability restored: the retained ORIGINAL payloads are
    # reused WITHOUT new invocations:
    r_k2b = await work.resolve(ns, k2, seam)
    assert r_k2b.outcome is RamWorkOutcome.HIT
    assert r_k2b.invocations == 0 and len(calls) == 2
    assert r_k2b.payload is p_k2
    # The superseded envelope root never becomes current again:
    assert owner.lookup(k1, ns).outcome is RamStateOutcome.NOT_FOUND


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
async def test_l4b_capacity_refusal_preserves_usable_state(
    mode: AdmissionMode, endpoint: str
) -> None:
    """L4b: the ACTUAL capacity-refusal path preserves the old
    usable snapshot exactly, both modes, both representative
    endpoints: the session ceiling is set (from a probe-registry
    MEASUREMENT) one byte below the genuine next transition's
    charge; the second admission is refused with the fixed typed
    503 carrying the honest ACTUAL full candidate charge,
    commits nothing
    (atomic), and the existing lookup / payload HIT stay exactly
    usable."""
    ns, s1 = r_bootstrap(
        mode,
        f"ram019c-l4b-{mode.value}-{endpoint}",
        root_body="Read `A.md` before changing code.",
    )
    i1 = r_issue(s1, ns, "a1", endpoint, (CAUSAL_ROOT_FACT,), "cat A.md")
    assert i1.outcome is RootLineageOutcome.ACCEPTED, i1.diagnostics
    o1 = r_observe(i1.state, ns, (read_request(endpoint, "a1", L4_A, "cat A.md"),))
    assert o1.outcome is RootLineageOutcome.ACCEPTED, o1.diagnostics
    s2 = o1.state
    t1 = derive_root_region_admission(s1, ns)
    assert t1.outcome is RootRegionAdmissionOutcome.READY, t1.diagnostics
    t2 = derive_root_region_admission(s2, ns)
    assert t2.outcome is RootRegionAdmissionOutcome.READY, t2.diagnostics
    adm_l4b = t1.admission
    assert adm_l4b is not None
    k1 = adm_l4b.root_entry.content_key
    # Measure the ACTUAL charges on a probe registry (the same
    # namespace and the same operations):
    p_reg = _work_registry()
    p_work = p_reg.work
    assert p_work is not None
    p_owner = p_reg.acquire(ns)
    p_a1 = p_owner.admit(s1, t1, ns, expected_revision=0)
    assert p_a1.outcome is RamStateOutcome.ADMITTED
    charge1 = p_owner.owned_bytes
    pkey = p_owner.namespace.lineage_key
    pcalls: list[int] = []
    p_seam = _lifecycle_seam(pcalls)
    p_r = await p_work.resolve(ns, k1, p_seam)
    assert p_r.outcome is RamWorkOutcome.COMPLETED and len(pcalls) == 1
    w = p_work.session_bytes(pkey)
    assert w > 0
    p_a2 = p_owner.admit(s2, t2, ns, expected_revision=1)
    assert p_a2.outcome is RamStateOutcome.ADMITTED
    delta2 = p_owner.owned_bytes - charge1
    assert delta2 > 0
    # The real registry: the session ceiling sits one byte
    # BELOW the genuine next transition's charge:
    session_max = charge1 + w + delta2 - 1
    assert charge1 + w <= session_max
    r_reg = _work_registry()
    r_work = r_reg.work
    assert r_work is not None
    r_owner = r_reg.new_owner(ns, session_max_owned_bytes=session_max)
    r_a1 = r_owner.admit(s1, t1, ns, expected_revision=0)
    assert r_a1.outcome is RamStateOutcome.ADMITTED
    assert r_owner.owned_bytes == charge1  # the measurement aligns
    rcalls: list[int] = []
    r_seam = _lifecycle_seam(rcalls)
    r_r1 = await r_work.resolve(ns, k1, r_seam)
    assert r_r1.outcome is RamWorkOutcome.COMPLETED and len(rcalls) == 1
    p_r1 = r_r1.payload
    assert p_r1 is not None
    proc_before = r_reg.process_owned_bytes
    # The second admission crosses the measured session ceiling:
    r_a2 = r_owner.admit(s2, t2, ns, expected_revision=1)
    assert r_a2.outcome is RamStateOutcome.REFUSED
    assert r_a2.limitation is RamStateLimitation.SESSION_OWNED_BYTES_OVER_BOUND
    assert r_a2.http_status == 503
    assert (
        r_a2.charged_bytes == r_owner.owned_bytes + delta2
    )  # the honest ACTUAL full candidate charge
    # The refusal is atomic: the old usable snapshot is exactly
    # preserved and the existing HIT stays usable:
    assert r_owner.owned_bytes == charge1
    assert r_reg.process_owned_bytes == proc_before
    assert r_owner.lookup(k1, ns).outcome is RamStateOutcome.FOUND
    r_hit = await r_work.resolve(ns, k1, r_seam)
    assert r_hit.outcome is RamWorkOutcome.HIT
    assert r_hit.invocations == 0 and len(rcalls) == 1
    assert r_hit.payload is p_r1
    assert r_a2.session_owned_bytes == charge1 + w


L4C2_ROOT = "Second root. Read `A.md`."
L4C_OPAQUE = "Unknown root constituent.\n" + "x" * 32750


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
async def test_l4c_adverse_capacity_nonready_quarantines(
    mode: AdmissionMode, endpoint: str
) -> None:
    """L4c (adverse, non-READY path): the ACTUAL adverse
    s3/t3 of L4 (the trusted complete boundaryless
    root-bearing observation -> the ACTUAL non-READY T
    result) is capacity-refused on a MEASURED too-tight
    ceiling: the bounded owner quarantine is set (the
    pre-accounted flag only; the refused result is NOT
    retained) and the old usable state CANNOT be revived --
    every source-absent lookup / resolve refuses with the
    fixed typed currentness refusal, an EXACT replay of the
    adverse observation and a re-admit of the same result
    cannot unblock, the retained originals / payloads stay
    charged, the UNRELATED owner of the SAME registry is
    untouched, and the explicit teardown is the only exit
    (no epoch reset, no retry).  The admitted-adverse
    positive is L4; the non-adverse additive READY control
    is L4b."""
    # The genuine L4 lineage up to the adverse evidence:
    ns, s1 = r_bootstrap(mode, f"ram019c-l4c1-{mode.value}-{endpoint}", root_body="Initial root.")
    t1 = derive_root_region_admission(s1, ns)
    assert t1.outcome is RootRegionAdmissionOutcome.READY, t1.diagnostics
    i2 = r_issue(s1, ns, "v2", endpoint, (CAUSAL_ROOT_FACT,), MIX_CMD)
    assert i2.outcome is RootLineageOutcome.ACCEPTED, i2.diagnostics
    o2 = r_observe(
        i2.state,
        ns,
        (read_request(endpoint, "v2", mixed_body(L4_A, MARK, L4_V2_ROOT), MIX_CMD),),
    )
    assert o2.outcome is RootLineageOutcome.ACCEPTED, o2.diagnostics
    s2 = o2.state
    t2 = derive_root_region_admission(s2, ns)
    assert t2.outcome is RootRegionAdmissionOutcome.READY, t2.diagnostics
    adm2 = t2.admission
    assert adm2 is not None
    k2 = adm2.root_entry.content_key
    # The ADVERSE evidence: a genuinely trusted complete
    # BOUNDARYLESS root-bearing read of a GENUINE 32768-byte
    # opaque source (the accepted 018-q adverse shape at
    # substantial scale; the unknown root member hash stays
    # unknown):
    v2_occ = next(o for o in s2.d_state.occurrences if o.call_id == "v2")
    i3 = r_issue(s2, ns, "v3", endpoint, (v2_occ.occurrence_id,), BOUNDARYLESS_CMD)
    assert i3.outcome is RootLineageOutcome.ACCEPTED, i3.diagnostics
    o3 = r_observe(i3.state, ns, (read_request(endpoint, "v3", L4C_OPAQUE, BOUNDARYLESS_CMD),))
    assert o3.outcome is RootLineageOutcome.ACCEPTED, o3.diagnostics
    s3 = o3.state
    t3 = derive_root_region_admission(s3, ns)
    assert t3.outcome is RootRegionAdmissionOutcome.ROOT_CURRENTNESS_UNPROVEN
    assert t3.admission is None
    # Measure the ACTUAL charges on a probe registry (the
    # same namespace and the same operations):
    p_reg = _work_registry()
    p_work = p_reg.work
    assert p_work is not None
    p_owner = p_reg.acquire(ns)
    assert p_owner.admit(s1, t1, ns, expected_revision=0).outcome is RamStateOutcome.ADMITTED
    pcalls: list[int] = []
    p_seam = _lifecycle_seam(pcalls)
    adm_l4c1 = t1.admission
    assert adm_l4c1 is not None
    k1 = adm_l4c1.root_entry.content_key
    assert (await p_work.resolve(ns, k1, p_seam)).outcome is RamWorkOutcome.COMPLETED
    assert p_owner.admit(s2, t2, ns, expected_revision=1).outcome is RamStateOutcome.ADMITTED
    charge2 = p_owner.owned_bytes
    assert (await p_work.resolve(ns, k2, p_seam)).outcome is RamWorkOutcome.COMPLETED
    w2 = p_work.session_bytes(p_owner.namespace.lineage_key)
    assert w2 > 0
    # The probe retains the adverse state (sufficient
    # capacity): the same operations are NOT adverse there.
    assert p_owner.admit(s3, t3, ns, expected_revision=2).outcome is RamStateOutcome.ADMITTED
    delta3 = p_owner.owned_bytes - charge2
    assert delta3 > 0
    assert p_owner.quarantined is False
    # The real registry: the session ceiling sits one byte
    # BELOW the genuine adverse transition's charge:
    session_max = charge2 + w2 + delta3 - 1
    r_reg = _work_registry()
    r_work = r_reg.work
    assert r_work is not None
    r_owner = r_reg.new_owner(ns, session_max_owned_bytes=session_max)
    assert r_owner.admit(s1, t1, ns, expected_revision=0).outcome is RamStateOutcome.ADMITTED
    rcalls: list[int] = []
    r_seam = _lifecycle_seam(rcalls)
    assert (await r_work.resolve(ns, k1, r_seam)).outcome is RamWorkOutcome.COMPLETED
    assert r_owner.admit(s2, t2, ns, expected_revision=1).outcome is RamStateOutcome.ADMITTED
    assert r_owner.owned_bytes == charge2  # the measurement aligns
    r_k2 = await r_work.resolve(ns, k2, r_seam)
    assert r_k2.outcome is RamWorkOutcome.COMPLETED and len(rcalls) == 2
    proc_before = r_reg.process_owned_bytes
    # The adverse admission is capacity-refused and quarantines:
    r_a3 = r_owner.admit(s3, t3, ns, expected_revision=2)
    assert r_a3.outcome is RamStateOutcome.REFUSED
    assert r_a3.limitation is RamStateLimitation.SESSION_OWNED_BYTES_OVER_BOUND
    assert r_a3.http_status == 503
    assert r_a3.charged_bytes == r_owner.owned_bytes + delta3  # full candidate charge
    assert r_owner.quarantined is True
    # Atomic: nothing committed, nothing released:
    assert r_owner.owned_bytes == charge2
    assert r_reg.process_owned_bytes == proc_before
    # The old usable state CANNOT be revived (source-absent
    # lookup / resolve, zero new invocations):
    for old in (k1, k2):
        lk = r_owner.lookup(old, ns)
        assert lk.outcome is RamStateOutcome.NOT_FOUND
        assert lk.limitation is RamStateLimitation.OWNER_QUARANTINED
    r_stale = await r_work.resolve(ns, k2, r_seam)
    assert r_stale.outcome is RamWorkOutcome.REFUSED
    assert r_stale.limitation is RamStateLimitation.OWNER_QUARANTINED
    assert r_stale.http_status == 409
    assert r_stale.invocations == 0 and len(rcalls) == 2
    # The retained payloads stay charged (never evicted,
    # never re-served while quarantined):
    assert r_work.session_bytes(r_owner.namespace.lineage_key) > 0
    # An EXACT replay of the adverse observation cannot
    # unblock:
    o3r = r_observe(s3, ns, (read_request(endpoint, "v3", L4C_OPAQUE, BOUNDARYLESS_CMD),))
    assert o3r.outcome is RootLineageOutcome.REPLAYED
    assert o3r.state is s3
    r_a3r = r_owner.admit(o3r.state, t3, ns, expected_revision=2)
    assert r_a3r.outcome is RamStateOutcome.REFUSED
    assert r_a3r.limitation is RamStateLimitation.OWNER_QUARANTINED
    assert r_a3r.http_status is None
    assert r_owner.quarantined is True
    r_stale2 = await r_work.resolve(ns, k2, r_seam)
    assert r_stale2.outcome is RamWorkOutcome.REFUSED
    assert r_stale2.limitation is RamStateLimitation.OWNER_QUARANTINED
    assert len(rcalls) == 2
    # An UNRELATED owner of the SAME registry is untouched:
    ns_b, s1b = r_bootstrap(mode, f"ram019c-l4c1b-{mode.value}-{endpoint}", root_body="Other root.")
    t1b = derive_root_region_admission(s1b, ns_b)
    assert t1b.outcome is RootRegionAdmissionOutcome.READY, t1b.diagnostics
    r_owner_b = r_reg.acquire(ns_b)
    assert r_owner_b.admit(s1b, t1b, ns_b, expected_revision=0).outcome is RamStateOutcome.ADMITTED
    adm_b = t1b.admission
    assert adm_b is not None
    assert r_owner_b.lookup(adm_b.root_entry.content_key, ns_b).outcome is RamStateOutcome.FOUND
    # The explicit teardown is the only exit:
    proc_before_td = r_reg.process_owned_bytes
    td = await r_work.teardown_owner(ns)
    assert td.outcome is RamWorkOutcome.TEARDOWN
    assert 0 < td.freed_bytes <= proc_before_td
    assert r_reg.get(ns) is None
    # The unrelated owner survives the teardown untouched:
    assert r_owner_b.lookup(adm_b.root_entry.content_key, ns_b).outcome is RamStateOutcome.FOUND


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
async def test_l4c2_adverse_capacity_changed_root_quarantines(
    mode: AdmissionMode, endpoint: str
) -> None:
    """L4c2 (adverse, READY changed-root path): a genuinely
    NEW v2 WHOLE root read is READY yet REKEYS the retained
    root and FILE rows; when retaining THAT candidate is
    capacity-refused on a MEASURED too-tight ceiling, serving
    the old rekeyed-out keys would still serve stale
    governance: the owner quarantines and the source-absent
    lookup / resolve of the old keys refuses with the fixed
    typed currentness refusal (the old bytes stay retained
    and charged; the unrelated owner is untouched; teardown
    is the only exit).  The non-adverse additive READY
    control is L4b (every old current key preserved)."""
    ns, s0 = r_bootstrap(
        mode,
        f"ram019c-l4c2-{mode.value}-{endpoint}",
        root_body="Read `A.md` before changing code.",
    )
    s_files = _l1_dep_read(s0, ns, "a1", endpoint, "A.md", L4_A)
    s_root2 = _l1_dep_read(s_files, ns, "root2", endpoint, ROOT_FILENAME, L4C2_ROOT)
    t1 = derive_root_region_admission(s_files, ns)
    assert t1.outcome is RootRegionAdmissionOutcome.READY, t1.diagnostics
    t2c = derive_root_region_admission(s_root2, ns)
    assert t2c.outcome is RootRegionAdmissionOutcome.READY, t2c.diagnostics
    adm1 = t1.admission
    assert adm1 is not None
    adm2c = t2c.admission
    assert adm2c is not None
    k1 = adm1.root_entry.content_key
    k1a = _path_key(t1, "A.md")
    k2 = adm2c.root_entry.content_key
    k2a = _path_key(t2c, "A.md")
    assert k2 != k1  # the changed governing digest rekeys the root
    assert k2a != k1a  # ... and the FILE row under it
    # Measure the ACTUAL charges on a probe registry (the
    # same namespace and the same operations):
    p_reg = _work_registry()
    p_work = p_reg.work
    assert p_work is not None
    p_owner = p_reg.acquire(ns)
    assert p_owner.admit(s_files, t1, ns, expected_revision=0).outcome is RamStateOutcome.ADMITTED
    charge1 = p_owner.owned_bytes
    pcalls: list[int] = []
    p_seam = _lifecycle_seam(pcalls)
    assert (await p_work.resolve(ns, k1, p_seam)).outcome is RamWorkOutcome.COMPLETED
    w = p_work.session_bytes(p_owner.namespace.lineage_key)
    assert w > 0
    assert p_owner.admit(s_root2, t2c, ns, expected_revision=1).outcome is RamStateOutcome.ADMITTED
    delta2 = p_owner.owned_bytes - charge1
    assert delta2 > 0
    # The real registry: the session ceiling sits one byte
    # BELOW the genuine changed-root transition's charge:
    session_max = charge1 + w + delta2 - 1
    r_reg = _work_registry()
    r_work = r_reg.work
    assert r_work is not None
    r_owner = r_reg.new_owner(ns, session_max_owned_bytes=session_max)
    assert r_owner.admit(s_files, t1, ns, expected_revision=0).outcome is RamStateOutcome.ADMITTED
    assert r_owner.owned_bytes == charge1  # the measurement aligns
    rcalls: list[int] = []
    r_seam = _lifecycle_seam(rcalls)
    r_r1 = await r_work.resolve(ns, k1, r_seam)
    assert r_r1.outcome is RamWorkOutcome.COMPLETED and len(rcalls) == 1
    p_r1 = r_r1.payload
    assert p_r1 is not None
    proc_before = r_reg.process_owned_bytes
    # The changed-root admission is capacity-refused and
    # quarantines (a READY candidate that rekeys the
    # retained current keys is adverse):
    r_a2 = r_owner.admit(s_root2, t2c, ns, expected_revision=1)
    assert r_a2.outcome is RamStateOutcome.REFUSED
    assert r_a2.limitation is RamStateLimitation.SESSION_OWNED_BYTES_OVER_BOUND
    assert r_a2.http_status == 503
    assert r_a2.charged_bytes == r_owner.owned_bytes + delta2  # full candidate charge
    assert r_owner.quarantined is True
    # Atomic: nothing committed, nothing released:
    assert r_owner.owned_bytes == charge1
    assert r_reg.process_owned_bytes == proc_before
    # The old rekeyed-out keys CANNOT be revived
    # (source-absent lookup / resolve, zero new invocations):
    for old in (k1, k1a):
        lk = r_owner.lookup(old, ns)
        assert lk.outcome is RamStateOutcome.NOT_FOUND
        assert lk.limitation is RamStateLimitation.OWNER_QUARANTINED
    r_stale = await r_work.resolve(ns, k1, r_seam)
    assert r_stale.outcome is RamWorkOutcome.REFUSED
    assert r_stale.limitation is RamStateLimitation.OWNER_QUARANTINED
    assert r_stale.http_status == 409
    assert r_stale.invocations == 0 and len(rcalls) == 1
    # The retained payload stays charged (never re-served):
    assert r_work.session_bytes(r_owner.namespace.lineage_key) > 0
    # An UNRELATED owner of the SAME registry is untouched:
    ns_b, s1b = r_bootstrap(mode, f"ram019c-l4c2b-{mode.value}-{endpoint}", root_body="Other root.")
    t1b = derive_root_region_admission(s1b, ns_b)
    assert t1b.outcome is RootRegionAdmissionOutcome.READY, t1b.diagnostics
    r_owner_b = r_reg.acquire(ns_b)
    assert r_owner_b.admit(s1b, t1b, ns_b, expected_revision=0).outcome is RamStateOutcome.ADMITTED
    adm_b = t1b.admission
    assert adm_b is not None
    assert r_owner_b.lookup(adm_b.root_entry.content_key, ns_b).outcome is RamStateOutcome.FOUND
    # The explicit teardown is the only exit:
    proc_before_td = r_reg.process_owned_bytes
    td = await r_work.teardown_owner(ns)
    assert td.outcome is RamWorkOutcome.TEARDOWN
    assert 0 < td.freed_bytes <= proc_before_td
    assert r_reg.get(ns) is None
    assert r_owner_b.lookup(adm_b.root_entry.content_key, ns_b).outcome is RamStateOutcome.FOUND


L4C3_A2 = "Revised A body.\n" + "y" * 4080


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
async def test_l4c3_adverse_capacity_changed_file_quarantines(
    mode: AdmissionMode, endpoint: str
) -> None:
    """L4c3 (adverse, READY changed-FILE path): a genuinely NEW
    v2 A.md read (a true descendant of the v1 read, distinct
    bytes) is READY yet REKEYS ONLY the FILE row -- the
    unchanged governing root PRESERVES the root key; when
    retaining THAT candidate is capacity-refused on a MEASURED
    too-tight ceiling, serving the old rekeyed-out FILE key
    would still serve stale governance: the owner quarantines
    and EVERY source-absent lookup / resolve -- including the
    PRESERVED root key -- refuses with the fixed typed
    currentness refusal.  The old bytes stay retained and
    charged; the unrelated owner is untouched; the explicit
    teardown is the only exit.  The non-adverse additive READY
    control is L4b; the changed-root analogue is L4c2."""
    ns, s0 = r_bootstrap(
        mode,
        f"ram019c-l4c3-{mode.value}-{endpoint}",
        root_body="Read `A.md` before changing code.",
    )
    s_files = _l1_dep_read(s0, ns, "a1", endpoint, "A.md", L4_A)
    a1_occ = next(o for o in s_files.d_state.occurrences if o.call_id == "a1")
    i2 = r_issue(s_files, ns, "a2", endpoint, (a1_occ.occurrence_id,), "cat A.md")
    assert i2.outcome is RootLineageOutcome.ACCEPTED, i2.diagnostics
    o2 = r_observe(i2.state, ns, (read_request(endpoint, "a2", L4C3_A2, "cat A.md"),))
    assert o2.outcome is RootLineageOutcome.ACCEPTED, o2.diagnostics
    s_files2 = o2.state
    t1 = derive_root_region_admission(s_files, ns)
    assert t1.outcome is RootRegionAdmissionOutcome.READY, t1.diagnostics
    t2 = derive_root_region_admission(s_files2, ns)
    assert t2.outcome is RootRegionAdmissionOutcome.READY, t2.diagnostics
    adm1 = t1.admission
    assert adm1 is not None
    adm2 = t2.admission
    assert adm2 is not None
    k1 = adm1.root_entry.content_key
    k1a = _path_key(t1, "A.md")
    k2 = adm2.root_entry.content_key
    k2a = _path_key(t2, "A.md")
    assert k2 == k1  # the unchanged governing root PRESERVES the root key
    assert k2a != k1a  # ... the changed FILE row rekeys
    # Measure the ACTUAL charges on a probe registry (the
    # same namespace and the same operations):
    p_reg = _work_registry()
    p_work = p_reg.work
    assert p_work is not None
    p_owner = p_reg.acquire(ns)
    assert p_owner.admit(s_files, t1, ns, expected_revision=0).outcome is RamStateOutcome.ADMITTED
    charge1 = p_owner.owned_bytes
    pcalls: list[int] = []
    p_seam = _lifecycle_seam(pcalls)
    assert (await p_work.resolve(ns, k1a, p_seam)).outcome is RamWorkOutcome.COMPLETED
    w = p_work.session_bytes(p_owner.namespace.lineage_key)
    assert w > 0
    assert p_owner.admit(s_files2, t2, ns, expected_revision=1).outcome is RamStateOutcome.ADMITTED
    delta2 = p_owner.owned_bytes - charge1
    assert delta2 > 0
    # The SAME operations under sufficient capacity do NOT
    # quarantine: the current rows are simply rekeyed (the old
    # FILE row is no longer current; the new one is):
    assert p_owner.quarantined is False
    assert p_owner.lookup(k1a, ns).outcome is RamStateOutcome.NOT_FOUND
    assert p_owner.lookup(k2a, ns).outcome is RamStateOutcome.FOUND
    # The real registry: the session ceiling sits one byte
    # BELOW the genuine changed-FILE transition's charge:
    session_max = charge1 + w + delta2 - 1
    r_reg = _work_registry()
    r_work = r_reg.work
    assert r_work is not None
    r_owner = r_reg.new_owner(ns, session_max_owned_bytes=session_max)
    assert r_owner.admit(s_files, t1, ns, expected_revision=0).outcome is RamStateOutcome.ADMITTED
    assert r_owner.owned_bytes == charge1  # the measurement aligns
    rcalls: list[int] = []
    r_seam = _lifecycle_seam(rcalls)
    assert (await r_work.resolve(ns, k1a, r_seam)).outcome is RamWorkOutcome.COMPLETED
    assert len(rcalls) == 1
    proc_before = r_reg.process_owned_bytes
    # The changed-FILE admission is capacity-refused and
    # quarantines (a READY candidate rekeying a retained
    # current key is adverse, even when the root key is
    # preserved):
    r_a2 = r_owner.admit(s_files2, t2, ns, expected_revision=1)
    assert r_a2.outcome is RamStateOutcome.REFUSED
    assert r_a2.limitation is RamStateLimitation.SESSION_OWNED_BYTES_OVER_BOUND
    assert r_a2.http_status == 503
    assert r_a2.charged_bytes == r_owner.owned_bytes + delta2  # full candidate charge
    assert r_owner.quarantined is True
    # Atomic: nothing committed, nothing released:
    assert r_owner.owned_bytes == charge1
    assert r_reg.process_owned_bytes == proc_before
    # EVERY old key is unusable (the quarantine is
    # owner-level; the preserved root key is fenced too):
    for old in (k1, k1a):
        lk = r_owner.lookup(old, ns)
        assert lk.outcome is RamStateOutcome.NOT_FOUND
        assert lk.limitation is RamStateLimitation.OWNER_QUARANTINED
    r_stale = await r_work.resolve(ns, k1a, r_seam)
    assert r_stale.outcome is RamWorkOutcome.REFUSED
    assert r_stale.limitation is RamStateLimitation.OWNER_QUARANTINED
    assert r_stale.http_status == 409
    assert r_stale.invocations == 0 and len(rcalls) == 1
    # The retained payload stays charged (never evicted,
    # never re-served while quarantined):
    assert r_work.session_bytes(r_owner.namespace.lineage_key) > 0
    # An EXACT replay of the changed-FILE observation cannot
    # unblock:
    o2r = r_observe(s_files2, ns, (read_request(endpoint, "a2", L4C3_A2, "cat A.md"),))
    assert o2r.outcome is RootLineageOutcome.REPLAYED
    assert o2r.state is s_files2
    r_a2r = r_owner.admit(o2r.state, t2, ns, expected_revision=1)
    assert r_a2r.outcome is RamStateOutcome.REFUSED
    assert r_a2r.limitation is RamStateLimitation.OWNER_QUARANTINED
    assert r_a2r.http_status is None
    assert r_owner.quarantined is True
    # An UNRELATED owner of the SAME registry is untouched:
    ns_b, s1b = r_bootstrap(mode, f"ram019c-l4c3b-{mode.value}-{endpoint}", root_body="Other root.")
    t1b = derive_root_region_admission(s1b, ns_b)
    assert t1b.outcome is RootRegionAdmissionOutcome.READY, t1b.diagnostics
    r_owner_b = r_reg.acquire(ns_b)
    assert r_owner_b.admit(s1b, t1b, ns_b, expected_revision=0).outcome is RamStateOutcome.ADMITTED
    adm_b = t1b.admission
    assert adm_b is not None
    assert r_owner_b.lookup(adm_b.root_entry.content_key, ns_b).outcome is RamStateOutcome.FOUND
    # The explicit teardown is the only exit:
    proc_before_td = r_reg.process_owned_bytes
    td = await r_work.teardown_owner(ns)
    assert td.outcome is RamWorkOutcome.TEARDOWN
    assert 0 < td.freed_bytes <= proc_before_td
    assert r_reg.get(ns) is None
    # The unrelated owner survives the teardown untouched:
    assert r_owner_b.lookup(adm_b.root_entry.content_key, ns_b).outcome is RamStateOutcome.FOUND


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
async def test_l4c4_admitted_changed_file_failure_lifecycle(
    mode: AdmissionMode, endpoint: str
) -> None:
    """L4c4 (admitted adverse changed-FILE positive + work
    failure / source-absent composition): with sufficient
    capacity the SAME genuinely changed A.md transition
    COMMITS: the old rekeyed-out FILE key is no longer
    current (the source-absent lookup / resolve cannot
    revive it -- supersession, not quarantine), the
    PRESERVED root key stays CURRENT and its retained
    payload is re-served as a RAM-only HIT (zero new
    invocations), and a REQUIRED WORK FAILURE on the new
    FILE key is terminal for that key ALONE (fixed 503, the
    original failed attempt still applies, no retry) without
    poisoning the preserved root key or the admitted current
    rows.  The capacity-refusal quarantine analogue is
    L4c3."""
    ns, s0 = r_bootstrap(
        mode,
        f"ram019c-l4c4-{mode.value}-{endpoint}",
        root_body="Read `A.md` before changing code.",
    )
    s_files = _l1_dep_read(s0, ns, "a1", endpoint, "A.md", L4_A)
    a1_occ = next(o for o in s_files.d_state.occurrences if o.call_id == "a1")
    i2 = r_issue(s_files, ns, "a2", endpoint, (a1_occ.occurrence_id,), "cat A.md")
    assert i2.outcome is RootLineageOutcome.ACCEPTED, i2.diagnostics
    o2 = r_observe(i2.state, ns, (read_request(endpoint, "a2", L4C3_A2, "cat A.md"),))
    assert o2.outcome is RootLineageOutcome.ACCEPTED, o2.diagnostics
    s_files2 = o2.state
    t1 = derive_root_region_admission(s_files, ns)
    assert t1.outcome is RootRegionAdmissionOutcome.READY, t1.diagnostics
    t2 = derive_root_region_admission(s_files2, ns)
    assert t2.outcome is RootRegionAdmissionOutcome.READY, t2.diagnostics
    adm1 = t1.admission
    assert adm1 is not None
    adm2 = t2.admission
    assert adm2 is not None
    k1 = adm1.root_entry.content_key
    k1a = _path_key(t1, "A.md")
    k2 = adm2.root_entry.content_key
    k2a = _path_key(t2, "A.md")
    assert k2 == k1
    assert k2a != k1a
    reg = _work_registry()
    work = reg.work
    assert work is not None
    owner = reg.acquire(ns)
    assert owner.admit(s_files, t1, ns, expected_revision=0).outcome is RamStateOutcome.ADMITTED
    calls: list[int] = []
    seam = _lifecycle_seam(calls)
    r1 = await work.resolve(ns, k1, seam)
    assert r1.outcome is RamWorkOutcome.COMPLETED and len(calls) == 1
    p_r1 = r1.payload
    assert p_r1 is not None
    # The genuinely changed FILE transition COMMITS:
    assert owner.admit(s_files2, t2, ns, expected_revision=1).outcome is RamStateOutcome.ADMITTED
    assert owner.quarantined is False
    # The old rekeyed-out FILE key cannot be revived
    # (source-absent lookup / resolve; supersession, not
    # quarantine):
    lk = owner.lookup(k1a, ns)
    assert lk.outcome is RamStateOutcome.NOT_FOUND
    stale = await work.resolve(ns, k1a, seam)
    assert stale.outcome is RamWorkOutcome.REFUSED
    assert stale.limitation is RamWorkLimitation.KEY_NOT_CURRENT
    assert stale.http_status == 409
    assert stale.invocations == 0 and len(calls) == 1
    # The PRESERVED root key stays current; its retained
    # payload is a RAM-only HIT:
    assert owner.lookup(k1, ns).outcome is RamStateOutcome.FOUND
    hit = await work.resolve(ns, k1, seam)
    assert hit.outcome is RamWorkOutcome.HIT
    assert hit.invocations == 0 and len(calls) == 1
    assert hit.payload is p_r1

    # The REQUIRED WORK on the new FILE key FAILS terminally:
    def failing_seam() -> WorkSeam:
        async def seam_fail() -> bytes:
            calls.append(1)
            raise RuntimeError("synthetic prepared-work failure")

        return seam_fail

    bad = await work.resolve(ns, k2a, failing_seam())
    assert bad.outcome is RamWorkOutcome.FAILED
    assert bad.limitation is RamWorkLimitation.WORK_FAILED
    assert bad.http_status == 503
    assert bad.invocations == 1
    assert bad.attempt_invocations == 1
    assert len(calls) == 2
    # No retry: the SAME fixed terminal failure re-serves
    # with zero new invocations:
    again = await work.resolve(ns, k2a, seam)
    assert again.outcome is RamWorkOutcome.FAILED
    assert again.limitation is RamWorkLimitation.WORK_FAILED
    assert again.http_status == 503
    assert again.invocations == 0
    assert again.attempt_invocations == 1
    assert len(calls) == 2
    # The failure does not poison the preserved root key,
    # and the admitted current rows are intact:
    assert owner.lookup(k2a, ns).outcome is RamStateOutcome.FOUND
    hit2 = await work.resolve(ns, k1, seam)
    assert hit2.outcome is RamWorkOutcome.HIT
    assert hit2.invocations == 0 and len(calls) == 2
    assert hit2.payload is p_r1


L5_ROOT = "Read `A.md` and `B.md` before work."
L5_B = "Synthetic nonroot B.\n"
L5_ROOT2 = "Second root. Read `A.md`."


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
async def test_l5_update_races_with_inflight_work(mode: AdmissionMode, endpoint: str) -> None:
    """L5 (store update vs in-flight work under pressure): the
    seam is ACTUALLY gated (append the invocation, signal
    entered, await release), so the claim is provably IN
    FLIGHT at the store transition.  An admitted NON-ADVERSE
    additive update committed while the attempt is in flight
    must neither lose nor delay-publish the in-flight
    completion (the gated claimant COMPLETES after the
    commit, the concurrent follower -- proven registered by
    its EXACT waiter reservation before release -- JOINS the
    ONE shared attempt with zero invocations, the retained
    payload is HIT-able, and the NEW key progresses with a
    second invocation); and a capacity-REFUSED changed-root
    update quarantines while the attempt is in flight (the
    ceiling crosses the store charge PLUS the ACTUAL LIVE
    work charge measured at the crossing, by exactly one
    byte), fencing the in-flight completion as the fixed 409
    currentness terminal (the ACTUAL invocation recorded,
    nothing published), while a resolve ordered AFTER the
    quarantine is refused pre-claim with zero invocations.
    The refused update commits nothing (the owner's state /
    occupancy and the unrelated owner of the same registry
    are preserved); the explicit teardown is the only exit.
    No lock is held across the await: the synchronous update
    commits while the gated seam awaits its release."""

    def make_gated(calls: list[int], entered: asyncio.Event, gate: asyncio.Event) -> WorkSeam:
        async def seam() -> bytes:
            calls.append(1)
            entered.set()
            await gate.wait()
            return LIFECYCLE_PAYLOAD

        return seam

    # -- Phase A: the admitted non-adverse additive update --
    ns_a, s0 = r_bootstrap(mode, f"ram019c-l5a-{mode.value}-{endpoint}", root_body=L5_ROOT)
    s_a = _l1_dep_read(s0, ns_a, "a1", endpoint, "A.md", L4_A)
    s_ab = _l1_dep_read(s_a, ns_a, "b1", endpoint, "B.md", L5_B)
    t1a = derive_root_region_admission(s_a, ns_a)
    assert t1a.outcome is RootRegionAdmissionOutcome.READY, t1a.diagnostics
    t2a = derive_root_region_admission(s_ab, ns_a)
    assert t2a.outcome is RootRegionAdmissionOutcome.READY, t2a.diagnostics
    adm1a = t1a.admission
    assert adm1a is not None
    adm2a = t2a.admission
    assert adm2a is not None
    k1a = adm1a.root_entry.content_key
    k_b = _path_key(t2a, "B.md")
    assert adm2a.root_entry.content_key == k1a  # the root is preserved
    gate = asyncio.Event()
    entered = asyncio.Event()
    reg_a = _work_registry()
    work_a = reg_a.work
    assert work_a is not None
    owner_a = reg_a.acquire(ns_a)
    assert owner_a.admit(s_a, t1a, ns_a, expected_revision=0).outcome is RamStateOutcome.ADMITTED
    calls_a: list[int] = []
    seam_a = make_gated(calls_a, entered, gate)
    t1 = asyncio.create_task(work_a.resolve(ns_a, k1a, seam_a))
    await entered.wait()  # the claim is live and the seam is in flight
    assert len(calls_a) == 1
    # The non-adverse additive update commits while the
    # attempt is in flight:
    assert owner_a.admit(s_ab, t2a, ns_a, expected_revision=1).outcome is RamStateOutcome.ADMITTED
    # The concurrent follower registers BEFORE the release
    # (its EXACT waiter reservation is charged):
    okey_a = owner_a.namespace.lineage_key
    w_before = work_a.session_bytes(okey_a)
    t2 = asyncio.create_task(work_a.resolve(ns_a, k1a, seam_a))
    await asyncio.sleep(0)
    assert work_a.session_bytes(okey_a) == w_before + RAM_WORK_WAITER_RESERVATION_BYTES
    gate.set()
    r1 = await t1
    assert r1.outcome is RamWorkOutcome.COMPLETED
    assert r1.invocations == 1
    r2 = await t2
    assert r2.outcome is RamWorkOutcome.JOINED
    assert r2.invocations == 0
    assert r2.payload is r1.payload
    # The in-flight completion published: the retained
    # payload is a RAM-only HIT; the NEW key progresses:
    hit = await work_a.resolve(ns_a, k1a, seam_a)
    assert hit.outcome is RamWorkOutcome.HIT and hit.invocations == 0
    assert hit.payload is r1.payload
    r_b = await work_a.resolve(ns_a, k_b, seam_a)
    assert r_b.outcome is RamWorkOutcome.COMPLETED
    assert r_b.invocations == 1 and len(calls_a) == 2
    # -- Phase C: the capacity-refused changed-root update --
    ns_c, s0c = r_bootstrap(
        mode,
        f"ram019c-l5c-{mode.value}-{endpoint}",
        root_body="Read `A.md` before changing code.",
    )
    s_fc = _l1_dep_read(s0c, ns_c, "a1", endpoint, "A.md", L4_A)
    s_rc = _l1_dep_read(s_fc, ns_c, "root2", endpoint, ROOT_FILENAME, L5_ROOT2)
    t1c = derive_root_region_admission(s_fc, ns_c)
    assert t1c.outcome is RootRegionAdmissionOutcome.READY, t1c.diagnostics
    t2c = derive_root_region_admission(s_rc, ns_c)
    assert t2c.outcome is RootRegionAdmissionOutcome.READY, t2c.diagnostics
    adm1c = t1c.admission
    assert adm1c is not None
    k1c = adm1c.root_entry.content_key
    k1ca = _path_key(t1c, "A.md")
    # Measure the ACTUAL store charge AND the ACTUAL LIVE
    # work charge at the crossing on a probe registry (the
    # probe attempt is gated IN FLIGHT while w_live is
    # read):
    p_reg = _work_registry()
    p_work = p_reg.work
    assert p_work is not None
    p_owner = p_reg.acquire(ns_c)
    assert p_owner.admit(s_fc, t1c, ns_c, expected_revision=0).outcome is RamStateOutcome.ADMITTED
    charge1 = p_owner.owned_bytes
    p_gate = asyncio.Event()
    p_entered = asyncio.Event()
    pcalls: list[int] = []
    p_seam = make_gated(pcalls, p_entered, p_gate)
    pt = asyncio.create_task(p_work.resolve(ns_c, k1c, p_seam))
    await p_entered.wait()
    w_live = p_work.session_bytes(p_owner.namespace.lineage_key)
    assert w_live > 0
    p_gate.set()
    assert (await pt).outcome is RamWorkOutcome.COMPLETED
    assert p_owner.admit(s_rc, t2c, ns_c, expected_revision=1).outcome is RamStateOutcome.ADMITTED
    delta2 = p_owner.owned_bytes - charge1
    assert delta2 > 0
    # The real registry: the session ceiling crosses the
    # store charge PLUS the ACTUAL LIVE work charge at the
    # crossing, by exactly one byte:
    reg_c = _work_registry()
    work_c = reg_c.work
    assert work_c is not None
    owner_c = reg_c.new_owner(ns_c, session_max_owned_bytes=charge1 + delta2 + w_live - 1)
    assert owner_c.admit(s_fc, t1c, ns_c, expected_revision=0).outcome is RamStateOutcome.ADMITTED
    assert owner_c.owned_bytes == charge1  # the measurement aligns
    gate_c = asyncio.Event()
    entered_c = asyncio.Event()
    calls_c: list[int] = []
    seam_c = make_gated(calls_c, entered_c, gate_c)
    tc1 = asyncio.create_task(work_c.resolve(ns_c, k1c, seam_c))
    await entered_c.wait()  # the claim is live and the seam is in flight
    assert len(calls_c) == 1
    # The LIVE work charge at the crossing aligns with the
    # probe's measured crossing charge:
    assert work_c.session_bytes(owner_c.namespace.lineage_key) == w_live
    proc_before = reg_c.process_owned_bytes
    # The changed-root update is capacity-refused and
    # quarantines while the attempt is in flight:
    rc_a2 = owner_c.admit(s_rc, t2c, ns_c, expected_revision=1)
    assert rc_a2.outcome is RamStateOutcome.REFUSED
    assert rc_a2.limitation is RamStateLimitation.SESSION_OWNED_BYTES_OVER_BOUND
    assert rc_a2.http_status == 503
    assert rc_a2.charged_bytes == owner_c.owned_bytes + delta2  # full candidate charge
    assert owner_c.quarantined is True
    # Atomic: nothing committed, nothing released:
    assert owner_c.owned_bytes == charge1
    assert reg_c.process_owned_bytes == proc_before
    gate_c.set()
    # The in-flight completion is fenced by the quarantine
    # (fixed 409 currentness terminal; the ACTUAL invocation
    # is recorded; nothing is published):
    r_inflight = await tc1
    assert r_inflight.outcome is RamWorkOutcome.FAILED
    assert r_inflight.limitation is RamWorkLimitation.KEY_NOT_CURRENT
    assert r_inflight.http_status == 409
    assert r_inflight.invocations == 1
    assert len(calls_c) == 1
    # The old keys are unusable; a resolve ordered AFTER the
    # quarantine is refused pre-claim (zero invocations):
    for old in (k1c, k1ca):
        lk = owner_c.lookup(old, ns_c)
        assert lk.outcome is RamStateOutcome.NOT_FOUND
        assert lk.limitation is RamStateLimitation.OWNER_QUARANTINED
    r_after = await work_c.resolve(ns_c, k1c, seam_c)
    assert r_after.outcome is RamWorkOutcome.REFUSED
    assert r_after.limitation is RamStateLimitation.OWNER_QUARANTINED
    assert r_after.http_status == 409
    assert r_after.invocations == 0 and len(calls_c) == 1
    # An UNRELATED owner of the SAME registry is untouched:
    ns_b, s1b = r_bootstrap(mode, f"ram019c-l5cb-{mode.value}-{endpoint}", root_body="Other root.")
    t1b = derive_root_region_admission(s1b, ns_b)
    assert t1b.outcome is RootRegionAdmissionOutcome.READY, t1b.diagnostics
    owner_b = reg_c.acquire(ns_b)
    assert owner_b.admit(s1b, t1b, ns_b, expected_revision=0).outcome is RamStateOutcome.ADMITTED
    adm_b = t1b.admission
    assert adm_b is not None
    assert owner_b.lookup(adm_b.root_entry.content_key, ns_b).outcome is RamStateOutcome.FOUND
    # The explicit teardown is the only exit:
    proc_before_td = reg_c.process_owned_bytes
    td = await work_c.teardown_owner(ns_c)
    assert td.outcome is RamWorkOutcome.TEARDOWN
    assert 0 < td.freed_bytes <= proc_before_td
    assert reg_c.get(ns_c) is None
    # The unrelated owner survives the teardown untouched:
    assert owner_b.lookup(adm_b.root_entry.content_key, ns_b).outcome is RamStateOutcome.FOUND


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
async def test_l5b_teardown_races_inflight_work_and_epoch_reacquire(
    mode: AdmissionMode, endpoint: str
) -> None:
    """L5b (teardown vs in-flight work, repeated cancellation
    during the drain, old-vs-new epoch): an admitted
    non-adverse update commits while the attempt is in
    flight; two concurrent joiners are REPEATEDLY cancelled
    (each detaches itself only; the work keeps running); the
    explicit async teardown then fences, cancels AND awaits
    the in-flight work (the claimant is re-served the fixed
    typed 503 OWNER_TORN_DOWN terminal with the ACTUAL
    invocation recorded), releases the store owner and the
    work plane in ONE critical section (no same-epoch reset
    window) with no leaked tasks and the honest freed-byte
    semantics.  The OLD owner/epoch can never be revived: a
    resolve on the spent namespace is refused owner-absent,
    and a re-acquire of the SAME namespace mints a DISTINCT
    fenced epoch whose owner has NO current rows (lookup
    NOT_FOUND, resolve KEY_NOT_CURRENT) and admits the
    genuine record fresh (expected_revision 0), where a
    brand-new attempt is legitimately invoked once -- the
    old owner's terminal metadata is gone with it."""
    ns, s0 = r_bootstrap(mode, f"ram019c-l5b-{mode.value}-{endpoint}", root_body=L5_ROOT)
    s_a = _l1_dep_read(s0, ns, "a1", endpoint, "A.md", L4_A)
    s_ab = _l1_dep_read(s_a, ns, "b1", endpoint, "B.md", L5_B)
    t1 = derive_root_region_admission(s_a, ns)
    assert t1.outcome is RootRegionAdmissionOutcome.READY, t1.diagnostics
    t2 = derive_root_region_admission(s_ab, ns)
    assert t2.outcome is RootRegionAdmissionOutcome.READY, t2.diagnostics
    adm1 = t1.admission
    assert adm1 is not None
    k1 = adm1.root_entry.content_key
    reg = _work_registry()
    work = reg.work
    assert work is not None
    owner = reg.acquire(ns)
    assert owner.admit(s_a, t1, ns, expected_revision=0).outcome is RamStateOutcome.ADMITTED
    gate = asyncio.Event()
    entered = asyncio.Event()
    calls: list[int] = []

    def make_gated() -> WorkSeam:
        async def seam() -> bytes:
            calls.append(1)
            entered.set()
            await gate.wait()
            return LIFECYCLE_PAYLOAD

        return seam

    r1task = asyncio.create_task(work.resolve(ns, k1, make_gated()))
    await entered.wait()  # the claim is live and the seam is in flight
    assert len(calls) == 1
    # The admitted non-adverse update commits while the
    # attempt is in flight:
    assert owner.admit(s_ab, t2, ns, expected_revision=1).outcome is RamStateOutcome.ADMITTED
    # Two concurrent joiners, repeatedly cancelled (each
    # detaches itself only; the work keeps running):
    j1 = asyncio.create_task(work.resolve(ns, k1, make_gated()))
    await asyncio.sleep(0)
    j2 = asyncio.create_task(work.resolve(ns, k1, make_gated()))
    await asyncio.sleep(0)
    j1.cancel()
    with pytest.raises(asyncio.CancelledError):
        await j1
    j2.cancel()
    with pytest.raises(asyncio.CancelledError):
        await j2
    assert len(calls) == 1  # the joiners never ran a seam of their own
    proc_before_td = reg.process_owned_bytes
    # The explicit teardown fences, cancels AND awaits the
    # in-flight work, then releases store + work atomically:
    td = await work.teardown_owner(ns)
    assert td.outcome is RamWorkOutcome.TEARDOWN
    assert 0 < td.freed_bytes <= proc_before_td
    assert reg.get(ns) is None
    # The in-flight claimant was re-served the fixed typed
    # 503 terminal (the ACTUAL invocation recorded):
    r1 = await r1task
    assert r1.outcome is RamWorkOutcome.FAILED
    assert r1.limitation is RamWorkLimitation.OWNER_TORN_DOWN
    assert r1.http_status == 503
    assert r1.invocations == 1
    assert len(calls) == 1
    # No leaked tasks:
    leftover = [t for t in asyncio.all_tasks() if t is not asyncio.current_task() and not t.done()]
    assert leftover == []
    # The OLD owner/epoch can never be revived:
    r_old = await work.resolve(ns, k1, make_gated())
    assert r_old.outcome is RamWorkOutcome.REFUSED
    assert r_old.limitation is RamWorkLimitation.OWNER_ABSENT
    assert r_old.invocations == 0 and len(calls) == 1
    # A re-acquire of the SAME namespace mints a DISTINCT
    # fenced epoch:
    owner2 = reg.acquire(ns)
    assert owner2.epoch != owner.epoch
    assert owner2.lookup(k1, ns).outcome is RamStateOutcome.NOT_FOUND
    r_pre = await work.resolve(ns, k1, make_gated())
    assert r_pre.outcome is RamWorkOutcome.REFUSED
    assert r_pre.limitation is RamWorkLimitation.KEY_NOT_CURRENT
    assert r_pre.http_status == 409
    # The genuine record admits fresh (expected_revision 0);
    # a brand-new attempt is legitimately invoked once:
    assert owner2.admit(s_a, t1, ns, expected_revision=0).outcome is RamStateOutcome.ADMITTED
    calls2: list[int] = []
    r_new = await work.resolve(ns, k1, _lifecycle_seam(calls2))
    assert r_new.outcome is RamWorkOutcome.COMPLETED
    assert r_new.invocations == 1 and len(calls2) == 1


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
async def test_l5c_repeated_teardown_cancellation_during_drain(
    mode: AdmissionMode, endpoint: str
) -> None:
    """L5c (repeated cancellation of the teardown task DURING
    its drain): the owned seam carries a controlled cleanup
    barrier that is ACTUALLY invoked and stays live (it
    handles cancellation at that barrier and blocks until
    the test releases it), so the drain's owned task is
    genuinely live while the teardown is held.  The teardown
    runs as its OWN task: it fences, cancels the dispatch
    task and awaits the drain; the test then cancels the
    TEARDOWN task repeatedly while the cleanup barrier is
    held and verifies the teardown stays PENDING -- the
    fence is held, the store owner is still registered, the
    live attempt is not yet finalized: the teardown cannot
    release or propagate while its owned task is still
    live.  Only after the controlled release does the drain
    complete (the attempt terminalizes), the store and work
    release atomically, and the cancellation PROPAGATE (the
    teardown task ends cancelled, after the actual
    release) -- with no leaked tasks, no charge leak and no
    double release (the process counter returns between the
    unrelated-owner baseline and the pre-teardown total)
    and the unrelated owner intact.  The invariant is that
    teardown cannot release/propagate while its owned task
    is live; this is not a promise that arbitrary callback
    cleanup is universally uncancellable."""
    ns, s0 = r_bootstrap(
        mode,
        f"ram019c-l5c-{mode.value}-{endpoint}",
        root_body="Read `A.md` before changing code.",
    )
    s_a = _l1_dep_read(s0, ns, "a1", endpoint, "A.md", L4_A)
    t1 = derive_root_region_admission(s_a, ns)
    assert t1.outcome is RootRegionAdmissionOutcome.READY, t1.diagnostics
    adm1 = t1.admission
    assert adm1 is not None
    k1 = adm1.root_entry.content_key
    reg = _work_registry()
    work = reg.work
    assert work is not None
    # An UNRELATED owner of the SAME registry (the baseline):
    ns_b, s1b = r_bootstrap(mode, f"ram019c-l5cb-{mode.value}-{endpoint}", root_body="Other root.")
    t1b = derive_root_region_admission(s1b, ns_b)
    assert t1b.outcome is RootRegionAdmissionOutcome.READY, t1b.diagnostics
    owner_b = reg.acquire(ns_b)
    assert owner_b.admit(s1b, t1b, ns_b, expected_revision=0).outcome is RamStateOutcome.ADMITTED
    adm_b = t1b.admission
    assert adm_b is not None
    k_b = adm_b.root_entry.content_key
    proc_unrelated = reg.process_owned_bytes
    # The main owner with ONE in-flight gated attempt:
    owner = reg.acquire(ns)
    assert owner.admit(s_a, t1, ns, expected_revision=0).outcome is RamStateOutcome.ADMITTED
    proc_before_td = reg.process_owned_bytes
    assert proc_before_td > proc_unrelated
    gate = asyncio.Event()
    entered = asyncio.Event()
    cleaning = asyncio.Event()
    clean_release = asyncio.Event()
    calls: list[int] = []

    def make_cleanup_seam() -> WorkSeam:
        async def seam() -> bytes:
            calls.append(1)
            entered.set()
            try:
                await gate.wait()
            finally:
                cleaning.set()
                # The controlled cleanup barrier: handles
                # cancellation at the barrier and stays
                # LIVE until the test releases it.
                while True:
                    try:
                        await clean_release.wait()
                        break
                    except asyncio.CancelledError:
                        continue
            return LIFECYCLE_PAYLOAD

        return seam

    r1task = asyncio.create_task(work.resolve(ns, k1, make_cleanup_seam()))
    await entered.wait()  # the claim is live and the seam is in flight
    assert len(calls) == 1
    # Start the teardown as its OWN task:
    tdtask = asyncio.create_task(work.teardown_owner(ns))
    await cleaning.wait()  # the owned cleanup is live at its barrier
    # Repeatedly cancel the TEARDOWN task while the cleanup
    # barrier is held: it must stay PENDING (no release, no
    # propagation, no fence drop) while the owned task is
    # still live:
    okey = owner.namespace.lineage_key
    for _ in (1, 2, 3):
        tdtask.cancel()
        await asyncio.sleep(0)
        assert not tdtask.done()
        assert reg.get(ns) is not None  # the store owner is still registered
        ow = work._owners.get(okey)
        assert ow is not None
        assert ow.fenced is True  # the fence is held
        assert len(ow.live) == 1  # the attempt is not yet finalized
    # Release the controlled cleanup barrier:
    clean_release.set()
    # The cancellation PROPAGATES only after the actual
    # release (drain complete, store + work released):
    with pytest.raises(asyncio.CancelledError):
        await tdtask
    assert reg.get(ns) is None
    assert work._owners.get(okey) is None
    # The claimant was re-served the fixed typed 503
    # terminal during the drain (the ACTUAL invocation
    # recorded):
    r1 = await r1task
    assert r1.outcome is RamWorkOutcome.FAILED
    assert r1.limitation is RamWorkLimitation.OWNER_TORN_DOWN
    assert r1.http_status == 503
    assert r1.invocations == 1
    assert len(calls) == 1
    # No leaked tasks:
    leftover = [t for t in asyncio.all_tasks() if t is not asyncio.current_task() and not t.done()]
    assert leftover == []
    # No charge leak and no double release (the unrelated
    # owner's charge is intact beneath the retained
    # high-water):
    assert proc_unrelated <= reg.process_owned_bytes < proc_before_td
    # The unrelated owner survives untouched:
    assert owner_b.lookup(k_b, ns_b).outcome is RamStateOutcome.FOUND


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
async def test_l6_lifecycle_hits_with_denied_host_io(
    mode: AdmissionMode, endpoint: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    """L6 (denied-filesystem lifecycle proof): after the
    genuine initial preparation (the two admissions and the
    prepared payload), the closed 24-facility host-IO trap
    stays open across repeated usable owner lookups, repeated
    RAM-only work hits of the retained payload (zero new
    seam invocations) and the representative retained-state
    traversals -- the retained history catalog, the current
    admission's path associations and key-record ownership
    groups, and the ACTUAL current graph overlay (nodes and
    edges) of the retained T result -- proving the normal
    RAM hit / current-selection path performs no content
    reads and no recovery deserialization.  The work plane's
    own denied-IO proof is test_p (test_bundle_ram_work)."""
    ns, s0 = r_bootstrap(mode, f"ram019c-l6-{mode.value}-{endpoint}", root_body=L5_ROOT)
    s_a = _l1_dep_read(s0, ns, "a1", endpoint, "A.md", L4_A)
    s_ab = _l1_dep_read(s_a, ns, "b1", endpoint, "B.md", L5_B)
    t1 = derive_root_region_admission(s_a, ns)
    assert t1.outcome is RootRegionAdmissionOutcome.READY, t1.diagnostics
    t2 = derive_root_region_admission(s_ab, ns)
    assert t2.outcome is RootRegionAdmissionOutcome.READY, t2.diagnostics
    reg = _work_registry()
    work = reg.work
    assert work is not None
    owner = reg.acquire(ns)
    assert owner.admit(s_a, t1, ns, expected_revision=0).outcome is RamStateOutcome.ADMITTED
    assert owner.admit(s_ab, t2, ns, expected_revision=1).outcome is RamStateOutcome.ADMITTED
    adm2 = t2.admission
    assert adm2 is not None
    k_root = adm2.root_entry.content_key
    k_a = _path_key(t2, "A.md")
    k_b = _path_key(t2, "B.md")
    # The genuine initial preparation before the trap is
    # installed:
    calls: list[int] = []
    seam = _lifecycle_seam(calls)
    r0 = await work.resolve(ns, k_root, seam)
    assert r0.outcome is RamWorkOutcome.COMPLETED
    assert r0.payload is not None
    assert len(calls) == 1
    # Install the closed 24-facility host-IO trap (scoped:
    # the patches are restored before any failure renders):
    io_calls: list[str] = []

    def trap(label: str) -> Callable[..., Any]:
        def refused(*trap_args: Any, **trap_kwargs: Any) -> Any:
            io_calls.append(label)
            raise AssertionError("forbidden host IO: " + label)

        return refused

    with monkeypatch.context() as scoped_patch:
        for module, name in _host_io_facilities():
            scoped_patch.setattr(module, name, trap(module.__name__ + "." + name))
        # Repeated usable owner lookups (the current rows:
        # the root and BOTH FILE rows):
        for key in (k_root, k_a, k_b):
            assert owner.lookup(key, ns).outcome is RamStateOutcome.FOUND
        # Repeated RAM-only work hits (the retained payload
        # by identity, zero new invocations):
        h1 = await work.resolve(ns, k_root, seam)
        assert h1.outcome is RamWorkOutcome.HIT
        h2 = await work.resolve(ns, k_root, seam)
        assert h2.outcome is RamWorkOutcome.HIT
        assert h1.payload is r0.payload
        assert h2.payload is r0.payload
        assert h1.invocations == 0 and len(calls) == 1
        # Representative retained-state traversals (pure
        # data access): the retained history catalog, the
        # current admission's path associations and
        # key-record ownership groups, and the ACTUAL
        # current graph overlay of the retained T result:
        for entry in owner.history:
            repr(entry)
        for assoc in adm2.path_associations:
            repr(assoc)
        for entry_row in adm2.entries:
            for group in entry_row.key_record.ownership_groups:
                repr(group)
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
        # The composed ASYNC lifecycle operation under the
        # SAME trap: the explicit teardown fences and
        # releases store + work without any host IO; the
        # namespace is then fenced old (the old owner's
        # lookup is refused epoch-fenced; the work plane
        # finds no live owner):
        td = await work.teardown_owner(ns)
        assert td.outcome is RamWorkOutcome.TEARDOWN
        assert td.freed_bytes > 0
        assert reg.get(ns) is None
        lk_td = owner.lookup(k_root, ns)
        assert lk_td.outcome is RamStateOutcome.NOT_FOUND
        assert lk_td.limitation is RamStateLimitation.EPOCH_FENCED
        r_td = await work.resolve(ns, k_root, seam)
        assert r_td.outcome is RamWorkOutcome.REFUSED
        assert r_td.limitation is RamWorkLimitation.OWNER_ABSENT
        assert r_td.invocations == 0 and len(calls) == 1
        # Zero content reads, zero new seam invocations:
        assert io_calls == []
        assert len(calls) == 1

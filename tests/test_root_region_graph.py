"""Permanent acceptance matrix (A-G) for the bounded pure
selected-root-region source + current-graph derivation (objective
018-r): ``derive_root_region_graph`` over the ACTUAL 018-p P state
with the ACTUAL same-run 018-q Q phase, the charged selected-source
resolution and the ACTUAL accepted F/E current graph under the
selected root.

Every fixture is synthetic and built exclusively through the ACTUAL
public P/Q factories and the public R API (no private kernel calls in
acceptance positives; model-level closed-law negatives exercise the
result/source constructors directly, which is the accepted internal
trusted boundary).  Readiness here is graph-only and INERT: it never
means admitted bundles, acquired dependencies, compiled cache, HTTP
readiness or v1 runtime.
"""

from __future__ import annotations

import json
from typing import Any

import pytest
from pydantic import ValidationError

from slaif_local_coding.constitution.bundles.bundle_admission_models import (
    AdmissionMode,
    make_bundle_admission_namespace,
)
from slaif_local_coding.constitution.bundles.causal_history_models import (
    CAUSAL_ROOT_FACT,
    CausalHistoryLimitation,
    HistoryBounds,
)
from slaif_local_coding.constitution.bundles.current_graph import _StageLedger
from slaif_local_coding.constitution.bundles.current_graph_models import (
    CURRENT_GRAPH_CONTRACT_VERSION,
    CURRENT_GRAPH_POLICY_VERSION,
    ROOT_OWNER,
    CurrentGraphBounds,
    CurrentGraphLimitation,
    CurrentGraphOutcome,
    CurrentGraphReason,
    CurrentGraphStatus,
    CurrentGraphSupplierKind,
    _owner_source,
)
from slaif_local_coding.constitution.bundles.currentness_models import (
    CURRENTNESS_CONTRACT_VERSION,
    CURRENTNESS_POLICY_VERSION,
    CurrentnessBounds,
)
from slaif_local_coding.constitution.bundles.graph_models import (
    ROOT_FILENAME,
    GraphBounds,
)
from slaif_local_coding.constitution.bundles.observation_models import PRIVATE_ID_PLACEHOLDER
from slaif_local_coding.constitution.bundles.root_lineage import _HOuter
from slaif_local_coding.constitution.bundles.root_lineage_models import (
    EnvelopeRootProvenance,
    ReadRootProvenance,
    RootLineageLimitation,
    RootLineageOutcome,
    RootSelectionOutcome,
    _lineage_key,
)
from slaif_local_coding.constitution.bundles.root_region_currentness_models import (
    RootRegionCurrentnessBounds,
    RootRegionCurrentnessOutcome,
    RootRegionUncertaintyClass,
)
from slaif_local_coding.constitution.bundles.root_region_graph import (
    _r_resolve_source,
    _RFOuter,
    _ROuter,
    _RQOuter,
    derive_root_region_graph,
)
from slaif_local_coding.constitution.bundles.root_region_graph_models import (
    ROOT_REGION_GRAPH_CONTRACT_VERSION,
    ROOT_REGION_GRAPH_POLICY_VERSION,
    ResolvedRootRegionSource,
    RootRegionGraphBounds,
    RootRegionGraphDiagnostic,
    RootRegionGraphOutcome,
    RootRegionGraphResult,
    root_region_graph_scope_key,
)
from slaif_local_coding.constitution.bundles.root_region_lineage import (
    bootstrap_root_region_lineage,
    observe_root_region_lineage,
    register_root_region_issuance,
    register_root_region_receipt,
    select_current_root_region,
    validate_root_region_lineage_state,
)
from slaif_local_coding.constitution.bundles.root_region_lineage_models import (
    ROOT_REGION_LINEAGE_POLICY_VERSION,
    RootRegionLineageFact,
    RootRegionReadProvenance,
    make_root_region_lineage_namespace,
)
from slaif_local_coding.constitution.cache import RequestIdentity
from tests.test_causal_history import (
    ENDPOINTS,
    FINGERPRINT,
    IDENTITY,
    MODES,
    ROOT_TEXT,
    WORKSPACE,
    read_request,
    sha256_hex,
)
from tests.test_root_lineage import _min_accepted_cap, occurrences, rooted
from tests.test_root_region_currentness import (
    A_TEXT as Q_A_TEXT,
)
from tests.test_root_region_currentness import (
    B_TEXT as Q_B_TEXT,
)
from tests.test_root_region_currentness import (
    BOUNDARYLESS_CMD,
    NONROOT_CMD,
    OPAQUE_BODY,
    REPEAT3_CMD,
    REPEAT_CMD,
    _e_audit_state,
    _e_branch_state,
    _frontier_state,
    q_bootstrap,
    q_issue,
    q_observe,
    q_occ,
)
from tests.test_root_region_currentness import (
    MARK as Q_MARK,
)
from tests.test_root_region_currentness import (
    MIX_CMD as Q_MIX_CMD,
)
from tests.test_root_region_currentness import (
    mixed_body as q_mixed_body,
)
from tests.test_root_region_lineage import (
    A_TEXT,
    B_TEXT,
    FIRST_CMD,
    LAST_CMD,
    MARK,
    MARK2,
    MIDDLE_CMD,
    MIX_CMD,
    V2,
    V3,
    _host_io_facilities,
    _mixed_body,
    _two_sibling_regions,
    r_bootstrap,
    r_issue,
    r_observe,
    region_fact,
)

# --- Shared R helpers ---------------------------------------------------


def _r(state: Any, ns: Any, **kwargs: Any) -> RootRegionGraphResult:
    """One public R derivation with the exact retained state identity."""
    r = derive_root_region_graph(state, ns, **kwargs)
    assert r.state is state
    assert r.lineage_key == state.lineage_key
    assert r.revision == state.revision
    return r


def r_receipt(
    state: Any, ns: Any, call_id: str, endpoint: str, facts: tuple[Any, ...], cmd: str
) -> Any:
    """The genuine delayed receipt for an issued call (the actual D
    receipt law): the accepted transition with its exact retained
    state."""
    t = register_root_region_receipt(
        state,
        ns,
        call_id,
        endpoint,
        "exec_command",
        json.dumps({"cmd": cmd}),
        facts,
        state.revision,
    )
    assert t.outcome.value == "accepted", t.diagnostics
    return t


def _assert_ready_bindings(r: RootRegionGraphResult, state: Any, root_body: str) -> None:
    """The closed READY law: exact root body, digest/length, original
    fact/occurrence/proof identity, actual Q ready + F ok + E overlay
    joins, no diagnostics, no published positive leakage."""
    assert r.outcome is RootRegionGraphOutcome.READY
    assert r.diagnostics == ()
    src = r.resolved_source
    assert src is not None
    assert src.root_text == root_body
    assert src.root_digest == sha256_hex(root_body)
    assert src.root_byte_length == len(root_body.encode("utf-8"))
    assert isinstance(src.fact, RootRegionLineageFact)
    assert any(f is src.fact for f in state.root_facts)
    q = r.q_result
    assert q is not None
    assert q.outcome is RootRegionCurrentnessOutcome.READY
    assert q.state is state
    assert r.q_result is not None
    assert q.scope_key == r.q_result.scope_key
    assert r.q_bounds == q.bounds
    f = r.f_result
    assert f is not None
    assert f.outcome is CurrentGraphOutcome.OK
    assert f.state is state.d_state
    assert f.overlay is not None
    assert f.overlay.root_digest == src.root_digest
    e = r.e_overlay
    assert e is not None
    assert e.scope_key == f.overlay.currentness_scope_key
    assert e.history_key == state.d_state.history_key
    assert e.revision == state.d_state.revision
    assert r.scope_key == root_region_graph_scope_key(
        state.lineage_key,
        ROOT_REGION_GRAPH_CONTRACT_VERSION,
        ROOT_REGION_GRAPH_POLICY_VERSION,
        r.bounds,
        r.q_bounds,
        r.f_bounds,
        r.e_bounds,
        r.graph_version,
    )


def _mixed_region_state(
    mode: AdmissionMode, endpoint: str, lineage: str, a_text: str = A_TEXT
) -> tuple[Any, Any]:
    """Bootstrap v1 -> genuinely issued descendant mixed-only read with
    the complete root V2 (the earned P fixture, no singleton); the
    nonroot A.md member body is parameterized for the version-
    ownership law."""
    ns, s0 = r_bootstrap(mode, lineage)
    t1 = r_issue(s0, ns, "m1", endpoint, (CAUSAL_ROOT_FACT,), MIX_CMD)
    assert t1.outcome.value == "accepted"
    t2 = r_observe(
        t1.state, ns, (read_request(endpoint, "m1", _mixed_body(a_text, MARK, V2), MIX_CMD),)
    )
    assert t2.outcome.value == "accepted", t2.diagnostics
    return ns, t2.state


# --- A. Readiness: envelope / whole-read / mixed-region sources ---------


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_a_bootstrap_envelope_ready(mode: AdmissionMode, endpoint: str) -> None:
    """A1: the bootstrap-only P state derives READY with the envelope
    source: the ACTUAL anchor root body, no occurrence/proof reference,
    and the F graph under the bootstrap root digest."""
    ns, s0 = r_bootstrap(mode, f"r-a-env-{endpoint}")
    r = _r(s0, ns)
    _assert_ready_bindings(r, s0, ROOT_TEXT)
    src = r.resolved_source
    assert src is not None
    assert src.kind == "envelope"
    assert src.occurrence is None and src.proof is None
    assert src.fact is s0.root_facts[0]
    assert src.fact.provenance.kind == "envelope"
    f = r.f_result
    assert f is not None
    assert f.overlay is not None
    assert f.overlay.root_digest == sha256_hex(ROOT_TEXT)


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_a_mixed_region_v2_ready(mode: AdmissionMode, endpoint: str) -> None:
    """A2: the earned mixed-only region v2 (no independent singleton)
    derives READY with the read_region source: exact V2 root body,
    original fact/occurrence/proof identity, whole-proof aggregate kept
    distinct from the root member."""
    ns, s2 = _mixed_region_state(mode, endpoint, f"r-a-mix-{endpoint}")
    r = _r(s2, ns)
    _assert_ready_bindings(r, s2, V2)
    src = r.resolved_source
    assert src is not None
    assert src.kind == "read_region"
    occ = region_fact(s2, "m1").provenance
    assert src.fact is region_fact(s2, "m1")
    actual_occ = next(o for o in s2.d_state.occurrences if o.call_id == "m1")
    assert actual_occ is not None
    assert src.occurrence is not None
    assert src.proof is not None
    assert src.occurrence is actual_occ
    assert src.proof is actual_occ.proof
    p = src.fact.provenance
    assert p.occurrence_id == occ.occurrence_id
    assert p.whole_proof_digest == actual_occ.proof.source_digest
    assert p.whole_proof_byte_length == actual_occ.proof.source_byte_length
    assert p.whole_proof_byte_length != src.root_byte_length  # aggregate != root
    assert p.root_member_digest == src.root_digest
    assert p.root_member_byte_length == src.root_byte_length
    # The original bootstrap root binding stays intact (immutable scope).
    assert actual_occ.proof.root_digest == sha256_hex(ROOT_TEXT)


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_a_whole_read_ready(mode: AdmissionMode, endpoint: str) -> None:
    """A3: a genuine whole-read of the root file (no marker) derives
    READY with the read source: the whole proof IS the root body."""
    cmd = "cat AGENTS.md"
    ns, s0 = r_bootstrap(mode, f"r-a-read-{endpoint}")
    t1 = r_issue(s0, ns, "m1", endpoint, (CAUSAL_ROOT_FACT,), cmd)
    assert t1.outcome.value == "accepted", t1.diagnostics
    t2 = r_observe(t1.state, ns, (read_request(endpoint, "m1", V2, cmd),))
    assert t2.outcome.value == "accepted", t2.diagnostics
    r = _r(t2.state, ns)
    _assert_ready_bindings(r, t2.state, V2)
    src = r.resolved_source
    assert src is not None
    assert src.kind == "read"
    assert isinstance(src.fact.provenance, ReadRootProvenance)
    assert src.fact.provenance.read_digest == sha256_hex(V2)
    assert src.fact.provenance.read_byte_length == len(V2.encode("utf-8"))
    assert src.proof is not None
    assert src.proof.root_path == ROOT_FILENAME


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
@pytest.mark.parametrize(
    ("cmd", "body", "seg_index"),
    [
        (FIRST_CMD, _mixed_body(V2, MARK, A_TEXT), 0),
        (MIDDLE_CMD, _mixed_body(A_TEXT, MARK, V2, MARK2, B_TEXT), 1),
        (LAST_CMD, _mixed_body(A_TEXT, MARK, B_TEXT, MARK2, V2), 2),
    ],
    ids=["root-first", "root-middle", "root-last"],
)
def test_a_root_positions_ready(
    mode: AdmissionMode,
    endpoint: str,
    cmd: str,
    body: str,
    seg_index: int,
) -> None:
    """A4: the root member at the FIRST, MIDDLE and LAST operand
    position of the mixed command derives READY with the exact root
    body and the ACTUAL segment coordinate (character sums, never
    byte offsets or carrier offsets)."""
    ns, s0 = r_bootstrap(mode, f"r-a-pos{seg_index}-{endpoint}")
    t1 = r_issue(s0, ns, "m1", endpoint, (CAUSAL_ROOT_FACT,), cmd)
    assert t1.outcome.value == "accepted"
    t2 = r_observe(t1.state, ns, (read_request(endpoint, "m1", body, cmd),))
    assert t2.outcome.value == "accepted", t2.diagnostics
    r = _r(t2.state, ns)
    _assert_ready_bindings(r, t2.state, V2)
    assert r.resolved_source is not None
    assert isinstance(r.resolved_source.fact.provenance, RootRegionReadProvenance)
    assert r.resolved_source.fact.provenance.root_segment_index == seg_index
    assert MARK not in r.resolved_source.root_text  # markers never in the root


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_a_unicode_nonroot_prefix_ready(mode: AdmissionMode, endpoint: str) -> None:
    """A5: a multi-byte Unicode NONROOT prefix precedes the root
    member; the root interval is the sum of preceding segment
    CHARACTER lengths (never UTF-8 byte lengths or carrier offsets),
    so the exact root body is materialized despite bytes != chars."""
    a_unicode = "Synthetic \u00fcn\u00efcod\u00e9 nonroot \u2713 body.\n"
    assert len(a_unicode.encode("utf-8")) != len(a_unicode)
    ns, s0 = r_bootstrap(mode, f"r-a-uni-{endpoint}")
    t1 = r_issue(s0, ns, "m1", endpoint, (CAUSAL_ROOT_FACT,), MIX_CMD)
    assert t1.outcome.value == "accepted"
    t2 = r_observe(
        t1.state,
        ns,
        (read_request(endpoint, "m1", _mixed_body(a_unicode, MARK, V2), MIX_CMD),),
    )
    assert t2.outcome.value == "accepted", t2.diagnostics
    r = _r(t2.state, ns)
    _assert_ready_bindings(r, t2.state, V2)
    assert r.resolved_source is not None
    assert r.resolved_source.root_text == V2
    assert r.resolved_source.root_byte_length == len(V2.encode("utf-8"))
    # The nonroot prefix stays nonroot (no root claim, exact bytes).
    f = r.resolved_source.fact
    assert f.source_byte_length == len(V2.encode("utf-8"))


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
@pytest.mark.parametrize(
    ("tag", "root_body"),
    [
        ("crlf", "Region root with CRLF\r\nsecond line\r\n"),
        ("empty", ""),
    ],
    ids=["crlf", "empty"],
)
def test_a_crlf_and_empty_root_ready(
    mode: AdmissionMode, endpoint: str, tag: str, root_body: str
) -> None:
    """A6: a CRLF root body and a genuinely proven EMPTY root region
    both derive READY with the EXACT root text (CR/LF preserved, zero
    bytes legal)."""
    ns, s0 = r_bootstrap(mode, f"r-a-{tag}-{endpoint}")
    t1 = r_issue(s0, ns, "m1", endpoint, (CAUSAL_ROOT_FACT,), MIX_CMD)
    assert t1.outcome.value == "accepted"
    t2 = r_observe(
        t1.state,
        ns,
        (read_request(endpoint, "m1", _mixed_body(A_TEXT, MARK, root_body), MIX_CMD),),
    )
    assert t2.outcome.value == "accepted", t2.diagnostics
    r = _r(t2.state, ns)
    _assert_ready_bindings(r, t2.state, root_body)
    assert r.resolved_source is not None
    assert r.resolved_source.root_text == root_body
    assert r.resolved_source.root_byte_length == len(root_body.encode("utf-8"))


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_a_multi_member_carrier_ready(mode: AdmissionMode, endpoint: str) -> None:
    """A7: the multi-member single-frame carrier (three operands,
    three segments, ONE final frame) derives READY with the ACTUAL
    original producer owner/frontier association retained: the
    occurrence call/endpoint identity, the requested member list and
    the frozen frontier (issued AND anchored authority)."""
    ns, s0 = r_bootstrap(mode, f"r-a-carrier-{endpoint}")
    t1 = r_issue(s0, ns, "m1", endpoint, (CAUSAL_ROOT_FACT,), MIDDLE_CMD)
    assert t1.outcome.value == "accepted"
    t2 = r_observe(
        t1.state,
        ns,
        (read_request(endpoint, "m1", _mixed_body(A_TEXT, MARK, V2, MARK2, B_TEXT), MIDDLE_CMD),),
    )
    assert t2.outcome.value == "accepted", t2.diagnostics
    s2 = t2.state
    r = _r(s2, ns)
    _assert_ready_bindings(r, s2, V2)
    assert r.resolved_source is not None
    occ = r.resolved_source.occurrence
    assert occ is not None
    assert occ.call_id == "m1"
    assert occ.endpoint == endpoint
    proof = r.resolved_source.proof
    assert proof is not None
    assert [m.normalized for m in proof.requested_members] == ["A.md", "AGENTS.md", "B.md"]
    assert proof.source_byte_length > r.resolved_source.root_byte_length
    f = r.resolved_source.fact
    assert f.issued is True and f.authority is True


# --- B. Version-owned withdrawal/restoration under the selected root ----

# The two genuine A.md versions for the B3 ownership law: each carries
# a REAL outgoing reference so the withdrawn/re-owned outgoing
# derivation is proven by an actual edge, not a vacuous fixture.
A_OLD_TEXT = "Follow `Old.md`.\n"
A_NEW_TEXT = "Follow `New.md`.\n"


def _revert_state(mode: AdmissionMode, endpoint: str, lineage: str) -> tuple[Any, Any]:
    """The earned P deliberate-revert fixture: v2 whole read, then a
    genuinely NEW issued/anchored region DESCENDANT carrying the OLD
    bootstrap bytes (a deliberate revert under the P partial order)."""
    ns, s0 = r_bootstrap(mode, lineage)
    t1 = r_issue(s0, ns, "s1", endpoint, (CAUSAL_ROOT_FACT,), "cat AGENTS.md")
    assert t1.outcome.value == "accepted"
    t2 = r_observe(t1.state, ns, (read_request(endpoint, "s1", V2, "cat AGENTS.md"),))
    assert t2.outcome.value == "accepted"
    s2 = t2.state
    t3 = r_issue(s2, ns, "m1", endpoint, (occurrences(s2, "s1")[0].occurrence_id,), MIX_CMD)
    assert t3.outcome.value == "accepted"
    t4 = r_observe(
        t3.state, ns, (read_request(endpoint, "m1", _mixed_body(A_TEXT, MARK, ROOT_TEXT), MIX_CMD),)
    )
    assert t4.outcome.value == "accepted", t4.diagnostics
    return ns, t4.state


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_b_revert_restores_v1_graph_under_selected_root(mode: AdmissionMode, endpoint: str) -> None:
    """B1: the deliberate revert (old bootstrap bytes on a genuinely
    new region descendant) restores the v1 semantics UNDER THE
    SELECTED ROOT: READY with the old root body, the F graph derived
    under the OLD digest (the v1-only currentness wins), the
    withdrawn v2 content is no longer a current node digest, and the
    old v2 read is PRESERVED (retained, dominated -- never erased)."""
    ns, s4 = _revert_state(mode, endpoint, f"r-b-rev-{endpoint}")
    r = _r(s4, ns)
    _assert_ready_bindings(r, s4, ROOT_TEXT)
    assert r.resolved_source is not None
    assert r.resolved_source.kind == "read_region"
    assert r.f_result is not None
    overlay = r.f_result.overlay
    assert overlay is not None
    assert overlay.root_digest == sha256_hex(ROOT_TEXT)
    root_nodes = [n for n in overlay.nodes if n.path == ROOT_FILENAME]
    assert len(root_nodes) == 1
    assert root_nodes[0].status is CurrentGraphStatus.CURRENT_KNOWN
    assert root_nodes[0].digest == sha256_hex(ROOT_TEXT)
    # The withdrawn v2 content is not a possessed current source.
    assert all(
        n.digest != sha256_hex(V2)
        for n in overlay.nodes
        if n.status is CurrentGraphStatus.CURRENT_KNOWN
    )
    # The old v2 read stays retained historical evidence.
    assert len(s4.root_facts) == 3
    assert next(
        f for f in s4.root_facts if f.provenance.kind == "read"
    ).source_digest == sha256_hex(V2)


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_b_historical_retention_old_bytes_region_ready(mode: AdmissionMode, endpoint: str) -> None:
    """B2: a v2->v3 singleton chain plus a genuinely issued region
    descendant carrying the OLDER v2 bytes: the frozen partial order
    selects the maximal original; R derives READY under the retained
    v2 bytes with every historical fact intact."""
    ns, s0 = r_bootstrap(mode, f"r-b-hist-{endpoint}")
    t1 = r_issue(s0, ns, "s1", endpoint, (CAUSAL_ROOT_FACT,), "cat AGENTS.md")
    assert t1.outcome.value == "accepted"
    t2 = r_observe(t1.state, ns, (read_request(endpoint, "s1", V2, "cat AGENTS.md"),))
    assert t2.outcome.value == "accepted"
    s2 = t2.state
    t3 = r_issue(s2, ns, "s2", endpoint, (occurrences(s2, "s1")[0].occurrence_id,), "cat AGENTS.md")
    assert t3.outcome.value == "accepted"
    t4 = r_observe(t3.state, ns, (read_request(endpoint, "s2", V3, "cat AGENTS.md"),))
    assert t4.outcome.value == "accepted"
    s4 = t4.state
    t5 = r_issue(s4, ns, "m1", endpoint, (occurrences(s4, "s2")[0].occurrence_id,), MIX_CMD)
    assert t5.outcome.value == "accepted"
    t6 = r_observe(
        t5.state, ns, (read_request(endpoint, "m1", _mixed_body(A_TEXT, MARK, V2), MIX_CMD),)
    )
    assert t6.outcome.value == "accepted", t6.diagnostics
    s6 = t6.state
    r = _r(s6, ns)
    _assert_ready_bindings(r, s6, V2)
    assert r.resolved_source is not None
    assert r.resolved_source.kind == "read_region"
    assert len(s6.root_facts) == 4  # all historical sources retained
    assert r.f_result is not None
    assert r.f_result.overlay is not None
    assert r.f_result.overlay.root_digest == sha256_hex(V2)


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_b_nonroot_version_change_same_root_graph(mode: AdmissionMode, endpoint: str) -> None:
    """B3: a nonroot-only version change on the SAME retained P/D
    state: the root body is unchanged, the graph stays under the same
    selected root digest, and the ACTUAL current F supplier/node/edge
    ownership moves to the newly granted version: A.md's OWN outgoing
    derivation withdraws and is re-owned by the new version (the
    supplying source owner), while the root-owned AGENTS.md->A.md
    edge stays stably owned by the root anchor and never inherits the
    target's witnesses."""
    ns, s2 = _mixed_region_state(mode, endpoint, f"r-b-nonroot-{endpoint}", a_text=A_OLD_TEXT)
    r2 = _r(s2, ns)
    _assert_ready_bindings(r2, s2, V2)
    assert r2.f_result is not None
    g2 = r2.f_result.overlay
    assert g2 is not None
    a1_digest = sha256_hex(A_OLD_TEXT)
    a2_digest = sha256_hex(A_NEW_TEXT)
    assert a2_digest != a1_digest
    # Before the change: A.md is owned by the ACTUAL first-granted
    # version (the version-owned path+digest identity); A's OWN
    # outgoing derivation is A-owned; the root->A edge is owned by
    # the root anchor with no inherited target witnesses.
    n2 = next(n for n in g2.nodes if n.path == "A.md")
    assert n2.status is CurrentGraphStatus.CURRENT_KNOWN
    assert n2.digest == a1_digest
    assert n2.owner == _owner_source("A.md", a1_digest)
    sup2 = next(
        s for s in g2.suppliers if s.kind is CurrentGraphSupplierKind.SOURCE and s.path == "A.md"
    )
    assert sup2.digest == a1_digest
    m1_occ = next(o for o in s2.d_state.occurrences if o.call_id == "m1")
    root_edge2 = next(e for e in g2.edges if e.source == ROOT_FILENAME and e.target == "A.md")
    assert root_edge2.owner == ROOT_OWNER
    assert root_edge2.witnesses == ()
    a_edge2 = next(e for e in g2.edges if e.source == "A.md" and e.target == "Old.md")
    assert a_edge2.owner == n2.owner
    assert a_edge2.witnesses == (m1_occ.occurrence_id,)
    assert (
        next(n for n in g2.nodes if n.path == "Old.md").status
        is CurrentGraphStatus.DISCOVERED_UNACQUIRED
    )
    # Genuinely issue the nonroot version change (the root is
    # unchanged).
    t3 = r_issue(s2, ns, "m2", endpoint, (m1_occ.occurrence_id,), MIX_CMD)
    assert t3.outcome.value == "accepted", t3.diagnostics
    t4 = r_observe(
        t3.state,
        ns,
        (read_request(endpoint, "m2", _mixed_body(A_NEW_TEXT, MARK, V2), MIX_CMD),),
    )
    assert t4.outcome.value == "accepted", t4.diagnostics
    s4 = t4.state
    r4 = _r(s4, ns)
    _assert_ready_bindings(r4, s4, V2)
    assert r4.f_result is not None
    g4 = r4.f_result.overlay
    assert g4 is not None
    assert g4.root_digest == g2.root_digest == sha256_hex(V2)
    # Ownership moves to the ACTUAL latest version: the node, its
    # source supplier and A's OWN outgoing derivation all bind the
    # new path+digest identity; the stale version's outgoing
    # derivation withdraws; the root-owned edge stays stable.
    n4 = next(n for n in g4.nodes if n.path == "A.md")
    assert n4.status is CurrentGraphStatus.CURRENT_KNOWN
    assert n4.digest == a2_digest
    assert n4.owner == _owner_source("A.md", a2_digest)
    assert n4.owner != n2.owner
    sup4 = next(
        s for s in g4.suppliers if s.kind is CurrentGraphSupplierKind.SOURCE and s.path == "A.md"
    )
    assert sup4.digest == a2_digest
    assert a1_digest not in {s.digest for s in g4.suppliers}
    m2_occ = next(o for o in s4.d_state.occurrences if o.call_id == "m2")
    root_edge4 = next(e for e in g4.edges if e.source == ROOT_FILENAME and e.target == "A.md")
    assert root_edge4.owner == ROOT_OWNER
    assert root_edge4.witnesses == ()
    assert not any(e.source == "A.md" and e.target == "Old.md" for e in g4.edges)
    a_edge4 = next(e for e in g4.edges if e.source == "A.md" and e.target == "New.md")
    assert a_edge4.owner == n4.owner
    assert a_edge4.witnesses == (m2_occ.occurrence_id,)
    # The stale version is never a current content; the new outgoing
    # target is only discovered (unacquired).
    assert "Old.md" not in {n.path for n in g4.nodes}
    assert (
        next(n for n in g4.nodes if n.path == "New.md").status
        is CurrentGraphStatus.DISCOVERED_UNACQUIRED
    )
    # The nested graph carries the ACTUAL accepted version tags of the
    # ACTUAL namespace (never caller constants).
    assert g4.graph_version == ns.graph_version
    assert g4.reference_version == ns.reference_version
    assert g4.proof_version == ns.proof_version


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_b_nested_version_tags_closed(mode: AdmissionMode, endpoint: str) -> None:
    """B4: the READY result's nested F/E evidence carries the ACTUAL
    fixed accepted version tags (closed constants, never caller
    supplied)."""
    ns, s2 = _mixed_region_state(mode, endpoint, f"r-b-tags-{endpoint}")
    r = _r(s2, ns)
    assert r.outcome is RootRegionGraphOutcome.READY
    assert r.contract_version == ROOT_REGION_GRAPH_CONTRACT_VERSION
    assert r.policy_version == ROOT_REGION_GRAPH_POLICY_VERSION
    assert r.f_result is not None
    overlay = r.f_result.overlay
    assert overlay is not None
    assert overlay.contract_version == CURRENT_GRAPH_CONTRACT_VERSION
    assert overlay.policy_version == CURRENT_GRAPH_POLICY_VERSION
    assert overlay.currentness_contract_version == CURRENTNESS_CONTRACT_VERSION
    assert overlay.currentness_policy_version == CURRENTNESS_POLICY_VERSION
    assert r.e_overlay is not None
    assert r.e_overlay.policy_version == CURRENTNESS_POLICY_VERSION


# B5 multi-source fixture: a fresh root referencing A.md and X.md,
# with a genuine two-node cycle (Cycle1<->Cycle2) hanging off A.md
# and a shared Target.md (the ordinary OR/cycle guide).
V1_ROOT = "Follow `A.md` and `X.md`.\n"
V2_ROOT = "Follow `X.md`.\n"
A_MD_TEXT = "Follow `Cycle1.md` and `Target.md`.\n"
X_MD_OLD = "Follow `Target.md`.\n"
X_MD_NEW = "Follow `Replacement.md`.\n"
CYCLE1_TEXT = "Follow `Cycle2.md`.\n"
CYCLE2_TEXT = "Follow `Cycle1.md`.\n"
TARGET_TEXT = "Synthetic target governance.\n"
REGION_PREFIX = "Synthetic region nonroot.\n"
MULTI_CMD = f"cat Note.md && echo '{MARK}' && cat AGENTS.md"


def _multi_source_state(
    mode: AdmissionMode, endpoint: str, lineage: str
) -> tuple[Any, Any, dict[str, Any]]:
    """The earned public-P multi-source fixture: every read is a
    genuine issued+anchored whole read under the anchor frontier."""
    ns, s0 = r_bootstrap(mode, lineage, root_body=V1_ROOT)
    state = s0
    original: dict[str, Any] = {}
    for cid, path, body in (
        ("a", "A.md", A_MD_TEXT),
        ("x", "X.md", X_MD_OLD),
        ("c1", "Cycle1.md", CYCLE1_TEXT),
        ("c2", "Cycle2.md", CYCLE2_TEXT),
        ("t", "Target.md", TARGET_TEXT),
    ):
        issued = r_issue(state, ns, cid, endpoint, (CAUSAL_ROOT_FACT,), f"cat {path}")
        assert issued.outcome.value == "accepted", issued.diagnostics
        obs = r_observe(issued.state, ns, (read_request(endpoint, cid, body, f"cat {path}"),))
        assert obs.outcome.value == "accepted", obs.diagnostics
        state = obs.state
        original[cid] = next(o for o in state.d_state.occurrences if o.call_id == cid)
    return ns, state, original


def _nodes(g: Any) -> dict[str, Any]:
    return {n.path: n for n in g.nodes}


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_b_multi_source_withdrawal_alternate_cycle_revert(
    mode: AdmissionMode, endpoint: str
) -> None:
    """B5: version-owned withdrawal, the surviving alternate, the
    genuine two-node cycle and the deliberate old-bytes revert under
    the SELECTED root: withdrawing the A.md branch withdraws its
    cycle while the surviving X.md alternate keeps Target.md; a
    genuine nonroot X.md version change withdraws Target.md and moves
    the ACTUAL supplier ownership to Replacement.md; a genuine
    old-bytes region revert restores the cycle with every original
    observation retained by identity (retained unreachable paths are
    possession, never erasure)."""
    ns, s1, original = _multi_source_state(mode, endpoint, f"r-b-multi-{endpoint}")
    r1 = _r(s1, ns)
    _assert_ready_bindings(r1, s1, V1_ROOT)
    assert r1.f_result is not None
    n1 = _nodes(r1.f_result.overlay)
    assert n1["A.md"].depth == 1 and n1["X.md"].depth == 1
    assert n1["Target.md"].depth == 2
    assert n1["Cycle1.md"].depth == 2 and n1["Cycle2.md"].depth == 3
    assert r1.f_result.overlay is not None
    assert r1.f_result.overlay.unreachable_current_paths == ()
    # Phase 2: a genuinely NEW region root (v2) drops the A.md branch:
    # the cycle and A.md withdraw as retained unreachable possession
    # while the surviving X.md alternate keeps Target.md at depth 2.
    issued = r_issue(s1, ns, "root2", endpoint, (CAUSAL_ROOT_FACT,), MULTI_CMD)
    assert issued.outcome.value == "accepted"
    obs = r_observe(
        issued.state,
        ns,
        (read_request(endpoint, "root2", _mixed_body(REGION_PREFIX, MARK, V2_ROOT), MULTI_CMD),),
    )
    assert obs.outcome.value == "accepted", obs.diagnostics
    s2 = obs.state
    root2 = next(o for o in s2.d_state.occurrences if o.call_id == "root2")
    r2 = _r(s2, ns)
    _assert_ready_bindings(r2, s2, V2_ROOT)
    assert r2.resolved_source is not None
    assert r2.resolved_source.occurrence is not None
    assert r2.resolved_source.proof is not None
    assert r2.resolved_source.kind == "read_region"
    assert r2.resolved_source.occurrence is root2
    assert r2.resolved_source.proof is root2.proof
    assert r2.f_result is not None
    assert r2.f_result.overlay is not None
    n2 = _nodes(r2.f_result.overlay)
    for gone in ("A.md", "Cycle1.md", "Cycle2.md"):
        assert gone not in n2
    assert {
        "A.md",
        "Cycle1.md",
        "Cycle2.md",
        "Note.md",
    } <= set(r2.f_result.overlay.unreachable_current_paths)
    assert n2["Target.md"].depth == 2  # surviving alternate via X.md
    # Phase 3: a genuine nonroot version change of X.md (a child of
    # the original X read AND the v2 root) withdraws Target.md and
    # grants Replacement.md: the ACTUAL supplier ownership moves to
    # the new X.md digest.
    x_old = original["x"]
    issued = r_issue(
        s2, ns, "xnew", endpoint, (x_old.occurrence_id, root2.occurrence_id), "cat X.md"
    )
    assert issued.outcome.value == "accepted", issued.diagnostics
    obs = r_observe(issued.state, ns, (read_request(endpoint, "xnew", X_MD_NEW, "cat X.md"),))
    assert obs.outcome.value == "accepted", obs.diagnostics
    s3 = obs.state
    x_new = next(o for o in s3.d_state.occurrences if o.call_id == "xnew")
    r3 = _r(s3, ns)
    _assert_ready_bindings(r3, s3, V2_ROOT)
    assert r3.f_result is not None
    n3 = _nodes(r3.f_result.overlay)
    assert "Target.md" not in n3
    assert r3.f_result.overlay is not None
    assert "Target.md" in r3.f_result.overlay.unreachable_current_paths
    assert n3["Replacement.md"].depth == 2
    x_digest = sha256_hex(X_MD_NEW)
    assert any(
        s.kind is CurrentGraphSupplierKind.SOURCE and s.path == "X.md" and s.digest == x_digest
        for s in r3.f_result.overlay.suppliers
    )
    # Phase 4: a genuine old-bytes region REVERT (child of the X.md
    # change) restores the v1 root: the cycle and Target.md come
    # back at their least derivation depths and the retained alternate
    # (Replacement.md) stays reachable under the new X.md.
    issued = r_issue(s3, ns, "revert", endpoint, (x_new.occurrence_id,), MULTI_CMD)
    assert issued.outcome.value == "accepted", issued.diagnostics
    obs = r_observe(
        issued.state,
        ns,
        (read_request(endpoint, "revert", _mixed_body(REGION_PREFIX, MARK, V1_ROOT), MULTI_CMD),),
    )
    assert obs.outcome.value == "accepted", obs.diagnostics
    s4 = obs.state
    revert_occ = next(o for o in s4.d_state.occurrences if o.call_id == "revert")
    r4 = _r(s4, ns)
    _assert_ready_bindings(r4, s4, V1_ROOT)
    assert r4.resolved_source is not None
    assert r4.resolved_source.occurrence is not None
    assert r4.resolved_source.proof is not None
    assert r4.resolved_source.occurrence is revert_occ
    assert r4.resolved_source.proof is revert_occ.proof
    assert r4.f_result is not None
    n4 = _nodes(r4.f_result.overlay)
    assert n4["Target.md"].depth == 2
    assert n4["Cycle1.md"].depth == 2 and n4["Cycle2.md"].depth == 3
    assert n4["Replacement.md"].depth == 2
    # Only the never-referenced Note.md stays current-unreachable.
    assert r4.f_result.overlay is not None
    assert r4.f_result.overlay.unreachable_current_paths == ("Note.md",)
    # The stable R scope key carries the ACTUAL advancing revision.
    assert r1.scope_key == r2.scope_key == r3.scope_key == r4.scope_key
    assert r1.revision < r2.revision < r3.revision < r4.revision
    # Every original observation is retained by identity (never
    # erased by a withdrawal).
    for old in original.values():
        assert any(o is old for o in s4.d_state.occurrences)


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_b_opaque_and_certificate_law(mode: AdmissionMode, endpoint: str) -> None:
    """B6: the READY overlay carries the ACTUAL opaque-group AND
    certificate law: a group certificate is usable only when EVERY
    possible nonroot member is independently current AND reachable
    in the joint fixed point (and shares the same canonical lexical
    directory); an unusable certificate is retained with its closed
    reasons and NEVER joins its target (an off-graph member never
    silently governs)."""
    # Usable AND certificate: the boundaryless (A.md, B.md) group
    # references C.md; both members are independently reachable
    # through the root; the certificate depth is 1 + MAX over ALL
    # members while the target's least depth takes the MIN over
    # alternatives (the ordinary route wins).
    root_body = "Read `Start.md` and `S.md` first."
    ns, s0 = r_bootstrap(mode, f"r-b-and-{endpoint}", root_body=root_body)
    t1 = r_issue(s0, ns, "c-start", endpoint, (CAUSAL_ROOT_FACT,), "cat Start.md")
    assert t1.outcome.value == "accepted"
    t2 = r_observe(
        t1.state,
        ns,
        (read_request(endpoint, "c-start", "Read `A.md` and `B.md` and `C.md`.", "cat Start.md"),),
    )
    assert t2.outcome.value == "accepted", t2.diagnostics
    t3 = r_issue(t2.state, ns, "c-ab", endpoint, (CAUSAL_ROOT_FACT,), "cat A.md B.md")
    assert t3.outcome.value == "accepted"
    t4 = r_observe(
        t3.state, ns, (read_request(endpoint, "c-ab", "See `C.md` here.\n", "cat A.md B.md"),)
    )
    assert t4.outcome.value == "accepted", t4.diagnostics
    s4 = t4.state
    r = _r(s4, ns)
    _assert_ready_bindings(r, s4, root_body)
    assert r.f_result is not None
    g = r.f_result.overlay
    assert g is not None
    cert = next(c for c in g.certificates if c.members == ("A.md", "B.md"))
    assert cert.usable is True and cert.reasons == ()
    assert cert.possible_origins == ("A.md", "B.md")
    assert cert.suppliers == ("A.md", "B.md")
    assert cert.resolved_target == "C.md"
    assert cert.depth == 3  # 1 + max(depth A, depth B)
    n = _nodes(g)
    assert n["C.md"].depth == 2  # the ordinary root->Start->C route wins
    assert n["A.md"].status is CurrentGraphStatus.DISCOVERED_UNACQUIRED
    assert n["B.md"].status is CurrentGraphStatus.DISCOVERED_UNACQUIRED
    # NO_COMMON_DIRECTORY: x/A.md and y/B.md never share the SAME
    # canonical lexical directory (convergent references never
    # compensate): the target is never joined.
    nd_root = "Read `x/A.md` and `y/B.md` first."
    ns2, s0 = r_bootstrap(mode, f"r-b-nd-{endpoint}", root_body=nd_root)
    t1 = r_issue(s0, ns2, "c-xy", endpoint, (CAUSAL_ROOT_FACT,), "cat x/A.md y/B.md")
    assert t1.outcome.value == "accepted"
    t2 = r_observe(
        t1.state,
        ns2,
        (read_request(endpoint, "c-xy", "See `z/C.md` here.\n", "cat x/A.md y/B.md"),),
    )
    assert t2.outcome.value == "accepted", t2.diagnostics
    s2 = t2.state
    r2 = _r(s2, ns2)
    _assert_ready_bindings(r2, s2, nd_root)
    assert r2.f_result is not None
    g2 = r2.f_result.overlay
    assert g2 is not None
    cert2 = next(c for c in g2.certificates if c.members == ("x/A.md", "y/B.md"))
    assert cert2.usable is False
    assert cert2.reasons == (CurrentGraphReason.NO_COMMON_DIRECTORY,)
    assert cert2.possible_origins == ("x/A.md", "y/B.md")
    assert cert2.suppliers == ("x/A.md", "y/B.md")
    assert cert2.resolved_target is None and cert2.depth is None
    assert "z/C.md" not in _nodes(g2)
    # NOT_INDEPENDENTLY_REACHABLE: a group member that is
    # independently off-graph (referenced by no current derivation)
    # can never be certified, even while its sibling is reachable.
    ng_root = "Read `A.md` first."
    ns3, s0 = r_bootstrap(mode, f"r-b-ng-{endpoint}", root_body=ng_root)
    t1 = r_issue(s0, ns3, "c-b", endpoint, (CAUSAL_ROOT_FACT,), "cat B.md")
    assert t1.outcome.value == "accepted"
    t2 = r_observe(t1.state, ns3, (read_request(endpoint, "c-b", "See `G.md`.\n", "cat B.md"),))
    assert t2.outcome.value == "accepted", t2.diagnostics
    t3 = r_issue(t2.state, ns3, "c-ad", endpoint, (CAUSAL_ROOT_FACT,), "cat A.md D.md")
    assert t3.outcome.value == "accepted"
    t4 = r_observe(
        t3.state, ns3, (read_request(endpoint, "c-ad", "See `H.md`.\n", "cat A.md D.md"),)
    )
    assert t4.outcome.value == "accepted", t4.diagnostics
    s3 = t4.state
    r3 = _r(s3, ns3)
    _assert_ready_bindings(r3, s3, ng_root)
    assert r3.f_result is not None
    g3 = r3.f_result.overlay
    assert g3 is not None
    cert3 = next(c for c in g3.certificates if c.members == ("A.md", "D.md"))
    assert cert3.usable is False
    assert CurrentGraphReason.NOT_INDEPENDENTLY_REACHABLE in cert3.reasons
    assert cert3.resolved_target == "H.md"
    assert "H.md" not in _nodes(g3)
    assert "D.md" not in _nodes(g3)
    assert g3.unreachable_current_paths == ("B.md",)
    assert all(c.usable is False for c in g3.certificates)


# B6b selected-root-owned certificate withdrawal/alternate fixture.
P1_V1_ROOT = "Read `Start.md` and `A.md` first."
P1_V2_ROOT = "Read `Start.md` first."
P2_V1_ROOT = "Read `A.md` and `B.md` first."
P2_V2_ROOT = "Read `A.md` first."
START_TEXT = "See `B.md` and `C.md`.\n"
AB_GROUP_TEXT = "See `C.md` here.\n"
WD_PREFIX = "Synthetic withdrawal nonroot.\n"
WD_CMD = f"cat WDnote.md && echo '{MARK}' && cat AGENTS.md"


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_b_opaque_certificate_withdrawal_and_alternate(mode: AdmissionMode, endpoint: str) -> None:
    """B6b: selected-root-owned opaque certificate
    withdrawal/restoration: a genuine MIXED-only root v2 that drops
    one possible group supplier makes the retained original
    certificate unusable (NOT_INDEPENDENTLY_REACHABLE) -- its target
    stays via the surviving ordinary alternate (the MIN law) when
    one exists and is withdrawn only when none does -- and a
    genuine old-bytes region descendant restores usability/target
    with the SAME original group/proof references.  Part 1 uses
    genuinely different supplier depths (A depth 1 direct, B depth 2
    via Start) so the certificate depth proves the 1 + MAX
    recomputation against the alternate MIN."""
    # Part 1: a surviving ordinary Start->C alternate keeps the
    # target while the certificate withdraws.
    ns, s0 = r_bootstrap(mode, f"r-b-wd1-{endpoint}", root_body=P1_V1_ROOT)
    t1 = r_issue(s0, ns, "c-start", endpoint, (CAUSAL_ROOT_FACT,), "cat Start.md")
    assert t1.outcome.value == "accepted"
    t2 = r_observe(t1.state, ns, (read_request(endpoint, "c-start", START_TEXT, "cat Start.md"),))
    assert t2.outcome.value == "accepted", t2.diagnostics
    t3 = r_issue(t2.state, ns, "c-ab", endpoint, (CAUSAL_ROOT_FACT,), "cat A.md B.md")
    assert t3.outcome.value == "accepted"
    t4 = r_observe(t3.state, ns, (read_request(endpoint, "c-ab", AB_GROUP_TEXT, "cat A.md B.md"),))
    assert t4.outcome.value == "accepted", t4.diagnostics
    s1 = t4.state
    ab_occ = next(o for o in s1.d_state.occurrences if o.call_id == "c-ab")
    r1 = _r(s1, ns)
    _assert_ready_bindings(r1, s1, P1_V1_ROOT)
    assert r1.f_result is not None
    g1 = r1.f_result.overlay
    assert g1 is not None
    n1 = _nodes(g1)
    assert n1["A.md"].depth == 1 and n1["B.md"].depth == 2
    assert n1["C.md"].depth == 2  # the ordinary Start->C route (MIN)
    cert1 = next(c for c in g1.certificates if c.members == ("A.md", "B.md"))
    assert cert1.usable is True and cert1.reasons == ()
    assert cert1.resolved_target == "C.md"
    assert cert1.depth == 3  # 1 + MAX(depth A=1, depth B=2)
    assert cert1.witnesses == (ab_occ.occurrence_id,)
    grp1 = next(s for s in g1.suppliers if s.kind is CurrentGraphSupplierKind.GROUP)
    assert grp1.members == ("A.md", "B.md")
    assert grp1.witnesses == (ab_occ.occurrence_id,)
    assert g1.unreachable_current_paths == ()
    # The mixed-only v2 root drops A.md (a possible group supplier):
    # the retained original certificate becomes unusable, but the
    # surviving ordinary Start->C alternate keeps the target.
    t5 = r_issue(s1, ns, "root2", endpoint, (CAUSAL_ROOT_FACT,), WD_CMD)
    assert t5.outcome.value == "accepted"
    s2 = r_observe(
        t5.state,
        ns,
        (read_request(endpoint, "root2", _mixed_body(WD_PREFIX, MARK, P1_V2_ROOT), WD_CMD),),
    ).state
    root2 = next(o for o in s2.d_state.occurrences if o.call_id == "root2")
    r2 = _r(s2, ns)
    _assert_ready_bindings(r2, s2, P1_V2_ROOT)
    assert r2.f_result is not None
    g2 = r2.f_result.overlay
    assert g2 is not None
    n2 = _nodes(g2)
    assert "A.md" not in n2
    assert n2["B.md"].depth == 2
    cert2 = next(c for c in g2.certificates if c.members == ("A.md", "B.md"))
    assert cert2.usable is False
    assert CurrentGraphReason.NOT_INDEPENDENTLY_REACHABLE in cert2.reasons
    assert cert2.resolved_target == "C.md"  # retained unresolved evidence
    assert cert2.depth is None
    assert n2["C.md"].depth == 2  # the surviving ordinary alternate
    assert any(e.source == "Start.md" and e.target == "C.md" for e in g2.edges)
    assert g2.unreachable_current_paths == ("WDnote.md",)
    # The SAME original group/proof references are retained.
    grp2 = next(s for s in g2.suppliers if s.kind is CurrentGraphSupplierKind.GROUP)
    assert grp2.identity == grp1.identity
    assert grp2.group_digest == grp1.group_digest
    assert grp2.witnesses == (ab_occ.occurrence_id,)
    assert cert2.witnesses == cert1.witnesses
    # The genuine old-bytes region revert restores the v1 root: the
    # original certificate is usable again at the recomputed depth.
    t6 = r_issue(s2, ns, "revert", endpoint, (root2.occurrence_id,), WD_CMD)
    assert t6.outcome.value == "accepted"
    s3 = r_observe(
        t6.state,
        ns,
        (read_request(endpoint, "revert", _mixed_body(WD_PREFIX, MARK, P1_V1_ROOT), WD_CMD),),
    ).state
    revert_occ = next(o for o in s3.d_state.occurrences if o.call_id == "revert")
    r3 = _r(s3, ns)
    _assert_ready_bindings(r3, s3, P1_V1_ROOT)
    assert r3.resolved_source is not None
    assert r3.resolved_source.occurrence is not None
    assert r3.resolved_source.occurrence is revert_occ
    assert r3.f_result is not None
    g3 = r3.f_result.overlay
    assert g3 is not None
    n3 = _nodes(g3)
    assert n3["A.md"].depth == 1
    cert3 = next(c for c in g3.certificates if c.members == ("A.md", "B.md"))
    assert cert3.usable is True and cert3.reasons == ()
    assert cert3.resolved_target == "C.md"
    assert cert3.depth == 3
    assert n3["C.md"].depth == 2
    grp3 = next(s for s in g3.suppliers if s.kind is CurrentGraphSupplierKind.GROUP)
    assert grp3.identity == grp1.identity
    assert grp3.group_digest == grp1.group_digest
    assert grp3.witnesses == (ab_occ.occurrence_id,)
    assert g3.unreachable_current_paths == ("WDnote.md",)
    # Part 2: the SAME root-owned withdrawal with NO surviving
    # ordinary alternate: the target is withdrawn with the unusable
    # certificate and restored by the genuine old-bytes revert.
    ns_b, s0 = r_bootstrap(mode, f"r-b-wd2-{endpoint}", root_body=P2_V1_ROOT)
    t1 = r_issue(s0, ns_b, "c-ab", endpoint, (CAUSAL_ROOT_FACT,), "cat A.md B.md")
    assert t1.outcome.value == "accepted"
    t2 = r_observe(
        t1.state, ns_b, (read_request(endpoint, "c-ab", AB_GROUP_TEXT, "cat A.md B.md"),)
    )
    assert t2.outcome.value == "accepted", t2.diagnostics
    sb1 = t2.state
    rb1 = _r(sb1, ns_b)
    _assert_ready_bindings(rb1, sb1, P2_V1_ROOT)
    assert rb1.f_result is not None
    gb1 = rb1.f_result.overlay
    assert gb1 is not None
    nb1 = _nodes(gb1)
    assert nb1["A.md"].depth == 1 and nb1["B.md"].depth == 1
    cb1 = next(c for c in gb1.certificates if c.members == ("A.md", "B.md"))
    assert cb1.usable is True and cb1.reasons == ()
    assert cb1.resolved_target == "C.md" and cb1.depth == 2
    assert nb1["C.md"].depth == 2
    t3 = r_issue(sb1, ns_b, "root2", endpoint, (CAUSAL_ROOT_FACT,), WD_CMD)
    assert t3.outcome.value == "accepted"
    sb2 = r_observe(
        t3.state,
        ns_b,
        (read_request(endpoint, "root2", _mixed_body(WD_PREFIX, MARK, P2_V2_ROOT), WD_CMD),),
    ).state
    root2b = next(o for o in sb2.d_state.occurrences if o.call_id == "root2")
    rb2 = _r(sb2, ns_b)
    _assert_ready_bindings(rb2, sb2, P2_V2_ROOT)
    assert rb2.f_result is not None
    gb2 = rb2.f_result.overlay
    assert gb2 is not None
    nb2 = _nodes(gb2)
    assert "B.md" not in nb2
    cb2 = next(c for c in gb2.certificates if c.members == ("A.md", "B.md"))
    assert cb2.usable is False
    assert CurrentGraphReason.NOT_INDEPENDENTLY_REACHABLE in cb2.reasons
    assert "C.md" not in nb2  # withdrawn: no surviving independent alternate
    assert gb2.unreachable_current_paths == ("WDnote.md",)
    t4 = r_issue(sb2, ns_b, "revert", endpoint, (root2b.occurrence_id,), WD_CMD)
    assert t4.outcome.value == "accepted"
    sb3 = r_observe(
        t4.state,
        ns_b,
        (read_request(endpoint, "revert", _mixed_body(WD_PREFIX, MARK, P2_V1_ROOT), WD_CMD),),
    ).state
    rb3 = _r(sb3, ns_b)
    _assert_ready_bindings(rb3, sb3, P2_V1_ROOT)
    assert rb3.f_result is not None
    gb3 = rb3.f_result.overlay
    assert gb3 is not None
    cb3 = next(c for c in gb3.certificates if c.members == ("A.md", "B.md"))
    assert cb3.usable is True and cb3.reasons == ()
    assert cb3.resolved_target == "C.md" and cb3.depth == 2
    assert _nodes(gb3)["C.md"].depth == 2


def _depth3_state(
    mode: AdmissionMode, endpoint: str, lineage: str, max_depth: int
) -> tuple[Any, Any]:
    """The earned public-P depth-3 chain (root -> S1 -> S2 -> S3)
    under a GENUINELY strict GraphBounds copy from the ACTUAL
    admission factory (a valid stricter copy, never a model_copy
    bypass)."""
    ns, s0 = r_bootstrap(
        mode,
        lineage,
        root_body="Read `S1.md` first.",
        graph_bounds=GraphBounds(max_depth=max_depth),
    )
    t1 = r_issue(s0, ns, "c-s1", endpoint, (CAUSAL_ROOT_FACT,), "cat S1.md")
    assert t1.outcome.value == "accepted"
    t2 = r_observe(t1.state, ns, (read_request(endpoint, "c-s1", "See `S2.md`.", "cat S1.md"),))
    assert t2.outcome.value == "accepted", t2.diagnostics
    s1_occ = next(o for o in t2.state.d_state.occurrences if o.call_id == "c-s1")
    t3 = r_issue(
        t2.state, ns, "c-s2", endpoint, (s1_occ.occurrence_id, CAUSAL_ROOT_FACT), "cat S2.md"
    )
    assert t3.outcome.value == "accepted", t3.diagnostics
    t4 = r_observe(t3.state, ns, (read_request(endpoint, "c-s2", "See `S3.md`.", "cat S2.md"),))
    assert t4.outcome.value == "accepted", t4.diagnostics
    return ns, t4.state


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_b_strict_max_depth_enforced_after_fixed_point(mode: AdmissionMode, endpoint: str) -> None:
    """B7: the strict GraphBounds.max_depth is enforced AFTER the
    joint fixed point over the ACTUAL selected-root graph: the
    genuine depth-3 chain under the strict max_depth=2 copy refuses
    with the exact graph-stage limitation, the R REFUSED retains the
    ACTUAL returned F evidence (no partial source, no R diagnostics),
    and the SAME fixture under the genuine max_depth=3 copy derives
    READY with S3.md at depth 3."""
    ns2, s2 = _depth3_state(mode, endpoint, f"r-b-d2-{endpoint}", 2)
    r2 = _r(s2, ns2)
    assert r2.outcome is RootRegionGraphOutcome.REFUSED
    assert r2.diagnostics == ()
    assert r2.resolved_source is None
    assert r2.e_overlay is None
    assert r2.f_result is not None
    assert r2.f_result.outcome is CurrentGraphOutcome.REFUSED_OVER_BOUND
    assert r2.f_result.diagnostics == (CurrentGraphLimitation.GRAPH_DEPTH_OVER_BOUND,)
    assert r2.q_result is not None
    assert r2.q_result.outcome is RootRegionCurrentnessOutcome.READY
    ns3, s3 = _depth3_state(mode, endpoint, f"r-b-d3-{endpoint}", 3)
    r3 = _r(s3, ns3)
    _assert_ready_bindings(r3, s3, "Read `S1.md` first.")
    assert r3.f_result is not None
    assert _nodes(r3.f_result.overlay)["S3.md"].depth == 3


# --- C. ACTUAL same-run Q mapping through the R result ------------------


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_c_joint_frontier_unproven_no_source(mode: AdmissionMode, endpoint: str) -> None:
    """C1: two unresolved incomparable opaque root branches (the
    ACTUAL same-run Q unproven) map to the R OWN outcome: the actual
    Q result is retained by reference, NO source is published, F
    NEVER runs, and no R diagnostics are invented."""
    ns, state, _v2 = _frontier_state(mode, endpoint, f"r-c-unp-{endpoint}")
    r = _r(state, ns)
    assert r.outcome is RootRegionGraphOutcome.ROOT_CURRENTNESS_UNPROVEN
    assert r.diagnostics == ()
    assert r.resolved_source is None
    assert r.f_result is None
    assert r.e_overlay is None
    q = r.q_result
    assert q is not None
    assert q.outcome is RootRegionCurrentnessOutcome.ROOT_CURRENTNESS_UNPROVEN
    assert q.state is state
    assert q.usable_selected_source_digest is None
    ua, ub = q_occ(state, "ua"), q_occ(state, "ub")
    assert {w.occurrence_id for w in q.uncertainty_witnesses} == {
        ua.occurrence_id,
        ub.occurrence_id,
    }
    # Every root fact (anchor + the three region witnesses) is
    # retained: uncertainty is interpretation, never erasure.
    # The anchor envelope fact and the proven v2 region fact are the
    # ONLY root facts: the two opaque boundaryless branches admit no
    # per-file root member, so no root fact is minted for them --
    # their retained evidence is the anchored occurrences themselves
    # (uncertainty is interpretation, never erasure).
    assert len(state.root_facts) == 2
    assert [f.provenance.kind for f in state.root_facts] == ["envelope", "read_region"]
    assert all(f.authority for f in state.root_facts)


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_c_child_of_one_stays_unproven(mode: AdmissionMode, endpoint: str) -> None:
    """C2: a known witness descending from ONLY one opaque branch
    leaves the other maximal: the R result stays unproven with the
    ACTUAL same-run Q evidence retained (including the actual OK P
    selection of the known bytes) and no source or F work."""
    ns, state, _v2 = _frontier_state(mode, endpoint, f"r-c-c1-{endpoint}")
    ua, ub = q_occ(state, "ua"), q_occ(state, "ub")
    state = q_observe(
        q_issue(state, ns, "va", endpoint, Q_MIX_CMD, (ua.occurrence_id,)),
        ns,
        endpoint,
        "va",
        q_mixed_body(Q_A_TEXT, Q_MARK, "R4."),
        Q_MIX_CMD,
    )
    r = _r(state, ns)
    assert r.outcome is RootRegionGraphOutcome.ROOT_CURRENTNESS_UNPROVEN
    assert r.diagnostics == ()
    assert r.resolved_source is None
    assert r.f_result is None
    assert r.e_overlay is None
    q = r.q_result
    assert q is not None
    assert q.outcome is RootRegionCurrentnessOutcome.ROOT_CURRENTNESS_UNPROVEN
    assert q.usable_selected_source_digest is None
    assert q.p_selection is not None
    assert q.p_selection.outcome is RootSelectionOutcome.OK
    assert q.p_selection.selected_source_digest == sha256_hex("R4.")
    assert {w.occurrence_id for w in q.uncertainty_witnesses} == {
        ua.occurrence_id,
        ub.occurrence_id,
    }


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_c_joint_coverage_ready_with_dominated_witnesses(
    mode: AdmissionMode, endpoint: str
) -> None:
    """C3: compatible equal-byte known maxima JOINTLY covering the
    branches restore the R READY outcome without inventing Va<->Vb
    edges: both dominated original witnesses stay retained on the
    actual Q result and the actual P selection, the selected root is
    the equal 'R4.' bytes and the ACTUAL F/E graph runs under it."""
    ns, state, _v2 = _frontier_state(mode, endpoint, f"r-c-jnt-{endpoint}")
    ua, ub = q_occ(state, "ua"), q_occ(state, "ub")
    state = q_observe(
        q_issue(state, ns, "va", endpoint, Q_MIX_CMD, (ua.occurrence_id,)),
        ns,
        endpoint,
        "va",
        q_mixed_body(Q_A_TEXT, Q_MARK, "R4."),
        Q_MIX_CMD,
    )
    va = q_occ(state, "va")
    state = q_observe(
        q_issue(state, ns, "vb", endpoint, Q_MIX_CMD, (ub.occurrence_id,)),
        ns,
        endpoint,
        "vb",
        q_mixed_body(Q_A_TEXT, Q_MARK, "R4."),
        Q_MIX_CMD,
    )
    vb = q_occ(state, "vb")
    edges = {(link.child, link.parent) for link in state.d_state.parent_links}
    assert (vb.occurrence_id, va.occurrence_id) not in edges
    assert (va.occurrence_id, vb.occurrence_id) not in edges
    r = _r(state, ns)
    _assert_ready_bindings(r, state, "R4.")
    assert r.resolved_source is not None
    assert r.resolved_source.kind == "read_region"
    q = r.q_result
    assert q is not None
    assert q.outcome is RootRegionCurrentnessOutcome.READY
    assert q.usable_selected_source_digest == sha256_hex("R4.")
    assert len(q.uncertainty_witnesses) == 2
    assert {w.occurrence_id for w in q.uncertainty_witnesses} == {
        ua.occurrence_id,
        ub.occurrence_id,
    }
    assert q.p_selection is not None
    assert len(q.p_selection.witness_facts) == 2


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_c_dominated_opaque_restores_ready(mode: AdmissionMode, endpoint: str) -> None:
    """C4: an uncertainty branch strictly dominated by a genuinely
    later supported authoritative root witness returns the R READY
    outcome: the dominated opaque witness stays retained by identity
    on the actual Q result and the selected root is the supported
    'R3.' bytes."""
    ns, state = q_bootstrap(mode, f"r-c-dom-{endpoint}")
    state = q_observe(
        q_issue(state, ns, "v2", endpoint, Q_MIX_CMD, (CAUSAL_ROOT_FACT,)),
        ns,
        endpoint,
        "v2",
        q_mixed_body(Q_A_TEXT, Q_MARK, "R2."),
        Q_MIX_CMD,
    )
    v2 = q_occ(state, "v2")
    state = q_observe(
        q_issue(state, ns, "u1", endpoint, BOUNDARYLESS_CMD, (v2.occurrence_id,)),
        ns,
        endpoint,
        "u1",
        OPAQUE_BODY,
        BOUNDARYLESS_CMD,
    )
    r_u1 = _r(state, ns)
    assert r_u1.outcome is RootRegionGraphOutcome.ROOT_CURRENTNESS_UNPROVEN
    assert r_u1.f_result is None and r_u1.resolved_source is None
    u1 = q_occ(state, "u1")
    state = q_observe(
        q_issue(state, ns, "v3", endpoint, Q_MIX_CMD, (u1.occurrence_id,)),
        ns,
        endpoint,
        "v3",
        q_mixed_body(Q_A_TEXT, Q_MARK, "R3."),
        Q_MIX_CMD,
    )
    r3 = _r(state, ns)
    _assert_ready_bindings(r3, state, "R3.")
    q = r3.q_result
    assert q is not None
    assert q.outcome is RootRegionCurrentnessOutcome.READY
    assert q.usable_selected_source_digest == sha256_hex("R3.")
    # The dominated witness stays retained (no evidence erased).
    assert len(q.uncertainty_witnesses) == 1
    assert q.uncertainty_witnesses[0].occurrence is u1


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_c_actual_authority_conflict_maps(mode: AdmissionMode, endpoint: str) -> None:
    """C5: two genuinely incomparable DIFFERING region roots map the
    ACTUAL same-run Q authority conflict to the R OWN outcome: the
    actual P ROOT_CONTENT_CONFLICT selection is retained (no usable
    source, no selected digest), NO source is published, F NEVER
    runs, no R diagnostics are invented, and both conflicting root
    facts stay retained."""
    ns, s4, f_m1, f_m2 = _two_sibling_regions(mode, f"r-c-cfl-{endpoint}", endpoint)
    r = _r(s4, ns)
    assert r.outcome is RootRegionGraphOutcome.ROOT_AUTHORITY_CONFLICT
    assert r.diagnostics == ()
    assert r.resolved_source is None
    assert r.f_result is None
    assert r.e_overlay is None
    q = r.q_result
    assert q is not None
    assert q.outcome is RootRegionCurrentnessOutcome.ROOT_AUTHORITY_CONFLICT
    assert q.state is s4
    assert q.usable_selected_source_digest is None
    assert q.p_selection is not None
    assert q.p_selection.outcome is RootSelectionOutcome.ROOT_CONTENT_CONFLICT
    assert q.p_selection.selected_source_digest is None
    assert len(q.p_selection.witness_facts) >= 2
    assert f_m1 in s4.root_facts and f_m2 in s4.root_facts


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_c_nonroot_only_opaque_ready(mode: AdmissionMode, endpoint: str) -> None:
    """C6: a complete NONROOT-only opaque group never becomes root
    uncertainty: the anchor stays known and the R derivation is
    READY under the envelope root with no uncertainty witnesses and
    no new root fact minted."""
    ns, state = q_bootstrap(mode, f"r-c-nr-{endpoint}")
    state = q_observe(
        q_issue(state, ns, "nr", endpoint, NONROOT_CMD, (CAUSAL_ROOT_FACT,)),
        ns,
        endpoint,
        "nr",
        Q_A_TEXT + Q_B_TEXT,
        NONROOT_CMD,
    )
    assert not any(f.provenance.kind != "envelope" for f in state.root_facts)
    r = _r(state, ns)
    _assert_ready_bindings(r, state, "Initial root.")
    assert r.resolved_source is not None
    assert r.resolved_source.kind == "envelope"
    q = r.q_result
    assert q is not None
    assert q.outcome is RootRegionCurrentnessOutcome.READY
    assert q.usable_selected_source_digest == sha256_hex("Initial root.")
    assert not q.uncertainty_witnesses


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_c_delayed_result_no_rollback(mode: AdmissionMode, endpoint: str) -> None:
    """C7: a genuine delayed sibling tool result after a known child
    blocks the R derivation WITHOUT inventing causal edges or
    rolling back the actual P selection: the READY state is not
    mutated by any query, the delayed state retains the same P
    selection digest, and both original maximal witnesses stay
    retained."""
    ns, state = q_bootstrap(mode, f"r-c-dly-{endpoint}")
    state = q_issue(state, ns, "ua", endpoint, BOUNDARYLESS_CMD, (CAUSAL_ROOT_FACT,))
    state = q_issue(state, ns, "ub", endpoint, BOUNDARYLESS_CMD, (CAUSAL_ROOT_FACT,))
    req_a = read_request(endpoint, "ua", OPAQUE_BODY, BOUNDARYLESS_CMD)
    req_b = read_request(endpoint, "ub", OPAQUE_BODY, BOUNDARYLESS_CMD)
    only_a = r_observe(state, ns, (req_a,)).state
    ua = q_occ(only_a, "ua")
    va_state = q_observe(
        q_issue(only_a, ns, "va", endpoint, Q_MIX_CMD, (ua.occurrence_id,)),
        ns,
        endpoint,
        "va",
        q_mixed_body(Q_A_TEXT, Q_MARK, "Known Va."),
        Q_MIX_CMD,
    )
    rk = _r(va_state, ns)
    _assert_ready_bindings(rk, va_state, "Known Va.")
    assert rk.q_result is not None
    assert rk.q_result.usable_selected_source_digest == sha256_hex("Known Va.")
    assert rk.q_result.p_selection is not None
    before = (
        tuple(o.occurrence_id for o in va_state.d_state.occurrences),
        tuple(f.source_digest for f in va_state.root_facts),
    )
    # The DELAYED ub result now blocks on a NEW state.
    delayed = r_observe(va_state, ns, (req_b,)).state
    assert delayed is not va_state
    rd = _r(delayed, ns)
    assert rd.outcome is RootRegionGraphOutcome.ROOT_CURRENTNESS_UNPROVEN
    assert rd.resolved_source is None and rd.f_result is None
    q = rd.q_result
    assert q is not None
    assert q.outcome is RootRegionCurrentnessOutcome.ROOT_CURRENTNESS_UNPROVEN
    assert q.state is delayed
    assert q.usable_selected_source_digest is None
    # The ACTUAL same-run P selection still carries the known Va.
    assert q.p_selection is not None
    assert q.p_selection.selected_source_digest == rk.q_result.p_selection.selected_source_digest
    ua_d, ub_d, va_d = (q_occ(delayed, c) for c in ("ua", "ub", "va"))
    edges = {(link.child, link.parent) for link in delayed.d_state.parent_links}
    assert (va_d.occurrence_id, ua_d.occurrence_id) in edges
    assert (ub_d.occurrence_id, va_d.occurrence_id) not in edges
    assert (va_d.occurrence_id, ub_d.occurrence_id) not in edges
    assert {w.call_id for w in q.uncertainty_witnesses} == {"ua", "ub"}
    # The READY state was not mutated by any query or later observe.
    after = (
        tuple(o.occurrence_id for o in va_state.d_state.occurrences),
        tuple(f.source_digest for f in va_state.root_facts),
    )
    assert before == after
    assert rk.q_result.state is va_state


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
@pytest.mark.parametrize(
    ("cmd", "expected_count"),
    ((REPEAT_CMD, 2), (REPEAT3_CMD, 3)),
    ids=["repeat2", "repeat3"],
)
def test_c_p_unsupported_complete_root_shape_unproven(
    mode: AdmissionMode, endpoint: str, cmd: str, expected_count: int
) -> None:
    """C8: a COMPLETE root-bearing occurrence excluded by the P
    root source-shape policy (repeated root operands, two and three,
    including the boundaryless triple) is explicit
    unsupported-root-shape uncertainty: the R result maps the ACTUAL
    same-run Q unproven with no source, no F and no R diagnostics,
    while the actual P selection stays its correct OK contract: the
    KNOWN authoritative anchor digest stays known and selected,
    while the individual per-file member hashes of the boundaryless
    repeated-root carrier remain unknown (never claimed per-file),
    and NO P authority fact is minted."""
    ns, state = q_bootstrap(mode, f"r-c-rep{expected_count}-{endpoint}")
    anchor_body = "Initial root."
    if cmd is REPEAT_CMD:
        body = q_mixed_body(anchor_body, Q_MARK, anchor_body)
    else:
        body = anchor_body + anchor_body + anchor_body + Q_A_TEXT
    state = q_observe(
        q_issue(state, ns, "rp", endpoint, cmd, (CAUSAL_ROOT_FACT,)), ns, endpoint, "rp", body, cmd
    )
    rp = q_occ(state, "rp")
    assert rp.anchored is True
    assert not any(f.provenance.kind != "envelope" for f in state.root_facts)
    r = _r(state, ns)
    assert r.outcome is RootRegionGraphOutcome.ROOT_CURRENTNESS_UNPROVEN
    assert r.diagnostics == ()
    assert r.resolved_source is None
    assert r.f_result is None
    assert r.e_overlay is None
    q = r.q_result
    assert q is not None
    assert q.outcome is RootRegionCurrentnessOutcome.ROOT_CURRENTNESS_UNPROVEN
    assert q.usable_selected_source_digest is None
    assert len(q.uncertainty_witnesses) == 1
    w = q.uncertainty_witnesses[0]
    assert w.occurrence is rp
    assert w.uncertainty_class is RootRegionUncertaintyClass.UNSUPPORTED_ROOT_SHAPE
    assert w.root_operand_count == expected_count
    assert q.p_selection is not None
    assert q.p_selection.outcome is RootSelectionOutcome.OK
    assert q.p_selection.selected_source_digest == sha256_hex(anchor_body)
    assert q.p_selection.limitations == ()


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_c_unissued_root_bearing_nonblocking_and_late_receipt(
    mode: AdmissionMode, endpoint: str
) -> None:
    """C9: unissued root-bearing evidence never blocks the R
    derivation: a mixed-only region observed WITHOUT issuance stays
    READY at the anchor (the actual P selection carries the
    ROOT_SOURCE_UNPROVEN limitation), a genuine issuance ALONE still
    never anchors (no authority, still READY), and only the matching
    delayed receipt anchors the SAME retained occurrence.  The
    opaque path activates at the receipt instead: the same retained
    occurrence becomes the actual UNPROVEN witness (original
    ID/proof/owner record, no P fact minted)."""
    # Part 1: the supported mixed-only region path.
    ns, s0 = q_bootstrap(mode, f"r-c-niss-{endpoint}")
    anchor_body = "Initial root."
    s1 = r_observe(
        s0,
        ns,
        (read_request(endpoint, "u1", q_mixed_body(Q_A_TEXT, Q_MARK, anchor_body), Q_MIX_CMD),),
    ).state
    u1 = q_occ(s1, "u1")
    assert u1.anchored is False
    f1 = next(f for f in s1.root_facts if f.provenance.kind == "read_region")
    assert f1.issued is False and f1.authority is False
    r1 = _r(s1, ns)
    _assert_ready_bindings(r1, s1, anchor_body)
    q1 = r1.q_result
    assert q1 is not None
    assert q1.outcome is RootRegionCurrentnessOutcome.READY
    assert not q1.uncertainty_witnesses
    assert q1.p_selection is not None
    assert RootLineageLimitation.ROOT_SOURCE_UNPROVEN in q1.p_selection.limitations
    # Issuance alone never anchors: still READY at the anchor.
    s2 = r_issue(s1, ns, "u1", endpoint, (CAUSAL_ROOT_FACT,), Q_MIX_CMD).state
    u2 = q_occ(s2, "u1")
    assert u2 is u1 and u2.anchored is False
    f2 = next(f for f in s2.root_facts if f.provenance.kind == "read_region")
    assert f2.issued is True and f2.authority is False
    r2 = _r(s2, ns)
    _assert_ready_bindings(r2, s2, anchor_body)
    assert r2.q_result is not None
    assert not r2.q_result.uncertainty_witnesses
    # The matching delayed receipt anchors the SAME retained
    # occurrence (same ID, ORIGINAL proof by identity); equal-byte
    # maxima are compatible: READY at the anchor, no uncertainty.
    s3 = r_receipt(s2, ns, "u1", endpoint, (CAUSAL_ROOT_FACT,), Q_MIX_CMD).state
    u3 = q_occ(s3, "u1")
    assert u3 is not u1
    assert u3.occurrence_id == u1.occurrence_id
    assert u3.proof is u1.proof
    assert u3.anchored is True
    f3 = next(f for f in s3.root_facts if f.provenance.kind == "read_region")
    assert f3.issued is True and f3.authority is True
    r3 = _r(s3, ns)
    _assert_ready_bindings(r3, s3, anchor_body)
    assert r3.q_result is not None
    assert not r3.q_result.uncertainty_witnesses
    # Part 2: the boundaryless OPAQUE path (late activation).
    ns_b, sb0 = q_bootstrap(mode, f"r-c-late-{endpoint}")
    sb1 = r_observe(sb0, ns_b, (read_request(endpoint, "uo", OPAQUE_BODY, BOUNDARYLESS_CMD),)).state
    original = q_occ(sb1, "uo")
    assert original.anchored is False
    original_proof = original.proof
    original_owner = next(x for x in sb1.d_state.results if x.call_id == "uo")
    assert original_owner.complete is True
    rb1 = _r(sb1, ns_b)
    _assert_ready_bindings(rb1, sb1, anchor_body)
    assert rb1.q_result is not None
    assert not rb1.q_result.uncertainty_witnesses
    # Issuance alone leaves the completed retained source unanchored.
    sb2 = r_issue(sb1, ns_b, "uo", endpoint, (CAUSAL_ROOT_FACT,), BOUNDARYLESS_CMD).state
    uo2 = q_occ(sb2, "uo")
    assert uo2 is original and uo2.anchored is False
    rb2 = _r(sb2, ns_b)
    _assert_ready_bindings(rb2, sb2, anchor_body)
    assert rb2.q_result is not None
    assert not rb2.q_result.uncertainty_witnesses
    # The matching delayed receipt activates the SAME retained
    # occurrence as the actual uncertainty witness.
    sb3 = r_receipt(sb2, ns_b, "uo", endpoint, (CAUSAL_ROOT_FACT,), BOUNDARYLESS_CMD).state
    final_occ = q_occ(sb3, "uo")
    assert final_occ is not original
    assert final_occ.occurrence_id == original.occurrence_id
    assert final_occ.proof is original_proof
    assert final_occ.anchored is True
    assert not any(f.provenance.kind != "envelope" for f in sb3.root_facts)
    rb3 = _r(sb3, ns_b)
    assert rb3.outcome is RootRegionGraphOutcome.ROOT_CURRENTNESS_UNPROVEN
    assert rb3.resolved_source is None and rb3.f_result is None
    assert rb3.diagnostics == ()
    qb3 = rb3.q_result
    assert qb3 is not None
    assert qb3.outcome is RootRegionCurrentnessOutcome.ROOT_CURRENTNESS_UNPROVEN
    assert qb3.usable_selected_source_digest is None
    assert len(qb3.uncertainty_witnesses) == 1
    w = qb3.uncertainty_witnesses[0]
    assert w.occurrence is final_occ
    assert w.result_record is original_owner
    assert w.uncertainty_class is RootRegionUncertaintyClass.OPAQUE_ROOT_BEARING_GROUP
    assert w.root_operand_count == 1


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_c_whole_and_region_descendant_of_all_ready(mode: AdmissionMode, endpoint: str) -> None:
    """C10: a genuinely NEW supported descendant of ALL unresolved
    maximal branches restores the R READY outcome in BOTH source
    forms: the whole singleton read (kind read) and the mixed-only
    region read (kind read_region); both dominated original
    witnesses stay retained on the actual Q result."""
    ns, state, _v2 = _frontier_state(mode, endpoint, f"r-c-wa-{endpoint}")
    ua, ub = q_occ(state, "ua"), q_occ(state, "ub")
    state = q_observe(
        q_issue(state, ns, "vs", endpoint, "cat AGENTS.md", (ua.occurrence_id, ub.occurrence_id)),
        ns,
        endpoint,
        "vs",
        "Singleton of all.\n",
        "cat AGENTS.md",
    )
    r = _r(state, ns)
    _assert_ready_bindings(r, state, "Singleton of all.\n")
    assert r.resolved_source is not None
    assert r.resolved_source.kind == "read"
    q = r.q_result
    assert q is not None
    assert q.outcome is RootRegionCurrentnessOutcome.READY
    assert q.usable_selected_source_digest == sha256_hex("Singleton of all.\n")
    assert {w.occurrence_id for w in q.uncertainty_witnesses} == {
        ua.occurrence_id,
        ub.occurrence_id,
    }
    assert q.p_selection is not None
    assert [f.provenance.kind for f in q.p_selection.witness_facts] == ["read"]
    # The mixed-only region form of the same descendant-of-all law.
    ns2, state2, _v2 = _frontier_state(mode, endpoint, f"r-c-ra-{endpoint}")
    ua2, ub2 = q_occ(state2, "ua"), q_occ(state2, "ub")
    state2 = q_observe(
        q_issue(state2, ns2, "vr", endpoint, Q_MIX_CMD, (ua2.occurrence_id, ub2.occurrence_id)),
        ns2,
        endpoint,
        "vr",
        q_mixed_body(Q_A_TEXT, Q_MARK, "Region of all."),
        Q_MIX_CMD,
    )
    r2 = _r(state2, ns2)
    _assert_ready_bindings(r2, state2, "Region of all.")
    assert r2.resolved_source is not None
    assert r2.resolved_source.kind == "read_region"
    assert r2.q_result is not None
    assert {w.occurrence_id for w in r2.q_result.uncertainty_witnesses} == {
        ua2.occurrence_id,
        ub2.occurrence_id,
    }


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_c_replayed_old_requests_after_known_new_root_no_rollback(
    mode: AdmissionMode, endpoint: str
) -> None:
    """C11: after a known new root (the descendant-of-all whole
    read) restores the R READY outcome, an EXACT replay of the old
    original request is a pure no-op (replayed outcome, same state
    object, no new occurrence or edge) and the READY derivation does
    not roll back: the selected root body and the actual Q evidence
    are unchanged."""
    ns, state, _v2 = _frontier_state(mode, endpoint, f"r-c-rep-{endpoint}")
    ua, ub = q_occ(state, "ua"), q_occ(state, "ub")
    ua_req = read_request(endpoint, "ua", OPAQUE_BODY, BOUNDARYLESS_CMD)
    # Replay of the ua observation on the UNPROVEN state: no-op.
    t0 = r_observe(state, ns, (ua_req,))
    assert t0.outcome.value == "replayed"
    assert t0.state is state
    r0 = _r(state, ns)
    assert r0.outcome is RootRegionGraphOutcome.ROOT_CURRENTNESS_UNPROVEN
    # The known new root: a descendant-of-all whole read.
    state = q_observe(
        q_issue(state, ns, "vs", endpoint, "cat AGENTS.md", (ua.occurrence_id, ub.occurrence_id)),
        ns,
        endpoint,
        "vs",
        "Singleton of all.\n",
        "cat AGENTS.md",
    )
    r1 = _r(state, ns)
    _assert_ready_bindings(r1, state, "Singleton of all.\n")
    occ_before = tuple(o.occurrence_id for o in state.d_state.occurrences)
    # Replay of the OLD ua request AFTER the known new root: pure
    # no-op, no rollback.
    t2 = r_observe(state, ns, (ua_req,))
    assert t2.outcome.value == "replayed"
    assert t2.state is state
    assert tuple(o.occurrence_id for o in state.d_state.occurrences) == occ_before
    r2 = _r(state, ns)
    _assert_ready_bindings(r2, state, "Singleton of all.\n")
    assert r1.q_result is not None
    assert r2.q_result is not None
    assert r1.q_result.p_selection is not None
    assert r2.q_result.p_selection is not None
    assert r2.q_result.scope_key == r1.q_result.scope_key
    assert r2.q_result.p_selection.selected_source_digest == (
        r1.q_result.p_selection.selected_source_digest
    )


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_c_nonready_target_reach_spies(
    mode: AdmissionMode, endpoint: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    """C12: positive-first target-reach evidence on the ACTUAL work,
    instrumented without any class-to-function replacement:
    (a) counting __init__ spies on the actual materialized source
    record class and the actual F graph class, and (b) delegating
    ENTRY counters on the R module's actual _r_resolve_source and
    its imported _derive_graph functions (normal original calls and
    returns preserved, exact restoration by monkeypatch).  The
    source-record constructor runs AFTER root extraction and the
    graph constructor is late in F, so the entry counters are the
    BEFORE-work proof on the ACTUAL Q non-ready outcomes: the READY
    derivation reaches BOTH entries and BOTH constructors, while the
    unproven and conflict states reach ZERO of the four (returned
    None source/F alone would not prove the work never ran)."""
    from slaif_local_coding.constitution.bundles import (
        root_region_graph as r_module,
    )
    from slaif_local_coding.constitution.bundles.current_graph_models import (
        CurrentGraph,
    )
    from slaif_local_coding.constitution.bundles.root_region_graph_models import (
        ResolvedRootRegionSource,
    )

    def _spy_cls(cls: Any) -> dict[str, int]:
        count = {"n": 0}
        original = cls.__init__

        def counting(self: Any, *args: Any, **kwargs: Any) -> None:
            count["n"] += 1
            original(self, *args, **kwargs)

        monkeypatch.setattr(cls, "__init__", counting)
        return count

    def _spy_entry(name: str) -> dict[str, int]:
        count = {"n": 0}
        original = getattr(r_module, name)

        def counting(*args: Any, **kwargs: Any) -> Any:
            count["n"] += 1
            return original(*args, **kwargs)

        monkeypatch.setattr(r_module, name, counting)
        return count

    src_cls = _spy_cls(ResolvedRootRegionSource)
    f_cls = _spy_cls(CurrentGraph)
    src_entry = _spy_entry("_r_resolve_source")
    f_entry = _spy_entry("_derive_graph")

    def _reset() -> None:
        src_cls["n"] = 0
        f_cls["n"] = 0
        src_entry["n"] = 0
        f_entry["n"] = 0

    def _all_zero() -> None:
        assert src_cls["n"] == 0
        assert f_cls["n"] == 0
        assert src_entry["n"] == 0
        assert f_entry["n"] == 0

    # READY positive: source resolution, F derivation and both
    # actual constructors are all reached.
    ns, s0 = r_bootstrap(mode, f"r-c-spy-{endpoint}")
    r = _r(s0, ns)
    assert r.outcome is RootRegionGraphOutcome.READY
    assert src_entry["n"] >= 1
    assert f_entry["n"] >= 1
    assert src_cls["n"] >= 1
    assert f_cls["n"] >= 1
    # Q non-ready: the ACTUAL unproven and conflict states reach
    # NEITHER entry NOR either constructor.
    _reset()
    ns_u, s_u, _v2 = _frontier_state(mode, endpoint, f"r-c-spyu-{endpoint}")
    r_u = _r(s_u, ns_u)
    assert r_u.outcome is RootRegionGraphOutcome.ROOT_CURRENTNESS_UNPROVEN
    assert r_u.resolved_source is None and r_u.f_result is None
    _all_zero()
    _reset()
    ns_c, s_c, _f1, _f2 = _two_sibling_regions(mode, f"r-c-spyc-{endpoint}", endpoint)
    r_c = _r(s_c, ns_c)
    assert r_c.outcome is RootRegionGraphOutcome.ROOT_AUTHORITY_CONFLICT
    assert r_c.resolved_source is None and r_c.f_result is None
    _all_zero()


# --- D. Refusal boundaries (fixed typed private errors) -----------------


def _d_ready_fixture(
    mode: AdmissionMode, endpoint: str, lineage: str
) -> tuple[Any, Any, RootRegionGraphResult]:
    """A genuine public P -> R READY on the ACTUAL mixed region
    (envelope anchor + one proven authoritative region child)."""
    ns, s0 = r_bootstrap(mode, lineage)
    t1 = r_issue(s0, ns, "m1", endpoint, (CAUSAL_ROOT_FACT,), MIX_CMD)
    assert t1.outcome.value == "accepted", t1.diagnostics
    state = r_observe(
        t1.state, ns, (read_request(endpoint, "m1", _mixed_body(A_TEXT, MARK, V2), MIX_CMD),)
    ).state
    r = _r(state, ns)
    assert r.outcome is RootRegionGraphOutcome.READY
    return ns, state, r


def _d_reconstruct(r: RootRegionGraphResult, **updates: Any) -> RootRegionGraphResult:
    """One public-constructor pass over the retained result fields:
    the nested records are passed as ACTUAL objects, so the outer
    closed law re-runs while the nested records are the forged
    ones (the model_copy-bypass pattern)."""
    fields = {name: getattr(r, name) for name in RootRegionGraphResult.model_fields}
    return RootRegionGraphResult(**{**fields, **updates})


def _d_mapped_refusal(r: RootRegionGraphResult, state: Any, q_diag: str) -> None:
    """A mapped Q refusal through the R public result: refused with
    NO R-OWN diagnostics, the ACTUAL same-run Q result retained by
    reference carrying the fixed Q reason, no source or F, and the
    exact prior state."""
    assert r.outcome is RootRegionGraphOutcome.REFUSED
    assert r.diagnostics == ()
    assert r.resolved_source is None
    assert r.f_result is None
    assert r.e_overlay is None
    assert r.q_result is not None
    assert r.q_result.outcome is RootRegionCurrentnessOutcome.REFUSED
    assert [d.value for d in r.q_result.diagnostics] == [q_diag]
    assert r.q_result.state is state
    assert r.state is state
    assert r.revision == state.revision


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_d_genuine_public_ready_positive(mode: AdmissionMode, endpoint: str) -> None:
    """D: genuine positive FIRST -- the actual public P -> R READY
    on the mixed-region fixture: the resolved source is the proven
    region child with the closed READY bindings (exact root body,
    digest/length, original fact/occurrence/proof identity, actual
    Q ready and F ok evidence, E overlay)."""
    _ns, state, r = _d_ready_fixture(mode, endpoint, f"r-d-pos-{endpoint}")
    _assert_ready_bindings(r, state, V2)
    assert r.resolved_source is not None
    assert r.resolved_source.kind == "read_region"
    assert r.q_result is not None
    assert r.q_result.p_selection is not None
    assert r.q_result.p_selection.outcome is RootSelectionOutcome.OK
    assert r.q_result.p_selection.selected_source_digest == sha256_hex(V2)


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_d_public_derivation_boundaries_refuse(mode: AdmissionMode, endpoint: str) -> None:
    """D: the public derivation's own early gates refuse with the
    fixed typed R diagnostics and the honest default domain: an
    unusable namespace (None, a partial ACTUAL instance, an
    unencodable graph version) is a foreign-scope refusal under
    the safe rejection graph version BEFORE any encoder
    exception, and a partial actual bound set is a malformed
    binding (exact prior state, no Q evidence invented, no
    source).  A valid STRICTER Q bounds copy is legal."""
    ns, state, _r0 = _d_ready_fixture(mode, endpoint, f"r-d-bd-{endpoint}")
    # Intentional malformed-input negative: a missing namespace.
    r_none = derive_root_region_graph(state, None)  # type: ignore[arg-type]
    assert r_none.outcome is RootRegionGraphOutcome.REFUSED
    assert r_none.diagnostics == (RootRegionGraphDiagnostic.FOREIGN_SCOPE,)
    assert r_none.graph_version == "unavailable"
    assert r_none.q_result is None and r_none.resolved_source is None
    assert r_none.state is state
    ns_partial = ns.model_construct(history_version=ns.history_version)
    r_partial = derive_root_region_graph(state, ns_partial)
    assert r_partial.outcome is RootRegionGraphOutcome.REFUSED
    assert r_partial.diagnostics == (RootRegionGraphDiagnostic.FOREIGN_SCOPE,)
    assert r_partial.graph_version == "unavailable"
    assert r_partial.q_result is None
    # The unencodable actual graph version is fenced BEFORE any
    # scope-key hash/encode (no UnicodeEncodeError escapes).
    ns_bad_v = ns.model_copy(update={"graph_version": "\ud800"})
    r_bad_v = derive_root_region_graph(state, ns_bad_v)
    assert r_bad_v.outcome is RootRegionGraphOutcome.REFUSED
    assert r_bad_v.diagnostics == (RootRegionGraphDiagnostic.FOREIGN_SCOPE,)
    assert r_bad_v.graph_version == "unavailable"
    assert r_bad_v.q_result is None
    for bad_bounds, deleted_field, kw in (
        (RootRegionGraphBounds(), "max_total_work_units", "bounds"),
        (RootRegionCurrentnessBounds(), "max_total_work_units", "root_region_currentness_bounds"),
        (CurrentGraphBounds(), "max_total_work_units", "current_graph_bounds"),
        (CurrentnessBounds(), "max_work_units", "nonroot_currentness_bounds"),
    ):
        object.__delattr__(bad_bounds, deleted_field)
        # Intentional malformed-input negative: a partial actual bounds copy.
        r_bad_b = derive_root_region_graph(state, ns, **{kw: bad_bounds})  # type: ignore[arg-type]
        assert r_bad_b.outcome is RootRegionGraphOutcome.REFUSED, (kw, r_bad_b.outcome)
        assert r_bad_b.diagnostics == (RootRegionGraphDiagnostic.MALFORMED_BINDING,)
        assert r_bad_b.q_result is None
        assert r_bad_b.state is state
    r_strict = derive_root_region_graph(
        state,
        ns,
        root_region_currentness_bounds=RootRegionCurrentnessBounds(max_total_work_units=500_000),
    )
    assert r_strict.outcome is RootRegionGraphOutcome.READY
    assert r_strict.state is state


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_d_foreign_scope_and_stale_key(mode: AdmissionMode, endpoint: str) -> None:
    """D: wrong actual namespace/state bindings map the ACTUAL
    same-run Q foreign-scope refusal before interpretation (the R
    result adds no own diagnostics; the nested Q evidence carries
    the reason): two different valid namespace factories are
    foreign scopes, an ACTUAL stale/borrowed lineage key on the
    state, and a copied namespace field tamper RETAINING the old
    keys; the partial actual namespace hits the R early gate
    itself (safe rejection scope, no Q phase at all)."""
    ns, state, _r0 = _d_ready_fixture(mode, endpoint, f"r-d-scope-{endpoint}")
    identity2 = RequestIdentity(
        principal="other-principal",
        session="other-session",
        repository="other-repo",
        route="other-route",
    )
    admission2 = make_bundle_admission_namespace(
        identity2,
        model_identity="synthetic-graph-model",
        config_fingerprint=FINGERPRINT,
        workspace=WORKSPACE,
        mode=mode,
    )
    ns_other_scope = make_root_region_lineage_namespace(admission2, f"r-d-scope-{endpoint}")
    _d_mapped_refusal(derive_root_region_graph(state, ns_other_scope), state, "foreign_scope")
    ns_stale = make_root_region_lineage_namespace(admission2, f"stale-{mode.value}")
    _d_mapped_refusal(derive_root_region_graph(state, ns_stale), state, "foreign_scope")
    borrowed = state.model_copy(update={"lineage_key": ns_other_scope.lineage_key})
    assert borrowed.lineage_key != state.lineage_key
    _d_mapped_refusal(derive_root_region_graph(borrowed, ns), borrowed, "foreign_scope")
    ns_tampered = ns.model_copy(update={"workspace": "/workX"})
    assert ns_tampered.lineage_key == ns.lineage_key
    assert ns_tampered.history_key == ns.history_key
    _d_mapped_refusal(derive_root_region_graph(state, ns_tampered), state, "foreign_scope")
    ns_partial = ns.model_construct(history_version=ns.history_version)
    r5 = derive_root_region_graph(state, ns_partial)
    assert r5.outcome is RootRegionGraphOutcome.REFUSED
    assert r5.diagnostics == (RootRegionGraphDiagnostic.FOREIGN_SCOPE,)
    assert r5.graph_version == "unavailable"
    assert r5.q_result is None
    assert r5.state is state


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_d_stale_version_fence(mode: AdmissionMode, endpoint: str) -> None:
    """D: a stale version control: an ACTUAL unsupported history
    version on a COPIED namespace whose keys are NOT recomputed --
    the scope fences still match the unchanged key, so the
    version-pair fence refuses with the ACTUAL same-run Q evidence
    retained (the R result adds no own diagnostics)."""
    ns, state, _r0 = _d_ready_fixture(mode, endpoint, f"r-d-ver-{endpoint}")
    bad = ns.model_copy(update={"history_version": "unsupported-causal-history/v0"})
    assert bad.lineage_key == ns.lineage_key  # stale: copied, not recomputed
    _d_mapped_refusal(derive_root_region_graph(state, bad), state, "version_unsupported")


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_d_coherent_rekeyed_unsupported_version(mode: AdmissionMode, endpoint: str) -> None:
    """D: a coherently rekeyed ACTUAL unsupported contract version
    (the accepted c2/c3 pattern through the actual _lineage_key
    recipe): the scope fence PRECEDES the version fence (a
    coherent v2 namespace over the genuine v1 state refuses
    foreign scope), and a namespace AND state rekeyed to the SAME
    coherent v2 key still refuses the unsupported version (scope
    identity alone is not version support)."""
    ns, state, _r0 = _d_ready_fixture(mode, endpoint, f"r-d-rekey-{endpoint}")
    v2 = "cache-root-region-lineage/v2"
    k2 = _lineage_key(
        ns.history_key, v2, ROOT_REGION_LINEAGE_POLICY_VERSION, ns.root_lineage_bounds
    )
    ns_v2 = ns.model_copy(update={"contract_version": v2, "lineage_key": k2})
    assert ns_v2.lineage_key == k2
    assert ns_v2.lineage_key != state.lineage_key
    _d_mapped_refusal(derive_root_region_graph(state, ns_v2), state, "foreign_scope")
    state_v2 = state.model_copy(update={"lineage_key": k2})
    _d_mapped_refusal(derive_root_region_graph(state_v2, ns_v2), state_v2, "version_unsupported")


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_d_forged_source_and_nested_joins_refused(mode: AdmissionMode, endpoint: str) -> None:
    """D: the model_copy-bypassed forged-join battery (the W-v4
    counterexamples as permanent controls): every copied tag /
    bounds / version / occurrence / graph splice is a fixed
    private constructor error -- never a READY, never an
    attribute error.  A genuine public READY positive on each
    fixture first.  The ACTUAL 3-char/5-byte UTF-8 Unicode
    content law (envelope kind): the incoherent declared-length
    forge is refused by the closed O(1) anchor join BEFORE any
    content measurement, and the coherent declared-length forge
    (every declared length at the char count) reaches and is
    refused by the capped no-copy UTF-8 measurement before the
    owned encode."""
    _ns, state, r = _d_ready_fixture(mode, endpoint, f"r-d-fg-{endpoint}")
    _assert_ready_bindings(r, state, V2)
    # Envelope anchor source forgeries (fresh envelope bootstrap).
    ns_e, s_e = r_bootstrap(mode, f"r-d-fo-{endpoint}")
    r_e = _r(s_e, ns_e)
    assert r_e.outcome is RootRegionGraphOutcome.READY
    assert r_e.resolved_source is not None
    assert r_e.resolved_source.kind == "envelope"
    src_proof = r_e.resolved_source.model_copy(update={"proof": object()})
    with pytest.raises(ValidationError, match="actual closed proof"):
        _d_reconstruct(r_e, resolved_source=src_proof)
    src_kind = r_e.resolved_source.model_copy(update={"kind": "read_region"})
    with pytest.raises(ValidationError, match="requires the actual read_region provenance"):
        _d_reconstruct(r_e, resolved_source=src_kind)
    # Nested Q/F/E evidence forgeries (stale or foreign tags).
    assert r_e.q_result is not None
    q_bad = r_e.q_result.model_copy(
        update={"bounds": RootRegionCurrentnessBounds(max_total_work_units=1)}
    )
    with pytest.raises(ValidationError, match="bounds"):
        _d_reconstruct(r_e, q_result=q_bad)
    assert r_e.f_result is not None
    assert r_e.f_result.overlay is not None
    f_bad = r_e.f_result.model_copy(
        update={
            "overlay": r_e.f_result.overlay.model_copy(update={"policy_version": "unsupported"})
        }
    )
    with pytest.raises(ValidationError, match="version tags"):
        _d_reconstruct(r_e, f_result=f_bad)
    f_bounds_bad = r_e.f_result.model_copy(
        update={
            "overlay": r_e.f_result.overlay.model_copy(
                update={"bounds": CurrentGraphBounds(max_total_work_units=1)}
            )
        }
    )
    with pytest.raises(ValidationError, match="bounds"):
        _d_reconstruct(r_e, f_result=f_bounds_bad)
    assert r_e.e_overlay is not None
    e_bad = r_e.e_overlay.model_copy(update={"bounds": CurrentnessBounds(max_work_units=1)})
    with pytest.raises(ValidationError, match="bounds"):
        _d_reconstruct(r_e, e_overlay=e_bad)
    # M06: the selected source occurrence + proof cloned TOGETHER
    # (matching IDs/content): a foreign source, refused.
    actual_occ = next(o for o in state.d_state.occurrences if o.call_id == "m1")
    cloned_occ = actual_occ.model_copy(deep=True)
    assert cloned_occ is not actual_occ
    assert r.resolved_source is not None
    copied_src = r.resolved_source.model_copy(
        update={"occurrence": cloned_occ, "proof": cloned_occ.proof}
    )
    with pytest.raises(ValidationError, match="original D-state member"):
        _d_reconstruct(r, resolved_source=copied_src)
    # M07: a genuine old graph spliced into the current wrapper.
    t3 = r_issue(state, _ns, "m2", endpoint, (actual_occ.occurrence_id,), MIX_CMD)
    assert t3.outcome.value == "accepted", t3.diagnostics
    state2 = r_observe(
        t3.state,
        _ns,
        (read_request(endpoint, "m2", _mixed_body(A_TEXT, MARK, V3), MIX_CMD),),
    ).state
    r_new = _r(state2, _ns)
    assert r_new.f_result is not None
    assert r_new.f_result.overlay is not None
    assert r_new.f_result.overlay.revision == state2.d_state.revision
    assert r.f_result is not None
    assert r.f_result.overlay is not None
    f_spliced = r_new.f_result.model_copy(update={"overlay": r.f_result.overlay})
    assert f_spliced.overlay is not None
    assert f_spliced.overlay.revision != state2.d_state.revision
    with pytest.raises(ValidationError, match="carried D revision"):
        _d_reconstruct(r_new, f_result=f_spliced)
    # M07 strong: the SAME selected root and namespace with an
    # ACTUAL nonroot supplier change (only the A.md member text
    # moves, the V2 root body does not): the new revision is
    # still a carried D revision when the old overlay is spliced
    # back (revision is a snapshot association, never a
    # freshness clock, and the root did not move).
    A2_TEXT = "Synthetic nonroot A2.\n"
    t4 = r_issue(state, _ns, "m3", endpoint, (actual_occ.occurrence_id,), MIX_CMD)
    assert t4.outcome.value == "accepted", t4.diagnostics
    state3 = r_observe(
        t4.state,
        _ns,
        (read_request(endpoint, "m3", _mixed_body(A2_TEXT, MARK, V2), MIX_CMD),),
    ).state
    r_3 = _r(state3, _ns)
    assert r_3.outcome is RootRegionGraphOutcome.READY
    assert r_3.resolved_source is not None
    assert r_3.resolved_source.root_text == V2
    assert r_3.f_result is not None
    assert r_3.f_result.overlay is not None
    assert r_3.f_result.overlay.revision == state3.d_state.revision
    assert r_3.f_result.overlay.revision != state.d_state.revision
    f_spliced2 = r_3.f_result.model_copy(update={"overlay": r.f_result.overlay})
    with pytest.raises(ValidationError, match="carried D revision"):
        _d_reconstruct(r_3, f_result=f_spliced2)
    # M08: malformed inherited GraphBounds BEFORE any serializer.
    g_bad = r_new.f_result.overlay.model_copy(
        update={
            "graph_bounds": r_new.f_result.overlay.graph_bounds.model_copy(
                update={"max_nodes": object()}
            )
        }
    )
    f_bad8 = r_new.f_result.model_copy(update={"overlay": g_bad})
    with pytest.raises(ValidationError, match="closed scalar fields"):
        _d_reconstruct(r_new, f_result=f_bad8)
    # The ACTUAL 3-char/5-byte UTF-8 Unicode content law on the
    # ENVELOPE kind (the single-file root body): genuine
    # positive first.
    _ns_u, s_u = r_bootstrap(mode, f"r-d-uni-{endpoint}", root_body="Üö\n")
    r_u = _r(s_u, _ns_u)
    assert r_u.outcome is RootRegionGraphOutcome.READY
    assert r_u.resolved_source is not None
    assert r_u.resolved_source.kind == "envelope"
    assert r_u.resolved_source.root_text == "Üö\n"
    assert r_u.resolved_source.root_byte_length == 5  # 2+2+1 UTF-8 bytes
    # (1) The INCOHERENT declared-length forge (the fact declares
    # the char count 3 while the envelope provenance anchor keeps
    # the actual 5): the closed O(1) local anchor join fires
    # BEFORE any content measurement.
    src = r_u.resolved_source
    assert src is not None
    src_inc = src.model_copy(
        update={
            "root_byte_length": 3,
            "fact": src.fact.model_copy(update={"source_byte_length": 3}),
        }
    )
    with pytest.raises(ValidationError, match="envelope provenance anchor binding"):
        _d_reconstruct(r_u, resolved_source=src_inc)
    # (2) The COHERENT declared-length forge (all three declared
    # lengths -- the source root_byte_length, the fact
    # source_byte_length and the envelope provenance
    # source_byte_length -- set to the char count 3) so every
    # closed O(1) equality join passes and the fence that fires
    # is the ACTUAL capped NO-COPY UTF-8 measurement of the
    # record's own bounded root text (2+2+1 bytes measured
    # before the owned encode, which is never allocated).
    prov_short = src.fact.provenance.model_copy(update={"source_byte_length": 3})
    fact_short = src.fact.model_copy(update={"provenance": prov_short, "source_byte_length": 3})
    src_short = src.model_copy(update={"root_byte_length": 3, "fact": fact_short})
    with pytest.raises(ValidationError, match="digest and byte length"):
        _d_reconstruct(r_u, resolved_source=src_short)


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_d_m09_source_field_deletions_refused(mode: AdmissionMode, endpoint: str) -> None:
    """D: each of the SEVEN declared ResolvedSource fields deleted
    on a negative copy is a fixed private constructor error (no
    attribute error, no echo); an invalid kind variant carrying a
    KNOWN SYNTHETIC private canary is refused by the fixed message
    BEFORE dispatch or interpolation (the canary is never
    echoed)."""
    _ns, _state, r = _d_ready_fixture(mode, endpoint, f"r-d-m09-{endpoint}")
    assert r.resolved_source is not None
    for field in (
        "kind",
        "fact",
        "root_text",
        "root_digest",
        "root_byte_length",
        "occurrence",
        "proof",
    ):
        src = r.resolved_source.model_copy()
        object.__delattr__(src, field)
        assert not hasattr(src, field)
        with pytest.raises(ValidationError):
            _d_reconstruct(r, resolved_source=src)
    canary = "canary-private-variant"
    src_c = r.resolved_source.model_copy(update={"kind": canary})
    with pytest.raises(ValidationError, match="closed variant") as excinfo:
        _d_reconstruct(r, resolved_source=src_c)
    assert canary not in str(excinfo.value)
    assert canary not in repr(excinfo.value)


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_d_m10_nested_field_deletions_refused(mode: AdmissionMode, endpoint: str) -> None:
    """D: the NINE nested record fields the boundary actually
    touches (q_result outcome/p_selection/usable digest, f_result
    state/outcome/overlay, p_selection outcome/digest/witnesses)
    deleted one at a time are fixed private constructor errors."""
    _ns, _state, r = _d_ready_fixture(mode, endpoint, f"r-d-m10-{endpoint}")
    for record_attr, field in (
        ("q_result", "outcome"),
        ("q_result", "p_selection"),
        ("q_result", "usable_selected_source_digest"),
        ("f_result", "state"),
        ("f_result", "outcome"),
        ("f_result", "overlay"),
    ):
        rec = getattr(r, record_attr).model_copy()
        object.__delattr__(rec, field)
        with pytest.raises(ValidationError):
            _d_reconstruct(r, **{record_attr: rec})
    assert r.q_result is not None
    assert r.q_result.p_selection is not None
    for field in ("outcome", "selected_source_digest", "witness_facts"):
        sel = r.q_result.p_selection.model_copy()
        object.__delattr__(sel, field)
        q_sel = r.q_result.model_copy(update={"p_selection": sel})
        with pytest.raises(ValidationError):
            _d_reconstruct(r, q_result=q_sel)


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_d_m11_selection_copies_refused(mode: AdmissionMode, endpoint: str) -> None:
    """D: the M11 selection-local battery on the SAME genuine
    READY fixture: seven forged P-selection copies (foreign
    revision/key, bool revision, list witnesses, foreign witness
    element, 1025 witnesses, non-container witnesses), the
    detached EXTRA witness (the ORIGINAL selected fact is retained
    in the tuple, so only the every-witness identity fence can
    refuse), the deleted authority flag (existence BEFORE read),
    and the two non-ready scope controls on a genuine public Q
    unproven result."""
    _ns, state, r = _d_ready_fixture(mode, endpoint, f"r-d-m11-{endpoint}")
    assert r.q_result is not None
    assert r.q_result.p_selection is not None
    sel = r.q_result.p_selection
    fact = sel.witness_facts[0]

    def forge(sel_update: dict[str, Any]) -> RootRegionGraphResult:
        forged_sel = sel.model_copy(update=sel_update)
        assert r.q_result is not None
        forged_q = r.q_result.model_copy(update={"p_selection": forged_sel})
        return _d_reconstruct(r, q_result=forged_q)

    with pytest.raises(ValidationError):
        forge({"revision": r.revision + 1})
    with pytest.raises(ValidationError):
        forge({"lineage_key": "f" * 64})
    with pytest.raises(ValidationError):
        forge({"revision": True})
    with pytest.raises(ValidationError):
        forge({"witness_facts": [fact]})
    with pytest.raises(ValidationError):
        forge({"witness_facts": (fact, object())})
    with pytest.raises(ValidationError):
        forge({"witness_facts": tuple([fact] * 1025)})
    with pytest.raises(ValidationError):
        forge({"witness_facts": object()})
    # The detached EXTRA witness: a VALUE-EQUAL clone of the selected
    # fact itself (same digest, so only the every-witness IDENTITY
    # fence can refuse) alongside the ORIGINAL retained fact (the
    # old source-fact-in-witnesses scan would pass this tuple).
    extra = fact.model_copy(deep=True)
    assert extra is not fact
    assert extra == fact
    with pytest.raises(ValidationError, match="original retained root facts"):
        forge({"witness_facts": (fact, extra)})
    noauth = fact.model_copy()
    object.__delattr__(noauth, "authority")
    assert not hasattr(noauth, "authority")
    with pytest.raises(ValidationError, match="authoritative"):
        forge({"witness_facts": (noauth,)})
    # The genuine UNPROVEN non-ready scope controls.
    ns_u, s_u, _v2 = _frontier_state(mode, endpoint, f"r-d-m11u-{endpoint}")
    r_u = _r(s_u, ns_u)
    assert r_u.outcome is RootRegionGraphOutcome.ROOT_CURRENTNESS_UNPROVEN
    assert r_u.q_result is not None
    sel_u = r_u.q_result.p_selection
    assert sel_u is not None

    def forge_u(sel_update: dict[str, Any]) -> RootRegionGraphResult:
        forged_sel = sel_u.model_copy(update=sel_update)
        assert r_u.q_result is not None
        forged_q = r_u.q_result.model_copy(update={"p_selection": forged_sel})
        fields_u = {n: getattr(r_u, n) for n in RootRegionGraphResult.model_fields}
        return RootRegionGraphResult(**{**fields_u, "q_result": forged_q})

    with pytest.raises(ValidationError):
        forge_u({"revision": r_u.revision + 1})
    with pytest.raises(ValidationError):
        forge_u({"lineage_key": "f" * 64})


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_d_public_state_forged_channels(mode: AdmissionMode, endpoint: str) -> None:
    """D: the PUBLIC derivation's own state-level law (the
    observed channels as permanent controls): a state whose
    d_state is not the actual bounded record is the fixed typed
    private ValueError; a forged D history key maps the ACTUAL
    same-run Q foreign-scope refusal; a top-level revision
    increment (the D revision unchanged) and every forged
    region-flag / proof-binding / provenance join are ACTUAL
    P-validation refusals carrying the fixed
    p_validation_problem (no P selection, no Q diagnostics, no
    source or F, the exact bad state retained), the forged
    provenance coordinates and whole-proof / root-member digest
    joins, a MISSING owning result record, and a CHANGED actual
    piece-producer binding (the typed result conflict).  The
    W-copy probe's deep-copied owning-record READY row is retained
    ONLY as a qualified outside-acceptance diagnostic (a
    value-equal model-copied input is still a valid input; the
    public derivation is a pure function of the exact input) --
    it is NOT a public-P-produced positive and is excluded from
    this acceptance matrix."""
    ns, state, r0 = _d_ready_fixture(mode, endpoint, f"r-d-pub-{endpoint}")
    assert r0.outcome is RootRegionGraphOutcome.READY
    rf = next(f for f in state.root_facts if f.provenance.kind == "read_region")
    occ = next(o for o in state.d_state.occurrences if o.call_id == "m1")

    def swap_root_facts(st: Any, new_fact: Any) -> Any:
        return st.model_copy(
            update={"root_facts": tuple(new_fact if f is rf else f for f in st.root_facts)}
        )

    def swap_occurrence(st: Any, new_occ: Any) -> Any:
        nd = st.d_state.model_copy(
            update={
                "occurrences": tuple(new_occ if o is occ else o for o in st.d_state.occurrences)
            }
        )
        return st.model_copy(update={"d_state": nd})

    def assert_mapped_p_refusal(
        r: RootRegionGraphResult,
        bad_state: Any,
        problem: RootLineageLimitation = RootLineageLimitation.MALFORMED_BINDING,
    ) -> None:
        assert r.outcome is RootRegionGraphOutcome.REFUSED
        assert r.diagnostics == ()
        assert r.resolved_source is None and r.f_result is None and r.e_overlay is None
        assert r.q_result is not None
        assert r.q_result.outcome is RootRegionCurrentnessOutcome.REFUSED
        assert r.q_result.diagnostics == ()
        assert r.q_result.p_selection is None
        assert r.q_result.usable_selected_source_digest is None
        assert r.q_result.p_validation_problem is problem
        assert r.q_result.state is bad_state
        assert r.state is bad_state
        assert r.revision == bad_state.revision

    # (1) the fixed typed private state boundary (no untyped
    # escape).
    bad_ds = state.model_copy(update={"d_state": object()})
    with pytest.raises(ValueError, match="actual bounded state record"):
        derive_root_region_graph(bad_ds, ns)
    # (2) the forged D history key: ACTUAL same-run Q
    # foreign-scope refusal (the R result adds no own
    # diagnostics).
    bad_hist = state.model_copy(
        update={"d_state": state.d_state.model_copy(update={"history_key": "f" * 64})}
    )
    _d_mapped_refusal(derive_root_region_graph(bad_hist, ns), bad_hist, "foreign_scope")
    # (3) the top-level revision increment (the D revision is
    # unchanged): ACTUAL P validation refusal.
    bad_rev = state.model_copy(update={"revision": state.revision + 1})
    assert_mapped_p_refusal(derive_root_region_graph(bad_rev, ns), bad_rev)
    # (4) the derived region flags.
    for flag in ("authority", "issued"):
        bad_flag = swap_root_facts(state, rf.model_copy(update={flag: False}))
        assert_mapped_p_refusal(derive_root_region_graph(bad_flag, ns), bad_flag)
    # (5) the forged proof root bindings.
    bad_rp = swap_occurrence(
        state, occ.model_copy(update={"proof": occ.proof.model_copy(update={"root_path": "A.md"})})
    )
    assert_mapped_p_refusal(derive_root_region_graph(bad_rp, ns), bad_rp)
    bad_sd = swap_occurrence(
        state,
        occ.model_copy(update={"proof": occ.proof.model_copy(update={"source_digest": "0" * 64})}),
    )
    assert_mapped_p_refusal(derive_root_region_graph(bad_sd, ns), bad_sd)
    # (6) the forged provenance member length and concrete class.
    bad_len = swap_root_facts(
        state,
        rf.model_copy(
            update={"provenance": rf.provenance.model_copy(update={"root_member_byte_length": 99})}
        ),
    )
    assert_mapped_p_refusal(derive_root_region_graph(bad_len, ns), bad_len)
    env_prov = EnvelopeRootProvenance.model_construct(
        kind="envelope",
        root_digest=rf.source_digest,
        workspace=ns.workspace,
        source_byte_length=rf.source_byte_length,
    )
    bad_cls = swap_root_facts(state, rf.model_copy(update={"provenance": env_prov}))
    assert_mapped_p_refusal(derive_root_region_graph(bad_cls, ns), bad_cls)
    # (7) the forged provenance coordinates.
    for field, value in (("root_segment_index", 5), ("root_member_position", 5)):
        bad_coord = swap_root_facts(
            state,
            rf.model_copy(update={"provenance": rf.provenance.model_copy(update={field: value})}),
        )
        assert_mapped_p_refusal(derive_root_region_graph(bad_coord, ns), bad_coord)
    # (8) the forged whole-proof aggregate and root-member digest
    # joins.
    forged_joins: list[tuple[str, Any]] = [
        ("whole_proof_digest", "0" * 64),
        ("whole_proof_byte_length", 99),
        ("root_member_digest", "0" * 64),
    ]
    for field, value in forged_joins:
        bad_join = swap_root_facts(
            state,
            rf.model_copy(update={"provenance": rf.provenance.model_copy(update={field: value})}),
        )
        assert_mapped_p_refusal(derive_root_region_graph(bad_join, ns), bad_join)
    # (9) the MISSING owning result record (the occurrence is
    # retained without its complete original record).
    bad_owner = state.model_copy(
        update={
            "d_state": state.d_state.model_copy(
                update={"results": tuple(r_ for r_ in state.d_state.results if r_.call_id != "m1")}
            )
        }
    )
    assert_mapped_p_refusal(derive_root_region_graph(bad_owner, ns), bad_owner)
    # (10) the CHANGED actual piece-producer binding (the stored
    # primitive association of the complete original record): the
    # typed result conflict, not the malformed binding.
    rec = next(r_ for r_ in state.d_state.results if r_.call_id == "m1")
    bad_cid = rec.model_copy(
        update={
            "piece_call_bindings": tuple(
                ("m9",) + b[1:] if i == 0 else b for i, b in enumerate(rec.piece_call_bindings)
            )
        }
    )
    bad_cid_state = state.model_copy(
        update={"d_state": state.d_state.model_copy(update={"results": (bad_cid,)})}
    )
    assert_mapped_p_refusal(
        derive_root_region_graph(bad_cid_state, ns),
        bad_cid_state,
        problem=RootLineageLimitation.RESULT_CONFLICT,
    )
    bad_fp = rec.model_copy(
        update={
            "piece_call_bindings": tuple(
                b[:3] + ("0" * 64,) if i == 0 else b for i, b in enumerate(rec.piece_call_bindings)
            )
        }
    )
    bad_fp_state = state.model_copy(
        update={"d_state": state.d_state.model_copy(update={"results": (bad_fp,)})}
    )
    assert_mapped_p_refusal(
        derive_root_region_graph(bad_fp_state, ns),
        bad_fp_state,
        problem=RootLineageLimitation.RESULT_CONFLICT,
    )
    # (11) the owning record whose call identity no longer matches
    # the occurrence, and the owning record that is no longer
    # complete: the occurrence is retained without its ACTUAL
    # complete original record (malformed binding).
    bad_call = rec.model_copy(update={"call_id": "m9"})
    bad_call_state = state.model_copy(
        update={"d_state": state.d_state.model_copy(update={"results": (bad_call,)})}
    )
    assert_mapped_p_refusal(derive_root_region_graph(bad_call_state, ns), bad_call_state)
    bad_inc = rec.model_copy(update={"complete": False})
    bad_inc_state = state.model_copy(
        update={"d_state": state.d_state.model_copy(update={"results": (bad_inc,)})}
    )
    assert_mapped_p_refusal(derive_root_region_graph(bad_inc_state, ns), bad_inc_state)
    # (12) the remaining actual piece-producer binding fields
    # (endpoint, tool): the typed result conflict.
    # The binding tuple is (call_id, endpoint, tool_name,
    # argument_fingerprint); the endpoint replacement touches ONLY
    # index 1, the tool replacement ONLY index 2.
    first = rec.piece_call_bindings[0]
    opposite = "chat" if first[1] == "responses" else "responses"
    assert opposite != first[1]
    bad_ep = rec.model_copy(
        update={
            "piece_call_bindings": tuple(
                b[:1] + (opposite,) + b[2:] if i == 0 else b if i == 0 else b
                for i, b in enumerate(rec.piece_call_bindings)
            )
        }
    )
    forged_first = bad_ep.piece_call_bindings[0]
    assert forged_first[1] == opposite
    assert forged_first[0] == first[0]
    assert forged_first[2:] == first[2:]
    bad_ep_state = state.model_copy(
        update={"d_state": state.d_state.model_copy(update={"results": (bad_ep,)})}
    )
    assert_mapped_p_refusal(
        derive_root_region_graph(bad_ep_state, ns),
        bad_ep_state,
        problem=RootLineageLimitation.RESULT_CONFLICT,
    )
    bad_tool = rec.model_copy(
        update={
            "piece_call_bindings": tuple(
                b[:2] + ("write_stdin",) + b[3:] if i == 0 else b
                for i, b in enumerate(rec.piece_call_bindings)
            )
        }
    )
    bad_tool_state = state.model_copy(
        update={"d_state": state.d_state.model_copy(update={"results": (bad_tool,)})}
    )
    assert_mapped_p_refusal(
        derive_root_region_graph(bad_tool_state, ns),
        bad_tool_state,
        problem=RootLineageLimitation.RESULT_CONFLICT,
    )


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_d_native_poll_producer_alias_refused(mode: AdmissionMode, endpoint: str) -> None:
    """D: on the ACTUAL synthetic native 3-piece carrier (the A8
    positive shape: exec m1 + polls p1/p2, marker split across the
    exec/poll boundary), aliasing the FIRST POLL piece's producer
    to the INITIAL exec owner (piece_call_bindings[1]'s call_id
    p1 -> m1) breaks the piece-producing association: the ACTUAL P
    validation maps the typed result conflict with all other
    binding coordinates untouched, and the R result carries no own
    diagnostics, no usable source digest, the exact bad state and
    no source or F.  This is a distinct actual 3-piece control:
    ordinary one-piece producer mutations do not cover it."""
    ns, s0 = r_bootstrap(mode, f"r-d-npv-{endpoint}")
    t1 = r_issue(s0, ns, "m1", endpoint, (CAUSAL_ROOT_FACT,), MIX_CMD)
    assert t1.outcome.value == "accepted"
    t2 = r_observe(t1.state, ns, (_native_multi_piece_request(endpoint),))
    assert t2.outcome.value == "accepted", t2.diagnostics
    state = t2.state
    # The genuine positive first on the SAME fixture.
    r_pos = _r(state, ns)
    assert r_pos.outcome is RootRegionGraphOutcome.READY
    assert r_pos.resolved_source is not None
    owner = next(x for x in state.d_state.results if x.call_id == "m1")
    bindings = [tuple(b) for b in owner.piece_call_bindings]
    assert bindings[0][0] == "m1" and bindings[1][0] == "p1"
    bindings[1] = ("m1",) + bindings[1][1:]
    bad = owner.model_copy(update={"piece_call_bindings": tuple(bindings)})
    assert bad.piece_call_bindings[1][1:] == owner.piece_call_bindings[1][1:]
    bad_state = state.model_copy(
        update={
            "d_state": state.d_state.model_copy(
                update={"results": tuple(bad if x is owner else x for x in state.d_state.results)}
            )
        }
    )
    r = derive_root_region_graph(bad_state, ns)
    assert r.outcome is RootRegionGraphOutcome.REFUSED
    assert r.diagnostics == ()
    assert r.resolved_source is None and r.f_result is None and r.e_overlay is None
    assert r.q_result is not None
    assert r.q_result.outcome is RootRegionCurrentnessOutcome.REFUSED
    assert r.q_result.diagnostics == ()
    assert r.q_result.p_selection is None
    assert r.q_result.usable_selected_source_digest is None
    assert r.q_result.p_validation_problem is RootLineageLimitation.RESULT_CONFLICT
    assert r.q_result.state is bad_state
    assert r.state is bad_state
    assert r.revision == bad_state.revision


def _native_multi_piece_request(endpoint: str) -> Any:
    """The synthetic native multi-piece carrier for the ACTUAL mixed
    command: exec piece + two poll pieces (len > 1), the marker
    literal split across the exec/poll piece boundary.  No client or
    native process starts; the frames are known synthetic literals."""
    import json as _json

    from slaif_local_coding.constitution.bundles.graph_observation import GraphRequest
    from tests.test_bundle_proof import (
        exec_call,
        frame_native_final,
        frame_native_running,
        out_item,
        poll_call,
    )

    full = _mixed_body(A_TEXT, MARK, V2)
    i = full.index(MARK)
    part0 = full[: i + 3]  # ends INSIDE the marker literal
    part1 = full[i + 3 : i + 11]
    part2 = full[i + 11 :]
    assert part0 + part1 + part2 == full
    assert MARK not in (part0, part1, part2)  # the marker crosses pieces
    if endpoint == "responses":
        payload = {
            "model": "synthetic-bundle-model",
            "input": [
                exec_call("m1", MIX_CMD),
                out_item("m1", frame_native_running(73, "0a1b2c", part0, 4)),
                poll_call("p1", 73),
                out_item("p1", frame_native_running(73, "3d4e5f", part1, 4)),
                poll_call("p2", 73),
                out_item("p2", frame_native_final("6e7f80", part2, 4)),
            ],
        }
        return GraphRequest(payload=payload, endpoint="responses", context=None)
    messages: list[dict[str, Any]] = [
        {
            "role": "assistant",
            "tool_calls": [
                {
                    "id": "m1",
                    "type": "function",
                    "function": {
                        "name": "exec_command",
                        "arguments": _json.dumps({"cmd": MIX_CMD}),
                    },
                }
            ],
        },
        {
            "role": "tool",
            "tool_call_id": "m1",
            "content": frame_native_running(73, "0a1b2c", part0, 4),
        },
        {
            "role": "assistant",
            "tool_calls": [
                {
                    "id": "p1",
                    "type": "function",
                    "function": {
                        "name": "write_stdin",
                        "arguments": _json.dumps({"session_id": 73, "chars": ""}),
                    },
                }
            ],
        },
        {
            "role": "tool",
            "tool_call_id": "p1",
            "content": frame_native_running(73, "3d4e5f", part1, 4),
        },
        {
            "role": "assistant",
            "tool_calls": [
                {
                    "id": "p2",
                    "type": "function",
                    "function": {
                        "name": "write_stdin",
                        "arguments": _json.dumps({"session_id": 73, "chars": ""}),
                    },
                }
            ],
        },
        {"role": "tool", "tool_call_id": "p2", "content": frame_native_final("6e7f80", part2, 4)},
    ]
    return GraphRequest(payload={"messages": messages}, endpoint="chat", context=None)


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_a_native_multi_piece_carrier_ready(mode: AdmissionMode, endpoint: str) -> None:
    """A8: the genuine native MULTI-PIECE carrier (exec + two
    polls, three pieces, marker split across the exec/poll
    boundary) derives READY with the ACTUAL original exec owner
    and poll piece producers retained by identity: the proof's
    original exec association, the INITIAL complete exec owning
    record in the exact input state, each piece joined to its
    ACTUAL producing call through that record's observed
    piece-call bindings, the FROZEN causal parent frontier (the
    m1 occurrence parented to the bootstrap root anchor), the
    proven executed operand list and the exact root body."""
    ns, s0 = r_bootstrap(mode, f"r-a-mp-{endpoint}")
    t1 = r_issue(s0, ns, "m1", endpoint, (CAUSAL_ROOT_FACT,), MIX_CMD)
    assert t1.outcome.value == "accepted"
    t2 = r_observe(t1.state, ns, (_native_multi_piece_request(endpoint),))
    assert t2.outcome.value == "accepted", t2.diagnostics
    s2 = t2.state
    r = _r(s2, ns)
    _assert_ready_bindings(r, s2, V2)
    assert r.resolved_source is not None
    proof = r.resolved_source.proof
    assert proof is not None
    assert len(proof.pieces) == 3
    pieces = proof.pieces
    # The original exec owner and the causally associated poll pieces
    # (never invented): each piece keeps its own call association.
    assert pieces[0].call_id == "m1"
    assert pieces[1].call_id == "p1"
    assert pieces[2].call_id == "p2"
    assert (pieces[0].call_position, pieces[0].result_position) == (0, 1)
    assert (pieces[1].call_position, pieces[1].result_position) == (2, 3)
    assert (pieces[2].call_position, pieces[2].result_position) == (4, 5)
    # The proof's ORIGINAL exec association: the exec call owns
    # the whole complete result (the polls only extend it).
    assert proof.call_id == "m1"
    assert proof.result_position == 1
    # The INITIAL exec owning record in the exact input state:
    # the m1 record is the COMPLETE original record, and every
    # retained piece joins its ACTUAL producing call through that
    # record's observed piece-call bindings (never invented).
    ds = s2.d_state
    m1_res = next(r_ for r_ in ds.results if r_.call_id == "m1")
    assert m1_res.complete is True
    assert m1_res in ds.results
    assert [b[0] for b in m1_res.piece_call_bindings] == ["m1", "p1", "p2"]
    for piece, binding in zip(pieces, m1_res.piece_call_bindings, strict=True):
        assert piece.call_id == binding[0]
    # The FROZEN causal parent frontier: the only occurrence is
    # m1's, parented to the ORIGINAL bootstrap root anchor fact
    # (the polls carry no frozen edge of their own).
    m1_occ = next(o for o in ds.occurrences if o.call_id == "m1")
    assert len(ds.parent_links) == 1
    assert ds.parent_links[0].child == m1_occ.occurrence_id
    assert ds.parent_links[0].parent == CAUSAL_ROOT_FACT
    # The resolved source is the INPUT's own original occurrence
    # and retained proof, by identity.
    assert r.resolved_source.occurrence is not None
    assert r.resolved_source.proof is not None
    assert r.resolved_source.occurrence is m1_occ
    assert r.resolved_source.proof is m1_occ.proof
    # The proven executed OPERAND list of the ACTUAL mixed
    # command (request operand evidence, NOT the causal
    # frontier; the causal frontier is the parent link above).
    assert proof.proven_executed == ("A.md", "AGENTS.md")
    # The root interval was reassembled across the split marker.
    assert r.resolved_source.root_text == V2
    f = r.resolved_source.fact
    assert f.issued is True and f.authority is True


# --- E. Work bounds and the independent domains ----------------------


@pytest.mark.parametrize("mode", MODES)
def test_e_full_operation_cap_first_over(mode: AdmissionMode) -> None:
    """E1: The REACHABLE full-operation work boundary of the R
    derivation: the measured minimum cap accepts the ENTIRE
    sequence (READY at the exact boundary with the ACTUAL F/E
    evidence and the actual same-run Q READY carrying P OK); the
    exact one-unit-below cap refuses the typed over-bound result
    with the crossing in the FINAL output reservation AFTER the
    ACTUAL F/E phase completed -- the actual F ok and E overlay and
    the actual same-run Q (READY, P OK) are retained, no resolved
    source is published, and the EXACT state is preserved (no
    partial positive output, no usable label, no revision
    advance)."""
    ns, state = _e_audit_state(mode, f"r-e1-{mode.value}")

    def _probe(_m: AdmissionMode, _t: str, _i: int, cap: int) -> bool:
        return (
            derive_root_region_graph(
                state, ns, bounds=RootRegionGraphBounds(max_total_work_units=cap)
            ).outcome
            is RootRegionGraphOutcome.READY
        )

    cap = _min_accepted_cap(mode, f"r-e1-{mode.value}", _probe)
    r = derive_root_region_graph(state, ns, bounds=RootRegionGraphBounds(max_total_work_units=cap))
    assert r.outcome is RootRegionGraphOutcome.READY
    assert r.resolved_source is not None
    assert r.resolved_source.root_text == "Cap root.\n"
    assert r.resolved_source.root_digest == sha256_hex("Cap root.\n")
    assert r.f_result is not None and r.f_result.outcome is CurrentGraphOutcome.OK
    assert r.e_overlay is not None
    assert r.q_result is not None
    assert r.q_result.outcome is RootRegionCurrentnessOutcome.READY
    assert r.q_result.p_selection is not None
    assert r.q_result.p_selection.outcome is RootSelectionOutcome.OK
    assert r.state is state
    below = derive_root_region_graph(
        state, ns, bounds=RootRegionGraphBounds(max_total_work_units=cap - 1)
    )
    assert below.outcome is RootRegionGraphOutcome.REFUSED
    assert below.diagnostics == (RootRegionGraphDiagnostic.WORK_UNITS_OVER_BOUND,)
    assert below.resolved_source is None
    assert below.f_result is not None and below.f_result.outcome is CurrentGraphOutcome.OK
    assert below.e_overlay is not None
    assert below.q_result is not None
    assert below.q_result.outcome is RootRegionCurrentnessOutcome.READY
    assert below.q_result.p_selection is not None
    assert below.q_result.p_selection.outcome is RootSelectionOutcome.OK
    assert below.state is state


@pytest.mark.parametrize("mode", MODES)
def test_e_independent_p_domain_discriminator(
    mode: AdmissionMode, monkeypatch: pytest.MonkeyPatch
) -> None:
    """E2: The ACTUAL independent P domain beneath the ONE R
    outer, on a genuinely public-P-built fixture where the FULL R
    work EXCEEDS the actual P ceiling -- the shape a shared
    min(P ceiling, R total) budget cannot pass.

    Build 1 (generous): the n=40 eligible-opaque-branch sequence
    under the DEFAULT P ceiling, with per-operation maxima of the
    ACTUAL _HOuter ledgers tracked by a counting __init__ wrapper
    on the REAL class (installed/restored by monkeypatch; class
    identity and isinstance preserved).

    Build 2 (strict): the SAME sequence rebuilt under a FRESH
    namespace (fresh lineage, identical field structure -- NOT one
    namespace identity across both builds) whose ACTUAL inherited P
    ceiling is the measured per-operation producer maximum -- fully
    public P production, so the state under test was built under
    its own ceiling.

    Measured law (no hardcoded caps): P phase units <= P ceiling
    < full-R work cap <= R default ceiling.  R at the DEFAULT total
    is READY with ALL N original dominated witnesses retained by
    reference (a single shared min(P ceiling, R total) budget would
    refuse here: the full R work crosses it).  R total set to the
    measured P ceiling REFUSES the typed over-bound result INSIDE
    the Q phase, after the actual P phase completed and BEFORE the
    Q result is constructed: the R total is a TRUE TOTAL, not
    'P ceiling plus remainder', and no partial Q/P evidence is
    fabricated (q_result stays None).  P-first-over is NOT
    attained by THIS 40-branch public production sequence (the
    producer maximum exceeds the P phase, so no producible ceiling
    falls below the P phase); it is not claimed universally
    unreachable."""
    n = 40
    track: dict[str, Any] = {"live": [], "max": 0}
    orig_init = _HOuter.__init__

    def counting_init(self: Any, *args: Any, **kwargs: Any) -> None:
        orig_init(self, *args, **kwargs)
        track["live"].append(self)

    monkeypatch.setattr(_HOuter, "__init__", counting_init)
    _e_branch_state(mode, f"r-e2gen-{mode.value}-{n}", n, track=track)
    producer_max = track["max"]
    assert producer_max > 0
    # Strict rebuild: fully public production under the measured ceiling.
    ns, state, sib_ids = _e_branch_state(mode, f"r-e2str-{mode.value}-{n}", n, p_cap=producer_max)
    assert ns.root_lineage_bounds.max_total_work_units == producer_max
    # The ACTUAL P phase of the derivation, counted on the P-domain
    # ledger (the Q phase charges its separate ledger).
    p_count = {"n": 0}
    orig_unit = _HOuter.unit

    def counting_unit(self: Any, *args: Any, **kwargs: Any) -> bool:
        allowed = orig_unit(self, *args, **kwargs)
        if allowed:
            p_count["n"] += 1
        return allowed

    monkeypatch.setattr(_HOuter, "unit", counting_unit)
    r_default = derive_root_region_graph(state, ns)
    p_phase = p_count["n"]
    assert p_phase <= producer_max

    def _rcap_probe(_m: AdmissionMode, _t: str, _i: int, cap: int) -> bool:
        return (
            derive_root_region_graph(
                state, ns, bounds=RootRegionGraphBounds(max_total_work_units=cap)
            ).outcome
            is RootRegionGraphOutcome.READY
        )

    r_cap = _min_accepted_cap(mode, f"r-e2cap-{mode.value}", _rcap_probe)
    # The discriminating shape, measured (not hardcoded).
    assert producer_max < r_cap
    assert r_cap <= RootRegionGraphBounds().max_total_work_units
    # DEFAULT R total: READY with ALL N original dominated
    # witnesses retained by reference, in canonical (class,
    # occurrence_id) order.
    assert r_default.outcome is RootRegionGraphOutcome.READY
    q = r_default.q_result
    assert q is not None
    assert q.outcome is RootRegionCurrentnessOutcome.READY
    assert q.usable_selected_source_digest == sha256_hex("Cap root.\n")
    assert q.p_selection is not None and q.p_selection.outcome is RootSelectionOutcome.OK
    assert r_default.resolved_source is not None
    assert r_default.resolved_source.root_digest == sha256_hex("Cap root.\n")
    witnesses = q.uncertainty_witnesses
    assert len(witnesses) == n
    final_sibs = {
        o.occurrence_id: o for o in state.d_state.occurrences if o.occurrence_id in set(sib_ids)
    }
    complete_records = {
        (r_.call_id, r_.endpoint, r_.tool_name, r_.argument_fingerprint): r_
        for r_ in state.d_state.results
        if r_.complete is True
    }
    for w in witnesses:
        # Per-witness IDENTITY against the final retained state and
        # the original owning complete result record (not
        # structural set equality).
        assert w.occurrence is final_sibs[w.occurrence_id]
        assert (
            w.result_record
            is complete_records[
                (
                    w.occurrence.call_id,
                    w.occurrence.endpoint,
                    w.occurrence.tool_name,
                    w.occurrence.argument_fingerprint,
                )
            ]
        )
    assert list(witnesses) == sorted(
        witnesses, key=lambda w: (w.uncertainty_class.value, w.occurrence_id)
    )
    assert r_default.state is state
    # Full-R boundary at the exact measured cap: READY with all N
    # witnesses.
    r_at = derive_root_region_graph(
        state, ns, bounds=RootRegionGraphBounds(max_total_work_units=r_cap)
    )
    assert r_at.outcome is RootRegionGraphOutcome.READY
    assert r_at.q_result is not None
    assert len(r_at.q_result.uncertainty_witnesses) == n
    assert r_at.state is state
    # One below: the crossing lands in the FINAL output
    # reservation AFTER the ACTUAL Q and F phases completed: the
    # actual same-run Q (READY, P OK, all N witnesses) and the
    # actual F evidence are retained, no resolved source is
    # published.
    r_below = derive_root_region_graph(
        state, ns, bounds=RootRegionGraphBounds(max_total_work_units=r_cap - 1)
    )
    assert r_below.outcome is RootRegionGraphOutcome.REFUSED
    assert r_below.diagnostics == (RootRegionGraphDiagnostic.WORK_UNITS_OVER_BOUND,)
    assert r_below.resolved_source is None
    assert r_below.f_result is not None and r_below.f_result.outcome is CurrentGraphOutcome.OK
    assert r_below.q_result is not None
    assert r_below.q_result.outcome is RootRegionCurrentnessOutcome.READY
    assert r_below.q_result.p_selection is not None
    assert r_below.q_result.p_selection.outcome is RootSelectionOutcome.OK
    assert len(r_below.q_result.uncertainty_witnesses) == n
    assert r_below.state is state
    # R total = the measured P ceiling: the crossing lands INSIDE
    # the Q phase (after the actual P phase completed, before the
    # Q result is constructed): no partial Q evidence is
    # fabricated.
    r_pcap = derive_root_region_graph(
        state, ns, bounds=RootRegionGraphBounds(max_total_work_units=producer_max)
    )
    assert r_pcap.outcome is RootRegionGraphOutcome.REFUSED
    assert r_pcap.diagnostics == (RootRegionGraphDiagnostic.WORK_UNITS_OVER_BOUND,)
    assert r_pcap.q_result is None
    assert r_pcap.f_result is None
    assert r_pcap.resolved_source is None
    assert r_pcap.state is state


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_e_independent_local_domains(
    mode: AdmissionMode, endpoint: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    """E2b: The INDEPENDENT Q-local and F-subtree work domains
    beneath the ONE R total, each measured on the ACTUAL ledger
    classes (class-preserving __init__ wrappers installed and
    restored by monkeypatch; class identity and isinstance
    preserved): the exact measured local cap is sufficient for its
    ACTUAL subtree while the successful full-R total EXCEEDS it --
    the shape a shared min(local ceiling, R total) budget cannot
    pass -- and the exact one-unit-below local cap refuses through
    the ACTUAL local channel (Q: the retained typed Q refusal
    carrying the actual P selection, no F and no source; F: the
    retained ACTUAL F over-bound refusal with the actual same-run Q
    READY, no source), each with the EXACT state and no R-own
    diagnostics."""
    ns, state, positive = _d_ready_fixture(mode, endpoint, f"r-e2b-{endpoint}")
    assert positive.outcome is RootRegionGraphOutcome.READY

    r_ledgers: list[Any] = []
    q_ledgers: list[Any] = []
    f_ledgers: list[Any] = []

    def install(cls: Any, bucket: list[Any]) -> None:
        orig_init = cls.__init__

        def counting_init(self: Any, *args: Any, **kwargs: Any) -> None:
            orig_init(self, *args, **kwargs)
            bucket.append(self)

        monkeypatch.setattr(cls, "__init__", counting_init)

    install(_ROuter, r_ledgers)
    install(_RQOuter, q_ledgers)
    install(_RFOuter, f_ledgers)

    def derive(**kwargs: Any) -> RootRegionGraphResult:
        r_ledgers.clear()
        q_ledgers.clear()
        f_ledgers.clear()
        return derive_root_region_graph(state, ns, **kwargs)

    def costs() -> dict[str, int]:
        return {
            "R": max(i.work_spent for i in r_ledgers),
            "Q": max(i.work_spent for i in q_ledgers),
            "F": max(i.work_spent for i in f_ledgers),
        }

    r_def = derive()
    cost = costs()
    assert r_def.outcome is RootRegionGraphOutcome.READY
    assert r_def.state is state
    assert 0 < cost["F"] < cost["Q"] < cost["R"] <= RootRegionGraphBounds().max_total_work_units
    # --- The Q-local domain ---
    r_q = derive(
        root_region_currentness_bounds=RootRegionCurrentnessBounds(max_total_work_units=cost["Q"])
    )
    actual = costs()
    assert actual["Q"] == cost["Q"] and actual["R"] > cost["Q"]
    assert r_q.outcome is RootRegionGraphOutcome.READY
    assert r_q.resolved_source is not None
    assert r_q.f_result is not None and r_q.f_result.outcome is CurrentGraphOutcome.OK
    assert r_q.q_result is not None
    assert r_q.q_result.outcome is RootRegionCurrentnessOutcome.READY
    assert r_q.state is state
    assert r_q.scope_key != r_def.scope_key
    r_qb = derive(
        root_region_currentness_bounds=RootRegionCurrentnessBounds(
            max_total_work_units=cost["Q"] - 1
        )
    )
    # The Q-local crossing lands BEFORE the F phase: this run has
    # NO F ledger at all (the absent phase, never a fabricated
    # zero).
    assert not f_ledgers
    assert r_qb.outcome is RootRegionGraphOutcome.REFUSED
    assert r_qb.diagnostics == ()
    assert r_qb.resolved_source is None
    assert r_qb.f_result is None
    assert r_qb.e_overlay is None
    assert r_qb.q_result is not None
    assert r_qb.q_result.outcome is RootRegionCurrentnessOutcome.REFUSED
    assert [d.value for d in r_qb.q_result.diagnostics] == ["work_units_over_bound"]
    assert r_qb.q_result.p_selection is not None
    assert r_qb.q_result.p_selection.outcome is RootSelectionOutcome.OK
    assert r_qb.q_result.state is state
    assert r_qb.state is state
    # --- The F-subtree domain ---
    r_f = derive(current_graph_bounds=CurrentGraphBounds(max_total_work_units=cost["F"]))
    actual = costs()
    assert actual["F"] == cost["F"] and actual["R"] > cost["F"]
    assert r_f.outcome is RootRegionGraphOutcome.READY
    assert r_f.resolved_source is not None
    assert r_f.f_result is not None and r_f.f_result.outcome is CurrentGraphOutcome.OK
    assert r_f.q_result is not None
    assert r_f.q_result.outcome is RootRegionCurrentnessOutcome.READY
    assert r_f.state is state
    assert r_f.scope_key != r_def.scope_key
    r_fb = derive(current_graph_bounds=CurrentGraphBounds(max_total_work_units=cost["F"] - 1))
    assert r_fb.outcome is RootRegionGraphOutcome.REFUSED
    assert r_fb.diagnostics == ()
    assert r_fb.resolved_source is None
    assert r_fb.e_overlay is None
    assert r_fb.f_result is not None
    assert r_fb.f_result.outcome is CurrentGraphOutcome.REFUSED_OVER_BOUND
    assert [d.value for d in r_fb.f_result.diagnostics] == ["total_work_units_over_bound"]
    assert r_fb.f_result.state is state.d_state
    assert r_fb.q_result is not None
    assert r_fb.q_result.outcome is RootRegionCurrentnessOutcome.READY
    assert r_fb.q_result.p_selection is not None
    assert r_fb.q_result.p_selection.outcome is RootSelectionOutcome.OK
    assert r_fb.state is state


@pytest.mark.parametrize("mode", MODES)
def test_e_source_precharge_sentinel(mode: AdmissionMode, monkeypatch: pytest.MonkeyPatch) -> None:
    """E3: Target-reaching control on the ACTUAL selected-source
    type: the per-source precharge (the closed source
    reservation, charged on the ONE R total BEFORE the source
    object is constructed) is a genuine, separately measured
    crossing window.  Counting ACTUAL
    ResolvedRootRegionSource.__init__ entries on the REAL class
    (the wrapper is installed/restored by monkeypatch; class
    identity and isinstance preserved): the smallest cap at which
    the source is constructed at all (the precharge fully passes)
    constructs EXACTLY the one source; one unit below it the typed
    over-bound refusal lands BEFORE any source construction (zero
    entries) with the EXACT state and the ACTUAL same-run Q (READY,
    P OK) retained; the full accepted cap completes with the
    single original source and the actual F ok evidence.  This
    measures the precharge boundary; it makes no zero-allocation
    claim about the other result construction."""
    ns, state = _e_audit_state(mode, f"r-e3-{mode.value}")
    count = {"n": 0}
    orig_init = ResolvedRootRegionSource.__init__

    def counting_init(self: Any, *args: Any, **kwargs: Any) -> None:
        orig_init(self, *args, **kwargs)
        count["n"] += 1

    monkeypatch.setattr(ResolvedRootRegionSource, "__init__", counting_init)

    def _accepted(_m: AdmissionMode, _t: str, _i: int, cap: int) -> bool:
        return derive_root_region_graph(
            state, ns, bounds=RootRegionGraphBounds(max_total_work_units=cap)
        ).outcome in (
            RootRegionGraphOutcome.READY,
            RootRegionGraphOutcome.ROOT_CURRENTNESS_UNPROVEN,
            RootRegionGraphOutcome.ROOT_AUTHORITY_CONFLICT,
        )

    def _constructed(_m: AdmissionMode, _t: str, _i: int, cap: int) -> bool:
        count["n"] = 0
        _accepted(_m, _t, _i, cap)
        return count["n"] >= 1

    w_full = _min_accepted_cap(mode, f"r-e3full-{mode.value}", _accepted)
    w_pre = _min_accepted_cap(mode, f"r-e3pre-{mode.value}", _constructed)
    assert w_pre < w_full
    # At the precharge-passing cap the construction IS reached
    # (exactly one entry); the later result work still crosses, so
    # the result is the typed refusal (no invented positive, no
    # source or F carried in the refused result).
    count["n"] = 0
    r_pre = derive_root_region_graph(
        state, ns, bounds=RootRegionGraphBounds(max_total_work_units=w_pre)
    )
    assert count["n"] == 1
    assert r_pre.outcome is RootRegionGraphOutcome.REFUSED
    assert r_pre.diagnostics == (RootRegionGraphDiagnostic.WORK_UNITS_OVER_BOUND,)
    assert r_pre.resolved_source is None
    assert r_pre.f_result is None
    assert r_pre.q_result is not None
    assert r_pre.q_result.outcome is RootRegionCurrentnessOutcome.READY
    assert r_pre.q_result.p_selection is not None
    assert r_pre.q_result.p_selection.outcome is RootSelectionOutcome.OK
    assert r_pre.state is state
    # One unit below the precharge: the refusal lands BEFORE any
    # source construction (zero entries).
    count["n"] = 0
    r_before = derive_root_region_graph(
        state, ns, bounds=RootRegionGraphBounds(max_total_work_units=w_pre - 1)
    )
    assert count["n"] == 0
    assert r_before.outcome is RootRegionGraphOutcome.REFUSED
    assert r_before.diagnostics == (RootRegionGraphDiagnostic.WORK_UNITS_OVER_BOUND,)
    assert r_before.resolved_source is None
    assert r_before.f_result is None
    assert r_before.q_result is not None
    assert r_before.q_result.outcome is RootRegionCurrentnessOutcome.READY
    assert r_before.q_result.p_selection is not None
    assert r_before.q_result.p_selection.outcome is RootSelectionOutcome.OK
    assert r_before.state is state
    # The full accepted cap: the single original source, reaching
    # the target with a genuine positive.
    count["n"] = 0
    r_full = derive_root_region_graph(
        state, ns, bounds=RootRegionGraphBounds(max_total_work_units=w_full)
    )
    assert count["n"] == 1
    assert r_full.outcome is RootRegionGraphOutcome.READY
    assert r_full.resolved_source is not None
    assert r_full.resolved_source.root_text == "Cap root.\n"
    assert r_full.f_result is not None and r_full.f_result.outcome is CurrentGraphOutcome.OK
    assert r_full.state is state


@pytest.mark.parametrize("mode", MODES)
def test_e_source_slice_target_sentinel(mode: AdmissionMode) -> None:
    """E3b: Target-reaching control on the ACTUAL owned source
    SLICE (distinct from the post-slice content-measurement
    boundary, which measures statement entry, not the slice): a
    sys.settrace LINE entry on the exact slice statement of the
    charged resolver -- the line derived from the SOLE BINARY_SLICE
    of the code object, never hardcoded -- counts statement entry
    BEFORE the builtin slice executes.  The genuine full
    derivation enters the slice line exactly once (READY); the
    smallest cap at which the slice statement is reached enters it
    once and then the LATER reserved work crosses, so the typed R
    over-bound refusal publishes no source and no F while the
    actual same-run Q (READY, P OK) is retained on the EXACT
    state; one unit below it the refusal lands BEFORE the slice
    statement (zero entries, identical refusal).  Qualification:
    the line event measures statement entry, not completed opcode
    execution nor all allocations; the earlier opcode-event
    instrumentation attempt failed on this interpreter (zero
    events despite READY) and is preserved as a failed probe."""
    import dis as _dis
    import sys as _sys

    code = _r_resolve_source.__code__
    slice_instrs = [inst for inst in _dis.get_instructions(code) if inst.opname == "BINARY_SLICE"]
    assert len(slice_instrs) == 1
    assert slice_instrs[0].positions is not None
    slice_line = slice_instrs[0].positions.lineno
    ns, state = _e_audit_state(mode, f"r-e3b-{mode.value}")

    def _trace_derive(cap: int) -> tuple[RootRegionGraphResult, int]:
        hits: list[int] = []

        def trace(frame: Any, event: str, _arg: Any) -> Any:
            if frame.f_code is code:
                if event == "line" and frame.f_lineno == slice_line:
                    hits.append(frame.f_lineno)
                return trace
            return None

        assert _sys.gettrace() is None
        _sys.settrace(trace)
        try:
            r = derive_root_region_graph(
                state, ns, bounds=RootRegionGraphBounds(max_total_work_units=cap)
            )
        finally:
            _sys.settrace(None)
        return r, len(hits)

    def _reached(_m: AdmissionMode, _t: str, _i: int, cap: int) -> bool:
        return _trace_derive(cap)[1] >= 1

    w_slice = _min_accepted_cap(mode, f"r-e3b-{mode.value}", _reached)
    # The genuine full derivation enters the slice exactly once.
    r_full, hits_full = _trace_derive(RootRegionGraphBounds().max_total_work_units)
    assert hits_full == 1
    assert r_full.outcome is RootRegionGraphOutcome.READY
    assert r_full.resolved_source is not None
    assert r_full.resolved_source.root_text == "Cap root.\n"
    assert r_full.state is state
    # At the smallest slice-reaching cap: the slice statement is
    # entered once, then the later reserved work crosses -- the
    # typed R refusal, no source or F, the actual same-run Q
    # retained, EXACT state.
    r_at, hits_at = _trace_derive(w_slice)
    assert hits_at == 1
    assert r_at.outcome is RootRegionGraphOutcome.REFUSED
    assert r_at.diagnostics == (RootRegionGraphDiagnostic.WORK_UNITS_OVER_BOUND,)
    assert r_at.resolved_source is None
    assert r_at.f_result is None
    assert r_at.q_result is not None
    assert r_at.q_result.outcome is RootRegionCurrentnessOutcome.READY
    assert r_at.q_result.p_selection is not None
    assert r_at.q_result.p_selection.outcome is RootSelectionOutcome.OK
    assert r_at.state is state
    # One unit below: the refusal lands BEFORE the slice statement
    # (zero entries), identical typed refusal.
    r_before, hits_before = _trace_derive(w_slice - 1)
    assert hits_before == 0
    assert r_before.outcome is RootRegionGraphOutcome.REFUSED
    assert r_before.diagnostics == (RootRegionGraphDiagnostic.WORK_UNITS_OVER_BOUND,)
    assert r_before.resolved_source is None
    assert r_before.f_result is None
    assert r_before.q_result is not None
    assert r_before.q_result.outcome is RootRegionCurrentnessOutcome.READY
    assert r_before.state is state


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_e_inherited_retention_count_first_over(mode: AdmissionMode, endpoint: str) -> None:
    """E4: The ACTUAL inherited D retention-count domain
    (max_occurrences) beneath the region operations, at a genuine
    STRICTER cap: the genuine supported positive runs first (three
    accepted one-request observations retained at the cap, R READY
    on the exact state), then the first-over observation refuses
    the exact mapped retention bound with the EXACT prior state and
    no revision advance, retaining the ACTUAL refused D
    transition; at the same boundary a model-copied state carrying
    an EXTRA non-record occurrence is refused by the ACTUAL P
    validation for the retention count (no P selection, no usable
    digest, the exact bad state, no source or F)."""
    k = 3
    admission = make_bundle_admission_namespace(
        IDENTITY,
        model_identity="synthetic-r-model",
        config_fingerprint=FINGERPRINT,
        workspace=WORKSPACE,
        mode=mode,
    )
    ns = make_root_region_lineage_namespace(
        admission,
        f"r-e4-{mode.value}-{endpoint}",
        history_bounds=HistoryBounds(max_occurrences=k),
    )
    assert ns.history_bounds.max_occurrences == k
    t0 = bootstrap_root_region_lineage((rooted("Retention root."),), ns)
    assert t0.outcome.value == "accepted", t0.diagnostics
    state = t0.state
    for i in range(k):
        t = observe_root_region_lineage(
            state,
            ns,
            state.revision,
            (read_request(endpoint, f"r{i}", A_TEXT, "cat A.md"),),
        )
        assert t.outcome.value == "accepted", (t.outcome, t.diagnostics)
        state = t.state
    at_cap = state
    assert len(at_cap.d_state.occurrences) == k
    # The genuine R positive at the cap (the envelope anchor root).
    r_at = derive_root_region_graph(at_cap, ns)
    assert r_at.outcome is RootRegionGraphOutcome.READY
    assert r_at.resolved_source is not None
    assert r_at.resolved_source.root_text == "Retention root."
    assert r_at.state is at_cap
    # The first-over observation: the exact retention bound, exact
    # prior state.
    t_over = observe_root_region_lineage(
        at_cap,
        ns,
        at_cap.revision,
        (read_request(endpoint, "over", A_TEXT, "cat A.md"),),
    )
    assert t_over.outcome is RootLineageOutcome.REFUSED_OVER_BOUND
    assert t_over.state is at_cap
    assert t_over.diagnostics == (RootLineageLimitation.OCCURRENCES_OVER_BOUND,)
    assert t_over.new_root_facts == ()
    assert t_over.d_transition is not None
    assert t_over.d_transition.outcome.value == "refused_over_bound"
    assert t_over.d_transition.diagnostics == (CausalHistoryLimitation.OCCURRENCES_OVER_BOUND,)
    assert t_over.revision_after == at_cap.revision
    # At the same boundary: a model-copied state carrying an EXTRA
    # non-record occurrence is refused by the ACTUAL P validation
    # for the retention count BEFORE the malformed element is
    # inspected.
    bad = at_cap.model_copy(
        update={
            "d_state": at_cap.d_state.model_copy(
                update={"occurrences": at_cap.d_state.occurrences + (object(),)}
            )
        }
    )
    r_bad = derive_root_region_graph(bad, ns)
    assert r_bad.outcome is RootRegionGraphOutcome.REFUSED
    assert r_bad.diagnostics == ()
    assert r_bad.resolved_source is None and r_bad.f_result is None and r_bad.e_overlay is None
    assert r_bad.q_result is not None
    assert r_bad.q_result.outcome is RootRegionCurrentnessOutcome.REFUSED
    assert r_bad.q_result.p_selection is None
    assert r_bad.q_result.usable_selected_source_digest is None
    assert r_bad.q_result.p_validation_problem is RootLineageLimitation.OCCURRENCES_OVER_BOUND
    assert r_bad.q_result.state is bad
    assert r_bad.state is bad


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_e_inherited_batch_domain(mode: AdmissionMode, endpoint: str) -> None:
    """E5: The ACTUAL inherited D per-batch request domain beneath
    the region operations: with max_requests=1, two SEPARATE
    one-request observations are each legal and BOTH retained (the
    per-batch domain, not a cumulative cap; R READY on the exact
    state with no root uncertainty), while ONE two-request batch
    refuses the exact mapped batch bound BEFORE the deliberately
    malformed second element (missing call id) is inspected -- the
    count gate precedes element validation -- with the EXACT prior
    state, no D transition and no revision advance."""
    admission = make_bundle_admission_namespace(
        IDENTITY,
        model_identity="synthetic-r-model",
        config_fingerprint=FINGERPRINT,
        workspace=WORKSPACE,
        mode=mode,
        graph_bounds=GraphBounds(max_requests=1),
    )
    ns = make_root_region_lineage_namespace(admission, f"r-e5-{mode.value}-{endpoint}")
    t0 = bootstrap_root_region_lineage((rooted("Batch root."),), ns)
    assert t0.outcome.value == "accepted", t0.diagnostics
    s0 = t0.state
    t1 = observe_root_region_lineage(
        s0, ns, s0.revision, (read_request(endpoint, "b1", A_TEXT, "cat A.md"),)
    )
    assert t1.outcome.value == "accepted", (t1.outcome, t1.diagnostics)
    s1 = t1.state
    t2 = observe_root_region_lineage(
        s1, ns, s1.revision, (read_request(endpoint, "b2", B_TEXT, "cat B.md"),)
    )
    assert t2.outcome.value == "accepted", (t2.outcome, t2.diagnostics)
    s2 = t2.state
    assert len(s2.d_state.occurrences) == 2
    # The ACTUAL R derivation over the retained state at the bound:
    # READY with the anchor root usable, both completed
    # observations retained, no root uncertainty, exact state.
    r7 = derive_root_region_graph(s2, ns)
    assert r7.outcome is RootRegionGraphOutcome.READY
    assert r7.resolved_source is not None
    assert r7.resolved_source.root_text == "Batch root."
    assert r7.q_result is not None
    assert r7.q_result.p_selection is not None
    assert r7.q_result.p_selection.outcome is RootSelectionOutcome.OK
    assert not r7.q_result.uncertainty_witnesses
    assert r7.state is s2
    # One two-request batch: the bound fires before the bad element.
    t3 = observe_root_region_lineage(
        s2,
        ns,
        s2.revision,
        (
            read_request(endpoint, "b3", A_TEXT, "cat A.md"),
            read_request(endpoint, "", B_TEXT, "cat B.md"),
        ),
    )
    assert t3.outcome is RootLineageOutcome.REFUSED_OVER_BOUND
    assert t3.state is s2
    assert t3.diagnostics == (RootLineageLimitation.BATCH_OVER_BOUND,)
    assert t3.new_root_facts == ()
    # The mapped refusal retains the ACTUAL refused D transition
    # (propagated evidence, never invented).
    assert t3.d_transition is not None
    assert t3.d_transition.outcome.value == "refused_over_bound"
    assert t3.d_transition.diagnostics == (CausalHistoryLimitation.BATCH_OVER_BOUND,)
    assert t3.revision_after == s2.revision


@pytest.mark.parametrize("mode", MODES)
def test_e_own_diagnostics_constructor_evidence(mode: AdmissionMode) -> None:
    """E6: The R-OWN diagnostic domain (max_diagnostics).  The
    PUBLIC first-over is not claimed: a public R refusal carries at
    most ONE own fixed diagnostic by construction, so the honest
    constructor evidence is used instead.  First the genuine public
    refusal under the strict max_diagnostics=1 bound carries
    EXACTLY ONE own diagnostic within the bound (the typed work
    over-bound result, EXACT state retained); then the direct
    closed constructor refuses a forged result record carrying TWO
    distinct own diagnostics under that same strict bound (the
    count bound is enforced at the model boundary)."""
    ns, state = _e_audit_state(mode, f"r-e6-{mode.value}")
    strict = RootRegionGraphBounds(max_total_work_units=50, max_diagnostics=1)
    r = derive_root_region_graph(state, ns, strict)
    assert r.outcome is RootRegionGraphOutcome.REFUSED
    assert r.diagnostics == (RootRegionGraphDiagnostic.WORK_UNITS_OVER_BOUND,)
    assert r.resolved_source is None
    assert r.state is state
    # The closed constructor boundary: TWO distinct own diagnostics
    # under the strict bound are refused.
    with pytest.raises(ValidationError, match="R diagnostics exceed"):
        _d_reconstruct(
            r,
            diagnostics=(
                RootRegionGraphDiagnostic.WORK_UNITS_OVER_BOUND,
                RootRegionGraphDiagnostic.SOURCE_RESOLUTION_FAILED,
            ),
        )


# --- F. Scale law of the measured content reservation ----------------


@pytest.mark.parametrize("mode", MODES)
def test_f_scale_ready_and_honest_refusal(mode: AdmissionMode) -> None:
    """F1: The measured scale law of the R-owned content
    reservations (the source-pinned moving baselines as permanent
    controls; the source BYTES are the measured input, not
    hardcoded work values): for the root-only bootstrap (envelope
    source; the Responses envelope bootstrap carries no read-
    endpoint parameter, on both modes) and the mixed-region shape
    (read_region source, no singleton, on both read endpoints),
    32768 and 65536 root-member UTF-8 bytes derive READY; 131072
    refuses the typed R total over-bound with the HONEST stage
    evidence: the root-only crossing lands in the FINAL output
    reservation AFTER the F phase (which counts BOUNDED operations
    in its separate source-byte/stage domain, never per-byte), so
    the actual F ok is retained; the mixed crossing lands in the
    CHARGED SELECTED-SOURCE RESOLUTION (the source-constructor
    content-verification reservation, after the selected-root
    slice), so F never runs and no F result is published.  The
    R-owned per-content reservations are a separate new R policy.
    No cap is raised and no positive is faked."""
    for nbytes in (32768, 65536, 131072):
        ns_b, s_b = r_bootstrap(mode, f"r-f1ro-{mode.value}-{nbytes}", root_body="x" * nbytes)
        r_b = derive_root_region_graph(s_b, ns_b)
        if nbytes <= 65536:
            assert r_b.outcome is RootRegionGraphOutcome.READY
            assert r_b.resolved_source is not None
            assert r_b.resolved_source.kind == "envelope"
            assert r_b.resolved_source.root_byte_length == nbytes
            assert r_b.resolved_source.root_digest == sha256_hex("x" * nbytes)
            assert r_b.f_result is not None and r_b.f_result.outcome is CurrentGraphOutcome.OK
            assert r_b.state is s_b
        else:
            assert r_b.outcome is RootRegionGraphOutcome.REFUSED
            assert r_b.diagnostics == (RootRegionGraphDiagnostic.WORK_UNITS_OVER_BOUND,)
            assert r_b.resolved_source is None
            assert r_b.f_result is not None and r_b.f_result.outcome is CurrentGraphOutcome.OK
            assert r_b.q_result is not None
            assert r_b.q_result.outcome is RootRegionCurrentnessOutcome.READY
            assert r_b.state is s_b
    for endpoint in ENDPOINTS:
        for nbytes in (32768, 65536, 131072):
            ns_m, s_m0 = r_bootstrap(mode, f"r-f1mx-{mode.value}-{endpoint}-{nbytes}")
            t1 = r_issue(s_m0, ns_m, "m1", endpoint, (CAUSAL_ROOT_FACT,), MIX_CMD)
            assert t1.outcome.value == "accepted", t1.diagnostics
            s_m = r_observe(
                t1.state,
                ns_m,
                (read_request(endpoint, "m1", _mixed_body(A_TEXT, MARK, "x" * nbytes), MIX_CMD),),
            ).state
            r_m = derive_root_region_graph(s_m, ns_m)
            if nbytes <= 65536:
                assert r_m.outcome is RootRegionGraphOutcome.READY
                assert r_m.resolved_source is not None
                assert r_m.resolved_source.kind == "read_region"
                assert r_m.resolved_source.root_byte_length == nbytes
                assert r_m.f_result is not None and r_m.f_result.outcome is CurrentGraphOutcome.OK
                assert r_m.state is s_m
            else:
                assert r_m.outcome is RootRegionGraphOutcome.REFUSED
                assert r_m.diagnostics == (RootRegionGraphDiagnostic.WORK_UNITS_OVER_BOUND,)
                assert r_m.resolved_source is None
                assert r_m.f_result is None
                assert r_m.q_result is not None
                assert r_m.q_result.outcome is RootRegionCurrentnessOutcome.READY
                assert r_m.state is s_m


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_f_multi_dependency_history_scale(
    mode: AdmissionMode, endpoint: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    """F2: The multiple-dependency / version-history shape at the
    32768 root-member UTF-8 byte scale (both modes, both
    endpoints, no singleton): the genuine version-owned
    withdrawal, surviving alternate, cycle-only disappearance and
    old-bytes revert laws (the B5 law at substantial size) hold at
    every phase, with the ACTUAL measured R/Q/P/F costs and the
    declared stage byte domain (the counters and the ordinary
    graph law are DISTINCT assertions).  The nonroot prefix is
    Unicode (character/byte distinct); the root members are
    exactly 32768 ASCII bytes each.  No generic
    throughput/runtime claim."""
    header1 = "Follow `A.md` and `X.md`.\n"
    header2 = "Follow `X.md`.\n"
    v1 = header1 + "x" * (32768 - len(header1))
    v2 = header2 + "x" * (32768 - len(header2))
    assert len(v1.encode("utf-8")) == 32768 and len(v2.encode("utf-8")) == 32768
    x_new = "Follow `Replacement.md`.\n"
    prefix = "Synthetic pr\u00e9fix nonroot.\n"
    assert len(prefix.encode("utf-8")) > len(prefix)  # nonroot prefix is not ASCII
    cmd = f"cat Note.md && echo '{MARK}' && cat AGENTS.md"
    ns, state = r_bootstrap(mode, f"r-f2-{mode.value}-{endpoint}", root_body=v1)

    def read(st: Any, cid: str, path: str, body: str, frontier: tuple[Any, ...]) -> Any:
        issued = r_issue(st, ns, cid, endpoint, frontier, f"cat {path}")
        assert issued.outcome.value == "accepted", issued.diagnostics
        obs = r_observe(issued.state, ns, (read_request(endpoint, cid, body, f"cat {path}"),))
        assert obs.outcome.value == "accepted", obs.diagnostics
        return obs.state

    state = read(state, "a", "A.md", "Follow `Cycle1.md` and `Target.md`.\n", (CAUSAL_ROOT_FACT,))
    state = read(state, "x", "X.md", "Follow `Target.md`.\n", (CAUSAL_ROOT_FACT,))
    state = read(state, "cycle1", "Cycle1.md", "Follow `Cycle2.md`.\n", (CAUSAL_ROOT_FACT,))
    state = read(state, "cycle2", "Cycle2.md", "Follow `Cycle1.md`.\n", (CAUSAL_ROOT_FACT,))
    state = read(
        state, "target", "Target.md", "Synthetic target governance.\n", (CAUSAL_ROOT_FACT,)
    )

    # --- Actual ledger measurement (class-preserving wrappers). ---
    r_ledgers: list[Any] = []
    q_ledgers: list[Any] = []
    f_ledgers: list[Any] = []
    stage_ledgers: list[Any] = []

    def install(cls: Any, bucket: list[Any]) -> None:
        orig_init = cls.__init__

        def counting_init(self: Any, *args: Any, **kwargs: Any) -> None:
            orig_init(self, *args, **kwargs)
            bucket.append(self)

        monkeypatch.setattr(cls, "__init__", counting_init)

    install(_ROuter, r_ledgers)
    install(_RQOuter, q_ledgers)
    install(_RFOuter, f_ledgers)
    install(_StageLedger, stage_ledgers)
    p_count = {"n": 0}
    orig_unit = _HOuter.unit

    def counting_unit(self: Any, *args: Any, **kwargs: Any) -> bool:
        allowed = orig_unit(self, *args, **kwargs)
        if allowed:
            p_count["n"] += 1
        return allowed

    monkeypatch.setattr(_HOuter, "unit", counting_unit)

    def reset_counters() -> None:
        r_ledgers.clear()
        q_ledgers.clear()
        f_ledgers.clear()
        stage_ledgers.clear()
        p_count["n"] = 0

    # Phase 1 (v1 root): the full dependency shape is READY at
    # least depths, nothing current-unreachable.
    reset_counters()
    r1 = _r(state, ns)
    assert r1.outcome is RootRegionGraphOutcome.READY
    assert r1.resolved_source is not None
    assert r1.f_result is not None
    assert r1.f_result.overlay is not None
    n1 = _nodes(r1.f_result.overlay)
    assert r1.resolved_source.root_text == v1
    assert n1["A.md"].depth == 1 and n1["X.md"].depth == 1
    assert n1["Target.md"].depth == 2
    assert n1["Cycle1.md"].depth == 2 and n1["Cycle2.md"].depth == 3
    assert r1.f_result.overlay.unreachable_current_paths == ()
    # Phase 2: the genuinely NEW region root (v2) drops the A.md
    # branch at substantial size; the measured cost snapshot lands
    # on this phase.
    issued = r_issue(state, ns, "root2", endpoint, (CAUSAL_ROOT_FACT,), cmd)
    assert issued.outcome.value == "accepted"
    state = r_observe(
        issued.state,
        ns,
        (read_request(endpoint, "root2", _mixed_body(prefix, MARK, v2), cmd),),
    ).state
    root2 = next(o for o in state.d_state.occurrences if o.call_id == "root2")
    reset_counters()
    r2 = _r(state, ns)
    _assert_ready_bindings(r2, state, v2)
    assert r2.resolved_source is not None
    assert r2.resolved_source.occurrence is not None
    assert r2.resolved_source.proof is not None
    assert r2.resolved_source.kind == "read_region"
    assert r2.resolved_source.occurrence is root2
    assert r2.resolved_source.proof is root2.proof
    assert r2.f_result is not None
    assert r2.f_result.overlay is not None
    n2 = _nodes(r2.f_result.overlay)
    for gone in ("A.md", "Cycle1.md", "Cycle2.md"):
        assert gone not in n2
    assert {
        "A.md",
        "Cycle1.md",
        "Cycle2.md",
        "Note.md",
    } <= set(r2.f_result.overlay.unreachable_current_paths)
    assert n2["X.md"].depth == 1
    assert n2["Target.md"].depth == 2  # surviving alternate via X.md
    # The measured costs and the declared stage byte domain
    # (counters and the ordinary graph law are distinct
    # assertions).
    assert (
        0
        < p_count["n"]
        < max(i.work_spent for i in q_ledgers)
        < max(i.work_spent for i in r_ledgers)
        <= RootRegionGraphBounds().max_total_work_units
    )
    assert 0 < max(i.work_spent for i in f_ledgers) < max(i.work_spent for i in r_ledgers)
    st = stage_ledgers[-1]
    assert st.work_spent > 0
    assert st.nodes_spent == len(r2.f_result.overlay.nodes)
    assert st.edges_spent == len(r2.f_result.overlay.edges)
    assert st.bytes_spent > 0
    assert st.diag_spent == 0
    # Phase 3: a genuine nonroot X.md version change at this scale
    # withdraws Target.md and grants Replacement.md: the ACTUAL
    # supplier ownership moves to the new X.md digest.
    x_old = next(o for o in state.d_state.occurrences if o.call_id == "x")
    issued = r_issue(
        state, ns, "xnew", endpoint, (x_old.occurrence_id, root2.occurrence_id), "cat X.md"
    )
    assert issued.outcome.value == "accepted", issued.diagnostics
    state = r_observe(issued.state, ns, (read_request(endpoint, "xnew", x_new, "cat X.md"),)).state
    r3 = _r(state, ns)
    _assert_ready_bindings(r3, state, v2)
    assert r3.f_result is not None
    assert r3.f_result.overlay is not None
    n3 = _nodes(r3.f_result.overlay)
    assert "Target.md" not in n3
    assert "Target.md" in r3.f_result.overlay.unreachable_current_paths
    assert n3["Replacement.md"].depth == 2
    assert any(
        s.kind is CurrentGraphSupplierKind.SOURCE
        and s.path == "X.md"
        and s.digest == sha256_hex(x_new)
        for s in r3.f_result.overlay.suppliers
    )
    # Phase 4: a genuine old-bytes region REVERT restores the v1
    # root at substantial size: the cycle and Target.md come back
    # at their least derivation depths and the retained alternate
    # (Replacement.md) stays reachable under the new X.md.
    x_new_occ = next(o for o in state.d_state.occurrences if o.call_id == "xnew")
    issued = r_issue(state, ns, "revert", endpoint, (x_new_occ.occurrence_id,), cmd)
    assert issued.outcome.value == "accepted", issued.diagnostics
    state = r_observe(
        issued.state,
        ns,
        (read_request(endpoint, "revert", _mixed_body(prefix, MARK, v1), cmd),),
    ).state
    revert_occ = next(o for o in state.d_state.occurrences if o.call_id == "revert")
    r4 = _r(state, ns)
    _assert_ready_bindings(r4, state, v1)
    assert r4.resolved_source is not None
    assert r4.resolved_source.occurrence is not None
    assert r4.resolved_source.proof is not None
    assert r4.resolved_source.occurrence is revert_occ
    assert r4.resolved_source.proof is revert_occ.proof
    assert r4.f_result is not None
    assert r4.f_result.overlay is not None
    n4 = _nodes(r4.f_result.overlay)
    assert n4["A.md"].depth == 1 and n4["X.md"].depth == 1
    assert n4["Target.md"].depth == 2
    assert n4["Cycle1.md"].depth == 2 and n4["Cycle2.md"].depth == 3
    assert n4["Replacement.md"].depth == 2
    # Only the never-referenced Note.md stays current-unreachable.
    assert r4.f_result.overlay.unreachable_current_paths == ("Note.md",)
    # The stable R scope key carries the ACTUAL advancing revision.
    assert r1.scope_key == r2.scope_key == r3.scope_key == r4.scope_key
    assert r1.revision < r2.revision < r3.revision < r4.revision


# --- G. Invariants, privacy and purity --------------------------------


@pytest.mark.parametrize("mode", MODES)
def test_g_idempotent_derivation_and_scope_key(mode: AdmissionMode) -> None:
    """G1: The derivation is pure and idempotent: repeated
    derivation on the SAME state yields fresh results with
    identical canonical serialization (pure data proof, NOT a
    wire-byte claim) with the EXACT state retained; the stable
    scope key binds the actual lineage key + R/Q/F/E
    contract/policy + EVERY effective bound set + the actual
    graph version -- NOT the carried revision (a GENUINE accepted
    transition that advances the carried revision by one keeps the
    same scope key, and a revision-tampered state changes the
    carried revision but not the scope key); a rejected input
    scope characterizes the derivation in the default domain (same
    scope key) and distinct R bounds yield a distinct scope
    key."""
    ns, state = _e_audit_state(mode, f"r-g1-{mode.value}")
    ra = derive_root_region_graph(state, ns)
    rb = derive_root_region_graph(state, ns)
    assert ra is not rb
    assert ra.outcome is RootRegionGraphOutcome.READY
    assert ra.model_dump_json() == rb.model_dump_json()
    assert ra.state is state and rb.state is state
    assert (
        ra.scope_key
        == rb.scope_key
        == root_region_graph_scope_key(
            state.lineage_key,
            ROOT_REGION_GRAPH_CONTRACT_VERSION,
            ROOT_REGION_GRAPH_POLICY_VERSION,
            RootRegionGraphBounds(),
            RootRegionCurrentnessBounds(),
            CurrentGraphBounds(),
            CurrentnessBounds(),
            ns.graph_version,
        )
    )
    # A rejected input scope characterizes the derivation in the
    # DEFAULT domain: the same state lineage key and default
    # bounds.
    identity2 = RequestIdentity(
        principal="g1-other-principal",
        session="s",
        repository="r",
        route="x",
    )
    admission2 = make_bundle_admission_namespace(
        identity2,
        model_identity="synthetic-r-model",
        config_fingerprint=FINGERPRINT,
        workspace=WORKSPACE,
        mode=mode,
    )
    ns_foreign = make_root_region_lineage_namespace(admission2, f"r-g1-{mode.value}")
    foreign = derive_root_region_graph(state, ns_foreign)
    assert foreign.outcome is RootRegionGraphOutcome.REFUSED
    assert foreign.scope_key == ra.scope_key
    # Distinct R bounds yield a distinct scope key.
    strict = RootRegionGraphBounds(max_total_work_units=65536, max_diagnostics=1)
    rs = derive_root_region_graph(state, ns, strict)
    assert rs.outcome is RootRegionGraphOutcome.READY
    assert rs.scope_key != ra.scope_key
    assert rs.scope_key == root_region_graph_scope_key(
        state.lineage_key,
        ROOT_REGION_GRAPH_CONTRACT_VERSION,
        ROOT_REGION_GRAPH_POLICY_VERSION,
        strict,
        RootRegionCurrentnessBounds(),
        CurrentGraphBounds(),
        CurrentnessBounds(),
        ns.graph_version,
    )
    # A GENUINE accepted transition (an extra legitimate
    # observation advances the carried revision by one) keeps the
    # SAME stable scope key: the key binds the actual scope
    # identity, NOT the carried revision.
    s_next = q_observe(state, ns, "responses", "g1-next", A_TEXT + B_TEXT, NONROOT_CMD)
    assert s_next.revision == state.revision + 1
    rn = derive_root_region_graph(s_next, ns)
    assert rn.outcome is RootRegionGraphOutcome.READY
    assert rn.resolved_source is not None
    assert rn.resolved_source.root_text == "Cap root.\n"
    assert rn.revision == s_next.revision
    assert rn.scope_key == ra.scope_key
    # A changed CARRIED revision (the 1:1 D law broken) still
    # characterizes the same stable scope key.
    bad_rev = state.model_copy(update={"revision": state.revision + 1})
    rb2 = derive_root_region_graph(bad_rev, ns)
    assert rb2.outcome is RootRegionGraphOutcome.REFUSED
    assert rb2.revision == bad_rev.revision
    assert rb2.scope_key == ra.scope_key


@pytest.mark.parametrize("mode", MODES)
def test_g_privacy_repr_canaries(mode: AdmissionMode) -> None:
    """G2: Operational reprs stay fixed non-echoing: a distinct
    ROOT body canary, an opaque body canary, a DISTINCT known
    NONROOT source canary, a distinct call ID and the identity
    canaries are all absent from every R str/repr surface (result,
    retained Q result, carried P selection, uncertainty witness);
    the witness's private references render as the fixed
    placeholder; the fixed malformed-input operational exception
    carries no canary in str/repr -- including when the malformed
    input is a REAL canary-bearing state with an actual O1 field
    malformed (copied revision=True: the shape fence rejects
    bool-as-int before any work), not only a canary-free object
    (whose exception non-echo alone is vacuous for retained
    source)."""
    root_canary = "GROOT-CANARY-018R"
    body_canary = "GBOD-CANARY-018R"
    nonroot_canary = "GNONROOT-CANARY-018R"
    call_id = "g-call-018r"
    identity = RequestIdentity(
        principal="g-priv-principal",
        session="g-priv-session",
        repository="g-priv-repository",
        route="g-priv-route",
    )
    ns, s0 = r_bootstrap(
        mode,
        f"r-g2-{mode.value}",
        root_body=f"Synthetic root. {root_canary}",
        identity=identity,
        model_identity="synthetic-r-model",
    )
    body = f"Unknown root constituent. {body_canary}\n" + A_TEXT
    # The genuine anchor law (the C9 pattern): the observation
    # first (unissued, unanchored), then issuance ALONE still
    # never anchors, and only the matching delayed receipt
    # activates the retained occurrence.
    s2 = r_observe(s0, ns, (read_request("responses", call_id, body, BOUNDARYLESS_CMD),)).state
    t1 = r_issue(s2, ns, call_id, "responses", (CAUSAL_ROOT_FACT,), BOUNDARYLESS_CMD)
    assert t1.outcome.value == "accepted", t1.diagnostics
    t3 = r_receipt(t1.state, ns, call_id, "responses", (CAUSAL_ROOT_FACT,), BOUNDARYLESS_CMD)
    state = t3.state
    # A DISTINCT known NONROOT source: an accepted nonroot read
    # whose retained body carries the canary must not leak into any
    # R surface.
    t_nr = r_observe(
        state,
        ns,
        (
            read_request(
                "responses",
                "g-nr",
                A_TEXT + nonroot_canary + "\n" + B_TEXT,
                NONROOT_CMD,
            ),
        ),
    ).state
    r = derive_root_region_graph(t_nr, ns)
    assert r.outcome is RootRegionGraphOutcome.ROOT_CURRENTNESS_UNPROVEN
    q = r.q_result
    assert q is not None
    assert len(q.uncertainty_witnesses) == 1
    surfaces = [repr(r), str(r), repr(q), str(q)]
    for w in q.uncertainty_witnesses:
        surfaces += [repr(w), str(w)]
    for d in q.diagnostics:
        surfaces += [repr(d), str(d)]
    assert q.p_selection is not None
    surfaces += [repr(q.p_selection), str(q.p_selection)]
    canaries = (
        root_canary,
        body_canary,
        nonroot_canary,
        call_id,
        identity.principal,
        identity.session,
        identity.repository,
        identity.route,
        "synthetic-r-model",
    )
    for surface in surfaces:
        for canary in canaries:
            assert canary not in surface
    assert PRIVATE_ID_PLACEHOLDER in repr(q.uncertainty_witnesses[0])
    # The fixed malformed-input operational exception carries no
    # canary in str/repr -- including a REAL canary-bearing state
    # with an actual O1 field malformed.
    with pytest.raises(ValueError, match="actual bounded state record") as excinfo:
        # Intentional malformed-input negative: a non-state object.
        derive_root_region_graph(object(), ns)  # type: ignore[arg-type]
    for surface in (str(excinfo.value), repr(excinfo.value)):
        for canary in canaries:
            assert canary not in surface
    bad_state = state.model_copy(update={"revision": True})
    with pytest.raises(ValueError, match="actual bounded state record") as excinfo2:
        derive_root_region_graph(bad_state, ns)
    for surface in (str(excinfo2.value), repr(excinfo2.value)):
        for canary in canaries:
            assert canary not in surface


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_g_no_host_io_on_public_paths(
    mode: AdmissionMode, endpoint: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    """G3: No host IO anywhere on the R public surface.

    Fixture and import setup happen BEFORE the traps open; the
    traps (the closed 24-facility surface) then cover the whole
    operation on the SAME legitimate state: factory, bootstrap,
    issuance, observation, receipt, validation, selection and the
    R derivation over READY / UNPROVEN / ROOT_AUTHORITY_CONFLICT
    (actual P conflict) / REFUSED (foreign scope, over-bound,
    version, malformed bounds and actual P validation problem) and
    the malformed-state error outcomes.  The ACTUAL prebuilt
    request object is passed to the public observation.  Every R
    str/repr surface must be free of the canaries and the original
    request payloads must be unchanged afterwards."""
    marker = "PURITY-MARKER-018R"
    root_body = "PRIVATE-ROOT-CONTENT-018R. Read `A.md`."
    new_root = "PRIVATE-NEW-CONTENT-018R"
    new_body = f"Ordinary A.\n{marker}\n{new_root}."
    opaque_body = "Unknown root constituent. PRIVATE-OPAQUE-018R\n" + A_TEXT
    call_id = "purity-call-018r"
    call_id2 = "purity-call2-018r"
    identity = RequestIdentity(
        principal="purity-principal-018r",
        session="purity-session-018r",
        repository="purity-repository-018r",
        route="purity-route-018r",
    )
    canaries = (
        identity.principal,
        identity.session,
        identity.repository,
        identity.route,
        "purity-model-018r",
        "purity-lineage-018r",
        call_id,
        call_id2,
        marker,
        root_body,
        new_root,
        "PRIVATE-OPAQUE-018R",
    )
    cmd = f"cat A.md && echo '{marker}' && cat AGENTS.md"
    root = rooted(root_body)
    request = read_request(endpoint, call_id, new_body, cmd)
    opaque_request = read_request(endpoint, call_id2, opaque_body, BOUNDARYLESS_CMD)
    originals = [json.dumps(q.payload, sort_keys=True) for q in (root, request, opaque_request)]
    calls: list[str] = []

    def trap(label: str) -> Any:
        def refused(*trap_args: Any, **trap_kwargs: Any) -> Any:
            calls.append(label)
            raise AssertionError("forbidden host IO: " + label)

        return refused

    for module, name in _host_io_facilities():
        monkeypatch.setattr(module, name, trap(module.__name__ + "." + name))

    try:
        admission = make_bundle_admission_namespace(
            identity,
            model_identity="purity-model-018r",
            config_fingerprint="c" * 64,
            workspace="/work",
            mode=mode,
        )
        ns = make_root_region_lineage_namespace(admission, "purity-lineage-018r")
        t0 = bootstrap_root_region_lineage((root,), ns)
        assert t0.outcome.value == "accepted", t0.diagnostics
        s1 = register_root_region_issuance(
            t0.state,
            ns,
            call_id,
            endpoint,
            "exec_command",
            json.dumps({"cmd": cmd}),
            (CAUSAL_ROOT_FACT,),
            t0.state.revision,
        )
        assert s1.outcome.value == "accepted", s1.diagnostics
        # The ACTUAL prebuilt request object is passed to the public
        # observation (so the unchanged-payload assertion below covers
        # the object the API really consumed).
        t2 = observe_root_region_lineage(s1.state, ns, s1.state.revision, (request,))
        assert t2.outcome.value == "accepted", t2.diagnostics
        s2 = t2.state
        assert validate_root_region_lineage_state(s2, ns.root_lineage_bounds) is None
        assert select_current_root_region(s2, ns).outcome is RootSelectionOutcome.OK
        r_ready = derive_root_region_graph(s2, ns)
        assert r_ready.outcome is RootRegionGraphOutcome.READY
        # Non-ready: the late opaque row-4 activation on the SAME state
        # tree (issue then receipt; the genuine anchor law).
        s3 = observe_root_region_lineage(s2, ns, s2.revision, (opaque_request,))
        assert s3.outcome.value == "accepted", s3.diagnostics
        s4 = register_root_region_issuance(
            s3.state,
            ns,
            call_id2,
            endpoint,
            "exec_command",
            json.dumps({"cmd": BOUNDARYLESS_CMD}),
            (CAUSAL_ROOT_FACT,),
            s3.state.revision,
        )
        assert s4.outcome.value == "accepted", s4.diagnostics
        t4 = register_root_region_receipt(
            s4.state,
            ns,
            call_id2,
            endpoint,
            "exec_command",
            json.dumps({"cmd": BOUNDARYLESS_CMD}),
            (CAUSAL_ROOT_FACT,),
            s4.state.revision,
        )
        assert t4.outcome.value == "accepted", t4.diagnostics
        r_unproven = derive_root_region_graph(t4.state, ns)
        assert r_unproven.outcome is RootRegionGraphOutcome.ROOT_CURRENTNESS_UNPROVEN
        assert r_unproven.q_result is not None
        assert len(r_unproven.q_result.uncertainty_witnesses) == 1
        # Refusals: foreign scope, over-bound, malformed-state error.
        ns_foreign = make_root_region_lineage_namespace(admission, "purity-lineage-other")
        r_foreign = derive_root_region_graph(s2, ns_foreign)
        assert r_foreign.outcome is RootRegionGraphOutcome.REFUSED
        r_over = derive_root_region_graph(s2, ns, RootRegionGraphBounds(max_total_work_units=50))
        assert r_over.outcome is RootRegionGraphOutcome.REFUSED
        with pytest.raises(ValueError, match="actual bounded state record"):
            # Intentional malformed-input negative: a non-state object.
            derive_root_region_graph(object(), ns)  # type: ignore[arg-type]
        # Actual public authority CONFLICT (two incomparable known
        # region maxima, the accepted P conflict fixture): the ACTUAL P
        # conflict maps to the R ROOT_AUTHORITY_CONFLICT outcome with
        # the actual P selection retained and no source or F.
        c_ns, c_state, _cf1, _cf2 = _two_sibling_regions(
            mode, f"purity-conflict-{mode.value}-{endpoint}", endpoint
        )
        assert (
            select_current_root_region(c_state, c_ns).outcome
            is RootSelectionOutcome.ROOT_CONTENT_CONFLICT
        )
        r_conflict = derive_root_region_graph(c_state, c_ns)
        assert r_conflict.outcome is RootRegionGraphOutcome.ROOT_AUTHORITY_CONFLICT
        assert r_conflict.resolved_source is None and r_conflict.f_result is None
        assert r_conflict.q_result is not None
        assert r_conflict.q_result.p_selection is not None
        assert r_conflict.q_result.p_selection.outcome is RootSelectionOutcome.ROOT_CONTENT_CONFLICT
        assert r_conflict.q_result.p_selection.selected_source_digest is None
        assert r_conflict.q_result.usable_selected_source_digest is None
        # Actual version refusal (the coherent v2 rekey, c3 pattern)
        # and bad-bounds (raw override dict) and actual P validation
        # refusal (forged region flag) all run under the traps.
        v2 = "cache-root-region-lineage/v2"
        k2 = _lineage_key(
            c_ns.history_key, v2, ROOT_REGION_LINEAGE_POLICY_VERSION, c_ns.root_lineage_bounds
        )
        c_ns_v2 = c_ns.model_copy(update={"contract_version": v2, "lineage_key": k2})
        c_state_v2 = c_state.model_copy(update={"lineage_key": k2})
        r_version = derive_root_region_graph(c_state_v2, c_ns_v2)
        assert r_version.outcome is RootRegionGraphOutcome.REFUSED
        # The version fence refusal is carried through the ACTUAL
        # same-run Q channel (the D-verified law): no R-own
        # diagnostics, the fixed Q version reason.
        assert r_version.diagnostics == ()
        assert r_version.resolved_source is None and r_version.f_result is None
        assert r_version.q_result is not None
        assert r_version.q_result.outcome is RootRegionCurrentnessOutcome.REFUSED
        assert [d.value for d in r_version.q_result.diagnostics] == ["version_unsupported"]
        r_badbounds = derive_root_region_graph(
            c_state,
            c_ns,
            {"max_total_work_units": 1, "max_diagnostics": 1},  # type: ignore[arg-type]
        )
        assert r_badbounds.outcome is RootRegionGraphOutcome.REFUSED
        assert [d.value for d in r_badbounds.diagnostics] == ["malformed_binding"]
        read_fact = next(f for f in c_state.root_facts if f.provenance.kind == "read_region")
        forged = read_fact.model_copy(update={"issued": False})
        c_bad = c_state.model_copy(
            update={
                "root_facts": tuple(forged if x is read_fact else x for x in c_state.root_facts)
            }
        )
        r_pval = derive_root_region_graph(c_bad, c_ns)
        assert r_pval.outcome is RootRegionGraphOutcome.REFUSED
        assert r_pval.q_result is not None
        assert r_pval.q_result.p_validation_problem is RootLineageLimitation.MALFORMED_BINDING
        assert r_pval.q_result.p_selection is None
        # Privacy on the R surfaces.
        surfaces = [
            repr(r_ready),
            repr(r_unproven),
            repr(r_foreign),
            repr(r_over),
            repr(r_conflict),
            repr(r_version),
            repr(r_badbounds),
            repr(r_pval),
            repr(r_conflict.q_result.p_selection),
        ]
        for w in r_unproven.q_result.uncertainty_witnesses:
            surfaces.append(repr(w))
        for surface in surfaces:
            for canary in canaries:
                assert canary not in surface
        # The original request payloads are unchanged.
        assert [
            json.dumps(q.payload, sort_keys=True) for q in (root, request, opaque_request)
        ] == originals
        assert calls == []
    finally:
        # Guaranteed trap restore BEFORE any error
        # formatting: the traps are a strictly scoped
        # test window, never a session-wide state.
        monkeypatch.undo()


@pytest.mark.parametrize("mode", MODES)
def test_g_fixed_private_errors_omit_canaries(mode: AdmissionMode) -> None:
    """G4: The fixed private constructor errors (the M09 closed
    kind variant, the M10 nested field deletion, the M11 detached
    extra-witness forge) carry NO canary content in str/repr on a
    genuine READY fixture whose retained root text and nonroot
    member actually carry the canaries."""
    root_canary = "GROOT4-CANARY-018R"
    nonroot_canary = "GNONROOT4-CANARY-018R"
    _ns, s0 = r_bootstrap(mode, f"r-g4-{mode.value}")
    t1 = r_issue(s0, _ns, "m1", "responses", (CAUSAL_ROOT_FACT,), MIX_CMD)
    assert t1.outcome.value == "accepted", t1.diagnostics
    state = r_observe(
        t1.state,
        _ns,
        (
            read_request(
                "responses",
                "m1",
                _mixed_body(A_TEXT + nonroot_canary, MARK, f"{root_canary} region root.\n"),
                MIX_CMD,
            ),
        ),
    ).state
    r = _r(state, _ns)
    assert r.outcome is RootRegionGraphOutcome.READY
    assert r.resolved_source is not None
    assert r.resolved_source.root_text == f"{root_canary} region root.\n"
    canaries = (root_canary, nonroot_canary)
    # M09: the unknown closed variant (fixed message before
    # dispatch or interpolation).
    src_c = r.resolved_source.model_copy(update={"kind": "g-unknown-variant"})
    with pytest.raises(ValidationError) as e1:
        _d_reconstruct(r, resolved_source=src_c)
    for surface in (str(e1.value), repr(e1.value)):
        for canary in canaries:
            assert canary not in surface
    # M10: the nested field deletion.
    assert r.q_result is not None
    assert r.q_result.p_selection is not None
    sel = r.q_result.p_selection.model_copy()
    object.__delattr__(sel, "outcome")
    q_sel = r.q_result.model_copy(update={"p_selection": sel})
    with pytest.raises(ValidationError) as e2:
        _d_reconstruct(r, q_result=q_sel)
    for surface in (str(e2.value), repr(e2.value)):
        for canary in canaries:
            assert canary not in surface
    # M11: the detached EXTRA witness (the original retained fact
    # is kept in the tuple).
    fact = r.q_result.p_selection.witness_facts[0]
    extra = fact.model_copy(deep=True)
    forged_sel = r.q_result.p_selection.model_copy(update={"witness_facts": (fact, extra)})
    forged_q = r.q_result.model_copy(update={"p_selection": forged_sel})
    with pytest.raises(ValidationError) as e3:
        _d_reconstruct(r, q_result=forged_q)
    for surface in (str(e3.value), repr(e3.value)):
        for canary in canaries:
            assert canary not in surface

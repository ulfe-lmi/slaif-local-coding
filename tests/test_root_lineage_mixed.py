"""Durable original-API acceptance: root-aware MIXED observation (018-o).

The A-H actual-path matrix of the activated 018-o order, over BOTH
read endpoints and BOTH admission modes, exercised on the ACTUAL
retained 018-h state and namespace earned through the original
public D/H APIs (bootstrap, issuance, observation, receipt,
selection) plus ordinary public I (``derive_current_root_composition``)
on the SAME retained state.  The NEW pure operation
``observe_root_lineage_mixed`` acquires a proven mixed root member
whose digest is an independently authoritative known root version
(pre-batch) or is established by an INDEPENDENT authoritative
complete whole singleton root read in the SAME batch; a mixed read
never mints governing authority.  The OLD public
``observe_root_lineage`` keeps its EXACT post-refresh mixed refusal
law (never broadened).  No strategic-runtime dependency:
known-synthetic original API fixtures only; every oracle asserts the
exact typed outcome, the exact prior-state identity on refusal, the
original proof/anchor/occurrence identities and the fixed closed
diagnostics.
"""

from __future__ import annotations

import builtins
import json
from typing import Any

import pytest

from slaif_local_coding.constitution.bundles import (
    bundle_proof as bp_mod,
)
from slaif_local_coding.constitution.bundles import (
    causal_history as d_mod,
)
from slaif_local_coding.constitution.bundles import (
    root_lineage as rl_mod,
)
from slaif_local_coding.constitution.bundles.bundle_admission import (
    _key_canonical,
)
from slaif_local_coding.constitution.bundles.bundle_admission_models import (
    AdmissionMode,
)
from slaif_local_coding.constitution.bundles.bundle_proof_models import (
    BundleProof,
    BundleProofBounds,
)
from slaif_local_coding.constitution.bundles.causal_history import (
    _RootLineageContext,
)
from slaif_local_coding.constitution.bundles.causal_history_models import (
    CAUSAL_ROOT_FACT,
    CausalHistoryOutcome,
)
from slaif_local_coding.constitution.bundles.current_admission_models import (
    _entry_admission_namespace,
)
from slaif_local_coding.constitution.bundles.graph_models import _sha256_hex
from slaif_local_coding.constitution.bundles.observation_models import (
    Limitation,
)
from slaif_local_coding.constitution.bundles.root_lineage import (
    _HOuter,
    bootstrap_root_lineage,
    observe_root_lineage,
    observe_root_lineage_mixed,
    register_root_issuance,
    select_current_root,
)
from slaif_local_coding.constitution.bundles.root_lineage_models import (
    ROOT_LINEAGE_MIXED_OBSERVATION_VERSION,
    ROOT_LINEAGE_POLICY_VERSION,
    ReadRootProvenance,
    RootLineageBounds,
    RootLineageLimitation,
    RootLineageNamespace,
    RootLineageOutcome,
    RootSelectionOutcome,
    _lineage_key,
)
from tests.test_causal_history import (
    ENDPOINTS,
    MODES,
    ROOT_TEXT,
    read_request,
    root_request,
    sha256_hex,
)
from tests.test_current_root_composition import (
    _L as I_L,
)
from tests.test_current_root_composition import (
    _OUT as I_OUT,
)
from tests.test_current_root_composition import (
    assert_i_ok,
    assert_i_refused,
    derive,
    i_members_of,
    refreshed,
)
from tests.test_root_lineage import (
    ROOT_READ_ARGS,
    SIBLING_X,
    SIBLING_Y,
    SIBLING_Z,
    _min_accepted_cap,
    _terminal_only,
    _truncated_root_request,
    bootstrap,
    changed_root_envelope,
    h_ns,
    issue,
    occurrences,
    read_fact,
    root_chain,
)

# --- Module constants (known-synthetic original API fixtures) -----------

V2 = "Read `A.md` for the refresh."
V3 = "Read `A.md` after the refresh."
V4 = "Read `A.md` for the equal bytes."
A_TEXT = "Synthetic nonroot A.\n"
A2_TEXT = "Synthetic nonroot A second.\n"
B_TEXT = "Synthetic nonroot B.\n"
MARK = "ROOTSEP"
MARK2 = "OTHERSEP"
MIX_CMD = f"cat A.md && echo '{MARK}' && cat AGENTS.md"
MIXB_CMD = f"cat B.md && echo '{MARK2}' && cat AGENTS.md"
REPEAT_CMD = f"cat AGENTS.md && echo '{MARK}' && cat AGENTS.md"
REPEAT_OPAQUE_CMD = f"cat AGENTS.md && echo '{MARK}' && cat AGENTS.md && cat B.md"
BOUNDARYLESS_CMD = "cat A.md && cat AGENTS.md"
FOREIGN_ROOT = "Foreign root bytes 018o."
FOREIGN_ROOT2 = "Foreign root bytes 018o two."
CANARY = "canary-mixed-body-018o-9c2d"


def _mixed_body(a_text: str, root_body: str, mark: str = MARK) -> str:
    return f"{a_text}{mark}\n{root_body}"


def _issue(
    state: Any, ns: Any, cid: str, endpoint: str, parent_occ: str | tuple[str, ...], cmd: str
) -> Any:
    # A single parent ID or an ACTUAL flat tuple of parent IDs;
    # the frontier is never wrapped a second time (the D issuance
    # law takes the frozen parent frontier verbatim).
    frontier = (parent_occ,) if isinstance(parent_occ, str) else tuple(parent_occ)
    return issue(state, ns, cid, endpoint, frontier, args=json.dumps({"cmd": cmd}))


def _v2_state(
    mode: AdmissionMode, lineage: str, endpoint: str, bounds: Any = None
) -> tuple[Any, Any]:
    """Bootstrap + an ACTUAL issued singleton v2 refresh."""
    ns, s0 = bootstrap(mode, lineage, bounds=bounds)
    s1 = refreshed(s0, ns, "fresh-root", endpoint, V2)
    return ns, s1


def _assert_refused(
    t: Any, prior: Any, outcome: RootLineageOutcome, diags: tuple[Any, ...]
) -> None:
    assert t.outcome is outcome, (t.outcome, t.diagnostics)
    assert t.state is prior
    assert t.diagnostics == diags
    assert t.new_root_facts == ()
    assert t.revision_after == prior.revision


# --- A. Known pre-batch v2 mixed acquisition + I whole-bundle admission -


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_a_known_v2_mixed_acquired_i_whole_bundle(mode: AdmissionMode, endpoint: str) -> None:
    """A (018-o acceptance 1): bootstrap v1 -> issued singleton v2
    refresh -> an issued DESCENDANT mixed proven read containing v2
    (an independently authoritative pre-batch known version) with no
    new envelope.  The NEW operation accepts; the OLD public
    observation keeps refusing the same read; ordinary I admits the
    supported whole bundle with one governing root (v2), the mixed
    read mints no root fact, the original proof root binding stays at
    the immutable bootstrap, and the root entry carries the
    INDEPENDENT original-C canonical key."""
    # The new operation's contract surface pins its exact version.
    assert ROOT_LINEAGE_MIXED_OBSERVATION_VERSION == "root-lineage-mixed-observation/v1"
    ns, s1 = _v2_state(mode, "o-a", endpoint)
    fact = read_fact(s1, "fresh-root")
    # The OLD public observer keeps its exact post-refresh mixed
    # refusal (never broadened).
    to1 = _issue(s1, ns, "old-mix", endpoint, fact.provenance.occurrence_id, MIX_CMD)  # type: ignore[union-attr]
    assert to1.outcome is RootLineageOutcome.ACCEPTED
    to2 = observe_root_lineage(
        to1.state,
        ns,
        to1.state.revision,
        (read_request(endpoint, "old-mix", _mixed_body(A_TEXT, V2), MIX_CMD),),
    )
    _assert_refused(
        to2,
        to1.state,
        RootLineageOutcome.REFUSED_ROOT_CONFLICT,
        (RootLineageLimitation.COMPETING_ROOTS,),
    )
    # The NEW operation acquires the same mixed read.
    t1 = _issue(s1, ns, "m1", endpoint, fact.provenance.occurrence_id, MIX_CMD)  # type: ignore[union-attr]
    assert t1.outcome is RootLineageOutcome.ACCEPTED
    t2 = observe_root_lineage_mixed(
        t1.state,
        ns,
        t1.state.revision,
        (read_request(endpoint, "m1", _mixed_body(A_TEXT, V2), MIX_CMD),),
    )
    assert t2.outcome is RootLineageOutcome.ACCEPTED, t2.diagnostics
    s2 = t2.state
    # No new root fact for the mixed read; the v2 fact is unchanged.
    assert not any(
        f.provenance.kind == "read" and f.provenance.call_id == "m1" for f in s2.root_facts
    )
    assert read_fact(s2, "fresh-root") is not None
    assert len(s2.root_facts) == len(s1.root_facts)
    occ = occurrences(s2, "m1")[0]
    proof = occ.proof
    assert proof is not None
    assert len(proof.segments) == 2
    # The original proof ROOT BINDING stays at the immutable
    # bootstrap; the proven member digest is a source-content fact
    # with a different purpose.
    assert proof.root_digest == sha256_hex(ROOT_TEXT)
    root_seg = [
        sg
        for sg in proof.segments
        if proof.requested_members[sg.member_positions[0]].normalized == "AGENTS.md"
    ]
    assert len(root_seg) == 1
    assert root_seg[0].member_digest == sha256_hex(V2)
    # Selection is unchanged (v2, the read provenance).
    sel = select_current_root(s2, ns)
    assert sel.outcome is RootSelectionOutcome.OK
    assert sel.selected_source_digest == sha256_hex(V2)
    # Ordinary public I on the SAME retained state.
    r = derive(s2, ns)
    assert_i_ok(r, s2)
    assert r.graph.root_digest == sha256_hex(V2)  # type: ignore[union-attr]
    assert r.selected_root_provenance.kind == "read"  # type: ignore[union-attr]
    assert r.selected_root_provenance.call_id == "fresh-root"  # type: ignore[union-attr]
    adm = r.admission
    assert adm is not None
    members = i_members_of(adm)
    whole = members[("A.md", "AGENTS.md")]
    assert whole.proof is proof
    assert proof is not None
    assert whole.key_record.aggregate_source_digest == proof.source_digest

    # Independent original-C canonical keys: recompute each key
    # record's content key from its ACTUAL fields through the
    # accepted 018-c recipe (bundle_admission._key_canonical with
    # the actual accepted C inputs, the returned BYTES hashed once)
    # -- the mixed read changes nothing about the root entry.
    def _independent_c_key(kr: Any) -> str:
        return _sha256_hex(
            _key_canonical(
                _entry_admission_namespace(kr),
                kr.root_digest,
                kr.authority_class,
                kr.member_occurrences,
                kr.member_classes,
                kr.aggregate_source_digest,
                kr.ownership_groups,
            )
        )

    kr = adm.root_entry.key_record
    assert _independent_c_key(kr) == kr.content_key
    assert _independent_c_key(whole.key_record) == whole.key_record.content_key


# --- B. Same-batch independent singleton authority (all orders) --------


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_b_same_batch_singleton_v3_mixed_v3(mode: AdmissionMode, endpoint: str) -> None:
    """B (018-o acceptance 2): an ACTUAL independently issued
    singleton v3 refresh and a mixed v3 read in ONE observation
    batch, in BOTH request-order permutations, with and without the
    independently authorized changed v3 envelope alongside.  The
    singleton ALONE supplies the new authority (the mixed read mints
    no root fact); the original bindings are preserved; ordinary I
    produces the expected v3 graph/admission with the whole bundle
    admitted under one governing root."""
    ns, s1 = _v2_state(mode, "o-b", endpoint)
    body3 = _mixed_body(A_TEXT, V3)
    cases: list[tuple[str, ...]] = [
        ("v3r", "m3"),
        ("m3", "v3r"),
        ("env3", "v3r", "m3"),
        ("m3", "env3", "v3r"),
    ]
    for order in cases:
        ns_c, s1_c = _v2_state(mode, f"o-b-{'-'.join(order)}", endpoint)
        fact_c = read_fact(s1_c, "fresh-root")
        reqs: list[Any] = []
        for cid in order:
            if cid == "v3r":
                reqs.append(read_request(endpoint, "v3r", V3, "cat AGENTS.md"))
            elif cid == "m3":
                reqs.append(read_request(endpoint, "m3", body3, MIX_CMD))
            else:
                reqs.append(changed_root_envelope(V3))
        ti = _issue(s1_c, ns_c, "v3r", endpoint, fact_c.provenance.occurrence_id, "cat AGENTS.md")  # type: ignore[union-attr]
        assert ti.outcome is RootLineageOutcome.ACCEPTED
        if "m3" in order:
            tm = _issue(ti.state, ns_c, "m3", endpoint, fact_c.provenance.occurrence_id, MIX_CMD)  # type: ignore[union-attr]
            assert tm.outcome is RootLineageOutcome.ACCEPTED
            base = tm.state
        else:
            base = ti.state
        t = observe_root_lineage_mixed(base, ns_c, base.revision, tuple(reqs))
        assert t.outcome is RootLineageOutcome.ACCEPTED, (order, t.diagnostics)
        s = t.state
        # The singleton ALONE supplies the new authority fact.
        v3_fact = read_fact(s, "v3r")
        assert v3_fact.authority is True
        assert v3_fact.source_digest == sha256_hex(V3)
        assert not any(
            f.provenance.kind == "read" and f.provenance.call_id == "m3" for f in s.root_facts
        )
        # Ordinary I: the expected v3 graph/admission.
        r = derive(s, ns_c)
        assert_i_ok(r, s)
        assert r.graph.root_digest == sha256_hex(V3)  # type: ignore[union-attr]
        assert r.selected_root_provenance.call_id == "v3r"  # type: ignore[union-attr]
        members = i_members_of(r.admission)
        assert ("A.md", "AGENTS.md") in members
        # The mixed occurrence keeps its ORIGINAL bootstrap root
        # binding (no rebinding to v3).
        assert occurrences(s, "m3")[0].proof.root_digest == sha256_hex(ROOT_TEXT)


# --- C. Replay idempotence, later descendant, equal-byte witnesses -----


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_c_replay_idempotence_and_equal_byte_witnesses(mode: AdmissionMode, endpoint: str) -> None:
    """C (018-o acceptance 3): the mixed batch REPLAYS idempotently
    through the new operation (exact prior state, no revision
    advance, first provenance kept), then a later genuine descendant
    is observed through the ACTUAL resulting state with its causal
    parent binding, and two INCOMPARABLE equal-byte singleton
    witnesses are ALL retained without false semantic misses at the
    I boundary."""
    ns, s1 = _v2_state(mode, "o-c", endpoint)
    fact = read_fact(s1, "fresh-root")
    t1 = _issue(s1, ns, "m1", endpoint, fact.provenance.occurrence_id, MIX_CMD)  # type: ignore[union-attr]
    assert t1.outcome is RootLineageOutcome.ACCEPTED
    t2 = observe_root_lineage_mixed(
        t1.state,
        ns,
        t1.state.revision,
        (read_request(endpoint, "m1", _mixed_body(A_TEXT, V2), MIX_CMD),),
    )
    assert t2.outcome is RootLineageOutcome.ACCEPTED
    s2 = t2.state
    # Replay: idempotent no-op on the EXACT state.
    t3 = observe_root_lineage_mixed(
        s2,
        ns,
        s2.revision,
        (read_request(endpoint, "m1", _mixed_body(A_TEXT, V2), MIX_CMD),),
    )
    assert t3.outcome is RootLineageOutcome.REPLAYED
    assert t3.state is s2
    assert t3.diagnostics == ()
    assert t3.new_root_facts == ()
    assert occurrences(s2, "m1")[0] is occurrences(t3.state, "m1")[0]
    # A later genuine descendant through the ACTUAL resulting state:
    # the trusted frontier names the newly retained MIXED occurrence
    # m1 (causal parent binding through the legitimate resulting
    # state, never a synthetic or replaced anchor).
    m1_occ = occurrences(s2, "m1")[0]
    t4 = _issue(s2, ns, "d4", endpoint, m1_occ.occurrence_id, "cat AGENTS.md")
    assert t4.outcome is RootLineageOutcome.ACCEPTED
    t5 = observe_root_lineage_mixed(
        t4.state,
        ns,
        t4.state.revision,
        (read_request(endpoint, "d4", V4, "cat AGENTS.md"),),
    )
    assert t5.outcome is RootLineageOutcome.ACCEPTED
    s5 = t5.state
    d4_fact = read_fact(s5, "d4")
    assert d4_fact.authority is True  # via m1 -> v2 -> bootstrap
    # Ordinary I after the first V4 witness.
    r5 = derive(s5, ns)
    assert_i_ok(r5, s5)
    assert r5.graph.root_digest == sha256_hex(V4)  # type: ignore[union-attr]
    root_key5 = r5.admission.root_entry.content_key  # type: ignore[union-attr]
    sel5 = select_current_root(s5, ns)
    assert len(sel5.witness_facts) == 1
    assert sel5.witness_facts[0] is d4_fact
    # Two INCOMPARABLE equal-byte witnesses under the SAME intended
    # shared frontier (m1): neither dominates the other, ALL are
    # retained, no false semantic miss.
    t6 = _issue(s5, ns, "w1", endpoint, m1_occ.occurrence_id, "cat AGENTS.md")
    t7 = observe_root_lineage_mixed(
        t6.state,
        ns,
        t6.state.revision,
        (read_request(endpoint, "w1", V4, "cat AGENTS.md"),),
    )
    assert t7.outcome is RootLineageOutcome.ACCEPTED
    t8 = _issue(t7.state, ns, "w2", endpoint, m1_occ.occurrence_id, "cat AGENTS.md")
    t9 = observe_root_lineage_mixed(
        t8.state,
        ns,
        t8.state.revision,
        (read_request(endpoint, "w2", V4, "cat AGENTS.md"),),
    )
    assert t9.outcome is RootLineageOutcome.ACCEPTED
    s9 = t9.state
    sel = select_current_root(s9, ns)
    assert sel.outcome is RootSelectionOutcome.OK
    assert sel.selected_source_digest == sha256_hex(V4)
    witness_ids = {
        f.provenance.call_id
        for f in sel.witness_facts
        if isinstance(f.provenance, ReadRootProvenance)
    }
    assert witness_ids == {"d4", "w1", "w2"}
    assert all(f.source_digest == sha256_hex(V4) for f in sel.witness_facts)
    # Ordinary I after the equal-byte witness growth: the semantic
    # root/content keys stay EQUAL while the ORIGINAL witnesses grow
    # (identity, not digest or index order).
    r = derive(s9, ns)
    assert_i_ok(r, s9)
    assert r.graph.root_digest == sha256_hex(V4)  # type: ignore[union-attr]
    assert r.admission.root_entry.content_key == root_key5  # type: ignore[union-attr]
    assert len(sel.witness_facts) == 3
    assert {id(f) for f in sel.witness_facts} == {
        id(read_fact(s9, "d4")),
        id(read_fact(s9, "w1")),
        id(read_fact(s9, "w2")),
    }
    # S1 law: the H root facts are RE-DERIVED (model_copy) after every
    # accepted D transition, so the d4 fact object in the final state
    # need not be the SAME Python object captured from the earlier
    # state.  What IS required: the final selection exposes the ACTUAL
    # facts of the final state (asserted above), and the ORIGINAL read
    # provenance coordinates stay EXACTLY unchanged across states.
    d4_fact9 = read_fact(s9, "d4")
    assert isinstance(d4_fact9.provenance, ReadRootProvenance)
    assert isinstance(d4_fact.provenance, ReadRootProvenance)
    assert d4_fact9.source_digest == d4_fact.source_digest
    assert d4_fact9.source_byte_length == d4_fact.source_byte_length
    assert d4_fact9.provenance == d4_fact.provenance
    assert d4_fact9.provenance.kind == "read"
    assert d4_fact9.provenance.occurrence_id == d4_fact.provenance.occurrence_id
    assert d4_fact9.provenance.call_id == d4_fact.provenance.call_id
    assert d4_fact9.provenance.endpoint == d4_fact.provenance.endpoint
    assert d4_fact9.provenance.read_digest == d4_fact.provenance.read_digest
    assert d4_fact9.provenance.read_byte_length == d4_fact.provenance.read_byte_length
    # The ORIGINAL retained D occurrence/proof identity is required
    # and invariant across states (the D state is retained by
    # reference, never rewritten per witness).
    assert occurrences(s9, "m1")[0] is m1_occ
    assert occurrences(s9, "m1")[0].proof is m1_occ.proof
    d4_occ5 = occurrences(s5, "d4")[0]
    assert occurrences(s9, "d4")[0] is d4_occ5
    assert occurrences(s9, "d4")[0].proof is d4_occ5.proof
    if mode is AdmissionMode.LEAN:
        # The mixed-bundle isolated nonroot region keeps its
        # INDEPENDENT semantic content key across witness growth.
        m5 = i_members_of(r5.admission)
        m9 = i_members_of(r.admission)
        assert ("A.md",) in m5 and ("A.md",) in m9
        assert m5[("A.md",)].content_key == m9[("A.md",)].content_key
        assert m5[("A.md",)].key_record.aggregate_source_digest == sha256_hex(A_TEXT)


# --- D. Historical non-bootstrap v2 after v3 + I selected-digest -------


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_d_historical_v2_mixed_after_v3_i_exclusion(mode: AdmissionMode, endpoint: str) -> None:
    """D (018-o acceptance 4): a KNOWN historical NON-BOOTSTRAP v2
    mixed source observed AFTER v3 is legitimate source evidence for
    the new operation; ordinary I applies its ACTUAL selected-digest
    exclusion (the stale v2 root group supplies nothing), lean keeps
    the independently eligible isolated nonroot region and greedy
    keeps its whole-bundle law.  The OLD observer's post-refresh
    mixed refusal and the historical bootstrap-compatible mixed
    positive are preserved."""
    ns, s1 = _v2_state(mode, "o-d", endpoint)
    t = _issue(
        s1,
        ns,
        "v3r",
        endpoint,
        read_fact(s1, "fresh-root").provenance.occurrence_id,  # type: ignore[union-attr]
        "cat AGENTS.md",
    )
    assert t.outcome is RootLineageOutcome.ACCEPTED
    # Observe the v3 singleton read (the refresh) through the old op.
    t3 = observe_root_lineage(
        t.state,
        ns,
        t.state.revision,
        (read_request(endpoint, "v3r", V3, "cat AGENTS.md"),),
    )
    assert t3.outcome is RootLineageOutcome.ACCEPTED
    s3 = t3.state
    v3_occ = occurrences(s3, "v3r")[0].occurrence_id
    # NEW op: the historical v2 mixed read is source evidence.
    th = _issue(s3, ns, "mh", endpoint, v3_occ, MIX_CMD)
    assert th.outcome is RootLineageOutcome.ACCEPTED
    t_h = observe_root_lineage_mixed(
        th.state,
        ns,
        th.state.revision,
        (read_request(endpoint, "mh", _mixed_body(A2_TEXT, V2), MIX_CMD),),
    )
    assert t_h.outcome is RootLineageOutcome.ACCEPTED, t_h.diagnostics
    s_h = t_h.state
    assert not any(
        f.provenance.kind == "read" and f.provenance.call_id == "mh" for f in s_h.root_facts
    )
    # OLD op: the SAME post-refresh mixed read is still refused.
    to = _issue(s3, ns, "mh-old", endpoint, v3_occ, MIX_CMD)
    assert to.outcome is RootLineageOutcome.ACCEPTED
    t_o = observe_root_lineage(
        to.state,
        ns,
        to.state.revision,
        (read_request(endpoint, "mh-old", _mixed_body(A2_TEXT, V2), MIX_CMD),),
    )
    _assert_refused(
        t_o,
        to.state,
        RootLineageOutcome.REFUSED_ROOT_CONFLICT,
        (RootLineageLimitation.COMPETING_ROOTS,),
    )
    # NEW op: the historical bootstrap-compatible mixed positive is
    # preserved (same-bytes root member stays consistent).
    tb = _issue(s3, ns, "mb", endpoint, v3_occ, MIX_CMD)
    assert tb.outcome is RootLineageOutcome.ACCEPTED
    t_b = observe_root_lineage_mixed(
        tb.state,
        ns,
        tb.state.revision,
        (read_request(endpoint, "mb", _mixed_body(A2_TEXT, ROOT_TEXT), MIX_CMD),),
    )
    assert t_b.outcome is RootLineageOutcome.ACCEPTED, t_b.diagnostics
    # I: v3 selected; the stale v2 root group is excluded.
    r = derive(s_h, ns)
    assert_i_ok(r, s_h)
    assert r.graph.root_digest == sha256_hex(V3)  # type: ignore[union-attr]
    adm = r.admission
    members = i_members_of(adm)
    mh_occ = occurrences(s_h, "mh")[0]
    proof_h = mh_occ.proof
    assert isinstance(proof_h, BundleProof)
    for entry in adm.entries:  # type: ignore[union-attr]
        if entry.proof is proof_h:
            for pos in entry.admitted_segments:
                seg = proof_h.segments[pos]
                members_of_seg = [
                    proof_h.requested_members[m].normalized for m in seg.member_positions
                ]
                assert "AGENTS.md" not in members_of_seg or seg.member_digest == sha256_hex(V3)
    if mode is AdmissionMode.LEAN:
        # The independently eligible isolated nonroot region survives.
        assert ("A.md",) in members
        assert members[("A.md",)].proof is mh_occ.proof
        assert members[("A.md",)].key_record.aggregate_source_digest == sha256_hex(A2_TEXT)
    else:
        # Greedy keeps its whole-bundle law: no isolated segment.
        assert ("A.md",) not in members


# --- E. Conflicting known branches, mixed evidence, resolution ---------


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_e_conflicting_known_branches_mixed_evidence_resolves(
    mode: AdmissionMode, endpoint: str
) -> None:
    """E (018-o acceptance 5): with CONFLICTING known authoritative
    roots (two differing sibling branches), a mixed read matching a
    known branch is accepted as source evidence by the new operation
    while ordinary I stays explicitly conflicted with no ready
    output; a genuine singleton descendant of ALL branches still
    resolves the conflict to the sole maximal witness."""
    ns, s0 = bootstrap(mode, "o-e")
    t1 = _issue(s0, ns, "wx", endpoint, CAUSAL_ROOT_FACT, "cat AGENTS.md")
    assert t1.outcome is RootLineageOutcome.ACCEPTED
    t2 = observe_root_lineage_mixed(
        t1.state,
        ns,
        t1.state.revision,
        (read_request(endpoint, "wx", SIBLING_X, "cat AGENTS.md"),),
    )
    assert t2.outcome is RootLineageOutcome.ACCEPTED
    occ_x = occurrences(t2.state, "wx")[0]
    t3 = _issue(t2.state, ns, "wy", endpoint, CAUSAL_ROOT_FACT, "cat AGENTS.md")
    assert t3.outcome is RootLineageOutcome.ACCEPTED
    t4 = observe_root_lineage_mixed(
        t3.state,
        ns,
        t3.state.revision,
        (read_request(endpoint, "wy", SIBLING_Y, "cat AGENTS.md"),),
    )
    assert t4.outcome is RootLineageOutcome.ACCEPTED
    s_c = t4.state
    sel = select_current_root(s_c, ns)
    assert sel.outcome is RootSelectionOutcome.ROOT_CONTENT_CONFLICT
    assert sel.selected_source_digest is None
    # The mixed read matching a known branch: evidence retained.
    tm = _issue(s_c, ns, "mc", endpoint, occ_x.occurrence_id, MIX_CMD)
    assert tm.outcome is RootLineageOutcome.ACCEPTED
    t_m = observe_root_lineage_mixed(
        tm.state,
        ns,
        tm.state.revision,
        (read_request(endpoint, "mc", _mixed_body(A_TEXT, SIBLING_X), MIX_CMD),),
    )
    assert t_m.outcome is RootLineageOutcome.ACCEPTED, t_m.diagnostics
    s_m = t_m.state
    assert not any(
        f.provenance.kind == "read" and f.provenance.call_id == "mc" for f in s_m.root_facts
    )
    # I stays explicitly conflicted: no ready graph/admission.
    r = derive(s_m, ns)
    assert_i_refused(r, s_m, I_OUT.REFUSED_ROOT_CONFLICT, (I_L.ROOT_CONFLICT,))
    # A genuine singleton descendant of ALL branches resolves it.
    occ_y = occurrences(s_c, "wy")[0]
    t5 = _issue(
        s_m,
        ns,
        "z2",
        endpoint,
        (occ_x.occurrence_id, occ_y.occurrence_id),
        "cat AGENTS.md",
    )
    assert t5.outcome is RootLineageOutcome.ACCEPTED
    t6 = observe_root_lineage_mixed(
        t5.state,
        ns,
        t5.state.revision,
        (read_request(endpoint, "z2", SIBLING_Z, "cat AGENTS.md"),),
    )
    assert t6.outcome is RootLineageOutcome.ACCEPTED
    s6 = t6.state
    sel6 = select_current_root(s6, ns)
    assert sel6.outcome is RootSelectionOutcome.OK
    assert sel6.selected_source_digest == sha256_hex(SIBLING_Z)
    assert len(sel6.witness_facts) == 1
    assert sel6.witness_facts[0] is read_fact(s6, "z2")
    r6 = derive(s6, ns)
    assert_i_ok(r6, s6)
    assert r6.graph.root_digest == sha256_hex(SIBLING_Z)  # type: ignore[union-attr]


# --- F. No self-authorization: unknown / unproven / envelope-only -------


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_f_unauthorized_mixed_sources_refuse(mode: AdmissionMode, endpoint: str) -> None:
    """F (018-o acceptance 6): an initially-unknown mixed root digest
    that no INDEPENDENT authoritative complete whole singleton root
    read establishes in the SAME batch refuses with
    ``REFUSED_ROOT_CONFLICT`` / ``COMPETING_ROOTS`` and the EXACT
    prior H state -- while the actual accepted D candidate is
    retained by identity as internal DISCARDED evidence (never
    partially published).  A mixed read, a changed envelope, an
    unproven source, a caller digest/header or body flag cannot
    authorize itself: the envelope deferral verification keeps its
    DETERMINISTIC precedence FIRST (``ENVELOPE_UNPROVEN`` fires
    before the mixed pending check even when both are unverified)."""
    ns, s1 = _v2_state(mode, "o-f", endpoint)
    fact = read_fact(s1, "fresh-root")
    assert isinstance(fact.provenance, ReadRootProvenance)
    # (1) Unknown foreign digest, issued mixed read, alone.
    t1 = _issue(s1, ns, "f1", endpoint, fact.provenance.occurrence_id, MIX_CMD)
    assert t1.outcome is RootLineageOutcome.ACCEPTED
    t2 = observe_root_lineage_mixed(
        t1.state,
        ns,
        t1.state.revision,
        (read_request(endpoint, "f1", _mixed_body(A_TEXT, FOREIGN_ROOT), MIX_CMD),),
    )
    _assert_refused(
        t2,
        t1.state,
        RootLineageOutcome.REFUSED_ROOT_CONFLICT,
        (RootLineageLimitation.COMPETING_ROOTS,),
    )
    # Discarded-evidence law: the ACTUAL accepted D candidate is
    # retained by identity inside the refused H result.
    assert t2.d_transition is not None
    assert t2.d_transition.outcome is CausalHistoryOutcome.ACCEPTED
    # (2) Unissued (unproven) singleton v3 + mixed v3 in ONE batch:
    # the unproven source cannot establish the mixed digest.
    t3 = _issue(s1, ns, "f2", endpoint, fact.provenance.occurrence_id, MIX_CMD)
    assert t3.outcome is RootLineageOutcome.ACCEPTED
    t4 = observe_root_lineage_mixed(
        t3.state,
        ns,
        t3.state.revision,
        (
            read_request(endpoint, "u3", V3, "cat AGENTS.md"),
            read_request(endpoint, "f2", _mixed_body(A_TEXT, V3), MIX_CMD),
        ),
    )
    _assert_refused(
        t4,
        t3.state,
        RootLineageOutcome.REFUSED_ROOT_CONFLICT,
        (RootLineageLimitation.COMPETING_ROOTS,),
    )
    assert t4.d_transition is not None
    assert t4.d_transition.outcome is CausalHistoryOutcome.ACCEPTED
    # (3) A changed envelope ALONE: the envelope deferral law.
    t5 = observe_root_lineage_mixed(
        s1,
        ns,
        s1.revision,
        (changed_root_envelope(V3),),
    )
    _assert_refused(
        t5,
        s1,
        RootLineageOutcome.REFUSED_ROOT_AUTHORITY,
        (RootLineageLimitation.ENVELOPE_UNPROVEN,),
    )
    # (4) Mixed v3 + changed v3 envelope, BOTH unverified: the
    # deterministic precedence -- envelope FIRST, even though the
    # mixed read is listed first in the batch.
    t6 = _issue(s1, ns, "f4", endpoint, fact.provenance.occurrence_id, MIX_CMD)
    assert t6.outcome is RootLineageOutcome.ACCEPTED
    t7 = observe_root_lineage_mixed(
        t6.state,
        ns,
        t6.state.revision,
        (
            read_request(endpoint, "f4", _mixed_body(A_TEXT, V3), MIX_CMD),
            changed_root_envelope(V3),
        ),
    )
    _assert_refused(
        t7,
        t6.state,
        RootLineageOutcome.REFUSED_ROOT_AUTHORITY,
        (RootLineageLimitation.ENVELOPE_UNPROVEN,),
    )
    assert t7.d_transition is not None
    assert t7.d_transition.outcome is CausalHistoryOutcome.ACCEPTED


# --- G. Old acquisition semantics preserved by the new operation --------


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_g_old_mixed_semantics_preserved(mode: AdmissionMode, endpoint: str) -> None:
    """G (018-o acceptance 7): the new operation earns NO new
    exception where the existing law already has exact semantics.
    The genuine boundaryless positive (retained as an ordinary
    occurrence, no root fact, no I entry from that occurrence) is
    shown BEFORE the negatives: repeated root operands (two
    normalized root-path occurrences, with and without an extra
    member) keep the old COMPETING_ROOTS refusal, and a nonzero
    terminal frame with the same call id keeps the exact old
    completion refusal (no occurrence retained)."""
    ns, s1 = _v2_state(mode, "o-g", endpoint)
    fact = read_fact(s1, "fresh-root")
    assert isinstance(fact.provenance, ReadRootProvenance)
    # Genuine positive: the boundaryless bundle keeps its exact
    # old acquisition semantics -- no proven root region, so no
    # new mixed exception; retained as an ordinary occurrence.
    t1 = _issue(s1, ns, "b1", endpoint, fact.provenance.occurrence_id, BOUNDARYLESS_CMD)
    assert t1.outcome is RootLineageOutcome.ACCEPTED
    t2 = observe_root_lineage_mixed(
        t1.state,
        ns,
        t1.state.revision,
        (read_request(endpoint, "b1", A_TEXT + V2, BOUNDARYLESS_CMD),),
    )
    assert t2.outcome is RootLineageOutcome.ACCEPTED, t2.diagnostics
    s2 = t2.state
    occ = occurrences(s2, "b1")[0]
    assert len(occ.proof.segments) == 1
    assert occ.proof.segments[0].member_positions == (0, 1)
    assert occ.proof.segments[0].member_digest is None
    assert not any(
        f.provenance.kind == "read" and f.provenance.call_id == "b1" for f in s2.root_facts
    )
    # Ordinary I: no admitted entry carries that occurrence's proof.
    r = derive(s2, ns)
    assert_i_ok(r, s2)
    for m in i_members_of(r.admission).values():
        assert m.proof is not occ.proof
    # Repeated root operands: exactly TWO normalized root-path
    # occurrences -- no new exception (the old whole-pass law).
    t3 = _issue(s1, ns, "r1", endpoint, fact.provenance.occurrence_id, REPEAT_CMD)
    assert t3.outcome is RootLineageOutcome.ACCEPTED
    t4 = observe_root_lineage_mixed(
        t3.state,
        ns,
        t3.state.revision,
        (read_request(endpoint, "r1", V2 + MARK + "\n" + V2, REPEAT_CMD),),
    )
    _assert_refused(
        t4,
        t3.state,
        RootLineageOutcome.REFUSED_ROOT_CONFLICT,
        (RootLineageLimitation.COMPETING_ROOTS,),
    )
    # The member-occurrence gate with an additional member present.
    t5 = _issue(s1, ns, "r2", endpoint, fact.provenance.occurrence_id, REPEAT_OPAQUE_CMD)
    assert t5.outcome is RootLineageOutcome.ACCEPTED
    t6 = observe_root_lineage_mixed(
        t5.state,
        ns,
        t5.state.revision,
        (read_request(endpoint, "r2", V2 + MARK + "\n" + V2 + B_TEXT, REPEAT_OPAQUE_CMD),),
    )
    _assert_refused(
        t6,
        t5.state,
        RootLineageOutcome.REFUSED_ROOT_CONFLICT,
        (RootLineageLimitation.COMPETING_ROOTS,),
    )
    # Nonzero terminal frame, same call id: the exact old
    # completion refusal; no occurrence is retained.
    t7 = _issue(s1, ns, "nz", endpoint, fact.provenance.occurrence_id, MIX_CMD)
    assert t7.outcome is RootLineageOutcome.ACCEPTED
    t8 = observe_root_lineage_mixed(
        t7.state,
        ns,
        t7.state.revision,
        (_terminal_only(endpoint, "nz", _mixed_body(A_TEXT, V2), 1),),
    )
    _assert_refused(
        t8,
        t7.state,
        RootLineageOutcome.REFUSED_CONFLICT,
        (RootLineageLimitation.ISSUANCE_CONFLICT,),
    )
    assert len(occurrences(t8.state, "nz")) == 0


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_g_unsupported_incomplete_truncated_retain_old_semantics(
    mode: AdmissionMode, endpoint: str
) -> None:
    """G (018-o acceptance 7, continued): an UNSUPPORTED compound
    plan, a PAIRED pending (incomplete) root read and an ACTUAL
    earned TRUNCATION on a complete frame retain their EXACT old
    acquisition/limitation semantics through the NEW operation --
    the new mixed exception applies only to COMPLETE proven mixed
    proofs (the boundaryless retention positive in the sibling
    control precedes the negatives).  Outcome and retention match
    the old public observer; no completion is invented."""
    ns, s1 = _v2_state(mode, "o-g2", endpoint)
    fact = read_fact(s1, "fresh-root")
    assert isinstance(fact.provenance, ReadRootProvenance)
    # Unsupported compound plan: the form grants nothing; the exact
    # prior state is preserved (REPLAYED with the fixed
    # PLAN_UNSUPPORTED diagnostic, as under the old observer).
    cmd = "cat A.md && echo X && cat AGENTS.md"
    t1 = _issue(s1, ns, "up1", endpoint, fact.provenance.occurrence_id, cmd)
    assert t1.outcome is RootLineageOutcome.ACCEPTED
    t2 = observe_root_lineage_mixed(
        t1.state,
        ns,
        t1.state.revision,
        (read_request(endpoint, "up1", SIBLING_X, cmd),),
    )
    assert t2.outcome is RootLineageOutcome.REPLAYED
    assert t2.state is t1.state
    assert t2.diagnostics == (RootLineageLimitation.PLAN_UNSUPPORTED,)
    assert t2.new_root_facts == ()
    assert t2.revision_after == t1.state.revision
    assert occurrences(t1.state, "up1") == []
    # PAIRED pending (incomplete) root read: honestly retained as a
    # partial result; no occurrence, no root fact.
    t3 = _issue(s1, ns, "pt1", endpoint, fact.provenance.occurrence_id, "cat AGENTS.md")
    assert t3.outcome is RootLineageOutcome.ACCEPTED
    t4 = observe_root_lineage_mixed(
        t3.state,
        ns,
        t3.state.revision,
        (root_chain(endpoint, "pt1", "Pending part."),),
    )
    assert t4.outcome is RootLineageOutcome.ACCEPTED, t4.diagnostics
    s4 = t4.state
    assert occurrences(s4, "pt1") == []
    assert not any(
        f.provenance.kind == "read" and f.provenance.call_id == "pt1" for f in s4.root_facts
    )
    pend = [r for r in s4.d_state.results if r.call_id == "pt1"]
    assert len(pend) == 1
    assert pend[0].complete is False
    # ACTUAL earned truncation on a complete (exit-zero) frame:
    # never completes; the typed PROCESS_TRUNCATED limitation is
    # retained; no occurrence, no root fact.
    t5 = _issue(s1, ns, "tt1", endpoint, fact.provenance.occurrence_id, "cat AGENTS.md")
    assert t5.outcome is RootLineageOutcome.ACCEPTED
    t6 = observe_root_lineage_mixed(
        t5.state,
        ns,
        t5.state.revision,
        (_truncated_root_request(endpoint, "tt1"),),
    )
    assert t6.outcome is RootLineageOutcome.ACCEPTED, t6.diagnostics
    s6 = t6.state
    assert occurrences(s6, "tt1") == []
    assert not any(
        f.provenance.kind == "read" and f.provenance.call_id == "tt1" for f in s6.root_facts
    )
    assert t6.d_transition is not None
    assert Limitation.PROCESS_TRUNCATED in t6.d_transition.observation_limitations
    trunc = [r for r in s6.d_state.results if r.call_id == "tt1"]
    assert len(trunc) == 1
    assert trunc[0].complete is False
    # The selection is unchanged by any of these honest retentions.
    sel = select_current_root(s6, ns)
    assert sel.outcome is RootSelectionOutcome.OK
    assert sel.selected_source_digest == sha256_hex(V2)
    assert sel.limitations == ()


# --- H. Gates, resource law, privacy ------------------------------------


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_h_gates_refuse_before_compatibility(mode: AdmissionMode, endpoint: str) -> None:
    """H (018-o acceptance 8): the existing namespace/revision/
    version/state-integrity gates run BEFORE any compatibility
    interpretation in the new operation: a fully VALID known mixed
    read under a foreign namespace, a stale revision, a forged
    lineage key or a forged wrapped D history key refuses whole
    with the exact prior state and NO D transition; a malformed
    state argument raises the fixed bounded error before any field
    interpretation."""
    ns, s1 = _v2_state(mode, "o-h-g", endpoint)
    fact = read_fact(s1, "fresh-root")
    assert isinstance(fact.provenance, ReadRootProvenance)
    t1 = _issue(s1, ns, "h1", endpoint, fact.provenance.occurrence_id, MIX_CMD)
    assert t1.outcome is RootLineageOutcome.ACCEPTED
    s_i = t1.state
    req = read_request(endpoint, "h1", _mixed_body(A_TEXT, V2), MIX_CMD)
    # Cross-namespace: refused at the scope gate, before compatibility.
    ns_other = h_ns(mode, "o-h-g-other")
    t = observe_root_lineage_mixed(s_i, ns_other, s_i.revision, (req,))
    assert t.outcome is RootLineageOutcome.REFUSED_FOREIGN_SCOPE
    assert t.state is s_i
    assert t.d_transition is None
    assert t.diagnostics == ()
    assert t.revision_after == s_i.revision
    # Stale revision: the CAS fence.
    t = observe_root_lineage_mixed(s_i, ns, s_i.revision + 1, (req,))
    assert t.outcome is RootLineageOutcome.REFUSED_CAS_MISMATCH
    assert t.state is s_i
    assert t.d_transition is None
    assert t.diagnostics == ()
    # A forged lineage key on the retained state.
    s_fk = s_i.model_copy(update={"lineage_key": "f" * 64})
    t = observe_root_lineage_mixed(s_fk, ns, s_fk.revision, (req,))
    assert t.outcome is RootLineageOutcome.REFUSED_FOREIGN_SCOPE
    assert t.state is s_fk
    assert t.d_transition is None
    # A forged wrapped D history key.
    s_dh = s_i.model_copy(
        update={"d_state": s_i.d_state.model_copy(update={"history_key": "e" * 64})}
    )
    t = observe_root_lineage_mixed(s_dh, ns, s_dh.revision, (req,))
    assert t.outcome is RootLineageOutcome.REFUSED_FOREIGN_SCOPE
    assert t.state is s_dh
    assert t.d_transition is None
    # Malformed state: the fixed bounded error, no private value.
    with pytest.raises(
        ValueError,
        match="the root-lineage state must carry an actual bounded state record",
    ):
        # Intentional malformed state input (the fixed bounded error).
        observe_root_lineage_mixed("not-a-state", ns, 0, (req,))  # type: ignore[arg-type]


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_h_mixed_pending_snapshot_precharge(
    mode: AdmissionMode, endpoint: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    """H (018-o acceptance 8, resource law): the pending-set SNAPSHOT
    (the frozenset copy of the deferred mixed digests) is CHARGED on
    the SAME H outer BEFORE the copy.  The module-local frozenset
    interceptor observes the ACTUAL pending-set copy (the C-path set
    copy never invokes a subclass ``__iter__``, so only the
    intercepted call proves snapshot work); the traced H outer
    records the exact reservation.  At the measured reservation
    END the snapshot admission succeeds exactly at its limit and
    the LATER charged union work truthfully refuses the operation
    (not an overall success); one unit below the end the
    reservation refuses BEFORE any snapshot work (zero observed
    copies).  The k=2 unresolved-digest conflict is labeled
    PENDING-VERIFICATION REACHABILITY at its measured at-limit/
    one-below (the operation completes the charged pending
    verification under the cap); it is not a B/D collection-cap
    limit at its WORK boundary; the ACTUAL inherited B pending-
    collection cap is the separate dedicated control
    (``test_h_mixed_pending_collection_cap``).  The setup is the
    BOOTSTRAP-STATE minimal fixture (the mixed read issued directly
    from CAUSAL_ROOT_FACT right after the bootstrap, no intervening
    refresh read).  The same setup identities/lengths run under
    every cap control."""
    expected_digest = sha256_hex(FOREIGN_ROOT)
    expected_digest2 = sha256_hex(FOREIGN_ROOT2)

    def run(cap: int | None, tag: str, k: int) -> tuple[Any, Any, list[tuple[int, int]]]:
        bounds = RootLineageBounds() if cap is None else RootLineageBounds(max_total_work_units=cap)
        ns_c = h_ns(mode, tag, bounds=bounds)
        t0 = bootstrap_root_lineage((root_request(),), ns_c)
        if t0.outcome is not RootLineageOutcome.ACCEPTED:
            return t0, None, []
        s0 = t0.state
        # BOOTSTRAP-STATE fixture: the mixed read is issued directly
        # from CAUSAL_ROOT_FACT right after the bootstrap (no
        # intervening refresh read), the genuinely minimal setup
        # for the pending-snapshot reservation boundary.
        t1 = _issue(s0, ns_c, "m1", endpoint, CAUSAL_ROOT_FACT, MIX_CMD)
        if t1.outcome is not RootLineageOutcome.ACCEPTED:
            return t1, s0, []
        s_state = t1.state
        requests: tuple[Any, ...] = ()
        if k == 1:
            requests = (read_request(endpoint, "m1", _mixed_body(A_TEXT, FOREIGN_ROOT), MIX_CMD),)
        else:
            t2 = _issue(s_state, ns_c, "m2", endpoint, CAUSAL_ROOT_FACT, MIXB_CMD)
            if t2.outcome is not RootLineageOutcome.ACCEPTED:
                return t2, s_state, []
            s_state = t2.state
            requests = (
                read_request(endpoint, "m1", _mixed_body(A_TEXT, FOREIGN_ROOT), MIX_CMD),
                read_request(
                    endpoint,
                    "m2",
                    _mixed_body(B_TEXT, FOREIGN_ROOT2, MARK2),
                    MIXB_CMD,
                ),
            )
        ledgers: list[Any] = []
        snapshots: list[tuple[int, int]] = []

        class TraceOuter(_HOuter):
            def __init__(self, work_cap: int) -> None:
                super().__init__(work_cap)
                self.last_reservation: tuple[int, int, int, bool] | None = None
                ledgers.append(self)

            def units(self, n: int) -> bool:
                before = self.work_spent
                accepted = super().units(n)
                self.last_reservation = (n, before, self.work_spent, accepted)
                return accepted

        def observed_freeze(value: Any = ()) -> Any:
            if type(value) is set and value == (
                {expected_digest} if k == 1 else {expected_digest, expected_digest2}
            ):
                ledger = ledgers[-1]
                n, before, after, accepted = ledger.last_reservation
                assert accepted and n == len(value) + 1 and after - before == n
                assert ledger.work_spent == after and after <= ledger.work_cap
                snapshots.append((before, after))
            return builtins.frozenset(value)

        monkeypatch.setattr(rl_mod, "_HOuter", TraceOuter)
        monkeypatch.setattr(rl_mod, "frozenset", observed_freeze, raising=False)
        t = observe_root_lineage_mixed(s_state, ns_c, s_state.revision, requests)
        return t, s_state, snapshots

    # k=1, large cap: the unresolved foreign digest refuses with the
    # exact conflict; the snapshot ran ONCE, fully prepaid.
    t1, prior1, snaps1 = run(None, f"hps-{mode.value}-{endpoint}-k1", 1)
    _assert_refused(
        t1,
        prior1,
        RootLineageOutcome.REFUSED_ROOT_CONFLICT,
        (RootLineageLimitation.COMPETING_ROOTS,),
    )
    assert len(snaps1) == 1
    boundary = snaps1[0][1]
    # Exactly at the reservation END: the snapshot admission
    # succeeds at its limit; the LATER charged union work refuses
    # the operation (not an overall success), exact prior state.
    t2, prior2, snaps2 = run(boundary, f"hps-{mode.value}-{endpoint}-k1", 1)
    assert len(snaps2) == 1 and snaps2[0][1] == boundary
    _assert_refused(
        t2,
        prior2,
        RootLineageOutcome.REFUSED_OVER_BOUND,
        (RootLineageLimitation.WORK_UNITS_OVER_BOUND,),
    )
    assert t2.d_transition is not None
    assert t2.d_transition.outcome is CausalHistoryOutcome.ACCEPTED
    # ONE unit below the end: the reservation refuses BEFORE any
    # snapshot work (zero observed copies), exact prior state.
    t3, prior3, snaps3 = run(boundary - 1, f"hps-{mode.value}-{endpoint}-k1", 1)
    assert snaps3 == [], "snapshot executed before full reservation"
    _assert_refused(
        t3,
        prior3,
        RootLineageOutcome.REFUSED_OVER_BOUND,
        (RootLineageLimitation.WORK_UNITS_OVER_BOUND,),
    )
    assert t3.d_transition is not None
    assert t3.d_transition.outcome is CausalHistoryOutcome.ACCEPTED
    # k=2: PENDING-VERIFICATION REACHABILITY at the MEASURED
    # at-limit/one-below: the operation completes the charged
    # snapshot + union verification under the cap and then refuses
    # the unresolved digests; one below it, the over-bound refusal.
    # (The ACTUAL B pending-collection cap is exercised by the
    # dedicated test_h_mixed_pending_collection_cap control.)

    def k2_reaches_pending(_mode: Any, _tag: str, i: int, cap: int) -> bool:
        t, _prior, _snaps = run(cap, f"{_tag}-{i:05d}", 2)
        return bool(t.outcome is RootLineageOutcome.REFUSED_ROOT_CONFLICT)

    t2_cap = _min_accepted_cap(mode, f"hps-{mode.value}-{endpoint}-k2", k2_reaches_pending)
    t4, prior4, snaps4 = run(t2_cap, f"hps-{mode.value}-{endpoint}-k2-at", 2)
    _assert_refused(
        t4,
        prior4,
        RootLineageOutcome.REFUSED_ROOT_CONFLICT,
        (RootLineageLimitation.COMPETING_ROOTS,),
    )
    assert len(snaps4) == 1
    assert t4.d_transition is not None
    cand = t4.d_transition.state
    assert len([o for o in cand.occurrences if o.call_id == "m1"]) == 1
    assert len([o for o in cand.occurrences if o.call_id == "m2"]) == 1
    t5, prior5, snaps5 = run(t2_cap - 1, f"hps-{mode.value}-{endpoint}-k2-blw", 2)
    _assert_refused(
        t5,
        prior5,
        RootLineageOutcome.REFUSED_OVER_BOUND,
        (RootLineageLimitation.WORK_UNITS_OVER_BOUND,),
    )


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_h_mixed_pending_collection_cap(
    mode: AdmissionMode, endpoint: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    """H (018-o acceptance 8, bounded pending COLLECTION): the
    ACTUAL inherited B candidate cap (``BundleProofBounds.max_
    bundles``) is exercised through the new operation: an
    independent singleton v3 read plus TWO distinct equal-byte
    mixed v3 reads give the D core its ACTUAL candidate count
    (>= 3), two pending-add ATTEMPTS but ONE unique pending
    digest (attempts are counted before dedup; no seam dedup, no
    new domain, no min/domain change).  At the measured candidate
    count the full O -> ordinary I positive holds; one below it
    the EXACT prior state returns ``BUNDLES_OVER_BOUND`` with
    ZERO pending-add and ZERO retained-digest events (no pending
    metadata retained before the candidate-cap refusal)."""
    v2b = "Read `A.md` under version two.\n"
    v3b = "Read `A.md` under version three.\n"
    cmdb = "cat AGENTS.md && echo 'ROOTSEP' && cat A.md"
    argsb = json.dumps({"cmd": cmdb})
    mixbody = v3b + "ROOTSEP\nKnown synthetic A.\n"

    recorded: list[tuple[int, int]] = []
    attempts: list[Any] = []

    class ObservedSet(set[str]):
        def add(self, value: Any) -> None:
            attempts.append(value)
            return super().add(value)

    class ObservedContext(_RootLineageContext):
        def __init__(self, *pos: Any, **kw: Any) -> None:
            super().__init__(*pos, **kw)
            if self.mixed_root_acquisition:
                self.deferred_mixed_digests = ObservedSet()

    original_collect = bp_mod._proof_collect

    def collect(*pos: Any, **kw: Any) -> Any:
        result = original_collect(*pos, **kw)
        context = kw.get("lineage_context")
        assert context is not None and context.mixed_root_acquisition
        recorded.append((result.candidates_inspected, len(context.deferred_mixed_digests)))
        return result

    def run(cap: int, tag: str) -> tuple[Any, Any, Any]:
        ns, initial = bootstrap(mode, tag, proof_bounds=BundleProofBounds(max_bundles=cap))
        state = refreshed(initial, ns, "root2", endpoint, v2b)
        parent = occurrences(state, "root2")[0].occurrence_id
        for cid, args in (
            ("root3", json.dumps({"cmd": "cat AGENTS.md"})),
            ("mixed3a", argsb),
            ("mixed3b", argsb),
        ):
            issued = issue(state, ns, cid, endpoint, (parent,), args=args)
            assert issued.outcome is RootLineageOutcome.ACCEPTED, issued.diagnostics
            state = issued.state
        recorded.clear()
        attempts.clear()
        # Both patches scope to the TARGET mixed-observe call only:
        # the next run's bootstrap/refresh must not reach the
        # wrappers (which assert the mixed context).
        with monkeypatch.context() as mp:
            mp.setattr(d_mod, "_proof_collect", collect)
            mp.setattr(rl_mod, "_RootLineageContext", ObservedContext)
            t = observe_root_lineage_mixed(
                state,
                ns,
                state.revision,
                (
                    read_request(endpoint, "root3", v3b, "cat AGENTS.md"),
                    read_request(endpoint, "mixed3a", mixbody, cmdb),
                    read_request(endpoint, "mixed3b", mixbody, cmdb),
                ),
            )
        return t, state, ns

    t_hi, _prior_hi, ns_hi = run(128, f"o-hpc-{mode.value}-{endpoint}")
    assert t_hi.outcome is RootLineageOutcome.ACCEPTED, t_hi.diagnostics
    assert len(recorded) == 1
    measured, pending, adds = (*recorded[0], len(attempts))
    assert measured >= 3 and pending == 1 and adds == 2
    assert derive(t_hi.state, ns_hi).outcome.value == "ok"

    t_at, _prior_at, ns_at = run(measured, f"o-hpc-{mode.value}-{endpoint}-at")
    assert t_at.outcome is RootLineageOutcome.ACCEPTED, t_at.diagnostics
    assert len(recorded) == 1
    assert recorded[0][0] == measured and recorded[0][1] == 1 and len(attempts) == 2
    assert derive(t_at.state, ns_at).outcome.value == "ok"

    t_bl, prior_bl, _ns_bl = run(measured - 1, f"o-hpc-{mode.value}-{endpoint}-blw")
    assert t_bl.outcome is RootLineageOutcome.REFUSED_OVER_BOUND
    assert t_bl.diagnostics == (RootLineageLimitation.BUNDLES_OVER_BOUND,)
    assert t_bl.state is prior_bl
    assert t_bl.new_root_facts == ()
    assert t_bl.revision_after == prior_bl.revision
    # The D core itself refused before any accepted candidate, and
    # H mirrored the exact D outcome 1:1 (the D transition is
    # retained by identity as evidence).
    assert t_bl.d_transition is not None
    assert t_bl.d_transition.outcome is not CausalHistoryOutcome.ACCEPTED
    assert len(recorded) == 1
    assert recorded[0] == (measured, 0), (
        "pending metadata retained before the candidate-cap refusal"
    )
    assert attempts == []


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_h_malformed_state_integrity_refuses(mode: AdmissionMode, endpoint: str) -> None:
    """H (018-o acceptance 8, continued): a COHERENTLY scoped,
    revision-matched MALFORMED H state (the missing root-fact
    inventory over an actual retained D state, and a forged orphan
    read provenance) still reaches the charged cross-record
    INTEGRITY validator in the new operation BEFORE any positive
    compatibility work: the exact integrity refusal, the EXACT
    prior state, NO D transition, no minted facts.  The new
    operation's version gate keeps the exact version limitation for
    a coherent unsupported version (the scope key recomputed over
    it).  These pin the validator and the version fence against
    accidental skipping in the new operation; no existing law is
    weakened."""
    ns, s1 = _v2_state(mode, "o-h-m", endpoint)
    fact = read_fact(s1, "fresh-root")
    req = read_request(endpoint, "hm1", _mixed_body(A_TEXT, V2), MIX_CMD)
    # (a) the earned read fact omitted while the ACTUAL D stays
    # intact: the complete fact inventory is an incoherent binding.
    s_a = s1.model_copy(update={"root_facts": tuple(f for f in s1.root_facts if f is not fact)})
    t = observe_root_lineage_mixed(s_a, ns, s_a.revision, (req,))
    assert t.outcome is RootLineageOutcome.REFUSED_CONFLICT
    assert t.diagnostics == (RootLineageLimitation.MALFORMED_BINDING,)
    assert t.state is s_a
    assert t.d_transition is None
    assert t.new_root_facts == ()
    assert t.revision_after == s_a.revision
    # (b) an orphan read provenance: the occurrence id names no
    # retained occurrence (a forged inventory row).
    orphan_p = fact.provenance.model_copy(update={"occurrence_id": "d" * 64})
    s_b = s1.model_copy(
        update={
            "root_facts": tuple(
                fact.model_copy(update={"provenance": orphan_p}) if f is fact else f
                for f in s1.root_facts
            )
        }
    )
    t = observe_root_lineage_mixed(s_b, ns, s_b.revision, (req,))
    assert t.outcome is RootLineageOutcome.REFUSED_CONFLICT
    assert t.diagnostics == (RootLineageLimitation.MALFORMED_BINDING,)
    assert t.state is s_b
    assert t.d_transition is None
    assert t.new_root_facts == ()
    # (c) a COHERENT unsupported contract version: the SAME actual
    # D scope (history key, bounds) as the retained state, only the
    # H version tag changed and the H lineage key re-bound over it
    # (the scope key is recomputed over it, so this is not a
    # foreign-scope artifact): the exact version limitation, never
    # a generic malformed label.
    data = ns.model_dump()
    data.update(
        contract_version="unsupported-synthetic/v9",
        lineage_key=_lineage_key(
            ns.history_key,
            "unsupported-synthetic/v9",
            ROOT_LINEAGE_POLICY_VERSION,
            ns.root_lineage_bounds,
        ),
    )
    ns9 = RootLineageNamespace(**data)
    s9 = s1.model_copy(update={"lineage_key": ns9.lineage_key})
    t = observe_root_lineage_mixed(s9, ns9, s9.revision, (req,))
    assert t.outcome is RootLineageOutcome.REFUSED_VERSION_CONFLICT
    assert t.diagnostics == (RootLineageLimitation.VERSION_UNSUPPORTED,)
    assert t.state is s9
    assert t.d_transition is None
    assert t.new_root_facts == ()


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_h_mixed_op_work_at_limit_one_below(mode: AdmissionMode, endpoint: str) -> None:
    """H (018-o acceptance 8, resource law): the FULL positive mixed
    sequence (bootstrap, issued refresh, issued mixed read, mixed
    observation) under the SAME cap on every operation accepts at
    its MEASURED minimal cap (fresh per-operation outers, the
    inherited H total-work domain name), and the first
    non-accepted step at cap-1 is EXACTLY the new mixed operation
    (the four genuine setup steps accepted beneath it), the exact
    over-bound refusal with the exact prior state and no revision
    advance."""

    def run_steps(cap: int, tag: str) -> tuple[Any, list[tuple[str, Any, Any]]]:
        bounds = RootLineageBounds(max_total_work_units=cap)
        ns_c = h_ns(mode, tag, bounds=bounds)
        t0 = bootstrap_root_lineage((root_request(),), ns_c)
        steps: list[tuple[str, Any, Any]] = [("bootstrap", t0, None)]
        if t0.outcome is not RootLineageOutcome.ACCEPTED:
            return ns_c, steps
        s0 = t0.state
        t1 = register_root_issuance(
            s0,
            ns_c,
            "fr",
            endpoint,
            "exec_command",
            ROOT_READ_ARGS,
            (CAUSAL_ROOT_FACT,),
            s0.revision,
        )
        steps.append(("issue-fr", t1, s0))
        if t1.outcome is not RootLineageOutcome.ACCEPTED:
            return ns_c, steps
        s1 = t1.state
        t2 = observe_root_lineage(
            s1,
            ns_c,
            s1.revision,
            (read_request(endpoint, "fr", V2, "cat AGENTS.md"),),
        )
        steps.append(("observe-fr", t2, s1))
        if t2.outcome is not RootLineageOutcome.ACCEPTED:
            return ns_c, steps
        s2 = t2.state
        fact = read_fact(s2, "fr")
        assert isinstance(fact.provenance, ReadRootProvenance)
        t3 = register_root_issuance(
            s2,
            ns_c,
            "m1",
            endpoint,
            "exec_command",
            json.dumps({"cmd": MIX_CMD}),
            (fact.provenance.occurrence_id,),
            s2.revision,
        )
        steps.append(("issue-m1", t3, s2))
        if t3.outcome is not RootLineageOutcome.ACCEPTED:
            return ns_c, steps
        s3 = t3.state
        t4 = observe_root_lineage_mixed(
            s3,
            ns_c,
            s3.revision,
            (read_request(endpoint, "m1", _mixed_body(A_TEXT, V2), MIX_CMD),),
        )
        steps.append(("observe-mixed", t4, s3))
        return ns_c, steps

    def all_accepted(_mode: Any, _tag: str, i: int, cap: int) -> bool:
        _ns_c, steps = run_steps(cap, f"{_tag}-{i:05d}")
        return len(steps) == 5 and all(
            t.outcome is RootLineageOutcome.ACCEPTED for _n, t, _p in steps
        )

    cap = _min_accepted_cap(mode, f"hwl-{mode.value}-{endpoint}", all_accepted)
    ns_at, steps = run_steps(cap, f"hwl-{mode.value}-{endpoint}-at")
    assert len(steps) == 5
    for name, t, _prior in steps:
        assert t.outcome is RootLineageOutcome.ACCEPTED, (name, t.diagnostics)
    s_at = steps[-1][1].state
    # Selection sanity on the final accepted state.
    sel = select_current_root(s_at, ns_at)
    assert sel.outcome is RootSelectionOutcome.OK
    assert sel.selected_source_digest == sha256_hex(V2)
    _ns_b, steps1 = run_steps(cap - 1, f"hwl-{mode.value}-{endpoint}-below")
    # The four genuine setup steps stay accepted at cap-1; the
    # crossing step is EXACTLY the new mixed operation (the
    # claimed NEW-operation work boundary, not a setup step).
    for name, t, _prior in steps1[:4]:
        assert t.outcome is RootLineageOutcome.ACCEPTED, (name, t.diagnostics)
    name, t, prior = steps1[4]
    assert name == "observe-mixed"
    assert t.outcome is RootLineageOutcome.REFUSED_OVER_BOUND
    assert t.diagnostics == (RootLineageLimitation.WORK_UNITS_OVER_BOUND,)
    assert prior is not None and t.state is prior
    assert t.revision_after == prior.revision
    assert t.new_root_facts == ()


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_h_privacy_canary(mode: AdmissionMode, endpoint: str) -> None:
    """H (018-o acceptance 8, privacy): the private errors/reprs of
    the new operation expose NO source text and NO identity values
    on the accepted and the refused paths: the canary body text and
    its sha never appear in any operational str/repr, and the call
    ids are placeholdered (digests and occurrence ids stay legal)."""
    ns, s1 = _v2_state(mode, "o-h-p", endpoint)
    fact = read_fact(s1, "fresh-root")
    assert isinstance(fact.provenance, ReadRootProvenance)
    body = _mixed_body(CANARY + " source line\n", V2)
    t1 = _issue(s1, ns, "pc1", endpoint, fact.provenance.occurrence_id, MIX_CMD)
    assert t1.outcome is RootLineageOutcome.ACCEPTED
    t2 = observe_root_lineage_mixed(
        t1.state,
        ns,
        t1.state.revision,
        (read_request(endpoint, "pc1", body, MIX_CMD),),
    )
    assert t2.outcome is RootLineageOutcome.ACCEPTED
    s2 = t2.state
    canary_sha = sha256_hex(CANARY)
    for text in (str(t1), repr(t1), str(t2), repr(t2), repr(s1), repr(s2)):
        assert CANARY not in text
        assert canary_sha not in text
        assert "pc1" not in text
    for f in s2.root_facts:
        text = repr(f)
        assert CANARY not in text
        assert canary_sha not in text
        assert "pc1" not in text
    # The refused path: the canary body under an unresolved foreign
    # digest keeps the same privacy on the discarded-evidence result.
    t3 = _issue(s1, ns, "pc2", endpoint, fact.provenance.occurrence_id, MIX_CMD)
    assert t3.outcome is RootLineageOutcome.ACCEPTED
    t4 = observe_root_lineage_mixed(
        t3.state,
        ns,
        t3.state.revision,
        (
            read_request(
                endpoint,
                "pc2",
                _mixed_body(CANARY + " source line\n", FOREIGN_ROOT),
                MIX_CMD,
            ),
        ),
    )
    assert t4.outcome is RootLineageOutcome.REFUSED_ROOT_CONFLICT
    for text in (str(t4), repr(t4), repr(t4.state), repr(t4.d_transition)):
        assert CANARY not in text
        assert canary_sha not in text
        assert "pc2" not in text

"""Durable original-API acceptance: pure root-region currentness (018-q).

The A-F actual-path matrix of the activated 018-q order, over BOTH
read endpoints and BOTH admission modes, exercised on the SAME
legitimate state earned through the accepted public P APIs
(bootstrap/issuance/receipt/observe/selection/validation) and the
NEW public Q derivation
(``derive_root_region_currentness``) with original GraphRequests
and original proofs.  A known authoritative root is NOT currently
usable after a trusted complete root-bearing observation whose
governing root cannot be established under P source policy: the
audit case returns ``root_currentness_unproven`` with no usable
selected source while P authority-only selection stays its same
correct contract; the combined frozen frontier restores readiness
only through genuinely later supported authoritative witnesses
(dominance, joint coverage, descendant-of-all, genuine old-bytes
revert); every evidence-table exclusion row holds through actual
public APIs; malformed/forged inputs refuse with the fixed typed
law; the ONE Q outer and the ACTUAL independent P domain are
measured at their real boundaries; the result retains the EXACT
input state, the actual same-run P selection and the actual
retained occurrence/result references by identity; operational
reprs are fixed non-echoing with ROOT/nonroot/source/identity
canaries; no host IO anywhere on the public surface.  No
strategic-runtime dependency: known-synthetic original API
fixtures only.  Existing H/O/I/P tests remain unchanged.

Sections: A the four-case audit scenario with original identities;
B the combined-frontier matrix (dominance, joint coverage,
child-of-one, later opaque, old-bytes revert, replay, reversed
permutations); C the closed evidence-table exclusions; D the
malformed/forged/coherent-rekey gates; E the work boundaries
(full-operation cap, the ACTUAL independent P domain at the
measured eligible-frontier discriminator, full-Q cap with
eligible dominated uncertainty, witness pre-construction
sentinel, inherited per-batch request domain, post-selection Q
overflow, constructor-level collection ceilings); F invariants,
privacy and purity.
"""

from __future__ import annotations

import json
from typing import Any

import pytest
from pydantic import ValidationError

from slaif_local_coding.constitution.bundles import GraphBounds
from slaif_local_coding.constitution.bundles.bundle_admission_models import (
    AdmissionMode,
    make_bundle_admission_namespace,
)
from slaif_local_coding.constitution.bundles.causal_history_models import (
    CAUSAL_ROOT_FACT,
    CausalHistoryLimitation,
    HistoryBounds,
    validate_causal_history_state,
)
from slaif_local_coding.constitution.bundles.graph_observation import GraphRequest
from slaif_local_coding.constitution.bundles.observation_models import (
    PRIVATE_ID_PLACEHOLDER,
)
from slaif_local_coding.constitution.bundles.root_lineage import _HOuter
from slaif_local_coding.constitution.bundles.root_lineage_models import (
    RootLineageBounds,
    RootLineageLimitation,
    RootLineageOutcome,
    RootSelectionOutcome,
    _lineage_key,
)
from slaif_local_coding.constitution.bundles.root_region_currentness import (
    _QOuter,
    _QPAdapter,
    derive_root_region_currentness,
)
from slaif_local_coding.constitution.bundles.root_region_currentness_models import (
    ROOT_REGION_CURRENTNESS_CONTRACT_VERSION,
    ROOT_REGION_CURRENTNESS_POLICY_VERSION,
    RootRegionCurrentnessBounds,
    RootRegionCurrentnessDiagnostic,
    RootRegionCurrentnessOutcome,
    RootRegionCurrentnessResult,
    RootRegionUncertaintyClass,
    RootRegionUncertaintyWitness,
    root_region_currentness_scope_key,
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
    make_root_region_lineage_namespace,
)
from slaif_local_coding.constitution.cache import RequestIdentity
from tests.test_causal_history import (
    ENDPOINTS,
    FINGERPRINT,
    IDENTITY,
    MODES,
    WORKSPACE,
    exec_call,
    out_item,
    read_request,
    sha256_hex,
)
from tests.test_root_lineage import _min_accepted_cap, rooted
from tests.test_root_region_lineage import (
    V2,
    V3,
    _g_setup,
    _host_io_facilities,
    _j_forge_coherent_rekey,
    _j_forge_d_owner_missing,
    _j_forge_d_owner_rekeyed,
    _j_forge_detached_occurrence,
    _j_forge_endpoint_mismatch,
    _j_forge_flag,
    _j_forge_original_proof_identity,
    _j_forge_owner_mismatch,
    _j_forge_root_member_length,
    _j_forge_segment_swap,
    _j_forge_whole_proof_digest,
    _j_forge_whole_proof_length,
    _j_forge_wrong_root_path,
    _two_sibling_regions,
)

# --- Module constants (known-synthetic original API fixtures) -----------

MARK = "QSEP"
MIX_CMD = f"cat A.md && echo '{MARK}' && cat AGENTS.md"
BOUNDARYLESS_CMD = "cat AGENTS.md A.md"
BOUNDARYLESS_REV_CMD = "cat A.md AGENTS.md"
REPEAT_CMD = f"cat AGENTS.md && echo '{MARK}' && cat AGENTS.md"
REPEAT3_CMD = "cat AGENTS.md AGENTS.md AGENTS.md A.md"
REPEAT_OPAQUE_CMD = f"cat AGENTS.md && echo '{MARK}' && cat AGENTS.md B.md"
NONROOT_CMD = "cat A.md && cat B.md"
WRONGPATH_CMD = "cat SUB/AGENTS.md"
A_TEXT = "Synthetic nonroot A.\n"
B_TEXT = "Synthetic nonroot B.\n"
OPAQUE_BODY = "Unknown root constituent.\n" + A_TEXT


def mixed_body(*parts: str) -> str:
    """The mixed body layout for the marker-separated command:
    ``file body + MARK + "\\n" + file body + ...``."""
    out = parts[0]
    for marker, body in zip(parts[1::2], parts[2::2], strict=True):
        out += f"{marker}\n{body}"
    return out


def q_ns(mode: AdmissionMode, lineage: str, **kwargs: Any) -> Any:
    """A root-region scope over the ACTUAL accepted 018-d scope."""
    identity = kwargs.pop("identity", IDENTITY)
    model_identity = kwargs.pop("model_identity", "synthetic-currentness-model")
    admission = make_bundle_admission_namespace(
        identity,
        model_identity=model_identity,
        config_fingerprint=FINGERPRINT,
        workspace=kwargs.pop("workspace", WORKSPACE),
        mode=mode,
        **kwargs,
    )
    return make_root_region_lineage_namespace(admission, lineage)


def q_bootstrap(mode: AdmissionMode, lineage: str, root_body: str = "Initial root.") -> Any:
    ns = q_ns(mode, lineage)
    t = bootstrap_root_region_lineage((rooted(root_body),), ns)
    assert t.outcome.value == "accepted", t.diagnostics
    return ns, t.state


def q_issue(
    state: Any, ns: Any, cid: str, endpoint: str, cmd: str, frontier: tuple[str, ...]
) -> Any:
    t = register_root_region_issuance(
        state,
        ns,
        cid,
        endpoint,
        "exec_command",
        json.dumps({"cmd": cmd}),
        tuple(frontier),
        state.revision,
    )
    assert t.outcome.value == "accepted", (t.outcome, t.diagnostics)
    return t.state


def q_observe(state: Any, ns: Any, endpoint: str, cid: str, body: str, cmd: str) -> Any:
    t = observe_root_region_lineage(
        state, ns, state.revision, (read_request(endpoint, cid, body, cmd),)
    )
    assert t.outcome.value == "accepted", (t.outcome, t.diagnostics)
    return t.state


def q_occ(state: Any, cid: str) -> Any:
    return next(x for x in state.d_state.occurrences if x.call_id == cid)


def q_anchor_fact(state: Any) -> Any:
    return next(f for f in state.root_facts if f.provenance.kind == "envelope")


def q_result(state: Any, ns: Any, bounds: RootRegionCurrentnessBounds | None = None) -> Any:
    return derive_root_region_currentness(state, ns, bounds)


def q_scope_key(state: Any, bounds: RootRegionCurrentnessBounds) -> str:
    return root_region_currentness_scope_key(
        state.lineage_key,
        ROOT_REGION_CURRENTNESS_CONTRACT_VERSION,
        ROOT_REGION_CURRENTNESS_POLICY_VERSION,
        bounds,
    )


def assert_state_identity(r: Any, state: Any) -> None:
    """The EXACT input state is retained by reference (the query is
    pure: no partial output, no revision advance)."""
    assert r.state is state
    assert r.revision == state.revision
    assert r.lineage_key == state.lineage_key


# --- A. The four-case audit scenario ------------------------------------


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_a_audit_case_ready_then_boundaryless_unproven(mode: AdmissionMode, endpoint: str) -> None:
    """Bootstrap v1 -> proven mixed-only v2 -> Q ready -> trusted
    complete boundaryless root+A (changed root, no independent
    singleton) -> Q root_currentness_unproven with no usable
    selected source; P authority-only selection remains its same
    correct contract; the unknown root member hash stays unknown;
    original bootstrap/proofs/occurrences/owner/frozen links are
    retained by identity."""
    ns, state1 = q_bootstrap(mode, f"audit-{mode.value}-{endpoint}")
    root_body = "Second root."
    state2 = q_observe(
        q_issue(state1, ns, "v2", endpoint, MIX_CMD, (CAUSAL_ROOT_FACT,)),
        ns,
        endpoint,
        "v2",
        mixed_body(A_TEXT, MARK, root_body),
        MIX_CMD,
    )
    r2 = q_result(state2, ns)
    assert r2.outcome is RootRegionCurrentnessOutcome.READY
    assert r2.usable_selected_source_digest == sha256_hex(root_body)
    assert r2.p_selection is not None
    assert r2.p_selection.outcome is RootSelectionOutcome.OK
    assert r2.p_selection.selected_source_digest == sha256_hex(root_body)
    assert not r2.uncertainty_witnesses
    assert not r2.diagnostics
    assert not r2.p_validation_problem
    assert_state_identity(r2, state2)

    v2 = q_occ(state2, "v2")
    v2_fact = next(f for f in state2.root_facts if f.provenance.kind == "read_region")
    anchor = q_anchor_fact(state2)
    state3 = q_observe(
        q_issue(state2, ns, "v3", endpoint, BOUNDARYLESS_CMD, (v2.occurrence_id,)),
        ns,
        endpoint,
        "v3",
        OPAQUE_BODY,
        BOUNDARYLESS_CMD,
    )
    v3 = q_occ(state3, "v3")
    assert v3.anchored
    seg = v3.proof.segments[0]
    assert seg.member_digest is None
    assert len(seg.member_positions) == 2

    r3 = q_result(state3, ns)
    assert r3.outcome is RootRegionCurrentnessOutcome.ROOT_CURRENTNESS_UNPROVEN
    assert r3.usable_selected_source_digest is None
    assert r3.p_selection is not None
    assert r3.p_selection.outcome is RootSelectionOutcome.OK
    assert r3.p_selection.selected_source_digest == sha256_hex(root_body)
    assert len(r3.uncertainty_witnesses) == 1
    w = r3.uncertainty_witnesses[0]
    assert w.occurrence is v3
    assert w.uncertainty_class.value == "opaque_root_bearing_group"
    assert w.root_operand_count == 1
    assert w.whole_proof_digest == v3.proof.source_digest
    assert w.whole_proof_byte_length == v3.proof.source_byte_length
    owner = next(r for r in state3.d_state.results if r.call_id == "v3" and r.endpoint == endpoint)
    assert owner.complete
    assert w.result_record is owner
    # Unknown root member hash stays unknown; no P fact minted for v3.
    assert not any(
        f.provenance.kind != "envelope" and f.provenance.occurrence_id == v3.occurrence_id
        for f in state3.root_facts
    )
    # Original identities retained by reference: the anchor fact and
    # the v2 occurrence keep object identity; the read_region fact
    # re-derives its flags on the accepted D transition (the S1 law)
    # and is compared by its ORIGINAL provenance/proof coordinates,
    # never by cross-transition object identity.
    assert q_anchor_fact(state3) is anchor
    v2_fact3 = next(f for f in state3.root_facts if f.provenance.kind == "read_region")
    assert v2_fact3.provenance is v2_fact.provenance
    assert v2_fact3.source_digest == v2_fact.source_digest
    assert v2_fact3.source_byte_length == v2_fact.source_byte_length
    assert v2_fact3.issued is True and v2_fact3.authority is True
    assert q_occ(state3, "v2") is v2
    assert state3.d_state.root is not None
    assert len(state3.d_state.parent_links) == len(state2.d_state.parent_links) + 1
    assert_state_identity(r3, state3)
    # Idempotent query: no revision advance, no state mutation.
    r3b = q_result(state3, ns)
    assert r3b.state is state3
    assert r3b.revision == state3.revision
    assert state3.d_state.revision == r3b.revision


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_a_p_selection_unchanged_contract(mode: AdmissionMode, endpoint: str) -> None:
    """On the audit state the actual P public selection is still the
    same correct authority-only contract (ok at the known root, no
    unproven limitation invented by Q)."""
    ns, state1 = q_bootstrap(mode, f"audit-p-{mode.value}-{endpoint}")
    root_body = "Second root."
    state2 = q_observe(
        q_issue(state1, ns, "v2", endpoint, MIX_CMD, (CAUSAL_ROOT_FACT,)),
        ns,
        endpoint,
        "v2",
        mixed_body(A_TEXT, MARK, root_body),
        MIX_CMD,
    )
    v2 = q_occ(state2, "v2")
    state3 = q_observe(
        q_issue(state2, ns, "v3", endpoint, BOUNDARYLESS_CMD, (v2.occurrence_id,)),
        ns,
        endpoint,
        "v3",
        OPAQUE_BODY,
        BOUNDARYLESS_CMD,
    )
    sel = select_current_root_region(state3, ns)
    assert sel.outcome is RootSelectionOutcome.OK
    assert sel.selected_source_digest == sha256_hex(root_body)
    assert sel.limitations == ()
    assert validate_root_region_lineage_state(state3, ns.root_lineage_bounds) is None
    # The Q result carries the ACTUAL same-run selection by reference.
    r3 = q_result(state3, ns)
    assert r3.p_selection is not None
    assert r3.p_selection.outcome is RootSelectionOutcome.OK
    assert r3.p_selection.selected_source_digest == sha256_hex(root_body)


# --- B. Combined-frontier matrix ----------------------------------------


def _frontier_state(mode: AdmissionMode, endpoint: str, lineage: str) -> tuple[Any, Any, Any]:
    """Bootstrap + proven v2 + two incomparable opaque branches on the
    ACTUAL given endpoint (both endpoints genuinely exercised)."""
    ns, state = q_bootstrap(mode, lineage)
    state = q_observe(
        q_issue(state, ns, "v2", endpoint, MIX_CMD, (CAUSAL_ROOT_FACT,)),
        ns,
        endpoint,
        "v2",
        mixed_body(A_TEXT, MARK, "Root B2."),
        MIX_CMD,
    )
    v2 = q_occ(state, "v2")
    state = q_observe(
        q_issue(state, ns, "ua", endpoint, BOUNDARYLESS_CMD, (v2.occurrence_id,)),
        ns,
        endpoint,
        "ua",
        OPAQUE_BODY,
        BOUNDARYLESS_CMD,
    )
    state = q_observe(
        q_issue(state, ns, "ub", endpoint, BOUNDARYLESS_CMD, (v2.occurrence_id,)),
        ns,
        endpoint,
        "ub",
        OPAQUE_BODY,
        BOUNDARYLESS_CMD,
    )
    return ns, state, v2


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_b_dominated_opaque_restores_ready(mode: AdmissionMode, endpoint: str) -> None:
    """An uncertainty ancestor strictly descended from a genuinely
    later supported authoritative root witness cannot displace it:
    the dominated witness is retained but readiness returns."""
    ns, state = q_bootstrap(mode, f"dom-{mode.value}-{endpoint}")
    state = q_observe(
        q_issue(state, ns, "v2", endpoint, MIX_CMD, (CAUSAL_ROOT_FACT,)),
        ns,
        endpoint,
        "v2",
        mixed_body(A_TEXT, MARK, "R2."),
        MIX_CMD,
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
    r = q_result(state, ns)
    assert r.outcome is RootRegionCurrentnessOutcome.ROOT_CURRENTNESS_UNPROVEN
    assert len(r.uncertainty_witnesses) == 1
    u1 = q_occ(state, "u1")
    state = q_observe(
        q_issue(state, ns, "v3", endpoint, MIX_CMD, (u1.occurrence_id,)),
        ns,
        endpoint,
        "v3",
        mixed_body(A_TEXT, MARK, "R3."),
        MIX_CMD,
    )
    r = q_result(state, ns)
    assert r.outcome is RootRegionCurrentnessOutcome.READY
    assert r.usable_selected_source_digest == sha256_hex("R3.")
    # The dominated witness stays retained (no evidence erased).
    assert len(r.uncertainty_witnesses) == 1
    assert r.uncertainty_witnesses[0].occurrence is u1


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_b_child_of_one_stays_blocked(mode: AdmissionMode, endpoint: str) -> None:
    """Two unresolved incomparable opaque branches: a known witness
    descending from ONLY one branch leaves the other maximal --
    fixed unproven, no usable source, no invented edges."""
    ns, state, v2 = _frontier_state(mode, endpoint, f"child1-{mode.value}-{endpoint}")
    ua, ub = q_occ(state, "ua"), q_occ(state, "ub")
    r = q_result(state, ns)
    assert r.outcome is RootRegionCurrentnessOutcome.ROOT_CURRENTNESS_UNPROVEN
    assert {w.occurrence_id for w in r.uncertainty_witnesses} == {
        ua.occurrence_id,
        ub.occurrence_id,
    }
    state = q_observe(
        q_issue(state, ns, "va", endpoint, MIX_CMD, (ua.occurrence_id,)),
        ns,
        endpoint,
        "va",
        mixed_body(A_TEXT, MARK, "R4."),
        MIX_CMD,
    )
    r = q_result(state, ns)
    assert r.outcome is RootRegionCurrentnessOutcome.ROOT_CURRENTNESS_UNPROVEN
    assert r.usable_selected_source_digest is None
    assert {w.occurrence_id for w in r.uncertainty_witnesses} == {
        ua.occurrence_id,
        ub.occurrence_id,
    }
    # The known maxima are still an actual OK P selection.
    assert r.p_selection is not None
    assert r.p_selection.outcome is RootSelectionOutcome.OK
    assert r.p_selection.selected_source_digest == sha256_hex("R4.")


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_b_joint_coverage_restores_ready(mode: AdmissionMode, endpoint: str) -> None:
    """Compatible equal-byte known maxima jointly covering the
    branches restore readiness WITHOUT inventing Va<->Vb edges
    (neither descends the other)."""
    ns, state, v2 = _frontier_state(mode, endpoint, f"joint-{mode.value}-{endpoint}")
    ua, ub = q_occ(state, "ua"), q_occ(state, "ub")
    state = q_observe(
        q_issue(state, ns, "va", endpoint, MIX_CMD, (ua.occurrence_id,)),
        ns,
        endpoint,
        "va",
        mixed_body(A_TEXT, MARK, "R4."),
        MIX_CMD,
    )
    va = q_occ(state, "va")
    state = q_observe(
        q_issue(state, ns, "vb", endpoint, MIX_CMD, (ub.occurrence_id,)),
        ns,
        endpoint,
        "vb",
        mixed_body(A_TEXT, MARK, "R4."),
        MIX_CMD,
    )
    vb = q_occ(state, "vb")
    # No frozen edge between the compatible maxima.
    edges = {(link.child, link.parent) for link in state.d_state.parent_links}
    assert (vb.occurrence_id, va.occurrence_id) not in edges
    assert (va.occurrence_id, vb.occurrence_id) not in edges
    r = q_result(state, ns)
    assert r.outcome is RootRegionCurrentnessOutcome.READY
    assert r.usable_selected_source_digest == sha256_hex("R4.")
    assert len(r.uncertainty_witnesses) == 2  # both dominated, retained
    assert {w.occurrence_id for w in r.uncertainty_witnesses} == {
        ua.occurrence_id,
        ub.occurrence_id,
    }
    # P retains BOTH actual original witnesses.
    assert r.p_selection is not None
    assert len(r.p_selection.witness_facts) == 2


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_b_old_bytes_revert_restores(mode: AdmissionMode, endpoint: str) -> None:
    """A genuinely NEW supported descendant of ALL unresolved maximal
    branches with the OLD root bytes restores that version (a
    deliberate revert), while a later equal-byte opaque child keeps
    blocking until a genuine descendant of all arrives."""
    ns, state, v2 = _frontier_state(mode, endpoint, f"revert-{mode.value}-{endpoint}")
    ua, ub = q_occ(state, "ua"), q_occ(state, "ub")
    state = q_observe(
        q_issue(state, ns, "va", endpoint, MIX_CMD, (ua.occurrence_id,)),
        ns,
        endpoint,
        "va",
        mixed_body(A_TEXT, MARK, "R4."),
        MIX_CMD,
    )
    va = q_occ(state, "va")
    state = q_observe(
        q_issue(state, ns, "vb", endpoint, MIX_CMD, (ub.occurrence_id,)),
        ns,
        endpoint,
        "vb",
        mixed_body(A_TEXT, MARK, "R4."),
        MIX_CMD,
    )
    vb = q_occ(state, "vb")
    state = q_observe(
        q_issue(state, ns, "uc", endpoint, BOUNDARYLESS_CMD, (vb.occurrence_id,)),
        ns,
        endpoint,
        "uc",
        OPAQUE_BODY,
        BOUNDARYLESS_CMD,
    )
    uc = q_occ(state, "uc")
    r = q_result(state, ns)
    assert r.outcome is RootRegionCurrentnessOutcome.ROOT_CURRENTNESS_UNPROVEN
    # Genuine revert: descendant of the known va AND the unknown uc,
    # carrying v2's original root bytes.
    state = q_observe(
        q_issue(state, ns, "vr", endpoint, MIX_CMD, (va.occurrence_id, uc.occurrence_id)),
        ns,
        endpoint,
        "vr",
        mixed_body(A_TEXT, MARK, "Root B2."),
        MIX_CMD,
    )
    r = q_result(state, ns)
    assert r.outcome is RootRegionCurrentnessOutcome.READY
    assert r.usable_selected_source_digest == sha256_hex("Root B2.")
    # All three uncertainties are now dominated and retained.
    assert {w.occurrence_id for w in r.uncertainty_witnesses} == {
        ua.occurrence_id,
        ub.occurrence_id,
        uc.occurrence_id,
    }


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_b_singleton_descendant_of_all_restores(mode: AdmissionMode, endpoint: str) -> None:
    """A genuinely NEW supported WHOLE singleton root occurrence
    descended from ALL unresolved maximal branches restores readiness
    (a later supported known witness need not be forced into region
    form: both P whole and region sources qualify)."""
    ns, state, _v2 = _frontier_state(mode, endpoint, f"single-{mode.value}-{endpoint}")
    ua, ub = q_occ(state, "ua"), q_occ(state, "ub")
    state = q_observe(
        q_issue(state, ns, "vs", endpoint, "cat AGENTS.md", (ua.occurrence_id, ub.occurrence_id)),
        ns,
        endpoint,
        "vs",
        "Singleton of all.\n",
        "cat AGENTS.md",
    )
    r = q_result(state, ns)
    assert r.outcome is RootRegionCurrentnessOutcome.READY
    assert r.usable_selected_source_digest == sha256_hex("Singleton of all.\n")
    assert {w.occurrence_id for w in r.uncertainty_witnesses} == {
        ua.occurrence_id,
        ub.occurrence_id,
    }
    assert r.p_selection is not None
    assert r.p_selection.outcome is RootSelectionOutcome.OK
    # The whole singleton read fact is the selected witness.
    assert [f.provenance.kind for f in r.p_selection.witness_facts] == ["read"]
    assert_state_identity(r, state)


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_b_replay_reversed_operand_equal_byte_no_edges(mode: AdmissionMode, endpoint: str) -> None:
    """Replays, reversed request permutations and equal-byte
    uncertainties add no causal edges and never suppress unknown
    evidence: the retained uncertainty set is invariant (the delayed
    original receipt case is the row-4 delayed qualification, tested
    in C)."""
    ns, state, v2 = _frontier_state(mode, endpoint, f"perm-{mode.value}-{endpoint}")
    ua, ub = q_occ(state, "ua"), q_occ(state, "ub")
    # Replay of the ua observation: no new occurrence, no new edge.
    replay = observe_root_region_lineage(
        state,
        ns,
        state.revision,
        (read_request(endpoint, "ua", OPAQUE_BODY, BOUNDARYLESS_CMD),),
    )
    assert replay.outcome.value == "replayed"
    assert replay.state is state
    r = q_result(state, ns)
    assert r.outcome is RootRegionCurrentnessOutcome.ROOT_CURRENTNESS_UNPROVEN
    assert {w.occurrence_id for w in r.uncertainty_witnesses} == {
        ua.occurrence_id,
        ub.occurrence_id,
    }
    # Reversed request permutation: the SAME two members with the root
    # operand LAST is a distinct occurrence (root position 1, not 0);
    # no edge is invented and the classification is unchanged.
    state = q_observe(
        q_issue(state, ns, "ur", endpoint, BOUNDARYLESS_REV_CMD, (v2.occurrence_id,)),
        ns,
        endpoint,
        "ur",
        A_TEXT + OPAQUE_BODY,
        BOUNDARYLESS_REV_CMD,
    )
    ur = q_occ(state, "ur")
    r = q_result(state, ns)
    assert r.outcome is RootRegionCurrentnessOutcome.ROOT_CURRENTNESS_UNPROVEN
    assert len(r.uncertainty_witnesses) == 3
    assert {w.occurrence_id for w in r.uncertainty_witnesses} == {
        ua.occurrence_id,
        ub.occurrence_id,
        ur.occurrence_id,
    }
    w_ur = next(w for w in r.uncertainty_witnesses if w.occurrence_id == ur.occurrence_id)
    assert w_ur.uncertainty_class is RootRegionUncertaintyClass.OPAQUE_ROOT_BEARING_GROUP
    assert w_ur.root_operand_count == 1
    # Equal-byte uncertainty on a fourth branch: distinct witnesses,
    # no digest-based dedup, no invented dominance.
    state = q_observe(
        q_issue(state, ns, "uc", endpoint, BOUNDARYLESS_CMD, (v2.occurrence_id,)),
        ns,
        endpoint,
        "uc",
        OPAQUE_BODY,
        BOUNDARYLESS_CMD,
    )
    uc = q_occ(state, "uc")
    r = q_result(state, ns)
    assert r.outcome is RootRegionCurrentnessOutcome.ROOT_CURRENTNESS_UNPROVEN
    assert len(r.uncertainty_witnesses) == 4
    ids = {w.occurrence_id for w in r.uncertainty_witnesses}
    assert ua.occurrence_id in ids and ub.occurrence_id in ids
    assert ur.occurrence_id in ids and uc.occurrence_id in ids
    # Canonical deterministic metadata order.
    keys = [(w.uncertainty_class.value, w.occurrence_id) for w in r.uncertainty_witnesses]
    assert keys == sorted(keys)


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_b_delayed_result_and_arrival_permutations_no_edges(
    mode: AdmissionMode, endpoint: str
) -> None:
    """Actual delayed tool-result and original request-arrival
    permutations invent NO causal edges (the frozen frontier is the
    only edge source): a delayed sibling result after a known child
    blocks without an invented edge, the opposite arrival matches,
    and forward/reversed two-request batches observe identically."""
    ns, state = q_bootstrap(mode, f"arriv-{mode.value}-{endpoint}")
    state = q_issue(state, ns, "ua", endpoint, BOUNDARYLESS_CMD, (CAUSAL_ROOT_FACT,))
    state = q_issue(state, ns, "ub", endpoint, BOUNDARYLESS_CMD, (CAUSAL_ROOT_FACT,))
    req_a = read_request(endpoint, "ua", OPAQUE_BODY, BOUNDARYLESS_CMD)
    req_b = read_request(endpoint, "ub", OPAQUE_BODY, BOUNDARYLESS_CMD)
    # Only ua observed; a known proven child of ua restores readiness.
    only_a_t = observe_root_region_lineage(state, ns, state.revision, (req_a,))
    assert only_a_t.outcome.value == "accepted", only_a_t.diagnostics
    only_a = only_a_t.state
    ua = q_occ(only_a, "ua")
    va_state = q_observe(
        q_issue(only_a, ns, "va", endpoint, MIX_CMD, (ua.occurrence_id,)),
        ns,
        endpoint,
        "va",
        mixed_body(A_TEXT, MARK, "Known Va."),
        MIX_CMD,
    )
    rk = q_result(va_state, ns)
    assert rk.outcome is RootRegionCurrentnessOutcome.READY
    assert rk.usable_selected_source_digest == sha256_hex("Known Va.")
    # The DELAYED ub result now blocks: no invented Va<->Ub edge, and
    # the ACTUAL same-run P selection still carries the known Va.
    delayed_t = observe_root_region_lineage(va_state, ns, va_state.revision, (req_b,))
    assert delayed_t.outcome.value == "accepted", delayed_t.diagnostics
    delayed = delayed_t.state
    rd = q_result(delayed, ns)
    assert rd.outcome is RootRegionCurrentnessOutcome.ROOT_CURRENTNESS_UNPROVEN
    assert rd.usable_selected_source_digest is None
    assert rd.p_selection is not None
    assert rd.p_selection.selected_source_digest == rk.p_selection.selected_source_digest
    ua_d, ub_d, va_d = (q_occ(delayed, c) for c in ("ua", "ub", "va"))
    edges = {(link.child, link.parent) for link in delayed.d_state.parent_links}
    assert (ub_d.occurrence_id, CAUSAL_ROOT_FACT) in edges
    assert (va_d.occurrence_id, ua_d.occurrence_id) in edges
    assert (ub_d.occurrence_id, va_d.occurrence_id) not in edges
    assert (va_d.occurrence_id, ub_d.occurrence_id) not in edges
    assert {w.call_id for w in rd.uncertainty_witnesses} == {"ua", "ub"}
    for w in rd.uncertainty_witnesses:
        assert w.occurrence is q_occ(delayed, w.call_id)
    # Opposite arrival: the ub result BEFORE the known va child gives
    # the SAME final semantics (no rollback, no invented edge).
    early_b_t = observe_root_region_lineage(only_a, ns, only_a.revision, (req_b,))
    assert early_b_t.outcome.value == "accepted", early_b_t.diagnostics
    early_b = early_b_t.state
    ua_e = q_occ(early_b, "ua")
    early_final = q_observe(
        q_issue(early_b, ns, "va", endpoint, MIX_CMD, (ua_e.occurrence_id,)),
        ns,
        endpoint,
        "va",
        mixed_body(A_TEXT, MARK, "Known Va."),
        MIX_CMD,
    )
    re = q_result(early_final, ns)
    assert re.outcome is RootRegionCurrentnessOutcome.ROOT_CURRENTNESS_UNPROVEN
    assert re.p_selection is not None
    assert re.p_selection.selected_source_digest == rd.p_selection.selected_source_digest
    assert {w.call_id for w in re.uncertainty_witnesses} == {"ua", "ub"}
    # Actual two-request batches: forward AND reversed original
    # request order observe identically (all links still to the
    # anchor; no edge between the siblings).
    for requests in ((req_a, req_b), (req_b, req_a)):
        st = observe_root_region_lineage(state, ns, state.revision, tuple(requests))
        assert st.outcome.value == "accepted", st.diagnostics
        rr = q_result(st.state, ns)
        assert rr.outcome is RootRegionCurrentnessOutcome.ROOT_CURRENTNESS_UNPROVEN
        assert {w.call_id for w in rr.uncertainty_witnesses} == {"ua", "ub"}
        assert all(link.parent == CAUSAL_ROOT_FACT for link in st.state.d_state.parent_links)


# --- C. Closed evidence-table exclusions --------------------------------


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_c_nonroot_only_opaque_no_root_uncertainty(mode: AdmissionMode, endpoint: str) -> None:
    """A complete NONROOT-only opaque group does not become root
    uncertainty (row 6); the anchor stays known and usable."""
    ns, state = q_bootstrap(mode, f"nonroot-{mode.value}-{endpoint}")
    state = q_observe(
        q_issue(state, ns, "nr", endpoint, NONROOT_CMD, (CAUSAL_ROOT_FACT,)),
        ns,
        endpoint,
        "nr",
        A_TEXT + B_TEXT,
        NONROOT_CMD,
    )
    # P: no root fact is minted for the nonroot read.
    assert not any(f.provenance.kind != "envelope" for f in state.root_facts)
    r = q_result(state, ns)
    assert r.outcome is RootRegionCurrentnessOutcome.READY
    assert r.usable_selected_source_digest == sha256_hex("Initial root.")
    assert not r.uncertainty_witnesses
    assert_state_identity(r, state)


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_c_unissued_observation_then_delayed_receipt(mode: AdmissionMode, endpoint: str) -> None:
    """Unissued/unanchored observations contribute no uncertainty
    (row 4); a later genuine delayed receipt qualifies the SAME
    original retained occurrence under unchanged frozen ancestry --
    no reread, no new clock, and row 1: NO second uncertainty record
    for the P fact in any phase."""
    ns, state1 = q_bootstrap(mode, f"uniss-{mode.value}-{endpoint}")
    anchor_body = "Initial root."
    # Observe WITHOUT issuance: the mixed-only region is retained
    # unproven (unanchored, no parent edge of its own).
    t2 = observe_root_region_lineage(
        state1,
        ns,
        state1.revision,
        (read_request(endpoint, "u1", mixed_body(A_TEXT, MARK, anchor_body), MIX_CMD),),
    )
    assert t2.outcome.value == "accepted", t2.diagnostics
    state2 = t2.state
    u1 = q_occ(state2, "u1")
    assert u1.anchored is False
    f2 = next(f for f in state2.root_facts if f.provenance.kind == "read_region")
    assert f2.issued is False and f2.authority is False
    sel2 = select_current_root_region(state2, ns)
    assert sel2.outcome is RootSelectionOutcome.OK
    assert RootLineageLimitation.ROOT_SOURCE_UNPROVEN in sel2.limitations
    # Q: no uncertainty from the unissued occurrence; READY at anchor.
    r2 = q_result(state2, ns)
    assert r2.outcome is RootRegionCurrentnessOutcome.READY
    assert r2.usable_selected_source_digest == sha256_hex(anchor_body)
    assert not r2.uncertainty_witnesses
    assert r2.p_selection is not None
    assert RootLineageLimitation.ROOT_SOURCE_UNPROVEN in r2.p_selection.limitations
    assert_state_identity(r2, state2)
    # A later actual ISSUANCE alone never anchors (no authority).
    state3 = q_issue(state2, ns, "u1", endpoint, MIX_CMD, (CAUSAL_ROOT_FACT,))
    u3 = q_occ(state3, "u1")
    assert u3 is u1 and u3.anchored is False
    f3 = next(f for f in state3.root_facts if f.provenance.kind == "read_region")
    assert f3.issued is True and f3.authority is False
    r3 = q_result(state3, ns)
    assert r3.outcome is RootRegionCurrentnessOutcome.READY
    assert not r3.uncertainty_witnesses
    assert_state_identity(r3, state3)
    # The matching delayed receipt anchors the SAME retained occurrence.
    t4 = register_root_region_receipt(
        state3,
        ns,
        "u1",
        endpoint,
        "exec_command",
        json.dumps({"cmd": MIX_CMD}),
        (CAUSAL_ROOT_FACT,),
        state3.revision,
    )
    assert t4.outcome.value == "accepted", t4.diagnostics
    state4 = t4.state
    # The receipt immutably replaces the occurrence object with its
    # anchored re-derivation (the actual D law): same occurrence ID,
    # the ORIGINAL retained proof by identity, never the old object.
    u4 = q_occ(state4, "u1")
    assert u4 is not u1
    assert u4.occurrence_id == u1.occurrence_id
    assert u4.proof is u1.proof
    assert u4.anchored is True
    f4 = next(f for f in state4.root_facts if f.provenance.kind == "read_region")
    assert f4.issued is True and f4.authority is True
    # Equal-byte maxima are compatible: KNOWN governing source, READY,
    # and still NO uncertainty record for the P fact (row 1).
    r4 = q_result(state4, ns)
    assert r4.outcome is RootRegionCurrentnessOutcome.READY
    assert r4.usable_selected_source_digest == sha256_hex(anchor_body)
    assert not r4.uncertainty_witnesses
    assert_state_identity(r4, state4)


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_c_late_opaque_unissued_then_receipt_activates(mode: AdmissionMode, endpoint: str) -> None:
    """Row-4 activation on the OPAQUE path: an unissued unanchored
    root-bearing opaque group contributes nothing (READY); a genuine
    issuance ALONE leaves the completed retained source unanchored
    (no authority, no edge, no Q change); the matching delayed
    receipt qualifies the SAME original retained occurrence (exact
    original ID/proof/owner) and the Q result becomes UNPROVEN with a
    witness that IS the final anchored occurrence (no P fact minted)."""
    ns, state0 = q_bootstrap(mode, f"lateop-{mode.value}-{endpoint}")
    anchor_body = "Initial root."
    t1 = observe_root_region_lineage(
        state0,
        ns,
        state0.revision,
        (read_request(endpoint, "uo", OPAQUE_BODY, BOUNDARYLESS_CMD),),
    )
    assert t1.outcome.value == "accepted", t1.diagnostics
    state1 = t1.state
    original = q_occ(state1, "uo")
    assert original.anchored is False
    original_proof = original.proof
    original_owner = next(x for x in state1.d_state.results if x.call_id == "uo")
    assert original_owner.complete is True
    r0 = q_result(state1, ns)
    assert r0.outcome is RootRegionCurrentnessOutcome.READY
    assert r0.usable_selected_source_digest == sha256_hex(anchor_body)
    assert not r0.uncertainty_witnesses
    assert_state_identity(r0, state1)
    # A genuine issuance alone leaves the retained source unanchored.
    state2 = q_issue(state1, ns, "uo", endpoint, BOUNDARYLESS_CMD, (CAUSAL_ROOT_FACT,))
    u2 = q_occ(state2, "uo")
    assert u2 is original and u2.anchored is False
    r2 = q_result(state2, ns)
    assert r2.outcome is RootRegionCurrentnessOutcome.READY
    assert not r2.uncertainty_witnesses
    assert_state_identity(r2, state2)
    # The matching delayed receipt qualifies the same retained
    # occurrence (the anchored re-derivation immutably replaces the
    # object: same ID, ORIGINAL proof by identity).
    t3 = register_root_region_receipt(
        state2,
        ns,
        "uo",
        endpoint,
        "exec_command",
        json.dumps({"cmd": BOUNDARYLESS_CMD}),
        (CAUSAL_ROOT_FACT,),
        state2.revision,
    )
    assert t3.outcome.value == "accepted", t3.diagnostics
    state3 = t3.state
    final_occ = q_occ(state3, "uo")
    assert final_occ is not original
    assert final_occ.occurrence_id == original.occurrence_id
    assert final_occ.proof is original_proof
    assert final_occ.anchored is True
    assert not any(f.provenance.kind != "envelope" for f in state3.root_facts)
    # Q: the opaque group is now ACTIVE uncertainty; the witness IS
    # the final anchored occurrence with the ORIGINAL owner record.
    r3 = q_result(state3, ns)
    assert r3.outcome is RootRegionCurrentnessOutcome.ROOT_CURRENTNESS_UNPROVEN
    assert r3.usable_selected_source_digest is None
    assert len(r3.uncertainty_witnesses) == 1
    w = r3.uncertainty_witnesses[0]
    assert w.occurrence is final_occ
    assert w.result_record is original_owner
    assert w.uncertainty_class is RootRegionUncertaintyClass.OPAQUE_ROOT_BEARING_GROUP
    assert w.root_operand_count == 1
    assert w.whole_proof_digest == original_proof.source_digest
    assert w.whole_proof_byte_length == original_proof.source_byte_length
    assert_state_identity(r3, state3)


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
@pytest.mark.parametrize(
    ("cmd", "expected_count"),
    (
        (REPEAT_CMD, 2),
        (REPEAT3_CMD, 3),
        (REPEAT_OPAQUE_CMD, 2),
    ),
)
def test_c_repeated_root_operands_are_unsupported_evidence(
    mode: AdmissionMode, endpoint: str, cmd: str, expected_count: int
) -> None:
    """A qualifying complete root-bearing occurrence excluded by the
    P root source-shape policy (repeated root operands, two and three,
    including the hidden opaque second operand) is explicit
    unsupported-root-evidence uncertainty (row 3): the known member
    bytes are NOT called unknown and NO P authority fact is minted
    (the n==1 known-bytes subcase is unreachable under the current P
    region exception and is qualified as such in the contract)."""
    ns, state = q_bootstrap(mode, f"rep{expected_count}-{mode.value}-{endpoint}")
    anchor_body = "Initial root."
    if cmd is REPEAT_CMD:
        body = mixed_body(anchor_body, MARK, anchor_body)
    elif cmd is REPEAT3_CMD:
        # Boundaryless: one undifferentiated stream, no attribution,
        # three repeated root operands (the proven S-probe shape).
        body = anchor_body + anchor_body + anchor_body + A_TEXT
    else:
        body = mixed_body(anchor_body, MARK, anchor_body + B_TEXT)
    state = q_observe(
        q_issue(state, ns, "rp", endpoint, cmd, (CAUSAL_ROOT_FACT,)),
        ns,
        endpoint,
        "rp",
        body,
        cmd,
    )
    rp = q_occ(state, "rp")
    assert rp.anchored is True
    # P mints NO root fact for the repeated-root shape.
    assert not any(f.provenance.kind != "envelope" for f in state.root_facts)
    sel = select_current_root_region(state, ns)
    assert sel.outcome is RootSelectionOutcome.OK
    assert sel.selected_source_digest == sha256_hex(anchor_body)
    r = q_result(state, ns)
    assert r.outcome is RootRegionCurrentnessOutcome.ROOT_CURRENTNESS_UNPROVEN
    assert r.usable_selected_source_digest is None
    assert len(r.uncertainty_witnesses) == 1
    w = r.uncertainty_witnesses[0]
    assert w.occurrence is rp
    assert w.uncertainty_class is RootRegionUncertaintyClass.UNSUPPORTED_ROOT_SHAPE
    assert w.root_operand_count == expected_count
    # The P selection stays its same correct contract (no unproven
    # limitation: the known member bytes are not called unknown).
    assert r.p_selection is not None
    assert r.p_selection.outcome is RootSelectionOutcome.OK
    assert r.p_selection.selected_source_digest == sha256_hex(anchor_body)
    assert r.p_selection.limitations == ()
    assert_state_identity(r, state)


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_c_wrong_root_like_path_no_root_uncertainty(mode: AdmissionMode, endpoint: str) -> None:
    """A complete read of a root-LIKE but different normalized path
    does not become root uncertainty (row 6); the wrong path/workspace
    actual namespace/state binding is a D-row refusal, not an
    uncertainty."""
    ns, state = q_bootstrap(mode, f"wrongpath-{mode.value}-{endpoint}")
    state = q_observe(
        q_issue(state, ns, "wp", endpoint, WRONGPATH_CMD, (CAUSAL_ROOT_FACT,)),
        ns,
        endpoint,
        "wp",
        "Subdirectory root-like file.\n",
        WRONGPATH_CMD,
    )
    assert not any(f.provenance.kind != "envelope" for f in state.root_facts)
    r = q_result(state, ns)
    assert r.outcome is RootRegionCurrentnessOutcome.READY
    assert not r.uncertainty_witnesses
    assert_state_identity(r, state)


def _frame_request(endpoint: str, cid: str, cmd: str, frame_text: str) -> GraphRequest:
    """One original call/result request carrying a raw synthetic frame."""
    if endpoint == "responses":
        return GraphRequest(
            payload={"input": [exec_call(cid, cmd), out_item(cid, frame_text)]},
            endpoint="responses",
            context=None,
        )
    return GraphRequest(
        payload={
            "messages": [
                {
                    "role": "assistant",
                    "tool_calls": [
                        {
                            "id": cid,
                            "type": "function",
                            "function": {
                                "name": "exec_command",
                                "arguments": json.dumps({"cmd": cmd}),
                            },
                        }
                    ],
                },
                {"role": "tool", "tool_call_id": cid, "content": frame_text},
            ]
        },
        endpoint="chat",
        context=None,
    )


def _mixed_frame_request(endpoint: str, cid: str, frame: str) -> GraphRequest:
    """One original read request on EITHER endpoint carrying the given
    synthetic frame for the ACTUAL mixed root command."""
    return _frame_request(endpoint, cid, MIX_CMD, frame)


def _unpaired_frame_request(endpoint: str, cid: str, text: str) -> GraphRequest:
    """A result frame with NO causally paired call (a stray)."""
    if endpoint == "responses":
        return GraphRequest(
            payload={"input": [out_item(cid, text)]},
            endpoint="responses",
            context=None,
        )
    return GraphRequest(
        payload={"messages": [{"role": "tool", "tool_call_id": cid, "content": text}]},
        endpoint="chat",
        context=None,
    )


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_c_unacquired_shapes_cannot_poison_currentness(mode: AdmissionMode, endpoint: str) -> None:
    """Unsupported grammar, pending/partial, truncated, nonzero-exit and
    unpaired root-BEARING observations establish NO COMPLETED source
    occurrence and gain no uncertainty exception (row 5): their exact
    existing typed limitations/source retention are preserved and
    requesting a root path alone cannot poison currentness."""
    ns, state = q_bootstrap(mode, f"unacq-{mode.value}-{endpoint}")
    anchor_body = "Initial root."
    # (0) unsupported root-bearing read syntax: non-acquiring no-op.
    t0 = observe_root_region_lineage(
        state,
        ns,
        state.revision,
        (read_request(endpoint, "ua-0", A_TEXT, cmd="sed -n 1p AGENTS.md"),),
    )
    assert t0.outcome.value == "replayed"
    assert t0.state is state
    # (1) PENDING (incomplete) root-bearing mixed read: retained
    # honestly as a PARTIAL result, no occurrence.
    pending_frame = (
        "Chunk ID: a1b2c3\n"
        "Wall time: 0.0010 seconds\n"
        "Process running with session ID 9301\n"
        "Original token count: 4\n"
        f"Output:\n{A_TEXT}{MARK}\nPartial region."
    )
    t1 = observe_root_region_lineage(
        state, ns, state.revision, (_mixed_frame_request(endpoint, "ua-1", pending_frame),)
    )
    assert t1.outcome.value == "accepted"
    assert t1.state.d_state.occurrences == ()
    pend = [r for r in t1.state.d_state.results if r.call_id == "ua-1"]
    assert len(pend) == 1 and pend[0].complete is False
    # (2) ACTUAL earned TRUNCATION on a complete root-bearing mixed
    # frame: never complete; only the non-acquiring result record.
    warning = (
        f"Warning: truncated output (original token count: 512)\n"
        f"Total output lines: 64\n\n{mixed_body(A_TEXT, MARK, 'Region part.' + anchor_body)}"
    )
    truncated_frame = (
        "Chunk ID: 3d4e5f\n"
        "Wall time: 0.6789 seconds\n"
        "Process exited with code 0\n"
        "Original token count: 512\n"
        f"Output:\n{warning}"
    )
    t2 = observe_root_region_lineage(
        state, ns, state.revision, (_mixed_frame_request(endpoint, "ua-2", truncated_frame),)
    )
    assert t2.outcome.value == "accepted"
    assert t2.state.d_state.occurrences == ()
    trunc = [r for r in t2.state.d_state.results if r.call_id == "ua-2"]
    assert len(trunc) == 1 and trunc[0].complete is False
    # (3) nonzero-exit root-bearing mixed frame: no per-read completion.
    nonzero_frame = (
        "Chunk ID: synthetic\n"
        "Wall time: 0.0000 seconds\n"
        "Process exited with code 1\n"
        f"Output:\n{mixed_body(A_TEXT, MARK, anchor_body)}"
    )
    t3 = observe_root_region_lineage(
        state, ns, state.revision, (_mixed_frame_request(endpoint, "ua-3", nonzero_frame),)
    )
    assert t3.outcome.value == "replayed"
    assert t3.state is state
    # (4) unpaired stray result frame (no causally paired call): the
    # EXACT prior state is preserved.
    t4 = observe_root_region_lineage(
        state,
        ns,
        state.revision,
        (_unpaired_frame_request(endpoint, "ua-4", "Stray output frame.\n"),),
    )
    assert t4.outcome.value == "replayed"
    assert t4.state is state
    # Q: every retained state keeps the anchor known/usable; NO
    # uncertainty from any of the unacquired root-bearing shapes.
    for st in (state, t1.state, t2.state):
        r = q_result(st, ns)
        assert r.outcome is RootRegionCurrentnessOutcome.READY
        assert r.usable_selected_source_digest == sha256_hex(anchor_body)
        assert not r.uncertainty_witnesses
        assert_state_identity(r, st)


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_c_current_p_whole_and_region_positive(mode: AdmissionMode, endpoint: str) -> None:
    """Current P positive control (BOTH source forms): a whole
    singleton root read and a mixed-only region read are KNOWN
    governing witnesses under unchanged P law and earn NO uncertainty
    record (row 1)."""
    ns, state = q_bootstrap(mode, f"posctl-{mode.value}-{endpoint}")
    state = q_observe(
        q_issue(state, ns, "s1", endpoint, "cat AGENTS.md", (CAUSAL_ROOT_FACT,)),
        ns,
        endpoint,
        "s1",
        "Whole singleton root.\n",
        "cat AGENTS.md",
    )
    r = q_result(state, ns)
    assert r.outcome is RootRegionCurrentnessOutcome.READY
    assert r.usable_selected_source_digest == sha256_hex("Whole singleton root.\n")
    assert not r.uncertainty_witnesses
    assert_state_identity(r, state)
    s1 = q_occ(state, "s1")
    state = q_observe(
        q_issue(state, ns, "s2", endpoint, MIX_CMD, (s1.occurrence_id,)),
        ns,
        endpoint,
        "s2",
        mixed_body(A_TEXT, MARK, "Region root.\n"),
        MIX_CMD,
    )
    r = q_result(state, ns)
    assert r.outcome is RootRegionCurrentnessOutcome.READY
    assert r.usable_selected_source_digest == sha256_hex("Region root.\n")
    assert not r.uncertainty_witnesses
    assert_state_identity(r, state)


# --- D. Malformed / forged / coherent-rekey gates ------------------------


def _p_problem(bad: Any, ns: Any) -> Any:
    """The direct ACTUAL P validator under a fresh independent
    P-domain ledger with the SAME namespace kwargs the Q kernel
    passes (capped at the ACTUAL inherited P ceiling): the exact
    actual validation problem Q must carry."""
    return validate_root_region_lineage_state(
        bad,
        ns.root_lineage_bounds,
        _HOuter(ns.root_lineage_bounds.max_total_work_units),
        history_bounds=ns.history_bounds,
        graph_bounds=ns.graph_bounds,
        proof_bounds=ns.proof_bounds,
        observation_bounds=ns.observation_bounds,
        workspace=ns.workspace,
    )


@pytest.mark.parametrize("mode", MODES)
def test_d_malformed_non_p_state_refuses_before_result(mode: AdmissionMode) -> None:
    """Malformed non-P state objects fail with the fixed private
    ValueError BEFORE result construction (the explicit P/old-I
    boundary), never an honest no-root/uncertainty result: wrong
    object types, PARTIAL actual state instances (fields never set)
    and a wrong-shape (bool) revision on a complete model."""
    ns, state = q_bootstrap(mode, f"malformed-{mode.value}")
    for bad in (object(), {"state": True}, "a state", 42):
        with pytest.raises(ValueError, match="actual bounded state record"):
            derive_root_region_currentness(bad, ns)  # type: ignore[arg-type]
    # Partial ACTUAL state instances (the O(1) field-EXISTENCE
    # fence): only revision set (d_state missing -- it has no
    # model default, so the fence fires before any P shape work);
    # revision + lineage_key set (d_state still missing).
    partial = state.model_construct(revision=True)
    partial2 = state.model_construct(revision=1, lineage_key=state.lineage_key)
    for bad in (partial, partial2):
        with pytest.raises(ValueError, match="actual bounded state record"):
            derive_root_region_currentness(bad, ns)
    # A shape-VALID state whose DEFAULT-FILLED root_facts is empty
    # over the anchor-bearing D state is not a ValueError: the
    # ACTUAL P validation integrity law refuses it typed, carried
    # on the actual P problem channel, exact state retained.
    partial3 = state.model_construct(
        revision=1, lineage_key=state.lineage_key, d_state=state.d_state
    )
    r3 = q_result(partial3, ns)
    assert r3.outcome is RootRegionCurrentnessOutcome.REFUSED
    assert r3.p_selection is None
    assert r3.p_validation_problem is RootLineageLimitation.MALFORMED_BINDING
    assert r3.usable_selected_source_digest is None
    assert_state_identity(r3, partial3)
    # A wrong-shape revision (bool) on a complete model fails the
    # accepted P O(1) shape fence.
    forged = state.model_copy(update={"revision": True})
    with pytest.raises(ValueError, match="actual bounded state record"):
        derive_root_region_currentness(forged, ns)


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_d_foreign_scope_and_stale_key(mode: AdmissionMode, endpoint: str) -> None:
    """Wrong actual namespace/state bindings refuse before
    interpretation with the fixed typed scope diagnostic: two
    different valid namespace factories are foreign scopes; an
    ACTUAL stale/borrowed lineage key on the state, a copied
    namespace field tamper RETAINING the old keys (the full ns
    revalidation refuses) and a partial actual namespace instance
    all refuse foreign scope.  The exact prior state is preserved
    and no P result is invented."""
    ns, state = q_bootstrap(mode, f"scope-{mode.value}-{endpoint}")
    lineage = f"scope-{mode.value}-{endpoint}"
    identity2 = RequestIdentity(
        principal="other-principal",
        session="other-session",
        repository="other-repo",
        route="other-route",
    )
    admission2 = make_bundle_admission_namespace(
        identity2,
        model_identity="synthetic-currentness-model",
        config_fingerprint=FINGERPRINT,
        workspace=WORKSPACE,
        mode=mode,
    )
    # Same lineage ID over a DIFFERENT D scope: a foreign scope.
    ns_other_scope = make_root_region_lineage_namespace(admission2, lineage)
    r = q_result(state, ns_other_scope)
    assert r.outcome is RootRegionCurrentnessOutcome.REFUSED
    assert [d.value for d in r.diagnostics] == ["foreign_scope"]
    assert r.p_selection is None
    assert r.p_validation_problem is None
    assert r.usable_selected_source_digest is None
    assert_state_identity(r, state)
    # A second different valid namespace factory (different lineage
    # ID, same shape): foreign scope as well.
    ns_stale = make_root_region_lineage_namespace(admission2, f"stale-{mode.value}")
    r2 = q_result(state, ns_stale)
    assert r2.outcome is RootRegionCurrentnessOutcome.REFUSED
    assert [d.value for d in r2.diagnostics] == ["foreign_scope"]
    assert r2.p_selection is None
    assert_state_identity(r2, state)
    # An ACTUAL stale/borrowed key: the state's lineage key copied
    # from the OTHER scope over the genuine namespace.
    borrowed = state.model_copy(update={"lineage_key": ns_other_scope.lineage_key})
    assert borrowed.lineage_key != state.lineage_key
    r3 = q_result(borrowed, ns)
    assert r3.outcome is RootRegionCurrentnessOutcome.REFUSED
    assert [d.value for d in r3.diagnostics] == ["foreign_scope"]
    assert r3.p_selection is None
    assert_state_identity(r3, borrowed)
    # A copied namespace field tamper RETAINING the old keys: the
    # key fences pass but the FULL ns revalidation refuses.
    ns_tampered = ns.model_copy(update={"workspace": "/workX"})
    assert ns_tampered.lineage_key == ns.lineage_key
    assert ns_tampered.history_key == ns.history_key
    r4 = q_result(state, ns_tampered)
    assert r4.outcome is RootRegionCurrentnessOutcome.REFUSED
    assert [d.value for d in r4.diagnostics] == ["foreign_scope"]
    assert r4.p_selection is None
    assert_state_identity(r4, state)
    # A partial ACTUAL namespace instance (fields never set): a
    # typed foreign-scope refusal in the default domain, never an
    # internal error.
    ns_partial = ns.model_construct(history_version=ns.history_version)
    r5 = q_result(state, ns_partial)
    assert r5.outcome is RootRegionCurrentnessOutcome.REFUSED
    assert [d.value for d in r5.diagnostics] == ["foreign_scope"]
    assert r5.p_selection is None
    assert r5.bounds == RootRegionCurrentnessBounds()
    assert r5.scope_key == q_scope_key(state, RootRegionCurrentnessBounds())
    assert_state_identity(r5, state)


@pytest.mark.parametrize("mode", MODES)
def test_d_stale_version_fence(mode: AdmissionMode) -> None:
    """A stale version control: an ACTUAL unsupported D version on
    a COPIED namespace whose keys are NOT recomputed (a stale key
    copy) -- the scope fences still match the unchanged key, so
    the version-pair fence refuses the unsupported version with
    the fixed diagnostic, exact prior state, no P result.  (A
    COHERENT rekey that does recompute the key is the separate
    coherent-rekey test; changing a recipe-input version there
    moves the key, while this copied D version does not.)"""
    ns, state = q_bootstrap(mode, f"version-{mode.value}")
    bad = ns.model_copy(update={"history_version": "unsupported-causal-history/v0"})
    assert bad.lineage_key == ns.lineage_key  # stale: copied, not recomputed
    r = q_result(state, bad)
    assert r.outcome is RootRegionCurrentnessOutcome.REFUSED
    assert [d.value for d in r.diagnostics] == ["version_unsupported"]
    assert r.p_selection is None
    assert r.p_validation_problem is None
    assert r.usable_selected_source_digest is None
    assert_state_identity(r, state)


@pytest.mark.parametrize("mode", MODES)
def test_d_coherent_rekeyed_unsupported_version(mode: AdmissionMode) -> None:
    """A coherently rekeyed ACTUAL unsupported contract version
    (the accepted P c2/c3 pattern: the lineage key honestly
    recomputed for v2 through the actual _lineage_key recipe): the
    scope fence PRECEDES the version fence (a coherent v2 namespace
    over the genuine v1 state refuses foreign scope), and a
    namespace AND state rekeyed to the SAME coherent v2 key still
    refuses the unsupported version (scope identity alone is not
    version support)."""
    ns, state = q_bootstrap(mode, f"coherent-ver-{mode.value}")
    v2 = "cache-root-region-lineage/v2"
    k2 = _lineage_key(
        ns.history_key, v2, ROOT_REGION_LINEAGE_POLICY_VERSION, ns.root_lineage_bounds
    )
    ns_v2 = ns.model_copy(update={"contract_version": v2, "lineage_key": k2})
    assert ns_v2.lineage_key == k2
    assert ns_v2.lineage_key != state.lineage_key
    # (c2) the coherent v2 namespace over the genuine v1 state: the
    # lineage-key scope fence precedes the version-support fence.
    r = q_result(state, ns_v2)
    assert r.outcome is RootRegionCurrentnessOutcome.REFUSED
    assert [d.value for d in r.diagnostics] == ["foreign_scope"]
    assert r.p_selection is None
    assert_state_identity(r, state)
    # (c3) namespace AND state rekeyed to the SAME coherent v2 key:
    # scope matches, the version-pair fence still refuses.
    state_v2 = state.model_copy(update={"lineage_key": k2})
    r2 = q_result(state_v2, ns_v2)
    assert r2.outcome is RootRegionCurrentnessOutcome.REFUSED
    assert [d.value for d in r2.diagnostics] == ["version_unsupported"]
    assert r2.p_selection is None
    assert r2.p_validation_problem is None
    assert r2.usable_selected_source_digest is None
    assert_state_identity(r2, state_v2)


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_d_forged_state_refuses_with_actual_p_problem(mode: AdmissionMode, endpoint: str) -> None:
    """Forged derived flags and a revision/consistency tamper refuse
    through the ACTUAL P validation (invoked under the same budget):
    the Q result carries the ACTUAL P validation reason -- exactly
    the one the direct P validator reports -- with p_selection still
    None (a P selection is never fabricated)."""
    ns, state1 = q_bootstrap(mode, f"forged-{mode.value}-{endpoint}")
    state2 = q_observe(
        q_issue(state1, ns, "s1", endpoint, "cat AGENTS.md", (CAUSAL_ROOT_FACT,)),
        ns,
        endpoint,
        "s1",
        "Forged base root.\n",
        "cat AGENTS.md",
    )
    read_fact = next(f for f in state2.root_facts if f.provenance.kind == "read")
    forged_fact = read_fact.model_copy(update={"issued": False})
    bad = state2.model_copy(
        update={
            "root_facts": tuple(forged_fact if x is read_fact else x for x in state2.root_facts)
        }
    )
    expected = _p_problem(bad, ns)
    assert expected is not None
    r = q_result(bad, ns)
    assert r.outcome is RootRegionCurrentnessOutcome.REFUSED
    assert r.p_validation_problem is expected
    assert r.p_selection is None
    assert r.usable_selected_source_digest is None
    assert r.diagnostics == ()
    assert_state_identity(r, bad)
    # A revision/consistency tamper (the 1:1 D law broken).
    bad2 = state2.model_copy(update={"revision": state2.revision + 1})
    expected2 = _p_problem(bad2, ns)
    assert expected2 is not None
    r2 = q_result(bad2, ns)
    assert r2.outcome is RootRegionCurrentnessOutcome.REFUSED
    assert r2.p_validation_problem is expected2
    assert r2.p_selection is None
    assert_state_identity(r2, bad2)


@pytest.mark.parametrize(
    "forge",
    [
        _j_forge_flag,
        _j_forge_detached_occurrence,
        _j_forge_coherent_rekey,
        _j_forge_segment_swap,
        _j_forge_endpoint_mismatch,
        _j_forge_owner_mismatch,
        _j_forge_wrong_root_path,
        _j_forge_whole_proof_digest,
        _j_forge_whole_proof_length,
        _j_forge_root_member_length,
        _j_forge_original_proof_identity,
        _j_forge_d_owner_missing,
        _j_forge_d_owner_rekeyed,
    ],
    ids=[
        "flag-mismatch",
        "detached-occurrence",
        "coherent-rekey",
        "segment-swap",
        "endpoint-mismatch",
        "owner-mismatch",
        "wrong-root-path",
        "whole-proof-digest",
        "whole-proof-length",
        "root-member-length",
        "original-proof-identity",
        "d-owner-missing",
        "d-owner-rekeyed",
    ],
)
@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_d_forged_joins_refused_with_actual_p_problem(
    forge: Any, mode: AdmissionMode, endpoint: str
) -> None:
    """After a GENUINE P positive, every actual proof/complete-owner/
    producer-association/anchoring malformed join (the accepted P
    positive-then-forgery patterns) is refused by the Q public
    derivation with the EXACT actual P validation problem -- the
    same reason the direct P validator reports under a fresh
    independent P-domain ledger -- with p_selection still None
    (never fabricated) and the exact forged state retained.  For
    the D-level ownership forges the OLD D validator law alone
    stays coherent (None): the NEW region join is what refuses."""
    ns, good = _g_setup(mode, endpoint)
    sel0 = select_current_root_region(good, ns)
    assert sel0.outcome is RootSelectionOutcome.OK
    assert sel0.selected_source_digest is not None
    # The explicit Q POSITIVE on this SAME good fixture before any
    # forgery is applied: READY, usable selected source, exact
    # state retained.
    r0 = q_result(good, ns)
    assert r0.outcome is RootRegionCurrentnessOutcome.READY
    assert r0.usable_selected_source_digest == sel0.selected_source_digest
    assert r0.p_selection is not None
    assert r0.p_selection.outcome is RootSelectionOutcome.OK
    assert r0.p_selection.selected_source_digest == sel0.selected_source_digest
    assert not r0.uncertainty_witnesses
    assert_state_identity(r0, good)
    bad = forge(good)
    assert bad is not good
    if forge in (_j_forge_d_owner_missing, _j_forge_d_owner_rekeyed):
        assert validate_causal_history_state(bad.d_state) is None
    expected = _p_problem(bad, ns)
    assert expected is not None
    r = q_result(bad, ns)
    assert r.outcome is RootRegionCurrentnessOutcome.REFUSED
    assert r.p_validation_problem is expected
    assert r.p_selection is None
    assert r.usable_selected_source_digest is None
    assert r.diagnostics == ()
    assert_state_identity(r, bad)


@pytest.mark.parametrize("mode", MODES)
def test_d_q_bounds_malformed_and_stricter_legal(mode: AdmissionMode) -> None:
    """Q bounds gates: a raw override dictionary, a MALFORMED
    model_copy-mutated bound and a wider direct construction all
    refuse with the fixed malformed diagnostic BEFORE any serializer
    visit; a valid STRICTER copy is legal and the derivation runs
    under the stricter domain (the supplied bound is freshly
    validated into an equivalent effective value: value equality and
    the derived key, not unpromised input-bound identity)."""
    ns, state = q_bootstrap(mode, f"bounds-{mode.value}")
    # A raw override dictionary.
    r = q_result(state, ns, {"max_total_work_units": 1, "max_diagnostics": 1})  # type: ignore[arg-type]
    assert r.outcome is RootRegionCurrentnessOutcome.REFUSED
    assert [d.value for d in r.diagnostics] == ["malformed_binding"]
    assert r.p_selection is None
    assert_state_identity(r, state)
    # A MALFORMED model_copy-mutated bound (a non-scalar field).
    r = q_result(
        state,
        ns,
        RootRegionCurrentnessBounds().model_copy(update={"max_diagnostics": []}),
    )
    assert r.outcome is RootRegionCurrentnessOutcome.REFUSED
    assert [d.value for d in r.diagnostics] == ["malformed_binding"]
    assert r.p_selection is None
    assert_state_identity(r, state)
    # A wider direct construction (beyond the hard ceiling).
    r = q_result(
        state,
        ns,
        RootRegionCurrentnessBounds.model_construct(max_total_work_units=2**31),
    )
    assert r.outcome is RootRegionCurrentnessOutcome.REFUSED
    assert [d.value for d in r.diagnostics] == ["malformed_binding"]
    assert r.p_selection is None
    assert_state_identity(r, state)
    # A valid STRICTER copy is legal (the small fixture fits): the
    # derived effective bound is value-equal under the derived key.
    strict = RootRegionCurrentnessBounds(max_total_work_units=65536, max_diagnostics=1)
    r = q_result(state, ns, strict)
    assert r.outcome is RootRegionCurrentnessOutcome.READY
    assert r.bounds == strict
    assert r.bounds.max_total_work_units == 65536
    assert r.bounds.max_diagnostics == 1
    assert r.scope_key == q_scope_key(state, strict)
    assert_state_identity(r, state)


# --- E. Work boundaries (ONE Q outer + ACTUAL independent P domain) ------


def _e_audit_state(mode: AdmissionMode, lineage: str) -> tuple[Any, Any]:
    """A fresh full-operation sequence (both modes): bootstrap v1,
    an issued+observed MIXED v2 (a known supported witness), and an
    UNISSUED unanchored boundaryless v3 observation (row 4: it
    contributes nothing to uncertainty).  Q is READY selecting v2
    under the default domain; the exact P selection stays OK."""
    ns, s0 = q_bootstrap(mode, lineage, root_body="Measure root.")
    s1 = q_issue(s0, ns, "e1", "responses", MIX_CMD, (CAUSAL_ROOT_FACT,))
    s2 = q_observe(s1, ns, "responses", "e1", mixed_body(A_TEXT, MARK, "Cap root.\n"), MIX_CMD)
    s3 = q_observe(s2, ns, "responses", "e2", OPAQUE_BODY, BOUNDARYLESS_CMD)
    return ns, s3


def _e1_probe(mode: AdmissionMode, tag: str, n: int, cap: int) -> bool:
    ns, state = _e_audit_state(mode, f"{tag}-{n}")
    r = q_result(state, ns, RootRegionCurrentnessBounds(max_total_work_units=cap))
    return r.outcome is RootRegionCurrentnessOutcome.READY


@pytest.mark.parametrize("mode", MODES)
def test_e_full_operation_cap_first_over(mode: AdmissionMode) -> None:
    """The REACHABLE full-operation work boundary of the Q
    derivation: the measured minimum cap accepts the ENTIRE
    sequence (READY at the exact boundary), and the exact
    one-unit-below cap refuses the typed over-bound result
    preserving the EXACT state and the ACTUAL same-run P selection
    (the crossing lands in the charged assessment/result
    construction AFTER the P phase; no partial positive output, no
    usable label, no revision advance)."""
    cap = _min_accepted_cap(mode, "e1", _e1_probe)
    ns, state = _e_audit_state(mode, "e1-final")
    r = q_result(state, ns, RootRegionCurrentnessBounds(max_total_work_units=cap))
    assert r.outcome is RootRegionCurrentnessOutcome.READY
    assert r.usable_selected_source_digest == sha256_hex("Cap root.\n")
    assert r.p_selection is not None
    assert r.p_selection.outcome is RootSelectionOutcome.OK
    assert_state_identity(r, state)
    below = q_result(state, ns, RootRegionCurrentnessBounds(max_total_work_units=cap - 1))
    assert below.outcome is RootRegionCurrentnessOutcome.REFUSED
    assert [d.value for d in below.diagnostics] == ["work_units_over_bound"]
    assert below.p_selection is not None
    assert below.p_selection.outcome is RootSelectionOutcome.OK
    assert below.p_validation_problem is None
    assert below.usable_selected_source_digest is None
    assert_state_identity(below, state)


def _e_branch_state(
    mode: AdmissionMode,
    lineage: str,
    n: int,
    p_cap: int | None = None,
    track: dict[str, Any] | None = None,
) -> tuple[Any, Any, list[str]]:
    """The eligible-opaque-branch shape (the measured n40
    discriminator fixture, generalized): bootstrap a measured root,
    then N trusted complete OPAQUE root-bearing sibling observations
    (boundaryless, frontier = the anchor only, issued plus matched
    receipt -> anchored), then ONE known mixed descendant-of-all
    (frontier = anchor + all sibling occurrences) with a distinct
    root body.  Returns (ns, final state, sibling occurrence ids)
    when every public step is accepted.  ``p_cap`` (when given) is
    the ACTUAL inherited P ceiling binding the WHOLE production
    sequence (the P bounds bind into the lineage key, so the state
    is built under its own ceiling).  ``track`` (when given)
    records the maximum work_spent over the ACTUAL _HOuter ledgers
    created so far (the caller installs the counting __init__
    wrapper before the call)."""
    bounds = RootLineageBounds(max_total_work_units=p_cap) if p_cap is not None else None
    admission = make_bundle_admission_namespace(
        IDENTITY,
        model_identity="synthetic-currentness-model",
        config_fingerprint=FINGERPRINT,
        workspace=WORKSPACE,
        mode=mode,
    )
    ns = make_root_region_lineage_namespace(admission, lineage, bounds=bounds)

    def snap() -> None:
        if track is not None:
            track["max"] = max([track["max"]] + [i.work_spent for i in track["live"]])

    t0 = bootstrap_root_region_lineage((rooted("Measure root."),), ns)
    assert t0.outcome.value == "accepted", t0.diagnostics
    snap()
    state = t0.state
    sib_ids: list[str] = []
    for i in range(n):
        cid = f"s{i}"
        t_o = observe_root_region_lineage(
            state,
            ns,
            state.revision,
            (read_request("responses", cid, OPAQUE_BODY, BOUNDARYLESS_CMD),),
        )
        assert t_o.outcome.value == "accepted", (t_o.outcome, t_o.diagnostics)
        snap()
        state = t_o.state
        t_i = register_root_region_issuance(
            state,
            ns,
            cid,
            "responses",
            "exec_command",
            json.dumps({"cmd": BOUNDARYLESS_CMD}),
            (CAUSAL_ROOT_FACT,),
            state.revision,
        )
        assert t_i.outcome.value == "accepted", (t_i.outcome, t_i.diagnostics)
        snap()
        state = t_i.state
        t_r = register_root_region_receipt(
            state,
            ns,
            cid,
            "responses",
            "exec_command",
            json.dumps({"cmd": BOUNDARYLESS_CMD}),
            (CAUSAL_ROOT_FACT,),
            state.revision,
        )
        assert t_r.outcome.value == "accepted", (t_r.outcome, t_r.diagnostics)
        snap()
        state = t_r.state
        sib_ids.append(next(o.occurrence_id for o in state.d_state.occurrences if o.call_id == cid))
    d_frontier = (CAUSAL_ROOT_FACT,) + tuple(sib_ids)
    t_di = register_root_region_issuance(
        state,
        ns,
        "d1",
        "responses",
        "exec_command",
        json.dumps({"cmd": MIX_CMD}),
        d_frontier,
        state.revision,
    )
    assert t_di.outcome.value == "accepted", (t_di.outcome, t_di.diagnostics)
    snap()
    state = t_di.state
    t_do = observe_root_region_lineage(
        state,
        ns,
        state.revision,
        (read_request("responses", "d1", A_TEXT + MARK + "\n" + "Cap root.\n", MIX_CMD),),
    )
    assert t_do.outcome.value == "accepted", (t_do.outcome, t_do.diagnostics)
    snap()
    state = t_do.state
    sel = select_current_root_region(state, ns)
    snap()
    assert sel.outcome is RootSelectionOutcome.OK, sel.limitations
    return ns, state, sib_ids


@pytest.mark.parametrize("mode", MODES)
def test_e_independent_p_domain_discriminator(
    mode: AdmissionMode, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The ACTUAL independent P domain beneath the ONE Q outer, on
    a genuinely public-P-built fixture where the FULL Q work
    EXCEEDS the actual P ceiling -- the shape a shared
    min(P ceiling, Q total) budget cannot pass.

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
    < full-Q work cap <= Q default ceiling.  Q at the DEFAULT total
    is READY with ALL N original dominated witnesses retained by
    reference (a single shared min(P ceiling, Q total) budget would
    refuse here: the full Q work crosses it).  Q total set to the
    measured P ceiling REFUSES the typed over-bound result AFTER
    the actual P selection completed (p_selection retained, exact
    state) -- a 'P ceiling pre-reserved from the Q total'
    implementation would refuse before any P work (p_selection
    None).  P-first-over is NOT attained by this public production
    sequence (the producer maximum exceeds the P phase, so no
    producible ceiling falls below the P phase); it is not claimed
    universally unreachable -- the charging-adapter mechanism is
    exercised directly below."""
    n = 40
    track: dict[str, Any] = {"live": [], "max": 0}
    orig_init = _HOuter.__init__

    def counting_init(self: Any, *args: Any, **kwargs: Any) -> None:
        orig_init(self, *args, **kwargs)
        track["live"].append(self)

    monkeypatch.setattr(_HOuter, "__init__", counting_init)
    _e_branch_state(mode, f"e2gen-{mode.value}-{n}", n, track=track)
    producer_max = track["max"]
    assert producer_max > 0
    # Strict rebuild: fully public production under the measured ceiling.
    ns, state, sib_ids = _e_branch_state(mode, f"e2str-{mode.value}-{n}", n, p_cap=producer_max)
    assert ns.root_lineage_bounds.max_total_work_units == producer_max
    # The ACTUAL P phase of the derivation, counted on the P-domain
    # ledger (the Q phase charges the separate _QOuter).
    p_count = {"n": 0}
    orig_unit = _HOuter.unit

    def counting_unit(self: Any, *args: Any, **kwargs: Any) -> bool:
        allowed = orig_unit(self, *args, **kwargs)
        if allowed:
            p_count["n"] += 1
        return allowed

    monkeypatch.setattr(_HOuter, "unit", counting_unit)
    r_default = q_result(state, ns)
    p_phase = p_count["n"]
    assert p_phase <= producer_max

    def _qcap_probe(_m: AdmissionMode, _tag: str, _i: int, cap: int) -> bool:
        return (
            q_result(state, ns, RootRegionCurrentnessBounds(max_total_work_units=cap)).outcome
            is RootRegionCurrentnessOutcome.READY
        )

    q_cap = _min_accepted_cap(mode, f"e2cap-{mode.value}", _qcap_probe)
    # The discriminating shape, measured (not hardcoded).
    assert producer_max < q_cap
    assert q_cap <= RootRegionCurrentnessBounds().max_total_work_units
    # DEFAULT Q total: READY with ALL N original dominated
    # witnesses retained by reference, in canonical (class,
    # occurrence_id) order.
    assert r_default.outcome is RootRegionCurrentnessOutcome.READY
    assert r_default.usable_selected_source_digest == sha256_hex("Cap root.\n")
    assert r_default.p_selection is not None
    assert r_default.p_selection.outcome is RootSelectionOutcome.OK
    witnesses = r_default.uncertainty_witnesses
    assert len(witnesses) == n
    final_sibs = {
        o.occurrence_id: o for o in state.d_state.occurrences if o.occurrence_id in set(sib_ids)
    }
    complete_records = {
        (r.call_id, r.endpoint, r.tool_name, r.argument_fingerprint): r
        for r in state.d_state.results
        if r.complete is True
    }
    for w in witnesses:
        # Per-witness IDENTITY against the final retained state and
        # the original owning complete result record (not structural
        # set equality).
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
    assert all(isinstance(w, RootRegionUncertaintyWitness) for w in witnesses)
    assert_state_identity(r_default, state)
    # Full-Q boundary at the exact measured cap and one unit below:
    # p_phase < q_cap - 1 (the Q phase charges positive work), so
    # the crossing lands in the Q phase AFTER the P phase and the
    # actual P selection is retained.
    assert p_phase < q_cap - 1
    r_at = q_result(state, ns, RootRegionCurrentnessBounds(max_total_work_units=q_cap))
    assert r_at.outcome is RootRegionCurrentnessOutcome.READY
    assert len(r_at.uncertainty_witnesses) == n
    assert_state_identity(r_at, state)
    r_below = q_result(state, ns, RootRegionCurrentnessBounds(max_total_work_units=q_cap - 1))
    assert r_below.outcome is RootRegionCurrentnessOutcome.REFUSED
    assert [d.value for d in r_below.diagnostics] == ["work_units_over_bound"]
    assert r_below.p_selection is not None
    assert r_below.p_selection.outcome is RootSelectionOutcome.OK
    assert r_below.p_validation_problem is None
    assert r_below.usable_selected_source_digest is None
    assert_state_identity(r_below, state)
    # Q total = the measured P ceiling: the Q total is a TRUE TOTAL,
    # not 'P ceiling plus remainder' -- the refusal lands in the Q
    # phase after the actual P selection completed.
    r_at_pcap = q_result(state, ns, RootRegionCurrentnessBounds(max_total_work_units=producer_max))
    assert r_at_pcap.outcome is RootRegionCurrentnessOutcome.REFUSED
    assert [d.value for d in r_at_pcap.diagnostics] == ["work_units_over_bound"]
    assert r_at_pcap.p_selection is not None
    assert r_at_pcap.p_selection.outcome is RootSelectionOutcome.OK
    assert r_at_pcap.p_validation_problem is None
    assert r_at_pcap.usable_selected_source_digest is None
    assert_state_identity(r_at_pcap, state)


@pytest.mark.parametrize("mode", MODES)
def test_e_p_first_over_adapter_mechanism(mode: AdmissionMode) -> None:
    """The P-domain crossing mechanism itself -- the ACTUAL
    P-first-over shape (the inherited P ceiling crosses while the
    Q total is NOT charged for the crossing unit) -- exercised
    directly on the charging adapter.  The n=40 public production
    sequence does NOT attain this shape (its producer maximum
    exceeds its P phase, so no producible namespace ceiling falls
    below the P phase); it is not claimed universally unreachable,
    and this control exercises the law without a fake public
    positive."""
    q_outer = _QOuter(1048576)
    cap = 3
    adapter = _QPAdapter(q_outer, cap)
    for _ in range(cap):
        assert adapter.unit() is True
    # The P-domain crossing refuses with the P fixed over-bound
    # report WITHOUT charging the Q total for the crossing unit.
    assert adapter.unit() is False
    assert adapter.exhausted is True
    assert q_outer.work_spent == cap
    # The Q total is independent and intact afterwards.
    assert q_outer.unit() is True
    assert q_outer.work_spent == cap + 1


@pytest.mark.parametrize("mode", MODES)
def test_e_q_overflow_mid_p_phase_default_p(mode: AdmissionMode) -> None:
    """Q overflow mid-P-phase under the P DEFAULT domain: the small
    Q total crosses during the namespace phase before any P work
    completes (p_selection None, p_validation_problem None, exact
    state preserved)."""
    ns, state = _e_audit_state(mode, f"e3-{mode.value}")
    small = q_result(state, ns, RootRegionCurrentnessBounds(max_total_work_units=50))
    assert small.outcome is RootRegionCurrentnessOutcome.REFUSED
    assert [d.value for d in small.diagnostics] == ["work_units_over_bound"]
    assert small.p_selection is None
    assert small.p_validation_problem is None
    assert small.usable_selected_source_digest is None
    assert_state_identity(small, state)


@pytest.mark.parametrize("mode", MODES)
def test_e_full_q_cap_with_eligible_uncertainty(mode: AdmissionMode) -> None:
    """The REACHABLE full-Q work boundary with ACTUAL eligible
    dominated uncertainty: the n=2 sibling-opaque + descendant-of-
    all fixture (two eligible opaque anchor parents jointly
    dominated by the known mixed descendant; the canonical pairwise
    work charged on the Q total).  The measured minimum cap accepts
    the ENTIRE derivation (READY at the exact boundary with both
    original witnesses retained in canonical order); the exact
    one-unit-below cap refuses the typed over-bound result
    preserving the EXACT state and the ACTUAL same-run P selection
    (the crossing is in the Q phase after the P phase)."""
    n = 2
    ns4, state, sib_ids = _e_branch_state(mode, f"e4-{mode.value}-{n}", n)

    def _qcap_probe(_m: AdmissionMode, _tag: str, _i: int, cap: int) -> bool:
        return (
            q_result(state, ns4, RootRegionCurrentnessBounds(max_total_work_units=cap)).outcome
            is RootRegionCurrentnessOutcome.READY
        )

    cap = _min_accepted_cap(mode, f"e4cap-{mode.value}", _qcap_probe)
    r = q_result(state, ns4, RootRegionCurrentnessBounds(max_total_work_units=cap))
    assert r.outcome is RootRegionCurrentnessOutcome.READY
    assert r.usable_selected_source_digest == sha256_hex("Cap root.\n")
    assert r.p_selection is not None
    assert r.p_selection.outcome is RootSelectionOutcome.OK
    witnesses = r.uncertainty_witnesses
    assert len(witnesses) == n
    assert list(witnesses) == sorted(
        witnesses, key=lambda w: (w.uncertainty_class.value, w.occurrence_id)
    )
    final_sibs = {
        o.occurrence_id: o for o in state.d_state.occurrences if o.occurrence_id in set(sib_ids)
    }
    complete_records = {
        (r.call_id, r.endpoint, r.tool_name, r.argument_fingerprint): r
        for r in state.d_state.results
        if r.complete is True
    }
    for w in witnesses:
        # Per-witness IDENTITY against the final retained state and
        # the original owning complete result record (not structural
        # set equality).
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
    assert_state_identity(r, state)
    below = q_result(state, ns4, RootRegionCurrentnessBounds(max_total_work_units=cap - 1))
    assert below.outcome is RootRegionCurrentnessOutcome.REFUSED
    assert [d.value for d in below.diagnostics] == ["work_units_over_bound"]
    assert below.p_selection is not None
    assert below.p_selection.outcome is RootSelectionOutcome.OK
    assert below.p_validation_problem is None
    assert below.usable_selected_source_digest is None
    assert_state_identity(below, state)


def _e_witness_state(mode: AdmissionMode, lineage: str) -> tuple[Any, Any, Any, Any]:
    """The row-4 activation sequence (the C late-opaque shape on
    the opaque path): returns (ns, state, the ONE genuine witness,
    the genuine UNPROVEN result) with original ID/proof/owner
    identity."""
    ns, s0 = q_bootstrap(mode, lineage)
    t1 = observe_root_region_lineage(
        s0, ns, s0.revision, (read_request("responses", "w", OPAQUE_BODY, BOUNDARYLESS_CMD),)
    )
    assert t1.outcome.value == "accepted", t1.diagnostics
    s2 = q_issue(t1.state, ns, "w", "responses", BOUNDARYLESS_CMD, (CAUSAL_ROOT_FACT,))
    t3 = register_root_region_receipt(
        s2,
        ns,
        "w",
        "responses",
        "exec_command",
        json.dumps({"cmd": BOUNDARYLESS_CMD}),
        (CAUSAL_ROOT_FACT,),
        s2.revision,
    )
    assert t3.outcome.value == "accepted", t3.diagnostics
    s3 = t3.state
    r = q_result(s3, ns)
    assert r.outcome is RootRegionCurrentnessOutcome.ROOT_CURRENTNESS_UNPROVEN
    assert len(r.uncertainty_witnesses) == 1
    return ns, s3, r.uncertainty_witnesses[0], r


@pytest.mark.parametrize("mode", MODES)
def test_e_witness_precharge_sentinel(mode: AdmissionMode, monkeypatch: pytest.MonkeyPatch) -> None:
    """Target-reaching control on the ACTUAL witness type: the
    per-eligible-witness precharge (the fixed witness unit count,
    charged on the Q total BEFORE the witness object is
    constructed) is a genuine, separately measured crossing
    window.  Counting ACTUAL RootRegionUncertaintyWitness.__init__
    entries on the REAL class (the wrapper is installed/restored
    by monkeypatch; class identity and isinstance preserved): the
    smallest cap at which the witness is constructed at all (the
    precharge fully passes) constructs EXACTLY the one witness;
    one unit below it the typed over-bound refusal lands BEFORE
    any witness construction (zero entries) with the EXACT state
    and the ACTUAL P selection retained; the full accepted cap
    completes with the single original witness.  This measures the
    precharge boundary; it makes no zero-allocation claim about
    other result construction."""
    ns, state, w0, _r = _e_witness_state(mode, f"e6-{mode.value}")
    count = {"n": 0}
    orig_init = RootRegionUncertaintyWitness.__init__

    def counting_init(self: Any, *args: Any, **kwargs: Any) -> None:
        orig_init(self, *args, **kwargs)
        count["n"] += 1

    monkeypatch.setattr(RootRegionUncertaintyWitness, "__init__", counting_init)

    def _accepted(_m: AdmissionMode, _tag: str, _i: int, cap: int) -> bool:
        return q_result(
            state, ns, RootRegionCurrentnessBounds(max_total_work_units=cap)
        ).outcome in (
            RootRegionCurrentnessOutcome.READY,
            RootRegionCurrentnessOutcome.ROOT_CURRENTNESS_UNPROVEN,
        )

    def _constructed(_m: AdmissionMode, _tag: str, _i: int, cap: int) -> bool:
        count["n"] = 0
        _accepted(_m, _tag, _i, cap)
        return count["n"] >= 1

    w_full = _min_accepted_cap(mode, f"e6full-{mode.value}", _accepted)
    w_pre = _min_accepted_cap(mode, f"e6pre-{mode.value}", _constructed)
    assert w_pre < w_full
    # At the precharge-passing cap the construction IS reached
    # (exactly one entry); the later result-construction work still
    # crosses, so the result is the typed refusal (no invented
    # positive, no witness carried in the refused result).
    count["n"] = 0
    r_pre = q_result(state, ns, RootRegionCurrentnessBounds(max_total_work_units=w_pre))
    assert count["n"] == 1
    assert r_pre.outcome is RootRegionCurrentnessOutcome.REFUSED
    assert [d.value for d in r_pre.diagnostics] == ["work_units_over_bound"]
    assert r_pre.p_selection is not None
    assert r_pre.p_selection.outcome is RootSelectionOutcome.OK
    assert r_pre.uncertainty_witnesses == ()
    assert_state_identity(r_pre, state)
    # One unit below the precharge: the refusal lands BEFORE any
    # witness construction (zero entries).
    count["n"] = 0
    r_before = q_result(state, ns, RootRegionCurrentnessBounds(max_total_work_units=w_pre - 1))
    assert count["n"] == 0
    assert r_before.outcome is RootRegionCurrentnessOutcome.REFUSED
    assert [d.value for d in r_before.diagnostics] == ["work_units_over_bound"]
    assert r_before.p_selection is not None
    assert r_before.p_selection.outcome is RootSelectionOutcome.OK
    assert r_before.uncertainty_witnesses == ()
    assert_state_identity(r_before, state)
    # The full accepted cap: the single original witness, reaching
    # the target with a genuine positive.
    count["n"] = 0
    r_full = q_result(state, ns, RootRegionCurrentnessBounds(max_total_work_units=w_full))
    assert count["n"] == 1
    assert r_full.outcome is RootRegionCurrentnessOutcome.ROOT_CURRENTNESS_UNPROVEN
    assert len(r_full.uncertainty_witnesses) == 1
    assert isinstance(r_full.uncertainty_witnesses[0], RootRegionUncertaintyWitness)
    assert r_full.uncertainty_witnesses[0].occurrence is w0.occurrence
    assert r_full.uncertainty_witnesses[0].occurrence_id == w0.occurrence_id
    assert_state_identity(r_full, state)


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_e_inherited_batch_domain(mode: AdmissionMode, endpoint: str) -> None:
    """The ACTUAL inherited D per-batch request domain beneath the
    region operations: with max_requests=1, two SEPARATE
    one-request observations are each legal and BOTH retained (the
    per-batch domain, not a cumulative cap), while ONE two-request
    batch refuses the exact mapped batch bound BEFORE the
    deliberately malformed second element (missing call id) is
    inspected -- the count gate precedes element validation --
    with the EXACT prior state, no D transition and no revision
    advance."""
    admission = make_bundle_admission_namespace(
        IDENTITY,
        model_identity="synthetic-currentness-model",
        config_fingerprint=FINGERPRINT,
        workspace=WORKSPACE,
        mode=mode,
        graph_bounds=GraphBounds(max_requests=1),
    )
    ns = make_root_region_lineage_namespace(admission, f"e7-{mode.value}-{endpoint}")
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
    # The ACTUAL Q derivation over the retained state at the bound:
    # READY with the anchor root usable, both completed observations
    # retained, no root uncertainty, exact state.
    r7 = q_result(s2, ns)
    assert r7.outcome is RootRegionCurrentnessOutcome.READY
    assert r7.usable_selected_source_digest == sha256_hex("Batch root.")
    assert r7.p_selection is not None
    assert r7.p_selection.outcome is RootSelectionOutcome.OK
    assert not r7.uncertainty_witnesses
    assert_state_identity(r7, s2)
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
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_e_inherited_retention_count_first_over(mode: AdmissionMode, endpoint: str) -> None:
    """The ACTUAL inherited D retention-count domain (max_
    occurrences) beneath the region operations, at a genuine
    STRICTER cap: the genuine supported positive runs first (three
    accepted one-request observations retained at the cap), then
    the first-over observation refuses the exact mapped retention
    bound with the EXACT prior state and no revision advance,
    retaining the ACTUAL refused D transition; at the same boundary
    a batch carrying a bad element (missing call id) is refused for
    the BOUND before the bad element is inspected -- the fixed
    bound precedence applies to the retention gate as well as to
    the batch COUNT gate exercised above."""

    k = 3
    admission = make_bundle_admission_namespace(
        IDENTITY,
        model_identity="synthetic-currentness-model",
        config_fingerprint=FINGERPRINT,
        workspace=WORKSPACE,
        mode=mode,
    )
    ns = make_root_region_lineage_namespace(
        admission,
        f"e8-{mode.value}-{endpoint}",
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
    # At the same boundary, a batch carrying a bad element (missing
    # call id) is refused for the BOUND before the bad element is
    # inspected.
    t_bad = observe_root_region_lineage(
        at_cap,
        ns,
        at_cap.revision,
        (
            read_request(endpoint, "bad1", A_TEXT, "cat A.md"),
            read_request(endpoint, "", B_TEXT, "cat B.md"),
        ),
    )
    assert t_bad.outcome is RootLineageOutcome.REFUSED_OVER_BOUND
    assert t_bad.state is at_cap
    assert t_bad.diagnostics == (RootLineageLimitation.OCCURRENCES_OVER_BOUND,)
    assert t_bad.d_transition is not None
    assert t_bad.d_transition.outcome.value == "refused_over_bound"
    assert t_bad.revision_after == at_cap.revision


@pytest.mark.parametrize("mode", MODES)
def test_e_constructor_collection_ceilings(mode: AdmissionMode) -> None:
    """Constructor-level collection ceilings (CLOSED intrinsic law
    before any dump/serialization visit).  The public first-over
    of the two ceilings is UNREACHABLE through the charged kernel
    for two separate reasons, qualified honestly (not 'dedup
    alone'): (a) more than 4096 uncertainty witnesses cannot be
    retained because the ACTUAL inherited D collection and work
    domains (max_occurrences and the per-operation work bounds)
    bound the retained occurrence population below the Q witness
    ceiling; and (b) more than 64 OWN Q diagnostics cannot be
    emitted because a public Q derivation emits at most ONE own
    fixed diagnostic per outcome (carried P selection limitations
    are a separate P evidence channel, not Q diagnostics).  The
    constructor fences are the closed law.  A genuine positive
    constructor roundtrip on the ACTUAL result fields runs
    first."""

    ns, state, w0, r = _e_witness_state(mode, f"e5-{mode.value}")
    base = {
        "outcome": r.outcome,
        "state": state,
        "p_selection": r.p_selection,
        "p_validation_problem": r.p_validation_problem,
        "usable_selected_source_digest": r.usable_selected_source_digest,
        "uncertainty_witnesses": r.uncertainty_witnesses,
        "diagnostics": r.diagnostics,
        "bounds": r.bounds,
        "lineage_key": r.lineage_key,
        "scope_key": r.scope_key,
        "revision": r.revision,
    }
    ok = RootRegionCurrentnessResult.model_validate(base)
    assert ok.uncertainty_witnesses[0] is w0
    assert ok.state is state
    # 4097 witness copies: the closed ceiling is 4096 (the
    # at-cap 4096 identical copies are unreachable by the dedup
    # law; the ceiling is constructor-level law).
    with pytest.raises(ValidationError, match="inherited ceiling"):
        RootRegionCurrentnessResult.model_validate(dict(base, uncertainty_witnesses=[w0] * 4097))
    # 65 diagnostics: the ceiling is prefetched BEFORE any nested
    # enum validation (the model-level actual-bounds cap gate fires
    # first under the default domain).
    with pytest.raises(ValidationError, match="actual Q bounds"):
        RootRegionCurrentnessResult.model_validate(
            dict(base, diagnostics=(RootRegionCurrentnessDiagnostic.FOREIGN_SCOPE,) * 65)
        )
    # A VALID STRICTER max_diagnostics=1 with two diagnostics
    # (the second an invalid enum sentinel): the actual cap gate
    # fires BEFORE any diagnostics element is visited.
    strict = RootRegionCurrentnessBounds(max_total_work_units=65536, max_diagnostics=1)
    sentinel = "not-a-real-q-diagnostic"
    with pytest.raises(ValidationError) as excinfo:
        RootRegionCurrentnessResult.model_validate(
            dict(
                base,
                bounds=strict,
                diagnostics=(RootRegionCurrentnessDiagnostic.FOREIGN_SCOPE, sentinel),
            )
        )
    errors = excinfo.value.errors()
    assert errors
    assert not any(e["loc"] == ("diagnostics", 1) for e in errors)


# --- F. Invariants, privacy and purity -----------------------------------


@pytest.mark.parametrize("mode", MODES)
def test_f_idempotent_query_and_scope_key(mode: AdmissionMode) -> None:
    """The query is pure and idempotent: repeated derivation on the
    SAME state yields fresh results with identical canonical
    serialization (pure data proof, NOT a wire-byte claim) with the
    EXACT state retained; the stable scope key binds the actual
    lineage key + Q contract/policy + bounds -- NOT the carried
    revision (a GENUINE accepted transition that advances the
    carried revision by one keeps the same scope key, and a
    revision-tampered state changes the carried revision but not
    the scope key); a rejected input scope characterizes the
    derivation in the default domain (same scope key) and distinct
    bounds yield a distinct scope key."""
    ns, state = _e_audit_state(mode, f"f1-{mode.value}")
    ra = q_result(state, ns)
    rb = q_result(state, ns)
    assert ra is not rb
    assert ra.outcome is RootRegionCurrentnessOutcome.READY
    assert ra.model_dump_json() == rb.model_dump_json()
    assert ra.state is state and rb.state is state
    assert ra.scope_key == rb.scope_key == q_scope_key(state, RootRegionCurrentnessBounds())
    # A rejected input scope characterizes the derivation in the
    # DEFAULT domain: the same state lineage key and default bounds.
    identity2 = RequestIdentity(
        principal="f1-other-principal",
        session="s",
        repository="r",
        route="x",
    )
    admission2 = make_bundle_admission_namespace(
        identity2,
        model_identity="synthetic-currentness-model",
        config_fingerprint=FINGERPRINT,
        workspace=WORKSPACE,
        mode=mode,
    )
    ns_foreign = make_root_region_lineage_namespace(admission2, f"f1-{mode.value}")
    foreign = q_result(state, ns_foreign)
    assert foreign.outcome is RootRegionCurrentnessOutcome.REFUSED
    assert foreign.scope_key == ra.scope_key
    # Distinct bounds yield a distinct scope key.
    strict = RootRegionCurrentnessBounds(max_total_work_units=65536, max_diagnostics=1)
    rs = q_result(state, ns, strict)
    assert rs.outcome is RootRegionCurrentnessOutcome.READY
    assert rs.scope_key != ra.scope_key
    assert rs.scope_key == q_scope_key(state, strict)
    # A GENUINE accepted transition (an extra legitimate
    # observation advances the carried revision by one) keeps the
    # SAME stable scope key: the key binds the actual lineage key +
    # Q contract/policy + bounds, NOT the carried revision.
    s_next = q_observe(state, ns, "responses", "f1-next", A_TEXT + B_TEXT, NONROOT_CMD)
    assert s_next.revision == state.revision + 1
    rn = q_result(s_next, ns)
    assert rn.outcome is RootRegionCurrentnessOutcome.READY
    assert rn.usable_selected_source_digest == ra.usable_selected_source_digest
    assert rn.revision == s_next.revision
    assert rn.scope_key == ra.scope_key
    # A changed CARRIED revision (the 1:1 D law broken) still
    # characterizes the same stable scope key.
    bad_rev = state.model_copy(update={"revision": state.revision + 1})
    rb2 = q_result(bad_rev, ns)
    assert rb2.outcome is RootRegionCurrentnessOutcome.REFUSED
    assert rb2.revision == bad_rev.revision
    assert rb2.scope_key == ra.scope_key


@pytest.mark.parametrize("mode", MODES)
def test_f_privacy_repr_canaries(mode: AdmissionMode) -> None:
    """Operational reprs stay fixed non-echoing: a distinct ROOT
    body canary, an opaque body canary, a DISTINCT known NONROOT
    source canary, a distinct call ID and the identity canaries
    are all absent from every Q str/repr surface (result, witness,
    diagnostics, carried P selection); the witness's private
    references render as the fixed placeholder; the fixed
    malformed-input operational exception carries no canary in
    str/repr."""
    root_canary = "FROOT-CANARY-018Q"
    body_canary = "FOBOD-CANARY-018Q"
    nonroot_canary = "FNONROOT-CANARY-018Q"
    call_id = "f-call-018q"
    identity = RequestIdentity(
        principal="f-priv-principal",
        session="f-priv-session",
        repository="f-priv-repository",
        route="f-priv-route",
    )
    admission = make_bundle_admission_namespace(
        identity,
        model_identity="f-priv-model",
        config_fingerprint=FINGERPRINT,
        workspace=WORKSPACE,
        mode=mode,
    )
    ns = make_root_region_lineage_namespace(admission, f"f-priv-{mode.value}")
    t0 = bootstrap_root_region_lineage((rooted(f"Synthetic root. {root_canary}"),), ns)
    assert t0.outcome.value == "accepted", t0.diagnostics
    body = f"Unknown root constituent. {body_canary}\n" + A_TEXT
    t1 = observe_root_region_lineage(
        t0.state,
        ns,
        t0.state.revision,
        (read_request("responses", call_id, body, BOUNDARYLESS_CMD),),
    )
    assert t1.outcome.value == "accepted", t1.diagnostics
    s2 = q_issue(t1.state, ns, call_id, "responses", BOUNDARYLESS_CMD, (CAUSAL_ROOT_FACT,))
    t3 = register_root_region_receipt(
        s2,
        ns,
        call_id,
        "responses",
        "exec_command",
        json.dumps({"cmd": BOUNDARYLESS_CMD}),
        (CAUSAL_ROOT_FACT,),
        s2.revision,
    )
    assert t3.outcome.value == "accepted", t3.diagnostics
    state = t3.state
    # A DISTINCT known NONROOT source: an accepted nonroot read
    # whose retained body carries the canary must not leak into any
    # Q surface.
    t_nr = observe_root_region_lineage(
        state,
        ns,
        state.revision,
        (
            read_request(
                "responses",
                "f-nr",
                A_TEXT + nonroot_canary + "\n" + B_TEXT,
                NONROOT_CMD,
            ),
        ),
    )
    assert t_nr.outcome.value == "accepted", t_nr.diagnostics
    state = t_nr.state
    r = q_result(state, ns)
    assert r.outcome is RootRegionCurrentnessOutcome.ROOT_CURRENTNESS_UNPROVEN
    assert len(r.uncertainty_witnesses) == 1
    surfaces = [repr(r), str(r)]
    for w in r.uncertainty_witnesses:
        surfaces += [repr(w), str(w)]
    for d in r.diagnostics:
        surfaces += [repr(d), str(d)]
    assert r.p_selection is not None
    surfaces += [repr(r.p_selection), str(r.p_selection)]
    canaries = (
        root_canary,
        body_canary,
        nonroot_canary,
        call_id,
        identity.principal,
        identity.session,
        identity.repository,
        identity.route,
        "f-priv-model",
    )
    for surface in surfaces:
        for canary in canaries:
            assert canary not in surface
    assert PRIVATE_ID_PLACEHOLDER in repr(r.uncertainty_witnesses[0])
    # The fixed malformed-input operational exception carries no
    # canary in str/repr -- including when the malformed input is a
    # REAL canary-bearing state with an actual O1 field malformed
    # (copied revision=True: the shape fence rejects bool-as-int
    # before any work), not only a canary-free object.
    with pytest.raises(ValueError, match="actual bounded state record") as excinfo:
        q_result(object(), ns)
    for surface in (str(excinfo.value), repr(excinfo.value)):
        for canary in canaries:
            assert canary not in surface
    bad_state = state.model_copy(update={"revision": True})
    with pytest.raises(ValueError, match="actual bounded state record") as excinfo2:
        q_result(bad_state, ns)
    for surface in (str(excinfo2.value), repr(excinfo2.value)):
        for canary in canaries:
            assert canary not in surface


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_f_no_host_io_on_public_paths(
    mode: AdmissionMode, endpoint: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    """No host IO anywhere on the Q public surface.

    Fixture and import setup happen BEFORE the traps open; the traps
    (the closed 24-facility surface, the accepted P list) then cover
    the whole operation on the SAME legitimate state: factory,
    bootstrap, issuance, observation, receipt, validation, selection
    and the Q derivation over READY / UNPROVEN / ROOT_AUTHORITY_
    CONFLICT (actual P conflict) / REFUSED (foreign scope, over-
    bound, version, malformed bounds and actual P validation
    problem) and the malformed-state error outcomes.  The ACTUAL
    prebuilt request object is passed to the public observation.
    Every Q str/repr surface must be free of the canaries and the
    original request payloads must be unchanged afterwards."""
    marker = "PURITY-MARKER-018Q"
    root_body = "PRIVATE-ROOT-CONTENT-018Q. Read `A.md`."
    new_root = "PRIVATE-NEW-CONTENT-018Q"
    new_body = f"Ordinary A.\n{marker}\n{new_root}."
    opaque_body = "Unknown root constituent. PRIVATE-OPAQUE-018Q\n" + A_TEXT
    call_id = "purity-call-018q"
    call_id2 = "purity-call2-018q"
    identity = RequestIdentity(
        principal="purity-principal-018q",
        session="purity-session-018q",
        repository="purity-repository-018q",
        route="purity-route-018q",
    )
    canaries = (
        identity.principal,
        identity.session,
        identity.repository,
        identity.route,
        "purity-model-018q",
        "purity-lineage-018q",
        call_id,
        call_id2,
        marker,
        root_body,
        new_root,
        "PRIVATE-OPAQUE-018Q",
        V2,
        V3,
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

    admission = make_bundle_admission_namespace(
        identity,
        model_identity="purity-model-018q",
        config_fingerprint="c" * 64,
        workspace="/work",
        mode=mode,
    )
    ns = make_root_region_lineage_namespace(admission, "purity-lineage-018q")
    t0 = bootstrap_root_region_lineage((root,), ns)
    assert t0.outcome.value == "accepted", t0.diagnostics
    s1 = q_issue(t0.state, ns, call_id, endpoint, cmd, (CAUSAL_ROOT_FACT,))
    # The ACTUAL prebuilt request object is passed to the public
    # observation (so the unchanged-payload assertion below covers
    # the object the API really consumed).
    t2 = observe_root_region_lineage(s1, ns, s1.revision, (request,))
    assert t2.outcome.value == "accepted", t2.diagnostics
    s2 = t2.state
    assert validate_root_region_lineage_state(s2, ns.root_lineage_bounds) is None
    assert select_current_root_region(s2, ns).outcome is RootSelectionOutcome.OK
    r_ready = q_result(s2, ns)
    assert r_ready.outcome is RootRegionCurrentnessOutcome.READY
    # Non-ready: the late opaque row-4 activation on the SAME state
    # tree (issue then receipt; the genuine anchor law).
    s3 = observe_root_region_lineage(s2, ns, s2.revision, (opaque_request,))
    assert s3.outcome.value == "accepted", s3.diagnostics
    s4 = q_issue(s3.state, ns, call_id2, endpoint, BOUNDARYLESS_CMD, (CAUSAL_ROOT_FACT,))
    t4 = register_root_region_receipt(
        s4,
        ns,
        call_id2,
        endpoint,
        "exec_command",
        json.dumps({"cmd": BOUNDARYLESS_CMD}),
        (CAUSAL_ROOT_FACT,),
        s4.revision,
    )
    assert t4.outcome.value == "accepted", t4.diagnostics
    r_unproven = q_result(t4.state, ns)
    assert r_unproven.outcome is RootRegionCurrentnessOutcome.ROOT_CURRENTNESS_UNPROVEN
    assert len(r_unproven.uncertainty_witnesses) == 1
    # Refusals: foreign scope, over-bound, malformed-state error.
    ns_foreign = make_root_region_lineage_namespace(admission, "purity-lineage-other")
    r_foreign = q_result(s2, ns_foreign)
    assert r_foreign.outcome is RootRegionCurrentnessOutcome.REFUSED
    r_over = q_result(s2, ns, RootRegionCurrentnessBounds(max_total_work_units=50))
    assert r_over.outcome is RootRegionCurrentnessOutcome.REFUSED
    with pytest.raises(ValueError, match="actual bounded state record"):
        q_result(object(), ns)
    # Actual public authority CONFLICT (two incomparable known
    # region maxima, the accepted P conflict fixture): the ACTUAL P
    # conflict maps to the Q ROOT_AUTHORITY_CONFLICT outcome with
    # the actual P selection retained and no usable source.
    c_ns, c_state, _cf1, _cf2 = _two_sibling_regions(
        mode, f"purity-conflict-{mode.value}-{endpoint}", endpoint
    )
    assert (
        select_current_root_region(c_state, c_ns).outcome
        is RootSelectionOutcome.ROOT_CONTENT_CONFLICT
    )
    r_conflict = q_result(c_state, c_ns)
    assert r_conflict.outcome is RootRegionCurrentnessOutcome.ROOT_AUTHORITY_CONFLICT
    assert r_conflict.p_selection is not None
    assert r_conflict.p_selection.outcome is RootSelectionOutcome.ROOT_CONTENT_CONFLICT
    assert r_conflict.p_selection.selected_source_digest is None
    assert r_conflict.usable_selected_source_digest is None
    # Actual version refusal (the coherent v2 rekey, c3 pattern)
    # and bad-bounds (raw override dict) and actual P validation
    # refusal (forged region flag) all run under the traps.
    v2 = "cache-root-region-lineage/v2"
    k2 = _lineage_key(
        c_ns.history_key, v2, ROOT_REGION_LINEAGE_POLICY_VERSION, c_ns.root_lineage_bounds
    )
    c_ns_v2 = c_ns.model_copy(update={"contract_version": v2, "lineage_key": k2})
    c_state_v2 = c_state.model_copy(update={"lineage_key": k2})
    r_version = q_result(c_state_v2, c_ns_v2)
    assert r_version.outcome is RootRegionCurrentnessOutcome.REFUSED
    assert [d.value for d in r_version.diagnostics] == ["version_unsupported"]
    r_badbounds = q_result(
        c_state,
        c_ns,
        {"max_total_work_units": 1, "max_diagnostics": 1},  # type: ignore[arg-type]
    )
    assert r_badbounds.outcome is RootRegionCurrentnessOutcome.REFUSED
    assert [d.value for d in r_badbounds.diagnostics] == ["malformed_binding"]
    read_fact = next(f for f in c_state.root_facts if f.provenance.kind == "read_region")
    forged = read_fact.model_copy(update={"issued": False})
    c_bad = c_state.model_copy(
        update={"root_facts": tuple(forged if x is read_fact else x for x in c_state.root_facts)}
    )
    expected_c = _p_problem(c_bad, c_ns)
    assert expected_c is not None
    r_pval = q_result(c_bad, c_ns)
    assert r_pval.outcome is RootRegionCurrentnessOutcome.REFUSED
    assert r_pval.p_validation_problem is expected_c
    assert r_pval.p_selection is None
    # Privacy on the Q surfaces.
    surfaces = [repr(r_ready), repr(r_unproven), repr(r_foreign), repr(r_over)]
    for w in r_unproven.uncertainty_witnesses:
        surfaces.append(repr(w))
    surfaces += [
        repr(r_conflict),
        repr(r_version),
        repr(r_badbounds),
        repr(r_pval),
        repr(r_conflict.p_selection),
    ]
    for surface in surfaces:
        for canary in canaries:
            assert canary not in surface
    # The original request payloads are unchanged.
    assert [
        json.dumps(q.payload, sort_keys=True) for q in (root, request, opaque_request)
    ] == originals
    assert calls == []

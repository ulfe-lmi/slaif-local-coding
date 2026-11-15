"""Durable original-API acceptance: versioned root-region authority producer (018-p).

The A-L actual-path matrix of the activated 018-p order, over BOTH
read endpoints and BOTH admission modes, exercised on the SAME
legitimate state earned through the NEW public region APIs
(bootstrap_root_region_lineage, register_root_region_issuance,
observe_root_region_lineage, register_root_region_receipt,
select_current_root_region, validate_root_region_lineage_state)
with original GraphRequests and original proofs.  A genuinely
issued, complete, uniquely attributable NEW root region in an
ordinary mixed read acquires source evidence AND authority with NO
independent singleton; an unknown mixed root needs no independent
singleton in the NEW contract; repeated roots, opaque root groups,
partial/truncated/nonzero/unpaired/unsupported reads gain NO
exception; the old H/O public law is unchanged; the existing old I
honestly refuses a region-version state.  No strategic-runtime
dependency: known-synthetic original API fixtures only; every
oracle asserts the exact typed outcome, the exact prior-state
identity on refusal, the original proof/anchor/occurrence
identities and the fixed closed diagnostics.  Sections: A
bootstrap/mixed acquisition; B frozen partial order, revert,
historical retention; C issuance/authority/receipt, conflict and
envelope-alone precedence; D no-exception read shapes; E resulting
state support, original identities and the old-I honest refusal;
F the ONE new-operation outer and the BEFORE-materialization
retention/work boundaries with real constructor counters (fact
count across BOTH read provenance kinds, logical root-member bytes
with a mixed aggregate larger than the cap, and the measured
work preconstruction boundary); G the direct validator forge
matrix; H the selection-constructor invariants; I the
scope/version/CAS gates including coherent unsupported-version
namespaces/states on ALL four operations; J the public-operation
forge matrix including whole-proof/root-member joins, original
proof identity and the D-level owning-result omission/producer
association (the old D validator stays None); K the fixed
non-echoing privacy law strengthened with ROOT-source and ID-field
canaries; L the closed host-IO purity surface over the ENTIRE public
region path (factory, bootstrap, issuance, observation, validate,
selection, receipt, replay and the fixed refusals) with operational
representation privacy and unchanged original payloads.
"""

from __future__ import annotations

import asyncio
import builtins
import io
import json
import os
import socket
import subprocess
from collections.abc import Callable
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
    CausalHistoryOutcome,
    HistoryBounds,
    validate_causal_history_state,
)
from slaif_local_coding.constitution.bundles.graph_observation import GraphRequest
from slaif_local_coding.constitution.bundles.observation_models import Limitation
from slaif_local_coding.constitution.bundles.root_lineage_models import (
    EnvelopeRootProvenance,
    ReadRootProvenance,
    RootLineageBounds,
    RootLineageLimitation,
    RootLineageOutcome,
    RootSelectionOutcome,
    _lineage_key,
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
    ROOT_REGION_LINEAGE_CONTRACT_VERSION,
    ROOT_REGION_LINEAGE_POLICY_VERSION,
    RootRegionLineageFact,
    RootRegionLineageTransition,
    RootRegionReadProvenance,
    RootRegionSelectionResult,
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
    exec_call,
    out_item,
    read_request,
    root_request,
    sha256_hex,
)
from tests.test_current_root_composition import derive
from tests.test_root_lineage import (
    SIBLING_X,
    _min_accepted_cap,
    changed_root_envelope,
    occurrences,
    rooted,
)

# --- Module constants (known-synthetic original API fixtures) -----------

V2 = "Read `A.md` for the region refresh."
V3 = "Read `A.md` after the region refresh."
V4 = "Read `A.md` for the descent."
A_TEXT = "Synthetic nonroot A.\n"
B_TEXT = "Synthetic nonroot B.\n"
MARK = "ROOTSEP"
MARK2 = "OTHERSEP"
MIX_CMD = f"cat A.md && echo '{MARK}' && cat AGENTS.md"
FIRST_CMD = f"cat AGENTS.md && echo '{MARK}' && cat A.md"
MIDDLE_CMD = f"cat A.md && echo '{MARK}' && cat AGENTS.md && echo '{MARK2}' && cat B.md"
LAST_CMD = f"cat A.md && echo '{MARK}' && cat B.md && echo '{MARK2}' && cat AGENTS.md"
REPEAT_CMD = f"cat AGENTS.md && echo '{MARK}' && cat AGENTS.md"
REPEAT_OPAQUE_CMD = f"cat AGENTS.md && echo '{MARK}' && cat AGENTS.md B.md"
BOUNDARYLESS_CMD = "cat A.md && cat AGENTS.md"
CANARY = "canary-region-body-018p-4d7e"
ROOT_CANARY = "canary-region-root-018p-9c21"
ID_CANARY = "canary-region-id-018p-5e77"


def _mixed_body(*parts: str) -> str:
    """The mixed body layout for the marker-separated command:
    ``file body + MARK + "\n" + file body + ...`` (a trailing file
    body without a suffix marker is a proven final segment)."""
    out = parts[0]
    for marker, body in zip(parts[1::2], parts[2::2], strict=True):
        out += f"{marker}\n{body}"
    return out


def r_ns(
    mode: AdmissionMode,
    lineage: str,
    bounds: RootLineageBounds | None = None,
    **kwargs: Any,
) -> Any:
    """A root-region scope over the ACTUAL accepted 018-d scope."""
    history_bounds = kwargs.pop("history_bounds", None)
    identity = kwargs.pop("identity", IDENTITY)
    model_identity = kwargs.pop("model_identity", "synthetic-history-model")
    admission = make_bundle_admission_namespace(
        identity,
        model_identity=model_identity,
        config_fingerprint=FINGERPRINT,
        workspace=kwargs.pop("workspace", WORKSPACE),
        mode=mode,
        **kwargs,
    )
    return make_root_region_lineage_namespace(
        admission, lineage, bounds=bounds, history_bounds=history_bounds
    )


def r_bootstrap(mode: AdmissionMode, lineage: str, **kwargs: Any) -> tuple[Any, Any]:
    root_body = kwargs.pop("root_body", None)
    ns = r_ns(mode, lineage, **kwargs)
    item = rooted(root_body) if root_body is not None else root_request()
    t = bootstrap_root_region_lineage((item,), ns)
    assert t.outcome is RootLineageOutcome.ACCEPTED
    return ns, t.state


def r_issue(
    state: Any, ns: Any, cid: str, endpoint: str, frontier: tuple[str, ...], cmd: str
) -> Any:
    return register_root_region_issuance(
        state,
        ns,
        cid,
        endpoint,
        "exec_command",
        json.dumps({"cmd": cmd}),
        tuple(frontier),
        state.revision,
    )


def r_receipt(
    state: Any, ns: Any, cid: str, endpoint: str, frontier: tuple[str, ...], cmd: str
) -> Any:
    return register_root_region_receipt(
        state,
        ns,
        cid,
        endpoint,
        "exec_command",
        json.dumps({"cmd": cmd}),
        tuple(frontier),
        state.revision,
    )


def r_observe(state: Any, ns: Any, requests: tuple[Any, ...]) -> Any:
    return observe_root_region_lineage(state, ns, state.revision, requests)


def region_fact(state: Any, call_id: str) -> Any:
    return next(
        f
        for f in state.root_facts
        if f.provenance.kind == "read_region" and f.provenance.call_id == call_id
    )


def read_region_facts(state: Any) -> list[Any]:
    return [f for f in state.root_facts if f.provenance.kind == "read_region"]


def assert_refused(t: Any, prior: Any, outcome: RootLineageOutcome, diags: tuple[Any, ...]) -> None:
    assert t.outcome is outcome, (t.outcome, t.diagnostics)
    assert t.state is prior
    assert t.diagnostics == diags
    assert t.new_root_facts == ()
    assert t.revision_after == prior.revision


def _assert_region_bindings(
    state: Any,
    call_id: str,
    root_body: str,
    expected_segment_index: int | None = None,
    expected_member_position: int | None = None,
) -> None:
    """The exact original segment/member/carrier coordinates and
    proof identity of one retained region fact."""
    f = region_fact(state, call_id)
    assert f.source_digest == sha256_hex(root_body)
    assert f.source_byte_length == len(root_body.encode("utf-8"))
    p = f.provenance
    assert p.kind == "read_region"
    assert p.call_id == call_id
    occ = next(o for o in state.d_state.occurrences if o.call_id == call_id)
    proof = occ.proof
    assert p.occurrence_id == occ.occurrence_id
    assert p.whole_proof_digest == proof.source_digest
    assert p.whole_proof_byte_length == proof.source_byte_length
    assert p.whole_proof_byte_length != f.source_byte_length  # aggregate != root body
    assert 0 <= p.root_segment_index < len(proof.segments)
    seg = proof.segments[p.root_segment_index]
    assert seg.member_positions == (p.root_member_position,)
    assert seg.member_digest == p.root_member_digest
    assert seg.byte_length == p.root_member_byte_length
    member = proof.requested_members[p.root_member_position]
    assert member.normalized == "AGENTS.md"
    assert proof.source_digest != p.root_member_digest  # distinct bindings
    assert proof.root_digest == sha256_hex(ROOT_TEXT)  # bootstrap root binding
    if expected_segment_index is not None:
        assert p.root_segment_index == expected_segment_index
    if expected_member_position is not None:
        assert p.root_member_position == expected_member_position


# --- A. Bootstrap + issued descendant mixed-only read, NO singleton -----


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_a_bootstrap_mixed_only_region_v2(mode: AdmissionMode, endpoint: str) -> None:
    """A (018-p acceptance 1): bootstrap v1 -> genuinely issued
    DESCENDANT mixed-only read with a new complete root v2 plus
    nonroot source, NO independent singleton: accepted source,
    actual selected root v2, root byte length distinct from the
    aggregate, exact original segment/member/carrier coordinates and
    original proof identity."""
    assert ROOT_REGION_LINEAGE_CONTRACT_VERSION == "cache-root-region-lineage/v1"
    assert ROOT_REGION_LINEAGE_POLICY_VERSION == "root-region-lineage-policy/v1"
    ns, s0 = r_bootstrap(mode, "p-a")
    assert s0.revision == 1
    assert len(s0.root_facts) == 1
    env = s0.root_facts[0]
    assert env.provenance.kind == "envelope"
    assert env.issued is False and env.authority is True
    assert validate_root_region_lineage_state(s0, ns.root_lineage_bounds) is None
    sel0 = select_current_root_region(s0, ns)
    assert sel0.outcome is RootSelectionOutcome.OK
    assert sel0.selected_source_digest == sha256_hex(ROOT_TEXT)

    t1 = r_issue(s0, ns, "m1", endpoint, (CAUSAL_ROOT_FACT,), MIX_CMD)
    assert t1.outcome is RootLineageOutcome.ACCEPTED, t1.diagnostics
    t2 = r_observe(
        t1.state, ns, (read_request(endpoint, "m1", _mixed_body(A_TEXT, MARK, V2), MIX_CMD),)
    )
    assert t2.outcome is RootLineageOutcome.ACCEPTED, (t2.outcome, t2.diagnostics)
    s2 = t2.state
    assert s2 is not s0
    assert len(read_region_facts(s2)) == 1
    _assert_region_bindings(s2, "m1", V2, expected_segment_index=1, expected_member_position=1)
    f2 = region_fact(s2, "m1")
    # Issued (retained issuance) AND anchored (complete read + frozen
    # frontier) AND the frozen ancestry reaches the bootstrap: the
    # region EARNS authority without any independent singleton.
    assert f2.issued is True and f2.authority is True
    assert len(t2.new_root_facts) == 1
    assert t2.new_root_facts[0] is f2
    sel2 = select_current_root_region(s2, ns)
    assert sel2.outcome is RootSelectionOutcome.OK
    assert sel2.selected_source_digest == sha256_hex(V2)
    assert sel2.limitations == ()
    assert validate_root_region_lineage_state(s2, ns.root_lineage_bounds) is None
    # Receipt idempotence: the result already paired in the same
    # batch anchors under exactly this frozen frontier, so the
    # matching late receipt is a pure REPLAYED no-op.
    t3 = r_receipt(s2, ns, "m1", endpoint, (CAUSAL_ROOT_FACT,), MIX_CMD)
    assert t3.outcome is RootLineageOutcome.REPLAYED
    assert t3.state is s2
    assert t3.new_root_facts == ()
    # Observation replay idempotence at the same revision.
    t4 = r_observe(s2, ns, (read_request(endpoint, "m1", _mixed_body(A_TEXT, MARK, V2), MIX_CMD),))
    assert t4.outcome is RootLineageOutcome.REPLAYED
    assert t4.state is s2
    assert t4.diagnostics == ()
    assert t4.new_root_facts == ()
    assert validate_root_region_lineage_state(s2, ns.root_lineage_bounds) is None


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
@pytest.mark.parametrize(
    ("cmd", "body", "seg_index", "member_pos"),
    [
        (FIRST_CMD, _mixed_body(V2, MARK, A_TEXT), 0, 0),
        (MIDDLE_CMD, _mixed_body(A_TEXT, MARK, V2, MARK2, B_TEXT), 1, 1),
        (LAST_CMD, _mixed_body(A_TEXT, MARK, B_TEXT, MARK2, V2), 2, 2),
    ],
    ids=["root-first", "root-middle", "root-last"],
)
def test_a_root_positions(
    mode: AdmissionMode,
    endpoint: str,
    cmd: str,
    body: str,
    seg_index: int,
    member_pos: int,
) -> None:
    """A (018-p acceptance 1, continued): the root member is proven
    at the FIRST, MIDDLE and LAST operand position of the mixed
    command; the region coordinates bind the ACTUAL segment and
    member positions in every case."""
    ns, s0 = r_bootstrap(mode, f"p-ap-{seg_index}")
    t1 = r_issue(s0, ns, "m1", endpoint, (CAUSAL_ROOT_FACT,), cmd)
    assert t1.outcome is RootLineageOutcome.ACCEPTED
    t2 = r_observe(t1.state, ns, (read_request(endpoint, "m1", body, cmd),))
    assert t2.outcome is RootLineageOutcome.ACCEPTED, (t2.outcome, t2.diagnostics)
    s2 = t2.state
    _assert_region_bindings(s2, "m1", V2, seg_index, member_pos)
    sel = select_current_root_region(s2, ns)
    assert sel.outcome is RootSelectionOutcome.OK
    assert sel.selected_source_digest == sha256_hex(V2)
    assert validate_root_region_lineage_state(s2, ns.root_lineage_bounds) is None


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_a_unicode_crlf_and_empty_root(mode: AdmissionMode, endpoint: str) -> None:
    """A (018-p acceptance 1, continued): a Unicode multi-byte root
    body and a CRLF root body bind EXACT UTF-8 root-member bytes
    (never characters); a genuinely proven EMPTY root region is
    legal (zero bytes)."""
    unicode_body = "Ünïcodé region rööt ✓\n"
    crlf_body = "Region root with CRLF\r\nsecond line\r\n"
    for tag, root_body in (
        ("uni", unicode_body),
        ("crlf", crlf_body),
        ("empty", ""),
    ):
        ns, s0 = r_bootstrap(mode, f"p-a-{tag}")
        t1 = r_issue(s0, ns, "m1", endpoint, (CAUSAL_ROOT_FACT,), MIX_CMD)
        assert t1.outcome is RootLineageOutcome.ACCEPTED
        t2 = r_observe(
            t1.state,
            ns,
            (read_request(endpoint, "m1", _mixed_body(A_TEXT, MARK, root_body), MIX_CMD),),
        )
        assert t2.outcome is RootLineageOutcome.ACCEPTED, (t2.outcome, t2.diagnostics)
        s2 = t2.state
        f = region_fact(s2, "m1")
        assert f.source_byte_length == len(root_body.encode("utf-8"))
        if tag == "uni":
            # Multibyte: UTF-8 byte length strictly exceeds char count.
            assert f.source_byte_length != len(root_body)
        else:
            # ASCII (CRLF) source: byte length equals char length, but
            # the span/hash still bind the exact bytes.
            assert f.source_byte_length == len(root_body)
        sel = select_current_root_region(s2, ns)
        assert sel.outcome is RootSelectionOutcome.OK
        assert sel.selected_source_digest == sha256_hex(root_body)
        assert validate_root_region_lineage_state(s2, ns.root_lineage_bounds) is None


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_a_bootstrap_same_byte_singleton_inventory(mode: AdmissionMode, endpoint: str) -> None:
    """A (018-p acceptance + validator inventory law): a bootstrap
    batch carrying an ordinary SAME-bootstrap-bytes complete root
    singleton read accepts the D occurrence and retains the EXACT
    eligible-source inventory: the ONE anchor fact PLUS the eligible
    unproven read fact, with normal caps and flags.  The accepted
    bootstrap state satisfies its own complete validation."""
    ns, _ = r_bootstrap(mode, "p-a-inv")
    ns_inv = r_ns(mode, "p-a-inv")
    t0 = bootstrap_root_region_lineage(
        (root_request(), read_request(endpoint, "bs", ROOT_TEXT, "cat AGENTS.md")), ns_inv
    )
    assert t0.outcome is RootLineageOutcome.ACCEPTED, (t0.outcome, t0.diagnostics)
    s0 = t0.state
    assert s0.revision == 1
    kinds = [f.provenance.kind for f in s0.root_facts]
    assert kinds == ["envelope", "read"]
    read = s0.root_facts[1]
    assert read.issued is False and read.authority is False
    assert read.source_digest == sha256_hex(ROOT_TEXT)
    assert len(t0.new_root_facts) == 2
    assert validate_root_region_lineage_state(s0, ns_inv.root_lineage_bounds) is None
    sel = select_current_root_region(s0, ns_inv)
    assert sel.outcome is RootSelectionOutcome.OK
    assert sel.selected_source_digest == sha256_hex(ROOT_TEXT)
    assert [lim for lim in sel.limitations if lim is RootLineageLimitation.ROOT_SOURCE_UNPROVEN]


# --- B. Singleton/region interop on the frozen partial order -----------


def p_read_fact(state: Any, call_id: str) -> Any:
    return next(
        f
        for f in state.root_facts
        if f.provenance.kind == "read" and f.provenance.call_id == call_id
    )


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_b_equal_byte_singleton_region_witnesses(mode: AdmissionMode, endpoint: str) -> None:
    """New singleton and mixed-region histories interoperate in the NEW
    contract: two INCOMPARABLE equal-byte originals (an old whole-read
    witness and a NEW region witness, both children of the anchor) are
    ALL retained as the equal maximal witness set of ONE ok selection,
    with the original witnesses preserved by identity."""
    ns, s0 = r_bootstrap(mode, "p-b-eq")
    t1 = r_issue(s0, ns, "s1", endpoint, (CAUSAL_ROOT_FACT,), "cat AGENTS.md")
    assert t1.outcome is RootLineageOutcome.ACCEPTED
    t2 = r_observe(t1.state, ns, (read_request(endpoint, "s1", V2, "cat AGENTS.md"),))
    assert t2.outcome is RootLineageOutcome.ACCEPTED, (t2.outcome, t2.diagnostics)
    s2 = t2.state
    t3 = r_issue(s2, ns, "m1", endpoint, (CAUSAL_ROOT_FACT,), MIX_CMD)
    assert t3.outcome is RootLineageOutcome.ACCEPTED
    t4 = r_observe(
        t3.state, ns, (read_request(endpoint, "m1", _mixed_body(A_TEXT, MARK, V2), MIX_CMD),)
    )
    assert t4.outcome is RootLineageOutcome.ACCEPTED, (t4.outcome, t4.diagnostics)
    s4 = t4.state
    assert len(s4.root_facts) == 3
    f_s1 = p_read_fact(s4, "s1")
    f_m1 = region_fact(s4, "m1")
    assert f_s1.issued is True and f_s1.authority is True
    assert f_m1.issued is True and f_m1.authority is True
    assert f_s1.source_digest == f_m1.source_digest == sha256_hex(V2)
    _assert_region_bindings(s4, "m1", V2, expected_segment_index=1, expected_member_position=1)
    sel = select_current_root_region(s4, ns)
    assert sel.outcome is RootSelectionOutcome.OK
    assert sel.selected_source_digest == sha256_hex(V2)
    assert [f.provenance.kind for f in sel.witness_facts] == ["read", "read_region"]
    assert sel.witness_facts[0] is f_s1
    assert sel.witness_facts[1] is f_m1
    assert sel.limitations == ()
    assert validate_root_region_lineage_state(s4, ns.root_lineage_bounds) is None


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_b_deliberate_revert_v1_after_v2(mode: AdmissionMode, endpoint: str) -> None:
    """A genuinely NEW issued/anchored DESCENDANT carrying the OLD
    bootstrap bytes is a deliberate revert, NOT stale evidence: under
    the NEW P contract the frozen partial order (occurrence ancestry,
    never receipt order or source freshness) selects it, and the old
    v2 read is PRESERVED (retained, dominated -- never erased)."""
    ns, s0 = r_bootstrap(mode, "p-b-rev")
    t1 = r_issue(s0, ns, "s1", endpoint, (CAUSAL_ROOT_FACT,), "cat AGENTS.md")
    assert t1.outcome is RootLineageOutcome.ACCEPTED
    t2 = r_observe(t1.state, ns, (read_request(endpoint, "s1", V2, "cat AGENTS.md"),))
    assert t2.outcome is RootLineageOutcome.ACCEPTED, (t2.outcome, t2.diagnostics)
    s2 = t2.state
    t3 = r_issue(s2, ns, "m1", endpoint, (occurrences(s2, "s1")[0].occurrence_id,), MIX_CMD)
    assert t3.outcome is RootLineageOutcome.ACCEPTED
    t4 = r_observe(
        t3.state, ns, (read_request(endpoint, "m1", _mixed_body(A_TEXT, MARK, ROOT_TEXT), MIX_CMD),)
    )
    assert t4.outcome is RootLineageOutcome.ACCEPTED, (t4.outcome, t4.diagnostics)
    s4 = t4.state
    f_m1 = region_fact(s4, "m1")
    assert f_m1.issued is True and f_m1.authority is True
    assert f_m1.source_digest == sha256_hex(ROOT_TEXT)
    # The old v2 read is preserved as historical (dominated) evidence.
    assert p_read_fact(s4, "s1").source_digest == sha256_hex(V2)
    assert p_read_fact(s4, "s1").authority is True
    assert len(s4.root_facts) == 3
    sel = select_current_root_region(s4, ns)
    assert sel.outcome is RootSelectionOutcome.OK
    assert sel.selected_source_digest == sha256_hex(ROOT_TEXT)
    assert [f.provenance.kind for f in sel.witness_facts] == ["read_region"]
    assert sel.limitations == ()
    assert validate_root_region_lineage_state(s4, ns.root_lineage_bounds) is None


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_b_historical_retention_partial_order(mode: AdmissionMode, endpoint: str) -> None:
    """Known historical source retention in the NEW contract: a v2->v3
    singleton chain plus a genuinely issued region descendant carrying
    the OLDER v2 bytes; the frozen partial order selects the maximal
    original and every retained fact stays intact."""
    ns, s0 = r_bootstrap(mode, "p-b-hist")
    t1 = r_issue(s0, ns, "s1", endpoint, (CAUSAL_ROOT_FACT,), "cat AGENTS.md")
    assert t1.outcome is RootLineageOutcome.ACCEPTED
    t2 = r_observe(t1.state, ns, (read_request(endpoint, "s1", V2, "cat AGENTS.md"),))
    assert t2.outcome is RootLineageOutcome.ACCEPTED, (t2.outcome, t2.diagnostics)
    s2 = t2.state
    t3 = r_issue(s2, ns, "s2", endpoint, (occurrences(s2, "s1")[0].occurrence_id,), "cat AGENTS.md")
    assert t3.outcome is RootLineageOutcome.ACCEPTED
    t4 = r_observe(t3.state, ns, (read_request(endpoint, "s2", V3, "cat AGENTS.md"),))
    assert t4.outcome is RootLineageOutcome.ACCEPTED, (t4.outcome, t4.diagnostics)
    s4 = t4.state
    t5 = r_issue(s4, ns, "m1", endpoint, (occurrences(s4, "s2")[0].occurrence_id,), MIX_CMD)
    assert t5.outcome is RootLineageOutcome.ACCEPTED
    t6 = r_observe(
        t5.state, ns, (read_request(endpoint, "m1", _mixed_body(A_TEXT, MARK, V2), MIX_CMD),)
    )
    assert t6.outcome is RootLineageOutcome.ACCEPTED, (t6.outcome, t6.diagnostics)
    s6 = t6.state
    # All four historical sources retained.
    assert len(s6.root_facts) == 4
    assert p_read_fact(s6, "s1").source_digest == sha256_hex(V2)
    assert p_read_fact(s6, "s2").source_digest == sha256_hex(V3)
    f_m1 = region_fact(s6, "m1")
    assert f_m1.source_digest == sha256_hex(V2)
    assert f_m1.issued is True and f_m1.authority is True
    sel = select_current_root_region(s6, ns)
    assert sel.outcome is RootSelectionOutcome.OK
    assert sel.selected_source_digest == sha256_hex(V2)
    assert [f.provenance.kind for f in sel.witness_facts] == ["read_region"]
    assert sel.limitations == ()
    assert validate_root_region_lineage_state(s6, ns.root_lineage_bounds) is None


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_b_delayed_old_receipt_conflict(mode: AdmissionMode, endpoint: str) -> None:
    """A delayed old receipt proves an UNISSUED mixed region that was
    retained unproven; the frozen partial order then exposes the
    explicit differing-maximal conflict (never a silent override), and
    all originals are preserved."""
    ns, s0 = r_bootstrap(mode, "p-b-dlr")
    t1 = r_issue(s0, ns, "s1", endpoint, (CAUSAL_ROOT_FACT,), "cat AGENTS.md")
    assert t1.outcome is RootLineageOutcome.ACCEPTED
    t2 = r_observe(t1.state, ns, (read_request(endpoint, "s1", V2, "cat AGENTS.md"),))
    assert t2.outcome is RootLineageOutcome.ACCEPTED, (t2.outcome, t2.diagnostics)
    s2 = t2.state
    # The mixed region is observed WITHOUT issuance: retained, unproven.
    t3 = r_observe(
        s2, ns, (read_request(endpoint, "u1", _mixed_body(A_TEXT, MARK, ROOT_TEXT), MIX_CMD),)
    )
    assert t3.outcome is RootLineageOutcome.ACCEPTED, (t3.outcome, t3.diagnostics)
    s3 = t3.state
    f_u1 = region_fact(s3, "u1")
    assert f_u1.issued is False and f_u1.authority is False
    assert occurrences(s3, "u1")[0].anchored is False
    sel3 = select_current_root_region(s3, ns)
    assert sel3.outcome is RootSelectionOutcome.OK
    assert sel3.selected_source_digest == sha256_hex(V2)
    assert RootLineageLimitation.ROOT_SOURCE_UNPROVEN in sel3.limitations
    # The matching late receipt proves the retained region.
    t4 = r_receipt(s3, ns, "u1", endpoint, (CAUSAL_ROOT_FACT,), MIX_CMD)
    assert t4.outcome is RootLineageOutcome.ACCEPTED, (t4.outcome, t4.diagnostics)
    s4 = t4.state
    f_u1_4 = region_fact(s4, "u1")
    assert f_u1_4.issued is True and f_u1_4.authority is True
    assert occurrences(s4, "u1")[0].anchored is True
    # s1 (v2, child of the anchor) and u1 (old bytes, child of the
    # anchor) are incomparable maximal originals: explicit conflict,
    # NO selected current source, both preserved.
    sel4 = select_current_root_region(s4, ns)
    assert sel4.outcome is RootSelectionOutcome.ROOT_CONTENT_CONFLICT
    assert sel4.selected_source_digest is None
    # Canonical (kind, occurrence_id) order: the read witness first.
    w_s1 = p_read_fact(s4, "s1")
    w_u1 = region_fact(s4, "u1")
    assert [f.provenance.kind for f in sel4.witness_facts] == ["read", "read_region"]
    assert sel4.witness_facts[0] is w_s1
    assert sel4.witness_facts[1] is w_u1
    assert len({f.source_digest for f in sel4.witness_facts}) == 2
    assert sel4.limitations == ()
    assert len(s4.root_facts) == 3
    assert validate_root_region_lineage_state(s4, ns.root_lineage_bounds) is None


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_b_late_authority_to_ancestor_no_override(mode: AdmissionMode, endpoint: str) -> None:
    """Late authority to a proven ANCESTOR cannot beat its actual
    DESCENDANT: the unissued unproven ancestor region is proven by a
    matching late receipt only after a genuine issued descendant read
    exists; the frozen partial order keeps the descendant selected.
    Frozen parents only, never receipt order."""
    ns, s0 = r_bootstrap(mode, "p-b-anc")
    # Unissued mixed region observed first: retained unproven (child of
    # the anchor once its receipt names the anchor frontier).
    t1 = r_observe(s0, ns, (read_request(endpoint, "u1", _mixed_body(A_TEXT, MARK, V2), MIX_CMD),))
    assert t1.outcome is RootLineageOutcome.ACCEPTED, (t1.outcome, t1.diagnostics)
    s1 = t1.state
    f_u1 = region_fact(s1, "u1")
    assert f_u1.issued is False and f_u1.authority is False
    # A genuine issued singleton read as a child of the (still
    # unanchored) retained occurrence.
    t2 = r_issue(s1, ns, "s1", endpoint, (occurrences(s1, "u1")[0].occurrence_id,), "cat AGENTS.md")
    assert t2.outcome is RootLineageOutcome.ACCEPTED, (t2.outcome, t2.diagnostics)
    s2 = t2.state
    t3 = r_observe(s2, ns, (read_request(endpoint, "s1", V3, "cat AGENTS.md"),))
    assert t3.outcome is RootLineageOutcome.ACCEPTED, (t3.outcome, t3.diagnostics)
    s3 = t3.state
    f_s1 = p_read_fact(s3, "s1")
    # The descendant is issued but its frozen parent chain does not
    # yet reach the anchor (the parent is unanchored): no authority.
    assert f_s1.issued is True and f_s1.authority is False
    sel3 = select_current_root_region(s3, ns)
    assert sel3.outcome is RootSelectionOutcome.OK
    assert sel3.selected_source_digest == sha256_hex(ROOT_TEXT)
    assert RootLineageLimitation.ROOT_SOURCE_UNPROVEN in sel3.limitations
    # The late receipt proves the ancestor; the chain now reaches the
    # anchor and BOTH become authoritative -- but the DESCENDANT
    # stays the maximal selected original (no rollback).
    t4 = r_receipt(s3, ns, "u1", endpoint, (CAUSAL_ROOT_FACT,), MIX_CMD)
    assert t4.outcome is RootLineageOutcome.ACCEPTED, (t4.outcome, t4.diagnostics)
    s4 = t4.state
    assert region_fact(s4, "u1").authority is True
    assert p_read_fact(s4, "s1").authority is True
    sel4 = select_current_root_region(s4, ns)
    assert sel4.outcome is RootSelectionOutcome.OK
    assert sel4.selected_source_digest == sha256_hex(V3)
    assert [f.provenance.kind for f in sel4.witness_facts] == ["read"]
    assert sel4.limitations == ()
    assert validate_root_region_lineage_state(s4, ns.root_lineage_bounds) is None


# --- C. Authority, causal resolution, envelope law ---------------------

E_BODY = "Envelope changed root body."


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_c_unissued_mixed_issuance_then_receipt(mode: AdmissionMode, endpoint: str) -> None:
    """Unissued mixed-only source stays unproven; a later actual
    ISSUANCE alone retains the issued flag but NEVER anchors (no
    authority); the matching late RECEIPT then anchors the occurrence
    and the region earns authority under its frozen frontier."""
    ns, s0 = r_bootstrap(mode, "p-c-uir")
    t1 = r_observe(s0, ns, (read_request(endpoint, "u1", _mixed_body(A_TEXT, MARK, V2), MIX_CMD),))
    assert t1.outcome is RootLineageOutcome.ACCEPTED, (t1.outcome, t1.diagnostics)
    s1 = t1.state
    f1 = region_fact(s1, "u1")
    assert f1.issued is False and f1.authority is False
    sel1 = select_current_root_region(s1, ns)
    assert sel1.outcome is RootSelectionOutcome.OK
    assert sel1.selected_source_digest == sha256_hex(ROOT_TEXT)
    assert RootLineageLimitation.ROOT_SOURCE_UNPROVEN in sel1.limitations
    # The later actual issuance (same immutable binding) is accepted
    # but does NOT anchor the already-observed occurrence.
    t2 = r_issue(s1, ns, "u1", endpoint, (CAUSAL_ROOT_FACT,), MIX_CMD)
    assert t2.outcome is RootLineageOutcome.ACCEPTED, (t2.outcome, t2.diagnostics)
    s2 = t2.state
    f2 = region_fact(s2, "u1")
    assert f2.issued is True and f2.authority is False
    assert occurrences(s2, "u1")[0].anchored is False
    sel2 = select_current_root_region(s2, ns)
    assert sel2.outcome is RootSelectionOutcome.OK
    assert sel2.selected_source_digest == sha256_hex(ROOT_TEXT)
    assert RootLineageLimitation.ROOT_SOURCE_UNPROVEN in sel2.limitations
    # The matching valid receipt proves the retained region.
    t3 = r_receipt(s2, ns, "u1", endpoint, (CAUSAL_ROOT_FACT,), MIX_CMD)
    assert t3.outcome is RootLineageOutcome.ACCEPTED, (t3.outcome, t3.diagnostics)
    s3 = t3.state
    f3 = region_fact(s3, "u1")
    assert f3.issued is True and f3.authority is True
    assert occurrences(s3, "u1")[0].anchored is True
    sel3 = select_current_root_region(s3, ns)
    assert sel3.outcome is RootSelectionOutcome.OK
    assert sel3.selected_source_digest == sha256_hex(V2)
    assert sel3.limitations == ()
    assert validate_root_region_lineage_state(s3, ns.root_lineage_bounds) is None


def _two_sibling_regions(
    mode: AdmissionMode, lineage: str, endpoint: str
) -> tuple[Any, Any, Any, Any]:
    """Bootstrap + two INCOMPARABLE issued region children of the
    anchor (v2 and v3 bytes); returns (ns, state, m1 fact, m2 fact)."""
    ns, s0 = r_bootstrap(mode, lineage)
    t1 = r_issue(s0, ns, "m1", endpoint, (CAUSAL_ROOT_FACT,), MIX_CMD)
    assert t1.outcome is RootLineageOutcome.ACCEPTED
    t2 = r_observe(
        t1.state, ns, (read_request(endpoint, "m1", _mixed_body(A_TEXT, MARK, V2), MIX_CMD),)
    )
    assert t2.outcome is RootLineageOutcome.ACCEPTED, (t2.outcome, t2.diagnostics)
    s2 = t2.state
    t3 = r_issue(s2, ns, "m2", endpoint, (CAUSAL_ROOT_FACT,), MIX_CMD)
    assert t3.outcome is RootLineageOutcome.ACCEPTED
    t4 = r_observe(
        t3.state, ns, (read_request(endpoint, "m2", _mixed_body(A_TEXT, MARK, V3), MIX_CMD),)
    )
    assert t4.outcome is RootLineageOutcome.ACCEPTED, (t4.outcome, t4.diagnostics)
    s4 = t4.state
    return ns, s4, region_fact(s4, "m1"), region_fact(s4, "m2")


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_c_incomparable_differing_regions_conflict(mode: AdmissionMode, endpoint: str) -> None:
    """Incomparable differing regions conflict with NO selected
    current source; both maximal witnesses are retained."""
    ns, s4, f_m1, f_m2 = _two_sibling_regions(mode, "p-c-diff", endpoint)
    assert f_m1.authority and f_m2.authority
    expected = tuple(
        sorted(
            (f_m1, f_m2),
            key=lambda f: (f.provenance.kind, f.provenance.occurrence_id),
        )
    )
    sel = select_current_root_region(s4, ns)
    assert sel.outcome is RootSelectionOutcome.ROOT_CONTENT_CONFLICT
    assert sel.selected_source_digest is None
    assert sel.witness_facts == expected
    assert sel.witness_facts[0] is expected[0]
    assert sel.witness_facts[1] is expected[1]
    assert len({f.source_digest for f in sel.witness_facts}) == 2
    assert sel.limitations == ()
    assert len(s4.root_facts) == 3
    assert validate_root_region_lineage_state(s4, ns.root_lineage_bounds) is None


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_c_descendant_of_all_resolves(mode: AdmissionMode, endpoint: str) -> None:
    """A genuine region descendant of ALL relevant branches resolves
    the conflict: ONE witness, the new source selected, both parents
    preserved (dominated, never erased)."""
    ns, s4, f_m1, f_m2 = _two_sibling_regions(mode, "p-c-all", endpoint)
    t5 = r_issue(
        s4,
        ns,
        "m3",
        endpoint,
        (
            occurrences(s4, "m1")[0].occurrence_id,
            occurrences(s4, "m2")[0].occurrence_id,
        ),
        MIX_CMD,
    )
    assert t5.outcome is RootLineageOutcome.ACCEPTED
    t6 = r_observe(
        t5.state, ns, (read_request(endpoint, "m3", _mixed_body(A_TEXT, MARK, V4), MIX_CMD),)
    )
    assert t6.outcome is RootLineageOutcome.ACCEPTED, (t6.outcome, t6.diagnostics)
    s6 = t6.state
    f_m3 = region_fact(s6, "m3")
    assert f_m3.issued is True and f_m3.authority is True
    assert region_fact(s6, "m1").source_digest == sha256_hex(V2)
    assert region_fact(s6, "m2").source_digest == sha256_hex(V3)
    assert len(s6.root_facts) == 4
    sel = select_current_root_region(s6, ns)
    assert sel.outcome is RootSelectionOutcome.OK
    assert sel.selected_source_digest == sha256_hex(V4)
    assert sel.witness_facts == (f_m3,)
    assert sel.limitations == ()
    assert validate_root_region_lineage_state(s6, ns.root_lineage_bounds) is None


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_c_child_of_one_branch_conflict(mode: AdmissionMode, endpoint: str) -> None:
    """A child of ONE branch cannot dominate the other branch: the
    new region and the untouched sibling remain differing maximal
    originals with no selected source."""
    ns, s4, f_m1, f_m2 = _two_sibling_regions(mode, "p-c-one", endpoint)
    t5 = r_issue(s4, ns, "m3", endpoint, (occurrences(s4, "m1")[0].occurrence_id,), MIX_CMD)
    assert t5.outcome is RootLineageOutcome.ACCEPTED
    t6 = r_observe(
        t5.state, ns, (read_request(endpoint, "m3", _mixed_body(A_TEXT, MARK, V4), MIX_CMD),)
    )
    assert t6.outcome is RootLineageOutcome.ACCEPTED, (t6.outcome, t6.diagnostics)
    s6 = t6.state
    # S1 re-derivation replaces fact objects on the accepted
    # transition: the witnesses must be asserted from the FINAL same
    # state, canonical-sorted by provenance coordinates
    # (kind, occurrence_id) -- never by call/issuance order.
    w_m2 = region_fact(s6, "m2")
    w_m3 = region_fact(s6, "m3")
    assert w_m3.authority is True
    expected = tuple(
        sorted(
            (w_m2, w_m3),
            key=lambda f: (f.provenance.kind, f.provenance.occurrence_id),
        )
    )
    sel = select_current_root_region(s6, ns)
    assert sel.outcome is RootSelectionOutcome.ROOT_CONTENT_CONFLICT
    assert sel.selected_source_digest is None
    assert sel.witness_facts == expected
    assert sel.witness_facts[0] is expected[0]
    assert sel.witness_facts[1] is expected[1]
    assert len({f.source_digest for f in sel.witness_facts}) == 2
    assert len(s6.root_facts) == 4


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_c_envelope_alone_atomic_refusal(mode: AdmissionMode, endpoint: str) -> None:
    """Envelope-alone authorization refuses atomically: a changed
    envelope with an UNISSUED (unproven) mixed region in the same
    batch grants nothing; the EXACT prior region state is preserved
    while the actual accepted D candidate is carried only as
    discarded evidence (the D revision fields mirror it)."""
    ns, s0 = r_bootstrap(mode, "p-c-env")
    prior_d_revision = s0.d_state.revision
    t = r_observe(
        s0,
        ns,
        (
            changed_root_envelope(E_BODY),
            read_request(endpoint, "m1", _mixed_body(A_TEXT, MARK, E_BODY), MIX_CMD),
        ),
    )
    assert_refused(
        t, s0, RootLineageOutcome.REFUSED_ROOT_AUTHORITY, (RootLineageLimitation.ENVELOPE_UNPROVEN,)
    )
    assert t.d_transition is not None
    assert t.d_transition.outcome is CausalHistoryOutcome.ACCEPTED
    assert t.d_revision_before == prior_d_revision
    assert t.d_revision_after == prior_d_revision + 1
    assert t.d_transition.state is not s0.d_state
    assert s0.d_state.revision == prior_d_revision
    assert read_region_facts(s0) == []
    assert validate_root_region_lineage_state(s0, ns.root_lineage_bounds) is None


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_c_same_batch_authorized_region_envelope(mode: AdmissionMode, endpoint: str) -> None:
    """A same-batch INDEPENDENTLY authorized region plus a matching
    changed envelope is accepted atomically: the region read (issued
    pre-batch under the anchor frontier) earns authority in the same
    batch and authorizes the changed envelope; the D anchor stays
    immutable, the selection follows the region, and the now-known
    envelope replays as a noop afterwards."""
    ns, s0 = r_bootstrap(mode, "p-c-sb")
    anchor = s0.d_state.root
    assert anchor is not None
    t1 = r_issue(s0, ns, "sr", endpoint, (CAUSAL_ROOT_FACT,), MIX_CMD)
    assert t1.outcome is RootLineageOutcome.ACCEPTED
    t2 = r_observe(
        t1.state,
        ns,
        (
            changed_root_envelope(E_BODY),
            read_request(endpoint, "sr", _mixed_body(A_TEXT, MARK, E_BODY), MIX_CMD),
        ),
    )
    assert t2.outcome is RootLineageOutcome.ACCEPTED, (t2.outcome, t2.diagnostics)
    s2 = t2.state
    assert s2.d_state.root is anchor  # the bootstrap anchor stays immutable
    f_sr = region_fact(s2, "sr")
    assert f_sr.issued is True and f_sr.authority is True
    assert f_sr.source_digest == sha256_hex(E_BODY)
    _assert_region_bindings(s2, "sr", E_BODY, expected_segment_index=1, expected_member_position=1)
    sel = select_current_root_region(s2, ns)
    assert sel.outcome is RootSelectionOutcome.OK
    assert sel.selected_source_digest == sha256_hex(E_BODY)
    assert [f.provenance.kind for f in sel.witness_facts] == ["read_region"]
    assert sel.limitations == ()
    # The now-known new envelope replays; the old envelope still does.
    t3 = r_observe(s2, ns, (changed_root_envelope(E_BODY),))
    assert t3.outcome is RootLineageOutcome.REPLAYED
    assert t3.state is s2
    t4 = r_observe(s2, ns, (root_request(),))
    assert t4.outcome is RootLineageOutcome.REPLAYED
    assert t4.state is s2
    assert validate_root_region_lineage_state(s2, ns.root_lineage_bounds) is None


# --- D. No-exception shapes through the NEW public operation -----------


def _mixed_frame_request(endpoint: str, cid: str, frame: str) -> Any:
    """One original read request on EITHER endpoint carrying the given
    synthetic frame for the ACTUAL mixed command (known-synthetic,
    original frames only; no process/client startup)."""
    if endpoint == "responses":
        payload = {"input": [exec_call(cid, MIX_CMD), out_item(cid, frame)]}
    else:
        payload = {
            "messages": [
                {
                    "role": "assistant",
                    "tool_calls": [
                        {
                            "id": cid,
                            "type": "function",
                            "function": {
                                "name": "exec_command",
                                "arguments": json.dumps({"cmd": MIX_CMD}),
                            },
                        }
                    ],
                },
                {"role": "tool", "tool_call_id": cid, "content": frame},
            ]
        }
    return GraphRequest(payload=payload, endpoint=endpoint, context=None)


def _pending_mixed_request(endpoint: str, cid: str, part: str, session_id: int = 9301) -> Any:
    frame = (
        "Chunk ID: a1b2c3\n"
        "Wall time: 0.0010 seconds\n"
        f"Process running with session ID {session_id}\n"
        "Original token count: 4\n"
        f"Output:\n{part}"
    )
    return _mixed_frame_request(endpoint, cid, frame)


def _truncated_mixed_request(endpoint: str, cid: str) -> Any:
    body = _mixed_body(A_TEXT, MARK, V2)
    warning = (
        f"Warning: truncated output (original token count: 512)\nTotal output lines: 64\n\n{body}"
    )
    frame = (
        "Chunk ID: 3d4e5f\n"
        "Wall time: 0.6789 seconds\n"
        "Process exited with code 0\n"
        "Original token count: 512\n"
        f"Output:\n{warning}"
    )
    return _mixed_frame_request(endpoint, cid, frame)


def _nonzero_mixed_request(endpoint: str, cid: str, body: str, code: int = 1) -> Any:
    frame = (
        "Chunk ID: synthetic\n"
        "Wall time: 0.0000 seconds\n"
        f"Process exited with code {code}\n"
        f"Output:\n{body}"
    )
    return _mixed_frame_request(endpoint, cid, frame)


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_d_repeated_root_matching_no_region(mode: AdmissionMode, endpoint: str) -> None:
    """A repeated root that MATCHES the current anchor is a retained
    ordinary read but mints NO root fact (the singleton-root filter;
    repeated roots gain NO exception in the NEW contract); the
    selection stays the anchor."""
    ns, s0 = r_bootstrap(mode, "p-d-rep")
    t1 = r_issue(s0, ns, "rp", endpoint, (CAUSAL_ROOT_FACT,), REPEAT_CMD)
    assert t1.outcome is RootLineageOutcome.ACCEPTED
    t2 = r_observe(
        t1.state,
        ns,
        (read_request(endpoint, "rp", _mixed_body(ROOT_TEXT, MARK, ROOT_TEXT), REPEAT_CMD),),
    )
    assert t2.outcome is RootLineageOutcome.ACCEPTED, (t2.outcome, t2.diagnostics)
    s2 = t2.state
    assert len(occurrences(s2, "rp")) == 1
    assert read_region_facts(s2) == []
    assert not any(f.provenance.kind == "read" for f in s2.root_facts)
    sel = select_current_root_region(s2, ns)
    assert sel.outcome is RootSelectionOutcome.OK
    assert sel.selected_source_digest == sha256_hex(ROOT_TEXT)
    assert sel.limitations == ()
    assert validate_root_region_lineage_state(s2, ns.root_lineage_bounds) is None


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_d_repeated_root_competing_refused(mode: AdmissionMode, endpoint: str) -> None:
    """Repeated root operands with bodies DISAGREEING with the current
    anchor are competing root evidence at the ACTUAL D level: the
    whole D candidate is atomically discarded and the EXACT prior
    region state is preserved (old D law unchanged)."""
    ns, s0 = r_bootstrap(mode, "p-d-repc")
    t1 = r_issue(s0, ns, "rp", endpoint, (CAUSAL_ROOT_FACT,), REPEAT_CMD)
    assert t1.outcome is RootLineageOutcome.ACCEPTED
    t2 = r_observe(
        t1.state, ns, (read_request(endpoint, "rp", _mixed_body(V2, MARK, V3), REPEAT_CMD),)
    )
    assert_refused(
        t2,
        t1.state,
        RootLineageOutcome.REFUSED_ROOT_CONFLICT,
        (RootLineageLimitation.COMPETING_ROOTS,),
    )
    assert t2.d_transition is not None
    assert t2.d_transition.outcome is CausalHistoryOutcome.REFUSED_ROOT_CONFLICT
    assert occurrences(t1.state, "rp") == []


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_d_hidden_opaque_root_no_region(mode: AdmissionMode, endpoint: str) -> None:
    """A second root occurrence hidden INSIDE an opaque multi-member
    segment (no attribution) grants NO exception: the read is a
    retained ordinary proof, no region fact is minted, and the
    selection stays the anchor (the matching proven first root
    segment is not competing)."""
    ns, s0 = r_bootstrap(mode, "p-d-hid")
    t1 = r_issue(s0, ns, "hp", endpoint, (CAUSAL_ROOT_FACT,), REPEAT_OPAQUE_CMD)
    assert t1.outcome is RootLineageOutcome.ACCEPTED
    t2 = r_observe(
        t1.state,
        ns,
        (
            read_request(
                endpoint, "hp", _mixed_body(ROOT_TEXT, MARK, ROOT_TEXT + B_TEXT), REPEAT_OPAQUE_CMD
            ),
        ),
    )
    assert t2.outcome is RootLineageOutcome.ACCEPTED, (t2.outcome, t2.diagnostics)
    s2 = t2.state
    assert len(occurrences(s2, "hp")) == 1
    assert read_region_facts(s2) == []
    assert not any(f.provenance.kind == "read" for f in s2.root_facts)
    sel = select_current_root_region(s2, ns)
    assert sel.outcome is RootSelectionOutcome.OK
    assert sel.selected_source_digest == sha256_hex(ROOT_TEXT)
    assert sel.limitations == ()
    assert validate_root_region_lineage_state(s2, ns.root_lineage_bounds) is None


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_d_missing_marker_in_earned_plan(mode: AdmissionMode, endpoint: str) -> None:
    """A body that is missing the EARNED plan's marker line is a
    typed MARKER_MISSING non-acquiring observation: the form grants
    nothing and the EXACT prior state is preserved (no exception)."""
    ns, s0 = r_bootstrap(mode, "p-d-mk")
    t1 = r_issue(s0, ns, "dq", endpoint, (CAUSAL_ROOT_FACT,), MIX_CMD)
    assert t1.outcome is RootLineageOutcome.ACCEPTED
    t2 = r_observe(t1.state, ns, (read_request(endpoint, "dq", SIBLING_X, MIX_CMD),))
    assert_refused(
        t2, t1.state, RootLineageOutcome.REPLAYED, (RootLineageLimitation.MARKER_MISSING,)
    )
    assert occurrences(t1.state, "dq") == []


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_d_truly_unsupported_grammar(mode: AdmissionMode, endpoint: str) -> None:
    """A command that is NOT a literal read plan at all (echo only,
    no cat statement) is a typed PLAN_UNSUPPORTED non-acquiring
    observation: the form grants nothing and the EXACT prior state
    is preserved (no exception)."""
    ns, s0 = r_bootstrap(mode, "p-d-unsup")
    t1 = r_issue(s0, ns, "un", endpoint, (CAUSAL_ROOT_FACT,), "echo 'ROOTSEP'")
    assert t1.outcome is RootLineageOutcome.ACCEPTED
    t2 = r_observe(t1.state, ns, (read_request(endpoint, "un", SIBLING_X, "echo 'ROOTSEP'"),))
    assert_refused(
        t2, t1.state, RootLineageOutcome.REPLAYED, (RootLineageLimitation.PLAN_UNSUPPORTED,)
    )
    assert occurrences(t1.state, "un") == []


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_d_pending_mixed_retained(mode: AdmissionMode, endpoint: str) -> None:
    """A paired PENDING mixed read is retained honestly as a PARTIAL
    result: no occurrence, no region fact, the bootstrap stays
    current (partial reads gain NO exception)."""
    ns, s0 = r_bootstrap(mode, "p-d-pend")
    t1 = r_issue(s0, ns, "pm", endpoint, (CAUSAL_ROOT_FACT,), MIX_CMD)
    assert t1.outcome is RootLineageOutcome.ACCEPTED
    t2 = r_observe(
        t1.state,
        ns,
        (_pending_mixed_request(endpoint, "pm", A_TEXT + MARK + "\nPartial region."),),
    )
    assert t2.outcome is RootLineageOutcome.ACCEPTED, (t2.outcome, t2.diagnostics)
    s2 = t2.state
    assert occurrences(s2, "pm") == []
    assert read_region_facts(s2) == []
    pend = [r for r in s2.d_state.results if r.call_id == "pm"]
    assert len(pend) == 1
    assert pend[0].complete is False
    sel = select_current_root_region(s2, ns)
    assert sel.outcome is RootSelectionOutcome.OK
    assert sel.selected_source_digest == sha256_hex(ROOT_TEXT)
    assert sel.limitations == ()


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_d_truncated_mixed_retained(mode: AdmissionMode, endpoint: str) -> None:
    """An ACTUAL earned TRUNCATION on a complete (exit-zero) mixed
    read frame: the output never completes -- the batch is retained
    honestly as an INCOMPLETE result carrying the typed
    PROCESS_TRUNCATED limitation, NO occurrence and NO region fact
    are minted, and the bootstrap stays the selected current root."""
    ns, s0 = r_bootstrap(mode, "p-d-trunc")
    t1 = r_issue(s0, ns, "tm", endpoint, (CAUSAL_ROOT_FACT,), MIX_CMD)
    assert t1.outcome is RootLineageOutcome.ACCEPTED
    t2 = r_observe(t1.state, ns, (_truncated_mixed_request(endpoint, "tm"),))
    assert t2.outcome is RootLineageOutcome.ACCEPTED, (t2.outcome, t2.diagnostics)
    s2 = t2.state
    assert occurrences(s2, "tm") == []
    assert read_region_facts(s2) == []
    pend = [r for r in s2.d_state.results if r.call_id == "tm"]
    assert len(pend) == 1
    assert pend[0].complete is False
    dt = t2.d_transition
    assert dt is not None
    assert Limitation.PROCESS_TRUNCATED in dt.observation_limitations
    sel = select_current_root_region(s2, ns)
    assert sel.outcome is RootSelectionOutcome.OK
    assert sel.selected_source_digest == sha256_hex(ROOT_TEXT)
    assert sel.limitations == ()


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_d_nonzero_mixed_noop(mode: AdmissionMode, endpoint: str) -> None:
    """A nonzero-exit mixed frame is NOT a completed read: the form
    grants nothing and the EXACT prior state is preserved (old law)."""
    ns, s0 = r_bootstrap(mode, "p-d-nz")
    t1 = r_issue(s0, ns, "nz", endpoint, (CAUSAL_ROOT_FACT,), MIX_CMD)
    assert t1.outcome is RootLineageOutcome.ACCEPTED
    t2 = r_observe(
        t1.state, ns, (_nonzero_mixed_request(endpoint, "nz", _mixed_body(A_TEXT, MARK, V2)),)
    )
    assert_refused(
        t2, t1.state, RootLineageOutcome.REPLAYED, (RootLineageLimitation.OUTPUT_INCONSISTENT,)
    )
    assert occurrences(t1.state, "nz") == []


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_d_unpaired_frame_noop(mode: AdmissionMode, endpoint: str) -> None:
    """A result frame with NO causally paired call is an unpairable
    stray: the batch grants nothing and the EXACT prior state is
    preserved (unpaired results never anchor)."""
    ns, s0 = r_bootstrap(mode, "p-d-unp")
    if endpoint == "responses":
        payload = {"input": [out_item("ghost", "Stray output frame.\n")]}
    else:
        payload = {
            "messages": [
                {"role": "tool", "tool_call_id": "ghost", "content": "Stray output frame.\n"}
            ]
        }
    req = GraphRequest(payload=payload, endpoint=endpoint, context=None)
    t = r_observe(s0, ns, (req,))
    assert t.outcome is RootLineageOutcome.REPLAYED
    assert t.state is s0
    assert t.diagnostics == ()
    assert t.new_root_facts == ()


# --- E. Resulting states + honest old-I refusal ------------------------


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_e_resulting_state_supports_operations(mode: AdmissionMode, endpoint: str) -> None:
    """Actual resulting states support subsequent new-version
    registration, observation, validation and selection: a new
    issuance anchored at the actual region occurrence, an ordinary
    nonroot read that mints nothing, clean validation, and a new
    region descendant that refreshes the selection."""
    ns, s0 = r_bootstrap(mode, "p-e-supp")
    t1 = r_issue(s0, ns, "m1", endpoint, (CAUSAL_ROOT_FACT,), MIX_CMD)
    assert t1.outcome is RootLineageOutcome.ACCEPTED
    t2 = r_observe(
        t1.state, ns, (read_request(endpoint, "m1", _mixed_body(A_TEXT, MARK, V2), MIX_CMD),)
    )
    assert t2.outcome is RootLineageOutcome.ACCEPTED, (t2.outcome, t2.diagnostics)
    s2 = t2.state
    # The original anchor/occurrence/proof identities are preserved
    # BY REFERENCE through every subsequent operation (retained by
    # bounded immutable reference, never copied per operation).
    anchor = s2.d_state.root
    assert anchor is not None
    m1_occ = next(o for o in s2.d_state.occurrences if o.call_id == "m1")
    m1_proof = m1_occ.proof
    t3 = r_issue(s2, ns, "m2", endpoint, (occurrences(s2, "m1")[0].occurrence_id,), MIX_CMD)
    assert t3.outcome is RootLineageOutcome.ACCEPTED
    assert t3.state.d_state.root is anchor
    t4 = r_observe(t3.state, ns, (read_request(endpoint, "n1", A_TEXT, "cat A.md"),))
    assert t4.outcome is RootLineageOutcome.ACCEPTED, (t4.outcome, t4.diagnostics)
    s4 = t4.state
    assert s4.d_state.root is anchor
    n1_occ4 = next(o for o in s4.d_state.occurrences if o.call_id == "n1")
    n1_proof4 = n1_occ4.proof
    m1_occ4 = next(o for o in s4.d_state.occurrences if o.call_id == "m1")
    assert m1_occ4 is m1_occ
    assert m1_occ4.proof is m1_proof
    assert len(read_region_facts(s4)) == 1
    assert not any(f.provenance.kind == "read" for f in s4.root_facts)
    assert validate_root_region_lineage_state(s4, ns.root_lineage_bounds) is None
    sel4 = select_current_root_region(s4, ns)
    assert sel4.outcome is RootSelectionOutcome.OK
    assert sel4.selected_source_digest == sha256_hex(V2)
    t5 = r_observe(
        t4.state, ns, (read_request(endpoint, "m2", _mixed_body(A_TEXT, MARK, V3), MIX_CMD),)
    )
    assert t5.outcome is RootLineageOutcome.ACCEPTED, (t5.outcome, t5.diagnostics)
    s5 = t5.state
    assert s5.d_state.root is anchor
    m1_occ5 = next(o for o in s5.d_state.occurrences if o.call_id == "m1")
    assert m1_occ5 is m1_occ
    assert m1_occ5.occurrence_id == m1_occ.occurrence_id
    assert m1_occ5.proof is m1_proof
    n1_occ5 = next(o for o in s5.d_state.occurrences if o.call_id == "n1")
    assert n1_occ5 is n1_occ4
    assert n1_occ5.proof is n1_proof4
    sel5 = select_current_root_region(s5, ns)
    assert sel5.outcome is RootSelectionOutcome.OK
    assert sel5.selected_source_digest == sha256_hex(V3)
    assert validate_root_region_lineage_state(s5, ns.root_lineage_bounds) is None


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_e_old_i_refuses_region_state_honestly(mode: AdmissionMode, endpoint: str) -> None:
    """The existing old I must honestly refuse a genuinely unsupported
    region-version state BEFORE positive use.  The fixed state-shape
    gate classifies the region state as REFUSED_STATE_MALFORMED /
    STATE_MALFORMED first; the old result schema carries an
    InstanceOf[RootLineageState] and cannot hold a foreign state
    without broadening the old positive law, so the narrow explicit
    rejection boundary is a TYPED fixed private ValueError
    BEFORE any old positive work or result construction (no
    graph/admission/selection, no partial output, no fabricated old
    state).  The old I positive behavior, types, schemas and
    versions are unchanged; the new consumer round, not this
    producer round, must consume the region state."""
    ns, s0 = r_bootstrap(mode, "p-e-oldi")
    t1 = r_issue(s0, ns, "m1", endpoint, (CAUSAL_ROOT_FACT,), MIX_CMD)
    assert t1.outcome is RootLineageOutcome.ACCEPTED
    t2 = r_observe(
        t1.state, ns, (read_request(endpoint, "m1", _mixed_body(A_TEXT, MARK, V2), MIX_CMD),)
    )
    assert t2.outcome is RootLineageOutcome.ACCEPTED, (t2.outcome, t2.diagnostics)
    s2 = t2.state
    with pytest.raises(
        ValueError,
        match="a NEW 018-p root-region lineage state is genuinely unsupported",
    ):
        derive(s2, ns)


# --- F. ONE new-operation outer at the actual work ceiling --------------


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_f_sequence_work_cap_target_reached(mode: AdmissionMode, endpoint: str) -> None:
    """The minimum cap at which the full bootstrap -> issuance ->
    mixed-observation sequence is accepted is the ACTUAL work
    boundary; exactly one unit below it the genuine setup steps are
    accepted and the TARGET mixed operation is refused with the exact
    domain reason and the EXACT prior state (no partial output)."""

    def run_steps(cap: int, tag: str) -> tuple[Any, Any, Any, Any]:
        ns = r_ns(mode, tag, bounds=RootLineageBounds(max_total_work_units=cap))
        t0 = bootstrap_root_region_lineage((root_request(),), ns)
        if t0.outcome is not RootLineageOutcome.ACCEPTED:
            return ns, t0, None, None
        t1 = r_issue(t0.state, ns, "m1", endpoint, (CAUSAL_ROOT_FACT,), MIX_CMD)
        if t1.outcome is not RootLineageOutcome.ACCEPTED:
            return ns, t0, t1, None
        t2 = r_observe(
            t1.state, ns, (read_request(endpoint, "m1", _mixed_body(A_TEXT, MARK, V2), MIX_CMD),)
        )
        return ns, t0, t1, t2

    def probe(m: AdmissionMode, tag: str, n: int, cap: int) -> bool:
        _ns, t0, t1, t2 = run_steps(cap, f"p-f-{m.value}-{tag}-{n}")
        return (
            t0 is not None
            and t0.outcome is RootLineageOutcome.ACCEPTED
            and t1 is not None
            and t1.outcome is RootLineageOutcome.ACCEPTED
            and t2 is not None
            and t2.outcome is RootLineageOutcome.ACCEPTED
        )

    cap = _min_accepted_cap(mode, f"{endpoint}-seq", probe)
    # AT the cap: the full sequence is accepted and the selection
    # follows the region.
    ns, t0, t1, t2 = run_steps(cap, f"p-f-{mode.value}-{endpoint}-at")
    assert t0.outcome is RootLineageOutcome.ACCEPTED
    assert t1.outcome is RootLineageOutcome.ACCEPTED
    assert t2.outcome is RootLineageOutcome.ACCEPTED, (t2.outcome, t2.diagnostics)
    sel = select_current_root_region(t2.state, ns)
    assert sel.outcome is RootSelectionOutcome.OK
    assert sel.selected_source_digest == sha256_hex(V2)
    # ONE unit below: the genuine setup steps are accepted and the
    # TARGET mixed operation crosses.
    ns1, t0b, t1b, t2b = run_steps(cap - 1, f"p-f-{mode.value}-{endpoint}-below")
    assert t0b.outcome is RootLineageOutcome.ACCEPTED, (t0b.outcome, t0b.diagnostics)
    assert t1b.outcome is RootLineageOutcome.ACCEPTED, (t1b.outcome, t1b.diagnostics)
    assert t2b is not None
    assert t2b.outcome is RootLineageOutcome.REFUSED_OVER_BOUND
    assert t2b.diagnostics == (RootLineageLimitation.WORK_UNITS_OVER_BOUND,)
    assert t2b.state is t1b.state
    assert t2b.new_root_facts == ()
    assert t2b.revision_after == t1b.state.revision


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_f_bootstrap_work_cap_at_limit_first_over(
    mode: AdmissionMode, endpoint: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The bootstrap work boundary, MEASURED on this fixture with a
    real constructor counter (the empty published output alone proves
    only atomicity, not zero constructions):

    - at the full minimum cap the bootstrap is ACCEPTED and exactly
      ONE anchor fact is constructed;
    - one below it the operation is refused atomically with the
      EXACT prior region composition origin and ZERO published root
      facts; the crossing reservation falls AFTER the anchor fact
      construction (the fact object is constructed but never
      retained -- the constructor counter separates that from a
      preconstruction refusal);
    - the ACTUAL preconstruction boundary (the highest cap at which
      the refusal precedes ANY root-fact construction, counter 0) is
      located by a second measured search and pinned at both edges
      (zero constructions below/at it, one constructed-then-refused
      above it)."""

    counts = {"n": 0}
    orig_init = RootRegionLineageFact.__init__

    def counting_init(self: Any, *args: Any, **kwargs: Any) -> None:
        counts["n"] += 1
        orig_init(self, *args, **kwargs)

    # Class identity is preserved (the kernel does isinstance against
    # the real class); only the constructor is instrumented.
    monkeypatch.setattr(RootRegionLineageFact, "__init__", counting_init)

    def accepted(m: AdmissionMode, tag: str, n: int, cap: int) -> bool:
        ns = r_ns(
            m, f"p-fb-{m.value}-{tag}-{n}", bounds=RootLineageBounds(max_total_work_units=cap)
        )
        return bootstrap_root_region_lineage((root_request(),), ns).outcome is (
            RootLineageOutcome.ACCEPTED
        )

    def ctor_reached(m: AdmissionMode, tag: str, n: int, cap: int) -> bool:
        ns = r_ns(
            m, f"p-fb-{m.value}-{tag}-{n}", bounds=RootLineageBounds(max_total_work_units=cap)
        )
        before = counts["n"]
        t = bootstrap_root_region_lineage((root_request(),), ns)
        assert t.outcome in (
            RootLineageOutcome.ACCEPTED,
            RootLineageOutcome.REFUSED_OVER_BOUND,
        ), (t.outcome, t.diagnostics)
        if t.outcome is RootLineageOutcome.REFUSED_OVER_BOUND:
            assert t.diagnostics == (RootLineageLimitation.WORK_UNITS_OVER_BOUND,)
        return counts["n"] - before >= 1

    cap = _min_accepted_cap(mode, f"{endpoint}-boot", accepted)
    ns = r_ns(
        mode, f"p-fb-{mode.value}-{endpoint}-at", bounds=RootLineageBounds(max_total_work_units=cap)
    )
    base = counts["n"]
    t = bootstrap_root_region_lineage((root_request(),), ns)
    assert t.outcome is RootLineageOutcome.ACCEPTED, (t.outcome, t.diagnostics)
    assert len(t.state.root_facts) == 1
    assert t.new_root_facts == (t.state.root_facts[0],)
    assert counts["n"] == base + 1  # exactly the ONE anchor fact
    assert validate_root_region_lineage_state(t.state, ns.root_lineage_bounds) is None
    # One below the full minimum: atomic refusal, exact prior origin,
    # zero PUBLISHED facts; the crossing reservation is measured, not
    # assumed.
    ns1 = r_ns(
        mode,
        f"p-fb-{mode.value}-{endpoint}-below",
        bounds=RootLineageBounds(max_total_work_units=cap - 1),
    )
    before1 = counts["n"]
    t1 = bootstrap_root_region_lineage((root_request(),), ns1)
    assert t1.outcome is RootLineageOutcome.REFUSED_OVER_BOUND
    assert t1.diagnostics == (RootLineageLimitation.WORK_UNITS_OVER_BOUND,)
    assert t1.new_root_facts == ()
    assert t1.revision_before == 0
    assert t1.revision_after == 0
    assert t1.state.revision == 0
    assert t1.state.root_facts == ()
    assert t1.state.d_state.revision == 0
    assert t1.state.d_state.root is None
    assert t1.d_transition is not None
    assert t1.d_transition.outcome is CausalHistoryOutcome.ACCEPTED
    assert t1.d_revision_before == 0
    assert t1.d_revision_after == 1
    delta1 = counts["n"] - before1
    # The ACTUAL preconstruction boundary: the highest cap whose
    # refusal precedes ANY root-fact construction.
    cap_ctor = _min_accepted_cap(mode, f"{endpoint}-bootctor", ctor_reached)
    assert cap_ctor <= cap
    ns_pre = r_ns(
        mode,
        f"p-fb-{mode.value}-{endpoint}-pre",
        bounds=RootLineageBounds(max_total_work_units=cap_ctor - 1),
    )
    before_pre = counts["n"]
    t_pre = bootstrap_root_region_lineage((root_request(),), ns_pre)
    assert t_pre.outcome is RootLineageOutcome.REFUSED_OVER_BOUND
    assert t_pre.diagnostics == (RootLineageLimitation.WORK_UNITS_OVER_BOUND,)
    assert counts["n"] == before_pre  # ZERO constructions
    assert t_pre.new_root_facts == ()
    assert t_pre.state.revision == 0
    assert t_pre.state.root_facts == ()
    assert t_pre.state.d_state.revision == 0
    # One above the preconstruction boundary the anchor fact IS
    # constructed before the later refusal (still unpublished).
    ns_c = r_ns(
        mode,
        f"p-fb-{mode.value}-{endpoint}-ctor",
        bounds=RootLineageBounds(max_total_work_units=cap_ctor),
    )
    before_c = counts["n"]
    t_c = bootstrap_root_region_lineage((root_request(),), ns_c)
    assert counts["n"] - before_c == 1  # exactly the anchor fact
    assert t_c.new_root_facts == ()
    assert t_c.state.revision == 0
    assert t_c.state.root_facts == ()
    assert t_c.state.d_state.revision == 0
    if t_c.outcome is RootLineageOutcome.ACCEPTED:
        assert cap_ctor == cap  # the ctor-entry cap is the full minimum
    else:
        assert t_c.outcome is RootLineageOutcome.REFUSED_OVER_BOUND
        assert t_c.diagnostics == (RootLineageLimitation.WORK_UNITS_OVER_BOUND,)
    # And the cap-1 delta is exactly what the measured boundary says:
    # the anchor was constructed iff cap-1 reached the ctor boundary.
    assert delta1 == (1 if cap - 1 >= cap_ctor else 0)


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_f_bootstrap_fact_count_at_limit_first_over(
    mode: AdmissionMode, endpoint: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The retained root-fact count at the NEW bootstrap, covering
    BOTH read provenance kinds: at the cap the batch (anchor + one
    same-source whole-singleton read + one same-source mixed read)
    is accepted with EXACTLY one construction per retained fact and
    per provenance; the retained READ facts are unproven (the
    bootstrap anchor is authoritative); the FIRST-OVER candidate is
    refused with the exact domain reason BEFORE its provenance OR
    fact materializes (MEASURED: the crossing candidate allocates
    neither), the region origin is preserved exactly, and the
    ACTUAL accepted D candidate is carried only as explicitly
    discarded transition evidence."""

    counts = {"fact": 0, "envelope": 0, "read": 0, "region": 0}
    orig_fact_init = RootRegionLineageFact.__init__
    orig_envelope_init = EnvelopeRootProvenance.__init__
    orig_read_init = ReadRootProvenance.__init__
    orig_region_init = RootRegionReadProvenance.__init__

    def counting_fact_init(self: Any, *args: Any, **kwargs: Any) -> None:
        counts["fact"] += 1
        orig_fact_init(self, *args, **kwargs)

    def counting_envelope_init(self: Any, *args: Any, **kwargs: Any) -> None:
        counts["envelope"] += 1
        orig_envelope_init(self, *args, **kwargs)

    def counting_read_init(self: Any, *args: Any, **kwargs: Any) -> None:
        counts["read"] += 1
        orig_read_init(self, *args, **kwargs)

    def counting_region_init(self: Any, *args: Any, **kwargs: Any) -> None:
        counts["region"] += 1
        orig_region_init(self, *args, **kwargs)

    # The class identities are preserved (the module aliases stay the
    # ORIGINAL classes; the kernel does isinstance against them);
    # only the constructors are instrumented and restored.
    monkeypatch.setattr(RootRegionLineageFact, "__init__", counting_fact_init)
    monkeypatch.setattr(EnvelopeRootProvenance, "__init__", counting_envelope_init)
    monkeypatch.setattr(ReadRootProvenance, "__init__", counting_read_init)
    monkeypatch.setattr(RootRegionReadProvenance, "__init__", counting_region_init)
    bounds = RootLineageBounds(max_root_facts=3)
    mixed_body = _mixed_body(A_TEXT, MARK, ROOT_TEXT)
    ns_at = r_ns(mode, f"p-fbc-{mode.value}-{endpoint}-at", bounds=bounds)
    base = dict(counts)
    t_at = bootstrap_root_region_lineage(
        (
            root_request(),
            read_request(endpoint, "bx", ROOT_TEXT, "cat AGENTS.md"),
            read_request(endpoint, "mx", mixed_body, MIX_CMD),
        ),
        ns_at,
    )
    assert t_at.outcome is RootLineageOutcome.ACCEPTED, (t_at.outcome, t_at.diagnostics)
    assert len(t_at.state.root_facts) == 3
    assert counts["fact"] == base["fact"] + 3  # anchor + both accepted reads
    assert counts["envelope"] == base["envelope"] + 1  # the anchor only
    assert counts["read"] == base["read"] + 1  # the singleton read only
    assert counts["region"] == base["region"] + 1  # the mixed read only
    for fact in t_at.state.root_facts:
        if fact.provenance.kind in ("read", "read_region"):
            assert fact.issued is False
            assert fact.authority is False
    anchor_fact = next(f for f in t_at.state.root_facts if f.provenance.kind == "envelope")
    assert anchor_fact.issued is False
    assert anchor_fact.authority is True
    assert validate_root_region_lineage_state(t_at.state, ns_at.root_lineage_bounds) is None
    ns_over = r_ns(mode, f"p-fbc-{mode.value}-{endpoint}-over", bounds=bounds)
    before = dict(counts)
    t_over = bootstrap_root_region_lineage(
        (
            root_request(),
            read_request(endpoint, "bx", ROOT_TEXT, "cat AGENTS.md"),
            read_request(endpoint, "mx", mixed_body, MIX_CMD),
            read_request(endpoint, "bz", ROOT_TEXT, "cat AGENTS.md"),
        ),
        ns_over,
    )
    assert t_over.outcome is RootLineageOutcome.REFUSED_OVER_BOUND
    assert t_over.diagnostics == (RootLineageLimitation.ROOT_FACTS_OVER_BOUND,)
    assert t_over.new_root_facts == ()
    assert t_over.state.revision == 0
    assert t_over.state.root_facts == ()
    assert t_over.state.d_state.revision == 0
    assert t_over.state.d_state.root is None
    # The crossing candidate materialized NOTHING: exactly the
    # anchor plus the two pre-crossing reads were constructed (four
    # fact / four provenance constructions would include the
    # crossing candidate).
    assert counts["fact"] == before["fact"] + 3
    assert counts["envelope"] == before["envelope"] + 1
    assert counts["read"] == before["read"] + 1  # bx only, not the crossing bz
    assert counts["region"] == before["region"] + 1  # mx only
    # The ACTUAL accepted D candidate is carried as explicitly
    # discarded transition evidence (the region state is untouched).
    assert t_over.d_transition is not None
    assert t_over.d_transition.outcome is CausalHistoryOutcome.ACCEPTED
    assert t_over.d_revision_before == 0
    assert t_over.d_revision_after == 1


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_f_bootstrap_source_bytes_at_limit_first_over(
    mode: AdmissionMode, endpoint: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The logical root-source byte cap at the NEW bootstrap counts
    ACTUAL exact UTF-8 root-MEMBER bytes, never the mixed aggregate
    (which stays D/B-owned): the mixed case uses an aggregate
    STRICTLY LARGER than the cap while the anchor + root member fit
    it exactly, across BOTH whole-singleton (read) and mixed
    (read_region) provenance kinds.  At the cap the batch is
    accepted; the FIRST-OVER read is refused with the exact domain
    reason BEFORE its provenance OR fact materializes (MEASURED:
    zero constructions for the crossing candidate), the region
    origin is preserved exactly, and the accepted D candidate is
    carried only as explicitly discarded transition evidence."""

    counts = {"fact": 0, "envelope": 0, "read": 0, "region": 0}
    orig_fact_init = RootRegionLineageFact.__init__
    orig_envelope_init = EnvelopeRootProvenance.__init__
    orig_read_init = ReadRootProvenance.__init__
    orig_region_init = RootRegionReadProvenance.__init__

    def counting_fact_init(self: Any, *args: Any, **kwargs: Any) -> None:
        counts["fact"] += 1
        orig_fact_init(self, *args, **kwargs)

    def counting_envelope_init(self: Any, *args: Any, **kwargs: Any) -> None:
        counts["envelope"] += 1
        orig_envelope_init(self, *args, **kwargs)

    def counting_read_init(self: Any, *args: Any, **kwargs: Any) -> None:
        counts["read"] += 1
        orig_read_init(self, *args, **kwargs)

    def counting_region_init(self: Any, *args: Any, **kwargs: Any) -> None:
        counts["region"] += 1
        orig_region_init(self, *args, **kwargs)

    # The class identities are preserved (the module aliases stay the
    # ORIGINAL classes; the kernel does isinstance against them);
    # only the constructors are instrumented and restored.
    monkeypatch.setattr(RootRegionLineageFact, "__init__", counting_fact_init)
    monkeypatch.setattr(EnvelopeRootProvenance, "__init__", counting_envelope_init)
    monkeypatch.setattr(ReadRootProvenance, "__init__", counting_read_init)
    monkeypatch.setattr(RootRegionReadProvenance, "__init__", counting_region_init)
    root_bytes = len(ROOT_TEXT.encode("utf-8"))
    cap = 2 * root_bytes
    bounds = RootLineageBounds(max_retained_root_source_bytes=cap)
    # The nonroot member is sized so the retained mixed AGGREGATE
    # (the sum of the retained member bytes; the marker echo is not
    # retained source) is strictly LARGER than the stricter H
    # logical-root cap by design, while the root member itself (==
    # the anchor bytes) fits it.
    big_a = A_TEXT + "x" * (root_bytes - len(A_TEXT) + 1)
    assert len(big_a.encode("utf-8")) == root_bytes + 1
    mixed_body = _mixed_body(big_a, MARK, ROOT_TEXT)
    shapes = {
        "singleton": (
            read_request(endpoint, "bx", ROOT_TEXT, "cat AGENTS.md"),
            read_request(endpoint, "by", ROOT_TEXT, "cat AGENTS.md"),
            "read",
        ),
        "mixed": (
            read_request(endpoint, "mx", mixed_body, MIX_CMD),
            read_request(endpoint, "mx2", mixed_body, MIX_CMD),
            "region",
        ),
    }
    for shape, (first_read, second_read, prov_kind) in shapes.items():
        ns_at = r_ns(mode, f"p-fbb-{mode.value}-{endpoint}-{shape}-at", bounds=bounds)
        base = dict(counts)
        t_at = bootstrap_root_region_lineage(
            (root_request(), first_read),
            ns_at,
        )
        assert t_at.outcome is RootLineageOutcome.ACCEPTED, (shape, t_at.outcome, t_at.diagnostics)
        assert len(t_at.state.root_facts) == 2
        assert sum(f.source_byte_length for f in t_at.state.root_facts) == cap
        assert counts["fact"] == base["fact"] + 2  # anchor + exactly the one read
        assert counts["envelope"] == base["envelope"] + 1
        assert counts["read"] == base["read"] + (1 if prov_kind == "read" else 0)
        assert counts["region"] == base["region"] + (1 if prov_kind == "region" else 0)
        assert validate_root_region_lineage_state(t_at.state, ns_at.root_lineage_bounds) is None
        if prov_kind == "region":
            # The mixed AGGREGATE exceeds the cap: it is D/B-owned
            # and never the logical root-body size.
            mixed_occ = next(o for o in t_at.state.d_state.occurrences if o.call_id == "mx")
            assert mixed_occ.proof.source_byte_length > cap
            region_fact = next(
                f for f in t_at.state.root_facts if f.provenance.kind == "read_region"
            )
            assert region_fact.source_byte_length == root_bytes
            assert region_fact.issued is False
            assert region_fact.authority is False
        ns_over = r_ns(mode, f"p-fbb-{mode.value}-{endpoint}-{shape}-over", bounds=bounds)
        before = dict(counts)
        t_over = bootstrap_root_region_lineage(
            (root_request(), first_read, second_read),
            ns_over,
        )
        assert t_over.outcome is RootLineageOutcome.REFUSED_OVER_BOUND
        assert t_over.diagnostics == (RootLineageLimitation.ROOT_SOURCE_BYTES_OVER_BOUND,)
        assert t_over.new_root_facts == ()
        assert t_over.state.revision == 0
        assert t_over.state.root_facts == ()
        assert t_over.state.d_state.revision == 0
        assert t_over.state.d_state.root is None
        # The crossing candidate materialized NOTHING: exactly the
        # anchor plus the one pre-crossing read were constructed
        # (three fact / three provenance constructions would include
        # the crossing candidate).
        assert counts["fact"] == before["fact"] + 2
        assert counts["envelope"] == before["envelope"] + 1
        assert counts["read"] == before["read"] + (1 if prov_kind == "read" else 0)
        assert counts["region"] == before["region"] + (1 if prov_kind == "region" else 0)
        # The ACTUAL accepted D candidate is carried as explicitly
        # discarded transition evidence (the region state is
        # untouched).
        assert t_over.d_transition is not None
        assert t_over.d_transition.outcome is CausalHistoryOutcome.ACCEPTED
        assert t_over.d_revision_before == 0
        assert t_over.d_revision_after == 1


# --- F (continued). Independent inherited domains and precharge --------


@pytest.mark.parametrize("mode", MODES)
def test_f_total_work_units_domains_p(mode: AdmissionMode) -> None:
    """The ONE shared P outer work domain and the INDEPENDENT D-local
    per-transition work domain, measured fresh at runtime (never
    hardcoded) on the NEW surface: the minimal accepted P bootstrap
    cap and the minimal accepted P bootstrap+issue+mixed-read cap;
    cap-minus-1 refuses with the exact domain reason and EXACT prior
    state; a genuinely smaller D-local cap at exactly its measured
    cost still accepts the whole sequence beneath the unchanged H
    outer (a global-min / shared-budget implementation cannot pass),
    and the D cap one below its own cost first-overs in the D domain
    with the exact mapped reason while the P cap stays unchanged;
    the select bounds override and the non-model bounds refusal are
    exact."""

    def boot_probe(m: AdmissionMode, tag: str, i: int, cap: int) -> bool:
        ns = r_ns(m, f"{tag}-b{i}", bounds=RootLineageBounds(max_total_work_units=cap))
        return bootstrap_root_region_lineage((root_request(),), ns).outcome is (
            RootLineageOutcome.ACCEPTED
        )

    def seq_probe(m: AdmissionMode, tag: str, i: int, cap: int) -> bool:
        ns = r_ns(m, f"{tag}-s{i}", bounds=RootLineageBounds(max_total_work_units=cap))
        t0 = bootstrap_root_region_lineage((root_request(),), ns)
        if t0.outcome is not RootLineageOutcome.ACCEPTED:
            return False
        t1 = r_issue(t0.state, ns, "w1", "responses", (CAUSAL_ROOT_FACT,), MIX_CMD)
        if t1.outcome is not RootLineageOutcome.ACCEPTED:
            return False
        t2 = r_observe(
            t1.state,
            ns,
            (read_request("responses", "w1", _mixed_body(A_TEXT, MARK, V2), MIX_CMD),),
        )
        return t2.outcome is RootLineageOutcome.ACCEPTED

    def dseq_probe(m: AdmissionMode, tag: str, i: int, cap: int) -> bool:
        """The same P sequence with the D LOCAL per-transition cap
        varied (the P outer stays at its default ceiling)."""
        ns = r_ns(m, f"{tag}-d{i}", history_bounds=HistoryBounds(max_work_units=cap))
        t0 = bootstrap_root_region_lineage((root_request(),), ns)
        if t0.outcome is not RootLineageOutcome.ACCEPTED:
            return False
        t1 = r_issue(t0.state, ns, "w1", "responses", (CAUSAL_ROOT_FACT,), MIX_CMD)
        if t1.outcome is not RootLineageOutcome.ACCEPTED:
            return False
        t2 = r_observe(
            t1.state,
            ns,
            (read_request("responses", "w1", _mixed_body(A_TEXT, MARK, V2), MIX_CMD),),
        )
        return t2.outcome is RootLineageOutcome.ACCEPTED

    w_boot = _min_accepted_cap(mode, "pw-b", boot_probe)
    w_seq = _min_accepted_cap(mode, "pw-s", seq_probe)
    # The D-local cap has its own (lower) hard ceiling: search under it.
    w_d_seq = _min_accepted_cap(mode, "pw-d", dseq_probe, hi=65536)
    assert w_seq > w_boot  # the sequence costs strictly more outer work
    # The D-local per-transition cost of the same sequence is genuinely
    # SMALLER than the P outer cost (measured, source/fixture
    # dependent, never hardcoded), so the independent-domain positive
    # is not vacuous.
    assert w_d_seq < w_seq
    # INDEPENDENT-DOMAIN POSITIVE: the P outer at exactly its measured
    # cost and the D-local cap at exactly its (smaller) measured cost
    # both accept the full sequence.
    ns_x = r_ns(
        mode,
        "pw-x",
        bounds=RootLineageBounds(max_total_work_units=w_seq),
        history_bounds=HistoryBounds(max_work_units=w_d_seq),
    )
    x0 = bootstrap_root_region_lineage((root_request(),), ns_x)
    assert x0.outcome is RootLineageOutcome.ACCEPTED
    x1 = r_issue(x0.state, ns_x, "w1", "responses", (CAUSAL_ROOT_FACT,), MIX_CMD)
    assert x1.outcome is RootLineageOutcome.ACCEPTED
    x2 = r_observe(
        x1.state,
        ns_x,
        (read_request("responses", "w1", _mixed_body(A_TEXT, MARK, V2), MIX_CMD),),
    )
    assert x2.outcome is RootLineageOutcome.ACCEPTED
    # ACTUAL D FIRST-OVER beneath the shared P outer: the D-local cap
    # one below its own cost refuses in the D domain with the exact
    # mapped reason while the P cap stays unchanged.
    ns_y = r_ns(
        mode,
        "pw-y",
        bounds=RootLineageBounds(max_total_work_units=w_seq),
        history_bounds=HistoryBounds(max_work_units=w_d_seq - 1),
    )
    y0 = bootstrap_root_region_lineage((root_request(),), ns_y)
    assert y0.outcome is RootLineageOutcome.ACCEPTED
    y1 = r_issue(y0.state, ns_y, "w1", "responses", (CAUSAL_ROOT_FACT,), MIX_CMD)
    assert y1.outcome is RootLineageOutcome.ACCEPTED
    y2 = r_observe(
        y1.state,
        ns_y,
        (read_request("responses", "w1", _mixed_body(A_TEXT, MARK, V2), MIX_CMD),),
    )
    assert_refused(
        y2,
        y1.state,
        RootLineageOutcome.REFUSED_OVER_BOUND,
        (RootLineageLimitation.WORK_UNITS_OVER_BOUND,),
    )
    assert y2.d_transition is not None
    assert y2.d_transition.outcome is CausalHistoryOutcome.REFUSED_OVER_BOUND
    # cap - 1 on the bootstrap: exact domain refusal, nothing retained.
    ns_b = r_ns(mode, "pw-b1", bounds=RootLineageBounds(max_total_work_units=w_boot - 1))
    r_b = bootstrap_root_region_lineage((root_request(),), ns_b)
    assert r_b.outcome is RootLineageOutcome.REFUSED_OVER_BOUND
    assert r_b.diagnostics == (RootLineageLimitation.WORK_UNITS_OVER_BOUND,)
    assert r_b.new_root_facts == ()
    assert r_b.state.revision == 0
    assert r_b.state.root_facts == ()
    # cap - 1 on the sequence: boot+issue legal, the mixed read
    # first-overs with the EXACT prior state preserved.
    ns_s = r_ns(mode, "pw-s1", bounds=RootLineageBounds(max_total_work_units=w_seq - 1))
    s0 = bootstrap_root_region_lineage((root_request(),), ns_s).state
    s1 = r_issue(s0, ns_s, "w1", "responses", (CAUSAL_ROOT_FACT,), MIX_CMD).state
    r_s = r_observe(
        s1,
        ns_s,
        (read_request("responses", "w1", _mixed_body(A_TEXT, MARK, V2), MIX_CMD),),
    )
    assert_refused(
        r_s,
        s1,
        RootLineageOutcome.REFUSED_OVER_BOUND,
        (RootLineageLimitation.WORK_UNITS_OVER_BOUND,),
    )
    # Select-side bounds overrides on a default-bounds P state.
    ns, s0 = r_bootstrap(mode, "pw-sel")
    t1 = r_issue(s0, ns, "ws2", "responses", (CAUSAL_ROOT_FACT,), MIX_CMD)
    t2 = r_observe(
        t1.state,
        ns,
        (read_request("responses", "ws2", _mixed_body(A_TEXT, MARK, V2), MIX_CMD),),
    )
    s2 = t2.state
    q1 = select_current_root_region(s2, ns, bounds=RootLineageBounds(max_total_work_units=1))
    assert q1.outcome is RootSelectionOutcome.REFUSED
    assert q1.limitations == (RootLineageLimitation.WORK_UNITS_OVER_BOUND,)
    q2 = select_current_root_region(s2, ns, bounds="x")  # type: ignore[arg-type]
    # ^ intentional non-model bounds refusal (constructor-level probe)
    assert q2.outcome is RootSelectionOutcome.REFUSED
    assert q2.limitations == (RootLineageLimitation.MALFORMED_BINDING,)


def test_f_diagnostics_ceiling_and_bounds_shape_p() -> None:
    """CONSTRUCTOR-ONLY model law on the NEW transition record, exact
    scope: the public API always emits a bounded, sorted,
    deduplicated closed-enum diagnostic tuple, and the closed enum
    has FEWER than 64 members, so the raw 64 ceiling is structurally
    unreachable by any public result (proven here, not fabricated; no
    public first-over is constructed).  The hard 64 ceiling is
    prefetched BEFORE any element is validated -- the before-element
    sentinel proves a 65-tuple of non-members fails with exactly the
    field-level ceiling error and no element-level error, while a
    length-lawful 64-tuple with one non-member is then validated
    element-by-element at the exact index; sorted/dedup order is
    enforced; the bounds' max_diagnostics shape law is exact."""
    ns, s0 = r_bootstrap(MODES[0], "p-f-diag")
    t = observe_root_region_lineage(s0, ns, s0.revision, (root_request(),))
    assert t.outcome is RootLineageOutcome.REPLAYED

    def with_diags(diags: Any) -> Any:
        return RootRegionLineageTransition(
            state=t.state,
            outcome=t.outcome,
            diagnostics=diags,
            d_transition=t.d_transition,
            revision_before=t.revision_before,
            revision_after=t.revision_after,
            d_revision_before=t.d_revision_before,
            d_revision_after=t.d_revision_after,
            new_root_facts=(),
        )

    all_members = tuple(sorted(RootLineageLimitation, key=lambda m: m.value))
    assert len(all_members) < 64  # raw ceiling structurally unreachable
    # The ceiling preflight fires before a single element validates.
    with pytest.raises(ValidationError):
        with_diags((all_members[0],) * 65)
    # BEFORE-ELEMENT sentinel: a 65-tuple whose elements are all
    # non-members still fails with EXACTLY the field-level ceiling
    # error and no element-level error -- had element iteration run
    # first, the closed-enum validation would report index 0.
    with pytest.raises(ValidationError) as over_exc:
        with_diags(("not-a-limitation",) * 65)
    over_errs = over_exc.value.errors()
    assert len(over_errs) == 1
    assert over_errs[0]["loc"] == ("diagnostics",)
    # ...and a length-LAWFUL 64-tuple with one non-member element is
    # validated element-by-element AFTER the ceiling preflight, at the
    # exact index.
    with pytest.raises(ValidationError) as elem_exc:
        with_diags(all_members + all_members[:8] + ("not-a-limitation",))
    elem_errs = elem_exc.value.errors()
    assert len(elem_errs) == 1
    assert elem_errs[0]["loc"] == ("diagnostics", 63)
    # The dedup law.
    with pytest.raises(ValidationError):
        with_diags((all_members[0], all_members[0]))
    # The order law.
    with pytest.raises(ValidationError):
        with_diags((all_members[1], all_members[0]))
    # The full closed enum, sorted and deduplicated, is coherent.
    ok = with_diags(all_members)
    assert ok.diagnostics == all_members
    # The bounds shape law.
    with pytest.raises(ValidationError):
        RootLineageBounds(max_diagnostics=0)
    with pytest.raises(ValidationError):
        RootLineageBounds(max_diagnostics=65)
    assert RootLineageBounds(max_diagnostics=64).max_diagnostics == 64


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_f_batch_requests_bound_preserved_p(mode: AdmissionMode, endpoint: str) -> None:
    """The ORIGINAL per-batch request limit is preserved under the
    NEW operations: successive batches AT the bound are each legal --
    two accepted 2-request batches retain 4 historical reads, MORE
    than the bound of 2, so an accidental CUMULATIVE max_requests=2
    implementation cannot pass -- and the 3-request batch crossing
    it is refused with the exact mapped domain reason, EXACT prior
    state."""
    ns, s0 = r_bootstrap(mode, f"p-f-batch-{endpoint}", graph_bounds=GraphBounds(max_requests=2))
    t1 = r_observe(
        s0,
        ns,
        (
            read_request(endpoint, "b1", A_TEXT, "cat A.md"),
            read_request(endpoint, "b2", B_TEXT, "cat B.md"),
        ),
    )
    assert t1.outcome is RootLineageOutcome.ACCEPTED
    s1 = t1.state
    # Second legal batch AT the bound: the cumulative retained reads
    # (4) now EXCEED the per-batch bound (2) -- per-batch domain
    # proven.
    t2 = r_observe(
        s1,
        ns,
        (
            read_request(endpoint, "c1", A_TEXT, "cat A.md"),
            read_request(endpoint, "c2", B_TEXT, "cat B.md"),
        ),
    )
    assert t2.outcome is RootLineageOutcome.ACCEPTED
    s2 = t2.state
    assert len(s2.d_state.occurrences) == 4
    # The crossing batch refuses with the exact prior state.
    t3 = r_observe(
        s2,
        ns,
        (
            read_request(endpoint, "d1", A_TEXT, "cat A.md"),
            read_request(endpoint, "d2", B_TEXT, "cat B.md"),
            read_request(endpoint, "d3", A_TEXT, "cat A.md"),
        ),
    )
    assert_refused(
        t3,
        s2,
        RootLineageOutcome.REFUSED_OVER_BOUND,
        (RootLineageLimitation.BATCH_OVER_BOUND,),
    )


# --- G. Direct validate_root_region_lineage_state matrix ----------------


def _g_setup(mode: AdmissionMode, endpoint: str) -> tuple[Any, Any]:
    """Bootstrap + a genuinely issued region (v2) + one nonroot read;
    returns (ns, state) with region fact 'm1' and nonroot occurrence
    'n1', earned on the GIVEN actual endpoint/admission mode (the
    public-operation forgeries must be exercised across BOTH)."""
    ns, s0 = r_bootstrap(mode, "p-g")
    t1 = r_issue(s0, ns, "m1", endpoint, (CAUSAL_ROOT_FACT,), MIX_CMD)
    assert t1.outcome is RootLineageOutcome.ACCEPTED
    t2 = r_observe(
        t1.state, ns, (read_request(endpoint, "m1", _mixed_body(A_TEXT, MARK, V2), MIX_CMD),)
    )
    assert t2.outcome is RootLineageOutcome.ACCEPTED, (t2.outcome, t2.diagnostics)
    t3 = r_observe(t2.state, ns, (read_request(endpoint, "n1", A_TEXT, "cat A.md"),))
    assert t3.outcome is RootLineageOutcome.ACCEPTED, (t3.outcome, t3.diagnostics)
    return ns, t3.state


def _g_swap(state: Any, fact: Any, replacement: Any) -> Any:
    return state.model_copy(
        update={"root_facts": tuple(f if f is not fact else replacement for f in state.root_facts)}
    )


def test_g_forged_kind_tag_malformed() -> None:
    """A forged provenance whose concrete class disagrees with its
    kind tag is refused by the class-first fence (never a
    dereference of an absent field)."""
    ns, s = _g_setup(MODES[0], ENDPOINTS[0])
    m1 = region_fact(s, "m1")
    forged_p = EnvelopeRootProvenance.model_construct(
        kind="read",
        root_digest=m1.source_digest,
        workspace=WORKSPACE,
        source_byte_length=m1.source_byte_length,
    )
    forged = RootRegionLineageFact.model_construct(
        source_digest=m1.source_digest,
        source_byte_length=m1.source_byte_length,
        provenance=forged_p,
        issued=True,
        authority=True,
    )
    bad = _g_swap(s, m1, forged)
    assert (
        validate_root_region_lineage_state(bad, ns.root_lineage_bounds)
        is RootLineageLimitation.MALFORMED_BINDING
    )


def test_g_stored_flags_never_trusted() -> None:
    """Stored flag bits that disagree with the flags DERIVED from the
    actual D state are refused (the stored bits are never trusted)."""
    ns, s = _g_setup(MODES[0], ENDPOINTS[0])
    m1 = region_fact(s, "m1")
    bad = _g_swap(s, m1, m1.model_copy(update={"issued": False}))
    assert (
        validate_root_region_lineage_state(bad, ns.root_lineage_bounds)
        is RootLineageLimitation.MALFORMED_BINDING
    )


def test_g_detached_occurrence_malformed() -> None:
    """A region fact whose occurrence is not the ACTUAL retained
    occurrence is a detached incoherent binding."""
    ns, s = _g_setup(MODES[0], ENDPOINTS[0])
    m1 = region_fact(s, "m1")
    bad_p = m1.provenance.model_copy(update={"occurrence_id": "f" * 64})
    bad = _g_swap(s, m1, m1.model_copy(update={"provenance": bad_p}))
    assert (
        validate_root_region_lineage_state(bad, ns.root_lineage_bounds)
        is RootLineageLimitation.MALFORMED_BINDING
    )


def test_g_coherent_rekey_refused() -> None:
    """A coherently rekeyed region (fact source AND provenance member
    binding swapped together) is still refused: the join is against
    the ACTUAL retained proof segment, never against the fact's own
    words."""
    ns, s = _g_setup(MODES[0], ENDPOINTS[0])
    m1 = region_fact(s, "m1")
    a_digest = sha256_hex(A_TEXT)
    a_len = len(A_TEXT.encode("utf-8"))
    bad_p = m1.provenance.model_copy(
        update={"root_member_digest": a_digest, "root_member_byte_length": a_len}
    )
    bad = _g_swap(
        s,
        m1,
        m1.model_copy(
            update={"provenance": bad_p, "source_digest": a_digest, "source_byte_length": a_len}
        ),
    )
    assert (
        validate_root_region_lineage_state(bad, ns.root_lineage_bounds)
        is RootLineageLimitation.MALFORMED_BINDING
    )


def test_g_segment_index_swap_malformed() -> None:
    """Pointing the region at the NONROOT segment index breaks the
    actual segment/member join."""
    ns, s = _g_setup(MODES[0], ENDPOINTS[0])
    m1 = region_fact(s, "m1")
    bad_p = m1.provenance.model_copy(update={"root_segment_index": 0})
    bad = _g_swap(s, m1, m1.model_copy(update={"provenance": bad_p}))
    assert (
        validate_root_region_lineage_state(bad, ns.root_lineage_bounds)
        is RootLineageLimitation.MALFORMED_BINDING
    )


def test_g_inventory_gap_malformed() -> None:
    """Dropping an earned region fact (the occurrence is retained) is
    an inventory gap: an omitted earned fact is an incoherent binding,
    never a silent rollback."""
    ns, s = _g_setup(MODES[0], ENDPOINTS[0])
    m1 = region_fact(s, "m1")
    bad = s.model_copy(update={"root_facts": tuple(f for f in s.root_facts if f is not m1)})
    assert (
        validate_root_region_lineage_state(bad, ns.root_lineage_bounds)
        is RootLineageLimitation.MALFORMED_BINDING
    )


def test_g_phantom_region_fact_malformed() -> None:
    """A region fact for a NON-ELIGIBLE (rootless) occurrence is an
    extra phantom in the complete 1:1 fact inventory."""
    ns, s = _g_setup(MODES[0], ENDPOINTS[0])
    n1 = next(o for o in s.d_state.occurrences if o.call_id == "n1")
    seg = n1.proof.segments[0]
    phantom_p = RootRegionReadProvenance.model_construct(
        occurrence_id=n1.occurrence_id,
        call_id="n1",
        endpoint=ENDPOINTS[0],
        whole_proof_digest=n1.proof.source_digest,
        whole_proof_byte_length=n1.proof.source_byte_length,
        root_segment_index=0,
        root_member_position=0,
        root_member_digest=seg.member_digest,
        root_member_byte_length=seg.byte_length,
    )
    phantom = RootRegionLineageFact.model_construct(
        source_digest=seg.member_digest,
        source_byte_length=seg.byte_length,
        provenance=phantom_p,
        issued=False,
        authority=False,
    )
    bad = s.model_copy(update={"root_facts": s.root_facts + (phantom,)})
    assert (
        validate_root_region_lineage_state(bad, ns.root_lineage_bounds)
        is RootLineageLimitation.MALFORMED_BINDING
    )


def test_g_unsorted_facts_malformed() -> None:
    """Root facts out of provenance-key order are refused."""
    ns, s = _g_setup(MODES[0], ENDPOINTS[0])
    bad = s.model_copy(update={"root_facts": s.root_facts[::-1]})
    assert (
        validate_root_region_lineage_state(bad, ns.root_lineage_bounds)
        is RootLineageLimitation.MALFORMED_BINDING
    )


def test_g_revision_mismatch_malformed() -> None:
    """A region revision out of 1:1 with the wrapped D revision is
    refused."""
    ns, s = _g_setup(MODES[0], ENDPOINTS[0])
    bad = s.model_copy(update={"revision": s.revision + 1})
    assert (
        validate_root_region_lineage_state(bad, ns.root_lineage_bounds)
        is RootLineageLimitation.MALFORMED_BINDING
    )


def test_g_bad_lineage_key_malformed() -> None:
    """A non-64-hex lineage key is refused at the shape law."""
    ns, s = _g_setup(MODES[0], ENDPOINTS[0])
    bad = s.model_copy(update={"lineage_key": "not-hex"})
    assert (
        validate_root_region_lineage_state(bad, ns.root_lineage_bounds)
        is RootLineageLimitation.MALFORMED_BINDING
    )


def test_g_fact_count_over_bound() -> None:
    """A stricter effective fact-count bound over all retained facts
    is enforced before any nested work."""
    ns, s = _g_setup(MODES[0], ENDPOINTS[0])
    bounds = RootLineageBounds(max_root_facts=1)
    assert (
        validate_root_region_lineage_state(s, bounds) is RootLineageLimitation.ROOT_FACTS_OVER_BOUND
    )


def test_g_source_bytes_over_bound() -> None:
    """A stricter effective logical root-source byte bound over all
    retained facts is enforced in the retention walk."""
    ns, s = _g_setup(MODES[0], ENDPOINTS[0])
    bounds = RootLineageBounds(max_retained_root_source_bytes=1)
    assert (
        validate_root_region_lineage_state(s, bounds)
        is RootLineageLimitation.ROOT_SOURCE_BYTES_OVER_BOUND
    )


# --- H. Selection-result constructor invariants -------------------------


def _h_setup() -> tuple[Any, Any, Any, Any]:
    """Bootstrap + an old whole-read witness and a NEW region witness
    with ONE equal source digest (v2), both authoritative."""
    mode, endpoint = MODES[0], ENDPOINTS[0]
    ns, s0 = r_bootstrap(mode, "p-h")
    t1 = r_issue(s0, ns, "s1", endpoint, (CAUSAL_ROOT_FACT,), "cat AGENTS.md")
    assert t1.outcome is RootLineageOutcome.ACCEPTED
    t2 = r_observe(t1.state, ns, (read_request(endpoint, "s1", V2, "cat AGENTS.md"),))
    assert t2.outcome is RootLineageOutcome.ACCEPTED
    t3 = r_issue(t2.state, ns, "m1", endpoint, (CAUSAL_ROOT_FACT,), MIX_CMD)
    assert t3.outcome is RootLineageOutcome.ACCEPTED
    t4 = r_observe(
        t3.state, ns, (read_request(endpoint, "m1", _mixed_body(A_TEXT, MARK, V2), MIX_CMD),)
    )
    assert t4.outcome is RootLineageOutcome.ACCEPTED, (t4.outcome, t4.diagnostics)
    s = t4.state
    return ns, s, p_read_fact(s, "s1"), region_fact(s, "m1")


def test_h_ok_witness_digest_mismatch() -> None:
    ns, s, _f_s1, f_m1 = _h_setup()
    with pytest.raises(ValidationError):
        RootRegionSelectionResult(
            outcome=RootSelectionOutcome.OK,
            selected_source_digest=sha256_hex(V3),
            witness_facts=(f_m1,),
            lineage_key=s.lineage_key,
            revision=s.revision,
        )


def test_h_ok_unissued_witness() -> None:
    ns, s, _f_s1, f_m1 = _h_setup()
    unissued = f_m1.model_copy(update={"issued": False, "authority": False})
    with pytest.raises(ValidationError):
        RootRegionSelectionResult(
            outcome=RootSelectionOutcome.OK,
            selected_source_digest=sha256_hex(V2),
            witness_facts=(unissued,),
            lineage_key=s.lineage_key,
            revision=s.revision,
        )


def test_h_witness_count_over_ceiling() -> None:
    ns, s, _f_s1, f_m1 = _h_setup()
    with pytest.raises(ValidationError):
        RootRegionSelectionResult(
            outcome=RootSelectionOutcome.OK,
            selected_source_digest=sha256_hex(V2),
            witness_facts=(f_m1,) * 1025,
            lineage_key=s.lineage_key,
            revision=s.revision,
        )


def test_h_limitations_over_ceiling() -> None:
    ns, s, _f_s1, f_m1 = _h_setup()
    with pytest.raises(ValidationError):
        RootRegionSelectionResult(
            outcome=RootSelectionOutcome.NO_SELECTED_ROOT,
            limitations=(RootLineageLimitation.ENVELOPE_UNPROVEN,) * 65,
            lineage_key=s.lineage_key,
            revision=s.revision,
        )


def test_h_duplicate_witness_keys() -> None:
    ns, s, _f_s1, f_m1 = _h_setup()
    with pytest.raises(ValidationError):
        RootRegionSelectionResult(
            outcome=RootSelectionOutcome.OK,
            selected_source_digest=sha256_hex(V2),
            witness_facts=(f_m1, f_m1),
            lineage_key=s.lineage_key,
            revision=s.revision,
        )


def test_h_ok_without_witnesses() -> None:
    ns, s, _f_s1, f_m1 = _h_setup()
    with pytest.raises(ValidationError):
        RootRegionSelectionResult(
            outcome=RootSelectionOutcome.OK,
            selected_source_digest=sha256_hex(V2),
            witness_facts=(),
            lineage_key=s.lineage_key,
            revision=s.revision,
        )


def test_h_conflict_single_witness() -> None:
    ns, s, _f_s1, f_m1 = _h_setup()
    with pytest.raises(ValidationError):
        RootRegionSelectionResult(
            outcome=RootSelectionOutcome.ROOT_CONTENT_CONFLICT,
            witness_facts=(f_m1,),
            lineage_key=s.lineage_key,
            revision=s.revision,
        )


def test_h_conflict_equal_digest_witnesses() -> None:
    ns, s, f_s1, f_m1 = _h_setup()
    assert f_s1.source_digest == f_m1.source_digest
    with pytest.raises(ValidationError):
        RootRegionSelectionResult(
            outcome=RootSelectionOutcome.ROOT_CONTENT_CONFLICT,
            witness_facts=(f_s1, f_m1),
            lineage_key=s.lineage_key,
            revision=s.revision,
        )


def test_h_non_ok_with_witnesses() -> None:
    ns, s, _f_s1, f_m1 = _h_setup()
    with pytest.raises(ValidationError):
        RootRegionSelectionResult(
            outcome=RootSelectionOutcome.NO_SELECTED_ROOT,
            witness_facts=(f_m1,),
            lineage_key=s.lineage_key,
            revision=s.revision,
        )


def test_h_refused_without_limitations() -> None:
    ns, s, _f_s1, f_m1 = _h_setup()
    with pytest.raises(ValidationError):
        RootRegionSelectionResult(
            outcome=RootSelectionOutcome.REFUSED,
            lineage_key=s.lineage_key,
            revision=s.revision,
        )


# --- I. Scope, version and CAS gates on the NEW public operations ------


def _root_item_ws(workspace: str, path: str = "AGENTS.md") -> dict[str, Any]:
    return {
        "role": "user",
        "content": [
            {
                "type": "input_text",
                "text": (
                    f"# {path} instructions for {workspace}\n\n"
                    f"<INSTRUCTIONS>\n{ROOT_TEXT}\n</INSTRUCTIONS>\n"
                ),
            }
        ],
    }


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_i_scope_cas_version_gates(mode: AdmissionMode, endpoint: str) -> None:
    """The fixed O(1) scope/CAS/version fences run FIRST on the NEW
    public operations, before any D work: a different lineage scope,
    a different D workspace scope, a wrong region contract version
    and a CAS mismatch each refuse with the exact closed outcome and
    the EXACT prior state."""
    ns, s0 = r_bootstrap(mode, "p-i-gate")
    t1 = r_issue(s0, ns, "m1", endpoint, (CAUSAL_ROOT_FACT,), MIX_CMD)
    assert t1.outcome is RootLineageOutcome.ACCEPTED
    t2 = r_observe(
        t1.state, ns, (read_request(endpoint, "m1", _mixed_body(A_TEXT, MARK, V2), MIX_CMD),)
    )
    assert t2.outcome is RootLineageOutcome.ACCEPTED, (t2.outcome, t2.diagnostics)
    s2 = t2.state
    probe = (read_request(endpoint, "x1", A_TEXT, "cat A.md"),)
    # (a) A different lineage scope (same D scope) is foreign.
    ns_other = r_ns(mode, "p-i-gate-other")
    t = r_observe(s2, ns_other, probe)
    assert_refused(t, s2, RootLineageOutcome.REFUSED_FOREIGN_SCOPE, ())
    assert t.d_transition is None
    # (b) A different D workspace scope is foreign.
    ns_ws = r_ns(mode, "p-i-gate", workspace="/work2")
    t = r_observe(s2, ns_ws, probe)
    assert_refused(t, s2, RootLineageOutcome.REFUSED_FOREIGN_SCOPE, ())
    assert t.d_transition is None
    # (c) Unsupported region versions are refused on ALL FOUR public
    # operations (observation, issuance, receipt and selection), with
    # the exact closed version limitation and no D work.
    v2 = "cache-root-region-lineage/v2"
    # (c1) A self-INCONSISTENT v2 namespace (contract_version v2 but
    # the stale v1-recomputed lineage key): the genuine state's own
    # key still matches the stale key, so the version-pair fence is
    # the one that catches the unsupported version.
    ns_badver = ns.model_copy(update={"contract_version": v2})
    assert ns_badver.lineage_key == s2.lineage_key
    for t in (
        r_observe(s2, ns_badver, probe),
        r_issue(s2, ns_badver, "x2", endpoint, (CAUSAL_ROOT_FACT,), "cat A.md"),
        r_receipt(s2, ns_badver, "x3", endpoint, (CAUSAL_ROOT_FACT,), "cat A.md"),
    ):
        assert_refused(
            t,
            s2,
            RootLineageOutcome.REFUSED_VERSION_CONFLICT,
            (RootLineageLimitation.VERSION_UNSUPPORTED,),
        )
        assert t.d_transition is None
    sel = select_current_root_region(s2, ns_badver)
    assert sel.outcome is RootSelectionOutcome.REFUSED
    assert sel.limitations == (RootLineageLimitation.VERSION_UNSUPPORTED,)
    assert sel.selected_source_digest is None
    assert sel.witness_facts == ()
    assert sel.lineage_key == s2.lineage_key
    assert sel.revision == s2.revision
    # (c2) A self-CONSISTENT v2 namespace (its lineage key honestly
    # recomputed for v2) over the genuine v1 state: the lineage-key
    # scope fence precedes the version-support fence.
    k2 = _lineage_key(
        ns.history_key, v2, ROOT_REGION_LINEAGE_POLICY_VERSION, ns.root_lineage_bounds
    )
    ns_v2 = ns.model_copy(update={"contract_version": v2, "lineage_key": k2})
    assert ns_v2.lineage_key != s2.lineage_key
    for t in (
        r_observe(s2, ns_v2, probe),
        r_issue(s2, ns_v2, "x2", endpoint, (CAUSAL_ROOT_FACT,), "cat A.md"),
        r_receipt(s2, ns_v2, "x3", endpoint, (CAUSAL_ROOT_FACT,), "cat A.md"),
    ):
        assert_refused(t, s2, RootLineageOutcome.REFUSED_FOREIGN_SCOPE, ())
        assert t.d_transition is None
    sel = select_current_root_region(s2, ns_v2)
    assert sel.outcome is RootSelectionOutcome.REFUSED
    assert sel.limitations == (RootLineageLimitation.FOREIGN_SCOPE,)
    assert sel.selected_source_digest is None
    assert sel.lineage_key == s2.lineage_key
    assert sel.revision == s2.revision
    # (c3) A fully COHERENT v2 namespace AND a state rekeyed to the
    # same consistent v2 key: the version-pair fence still refuses
    # the unsupported contract version (scope identity alone is not
    # version support).
    s2_v2 = s2.model_copy(update={"lineage_key": k2})
    for t in (
        r_observe(s2_v2, ns_v2, probe),
        r_issue(s2_v2, ns_v2, "x2", endpoint, (CAUSAL_ROOT_FACT,), "cat A.md"),
        r_receipt(s2_v2, ns_v2, "x3", endpoint, (CAUSAL_ROOT_FACT,), "cat A.md"),
    ):
        assert_refused(
            t,
            s2_v2,
            RootLineageOutcome.REFUSED_VERSION_CONFLICT,
            (RootLineageLimitation.VERSION_UNSUPPORTED,),
        )
        assert t.d_transition is None
    sel = select_current_root_region(s2_v2, ns_v2)
    assert sel.outcome is RootSelectionOutcome.REFUSED
    assert sel.limitations == (RootLineageLimitation.VERSION_UNSUPPORTED,)
    assert sel.selected_source_digest is None
    assert sel.lineage_key == s2_v2.lineage_key
    assert sel.revision == s2_v2.revision
    # (d) A CAS mismatch refuses before any work.
    t = observe_root_region_lineage(s2, ns, s2.revision + 1, probe)
    assert_refused(t, s2, RootLineageOutcome.REFUSED_CAS_MISMATCH, ())
    assert t.d_transition is None


@pytest.mark.parametrize("mode", MODES)
def test_i_bootstrap_scope_gates(mode: AdmissionMode) -> None:
    """A bootstrap envelope under a WRONG workspace or a WRONG root
    path is a typed D-level refusal carried through the NEW
    bootstrap: no anchor, no facts, the strict old root law
    unchanged (the region composition origin is carried)."""
    ns = r_ns(mode, "p-i-bootws")
    bad_ws = GraphRequest(
        payload={"input": [_root_item_ws("/workX")]}, endpoint="responses", context=None
    )
    t = bootstrap_root_region_lineage((bad_ws,), ns)
    assert t.outcome is RootLineageOutcome.REFUSED_ROOT_CONFLICT
    assert t.diagnostics == (RootLineageLimitation.WORKSPACE_MISMATCH,)
    assert t.new_root_facts == ()
    assert t.state.revision == 0
    assert t.state.root_facts == ()
    ns2 = r_ns(mode, "p-i-bootpath")
    bad_path = GraphRequest(
        payload={"input": [_root_item_ws(WORKSPACE, path="README.md")]},
        endpoint="responses",
        context=None,
    )
    t2 = bootstrap_root_region_lineage((bad_path,), ns2)
    assert t2.outcome is RootLineageOutcome.REFUSED_NO_ROOT
    assert t2.diagnostics == (RootLineageLimitation.NO_ROOT,)
    assert t2.new_root_facts == ()
    assert t2.state.revision == 0
    assert t2.state.root_facts == ()


# --- J. Forged states through the PUBLIC operations --------------------


def _j_forge_flag(state: Any) -> Any:
    m1 = region_fact(state, "m1")
    return _g_swap(state, m1, m1.model_copy(update={"issued": False}))


def _j_forge_detached_occurrence(state: Any) -> Any:
    m1 = region_fact(state, "m1")
    bad_p = m1.provenance.model_copy(update={"occurrence_id": "f" * 64})
    return _g_swap(state, m1, m1.model_copy(update={"provenance": bad_p}))


def _j_forge_coherent_rekey(state: Any) -> Any:
    m1 = region_fact(state, "m1")
    a_digest = sha256_hex(A_TEXT)
    a_len = len(A_TEXT.encode("utf-8"))
    bad_p = m1.provenance.model_copy(
        update={"root_member_digest": a_digest, "root_member_byte_length": a_len}
    )
    return _g_swap(
        state,
        m1,
        m1.model_copy(
            update={"provenance": bad_p, "source_digest": a_digest, "source_byte_length": a_len}
        ),
    )


def _j_forge_segment_swap(state: Any) -> Any:
    m1 = region_fact(state, "m1")
    bad_p = m1.provenance.model_copy(update={"root_segment_index": 0})
    return _g_swap(state, m1, m1.model_copy(update={"provenance": bad_p}))


def _j_forge_endpoint_mismatch(state: Any) -> Any:
    m1 = region_fact(state, "m1")
    other = "chat" if m1.provenance.endpoint == "responses" else "responses"
    bad_p = m1.provenance.model_copy(update={"endpoint": other})
    return _g_swap(state, m1, m1.model_copy(update={"provenance": bad_p}))


def _j_forge_owner_mismatch(state: Any) -> Any:
    m1 = region_fact(state, "m1")
    bad_p = m1.provenance.model_copy(update={"call_id": "not-m1"})
    return _g_swap(state, m1, m1.model_copy(update={"provenance": bad_p}))


def _j_forge_wrong_root_path(state: Any) -> Any:
    """A region rekeyed so its member position points at the
    NONROOT member (digests made consistent) reaches the actual
    member-path fence."""
    m1 = region_fact(state, "m1")
    n1 = next(o for o in state.d_state.occurrences if o.call_id == "n1")
    seg0 = n1.proof.segments[0]
    bad_p = m1.provenance.model_copy(
        update={
            "root_segment_index": 0,
            "root_member_position": 0,
            "root_member_digest": seg0.member_digest,
            "root_member_byte_length": seg0.byte_length,
        }
    )
    return _g_swap(
        state,
        m1,
        m1.model_copy(
            update={
                "provenance": bad_p,
                "source_digest": seg0.member_digest,
                "source_byte_length": seg0.byte_length,
            }
        ),
    )


def _j_forge_whole_proof_digest(state: Any) -> Any:
    """A forged whole-proof aggregate digest (the fact's root-body
    fields stay self-consistent): the retained occurrence's ACTUAL
    whole proof must still bind."""
    m1 = region_fact(state, "m1")
    bad_p = m1.provenance.model_copy(update={"whole_proof_digest": "e" * 64})
    return _g_swap(state, m1, m1.model_copy(update={"provenance": bad_p}))


def _j_forge_whole_proof_length(state: Any) -> Any:
    """A forged whole-proof aggregate byte length (off by one)."""
    m1 = region_fact(state, "m1")
    bad_p = m1.provenance.model_copy(
        update={"whole_proof_byte_length": m1.provenance.whole_proof_byte_length + 1}
    )
    return _g_swap(state, m1, m1.model_copy(update={"provenance": bad_p}))


def _j_forge_root_member_length(state: Any) -> Any:
    """A forged ROOT MEMBER byte length (digest unchanged): the
    actual segment member length must still join."""
    m1 = region_fact(state, "m1")
    bad_p = m1.provenance.model_copy(
        update={"root_member_byte_length": m1.provenance.root_member_byte_length + 1}
    )
    return _g_swap(state, m1, m1.model_copy(update={"provenance": bad_p}))


def _j_forge_original_proof_identity(state: Any) -> Any:
    """Swap the region occurrence's retained PROOF for a different
    GENUINE retained proof (n1's nonroot read): every stored field
    stays self-consistent with the original m1 proof, but the
    proof still carries the immutable bootstrap root binding while
    its source/member/owner association no longer matches the
    ACTUAL retained original proof of that occurrence."""
    m1_occ = next(o for o in state.d_state.occurrences if o.call_id == "m1")
    n1_occ = next(o for o in state.d_state.occurrences if o.call_id == "n1")
    assert m1_occ.proof is not n1_occ.proof
    bad_occ = m1_occ.model_copy(update={"proof": n1_occ.proof})
    d_bad = state.d_state.model_copy(
        update={
            "occurrences": tuple(
                o if o is not m1_occ else bad_occ for o in state.d_state.occurrences
            )
        }
    )
    return state.model_copy(update={"d_state": d_bad})


def _j_forge_d_owner_missing(state: Any) -> Any:
    """OMIT the ACTUAL retained D result that owns the region
    occurrence: the old D validator law alone does not require an
    owning result (it stays None), so the NEW region ownership join
    is the one that must refuse."""
    m1_result = next(r for r in state.d_state.results if r.call_id == "m1")
    d_bad = state.d_state.model_copy(
        update={"results": tuple(r for r in state.d_state.results if r is not m1_result)}
    )
    return state.model_copy(update={"d_state": d_bad})


def _j_forge_d_owner_rekeyed(state: Any) -> Any:
    """REKEY the ACTUAL retained D owning result's producer
    association (the occurrence's call no longer owns the complete
    result): the old D validator stays None, the NEW region
    ownership join must refuse."""
    m1_result = next(r for r in state.d_state.results if r.call_id == "m1")
    d_bad = state.d_state.model_copy(
        update={
            "results": tuple(
                r if r is not m1_result else m1_result.model_copy(update={"call_id": "not-m1"})
                for r in state.d_state.results
            )
        }
    )
    return state.model_copy(update={"d_state": d_bad})


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
def test_j_forged_states_refused_through_public_operations(
    forge: Callable[[Any], Any], mode: AdmissionMode, endpoint: str
) -> None:
    """Every forged region state is refused by the PUBLIC
    operations -- selection (typed refused query), observation and
    registration (issuance AND receipt; exact prior forged state, no
    D work) -- on BOTH read endpoints and BOTH admission modes, not
    only by the direct validator (the public gates run the charged
    cross-record validation BEFORE any positive work)."""
    ns, good = _g_setup(mode, endpoint)
    bad = forge(good)
    assert bad is not good
    # The D-level ownership forges: the OLD D validator law alone
    # stays coherent (None); the NEW region ownership join is what
    # refuses them.
    if forge in (_j_forge_d_owner_missing, _j_forge_d_owner_rekeyed):
        assert validate_causal_history_state(bad.d_state) is None
    # Selection: the typed refused query.
    sel = select_current_root_region(bad, ns)
    assert sel.outcome is RootSelectionOutcome.REFUSED
    assert sel.limitations == (RootLineageLimitation.MALFORMED_BINDING,)
    assert sel.selected_source_digest is None
    assert sel.witness_facts == ()
    assert sel.lineage_key == bad.lineage_key
    assert sel.revision == bad.revision
    # Observation: exact prior (forged) state, no D work.
    t = r_observe(bad, ns, (read_request(endpoint, "x1", A_TEXT, "cat A.md"),))
    assert t.outcome is RootLineageOutcome.REFUSED_CONFLICT
    assert t.diagnostics == (RootLineageLimitation.MALFORMED_BINDING,)
    assert t.state is bad
    assert t.new_root_facts == ()
    assert t.d_transition is None
    # Registration (issuance AND receipt): exact prior (forged)
    # state, no D work.
    for t in (
        r_issue(bad, ns, "x2", endpoint, (CAUSAL_ROOT_FACT,), "cat A.md"),
        r_receipt(bad, ns, "x3", endpoint, (CAUSAL_ROOT_FACT,), "cat A.md"),
    ):
        assert t.outcome is RootLineageOutcome.REFUSED_CONFLICT
        assert t.diagnostics == (RootLineageLimitation.MALFORMED_BINDING,)
        assert t.state is bad
        assert t.new_root_facts == ()
        assert t.d_transition is None
    # The genuine state stays coherent (the forge touched a copy).
    assert validate_root_region_lineage_state(good, ns.root_lineage_bounds) is None


# --- K. Privacy: fixed non-echoing errors and reprs ---------------------


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_k_privacy_no_raw_body_echo(mode: AdmissionMode, endpoint: str) -> None:
    """The fixed privacy law: retained records, transitions,
    diagnostics and selections never echo retained raw content or
    identity fields -- a canary planted in the NONROOT segment of a
    mixed read, a canary planted in the ROOT source envelope, and a
    canary planted in EVERY identity/model field are all absent from
    every str/repr surface (retained identity is digest/length bound,
    content never re-serialized, identity fields are canonically
    hashed), including the fixed private old-I rejection message."""
    body = _mixed_body(f"{A_TEXT}{CANARY}", MARK, V2)
    identity = RequestIdentity(
        principal=ID_CANARY,
        session=ID_CANARY,
        repository=ID_CANARY,
        route=ID_CANARY,
    )
    ns, s0 = r_bootstrap(
        mode,
        "p-k-priv",
        identity=identity,
        model_identity=ID_CANARY,
        root_body=f"Synthetic root. {ROOT_CANARY}",
    )
    t1 = r_issue(s0, ns, "m1", endpoint, (CAUSAL_ROOT_FACT,), MIX_CMD)
    assert t1.outcome is RootLineageOutcome.ACCEPTED
    t2 = r_observe(t1.state, ns, (read_request(endpoint, "m1", body, MIX_CMD),))
    assert t2.outcome is RootLineageOutcome.ACCEPTED, (t2.outcome, t2.diagnostics)
    s2 = t2.state
    sel = select_current_root_region(s2, ns)
    assert sel.outcome is RootSelectionOutcome.OK
    surfaces = [
        repr(ns),
        str(ns),
        repr(t1),
        str(t1),
        repr(t2),
        str(t2),
        repr(s2),
        str(s2),
        repr(s2.d_state),
        str(s2.d_state),
        repr(sel),
        str(sel),
    ]
    for fact in s2.root_facts:
        surfaces += [repr(fact), str(fact), repr(fact.provenance), str(fact.provenance)]
    for occ in s2.d_state.occurrences:
        surfaces += [repr(occ), str(occ), repr(occ.proof), str(occ.proof)]
    for result in s2.d_state.results:
        surfaces += [repr(result), str(result)]
    for issuance in s2.d_state.issuances:
        surfaces += [repr(issuance), str(issuance)]
    for limitation in list(t2.diagnostics) + list(sel.limitations):
        surfaces += [repr(limitation), str(limitation)]
    try:
        derive(s2, ns)
    except ValueError as exc:
        surfaces += [repr(exc), str(exc)]
    else:
        raise AssertionError("the old I must honestly refuse the region state")
    for surface in surfaces:
        for canary in (CANARY, ROOT_CANARY, ID_CANARY):
            assert canary not in surface


# --- L. Purity: no host IO on ANY public region path -------------------


def _host_io_facilities() -> list[tuple[Any, str]]:
    """The closed host-facility surface the NEW pure producer must
    never touch: the same 24 process/file/network entry points the
    independent ROOT purity probe traps (eight core facilities plus
    the sixteen os entry points present on this platform)."""
    facilities: list[tuple[Any, str]] = [
        (builtins, "open"),
        (io, "open"),
        (socket, "socket"),
        (socket, "create_connection"),
        (socket, "getaddrinfo"),
        (subprocess, "Popen"),
        (asyncio, "create_subprocess_exec"),
        (asyncio, "create_subprocess_shell"),
    ]
    facilities.extend(
        (os, name)
        for name in (
            "open",
            "stat",
            "lstat",
            "listdir",
            "scandir",
            "readlink",
            "access",
            "unlink",
            "replace",
            "rename",
            "mkdir",
            "rmdir",
            "remove",
            "system",
            "fork",
            "posix_spawn",
        )
        if hasattr(os, name)
    )
    return facilities


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_l_no_host_io_on_public_paths(
    mode: AdmissionMode, endpoint: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    """No host IO anywhere on the NEW public region paths.

    Fixture and import setup happen BEFORE the traps open; the traps
    then cover the entire public surface on the SAME legitimate state
    (factory, bootstrap, issuance, observation, validate, selection,
    receipt, replay, the fixed CAS-mismatch and forged-state refusals
    and the malformed-state error).  Every operational record's
    str/repr must be free of the identity/root/new-content canaries
    and the original request payloads must be unchanged afterwards."""
    marker = "PURITY-MARKER-018P"
    root_body = "PRIVATE-ROOT-CONTENT-018P. Read `A.md`."
    new_root = "PRIVATE-NEW-CONTENT-018P"
    new_body = f"Ordinary A.\n{marker}\n{new_root}."
    call_id = "purity-call-018p"
    identity = RequestIdentity(
        principal="purity-principal-018p",
        session="purity-session-018p",
        repository="purity-repository-018p",
        route="purity-route-018p",
    )
    canaries = (
        identity.principal,
        identity.session,
        identity.repository,
        identity.route,
        "purity-model-018p",
        "purity-lineage-018p",
        call_id,
        marker,
        root_body,
        new_root,
    )
    cmd = f"cat A.md && echo '{marker}' && cat AGENTS.md"
    args = json.dumps({"cmd": cmd})
    root = rooted(root_body)
    request = read_request(endpoint, call_id, new_body, cmd)
    originals = [json.dumps(q.payload, sort_keys=True) for q in (root, request)]
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
        model_identity="purity-model-018p",
        config_fingerprint="c" * 64,
        workspace="/work",
        mode=mode,
    )
    ns = make_root_region_lineage_namespace(admission, "purity-lineage-018p")
    t0 = bootstrap_root_region_lineage((root,), ns)
    assert t0.outcome is RootLineageOutcome.ACCEPTED, t0.diagnostics
    t1 = register_root_region_issuance(
        t0.state,
        ns,
        call_id,
        endpoint,
        "exec_command",
        args,
        (CAUSAL_ROOT_FACT,),
        t0.state.revision,
    )
    assert t1.outcome is RootLineageOutcome.ACCEPTED, t1.diagnostics
    t2 = observe_root_region_lineage(t1.state, ns, t1.state.revision, (request,))
    assert t2.outcome is RootLineageOutcome.ACCEPTED, (t2.outcome, t2.diagnostics)
    state = t2.state
    assert validate_root_region_lineage_state(state, ns.root_lineage_bounds) is None
    query = select_current_root_region(state, ns)
    assert query.outcome is RootSelectionOutcome.OK, query.limitations
    region = next(f for f in state.root_facts if f.provenance.kind == "read_region")
    region_prov = region.provenance
    assert isinstance(region_prov, RootRegionReadProvenance)
    assert query.witness_facts[0] is region
    receipt = register_root_region_receipt(
        state,
        ns,
        call_id,
        endpoint,
        "exec_command",
        args,
        (CAUSAL_ROOT_FACT,),
        state.revision,
    )
    assert receipt.outcome is RootLineageOutcome.REPLAYED and receipt.state is state
    replay = observe_root_region_lineage(state, ns, state.revision, (request,))
    assert replay.outcome is RootLineageOutcome.REPLAYED and replay.state is state
    cas = observe_root_region_lineage(state, ns, state.revision + 1, (request,))
    assert cas.outcome is RootLineageOutcome.REFUSED_CAS_MISMATCH and cas.state is state
    forged = region.model_copy(update={"issued": False})
    bad = state.model_copy(
        update={"root_facts": tuple(forged if x is region else x for x in state.root_facts)}
    )
    bad_query = select_current_root_region(bad, ns)
    assert bad_query.outcome is RootSelectionOutcome.REFUSED
    conflict_transitions = [
        operation(
            bad,
            ns,
            "descendant",
            endpoint,
            "exec_command",
            args,
            (region_prov.occurrence_id,),
            bad.revision,
        )
        for operation in (register_root_region_issuance, register_root_region_receipt)
    ]
    for transition in conflict_transitions:
        assert transition.outcome is RootLineageOutcome.REFUSED_CONFLICT
        assert transition.state is bad
    observed = observe_root_region_lineage(bad, ns, bad.revision, (request,))
    assert observed.outcome is RootLineageOutcome.REFUSED_CONFLICT
    assert observed.state is bad
    objects: list[Any] = [
        ns,
        t0,
        t1,
        t2,
        state,
        query,
        receipt,
        replay,
        cas,
        bad,
        bad_query,
        observed,
    ]
    objects.extend(conflict_transitions)
    objects.extend(state.root_facts)
    objects.extend(fact.provenance for fact in state.root_facts)
    objects.extend(state.d_state.occurrences)
    objects.extend(state.d_state.results)
    surfaces: list[str] = []
    for obj in objects:
        surfaces.extend((repr(obj), str(obj)))
    malformed: Any = None  # deliberate out-of-contract input
    try:
        select_current_root_region(malformed, ns)
    except ValueError as exc:
        surfaces.extend((repr(exc), str(exc)))
    else:
        raise AssertionError("malformed state not refused")
    for surface in surfaces:
        for canary in canaries:
            assert canary not in surface, (canary, surface[:120])
    assert not calls
    assert [json.dumps(q.payload, sort_keys=True) for q in (root, request)] == originals

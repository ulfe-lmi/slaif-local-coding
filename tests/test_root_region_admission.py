"""Permanent 018-t complete-consumer controls (first batch).

This module is the permanent A-G acceptance-matrix home for the
complete root-region admission consumer (active order 018-t).
This first batch carries the genuine public positives (envelope and
mixed-only region, both modes and both read endpoints), the whole-
operation exact/one-below crossing under the SAME explicit bound/
call shape, the closed bootstrap-pass overflow law (legal caps at
or just above the bootstrap charge map to the fixed typed refusal,
never a leaked internal overflow, and an unjoined namespace keeps
the exact foreign-scope shape even when the crossing hits before
the fence runs), the inherited G-channel result-model law (the G
refusal limitation is carried ONLY on the actual G-domain REFUSED
outcome, with the exact diagnostic pairing and the closed empty-
diagnostics boundary), the third-parent carried-bound-set
ordering (the closed O(1) eleven/six bound-set fences and the
closed source-independent carried R joins complete at the
full-result carrying boundary BEFORE the consumer scope-key
serializer targets) and the terminal-refusal body-freeness (the
overflow-tail record retains the actual R object by reference
as bounded evidence and its third-parent revalidation never
re-enters the root body content pass).  The remaining ordered
evidence (B version/withdrawal matrix, C third-parent bypass
battery, D local-cap discriminators and G = F+admission < whole,
E source-scale, F purity/IO traps, G criterion map) is added to
this module in the later batches of the same active order.
"""

from __future__ import annotations

import json
from typing import Any

import pytest
from pydantic import ValidationError

from slaif_local_coding.constitution.bundles import (
    root_region_admission as _t_mod,
)
from slaif_local_coding.constitution.bundles import (
    root_region_admission_result_models as _result_models,
)
from slaif_local_coding.constitution.bundles import (
    root_region_currentness as _q_mod,
)
from slaif_local_coding.constitution.bundles import (
    root_region_graph as _r_mod,
)
from slaif_local_coding.constitution.bundles import (
    root_region_graph_models as _graph_models,
)
from slaif_local_coding.constitution.bundles.bundle_admission_models import (
    AdmissionMode,
    make_bundle_admission_namespace,
)
from slaif_local_coding.constitution.bundles.causal_history_models import (
    CAUSAL_ROOT_FACT,
    CausalHistoryLimitation,
)
from slaif_local_coding.constitution.bundles.current_admission_models import (
    CurrentAdmissionBounds,
    CurrentAdmissionLimitation,
    _canonical_entry_key,
)
from slaif_local_coding.constitution.bundles.current_graph_models import (
    CurrentGraphBounds,
    CurrentGraphOutcome,
    CurrentGraphStatus,
)
from slaif_local_coding.constitution.bundles.graph_models import (
    ROOT_FILENAME,
    GraphBounds,
)
from slaif_local_coding.constitution.bundles.root_lineage import (
    _HOuter,
)
from slaif_local_coding.constitution.bundles.root_lineage_models import (
    RootLineageLimitation,
    RootLineageOutcome,
    RootSelectionOutcome,
)
from slaif_local_coding.constitution.bundles.root_region_admission import (
    derive_root_region_admission,
)
from slaif_local_coding.constitution.bundles.root_region_admission_result_models import (
    RootRegionAdmissionBounds,
    RootRegionAdmissionDiagnostic,
    RootRegionAdmissionOutcome,
    RootRegionAdmissionResult,
)
from slaif_local_coding.constitution.bundles.root_region_currentness_models import (
    RootRegionCurrentnessBounds,
    RootRegionCurrentnessOutcome,
)
from slaif_local_coding.constitution.bundles.root_region_graph_models import (
    RootRegionGraphBounds,
    RootRegionGraphDiagnostic,
    RootRegionGraphOutcome,
)
from slaif_local_coding.constitution.bundles.root_region_lineage import (
    bootstrap_root_region_lineage,
    observe_root_region_lineage,
)
from slaif_local_coding.constitution.bundles.root_region_lineage_models import (
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
    frame,
    read_request,
    sha256_hex,
)
from tests.test_root_lineage import rooted
from tests.test_root_region_currentness import (
    A_TEXT as Q_A_TEXT,
)
from tests.test_root_region_currentness import (
    MARK as Q_MARK,
)
from tests.test_root_region_currentness import (
    MIX_CMD as Q_MIX_CMD,
)
from tests.test_root_region_currentness import (
    _e_branch_state,
    _frontier_state,
    q_issue,
    q_observe,
    q_occ,
)
from tests.test_root_region_currentness import (
    mixed_body as q_mixed_body,
)
from tests.test_root_region_graph import (
    A_NEW_TEXT,
    A_OLD_TEXT,
    MULTI_CMD,
    REGION_PREFIX,
    V1_ROOT,
    V2_ROOT,
    X_MD_NEW,
    X_MD_OLD,
    _d_ready_fixture,
    _mixed_region_state,
    _multi_source_state,
    _native_multi_piece_request,
    _revert_state,
)
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

# The anchor scope for the crossing/channel controls (first mode and
# read endpoint; the full 2x2 scope is exercised by the positive
# matrix).
_MODE = MODES[0]
_ENDPOINT = ENDPOINTS[0]


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_a_genuine_envelope_positive_ready(mode: AdmissionMode, endpoint: str) -> None:
    """A1: the genuine public P bootstrap envelope READYs the
    complete public derivation in both modes and both read
    endpoints: the exact input retained by identity, the ACTUAL R
    READY result retained by reference, the ACTUAL S admission
    parent by reference (the third carrying boundary), the
    envelope root source and the honest same-run counters."""
    ns, state = r_bootstrap(mode, f"t018a-env-{endpoint}")
    r = derive_root_region_admission(state, ns)
    assert r.outcome is RootRegionAdmissionOutcome.READY
    assert r.diagnostics == ()
    assert r.g_limitation is None
    assert r.state is state
    assert r.ns is ns
    assert r.revision == state.revision
    assert r.lineage_key == state.lineage_key
    rr = r.r_result
    assert rr is not None
    assert rr.outcome is RootRegionGraphOutcome.READY
    assert rr.state is state
    src = rr.resolved_source
    assert src is not None
    assert src.kind == "envelope"
    adm = r.admission
    assert adm is not None
    assert adm.state is state
    assert adm.ns is ns
    assert adm.r_result is rr
    assert adm.g_bounds is r.g_bounds
    assert adm.root_entry.root_source is src
    # honest same-run counters under the ACTUAL effective bounds
    assert 0 < r.r_work_units <= r.work_units <= r.bounds.max_total_work_units
    assert 0 < r.g_work_units <= r.g_bounds.max_total_work_units
    assert r.stage_work_units <= ns.graph_bounds.max_work_units
    assert r.entry_source_bytes == src.root_byte_length


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_d_original_batch_domain_not_cumulative(mode: AdmissionMode, endpoint: str) -> None:
    """D: the ACTUAL inherited D per-batch request domain
    (max_requests) beneath the complete consumer: with
    max_requests=1, two SEPARATE one-request observations are
    each legal and BOTH retained (the per-batch domain, not a
    cumulative cap) and the complete public derivation READYs on
    the exact retained state; ONE two-request batch refuses the
    exact mapped batch bound BEFORE the deliberately malformed
    second element (missing call id) is inspected -- the count
    gate precedes element validation -- with the EXACT prior
    state, no D transition and no revision advance, and the
    complete public derivation remains READY on the preserved
    state (original-batch caps are not cumulative retention
    caps)."""
    admission = make_bundle_admission_namespace(
        IDENTITY,
        model_identity="synthetic-t-model",
        config_fingerprint=FINGERPRINT,
        workspace=WORKSPACE,
        mode=mode,
        graph_bounds=GraphBounds(max_requests=1),
    )
    ns = make_root_region_lineage_namespace(admission, f"t018d-b-{mode.value}-{endpoint}")
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
    # The ACTUAL complete public derivation over the retained
    # state at the bound: READY with the anchor root usable,
    # both completed observations retained, no root uncertainty,
    # exact state.
    r1 = derive_root_region_admission(s2, ns)
    assert r1.outcome is RootRegionAdmissionOutcome.READY
    assert r1.admission is not None
    assert r1.state is s2
    rr1 = r1.r_result
    assert rr1 is not None
    assert rr1.outcome is RootRegionGraphOutcome.READY
    src1 = rr1.resolved_source
    assert src1 is not None
    assert src1.kind == "envelope"
    assert src1.root_text == "Batch root."
    assert rr1.q_result is not None
    assert rr1.q_result.p_selection is not None
    assert rr1.q_result.p_selection.outcome is RootSelectionOutcome.OK
    assert not rr1.q_result.uncertainty_witnesses
    assert rr1.state is s2
    # One two-request batch: the bound fires before the bad
    # element (the count gate precedes element validation).
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
    assert t3.d_transition is not None
    assert t3.d_transition.outcome.value == "refused_over_bound"
    assert t3.d_transition.diagnostics == (CausalHistoryLimitation.BATCH_OVER_BOUND,)
    assert t3.revision_after == s2.revision
    # The preserved state is UNCHANGED (identity + revision), and
    # the complete public derivation remains READY on it.
    r2 = derive_root_region_admission(s2, ns)
    assert r2.outcome is RootRegionAdmissionOutcome.READY
    assert r2.admission is not None
    assert r2.state is s2
    assert r2.revision == s2.revision
    rr2 = r2.r_result
    assert rr2 is not None
    assert rr2.outcome is RootRegionGraphOutcome.READY
    assert rr2.state is s2
    src2 = rr2.resolved_source
    assert src2 is not None
    assert src2.root_digest == src1.root_digest
    assert src2.root_text == "Batch root."


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_f_canonical_payload_data_preservation(mode: AdmissionMode, endpoint: str) -> None:
    """F: canonical payload DATA preservation beyond the
    key-record JSON: two complete public derivations of the SAME
    state/namespace (no revision advance, no bounds change)
    produce byte-identical canonical admission payload DATA --
    the full admission JSON, the root and every FILE key record,
    the scope key and the honest work counters -- while the exact
    input state/namespace/revision remain identity-bound, the
    canonical INPUT payload DATA is unchanged by the derivations,
    the selected source evidence agrees, and every retained
    original proof is the SAME object in both results."""
    ns, state, _v2_body, v2_digest = _t_e_multi_dep_state(
        mode,
        endpoint,
        f"t018f-data-{endpoint}",
        graph_bounds=GraphBounds(max_work_units=1_048_576),
    )
    # the canonical INPUT payload DATA, snapshotted before any
    # T call (input preservation, not merely output determinism):
    state_data = json.dumps(state.model_dump(mode="json"), sort_keys=True)
    ns_data = json.dumps(ns.model_dump(mode="json"), sort_keys=True)
    r1 = derive_root_region_admission(state, ns)
    r2 = derive_root_region_admission(state, ns)
    # the canonical INPUT payload DATA is unchanged by the
    # derivations:
    assert json.dumps(state.model_dump(mode="json"), sort_keys=True) == state_data
    assert json.dumps(ns.model_dump(mode="json"), sort_keys=True) == ns_data
    assert r1.outcome is RootRegionAdmissionOutcome.READY
    assert r2.outcome is RootRegionAdmissionOutcome.READY
    assert r1.state is state
    assert r2.state is state
    assert r1.ns is ns
    assert r2.ns is ns
    assert r1.revision == state.revision
    assert r2.revision == state.revision
    assert r1.lineage_key == state.lineage_key
    assert r2.lineage_key == state.lineage_key
    assert r1.scope_key == r2.scope_key
    rr1 = r1.r_result
    rr2 = r2.r_result
    assert rr1 is not None and rr2 is not None
    assert rr1.scope_key == rr2.scope_key
    assert rr1.resolved_source is not None
    assert rr2.resolved_source is not None
    assert rr1.resolved_source.root_digest == v2_digest
    assert rr2.resolved_source.root_digest == v2_digest
    adm1 = r1.admission
    adm2 = r2.admission
    assert adm1 is not None and adm2 is not None
    # the FULL canonical admission payload DATA is byte-identical:
    data1 = json.dumps(adm1.model_dump(mode="json"), sort_keys=True)
    data2 = json.dumps(adm2.model_dump(mode="json"), sort_keys=True)
    assert data1 == data2
    # every key record (root and FILE) is byte-identical, and the
    # retained original proofs are the SAME objects:

    def _kr(entry: Any) -> str:
        return json.dumps(entry.key_record.model_dump(mode="json"), sort_keys=True)

    assert adm1.root_entry.content_key == adm2.root_entry.content_key
    assert _kr(adm1.root_entry) == _kr(adm2.root_entry)
    assert len(adm1.entries) == len(adm2.entries)
    for e1, e2 in zip(adm1.entries, adm2.entries, strict=True):
        assert e1.content_key == e2.content_key
        assert _kr(e1) == _kr(e2)
        assert e1.proof is e2.proof
    # honest work counters are deterministic:
    assert r1.work_units == r2.work_units
    assert r1.r_work_units == r2.r_work_units
    assert r1.g_work_units == r2.g_work_units
    assert r1.stage_work_units == r2.stage_work_units
    assert r1.entry_source_bytes == r2.entry_source_bytes


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_a_genuine_mixed_region_positive_ready(mode: AdmissionMode, endpoint: str) -> None:
    """A2: the earned mixed-only NEW root region (NO independent
    singleton) READYs the complete derivation: the read_region
    root source retained by reference with the V2 bytes/digest and
    the admission parent joined to it."""
    ns, state = _mixed_region_state(mode, endpoint, f"t018a-mix-{endpoint}")
    r = derive_root_region_admission(state, ns)
    assert r.outcome is RootRegionAdmissionOutcome.READY
    assert r.diagnostics == ()
    assert r.g_limitation is None
    rr = r.r_result
    assert rr is not None
    assert rr.outcome is RootRegionGraphOutcome.READY
    src = rr.resolved_source
    assert src is not None
    assert src.kind == "read_region"
    assert src.root_text == V2
    assert src.root_digest == sha256_hex(V2)
    adm = r.admission
    assert adm is not None
    assert adm.state is state
    assert adm.ns is ns
    assert adm.r_result is rr
    assert adm.root_entry.root_source is src
    assert adm.root_entry.root_digest == src.root_digest
    assert 0 < r.g_work_units <= r.g_bounds.max_total_work_units
    assert r.work_units <= r.bounds.max_total_work_units


def test_d_whole_exact_and_one_below() -> None:
    """D1: the whole-operation exact/one-below pair under the SAME
    explicit bound/call shape (the explicit-bounds path cost W0):
    the exact cap READYs at W0; one below REFUSES with the fixed
    work diagnostic at W0-1, retaining the ACTUAL R result as
    bounded evidence (the crossing is after the R return), exposing
    no admission and no G channel."""
    ns, state = r_bootstrap(_MODE, "t018a-whole")
    r0 = derive_root_region_admission(state, ns, bounds=RootRegionAdmissionBounds())
    assert r0.outcome is RootRegionAdmissionOutcome.READY
    w0 = r0.work_units
    assert w0 > 0
    exact = derive_root_region_admission(
        state, ns, bounds=RootRegionAdmissionBounds(max_total_work_units=w0)
    )
    assert exact.outcome is RootRegionAdmissionOutcome.READY
    assert exact.work_units == w0
    assert exact.admission is not None
    below = derive_root_region_admission(
        state, ns, bounds=RootRegionAdmissionBounds(max_total_work_units=w0 - 1)
    )
    assert below.outcome is RootRegionAdmissionOutcome.REFUSED
    assert below.diagnostics == (RootRegionAdmissionDiagnostic.WORK_UNITS_OVER_BOUND,)
    assert below.work_units == w0 - 1
    assert below.admission is None
    assert below.g_limitation is None
    rr = below.r_result
    assert rr is not None
    assert rr.outcome is RootRegionGraphOutcome.READY
    assert rr.state is state


@pytest.mark.parametrize("cap", [1, 64, 65, 68])
def test_d_bootstrap_crossing_clean_work_refusal(cap: int) -> None:
    """D2: a legal consumer cap at or just above the closed
    bootstrap charge crosses in the closed early passes (the base
    charge, the fence charge or the bound-resolution charge): the
    public derivation maps it to the fixed typed work refusal with
    the honest spent counter (exactly the cap), no R result, no
    admission, no G channel, and NEVER leaks the internal
    overflow."""
    ns, state = r_bootstrap(_MODE, f"t018a-cap{cap}")
    r = derive_root_region_admission(
        state, ns, bounds=RootRegionAdmissionBounds(max_total_work_units=cap)
    )
    assert r.outcome is RootRegionAdmissionOutcome.REFUSED
    assert r.diagnostics == (RootRegionAdmissionDiagnostic.WORK_UNITS_OVER_BOUND,)
    assert r.work_units == cap
    assert r.r_result is None
    assert r.admission is None
    assert r.g_limitation is None
    assert r.state is state
    assert r.ns is ns


def test_d_bootstrap_crossing_foreign_ns_shape() -> None:
    """D3: a bypass-copied UNJOINED namespace (negative stimulus
    copy-only) keeps the exact foreign-scope refusal shape on BOTH
    the charged fence path and the bootstrap-crossing path (the
    crossing can hit the fence charge before the fence runs; the
    closed predicate re-runs under the refusal convention and the
    shape is preserved)."""
    ns, state = r_bootstrap(_MODE, "t018a-foreign")
    foreign = ns.model_copy(update={"lineage_key": "f" * 64})
    r0 = derive_root_region_admission(state, foreign)
    assert r0.outcome is RootRegionAdmissionOutcome.REFUSED
    assert r0.diagnostics == (RootRegionAdmissionDiagnostic.FOREIGN_SCOPE,)
    assert r0.r_result is None
    assert r0.admission is None
    assert r0.g_limitation is None
    assert r0.ns is foreign
    for cap in (1, 65):
        r = derive_root_region_admission(
            state,
            foreign,
            bounds=RootRegionAdmissionBounds(max_total_work_units=cap),
        )
        assert r.outcome is RootRegionAdmissionOutcome.REFUSED
        assert r.diagnostics == (RootRegionAdmissionDiagnostic.FOREIGN_SCOPE,)
        assert r.work_units == cap
        assert r.r_result is None
        assert r.admission is None
        assert r.g_limitation is None
        assert r.ns is foreign


def test_d_g_domain_refusal_and_channel_law() -> None:
    """D4: the ACTUAL G-domain crossing (a legal G total cap of 1)
    REFUSES through the public derivation with the ACTUAL inherited
    G limitation retained in the distinct G channel (the consumer-
    OWN diagnostic names the domain); the result-model law closes
    the bypass-copy boundary: empty diagnostics carrying the G
    channel refuse with the fixed private error (never an index
    error), the READY and mapped non-READY variants globally forbid
    the field, and the exact diagnostic pairing law is preserved."""
    ns, state = r_bootstrap(_MODE, "t018a-gchan")
    g_refused = derive_root_region_admission(
        state, ns, admission_bounds=CurrentAdmissionBounds(max_total_work_units=1)
    )
    assert g_refused.outcome is RootRegionAdmissionOutcome.REFUSED
    assert g_refused.g_limitation is CurrentAdmissionLimitation.TOTAL_WORK_UNITS_OVER_BOUND
    assert g_refused.diagnostics == (RootRegionAdmissionDiagnostic.ADMISSION_OVER_BOUND,)
    assert g_refused.r_result is None
    assert g_refused.admission is None
    assert g_refused.g_work_units == 1
    assert g_refused.work_units <= g_refused.bounds.max_total_work_units
    # empty diagnostics carrying the G channel: the fixed private
    # boundary error, never an index error.
    with pytest.raises(
        ValidationError,
        match="the G limitation is carried only with the actual G-domain refusal diagnostic",
    ):
        RootRegionAdmissionResult.model_validate(g_refused.model_copy(update={"diagnostics": ()}))
    # the G channel dropped on the G-domain refusal: the existing
    # fixed pairing law is preserved.
    with pytest.raises(
        ValidationError,
        match="a G-domain refusal without the R result carries the actual G limitation",
    ):
        RootRegionAdmissionResult.model_validate(
            g_refused.model_copy(update={"g_limitation": None})
        )
    # the READY outcome globally forbids the G field.
    ready = derive_root_region_admission(state, ns)
    assert ready.outcome is RootRegionAdmissionOutcome.READY
    with pytest.raises(
        ValidationError,
        match="the G limitation is carried only on the actual G-domain refusal",
    ):
        RootRegionAdmissionResult.model_validate(
            ready.model_copy(update={"g_limitation": g_refused.g_limitation})
        )
    # the mapped non-READY variant (the ACTUAL same-run Q unproven)
    # globally forbids the G field.
    ns2, state2, _ = _frontier_state(_MODE, _ENDPOINT, "t018a-frontier")
    unproven = derive_root_region_admission(state2, ns2)
    assert unproven.outcome is RootRegionAdmissionOutcome.ROOT_CURRENTNESS_UNPROVEN
    assert unproven.diagnostics == ()
    assert unproven.r_result is not None
    assert unproven.admission is None
    assert unproven.g_limitation is None
    with pytest.raises(
        ValidationError,
        match="the G limitation is carried only on the actual G-domain refusal",
    ):
        RootRegionAdmissionResult.model_validate(
            unproven.model_copy(
                update={"g_limitation": CurrentAdmissionLimitation.TOTAL_WORK_UNITS_OVER_BOUND}
            )
        )
    # the exact pairing law: the over-bound diagnostic must not
    # carry the state-malformed limitation.
    with pytest.raises(
        ValidationError,
        match="the G over-bound diagnostic must not carry the state-malformed limitation",
    ):
        RootRegionAdmissionResult.model_validate(
            g_refused.model_copy(
                update={"g_limitation": CurrentAdmissionLimitation.STATE_MALFORMED}
            )
        )


def test_c_third_parent_bound_set_ordering(monkeypatch: pytest.MonkeyPatch) -> None:
    """C1: at the THIRD carrying boundary the closed O(1) carried-
    bound-set fences and the closed source-independent carried R
    joins (never the charged root-body content pass) complete
    BEFORE the consumer scope-key serializer targets: the legal
    stricter-Q-bounds positive is derived through the public
    operation on a genuine READY envelope bootstrap (never a
    model_copy manufacture) and revalidated at the boundary with
    the real scope serializer reached; a bypass-copied result
    corrupting the ACTUAL nested Q result bound set (distinct
    from the flat R-carried Q domain) or carrying a foreign-class
    flat R set refuses with the fixed private error BEFORE the
    real scope serializer/hash target is reached (the real target
    instrumented to count, never replaced by a function; the
    admission-to-R identity link is kept coherent in the negative
    copies so the bound gate, not the earlier identity join, is
    the refusal); the R-not-carried path closes the six
    P-namespace sets under their own fixed error."""
    ns, state = r_bootstrap(_MODE, "t018a-thirdparent")
    # The genuine stricter-Q-bounds positive through the public
    # operation (the legal stricter copy, never a model_copy).
    default_qb = RootRegionCurrentnessBounds()
    strict_qb = RootRegionCurrentnessBounds(
        max_total_work_units=max(1, default_qb.max_total_work_units // 2),
        max_diagnostics=max(1, default_qb.max_diagnostics // 2),
    )
    pos = derive_root_region_admission(state, ns, root_region_currentness_bounds=strict_qb)
    assert pos.outcome is RootRegionAdmissionOutcome.READY
    rr = pos.r_result
    assert rr is not None
    adm = pos.admission
    assert adm is not None
    assert adm.r_result is rr
    assert rr.q_bounds.max_total_work_units == strict_qb.max_total_work_units
    assert rr.q_bounds.max_diagnostics == strict_qb.max_diagnostics
    q = rr.q_result
    assert q is not None
    assert q.bounds.max_total_work_units == strict_qb.max_total_work_units
    assert q.bounds.max_diagnostics == strict_qb.max_diagnostics
    # Instrument the ACTUAL T scope serializer target (the real
    # function wrapped to count, never replaced by a fake).
    hits: list[int] = []
    real_scope = _result_models.root_region_admission_scope_key

    def _counting_scope(*args: Any, **kwargs: Any) -> str:
        hits.append(1)
        return real_scope(*args, **kwargs)

    monkeypatch.setattr(_result_models, "root_region_admission_scope_key", _counting_scope)
    # The genuine result revalidates at the third boundary with
    # the real scope serializer reached.
    revalidated = _result_models.RootRegionAdmissionResult.model_validate(pos)
    assert revalidated.outcome is RootRegionAdmissionOutcome.READY
    assert revalidated.r_result is not None
    assert revalidated.r_result.q_bounds.max_total_work_units == strict_qb.max_total_work_units
    assert len(hits) >= 1
    # (a) the ACTUAL nested Q result bound set corrupted (distinct
    # from the flat R-carried Q domain): the ACTUAL R boundary's
    # fixed bound-join error, BEFORE the real scope serializer.
    bad_qb = q.bounds.model_copy(update={"max_total_work_units": 0})
    q_bad = q.model_copy(update={"bounds": bad_qb})
    rr_bad = rr.model_copy(update={"q_result": q_bad})
    # the admission-to-R identity link is kept coherent (both point
    # at the swapped record) so the ACTUAL nested bound gate, not
    # the earlier identity join, is the refusal.
    adm_bad = adm.model_copy(update={"r_result": rr_bad})
    hits_a = len(hits)
    with pytest.raises(
        ValidationError,
        match="the Q result bounds must carry actual closed scalar fields",
    ):
        _result_models.RootRegionAdmissionResult.model_validate(
            pos.model_copy(update={"r_result": rr_bad, "admission": adm_bad})
        )
    assert len(hits) == hits_a
    # (b) a foreign-class flat R-carried set: the fixed eleven-set
    # error (the closed O(1) class fence), BEFORE the serializer.
    rr_foreign = rr.model_copy(update={"q_bounds": CurrentGraphBounds()})
    adm_foreign = adm.model_copy(update={"r_result": rr_foreign})
    hits_b = len(hits)
    with pytest.raises(
        ValidationError,
        match="the actual eleven carried bound sets must be closed scalar sets",
    ):
        _result_models.RootRegionAdmissionResult.model_validate(
            pos.model_copy(update={"r_result": rr_foreign, "admission": adm_foreign})
        )
    assert len(hits) == hits_b
    # (c) the R-not-carried path closes the six P-namespace sets
    # under their own fixed error, BEFORE the serializer.
    early = derive_root_region_admission(
        state, ns, bounds=RootRegionAdmissionBounds(max_total_work_units=65)
    )
    assert early.outcome is RootRegionAdmissionOutcome.REFUSED
    assert early.r_result is None
    ns_foreign_bounds = early.ns.model_copy(update={"bounds": object()})
    hits_c = len(hits)
    with pytest.raises(
        ValidationError,
        match="the carried P namespace bound sets must be closed scalar sets",
    ):
        _result_models.RootRegionAdmissionResult.model_validate(
            early.model_copy(update={"ns": ns_foreign_bounds})
        )
    assert len(hits) == hits_c


def test_c_overflow_tail_body_free(monkeypatch: pytest.MonkeyPatch) -> None:
    """C2: the terminal REFUSED record retains the ACTUAL
    returned R object by reference as bounded evidence WITHOUT
    admitting or authorizing its source: after the genuine public
    one-below crossing (the actual R READY result with its
    resolved source retained, no admission), revalidating the
    terminal record at the third carrying boundary closes the
    carried source-independent joins and NEVER re-enters the R
    source validator (the root-body content pass) -- the
    complete charged source law stays on the metered R-derivation
    and S-parent path.  The real target is wrapped to count,
    never replaced; the same public run's charged derivation
    passes prove the spy is live."""
    ns, state = r_bootstrap(_MODE, "t018a-tail")
    r0 = derive_root_region_admission(state, ns, bounds=RootRegionAdmissionBounds())
    assert r0.outcome is RootRegionAdmissionOutcome.READY
    w0 = r0.work_units
    hits: list[int] = []
    real_src = _graph_models._r_source_closed

    def _counting_source(src: Any) -> None:
        hits.append(1)
        real_src(src)

    monkeypatch.setattr(_graph_models, "_r_source_closed", _counting_source)
    below = derive_root_region_admission(
        state, ns, bounds=RootRegionAdmissionBounds(max_total_work_units=w0 - 1)
    )
    assert below.outcome is RootRegionAdmissionOutcome.REFUSED
    assert below.diagnostics == (RootRegionAdmissionDiagnostic.WORK_UNITS_OVER_BOUND,)
    assert below.admission is None
    rr = below.r_result
    assert rr is not None
    assert rr.outcome is RootRegionGraphOutcome.READY
    assert rr.resolved_source is not None
    live = len(hits)
    assert live > 0  # the spy is live on the charged derivation path
    # The terminal record revalidates at the third carrying
    # boundary WITHOUT re-entering the root body target.
    revalidated = _result_models.RootRegionAdmissionResult.model_validate(below)
    assert revalidated.outcome is RootRegionAdmissionOutcome.REFUSED
    assert revalidated.r_result is rr
    assert revalidated.admission is None
    assert len(hits) == live


# --- B. Version change / withdrawal / Q blocks at consumer level -------


def _assert_consumer_ready(
    r: RootRegionAdmissionResult,
    state: Any,
    ns: Any,
    root_digest: str,
) -> Any:
    """The mode-independent complete-consumer READY invariants
    (outcome, exact input retention, root-digest pins, supplier and
    admission joins, the accepted G counter law and honest same-run
    ledgers).  Entry counts may legitimately differ by mode; these
    identities may not."""
    assert r.outcome is RootRegionAdmissionOutcome.READY
    assert r.diagnostics == ()
    assert r.g_limitation is None
    assert r.state is state
    assert r.ns is ns
    assert r.revision == state.revision
    assert r.lineage_key == state.lineage_key
    rr = r.r_result
    assert rr is not None
    assert rr.outcome is RootRegionGraphOutcome.READY
    assert rr.state is state
    src = rr.resolved_source
    assert src is not None
    assert src.root_digest == root_digest
    adm = r.admission
    assert adm is not None
    assert adm.state is state
    assert adm.ns is ns
    assert adm.r_result is rr
    assert adm.root_entry.root_source is src
    assert adm.root_entry.root_digest == root_digest
    # The accepted G reverse-index/counter law (mode-independent):
    # the mandatory root entry is the +1 the G caps count, and the
    # reverse attempts are counted before dedup.
    assert adm.entries_retained == 1 + len(adm.entries)
    assert adm.member_occurrences_charged == 1 + sum(
        len(e.key_record.member_occurrences) for e in adm.entries
    )
    assert adm.reverse_association_attempts >= adm.member_occurrences_charged
    root_rows = [row for row in adm.path_associations if row.path == ROOT_FILENAME]
    assert len(root_rows) == 1
    assert root_rows[0].is_root is True
    assert adm.root_entry.content_key in root_rows[0].content_keys
    # Honest same-run counters under the ACTUAL effective bounds.
    assert 0 < r.r_work_units <= r.work_units <= r.bounds.max_total_work_units
    assert 0 < r.g_work_units <= r.g_bounds.max_total_work_units
    assert r.stage_work_units <= ns.graph_bounds.max_work_units
    assert src.root_byte_length <= r.entry_source_bytes
    assert r.entry_source_bytes <= r.g_bounds.max_total_entry_source_bytes
    return adm


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_b_revert_deliberate_old_bytes_ready_admission(mode: AdmissionMode, endpoint: str) -> None:
    """B1: the deliberate revert (a genuinely NEW issued/anchored
    region descendant carrying the OLD bootstrap bytes) READYs the
    complete public consumer: the read_region root pinned to the old
    bytes, the withdrawn v2 content no longer a current supplier, the
    retained root facts, and the admitted A.md FILE row with its exact
    single association key under the selected root."""
    ns, state = _revert_state(mode, endpoint, f"t018b-rev-{endpoint}")
    r = derive_root_region_admission(state, ns)
    adm = _assert_consumer_ready(r, state, ns, sha256_hex(ROOT_TEXT))
    rr = r.r_result
    assert rr is not None
    src = rr.resolved_source
    assert src is not None
    assert src.kind == "read_region"
    assert src.root_text == ROOT_TEXT
    # The retained root facts: the envelope bootstrap, the retained
    # v2 read and the new region read (nothing erased).
    assert len(state.root_facts) == 3
    assert sorted(f.provenance.kind for f in state.root_facts) == [
        "envelope",
        "read",
        "read_region",
    ]
    assert next(
        f for f in state.root_facts if f.provenance.kind == "read"
    ).source_digest == sha256_hex(V2)
    # The withdrawn v2 content is not a possessed current supplier;
    # the root path is pinned to the reverted bytes.
    f_result = rr.f_result
    assert f_result is not None
    overlay = f_result.overlay
    assert overlay is not None
    assert overlay.root_digest == sha256_hex(ROOT_TEXT)
    root_nodes = [n for n in overlay.nodes if n.path == ROOT_FILENAME]
    assert len(root_nodes) == 1
    assert root_nodes[0].status is CurrentGraphStatus.CURRENT_KNOWN
    assert root_nodes[0].digest == sha256_hex(ROOT_TEXT)
    assert all(
        n.digest != sha256_hex(V2)
        for n in overlay.nodes
        if n.status is CurrentGraphStatus.CURRENT_KNOWN
    )
    # The admitted A.md FILE row: exactly one association key.
    a_rows = [row for row in adm.path_associations if row.path == "A.md"]
    assert len(a_rows) == 1
    assert len(a_rows[0].content_keys) == 1
    assert a_rows[0].is_root is False


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_b_nonroot_version_change_key_rotation(mode: AdmissionMode, endpoint: str) -> None:
    """B2: a genuine nonroot version change under the UNCHANGED
    selected root: the root digest stays pinned, the A.md node digest
    rotates to the new bytes, the A.md association is exactly ONE key
    and CHANGED, the root-path keys form a superset, the old outgoing
    reference is withdrawn and the new one is discovered
    unacquired -- admission as well as graph results."""
    ns, s0 = _mixed_region_state(mode, endpoint, f"t018b-vchg-{endpoint}", a_text=A_OLD_TEXT)
    r0 = derive_root_region_admission(s0, ns)
    adm0 = _assert_consumer_ready(r0, s0, ns, sha256_hex(V2))
    rr0 = r0.r_result
    assert rr0 is not None
    a0 = [row for row in adm0.path_associations if row.path == "A.md"]
    assert len(a0) == 1
    assert len(a0[0].content_keys) == 1
    key0 = a0[0].content_keys[0]
    g0 = [row for row in adm0.path_associations if row.path == ROOT_FILENAME]
    assert len(g0) == 1
    assert rr0.f_result is not None
    ov0 = rr0.f_result.overlay
    assert ov0 is not None
    a0_nodes = [n for n in ov0.nodes if n.path == "A.md"]
    assert len(a0_nodes) == 1
    assert a0_nodes[0].status is CurrentGraphStatus.CURRENT_KNOWN
    assert a0_nodes[0].digest == sha256_hex(A_OLD_TEXT)
    assert any(
        n.path == "Old.md" and n.status is CurrentGraphStatus.DISCOVERED_UNACQUIRED
        for n in ov0.nodes
    )
    # A genuine new A.md version (descendant of m1) under the same
    # root bytes.
    m1 = next(o for o in s0.d_state.occurrences if o.call_id == "m1")
    t3 = r_issue(s0, ns, "m2", endpoint, (m1.occurrence_id,), MIX_CMD)
    assert t3.outcome.value == "accepted"
    t4 = r_observe(
        t3.state, ns, (read_request(endpoint, "m2", _mixed_body(A_NEW_TEXT, MARK, V2), MIX_CMD),)
    )
    assert t4.outcome.value == "accepted", t4.diagnostics
    s1 = t4.state
    r1 = derive_root_region_admission(s1, ns)
    adm1 = _assert_consumer_ready(r1, s1, ns, sha256_hex(V2))
    rr1 = r1.r_result
    assert rr1 is not None
    a1 = [row for row in adm1.path_associations if row.path == "A.md"]
    assert len(a1) == 1
    assert len(a1[0].content_keys) == 1
    key1 = a1[0].content_keys[0]
    assert key1 != key0
    g1 = [row for row in adm1.path_associations if row.path == ROOT_FILENAME]
    assert len(g1) == 1
    # The governing ROOT_ENTRY key persists across the version
    # change; the OLD mixed A+root canonical key (it bound the
    # old A.md member content) is withdrawn from the root row
    # and from EVERY row, and the NEW mixed key appears.
    rk = adm0.root_entry.content_key
    assert rk in g0[0].content_keys
    assert adm1.root_entry.content_key == rk
    assert rk in g1[0].content_keys
    assert key0 in g0[0].content_keys
    assert key0 not in g1[0].content_keys
    all_keys1 = {k for row in adm1.path_associations for k in row.content_keys}
    assert key0 not in all_keys1
    assert key1 in g1[0].content_keys
    assert rr1.f_result is not None
    ov1 = rr1.f_result.overlay
    assert ov1 is not None
    a1_nodes = [n for n in ov1.nodes if n.path == "A.md"]
    assert len(a1_nodes) == 1
    assert a1_nodes[0].digest == sha256_hex(A_NEW_TEXT)
    assert any(
        n.path == "New.md" and n.status is CurrentGraphStatus.DISCOVERED_UNACQUIRED
        for n in ov1.nodes
    )
    assert all(n.path != "Old.md" for n in ov1.nodes)


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_b_multi_source_version_withdrawal(mode: AdmissionMode, endpoint: str) -> None:
    """B3: a genuine new X.md version (a descendant of the original
    whole read) under the UNCHANGED envelope root: the X.md
    association rotates to exactly ONE changed key, the X.md node
    digest is the new bytes, the old version is no longer a current
    supplier, and the new reference is discovered unacquired."""
    ns, s0, original = _multi_source_state(mode, endpoint, f"t018b-multi-{endpoint}")
    r0 = derive_root_region_admission(s0, ns)
    adm0 = _assert_consumer_ready(r0, s0, ns, sha256_hex(V1_ROOT))
    rr0 = r0.r_result
    assert rr0 is not None
    src0 = rr0.resolved_source
    assert src0 is not None
    assert src0.kind == "envelope"
    assert src0.root_text == V1_ROOT
    x0 = [row for row in adm0.path_associations if row.path == "X.md"]
    assert len(x0) == 1
    assert len(x0[0].content_keys) == 1
    key0 = x0[0].content_keys[0]
    t3 = r_issue(s0, ns, "x2", endpoint, (original["x"].occurrence_id,), "cat X.md")
    assert t3.outcome.value == "accepted", t3.diagnostics
    t4 = r_observe(t3.state, ns, (read_request(endpoint, "x2", X_MD_NEW, "cat X.md"),))
    assert t4.outcome.value == "accepted", t4.diagnostics
    s1 = t4.state
    r1 = derive_root_region_admission(s1, ns)
    adm1 = _assert_consumer_ready(r1, s1, ns, sha256_hex(V1_ROOT))
    rr1 = r1.r_result
    assert rr1 is not None
    x1 = [row for row in adm1.path_associations if row.path == "X.md"]
    assert len(x1) == 1
    assert len(x1[0].content_keys) == 1
    key1 = x1[0].content_keys[0]
    assert key1 != key0
    assert rr1.f_result is not None
    ov1 = rr1.f_result.overlay
    assert ov1 is not None
    x1_nodes = [n for n in ov1.nodes if n.path == "X.md"]
    assert len(x1_nodes) == 1
    assert x1_nodes[0].status is CurrentGraphStatus.CURRENT_KNOWN
    assert x1_nodes[0].digest == sha256_hex(X_MD_NEW)
    assert any(
        n.path == "Replacement.md" and n.status is CurrentGraphStatus.DISCOVERED_UNACQUIRED
        for n in ov1.nodes
    )
    assert all(
        n.digest != sha256_hex(X_MD_OLD)
        for n in ov1.nodes
        if n.status is CurrentGraphStatus.CURRENT_KNOWN
    )


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_b_q_uncertainty_blocks_before_admission(mode: AdmissionMode, endpoint: str) -> None:
    """B4: Q uncertainty must block BEFORE admission: the two-branch
    frontier is unproven with the ACTUAL R evidence retained and no
    admission; a child of one branch cannot erase the other; the
    genuine joint equal-byte coverage restores READY under the
    original maximal witnesses (the A.md FILE entry retains BOTH
    original witnesses and no invented va<->vb edge exists)."""
    ns, s0, _v2 = _frontier_state(mode, endpoint, f"t018b-front-{endpoint}")
    r0 = derive_root_region_admission(s0, ns)
    assert r0.outcome is RootRegionAdmissionOutcome.ROOT_CURRENTNESS_UNPROVEN
    assert r0.diagnostics == ()
    assert r0.g_limitation is None
    assert r0.r_result is not None
    assert r0.r_result.outcome is RootRegionGraphOutcome.ROOT_CURRENTNESS_UNPROVEN
    assert r0.r_result.resolved_source is None
    assert r0.r_result.f_result is None
    assert r0.admission is None
    assert r0.state is s0
    assert r0.ns is ns
    assert r0.g_work_units == 0
    assert 0 < r0.work_units <= r0.bounds.max_total_work_units
    # A child of one opaque branch: still unproven, no admission.
    ua, ub = q_occ(s0, "ua"), q_occ(s0, "ub")
    s1 = q_observe(
        q_issue(s0, ns, "va", endpoint, Q_MIX_CMD, (ua.occurrence_id,)),
        ns,
        endpoint,
        "va",
        q_mixed_body(Q_A_TEXT, Q_MARK, "R4."),
        Q_MIX_CMD,
    )
    r1 = derive_root_region_admission(s1, ns)
    assert r1.outcome is RootRegionAdmissionOutcome.ROOT_CURRENTNESS_UNPROVEN
    assert r1.r_result is not None
    assert r1.r_result.resolved_source is None
    assert r1.admission is None
    va = q_occ(s1, "va")
    # The genuine joint coverage: equal 'R4.' root bytes descended
    # from BOTH maximal branches.
    s2 = q_observe(
        q_issue(s1, ns, "vb", endpoint, Q_MIX_CMD, (ub.occurrence_id,)),
        ns,
        endpoint,
        "vb",
        q_mixed_body(Q_A_TEXT, Q_MARK, "R4."),
        Q_MIX_CMD,
    )
    vb = q_occ(s2, "vb")
    links = {(link.child, link.parent) for link in s2.d_state.parent_links}
    assert (va.occurrence_id, ua.occurrence_id) in links
    assert (vb.occurrence_id, ub.occurrence_id) in links
    assert (va.occurrence_id, vb.occurrence_id) not in links
    assert (vb.occurrence_id, va.occurrence_id) not in links
    r2 = derive_root_region_admission(s2, ns)
    adm2 = _assert_consumer_ready(r2, s2, ns, sha256_hex("R4."))
    rr2 = r2.r_result
    assert rr2 is not None
    src2 = rr2.resolved_source
    assert src2 is not None
    assert src2.kind == "read_region"
    assert src2.root_text == "R4."
    # R4. references nothing, so A.md is graph-ineligible:
    # lean admits only the proven AGENTS.md segment (width 1)
    # while greedy retains the whole A+root bundle (width 2,
    # background A, never authority).  In BOTH modes the
    # root-bearing row carries the TWO original maximal R4.
    # witnesses (va and vb).
    root_rows = [row for row in adm2.path_associations if row.path == ROOT_FILENAME]
    assert len(root_rows) == 1
    if mode is AdmissionMode.LEAN:
        assert [row for row in adm2.path_associations if row.path == "A.md"] == []
        file_root_entries = [e for e in adm2.entries if e.content_key in root_rows[0].content_keys]
        assert len(file_root_entries) == 1
        assert file_root_entries[0].width == 1
        assert len(file_root_entries[0].witnesses) == 2
    else:
        a_rows = [row for row in adm2.path_associations if row.path == "A.md"]
        assert len(a_rows) == 1
        assert len(a_rows[0].content_keys) == 1
        assert a_rows[0].is_root is False
        bundle_key = a_rows[0].content_keys[0]
        assert bundle_key in root_rows[0].content_keys
        bundle_entries = [e for e in adm2.entries if e.content_key == bundle_key]
        assert len(bundle_entries) == 1
        assert bundle_entries[0].width == 2
        assert len(bundle_entries[0].witnesses) == 2
    # The original maximal witnesses stay retained on the actual Q
    # result (no evidence erased).
    q2 = rr2.q_result
    assert q2 is not None
    assert len(q2.uncertainty_witnesses) == 2
    assert {w.occurrence_id for w in q2.uncertainty_witnesses} == {
        ua.occurrence_id,
        ub.occurrence_id,
    }


def test_c_t_bounds_original_class() -> None:
    """C3: the consumer bound set is closed to the ORIGINAL class and
    ranges (the existing D1 boundary law on the NEW T bounds): the
    exact-cap original-class positive READYs; a shadow subclass
    refuses through the public derivation with the fixed
    malformed-binding diagnostic (no R result, no admission, no G
    channel); a bypass-copied result carrying the shadow class
    refuses at the carrying boundary with the fixed private error."""
    ns, state = r_bootstrap(_MODE, "t018c-class")
    r0 = derive_root_region_admission(state, ns, bounds=RootRegionAdmissionBounds())
    assert r0.outcome is RootRegionAdmissionOutcome.READY
    w0 = r0.work_units
    exact = derive_root_region_admission(
        state, ns, bounds=RootRegionAdmissionBounds(max_total_work_units=w0)
    )
    assert exact.outcome is RootRegionAdmissionOutcome.READY
    assert exact.work_units == w0
    assert exact.admission is not None

    class _ShadowBounds(RootRegionAdmissionBounds):
        pass

    shadow = derive_root_region_admission(state, ns, bounds=_ShadowBounds())
    assert shadow.outcome is RootRegionAdmissionOutcome.REFUSED
    assert shadow.diagnostics == (RootRegionAdmissionDiagnostic.MALFORMED_BINDING,)
    assert shadow.r_result is None
    assert shadow.admission is None
    assert shadow.g_limitation is None
    assert shadow.state is state
    assert shadow.ns is ns
    with pytest.raises(
        ValidationError,
        match="the consumer bounds must be closed under the original class and ranges",
    ):
        RootRegionAdmissionResult.model_validate(
            exact.model_copy(update={"bounds": _ShadowBounds()})
        )


# --- D. Local-cap discriminators at consumer level ----------------------


@pytest.mark.parametrize("fixture", ["envelope", "mixed"])
def test_d_g_subtree_below_entire(fixture: str) -> None:
    """D5: the real whole-operation/domain discriminators on genuine
    public positives: the ACTUAL G subtree (F + admission) is
    STRICTLY BELOW the entire operation cost in both shapes, its
    stage sits inside it, and the positive local-cap-less-than-
    entire-total case (the local G total capped at the default-run
    measured G cost) still READYs with the R derivation work
    unchanged."""
    if fixture == "envelope":
        ns, state = r_bootstrap(_MODE, "t018d-g-envelope")
    else:
        ns, state = _mixed_region_state(_MODE, _ENDPOINT, "t018d-g-mixed")
    base = derive_root_region_admission(state, ns, bounds=RootRegionAdmissionBounds())
    assert base.outcome is RootRegionAdmissionOutcome.READY
    wg = base.g_work_units
    assert 0 < base.r_work_units < base.work_units
    assert 0 < wg < base.work_units
    assert 0 < base.stage_work_units <= wg
    exact_g = derive_root_region_admission(
        state,
        ns,
        bounds=RootRegionAdmissionBounds(),
        admission_bounds=CurrentAdmissionBounds(max_total_work_units=wg),
    )
    assert exact_g.outcome is RootRegionAdmissionOutcome.READY
    assert exact_g.admission is not None
    assert 0 < exact_g.g_work_units <= wg
    assert exact_g.g_work_units < exact_g.work_units
    # The R derivation work is independent of the G subtree cap.
    assert exact_g.r_work_units == base.r_work_units
    assert exact_g.stage_work_units <= ns.graph_bounds.max_work_units


def test_d_q_local_first_over_before_target() -> None:
    """D6: the reachable Q local first-over BEFORE its target: a
    legal Q total of 1 crosses the ACTUAL Q derivation before any
    F/admission work, the public derivation REFUSES with the mapped
    R/Q refusal shape (the precise Q channel retained on the actual
    R evidence, NO consumer-own diagnostic invented, no G channel),
    and the honest counters show zero G-stage work and zero owned
    entry-source bytes."""
    ns, state = r_bootstrap(_MODE, "t018d-q1")
    r = derive_root_region_admission(
        state,
        ns,
        bounds=RootRegionAdmissionBounds(),
        root_region_currentness_bounds=RootRegionCurrentnessBounds(
            max_total_work_units=1,
            max_diagnostics=1,
        ),
    )
    assert r.outcome is RootRegionAdmissionOutcome.REFUSED
    assert r.diagnostics == ()
    assert r.g_limitation is None
    rr = r.r_result
    assert rr is not None
    assert rr.outcome is RootRegionGraphOutcome.REFUSED
    q = rr.q_result
    assert q is not None
    assert q.outcome is RootRegionCurrentnessOutcome.REFUSED
    assert rr.resolved_source is None
    assert rr.f_result is None
    assert r.admission is None
    assert r.g_work_units == 0
    assert r.stage_work_units == 0
    assert r.entry_source_bytes == 0
    assert 0 < r.r_work_units < r.work_units <= r.bounds.max_total_work_units


# --- E. Complete-operation source scale ----------------------------------


class _LedgerCollector:
    """Capture the ACTUAL same-run ledger references by non-invasive
    constructor wrappers: the real classes, real instances and real
    counters are preserved (nothing is subclassed or replaced); the
    wrappers only record references and measure the ACTUAL charged
    ledger deltas.  Each ``take()`` covers exactly ONE public
    derivation (the instances constructed since the previous take):
    a phase that never ran in this call reads ZERO, never a stale
    earlier object.  The retained (meter, ledger) references keep
    every ledger alive for the collector's lifetime, so the actual
    ledger IDs aggregated below can never be recycled into another
    ledger while the collector lives."""

    def __init__(self, monkeypatch: pytest.MonkeyPatch) -> None:
        self.monkeypatch = monkeypatch
        self.q_outers: list[Any] = []
        self.p_domains: list[Any] = []
        self.g_subtrees: list[Any] = []
        self.t_outers: list[Any] = []
        self.meter_ledgers: list[tuple[Any, Any]] = []
        self.ledger_charged: dict[int, int] = {}
        self._install()

    def _install(self) -> None:
        mp = self.monkeypatch

        def spy(class_: Any, bucket: list[Any]) -> None:
            real = class_.__init__

            def wrapped(self: Any, *args: Any, **kwargs: Any) -> None:
                real(self, *args, **kwargs)
                bucket.append(self)

            mp.setattr(class_, "__init__", wrapped)

        spy(_r_mod._RQOuter, self.q_outers)
        spy(_q_mod._QPAdapter, self.p_domains)
        spy(_t_mod._TSubtree, self.g_subtrees)
        spy(_t_mod._TOuter, self.t_outers)
        col = self
        real_mi = _t_mod._TMeter.__init__

        def meter_init(self: Any, ledger: Any, *args: Any, **kwargs: Any) -> None:
            real_mi(self, ledger, *args, **kwargs)
            col.meter_ledgers.append((self, ledger))

        mp.setattr(_t_mod._TMeter, "__init__", meter_init)
        real_reserve = _t_mod._TMeter.reserve

        def meter_reserve(self: Any, units: int) -> None:
            ledger = self._ledger
            before = ledger.work_spent
            try:
                real_reserve(self, units)
            finally:
                # the ACTUAL charged delta of the real ledger
                # (a partial refusal charges less than the
                # attempted units; a crossed refusal charges what
                # it charged before raising):
                col.ledger_charged[id(ledger)] = col.ledger_charged.get(id(ledger), 0) + (
                    ledger.work_spent - before
                )

        mp.setattr(_t_mod._TMeter, "reserve", meter_reserve)

    def take(self) -> dict[str, int]:
        """The actual counters of THIS derivation only: the Q total
        (with the coupled actual P phase), the independent P-domain
        outer, the F subtree under the G outer, the G subtree total,
        and the ACTUAL charged S-component validation reservations
        split between the T entire outer and the G subtree ledger
        (a phase absent from this call reads ZERO)."""
        q = sum(x.work_spent for x in self.q_outers)
        p = sum(x.work_spent for x in self.p_domains)
        g_list = list(self.g_subtrees)
        g = g_list[-1] if g_list else None
        f = sum(x.f_work_spent for x in g_list)
        t = self.t_outers[-1] if self.t_outers else None
        val_t = self.ledger_charged.get(id(t), 0) if t is not None else 0
        val_g = self.ledger_charged.get(id(g), 0) if g is not None else 0
        # bind the next take() to the NEXT derivation: the spy
        # closures append into these SAME list objects, so clear
        # in place (a rebind would detach the live observers):
        self.q_outers.clear()
        self.p_domains.clear()
        self.g_subtrees.clear()
        self.t_outers.clear()
        return {
            "q_outer_work": q,
            "p_domain_work": p,
            "f_subtree_work": f,
            "g_subtree_work": g.work_spent if g is not None else 0,
            "validation_t_outer": val_t,
            "validation_g_subtree": val_g,
        }


def _t_e_record(
    shape: str,
    mode: Any,
    endpoint: Any,
    nbytes: int,
    outcome: str,
    extra: dict[str, Any],
) -> None:
    """Record the per-shape actual E result in the protected test
    output (stdout capture; no host IO)."""
    rec = {
        "shape": shape,
        "mode": mode.value,
        "endpoint": endpoint,
        "root_bytes": nbytes,
        "outcome": outcome,
    }
    rec.update(extra)
    print("t-e-record " + json.dumps(rec, sort_keys=True))


def _t_e_mixed_state(
    mode: Any, endpoint: str, lineage: str, nbytes: int, graph_bounds: Any = None
) -> tuple[Any, Any]:
    """ONE genuine public P mixed-region (no singleton) state whose
    selected root region references A.md, at the given root-member
    byte scale."""
    header = "Follow `A.md`.\n"
    body = header + "x" * (nbytes - len(header))
    assert len(body.encode("utf-8")) == nbytes
    if graph_bounds is None:
        ns, s0 = r_bootstrap(mode, lineage)
    else:
        ns, s0 = r_bootstrap(mode, lineage, graph_bounds=graph_bounds)
    t1 = r_issue(s0, ns, "m1", endpoint, (CAUSAL_ROOT_FACT,), MIX_CMD)
    assert t1.outcome.value == "accepted", t1.diagnostics
    obs = r_observe(
        t1.state, ns, (read_request(endpoint, "m1", _mixed_body(A_TEXT, MARK, body), MIX_CMD),)
    )
    assert obs.outcome.value == "accepted", obs.diagnostics
    return ns, obs.state


def _t_e_dep_read(state: Any, ns: Any, cid: str, endpoint: str, path: str, body: str) -> Any:
    issued = r_issue(state, ns, cid, endpoint, (CAUSAL_ROOT_FACT,), f"cat {path}")
    assert issued.outcome.value == "accepted", issued.diagnostics
    obs = r_observe(issued.state, ns, (read_request(endpoint, cid, body, f"cat {path}"),))
    assert obs.outcome.value == "accepted", obs.diagnostics
    return obs.state


def _t_e_multi_dep_state(
    mode: Any, endpoint: str, lineage: str, graph_bounds: Any = None
) -> tuple[Any, Any, str, str]:
    """The genuine multi-dependency / version-history shape at the
    32768 root-member byte scale (v2 is the selected newer root).
    Returns (ns, state, expected_v2_body, expected_v2_digest): the
    expected selected-source identity is retained from the fixture
    itself because v1 and v2 share the same references and byte
    scale (the length/row assertions alone cannot distinguish a
    failed refresh from the genuine v2 selection)."""
    header = "Follow `A.md` and `X.md`.\n"
    v1 = header + "x" * (32768 - len(header))
    v2_header = header + "Version two.\n"
    v2 = v2_header + "x" * (32768 - len(v2_header))
    assert len(v1.encode("utf-8")) == 32768 and len(v2.encode("utf-8")) == 32768
    if graph_bounds is None:
        ns, state = r_bootstrap(mode, lineage, root_body=v1)
    else:
        ns, state = r_bootstrap(mode, lineage, root_body=v1, graph_bounds=graph_bounds)
    state = _t_e_dep_read(state, ns, "a", endpoint, "A.md", "Follow `X.md`.\n")
    state = _t_e_dep_read(state, ns, "x", endpoint, "X.md", "Follow `Target.md`.\n")
    state = _t_e_dep_read(state, ns, "t", endpoint, "Target.md", "Synthetic target governance.\n")
    state = _t_e_dep_read(state, ns, "root2", endpoint, ROOT_FILENAME, v2)
    return ns, state, v2, sha256_hex(v2)


@pytest.mark.parametrize("mode", MODES)
def test_e_root_only_scale_outcomes_and_costs(
    mode: AdmissionMode, monkeypatch: pytest.MonkeyPatch
) -> None:
    """E1: the root-only (envelope) complete operation at 32768/
    65536/131072 UTF-8 root bytes (both modes): ACTUAL READY at
    32768/65536 under the original single-source 1000000 and
    entry-source 16777216 byte domains, with the whole/R/Q/P/F/
    G-stage/validation actual same-run ledger costs and the
    effective configuration recorded per shape; 131072 is recorded
    HONESTLY as the actual R-total refusal (the F OK result
    retained, no usable source, no admission, no G channel).  Whole
    and G costs are monotone in the actual source bytes."""
    col = _LedgerCollector(monkeypatch)
    work_by: dict[int, int] = {}
    g_by: dict[int, int] = {}
    for nbytes in (32768, 65536, 131072):
        body = "x" * nbytes
        assert len(body.encode("utf-8")) == nbytes
        ns, state = r_bootstrap(mode, f"t018e-ro-{mode.value}-{nbytes}", root_body=body)
        r = derive_root_region_admission(state, ns, bounds=RootRegionAdmissionBounds())
        measured = col.take()
        if nbytes <= 65536:
            assert r.outcome is RootRegionAdmissionOutcome.READY
            rr = r.r_result
            assert rr is not None and rr.outcome is RootRegionGraphOutcome.READY
            resolved = rr.resolved_source
            assert resolved is not None and resolved.kind == "envelope"
            assert resolved.root_byte_length == nbytes
            assert ns.graph_bounds.max_single_source_bytes == 1_000_000
            assert nbytes <= ns.graph_bounds.max_single_source_bytes
            assert r.g_bounds.max_total_entry_source_bytes == 16_777_216
            assert nbytes <= r.g_bounds.max_total_entry_source_bytes
            assert 0 < r.r_work_units < r.work_units <= r.bounds.max_total_work_units
            assert 0 < r.g_work_units < r.work_units
            assert 0 < r.stage_work_units <= r.g_work_units
            # the actual same-run ledger decomposition is closed:
            assert 0 < measured["p_domain_work"] <= measured["q_outer_work"]
            assert measured["q_outer_work"] <= r.r_work_units
            assert 0 < measured["f_subtree_work"] <= r.g_work_units
            assert measured["g_subtree_work"] == r.g_work_units
            assert measured["validation_t_outer"] > 0
            assert measured["validation_g_subtree"] > 0
            adm = r.admission
            assert adm is not None
            assert adm.entries == ()
            assert adm.entries_retained == 1
            assert adm.member_occurrences_charged == 1
            work_by[nbytes] = r.work_units
            g_by[nbytes] = r.g_work_units
            _t_e_record(
                "root_only",
                mode,
                None,
                nbytes,
                "ready",
                {
                    "work_units": r.work_units,
                    "r_work_units": r.r_work_units,
                    "g_work_units": r.g_work_units,
                    "stage_work_units": r.stage_work_units,
                    "entry_source_bytes": r.entry_source_bytes,
                    "q_outer_work": measured["q_outer_work"],
                    "p_domain_work": measured["p_domain_work"],
                    "f_subtree_work": measured["f_subtree_work"],
                    "validation_t_outer": measured["validation_t_outer"],
                    "validation_g_subtree": measured["validation_g_subtree"],
                    "single_source_cap": ns.graph_bounds.max_single_source_bytes,
                    "entry_byte_cap": r.g_bounds.max_total_entry_source_bytes,
                    "stage_cap": ns.graph_bounds.max_work_units,
                    "g_cap": r.g_bounds.max_total_work_units,
                    "t_cap": r.bounds.max_total_work_units,
                    "entries_retained": adm.entries_retained,
                    "member_occurrences_charged": adm.member_occurrences_charged,
                },
            )
        else:
            assert r.outcome is RootRegionAdmissionOutcome.REFUSED
            assert r.diagnostics == (RootRegionAdmissionDiagnostic.WORK_UNITS_OVER_BOUND,)
            assert r.g_limitation is None
            rr = r.r_result
            assert rr is not None
            assert rr.outcome is RootRegionGraphOutcome.REFUSED
            assert rr.diagnostics == (RootRegionGraphDiagnostic.WORK_UNITS_OVER_BOUND,)
            assert rr.resolved_source is None
            assert rr.f_result is not None and rr.f_result.outcome is CurrentGraphOutcome.OK
            assert rr.q_result is not None
            assert rr.q_result.outcome is RootRegionCurrentnessOutcome.READY
            assert r.admission is None
            assert r.entry_source_bytes == 0
            assert r.work_units <= r.bounds.max_total_work_units
            _t_e_record(
                "root_only",
                mode,
                None,
                nbytes,
                "refused_r_total",
                {
                    "work_units": r.work_units,
                    "r_work_units": r.r_work_units,
                    "g_work_units": r.g_work_units,
                    "stage_work_units": r.stage_work_units,
                    "q_outer_work": measured["q_outer_work"],
                    "p_domain_work": measured["p_domain_work"],
                    "f_subtree_work": measured["f_subtree_work"],
                    "validation_t_outer": measured["validation_t_outer"],
                    "validation_g_subtree": measured["validation_g_subtree"],
                    "single_source_cap": ns.graph_bounds.max_single_source_bytes,
                    "f_retained": "ok",
                    "usable_source": False,
                },
            )
    assert work_by[65536] > work_by[32768]
    assert g_by[65536] > g_by[32768]


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_e_mixed_region_no_singleton_scale(
    mode: AdmissionMode, endpoint: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    """E2: the mixed-region no-singleton complete operation at
    32768/65536/131072 UTF-8 root bytes (both modes, BOTH read
    endpoints): the source SIZE domains accept the scale, but the
    original DEFAULT admission stage-work domain (65536) exhausts on
    the actual root-member span (the typed G stage refusal with the
    ACTUAL R READY result retained and no admission); the LEGAL
    instance of that original stage domain (1048576, the unchanged
    hard range) carries the complete operation READY with the one
    A.md FILE entry and all actual same-run costs recorded; 65536
    under the legal stage honestly refuses at the UNCHANGED G-total
    hard ceiling; 131072 honestly refuses at the R total BEFORE F."""
    col = _LedgerCollector(monkeypatch)
    legal_stage = GraphBounds(max_work_units=1_048_576)
    for nbytes in (32768, 65536):
        # (a) the ORIGINAL default stage-work domain: honest refusal.
        ns, s_m = _t_e_mixed_state(
            mode, endpoint, f"t018e-mx-{mode.value}-{endpoint}-{nbytes}", nbytes
        )
        r = derive_root_region_admission(s_m, ns, bounds=RootRegionAdmissionBounds())
        measured = col.take()
        assert r.outcome is RootRegionAdmissionOutcome.REFUSED
        assert r.diagnostics == (RootRegionAdmissionDiagnostic.ADMISSION_OVER_BOUND,)
        assert r.g_limitation is CurrentAdmissionLimitation.ADMISSION_WORK_UNITS_EXHAUSTED
        rr = r.r_result
        assert rr is not None and rr.outcome is RootRegionGraphOutcome.READY
        resolved = rr.resolved_source
        assert resolved is not None and resolved.kind == "read_region"
        assert resolved.root_byte_length == nbytes
        assert r.admission is None
        assert r.entry_source_bytes == 0
        assert r.stage_work_units == ns.graph_bounds.max_work_units
        assert measured["g_subtree_work"] == r.g_work_units
        assert 0 < measured["q_outer_work"] <= r.r_work_units
        _t_e_record(
            "mixed_region",
            mode,
            endpoint,
            nbytes,
            "refused_g_stage_default",
            {
                "work_units": r.work_units,
                "r_work_units": r.r_work_units,
                "g_work_units": r.g_work_units,
                "stage_work_units": r.stage_work_units,
                "q_outer_work": measured["q_outer_work"],
                "p_domain_work": measured["p_domain_work"],
                "f_subtree_work": measured["f_subtree_work"],
                "stage_cap": ns.graph_bounds.max_work_units,
                "single_source_cap": ns.graph_bounds.max_single_source_bytes,
                "entry_byte_cap": r.g_bounds.max_total_entry_source_bytes,
                "g_cap": r.g_bounds.max_total_work_units,
            },
        )
        if nbytes == 32768:
            # (b) the LEGAL instance of the original stage domain:
            # the complete operation READYs.
            ns2, s_m2 = _t_e_mixed_state(
                mode,
                endpoint,
                f"t018e-mx-{mode.value}-{endpoint}-{nbytes}-stage",
                nbytes,
                graph_bounds=legal_stage,
            )
            r2 = derive_root_region_admission(s_m2, ns2, bounds=RootRegionAdmissionBounds())
            measured2 = col.take()
            assert r2.outcome is RootRegionAdmissionOutcome.READY
            rr2 = r2.r_result
            assert rr2 is not None and rr2.outcome is RootRegionGraphOutcome.READY
            assert rr2.resolved_source is not None
            assert rr2.resolved_source.root_byte_length == nbytes
            assert ns2.graph_bounds.max_work_units == 1_048_576
            assert ns2.graph_bounds.max_single_source_bytes == 1_000_000
            assert r2.g_bounds.max_total_entry_source_bytes == 16_777_216
            assert 0 < r2.r_work_units < r2.work_units <= r2.bounds.max_total_work_units
            assert 0 < r2.g_work_units < r2.work_units
            # the R derivation work is independent of the stage cap:
            assert r2.r_work_units == r.r_work_units
            assert 0 < measured2["f_subtree_work"] <= r2.g_work_units
            assert measured2["validation_g_subtree"] > 0
            assert measured2["validation_t_outer"] > 0
            adm = r2.admission
            assert adm is not None
            assert [row.path for row in adm.path_associations] == ["A.md", ROOT_FILENAME]
            assert len(adm.entries) == 1
            assert adm.entries_retained == 1 + len(adm.entries)
            assert adm.member_occurrences_charged == 1 + sum(
                len(e.key_record.member_occurrences) for e in adm.entries
            )
            _t_e_record(
                "mixed_region",
                mode,
                endpoint,
                nbytes,
                "ready_legal_stage",
                {
                    "work_units": r2.work_units,
                    "r_work_units": r2.r_work_units,
                    "g_work_units": r2.g_work_units,
                    "stage_work_units": r2.stage_work_units,
                    "entry_source_bytes": r2.entry_source_bytes,
                    "q_outer_work": measured2["q_outer_work"],
                    "p_domain_work": measured2["p_domain_work"],
                    "f_subtree_work": measured2["f_subtree_work"],
                    "validation_t_outer": measured2["validation_t_outer"],
                    "validation_g_subtree": measured2["validation_g_subtree"],
                    "stage_cap": ns2.graph_bounds.max_work_units,
                    "g_cap": r2.g_bounds.max_total_work_units,
                    "entries_retained": adm.entries_retained,
                    "member_occurrences_charged": adm.member_occurrences_charged,
                    "reverse_association_attempts": adm.reverse_association_attempts,
                },
            )
        else:
            # 65536 under the legal stage: honest refusal at the
            # UNCHANGED G-total hard ceiling (not the stage).
            ns3, s_m3 = _t_e_mixed_state(
                mode,
                endpoint,
                f"t018e-mx-{mode.value}-{endpoint}-{nbytes}-stage",
                nbytes,
                graph_bounds=legal_stage,
            )
            r3 = derive_root_region_admission(s_m3, ns3, bounds=RootRegionAdmissionBounds())
            measured3 = col.take()
            assert r3.outcome is RootRegionAdmissionOutcome.REFUSED
            assert r3.diagnostics == (RootRegionAdmissionDiagnostic.ADMISSION_OVER_BOUND,)
            assert r3.g_limitation is CurrentAdmissionLimitation.TOTAL_WORK_UNITS_OVER_BOUND
            assert r3.g_work_units == r3.g_bounds.max_total_work_units
            assert r3.admission is None
            assert r3.entry_source_bytes == 0
            assert r3.stage_work_units < ns3.graph_bounds.max_work_units
            assert measured3["g_subtree_work"] == r3.g_work_units
            _t_e_record(
                "mixed_region",
                mode,
                endpoint,
                nbytes,
                "refused_g_total_legal_stage",
                {
                    "work_units": r3.work_units,
                    "r_work_units": r3.r_work_units,
                    "g_work_units": r3.g_work_units,
                    "stage_work_units": r3.stage_work_units,
                    "q_outer_work": measured3["q_outer_work"],
                    "f_subtree_work": measured3["f_subtree_work"],
                    "stage_cap": ns3.graph_bounds.max_work_units,
                    "g_cap": r3.g_bounds.max_total_work_units,
                },
            )
    # 131072: the honest R-total refusal BEFORE F.
    ns4, s_m4 = _t_e_mixed_state(mode, endpoint, f"t018e-mx-{mode.value}-{endpoint}-131072", 131072)
    r4 = derive_root_region_admission(s_m4, ns4, bounds=RootRegionAdmissionBounds())
    measured4 = col.take()
    assert r4.outcome is RootRegionAdmissionOutcome.REFUSED
    assert r4.diagnostics == (RootRegionAdmissionDiagnostic.WORK_UNITS_OVER_BOUND,)
    assert r4.g_limitation is None
    rr4 = r4.r_result
    assert rr4 is not None
    assert rr4.outcome is RootRegionGraphOutcome.REFUSED
    assert rr4.resolved_source is None
    assert rr4.f_result is None
    assert rr4.q_result is not None
    assert rr4.q_result.outcome is RootRegionCurrentnessOutcome.READY
    assert r4.admission is None
    assert r4.g_work_units == 0
    assert r4.entry_source_bytes == 0
    _t_e_record(
        "mixed_region",
        mode,
        endpoint,
        131072,
        "refused_r_total_before_f",
        {
            "work_units": r4.work_units,
            "r_work_units": r4.r_work_units,
            "q_outer_work": measured4["q_outer_work"],
            "p_domain_work": measured4["p_domain_work"],
            "f_retained": None,
            "usable_source": False,
        },
    )


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_e_multi_dependency_history_scale(
    mode: AdmissionMode, endpoint: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    """E3: the multi-dependency / version-history complete
    operation at the 32768 root-member byte scale (both modes, both
    endpoints): the same honest original-domain record as the
    mixed-region shape (the default admission stage-work domain
    exhausts on the actual root-member span; the legal instance of
    that original stage domain carries the complete operation
    READY), with the ACTUAL selected source pinned to the genuine
    v2 root read (body/digest/original proof identity, not just the
    shared byte scale) and all actual same-run costs recorded."""
    col = _LedgerCollector(monkeypatch)
    legal_stage = GraphBounds(max_work_units=1_048_576)
    # (a) the ORIGINAL default stage-work domain record:
    ns, state, v2_body, v2_digest = _t_e_multi_dep_state(
        mode, endpoint, f"t018e-md-{mode.value}-{endpoint}"
    )
    r = derive_root_region_admission(state, ns, bounds=RootRegionAdmissionBounds())
    measured = col.take()
    assert r.outcome is RootRegionAdmissionOutcome.REFUSED
    assert r.diagnostics == (RootRegionAdmissionDiagnostic.ADMISSION_OVER_BOUND,)
    assert r.g_limitation is CurrentAdmissionLimitation.ADMISSION_WORK_UNITS_EXHAUSTED
    rr = r.r_result
    assert rr is not None and rr.outcome is RootRegionGraphOutcome.READY
    resolved = rr.resolved_source
    assert resolved is not None
    # the ACTUAL selected source is the genuinely new v2 root read
    # (v1 and v2 share the same references and byte scale, so the
    # fixture body/digest/proof identity pins the real refresh):
    assert resolved.kind == "read"
    assert resolved.root_text == v2_body
    assert resolved.root_digest == v2_digest
    assert resolved.root_byte_length == 32768
    root2_occ = next(o for o in state.d_state.occurrences if o.call_id == "root2")
    assert resolved.occurrence is not None and resolved.proof is not None
    assert resolved.occurrence is root2_occ
    assert resolved.proof is root2_occ.proof
    assert r.admission is None
    assert r.entry_source_bytes == 0
    assert r.stage_work_units == ns.graph_bounds.max_work_units
    _t_e_record(
        "multi_dependency_history",
        mode,
        endpoint,
        32768,
        "refused_g_stage_default",
        {
            "work_units": r.work_units,
            "r_work_units": r.r_work_units,
            "g_work_units": r.g_work_units,
            "stage_work_units": r.stage_work_units,
            "q_outer_work": measured["q_outer_work"],
            "p_domain_work": measured["p_domain_work"],
            "f_subtree_work": measured["f_subtree_work"],
            "stage_cap": ns.graph_bounds.max_work_units,
            "g_cap": r.g_bounds.max_total_work_units,
            "selected_root_digest": v2_digest,
        },
    )
    # (b) the LEGAL instance of the original stage domain:
    ns2, state2, v2_body2, v2_digest2 = _t_e_multi_dep_state(
        mode,
        endpoint,
        f"t018e-md-{mode.value}-{endpoint}-stage",
        graph_bounds=legal_stage,
    )
    r2 = derive_root_region_admission(state2, ns2, bounds=RootRegionAdmissionBounds())
    measured2 = col.take()
    assert r2.outcome is RootRegionAdmissionOutcome.READY
    rr2 = r2.r_result
    assert rr2 is not None and rr2.outcome is RootRegionGraphOutcome.READY
    resolved2 = rr2.resolved_source
    assert resolved2 is not None
    assert resolved2.kind == "read"
    assert resolved2.root_text == v2_body2
    assert resolved2.root_digest == v2_digest2
    assert resolved2.root_byte_length == 32768
    root2_occ2 = next(o for o in state2.d_state.occurrences if o.call_id == "root2")
    assert resolved2.occurrence is not None and resolved2.proof is not None
    assert resolved2.occurrence is root2_occ2
    assert resolved2.proof is root2_occ2.proof
    assert 0 < measured2["f_subtree_work"] <= r2.g_work_units
    assert measured2["validation_g_subtree"] > 0
    assert measured2["validation_t_outer"] > 0
    adm = r2.admission
    assert adm is not None
    dep_paths = {row.path for row in adm.path_associations if not row.is_root}
    assert {"A.md", "X.md", "Target.md"} <= dep_paths
    assert adm.entries_retained == 1 + len(adm.entries)
    assert adm.member_occurrences_charged == 1 + sum(
        len(e.key_record.member_occurrences) for e in adm.entries
    )
    _t_e_record(
        "multi_dependency_history",
        mode,
        endpoint,
        32768,
        "ready_legal_stage",
        {
            "work_units": r2.work_units,
            "r_work_units": r2.r_work_units,
            "g_work_units": r2.g_work_units,
            "stage_work_units": r2.stage_work_units,
            "entry_source_bytes": r2.entry_source_bytes,
            "q_outer_work": measured2["q_outer_work"],
            "p_domain_work": measured2["p_domain_work"],
            "f_subtree_work": measured2["f_subtree_work"],
            "validation_t_outer": measured2["validation_t_outer"],
            "validation_g_subtree": measured2["validation_g_subtree"],
            "stage_cap": ns2.graph_bounds.max_work_units,
            "entries_retained": adm.entries_retained,
            "member_occurrences_charged": adm.member_occurrences_charged,
            "reverse_association_attempts": adm.reverse_association_attempts,
            "selected_root_digest": v2_digest2,
        },
    )


# --- F. Purity, scope-versus-revision, exact retention -------------------

_F_ROOT_BODY = "PRIVATE-ROOT-018T. Read `A.md`."
_F_NONROOT = "PRIVATE-NONROOT-018T. " + MARK + " end.\n"
_F_CALL_ID = "f-purity-call-018t"
_F_MODEL_ID = "canary-model-018t"
_F_IDENTITY = RequestIdentity(
    principal="canary-principal-018t",
    session="canary-session-018t",
    repository="canary-repo-018t",
    route="canary-route-018t",
)
_F_CANARIES = (
    _F_ROOT_BODY,
    _F_NONROOT,
    _F_CALL_ID,
    MARK,
    _F_MODEL_ID,
    "canary-principal-018t",
    "canary-session-018t",
    "canary-repo-018t",
    "canary-route-018t",
)


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_f_scope_deterministic_and_revision_separate(mode: AdmissionMode, endpoint: str) -> None:
    """F1: the consumer scope key is deterministic and binds the
    ACTUAL lineage/version/bounds context, NOT the carried revision:
    two derivations of the SAME state agree; a genuine
    revision-advancing transition on the SAME lineage and bounds
    keeps the stable scope key while the revision join and the
    admission content move; a derivation-only bounds change moves
    the scope key while the canonical C content key and the
    canonical payload DATA stay byte-identical."""
    ns, s1 = r_bootstrap(mode, f"t018f-sc-{endpoint}")
    base = RootRegionAdmissionBounds()
    r1a = derive_root_region_admission(s1, ns, bounds=base)
    r1b = derive_root_region_admission(s1, ns, bounds=base)
    assert r1a.outcome is RootRegionAdmissionOutcome.READY
    assert r1a.scope_key == r1b.scope_key
    # a genuine revision advance on the SAME lineage and bounds:
    s2 = _t_e_dep_read(s1, ns, "fa", endpoint, "A.md", "Ordinary F1.\n")
    # the issue and the observe are TWO accepted D transitions
    # (each advances the revision exactly once):
    assert s2.revision == s1.revision + 2
    r2 = derive_root_region_admission(s2, ns, bounds=base)
    assert r2.outcome is RootRegionAdmissionOutcome.READY
    # the stable scope key is unchanged (the revision is a separate
    # join, never a scope ingredient):
    assert r2.scope_key == r1a.scope_key
    assert r2.revision == s2.revision
    assert r1a.revision == s1.revision
    assert r2.revision != r1a.revision
    # the admission content moved with the genuine evidence:
    adm1 = r1a.admission
    adm2 = r2.admission
    assert adm1 is not None and adm2 is not None
    assert adm1.entries == ()
    assert len(adm2.entries) >= 1
    # the canonical C content key and canonical payload DATA are
    # stable across the genuine content change of the NONROOT member
    # (the root key is bound to the selected governing root digest,
    # which did not change):
    assert adm2.root_entry.content_key == adm1.root_entry.content_key
    # derivation-only bounds change: the scope key moves, the
    # canonical content key and payload DATA do not:
    strict = RootRegionAdmissionBounds(max_total_work_units=r1a.work_units)
    r3 = derive_root_region_admission(s1, ns, bounds=strict)
    assert r3.outcome is RootRegionAdmissionOutcome.READY
    assert r3.scope_key != r1a.scope_key
    assert r3.admission is not None
    assert r3.admission.root_entry.content_key == adm1.root_entry.content_key
    payload1 = json.dumps(adm1.root_entry.key_record.model_dump(mode="json"), sort_keys=True)
    payload3 = json.dumps(
        r3.admission.root_entry.key_record.model_dump(mode="json"), sort_keys=True
    )
    assert payload1 == payload3
    assert r3.admission.state is s1
    assert r3.admission.r_result is r3.r_result


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_f_exact_input_and_original_reference_retention(mode: AdmissionMode, endpoint: str) -> None:
    """F2: exact input retention and original-reference identity on
    the complete result: the actual P state/namespace/revision/
    lineage joins, the explicit bounds instance, the R result state
    join, the admission-parent joins (state/ns/r_result by
    identity), the root entry's ACTUAL resolved source by identity,
    and every FILE entry's proof by identity from the SAME wrapped
    D state (never a copied original)."""
    ns, state, _v2_body, _v2_digest = _t_e_multi_dep_state(
        mode,
        endpoint,
        f"t018f-rt-{endpoint}",
        graph_bounds=GraphBounds(max_work_units=1_048_576),
    )
    bounds = RootRegionAdmissionBounds()
    r = derive_root_region_admission(state, ns, bounds=bounds)
    assert r.outcome is RootRegionAdmissionOutcome.READY
    assert r.state is state
    assert r.ns is ns
    assert r.revision == state.revision
    assert r.lineage_key == state.lineage_key
    # the explicit bounds are legal by VALUE (the resolved
    # bound model carries exactly these caps):
    assert r.bounds == bounds
    rr = r.r_result
    assert rr is not None
    assert rr.state is state
    assert rr.revision == state.revision
    assert rr.lineage_key == state.lineage_key
    adm = r.admission
    assert adm is not None
    assert adm.state is state
    assert adm.ns is ns
    assert adm.r_result is rr
    src = rr.resolved_source
    assert src is not None
    assert adm.root_entry.root_source is src
    assert adm.root_entry.root_digest == src.root_digest
    # every FILE entry retains the ACTUAL retained original proof
    # by identity, joined through the entry's ACTUAL witness
    # coordinates (member_occurrences are PATHS, never occurrence
    # IDs): the proof is the proof of one of the witnessed
    # original occurrences, and every witness coordinates a
    # genuine retained occurrence of the SAME wrapped D state:
    by_occ = {o.occurrence_id: o for o in state.d_state.occurrences}
    assert adm.entries
    for entry in adm.entries:
        assert entry.proof is not None
        assert entry.witnesses
        for w in entry.witnesses:
            assert w.occurrence_id in by_occ
        assert any(by_occ[w.occurrence_id].proof is entry.proof for w in entry.witnesses)
    # the genuine dependency reads are all retained: the original
    # occurrence proof of each is the retained proof of at least
    # one admitted entry (identity, not value membership):
    for cid in ("a", "x", "t"):
        occ = next(o for o in state.d_state.occurrences if o.call_id == cid)
        assert any(e.proof is occ.proof for e in adm.entries)


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_f_canaries_absent_from_renderings_and_errors(mode: AdmissionMode, endpoint: str) -> None:
    """F3: no raw root/nonroot/marker/ID/model/identity canary
    appears in ANY tested rendering of the complete result (genuine
    READY and the genuine refusal) or in the fixed private bypass-
    copy error, while the canaries genuinely ride the ACTUAL
    carried state (the negative is not vacuous)."""
    ns, s0 = r_bootstrap(
        mode,
        f"t018f-cy-{endpoint}",
        root_body=_F_ROOT_BODY,
        identity=_F_IDENTITY,
        model_identity=_F_MODEL_ID,
    )
    t1 = r_issue(s0, ns, _F_CALL_ID, endpoint, (CAUSAL_ROOT_FACT,), "cat A.md")
    assert t1.outcome.value == "accepted", t1.diagnostics
    obs1 = r_observe(
        t1.state,
        ns,
        (read_request(endpoint, _F_CALL_ID, _F_NONROOT, "cat A.md"),),
    )
    assert obs1.outcome.value == "accepted", obs1.diagnostics
    s1 = obs1.state
    r = derive_root_region_admission(s1, ns, bounds=RootRegionAdmissionBounds())
    assert r.outcome is RootRegionAdmissionOutcome.READY
    # the canaries really ride the actual carried state:
    occ = next(o for o in s1.d_state.occurrences if o.call_id == _F_CALL_ID)
    assert _F_NONROOT in occ.proof.source_text
    rr = r.r_result
    assert rr is not None and rr.resolved_source is not None
    assert rr.resolved_source.root_text == _F_ROOT_BODY
    adm = r.admission
    assert adm is not None
    renderings = [
        repr(r),
        str(r),
        repr(r.diagnostics),
        repr(adm),
        repr(adm.root_entry),
        repr(rr),
        repr(r.bounds),
        repr(r.g_bounds),
    ]
    renderings.extend(repr(row) for row in adm.path_associations)
    renderings.extend(repr(entry) for entry in adm.entries)
    for rendering in renderings:
        for canary in _F_CANARIES:
            assert canary not in rendering, (canary, rendering[:200])
    # the genuine refusal renders canary-free as well:
    refused = derive_root_region_admission(
        s1, ns, bounds=RootRegionAdmissionBounds(max_total_work_units=1)
    )
    assert refused.outcome is RootRegionAdmissionOutcome.REFUSED
    for rendering in (repr(refused), str(refused), repr(refused.diagnostics)):
        for canary in _F_CANARIES:
            assert canary not in rendering, (canary, rendering[:200])
    # the fixed private bypass-copy error carries no canary content:
    q = rr.q_result
    assert q is not None
    bad_qb = q.bounds.model_copy(update={"max_total_work_units": 0})
    q_bad = q.model_copy(update={"bounds": bad_qb})
    rr_bad = rr.model_copy(update={"q_result": q_bad})
    adm_bad = adm.model_copy(update={"r_result": rr_bad})
    with pytest.raises(
        ValidationError,
        match="the Q result bounds must carry actual closed scalar fields",
    ) as excinfo:
        _result_models.RootRegionAdmissionResult.model_validate(
            r.model_copy(update={"r_result": rr_bad, "admission": adm_bad})
        )
    for canary in _F_CANARIES:
        assert canary not in str(excinfo.value)


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_f_no_host_io_on_consumer_paths(
    mode: AdmissionMode, endpoint: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    """F4: no host IO after fixture/import setup on the consumer's
    ready / non-ready / refusal paths: the closed 24-facility trap
    is open for the entire public derivation and for every later
    operational-record rendering (pure data evidence, not a wire-
    byte proof)."""
    # fixture and import setup BEFORE the traps:
    ns, s_ready, _v2_body, _v2_digest = _t_e_multi_dep_state(
        mode,
        endpoint,
        f"t018f-io-{endpoint}",
        graph_bounds=GraphBounds(max_work_units=1_048_576),
    )
    ns_u, s_unproven, _ = _frontier_state(mode, endpoint, f"t018f-iu-{endpoint}")
    calls: list[str] = []

    def trap(label: str) -> Any:
        def refused(*trap_args: Any, **trap_kwargs: Any) -> Any:
            calls.append(label)
            raise AssertionError("forbidden host IO: " + label)

        return refused

    for module, name in _host_io_facilities():
        monkeypatch.setattr(module, name, trap(module.__name__ + "." + name))
    r_ready = derive_root_region_admission(s_ready, ns, bounds=RootRegionAdmissionBounds())
    assert r_ready.outcome is RootRegionAdmissionOutcome.READY
    r_un = derive_root_region_admission(s_unproven, ns_u)
    assert r_un.outcome is RootRegionAdmissionOutcome.ROOT_CURRENTNESS_UNPROVEN
    r_ref = derive_root_region_admission(
        s_ready, ns, bounds=RootRegionAdmissionBounds(max_total_work_units=1)
    )
    assert r_ref.outcome is RootRegionAdmissionOutcome.REFUSED
    assert calls == []
    # every operational record still renders after the traps:
    for record in (r_ready, r_un, r_ref, r_ready.admission, r_ready.r_result):
        repr(record)
        str(record)
    assert calls == []


# --- A. Provenance pinning, source shapes, native carrier, key law ------


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_a_provenance_key_pinning(mode: AdmissionMode, endpoint: str) -> None:
    """A3: the canonical C ROOT_ENTRY key is provenance-invariant:
    a genuine complete whole singleton read of the SAME bootstrap
    bytes selects the 'read' source pinned to the same digest, and
    the root entry's canonical content key stays BYTE-IDENTICAL to
    the envelope-bootstrap derivation (the semantic key record, not
    the scope key, is provenance-invariant)."""
    ns, s0 = r_bootstrap(mode, f"t018a-pin-{endpoint}")
    r0 = derive_root_region_admission(s0, ns)
    adm0 = _assert_consumer_ready(r0, s0, ns, sha256_hex(ROOT_TEXT))
    k0 = adm0.root_entry.content_key
    t1 = r_issue(s0, ns, "s1", endpoint, (CAUSAL_ROOT_FACT,), "cat AGENTS.md")
    assert t1.outcome.value == "accepted", t1.diagnostics
    t2 = r_observe(t1.state, ns, (read_request(endpoint, "s1", ROOT_TEXT, "cat AGENTS.md"),))
    assert t2.outcome.value == "accepted", t2.diagnostics
    s1 = t2.state
    r1 = derive_root_region_admission(s1, ns)
    adm1 = _assert_consumer_ready(r1, s1, ns, sha256_hex(ROOT_TEXT))
    rr1 = r1.r_result
    assert rr1 is not None
    src = rr1.resolved_source
    assert src is not None
    assert src.kind == "read"
    assert src.root_digest == sha256_hex(ROOT_TEXT)
    assert src.root_text == ROOT_TEXT
    s1_occ = next(o for o in s1.d_state.occurrences if o.call_id == "s1")
    assert s1_occ is not None
    assert src.occurrence is not None
    assert src.occurrence is s1_occ
    assert src.proof is s1_occ.proof
    # The semantic canonical key is provenance-invariant.
    assert adm1.root_entry.content_key == k0
    # The read fact is retained alongside the envelope (erased).
    kinds = sorted(f.provenance.kind for f in s1.root_facts)
    assert kinds == ["envelope", "read"]


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
@pytest.mark.parametrize("shape", ["unicode", "crlf", "empty"])
def test_a_source_shape_law_unicode_crlf_empty(
    mode: AdmissionMode, endpoint: str, shape: str
) -> None:
    """A4: the Unicode nonroot prefix, the CRLF root+nonroot and the
    exact EMPTY root all READY the complete consumer with the
    measured UTF-8 root digest/length, and the admitted A.md row
    (where the root references it) retains the actual bytes."""
    if shape == "unicode":
        a_text = "Synthetic nonroot A. Å ö 漢.\n"
        ns, state = _mixed_region_state(mode, endpoint, f"t018a-uni-{endpoint}", a_text=a_text)
        r = derive_root_region_admission(state, ns)
        adm = _assert_consumer_ready(r, state, ns, sha256_hex(V2))
        rr = r.r_result
        assert rr is not None and rr.f_result is not None
        ov = rr.f_result.overlay
        assert ov is not None
        nodes = [n for n in ov.nodes if n.path == "A.md"]
        assert len(nodes) == 1
        assert nodes[0].digest == sha256_hex(a_text)
        a_rows = [row for row in adm.path_associations if row.path == "A.md"]
        assert len(a_rows) == 1
        assert len(a_rows[0].content_keys) == 1
    elif shape == "crlf":
        root_crlf = "Read `A.md` for the region refresh.\r\nSecond line.\r\n"
        a_crlf = "Synthetic nonroot A.\r\nSecond line.\r\n"
        ns, s0 = r_bootstrap(mode, f"t018a-crlf-{endpoint}")
        t1 = r_issue(s0, ns, "m1", endpoint, (CAUSAL_ROOT_FACT,), MIX_CMD)
        assert t1.outcome.value == "accepted", t1.diagnostics
        t2 = r_observe(
            t1.state,
            ns,
            (
                read_request(
                    endpoint,
                    "m1",
                    _mixed_body(a_crlf, MARK, root_crlf),
                    MIX_CMD,
                ),
            ),
        )
        assert t2.outcome.value == "accepted", t2.diagnostics
        state = t2.state
        r = derive_root_region_admission(state, ns)
        _assert_consumer_ready(r, state, ns, sha256_hex(root_crlf))
        rr = r.r_result
        assert rr is not None
        src = rr.resolved_source
        assert src is not None
        assert src.root_byte_length == len(root_crlf.encode("utf-8"))
        assert rr.f_result is not None
        ov = rr.f_result.overlay
        assert ov is not None
        nodes = [n for n in ov.nodes if n.path == "A.md"]
        assert len(nodes) == 1
        assert nodes[0].digest == sha256_hex(a_crlf)
    else:
        ns, state = r_bootstrap(mode, f"t018a-empty-{endpoint}", root_body="")
        r = derive_root_region_admission(state, ns)
        adm = _assert_consumer_ready(r, state, ns, sha256_hex(""))
        rr = r.r_result
        assert rr is not None
        src = rr.resolved_source
        assert src is not None
        assert src.root_byte_length == 0
        assert adm.entries == ()
        assert r.entry_source_bytes == 0


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_a_native_multi_piece_owner_association(mode: AdmissionMode, endpoint: str) -> None:
    """A5: the genuine native MULTI-PIECE carrier (exec + two
    polls, three pieces, the marker split across the exec/poll
    boundary) READYs the complete consumer with the ACTUAL original
    exec owner and poll piece producers retained by identity at the
    admission parent (never invented): the proof's original exec
    association, the complete owning record's observed piece-call
    bindings, the frozen bootstrap parent link, and the exact root
    body/digest."""
    ns, s0 = r_bootstrap(mode, f"t018a-native-{endpoint}")
    t1 = r_issue(s0, ns, "m1", endpoint, (CAUSAL_ROOT_FACT,), MIX_CMD)
    assert t1.outcome.value == "accepted", t1.diagnostics
    t2 = r_observe(t1.state, ns, (_native_multi_piece_request(endpoint),))
    assert t2.outcome.value == "accepted", t2.diagnostics
    s2 = t2.state
    r = derive_root_region_admission(s2, ns)
    _assert_consumer_ready(r, s2, ns, sha256_hex(V2))
    rr = r.r_result
    assert rr is not None
    src = rr.resolved_source
    assert src is not None
    assert src.kind == "read_region"
    assert src.root_text == V2
    proof = src.proof
    assert proof is not None
    assert len(proof.pieces) == 3
    pieces = proof.pieces
    assert [p.call_id for p in pieces] == ["m1", "p1", "p2"]
    assert proof.call_id == "m1"
    m1_occ = next(o for o in s2.d_state.occurrences if o.call_id == "m1")
    assert m1_occ is not None
    assert src.occurrence is not None
    assert src.occurrence is m1_occ
    assert proof is m1_occ.proof
    m1_res = next(x for x in s2.d_state.results if x.call_id == "m1")
    assert m1_res.complete is True
    assert [b[0] for b in m1_res.piece_call_bindings] == ["m1", "p1", "p2"]
    for piece, binding in zip(pieces, m1_res.piece_call_bindings, strict=True):
        assert piece.call_id == binding[0]
    # The frozen causal parent frontier: the polls carry no edge of
    # their own; m1 is parented to the bootstrap root anchor.
    assert len(s2.d_state.parent_links) == 1
    assert s2.d_state.parent_links[0].child == m1_occ.occurrence_id
    assert s2.d_state.parent_links[0].parent == CAUSAL_ROOT_FACT


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_a_file_key_law_repeated_operand_and_width(mode: AdmissionMode, endpoint: str) -> None:
    """A6: the FILE key law at the consumer: the repeated file
    operand does NOT inflate slot width (width 1, the member
    occurrences carry the path twice, one witness, exactly ONE
    reverse-row key); the plain region read admits the whole
    graph-eligible mixed bundle at width 2 in BOTH modes (every
    member is eligible under the selected root), with the
    governing root row sharing the bundle key; the first
    compatible original proof is retained by identity; and the
    exact reverse rows represent only the admitted members and
    the governing root path."""
    # (a) the repeated operand (genuine read, probe-confirmed shape).
    a_rep = "Synthetic A repeated.\n"
    ns, s0 = r_bootstrap(mode, f"t018a-rep-{endpoint}")
    t1 = r_issue(s0, ns, "rep", endpoint, (CAUSAL_ROOT_FACT,), "cat A.md && cat A.md")
    assert t1.outcome.value == "accepted", t1.diagnostics
    t2 = r_observe(
        t1.state,
        ns,
        (
            read_request(
                endpoint,
                "rep",
                frame(a_rep) + frame(a_rep),
                "cat A.md && cat A.md",
            ),
        ),
    )
    assert t2.outcome.value == "accepted", t2.diagnostics
    state = t2.state
    r = derive_root_region_admission(state, ns)
    adm = _assert_consumer_ready(r, state, ns, sha256_hex(ROOT_TEXT))
    assert len(adm.entries) == 1
    e = adm.entries[0]
    assert e.width == 1
    assert e.key_record.member_occurrences == ("A.md", "A.md")
    assert len(e.witnesses) == 1
    rep_occ = next(o for o in state.d_state.occurrences if o.call_id == "rep")
    assert e.proof is rep_occ.proof
    a_rows = [row for row in adm.path_associations if row.path == "A.md"]
    assert len(a_rows) == 1
    assert len(a_rows[0].content_keys) == 1
    assert a_rows[0].content_keys[0] == e.content_key
    assert a_rows[0].is_root is False
    # (b) the plain region read: the mode-accepted width and the
    # exact reverse rows.
    ns_m, sm = _mixed_region_state(mode, endpoint, f"t018a-file-{endpoint}")
    rm = derive_root_region_admission(sm, ns_m)
    adm_m = _assert_consumer_ready(rm, sm, ns_m, sha256_hex(V2))
    m1_occ = next(o for o in sm.d_state.occurrences if o.call_id == "m1")
    assert m1_occ is not None
    a_rows = [row for row in adm_m.path_associations if row.path == "A.md"]
    assert len(a_rows) == 1
    assert len(a_rows[0].content_keys) == 1
    akey = a_rows[0].content_keys[0]
    a_entries = [e for e in adm_m.entries if e.content_key == akey]
    assert len(a_entries) == 1
    ae = a_entries[0]
    # The first compatible original proof is retained by identity.
    assert ae.proof is m1_occ.proof
    assert len(ae.witnesses) >= 1
    assert all(w.occurrence_id == m1_occ.occurrence_id for w in ae.witnesses)
    # Both modes admit the whole graph-eligible bundle here: the
    # width-1 versus width-2 contrast is the repeated-operand
    # entry (a) against this bundle entry (b).
    assert ae.width == 2
    assert ae.key_record.member_occurrences == ("A.md", ROOT_FILENAME)
    root_rows = [row for row in adm_m.path_associations if row.path == ROOT_FILENAME]
    assert akey in root_rows[0].content_keys
    paths = {row.path for row in adm_m.path_associations if row.content_keys}
    assert paths == {"A.md", ROOT_FILENAME}


# --- B. Overlap / withdrawal / replay-conflict at consumer level --------


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_b_overlap_entries_ab_ac_a(mode: AdmissionMode, endpoint: str) -> None:
    """B5: the overlapping [A,B]/[A,C] entries share member A.md:
    the exact reverse row maps A.md to BOTH admitted bundle keys
    (width-2 proven partitions under a root that references every
    member), B.md/C.md map to their own bundle key, and the first
    compatible original proofs are retained by identity.  A
    child-of-one A version (a child of the first bundle's A
    segment only) withdraws the OLD bundle keys from EVERY row
    (the governing root key alone survives) while A.md itself
    stays unadmitted against the second bundle's retained
    lineage; the exact reverse rows after are the lean isolated
    eligible segments (B.md, C.md, their original bundle proofs
    retained) or the greedy no-bundle admission (root only).  A
    genuine A version descended from BOTH bundle lineages (and
    the child-of-one version) is unambiguous and CURRENT,
    admitting its OWN distinct singleton key with the old
    overlapping keys still withdrawn."""
    seg_a, seg_b, seg_c = "A part one.\n", "B part.\n", "C part.\n"
    mkr = "OVLMARK"
    root_body = "Read `A.md`, `B.md` and `C.md` before changing code."
    ns, s0 = r_bootstrap(mode, f"t018b-overlap-{endpoint}", root_body=root_body)
    cmd_ab = f"cat A.md && echo '{mkr}' && cat B.md"
    t1 = r_issue(s0, ns, "p1", endpoint, (CAUSAL_ROOT_FACT,), cmd_ab)
    assert t1.outcome.value == "accepted", t1.diagnostics
    t2 = r_observe(
        t1.state, ns, (read_request(endpoint, "p1", seg_a + mkr + "\n" + seg_b, cmd=cmd_ab),)
    )
    assert t2.outcome.value == "accepted", t2.diagnostics
    s1 = t2.state
    p1_occ = next(o for o in s1.d_state.occurrences if o.call_id == "p1")
    assert p1_occ is not None
    cmd_ac = f"cat A.md && echo '{mkr}' && cat C.md"
    t3 = r_issue(s1, ns, "p2", endpoint, (p1_occ.occurrence_id, CAUSAL_ROOT_FACT), cmd_ac)
    assert t3.outcome.value == "accepted", t3.diagnostics
    t4 = r_observe(
        t3.state, ns, (read_request(endpoint, "p2", seg_a + mkr + "\n" + seg_c, cmd=cmd_ac),)
    )
    assert t4.outcome.value == "accepted", t4.diagnostics
    s2 = t4.state
    r1 = derive_root_region_admission(s2, ns)
    adm1 = _assert_consumer_ready(r1, s2, ns, sha256_hex(root_body))
    by1 = {e.key_record.member_occurrences: e for e in adm1.entries}
    assert set(by1) == {("A.md", "B.md"), ("A.md", "C.md")}
    assert by1[("A.md", "B.md")].width == 2
    assert by1[("A.md", "C.md")].width == 2
    p2_occ = next(o for o in s2.d_state.occurrences if o.call_id == "p2")
    assert p2_occ is not None
    assert by1[("A.md", "B.md")].proof is p1_occ.proof
    assert by1[("A.md", "C.md")].proof is p2_occ.proof
    rows1 = {row.path: row for row in adm1.path_associations if row.content_keys}
    assert set(rows1) == {"AGENTS.md", "A.md", "B.md", "C.md"}
    a_keys1 = rows1["A.md"].content_keys
    # The overlap: A.md maps to ALL admitted keys, canonical order.
    assert len(a_keys1) == 2
    assert a_keys1 == tuple(
        sorted({by1[("A.md", "B.md")].content_key, by1[("A.md", "C.md")].content_key})
    )
    assert rows1["B.md"].content_keys == (by1[("A.md", "B.md")].content_key,)
    assert rows1["C.md"].content_keys == (by1[("A.md", "C.md")].content_key,)
    assert rows1["A.md"].is_root is False
    assert rows1["AGENTS.md"].is_root is True
    rk0 = adm1.root_entry.content_key
    # A genuine new A.md version (a child of the first bundle's
    # A segment occurrence).
    t5 = r_issue(s2, ns, "a2", endpoint, (p1_occ.occurrence_id,), "cat A.md")
    assert t5.outcome.value == "accepted", t5.diagnostics
    t6 = r_observe(
        t5.state, ns, (read_request(endpoint, "a2", frame("A part two.\n"), "cat A.md"),)
    )
    assert t6.outcome.value == "accepted", t6.diagnostics
    s3 = t6.state
    a2_occ = next(o for o in s3.d_state.occurrences if o.call_id == "a2")
    assert a2_occ is not None
    r2 = derive_root_region_admission(s3, ns)
    adm2 = _assert_consumer_ready(r2, s3, ns, sha256_hex(root_body))
    all_keys2 = {k for row in adm2.path_associations for k in row.content_keys}
    # Every OLD non-root key is withdrawn from EVERY row; the
    # governing root key is unchanged (root bytes unchanged).
    for old in a_keys1:
        assert old not in all_keys2
    assert adm2.root_entry.content_key == rk0
    rows2 = {row.path: row for row in adm2.path_associations if row.content_keys}
    assert "A.md" not in rows2
    if mode is AdmissionMode.LEAN:
        # The proven partitions survive as isolated eligible
        # segments for the untouched members, their original
        # bundle proofs retained by identity.
        by2 = {e.key_record.member_occurrences: e for e in adm2.entries}
        assert set(by2) == {("B.md",), ("C.md",)}
        assert by2[("B.md",)].width == 1
        assert by2[("C.md",)].width == 1
        assert by2[("B.md",)].proof is p1_occ.proof
        assert by2[("C.md",)].proof is p2_occ.proof
        assert rows2["B.md"].content_keys == (by2[("B.md",)].content_key,)
        assert rows2["C.md"].content_keys == (by2[("C.md",)].content_key,)
    else:
        # Greedy admits whole bundles only: the staled bundles
        # withdraw entirely and only the root remains.
        assert adm2.entries == ()
        assert set(rows2) == {"AGENTS.md"}
    # Phase 3: a genuine A version descended from BOTH bundle
    # lineages (and the child-of-one version): the single causal-
    # maximal A occurrence is unambiguous and CURRENT, admitting
    # its OWN distinct singleton key.
    t7 = r_issue(
        s3,
        ns,
        "a3",
        endpoint,
        (p1_occ.occurrence_id, p2_occ.occurrence_id, a2_occ.occurrence_id),
        "cat A.md",
    )
    assert t7.outcome.value == "accepted", t7.diagnostics
    t8 = r_observe(
        t7.state, ns, (read_request(endpoint, "a3", frame("A part three.\n"), "cat A.md"),)
    )
    assert t8.outcome.value == "accepted", t8.diagnostics
    s4 = t8.state
    r3 = derive_root_region_admission(s4, ns)
    adm3 = _assert_consumer_ready(r3, s4, ns, sha256_hex(root_body))
    a3_occ = next(o for o in s4.d_state.occurrences if o.call_id == "a3")
    assert a3_occ is not None
    a_entries3 = [e for e in adm3.entries if e.key_record.member_occurrences == ("A.md",)]
    assert len(a_entries3) == 1
    a_entry3 = a_entries3[0]
    assert a_entry3.width == 1
    assert a_entry3.proof is a3_occ.proof
    key_a3 = a_entry3.content_key
    a_rows3 = [row for row in adm3.path_associations if row.path == "A.md"]
    assert len(a_rows3) == 1
    assert a_rows3[0].content_keys == (key_a3,)
    all_keys3 = {k for row in adm3.path_associations for k in row.content_keys}
    # The old overlapping keys stay withdrawn; the governing root
    # key is unchanged.
    for old in a_keys1:
        assert old not in all_keys3
    assert adm3.root_entry.content_key == rk0
    if mode is AdmissionMode.LEAN:
        # The untouched members' segments plus the new A
        # singleton.
        assert {e.key_record.member_occurrences for e in adm3.entries} == {
            ("A.md",),
            ("B.md",),
            ("C.md",),
        }
    else:
        # Greedy: the staled whole bundles withhold B.md/C.md
        # (no standalone reads); only the new singleton bundle
        # is admitted.
        assert {e.key_record.member_occurrences for e in adm3.entries} == {("A.md",)}


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_b_withdrawal_alternate_cycle_admission(mode: AdmissionMode, endpoint: str) -> None:
    """B6: version-owned withdrawal, the surviving complete
    alternate and the cycle, tested on the ADMISSION results as
    well as the graph: under the new region root V2_ROOT the A.md
    branch (with its two-node cycle) withdraws as retained
    unreachable possession; the surviving X.md alternate keeps
    Target.md at its least recomputed depth; the admitted X.md/
    Target.md entries are REKEYED under the new governing root
    digest (the canonical key binds it) while their ORIGINAL
    proofs are retained by identity; and the exact reverse rows
    represent only the still-admitted members."""
    ns, s1, original = _multi_source_state(mode, endpoint, f"t018b-cycle-{endpoint}")
    r1 = derive_root_region_admission(s1, ns)
    adm1 = _assert_consumer_ready(r1, s1, ns, sha256_hex(V1_ROOT))
    for path in ("A.md", "X.md", "Cycle1.md", "Cycle2.md", "Target.md"):
        rows = [row for row in adm1.path_associations if row.path == path]
        assert len(rows) == 1
        assert len(rows[0].content_keys) == 1
    key_x1 = next(row.content_keys[0] for row in adm1.path_associations if row.path == "X.md")
    key_t1 = next(row.content_keys[0] for row in adm1.path_associations if row.path == "Target.md")
    # Phase 2: a genuinely NEW region root (v2) drops the A.md
    # branch: the cycle and A.md withdraw; the surviving X.md
    # alternate keeps Target.md.
    issued = r_issue(s1, ns, "root2", endpoint, (CAUSAL_ROOT_FACT,), MULTI_CMD)
    assert issued.outcome.value == "accepted", issued.diagnostics
    obs = r_observe(
        issued.state,
        ns,
        (read_request(endpoint, "root2", _mixed_body(REGION_PREFIX, MARK, V2_ROOT), MULTI_CMD),),
    )
    assert obs.outcome.value == "accepted", obs.diagnostics
    s2 = obs.state
    r2 = derive_root_region_admission(s2, ns)
    adm2 = _assert_consumer_ready(r2, s2, ns, sha256_hex(V2_ROOT))
    # The withdrawn members are no longer represented by an
    # admitted key.
    paths2 = {row.path for row in adm2.path_associations if row.content_keys}
    for gone in ("A.md", "Cycle1.md", "Cycle2.md"):
        assert gone not in paths2
    # The surviving alternate keeps ONE key, REKEYED under the new
    # governing root digest, with the ORIGINAL proof retained.
    x_rows = [row for row in adm2.path_associations if row.path == "X.md"]
    t_rows = [row for row in adm2.path_associations if row.path == "Target.md"]
    assert len(x_rows) == 1
    assert len(x_rows[0].content_keys) == 1
    assert x_rows[0].content_keys[0] != key_x1
    assert len(t_rows) == 1
    assert len(t_rows[0].content_keys) == 1
    assert t_rows[0].content_keys[0] != key_t1
    x_entries = [e for e in adm2.entries if e.content_key == x_rows[0].content_keys[0]]
    t_entries = [e for e in adm2.entries if e.content_key == t_rows[0].content_keys[0]]
    assert len(x_entries) == 1
    assert len(t_entries) == 1
    assert x_entries[0].proof is original["x"].proof
    assert t_entries[0].proof is original["t"].proof
    # The graph side agrees: least depth recomputed through the
    # surviving alternate, withdrawn paths retained as possession.
    rr2 = r2.r_result
    assert rr2 is not None and rr2.f_result is not None
    ov2 = rr2.f_result.overlay
    assert ov2 is not None
    nodes2 = {n.path: n for n in ov2.nodes}
    for gone in ("A.md", "Cycle1.md", "Cycle2.md"):
        assert gone not in nodes2
    assert nodes2["Target.md"].depth == 2
    assert {"A.md", "Cycle1.md", "Cycle2.md"} <= set(ov2.unreachable_current_paths)
    # Mode law on the root bundle's nonroot member: lean admits no
    # background, greedy retains the whole root bundle.
    if mode is AdmissionMode.LEAN:
        assert "Note.md" not in paths2
    else:
        n_rows = [row for row in adm2.path_associations if row.path == "Note.md"]
        assert len(n_rows) == 1
        assert len(n_rows[0].content_keys) == 1
        n_entries = [e for e in adm2.entries if e.content_key == n_rows[0].content_keys[0]]
        assert len(n_entries) == 1
        assert n_entries[0].width == 2


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_b_replay_noop_and_authority_conflict(mode: AdmissionMode, endpoint: str) -> None:
    """B7: replayed history never rolls the selection back: the
    EXACT replay of the same original region read after the
    changed-root selection is a pure idempotent transition
    (REPLAYED, the EXACT prior state object, no revision advance)
    and the consumer output is unchanged; a genuinely NEW same-
    byte region occurrence (a child of the proven maximal) also
    keeps the selection and the semantic key stable while the new
    fact is retained.  DIFFERING maximal root bytes (a child of
    each opaque branch) are an explicit authority conflict that
    blocks BEFORE admission (the actual R evidence retained, no
    usable source, no G channel)."""
    # (a) the exact replay of the SAME original call/result.
    ns, s0 = _mixed_region_state(mode, endpoint, f"t018b-replay-{endpoint}")
    r0 = derive_root_region_admission(s0, ns)
    adm0 = _assert_consumer_ready(r0, s0, ns, sha256_hex(V2))
    k0 = adm0.root_entry.content_key
    rev0 = r0.revision
    t_replay = r_observe(
        s0, ns, (read_request(endpoint, "m1", _mixed_body(A_TEXT, MARK, V2), MIX_CMD),)
    )
    assert t_replay.outcome is RootLineageOutcome.REPLAYED
    assert t_replay.state is s0
    r1 = derive_root_region_admission(t_replay.state, ns)
    adm1 = _assert_consumer_ready(r1, t_replay.state, ns, sha256_hex(V2))
    assert r1.revision == rev0
    assert adm1.root_entry.content_key == k0
    # (b) a genuinely NEW same-byte region occurrence (a child of
    # the proven maximal): stable selection, retained fact.
    m1 = next(o for o in s0.d_state.occurrences if o.call_id == "m1")
    assert m1 is not None
    t3 = r_issue(s0, ns, "replay2", endpoint, (m1.occurrence_id,), MIX_CMD)
    assert t3.outcome.value == "accepted", t3.diagnostics
    t4 = r_observe(
        t3.state, ns, (read_request(endpoint, "replay2", _mixed_body(A_TEXT, MARK, V2), MIX_CMD),)
    )
    assert t4.outcome.value == "accepted", t4.diagnostics
    s1 = t4.state
    r2 = derive_root_region_admission(s1, ns)
    adm2 = _assert_consumer_ready(r2, s1, ns, sha256_hex(V2))
    assert r2.revision > rev0
    assert len(s1.root_facts) == len(s0.root_facts) + 1
    assert adm2.root_entry.content_key == k0
    # (c) differing maximal root bytes: authority conflict.
    ns, fs0, _v2 = _frontier_state(mode, endpoint, f"t018b-conf-{endpoint}")
    ua, ub = q_occ(fs0, "ua"), q_occ(fs0, "ub")
    s1c = q_observe(
        q_issue(fs0, ns, "va", endpoint, Q_MIX_CMD, (ua.occurrence_id,)),
        ns,
        endpoint,
        "va",
        q_mixed_body(Q_A_TEXT, Q_MARK, "R5."),
        Q_MIX_CMD,
    )
    s2c = q_observe(
        q_issue(s1c, ns, "vb", endpoint, Q_MIX_CMD, (ub.occurrence_id,)),
        ns,
        endpoint,
        "vb",
        q_mixed_body(Q_A_TEXT, Q_MARK, "R6."),
        Q_MIX_CMD,
    )
    r2c = derive_root_region_admission(s2c, ns)
    assert r2c.outcome is RootRegionAdmissionOutcome.ROOT_AUTHORITY_CONFLICT
    assert r2c.diagnostics == ()
    assert r2c.g_limitation is None
    assert r2c.admission is None
    assert r2c.r_result is not None
    assert r2c.r_result.outcome is RootRegionGraphOutcome.ROOT_AUTHORITY_CONFLICT
    assert r2c.r_result.resolved_source is None
    assert r2c.r_result.f_result is None
    assert r2c.state is s2c
    assert r2c.ns is ns
    assert r2c.g_work_units == 0
    assert 0 < r2c.work_units <= r2c.bounds.max_total_work_units
    # The conflict is stable (no invented recovery on re-derivation).
    r3c = derive_root_region_admission(s2c, ns)
    assert r3c.outcome is RootRegionAdmissionOutcome.ROOT_AUTHORITY_CONFLICT
    assert r3c.admission is None


# --- C. Full-result third-parent bypass battery --------------------------


def test_c_third_parent_bypass_battery(monkeypatch: pytest.MonkeyPatch) -> None:
    """C4: the COMPLETE full-result THIRD-parent genuine positive
    then negative-only mutations (copy-only, never a weakening of
    any predicate): every bypass-copied nested variant --
    malformed/missing leaf fields, a detached genuine proof from
    another state, a coherent foreign/rekeyed namespace, a
    coherently wrong version tag, and the ACTUAL later same-root
    graph splices (R result and whole admission from a genuine
    SAME-lineage later state) -- refuses with a fixed private
    error at the third carrying boundary, phase-faithfully:
    gates specified BEFORE the consumer scope-key serializer
    target refuse without reaching it (the real target wrapped
    to count, never replaced; the hit counter stays put), while
    the leaf / S-parent law gates specified at the phase-5 S
    re-validation refuse AFTER the serializer is reached (the
    hit counter advances)."""
    ns, state = _mixed_region_state(_MODE, _ENDPOINT, "t018c-battery")
    pos = derive_root_region_admission(state, ns)
    assert pos.outcome is RootRegionAdmissionOutcome.READY
    rr = pos.r_result
    assert rr is not None
    adm = pos.admission
    assert adm is not None
    e0 = adm.entries[0]
    hits: list[int] = []
    real_scope = _result_models.root_region_admission_scope_key

    def _counting_scope(*args: Any, **kwargs: Any) -> str:
        hits.append(1)
        return real_scope(*args, **kwargs)

    monkeypatch.setattr(_result_models, "root_region_admission_scope_key", _counting_scope)
    # The genuine result revalidates at the third boundary with
    # the real scope serializer reached.
    revalidated = _result_models.RootRegionAdmissionResult.model_validate(pos)
    assert revalidated.outcome is RootRegionAdmissionOutcome.READY
    assert len(hits) >= 1

    def _refused(update: dict[str, Any], pattern: str, pre_scope: bool) -> None:
        before = len(hits)
        with pytest.raises(ValidationError, match=pattern):
            _result_models.RootRegionAdmissionResult.model_validate(pos.model_copy(update=update))
        if pre_scope:
            # The refusing gate is specified before the phase-3
            # scope-key serializer target: the real target never
            # runs for this shape.
            assert len(hits) == before
        else:
            # The gate is specified at the phase-5 S parent /
            # leaf re-validation, AFTER the phase-3 scope
            # recompute: the serializer is reached first.
            assert len(hits) > before

    # (a) malformed / missing leaf variants.
    bad_proof = e0.model_copy(update={"proof": None})
    _refused(
        {"admission": adm.model_copy(update={"entries": (bad_proof,)})},
        "a file entry keeps its retained original proof",
        False,
    )
    bad_width = e0.model_copy(update={"width": True})
    _refused(
        {"admission": adm.model_copy(update={"entries": (bad_width,)})},
        "the entry width must carry a closed positive integer",
        False,
    )
    bad_kr = e0.model_copy(update={"key_record": None})
    _refused(
        {"admission": adm.model_copy(update={"entries": (bad_kr,)})},
        "the entry key record must be the actual canonical record",
        False,
    )
    # (b) a DETACHED genuine original: the proof of a genuine
    # same-shape state that is not THIS input state's retained
    # proof (the witnesses stay coherent, so the proof-identity
    # join, not a coordinate fence, is the refusal).
    ns_x, state_x = _mixed_region_state(_MODE, _ENDPOINT, "t018c-detch")
    r_x = derive_root_region_admission(state_x, ns_x)
    assert r_x.outcome is RootRegionAdmissionOutcome.READY
    adm_x = r_x.admission
    assert adm_x is not None
    det_e = e0.model_copy(update={"proof": adm_x.entries[0].proof})
    _refused(
        {"admission": adm.model_copy(update={"entries": (det_e,)})},
        "the file entry proof must be an original D-state retained proof",
        False,
    )
    # (c) coherent FOREIGN namespace rekey: result and admission
    # both carry the unjoined namespace (the identity joins hold,
    # the state-lineage join is the refusal).
    foreign = ns.model_copy(update={"lineage_key": "f" * 64})
    _refused(
        {
            "ns": foreign,
            "admission": adm.model_copy(update={"ns": foreign}),
        },
        "the consumer namespace must join the exact input state lineage",
        True,
    )
    # (c2) coherently WRONG version tag: both carried namespaces
    # agree on a tag that is not the actual fixed lineage tag
    # (the S parent version-identity fence over the actual
    # supported region versions is the first fence to fire).
    wrong_tag = ns.model_copy(update={"policy_version": "root-region-lineage-policy/v0"})
    _refused(
        {
            "ns": wrong_tag,
            "admission": adm.model_copy(update={"ns": wrong_tag}),
        },
        "the carried namespace must carry the actual supported version identities",
        False,
    )
    # (d) the ACTUAL later same-lineage same-root stale-graph
    # splices: a genuine A.md version change under the UNCHANGED
    # root (a complete whole singleton read issued as a child of
    # the m1 mixed occurrence of THIS battery lineage), then the
    # later R result / later whole admission spliced into the
    # EARLIER result (each piece genuine and self-consistent in
    # its own state; the lineage key and the root digest are
    # unchanged, the revision advances).
    m1 = next(o for o in state.d_state.occurrences if o.call_id == "m1")
    assert m1 is not None
    t5 = r_issue(state, ns, "cnew", _ENDPOINT, (m1.occurrence_id,), "cat A.md")
    assert t5.outcome.value == "accepted", t5.diagnostics
    t6 = r_observe(t5.state, ns, (read_request(_ENDPOINT, "cnew", A_NEW_TEXT, "cat A.md"),))
    assert t6.outcome.value == "accepted", t6.diagnostics
    s_late = t6.state
    assert s_late is not state
    assert s_late.lineage_key == state.lineage_key
    assert s_late.revision > state.revision
    r_late = derive_root_region_admission(s_late, ns)
    assert r_late.outcome is RootRegionAdmissionOutcome.READY
    # (d1) the later R result: its carried state is the later
    # state, never the earlier input state.
    _refused(
        {
            "r_result": r_late.r_result,
            "admission": adm.model_copy(update={"r_result": r_late.r_result}),
        },
        "the actual R result must retain the exact input state by identity",
        True,
    )
    # (d2) the later whole admission: the same carried-state law
    # at the admission parent.
    _refused(
        {"admission": r_late.admission},
        "the admission parent must retain the exact input state and namespace",
        True,
    )
    # (e) the INCOHERENT carried namespace (result only): a
    # value-EQUAL but distinct namespace object on the result;
    # the admission parent must retain the EXACT input namespace
    # by identity (value equality is not identity; the lineage
    # joins pass, the admission-namespace identity join is the
    # refusal, before the scope target).
    ns_copy = ns.model_copy()
    _refused(
        {"ns": ns_copy},
        "the admission parent must retain the exact input state and namespace",
        True,
    )
    # (f) the retained-content / group-partition law re-run at
    # the THIRD parent (the S leaf law's admitted-segment
    # domain): the genuine A.md entry partition is positive
    # first (the revalidated READY parent above), then a
    # duplicated index vector and a count-valid out-of-range
    # index each refuse at the carrying boundary.  All three
    # fences sit at the phase-5 S re-validation, after the
    # phase-3 scope target.
    assert e0.proof is not None
    assert len(e0.proof.segments) == 2
    _refused(
        {
            "admission": adm.model_copy(
                update={"entries": (e0.model_copy(update={"admitted_segments": (0, 0)}),)}
            )
        },
        "admitted segment indices must be distinct and increasing",
        False,
    )
    _refused(
        {
            "admission": adm.model_copy(
                update={
                    "entries": (
                        e0.model_copy(update={"admitted_segments": (len(e0.proof.segments),)}),
                    )
                }
            )
        },
        "admitted segment indices must index the proof segments",
        False,
    )
    # (g) the canonical key-record law at the THIRD parent: the
    # FOUR bound sets carried inside the genuine A.md key record
    # close at the leaf law re-run; a zero under the original
    # floor on one carried set refuses the bypassed entry copy.
    forged_kr = e0.key_record.model_copy(
        update={
            "admission_bounds": e0.key_record.admission_bounds.model_copy(update={"max_entries": 0})
        }
    )
    _refused(
        {
            "admission": adm.model_copy(
                update={"entries": (e0.model_copy(update={"key_record": forged_kr}),)}
            )
        },
        "the key record carried bound sets must be closed scalar sets",
        False,
    )
    # (h) the exact reverse-index law at the THIRD parent: the
    # complete path association is positive first (the
    # revalidated READY parent), then a missing represented path
    # and an extra admitted key on a path each refuse.
    rows = adm.path_associations
    a_row = next(row for row in rows if row.path == "A.md")
    root_key = adm.root_entry.content_key
    assert a_row.content_keys
    _refused(
        {
            "admission": adm.model_copy(
                update={"path_associations": tuple(row for row in rows if row.path != "A.md")}
            )
        },
        "the reverse index covers exactly the represented member paths in order",
        False,
    )
    _refused(
        {
            "admission": adm.model_copy(
                update={
                    "path_associations": tuple(
                        row
                        if row.path != "A.md"
                        else row.model_copy(update={"content_keys": (*row.content_keys, root_key)})
                        for row in rows
                    )
                }
            )
        },
        "the reverse index maps every path to all and only its admitted keys",
        False,
    )
    # (i) the CANONICAL key law at the THIRD parent: the entry and
    # its key record carry the SAME bogus 64-hex content key, so
    # the entry/record equality join holds and the ACTUAL
    # canonical 018-c recomputation from the record's real fields
    # is the refusal (distinct from the shape/index gates).
    bogus_key = "b" * 64
    _refused(
        {
            "admission": adm.model_copy(
                update={
                    "entries": (
                        e0.model_copy(
                            update={
                                "content_key": bogus_key,
                                "key_record": e0.key_record.model_copy(
                                    update={"content_key": bogus_key}
                                ),
                            }
                        ),
                    )
                }
            )
        },
        "content key must bind the actual canonical 018-c recipe",
        False,
    )
    # (j) the RETAINED-CONTENT digest join at the THIRD parent:
    # the ownership-group digest is altered and the NEGATIVE copy
    # rekeyed with the ACTUAL C recipe (so the canonical check
    # holds), and the altered group must still refuse against the
    # retained ORIGINAL proof segment digest.
    group0 = e0.key_record.ownership_groups[0]
    altered_kr = e0.key_record.model_copy(
        update={
            "ownership_groups": (
                group0.model_copy(update={"group_digest": "d" * 64}),
                *e0.key_record.ownership_groups[1:],
            )
        }
    )
    altered_key = _canonical_entry_key(altered_kr)
    assert altered_key != e0.key_record.content_key
    _refused(
        {
            "admission": adm.model_copy(
                update={
                    "entries": (
                        e0.model_copy(
                            update={
                                "content_key": altered_key,
                                "key_record": altered_kr.model_copy(
                                    update={"content_key": altered_key}
                                ),
                            }
                        ),
                    )
                }
            )
        },
        "a single-member segment group is proven with the member digest",
        False,
    )


# --- D. Independent local domains (complete consumer) ---------------------


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_d_f_subtree_local_domain(
    mode: AdmissionMode, endpoint: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    """D: the ACTUAL F-subtree work domain beneath the ONE entire
    consumer, measured on the ACTUAL F ledger class (class-
    preserving __init__ wrapper, installed and restored by
    monkeypatch; the same G subtree ledger created before the F
    phase stays the shared G domain): a genuine F cap EXACTLY at
    the measured F cost yields the FULL READY admission while the
    ACTUAL G and whole counters exceed it (the independent-domain
    shape a shared minimum cannot pass); the F one-below crossing
    lands the typed F over-bound refusal with the ACTUAL same-run
    Q READY retained, the EXACT original state, no admission and
    no G admission-stage work (the admission assembly target is
    counted, never replaced, and never reached)."""
    ns, state, _r = _d_ready_fixture(mode, endpoint, f"t018d-f-{endpoint}")
    f_ledgers: list[Any] = []
    orig_init = _r_mod._RFOuter.__init__

    def counting_init(self: Any, *args: Any, **kwargs: Any) -> None:
        orig_init(self, *args, **kwargs)
        f_ledgers.append(self)

    monkeypatch.setattr(_r_mod._RFOuter, "__init__", counting_init)
    # before-target spy on the G admission assembly (counted,
    # never replaced).
    adm_calls = {"n": 0}
    real_admission = _t_mod._t_admission

    def counting_admission(*args: Any, **kwargs: Any) -> Any:
        adm_calls["n"] += 1
        return real_admission(*args, **kwargs)

    monkeypatch.setattr(_t_mod, "_t_admission", counting_admission)

    def derive(**kwargs: Any) -> RootRegionAdmissionResult:
        f_ledgers.clear()
        return derive_root_region_admission(state, ns, **kwargs)

    r_def = derive()
    assert r_def.outcome is RootRegionAdmissionOutcome.READY
    assert r_def.admission is not None
    f_cost = max(i.work_spent for i in f_ledgers)
    assert 0 < f_cost
    assert adm_calls["n"] == 1
    # the independent-domain shape: the actual G subtree and the
    # entire consumer both EXCEED the actual F cost.
    assert f_cost < r_def.g_work_units < r_def.work_units
    rr = r_def.r_result
    assert rr is not None
    assert rr.f_result is not None
    assert rr.f_result.outcome is CurrentGraphOutcome.OK
    # positive: the genuine F cap EXACTLY at the measured F cost
    # still READYs the full admission (the F phase completes at
    # its cap; the G/whole domains are independent).
    r_f = derive(current_graph_bounds=CurrentGraphBounds(max_total_work_units=f_cost))
    assert max(i.work_spent for i in f_ledgers) == f_cost
    assert r_f.outcome is RootRegionAdmissionOutcome.READY
    assert r_f.admission is not None
    assert r_f.r_result is not None
    assert r_f.r_result.f_result is not None
    assert r_f.r_result.f_result.outcome is CurrentGraphOutcome.OK
    assert r_f.r_result.q_result is not None
    assert r_f.r_result.q_result.outcome is RootRegionCurrentnessOutcome.READY
    assert r_f.state is state
    assert r_f.scope_key != r_def.scope_key
    # the independent-domain shape holds on the capped run too:
    # the measured F cost stays strictly below actual G and whole.
    assert f_cost < r_f.g_work_units < r_f.work_units
    # one below: the typed F over-bound refusal through the ACTUAL
    # F channel (no consumer-own diagnostic invented, no G channel,
    # no admission, the original state retained).
    adm_calls["n"] = 0
    r_fb = derive(current_graph_bounds=CurrentGraphBounds(max_total_work_units=f_cost - 1))
    assert adm_calls["n"] == 0
    assert r_fb.outcome is RootRegionAdmissionOutcome.REFUSED
    assert r_fb.diagnostics == ()
    assert r_fb.g_limitation is None
    assert r_fb.admission is None
    assert r_fb.stage_work_units == 0
    assert r_fb.entry_source_bytes == 0
    rrb = r_fb.r_result
    assert rrb is not None
    assert rrb.outcome is RootRegionGraphOutcome.REFUSED
    assert rrb.diagnostics == ()
    assert rrb.resolved_source is None
    assert rrb.e_overlay is None
    assert rrb.f_result is not None
    assert rrb.f_result.outcome is CurrentGraphOutcome.REFUSED_OVER_BOUND
    assert [d.value for d in rrb.f_result.diagnostics] == ["total_work_units_over_bound"]
    assert rrb.q_result is not None
    assert rrb.q_result.outcome is RootRegionCurrentnessOutcome.READY
    assert rrb.q_result.p_selection is not None
    assert rrb.q_result.p_selection.outcome is RootSelectionOutcome.OK
    assert rrb.state is state
    assert r_fb.state is state
    assert r_fb.revision == state.revision


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_d_q_subtree_local_domain(
    mode: AdmissionMode, endpoint: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    """D: the ACTUAL Q-local work domain beneath the ONE entire
    consumer, measured on the ACTUAL Q ledger class (class-
    preserving __init__ wrappers, installed and restored by
    monkeypatch): a genuine Q cap EXACTLY at the measured Q cost
    still READYs the full admission while the successful whole
    exceeds it; the Q one-below crossing lands BEFORE any
    F/admission work (the absent F phase, never a fabricated
    zero) through the ACTUAL Q channel (the typed Q refusal
    carrying the actual P selection, NO consumer-own diagnostic
    invented, no G channel, the exact original state retained)."""
    ns, state, _r = _d_ready_fixture(mode, endpoint, f"t018d-q-{endpoint}")
    q_ledgers: list[Any] = []
    f_ledgers: list[Any] = []
    orig_q_init = _r_mod._RQOuter.__init__

    def counting_q_init(self: Any, *args: Any, **kwargs: Any) -> None:
        orig_q_init(self, *args, **kwargs)
        q_ledgers.append(self)

    monkeypatch.setattr(_r_mod._RQOuter, "__init__", counting_q_init)
    orig_f_init = _r_mod._RFOuter.__init__

    def counting_f_init(self: Any, *args: Any, **kwargs: Any) -> None:
        orig_f_init(self, *args, **kwargs)
        f_ledgers.append(self)

    monkeypatch.setattr(_r_mod._RFOuter, "__init__", counting_f_init)

    def derive(**kwargs: Any) -> RootRegionAdmissionResult:
        q_ledgers.clear()
        f_ledgers.clear()
        return derive_root_region_admission(state, ns, **kwargs)

    r_def = derive()
    assert r_def.outcome is RootRegionAdmissionOutcome.READY
    assert r_def.admission is not None
    q_cost = max(i.work_spent for i in q_ledgers)
    assert 0 < q_cost < r_def.r_work_units < r_def.work_units
    # positive: the genuine Q cap EXACTLY at the measured Q cost
    # still READYs the full admission (the Q phase completes at
    # its cap; the R/whole domains are independent).
    r_q = derive(
        root_region_currentness_bounds=RootRegionCurrentnessBounds(max_total_work_units=q_cost)
    )
    assert max(i.work_spent for i in q_ledgers) == q_cost
    assert r_q.outcome is RootRegionAdmissionOutcome.READY
    assert r_q.admission is not None
    assert r_q.r_result is not None
    assert r_q.r_result.q_result is not None
    assert r_q.r_result.q_result.outcome is RootRegionCurrentnessOutcome.READY
    assert r_q.r_result.f_result is not None
    assert r_q.r_result.f_result.outcome is CurrentGraphOutcome.OK
    assert r_q.state is state
    assert r_q.scope_key != r_def.scope_key
    # the measured Q cap sits strictly below the successful whole
    # admission (the independent-domain shape).
    assert q_cost < r_q.r_work_units < r_q.work_units
    # one below: the typed Q over-bound refusal BEFORE any
    # F/admission work (the F phase never runs at all).
    r_qb = derive(
        root_region_currentness_bounds=RootRegionCurrentnessBounds(max_total_work_units=q_cost - 1)
    )
    assert not f_ledgers
    assert r_qb.outcome is RootRegionAdmissionOutcome.REFUSED
    assert r_qb.diagnostics == ()
    assert r_qb.g_limitation is None
    assert r_qb.admission is None
    assert r_qb.stage_work_units == 0
    assert r_qb.entry_source_bytes == 0
    rrb = r_qb.r_result
    assert rrb is not None
    assert rrb.outcome is RootRegionGraphOutcome.REFUSED
    assert rrb.diagnostics == ()
    assert rrb.resolved_source is None
    assert rrb.f_result is None
    assert rrb.e_overlay is None
    assert rrb.q_result is not None
    assert rrb.q_result.outcome is RootRegionCurrentnessOutcome.REFUSED
    assert [d.value for d in rrb.q_result.diagnostics] == ["work_units_over_bound"]
    assert rrb.q_result.p_selection is not None
    assert rrb.q_result.p_selection.outcome is RootSelectionOutcome.OK
    assert rrb.q_result.state is state
    assert rrb.state is state
    assert r_qb.state is state
    assert r_qb.revision == state.revision


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_d_r_total_local_domain(
    mode: AdmissionMode, endpoint: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    """D: the ACTUAL R-total work domain beneath the ONE entire
    consumer, measured on the ACTUAL R ledger class (class-
    preserving __init__ wrapper, cross-checked against the honest
    same-run r_work_units counter): a genuine R cap EXACTLY at the
    measured R cost still READYs the full admission while the
    successful whole exceeds it; the R one-below crossing carries
    the ACTUAL R work_units_over_bound through the mapped channel
    (no consumer-invented diagnostic, no G channel), retains the
    actual R result with the intermediates ACTUALLY returned
    (Q READY and the actual F OK as bounded evidence, no usable
    source), never reaches the admission assembly (counted, never
    replaced), and keeps the exact original state.  No
    zero-allocation claim about other construction."""
    ns, state, _r = _d_ready_fixture(mode, endpoint, f"t018d-r-{endpoint}")
    r_ledgers: list[Any] = []
    orig_init = _r_mod._ROuter.__init__

    def counting_init(self: Any, *args: Any, **kwargs: Any) -> None:
        orig_init(self, *args, **kwargs)
        r_ledgers.append(self)

    monkeypatch.setattr(_r_mod._ROuter, "__init__", counting_init)
    # before-target spy on the G admission assembly (counted,
    # never replaced).
    adm_calls = {"n": 0}
    real_admission = _t_mod._t_admission

    def counting_admission(*args: Any, **kwargs: Any) -> Any:
        adm_calls["n"] += 1
        return real_admission(*args, **kwargs)

    monkeypatch.setattr(_t_mod, "_t_admission", counting_admission)

    def derive(**kwargs: Any) -> RootRegionAdmissionResult:
        r_ledgers.clear()
        return derive_root_region_admission(state, ns, **kwargs)

    r_def = derive()
    assert r_def.outcome is RootRegionAdmissionOutcome.READY
    assert r_def.admission is not None
    assert adm_calls["n"] == 1
    r_cost = max(i.work_spent for i in r_ledgers)
    assert 0 < r_cost == r_def.r_work_units < r_def.work_units
    # positive: the genuine R cap EXACTLY at the measured R cost
    # still READYs the full admission (the R derivation completes
    # at its cap; the entire-consumer domain is independent).
    r_x = derive(root_region_graph_bounds=RootRegionGraphBounds(max_total_work_units=r_cost))
    assert max(i.work_spent for i in r_ledgers) == r_cost
    assert r_x.outcome is RootRegionAdmissionOutcome.READY
    assert r_x.admission is not None
    assert r_x.r_result is not None
    assert r_x.r_result.outcome is RootRegionGraphOutcome.READY
    assert r_x.r_work_units == r_cost
    assert r_cost < r_x.work_units
    assert r_x.state is state
    assert r_x.scope_key != r_def.scope_key
    # one below: the mapped ACTUAL R total crossing (the precise
    # R channel retained, the actual F OK as bounded evidence when
    # the crossing lands after F, no usable source, no admission).
    adm_calls["n"] = 0
    r_rb = derive(root_region_graph_bounds=RootRegionGraphBounds(max_total_work_units=r_cost - 1))
    assert adm_calls["n"] == 0
    assert r_rb.outcome is RootRegionAdmissionOutcome.REFUSED
    assert r_rb.diagnostics == (RootRegionAdmissionDiagnostic.WORK_UNITS_OVER_BOUND,)
    assert r_rb.g_limitation is None
    assert r_rb.admission is None
    assert r_rb.stage_work_units == 0
    assert r_rb.entry_source_bytes == 0
    rrb = r_rb.r_result
    assert rrb is not None
    assert rrb.outcome is RootRegionGraphOutcome.REFUSED
    assert [d.value for d in rrb.diagnostics] == ["work_units_over_bound"]
    assert rrb.resolved_source is None
    assert rrb.q_result is not None
    assert rrb.q_result.outcome is RootRegionCurrentnessOutcome.READY
    # the crossing lands after the F phase: the ACTUAL F OK result
    # is retained as bounded evidence (never a fabricated or
    # re-run intermediate).
    assert rrb.f_result is not None
    assert rrb.f_result.outcome is CurrentGraphOutcome.OK
    assert rrb.state is state
    assert r_rb.state is state
    assert r_rb.revision == state.revision


@pytest.mark.parametrize("mode", MODES)
def test_d_p_local_domain(mode: AdmissionMode, monkeypatch: pytest.MonkeyPatch) -> None:
    """D: the ACTUAL independent P domain beneath the ONE entire
    consumer, on the genuine public-P-built n=40
    eligible-opaque-branch fixture (the measured discriminator
    shape, reused from the accepted Q suite's producer).

    Build 1 (generous): the full public P production under the
    DEFAULT P ceiling, with the per-operation maxima of the
    ACTUAL _HOuter ledgers tracked by a counting __init__ wrapper
    on the REAL class (installed/restored by monkeypatch; class
    identity and isinstance preserved).  Build 2 (strict): the
    SAME sequence rebuilt under a FRESH namespace (fresh lineage,
    identical field structure -- NOT one namespace identity
    across both builds) whose ACTUAL inherited P ceiling
    (ns.root_lineage_bounds) is the frozen per-operation producer
    maximum -- fully public P production, so the state under test
    was built under its own ceiling.

    The ACTUAL P cost of the public derivation is measured on that
    SAME strict-built ns/state (no fresh copied state or namespace,
    no replaced class) through the existing real-class ledger
    collector (the actual same-run _QPAdapter P-domain outer):
    actual P cost <= producer max < successful T whole cost --
    the discriminating shape a single shared min(P ceiling, whole)
    budget cannot pass (the whole exceeds the actual P domain
    while the P phase fits it).

    P-first-over is NOT attained by this public production
    sequence (the producer maximum exceeds the derivation's P
    phase, so no producible ceiling falls below it); the
    charging-adapter P-crossing mechanism is exercised directly
    by the accepted Q suite's
    test_e_p_first_over_adapter_mechanism, which is a direct
    mechanism control, NOT public T evidence and NOT a
    universal-unreachability claim.  No public P one-below
    positive is invented here."""
    n = 40
    track: dict[str, Any] = {"live": [], "max": 0}
    orig_init = _HOuter.__init__

    def counting_init(self: Any, *args: Any, **kwargs: Any) -> None:
        orig_init(self, *args, **kwargs)
        track["live"].append(self)

    monkeypatch.setattr(_HOuter, "__init__", counting_init)
    # Build 1 (generous): the per-operation producer maximum.
    _e_branch_state(mode, f"t018d-p-{mode.value}-{n}", n, track=track)
    producer_max = track["max"]
    assert producer_max > 0
    # Build 2 (strict): fully public production under the measured
    # producer maximum (the P bounds bind into the lineage key).
    ns, state, _sib_ids = _e_branch_state(
        mode, f"t018d-p-str-{mode.value}-{n}", n, p_cap=producer_max
    )
    assert ns.root_lineage_bounds.max_total_work_units == producer_max
    # The ACTUAL P cost of the public derivation on that SAME
    # strict-built ns/state (the real same-run P-domain ledger).
    col = _LedgerCollector(monkeypatch)
    r = derive_root_region_admission(state, ns)
    assert r.outcome is RootRegionAdmissionOutcome.READY
    assert r.diagnostics == ()
    assert r.g_limitation is None
    assert r.state is state
    assert r.ns is ns
    assert r.revision == state.revision
    assert r.lineage_key == state.lineage_key
    rr = r.r_result
    assert rr is not None
    assert rr.outcome is RootRegionGraphOutcome.READY
    assert rr.state is state
    assert rr.q_result is not None
    assert rr.q_result.outcome is RootRegionCurrentnessOutcome.READY
    assert rr.q_result.p_selection is not None
    assert rr.q_result.p_selection.outcome is RootSelectionOutcome.OK
    src = rr.resolved_source
    assert src is not None
    assert src.kind == "read_region"
    assert src.root_text == "Cap root.\n"
    assert src.root_digest == sha256_hex("Cap root.\n")
    adm = r.admission
    assert adm is not None
    assert adm.state is state
    assert adm.ns is ns
    assert adm.r_result is rr
    assert adm.root_entry.root_source is src
    # The discriminating shape, measured (not hardcoded): the
    # ACTUAL P phase fits the ACTUAL inherited P domain, and the
    # successful T whole EXCEEDS that domain.
    t = col.take()
    assert 0 < t["p_domain_work"] <= producer_max
    assert producer_max < r.work_units
    # honest same-run counters under the ACTUAL effective bounds
    assert 0 < r.r_work_units <= r.work_units <= r.bounds.max_total_work_units
    assert 0 < r.g_work_units <= r.g_bounds.max_total_work_units
    assert r.stage_work_units <= ns.graph_bounds.max_work_units

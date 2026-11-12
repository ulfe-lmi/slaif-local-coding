"""Inert current-root graph/admission composition derivation (018-i).

ONE bounded pure public operation over the ACTUAL retained 018-h
root-lineage state and its ACTUAL namespace: it derives, in ONE
charged operation, the ACTUAL 018-h current-root selection AND the
actual selected root source resolution (ENVELOPE from the actual
immutable D.root anchor; READ from the actual selected witness
occurrence in the SAME D state) AND the accepted 018-f current
graph over a freshly recomputed least fixed point with the selected
root as the NEW root supplier AND the canonical 018-c admission
under the selected governing root digest.

The derivation is INERT: it creates no compiler object, no cache
entry and no runtime/session ownership; it never activates the
legacy profile; the EXACT input state object is preserved on every
outcome (identity, no mutation, no CAS advance); an authoritative
differing-root (or no-selected-root) result is a fixed
``refused_root_conflict`` with NO selected source and NO ready
graph/admission -- never a bootstrap fallback.

Resource law (one charged operation):

* ONE NEW composition outer work ledger (the NEW
  ``CurrentRootCompositionBounds.max_total_work_units`` ceiling)
  charges EVERY unit of the ENTIRE operation -- H namespace/
  state/selection/source-resolution plus D/E/F/G/scanner/closure/
  key/index/model/source/sort/output work -- before the crossing
  operation;
* the accepted 018-g G total (the ACTUAL supplied
  ``CurrentAdmissionBounds`` ceiling) covers the ENTIRE F+admission
  subtree exactly as in the accepted 018-g law: it is active across
  BOTH the F phase and the G admission phase (one ledger, no reset);
  only the H and new-I phases sit outside it;
* the NEW-I phase work (the composition 10-bound-set scope key, the
  I record/wrapper model passes including the per-entry
  admission-namespace re-derivation join and the result association
  joins) charges the ONE composition outer only -- never the G
  total or the G admission stage (I1 domain law);
* the ACTUAL supplied 018-f ``CurrentGraphBounds`` ceiling counts
  ONLY the F-subtree visits while the F phase is active (the
  accepted 018-g F-phase law);
* the ACTUAL ``RootLineageBounds`` ceiling keeps its OWN independent
  H-selection domain (the composition supplies its own H-domain
  outer beneath the composition total);
* the inherited D local / E currentness / F graph-stage / G
  admission-stage ceilings keep their original units and domains;
* the selected root scanner region is prefight and charged EXACTLY
  ONCE in the actual F document/source-byte stage domains before
  the F scan (the bootstrap integrity is reused through the narrow
  typed same-run validated context; the old public bootstrap law is
  unchanged);
* no public H then public G with fresh uncharged fuel: the H
  phase, the F phase and the G phase run through ONE charged
  operation with the same retained H selection and same-run E
  overlay.
"""

from __future__ import annotations

from . import current_graph as _current_graph
from . import root_lineage as _root_lineage
from .bundle_admission import _key_canonical
from .bundle_admission_models import (
    BoundaryClass,
    BundleAdmissionNamespace,
    BundleKeyRecord,
    EntryClass,
    MemberClass,
    OwnershipGroup,
)
from .bundle_proof_models import ROOT_FILENAME
from .causal_history_models import CompletedReadOccurrence
from .current_admission import (
    _assemble_file_entries,
    _charge_entry_model,
    _GOuter,
    _GOverflow,
    _GStage,
)
from .current_admission_models import (
    CurrentAdmissionBounds,
    CurrentAdmissionLimitation,
    CurrentAdmissionPathAssociation,
)
from .current_graph_models import (
    CURRENT_GRAPH_CONTRACT_VERSION,
    CURRENT_GRAPH_POLICY_VERSION,
    CurrentGraphBounds,
    CurrentGraphResult,
)
from .current_root_composition_models import (
    ADMISSION_BOUND_FENCE_UNITS,
    CURRENT_ROOT_COMPOSITION_CONTRACT_VERSION,
    CURRENT_ROOT_COMPOSITION_POLICY_VERSION,
    ENTRY_METADATA_FENCE_UNITS,
    KEY_RECORD_FENCE_UNITS,
    PLANNER_PRECHARGE_PER_ENTRY,
    ROOT_ENTRY_FENCE_WALK_UNITS,
    CurrentRootComposition,
    CurrentRootCompositionAdmission,
    CurrentRootCompositionBounds,
    CurrentRootCompositionEntry,
    CurrentRootCompositionLimitation,
    CurrentRootCompositionOutcome,
    _closed_bounds_fence,
    canonical_rekey_calc_units,
    canonical_rekey_units,
    current_root_composition_scope_key,
    retained_content_join_file_units,
    retained_content_join_root_units,
    retained_content_join_units,
    row_shape_units,
)
from .currentness_models import CurrentnessBounds, CurrentnessGroupRecord
from .graph_models import _sha256_hex
from .root_lineage_models import (
    ROOT_LINEAGE_CONTRACT_VERSION,
    ROOT_LINEAGE_POLICY_VERSION,
    RootLineageBounds,
    RootLineageLimitation,
    RootLineageNamespace,
    RootLineageProvenance,
    RootLineageState,
    RootSelectionOutcome,
    RootSelectionResult,
    root_lineage_bounds_shape_ok,
)
from .root_region_lineage_models import (
    RootRegionLineageState as _RootRegionLineageState,
)

_L = CurrentRootCompositionLimitation


class _COverflow(Exception):
    """The NEW composition outer total crossed -- a fixed whole-
    result refusal, never a private escape."""

    __slots__ = ("limitation",)

    def __init__(self, limitation: CurrentRootCompositionLimitation) -> None:
        self.limitation = limitation
        super().__init__(limitation.value)


class _ITotal:
    """The NEW composition outer work ledger (ONE per operation).

    Charges EVERY unit of the entire operation (H phase, F phase,
    G phase and composition glue) against the NEW
    ``max_total_work_units`` ceiling BEFORE the crossing work runs;
    cumulative and never reset within the operation."""

    __slots__ = ("work_cap", "work_spent")

    def __init__(self, work_cap: int) -> None:
        self.work_cap = work_cap
        self.work_spent = 0

    def unit(self) -> None:
        if self.work_spent + 1 > self.work_cap:
            raise _COverflow(_L.TOTAL_WORK_UNITS_OVER_BOUND)
        self.work_spent += 1

    def units(self, n: int) -> None:
        for _ in range(n):
            self.unit()


class _CFacade(_GOuter):
    """The F+G phase charging facade: the accepted 018-g G outer
    (whose F-phase ceiling binds while ``begin_f``/``end_f`` is
    active) extended so that EVERY unit additionally charges the NEW
    composition total -- the accepted G-subtree total law, nested
    beneath the composition total.  Inheriting the ACTUAL ``_GOuter``
    keeps it the actual G outer for every accepted private seam (the
    F phase, entry assembly, the charged sorts) while the
    composition total keeps binding on the SAME unit."""

    __slots__ = ("itotal",)

    def __init__(
        self,
        itotal: _ITotal,
        f_bounds: CurrentGraphBounds,
        g_bounds: CurrentAdmissionBounds,
    ) -> None:
        super().__init__(f_bounds, g_bounds)
        self.itotal = itotal

    def unit(self) -> bool:
        self.itotal.unit()
        return super().unit()


class _HAdapter(_root_lineage._HOuter):
    """The H-phase charging adapter: the ACTUAL H-domain outer
    (independent ceiling) AND the NEW composition total on every
    unit.  An H-domain crossing refuses with the H fixed name; the
    composition total crossing raises the composition fixed name.
    Inheriting the ACTUAL ``_HOuter`` keeps it the real H-domain
    ledger for the accepted selection kernel and state validation.
    The G total is NOT charged during the H phase (the G subtree
    covers F+admission only)."""

    __slots__ = ("itotal",)

    def __init__(self, itotal: _ITotal, work_cap: int) -> None:
        super().__init__(work_cap)
        self.itotal = itotal

    def unit(self) -> bool:
        if not super().unit():
            return False
        self.itotal.unit()
        return True


def _refuse(
    state: RootLineageState,
    outcome: CurrentRootCompositionOutcome,
    limitations: tuple[CurrentRootCompositionLimitation, ...],
    selection: RootSelectionResult | None = None,
) -> CurrentRootComposition:
    """The fixed whole-result refusal (exact input state, no
    partial graph/entries, no selected source)."""
    return CurrentRootComposition(
        outcome=outcome,
        state=state,
        selection=selection,
        diagnostics=tuple(sorted(set(limitations), key=lambda item: item.value)),
    )


def _h_refusal(
    state: RootLineageState, limitation: RootLineageLimitation
) -> CurrentRootComposition:
    """The ACTUAL 018-h domain reason, propagated 1:1 by value,
    with the accepted H closed outcome mapping: every
    ``*_over_bound`` retained-state crossing (H-owned or mirrored
    1:1 from the actual D domain) is the fixed over-bound refusal,
    never a malformed label; the H scope names keep their fixed
    composition outcomes."""
    if limitation is RootLineageLimitation.WORK_UNITS_OVER_BOUND:
        return _refuse(
            state, CurrentRootCompositionOutcome.REFUSED_OVER_BOUND, (_L.WORK_UNITS_OVER_BOUND,)
        )
    if limitation is RootLineageLimitation.FOREIGN_SCOPE:
        return _refuse(
            state, CurrentRootCompositionOutcome.REFUSED_FOREIGN_SCOPE, (_L.FOREIGN_SCOPE,)
        )
    if limitation is RootLineageLimitation.VERSION_UNSUPPORTED:
        return _refuse(
            state,
            CurrentRootCompositionOutcome.REFUSED_VERSION_CONFLICT,
            (_L.VERSION_UNSUPPORTED,),
        )
    if limitation.value.endswith("_over_bound"):
        return _refuse(
            state, CurrentRootCompositionOutcome.REFUSED_OVER_BOUND, (_L(limitation.value),)
        )
    return _refuse(
        state,
        CurrentRootCompositionOutcome.REFUSED_STATE_MALFORMED,
        (_L(limitation.value),),
    )


def _f_refusal(state: RootLineageState, graph_result: CurrentGraphResult) -> CurrentRootComposition:
    """The fixed upstream F refusal mapping (exact F names, 1:1,
    the accepted 018-g mapping pattern)."""
    mapped = tuple(_L(limitation.value) for limitation in graph_result.diagnostics)
    outcome = CurrentRootCompositionOutcome(graph_result.outcome.value)
    return _refuse(state, outcome, mapped)


def _build_selected_root_entry(
    admission_ns: BundleAdmissionNamespace,
    root_digest: str,
    root_text: str,
    root_bytes: int,
    root_provenance: RootLineageProvenance,
    facade: _CFacade,
    stage_g: _GStage,
    workspace_bytes: int,
) -> CurrentRootCompositionEntry:
    """The required first-class root entry under the SELECTED
    governing root digest.

    Mirrors the accepted 018-g ``_build_root_entry`` reservation law
    byte-for-byte (9 / 3+3*1+1 / 28+12+8 units and the
    ``_charge_entry_model`` entry-validation reservation); the
    canonical ROOT_ENTRY key reuses the 018-c recipe; the root
    provenance is the ACTUAL 018-h ENVELOPE or READ variant bound
    to the selected source (never a fabricated anchor, envelope or
    read occurrence); the exact EMPTY root is legal.
    """
    facade.units(9)
    stage_g.units(9)  # the _v_group pass for the single root group (3k+6)
    groups = (
        OwnershipGroup(
            group_index=0,
            member_occurrence_indices=(0,),
            boundary_class=BoundaryClass.PROVEN,
            group_digest=root_digest,
        ),
    )
    facade.units(3 + 3 * 1 + 1)
    stage_g.units(3 + 3 * 1 + 1)  # 1 dict + 3 member passes + 1 group + json + hash
    canonical = _key_canonical(
        admission_ns,
        root_digest,
        EntryClass.ROOT_ENTRY,
        (ROOT_FILENAME,),
        (MemberClass.ELIGIBLE,),
        root_digest,
        groups,
    )
    content_key = _sha256_hex(canonical)
    facade.units(28 + 12 * 1 + 8 * 1)
    stage_g.units(28 + 12 * 1 + 8 * 1)  # same pass law as the file record
    key_record = BundleKeyRecord(
        mode=admission_ns.mode,
        authority_class=EntryClass.ROOT_ENTRY,
        principal=admission_ns.principal,
        session=admission_ns.session,
        repository=admission_ns.repository,
        route=admission_ns.route,
        config_fingerprint=admission_ns.config_fingerprint,
        model_identity=admission_ns.model_identity,
        workspace=admission_ns.workspace,
        root_digest=root_digest,
        reference_version=admission_ns.reference_version,
        admission_bounds=admission_ns.bounds,
        proof_bounds=admission_ns.proof_bounds,
        graph_bounds=admission_ns.graph_bounds,
        observation_bounds=admission_ns.observation_bounds,
        member_occurrences=(ROOT_FILENAME,),
        member_classes=(MemberClass.ELIGIBLE,),
        aggregate_source_digest=root_digest,
        ownership_groups=groups,
        content_key=content_key,
    )
    _charge_entry_model(
        facade,
        stage_g,
        0,
        0,
        1,
        1,
        len(root_text),
        root_bytes,
        workspace_bytes,
    )
    # The closed pre-dump metadata fence inside the entry model
    # pass (the L01 closed entry / key-record / ownership shape plus
    # the bound-model fence) is NEW-I-only constructor work (the
    # accepted 018-g root entry has no such fence): reserved on the
    # ONE composition outer ONLY before the construction that
    # triggers it (the shared entry-model reservation above keeps
    # the accepted 018-g G-total / admission-stage formula untouched
    # and is never inflated or renamed by the fence).  The root
    # record's O(n) fence walk is the fixed single-occurrence term.
    facade.itotal.units(
        KEY_RECORD_FENCE_UNITS + ENTRY_METADATA_FENCE_UNITS + ROOT_ENTRY_FENCE_WALK_UNITS
    )
    return CurrentRootCompositionEntry(
        entry_class=EntryClass.ROOT_ENTRY,
        content_key=content_key,
        key_record=key_record,
        width=1,
        member_classes=(MemberClass.ELIGIBLE,),
        root_digest=root_digest,
        root_text=root_text,
        root_source_byte_length=root_bytes,
        root_provenance=root_provenance,
        witnesses=(),
    )


def _region_state_refusal(state: object) -> ValueError | None:
    """Narrow explicit rejection of the NEW 018-p root-region
    versioned state by the OLD composition (018-p order: "the
    existing old I must honestly refuse a genuinely unsupported
    region-version state BEFORE positive use; if a narrow explicit
    rejection adapter is required, document it and test typed
    fail-closed behavior without broadening old positive law").

    The old result schema carries an ``InstanceOf[RootLineageState]``
    and cannot hold a region state without broadening the old
    positive law, so the typed fail-closed refusal is a fixed private
    raise BEFORE any old positive work or result construction.  All
    old positive behavior, types, schemas, versions and recipes are
    preserved; no old state is fabricated to fit a refusal."""
    if isinstance(state, _RootRegionLineageState):
        return ValueError(
            "current root composition: a NEW 018-p root-region "
            "lineage state is genuinely unsupported by the OLD "
            "composition (state-shape refusal "
            "REFUSED_STATE_MALFORMED / STATE_MALFORMED); no "
            "positive work is performed"
        )
    return None


def derive_current_root_composition(
    state: RootLineageState,
    ns: RootLineageNamespace,
    composition_bounds: CurrentRootCompositionBounds | None = None,
    currentness_bounds: CurrentnessBounds | None = None,
    graph_bounds: CurrentGraphBounds | None = None,
    admission_bounds: CurrentAdmissionBounds | None = None,
    lineage_bounds: RootLineageBounds | None = None,
) -> CurrentRootComposition:
    """The ONE bounded pure current-root composition derivation
    (018-i).

    Takes the ACTUAL retained 018-h state, its ACTUAL namespace and
    explicit bound overrides (defaults when omitted; each override
    is fresh actual-field validated BEFORE any fuel is read from
    it and may equal the supported default/hard values).  The input
    is the INTERNAL retained-history boundary, never a public
    supplied selection/current flag: object construction is not
    authentication and no caller-made positive snapshot establishes
    authority.  Every outcome carries the EXACT input state; a
    budget/foreign/version/malformed input is a fixed typed refusal
    with no partial graph/entries; an authoritative differing-root
    (or no-selected-root) selection is the fixed
    ``refused_root_conflict`` (no selected source, no ready
    graph/admission, never a bootstrap fallback)."""
    # --- Early O(1) fences (no scan/copy of the historical state) ----
    if not _root_lineage._state_shape(state):
        region_refusal = _region_state_refusal(state)
        if region_refusal is not None:
            raise region_refusal
        return _refuse(
            state,
            CurrentRootCompositionOutcome.REFUSED_STATE_MALFORMED,
            (_L.STATE_MALFORMED,),
        )
    if not _root_lineage._preflight_ns_shape(ns):
        return _refuse(
            state,
            CurrentRootCompositionOutcome.REFUSED_FOREIGN_SCOPE,
            (_L.FOREIGN_SCOPE,),
        )
    if state.d_state.root is None:
        return _refuse(state, CurrentRootCompositionOutcome.REFUSED_NO_ROOT, (_L.NO_ROOT,))

    # --- Fresh bound validation (fixed closed-int models) BEFORE any
    # --- fuel is read from the overrides.  The CLOSED scalar fence
    # --- runs BEFORE any serializer dump can walk an unexpected
    # --- container (I8: a model_copy bypass cannot smuggle a
    # --- wrong-shape field past the fence; the accepted H shape law
    # --- is mirrored for the H-domain override).
    try:
        if composition_bounds is not None:
            _closed_bounds_fence(composition_bounds, "composition_bounds")
        effective_c = CurrentRootCompositionBounds.model_validate(
            CurrentRootCompositionBounds().model_dump(mode="python", warnings=False)
            if composition_bounds is None
            else composition_bounds.model_dump(mode="python", warnings=False)
        )
    except Exception:
        raise ValueError(
            "current root composition bounds failed the actual composition validation"
        ) from None
    if lineage_bounds is not None and not root_lineage_bounds_shape_ok(lineage_bounds):
        return _refuse(
            state,
            CurrentRootCompositionOutcome.REFUSED_STATE_MALFORMED,
            (_L.MALFORMED_BINDING,),
        )
    try:
        effective_lineage = RootLineageBounds.model_validate(
            ns.root_lineage_bounds.model_dump(mode="python", warnings=False)
            if lineage_bounds is None
            else lineage_bounds.model_dump(mode="python", warnings=False)
        )
    except Exception:
        return _refuse(
            state,
            CurrentRootCompositionOutcome.REFUSED_STATE_MALFORMED,
            (_L.MALFORMED_BINDING,),
        )
    try:
        if graph_bounds is not None:
            _closed_bounds_fence(graph_bounds, "graph_bounds")
        effective_f = CurrentGraphBounds.model_validate(
            CurrentGraphBounds().model_dump(mode="python", warnings=False)
            if graph_bounds is None
            else graph_bounds.model_dump(mode="python", warnings=False)
        )
    except Exception:
        raise ValueError(
            "current graph bounds failed the actual current-graph validation"
        ) from None
    try:
        if admission_bounds is not None:
            _closed_bounds_fence(admission_bounds, "admission_bounds")
        effective_g = CurrentAdmissionBounds.model_validate(
            CurrentAdmissionBounds().model_dump(mode="python", warnings=False)
            if admission_bounds is None
            else admission_bounds.model_dump(mode="python", warnings=False)
        )
    except Exception:
        raise ValueError(
            "current admission bounds failed the actual current-admission validation"
        ) from None
    try:
        if currentness_bounds is not None:
            _closed_bounds_fence(currentness_bounds, "currentness_bounds")
    except Exception:
        raise ValueError("currentness bounds failed the actual currentness validation") from None

    itotal = _ITotal(effective_c.max_total_work_units)
    facade = _CFacade(itotal, effective_f, effective_g)
    stage_f = _current_graph._StageLedger(ns.graph_bounds)
    stage_g = _GStage(ns.graph_bounds)
    d_ns = _root_lineage._d_namespace(ns)  # the ACTUAL derived D scope

    # --- ACTUAL 018-h phase (independent H ceiling beneath the total)
    try:
        adapter = _HAdapter(itotal, effective_lineage.max_total_work_units)
        if not adapter.units(11):
            return _refuse(
                state,
                CurrentRootCompositionOutcome.REFUSED_OVER_BOUND,
                (_L.WORK_UNITS_OVER_BOUND,),
            )
        if state.lineage_key != ns.lineage_key:
            return _refuse(
                state,
                CurrentRootCompositionOutcome.REFUSED_FOREIGN_SCOPE,
                (_L.FOREIGN_SCOPE,),
            )
        if state.d_state.history_key != ns.history_key:
            return _refuse(
                state,
                CurrentRootCompositionOutcome.REFUSED_FOREIGN_SCOPE,
                (_L.FOREIGN_SCOPE,),
            )
        for actual, supported in _root_lineage._version_pairs(ns):
            if actual != supported:
                return _refuse(
                    state,
                    CurrentRootCompositionOutcome.REFUSED_VERSION_CONFLICT,
                    (_L.VERSION_UNSUPPORTED,),
                )
        if not adapter.units(_root_lineage._ns_reservation(ns)):
            return _refuse(
                state,
                CurrentRootCompositionOutcome.REFUSED_OVER_BOUND,
                (_L.WORK_UNITS_OVER_BOUND,),
            )
        if not _root_lineage._revalidate_h_ns(ns):
            return _refuse(
                state,
                CurrentRootCompositionOutcome.REFUSED_FOREIGN_SCOPE,
                (_L.FOREIGN_SCOPE,),
            )
        if not adapter.unit():
            return _refuse(
                state,
                CurrentRootCompositionOutcome.REFUSED_OVER_BOUND,
                (_L.WORK_UNITS_OVER_BOUND,),
            )
        # The retained-state integrity binds the ACTUAL namespace
        # retention policy, INDEPENDENTLY of the operation override:
        # a wider lineage override governs ONLY the H-domain
        # operation work fuel (the ``_HAdapter`` ceiling above) and
        # the scope-key binding -- it can never legitimize a
        # retained state that already exceeds its own namespace
        # caps.  The override may be STRICTER on work without
        # loosening retention: the adapter ceiling and the
        # validator's own backstop both keep binding.
        problem = _root_lineage.validate_root_lineage_state(
            state,
            ns.root_lineage_bounds,
            adapter,
            history_bounds=ns.history_bounds,
            graph_bounds=ns.graph_bounds,
            proof_bounds=ns.proof_bounds,
            observation_bounds=ns.observation_bounds,
            workspace=ns.workspace,
        )
        if problem is not None:
            return _h_refusal(state, problem)

        # --- ACTUAL same-run selection (the accepted H law) ---------
        selection = _root_lineage._selection_kernel(state, state.d_state, adapter)
        if selection.outcome is RootSelectionOutcome.REFUSED:
            return _h_refusal(state, selection.limitations[0])
        if selection.outcome in (
            RootSelectionOutcome.ROOT_CONTENT_CONFLICT,
            RootSelectionOutcome.NO_SELECTED_ROOT,
        ):
            # Authoritative differing-root (or no selected root):
            # NO selected source, NO ready graph/admission, NEVER a
            # bootstrap fallback -- the actual selection is carried.
            return _refuse(
                state,
                CurrentRootCompositionOutcome.REFUSED_ROOT_CONFLICT,
                (_L.ROOT_CONFLICT,),
                selection=selection,
            )

        # --- ACTUAL selected root source resolution ------------------
        d_state = state.d_state
        anchor = d_state.root
        assert anchor is not None  # fenced above
        witness = selection.witness_facts[0]  # the first canonical maximum
        provenance = witness.provenance
        if provenance.kind == "envelope":
            if not adapter.unit():
                return _refuse(
                    state,
                    CurrentRootCompositionOutcome.REFUSED_OVER_BOUND,
                    (_L.WORK_UNITS_OVER_BOUND,),
                )
            if (
                provenance.root_digest != anchor.root_digest
                or provenance.source_byte_length != anchor.source_byte_length
                or provenance.workspace != ns.workspace
            ):
                return _refuse(
                    state,
                    CurrentRootCompositionOutcome.REFUSED_STATE_MALFORMED,
                    (_L.MALFORMED_BINDING,),
                )
            root_text = anchor.root_text
            root_digest = anchor.root_digest
            root_bytes = anchor.source_byte_length
        else:
            occurrence: CompletedReadOccurrence | None = None
            for candidate in d_state.occurrences:
                if not adapter.unit():
                    return _refuse(
                        state,
                        CurrentRootCompositionOutcome.REFUSED_OVER_BOUND,
                        (_L.WORK_UNITS_OVER_BOUND,),
                    )
                if candidate.occurrence_id == provenance.occurrence_id:
                    occurrence = candidate
                    break
            if occurrence is None:
                return _refuse(
                    state,
                    CurrentRootCompositionOutcome.REFUSED_STATE_MALFORMED,
                    (_L.MALFORMED_BINDING,),
                )
            if not adapter.unit():
                return _refuse(
                    state,
                    CurrentRootCompositionOutcome.REFUSED_OVER_BOUND,
                    (_L.WORK_UNITS_OVER_BOUND,),
                )
            if (
                occurrence.call_id != provenance.call_id
                or occurrence.endpoint != provenance.endpoint
            ):
                return _refuse(
                    state,
                    CurrentRootCompositionOutcome.REFUSED_STATE_MALFORMED,
                    (_L.MALFORMED_BINDING,),
                )
            proof = occurrence.proof
            if not adapter.unit():
                return _refuse(
                    state,
                    CurrentRootCompositionOutcome.REFUSED_OVER_BOUND,
                    (_L.WORK_UNITS_OVER_BOUND,),
                )
            if proof.root_path != ROOT_FILENAME or proof.root_digest != anchor.root_digest:
                return _refuse(
                    state,
                    CurrentRootCompositionOutcome.REFUSED_STATE_MALFORMED,
                    (_L.MALFORMED_BINDING,),
                )
            region_bytes = 0
            for segment in proof.segments:
                if not adapter.unit():
                    return _refuse(
                        state,
                        CurrentRootCompositionOutcome.REFUSED_OVER_BOUND,
                        (_L.WORK_UNITS_OVER_BOUND,),
                    )
                region_bytes += segment.byte_length
            if not adapter.unit():
                return _refuse(
                    state,
                    CurrentRootCompositionOutcome.REFUSED_OVER_BOUND,
                    (_L.WORK_UNITS_OVER_BOUND,),
                )
            # A complete singleton root read: the root member is the
            # read target and the whole-read aggregate is the root
            # body (the H retention law).
            root_member = False
            for member in proof.requested_members:
                if not adapter.unit():
                    return _refuse(
                        state,
                        CurrentRootCompositionOutcome.REFUSED_OVER_BOUND,
                        (_L.WORK_UNITS_OVER_BOUND,),
                    )
                if member.normalized is not None and member.normalized == ROOT_FILENAME:
                    root_member = True
            if not root_member or region_bytes != provenance.read_byte_length:
                return _refuse(
                    state,
                    CurrentRootCompositionOutcome.REFUSED_STATE_MALFORMED,
                    (_L.MALFORMED_BINDING,),
                )
            root_text = proof.source_text
            root_digest = provenance.read_digest
            root_bytes = provenance.read_byte_length

        # --- ACTUAL 018-f phase: the selected root scanner region is
        # --- prefight/charged ONCE in the F document/source-byte
        # --- domains inside _derive_graph (the accepted G total AND
        # --- the F-subtree ceiling bind through the facade) --------
        facade.begin_f()
        try:
            graph_result, overlay = _current_graph._derive_graph(
                d_state,
                d_ns,
                effective_f,
                currentness_bounds,
                facade,
                stage_f,
                root_text=root_text,
                root_digest=root_digest,
            )
        finally:
            facade.end_f()
        if graph_result.outcome.value != "ok":
            return _f_refusal(state, graph_result)
        graph = graph_result.overlay
        assert graph is not None  # ok carries its graph (model law)
        assert overlay is not None  # ok carries its overlay (model law)

        # --- ACTUAL 018-g admission phase under the SELECTED root ---
        # The same G outer instance keeps the G total active across
        # BOTH phases (the accepted 018-g G-subtree law).
        facade.unit()
        stage_g.unit()
        try:
            admission_ns = BundleAdmissionNamespace(
                principal=ns.principal,
                session=ns.session,
                repository=ns.repository,
                route=ns.route,
                model_identity=ns.model_identity,
                config_fingerprint=ns.config_fingerprint,
                workspace=ns.workspace,
                mode=ns.mode,
                admission_version=ns.admission_version,
                observation_version=ns.observation_version,
                graph_version=ns.graph_version,
                reference_version=ns.reference_version,
                proof_version=ns.proof_version,
                bounds=ns.bounds,
                proof_bounds=ns.proof_bounds,
                graph_bounds=ns.graph_bounds,
                observation_bounds=ns.observation_bounds,
                namespace_key=ns.admission_namespace_key,
                scoped_key=ns.admission_scoped_key,
            )
        except Exception:
            return _refuse(
                state,
                CurrentRootCompositionOutcome.REFUSED_FOREIGN_SCOPE,
                (_L.FOREIGN_SCOPE,),
            )

        eligible: dict[str, int] = {}
        for node in graph.nodes:
            facade.unit()
            stage_g.unit()
            eligible[node.path] = node.depth
        groups_by_occ: dict[str, list[CurrentnessGroupRecord]] = {}
        for group in overlay.groups:
            facade.unit()
            stage_g.unit()
            groups_by_occ.setdefault(group.occurrence_id, []).append(group)

        facade.units(2)
        stage_g.units(2)  # the ONE workspace byte-length measurement
        workspace_bytes = len(ns.workspace.encode("utf-8"))
        # The file-entry pre-dump metadata fence reservation
        # (L01/M01): every newly constructed file entry's
        # ``_v_entry`` runs the closed M01 entry / key-record /
        # ownership metadata fence (the four carried bound models
        # BEFORE the accepted helpers may serialize them, the O(1)
        # length gates under the ACTUAL inherited caps before any
        # element visit, the bounded scalar / path / index / enum
        # walks, the dense group ordering and the unique partition
        # law).  Constructions are bounded by the plan count, which
        # is bounded by the proof segment count per occurrence, and
        # each entry's walks are bounded by fifteen times its
        # occurrence's member positions plus the per-path byte-cap
        # walk, the segment / witness / group dimensions under the
        # actual inherited caps (the accepted per-dimension
        # coefficients): the closed upper bound is charged BEFORE
        # the assembly (the charged O(occurrences) metadata walk
        # carries no source inspection).  The per-segment planning
        # visits are precharged from the VALIDATED segment count
        # BEFORE the first segment element is fetched, and BEFORE
        # their bounds enter the reservation (M02/018-n).
        path_cap = min(ns.graph_bounds.max_path_bytes, ns.observation_bounds.max_path_bytes)
        plan_fixed = 0
        plan_walk = 0
        # 018-n: the LEAF retained-content join runs inside the
        # G-stage entry construction (the entry model validator),
        # BEFORE the later parent-boundary join charges: the NEW-I
        # join work of that leaf run is precharged on the ONE
        # composition outer HERE, closed at the plan metadata (the
        # retained root text length; per planned occurrence the
        # segment count and the ACTUAL declared member ceiling).
        # The accepted G plan admits EITHER the whole bundle (one
        # entry) OR one singleton entry per isolated all-eligible
        # segment (at most one per planned segment, never the whole
        # plus isolated rows together).  Isolated segments are
        # DISJOINT, so the total sliced / joined / encoded /
        # hashed characters over ALL isolated entries is at most
        # the retained source character length: the source work is
        # reserved ONCE per occurrence, never multiplied by the
        # segment count (multiplying it could consume the whole I
        # cap for an ordinary mixed proof), while the per-entry
        # fixed / traversal / member work is reserved at the
        # singleton bound per planned segment (n > 0: that
        # aggregate dominates the whole-bundle alternative).  The
        # accepted G stage formulas stay untouched.
        plan_join = retained_content_join_root_units(len(root_text))
        for occurrence in d_state.occurrences:
            itotal.unit()
            segments = occurrence.proof.segments
            n_segments = len(segments)
            # 018-n: the per-segment planning visits are precharged
            # from the VALIDATED segment count BEFORE the first
            # segment element is fetched (the M02 per-segment
            # domain and cost are unchanged: one unit per segment,
            # charged as the closed count instead of interleaved
            # with the fetch).
            itotal.units(n_segments)
            member_positions = 0
            for segment in segments:
                member_positions += len(segment.member_positions)
            if n_segments:
                plan_fixed += KEY_RECORD_FENCE_UNITS + ENTRY_METADATA_FENCE_UNITS
                group_count = len(groups_by_occ.get(occurrence.occurrence_id, ()))
                plans_cap = max(1, n_segments, group_count)
                plan_walk += (
                    15 * member_positions
                    + member_positions * (path_cap + 1)
                    + 3 * n_segments
                    + 6 * plans_cap
                    + 4 * plans_cap * n_segments
                    + 2 * group_count
                )
                plan_join += (
                    n_segments
                    * retained_content_join_file_units(
                        1,
                        n_segments,
                        0,
                        ns.proof_bounds.max_members,
                    )
                    + 10 * occurrence.proof.source_char_length
                )
        itotal.units(plan_fixed + plan_walk + plan_join)
        if root_bytes > ns.graph_bounds.max_single_source_bytes:
            raise _GOverflow(CurrentAdmissionLimitation.ENTRY_SOURCE_BYTES_OVER_BOUND)
        if root_bytes > effective_g.max_total_entry_source_bytes:
            raise _GOverflow(CurrentAdmissionLimitation.TOTAL_ENTRY_SOURCE_BYTES_OVER_BOUND)
        root_entry = _build_selected_root_entry(
            admission_ns,
            root_digest,
            root_text,
            root_bytes,
            provenance,
            facade,
            stage_g,
            workspace_bytes,
        )
        total_entry_bytes = root_bytes

        entries, path_keys, attempts, member_occ_charged, total_entry_bytes, diagnostics = (
            _assemble_file_entries(
                d_state,
                d_ns,
                admission_ns,
                root_digest,
                effective_g,
                workspace_bytes,
                root_entry.content_key,
                total_entry_bytes,
                groups_by_occ,
                eligible,
                CurrentRootCompositionEntry,
                facade,
                stage_g,
                selected_root_digest=root_digest,
            )
        )

        # --- Reverse-index rows (the accepted G charged pattern) ----
        path_associations = []
        for path, keys in _current_graph._sorted(
            path_keys.items(), lambda item: item[0], facade, stage_g
        ):
            facade.units(1 + 2 * len(keys))
            stage_g.units(1 + 2 * len(keys))
            path_associations.append(
                CurrentAdmissionPathAssociation(
                    scoped_key=admission_ns.scoped_key,
                    path=path,
                    content_keys=tuple(_current_graph._sorted(keys, None, facade, stage_g)),
                    is_root=path == ROOT_FILENAME,
                )
            )
        facade.units(len(path_associations))
        stage_g.units(len(path_associations))
        associations = tuple(path_associations)

        sorted_keys = _current_graph._sorted(entries, None, facade, stage_g)
        facade.units(len(sorted_keys))
        stage_g.units(len(sorted_keys))
        file_entries = tuple(entries[key] for key in sorted_keys)

        # --- The I derivation scope key (10 bound sets) --------------
        # The composition identity is NEW-I work: charged to the ONE
        # composition outer only, OUTSIDE the accepted G total and the
        # G admission stage (which cover the F+admission subtree
        # exactly as in the accepted 018-g law).
        bound_models = (
            effective_c,
            overlay.bounds,
            effective_f,
            ns.bounds,
            effective_g,
            ns.proof_bounds,
            ns.graph_bounds,
            ns.observation_bounds,
            ns.history_bounds,
            effective_lineage,
        )
        fence_units = sum(len(type(bound).model_fields) for bound in bound_models)
        scope_key_units = 2 * fence_units + 10 + 10 + 1 + 1 + 1 + 1
        itotal.units(scope_key_units)
        scope_key = current_root_composition_scope_key(
            d_state.history_key,
            ns.workspace,
            root_digest,
            ns.lineage_key,
            ns.lineage_id,
            d_state.revision,
            CURRENT_ROOT_COMPOSITION_CONTRACT_VERSION,
            CURRENT_ROOT_COMPOSITION_POLICY_VERSION,
            ns.admission_version,
            ns.observation_version,
            ns.graph_version,
            ns.reference_version,
            ns.proof_version,
            ns.history_version,
            ns.arguments_version,
            ROOT_LINEAGE_CONTRACT_VERSION,
            ROOT_LINEAGE_POLICY_VERSION,
            graph.currentness_contract_version,
            graph.currentness_policy_version,
            graph.currentness_recipe_version,
            CURRENT_GRAPH_CONTRACT_VERSION,
            CURRENT_GRAPH_POLICY_VERSION,
            overlay.scope_key,
            graph.scope_key,
            ns.admission_namespace_key,
            ns.admission_scoped_key,
            effective_c,
            overlay.bounds,
            effective_f,
            ns.bounds,
            effective_g,
            ns.proof_bounds,
            ns.graph_bounds,
            ns.observation_bounds,
            ns.history_bounds,
            effective_lineage,
        )

        association_key_count = sum(len(keys) for keys in path_keys.values())
        # The G-mirroring admission output walk (the accepted 018-g
        # CurrentAdmission record walk over the G admission records:
        # construction, root binding, the key/adjacency/root-
        # membership walks, entry visits, row walks, reverse-index
        # lookups and the reason sorted/dedup walk plus count/cap
        # binding) stays in the G total AND the G admission stage.
        admission_output_units = (
            19
            + 3 * len(file_entries)
            + 3 * len(associations)
            + association_key_count
            + member_occ_charged
            + 2
            + len(diagnostics)
        )
        facade.units(admission_output_units)
        stage_g.units(admission_output_units)
        # The NEW-I wrapper delta on the SAME construction: the I
        # record's extra bound/version/metadata fields (27 - 19)
        # plus the model walk's NEW-derivation-cap shape check and
        # binding (2 units), the I scope-key re-verification pass
        # and the admission model's per-entry ACTUAL namespace
        # re-derivation join (the accepted reconstruction law,
        # fixed ~60 units upper-rounded to 64, PLUS the scoped-key
        # workspace encode pass 2*workspace_bytes) for the root
        # entry plus every file entry -- charged to the ONE
        # composition outer only.
        # The M02/018-n reservation-calculation precharge in strict
        # order on the ONE composition outer: FIRST the closed O(1)
        # work of the tuple expansion plus the walk-free planner
        # evaluation is charged BEFORE the expansion allocates or
        # the planner may run; THEN the walk-free planner result
        # (no group / witness / element visit, no allocation beyond
        # the running sums) is evaluated and charged, reserving the
        # ACTUAL per-entry reservation-calculation encode / loop /
        # allocation work; ONLY THEN may that calculation (and the
        # row-shape / join-sum evaluations) run; the resulting
        # per-entry canonical re-derivation reservation plus the
        # 018-n retained-content-join reservation are charged
        # BEFORE the construction may fence, join, serialize, hash
        # or walk any element.
        entry_count = 1 + len(file_entries)
        itotal.units(entry_count * PLANNER_PRECHARGE_PER_ENTRY + 4)
        entry_tuples = (root_entry, *file_entries)
        calc_units = (
            sum(canonical_rekey_calc_units(e.key_record, e) for e in entry_tuples)
            + 2 * entry_count
            + 2 * len(associations)
        )
        itotal.units(calc_units)
        rekey_sum = sum(canonical_rekey_units(e.key_record, e) for e in entry_tuples)
        row_sum = sum(row_shape_units(row.content_keys) for row in associations)
        join_sum = sum(retained_content_join_units(e) for e in entry_tuples)
        itotal.units(
            10
            + scope_key_units
            # The admission record's per-entry key-record re-fence
            # (I8/M01): the closed four-bound-model fence walk per
            # retained entry plus the scoped-key workspace encode
            # pass, charged before the construction.
            + (64 + 2 * workspace_bytes + KEY_RECORD_FENCE_UNITS) * entry_count
            # The M01 closed TEN admission bound-model fence runs
            # inside the admission construction (re-fenced before
            # the first inherited cap is read on BOTH parent
            # boundaries): bounded METADATA work, upper-bound-
            # charged BEFORE the construction that performs it.
            + ADMISSION_BOUND_FENCE_UNITS
            # The J01/J02 actual-field association joins run inside
            # the admission construction: one selected-digest
            # comparison per file entry plus its key-record
            # governing field (J01), the expected reverse-relation
            # build over the retained member occurrences and the
            # per-row path/scope/flag/membership/key-set checks with
            # the completeness set (J02).  Bounded METADATA work,
            # upper-rounded here BEFORE the construction that
            # performs it.
            + 2
            + 2 * len(file_entries)
            + member_occ_charged
            + 4 * len(associations)
            + association_key_count
            # The K01/K02 ACTUAL canonical re-derivation and row
            # shape fences run inside the admission construction
            # for the root entry plus every file entry: per entry
            # the M01 closed bound fences, the retained digest and
            # content-key comparisons and the accepted C recipe
            # re-derivation (three bound-model dump passes and
            # five sha256 passes at the ACTUAL field lengths), and
            # per reverse-index row the closed tuple/scalar/
            # distinct/sorted shape fence before the set
            # comparison.  Bounded METADATA work, upper-bound-
            # charged BEFORE the construction that performs it.
            + rekey_sum
            + row_sum
            # The 018-n retained-content join re-runs inside the
            # admission construction (the preflighted root-bytes
            # encode / hash and the admitted region's member /
            # digest re-derivation from the retained original
            # proof): upper-bound-charged BEFORE the construction
            # that performs it.
            + join_sum
        )
        # The model walk's ACTUAL input-namespace D re-derivation
        # (the canonical history-field pass over the root entry key
        # record context plus one encode/hash) is NEW-I wrapper
        # work of the same class as the scope-key re-verification:
        # charged to the ONE composition outer only.
        itotal.units(scope_key_units)
        admission = CurrentRootCompositionAdmission(
            history_key=d_state.history_key,
            revision=d_state.revision,
            workspace=ns.workspace,
            root_path=ROOT_FILENAME,
            root_digest=root_digest,
            lineage_key=ns.lineage_key,
            lineage_id=ns.lineage_id,
            admission_version=ns.admission_version,
            observation_version=ns.observation_version,
            graph_version=ns.graph_version,
            reference_version=ns.reference_version,
            proof_version=ns.proof_version,
            history_version=ns.history_version,
            arguments_version=ns.arguments_version,
            lineage_contract_version=ROOT_LINEAGE_CONTRACT_VERSION,
            lineage_policy_version=ROOT_LINEAGE_POLICY_VERSION,
            currentness_contract_version=graph.currentness_contract_version,
            currentness_policy_version=graph.currentness_policy_version,
            currentness_recipe_version=graph.currentness_recipe_version,
            graph_contract_version=graph.contract_version,
            graph_policy_version=graph.policy_version,
            contract_version=CURRENT_ROOT_COMPOSITION_CONTRACT_VERSION,
            policy_version=CURRENT_ROOT_COMPOSITION_POLICY_VERSION,
            bounds=effective_c,
            currentness_bounds=overlay.bounds,
            graph_bounds=effective_f,
            admission_bounds=ns.bounds,
            admission_derivation_bounds=effective_g,
            proof_bounds=ns.proof_bounds,
            inherited_graph_bounds=ns.graph_bounds,
            observation_bounds=ns.observation_bounds,
            history_bounds=ns.history_bounds,
            lineage_bounds=effective_lineage,
            currentness_scope_key=overlay.scope_key,
            graph_scope_key=graph.scope_key,
            admission_namespace_key=admission_ns.namespace_key,
            admission_scoped_key=admission_ns.scoped_key,
            scope_key=scope_key,
            root_entry=root_entry,
            entries=file_entries,
            path_associations=associations,
            graph=graph,
            work_units=itotal.work_spent,
            entry_source_bytes=total_entry_bytes,
            entries_retained=1 + len(file_entries),
            member_occurrences_charged=member_occ_charged,
            reverse_association_attempts=attempts,
            emitted_admission_reasons=len(diagnostics),
            admission_reasons=diagnostics,
        )

        # --- The composition result (the charged model pass) --------
        surfaced = (
            (_L.ROOT_SOURCE_UNPROVEN,)
            if "root_source_unproven" in {item.value for item in selection.limitations}
            else ()
        )
        # The result model's ACTUAL join work (upper bound): the
        # fixed scope/revision/identity joins, the per-witness
        # retained-fact search (up to one linear pass over the
        # retained root facts per selected witness), the provenance
        # witness scan and the surfaced-limitation set pass.  This is
        # NEW-I wrapper association work: charged to the ONE
        # composition outer only, OUTSIDE the accepted G total and
        # the G admission stage (the I1 domain law: the G total
        # covers the F+admission subtree exactly; only the H and
        # new-I phases sit outside it).
        witness_count = len(selection.witness_facts)
        retained_count = len(state.root_facts)
        limitation_count = len(selection.limitations)
        # The ACTUAL input-state proof/witness join (I7) adds
        # charged metadata work on the I outer: the two O(m)
        # occurrence index constructions (by occurrence ID and by
        # proof identity), the READ selected-provenance occurrence
        # re-bind (at most 3 comparisons), one proof-identity probe
        # per file entry, and per witness the index lookup plus the
        # three original coordinate re-checks plus the occurrence-
        # local segment span check (one per segment).  No source
        # bytes are rewalked -- metadata only.
        occurrence_count = len(d_state.occurrences)
        file_entry_count = len(file_entries)
        # 018-n: the count walks are charged BEFORE they run: the
        # per-entry witness-count pass and the nested per-witness
        # segment-index pass are closed per-element work, reserved
        # on the ONE composition outer before the first element is
        # read (the callers no longer expand entries or count
        # witnesses before the charge).
        itotal.units(3 * file_entry_count + 2)
        entry_witness_count = sum(len(entry.witnesses) for entry in file_entries)
        itotal.units(3 * entry_witness_count + 2)
        entry_segment_count = sum(
            len(witness.segment_indices) for entry in file_entries for witness in entry.witnesses
        )
        # The M02/018-n reservation-calculation precharge for the
        # RESULT reservation in strict order: the closed O(1) work
        # of the walk-free planner evaluation is charged BEFORE it
        # may run; the walk-free planner result (no group /
        # witness / element visit) is then evaluated and charged,
        # reserving the ACTUAL per-entry reservation-calculation
        # encode / loop / allocation work; ONLY THEN may that
        # calculation (and the row-shape / join-sum evaluations)
        # run; the resulting per-entry canonical re-derivation
        # reservation plus the 018-n retained-content-join
        # reservation are charged BEFORE the result construction
        # may fence, join, serialize, hash or walk any element.
        entry_count = 1 + file_entry_count
        itotal.units(entry_count * PLANNER_PRECHARGE_PER_ENTRY + 4)
        calc_units = (
            sum(canonical_rekey_calc_units(e.key_record, e) for e in (root_entry, *file_entries))
            + 2 * entry_count
            + 2 * len(associations)
        )
        itotal.units(calc_units)
        rekey_sum = sum(canonical_rekey_units(e.key_record, e) for e in (root_entry, *file_entries))
        row_sum = sum(row_shape_units(row.content_keys) for row in associations)
        join_sum = sum(retained_content_join_units(e) for e in (root_entry, *file_entries))
        result_units = (
            28
            + witness_count * (retained_count + 3)
            + 2 * limitation_count
            + 2 * occurrence_count
            + 1
            + 3
            + 1
            + file_entry_count
            + 5 * entry_witness_count
            + entry_segment_count
            # The M01 closed TEN admission bound-model fence runs
            # AGAIN on the nested admission inside the result
            # construction: the same bounded metadata upper bound
            # as the admission-construction reservation.
            + ADMISSION_BOUND_FENCE_UNITS
            # The J01/J02 actual-field association re-joins run
            # AGAIN on the nested admission inside the result
            # construction (a model_copy-bypassed nested record is
            # re-checked on the ok path): the same bounded metadata
            # upper bound as the admission-construction reservation.
            + 2
            + 2 * file_entry_count
            + member_occ_charged
            + 4 * len(associations)
            + association_key_count
            # The K01/K02 ACTUAL canonical re-derivation and row
            # shape fences run AGAIN on the nested admission
            # inside the result construction: the same bounded
            # metadata upper bound as the admission-construction
            # reservation (the M01 per-entry fence walk term).
            + rekey_sum
            + row_sum
            # The 018-n retained-content join re-runs AGAIN on the
            # nested admission inside the result construction (the
            # preflighted root-bytes encode / hash and the admitted
            # region's member / digest re-derivation from the
            # retained original proof): upper-bound-charged BEFORE
            # the construction that performs it.
            + join_sum
        )
        itotal.units(result_units)
        return CurrentRootComposition(
            outcome=CurrentRootCompositionOutcome.OK,
            state=state,
            selection=selection,
            selected_root_provenance=provenance,
            selected_root_source_byte_length=root_bytes,
            graph=graph,
            admission=admission,
            diagnostics=surfaced,
        )
    except _COverflow as overflow:
        return _refuse(
            state, CurrentRootCompositionOutcome.REFUSED_OVER_BOUND, (overflow.limitation,)
        )
    except _GOverflow as overflow:
        return _refuse(
            state,
            CurrentRootCompositionOutcome.REFUSED_OVER_BOUND,
            (_L(overflow.limitation.value),),
        )
    except _current_graph._StageOverflow as overflow:
        return _refuse(
            state,
            CurrentRootCompositionOutcome.REFUSED_OVER_BOUND,
            (_L(overflow.limitation.value),),
        )
    except _current_graph._Malformed as malformed:
        return _refuse(
            state,
            CurrentRootCompositionOutcome.REFUSED_STATE_MALFORMED,
            (_L(malformed.limitation.value),),
        )
    except ValueError:
        # A retained source region is not valid UTF-8 (or an entry
        # model refused the assembled record): the fixed state-
        # malformed refusal, never an uncaught encode error.
        return _refuse(
            state,
            CurrentRootCompositionOutcome.REFUSED_STATE_MALFORMED,
            (_L.STATE_MALFORMED,),
        )

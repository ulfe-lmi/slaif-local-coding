"""Pure versioned root-region currentness derivation (objective 018-q).

``derive_root_region_currentness`` is the ONE bounded pure query above
the accepted 018-p root-region producer: it retains the EXACT input
P state by reference on EVERY outcome, recomputes the actual same-run
P validation and authority selection under the ACTUAL independent P
domain (coupled unit-for-unit into the ONE Q outer, the accepted
``_HAdapter`` composition law -- no second full-P public call, no
reset ledger, no pre-reserved whole P ceiling), then assesses the
combined evidence frontier of actual authoritative P facts and
eligible uncertainty occurrences over the SAME actual D state
(frozen parent evidence only) and interprets currentness.

Refusal precedence (explicit and fixed): O(1) shape/scope/version/
bounds fences; the ACTUAL P phase (the namespace
reservation/revalidation phase included) under the ACTUAL independent
P domain coupled unit-for-unit into the ONE Q total; the actual P
validation (its ACTUAL reason carried before selection, never a
fabricated P result); the actual P authority-selection
refusal/conflict/no-root mapping, each mapped early result precharging
its OWN bounded result construction before it is built; then the
charged uncertainty/currentness assessment before any ready
interpretation.  A malformed non-P state fails with a fixed private
ValueError BEFORE result construction.  A Q work crossing keeps
whatever ACTUAL P selection was already computed.  The query never
advances a revision, never mints a root authority fact and never copies
source.
"""

from __future__ import annotations

from .bundle_proof_models import ROOT_FILENAME
from .causal_history import _ancestors_of
from .causal_history_models import (
    CAUSAL_ROOT_FACT,
    CausalHistoryState,
    ResultFingerprintRecord,
)
from .graph_models import _fixed
from .root_lineage import _RESULT_BUILD_UNITS, _RESULT_FACT_UNITS, _HOuter
from .root_lineage_models import RootLineageLimitation, RootSelectionOutcome
from .root_region_currentness_models import (
    ROOT_REGION_CURRENTNESS_CONTRACT_VERSION,
    ROOT_REGION_CURRENTNESS_POLICY_VERSION,
    RootRegionCurrentnessBounds,
    RootRegionCurrentnessDiagnostic,
    RootRegionCurrentnessOutcome,
    RootRegionCurrentnessResult,
    RootRegionUncertaintyClass,
    RootRegionUncertaintyWitness,
    root_region_currentness_bounds_shape_ok,
    root_region_currentness_scope_key,
)
from .root_region_lineage import (
    _region_ns_reservation,
    _region_preflight_ns_shape,
    _region_revalidate_ns,
    _region_selection_kernel,
    _region_state_shape,
    _region_version_pairs,
    validate_root_region_lineage_state,
)
from .root_region_lineage_models import (
    RootRegionLineageNamespace,
    RootRegionLineageState,
    RootRegionSelectionResult,
    _region_provenance_key,
)

#: Fixed Q base charge: the early gates, the adapter/ledger
#: construction and the scope-key recomputation BEFORE the first
#: positive work.
_Q_BASE_UNITS = 12
#: One charged uncertainty witness construction (bounded immutable
#: references + closed metadata joins, charged BEFORE the record
#: builds).
_Q_WITNESS_UNITS = 12
#: Per-witness result-construction charge (the P result fact unit).
_Q_RESULT_WITNESS_UNITS = _RESULT_FACT_UNITS


class _QOverflow(Exception):
    """The ONE Q outer crossed: a fixed private resource fact.

    The public derivation maps it to the typed atomic over-bound
    refusal preserving the EXACT prior state and whatever actual P
    selection was already computed."""


class _QOuter:
    """ONE Q outer work ledger over the ENTIRE derivation.

    Charges EVERY unit of the whole operation (early gates, the
    coupled P phase, evidence inventory, membership/ancestry,
    maxima/dominance, canonical sorting/dedup and result/model
    construction) against the ACTUAL ``max_total_work_units`` BEFORE
    the crossing work runs; cumulative and NEVER reset.  A crossing
    raises the fixed private overflow (the caller maps it)."""

    __slots__ = ("work_cap", "work_spent")

    def __init__(self, work_cap: int) -> None:
        self.work_cap = work_cap
        self.work_spent = 0

    def unit(self) -> bool:
        if self.work_spent + 1 > self.work_cap:
            raise _QOverflow()
        self.work_spent += 1
        return True

    def units(self, n: int) -> None:
        for _ in range(n):
            self.unit()


class _QPAdapter(_HOuter):
    """The P-phase charging adapter (the accepted ``_HAdapter``
    composition law): the ACTUAL P-domain outer (INDEPENDENT ceiling
    from the ACTUAL inherited root-lineage bounds) AND the ONE Q
    total on every unit.  A P-domain crossing refuses with the P
    fixed over-bound name (the accepted private P kernels map it);
    a Q-total crossing raises the fixed private Q overflow.
    Inheriting the ACTUAL ``_HOuter`` keeps it the real P-domain
    ledger for the accepted private P validation and selection
    kernel; the Q total is NOT pre-reserved by the P ceiling (the
    ACTUAL P units flow through)."""

    __slots__ = ("qtotal",)

    def __init__(self, qtotal: _QOuter, work_cap: int) -> None:
        super().__init__(work_cap)
        self.qtotal = qtotal

    def unit(self) -> bool:
        if not super().unit():
            return False
        self.qtotal.unit()
        return True


def _q_result(
    state: RootRegionLineageState,
    q_scope_key: str,
    q_bounds: RootRegionCurrentnessBounds,
    outcome: RootRegionCurrentnessOutcome,
    p_selection: RootRegionSelectionResult | None = None,
    p_validation_problem: RootLineageLimitation | None = None,
    usable_selected_source_digest: str | None = None,
    uncertainty_witnesses: tuple[RootRegionUncertaintyWitness, ...] = (),
    diagnostics: tuple[RootRegionCurrentnessDiagnostic, ...] = (),
) -> RootRegionCurrentnessResult:
    """The closed result construction (charged by the caller)."""
    return RootRegionCurrentnessResult(
        outcome=outcome,
        state=state,
        p_selection=p_selection,
        p_validation_problem=p_validation_problem,
        usable_selected_source_digest=usable_selected_source_digest,
        uncertainty_witnesses=uncertainty_witnesses,
        diagnostics=diagnostics,
        bounds=q_bounds,
        lineage_key=state.lineage_key,
        scope_key=q_scope_key,
        revision=state.revision,
    )


#: The closed top-level state fields the accepted P shape helper
#: and this derivation dereference BEFORE any P work (the narrow
#: O(1) field-EXISTENCE fence set; the value/type law stays with
#: the accepted P fences).
_Q_STATE_BOUNDARY_FIELDS = ("d_state", "revision", "lineage_key", "root_facts")
#: The closed wrapped-D fields dereferenced at the same boundary.
_Q_STATE_D_FIELDS = ("revision", "history_key")


def _q_state_boundary_ok(state: object) -> bool:
    """The narrow closed O(1) field-EXISTENCE fence over the exact
    top-level state fields dereferenced BEFORE the accepted P shape
    helpers run: a partial actual state instance (fields never set)
    is a malformed non-P record (the fixed private ValueError),
    never an internal attribute error.  No value law is added here;
    the accepted P shape fences remain authoritative afterward."""
    if not isinstance(state, RootRegionLineageState):
        return False
    if not all(hasattr(state, name) for name in _Q_STATE_BOUNDARY_FIELDS):
        return False
    d_state = state.d_state
    return isinstance(d_state, CausalHistoryState) and all(
        hasattr(d_state, name) for name in _Q_STATE_D_FIELDS
    )


def _q_ns_boundary_ok(ns: object) -> bool:
    """The narrow closed O(1) field-EXISTENCE fence over the actual
    namespace model's own closed field set, BEFORE the accepted P
    shape helpers may dereference fields: a partial actual namespace
    instance is a typed foreign-scope input (the default-domain
    refusal), never an internal attribute error.  No value law is
    added here; the accepted P shape and revalidation fences remain
    authoritative afterward."""
    if not isinstance(ns, RootRegionLineageNamespace):
        return False
    return all(hasattr(ns, name) for name in RootRegionLineageNamespace.model_fields)


def _q_uncertainty_assessment(
    state: RootRegionLineageState,
    outer: _QOuter,
) -> tuple[tuple[RootRegionUncertaintyWitness, ...], bool]:
    """The charged combined-frontier uncertainty assessment.

    Returns (ALL qualifying uncertainty witnesses in canonical
    deterministic metadata order, whether ANY qualifying witness is
    undominated).  EVERY candidate attempt counts BEFORE dedup;
    every actual visit/comparison/membership/ancestor-traversal/
    record construction charges the ONE Q outer BEFORE the work.
    Only frozen parent evidence adds edges; the original proofs are
    reached by reference (metadata only), never walked or re-hashed."""
    d_state: CausalHistoryState = state.d_state

    # Frozen parent evidence (child -> ordered parents).
    parent_map: dict[str, list[str]] = {}
    for link in d_state.parent_links:
        outer.unit()
        parent_map.setdefault(link.child, []).append(link.parent)

    # Trusted INTERNAL issuance binding index.
    issuances: set[tuple[str, str, str, str]] = set()
    for call in d_state.issuances:
        outer.unit()
        issuances.add((call.call_id, call.endpoint, call.tool_name, call.argument_fingerprint))

    # Complete original owning result index (the witness retains the
    # ACTUAL complete record by reference).
    complete_result_records: dict[tuple[str, str, str, str], ResultFingerprintRecord] = {}
    for record in d_state.results:
        outer.unit()
        if record.complete is True:
            complete_result_records[
                (record.call_id, record.endpoint, record.tool_name, record.argument_fingerprint)
            ] = record

    # Row 1: every P fact occurrence already represents its completed
    # root source (no second uncertainty record); the AUTHORITATIVE
    # read/region occurrences are the KNOWN governing witnesses whose
    # strict descendants dominate uncertainty.
    known_occurrences: set[str] = set()
    fact_ancestors: list[set[str]] = []
    for fact in state.root_facts:
        outer.unit()
        kind, occurrence_id = _region_provenance_key(fact.provenance)
        if kind == "envelope":
            continue  # the anchor is a frontier node, never an uncertainty
        known_occurrences.add(occurrence_id)
        if fact.authority:
            outer.unit()
            fact_ancestors.append(_ancestors_of(occurrence_id, parent_map, outer))

    witnesses: list[RootRegionUncertaintyWitness] = []
    has_undominated = False
    for occ in d_state.occurrences:
        outer.unit()
        if occ.occurrence_id in known_occurrences:
            continue  # row 1: the P fact already represents this occurrence
        if occ.anchored is not True:
            continue  # unanchored: no temporal edge, no uncertainty
        call_key = (occ.call_id, occ.endpoint, occ.tool_name, occ.argument_fingerprint)
        if call_key not in issuances:
            continue  # unissued: no uncertainty (a later genuine issuance may qualify)
        result_record = complete_result_records.get(call_key)
        if result_record is None:
            continue  # no complete original owning result
        proof = occ.proof
        if proof.root_path != ROOT_FILENAME:
            continue  # wrong effective root: no root uncertainty
        n_root = 0
        root_position = -1
        for position, member in enumerate(proof.requested_members):
            outer.unit()
            if member.normalized == ROOT_FILENAME:
                n_root += 1
                root_position = position
        if n_root < 1:
            continue  # nonroot-only: no root uncertainty
        outer.unit()
        if CAUSAL_ROOT_FACT not in _ancestors_of(occ.occurrence_id, parent_map, outer):
            continue  # frozen ancestry does not reach the immutable bootstrap
        # Charged classification (row 2 opaque vs row 3 unsupported).
        uncertainty_class: RootRegionUncertaintyClass
        if n_root >= 2:
            uncertainty_class = RootRegionUncertaintyClass.UNSUPPORTED_ROOT_SHAPE
        else:
            root_member_known = False
            for segment in proof.segments:
                # Precharge the ACTUAL membership-walk width BEFORE
                # the charged scan.
                outer.units(1 + len(segment.member_positions))
                if root_position in segment.member_positions:
                    if segment.member_digest is not None:
                        root_member_known = True
                    break
            uncertainty_class = (
                RootRegionUncertaintyClass.UNSUPPORTED_ROOT_SHAPE
                if root_member_known
                else RootRegionUncertaintyClass.OPAQUE_ROOT_BEARING_GROUP
            )
        # Charged dominance: the witness is blocked iff a genuinely
        # later supported authoritative root witness STRICTLY
        # descends from it (the envelope anchor never dominates; a
        # single descendant-of-all suffices and compatible maxima
        # jointly covering branches suffice -- no edges invented).
        dominated = False
        for ancestors in fact_ancestors:
            outer.unit()
            if occ.occurrence_id in ancestors:
                dominated = True
                break
        if not dominated:
            has_undominated = True
        outer.units(_Q_WITNESS_UNITS)
        witnesses.append(
            RootRegionUncertaintyWitness(
                occurrence=occ,
                result_record=result_record,
                occurrence_id=occ.occurrence_id,
                call_id=occ.call_id,
                endpoint=occ.endpoint,
                uncertainty_class=uncertainty_class,
                whole_proof_digest=proof.source_digest,
                whole_proof_byte_length=proof.source_byte_length,
                root_operand_count=n_root,
            )
        )
    if len(witnesses) > 1:
        outer.units(len(witnesses) * (len(witnesses) - 1))
    return (
        tuple(sorted(witnesses, key=lambda w: (w.uncertainty_class.value, w.occurrence_id))),
        has_undominated,
    )


def derive_root_region_currentness(
    state: RootRegionLineageState,
    ns: RootRegionLineageNamespace,
    bounds: RootRegionCurrentnessBounds | None = None,
) -> RootRegionCurrentnessResult:
    """The bounded pure root-currentness derivation query (018-q).

    ONE Q outer covers the ENTIRE operation: the O(1) shape/scope/
    history/version/bounds fences, the ACTUAL P phase (namespace
    reservation/revalidation included) under the ACTUAL independent
    P domain coupled unit-for-unit into the Q total (no second
    full-P public call, no reset ledger, no pre-reserved ceiling),
    the charged evidence inventory, owner/issuance membership, parent
    maps/ancestry, dominance, canonical sorting/dedup and the final
    result/model construction (the mapped early P refusal/conflict/
    no-root results precharge their own bounded construction before
    they are built).
    The EXACT input P state is retained by reference on EVERY
    outcome; the query never advances a revision, never mints a root
    authority fact and never copies source.  A malformed non-P state
    fails with a fixed private ValueError before result construction;
    every other failure is a typed refusal carrying the ACTUAL
    same-run P selection (once computed) and, when P validation
    refused before selection, the ACTUAL P validation reason.  A
    rejected input scope or bounds characterizes the derivation with
    the default domain (the unusable input is never partially
    trusted)."""
    if not _q_state_boundary_ok(state) or not _region_state_shape(state):
        raise _fixed("the region lineage state must carry an actual bounded state record")

    def _refuse(
        q_bounds: RootRegionCurrentnessBounds,
        q_scope_key: str,
        diagnostics: tuple[RootRegionCurrentnessDiagnostic, ...],
        p_selection: RootRegionSelectionResult | None = None,
        p_validation_problem: RootLineageLimitation | None = None,
    ) -> RootRegionCurrentnessResult:
        return _q_result(
            state,
            q_scope_key,
            q_bounds,
            RootRegionCurrentnessOutcome.REFUSED,
            p_selection=p_selection,
            p_validation_problem=p_validation_problem,
            diagnostics=diagnostics,
        )

    default_bounds = RootRegionCurrentnessBounds()
    if not _q_ns_boundary_ok(ns) or not _region_preflight_ns_shape(ns):
        return _refuse(
            default_bounds,
            root_region_currentness_scope_key(
                state.lineage_key,
                ROOT_REGION_CURRENTNESS_CONTRACT_VERSION,
                ROOT_REGION_CURRENTNESS_POLICY_VERSION,
                default_bounds,
            ),
            (RootRegionCurrentnessDiagnostic.FOREIGN_SCOPE,),
        )

    q_bounds = default_bounds
    if bounds is not None:
        if not root_region_currentness_bounds_shape_ok(bounds):
            return _refuse(
                default_bounds,
                root_region_currentness_scope_key(
                    state.lineage_key,
                    ROOT_REGION_CURRENTNESS_CONTRACT_VERSION,
                    ROOT_REGION_CURRENTNESS_POLICY_VERSION,
                    default_bounds,
                ),
                (RootRegionCurrentnessDiagnostic.MALFORMED_BINDING,),
            )
        try:
            q_bounds = RootRegionCurrentnessBounds.model_validate(
                bounds.model_dump(mode="python", warnings=False)
            )
        except Exception:
            return _refuse(
                default_bounds,
                root_region_currentness_scope_key(
                    state.lineage_key,
                    ROOT_REGION_CURRENTNESS_CONTRACT_VERSION,
                    ROOT_REGION_CURRENTNESS_POLICY_VERSION,
                    default_bounds,
                ),
                (RootRegionCurrentnessDiagnostic.MALFORMED_BINDING,),
            )
    q_scope_key = root_region_currentness_scope_key(
        state.lineage_key,
        ROOT_REGION_CURRENTNESS_CONTRACT_VERSION,
        ROOT_REGION_CURRENTNESS_POLICY_VERSION,
        q_bounds,
    )
    q_outer = _QOuter(q_bounds.max_total_work_units)
    p_selection: RootRegionSelectionResult | None = None
    try:
        q_outer.units(_Q_BASE_UNITS)
        if state.lineage_key != ns.lineage_key:
            return _refuse(q_bounds, q_scope_key, (RootRegionCurrentnessDiagnostic.FOREIGN_SCOPE,))
        if state.d_state.history_key != ns.history_key:
            return _refuse(q_bounds, q_scope_key, (RootRegionCurrentnessDiagnostic.FOREIGN_SCOPE,))
        for actual, supported in _region_version_pairs(ns):
            if actual != supported:
                return _refuse(
                    q_bounds, q_scope_key, (RootRegionCurrentnessDiagnostic.VERSION_UNSUPPORTED,)
                )
        p_adapter = _QPAdapter(q_outer, ns.root_lineage_bounds.max_total_work_units)
        # The ACTUAL P phase: the namespace reservation/revalidation
        # phase included, under the ACTUAL independent P domain,
        # coupled unit-for-unit into the ONE Q total (the accepted
        # ``_HAdapter`` composition law -- no second full-P public
        # call, no reset ledger, no pre-reserved ceiling).
        if not p_adapter.units(_region_ns_reservation(ns)):
            return _refuse(
                q_bounds,
                q_scope_key,
                (RootRegionCurrentnessDiagnostic.WORK_UNITS_OVER_BOUND,),
            )
        if not _region_revalidate_ns(ns):
            return _refuse(q_bounds, q_scope_key, (RootRegionCurrentnessDiagnostic.FOREIGN_SCOPE,))
        problem = validate_root_region_lineage_state(
            state,
            ns.root_lineage_bounds,
            p_adapter,
            history_bounds=ns.history_bounds,
            graph_bounds=ns.graph_bounds,
            proof_bounds=ns.proof_bounds,
            observation_bounds=ns.observation_bounds,
            workspace=ns.workspace,
        )
        if problem is not None:
            q_outer.units(_RESULT_BUILD_UNITS)
            return _refuse(q_bounds, q_scope_key, (), p_validation_problem=problem)
        p_sel = _region_selection_kernel(state, state.d_state, p_adapter)
        p_selection = p_sel
        # Ordered precedence: the actual P refusal/conflict/no-root
        # maps BEFORE any uncertainty assessment; each mapped early
        # result precharges its OWN bounded result construction (the
        # carried actual P selection's witness facts included) before
        # it is built.  On those mapped early results the uncertainty
        # inventory is not computed (the actual P result is retained,
        # no selection invented).
        if p_sel.outcome is RootSelectionOutcome.REFUSED:
            q_outer.units(_RESULT_BUILD_UNITS + _Q_RESULT_WITNESS_UNITS * len(p_sel.witness_facts))
            return _refuse(q_bounds, q_scope_key, (), p_selection=p_sel)
        if p_sel.outcome is RootSelectionOutcome.ROOT_CONTENT_CONFLICT:
            q_outer.units(_RESULT_BUILD_UNITS + _Q_RESULT_WITNESS_UNITS * len(p_sel.witness_facts))
            return _q_result(
                state,
                q_scope_key,
                q_bounds,
                RootRegionCurrentnessOutcome.ROOT_AUTHORITY_CONFLICT,
                p_selection=p_sel,
            )
        if p_sel.outcome is RootSelectionOutcome.NO_SELECTED_ROOT:
            q_outer.units(_RESULT_BUILD_UNITS + _Q_RESULT_WITNESS_UNITS * len(p_sel.witness_facts))
            return _q_result(
                state,
                q_scope_key,
                q_bounds,
                RootRegionCurrentnessOutcome.ROOT_CURRENTNESS_UNPROVEN,
                p_selection=p_sel,
            )

        witnesses, has_undominated = _q_uncertainty_assessment(state, q_outer)
        q_outer.units(
            _RESULT_BUILD_UNITS
            + _Q_RESULT_WITNESS_UNITS * len(p_sel.witness_facts)
            + _Q_RESULT_WITNESS_UNITS * len(witnesses)
            + len(witnesses) * (len(witnesses) - 1)
        )
        if has_undominated:
            return _q_result(
                state,
                q_scope_key,
                q_bounds,
                RootRegionCurrentnessOutcome.ROOT_CURRENTNESS_UNPROVEN,
                p_selection=p_sel,
                uncertainty_witnesses=witnesses,
            )
        return _q_result(
            state,
            q_scope_key,
            q_bounds,
            RootRegionCurrentnessOutcome.READY,
            p_selection=p_sel,
            usable_selected_source_digest=p_sel.selected_source_digest,
            uncertainty_witnesses=witnesses,
        )
    except _QOverflow:
        return _refuse(
            q_bounds,
            q_scope_key,
            (RootRegionCurrentnessDiagnostic.WORK_UNITS_OVER_BOUND,),
            p_selection=p_selection,
        )

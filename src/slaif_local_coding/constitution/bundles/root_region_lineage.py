"""Versioned root-region authority producer state machine (018-p; INERT).

The PURE root-region producer/validator/authority/selection surface
required by the accepted rules 3/8 for ordinary mixed-only
changed-root acquisition.  It closes the PRODUCER half of whole018:
a genuinely issued, complete, uniquely attributable NEW root
REGION in an ordinary mixed read earns source evidence and (via the
actual trusted issuance + anchored occurrence + frozen bootstrap
ancestry) authority under the NEW explicit version, with no
independent singleton required.

The NEW contract/policy versions are ``cache-root-region-lineage/v1``
/ ``root-region-lineage-policy/v1``; the accepted 018-h
``cache-root-lineage/v1`` / ``root-lineage-policy/v1`` and the 018-o
``root-lineage-mixed-observation/v1`` operations keep their EXACT
accepted behavior, schemas, recipe bytes and cap domains.  The new
state wraps the ACTUAL 018-d state by immutable reference and its
revision stays in exact 1:1 with it.

ONE new-operation outer at the ACTUAL unchanged
``RootLineageBounds.max_total_work_units`` covers the ENTIRE
operation and couples the ACTUAL D work (the inherited D/B local
domains stay independent with unchanged limits).  Private kernel
sharing reuses the accepted root-lineage primitives (the S3
singleton filter, the anchor/proof integrity laws, the S1 flag
re-derivation law, the causal-maximal selection law, the D
core) with correct type/version dispatch; no old public fence is
weakened and no second full-H budget layer is invented.

The producer policy: bootstrap is the actual legitimate effective
Responses AGENTS envelope (including exact empty source).  New
observation runs namespace/version/CAS/state-integrity gates FIRST,
then the actual original-request D observation under the private
region-acquisition policy: a foreign root MEMBER is provisionally
source-compatible ONLY when the actual complete proof has exactly
ONE normalized effective-root occurrence over ALL requested
operands and a single proven complete whole region for that
member; an UNKNOWN mixed root needs no independent singleton in
this NEW contract (it is retained unproven and may later earn
authority by genuine issuance/receipt/ancestry).  Repeated roots,
opaque root groups, partial/truncated/nonzero/unpaired/unsupported
reads gain NO exception.  Authority requires actual trusted
INTERNAL issuance, the complete original owning result, the
anchored original occurrence and frozen ancestry reaching the
immutable bootstrap; body flags, caller digests, envelope text, ID
novelty, equality, arrival and revisions never establish
authority/currentness.  A changed envelope in the same batch may
match an independently earned authoritative root REGION but cannot
authorize itself.  A genuinely NEW authoritative region occurrence
containing old bytes AFTER a newer one is a deliberate revert
under the same frozen partial-order law as a singleton.  O's
source-only mixed-fact suppression is NOT carried into this NEW
authority contract.

It is inert: no adapter runtime/compiler/recovery wiring, no RAM
service, no disk, no HTTP/SSE observer.  Object construction is
NOT authentication: an internal trusted boundary, never a public
body/header authority path.
"""

from __future__ import annotations

from collections.abc import Callable

from .bundle_admission_models import ADMISSION_CONTRACT_VERSION
from .bundle_proof import _HOuterOverflow
from .bundle_proof_models import (
    BUNDLE_PROOF_CONTRACT_VERSION,
    ROOT_FILENAME,
    BundleProofBounds,
    BundleSegment,
)
from .causal_history import (
    _ancestors_of,
    _observe_causal_history_core,
    _register_issuance_core,
    _register_receipt_core,
    _RootLineageContext,
    _UnitLedger,
    _WorkOverflowError,
)
from .causal_history_models import (
    CAUSAL_ARGUMENTS_JSON_VERSION,
    CAUSAL_HISTORY_CONTRACT_VERSION,
    CAUSAL_ROOT_FACT,
    CausalHistoryNamespace,
    CausalHistoryOutcome,
    CausalHistoryState,
    CausalHistoryTransition,
    CompletedReadOccurrence,
    HistoryBounds,
    validate_causal_history_state,
)
from .graph_models import GRAPH_CONTRACT_VERSION, REFERENCE_GRAMMAR, GraphBounds, _fixed
from .graph_observation import GraphRequest
from .observation_models import OBSERVER_VERSION, ObservationBounds
from .root_lineage import (
    _FACT_BUILD_UNITS,
    _H_LIMITATION_MAP,
    _H_OUTCOME_MAP,
    _RESULT_BUILD_UNITS,
    _RESULT_FACT_UNITS,
    _STATE_BUILD_UNITS,
    _STATE_FACT_UNITS,
    _TRANSITION_BUILD_UNITS,
    _CoupledUnit,
    _h_anchor_integrity,
    _h_proof_integrity,
    _hex64_ok,
    _HOuter,
    _is_singleton_root_read,
)
from .root_lineage_models import (
    EnvelopeRootProvenance,
    ReadRootProvenance,
    RootLineageBounds,
    RootLineageLimitation,
    RootLineageOutcome,
    RootSelectionOutcome,
    admission_bounds_shape_ok,
    graph_bounds_shape_ok,
    history_bounds_shape_ok,
    observation_bounds_shape_ok,
    proof_bounds_shape_ok,
    root_lineage_bounds_shape_ok,
)
from .root_region_lineage_models import (
    ROOT_REGION_LINEAGE_CONTRACT_VERSION,
    ROOT_REGION_LINEAGE_POLICY_VERSION,
    RootRegionLineageFact,
    RootRegionLineageNamespace,
    RootRegionLineageState,
    RootRegionLineageTransition,
    RootRegionReadProvenance,
    RootRegionSelectionResult,
    _region_provenance_key,
    root_region_ns_scalar_shape_ok,
)

# --- Region shape / gate helpers (the accepted H law, region dispatch) ----


def _region_preflight_ns_shape(ns: object) -> bool:
    """The O(1) shape fence BEFORE any unvalidated fuel (K5)."""
    if not isinstance(ns, RootRegionLineageNamespace):
        return False
    if not root_region_ns_scalar_shape_ok(ns):
        return False
    if not root_lineage_bounds_shape_ok(ns.root_lineage_bounds):
        return False
    if not history_bounds_shape_ok(ns.history_bounds):
        return False
    if not graph_bounds_shape_ok(ns.graph_bounds):
        return False
    if not proof_bounds_shape_ok(ns.proof_bounds):
        return False
    if not observation_bounds_shape_ok(ns.observation_bounds):
        return False
    if not admission_bounds_shape_ok(ns.bounds):
        return False
    return True


def _region_state_shape(state: object) -> bool:
    """The fixed O(1) region-state shape fence BEFORE any field
    dereference in a public entry (K5)."""
    return (
        isinstance(state, RootRegionLineageState)
        and isinstance(state.d_state, CausalHistoryState)
        and isinstance(state.revision, int)
        and not isinstance(state.revision, bool)
        and _hex64_ok(state.lineage_key)
        and isinstance(state.root_facts, tuple)
        and isinstance(state.d_state.revision, int)
        and not isinstance(state.d_state.revision, bool)
        and _hex64_ok(state.d_state.history_key)
    )


def _region_version_pairs(ns: RootRegionLineageNamespace) -> tuple[tuple[str, str], ...]:
    """The SEVEN actual D version identities plus the TWO NEW
    region version identities, paired with the supported constants."""
    return (
        (ns.history_version, CAUSAL_HISTORY_CONTRACT_VERSION),
        (ns.arguments_version, CAUSAL_ARGUMENTS_JSON_VERSION),
        (ns.admission_version, ADMISSION_CONTRACT_VERSION),
        (ns.observation_version, OBSERVER_VERSION),
        (ns.graph_version, GRAPH_CONTRACT_VERSION),
        (ns.reference_version, REFERENCE_GRAMMAR),
        (ns.proof_version, BUNDLE_PROOF_CONTRACT_VERSION),
        (ns.contract_version, ROOT_REGION_LINEAGE_CONTRACT_VERSION),
        (ns.policy_version, ROOT_REGION_LINEAGE_POLICY_VERSION),
    )


def _region_d_namespace(ns: RootRegionLineageNamespace) -> CausalHistoryNamespace:
    """The ACTUAL accepted D scope derived from the region scope's
    ACTUAL D fields (re-validated by construction)."""
    return CausalHistoryNamespace(
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
        admission_namespace_key=ns.admission_namespace_key,
        admission_scoped_key=ns.admission_scoped_key,
        lineage_id=ns.lineage_id,
        history_version=ns.history_version,
        arguments_version=ns.arguments_version,
        history_bounds=ns.history_bounds,
        history_key=ns.history_key,
        state_scoped_key=ns.state_scoped_key,
    )


def _region_ns_reservation(ns: RootRegionLineageNamespace) -> int:
    """Honest conservative pre-reservation for the revalidated
    region namespace chain (two full revalidation passes over the
    closed field set with the nested bound sets, the full actual D
    admission re-validation, the sha256 key recomputations and the
    bounded workspace/config walks)."""
    return 2 * (512 + len(ns.workspace) + len(ns.config_fingerprint))


def _region_revalidate_ns(ns: RootRegionLineageNamespace) -> bool:
    """Re-run the ACTUAL accepted validators over the ACTUAL
    fields; a forged nested model copy carries no acquired
    authority."""
    try:
        RootRegionLineageNamespace.model_validate(ns.model_dump(mode="python", warnings=False))
    except Exception:
        return False
    return True


def _region_closed(
    state: RootRegionLineageState,
    outcome: RootLineageOutcome,
    limitations: tuple[RootLineageLimitation, ...],
    d_transition: CausalHistoryTransition | None = None,
) -> RootRegionLineageTransition:
    """A non-accepted region transition over the EXACT prior
    region state (every refusal and every replay)."""
    if d_transition is not None:
        d_before = d_transition.revision_before
        d_after = d_transition.revision_after
    else:
        d_before = d_after = state.d_state.revision
    return RootRegionLineageTransition(
        state=state,
        outcome=outcome,
        diagnostics=limitations,
        d_transition=d_transition,
        revision_before=state.revision,
        revision_after=state.revision,
        d_revision_before=d_before,
        d_revision_after=d_after,
    )


def _region_map_d_refusal(
    d_trans: CausalHistoryTransition,
    ctx: _RootLineageContext,
    state: RootRegionLineageState,
    outer: _HOuter,
) -> RootRegionLineageTransition:
    """Map one actual D refusal onto the closed region vocabulary
    (mirrored 1:1 under the exact fixed names)."""
    if ctx.outer_exhausted:
        return _region_closed(
            state,
            RootLineageOutcome.REFUSED_OVER_BOUND,
            (RootLineageLimitation.WORK_UNITS_OVER_BOUND,),
            d_trans,
        )
    if not outer.units(2 * len(d_trans.diagnostics)):
        return _region_closed(
            state,
            RootLineageOutcome.REFUSED_OVER_BOUND,
            (RootLineageLimitation.WORK_UNITS_OVER_BOUND,),
            d_trans,
        )
    outcome = _H_OUTCOME_MAP[d_trans.outcome]
    limitations = tuple(_H_LIMITATION_MAP[lim] for lim in d_trans.diagnostics)
    return _region_closed(state, outcome, limitations, d_trans)


def _region_gate(
    state: RootRegionLineageState,
    ns: RootRegionLineageNamespace,
    expected_revision: int,
    outer: _HOuter,
) -> tuple[CausalHistoryNamespace | None, RootRegionLineageTransition | None]:
    """The shared early region gates: the fixed O(1) scope/CAS/
    D-state-binding/version fences FIRST, then the charged full
    namespace revalidation and the derived ACTUAL D namespace."""
    if not outer.units(11):
        return None, _region_closed(
            state,
            RootLineageOutcome.REFUSED_OVER_BOUND,
            (RootLineageLimitation.WORK_UNITS_OVER_BOUND,),
        )
    if state.lineage_key != ns.lineage_key:
        return None, _region_closed(state, RootLineageOutcome.REFUSED_FOREIGN_SCOPE, ())
    if state.revision != expected_revision:
        return None, _region_closed(state, RootLineageOutcome.REFUSED_CAS_MISMATCH, ())
    if state.d_state.history_key != ns.history_key:
        return None, _region_closed(state, RootLineageOutcome.REFUSED_FOREIGN_SCOPE, ())
    for actual, supported in _region_version_pairs(ns):
        if actual != supported:
            return None, _region_closed(
                state,
                RootLineageOutcome.REFUSED_VERSION_CONFLICT,
                (RootLineageLimitation.VERSION_UNSUPPORTED,),
            )
    if not outer.units(_region_ns_reservation(ns)):
        return None, _region_closed(
            state,
            RootLineageOutcome.REFUSED_OVER_BOUND,
            (RootLineageLimitation.WORK_UNITS_OVER_BOUND,),
        )
    if not _region_revalidate_ns(ns):
        return None, _region_closed(state, RootLineageOutcome.REFUSED_FOREIGN_SCOPE, ())
    if not outer.units(_region_ns_reservation(ns)):
        return None, _region_closed(
            state,
            RootLineageOutcome.REFUSED_OVER_BOUND,
            (RootLineageLimitation.WORK_UNITS_OVER_BOUND,),
        )
    return _region_d_namespace(ns), None


# --- Region fact construction / S1 / retention ----------------------------


def _region_root_segment(
    occ: CompletedReadOccurrence, charge: Callable[[], bool]
) -> tuple[BundleSegment | None, int, bool]:
    """The NEW explicit mixed single-root REGION filter (charged
    BEFORE each actual comparison, duplicates and skips included).

    A completed occurrence carries a retained root-region candidate
    ONLY for a MULTI-MEMBER complete proof with exactly ONE
    normalized effective-root occurrence over ALL requested operands
    and a single proven complete whole region for it: one
    attributable single-member segment (non-None member digest, a
    unique member position) owned by the root member.  Repeated
    root operands, two proven root segments and every other shape
    are never candidates.  Returns ``(segment, index, True)`` for
    the eligible segment with its ACTUAL position in the proof's
    ordered segment tuple (or ``(None, 0, True)`` when none), or
    ``(None, 0, False)`` when a charge was refused (the caller maps
    it to WORK_UNITS_OVER_BOUND)."""
    proof = occ.proof
    if not charge():
        return None, 0, False
    if len(proof.requested_members) < 2:
        return None, 0, True  # region provenance is mixed-proof only
    root_occurrences = 0
    for member in proof.requested_members:
        if not charge():
            return None, 0, False
        if member.normalized == ROOT_FILENAME:
            root_occurrences += 1
            if root_occurrences > 1:
                return None, 0, True  # repeated root operand: no region
    if root_occurrences != 1:
        return None, 0, True
    found: BundleSegment | None = None
    found_index = 0
    for index, segment in enumerate(proof.segments):
        if not charge():
            return None, 0, False
        if segment.member_digest is None:
            continue  # no single-occurrence proof: never inferred
        member = proof.requested_members[segment.member_positions[0]]
        if not charge():
            return None, 0, False
        if member.normalized == ROOT_FILENAME:
            if found is not None:
                return None, 0, True  # two proven root segments: no region
            found = segment
            found_index = index
    return found, found_index, True


def _region_new_root_facts(
    new_occurrences: tuple[CompletedReadOccurrence, ...],
    old_count: int,
    old_bytes: int,
    bounds: RootLineageBounds,
    outer: _HOuter,
) -> tuple[RootRegionLineageFact, ...] | RootLineageLimitation | None:
    """The NEW retention filter: EVERY eligible source candidate
    is retained as a root fact -- the complete whole singleton root
    read keeps its OLD whole-read provenance (the accepted S3 law,
    unchanged) and the proven mixed single root uses the NEW
    read_region provenance.  Facts and ACTUAL ROOT MEMBER bytes are
    counted and preflighted BEFORE materialization under the
    unchanged H ceilings (K4: the crossing candidate is refused
    before the crossing fact materializes); the mixed aggregate
    bytes stay D/B-owned and are never the logical root-body size.
    Flags start unproven: the S1 re-derivation over the NEW state
    decides them.  Returns the new fact tuple, the FIRST actual cap
    refusal, or None on exhaustion."""
    out: list[RootRegionLineageFact] = []
    out_bytes = 0
    for occ in new_occurrences:
        singleton = _is_singleton_root_read(occ, outer.unit)
        if singleton is None:
            return None
        segment: BundleSegment | None
        member_digest: str | None
        if singleton:
            proof = occ.proof
            segment = proof.segments[0]
            if segment.member_digest is None:
                raise _fixed("unreachable: the S3 filter retains only the proven member digest")
            member_digest = segment.member_digest
            member_bytes = segment.byte_length
            segment_index = 0
            member_position = 0
            is_region = False
        else:
            segment, segment_index, ok = _region_root_segment(occ, outer.unit)
            if not ok:
                return None
            if segment is None:
                continue
            member_digest = segment.member_digest
            member_bytes = segment.byte_length
            if member_digest is None:
                raise _fixed("unreachable: the region filter retains only the proven member")
            member_position = segment.member_positions[0]
            is_region = True
        # The logical retention cap preflight BEFORE the crossing
        # provenance/fact materializes (K4): the candidate is
        # counted and its ACTUAL root-member bytes are compared
        # against the unchanged H ceilings, and the fact build is
        # reserved, before any new record is constructed.
        if old_count + len(out) + 1 > bounds.max_root_facts:
            return RootLineageLimitation.ROOT_FACTS_OVER_BOUND
        if old_bytes + out_bytes + member_bytes > bounds.max_retained_root_source_bytes:
            return RootLineageLimitation.ROOT_SOURCE_BYTES_OVER_BOUND
        if not outer.units(_FACT_BUILD_UNITS):
            return None
        if is_region:
            provenance: ReadRootProvenance | RootRegionReadProvenance = RootRegionReadProvenance(
                occurrence_id=occ.occurrence_id,
                call_id=occ.call_id,
                endpoint=occ.endpoint,
                whole_proof_digest=occ.proof.source_digest,
                whole_proof_byte_length=occ.proof.source_byte_length,
                root_segment_index=segment_index,
                root_member_position=member_position,
                root_member_digest=member_digest,
                root_member_byte_length=member_bytes,
            )
        else:
            provenance = ReadRootProvenance(
                occurrence_id=occ.occurrence_id,
                call_id=occ.call_id,
                endpoint=occ.endpoint,
                read_digest=occ.proof.source_digest,
                read_byte_length=occ.proof.source_byte_length,
            )
        out.append(
            RootRegionLineageFact(
                source_digest=member_digest,
                source_byte_length=member_bytes,
                provenance=provenance,
                issued=False,
                authority=False,
            )
        )
        out_bytes += member_bytes
    return tuple(out)


def _region_derive_flags(
    d_state: CausalHistoryState,
    facts: tuple[RootRegionLineageFact, ...],
    outer: _HOuter,
) -> tuple[RootRegionLineageFact, ...] | None:
    """The S1 authority re-derivation (the accepted law, unchanged):
    after EVERY accepted D transition, ALL retained facts'
    issued/authority flags are recomputed from the ACTUAL new D
    state.  Both supported read provenance variants (the old whole
    read and the NEW region read) have the same trusted
    causal-authority requirements: issued = the matching INTERNAL
    issuance is retained; authority = issued AND the occurrence is
    anchored AND the frozen parent evidence reaches the ORIGINAL
    bootstrap root fact.  The envelope fact is the anchor itself
    (never issued, always authoritative).  Returns None on
    exhaustion."""
    issued_ids: set[str] = set()
    for issuance in d_state.issuances:
        if not outer.unit():
            return None
        issued_ids.add(issuance.call_id)
    occ_by_id: dict[str, CompletedReadOccurrence] = {}
    for occ in d_state.occurrences:
        if not outer.unit():
            return None
        occ_by_id[occ.occurrence_id] = occ
    parent_map: dict[str, list[str]] = {}
    for link in d_state.parent_links:
        if not outer.unit():
            return None
        parent_map.setdefault(link.child, []).append(link.parent)
    out: list[RootRegionLineageFact] = []
    for fact in facts:
        if not outer.unit():
            return None
        if isinstance(fact.provenance, EnvelopeRootProvenance):
            out.append(fact)
            continue
        p = fact.provenance
        issued = p.call_id in issued_ids
        authority = False
        if issued:
            bound_occ = occ_by_id.get(p.occurrence_id)
            if bound_occ is not None and bound_occ.anchored:
                try:
                    ancestors = _ancestors_of(p.occurrence_id, parent_map, outer)
                except _WorkOverflowError:
                    return None
                if not outer.unit():
                    return None
                authority = CAUSAL_ROOT_FACT in ancestors
        if not outer.units(4):
            return None
        out.append(fact.model_copy(update={"issued": issued, "authority": authority}))
    return tuple(out)


def _region_retention_check(
    facts: tuple[RootRegionLineageFact, ...],
    bounds: RootLineageBounds,
    outer: _HOuter,
    state: RootRegionLineageState,
    d_trans: CausalHistoryTransition,
) -> RootRegionLineageTransition | None:
    """The retention caps, counted BEFORE retention (the actual
    fact count and the logical exact UTF-8 root source bytes over
    ALL retained facts, bootstrap once)."""
    if len(facts) > bounds.max_root_facts:
        return _region_closed(
            state,
            RootLineageOutcome.REFUSED_OVER_BOUND,
            (RootLineageLimitation.ROOT_FACTS_OVER_BOUND,),
            d_trans,
        )
    total = 0
    for fact in facts:
        if not outer.unit():
            return _region_closed(
                state,
                RootLineageOutcome.REFUSED_OVER_BOUND,
                (RootLineageLimitation.WORK_UNITS_OVER_BOUND,),
                d_trans,
            )
        total += fact.source_byte_length
        if total > bounds.max_retained_root_source_bytes:
            return _region_closed(
                state,
                RootLineageOutcome.REFUSED_OVER_BOUND,
                (RootLineageLimitation.ROOT_SOURCE_BYTES_OVER_BOUND,),
                d_trans,
            )
    return None


def _region_combine_facts(
    old: tuple[RootRegionLineageFact, ...],
    new: tuple[RootRegionLineageFact, ...],
    outer: _HOuter,
) -> tuple[RootRegionLineageFact, ...] | None:
    """Sorted-deduplicated union by region provenance identity
    (the charged pair-counting reservation precedes the canonical
    sort)."""
    if not outer.units(len(old)):
        return None
    combined = list(old)
    old_keys: set[tuple[str, str]] = set()
    for fact in old:
        if not outer.unit():
            return None
        old_keys.add(_region_provenance_key(fact.provenance))
    for fact in new:
        if not outer.unit():
            return None
        key = _region_provenance_key(fact.provenance)
        if key not in old_keys:
            if not outer.unit():
                return None
            combined.append(fact)
            old_keys.add(key)
    if len(combined) > 1:
        if not outer.units(len(combined) * (len(combined) - 1)):
            return None
    return tuple(sorted(combined, key=lambda f: _region_provenance_key(f.provenance)))


def _deferred_region_digests(sink: list[frozenset[str]], outer: _HOuter) -> tuple[str, ...] | None:
    """The sorted union of the batch's deferred same-scope envelope
    digests (charged per digest; None on exhaustion)."""
    if not sink:
        return ()
    union: set[str] = set()
    for digest_set in sink:
        for digest in digest_set:
            if not outer.unit():
                return None
            union.add(digest)
    if len(union) > 1:
        if not outer.units(len(union) * (len(union) - 1)):
            return None
    return tuple(sorted(union))


# --- Bounded charged region state validation ------------------------------


def validate_root_region_lineage_state(
    state: RootRegionLineageState,
    bounds: RootLineageBounds | None = None,
    work: _UnitLedger | None = None,
    history_bounds: HistoryBounds | None = None,
    graph_bounds: GraphBounds | None = None,
    proof_bounds: BundleProofBounds | None = None,
    observation_bounds: ObservationBounds | None = None,
    workspace: str | None = None,
) -> RootLineageLimitation | None:
    """Bounded, charged cross-record integrity for one region
    state (the accepted H validation law, NEW kind handling
    explicit at every step; no envelope fallthrough).

    1. the NEW region record shape law (revision integral
       0..MAX_REVISION in EXACT 1:1 with the wrapped D revision,
       64-hex keys, the root-facts tuple shape, the sorted/
       deduplicated region provenance identity and every fact's
       intrinsic fields, including the full read_region field
       fences);
    2. the effective retention bounds (fact count and logical root
       source bytes over ALL retained facts, bootstrap once);
    3. the ACTUAL root-anchor source integrity (the accepted F
       anchor law);
    4. the ACTUAL D cross-record integrity through the real
       accepted D validator; 4b. the private retained
       result/proof binding coherence; 4c. the completed-
       occurrence/result ownership join;
    5. the ACTUAL earned proof-record integrity for EVERY retained
       occurrence exactly ONCE, the retained occurrence root
       bindings, and the COMPLETE 1:1 fact inventory: every
       eligible singleton root-read occurrence retains its read
       fact AND every eligible mixed single-root occurrence
       retains its read_region fact (an omitted earned fact is an
       incoherent binding, never a silent rollback; a detached
       coherently rekeyed region is refused);
    6. the per-fact provenance binding (read_region joins the
       ACTUAL retained occurrence, proof aggregate, segment index,
       unique member position and member digest/length) and the
       DERIVED flags re-derived from the ACTUAL D state -- the
       stored flags are NEVER trusted.

    Length preflights run BEFORE any map/iteration/copy; every
    actual visit/comparison/membership attempt charges BEFORE the
    operation.  Returns ``None`` when coherent, else the ONE fixed
    closed limitation (first refusal wins)."""
    from .causal_history_models import MAX_REVISION, ResultFingerprintRecord

    if bounds is not None:
        if not root_lineage_bounds_shape_ok(bounds):
            return RootLineageLimitation.MALFORMED_BINDING
        try:
            bounds = RootLineageBounds.model_validate(
                bounds.model_dump(mode="python", warnings=False)
            )
        except Exception:
            return RootLineageLimitation.MALFORMED_BINDING
    effective = RootLineageBounds() if bounds is None else bounds
    if history_bounds is not None:
        if not history_bounds_shape_ok(history_bounds):
            return RootLineageLimitation.MALFORMED_BINDING
        try:
            history_bounds = HistoryBounds.model_validate(
                history_bounds.model_dump(mode="python", warnings=False)
            )
        except Exception:
            return RootLineageLimitation.MALFORMED_BINDING
    d_bounds = HistoryBounds() if history_bounds is None else history_bounds
    if graph_bounds is not None:
        if not graph_bounds_shape_ok(graph_bounds):
            return RootLineageLimitation.MALFORMED_BINDING
        try:
            graph_bounds = GraphBounds.model_validate(
                graph_bounds.model_dump(mode="python", warnings=False)
            )
        except Exception:
            return RootLineageLimitation.MALFORMED_BINDING
    g_bounds = GraphBounds() if graph_bounds is None else graph_bounds
    if proof_bounds is not None:
        if not proof_bounds_shape_ok(proof_bounds):
            return RootLineageLimitation.MALFORMED_BINDING
        try:
            proof_bounds = BundleProofBounds.model_validate(
                proof_bounds.model_dump(mode="python", warnings=False)
            )
        except Exception:
            return RootLineageLimitation.MALFORMED_BINDING
    p_bounds = BundleProofBounds() if proof_bounds is None else proof_bounds
    if observation_bounds is not None:
        if not observation_bounds_shape_ok(observation_bounds):
            return RootLineageLimitation.MALFORMED_BINDING
        try:
            observation_bounds = ObservationBounds.model_validate(
                observation_bounds.model_dump(mode="python", warnings=False)
            )
        except Exception:
            return RootLineageLimitation.MALFORMED_BINDING
    o_bounds = ObservationBounds() if observation_bounds is None else observation_bounds
    ledger = _CoupledUnit(work, effective.max_total_work_units)

    # --- 1. The NEW region record shape law (model_copy is not authority)
    if not ledger.unit():
        return RootLineageLimitation.WORK_UNITS_OVER_BOUND
    if not isinstance(state, RootRegionLineageState):
        return RootLineageLimitation.MALFORMED_BINDING
    revision = state.revision
    if (
        not isinstance(revision, int)
        or isinstance(revision, bool)
        or not 0 <= revision <= MAX_REVISION
    ):
        return RootLineageLimitation.MALFORMED_BINDING
    if not _hex64_ok(state.lineage_key):
        return RootLineageLimitation.MALFORMED_BINDING
    if not ledger.unit():
        return RootLineageLimitation.WORK_UNITS_OVER_BOUND
    d_state = state.d_state
    if not isinstance(d_state, CausalHistoryState):
        return RootLineageLimitation.MALFORMED_BINDING
    d_revision = d_state.revision
    if (
        not isinstance(d_revision, int)
        or isinstance(d_revision, bool)
        or not 0 <= d_revision <= MAX_REVISION
    ):
        return RootLineageLimitation.MALFORMED_BINDING
    if not ledger.unit():
        return RootLineageLimitation.WORK_UNITS_OVER_BOUND
    if revision != d_revision:
        return RootLineageLimitation.MALFORMED_BINDING
    if not _hex64_ok(d_state.history_key):
        return RootLineageLimitation.MALFORMED_BINDING
    facts = state.root_facts
    if not isinstance(facts, tuple):
        return RootLineageLimitation.MALFORMED_BINDING
    if len(facts) > effective.max_root_facts:
        return RootLineageLimitation.ROOT_FACTS_OVER_BOUND
    keys_list: list[tuple[str, str]] = []
    for fact in facts:
        if not ledger.unit():
            return RootLineageLimitation.WORK_UNITS_OVER_BOUND
        if not isinstance(fact, RootRegionLineageFact):
            return RootLineageLimitation.MALFORMED_BINDING
        provenance = fact.provenance
        if not isinstance(
            provenance, (EnvelopeRootProvenance, ReadRootProvenance, RootRegionReadProvenance)
        ):
            return RootLineageLimitation.MALFORMED_BINDING
        # The concrete class is fenced against the kind tag BEFORE
        # any key/dispatch dereference: a forged instance
        # (model_construct) with a mismatched tag is malformed,
        # never a dereference of an absent field.
        if (
            (isinstance(provenance, EnvelopeRootProvenance) and provenance.kind != "envelope")
            or (isinstance(provenance, ReadRootProvenance) and provenance.kind != "read")
            or (
                isinstance(provenance, RootRegionReadProvenance)
                and provenance.kind != "read_region"
            )
        ):
            return RootLineageLimitation.MALFORMED_BINDING
        if not _hex64_ok(fact.source_digest):
            return RootLineageLimitation.MALFORMED_BINDING
        if (
            not isinstance(fact.source_byte_length, int)
            or isinstance(fact.source_byte_length, bool)
            or fact.source_byte_length < 0
        ):
            return RootLineageLimitation.MALFORMED_BINDING
        if not isinstance(fact.issued, bool) or not isinstance(fact.authority, bool):
            return RootLineageLimitation.MALFORMED_BINDING
        if isinstance(provenance, EnvelopeRootProvenance):
            if (
                not _hex64_ok(provenance.root_digest)
                or not isinstance(provenance.workspace, str)
                or not 1 <= len(provenance.workspace) <= 1024
                or not provenance.workspace.startswith("/")
                or (
                    not isinstance(provenance.source_byte_length, int)
                    or isinstance(provenance.source_byte_length, bool)
                    or provenance.source_byte_length < 0
                )
            ):
                return RootLineageLimitation.MALFORMED_BINDING
        elif isinstance(provenance, ReadRootProvenance):
            if (
                not _hex64_ok(provenance.occurrence_id)
                or not _hex64_ok(provenance.read_digest)
                or not isinstance(provenance.call_id, str)
                or not 1 <= len(provenance.call_id) <= 256
                or any(c.isspace() for c in provenance.call_id)
                or provenance.endpoint not in ("responses", "chat")
                or (
                    not isinstance(provenance.read_byte_length, int)
                    or isinstance(provenance.read_byte_length, bool)
                    or provenance.read_byte_length < 0
                )
            ):
                return RootLineageLimitation.MALFORMED_BINDING
        else:
            # The NEW read_region closed field fence (every actual
            # scalar; a container in a scalar slot is malformed).
            if (
                not _hex64_ok(provenance.occurrence_id)
                or not _hex64_ok(provenance.whole_proof_digest)
                or not _hex64_ok(provenance.root_member_digest)
                or not isinstance(provenance.call_id, str)
                or not 1 <= len(provenance.call_id) <= 256
                or any(c.isspace() for c in provenance.call_id)
                or provenance.endpoint not in ("responses", "chat")
                or (
                    not isinstance(provenance.whole_proof_byte_length, int)
                    or isinstance(provenance.whole_proof_byte_length, bool)
                    or provenance.whole_proof_byte_length < 0
                )
                or (
                    not isinstance(provenance.root_segment_index, int)
                    or isinstance(provenance.root_segment_index, bool)
                    or provenance.root_segment_index < 0
                )
                or (
                    not isinstance(provenance.root_member_position, int)
                    or isinstance(provenance.root_member_position, bool)
                    or provenance.root_member_position < 0
                )
                or (
                    not isinstance(provenance.root_member_byte_length, int)
                    or isinstance(provenance.root_member_byte_length, bool)
                    or provenance.root_member_byte_length < 0
                )
            ):
                return RootLineageLimitation.MALFORMED_BINDING
        if not ledger.unit():
            return RootLineageLimitation.WORK_UNITS_OVER_BOUND
        keys_list.append(_region_provenance_key(provenance))
    # Sorted/deduplicated region provenance identity over the STORED
    # order (one charged strict-increase comparison per adjacent pair).
    for index in range(len(keys_list) - 1):
        if not ledger.unit():
            return RootLineageLimitation.WORK_UNITS_OVER_BOUND
        if not keys_list[index] < keys_list[index + 1]:
            return RootLineageLimitation.MALFORMED_BINDING

    # --- 2. The retention byte walk + the anchor-presence law ---
    anchor = d_state.root
    envelope_seen = 0
    total = 0
    for fact in facts:
        if not ledger.unit():
            return RootLineageLimitation.WORK_UNITS_OVER_BOUND
        total += fact.source_byte_length
        if total > effective.max_retained_root_source_bytes:
            return RootLineageLimitation.ROOT_SOURCE_BYTES_OVER_BOUND
        if fact.provenance.kind == "envelope":
            envelope_seen += 1
            ep = fact.provenance
            if (
                anchor is None
                or not isinstance(ep, EnvelopeRootProvenance)
                or ep.root_digest != anchor.root_digest
                or ep.workspace != anchor.workspace
                or ep.source_byte_length != anchor.source_byte_length
                or fact.source_digest != anchor.root_digest
                or fact.source_byte_length != anchor.source_byte_length
            ):
                return RootLineageLimitation.MALFORMED_BINDING
    if envelope_seen != (1 if anchor is not None else 0):
        return RootLineageLimitation.MALFORMED_BINDING

    # --- 3. The ACTUAL root-anchor source integrity (F law) ---
    if anchor is not None:
        if not ledger.unit():
            return RootLineageLimitation.WORK_UNITS_OVER_BOUND
        coherent = _h_anchor_integrity(anchor, g_bounds, effective, workspace, ledger)
        if coherent is None:
            return RootLineageLimitation.WORK_UNITS_OVER_BOUND
        if not coherent:
            return RootLineageLimitation.MALFORMED_BINDING
    else:
        if not ledger.unit():
            return RootLineageLimitation.WORK_UNITS_OVER_BOUND
        if d_state.occurrences or d_state.issuances or d_state.results:
            return RootLineageLimitation.MALFORMED_BINDING

    # --- 4. The ACTUAL D cross-record integrity ---
    d_problem = validate_causal_history_state(d_state, d_bounds, work=ledger.unit)
    if d_problem is not None:
        return _H_LIMITATION_MAP[d_problem]

    # --- 4b. Private retained result/proof binding coherence ---
    for result in d_state.results:
        if not ledger.unit():
            return RootLineageLimitation.WORK_UNITS_OVER_BOUND
        for piece_binding in result.piece_call_bindings:
            if not ledger.unit():
                return RootLineageLimitation.WORK_UNITS_OVER_BOUND
            if piece_binding[1] != result.endpoint:
                return RootLineageLimitation.RESULT_CONFLICT

    # --- 4c. Private completed-occurrence/result ownership join ---
    result_by_call: dict[str, ResultFingerprintRecord] = {}
    for result in d_state.results:
        if not ledger.unit():
            return RootLineageLimitation.WORK_UNITS_OVER_BOUND
        result_by_call[result.call_id] = result

    # --- 5/6. The ACTUAL proof source integrity (once per occurrence)
    # + the retained occurrence root bindings + the COMPLETE 1:1 fact
    # inventory (singleton read facts AND region facts) ---
    occ_by_id: dict[str, CompletedReadOccurrence] = {}
    eligible_read: set[str] = set()
    eligible_region: set[str] = set()
    for occ in d_state.occurrences:
        if not ledger.unit():
            return RootLineageLimitation.WORK_UNITS_OVER_BOUND
        record = _h_proof_integrity(occ, g_bounds, p_bounds, o_bounds, ledger)
        if record is None:
            return RootLineageLimitation.WORK_UNITS_OVER_BOUND
        if isinstance(record, RootLineageLimitation):
            return record
        if not record:
            return RootLineageLimitation.MALFORMED_BINDING
        if not ledger.unit():
            return RootLineageLimitation.WORK_UNITS_OVER_BOUND
        if anchor is not None and (
            occ.proof.root_path != ROOT_FILENAME or occ.proof.root_digest != anchor.root_digest
        ):
            return RootLineageLimitation.MALFORMED_BINDING
        if not ledger.unit():
            return RootLineageLimitation.WORK_UNITS_OVER_BOUND
        owning = result_by_call.get(occ.call_id)
        if owning is None or owning.complete is not True:
            return RootLineageLimitation.MALFORMED_BINDING
        if not ledger.unit():
            return RootLineageLimitation.WORK_UNITS_OVER_BOUND
        pieces = occ.proof.pieces
        if (
            len(owning.piece_call_bindings) != len(pieces)
            or len(owning.piece_facts) != len(pieces)
            or len(owning.piece_completion) != len(pieces)
        ):
            return RootLineageLimitation.RESULT_CONFLICT
        for piece_index in range(len(pieces)):
            if not ledger.unit():
                return RootLineageLimitation.WORK_UNITS_OVER_BOUND
            piece = pieces[piece_index]
            binding = owning.piece_call_bindings[piece_index]
            if piece.call_id != binding[0]:
                return RootLineageLimitation.RESULT_CONFLICT
            if piece_index == 0:
                if (
                    binding[1] != owning.endpoint
                    or binding[2] != owning.tool_name
                    or binding[3] != owning.argument_fingerprint
                ):
                    return RootLineageLimitation.RESULT_CONFLICT
            pfact = owning.piece_facts[piece_index]
            if (
                pfact[0] != piece_index
                or pfact[1] != piece.char_length
                or pfact[2] != piece.byte_length
            ):
                return RootLineageLimitation.RESULT_CONFLICT
        if not ledger.unit():
            return RootLineageLimitation.WORK_UNITS_OVER_BOUND
        occ_by_id[occ.occurrence_id] = occ
        singleton = _is_singleton_root_read(occ, ledger.unit)
        if singleton is None:
            return RootLineageLimitation.WORK_UNITS_OVER_BOUND
        if singleton:
            if not ledger.unit():
                return RootLineageLimitation.WORK_UNITS_OVER_BOUND
            eligible_read.add(occ.occurrence_id)
            continue
        segment, _index, ok = _region_root_segment(occ, ledger.unit)
        if not ok:
            return RootLineageLimitation.WORK_UNITS_OVER_BOUND
        if segment is not None:
            if not ledger.unit():
                return RootLineageLimitation.WORK_UNITS_OVER_BOUND
            eligible_region.add(occ.occurrence_id)
    retained_read: set[str] = set()
    retained_region: set[str] = set()
    for fact in facts:
        if not ledger.unit():
            return RootLineageLimitation.WORK_UNITS_OVER_BOUND
        if fact.provenance.kind == "read":
            if not ledger.unit():
                return RootLineageLimitation.WORK_UNITS_OVER_BOUND
            retained_read.add(fact.provenance.occurrence_id)
        elif fact.provenance.kind == "read_region":
            if not ledger.unit():
                return RootLineageLimitation.WORK_UNITS_OVER_BOUND
            retained_region.add(fact.provenance.occurrence_id)
    if not ledger.units(1 + min(len(eligible_read), len(retained_read))):
        return RootLineageLimitation.WORK_UNITS_OVER_BOUND
    if eligible_read != retained_read:
        return RootLineageLimitation.MALFORMED_BINDING
    if not ledger.units(1 + min(len(eligible_region), len(retained_region))):
        return RootLineageLimitation.WORK_UNITS_OVER_BOUND
    if eligible_region != retained_region:
        return RootLineageLimitation.MALFORMED_BINDING

    # --- 7. Per-fact provenance binding + DERIVED flags (S1, the
    # stored bits are NEVER trusted) ---
    issued_ids: set[str] = set()
    for issuance in d_state.issuances:
        if not ledger.unit():
            return RootLineageLimitation.WORK_UNITS_OVER_BOUND
        issued_ids.add(issuance.call_id)
    parent_map: dict[str, list[str]] = {}
    for link in d_state.parent_links:
        if not ledger.unit():
            return RootLineageLimitation.WORK_UNITS_OVER_BOUND
        parent_map.setdefault(link.child, []).append(link.parent)
    for fact in facts:
        if not ledger.unit():
            return RootLineageLimitation.WORK_UNITS_OVER_BOUND
        p = fact.provenance
        if not isinstance(p, (ReadRootProvenance, RootRegionReadProvenance)):
            # The envelope fact's derived flags are fixed by law.
            if fact.issued is not False or fact.authority is not True:
                return RootLineageLimitation.MALFORMED_BINDING
            continue
        if not ledger.unit():
            return RootLineageLimitation.WORK_UNITS_OVER_BOUND
        bound_occ = occ_by_id.get(p.occurrence_id)
        if bound_occ is None or bound_occ.call_id != p.call_id or bound_occ.endpoint != p.endpoint:
            return RootLineageLimitation.MALFORMED_BINDING
        if not ledger.unit():
            return RootLineageLimitation.WORK_UNITS_OVER_BOUND
        proof = bound_occ.proof
        if isinstance(p, ReadRootProvenance):
            if (
                proof.source_digest != p.read_digest
                or proof.source_byte_length != p.read_byte_length
                or fact.source_digest != proof.source_digest
                or fact.source_byte_length != proof.source_byte_length
            ):
                return RootLineageLimitation.MALFORMED_BINDING
        else:
            # The NEW read_region join: the WHOLE proof aggregate
            # binding AND the ACTUAL root segment/member binding
            # (a detached coherently rekeyed region is refused).
            if (
                proof.source_digest != p.whole_proof_digest
                or proof.source_byte_length != p.whole_proof_byte_length
            ):
                return RootLineageLimitation.MALFORMED_BINDING
            if not ledger.unit():
                return RootLineageLimitation.WORK_UNITS_OVER_BOUND
            if p.root_segment_index >= len(proof.segments):
                return RootLineageLimitation.MALFORMED_BINDING
            segment = proof.segments[p.root_segment_index]
            if (
                len(segment.member_positions) != 1
                or segment.member_positions[0] != p.root_member_position
                or segment.member_digest != p.root_member_digest
                or segment.byte_length != p.root_member_byte_length
            ):
                return RootLineageLimitation.MALFORMED_BINDING
            if not ledger.unit():
                return RootLineageLimitation.WORK_UNITS_OVER_BOUND
            if (
                p.root_member_position >= len(proof.requested_members)
                or proof.requested_members[p.root_member_position].normalized != ROOT_FILENAME
            ):
                return RootLineageLimitation.MALFORMED_BINDING
            if (
                fact.source_digest != p.root_member_digest
                or fact.source_byte_length != p.root_member_byte_length
            ):
                return RootLineageLimitation.MALFORMED_BINDING
        # The DERIVED flag law (S1): re-derived from the ACTUAL D
        # state; the stored bits must match exactly.
        derived_issued = p.call_id in issued_ids
        derived_authority = False
        if derived_issued and bound_occ.anchored:
            try:
                ancestors = _ancestors_of(p.occurrence_id, parent_map, ledger)
            except _WorkOverflowError:
                return RootLineageLimitation.WORK_UNITS_OVER_BOUND
            if not ledger.unit():
                return RootLineageLimitation.WORK_UNITS_OVER_BOUND
            derived_authority = CAUSAL_ROOT_FACT in ancestors
        if fact.issued is not derived_issued or fact.authority is not derived_authority:
            return RootLineageLimitation.MALFORMED_BINDING
    return None


# --- The public region operations -----------------------------------------


def bootstrap_root_region_lineage(
    requests: tuple[GraphRequest, ...],
    ns: RootRegionLineageNamespace,
) -> RootRegionLineageTransition:
    """The ONE legitimate bootstrap over the NEW region contract.

    Runs the ACTUAL accepted D bootstrap (the legitimate effective
    Responses AGENTS envelope with exact source bytes, workspace
    and first original spans; exact empty root is legal; rootless
    refuses) under the STRICT old root law -- no relaxed envelope
    law and no refresh acquisition at bootstrap (a competing root
    read in the bootstrap batch keeps the exact old refusal).  The
    accepted state is wrapped with the bootstrap ENVELOPE fact
    (never issued, always authoritative) PLUS the EXACT eligible-
    source inventory of the bootstrap batch (every D-accepted
    eligible source candidate retained UNPROVEN with normal caps
    and flags, so the accepted bootstrap state satisfies its own
    complete validation inventory) and region revision 1; every
    refusal preserves the EXACT prior state (the region composition
    origin)."""
    if not _region_preflight_ns_shape(ns):
        if _hex64_ok(ns.lineage_key) and _hex64_ok(ns.history_key):
            origin = RootRegionLineageState(
                lineage_key=ns.lineage_key,
                revision=0,
                d_state=CausalHistoryState(history_key=ns.history_key, revision=0),
            )
            return _region_closed(origin, RootLineageOutcome.REFUSED_FOREIGN_SCOPE, ())
        raise _fixed("the bootstrap scope must carry actual 64-hex key fields")
    outer = _HOuter(ns.root_lineage_bounds.max_total_work_units)
    empty = CausalHistoryState(history_key=ns.history_key, revision=0)
    origin = RootRegionLineageState(lineage_key=ns.lineage_key, revision=0, d_state=empty)
    d_ns, gated = _region_gate(origin, ns, 0, outer)
    if gated is not None:
        return gated
    assert d_ns is not None
    ctx = _RootLineageContext(
        known_root_digests=frozenset(),
        relaxed_envelope_law=False,
        root_read_acquisition=False,
        outer_charge=outer.unit,
    )
    try:
        d_trans = _observe_causal_history_core(requests, d_ns, empty, 0, context=ctx)
    except _HOuterOverflow:
        return _region_closed(
            origin,
            RootLineageOutcome.REFUSED_OVER_BOUND,
            (RootLineageLimitation.WORK_UNITS_OVER_BOUND,),
        )
    if d_trans.outcome is CausalHistoryOutcome.REPLAYED:
        if not outer.units(2 * len(d_trans.diagnostics)):
            return _region_closed(
                origin,
                RootLineageOutcome.REFUSED_OVER_BOUND,
                (RootLineageLimitation.WORK_UNITS_OVER_BOUND,),
                d_trans,
            )
        limitations = tuple(_H_LIMITATION_MAP[lim] for lim in d_trans.diagnostics)
        return _region_closed(origin, RootLineageOutcome.REPLAYED, limitations, d_trans)
    if d_trans.outcome is not CausalHistoryOutcome.ACCEPTED:
        return _region_map_d_refusal(d_trans, ctx, origin, outer)
    root = d_trans.state.root
    if root is None:
        raise _fixed("an accepted bootstrap retains the evidenced root anchor")
    bounds = ns.root_lineage_bounds
    if not outer.unit():
        return _region_closed(
            origin,
            RootLineageOutcome.REFUSED_OVER_BOUND,
            (RootLineageLimitation.WORK_UNITS_OVER_BOUND,),
            d_trans,
        )
    if root.source_byte_length > bounds.max_retained_root_source_bytes:
        return _region_closed(
            origin,
            RootLineageOutcome.REFUSED_OVER_BOUND,
            (RootLineageLimitation.ROOT_SOURCE_BYTES_OVER_BOUND,),
            d_trans,
        )
    if not outer.units(_FACT_BUILD_UNITS):
        return _region_closed(
            origin,
            RootLineageOutcome.REFUSED_OVER_BOUND,
            (RootLineageLimitation.WORK_UNITS_OVER_BOUND,),
            d_trans,
        )
    anchor_fact = RootRegionLineageFact(
        source_digest=root.root_digest,
        source_byte_length=root.source_byte_length,
        provenance=EnvelopeRootProvenance(
            root_digest=root.root_digest,
            workspace=root.workspace,
            source_byte_length=root.source_byte_length,
        ),
        issued=False,
        authority=True,
    )
    # The EXACT eligible-source inventory of the bootstrap batch:
    # EVERY D-accepted eligible source candidate (the singleton
    # whole root read keeps its OLD read provenance; a proven
    # mixed single root uses the NEW region provenance) is
    # retained UNPROVEN alongside the ONE anchor fact, counted
    # and source-bytes preflighted BEFORE materialization under
    # the unchanged H ceilings (K4), with the S1 re-derivation
    # and the retention caps.
    new_facts = _region_new_root_facts(
        d_trans.new_occurrences,
        1,
        root.source_byte_length,
        bounds,
        outer,
    )
    if new_facts is None:
        return _region_closed(
            origin,
            RootLineageOutcome.REFUSED_OVER_BOUND,
            (RootLineageLimitation.WORK_UNITS_OVER_BOUND,),
            d_trans,
        )
    if isinstance(new_facts, RootLineageLimitation):
        return _region_closed(
            origin,
            RootLineageOutcome.REFUSED_OVER_BOUND,
            (new_facts,),
            d_trans,
        )
    combined = _region_combine_facts((anchor_fact,), new_facts, outer)
    if combined is None:
        return _region_closed(
            origin,
            RootLineageOutcome.REFUSED_OVER_BOUND,
            (RootLineageLimitation.WORK_UNITS_OVER_BOUND,),
            d_trans,
        )
    derived = _region_derive_flags(d_trans.state, combined, outer)
    if derived is None:
        return _region_closed(
            origin,
            RootLineageOutcome.REFUSED_OVER_BOUND,
            (RootLineageLimitation.WORK_UNITS_OVER_BOUND,),
            d_trans,
        )
    over = _region_retention_check(derived, bounds, outer, origin, d_trans)
    if over is not None:
        return over
    if not outer.units(2 * len(new_facts)):
        return _region_closed(
            origin,
            RootLineageOutcome.REFUSED_OVER_BOUND,
            (RootLineageLimitation.WORK_UNITS_OVER_BOUND,),
            d_trans,
        )
    new_keys = {_region_provenance_key(f.provenance) for f in new_facts}
    if not outer.units(2 * len(derived)):
        return _region_closed(
            origin,
            RootLineageOutcome.REFUSED_OVER_BOUND,
            (RootLineageLimitation.WORK_UNITS_OVER_BOUND,),
            d_trans,
        )
    retained_new = tuple(f for f in derived if _region_provenance_key(f.provenance) in new_keys)
    if not outer.units(_STATE_BUILD_UNITS + _STATE_FACT_UNITS * len(derived)):
        return _region_closed(
            origin,
            RootLineageOutcome.REFUSED_OVER_BOUND,
            (RootLineageLimitation.WORK_UNITS_OVER_BOUND,),
            d_trans,
        )
    new_state = RootRegionLineageState(
        lineage_key=ns.lineage_key,
        revision=1,
        d_state=d_trans.state,
        root_facts=derived,
    )
    if not outer.units(_TRANSITION_BUILD_UNITS + _STATE_FACT_UNITS * len(retained_new)):
        return _region_closed(
            origin,
            RootLineageOutcome.REFUSED_OVER_BOUND,
            (RootLineageLimitation.WORK_UNITS_OVER_BOUND,),
            d_trans,
        )
    return RootRegionLineageTransition(
        state=new_state,
        outcome=RootLineageOutcome.ACCEPTED,
        d_transition=d_trans,
        revision_before=0,
        revision_after=1,
        d_revision_before=d_trans.revision_before,
        d_revision_after=d_trans.revision_after,
        new_root_facts=(anchor_fact,) + retained_new,
    )


def _region_observe_finalize(
    state: RootRegionLineageState,
    ns: RootRegionLineageNamespace,
    d_trans: CausalHistoryTransition,
    outer: _HOuter,
    deferred: tuple[str, ...],
) -> RootRegionLineageTransition:
    """The shared ACCEPTED-D-candidate finalization of the NEW
    region observation.

    The NEW retention (EVERY eligible source candidate: the
    singleton whole read keeps its old provenance, the proven
    mixed single root uses the NEW region provenance; counted and
    source-bytes preflighted BEFORE retention), the S1 re-
    derivation over ALL retained facts, the retention caps, and
    THEN the atomic deferred-verification with the deterministic
    refusal precedence: the EXISTING envelope deferral
    verification (every deferred envelope digest must match an
    authoritative retained root fact -- a same-batch
    independently earned AUTHORITATIVE ROOT REGION establishes the
    matching envelope's known-source status atomically; the
    envelope itself grants no ordering and cannot authorize
    itself).  A deferred envelope WITHOUT authority -- or a
    replay with a nonempty deferral sink (replays earn no facts) --
    is a fixed whole-transition REFUSED_ROOT_AUTHORITY preserving
    the EXACT prior region state (the actual accepted D candidate
    is retained by identity as discarded evidence, never partially
    published).  Unknown mixed root sources need NO independent
    singleton in this NEW contract: they are retained unproven
    and may later earn authority by genuine issuance/receipt/
    ancestry."""
    old_bytes = 0
    for fact in state.root_facts:
        if not outer.unit():
            return _region_closed(
                state,
                RootLineageOutcome.REFUSED_OVER_BOUND,
                (RootLineageLimitation.WORK_UNITS_OVER_BOUND,),
                d_trans,
            )
        old_bytes += fact.source_byte_length
    new_facts = _region_new_root_facts(
        d_trans.new_occurrences,
        len(state.root_facts),
        old_bytes,
        ns.root_lineage_bounds,
        outer,
    )
    if new_facts is None:
        return _region_closed(
            state,
            RootLineageOutcome.REFUSED_OVER_BOUND,
            (RootLineageLimitation.WORK_UNITS_OVER_BOUND,),
            d_trans,
        )
    if isinstance(new_facts, RootLineageLimitation):
        return _region_closed(
            state,
            RootLineageOutcome.REFUSED_OVER_BOUND,
            (new_facts,),
            d_trans,
        )
    combined = _region_combine_facts(state.root_facts, new_facts, outer)
    if combined is None:
        return _region_closed(
            state,
            RootLineageOutcome.REFUSED_OVER_BOUND,
            (RootLineageLimitation.WORK_UNITS_OVER_BOUND,),
            d_trans,
        )
    derived = _region_derive_flags(d_trans.state, combined, outer)
    if derived is None:
        return _region_closed(
            state,
            RootLineageOutcome.REFUSED_OVER_BOUND,
            (RootLineageLimitation.WORK_UNITS_OVER_BOUND,),
            d_trans,
        )
    bounds = ns.root_lineage_bounds
    over = _region_retention_check(derived, bounds, outer, state, d_trans)
    if over is not None:
        return over
    if deferred:
        if not outer.unit():
            return _region_closed(
                state,
                RootLineageOutcome.REFUSED_OVER_BOUND,
                (RootLineageLimitation.WORK_UNITS_OVER_BOUND,),
                d_trans,
            )
        authoritative: set[str] = set()
        for fact in derived:
            if not outer.unit():
                return _region_closed(
                    state,
                    RootLineageOutcome.REFUSED_OVER_BOUND,
                    (RootLineageLimitation.WORK_UNITS_OVER_BOUND,),
                    d_trans,
                )
            if fact.authority:
                authoritative.add(fact.source_digest)
        for digest in deferred:
            if not outer.unit():
                return _region_closed(
                    state,
                    RootLineageOutcome.REFUSED_OVER_BOUND,
                    (RootLineageLimitation.WORK_UNITS_OVER_BOUND,),
                    d_trans,
                )
            if digest not in authoritative:
                return _region_closed(
                    state,
                    RootLineageOutcome.REFUSED_ROOT_AUTHORITY,
                    (RootLineageLimitation.ENVELOPE_UNPROVEN,),
                    d_trans,
                )
    if not outer.units(2 * len(new_facts)):
        return _region_closed(
            state,
            RootLineageOutcome.REFUSED_OVER_BOUND,
            (RootLineageLimitation.WORK_UNITS_OVER_BOUND,),
            d_trans,
        )
    new_keys = {_region_provenance_key(f.provenance) for f in new_facts}
    if not outer.units(2 * len(derived)):
        return _region_closed(
            state,
            RootLineageOutcome.REFUSED_OVER_BOUND,
            (RootLineageLimitation.WORK_UNITS_OVER_BOUND,),
            d_trans,
        )
    retained_new = tuple(f for f in derived if _region_provenance_key(f.provenance) in new_keys)
    if not outer.units(_STATE_BUILD_UNITS + _STATE_FACT_UNITS * len(derived)):
        return _region_closed(
            state,
            RootLineageOutcome.REFUSED_OVER_BOUND,
            (RootLineageLimitation.WORK_UNITS_OVER_BOUND,),
            d_trans,
        )
    new_state = RootRegionLineageState(
        lineage_key=ns.lineage_key,
        revision=state.revision + 1,
        d_state=d_trans.state,
        root_facts=derived,
    )
    if not outer.units(_TRANSITION_BUILD_UNITS + _STATE_FACT_UNITS * len(retained_new)):
        return _region_closed(
            state,
            RootLineageOutcome.REFUSED_OVER_BOUND,
            (RootLineageLimitation.WORK_UNITS_OVER_BOUND,),
            d_trans,
        )
    return RootRegionLineageTransition(
        state=new_state,
        outcome=RootLineageOutcome.ACCEPTED,
        d_transition=d_trans,
        revision_before=state.revision,
        revision_after=state.revision + 1,
        d_revision_before=d_trans.revision_before,
        d_revision_after=d_trans.revision_after,
        new_root_facts=retained_new,
    )


def observe_root_region_lineage(
    state: RootRegionLineageState,
    ns: RootRegionLineageNamespace,
    expected_revision: int,
    requests: tuple[GraphRequest, ...],
) -> RootRegionLineageTransition:
    """The NEW region-contract observation transition.

    The same gates as the original-payload H observation run
    FIRST (fixed scope/CAS/D-state-binding/version fences, the
    charged FULL namespace revalidation, the charged cross-record
    state integrity) before any compatibility interpretation.  The
    ACTUAL D observation then runs under the NEW private region-
    acquisition policy: the relaxed envelope law AND the singleton
    root-read acquisition AND the NEW mixed root-region
    acquisition (a proven SINGLE root-path segment of a mixed
    proof is retained SOURCE evidence -- known OR unknown: an
    unknown mixed root needs NO independent singleton in this NEW
    contract and stays unproven until genuine issuance/receipt/
    ancestry).  Repeated root operands, opaque root groups and
    every no-context / no-flag run keep the exact old refusal.
    After an accepted D transition the shared finalization runs
    (retention, S1 re-derivation, caps, atomic envelope
    verification with its deterministic refusal precedence).  A
    deferred envelope without an authoritative retained root fact
    is a fixed whole-transition REFUSED_ROOT_AUTHORITY preserving
    the EXACT prior region state (the actual accepted D candidate
    is retained by identity as discarded evidence).  The private
    region-occurrence counting, candidate attempts, allocation,
    inventory/fact construction and final authority membership
    work is charged on the SAME ONE new-operation outer coupled to
    the ACTUAL D work; the inherited local domains stay
    independent with unchanged limits.  No independent current-
    selection query is made merely to acquire source evidence."""
    if not _region_state_shape(state):
        raise _fixed("the region lineage state must carry an actual bounded state record")
    if not _region_preflight_ns_shape(ns):
        return _region_closed(state, RootLineageOutcome.REFUSED_FOREIGN_SCOPE, ())
    outer = _HOuter(ns.root_lineage_bounds.max_total_work_units)
    d_ns, gated = _region_gate(state, ns, expected_revision, outer)
    if gated is not None:
        return gated
    assert d_ns is not None
    if not outer.unit():
        return _region_closed(
            state,
            RootLineageOutcome.REFUSED_OVER_BOUND,
            (RootLineageLimitation.WORK_UNITS_OVER_BOUND,),
        )
    problem = validate_root_region_lineage_state(
        state,
        ns.root_lineage_bounds,
        outer,
        history_bounds=ns.history_bounds,
        graph_bounds=ns.graph_bounds,
        proof_bounds=ns.proof_bounds,
        observation_bounds=ns.observation_bounds,
        workspace=ns.workspace,
    )
    if problem is not None:
        outcome = (
            RootLineageOutcome.REFUSED_OVER_BOUND
            if problem.value.endswith("_over_bound")
            else RootLineageOutcome.REFUSED_CONFLICT
        )
        return _region_closed(state, outcome, (problem,))
    d_state = state.d_state
    # The pre-batch known root digest set (the relaxed envelope
    # law's membership context): ONLY the bootstrap anchor and the
    # actually EARNED authoritative root sources after the charged
    # state validation (K1) -- merely retained complete bytes do
    # not justify an envelope; a new source needs its own
    # authority, charged per fact.  Known historical versions may
    # supply ordinary source evidence (never freshness).
    known: set[str] = set()
    if d_state.root is not None:
        if not outer.unit():
            return _region_closed(
                state,
                RootLineageOutcome.REFUSED_OVER_BOUND,
                (RootLineageLimitation.WORK_UNITS_OVER_BOUND,),
            )
        known.add(d_state.root.root_digest)
    for fact in state.root_facts:
        if not outer.unit():
            return _region_closed(
                state,
                RootLineageOutcome.REFUSED_OVER_BOUND,
                (RootLineageLimitation.WORK_UNITS_OVER_BOUND,),
            )
        if fact.authority:
            known.add(fact.source_digest)
    ctx = _RootLineageContext(
        known_root_digests=frozenset(known),
        relaxed_envelope_law=True,
        root_read_acquisition=True,
        outer_charge=outer.unit,
        region_root_acquisition=True,
    )
    deferred_sink: list[frozenset[str]] = []
    try:
        d_trans = _observe_causal_history_core(
            requests,
            d_ns,
            d_state,
            expected_revision,
            context=ctx,
            deferred_sink=deferred_sink,
        )
    except _HOuterOverflow:
        return _region_closed(
            state,
            RootLineageOutcome.REFUSED_OVER_BOUND,
            (RootLineageLimitation.WORK_UNITS_OVER_BOUND,),
        )
    deferred = _deferred_region_digests(deferred_sink, outer)
    if deferred is None:
        return _region_closed(
            state,
            RootLineageOutcome.REFUSED_OVER_BOUND,
            (RootLineageLimitation.WORK_UNITS_OVER_BOUND,),
            d_trans,
        )
    if d_trans.outcome is CausalHistoryOutcome.REPLAYED:
        if deferred:
            # Replays earn no facts: an unknown changed envelope in
            # a replayed batch is a fixed root-authority refusal.
            return _region_closed(
                state,
                RootLineageOutcome.REFUSED_ROOT_AUTHORITY,
                (RootLineageLimitation.ENVELOPE_UNPROVEN,),
                d_trans,
            )
        if not outer.units(2 * len(d_trans.diagnostics)):
            return _region_closed(
                state,
                RootLineageOutcome.REFUSED_OVER_BOUND,
                (RootLineageLimitation.WORK_UNITS_OVER_BOUND,),
                d_trans,
            )
        limitations = tuple(_H_LIMITATION_MAP[lim] for lim in d_trans.diagnostics)
        return _region_closed(state, RootLineageOutcome.REPLAYED, limitations, d_trans)
    if d_trans.outcome is not CausalHistoryOutcome.ACCEPTED:
        return _region_map_d_refusal(d_trans, ctx, state, outer)
    return _region_observe_finalize(state, ns, d_trans, outer, deferred)


def _region_register_finalize(
    state: RootRegionLineageState,
    ns: RootRegionLineageNamespace,
    d_trans: CausalHistoryTransition,
    outer: _HOuter,
) -> RootRegionLineageTransition:
    """The shared accepted-registration finalization (S1 re-
    derivation over ALL retained facts; no new root fact is
    retained -- only reads create occurrences)."""
    derived = _region_derive_flags(d_trans.state, state.root_facts, outer)
    if derived is None:
        return _region_closed(
            state,
            RootLineageOutcome.REFUSED_OVER_BOUND,
            (RootLineageLimitation.WORK_UNITS_OVER_BOUND,),
            d_trans,
        )
    if not outer.units(_STATE_BUILD_UNITS + _STATE_FACT_UNITS * len(derived)):
        return _region_closed(
            state,
            RootLineageOutcome.REFUSED_OVER_BOUND,
            (RootLineageLimitation.WORK_UNITS_OVER_BOUND,),
            d_trans,
        )
    new_state = RootRegionLineageState(
        lineage_key=ns.lineage_key,
        revision=state.revision + 1,
        d_state=d_trans.state,
        root_facts=derived,
    )
    if not outer.units(_TRANSITION_BUILD_UNITS):
        return _region_closed(
            state,
            RootLineageOutcome.REFUSED_OVER_BOUND,
            (RootLineageLimitation.WORK_UNITS_OVER_BOUND,),
            d_trans,
        )
    return RootRegionLineageTransition(
        state=new_state,
        outcome=RootLineageOutcome.ACCEPTED,
        d_transition=d_trans,
        revision_before=state.revision,
        revision_after=state.revision + 1,
        d_revision_before=d_trans.revision_before,
        d_revision_after=d_trans.revision_after,
    )


def _region_register_preflight(
    state: RootRegionLineageState,
    ns: RootRegionLineageNamespace,
    expected_revision: int,
) -> tuple[
    RootRegionLineageTransition | None,
    CausalHistoryNamespace | None,
    _HOuter | None,
    _RootLineageContext | None,
]:
    """The shared registration pre-gates (shape, foreign scope,
    gate, charged state integrity).  Returns the refusal (or the
    derived D namespace + outer + no-acquisition context)."""
    if not _region_state_shape(state):
        raise _fixed("the region lineage state must carry an actual bounded state record")
    if not _region_preflight_ns_shape(ns):
        return _region_closed(state, RootLineageOutcome.REFUSED_FOREIGN_SCOPE, ()), None, None, None
    outer = _HOuter(ns.root_lineage_bounds.max_total_work_units)
    d_ns, gated = _region_gate(state, ns, expected_revision, outer)
    if gated is not None:
        return gated, None, None, None
    assert d_ns is not None
    if not outer.unit():
        return (
            _region_closed(
                state,
                RootLineageOutcome.REFUSED_OVER_BOUND,
                (RootLineageLimitation.WORK_UNITS_OVER_BOUND,),
            ),
            None,
            None,
            None,
        )
    problem = validate_root_region_lineage_state(
        state,
        ns.root_lineage_bounds,
        outer,
        history_bounds=ns.history_bounds,
        graph_bounds=ns.graph_bounds,
        proof_bounds=ns.proof_bounds,
        observation_bounds=ns.observation_bounds,
        workspace=ns.workspace,
    )
    if problem is not None:
        outcome = (
            RootLineageOutcome.REFUSED_OVER_BOUND
            if problem.value.endswith("_over_bound")
            else RootLineageOutcome.REFUSED_CONFLICT
        )
        return _region_closed(state, outcome, (problem,)), None, None, None
    ctx = _RootLineageContext(
        known_root_digests=frozenset(),
        relaxed_envelope_law=False,
        root_read_acquisition=False,
        outer_charge=outer.unit,
    )
    return None, d_ns, outer, ctx


def register_root_region_issuance(
    state: RootRegionLineageState,
    ns: RootRegionLineageNamespace,
    call_id: str,
    endpoint: str,
    tool_name: str,
    arguments: str,
    parent_frontier: tuple[str, ...] | list[str],
    expected_revision: int,
) -> RootRegionLineageTransition:
    """Trusted INTERNAL issuance registration under the NEW region
    contract (the actual D issuance law, ONE new-operation outer,
    coupled D work ledger).  Issuance is NOT source acquisition or
    success; it can -- together with a subsequent matching
    receipt -- earn a previously unproven root read or ROOT REGION
    its authority via the S1 re-derivation.  The accepted state
    re-derives ALL facts' flags; no new root fact is retained
    (only reads create occurrences)."""
    pre, d_ns, outer, ctx = _region_register_preflight(state, ns, expected_revision)
    if pre is not None:
        return pre
    assert d_ns is not None and outer is not None and ctx is not None
    try:
        d_trans = _register_issuance_core(
            state.d_state,
            d_ns,
            call_id,
            endpoint,
            tool_name,
            arguments,
            parent_frontier,
            expected_revision,
            context=ctx,
        )
    except _HOuterOverflow:
        return _region_closed(
            state,
            RootLineageOutcome.REFUSED_OVER_BOUND,
            (RootLineageLimitation.WORK_UNITS_OVER_BOUND,),
        )
    if d_trans.outcome is CausalHistoryOutcome.REPLAYED:
        if not outer.units(2 * len(d_trans.diagnostics)):
            return _region_closed(
                state,
                RootLineageOutcome.REFUSED_OVER_BOUND,
                (RootLineageLimitation.WORK_UNITS_OVER_BOUND,),
                d_trans,
            )
        limitations = tuple(_H_LIMITATION_MAP[lim] for lim in d_trans.diagnostics)
        return _region_closed(state, RootLineageOutcome.REPLAYED, limitations, d_trans)
    if d_trans.outcome is not CausalHistoryOutcome.ACCEPTED:
        return _region_map_d_refusal(d_trans, ctx, state, outer)
    return _region_register_finalize(state, ns, d_trans, outer)


def register_root_region_receipt(
    state: RootRegionLineageState,
    ns: RootRegionLineageNamespace,
    call_id: str,
    endpoint: str,
    tool_name: str,
    arguments: str,
    parent_frontier: tuple[str, ...] | list[str],
    expected_revision: int,
) -> RootRegionLineageTransition:
    """Trusted INTERNAL late-receipt registration under the NEW
    region contract (the actual D receipt law, ONE new-operation
    outer, coupled D work ledger).  A matching valid late receipt
    anchors a previously unanchored occurrence under its frozen
    frontier and can thereby earn a previously unproven root read
    or ROOT REGION its authority via the S1 re-derivation (even
    for a NONROOT ancestor's receipt, which opens a descendant's
    bootstrap path).  A bad/cyclic/mismatched receipt refuses
    atomically with the EXACT prior region state."""
    pre, d_ns, outer, ctx = _region_register_preflight(state, ns, expected_revision)
    if pre is not None:
        return pre
    assert d_ns is not None and outer is not None and ctx is not None
    try:
        d_trans = _register_receipt_core(
            state.d_state,
            d_ns,
            call_id,
            endpoint,
            tool_name,
            arguments,
            parent_frontier,
            expected_revision,
            context=ctx,
        )
    except _HOuterOverflow:
        return _region_closed(
            state,
            RootLineageOutcome.REFUSED_OVER_BOUND,
            (RootLineageLimitation.WORK_UNITS_OVER_BOUND,),
        )
    if d_trans.outcome is CausalHistoryOutcome.REPLAYED:
        if not outer.units(2 * len(d_trans.diagnostics)):
            return _region_closed(
                state,
                RootLineageOutcome.REFUSED_OVER_BOUND,
                (RootLineageLimitation.WORK_UNITS_OVER_BOUND,),
                d_trans,
            )
        limitations = tuple(_H_LIMITATION_MAP[lim] for lim in d_trans.diagnostics)
        return _region_closed(state, RootLineageOutcome.REPLAYED, limitations, d_trans)
    if d_trans.outcome is not CausalHistoryOutcome.ACCEPTED:
        return _region_map_d_refusal(d_trans, ctx, state, outer)
    return _region_register_finalize(state, ns, d_trans, outer)


def _region_selection_kernel(
    state: RootRegionLineageState,
    d_state: CausalHistoryState,
    outer: _HOuter,
) -> RootRegionSelectionResult:
    """The charged causal-maximal selection compute (the accepted
    H selection law, NEW contract dispatch): a fact B dominates A
    iff A is the bootstrap anchor or A's occurrence is a strict
    ancestor of B's occurrence (BOTH supported read provenance
    variants -- the old whole read and the NEW region read -- have
    the same partial-order conflict semantics; a child of one
    branch dominates that branch's ancestors only; a genuine child
    of ALL relevant branches dominates all of them; delayed older
    receipts never override a proven descendant).  ALL maximal
    witnesses with ONE equal source digest are OK; differing
    maximal sources are an explicit ROOT_CONTENT_CONFLICT with NO
    selected source; no authoritative fact at all is the honest
    NO_SELECTED_ROOT; retained complete but unproven root reads or
    regions expose the fixed ROOT_SOURCE_UNPROVEN limitation."""
    scope_key = state.lineage_key
    revision = state.revision

    def _refused(limitation: RootLineageLimitation) -> RootRegionSelectionResult:
        return RootRegionSelectionResult(
            outcome=RootSelectionOutcome.REFUSED,
            limitations=(limitation,),
            lineage_key=scope_key,
            revision=revision,
        )

    parent_map: dict[str, list[str]] = {}
    for link in d_state.parent_links:
        if not outer.unit():
            return _refused(RootLineageLimitation.WORK_UNITS_OVER_BOUND)
        parent_map.setdefault(link.child, []).append(link.parent)
    authoritative: list[RootRegionLineageFact] = []
    unproven = False
    for fact in state.root_facts:
        if not outer.unit():
            return _refused(RootLineageLimitation.WORK_UNITS_OVER_BOUND)
        if fact.authority:
            authoritative.append(fact)
        elif isinstance(fact.provenance, (ReadRootProvenance, RootRegionReadProvenance)):
            unproven = True
    limitations: tuple[RootLineageLimitation, ...] = (
        (RootLineageLimitation.ROOT_SOURCE_UNPROVEN,) if unproven else ()
    )
    if not authoritative:
        if not outer.units(_RESULT_BUILD_UNITS):
            return _refused(RootLineageLimitation.WORK_UNITS_OVER_BOUND)
        return RootRegionSelectionResult(
            outcome=RootSelectionOutcome.NO_SELECTED_ROOT,
            limitations=limitations,
            lineage_key=scope_key,
            revision=revision,
        )
    ancestors: dict[tuple[str, str], set[str]] = {}
    for fact in authoritative:
        key = _region_provenance_key(fact.provenance)
        if not outer.unit():
            return _refused(RootLineageLimitation.WORK_UNITS_OVER_BOUND)
        if isinstance(fact.provenance, EnvelopeRootProvenance):
            ancestors[key] = set()
        else:
            try:
                ancestors[key] = _ancestors_of(fact.provenance.occurrence_id, parent_map, outer)
            except _WorkOverflowError:
                return _refused(RootLineageLimitation.WORK_UNITS_OVER_BOUND)
    dominated: set[tuple[str, str]] = set()
    for a in authoritative:
        key_a = _region_provenance_key(a.provenance)
        for b in authoritative:
            if not outer.unit():
                return _refused(RootLineageLimitation.WORK_UNITS_OVER_BOUND)
            if a is b:
                continue
            key_b = _region_provenance_key(b.provenance)
            if a.provenance.kind == "envelope" and b.provenance.kind in ("read", "read_region"):
                dominated.add(key_a)
            elif (
                a.provenance.kind in ("read", "read_region")
                and b.provenance.kind in ("read", "read_region")
                and a.provenance.occurrence_id in ancestors[key_b]
            ):
                dominated.add(key_a)
    maximal_list: list[RootRegionLineageFact] = []
    for f in authoritative:
        if not outer.unit():
            return _refused(RootLineageLimitation.WORK_UNITS_OVER_BOUND)
        if _region_provenance_key(f.provenance) not in dominated:
            maximal_list.append(f)
    if len(maximal_list) > 1 and not outer.units(len(maximal_list) * (len(maximal_list) - 1)):
        return _refused(RootLineageLimitation.WORK_UNITS_OVER_BOUND)
    maximal = tuple(sorted(maximal_list, key=lambda f: _region_provenance_key(f.provenance)))
    digests: set[str] = set()
    for f in maximal:
        if not outer.unit():
            return _refused(RootLineageLimitation.WORK_UNITS_OVER_BOUND)
        digests.add(f.source_digest)
    if not outer.units(_RESULT_BUILD_UNITS + _RESULT_FACT_UNITS * len(maximal)):
        return _refused(RootLineageLimitation.WORK_UNITS_OVER_BOUND)
    if len(digests) == 1:
        return RootRegionSelectionResult(
            outcome=RootSelectionOutcome.OK,
            selected_source_digest=maximal[0].source_digest,
            witness_facts=maximal,
            limitations=limitations,
            lineage_key=scope_key,
            revision=revision,
        )
    return RootRegionSelectionResult(
        outcome=RootSelectionOutcome.ROOT_CONTENT_CONFLICT,
        witness_facts=maximal,
        limitations=limitations,
        lineage_key=scope_key,
        revision=revision,
    )


def select_current_root_region(
    state: RootRegionLineageState,
    ns: RootRegionLineageNamespace,
    bounds: RootLineageBounds | None = None,
) -> RootRegionSelectionResult:
    """The bounded pure current-root selection query (NEW region
    contract).

    The O(1) shape preflight, the fixed early scope/D-state-
    binding/version fences, the charged full revalidation and the
    charged cross-record state validation run BEFORE any positive
    interpretation; a budget/foreign/version/malformed input is a
    fixed typed REFUSED result (never relabelled as a root
    absence).  The optional query override bounds are fresh
    actual-field validated BEFORE any fuel is read from them.
    The query never advances any revision and never manufactures
    a root; a differing authoritative conflict carries NO
    selected source."""
    if not _region_state_shape(state):
        raise _fixed("the region lineage state must carry an actual bounded state record")
    scope_key = state.lineage_key
    revision = state.revision

    def _refused(limitation: RootLineageLimitation) -> RootRegionSelectionResult:
        return RootRegionSelectionResult(
            outcome=RootSelectionOutcome.REFUSED,
            limitations=(limitation,),
            lineage_key=scope_key,
            revision=revision,
        )

    if not _region_preflight_ns_shape(ns):
        return _refused(RootLineageLimitation.FOREIGN_SCOPE)
    effective = ns.root_lineage_bounds
    if bounds is not None:
        if not root_lineage_bounds_shape_ok(bounds):
            return _refused(RootLineageLimitation.MALFORMED_BINDING)
        try:
            effective = RootLineageBounds.model_validate(
                bounds.model_dump(mode="python", warnings=False)
            )
        except Exception:
            return _refused(RootLineageLimitation.MALFORMED_BINDING)
    outer = _HOuter(effective.max_total_work_units)
    if not outer.units(11):
        return _refused(RootLineageLimitation.WORK_UNITS_OVER_BOUND)
    if state.lineage_key != ns.lineage_key:
        return _refused(RootLineageLimitation.FOREIGN_SCOPE)
    if state.d_state.history_key != ns.history_key:
        return _refused(RootLineageLimitation.FOREIGN_SCOPE)
    for actual, supported in _region_version_pairs(ns):
        if actual != supported:
            return _refused(RootLineageLimitation.VERSION_UNSUPPORTED)
    if not outer.units(_region_ns_reservation(ns)):
        return _refused(RootLineageLimitation.WORK_UNITS_OVER_BOUND)
    if not _region_revalidate_ns(ns):
        return _refused(RootLineageLimitation.FOREIGN_SCOPE)
    if not outer.unit():
        return _refused(RootLineageLimitation.WORK_UNITS_OVER_BOUND)
    problem = validate_root_region_lineage_state(
        state,
        effective,
        outer,
        history_bounds=ns.history_bounds,
        graph_bounds=ns.graph_bounds,
        proof_bounds=ns.proof_bounds,
        observation_bounds=ns.observation_bounds,
        workspace=ns.workspace,
    )
    if problem is not None:
        return _refused(problem)
    d_state = state.d_state
    return _region_selection_kernel(state, d_state, outer)

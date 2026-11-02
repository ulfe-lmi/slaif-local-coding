"""Inert current bundle admission derivation (objective 018-g).

ONE bounded pure public operation over the ACTUAL retained 018-d
causal history and its ACTUAL namespace: it derives the accepted
018-f current graph (internally, through the private same-run seam)
AND the current admission entries with the canonical 018-c semantic
keys, the exact retained source/provenance and the complete reverse
member index.  Stale, conflicting and ambiguous groups — and
unproven root-owned opaque regions — are excluded BEFORE entry
planning or copying.

The derivation is INERT: it creates no compiler object, no cache
entry and no runtime/session ownership; it never activates the
legacy profile; the EXACT input state is preserved on every outcome.

Resource law (one charged operation):

* ONE G outer work ledger (the NEW
  ``CurrentAdmissionBounds.max_total_work_units`` ceiling) spans the
  ENTIRE derivation — history validation, 018-e currentness, 018-f
  graph, admission planning, source/key construction, interning,
  witness/origin/index and output work — every unit charged BEFORE
  the crossing operation;
* the ACTUAL supplied 018-f ``CurrentGraphBounds.max_total_work_units``
  ceiling counts ONLY the F-subtree visits (each actual F visit
  charges the G outer once as well); it stops binding once the F
  phase returns — G admission/output work is never charged to the F
  domain and no per-group/pass reset occurs;
* admission planning/output runs on its OWN stage ledger (the ACTUAL
  inherited ``GraphBounds.max_work_units``, a distinct domain from F
  graph work);
* newly owned entry-source UTF-8 bytes are counted once per DISTINCT
  interned semantic entry (root included) against the NEW cumulative
  ceiling, with the per-entry cap the ACTUAL inherited
  ``GraphBounds.max_single_source_bytes`` preflighted BEFORE any walk
  or copy;
* the ACTUAL inherited admission caps (entries / member occurrences /
  reverse associations) keep their admission-output domains, with
  association attempts charged BEFORE dedup;
* NEW admission diagnostics (at most ONE fixed
  ``candidate_unproven`` per derivation) run under the NEW
  ``max_diagnostics`` admission domain AND the ACTUAL inherited
  admission diagnostics ceiling in the SAME domain; the actual
  bounded sorted/deduplicated reason tuple is RETAINED in the NEW
  overlay (``admission_reasons``) with ``emitted_admission_reasons``
  bound to its length; 018-f graph diagnostics stay F output by
  reference.
"""

from __future__ import annotations

import hashlib
from collections.abc import Sequence

from pydantic import ValidationError

from . import current_graph as _current_graph
from . import currentness as _currentness
from .bundle_admission import _key_canonical, _segment_all_eligible
from .bundle_admission_models import (
    AdmissionMode,
    BoundaryClass,
    BundleAdmissionNamespace,
    BundleKeyRecord,
    EntryClass,
    MemberClass,
    OwnershipGroup,
)
from .bundle_proof_models import ROOT_FILENAME, BundleProof
from .causal_history_models import (
    CausalHistoryNamespace,
    CausalHistoryState,
    RootAnchor,
)
from .current_admission_models import (
    CURRENT_ADMISSION_CONTRACT_VERSION,
    CURRENT_ADMISSION_POLICY_VERSION,
    CurrentAdmission,
    CurrentAdmissionBounds,
    CurrentAdmissionEntry,
    CurrentAdmissionLimitation,
    CurrentAdmissionOutcome,
    CurrentAdmissionPathAssociation,
    CurrentAdmissionResult,
    CurrentAdmissionWitness,
    RetainedRootProvenance,
    current_admission_scope_key,
)
from .current_graph_models import (
    CurrentGraphBounds,
    CurrentGraphLimitation,
    CurrentGraphOutcome,
    CurrentGraphResult,
)
from .currentness_models import (
    CURRENTNESS_CONTRACT_VERSION,
    OPAQUE_GROUP_RECIPE_VERSION,
    CurrentnessBounds,
    CurrentnessGroupRecord,
    CurrentnessStatus,
)


class _GOverflow(Exception):
    """A current-admission owned domain (outer or admission stage)
    crossed — a fixed whole-result refusal, never a private escape."""

    __slots__ = ("limitation",)

    def __init__(self, limitation: CurrentAdmissionLimitation) -> None:
        self.limitation = limitation
        super().__init__(limitation.value)


class _GOuter(_current_graph._OuterLedger):
    """ONE chained OUTER ledger over the ENTIRE 018-g derivation.

    The NEW G total ceiling (``work_cap``) is charged by EVERY unit
    of the whole operation.  The ACTUAL supplied 018-f total-work
    ceiling (``f_work_cap``) counts ONLY the F-subtree visits: while
    the explicit F phase (``begin_f``/``end_f`` around the single
    ``_derive_graph`` call) is active, every unit additionally
    charges the distinct ``f_work_spent`` counter and a crossing F
    subtree refuses even when the G total still has headroom; after
    the F phase returns the F cap is no longer enforced and G
    admission/output work charges the G total only.  Both crossings
    carry the ONE shared-outer fixed name.  ``diag()`` is the F-
    domain graph-diagnostic counter (the ACTUAL supplied F
    ``max_diagnostics``); ``adiam()`` is the NEW G admission-
    diagnostic counter (the NEW ``max_diagnostics``).
    """

    __slots__ = ("f_work_cap", "f_work_spent", "g_diag_cap", "g_diag_spent", "_f_phase")

    def __init__(self, f_bounds: CurrentGraphBounds, g_bounds: CurrentAdmissionBounds) -> None:
        super().__init__(f_bounds)
        # The inherited work_cap/diag_cap are rebound to their G-
        # owned domains: work_cap is the NEW G TOTAL ceiling, diag_cap
        # stays the ACTUAL supplied F graph-diagnostic ceiling.
        self.work_cap = g_bounds.max_total_work_units
        self.f_work_cap = f_bounds.max_total_work_units
        self.f_work_spent = 0
        self.g_diag_cap = g_bounds.max_diagnostics
        self.g_diag_spent = 0
        self._f_phase = False

    def begin_f(self) -> None:
        """Enter the F-subtree phase (its ceiling binds here)."""
        self._f_phase = True

    def end_f(self) -> None:
        """Leave the F-subtree phase (its ceiling no longer binds)."""
        self._f_phase = False

    def unit(self) -> bool:
        if self._f_phase and self.f_work_spent + 1 > self.f_work_cap:
            raise _GOverflow(CurrentAdmissionLimitation.TOTAL_WORK_UNITS_OVER_BOUND)
        if self.work_spent + 1 > self.work_cap:
            raise _GOverflow(CurrentAdmissionLimitation.TOTAL_WORK_UNITS_OVER_BOUND)
        if self._f_phase:
            self.f_work_spent += 1
        self.work_spent += 1
        return True

    def diag(self) -> None:
        if self.diag_spent + 1 > self.diag_cap:
            raise _GOverflow(CurrentAdmissionLimitation.DIAGNOSTICS_FULL)
        self.diag_spent += 1

    def adiam(self) -> None:
        if self.g_diag_spent + 1 > self.g_diag_cap:
            raise _GOverflow(CurrentAdmissionLimitation.ADMISSION_DIAGNOSTICS_FULL)
        self.g_diag_spent += 1


class _GStage(_current_graph._StageLedger):
    """The ADMISSION planning/output stage domain: the ACTUAL
    inherited ``GraphBounds.max_work_units``, a distinct counter
    from the F graph stage (same cap value, different domain, a
    different fixed refusal name)."""

    __slots__ = ()

    def unit(self) -> None:
        if self.work_spent + 1 > self.bounds.max_work_units:
            raise _GOverflow(CurrentAdmissionLimitation.ADMISSION_WORK_UNITS_EXHAUSTED)
        self.work_spent += 1


#: Exact 1:1 value mapping from the 018-f closed limitation names to
#: the propagated 018-g names (same strings, distinct enum).
_GRAPH_LIMITATION_MAP = {
    limitation: CurrentAdmissionLimitation(limitation.value)
    for limitation in CurrentGraphLimitation
}


def _sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _refuse(
    state: CausalHistoryState,
    outcome: CurrentAdmissionOutcome,
    diagnostics: tuple[CurrentAdmissionLimitation, ...],
) -> CurrentAdmissionResult:
    return CurrentAdmissionResult(
        outcome=outcome, state=state, overlay=None, diagnostics=diagnostics
    )


def _refuse_from_graph(
    state: CausalHistoryState, graph_result: CurrentGraphResult
) -> CurrentAdmissionResult:
    """The fixed upstream refusal mapping (exact F names, 1:1)."""
    mapped = tuple(_GRAPH_LIMITATION_MAP[name] for name in graph_result.diagnostics)
    outcome = CurrentAdmissionOutcome(graph_result.outcome.value)
    return _refuse(state, outcome, mapped)


def derive_current_admission(
    state: CausalHistoryState,
    ns: CausalHistoryNamespace,
    bounds: CurrentAdmissionBounds | None = None,
    currentness_bounds: CurrentnessBounds | None = None,
    graph_bounds: CurrentGraphBounds | None = None,
) -> CurrentAdmissionResult:
    """The ONE bounded pure current-admission derivation (018-g).

    Takes the ACTUAL 018-d state, its ACTUAL namespace, explicit NEW
    current-admission bounds (defaults when omitted) and the ACTUAL
    supplied 018-e/018-f derivation bounds.  The input is the
    INTERNAL retained-history boundary, never a public supplied
    proof/snapshot/header authority: object construction is not
    authentication, and no caller-supplied overlay/graph/current
    flag establishes anything.  Foreign scope, unsupported coherent
    versions, malformed state, no root and every resource crossing
    give a fixed whole-result typed refusal with the EXACT input
    state and NO partial entries/index/graph; the early fences are
    O(1) in the historical state and every later inspection/copy is
    charged BEFORE the operation.
    """
    # --- Early O(1) fences (no scan/copy of the historical state) ---
    if state.history_key != ns.history_key:
        return _refuse(
            state,
            CurrentAdmissionOutcome.REFUSED_FOREIGN_SCOPE,
            (CurrentAdmissionLimitation.FOREIGN_SCOPE,),
        )
    if not _currentness._revalidate_ns(ns):
        return _refuse(
            state,
            CurrentAdmissionOutcome.REFUSED_VERSION_CONFLICT,
            (CurrentAdmissionLimitation.VERSION_UNSUPPORTED,),
        )
    try:
        effective_bounds = CurrentAdmissionBounds.model_validate(
            CurrentAdmissionBounds().model_dump(warnings=False)
            if bounds is None
            else bounds.model_dump(warnings=False)
        )
    except Exception:
        raise ValueError(
            "current admission bounds failed the actual current-admission validation"
        ) from None
    try:
        effective_graph_bounds = CurrentGraphBounds.model_validate(
            CurrentGraphBounds().model_dump(warnings=False)
            if graph_bounds is None
            else graph_bounds.model_dump(warnings=False)
        )
    except Exception:
        raise ValueError(
            "current graph bounds failed the actual current-graph validation"
        ) from None

    outer = _GOuter(effective_graph_bounds, effective_bounds)
    stage_f = _current_graph._StageLedger(ns.graph_bounds)
    stage_g = _GStage(ns.graph_bounds)
    try:
        return _derive_admission(
            state,
            ns,
            effective_bounds,
            currentness_bounds,
            effective_graph_bounds,
            outer,
            stage_f,
            stage_g,
        )
    except _GOverflow as overflow:
        return _refuse(state, CurrentAdmissionOutcome.REFUSED_OVER_BOUND, (overflow.limitation,))
    except _current_graph._StageOverflow as overflow:
        return _refuse(
            state,
            CurrentAdmissionOutcome.REFUSED_OVER_BOUND,
            (_GRAPH_LIMITATION_MAP[overflow.limitation],),
        )
    except _current_graph._Malformed as malformed:
        return _refuse(
            state,
            CurrentAdmissionOutcome.REFUSED_STATE_MALFORMED,
            (_GRAPH_LIMITATION_MAP[malformed.limitation],),
        )


def _derive_admission(
    state: CausalHistoryState,
    ns: CausalHistoryNamespace,
    g_bounds: CurrentAdmissionBounds,
    currentness_bounds: CurrentnessBounds | None,
    f_bounds: CurrentGraphBounds,
    outer: _GOuter,
    stage_f: _current_graph._StageLedger,
    stage_g: _GStage,
) -> CurrentAdmissionResult:
    # --- ACTUAL F current graph + SAME-run E overlay (charged) ------
    #
    # The F phase charges BOTH ledgers on every F unit (the G total
    # and the F subtree ceiling); once the call returns, only the G
    # total keeps binding.
    outer.begin_f()
    try:
        graph_result, overlay = _current_graph._derive_graph(
            state, ns, f_bounds, currentness_bounds, outer, stage_f
        )
    finally:
        outer.end_f()
    if graph_result.outcome is not CurrentGraphOutcome.OK:
        return _refuse_from_graph(state, graph_result)
    assert overlay is not None  # ok carries its overlay (model law)
    graph = graph_result.overlay
    assert graph is not None

    anchor = state.root
    assert anchor is not None  # F refused no-root before reaching here

    root_digest = anchor.root_digest

    # --- ACTUAL 018-c admission namespace (coherent reconstruction) -
    #
    # The ns already binds the admission fields AND both 64-hex
    # scope keys; constructing the actual 018-c namespace model
    # re-derives both keys from the actual fields, so an incoherent
    # scope is a fixed foreign-scope refusal, never a silent pass.
    outer.unit()
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
            CurrentAdmissionOutcome.REFUSED_FOREIGN_SCOPE,
            (CurrentAdmissionLimitation.FOREIGN_SCOPE,),
        )

    # --- Eligibility: every F node is root-reachable (root depth 0) -
    eligible: dict[str, int] = {}
    for node in graph.nodes:
        outer.unit()
        stage_g.unit()
        eligible[node.path] = node.depth

    # --- ACTUAL SAME-run E owned groups per occurrence --------------
    groups_by_occ: dict[str, list[CurrentnessGroupRecord]] = {}
    for group in overlay.groups:
        outer.unit()
        stage_g.unit()
        groups_by_occ.setdefault(group.occurrence_id, []).append(group)

    # --- Charged assembly region: a malformed retained proof, anchor or
    # model selection fails CLOSED with the fixed state-malformed refusal,
    # never an uncaught Pydantic/attribute exception.  Ledger overflows
    # and upstream _Malformed signals propagate untouched.
    try:
        # --- The required root entry (the anchor is the only supplier) --
        outer.units(2)
        stage_g.units(2)  # the ONE workspace byte-length measurement
        workspace_bytes = len(ns.workspace.encode("utf-8"))
        if anchor.source_byte_length > ns.graph_bounds.max_single_source_bytes:
            raise _GOverflow(CurrentAdmissionLimitation.ENTRY_SOURCE_BYTES_OVER_BOUND)
        if anchor.source_byte_length > g_bounds.max_total_entry_source_bytes:
            raise _GOverflow(CurrentAdmissionLimitation.TOTAL_ENTRY_SOURCE_BYTES_OVER_BOUND)
        root_entry = _build_root_entry(admission_ns, ns, anchor, outer, stage_g, workspace_bytes)
        total_entry_bytes = anchor.source_byte_length

        # --- Reverse-index association (attempts charged BEFORE dedup) --
        path_keys: dict[str, set[str]] = {}
        attempts = 0

        def _associate(path: str, key: str) -> None:
            nonlocal attempts
            outer.unit()
            stage_g.unit()
            if attempts + 1 > ns.bounds.max_reverse_associations:
                raise _GOverflow(CurrentAdmissionLimitation.REVERSE_ASSOCIATIONS_OVER_BOUND)
            attempts += 1
            path_keys.setdefault(path, set()).add(key)

        _associate(ROOT_FILENAME, root_entry.content_key)
        entries: dict[str, CurrentAdmissionEntry] = {}
        member_occ_charged = 1  # the required root member occurrence
        unproven = False

        for occurrence in state.occurrences:
            outer.unit()
            stage_g.unit()  # the proof plan visit
            proof = occurrence.proof
            groups = groups_by_occ.get(occurrence.occurrence_id)
            if groups is None:
                raise _current_graph._Malformed(CurrentGraphLimitation.STATE_MALFORMED)

            whole_ok = True
            root_owned_opaque = False
            for group in groups:
                outer.unit()
                stage_g.unit()  # the group currentness/ownership inspection
                if group.group_status not in (
                    CurrentnessStatus.CURRENT_KNOWN,
                    CurrentnessStatus.CURRENT_OPAQUE,
                ):
                    whole_ok = False
                outer.units(len(group.members))
                stage_g.units(len(group.members))  # the root-membership walk
                if (
                    group.boundary_class is BoundaryClass.BOUNDARYLESS
                    and ROOT_FILENAME in group.members
                ):
                    root_owned_opaque = True

            member_flags: list[bool] = []
            for member in proof.requested_members:
                outer.unit()
                stage_g.unit()  # the member eligibility inspection
                member_flags.append(member.normalized is not None and member.normalized in eligible)

            plans = _currentness_plans(
                proof,
                ns.mode,
                eligible,
                groups,
                whole_ok,
                root_owned_opaque,
                member_flags,
                outer,
                stage_g,
            )

            admitted_any = False
            for plan in plans:
                admitted, classes, aggregate, content_key, key_record = _entry_descriptor(
                    admission_ns, root_digest, proof, plan, eligible, outer, stage_g
                )
                for occurrence_path in key_record.member_occurrences:
                    _associate(occurrence_path, content_key)
                outer.unit()
                stage_g.unit()  # the interning lookup/identity
                existing = entries.get(content_key)
                plan_len = len(plan)
                outer.units(1 + 2 * plan_len)
                stage_g.units(1 + 2 * plan_len)
                # 1 witness construction + the two LINEAR segment-index
                # passes (nonnegativity, strict-increasing adjacency)
                witness = CurrentAdmissionWitness(
                    occurrence_id=occurrence.occurrence_id,
                    request_index=proof.request_index,
                    call_position=proof.call_position,
                    result_position=proof.result_position,
                    segment_indices=plan,
                )
                if existing is not None:
                    # Known duplicate key: charged witness retention, NO
                    # new source ownership (the distinct key already
                    # counted its source bytes once).
                    merged = _merge_witnesses(existing, witness, outer, stage_g)
                    entries[content_key] = existing.model_copy(update={"witnesses": merged})
                else:
                    region_bytes = 0
                    region_chars = 0
                    for position in plan:
                        outer.unit()
                        stage_g.unit()  # the proven byte/char fact walk
                        segment = proof.segments[position]
                        region_bytes += segment.byte_length
                        region_chars += segment.char_length
                    segments_of_proof = len(proof.segments)
                    member_occ = len(key_record.member_occurrences)
                    if region_bytes > ns.graph_bounds.max_single_source_bytes:
                        raise _GOverflow(CurrentAdmissionLimitation.ENTRY_SOURCE_BYTES_OVER_BOUND)
                    if total_entry_bytes + region_bytes > g_bounds.max_total_entry_source_bytes:
                        raise _GOverflow(
                            CurrentAdmissionLimitation.TOTAL_ENTRY_SOURCE_BYTES_OVER_BOUND
                        )
                    if 1 + len(entries) + 1 > ns.bounds.max_entries:
                        raise _GOverflow(CurrentAdmissionLimitation.ENTRIES_OVER_BOUND)
                    member_count = len(key_record.member_occurrences)
                    if member_occ_charged + member_count > ns.bounds.max_member_occurrences:
                        raise _GOverflow(CurrentAdmissionLimitation.MEMBER_OCCURRENSES_OVER_BOUND)
                    _charge_entry_model(
                        outer,
                        stage_g,
                        segments_of_proof,
                        plan_len,
                        member_occ,
                        len(key_record.ownership_groups),
                        region_chars,
                        region_bytes,
                        workspace_bytes,
                    )
                    entry = CurrentAdmissionEntry(
                        entry_class=EntryClass.FILE_BUNDLE_ENTRY,
                        content_key=content_key,
                        key_record=key_record,
                        width=len(set(admitted)),
                        member_classes=classes,
                        root_digest=root_digest,
                        proof=proof,
                        admitted_segments=plan,
                        witnesses=(witness,),
                    )
                    entries[content_key] = entry
                    total_entry_bytes += region_bytes
                    member_occ_charged += member_count
                admitted_any = True
            if not admitted_any:
                unproven = True

        diagnostics: tuple[CurrentAdmissionLimitation, ...] = ()
        if unproven:
            outer.adiam()
            diagnostics = (CurrentAdmissionLimitation.CANDIDATE_UNPROVEN,)

        # --- Reverse-index rows (NEW G-owned typed rows, charged) -------
        path_associations: list[CurrentAdmissionPathAssociation] = []
        for path, keys in _current_graph._sorted(
            path_keys.items(), lambda item: item[0], outer, stage_g
        ):
            outer.units(1 + 2 * len(keys))
            stage_g.units(1 + 2 * len(keys))
            # 1 row construction + the content-key validator walk (k hex
            # checks + k set insertions) + path/scoped/root-flag checks
            path_associations.append(
                CurrentAdmissionPathAssociation(
                    scoped_key=admission_ns.scoped_key,
                    path=path,
                    content_keys=tuple(_current_graph._sorted(keys, None, outer, stage_g)),
                    is_root=path == ROOT_FILENAME,
                )
            )

        outer.units(len(path_associations))
        stage_g.units(len(path_associations))  # the association list-to-tuple copy
        associations = tuple(path_associations)

        # --- Interned file entries, sorted by distinct content key ------
        sorted_keys = _current_graph._sorted(entries, None, outer, stage_g)
        outer.units(len(sorted_keys))
        stage_g.units(len(sorted_keys))  # the interned entry reference copies
        file_entries = tuple(entries[key] for key in sorted_keys)

        outer.units(18)
        stage_g.units(18)
        # the derivation scope key: 7 bound model_dumps + 7 json encodes +
        # 1 payload list + 1 outer json + 1 encode + 1 sha256
        scope_key = current_admission_scope_key(
            state.history_key,
            ns.workspace,
            root_digest,
            CURRENT_ADMISSION_CONTRACT_VERSION,
            CURRENT_ADMISSION_POLICY_VERSION,
            ns.admission_version,
            ns.observation_version,
            ns.graph_version,
            ns.reference_version,
            ns.proof_version,
            ns.history_version,
            ns.arguments_version,
            CURRENTNESS_CONTRACT_VERSION,
            overlay.policy_version,
            OPAQUE_GROUP_RECIPE_VERSION,
            graph.contract_version,
            graph.policy_version,
            overlay.scope_key,
            graph.scope_key,
            ns.admission_namespace_key,
            ns.admission_scoped_key,
            g_bounds,
            overlay.bounds,
            f_bounds,
            ns.bounds,
            ns.proof_bounds,
            ns.graph_bounds,
            ns.observation_bounds,
        )

        association_key_count = sum(len(keys) for keys in path_keys.values())
        output_units = (
            19
            + 3 * len(file_entries)
            + 3 * len(associations)
            + association_key_count
            + member_occ_charged
            + 2
            + len(diagnostics)
        )
        outer.units(output_units)
        stage_g.units(output_units)
        # the CurrentAdmission model-validation walk: 1 construction +
        # root binding + 18 scope-key recompute + n keys list + n
        # adjacency walk + n root-membership + (n + 1) entry visits + R
        # rows dict + R row-flag walk + R key-set objects + A key-set
        # insertions + M O(1) reverse-index member lookups + 1
        # admission_reasons sorted/dedup walk + 1 reason count/cap
        # binding (+ r reason visits, r = len(admission_reasons))
        admission = CurrentAdmission(
            history_key=state.history_key,
            revision=state.revision,
            workspace=ns.workspace,
            root_path=ROOT_FILENAME,
            root_digest=root_digest,
            admission_version=ns.admission_version,
            observation_version=ns.observation_version,
            graph_version=ns.graph_version,
            reference_version=ns.reference_version,
            proof_version=ns.proof_version,
            history_version=ns.history_version,
            arguments_version=ns.arguments_version,
            currentness_contract_version=CURRENTNESS_CONTRACT_VERSION,
            currentness_policy_version=overlay.policy_version,
            currentness_recipe_version=OPAQUE_GROUP_RECIPE_VERSION,
            graph_contract_version=graph.contract_version,
            graph_policy_version=graph.policy_version,
            contract_version=CURRENT_ADMISSION_CONTRACT_VERSION,
            policy_version=CURRENT_ADMISSION_POLICY_VERSION,
            bounds=g_bounds,
            currentness_bounds=overlay.bounds,
            graph_bounds=f_bounds,
            admission_bounds=ns.bounds,
            proof_bounds=ns.proof_bounds,
            inherited_graph_bounds=ns.graph_bounds,
            observation_bounds=ns.observation_bounds,
            currentness_scope_key=overlay.scope_key,
            graph_scope_key=graph.scope_key,
            admission_namespace_key=ns.admission_namespace_key,
            admission_scoped_key=ns.admission_scoped_key,
            scope_key=scope_key,
            root_entry=root_entry,
            entries=file_entries,
            path_associations=associations,
            graph=graph,
            work_units=outer.work_spent,
            entry_source_bytes=total_entry_bytes,
            entries_retained=1 + len(file_entries),
            member_occurrences_charged=member_occ_charged,
            reverse_association_attempts=attempts,
            emitted_admission_reasons=len(diagnostics),
            admission_reasons=diagnostics,
        )
        return CurrentAdmissionResult(
            outcome=CurrentAdmissionOutcome.OK, state=state, overlay=admission, diagnostics=()
        )

    except (ValidationError, ValueError, TypeError, KeyError, IndexError, AttributeError):
        return _refuse(
            state,
            CurrentAdmissionOutcome.REFUSED_STATE_MALFORMED,
            (CurrentAdmissionLimitation.STATE_MALFORMED,),
        )


def _currentness_plans(
    proof: BundleProof,
    mode: AdmissionMode,
    eligible: dict[str, int],
    groups: Sequence[CurrentnessGroupRecord],
    whole_ok: bool,
    root_owned_opaque: bool,
    member_flags: Sequence[bool],
    outer: _GOuter,
    stage_g: _GStage,
) -> tuple[tuple[int, ...], ...]:
    """The current-admission truth table (the exact original rows,
    filtered by the ACTUAL per-owned-group currentness and the
    unproven-root-bytes exclusion).

    * whole admissible (ALL owned groups current and compatible, and
      NO root-owned boundaryless group whose unattributed root bytes
      RootAnchor compatibility can never be proven): all members
      independently eligible -> the complete whole bundle in BOTH
      modes; mixed eligible/background -> greedy admits the whole iff
      at least one is independently eligible, lean admits each
      independently proven all-eligible segment as its own contiguous
      entry (never the whole PLUS isolated rows together);
    * whole NOT admissible: whole admission is impossible in BOTH
      modes; lean admits each independently CURRENT all-eligible
      group that is not a root-owned opaque region as its own single-
      segment entry; greedy gains NO new isolated-region rule;
    * zero independently eligible members: neither mode admits.
    """
    segments = proof.segments
    n_segments = len(segments)
    n_members = len(member_flags)
    # The whole-tuple construction copies n elements (charged before).
    outer.units(n_segments)
    stage_g.units(n_segments)
    whole = tuple(range(n_segments))
    if whole_ok and not root_owned_opaque:
        # all(): a linear walk (may short-circuit) charged before.
        outer.units(n_members)
        stage_g.units(n_members)
        if all(member_flags):
            outer.unit()
            stage_g.unit()  # the single-plan tuple construction
            return (whole,)
        # any(): a second linear walk charged before.
        outer.units(n_members)
        stage_g.units(n_members)
        if any(member_flags) and mode is AdmissionMode.GREEDY:
            outer.unit()
            stage_g.unit()  # the single-plan tuple construction
            return (whole,)
        if mode is AdmissionMode.LEAN:
            # whole_ok and no root-owned opaque group in this proof:
            # every all-eligible segment row is a current all-
            # eligible group (the exact 018-c lean isolated row).
            # Every segment visit and its all-eligibility member walk
            # is charged BEFORE the operation.
            rows: list[tuple[int, ...]] = []
            for position, segment in enumerate(segments):
                outer.unit()
                stage_g.unit()  # the segment plan visit
                outer.units(len(segment.member_positions))
                stage_g.units(len(segment.member_positions))
                if _segment_all_eligible(proof, segment, eligible):
                    outer.unit()
                    stage_g.unit()  # the single-index row tuple construction
                    rows.append((position,))
            outer.units(len(rows))
            stage_g.units(len(rows))  # the plan tuple element copies
            return tuple(rows)
        outer.unit()
        stage_g.unit()  # the empty-plan construction
        return ()
    if mode is AdmissionMode.LEAN:
        rows = []
        for group in groups:
            outer.unit()
            stage_g.unit()  # the group plan visit
            if group.group_status not in (
                CurrentnessStatus.CURRENT_KNOWN,
                CurrentnessStatus.CURRENT_OPAQUE,
            ):
                continue
            outer.units(len(group.members))
            stage_g.units(len(group.members))  # the root-membership walk
            if (
                group.boundary_class is BoundaryClass.BOUNDARYLESS
                and ROOT_FILENAME in group.members
            ):
                continue
            segment = segments[group.group_index]
            outer.units(len(segment.member_positions))
            stage_g.units(len(segment.member_positions))  # the all-eligible walk
            if _segment_all_eligible(proof, segment, eligible):
                outer.unit()
                stage_g.unit()  # the single-index row tuple construction
                rows.append((group.group_index,))
        outer.units(len(rows))
        stage_g.units(len(rows))  # the plan tuple element copies
        return tuple(rows)
    outer.unit()
    stage_g.unit()  # the empty-plan construction
    return ()


def _entry_descriptor(
    admission_ns: BundleAdmissionNamespace,
    root_digest: str,
    proof: BundleProof,
    plan: tuple[int, ...],
    eligible: dict[str, int],
    outer: _GOuter,
    stage_g: _GStage,
) -> tuple[tuple[str, ...], tuple[MemberClass, ...], str, str, BundleKeyRecord]:
    """The 018-c canonical descriptor and key for one admitted plan
    (NO source materialization).

    Mirrors the accepted 018-c ``_file_entry`` descriptor law exactly
    (ordered admitted member occurrences, the per-occurrence
    ELIGIBLE/GREEDY_BACKGROUND authority vector, the entry-local
    ownership partition with PROVEN/BOUNDARYLESS classes and REUSED
    proven digests, the exact aggregate digest) and stops BEFORE the
    source-owning entry materialization: ``_key_canonical`` and the
    key record re-derive everything from fields only, so no admitted
    source slice/join/encode/hash happens here.
    """
    segments = proof.segments
    outer.units(len(plan))
    stage_g.units(len(plan))  # the admitted-set copy before descriptor work
    admitted_set = set(plan)
    admitted: list[str] = []
    classes: list[MemberClass] = []
    groups: list[OwnershipGroup] = []
    entry_local = 0
    for position, segment in enumerate(segments):
        outer.unit()
        stage_g.unit()  # the segment descriptor visit (admitted or skipped)
        if position not in admitted_set:
            continue
        start = entry_local
        for member_position in segment.member_positions:
            outer.unit()
            stage_g.unit()  # the member descriptor/class walk
            member = proof.requested_members[member_position]
            if member.normalized is None:
                raise _current_graph._Malformed(CurrentGraphLimitation.STATE_MALFORMED)
            admitted.append(member.normalized)
            classes.append(
                MemberClass.ELIGIBLE
                if member.normalized in eligible
                else MemberClass.GREEDY_BACKGROUND
            )
            entry_local += 1
        n_indices = entry_local - start
        outer.units(2 * n_indices)
        stage_g.units(2 * n_indices)  # the indices tuple construction + copy
        indices = tuple(range(start, entry_local))
        if len(segment.member_positions) == 1 and segment.member_digest is not None:
            outer.units(3 * len(indices) + 6)
            stage_g.units(3 * len(indices) + 6)
            # the _v_group pass: k set insertions + sorted(indices)
            # over the GENERATED strictly-increasing tuple (single
            # ascending run: k-1 comparisons + k copy) + the
            # proven/boundaryless checks + field validators
            groups.append(
                OwnershipGroup(
                    group_index=len(groups),
                    member_occurrence_indices=indices,
                    boundary_class=BoundaryClass.PROVEN,
                    group_digest=segment.member_digest,
                )
            )
        else:
            if len(indices) == 1:
                raise _current_graph._Malformed(CurrentGraphLimitation.STATE_MALFORMED)
            outer.units(3 * len(indices) + 6)
            stage_g.units(3 * len(indices) + 6)  # the same _v_group pass law
            groups.append(
                OwnershipGroup(
                    group_index=len(groups),
                    member_occurrence_indices=indices,
                    boundary_class=BoundaryClass.BOUNDARYLESS,
                    group_digest=segment.digest,
                )
            )
    # The admitted region digest is REUSED from the already-proven
    # 018-b facts (whole-bundle aggregate digest, or the single
    # admitted segment's own proven digest): no new owned copy, join
    # or digest recomputation over the source.
    if plan == tuple(range(len(segments))):
        aggregate = proof.source_digest
    else:
        aggregate = segments[plan[0]].digest
    outer.units(3 + 3 * len(admitted) + len(groups))
    stage_g.units(3 + 3 * len(admitted) + len(groups))
    # 1 dict setup + member_occurrences list copy + member_classes list
    # copy + per-group index list copies (member passes: 3m + g) +
    # 1 json/encode + 1 sha256
    canonical = _key_canonical(
        admission_ns,
        root_digest,
        EntryClass.FILE_BUNDLE_ENTRY,
        tuple(admitted),
        tuple(classes),
        aggregate,
        tuple(groups),
    )
    content_key = _sha256_hex(canonical)
    m_members = len(admitted)
    g_groups = len(groups)
    outer.units(28 + 12 * m_members + 8 * g_groups)
    stage_g.units(28 + 12 * m_members + 8 * g_groups)
    # 12 field-validator checks (identity/version/hex) + 4 nested
    # bounds model validations + the ownership tuple reference walk +
    # the seen-index walk (setup, g dense checks, m copies) +
    # sorted(seen) over the GENERATED strictly-increasing sequence
    # (single ascending run by construction: run-identification
    # comparisons plus one copy, no merge passes: 2m) + list(range)
    # construction/compare (2m) + set(seen) duplicate check (m) +
    # member_classes alignment (m) + the canonical re-derivation
    # (1 dict + 4 bounds dumps + 3m member/class/index copies + g
    # group descriptors + json + encode) + sha256 + content-key
    # compare (28 fixed + 9m + 2g, the increasing-run construction
    # invariant replacing any general sort bound) + the SECOND nested
    # group pass: the actual nested BundleKeyRecord validation reruns
    # every OwnershipGroup _v_group (set + single-run sorted + copy)
    # after the field validators (3m + 6g)
    key_record = BundleKeyRecord(
        mode=admission_ns.mode,
        authority_class=EntryClass.FILE_BUNDLE_ENTRY,
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
        member_occurrences=tuple(admitted),
        member_classes=tuple(classes),
        aggregate_source_digest=aggregate,
        ownership_groups=tuple(groups),
        content_key=content_key,
    )
    return tuple(admitted), tuple(classes), aggregate, content_key, key_record


def _build_root_entry(
    admission_ns: BundleAdmissionNamespace,
    ns: CausalHistoryNamespace,
    anchor: RootAnchor,
    outer: _GOuter,
    stage_g: _GStage,
    workspace_bytes: int,
) -> CurrentAdmissionEntry:
    """The required first-class root entry.

    The canonical ROOT_ENTRY key reuses the 018-c recipe byte-for-
    byte; the typed retained-root provenance mirrors the ACTUAL
    RootAnchor fields exactly (no RootEnvelopeOccurrence, no
    RootOccurrence and no transport envelope is fabricated); the
    exact EMPTY root is legal.
    """
    outer.units(9)
    stage_g.units(9)  # the _v_group pass for the single root group (3k+6)
    groups = (
        OwnershipGroup(
            group_index=0,
            member_occurrence_indices=(0,),
            boundary_class=BoundaryClass.PROVEN,
            group_digest=anchor.root_digest,
        ),
    )
    outer.units(3 + 3 * 1 + 1)
    stage_g.units(3 + 3 * 1 + 1)  # 1 dict + 3 member passes + 1 group + json + hash
    canonical = _key_canonical(
        admission_ns,
        anchor.root_digest,
        EntryClass.ROOT_ENTRY,
        (ROOT_FILENAME,),
        (MemberClass.ELIGIBLE,),
        anchor.root_digest,
        groups,
    )
    content_key = _sha256_hex(canonical)
    outer.units(28 + 12 * 1 + 8 * 1)
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
        root_digest=anchor.root_digest,
        reference_version=admission_ns.reference_version,
        admission_bounds=admission_ns.bounds,
        proof_bounds=admission_ns.proof_bounds,
        graph_bounds=admission_ns.graph_bounds,
        observation_bounds=admission_ns.observation_bounds,
        member_occurrences=(ROOT_FILENAME,),
        member_classes=(MemberClass.ELIGIBLE,),
        aggregate_source_digest=anchor.root_digest,
        ownership_groups=groups,
        content_key=content_key,
    )
    _charge_entry_model(
        outer,
        stage_g,
        0,
        0,
        1,
        1,
        len(anchor.root_text),
        anchor.source_byte_length,
        workspace_bytes,
    )
    return CurrentAdmissionEntry(
        entry_class=EntryClass.ROOT_ENTRY,
        content_key=content_key,
        key_record=key_record,
        width=1,
        member_classes=(MemberClass.ELIGIBLE,),
        root_digest=anchor.root_digest,
        root_text=anchor.root_text,
        root_source_byte_length=anchor.source_byte_length,
        root_provenance=RetainedRootProvenance(
            first_request_index=anchor.first_request_index,
            location=anchor.location,
            content_span=anchor.content_span,
            envelope_span=anchor.envelope_span,
            source_byte_length=anchor.source_byte_length,
            root_digest=anchor.root_digest,
            workspace=ns.workspace,
        ),
        witnesses=(),
    )


def _charge_entry_model(
    outer: _GOuter,
    stage_g: _GStage,
    n_segments: int,
    p_admitted: int,
    m_admitted: int,
    g_groups: int,
    region_chars: int,
    region_bytes: int,
    workspace_bytes: int,
) -> None:
    """Reserve the ACTUAL entry model-validation metadata work on
    BOTH ledgers BEFORE the construction that triggers it:

    * fixed 95: 10 entry setup, authority/alignment checks and the
      witness-field linear coordinate walk; 60 the canonical-entry
      re-derivation of the ADMISSION NAMESPACE (one
      _canonical_namespace_fields pass: 4 bounds dumps + 4 inner
      json + list + outer json + encode, two sha256 and the scoped
      concat, 13 field-validator checks, the 4 nested bounds model
      validations, and _v_bound_integrity's second canonical pass +
      2 sha256 + 2 compares); 9 the _key_canonical fixed pass (dict,
      4 bounds dumps, json, encode, sha256) plus the key compare;
      16 the class-specific checks (root encode/hash setup and
      provenance bindings, or the file-entry region digest/width
      checks);
    * 9 * m_admitted: the re-derivation 3m member/class/index list
      copies plus the admitted member walk (lookup, check, append)
      and the occurrence-tuple rebuild, compare and width set;
    * g_groups: the re-derivation ownership-group descriptors;
    * 2 * n_segments: the validator walks EVERY original proof
      segment (skipped/stale metadata included) for the offset
      arithmetic, plus the worst-case whole-bundle range tuple
      construction;
    * 2 * p_admitted: the linear adjacency check over the admitted
      indices plus the ONE built admitted-index set insertions;
    * 2 * region_chars + 2 * region_bytes: the admitted region
      slice + join (char passes) plus the UTF-8 encode + digest
      (byte passes; a root entry pays the same law over its
      retained root text; an EMPTY region still performs the fixed
      encode/hash covered by the fixed units);
    * 2 * workspace_bytes: the workspace canonical encode walks in
      the namespace field validator and the bound-integrity
      re-canonical pass.

    No stale SOURCE inspection happens in the model: the bounded
    metadata walk is separate and fully reserved here.  The linear
    admitted-index membership keeps a whole N-segment entry
    LINEAR, not quadratic, in the proof length."""
    units = (
        95
        + 9 * m_admitted
        + g_groups
        + 2 * n_segments
        + 2 * p_admitted
        + 2 * region_chars
        + 2 * region_bytes
        + 2 * workspace_bytes
    )
    outer.units(units)
    stage_g.units(units)


def _merge_witnesses(
    existing: CurrentAdmissionEntry,
    witness: CurrentAdmissionWitness,
    outer: _GOuter,
    stage_g: _GStage,
) -> tuple[CurrentAdmissionWitness, ...]:
    """Charged witness retention for a KNOWN interned key.

    The dedup over the FULL coordinate tuples (duplicates count
    before dedup) and the stable sort are ACTUAL collection work:
    a linear reservation (ONE construction unit + n membership units
    for the dedup walk over the input length + n working-copy units)
    is charged on BOTH ledgers BEFORE the operation, then the shared
    charged merge accounts every actual comparison and element
    write.  The first origin is never relabeled; distinct equal-
    byte incomparable witnesses are all retained.
    """
    # O(1) length FIRST; the linear reservation (ONE construction
    # unit + n dedup-walk units + n working-copy units over the INPUT
    # length) is charged on BOTH ledgers BEFORE any copy/iteration,
    # so an exhausted ledger refuses with zero pre-copy reads.
    n = len(existing.witnesses) + 1
    outer.units(1 + 2 * n)
    stage_g.units(1 + 2 * n)
    values = [*existing.witnesses, witness]
    unique: dict[tuple[str, int, int, int, tuple[int, ...]], CurrentAdmissionWitness] = {}
    for value in values:
        outer.units(2)
        stage_g.units(2)  # the 5-tuple coordinate construction + dict op
        coord = (
            value.occurrence_id,
            value.request_index,
            value.call_position,
            value.result_position,
            value.segment_indices,
        )
        unique.setdefault(coord, value)
    outer.units(4 * len(unique))
    stage_g.units(4 * len(unique))
    # the charged sort's one-shot 5-field key extraction (4 extra
    # element copies beyond the shared helper's own 1 + n reservation)
    ordered = _current_graph._sorted(
        unique.values(),
        lambda w: (
            w.occurrence_id,
            w.request_index,
            w.call_position,
            w.result_position,
            w.segment_indices,
        ),
        outer,
        stage_g,
    )
    outer.units(len(ordered))
    stage_g.units(len(ordered))  # the FINAL witness tuple output copy
    return tuple(ordered)

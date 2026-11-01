"""Pure nonroot currentness and overlap overlay derivation
(objective 018-e, slice e; INERT).

``derive_currentness_overlay(state, ns, bounds=None)`` is the ONE
documented pure derivation: over the ACTUAL accepted 018-d
``CausalHistoryState`` and its actual namespace it determines which
NONROOT source facts / ownership groups are current, stale or
ambiguous and indexes the overlapping represented paths.

It does not select graph reachability/admission, compile, inject,
replace or own RAM services; it advances no revision; it never
mutates its input (the state and its verbatim retained proofs are
immutable); and no receipt arrival, revision, call ID, digest or
registration order is ever treated as chronology — only the actual
frozen 018-d parent evidence establishes temporal edges.  It is
pure and inert: no host IO, no RAM service/locks, no compiler, no
HTTP/SSE observer and no new metrics.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass

from .bundle_admission_models import (
    BoundaryClass,
    BundleAdmissionNamespace,
    _canonical_namespace_fields,
)
from .bundle_proof_models import BundleSegment
from .causal_history import _supported_version_pairs
from .causal_history_models import (
    CausalHistoryLimitation,
    CausalHistoryNamespace,
    CausalHistoryState,
    HistoryBounds,
    _canonical_history_fields,
    validate_causal_history_state,
)
from .client_paths import validate_workspace
from .currentness_models import (
    CURRENTNESS_POLICY_VERSION,
    CurrentnessBounds,
    CurrentnessGroupRecord,
    CurrentnessLimitation,
    CurrentnessOutcome,
    CurrentnessOverlay,
    CurrentnessPathRecord,
    CurrentnessReason,
    CurrentnessResult,
    CurrentnessStatus,
    GroupPathRow,
    currentness_scope_key,
    opaque_group_identity,
)


def _sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class _LedgerOverflow(Exception):
    """A derived bound was crossed before its operation.

    The crossed limitation is carried; the derivation refuses
    atomically with the EXACT prior state and no partial overlay.
    Resource exhaustion is never a content conflict.
    """

    def __init__(self, limitation: CurrentnessLimitation) -> None:
        super().__init__(limitation.value)
        self.limitation = limitation


class _CurrentnessLedger:
    """ONE shared charged ledger over the ENTIRE derivation.

    Every unit is charged BEFORE the crossing operation (a charge
    that would cross refuses immediately).  ``work`` is the shared
    derivation work ledger (state validation, occurrence/group/
    member inspection, causal parent-edge visits, emission units);
    the other counters are the distinct derived ceilings.
    """

    __slots__ = (
        "work_cap",
        "work_spent",
        "pair_cap",
        "pair_spent",
        "path_cap",
        "path_spent",
        "group_cap",
        "group_spent",
        "member_cap",
        "member_spent",
        "diag_cap",
        "diag_spent",
    )

    def __init__(self, bounds: CurrentnessBounds) -> None:
        self.work_cap = bounds.max_work_units
        self.work_spent = 0
        self.pair_cap = bounds.max_relation_pairs
        self.pair_spent = 0
        self.path_cap = bounds.max_paths
        self.path_spent = 0
        self.group_cap = bounds.max_groups
        self.group_spent = 0
        self.member_cap = bounds.max_witness_memberships
        self.member_spent = 0
        self.diag_cap = bounds.max_diagnostics
        self.diag_spent = 0

    def unit(self) -> bool:
        if self.work_spent + 1 > self.work_cap:
            raise _LedgerOverflow(CurrentnessLimitation.WORK_UNITS_OVER_BOUND)
        self.work_spent += 1
        return True

    def pair(self) -> None:
        if self.pair_spent + 1 > self.pair_cap:
            raise _LedgerOverflow(CurrentnessLimitation.RELATION_PAIRS_OVER_BOUND)
        self.pair_spent += 1

    def path(self) -> None:
        if self.path_spent + 1 > self.path_cap:
            raise _LedgerOverflow(CurrentnessLimitation.PATHS_OVER_BOUND)
        self.path_spent += 1

    def group(self) -> None:
        if self.group_spent + 1 > self.group_cap:
            raise _LedgerOverflow(CurrentnessLimitation.GROUPS_OVER_BOUND)
        self.group_spent += 1

    def membership(self) -> None:
        # One emitted association row; see
        # ``CurrentnessBounds.max_witness_memberships`` for the
        # exact unit formula.  Charged BEFORE the row is retained.
        if self.member_spent + 1 > self.member_cap:
            raise _LedgerOverflow(CurrentnessLimitation.WITNESS_MEMBERSHIPS_OVER_BOUND)
        self.member_spent += 1

    def diagnostic(self) -> None:
        if self.diag_spent + 1 > self.diag_cap:
            raise _LedgerOverflow(CurrentnessLimitation.DIAGNOSTICS_FULL)
        self.diag_spent += 1


@dataclass(frozen=True)
class _Claim:
    """One path claim: a retained completed occurrence's owned
    group/member position representing one normalized NONROOT path.

    Repeated operands keep one claim per occurrence position; the
    SAME occurrence can never order its own groups (no self-clock,
    no first/last picking).
    """

    occurrence_id: str
    group_index: int
    member_position: int
    path: str
    known_digest: str | None
    opaque_identity: str


class _RelationIndex:
    """Charged occurrence-relation index over the frozen 018-d
    parent evidence (ONE shared traversal for the whole
    derivation; repeated pair requests with fresh budgets never
    satisfy the shared-work law).

    Every PAIR ATTEMPT (duplicates included) charges one relation
    pair AND one shared work unit BEFORE the memoization lookup;
    every causal parent-edge visit during a closure walk and every
    closure construction charges one shared work unit; a completed
    closure is memoized per start node and reused (the reuse is a
    charged lookup, never a fresh walk).

    The stored value under the canonical sorted key is ALWAYS the
    relation of the lexicographically FIRST occurrence to the
    second: "before" means the first occurrence is OLDER.  A
    flipped query inverts the stored direction; chronology never
    depends on query order.
    """

    __slots__ = ("_ledger", "_parent_map", "_known", "_memo", "_pairs")

    _INVERSE = {
        "before": "after",
        "after": "before",
        "same": "same",
        "incomparable": "incomparable",
        "unknown": "unknown",
    }

    def __init__(
        self,
        parent_map: dict[str, list[str]],
        ledger: _CurrentnessLedger,
        known: set[str],
    ) -> None:
        self._ledger = ledger
        self._parent_map = parent_map
        self._known = known
        self._memo: dict[str, set[str]] = {}
        self._pairs: dict[tuple[str, str], str] = {}

    def relation(self, a: str, b: str) -> str:
        self._ledger.pair()
        self._ledger.unit()
        if a not in self._known or b not in self._known:
            return "unknown"
        if a == b:
            return "same"
        first, second = (a, b) if a < b else (b, a)
        cached = self._pairs.get((first, second))
        if cached is not None:
            return cached if (a, b) == (first, second) else self._INVERSE[cached]
        if first in self._ancestors(second):
            result = "before"
        elif second in self._ancestors(first):
            result = "after"
        else:
            result = "incomparable"
        self._pairs[(first, second)] = result
        return result if (a, b) == (first, second) else self._INVERSE[result]

    def _ancestors(self, start: str) -> set[str]:
        cached = self._memo.get(start)
        if cached is not None:
            return cached
        # The closure construction is charged BEFORE the copies.
        self._ledger.unit()
        seen: set[str] = {start}
        stack: list[str] = [start]
        while stack:
            node = stack.pop()
            for parent in self._parent_map.get(node, ()):
                # Every actual parent-edge visit charges the ONE
                # shared ledger BEFORE the visit.
                self._ledger.unit()
                if parent not in seen:
                    seen.add(parent)
                    stack.append(parent)
        self._memo[start] = seen
        return seen


def _revalidate_ns(ns: CausalHistoryNamespace) -> bool:
    """Explicit ACTUAL-field revalidation of the history namespace
    and its underlying admission scope (O(1) in the historical
    state).

    A borrowed key, ``model_copy``/``model_construct`` instance or
    stale scoped key cannot hide different actual fields or bound
    sets: the ACTUAL accepted admission namespace is revalidated
    from the actual fields, BOTH admission keys and BOTH history
    scope keys are recomputed and compared, the actual history
    bounds are revalidated through the real validators, and the
    SEVEN actual version identities are checked against the
    supported constants (fail closed, never interpreted as
    positive evidence).

    The FULL actual history-namespace field shape is ALSO
    revalidated through the real constructors (a fresh dict through
    the real field/model validators): coherent keys cannot rescue
    an invalid lineage or any other actual field.  This stays O(1)
    in the historical state and makes no authentication claim.
    """
    for actual, supported in _supported_version_pairs(ns):
        if actual != supported:
            return False
    try:
        # warnings=False: a forged (unvalidated) instance must be
        # rejected by the fresh validators WITHOUT the serializer
        # echoing its private field values into a warning.
        CausalHistoryNamespace.model_validate(ns.model_dump(warnings=False))
    except Exception:
        return False
    try:
        BundleAdmissionNamespace.model_validate(
            {
                "principal": ns.principal,
                "session": ns.session,
                "repository": ns.repository,
                "route": ns.route,
                "model_identity": ns.model_identity,
                "config_fingerprint": ns.config_fingerprint,
                "workspace": ns.workspace,
                "mode": ns.mode.value,
                "admission_version": ns.admission_version,
                "observation_version": ns.observation_version,
                "graph_version": ns.graph_version,
                "reference_version": ns.reference_version,
                "proof_version": ns.proof_version,
                "bounds": ns.bounds.model_dump(warnings=False),
                "proof_bounds": ns.proof_bounds.model_dump(warnings=False),
                "graph_bounds": ns.graph_bounds.model_dump(warnings=False),
                "observation_bounds": ns.observation_bounds.model_dump(warnings=False),
                "namespace_key": ns.admission_namespace_key,
                "scoped_key": ns.admission_scoped_key,
            }
        )
    except Exception:
        return False
    try:
        expected_admission = _canonical_namespace_fields(
            ns.principal,
            ns.session,
            ns.repository,
            ns.route,
            ns.model_identity,
            ns.config_fingerprint,
            ns.admission_version,
            ns.graph_version,
            ns.reference_version,
            ns.proof_version,
            ns.observation_version,
            str(ns.mode),
            ns.bounds,
            ns.proof_bounds,
            ns.graph_bounds,
            ns.observation_bounds,
        )
    except Exception:
        return False
    expected_ns_key = _sha256_hex(expected_admission)
    if ns.admission_namespace_key != expected_ns_key:
        return False
    if ns.admission_scoped_key != _sha256_hex(
        (expected_ns_key + "\0" + ns.workspace).encode("utf-8")
    ):
        return False
    try:
        HistoryBounds.model_validate(ns.history_bounds.model_dump(warnings=False))
    except Exception:
        return False
    try:
        expected_history = _sha256_hex(
            _canonical_history_fields(
                ns.principal,
                ns.session,
                ns.repository,
                ns.route,
                ns.model_identity,
                ns.config_fingerprint,
                ns.workspace,
                str(ns.mode),
                ns.admission_version,
                ns.observation_version,
                ns.graph_version,
                ns.reference_version,
                ns.proof_version,
                ns.admission_namespace_key,
                ns.admission_scoped_key,
                ns.lineage_id,
                ns.history_version,
                ns.arguments_version,
                ns.history_bounds,
                ns.bounds,
                ns.proof_bounds,
                ns.graph_bounds,
                ns.observation_bounds,
            )
        )
    except Exception:
        return False
    if ns.history_key != expected_history:
        return False
    if ns.state_scoped_key != _sha256_hex((expected_history + "\0" + ns.workspace).encode("utf-8")):
        return False
    workspace = validate_workspace(ns.workspace, ns.graph_bounds.max_path_bytes)
    if workspace is None or workspace != ns.workspace:
        return False
    return True


def _refusal(
    state: CausalHistoryState,
    outcome: CurrentnessOutcome,
    diagnostics: tuple[CurrentnessLimitation, ...],
) -> CurrentnessResult:
    return CurrentnessResult(outcome=outcome, state=state, diagnostics=diagnostics)


def _evidenced_equal(
    r_digest: str | None,
    r_identity: str,
    c_digest: str | None,
    c_identity: str,
) -> bool:
    """Two claims are evidenced equal iff BOTH are individually
    known with equal digests, or BOTH are unattributed within the
    same single opaque group.  A known-versus-unattributed pair has
    NO equality proof (never a false byte inequality)."""
    if r_digest is not None and c_digest is not None:
        return r_digest == c_digest
    if r_digest is None and c_digest is None:
        return r_identity == c_identity
    return False


def _proof_group_shape(
    segment: BundleSegment,
) -> tuple[BoundaryClass, str, tuple[str | None, ...]] | None:
    """The ACCEPTED boundary law for one retained segment
    (the accepted 018-c ``_file_entry`` classification): PROVEN
    only for a segment that actually attributes exactly one member
    with its granted digest; EVERY other form — including a
    multi-member partition segment behind an outer marker — stays
    BOUNDARYLESS with its exact group bytes digest and unknown
    per-member attribution.  A singleton segment WITHOUT a granted
    digest cannot be represented by the accepted law (returns
    None).  Whole-proof kind and outer markers are provenance,
    never the boundary class.
    """
    positions = segment.member_positions
    digest = segment.member_digest
    group_digest = segment.digest
    if len(positions) == 1 and digest is not None:
        return BoundaryClass.PROVEN, digest, (digest,)
    if len(positions) == 1:
        return None
    return BoundaryClass.BOUNDARYLESS, group_digest, (None,) * len(positions)


def derive_currentness_overlay(
    state: CausalHistoryState,
    ns: CausalHistoryNamespace,
    bounds: CurrentnessBounds | None = None,
) -> CurrentnessResult:
    """The ONE bounded pure currentness derivation (018-e).

    Takes the ACTUAL 018-d state, its ACTUAL namespace and explicit
    currentness bounds (defaults when omitted).  The input is the
    INTERNAL retained-history boundary, never a public supplied
    proof/snapshot/header authority: object construction is not
    authentication.  Unsupported coherent actual versions, foreign
    scope, malformed state or exhausted derived resources give a
    fixed explicit typed refusal with NO partial overlay; the
    EXACT input state is preserved on every outcome.  Early
    fences are O(1) in the historical state; every later scan is
    charged on the ONE shared derivation ledger.
    """
    # --- Early O(1) fences (no scan/copy of the historical state) ---
    if state.history_key != ns.history_key:
        return _refusal(
            state, CurrentnessOutcome.REFUSED_FOREIGN_SCOPE, (CurrentnessLimitation.FOREIGN_SCOPE,)
        )
    if not _revalidate_ns(ns):
        return _refusal(
            state,
            CurrentnessOutcome.REFUSED_VERSION_CONFLICT,
            (CurrentnessLimitation.VERSION_UNSUPPORTED,),
        )
    try:
        effective = CurrentnessBounds.model_validate(
            CurrentnessBounds().model_dump(warnings=False)
            if bounds is None
            else bounds.model_dump(warnings=False)
        )
    except Exception:
        raise ValueError("currentness bounds failed the actual currentness validation") from None
    ledger = _CurrentnessLedger(effective)
    # --- Charged cross-record integrity (the ONE shared ledger) ---
    try:
        state_refusal = validate_causal_history_state(state, ns.history_bounds, work=ledger.unit)
    except _LedgerOverflow as overflow:
        return _refusal(state, CurrentnessOutcome.REFUSED_OVER_BOUND, (overflow.limitation,))
    if state_refusal is not None:
        if state_refusal is CausalHistoryLimitation.WORK_UNITS_OVER_BOUND:
            return _refusal(
                state,
                CurrentnessOutcome.REFUSED_OVER_BOUND,
                (CurrentnessLimitation.WORK_UNITS_OVER_BOUND,),
            )
        return _refusal(
            state,
            CurrentnessOutcome.REFUSED_STATE_MALFORMED,
            (CurrentnessLimitation.STATE_MALFORMED,),
        )
    try:
        # --- Charged occurrence scan: ownership groups + claims ---
        occurrence_ids: set[str] = set()
        for occurrence in state.occurrences:
            ledger.unit()
            occurrence_ids.add(occurrence.occurrence_id)
        parent_map: dict[str, list[str]] = {}
        for link in state.parent_links:
            ledger.unit()
            parent_map.setdefault(link.child, []).append(link.parent)
        relations = _RelationIndex(parent_map, ledger, occurrence_ids)
        # Group facts and per-path claims (root paths are scope
        # context only, never nonroot contenders).
        path_claims: dict[str, list[_Claim]] = {}
        group_facts: list[
            tuple[
                str,
                int,
                BoundaryClass,
                tuple[str, ...],
                tuple[str | None, ...],
                str,
                str | None,
            ]
        ] = []
        for occurrence in state.occurrences:
            proof = occurrence.proof
            root_path = proof.root_path
            for group_index, segment in enumerate(proof.segments):
                # Charge BEFORE the segment shape is inspected.
                ledger.unit()
                shape = _proof_group_shape(segment)
                if shape is None:
                    return _refusal(
                        state,
                        CurrentnessOutcome.REFUSED_STATE_MALFORMED,
                        (CurrentnessLimitation.STATE_MALFORMED,),
                    )
                boundary, group_digest, member_digests = shape
                member_list: list[str] = []
                for position in segment.member_positions:
                    # Charge BEFORE reading the requested member.
                    ledger.unit()
                    normalized = proof.requested_members[position].normalized
                    if normalized is None:
                        return _refusal(
                            state,
                            CurrentnessOutcome.REFUSED_STATE_MALFORMED,
                            (CurrentnessLimitation.STATE_MALFORMED,),
                        )
                    member_list.append(normalized)
                members = tuple(member_list)
                # Reserve the group cap and charge the work BEFORE
                # the canonical identity is built or retained.
                ledger.group()
                ledger.unit()
                identity = opaque_group_identity(
                    boundary,
                    members,
                    group_digest,
                    member_digests,
                    policy_version=CURRENTNESS_POLICY_VERSION,
                    proof_version=ns.proof_version,
                    observation_version=ns.observation_version,
                )
                group_facts.append(
                    (
                        occurrence.occurrence_id,
                        group_index,
                        boundary,
                        members,
                        member_digests,
                        identity,
                        root_path,
                    )
                )
                for local_index, member_path in enumerate(members):
                    ledger.unit()
                    if member_path == root_path:
                        continue
                    rows = path_claims.get(member_path)
                    if rows is None:
                        ledger.path()
                        rows = path_claims[member_path] = []
                    ledger.membership()
                    rows.append(
                        _Claim(
                            occurrence.occurrence_id,
                            group_index,
                            local_index,
                            member_path,
                            member_digests[local_index],
                            identity,
                        )
                    )
        # --- Global maximal-frontier path summaries: ONE charged
        # pass emits the record AND the reverse path index ---
        maximal_by_path: dict[str, list[_Claim]] = {}
        path_records: list[CurrentnessPathRecord] = []
        for path in sorted(path_claims):
            ledger.unit()
            claims = path_claims[path]
            maximal: list[_Claim] = []
            for claim in claims:
                ledger.unit()
                dominated = False
                for other in claims:
                    if other is claim:
                        continue
                    # Charge the ACTUAL identity comparison BEFORE
                    # the same-occurrence skip: N claims on one
                    # path cost N*(N-1) charged events (duplicates
                    # count), never a free quadratic string scan.
                    ledger.unit()
                    if other.occurrence_id == claim.occurrence_id:
                        continue
                    # A claim is dominated only by a provably
                    # NEWER occurrence: this claim is OLDER
                    # (BEFORE other) under the frozen edges.
                    if relations.relation(claim.occurrence_id, other.occurrence_id) == "before":
                        dominated = True
                        break
                if not dominated:
                    maximal.append(claim)
            maximal_by_path[path] = maximal
            known: set[str] = set()
            opaque: set[str] = set()
            # The reverse path index retains EVERY overlapping
            # occurrence (dominated witnesses included); witnesses
            # retain the maximal frontier only.  Every emitted
            # association is charged BEFORE its retention.
            overlapping: set[str] = set()
            for claim in claims:
                ledger.unit()
                if claim.occurrence_id not in overlapping:
                    ledger.membership()
                overlapping.add(claim.occurrence_id)
            witness_ids: set[str] = set()
            for claim in maximal:
                ledger.unit()
                if claim.known_digest is not None:
                    known.add(claim.known_digest)
                else:
                    opaque.add(claim.opaque_identity)
                if claim.occurrence_id not in witness_ids:
                    ledger.membership()
                witness_ids.add(claim.occurrence_id)
            overlapping_tuple = tuple(sorted(overlapping))
            witnesses = tuple(sorted(witness_ids))
            if not opaque and len(known) == 1:
                record = CurrentnessPathRecord(
                    path=path,
                    status=CurrentnessStatus.CURRENT_KNOWN,
                    known_digest=next(iter(known)),
                    witnesses=witnesses,
                    overlapping_occurrences=overlapping_tuple,
                )
            elif not known and len(opaque) == 1:
                record = CurrentnessPathRecord(
                    path=path,
                    status=CurrentnessStatus.CURRENT_OPAQUE,
                    opaque_identity=next(iter(opaque)),
                    witnesses=witnesses,
                    overlapping_occurrences=overlapping_tuple,
                )
            elif len(known) >= 2:
                ledger.diagnostic()
                record = CurrentnessPathRecord(
                    path=path,
                    status=CurrentnessStatus.CONTENT_CONFLICT,
                    reasons=(CurrentnessReason.KNOWN_CONTENT_CONFLICT,),
                    witnesses=witnesses,
                    overlapping_occurrences=overlapping_tuple,
                )
            else:
                ledger.diagnostic()
                record = CurrentnessPathRecord(
                    path=path,
                    status=CurrentnessStatus.OWNERSHIP_AMBIGUITY,
                    reasons=(CurrentnessReason.OWNERSHIP_AMBIGUITY,),
                    witnesses=witnesses,
                    overlapping_occurrences=overlapping_tuple,
                )
            path_records.append(record)
        group_records: list[CurrentnessGroupRecord] = []
        for fact in sorted(group_facts, key=lambda fact: (fact[0], fact[1])):
            (
                occurrence_id,
                group_index,
                boundary,
                members,
                member_digests,
                identity,
                group_root_path,
            ) = fact
            group_rows: list[GroupPathRow] = []
            # Root paths are scope context only: no path row.
            nonroot_paths = sorted({member for member in members if member != group_root_path})
            for path in nonroot_paths:
                ledger.unit()
                own_digest: str | None = None
                for local_index, member_path in enumerate(members):
                    ledger.unit()
                    if member_path == path:
                        own_digest = member_digests[local_index]
                        break
                blockers: set[CurrentnessReason] = set()
                row_witnesses: set[str] = set()
                for claim in maximal_by_path[path]:
                    ledger.unit()
                    if claim.occurrence_id == occurrence_id and claim.group_index == group_index:
                        continue
                    if claim.occurrence_id == occurrence_id:
                        # The SAME occurrence never orders its own
                        # groups (no self-clock).
                        relation = "incomparable"
                    else:
                        relation = relations.relation(occurrence_id, claim.occurrence_id)
                    equal = _evidenced_equal(
                        own_digest,
                        identity,
                        claim.known_digest,
                        claim.opaque_identity,
                    )
                    if equal:
                        continue
                    both_known_differ = (
                        own_digest is not None
                        and claim.known_digest is not None
                        and own_digest != claim.known_digest
                    )
                    if relation == "before":
                        # A provably NEWER claim (this group's
                        # occurrence is older) without an equality
                        # proof stales this historical candidate.
                        blockers.add(
                            CurrentnessReason.PROVEN_CHANGE
                            if both_known_differ
                            else CurrentnessReason.UNPROVEN_OWNERSHIP
                        )
                    elif relation == "after":
                        # An OLDER claim is dominated and never
                        # blocks (replays cannot change the
                        # frontier).
                        continue
                    else:
                        blockers.add(
                            CurrentnessReason.KNOWN_CONTENT_CONFLICT
                            if both_known_differ
                            else CurrentnessReason.OWNERSHIP_AMBIGUITY
                        )
                    if claim.occurrence_id not in row_witnesses:
                        ledger.membership()
                    row_witnesses.add(claim.occurrence_id)
                # Reserve the emitted-row unit BEFORE the row is
                # constructed (never only before the append).
                ledger.membership()
                if not blockers:
                    row = GroupPathRow(
                        path=path,
                        status=(
                            CurrentnessStatus.CURRENT_KNOWN
                            if own_digest is not None
                            else CurrentnessStatus.CURRENT_OPAQUE
                        ),
                    )
                else:
                    sorted_blockers = tuple(sorted(blockers, key=lambda reason: reason.value))
                    if (
                        CurrentnessReason.PROVEN_CHANGE in sorted_blockers
                        or CurrentnessReason.UNPROVEN_OWNERSHIP in sorted_blockers
                    ):
                        row_status = CurrentnessStatus.STALE
                    elif CurrentnessReason.KNOWN_CONTENT_CONFLICT in sorted_blockers:
                        row_status = CurrentnessStatus.CONTENT_CONFLICT
                    else:
                        row_status = CurrentnessStatus.OWNERSHIP_AMBIGUITY
                    for _reason in sorted_blockers:
                        ledger.diagnostic()
                    row = GroupPathRow(
                        path=path,
                        status=row_status,
                        reasons=sorted_blockers,
                        witnesses=tuple(sorted(row_witnesses)),
                    )
                group_rows.append(row)
            if not group_rows:
                # A group with no nonroot members (a root-only
                # proof) is current-opaque: its scope context
                # never contends.
                group_status = CurrentnessStatus.CURRENT_OPAQUE
            elif any(row.status is CurrentnessStatus.STALE for row in group_rows):
                group_status = CurrentnessStatus.STALE
            elif any(row.status is CurrentnessStatus.CONTENT_CONFLICT for row in group_rows):
                group_status = CurrentnessStatus.CONTENT_CONFLICT
            elif any(row.status is CurrentnessStatus.OWNERSHIP_AMBIGUITY for row in group_rows):
                group_status = CurrentnessStatus.OWNERSHIP_AMBIGUITY
            elif all(row.status is CurrentnessStatus.CURRENT_KNOWN for row in group_rows):
                group_status = CurrentnessStatus.CURRENT_KNOWN
            else:
                group_status = CurrentnessStatus.CURRENT_OPAQUE
            group_records.append(
                CurrentnessGroupRecord(
                    occurrence_id=occurrence_id,
                    group_index=group_index,
                    boundary_class=boundary,
                    members=members,
                    member_digests=member_digests,
                    root_path=group_root_path,
                    opaque_identity=identity,
                    path_rows=tuple(group_rows),
                    group_status=group_status,
                )
            )
        # Whole-proof usability: ONE charged pass over the emitted
        # group records (never an uncharged occurrence x group
        # scan); a stale or blocked group withholds ONLY its own
        # occurrence.
        blocked: set[str] = set()
        for group_record in group_records:
            ledger.unit()
            if group_record.group_status not in (
                CurrentnessStatus.CURRENT_KNOWN,
                CurrentnessStatus.CURRENT_OPAQUE,
            ):
                blocked.add(group_record.occurrence_id)
        usable = tuple(sorted(occurrence_ids - blocked))
        emitted = ledger.diag_spent
        overlay = CurrentnessOverlay(
            history_key=state.history_key,
            revision=state.revision,
            workspace=ns.workspace,
            policy_version=CURRENTNESS_POLICY_VERSION,
            bounds=effective,
            scope_key=currentness_scope_key(
                state.history_key, ns.workspace, CURRENTNESS_POLICY_VERSION, effective
            ),
            paths=tuple(path_records),
            groups=tuple(group_records),
            usable_occurrences=tuple(sorted(usable)),
            emitted_reasons=emitted,
        )
        return CurrentnessResult(outcome=CurrentnessOutcome.OK, state=state, overlay=overlay)
    except _LedgerOverflow as overflow:
        return _refusal(state, CurrentnessOutcome.REFUSED_OVER_BOUND, (overflow.limitation,))

"""Inert lean/greedy bundle admission and structural identity (018-c).

One coherent PURE/INERT original-API composition: the accepted 017
observation (re-derived under the ACTUAL effective ``ObservationBounds``),
the single evidenced root/workspace binding (the 018-a law), the
accepted 018-a raw-reference facts (nodes, edges, missing,
unresolved-origin candidates) and the accepted 018-b bundle-proof pass
(self-contained whole-bundle source proofs) are composed into ONE
bounded lean/greedy admission snapshot: the required first-class root
entry, the admitted file-bundle entries with their canonical
structural content keys, the group-owned dependency certificates (the
boundaryless all-eligible common-base law), the complete reverse
member-path index and the source-version observations retained
independently of admission.

Shared-cumulative preflight law (order 018-c): the composition runs
ONE set of cumulative ledgers under the ACTUAL effective values and
NEVER resets any of them per request/group/pass.  Every inspected
source body (every root occurrence, duplicates included; every
selected candidate's full output; every native piece reconstruction;
every group reference-scan body) is accounted with its EXACT UTF-8
byte length against the effective ``GraphBounds`` source ceilings
BEFORE any owned copy/retention.  Every raw-source scan counts as a
document/source-group under the effective ``max_documents`` and all
reference candidates share the effective per-document and total
candidate ceilings.  The effective ``max_work_units`` is ONE shared
admission-closure work ledger: the raw-reference closure, every
queue/candidate reconsideration, every possible-supplier examination
and every reverse-index association operation (duplicate and
unsupported attempts included) charge 1 BEFORE the work.  The
accepted graph/proof public wrappers remain unchanged and keep their
own standalone behavior; this composition reuses their measured
trusted facts and private cores under the shared ledgers rather than
running two independent full passes with reset ledgers (summing stage
totals after the fact would not satisfy the preflight law).  The
accepted 018-a graph ``max_depth`` is NOT applied as an upfront gate
here: the raw closure runs un-gated under the shared ledgers, and the
effective ``max_depth`` is applied to each target's LEAST complete
AND/OR derivation (root 0; a file reference adds 1; a group
certificate adds 1 to the MAXIMUM supplier least-derivation) AFTER
the bounded certificate fixed point, so a valid shorter group
derivation neither pre-empts nor is pre-empted by a longer raw walk.
No bound refusal retains partial admission.  Nothing here is a v1
runtime, compiler or cache-hit claim; the module is never active in
the adapter request path, no command string is executed and no
model/client/service facility is started.
"""

from __future__ import annotations

import json
import math
from collections import deque
from dataclasses import dataclass, field
from typing import Any

from ..cache import RequestIdentity
from .bundle_admission_models import (
    ADMISSION_CONTRACT_VERSION,
    AdmissionLimitation,
    AdmissionMode,
    AdmissionOutcome,
    BoundaryClass,
    BundleAdmissionBounds,
    BundleAdmissionNamespace,
    BundleAdmissionSnapshot,
    BundleEntry,
    BundleKeyRecord,
    EligibilityNode,
    EntryClass,
    GroupCertificate,
    MemberClass,
    OffgraphSourceNode,
    OrdinaryRelationship,
    OwnershipGroup,
    PathAssociation,
    RootEnvelopeOccurrence,
    SourceVersionObservation,
    UnresolvedOriginRecord,
)
from .bundle_proof import (
    _BridgeSourceLedger,
    _BudgetState,
    _proof_pass,
    _SearchLedger,
)
from .bundle_proof_models import (
    BUNDLE_PROOF_CONTRACT_VERSION,
    ROOT_FILENAME,
    BundleLimitation,
    BundleProof,
    BundleProofNamespace,
    BundleProofOutcome,
    BundleSegment,
    make_bundle_proof_namespace,
)
from .client_paths import validate_workspace
from .graph import resolve_reference
from .graph_models import (
    GRAPH_CONTRACT_VERSION,
    REFERENCE_GRAMMAR,
    CandidateStatus,
    GraphLimitation,
    NodeStatus,
    ReferenceCandidate,
    _fixed,
    _sha256_hex,
)
from .graph_observation import GraphRequest, _carrier_string
from .observation_models import (
    EMPTY_SOURCE_SHA256,
    OBSERVER_VERSION,
    Limitation,
    ObservationReport,
    PathContext,
    RootOccurrence,
    sha256_hex,
)
from .observe import observe_request
from .process_chunks import _utf8_byte_length_range
from .references import scan_references

#: Closed mapping from the accepted 018-a graph-stage refusal reasons
#: to the admission closed vocabulary (propagated, never relabeled).
#: Total over every reason the factored raw-reference closure, the
#: root document law and the bounded reference scan can emit at
#: snapshot level (the per-candidate path/target law stays inside the
#: typed candidate records, not in this map).
_GRAPH_BUDGET_MAP: dict[GraphLimitation, AdmissionLimitation] = {
    GraphLimitation.NO_ROOT: AdmissionLimitation.NO_ROOT,
    GraphLimitation.WORKSPACE_UNPROVEN: AdmissionLimitation.WORKSPACE_UNPROVEN,
    GraphLimitation.COMPETING_ROOTS: AdmissionLimitation.COMPETING_ROOTS,
    GraphLimitation.ROOT_CONTEXT_MISMATCH: AdmissionLimitation.ROOT_CONTEXT_MISMATCH,
    GraphLimitation.ROOT_VERSION_CONFLICT: AdmissionLimitation.VERSION_UNSUPPORTED,
    GraphLimitation.BATCH_OVER_BOUND: AdmissionLimitation.BATCH_OVER_BOUND,
    GraphLimitation.SOURCE_OVER_BOUND: AdmissionLimitation.SOURCE_OVER_BOUND,
    GraphLimitation.TOTAL_SOURCE_OVER_BOUND: AdmissionLimitation.TOTAL_SOURCE_OVER_BOUND,
    GraphLimitation.DOCUMENT_OVER_BOUND: AdmissionLimitation.DOCUMENT_OVER_BOUND,
    GraphLimitation.CANDIDATES_PER_DOCUMENT_OVER_BOUND: (
        AdmissionLimitation.CANDIDATES_PER_DOCUMENT_OVER_BOUND
    ),
    GraphLimitation.CANDIDATES_TOTAL_OVER_BOUND: AdmissionLimitation.CANDIDATES_TOTAL_OVER_BOUND,
    GraphLimitation.NODES_OVER_BOUND: AdmissionLimitation.NODES_OVER_BOUND,
    GraphLimitation.EDGES_OVER_BOUND: AdmissionLimitation.EDGES_OVER_BOUND,
    GraphLimitation.WORK_UNITS_EXHAUSTED: AdmissionLimitation.WORK_UNITS_EXHAUSTED,
    GraphLimitation.MALFORMED_UNICODE: AdmissionLimitation.MALFORMED_UNICODE,
    GraphLimitation.VERSION_CONFLICT: AdmissionLimitation.SOURCE_CONFLICT,
    GraphLimitation.CANDIDATE_DIGEST_MISMATCH: AdmissionLimitation.SOURCE_CONFLICT,
    GraphLimitation.NAMESPACE_MISMATCH: AdmissionLimitation.NAMESPACE_MISMATCH,
    GraphLimitation.WORKSPACE_MISMATCH: AdmissionLimitation.WORKSPACE_MISMATCH,
    GraphLimitation.BOUNDS_MISMATCH: AdmissionLimitation.BOUNDS_MISMATCH,
    GraphLimitation.DIAGNOSTICS_FULL: AdmissionLimitation.DIAGNOSTICS_FULL,
}

#: Closed mapping from the accepted 018-b proof-stage reasons to the
#: admission closed vocabulary (propagated, never relabeled).  Total
#: over every ``BundleLimitation`` member the shared proof pass can
#: emit (snapshot-level refusals and per-candidate fixed reasons).
_PROOF_BUDGET_MAP: dict[BundleLimitation, AdmissionLimitation] = {
    BundleLimitation.NO_ROOT: AdmissionLimitation.NO_ROOT,
    BundleLimitation.COMPETING_ROOTS: AdmissionLimitation.COMPETING_ROOTS,
    BundleLimitation.WORKSPACE_UNPROVEN: AdmissionLimitation.WORKSPACE_UNPROVEN,
    BundleLimitation.WORKSPACE_MISMATCH: AdmissionLimitation.WORKSPACE_MISMATCH,
    BundleLimitation.ROOT_CONTEXT_MISMATCH: AdmissionLimitation.ROOT_CONTEXT_MISMATCH,
    BundleLimitation.VERSION_UNSUPPORTED: AdmissionLimitation.VERSION_UNSUPPORTED,
    BundleLimitation.BATCH_OVER_BOUND: AdmissionLimitation.BATCH_OVER_BOUND,
    BundleLimitation.BUNDLES_OVER_BOUND: AdmissionLimitation.BUNDLES_OVER_BOUND,
    BundleLimitation.SOURCE_OVER_BOUND: AdmissionLimitation.SOURCE_OVER_BOUND,
    BundleLimitation.TOTAL_SOURCE_OVER_BOUND: AdmissionLimitation.TOTAL_SOURCE_OVER_BOUND,
    BundleLimitation.MEMBERS_OVER_BOUND: AdmissionLimitation.MEMBERS_OVER_BOUND,
    BundleLimitation.SEGMENTS_OVER_BOUND: AdmissionLimitation.SEGMENTS_OVER_BOUND,
    BundleLimitation.MARKER_OVER_BOUND: AdmissionLimitation.MARKER_OVER_BOUND,
    BundleLimitation.MARKER_SEARCH_OVER_BOUND: AdmissionLimitation.MARKER_SEARCH_OVER_BOUND,
    BundleLimitation.MARKER_EMPTY: AdmissionLimitation.MARKER_EMPTY,
    BundleLimitation.MARKER_MISSING: AdmissionLimitation.MARKER_MISSING,
    BundleLimitation.MARKER_DUPLICATE: AdmissionLimitation.MARKER_DUPLICATE,
    BundleLimitation.MARKER_ORDER: AdmissionLimitation.MARKER_ORDER,
    BundleLimitation.MARKER_OVERLAP: AdmissionLimitation.MARKER_OVERLAP,
    BundleLimitation.PLAN_UNSUPPORTED: AdmissionLimitation.PLAN_UNSUPPORTED,
    BundleLimitation.MEMBER_UNRESOLVED: AdmissionLimitation.MEMBER_UNRESOLVED,
    BundleLimitation.MEMBER_PATH_OVER_BOUND: AdmissionLimitation.MEMBER_PATH_OVER_BOUND,
    BundleLimitation.SEGMENT_UNEXPLAINED: AdmissionLimitation.SEGMENT_UNEXPLAINED,
    BundleLimitation.OUTPUT_INCONSISTENT: AdmissionLimitation.OUTPUT_INCONSISTENT,
    BundleLimitation.SOURCE_CONFLICT: AdmissionLimitation.SOURCE_CONFLICT,
    BundleLimitation.SEAM_CONFLICT: AdmissionLimitation.SEAM_CONFLICT,
    BundleLimitation.DIAGNOSTICS_FULL: AdmissionLimitation.DIAGNOSTICS_FULL,
}


# --- Original-input collection phase (private validated facts) ---------------


class _AdmissionRefusal(Exception):
    """One private typed whole-snapshot refusal (nothing retained).

    ``stage_cap`` is the ACTUAL diagnostic cap of the stage that
    refused: the emitted total (the fixed reason plus the copied
    observation/global limitations) must not exceed it (and, in
    every case, the final admission total cap).  Shared early
    root/binding and batch refusals belong to BOTH the accepted
    graph and proof surfaces and therefore carry the stricter of
    the two stage caps; proof-stage refusals carry the proof cap,
    closure-stage refusals the graph cap and admission/index-phase
    refusals the admission cap.

    The operational repr carries fixed enums only (no source, no
    identity VALUES).
    """

    def __init__(
        self,
        outcome: AdmissionOutcome,
        conflicts: tuple[AdmissionLimitation, ...],
        limitations: tuple[Limitation, ...],
        stage_cap: int,
    ) -> None:
        super().__init__()
        self.outcome = outcome
        self.conflicts = conflicts
        self.limitations = limitations
        self.stage_cap = stage_cap

    def __repr__(self) -> str:
        return (
            f"_AdmissionRefusal(outcome={self.outcome.value!r}, "
            f"conflicts={[v.value for v in self.conflicts]!r})"
        )

    __str__ = __repr__


@dataclass
class _AdmissionFacts:
    """Private validated facts after the original-input collection phase.

    Everything here is re-derived from the ORIGINAL decoded API payloads
    under the namespace's ACTUAL effective ceilings: the 017 re-
    observation pass (derived-workspace contexts), the single
    evidenced root/workspace binding (the 018-a law), the root source
    copied under the SHARED cumulative source ledger, the cumulative
    ledger state and the shared 018-b ``_proof_pass`` result.  The
    operational repr is private-safe (no raw source, no payload, no
    identity VALUES; the embedded accepted records are themselves
    repr-suppressed).
    """

    namespace: BundleAdmissionNamespace
    proof_namespace: BundleProofNamespace
    requests: tuple[GraphRequest, ...]
    contexts: list[PathContext]
    reports: list[ObservationReport]
    ordered_limitations: tuple[Limitation, ...]
    root_digest: str
    root_content: str
    root_occurrences: tuple[tuple[int, RootOccurrence], ...]
    ledger: _BridgeSourceLedger
    search: _SearchLedger
    budget: _BudgetState
    diagnostics: list[BundleLimitation]
    bundles: list[BundleProof]
    proof_candidates_inspected: int

    def __repr__(self) -> str:
        return (
            "_AdmissionFacts(request_count="
            f"{len(self.requests)}, "
            f"root_digest={self.root_digest!r}, "
            f"root_occurrences={len(self.root_occurrences)}, "
            f"bundles={len(self.bundles)}, "
            f"ordered_limitations={[v.value for v in self.ordered_limitations]!r}, "
            f"source_bytes_inspected={self.ledger.total_bytes}, "
            f"proof_candidates_inspected={self.proof_candidates_inspected})"
        )


def _proof_outcome(outcome: BundleProofOutcome) -> AdmissionOutcome:
    """Map the accepted 018-b outcome onto the admission vocabulary
    (the values are identical by the accepted 018-a law)."""
    return AdmissionOutcome(outcome.value)


def _refuse_admission(
    namespace: BundleAdmissionNamespace,
    refusal: _AdmissionRefusal,
    request_count: int,
    work_units: int = 0,
    extra_documents: int = 0,
    extra_candidates: int = 0,
) -> BundleAdmissionSnapshot:
    """A typed snapshot refusal with a bounded final diagnostic.

    The emitted total (the fixed reason plus the copied
    observation/global limitations) is bounded BEFORE retention by
    BOTH the ACTUAL diagnostic cap of the refusing stage
    (``refusal.stage_cap``; shared early root/binding and batch
    refusals carry the stricter graph/proof surface cap) and the
    final admission total cap (which ALWAYS applies to final
    output).  Overflow is ONE fixed ``DIAGNOSTICS_FULL`` refusal
    with NO copied limitations (no silent truncation, no
    governance loss).  A refused snapshot retains no partial
    admission.
    """
    if len(refusal.conflicts) + len(refusal.limitations) > min(
        refusal.stage_cap, namespace.bounds.max_diagnostics
    ):
        return BundleAdmissionSnapshot(
            namespace=namespace,
            outcome=AdmissionOutcome.OVER_BOUND,
            conflicts=(AdmissionLimitation.DIAGNOSTICS_FULL,),
            request_count=request_count,
            entries_retained=0,
            member_occurrences_charged=0,
            reverse_association_attempts=0,
            work_units=work_units,
            extra_documents_inspected=extra_documents,
            extra_candidates_inspected=extra_candidates,
        )
    return BundleAdmissionSnapshot(
        namespace=namespace,
        outcome=refusal.outcome,
        conflicts=refusal.conflicts,
        request_count=request_count,
        entries_retained=0,
        member_occurrences_charged=0,
        reverse_association_attempts=0,
        observation_limitations=refusal.limitations,
        work_units=work_units,
        extra_documents_inspected=extra_documents,
        extra_candidates_inspected=extra_candidates,
    )


def _admission_collect(
    requests: tuple[GraphRequest, ...],
    namespace: BundleAdmissionNamespace,
) -> _AdmissionFacts:
    """The original-input collection phase (raises ``_AdmissionRefusal``).

    Reuses the accepted 017 observation pass, the 018-a root /
    workspace binding law (including the derived-workspace
    re-observation), the shared cumulative source ledger and the
    accepted 018-b ``_proof_pass`` core: no caller flag, hash,
    fabricated member boundary or supplied snapshot creates source
    authority, and no read/parser logic is reimplemented.  On a
    version conflict of the retained proofs the ADMISSION refuses
    ready (nothing retained here; the 018-b proof stage keeps its own
    evidence).
    """
    request_count = len(requests)
    graph_bounds = namespace.graph_bounds
    proof_bounds = namespace.proof_bounds

    if (
        namespace.admission_version != ADMISSION_CONTRACT_VERSION
        or namespace.reference_version != REFERENCE_GRAMMAR
        or namespace.observation_version != OBSERVER_VERSION
        or namespace.graph_version != GRAPH_CONTRACT_VERSION
        or namespace.proof_version != BUNDLE_PROOF_CONTRACT_VERSION
    ):
        raise _AdmissionRefusal(
            AdmissionOutcome.VERSION_CONFLICT,
            (AdmissionLimitation.VERSION_UNSUPPORTED,),
            (),
            namespace.bounds.max_diagnostics,
        )
    if request_count > graph_bounds.max_requests:
        raise _AdmissionRefusal(
            AdmissionOutcome.OVER_BOUND,
            (AdmissionLimitation.BATCH_OVER_BOUND,),
            (),
            min(graph_bounds.max_diagnostics, proof_bounds.max_diagnostics),
        )

    # --- 017 observation pass (actual effective 017 ceilings) ---------
    reports = [
        observe_request(
            request.payload,
            request.context,
            namespace.observation_bounds,
            request.endpoint,
        )
        for request in requests
    ]

    def _limitations() -> tuple[Limitation, ...]:
        collected: set[Limitation] = set()
        for report in reports:
            collected.update(report.roots.conflicts)
            collected.update(reason for read in report.reads for reason in read.reasons)
            collected.update(reason for proc in report.processes for reason in proc.reasons)
            collected.update(record.limitation for record in report.unpaired)
        return tuple(sorted(collected))

    ordered_limitations = _limitations()

    # --- Root / workspace binding (the 018-a law) ----------------------
    authoritative: list[tuple[int, RootOccurrence]] = []
    for request_index, report in enumerate(reports):
        for root_occ in report.roots.roots:
            authoritative.append((request_index, root_occ))
    if not authoritative:
        raise _AdmissionRefusal(
            AdmissionOutcome.NO_ROOT,
            (AdmissionLimitation.NO_ROOT,),
            ordered_limitations,
            min(graph_bounds.max_diagnostics, proof_bounds.max_diagnostics),
        )
    identities = {(occ.scope_label, occ.digest) for _, occ in authoritative}
    if len(identities) > 1:
        raise _AdmissionRefusal(
            AdmissionOutcome.ROOT_CONFLICT,
            (AdmissionLimitation.COMPETING_ROOTS,),
            ordered_limitations,
            min(graph_bounds.max_diagnostics, proof_bounds.max_diagnostics),
        )
    scope_label, root_digest = next(iter(identities))
    if scope_label is None or root_digest is None:
        raise _AdmissionRefusal(
            AdmissionOutcome.NO_ROOT,
            (AdmissionLimitation.NO_ROOT,),
            ordered_limitations,
            min(graph_bounds.max_diagnostics, proof_bounds.max_diagnostics),
        )
    workspace = validate_workspace(scope_label, graph_bounds.max_path_bytes)
    if workspace is None or workspace != scope_label:
        raise _AdmissionRefusal(
            AdmissionOutcome.WORKSPACE_UNPROVEN,
            (AdmissionLimitation.WORKSPACE_UNPROVEN,),
            ordered_limitations,
            min(graph_bounds.max_diagnostics, proof_bounds.max_diagnostics),
        )
    if workspace != namespace.workspace:
        raise _AdmissionRefusal(
            AdmissionOutcome.ROOT_CONFLICT,
            (AdmissionLimitation.WORKSPACE_MISMATCH,),
            ordered_limitations,
            min(graph_bounds.max_diagnostics, proof_bounds.max_diagnostics),
        )
    for request in requests:
        request_context = request.context
        if (
            request_context is not None
            and request_context.workspace is not None
            and request_context.workspace != workspace
        ):
            raise _AdmissionRefusal(
                AdmissionOutcome.ROOT_CONFLICT,
                (AdmissionLimitation.ROOT_CONTEXT_MISMATCH,),
                ordered_limitations,
                min(graph_bounds.max_diagnostics, proof_bounds.max_diagnostics),
            )

    # --- Derived-workspace re-observation (the 018-a law) --------------
    contexts: list[PathContext] = []
    for index, request in enumerate(requests):
        context = request.context
        if context is not None and context.workspace is not None:
            contexts.append(context)
            continue
        derived = PathContext(
            workspace=workspace,
            workdir=context.workdir if context is not None else None,
        )
        reports[index] = observe_request(
            request.payload,
            derived,
            namespace.observation_bounds,
            request.endpoint,
        )
        contexts.append(derived)
    authoritative = []
    for request_index, report in enumerate(reports):
        for root_occ in report.roots.roots:
            authoritative.append((request_index, root_occ))
    ordered_limitations = _limitations()

    # --- Shared cumulative ledgers (before any copy/retention) --------
    ledger = _BridgeSourceLedger(graph_bounds)
    search = _SearchLedger(proof_bounds.max_marker_search)
    budget = _BudgetState(proof_bounds)
    # The known observation/global limitations are shared stage
    # output: they count against the proof-stage total (the
    # accepted 018-b law), the graph-stage total (the accepted
    # 018-a stage law) and the final admission total.  If they
    # alone exceed the ACTUAL stricter of the three caps the whole
    # snapshot is refused BEFORE any source work (no root fetch,
    # no proof body fetch, no appended diagnostic) with the one
    # bounded fixed reason.  Independent proof/candidate and
    # closure diagnostics keep their own stage caps (they are not
    # output of another stage).
    if len(ordered_limitations) > min(
        proof_bounds.max_diagnostics,
        namespace.bounds.max_diagnostics,
        graph_bounds.max_diagnostics,
    ):
        raise _AdmissionRefusal(
            AdmissionOutcome.OVER_BOUND,
            (AdmissionLimitation.DIAGNOSTICS_FULL,),
            (),
            namespace.bounds.max_diagnostics,
        )

    # Every root occurrence (duplicates included) is an inspected
    # source body: measured and accounted BEFORE any owned copy; only
    # the first occurrence is copied (its digest is already bound by
    # the single (scope_label, digest) identity above).
    root_content: str | None = None
    for request_index, root_occ in authoritative:
        carrier = _carrier_string(requests[request_index].payload, root_occ.location)
        span = root_occ.content_span
        if carrier is None or span is None or span.end > len(carrier):
            continue
        n_bytes = _utf8_byte_length_range(carrier, span.start, span.end)
        if n_bytes is None:
            raise _AdmissionRefusal(
                AdmissionOutcome.WORKSPACE_UNPROVEN,
                (AdmissionLimitation.WORKSPACE_UNPROVEN,),
                ordered_limitations,
                min(graph_bounds.max_diagnostics, proof_bounds.max_diagnostics),
            )
        ledger.account(n_bytes)
        if ledger.refusal is not None:
            raise _AdmissionRefusal(
                AdmissionOutcome.OVER_BOUND,
                (_PROOF_BUDGET_MAP[ledger.refusal],),
                ordered_limitations,
                min(graph_bounds.max_diagnostics, proof_bounds.max_diagnostics),
            )
        if root_content is None:
            root_content = carrier[span.start : span.end]
            if sha256_hex(root_content) != root_digest:
                # Defensive 017 integrity defect: the root is not
                # acquired (no echo of the content).
                raise _AdmissionRefusal(
                    AdmissionOutcome.WORKSPACE_UNPROVEN,
                    (AdmissionLimitation.WORKSPACE_UNPROVEN,),
                    ordered_limitations,
                    min(graph_bounds.max_diagnostics, proof_bounds.max_diagnostics),
                )
    if root_content is None:
        raise _AdmissionRefusal(
            AdmissionOutcome.NO_ROOT,
            (AdmissionLimitation.NO_ROOT,),
            ordered_limitations,
            min(graph_bounds.max_diagnostics, proof_bounds.max_diagnostics),
        )

    # --- The proof namespace for the shared 018-b core -----------------
    proof_namespace = make_bundle_proof_namespace(
        RequestIdentity(
            principal=namespace.principal,
            session=namespace.session,
            repository=namespace.repository,
            route=namespace.route,
        ),
        model_identity=namespace.model_identity,
        config_fingerprint=namespace.config_fingerprint,
        workspace=namespace.workspace,
        bounds=namespace.proof_bounds,
        graph_bounds=namespace.graph_bounds,
        observation_bounds=namespace.observation_bounds,
    )

    diagnostics: list[BundleLimitation] = []

    def _note_diagnostic(reason: BundleLimitation) -> bool:
        """Retain one candidate-level fixed diagnostic only while the
        TOTAL emitted diagnostics (candidate reasons + observation /
        global limitations) stay at the ACTUAL proof-stage bound (the
        accepted 018-b law) AND the ACTUAL admission bound.  The bound
        is enforced BEFORE retention/append: overflow is the bounded
        ``DIAGNOSTICS_FULL`` refusal, never a truncated or unbounded
        reason list."""
        total_if_retained = len(diagnostics) + len(ordered_limitations) + 1
        if (
            total_if_retained > proof_bounds.max_diagnostics
            or total_if_retained > namespace.bounds.max_diagnostics
        ):
            return False
        diagnostics.append(reason)
        return True

    result = _proof_pass(
        requests,
        contexts,
        reports,
        proof_namespace,
        namespace.proof_bounds,
        root_digest,
        ledger,
        search,
        budget,
        diagnostics,
        _note_diagnostic,
        len(ordered_limitations),
    )
    if result.refusal_reason is not None:
        if result.refusal_outcome is None:
            raise _fixed("a proof pass refusal carries its outcome")
        limitations: tuple[Limitation, ...] = (
            ()
            if result.refusal_reason is BundleLimitation.DIAGNOSTICS_FULL
            else ordered_limitations
        )
        raise _AdmissionRefusal(
            _proof_outcome(result.refusal_outcome),
            (_PROOF_BUDGET_MAP[result.refusal_reason],),
            limitations,
            proof_bounds.max_diagnostics,
        )
    if result.conflicts:
        # A version conflict of the retained proofs refuses the
        # ADMISSION ready: nothing is retained in this slice (the
        # 018-b proof stage keeps its own evidence).
        raise _AdmissionRefusal(
            AdmissionOutcome.VERSION_CONFLICT,
            tuple(sorted({_PROOF_BUDGET_MAP[c] for c in result.conflicts})),
            ordered_limitations,
            proof_bounds.max_diagnostics,
        )
    return _AdmissionFacts(
        namespace=namespace,
        proof_namespace=proof_namespace,
        requests=requests,
        contexts=contexts,
        reports=reports,
        ordered_limitations=ordered_limitations,
        root_digest=root_digest,
        root_content=root_content,
        root_occurrences=tuple(authoritative),
        ledger=ledger,
        search=search,
        budget=budget,
        diagnostics=diagnostics,
        bundles=result.bundles,
        proof_candidates_inspected=result.candidates_inspected,
    )


# --- The shared admission-closure work ledger and scan budgets ---------------


class _AdmissionWorkCounter:
    """The ONE shared cumulative work-unit ledger (order 018-c law).

    ``charge`` records ONE unit BEFORE the work it gates and reports
    whether the charge is allowed: a charge that would cross the
    ACTUAL effective ``GraphBounds.max_work_units`` is refused BEFORE
    the crossing operation runs.  The counter is cumulative and is
    NEVER reset per request/group/pass; the raw-reference closure,
    every queue/candidate reconsideration, every possible-supplier
    examination and every reverse-index association operation all
    charge this ONE ledger.
    """

    __slots__ = ("_limit", "units", "refused")

    def __init__(self, limit: int) -> None:
        self._limit = limit
        self.units = 0
        self.refused = False

    def charge(self) -> bool:
        # Refuse BEFORE the crossing unit is counted: the crossing
        # operation never runs and its unit is not consumed
        # (at-limit is at-limit: exactly ``_limit`` units succeed).
        if self.units + 1 > self._limit:
            self.refused = True
            return False
        self.units += 1
        return True


class _ScanBudgetCounter:
    """One cumulative scan-budget counter (documents or candidates).

    Every raw-source scan counts as a document/source-group under the
    ACTUAL effective ``max_documents``; all reference candidates share
    the ACTUAL effective total candidate ceiling.  At-limit is
    at-limit; the first crossing scan/candidate is a fixed typed
    refusal decided BEFORE the work/retention.
    """

    __slots__ = ("_limit", "count", "refused")

    def __init__(self, limit: int) -> None:
        self._limit = limit
        self.count = 0
        self.refused = False

    def charge(self) -> bool:
        # Refuse BEFORE the crossing scan/candidate is counted
        # (at-limit is at-limit: exactly ``_limit`` units succeed).
        if self.count + 1 > self._limit:
            self.refused = True
            return False
        self.count += 1
        return True


@dataclass
class _SourceNode:
    """One closure node (path -> source facts; no fabricated edges).

    ``digest`` is ``None`` on a version conflict (no version is ever
    selected); ``text`` is the acquired source text (``None`` for
    content-missing or conflicted nodes).  A scanned node is never
    rescanned; a conflicted node never expands (no digest to bind).
    """

    path: str
    digest: str | None
    text: str | None
    status: NodeStatus
    scanned: bool = False

    def __repr__(self) -> str:
        # Operational repr never exposes the acquired source text.
        return (
            "_SourceNode("
            f"path={self.path!r}, "
            f"status={self.status.value!r}, "
            f"digest={self.digest!r}, "
            f"text=<suppressed>, "
            f"scanned={self.scanned!r})"
        )

    __str__ = __repr__


@dataclass
class _CertificateFact:
    """One earned group-owned dependency certificate (raw fact)."""

    group: _GroupSource
    candidate: ReferenceCandidate
    target_path: str
    depth: int

    def __repr__(self) -> str:
        return (
            "_CertificateFact("
            f"group={self.group!r}, "
            f"candidate={self.candidate!r}, "
            f"target_path={self.target_path!r}, "
            f"depth={self.depth!r})"
        )

    __str__ = __repr__


@dataclass
class _GroupCandidate:
    """One reference measured inside a boundaryless group."""

    candidate: ReferenceCandidate
    state: str = "pending"  # "pending" | "certificate" | "unresolved"
    resolved: str | None = None

    def __repr__(self) -> str:
        return (
            "_GroupCandidate("
            f"candidate={self.candidate!r}, "
            f"state={self.state!r}, "
            f"resolved={self.resolved!r})"
        )

    __str__ = __repr__


@dataclass
class _GroupSource:
    """One boundaryless cat-run group (a proof segment, >= 2 members).

    The group is scanned for its references REGARDLESS of supplier
    eligibility (the unresolved-origin evidence is retained); a
    certificate is earned only under the all-eligible common-base
    law.  ``supplier_occurrences`` is the ordered supplier sequence
    (repetitions preserved); ``possible_origins`` the sorted unique
    supplier paths.
    """

    proof: BundleProof
    segment_index: int
    text: str
    digest: str
    supplier_occurrences: tuple[str, ...]
    possible_origins: tuple[str, ...]
    candidates: list[_GroupCandidate] = field(default_factory=list)
    scanned: bool = False

    def __repr__(self) -> str:
        # Operational repr never exposes the group source text; the
        # embedded proof/candidates keep their own safe reprs.
        return (
            "_GroupSource("
            f"request_index={self.proof.request_index!r}, "
            f"result_location={self.proof.result_location!r}, "
            f"segment_index={self.segment_index!r}, "
            f"digest={self.digest!r}, "
            f"supplier_occurrences={self.supplier_occurrences!r}, "
            f"possible_origins={self.possible_origins!r}, "
            f"candidate_count={len(self.candidates)!r}, "
            f"scanned={self.scanned!r}, "
            f"text=<suppressed>)"
        )

    __str__ = __repr__


@dataclass
class _ClosureResult:
    """The measured AND/OR raw-reference closure facts (private)."""

    nodes: dict[str, _SourceNode]
    best_depth: dict[str, int]
    relationships: dict[tuple[str, str], int]
    certificates: list[_CertificateFact]
    groups: list[_GroupSource]
    closure_diagnostics: list[AdmissionLimitation]


def _dir_name(path: str) -> str:
    """The canonical lexical directory of one normalized relative
    path (``''`` for a workspace-root file).  Lexical only: no
    filesystem, no normalization beyond the accepted path law."""
    if "/" in path:
        return path.rsplit("/", 1)[0]
    return ""


def _admission_closure(
    facts: _AdmissionFacts,
    work: _AdmissionWorkCounter,
    documents: _ScanBudgetCounter,
    candidate_total: _ScanBudgetCounter,
) -> _ClosureResult:
    """The new bounded AND/OR raw-reference closure (018-c law).

    Runs the raw-reference closure over the validated source groups
    from the shared ``_proof_pass`` under ONE shared work ledger and
    the ACTUAL effective node/edge/document/candidate ceilings:

    * eligible nodes (root, independently attributable acquired
      members) are scanned with the accepted bounded scanner
      (``referring_path``/``referring_digest`` attribution);
    * boundaryless groups are scanned unattributed
      (``referring_path=None``) and their references become
      group-owned candidates;
    * a group candidate earns a GROUP-OWNED certificate exactly when
      EVERY possible supplier is independently eligible and every
      supplier shares the same canonical lexical directory (the
      common base is a resolution base only — no supplying file, no
      file edge, no fabricated shortest distance is invented);
    * eligibility and the LEAST complete AND/OR derivation depth are
      relaxed to a bounded fixed point (root 0; a file reference
      adds 1; a certificate adds 1 to the MAXIMUM supplier
      least-derivation; alternative complete derivations take the
      minimum); cycles never create initial eligibility;
    * the effective ``max_depth`` is applied to each target's LEAST
      complete derivation AFTER the fixed point (a longer alternate
      walk neither pre-empts nor is pre-empted by a valid shorter
      derivation); over-depth is a typed whole-snapshot refusal.

    No depth gate pre-empts the closure (the accepted 018-a
    ``max_depth`` is not applied as an upfront gate here).  Every
    charge happens BEFORE the work/retention it gates.
    """
    namespace = facts.namespace
    graph_bounds = namespace.graph_bounds
    workspace = namespace.workspace
    scoped_key = namespace.scoped_key
    limitations = facts.ordered_limitations

    nodes: dict[str, _SourceNode] = {}
    best_depth: dict[str, int] = {}
    relationships: dict[tuple[str, str], int] = {}
    certificates: list[_CertificateFact] = []
    groups: list[_GroupSource] = []
    closure_diagnostics: list[AdmissionLimitation] = []
    max_nodes = graph_bounds.max_nodes
    max_edges = graph_bounds.max_edges
    max_path_bytes = graph_bounds.max_path_bytes

    def _charged_segment_texts(proof: BundleProof) -> list[str]:
        """The exact ordered segment bytes (the segments concatenate in
        order into the self-contained aggregate source).

        Every NEW substring copy is a genuine owned copy of source
        bytes: it is charged to the SAME shared source ledger (the
        MEASURED ``segment.byte_length``) BEFORE slicing/retention and
        the first crossing copy is a typed whole-snapshot refusal
        (at-limit is at-limit, one global ledger, never reset).  The
        whole aggregate source was already accounted in the proof
        pass; these re-exposures are additional owned copies and the
        already-owned validated segment text is reused for all
        subsequent scans/finalization."""
        ledger = facts.ledger
        texts: list[str] = []
        offset = 0
        for segment in proof.segments:
            ledger.account(segment.byte_length)
            if ledger.refusal is not None:
                raise _AdmissionRefusal(
                    AdmissionOutcome.OVER_BOUND,
                    (_PROOF_BUDGET_MAP[ledger.refusal],),
                    limitations,
                    graph_bounds.max_diagnostics,
                )
            texts.append(proof.source_text[offset : offset + segment.char_length])
            offset += segment.char_length
        return texts

    def _note_diagnostic(reason: AdmissionLimitation) -> bool:
        # The closure diagnostics are GRAPH-STAGE output: the ACTUAL
        # stricter of the graph cap (the accepted 018-a stage law) and
        # the final admission total bound gates every append BEFORE
        # retention (overflow is the bounded DIAGNOSTICS_FULL refusal).
        if len(closure_diagnostics) + len(limitations) + 1 > graph_bounds.max_diagnostics or (
            len(facts.diagnostics) + len(closure_diagnostics) + len(limitations) + 1
            > namespace.bounds.max_diagnostics
        ):
            return False
        closure_diagnostics.append(reason)
        return True

    def _add_node(path: str, digest: str | None, text: str | None, status: NodeStatus) -> None:
        # The node bound is enforced BEFORE each insertion (018-a law).
        if path not in nodes and len(nodes) + 1 > max_nodes:
            raise _AdmissionRefusal(
                AdmissionOutcome.OVER_BOUND,
                (AdmissionLimitation.NODES_OVER_BOUND,),
                limitations,
                graph_bounds.max_diagnostics,
            )
        existing = nodes.get(path)
        if existing is None:
            nodes[path] = _SourceNode(path, digest, text, status)
            return
        if existing.status is NodeStatus.VERSION_CONFLICT:
            return
        if status is NodeStatus.VERSION_CONFLICT or (
            digest is not None and existing.digest is not None and digest != existing.digest
        ):
            # Same path, different content: typed conflict, no version
            # selected (no digest retained; the node never expands).
            nodes[path] = _SourceNode(path, None, None, NodeStatus.VERSION_CONFLICT)

    def _relate(referring: str, referring_digest: str, target: str) -> None:
        key = (referring, target)
        if key not in relationships:
            # The COMBINED ordinary-relationship plus certificate
            # count is bounded by the ACTUAL effective max_edges.
            if len(relationships) + len(certificates) + 1 > max_edges:
                raise _AdmissionRefusal(
                    AdmissionOutcome.OVER_BOUND,
                    (AdmissionLimitation.EDGES_OVER_BOUND,),
                    limitations,
                    graph_bounds.max_diagnostics,
                )
        relationships[key] = relationships.get(key, 0) + 1

    # --- Root node (depth 0, always eligible) --------------------------
    root_status = (
        NodeStatus.ACQUIRED_EMPTY
        if facts.root_digest == EMPTY_SOURCE_SHA256
        else NodeStatus.ACQUIRED
    )
    _add_node(ROOT_FILENAME, facts.root_digest, facts.root_content, root_status)
    best_depth[ROOT_FILENAME] = 0

    # --- Acquired members and boundaryless groups (the validated proofs)
    for proof in facts.bundles:
        for segment_index, text in enumerate(_charged_segment_texts(proof)):
            segment = proof.segments[segment_index]
            positions = segment.member_positions
            if len(positions) == 1 and segment.member_digest is not None:
                # Independently attributable single-occurrence member:
                # the path acquires its proven source (the segment's
                # exact bytes).
                member = proof.requested_members[positions[0]]
                path = member.normalized
                if path is None:
                    continue  # defensive (the resolved-member law)
                member_status = (
                    NodeStatus.ACQUIRED_EMPTY
                    if segment.member_digest == EMPTY_SOURCE_SHA256
                    else NodeStatus.ACQUIRED
                )
                _add_node(path, segment.member_digest, text, member_status)
            else:
                # Boundaryless group (>= 2 occurrences, or a repeated
                # group with no single-occurrence attribution): no
                # per-file hash is ever invented from the width.
                suppliers: list[str] = []
                for position in positions:
                    normalized = proof.requested_members[position].normalized
                    if normalized is not None:
                        suppliers.append(normalized)
                if not suppliers:
                    continue  # no possible origin: nothing to retain
                groups.append(
                    _GroupSource(
                        proof=proof,
                        segment_index=segment_index,
                        text=text,
                        digest=segment.digest,
                        supplier_occurrences=tuple(suppliers),
                        possible_origins=tuple(sorted(set(suppliers))),
                    )
                )

    # --- Eager group scans (unresolved-origin evidence is retained) -----
    queue: deque[str] = deque([ROOT_FILENAME])
    for group in groups:
        if not work.charge():
            raise _AdmissionRefusal(
                AdmissionOutcome.OVER_BOUND,
                (AdmissionLimitation.WORK_UNITS_EXHAUSTED,),
                limitations,
                graph_bounds.max_diagnostics,
            )
        group.scanned = True
        if not documents.charge():
            raise _AdmissionRefusal(
                AdmissionOutcome.OVER_BOUND,
                (AdmissionLimitation.DOCUMENT_OVER_BOUND,),
                limitations,
                graph_bounds.max_diagnostics,
            )
        scan = scan_references(
            group.text,
            referring_path=None,
            scoped_key=scoped_key,
            referring_digest=None,
            bounds=graph_bounds,
        )
        if scan.limitation is not None:
            # A scanner resource/malformed-source limitation is a TYPED
            # WHOLE-SNAPSHOT refusal (the accepted 018-a scan law): the
            # document's candidate enumeration is incomplete, so no
            # partial COMPLETE with a diagnostic is ever emitted; the
            # actual reason is propagated.
            raise _AdmissionRefusal(
                AdmissionOutcome.OVER_BOUND,
                (_GRAPH_BUDGET_MAP[scan.limitation],),
                limitations,
                graph_bounds.max_diagnostics,
            )
        for candidate in scan.candidates:
            if not work.charge():
                raise _AdmissionRefusal(
                    AdmissionOutcome.OVER_BOUND,
                    (AdmissionLimitation.WORK_UNITS_EXHAUSTED,),
                    limitations,
                    graph_bounds.max_diagnostics,
                )
            if not candidate_total.charge():
                raise _AdmissionRefusal(
                    AdmissionOutcome.OVER_BOUND,
                    (AdmissionLimitation.CANDIDATES_TOTAL_OVER_BOUND,),
                    limitations,
                    graph_bounds.max_diagnostics,
                )
            group.candidates.append(_GroupCandidate(candidate=candidate))

    # --- Fixed point: node scans + certificate reconsideration ----------
    # Scanned-text caching must not freeze downstream or certificate
    # depths: when a better least derivation appears for an
    # already-scanned node the node is RE-scanned under the SAME work
    # ledger (a charged additional actual scan) and its outgoing
    # relationships are re-relaxed at the improved depth; an
    # already-earned certificate is re-derived (1 + the improved
    # MAXIMUM supplier least-derivation) and its target re-relaxed.
    # Every depth is a strictly decreasing integer bounded below by
    # 0, so the fixed point terminates; every charged operation
    # counts against the ONE shared work ledger.
    scan_depth: dict[str, int] = {}
    cert_depth_checked: dict[tuple[int, int], int] = {}
    cert_facts: dict[tuple[int, int], _CertificateFact] = {}

    def _enqueue_target(resolved: str, improved: bool) -> bool:
        target_node = nodes[resolved]
        if (
            target_node.text is not None
            and target_node.status is not NodeStatus.VERSION_CONFLICT
            and (improved or not target_node.scanned)
        ):
            queue.append(resolved)
            return True
        return False

    while True:
        # 1) drain the scan queue (each scan/re-scan is one charged operation)
        while queue:
            if not work.charge():
                raise _AdmissionRefusal(
                    AdmissionOutcome.OVER_BOUND,
                    (AdmissionLimitation.WORK_UNITS_EXHAUSTED,),
                    limitations,
                    graph_bounds.max_diagnostics,
                )
            path = queue.popleft()
            node = nodes[path]
            if node.text is None or node.status is NodeStatus.VERSION_CONFLICT:
                continue
            current_depth = best_depth.get(path)
            if current_depth is None:
                continue  # defensive: queued nodes carry a derivation
            rescanning = node.scanned and current_depth < scan_depth.get(path, math.inf)
            if node.scanned and not rescanning:
                continue  # the cached scan already reflects the current depth
            node.scanned = True
            if not documents.charge():
                raise _AdmissionRefusal(
                    AdmissionOutcome.OVER_BOUND,
                    (AdmissionLimitation.DOCUMENT_OVER_BOUND,),
                    limitations,
                    graph_bounds.max_diagnostics,
                )
            scan = scan_references(
                node.text,
                referring_path=node.path,
                scoped_key=scoped_key,
                referring_digest=node.digest,
                bounds=graph_bounds,
            )
            if scan.limitation is not None:
                # The same accepted 018-a scan law applies to every
                # re-scan: a scanner resource/malformed-source
                # limitation is a typed whole-snapshot refusal, never
                # a partial COMPLETE with a diagnostic.
                raise _AdmissionRefusal(
                    AdmissionOutcome.OVER_BOUND,
                    (_GRAPH_BUDGET_MAP[scan.limitation],),
                    limitations,
                    graph_bounds.max_diagnostics,
                )
            for candidate in scan.candidates:
                if not work.charge():
                    raise _AdmissionRefusal(
                        AdmissionOutcome.OVER_BOUND,
                        (AdmissionLimitation.WORK_UNITS_EXHAUSTED,),
                        limitations,
                        graph_bounds.max_diagnostics,
                    )
                if not candidate_total.charge():
                    raise _AdmissionRefusal(
                        AdmissionOutcome.OVER_BOUND,
                        (AdmissionLimitation.CANDIDATES_TOTAL_OVER_BOUND,),
                        limitations,
                        graph_bounds.max_diagnostics,
                    )
                if candidate.status is not CandidateStatus.ACCEPTED:
                    continue  # the typed reason stays in the candidate record
                resolved, limitation = resolve_reference(
                    node.path, candidate.target_chars, workspace, max_path_bytes
                )
                if limitation is not None or resolved is None:
                    continue  # typed per-candidate non-acquisition (retained)
                assert node.digest is not None  # a scanned node is acquired
                if not rescanning:
                    _relate(node.path, node.digest, resolved)
                new_depth = best_depth[node.path] + 1
                improved = new_depth < best_depth.get(resolved, math.inf)
                if improved:
                    best_depth[resolved] = new_depth
                if resolved not in nodes:
                    if len(nodes) + 1 > max_nodes:
                        raise _AdmissionRefusal(
                            AdmissionOutcome.OVER_BOUND,
                            (AdmissionLimitation.NODES_OVER_BOUND,),
                            limitations,
                            graph_bounds.max_diagnostics,
                        )
                    nodes[resolved] = _SourceNode(
                        resolved, None, None, NodeStatus.DISCOVERED_CONTENT_MISSING
                    )
                _enqueue_target(resolved, improved)
            scan_depth[path] = best_depth[path]
        # 2) one certificate reconsideration pass
        progress = False
        for group_index, group in enumerate(groups):
            for gc_index, gc in enumerate(group.candidates):
                cert_key = (group_index, gc_index)
                if gc.state == "certificate":
                    # An already-earned certificate is re-derived
                    # whenever a supplier's least derivation improved:
                    # the witness depth (1 + MAXIMUM supplier
                    # least-derivation) and the target relaxation
                    # follow the improvement under the SAME ledger.
                    if not work.charge():
                        raise _AdmissionRefusal(
                            AdmissionOutcome.OVER_BOUND,
                            (AdmissionLimitation.WORK_UNITS_EXHAUSTED,),
                            limitations,
                            graph_bounds.max_diagnostics,
                        )
                    max_supplier_depth = 0
                    for supplier in group.possible_origins:
                        if not work.charge():
                            raise _AdmissionRefusal(
                                AdmissionOutcome.OVER_BOUND,
                                (AdmissionLimitation.WORK_UNITS_EXHAUSTED,),
                                limitations,
                                graph_bounds.max_diagnostics,
                            )
                        supplier_depth = best_depth.get(supplier)
                        if supplier_depth is None:
                            continue  # defensive: earned implies eligible
                        if supplier_depth > max_supplier_depth:
                            max_supplier_depth = supplier_depth
                    checked = cert_depth_checked.get(cert_key)
                    if checked is not None and max_supplier_depth >= checked:
                        continue  # no supplier improvement since last check
                    fact = cert_facts.get(cert_key)
                    if fact is None:
                        continue  # defensive
                    cert_depth_checked[cert_key] = max_supplier_depth
                    new_depth = 1 + max_supplier_depth
                    if new_depth < fact.depth:
                        fact.depth = new_depth
                        improved = new_depth < best_depth.get(fact.target_path, math.inf)
                        if improved:
                            best_depth[fact.target_path] = new_depth
                            progress = True
                        if _enqueue_target(fact.target_path, improved):
                            progress = True
                    continue
                if gc.state != "pending":
                    continue
                if not work.charge():
                    raise _AdmissionRefusal(
                        AdmissionOutcome.OVER_BOUND,
                        (AdmissionLimitation.WORK_UNITS_EXHAUSTED,),
                        limitations,
                        graph_bounds.max_diagnostics,
                    )
                all_eligible = True
                max_supplier_depth = 0
                for supplier in group.possible_origins:
                    if not work.charge():
                        raise _AdmissionRefusal(
                            AdmissionOutcome.OVER_BOUND,
                            (AdmissionLimitation.WORK_UNITS_EXHAUSTED,),
                            limitations,
                            graph_bounds.max_diagnostics,
                        )
                    supplier_depth = best_depth.get(supplier)
                    if supplier_depth is None:
                        all_eligible = False
                        break
                    if supplier_depth > max_supplier_depth:
                        max_supplier_depth = supplier_depth
                if not all_eligible:
                    continue  # still pending: reconsider when eligibility grows
                directories = {_dir_name(supplier) for supplier in group.possible_origins}
                if len(directories) > 1:
                    # Different canonical directories: equal directories
                    # alone never identify a supplier — terminal
                    # unresolved-origin evidence.
                    gc.state = "unresolved"
                    continue
                resolved, limitation = resolve_reference(
                    group.possible_origins[0],
                    gc.candidate.target_chars,
                    workspace,
                    max_path_bytes,
                )
                if limitation is not None or resolved is None:
                    # A typed non-resolution (traversal/outside/absolute
                    # unproven): terminal, retained as evidence.
                    gc.state = "unresolved"
                    continue
                depth = 1 + max_supplier_depth
                if len(relationships) + len(certificates) + 1 > max_edges:
                    raise _AdmissionRefusal(
                        AdmissionOutcome.OVER_BOUND,
                        (AdmissionLimitation.EDGES_OVER_BOUND,),
                        limitations,
                        graph_bounds.max_diagnostics,
                    )
                fact = _CertificateFact(group, gc.candidate, resolved, depth)
                certificates.append(fact)
                cert_facts[cert_key] = fact
                cert_depth_checked[cert_key] = max_supplier_depth
                gc.state = "certificate"
                gc.resolved = resolved
                if depth < best_depth.get(resolved, math.inf):
                    best_depth[resolved] = depth
                    progress = True
                if resolved not in nodes:
                    if len(nodes) + 1 > max_nodes:
                        raise _AdmissionRefusal(
                            AdmissionOutcome.OVER_BOUND,
                            (AdmissionLimitation.NODES_OVER_BOUND,),
                            limitations,
                            graph_bounds.max_diagnostics,
                        )
                    nodes[resolved] = _SourceNode(
                        resolved, None, None, NodeStatus.DISCOVERED_CONTENT_MISSING
                    )
                if _enqueue_target(resolved, True):
                    progress = True
        if not progress:
            break

    # --- The LEAST-derivation depth gate (after the bounded fixed point) --
    for path, depth in best_depth.items():
        if path == ROOT_FILENAME:
            continue
        if depth > graph_bounds.max_depth:
            # A target whose only complete derivations exceed the bound
            # is a typed whole-snapshot refusal — never silent lost
            # reachability.  A known in-budget proof never fails because
            # another route is longer.
            raise _AdmissionRefusal(
                AdmissionOutcome.OVER_BOUND,
                (AdmissionLimitation.DERIVATION_DEPTH_OVER_BOUND,),
                limitations,
                graph_bounds.max_diagnostics,
            )

    return _ClosureResult(
        nodes=nodes,
        best_depth=best_depth,
        relationships=relationships,
        certificates=certificates,
        groups=groups,
        closure_diagnostics=closure_diagnostics,
    )


# --- Admission decision, canonical keys and public composition ---------------


def _key_canonical(
    namespace: BundleAdmissionNamespace,
    root_digest: str,
    authority_class: EntryClass,
    member_occurrences: tuple[str, ...],
    member_classes: tuple[MemberClass, ...],
    aggregate_source_digest: str,
    ownership_groups: tuple[OwnershipGroup, ...],
) -> bytes:
    """The canonical semantic-key payload (mirrors ``BundleKeyRecord``
    validation exactly: the same fields, the same JSON encoding)."""
    canonical = {
        "admission_version": ADMISSION_CONTRACT_VERSION,
        "graph_version": namespace.graph_version,
        "reference_version": namespace.reference_version,
        "proof_version": namespace.proof_version,
        "observation_version": namespace.observation_version,
        "mode": namespace.mode.value,
        "authority_class": authority_class.value,
        "principal": namespace.principal,
        "session": namespace.session,
        "repository": namespace.repository,
        "route": namespace.route,
        "config_fingerprint": namespace.config_fingerprint,
        "model_identity": namespace.model_identity,
        "workspace": namespace.workspace,
        "root_digest": root_digest,
        "admission_bounds": namespace.bounds.model_dump(mode="json"),
        "proof_bounds": namespace.proof_bounds.model_dump(mode="json"),
        "graph_bounds": namespace.graph_bounds.model_dump(mode="json"),
        "observation_bounds": namespace.observation_bounds.model_dump(mode="json"),
        "member_occurrences": list(member_occurrences),
        "member_classes": [m.value for m in member_classes],
        "aggregate_source_digest": aggregate_source_digest,
        "ownership_groups": [
            {
                "member_occurrence_indices": list(g.member_occurrence_indices),
                "boundary_class": g.boundary_class.value,
                "group_digest": g.group_digest,
            }
            for g in ownership_groups
        ],
    }
    return json.dumps(canonical, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _root_entry(
    namespace: BundleAdmissionNamespace,
    root_digest: str,
    root_content: str,
    root_occurrences: tuple[tuple[int, RootOccurrence], ...],
) -> BundleEntry:
    """The required first-class root entry (ROOT-ENVELOPE AUTHORITY).

    One known source occurrence at the normalized root: the exact
    extracted source bytes (repr-suppressed, invariants bind the
    lengths and digest to them) with the bounded original envelope
    provenance retained (same-root duplicates dedup as an entry).
    """
    groups = (
        OwnershipGroup(
            group_index=0,
            member_occurrence_indices=(0,),
            boundary_class=BoundaryClass.PROVEN,
            group_digest=root_digest,
        ),
    )
    canonical = _key_canonical(
        namespace,
        root_digest,
        EntryClass.ROOT_ENTRY,
        (ROOT_FILENAME,),
        (MemberClass.ELIGIBLE,),
        root_digest,
        groups,
    )
    content_key = _sha256_hex(canonical)
    key_record = BundleKeyRecord(
        mode=namespace.mode,
        authority_class=EntryClass.ROOT_ENTRY,
        principal=namespace.principal,
        session=namespace.session,
        repository=namespace.repository,
        route=namespace.route,
        config_fingerprint=namespace.config_fingerprint,
        model_identity=namespace.model_identity,
        workspace=namespace.workspace,
        root_digest=root_digest,
        reference_version=namespace.reference_version,
        admission_bounds=namespace.bounds,
        proof_bounds=namespace.proof_bounds,
        graph_bounds=namespace.graph_bounds,
        observation_bounds=namespace.observation_bounds,
        member_occurrences=(ROOT_FILENAME,),
        member_classes=(MemberClass.ELIGIBLE,),
        aggregate_source_digest=root_digest,
        ownership_groups=groups,
        content_key=content_key,
    )
    return BundleEntry(
        entry_class=EntryClass.ROOT_ENTRY,
        content_key=content_key,
        key_record=key_record,
        width=1,
        member_classes=(MemberClass.ELIGIBLE,),
        root_digest=root_digest,
        source_text=root_content,
        source_char_length=len(root_content),
        # The exact byte length is REUSED from the measured 017 root
        # occurrence (the digest already binds the copied content to
        # it): no re-encoding of the root source here.
        source_byte_length=(
            root_occurrences[0][1].byte_length
            if root_occurrences[0][1].byte_length is not None
            else len(root_content.encode("utf-8"))
        ),
        envelope_occurrences=tuple(
            RootEnvelopeOccurrence(
                request_index=request_index,
                carrier_location=occurrence.location,
                kind=occurrence.kind,
                status=occurrence.status,
                content_span=occurrence.content_span,
                envelope_span=occurrence.envelope_span,
                digest=occurrence.digest,
                byte_length=occurrence.byte_length,
                reasons=occurrence.reasons,
            )
            for request_index, occurrence in root_occurrences
        ),
    )


def _file_entry(
    namespace: BundleAdmissionNamespace,
    root_digest: str,
    proof: BundleProof,
    admitted_segment_indices: tuple[int, ...],
    best_depth: dict[str, int],
) -> BundleEntry:
    """One file-bundle entry for an admitted proven region.

    The original proof is never reindexed or refabricated: its
    complete requested members, member positions, pieces and segments
    stay untouched in the embedded provenance; the entry-local
    ownership groups and the admitted member sequence are the canonical
    key descriptor.  The admitted region is the whole bundle or ONE
    indivisible proven group (the model enforces the no-splice law).
    """
    segments = proof.segments
    admitted_set = set(admitted_segment_indices)
    admitted: list[str] = []
    classes: list[MemberClass] = []
    groups: list[OwnershipGroup] = []
    entry_local = 0
    for position, segment in enumerate(segments):
        if position not in admitted_set:
            continue
        start = entry_local
        for member_position in segment.member_positions:
            member = proof.requested_members[member_position]
            if member.normalized is None:
                raise _fixed("admitted members must be resolved paths")
            admitted.append(member.normalized)
            if member.normalized in best_depth:
                classes.append(MemberClass.ELIGIBLE)
            else:
                classes.append(MemberClass.GREEDY_BACKGROUND)
            entry_local += 1
        indices = tuple(range(start, entry_local))
        if len(segment.member_positions) == 1 and segment.member_digest is not None:
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
                raise _fixed("a singleton group is proven, never boundaryless")
            groups.append(
                OwnershipGroup(
                    group_index=len(groups),
                    member_occurrence_indices=indices,
                    boundary_class=BoundaryClass.BOUNDARYLESS,
                    group_digest=segment.digest,
                )
            )
    # The admitted region digest is REUSED from the already-proven
    # 018-b facts (the whole-bundle aggregate digest, or the single
    # admitted segment's own proven digest): no new owned copy, join
    # or digest recomputation over the source (the model re-verifies
    # the binding independently).
    if admitted_segment_indices == tuple(range(len(segments))):
        aggregate = proof.source_digest
    else:
        aggregate = segments[admitted_segment_indices[0]].digest
    canonical = _key_canonical(
        namespace,
        root_digest,
        EntryClass.FILE_BUNDLE_ENTRY,
        tuple(admitted),
        tuple(classes),
        aggregate,
        tuple(groups),
    )
    content_key = _sha256_hex(canonical)
    key_record = BundleKeyRecord(
        mode=namespace.mode,
        authority_class=EntryClass.FILE_BUNDLE_ENTRY,
        principal=namespace.principal,
        session=namespace.session,
        repository=namespace.repository,
        route=namespace.route,
        config_fingerprint=namespace.config_fingerprint,
        model_identity=namespace.model_identity,
        workspace=namespace.workspace,
        root_digest=root_digest,
        reference_version=namespace.reference_version,
        admission_bounds=namespace.bounds,
        proof_bounds=namespace.proof_bounds,
        graph_bounds=namespace.graph_bounds,
        observation_bounds=namespace.observation_bounds,
        member_occurrences=tuple(admitted),
        member_classes=tuple(classes),
        aggregate_source_digest=aggregate,
        ownership_groups=tuple(groups),
        content_key=content_key,
    )
    return BundleEntry(
        entry_class=EntryClass.FILE_BUNDLE_ENTRY,
        content_key=content_key,
        key_record=key_record,
        width=len(set(admitted)),
        member_classes=tuple(classes),
        root_digest=root_digest,
        proof=proof,
        admitted_segments=admitted_segment_indices,
    )


def _segment_all_eligible(
    proof: BundleProof, segment: BundleSegment, best_depth: dict[str, int]
) -> bool:
    """Every member occurrence of the segment is independently
    root-reachable (eligibility, not acquisition)."""
    for member_position in segment.member_positions:
        member = proof.requested_members[member_position]
        if member.normalized is None or member.normalized not in best_depth:
            return False
    return True


def _admission_plans(
    proof: BundleProof,
    mode: AdmissionMode,
    best_depth: dict[str, int],
) -> tuple[tuple[int, ...], ...]:
    """The admission truth table (the order's binding rows).

    * all members eligible: the complete whole bundle (both modes);
    * mixed eligible/background: greedy admits the whole when at least
      one member is eligible; lean admits each independently proven
      all-eligible group (a singleton segment, or a multi-member
      segment all of whose members are eligible) as its own entry —
      never concatenating around a background member;
    * zero eligible: neither mode admits.
    """
    segments = proof.segments
    member_flags = [
        member.normalized is not None and member.normalized in best_depth
        for member in proof.requested_members
    ]
    if all(member_flags):
        return (tuple(range(len(segments))),)
    if any(member_flags) and mode is AdmissionMode.GREEDY:
        return (tuple(range(len(segments))),)
    if mode is AdmissionMode.LEAN:
        return tuple(
            (position,)
            for position, segment in enumerate(segments)
            if _segment_all_eligible(proof, segment, best_depth)
        )
    return ()


def _admission_pass(
    requests: tuple[GraphRequest, ...],
    namespace: BundleAdmissionNamespace,
) -> BundleAdmissionSnapshot:
    """One bounded batch of decoded requests to one admission snapshot.

    The composition is: the original-input collection phase (017
    re-observation, the 018-a root binding, the shared 018-b proof
    pass on ONE source ledger), the new AND/OR raw-reference closure
    (one shared work ledger, the ACTUAL effective node/edge/document/
    candidate ceilings), the lean/greedy truth-table decision with
    structural content keys, the complete reverse member-path index
    and the source-version observations retained independently of
    admission.  No bound refusal retains partial admission.
    """
    request_count = len(requests)
    graph_bounds = namespace.graph_bounds
    work = _AdmissionWorkCounter(graph_bounds.max_work_units)
    documents = _ScanBudgetCounter(graph_bounds.max_documents)
    candidate_total = _ScanBudgetCounter(graph_bounds.max_reference_candidates_total)

    try:
        facts = _admission_collect(requests, namespace)
    except _AdmissionRefusal as refusal:
        return _refuse_admission(namespace, refusal, request_count)
    try:
        closure = _admission_closure(facts, work, documents, candidate_total)
        return _admission_finalize(facts, closure, namespace, work, documents, candidate_total)
    except _AdmissionRefusal as refusal:
        return _refuse_admission(
            namespace,
            refusal,
            request_count,
            work.units,
            documents.count,
            candidate_total.count,
        )


def _admission_finalize(
    facts: _AdmissionFacts,
    closure: _ClosureResult,
    namespace: BundleAdmissionNamespace,
    work: _AdmissionWorkCounter,
    documents: _ScanBudgetCounter,
    candidate_total: _ScanBudgetCounter,
) -> BundleAdmissionSnapshot:
    """The admission/index phase (structural interning by content
    key, the complete reverse member-path index, the source-version
    observations, certificates, relationships and the reachable
    eligibility / offgraph node facts).

    Runs under the SAME shared work ledger as the closure: every
    actual association attempt and every bound check is charged
    before the work/retention it gates, and any later resource
    failure is a typed whole-empty snapshot refusal (never a
    private exception out of the public API).
    """
    # --- The required first-class root entry ---------------------------
    root_digest = facts.root_digest
    root_entry = _root_entry(namespace, root_digest, facts.root_content, facts.root_occurrences)

    # --- Admission decision (structural interning by content key) ------
    # Complete reverse member-path index: every ACTUAL association
    # attempt (repeated member occurrences, interned duplicate entries
    # and background members included) charges the ONE shared work
    # ledger and counts against the ACTUAL admission association
    # ceiling BEFORE the rows deduplicate the content keys (at-limit
    # is at-limit; the first crossing attempt is a fixed typed
    # refusal, never a post-dedup discard).
    path_keys: dict[str, set[str]] = {}
    attempts = 0

    def _associate(path: str, key: str) -> None:
        nonlocal attempts
        if not work.charge():
            raise _AdmissionRefusal(
                AdmissionOutcome.OVER_BOUND,
                (AdmissionLimitation.WORK_UNITS_EXHAUSTED,),
                facts.ordered_limitations,
                namespace.bounds.max_diagnostics,
            )
        if attempts + 1 > namespace.bounds.max_reverse_associations:
            raise _AdmissionRefusal(
                AdmissionOutcome.OVER_BOUND,
                (AdmissionLimitation.REVERSE_ASSOCIATIONS_OVER_BOUND,),
                facts.ordered_limitations,
                namespace.bounds.max_diagnostics,
            )
        attempts += 1
        path_keys.setdefault(path, set()).add(key)

    entries: dict[str, BundleEntry] = {}
    member_occurrences_charged = 1  # the required root member occurrence
    unproven_diagnostic = False
    _associate(ROOT_FILENAME, root_entry.content_key)
    for proof in facts.bundles:
        admitted_any = False
        for admitted_segments in _admission_plans(proof, namespace.mode, closure.best_depth):
            entry = _file_entry(
                namespace, root_digest, proof, admitted_segments, closure.best_depth
            )
            # Every represented member OCCURRENCE of every admitted
            # plan is an actual association attempt, BEFORE the
            # content-key interning dedup (duplicates keep their
            # charged units; the rows dedup afterwards).
            for occurrence_path in entry.key_record.member_occurrences:
                _associate(occurrence_path, entry.content_key)
            if entry.content_key in entries:
                admitted_any = True  # interned: the same key/entry identity
                continue
            # Budget checks BEFORE retention (at-limit stays at-limit).
            if 1 + len(entries) + 1 > namespace.bounds.max_entries:
                raise _AdmissionRefusal(
                    AdmissionOutcome.OVER_BOUND,
                    (AdmissionLimitation.ENTRIES_OVER_BOUND,),
                    facts.ordered_limitations,
                    namespace.bounds.max_diagnostics,
                )
            occurrences = len(entry.key_record.member_occurrences)
            if member_occurrences_charged + occurrences > namespace.bounds.max_member_occurrences:
                raise _AdmissionRefusal(
                    AdmissionOutcome.OVER_BOUND,
                    (AdmissionLimitation.MEMBER_OCCURRENCES_OVER_BOUND,),
                    facts.ordered_limitations,
                    namespace.bounds.max_diagnostics,
                )
            entries[entry.content_key] = entry
            member_occurrences_charged += occurrences
            admitted_any = True
        if not admitted_any:
            unproven_diagnostic = True

    path_associations = tuple(
        PathAssociation(
            scoped_key=namespace.scoped_key,
            path=path,
            content_keys=tuple(sorted(keys)),
            is_root=path == ROOT_FILENAME,
        )
        for path, keys in sorted(path_keys.items())
    )

    # --- Source-version observations (independent of admission) --------
    observations: list[SourceVersionObservation] = []
    for proof in facts.bundles:
        proven: dict[str, str] = {}
        for segment in proof.segments:
            if segment.member_digest is None:
                continue  # no single-occurrence proof: never invented
            member = proof.requested_members[segment.member_positions[0]]
            member_path = member.normalized
            if member_path is not None and member_path != ROOT_FILENAME:
                proven.setdefault(member_path, segment.member_digest)
        counts: dict[str, int] = {}
        for member in proof.requested_members:
            if member.normalized is not None:
                counts[member.normalized] = counts.get(member.normalized, 0) + 1
        for path in sorted(proven):
            observations.append(
                SourceVersionObservation(
                    scoped_key=namespace.scoped_key,
                    path=path,
                    content_digest=proven[path],
                    request_index=proof.request_index,
                    carrier_location=proof.result_location,
                    occurrence_count=counts[path],
                )
            )
    version_observations = tuple(
        sorted(
            observations,
            key=lambda o: (o.path, o.request_index, o.carrier_location),
        )
    )

    # --- Group certificates and ordinary relationships ------------------
    certificate_records = tuple(
        GroupCertificate(
            admission_version=ADMISSION_CONTRACT_VERSION,
            scoped_key=namespace.scoped_key,
            root_digest=root_digest,
            source_digest=certificate.group.digest,
            request_index=certificate.group.proof.request_index,
            carrier_location=certificate.group.proof.result_location,
            segment_index=certificate.group.segment_index,
            supplier_occurrences=certificate.group.supplier_occurrences,
            syntax=certificate.candidate.syntax,
            evidence_span=certificate.candidate.target_char_span,
            target_path=certificate.target_path,
            derivation_depth=certificate.depth,
        )
        for certificate in sorted(
            closure.certificates,
            key=lambda c: (
                c.group.digest,
                c.group.proof.request_index,
                c.group.proof.result_location,
                c.group.segment_index,
                c.candidate.syntax.value,
                c.candidate.target_char_span.start,
                c.candidate.target_char_span.end,
                c.target_path,
            ),
        )
    )
    relationship_records: list[OrdinaryRelationship] = []
    for (referring, target), occurrence_count in sorted(closure.relationships.items()):
        # The referrer of a retained relationship is always an acquired,
        # scanned node with a proven digest; if that invariant were ever
        # broken the relationship is dropped (the model refuses "" digests).
        referring_digest = closure.nodes[referring].digest
        if referring_digest is None:
            continue
        relationship_records.append(
            OrdinaryRelationship(
                scoped_key=namespace.scoped_key,
                referring_path=referring,
                referring_digest=referring_digest,
                target_path=target,
                occurrence_count=occurrence_count,
            )
        )

    # --- Eligibility nodes and unresolved-origin records ----------------
    # Eligibility means an independent root derivation (a finite
    # AND/OR least derivation from the root): acquired sources that
    # no root derivation reaches are retained separately as offgraph
    # provenance (their outgoing references never expanded reach).
    eligibility_nodes = tuple(
        EligibilityNode(
            scoped_key=namespace.scoped_key,
            path=path,
            status=node.status,
            source_digest=node.digest,
        )
        for path, node in sorted(closure.nodes.items())
        if path in closure.best_depth
    )
    offgraph_nodes = tuple(
        OffgraphSourceNode(
            scoped_key=namespace.scoped_key,
            path=path,
            status=node.status,
            source_digest=node.digest,
        )
        for path, node in sorted(closure.nodes.items())
        if path not in closure.best_depth
    )

    # --- Every original accepted 018-b proof, retained verbatim --------
    # Independent of semantic entry interning: all exact original
    # carriers, spans, piece IDs and positions are retained in a
    # separate bounded occurrence provenance (the proof pass already
    # bounded the retained count under the ACTUAL max_bundles).
    source_proofs = tuple(
        sorted(
            facts.bundles,
            key=lambda b: (b.request_index, b.call_id, b.result_location),
        )
    )
    origin_records: list[UnresolvedOriginRecord] = []
    for group in closure.groups:
        remaining = [gc.candidate for gc in group.candidates if gc.state != "certificate"]
        if not remaining:
            continue
        origin_records.append(
            UnresolvedOriginRecord(
                scoped_key=namespace.scoped_key,
                source_digest=group.digest,
                possible_origins=group.possible_origins,
                candidates=tuple(remaining),
                request_index=group.proof.request_index,
                carrier_location=group.proof.result_location,
                segment_index=group.segment_index,
            )
        )
    unresolved_origins = tuple(
        sorted(
            origin_records,
            key=lambda r: (
                r.source_digest,
                r.request_index,
                r.carrier_location,
                r.segment_index,
                r.possible_origins,
            ),
        )
    )

    # --- Total emitted diagnostics (bounded before retention) -----------
    diagnostics = tuple(_PROOF_BUDGET_MAP[d] for d in facts.diagnostics) + tuple(
        closure.closure_diagnostics
    )
    if unproven_diagnostic:
        if len(diagnostics) + len(facts.ordered_limitations) + 1 > namespace.bounds.max_diagnostics:
            raise _AdmissionRefusal(
                AdmissionOutcome.OVER_BOUND,
                (AdmissionLimitation.DIAGNOSTICS_FULL,),
                facts.ordered_limitations,
                namespace.bounds.max_diagnostics,
            )
        diagnostics = diagnostics + (AdmissionLimitation.CANDIDATE_UNPROVEN,)
    if len(diagnostics) + len(facts.ordered_limitations) > namespace.bounds.max_diagnostics:
        # Defensive: the incremental bound already enforces this total.
        raise _AdmissionRefusal(
            AdmissionOutcome.OVER_BOUND,
            (AdmissionLimitation.DIAGNOSTICS_FULL,),
            facts.ordered_limitations,
            namespace.bounds.max_diagnostics,
        )

    return BundleAdmissionSnapshot(
        namespace=namespace,
        outcome=AdmissionOutcome.COMPLETE,
        root_entry=root_entry,
        entries=tuple(sorted(entries.values(), key=lambda e: e.content_key)),
        certificates=certificate_records,
        path_associations=path_associations,
        version_observations=version_observations,
        ordinary_relationships=tuple(relationship_records),
        eligibility_nodes=eligibility_nodes,
        offgraph_nodes=offgraph_nodes,
        source_proofs=source_proofs,
        unresolved_origins=unresolved_origins,
        conflicts=(),
        diagnostics=diagnostics,
        observation_limitations=facts.ordered_limitations,
        request_count=len(facts.requests),
        entries_retained=1 + len(entries),
        member_occurrences_charged=member_occurrences_charged,
        reverse_association_attempts=attempts,
        work_units=work.units,
        extra_documents_inspected=documents.count,
        extra_candidates_inspected=candidate_total.count,
        root_path=ROOT_FILENAME,
        root_digest=root_digest,
    )


def observe_bundle_admission_batch(
    requests: tuple[GraphRequest, ...],
    namespace: BundleAdmissionNamespace,
    bounds: BundleAdmissionBounds | None = None,
) -> BundleAdmissionSnapshot:
    """One bounded batch of decoded requests to one bundle-admission
    snapshot (objective 018-c).

    The entry takes exactly one namespace (mixed-namespace batches are
    structurally impossible; the record's scoped keys bind it).
    ``bounds``, when supplied, must equal the namespace's effective
    admission bounds.  The 017 re-observation pass always runs under
    the ACTUAL effective ``ObservationBounds`` carried by the
    namespace, and the source/path/candidate budgets under the ACTUAL
    effective ``GraphBounds``.  No caller flag, hash, fabricated member
    boundary or supplied snapshot creates source authority; re-
    derivation starts from the original API payloads.
    """
    if bounds is not None and bounds != namespace.bounds:
        raise _fixed("bounds must equal the namespace effective bounds")
    return _admission_pass(requests, namespace)


def observe_bundle_admission(
    payload: dict[str, Any],
    namespace: BundleAdmissionNamespace,
    *,
    endpoint: str,
    context: PathContext | None = None,
    bounds: BundleAdmissionBounds | None = None,
) -> BundleAdmissionSnapshot:
    """One decoded request to one bundle-admission snapshot.

    The public single-request form: the batch law applies with
    ``request_count`` 1.  ``endpoint`` is the explicit validated
    endpoint context; ``context`` the evidenced client-workspace
    context (``None`` allowed; the derived-workspace law applies).
    """
    request = GraphRequest(payload=payload, endpoint=endpoint, context=context)
    return observe_bundle_admission_batch((request,), namespace, bounds=bounds)

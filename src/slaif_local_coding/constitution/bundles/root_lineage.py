"""Versioned root-authority lineage state machine (objective 018-h;
INERT).

``ROOT_LINEAGE_CONTRACT_VERSION = "cache-root-lineage/v1"``;
``ROOT_LINEAGE_POLICY_VERSION = "root-lineage-policy/v1"``.

ONE inert versioned ROOT-LINEAGE/ORIGINAL-OBSERVATION composition:
bootstrap from the accepted legitimate effective Responses AGENTS
envelope (strict old root law, no refresh at bootstrap), trusted
original-observation transitions that earn genuine same-root versions
from original complete singleton root reads plus trusted issuance/
receipt causal evidence, and a bounded pure current-root selection
over the causal MAXIMAL authoritative root facts.

Laws implemented here (the records live in
``root_lineage_models.py``):

- SOURCE acquisition and AUTHORITY are separate.  A genuine refresh
  authority witness additionally has an ACTUAL matching INTERNAL
  issuance/receipt with the accepted frozen parent frontier and a
  PROVEN causal ancestry to the bootstrap root fact (S1: flags are
  re-derived for ALL retained facts from the ACTUAL new D state
  after EVERY accepted D transition -- a late issuance/receipt, even
  a NONROOT one, can earn authority; a single receipt row never
  grants flags).
- Read ID novelty, receipt arrival, HTTP positions, digests,
  revisions and body flags are never clocks or trust.  Construction
  is not authentication.
- Retained complete but unissued/unanchored root reads stay UNPROVEN
  source (fixed typed limitation exposure), never current authority;
  the relaxed envelope law's known-source context is ONLY the
  bootstrap anchor and the actually earned authoritative root
  sources -- retained complete bytes alone never justify an
  envelope.
- Every public boundary validates the ACTUAL state under the ONE
  outer ledger BEFORE any positive interpretation or D work:
  retention, source provenance, the anchor law against the full
  actual D state, and the DERIVED flags re-derived from the actual
  issuance/anchoring/DAG (stored positive bits are never trusted;
  an incoherent binding is refused, never minted).  The fixed O(1)
  shape/scope/CAS/key/version fences run before any unvalidated
  fuel or wide walk, and the exact validation domain reason is
  always propagated (never a blanket malformed label for a
  capacity/work failure).  The warning-suppressed dump keeps a
  malformed field private on the refusal path.
- Old/shifted replay is a pure no-op (FIRST provenance, no revision
  advance, no rollback); an unknown changed envelope WITHOUT
  independent accepted root-read authority is a fixed whole-
  transition root-authority refusal preserving the EXACT prior H
  state (the same-batch independently earned authoritative root read
  establishes the matching envelope's known-source status
  atomically; the envelope itself grants no ordering).
- Select current authority from the causal maximal authoritative
  root facts using ONLY frozen transitive parent evidence; distinct
  incomparable equal-byte witnesses are compatible and ALL maximal
  originals are retained; differing maximal sources are an explicit
  ROOT_CONTENT_CONFLICT with NO selected source; a child of one
  branch cannot resolve the other, a genuine child of ALL relevant
  branches can; no lexical/receipt winner.

Resource law: ONE outer H ledger covers the full new operation
(early gates, actual observation/collection, old-state validation,
D transition/argument/result/DAG work, lineage acquisition/
ancestry/maxima/source/provenance/index/output work); the inherited
D local per-transition ledger keeps its own domain and ceiling.
Every actual visit/comparison/association/copy/sort charges BEFORE
the operation; honest conservative reservations precede inherited
bounded work.  Every refusal/replay preserves the EXACT prior H
state; one accepted state change advances the H revision exactly
once.

It is pure and inert: no pipeline activation, no RAM service/locks,
no compiler, no disk, no HTTP/SSE observer and no new metrics.
"""

from __future__ import annotations

from collections.abc import Callable

from .bundle_admission_models import ADMISSION_CONTRACT_VERSION
from .bundle_proof import _HOuterOverflow
from .bundle_proof_models import (
    BUNDLE_PROOF_CONTRACT_VERSION,
    BundleMarkerFact,
    BundleMarkerRole,
    BundlePiece,
    BundleProof,
    BundleProofBounds,
    BundleProofKind,
    BundleSegment,
    BundleSourceRole,
    BundleSurface,
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
    MAX_REVISION,
    CausalHistoryLimitation,
    CausalHistoryNamespace,
    CausalHistoryOutcome,
    CausalHistoryState,
    CausalHistoryTransition,
    CompletedReadOccurrence,
    HistoryBounds,
    ResultFingerprintRecord,
    RootAnchor,
    validate_causal_history_state,
)
from .compound_reads import READ_PLAN_GRAMMAR
from .graph_models import (
    _HEX_DIGITS,
    GRAPH_CONTRACT_VERSION,
    REFERENCE_GRAMMAR,
    ROOT_FILENAME,
    GraphBounds,
    _fixed,
    _sha256_hex,
)
from .graph_observation import GraphRequest
from .literal_loops import LOOP_GRAMMAR
from .observation_models import (
    EMPTY_SOURCE_SHA256,
    OBSERVER_VERSION,
    READ_GRAMMAR,
    CharSpan,
    NormalizedPath,
    ObservationBounds,
)
from .root_lineage_models import (
    ROOT_LINEAGE_CONTRACT_VERSION,
    ROOT_LINEAGE_POLICY_VERSION,
    EnvelopeRootProvenance,
    ReadRootProvenance,
    RootLineageBounds,
    RootLineageFact,
    RootLineageLimitation,
    RootLineageNamespace,
    RootLineageOutcome,
    RootLineageState,
    RootLineageTransition,
    RootSelectionOutcome,
    RootSelectionResult,
    _provenance_key,
    admission_bounds_shape_ok,
    graph_bounds_shape_ok,
    history_bounds_shape_ok,
    observation_bounds_shape_ok,
    proof_bounds_shape_ok,
    root_lineage_bounds_shape_ok,
    root_lineage_ns_scalar_shape_ok,
)

# --- Outcome / limitation maps (mirrored 1:1, exact names) -------------

_H_OUTCOME_MAP: dict[CausalHistoryOutcome, RootLineageOutcome] = {
    CausalHistoryOutcome.ACCEPTED: RootLineageOutcome.ACCEPTED,
    CausalHistoryOutcome.REPLAYED: RootLineageOutcome.REPLAYED,
    CausalHistoryOutcome.REFUSED_CAS_MISMATCH: RootLineageOutcome.REFUSED_CAS_MISMATCH,
    CausalHistoryOutcome.REFUSED_FOREIGN_SCOPE: RootLineageOutcome.REFUSED_FOREIGN_SCOPE,
    CausalHistoryOutcome.REFUSED_NO_ROOT: RootLineageOutcome.REFUSED_NO_ROOT,
    CausalHistoryOutcome.REFUSED_ROOT_CONFLICT: RootLineageOutcome.REFUSED_ROOT_CONFLICT,
    CausalHistoryOutcome.REFUSED_VERSION_CONFLICT: RootLineageOutcome.REFUSED_VERSION_CONFLICT,
    CausalHistoryOutcome.REFUSED_CONFLICT: RootLineageOutcome.REFUSED_CONFLICT,
    CausalHistoryOutcome.REFUSED_UNKNOWN_PARENT: RootLineageOutcome.REFUSED_UNKNOWN_PARENT,
    CausalHistoryOutcome.REFUSED_CYCLE: RootLineageOutcome.REFUSED_CYCLE,
    CausalHistoryOutcome.REFUSED_OVER_BOUND: RootLineageOutcome.REFUSED_OVER_BOUND,
}

_H_LIMITATION_MAP: dict[CausalHistoryLimitation, RootLineageLimitation] = {
    CausalHistoryLimitation.NO_ROOT: RootLineageLimitation.NO_ROOT,
    CausalHistoryLimitation.COMPETING_ROOTS: RootLineageLimitation.COMPETING_ROOTS,
    CausalHistoryLimitation.WORKSPACE_MISMATCH: RootLineageLimitation.WORKSPACE_MISMATCH,
    CausalHistoryLimitation.ROOT_CONTEXT_MISMATCH: RootLineageLimitation.ROOT_CONTEXT_MISMATCH,
    CausalHistoryLimitation.WORKSPACE_UNPROVEN: RootLineageLimitation.WORKSPACE_UNPROVEN,
    CausalHistoryLimitation.VERSION_UNSUPPORTED: RootLineageLimitation.VERSION_UNSUPPORTED,
    CausalHistoryLimitation.BATCH_OVER_BOUND: RootLineageLimitation.BATCH_OVER_BOUND,
    CausalHistoryLimitation.DIAGNOSTICS_FULL: RootLineageLimitation.DIAGNOSTICS_FULL,
    CausalHistoryLimitation.ARGUMENTS_UNSUPPORTED: RootLineageLimitation.ARGUMENTS_UNSUPPORTED,
    CausalHistoryLimitation.ARGUMENTS_MALFORMED_UNICODE: (
        RootLineageLimitation.ARGUMENTS_MALFORMED_UNICODE
    ),
    CausalHistoryLimitation.ARGUMENTS_OVER_BOUND: RootLineageLimitation.ARGUMENTS_OVER_BOUND,
    CausalHistoryLimitation.CALL_ID_MISSING: RootLineageLimitation.CALL_ID_MISSING,
    CausalHistoryLimitation.CALL_ID_MALFORMED: RootLineageLimitation.CALL_ID_MALFORMED,
    CausalHistoryLimitation.FRONTIER_OVER_BOUND: RootLineageLimitation.FRONTIER_OVER_BOUND,
    CausalHistoryLimitation.FRONTIER_CONFLICT: RootLineageLimitation.FRONTIER_CONFLICT,
    CausalHistoryLimitation.ISSUANCE_CONFLICT: RootLineageLimitation.ISSUANCE_CONFLICT,
    CausalHistoryLimitation.RESULT_CONFLICT: RootLineageLimitation.RESULT_CONFLICT,
    CausalHistoryLimitation.RECEIPT_BINDING_MISMATCH: (
        RootLineageLimitation.RECEIPT_BINDING_MISMATCH
    ),
    CausalHistoryLimitation.RECEIPT_UNKNOWN_PARENT: (RootLineageLimitation.RECEIPT_UNKNOWN_PARENT),
    CausalHistoryLimitation.RECEIPT_CYCLE: RootLineageLimitation.RECEIPT_CYCLE,
    CausalHistoryLimitation.SEAM_CONFLICT: RootLineageLimitation.SEAM_CONFLICT,
    CausalHistoryLimitation.BUNDLES_OVER_BOUND: RootLineageLimitation.BUNDLES_OVER_BOUND,
    CausalHistoryLimitation.SOURCE_OVER_BOUND: RootLineageLimitation.SOURCE_OVER_BOUND,
    CausalHistoryLimitation.TOTAL_SOURCE_OVER_BOUND: (
        RootLineageLimitation.TOTAL_SOURCE_OVER_BOUND
    ),
    CausalHistoryLimitation.MEMBERS_OVER_BOUND: RootLineageLimitation.MEMBERS_OVER_BOUND,
    CausalHistoryLimitation.SEGMENTS_OVER_BOUND: RootLineageLimitation.SEGMENTS_OVER_BOUND,
    CausalHistoryLimitation.MARKER_OVER_BOUND: RootLineageLimitation.MARKER_OVER_BOUND,
    CausalHistoryLimitation.MARKER_SEARCH_OVER_BOUND: (
        RootLineageLimitation.MARKER_SEARCH_OVER_BOUND
    ),
    CausalHistoryLimitation.MARKER_EMPTY: RootLineageLimitation.MARKER_EMPTY,
    CausalHistoryLimitation.MARKER_MISSING: RootLineageLimitation.MARKER_MISSING,
    CausalHistoryLimitation.MARKER_DUPLICATE: RootLineageLimitation.MARKER_DUPLICATE,
    CausalHistoryLimitation.MARKER_ORDER: RootLineageLimitation.MARKER_ORDER,
    CausalHistoryLimitation.MARKER_OVERLAP: RootLineageLimitation.MARKER_OVERLAP,
    CausalHistoryLimitation.PLAN_UNSUPPORTED: RootLineageLimitation.PLAN_UNSUPPORTED,
    CausalHistoryLimitation.MEMBER_UNRESOLVED: RootLineageLimitation.MEMBER_UNRESOLVED,
    CausalHistoryLimitation.MEMBER_PATH_OVER_BOUND: (RootLineageLimitation.MEMBER_PATH_OVER_BOUND),
    CausalHistoryLimitation.SEGMENT_UNEXPLAINED: RootLineageLimitation.SEGMENT_UNEXPLAINED,
    CausalHistoryLimitation.OUTPUT_INCONSISTENT: RootLineageLimitation.OUTPUT_INCONSISTENT,
    CausalHistoryLimitation.SOURCE_CONFLICT: RootLineageLimitation.SOURCE_CONFLICT,
    CausalHistoryLimitation.MALFORMED_BINDING: RootLineageLimitation.MALFORMED_BINDING,
    CausalHistoryLimitation.ISSUANCES_OVER_BOUND: RootLineageLimitation.ISSUANCES_OVER_BOUND,
    CausalHistoryLimitation.OCCURRENCES_OVER_BOUND: (RootLineageLimitation.OCCURRENCES_OVER_BOUND),
    CausalHistoryLimitation.CAUSAL_LINKS_OVER_BOUND: (
        RootLineageLimitation.CAUSAL_LINKS_OVER_BOUND
    ),
    CausalHistoryLimitation.RESULTS_OVER_BOUND: RootLineageLimitation.RESULTS_OVER_BOUND,
    CausalHistoryLimitation.RETAINED_MEMBERS_OVER_BOUND: (
        RootLineageLimitation.RETAINED_MEMBERS_OVER_BOUND
    ),
    CausalHistoryLimitation.RETAINED_PIECES_OVER_BOUND: (
        RootLineageLimitation.RETAINED_PIECES_OVER_BOUND
    ),
    CausalHistoryLimitation.RETAINED_SOURCE_BYTES_OVER_BOUND: (
        RootLineageLimitation.RETAINED_SOURCE_BYTES_OVER_BOUND
    ),
    CausalHistoryLimitation.WORK_UNITS_OVER_BOUND: (RootLineageLimitation.WORK_UNITS_OVER_BOUND),
    CausalHistoryLimitation.REVISION_OVERFLOW: RootLineageLimitation.REVISION_OVERFLOW,
    CausalHistoryLimitation.REPLAY_POSITION_SHIFTED: (
        RootLineageLimitation.REPLAY_POSITION_SHIFTED
    ),
}


class _HOuter:
    """ONE charged H outer work ledger over the ENTIRE new operation.

    ``unit`` charges ONE unit BEFORE the work it gates and reports
    whether the charge is allowed: a charge that would cross the
    ACTUAL ``RootLineageBounds.max_total_work_units`` is refused
    BEFORE the crossing operation runs (the crossing is recorded on
    ``exhausted`` so the D-coupled ledgers and the composition map
    it to the fixed H over-bound refusal).  Cumulative and NEVER
    reset within the operation; the D local ledger keeps its own
    independent ceiling."""

    __slots__ = ("work_cap", "work_spent", "exhausted")

    def __init__(self, work_cap: int) -> None:
        self.work_cap = work_cap
        self.work_spent = 0
        self.exhausted = False

    def unit(self) -> bool:
        if self.exhausted:
            return False
        if self.work_spent + 1 > self.work_cap:
            self.exhausted = True
            return False
        self.work_spent += 1
        return True

    def units(self, n: int) -> bool:
        """Reserve n work units BEFORE the operation they bound (each
        unit charges individually so the crossing unit refuses)."""
        for _ in range(n):
            if not self.unit():
                return False
        return True


#: Honest conservative CONSTRUCTOR reservations (H-V2-4),
#: charged BEFORE the actual model constructor/copy runs (the
#: nested (re)validation walks over the closed field set):
_FACT_BUILD_UNITS = 24  # one RootLineageFact + its nested provenance
_FACT_COPY_UNITS = 4  # one model_copy field merge (no revalidation)
_STATE_BUILD_UNITS = 4  # RootLineageState fixed base
_STATE_FACT_UNITS = 24  # per retained fact (nested revalidation walk)
_TRANSITION_BUILD_UNITS = 8  # RootLineageTransition fixed base
_RESULT_BUILD_UNITS = 8  # RootSelectionResult fixed base
_RESULT_FACT_UNITS = 4  # per witness fact (InstanceOf identity + key)


class _CoupledUnit:
    """ONE coupled work unit over the shared ledger plus the local
    hard ceiling (standalone validator use is never unbounded)."""

    __slots__ = ("work", "budget", "spent")

    def __init__(self, work: _UnitLedger | None, budget: int) -> None:
        self.work = work
        self.budget = budget
        self.spent = 0

    def unit(self) -> bool:
        if self.spent + 1 > self.budget:
            return False
        self.spent += 1
        if self.work is None:
            return True
        return self.work.unit()

    def units(self, n: int) -> bool:
        """Reserve n work units BEFORE the operations they bound
        (each unit charges individually so the crossing unit
        refuses)."""
        for _ in range(n):
            if not self.unit():
                return False
        return True


class _BadUtf8(ValueError):
    """An isolated surrogate reached by the no-copy UTF-8 byte walk:
    the source is unencodable BEFORE any owned copy can raise."""


def _utf8_byte_length_range(
    text: str,
    start: int,
    end: int,
    cap: int,
    charge: Callable[[], bool],
) -> int | None:
    """Charged no-copy UTF-8 byte-length walk with early exit.

    Every character inspection charges the ledger BEFORE it; a
    crossing returns None (the caller maps it to
    WORK_UNITS_OVER_BOUND).  An isolated surrogate raises the fixed
    ``_BadUtf8`` (the caller maps it to MALFORMED_BINDING) BEFORE
    the owned encode copy can ever raise.  Returns the exact byte
    length, or ``cap + 1`` the moment the running total would cross
    the cap (no unbounded precursor)."""
    total = 0
    for index in range(start, end):
        if not charge():
            return None
        code = ord(text[index])
        if 0xD800 <= code <= 0xDFFF:
            raise _BadUtf8()
        if code < 0x80:
            total += 1
        elif code < 0x800:
            total += 2
        elif code < 0x10000:
            total += 3
        else:
            total += 4
        if total > cap:
            return cap + 1
    return total


def _is_singleton_root_read(
    occ: CompletedReadOccurrence, charge: Callable[[], bool]
) -> bool | None:
    """The S3 explicit singleton whole-source root-read filter
    (charged BEFORE each actual comparison, duplicates and skips
    included).

    A completed occurrence is a retained root-source candidate ONLY
    for a complete whole singleton read of the EXACT normalized root
    path: one requested member (AGENTS.md), one attributable proven
    segment covering the complete source at position (0,) with a
    non-None member digest.  Returns ``True``/``False`` for the
    eligibility decision, or ``None`` when a charge was refused (the
    caller maps it to WORK_UNITS_OVER_BOUND)."""
    proof = occ.proof
    if not charge():
        return None
    if len(proof.requested_members) != 1:
        return False
    if not charge():
        return None
    member = proof.requested_members[0]
    if member.normalized != ROOT_FILENAME:
        return False
    if not charge():
        return None
    if len(proof.segments) != 1:
        return False
    segment = proof.segments[0]
    if not charge():
        return None
    if segment.member_positions != (0,) or segment.member_digest is None:
        return False
    if not charge():
        return None
    return segment.byte_length == proof.source_byte_length


def _h_anchor_integrity(
    anchor: RootAnchor,
    g_bounds: GraphBounds,
    h_bounds: RootLineageBounds,
    workspace: str | None,
    ledger: _CoupledUnit,
) -> bool | None:
    """Fresh charged validation of the ACTUAL retained root anchor
    (the accepted F anchor law, H-owned under the ONE outer).

    ``model_copy``/``model_construct`` bypass the record validators,
    so EVERY actual field is freshly validated, each check charged:
    FIRST the field SHAPES -- root_text a str, root_digest a 64-hex
    str, workspace an absolute 1..1024 control-character-free str,
    location a 1..1024 control-character-free str,
    first_request_index and source_byte_length integral (non-bool)
    nonnegative ints, and the content/envelope spans CharSpans with
    integral (non-bool) nonnegative coordinates (the content span
    exactly covers the root text; the envelope span, when present,
    contains it) -- so no len()/comparison below can ever hit a
    wrong-type field; THEN the O(1) character count against the
    ACTUAL single-source byte cap AND the retained-root byte cap
    BEFORE any character inspection (bytes are never fewer than
    characters, so an over-count root refuses without ANY character
    inspection); the actual byte length is then prefetched by a
    charged no-copy walk with an early exit at the effective cap
    that also refuses an unencodable (isolated-surrogate) source
    BEFORE the owned encode copy; the digest is re-checked from that
    copy; and the workspace is compared to the ACTUAL namespace
    workspace when supplied.  Returns True when coherent, False when
    the binding is malformed (the caller maps it to
    MALFORMED_BINDING), or None when a charge was refused (the
    caller maps it to WORK_UNITS_OVER_BOUND)."""
    if not ledger.unit():
        return None
    if not isinstance(anchor.root_text, str):
        return False
    if not ledger.unit():
        return None
    if not _hex64_ok(anchor.root_digest):
        return False
    if not ledger.unit():
        return None
    if (
        not isinstance(anchor.workspace, str)
        or not 1 <= len(anchor.workspace) <= 1024
        or not anchor.workspace.startswith("/")
        or any(ord(c) < 0x20 or ord(c) == 0x7F or c.isspace() for c in anchor.workspace)
    ):
        return False
    if not ledger.unit():
        return None
    if (
        not isinstance(anchor.location, str)
        or not 1 <= len(anchor.location) <= 1024
        or any(ord(c) < 0x20 or ord(c) == 0x7F for c in anchor.location)
    ):
        return False
    if not ledger.unit():
        return None
    if (
        not isinstance(anchor.first_request_index, int)
        or isinstance(anchor.first_request_index, bool)
        or anchor.first_request_index < 0
    ):
        return False
    if not ledger.unit():
        return None
    if (
        not isinstance(anchor.source_byte_length, int)
        or isinstance(anchor.source_byte_length, bool)
        or anchor.source_byte_length < 0
    ):
        return False
    if not ledger.unit():
        return None
    span = anchor.content_span
    if (
        not isinstance(span, CharSpan)
        or not isinstance(span.start, int)
        or isinstance(span.start, bool)
        or not isinstance(span.end, int)
        or isinstance(span.end, bool)
        or span.start < 0
        or span.end < span.start
        or span.end - span.start != len(anchor.root_text)
    ):
        return False
    if not ledger.unit():
        return None
    envelope = anchor.envelope_span
    if envelope is not None and (
        not isinstance(envelope, CharSpan)
        or not isinstance(envelope.start, int)
        or isinstance(envelope.start, bool)
        or not isinstance(envelope.end, int)
        or isinstance(envelope.end, bool)
        or envelope.start < 0
        or envelope.end < envelope.start
        or envelope.start > span.start
        or span.end > envelope.end
    ):
        return False
    cap = min(g_bounds.max_single_source_bytes, h_bounds.max_retained_root_source_bytes)
    if not ledger.unit():
        return None
    if len(anchor.root_text) > cap:
        return False
    if not ledger.unit():
        return None
    try:
        actual_bytes = _utf8_byte_length_range(
            anchor.root_text, 0, len(anchor.root_text), cap, ledger.unit
        )
    except _BadUtf8:
        return False
    if actual_bytes is None:
        return None
    if not ledger.unit():
        return None
    if actual_bytes > cap or actual_bytes != anchor.source_byte_length:
        return False
    if not ledger.unit():
        return None
    root_bytes = anchor.root_text.encode("utf-8")
    if not ledger.unit():
        return None
    if _sha256_hex(root_bytes) != anchor.root_digest:
        return False
    if workspace is not None:
        if not ledger.unit():
            return None
        if anchor.workspace != workspace:
            return False
    return True


def _bounded_text(value: object, limit: int) -> bool:
    """O(1) bounded nonempty text shape fence (an actual str with
    no control characters; a wrong-type value is malformed, never
    an escaping exception)."""
    return (
        isinstance(value, str)
        and 1 <= len(value) <= limit
        and not any(ord(c) < 0x20 or ord(c) == 0x7F for c in value)
    )


def _relative_path_shape(value: object) -> bool:
    """O(1) resolved relative-path shape fence (an actual str,
    nonempty bounded relative POSIX text; no control characters,
    no absolute anchor; a wrong-type value is malformed, never an
    escaping exception)."""
    return isinstance(value, str) and _bounded_text(value, 1024) and not value.startswith("/")


def _span_shape(span: object) -> bool:
    """O(1) CharSpan shape fence (integral non-bool nonnegative
    coordinates, half-open ordering; no traversal)."""
    return (
        isinstance(span, CharSpan)
        and isinstance(span.start, int)
        and not isinstance(span.start, bool)
        and isinstance(span.end, int)
        and not isinstance(span.end, bool)
        and span.start >= 0
        and span.end >= span.start
    )


def _h_proof_integrity(
    occ: CompletedReadOccurrence,
    g_bounds: GraphBounds,
    p_bounds: BundleProofBounds,
    o_bounds: ObservationBounds,
    ledger: _CoupledUnit,
) -> bool | RootLineageLimitation | None:
    """Fresh charged validation of ONE retained occurrence's ACTUAL
    proof record (called exactly ONCE per retained occurrence -- no
    repeated full source per witness).

    Every retained occurrence's proof is self-contained (the source
    text plus the exact aggregate lengths/digests and its original
    carriers/segments/members/markers), and
    ``model_copy``/``model_construct`` bypass the record validators,
    so EVERY actual field the composition interprets is freshly
    validated, each check charged: the identity/binding shapes
    (occurrence/call/endpoint/tool/argument fingerprint, the proof's
    call/endpoint cross-binding to its occurrence, the ACTUAL
    supported proof version and the ACTUAL earned read grammar,
    integral positions, the FILE tool result source role, the bounded
    text and relative-path shapes, the ACTUAL proof scalar and
    container shape fences BEFORE any len/iteration/comparison/
    arithmetic); the O(1) EFFECTIVE per-snapshot
    collection prefights BEFORE any walk (a single forged proof wider
    than ANY legal original snapshot -- members/segments/pieces
    against the actual inherited snapshot caps, markers against the
    actual command-length law -- refuses without a traversal;
    cumulative retention stays in the actual D domain); the requested
    members / proven-executed PER-INDEX alignment (the resolved path
    proven executed for each requested occurrence, with the ACTUAL
    inherited path ceilings, charged no-copy byte walks); the
    ORIGINAL CARRIER law (at least one piece, ordered piece indices,
    the initial carrier bound to the occurrence's original call, the
    span/length UTF-8 coherence per carrier); the ordered
    segment/member/span laws (positions index the members, UTF-8
    length ranges, digests, the per-member digest law, the
    empty-digest law, per-carrier span alignment with the ORIGINAL
    per-carrier CONTAINMENT and carrier COVERAGE -- a segment's
    source is exactly the union of its original carrier sub-spans,
    the partitioned kind law); the marker shapes (including the
    actual single-marker ceiling; the ORIGINAL plan-statement index
    domain -- nonnegative, strictly ascending, not a contiguous
    ordinal) with the same containment/coverage laws; THEN the
    declared character count against the actual text
    and the ACTUAL single-source byte cap fence BEFORE any character
    inspection (bytes are never fewer than characters, so an
    over-count source refuses without ANY character inspection); the
    actual byte length is then measured by a charged no-copy walk
    with an early exit at the ACTUAL single-source byte cap (an
    isolated-surrogate source refuses before the owned encode), and
    a crossing of that cap is the INHERITED source-domain
    ``SOURCE_OVER_BOUND`` refusal BEFORE any owned encode/hash; the
    ordered segment totals bind the source, the single whole-source
    segment's digest equals the exact aggregate digest (the single
    owned encode is reused), and the digest is re-checked from that
    single encode.  Returns True when coherent, the exact inherited
    source-domain limitation when the actual byte cap is crossed,
    False when malformed (the caller maps it to MALFORMED_BINDING),
    or None when a charge was refused (the caller maps it to
    WORK_UNITS_OVER_BOUND)."""
    proof = occ.proof
    if not ledger.unit():
        return None
    if (
        not isinstance(occ.occurrence_id, str)
        or not _hex64_ok(occ.occurrence_id)
        or not isinstance(occ.call_id, str)
        or not 1 <= len(occ.call_id) <= 256
        or any(c.isspace() for c in occ.call_id)
        or occ.endpoint not in ("responses", "chat")
        or not isinstance(occ.tool_name, str)
        or not _bounded_text(occ.tool_name, 128)
        or not _hex64_ok(occ.argument_fingerprint)
        or not isinstance(occ.anchored, bool)
        or not isinstance(proof, BundleProof)
    ):
        return False
    # The ACTUAL proof scalar/container shape fences BEFORE any
    # len/iteration/comparison/arithmetic/preflight: a forged
    # None or wrong-type nested field on an otherwise real earned
    # record refuses as the fixed typed malformed binding (the
    # caller maps False to MALFORMED_BINDING), never as an
    # escaping TypeError.
    if not ledger.unit():
        return None
    if (
        not isinstance(proof.requested_members, tuple)
        or not isinstance(proof.segments, tuple)
        or not isinstance(proof.pieces, tuple)
        or not isinstance(proof.markers, tuple)
        or not isinstance(proof.proven_executed, tuple)
        or not isinstance(proof.source_text, str)
        or not isinstance(proof.source_char_length, int)
        or isinstance(proof.source_char_length, bool)
        or not isinstance(proof.source_byte_length, int)
        or isinstance(proof.source_byte_length, bool)
        or proof.source_char_length < 0
        or proof.source_byte_length < 0
        or not _hex64_ok(proof.source_digest)
        or not isinstance(proof.request_index, int)
        or isinstance(proof.request_index, bool)
        or proof.request_index < 0
        or proof.source_role is not BundleSourceRole.FILE_TOOL_RESULT
    ):
        return False
    # O(1) EFFECTIVE per-snapshot collection prefights BEFORE any
    # walk: members/segments/pieces against the ACTUAL inherited
    # snapshot caps; the marker count against the actual command-
    # length law (a finite && plan: the first statement plus one
    # separator plus a minimum statement per further statement).
    # A single forged proof wider than ANY legal original snapshot
    # refuses without a traversal; cumulative retention stays in the
    # actual D domain (never summed here against batch caps, and no
    # per-proof work reset).
    if not ledger.unit():
        return None
    max_markers = 1 + (o_bounds.max_command_chars - 7) // 11
    if (
        len(proof.requested_members) > p_bounds.max_members
        or len(proof.segments) > p_bounds.max_segments
        or len(proof.pieces) > o_bounds.max_process_pieces
        or len(proof.markers) > max_markers
    ):
        return False
    if not ledger.unit():
        return None
    # Cross-record binding: the retained proof is the occurrence's
    # OWN original record under the ACTUAL supported proof version
    # and the ACTUAL earned read grammar (never another
    # occurrence's carrier record, never an unsupported version or
    # grammar shape).
    if (
        proof.call_id != occ.call_id
        or proof.endpoint != occ.endpoint
        or proof.proof_version != BUNDLE_PROOF_CONTRACT_VERSION
        or proof.grammar not in (READ_GRAMMAR, READ_PLAN_GRAMMAR, LOOP_GRAMMAR)
        or not isinstance(proof.kind, BundleProofKind)
        or not isinstance(proof.surface, BundleSurface)
        or (proof.command_digest is not None and not _hex64_ok(proof.command_digest))
        or not _bounded_text(proof.call_location, 1024)
        or not isinstance(proof.call_position, int)
        or isinstance(proof.call_position, bool)
        or proof.call_position < 0
        or not _bounded_text(proof.result_location, 1024)
        or not isinstance(proof.result_position, int)
        or isinstance(proof.result_position, bool)
        or proof.result_position < 0
        or not _relative_path_shape(proof.root_path)
    ):
        return False
    members = proof.requested_members
    if not ledger.unit():
        return None
    if not members:
        return False
    # The ACTUAL inherited path ceilings (a legal member reference is
    # within BOTH, hence within the smaller); the charged no-copy
    # byte walk runs BEFORE any encode/copy of the path.
    path_cap = min(g_bounds.max_path_bytes, o_bounds.max_path_bytes)
    member_norms: list[str] = []
    for member in members:
        if not ledger.unit():
            return None
        if not isinstance(member, NormalizedPath):
            return False
        normalized = member.normalized
        if not isinstance(normalized, str) or not _relative_path_shape(normalized):
            return False
        if len(normalized) > path_cap:
            return False
        try:
            path_bytes = _utf8_byte_length_range(
                normalized, 0, len(normalized), path_cap, ledger.unit
            )
        except _BadUtf8:
            return False
        if path_bytes is None:
            return None
        if path_bytes > path_cap:
            return False
        member_norms.append(normalized)
    if not ledger.unit():
        return None
    if (
        not isinstance(proof.distinct_member_count, int)
        or isinstance(proof.distinct_member_count, bool)
        or proof.distinct_member_count < 0
    ):
        return False
    if not ledger.units(len(member_norms)):
        return None
    if proof.distinct_member_count != len(set(member_norms)):
        return False
    proven = proof.proven_executed
    if not ledger.unit():
        return None
    if not isinstance(proven, tuple) or len(proven) != len(members):
        return False
    for index, path in enumerate(proven):
        if not ledger.unit():
            return None
        # PER-INDEX executed-member alignment: the resolved path
        # proven executed for each requested occurrence is that
        # occurrence's OWN resolved path (never a different member's
        # path; equality also re-asserts the validated shape/cap).
        if path != member_norms[index]:
            return False
    pieces = proof.pieces
    if not ledger.unit():
        return None
    # ORIGINAL CARRIER law: the complete proven output retains its
    # carriers (a metadata-only record is not source proof).
    if not pieces:
        return False
    piece_count = len(pieces)
    for position, piece in enumerate(pieces):
        if not ledger.unit():
            return None
        if not isinstance(piece, BundlePiece) or not _span_shape(piece.char_span):
            return False
        if (
            not isinstance(piece.piece_index, int)
            or isinstance(piece.piece_index, bool)
            or piece.piece_index != position
            or not _bounded_text(piece.carrier_location, 1024)
            or not isinstance(piece.char_length, int)
            or isinstance(piece.char_length, bool)
            or piece.char_length != piece.char_span.end - piece.char_span.start
            or not isinstance(piece.byte_length, int)
            or isinstance(piece.byte_length, bool)
            or not (piece.char_length <= piece.byte_length <= 4 * piece.char_length)
            or not isinstance(piece.call_id, str)
            or not 1 <= len(piece.call_id) <= 256
            or any(c.isspace() for c in piece.call_id)
            or not _bounded_text(piece.call_location, 1024)
            or not isinstance(piece.call_position, int)
            or isinstance(piece.call_position, bool)
            or piece.call_position < 0
            or not isinstance(piece.result_position, int)
            or isinstance(piece.result_position, bool)
            or piece.result_position < 0
        ):
            return False
        if position == 0:
            # The initial carrier is the occurrence's ORIGINAL exec
            # result (the initial-EXEC owner law; later carriers stay
            # causally associated and are never renumbered).
            if not ledger.unit():
                return None
            if piece.call_id != occ.call_id:
                return False
    segments = proof.segments
    for position, segment in enumerate(segments):
        if not ledger.unit():
            return None
        if not isinstance(segment, BundleSegment):
            return False
        positions = segment.member_positions
        if (
            not isinstance(segment.index, int)
            or isinstance(segment.index, bool)
            or segment.index != position
            or not isinstance(positions, tuple)
            or not positions
            or not isinstance(segment.char_length, int)
            or isinstance(segment.char_length, bool)
            or segment.char_length < 0
            or not isinstance(segment.byte_length, int)
            or isinstance(segment.byte_length, bool)
            or not (segment.char_length <= segment.byte_length <= 4 * segment.char_length)
            or not _hex64_ok(segment.digest)
            or (segment.member_digest is not None and not _hex64_ok(segment.member_digest))
            or not isinstance(segment.piece_spans, tuple)
            or len(segment.piece_spans) != piece_count
        ):
            return False
        for pos in positions:
            if not ledger.unit():
                return None
            if not isinstance(pos, int) or isinstance(pos, bool) or not 0 <= pos < len(members):
                return False
        if not ledger.unit():
            return None
        if (segment.char_length == 0 and segment.digest != EMPTY_SOURCE_SHA256) or (
            segment.member_digest is not None
            and (len(positions) != 1 or segment.member_digest != segment.digest)
        ):
            return False
        # ORIGINAL per-carrier CONTAINMENT and carrier COVERAGE:
        # every sub-span is a region of that carrier's EXACT output
        # span, and the segment's source is exactly the union of its
        # original carrier sub-spans.
        covered = 0
        for piece_index, span in enumerate(segment.piece_spans):
            if span is None:
                # No overlap with this carrier.
                continue
            if not ledger.unit():
                return None
            if not _span_shape(span):
                return False
            carrier = pieces[piece_index].char_span
            if span.start < carrier.start or span.end > carrier.end:
                return False
            covered += span.end - span.start
        if not ledger.unit():
            return None
        if covered != segment.char_length:
            return False
    if not ledger.unit():
        return None
    if len(segments) > 1 and proof.kind is not BundleProofKind.PARTITIONED:
        return False
    markers = proof.markers
    if not ledger.unit():
        return None
    if not isinstance(markers, tuple):
        return False
    # The marker index is the ORIGINAL PLAN STATEMENT index (the
    # accepted B law), not a contiguous marker ordinal: a plan
    # interleaves non-echo statements (cat/exec) between markers, so
    # the indices are strictly ascending without being contiguous
    # (prefix/interior/suffix markers alike).
    previous_marker_index: int | None = None
    for marker in markers:
        if not ledger.unit():
            return None
        if not isinstance(marker, BundleMarkerFact):
            return False
        if (
            not isinstance(marker.index, int)
            or isinstance(marker.index, bool)
            or marker.index < 0
            or previous_marker_index is not None
            and marker.index <= previous_marker_index
            or not isinstance(marker.role, BundleMarkerRole)
            or not isinstance(marker.char_length, int)
            or isinstance(marker.char_length, bool)
            or marker.char_length < 1
            or not isinstance(marker.byte_length, int)
            or isinstance(marker.byte_length, bool)
            or marker.byte_length > p_bounds.max_marker
            or not (marker.char_length <= marker.byte_length <= 4 * marker.char_length)
            or not _hex64_ok(marker.digest)
            or not isinstance(marker.piece_spans, tuple)
            or len(marker.piece_spans) != piece_count
        ):
            return False
        previous_marker_index = marker.index
        covered = 0
        for piece_index, span in enumerate(marker.piece_spans):
            if span is None:
                # No overlap with this carrier.
                continue
            if not ledger.unit():
                return None
            if not _span_shape(span):
                return False
            carrier = pieces[piece_index].char_span
            if span.start < carrier.start or span.end > carrier.end:
                return False
            covered += span.end - span.start
        if not ledger.unit():
            return None
        if covered != marker.char_length:
            return False
    text_ = proof.source_text
    chars = len(text_)
    cap = g_bounds.max_single_source_bytes
    if not ledger.unit():
        return None
    if proof.source_char_length != chars:
        return False
    # ACTUAL single-source byte cap fence BEFORE any character
    # inspection (bytes are never fewer than characters): an
    # over-count source crosses the inherited cap without ANY
    # character inspection.
    if not ledger.unit():
        return None
    if chars > cap:
        return RootLineageLimitation.SOURCE_OVER_BOUND
    if not ledger.unit():
        return None
    if proof.source_byte_length < chars or proof.source_byte_length > 4 * chars:
        return False
    try:
        actual = _utf8_byte_length_range(text_, 0, chars, cap, ledger.unit)
    except _BadUtf8:
        return False
    if actual is None:
        return None
    if not ledger.unit():
        return None
    # The ACTUAL measured bytes crossing the inherited single-source
    # byte cap is the exact source-domain refusal, decided BEFORE the
    # owned encode/hash below (a declared length lying above the cap
    # while the actual bytes stay below it is a malformed binding,
    # caught by the equality below).
    if actual > cap:
        return RootLineageLimitation.SOURCE_OVER_BOUND
    if actual != proof.source_byte_length:
        return False
    if not ledger.unit():
        return None
    total_chars = 0
    total_bytes = 0
    for segment in segments:
        if not ledger.unit():
            return None
        total_chars += segment.char_length
        total_bytes += segment.byte_length
    if not ledger.unit():
        return None
    if total_chars != chars or total_bytes != proof.source_byte_length:
        return False
    if not ledger.unit():
        return None
    source_sha = _sha256_hex(text_.encode("utf-8"))
    if not ledger.unit():
        return None
    if source_sha != proof.source_digest:
        return False
    if not ledger.unit():
        return None
    # A single segment IS the whole source: its digest must equal
    # the exact aggregate digest (zero extra copies -- the single
    # owned encode is reused).
    if len(segments) == 1 and segments[0].digest != source_sha:
        return False
    return True


def _hex64_ok(value: object) -> bool:
    """O(1) 64-hex shape fence (no traversal, no exception)."""
    return isinstance(value, str) and len(value) == 64 and set(value) <= _HEX_DIGITS


def _preflight_ns_shape(ns: object) -> bool:
    """The O(1) shape fence BEFORE any unvalidated fuel (K5).

    A forged scope (``model_construct``/``model_copy``) is refused
    before the work cap is read from its possibly non-integer
    nested bounds, before the wide revalidation dump, and before
    any origin/state constructor consumes its key fields: EVERY
    actual namespace scalar (identity, workspace, mode, versions,
    opaque keys) and EVERY scalar of the SIX nested bound sets is
    fenced to its declared hard cap by the closed scalar fences
    (an unexpected container in a scalar slot refuses before any
    serializer traversal).  No serialization, no forged-field
    traversal, no exception as control flow."""
    if not isinstance(ns, RootLineageNamespace):
        return False
    if not root_lineage_ns_scalar_shape_ok(ns):
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


def _state_shape(h_state: object) -> bool:
    """The fixed O(1) H-state shape fence BEFORE any field
    dereference in a public entry (K5): a malformed non-model or
    wrong-type nested input refuses with the fixed non-echoing
    error, never as AttributeError/TypeError escaping the API.
    Covers exactly the fields the early gates read: the H and D
    model classes, the two integral (non-bool) revisions, both
    64-hex scope keys and the root-facts tuple type."""
    return (
        isinstance(h_state, RootLineageState)
        and isinstance(h_state.d_state, CausalHistoryState)
        and isinstance(h_state.revision, int)
        and not isinstance(h_state.revision, bool)
        and _hex64_ok(h_state.lineage_key)
        and isinstance(h_state.root_facts, tuple)
        and isinstance(h_state.d_state.revision, int)
        and not isinstance(h_state.d_state.revision, bool)
        and _hex64_ok(h_state.d_state.history_key)
    )


def _state_refusal_outcome(problem: RootLineageLimitation) -> RootLineageOutcome:
    """The fixed closed outcome of a charged state-validation
    refusal (the closed resource domain -- every *_over_bound
    limitation, H-owned AND mirrored 1:1 from the actual D domain --
    is an over-bound refusal; a malformed binding mirrors the actual
    D pairing)."""
    if problem.value.endswith("_over_bound"):
        return RootLineageOutcome.REFUSED_OVER_BOUND
    return RootLineageOutcome.REFUSED_CONFLICT


def _ns_reservation(ns: RootLineageNamespace) -> int:
    """Honest conservative pre-reservation (H-V2-4) for the
    revalidated namespace chain, charged BEFORE the work: two full
    revalidation passes (the H scope model and the derived D scope)
    over the closed field set, each with its nested bound sets, the
    full actual D admission re-validation, the sha256 key
    recomputations and the bounded workspace/config walks (linear
    in the actual bounded text lengths)."""
    return 2 * (512 + len(ns.workspace) + len(ns.config_fingerprint))


def _revalidate_h_ns(ns: RootLineageNamespace) -> bool:
    """Re-run the ACTUAL accepted validators over the ACTUAL fields.

    A forged nested model copy (``model_copy``/``model_construct``)
    carries no acquired authority: every field, the full actual D
    scope (its admission re-validation and BOTH D 64-hex keys), the
    NEW bounds and the recomputed lineage key are revalidated; the
    opaque keys alone are not enough.  The dump suppresses
    serialization warnings so a malformed input value never
    leaks into a warning message (the refusal stays fixed and
    private, K6)."""
    try:
        RootLineageNamespace.model_validate(ns.model_dump(mode="python", warnings=False))
    except Exception:
        return False
    return True


def _version_pairs(ns: RootLineageNamespace) -> tuple[tuple[str, str], ...]:
    """The SEVEN actual D version identities plus the TWO H version
    identities, paired with the supported constants (all O(1) field
    reads; a coherent direct construction with an unsupported ACTUAL
    version recomputes its keys correctly and must still refuse)."""
    return (
        (ns.history_version, CAUSAL_HISTORY_CONTRACT_VERSION),
        (ns.arguments_version, CAUSAL_ARGUMENTS_JSON_VERSION),
        (ns.admission_version, ADMISSION_CONTRACT_VERSION),
        (ns.observation_version, OBSERVER_VERSION),
        (ns.graph_version, GRAPH_CONTRACT_VERSION),
        (ns.reference_version, REFERENCE_GRAMMAR),
        (ns.proof_version, BUNDLE_PROOF_CONTRACT_VERSION),
        (ns.contract_version, ROOT_LINEAGE_CONTRACT_VERSION),
        (ns.policy_version, ROOT_LINEAGE_POLICY_VERSION),
    )


def _d_namespace(ns: RootLineageNamespace) -> CausalHistoryNamespace:
    """The ACTUAL accepted D scope derived from the H scope's ACTUAL
    D fields (re-validated by construction)."""
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


def _closed(
    h_state: RootLineageState,
    outcome: RootLineageOutcome,
    limitations: tuple[RootLineageLimitation, ...],
    d_transition: CausalHistoryTransition | None = None,
) -> RootLineageTransition:
    """A non-accepted H transition over the EXACT prior H state:
    every refusal (with or without the actual D transition as
    evidence -- including the ACTUAL accepted D candidate the H
    post-D law atomically discarded) and every replay."""
    if d_transition is not None:
        d_before = d_transition.revision_before
        d_after = d_transition.revision_after
    else:
        d_before = d_after = h_state.d_state.revision
    return RootLineageTransition(
        state=h_state,
        outcome=outcome,
        diagnostics=limitations,
        d_transition=d_transition,
        revision_before=h_state.revision,
        revision_after=h_state.revision,
        d_revision_before=d_before,
        d_revision_after=d_after,
    )


def _map_d_refusal(
    d_trans: CausalHistoryTransition,
    ctx: _RootLineageContext,
    h_state: RootLineageState,
    outer: _HOuter,
) -> RootLineageTransition:
    """Map one actual D refusal onto the closed H vocabulary.

    An H outer crossing recorded on the lineage context maps to the
    H over-bound refusal; otherwise the D outcome and its
    diagnostics are mirrored 1:1 under their exact fixed names (the
    D transition is retained by identity as evidence).  The
    diagnostic map walk charges BEFORE the mapping."""
    if ctx.outer_exhausted:
        return _closed(
            h_state,
            RootLineageOutcome.REFUSED_OVER_BOUND,
            (RootLineageLimitation.WORK_UNITS_OVER_BOUND,),
            d_trans,
        )
    if not outer.units(2 * len(d_trans.diagnostics)):
        return _closed(
            h_state,
            RootLineageOutcome.REFUSED_OVER_BOUND,
            (RootLineageLimitation.WORK_UNITS_OVER_BOUND,),
            d_trans,
        )
    outcome = _H_OUTCOME_MAP[d_trans.outcome]
    limitations = tuple(_H_LIMITATION_MAP[lim] for lim in d_trans.diagnostics)
    return _closed(h_state, outcome, limitations, d_trans)


def _gate(
    h_state: RootLineageState,
    ns: RootLineageNamespace,
    expected_revision: int,
    outer: _HOuter,
) -> tuple[CausalHistoryNamespace | None, RootLineageTransition | None]:
    """The shared early H gates: the fixed O(1) scope/CAS/
    D-state-binding/version fences FIRST, then the charged full
    namespace revalidation and the derived ACTUAL D namespace (all
    before any D work).  A foreign/CAS-mismatched/version-
    conflicting scope is refused without the wide walk (K5).
    Returns the derived ACTUAL D namespace, or the exact prior-
    state transition."""
    if not outer.units(11):
        return None, _closed(
            h_state,
            RootLineageOutcome.REFUSED_OVER_BOUND,
            (RootLineageLimitation.WORK_UNITS_OVER_BOUND,),
        )
    if h_state.lineage_key != ns.lineage_key:
        return None, _closed(h_state, RootLineageOutcome.REFUSED_FOREIGN_SCOPE, ())
    if h_state.revision != expected_revision:
        return None, _closed(h_state, RootLineageOutcome.REFUSED_CAS_MISMATCH, ())
    # The wrapped ACTUAL D state must belong to this lineage's ACTUAL
    # D scope (a forged replacement D state is refused before any D
    # work; object construction is not authentication).
    if h_state.d_state.history_key != ns.history_key:
        return None, _closed(h_state, RootLineageOutcome.REFUSED_FOREIGN_SCOPE, ())
    for actual, supported in _version_pairs(ns):
        if actual != supported:
            return None, _closed(
                h_state,
                RootLineageOutcome.REFUSED_VERSION_CONFLICT,
                (RootLineageLimitation.VERSION_UNSUPPORTED,),
            )
    # The charged FULL revalidation after the cheap fences (the
    # fresh actual-field validation of the whole scope, incl. the
    # nested bounds, under the warning-suppressed dump).
    if not outer.units(_ns_reservation(ns)):
        return None, _closed(
            h_state,
            RootLineageOutcome.REFUSED_OVER_BOUND,
            (RootLineageLimitation.WORK_UNITS_OVER_BOUND,),
        )
    if not _revalidate_h_ns(ns):
        return None, _closed(h_state, RootLineageOutcome.REFUSED_FOREIGN_SCOPE, ())
    if not outer.units(_ns_reservation(ns)):
        return None, _closed(
            h_state,
            RootLineageOutcome.REFUSED_OVER_BOUND,
            (RootLineageLimitation.WORK_UNITS_OVER_BOUND,),
        )
    return _d_namespace(ns), None


def _deferred_digests(sink: list[frozenset[str]], outer: _HOuter) -> tuple[str, ...] | None:
    """The sorted union of the batch's deferred same-scope envelope
    digests (charged per digest; None on H outer exhaustion)."""
    if not sink:
        return ()
    union: set[str] = set()
    for digest_set in sink:
        for digest in digest_set:
            if not outer.unit():
                return None
            union.add(digest)
    if len(union) > 1:
        # Pair-counting reservation for the charged canonical sort
        # (the conservative ordered-pair bound; see the D
        # _sort_comparison_reservation derivation).
        if not outer.units(len(union) * (len(union) - 1)):
            return None
    return tuple(sorted(union))


def _new_root_facts(
    new_occurrences: tuple[CompletedReadOccurrence, ...],
    old_count: int,
    old_bytes: int,
    bounds: RootLineageBounds,
    outer: _HOuter,
) -> tuple[RootLineageFact, ...] | RootLineageLimitation | None:
    """The S3 explicit singleton whole-source root-read filter.

    A new completed occurrence is a retained root-source candidate
    ONLY for a complete whole singleton read of the EXACT normalized
    root path: one requested member (AGENTS.md), one attributable
    proven segment covering the complete source at position (0,)
    with a non-None member digest.  Opaque/mixed bundles, repeated
    root operands, isolated root segments in a larger bundle and
    partial/truncated/nonzero/unpaired reads are never candidates.
    The root body of such a read IS the original whole-read source
    (the fact source binds the retained original binding, never a
    re-hashed copy).  Flags start unproven: the S1 re-derivation
    over the NEW state decides them.  Returns the new fact tuple,
    the FIRST actual cap refusal (the crossing is refused BEFORE
    the crossing fact materializes, K4), or None on exhaustion."""
    out: list[RootLineageFact] = []
    out_bytes = 0
    for occ in new_occurrences:
        eligible = _is_singleton_root_read(occ, outer.unit)
        if eligible is None:
            return None
        if not eligible:
            continue
        proof = occ.proof
        segment = proof.segments[0]
        if segment.member_digest is None:
            raise _fixed("unreachable: the S3 filter retains only the proven member digest")
        # The logical retention cap preflight BEFORE the crossing
        # fact materializes (K4): a first-over candidate is refused
        # with its exact domain reason, no new fact constructed.
        if old_count + len(out) + 1 > bounds.max_root_facts:
            return RootLineageLimitation.ROOT_FACTS_OVER_BOUND
        if old_bytes + out_bytes + segment.byte_length > bounds.max_retained_root_source_bytes:
            return RootLineageLimitation.ROOT_SOURCE_BYTES_OVER_BOUND
        if not outer.units(_FACT_BUILD_UNITS):
            return None
        out.append(
            RootLineageFact(
                source_digest=segment.member_digest,
                source_byte_length=segment.byte_length,
                provenance=ReadRootProvenance(
                    occurrence_id=occ.occurrence_id,
                    call_id=occ.call_id,
                    endpoint=occ.endpoint,
                    read_digest=proof.source_digest,
                    read_byte_length=proof.source_byte_length,
                ),
                issued=False,
                authority=False,
            )
        )
        out_bytes += segment.byte_length
    return tuple(out)


def _derive_flags(
    d_state: CausalHistoryState,
    facts: tuple[RootLineageFact, ...],
    outer: _HOuter,
) -> tuple[RootLineageFact, ...] | None:
    """The S1 authority re-derivation.

    After EVERY accepted D transition, ALL retained facts' issued/
    authority flags are recomputed from the ACTUAL new D state:
    issued = the matching INTERNAL issuance is retained; authority =
    issued AND the occurrence is anchored AND the frozen parent
    evidence reaches the ORIGINAL bootstrap root fact (CAUSAL_ROOT_
    FACT ALWAYS means the original bootstrap, never a selected
    latest).  A late issuance/receipt -- even a NONROOT ancestor's --
    can earn a previously unproven root read its authority; flags
    never come from a single receipt row.  The envelope fact is the
    anchor itself (never issued, always authoritative).  Returns
    None on H outer exhaustion."""
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
    out: list[RootLineageFact] = []
    for fact in facts:
        if not outer.unit():
            return None
        if fact.provenance.kind == "envelope":
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
        if not outer.units(_FACT_COPY_UNITS):
            return None
        out.append(fact.model_copy(update={"issued": issued, "authority": authority}))
    return tuple(out)


def _retention_check(
    facts: tuple[RootLineageFact, ...],
    bounds: RootLineageBounds,
    outer: _HOuter,
    h_state: RootLineageState,
    d_trans: CausalHistoryTransition,
) -> RootLineageTransition | None:
    """The retention caps, counted BEFORE retention (the actual
    fact count and the logical exact UTF-8 root source bytes over
    ALL retained facts, bootstrap once).  Returns the exact
    prior-state refusal, or None when within bounds."""
    if len(facts) > bounds.max_root_facts:
        return _closed(
            h_state,
            RootLineageOutcome.REFUSED_OVER_BOUND,
            (RootLineageLimitation.ROOT_FACTS_OVER_BOUND,),
            d_trans,
        )
    total = 0
    for fact in facts:
        if not outer.unit():
            return _closed(
                h_state,
                RootLineageOutcome.REFUSED_OVER_BOUND,
                (RootLineageLimitation.WORK_UNITS_OVER_BOUND,),
                d_trans,
            )
        total += fact.source_byte_length
        if total > bounds.max_retained_root_source_bytes:
            return _closed(
                h_state,
                RootLineageOutcome.REFUSED_OVER_BOUND,
                (RootLineageLimitation.ROOT_SOURCE_BYTES_OVER_BOUND,),
                d_trans,
            )
    return None


def _combine_facts(
    old: tuple[RootLineageFact, ...],
    new: tuple[RootLineageFact, ...],
    outer: _HOuter,
) -> tuple[RootLineageFact, ...] | None:
    """Sorted-deduplicated union by provenance identity (a fresh
    occurrence ID can never collide with a retained fact; the check
    is defensive).  The charged pair-counting reservation precedes
    the canonical sort."""
    if not outer.units(len(old)):
        return None
    combined = list(old)
    old_keys: set[tuple[str, str]] = set()
    for fact in old:
        if not outer.unit():
            return None
        old_keys.add(_provenance_key(fact.provenance))
    for fact in new:
        if not outer.unit():
            return None
        key = _provenance_key(fact.provenance)
        if key not in old_keys:
            if not outer.unit():
                return None
            combined.append(fact)
            old_keys.add(key)
    if len(combined) > 1:
        if not outer.units(len(combined) * (len(combined) - 1)):
            return None
    return tuple(sorted(combined, key=lambda f: _provenance_key(f.provenance)))


# --- Bounded charged state validation ------------------------------------


def validate_root_lineage_state(
    h_state: RootLineageState,
    bounds: RootLineageBounds | None = None,
    work: _UnitLedger | None = None,
    history_bounds: HistoryBounds | None = None,
    graph_bounds: GraphBounds | None = None,
    proof_bounds: BundleProofBounds | None = None,
    observation_bounds: ObservationBounds | None = None,
    workspace: str | None = None,
) -> RootLineageLimitation | None:
    """Bounded, charged cross-record integrity for one H state.

    The ONE cross-record validation law: record models enforce
    field-level shape and intrinsic coherence only, and
    ``model_copy``/``model_construct`` bypass them -- so EVERY
    actual field the composition interprets is freshly re-validated
    BEFORE positive use, each check charged:

    1. the NEW H record shape law (revision integral 0..MAX_REVISION
       and in EXACT 1:1 with the wrapped D revision, 64-hex keys,
       the root-facts tuple shape, the sorted/deduplicated
       provenance identity and every fact's intrinsic fields);
    2. the effective retention bounds (fact count and logical exact
       UTF-8 root source bytes over ALL retained facts, bootstrap
       once) -- resource-domain refusals win with their exact names;
    3. the ACTUAL root-anchor source integrity (the accepted F
       anchor law, H-owned): every anchor field shape, the O(1)
       character preflight against the ACTUAL single-source AND
       retained-root byte caps, the charged no-copy UTF-8 byte walk
       with early exit and isolated-surrogate refusal BEFORE any
       owned copy, the digest re-checked from that copy, the
       workspace compared to the ACTUAL namespace workspace when
       supplied, and the retained occurrence root bindings
       re-verified;
    4. the ACTUAL D cross-record integrity through the real accepted
       D validator (retention, identity, observed binding, anchored
       semantics, frontier, parent-edge and acyclicity laws) with
       the ACTUAL D bounds in their own local domain while the SAME
       outer is charged per unit;
    4b. the H-PRIVATE retained result/proof binding coherence (the
       accepted 017/D builder invariant invisible to the OLD observed
       D validator: every retained piece producer binding was derived
       from the SAME original request, so its endpoint family always
       equals the record's own endpoint; a flipped piece endpoint in
       a retained record is an incoherent result binding, never a new
       trust source -- the old public D behavior stays unchanged);
    4c. the H-PRIVATE completed-occurrence/result ownership join (the
       accepted 017/D builder pairing invisible to the OLD observed D
       validator: EVERY completed occurrence's complete owning result
       record -- keyed by the read's own call ID -- retains the EXACT
       producing-call association of the occurrence's RETAINED proof
       pieces, aligned by piece index, and the complete record's
       piece facts ARE the exact original piece facts of the complete
       proof; a missing/incomplete owning result, a changed piece
       producer ID, a mismatched initial owner binding or a
       mismatched piece length erases the original poll ownership
       that the retained proof alone cannot re-prove -- the old
       public D behavior stays unchanged; the charged result index
       is built beforehand and each occurrence's join is evaluated
       in the step 5/6 pass ONLY after that occurrence's ACTUAL
       proof integrity validation has succeeded, so the proof is
       walked exactly once and malformed proofs keep their typed
       shape refusals);
    5. the ACTUAL earned proof-record integrity for EVERY
       retained occurrence exactly ONCE (no repeated full source
       per witness): the identity/binding shapes, the proof's
       call/endpoint cross-binding, the ACTUAL supported proof
       version and the ACTUAL earned read grammar, the ACTUAL proof
       scalar/container shape fences before any len/iteration/
       arithmetic, the O(1)
       EFFECTIVE per-snapshot collection prefights (members/
       segments/pieces/markers against the actual inherited
       snapshot caps and the actual command-length law, before
       any walk), the resolved member paths with the distinct
       count, the PER-INDEX proven-executed member alignment and
       the ACTUAL inherited path ceilings, the ORIGINAL CARRIER
       law (ordered pieces, the initial carrier bound to the
       occurrence's original call, span/length UTF-8 coherence
       per carrier), the ordered segment/member/span laws (member
       positions, UTF-8 length ranges, digests, the per-member
       and empty-digest laws, the ORIGINAL per-carrier span
       containment and carrier coverage, the partitioned kind
       law), the marker shapes (including the actual single-
       marker ceiling) with the same containment/coverage laws,
       the declared character count against the actual text, the
       ACTUAL single-source byte cap fence BEFORE any character
       inspection, the charged no-copy byte walk early-exiting at
       that ACTUAL byte cap (a crossing is the inherited
       source-domain SOURCE_OVER_BOUND refusal before any owned
       encode/hash), the ordered segment totals, the single whole-
       source segment digest equality, and the digest re-checked
       from the single owned encode;
    6. the COMPLETE fact inventory: EVERY actual eligible singleton
       root-read D occurrence retains its H read fact (1:1 -- an
       omitted earned fact is an incoherent binding, never a silent
       rollback) and every retained read fact binds an eligible
       occurrence;
    7. the per-read-fact provenance binding and the DERIVED flags
       re-derived from the ACTUAL D state (issuance, anchoring and
       frozen-parent ancestry to the bootstrap root fact) -- the
       stored flags are NEVER trusted: a forged positive bit is an
       incoherent binding, never minted authority.

    Length preflights run BEFORE any map/iteration/copy; every
    actual visit/comparison/membership attempt charges BEFORE the
    operation (the supplied shared ledger when present, ALWAYS plus
    the local hard ceiling -- standalone use is never unbounded):
    the sorted/deduplicated provenance identity is one charged
    strict-increase comparison per adjacent stored pair (no sort,
    set or copy is built), every fact-set membership is charged
    before its insert, and the final inventory set-equality
    comparison is preceded by a reservation of its ACTUAL
    length-gate plus element-attempt work.  A refused charge stops
    with WORK_UNITS_OVER_BOUND before the crossing operation.
    Returns ``None`` when coherent, else the ONE fixed closed
    limitation (first refusal wins)."""
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

    # --- 1. The NEW H record shape law (model_copy is not authority) ---
    if not ledger.unit():
        return RootLineageLimitation.WORK_UNITS_OVER_BOUND
    if not isinstance(h_state, RootLineageState):
        return RootLineageLimitation.MALFORMED_BINDING
    revision = h_state.revision
    if (
        not isinstance(revision, int)
        or isinstance(revision, bool)
        or not 0 <= revision <= MAX_REVISION
    ):
        return RootLineageLimitation.MALFORMED_BINDING
    if not _hex64_ok(h_state.lineage_key):
        return RootLineageLimitation.MALFORMED_BINDING
    if not ledger.unit():
        return RootLineageLimitation.WORK_UNITS_OVER_BOUND
    d_state = h_state.d_state
    if not isinstance(d_state, CausalHistoryState):
        return RootLineageLimitation.MALFORMED_BINDING
    d_revision = d_state.revision
    if (
        not isinstance(d_revision, int)
        or isinstance(d_revision, bool)
        or not 0 <= d_revision <= MAX_REVISION
    ):
        return RootLineageLimitation.MALFORMED_BINDING
    # The composition and the wrapped D state advance in EXACT 1:1
    # (re-derived from the actual fields, never trusted).
    if not ledger.unit():
        return RootLineageLimitation.WORK_UNITS_OVER_BOUND
    if revision != d_revision:
        return RootLineageLimitation.MALFORMED_BINDING
    if not _hex64_ok(d_state.history_key):
        return RootLineageLimitation.MALFORMED_BINDING
    facts = h_state.root_facts
    if not isinstance(facts, tuple):
        return RootLineageLimitation.MALFORMED_BINDING
    # The hard retention ceiling is prefetched BEFORE any nested walk.
    if len(facts) > effective.max_root_facts:
        return RootLineageLimitation.ROOT_FACTS_OVER_BOUND
    keys_list: list[tuple[str, str]] = []
    for fact in facts:
        if not ledger.unit():
            return RootLineageLimitation.WORK_UNITS_OVER_BOUND
        if not isinstance(fact, RootLineageFact):
            return RootLineageLimitation.MALFORMED_BINDING
        provenance = fact.provenance
        if not isinstance(provenance, (EnvelopeRootProvenance, ReadRootProvenance)):
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
        else:
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
        if not ledger.unit():
            return RootLineageLimitation.WORK_UNITS_OVER_BOUND
        keys_list.append(_provenance_key(provenance))
    # Sorted/deduplicated provenance identity over the STORED
    # order: one charged strict-increase comparison per adjacent
    # pair (no sort, no set, no copy is built; each comparison
    # attempt is charged BEFORE it).
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

    # --- 3. The ACTUAL root-anchor source integrity (F law, H-owned) ---
    if anchor is not None:
        if not ledger.unit():
            return RootLineageLimitation.WORK_UNITS_OVER_BOUND
        coherent = _h_anchor_integrity(anchor, g_bounds, effective, workspace, ledger)
        if coherent is None:
            return RootLineageLimitation.WORK_UNITS_OVER_BOUND
        if not coherent:
            return RootLineageLimitation.MALFORMED_BINDING
    else:
        # A rootless composition state retains NO completed D
        # evidence: no legitimate D transition produces occurrences,
        # issuances or results without the retained root anchor.
        if not ledger.unit():
            return RootLineageLimitation.WORK_UNITS_OVER_BOUND
        if d_state.occurrences or d_state.issuances or d_state.results:
            return RootLineageLimitation.MALFORMED_BINDING

    # --- 4. The ACTUAL D cross-record integrity (the real accepted
    # D validator; its own local D bounds keep their own domain while
    # the SAME outer is charged per unit) ---
    d_problem = validate_causal_history_state(d_state, d_bounds, work=ledger.unit)
    if d_problem is not None:
        return _H_LIMITATION_MAP[d_problem]

    # --- 4b. H-PRIVATE retained result/proof binding coherence (the
    # accepted 017/D builder invariant that the OLD observed D
    # validator cannot see: EVERY retained piece producer binding was
    # derived from the SAME original request, so its endpoint family
    # always equals the record's own endpoint; a flipped piece
    # endpoint in a retained record is an incoherent result binding,
    # never a new trust source.  The old public D behavior is
    # unchanged -- this check is H-private, charged under the SAME
    # outer, and runs before any positive interpretation.) ---
    for result in d_state.results:
        if not ledger.unit():
            return RootLineageLimitation.WORK_UNITS_OVER_BOUND
        for piece_binding in result.piece_call_bindings:
            if not ledger.unit():
                return RootLineageLimitation.WORK_UNITS_OVER_BOUND
            if piece_binding[1] != result.endpoint:
                return RootLineageLimitation.RESULT_CONFLICT

    # --- 4c. H-PRIVATE completed-occurrence/result ownership join:
    # the charged owning-result index (the accepted 017/D builder
    # pairing that the OLD observed D validator cannot see).  EVERY
    # completed occurrence's complete owning result record -- keyed
    # by the read's own call ID -- retains the EXACT producing-call
    # association of the occurrence's RETAINED proof pieces, aligned
    # by piece index; a complete record's piece facts ARE the exact
    # original piece facts of the complete proof.  A
    # missing/incomplete owning result, a changed piece producer ID,
    # a mismatched initial owner binding or a mismatched piece
    # length erases the original poll ownership that the retained
    # proof alone cannot re-prove.  The old public D behavior is
    # unchanged -- the join re-derives from the ACTUAL records,
    # charged under the SAME outer; each occurrence's join runs in
    # the 5/6 pass after its ACTUAL proof integrity succeeds, so a
    # malformed proof never reaches the piece fields before its
    # typed shape refusal.) ---
    result_by_call: dict[str, ResultFingerprintRecord] = {}
    for result in d_state.results:
        if not ledger.unit():
            return RootLineageLimitation.WORK_UNITS_OVER_BOUND
        result_by_call[result.call_id] = result
    # --- 5/6. The ACTUAL proof source integrity (once per occurrence)
    # + the retained occurrence root bindings + the COMPLETE 1:1 fact
    # inventory (every eligible singleton root-read occurrence keeps
    # its H read fact; no silent rollback) ---
    occ_by_id: dict[str, CompletedReadOccurrence] = {}
    eligible: set[str] = set()
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
        # 4c join for THIS occurrence (after its actual proof
        # integrity succeeded above; the proof is walked once).
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
                # The initial piece is produced by the read's OWN
                # call: its binding is the record's actual known
                # owner binding, never a detached join coordinate.
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
        is_root = _is_singleton_root_read(occ, ledger.unit)
        if is_root is None:
            return RootLineageLimitation.WORK_UNITS_OVER_BOUND
        if is_root:
            if not ledger.unit():
                return RootLineageLimitation.WORK_UNITS_OVER_BOUND
            eligible.add(occ.occurrence_id)
    retained: set[str] = set()
    for fact in facts:
        if not ledger.unit():
            return RootLineageLimitation.WORK_UNITS_OVER_BOUND
        if fact.provenance.kind != "read":
            continue
        if not ledger.unit():
            return RootLineageLimitation.WORK_UNITS_OVER_BOUND
        retained.add(fact.provenance.occurrence_id)
    # The set-equality comparison gates on length then hashes up
    # to the smaller set: reserve that ACTUAL work BEFORE the
    # comparison.
    if not ledger.units(1 + min(len(eligible), len(retained))):
        return RootLineageLimitation.WORK_UNITS_OVER_BOUND
    if eligible != retained:
        return RootLineageLimitation.MALFORMED_BINDING

    # --- 7. Per-read-fact provenance binding + DERIVED flags ---
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
        if not isinstance(fact.provenance, ReadRootProvenance):
            # The envelope fact's derived flags are fixed by law.
            if fact.issued is not False or fact.authority is not True:
                return RootLineageLimitation.MALFORMED_BINDING
            continue
        p = fact.provenance
        if not ledger.unit():
            return RootLineageLimitation.WORK_UNITS_OVER_BOUND
        bound_occ = occ_by_id.get(p.occurrence_id)
        if bound_occ is None or bound_occ.call_id != p.call_id or bound_occ.endpoint != p.endpoint:
            return RootLineageLimitation.MALFORMED_BINDING
        if not ledger.unit():
            return RootLineageLimitation.WORK_UNITS_OVER_BOUND
        proof = bound_occ.proof
        if (
            proof.source_digest != p.read_digest
            or proof.source_byte_length != p.read_byte_length
            or fact.source_digest != proof.source_digest
            or fact.source_byte_length != proof.source_byte_length
        ):
            return RootLineageLimitation.MALFORMED_BINDING
        # The DERIVED flag law (S1): re-derived from the ACTUAL D
        # state; the stored bits must match exactly (a forged stored
        # issued/authority is an incoherent binding, never minted
        # authority).
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


# --- The public operations -------------------------------------------------


def bootstrap_root_lineage(
    requests: tuple[GraphRequest, ...],
    ns: RootLineageNamespace,
) -> RootLineageTransition:
    """The ONE legitimate bootstrap over the NEW composition.

    Runs the ACTUAL accepted D bootstrap (the legitimate effective
    Responses AGENTS envelope with exact source bytes, workspace and
    first original spans; empty root is legal; rootless refuses)
    under the STRICT old root law -- no relaxed envelope law and no
    refresh acquisition at bootstrap (a competing root read in the
    bootstrap batch keeps the exact old refusal).  The accepted
    state is wrapped with the bootstrap ENVELOPE fact (never
    issued, always authoritative) and H revision 1; every refusal
    preserves the EXACT prior H state (the composition origin)."""
    if not _preflight_ns_shape(ns):
        if _hex64_ok(ns.lineage_key) and _hex64_ok(ns.history_key):
            origin = RootLineageState(
                lineage_key=ns.lineage_key,
                revision=0,
                d_state=CausalHistoryState(history_key=ns.history_key, revision=0),
            )
            return _closed(origin, RootLineageOutcome.REFUSED_FOREIGN_SCOPE, ())
        raise _fixed("the bootstrap scope must carry actual 64-hex key fields")
    outer = _HOuter(ns.root_lineage_bounds.max_total_work_units)
    empty = CausalHistoryState(history_key=ns.history_key, revision=0)
    origin = RootLineageState(lineage_key=ns.lineage_key, revision=0, d_state=empty)
    d_ns, gated = _gate(origin, ns, 0, outer)
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
        return _closed(
            origin,
            RootLineageOutcome.REFUSED_OVER_BOUND,
            (RootLineageLimitation.WORK_UNITS_OVER_BOUND,),
        )
    if d_trans.outcome is CausalHistoryOutcome.REPLAYED:
        if not outer.units(2 * len(d_trans.diagnostics)):
            return _closed(
                origin,
                RootLineageOutcome.REFUSED_OVER_BOUND,
                (RootLineageLimitation.WORK_UNITS_OVER_BOUND,),
                d_trans,
            )
        limitations = tuple(_H_LIMITATION_MAP[lim] for lim in d_trans.diagnostics)
        return _closed(origin, RootLineageOutcome.REPLAYED, limitations, d_trans)
    if d_trans.outcome is not CausalHistoryOutcome.ACCEPTED:
        return _map_d_refusal(d_trans, ctx, origin, outer)
    root = d_trans.state.root
    if root is None:
        raise _fixed("an accepted bootstrap retains the evidenced root anchor")
    bounds = ns.root_lineage_bounds
    if not outer.unit():
        return _closed(
            origin,
            RootLineageOutcome.REFUSED_OVER_BOUND,
            (RootLineageLimitation.WORK_UNITS_OVER_BOUND,),
            d_trans,
        )
    if root.source_byte_length > bounds.max_retained_root_source_bytes:
        return _closed(
            origin,
            RootLineageOutcome.REFUSED_OVER_BOUND,
            (RootLineageLimitation.ROOT_SOURCE_BYTES_OVER_BOUND,),
            d_trans,
        )
    if not outer.units(_FACT_BUILD_UNITS):
        return _closed(
            origin,
            RootLineageOutcome.REFUSED_OVER_BOUND,
            (RootLineageLimitation.WORK_UNITS_OVER_BOUND,),
            d_trans,
        )
    fact = RootLineageFact(
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
    if not outer.units(_STATE_BUILD_UNITS + _STATE_FACT_UNITS):
        return _closed(
            origin,
            RootLineageOutcome.REFUSED_OVER_BOUND,
            (RootLineageLimitation.WORK_UNITS_OVER_BOUND,),
            d_trans,
        )
    new_state = RootLineageState(
        lineage_key=ns.lineage_key,
        revision=1,
        d_state=d_trans.state,
        root_facts=(fact,),
    )
    if not outer.units(_TRANSITION_BUILD_UNITS + _STATE_FACT_UNITS):
        return _closed(
            origin,
            RootLineageOutcome.REFUSED_OVER_BOUND,
            (RootLineageLimitation.WORK_UNITS_OVER_BOUND,),
            d_trans,
        )
    return RootLineageTransition(
        state=new_state,
        outcome=RootLineageOutcome.ACCEPTED,
        d_transition=d_trans,
        revision_before=0,
        revision_after=1,
        d_revision_before=d_trans.revision_before,
        d_revision_after=d_trans.revision_after,
        new_root_facts=(fact,),
    )


def observe_root_lineage(
    h_state: RootLineageState,
    ns: RootLineageNamespace,
    expected_revision: int,
    requests: tuple[GraphRequest, ...],
) -> RootLineageTransition:
    """The original-payload root-lineage observation transition.

    The ACTUAL D observation runs under the relaxed H context
    (changed SAME-scope envelopes deferred to the composition's
    atomic same-batch verification; the narrow singleton root-read
    acquisition seam retains refresh SOURCE candidates instead of
    the old competing-root refusal).  After an accepted D
    transition: the S1 re-derivation over ALL retained facts, the
    S3 singleton root-read retention (counted and source-bytes
    preflighted BEFORE retention), and the atomic envelope
    verification (every deferred digest must match an authoritative
    retained root fact -- the same-batch independently earned
    authoritative root read establishes the matching envelope's
    known-source status atomically; the envelope itself grants no
    ordering).  A deferred envelope WITHOUT authority -- or a
    replay with a nonempty deferral sink (replays earn no facts) --
    is a fixed whole-transition REFUSED_ROOT_AUTHORITY preserving
    the EXACT prior H state (the actual accepted D candidate is
    retained by identity as discarded evidence)."""
    if not _state_shape(h_state):
        raise _fixed("the root-lineage state must carry an actual bounded state record")
    if not _preflight_ns_shape(ns):
        return _closed(h_state, RootLineageOutcome.REFUSED_FOREIGN_SCOPE, ())
    outer = _HOuter(ns.root_lineage_bounds.max_total_work_units)
    d_ns, gated = _gate(h_state, ns, expected_revision, outer)
    if gated is not None:
        return gated
    assert d_ns is not None
    # The charged cross-record state integrity gate (K2): actual
    # D/H integrity, retention, source provenance and the DERIVED
    # flags (re-derived from the actual D state, never trusted
    # stored bits) are validated under the ONE outer ledger before
    # any positive interpretation or D work.
    if not outer.unit():
        return _closed(
            h_state,
            RootLineageOutcome.REFUSED_OVER_BOUND,
            (RootLineageLimitation.WORK_UNITS_OVER_BOUND,),
        )
    problem = validate_root_lineage_state(
        h_state,
        ns.root_lineage_bounds,
        outer,
        history_bounds=ns.history_bounds,
        graph_bounds=ns.graph_bounds,
        proof_bounds=ns.proof_bounds,
        observation_bounds=ns.observation_bounds,
        workspace=ns.workspace,
    )
    if problem is not None:
        return _closed(h_state, _state_refusal_outcome(problem), (problem,))
    d_state = h_state.d_state
    # The pre-batch known root digest set (the relaxed envelope
    # law's membership context): ONLY the bootstrap anchor and the
    # actually EARNED authoritative root sources after the charged
    # state validation (K1) -- merely retained complete bytes do
    # not justify an envelope; a new source needs its own same-
    # batch independent authority, charged per fact.
    known: set[str] = set()
    if d_state.root is not None:
        if not outer.unit():
            return _closed(
                h_state,
                RootLineageOutcome.REFUSED_OVER_BOUND,
                (RootLineageLimitation.WORK_UNITS_OVER_BOUND,),
            )
        known.add(d_state.root.root_digest)
    for fact in h_state.root_facts:
        if not outer.unit():
            return _closed(
                h_state,
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
        return _closed(
            h_state,
            RootLineageOutcome.REFUSED_OVER_BOUND,
            (RootLineageLimitation.WORK_UNITS_OVER_BOUND,),
        )
    deferred = _deferred_digests(deferred_sink, outer)
    if deferred is None:
        return _closed(
            h_state,
            RootLineageOutcome.REFUSED_OVER_BOUND,
            (RootLineageLimitation.WORK_UNITS_OVER_BOUND,),
            d_trans,
        )
    if d_trans.outcome is CausalHistoryOutcome.REPLAYED:
        if deferred:
            # Replays earn no facts: an unknown changed envelope in
            # a replayed batch is a fixed root-authority refusal.
            return _closed(
                h_state,
                RootLineageOutcome.REFUSED_ROOT_AUTHORITY,
                (RootLineageLimitation.ENVELOPE_UNPROVEN,),
                d_trans,
            )
        if not outer.units(2 * len(d_trans.diagnostics)):
            return _closed(
                h_state,
                RootLineageOutcome.REFUSED_OVER_BOUND,
                (RootLineageLimitation.WORK_UNITS_OVER_BOUND,),
                d_trans,
            )
        limitations = tuple(_H_LIMITATION_MAP[lim] for lim in d_trans.diagnostics)
        return _closed(h_state, RootLineageOutcome.REPLAYED, limitations, d_trans)
    if d_trans.outcome is not CausalHistoryOutcome.ACCEPTED:
        return _map_d_refusal(d_trans, ctx, h_state, outer)
    # --- ACCEPTED: S3 retention + S1 re-derivation + caps + envelope ---
    old_bytes = 0
    for fact in h_state.root_facts:
        if not outer.unit():
            return _closed(
                h_state,
                RootLineageOutcome.REFUSED_OVER_BOUND,
                (RootLineageLimitation.WORK_UNITS_OVER_BOUND,),
                d_trans,
            )
        old_bytes += fact.source_byte_length
    new_facts = _new_root_facts(
        d_trans.new_occurrences,
        len(h_state.root_facts),
        old_bytes,
        ns.root_lineage_bounds,
        outer,
    )
    if new_facts is None:
        return _closed(
            h_state,
            RootLineageOutcome.REFUSED_OVER_BOUND,
            (RootLineageLimitation.WORK_UNITS_OVER_BOUND,),
            d_trans,
        )
    if isinstance(new_facts, RootLineageLimitation):
        return _closed(
            h_state,
            RootLineageOutcome.REFUSED_OVER_BOUND,
            (new_facts,),
            d_trans,
        )
    combined = _combine_facts(h_state.root_facts, new_facts, outer)
    if combined is None:
        return _closed(
            h_state,
            RootLineageOutcome.REFUSED_OVER_BOUND,
            (RootLineageLimitation.WORK_UNITS_OVER_BOUND,),
            d_trans,
        )
    derived = _derive_flags(d_trans.state, combined, outer)
    if derived is None:
        return _closed(
            h_state,
            RootLineageOutcome.REFUSED_OVER_BOUND,
            (RootLineageLimitation.WORK_UNITS_OVER_BOUND,),
            d_trans,
        )
    bounds = ns.root_lineage_bounds
    over = _retention_check(derived, bounds, outer, h_state, d_trans)
    if over is not None:
        return over
    if deferred:
        if not outer.unit():
            return _closed(
                h_state,
                RootLineageOutcome.REFUSED_OVER_BOUND,
                (RootLineageLimitation.WORK_UNITS_OVER_BOUND,),
                d_trans,
            )
        authoritative: set[str] = set()
        for fact in derived:
            if not outer.unit():
                return _closed(
                    h_state,
                    RootLineageOutcome.REFUSED_OVER_BOUND,
                    (RootLineageLimitation.WORK_UNITS_OVER_BOUND,),
                    d_trans,
                )
            if fact.authority:
                authoritative.add(fact.source_digest)
        for digest in deferred:
            if not outer.unit():
                return _closed(
                    h_state,
                    RootLineageOutcome.REFUSED_OVER_BOUND,
                    (RootLineageLimitation.WORK_UNITS_OVER_BOUND,),
                    d_trans,
                )
            if digest not in authoritative:
                return _closed(
                    h_state,
                    RootLineageOutcome.REFUSED_ROOT_AUTHORITY,
                    (RootLineageLimitation.ENVELOPE_UNPROVEN,),
                    d_trans,
                )
    if not outer.units(2 * len(new_facts)):
        return _closed(
            h_state,
            RootLineageOutcome.REFUSED_OVER_BOUND,
            (RootLineageLimitation.WORK_UNITS_OVER_BOUND,),
            d_trans,
        )
    new_keys = {_provenance_key(f.provenance) for f in new_facts}
    if not outer.units(2 * len(derived)):
        return _closed(
            h_state,
            RootLineageOutcome.REFUSED_OVER_BOUND,
            (RootLineageLimitation.WORK_UNITS_OVER_BOUND,),
            d_trans,
        )
    retained_new = tuple(f for f in derived if _provenance_key(f.provenance) in new_keys)
    if not outer.units(_STATE_BUILD_UNITS + _STATE_FACT_UNITS * len(derived)):
        return _closed(
            h_state,
            RootLineageOutcome.REFUSED_OVER_BOUND,
            (RootLineageLimitation.WORK_UNITS_OVER_BOUND,),
            d_trans,
        )
    new_state = RootLineageState(
        lineage_key=ns.lineage_key,
        revision=h_state.revision + 1,
        d_state=d_trans.state,
        root_facts=derived,
    )
    if not outer.units(_TRANSITION_BUILD_UNITS + _STATE_FACT_UNITS * len(retained_new)):
        return _closed(
            h_state,
            RootLineageOutcome.REFUSED_OVER_BOUND,
            (RootLineageLimitation.WORK_UNITS_OVER_BOUND,),
            d_trans,
        )
    return RootLineageTransition(
        state=new_state,
        outcome=RootLineageOutcome.ACCEPTED,
        d_transition=d_trans,
        revision_before=h_state.revision,
        revision_after=h_state.revision + 1,
        d_revision_before=d_trans.revision_before,
        d_revision_after=d_trans.revision_after,
        new_root_facts=retained_new,
    )


def register_root_issuance(
    h_state: RootLineageState,
    ns: RootLineageNamespace,
    call_id: str,
    endpoint: str,
    tool_name: str,
    arguments: str,
    parent_frontier: tuple[str, ...] | list[str],
    expected_revision: int,
) -> RootLineageTransition:
    """Trusted INTERNAL issuance registration under the NEW
    composition (the actual D issuance law, ONE H outer operation,
    coupled D work ledger).  Issuance is NOT source acquisition or
    success; it can -- together with a subsequent matching receipt
    -- earn a previously unproven root read its authority via the
    S1 re-derivation.  The accepted state re-derives ALL facts'
    flags; no new root fact is retained (only reads create
    occurrences)."""
    if not _state_shape(h_state):
        raise _fixed("the root-lineage state must carry an actual bounded state record")
    if not _preflight_ns_shape(ns):
        return _closed(h_state, RootLineageOutcome.REFUSED_FOREIGN_SCOPE, ())
    outer = _HOuter(ns.root_lineage_bounds.max_total_work_units)
    d_ns, gated = _gate(h_state, ns, expected_revision, outer)
    if gated is not None:
        return gated
    assert d_ns is not None
    if not outer.unit():
        return _closed(
            h_state,
            RootLineageOutcome.REFUSED_OVER_BOUND,
            (RootLineageLimitation.WORK_UNITS_OVER_BOUND,),
        )
    problem = validate_root_lineage_state(
        h_state,
        ns.root_lineage_bounds,
        outer,
        history_bounds=ns.history_bounds,
        graph_bounds=ns.graph_bounds,
        proof_bounds=ns.proof_bounds,
        observation_bounds=ns.observation_bounds,
        workspace=ns.workspace,
    )
    if problem is not None:
        return _closed(h_state, _state_refusal_outcome(problem), (problem,))
    ctx = _RootLineageContext(
        known_root_digests=frozenset(),
        relaxed_envelope_law=False,
        root_read_acquisition=False,
        outer_charge=outer.unit,
    )
    try:
        d_trans = _register_issuance_core(
            h_state.d_state,
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
        return _closed(
            h_state,
            RootLineageOutcome.REFUSED_OVER_BOUND,
            (RootLineageLimitation.WORK_UNITS_OVER_BOUND,),
        )
    if d_trans.outcome is CausalHistoryOutcome.REPLAYED:
        if not outer.units(2 * len(d_trans.diagnostics)):
            return _closed(
                h_state,
                RootLineageOutcome.REFUSED_OVER_BOUND,
                (RootLineageLimitation.WORK_UNITS_OVER_BOUND,),
                d_trans,
            )
        limitations = tuple(_H_LIMITATION_MAP[lim] for lim in d_trans.diagnostics)
        return _closed(h_state, RootLineageOutcome.REPLAYED, limitations, d_trans)
    if d_trans.outcome is not CausalHistoryOutcome.ACCEPTED:
        return _map_d_refusal(d_trans, ctx, h_state, outer)
    derived = _derive_flags(d_trans.state, h_state.root_facts, outer)
    if derived is None:
        return _closed(
            h_state,
            RootLineageOutcome.REFUSED_OVER_BOUND,
            (RootLineageLimitation.WORK_UNITS_OVER_BOUND,),
            d_trans,
        )
    if not outer.units(_STATE_BUILD_UNITS + _STATE_FACT_UNITS * len(derived)):
        return _closed(
            h_state,
            RootLineageOutcome.REFUSED_OVER_BOUND,
            (RootLineageLimitation.WORK_UNITS_OVER_BOUND,),
            d_trans,
        )
    new_state = RootLineageState(
        lineage_key=ns.lineage_key,
        revision=h_state.revision + 1,
        d_state=d_trans.state,
        root_facts=derived,
    )
    if not outer.units(_TRANSITION_BUILD_UNITS):
        return _closed(
            h_state,
            RootLineageOutcome.REFUSED_OVER_BOUND,
            (RootLineageLimitation.WORK_UNITS_OVER_BOUND,),
            d_trans,
        )
    return RootLineageTransition(
        state=new_state,
        outcome=RootLineageOutcome.ACCEPTED,
        d_transition=d_trans,
        revision_before=h_state.revision,
        revision_after=h_state.revision + 1,
        d_revision_before=d_trans.revision_before,
        d_revision_after=d_trans.revision_after,
    )


def register_root_receipt(
    h_state: RootLineageState,
    ns: RootLineageNamespace,
    call_id: str,
    endpoint: str,
    tool_name: str,
    arguments: str,
    parent_frontier: tuple[str, ...] | list[str],
    expected_revision: int,
) -> RootLineageTransition:
    """Trusted INTERNAL late-receipt registration under the NEW
    composition (the actual D receipt law, ONE H outer operation,
    coupled D work ledger).  A matching valid late receipt anchors a
    previously unanchored occurrence under its frozen frontier and
    can thereby earn a previously unproven root read its authority
    via the S1 re-derivation (even for a NONROOT ancestor's
    receipt, which opens a descendant's bootstrap path).  A
    bad/cyclic/mismatched receipt refuses atomically with the
    EXACT prior H state."""
    if not _state_shape(h_state):
        raise _fixed("the root-lineage state must carry an actual bounded state record")
    if not _preflight_ns_shape(ns):
        return _closed(h_state, RootLineageOutcome.REFUSED_FOREIGN_SCOPE, ())
    outer = _HOuter(ns.root_lineage_bounds.max_total_work_units)
    d_ns, gated = _gate(h_state, ns, expected_revision, outer)
    if gated is not None:
        return gated
    assert d_ns is not None
    if not outer.unit():
        return _closed(
            h_state,
            RootLineageOutcome.REFUSED_OVER_BOUND,
            (RootLineageLimitation.WORK_UNITS_OVER_BOUND,),
        )
    problem = validate_root_lineage_state(
        h_state,
        ns.root_lineage_bounds,
        outer,
        history_bounds=ns.history_bounds,
        graph_bounds=ns.graph_bounds,
        proof_bounds=ns.proof_bounds,
        observation_bounds=ns.observation_bounds,
        workspace=ns.workspace,
    )
    if problem is not None:
        return _closed(h_state, _state_refusal_outcome(problem), (problem,))
    ctx = _RootLineageContext(
        known_root_digests=frozenset(),
        relaxed_envelope_law=False,
        root_read_acquisition=False,
        outer_charge=outer.unit,
    )
    try:
        d_trans = _register_receipt_core(
            h_state.d_state,
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
        return _closed(
            h_state,
            RootLineageOutcome.REFUSED_OVER_BOUND,
            (RootLineageLimitation.WORK_UNITS_OVER_BOUND,),
        )
    if d_trans.outcome is CausalHistoryOutcome.REPLAYED:
        if not outer.units(2 * len(d_trans.diagnostics)):
            return _closed(
                h_state,
                RootLineageOutcome.REFUSED_OVER_BOUND,
                (RootLineageLimitation.WORK_UNITS_OVER_BOUND,),
                d_trans,
            )
        limitations = tuple(_H_LIMITATION_MAP[lim] for lim in d_trans.diagnostics)
        return _closed(h_state, RootLineageOutcome.REPLAYED, limitations, d_trans)
    if d_trans.outcome is not CausalHistoryOutcome.ACCEPTED:
        return _map_d_refusal(d_trans, ctx, h_state, outer)
    derived = _derive_flags(d_trans.state, h_state.root_facts, outer)
    if derived is None:
        return _closed(
            h_state,
            RootLineageOutcome.REFUSED_OVER_BOUND,
            (RootLineageLimitation.WORK_UNITS_OVER_BOUND,),
            d_trans,
        )
    if not outer.units(_STATE_BUILD_UNITS + _STATE_FACT_UNITS * len(derived)):
        return _closed(
            h_state,
            RootLineageOutcome.REFUSED_OVER_BOUND,
            (RootLineageLimitation.WORK_UNITS_OVER_BOUND,),
            d_trans,
        )
    new_state = RootLineageState(
        lineage_key=ns.lineage_key,
        revision=h_state.revision + 1,
        d_state=d_trans.state,
        root_facts=derived,
    )
    if not outer.units(_TRANSITION_BUILD_UNITS):
        return _closed(
            h_state,
            RootLineageOutcome.REFUSED_OVER_BOUND,
            (RootLineageLimitation.WORK_UNITS_OVER_BOUND,),
            d_trans,
        )
    return RootLineageTransition(
        state=new_state,
        outcome=RootLineageOutcome.ACCEPTED,
        d_transition=d_trans,
        revision_before=h_state.revision,
        revision_after=h_state.revision + 1,
        d_revision_before=d_trans.revision_before,
        d_revision_after=d_trans.revision_after,
    )


def _selection_kernel(
    h_state: RootLineageState,
    d_state: CausalHistoryState,
    outer: _HOuter,
) -> RootSelectionResult:
    """The charged causal-maximal selection compute.

    PRIVATE factoring for the 018-i composition: the ACTUAL
    selection law of the public query, extracted verbatim -- a fact
    B dominates A iff A is the bootstrap anchor or A's occurrence
    is a strict ancestor of B's occurrence; ALL maximal witnesses
    with ONE equal source digest are OK; differing maximal sources
    are an explicit ROOT_CONTENT_CONFLICT with NO selected source;
    no authoritative fact at all is the honest NO_SELECTED_ROOT;
    retained complete but unproven root reads expose the fixed
    ROOT_SOURCE_UNPROVEN limitation.  Every step charges the
    supplied H outer exactly as in the public query (the
    composition supplies its own H-domain adapter, so the
    independent H ceiling keeps binding beneath the composition
    total)."""
    scope_key = h_state.lineage_key
    revision = h_state.revision

    def _refused(limitation: RootLineageLimitation) -> RootSelectionResult:
        return RootSelectionResult(
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
    authoritative: list[RootLineageFact] = []
    unproven = False
    for fact in h_state.root_facts:
        if not outer.unit():
            return _refused(RootLineageLimitation.WORK_UNITS_OVER_BOUND)
        if fact.authority:
            authoritative.append(fact)
        elif fact.provenance.kind == "read":
            unproven = True
    limitations: tuple[RootLineageLimitation, ...] = (
        (RootLineageLimitation.ROOT_SOURCE_UNPROVEN,) if unproven else ()
    )
    if not authoritative:
        if not outer.units(_RESULT_BUILD_UNITS):
            return _refused(RootLineageLimitation.WORK_UNITS_OVER_BOUND)
        return RootSelectionResult(
            outcome=RootSelectionOutcome.NO_SELECTED_ROOT,
            limitations=limitations,
            lineage_key=scope_key,
            revision=revision,
        )
    ancestors: dict[tuple[str, str], set[str]] = {}
    for fact in authoritative:
        key = _provenance_key(fact.provenance)
        if not outer.unit():
            return _refused(RootLineageLimitation.WORK_UNITS_OVER_BOUND)
        if fact.provenance.kind == "read":
            try:
                ancestors[key] = _ancestors_of(fact.provenance.occurrence_id, parent_map, outer)
            except _WorkOverflowError:
                return _refused(RootLineageLimitation.WORK_UNITS_OVER_BOUND)
        else:
            ancestors[key] = set()
    dominated: set[tuple[str, str]] = set()
    for a in authoritative:
        key_a = _provenance_key(a.provenance)
        for b in authoritative:
            if not outer.unit():
                return _refused(RootLineageLimitation.WORK_UNITS_OVER_BOUND)
            if a is b:
                continue
            key_b = _provenance_key(b.provenance)
            if a.provenance.kind == "envelope" and b.provenance.kind == "read":
                dominated.add(key_a)
            elif (
                a.provenance.kind == "read"
                and b.provenance.kind == "read"
                and a.provenance.occurrence_id in ancestors[key_b]
            ):
                dominated.add(key_a)
    maximal_list: list[RootLineageFact] = []
    for f in authoritative:
        if not outer.unit():
            return _refused(RootLineageLimitation.WORK_UNITS_OVER_BOUND)
        if _provenance_key(f.provenance) not in dominated:
            maximal_list.append(f)
    if len(maximal_list) > 1 and not outer.units(len(maximal_list) * (len(maximal_list) - 1)):
        return _refused(RootLineageLimitation.WORK_UNITS_OVER_BOUND)
    maximal = tuple(sorted(maximal_list, key=lambda f: _provenance_key(f.provenance)))
    digests: set[str] = set()
    for f in maximal:
        if not outer.unit():
            return _refused(RootLineageLimitation.WORK_UNITS_OVER_BOUND)
        digests.add(f.source_digest)
    if not outer.units(_RESULT_BUILD_UNITS + _RESULT_FACT_UNITS * len(maximal)):
        return _refused(RootLineageLimitation.WORK_UNITS_OVER_BOUND)
    if len(digests) == 1:
        return RootSelectionResult(
            outcome=RootSelectionOutcome.OK,
            selected_source_digest=maximal[0].source_digest,
            witness_facts=maximal,
            limitations=limitations,
            lineage_key=scope_key,
            revision=revision,
        )
    return RootSelectionResult(
        outcome=RootSelectionOutcome.ROOT_CONTENT_CONFLICT,
        witness_facts=maximal,
        limitations=limitations,
        lineage_key=scope_key,
        revision=revision,
    )


def select_current_root(
    h_state: RootLineageState,
    ns: RootLineageNamespace,
    bounds: RootLineageBounds | None = None,
) -> RootSelectionResult:
    """The bounded pure current-root selection query.

    The O(1) shape preflight, the fixed early scope/D-state-
    binding/version fences, the charged full revalidation and the
    charged cross-record state validation (the exact domain reason
    propagates; the derived flags are re-derived from the actual D
    state, never trusted stored bits) run BEFORE any positive
    interpretation; a budget/foreign/version/malformed input is a
    fixed typed REFUSED result (never relabelled as a root absence,
    never a blanket malformed label for a capacity/work failure).
    The optional query override bounds are fresh actual-field
    validated BEFORE any fuel is read from them.  Then the causal
    maximal authoritative root facts are computed using ONLY
    frozen transitive parent evidence: a fact B dominates A iff A is
    the bootstrap anchor or A's occurrence is a strict ancestor of
    B's occurrence (a child of one branch dominates that branch's
    ancestors only; a genuine child of ALL relevant branches
    dominates all of them; delayed older receipts never override a
    proven descendant).  ALL maximal witnesses with ONE equal
    source digest are OK (the selected source with all compatible
    maximal originals retained); differing maximal sources are an
    explicit ROOT_CONTENT_CONFLICT with NO selected source; no
    authoritative fact at all is the honest NO_SELECTED_ROOT.
    Retained complete but unproven root reads are never selected and
    expose the fixed ROOT_SOURCE_UNPROVEN limitation.  The query
    never advances any revision and never manufactures a root."""
    if not _state_shape(h_state):
        raise _fixed("the root-lineage state must carry an actual bounded state record")
    scope_key = h_state.lineage_key
    revision = h_state.revision

    def _refused(limitation: RootLineageLimitation) -> RootSelectionResult:
        return RootSelectionResult(
            outcome=RootSelectionOutcome.REFUSED,
            limitations=(limitation,),
            lineage_key=scope_key,
            revision=revision,
        )

    if not _preflight_ns_shape(ns):
        return _refused(RootLineageLimitation.FOREIGN_SCOPE)
    # The optional query override bounds are fresh actual-field
    # validated (fixed O(1) closed-int model) BEFORE any fuel is
    # read from them; a malformed override is a fixed typed
    # refusal, never an unvalidated cap (K5).
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
    if h_state.lineage_key != ns.lineage_key:
        return _refused(RootLineageLimitation.FOREIGN_SCOPE)
    if h_state.d_state.history_key != ns.history_key:
        return _refused(RootLineageLimitation.FOREIGN_SCOPE)
    for actual, supported in _version_pairs(ns):
        if actual != supported:
            return _refused(RootLineageLimitation.VERSION_UNSUPPORTED)
    if not outer.units(_ns_reservation(ns)):
        return _refused(RootLineageLimitation.WORK_UNITS_OVER_BOUND)
    if not _revalidate_h_ns(ns):
        return _refused(RootLineageLimitation.FOREIGN_SCOPE)
    if not outer.unit():
        return _refused(RootLineageLimitation.WORK_UNITS_OVER_BOUND)
    problem = validate_root_lineage_state(
        h_state,
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
    d_state = h_state.d_state
    return _selection_kernel(h_state, d_state, outer)

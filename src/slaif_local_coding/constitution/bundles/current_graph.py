"""Current graph closure and version-owned withdrawal derivation
(objective 018-f, slice f; INERT).

``derive_current_graph`` is the ONE bounded pure current-graph
derivation: it takes the ACTUAL 018-d retained state, its ACTUAL
namespace, explicit current-graph bounds and explicit 018-e
currentness bounds, and derives the pure current graph over the
CURRENT semantic sources selected from the ACTUAL 018-e
per-ownership-group currentness records.

The law surface implemented here:

- construction is not authentication: early O(1) fences (history
  scope, ACTUAL-field namespace revalidation, fresh new-bounds
  validation) precede any interpretation;
- the RootAnchor is the ONLY root-text supplier and is freshly
  validated before governing use: the O(1) character count is
  checked against the inherited single-source byte cap BEFORE any
  character inspection (bytes are never fewer than characters), the
  actual UTF-8 byte length is then prefetched by a charged no-copy
  walk with an early exit at the cap that also refuses an
  unencodable (isolated-surrogate) source before any encode
  allocation, the graph-stage document/source-byte domains are
  charged for the region, and only then the owned encode copy, the
  digest recheck, and the ACTUAL field shapes and provenance: the
  workspace, the location text shape, the nonnegative original
  request index, the nonnegative/ordered/exact-length content span,
  the envelope span containment of the content span, and every
  retained occurrence's root binding — each failure a fixed typed
  refusal, never an uncaught exception;
- supplier selection happens BEFORE any scan: CURRENT proven
  singleton groups supply their exact member bytes (extracted only
  when scanned); CURRENT boundaryless groups supply their exact
  aggregate segment bytes (unattributed, no per-file hash); stale/
  conflicted/ambiguous groups and root-only groups are excluded
  (no scan, no copy, no edge, no certificate); every actual region
  copy/inspection is precharged (byte budget BEFORE the copy);
- ONE joint least fixed point from the immutable root: ordinary
  expansion over acquired current sources and group-certificate
  acceptance iterate together until no progress; a certificate
  target with a possessed current source becomes scannable in a
  later pass; certificates blocked only by not-yet-reached
  suppliers are transient and reconsidered until stable;
- the accepted common-lexical-directory law governs group
  certificates: the SAME canonical directory across ALL nonroot
  possible suppliers is checked BEFORE any target resolution,
  per-origin resolution must still agree (a disagreement is a
  corrupted-state refusal, never a pick), a root member makes the
  certificate strictly unusable, and supplier eligibility requires
  an independently current (KNOWN or OPAQUE) path reached in the
  joint fixed point — never an invented singleton hash;
- least complete AND/OR depth is relaxed after the fixed point and
  ``max_depth`` is enforced after the fixed point against the
  LEAST complete derivation (cycles never bootstrap);
- the root closure node is retained like any other node (charged
  before insertion, never an uncharged bypass of the node ceiling)
  and every emitted certificate reason entry is charged on the
  shared outer diagnostic ledger and the inherited stage
  diagnostic domain BEFORE its retention;
- ONE charged OUTER work ledger spans the ENTIRE operation
  (history validation, the nested 018-e derivation through the
  private shared-work seam, selection/interning, source/scan/
  closure/depth work and every emitted output association) plus
  the inherited graph-stage domains in their actual
  ``GraphBounds``.

No pipeline activation, no RAM service, no compiler, no disk, no
HTTP/SSE observer, no new metrics; the derivation never mutates
the input state, never advances a revision and never introduces a
clock.  The typed records and the scope-key recipe live in
``current_graph_models``.
"""

from __future__ import annotations

from collections.abc import Callable, Iterator
from dataclasses import dataclass
from typing import Any, Protocol, cast

from . import currentness as _currentness
from .bundle_proof_models import BundleProof, BundleSegment
from .causal_history_models import (
    CausalHistoryLimitation,
    CausalHistoryNamespace,
    CausalHistoryState,
    RootAnchor,
    validate_causal_history_state,
)
from .current_graph_models import (
    CURRENT_GRAPH_CONTRACT_VERSION,
    CURRENT_GRAPH_POLICY_VERSION,
    ROOT_OWNER,
    CurrentGraph,
    CurrentGraphBounds,
    CurrentGraphCandidate,
    CurrentGraphCertificate,
    CurrentGraphEdge,
    CurrentGraphEdgeKind,
    CurrentGraphLimitation,
    CurrentGraphNode,
    CurrentGraphOrigin,
    CurrentGraphOutcome,
    CurrentGraphReason,
    CurrentGraphResult,
    CurrentGraphStatus,
    CurrentGraphSupplier,
    CurrentGraphSupplierKind,
    _owner_source,
    current_graph_scope_key,
)
from .currentness_models import (
    CURRENTNESS_CONTRACT_VERSION,
    CURRENTNESS_POLICY_VERSION,
    OPAQUE_GROUP_RECIPE_VERSION,
    CurrentnessBounds,
    CurrentnessLimitation,
    CurrentnessOutcome,
    CurrentnessPathRecord,
    CurrentnessResult,
    CurrentnessStatus,
)
from .graph import resolve_reference
from .graph_models import (
    _HEX_DIGITS,
    ROOT_FILENAME,
    CandidateStatus,
    GraphBounds,
    GraphLimitation,
    ReferenceCandidate,
    _sha256_hex,
)
from .observation_models import EMPTY_SOURCE_SHA256, CharSpan
from .references import ReferenceScan, scan_references


class _OuterOverflow(Exception):
    """The private OUTER current-graph ledger crossed a ceiling."""

    __slots__ = ("limitation",)

    def __init__(self, limitation: CurrentGraphLimitation) -> None:
        self.limitation = limitation
        super().__init__(limitation.value)


class _StageOverflow(Exception):
    """An inherited graph-stage domain (actual GraphBounds) crossed."""

    __slots__ = ("limitation",)

    def __init__(self, limitation: CurrentGraphLimitation) -> None:
        self.limitation = limitation
        super().__init__(limitation.value)


class _Malformed(Exception):
    """A charged integrity check failed (maps to a closed refusal)."""

    __slots__ = ("limitation",)

    def __init__(self, limitation: CurrentGraphLimitation) -> None:
        self.limitation = limitation
        super().__init__(limitation.value)


class _BadUtf8(Exception):
    """A retained source range holds an unencodable code point.

    Isolated surrogates (``0xD800..0xDFFF``) are legal Python
    characters but unencodable in UTF-8; the bounded walk detects
    them BYTES-before any encode allocation so a corrupted retained
    source is a fixed typed refusal, never an uncaught
    ``UnicodeEncodeError``."""

    __slots__ = ()


class _OuterLedger:
    """ONE charged OUTER ledger over the ENTIRE derivation."""

    __slots__ = ("work_cap", "work_spent", "diag_cap", "diag_spent")

    def __init__(self, bounds: CurrentGraphBounds) -> None:
        self.work_cap = bounds.max_total_work_units
        self.work_spent = 0
        self.diag_cap = bounds.max_diagnostics
        self.diag_spent = 0

    def unit(self) -> bool:
        if self.work_spent + 1 > self.work_cap:
            raise _OuterOverflow(CurrentGraphLimitation.TOTAL_WORK_UNITS_OVER_BOUND)
        self.work_spent += 1
        return True

    def units(self, n: int) -> None:
        """Reserve n work units BEFORE the operation they bound
        (length-based collection reservation; each unit charges
        individually so the crossing unit refuses)."""
        for _ in range(n):
            self.unit()

    def charge(self) -> None:
        """None-returning charging view for the private 018-e seam
        (which expects ``Callable[[], None]``)."""
        self.unit()

    def diag(self) -> None:
        if self.diag_spent + 1 > self.diag_cap:
            raise _OuterOverflow(CurrentGraphLimitation.DIAGNOSTICS_FULL)
        self.diag_spent += 1


class _StageLedger:
    """The inherited graph-stage domains (the ACTUAL GraphBounds)."""

    __slots__ = (
        "bounds",
        "work_spent",
        "nodes_spent",
        "edges_spent",
        "candidates_spent",
        "documents_spent",
        "bytes_spent",
        "diag_spent",
    )

    def __init__(self, bounds: GraphBounds) -> None:
        self.bounds = bounds
        self.work_spent = 0
        self.nodes_spent = 0
        self.edges_spent = 0
        self.candidates_spent = 0
        self.documents_spent = 0
        self.bytes_spent = 0
        self.diag_spent = 0

    def unit(self) -> None:
        if self.work_spent + 1 > self.bounds.max_work_units:
            raise _StageOverflow(CurrentGraphLimitation.GRAPH_WORK_UNITS_OVER_BOUND)
        self.work_spent += 1

    def units(self, n: int) -> None:
        """Reserve n stage work units BEFORE the operation they bound
        (length-based collection reservation; each unit charges
        individually so the crossing unit refuses)."""
        for _ in range(n):
            self.unit()

    def node(self) -> None:
        if self.nodes_spent + 1 > self.bounds.max_nodes:
            raise _StageOverflow(CurrentGraphLimitation.GRAPH_NODES_OVER_BOUND)
        self.nodes_spent += 1

    def edge(self) -> None:
        if self.edges_spent + 1 > self.bounds.max_edges:
            raise _StageOverflow(CurrentGraphLimitation.GRAPH_EDGES_OVER_BOUND)
        self.edges_spent += 1

    def candidate(self) -> None:
        if self.candidates_spent + 1 > self.bounds.max_reference_candidates_total:
            raise _StageOverflow(CurrentGraphLimitation.GRAPH_CANDIDATES_OVER_BOUND)
        self.candidates_spent += 1

    def document(self) -> None:
        if self.documents_spent + 1 > self.bounds.max_documents:
            raise _StageOverflow(CurrentGraphLimitation.GRAPH_DOCUMENTS_OVER_BOUND)
        self.documents_spent += 1

    def source_bytes(self, byte_length: int) -> None:
        if byte_length > self.bounds.max_single_source_bytes:
            raise _StageOverflow(CurrentGraphLimitation.GRAPH_SOURCE_BYTES_OVER_BOUND)
        if self.bytes_spent + byte_length > self.bounds.max_total_inspected_source_bytes:
            raise _StageOverflow(CurrentGraphLimitation.GRAPH_SOURCE_BYTES_OVER_BOUND)
        self.bytes_spent += byte_length

    def diag(self) -> None:
        if self.diag_spent + 1 > self.bounds.max_diagnostics:
            raise _StageOverflow(CurrentGraphLimitation.GRAPH_DIAGNOSTICS_OVER_BOUND)
        self.diag_spent += 1


@dataclass
class _ProvenSupplier:
    """One interned CURRENT proven singleton supplier."""

    path: str
    digest: str
    occurrence_id: str
    group_index: int
    witnesses: list[str]
    coordinates: list[CurrentGraphOrigin]


@dataclass
class _OpaqueSupplier:
    """One interned CURRENT boundaryless group supplier."""

    identity: str
    group_digest: str
    members: tuple[str, ...]
    witnesses: list[str]
    coordinates: list[CurrentGraphOrigin]
    body: str
    scan: ReferenceScan


@dataclass
class _Node:
    """One closure node's honest availability facts."""

    status: CurrentGraphStatus
    digest: str | None
    owner: str | None
    witnesses: tuple[str, ...]


@dataclass
class _Certificate:
    """One group-candidate certificate (usable or retained evidence)."""

    supplier: _OpaqueSupplier
    candidate: ReferenceCandidate
    key: tuple[str, int, int, int]
    usable: bool = False
    permanent: bool = False
    reasons: tuple[CurrentGraphReason, ...] = ()
    resolved_target: str | None = None


_CURRENTNESS_MAP: dict[
    tuple[CurrentnessOutcome, CurrentnessLimitation],
    tuple[CurrentGraphOutcome, CurrentGraphLimitation],
] = {
    (
        CurrentnessOutcome.REFUSED_FOREIGN_SCOPE,
        CurrentnessLimitation.FOREIGN_SCOPE,
    ): (CurrentGraphOutcome.REFUSED_FOREIGN_SCOPE, CurrentGraphLimitation.FOREIGN_SCOPE),
    (
        CurrentnessOutcome.REFUSED_VERSION_CONFLICT,
        CurrentnessLimitation.VERSION_UNSUPPORTED,
    ): (
        CurrentGraphOutcome.REFUSED_VERSION_CONFLICT,
        CurrentGraphLimitation.VERSION_UNSUPPORTED,
    ),
    (
        CurrentnessOutcome.REFUSED_STATE_MALFORMED,
        CurrentnessLimitation.STATE_MALFORMED,
    ): (
        CurrentGraphOutcome.REFUSED_STATE_MALFORMED,
        CurrentGraphLimitation.STATE_MALFORMED,
    ),
    (
        CurrentnessOutcome.REFUSED_OVER_BOUND,
        CurrentnessLimitation.PATHS_OVER_BOUND,
    ): (CurrentGraphOutcome.REFUSED_OVER_BOUND, CurrentGraphLimitation.PATHS_OVER_BOUND),
    (
        CurrentnessOutcome.REFUSED_OVER_BOUND,
        CurrentnessLimitation.GROUPS_OVER_BOUND,
    ): (CurrentGraphOutcome.REFUSED_OVER_BOUND, CurrentGraphLimitation.GROUPS_OVER_BOUND),
    (
        CurrentnessOutcome.REFUSED_OVER_BOUND,
        CurrentnessLimitation.WITNESS_MEMBERSHIPS_OVER_BOUND,
    ): (
        CurrentGraphOutcome.REFUSED_OVER_BOUND,
        CurrentGraphLimitation.WITNESS_MEMBERSHIPS_OVER_BOUND,
    ),
    (
        CurrentnessOutcome.REFUSED_OVER_BOUND,
        CurrentnessLimitation.RELATION_PAIRS_OVER_BOUND,
    ): (
        CurrentGraphOutcome.REFUSED_OVER_BOUND,
        CurrentGraphLimitation.RELATION_PAIRS_OVER_BOUND,
    ),
    (
        CurrentnessOutcome.REFUSED_OVER_BOUND,
        CurrentnessLimitation.WORK_UNITS_OVER_BOUND,
    ): (
        CurrentGraphOutcome.REFUSED_OVER_BOUND,
        CurrentGraphLimitation.CURRENTNESS_WORK_UNITS_OVER_BOUND,
    ),
    (
        CurrentnessOutcome.REFUSED_OVER_BOUND,
        CurrentnessLimitation.DIAGNOSTICS_FULL,
    ): (
        CurrentGraphOutcome.REFUSED_OVER_BOUND,
        CurrentGraphLimitation.CURRENTNESS_DIAGNOSTICS_OVER_BOUND,
    ),
}

_DEPTH_INF = 10**9


def _refuse(
    state: CausalHistoryState,
    outcome: CurrentGraphOutcome,
    limitations: tuple[CurrentGraphLimitation, ...],
) -> CurrentGraphResult:
    return CurrentGraphResult(
        outcome=outcome,
        state=state,
        diagnostics=tuple(sorted(set(limitations), key=lambda r: r.value)),
    )


def _scan_limitation_refusal(
    state: CausalHistoryState, limitation: GraphLimitation
) -> CurrentGraphResult:
    """The accepted 018-a scan law: a scanner limitation on any
    inspected current body is a typed whole-result refusal, never a
    partial graph with a diagnostic."""
    if limitation is GraphLimitation.CANDIDATES_PER_DOCUMENT_OVER_BOUND:
        return _refuse(
            state,
            CurrentGraphOutcome.REFUSED_OVER_BOUND,
            (CurrentGraphLimitation.GRAPH_CANDIDATES_OVER_BOUND,),
        )
    # MALFORMED_UNICODE: a retained source region the accepted
    # scanner cannot decode is a corrupted retained state: fail
    # closed as malformed, never as a partial derivation.
    return _refuse(
        state,
        CurrentGraphOutcome.REFUSED_STATE_MALFORMED,
        (CurrentGraphLimitation.STATE_MALFORMED,),
    )


def _utf8_byte_length_range(text: str, start: int, end: int, cap: int) -> int:
    """Exact UTF-8 byte length of one character range, bounded.

    A no-copy charged walk (indexing only) with an EARLY EXIT: as
    soon as the accumulated byte count exceeds ``cap`` the walk
    stops and returns the unambiguous over-cap marker ``cap + 1``,
    so an over-budget region is refused without ever inspecting its
    tail.  Callers preflight the O(1) character count first (bytes
    are never fewer than characters), so the walk never needs to
    inspect more characters than ``cap`` bytes of single-byte text.
    An isolated surrogate is refused immediately (``_BadUtf8``)
    rather than silently counted, so the walk can never return a
    length for a range the owned encode could not produce.
    The byte budget is precharged with the ACTUAL length BEFORE any
    slice/encode allocation, so a forged length or an over-budget
    region never reaches an owned copy."""
    total = 0
    for index in range(start, end):
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


def _validate_anchor(
    state: CausalHistoryState,
    ns: CausalHistoryNamespace,
    anchor: RootAnchor,
    outer: _OuterLedger,
    stage: _StageLedger,
) -> None:
    """Fresh charged validation of the ACTUAL root anchor.

    ``model_validate(existing_instance)`` alone is not enough (a
    forged ``model_construct`` instance bypasses the validators),
    so EVERY actual field is freshly validated, each check charged:
    FIRST the field SHAPES — root_text is a str, root_digest a
    64-hex str, workspace a str, location a 1..1024 control-
    character-free str, first_request_index and source_byte_length
    integral (non-bool) nonnegative ints, and the content/envelope
    spans CharSpans with integral (non-bool) nonnegative
    coordinates (the content span exactly covers the root text; the
    envelope span, when present, contains it) — so no len()/
    comparison below can ever hit a wrong-type field; THEN the O(1)
    character count against the inherited single-source byte cap
    AND the remaining inspected-source byte allowance BEFORE any
    character inspection (bytes are never fewer than characters, so
    an over-count root refuses without ANY character inspection);
    the actual byte length is then prefetched by a charged no-copy
    walk with an early exit at the effective cap that also refuses
    an unencodable (isolated-surrogate) source BEFORE the owned
    encode copy can ever raise; the graph-stage document/
    source-byte domains are charged for the region before the copy;
    the digest is rechecked from that copy; the workspace is
    compared against the ACTUAL revalidated namespace workspace;
    and finally every retained occurrence's root binding is charged
    and verified.  Every failure is a fixed typed refusal
    (``ROOT_MALFORMED``; the byte-cap crossing is
    ``GRAPH_SOURCE_BYTES_OVER_BOUND``), never an uncaught
    exception.  Every validation step charges BOTH the shared outer
    work ledger and the inherited graph-stage work domain.
    """
    outer.unit()
    stage.unit()
    if not isinstance(anchor.root_text, str):
        raise _Malformed(CurrentGraphLimitation.ROOT_MALFORMED)
    outer.unit()
    stage.unit()
    if (
        not isinstance(anchor.root_digest, str)
        or len(anchor.root_digest) != 64
        or not set(anchor.root_digest) <= _HEX_DIGITS
    ):
        raise _Malformed(CurrentGraphLimitation.ROOT_MALFORMED)
    outer.unit()
    stage.unit()
    if (
        not isinstance(anchor.workspace, str)
        or not isinstance(anchor.location, str)
        or not 1 <= len(anchor.location) <= 1024
        or any(ord(c) < 0x20 or ord(c) == 0x7F for c in anchor.location)
    ):
        raise _Malformed(CurrentGraphLimitation.ROOT_MALFORMED)
    outer.unit()
    stage.unit()
    if (
        not isinstance(anchor.first_request_index, int)
        or isinstance(anchor.first_request_index, bool)
        or anchor.first_request_index < 0
    ):
        raise _Malformed(CurrentGraphLimitation.ROOT_MALFORMED)
    outer.unit()
    stage.unit()
    if (
        not isinstance(anchor.source_byte_length, int)
        or isinstance(anchor.source_byte_length, bool)
        or anchor.source_byte_length < 0
    ):
        raise _Malformed(CurrentGraphLimitation.ROOT_MALFORMED)
    outer.unit()
    stage.unit()
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
        raise _Malformed(CurrentGraphLimitation.ROOT_MALFORMED)
    outer.unit()
    stage.unit()
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
        raise _Malformed(CurrentGraphLimitation.ROOT_MALFORMED)
    outer.unit()
    stage.unit()
    cap = min(
        ns.graph_bounds.max_single_source_bytes,
        ns.graph_bounds.max_total_inspected_source_bytes - stage.bytes_spent,
    )
    if len(anchor.root_text) > cap:
        raise _StageOverflow(CurrentGraphLimitation.GRAPH_SOURCE_BYTES_OVER_BOUND)
    try:
        actual_bytes = _utf8_byte_length_range(anchor.root_text, 0, len(anchor.root_text), cap)
    except _BadUtf8:
        raise _Malformed(CurrentGraphLimitation.ROOT_MALFORMED) from None
    if actual_bytes > cap:
        raise _StageOverflow(CurrentGraphLimitation.GRAPH_SOURCE_BYTES_OVER_BOUND)
    if actual_bytes != anchor.source_byte_length:
        raise _Malformed(CurrentGraphLimitation.ROOT_MALFORMED)
    outer.unit()
    stage.document()
    stage.source_bytes(actual_bytes)
    outer.unit()
    stage.unit()
    root_bytes = anchor.root_text.encode("utf-8")
    if _sha256_hex(root_bytes) != anchor.root_digest:
        raise _Malformed(CurrentGraphLimitation.ROOT_MALFORMED)
    outer.unit()
    stage.unit()
    if anchor.workspace != ns.workspace:
        raise _Malformed(CurrentGraphLimitation.ROOT_MALFORMED)
    for occurrence in state.occurrences:
        outer.unit()
        stage.unit()
        if (
            occurrence.proof.root_path != ROOT_FILENAME
            or occurrence.proof.root_digest != anchor.root_digest
        ):
            raise _Malformed(CurrentGraphLimitation.STATE_MALFORMED)


def _segment_at(
    proof: BundleProof,
    group_index: int,
    outer: _OuterLedger,
    stage: _StageLedger,
) -> tuple[int, BundleSegment]:
    """Charged (offset, segment) for one retained proof segment.

    Raw length preflights run BEFORE any copy; every inspected
    segment is charged on BOTH the shared outer work ledger and the
    inherited graph-stage work domain before the operation.  A
    corrupted retained shape is a malformed state, never a silent
    pick."""
    outer.unit()
    stage.unit()
    if group_index >= len(proof.segments):
        raise _Malformed(CurrentGraphLimitation.STATE_MALFORMED)
    offset = 0
    for position in range(group_index):
        outer.unit()
        stage.unit()
        offset += proof.segments[position].char_length
    outer.unit()
    stage.unit()
    segment = proof.segments[group_index]
    if segment.index != group_index:
        raise _Malformed(CurrentGraphLimitation.STATE_MALFORMED)
    if offset + segment.char_length > len(proof.source_text):
        raise _Malformed(CurrentGraphLimitation.STATE_MALFORMED)
    return offset, segment


def _extract_region(
    source_text: str,
    offset: int,
    char_length: int,
    recorded_byte_length: int,
    expected_digest: str,
    outer: _OuterLedger,
    stage: _StageLedger,
) -> str:
    """Preflight, precharge, copy and digest-verify one exact region.

    The O(1) character count is checked against the inherited
    single-source byte cap AND the remaining inspected-source byte
    allowance FIRST (bytes are never fewer than characters), so an
    over-count region refuses without any character inspection --
    even when it would fit the per-source cap but not the remaining
    total budget; the ACTUAL byte length is then walked (no copy,
    early exit at the effective cap, an unencodable source is a
    fixed malformed refusal) and checked against the retained
    metadata; the graph-stage document and source-byte
    domains are charged BEFORE the owned slice copy; the digest is
    rechecked from the copy.  Any mismatch is a corrupted retained
    source: malformed state.  Every inspection step charges BOTH
    the shared outer work ledger and the inherited graph-stage work
    domain."""
    outer.unit()
    stage.unit()
    cap = min(
        stage.bounds.max_single_source_bytes,
        stage.bounds.max_total_inspected_source_bytes - stage.bytes_spent,
    )
    if char_length > cap:
        raise _StageOverflow(CurrentGraphLimitation.GRAPH_SOURCE_BYTES_OVER_BOUND)
    try:
        byte_length = _utf8_byte_length_range(source_text, offset, offset + char_length, cap)
    except _BadUtf8:
        raise _Malformed(CurrentGraphLimitation.STATE_MALFORMED) from None
    if byte_length > cap:
        raise _StageOverflow(CurrentGraphLimitation.GRAPH_SOURCE_BYTES_OVER_BOUND)
    if byte_length != recorded_byte_length:
        raise _Malformed(CurrentGraphLimitation.STATE_MALFORMED)
    stage.document()
    stage.source_bytes(byte_length)
    outer.unit()
    stage.unit()
    body = source_text[offset : offset + char_length]
    outer.unit()
    stage.unit()
    if _sha256_hex(body.encode("utf-8")) != expected_digest:
        raise _Malformed(CurrentGraphLimitation.STATE_MALFORMED)
    return body


def _dirname(path: str) -> str:
    parts = [part for part in path.split("/") if part]
    return "/".join(parts[:-1]) if len(parts) > 1 else "."


class _ChargedSortable[T](Protocol):
    """Structural input for a graph-owned sort: sized and iterable.

    mypy cannot express ``Sized & Iterable[T]`` in an annotation, so the
    same structural contract is named here; list/set/dict_values inputs
    satisfy it without any conversion.
    """

    def __len__(self) -> int: ...

    def __iter__(self) -> Iterator[T]: ...


def _charged_sort[T](
    values: _ChargedSortable[T],
    key: Callable[[T], object] | None,
    outer: _OuterLedger,
    stage: _StageLedger,
) -> list[T]:
    """Charged stable merge sort (bottom-up) for graph-owned sorts.

    The caller reserves the LINEAR part (the construction unit and
    the working-copy walk, plus any set-construction walk) BEFORE
    calling; this engine then charges every ACTUAL comparison (one
    outer + one stage unit BEFORE each comparison) and every ACTUAL
    element write into a merge output (one unit BEFORE each
    value/key-pair write), so the comparison cost is actual work,
    never a built-in-sort upper-bound assumption.  Each element's
    key is extracted ONCE (part of the reserved working copy) and
    then MOVES WITH its value through every merge pass, so later
    passes never compare stale keys.  The merge is deterministic and
    stable, so the output is identical to the built-in ``sorted``
    over the same values: exactly n element writes per doubling
    pass (n * ceil(log2 n) total) and one comparison per merge
    decision (the left run wins ties)."""
    n = len(values)
    if n <= 1:
        return list(values)
    left_vals: list[Any] = list(values)
    left_keys: list[Any] = [key(v) for v in values] if key is not None else list(values)
    right_vals: list[Any] = [None] * n
    right_keys: list[Any] = [None] * n
    width = 1
    while width < n:
        for lo in range(0, n, 2 * width):
            mid = lo + width
            hi = min(lo + 2 * width, n)
            if mid >= n:
                for idx in range(lo, n):
                    outer.unit()  # one element write (value + key pair)
                    stage.unit()
                    right_vals[idx] = left_vals[idx]
                    right_keys[idx] = left_keys[idx]
                continue
            i, j, k = lo, mid, lo
            while i < mid and j < hi:
                outer.unit()  # one comparison
                stage.unit()
                if not (left_keys[j] < left_keys[i]):  # left wins ties
                    outer.unit()  # one element write
                    stage.unit()
                    right_vals[k], right_keys[k] = left_vals[i], left_keys[i]
                    i += 1
                else:
                    outer.unit()  # one element write
                    stage.unit()
                    right_vals[k], right_keys[k] = left_vals[j], left_keys[j]
                    j += 1
                k += 1
            while i < mid:
                outer.unit()  # one element write
                stage.unit()
                right_vals[k], right_keys[k] = left_vals[i], left_keys[i]
                i += 1
                k += 1
            while j < hi:
                outer.unit()  # one element write
                stage.unit()
                right_vals[k], right_keys[k] = left_vals[j], left_keys[j]
                j += 1
                k += 1
        left_vals, right_vals = right_vals, left_vals
        left_keys, right_keys = right_keys, left_keys
        width *= 2
    return cast(list[T], left_vals)


def _sorted[T](
    values: _ChargedSortable[T],
    key: Callable[[T], object] | None,
    outer: _OuterLedger,
    stage: _StageLedger,
) -> list[T]:
    """ONE charged graph-owned sort over ``n = len(values)`` values.

    Linear reservation BEFORE the operation (both ledgers): ONE
    construction unit + n working-copy units (the one-shot key
    extraction of a keyed sort is part of that walk); the charged
    merge then accounts every actual comparison and element write.
    An empty input performs no work and reserves nothing."""
    n = len(values)
    if n == 0:
        return []
    outer.units(1 + n)
    stage.units(1 + n)
    return _charged_sort(values, key, outer, stage)


def _sort_witnesses(values: list[str], outer: _OuterLedger, stage: _StageLedger) -> tuple[str, ...]:
    """Sorted, deduplicated witness retention.

    The set dedup and the sort are ACTUAL collection work: a
    linear reservation (ONE construction unit + n membership/hash
    units for the dedup set construction over the INPUT length, so
    duplicates count, + n working-copy units for the charged sort)
    is charged on BOTH ledgers BEFORE the operation, and the
    charged merge then accounts every actual comparison and
    element write -- at every caller (node join, supplier and
    certificate output assembly)."""
    n = len(values)
    if n == 0:
        return ()
    outer.units(1 + 2 * n)
    stage.units(1 + 2 * n)
    return tuple(_charged_sort(set(values), None, outer, stage))


def _refusal_from_currentness(
    state: CausalHistoryState, cr: CurrentnessResult
) -> CurrentGraphResult:
    mapping = _CURRENTNESS_MAP.get(
        (cr.outcome, cr.diagnostics[0])
        if cr.diagnostics
        else (cr.outcome, CurrentnessLimitation.STATE_MALFORMED)
    )
    if mapping is None:
        # Fail closed: an unknown currentness pairing is a state
        # inconsistency, never interpreted as positive evidence.
        mapping = (
            CurrentGraphOutcome.REFUSED_STATE_MALFORMED,
            CurrentGraphLimitation.STATE_MALFORMED,
        )
    return _refuse(state, mapping[0], (mapping[1],))


def derive_current_graph(
    state: CausalHistoryState,
    ns: CausalHistoryNamespace,
    bounds: CurrentGraphBounds | None = None,
    currentness_bounds: CurrentnessBounds | None = None,
) -> CurrentGraphResult:
    """The ONE bounded pure current-graph derivation (018-f).

    Takes the ACTUAL 018-d state, its ACTUAL namespace and explicit
    current-graph/currentness bounds (defaults when omitted).  The
    input is the INTERNAL retained-history boundary, never a public
    supplied proof/snapshot/header authority: object construction
    is not authentication.  Unsupported coherent actual versions,
    foreign scope, malformed state, no root or exhausted derived
    resources give a fixed explicit typed refusal with NO partial
    graph; the EXACT input state is preserved on every outcome.
    Early fences are O(1) in the historical state; every later
    inspection/copy is charged on the ledgers BEFORE the operation.
    """
    # --- Early O(1) fences (no scan/copy of the historical state) ---
    if state.history_key != ns.history_key:
        return _refuse(
            state,
            CurrentGraphOutcome.REFUSED_FOREIGN_SCOPE,
            (CurrentGraphLimitation.FOREIGN_SCOPE,),
        )
    if not _currentness._revalidate_ns(ns):
        return _refuse(
            state,
            CurrentGraphOutcome.REFUSED_VERSION_CONFLICT,
            (CurrentGraphLimitation.VERSION_UNSUPPORTED,),
        )
    try:
        effective_bounds = CurrentGraphBounds.model_validate(
            CurrentGraphBounds().model_dump(warnings=False)
            if bounds is None
            else bounds.model_dump(warnings=False)
        )
    except Exception:
        raise ValueError(
            "current graph bounds failed the actual current-graph validation"
        ) from None

    outer = _OuterLedger(effective_bounds)
    stage = _StageLedger(ns.graph_bounds)
    try:
        return _derive_graph(state, ns, effective_bounds, currentness_bounds, outer, stage)
    except _OuterOverflow as overflow:
        return _refuse(state, CurrentGraphOutcome.REFUSED_OVER_BOUND, (overflow.limitation,))
    except _StageOverflow as overflow:
        return _refuse(state, CurrentGraphOutcome.REFUSED_OVER_BOUND, (overflow.limitation,))
    except _Malformed as malformed:
        return _refuse(state, CurrentGraphOutcome.REFUSED_STATE_MALFORMED, (malformed.limitation,))


def _derive_graph(
    state: CausalHistoryState,
    ns: CausalHistoryNamespace,
    bounds: CurrentGraphBounds,
    currentness_bounds: CurrentnessBounds | None,
    outer: _OuterLedger,
    stage: _StageLedger,
) -> CurrentGraphResult:
    # --- Charged 018-d history validation (own domain + shared outer) ---
    state_limitation = validate_causal_history_state(state, ns.history_bounds, work=outer.unit)
    if state_limitation is CausalHistoryLimitation.WORK_UNITS_OVER_BOUND:
        return _refuse(
            state,
            CurrentGraphOutcome.REFUSED_OVER_BOUND,
            (CurrentGraphLimitation.HISTORY_WORK_UNITS_OVER_BOUND,),
        )
    if state_limitation is not None:
        return _refuse(
            state,
            CurrentGraphOutcome.REFUSED_STATE_MALFORMED,
            (CurrentGraphLimitation.STATE_MALFORMED,),
        )

    # --- ACTUAL 018-e currentness through the private shared-work seam ---
    currentness_result = _currentness._derive(state, ns, currentness_bounds, outer=outer.charge)
    if currentness_result.outcome is not CurrentnessOutcome.OK:
        return _refusal_from_currentness(state, currentness_result)
    overlay = currentness_result.overlay
    assert overlay is not None  # ok carries its overlay (model law)

    # --- Root: the ONLY root-text supplier (fresh charged validation) ---
    anchor = state.root
    if anchor is None:
        return _refuse(
            state,
            CurrentGraphOutcome.REFUSED_NO_ROOT,
            (CurrentGraphLimitation.ROOT_MISSING,),
        )
    _validate_anchor(state, ns, anchor, outer, stage)

    # --- Actual path records and proof index (charged builds) -------
    path_records: dict[str, CurrentnessPathRecord] = {}
    for path_record in overlay.paths:
        outer.unit()
        stage.unit()
        path_records[path_record.path] = path_record
    proofs: dict[str, BundleProof] = {}
    for occurrence in state.occurrences:
        outer.unit()
        stage.unit()
        proofs[occurrence.occurrence_id] = occurrence.proof

    # --- Supplier selection (BEFORE any scan) ------------------------
    proven: dict[tuple[str, str], _ProvenSupplier] = {}
    opaque: dict[tuple[str, str, tuple[str, ...]], _OpaqueSupplier] = {}
    for group in overlay.groups:
        outer.unit()  # group interning attempt (shared + graph-stage)
        stage.unit()
        status = group.group_status
        if status not in (
            CurrentnessStatus.CURRENT_KNOWN,
            CurrentnessStatus.CURRENT_OPAQUE,
        ):
            continue  # EXCLUDED: no scan, no copy, no edge, no certificate
        proof = proofs.get(group.occurrence_id)
        if proof is None:
            raise _Malformed(CurrentGraphLimitation.STATE_MALFORMED)
        origin = CurrentGraphOrigin(
            occurrence_id=group.occurrence_id,
            group_index=group.group_index,
            request_index=proof.request_index,
            call_position=proof.call_position,
            result_position=proof.result_position,
        )
        if status is CurrentnessStatus.CURRENT_KNOWN:
            if len(group.members) != 1 or group.member_digests[0] is None:
                raise _Malformed(CurrentGraphLimitation.STATE_MALFORMED)
            path = group.members[0]
            digest = group.member_digests[0]
            if path == ROOT_FILENAME:
                continue  # the root anchor is the ONLY root-text supplier
            outer.unit()
            if group.group_index >= len(proof.segments) or (
                proof.segments[group.group_index].member_digest is not None
                and proof.segments[group.group_index].member_digest != digest
            ):
                raise _Malformed(CurrentGraphLimitation.STATE_MALFORMED)
            record = path_records.get(path)
            if (
                record is None
                or record.status is not CurrentnessStatus.CURRENT_KNOWN
                or record.known_digest != digest
            ):
                raise _Malformed(CurrentGraphLimitation.STATE_MALFORMED)
            supplier = proven.get((path, digest))
            if supplier is None:
                outer.unit()  # owner/proof metadata interned once (both ledgers)
                stage.unit()
                proven[(path, digest)] = _ProvenSupplier(
                    path=path,
                    digest=digest,
                    occurrence_id=group.occurrence_id,
                    group_index=group.group_index,
                    witnesses=[group.occurrence_id],
                    coordinates=[origin],
                )
            else:
                # A repeated contributing group retains its own
                # original coordinate even when the witness
                # occurrence is already present.
                outer.unit()  # association attempt (charged before append)
                stage.unit()
                supplier.coordinates.append(origin)
                # Duplicate witness elimination and ordering are
                # DEFERRED to the charged output retention
                # (_sort_witnesses), which accounts over the FULL
                # input length (duplicates counted); no uncharged
                # membership scan or in-place sort runs here.
                supplier.witnesses.append(group.occurrence_id)
        else:  # CURRENT_OPAQUE
            # The root-only membership scan is a linear per-member
            # walk: reserved on BOTH ledgers before it runs.
            outer.units(len(group.members))
            stage.units(len(group.members))
            if all(member == ROOT_FILENAME for member in group.members):
                continue  # a root-only group supplies nothing
            if len(group.members) < 2:
                raise _Malformed(CurrentGraphLimitation.STATE_MALFORMED)
            offset, segment = _segment_at(proof, group.group_index, outer, stage)
            key = (group.opaque_identity, segment.digest, group.members)
            opaque_supplier = opaque.get(key)
            if opaque_supplier is None:
                # First intern: the aggregate region is preflighted,
                # precharged, copied and scanned ONCE.
                body = _extract_region(
                    proof.source_text,
                    offset,
                    segment.char_length,
                    segment.byte_length,
                    segment.digest,
                    outer,
                    stage,
                )
                outer.unit()  # the aggregate scan (outer + stage)
                stage.unit()
                scan = scan_references(
                    body,
                    referring_path=None,
                    scoped_key=ns.admission_scoped_key,
                    referring_digest=None,
                    bounds=ns.graph_bounds,
                )
                if scan.limitation is not None:
                    return _scan_limitation_refusal(state, scan.limitation)
                opaque[key] = _OpaqueSupplier(
                    identity=group.opaque_identity,
                    group_digest=segment.digest,
                    members=group.members,
                    witnesses=[group.occurrence_id],
                    coordinates=[origin],
                    body=body,
                    scan=scan,
                )
            else:
                # Repeated group: retain its original coordinate;
                # witness dedup/ordering is deferred to the charged
                # output retention (full input length accounted).
                outer.unit()  # association attempt (charged before append)
                stage.unit()
                opaque_supplier.coordinates.append(origin)
                opaque_supplier.witnesses.append(group.occurrence_id)

    # --- Joint least fixed point from the immutable root ------------
    # The root closure node is retained like any other node: its
    # slot is charged on the shared outer work ledger and the
    # inherited node ceiling BEFORE insertion (no uncharged root
    # bypass of the node cap).
    outer.unit()
    stage.node()
    R: dict[str, _Node] = {
        ROOT_FILENAME: _Node(
            CurrentGraphStatus.CURRENT_KNOWN,
            anchor.root_digest,
            ROOT_OWNER,
            (),
        )
    }
    scanned: set[str] = set()
    edges: dict[tuple[str, str, str], tuple[str, ...]] = {}
    certificates: dict[tuple[str, int, int, int], _Certificate] = {}
    evaluated: set[tuple[str, int, int, int]] = set()
    candidates: dict[tuple[str, int, int, int], CurrentGraphCandidate] = {}

    def join_target(path: str) -> bool:
        """Join one resolved target with its honest status.

        Returns True on progress (a new node)."""
        if path in R:
            return False
        record = path_records.get(path)
        if record is None:
            node = _Node(CurrentGraphStatus.DISCOVERED_UNACQUIRED, None, None, ())
        elif record.status is CurrentnessStatus.CURRENT_KNOWN:
            digest = record.known_digest
            if digest is None:
                raise _Malformed(CurrentGraphLimitation.STATE_MALFORMED)
            supplier = proven.get((path, digest))
            if supplier is None:
                raise _Malformed(CurrentGraphLimitation.STATE_MALFORMED)
            owner = _owner_source(path, digest)
            witnesses = _sort_witnesses(supplier.witnesses, outer, stage)
            if digest == EMPTY_SOURCE_SHA256:
                node = _Node(CurrentGraphStatus.CURRENT_EMPTY, digest, owner, witnesses)
            else:
                node = _Node(CurrentGraphStatus.CURRENT_KNOWN, digest, owner, witnesses)
        elif record.status is CurrentnessStatus.CURRENT_OPAQUE:
            node = _Node(CurrentGraphStatus.DISCOVERED_UNACQUIRED, None, None, ())
        else:
            if record.status is CurrentnessStatus.CONTENT_CONFLICT:
                status = CurrentGraphStatus.BLOCKED_CONFLICT
            else:
                status = CurrentGraphStatus.BLOCKED_AMBIGUITY
            outer.diag()  # charged BEFORE the actual emission
            stage.diag()
            node = _Node(status, None, None, ())
        outer.unit()
        stage.node()
        R[path] = node
        return True

    def ordinary_edge(source: str, target: str, owner: str, witnesses: tuple[str, ...]) -> bool:
        """Emit one ordinary edge (dedup by (source, target, owner)).

        Returns True on a new edge."""
        outer.unit()  # association attempt (charged before dedup)
        stage.unit()
        key = (source, target, owner)
        if key in edges:
            return False
        stage.edge()
        edges[key] = witnesses
        return True

    def retain_candidate(owner: str, candidate: ReferenceCandidate) -> None:
        key = (
            owner,
            candidate.occurrence_index,
            candidate.target_char_span.start,
            candidate.target_char_span.end,
        )
        if key not in candidates:
            candidates[key] = CurrentGraphCandidate(candidate=candidate, owner=owner)

    def evaluate_certificate(
        supplier: _OpaqueSupplier,
        candidate: ReferenceCandidate,
        suppliers: tuple[str, ...],
        has_root: bool,
        no_common: bool,
    ) -> _Certificate:
        """Charged usability evaluation of one group candidate.

        A supplier is independently eligible when its path is in R
        at THIS pass AND independently current (CURRENT_KNOWN or
        CURRENT_OPAQUE path record) — an unread/group-only node
        stays honestly unavailable and still supports the group.
        A reachability-only block is transient; a supplier already
        in R but not current is permanent (path currentness is a
        fixed derivation fact)."""
        cert = _Certificate(
            supplier=supplier,
            candidate=candidate,
            key=(
                supplier.identity,
                candidate.occurrence_index,
                candidate.target_char_span.start,
                candidate.target_char_span.end,
            ),
        )
        reasons: set[CurrentGraphReason] = set()
        permanent = candidate.status is not CandidateStatus.ACCEPTED
        if has_root:
            reasons.add(CurrentGraphReason.ROOT_MEMBER_UNATTRIBUTED)
        if no_common:
            reasons.add(CurrentGraphReason.NO_COMMON_DIRECTORY)
        for member in suppliers:
            outer.unit()  # per-supplier eligibility inspection
            stage.unit()
            record = path_records.get(member)
            current = record is not None and record.status in (
                CurrentnessStatus.CURRENT_KNOWN,
                CurrentnessStatus.CURRENT_OPAQUE,
            )
            if member not in R:
                reasons.add(CurrentGraphReason.NOT_INDEPENDENTLY_REACHABLE)
            elif not current:
                reasons.add(CurrentGraphReason.NOT_INDEPENDENTLY_REACHABLE)
                permanent = True
        if candidate.status is CandidateStatus.ACCEPTED and not no_common:
            resolved: str | None = None
            first = True
            for member in suppliers:
                outer.unit()  # per-origin resolution
                stage.unit()
                got, limitation = resolve_reference(
                    member,
                    candidate.target_chars,
                    ns.workspace,
                    ns.graph_bounds.max_path_bytes,
                )
                if limitation is not None or got is None:
                    cert.candidate = candidate.model_copy(
                        update={"reasons": candidate.reasons + (limitation,)}
                    )
                    permanent = True
                    break
                if first:
                    resolved = got
                    first = False
                elif got != resolved:
                    # A common-directory disagreement is a corrupted
                    # retained state, never a silent pick.
                    raise _Malformed(CurrentGraphLimitation.STATE_MALFORMED)
            cert.resolved_target = resolved
        cert.reasons = tuple(_sorted(reasons, lambda r: r.value, outer, stage))
        cert.permanent = permanent
        cert.usable = not permanent and not reasons and cert.resolved_target is not None
        return cert

    def retain_certificate(cert: _Certificate) -> None:
        """Retain one emitted certificate.

        Every emitted reason entry is charged on the shared outer
        diagnostic ledger AND the inherited stage diagnostic domain
        BEFORE the actual retention (duplicates count before output
        dedup); a usable certificate carries no reasons."""
        for _ in cert.reasons:
            outer.diag()
            stage.diag()
        certificates[cert.key] = cert

    def certificate_phase(finalize: bool) -> bool:
        progress = False
        outer.unit()  # pass-iteration construction (owned copy)
        stage.unit()
        # The opaque-supplier iteration is a charged sort every
        # pass (linear reservation + actual comparison/writes).
        opaque_suppliers = _sorted(
            opaque.values(),
            lambda s: (s.identity, s.group_digest),
            outer,
            stage,
        )
        for supplier in opaque_suppliers:
            # Per-supplier member compound: linear reservation for
            # the member filter walk AND the any() walk BEFORE they
            # run; the dedup set sort then charges its actual
            # comparisons and element writes.
            outer.units(2 * len(supplier.members))
            stage.units(2 * len(supplier.members))
            member_set = {m for m in supplier.members if m != ROOT_FILENAME}
            has_root = any(m == ROOT_FILENAME for m in supplier.members)
            suppliers = tuple(_sorted(member_set, None, outer, stage))
            directories: set[str] = set()
            for member in suppliers:
                outer.unit()  # per-member directory inspection
                stage.unit()
                directories.add(_dirname(member))
            no_common = len(directories) > 1
            for candidate in supplier.scan.candidates:
                outer.unit()  # per-candidate visit (finalized included)
                stage.unit()  # per-candidate stage visit (finalized included)
                key = (
                    supplier.identity,
                    candidate.occurrence_index,
                    candidate.target_char_span.start,
                    candidate.target_char_span.end,
                )
                if key in certificates:
                    continue  # already finalized
                if key not in evaluated:
                    evaluated.add(key)
                    stage.candidate()
                cert = evaluate_certificate(supplier, candidate, suppliers, has_root, no_common)
                if cert.usable:
                    stage.edge()  # shared edge ceiling, before retention
                    retain_certificate(cert)
                    assert cert.resolved_target is not None
                    if join_target(cert.resolved_target):
                        progress = True
                elif cert.permanent or finalize:
                    retain_certificate(cert)
                # else: transient (reachability may improve): re-
                # evaluated in a later pass, finalized at the end.
        return progress

    def ordinary_phase() -> bool | CurrentGraphResult:
        progress = False
        outer.unit()  # pass-iteration construction (owned copy)
        stage.unit()
        # The per-pass node walk is a charged sort over R.
        paths = _sorted(R, None, outer, stage)
        for path in paths:
            outer.unit()  # per-node visit (skipped nodes included)
            stage.unit()
            if path in scanned:
                continue
            node = R[path]
            if node.status is not CurrentGraphStatus.CURRENT_KNOWN:
                continue  # CURRENT_EMPTY acquires no outgoing edges
            node_digest = node.digest
            node_owner = node.owner
            if node_digest is None or node_owner is None:
                raise _Malformed(CurrentGraphLimitation.STATE_MALFORMED)
            if path == ROOT_FILENAME:
                # The root region already paid its document/
                # source-byte domains at anchor validation (the
                # single charged inspection point for that region);
                # only the scan work is charged here.
                body = anchor.root_text
            else:
                supplier = proven[(path, node_digest)]
                offset, segment = _segment_at(
                    proofs[supplier.occurrence_id], supplier.group_index, outer, stage
                )
                outer.unit()
                if segment.digest != node_digest:
                    raise _Malformed(CurrentGraphLimitation.STATE_MALFORMED)
                body = _extract_region(
                    proofs[supplier.occurrence_id].source_text,
                    offset,
                    segment.char_length,
                    segment.byte_length,
                    node_digest,
                    outer,
                    stage,
                )
            outer.unit()  # the scan (outer + stage ledgers)
            stage.unit()
            scan = scan_references(
                body,
                referring_path=path,
                scoped_key=ns.admission_scoped_key,
                referring_digest=node_digest,
                bounds=ns.graph_bounds,
            )
            if scan.limitation is not None:
                return _scan_limitation_refusal(state, scan.limitation)
            for candidate in scan.candidates:
                outer.unit()
                stage.unit()
                stage.candidate()
                if candidate.status is not CandidateStatus.ACCEPTED:
                    retain_candidate(node_owner, candidate)
                    continue
                outer.unit()  # per-candidate resolution
                stage.unit()
                resolved, limitation = resolve_reference(
                    path,
                    candidate.target_chars,
                    ns.workspace,
                    ns.graph_bounds.max_path_bytes,
                )
                if limitation is not None or resolved is None:
                    retain_candidate(
                        node_owner,
                        candidate.model_copy(update={"reasons": candidate.reasons + (limitation,)}),
                    )
                    continue
                ordinary_edge(path, resolved, node_owner, node.witnesses)
                if join_target(resolved):
                    progress = True
            scanned.add(path)
        return progress

    progress = True
    while progress:
        phase = ordinary_phase()
        if isinstance(phase, CurrentGraphResult):
            return phase
        progress = phase | certificate_phase(False)
    certificate_phase(True)

    # --- Least complete AND/OR depth relaxation (charged) -----------
    # Depth-table construction: one unit per reachable path plus
    # the root assignment, reserved on BOTH ledgers before the walk.
    outer.units(len(R) + 1)
    stage.units(len(R) + 1)
    depth: dict[str, int] = {path: _DEPTH_INF for path in R}
    depth[ROOT_FILENAME] = 0
    # Usable-certificate selection: the charged sort, then the
    # linear filter walk reserved BEFORE it runs.
    ordered_certs = _sorted(certificates.values(), lambda c: c.key, outer, stage)
    outer.units(len(ordered_certs))
    stage.units(len(ordered_certs))
    usable_certs = [cert for cert in ordered_certs if cert.usable]
    changed = True
    while changed:
        changed = False
        # Per-iteration edge-set charged sort.
        ordered_edges = _sorted(edges, None, outer, stage)
        for source, target, _owner in ordered_edges:
            outer.unit()  # per relaxation visit
            stage.unit()
            if depth[source] >= _DEPTH_INF or target == ROOT_FILENAME:
                continue  # the root self/back-cycle target stays 0
            candidate_depth = depth[source] + 1
            if candidate_depth < depth[target]:
                depth[target] = candidate_depth
                changed = True
        for cert in usable_certs:
            outer.unit()  # per relaxation visit
            stage.unit()
            cert_target = cert.resolved_target
            assert cert_target is not None  # usable carries its target
            if cert_target == ROOT_FILENAME:
                continue
            cert_depth: int | None = None
            # Per-cert member-set filter walk (linear, reserved
            # BEFORE), then the charged dedup sort.
            outer.units(len(cert.supplier.members))
            stage.units(len(cert.supplier.members))
            cert_members = {m for m in cert.supplier.members if m != ROOT_FILENAME}
            for member in _sorted(cert_members, None, outer, stage):
                outer.unit()  # per-member depth inspection
                stage.unit()
                if depth[member] >= _DEPTH_INF:
                    cert_depth = None
                    break
                candidate_depth = 1 + depth[member]
                cert_depth = (
                    candidate_depth if cert_depth is None else max(cert_depth, candidate_depth)
                )
            if cert_depth is None:
                continue
            if cert_depth < depth[cert_target]:
                depth[cert_target] = cert_depth
                changed = True
    # Depth-check iteration charged sort.
    for path in _sorted(R, None, outer, stage):
        outer.unit()  # per-node depth inspection
        stage.unit()
        if depth[path] >= _DEPTH_INF:
            # Every join follows an emitted derivation from the
            # root, so a least derivation always exists; fail
            # closed rather than emit a bogus depth.
            raise _Malformed(CurrentGraphLimitation.STATE_MALFORMED)
        if depth[path] > ns.graph_bounds.max_depth:
            return _refuse(
                state,
                CurrentGraphOutcome.REFUSED_OVER_BOUND,
                (CurrentGraphLimitation.GRAPH_DEPTH_OVER_BOUND,),
            )

    # --- Output assembly (deterministic, version-owned) -------------
    # Every emitted output association (node, edge, certificate,
    # candidate, supplier, unreachable path) and the scope-key
    # computation are charged on BOTH ledgers BEFORE the record is
    # assembled (all output owner/witness association attempts count
    # even before interning/dedup).
    node_tuples = []
    emitted = 0
    for path in _sorted(R, None, outer, stage):
        outer.unit()  # node record emission
        stage.unit()
        node = R[path]
        if node.status in (
            CurrentGraphStatus.BLOCKED_CONFLICT,
            CurrentGraphStatus.BLOCKED_AMBIGUITY,
        ):
            emitted += 1
        node_tuples.append(
            CurrentGraphNode(
                path=path,
                status=node.status,
                digest=node.digest,
                owner=node.owner,
                witnesses=node.witnesses,
                depth=depth[path],
            )
        )
    edge_tuples = []
    for source, target, owner in _sorted(edges, None, outer, stage):
        outer.unit()  # edge record emission
        stage.unit()
        edge_tuples.append(
            CurrentGraphEdge(
                source=source,
                target=target,
                kind=CurrentGraphEdgeKind.ORDINARY,
                owner=owner,
                witnesses=edges[(source, target, owner)],
                depth=depth[source] + 1,
            )
        )
    certificate_tuples = []
    # Per-supplier immutable output metadata (sorted possible
    # origins, supplier tuple, usable-depth base, deduplicated
    # witnesses) is built ONCE per supplier and reused by every
    # certificate that supplier emitted: the set walks, dedup sorts
    # and witness retention are charged once per supplier, not
    # re-charged per candidate.
    supplier_out: dict[
        tuple[str, str, tuple[str, ...]],
        tuple[tuple[str, ...], tuple[str, ...], int | None, tuple[str, ...]],
    ] = {}
    for cert in _sorted(certificates.values(), lambda c: c.key, outer, stage):
        outer.unit()  # certificate record emission
        stage.unit()
        cert_supplier = cert.supplier
        outer.unit()  # supplier-output cache key construction + probe
        stage.unit()
        out_key = (
            cert_supplier.identity,
            cert_supplier.group_digest,
            cert_supplier.members,
        )
        cached = supplier_out.get(out_key)
        if cached is None:
            # Per-supplier possible-origin and supplier set walks
            # (linear, reserved BEFORE), then the charged dedup
            # sorts; the usable-depth walk is computed LAZILY on
            # the first usable certificate that needs it (an
            # unusable/offgraph certificate never performs a depth
            # lookup for supplier paths absent from the fixed
            # point).
            outer.units(2 * len(cert_supplier.members))
            stage.units(2 * len(cert_supplier.members))
            origin_set = set(cert_supplier.members)
            cert_supplier_set = {m for m in cert_supplier.members if m != ROOT_FILENAME}
            possible_origins = tuple(_sorted(origin_set, None, outer, stage))
            suppliers = tuple(_sorted(cert_supplier_set, None, outer, stage))
            witnesses = _sort_witnesses(cert_supplier.witnesses, outer, stage)
            cached = (possible_origins, suppliers, None, witnesses)
            supplier_out[out_key] = cached
        possible_origins, suppliers, depth_base, witnesses = cached
        if cert.usable and depth_base is None:
            # Charged usable-depth member walk: reserved BEFORE the
            # walk, computed ONCE per supplier.
            outer.units(len(suppliers))
            stage.units(len(suppliers))
            depth_base = 1 + max(depth[m] for m in suppliers)
            supplier_out[out_key] = (possible_origins, suppliers, depth_base, witnesses)
        certificate_tuples.append(
            CurrentGraphCertificate(
                group_identity=cert_supplier.identity,
                group_digest=cert_supplier.group_digest,
                members=cert_supplier.members,
                candidate=cert.candidate,
                possible_origins=possible_origins,
                suppliers=suppliers,
                resolved_target=cert.resolved_target,
                depth=depth_base if cert.usable else None,
                usable=cert.usable,
                reasons=cert.reasons,
                witnesses=witnesses,
            )
        )
        emitted += len(cert.reasons)
    candidate_list = []
    for entry in _sorted(
        candidates.values(),
        lambda c: (
            c.owner,
            c.candidate.occurrence_index,
            c.candidate.target_char_span.start,
            c.candidate.target_char_span.end,
        ),
        outer,
        stage,
    ):
        outer.unit()  # candidate record emission
        stage.unit()
        candidate_list.append(entry)
    candidate_tuples = tuple(candidate_list)
    outer.unit()  # root supplier record emission
    stage.unit()
    supplier_tuples = [
        CurrentGraphSupplier(
            kind=CurrentGraphSupplierKind.ROOT,
            path=ROOT_FILENAME,
            digest=anchor.root_digest,
        )
    ]
    for path, digest in _sorted(proven, None, outer, stage):
        prov = proven[(path, digest)]
        outer.unit()  # supplier record emission
        stage.unit()
        # Coordinate tuple copy: linear owned copy reserved BEFORE.
        outer.units(len(prov.coordinates))
        stage.units(len(prov.coordinates))
        supplier_tuples.append(
            CurrentGraphSupplier(
                kind=CurrentGraphSupplierKind.SOURCE,
                path=path,
                digest=digest,
                members=(path,),
                witnesses=_sort_witnesses(prov.witnesses, outer, stage),
                coordinates=tuple(prov.coordinates),
            )
        )
    for identity, group_digest, members in _sorted(opaque, None, outer, stage):
        opaque_supplier = opaque[(identity, group_digest, members)]
        outer.unit()  # supplier record emission
        stage.unit()
        # Coordinate tuple copy: linear owned copy reserved BEFORE.
        outer.units(len(opaque_supplier.coordinates))
        stage.units(len(opaque_supplier.coordinates))
        supplier_tuples.append(
            CurrentGraphSupplier(
                kind=CurrentGraphSupplierKind.GROUP,
                identity=identity,
                group_digest=group_digest,
                members=members,
                witnesses=_sort_witnesses(opaque_supplier.witnesses, outer, stage),
                coordinates=tuple(opaque_supplier.coordinates),
            )
        )
    # Unreachable selection: the filter walk (linear, reserved
    # BEFORE), then the charged sort over the selected paths.
    outer.units(len(proven))
    stage.units(len(proven))
    unreachable_selected = [p for (p, _digest) in proven if p not in R]
    unreachable_list = []
    for path in _sorted(unreachable_selected, None, outer, stage):
        outer.unit()  # unreachable path association
        stage.unit()
        unreachable_list.append(path)
    unreachable = tuple(unreachable_list)
    outer.unit()  # scope-key computation
    stage.unit()
    scope_key = current_graph_scope_key(
        state.history_key,
        ns.workspace,
        anchor.root_digest,
        CURRENT_GRAPH_CONTRACT_VERSION,
        CURRENT_GRAPH_POLICY_VERSION,
        ns.graph_version,
        ns.reference_version,
        ns.proof_version,
        CURRENTNESS_CONTRACT_VERSION,
        CURRENTNESS_POLICY_VERSION,
        OPAQUE_GROUP_RECIPE_VERSION,
        overlay.scope_key,
        bounds,
        overlay.bounds,
        ns.graph_bounds,
    )
    graph = CurrentGraph(
        history_key=state.history_key,
        revision=state.revision,
        workspace=ns.workspace,
        root_path=ROOT_FILENAME,
        root_digest=anchor.root_digest,
        graph_version=ns.graph_version,
        reference_version=ns.reference_version,
        proof_version=ns.proof_version,
        currentness_contract_version=CURRENTNESS_CONTRACT_VERSION,
        currentness_policy_version=CURRENTNESS_POLICY_VERSION,
        currentness_recipe_version=OPAQUE_GROUP_RECIPE_VERSION,
        contract_version=CURRENT_GRAPH_CONTRACT_VERSION,
        policy_version=CURRENT_GRAPH_POLICY_VERSION,
        bounds=bounds,
        currentness_bounds=overlay.bounds,
        graph_bounds=ns.graph_bounds,
        currentness_scope_key=overlay.scope_key,
        scope_key=scope_key,
        suppliers=tuple(supplier_tuples),
        nodes=tuple(node_tuples),
        edges=tuple(edge_tuples),
        certificates=tuple(certificate_tuples),
        candidates=candidate_tuples,
        unreachable_current_paths=unreachable,
        emitted_reasons=emitted,
    )
    return CurrentGraphResult(
        outcome=CurrentGraphOutcome.OK,
        state=state,
        overlay=graph,
        diagnostics=(),
    )

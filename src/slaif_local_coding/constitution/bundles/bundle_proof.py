"""Pure bundle-proof bridge collector (objective 018-b).

``observe_bundle_proofs`` / ``observe_bundle_proof`` take one bounded
batch of decoded :class:`GraphRequest` payloads plus ONE explicit
trusted namespace, re-derive the accepted 017 observation proof under
the namespace's ACTUAL effective ``ObservationBounds``, and earn
immutable SELF-CONTAINED bundle source proofs:

- **whole** proofs retain the 017-attributed boundaryless region (a
  complete single ``cat``, a complete finite plan with no interior
  echo, or a complete guarded loop) with the exact aggregate source
  TEXT, the requested versus proven-executed occurrences and the
  original per-piece carrier spans;
- **partitioned** proofs earn the new finite unique-marker partition:
  EVERY statement of the bounded literal ``&&`` plan is a validated
  ``cat`` / literal-absolute-``cd`` / safe-literal-``echo`` under the
  existing path and argument laws, and every marker literal plus LF
  occurs EXACTLY ONCE (ALL overlapping matches counted) in the full
  proven output, in command order, non-overlapping.  Segments are the
  maximal consecutive ``cat`` groups between proven markers; a group
  may contain A+B with unknown internal boundaries (never split); the
  per-file digest is proven only for a segment owning exactly one
  attributable member occurrence; the whole-source digest is over the
  ordered proven segments only.

No caller report flag, hash, fabricated member boundary or supplied
snapshot creates source authority: the original call identity,
inventory and structural pairing law is the accepted 017 law,
re-derived over the exact payload.  A negative old surface alone
never vetoes an independently earned positive proof; a same-occurrence
mismatched proof acquires nothing and refuses ready.

Budget law (engineering bounds, never a product guarantee): every
inspected source body (every root occurrence, duplicates included;
every selected candidate's full output; every native piece
reconstruction) is preflighted against the ACTUAL effective
``GraphBounds`` source budgets BEFORE any owned copy/retention.  The
new ``BundleProofBounds`` bound the candidate count, represented
member occurrences, per-bundle slots, marker size and the SHARED
cumulative marker-search window charge (never reset per
marker/file/request).  The module is pure: no filesystem, network or
shell facility is imported or used; no observed command is executed.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from .bundle_proof_models import (
    BUNDLE_PROOF_CONTRACT_VERSION,
    ROOT_FILENAME,
    BundleLimitation,
    BundleMarkerFact,
    BundleMarkerRole,
    BundlePiece,
    BundleProof,
    BundleProofBounds,
    BundleProofKind,
    BundleProofNamespace,
    BundleProofOutcome,
    BundleProofSnapshot,
    BundleSegment,
    BundleSourceRole,
    BundleSurface,
)
from .client_paths import validate_workspace
from .compound_reads import (
    READ_PLAN_GRAMMAR,
    PlanStatement,
    PlanStatementKind,
    ReadPlanParse,
    parse_read_plan,
)
from .graph_models import GRAPH_CONTRACT_VERSION, GraphBounds, _fixed
from .graph_observation import GraphRequest, _carrier_string
from .literal_loops import LOOP_GRAMMAR, LoopParse, parse_literal_loop
from .observation_models import (
    OBSERVER_VERSION,
    READ_GRAMMAR,
    CharSpan,
    Limitation,
    NormalizedPath,
    ObservationBounds,
    PathContext,
    ProcessObservation,
    ProcessOutcome,
    ReadCommandParse,
    ReadObservation,
    ReadOutcome,
    contains_lone_surrogates,
    sha256_hex,
)
from .observe import observe_request
from .process_chunks import _utf8_byte_length_range
from .read_grammar import parse_read_command, unwrap_call_arguments
from .tool_results import _workdir_literal


class _BridgeSourceLedger:
    """Bridge-owned cumulative source budget ledger.

    Mirrors the 018-a graph-ledger law for this slice: every inspected
    source body (every root occurrence, duplicates included; every
    selected candidate's full output; every native piece
    reconstruction) is accounted with its EXACT UTF-8 byte length
    BEFORE any bridge-owned copy/retention.  At-limit stays at-limit;
    the first over-bound body is a fixed typed refusal and no owned
    copy is made for the exceeding or later bodies.  The per-body and
    per-batch ceilings are the ACTUAL effective ``GraphBounds``
    carried by the namespace.
    """

    def __init__(self, graph_bounds: GraphBounds) -> None:
        self._max_single: int = graph_bounds.max_single_source_bytes
        self._max_total: int = graph_bounds.max_total_inspected_source_bytes
        self.total_bytes: int = 0
        self.refusal: BundleLimitation | None = None

    def account(self, byte_length: int) -> None:
        if self.refusal is not None:
            return
        if byte_length > self._max_single:
            self.refusal = BundleLimitation.SOURCE_OVER_BOUND
            return
        if self.total_bytes + byte_length > self._max_total:
            self.refusal = BundleLimitation.TOTAL_SOURCE_OVER_BOUND
            return
        self.total_bytes += byte_length


class _SearchLedger:
    """Shared cumulative marker-search window charge.

    Each marker scan charges the EXACT UTF-8 byte length of the full
    searched window (the candidate's full proven output).  The charge
    is cumulative over the whole snapshot and is NEVER reset per
    marker/file/request; the first crossing search is a fixed typed
    refusal decided BEFORE the scan runs.
    """

    def __init__(self, max_marker_search: int) -> None:
        self._max: int = max_marker_search
        self.total_bytes: int = 0
        self.refused: bool = False

    def charge(self, window_bytes: int) -> None:
        if self.refused:
            return
        if self.total_bytes + window_bytes > self._max:
            self.refused = True
            return
        self.total_bytes += window_bytes


class _PieceInfo:
    """One original output carrier with its exact join coordinates.

    ``carrier_start``/``carrier_end`` are the absolute character span
    of this carrier's exact output text inside the decoded JSON string
    that carried it; ``join_start``/``join_end`` are the corresponding
    half-open coordinates in the transient ordered concatenation
    (the virtual joined view that never becomes a carrier).
    """

    __slots__ = ("carrier_location", "carrier_start", "carrier_end", "join_start", "join_end")

    def __init__(
        self,
        carrier_location: str,
        carrier_start: int,
        carrier_end: int,
        join_start: int,
        join_end: int,
    ) -> None:
        self.carrier_location = carrier_location
        self.carrier_start = carrier_start
        self.carrier_end = carrier_end
        self.join_start = join_start
        self.join_end = join_end


def _call_arguments(payload: dict[str, Any], location: str) -> object | None:
    """The exact tool-call arguments at one 017 call location.

    Strict walker over the two 017 call-location shapes (Responses
    ``$.input[i]`` function_call item; Chat
    ``$.messages[i].tool_calls[j]`` function entry).  Any deviation
    from the schema-evidenced shape returns ``None`` (a defensive
    payload/observation mismatch, typed by the caller — never a
    guess, never an invention).
    """
    if location.startswith("$.input["):
        index_s, sep, tail = location[len("$.input[") :].partition("]")
        if tail != "" or not sep or not index_s.isdigit():
            return None
        index = int(index_s)
        items = payload.get("input")
        if not isinstance(items, list) or index >= len(items):
            return None
        item = items[index]
        if not isinstance(item, dict) or item.get("type") != "function_call":
            return None
        return item.get("arguments")
    if location.startswith("$.messages["):
        index_s, sep, tail = location[len("$.messages[") :].partition("]")
        if tail == "" or not sep or not index_s.isdigit():
            return None
        index = int(index_s)
        messages = payload.get("messages")
        if not isinstance(messages, list) or index >= len(messages):
            return None
        message = messages[index]
        if not isinstance(message, dict) or message.get("role") != "assistant":
            return None
        if not tail.startswith(".tool_calls["):
            return None
        tool_index_s, sep2, tail2 = tail[len(".tool_calls[") :].partition("]")
        if tail2 != "" or not sep2 or not tool_index_s.isdigit():
            return None
        tool_index = int(tool_index_s)
        tool_calls = message.get("tool_calls")
        if not isinstance(tool_calls, list) or tool_index >= len(tool_calls):
            return None
        tool = tool_calls[tool_index]
        if not isinstance(tool, dict) or tool.get("type") != "function":
            return None
        function = tool.get("function")
        if not isinstance(function, dict):
            return None
        return function.get("arguments")
    return None


def _call_position(location: str) -> int | None:
    """The 017-m structural call position (the Responses input item
    index, or the Chat assistant message index), or ``None`` for a
    malformed location.  Positions come from the exact structural
    location, never from lexical call IDs."""
    if location.startswith("$.input["):
        index_s, sep, tail = location[len("$.input[") :].partition("]")
        if sep and index_s.isdigit() and tail == "":
            return int(index_s)
        return None
    if location.startswith("$.messages["):
        index_s, sep, _tail = location[len("$.messages[") :].partition("]")
        if sep and index_s.isdigit():
            return int(index_s)
    return None


def _clip_join_range(
    pieces: tuple[_PieceInfo, ...], start: int, end: int
) -> tuple[CharSpan | None, ...]:
    """Map one transient joined-view range back onto the original
    carriers as ABSOLUTE per-carrier sub-spans.

    The accepted 017 mapping law: a zero-width touch keeps the real
    zero-width carrier span (never ``None``); no overlap is ``None``;
    no span over a detached substring or a virtual joined string is
    ever minted.
    """
    spans: list[CharSpan | None] = []
    for piece in pieces:
        local_start = max(start, piece.join_start)
        local_end = min(end, piece.join_end)
        if local_end >= local_start:
            offset = local_start - piece.join_start
            spans.append(
                CharSpan(
                    start=piece.carrier_start + offset,
                    end=piece.carrier_start + (local_end - piece.join_start),
                )
            )
        else:
            spans.append(None)
    return tuple(spans)


def _locate_one(full_output: str, needle: str) -> tuple[int | None, bool]:
    """One marker's scan of the full proven output.

    ALL overlapping matches are counted (the scan advances one
    character per hit).  Returns ``(first index or None, saw a
    second)`` — the charged, bounded, linear scan law.
    """
    first: int | None = None
    count = 0
    start = 0
    while True:
        index = full_output.find(needle, start)
        if index < 0:
            break
        count += 1
        if first is None:
            first = index
        start = index + 1
        if count > 1:
            break
    return first, count > 1


def _marker_order_ok(located: tuple[CharSpan, ...]) -> BundleLimitation | None:
    """The located marker spans must be strictly increasing in command
    order (non-overlapping; a collision, an order inversion or a
    duplicate is a typed refusal, never a best-looking split)."""
    for earlier, later in zip(located, located[1:], strict=False):
        if later.start <= earlier.start:
            return BundleLimitation.MARKER_ORDER
        if later.start < earlier.end:
            return BundleLimitation.MARKER_OVERLAP
    return None


class _BudgetState:
    """Cumulative represented-member-occurrence charge over the proven
    bundles.

    ``max_members`` counts represented occurrences BEFORE distinct-slot
    dedup (a repeated A+A group owns two attributable occurrences).
    The first over-bound proven bundle is a fixed typed snapshot-level
    refusal; the offending and later bundles are not retained.
    """

    def __init__(self, bounds: BundleProofBounds) -> None:
        self._max: int = bounds.max_members
        self.members_charged: int = 0
        self.refusal: BundleLimitation | None = None

    def charge(self, count: int) -> None:
        if self.refusal is not None:
            return
        if self.members_charged + count > self._max:
            self.refusal = BundleLimitation.MEMBERS_OVER_BOUND
            return
        self.members_charged += count


# Every budget bound is a SNAPSHOT-level refusal (one per bound, no
# bundles retained), never a candidate diagnostic: a snapshot-wide
# budget that is exhausted must stop ALL further candidate
# inspection/reconstruction work (no unbounded find/search/copy
# beyond the bound).
_BUDGET_REASONS: frozenset[BundleLimitation] = frozenset(
    {
        BundleLimitation.BATCH_OVER_BOUND,
        BundleLimitation.BUNDLES_OVER_BOUND,
        BundleLimitation.SOURCE_OVER_BOUND,
        BundleLimitation.TOTAL_SOURCE_OVER_BOUND,
        BundleLimitation.MEMBERS_OVER_BOUND,
        BundleLimitation.SEGMENTS_OVER_BOUND,
        BundleLimitation.MARKER_OVER_BOUND,
        BundleLimitation.MARKER_SEARCH_OVER_BOUND,
        BundleLimitation.DIAGNOSTICS_FULL,
    }
)


def _member_paths_within_bounds(
    members: tuple[NormalizedPath, ...], namespace: BundleProofNamespace
) -> BundleLimitation | None:
    """Both ACTUAL path ceilings bound every normalized represented
    member reference: the effective ``GraphBounds`` path bound (the
    bridge source scope, order 83/84) and the effective
    ``ObservationBounds`` path bound (the 017 reparse enforces its own
    half; the bridge re-checks both explicitly).  UTF-8 bytes, never
    characters.  A violation is the fixed typed
    ``MEMBER_PATH_OVER_BOUND`` non-acquisition (a candidate
    diagnostic): no source, digest or proof follows from an
    over-bound reference.  Unresolved members are typed separately
    (``MEMBER_UNRESOLVED`` downstream)."""
    graph_max = namespace.graph_bounds.max_path_bytes
    obs_max = namespace.observation_bounds.max_path_bytes
    for member in members:
        normalized = member.normalized
        if normalized is None:
            continue
        length = len(normalized.encode("utf-8"))
        if length > graph_max or length > obs_max:
            return BundleLimitation.MEMBER_PATH_OVER_BOUND
    return None


def _runs_and_members(
    statements: tuple[PlanStatement, ...],
) -> tuple[tuple[tuple[int, ...], ...], tuple[tuple[int, ...], ...]]:
    """Maximal non-echo statement runs and each run's ordered cat
    member positions.

    One run exists at each end and between every consecutive marker,
    so ``len(runs) == len(echo statements) + 1``; a run without a cat
    statement produces no output and its slot must be EMPTY.  Member
    positions are occurrence positions into the plan's
    ``requested_members`` (statement/operand order, never a lexical
    sort).
    """
    runs: list[tuple[int, ...]] = []
    current: list[int] = []
    for index, statement in enumerate(statements):
        if statement.kind is PlanStatementKind.ECHO:
            runs.append(tuple(current))
            current = []
        else:
            current.append(index)
    runs.append(tuple(current))
    members: list[tuple[int, ...]] = []
    next_position = 0
    for run in runs:
        positions: list[int] = []
        for statement_index in run:
            statement = statements[statement_index]
            if statement.kind is PlanStatementKind.CAT:
                operand_count = len(statement.cat_operands)
                positions.extend(range(next_position, next_position + operand_count))
                next_position += operand_count
        members.append(tuple(positions))
    return tuple(runs), tuple(members)


def _finite_marker_plan(
    plan: ReadPlanParse, bounds: BundleProofBounds
) -> tuple[tuple[str, ...] | None, BundleLimitation | None]:
    """The finite unique-marker plan predicate.

    Earned ONLY when every statement is clean (no typed reasons) with
    a kind in {cat, cd, echo}: cats carry at least one fully
    normalized operand; cds carry their validated absolute target;
    echo literals are present and NONEMPTY.  At least one cat
    statement must exist; marker literals must be pairwise distinct;
    each marker's UTF-8 byte length INCLUDING the emitted LF must be
    within ``max_marker``.  LS/sleep/semicolon/glob/substitution/
    redirection/heredoc/dynamic/loop forms carry typed reasons or an
    OTHER kind and are refused here.
    """
    literals: list[str] = []
    has_cat = False
    for statement in plan.statements:
        if statement.reasons:
            return None, BundleLimitation.PLAN_UNSUPPORTED
        if statement.kind is PlanStatementKind.CAT:
            if not statement.cat_operands:
                return None, BundleLimitation.PLAN_UNSUPPORTED
            if any(operand.normalized is None for operand in statement.cat_operands):
                return None, BundleLimitation.MEMBER_UNRESOLVED
            has_cat = True
        elif statement.kind is PlanStatementKind.CD:
            if statement.cd_target is None:
                return None, BundleLimitation.PLAN_UNSUPPORTED
        elif statement.kind is PlanStatementKind.ECHO:
            literal = statement.echo_literal
            if literal is None or literal == "":
                return None, BundleLimitation.MARKER_EMPTY
            literals.append(literal)
        else:
            return None, BundleLimitation.PLAN_UNSUPPORTED
    if not has_cat:
        return None, BundleLimitation.PLAN_UNSUPPORTED
    for literal in literals:
        if len((literal + "\n").encode("utf-8")) > bounds.max_marker:
            return None, BundleLimitation.MARKER_OVER_BOUND
    if len(set(literals)) != len(literals):
        return None, BundleLimitation.MARKER_DUPLICATE
    return tuple(literals), None


def _unwrap_for_reparse(
    arguments: object, context: PathContext, bounds: ObservationBounds
) -> tuple[str, PathContext] | None:
    """The exact command string and effective call context.

    Mirrors the 017 reparse law: an unsupported or non-literal per-
    call workdir, and an unencodable workdir spelling, are typed
    absent before any grammar is consulted (never a fallback to the
    batch context).
    """
    unwrapped = unwrap_call_arguments(arguments, bounds.max_command_chars)
    if unwrapped is None or (
        unwrapped.workdir is not None and not _workdir_literal(unwrapped.workdir)
    ):
        return None
    if unwrapped.workdir is not None and contains_lone_surrogates(unwrapped.workdir):
        return None
    call_context = context
    if unwrapped.workdir is not None:
        call_context = PathContext(workspace=context.workspace, workdir=unwrapped.workdir)
    return unwrapped.command, call_context


def _parse_forms(
    command: str, call_context: PathContext, bounds: ObservationBounds
) -> tuple[ReadCommandParse, ReadPlanParse, LoopParse]:
    """The three bounded grammar parses (single, plan, loop) under the
    ACTUAL effective 017 bounds; command syntax is data, nothing is
    executed or expanded."""
    parsed = parse_read_command(
        command,
        call_context,
        bounds.max_command_chars,
        bounds.max_operands,
        bounds.max_path_bytes,
    )
    plan = parse_read_plan(
        command,
        call_context,
        bounds.max_command_chars,
        bounds.max_operands,
        bounds.max_path_bytes,
    )
    loop = parse_literal_loop(
        command,
        call_context,
        bounds.max_command_chars,
        bounds.max_operands,
        bounds.max_path_bytes,
    )
    return parsed, plan, loop


def _selected_form(
    parsed: ReadCommandParse, plan: ReadPlanParse, loop: LoopParse
) -> tuple[str, tuple[NormalizedPath, ...], str, str | None]:
    """The 017 grammar-identity selection:
    ``(form, requested members, grammar, command digest)``.

    ``form`` is ``"single"`` (a complete all-cat parse), ``"plan"``
    (a complete finite plan, or the typed plan domain) or ``"loop"``
    (the loop parser's domain).  The selection mirrors the accepted 017
    grammar-identity law exactly, so the re-derived requested members
    equal the observation's.
    """
    if parsed.complete:
        return "single", parsed.operands, READ_GRAMMAR, parsed.command_digest
    if plan.complete:
        return "plan", plan.requested_members, READ_PLAN_GRAMMAR, plan.command_digest
    if loop.is_loop_attempt:
        return "loop", loop.requested_members, LOOP_GRAMMAR, loop.command_digest
    return "plan", plan.requested_members, READ_PLAN_GRAMMAR, plan.command_digest


def _bundle_proof(
    *,
    surface: BundleSurface,
    kind: BundleProofKind,
    grammar: str,
    command_digest: str | None,
    request_index: int,
    call_id: str,
    call_location: str,
    call_position: int,
    result_location: str,
    result_position: int,
    endpoint: str,
    root_digest: str,
    requested: tuple[NormalizedPath, ...],
    pieces: tuple[BundlePiece, ...],
    segments: tuple[BundleSegment, ...],
    markers: tuple[BundleMarkerFact, ...],
    source_text: str,
) -> BundleProof:
    """The self-contained proof record (invariants bind every
    length/digest to the exact aggregate source text)."""
    resolved = [member.normalized for member in requested]
    if any(path is None for path in resolved):
        raise _fixed("proven_executed paths must all be resolved")
    proven = tuple(path for path in resolved if path is not None)
    distinct = len(set(resolved))
    return BundleProof(
        surface=surface,
        kind=kind,
        grammar=grammar,
        command_digest=command_digest,
        request_index=request_index,
        call_id=call_id,
        call_location=call_location,
        call_position=call_position,
        result_location=result_location,
        result_position=result_position,
        endpoint=endpoint,
        source_role=BundleSourceRole.FILE_TOOL_RESULT,
        root_path=ROOT_FILENAME,
        root_digest=root_digest,
        requested_members=requested,
        proven_executed=proven,
        distinct_member_count=distinct,
        pieces=pieces,
        segments=segments,
        markers=markers,
        source_text=source_text,
        source_char_length=len(source_text),
        source_byte_length=len(source_text.encode("utf-8")),
        source_digest=sha256_hex(source_text),
    )


def _plan_echo_split(plan: ReadPlanParse) -> tuple[list[tuple[int, str]], list[tuple[int, str]]]:
    """The plan's (prefix, suffix) echo statements as
    ``(statement index, literal)`` pairs in command order.

    Only a COMPLETE plan (no interior echo, no typed reasons) reaches
    this helper: every echo is a proven outer boundary at its exact
    position, and every earned echo carries its literal.
    """
    cat_indexes = [
        index for index, st in enumerate(plan.statements) if st.kind is PlanStatementKind.CAT
    ]
    first_cat, last_cat = cat_indexes[0], cat_indexes[-1]
    prefix: list[tuple[int, str]] = []
    suffix: list[tuple[int, str]] = []
    for index, st in enumerate(plan.statements):
        if st.kind is not PlanStatementKind.ECHO:
            continue
        literal = st.echo_literal
        if literal is None:
            # A complete earned plan never loses a literal; defensive.
            raise _fixed("a complete plan echo lost its literal")
        if index < first_cat:
            prefix.append((index, literal))
        elif index > last_cat:
            suffix.append((index, literal))
    return prefix, suffix


def _read_plan_boundary_markers(
    plan: ReadPlanParse, content_span: CharSpan, carrier: str
) -> tuple[BundleMarkerFact, ...] | None:
    """The proven prefix/suffix marker facts of a whole legacy plan.

    The marker lines sit OUTSIDE the 017-attributed region (the
    carrier before/after it) and are byte-verified against the plan
    literals; any mismatch is a defensive ``None`` (typed by the
    caller as ``OUTPUT_INCONSISTENT``).  Facts are ordered by
    statement index (prefix first, then suffix).
    """
    prefix, suffix = _plan_echo_split(plan)
    prefix_total = sum(len(literal) + 1 for _, literal in prefix)
    suffix_total = sum(len(literal) + 1 for _, literal in suffix)
    base = content_span.start
    prefix_text = "".join(literal + "\n" for _, literal in prefix)
    if prefix_total and carrier[base - prefix_total : base] != prefix_text:
        return None
    suffix_text = "".join(literal + "\n" for _, literal in suffix)
    if suffix_total and carrier[content_span.end : content_span.end + suffix_total] != suffix_text:
        return None
    facts: list[BundleMarkerFact] = []
    offset = 0
    for index, literal in prefix:
        text = literal + "\n"
        start = base - prefix_total + offset
        facts.append(
            BundleMarkerFact(
                index=index,
                role=BundleMarkerRole.PREFIX,
                char_length=len(text),
                byte_length=len(text.encode("utf-8")),
                digest=sha256_hex(text),
                piece_spans=(CharSpan(start=start, end=start + len(text)),),
            )
        )
        offset += len(text)
    offset = 0
    for index, literal in suffix:
        text = literal + "\n"
        start = content_span.end + offset
        facts.append(
            BundleMarkerFact(
                index=index,
                role=BundleMarkerRole.SUFFIX,
                char_length=len(text),
                byte_length=len(text.encode("utf-8")),
                digest=sha256_hex(text),
                piece_spans=(CharSpan(start=start, end=start + len(text)),),
            )
        )
        offset += len(text)
    return tuple(facts)


def _process_plan_boundary_markers(
    plan: ReadPlanParse,
    pieces_info: tuple[_PieceInfo, ...],
    full_output: str,
    region_spans: tuple[CharSpan | None, ...],
) -> tuple[BundleMarkerFact, ...] | None:
    """The proven prefix/suffix marker facts of a whole native plan.

    The region's joined-view coordinates are recovered from the
    accepted per-piece mapping (contiguous by law); the prefix/suffix
    echo lines are byte-verified against the plan literals in the full
    proven output, and their marker intervals are mapped back onto the
    original pieces (the zero-width touch law applies).
    """
    region_start: int | None = None
    region_end: int | None = None
    for span, info in zip(region_spans, pieces_info, strict=True):
        if span is not None:
            join_start = info.join_start + (span.start - info.carrier_start)
            join_end = info.join_start + (span.end - info.carrier_start)
            if region_start is None:
                region_start = join_start
            region_end = join_end
    if region_start is None or region_end is None:
        return None
    prefix, suffix = _plan_echo_split(plan)
    prefix_total = sum(len(literal) + 1 for _, literal in prefix)
    suffix_total = sum(len(literal) + 1 for _, literal in suffix)
    if region_start != prefix_total or region_end != len(full_output) - suffix_total:
        return None
    prefix_text = "".join(literal + "\n" for _, literal in prefix)
    if full_output[:prefix_total] != prefix_text:
        return None
    suffix_text = "".join(literal + "\n" for _, literal in suffix)
    if full_output[region_end:] != suffix_text:
        return None
    facts: list[BundleMarkerFact] = []
    offset = 0
    for index, literal in prefix:
        text = literal + "\n"
        facts.append(
            BundleMarkerFact(
                index=index,
                role=BundleMarkerRole.PREFIX,
                char_length=len(text),
                byte_length=len(text.encode("utf-8")),
                digest=sha256_hex(text),
                piece_spans=_clip_join_range(pieces_info, offset, offset + len(text)),
            )
        )
        offset += len(text)
    offset = 0
    for index, literal in suffix:
        text = literal + "\n"
        start = region_end + offset
        facts.append(
            BundleMarkerFact(
                index=index,
                role=BundleMarkerRole.SUFFIX,
                char_length=len(text),
                byte_length=len(text.encode("utf-8")),
                digest=sha256_hex(text),
                piece_spans=_clip_join_range(pieces_info, start, start + len(text)),
            )
        )
        offset += len(text)
    return tuple(facts)


def _partition_segments_and_markers(
    plan: ReadPlanParse,
    located: tuple[CharSpan, ...],
    full_output: str,
    pieces_info: tuple[_PieceInfo, ...],
    bounds: BundleProofBounds,
) -> tuple[
    tuple[BundleSegment, ...] | None,
    tuple[BundleMarkerFact, ...] | None,
    str | None,
    BundleLimitation | None,
]:
    """The finite unique-marker partition over the full proven output.

    Runs (maximal non-echo statement blocks) align positionally with
    the slots between located markers: a cat run owns its slot's bytes
    as ONE boundaryless segment (a group may contain A+B with unknown
    internal boundaries, never split); a run without a cat statement
    must have an EMPTY slot (``SEGMENT_UNEXPLAINED`` otherwise).
    Returns ``(segments, markers, source_text, limitation)``.
    """
    runs, run_members = _runs_and_members(plan.statements)
    slots: list[tuple[int, int]] = []
    previous = 0
    for span in located:
        slots.append((previous, span.start))
        previous = span.end
    slots.append((previous, len(full_output)))
    if len(slots) != len(runs):
        # Structural invariant (runs == markers + 1); never reachable.
        return None, None, None, BundleLimitation.OUTPUT_INCONSISTENT
    if len(slots) > bounds.max_segments:
        return None, None, None, BundleLimitation.SEGMENTS_OVER_BOUND
    cat_indexes = [
        index for index, st in enumerate(plan.statements) if st.kind is PlanStatementKind.CAT
    ]
    first_cat, last_cat = cat_indexes[0], cat_indexes[-1]
    facts: list[BundleMarkerFact] = []
    marker_counter = 0
    for st_index, st in enumerate(plan.statements):
        if st.kind is not PlanStatementKind.ECHO:
            continue
        literal = st.echo_literal
        if literal is None:
            return None, None, None, BundleLimitation.OUTPUT_INCONSISTENT
        span = located[marker_counter]
        marker_counter += 1
        if st_index < first_cat:
            role = BundleMarkerRole.PREFIX
        elif st_index > last_cat:
            role = BundleMarkerRole.SUFFIX
        else:
            role = BundleMarkerRole.INTERIOR
        text = literal + "\n"
        facts.append(
            BundleMarkerFact(
                index=st_index,
                role=role,
                char_length=len(text),
                byte_length=len(text.encode("utf-8")),
                digest=sha256_hex(text),
                piece_spans=_clip_join_range(pieces_info, span.start, span.end),
            )
        )
    segments: list[BundleSegment] = []
    source_parts: list[str] = []
    segment_index = 0
    for members, (slot_start, slot_end) in zip(run_members, slots, strict=True):
        slot_text = full_output[slot_start:slot_end]
        if not members:
            if slot_text != "":
                return None, None, None, BundleLimitation.SEGMENT_UNEXPLAINED
            continue
        source_parts.append(slot_text)
        digest = sha256_hex(slot_text)
        segments.append(
            BundleSegment(
                index=segment_index,
                member_positions=members,
                char_length=len(slot_text),
                byte_length=len(slot_text.encode("utf-8")),
                digest=digest,
                member_digest=digest if len(members) == 1 else None,
                piece_spans=_clip_join_range(pieces_info, slot_start, slot_end),
            )
        )
        segment_index += 1
    return tuple(segments), tuple(facts), "".join(source_parts), None


def _read_bundle(
    request_index: int,
    read: ReadObservation,
    payload: dict[str, Any],
    context: PathContext,
    namespace: BundleProofNamespace,
    bounds: BundleProofBounds,
    search: _SearchLedger,
    budget: _BudgetState,
    root_digest: str,
) -> tuple[BundleProof | None, BundleLimitation | None]:
    """One selected legacy read candidate to a whole/partition proof.

    Returns ``(proof, None)`` or ``(None, limitation)``.  The
    cumulative member preflight is charged by the caller BEFORE any
    output-carrier fetch (already-parsed 017 member metadata); the
    builder keeps only the defensive no-charge refusal check so a
    standalone call can never allocate a proof under an active
    member refusal.
    """
    output_span = read.wrapper.output_span
    if output_span is None:
        return None, BundleLimitation.OUTPUT_INCONSISTENT  # defensive
    call_position = _call_position(read.call_location)
    if call_position is None:
        return None, BundleLimitation.OUTPUT_INCONSISTENT
    # The strict result pointer (``$.input[i]`` / ``$.messages[i]``)
    # supplies the exact numeric result position: retain it.
    result_position = _call_position(read.result_location)
    if result_position is None:
        return None, BundleLimitation.OUTPUT_INCONSISTENT
    arguments = _call_arguments(payload, read.call_location)
    if arguments is None:
        return None, BundleLimitation.OUTPUT_INCONSISTENT
    unwrapped = _unwrap_for_reparse(arguments, context, namespace.observation_bounds)
    if unwrapped is None:
        return None, BundleLimitation.PLAN_UNSUPPORTED
    command, call_context = unwrapped
    parsed, plan, loop = _parse_forms(command, call_context, namespace.observation_bounds)
    form, requested, grammar, command_digest = _selected_form(parsed, plan, loop)
    if requested != read.requested_members:
        return None, BundleLimitation.OUTPUT_INCONSISTENT
    if any(member.normalized is None for member in requested):
        return None, BundleLimitation.MEMBER_UNRESOLVED
    # The caller already charged the represented member occurrences
    # (already-parsed 017 metadata) BEFORE any output-carrier fetch:
    # at-limit stays at-limit, the first over-bound proven candidate
    # is a fixed typed snapshot refusal, never a post-fetch or
    # post-allocation discard.
    if budget.refusal is not None:
        return None, BundleLimitation.MEMBERS_OVER_BOUND
    # The single original output carrier (the complete proven output
    # region of the result); fetched only after the preflight and
    # shared by both proof forms.
    carrier = _carrier_string(payload, read.result_location)
    if carrier is None or output_span.end > len(carrier):
        return None, BundleLimitation.OUTPUT_INCONSISTENT

    body_bytes = _utf8_byte_length_range(carrier, output_span.start, output_span.end)
    if body_bytes is None:
        return None, BundleLimitation.OUTPUT_INCONSISTENT
    pieces = (
        BundlePiece(
            piece_index=0,
            carrier_location=read.result_location,
            char_span=output_span,
            char_length=output_span.end - output_span.start,
            byte_length=body_bytes,
            call_id=read.call_id,
            call_location=read.call_location,
            call_position=call_position,
            result_position=result_position,
        ),
    )

    whole = form in ("single", "loop") or (form == "plan" and plan.complete)
    if whole:
        if (
            read.outcome is not ReadOutcome.COMPLETE
            or not read.removable
            or read.content_span is None
            or read.bundle_digest is None
        ):
            return None, BundleLimitation.OUTPUT_INCONSISTENT
        content_span = read.content_span
        source = carrier[content_span.start : content_span.end]
        if sha256_hex(source) != read.bundle_digest:
            return None, BundleLimitation.OUTPUT_INCONSISTENT
        markers: tuple[BundleMarkerFact, ...] = ()
        if form == "plan":
            boundary_markers = _read_plan_boundary_markers(plan, content_span, carrier)
            if boundary_markers is None:
                return None, BundleLimitation.OUTPUT_INCONSISTENT
            markers = boundary_markers
        proof = _bundle_proof(
            surface=BundleSurface.READ,
            kind=BundleProofKind.WHOLE,
            grammar=grammar,
            command_digest=command_digest,
            request_index=request_index,
            call_id=read.call_id,
            call_location=read.call_location,
            call_position=call_position,
            result_location=read.result_location,
            result_position=result_position,
            endpoint=read.endpoint,
            root_digest=root_digest,
            requested=requested,
            pieces=pieces,
            segments=(
                BundleSegment(
                    index=0,
                    member_positions=tuple(range(len(requested))),
                    char_length=len(source),
                    byte_length=len(source.encode("utf-8")),
                    digest=sha256_hex(source),
                    member_digest=sha256_hex(source) if len(requested) == 1 else None,
                    piece_spans=(content_span,),
                ),
            ),
            markers=markers,
            source_text=source,
        )
        return proof, None

    # form == "plan" (incomplete) or "loop" (incomplete attempt).
    if form == "loop":
        # A loop command is not a finite ``&&`` plan: typed, never
        # partitioned.
        return None, BundleLimitation.PLAN_UNSUPPORTED
    literals, predicate = _finite_marker_plan(plan, bounds)
    if literals is None:
        return None, predicate
    if read.wrapper.reasons != ():
        # The all-success partition requirement (global exit zero, no
        # truncation/unknown/missing) is not proven by this wrapper.
        return None, BundleLimitation.OUTPUT_INCONSISTENT
    full_output = carrier[output_span.start : output_span.end]
    window_bytes = _utf8_byte_length_range(carrier, output_span.start, output_span.end)
    if window_bytes is None:
        return None, BundleLimitation.OUTPUT_INCONSISTENT
    located: list[CharSpan] = []
    for literal in literals:
        if search.refused:
            return None, BundleLimitation.MARKER_SEARCH_OVER_BOUND
        search.charge(window_bytes)
        if search.refused:
            return None, BundleLimitation.MARKER_SEARCH_OVER_BOUND
        first, duplicate = _locate_one(full_output, literal + "\n")
        if first is None:
            return None, BundleLimitation.MARKER_MISSING
        if duplicate:
            return None, BundleLimitation.MARKER_DUPLICATE
        located.append(CharSpan(start=first, end=first + len(literal) + 1))
    order_reason = _marker_order_ok(tuple(located))
    if order_reason is not None:
        return None, order_reason
    pieces_info = (
        _PieceInfo(read.result_location, output_span.start, output_span.end, 0, len(full_output)),
    )
    segments, partition_markers, source_text, reason = _partition_segments_and_markers(
        plan, tuple(located), full_output, pieces_info, bounds
    )
    if segments is None or partition_markers is None or source_text is None:
        return None, reason
    proof = _bundle_proof(
        surface=BundleSurface.READ,
        kind=BundleProofKind.PARTITIONED,
        grammar=READ_PLAN_GRAMMAR,
        command_digest=plan.command_digest,
        request_index=request_index,
        call_id=read.call_id,
        call_location=read.call_location,
        call_position=call_position,
        result_location=read.result_location,
        result_position=result_position,
        endpoint=read.endpoint,
        root_digest=root_digest,
        requested=requested,
        pieces=pieces,
        segments=segments,
        markers=partition_markers,
        source_text=source_text,
    )
    return proof, None


def _bundle_refusal(
    namespace: BundleProofNamespace,
    outcome: BundleProofOutcome,
    conflicts: tuple[BundleLimitation, ...],
    request_count: int,
    limitations: tuple[Limitation, ...],
    candidates_inspected: int = 0,
    source_bytes_inspected: int = 0,
    marker_search_bytes: int = 0,
) -> BundleProofSnapshot:
    """A typed snapshot refusal with a bounded final diagnostic.

    Total emitted fixed diagnostics (fixed reasons + copied
    observation/global limitations) are bounded by ``max_diagnostics``
    at every public refusal: overflow is ONE fixed ``DIAGNOSTICS_FULL``
    refusal, never unbounded copied reasons (no silent truncation, no
    governance loss).
    """
    if len(conflicts) + len(limitations) > namespace.bounds.max_diagnostics:
        return BundleProofSnapshot(
            namespace=namespace,
            outcome=BundleProofOutcome.OVER_BOUND,
            conflicts=(BundleLimitation.DIAGNOSTICS_FULL,),
            request_count=request_count,
            candidates_inspected=candidates_inspected,
            source_bytes_inspected=source_bytes_inspected,
            marker_search_bytes=marker_search_bytes,
        )
    return BundleProofSnapshot(
        namespace=namespace,
        outcome=outcome,
        conflicts=conflicts,
        request_count=request_count,
        observation_limitations=limitations,
        candidates_inspected=candidates_inspected,
        source_bytes_inspected=source_bytes_inspected,
        marker_search_bytes=marker_search_bytes,
    )


def _seam_signature(proof: BundleProof) -> tuple[object, ...]:
    """The same-occurrence proof signature the consistency law compares
    BEFORE retention.

    Path/digest alone is not the contracted proof: the signature
    carries the full common source/member/ownership/original-carrier/
    authority facts — the structural call/result positions, the
    ordered resolved member paths, the exact command digest, the
    ordered normalized REQUESTED members (kept distinct from the
    proven-executed paths), the exact source digest, each piece's
    carrier evidence and per-piece call identity/location plus
    call/result association, each segment's ordered member positions
    and per-file digest, each marker fact, and the
    endpoint/source-role/root-authority binding.  The private call
    ID values stay internal association data: the signature is
    compared in memory only and never rendered, logged, or reused as
    semantic compiler/cache key material.
    The 017 parser ``surface`` is deliberately NOT part of the
    signature: one physical occurrence is compared across the read
    and process surfaces — distinct parser surfaces may agree, but
    every common source/ownership fact must.
    """
    piece_evidence = tuple(
        (
            piece.piece_index,
            piece.carrier_location,
            piece.char_span.start,
            piece.char_span.end,
            piece.byte_length,
            piece.call_id,
            piece.call_location,
            piece.call_position,
            piece.result_position,
        )
        for piece in proof.pieces
    )
    segment_evidence = tuple(
        (
            segment.index,
            segment.member_positions,
            segment.char_length,
            segment.byte_length,
            segment.digest,
            segment.member_digest,
            tuple(None if span is None else (span.start, span.end) for span in segment.piece_spans),
        )
        for segment in proof.segments
    )
    marker_evidence = tuple(
        (
            marker.index,
            marker.role,
            marker.char_length,
            marker.byte_length,
            marker.digest,
            tuple(None if span is None else (span.start, span.end) for span in marker.piece_spans),
        )
        for marker in proof.markers
    )
    return (
        proof.request_index,
        proof.call_id,
        proof.call_location,
        proof.result_location,
        proof.call_position,
        proof.result_position,
        tuple(member.normalized for member in proof.requested_members),
        proof.proven_executed,
        proof.command_digest,
        proof.source_digest,
        proof.endpoint,
        proof.source_role,
        proof.root_path,
        proof.root_digest,
        proof.proof_version,
        piece_evidence,
        segment_evidence,
        marker_evidence,
    )


@dataclass
class _ProofPassResult:
    """The result of one bounded proof pass over collected 017 facts.

    ``refusal_outcome`` / ``refusal_reason`` are set exactly when the
    pass refuses the whole snapshot (a budget crossing, a
    diagnostics-full overflow, or a competing root-path read); on a
    refusal ``bundles`` is empty.  On a non-refused pass
    ``conflicts`` carries the retained closed-vocabulary conflicts
    and ``candidates_inspected`` the measured counter at the stopping
    point.  Candidate-level diagnostics are appended by the caller's
    ``note_diagnostic`` callback to the caller's own bounded list.
    """

    bundles: list[BundleProof]
    conflicts: tuple[BundleLimitation, ...]
    candidates_inspected: int
    refusal_outcome: BundleProofOutcome | None
    refusal_reason: BundleLimitation | None


def _proof_pass(
    requests: tuple[GraphRequest, ...],
    contexts: list[PathContext],
    reports: list[Any],
    namespace: BundleProofNamespace,
    effective: BundleProofBounds,
    root_digest: str,
    ledger: _BridgeSourceLedger,
    search: _SearchLedger,
    budget: _BudgetState,
    diagnostics: list[BundleLimitation],
    note_diagnostic: Callable[[BundleLimitation], bool],
    base_diagnostic_count: int,
) -> _ProofPassResult:
    """The private collector core shared by the accepted public
    wrapper and the 018-c admission composition.

    One bounded candidate pass over the ALREADY COLLECTED 017 facts
    (the validated reports, contexts and root binding) with the SAME
    cumulative ledger state: every selected candidate is counted
    before dedup or refusal, both ACTUAL path ceilings are enforced
    before any member charge or source/proof copy, the cumulative
    member preflight is charged before any fetch from
    already-parsed 017 metadata, every inspected body is accounted
    before any owned copy, and the same-occurrence consistency law
    compares the full proof signature before retention.  The
    diagnostics bound is enforced through the caller's
    ``note_diagnostic`` callback (``False`` refuses the pass with
    the bounded ``DIAGNOSTICS_FULL``) so the TOTAL emitted bound is
    the caller's single finite budget.  The accepted public
    wrapper's signature and every result are unchanged by this
    factoring.
    """
    candidates_inspected = 0
    max_diagnostics = effective.max_diagnostics

    def _refuse(outcome: BundleProofOutcome, reason: BundleLimitation) -> _ProofPassResult:
        return _ProofPassResult(
            bundles=[],
            conflicts=(),
            candidates_inspected=candidates_inspected,
            refusal_outcome=outcome,
            refusal_reason=reason,
        )

    def _over_bound(reason: BundleLimitation | None = None) -> _ProofPassResult:
        effective_reason = reason if reason is not None else ledger.refusal
        if effective_reason is None:
            raise _fixed("a budget refusal was recorded without a reason")
        return _refuse(BundleProofOutcome.OVER_BOUND, effective_reason)

    # --- Candidate enumeration (reads then processes, deterministic) ---
    positives: dict[tuple[int, str, str], list[BundleProof]] = {}
    for request_index, request in enumerate(requests):
        context = contexts[request_index]
        payload = request.payload
        report = reports[request_index]
        for read in report.reads:
            if not (read.wrapper.output_present and read.wrapper.output_span is not None):
                continue  # no proven output: not a source candidate
            candidates_inspected += 1
            if candidates_inspected > effective.max_bundles:
                return _refuse(BundleProofOutcome.OVER_BOUND, BundleLimitation.BUNDLES_OVER_BOUND)
            # Both ACTUAL path ceilings (graph + observation) bound
            # every normalized represented member BEFORE any member
            # charge or source/proof copy: a violation is a fixed
            # typed non-acquisition (candidate diagnostic), never an
            # over-bound acquisition.
            path_reason = _member_paths_within_bounds(read.requested_members, namespace)
            if path_reason is not None:
                if not note_diagnostic(path_reason):
                    return _refuse(BundleProofOutcome.OVER_BOUND, BundleLimitation.DIAGNOSTICS_FULL)
                continue
            # The cumulative member preflight is charged BEFORE any
            # output-carrier fetch: the represented member count is
            # already-parsed 017 metadata (the order's preflight law:
            # at-limit stays at-limit, the first over-bound proven
            # candidate is a fixed typed snapshot refusal, never a
            # post-fetch or post-allocation discard).
            budget.charge(len(read.requested_members))
            if budget.refusal is not None:
                return _over_bound(budget.refusal)
            # The full output body is charged BEFORE any owned copy.
            read_span = read.wrapper.output_span
            read_carrier = _carrier_string(payload, read.result_location)
            if (
                read_carrier is not None
                and read_span is not None
                and read_span.end <= len(read_carrier)
            ):
                read_bytes = _utf8_byte_length_range(read_carrier, read_span.start, read_span.end)
                if read_bytes is not None:
                    ledger.account(read_bytes)
            if ledger.refusal is not None:
                return _over_bound()
            proof, reason = _read_bundle(
                request_index,
                read,
                payload,
                context,
                namespace,
                effective,
                search,
                budget,
                root_digest,
            )
            if reason is not None and reason in _BUDGET_REASONS:
                return _over_bound(budget.refusal if budget.refusal is not None else reason)
            if budget.refusal is not None:
                return _over_bound(budget.refusal)
            if reason is not None:
                if not note_diagnostic(reason):
                    return _refuse(BundleProofOutcome.OVER_BOUND, BundleLimitation.DIAGNOSTICS_FULL)
            elif proof is not None:
                key = (request_index, read.call_id, read.result_location)
                positives.setdefault(key, []).append(proof)
        for proc in report.processes:
            if proc.outcome is not ProcessOutcome.COMPLETE:
                continue  # no complete paired process proof: no candidate
            candidates_inspected += 1
            if candidates_inspected > effective.max_bundles:
                return _refuse(BundleProofOutcome.OVER_BOUND, BundleLimitation.BUNDLES_OVER_BOUND)
            # Both ACTUAL path ceilings (graph + observation) bound
            # every normalized represented member BEFORE any member
            # charge or source/proof copy (same law as the read path).
            path_reason = _member_paths_within_bounds(proc.requested_members, namespace)
            if path_reason is not None:
                if not note_diagnostic(path_reason):
                    return _refuse(BundleProofOutcome.OVER_BOUND, BundleLimitation.DIAGNOSTICS_FULL)
                continue
            # The cumulative member preflight is charged BEFORE any
            # piece/body reconstruction from already-parsed 017
            # member metadata (the same preflight law as the read
            # path).
            budget.charge(len(proc.requested_members))
            if budget.refusal is not None:
                return _over_bound(budget.refusal)
            # Every native piece reconstruction is charged BEFORE any
            # owned copy (the cumulative exact byte length is the
            # 017-proven total over the ordered pieces).
            ledger.account(proc.total_byte_length)
            if ledger.refusal is not None:
                return _over_bound()
            proof, reason = _process_bundle(
                request_index,
                proc,
                payload,
                context,
                namespace,
                effective,
                search,
                budget,
                root_digest,
            )
            if reason is not None and reason in _BUDGET_REASONS:
                return _over_bound(budget.refusal if budget.refusal is not None else reason)
            if budget.refusal is not None:
                return _over_bound(budget.refusal)
            if reason is not None:
                if not note_diagnostic(reason):
                    return _refuse(BundleProofOutcome.OVER_BOUND, BundleLimitation.DIAGNOSTICS_FULL)
            elif proof is not None:
                key = (request_index, proc.exec_call_id, proc.initial_result_location)
                positives.setdefault(key, []).append(proof)

    # --- Same-occurrence consistency law (before retention) -----------
    bundles: list[BundleProof] = []
    seam_conflict = False
    for proofs in positives.values():
        if len(proofs) == 1:
            bundles.append(proofs[0])
            continue
        signatures = [_seam_signature(proof) for proof in proofs]
        if len(set(signatures)) == 1:
            # The same physical occurrence carrying the SAME proof
            # signature is ONE record (read primary).
            bundles.append(next((p for p in proofs if p.surface is BundleSurface.READ), proofs[0]))
        else:
            # A mismatched proof acquires NOTHING from that occurrence;
            # ready is refused.
            seam_conflict = True

    # --- Conflicting root-path read (the 018-a law, graph.py) ---------
    # A tool read at the root path with different content is a
    # competing effective root: no reset/supersession, typed conflict
    # (a tool read never establishes the root).  Only an independently
    # proven SINGLE-occurrence root-path member digest is compared
    # against the established root digest; a boundaryless or repeated
    # group never infers a root hash, and a same-bytes root-path read
    # is consistent.  The refusal retains no bundles.
    for proof in bundles:
        for segment in proof.segments:
            if segment.member_digest is None:
                continue  # no single-occurrence proof: never inferred
            member = proof.requested_members[segment.member_positions[0]]
            if member.normalized == ROOT_FILENAME and segment.member_digest != root_digest:
                return _refuse(BundleProofOutcome.ROOT_CONFLICT, BundleLimitation.COMPETING_ROOTS)

    # --- Per-path source conflict (proven single-occurrence digests) --
    path_digests: dict[str, str] = {}
    conflict_paths: set[str] = set()
    for proof in bundles:
        for segment in proof.segments:
            if segment.member_digest is None:
                continue
            member = proof.requested_members[segment.member_positions[0]]
            path = member.normalized
            if path is None:
                continue  # defensive (the resolved-member law)
            if path in path_digests and path_digests[path] != segment.member_digest:
                conflict_paths.add(path)
            else:
                path_digests.setdefault(path, segment.member_digest)
    source_conflict = bool(conflict_paths)
    if source_conflict:
        bundles = [
            proof
            for proof in bundles
            if not any(
                segment.member_digest is not None
                and proof.requested_members[segment.member_positions[0]].normalized
                in conflict_paths
                for segment in proof.segments
            )
        ]

    conflicts: tuple[BundleLimitation, ...] = ()
    if seam_conflict:
        conflicts = (BundleLimitation.SEAM_CONFLICT,)
    elif source_conflict:
        conflicts = (BundleLimitation.SOURCE_CONFLICT,)

    # --- Bounded final diagnostic at every public exit ----------------
    if len(conflicts) + len(diagnostics) + base_diagnostic_count > max_diagnostics:
        return _refuse(BundleProofOutcome.OVER_BOUND, BundleLimitation.DIAGNOSTICS_FULL)
    return _ProofPassResult(
        bundles=bundles,
        conflicts=conflicts,
        candidates_inspected=candidates_inspected,
        refusal_outcome=None,
        refusal_reason=None,
    )


def observe_bundle_proofs(
    requests: tuple[GraphRequest, ...],
    namespace: BundleProofNamespace,
    bounds: BundleProofBounds | None = None,
) -> BundleProofSnapshot:
    """One bounded batch of decoded requests to one bundle-proof
    snapshot (objective 018-b).

    The entry takes exactly one namespace (mixed-namespace batches are
    structurally impossible; the record's scoped keys bind it).
    ``bounds``, when supplied, must equal the namespace's effective
    proof bounds.  The 017 re-observation pass always runs under the
    ACTUAL effective ``ObservationBounds`` carried by the namespace,
    and the source budgets under the ACTUAL effective ``GraphBounds``.
    No caller flag, hash, fabricated member boundary or supplied
    snapshot creates source authority.
    """
    if bounds is None:
        effective = namespace.bounds
    elif bounds != namespace.bounds:
        raise _fixed("bounds must equal the namespace effective bounds")
    else:
        effective = bounds

    if (
        namespace.bundle_proof_version != BUNDLE_PROOF_CONTRACT_VERSION
        or namespace.observation_version != OBSERVER_VERSION
        or namespace.graph_version != GRAPH_CONTRACT_VERSION
    ):
        return _bundle_refusal(
            namespace,
            BundleProofOutcome.VERSION_CONFLICT,
            (BundleLimitation.VERSION_UNSUPPORTED,),
            len(requests),
            (),
        )

    request_count = len(requests)
    graph_bounds = namespace.graph_bounds
    if request_count > graph_bounds.max_requests:
        return _bundle_refusal(
            namespace,
            BundleProofOutcome.OVER_BOUND,
            (BundleLimitation.BATCH_OVER_BOUND,),
            request_count,
            (),
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
    authoritative: list[tuple[int, Any]] = []
    for request_index, report in enumerate(reports):
        for root_occ in report.roots.roots:
            authoritative.append((request_index, root_occ))
    if not authoritative:
        return _bundle_refusal(
            namespace,
            BundleProofOutcome.NO_ROOT,
            (BundleLimitation.NO_ROOT,),
            request_count,
            ordered_limitations,
        )
    identities = {(occ.scope_label, occ.digest) for _, occ in authoritative}
    if len(identities) > 1:
        return _bundle_refusal(
            namespace,
            BundleProofOutcome.ROOT_CONFLICT,
            (BundleLimitation.COMPETING_ROOTS,),
            request_count,
            ordered_limitations,
        )
    scope_label, root_digest = next(iter(identities))
    if scope_label is None or root_digest is None:
        return _bundle_refusal(
            namespace,
            BundleProofOutcome.NO_ROOT,
            (BundleLimitation.NO_ROOT,),
            request_count,
            ordered_limitations,
        )
    workspace = validate_workspace(scope_label, graph_bounds.max_path_bytes)
    if workspace is None or workspace != scope_label:
        return _bundle_refusal(
            namespace,
            BundleProofOutcome.WORKSPACE_UNPROVEN,
            (BundleLimitation.WORKSPACE_UNPROVEN,),
            request_count,
            ordered_limitations,
        )
    if workspace != namespace.workspace:
        return _bundle_refusal(
            namespace,
            BundleProofOutcome.ROOT_CONFLICT,
            (BundleLimitation.WORKSPACE_MISMATCH,),
            request_count,
            ordered_limitations,
        )
    for request in requests:
        request_context = request.context
        if (
            request_context is not None
            and request_context.workspace is not None
            and request_context.workspace != workspace
        ):
            return _bundle_refusal(
                namespace,
                BundleProofOutcome.ROOT_CONFLICT,
                (BundleLimitation.ROOT_CONTEXT_MISMATCH,),
                request_count,
                ordered_limitations,
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

    # --- Bridge-owned ledgers (before any copy/retention) --------------
    ledger = _BridgeSourceLedger(graph_bounds)
    search = _SearchLedger(effective.max_marker_search)
    budget = _BudgetState(effective)
    candidates_inspected = 0
    max_diagnostics = effective.max_diagnostics
    if len(ordered_limitations) > max_diagnostics:
        return _bundle_refusal(
            namespace,
            BundleProofOutcome.OVER_BOUND,
            (BundleLimitation.DIAGNOSTICS_FULL,),
            request_count,
            (),
            candidates_inspected,
            ledger.total_bytes,
            search.total_bytes,
        )

    def _over_bound(reason: BundleLimitation | None = None) -> BundleProofSnapshot:
        effective_reason = reason if reason is not None else ledger.refusal
        if effective_reason is None:
            raise _fixed("a budget refusal was recorded without a reason")
        return _bundle_refusal(
            namespace,
            BundleProofOutcome.OVER_BOUND,
            (effective_reason,),
            request_count,
            ordered_limitations,
            candidates_inspected,
            ledger.total_bytes,
            search.total_bytes,
        )

    diagnostics: list[BundleLimitation] = []

    # Every root occurrence (duplicates included) is an inspected
    # source body: measured and accounted BEFORE any bridge-owned copy;
    # only the first occurrence is copied (its digest is already bound
    # by the single (scope_label, digest) identity above).
    root_content: str | None = None
    for request_index, root_occ in authoritative:
        carrier = _carrier_string(requests[request_index].payload, root_occ.location)
        span = root_occ.content_span
        if carrier is None or span is None or span.end > len(carrier):
            continue
        n_bytes = _utf8_byte_length_range(carrier, span.start, span.end)
        if n_bytes is None:
            return _bundle_refusal(
                namespace,
                BundleProofOutcome.WORKSPACE_UNPROVEN,
                (BundleLimitation.WORKSPACE_UNPROVEN,),
                request_count,
                ordered_limitations,
                candidates_inspected,
                ledger.total_bytes,
                search.total_bytes,
            )
        ledger.account(n_bytes)
        if ledger.refusal is not None:
            return _over_bound()
        if root_content is None:
            root_content = carrier[span.start : span.end]
            if sha256_hex(root_content) != root_digest:
                # Defensive 017 integrity defect: the root is not
                # acquired (no echo of the content).
                return _bundle_refusal(
                    namespace,
                    BundleProofOutcome.NO_ROOT,
                    (BundleLimitation.WORKSPACE_UNPROVEN,),
                    request_count,
                    ordered_limitations,
                    candidates_inspected,
                    ledger.total_bytes,
                    search.total_bytes,
                )
    if root_content is None:
        return _bundle_refusal(
            namespace,
            BundleProofOutcome.NO_ROOT,
            (BundleLimitation.NO_ROOT,),
            request_count,
            ordered_limitations,
            candidates_inspected,
            ledger.total_bytes,
            search.total_bytes,
        )

    def _note_diagnostic(reason: BundleLimitation) -> bool:
        """Retain one candidate-level fixed diagnostic only while the
        TOTAL emitted diagnostics (candidate reasons + observation /
        global limitations) stay at the finite bound.  The bound is
        enforced BEFORE retention/append: overflow is the bounded
        ``DIAGNOSTICS_FULL`` refusal, never a truncated or unbounded
        reason list (no silent truncation, no governance loss)."""
        if len(diagnostics) + len(ordered_limitations) + 1 > max_diagnostics:
            return False
        diagnostics.append(reason)
        return True

    result = _proof_pass(
        requests,
        contexts,
        reports,
        namespace,
        effective,
        root_digest,
        ledger,
        search,
        budget,
        diagnostics,
        _note_diagnostic,
        len(ordered_limitations),
    )
    candidates_inspected = result.candidates_inspected
    if result.refusal_reason is not None:
        # A diagnostics-full overflow refuses with NO copied
        # limitations (one bounded fixed reason); every other
        # refusal retains the observed limitations.
        limitations: tuple[Limitation, ...] = (
            ()
            if result.refusal_reason is BundleLimitation.DIAGNOSTICS_FULL
            else ordered_limitations
        )
        refusal_outcome = result.refusal_outcome
        if refusal_outcome is None:
            raise _fixed("a proof pass refusal carries its outcome")
        return _bundle_refusal(
            namespace,
            refusal_outcome,
            (result.refusal_reason,),
            request_count,
            limitations,
            candidates_inspected,
            ledger.total_bytes,
            search.total_bytes,
        )
    conflicts = result.conflicts
    outcome = BundleProofOutcome.VERSION_CONFLICT if conflicts else BundleProofOutcome.COMPLETE
    return BundleProofSnapshot(
        namespace=namespace,
        outcome=outcome,
        root_path=ROOT_FILENAME,
        root_digest=root_digest,
        bundles=tuple(result.bundles),
        conflicts=conflicts,
        diagnostics=tuple(diagnostics),
        observation_limitations=ordered_limitations,
        request_count=request_count,
        candidates_inspected=candidates_inspected,
        marker_search_bytes=search.total_bytes,
        source_bytes_inspected=ledger.total_bytes,
    )


def observe_bundle_proof(
    payload: dict[str, Any],
    namespace: BundleProofNamespace,
    *,
    endpoint: str,
    context: PathContext | None = None,
    bounds: BundleProofBounds | None = None,
) -> BundleProofSnapshot:
    """One decoded request to one bundle-proof snapshot.

    The public single-request form: the batch law applies with
    ``request_count`` 1.  ``endpoint`` is the explicit validated
    endpoint context; ``context`` the evidenced client-workspace
    context (``None`` allowed; the derived-workspace law applies).
    """
    request = GraphRequest(payload=payload, endpoint=endpoint, context=context)
    return observe_bundle_proofs((request,), namespace, bounds=bounds)


def _process_bundle(
    request_index: int,
    proc: ProcessObservation,
    payload: dict[str, Any],
    context: PathContext,
    namespace: BundleProofNamespace,
    bounds: BundleProofBounds,
    search: _SearchLedger,
    budget: _BudgetState,
    root_digest: str,
) -> tuple[BundleProof | None, BundleLimitation | None]:
    """One selected COMPLETE native process candidate to a whole/
    partition proof.

    The exact original carriers are re-fetched from the payload (each
    piece maps only to its own carrier, never an imaginary
    concatenated string); ``COMPLETE`` is the complete paired
    wrapper/process proof (global exit zero, every piece present,
    untruncated) and is the all-success prerequisite for both forms.
    The cumulative member preflight is charged by the caller BEFORE
    any piece/body reconstruction (already-parsed 017 member
    metadata); an overflow returns the snapshot-level
    ``(None, MEMBERS_OVER_BOUND)`` refusal.
    """
    call_position = _call_position(proc.exec_call_location)
    if call_position is None:
        return None, BundleLimitation.OUTPUT_INCONSISTENT
    arguments = _call_arguments(payload, proc.exec_call_location)
    if arguments is None:
        return None, BundleLimitation.OUTPUT_INCONSISTENT
    unwrapped = _unwrap_for_reparse(arguments, context, namespace.observation_bounds)
    if unwrapped is None:
        return None, BundleLimitation.PLAN_UNSUPPORTED
    command, call_context = unwrapped
    parsed, plan, loop = _parse_forms(command, call_context, namespace.observation_bounds)
    form, requested, grammar, command_digest = _selected_form(parsed, plan, loop)
    if requested != proc.requested_members:
        return None, BundleLimitation.OUTPUT_INCONSISTENT
    if any(member.normalized is None for member in requested):
        return None, BundleLimitation.MEMBER_UNRESOLVED
    # The caller already charged the represented member occurrences
    # (already-parsed 017 metadata) BEFORE any piece/body
    # reconstruction: at-limit stays at-limit, the first over-bound
    # proven candidate is a fixed typed snapshot refusal, never a
    # post-fetch or post-allocation discard.
    if budget.refusal is not None:
        return None, BundleLimitation.MEMBERS_OVER_BOUND

    texts: list[str] = []
    pieces_info: list[_PieceInfo] = []
    bundle_pieces: list[BundlePiece] = []
    # The actual exec/poll call association of every original piece,
    # from the 017 observation structure (never invented from IDs or
    # detached join coordinates): the initial piece is the exec
    # call's result; each poll piece is its causally associated poll's
    # result.
    associations: list[tuple[str, str, int, int, str]] = [
        (
            proc.exec_call_id,
            proc.exec_call_location,
            proc.exec_call_position,
            proc.initial_result_position,
            proc.initial_result_location,
        ),
    ]
    for poll in proc.polls:
        associations.append(
            (
                poll.poll_call_id,
                poll.poll_call_location,
                poll.poll_position,
                poll.result_position,
                poll.result_location,
            )
        )
    if len(associations) != len(proc.pieces):
        return None, BundleLimitation.OUTPUT_INCONSISTENT
    join_offset = 0
    for piece, association in zip(proc.pieces, associations, strict=True):
        (
            piece_call_id,
            piece_call_location,
            piece_call_position,
            piece_result_position,
            piece_result_location,
        ) = association
        if piece.result_location != piece_result_location:
            return None, BundleLimitation.OUTPUT_INCONSISTENT
        carrier = _carrier_string(payload, piece.result_location)
        span = piece.char_span
        if carrier is None or span.end > len(carrier):
            return None, BundleLimitation.OUTPUT_INCONSISTENT
        text = carrier[span.start : span.end]
        if len(text) != piece.char_length:
            return None, BundleLimitation.OUTPUT_INCONSISTENT
        texts.append(text)
        pieces_info.append(
            _PieceInfo(
                piece.result_location, span.start, span.end, join_offset, join_offset + len(text)
            )
        )
        bundle_pieces.append(
            BundlePiece(
                piece_index=piece.piece_index,
                carrier_location=piece.result_location,
                char_span=span,
                char_length=piece.char_length,
                byte_length=piece.byte_length,
                call_id=piece_call_id,
                call_location=piece_call_location,
                call_position=piece_call_position,
                result_position=piece_result_position,
            )
        )
        join_offset += len(text)
    full_output = "".join(texts)
    pieces_tuple = tuple(pieces_info)

    if proc.proven_region_char_length is not None:
        # Whole (017-attributed region) proof over the proven pieces.
        if proc.bundle_digest is None or proc.region_piece_spans == ():
            return None, BundleLimitation.OUTPUT_INCONSISTENT
        parts: list[str] = []
        for text, info, region_span in zip(
            texts, pieces_info, proc.region_piece_spans, strict=True
        ):
            if region_span is not None:
                local_start = region_span.start - info.carrier_start
                local_end = region_span.end - info.carrier_start
                parts.append(text[local_start:local_end])
        region_text = "".join(parts)
        if sha256_hex(region_text) != proc.bundle_digest:
            return None, BundleLimitation.OUTPUT_INCONSISTENT
        markers: tuple[BundleMarkerFact, ...] = ()
        if form == "plan":
            boundary_markers = _process_plan_boundary_markers(
                plan, pieces_tuple, full_output, proc.region_piece_spans
            )
            if boundary_markers is None:
                return None, BundleLimitation.OUTPUT_INCONSISTENT
            markers = boundary_markers
        proof = _bundle_proof(
            surface=BundleSurface.PROCESS,
            kind=BundleProofKind.WHOLE,
            grammar=grammar,
            command_digest=command_digest,
            request_index=request_index,
            call_id=proc.exec_call_id,
            call_location=proc.exec_call_location,
            call_position=call_position,
            result_location=proc.initial_result_location,
            result_position=proc.initial_result_position,
            endpoint=proc.endpoint,
            root_digest=root_digest,
            requested=requested,
            pieces=tuple(bundle_pieces),
            segments=(
                BundleSegment(
                    index=0,
                    member_positions=tuple(range(len(requested))),
                    char_length=len(region_text),
                    byte_length=len(region_text.encode("utf-8")),
                    digest=sha256_hex(region_text),
                    member_digest=sha256_hex(region_text) if len(requested) == 1 else None,
                    piece_spans=proc.region_piece_spans,
                ),
            ),
            markers=markers,
            source_text=region_text,
        )
        return proof, None

    # COMPLETE without an attributable region: the partition surface.
    if form in ("single", "loop"):
        # A complete single/loop form earns its 017 region; a region-
        # None observation for such a form is a defensive mismatch,
        # and a loop command is never a finite ``&&`` plan.
        return None, BundleLimitation.OUTPUT_INCONSISTENT
    literals, predicate = _finite_marker_plan(plan, bounds)
    if literals is None:
        return None, predicate
    # The full searched window is the full proven output (the ordered
    # join of the exact pieces); its exact UTF-8 length is charged
    # once per marker scan to the shared cumulative ledger.
    window_bytes = len(full_output.encode("utf-8"))
    located: list[CharSpan] = []
    for literal in literals:
        if search.refused:
            return None, BundleLimitation.MARKER_SEARCH_OVER_BOUND
        search.charge(window_bytes)
        if search.refused:
            return None, BundleLimitation.MARKER_SEARCH_OVER_BOUND
        first, duplicate = _locate_one(full_output, literal + "\n")
        if first is None:
            return None, BundleLimitation.MARKER_MISSING
        if duplicate:
            return None, BundleLimitation.MARKER_DUPLICATE
        located.append(CharSpan(start=first, end=first + len(literal) + 1))
    order_reason = _marker_order_ok(tuple(located))
    if order_reason is not None:
        return None, order_reason
    segments, partition_markers, source_text, reason = _partition_segments_and_markers(
        plan, tuple(located), full_output, pieces_tuple, bounds
    )
    if segments is None or partition_markers is None or source_text is None:
        return None, reason
    proof = _bundle_proof(
        surface=BundleSurface.PROCESS,
        kind=BundleProofKind.PARTITIONED,
        grammar=READ_PLAN_GRAMMAR,
        command_digest=plan.command_digest,
        request_index=request_index,
        call_id=proc.exec_call_id,
        call_location=proc.exec_call_location,
        call_position=call_position,
        result_location=proc.initial_result_location,
        result_position=proc.initial_result_position,
        endpoint=proc.endpoint,
        root_digest=root_digest,
        requested=requested,
        pieces=tuple(bundle_pieces),
        segments=segments,
        markers=partition_markers,
        source_text=source_text,
    )
    return proof, None

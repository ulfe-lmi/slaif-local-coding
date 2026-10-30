"""Pure per-request process/chunk observation (objective 017, D09).

This module is the D09 process/chunk collector on the same inert
pure-observation surface: it associates an original exec occurrence with
its causally linked empty-stdin polls and final process completion over
the pinned native 0.164.0 exec-wrapper format
(``codex-native-exec-wrapper/v1``), and retains the exact observed source
pieces with their per-result coordinates.  It is inert: nothing here is
wired into the legacy request execution path, no observed command is
executed, no filesystem or network access occurs, and no identity is
inferred from untrusted text.

Native wrapper law (distinct from the legacy ``codex-exec-wrapper/v1``
grammar): the pinned function_tool_response text wrapper is the header
sections in the fixed order — optional ``Chunk ID: `` (six lowercase
hex), mandatory ``Wall time: `` (bounded four-decimal seconds), optional
``Process exited with code `` or ``Process running with session ID ``
(strict i32; mutually exclusive), optional ``Original token count: ``
(bounded unsigned) — over the exact ``Output:`` delimiter line, which is
LF-terminated even when the output is empty.  Dispatch is on bounded
header evidence only: everything after the delimiter is the exact output
section and is never re-parsed as header.  The version-bound native
truncation fact (the pinned two-line warning over the head/marker/tail
body, or a pinned omission marker) is read from the output section and
can only ever mark the frame truncated — never complete.  The legacy
single-result surface (including source-is-source) is untouched.  The
grammars INTERSECT on final headers without the pinned ``Original
token count:`` section: such frames keep their existing positive
legacy read semantics, and the process surface may add a consistent
second observation there.  Pinned frames WITH that section stay
honestly typed non-acquiring on the legacy grammar, and are acquired
on THIS process surface under the single-final law below (objective
017-am; process grammar ``process-chunk/v2``): an already-exited
native exec (a complete pinned native result which finishes
immediately, including an empty source) acquires the earned literal
read region with zero polls, no invented session and no dummy
terminal piece.
  A header whose first delimiter lies beyond the configured
  ``max_wrapper_header_lines`` window is the fixed
  ``WRAPPER_HEADER_OVER_BOUND`` resource refusal, decided before the
  output section is scanned at all, and distinct from the
  ``MALFORMED_WRAPPER`` grammar verdict over a fully visible header.

Chain law (closed grammar, one selected endpoint domain):

- an exec occurrence is an eligible exec-family call with an exact string
  ID and EXACTLY ONE result whose bounded native header proves a running
  session (session section present, exit section absent in the closed
  section grammar); it claims the session.  Bounded header identity is
  decided separately from body eligibility: a competing owner with an
  over-bound or otherwise ineligible body still claims its session and
  is never silently dropped (the good-looking chain then conflicts, and
  the sole over-bound owner carries the fixed OVER_BOUND refusal).
  Duplicated same-call results and pre-call results never claim a
  session themselves, but their clean running headers stay observable
  as NEGATIVE ambiguity for the claimed session (the session can no
  longer be established cleanly; the records never acquire and never
  prove execution).  Any frame typing without a clean running header
  claims nothing.
- an immediate-exec occurrence is an eligible exec-family call with an
  exact string ID whose bounded closed native header on a causally
  following result proves an ACTUAL exit (exit section present, running
  section absent): the already-exited single-final shape (process
  grammar ``process-chunk/v2``, objective 017-am).  The result is its
  own initial and terminal result: zero polls, exactly one piece, no
  invented session.  The complete-request count of such occurrences is
  decided from bounded header facts BEFORE any full-frame body work or
  retention and is bounded by ``max_process_immediate_execs`` (a fixed
  non-acquiring ``OVER_BOUND`` for every occurrence when exceeded; the
  count does NOT consume ``max_process_sessions`` because a final frame
  carries no session section, and the zero-poll result trivially
  satisfies the poll ceiling with exactly one piece against the
  cumulative char/byte bounds).  A duplicated result, a pre-call result
  or a colliding call ID is a fixed non-acquiring
  ``PROCESS_CHAIN_CONFLICT`` (the strict identity and numeric
  structural causality law applies to zero-poll results exactly as to
  chains).  A result carrying no classifiable closed native header
  (including an entirely empty result string) is not a known-native
  frame and emits no process observation (the legacy surface keeps its
  honest typing, including ``MISSING_OUTPUT_BODY``).  A single-final
  frame never claims session ownership, never repairs a conflicting or
  missing running chain, and never participates in the poll law;
  unknown unique opaque tool families stay isolated in all of these
  cases.
- session ownership: the session must be established by exactly ONE
  eligible exec occurrence in the request — across ALL eligible execs,
  even when the command is not an earned read.  A second running frame
  with the same session is a typed ``PROCESS_SESSION_CONFLICT``; both
  affected chains are invalidated.
  Any other unresolved known-native running claim — a duplicated or
  pre-call exec result, or a write_stdin result whose header session
  contradicts or cannot be attributed to the poll's closed argument
  session — is negative-only ambiguity: it invalidates the claimed
  session without proving execution, and the affected chain is a typed
  ``PROCESS_SESSION_CONFLICT``.
- a poll is a bare ``write_stdin`` call whose arguments are EXACTLY the
  closed empty-stdin shape ``{"session_id": <strict positive int>,
  "chars": ""}`` matching the chain session.  A matching-session poll
  with nonempty or invalid chars, a missing result, a duplicated result,
  a pre-call result, a foreign-session result frame, an after-final
  position, or a colliding call ID INVALIDATES the affected initial
  chain (typed; never filtered away as "not a chain poll", never
  first-match).  A poll whose closed argument session is proven
  different and whose own result names that same session — or a poll
  whose result carries no parseable native claim at all — is an
  unrelated unique opaque call: it neither joins nor poisons.  A
  write_stdin result whose clean running header names a session
  different from the poll's closed argument session (including
  malformed or absent argument identity) is an explicit foreign or
  unattributable claim: negative ambiguity for that session, never an
  execution proof (the malformed arguments are never accepted).  An
  UNASSIGNABLE argument session (malformed/absent/non-int identity,
  undecodable arguments) whose bounded own result records contain a
  KNOWN native frame — a well-formed running, final or unknown-status
  header (duplicated results never repair) — is not opaque: a poll
  ISSUED after the exec issue and before the chain's terminal result
  (no terminal result: the chain is still open) is potentially
  associated, and its native record prevents complete-source proof
  even when the result is delivered late (it can still hide a piece);
  the affected chain is negatively invalidated (typed
  ``PROCESS_CHAIN_CONFLICT``); the SID is never coerced, no execution
  or owner is inferred, and a poll issued before the exec issue or
  after the terminal result is not poisoned (numeric call/result
  chronology).  No
  generic poll option support is claimed (extra argument keys have no
  declared compatible grammar).
- a known-native result whose bounded header is unclassifiable because
  the configured header-line cap is exhausted — the first ``Output:``
  delimiter beyond the character window, or more lines than the cap
  within it — is a blocked anchor: the bounds prevent a complete owner
  inventory, so every claimant and every exec-origin anchor carries the
  fixed non-acquiring ``OVER_BOUND`` (never a selection from an
  incomplete inventory; a blocked exec keeps its honest record even with
  no valid claimant).  A poll-origin anchor invalidates the actual exec
  claimants but is never itself observed (a write_stdin call is not an
  original exec and no process origin is invented); with only
  poll-origin anchors the read surface keeps its honest bookkeeping.
  A fully visible malformed header claims nothing.  Unknown unique
  opaque tool families can never assert session ownership in any of
  these cases.
- the first frame carrying the exit section terminates the chain.
- completion is earned only when every associated frame parses, every
  piece is within its per-frame bound, the cumulative source stays within
  the declared character AND exact UTF-8 byte bounds (both checked before
  any piece retention or concatenation copy), and the final frame proves
  exit zero without truncation.  A truncated frame anywhere invalidates
  whole-source completion even on final exit zero.  Empty pieces are
  exact (the proven empty output retains the delimiter LF) and cannot
  inflate the nonempty-piece proof.
- the earned outer attribution is computed on the transient ordered
  concatenation with the existing outer-region law (single / plan / loop
  parsers) and mapped back onto the original pieces as absolute
  per-piece sub-spans; raw source never enters the report, no dummy span
  over a virtual joined string is minted, and the occurrence-hash law
  holds (one attributable occurrence may carry its exact member digest;
  boundaryless multiple occurrences stay unknown).  ``proven_executed``
  is nonempty only for a complete all-cat parse of the original command
  (the actual sleep-bearing stream command stays unearned).
- bounded before retention: the complete-inventory preflight mirrors the
  read surface (over-bound requests carry no process observation; the
  read surface reports the bound); the complete owner inventory is
  decided from bounded header facts BEFORE any full frame body work (the
  session count is a preflight over the header facts); the per-chain
  poll/piece ceilings are decided before the over-limit candidate frame
  is parsed or retained (an at-limit chain stays exactly at the bound);
  and the cumulative source char/byte bounds are decided before any
  process piece is allocated or retained (a fixed non-acquiring
  ``OVER_BOUND`` in every case).
"""

from __future__ import annotations

import json
import re
from collections.abc import Callable
from itertools import islice
from typing import Any, TypedDict

from ..bundles.compound_reads import ReadPlanParse, parse_read_plan, plan_source_region
from ..bundles.literal_loops import LoopParse, parse_literal_loop
from ..bundles.observation_models import (
    EMPTY_SOURCE_SHA256,
    CharSpan,
    Limitation,
    NativeWrapperFacts,
    NormalizedPath,
    ObservationBounds,
    PathContext,
    ProcessObservation,
    ProcessOutcome,
    ProcessPiece,
    ProcessPoll,
    ReadCommandParse,
    contains_lone_surrogates,
    sha256_hex,
)
from ..bundles.read_grammar import (
    parse_read_command,
    raw_argument_bound,
    unwrap_call_arguments,
)
from ..bundles.tool_results import (
    _call_entries,
    _call_records,
    _inventory_totals,
    _result_entries,
    _workdir_literal,
    final_cat_evidence,
)

_EXEC_LEAVES = ("exec_command", "shell_command")
_POLL_LEAF = "write_stdin"

_SECTION_CHUNK = "Chunk ID: "
_SECTION_WALL = "Wall time: "
_SECTION_EXIT = "Process exited with code "
_SECTION_RUNNING = "Process running with session ID "
_SECTION_TOKENS = "Original token count: "
_OUTPUT_DELIMITER = "\nOutput:\n"
_CHUNK_ID_RE = re.compile(r"^[0-9a-f]{6}$")
_WALL_NUM_RE = re.compile(r"^[0-9]{1,4}\.[0-9]{4}$")
_I32_TOKEN_RE = re.compile(r"^-?[0-9]{1,10}$")
_UINT_TOKEN_RE = re.compile(r"^[0-9]{1,10}$")
_WALL_TIME_MAX_SECONDS = 2048
_MAX_HEADER_TOKEN_COUNT = 10_000_000
_I32_MIN = -(2**31)
_I32_MAX = 2**31 - 1
#: A closed native header line is at most this many characters (the
#: longest closed section plus its newline: the running section over a
#: ten-digit i32); the bounded header prefix is
#: ``max_wrapper_header_lines * _MAX_CLOSED_HEADER_LINE_CHARS``.
_MAX_CLOSED_HEADER_LINE_CHARS = 44
# Pinned truncation formatter facts (version-bound native semantics; the
# warning and marker live INSIDE the output section, after the delimiter).
_TRUNCATION_WARNING_RE = re.compile(
    r"^Warning: truncated output \(original token count: [0-9]{1,10}\)\n"
    r"Total output lines: [0-9]{1,10}\n\n"
)
#: Bounded prefix window for the pinned truncation warning (the longest
#: pinned warning: the fixed labels plus two ten-digit counts = 93).
_TRUNCATION_WARNING_MAX_CHARS = 96
_BYTE_OMISSION_MARKER_RE = re.compile(r"\.\.\. [0-9]{1,10} bytes omitted \.\.\.")
_TOKEN_OMISSION_MARKER_RE = re.compile("\u2026[0-9]{1,10} tokens truncated\u2026")


def _parse_i32(token: str) -> int | None:
    """Strict i32 decimal token (bounded work; never int()-forced)."""

    if not _I32_TOKEN_RE.fullmatch(token):
        return None
    value = int(token)
    if not _I32_MIN <= value <= _I32_MAX:
        return None
    return value


def _utf8_byte_length_range(text: str, start: int, end: int) -> int | None:
    """Exact UTF-8 byte length of ``text[start:end]`` without a copy.

    One counting pass over the bounded original-string range (no slice,
    no encoding allocation); returns ``None`` when the range carries a
    lone surrogate (not valid UTF-8), mirroring the encode contract the
    typed ``MALFORMED_UNICODE`` refusal implements.
    """

    total = 0
    for char in islice(text, start, end):
        code = ord(char)
        if code < 0x80:
            total += 1
        elif code < 0x800:
            total += 2
        elif code < 0x10000:
            if 0xD800 <= code <= 0xDFFF:
                return None
            total += 3
        else:
            total += 4
    return total


def _parse_header_sections(
    sections: list[str],
) -> tuple[bool, int | None, int | None, int | None] | None:
    """Closed native section grammar over the exact header lines.

    Returns ``(chunk_present, exit_code, session_id, token_count)`` for a
    well-formed closed header (the fixed section order, at most five
    sections, each matched by its bounded grammar; exit and running are
    mutually exclusive); ``None`` on any grammar violation.
    """

    if not 1 <= len(sections) <= 5 or any(section == "" for section in sections):
        return None
    chunk_present = False
    exit_code: int | None = None
    session_id: int | None = None
    token_count: int | None = None
    i = 0
    if sections[i].startswith(_SECTION_CHUNK):
        if not _CHUNK_ID_RE.fullmatch(sections[i][len(_SECTION_CHUNK) :]):
            return None
        chunk_present = True
        i += 1
    if i >= len(sections) or not sections[i].startswith(_SECTION_WALL):
        return None
    wall = sections[i][len(_SECTION_WALL) :]
    if not wall.endswith(" seconds"):
        return None
    number = wall[: -len(" seconds")]
    if not _WALL_NUM_RE.fullmatch(number) or float(number) > _WALL_TIME_MAX_SECONDS:
        return None
    i += 1
    if i < len(sections) and sections[i].startswith(_SECTION_EXIT):
        exit_code = _parse_i32(sections[i][len(_SECTION_EXIT) :])
        if exit_code is None:
            return None
        i += 1
    if i < len(sections) and sections[i].startswith(_SECTION_RUNNING):
        if exit_code is not None:
            # The pinned sections are mutually exclusive: one frame is
            # either exited or running, never both.
            return None
        session_id = _parse_i32(sections[i][len(_SECTION_RUNNING) :])
        if session_id is None or session_id <= 0:
            return None
        i += 1
    if i < len(sections) and sections[i].startswith(_SECTION_TOKENS):
        token = sections[i][len(_SECTION_TOKENS) :]
        if not _UINT_TOKEN_RE.fullmatch(token) or int(token) > _MAX_HEADER_TOKEN_COUNT:
            return None
        token_count = int(token)
        i += 1
    if i != len(sections):
        return None
    return chunk_present, exit_code, session_id, token_count


def parse_native_wrapper(output: str, bounds: ObservationBounds) -> NativeWrapperFacts:
    """Parse the pinned native exec wrapper from one result body.

    The complete wrapper is the header plus the exact ``Output:``
    delimiter line plus the output section (the delimiter line is
    LF-terminated even when the output is empty).  Every grammar or
    encoding violation is a fixed typed refusal; header dispatch is
    bounded (the closed section grammar — at most five sections, each
    matched by a bounded grammar — capped by the configured
    ``max_wrapper_header_lines``), and the output section is never
    re-parsed as header.  Header refusals (cap or grammar) are decided
    before the output section is scanned at all, over the bounded
    header prefix only (the source body is never searched for Output
    metadata); once the header is classified, source ranges are counted,
    never copied or encoded, before any byte fact is retained.  A header
    the configured cap cannot classify — no delimiter in the bounded
    window while the string extends beyond it, or more lines than the
    cap within it — is a fixed ``WRAPPER_HEADER_OVER_BOUND`` resource
    refusal (the complete header was never inspected), distinct from the
    ``MALFORMED_WRAPPER`` grammar verdict over a fully visible header.
    """

    def _refused(reason: Limitation) -> NativeWrapperFacts:
        return NativeWrapperFacts(output_present=False, reasons=(reason,))

    if len(output) > bounds.max_output_chars:
        return _refused(Limitation.OUTPUT_OVER_BOUND)
    if output == "":
        return _refused(Limitation.MISSING_OUTPUT_BODY)
    # Bounded header discovery: the delimiter is located inside the
    # bounded header window BEFORE any slice or split (a closed header
    # line is at most ``_MAX_CLOSED_HEADER_LINE_CHARS``, so the window
    # of ``max_wrapper_header_lines`` closed lines plus the delimiter
    # reaches every classifiable header).  A first delimiter beyond the
    # cap means the configured resource ceiling, not the closed grammar,
    # was exceeded: a fixed ``WRAPPER_HEADER_OVER_BOUND`` refusal,
    # distinct from a grammar verdict over a fully visible header.
    cap = bounds.max_wrapper_header_lines * _MAX_CLOSED_HEADER_LINE_CHARS
    window = output[: cap + len(_OUTPUT_DELIMITER)]
    index = window.find(_OUTPUT_DELIMITER)
    if index < 0:
        # No delimiter in the bounded header window: a header that
        # extends beyond the window is a genuinely incomplete inventory
        # — a typed resource refusal, decided WITHOUT searching the
        # source body for Output metadata.  A string fully inside the
        # window was completely inspected: a grammar verdict.
        if len(output) > cap + len(_OUTPUT_DELIMITER):
            return _refused(Limitation.WRAPPER_HEADER_OVER_BOUND)
        return _refused(Limitation.MALFORMED_WRAPPER)
    body_start = index + len(_OUTPUT_DELIMITER)
    sections = window[:index].split("\n")
    if len(sections) > bounds.max_wrapper_header_lines:
        return _refused(Limitation.WRAPPER_HEADER_OVER_BOUND)
    parsed = _parse_header_sections(sections)
    if parsed is None:
        return _refused(Limitation.MALFORMED_WRAPPER)
    chunk_present, exit_code, session_id, token_count = parsed

    # The header is classified: only now is the output section scanned.
    # The exact UTF-8 validity and byte length of the body are decided
    # (counted, never copied or encoded) before any source range is
    # retained; a closed well-formed header is pure ASCII by grammar, so
    # the body range decides frame validity.  A lone surrogate is the
    # typed MALFORMED_UNICODE refusal, mirroring the encode contract.
    body_bytes = _utf8_byte_length_range(output, body_start, len(output))
    if body_bytes is None:
        return _refused(Limitation.MALFORMED_UNICODE)

    # The pinned two-line warning is anchored to the START of the output
    # section: ``^`` only anchors the carrier start, so the prefix is
    # matched over the bounded warning window (a recorded native warning
    # can never be missed, and body content later in the section is not
    # a header).  The omission markers keep their whole-body search.
    warning_window = output[body_start : body_start + _TRUNCATION_WARNING_MAX_CHARS]
    truncated = (
        _TRUNCATION_WARNING_RE.match(warning_window) is not None
        or _BYTE_OMISSION_MARKER_RE.search(output, body_start) is not None
        or _TOKEN_OMISSION_MARKER_RE.search(output, body_start) is not None
    )
    return NativeWrapperFacts(
        chunk_id_present=chunk_present,
        wall_time_present=True,
        exit_code=exit_code,
        session_id=session_id,
        original_token_count=token_count,
        output_present=True,
        output_span=CharSpan(start=body_start, end=len(output)),
        output_char_length=len(output) - body_start,
        output_byte_length=body_bytes,
        truncated=truncated,
    )


def _native_header_facts(output: str, bounds: ObservationBounds) -> NativeWrapperFacts | None:
    """Bounded native header identity, separate from body eligibility.

    The closed section grammar is decided over the bounded header prefix
    only: at most ``max_wrapper_header_lines`` closed lines, each within
    its bounded grammar, over the exact ``Output:`` delimiter line.  A
    running section proves the session identity even when the body is
    over-bound or otherwise ineligible — a competing owner is never
    silently dropped because of its body.  Returns the header facts (the
    output span and character length are measured; the byte fact and
    truncation stay owned by the full-frame body-eligibility decision)
    for a well-formed native header, or ``None`` when the header is not
    the closed native grammar (missing delimiter, malformed sections, or
    a prefix no closed form can reach).  This helper copies at most the
    bounded header window and never encodes or retains the body.
    """

    limit = bounds.max_wrapper_header_lines * _MAX_CLOSED_HEADER_LINE_CHARS
    window = output[: limit + len(_OUTPUT_DELIMITER)]
    index = window.find(_OUTPUT_DELIMITER)
    if index < 0:
        return None
    sections = window[:index].split("\n")
    if len(sections) > bounds.max_wrapper_header_lines:
        return None
    parsed = _parse_header_sections(sections)
    if parsed is None:
        return None
    chunk_present, exit_code, session_id, token_count = parsed
    body_start = index + len(_OUTPUT_DELIMITER)
    return NativeWrapperFacts(
        chunk_id_present=chunk_present,
        wall_time_present=True,
        exit_code=exit_code,
        session_id=session_id,
        original_token_count=token_count,
        output_present=True,
        output_span=CharSpan(start=body_start, end=len(output)),
        output_char_length=len(output) - body_start,
    )


def _header_beyond_cap(output: str, bounds: ObservationBounds) -> bool:
    """Whether the header cannot be classified within the configured cap.

    The decision is made over the bounded header prefix ONLY
    (``max_wrapper_header_lines * _MAX_CLOSED_HEADER_LINE_CHARS`` plus
    the delimiter), never by searching the source body for Output
    metadata.  Two resource exhaustions, both distinguished from a
    malformed-grammar verdict over a fully classifiable header window:

    - the header already carries more lines than the cap allows within
      the window (a bounded line count over the visible prefix, no
      copy); or
    - no delimiter lies inside the window and the string extends beyond
      it: a genuinely incomplete inventory (a closed running-section
      line may hide beyond the cap) — a fixed resource condition.

    A string fully inside the window was completely inspected: a
    malformed header there claims nothing.
    """

    cap = bounds.max_wrapper_header_lines * _MAX_CLOSED_HEADER_LINE_CHARS
    window = output[: cap + len(_OUTPUT_DELIMITER)]
    first = window.find(_OUTPUT_DELIMITER)
    if first < 0:
        return len(output) > cap + len(_OUTPUT_DELIMITER)
    return output.count("\n", 0, first) + 1 > bounds.max_wrapper_header_lines


class _PollShape:
    """Closed classification of one write_stdin call against one chain."""

    CLOSED = "closed"
    NONEMPTY = "nonempty"
    INVALID = "invalid"
    UNRELATED = "unrelated"


def _decode_poll_arguments(
    arguments: object, bounds: ObservationBounds
) -> dict[str, object] | None:
    """Bounded decode of one write_stdin argument (no key copy retained)."""

    decoded: object = arguments
    if isinstance(decoded, str):
        if len(decoded) > raw_argument_bound(bounds.max_command_chars):
            return None
        try:
            decoded = json.loads(decoded)
        except (json.JSONDecodeError, RecursionError, ValueError):
            return None
    if not isinstance(decoded, dict):
        return None
    return decoded


def _poll_argument_session(decoded: dict[str, object] | None) -> int | None:
    """The poll's closed argument session identity, or ``None``.

    A strict positive int (never bool) session identity is the only
    provable one; malformed, absent, non-int or undecodable arguments
    prove no session at all (never inferred, never coerced).
    """

    if decoded is None:
        return None
    raw_session = decoded.get("session_id")
    if type(raw_session) is not int or not 0 < raw_session <= _I32_MAX:
        return None
    return raw_session


def _classify_poll_arguments(arguments: object, session: int, bounds: ObservationBounds) -> str:
    """Classify one write_stdin call against the chain session (closed).

    Only the exact closed empty-stdin shape ``{"session_id": <strict
    positive int == session>, "chars": ""}`` is a chain poll.  A
    matching session with nonempty/absent/mistyped chars or extra keys
    is a matching-session invalidation (never silently dropped).  A
    session that is proven different, or cannot be proven at all
    (malformed/absent/non-int identity, undecodable arguments), is an
    unrelated unique opaque call — it neither joins nor poisons.
    """

    decoded = _decode_poll_arguments(arguments, bounds)
    arg_session = _poll_argument_session(decoded)
    if arg_session is None or arg_session != session:
        return _PollShape.UNRELATED
    if decoded is None:
        return _PollShape.UNRELATED  # unreachable: a proven session implies a dict
    # Matching session: the closed empty-stdin law, checked with O(1)
    # dict probes only — no key set or copy of the argument object is
    # ever built (an adversarial extra-key document must not allocate).
    if len(decoded) != 2 or "chars" not in decoded:
        # Extra keys have no declared compatible poll grammar (no
        # generic poll option support); a missing closed key is not the
        # closed poll.  Matching-session invalidation either way.
        return _PollShape.INVALID
    chars = decoded["chars"]
    if type(chars) is not str:
        return _PollShape.INVALID
    if chars != "":
        return _PollShape.NONEMPTY
    return _PollShape.CLOSED


class _BaseObservationFields(TypedDict):
    """Exact ProcessObservation fields shared by one collected chain."""

    endpoint: str
    exec_call_id: str
    exec_call_location: str
    exec_call_position: int
    initial_result_location: str
    initial_result_position: int
    initial_wrapper: NativeWrapperFacts
    requested_members: tuple[NormalizedPath, ...]
    polls: tuple[ProcessPoll, ...]
    final_result_location: str | None
    final_result_position: int | None
    final_wrapper: NativeWrapperFacts | None
    pieces: tuple[ProcessPiece, ...]
    piece_count: int
    nonempty_piece_count: int
    total_char_length: int
    total_byte_length: int


#: One exec-occurrence claimant: exact ID/position/location/name/arguments
#: plus its single causally following result, the bounded header facts
#: (running-session identity; the sole owner upgrades element 8 to the
#: full parsed frame for the body-eligibility decision) and the
#: header-proven running session.
Claimant = tuple[str, int, str, str, object, int, str, str, NativeWrapperFacts, int]

#: One blocked owner anchor: a known-native result record whose bounded
#: header is unclassifiable because the first delimiter lies beyond the
#: configured header cap (a hidden-claim risk that makes the complete
#: owner inventory impossible).  Same field layout as a Claimant minus
#: the claimed session; element 8 is the refused frame.
BlockedAnchor = tuple[str, int, str, str, object, int, str, str, NativeWrapperFacts]

#: One bound chain poll: exact ID/position/location plus its own result.
ChainPoll = tuple[str, int, str, int, str, str, NativeWrapperFacts]

#: One already-exited single-final occurrence (objective 017-am): the
#: same field layout as a Claimant minus the claimed session; element 8
#: is the bounded header facts (upgraded to the full parsed frame by the
#: body-eligibility decision, which is the sole full frame parse on the
#: occurrence).
ImmediateCandidate = tuple[str, int, str, str, object, int, str, str, NativeWrapperFacts]


def _all_cat_region(
    arguments: object,
    context: PathContext,
    bounds: ObservationBounds,
) -> tuple[
    str | None, tuple[NormalizedPath, ...], ReadCommandParse | ReadPlanParse | LoopParse | None
]:
    """The original command's finite parsed data and earned region law.

    Returns ``(region_kind, requested_members, region_source)`` where
    ``region_kind`` is ``"single"``, ``"plan"`` or ``"loop"`` only for a
    COMPLETE all-cat parse (an earned region exists); otherwise
    ``None``.  ``requested_members`` preserves the exact original
    command's finite parsed data in every outcome (never executed, never
    expanded).  The actual sleep-bearing stream command parses to no
    region and stays unearned.
    """

    unwrapped = unwrap_call_arguments(arguments, bounds.max_command_chars)
    if unwrapped is None or (
        unwrapped.workdir is not None and not _workdir_literal(unwrapped.workdir)
    ):
        return None, (), None
    if unwrapped.workdir is not None and contains_lone_surrogates(unwrapped.workdir):
        return None, (), None
    call_context = context
    if unwrapped.workdir is not None:
        call_context = PathContext(workspace=context.workspace, workdir=unwrapped.workdir)
    parsed = parse_read_command(
        unwrapped.command,
        call_context,
        bounds.max_command_chars,
        bounds.max_operands,
        bounds.max_path_bytes,
    )
    if parsed.complete:
        return "single", parsed.operands, parsed
    plan = parse_read_plan(
        unwrapped.command,
        call_context,
        bounds.max_command_chars,
        bounds.max_operands,
        bounds.max_path_bytes,
    )
    if plan.complete:
        return "plan", plan.requested_members, plan
    loop = parse_literal_loop(
        unwrapped.command,
        call_context,
        bounds.max_command_chars,
        bounds.max_operands,
        bounds.max_path_bytes,
    )
    if loop.is_loop_attempt:
        if loop.complete and loop.reasons == ():
            return "loop", loop.requested_members, loop
        return None, loop.requested_members, None
    return None, plan.requested_members, None


def _evidence_parse(
    arguments: object,
    context: PathContext,
    bounds: ObservationBounds,
) -> ReadCommandParse | ReadPlanParse | LoopParse | None:
    """The most specific recognized command parse for final-cat evidence.

    Mirrors the read surface's grammar-identity selection (a complete
    single cat, else the loop domain when attempted, else the plan) so
    the D09 process surface decides its final-``cat`` execution
    evidence from the same typed form (objective 017-am).  Bounded; no
    payload retention.
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
    parsed = parse_read_command(
        unwrapped.command,
        call_context,
        bounds.max_command_chars,
        bounds.max_operands,
        bounds.max_path_bytes,
    )
    if parsed.complete:
        return parsed
    loop = parse_literal_loop(
        unwrapped.command,
        call_context,
        bounds.max_command_chars,
        bounds.max_operands,
        bounds.max_path_bytes,
    )
    if loop.is_loop_attempt:
        return loop
    return parse_read_plan(
        unwrapped.command,
        call_context,
        bounds.max_command_chars,
        bounds.max_operands,
        bounds.max_path_bytes,
    )


def _map_region_to_pieces(
    region: CharSpan,
    piece_texts: tuple[str, ...],
    piece_spans: tuple[CharSpan, ...],
) -> tuple[tuple[CharSpan | None, ...], int, str]:
    """Map the earned region (transient joined-view coordinates) back onto
    the original pieces as ABSOLUTE per-piece sub-spans.

    Returns ``(per_piece_spans, region_char_length, region_digest)``.
    Each published span is absolute in the exact decoded JSON string that
    carried that piece's result text (the output-local clip plus the
    owning piece's ``char_span.start``); no span over a detached output
    substring or a virtual joined string is minted.  A zero-width region
    touching a piece keeps that piece's real zero-width carrier span
    (a proven empty source over the exact output start), never ``None``.
    """

    per_piece: list[CharSpan | None] = []
    region_parts: list[str] = []
    offset = 0
    for text, span in zip(piece_texts, piece_spans, strict=True):
        piece_start, piece_end = offset, offset + len(text)
        local_start = max(region.start, piece_start)
        local_end = min(region.end, piece_end)
        if local_end >= local_start:
            # A zero-width touch keeps the real zero-width carrier span
            # (a proven empty source over the exact output start).
            per_piece.append(
                CharSpan(
                    start=span.start + (local_start - piece_start),
                    end=span.start + (local_end - piece_start),
                )
            )
            region_parts.append(text[local_start - piece_start : local_end - piece_start])
        else:
            per_piece.append(None)
        offset = piece_end
    return (
        tuple(per_piece),
        region.end - region.start,
        sha256_hex("".join(region_parts)),
    )


def observe_processes(
    payload: dict[str, Any],
    context: PathContext,
    bounds: ObservationBounds,
    selected_endpoint: str | None = None,
    suppress_acquisition: bool = False,
) -> tuple[ProcessObservation, ...]:
    """Collect D09 process/chunk observations over one decoded payload.

    Only one selected endpoint domain is inspected (an explicit validated
    endpoint or the unambiguously inferred envelope); a mixed shape
    (``suppress_acquisition``) and an unknown selection carry no process
    observation — the read surface keeps its bookkeeping.  Over-bound
    requests (item / command / output inventory bounds) carry no process
    observation: the read surface reports the fixed ``OVER_BOUND`` bound
    fact and the process surface never builds a partial inventory.
    Process-specific bounds (sessions / polls / pieces / cumulative
    source chars and exact UTF-8 bytes, plus the per-request
    immediate-exec count for already-exited single-final results) are
    decided before any process piece is allocated or retained.  The
    blocked-anchor and session-cap early returns INCLUDE the
    already-exited single-final occurrences: a blocked inventory makes
    every candidate a fixed non-acquiring OVER_BOUND (no body parse),
    and the session cap (running-chain ownership only) leaves them
    decided by their own independent count law.
    """

    if selected_endpoint not in ("responses", "chat") or suppress_acquisition:
        return ()

    if selected_endpoint == "responses":
        raw_items = payload.get("input")
        resp_items = raw_items if isinstance(raw_items, list) else None
        chat_msgs: list[Any] | None = None
    else:
        resp_items = None
        raw_msgs = payload.get("messages")
        chat_msgs = raw_msgs if isinstance(raw_msgs, list) else None

    if (resp_items is not None and len(resp_items) > bounds.max_items) or (
        chat_msgs is not None and len(chat_msgs) > bounds.max_items
    ):
        return ()
    if chat_msgs is not None:
        for message in chat_msgs:
            if isinstance(message, dict) and message.get("role") == "assistant":
                tool_calls = message.get("tool_calls")
                if isinstance(tool_calls, list) and len(tool_calls) > bounds.max_items:
                    return ()
    command_total, output_total = _inventory_totals(
        resp_items, chat_msgs, bounds.max_commands, bounds.max_outputs
    )
    if command_total > bounds.max_commands or output_total > bounds.max_outputs:
        return ()

    responses_records, chat_records = _call_records(resp_items, chat_msgs)
    responses_outputs, _responses_defects, chat_outputs, _chat_defects = _result_entries(
        resp_items, chat_msgs
    )
    responses_calls, chat_calls = _call_entries(payload, bounds, responses_records, chat_records)

    if selected_endpoint == "responses":
        records, outputs, calls = responses_records, responses_outputs, responses_calls
    else:
        records, outputs, calls = chat_records, chat_outputs, chat_calls

    # Identity-collision map over the COMPLETE schema-evidenced inventory:
    # a chain ID colliding with any other schema record (any family) is a
    # typed conflict — relevant unknown-call collisions cannot disappear.
    records_by_id: dict[str, list[tuple[int, str]]] = {}
    for _family, position, location, raw_id, _name, _arguments in records:
        if isinstance(raw_id, str) and raw_id:
            records_by_id.setdefault(raw_id, []).append((position, location))

    def _id_collided(call_id: str) -> bool:
        return len(records_by_id.get(call_id, ())) > 1

    # 1. Known-native owner inventory (the exec and write_stdin leaves
    #    only; unknown unique opaque families can never assert session
    #    ownership, join, or poison).  Bounded header identity is
    #    decided before any full frame body work (the session count is
    #    a preflight over the header facts, not over retained full
    #    frames), and a competing owner with an over-bound or otherwise
    #    ineligible body still claims its session and is never silently
    #    dropped:
    #
    # - a clean running header on the single causally following result
    #   of an eligible exec-family call is the one legitimate claim;
    # - a clean running header on any OTHER known-native result record
    #   (a duplicated or pre-call exec result, or a write_stdin result
    #   whose closed argument session is not the header session) is an
    #   explicit unresolved claim: NEGATIVE ambiguity only — the record
    #   never acquires, never proves execution, and its session can no
    #   longer be established cleanly;
    # - a known-native result whose bounded header is unclassifiable and
    #   whose first delimiter lies beyond the configured header cap is
    #   a blocked anchor: the bounds prevent a complete owner inventory,
    #   so no good-looking owner may be selected (fixed OVER_BOUND).
    claimants: list[Claimant] = []
    ambiguous_sessions: set[int] = set()
    blocked_anchors: list[BlockedAnchor] = []
    # Already-exited single-final occurrences (objective 017-am): clean
    # candidates (bounded header facts only, no full frame parse yet)
    # and the strict identity/causality conflicts (duplicated or
    # pre-call final results, one per call).
    immediate_candidates: list[ImmediateCandidate] = []
    immediate_conflicts: list[ImmediateCandidate] = []
    immediate_conflict_ids: set[str] = set()
    for call_id, position, location, name, arguments in calls:
        leaf = name.rsplit("/", 1)[-1]
        if leaf not in _EXEC_LEAVES and leaf != _POLL_LEAF:
            continue
        results = outputs.get(call_id, ())
        if not results:
            continue
        for result_position, result_location, text in results:
            header = _native_header_facts(text, bounds)
            if header is None:
                if _header_beyond_cap(text, bounds):
                    blocked_anchors.append(
                        (
                            call_id,
                            position,
                            location,
                            name,
                            arguments,
                            result_position,
                            result_location,
                            text,
                            parse_native_wrapper(text, bounds),
                        )
                    )
                continue
            if header.exit_code is not None:
                # An already-exited closed native frame (single-final,
                # objective 017-am): the result is its own initial and
                # terminal result.  The closed grammar makes exit and
                # running mutually exclusive, so it carries no session
                # and claims no chain; only an exec-family call with
                # exactly its own causally following result is an
                # immediate-exec candidate.  A write_stdin result
                # carrying such a frame is decided by the chain poll
                # law (a chain terminal or an unidentifiable poll),
                # never here.
                if leaf in _EXEC_LEAVES:
                    if len(results) == 1 and result_position > position:
                        immediate_candidates.append(
                            (
                                call_id,
                                position,
                                location,
                                name,
                                arguments,
                                result_position,
                                result_location,
                                text,
                                header,
                            )
                        )
                    elif call_id not in immediate_conflict_ids:
                        # Duplicated or pre-call final result on an
                        # exec-family call: the strict identity and
                        # numeric structural causality law applies to
                        # zero-poll results exactly as to chains — a
                        # fixed non-acquiring conflict (one
                        # observation per call, below).
                        immediate_conflict_ids.add(call_id)
                        immediate_conflicts.append(
                            (
                                call_id,
                                position,
                                location,
                                name,
                                arguments,
                                result_position,
                                result_location,
                                text,
                                header,
                            )
                        )
                continue
            if header.session_id is None:
                # A fully visible closed header with neither running
                # nor exit section: an unknown-status frame.  It claims
                # no session and is not a single-final (no exit): no
                # process observation here (a poll's own frame stays a
                # chain poll law decision).
                continue
            session = header.session_id
            if leaf in _EXEC_LEAVES:
                if len(results) == 1 and result_position > position:
                    # The one legitimate claim: the bounded header facts
                    # carry the identity; the sole owner upgrades to the
                    # full frame for the body-eligibility decision.
                    claimants.append(
                        (
                            call_id,
                            position,
                            location,
                            name,
                            arguments,
                            result_position,
                            result_location,
                            text,
                            header,
                            session,
                        )
                    )
                else:
                    # Duplicated or pre-call result on an exec-family
                    # call: the explicit running claim stays observable
                    # as negative ambiguity; the record never acquires.
                    ambiguous_sessions.add(session)
            else:
                # A write_stdin result whose header session differs from
                # the poll's closed argument session (including
                # malformed or absent argument identity) is an explicit
                # foreign or unattributable running claim: negative
                # ambiguity only.  A header matching the closed argument
                # session is the poll's own frame, decided by the chain
                # poll law.
                if _poll_argument_session(_decode_poll_arguments(arguments, bounds)) != session:
                    ambiguous_sessions.add(session)

    def _immediate_observations(blocked: bool, endpoint: str) -> list[ProcessObservation]:
        """Assemble the already-exited single-final observations.

        ``blocked``: a blocked anchor prevents a complete owner
        inventory — every candidate is a fixed non-acquiring
        OVER_BOUND with NO full-frame body parse (no selection from an
        incomplete inventory, mirroring the anchor/claimant refusal).
        Otherwise the candidates are decided by their own
        complete-request count law, independent of session ownership
        (the immediate count never consumes a session): over the bound
        every candidate is a fixed non-acquiring OVER_BOUND decided
        before any full-frame body work; a collided ID is a typed
        conflict; only a clean candidate parses its frame once.
        Duplicated or pre-call final results always trail as one fixed
        non-acquiring conflict per call (never selected, never
        acquired).  A poll-origin anchor never enters these lists: a
        write_stdin result is decided by the chain poll law and no
        poll is ever turned into an exec origin.
        """

        assembled: list[ProcessObservation] = []
        if blocked:
            for candidate in sorted(immediate_candidates, key=_claimant_key):
                assembled.append(_over_bound_observation(endpoint, candidate, context, bounds))
        else:
            immediate_over_bound = len(immediate_candidates) > bounds.max_process_immediate_execs
            for candidate in sorted(immediate_candidates, key=_claimant_key):
                if immediate_over_bound:
                    assembled.append(_over_bound_observation(endpoint, candidate, context, bounds))
                    continue
                if _id_collided(candidate[0]):
                    assembled.append(
                        _conflict_observation(
                            endpoint,
                            candidate,
                            (Limitation.PROCESS_CHAIN_CONFLICT,),
                            context,
                            bounds,
                        )
                    )
                    continue
                assembled.append(_collect_single_final(endpoint, candidate, context, bounds))
        for conflict in sorted(immediate_conflicts, key=_claimant_key):
            assembled.append(
                _conflict_observation(
                    endpoint,
                    conflict,
                    (Limitation.PROCESS_CHAIN_CONFLICT,),
                    context,
                    bounds,
                )
            )
        return assembled

    # 1b. Blocked anchors: the bounds prevent a complete owner inventory
    #     — fixed non-acquiring OVER_BOUND for every claimant AND
    #     exec-origin anchor, never a selection from an incomplete
    #     inventory (checked before any session grouping or body work).
    #     A blocked exec-origin anchor keeps its honest record even with
    #     no valid claimant (that exec occurrence cannot be classified
    #     within the cap).  A poll-origin anchor invalidates the actual
    #     exec claimants but is never itself observed: a write_stdin
    #     call is not an original exec and no process origin is
    #     invented.  The already-exited single-final candidates are
    #     INCLUDED in this refusal (fixed non-acquiring OVER_BOUND, no
    #     body parse); with only poll-origin anchors and no immediate
    #     occurrences the read surface keeps its honest bookkeeping
    #     (no process observation).
    if blocked_anchors:
        observed_anchors = [
            anchor for anchor in blocked_anchors if anchor[3].rsplit("/", 1)[-1] in _EXEC_LEAVES
        ]
        anchors: list[Claimant | BlockedAnchor] = [*claimants, *observed_anchors]
        anchored = [
            _over_bound_observation(selected_endpoint, anchor, context, bounds)
            for anchor in sorted(anchors, key=_claimant_key)
        ]
        anchored.extend(_immediate_observations(True, selected_endpoint))
        return tuple(anchored)

    # 2. Session ownership: exactly one claimant per session (across ALL
    #    eligible execs, even non-earned-read commands), and no
    #    unresolved known-native claim may remain.
    by_session: dict[int, list[Claimant]] = {}
    for claimant in claimants:
        by_session.setdefault(claimant[9], []).append(claimant)
    if len(by_session) > bounds.max_process_sessions:
        overflowed = [
            _over_bound_observation(selected_endpoint, claimant, context, bounds)
            for claimant in sorted(claimants, key=_claimant_key)
        ]
        # The session cap bounds running-chain ownership only: a
        # single-final claims no session, so its candidates stay decided
        # by their own independent count law (never dropped here).
        overflowed.extend(_immediate_observations(False, selected_endpoint))
        return tuple(overflowed)

    # 3. Poll candidates per chain (closed empty-stdin law).
    poll_calls: list[tuple[str, int, str, object]] = []
    for call_id, position, location, name, arguments in calls:
        if name == _POLL_LEAF:
            poll_calls.append((call_id, position, location, arguments))
    poll_calls.sort(key=lambda item: (item[1], item[0]))

    observations: list[ProcessObservation] = []
    for session, group in sorted(by_session.items(), key=lambda kv: _claimant_key(kv[1][0])):
        if len(group) > 1 or session in ambiguous_sessions:
            # Session not uniquely established — a second claimant or an
            # unresolved known-native running claim (negative
            # ambiguity): every affected initial chain is invalidated
            # (all claimants observable).
            for conflicted in group:
                observations.append(
                    _conflict_observation(
                        selected_endpoint,
                        conflicted,
                        (Limitation.PROCESS_SESSION_CONFLICT,),
                        context,
                        bounds,
                    )
                )
            continue
        claimant = group[0]
        if _id_collided(claimant[0]):
            observations.append(
                _conflict_observation(
                    selected_endpoint,
                    claimant,
                    (Limitation.PROCESS_CHAIN_CONFLICT,),
                    context,
                    bounds,
                )
            )
            continue
        # Sole owner: the body-eligibility decision is the only full
        # frame parse on this chain (after the count/ownership
        # preflights), upgrading the header facts to the full frame.
        frame = parse_native_wrapper(claimant[7], bounds)
        full: Claimant = (
            claimant[0],
            claimant[1],
            claimant[2],
            claimant[3],
            claimant[4],
            claimant[5],
            claimant[6],
            claimant[7],
            frame,
            claimant[9],
        )
        if frame.reasons:
            # Sole owner with an ineligible body: the fixed non-acquiring
            # typed refusal (over-bound stays OVER_BOUND; any other frame
            # refusal keeps its typed reasons).  Competing-owner law was
            # decided above; body eligibility never silences a claimed
            # session.
            if Limitation.OUTPUT_OVER_BOUND in frame.reasons:
                observations.append(
                    _over_bound_observation(selected_endpoint, full, context, bounds)
                )
            else:
                observations.append(
                    _conflict_observation(selected_endpoint, full, frame.reasons, context, bounds)
                )
            continue
        observations.append(
            _collect_chain(
                selected_endpoint,
                session,
                full,
                poll_calls,
                outputs,
                bounds,
                context,
                _id_collided,
            )
        )

    # 4. Already-exited single-final observations (objective 017-am),
    #    appended after the chain observations, sorted by
    #    (exec_call_position, exec_call_id); the duplicated or pre-call
    #    conflicts trail (one fixed non-acquiring observation per
    #    call, never selected, never acquired).  The complete-request
    #    count is decided from bounded header facts BEFORE any full
    #    frame body work or retention: over the bound, every candidate
    #    is a fixed non-acquiring OVER_BOUND (no selection, no full
    #    frame parse).  The count does NOT consume max_process_sessions
    #    (a final frame carries no session section), and the zero-poll
    #    result trivially satisfies the poll ceiling with exactly one
    #    piece against the cumulative char/byte bounds.  The same
    #    assembly is reused by the blocked-anchor and session-cap
    #    early returns so an immediate occurrence is never dropped by
    #    an unrelated refusal.
    observations.extend(_immediate_observations(False, selected_endpoint))
    return tuple(observations)


def _claimant_key(anchor: Claimant | BlockedAnchor) -> tuple[int, str]:
    return anchor[1], anchor[0]


def _over_bound_observation(
    endpoint: str,
    claimant: Claimant | BlockedAnchor | ImmediateCandidate,
    context: PathContext,
    bounds: ObservationBounds,
) -> ProcessObservation:
    """Fixed non-acquiring OVER_BOUND process observation (no pieces)."""

    _kind, requested, _source = _all_cat_region(claimant[4], context, bounds)
    return ProcessObservation(
        endpoint=endpoint,
        exec_call_id=claimant[0],
        exec_call_location=claimant[2],
        exec_call_position=claimant[1],
        initial_result_location=claimant[6],
        initial_result_position=claimant[5],
        initial_wrapper=claimant[8],
        requested_members=requested,
        piece_count=0,
        nonempty_piece_count=0,
        total_char_length=0,
        total_byte_length=0,
        outcome=ProcessOutcome.UNSUPPORTED,
        reasons=(Limitation.OVER_BOUND,),
    )


def _conflict_observation(
    endpoint: str,
    claimant: Claimant | ImmediateCandidate,
    reasons: tuple[Limitation, ...],
    context: PathContext,
    bounds: ObservationBounds,
) -> ProcessObservation:
    """Typed non-acquiring process observation for an invalidated or
    body-ineligible sole-owner chain."""

    _kind, requested, _source = _all_cat_region(claimant[4], context, bounds)
    return ProcessObservation(
        endpoint=endpoint,
        exec_call_id=claimant[0],
        exec_call_location=claimant[2],
        exec_call_position=claimant[1],
        initial_result_location=claimant[6],
        initial_result_position=claimant[5],
        initial_wrapper=claimant[8],
        requested_members=requested,
        piece_count=0,
        nonempty_piece_count=0,
        total_char_length=0,
        total_byte_length=0,
        outcome=ProcessOutcome.UNSUPPORTED,
        reasons=reasons,
    )


def _collect_chain(
    endpoint: str,
    session: int,
    claimant: Claimant,
    poll_calls: list[tuple[str, int, str, object]],
    outputs: dict[str, list[tuple[int, str, str]]],
    bounds: ObservationBounds,
    context: PathContext,
    id_collided: Callable[[str], bool],
) -> ProcessObservation:
    """Collect one sole-owner chain: polls, frames, bounds, completion."""

    (
        call_id,
        call_position,
        _location,
        _name,
        _arguments,
        initial_position,
        _result_location,
        _initial_text,
        _initial_frame,
        _session,
    ) = claimant
    conflict_reasons: list[Limitation] = []
    # Unassignable-argument write_stdin candidates: (call position,
    # call ID); decided against the completed chronology after the
    # poll loop (below).
    orphan_polls: list[tuple[int, str]] = []
    chain_polls: list[ChainPoll] = []
    final: NativeWrapperFacts | None = None
    final_position = -1
    final_location = ""
    # Serial causality anchor: the previous accepted result position
    # (the initial running result until a chain poll is accepted).
    last_result_position = initial_position
    # The original command's finite parsed data is preserved in EVERY
    # outcome (bounded command parse; no payload retention).
    region_kind, requested_members, region_source = _all_cat_region(_arguments, context, bounds)

    for poll_id, poll_position, poll_location, poll_arguments in poll_calls:
        shape = _classify_poll_arguments(poll_arguments, session, bounds)
        if shape is _PollShape.UNRELATED:
            if _poll_argument_session(_decode_poll_arguments(poll_arguments, bounds)) is not None:
                # A proven-different valid argument session: unrelated
                # unique opaque call — it neither joins nor poisons.
                continue
            # An UNASSIGNABLE argument session (malformed/absent/non-int
            # identity, undecodable arguments) is a negative-evidence
            # candidate, decided against the chain's open lifetime
            # AFTER the poll loop, once the terminal result position
            # is known: a poll issued inside the lifetime counts even
            # when its result is delivered late, and a poll issued
            # before the exec issue can never belong to this chain.
            orphan_polls.append((poll_position, poll_id))
            continue
        if shape in (_PollShape.NONEMPTY, _PollShape.INVALID):
            # A matching-session poll that is not the closed empty-stdin
            # poll INVALIDATES the affected initial chain — never filtered
            # away as "not a chain poll", even when a later clean poll
            # returns exit 0.
            if Limitation.PROCESS_POLL_INVALID not in conflict_reasons:
                conflict_reasons.append(Limitation.PROCESS_POLL_INVALID)
            continue
        # shape == CLOSED: a chain poll for this session.
        if final is not None:
            # An after-final poll: the chain already proved completion; a
            # later matching poll is a typed conflict, never silently
            # ignored.
            if Limitation.PROCESS_CHAIN_CONFLICT not in conflict_reasons:
                conflict_reasons.append(Limitation.PROCESS_CHAIN_CONFLICT)
            continue
        # Resource ceiling BEFORE any further work on this candidate:
        # accepting this poll would exceed the configured poll/piece
        # bound, so the over-limit candidate frame is neither parsed
        # nor retained (at-limit chains stay exactly at the bound).
        if (
            len(chain_polls) >= bounds.max_process_polls
            or (1 + len(chain_polls)) >= bounds.max_process_pieces
        ):
            return _over_bound_observation(endpoint, claimant, context, bounds)
        if poll_position <= last_result_position:
            # Serial causality broken: the poll was issued at or before
            # the previous accepted result (for the first chain poll,
            # the initial running result).  The affected chain is
            # invalidated (typed) — never re-ordered, never skipped.
            if Limitation.PROCESS_CHAIN_CONFLICT not in conflict_reasons:
                conflict_reasons.append(Limitation.PROCESS_CHAIN_CONFLICT)
            continue
        if id_collided(poll_id):
            if Limitation.PROCESS_CHAIN_CONFLICT not in conflict_reasons:
                conflict_reasons.append(Limitation.PROCESS_CHAIN_CONFLICT)
            continue
        results = outputs.get(poll_id, ())
        if len(results) == 0:
            # An issued poll missing its own result invalidates the
            # affected initial chain.
            if Limitation.PROCESS_CHAIN_CONFLICT not in conflict_reasons:
                conflict_reasons.append(Limitation.PROCESS_CHAIN_CONFLICT)
            continue
        if len(results) > 1:
            # A duplicated result on a chain call: conflicting identity.
            if Limitation.PROCESS_CHAIN_CONFLICT not in conflict_reasons:
                conflict_reasons.append(Limitation.PROCESS_CHAIN_CONFLICT)
            continue
        result_position, result_location, text = results[0]
        if result_position <= poll_position:
            # Pre-call result on the poll: causality broken.
            if Limitation.PROCESS_CHAIN_CONFLICT not in conflict_reasons:
                conflict_reasons.append(Limitation.PROCESS_CHAIN_CONFLICT)
            continue
        frame = parse_native_wrapper(text, bounds)
        if Limitation.OUTPUT_OVER_BOUND in frame.reasons:
            # Over-bound frame: fixed non-acquiring OVER_BOUND, no piece
            # retention for this chain.
            return _over_bound_observation(endpoint, claimant, context, bounds)
        if frame.reasons:
            # A frame that does not parse the closed native grammar
            # breaks chain coherence.
            if Limitation.PROCESS_CHAIN_CONFLICT not in conflict_reasons:
                conflict_reasons.append(Limitation.PROCESS_CHAIN_CONFLICT)
            for reason in frame.reasons:
                if reason not in conflict_reasons:
                    conflict_reasons.append(reason)
            continue
        if frame.exit_code is None and frame.session_id != session:
            # Neither an actual exit nor a same-session running frame:
            # an unknown-status or foreign-session frame is conflicting
            # identity for the affected chain.
            if Limitation.PROCESS_CHAIN_CONFLICT not in conflict_reasons:
                conflict_reasons.append(Limitation.PROCESS_CHAIN_CONFLICT)
            continue
        chain_polls.append(
            (poll_id, poll_position, poll_location, result_position, result_location, text, frame)
        )
        last_result_position = result_position
        if frame.exit_code is not None:
            # The first frame carrying the exit section terminates the
            # chain.
            final = frame
            final_position = result_position
            final_location = result_location

    # Unassignable-argument native polls decided against the completed
    # chronology: a poll ISSUED after the exec issue and before the
    # chain's terminal result (no terminal result: the chain is still
    # open) is potentially associated, and any of its bounded own
    # result records carrying a well-formed native header — running,
    # final or unknown-status (a malformed header claims nothing; an
    # over-bound header was already a blocked anchor in the owner
    # inventory; duplicated results never repair) — prevents
    # complete-source proof while the chain was open, even when the
    # result is delivered late (it can still hide a piece).  Negative
    # invalidation: never SID coercion, never inferred execution or
    # owner.  A poll issued before the exec issue or after the
    # terminal result is not poisoned (numeric call/result chronology).
    if not conflict_reasons:
        for poll_position, poll_id in orphan_polls:
            if not (
                call_position < poll_position
                and (final_position < 0 or poll_position < final_position)
            ):
                continue
            for _orphan_position, _orphan_location, orphan_text in outputs.get(poll_id, ()):
                if _native_header_facts(orphan_text, bounds) is not None:
                    conflict_reasons.append(Limitation.PROCESS_CHAIN_CONFLICT)
                    break
            if Limitation.PROCESS_CHAIN_CONFLICT in conflict_reasons:
                break

    if conflict_reasons:
        return _conflict_observation(endpoint, claimant, tuple(conflict_reasons), context, bounds)

    # Cumulative source bound BEFORE any piece retention or
    # concatenation copy: the exact UTF-8 byte total and the character
    # total are decided from the bounded frame parses only.
    frames: list[NativeWrapperFacts] = [_initial_frame]
    frames.extend(poll[6] for poll in chain_polls)
    total_chars = sum(frame.output_char_length or 0 for frame in frames)
    total_bytes = sum(frame.output_byte_length or 0 for frame in frames)
    if (
        total_chars > bounds.max_process_source_chars
        or total_bytes > bounds.max_process_source_bytes
    ):
        return _over_bound_observation(endpoint, claimant, context, bounds)

    # Bounds decided: retain the exact pieces and the frames.
    texts: list[str] = []
    pieces: list[ProcessPiece] = []
    piece_spans: list[CharSpan] = []
    initial_frame = _initial_frame
    assert initial_frame.output_span is not None
    assert initial_frame.output_char_length is not None
    assert initial_frame.output_byte_length is not None
    texts.append(_initial_text[initial_frame.output_span.start : initial_frame.output_span.end])
    pieces.append(
        ProcessPiece(
            piece_index=0,
            result_location=_result_location,
            char_span=initial_frame.output_span,
            char_length=initial_frame.output_char_length,
            byte_length=initial_frame.output_byte_length,
            empty=initial_frame.output_char_length == 0,
        )
    )
    piece_spans.append(initial_frame.output_span)
    polls: list[ProcessPoll] = []
    for index, (
        poll_id,
        poll_position,
        poll_location,
        result_position,
        result_location,
        text,
        frame,
    ) in enumerate(chain_polls, start=1):
        assert frame.output_span is not None
        assert frame.output_char_length is not None
        assert frame.output_byte_length is not None
        texts.append(text[frame.output_span.start : frame.output_span.end])
        piece = ProcessPiece(
            piece_index=index,
            result_location=result_location,
            char_span=frame.output_span,
            char_length=frame.output_char_length,
            byte_length=frame.output_byte_length,
            empty=frame.output_char_length == 0,
        )
        pieces.append(piece)
        piece_spans.append(frame.output_span)
        polls.append(
            ProcessPoll(
                poll_call_id=poll_id,
                poll_call_location=poll_location,
                poll_position=poll_position,
                result_location=result_location,
                result_position=result_position,
                wrapper=frame,
                piece=piece,
            )
        )

    nonempty = sum(1 for piece in pieces if not piece.empty)

    base: _BaseObservationFields = {
        "endpoint": endpoint,
        "exec_call_id": call_id,
        "exec_call_location": claimant[2],
        "exec_call_position": claimant[1],
        "initial_result_location": _result_location,
        "initial_result_position": initial_position,
        "initial_wrapper": initial_frame,
        "requested_members": requested_members,
        "polls": tuple(polls),
        "final_result_location": final_location if final is not None else None,
        "final_result_position": final_position if final is not None else None,
        "final_wrapper": final,
        "pieces": tuple(pieces),
        "piece_count": len(pieces),
        "nonempty_piece_count": nonempty,
        "total_char_length": total_chars,
        "total_byte_length": total_bytes,
    }

    return _finish_process_observation(
        base,
        tuple(frames),
        tuple(texts),
        tuple(piece_spans),
        region_kind,
        region_source,
        _evidence_parse(_arguments, context, bounds),
    )


def _finish_process_observation(
    base: _BaseObservationFields,
    frames: tuple[NativeWrapperFacts, ...],
    texts: tuple[str, ...],
    piece_spans: tuple[CharSpan, ...],
    region_kind: str | None,
    region_source: ReadCommandParse | ReadPlanParse | LoopParse | None,
    evidence_parse: ReadCommandParse | ReadPlanParse | LoopParse | None,
) -> ProcessObservation:
    """The shared terminal completion law over the retained pieces.

    Used by both chain collection and single-final collection
    (objective 017-am): the chain's final frame is
    ``base["final_wrapper"]``; a single-final occurrence's frame is both
    its initial and terminal result.  Behavior is identical to the
    original chain tail, plus the additive final-``cat`` evidence
    decided from the terminal frame's exit fact (evidence only, never
    acquisition — a single-final status cannot repair a conflicting or
    missing running chain, which the collector decides separately).
    """

    final = base["final_wrapper"]
    truncated_frames = [frame for frame in frames if frame.truncated]

    exit_zero: bool | None = None
    if final is not None and final.exit_code is not None:
        exit_zero = final.exit_code == 0
    evidence, evidence_indexes = final_cat_evidence(evidence_parse, exit_zero)

    if truncated_frames:
        # A truncated frame anywhere invalidates whole-source completion
        # even on final exit zero.
        return ProcessObservation(
            **base,
            outcome=ProcessOutcome.TRUNCATED,
            final_cat_evidence=evidence,
            final_cat_member_indexes=evidence_indexes,
            reasons=(Limitation.PROCESS_TRUNCATED,),
        )
    if final is None:
        # No frame proved completion: an honest still-running state,
        # never a completion claim (no exit fact: unknown evidence).
        return ProcessObservation(
            **base,
            outcome=ProcessOutcome.RUNNING,
            final_cat_evidence=evidence,
            final_cat_member_indexes=evidence_indexes,
            reasons=(Limitation.PROCESS_RUNNING,),
        )
    if final.exit_code is None:
        # Defensive: a terminating frame always carries the exit section.
        return ProcessObservation(
            **base,
            outcome=ProcessOutcome.UNSUPPORTED,
            final_cat_evidence=evidence,
            final_cat_member_indexes=evidence_indexes,
            reasons=(Limitation.PROCESS_CHAIN_CONFLICT,),
        )
    if final.exit_code != 0:
        return ProcessObservation(
            **base,
            outcome=ProcessOutcome.NONZERO_EXIT,
            final_cat_evidence=evidence,
            final_cat_member_indexes=evidence_indexes,
        )

    # Proven final success: the earned outer attribution on the transient
    # joined view, mapped back onto the original pieces.
    concatenated = "".join(texts)
    region: CharSpan | None = None
    proven: tuple[str, ...] = ()
    if region_kind == "single":
        parsed = region_source
        assert parsed is not None
        assert isinstance(parsed, ReadCommandParse)
        if parsed.reasons == ():
            region = CharSpan(start=0, end=len(concatenated))
            proven = tuple(o.normalized for o in parsed.operands if o.normalized is not None)
    elif region_kind == "plan":
        plan = region_source
        assert plan is not None
        assert isinstance(plan, ReadPlanParse)
        plan_region, _plan_reasons = plan_source_region(plan, concatenated)
        if plan_region is not None:
            region = plan_region
            proven = tuple(m.normalized for m in plan.requested_members if m.normalized is not None)
    elif region_kind == "loop":
        loop = region_source
        assert loop is not None
        assert isinstance(loop, LoopParse)
        region = CharSpan(start=0, end=len(concatenated))
        proven = tuple(m.normalized for m in loop.requested_members if m.normalized is not None)

    if region is None:
        # Process completion is earned; source attribution to the
        # requested members is not (the command is not a complete all-cat
        # parse).  No digest, no region, no invented width.
        return ProcessObservation(
            **base,
            outcome=ProcessOutcome.COMPLETE,
            final_cat_evidence=evidence,
            final_cat_member_indexes=evidence_indexes,
        )

    region_piece_spans, region_length, region_digest = _map_region_to_pieces(
        region, texts, piece_spans
    )
    distinct = len(set(proven))
    if len(proven) == 1:
        # The occurrence-hash law: exactly one attributable file
        # occurrence covering the proven region carries its exact digest
        # (a zero-byte region is the complete empty version).
        member_digests: tuple[str | None, ...] = (
            EMPTY_SOURCE_SHA256 if region_length == 0 else region_digest,
        )
    else:
        # Boundaryless multiple occurrences (repeated or distinct
        # members alike): none is attributable on its own, so every
        # member digest stays unknown and no per-member hash is invented.
        member_digests = tuple(None for _ in proven)
    return ProcessObservation(
        **base,
        proven_executed=proven,
        member_digests=member_digests,
        region_piece_spans=region_piece_spans,
        proven_region_char_length=region_length,
        distinct_member_count=distinct,
        slot_width=distinct,
        outcome=ProcessOutcome.COMPLETE,
        bundle_digest=region_digest,
        final_cat_evidence=evidence,
        final_cat_member_indexes=evidence_indexes,
    )


def _collect_single_final(
    endpoint: str,
    candidate: ImmediateCandidate,
    context: PathContext,
    bounds: ObservationBounds,
) -> ProcessObservation:
    """Collect one already-exited single-final occurrence (objective 017-am).

    The result is its own initial and terminal result: zero polls,
    exactly one piece, no invented session, and no coordinate into a
    virtual joined string (the transient joined view of one piece IS
    that piece's own text).  The body-eligibility decision is the sole
    full frame parse on this occurrence (after the immediate-count
    preflight); the completion law is the shared terminal law over the
    single piece.
    """

    (
        call_id,
        call_position,
        _location,
        _name,
        _arguments,
        initial_position,
        _result_location,
        _initial_text,
        _header,
    ) = candidate
    # Sole-candidate body eligibility: the only full frame parse on
    # this occurrence (after the count/ownership preflights), upgrading
    # the header facts to the full frame.
    frame = parse_native_wrapper(_initial_text, bounds)
    full: ImmediateCandidate = (*candidate[:8], frame)
    if frame.reasons:
        # Over-bound stays OVER_BOUND; any other frame refusal keeps its
        # typed reasons (non-acquiring either way).
        if Limitation.OUTPUT_OVER_BOUND in frame.reasons:
            return _over_bound_observation(endpoint, full, context, bounds)
        return _conflict_observation(endpoint, full, frame.reasons, context, bounds)
    # The original command's finite parsed data is preserved in EVERY
    # outcome (bounded command parse; no payload retention).
    region_kind, requested_members, region_source = _all_cat_region(_arguments, context, bounds)
    # Cumulative source bound BEFORE any piece retention or
    # concatenation copy (the single frame's exact char/byte totals).
    total_chars = frame.output_char_length or 0
    total_bytes = frame.output_byte_length or 0
    if (
        total_chars > bounds.max_process_source_chars
        or total_bytes > bounds.max_process_source_bytes
    ):
        return _over_bound_observation(endpoint, full, context, bounds)
    # Bounds decided: retain the exact one piece (absolute offsets in
    # the exact decoded JSON string that carried the result text).
    assert frame.output_span is not None
    assert frame.output_char_length is not None
    assert frame.output_byte_length is not None
    text = _initial_text[frame.output_span.start : frame.output_span.end]
    piece = ProcessPiece(
        piece_index=0,
        result_location=_result_location,
        char_span=frame.output_span,
        char_length=frame.output_char_length,
        byte_length=frame.output_byte_length,
        empty=frame.output_char_length == 0,
    )
    base: _BaseObservationFields = {
        "endpoint": endpoint,
        "exec_call_id": call_id,
        "exec_call_location": _location,
        "exec_call_position": call_position,
        "initial_result_location": _result_location,
        "initial_result_position": initial_position,
        "initial_wrapper": frame,
        "requested_members": requested_members,
        "polls": (),
        "final_result_location": _result_location,
        "final_result_position": initial_position,
        "final_wrapper": frame,
        "pieces": (piece,),
        "piece_count": 1,
        "nonempty_piece_count": 0 if piece.empty else 1,
        "total_char_length": total_chars,
        "total_byte_length": total_bytes,
    }
    return _finish_process_observation(
        base,
        (frame,),
        (text,),
        (frame.output_span,),
        region_kind,
        region_source,
        _evidence_parse(_arguments, context, bounds),
    )

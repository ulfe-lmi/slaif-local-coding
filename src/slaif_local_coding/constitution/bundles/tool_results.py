"""Supported tool call/result pairing and exec-wrapper parsing (D05).

Pairing law: a call and its result pair by **exact call ID** and **within
the same endpoint envelope** — a Responses ``input`` call pairs only with a
Responses ``function_call_output``, a Chat ``messages`` call only with a
Chat ``role=tool`` message.  An ID match across endpoints is never evidence
(mixed shapes are typed missing/mismatched, never guessed).  Only supported
tool names are eligible: the bare supported names, ``write_stdin`` (typed
deferred), or a namespace-qualified name whose **leaf** is a known
executable supported name **and** whose exact name the request's own
``tools`` array declares with the compatible ``cmd`` string schema.  A
declared unrelated bare function with a ``cmd``-shaped parameter is not an
exec tool; suffix or substring resemblance is never evidence.  Identity-
conflict law: the relevant schema-evidenced call identities are
inventoried **before** read eligibility is applied —
every call record in a schema call position (Responses ``input``
``function_call`` and ``custom_tool_call`` items; Chat assistant
``tool_calls`` ``function`` entry), regardless of whether its tool
name earns read support.  The Responses ``custom_tool_call`` wire
family is identity bookkeeping only: it earns no custom-tool read
parsing, execution or acquisition, its opaque input is never
captured as arguments and never reinterpreted as a shell or source
oracle, and no generic unknown-family wildcard recognition is
invented.  An unknown or ineligible tool call never acquires a
source, but a collision with an eligible call ID cannot disappear
through eligibility filtering: an exact ID collision makes the
ambiguous eligible chain a typed ``DUPLICATE_CALL_ID`` conflict,
non-removable, with no acquired digest, span or proven members, and
every relevant occurrence stays observable, never first-match.  A
unique unrelated opaque custom call neither records nor poisons a
separate valid read.  Arbitrary nested text objects carrying
``id``/``name`` are not call records.  Missing, empty or malformed
call IDs remain observable as typed conflicts and never acquire
content; no ID is ever invented.  Duplicate or missing call IDs are
typed conflicts, never first-match selection.  Complete-inventory
bound law: ``max_commands`` is enforced against **all** relevant
schema-position call records — including unsupported names, opaque
custom records and missing/empty/malformed IDs — and
``max_outputs`` against **all** relevant result records, including
invalid IDs, before any identity map or typed diagnostic is
retained or built: a fixed non-acquiring ``OVER_BOUND`` result,
never a silently truncated inventory that acquires an earlier chain
while missing a later collision.  For explicit endpoint selection
only the selected domain contributes; mixed input remains
non-acquiring under the existing law, bounded across its inspected
domains.  Result-ID observability law: in the relevant Responses
``function_call_output`` and Chat ``role=tool`` schema positions, an
absent/null/empty result ID is typed ``MISSING_RESULT_ID`` and a
present non-string result ID is typed ``MALFORMED_RESULT_ID`` —
fixed, non-echoing, unpaired limitations: no ID is invented, no
unhashable value is hashed, the malformed output is never attached
to any call and nothing is acquired from it.  Causality law: a
result attaches to its matching call only when its exact numeric
structural position (the ``input`` item index;
the Chat ``messages`` index of the assistant message carrying the call)
follows the call's position — never from lexical call IDs, JSONPath
string sorting or JSONPath evaluation.  A pre-call result is a typed
``PRE_CALL_RESULT`` chain: non-removable, with no bundle/member digest,
no source span and no proven-executed claim; missing initial calls
remain unsupported.  Multi-chunk results and process-running/
write_stdin traffic are explicitly deferred in this slice (typed
unsupported, D09 territory).

Endpoint-selection law: one API request is one endpoint, never a batch of
two.  The selected domain is an explicit validated endpoint context or an
inferred **unambiguous** supported envelope (exactly one of ``input`` /
``messages`` present).  A mixed shape (both present, no explicit context)
is typed ``ENDPOINT_UNSUPPORTED`` and non-removable: pairing bookkeeping
(duplicate/missing/mismatched IDs) is preserved, but no read is ever
acquired from either container — never by precedence, never as two real
calls.  An explicit endpoint scopes observation to its own root/call/
result container; the other container is never acquired.  The global
endpoint and per-read endpoints always agree about the selected domain
(the per-read value is the container provenance of a typed record when the
global selection is mixed).

Wrapper law: the observed Codex exec wrapper carries its metadata **before**
the ``Output:`` line; everything after that line is source, and source that
merely looks like execution metadata never redefines wrapper status.  The
recognized header lines are the human-handoff real format
(``Chunk ID: <token>``) plus the explicitly earned compatible variant
(``Chunk Id: <token>``), ``Wall time: <…>``, ``Process exited with code
<0-255>`` (bounded ASCII numeric grammar) and ``Truncated: true|false``.
Each status field (exit code, truncation) appears at most once: any
repetition — contradictory or identical — is a typed
``MALFORMED_WRAPPER`` limitation, never last-field-wins.  The declared
``max_wrapper_header_lines`` bound is enforced before the frame is
accepted.  A proven empty successful output (wrapper exit zero,
``Output:`` present, zero content bytes) is a complete empty version; a
missing body is a different, explicit state.
"""

from __future__ import annotations

from typing import Any

from ..bundles.compound_reads import (
    READ_PLAN_GRAMMAR,
    parse_read_plan,
    plan_source_region,
)
from ..bundles.literal_loops import (
    LOOP_GRAMMAR,
    LoopParse,
    parse_literal_loop,
)
from ..bundles.observation_models import (
    EMPTY_SOURCE_SHA256,
    CharSpan,
    ExitStatus,
    Limitation,
    ObservationBounds,
    PathContext,
    ReadObservation,
    ReadOutcome,
    TruncationStatus,
    UnpairedRecord,
    WrapperFacts,
    contains_lone_surrogates,
    sha256_hex,
)
from ..bundles.read_grammar import parse_read_command, unwrap_call_arguments

_SUPPORTED_TOOL_NAMES = frozenset({"exec_command", "shell_command"})
_WRITE_STDIN = "write_stdin"
_OUTPUT_MARKER = "Output:"
_RUNNING_MARKER = "Process is still running"
_EXIT_PREFIX = "Process exited with code "
# Human-handoff 6.2 real format first; the compatible variant earned by the
# 017 slice fixtures/tests is explicitly retained.
_CHUNK_ID_PREFIXES = ("Chunk ID: ", "Chunk Id: ")
# The documented status range is 0..255: at most three ASCII digits.
_MAX_EXIT_DIGITS = 3
_HEADER_VALUE_MAX_CHARS = 128


def _declared_tool_names(payload: dict[str, Any], bounds: ObservationBounds) -> set[str]:
    """Names the request's own ``tools`` envelope declares (evidence only)."""

    tools = payload.get("tools")
    if not isinstance(tools, list):
        return set()
    names: set[str] = set()
    for tool in tools[: bounds.max_tools]:
        if not isinstance(tool, dict) or tool.get("type") != "function":
            continue
        name = tool.get("name")
        if isinstance(name, str) and name:
            names.add(name)
    return names


def _envelope_proves_executable(
    payload: dict[str, Any], name: str, bounds: ObservationBounds
) -> bool:
    """Explicit compatible declaration for a namespace-qualified tool name.

    The request's own ``tools`` array must declare the exact name with a
    ``cmd`` string parameter (the observed Codex exec schema).  Suffix or
    substring resemblance is never evidence, and a declaration alone never
    makes an unrelated bare function an exec tool (the leaf of a supported
    name is required first).
    """

    tools = payload.get("tools")
    if not isinstance(tools, list):
        return False
    for tool in tools[: bounds.max_tools]:
        if not isinstance(tool, dict) or tool.get("type") != "function":
            continue
        if tool.get("name") != name:
            continue
        parameters = tool.get("parameters")
        if not isinstance(parameters, dict):
            continue
        properties = parameters.get("properties")
        if not isinstance(properties, dict):
            continue
        cmd = properties.get("cmd")
        if isinstance(cmd, dict) and cmd.get("type") == "string":
            return True
    return False


def _eligible_tool_name(name: str, payload: dict[str, Any], bounds: ObservationBounds) -> bool:
    """Eligibility: known executable name, plus explicit compatible
    declaration for supported namespace-qualified forms."""

    if name in _SUPPORTED_TOOL_NAMES or name == _WRITE_STDIN:
        return True
    if "/" not in name:
        # A bare unknown function (even declared with a cmd-shaped
        # parameter) is never an exec tool.
        return False
    leaf = name.rsplit("/", 1)[-1]
    if leaf not in _SUPPORTED_TOOL_NAMES:
        return False
    return _envelope_proves_executable(payload, name, bounds)


def parse_wrapper(output: str, bounds: ObservationBounds) -> WrapperFacts:
    """Parse exec-wrapper metadata from one result body (versioned format).

    The header is a bounded block of recognized lines before the ``Output:``
    marker line, which itself must be newline-terminated.  Everything after
    the marker line is the exact source region.  Status fields appear at
    most once; the header-line bound is enforced before the frame is
    accepted.  Plain unstructured output is unknown completion, never
    complete; process-running bodies are typed.
    """

    def _facts(
        exit_status: ExitStatus,
        exit_code: int | None,
        truncation: TruncationStatus,
        output_present: bool,
        header_span: CharSpan | None,
        output_span: CharSpan | None,
        reasons: tuple[Limitation, ...],
    ) -> WrapperFacts:
        return WrapperFacts(
            exit_status=exit_status,
            exit_code=exit_code,
            truncation=truncation,
            output_present=output_present,
            header_span=header_span,
            output_span=output_span,
            reasons=reasons,
        )

    if len(output) > bounds.max_output_chars:
        return _facts(
            ExitStatus.UNKNOWN,
            None,
            TruncationStatus.UNKNOWN,
            False,
            None,
            None,
            (Limitation.OUTPUT_OVER_BOUND,),
        )
    if output == "":
        return _facts(
            ExitStatus.UNKNOWN,
            None,
            TruncationStatus.UNKNOWN,
            False,
            None,
            None,
            (Limitation.MISSING_OUTPUT_BODY,),
        )

    lines = output.split("\n")
    exit_status = ExitStatus.UNKNOWN
    exit_code: int | None = None
    exit_seen = False
    truncation = TruncationStatus.UNKNOWN
    truncation_seen = False
    saw_header = False
    header_lines = 0
    index = 0

    def _count_header_line() -> tuple[Limitation | None, bool]:
        # Enforce the declared header-line bound before the frame is
        # accepted; over-bound headers are typed, never complete.
        nonlocal header_lines, saw_header
        header_lines += 1
        if header_lines > bounds.max_wrapper_header_lines:
            return Limitation.OVER_BOUND, True
        saw_header = True
        return None, True

    while index < len(lines):
        line = lines[index].rstrip("\r")
        if line == _OUTPUT_MARKER:
            if index == len(lines) - 1:
                # The marker line is not newline-terminated: torn wrapper.
                return _facts(
                    exit_status,
                    exit_code,
                    truncation,
                    False,
                    None,
                    None,
                    (Limitation.MALFORMED_WRAPPER,),
                )
            break
        if line == _RUNNING_MARKER:
            return _facts(
                ExitStatus.UNKNOWN,
                None,
                TruncationStatus.UNKNOWN,
                False,
                None,
                None,
                (Limitation.PROCESS_RUNNING,),
            )
        matched = False
        if line.startswith(_CHUNK_ID_PREFIXES) or line.startswith("Wall time: "):
            value = line.split(": ", 1)[1]
            if value and len(value) <= _HEADER_VALUE_MAX_CHARS:
                over, ok = _count_header_line()
                if over is not None:
                    return _facts(exit_status, exit_code, truncation, False, None, None, (over,))
                matched = ok
        elif line.startswith(_EXIT_PREFIX):
            if exit_seen:
                # A repeated status field (contradictory or identical) is
                # malformed: the versioned wrapper carries each status
                # field exactly once.  Never last-field-wins — the frame
                # carries no trusted status at all.
                return _facts(
                    ExitStatus.UNKNOWN,
                    None,
                    TruncationStatus.UNKNOWN,
                    False,
                    None,
                    None,
                    (Limitation.MALFORMED_WRAPPER,),
                )
            value = line[len(_EXIT_PREFIX) :]
            # Bounded canonical ASCII decimal grammar: 0..255, no leading
            # zeros, at most three digits.  Unicode digit-likes, padded and
            # over-long fields are typed malformed, never int()-converted
            # (no ValueError, no unbounded work).
            if (
                value
                and value.isascii()
                and value.isdigit()
                and len(value) <= _MAX_EXIT_DIGITS
                and (value == "0" or value[0] != "0")
            ):
                code = int(value)
                if code <= 255:
                    over, _ = _count_header_line()
                    if over is not None:
                        return _facts(
                            exit_status,
                            exit_code,
                            truncation,
                            False,
                            None,
                            None,
                            (over,),
                        )
                    exit_status = ExitStatus.ZERO if code == 0 else ExitStatus.NONZERO
                    exit_code = code
                    exit_seen = True
                    matched = True
        elif line.startswith("Truncated: "):
            if truncation_seen:
                return _facts(
                    ExitStatus.UNKNOWN,
                    None,
                    TruncationStatus.UNKNOWN,
                    False,
                    None,
                    None,
                    (Limitation.MALFORMED_WRAPPER,),
                )
            value = line.split(": ", 1)[1]
            if value in ("true", "false"):
                over, _ = _count_header_line()
                if over is not None:
                    return _facts(
                        exit_status,
                        exit_code,
                        truncation,
                        False,
                        None,
                        None,
                        (over,),
                    )
                truncation = TruncationStatus.TRUE if value == "true" else TruncationStatus.FALSE
                truncation_seen = True
                matched = True
        if not matched:
            reason = Limitation.MALFORMED_WRAPPER if saw_header else Limitation.UNKNOWN_COMPLETION
            return _facts(exit_status, exit_code, truncation, False, None, None, (reason,))
        index += 1
    else:
        # No ``Output:`` marker anywhere.
        reason = Limitation.MALFORMED_WRAPPER if saw_header else Limitation.UNKNOWN_COMPLETION
        return _facts(exit_status, exit_code, truncation, False, None, None, (reason,))

    # Content is everything after the marker line's newline: exact source.
    output_start = sum(len(part) + 1 for part in lines[: index + 1])
    output_span = CharSpan(start=output_start, end=len(output))
    header_span = CharSpan(start=0, end=output_start)

    if truncation is TruncationStatus.TRUE:
        return _facts(
            exit_status,
            exit_code,
            truncation,
            True,
            header_span,
            output_span,
            (Limitation.TRUNCATED_OUTPUT,),
        )
    if exit_status is ExitStatus.NONZERO:
        return _facts(
            exit_status,
            exit_code,
            truncation,
            True,
            header_span,
            output_span,
            (Limitation.NONZERO_EXIT,),
        )
    if exit_status is ExitStatus.UNKNOWN:
        return _facts(
            exit_status,
            exit_code,
            truncation,
            True,
            header_span,
            output_span,
            (Limitation.UNKNOWN_COMPLETION,),
        )
    return _facts(ExitStatus.ZERO, exit_code, truncation, True, header_span, output_span, ())


def _workdir_literal(workdir: str) -> bool:
    """Explicit per-call workdir must be a clean literal (no control chars)."""

    return bool(workdir) and not any(ord(c) < 0x20 or ord(c) == 0x7F for c in workdir)


#: One schema-evidenced call record: ``(wire_family, position, location,
#: raw_id, raw_name, arguments)``.  ``wire_family`` is the exact schema
#: item type that evidences the record (Responses ``function_call`` /
#: ``custom_tool_call``; Chat ``function``); it preserves the exact
#: family/name/ID association and gates acquisition eligibility (the
#: custom family is identity bookkeeping only).  ``position`` is the
#: exact numeric structural position (the Responses ``input`` item index,
#: or the Chat ``messages`` index of the assistant message carrying the
#: tool call); causality is established from these positions, never from
#: lexical IDs.  ``raw_id``/``raw_name`` are the exact observed values
#: (any JSON type, or ``None`` when the key is absent); no ID is ever
#: invented.  ``arguments`` carries the exact observed function arguments
#: only — the opaque ``custom_tool_call`` input is never captured here.
CallRecord = tuple[str, int, str, object, object, object]

#: Wire families that may earn read acquisition.  The Responses
#: ``custom_tool_call`` family is deliberately absent: it participates in
#: identity bookkeeping only and never acquires, whatever its name.
_ACQUIRABLE_CALL_FAMILIES = frozenset({"function_call", "function"})

#: One eligible acquisition call: ``(id, position, location, name,
#: arguments)``.
EligibleCall = tuple[str, int, str, str, object]


def _call_records(
    input_items: list[Any] | None, messages: list[Any] | None
) -> tuple[list[CallRecord], list[CallRecord]]:
    """Inventory every schema-evidenced call record per endpoint.

    Returns ``(responses_records, chat_records)``.  A call record is any
    object in a schema call position — a Responses ``input`` item with
    ``type == "function_call"`` or ``type == "custom_tool_call"``, or a
    Chat assistant ``tool_calls`` entry with ``type == "function"`` —
    **regardless of whether its tool name earns read support**.  The
    inventory exists so that an unknown/ineligible call's ID (and an
    opaque custom call's ID) still participates in identity-conflict
    bookkeeping; it is not evidence of read or execution support, and
    arbitrary nested text objects carrying ``id``/``name`` fields are
    not call records.  The ``custom_tool_call`` family is captured for
    identity bookkeeping only: its opaque ``input`` is never stored in
    the record (``arguments`` stays ``None``) and the family never earns
    acquisition.  No other wire family is recognized (no generic
    unknown-family wildcard).
    """

    responses: list[CallRecord] = []
    if input_items is not None:
        for index, item in enumerate(input_items):
            if not isinstance(item, dict):
                continue
            wire_family = item.get("type")
            if wire_family == "function_call":
                arguments: object = item.get("arguments")
            elif wire_family == "custom_tool_call":
                arguments = None
            else:
                continue
            responses.append(
                (
                    wire_family,
                    index,
                    f"$.input[{index}]",
                    item["call_id"] if "call_id" in item else None,
                    item.get("name"),
                    arguments,
                )
            )

    chat: list[CallRecord] = []
    if messages is not None:
        for index, message in enumerate(messages):
            if not isinstance(message, dict) or message.get("role") != "assistant":
                continue
            tool_calls = message.get("tool_calls")
            if not isinstance(tool_calls, list):
                continue
            for tool_index, tool in enumerate(tool_calls):
                if not isinstance(tool, dict) or tool.get("type") != "function":
                    continue
                function = tool.get("function")
                if isinstance(function, dict):
                    raw_name = function.get("name")
                    arguments = function.get("arguments")
                else:
                    raw_name = None
                    arguments = None
                chat.append(
                    (
                        "function",
                        index,
                        f"$.messages[{index}].tool_calls[{tool_index}]",
                        tool["id"] if "id" in tool else None,
                        raw_name,
                        arguments,
                    )
                )
    return responses, chat


def _call_entries(
    payload: dict[str, Any],
    bounds: ObservationBounds,
    responses_records: list[CallRecord],
    chat_records: list[CallRecord],
) -> tuple[list[EligibleCall], list[EligibleCall]]:
    """Eligible acquisition calls with exact structural positions.

    Returns ``(responses_calls, chat_calls)`` as
    ``(call_id, position, location, tool_name, arguments)`` tuples.  A
    record earns read eligibility only when its wire family is an
    acquirable family (the ``custom_tool_call`` family never does,
    whatever its name), its observed ID is a non-empty string, **and**
    its tool name is a supported read name (bare supported name,
    deferred ``write_stdin``, or an envelope-proven namespace form).
    Unsupported names never acquire; malformed or missing IDs never
    pair.  Endpoints never mix.
    """

    def _eligible(records: list[CallRecord]) -> list[EligibleCall]:
        calls: list[EligibleCall] = []
        for wire_family, position, location, raw_id, raw_name, arguments in records:
            if wire_family not in _ACQUIRABLE_CALL_FAMILIES:
                continue
            if not isinstance(raw_id, str) or not raw_id:
                continue
            if not isinstance(raw_name, str) or not raw_name:
                continue
            if not _eligible_tool_name(raw_name, payload, bounds):
                continue
            calls.append((raw_id, position, location, raw_name, arguments))
        return calls

    return _eligible(responses_records), _eligible(chat_records)


#: One typed result-ID defect: ``(location, limitation)`` for a schema
#: result position whose ID is absent/null/empty (``MISSING_RESULT_ID``)
#: or present but non-string (``MALFORMED_RESULT_ID``).  Defects are
#: observable, counted against the output bound, never paired, never
#: acquired, and never echo the offending value.
ResultDefect = tuple[str, Limitation]


def _result_entries(
    input_items: list[Any] | None, messages: list[Any] | None
) -> tuple[
    dict[str, list[tuple[int, str, str]]],
    list[ResultDefect],
    dict[str, list[tuple[int, str, str]]],
    list[ResultDefect],
]:
    """Collect results by exact call ID per endpoint, with typed ID defects.

    Returns ``(responses_outputs, responses_defects, chat_outputs,
    chat_defects)`` where ``outputs`` maps a valid non-empty string ID to
    ``[(position, location, text)]`` and position is the exact numeric
    structural position (the ``input`` item index; the Chat ``messages``
    index of the tool message).  A result whose ID is absent, JSON null
    or an empty string is a typed ``MISSING_RESULT_ID`` defect; a
    present non-string ID is a typed ``MALFORMED_RESULT_ID`` defect.
    Defects are not pairing evidence: they can never match a call, and
    the defect is observed by the pairing bookkeeping, not resolved by
    invention — no ID is invented, no unhashable value is hashed, and
    the output is never attached to any call or acquired.
    """

    responses: dict[str, list[tuple[int, str, str]]] = {}
    responses_defects: list[ResultDefect] = []
    if input_items is not None:
        for index, item in enumerate(input_items):
            if not isinstance(item, dict) or item.get("type") != "function_call_output":
                continue
            location = f"$.input[{index}]"
            call_id = item["call_id"] if "call_id" in item else None
            if call_id is None or call_id == "":
                responses_defects.append((location, Limitation.MISSING_RESULT_ID))
                continue
            if not isinstance(call_id, str):
                responses_defects.append((location, Limitation.MALFORMED_RESULT_ID))
                continue
            output = item.get("output")
            responses.setdefault(call_id, []).append(
                (index, location, output if isinstance(output, str) else "")
            )

    chat: dict[str, list[tuple[int, str, str]]] = {}
    chat_defects: list[ResultDefect] = []
    if messages is not None:
        for index, message in enumerate(messages):
            if not isinstance(message, dict) or message.get("role") != "tool":
                continue
            location = f"$.messages[{index}]"
            call_id = message["tool_call_id"] if "tool_call_id" in message else None
            if call_id is None or call_id == "":
                chat_defects.append((location, Limitation.MISSING_RESULT_ID))
                continue
            if not isinstance(call_id, str):
                chat_defects.append((location, Limitation.MALFORMED_RESULT_ID))
                continue
            content = message.get("content")
            chat.setdefault(call_id, []).append(
                (index, location, content if isinstance(content, str) else "")
            )
    return responses, responses_defects, chat, chat_defects


def _build_loop_observation(
    *,
    call_id: str,
    endpoint: str,
    call_location: str,
    tool_name: str,
    result_location: str,
    output_text: str,
    loop: LoopParse,
    bounds: ObservationBounds,
) -> ReadObservation:
    """One loop-parsed read observation (grammar ``LOOP_GRAMMAR``).

    Grammar-identity law: the loop parser evaluated the command, so every
    observation it produces carries the actual shared loop grammar
    identity ``LOOP_GRAMMAR`` — the grammar label identifies the parser
    and never changes outcome, completeness, removability or digests.

    Completion law: only a structurally earned loop whose reasons are
    empty (every ``cat`` guarded, no body echo, no member-level
    limitation) plus a wrapper-proven exit-zero, untruncated, present
    output is a complete ordered whole-source bundle — one concatenated
    region with an exact digest, no fabricated internal boundaries or
    member hashes.  A recognized unguarded or labeled loop preserves the
    deterministic requested members but stays non-removable with no
    bundle digest (per-iteration execution and/or outer attribution is
    not proven).  Unknown, nonzero, partial, truncated or missing output
    never yields a whole complete bundle, and no earlier iteration is
    inferred to have succeeded.
    """

    if not loop.complete:
        # Structurally unsupported loop: no acquisition; the original
        # wrapper/global status is preserved as recorded facts.
        return ReadObservation(
            call_id=call_id,
            endpoint=endpoint,
            call_location=call_location,
            result_location=result_location,
            read_grammar=LOOP_GRAMMAR,
            requested_members=loop.requested_members,
            outcome=ReadOutcome.UNSUPPORTED,
            completeness=ReadOutcome.UNSUPPORTED,
            wrapper=parse_wrapper(output_text, bounds),
            reasons=loop.reasons,
        )
    loop_wrapper = parse_wrapper(output_text, bounds)
    loop_content_span = (
        loop_wrapper.output_span
        if loop_wrapper.output_present and loop_wrapper.output_span is not None
        else None
    )
    if Limitation.PROCESS_RUNNING in loop_wrapper.reasons:
        return ReadObservation(
            call_id=call_id,
            endpoint=endpoint,
            call_location=call_location,
            result_location=result_location,
            read_grammar=LOOP_GRAMMAR,
            requested_members=loop.requested_members,
            outcome=ReadOutcome.UNSUPPORTED,
            completeness=ReadOutcome.UNSUPPORTED,
            wrapper=loop_wrapper,
            reasons=(Limitation.PROCESS_RUNNING,),
        )
    if loop_wrapper.reasons == () and loop_wrapper.output_present and loop_content_span is not None:
        loop_content = output_text[loop_content_span.start : loop_content_span.end]
        if contains_lone_surrogates(loop_content):
            # Unhashable content is rejected before any UTF-8 hashing:
            # the observation is typed, non-removable, and carries no
            # digest (ineligible for later graph/cache admission).
            return ReadObservation(
                call_id=call_id,
                endpoint=endpoint,
                call_location=call_location,
                result_location=result_location,
                read_grammar=LOOP_GRAMMAR,
                requested_members=loop.requested_members,
                outcome=ReadOutcome.UNSUPPORTED,
                completeness=ReadOutcome.UNSUPPORTED,
                wrapper=loop_wrapper,
                content_span=loop_content_span,
                removable=False,
                bundle_digest=None,
                member_digests=(),
                reasons=(Limitation.MALFORMED_UNICODE,),
            )
        if loop.reasons == ():
            # An all-success guarded pure-cat loop with a proven
            # exit-zero, untruncated, present output: the attributable
            # content region is ONE ordered whole bundle — one
            # concatenated region with an exact digest, even without
            # inner separators; repeated members preserve observed
            # order, distinct width is recorded, and individual member
            # hashes stay unknown (never fabricated).
            loop_proven = tuple(
                member.normalized
                for member in loop.requested_members
                if member.normalized is not None
            )
            loop_distinct = len(set(loop_proven))
            if len(loop_proven) == 1:
                loop_digest = (
                    EMPTY_SOURCE_SHA256 if loop_content == "" else sha256_hex(loop_content)
                )
                loop_member_digests: tuple[str | None, ...] = (loop_digest,)
            else:
                loop_member_digests = tuple(None for _ in range(loop_distinct))
            return ReadObservation(
                call_id=call_id,
                endpoint=endpoint,
                call_location=call_location,
                result_location=result_location,
                read_grammar=LOOP_GRAMMAR,
                requested_members=loop.requested_members,
                proven_executed=loop_proven,
                distinct_member_count=loop_distinct,
                slot_width=loop_distinct,
                outcome=ReadOutcome.COMPLETE,
                completeness=ReadOutcome.COMPLETE,
                wrapper=loop_wrapper,
                content_span=loop_content_span,
                removable=True,
                bundle_digest=sha256_hex(loop_content),
                member_digests=loop_member_digests,
            )
        # A recognized loop whose per-iteration execution or outer
        # attribution is not proven (an unguarded cat, a body echo, or a
        # member-level limitation): the deterministic requested members
        # are preserved, but the output is not attributable as a pure
        # source bundle — non-removable, no bundle digest.
        return ReadObservation(
            call_id=call_id,
            endpoint=endpoint,
            call_location=call_location,
            result_location=result_location,
            read_grammar=LOOP_GRAMMAR,
            requested_members=loop.requested_members,
            outcome=ReadOutcome.UNSUPPORTED,
            completeness=ReadOutcome.UNSUPPORTED,
            wrapper=loop_wrapper,
            content_span=loop_content_span,
            removable=False,
            reasons=loop.reasons,
        )
    # The wrapper is not proven: the global exit status alone is no
    # per-iteration proof — a nonzero in a guarded loop identifies no
    # failed iteration and proves no earlier source complete; no read
    # is proven and no bundle digest is issued.
    loop_reasons: list[Limitation] = []
    for reason in loop_wrapper.reasons:
        if reason not in loop_reasons:
            loop_reasons.append(reason)
    for reason in loop.reasons:
        if reason not in loop_reasons:
            loop_reasons.append(reason)
    if not loop_reasons:
        loop_reasons.append(Limitation.UNKNOWN_COMPLETION)
    if Limitation.NONZERO_EXIT in loop_wrapper.reasons:
        loop_outcome = ReadOutcome.NONZERO_EXIT
        loop_completeness = ReadOutcome.PARTIAL
    elif Limitation.TRUNCATED_OUTPUT in loop_wrapper.reasons:
        loop_outcome = ReadOutcome.TRUNCATED
        loop_completeness = ReadOutcome.PARTIAL
    elif Limitation.MISSING_OUTPUT_BODY in loop_wrapper.reasons:
        loop_outcome = ReadOutcome.MISSING_BODY
        loop_completeness = ReadOutcome.UNSUPPORTED
    else:
        loop_outcome = ReadOutcome.UNSUPPORTED
        loop_completeness = ReadOutcome.UNSUPPORTED
    return ReadObservation(
        call_id=call_id,
        endpoint=endpoint,
        call_location=call_location,
        result_location=result_location,
        read_grammar=LOOP_GRAMMAR,
        requested_members=loop.requested_members,
        outcome=loop_outcome,
        completeness=loop_completeness,
        wrapper=loop_wrapper,
        content_span=loop_content_span,
        reasons=tuple(loop_reasons),
    )


def _build_observation(
    *,
    call_id: str,
    endpoint: str,
    call_location: str,
    tool_name: str,
    arguments: object,
    result_location: str,
    output_text: str,
    context: PathContext,
    bounds: ObservationBounds,
) -> ReadObservation:
    def _common() -> tuple[str, str, str, str]:
        return call_id, endpoint, call_location, result_location

    if tool_name == _WRITE_STDIN:
        cid, ep, loc, rloc = _common()
        return ReadObservation(
            call_id=cid,
            endpoint=ep,
            call_location=loc,
            result_location=rloc,
            outcome=ReadOutcome.UNSUPPORTED,
            completeness=ReadOutcome.UNSUPPORTED,
            wrapper=parse_wrapper(output_text, bounds),
            reasons=(Limitation.WRITE_STDIN_CHUNK,),
        )

    unwrapped = unwrap_call_arguments(arguments, bounds.max_command_chars)
    if unwrapped is None or (
        unwrapped.workdir is not None and not _workdir_literal(unwrapped.workdir)
    ):
        cid, ep, loc, rloc = _common()
        return ReadObservation(
            call_id=cid,
            endpoint=ep,
            call_location=loc,
            result_location=rloc,
            outcome=ReadOutcome.UNSUPPORTED,
            completeness=ReadOutcome.UNSUPPORTED,
            wrapper=parse_wrapper(output_text, bounds),
            reasons=(Limitation.UNSUPPORTED_TOOL,),
        )

    # A per-call workdir that cannot be encoded as valid UTF-8 (lone
    # surrogates) is typed before any UTF-8 byte check: a fixed
    # non-removable limitation, no placeholder digest, no raw exception
    # echo.  It makes the call's workspace context unproven, so it applies
    # to relative and absolute operand variants alike — the whole call is
    # never resolved elsewhere.
    if unwrapped.workdir is not None and contains_lone_surrogates(unwrapped.workdir):
        cid, ep, loc, rloc = _common()
        return ReadObservation(
            call_id=cid,
            endpoint=ep,
            call_location=loc,
            result_location=rloc,
            outcome=ReadOutcome.UNSUPPORTED,
            completeness=ReadOutcome.UNSUPPORTED,
            wrapper=parse_wrapper(output_text, bounds),
            reasons=(Limitation.MALFORMED_UNICODE,),
        )

    # The explicit per-call workdir (supported argument object) takes
    # precedence over the batch default before any relative operand is
    # resolved; it is validated against the evidenced workspace and never
    # falls back to the batch context when invalid.
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
    if not parsed.complete:
        # Finite read-plan surface (D06/D07/D08): recognized all-cat /
        # literal-cd (plus bounded literal-echo outer boundaries) '&&'
        # plans.  The plan is parsed as data — never executed; per-command
        # exit metadata is never invented or inferred from source-looking
        # text after Output.
        #
        # Grammar-identity fallback law: the single-command grammar is the
        # primary grammar; a command it does not complete is evaluated by
        # the finite-plan parser, and EVERY observation that parser
        # produces — complete, unsupported, nonzero, missing/truncated/
        # running, malformed-content or outer-boundary-unproven — carries
        # the plan grammar ``READ_PLAN_GRAMMAR``.  An observation the
        # single grammar actually earned (below) keeps ``READ_GRAMMAR``.
        # The grammar label identifies the parser that evaluated the
        # command; it never changes outcome, completeness, removability or
        # digests, and an unsupported attempt is never a successful plan.
        plan = parse_read_plan(
            unwrapped.command,
            call_context,
            bounds.max_command_chars,
            bounds.max_operands,
            bounds.max_path_bytes,
        )
        if not plan.complete:
            # Finite literal-loop surface (D07): a loop command is
            # evaluated by the loop parser, and EVERY observation that
            # parser produces — complete, unsupported, nonzero,
            # missing/truncated/running, malformed-content or
            # iteration/outer-boundary-unproven — carries the actual
            # shared loop grammar identity ``LOOP_GRAMMAR``.  A command
            # outside the loop parser's domain keeps the typed
            # unsupported plan observation (plan grammar) above.
            loop = parse_literal_loop(
                unwrapped.command,
                call_context,
                bounds.max_command_chars,
                bounds.max_operands,
                bounds.max_path_bytes,
            )
            if loop.is_loop_attempt:
                return _build_loop_observation(
                    call_id=call_id,
                    endpoint=endpoint,
                    call_location=call_location,
                    tool_name=tool_name,
                    result_location=result_location,
                    output_text=output_text,
                    loop=loop,
                    bounds=bounds,
                )
            # Typed unsupported plan: no acquisition; the original
            # wrapper/global status is preserved as recorded facts.
            cid, ep, loc, rloc = _common()
            return ReadObservation(
                call_id=cid,
                endpoint=ep,
                call_location=loc,
                result_location=rloc,
                read_grammar=READ_PLAN_GRAMMAR,
                requested_members=plan.requested_members,
                outcome=ReadOutcome.UNSUPPORTED,
                completeness=ReadOutcome.UNSUPPORTED,
                wrapper=parse_wrapper(output_text, bounds),
                reasons=plan.reasons,
            )
        plan_wrapper = parse_wrapper(output_text, bounds)
        plan_content_span = (
            plan_wrapper.output_span
            if plan_wrapper.output_present and plan_wrapper.output_span is not None
            else None
        )
        if Limitation.PROCESS_RUNNING in plan_wrapper.reasons:
            cid, ep, loc, rloc = _common()
            return ReadObservation(
                call_id=cid,
                endpoint=ep,
                call_location=loc,
                result_location=rloc,
                read_grammar=READ_PLAN_GRAMMAR,
                requested_members=plan.requested_members,
                outcome=ReadOutcome.UNSUPPORTED,
                completeness=ReadOutcome.UNSUPPORTED,
                wrapper=plan_wrapper,
                reasons=(Limitation.PROCESS_RUNNING,),
            )
        if (
            plan_wrapper.reasons == ()
            and plan_wrapper.output_present
            and plan_content_span is not None
        ):
            plan_content = output_text[plan_content_span.start : plan_content_span.end]
            if contains_lone_surrogates(plan_content):
                # Unhashable content is rejected before any UTF-8 hashing:
                # the observation is typed, non-removable, and carries no
                # digest (ineligible for later graph/cache admission).
                cid, ep, loc, rloc = _common()
                return ReadObservation(
                    call_id=cid,
                    endpoint=ep,
                    call_location=loc,
                    result_location=rloc,
                    read_grammar=READ_PLAN_GRAMMAR,
                    requested_members=plan.requested_members,
                    outcome=ReadOutcome.UNSUPPORTED,
                    completeness=ReadOutcome.UNSUPPORTED,
                    wrapper=plan_wrapper,
                    content_span=plan_content_span,
                    removable=False,
                    bundle_digest=None,
                    member_digests=(),
                    reasons=(Limitation.MALFORMED_UNICODE,),
                )
            region, region_reasons = plan_source_region(plan, plan_content)
            if region is not None:
                # A proven exit-zero, untruncated, present output proves
                # each requested read succeeded: the attributable content
                # region is ONE ordered whole bundle, even without inner
                # separators; repeated operands preserve observed order,
                # distinct width is recorded, and individual member hashes
                # stay unknown (never fabricated).
                plan_proven = tuple(
                    member.normalized
                    for member in plan.requested_members
                    if member.normalized is not None
                )
                source = plan_content[region.start : region.end]
                plan_distinct = len(set(plan_proven))
                if len(plan_proven) == 1:
                    plan_digest = EMPTY_SOURCE_SHA256 if source == "" else sha256_hex(source)
                    plan_member_digests: tuple[str | None, ...] = (plan_digest,)
                else:
                    plan_member_digests = tuple(None for _ in range(plan_distinct))
                cid, ep, loc, rloc = _common()
                return ReadObservation(
                    call_id=cid,
                    endpoint=ep,
                    call_location=loc,
                    result_location=rloc,
                    read_grammar=READ_PLAN_GRAMMAR,
                    requested_members=plan.requested_members,
                    proven_executed=plan_proven,
                    distinct_member_count=plan_distinct,
                    slot_width=plan_distinct,
                    outcome=ReadOutcome.COMPLETE,
                    completeness=ReadOutcome.COMPLETE,
                    wrapper=plan_wrapper,
                    content_span=CharSpan(
                        start=plan_content_span.start + region.start,
                        end=plan_content_span.start + region.end,
                    ),
                    removable=True,
                    bundle_digest=sha256_hex(source),
                    member_digests=plan_member_digests,
                )
            # A complete plan whose output boundary cannot be proven
            # (collision, unknown internal boundary or extra output):
            # typed, non-removable, and no digest is issued.
            cid, ep, loc, rloc = _common()
            return ReadObservation(
                call_id=cid,
                endpoint=ep,
                call_location=loc,
                result_location=rloc,
                read_grammar=READ_PLAN_GRAMMAR,
                requested_members=plan.requested_members,
                outcome=ReadOutcome.UNSUPPORTED,
                completeness=ReadOutcome.UNSUPPORTED,
                wrapper=plan_wrapper,
                content_span=plan_content_span,
                removable=False,
                reasons=region_reasons,
            )
        # The wrapper is not proven: the global exit status alone is no
        # per-command proof — a nonzero in an '&&' chain identifies no
        # per-read failure and proves no earlier source complete; no read
        # is proven and no bundle digest is issued.
        plan_reasons: list[Limitation] = []
        for reason in plan_wrapper.reasons:
            if reason not in plan_reasons:
                plan_reasons.append(reason)
        if not plan_reasons:
            plan_reasons.append(Limitation.UNKNOWN_COMPLETION)
        if Limitation.NONZERO_EXIT in plan_wrapper.reasons:
            plan_outcome = ReadOutcome.NONZERO_EXIT
            plan_completeness = ReadOutcome.PARTIAL
        elif Limitation.TRUNCATED_OUTPUT in plan_wrapper.reasons:
            plan_outcome = ReadOutcome.TRUNCATED
            plan_completeness = ReadOutcome.PARTIAL
        elif Limitation.MISSING_OUTPUT_BODY in plan_wrapper.reasons:
            plan_outcome = ReadOutcome.MISSING_BODY
            plan_completeness = ReadOutcome.UNSUPPORTED
        else:
            plan_outcome = ReadOutcome.UNSUPPORTED
            plan_completeness = ReadOutcome.UNSUPPORTED
        cid, ep, loc, rloc = _common()
        return ReadObservation(
            call_id=cid,
            endpoint=ep,
            call_location=loc,
            result_location=rloc,
            read_grammar=READ_PLAN_GRAMMAR,
            requested_members=plan.requested_members,
            outcome=plan_outcome,
            completeness=plan_completeness,
            wrapper=plan_wrapper,
            content_span=plan_content_span,
            reasons=tuple(plan_reasons),
        )

    wrapper = parse_wrapper(output_text, bounds)
    content_span = (
        wrapper.output_span if wrapper.output_present and wrapper.output_span is not None else None
    )
    if Limitation.PROCESS_RUNNING in wrapper.reasons:
        cid, ep, loc, rloc = _common()
        return ReadObservation(
            call_id=cid,
            endpoint=ep,
            call_location=loc,
            result_location=rloc,
            requested_members=parsed.operands,
            outcome=ReadOutcome.UNSUPPORTED,
            completeness=ReadOutcome.UNSUPPORTED,
            wrapper=wrapper,
            reasons=(Limitation.PROCESS_RUNNING,),
        )

    reasons: list[Limitation] = []
    content = ""
    if content_span is not None:
        content = output_text[content_span.start : content_span.end]

    normalized = [o.normalized for o in parsed.operands]
    valid_normalized = [p for p in normalized if p is not None]

    outcome = ReadOutcome.UNSUPPORTED
    completeness = ReadOutcome.UNSUPPORTED
    proven: tuple[str, ...] = ()
    distinct: int | None = None
    bundle_digest: str | None = None
    member_digests: tuple[str | None, ...] = ()
    removable = False

    if wrapper.reasons == () and wrapper.output_present and content_span is not None:
        if contains_lone_surrogates(content):
            # Unhashable content is rejected before any UTF-8 hashing: the
            # observation is typed, non-removable, and carries no digest
            # (ineligible for later graph/cache admission).
            cid, ep, loc, rloc = _common()
            return ReadObservation(
                call_id=cid,
                endpoint=ep,
                call_location=loc,
                result_location=rloc,
                requested_members=parsed.operands,
                outcome=ReadOutcome.UNSUPPORTED,
                completeness=ReadOutcome.UNSUPPORTED,
                wrapper=wrapper,
                content_span=content_span,
                removable=False,
                bundle_digest=None,
                member_digests=(),
                reasons=(Limitation.MALFORMED_UNICODE,),
            )
        # Wrapper proves exit zero, no truncation marker, exact body present:
        # the content region is the complete attributable source.
        removable = True
        proven = tuple(valid_normalized)
        bundle_digest = sha256_hex(content)
        if len(valid_normalized) == 1:
            # Exactly one operand: the whole body is that one file, so the
            # member boundary and digest are proven (a zero-byte body is a
            # complete empty version with the exact empty digest).
            outcome = ReadOutcome.COMPLETE
            completeness = ReadOutcome.COMPLETE
            distinct = 1
            digest = EMPTY_SOURCE_SHA256 if content == "" else sha256_hex(content)
            member_digests = (digest,)
        else:
            # One ordered whole bundle; repeated operands preserve observed
            # order, distinct-member width is recorded separately, and
            # individual member boundaries/digests stay unknown (never
            # fabricated).
            outcome = ReadOutcome.COMPLETE
            completeness = ReadOutcome.COMPLETE
            distinct = len(set(valid_normalized))
            member_digests = tuple(None for _ in range(distinct))
    else:
        # The wrapper is not proven complete: propagate its typed reason(s)
        # at the read level (fall back to unknown completion only when the
        # wrapper already carries that reason or none at all).
        for reason in wrapper.reasons:
            if reason not in reasons:
                reasons.append(reason)
        if not reasons:
            reasons.append(Limitation.UNKNOWN_COMPLETION)
        if Limitation.NONZERO_EXIT in wrapper.reasons:
            outcome = ReadOutcome.NONZERO_EXIT
            completeness = ReadOutcome.PARTIAL
        elif Limitation.TRUNCATED_OUTPUT in wrapper.reasons:
            outcome = ReadOutcome.TRUNCATED
            completeness = ReadOutcome.PARTIAL
        elif Limitation.MISSING_OUTPUT_BODY in wrapper.reasons:
            outcome = ReadOutcome.MISSING_BODY
            completeness = ReadOutcome.UNSUPPORTED

    cid, ep, loc, rloc = _common()
    return ReadObservation(
        call_id=cid,
        endpoint=ep,
        call_location=loc,
        result_location=rloc,
        requested_members=parsed.operands,
        proven_executed=proven,
        distinct_member_count=distinct,
        slot_width=distinct,
        outcome=outcome,
        completeness=completeness,
        wrapper=wrapper,
        content_span=content_span,
        removable=removable,
        bundle_digest=bundle_digest,
        member_digests=member_digests,
        reasons=tuple(reasons),
    )


#: One planned pairing container: endpoint name, eligible calls, the
#: full schema-evidenced call inventory, and results by ID.
PlanEndpoint = tuple[
    str,
    list[EligibleCall],
    list[CallRecord],
    dict[str, list[tuple[int, str, str]]],
    list[ResultDefect],
]


def _pair_endpoint(
    endpoint: str,
    calls: list[EligibleCall],
    records: list[CallRecord],
    outputs: dict[str, list[tuple[int, str, str]]],
    defects: list[ResultDefect],
    context: PathContext,
    bounds: ObservationBounds,
    suppress_acquisition: bool = False,
) -> tuple[list[ReadObservation], list[UnpairedRecord]]:
    """Pair one endpoint's eligible calls with its own results by call ID.

    Identity-conflict law: duplicate/missing/mismatched bookkeeping is
    computed from the **full schema-evidenced call inventory** — every
    call record with a valid non-empty string ID, regardless of tool
    support **or wire family** (a Responses ``custom_tool_call``
    colliding with an eligible call ID makes the ambiguous chain
    typed/non-acquiring) — so a collision with an eligible call ID
    cannot disappear through eligibility filtering.  Acquisition stays
    restricted to eligible calls: an unknown/ineligible call never
    acquires a source, and an unrelated unknown or opaque custom call
    with a unique ID is neither recorded nor allowed to poison a
    separate valid chain.  Missing, empty or non-string call IDs are
    observable typed conflicts that never pair and never invent an ID.
    Typed result-ID defects (``MISSING_RESULT_ID`` /
    ``MALFORMED_RESULT_ID``) are emitted as bounded non-echoing unpaired
    records in structural order; they never pair, never acquire and
    never echo the offending value.

    Causality law: a result attaches to its matching call only when its
    exact numeric structural position follows the call's.  A pre-call
    result keeps its chain typed and non-removable (no bundle/member
    digest, no source span, no proven-executed claim); it is never
    attached to a future call.  Presentation order (sorted IDs) is
    separate from, and never used to establish, causality.

    Under ``suppress_acquisition`` (mixed envelope without explicit
    endpoint context) pairing bookkeeping — including cross-endpoint ID
    typing — is preserved, but no read is ever acquired: every
    observation is typed ``ENDPOINT_UNSUPPORTED`` with no proven
    members, no span, no digest and no removability.
    """

    calls_by_id: dict[str, list[EligibleCall]] = {}
    for call in calls:
        calls_by_id.setdefault(call[0], []).append(call)

    records_by_id: dict[str, list[CallRecord]] = {}
    for record in records:
        raw_id = record[3]
        if isinstance(raw_id, str) and raw_id:
            records_by_id.setdefault(raw_id, []).append(record)

    observations: list[ReadObservation] = []
    unpaired: list[UnpairedRecord] = []

    # Missing (absent key, JSON null or empty string) or malformed
    # (present but not a string) call IDs remain observable and never
    # pair: no ID is invented, no content is acquired.
    for _wire_family, _position, location, raw_id, _raw_name, _arguments in records:
        if raw_id is None or raw_id == "":
            unpaired.append(
                UnpairedRecord(
                    location=location,
                    call_id="",
                    limitation=Limitation.MISSING_CALL_ID,
                )
            )
        elif not isinstance(raw_id, str):
            unpaired.append(
                UnpairedRecord(
                    location=location,
                    call_id="",
                    limitation=Limitation.MALFORMED_CALL_ID,
                )
            )

    # Typed result-ID defects: observable, non-echoing, never paired and
    # never acquired (the offending value is never stored or echoed).
    for location, limitation in defects:
        unpaired.append(
            UnpairedRecord(
                location=location,
                call_id="",
                limitation=limitation,
            )
        )

    for call_id in sorted(calls_by_id):
        paired_calls = calls_by_id[call_id]
        colliding_records = records_by_id.get(call_id, [])
        if len(colliding_records) > 1:
            # Identity conflict across ANY schema-evidenced records
            # (supported, unsupported or mixed families): every
            # occurrence is observed, none acquires.
            for (
                _wire_family,
                _position,
                location,
                _raw_id,
                _raw_name,
                _arguments,
            ) in colliding_records:
                unpaired.append(
                    UnpairedRecord(
                        location=location,
                        call_id=call_id,
                        limitation=Limitation.DUPLICATE_CALL_ID,
                    )
                )
            continue
        _cid, call_position, location, name, arguments = paired_calls[0]
        results = outputs.get(call_id, [])
        if not results:
            unpaired.append(
                UnpairedRecord(
                    location=location,
                    call_id=call_id,
                    limitation=Limitation.MISSING_CALL_RESULT,
                )
            )
            continue
        if len(results) > 1:
            # Duplicate same-call results stay unsupported absent later
            # earned process-chain evidence (D09, deferred).
            for _rposition, rlocation, _text in results:
                unpaired.append(
                    UnpairedRecord(
                        location=rlocation,
                        call_id=call_id,
                        limitation=Limitation.MULTI_CHUNK_DEFERRED,
                    )
                )
            continue
        result_position, result_location, output_text = results[0]
        observation = _build_observation(
            call_id=call_id,
            endpoint=endpoint,
            call_location=location,
            tool_name=name,
            arguments=arguments,
            result_location=result_location,
            output_text=output_text,
            context=context,
            bounds=bounds,
        )
        if result_position <= call_position:
            # Causality: the result does not follow its matching call in
            # structural order.  The chain stays typed and
            # non-removable — no bundle/member digest, no source span,
            # no proven-executed claim — and is never attached to a
            # future call.
            observation = observation.model_copy(
                update={
                    "outcome": ReadOutcome.UNSUPPORTED,
                    "completeness": ReadOutcome.UNSUPPORTED,
                    "proven_executed": (),
                    "distinct_member_count": None,
                    "slot_width": None,
                    "content_span": None,
                    "removable": False,
                    "bundle_digest": None,
                    "member_digests": (),
                    "reasons": (Limitation.PRE_CALL_RESULT,)
                    + tuple(r for r in observation.reasons if r is not Limitation.PRE_CALL_RESULT),
                }
            )
        if suppress_acquisition:
            # The envelope is typed unsupported: the call evidence (ID,
            # locations, requested members, wrapper facts) is preserved,
            # but nothing is acquired from either container.
            observation = observation.model_copy(
                update={
                    "outcome": ReadOutcome.UNSUPPORTED,
                    "completeness": ReadOutcome.UNSUPPORTED,
                    "proven_executed": (),
                    "distinct_member_count": None,
                    "slot_width": None,
                    "content_span": None,
                    "removable": False,
                    "bundle_digest": None,
                    "member_digests": (),
                    "reasons": (Limitation.ENDPOINT_UNSUPPORTED,),
                }
            )
        observations.append(observation)

    for call_id in sorted(outputs):
        if call_id in calls_by_id:
            continue
        for _position, location, _text in outputs[call_id]:
            unpaired.append(
                UnpairedRecord(
                    location=location,
                    call_id=call_id,
                    limitation=Limitation.MISMATCHED_CALL_ID,
                )
            )
    return observations, unpaired


def observe_reads(
    payload: dict[str, Any],
    context: PathContext,
    bounds: ObservationBounds,
    selected_endpoint: str | None = None,
    suppress_acquisition: bool = False,
) -> tuple[tuple[ReadObservation, ...], tuple[UnpairedRecord, ...]]:
    """Pair supported calls with results by exact call ID (D05).

    Pairing is endpoint-scoped: a Responses call pairs only with
    Responses results and a Chat call only with Chat results — a
    cross-endpoint ID match is typed (missing/mismatched), never mixed
    evidence.  Identity-conflict bookkeeping uses the full
    schema-evidenced call inventory (eligibility- and family-
    independent); result causality uses exact numeric structural
    positions.

    Complete-inventory bound law: ``max_commands`` is enforced against
    **all** relevant schema-position call records (supported,
    unsupported, opaque ``custom_tool_call`` and missing/empty/malformed
    IDs) and ``max_outputs`` against **all** relevant result records
    (including invalid IDs), before any identity map or typed
    diagnostic is retained or built.  Over-bound input yields the fixed
    non-acquiring ``OVER_BOUND`` record — never a truncated inventory
    from which an earlier chain acquires while a later collision is
    missed.  The scan itself is bounded by the existing ``max_items``
    item bound before any record is retained.  For explicit endpoint
    selection only the selected domain is inspected and contributes;
    the mixed and legacy no-selection shapes inspect both present
    containers (bounded across the inspected domains).

    ``selected_endpoint`` scopes observation to one container (an
    explicit validated endpoint or an unambiguously inferred envelope);
    the other container is never acquired.  ``suppress_acquisition``
    (mixed envelope without explicit context) keeps pairing bookkeeping
    but acquires nothing from either container (typed
    ``ENDPOINT_UNSUPPORTED``).
    """

    input_items = payload.get("input")
    input_items = input_items if isinstance(input_items, list) else None
    messages = payload.get("messages")
    messages = messages if isinstance(messages, list) else None

    # Scope the inspected containers to the selected domain(s): an
    # explicit endpoint contributes its own domain only; the other
    # container is neither scanned nor counted.
    if selected_endpoint == "responses":
        resp_items, chat_msgs = input_items, None
    elif selected_endpoint == "chat":
        resp_items, chat_msgs = None, messages
    else:
        resp_items, chat_msgs = input_items, messages

    # The complete-inventory scan is bounded by the existing item bound
    # before any record is retained: an over-long inspected container is
    # a fixed non-acquiring OVER_BOUND.
    if (resp_items is not None and len(resp_items) > bounds.max_items) or (
        chat_msgs is not None and len(chat_msgs) > bounds.max_items
    ):
        return (
            (),
            (UnpairedRecord(location="$", call_id="", limitation=Limitation.OVER_BOUND),),
        )

    responses_records, chat_records = _call_records(resp_items, chat_msgs)
    (
        responses_outputs,
        responses_defects,
        chat_outputs,
        chat_defects,
    ) = _result_entries(resp_items, chat_msgs)

    # The bounds are decided on the complete relevant inventory (every
    # schema-position call record, every result record including ID
    # defects) before any identity map or diagnostic is built.
    command_total = len(responses_records) + len(chat_records)
    output_total = (
        sum(len(v) for v in responses_outputs.values())
        + len(responses_defects)
        + sum(len(v) for v in chat_outputs.values())
        + len(chat_defects)
    )
    if command_total > bounds.max_commands or output_total > bounds.max_outputs:
        return (
            (),
            (UnpairedRecord(location="$", call_id="", limitation=Limitation.OVER_BOUND),),
        )

    responses_calls, chat_calls = _call_entries(payload, bounds, responses_records, chat_records)

    plan: tuple[PlanEndpoint, ...]
    if selected_endpoint == "responses":
        plan = (
            (
                "responses",
                responses_calls,
                responses_records,
                responses_outputs,
                responses_defects,
            ),
        )
    elif selected_endpoint == "chat":
        plan = (
            (
                "chat",
                chat_calls,
                chat_records,
                chat_outputs,
                chat_defects,
            ),
        )
    else:
        # No selected domain (legacy direct callers): both containers.
        plan = (
            (
                "responses",
                responses_calls,
                responses_records,
                responses_outputs,
                responses_defects,
            ),
            (
                "chat",
                chat_calls,
                chat_records,
                chat_outputs,
                chat_defects,
            ),
        )

    observations: list[ReadObservation] = []
    unpaired: list[UnpairedRecord] = []
    for endpoint, calls, records, outputs, defects in plan:
        endpoint_observations, endpoint_unpaired = _pair_endpoint(
            endpoint, calls, records, outputs, defects, context, bounds, suppress_acquisition
        )
        observations.extend(endpoint_observations)
        unpaired.extend(endpoint_unpaired)
    return tuple(observations), tuple(unpaired)

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
exec tool; suffix or substring resemblance is never evidence.  Duplicate or
missing call IDs are typed conflicts, never first-match selection.
Multi-chunk results and process-running/write_stdin traffic are explicitly
deferred in this slice (typed unsupported, D09 territory).

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


def _call_entries(
    payload: dict[str, Any], bounds: ObservationBounds
) -> tuple[list[tuple[str, str, str, object]], list[tuple[str, str, str, object]]]:
    """Collect eligible calls per endpoint.

    Returns ``(responses_calls, chat_calls)`` as
    ``(call_id, location, tool_name, arguments)`` tuples: Responses calls
    from the ``input`` array, Chat calls from ``messages`` assistant
    ``tool_calls``.  Endpoints never mix.
    """

    def _eligible(name: Any) -> bool:
        if not isinstance(name, str) or not name:
            return False
        return _eligible_tool_name(name, payload, bounds)

    responses_calls: list[tuple[str, str, str, object]] = []
    input_items = payload.get("input")
    if isinstance(input_items, list):
        for index, item in enumerate(input_items):
            if not isinstance(item, dict) or item.get("type") != "function_call":
                continue
            call_id = item.get("call_id")
            name = item.get("name")
            arguments = item.get("arguments")
            if not isinstance(call_id, str) or not call_id:
                continue
            if not _eligible(name):
                continue
            responses_calls.append((call_id, f"$.input[{index}]", str(name), arguments))

    chat_calls: list[tuple[str, str, str, object]] = []
    messages = payload.get("messages")
    if isinstance(messages, list):
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
                if not isinstance(function, dict):
                    continue
                name = function.get("name")
                call_id = tool.get("id")
                arguments = function.get("arguments")
                if not isinstance(call_id, str) or not call_id:
                    continue
                if not _eligible(name):
                    continue
                chat_calls.append(
                    (call_id, f"$.messages[{index}].tool_calls[{tool_index}]", str(name), arguments)
                )
    return responses_calls, chat_calls


def _result_entries(
    payload: dict[str, Any],
) -> tuple[dict[str, list[tuple[str, str]]], dict[str, list[tuple[str, str]]]]:
    """Collect results by call ID per endpoint: ``{call_id: [(location, text)]}``."""

    responses: dict[str, list[tuple[str, str]]] = {}
    input_items = payload.get("input")
    if isinstance(input_items, list):
        for index, item in enumerate(input_items):
            if not isinstance(item, dict) or item.get("type") != "function_call_output":
                continue
            call_id = item.get("call_id")
            output = item.get("output")
            if not isinstance(call_id, str) or not call_id:
                continue
            responses.setdefault(call_id, []).append(
                (f"$.input[{index}]", output if isinstance(output, str) else "")
            )

    chat: dict[str, list[tuple[str, str]]] = {}
    messages = payload.get("messages")
    if isinstance(messages, list):
        for index, message in enumerate(messages):
            if not isinstance(message, dict) or message.get("role") != "tool":
                continue
            call_id = message.get("tool_call_id")
            content = message.get("content")
            if not isinstance(call_id, str) or not call_id:
                continue
            chat.setdefault(call_id, []).append(
                (f"$.messages[{index}]", content if isinstance(content, str) else "")
            )
    return responses, chat


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
        cid, ep, loc, rloc = _common()
        return ReadObservation(
            call_id=cid,
            endpoint=ep,
            call_location=loc,
            result_location=rloc,
            requested_members=parsed.operands,
            outcome=ReadOutcome.UNSUPPORTED,
            completeness=ReadOutcome.UNSUPPORTED,
            wrapper=parse_wrapper(output_text, bounds),
            reasons=parsed.reasons,
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


#: One planned pairing container: endpoint name, eligible calls, results.
PlanEndpoint = tuple[str, list[tuple[str, str, str, object]], dict[str, list[tuple[str, str]]]]


def _pair_endpoint(
    endpoint: str,
    calls: list[tuple[str, str, str, object]],
    outputs: dict[str, list[tuple[str, str]]],
    context: PathContext,
    bounds: ObservationBounds,
    suppress_acquisition: bool = False,
) -> tuple[list[ReadObservation], list[UnpairedRecord]]:
    """Pair one endpoint's eligible calls with its own results by call ID.

    Under ``suppress_acquisition`` (mixed envelope without explicit
    endpoint context) pairing bookkeeping — including cross-endpoint ID
    typing — is preserved, but no read is ever acquired: every observation
    is typed ``ENDPOINT_UNSUPPORTED`` with no proven members, no span, no
    digest and no removability.
    """

    calls_by_id: dict[str, list[tuple[str, str, str, object]]] = {}
    for call in calls:
        calls_by_id.setdefault(call[0], []).append(call)

    observations: list[ReadObservation] = []
    unpaired: list[UnpairedRecord] = []

    for call_id in sorted(calls_by_id):
        paired_calls = calls_by_id[call_id]
        if len(paired_calls) > 1:
            for _cid, location, _name, _args in paired_calls:
                unpaired.append(
                    UnpairedRecord(
                        location=location,
                        call_id=call_id,
                        limitation=Limitation.DUPLICATE_CALL_ID,
                    )
                )
            continue
        _cid, location, name, arguments = paired_calls[0]
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
            for rlocation, _text in results:
                unpaired.append(
                    UnpairedRecord(
                        location=rlocation,
                        call_id=call_id,
                        limitation=Limitation.MULTI_CHUNK_DEFERRED,
                    )
                )
            continue
        result_location, output_text = results[0]
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
        for location, _text in outputs[call_id]:
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

    Pairing is endpoint-scoped: a Responses call pairs only with Responses
    results and a Chat call only with Chat results — a cross-endpoint ID
    match is typed (missing/mismatched), never mixed evidence.

    ``selected_endpoint`` scopes observation to one container (an explicit
    validated endpoint or an unambiguously inferred envelope); the other
    container is never acquired.  ``suppress_acquisition`` (mixed envelope
    without explicit context) keeps pairing bookkeeping but acquires
    nothing from either container (typed ``ENDPOINT_UNSUPPORTED``).
    """

    responses_calls, chat_calls = _call_entries(payload, bounds)
    responses_outputs, chat_outputs = _result_entries(payload)
    over_commands = len(responses_calls) + len(chat_calls) > bounds.max_commands
    over_outputs = (
        sum(len(v) for v in responses_outputs.values()) + sum(len(v) for v in chat_outputs.values())
        > bounds.max_outputs
    )
    if over_commands or over_outputs:
        return (
            (),
            (UnpairedRecord(location="$", call_id="", limitation=Limitation.OVER_BOUND),),
        )

    plan: tuple[PlanEndpoint, ...]
    if selected_endpoint == "responses":
        plan = (("responses", responses_calls, responses_outputs),)
    elif selected_endpoint == "chat":
        plan = (("chat", chat_calls, chat_outputs),)
    else:
        # No selected domain (legacy direct callers): both containers.
        plan = (
            ("responses", responses_calls, responses_outputs),
            ("chat", chat_calls, chat_outputs),
        )

    observations: list[ReadObservation] = []
    unpaired: list[UnpairedRecord] = []
    for endpoint, calls, outputs in plan:
        endpoint_observations, endpoint_unpaired = _pair_endpoint(
            endpoint, calls, outputs, context, bounds, suppress_acquisition
        )
        observations.extend(endpoint_observations)
        unpaired.extend(endpoint_unpaired)
    return tuple(observations), tuple(unpaired)

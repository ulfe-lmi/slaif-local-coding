"""Supported tool call/result pairing and exec-wrapper parsing (D05).

Pairing law: a call and its result pair by **exact call ID**.  Only supported
tool names are eligible; namespace-qualified names need explicit
supported-envelope evidence (the request's own ``tools`` array declaring the
exact name with a string ``cmd`` parameter) — never a suffix-name guess.
Duplicate or missing call IDs are typed conflicts, never first-match
selection.  Multi-chunk results and process-running/write_stdin traffic are
explicitly deferred in this slice (typed unsupported, D09 territory).

Wrapper law: the observed Codex exec wrapper carries its metadata **before**
the ``Output:`` line; everything after that line is source, and source that
merely looks like execution metadata never redefines wrapper status.  A
proven empty successful output (wrapper exit zero, ``Output:`` present, zero
content bytes) is a complete empty version; a missing body is a different,
explicit state.
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
    sha256_hex,
)
from ..bundles.read_grammar import parse_read_command, unwrap_supported_arguments

_SUPPORTED_TOOL_NAMES = frozenset({"exec_command", "shell_command"})
_WRITE_STDIN = "write_stdin"
_OUTPUT_MARKER = "Output:"
_RUNNING_MARKER = "Process is still running"


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
    """Explicit supported-envelope evidence for a non-bare tool name.

    The request's own ``tools`` array must declare the exact name with a
    ``cmd`` string parameter (the observed Codex exec schema).  Suffix or
    substring resemblance is never evidence.
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


def parse_wrapper(output: str, bounds: ObservationBounds) -> WrapperFacts:
    """Parse exec-wrapper metadata from one result body (versioned format).

    The header is a bounded block of recognized lines before the ``Output:``
    marker line, which itself must be newline-terminated.  Everything after
    the marker line is the exact source region.  Plain unstructured output is
    unknown completion, never complete; process-running bodies are typed.
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
    truncation = TruncationStatus.UNKNOWN
    saw_header = False
    index = 0
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
        if line.startswith("Chunk Id: ") or line.startswith("Wall time: "):
            value = line.split(": ", 1)[1]
            if value and len(value) <= 128:
                saw_header = True
                matched = True
        elif line.startswith("Process exited with code "):
            value = line[len("Process exited with code ") :]
            digits = value.lstrip("-")
            if digits != "" and digits.isdigit() and value.startswith("-") is False:
                code = int(value)
                if 0 <= code <= 255:
                    exit_status = ExitStatus.ZERO if code == 0 else ExitStatus.NONZERO
                    exit_code = code
                    saw_header = True
                    matched = True
        elif line.startswith("Truncated: "):
            value = line.split(": ", 1)[1]
            if value == "true":
                truncation = TruncationStatus.TRUE
                saw_header = True
                matched = True
            elif value == "false":
                truncation = TruncationStatus.FALSE
                saw_header = True
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


def _call_entries(
    payload: dict[str, Any], bounds: ObservationBounds
) -> list[tuple[str, str, str, object]]:
    """Collect eligible calls: (call_id, location, tool_name, arguments)."""

    declared = _declared_tool_names(payload, bounds)

    def _eligible(name: Any) -> bool:
        if not isinstance(name, str) or not name:
            return False
        if name in _SUPPORTED_TOOL_NAMES or name == _WRITE_STDIN:
            return True
        # Namespace-qualified: explicit envelope evidence only, no suffix guess.
        return name in declared and _envelope_proves_executable(payload, name, bounds)

    calls: list[tuple[str, str, str, object]] = []
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
            if not isinstance(name, str) or not _eligible(name):
                continue
            calls.append((call_id, f"$.input[{index}]", name, arguments))

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
                if not isinstance(name, str) or not _eligible(name):
                    continue
                calls.append(
                    (
                        call_id,
                        f"$.messages[{index}].tool_calls[{tool_index}]",
                        name,
                        arguments,
                    )
                )
    return calls


def _result_entries(payload: dict[str, Any]) -> dict[str, list[tuple[str, str, str]]]:
    """Collect results by call ID: (location, endpoint, output_text) lists."""

    outputs: dict[str, list[tuple[str, str, str]]] = {}
    input_items = payload.get("input")
    if isinstance(input_items, list):
        for index, item in enumerate(input_items):
            if not isinstance(item, dict) or item.get("type") != "function_call_output":
                continue
            call_id = item.get("call_id")
            output = item.get("output")
            if not isinstance(call_id, str) or not call_id:
                continue
            outputs.setdefault(call_id, []).append(
                (f"$.input[{index}]", "responses", output if isinstance(output, str) else "")
            )
    messages = payload.get("messages")
    if isinstance(messages, list):
        for index, message in enumerate(messages):
            if not isinstance(message, dict) or message.get("role") != "tool":
                continue
            call_id = message.get("tool_call_id")
            content = message.get("content")
            if not isinstance(call_id, str) or not call_id:
                continue
            outputs.setdefault(call_id, []).append(
                (f"$.messages[{index}]", "chat", content if isinstance(content, str) else "")
            )
    return outputs


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

    command = unwrap_supported_arguments(arguments)
    if command is None:
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
    parsed = parse_read_command(
        command,
        context,
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
    elif Limitation.NONZERO_EXIT in wrapper.reasons:
        outcome = ReadOutcome.NONZERO_EXIT
        completeness = ReadOutcome.PARTIAL
        reasons.append(Limitation.NONZERO_EXIT)
    elif Limitation.TRUNCATED_OUTPUT in wrapper.reasons:
        outcome = ReadOutcome.TRUNCATED
        completeness = ReadOutcome.PARTIAL
        reasons.append(Limitation.TRUNCATED_OUTPUT)
    elif Limitation.MISSING_OUTPUT_BODY in wrapper.reasons:
        outcome = ReadOutcome.MISSING_BODY
        completeness = ReadOutcome.UNSUPPORTED
        reasons.append(Limitation.MISSING_OUTPUT_BODY)
    elif wrapper.output_present:
        reasons.append(Limitation.UNKNOWN_COMPLETION)
    else:
        reasons.append(Limitation.UNKNOWN_COMPLETION)

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


def observe_reads(
    payload: dict[str, Any],
    context: PathContext,
    bounds: ObservationBounds,
) -> tuple[tuple[ReadObservation, ...], tuple[UnpairedRecord, ...]]:
    """Pair supported calls with results by exact call ID (D05)."""

    calls = _call_entries(payload, bounds)
    outputs = _result_entries(payload)
    over_commands = len(calls) > bounds.max_commands
    over_outputs = sum(len(v) for v in outputs.values()) > bounds.max_outputs
    if over_commands or over_outputs:
        return (
            (),
            (UnpairedRecord(location="$", call_id="", limitation=Limitation.OVER_BOUND),),
        )

    calls_by_id: dict[str, list[tuple[str, str, str, object]]] = {}
    for call_id, location, name, arguments in calls:
        calls_by_id.setdefault(call_id, []).append((call_id, location, name, arguments))

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
            for rlocation, _endpoint, _text in results:
                unpaired.append(
                    UnpairedRecord(
                        location=rlocation,
                        call_id=call_id,
                        limitation=Limitation.MULTI_CHUNK_DEFERRED,
                    )
                )
            continue
        result_location, endpoint, output_text = results[0]
        observations.append(
            _build_observation(
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
        )

    for call_id in sorted(outputs):
        if call_id in calls_by_id:
            continue
        for location, _endpoint, _text in outputs[call_id]:
            unpaired.append(
                UnpairedRecord(
                    location=location,
                    call_id=call_id,
                    limitation=Limitation.MISMATCHED_CALL_ID,
                )
            )
    return tuple(observations), tuple(unpaired)

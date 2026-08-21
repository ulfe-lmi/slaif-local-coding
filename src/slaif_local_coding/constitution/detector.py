"""Evidence-based AGENTS.md observation over documented API envelope positions."""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from typing import Any

from ..config import ObservationPolicy
from .models import (
    CandidateReference,
    ConstitutionSourceObservation,
    EvidenceRecord,
    EvidenceType,
    IncompleteReason,
    ObservationContext,
    ObservationResult,
    RejectionCount,
    RejectionReason,
)
from .references import extract_references

_PROJECT = re.compile(
    r"^# AGENTS\.md instructions for (?P<directory>[^\r\n]+)\r?\n\r?\n"
    r"<INSTRUCTIONS>\r?\n(?P<content>.*?)\r?\n</INSTRUCTIONS>"
    r"(?P<tail>(?:\r?\n)?(?:<environment_context>\r?\n.*\r?\n"
    r"</environment_context>\r?\n?)?)$",
    re.DOTALL,
)
_PROJECT_MARKER = "# AGENTS.md instructions for "
_READ = re.compile(
    r"^(?:cat|head(?:\s+-n\s+\d+)?|tail(?:\s+-n\s+\d+)?|"
    r"sed\s+-n\s+['\"]?\d+(?:,\d+)?p['\"]?)\s+(?P<path>[^\s]+)$"
)
_SCHEME = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*:")
_DRIVE = re.compile(r"^[A-Za-z]:[\\/]")


@dataclass(frozen=True)
class _Found:
    path: str
    content: str
    evidence_type: EvidenceType
    location: str


def _logical_agents_path(
    label: str, max_bytes: int, *, project_directory: bool = False
) -> str | None:
    """Return a privacy-safe POSIX repository label, never resolving the filesystem."""
    if not label or any(ord(char) < 32 for char in label):
        return None
    if any(char in label for char in ("%", "?", "#")) or _SCHEME.match(label):
        return None
    if "\\" in label or label.startswith(("/", "//")) or _DRIVE.match(label):
        return (
            "AGENTS.md"
            if project_directory and label.startswith("/") and max_bytes >= len(b"AGENTS.md")
            else None
        )
    parts = [part for part in label.split("/") if part not in ("", ".")]
    if not parts or ".." in parts:
        return None
    if project_directory:
        if parts == ["repo"] or parts == ["repository"]:
            parts = []
        parts.append("AGENTS.md")
    if not parts or parts[-1] != "AGENTS.md":
        return None
    normalized = "/".join(parts)
    return normalized if len(normalized.encode()) <= max_bytes else None


def _content_items(payload: dict[str, Any]) -> list[tuple[dict[str, Any], str, str | None]]:
    """Enumerate only top-level Responses input and Chat message content items."""
    result: list[tuple[dict[str, Any], str, str | None]] = []
    for container_key in ("input", "messages"):
        container = payload.get(container_key)
        if not isinstance(container, list):
            continue
        for index, value in enumerate(container):
            location = f"$.{container_key}[{index}]"
            if not isinstance(value, dict):
                continue
            role = value.get("role") if isinstance(value.get("role"), str) else None
            content = value.get("content")
            if isinstance(content, list):
                for item_index, item in enumerate(content):
                    if isinstance(item, dict):
                        result.append((item, f"{location}.content[{item_index}]", role))
            elif container_key == "input" and "role" not in value:
                result.append((value, location, None))
    return result


def _project_sources(
    payload: dict[str, Any], policy: ObservationPolicy
) -> tuple[list[_Found], bool, bool]:
    invalid_path = False
    malformed = False
    supported: list[tuple[re.Match[str], str]] = []
    inputs = payload.get("input")
    if isinstance(inputs, list):
        for input_index, parent in enumerate(inputs):
            if not isinstance(parent, dict) or parent.get("role") != "user":
                continue
            content = parent.get("content")
            if not isinstance(content, list):
                continue
            for content_index, item in enumerate(content):
                if not isinstance(item, dict) or item.get("type") != "input_text":
                    continue
                text = item.get("text")
                if not isinstance(text, str) or _PROJECT_MARKER not in text:
                    continue
                match = _PROJECT.fullmatch(text)
                if match is None or "</INSTRUCTIONS>" in match.group("content"):
                    malformed = True
                    continue
                supported.append((match, f"$.input[{input_index}].content[{content_index}]"))
    if malformed or len(supported) != 1:
        return [], invalid_path, malformed or len(supported) > 1
    match, location = supported[0]
    logical = _logical_agents_path(
        match.group("directory").strip(), policy.max_path_bytes, project_directory=True
    )
    if logical is None:
        return [], True, malformed
    content = match.group("content")
    result = [_Found(logical, content, EvidenceType.PROJECT_INSTRUCTIONS, location)]

    instructions = payload.get("instructions")
    if isinstance(instructions, str) and instructions.startswith(_PROJECT_MARKER):
        corroboration = _PROJECT.fullmatch(instructions)
        if (
            corroboration is None
            or corroboration.group("tail") not in ("", "\n", "\r\n")
            or "</INSTRUCTIONS>" in corroboration.group("content")
        ):
            return [], invalid_path, True
        corroborating_logical = _logical_agents_path(
            corroboration.group("directory").strip(),
            policy.max_path_bytes,
            project_directory=True,
        )
        if corroborating_logical is None:
            return [], True, malformed
        if corroborating_logical != logical or corroboration.group("content") != content:
            return [], invalid_path, True
        result.append(_Found(logical, content, EvidenceType.PROJECT_INSTRUCTIONS, "$.instructions"))
    return result, invalid_path, malformed


def _input_files(payload: dict[str, Any], policy: ObservationPolicy) -> tuple[list[_Found], bool]:
    result: list[_Found] = []
    invalid_path = False
    for item, location, role in _content_items(payload):
        if item.get("type") != "input_file" or role not in (None, "user", "developer", "system"):
            continue
        filename = item.get("filename")
        content = item.get("content")
        logical = (
            _logical_agents_path(filename, policy.max_path_bytes)
            if isinstance(filename, str)
            else None
        )
        if logical is not None and isinstance(content, str):
            result.append(_Found(logical, content, EvidenceType.INPUT_FILE, location))
        elif isinstance(filename, str) and isinstance(content, str):
            invalid_path = True
    return result, invalid_path


def _parsed_command(arguments: Any) -> str | None:
    if isinstance(arguments, str):
        try:
            arguments = json.loads(arguments)
        except (json.JSONDecodeError, RecursionError):
            return None
    if not isinstance(arguments, dict) or set(arguments) != {"cmd"}:
        return None
    command = arguments.get("cmd")
    return command if isinstance(command, str) else None


def _tool_sources(payload: dict[str, Any], policy: ObservationPolicy) -> tuple[list[_Found], bool]:
    calls: dict[str, list[str]] = {}
    outputs: dict[str, list[tuple[str, str]]] = {}
    call_occurrences: dict[str, int] = {}
    invalid_path = False
    input_items = payload.get("input")
    if isinstance(input_items, list):
        for index, item in enumerate(input_items):
            if not isinstance(item, dict):
                continue
            location = f"$.input[{index}]"
            call_id = item.get("call_id")
            if item.get("type") == "function_call" and isinstance(call_id, str) and call_id:
                call_occurrences[call_id] = call_occurrences.get(call_id, 0) + 1
            if (
                item.get("type") == "function_call"
                and item.get("name") == "exec_command"
                and isinstance(call_id, str)
                and call_id
            ):
                command = _parsed_command(item.get("arguments"))
                match = _READ.fullmatch(command.strip()) if command is not None else None
                logical = (
                    _logical_agents_path(match.group("path"), policy.max_path_bytes)
                    if match is not None
                    else None
                )
                if logical is not None:
                    calls.setdefault(call_id, []).append(logical)
                elif match is not None:
                    invalid_path = True
            if item.get("type") == "function_call_output" and isinstance(call_id, str):
                output = item.get("output")
                if isinstance(output, str):
                    outputs.setdefault(call_id, []).append((output, location))
    messages = payload.get("messages")
    if isinstance(messages, list):
        for index, message in enumerate(messages):
            if not isinstance(message, dict):
                continue
            location = f"$.messages[{index}]"
            if message.get("role") == "assistant" and isinstance(message.get("tool_calls"), list):
                for tool in message["tool_calls"]:
                    if not isinstance(tool, dict) or tool.get("type") != "function":
                        continue
                    function = tool.get("function")
                    call_id = tool.get("id")
                    if isinstance(call_id, str) and call_id:
                        call_occurrences[call_id] = call_occurrences.get(call_id, 0) + 1
                    if (
                        not isinstance(function, dict)
                        or function.get("name") != "exec_command"
                        or not isinstance(call_id, str)
                    ):
                        continue
                    command = _parsed_command(function.get("arguments"))
                    match = _READ.fullmatch(command.strip()) if command is not None else None
                    logical = (
                        _logical_agents_path(match.group("path"), policy.max_path_bytes)
                        if match is not None
                        else None
                    )
                    if logical is not None:
                        calls.setdefault(call_id, []).append(logical)
                    elif match is not None:
                        invalid_path = True
            if message.get("role") == "tool":
                call_id = message.get("tool_call_id")
                content = message.get("content")
                if isinstance(call_id, str) and isinstance(content, str):
                    outputs.setdefault(call_id, []).append((content, location))
    found = [
        _Found(
            paths[0],
            outputs[call_id][0][0],
            EvidenceType.PAIRED_TOOL_RESULT,
            outputs[call_id][0][1],
        )
        for call_id, paths in calls.items()
        if call_occurrences.get(call_id) == 1
        and len(paths) == 1
        and len(outputs.get(call_id, ())) == 1
    ]
    return found, invalid_path


def observe_request(
    payload: dict[str, Any], context: ObservationContext, policy: ObservationPolicy
) -> ObservationResult:
    reasons: list[IncompleteReason] = []
    project, invalid_project, malformed_project = _project_sources(payload, policy)
    input_files, invalid_input = _input_files(payload, policy)
    tools, invalid_tool = _tool_sources(payload, policy)
    found = project + input_files + tools
    if invalid_project or invalid_input or invalid_tool:
        reasons.append(IncompleteReason.INVALID_ROOT_PATH)
    if malformed_project:
        reasons.append(IncompleteReason.PARSING_ERROR)
    if len(found) > policy.max_roots:
        found = found[: policy.max_roots]
        reasons.append(IncompleteReason.TOO_MANY_ROOTS)
    roots: list[ConstitutionSourceObservation] = []
    root_index: dict[tuple[str, str], int] = {}
    rejected = 0
    rejection_counts: dict[RejectionReason, int] = {}
    for item in found:
        encoded = item.content.encode("utf-8")
        digest = hashlib.sha256(encoded).hexdigest()
        key = (item.path, digest)
        evidence = EvidenceRecord(
            type=item.evidence_type, start_byte=0, end_byte=len(encoded), location=item.location
        )
        if key in root_index:
            index = root_index[key]
            root = roots[index]
            roots[index] = root.model_copy(update={"evidence": root.evidence + (evidence,)})
            continue
        source_reasons: list[IncompleteReason] = []
        candidates: tuple[CandidateReference, ...] = ()
        if len(encoded) > policy.max_source_bytes:
            source_reasons.append(IncompleteReason.SOURCE_TOO_LARGE)
        else:
            extraction = extract_references(item.content, policy)
            candidates = extraction.candidates
            rejected += extraction.rejected
            for count in extraction.rejection_counts:
                rejection_counts[count.reason] = rejection_counts.get(count.reason, 0) + count.count
            source_reasons.extend(extraction.reasons)
        for reason in source_reasons:
            if reason not in reasons:
                reasons.append(reason)
        root_index[key] = len(roots)
        roots.append(
            ConstitutionSourceObservation(
                logical_path=item.path,
                content_sha256=digest,
                byte_length=len(encoded),
                evidence=(evidence,),
                candidates=candidates,
                complete=not source_reasons,
                incomplete_reasons=tuple(source_reasons),
            )
        )
    return ObservationResult(
        schema_version=policy.schema_version,
        policy_version=policy.policy_version,
        context=context,
        roots=tuple(roots),
        complete=not reasons,
        incomplete_reasons=tuple(reasons),
        accepted_candidates=sum(len(root.candidates) for root in roots),
        rejected_candidates=rejected,
        rejection_counts=tuple(
            RejectionCount(reason=reason, count=count)
            for reason, count in sorted(rejection_counts.items(), key=lambda item: item[0].value)
        ),
    )

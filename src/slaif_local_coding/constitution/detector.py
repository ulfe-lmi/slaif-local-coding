"""Evidence-based AGENTS.md and dependency observation over request content only."""

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
    DependencyObservationReason,
    DependencyRejectionCount,
    EvidenceRecord,
    EvidenceType,
    IncompleteReason,
    ObservationContext,
    ObservationResult,
    ObservedDependency,
    RejectionCount,
    RejectionReason,
)
from .references import extract_references, validate_exact_repository_path

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
    """Return a canonical root label using the shared repository path grammar."""
    value = label.strip()
    if project_directory and value.startswith(("/", "//")):
        return "AGENTS.md" if max_bytes >= len(b"AGENTS.md") else None
    if project_directory:
        tentative = value.replace("\\", "/").rstrip("/")
        normalized, _, _ = validate_exact_repository_path(f"{tentative}/AGENTS.md", max_bytes)
        if normalized is None:
            return None
        parts = [part for part in normalized.split("/") if part not in ("", ".")]
        if parts and parts[0] in {"repo", "repository"}:
            parts.pop(0)
        normalized = "/".join(parts)
    else:
        normalized, _, _ = validate_exact_repository_path(value, max_bytes)
    if normalized is None:
        return None
    parts = [part for part in normalized.split("/") if part not in ("", ".")]
    return normalized if len(normalized.encode("utf-8")) <= max_bytes else None


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
    """Return only valid AGENTS.md input files and whether a root label was unsafe."""
    result: list[_Found] = []
    invalid_root = False
    for item, location, role in _content_items(payload):
        if item.get("type") != "input_file" or role not in (None, "user", "developer", "system"):
            continue
        filename = item.get("filename")
        content = item.get("content")
        if not isinstance(filename, str):
            continue
        logical, _, rejection = validate_exact_repository_path(filename, policy.max_path_bytes)
        logical_label = filename.split("#", 1)[0].split("?", 1)[0]
        basename = logical_label.replace("\\", "/").rstrip("/").split("/")[-1].lower()
        if logical is None:
            if basename == "agents.md":
                invalid_root = True
            continue
        if logical.split("/")[-1] != "AGENTS.md":
            continue
        if isinstance(content, str):
            result.append(_Found(logical, content, EvidenceType.INPUT_FILE, location))
        elif rejection is RejectionReason.PATH_TOO_LONG:
            invalid_root = True
    return result, invalid_root


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
    """Pair supported read calls one-to-one for AGENTS.md roots only."""
    calls: dict[str, list[_Found]] = {}
    outputs: dict[str, list[tuple[str, str]]] = {}
    call_occurrences: dict[str, int] = {}
    invalid_root = False

    def read_path(arguments: Any, location: str, call_id: Any) -> None:
        nonlocal invalid_root
        command = _parsed_command(arguments)
        match = _READ.fullmatch(command.strip()) if command is not None else None
        if match is None:
            return
        raw_path = match.group("path")
        logical, _, _ = validate_exact_repository_path(raw_path, policy.max_path_bytes)
        if logical is None:
            logical_label = raw_path.split("#", 1)[0].split("?", 1)[0]
            if logical_label.replace("\\", "/").rstrip("/").split("/")[-1].lower() == "agents.md":
                invalid_root = True
            return
        if logical.split("/")[-1] != "AGENTS.md" or not isinstance(call_id, str) or not call_id:
            return
        calls.setdefault(call_id, []).append(
            _Found(logical, "", EvidenceType.PAIRED_TOOL_RESULT, location)
        )

    input_items = payload.get("input")
    if isinstance(input_items, list):
        for index, item in enumerate(input_items):
            if not isinstance(item, dict):
                continue
            location = f"$.input[{index}]"
            call_id = item.get("call_id")
            if item.get("type") == "function_call" and isinstance(call_id, str) and call_id:
                call_occurrences[call_id] = call_occurrences.get(call_id, 0) + 1
                if item.get("name") == "exec_command":
                    read_path(item.get("arguments"), location, call_id)
            if item.get("type") == "function_call_output" and isinstance(call_id, str) and call_id:
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
                for _tool_index, tool in enumerate(message["tool_calls"]):
                    if not isinstance(tool, dict) or tool.get("type") != "function":
                        continue
                    function = tool.get("function")
                    call_id = tool.get("id")
                    if isinstance(call_id, str) and call_id:
                        call_occurrences[call_id] = call_occurrences.get(call_id, 0) + 1
                        if isinstance(function, dict) and function.get("name") == "exec_command":
                            read_path(
                                function.get("arguments"),
                                f"{location}.tool_calls[{_tool_index}]",
                                call_id,
                            )
            if message.get("role") == "tool":
                call_id = message.get("tool_call_id")
                content = message.get("content")
                if isinstance(call_id, str) and call_id and isinstance(content, str):
                    outputs.setdefault(call_id, []).append((content, location))

    found: list[_Found] = []
    for call_id, paired_calls in calls.items():
        paired_outputs = outputs.get(call_id, ())
        if (
            call_occurrences.get(call_id) == 1
            and len(paired_calls) == 1
            and len(paired_outputs) == 1
        ):
            source_call = paired_calls[0]
            output, output_location = paired_outputs[0]
            found.append(
                _Found(source_call.path, output, source_call.evidence_type, output_location)
            )
    return found, invalid_root


@dataclass(frozen=True)
class _DependencyEvidence:
    path: str
    content: str
    record: EvidenceRecord


def _dependency_input_files(
    payload: dict[str, Any],
    expected_paths: tuple[str, ...],
    root_path: str,
    policy: ObservationPolicy,
    rejections: dict[DependencyObservationReason, int],
) -> list[_DependencyEvidence]:
    expected = set(expected_paths)
    found: list[_DependencyEvidence] = []

    def reject(reason: DependencyObservationReason) -> None:
        rejections[reason] = rejections.get(reason, 0) + 1

    for item, location, role in _content_items(payload):
        if item.get("type") != "input_file" or role not in (None, "user", "developer", "system"):
            continue
        filename = item.get("filename")
        if not isinstance(filename, str):
            continue
        logical, _, rejection = validate_exact_repository_path(filename, policy.max_path_bytes)
        if logical is None:
            basename = filename.replace("\\", "/").rstrip("/").split("/")[-1]
            if basename in {path.rsplit("/", 1)[-1] for path in expected}:
                reason = (
                    DependencyObservationReason.AMBIGUOUS
                    if rejection is RejectionReason.AMBIGUOUS
                    else DependencyObservationReason.UNSAFE_PATH
                )
                rejections[reason] = rejections.get(reason, 0) + 1
            continue
        if logical == root_path or logical not in expected:
            continue
        content = item.get("content")
        if not isinstance(content, str):
            reject(DependencyObservationReason.MISMATCHED_PAIRING)
            continue
        try:
            encoded = content.encode("utf-8", errors="strict")
        except UnicodeEncodeError:
            reject(DependencyObservationReason.INVALID_CONTENT)
            continue
        if not encoded:
            reject(DependencyObservationReason.INVALID_CONTENT)
            continue
        if len(encoded) > policy.max_source_bytes:
            reject(DependencyObservationReason.CONTENT_TOO_LARGE)
            continue
        found.append(
            _DependencyEvidence(
                logical,
                content,
                EvidenceRecord(
                    type=EvidenceType.INPUT_FILE,
                    start_byte=0,
                    end_byte=len(encoded),
                    location=location,
                ),
            )
        )
    return found


def _dependency_tool_results(
    payload: dict[str, Any],
    expected_paths: tuple[str, ...],
    root_path: str,
    policy: ObservationPolicy,
    rejections: dict[DependencyObservationReason, int],
) -> list[_DependencyEvidence]:
    expected = set(expected_paths)
    calls: dict[str, list[str]] = {}
    outputs: dict[str, list[tuple[Any, str]]] = {}
    occurrences: dict[str, int] = {}

    def read_call(arguments: Any, call_id: Any) -> None:
        command = _parsed_command(arguments)
        match = _READ.fullmatch(command.strip()) if command is not None else None
        if match is None or not isinstance(call_id, str) or not call_id:
            return
        logical, _, rejection = validate_exact_repository_path(
            match.group("path"), policy.max_path_bytes
        )
        if logical is None:
            basename = match.group("path").replace("\\", "/").rstrip("/").split("/")[-1]
            if basename in {path.rsplit("/", 1)[-1] for path in expected}:
                reason = (
                    DependencyObservationReason.AMBIGUOUS
                    if rejection is RejectionReason.AMBIGUOUS
                    else DependencyObservationReason.UNSAFE_PATH
                )
                rejections[reason] = rejections.get(reason, 0) + 1
            return
        if logical != root_path and logical in expected:
            calls.setdefault(call_id, []).append(logical)

    input_items = payload.get("input")
    if isinstance(input_items, list):
        for index, item in enumerate(input_items):
            if not isinstance(item, dict):
                continue
            call_id = item.get("call_id")
            if item.get("type") == "function_call" and isinstance(call_id, str) and call_id:
                occurrences[call_id] = occurrences.get(call_id, 0) + 1
                if item.get("name") == "exec_command":
                    read_call(item.get("arguments"), call_id)
            if item.get("type") == "function_call_output" and isinstance(call_id, str) and call_id:
                outputs.setdefault(call_id, []).append((item.get("output"), f"$.input[{index}]"))

    messages = payload.get("messages")
    if isinstance(messages, list):
        for index, message in enumerate(messages):
            if not isinstance(message, dict):
                continue
            if message.get("role") == "assistant" and isinstance(message.get("tool_calls"), list):
                for _tool_index, tool in enumerate(message["tool_calls"]):
                    if not isinstance(tool, dict) or tool.get("type") != "function":
                        continue
                    function = tool.get("function")
                    call_id = tool.get("id")
                    if isinstance(call_id, str) and call_id:
                        occurrences[call_id] = occurrences.get(call_id, 0) + 1
                        if isinstance(function, dict) and function.get("name") == "exec_command":
                            read_call(
                                function.get("arguments"),
                                call_id,
                            )
            if message.get("role") == "tool":
                call_id = message.get("tool_call_id")
                if isinstance(call_id, str) and call_id:
                    outputs.setdefault(call_id, []).append(
                        (message.get("content"), f"$.messages[{index}]")
                    )

    by_path: dict[str, list[_DependencyEvidence]] = {path: [] for path in expected_paths}
    for call_id, paths in calls.items():
        for logical_path in paths:
            if len(paths) > 1:
                rejections[DependencyObservationReason.DUPLICATE_EVIDENCE] = (
                    rejections.get(DependencyObservationReason.DUPLICATE_EVIDENCE, 0) + 1
                )
                continue
            paired_outputs = outputs.get(call_id, [])
            if occurrences.get(call_id) != 1 or not paired_outputs:
                rejections[DependencyObservationReason.MISMATCHED_PAIRING] = (
                    rejections.get(DependencyObservationReason.MISMATCHED_PAIRING, 0) + 1
                )
                continue
            if len(paired_outputs) > 1:
                rejections[DependencyObservationReason.EXTRA_EVIDENCE] = (
                    rejections.get(DependencyObservationReason.EXTRA_EVIDENCE, 0) + 1
                )
                continue
            output, location = paired_outputs[0]
            if not isinstance(output, str):
                rejections[DependencyObservationReason.MISMATCHED_PAIRING] = (
                    rejections.get(DependencyObservationReason.MISMATCHED_PAIRING, 0) + 1
                )
                continue
            try:
                encoded = output.encode("utf-8", errors="strict")
            except UnicodeEncodeError:
                rejections[DependencyObservationReason.INVALID_CONTENT] = (
                    rejections.get(DependencyObservationReason.INVALID_CONTENT, 0) + 1
                )
                continue
            if not encoded:
                rejections[DependencyObservationReason.INVALID_CONTENT] = (
                    rejections.get(DependencyObservationReason.INVALID_CONTENT, 0) + 1
                )
                continue
            if len(encoded) > policy.max_source_bytes:
                rejections[DependencyObservationReason.CONTENT_TOO_LARGE] = (
                    rejections.get(DependencyObservationReason.CONTENT_TOO_LARGE, 0) + 1
                )
                continue
            by_path[logical_path].append(
                _DependencyEvidence(
                    logical_path,
                    output,
                    EvidenceRecord(
                        type=EvidenceType.PAIRED_TOOL_RESULT,
                        start_byte=0,
                        end_byte=len(encoded),
                        location=location,
                    ),
                )
            )

    found: list[_DependencyEvidence] = []
    for path in expected_paths:
        records = by_path[path]
        if not records:
            continue
        if len(records) > 1:
            rejections[DependencyObservationReason.DUPLICATE_EVIDENCE] = (
                rejections.get(DependencyObservationReason.DUPLICATE_EVIDENCE, 0) + 1
            )
            continue
        found.append(records[0])
    return found


def observe_request_for_pipeline(
    payload: dict[str, Any], context: ObservationContext, policy: ObservationPolicy
) -> tuple[ObservationResult, dict[tuple[str, str], bytes], dict[str, bytes]]:
    """Observe roots and uniquely evidenced dependencies without retaining state."""
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
    sources: dict[tuple[str, str], bytes] = {}
    rejected = 0
    rejection_counts: dict[RejectionReason, int] = {}
    for item in found:
        encoded = item.content.encode("utf-8", errors="strict")
        digest = hashlib.sha256(encoded).hexdigest()
        key = (item.path, digest)
        evidence = EvidenceRecord(
            type=item.evidence_type,
            start_byte=0,
            end_byte=len(encoded),
            location=item.location,
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
        sources[key] = encoded
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

    dependency_rejections: dict[DependencyObservationReason, int] = {}
    dependencies: list[ObservedDependency] = []
    dependency_sources: dict[str, bytes] = {}
    if len(roots) == 1 and roots[0].complete:
        root = roots[0]
        expected_paths = tuple(candidate.path for candidate in root.candidates)
        evidence_items = _dependency_input_files(
            payload, expected_paths, root.logical_path, policy, dependency_rejections
        ) + _dependency_tool_results(
            payload, expected_paths, root.logical_path, policy, dependency_rejections
        )
        grouped: dict[str, list[_DependencyEvidence]] = {path: [] for path in expected_paths}
        for dependency_item in evidence_items:
            grouped[dependency_item.path].append(dependency_item)
        for path in expected_paths:
            records = grouped[path]
            if len(records) > 1:
                dependency_rejections[DependencyObservationReason.DUPLICATE_EVIDENCE] = (
                    dependency_rejections.get(DependencyObservationReason.DUPLICATE_EVIDENCE, 0) + 1
                )
                continue
            if not records:
                continue
            record = records[0]
            encoded = records[0].content.encode("utf-8", errors="strict")
            dependencies.append(
                ObservedDependency(
                    logical_path=path,
                    byte_length=len(encoded),
                    evidence=(record.record,),
                )
            )
            dependency_sources[path] = encoded

    observation_result = ObservationResult(
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
        dependencies=tuple(dependencies),
        dependency_rejections=tuple(
            DependencyRejectionCount(reason=reason, count=count)
            for reason, count in sorted(
                dependency_rejections.items(), key=lambda item: item[0].value
            )
        ),
    )
    return observation_result, sources, dependency_sources


def observe_request_with_sources(
    payload: dict[str, Any], context: ObservationContext, policy: ObservationPolicy
) -> tuple[ObservationResult, dict[tuple[str, str], bytes]]:
    """Backward-compatible root-only source observation entry point."""
    result, sources, _ = observe_request_for_pipeline(payload, context, policy)
    return result, sources


def observe_request(
    payload: dict[str, Any], context: ObservationContext, policy: ObservationPolicy
) -> ObservationResult:
    """Observe without retaining exact source bytes beyond this synchronous call."""
    result, _, _ = observe_request_for_pipeline(payload, context, policy)
    return result

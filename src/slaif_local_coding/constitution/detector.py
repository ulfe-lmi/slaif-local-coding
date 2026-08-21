"""Evidence-based AGENTS.md observation over an already bounded JSON value."""

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
    r"<INSTRUCTIONS>\r?\n(?P<content>.*?)\r?\n</INSTRUCTIONS>(?:\r?\n|$)",
    re.DOTALL,
)
_READ = re.compile(
    r"^(?:cat|head(?:\s+-n\s+\d+)?|tail(?:\s+-n\s+\d+)?|"
    r"sed\s+-n\s+['\"]?\d+(?:,\d+)?p['\"]?)\s+"
    r"(?P<path>(?:[A-Za-z0-9_.-]+/)*AGENTS\.md)$"
)


@dataclass(frozen=True)
class _Found:
    path: str
    content: str
    evidence_type: EvidenceType
    location: str


def _walk(value: Any, location: str = "$") -> list[tuple[Any, str]]:
    found = [(value, location)]
    if isinstance(value, dict):
        for key, child in value.items():
            found.extend(_walk(child, f"{location}.{key}"))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            found.extend(_walk(child, f"{location}[{index}]"))
    return found


def _text(value: Any) -> str | None:
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        for key in ("text", "content"):
            candidate = value.get(key)
            if isinstance(candidate, str):
                return candidate
    return None


def _project_sources(payload: Any) -> list[_Found]:
    result: list[_Found] = []
    for value, location in _walk(payload):
        if not isinstance(value, str):
            continue
        match = _PROJECT.match(value)
        if not match:
            continue
        directory = match.group("directory").strip().replace("\\", "/").rstrip("/")
        logical = (
            "AGENTS.md" if directory in {".", "repo", "repository"} else f"{directory}/AGENTS.md"
        )
        # Absolute effective directories are labels only; avoid persisting a private host path.
        if logical.startswith("/"):
            logical = "AGENTS.md"
        result.append(
            _Found(logical, match.group("content"), EvidenceType.PROJECT_INSTRUCTIONS, location)
        )
    return result


def _input_files(payload: Any) -> list[_Found]:
    result: list[_Found] = []
    for value, location in _walk(payload):
        if not isinstance(value, dict):
            continue
        filename = value.get("filename") or value.get("name")
        if (
            not isinstance(filename, str)
            or filename.replace("\\", "/").split("/")[-1] != "AGENTS.md"
        ):
            continue
        if re.match(r"^[A-Za-z][A-Za-z0-9+.-]*:", filename) or filename.startswith(("/", "\\")):
            continue
        content = _text(value.get("content"))
        if content is None:
            content = _text(value.get("text"))
        if content is not None:
            result.append(
                _Found(filename.replace("\\", "/"), content, EvidenceType.INPUT_FILE, location)
            )
    return result


def _tool_sources(payload: Any) -> list[_Found]:
    calls: dict[str, str] = {}
    outputs: dict[str, tuple[str, str]] = {}
    for value, location in _walk(payload):
        if not isinstance(value, dict):
            continue
        call_id = value.get("call_id") or value.get("id")
        if value.get("type") in {"function_call", "tool_call"} and isinstance(call_id, str):
            arguments = value.get("arguments")
            if isinstance(value.get("function"), dict):
                arguments = value["function"].get("arguments")
            try:
                parsed = json.loads(arguments) if isinstance(arguments, str) else arguments
            except json.JSONDecodeError:
                parsed = None
            command = parsed.get("cmd") if isinstance(parsed, dict) else None
            if isinstance(command, str):
                match = _READ.fullmatch(command.strip())
                if match:
                    calls[call_id] = match.group("path")
        output_id = value.get("call_id") or value.get("tool_call_id")
        if value.get("type") == "function_call_output" or value.get("role") == "tool":
            content = _text(value.get("output")) or _text(value.get("content"))
            if isinstance(output_id, str) and content is not None:
                outputs[output_id] = (content, location)
    return [
        _Found(path, outputs[call_id][0], EvidenceType.PAIRED_TOOL_RESULT, outputs[call_id][1])
        for call_id, path in calls.items()
        if call_id in outputs
    ]


def observe_request(
    payload: dict[str, Any], context: ObservationContext, policy: ObservationPolicy
) -> ObservationResult:
    reasons: list[IncompleteReason] = []
    found = _project_sources(payload) + _input_files(payload) + _tool_sources(payload)
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

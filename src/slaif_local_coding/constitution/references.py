"""Deterministic syntactic repository-reference enumeration."""

from __future__ import annotations

import re
from dataclasses import dataclass

from ..config import ObservationPolicy
from .models import (
    CandidateReference,
    EvidenceRecord,
    EvidenceType,
    IncompleteReason,
    RejectionCount,
    RejectionReason,
)

_ALLOWED_SUFFIXES = (
    ".md",
    ".txt",
    ".rst",
    ".toml",
    ".yaml",
    ".yml",
    ".json",
    ".ini",
    ".cfg",
    ".sh",
    ".py",
)
_INLINE = re.compile(r"(?<!!)\[[^\]\n]*\]\((?P<path>[^\s)]+)(?:\s+['\"][^\n]*['\"])?\)")
_REFERENCE = re.compile(r"(?m)^\s*\[[^\]\n]+\]:\s*(?:<(?P<angle>[^>]+)>|(?P<plain>\S+))")
_BACKTICK = re.compile(r"`(?P<path>[^`\n]+)`")
_QUOTED = re.compile(r"(?P<quote>['\"])(?P<path>[^'\"\n]+)(?P=quote)")
_NORMATIVE = re.compile(r"(?i)\b(?:MUST(?:\s+NOT)?|NEVER|REQUIRED|binding|read|before)\b")
_BARE_PATH = re.compile(
    r"(?<![/:\\])\b(?P<path>(?:\.github/)?[A-Za-z0-9_.-]+(?:/[A-Za-z0-9_.-]+)*)"
)


@dataclass(frozen=True)
class Extraction:
    candidates: tuple[CandidateReference, ...]
    rejected: int
    reasons: tuple[IncompleteReason, ...]
    rejection_counts: tuple[RejectionCount, ...]


def _byte_offset(text: str, character_offset: int) -> int:
    return len(text[:character_offset].encode("utf-8"))


def _normalize(
    raw: str, max_bytes: int
) -> tuple[str | None, IncompleteReason | None, RejectionReason | None]:
    value = raw.strip()
    if "#" in value:
        value = value.split("#", 1)[0]
    if not value or "?" in value or "\x00" in value or any(ord(c) < 32 for c in value):
        return None, None, RejectionReason.AMBIGUOUS
    if re.match(r"^[A-Za-z][A-Za-z0-9+.-]*:", value):
        return None, None, RejectionReason.UNSAFE_LOCATION
    if value.startswith(("/", "\\", "//")) or re.match(r"^[A-Za-z]:[\\/]", value):
        return None, None, RejectionReason.UNSAFE_LOCATION
    if "%" in value or value.endswith("/"):
        return None, None, RejectionReason.AMBIGUOUS
    parts = [part for part in value.replace("\\", "/").split("/") if part not in {"", "."}]
    if not parts or ".." in parts:
        return None, None, RejectionReason.TRAVERSAL
    normalized = "/".join(parts)
    if normalized.startswith(".") and not normalized.startswith(".github/"):
        return None, None, RejectionReason.UNSUPPORTED_FILE
    basename = parts[-1]
    if not (
        basename == "Makefile"
        or basename == "AGENTS.md"
        or basename.lower().endswith(_ALLOWED_SUFFIXES)
    ):
        return None, None, RejectionReason.UNSUPPORTED_FILE
    if len(normalized.encode("utf-8")) > max_bytes:
        return None, IncompleteReason.PATH_TOO_LONG, RejectionReason.PATH_TOO_LONG
    return normalized, None, None


def extract_references(text: str, policy: ObservationPolicy) -> Extraction:
    matches: list[tuple[int, int, str, EvidenceType]] = []
    for pattern, evidence_type in (
        (_INLINE, EvidenceType.MARKDOWN_INLINE),
        (_REFERENCE, EvidenceType.MARKDOWN_REFERENCE),
        (_BACKTICK, EvidenceType.BACKTICK),
        (_QUOTED, EvidenceType.QUOTED),
    ):
        for match in pattern.finditer(text):
            group = "angle" if match.groupdict().get("angle") is not None else "path"
            if group not in match.groupdict():
                group = "plain"
            start, end = match.span(group)
            matches.append((start, end, match.group(group), evidence_type))
    for line_match in re.finditer(r"[^\n]*", text):
        line = line_match.group()
        if not _NORMATIVE.search(line):
            continue
        for match in _BARE_PATH.finditer(line):
            start, end = match.span("path")
            raw = match.group("path")
            # Prose punctuation terminates a bare token. Structured destination
            # forms retain their exact spans and are not trimmed here.
            trimmed = raw.rstrip(".,;:!?")
            end -= len(raw) - len(trimmed)
            if not trimmed:
                continue
            matches.append(
                (
                    line_match.start() + start,
                    line_match.start() + end,
                    trimmed,
                    EvidenceType.NORMATIVE_NEIGHBOR,
                )
            )
    matches.sort(key=lambda item: (item[0], item[1], item[3].value))
    paths: dict[str, list[EvidenceRecord]] = {}
    order: list[str] = []
    rejected = 0
    reasons: list[IncompleteReason] = []
    total_evidence = 0
    rejection_counts: dict[RejectionReason, int] = {}
    for start, end, raw, evidence_type in matches:
        normalized, limit_reason, rejection_reason = _normalize(raw, policy.max_path_bytes)
        if normalized is None:
            rejected += 1
            if rejection_reason is not None:
                rejection_counts[rejection_reason] = rejection_counts.get(rejection_reason, 0) + 1
            if limit_reason and limit_reason not in reasons:
                reasons.append(limit_reason)
            continue
        if normalized not in paths:
            if len(order) >= policy.max_candidates:
                if IncompleteReason.TOO_MANY_CANDIDATES not in reasons:
                    reasons.append(IncompleteReason.TOO_MANY_CANDIDATES)
                continue
            # A retained candidate must be born with evidence, even when the
            # global budget makes the overall manifest incomplete.
            if total_evidence >= policy.max_total_evidence:
                if IncompleteReason.EVIDENCE_BUDGET_EXCEEDED not in reasons:
                    reasons.append(IncompleteReason.EVIDENCE_BUDGET_EXCEEDED)
                continue
            paths[normalized] = []
            order.append(normalized)
        if total_evidence >= policy.max_total_evidence:
            if IncompleteReason.EVIDENCE_BUDGET_EXCEEDED not in reasons:
                reasons.append(IncompleteReason.EVIDENCE_BUDGET_EXCEEDED)
            continue
        evidence = paths[normalized]
        if len(evidence) >= policy.max_evidence_per_candidate:
            if IncompleteReason.EVIDENCE_BUDGET_EXCEEDED not in reasons:
                reasons.append(IncompleteReason.EVIDENCE_BUDGET_EXCEEDED)
            continue
        evidence.append(
            EvidenceRecord(
                type=evidence_type,
                start_byte=_byte_offset(text, start),
                end_byte=_byte_offset(text, end),
                location="source_content",
            )
        )
        total_evidence += 1
    complete = not reasons
    return Extraction(
        candidates=tuple(
            CandidateReference(
                path=path,
                first_seen=index,
                evidence=tuple(paths[path]),
                complete=complete,
            )
            for index, path in enumerate(order)
        ),
        rejected=rejected,
        reasons=tuple(reasons),
        rejection_counts=tuple(
            RejectionCount(reason=reason, count=count)
            for reason, count in sorted(rejection_counts.items(), key=lambda item: item[0].value)
        ),
    )

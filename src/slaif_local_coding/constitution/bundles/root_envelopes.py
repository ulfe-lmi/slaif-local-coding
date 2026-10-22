"""Versioned Codex project-instructions root envelope observation (D01/D02).

The versioned delimiter contract (``ENVELOPE_FORMAT``) is documented in
``docs/CACHE-OBSERVATION-CONTRACT.md``.  Parsing is linear and bounded; it
preserves exact source bytes, never strips source, and reports typed
limitations instead of choosing between competing occurrences.

Recognition law:

- only a Responses ``role="user"`` ``input_text`` item whose text **starts at
  character 0** with the exact header can be a root occurrence; assistant,
  developer, system and tool text, and quoted marker prose at any later
  offset, never create root authority;
- the exact inner content bytes (between the versioned delimiters) are the
  source: the optional environment-context tail and adjacent items are
  excluded from the source bytes and preserved as spans;
- repeated byte- and scope-identical roots are idempotent (every occurrence
  span is preserved); same-scope differing content is exposed as version
  candidates for later temporal resolution; differing scopes are an explicit
  conflict;
- malformed, duplicate/nested-ambiguous delimiters, unclosed tails,
  unsupported shapes and over-bound input yield typed limitations.
"""

from __future__ import annotations

from typing import Any

from ..bundles.observation_models import (
    ENVELOPE_FORMAT,
    CharSpan,
    Limitation,
    ObservationBounds,
    OccurrenceKind,
    RootOccurrence,
    RootScanResult,
    RootStatus,
    VersionCandidate,
    contains_lone_surrogates,
    sha256_hex,
)

_HEADER_PREFIX = "# AGENTS.md instructions for "
_OPEN = "<INSTRUCTIONS>"
_CLOSE = "</INSTRUCTIONS>"
_ENV_PREFIX = "<environment_context>"
_ENV_SUFFIX = "</environment_context>"


def _label_ok(label: str, max_label_bytes: int) -> bool:
    # The declared bound is in UTF-8 bytes, not Unicode characters:
    # "/\u00e9\u00e9\u00e9\u00e9" is 9 bytes and exceeds an 8-byte limit.
    if not label or len(label.encode("utf-8")) > max_label_bytes:
        return False
    if any(ord(c) < 0x20 or ord(c) == 0x7F for c in label):
        return False
    return True


def _is_environment_block(text: str) -> bool:
    """Well-formed standalone environment block (separate-item form)."""

    if not (text.startswith(_ENV_PREFIX) and text.endswith(_ENV_SUFFIX)):
        return False
    body = text[len(_ENV_PREFIX) : -len(_ENV_SUFFIX)]
    return body.startswith(("\r\n", "\n")) and body.endswith("\n")


def _line_break(text: str, pos: int) -> int | None:
    """Return the position after the LF or CRLF at *pos*, else ``None``."""

    if text[pos : pos + 1] == "\n":
        return pos + 1
    if text[pos : pos + 2] == "\r\n":
        return pos + 2
    return None


def _parse_item(
    text: str, bounds: ObservationBounds
) -> tuple[RootOccurrence | None, RootOccurrence | None]:
    """Classify one user input_text item.

    Returns ``(root, None)`` for a valid root, ``(None, limitation)`` when the
    item carries envelope-like or environment text that failed, and
    ``(None, None)`` for ordinary non-root content (including well-formed
    standalone environment blocks, which the caller classifies).
    """

    def _limitation(kind: OccurrenceKind, reason: Limitation) -> tuple[None, RootOccurrence]:
        return None, RootOccurrence(
            kind=kind, location="", status=RootStatus.UNSUPPORTED, reasons=(reason,)
        )

    if len(text) > bounds.max_item_chars:
        return _limitation(OccurrenceKind.NON_ROOT, Limitation.OVER_BOUND)
    if contains_lone_surrogates(text):
        return _limitation(OccurrenceKind.NON_ROOT, Limitation.MALFORMED_UNICODE)

    if not text.startswith(_HEADER_PREFIX):
        if "# AGENTS.md instructions for " in text:
            return _limitation(OccurrenceKind.MARKER_PROSE, Limitation.MARKER_MISPLACED)
        if text.startswith(_ENV_PREFIX):
            if len(text) <= bounds.max_environment_chars and _is_environment_block(text):
                return None, None
            return _limitation(OccurrenceKind.NON_ROOT, Limitation.MALFORMED_ENVIRONMENT)
        return None, None

    # Header contract: prefix + label + T1 + T2 + <INSTRUCTIONS> + T3, where
    # each T is LF or CRLF and T2 is the blank line.
    nl = text.find("\n", len(_HEADER_PREFIX))
    if nl == -1:
        return _limitation(OccurrenceKind.ROOT, Limitation.MALFORMED_DELIMITERS)
    label_end = nl
    if label_end > len(_HEADER_PREFIX) and text[label_end - 1] == "\r":
        label_end -= 1
    label = text[len(_HEADER_PREFIX) : label_end]
    if not _label_ok(label, bounds.max_label_bytes):
        return _limitation(OccurrenceKind.ROOT, Limitation.INVALID_SCOPE_LABEL)
    pos = _line_break(text, nl)
    if pos is None:
        return _limitation(OccurrenceKind.ROOT, Limitation.MALFORMED_DELIMITERS)
    pos2 = _line_break(text, pos)  # the blank line
    if pos2 is None or not text.startswith(_OPEN, pos2):
        return _limitation(OccurrenceKind.ROOT, Limitation.MALFORMED_DELIMITERS)
    start = _line_break(text, pos2 + len(_OPEN))
    if start is None:
        return _limitation(OccurrenceKind.ROOT, Limitation.MALFORMED_DELIMITERS)

    # First closing tag on its own line; an earlier literal is ambiguous and
    # never retried (the legacy detector has the same law).
    end = text.find(_CLOSE, start)
    if end == -1:
        return _limitation(OccurrenceKind.ROOT, Limitation.UNCLOSED_TAIL)
    if end < start or text[end - 1] != "\n":
        return _limitation(OccurrenceKind.ROOT, Limitation.MALFORMED_DELIMITERS)
    content_end = end - 1
    if content_end > start and text[content_end - 1] == "\r":
        content_end -= 1
    content = text[start:content_end]
    if _OPEN in content:
        return _limitation(OccurrenceKind.ROOT, Limitation.DUPLICATE_MARKER)

    tail = text[end + len(_CLOSE) :]
    envelope_end = end + len(_CLOSE)
    if tail not in ("", "\n", "\r\n"):
        environment = tail
        if environment.startswith("\r\n"):
            environment = environment[2:]
        elif environment.startswith("\n"):
            environment = environment[1:]
        if (
            not environment.startswith(_ENV_PREFIX)
            or not environment.endswith(_ENV_SUFFIX)
            or len(environment) > bounds.max_environment_chars
        ):
            return _limitation(OccurrenceKind.ROOT, Limitation.MALFORMED_DELIMITERS)
        body = environment[len(_ENV_PREFIX) : -len(_ENV_SUFFIX)]
        if not body.startswith(("\r\n", "\n")) or not body.endswith("\n"):
            return _limitation(OccurrenceKind.ROOT, Limitation.MALFORMED_DELIMITERS)
        envelope_end = len(text)

    return (
        RootOccurrence(
            kind=OccurrenceKind.ROOT,
            location="",
            status=RootStatus.OK,
            scope_label=label,
            content_span=CharSpan(start=start, end=content_end),
            envelope_span=CharSpan(start=0, end=envelope_end),
            digest=sha256_hex(content),
            byte_length=len(content.encode("utf-8")),
        ),
        None,
    )


def scan_root_envelopes(payload: dict[str, Any], bounds: ObservationBounds) -> RootScanResult:
    """Classify every user input_text item in a Responses payload (D01/D02).

    Only the Responses ``input`` array is a recognized root endpoint in this
    slice; any other endpoint is reported as ``UNSUPPORTED_ENDPOINT`` without
    scanning (the legacy detector keeps its own behavior on the legacy path).
    """

    if not isinstance(payload.get("input"), list):
        return RootScanResult(
            status=RootStatus.UNSUPPORTED,
            conflicts=(Limitation.UNSUPPORTED_ENDPOINT,),
        )

    items: list[tuple[str, str]] = []
    for index, parent in enumerate(payload["input"]):
        if not isinstance(parent, dict) or parent.get("role") != "user":
            continue
        content = parent.get("content")
        if not isinstance(content, list):
            continue
        for item_index, item in enumerate(content):
            if not isinstance(item, dict) or item.get("type") != "input_text":
                continue
            text = item.get("text")
            if not isinstance(text, str):
                continue
            items.append((f"$.input[{index}].content[{item_index}]", text))
    if len(items) > bounds.max_items:
        return RootScanResult(
            status=RootStatus.UNSUPPORTED,
            conflicts=(Limitation.OVER_BOUND,),
            scanned_items=len(items),
        )

    occurrences: list[RootOccurrence] = []
    for location, text in items:
        root, limitation = _parse_item(text, bounds)
        if root is not None:
            occurrences.append(root.model_copy(update={"location": location}))
        elif limitation is not None:
            occurrences.append(limitation.model_copy(update={"location": location}))
        else:
            is_env = text.startswith(_ENV_PREFIX)
            kind = OccurrenceKind.ENVIRONMENT if is_env else OccurrenceKind.NON_ROOT
            occurrences.append(RootOccurrence(kind=kind, location=location, status=RootStatus.OK))

    valid = [o for o in occurrences if o.kind is OccurrenceKind.ROOT and o.status is RootStatus.OK]
    by_scope: dict[str, dict[str, list[str]]] = {}
    for occ in valid:
        assert occ.scope_label is not None and occ.digest is not None
        by_scope.setdefault(occ.scope_label, {}).setdefault(occ.digest, []).append(occ.location)

    conflicts: tuple[Limitation, ...] = ()
    candidates: tuple[VersionCandidate, ...] = ()
    if len(by_scope) > 1:
        conflicts = (Limitation.COMPETING_ROOT_SCOPES,)
        status = RootStatus.CONFLICT
    elif len(by_scope) == 1:
        scope, digests = next(iter(by_scope.items()))
        if len(digests) == 1:
            status = RootStatus.OK
        else:
            status = RootStatus.VERSION_CANDIDATES
            candidates = tuple(
                VersionCandidate(
                    scope_label=scope,
                    digest=digest,
                    occurrences=tuple(locations),
                )
                for digest, locations in sorted(digests.items())
            )
    else:
        status = RootStatus.NO_ROOT

    return RootScanResult(
        envelope_format=ENVELOPE_FORMAT,
        status=status,
        occurrences=tuple(occurrences),
        version_candidates=candidates,
        conflicts=conflicts,
        scanned_items=len(items),
    )

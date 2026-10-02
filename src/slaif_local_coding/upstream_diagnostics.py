"""Bounded private classification of upstream HTTP error causes (order 015-a, P01).

The adapter forwards only a generic public error for upstream HTTP
rejections.  This module adds a *private, content-safe* cause classifier so
operators can distinguish authentication, rate-limit, image-count, and
context-length rejections without the adapter ever returning, logging,
persisting, or labeling with provider text.

Laws implemented here (order 015-a, workstream A):

* Only a bounded complete JSON object in explicitly supported provider
  shapes is inspected: the top-level ``error`` object (or, when absent, the
  top-level object itself) and the fixed string fields ``code``, ``type``,
  ``param``, and ``message``.  Numeric, null, collection, or otherwise
  unexpected field values are ignored, never raised.
* Raw strings are examined transiently only through explicit fixed matcher
  tables (exact matches for ``code``/``type``/``param``, fixed phrases for
  ``message``).  They are never returned, logged, persisted, or used as
  metric labels.
* The result is the closed enum :class:`UpstreamErrorReason`.  Status 401/
  403 alone establishes ``authentication``, 429 alone establishes
  ``rate_limit``, and any 5xx status alone establishes ``upstream_5xx``.
  Every other status requires sufficient allowlisted structured or
  fixed-pattern evidence; unknown, malformed, incomplete, oversized,
  unsupported, or ambiguous evidence is ``unknown``.
* Evidence from two or more *different* categories is ambiguous and
  normalizes to ``unknown`` for statuses that do not independently
  classify.
"""

from __future__ import annotations

import json
from enum import StrEnum
from typing import Any

from .json_structure import JsonNestingTooDeep, enforce_json_nesting

#: Bounded container nesting for the diagnostic parse.  Classification needs
#: at most the top-level object plus the ``error`` object; the bound is a
#: hard ceiling, not a tuning knob.
MAX_DIAGNOSTIC_JSON_DEPTH = 32


class UpstreamErrorReason(StrEnum):
    """Closed private classification of one upstream HTTP rejection."""

    AUTHENTICATION = "authentication"
    RATE_LIMIT = "rate_limit"
    IMAGE_COUNT_LIMIT = "image_count_limit"
    CONTEXT_LENGTH_LIMIT = "context_length_limit"
    MALFORMED_INPUT = "malformed_input"
    UPSTREAM_5XX = "upstream_5xx"
    UNKNOWN = "unknown"


#: HTTP statuses that establish their category by themselves.  Any 5xx
#: status establishes :attr:`UpstreamErrorReason.UPSTREAM_5XX` by range.
_STATUS_REASONS: dict[int, UpstreamErrorReason] = {
    401: UpstreamErrorReason.AUTHENTICATION,
    403: UpstreamErrorReason.AUTHENTICATION,
    429: UpstreamErrorReason.RATE_LIMIT,
}

#: Exact-match table for the allowlisted ``code`` field (lowercased).
_CODE_REASONS: dict[str, UpstreamErrorReason] = {
    # image-count evidence
    "image_count_limit": UpstreamErrorReason.IMAGE_COUNT_LIMIT,
    "image_count_exceeded": UpstreamErrorReason.IMAGE_COUNT_LIMIT,
    "image_limit": UpstreamErrorReason.IMAGE_COUNT_LIMIT,
    "image_limit_exceeded": UpstreamErrorReason.IMAGE_COUNT_LIMIT,
    "max_images": UpstreamErrorReason.IMAGE_COUNT_LIMIT,
    "max_images_exceeded": UpstreamErrorReason.IMAGE_COUNT_LIMIT,
    "max_num_images": UpstreamErrorReason.IMAGE_COUNT_LIMIT,
    "too_many_images": UpstreamErrorReason.IMAGE_COUNT_LIMIT,
    # context-length evidence
    "context_length": UpstreamErrorReason.CONTEXT_LENGTH_LIMIT,
    "context_length_exceeded": UpstreamErrorReason.CONTEXT_LENGTH_LIMIT,
    "context_length_limit": UpstreamErrorReason.CONTEXT_LENGTH_LIMIT,
    "context_limit_exceeded": UpstreamErrorReason.CONTEXT_LENGTH_LIMIT,
    "max_context_length": UpstreamErrorReason.CONTEXT_LENGTH_LIMIT,
    "max_context_length_exceeded": UpstreamErrorReason.CONTEXT_LENGTH_LIMIT,
    "maximum_context_length": UpstreamErrorReason.CONTEXT_LENGTH_LIMIT,
    "maximum_context_length_exceeded": UpstreamErrorReason.CONTEXT_LENGTH_LIMIT,
    "maximum_tokens_exceeded": UpstreamErrorReason.CONTEXT_LENGTH_LIMIT,
    "max_tokens_exceeded": UpstreamErrorReason.CONTEXT_LENGTH_LIMIT,
    "token_limit_exceeded": UpstreamErrorReason.CONTEXT_LENGTH_LIMIT,
    # malformed-input / parser evidence
    "invalid_json": UpstreamErrorReason.MALFORMED_INPUT,
    "json_parse_error": UpstreamErrorReason.MALFORMED_INPUT,
    "json_syntax_error": UpstreamErrorReason.MALFORMED_INPUT,
    "malformed_input": UpstreamErrorReason.MALFORMED_INPUT,
    "parser_error": UpstreamErrorReason.MALFORMED_INPUT,
    # explicit auth / rate-limit codes (status-derived where status matches)
    "authentication_error": UpstreamErrorReason.AUTHENTICATION,
    "invalid_api_key": UpstreamErrorReason.AUTHENTICATION,
    "rate_limit_exceeded": UpstreamErrorReason.RATE_LIMIT,
    "rate_limited": UpstreamErrorReason.RATE_LIMIT,
}

#: Exact-match table for the allowlisted ``type`` field (lowercased).
_TYPE_REASONS: dict[str, UpstreamErrorReason] = {
    "context_length_exceeded": UpstreamErrorReason.CONTEXT_LENGTH_LIMIT,
    "context_length_limit": UpstreamErrorReason.CONTEXT_LENGTH_LIMIT,
    "image_count_limit": UpstreamErrorReason.IMAGE_COUNT_LIMIT,
    "invalid_json": UpstreamErrorReason.MALFORMED_INPUT,
    "json_error": UpstreamErrorReason.MALFORMED_INPUT,
    "parser_error": UpstreamErrorReason.MALFORMED_INPUT,
}

#: Exact-match table for the allowlisted ``param`` field (lowercased).
_PARAM_REASONS: dict[str, UpstreamErrorReason] = {
    "context_length": UpstreamErrorReason.CONTEXT_LENGTH_LIMIT,
    "images": UpstreamErrorReason.IMAGE_COUNT_LIMIT,
    "json": UpstreamErrorReason.MALFORMED_INPUT,
    "max_num_images": UpstreamErrorReason.IMAGE_COUNT_LIMIT,
    "max_tokens": UpstreamErrorReason.CONTEXT_LENGTH_LIMIT,
}

#: Fixed phrase table for the allowlisted ``message`` field (lowercased,
#: substring).  Phrases are deliberately fixed and closed; free-form
#: provider text is never retained or echoed.
_MESSAGE_PATTERNS: tuple[tuple[str, UpstreamErrorReason], ...] = (
    ("images allowed per request", UpstreamErrorReason.IMAGE_COUNT_LIMIT),
    ("image limit", UpstreamErrorReason.IMAGE_COUNT_LIMIT),
    ("maximum number of images", UpstreamErrorReason.IMAGE_COUNT_LIMIT),
    ("too many images", UpstreamErrorReason.IMAGE_COUNT_LIMIT),
    ("context length exceeded", UpstreamErrorReason.CONTEXT_LENGTH_LIMIT),
    ("context_length", UpstreamErrorReason.CONTEXT_LENGTH_LIMIT),
    ("maximum context length", UpstreamErrorReason.CONTEXT_LENGTH_LIMIT),
    ("maximum number of tokens", UpstreamErrorReason.CONTEXT_LENGTH_LIMIT),
    ("too many tokens", UpstreamErrorReason.CONTEXT_LENGTH_LIMIT),
    ("invalid json", UpstreamErrorReason.MALFORMED_INPUT),
    ("malformed json", UpstreamErrorReason.MALFORMED_INPUT),
    ("json parse", UpstreamErrorReason.MALFORMED_INPUT),
    ("malformed request", UpstreamErrorReason.MALFORMED_INPUT),
)

_ALLOWLISTED_FIELDS = ("code", "type", "param", "message")


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON object key")
        result[key] = value
    return result


def _parse_bounded_object(raw: bytes, max_json_depth: int) -> dict[str, Any] | None:
    """Parse at most one bounded top-level JSON object; never raises.

    Returns ``None`` for empty, non-UTF-8, non-object, duplicate-key,
    non-finite, or over-deep content.
    """
    if not raw:
        return None
    try:
        enforce_json_nesting(raw, max_json_depth)
    except (JsonNestingTooDeep, ValueError):
        return None
    try:
        value = json.loads(
            raw.decode("utf-8"),
            object_pairs_hook=_reject_duplicate_keys,
            parse_constant=lambda _token: (_ for _ in ()).throw(
                ValueError("non-finite JSON number")
            ),
        )
    except (UnicodeDecodeError, json.JSONDecodeError, RecursionError, ValueError):
        return None
    if not isinstance(value, dict):
        return None
    return value


def _error_object(payload: dict[str, Any]) -> dict[str, Any]:
    error = payload.get("error")
    return error if isinstance(error, dict) else payload


def classify_upstream_error(
    status_code: int,
    body: bytes | None,
    *,
    max_json_depth: int = MAX_DIAGNOSTIC_JSON_DEPTH,
) -> UpstreamErrorReason:
    """Normalize one upstream HTTP rejection to the closed private reason.

    ``body`` is the bounded diagnostic slice already read from the upstream
    (or ``None`` when nothing was read or the status classifies alone).
    The function never raises and never exposes provider text.
    """
    if status_code in _STATUS_REASONS:
        return _STATUS_REASONS[status_code]
    if 500 <= status_code <= 599:
        return UpstreamErrorReason.UPSTREAM_5XX
    if body is None:
        return UpstreamErrorReason.UNKNOWN
    payload = _parse_bounded_object(body, max_json_depth)
    if payload is None:
        return UpstreamErrorReason.UNKNOWN
    error = _error_object(payload)
    reasons: set[UpstreamErrorReason] = set()
    for field in _ALLOWLISTED_FIELDS:
        value = error.get(field)
        if not isinstance(value, str):
            continue
        lowered = value.strip().lower()
        if not lowered:
            continue
        if field == "code":
            if lowered in _CODE_REASONS:
                reasons.add(_CODE_REASONS[lowered])
        elif field == "type":
            if lowered in _TYPE_REASONS:
                reasons.add(_TYPE_REASONS[lowered])
        elif field == "param":
            if lowered in _PARAM_REASONS:
                reasons.add(_PARAM_REASONS[lowered])
        else:  # message: fixed phrases only
            for phrase, reason in _MESSAGE_PATTERNS:
                if phrase in lowered:
                    reasons.add(reason)
    if len(reasons) == 1:
        return reasons.pop()
    return UpstreamErrorReason.UNKNOWN


def status_class(status_code: int) -> str:
    """Bounded status-class label for metric use: ``4xx`` or ``5xx``."""
    return "5xx" if 500 <= status_code <= 599 else "4xx"

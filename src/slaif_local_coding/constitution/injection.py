"""Endpoint-scoped, idempotent transforms for objective-003 library use.

These functions are intentionally not imported by public request handlers.  They
copy the supported OpenAI-compatible envelopes and alter only the stable
instruction location; image items and all unrelated values remain untouched.
"""

from __future__ import annotations

import copy
from collections.abc import Mapping
from enum import StrEnum
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from .working_set import WORKING_SET_RENDER_VERSION, WorkingSetSuccess

_GENERIC_OPEN_MARKER = "<SLAIF_RECONSTRUCTED_CONSTITUTION"
_GENERIC_CLOSE_PREFIX = "</SLAIF_RECONSTRUCTED_CONSTITUTION"
_GENERIC_CLOSE_MARKER = _GENERIC_CLOSE_PREFIX + ">"


def _opening_marker() -> str:
    return f'{_GENERIC_OPEN_MARKER} render_version="{WORKING_SET_RENDER_VERSION}">'


class InjectionOutcome(StrEnum):
    INSERTED = "inserted"
    UPDATED = "updated"
    IDEMPOTENT = "idempotent"


class InjectionFailureReason(StrEnum):
    UNSUPPORTED_SHAPE = "unsupported_shape"
    MALFORMED_MARKER = "malformed_marker"
    CONFLICTING_MARKER = "conflicting_marker"
    DUPLICATE_MARKER = "duplicate_marker"
    BOUNDS_EXCEEDED = "bounds_exceeded"


class InjectionResult(BaseModel):
    """Safe counts only; the transformed envelope is returned separately."""

    model_config = ConfigDict(frozen=True, extra="forbid")
    endpoint: Literal["/v1/responses", "/v1/chat/completions"]
    outcome: InjectionOutcome
    rendered_bytes: int = Field(ge=1)
    included_dependencies: int = Field(ge=0)
    missing_dependencies: int = Field(ge=0)
    omitted_dependencies: int = Field(ge=0)


class ConstitutionInjectionError(Exception):
    """Typed fail-closed injection error carrying no request-derived detail."""

    def __init__(self, reason: InjectionFailureReason) -> None:
        super().__init__(reason.value)
        self.reason = reason


class _MarkerFound:
    __slots__ = ("inner", "path")

    def __init__(self, path: tuple[Any, ...], inner: str) -> None:
        self.path = path
        self.inner = inner


def _scan(
    value: Any,
    *,
    path: tuple[Any, ...],
    depth: int,
    max_depth: int,
    counters: list[int],
    found: list[_MarkerFound],
) -> None:
    """Find exact and near-miss markers anywhere without interpreting payloads."""
    if depth > max_depth:
        raise ConstitutionInjectionError(InjectionFailureReason.BOUNDS_EXCEEDED)
    counters[0] += 1
    if counters[0] > counters[1]:
        raise ConstitutionInjectionError(InjectionFailureReason.BOUNDS_EXCEEDED)

    if isinstance(value, str):
        cursor = 0
        while True:
            positions = (
                value.find(_GENERIC_OPEN_MARKER, cursor),
                value.find(_GENERIC_CLOSE_PREFIX, cursor),
            )
            starts = [position for position in positions if position != -1]
            if not starts:
                return
            start = min(starts)
            if value.startswith(_GENERIC_CLOSE_PREFIX, start) and not value.startswith(
                _GENERIC_CLOSE_MARKER, start
            ):
                raise ConstitutionInjectionError(InjectionFailureReason.MALFORMED_MARKER)
            if value.startswith(_GENERIC_CLOSE_MARKER, start):
                raise ConstitutionInjectionError(InjectionFailureReason.MALFORMED_MARKER)
            if not value.startswith(_opening_marker(), start):
                raise ConstitutionInjectionError(InjectionFailureReason.MALFORMED_MARKER)
            close = value.find(_GENERIC_CLOSE_MARKER, start + len(_opening_marker()))
            if close == -1:
                raise ConstitutionInjectionError(InjectionFailureReason.MALFORMED_MARKER)
            end = close + len(_GENERIC_CLOSE_MARKER)
            inner = value[start + len(_opening_marker()) : close]
            if inner.startswith("\n"):
                inner = inner[1:]
            if inner.endswith("\n"):
                inner = inner[:-1]
            found.append(_MarkerFound(path, inner))
            cursor = end
        return

    if isinstance(value, Mapping):
        for key, child in value.items():
            _scan(
                child,
                path=(*path, key),
                depth=depth + 1,
                max_depth=max_depth,
                counters=counters,
                found=found,
            )
        return

    if isinstance(value, list):
        for index, child in enumerate(value):
            _scan(
                child,
                path=(*path, index),
                depth=depth + 1,
                max_depth=max_depth,
                counters=counters,
                found=found,
            )


def _validate_found(
    working_set: WorkingSetSuccess, found: list[_MarkerFound], expected_path: tuple[Any, ...]
) -> None:
    if len(found) > 1:
        raise ConstitutionInjectionError(InjectionFailureReason.DUPLICATE_MARKER)
    if not found or found[0].path != expected_path:
        raise ConstitutionInjectionError(InjectionFailureReason.CONFLICTING_MARKER)
    opening = _opening_marker()
    reconstructed = f"{opening}\n{found[0].inner}\n{_GENERIC_CLOSE_MARKER}"
    if reconstructed != working_set.rendered_text:
        raise ConstitutionInjectionError(InjectionFailureReason.CONFLICTING_MARKER)


def _result(
    endpoint: Literal["/v1/responses", "/v1/chat/completions"],
    outcome: InjectionOutcome,
    working_set: WorkingSetSuccess,
) -> InjectionResult:
    included = sum(item.status.value == "included" for item in working_set.dependencies)
    missing = sum(item.status.value == "missing" for item in working_set.dependencies)
    omitted = sum(item.status.value == "omitted" for item in working_set.dependencies)
    return InjectionResult(
        endpoint=endpoint,
        outcome=outcome,
        rendered_bytes=working_set.rendered_bytes,
        included_dependencies=included,
        missing_dependencies=missing,
        omitted_dependencies=omitted,
    )


def inject_responses(
    payload: dict[str, Any],
    working_set: WorkingSetSuccess,
    *,
    max_depth: int,
    max_nodes: int,
) -> tuple[dict[str, Any], InjectionResult]:
    """Insert or deterministically combine top-level Responses instructions."""
    if not isinstance(payload, dict):
        raise ConstitutionInjectionError(InjectionFailureReason.UNSUPPORTED_SHAPE)

    copied = copy.deepcopy(payload)
    found: list[_MarkerFound] = []
    counters = [0, max_nodes]
    _scan(
        copied,
        path=(),
        depth=0,
        max_depth=max_depth,
        counters=counters,
        found=found,
    )
    expected_path: tuple[Any, ...] = ("instructions",)
    if found:
        _validate_found(working_set, found, expected_path)
        return copied, _result("/v1/responses", InjectionOutcome.IDEMPOTENT, working_set)

    existing = copied.get("instructions")
    if existing is not None and not isinstance(existing, str):
        raise ConstitutionInjectionError(InjectionFailureReason.UNSUPPORTED_SHAPE)
    if existing is None:
        copied["instructions"] = working_set.rendered_text
        outcome = InjectionOutcome.INSERTED
    else:
        copied["instructions"] = f"{working_set.rendered_text}\n\n{existing}"
        outcome = InjectionOutcome.UPDATED
    return copied, _result("/v1/responses", outcome, working_set)


def inject_chat_completions(
    payload: dict[str, Any],
    working_set: WorkingSetSuccess,
    *,
    max_depth: int,
    max_nodes: int,
) -> tuple[dict[str, Any], InjectionResult]:
    """Insert one stable system instruction before all existing messages."""
    if not isinstance(payload, dict):
        raise ConstitutionInjectionError(InjectionFailureReason.UNSUPPORTED_SHAPE)

    copied = copy.deepcopy(payload)
    found: list[_MarkerFound] = []
    counters = [0, max_nodes]
    _scan(
        copied,
        path=(),
        depth=0,
        max_depth=max_depth,
        counters=counters,
        found=found,
    )
    expected_path: tuple[Any, ...] = ("messages", 0, "content")
    if found:
        _validate_found(working_set, found, expected_path)
        return copied, _result("/v1/chat/completions", InjectionOutcome.IDEMPOTENT, working_set)

    messages = copied.get("messages")
    if not isinstance(messages, list) or not all(isinstance(item, dict) for item in messages):
        raise ConstitutionInjectionError(InjectionFailureReason.UNSUPPORTED_SHAPE)
    copied["messages"] = [
        {"role": "system", "content": working_set.rendered_text},
        *messages,
    ]
    return copied, _result("/v1/chat/completions", InjectionOutcome.INSERTED, working_set)

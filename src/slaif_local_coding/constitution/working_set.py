"""Pure, bounded selection and rendering of validated constitutional indexes.

The selector is deliberately library-only.  It performs no filesystem, network,
model, cache, or repository access: callers supply already validated indexes and
the selector never treats those indexes as authoritative source material.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from enum import IntEnum, StrEnum
from pathlib import PurePosixPath
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from .compiler_models import (
    AcquisitionUrgency,
    CompiledDependency,
    CompiledIndex,
    ConstitutionalClass,
)

WORKING_SET_SCHEMA_VERSION = "working-set-v1"
WORKING_SET_RENDER_VERSION = "constitution-render-v1"
SOURCE_AUTHORITY_MARKER = (
    "Reconstructed context; repository/Git/GitHub/source files override this block."
)


class WorkingSetStatus(StrEnum):
    INCLUDED = "included"
    MISSING = "missing"
    OMITTED = "omitted"


class WorkingSetOmissionReason(StrEnum):
    CLASS_BELOW_POLICY = "classification_below_policy"
    BUDGET_EXCEEDED = "budget_exceeded"
    ENTRY_TOO_LARGE = "entry_too_large"
    NOT_ACQUIRED_OPTIONAL = "missing_optional"


class WorkingSetFailureReason(StrEnum):
    INVALID_INPUT = "invalid_input"
    DEPENDENCY_BUDGET_EXCEEDED = "dependency_budget_exceeded"
    ACQUISITION_BUDGET_EXCEEDED = "acquisition_budget_exceeded"
    ESSENTIAL_OVERFLOW = "essential_overflow"
    UNSAFE_MARKER_COLLISION = "unsafe_marker_collision"


class _UrgencyRank(IntEnum):
    IMMEDIATE = 0
    NEXT_TURN = 1
    BACKGROUND = 2
    NONE = 3


class WorkingSetPolicy(BaseModel):
    """Finite selector policy; every byte and entry bound is explicit."""

    model_config = ConfigDict(frozen=True, extra="forbid")
    max_rendered_bytes: int = Field(default=16_384, ge=256, le=4_194_304)
    max_dependencies: int = Field(default=128, ge=1, le=4_096)
    max_entries: int = Field(default=128, ge=1, le=4_096)
    max_acquisition_instructions: int = Field(default=128, ge=1, le=4_096)
    max_entry_bytes: int = Field(default=8_192, ge=128, le=1_048_576)
    include_p2_p3: bool = True

    @model_validator(mode="after")
    def bounded(self) -> WorkingSetPolicy:
        if self.max_entry_bytes > self.max_rendered_bytes:
            raise ValueError("working-set entry budget cannot exceed rendered budget")
        if self.max_entries > self.max_dependencies:
            raise ValueError("working-set included-entry budget cannot exceed dependency budget")
        return self


class WorkingSetMetadata(BaseModel):
    """Caller-controlled stable policy label; never an opaque runtime secret."""

    model_config = ConfigDict(frozen=True, extra="forbid")
    policy_version: str = Field(default="foundation-v1", min_length=1, max_length=64)


class WorkingSetDependency(BaseModel):
    """Bounded dependency state with the two independent compiler scores intact."""

    model_config = ConfigDict(frozen=True, extra="forbid")
    path: str = Field(min_length=1, max_length=512)
    classification: ConstitutionalClass
    status: WorkingSetStatus
    reference_confidence: float = Field(ge=0, le=1, allow_inf_nan=False)
    constitutional_priority: float = Field(ge=0, le=100, allow_inf_nan=False)
    acquisition_urgency: AcquisitionUrgency
    reason: WorkingSetOmissionReason | None = None


class AcquisitionInstruction(BaseModel):
    """Exact safe logical path to acquire through ordinary client-local tools."""

    model_config = ConfigDict(frozen=True, extra="forbid")
    path: str = Field(min_length=1, max_length=512)
    urgency: AcquisitionUrgency
    instruction: str = Field(min_length=1, max_length=768)


class WorkingSetSuccess(BaseModel):
    """A complete rendered working set plus safe metrics—never cache mechanics."""

    model_config = ConfigDict(frozen=True, extra="forbid")
    outcome: Literal["success"] = "success"
    rendered_text: str = Field(min_length=1, repr=False)
    content_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    rendered_bytes: int = Field(ge=1)
    schema_version: str = WORKING_SET_SCHEMA_VERSION
    render_version: str = WORKING_SET_RENDER_VERSION
    policy_version: str = Field(min_length=1, max_length=64)
    root_logical_path: str = Field(min_length=1, max_length=512)
    root_source_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    root_index_version: str = Field(min_length=1, max_length=64)
    dependencies: tuple[WorkingSetDependency, ...]
    acquisition_instructions: tuple[AcquisitionInstruction, ...]
    status_reasons: tuple[str, ...] = ()
    source_authority_statement: str = SOURCE_AUTHORITY_MARKER


class WorkingSetFailure(BaseModel):
    """Typed failure that preserves no unsafe partial normative rendering."""

    model_config = ConfigDict(frozen=True, extra="forbid")
    outcome: Literal["failure"] = "failure"
    reason: WorkingSetFailureReason
    detail: str = Field(default="", max_length=240)
    dependencies: tuple[WorkingSetDependency, ...] = ()
    acquisition_instructions: tuple[AcquisitionInstruction, ...] = ()


class WorkingSetSelectionError(Exception):
    """Raised by :func:`select_working_set` with a structured public failure."""

    def __init__(self, failure: WorkingSetFailure) -> None:
        super().__init__(failure.reason.value)
        self.failure = failure


def _dependency_block(index: CompiledIndex) -> str:
    value: dict[str, Any] = {
        "schema_version": index.schema_version,
        "compiler_version": index.compiler_version,
        "prompt_policy_version": index.prompt_policy_version,
        "model": index.model,
        "logical_path": index.source_logical_path,
        "source_sha256": index.source_sha256,
        "summary": index.summary,
        "rules": [rule.model_dump(mode="json") for rule in index.rules],
        "roles": list(index.roles),
        "authorities": list(index.authorities),
        "source_of_truth_boundaries": list(index.source_of_truth_boundaries),
        "ordering_constraints": list(index.ordering_constraints),
        "exceptions": list(index.exceptions),
        "reread_triggers": list(index.reread_triggers),
    }
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _root_block(index: CompiledIndex) -> str:
    return _dependency_block(index)


def _acquisition_text(item: CompiledDependency) -> str:
    if item.acquisition_urgency == AcquisitionUrgency.IMMEDIATE:
        action = "Read this file with ordinary local tools before substantive mutation."
    elif item.acquisition_urgency == AcquisitionUrgency.NEXT_TURN:
        action = "Read this file with ordinary local tools on the next turn."
    elif item.acquisition_urgency == AcquisitionUrgency.BACKGROUND:
        action = "Read this file with ordinary local tools when relevant."
    else:
        action = "Read this file with ordinary local tools when needed."
    return f"Acquire {item.path}: {action}"


def _safe_dependency_key(key: str, index: CompiledIndex) -> bool:
    if key != index.source_logical_path or "\x00" in key or "\\" in key:
        return False
    try:
        parsed = PurePosixPath(key)
    except (TypeError, ValueError):
        return False
    parts = parsed.parts
    return (
        not key.startswith(("/", "\\"))
        and not key.endswith("/")
        and all(part not in {"", ".", ".."} for part in parts)
        and key.encode("utf-8", errors="surrogatepass") == key.encode("utf-8")
    )


def _sort_p1(
    dependencies: list[CompiledDependency],
    acquired_dependencies: Mapping[str, CompiledIndex],
) -> list[CompiledDependency]:
    return sorted(
        dependencies,
        key=lambda item: (
            _UrgencyRank[item.acquisition_urgency.name]
            if item.path not in acquired_dependencies
            else 0,
            item.path,
            acquired_dependencies[item.path].source_sha256
            if item.path in acquired_dependencies
            else "",
            item.reference_confidence,
        ),
    )


def _sort_optional(
    dependencies: list[CompiledDependency],
    acquired_dependencies: Mapping[str, CompiledIndex],
) -> list[CompiledDependency]:
    return sorted(
        dependencies,
        key=lambda item: (
            -item.constitutional_priority,
            item.path,
            acquired_dependencies[item.path].source_sha256
            if item.path in acquired_dependencies
            else "",
        ),
    )


def select_working_set(
    root: CompiledIndex,
    acquired_dependencies: Mapping[str, CompiledIndex],
    *,
    policy: WorkingSetPolicy,
    metadata: WorkingSetMetadata,
) -> WorkingSetSuccess:
    """Select, order, and render one deterministic bounded working set.

    Failures are raised as :class:`WorkingSetSelectionError` and carry a typed
    :class:`WorkingSetFailure`. The root and every P1 dependency are essential;
    optional entries are omitted whole rather than truncated.
    """

    if len(root.dependencies) > policy.max_dependencies:
        raise WorkingSetSelectionError(
            WorkingSetFailure(reason=WorkingSetFailureReason.DEPENDENCY_BUDGET_EXCEEDED)
        )
    if len({item.path for item in root.dependencies}) != len(root.dependencies):
        raise WorkingSetSelectionError(
            WorkingSetFailure(
                reason=WorkingSetFailureReason.INVALID_INPUT, detail="duplicate dependency path"
            )
        )
    if any(item.classification == ConstitutionalClass.P0_ROOT for item in root.dependencies):
        raise WorkingSetSelectionError(
            WorkingSetFailure(
                reason=WorkingSetFailureReason.INVALID_INPUT, detail="non-root P0 dependency"
            )
        )

    supplied_by_path = {item.path: item for item in root.dependencies}
    if set(acquired_dependencies) - set(supplied_by_path):
        raise WorkingSetSelectionError(
            WorkingSetFailure(
                reason=WorkingSetFailureReason.INVALID_INPUT, detail="unknown acquired path"
            )
        )
    for key, index in acquired_dependencies.items():
        declaration = supplied_by_path.get(key)
        if (
            declaration is None
            or not _safe_dependency_key(key, index)
            or index.source_logical_path != key
        ):
            raise WorkingSetSelectionError(
                WorkingSetFailure(
                    reason=WorkingSetFailureReason.INVALID_INPUT, detail="unsafe acquired path"
                )
            )

    # A dependency declaration has no source hash; its exact logical path is the
    # acquisition identity. Supplied content is validated by its own index hash.
    p1 = [
        item
        for item in root.dependencies
        if item.classification == ConstitutionalClass.P1_DELEGATED_OR_SECURITY
    ]
    optional = [
        item
        for item in root.dependencies
        if item.classification
        in {
            ConstitutionalClass.P2_BINDING_PROCEDURE,
            ConstitutionalClass.P3_ARCHITECTURE_OR_CONTRACT,
        }
    ]
    background = [
        item
        for item in root.dependencies
        if item.classification == ConstitutionalClass.P4_BACKGROUND
    ]
    if len(p1) > policy.max_acquisition_instructions:
        raise WorkingSetSelectionError(
            WorkingSetFailure(reason=WorkingSetFailureReason.ACQUISITION_BUDGET_EXCEEDED)
        )

    opening_marker = (
        f'<SLAIF_RECONSTRUCTED_CONSTITUTION render_version="{WORKING_SET_RENDER_VERSION}">'
    )
    closing_marker = "</SLAIF_RECONSTRUCTED_CONSTITUTION>"
    marker_overhead = len(opening_marker.encode("utf-8")) + 1 + len(closing_marker.encode("utf-8"))
    pieces: list[str] = [
        json.dumps(
            {
                "authority": SOURCE_AUTHORITY_MARKER,
                "render_version": WORKING_SET_RENDER_VERSION,
                "schema_version": WORKING_SET_SCHEMA_VERSION,
                "policy_version": metadata.policy_version,
            },
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
    ]
    root_json = _root_block(root)
    if len(root_json.encode("utf-8")) > policy.max_entry_bytes:
        raise WorkingSetSelectionError(
            WorkingSetFailure(
                reason=WorkingSetFailureReason.ESSENTIAL_OVERFLOW, detail="root entry"
            )
        )
    pieces.append(root_json)
    consumed = sum(len(piece.encode("utf-8")) + 1 for piece in pieces) + marker_overhead

    states: dict[str, tuple[WorkingSetStatus, WorkingSetOmissionReason | None]] = {}
    ordered_states: list[WorkingSetDependency] = []
    instructions: list[AcquisitionInstruction] = []
    included_count = 0

    p1_included = [
        item for item in _sort_p1(p1, acquired_dependencies) if item.path in acquired_dependencies
    ]
    p1_missing = [
        item
        for item in _sort_p1(p1, acquired_dependencies)
        if item.path not in acquired_dependencies
    ]
    for item in p1_included:
        index = acquired_dependencies[item.path]
        block = _dependency_block(index)
        block_bytes = len(block.encode("utf-8"))
        if (
            block_bytes > policy.max_entry_bytes
            or consumed + block_bytes + 1 > policy.max_rendered_bytes
        ):
            raise WorkingSetSelectionError(
                WorkingSetFailure(
                    reason=WorkingSetFailureReason.ESSENTIAL_OVERFLOW,
                    detail="included P1 dependency",
                )
            )
        pieces.append(block)
        consumed += block_bytes + 1
        included_count += 1
        states[item.path] = (WorkingSetStatus.INCLUDED, None)
        ordered_states.append(_state(item, states[item.path]))
    for item in p1_missing:
        instruction = _acquisition_text(item)
        if len(instruction.encode("utf-8")) > policy.max_entry_bytes:
            raise WorkingSetSelectionError(
                WorkingSetFailure(
                    reason=WorkingSetFailureReason.ESSENTIAL_OVERFLOW,
                    detail="P1 acquisition instruction",
                )
            )
        # Instructions are governance state and therefore participate in the
        # same finite rendering budget as essential P1 content.
        instruction_piece = json.dumps(
            {"acquire": item.path, "instruction": instruction},
            ensure_ascii=False,
            separators=(",", ":"),
        )
        instruction_bytes = len(instruction_piece.encode("utf-8"))
        if consumed + instruction_bytes + 1 > policy.max_rendered_bytes:
            raise WorkingSetSelectionError(
                WorkingSetFailure(
                    reason=WorkingSetFailureReason.ESSENTIAL_OVERFLOW, detail="acquisition list"
                )
            )
        pieces.append(instruction_piece)
        consumed += instruction_bytes + 1
        instruction_model = AcquisitionInstruction(
            path=item.path,
            urgency=item.acquisition_urgency,
            instruction=instruction,
        )
        instructions.append(instruction_model)
        states[item.path] = (WorkingSetStatus.MISSING, None)
        ordered_states.append(_state(item, states[item.path]))

    optional_sorted = (
        _sort_optional(optional, acquired_dependencies) if policy.include_p2_p3 else []
    )
    for item in optional_sorted:
        if item.path not in acquired_dependencies:
            states[item.path] = (
                WorkingSetStatus.OMITTED,
                WorkingSetOmissionReason.NOT_ACQUIRED_OPTIONAL,
            )
            ordered_states.append(_state(item, states[item.path]))
            continue
        if included_count >= policy.max_entries:
            states[item.path] = (WorkingSetStatus.OMITTED, WorkingSetOmissionReason.BUDGET_EXCEEDED)
            ordered_states.append(_state(item, states[item.path]))
            continue
        index = acquired_dependencies[item.path]
        block = _dependency_block(index)
        block_bytes = len(block.encode("utf-8"))
        if block_bytes > policy.max_entry_bytes:
            states[item.path] = (WorkingSetStatus.OMITTED, WorkingSetOmissionReason.ENTRY_TOO_LARGE)
            ordered_states.append(_state(item, states[item.path]))
            continue
        if consumed + block_bytes + 1 > policy.max_rendered_bytes:
            states[item.path] = (WorkingSetStatus.OMITTED, WorkingSetOmissionReason.BUDGET_EXCEEDED)
            ordered_states.append(_state(item, states[item.path]))
            continue
        pieces.append(block)
        consumed += block_bytes + 1
        included_count += 1
        states[item.path] = (WorkingSetStatus.INCLUDED, None)
        ordered_states.append(_state(item, states[item.path]))

    for item in sorted(background, key=lambda value: (value.path, value.reference_confidence)):
        states[item.path] = (WorkingSetStatus.OMITTED, WorkingSetOmissionReason.CLASS_BELOW_POLICY)
        ordered_states.append(_state(item, states[item.path]))

    body = "\n".join(pieces)
    for marker in ("<SLAIF_RECONSTRUCTED_CONSTITUTION", "</SLAIF_RECONSTRUCTED_CONSTITUTION"):
        if marker in body:
            raise WorkingSetSelectionError(
                WorkingSetFailure(reason=WorkingSetFailureReason.UNSAFE_MARKER_COLLISION)
            )
    rendered_with_markers = f"{opening_marker}\n{body}\n{closing_marker}"
    encoded = rendered_with_markers.encode("utf-8")
    if len(encoded) > policy.max_rendered_bytes:
        raise WorkingSetSelectionError(
            WorkingSetFailure(
                reason=WorkingSetFailureReason.ESSENTIAL_OVERFLOW, detail="rendered working set"
            )
        )

    return WorkingSetSuccess(
        rendered_text=rendered_with_markers,
        content_sha256=hashlib.sha256(encoded).hexdigest(),
        rendered_bytes=len(encoded),
        policy_version=metadata.policy_version,
        root_logical_path=root.source_logical_path,
        root_source_sha256=root.source_sha256,
        root_index_version=root.schema_version,
        dependencies=tuple(ordered_states),
        acquisition_instructions=tuple(instructions),
    )


def _state(
    declaration: CompiledDependency,
    state: tuple[WorkingSetStatus, WorkingSetOmissionReason | None],
) -> WorkingSetDependency:
    return WorkingSetDependency(
        path=declaration.path,
        classification=declaration.classification,
        status=state[0],
        reference_confidence=declaration.reference_confidence,
        constitutional_priority=declaration.constitutional_priority,
        acquisition_urgency=declaration.acquisition_urgency,
        reason=state[1],
    )

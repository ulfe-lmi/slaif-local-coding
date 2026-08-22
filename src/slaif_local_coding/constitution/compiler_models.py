"""Strict, versioned contracts for objective-002 constitutional compilation.

These models describe *derived* indexes only.  They never replace the observed
source, Git/GitHub truth, OAP artifacts, or human authority.  Extra fields are
forbidden so a model cannot smuggle an alternate score or execution hint into
the contract.
"""

from __future__ import annotations

from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

INDEX_SCHEMA_VERSION = "constitution-index-v1"
COMPILER_VERSION = "compiler-v2"
PROMPT_POLICY_VERSION = "constitutional-rank-v2"


class RuleStrength(StrEnum):
    MUST = "must"
    MUST_NOT = "must_not"
    NEVER = "never"


class ConstitutionalClass(StrEnum):
    P0_ROOT = "P0"
    P1_DELEGATED_OR_SECURITY = "P1"
    P2_BINDING_PROCEDURE = "P2"
    P3_ARCHITECTURE_OR_CONTRACT = "P3"
    P4_BACKGROUND = "P4"


class AcquisitionUrgency(StrEnum):
    IMMEDIATE = "immediate"
    NEXT_TURN = "next_turn"
    BACKGROUND = "background"
    NONE = "none"


class FailureReason(StrEnum):
    INPUT_TOO_LARGE = "input_too_large"
    INVALID_INPUT = "invalid_input"
    INVALID_JSON = "invalid_json"
    OUTPUT_TOO_LARGE = "output_too_large"
    NESTING_TOO_DEEP = "nesting_too_deep"
    SCHEMA_INVALID = "schema_invalid"
    SOURCE_HASH_MISMATCH = "source_hash_mismatch"
    CANDIDATE_SET_MISMATCH = "candidate_set_mismatch"
    CONTRADICTORY_OUTPUT = "contradictory_output"
    UPSTREAM_TIMEOUT = "upstream_timeout"
    UPSTREAM_TRANSPORT = "upstream_transport"
    UPSTREAM_STATUS = "upstream_status"
    CANCELLED = "cancelled"


class CompiledRule(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    rule_id: str = Field(min_length=1, max_length=64, pattern=r"^[a-z0-9][a-z0-9_.-]{0,63}$")
    strength: RuleStrength
    statement: str = Field(min_length=1, max_length=700)
    location: str = Field(min_length=1, max_length=180)
    evidence: str = Field(min_length=1, max_length=700)


class CompiledDependency(BaseModel):
    """Ranking for one prior deterministic candidate, with independent scores."""

    model_config = ConfigDict(frozen=True, extra="forbid")
    path: str = Field(min_length=1, max_length=512)
    reference_confidence: float = Field(ge=0, le=1, allow_inf_nan=False)
    constitutional_priority: float = Field(ge=0, le=100, allow_inf_nan=False)
    classification: ConstitutionalClass
    relationship: str = Field(min_length=1, max_length=300)
    evidence: str = Field(min_length=1, max_length=500)
    acquisition_urgency: AcquisitionUrgency


class CompiledIndex(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    schema_version: Literal["constitution-index-v1"]
    compiler_version: str = Field(min_length=1, max_length=64)
    prompt_policy_version: str = Field(min_length=1, max_length=64)
    model: str = Field(min_length=1, max_length=128)
    source_logical_path: str = Field(min_length=1, max_length=512)
    source_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    source_byte_length: int = Field(ge=1)
    summary: str = Field(min_length=1, max_length=2000)
    rules: tuple[CompiledRule, ...] = Field(min_length=1, max_length=128)
    roles: tuple[str, ...] = Field(min_length=1, max_length=32)
    authorities: tuple[str, ...] = Field(min_length=1, max_length=32)
    source_of_truth_boundaries: tuple[str, ...] = Field(min_length=1, max_length=32)
    ordering_constraints: tuple[str, ...] = Field(default=(), max_length=32)
    exceptions: tuple[str, ...] = Field(default=(), max_length=32)
    dependencies: tuple[CompiledDependency, ...]
    reread_triggers: tuple[str, ...] = Field(min_length=1, max_length=32)
    status: Literal["success"] = "success"

    def effective_class(self) -> ConstitutionalClass:
        """Return the strongest class needed for the bounded pinned-cache decision."""
        dependency_classes = {item.classification for item in self.dependencies}
        ranks = [
            (rank, classification)
            for classification, rank in (
                (ConstitutionalClass.P0_ROOT, 0),
                (ConstitutionalClass.P1_DELEGATED_OR_SECURITY, 1),
                (ConstitutionalClass.P2_BINDING_PROCEDURE, 2),
                (ConstitutionalClass.P3_ARCHITECTURE_OR_CONTRACT, 3),
                (ConstitutionalClass.P4_BACKGROUND, 4),
            )
            if classification in dependency_classes
        ]
        return min(ranks, default=(4, ConstitutionalClass.P4_BACKGROUND))[1]


class CompilationFailure(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    reason: FailureReason
    detail: str = Field(default="", max_length=240)
    attempts: int = Field(ge=0)
    duration_seconds: float = Field(ge=0, allow_inf_nan=False)


class CompilerMetrics(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    attempts: int = Field(ge=0)
    successes: int = Field(ge=0)
    schema_failures: int = Field(ge=0)
    timeouts: int = Field(ge=0)
    transport_failures: int = Field(ge=0)
    cache_hits: int = Field(ge=0)
    cache_misses: int = Field(ge=0)
    deduplicated_waits: int = Field(ge=0)
    prompt_bytes: int = Field(ge=0)
    output_bytes: int = Field(ge=0)


class CompilerResult(BaseModel):
    """Discriminated safe result; ``failure`` carries no upstream payload."""

    model_config = ConfigDict(frozen=True, extra="forbid")
    index: CompiledIndex | None = None
    failure: CompilationFailure | None = None
    cache_outcome: Literal[
        "hit", "miss-persisted", "miss-write-failed", "disabled", "fallback-degraded"
    ]
    cache_detail: str = Field(default="", max_length=120)

    @property
    def ok(self) -> bool:
        return self.index is not None

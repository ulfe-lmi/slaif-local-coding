"""Typed, serializable observation contracts with no retained runtime state."""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class EvidenceType(StrEnum):
    PROJECT_INSTRUCTIONS = "project_instructions"
    INPUT_FILE = "input_file"
    PAIRED_TOOL_RESULT = "paired_tool_result"
    MARKDOWN_INLINE = "markdown_inline"
    MARKDOWN_REFERENCE = "markdown_reference"
    BACKTICK = "backtick"
    QUOTED = "quoted"
    NORMATIVE_NEIGHBOR = "normative_neighbor"


class IncompleteReason(StrEnum):
    SOURCE_TOO_LARGE = "source_too_large"
    TOO_MANY_ROOTS = "too_many_roots"
    TOO_MANY_CANDIDATES = "too_many_candidates"
    EVIDENCE_BUDGET_EXCEEDED = "evidence_budget_exceeded"
    PATH_TOO_LONG = "path_too_long"
    INVALID_ROOT_PATH = "invalid_root_path"
    PARSING_ERROR = "parsing_error"


class RejectionReason(StrEnum):
    AMBIGUOUS = "ambiguous"
    UNSAFE_LOCATION = "unsafe_location"
    TRAVERSAL = "traversal"
    UNSUPPORTED_FILE = "unsupported_file"
    PATH_TOO_LONG = "path_too_long"


class TrustClass(StrEnum):
    ABSENT = "absent"
    UNTRUSTED_CLIENT_HINT = "untrusted_client_hint"
    TRUSTED_INTERNAL = "trusted_internal"


class ObservationContext(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    endpoint: str
    route_id: str
    model: str
    streaming: bool
    principal: str | None = Field(default=None, repr=False)
    session: str | None = Field(default=None, repr=False)
    repository: str | None = Field(default=None, repr=False)
    discriminator_trust: TrustClass = TrustClass.ABSENT


class EvidenceRecord(BaseModel):
    """Half-open UTF-8 byte offsets into the exact observed source content."""

    model_config = ConfigDict(frozen=True, extra="forbid")
    type: EvidenceType
    start_byte: int = Field(ge=0)
    end_byte: int = Field(ge=0)
    location: str


class CandidateReference(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    path: str
    first_seen: int = Field(ge=0)
    evidence: tuple[EvidenceRecord, ...] = Field(min_length=1)
    complete: bool = True


class ConstitutionSourceObservation(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    source_kind: str = "AGENTS_ROOT"
    logical_path: str
    content_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    byte_length: int = Field(ge=0)
    evidence: tuple[EvidenceRecord, ...]
    candidates: tuple[CandidateReference, ...] = ()
    complete: bool = True
    incomplete_reasons: tuple[IncompleteReason, ...] = ()


class DependencyObservationReason(StrEnum):
    AMBIGUOUS = "ambiguous"
    UNSAFE_PATH = "unsafe_path"
    DUPLICATE_EVIDENCE = "duplicate_evidence"
    MISMATCHED_PAIRING = "mismatched_pairing"
    EXTRA_EVIDENCE = "extra_evidence"
    CONTENT_TOO_LARGE = "content_too_large"
    INVALID_CONTENT = "invalid_content"


class ObservedDependency(BaseModel):
    """A uniquely evidenced, bounded source crossing this request boundary."""

    model_config = ConfigDict(frozen=True, extra="forbid")
    logical_path: str
    byte_length: int = Field(ge=1)
    evidence: tuple[EvidenceRecord, ...] = Field(min_length=1)


class DependencyRejectionCount(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    reason: DependencyObservationReason
    count: int = Field(ge=1)


class RejectionCount(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    reason: RejectionReason
    count: int = Field(ge=1)


class ObservationResult(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    schema_version: str
    policy_version: str
    context: ObservationContext
    roots: tuple[ConstitutionSourceObservation, ...]
    complete: bool
    incomplete_reasons: tuple[IncompleteReason, ...]
    accepted_candidates: int = Field(ge=0)
    rejected_candidates: int = Field(ge=0)
    rejection_counts: tuple[RejectionCount, ...] = ()
    dependencies: tuple[ObservedDependency, ...] = ()
    dependency_rejections: tuple[DependencyRejectionCount, ...] = ()

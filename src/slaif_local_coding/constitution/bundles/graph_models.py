"""Typed immutable records for the 018-a trusted-namespace graph foundation.

Pure, inert, and versioned as ``cache-graph/v1`` (reference grammar
``reference-grammar/v1``).  These records bind the full scoped
namespace/workspace/version identity of their source (R2 law: every
document/candidate/edge carries an explicit stable scoped key, not just
a matching path), and their operational ``str``/``repr``/errors never
echo raw source content or private identity VALUES (R1 law:
principal/session/repository/route/model/config/workspace identity
values are not labels merely because bounded; the derived 64-hex scoped
key is observable like a digest, the private inputs hashing into it are
not).  No filesystem, network or shell facility is imported or used;
construction is NOT authentication — a namespace is only as trusted as
the verified identity the caller passed (see
``gateway_identity.verify_signed_identity`` / validated standalone
configuration).
"""

from __future__ import annotations

import hashlib
import json
from enum import StrEnum

from pydantic import ConfigDict, Field, field_validator, model_validator
from pydantic_core import core_schema

from ..cache import RequestIdentity
from .client_paths import validate_workspace
from .observation_models import (
    EMPTY_SOURCE_SHA256,
    OBSERVER_VERSION,
    PRIVATE_ID_PLACEHOLDER,
    CharSpan,
    Limitation,
    _Frozen,
)

GRAPH_CONTRACT_VERSION = "cache-graph/v1"
REFERENCE_GRAMMAR = "reference-grammar/v1"

#: The evidenced effective root filename inside its workspace.
ROOT_FILENAME = "AGENTS.md"

_HEX64 = r"^[0-9a-f]{64}$"
_HEX_DIGITS = frozenset("0123456789abcdef")


class _GraphFrozen(_Frozen):
    """017 frozen base plus graph-specific privacy-safe error hygiene.

    The 017 ``_Frozen`` semantics (frozen, extra-forbid) are preserved
    unchanged; this subclass only adds ``hide_input_in_errors`` so
    Pydantic validation errors on graph records (direct or nested)
    never echo caller-supplied input values (R1 law).  The 017 base
    class itself is not modified.
    """

    model_config = ConfigDict(frozen=True, extra="forbid", hide_input_in_errors=True)


def _fixed(msg: str) -> ValueError:
    """Fixed diagnostic message: never echoes the offending value."""
    return ValueError(msg)


def _check_text(value: str, field: str, max_len: int) -> str:
    if not 1 <= len(value) <= max_len:
        raise _fixed(f"{field} must be 1..{max_len} characters")
    if any(ord(c) < 0x20 or ord(c) == 0x7F for c in value):
        raise _fixed(f"{field} must not contain control characters")
    return value


def _check_hex64(value: str, field: str) -> str:
    if len(value) != 64 or not set(value) <= _HEX_DIGITS:
        raise _fixed(f"{field} must be a 64-hex digest")
    return value


def _check_rel_path(value: str) -> str:
    if not value:
        raise _fixed("path must be nonempty")
    if any(ord(c) < 0x20 or ord(c) == 0x7F for c in value):
        raise _fixed("path must not contain control characters")
    if "\\" in value or value.startswith("/"):
        raise _fixed("path must be a workspace-relative POSIX path")
    if value != value.strip():
        raise _fixed("path must not have leading or trailing whitespace")
    if any(part in ("", ".", "..") for part in value.split("/")):
        raise _fixed("path must be a normalized relative POSIX path")
    return value


def _canonical_namespace_fields(
    principal: str,
    session: str,
    repository: str,
    route: str,
    model_identity: str,
    config_fingerprint: str,
    graph_version: str,
    reference_version: str,
    observation_version: str,
    bounds: GraphBounds,
) -> bytes:
    payload = [
        principal,
        session,
        repository,
        route,
        model_identity,
        config_fingerprint,
        graph_version,
        reference_version,
        observation_version,
        json.dumps(bounds.model_dump(mode="json"), sort_keys=True, separators=(",", ":")),
    ]
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class GraphOutcome(StrEnum):
    """Fixed outcome vocabulary for one graph snapshot."""

    COMPLETE = "complete"
    NO_ROOT = "no_root"
    WORKSPACE_UNPROVEN = "workspace_unproven"
    ROOT_CONFLICT = "root_conflict"
    VERSION_CONFLICT = "version_conflict"
    OVER_BOUND = "over_bound"


class NodeStatus(StrEnum):
    ACQUIRED = "acquired"
    ACQUIRED_EMPTY = "acquired_empty"
    DISCOVERED_CONTENT_MISSING = "discovered_content_missing"
    VERSION_CONFLICT = "version_conflict"


class SourceKind(StrEnum):
    ROOT = "root"
    READ = "read"
    PROCESS = "process"


class CandidateSyntax(StrEnum):
    INLINE_LINK = "inline_link"
    REFERENCE_DEFINITION = "reference_definition"
    BACKTICK_CODE = "backtick_code"
    PLAIN_PATH = "plain_path"


class CandidateStatus(StrEnum):
    ACCEPTED = "accepted"
    REPEATED_TARGET = "repeated_target"
    UNSUPPORTED = "unsupported"
    EXTERNAL = "external"
    UNRESOLVED_ORIGIN = "unresolved_origin"
    OVER_BOUND = "over_bound"


class GraphLimitation(StrEnum):
    """Fixed, non-echoing graph limitation vocabulary (one per budget)."""

    # Root / workspace binding
    NO_ROOT = "no_root"
    WORKSPACE_UNPROVEN = "workspace_unproven"
    COMPETING_ROOTS = "competing_roots"
    ROOT_CONTEXT_MISMATCH = "root_context_mismatch"
    ROOT_VERSION_CONFLICT = "root_version_conflict"
    # Reference path resolution
    PATH_OUTSIDE_WORKSPACE = "path_outside_workspace"
    PATH_TRAVERSAL = "path_traversal"
    PATH_ABSOLUTE_UNPROVEN = "path_absolute_unproven"
    PATH_TOO_LONG = "path_too_long"
    # Reference target law
    TARGET_EMPTY = "target_empty"
    TARGET_UNSUPPORTED_CHAR = "target_unsupported_char"
    TARGET_PERCENT_ENCODING = "target_percent_encoding"
    TARGET_BACKSLASH = "target_backslash"
    TARGET_QUERY = "target_query"
    TARGET_CONTROL_CHAR = "target_control_char"
    TARGET_EXTERNAL_SCHEME = "target_external_scheme"
    TARGET_EXTERNAL_HOST = "target_external_host"
    TARGET_TILDE_OR_DRIVE = "target_tilde_or_drive"
    MARKUP_MISBALANCED = "markup_misbalanced"
    MARKUP_QUOTED_SPACE = "markup_quoted_space"
    MALFORMED_UNICODE = "malformed_unicode"
    # Budget refusals (one per GraphBounds constant)
    BATCH_OVER_BOUND = "batch_over_bound"
    DOCUMENT_OVER_BOUND = "document_over_bound"
    SOURCE_OVER_BOUND = "source_over_bound"
    TOTAL_SOURCE_OVER_BOUND = "total_source_over_bound"
    CANDIDATES_PER_DOCUMENT_OVER_BOUND = "candidates_per_document_over_bound"
    CANDIDATES_TOTAL_OVER_BOUND = "candidates_total_over_bound"
    NODES_OVER_BOUND = "nodes_over_bound"
    EDGES_OVER_BOUND = "edges_over_bound"
    DEPTH_OVER_BOUND = "depth_over_bound"
    WORK_UNITS_EXHAUSTED = "work_units_exhausted"
    DIAGNOSTICS_FULL = "diagnostics_full"
    # Scoped binding
    NAMESPACE_MISMATCH = "namespace_mismatch"
    WORKSPACE_MISMATCH = "workspace_mismatch"
    BOUNDS_MISMATCH = "bounds_mismatch"
    # Origin / version
    UNRESOLVED_ORIGIN = "unresolved_origin"
    VERSION_CONFLICT = "version_conflict"
    CANDIDATE_DIGEST_MISMATCH = "candidate_digest_mismatch"


class GraphBounds(_GraphFrozen):
    """Finite graph budgets (initial documented defaults).

    Every constant has its own fixed typed refusal.  Configurable
    STRICTER bounds are always permitted; wider bounds are not accepted
    beyond the declared ceilings.  ``max_requests`` bounds the public
    batch; the remaining constants bound one snapshot.  Budget constants
    are engineering bounds, not a product effective-context ``C`` or a
    RAM ceiling guarantee.
    """

    max_requests: int = Field(default=128, ge=1, le=10_000)
    max_documents: int = Field(default=128, ge=1, le=10_000)
    max_single_source_bytes: int = Field(default=1_000_000, ge=1, le=10_000_000)
    max_total_inspected_source_bytes: int = Field(default=4_194_304, ge=1, le=16_000_000)
    max_reference_candidates_total: int = Field(default=2048, ge=1, le=100_000)
    max_reference_candidates_per_document: int = Field(default=256, ge=1, le=10_000)
    max_nodes: int = Field(default=512, ge=1, le=10_000)
    max_edges: int = Field(default=2048, ge=1, le=100_000)
    max_depth: int = Field(default=64, ge=1, le=10_000)
    max_work_units: int = Field(default=65_536, ge=1, le=10_000_000)
    max_diagnostics: int = Field(default=64, ge=1, le=10_000)
    max_path_bytes: int = Field(default=4096, ge=1, le=65_536)


class GraphNamespace(_GraphFrozen):
    """Explicit trusted INTERNAL graph namespace (R1/R2 law).

    The identity components mirror ``constitution.cache.RequestIdentity``
    and MUST come from the existing trusted ingress
    (``gateway_identity.verify_signed_identity``) or a validated
    standalone configuration.  Object construction is not itself
    authentication.  ``workspace`` is the evidenced root scope observed
    for this snapshot; the FINAL state identity binds it:
    ``scoped_key = sha256(namespace_key + "\\0" + workspace)``.  The
    pre-root ``namespace_key`` (workspace-free) changes with the
    effective graph bounds: a bare caller tag cannot hide a different
    effective graph configuration.  The 64-hex keys are observable like
    digests; the private identity values hashing into them are suppressed
    in every operational representation and error.
    """

    principal: str = Field(min_length=1, max_length=256)
    session: str = Field(min_length=1, max_length=256)
    repository: str = Field(min_length=1, max_length=256)
    route: str = Field(min_length=1, max_length=64)
    model_identity: str = Field(min_length=1, max_length=256)
    config_fingerprint: str
    workspace: str
    graph_version: str = GRAPH_CONTRACT_VERSION
    reference_version: str = REFERENCE_GRAMMAR
    observation_version: str = OBSERVER_VERSION
    bounds: GraphBounds = GraphBounds()
    namespace_key: str
    scoped_key: str

    @field_validator("principal", "session", "repository", "route", "model_identity")
    @classmethod
    def _v_identity_text(cls, value: str, info: core_schema.FieldValidationInfo) -> str:
        limit = 256 if info.field_name != "route" else 64
        return _check_text(value, info.field_name or "field", limit)

    @field_validator("config_fingerprint", "namespace_key", "scoped_key")
    @classmethod
    def _v_hex64(cls, value: str, info: core_schema.FieldValidationInfo) -> str:
        return _check_hex64(value, info.field_name or "field")

    @field_validator("workspace")
    @classmethod
    def _v_workspace(cls, value: str, info: core_schema.FieldValidationInfo) -> str:
        # Structural + canonical-spelling check only: field validation
        # cannot see fields defined later (bounds), so the actual
        # configured byte bound is enforced by the model-level validator
        # below.  Noncanonical spellings (double slash, trailing slash,
        # ``.``/empty segments) are rejected consistently at every entry
        # point; the scoped key always binds the canonical spelling.
        if validate_workspace(value, 10**9) != value:
            raise _fixed("workspace must be a canonical absolute POSIX path")
        return value

    @model_validator(mode="after")
    def _v_bound_integrity(self) -> GraphNamespace:
        # Enforce the ACTUAL supplied bounds on the workspace byte length
        # (field order cannot do this), then recompute both keys from the
        # actual bound identity/versions/bounds/workspace so direct model
        # construction cannot retain inconsistent or forged keys (R2 law).
        if len(self.workspace.encode("utf-8")) > self.bounds.max_path_bytes:
            raise _fixed("workspace exceeds the actual configured path bound")
        canonical = _canonical_namespace_fields(
            self.principal,
            self.session,
            self.repository,
            self.route,
            self.model_identity,
            self.config_fingerprint,
            self.graph_version,
            self.reference_version,
            self.observation_version,
            self.bounds,
        )
        expected_key = _sha256_hex(canonical)
        expected_scoped = _sha256_hex((expected_key + "\0" + self.workspace).encode("utf-8"))
        if self.namespace_key != expected_key or self.scoped_key != expected_scoped:
            raise _fixed("namespace keys are inconsistent with the bound identity")
        return self

    def __repr__(self) -> str:
        return (
            "GraphNamespace("
            f"principal={PRIVATE_ID_PLACEHOLDER}, "
            f"session={PRIVATE_ID_PLACEHOLDER}, "
            f"repository={PRIVATE_ID_PLACEHOLDER}, "
            f"route={PRIVATE_ID_PLACEHOLDER}, "
            f"model_identity={PRIVATE_ID_PLACEHOLDER}, "
            f"config_fingerprint={PRIVATE_ID_PLACEHOLDER}, "
            f"workspace={PRIVATE_ID_PLACEHOLDER}, "
            f"graph_version={self.graph_version!r}, "
            f"reference_version={self.reference_version!r}, "
            f"observation_version={self.observation_version!r}, "
            f"bounds={self.bounds!r}, "
            f"namespace_key={self.namespace_key!r}, "
            f"scoped_key={self.scoped_key!r})"
        )

    __str__ = __repr__


def make_graph_namespace(
    identity: RequestIdentity,
    *,
    model_identity: str,
    config_fingerprint: str,
    workspace: str,
    bounds: GraphBounds | None = None,
) -> GraphNamespace:
    """Build the scoped graph namespace from an already-verified identity.

    The caller MUST hold a trusted ingress identity (see module law);
    this factory validates shapes only and performs no authentication.
    The effective bounds actually used are bound into the pre-root
    ``namespace_key``; the observed workspace is bound into the final
    ``scoped_key``.

    Invalid caller-supplied facts raise a plain ``ValueError`` with a
    fixed message that never echoes the offending value (the factory is
    the product path; direct model construction keeps the typed model
    validators as defense in depth).
    """
    _check_text(model_identity, "model_identity", 256)
    _check_hex64(config_fingerprint, "config_fingerprint")
    _check_text(identity.principal, "principal", 256)
    _check_text(identity.session, "session", 256)
    _check_text(identity.repository, "repository", 256)
    _check_text(identity.route, "route", 64)
    effective_bounds = bounds if bounds is not None else GraphBounds()
    if validate_workspace(workspace, effective_bounds.max_path_bytes) != workspace:
        raise _fixed("workspace must be a canonical bounded absolute POSIX path")
    canonical = _canonical_namespace_fields(
        identity.principal,
        identity.session,
        identity.repository,
        identity.route,
        model_identity,
        config_fingerprint,
        GRAPH_CONTRACT_VERSION,
        REFERENCE_GRAMMAR,
        OBSERVER_VERSION,
        effective_bounds,
    )
    namespace_key = _sha256_hex(canonical)
    scoped_key = _sha256_hex((namespace_key + "\0" + workspace).encode("utf-8"))
    return GraphNamespace(
        principal=identity.principal,
        session=identity.session,
        repository=identity.repository,
        route=identity.route,
        model_identity=model_identity,
        config_fingerprint=config_fingerprint,
        workspace=workspace,
        bounds=effective_bounds,
        namespace_key=namespace_key,
        scoped_key=scoped_key,
    )


class SourceOccurrence(_GraphFrozen):
    """Exact provenance of one observed source region in one original carrier.

    ``span`` is a half-open character span into the EXACT decoded JSON
    string that carried this piece (piece 0 = the single carrier for
    root/read surfaces; pieces > 0 = one original process result carrier
    each).  Provenance is never renumbered to normalize input order
    (R3 law).
    """

    request_index: int = Field(ge=0)
    carrier_location: str = Field(min_length=1)
    piece_index: int = Field(default=0, ge=0)
    span: CharSpan


class SourceDocument(_GraphFrozen):
    """One acquired (or missing/conflicting) workspace document.

    Status invariants (explicit, no fabricated provenance):
    ``DISCOVERED_CONTENT_MISSING`` carries NO kind/digest/lengths/
    occurrences (an unread reachable node has no observed source);
    ``ACQUIRED`` requires an earned kind, occurrences and nonzero
    byte/char lengths with a digest; ``ACQUIRED_EMPTY`` requires earned
    occurrences and the empty-source proof (digest, zero lengths);
    ``VERSION_CONFLICT`` selects NO version (no kind/digest/lengths) but
    retains the competing occurrences as evidence.
    """

    path: str
    scoped_key: str
    digest: str | None = Field(default=None, pattern=_HEX64)
    byte_length: int | None = Field(default=None, ge=0)
    char_length: int | None = Field(default=None, ge=0)
    status: NodeStatus
    kind: SourceKind | None = None
    occurrences: tuple[SourceOccurrence, ...] = ()
    graph_version: str = GRAPH_CONTRACT_VERSION

    @field_validator("path")
    @classmethod
    def _v_path(cls, value: str) -> str:
        checked = _check_rel_path(value)
        if not checked.endswith(".md"):
            raise _fixed("document path must end in .md")
        return checked

    @field_validator("scoped_key")
    @classmethod
    def _v_scoped_key(cls, value: str) -> str:
        return _check_hex64(value, "scoped_key")

    @model_validator(mode="after")
    def _v_status_invariants(self) -> SourceDocument:
        if self.status is NodeStatus.DISCOVERED_CONTENT_MISSING:
            if (
                self.kind is not None
                or self.digest is not None
                or self.byte_length is not None
                or self.char_length is not None
                or self.occurrences
            ):
                raise _fixed("missing node must not carry source provenance")
        elif self.status is NodeStatus.ACQUIRED:
            if (
                self.kind is None
                or not self.occurrences
                or self.digest is None
                or self.byte_length is None
                or self.byte_length < 1
                or self.char_length is None
                or self.char_length < 1
            ):
                raise _fixed("acquired node requires earned source proof")
        elif self.status is NodeStatus.ACQUIRED_EMPTY:
            if (
                self.kind is None
                or not self.occurrences
                or self.digest is None
                or self.digest != EMPTY_SOURCE_SHA256
                or self.byte_length != 0
                or self.char_length != 0
            ):
                raise _fixed("empty node requires earned empty-source proof")
        else:  # VERSION_CONFLICT: no version may be selected
            if (
                self.kind is not None
                or self.digest is not None
                or self.byte_length is not None
                or self.char_length is not None
                or not self.occurrences
            ):
                raise _fixed("conflict node must not select a version")
        return self


class ReferenceCandidate(_GraphFrozen):
    """One bounded raw reference occurrence in one acquired document.

    ``target_chars`` is protected internal metadata (original spelling);
    the operational representation never echoes it.  ``target_byte_span``
    is the same destination in the BYTE domain of the referring
    document's exact source string (computed with the accepted
    ``CharSpan.to_byte_span`` law; the two domains are never mixed).
    ``referring_path``/``referring_digest`` are ``None`` only for
    unresolved-origin candidates from a boundaryless multi-member
    bundle (no attributable referring document).
    """

    referring_path: str | None
    scoped_key: str
    referring_digest: str | None = Field(default=None, pattern=_HEX64)
    syntax: CandidateSyntax
    target_chars: str
    target_char_span: CharSpan
    target_byte_span: CharSpan
    resolved_path: str | None = None
    status: CandidateStatus = CandidateStatus.ACCEPTED
    reasons: tuple[GraphLimitation, ...] = ()
    occurrence_index: int = Field(default=0, ge=0)
    graph_version: str = GRAPH_CONTRACT_VERSION

    @field_validator("scoped_key")
    @classmethod
    def _v_scoped_key(cls, value: str) -> str:
        return _check_hex64(value, "scoped_key")

    def __repr__(self) -> str:
        return (
            "ReferenceCandidate("
            f"referring_path={self.referring_path!r}, "
            f"referring_digest={self.referring_digest!r}, "
            f"scoped_key={self.scoped_key!r}, "
            f"syntax={self.syntax.value!r}, "
            f"target_length={len(self.target_chars)!r}, "
            f"target_char_span={self.target_char_span!r}, "
            f"target_byte_span={self.target_byte_span!r}, "
            f"resolved_path={self.resolved_path!r}, "
            f"status={self.status.value!r}, "
            f"reasons={[r.value for r in self.reasons]!r}, "
            f"occurrence_index={self.occurrence_index!r}, "
            f"graph_version={self.graph_version!r})"
        )

    __str__ = __repr__


class UnresolvedOriginCandidate(_GraphFrozen):
    """Boundaryless multi-member bundle: candidates retained WITHOUT an edge.

    The whole bundle keeps its source proof (digest) and candidate
    evidence with possible origins; no member text, hash or graph edge
    is invented (a-slice law; b-scope admission logic is not built).
    """

    scoped_key: str
    bundle_digest: str = Field(pattern=_HEX64)
    possible_origins: tuple[str, ...]
    candidates: tuple[ReferenceCandidate, ...] = ()
    request_index: int = Field(ge=0)
    carrier_location: str = Field(min_length=1)
    graph_version: str = GRAPH_CONTRACT_VERSION

    @field_validator("scoped_key")
    @classmethod
    def _v_scoped_key(cls, value: str) -> str:
        return _check_hex64(value, "scoped_key")

    @field_validator("possible_origins")
    @classmethod
    def _v_origins(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        return tuple(_check_rel_path(origin) for origin in value)


class GraphEdge(_GraphFrozen):
    """One directed graph edge from a reachable attributable document.

    ``depth`` is the target's TRUE shortest root distance (relaxation
    law): a root self-reference is 0; a cycle back-edge carries the
    target's shortest distance, never the walk length.
    """

    scoped_key: str
    from_path: str
    to_path: str
    referring_digest: str = Field(pattern=_HEX64)
    occurrence_index: int = Field(ge=0)
    depth: int = Field(ge=0, le=10_000)
    graph_version: str = GRAPH_CONTRACT_VERSION

    @field_validator("scoped_key")
    @classmethod
    def _v_scoped_key(cls, value: str) -> str:
        return _check_hex64(value, "scoped_key")

    @field_validator("from_path", "to_path")
    @classmethod
    def _v_paths(cls, value: str) -> str:
        return _check_rel_path(value)


class GraphSnapshot(_GraphFrozen):
    """Pure graph foundation result for one bounded batch (018-a).

    Carries scoped keys, paths, digests, counts and fixed reasons only;
    never raw source content.  ``diagnostics`` are fixed bounded strings
    from a closed vocabulary (no payload text).
    """

    namespace: GraphNamespace
    outcome: GraphOutcome
    root_path: str | None = None
    root_digest: str | None = Field(default=None, pattern=_HEX64)
    nodes: tuple[SourceDocument, ...] = ()
    edges: tuple[GraphEdge, ...] = ()
    missing: tuple[str, ...] = ()
    unresolved_origins: tuple[UnresolvedOriginCandidate, ...] = ()
    conflicts: tuple[GraphLimitation, ...] = ()
    diagnostics: tuple[GraphLimitation, ...] = ()
    work_units: int = Field(default=0, ge=0)
    max_depth: int = Field(default=0, ge=0)
    request_count: int = Field(default=0, ge=0)
    documents_inspected: int = Field(default=0, ge=0)
    source_bytes_inspected: int = Field(default=0, ge=0)
    candidates_total: int = Field(default=0, ge=0)
    candidates_per_document_max: int = Field(default=0, ge=0)
    observation_limitations: tuple[Limitation, ...] = ()

    @field_validator("root_digest")
    @classmethod
    def _v_root_digest(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return _check_hex64(value, "root_digest")

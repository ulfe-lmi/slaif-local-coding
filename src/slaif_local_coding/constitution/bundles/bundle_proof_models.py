"""Typed immutable records for the 018-b bundle-proof bridge.

Pure, inert, and versioned as ``cache-bundle-proof/v1``.  These records
carry the complete ordered whole-bundle source proof for one bounded
batch of decoded requests under one explicit trusted namespace: the
requested versus proven-executed member occurrences, the ordered
normalized represented members, the exact aggregate source TEXT (self-
contained: the proof does not depend on caller payload survival), the
original carrier/piece spans, the call/result positions and IDs, the
original root authority, and the parser/proof versions.

Privacy law (R1, inherited from the 018-a graph records and the 017
observation records): operational ``str``/``repr``/validation errors
never echo raw source content, marker literals, private call/result ID
values or identity VALUES.  Digests, spans, counts, locations, fixed
enums and scoped keys are observable like any derived digest.  The
frozen base adds ``hide_input_in_errors`` so Pydantic validation errors
on these records (direct or nested) never echo caller-supplied input
values; the 017 base class and the 018-a graph records are not
modified.

Namespace law (R2, 018-a pattern): every record is scoped by an explicit
trusted namespace whose 64-hex keys bind the identity, the config
fingerprint, the proof/observation/graph versions, the NEW proof
bounds, the ACTUAL effective ``GraphBounds`` (batch/path/source budgets)
and the ACTUAL effective ``ObservationBounds`` (the 017 ceilings the
re-observation pass and the command reparse run under).  The keys are
recomputed on direct construction, so a forged or inconsistent key pair
cannot be retained and narrower actual bounds cannot hide behind an
opaque caller tag.  Object construction is NOT authentication: a
namespace is only as trusted as the verified identity the caller passed
(``gateway_identity.verify_signed_identity`` / validated standalone
configuration).

No filesystem, network or shell facility is imported or used.
"""

from __future__ import annotations

import json
from enum import StrEnum

from pydantic import Field, field_validator, model_validator
from pydantic_core import core_schema

from ..cache import RequestIdentity
from .client_paths import validate_workspace
from .graph_models import (
    GRAPH_CONTRACT_VERSION,
    GraphBounds,
    _check_hex64,
    _check_rel_path,
    _check_text,
    _fixed,
    _GraphFrozen,
    _sha256_hex,
)
from .observation_models import (
    EMPTY_SOURCE_SHA256,
    OBSERVER_VERSION,
    PRIVATE_ID_PLACEHOLDER,
    CharSpan,
    Limitation,
    NormalizedPath,
    ObservationBounds,
    sha256_hex,
)

BUNDLE_PROOF_CONTRACT_VERSION = "cache-bundle-proof/v1"

_HEX64 = r"^[0-9a-f]{64}$"

#: The evidenced effective root filename inside its workspace (018-a).
ROOT_FILENAME = "AGENTS.md"


class BundleSurface(StrEnum):
    """The 017 observation surface that earned one proven bundle (the
    PARSER surface).  It is not an authority role: the original API
    source-role classification of the carrier is ``endpoint`` +
    ``source_role`` on the record, and the effective root-authority
    binding is ``root_path``/``root_digest`` — a file tool result never
    carries root authority by appearing under the evidenced root."""

    READ = "read"
    PROCESS = "process"


class BundleSourceRole(StrEnum):
    """Original API source role of one proven bundle's carrier.

    Closed vocabulary for this slice: every proven bundle comes from a
    FILE tool result (a legacy read tool result or a native exec
    process result).  A file tool result is dependency candidate text
    under the evidenced root's scope; it holds NO root authority.
    Root-envelope content is bound at the snapshot level
    (``root_path``/``root_digest``) and is never a bundle carrier in
    this slice."""

    FILE_TOOL_RESULT = "file_tool_result"


class BundleProofKind(StrEnum):
    """Whole (boundaryless 017-attributed region) vs partitioned
    (finite unique-marker proof over the full proven output)."""

    WHOLE = "whole"
    PARTITIONED = "partitioned"


class BundleMarkerRole(StrEnum):
    """Position of a proven non-source marker line relative to the
    source segments (prefix / interior / suffix)."""

    PREFIX = "prefix"
    INTERIOR = "interior"
    SUFFIX = "suffix"


class BundleProofOutcome(StrEnum):
    """Fixed outcome vocabulary for one bundle-proof snapshot."""

    COMPLETE = "complete"
    NO_ROOT = "no_root"
    WORKSPACE_UNPROVEN = "workspace_unproven"
    ROOT_CONFLICT = "root_conflict"
    OVER_BOUND = "over_bound"
    VERSION_CONFLICT = "version_conflict"


class BundleLimitation(StrEnum):
    """Fixed, non-echoing bundle-proof limitation vocabulary."""

    # Root / workspace binding
    NO_ROOT = "no_root"
    COMPETING_ROOTS = "competing_roots"
    WORKSPACE_UNPROVEN = "workspace_unproven"
    WORKSPACE_MISMATCH = "workspace_mismatch"
    ROOT_CONTEXT_MISMATCH = "root_context_mismatch"
    # Version refusal (the entry's typed supported-version check)
    VERSION_UNSUPPORTED = "version_unsupported"
    # Batch / budget refusals (one per bound)
    BATCH_OVER_BOUND = "batch_over_bound"
    BUNDLES_OVER_BOUND = "bundles_over_bound"
    SOURCE_OVER_BOUND = "source_over_bound"
    TOTAL_SOURCE_OVER_BOUND = "total_source_over_bound"
    MEMBERS_OVER_BOUND = "members_over_bound"
    SEGMENTS_OVER_BOUND = "segments_over_bound"
    MARKER_OVER_BOUND = "marker_over_bound"
    MARKER_SEARCH_OVER_BOUND = "marker_search_over_bound"
    # Plan / partition law
    MARKER_EMPTY = "marker_empty"
    MARKER_MISSING = "marker_missing"
    MARKER_DUPLICATE = "marker_duplicate"
    MARKER_ORDER = "marker_order"
    MARKER_OVERLAP = "marker_overlap"
    PLAN_UNSUPPORTED = "plan_unsupported"
    MEMBER_UNRESOLVED = "member_unresolved"
    #: A normalized represented member reference exceeds one of the
    #: TWO ACTUAL path ceilings (the effective ``GraphBounds`` path
    #: bound or the effective ``ObservationBounds`` path bound, in
    #: UTF-8 bytes).  Fixed typed non-acquisition: no source, digest
    #: or proof follows from an over-bound reference.
    MEMBER_PATH_OVER_BOUND = "member_path_over_bound"
    SEGMENT_UNEXPLAINED = "segment_unexplained"
    # Integrity / consistency
    OUTPUT_INCONSISTENT = "output_inconsistent"
    SOURCE_CONFLICT = "source_conflict"
    SEAM_CONFLICT = "seam_conflict"
    # Diagnostic budget
    DIAGNOSTICS_FULL = "diagnostics_full"


class BundleProofBounds(_GraphFrozen):
    """New finite bundle-proof bounds (objective 018-b).

    Stricter bounds are always permitted; wider bounds are not accepted
    beyond the declared ceilings.  The batch bound, the path bound and
    the source budgets are NOT fields here: they are the ACTUAL
    effective ``GraphBounds`` carried by the namespace (reused exactly:
    ``max_requests``, ``max_path_bytes``, ``max_single_source_bytes``
    and ``max_total_inspected_source_bytes`` with their graph defaults).
    Budget constants are engineering bounds, never a product
    effective-context ``C`` or a RAM ceiling guarantee.
    """

    #: Inspected source-proof candidate occurrences in the bounded batch.
    #: Every SELECTED candidate (a read observation with a present
    #: wrapper output, a COMPLETE process observation) counts BEFORE
    #: dedup or refusal; duplicates and unsupported candidates are
    #: counted, never skipped.
    max_bundles: int = Field(default=128, ge=1, le=10_000)
    #: Represented member occurrences across the proven bundles, counted
    #: BEFORE distinct-slot dedup (a repeated A+A group owns two
    #: attributable member occurrences).
    max_members: int = Field(default=1024, ge=1, le=100_000)
    #: Source slots per proven bundle: ALL slots between proven markers
    #: (and the ends), including empty ones.
    max_segments: int = Field(default=32, ge=1, le=10_000)
    #: One marker literal's UTF-8 byte length INCLUDING the emitted LF.
    max_marker: int = Field(default=256, ge=2, le=65_536)
    #: Shared sum of explicitly bounded searched-window UTF-8 byte
    #: charges over the whole snapshot; NEVER reset per
    #: marker/file/request.
    max_marker_search: int = Field(default=16_777_216, ge=1, le=1_073_741_824)
    #: Total emitted fixed diagnostics on the final public snapshot
    #: (fixed reasons + copied observation/global limitations).
    max_diagnostics: int = Field(default=64, ge=1, le=10_000)


def _canonical_namespace_fields(
    principal: str,
    session: str,
    repository: str,
    route: str,
    model_identity: str,
    config_fingerprint: str,
    bundle_proof_version: str,
    observation_version: str,
    graph_version: str,
    bounds: BundleProofBounds,
    graph_bounds: GraphBounds,
    observation_bounds: ObservationBounds,
) -> bytes:
    payload = [
        principal,
        session,
        repository,
        route,
        model_identity,
        config_fingerprint,
        bundle_proof_version,
        observation_version,
        graph_version,
        json.dumps(bounds.model_dump(mode="json"), sort_keys=True, separators=(",", ":")),
        json.dumps(graph_bounds.model_dump(mode="json"), sort_keys=True, separators=(",", ":")),
        json.dumps(
            observation_bounds.model_dump(mode="json"), sort_keys=True, separators=(",", ":")
        ),
    ]
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")


class BundleProofNamespace(_GraphFrozen):
    """Explicit trusted INTERNAL bundle-proof namespace (R1/R2 law).

    The identity components mirror ``constitution.cache.RequestIdentity``
    and MUST come from the existing trusted ingress
    (``gateway_identity.verify_signed_identity``) or a validated
    standalone configuration.  Object construction is not itself
    authentication.  ``workspace`` is the evidenced root scope observed
    for this snapshot; the FINAL state identity binds it:
    ``scoped_key = sha256(namespace_key + "\\0" + workspace)``.  The
    pre-root ``namespace_key`` binds the identity, the config
    fingerprint, the three versions AND all three effective bound sets
    (the new proof bounds, the actual effective ``GraphBounds`` and the
    actual effective ``ObservationBounds``): a bare caller tag cannot
    hide a different effective configuration.  Noncanonical workspace
    spellings are rejected consistently at every entry point (the scoped
    key always binds the canonical spelling).  The 64-hex keys are
    observable like digests; the private identity values hashing into
    them are suppressed in every operational representation and error.
    """

    principal: str = Field(min_length=1, max_length=256)
    session: str = Field(min_length=1, max_length=256)
    repository: str = Field(min_length=1, max_length=256)
    route: str = Field(min_length=1, max_length=64)
    model_identity: str = Field(min_length=1, max_length=256)
    config_fingerprint: str
    workspace: str
    bundle_proof_version: str = BUNDLE_PROOF_CONTRACT_VERSION
    observation_version: str = OBSERVER_VERSION
    graph_version: str = GRAPH_CONTRACT_VERSION
    bounds: BundleProofBounds = BundleProofBounds()
    graph_bounds: GraphBounds = GraphBounds()
    observation_bounds: ObservationBounds = ObservationBounds()
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

    @field_validator("bundle_proof_version", "observation_version", "graph_version")
    @classmethod
    def _v_version_text(cls, value: str, info: core_schema.FieldValidationInfo) -> str:
        return _check_text(value, info.field_name or "field", 128)

    @field_validator("workspace")
    @classmethod
    def _v_workspace(cls, value: str, info: core_schema.FieldValidationInfo) -> str:
        # Structural + canonical-spelling check only: the ACTUAL
        # configured path bound is enforced by the model-level validator
        # below (field order cannot see graph_bounds).  Noncanonical
        # spellings (double slash, trailing slash, ``.``/empty
        # segments) are rejected consistently at every entry point.
        if validate_workspace(value, 10**9) != value:
            raise _fixed("workspace must be a canonical absolute POSIX path")
        return value

    @model_validator(mode="after")
    def _v_bound_integrity(self) -> BundleProofNamespace:
        # Enforce the ACTUAL supplied graph path bound on the workspace
        # byte length, then recompute both keys from the actual bound
        # identity/versions/bounds/workspace so direct model
        # construction cannot retain inconsistent or forged keys (R2
        # law).
        if len(self.workspace.encode("utf-8")) > self.graph_bounds.max_path_bytes:
            raise _fixed("workspace exceeds the actual configured path bound")
        canonical = _canonical_namespace_fields(
            self.principal,
            self.session,
            self.repository,
            self.route,
            self.model_identity,
            self.config_fingerprint,
            self.bundle_proof_version,
            self.observation_version,
            self.graph_version,
            self.bounds,
            self.graph_bounds,
            self.observation_bounds,
        )
        expected_key = _sha256_hex(canonical)
        expected_scoped = _sha256_hex((expected_key + "\0" + self.workspace).encode("utf-8"))
        if self.namespace_key != expected_key or self.scoped_key != expected_scoped:
            raise _fixed("namespace keys are inconsistent with the bound identity")
        return self

    def __repr__(self) -> str:
        return (
            "BundleProofNamespace("
            f"principal={PRIVATE_ID_PLACEHOLDER}, "
            f"session={PRIVATE_ID_PLACEHOLDER}, "
            f"repository={PRIVATE_ID_PLACEHOLDER}, "
            f"route={PRIVATE_ID_PLACEHOLDER}, "
            f"model_identity={PRIVATE_ID_PLACEHOLDER}, "
            f"config_fingerprint={PRIVATE_ID_PLACEHOLDER}, "
            f"workspace={PRIVATE_ID_PLACEHOLDER}, "
            f"bundle_proof_version={self.bundle_proof_version!r}, "
            f"observation_version={self.observation_version!r}, "
            f"graph_version={self.graph_version!r}, "
            f"bounds={self.bounds!r}, "
            f"graph_bounds={self.graph_bounds!r}, "
            f"observation_bounds={self.observation_bounds!r}, "
            f"namespace_key={self.namespace_key!r}, "
            f"scoped_key={self.scoped_key!r})"
        )

    __str__ = __repr__


def make_bundle_proof_namespace(
    identity: RequestIdentity,
    *,
    model_identity: str,
    config_fingerprint: str,
    workspace: str,
    bounds: BundleProofBounds | None = None,
    graph_bounds: GraphBounds | None = None,
    observation_bounds: ObservationBounds | None = None,
) -> BundleProofNamespace:
    """Build the scoped bundle-proof namespace from a verified identity.

    The caller MUST hold a trusted ingress identity (see module law);
    this factory validates shapes only and performs no authentication.
    The ACTUAL effective bound sets (the new proof bounds, the graph
    bounds and the 017 observation bounds actually used) are bound into
    the pre-root ``namespace_key``; the observed workspace is bound into
    the final ``scoped_key``.  Each argument defaults to the accepted
    default object, so the default namespace is behavior-identical to
    the 017/018-a defaults while remaining explicit and bound.

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
    effective_bounds = bounds if bounds is not None else BundleProofBounds()
    effective_graph = graph_bounds if graph_bounds is not None else GraphBounds()
    effective_observation = (
        observation_bounds if observation_bounds is not None else ObservationBounds()
    )
    if validate_workspace(workspace, effective_graph.max_path_bytes) != workspace:
        raise _fixed("workspace must be a canonical bounded absolute POSIX path")
    canonical = _canonical_namespace_fields(
        identity.principal,
        identity.session,
        identity.repository,
        identity.route,
        model_identity,
        config_fingerprint,
        BUNDLE_PROOF_CONTRACT_VERSION,
        OBSERVER_VERSION,
        GRAPH_CONTRACT_VERSION,
        effective_bounds,
        effective_graph,
        effective_observation,
    )
    namespace_key = _sha256_hex(canonical)
    scoped_key = _sha256_hex((namespace_key + "\0" + workspace).encode("utf-8"))
    return BundleProofNamespace(
        principal=identity.principal,
        session=identity.session,
        repository=identity.repository,
        route=identity.route,
        model_identity=model_identity,
        config_fingerprint=config_fingerprint,
        workspace=workspace,
        bounds=effective_bounds,
        graph_bounds=effective_graph,
        observation_bounds=effective_observation,
        namespace_key=namespace_key,
        scoped_key=scoped_key,
    )


class BundlePiece(_GraphFrozen):
    """One exact original carrier of the complete proven output.

    ``char_span`` is a half-open character span into the EXACT decoded
    JSON string that carried this carrier (legacy: the single result
    carrier's wrapper output span; native: one original process result
    carrier per piece).  Provenance is never renumbered (R3 law).

    The actual exec/poll call association of this piece is retained:
    ``call_id``/``call_location``/``call_position`` name the call that
    produced this carrier (the original exec call for the initial
    piece, the causally associated empty-stdin poll for each poll
    piece, from the 017 observation — never invented from IDs or
    detached join coordinates) and ``result_position`` the exact
    numeric structural position of the result carrier.  The private
    ID value is exact internal association data; operational
    ``str``/``repr`` suppress it (the fixed placeholder law; the
    observable empty no-ID state stays exact).
    """

    piece_index: int = Field(ge=0)
    carrier_location: str = Field(min_length=1)
    char_span: CharSpan
    char_length: int = Field(ge=0)
    byte_length: int = Field(ge=0)
    call_id: str
    call_location: str = Field(min_length=1)
    call_position: int = Field(ge=0)
    result_position: int = Field(ge=0)

    @model_validator(mode="after")
    def _v_span_consistency(self) -> BundlePiece:
        if self.char_length != self.char_span.end - self.char_span.start:
            raise _fixed("piece char_length must equal its carrier span length")
        if not (self.char_length <= self.byte_length <= 4 * self.char_length):
            raise _fixed("piece byte_length must be a valid UTF-8 length")
        return self

    def __repr__(self) -> str:
        call_id = self.call_id if self.call_id == "" else PRIVATE_ID_PLACEHOLDER
        return (
            f"BundlePiece(piece_index={self.piece_index}, "
            f"carrier_location={self.carrier_location!r}, "
            f"char_span={self.char_span!r}, "
            f"char_length={self.char_length}, "
            f"byte_length={self.byte_length}, "
            f"call_id='{call_id}', "
            f"call_location={self.call_location!r}, "
            f"call_position={self.call_position}, "
            f"result_position={self.result_position})"
        )

    __str__ = __repr__


class BundleSegment(_GraphFrozen):
    """One proven source segment: a maximal consecutive cat group
    between proven markers (or the ends).

    ``member_positions`` are the ordered positions (occurrence order)
    into the owning bundle's ``requested_members``; a boundaryless A+B
    group keeps both occurrences with unknown internal boundaries.
    ``member_digest`` is nonempty ONLY when the segment owns exactly one
    attributable member occurrence (in which case it equals the
    segment digest); a distinct-path width of one never earns it.
    ``piece_spans`` are absolute per-carrier sub-spans aligned with the
    bundle's pieces (``None`` = no overlap; a zero-width touch keeps the
    real zero-width carrier span).
    """

    index: int = Field(ge=0)
    member_positions: tuple[int, ...]
    char_length: int = Field(ge=0)
    byte_length: int = Field(ge=0)
    digest: str = Field(pattern=_HEX64)
    member_digest: str | None = Field(default=None, pattern=_HEX64)
    piece_spans: tuple[CharSpan | None, ...]

    @model_validator(mode="after")
    def _v_invariants(self) -> BundleSegment:
        if not self.member_positions:
            raise _fixed("a source segment owns at least one member occurrence")
        if any(position < 0 for position in self.member_positions):
            raise _fixed("segment member positions must be nonnegative")
        if self.char_length == 0 and self.digest != EMPTY_SOURCE_SHA256:
            raise _fixed("an empty segment requires the exact empty digest")
        if self.member_digest is not None:
            if len(self.member_positions) != 1 or self.member_digest != self.digest:
                raise _fixed(
                    "a per-file digest requires exactly one attributable "
                    "member occurrence equal to the segment digest"
                )
        return self


class BundleMarkerFact(_GraphFrozen):
    """One proven non-source marker line (literal + LF) retained for
    later replacement; its exact original intervals are preserved.

    The marker literal itself is source-adjacent text and is NEVER
    echoed: only its length, digest (literal + LF), role and per-carrier
    spans are observable.  A one-character fact (the bare LF) exists
    ONLY as a proven EXTERIOR empty-echo boundary: the accepted 017
    plan law earns an empty fully-quoted literal (``echo ''``) at a
    prefix/suffix position.  The NEW interior-marker law (the finite
    unique-marker partition) is strict and nonempty; interior facts are
    therefore always two characters or more, enforced by the collector
    predicate, not by this record's shape bound.
    """

    index: int = Field(ge=0)
    role: BundleMarkerRole
    char_length: int = Field(ge=1)
    byte_length: int = Field(ge=1)
    digest: str = Field(pattern=_HEX64)
    piece_spans: tuple[CharSpan | None, ...]

    @model_validator(mode="after")
    def _v_length(self) -> BundleMarkerFact:
        if not (self.char_length <= self.byte_length <= 4 * self.char_length):
            raise _fixed("marker byte_length must be a valid UTF-8 length")
        return self


class BundleProof(_GraphFrozen):
    """One complete ordered whole-bundle source proof for one occurrence.

    The record is SELF-CONTAINED: ``source_text`` is the exact aggregate
    source (the ordered proven segment bytes concatenated) and the
    invariants bind every length/digest to it, so the proof never
    depends on caller payload survival.  A bare digest or a
    metadata-only hash is not source proof (018-a seam law).

    Requested versus proven-executed stay distinct:
    ``requested_members`` is the exact original command's requested
    occurrences (order preserved); ``proven_executed`` lists the
    resolved normalized paths proven executed (the 017 law for whole
    proofs; the bridge all-success law for partitioned proofs — global
    exit zero over the finite ``&&`` plan proves every statement).

    ``surface`` is the 017 observation (parser) surface only.  The
    ORIGINAL API source-role classification is explicit and separate:
    ``endpoint`` (the original API endpoint domain of the occurrence)
    and ``source_role`` (a file tool result — no root authority).
    ``root_path``/``root_digest`` are the EFFECTIVE ROOT-AUTHORITY
    BINDING: the evidenced root's role and digest that scope the proof
    (the 018-a root law).  They describe the root that scopes this
    batch; they do NOT confer root authority on the bundle's own file-
    tool-result text.  ``pieces`` are the complete proven output
    carriers (native pieces map only to their original carriers; legacy
    is one result carrier), each with its actual exec/poll call
    association and numeric call/result positions.
    """

    surface: BundleSurface
    kind: BundleProofKind
    grammar: str
    command_digest: str | None = Field(default=None, pattern=_HEX64)
    request_index: int = Field(ge=0)
    call_id: str
    call_location: str = Field(min_length=1)
    call_position: int = Field(ge=0)
    result_location: str = Field(min_length=1)
    #: Exact numeric structural position of the result carrier (the
    #: Responses input item index of the result item, or the index of
    #: the Chat result (tool) message — the 017-m structural position
    #: law; native pieces carry their own per-piece result positions).
    result_position: int = Field(ge=0)
    endpoint: str
    source_role: BundleSourceRole = BundleSourceRole.FILE_TOOL_RESULT
    root_path: str
    root_digest: str = Field(pattern=_HEX64)
    requested_members: tuple[NormalizedPath, ...]
    proven_executed: tuple[str, ...]
    distinct_member_count: int = Field(ge=0)
    pieces: tuple[BundlePiece, ...]
    segments: tuple[BundleSegment, ...]
    markers: tuple[BundleMarkerFact, ...] = ()
    source_text: str
    source_char_length: int = Field(ge=0)
    source_byte_length: int = Field(ge=0)
    source_digest: str = Field(pattern=_HEX64)
    proof_version: str = BUNDLE_PROOF_CONTRACT_VERSION

    @field_validator("grammar")
    @classmethod
    def _v_grammar(cls, value: str) -> str:
        return _check_text(value, "grammar", 128)

    @field_validator("endpoint")
    @classmethod
    def _v_endpoint(cls, value: str) -> str:
        if value not in ("responses", "chat"):
            raise _fixed("endpoint must be an explicit validated endpoint")
        return value

    @field_validator("root_path")
    @classmethod
    def _v_root_path(cls, value: str) -> str:
        return _check_rel_path(value)

    @model_validator(mode="after")
    def _v_source_proof(self) -> BundleProof:
        if not self.requested_members:
            raise _fixed("a bundle proof requires requested member occurrences")
        if len(self.segments) > 1 and self.kind is not BundleProofKind.PARTITIONED:
            raise _fixed("only a partitioned proof carries multiple segments")
        for position, member in enumerate(self.requested_members):
            if member.normalized is None:
                raise _fixed("every represented member must be resolved")
            del position
        distinct = len({m.normalized for m in self.requested_members if m.normalized})
        if self.distinct_member_count != distinct:
            raise _fixed("distinct_member_count must equal the distinct resolved width")
        if len(self.proven_executed) != len(self.requested_members):
            raise _fixed("proven_executed must align with the requested occurrences")
        if len(self.pieces) < 1:
            raise _fixed("a bundle proof requires its original output carrier(s)")
        total_chars = sum(segment.char_length for segment in self.segments)
        total_bytes = sum(segment.byte_length for segment in self.segments)
        if (
            self.source_char_length != len(self.source_text)
            or total_chars != self.source_char_length
        ):
            raise _fixed("source_char_length must equal the exact aggregate text")
        if self.source_byte_length != len(self.source_text.encode("utf-8")):
            raise _fixed("source_byte_length must equal the exact UTF-8 text length")
        if total_bytes != self.source_byte_length:
            raise _fixed("source_byte_length must equal the ordered segment total")
        if sha256_hex(self.source_text) != self.source_digest:
            raise _fixed("source_digest must equal the exact aggregate text digest")
        if self.source_char_length == 0 and self.source_digest != EMPTY_SOURCE_SHA256:
            raise _fixed("an empty source requires the exact empty digest")
        if self.source_digest == EMPTY_SOURCE_SHA256 and self.source_char_length != 0:
            raise _fixed("the empty digest requires an empty source")
        return self

    def __repr__(self) -> str:
        # Operational representation: fixed enums, counts, locations,
        # spans, digests and resolved paths stay observable; the exact
        # source text and the private call ID value never do.
        members = [
            f"{{{member.form.value}:{member.normalized}}}" for member in self.requested_members
        ]
        return (
            f"BundleProof(surface={self.surface.value!r}, "
            f"kind={self.kind.value!r}, grammar={self.grammar!r}, "
            f"command_digest={self.command_digest!r}, "
            f"request_index={self.request_index}, call_id='{PRIVATE_ID_PLACEHOLDER}', "
            f"call_location={self.call_location!r}, call_position={self.call_position}, "
            f"result_location={self.result_location!r}, "
            f"result_position={self.result_position}, "
            f"root_path={self.root_path!r}, root_digest={self.root_digest!r}, "
            f"requested_members=[{', '.join(members)}], "
            f"endpoint={self.endpoint!r}, source_role={self.source_role.value!r}, "
            f"proven_executed={self.proven_executed!r}, "
            f"distinct_member_count={self.distinct_member_count}, "
            f"pieces={len(self.pieces)}, "
            f"segments={len(self.segments)}, "
            f"markers={len(self.markers)}, "
            f"source_text='<protected {self.source_char_length} chars>', "
            f"source_char_length={self.source_char_length}, "
            f"source_byte_length={self.source_byte_length}, "
            f"source_digest={self.source_digest!r}, "
            f"proof_version={self.proof_version!r})"
        )

    __str__ = __repr__


class BundleProofSnapshot(_GraphFrozen):
    """Pure bundle-proof result for one bounded batch (objective 018-b).

    ``root_path``/``root_digest`` are the effective root-authority
    binding of the evidenced batch (the single authoritative Responses
    root); they scope every bundle but confer no authority on the
    bundle carriers, whose original source role is
    ``BundleProof.source_role`` (a file tool result).  Carries scoped
    keys, resolved paths, digests, counts and fixed reasons only; the
    raw source text lives exclusively inside the self-contained
    ``BundleProof`` records (repr-suppressed).
    ``candidates_inspected`` counts EVERY selected source candidate
    (unsupported and duplicates included) before dedup/refusal.
    ``conflicts`` are snapshot-level fixed refusals; ``diagnostics`` are
    candidate-level fixed refusals; both are bounded together with
    ``observation_limitations`` by ``max_diagnostics`` (overflow is ONE
    fixed ``DIAGNOSTICS_FULL`` refusal, never unbounded copied reasons).
    """

    namespace: BundleProofNamespace
    outcome: BundleProofOutcome
    root_path: str | None = None
    root_digest: str | None = Field(default=None, pattern=_HEX64)
    bundles: tuple[BundleProof, ...] = ()
    conflicts: tuple[BundleLimitation, ...] = ()
    diagnostics: tuple[BundleLimitation, ...] = ()
    observation_limitations: tuple[Limitation, ...] = ()
    request_count: int = Field(default=0, ge=0)
    candidates_inspected: int = Field(default=0, ge=0)
    marker_search_bytes: int = Field(default=0, ge=0)
    source_bytes_inspected: int = Field(default=0, ge=0)

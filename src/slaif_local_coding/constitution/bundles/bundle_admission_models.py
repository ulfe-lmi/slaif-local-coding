"""Typed immutable records for the 018-c bundle-admission slice.

Pure, inert, and versioned as ``cache-bundle-admission/v1``.  These
records carry the lean/greedy admission decision for one bounded batch
of ORIGINAL decoded requests under one explicit trusted namespace: the
required first-class root entry, the admitted file-bundle entries with
their canonical structural content-key records, the group-owned
dependency certificates (the boundaryless all-eligible common-base law),
the complete reverse member-path index and the source-version
observations retained independently of admission.

Privacy law (inherited from the 018-a/018-b records): operational
``str``/``repr``/validation errors never echo raw source content,
private call/result ID values or identity VALUES.  Digests, spans,
counts, locations, fixed enums, scoped keys and content keys are
observable like any derived digest.  The frozen base adds
``hide_input_in_errors`` so Pydantic validation errors on these records
(direct or nested) never echo caller-supplied input values; the 017
base class and the 018-a/018-b records are not modified.

Namespace law (R2, 018-a/018-b pattern): every record is scoped by an
explicit trusted namespace whose 64-hex keys bind the identity, the
config fingerprint, the admission/proof/observation/graph versions, the
explicit admission MODE and ALL four effective bound sets (the new
admission bounds, the accepted proof bounds, the ACTUAL effective
``GraphBounds`` and the ACTUAL effective ``ObservationBounds``): a bare
caller tag cannot hide a different mode or effective configuration.
The keys are recomputed on direct construction, so a forged or
inconsistent key pair cannot be retained.  Object construction is NOT
authentication: a namespace is only as trusted as the verified
identity the caller passed (``gateway_identity.verify_signed_identity``
/ validated standalone configuration).

Authority law: the required root entry is the ONLY record carrying
root authority (ROOT-ENVELOPE AUTHORITY from the legitimate effective
Responses envelope).  Every file-bundle entry stays a file tool result
(dependency/data provenance) even when its bytes equal the root or its
text names ``AGENTS.md``; the ``member_classes`` vector records the
meaningful compiler authority of each represented member occurrence
(eligible versus greedy-background) without upgrading any of them.

No filesystem, network or shell facility is imported or used.
"""

from __future__ import annotations

import json
from enum import StrEnum

from pydantic import Field, field_validator, model_validator
from pydantic_core import core_schema

from ..cache import RequestIdentity
from .bundle_proof_models import (
    BUNDLE_PROOF_CONTRACT_VERSION,
    ROOT_FILENAME,
    BundleProof,
    BundleProofBounds,
)
from .client_paths import validate_workspace
from .graph_models import (
    GRAPH_CONTRACT_VERSION,
    REFERENCE_GRAMMAR,
    CandidateSyntax,
    GraphBounds,
    NodeStatus,
    ReferenceCandidate,
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
    ObservationBounds,
    OccurrenceKind,
    RootStatus,
)

ADMISSION_CONTRACT_VERSION = "cache-bundle-admission/v1"

_HEX64 = r"^[0-9a-f]{64}$"


class AdmissionMode(StrEnum):
    """Explicit admission mode (default ``lean``).

    Immutable within one admission scope: the mode is bound into the
    namespace key and the structural content key, and it is never
    changed implicitly in response to outcomes.
    """

    LEAN = "lean"
    GREEDY = "greedy"


class EntryClass(StrEnum):
    """Closed entry classes: the required root entry versus file entries.

    The two classes are never conflated: a root entry carries
    ROOT-ENVELOPE AUTHORITY; a file entry is file-tool-result
    dependency/data provenance even for identical bytes at
    ``AGENTS.md``.
    """

    ROOT_ENTRY = "root_entry"
    FILE_BUNDLE_ENTRY = "file_bundle_entry"


class MemberClass(StrEnum):
    """Per represented-member-occurrence compiler authority vector.

    ``eligible``: the member path is independently root-reachable in
    the accepted raw-reference graph of this snapshot (eligibility,
    not acquisition: a reachable content-missing node is eligible).
    ``greedy_background``: the member is co-admitted by greedy mode
    without independent eligibility; it keeps background provenance
    and cannot acquire root/system authority by co-occurrence.
    """

    ELIGIBLE = "eligible"
    GREEDY_BACKGROUND = "greedy_background"


class BoundaryClass(StrEnum):
    """Ownership-boundary class of one canonical key group.

    ``proven``: the group boundary is proven (a singleton, or a
    partition segment with its exact group digest).  ``boundaryless``:
    the group has no proven internal boundary; its individual members
    carry unknown attribution (no individual hash is ever invented
    from the width).
    """

    PROVEN = "proven"
    BOUNDARYLESS = "boundaryless"


class AdmissionOutcome(StrEnum):
    """Fixed outcome vocabulary (the accepted 018-a/018-b values)."""

    COMPLETE = "complete"
    NO_ROOT = "no_root"
    WORKSPACE_UNPROVEN = "workspace_unproven"
    ROOT_CONFLICT = "root_conflict"
    VERSION_CONFLICT = "version_conflict"
    OVER_BOUND = "over_bound"


class AdmissionLimitation(StrEnum):
    """CLOSED fixed vocabulary for every emitted admission reason.

    Free-form strings and arbitrary text are rejected by validation and
    never echoed.  The set is the union of (a) the admission's own
    budget/non-acquisition refusals (one per ``BundleAdmissionBounds``
    member, the AND/OR derivation-depth law, the total diagnostics
    bound and the typed ``CANDIDATE_UNPROVEN`` non-acquisition) and
    (b) the propagated closed-vocabulary reasons of the accepted
    stages, carried under their EXACT fixed names (propagated, never
    relabeled): the 018-a root/workspace binding and scoped binding
    laws, the 018-a/018-b consistency laws, the shared
    batch/source/candidate/work ceilings (one cumulative ledger over
    the ACTUAL effective graph/observation values) and the
    proof-stage ceilings and per-candidate fixed reasons.  The
    ``CANDIDATE_UNPROVEN`` member is the typed non-acquisition for an
    acquired bundle the mode/eligibility law does not admit (no
    admission, no partial retention).
    """

    # Root / workspace binding (the 018-a law, propagated)
    NO_ROOT = "no_root"
    WORKSPACE_UNPROVEN = "workspace_unproven"
    COMPETING_ROOTS = "competing_roots"
    ROOT_CONTEXT_MISMATCH = "root_context_mismatch"
    # Consistency / version (the 018-a/018-b laws, propagated)
    SEAM_CONFLICT = "seam_conflict"
    SOURCE_CONFLICT = "source_conflict"
    VERSION_UNSUPPORTED = "version_unsupported"
    # Scoped binding
    NAMESPACE_MISMATCH = "namespace_mismatch"
    WORKSPACE_MISMATCH = "workspace_mismatch"
    BOUNDS_MISMATCH = "bounds_mismatch"
    # Shared batch/source/candidate budgets (the ACTUAL effective
    # graph/observation ceilings, ONE cumulative ledger, never reset
    # per request/group/pass)
    BATCH_OVER_BOUND = "batch_over_bound"
    SOURCE_OVER_BOUND = "source_over_bound"
    TOTAL_SOURCE_OVER_BOUND = "total_source_over_bound"
    DOCUMENT_OVER_BOUND = "document_over_bound"
    CANDIDATES_PER_DOCUMENT_OVER_BOUND = "candidates_per_document_over_bound"
    CANDIDATES_TOTAL_OVER_BOUND = "candidates_total_over_bound"
    NODES_OVER_BOUND = "nodes_over_bound"
    EDGES_OVER_BOUND = "edges_over_bound"
    WORK_UNITS_EXHAUSTED = "work_units_exhausted"
    # Proof-stage budgets (the ACTUAL effective proof ceilings)
    BUNDLES_OVER_BOUND = "bundles_over_bound"
    MEMBERS_OVER_BOUND = "members_over_bound"
    SEGMENTS_OVER_BOUND = "segments_over_bound"
    MARKER_OVER_BOUND = "marker_over_bound"
    MARKER_SEARCH_OVER_BOUND = "marker_search_over_bound"
    # Admission budget refusals (one per BundleAdmissionBounds member)
    ENTRIES_OVER_BOUND = "entries_over_bound"
    MEMBER_OCCURRENCES_OVER_BOUND = "member_occurrences_over_bound"
    REVERSE_ASSOCIATIONS_OVER_BOUND = "reverse_associations_over_bound"
    # The AND/OR derivation-depth law (least complete derivation,
    # applied after the bounded certificate fixed point)
    DERIVATION_DEPTH_OVER_BOUND = "derivation_depth_over_bound"
    # Total emitted diagnostics
    DIAGNOSTICS_FULL = "diagnostics_full"
    # Typed non-acquisition (no admission, nothing retained)
    CANDIDATE_UNPROVEN = "candidate_unproven"
    # Propagated per-candidate fixed reasons (the accepted proof-stage
    # closed vocabulary, exact names)
    PLAN_UNSUPPORTED = "plan_unsupported"
    MEMBER_UNRESOLVED = "member_unresolved"
    MEMBER_PATH_OVER_BOUND = "member_path_over_bound"
    MARKER_EMPTY = "marker_empty"
    MARKER_MISSING = "marker_missing"
    MARKER_DUPLICATE = "marker_duplicate"
    MARKER_ORDER = "marker_order"
    MARKER_OVERLAP = "marker_overlap"
    SEGMENT_UNEXPLAINED = "segment_unexplained"
    OUTPUT_INCONSISTENT = "output_inconsistent"
    # Defensive scan integrity (the accepted stage laws, propagated)
    MALFORMED_UNICODE = "malformed_unicode"


class BundleAdmissionBounds(_GraphFrozen):
    """New finite admission bounds (objective 018-c, per SNAPSHOT).

    These are per-snapshot admission decisions, never session
    eviction.  The order fixes the defaults AND the hard ceilings at
    exactly 128 / 1024 / 4096 / 64: integers 1..ceiling are permitted
    (stricter settings allowed), and ANY wider direct or factory
    construction is refused.  The shared admission-closure work ledger
    is the ACTUAL effective ``GraphBounds.max_work_units`` carried by
    the namespace (shared with the accepted graph closure; never an
    independently reset or wider admission field).  The batch, path and
    source budgets are NOT fields here either: they are the ACTUAL
    effective ``GraphBounds`` / ``ObservationBounds`` /
    ``BundleProofBounds`` carried by the namespace (reused exactly).
    Budget constants are engineering bounds, never a product
    effective-context ``C`` or a RAM ceiling guarantee.
    """

    #: Retained DEDUPLICATED semantic entries (distinct content keys,
    #: the required root entry included).  Duplicate original
    #: observations consume the inspection/candidate budgets before
    #: dedup; this bound counts the deduplicated keys.
    max_entries: int = Field(default=128, ge=1, le=128)
    #: Retained represented member OCCURRENCES charged before
    #: distinct-path width (a repeated A+A group owns two occurrences).
    max_member_occurrences: int = Field(default=1024, ge=1, le=1024)
    #: Reverse-index association ATTEMPTS (every actual attempt counts
    #: before dedup; the root association is one of them).
    max_reverse_associations: int = Field(default=4096, ge=1, le=4096)
    #: Total emitted fixed diagnostics on the final public snapshot
    #: (conflicts + candidate diagnostics + observation/global
    #: limitations, including early refusals).
    max_diagnostics: int = Field(default=64, ge=1, le=64)


def _canonical_namespace_fields(
    principal: str,
    session: str,
    repository: str,
    route: str,
    model_identity: str,
    config_fingerprint: str,
    admission_version: str,
    graph_version: str,
    reference_version: str,
    proof_version: str,
    observation_version: str,
    mode: str,
    bounds: BundleAdmissionBounds,
    proof_bounds: BundleProofBounds,
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
        admission_version,
        graph_version,
        reference_version,
        proof_version,
        observation_version,
        mode,
        json.dumps(bounds.model_dump(mode="json"), sort_keys=True, separators=(",", ":")),
        json.dumps(proof_bounds.model_dump(mode="json"), sort_keys=True, separators=(",", ":")),
        json.dumps(graph_bounds.model_dump(mode="json"), sort_keys=True, separators=(",", ":")),
        json.dumps(
            observation_bounds.model_dump(mode="json"), sort_keys=True, separators=(",", ":")
        ),
    ]
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")


class BundleAdmissionNamespace(_GraphFrozen):
    """Explicit trusted INTERNAL bundle-admission namespace (R1/R2 law).

    The identity components mirror ``constitution.cache.RequestIdentity``
    and MUST come from the existing trusted ingress
    (``gateway_identity.verify_signed_identity``) or a validated
    standalone configuration.  Object construction is not itself
    authentication.  ``workspace`` is the evidenced root scope observed
    for this snapshot; the FINAL state identity binds it:
    ``scoped_key = sha256(namespace_key + "\0" + workspace)``.  The
    pre-root ``namespace_key`` binds the identity, the config
    fingerprint, the explicit MODE, the four versions AND all four
    effective bound sets (the new admission bounds, the accepted proof
    bounds, the ACTUAL effective ``GraphBounds`` and the ACTUAL
    effective ``ObservationBounds``): a bare caller tag cannot hide a
    different mode or effective configuration.  Noncanonical workspace
    spellings are rejected consistently at every entry point (the
    scoped key always binds the canonical spelling).  The 64-hex keys
    are observable like digests; the private identity values hashing
    into them are suppressed in every operational representation and
    error.
    """

    principal: str = Field(min_length=1, max_length=256)
    session: str = Field(min_length=1, max_length=256)
    repository: str = Field(min_length=1, max_length=256)
    route: str = Field(min_length=1, max_length=64)
    model_identity: str = Field(min_length=1, max_length=256)
    config_fingerprint: str
    workspace: str
    mode: AdmissionMode = AdmissionMode.LEAN
    admission_version: str = ADMISSION_CONTRACT_VERSION
    observation_version: str = OBSERVER_VERSION
    graph_version: str = GRAPH_CONTRACT_VERSION
    #: The actual accepted reference-scan grammar/registry identity
    #: (the accepted 018-a ``REFERENCE_GRAMMAR``), bound at scope
    #: level exactly like the accepted ``GraphNamespace`` law: the
    #: closure consumes the accepted bounded scanner, so its actual
    #: grammar identity is scope-binding material.
    reference_version: str = REFERENCE_GRAMMAR
    proof_version: str = BUNDLE_PROOF_CONTRACT_VERSION
    bounds: BundleAdmissionBounds = BundleAdmissionBounds()
    proof_bounds: BundleProofBounds = BundleProofBounds()
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

    @field_validator(
        "admission_version",
        "observation_version",
        "graph_version",
        "reference_version",
        "proof_version",
    )
    @classmethod
    def _v_version_text(cls, value: str, info: core_schema.FieldValidationInfo) -> str:
        return _check_text(value, info.field_name or "field", 128)

    @field_validator("workspace")
    @classmethod
    def _v_workspace(cls, value: str, info: core_schema.FieldValidationInfo) -> str:
        if validate_workspace(value, 10**9) != value:
            raise _fixed("workspace must be a canonical absolute POSIX path")
        return value

    @model_validator(mode="after")
    def _v_bound_integrity(self) -> BundleAdmissionNamespace:
        # Enforce the ACTUAL supplied graph path bound on the workspace
        # byte length, then recompute both keys from the actual bound
        # identity/versions/mode/bounds/workspace so direct model
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
            self.admission_version,
            self.graph_version,
            self.reference_version,
            self.proof_version,
            self.observation_version,
            self.mode.value,
            self.bounds,
            self.proof_bounds,
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
            "BundleAdmissionNamespace("
            f"principal={PRIVATE_ID_PLACEHOLDER}, "
            f"session={PRIVATE_ID_PLACEHOLDER}, "
            f"repository={PRIVATE_ID_PLACEHOLDER}, "
            f"route={PRIVATE_ID_PLACEHOLDER}, "
            f"model_identity={PRIVATE_ID_PLACEHOLDER}, "
            f"config_fingerprint={PRIVATE_ID_PLACEHOLDER}, "
            f"workspace={PRIVATE_ID_PLACEHOLDER}, "
            f"mode={self.mode!r}, "
            f"admission_version={self.admission_version!r}, "
            f"reference_version={self.reference_version!r}, "
            f"observation_version={self.observation_version!r}, "
            f"graph_version={self.graph_version!r}, "
            f"proof_version={self.proof_version!r}, "
            f"bounds={self.bounds!r}, "
            f"proof_bounds={self.proof_bounds!r}, "
            f"graph_bounds={self.graph_bounds!r}, "
            f"observation_bounds={self.observation_bounds!r}, "
            f"namespace_key={self.namespace_key!r}, "
            f"scoped_key={self.scoped_key!r})"
        )

    __str__ = __repr__


def make_bundle_admission_namespace(
    identity: RequestIdentity,
    *,
    model_identity: str,
    config_fingerprint: str,
    workspace: str,
    mode: AdmissionMode = AdmissionMode.LEAN,
    bounds: BundleAdmissionBounds | None = None,
    proof_bounds: BundleProofBounds | None = None,
    graph_bounds: GraphBounds | None = None,
    observation_bounds: ObservationBounds | None = None,
) -> BundleAdmissionNamespace:
    """Factory for an explicit trusted admission namespace.

    ``identity`` must already be verified by the existing trusted
    ingress; this factory validates SHAPES only and raises plain
    ``ValueError`` with fixed messages that never echo the offending
    value.  Noncanonical workspace spellings and over-bound workspaces
    are rejected here (the model-level validator enforces the same on
    direct construction).
    """
    if validate_workspace(workspace, 10**9) != workspace:
        raise _fixed("workspace must be a canonical absolute POSIX path")
    effective_graph = graph_bounds or GraphBounds()
    if len(workspace.encode("utf-8")) > effective_graph.max_path_bytes:
        raise _fixed("workspace exceeds the actual configured path bound")
    effective_bounds = bounds or BundleAdmissionBounds()
    effective_proof = proof_bounds or BundleProofBounds()
    effective_observation = observation_bounds or ObservationBounds()
    canonical = _canonical_namespace_fields(
        identity.principal,
        identity.session,
        identity.repository,
        identity.route,
        model_identity,
        config_fingerprint,
        ADMISSION_CONTRACT_VERSION,
        GRAPH_CONTRACT_VERSION,
        REFERENCE_GRAMMAR,
        BUNDLE_PROOF_CONTRACT_VERSION,
        OBSERVER_VERSION,
        mode.value,
        effective_bounds,
        effective_proof,
        effective_graph,
        effective_observation,
    )
    namespace_key = _sha256_hex(canonical)
    scoped_key = _sha256_hex((namespace_key + "\0" + workspace).encode("utf-8"))
    return BundleAdmissionNamespace(
        principal=identity.principal,
        session=identity.session,
        repository=identity.repository,
        route=identity.route,
        model_identity=model_identity,
        config_fingerprint=config_fingerprint,
        workspace=workspace,
        mode=mode,
        bounds=effective_bounds,
        proof_bounds=effective_proof,
        graph_bounds=effective_graph,
        observation_bounds=effective_observation,
        namespace_key=namespace_key,
        scoped_key=scoped_key,
    )


class OwnershipGroup(_GraphFrozen):
    """One canonical key-ownership group (ENTRY-LOCAL descriptor).

    The groups partition the entry's ordered member occurrences: every
    occurrence index appears in exactly one group, groups are ordered,
    and the indices within a group are strictly increasing.  The
    renumbering is solely a canonical key descriptor: the original
    proof ``member_positions``, piece spans, IDs and positions are
    retained unchanged in the embedded provenance.

    ``group_digest`` is nonempty ONLY for a proven group (a singleton
    with its exact attributable digest) or a multi-operand group whose
    segment bytes are exactly proven (the group digest is known while
    the per-member attribution inside it stays unknown).  A
    boundaryless group NEVER receives an individual per-file hash from
    its width.
    """

    group_index: int = Field(ge=0)
    member_occurrence_indices: tuple[int, ...] = Field(min_length=1)
    boundary_class: BoundaryClass
    group_digest: str | None = Field(default=None, pattern=_HEX64)

    @model_validator(mode="after")
    def _v_group(self) -> OwnershipGroup:
        indices = self.member_occurrence_indices
        if len(set(indices)) != len(indices):
            raise _fixed("group occurrence indices must be distinct")
        if indices != tuple(sorted(indices)):
            raise _fixed("group occurrence indices must be increasing")
        if self.boundary_class is BoundaryClass.PROVEN and self.group_digest is None:
            raise _fixed("a proven group requires its exact group digest")
        if self.boundary_class is BoundaryClass.BOUNDARYLESS:
            # A boundaryless multi-operand group may carry its exact
            # segment digest (group-level attribution) but never a
            # per-file hash; a boundaryless SINGLETON is impossible
            # (a singleton is proven by its single occurrence).
            if len(indices) == 1:
                raise _fixed("a singleton group is proven, never boundaryless")
        return self

    def __repr__(self) -> str:
        return (
            "OwnershipGroup("
            f"group_index={self.group_index!r}, "
            f"member_occurrence_indices={self.member_occurrence_indices!r}, "
            f"boundary_class={self.boundary_class!r}, "
            f"group_digest={self.group_digest!r})"
        )

    __str__ = __repr__


class BundleKeyRecord(_GraphFrozen):
    """The explicit CANONICAL semantic-key record (binding law).

    Separate from immutable occurrence/carrier evidence: it binds the
    ACTUAL trusted namespace-derived scope (principal, session,
    repository, route), the scoped actual configuration and versions,
    the ACTUAL effective bound sets (admission, proof, graph,
    observation), the normalized ordered member OCCURRENCES, the
    explicit per-occurrence authority vector, the exact aggregate
    source digest, the source/authority class and the meaningful
    source-ownership partition.  ``content_key`` is recomputed from
    these fields on every construction (factory and direct): a forged
    key is refused.  Binding the scope and the effective bounds inside
    the key (not only in the owning entry/namespace) means a record
    can never collide across scopes nor be reused after the scope's
    effective configuration changes.  The explicit authority vector
    (eligible versus greedy-background per occurrence) is meaningful
    compiler authority: a greedy-background member must not reuse a
    key after its independent graph eligibility later changes.

    Deliberately EXCLUDED (provenance, not semantic content):
    incidental call IDs, positions, occurrence IDs, per-occurrence
    parser command-form labels (read/process, single/loop/plan), the
    current graph serialization, unrelated acquisitions, revisions and
    causal frontiers.  Meaningful root/version/config/authority
    changes remain bound (workspace, root digest, mode, versions,
    config fingerprint, scope identity, effective bounds).
    """

    admission_version: str = ADMISSION_CONTRACT_VERSION
    graph_version: str = GRAPH_CONTRACT_VERSION
    reference_version: str = REFERENCE_GRAMMAR
    proof_version: str = BUNDLE_PROOF_CONTRACT_VERSION
    observation_version: str = OBSERVER_VERSION
    mode: AdmissionMode
    authority_class: EntryClass
    principal: str = Field(min_length=1, max_length=256)
    session: str = Field(min_length=1, max_length=256)
    repository: str = Field(min_length=1, max_length=256)
    route: str = Field(min_length=1, max_length=64)
    config_fingerprint: str
    model_identity: str = Field(min_length=1, max_length=256)
    workspace: str
    root_digest: str = Field(pattern=_HEX64)
    admission_bounds: BundleAdmissionBounds = BundleAdmissionBounds()
    proof_bounds: BundleProofBounds = BundleProofBounds()
    graph_bounds: GraphBounds = GraphBounds()
    observation_bounds: ObservationBounds = ObservationBounds()
    member_occurrences: tuple[str, ...] = Field(min_length=1)
    member_classes: tuple[MemberClass, ...] = Field(min_length=1)
    aggregate_source_digest: str = Field(pattern=_HEX64)
    ownership_groups: tuple[OwnershipGroup, ...] = Field(min_length=1)
    content_key: str

    @field_validator("principal", "session", "repository", "route", "model_identity")
    @classmethod
    def _v_identity_text(cls, value: str, info: core_schema.FieldValidationInfo) -> str:
        limit = 256 if info.field_name != "route" else 64
        return _check_text(value, info.field_name or "field", limit)

    @field_validator(
        "admission_version",
        "graph_version",
        "reference_version",
        "proof_version",
        "observation_version",
    )
    @classmethod
    def _v_versions(cls, value: str, info: core_schema.FieldValidationInfo) -> str:
        return _check_text(value, info.field_name or "field", 128)

    @field_validator("config_fingerprint", "content_key")
    @classmethod
    def _v_hex64(cls, value: str, info: core_schema.FieldValidationInfo) -> str:
        return _check_hex64(value, info.field_name or "field")

    @field_validator("member_occurrences")
    @classmethod
    def _v_members(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        for path in value:
            _check_rel_path(path)
        return value

    @model_validator(mode="after")
    def _v_key(self) -> BundleKeyRecord:
        # The ownership groups must partition the member occurrences
        # exactly (entry-local law).
        seen: list[int] = []
        for position, group in enumerate(self.ownership_groups):
            if group.group_index != position:
                raise _fixed("ownership group indices must be dense and ordered")
            seen.extend(group.member_occurrence_indices)
        if sorted(seen) != list(range(len(self.member_occurrences))) or len(seen) != len(set(seen)):
            raise _fixed("ownership groups must partition the member occurrences")
        if len(self.member_classes) != len(self.member_occurrences):
            raise _fixed("member_classes must align with the member occurrences")
        canonical = {
            "admission_version": self.admission_version,
            "graph_version": self.graph_version,
            "reference_version": self.reference_version,
            "proof_version": self.proof_version,
            "observation_version": self.observation_version,
            "mode": self.mode.value,
            "authority_class": self.authority_class.value,
            "principal": self.principal,
            "session": self.session,
            "repository": self.repository,
            "route": self.route,
            "config_fingerprint": self.config_fingerprint,
            "model_identity": self.model_identity,
            "workspace": self.workspace,
            "root_digest": self.root_digest,
            "admission_bounds": self.admission_bounds.model_dump(mode="json"),
            "proof_bounds": self.proof_bounds.model_dump(mode="json"),
            "graph_bounds": self.graph_bounds.model_dump(mode="json"),
            "observation_bounds": self.observation_bounds.model_dump(mode="json"),
            "member_occurrences": list(self.member_occurrences),
            "member_classes": [m.value for m in self.member_classes],
            "aggregate_source_digest": self.aggregate_source_digest,
            "ownership_groups": [
                {
                    "member_occurrence_indices": list(g.member_occurrence_indices),
                    "boundary_class": g.boundary_class.value,
                    "group_digest": g.group_digest,
                }
                for g in self.ownership_groups
            ],
        }
        expected = _sha256_hex(
            json.dumps(canonical, sort_keys=True, separators=(",", ":")).encode("utf-8")
        )
        if self.content_key != expected:
            raise _fixed("content_key is inconsistent with the canonical key record")
        return self

    def __repr__(self) -> str:
        return (
            "BundleKeyRecord("
            f"mode={self.mode!r}, "
            f"authority_class={self.authority_class!r}, "
            f"principal={PRIVATE_ID_PLACEHOLDER}, "
            f"session={PRIVATE_ID_PLACEHOLDER}, "
            f"repository={PRIVATE_ID_PLACEHOLDER}, "
            f"route={PRIVATE_ID_PLACEHOLDER}, "
            f"config_fingerprint={PRIVATE_ID_PLACEHOLDER}, "
            f"model_identity={PRIVATE_ID_PLACEHOLDER}, "
            f"workspace={PRIVATE_ID_PLACEHOLDER}, "
            f"root_digest={self.root_digest!r}, "
            f"reference_version={self.reference_version!r}, "
            f"admission_bounds={self.admission_bounds!r}, "
            f"proof_bounds={self.proof_bounds!r}, "
            f"graph_bounds={self.graph_bounds!r}, "
            f"observation_bounds={self.observation_bounds!r}, "
            f"member_occurrences={self.member_occurrences!r}, "
            f"member_classes={self.member_classes!r}, "
            f"aggregate_source_digest={self.aggregate_source_digest!r}, "
            f"ownership_groups={self.ownership_groups!r}, "
            f"content_key={self.content_key!r})"
        )

    __str__ = __repr__


class BundleEntry(_GraphFrozen):
    """One retained admission entry (the required root entry or a file
    bundle entry).

    The entry is SELF-CONTAINED: a root entry carries the exact
    extracted root source bytes (repr-suppressed, invariants bind the
    lengths and digest to them); a file entry embeds the accepted
    018-b ``BundleProof`` (itself self-contained, repr-suppressed) with
    the complete original provenance retained separately.  The
    ``content_key`` / ``key_record`` bind the structural identity;
    ``member_classes`` is the meaningful per-occurrence compiler
    authority vector (eligible versus greedy-background).
    """

    entry_class: EntryClass
    content_key: str
    key_record: BundleKeyRecord
    width: int = Field(ge=1)
    member_classes: tuple[MemberClass, ...] = Field(min_length=1)
    root_digest: str = Field(pattern=_HEX64)
    #: Exact extracted ROOT source bytes (root entries only; file
    #: entries keep their bytes exclusively inside the embedded proof).
    source_text: str | None = None
    source_char_length: int | None = Field(default=None, ge=0)
    source_byte_length: int | None = Field(default=None, ge=0)
    proof: BundleProof | None = None
    #: Original Responses user-envelope root occurrences (root entries
    #: only; same-root duplicates dedup as an entry while preserving
    #: their bounded original provenance, the ACTUAL originating
    #: request index included).
    envelope_occurrences: tuple[RootEnvelopeOccurrence, ...] = ()
    #: Ordered indices into the embedded proof's segments naming the
    #: ADMITTED region (file entries only).  The original proof is
    #: never reindexed or refabricated: its complete requested members,
    #: member positions, pieces and segments stay untouched; only the
    #: admitted region's semantic facts (ordered admitted members,
    #: admitted region digest, entry-local ownership groups) bind the
    #: key record.  A whole-bundle admission names every segment.
    admitted_segments: tuple[int, ...] = ()

    @field_validator("content_key")
    @classmethod
    def _v_content_key(cls, value: str) -> str:
        return _check_hex64(value, "content_key")

    @model_validator(mode="after")
    def _v_entry(self) -> BundleEntry:
        if self.content_key != self.key_record.content_key:
            raise _fixed("entry content_key must equal the key record content_key")
        if self.key_record.authority_class is not self.entry_class:
            raise _fixed("key record authority class must equal the entry class")
        if self.key_record.root_digest != self.root_digest:
            raise _fixed("entry root binding must equal the key record root binding")
        if len(self.member_classes) != len(self.key_record.member_occurrences):
            raise _fixed("member_classes must align with the member occurrences")
        if tuple(self.member_classes) != tuple(self.key_record.member_classes):
            raise _fixed("entry authority vector must equal the key record vector")
        if self.entry_class is EntryClass.ROOT_ENTRY:
            if self.admitted_segments:
                raise _fixed("the root entry admits the root, not proof segments")
            if self.source_text is None:
                raise _fixed("a root entry carries its exact extracted source bytes")
            text = self.source_text
            if self.source_char_length != len(text):
                raise _fixed("root source_char_length must equal the retained bytes")
            if self.source_byte_length != len(text.encode("utf-8")):
                raise _fixed("root source_byte_length must equal the retained bytes")
            if _sha256_hex(text.encode("utf-8")) != self.root_digest:
                raise _fixed("root digest must equal the retained root bytes")
            if self.key_record.member_occurrences != (ROOT_FILENAME,):
                raise _fixed("a root entry is one occurrence at the normalized root")
            if self.key_record.aggregate_source_digest != self.root_digest:
                raise _fixed("root aggregate digest must equal the root digest")
            if self.width != 1 or self.member_classes != (MemberClass.ELIGIBLE,):
                raise _fixed("the root is one always-eligible root-occurrence member")
            if self.proof is not None or self.envelope_occurrences:
                # The envelope occurrences are retained for root
                # entries; a proof is never a root carrier.
                if self.proof is not None:
                    raise _fixed("a root entry never embeds a file-tool proof")
        else:
            if self.proof is None:
                raise _fixed("a file entry embeds its accepted 018-b bundle proof")
            if self.source_text is not None:
                raise _fixed("file entry bytes live exclusively inside the proof")
            if self.envelope_occurrences:
                raise _fixed("envelope occurrences belong to the root entry only")
            proof = self.proof
            segments = proof.segments
            if not self.admitted_segments:
                raise _fixed("a file entry names its admitted proven segments")
            if self.admitted_segments != tuple(sorted(set(self.admitted_segments))):
                raise _fixed("admitted segment indices must be distinct and increasing")
            if self.admitted_segments[0] < 0 or self.admitted_segments[-1] >= len(segments):
                raise _fixed("admitted segment indices must index the proof segments")
            if len(self.admitted_segments) != 1 and self.admitted_segments != tuple(
                range(len(segments))
            ):
                # The admitted region is exactly the whole bundle or ONE
                # indivisible proven group; a non-contiguous subset would
                # concatenate A+C around a background B into a new source
                # (forbidden splice law).
                raise _fixed("admitted region is the whole bundle or one proven group")
            admitted: list[str] = []
            region: list[str] = []
            # Walk the ordered segments once: collect the admitted
            # member occurrences and cut the admitted region out of the
            # self-contained aggregate source (the segments are
            # concatenated in order into source_text).
            offset = 0
            for position, segment in enumerate(segments):
                if position in self.admitted_segments:
                    for member_position in segment.member_positions:
                        member = proof.requested_members[member_position]
                        if member.normalized is None:
                            raise _fixed("admitted members must be resolved paths")
                        admitted.append(member.normalized)
                    region.append(proof.source_text[offset : offset + segment.char_length])
                offset += segment.char_length
            admitted_tuple = tuple(admitted)
            if admitted_tuple != self.key_record.member_occurrences:
                raise _fixed("admitted members must equal the key record member occurrences")
            if (
                _sha256_hex("".join(region).encode("utf-8"))
                != self.key_record.aggregate_source_digest
            ):
                raise _fixed("admitted region digest must equal the key record aggregate")
            if self.width != len(set(admitted_tuple)):
                raise _fixed("width must equal the distinct admitted member paths")
        return self

    def __repr__(self) -> str:
        source = "<protected source>" if self.source_text is not None else "<proof-carried source>"
        return (
            "BundleEntry("
            f"entry_class={self.entry_class!r}, "
            f"content_key={self.content_key!r}, "
            f"key_record={self.key_record!r}, "
            f"width={self.width!r}, "
            f"member_classes={self.member_classes!r}, "
            f"root_digest={self.root_digest!r}, "
            f"admitted_segments={self.admitted_segments!r}, "
            f"source={source}, "
            f"source_char_length={self.source_char_length!r}, "
            f"source_byte_length={self.source_byte_length!r}, "
            f"proof={self.proof!r}, "
            f"envelope_occurrences={self.envelope_occurrences!r})"
        )

    __str__ = __repr__


class RootEnvelopeOccurrence(_GraphFrozen):
    """One ORIGINAL Responses user-envelope root occurrence, retained.

    The bounded fully-typed root provenance for the required root
    entry: the ACTUAL originating batch request index (the position of
    the ``GraphRequest`` that carried the occurrence — the same
    location/spans in a DIFFERENT request is different provenance and
    must stay attributable), the 017 classified occurrence facts
    (kind, status, content and envelope spans, earned digest, byte
    length, closed reasons) and the structural carrier location (the
    JSON pointer of the text item).  The private workspace scope
    label is deliberately NOT a field: the scope is bound exactly
    once by the owning entry's key record and the snapshot namespace,
    and the operational repr never echoes private scope or ID values.
    The accepted 017 ``RootOccurrence`` record and all 017 public
    behavior are unchanged.
    """

    request_index: int = Field(ge=0)
    carrier_location: str = Field(min_length=1)
    kind: OccurrenceKind
    status: RootStatus
    content_span: CharSpan | None = None
    envelope_span: CharSpan | None = None
    digest: str | None = Field(default=None, pattern=_HEX64)
    byte_length: int | None = Field(default=None, ge=0)
    reasons: tuple[Limitation, ...] = ()

    def __repr__(self) -> str:
        return (
            "RootEnvelopeOccurrence("
            f"request_index={self.request_index!r}, "
            f"carrier_location={self.carrier_location!r}, "
            f"kind={self.kind!r}, "
            f"status={self.status!r}, "
            f"content_span={self.content_span!r}, "
            f"envelope_span={self.envelope_span!r}, "
            f"digest={self.digest!r}, "
            f"byte_length={self.byte_length!r}, "
            f"reasons={[r.value for r in self.reasons]!r})"
        )

    __str__ = __repr__


class GroupCertificate(_GraphFrozen):
    """One typed GROUP-OWNED dependency certificate.

    Earned only under the boundaryless all-eligible common-base law:
    EVERY possible supplier of the group's reference is independently
    eligible and every supplier shares the same canonical lexical
    directory.  The certificate binds the complete possible-supplier
    OCCURRENCE sequence in original occurrence order (repetitions
    preserved, so ``A,B,A`` and ``A,A,B`` stay distinct and traceable
    through the actual original proof via the bound group digest and
    carrier), the ACTUAL reference evidence (closed syntax + exact
    character span) inside the group's own source, the group source
    digest, the original carrier provenance, the scope/root binding
    and the resolved target with its AND-OR derivation depth (1 + the
    maximum supplier least-derivation).  It never fabricates a
    supplying file, an A->C file edge or a true shortest file-edge
    distance; the accepted 018-a ``GraphEdge`` semantics remain
    unchanged and the combined ordinary-relationship plus certificate
    count is bounded snapshot-wide.

    ``segment_index`` is the ORIGINAL segment index of the group
    inside its source proof (carrier provenance, part of the record's
    uniqueness identity so two distinct identical groups of one
    carrier stay distinct; it is NOT semantic content-key material).
    """

    admission_version: str = ADMISSION_CONTRACT_VERSION
    scoped_key: str
    root_digest: str = Field(pattern=_HEX64)
    source_digest: str = Field(pattern=_HEX64)
    request_index: int = Field(ge=0)
    carrier_location: str = Field(min_length=1)
    segment_index: int = Field(ge=0)
    supplier_occurrences: tuple[str, ...] = Field(min_length=1)
    syntax: CandidateSyntax
    evidence_span: CharSpan
    target_path: str
    derivation_depth: int = Field(ge=1)

    @field_validator("scoped_key")
    @classmethod
    def _v_scoped_key(cls, value: str, info: core_schema.FieldValidationInfo) -> str:
        return _check_hex64(value, "scoped_key")

    @field_validator("supplier_occurrences")
    @classmethod
    def _v_supplier_occurrences(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        for path in value:
            _check_rel_path(path)
        return value

    @field_validator("target_path")
    @classmethod
    def _v_target_path(cls, value: str) -> str:
        return _check_rel_path(value)

    def __repr__(self) -> str:
        return (
            "GroupCertificate("
            f"scoped_key={self.scoped_key!r}, "
            f"root_digest={self.root_digest!r}, "
            f"source_digest={self.source_digest!r}, "
            f"request_index={self.request_index!r}, "
            f"carrier_location={self.carrier_location!r}, "
            f"segment_index={self.segment_index!r}, "
            f"supplier_occurrences={self.supplier_occurrences!r}, "
            f"syntax={self.syntax.value!r}, "
            f"evidence_span={self.evidence_span!r}, "
            f"target_path={self.target_path!r}, "
            f"derivation_depth={self.derivation_depth!r})"
        )

    __str__ = __repr__


class PathAssociation(_GraphFrozen):
    """One reverse-index row: represented path -> ALL admitted keys.

    The row deduplicates the content keys AFTER the actual
    association attempts were charged (the attempts are counted
    snapshot-wide, duplicates included).  The root path row is the
    complete root reverse association; greedy background members and
    every overlapping bundle are mapped, never omitted.
    """

    scoped_key: str
    path: str
    content_keys: tuple[str, ...] = Field(min_length=1)
    is_root: bool = False

    @field_validator("scoped_key")
    @classmethod
    def _v_scoped_key(cls, value: str, info: core_schema.FieldValidationInfo) -> str:
        return _check_hex64(value, "scoped_key")

    @field_validator("path")
    @classmethod
    def _v_path(cls, value: str) -> str:
        return _check_rel_path(value)

    @field_validator("content_keys")
    @classmethod
    def _v_content_keys(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        for key in value:
            _check_hex64(key, "content_key")
        if len(set(value)) != len(value):
            raise _fixed("content keys must be distinct")
        return value

    @model_validator(mode="after")
    def _w_root_row(self) -> PathAssociation:
        if self.is_root != (self.path == ROOT_FILENAME):
            raise _fixed("only the root path row may be the root association")
        return self

    def __repr__(self) -> str:
        return (
            "PathAssociation("
            f"scoped_key={self.scoped_key!r}, "
            f"path={self.path!r}, "
            f"content_keys={self.content_keys!r}, "
            f"is_root={self.is_root!r})"
        )

    __str__ = __repr__


class SourceVersionObservation(_GraphFrozen):
    """Source-version observation for one path on one original carrier.

    Retained independently of cache admission: a path that failed
    admission (or is off-graph) stays observable.  The digest is
    ``None`` when not actually proven (never invented); the ACTUAL
    original carrier (request index + structural carrier location)
    identifies the evidence, so a per-path digest/count alone can
    never masquerade as its carrier.  It is evidence for later
    invalidation of admitted bundles; this slice constructs no
    chronology from it.
    """

    scoped_key: str
    path: str
    content_digest: str | None = Field(default=None, pattern=_HEX64)
    request_index: int = Field(ge=0)
    carrier_location: str = Field(min_length=1)
    occurrence_count: int = Field(ge=1)

    @field_validator("scoped_key")
    @classmethod
    def _v_scoped_key(cls, value: str, info: core_schema.FieldValidationInfo) -> str:
        return _check_hex64(value, "scoped_key")

    @field_validator("path")
    @classmethod
    def _v_path(cls, value: str) -> str:
        return _check_rel_path(value)

    def __repr__(self) -> str:
        return (
            "SourceVersionObservation("
            f"scoped_key={self.scoped_key!r}, "
            f"path={self.path!r}, "
            f"content_digest={self.content_digest!r}, "
            f"request_index={self.request_index!r}, "
            f"carrier_location={self.carrier_location!r}, "
            f"occurrence_count={self.occurrence_count!r})"
        )

    __str__ = __repr__


class OrdinaryRelationship(_GraphFrozen):
    """One retained ordinary file-reference relationship.

    A separately typed projection of the accepted raw-reference graph
    closure: the referring document (path + version digest) and its
    target, with the repeated candidate occurrences that supported it
    preserved as a count.  It carries NO fabricated file-edge depth;
    together with the group certificates it is bounded by the
    ACTUAL effective ``GraphBounds.max_edges``.
    """

    scoped_key: str
    referring_path: str
    referring_digest: str = Field(pattern=_HEX64)
    target_path: str
    occurrence_count: int = Field(ge=1)

    @field_validator("scoped_key")
    @classmethod
    def _v_scoped_key(cls, value: str, info: core_schema.FieldValidationInfo) -> str:
        return _check_hex64(value, "scoped_key")

    @field_validator("referring_path", "target_path")
    @classmethod
    def _v_paths(cls, value: str) -> str:
        return _check_rel_path(value)

    def __repr__(self) -> str:
        return (
            "OrdinaryRelationship("
            f"scoped_key={self.scoped_key!r}, "
            f"referring_path={self.referring_path!r}, "
            f"referring_digest={self.referring_digest!r}, "
            f"target_path={self.target_path!r}, "
            f"occurrence_count={self.occurrence_count!r})"
        )

    __str__ = __repr__


class EligibilityNode(_GraphFrozen):
    """One reachable raw-reference node with its content status.

    Eligibility (independent root-reachability in the accepted
    raw-reference graph) is separate from acquisition and admission:
    a ``DISCOVERED_CONTENT_MISSING`` node is eligible without any
    source (no digest is invented).  The accepted 018-a ``NodeStatus``
    vocabulary is reused verbatim; no file-edge distance is retained.
    """

    scoped_key: str
    path: str
    status: NodeStatus
    source_digest: str | None = Field(default=None, pattern=_HEX64)

    @field_validator("scoped_key")
    @classmethod
    def _v_scoped_key(cls, value: str, info: core_schema.FieldValidationInfo) -> str:
        return _check_hex64(value, "scoped_key")

    @field_validator("path")
    @classmethod
    def _v_path(cls, value: str) -> str:
        return _check_rel_path(value)

    @model_validator(mode="after")
    def _w_status(self) -> EligibilityNode:
        if self.status is NodeStatus.DISCOVERED_CONTENT_MISSING:
            if self.source_digest is not None:
                raise _fixed("a content-missing node carries no source digest")
        elif self.status is NodeStatus.ACQUIRED:
            if self.source_digest is None:
                raise _fixed("an acquired node carries its earned source digest")
        elif self.status is NodeStatus.ACQUIRED_EMPTY:
            if self.source_digest != EMPTY_SOURCE_SHA256:
                raise _fixed("an acquired-empty node keeps the empty-source digest")
        else:  # VERSION_CONFLICT: no version may be selected
            if self.source_digest is not None:
                raise _fixed("a conflicted node selects no version")
        return self

    def __repr__(self) -> str:
        return (
            "EligibilityNode("
            f"scoped_key={self.scoped_key!r}, "
            f"path={self.path!r}, "
            f"status={self.status.value!r}, "
            f"source_digest={self.source_digest!r})"
        )

    __str__ = __repr__


class OffgraphSourceNode(_GraphFrozen):
    """One acquired source that is NOT independently root-reachable.

    An unrelated singleton read (or any acquired node without a
    complete AND/OR derivation from the root) is off-graph
    provenance: it is retained as a typed source observation
    independently of admission, but it is NOT an eligibility node
    and its outgoing references never expand reach.  The accepted
    018-a ``NodeStatus`` vocabulary is reused verbatim; no
    file-edge distance is retained.
    """

    scoped_key: str
    path: str
    status: NodeStatus
    source_digest: str | None = Field(default=None, pattern=_HEX64)

    @field_validator("scoped_key")
    @classmethod
    def _v_scoped_key(cls, value: str, info: core_schema.FieldValidationInfo) -> str:
        return _check_hex64(value, "scoped_key")

    @field_validator("path")
    @classmethod
    def _v_path(cls, value: str) -> str:
        return _check_rel_path(value)

    @model_validator(mode="after")
    def _w_status(self) -> OffgraphSourceNode:
        if self.status is NodeStatus.DISCOVERED_CONTENT_MISSING:
            if self.source_digest is not None:
                raise _fixed("a content-missing offgraph node carries no source digest")
        elif self.status is NodeStatus.ACQUIRED:
            if self.source_digest is None:
                raise _fixed("an acquired offgraph node carries its earned source digest")
        elif self.status is NodeStatus.ACQUIRED_EMPTY:
            if self.source_digest != EMPTY_SOURCE_SHA256:
                raise _fixed("an acquired-empty offgraph node keeps the empty-source digest")
        else:  # VERSION_CONFLICT: no version may be selected
            if self.source_digest is not None:
                raise _fixed("a conflicted offgraph node selects no version")
        return self

    def __repr__(self) -> str:
        return (
            "OffgraphSourceNode("
            f"scoped_key={self.scoped_key!r}, "
            f"path={self.path!r}, "
            f"status={self.status.value!r}, "
            f"source_digest={self.source_digest!r})"
        )

    __str__ = __repr__


class UnresolvedOriginRecord(_GraphFrozen):
    """Boundaryless bundle reference with unresolved origin.

    Mixed-eligibility suppliers or suppliers in different canonical
    directories never identify a supplying member: the record retains
    the group digest, the complete possible-origin path set, the
    ACTUAL reference candidates exactly as measured by the accepted
    018-a bounded scan (the typed ``ReferenceCandidate`` records,
    reused verbatim — no re-scan, no invented edge, no assumed common
    base) and the original carrier provenance.

    ``segment_index`` is the ORIGINAL segment index of the group
    inside its source proof (carrier provenance, part of the record's
    uniqueness identity so two distinct identical groups of one
    carrier stay distinct; it is NOT semantic content-key material).
    """

    scoped_key: str
    source_digest: str = Field(pattern=_HEX64)
    possible_origins: tuple[str, ...] = Field(min_length=1)
    candidates: tuple[ReferenceCandidate, ...] = ()
    request_index: int = Field(ge=0)
    carrier_location: str = Field(min_length=1)
    segment_index: int = Field(ge=0)

    @field_validator("scoped_key")
    @classmethod
    def _v_scoped_key(cls, value: str, info: core_schema.FieldValidationInfo) -> str:
        return _check_hex64(value, "scoped_key")

    @field_validator("possible_origins")
    @classmethod
    def _v_possible_origins(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        for path in value:
            _check_rel_path(path)
        if value != tuple(sorted(set(value))):
            raise _fixed("possible origins must be distinct and canonically ordered")
        return value

    def __repr__(self) -> str:
        return (
            "UnresolvedOriginRecord("
            f"scoped_key={self.scoped_key!r}, "
            f"source_digest={self.source_digest!r}, "
            f"possible_origins={self.possible_origins!r}, "
            f"candidates={self.candidates!r}, "
            f"request_index={self.request_index!r}, "
            f"carrier_location={self.carrier_location!r}, "
            f"segment_index={self.segment_index!r})"
        )

    __str__ = __repr__


class BundleAdmissionSnapshot(_GraphFrozen):
    """The bounded public admission snapshot (one original batch).

    Immutably carries the explicit trusted namespace, the fixed
    outcome, the required root entry (COMPLETE only), the admitted
    file entries (self-contained proofs retained), the group
    certificates, the complete reverse member-path index, the
    source-version observations retained independently of admission,
    the closed-vocabulary diagnostics and the measured counters.
    Refusals retain NO partial admission (entries, certificates,
    index rows, observations and root binding are all absent on a
    non-COMPLETE outcome).  Every counter is bound by the ACTUAL
    namespace effective values; the total emitted diagnostic count is
    bounded before retention.  ``str``/``repr`` never expose source
    bytes or private identity/scope values (the embedded records are
    all repr-suppressed).
    """

    admission_version: str = ADMISSION_CONTRACT_VERSION
    namespace: BundleAdmissionNamespace
    outcome: AdmissionOutcome
    root_entry: BundleEntry | None = None
    entries: tuple[BundleEntry, ...] = ()
    certificates: tuple[GroupCertificate, ...] = ()
    path_associations: tuple[PathAssociation, ...] = ()
    version_observations: tuple[SourceVersionObservation, ...] = ()
    ordinary_relationships: tuple[OrdinaryRelationship, ...] = ()
    eligibility_nodes: tuple[EligibilityNode, ...] = ()
    #: Acquired sources WITHOUT an independent root derivation:
    #: retained off-graph provenance, never eligibility.
    offgraph_nodes: tuple[OffgraphSourceNode, ...] = ()
    #: EVERY original accepted 018-b bundle proof retained verbatim
    #: (exact carriers, spans, piece IDs and positions), independent
    #: of semantic entry interning.
    source_proofs: tuple[BundleProof, ...] = ()
    unresolved_origins: tuple[UnresolvedOriginRecord, ...] = ()
    conflicts: tuple[AdmissionLimitation, ...] = ()
    diagnostics: tuple[AdmissionLimitation, ...] = ()
    #: 017 observation/global limitations (the accepted 017
    #: ``Limitation`` vocabulary, propagated from the observed
    #: surfaces), counted in the total emitted diagnostic bound.
    observation_limitations: tuple[Limitation, ...] = ()
    request_count: int = Field(ge=0)
    entries_retained: int = Field(ge=0)
    member_occurrences_charged: int = Field(ge=0)
    reverse_association_attempts: int = Field(ge=0)
    work_units: int = Field(ge=0)
    extra_documents_inspected: int = Field(ge=0)
    extra_candidates_inspected: int = Field(ge=0)
    root_path: str | None = None
    root_digest: str | None = Field(default=None, pattern=_HEX64)

    @field_validator("root_path")
    @classmethod
    def _v_root_path(cls, value: str | None) -> str | None:
        if value is None:
            return value
        return _check_rel_path(value)

    @model_validator(mode="after")
    def _v_snapshot(self) -> BundleAdmissionSnapshot:
        ns = self.namespace
        if self.outcome is AdmissionOutcome.COMPLETE:
            if self.root_entry is None or self.root_digest is None:
                raise _fixed("a complete admission carries its required root entry")
            if self.root_path != ROOT_FILENAME:
                raise _fixed("the root binding is the normalized root path")
            if self.root_entry.root_digest != self.root_digest:
                raise _fixed("root entry digest must equal the snapshot root digest")
        else:
            if (
                self.root_entry is not None
                or self.entries
                or self.certificates
                or self.path_associations
                or self.version_observations
                or self.ordinary_relationships
                or self.eligibility_nodes
                or self.offgraph_nodes
                or self.source_proofs
                or self.unresolved_origins
                or self.root_path is not None
                or self.root_digest is not None
            ):
                raise _fixed("a refused snapshot retains no admission")
        if self.root_entry is not None and self.root_entry.entry_class is not EntryClass.ROOT_ENTRY:
            raise _fixed("the root entry must be a root entry")
        file_keys = [entry.content_key for entry in self.entries]
        for entry in self.entries:
            if entry.entry_class is not EntryClass.FILE_BUNDLE_ENTRY:
                raise _fixed("file entries carry file authority only")
        if len(set(file_keys)) != len(file_keys):
            raise _fixed("entries must be unique by content key")
        if self.root_entry is not None and self.root_entry.content_key in file_keys:
            raise _fixed("the root key is distinct from every file key")
        retained = (1 if self.root_entry is not None else 0) + len(self.entries)
        if self.entries_retained != retained:
            raise _fixed("entries_retained must equal the retained entry count")
        if retained > ns.bounds.max_entries:
            raise _fixed("retained entries exceed the actual admission bound")
        # Member OCCURRENCES are charged (repeated members count once
        # each), never deduplicated width: the root carries one
        # occurrence, each file entry carries its admitted occurrences.
        charged_min = (1 if self.root_entry is not None else 0) + sum(
            len(entry.key_record.member_occurrences) for entry in self.entries
        )
        if self.member_occurrences_charged < charged_min:
            raise _fixed("member occurrences charged must cover every represented member")
        if self.member_occurrences_charged > ns.bounds.max_member_occurrences:
            raise _fixed("charged member occurrences exceed the actual bound")
        for entry in tuple([self.root_entry] if self.root_entry is not None else ()) + tuple(
            self.entries
        ):
            kr = entry.key_record
            if (kr.principal, kr.session, kr.repository, kr.route) != (
                ns.principal,
                ns.session,
                ns.repository,
                ns.route,
            ):
                raise _fixed("entry key record must bind the actual namespace identity")
            if (
                kr.model_identity != ns.model_identity
                or kr.config_fingerprint != ns.config_fingerprint
                or kr.workspace != ns.workspace
                or kr.mode != ns.mode
            ):
                raise _fixed("entry key record must bind the actual scope configuration")
            if (
                kr.admission_version,
                kr.graph_version,
                kr.reference_version,
                kr.proof_version,
                kr.observation_version,
            ) != (
                ns.admission_version,
                ns.graph_version,
                ns.reference_version,
                ns.proof_version,
                ns.observation_version,
            ):
                raise _fixed("entry key record must bind the actual versions")
            if (
                kr.admission_bounds,
                kr.proof_bounds,
                kr.graph_bounds,
                kr.observation_bounds,
            ) != (
                ns.bounds,
                ns.proof_bounds,
                ns.graph_bounds,
                ns.observation_bounds,
            ):
                raise _fixed("entry key record must bind the actual effective bounds")
            if self.root_digest is not None and kr.root_digest != self.root_digest:
                raise _fixed("entry key record root must equal the snapshot root")
        assoc_paths = [assoc.path for assoc in self.path_associations]
        if len(set(assoc_paths)) != len(assoc_paths):
            raise _fixed("reverse index paths must be unique")
        represented = set()
        if self.root_entry is not None:
            represented.add(ROOT_FILENAME)
        for entry in self.entries:
            represented.update(entry.key_record.member_occurrences)
        if set(assoc_paths) != represented:
            raise _fixed("the reverse index maps every represented path exactly once")
        admitted = set(file_keys)
        if self.root_entry is not None:
            admitted.add(self.root_entry.content_key)
        for assoc in self.path_associations:
            for key in assoc.content_keys:
                if key not in admitted:
                    raise _fixed("reverse index rows reference only admitted keys")
        if self.reverse_association_attempts < len(self.path_associations):
            raise _fixed("association attempts must cover every represented path")
        if self.reverse_association_attempts > ns.bounds.max_reverse_associations:
            raise _fixed("association attempts exceed the actual bound")
        obs_ids = [
            (obs.path, obs.request_index, obs.carrier_location) for obs in self.version_observations
        ]
        if len(set(obs_ids)) != len(obs_ids):
            raise _fixed("version observations must be unique per path and carrier")
        if any(obs.path == ROOT_FILENAME for obs in self.version_observations):
            raise _fixed("the root path is bound by the root entry, not an observation")
        cert_ids = [
            (
                cert.source_digest,
                cert.supplier_occurrences,
                cert.request_index,
                cert.carrier_location,
                cert.segment_index,
                cert.syntax.value,
                cert.evidence_span.start,
                cert.evidence_span.end,
                cert.target_path,
            )
            for cert in self.certificates
        ]
        if len(set(cert_ids)) != len(cert_ids):
            raise _fixed("certificates must be unique per group reference")
        rel_ids = [(rel.referring_path, rel.target_path) for rel in self.ordinary_relationships]
        if len(set(rel_ids)) != len(rel_ids):
            raise _fixed("ordinary relationships must be unique per pair")
        if len(self.ordinary_relationships) + len(self.certificates) > ns.graph_bounds.max_edges:
            raise _fixed("relationships plus certificates exceed the combined bound")
        node_paths = [node.path for node in self.eligibility_nodes]
        if len(set(node_paths)) != len(node_paths):
            raise _fixed("eligibility nodes must be unique per path")
        offgraph_paths = [node.path for node in self.offgraph_nodes]
        if len(set(offgraph_paths)) != len(offgraph_paths):
            raise _fixed("offgraph nodes must be unique per path")
        if set(offgraph_paths) & set(node_paths):
            raise _fixed("a node is either root-reachable or offgraph, never both")
        proof_ids = [
            (proof.request_index, proof.call_id, proof.result_location)
            for proof in self.source_proofs
        ]
        if len(set(proof_ids)) != len(proof_ids):
            raise _fixed("retained source proofs must be unique per occurrence")
        if len(self.source_proofs) > ns.proof_bounds.max_bundles:
            raise _fixed("retained source proofs exceed the actual proof bound")
        retained_proofs = set(proof_ids)
        for entry in self.entries:
            if entry.proof is not None:
                entry_proof_id = (
                    entry.proof.request_index,
                    entry.proof.call_id,
                    entry.proof.result_location,
                )
                if entry_proof_id not in retained_proofs:
                    raise _fixed("an entry proof must be a retained original proof")
        if self.root_digest is not None:
            for proof in self.source_proofs:
                if proof.root_digest != self.root_digest:
                    raise _fixed("a retained source proof must bind the snapshot root")
        origin_ids = [
            (
                origin.source_digest,
                origin.possible_origins,
                tuple(
                    (
                        candidate.syntax.value,
                        candidate.target_char_span.start,
                        candidate.target_char_span.end,
                        candidate.resolved_path,
                    )
                    for candidate in origin.candidates
                ),
                origin.request_index,
                origin.carrier_location,
                origin.segment_index,
            )
            for origin in self.unresolved_origins
        ]
        if len(set(origin_ids)) != len(origin_ids):
            raise _fixed("unresolved origin records must be unique per reference")
        if self.work_units > ns.graph_bounds.max_work_units:
            raise _fixed("work units exceed the actual shared graph bound")
        total_diagnostics = (
            len(self.conflicts) + len(self.diagnostics) + len(self.observation_limitations)
        )
        if total_diagnostics > ns.bounds.max_diagnostics:
            raise _fixed("emitted diagnostics exceed the actual bound")
        return self

    def __repr__(self) -> str:
        return (
            "BundleAdmissionSnapshot("
            f"namespace={self.namespace!r}, "
            f"outcome={self.outcome!r}, "
            f"root_entry={self.root_entry!r}, "
            f"entries={self.entries!r}, "
            f"certificates={self.certificates!r}, "
            f"path_associations={self.path_associations!r}, "
            f"version_observations={self.version_observations!r}, "
            f"ordinary_relationships={self.ordinary_relationships!r}, "
            f"eligibility_nodes={self.eligibility_nodes!r}, "
            f"offgraph_nodes={self.offgraph_nodes!r}, "
            f"source_proofs={self.source_proofs!r}, "
            f"unresolved_origins={self.unresolved_origins!r}, "
            f"conflicts={[v.value for v in self.conflicts]!r}, "
            f"diagnostics={[v.value for v in self.diagnostics]!r}, "
            f"observation_limitations={[v.value for v in self.observation_limitations]!r}, "
            f"request_count={self.request_count!r}, "
            f"entries_retained={self.entries_retained!r}, "
            f"member_occurrences_charged={self.member_occurrences_charged!r}, "
            f"reverse_association_attempts={self.reverse_association_attempts!r}, "
            f"work_units={self.work_units!r}, "
            f"extra_documents_inspected={self.extra_documents_inspected!r}, "
            f"extra_candidates_inspected={self.extra_candidates_inspected!r}, "
            f"root_path={self.root_path!r}, "
            f"root_digest={self.root_digest!r})"
        )

    __str__ = __repr__

"""Inert current bundle admission records (objective 018-g).

Versioned identities:

``CURRENT_ADMISSION_CONTRACT_VERSION = "cache-current-admission/v1"``;
``CURRENT_ADMISSION_POLICY_VERSION = "current-admission-policy/v1"``.

One inert pure derivation over ACTUAL retained 018-d causal history and
its ACTUAL namespace derives the accepted 018-f current graph AND the
current admission entries with the canonical 018-c semantic keys, the
exact retained source/provenance and the complete reverse member
index.  The records here are inert derivation outputs: they are not
runtime session/cache ownership, they create no compiler object, and
they never activate the legacy profile.  Operational reprs suppress
private source/ID values (fixed enums, counts, placeholders only).
"""

from __future__ import annotations

import hashlib
import json
from enum import StrEnum

from pydantic import Field, InstanceOf, field_validator, model_validator

from .bundle_admission import _key_canonical
from .bundle_admission_models import (
    BundleAdmissionBounds,
    BundleAdmissionNamespace,
    BundleKeyRecord,
    EntryClass,
    MemberClass,
    _canonical_namespace_fields,
)
from .bundle_proof_models import (
    ROOT_FILENAME,
    BundleProof,
    BundleProofBounds,
)
from .causal_history_models import (
    MAX_REVISION,
    CausalHistoryState,
)
from .current_graph_models import (
    CURRENT_GRAPH_CONTRACT_VERSION,
    CURRENT_GRAPH_POLICY_VERSION,
    PRIVATE_PATH_PLACEHOLDER,
    CurrentGraph,
    CurrentGraphBounds,
)
from .currentness_models import (
    CURRENTNESS_CONTRACT_VERSION,
    CURRENTNESS_POLICY_VERSION,
    OPAQUE_GROUP_RECIPE_VERSION,
    CurrentnessBounds,
)
from .graph_models import (
    GraphBounds,
    _check_rel_path,
    _fixed,
    _GraphFrozen,
)
from .observation_models import (
    PRIVATE_ID_PLACEHOLDER,
    CharSpan,
    ObservationBounds,
)

CURRENT_ADMISSION_CONTRACT_VERSION = "cache-current-admission/v1"
CURRENT_ADMISSION_POLICY_VERSION = "current-admission-policy/v1"

_HEX64 = r"^[0-9a-f]{64}$"
_HEX_DIGITS = frozenset("0123456789abcdef")


def _check_hex64(value: str, field: str) -> str:
    if len(value) != 64 or not set(value) <= _HEX_DIGITS:
        raise _fixed(f"{field} must be a 64-hex digest")
    return value


def _check_text(value: str, field: str, max_len: int) -> str:
    if not 1 <= len(value) <= max_len:
        raise _fixed(f"{field} must be 1..{max_len} characters")
    if any(ord(c) < 0x20 or ord(c) == 0x7F for c in value):
        raise _fixed(f"{field} must not contain control characters")
    return value


def _sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class CurrentAdmissionBounds(_GraphFrozen):
    """New finite per-DERIVATION current-admission bounds
    (objective 018-g).

    The order fixes the defaults AND the hard ceilings exactly:
    stricter positive values are permitted and ANY wider direct
    construction is refused.  These are DERIVED units over one pure
    derivation (work, newly owned entry-source UTF-8 bytes, newly
    emitted admission diagnostics), never token budgets, cache
    storage or total process RSS.  The accepted 017/018-a/b/c/d/e/f
    bound sets retain their exact scope/units and are not
    reinterpreted or globally minimized.
    """

    #: ONE OUTER work ledger over the ENTIRE operation: actual
    #: history validation, 018-e currentness, 018-f graph, admission
    #: planning, source/key construction, interning, witness/origin/
    #: index and output work, all charged BEFORE the crossing
    #: operation.  The ACTUAL supplied 018-f
    #: ``CurrentGraphBounds.max_total_work_units`` ceiling is enforced
    #: independently on the SAME shared outer (a private chained
    #: ledger): stricter F subtree work refuses even when the G total
    #: still has headroom, and no per-group/pass reset occurs.
    max_total_work_units: int = Field(default=1048576, ge=1, le=1048576)
    #: CUMULATIVE newly owned entry-source UTF-8 bytes across the
    #: DISTINCT interned semantic entries (root included), counted
    #: once per distinct content key.  The per-entry cap is the
    #: ACTUAL inherited ``GraphBounds.max_single_source_bytes``; this
    #: bound is the NEW cumulative domain.
    max_total_entry_source_bytes: int = Field(default=16777216, ge=1, le=16777216)
    #: TOTAL newly emitted ADMISSION diagnostics (fixed closed
    #: reasons for unadmitted current proofs and stage-level
    #: admission refusals), charged before each actual emission
    #: attempt.  Enforced in the SAME admission domain jointly with
    #: the ACTUAL inherited ``BundleAdmissionBounds.max_diagnostics``
    #: on the retained ``admission_reasons`` tuple.  018-f graph
    #: diagnostics stay F output by reference and are not re-emitted
    #: here; 018-f reason emission keeps the ACTUAL supplied
    #: current-graph diagnostic ceiling.
    max_diagnostics: int = Field(default=64, ge=1, le=64)


class CurrentAdmissionOutcome(StrEnum):
    """Closed derivation outcomes.

    ``ok`` carries the derived current admission (graph + entries +
    reverse index); every ``refused_*`` carries the EXACT input state
    and NO partial entries/index/graph.  A derivation never advances
    any revision.
    """

    OK = "ok"
    REFUSED_FOREIGN_SCOPE = "refused_foreign_scope"
    REFUSED_VERSION_CONFLICT = "refused_version_conflict"
    REFUSED_STATE_MALFORMED = "refused_state_malformed"
    REFUSED_NO_ROOT = "refused_no_root"
    REFUSED_OVER_BOUND = "refused_over_bound"


class CurrentAdmissionLimitation(StrEnum):
    """CLOSED fixed diagnostic vocabulary for current-admission
    refusals.

    (a) The 018-f current-graph names (which already carry the exact
    propagated 018-e/018-d stage names) are preserved EXACTLY when a
    refusal originates upstream of the admission phase, including the
    shared-outer ``total_work_units_over_bound`` name used by BOTH the
    G total domain and the independently enforced F subtree ceiling;
    (b) the admission-phase names below are G-own and never relabel
    an upstream domain.  Free-form strings and arbitrary text are
    rejected by validation and never echoed.
    """

    # --- Propagated 018-f names (exact values, upstream domain) ---
    FOREIGN_SCOPE = "foreign_scope"
    VERSION_UNSUPPORTED = "version_unsupported"
    STATE_MALFORMED = "state_malformed"
    ROOT_MISSING = "root_missing"
    ROOT_MALFORMED = "root_malformed"
    TOTAL_WORK_UNITS_OVER_BOUND = "total_work_units_over_bound"
    DIAGNOSTICS_FULL = "diagnostics_full"
    GRAPH_NODES_OVER_BOUND = "graph_nodes_over_bound"
    GRAPH_EDGES_OVER_BOUND = "graph_edges_over_bound"
    GRAPH_CANDIDATES_OVER_BOUND = "graph_candidates_over_bound"
    GRAPH_DOCUMENTS_OVER_BOUND = "graph_documents_over_bound"
    GRAPH_SOURCE_BYTES_OVER_BOUND = "graph_source_bytes_over_bound"
    GRAPH_DEPTH_OVER_BOUND = "graph_depth_over_bound"
    GRAPH_WORK_UNITS_OVER_BOUND = "graph_work_units_over_bound"
    GRAPH_DIAGNOSTICS_OVER_BOUND = "graph_diagnostics_over_bound"
    PATHS_OVER_BOUND = "paths_over_bound"
    GROUPS_OVER_BOUND = "groups_over_bound"
    WITNESS_MEMBERSHIPS_OVER_BOUND = "witness_memberships_over_bound"
    RELATION_PAIRS_OVER_BOUND = "relation_pairs_over_bound"
    CURRENTNESS_WORK_UNITS_OVER_BOUND = "currentness_work_units_over_bound"
    CURRENTNESS_DIAGNOSTICS_OVER_BOUND = "currentness_diagnostics_over_bound"
    HISTORY_WORK_UNITS_OVER_BOUND = "history_work_units_over_bound"
    # --- G-own admission-phase domains ---
    #: ADMISSION planning/output stage ledger (the ACTUAL inherited
    #: ``GraphBounds.max_work_units`` domain, distinct from F graph
    #: work).
    ADMISSION_WORK_UNITS_EXHAUSTED = "admission_work_units_exhausted"
    #: ONE distinct interned entry whose newly owned source UTF-8
    #: bytes exceed the ACTUAL inherited
    #: ``GraphBounds.max_single_source_bytes``.
    ENTRY_SOURCE_BYTES_OVER_BOUND = "entry_source_bytes_over_bound"
    #: CUMULATIVE newly owned entry-source bytes across the distinct
    #: interned entries exceed the NEW
    #: ``max_total_entry_source_bytes`` domain.
    TOTAL_ENTRY_SOURCE_BYTES_OVER_BOUND = "total_entry_source_bytes_over_bound"
    #: ADMISSION emitted diagnostics fill the NEW ``max_diagnostics``
    #: admission domain.
    ADMISSION_DIAGNOSTICS_FULL = "admission_diagnostics_full"
    # The ACTUAL inherited admission caps (their admission-output
    # domains, exact 018-c names).
    ENTRIES_OVER_BOUND = "entries_over_bound"
    MEMBER_OCCURRENSES_OVER_BOUND = "member_occurrences_over_bound"
    REVERSE_ASSOCIATIONS_OVER_BOUND = "reverse_associations_over_bound"
    #: Typed non-acquisition: a current proof the mode/eligibility
    #: law does not admit (no entry, no partial retention).
    CANDIDATE_UNPROVEN = "candidate_unproven"


class RetainedRootProvenance(_GraphFrozen):
    """The typed RETAINED root provenance for the current root entry.

    Mirrors the ACTUAL ``RootAnchor`` fields exactly: the narrow
    original extraction coordinates (first evidencing request index,
    decoded-carrier location, content and envelope character spans)
    and the measured root facts.  The anchor carries NO original
    ``RootOccurrence`` kind/status/reasons, and NONE are invented
    here; a ``RootEnvelopeOccurrence`` or original transport envelope
    is never fabricated.  The exact EMPTY root is legitimate (root
    authority is the evidenced envelope, not nonempty text): an
    empty content span and zero byte length are preserved unchanged.
    The private workspace scope is bound by the owning record's scope
    key, not echoed.
    """

    first_request_index: int = Field(ge=0)
    location: str = Field(min_length=1)
    content_span: CharSpan
    envelope_span: CharSpan | None = None
    source_byte_length: int = Field(ge=0)
    root_digest: str = Field(pattern=_HEX64)
    workspace: str

    @field_validator("location", "workspace")
    @classmethod
    def _v_text(cls, value: str, info: object) -> str:
        return _check_text(value, getattr(info, "field_name", "field") or "field", 1024)

    @field_validator("root_digest")
    @classmethod
    def _v_digest(cls, value: str, info: object) -> str:
        return _check_hex64(value, getattr(info, "field_name", "digest") or "digest")

    @model_validator(mode="after")
    def _v_consistency(self) -> RetainedRootProvenance:
        if self.content_span.length > self.source_byte_length and (
            self.source_byte_length != 0 or self.content_span.length != 0
        ):
            # Character span and byte length come from the SAME
            # measured anchor; a nonempty span can never fit in zero
            # bytes (and the exact-empty pair stays legal).
            raise _fixed("the retained root span and byte length must agree")
        return self

    def __repr__(self) -> str:  # noqa: D105 - privacy law
        return (
            "RetainedRootProvenance("
            f"first_request_index={self.first_request_index}, "
            f"location={self.location!r}, "
            f"content_span={self.content_span!r}, "
            f"envelope_span={self.envelope_span!r}, "
            f"source_byte_length={self.source_byte_length}, "
            f"root_digest={self.root_digest!r}, "
            f"workspace={PRIVATE_ID_PLACEHOLDER})"
        )

    __str__ = __repr__


class CurrentAdmissionWitness(_GraphFrozen):
    """One ORIGINAL proof/group coordinate of an admitted region.

    Provenance only: the retained verbatim occurrence the region was
    admitted from (occurrence identity plus the original request /
    call / result structural positions and the occurrence-local
    segment indices in THAT proof).  Each witness keeps ITS OWN
    original coordinates: an interned entry may combine equivalent
    regions from different proofs whose segment numbering differs,
    and no coordinate is reindexed to match a representative proof.
    Never a clock; equal distinct witnesses are all retained, never
    collapsed to a lexical/arrival winner.
    """

    occurrence_id: str = Field(pattern=_HEX64)
    request_index: int = Field(ge=0)
    call_position: int = Field(ge=0)
    result_position: int = Field(ge=0)
    segment_indices: tuple[int, ...] = Field(min_length=1)

    @field_validator("segment_indices")
    @classmethod
    def _v_segments(cls, value: tuple[int, ...], info: object) -> tuple[int, ...]:
        for index in value:
            if index < 0:
                raise _fixed("segment indices are occurrence-local and nonnegative")
        # Linear strictly-increasing adjacency check: equivalent to
        # sorted-and-distinct without a hidden built-in sort.
        for position in range(1, len(value)):
            if value[position] <= value[position - 1]:
                raise _fixed("segment indices must be distinct and increasing")
        return value

    def __repr__(self) -> str:  # noqa: D105 - privacy law
        return (
            "CurrentAdmissionWitness("
            f"occurrence_id={self.occurrence_id!r}, "
            f"request_index={self.request_index}, "
            f"call_position={self.call_position}, "
            f"result_position={self.result_position}, "
            f"segment_indices={self.segment_indices!r})"
        )

    __str__ = __repr__


def _entry_admission_namespace(
    key_record: BundleKeyRecord,
) -> BundleAdmissionNamespace:
    """Reconstruct the ACTUAL 018-c admission namespace bound by a
    key record (the record carries every field the canonical recipe
    consumes).  The namespace model re-derives both 64-hex scope keys
    from the actual fields, so a forged/inconsistent record cannot
    silently pass: construction here proves coherence, never source
    authority.
    """
    canonical = _canonical_namespace_fields(
        key_record.principal,
        key_record.session,
        key_record.repository,
        key_record.route,
        key_record.model_identity,
        key_record.config_fingerprint,
        key_record.admission_version,
        key_record.graph_version,
        key_record.reference_version,
        key_record.proof_version,
        key_record.observation_version,
        key_record.mode.value,
        key_record.admission_bounds,
        key_record.proof_bounds,
        key_record.graph_bounds,
        key_record.observation_bounds,
    )
    namespace_key = _sha256_hex(canonical)
    scoped_key = _sha256_hex((namespace_key + "\0" + key_record.workspace).encode("utf-8"))
    return BundleAdmissionNamespace(
        principal=key_record.principal,
        session=key_record.session,
        repository=key_record.repository,
        route=key_record.route,
        model_identity=key_record.model_identity,
        config_fingerprint=key_record.config_fingerprint,
        workspace=key_record.workspace,
        mode=key_record.mode,
        admission_version=key_record.admission_version,
        observation_version=key_record.observation_version,
        graph_version=key_record.graph_version,
        reference_version=key_record.reference_version,
        proof_version=key_record.proof_version,
        bounds=key_record.admission_bounds,
        proof_bounds=key_record.proof_bounds,
        graph_bounds=key_record.graph_bounds,
        observation_bounds=key_record.observation_bounds,
        namespace_key=namespace_key,
        scoped_key=scoped_key,
    )


def _canonical_entry_key(key_record: BundleKeyRecord) -> str:
    """Re-derive the canonical 018-c content key from a key record's
    ACTUAL fields using the accepted recipe (no second divergent
    canonical construction)."""
    namespace = _entry_admission_namespace(key_record)
    canonical = _key_canonical(
        namespace,
        key_record.root_digest,
        key_record.authority_class,
        key_record.member_occurrences,
        key_record.member_classes,
        key_record.aggregate_source_digest,
        key_record.ownership_groups,
    )
    return _sha256_hex(canonical)


class CurrentAdmissionEntry(_GraphFrozen):
    """One retained CURRENT admission entry.

    The 018-c canonical semantic key bytes and ``BundleKeyRecord``
    are REUSED for identical semantic inputs (same recipe, same
    fields); ``content_key`` must equal the key record's own
    ``content_key`` AND the re-derived canonical bytes, so merely
    well-shaped hex is never a binding.  A root entry carries the
    exact retained root source bytes (repr-suppressed; the
    invariants bind length and digest; the exact EMPTY root is
    legal) plus the typed ``RetainedRootProvenance`` and NO read
    witnesses (the anchor is evidenced, never a fabricated read
    occurrence).  A file entry keeps the accepted 018-b
    ``BundleProof`` by bounded immutable reference (the original
    proof is never reindexed or refabricated) with the admitted
    segment indices separate from entry-local canonical numbering;
    its ``witnesses`` retain ALL relevant maximal current
    proof/group coordinates, each with ITS OWN original occurrence /
    segment coordinates.
    """

    entry_class: EntryClass
    content_key: str = Field(pattern=_HEX64)
    #: Typed retained reference: the ALREADY-validated key record is
    #: class-checked, never revalidated (no implicit nested validator
    #: walk); wrong-class or dict input is refused.  Construction is
    #: never authentication: the public G history/namespace/source
    #: gates remain the authority.
    key_record: InstanceOf[BundleKeyRecord]
    width: int = Field(ge=1)
    member_classes: tuple[MemberClass, ...] = Field(min_length=1)
    root_digest: str = Field(pattern=_HEX64)
    #: Exact retained ROOT source bytes (root entries only; the
    #: exact empty root is legal).
    root_text: str | None = None
    root_source_byte_length: int | None = Field(default=None, ge=0)
    #: The typed retained-root provenance (root entries only).
    root_provenance: InstanceOf[RetainedRootProvenance] | None = None
    #: The retained verbatim original proof (file entries only),
    #: class-checked by typed reference: construction never reruns
    #: the old proof's whole-source validator; wrong-class or dict
    #: input is refused (construction is not authentication).
    proof: InstanceOf[BundleProof] | None = None
    #: Ordered indices into the retained proof's segments naming the
    #: ADMITTED region (file entries only): exactly the whole bundle
    #: or ONE indivisible proven group (the no-splice law).  Entry-
    #: local canonical numbering: witnesses keep their own original
    #: segment coordinates.
    admitted_segments: tuple[int, ...] = ()
    witnesses: tuple[InstanceOf[CurrentAdmissionWitness], ...] = ()

    @field_validator("content_key", "root_digest")
    @classmethod
    def _v_hex(cls, value: str, info: object) -> str:
        return _check_hex64(value, getattr(info, "field_name", "key") or "key")

    @field_validator("witnesses")
    @classmethod
    def _v_witnesses(
        cls, value: tuple[CurrentAdmissionWitness, ...], info: object
    ) -> tuple[CurrentAdmissionWitness, ...]:
        previous: tuple[str, int, int, int, tuple[int, ...]] | None = None
        # Linear strictly-increasing coordinate walk: equivalent to
        # sorted-and-deduplicated without a hidden built-in sort.
        for w in value:
            coord = (
                w.occurrence_id,
                w.request_index,
                w.call_position,
                w.result_position,
                w.segment_indices,
            )
            if previous is not None and coord <= previous:
                raise _fixed("witnesses must be sorted and deduplicated")
            previous = coord
        return tuple(value)

    @model_validator(mode="after")
    def _v_entry(self) -> CurrentAdmissionEntry:
        if self.key_record.authority_class != self.entry_class:
            raise _fixed("key record authority class must equal the entry class")
        if self.key_record.root_digest != self.root_digest:
            raise _fixed("entry root binding must equal the key record root binding")
        if len(self.member_classes) != len(self.key_record.member_occurrences):
            raise _fixed("member_classes must align with the member occurrences")
        if tuple(self.member_classes) != tuple(self.key_record.member_classes):
            raise _fixed("entry authority vector must equal the key record vector")
        if self.content_key != self.key_record.content_key:
            raise _fixed("content key must equal the key record content key")
        if _canonical_entry_key(self.key_record) != self.content_key:
            raise _fixed("content key must bind the actual canonical 018-c recipe")
        if self.entry_class is EntryClass.ROOT_ENTRY:
            if self.admitted_segments:
                raise _fixed("the root entry admits the root, not proof segments")
            if self.root_text is None or self.root_provenance is None:
                raise _fixed("a current root entry carries its retained root bytes and provenance")
            if self.proof is not None:
                raise _fixed("a root entry never embeds a file-tool proof")
            if self.witnesses:
                raise _fixed("the root entry is evidenced, never a fabricated read witness")
            text = self.root_text
            if self.root_source_byte_length != len(text.encode("utf-8")):
                raise _fixed("root source_byte_length must equal the retained bytes")
            if _sha256_hex(text.encode("utf-8")) != self.root_digest:
                raise _fixed("root digest must equal the retained root bytes")
            if self.key_record.member_occurrences != (ROOT_FILENAME,):
                raise _fixed("a root entry is one occurrence at the normalized root")
            if self.key_record.aggregate_source_digest != self.root_digest:
                raise _fixed("root aggregate digest must equal the root digest")
            if self.width != 1 or self.member_classes != (MemberClass.ELIGIBLE,):
                raise _fixed("the root is one always-eligible root-occurrence member")
            if self.root_provenance.root_digest != self.root_digest:
                raise _fixed("the retained root provenance binds the root digest")
            if self.root_provenance.source_byte_length != self.root_source_byte_length:
                raise _fixed("the retained root provenance binds the root bytes")
            return self
        if self.root_text is not None or self.root_source_byte_length is not None:
            raise _fixed("retained root bytes belong to the root entry only")
        if self.root_provenance is not None:
            raise _fixed("retained root provenance belongs to the root entry only")
        if self.proof is None:
            raise _fixed("a file entry keeps its retained original proof")
        if not self.witnesses:
            raise _fixed("a file entry retains its original proof witnesses")
        proof = self.proof
        segments = proof.segments
        if not self.admitted_segments:
            raise _fixed("a file entry names its admitted segments")
        # Linear strictly-increasing adjacency check: equivalent to
        # sorted-and-distinct without a hidden built-in sort; the
        # maximum index is the last one seen.
        previous = -1
        for index in self.admitted_segments:
            if index < 0 or index <= previous:
                raise _fixed("admitted segment indices must be distinct and increasing")
            previous = index
        if previous >= len(segments):
            raise _fixed("admitted segment indices must index the proof segments")
        if len(self.admitted_segments) != 1 and self.admitted_segments != tuple(
            range(len(segments))
        ):
            raise _fixed("admitted region is the whole bundle or one proven group")
        # ONE built admitted-index set: p insertions, then O(1)
        # membership for every original segment visit, so a whole
        # N-segment entry costs LINEAR, not quadratic, in the proof.
        admitted_set = set(self.admitted_segments)
        admitted: list[str] = []
        region: list[str] = []
        offset = 0
        for position, segment in enumerate(segments):
            if position in admitted_set:
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
        if _sha256_hex("".join(region).encode("utf-8")) != self.key_record.aggregate_source_digest:
            raise _fixed("admitted region digest must equal the key record aggregate")
        if self.width != len(set(admitted_tuple)):
            raise _fixed("width must equal the distinct admitted member paths")
        return self

    def __repr__(self) -> str:  # noqa: D105 - privacy law
        if self.entry_class is EntryClass.ROOT_ENTRY:
            source = f"<protected root source {len(self.root_text or '')} chars>"
        else:
            source = "<proof-carried source>"
        return (
            "CurrentAdmissionEntry("
            f"entry_class={self.entry_class.value!r}, "
            f"content_key={self.content_key!r}, "
            f"key_record=<canonical record suppressed>, "
            f"width={self.width!r}, "
            f"member_classes={[m.value for m in self.member_classes]!r}, "
            f"root_digest={self.root_digest!r}, "
            f"admitted_segments={self.admitted_segments!r}, "
            f"source={source}, "
            f"root_provenance={'yes' if self.root_provenance is not None else 'no'}, "
            f"witnesses={len(self.witnesses)})"
        )

    __str__ = __repr__


def current_admission_scope_key(
    history_key: str,
    workspace: str,
    root_digest: str,
    contract_version: str,
    policy_version: str,
    admission_version: str,
    observation_version: str,
    graph_version: str,
    reference_version: str,
    proof_version: str,
    history_version: str,
    arguments_version: str,
    currentness_contract_version: str,
    currentness_policy_version: str,
    currentness_recipe_version: str,
    graph_contract_version: str,
    graph_policy_version: str,
    currentness_scope_key: str,
    graph_scope_key: str,
    admission_namespace_key: str,
    admission_scoped_key: str,
    bounds: CurrentAdmissionBounds,
    currentness_bounds: CurrentnessBounds,
    graph_bounds: CurrentGraphBounds,
    admission_bounds: BundleAdmissionBounds,
    proof_bounds: BundleProofBounds,
    inherited_graph_bounds: GraphBounds,
    observation_bounds: ObservationBounds,
) -> str:
    """The derived current admission's output scope identity.

    Binds the ACTUAL 018-d history scope, the workspace, the ACTUAL
    root digest, every ACTUAL inherited version (admission/
    observation/graph/reference/proof/history/arguments), the
    accepted 018-e and 018-f contract/policy/recipe versions, the
    NEW current-admission contract/policy versions, the validated
    018-e and 018-f scope keys, the ACTUAL 018-c admission namespace
    and scoped keys, and EVERY effective bound set (new
    current-admission, currentness, current-graph, admission, proof,
    graph and observation) -- so a caller tag alone cannot establish
    identity and a forged/stale key cannot hide different actual
    version, bound or scope fields.  The derivation revalidates the
    actual fields first and emits only the supported constants.
    """
    payload = [
        contract_version,
        policy_version,
        admission_version,
        observation_version,
        graph_version,
        reference_version,
        proof_version,
        history_version,
        arguments_version,
        currentness_contract_version,
        currentness_policy_version,
        currentness_recipe_version,
        graph_contract_version,
        graph_policy_version,
        history_key,
        workspace,
        root_digest,
        currentness_scope_key,
        graph_scope_key,
        admission_namespace_key,
        admission_scoped_key,
        json.dumps(bounds.model_dump(mode="json"), sort_keys=True, separators=(",", ":")),
        json.dumps(
            currentness_bounds.model_dump(mode="json"), sort_keys=True, separators=(",", ":")
        ),
        json.dumps(graph_bounds.model_dump(mode="json"), sort_keys=True, separators=(",", ":")),
        json.dumps(admission_bounds.model_dump(mode="json"), sort_keys=True, separators=(",", ":")),
        json.dumps(proof_bounds.model_dump(mode="json"), sort_keys=True, separators=(",", ":")),
        json.dumps(
            inherited_graph_bounds.model_dump(mode="json"), sort_keys=True, separators=(",", ":")
        ),
        json.dumps(
            observation_bounds.model_dump(mode="json"), sort_keys=True, separators=(",", ":")
        ),
    ]
    return _sha256_hex(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8"))


class CurrentAdmissionPathAssociation(_GraphFrozen):
    """One NEW current-admission reverse-index row (path -> keys).

    The G-owned operational row for the derived output: the same
    fields and row law as the accepted 018-c
    ``PathAssociation`` (whose model, repr and behavior stay
    unchanged and are never opportunistically rewritten), but the
    operational repr of this NEW row never echoes the private member
    path (fixed placeholder, key count and root flag only).  The
    actual path remains an inspectable field; content keys are
    digests.
    """

    scoped_key: str
    path: str
    content_keys: tuple[str, ...] = Field(min_length=1)
    is_root: bool = False

    @field_validator("scoped_key")
    @classmethod
    def _v_scoped_key(cls, value: str, info: object) -> str:
        return _check_hex64(value, "scoped_key")

    @field_validator("path")
    @classmethod
    def _v_path(cls, value: str, info: object) -> str:
        return _check_rel_path(value)

    @field_validator("content_keys")
    @classmethod
    def _v_content_keys(cls, value: tuple[str, ...], info: object) -> tuple[str, ...]:
        for key in value:
            _check_hex64(key, "content_key")
        if len(set(value)) != len(value):
            raise _fixed("content keys must be distinct")
        return value

    @model_validator(mode="after")
    def _v_root_row(self) -> CurrentAdmissionPathAssociation:
        if self.is_root != (self.path == ROOT_FILENAME):
            raise _fixed("only the root path row may be the root association")
        return self

    def __repr__(self) -> str:  # noqa: D105 - privacy law
        return (
            "CurrentAdmissionPathAssociation("
            f"scoped_key={self.scoped_key!r}, "
            f"path={PRIVATE_PATH_PLACEHOLDER!r}, "
            f"content_keys={len(self.content_keys)}, "
            f"is_root={self.is_root!r})"
        )

    __str__ = __repr__


class CurrentAdmission(_GraphFrozen):
    """One derived CURRENT admission for the EXACT input history
    scope/revision it describes.

    Pure derivation output: not a fresh revision or clock, never
    mutates the input, confers no compiler-semantic key on any
    unchanged source beyond the canonical 018-c identity, and keeps
    the graph derivation complete-versus-acquired-versus-admitted
    separation (the accepted 018-f ``CurrentGraph`` is carried by
    reference with its own scope/diagnostics).  ``root_entry`` is
    always present on an ``ok`` derivation (the anchor is the only
    root-text supplier and stays current, empty or not); ``entries``
    are the interned file-bundle entries; ``path_associations`` is
    the complete reverse member-path index (every represented member
    path maps to ALL currently admitted content keys, overlaps and
    greedy background included); ``admission_reasons`` is the ACTUAL
    bounded sorted/deduplicated admission-reason tuple emitted by
    this derivation (a normal derivation emits at most ONE unique
    fixed ``candidate_unproven``), with ``emitted_admission_reasons``
    bound to its length and BOTH the NEW ``bounds.max_diagnostics``
    and the ACTUAL inherited ``admission_bounds.max_diagnostics``
    enforced in the SAME admission domain (018-f graph diagnostics
    stay F output by reference, never re-emitted here).
    ``scope_key`` is RECOMPUTED from the actual fields on every
    construction: a stale or forged key is refused, never retained.
    """

    history_key: str
    revision: int = Field(ge=0, le=MAX_REVISION)
    workspace: str
    root_path: str = ROOT_FILENAME
    root_digest: str
    admission_version: str
    observation_version: str
    graph_version: str
    reference_version: str
    proof_version: str
    history_version: str
    arguments_version: str
    currentness_contract_version: str = CURRENTNESS_CONTRACT_VERSION
    currentness_policy_version: str = CURRENTNESS_POLICY_VERSION
    currentness_recipe_version: str = OPAQUE_GROUP_RECIPE_VERSION
    graph_contract_version: str = CURRENT_GRAPH_CONTRACT_VERSION
    graph_policy_version: str = CURRENT_GRAPH_POLICY_VERSION
    contract_version: str = CURRENT_ADMISSION_CONTRACT_VERSION
    policy_version: str = CURRENT_ADMISSION_POLICY_VERSION
    bounds: CurrentAdmissionBounds = Field(default_factory=CurrentAdmissionBounds)
    currentness_bounds: CurrentnessBounds = Field(default_factory=CurrentnessBounds)
    graph_bounds: CurrentGraphBounds = Field(default_factory=CurrentGraphBounds)
    admission_bounds: BundleAdmissionBounds = Field(default_factory=BundleAdmissionBounds)
    proof_bounds: BundleProofBounds = Field(default_factory=BundleProofBounds)
    inherited_graph_bounds: GraphBounds = Field(default_factory=GraphBounds)
    observation_bounds: ObservationBounds = Field(default_factory=ObservationBounds)
    currentness_scope_key: str
    graph_scope_key: str
    admission_namespace_key: str
    admission_scoped_key: str
    scope_key: str
    #: Typed retained references: the already-validated entries/rows/
    #: graph are class-checked, never revalidated (no nested entry
    #: region re-copy, graph re-walk or container re-validation);
    #: wrong-class or dict input is refused (construction is not
    #: authentication).
    root_entry: InstanceOf[CurrentAdmissionEntry]
    entries: tuple[InstanceOf[CurrentAdmissionEntry], ...] = ()
    path_associations: tuple[InstanceOf[CurrentAdmissionPathAssociation], ...] = ()
    graph: InstanceOf[CurrentGraph]
    work_units: int = Field(ge=0)
    entry_source_bytes: int = Field(ge=0)
    entries_retained: int = Field(ge=1)
    member_occurrences_charged: int = Field(ge=1)
    reverse_association_attempts: int = Field(ge=0)
    emitted_admission_reasons: int = Field(ge=0, le=64)
    #: The ACTUAL bounded sorted/deduplicated admission-reason tuple
    #: emitted by this derivation (the fixed closed
    #: ``candidate_unproven`` for unadmitted current candidates;
    #: empty when every candidate is admitted).  A normal derivation
    #: emits at most ONE unique reason.  018-f graph diagnostics stay
    #: a distinct F output carried by reference, never re-emitted.
    admission_reasons: tuple[CurrentAdmissionLimitation, ...] = ()

    @field_validator(
        "history_key",
        "root_digest",
        "currentness_scope_key",
        "graph_scope_key",
        "admission_namespace_key",
        "admission_scoped_key",
        "scope_key",
    )
    @classmethod
    def _v_hex(cls, value: str, info: object) -> str:
        return _check_hex64(value, getattr(info, "field_name", "key") or "key")

    @field_validator("workspace")
    @classmethod
    def _v_workspace(cls, value: str, info: object) -> str:
        return _check_text(value, "workspace", 1024)

    @field_validator(
        "admission_version",
        "observation_version",
        "graph_version",
        "reference_version",
        "proof_version",
        "history_version",
        "arguments_version",
        "currentness_contract_version",
        "currentness_policy_version",
        "currentness_recipe_version",
        "graph_contract_version",
        "graph_policy_version",
        "contract_version",
        "policy_version",
    )
    @classmethod
    def _v_version(cls, value: str, info: object) -> str:
        return _check_text(value, getattr(info, "field_name", "version") or "version", 128)

    @field_validator("root_path")
    @classmethod
    def _v_root_path(cls, value: str, info: object) -> str:
        return _check_rel_path(value)

    @field_validator("admission_reasons")
    @classmethod
    def _v_admission_reasons(
        cls, value: tuple[CurrentAdmissionLimitation, ...]
    ) -> tuple[CurrentAdmissionLimitation, ...]:
        if tuple(sorted(set(value), key=lambda r: r.value)) != value:
            raise _fixed("admission reasons must be sorted and deduplicated")
        return value

    @model_validator(mode="after")
    def _v_admission(self) -> CurrentAdmission:
        if self.root_entry.entry_class is not EntryClass.ROOT_ENTRY:
            raise _fixed("the root entry is the required ROOT_ENTRY")
        if self.root_entry.root_digest != self.root_digest:
            raise _fixed("the root entry binds the actual root digest")
        keys = [entry.content_key for entry in self.entries]
        # Strictly-increasing adjacency walk: equivalent to sorted-
        # and-distinct, O(n) without a hidden built-in sort.
        for position in range(1, len(keys)):
            if keys[position] <= keys[position - 1]:
                raise _fixed("entries must be sorted by distinct content key")
        if self.root_entry.content_key in keys:
            raise _fixed("the root entry is never repeated among file entries")
        if self.entries_retained != 1 + len(self.entries):
            raise _fixed("entries_retained counts the root entry plus file entries")
        if self.graph.history_key != self.history_key or self.graph.revision != self.revision:
            raise _fixed("the carried graph describes the exact input scope/revision")
        if self.graph.root_digest != self.root_digest:
            raise _fixed("the carried graph binds the actual root digest")
        if self.graph.scope_key != self.graph_scope_key:
            raise _fixed("the carried graph scope key must equal the bound key")
        if self.emitted_admission_reasons != len(self.admission_reasons):
            raise _fixed("emitted_admission_reasons must equal the retained reason count")
        if self.emitted_admission_reasons > self.bounds.max_diagnostics:
            raise _fixed("emitted admission reasons cannot exceed the admission cap")
        if len(self.admission_reasons) > self.admission_bounds.max_diagnostics:
            raise _fixed("emitted admission reasons cannot exceed the inherited admission cap")
        rows = {row.path: row for row in self.path_associations}
        root_row = rows.get(self.root_path)
        if root_row is None or self.root_entry.content_key not in root_row.content_keys:
            raise _fixed("the reverse index maps the root to its content key")
        for row in self.path_associations:
            if row.is_root != (row.path == self.root_path):
                raise _fixed("root association flags must match the root path")
        # One built key-set index: linear in the row key count, then
        # O(1) membership (a dense overlapping row is not searched
        # once per entry over the raw tuple).
        key_sets = {path: set(row.content_keys) for path, row in rows.items()}
        for entry in (self.root_entry, *self.entries):
            for path in entry.key_record.member_occurrences:
                key_set = key_sets.get(path)
                if key_set is None or entry.content_key not in key_set:
                    raise _fixed("the reverse index covers every represented member path")
        expected_scope = current_admission_scope_key(
            self.history_key,
            self.workspace,
            self.root_digest,
            self.contract_version,
            self.policy_version,
            self.admission_version,
            self.observation_version,
            self.graph_version,
            self.reference_version,
            self.proof_version,
            self.history_version,
            self.arguments_version,
            self.currentness_contract_version,
            self.currentness_policy_version,
            self.currentness_recipe_version,
            self.graph_contract_version,
            self.graph_policy_version,
            self.currentness_scope_key,
            self.graph_scope_key,
            self.admission_namespace_key,
            self.admission_scoped_key,
            self.bounds,
            self.currentness_bounds,
            self.graph_bounds,
            self.admission_bounds,
            self.proof_bounds,
            self.inherited_graph_bounds,
            self.observation_bounds,
        )
        if self.scope_key != expected_scope:
            raise _fixed("scope key must bind the actual versions and effective bounds")
        return self

    def __repr__(self) -> str:  # noqa: D105 - privacy law
        return (
            "CurrentAdmission("
            f"history_key={self.history_key!r}, "
            f"revision={self.revision!r}, "
            f"workspace={PRIVATE_ID_PLACEHOLDER}, "
            f"root_digest={self.root_digest!r}, "
            f"contract_version={self.contract_version!r}, "
            f"policy_version={self.policy_version!r}, "
            f"scope_key={self.scope_key!r}, "
            f"root_entry={'yes'}, "
            f"entries={len(self.entries)}, "
            f"path_associations={len(self.path_associations)}, "
            f"graph={'yes'}, "
            f"work_units={self.work_units}, "
            f"entry_source_bytes={self.entry_source_bytes}, "
            f"entries_retained={self.entries_retained}, "
            f"member_occurrences_charged={self.member_occurrences_charged}, "
            f"reverse_association_attempts={self.reverse_association_attempts}, "
            f"emitted_admission_reasons={self.emitted_admission_reasons}, "
            f"admission_reasons={list(self.admission_reasons)})"
        )

    __str__ = __repr__


class CurrentAdmissionResult(_GraphFrozen):
    """One bounded current-admission derivation result.

    ``state`` is ALWAYS the EXACT input state object (identity
    preserved on every outcome; the input is immutable and the
    derivation never mutates or re-orders it).  ``ok`` carries the
    derived current admission and no DERIVATION-level diagnostics
    (the emitted admission reasons are retained INSIDE the overlay's
    ``admission_reasons``, bound to ``emitted_admission_reasons``);
    every refusal carries no partial entries/index/graph and its
    closed derivation reasons.
    """

    outcome: CurrentAdmissionOutcome
    #: The EXACT input state, class-checked by typed reference (never
    #: revalidated, never copied).
    state: InstanceOf[CausalHistoryState]
    #: The derived admission, class-checked by typed reference (no
    #: nested re-validation of entries or graph).
    overlay: InstanceOf[CurrentAdmission] | None = None
    diagnostics: tuple[CurrentAdmissionLimitation, ...] = ()

    @field_validator("diagnostics")
    @classmethod
    def _v_diagnostics(
        cls, value: tuple[CurrentAdmissionLimitation, ...]
    ) -> tuple[CurrentAdmissionLimitation, ...]:
        if tuple(sorted(set(value), key=lambda r: r.value)) != value:
            raise _fixed("diagnostics must be sorted and deduplicated")
        return value

    @model_validator(mode="after")
    def _v_result(self) -> CurrentAdmissionResult:
        if self.outcome is CurrentAdmissionOutcome.OK:
            if self.overlay is None or self.diagnostics:
                raise _fixed("an ok result carries its overlay and no diagnostics")
            return self
        if self.overlay is not None or not self.diagnostics:
            raise _fixed("a refusal carries no partial overlay and its closed reasons")
        return self

    def __repr__(self) -> str:  # noqa: D105 - privacy law
        return (
            f"CurrentAdmissionResult(outcome={self.outcome.value!r}, "
            f"overlay={'yes' if self.overlay is not None else 'no'}, "
            f"diagnostics={list(self.diagnostics)})"
        )

    __str__ = __repr__

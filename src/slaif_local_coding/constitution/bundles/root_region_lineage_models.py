"""Versioned root-region authority producer records (objective 018-p; INERT).

``ROOT_REGION_LINEAGE_CONTRACT_VERSION = "cache-root-region-lineage/v1"``;
``ROOT_REGION_LINEAGE_POLICY_VERSION = "root-region-lineage-policy/v1"``.

This module binds the ACTUAL accepted 018-d causal-history scope
(the same actual identity/config/workspace/mode fields, both
admission 64-hex keys, the seven actual version identities, the
inherited bound sets, the lineage ID and the actual
``history_key`` / ``state_scoped_key`` -- all revalidated against
the real accepted D validators, exactly as the accepted 018-h root
lineage scope) plus the NEW root-region contract/policy versions
and the ACTUAL UNCHANGED ``RootLineageBounds`` into a
recompute-and-verify region lineage scope.

It defines the typed immutable root-region records: the
discriminated root-source provenance (bootstrap ENVELOPE anchor
identity versus retained complete singleton root READ versus the
NEW explicit root-REGION read), the retained root fact with
DERIVED issued/authority flags, the state that wraps the ACTUAL
018-d state by immutable reference, the bounded transition result
and the pure current-root selection result.

The provenance union REUSES the supported original envelope and
whole-singleton READ shapes (the accepted 018-h records, unchanged)
and adds ONE explicit ``read_region`` provenance: a proven single
effective-root member segment of a multi-member (mixed) complete
proof, retaining the actual original occurrence/call/endpoint, the
WHOLE original proof digest and byte length, the root segment
index and the unique member position, plus the ROOT MEMBER digest
and byte length.  The whole-proof binding and the root-body
binding are DISTINCT: the selected root content is only that
original member segment (a zero-length region is legal when
genuinely proven), and the proof aggregate may include other
files.  A region fact's root body binds the member digest/length,
never the proof aggregate.

These are explicit NEW-version records, not silently widened old H
schemas: the old v1 records, versions, schemas, recipe bytes and
cap domains are unchanged.  The new state revision stays in exact
1:1 with its wrapped actual D revision.

It is pure and inert: no pipeline activation, no adapter
runtime/compiler/recovery wiring, no RAM service, no disk, no
HTTP/SSE observer and no new metrics.  The state machine itself
lives in ``root_region_lineage.py``.

Object construction is NOT authentication: this is an internal
trusted boundary, never a public body/header authority path.
"""

from __future__ import annotations

from typing import Annotated, Literal

from pydantic import Field, InstanceOf, field_validator, model_validator

from .bundle_admission_models import AdmissionMode, BundleAdmissionBounds
from .bundle_proof_models import BundleProofBounds
from .causal_history_models import (
    MAX_REVISION,
    CausalHistoryNamespace,
    CausalHistoryState,
    CausalHistoryTransition,
    HistoryBounds,
    make_causal_history_namespace,
)
from .graph_models import GraphBounds, _check_hex64, _fixed, _GraphFrozen
from .observation_models import PRIVATE_ID_PLACEHOLDER, ObservationBounds
from .root_lineage_models import (
    _DIAGNOSTIC_CEILING,
    _HARD_ROOT_FACTS,
    _HARD_ROOT_SOURCE_BYTES,
    EnvelopeRootProvenance,
    ReadRootProvenance,
    RootLineageBounds,
    RootLineageLimitation,
    RootLineageOutcome,
    RootSelectionOutcome,
    _hb_hex64,
    _hb_str,
    _lineage_key,
    admission_bounds_shape_ok,
    graph_bounds_shape_ok,
    history_bounds_shape_ok,
    observation_bounds_shape_ok,
    proof_bounds_shape_ok,
    root_lineage_bounds_shape_ok,
)

ROOT_REGION_LINEAGE_CONTRACT_VERSION = "cache-root-region-lineage/v1"
ROOT_REGION_LINEAGE_POLICY_VERSION = "root-region-lineage-policy/v1"


# --- The NEW explicit root-region read provenance ------------------------


class RootRegionReadProvenance(_GraphFrozen):
    """Retained complete mixed-read ROOT-REGION provenance (NEW kind).

    Binds the ACTUAL completed original mixed read: the
    occurrence/call identity and the original endpoint; the WHOLE
    original proof digest and byte length (the proof aggregate
    binding, retained verbatim from the original proof -- never a
    re-hash and distinct from the root body); the root segment
    index into the proof's ordered segments and the unique member
    position of the single attributable effective-root member
    inside that segment; and the ROOT MEMBER digest and byte
    length (the actual root body).  A zero-length root region is
    legal when genuinely proven.
    """

    kind: Literal["read_region"] = "read_region"
    occurrence_id: str
    call_id: str
    endpoint: str
    whole_proof_digest: str
    whole_proof_byte_length: int = Field(ge=0)
    root_segment_index: int = Field(ge=0)
    root_member_position: int = Field(ge=0)
    root_member_digest: str
    root_member_byte_length: int = Field(ge=0)

    @field_validator("occurrence_id", "whole_proof_digest", "root_member_digest")
    @classmethod
    def _v_hex64(cls, value: str, info: object) -> str:
        return _check_hex64(value, getattr(info, "field_name", "digest") or "digest")

    @field_validator("call_id")
    @classmethod
    def _v_call_id(cls, value: str) -> str:
        if not 1 <= len(value) <= 256 or any(c.isspace() for c in value):
            raise _fixed("call_id must be 1..256 non-space characters")
        try:
            value.encode("utf-8")
        except UnicodeEncodeError:
            raise _fixed("call_id must be valid UTF-8") from None
        return value

    @field_validator("endpoint")
    @classmethod
    def _v_endpoint(cls, value: str) -> str:
        if value not in ("responses", "chat"):
            raise _fixed("endpoint must be an explicit validated endpoint")
        return value

    def __repr__(self) -> str:  # noqa: D105 - privacy law
        return (
            f"RootRegionReadProvenance(occurrence_id={self.occurrence_id!r}, "
            f"call_id={PRIVATE_ID_PLACEHOLDER}, endpoint={self.endpoint!r}, "
            f"whole_proof_digest={self.whole_proof_digest!r}, "
            f"whole_proof_byte_length={self.whole_proof_byte_length}, "
            f"root_segment_index={self.root_segment_index}, "
            f"root_member_position={self.root_member_position}, "
            f"root_member_digest={self.root_member_digest!r}, "
            f"root_member_byte_length={self.root_member_byte_length})"
        )

    __str__ = __repr__


RootRegionLineageProvenance = Annotated[
    EnvelopeRootProvenance | ReadRootProvenance | RootRegionReadProvenance,
    Field(discriminator="kind"),
]


def _region_provenance_key(provenance: object) -> tuple[str, str]:
    """The sorted-deduplicated retention identity of one region
    provenance (one fact per occurrence, kind-discriminated).

    The CONCRETE class is fenced against the kind tag BEFORE any
    dispatch: a forged instance (model_construct) with a mismatched
    tag is a fixed typed error, never a dereference of an absent
    field."""
    if isinstance(provenance, EnvelopeRootProvenance):
        if provenance.kind != "envelope":
            raise _fixed("the envelope provenance kind tag does not match its concrete class")
        return ("envelope", "")
    if isinstance(provenance, ReadRootProvenance):
        if provenance.kind != "read":
            raise _fixed("the read provenance kind tag does not match its concrete class")
        return ("read", provenance.occurrence_id)
    if isinstance(provenance, RootRegionReadProvenance):
        if provenance.kind != "read_region":
            raise _fixed("the region provenance kind tag does not match its concrete class")
        return ("read_region", provenance.occurrence_id)
    raise _fixed("the root region fact provenance must be one of the supported provenance records")


class RootRegionLineageFact(_GraphFrozen):
    """ONE retained root-source fact under the NEW region contract.

    ``source_digest``/``source_byte_length`` are the ROOT BODY --
    comparable across facts (equal incomparable witnesses are
    compatible; differing maximal sources conflict).  For an
    envelope fact the root body is the anchor source; for a read
    fact it is the original whole-read aggregate binding (the
    singleton complete root read, unchanged old law); for a
    read_region fact it is the ACTUAL ROOT MEMBER digest and byte
    length (the single proven segment of the mixed proof) -- the
    proof aggregate stays in the provenance and is never the root
    body.

    ``issued`` and ``authority`` are DERIVED flags recomputed on
    EVERY accepted D transition (the S1 law, unchanged): a read or
    region fact is issued when its matching INTERNAL issuance is
    retained and authoritative only when issued AND anchored AND
    the frozen parent evidence reaches the ORIGINAL bootstrap root
    fact.  The envelope fact is the anchor itself: never issued,
    always authoritative.  Flags are derived state, never
    caller-supplied authority.
    """

    source_digest: str
    source_byte_length: int = Field(ge=0, le=_HARD_ROOT_SOURCE_BYTES)
    provenance: RootRegionLineageProvenance
    issued: bool = False
    authority: bool = False

    @field_validator("source_digest")
    @classmethod
    def _v_source_digest(cls, value: str) -> str:
        return _check_hex64(value, "source_digest")

    @model_validator(mode="after")
    def _v_flags(self) -> RootRegionLineageFact:
        p = self.provenance
        if p.kind == "envelope":
            if self.issued or not self.authority:
                raise _fixed("the bootstrap envelope fact is never issued and always authoritative")
            if (
                self.source_digest != p.root_digest
                or self.source_byte_length != p.source_byte_length
            ):
                raise _fixed("the envelope fact source must equal the anchor provenance binding")
        elif p.kind == "read":
            if self.authority and not self.issued:
                raise _fixed("a read root fact is authoritative only when issued")
            # The singleton root body IS the original whole-read
            # binding (unchanged old law).
            if self.source_digest != p.read_digest or self.source_byte_length != p.read_byte_length:
                raise _fixed("a read fact source must equal the original whole-read binding")
        else:
            if self.authority and not self.issued:
                raise _fixed("a region root fact is authoritative only when issued")
            # The region root body IS the actual root member
            # binding; the proof aggregate is distinct and never
            # substituted.
            if (
                self.source_digest != p.root_member_digest
                or self.source_byte_length != p.root_member_byte_length
            ):
                raise _fixed(
                    "a region fact source must equal the root member binding, "
                    "never the proof aggregate"
                )
        return self

    def __repr__(self) -> str:  # noqa: D105 - privacy law
        p = self.provenance
        if p.kind == "envelope":
            prov = (
                f"provenance=envelope(root_digest={p.root_digest!r}, "
                f"workspace={PRIVATE_ID_PLACEHOLDER}, "
                f"source_byte_length={p.source_byte_length})"
            )
        elif p.kind == "read":
            prov = (
                f"provenance=read(occurrence_id={p.occurrence_id!r}, "
                f"call_id={PRIVATE_ID_PLACEHOLDER}, endpoint={p.endpoint!r}, "
                f"read_digest={p.read_digest!r}, "
                f"read_byte_length={p.read_byte_length})"
            )
        else:
            prov = (
                f"provenance=read_region(occurrence_id={p.occurrence_id!r}, "
                f"call_id={PRIVATE_ID_PLACEHOLDER}, endpoint={p.endpoint!r}, "
                f"whole_proof_digest={p.whole_proof_digest!r}, "
                f"whole_proof_byte_length={p.whole_proof_byte_length}, "
                f"root_segment_index={p.root_segment_index}, "
                f"root_member_position={p.root_member_position}, "
                f"root_member_digest={p.root_member_digest!r}, "
                f"root_member_byte_length={p.root_member_byte_length})"
            )
        return (
            f"RootRegionLineageFact(source_digest={self.source_digest!r}, "
            f"source_byte_length={self.source_byte_length}, {prov}, "
            f"issued={self.issued}, authority={self.authority})"
        )

    __str__ = __repr__


class RootRegionLineageState(_GraphFrozen):
    """Immutable root-region lineage state for one region scope.

    ``d_state`` wraps the ACTUAL accepted 018-d state by immutable
    reference (``InstanceOf``: nested revalidation never reruns,
    identity is preserved and dict input is refused); the region
    revision is the NEW composition revision (the bootstrap-
    accepted state is 1; every later accepted state change
    increments exactly once; replays and refusals never advance
    it) and stays in exact 1:1 with the wrapped D revision.
    ``root_facts`` retains the complete supported root-source
    evidence, provenance-discriminated (envelope / read /
    read_region), with the DERIVED flags at the last accepted
    transition; sorted and deduplicated by provenance identity.
    """

    lineage_key: str
    revision: int = Field(ge=0, le=MAX_REVISION)
    d_state: InstanceOf[CausalHistoryState]
    root_facts: tuple[RootRegionLineageFact, ...] = Field(default=(), max_length=_HARD_ROOT_FACTS)

    @field_validator("lineage_key")
    @classmethod
    def _v_lineage_key(cls, value: str) -> str:
        return _check_hex64(value, "lineage_key")

    @field_validator("root_facts", mode="before")
    @classmethod
    def _v_root_facts_preflight(cls, value: object) -> object:
        # The hard retention ceiling is prefetched BEFORE any
        # nested fact validation.
        if isinstance(value, (list, tuple)) and len(value) > _HARD_ROOT_FACTS:
            raise _fixed("root facts exceed the hard retention ceiling")
        return value

    @model_validator(mode="after")
    def _v_state(self) -> RootRegionLineageState:
        keys = tuple(_region_provenance_key(f.provenance) for f in self.root_facts)
        if tuple(sorted(keys)) != keys or len(set(keys)) != len(keys):
            raise _fixed("root facts must be sorted and deduplicated by provenance identity")
        envelope_facts = [f for f in self.root_facts if f.provenance.kind == "envelope"]
        anchor = self.d_state.root
        if anchor is not None:
            if len(envelope_facts) != 1:
                raise _fixed(
                    "the retained root anchor requires exactly its bootstrap envelope fact"
                )
            p = envelope_facts[0].provenance
            if not isinstance(p, EnvelopeRootProvenance):
                raise _fixed("unreachable: the envelope filter retains only the anchor fact")
            if (
                p.root_digest != anchor.root_digest
                or p.workspace != anchor.workspace
                or p.source_byte_length != anchor.source_byte_length
            ):
                raise _fixed("the envelope fact must bind the actual root anchor identity")
            if (
                envelope_facts[0].source_digest != anchor.root_digest
                or envelope_facts[0].source_byte_length != anchor.source_byte_length
            ):
                raise _fixed("the envelope fact source must equal the actual root body")
        elif envelope_facts:
            raise _fixed("an envelope fact requires the actual retained root anchor")
        total_source_bytes = 0
        for fact in self.root_facts:
            total_source_bytes += fact.source_byte_length
            if total_source_bytes > _HARD_ROOT_SOURCE_BYTES:
                raise _fixed("retained root source bytes exceed the hard policy ceiling")
        if self.revision != self.d_state.revision:
            raise _fixed("the region revision must stay in exact 1:1 with the wrapped D revision")
        return self

    def __repr__(self) -> str:  # noqa: D105 - privacy law
        return (
            f"RootRegionLineageState(lineage_key={self.lineage_key!r}, "
            f"revision={self.revision}, d_state={self.d_state!r}, "
            f"root_facts={len(self.root_facts)})"
        )

    __str__ = __repr__


class RootRegionLineageTransition(_GraphFrozen):
    """One bounded root-region lineage transition result.

    ``state`` is the state AFTER the transition (the EXACT prior
    region state on every refusal and on replay, by identity);
    ``outcome`` is closed (the accepted 018-h vocabulary,
    propagated never relabeled); ``diagnostics`` is a sorted,
    deduplicated closed-enum tuple whose length never exceeds the
    hard diagnostic ceiling; ``d_transition`` retains the ACTUAL
    underlying 018-d transition (``None`` only for early region
    refusals before any D work).  An accepted D candidate may be
    carried only as explicitly discarded transition evidence: the
    region state stays the EXACT prior state and the revisions
    stay unchanged.  ``new_root_facts`` lists the facts retained
    by an accepted transition (empty on every refusal and on
    replay).
    """

    state: InstanceOf[RootRegionLineageState]
    outcome: RootLineageOutcome
    diagnostics: tuple[RootLineageLimitation, ...] = ()
    d_transition: InstanceOf[CausalHistoryTransition] | None = None
    revision_before: int = Field(ge=0)
    revision_after: int = Field(ge=0)
    d_revision_before: int = Field(ge=0)
    d_revision_after: int = Field(ge=0)
    new_root_facts: tuple[RootRegionLineageFact, ...] = Field(
        default=(), max_length=_HARD_ROOT_FACTS
    )

    @field_validator("diagnostics", mode="before")
    @classmethod
    def _v_diagnostics_preflight(cls, value: object) -> object:
        if isinstance(value, (list, tuple)) and len(value) > _DIAGNOSTIC_CEILING:
            raise _fixed("diagnostics exceed the hard ceiling")
        return value

    @field_validator("new_root_facts", mode="before")
    @classmethod
    def _v_new_root_facts_preflight(cls, value: object) -> object:
        if isinstance(value, (list, tuple)) and len(value) > _HARD_ROOT_FACTS:
            raise _fixed("new root facts exceed the hard retention ceiling")
        return value

    @model_validator(mode="after")
    def _v_transition(self) -> RootRegionLineageTransition:
        if tuple(sorted(set(self.diagnostics))) != self.diagnostics:
            raise _fixed("diagnostics must be sorted and deduplicated")
        if len(self.diagnostics) > _DIAGNOSTIC_CEILING:
            raise _fixed("diagnostics exceed the hard ceiling")
        if self.state.revision != self.revision_after:
            raise _fixed("the transition state must carry the after revision")
        if self.outcome is RootLineageOutcome.ACCEPTED:
            if self.revision_after != self.revision_before + 1:
                raise _fixed("an accepted transition advances the revision exactly once")
        elif self.revision_after != self.revision_before:
            raise _fixed("a non-accepted transition never advances the revision")
        new_keys = tuple(_region_provenance_key(f.provenance) for f in self.new_root_facts)
        if tuple(sorted(new_keys)) != new_keys or len(set(new_keys)) != len(new_keys):
            raise _fixed("new root facts must be sorted and deduplicated by provenance identity")
        if self.outcome is not RootLineageOutcome.ACCEPTED and self.new_root_facts:
            raise _fixed("only an accepted transition retains new root facts")
        if self.d_transition is None:
            if self.outcome is RootLineageOutcome.ACCEPTED:
                raise _fixed("an accepted transition carries the actual accepted D transition")
            if self.outcome is RootLineageOutcome.REPLAYED:
                raise _fixed("a replayed transition carries the replayed D transition")
            if self.d_revision_after != self.d_revision_before:
                raise _fixed("no D transition carries no D revision change")
        if self.d_transition is not None:
            d_outcome = self.d_transition.outcome.value
            if self.outcome is RootLineageOutcome.ACCEPTED:
                if d_outcome != "accepted":
                    raise _fixed("an accepted transition carries an accepted D transition")
                if self.state.d_state is not self.d_transition.state:
                    raise _fixed(
                        "an accepted transition wraps the exact accepted D candidate state"
                    )
            elif self.outcome is RootLineageOutcome.REPLAYED:
                if d_outcome != "replayed":
                    raise _fixed("a replayed transition carries a replayed D transition")
                if self.state.d_state is not self.d_transition.state:
                    raise _fixed("a replayed transition retains the exact prior D state")
            else:
                # A refused region transition carries the ACTUAL prior D
                # refusal or replay -- or the ACTUAL accepted D
                # candidate that the region post-D law (retention cap,
                # envelope verification) atomically discarded: that
                # prepared evidence is retained by identity, never
                # relabeled a D failure (the region state remains the
                # EXACT prior state and the region revisions unchanged,
                # while the D revision fields below must equal the
                # ACTUAL discarded candidate's fields).
                if d_outcome not in (
                    "accepted",
                    "replayed",
                    "refused_cas_mismatch",
                    "refused_foreign_scope",
                    "refused_no_root",
                    "refused_root_conflict",
                    "refused_version_conflict",
                    "refused_conflict",
                    "refused_unknown_parent",
                    "refused_cycle",
                    "refused_over_bound",
                ):
                    raise _fixed("a refused transition carries an actual D transition outcome")
            if (
                self.d_revision_before != self.d_transition.revision_before
                or self.d_revision_after != self.d_transition.revision_after
            ):
                raise _fixed("the D revisions must match the actual D transition")
        return self

    def __repr__(self) -> str:  # noqa: D105 - privacy law
        return (
            f"RootRegionLineageTransition(outcome={self.outcome.value!r}, "
            f"revision={self.revision_before}->{self.revision_after}, "
            f"diagnostics={list(self.diagnostics)}, "
            f"new_root_facts={len(self.new_root_facts)})"
        )

    __str__ = __repr__


class RootRegionSelectionResult(_GraphFrozen):
    """The bounded pure current-root selection result (NEW
    contract, same closed selection law as the accepted H query).

    ``ok`` carries the ONE equal maximal root source with ALL its
    compatible maximal originals retained (witness facts of ANY
    supported kind); ``root_content_conflict`` is explicit
    conflicting maximal sources with NO selected current source;
    ``no_selected_root`` is the honest absence of any
    authoritative root fact; ``refused`` is the fixed typed query
    failure (never relabelled as a root absence).
    """

    outcome: RootSelectionOutcome
    selected_source_digest: str | None = None
    witness_facts: tuple[InstanceOf[RootRegionLineageFact], ...] = Field(
        default=(), max_length=_HARD_ROOT_FACTS
    )
    limitations: tuple[RootLineageLimitation, ...] = ()
    lineage_key: str
    revision: int = Field(ge=0, le=MAX_REVISION)

    @field_validator("lineage_key")
    @classmethod
    def _v_lineage_key(cls, value: str) -> str:
        return _check_hex64(value, "lineage_key")

    @field_validator("selected_source_digest")
    @classmethod
    def _v_selected(cls, value: str | None) -> str | None:
        if value is None:
            return value
        return _check_hex64(value, "selected_source_digest")

    @field_validator("limitations", mode="before")
    @classmethod
    def _v_limitations_preflight(cls, value: object) -> object:
        # The hard diagnostic ceiling is prefetched BEFORE any nested
        # enum validation, set or sort: an overbound collection is
        # refused without validating or sorting a single element.
        if isinstance(value, (list, tuple)) and len(value) > _DIAGNOSTIC_CEILING:
            raise _fixed("limitations exceed the hard ceiling")
        return value

    @field_validator("witness_facts", mode="before")
    @classmethod
    def _v_witness_facts_preflight(cls, value: object) -> object:
        if isinstance(value, (list, tuple)) and len(value) > _HARD_ROOT_FACTS:
            raise _fixed("witness facts exceed the hard retention ceiling")
        return value

    @model_validator(mode="after")
    def _v_result(self) -> RootRegionSelectionResult:
        if tuple(sorted(set(self.limitations))) != self.limitations:
            raise _fixed("limitations must be sorted and deduplicated")
        if len(self.limitations) > _DIAGNOSTIC_CEILING:
            raise _fixed("limitations exceed the hard ceiling")
        keys = tuple(_region_provenance_key(f.provenance) for f in self.witness_facts)
        if tuple(sorted(keys)) != keys or len(set(keys)) != len(keys):
            raise _fixed("witness facts must be sorted and deduplicated by provenance identity")
        for fact in self.witness_facts:
            if not fact.authority:
                raise _fixed("witness facts are authoritative root facts only")
        if self.outcome is RootSelectionOutcome.OK:
            if self.selected_source_digest is None or not self.witness_facts:
                raise _fixed("an ok selection carries the equal maximal source and its witnesses")
            for fact in self.witness_facts:
                if fact.source_digest != self.selected_source_digest:
                    raise _fixed("ok witnesses all carry the selected source digest")
        elif self.outcome is RootSelectionOutcome.ROOT_CONTENT_CONFLICT:
            if self.selected_source_digest is not None:
                raise _fixed("a conflict selection carries no selected current source")
            if len(self.witness_facts) < 2:
                raise _fixed("a content conflict carries at least two maximal witnesses")
            if len({f.source_digest for f in self.witness_facts}) < 2:
                raise _fixed("a content conflict requires differing maximal root sources")
        else:
            if self.selected_source_digest is not None or self.witness_facts:
                raise _fixed("a non-ok selection carries no selected current source")
            if self.outcome is RootSelectionOutcome.REFUSED and not self.limitations:
                raise _fixed("a refused selection exposes its fixed typed limitations")
        return self

    def __repr__(self) -> str:  # noqa: D105 - privacy law
        return (
            f"RootRegionSelectionResult(outcome={self.outcome.value!r}, "
            f"selected_source_digest={self.selected_source_digest!r}, "
            f"witness_facts={len(self.witness_facts)}, "
            f"limitations={list(self.limitations)}, "
            f"lineage_key={self.lineage_key!r}, revision={self.revision})"
        )

    __str__ = __repr__


# --- The versioned region lineage scope -----------------------------------


def root_region_ns_scalar_shape_ok(ns: object) -> bool:
    """Closed scalar fence over the ACTUAL region namespace scalar
    fields (identity, workspace, mode, versions, opaque keys)
    BEFORE any wide revalidation dump can walk an unexpected
    container."""
    if not isinstance(ns, RootRegionLineageNamespace):
        return False
    return (
        _hb_str(ns.principal, 1, 256)
        and _hb_str(ns.session, 1, 256)
        and _hb_str(ns.repository, 1, 256)
        and _hb_str(ns.route, 1, 64)
        and _hb_str(ns.model_identity, 1, 256)
        and _hb_str(ns.config_fingerprint, 1, 1024)
        and _hb_str(ns.workspace, 1, 1024)
        and isinstance(ns.mode, AdmissionMode)
        and _hb_str(ns.lineage_id, 1, 128)
        and _hb_hex64(ns.history_key)
        and _hb_hex64(ns.lineage_key)
        and _hb_str(ns.admission_namespace_key, 1, 128)
        and _hb_str(ns.admission_scoped_key, 1, 128)
        and _hb_str(ns.state_scoped_key, 1, 128)
        and _hb_str(ns.admission_version, 1, 128)
        and _hb_str(ns.observation_version, 1, 128)
        and _hb_str(ns.graph_version, 1, 128)
        and _hb_str(ns.reference_version, 1, 128)
        and _hb_str(ns.proof_version, 1, 128)
        and _hb_str(ns.history_version, 1, 128)
        and _hb_str(ns.arguments_version, 1, 128)
        and _hb_str(ns.contract_version, 1, 128)
        and _hb_str(ns.policy_version, 1, 128)
    )


class RootRegionLineageNamespace(_GraphFrozen):
    """Explicit trusted INTERNAL root-region lineage scope (018-p).

    The scope binds the ACTUAL accepted 018-d causal-history scope
    (its actual fields AND its actual ``history_key`` /
    ``state_scoped_key`` revalidated through the real accepted D
    validators -- the opaque keys alone are not enough) plus the
    NEW root-region contract/policy versions and the ACTUAL
    UNCHANGED ``RootLineageBounds`` (the accepted 018-h bound
    set, reused as an independent inherited domain).  The
    independent inherited D/B local domains beneath the ONE new-
    operation outer stay intact.  ``lineage_key`` is recomputed
    from the actual D ``history_key`` and the NEW fields on every
    construction (factory and direct) and a mismatch is refused.

    Object construction is NOT authentication: this is an
    internal trusted boundary, never a public body/header
    authority path.  No anonymous fallback and no cross-scope
    reuse.  Errors and operational reprs suppress all private
    ID/source/marker/identity values.
    """

    principal: str = Field(min_length=1, max_length=256)
    session: str = Field(min_length=1, max_length=256)
    repository: str = Field(min_length=1, max_length=256)
    route: str = Field(min_length=1, max_length=64)
    model_identity: str = Field(min_length=1, max_length=256)
    config_fingerprint: str
    workspace: str
    mode: AdmissionMode
    admission_version: str
    observation_version: str
    graph_version: str
    reference_version: str
    proof_version: str
    bounds: BundleAdmissionBounds
    proof_bounds: BundleProofBounds
    graph_bounds: GraphBounds
    observation_bounds: ObservationBounds
    admission_namespace_key: str
    admission_scoped_key: str
    lineage_id: str = Field(min_length=1, max_length=128)
    history_version: str
    arguments_version: str
    history_bounds: HistoryBounds
    history_key: str
    state_scoped_key: str
    contract_version: str = ROOT_REGION_LINEAGE_CONTRACT_VERSION
    policy_version: str = ROOT_REGION_LINEAGE_POLICY_VERSION
    root_lineage_bounds: RootLineageBounds = Field(default_factory=RootLineageBounds)
    lineage_key: str

    @field_validator("lineage_id")
    @classmethod
    def _v_lineage_id(cls, value: str) -> str:
        if not 1 <= len(value) <= 128 or any(c.isspace() for c in value):
            raise _fixed("lineage_id must be 1..128 non-space characters")
        try:
            value.encode("utf-8")
        except UnicodeEncodeError:
            raise _fixed("lineage_id must be valid UTF-8") from None
        return value

    @field_validator("contract_version", "policy_version")
    @classmethod
    def _v_version(cls, value: str, info: object) -> str:
        field_name = getattr(info, "field_name", "version") or "version"
        if not 1 <= len(value) <= 128 or any(c.isspace() for c in value):
            raise _fixed(f"{field_name} must be 1..128 non-space characters")
        return value

    @field_validator(
        "admission_namespace_key",
        "admission_scoped_key",
        "history_key",
        "state_scoped_key",
        "lineage_key",
    )
    @classmethod
    def _v_hex64(cls, value: str, info: object) -> str:
        return _check_hex64(value, getattr(info, "field_name", "key") or "key")

    @model_validator(mode="after")
    def _v_scope(self) -> RootRegionLineageNamespace:
        # Revalidate the ACTUAL accepted 018-d scope on EVERY
        # construction (factory and direct), exactly as the
        # accepted H scope law: the actual D field constraints,
        # the nested bound sets, the admission re-validation and
        # BOTH D 64-hex keys are rerun through the real accepted
        # D validators.  The closed scalar fences over EVERY
        # nested bound set run BEFORE the nested model_dumps.
        if (
            not admission_bounds_shape_ok(self.bounds)
            or not proof_bounds_shape_ok(self.proof_bounds)
            or not graph_bounds_shape_ok(self.graph_bounds)
            or not observation_bounds_shape_ok(self.observation_bounds)
            or not history_bounds_shape_ok(self.history_bounds)
            or not root_lineage_bounds_shape_ok(self.root_lineage_bounds)
        ):
            raise _fixed("the nested region bound sets must carry actual scalar fields")
        try:
            CausalHistoryNamespace.model_validate(
                {
                    "principal": self.principal,
                    "session": self.session,
                    "repository": self.repository,
                    "route": self.route,
                    "model_identity": self.model_identity,
                    "config_fingerprint": self.config_fingerprint,
                    "workspace": self.workspace,
                    "mode": self.mode.value,
                    "admission_version": self.admission_version,
                    "observation_version": self.observation_version,
                    "graph_version": self.graph_version,
                    "reference_version": self.reference_version,
                    "proof_version": self.proof_version,
                    "bounds": self.bounds.model_dump(warnings=False),
                    "proof_bounds": self.proof_bounds.model_dump(warnings=False),
                    "graph_bounds": self.graph_bounds.model_dump(warnings=False),
                    "observation_bounds": self.observation_bounds.model_dump(warnings=False),
                    "admission_namespace_key": self.admission_namespace_key,
                    "admission_scoped_key": self.admission_scoped_key,
                    "lineage_id": self.lineage_id,
                    "history_version": self.history_version,
                    "arguments_version": self.arguments_version,
                    "history_bounds": self.history_bounds.model_dump(warnings=False),
                    "history_key": self.history_key,
                    "state_scoped_key": self.state_scoped_key,
                }
            )
            RootLineageBounds.model_validate(self.root_lineage_bounds.model_dump(warnings=False))
        except Exception:
            raise _fixed("region scope failed the actual accepted history validation") from None
        if self.lineage_key != _lineage_key(
            self.history_key,
            self.contract_version,
            self.policy_version,
            self.root_lineage_bounds,
        ):
            raise _fixed("lineage_key does not match the actual region scope fields")
        return self

    def __repr__(self) -> str:  # noqa: D105 - privacy law
        return (
            f"RootRegionLineageNamespace(principal={PRIVATE_ID_PLACEHOLDER}, "
            f"session={PRIVATE_ID_PLACEHOLDER}, "
            f"repository={PRIVATE_ID_PLACEHOLDER}, "
            f"route={PRIVATE_ID_PLACEHOLDER}, "
            f"model_identity={PRIVATE_ID_PLACEHOLDER}, "
            f"config_fingerprint={PRIVATE_ID_PLACEHOLDER}, "
            f"workspace={PRIVATE_ID_PLACEHOLDER}, "
            f"mode={self.mode!r}, "
            f"lineage_id={PRIVATE_ID_PLACEHOLDER}, "
            f"contract_version={self.contract_version!r}, "
            f"policy_version={self.policy_version!r}, "
            f"root_lineage_bounds={self.root_lineage_bounds!r}, "
            f"history_key={self.history_key!r}, "
            f"lineage_key={self.lineage_key!r})"
        )

    __str__ = __repr__


def make_root_region_lineage_namespace(
    admission: object,
    lineage_id: str,
    *,
    bounds: RootLineageBounds | None = None,
    history_bounds: HistoryBounds | None = None,
) -> RootRegionLineageNamespace:
    """Factory for a root-region scope over the ACTUAL accepted
    018-d causal-history scope.

    The ACTUAL admission namespace is bound through the accepted D
    factory (its actual fields AND both 64-hex keys recomputed);
    the NEW root-region versions and the ACTUAL UNCHANGED root
    lineage bounds are bound into the recomputed ``lineage_key``
    (the accepted version-agnostic key recipe).  A forged, stale
    or borrowed key pair is refused.  Not authentication.
    """
    from .bundle_admission_models import BundleAdmissionNamespace
    from .root_lineage_models import _revalidate_root_lineage_bounds

    if not isinstance(admission, BundleAdmissionNamespace):
        raise _fixed("the region scope requires the ACTUAL accepted admission namespace")
    d_ns = make_causal_history_namespace(admission, lineage_id, bounds=history_bounds)
    effective_bounds = _revalidate_root_lineage_bounds(
        RootLineageBounds() if bounds is None else bounds
    )
    lineage_key = _lineage_key(
        d_ns.history_key,
        ROOT_REGION_LINEAGE_CONTRACT_VERSION,
        ROOT_REGION_LINEAGE_POLICY_VERSION,
        effective_bounds,
    )
    return RootRegionLineageNamespace(
        principal=d_ns.principal,
        session=d_ns.session,
        repository=d_ns.repository,
        route=d_ns.route,
        model_identity=d_ns.model_identity,
        config_fingerprint=d_ns.config_fingerprint,
        workspace=d_ns.workspace,
        mode=d_ns.mode,
        admission_version=d_ns.admission_version,
        observation_version=d_ns.observation_version,
        graph_version=d_ns.graph_version,
        reference_version=d_ns.reference_version,
        proof_version=d_ns.proof_version,
        bounds=d_ns.bounds,
        proof_bounds=d_ns.proof_bounds,
        graph_bounds=d_ns.graph_bounds,
        observation_bounds=d_ns.observation_bounds,
        admission_namespace_key=d_ns.admission_namespace_key,
        admission_scoped_key=d_ns.admission_scoped_key,
        lineage_id=d_ns.lineage_id,
        history_version=d_ns.history_version,
        arguments_version=d_ns.arguments_version,
        history_bounds=d_ns.history_bounds,
        history_key=d_ns.history_key,
        state_scoped_key=d_ns.state_scoped_key,
        root_lineage_bounds=effective_bounds,
        lineage_key=lineage_key,
    )

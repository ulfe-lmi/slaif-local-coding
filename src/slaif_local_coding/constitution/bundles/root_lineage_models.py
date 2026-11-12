"""Versioned root-authority lineage records (objective 018-h; INERT).

``ROOT_LINEAGE_CONTRACT_VERSION = "cache-root-lineage/v1"``;
``ROOT_LINEAGE_POLICY_VERSION = "root-lineage-policy/v1"``.
``ROOT_LINEAGE_MIXED_OBSERVATION_VERSION =
"root-lineage-mixed-observation/v1"`` (the 018-o root-aware mixed
observation operation's versioned policy identity, documented for
the later runtime/recovery configuration identity; the accepted
contract/policy versions, schemas, defaults, recipe bytes and cap
domains are unchanged by it).

This module binds the ACTUAL accepted 018-d causal-history scope (its
actual identity/config/workspace/mode fields, both admission 64-hex
keys, the seven actual version identities, the four inherited bound
sets, the lineage ID and the actual ``history_key`` /
``state_scoped_key`` -- all revalidated against the real accepted
validators) plus the NEW root-lineage contract/policy versions and
the NEW root-lineage bounds into a recompute-and-verify lineage
scope.  It defines the typed immutable root-lineage records: the
discriminated actual root-source provenance (bootstrap ENVELOPE
anchor identity versus retained complete singleton root READ), the
retained root fact with DERIVED issued/authority flags, the state
that wraps the ACTUAL 018-d state by immutable reference, the bounded
transition result and the pure current-root selection result.

It is pure and inert: no pipeline activation, no RAM service/locks,
no compiler, no disk, no HTTP/SSE observer and no new metrics.  The
state machine itself lives in ``root_lineage.py``.

A selected current root is a DISTINCT derived source/authority fact:
the bootstrap RootAnchor, the CAUSAL_ROOT_FACT identity, every
historical proof binding, occurrence identity and frozen parent link
remain immutable facts and are never rewritten, relabelled or
superseded by selection.  Object construction is NOT authentication:
this is an internal trusted boundary, never a public body/header
authority path.
"""

from __future__ import annotations

import json
from enum import StrEnum
from typing import Annotated, Literal

from pydantic import Field, InstanceOf, field_validator, model_validator

from .bundle_admission_models import (
    ADMISSION_CONTRACT_VERSION,
    AdmissionMode,
    BundleAdmissionBounds,
    BundleAdmissionNamespace,
)
from .bundle_proof_models import BUNDLE_PROOF_CONTRACT_VERSION, BundleProofBounds
from .causal_history_models import (
    CAUSAL_ARGUMENTS_JSON_VERSION,
    CAUSAL_HISTORY_CONTRACT_VERSION,
    MAX_REVISION,
    CausalHistoryNamespace,
    CausalHistoryState,
    CausalHistoryTransition,
    HistoryBounds,
    make_causal_history_namespace,
)
from .graph_models import (
    GRAPH_CONTRACT_VERSION,
    REFERENCE_GRAMMAR,
    GraphBounds,
    _check_hex64,
    _fixed,
    _GraphFrozen,
    _sha256_hex,
)
from .observation_models import OBSERVER_VERSION, PRIVATE_ID_PLACEHOLDER, ObservationBounds

ROOT_LINEAGE_CONTRACT_VERSION = "cache-root-lineage/v1"
ROOT_LINEAGE_POLICY_VERSION = "root-lineage-policy/v1"
ROOT_LINEAGE_MIXED_OBSERVATION_VERSION = "root-lineage-mixed-observation/v1"

#: The hard diagnostic ceiling (``RootLineageBounds.max_diagnostics``
#: default) restated for the closed model shape, mirroring the
#: accepted 018-d transition law.
_DIAGNOSTIC_CEILING = 64

#: The hard policy ceiling on logical retained root source bytes
#: (``RootLineageBounds.max_retained_root_source_bytes`` default)
#: restated for the closed model shape.  Stricter EFFECTIVE bounds
#: are enforced at the charged kernel boundary, never by this model
#: alone.
_HARD_ROOT_SOURCE_BYTES = 16777216

#: The hard retention ceiling (``RootLineageBounds.max_root_facts``
#: default) restated as the model-shape tuple preflight.
_HARD_ROOT_FACTS = 1024


class RootLineageBounds(_GraphFrozen):
    """NEW finite root-lineage bounds (objective 018-h).

    The order fixes the defaults AND the hard ceilings exactly:
    stricter positive values are permitted and ANY wider direct or
    factory construction is refused.  ``max_total_work_units`` is the
    ONE outer PER-OPERATION work ledger covering the full new
    operation (early gates, actual original observation/collection,
    old-state validation, D transition/argument/result/DAG work,
    lineage acquisition/ancestry/maxima/source/provenance/index/
    output work); the inherited D local per-transition work ledger
    keeps its OWN domain and ceiling (no global minimum, no
    per-request/group/fact resets).  Source and work units are never
    tokens/cache occupancy/RSS.
    """

    #: Retained root facts (bootstrap + EACH distinct retained
    #: complete supported root-read candidate, including unproven;
    #: replay never adds).
    max_root_facts: int = Field(default=1024, ge=1, le=1024)
    #: Logical exact UTF-8 root source bytes over ALL retained facts
    #: (bootstrap once, even when proofs share underlying immutable
    #: storage).
    max_retained_root_source_bytes: int = Field(default=16777216, ge=1, le=16777216)
    #: ONE outer PER-OPERATION work ledger.
    max_total_work_units: int = Field(default=1048576, ge=1, le=1048576)
    #: TOTAL final closed-enum diagnostics per result.
    max_diagnostics: int = Field(default=64, ge=1, le=64)


class RootLineageOutcome(StrEnum):
    """Closed transition outcomes.

    The accepted 018-d vocabulary is mirrored 1:1 (propagated, never
    relabeled), plus the NEW H root-authority refusal.  ``accepted``
    advances the H composition revision exactly once; ``replayed``
    is a pure idempotent transition (no revision advance, no state
    mutation); every ``refused_*`` preserves the EXACT prior H state.
    """

    ACCEPTED = "accepted"
    REPLAYED = "replayed"
    REFUSED_CAS_MISMATCH = "refused_cas_mismatch"
    REFUSED_FOREIGN_SCOPE = "refused_foreign_scope"
    REFUSED_NO_ROOT = "refused_no_root"
    REFUSED_ROOT_CONFLICT = "refused_root_conflict"
    REFUSED_VERSION_CONFLICT = "refused_version_conflict"
    REFUSED_CONFLICT = "refused_conflict"
    REFUSED_UNKNOWN_PARENT = "refused_unknown_parent"
    REFUSED_CYCLE = "refused_cycle"
    REFUSED_OVER_BOUND = "refused_over_bound"
    #: A same-batch envelope whose changed bytes have no
    #: independent accepted root-read authority (atomic
    #: whole-transition refusal).
    REFUSED_ROOT_AUTHORITY = "refused_root_authority"


class RootLineageLimitation(StrEnum):
    """Closed fixed diagnostic vocabulary for root-lineage results.

    The accepted 018-d names are carried under their EXACT fixed
    names (propagated, never relabeled; the same 018-c/018-g
    pattern) plus the NEW H names.  Free-form strings and arbitrary
    text are rejected; no value echoes payload content.
    """

    # H-owned.
    ENVELOPE_UNPROVEN = "envelope_unproven"
    FOREIGN_SCOPE = "foreign_scope"
    ROOT_SOURCE_UNPROVEN = "root_source_unproven"
    ROOT_FACTS_OVER_BOUND = "root_facts_over_bound"
    ROOT_SOURCE_BYTES_OVER_BOUND = "root_source_bytes_over_bound"
    # Mirrored 1:1 from CausalHistoryLimitation (exact names).
    NO_ROOT = "no_root"
    COMPETING_ROOTS = "competing_roots"
    WORKSPACE_MISMATCH = "workspace_mismatch"
    ROOT_CONTEXT_MISMATCH = "root_context_mismatch"
    WORKSPACE_UNPROVEN = "workspace_unproven"
    VERSION_UNSUPPORTED = "version_unsupported"
    BATCH_OVER_BOUND = "batch_over_bound"
    DIAGNOSTICS_FULL = "diagnostics_full"
    ARGUMENTS_UNSUPPORTED = "arguments_unsupported"
    ARGUMENTS_MALFORMED_UNICODE = "arguments_malformed_unicode"
    ARGUMENTS_OVER_BOUND = "arguments_over_bound"
    CALL_ID_MISSING = "call_id_missing"
    CALL_ID_MALFORMED = "call_id_malformed"
    FRONTIER_OVER_BOUND = "frontier_over_bound"
    FRONTIER_CONFLICT = "frontier_conflict"
    ISSUANCE_CONFLICT = "issuance_conflict"
    RESULT_CONFLICT = "result_conflict"
    RECEIPT_BINDING_MISMATCH = "receipt_binding_mismatch"
    RECEIPT_UNKNOWN_PARENT = "receipt_unknown_parent"
    RECEIPT_CYCLE = "receipt_cycle"
    SEAM_CONFLICT = "seam_conflict"
    BUNDLES_OVER_BOUND = "bundles_over_bound"
    SOURCE_OVER_BOUND = "source_over_bound"
    TOTAL_SOURCE_OVER_BOUND = "total_source_over_bound"
    MEMBERS_OVER_BOUND = "members_over_bound"
    SEGMENTS_OVER_BOUND = "segments_over_bound"
    MARKER_OVER_BOUND = "marker_over_bound"
    MARKER_SEARCH_OVER_BOUND = "marker_search_over_bound"
    MARKER_EMPTY = "marker_empty"
    MARKER_MISSING = "marker_missing"
    MARKER_DUPLICATE = "marker_duplicate"
    MARKER_ORDER = "marker_order"
    MARKER_OVERLAP = "marker_overlap"
    PLAN_UNSUPPORTED = "plan_unsupported"
    MEMBER_UNRESOLVED = "member_unresolved"
    MEMBER_PATH_OVER_BOUND = "member_path_over_bound"
    SEGMENT_UNEXPLAINED = "segment_unexplained"
    OUTPUT_INCONSISTENT = "output_inconsistent"
    SOURCE_CONFLICT = "source_conflict"
    MALFORMED_BINDING = "malformed_binding"
    ISSUANCES_OVER_BOUND = "issuances_over_bound"
    OCCURRENCES_OVER_BOUND = "occurrences_over_bound"
    CAUSAL_LINKS_OVER_BOUND = "causal_links_over_bound"
    RESULTS_OVER_BOUND = "results_over_bound"
    RETAINED_MEMBERS_OVER_BOUND = "retained_members_over_bound"
    RETAINED_PIECES_OVER_BOUND = "retained_pieces_over_bound"
    RETAINED_SOURCE_BYTES_OVER_BOUND = "retained_source_bytes_over_bound"
    WORK_UNITS_OVER_BOUND = "work_units_over_bound"
    REVISION_OVERFLOW = "revision_overflow"
    REPLAY_POSITION_SHIFTED = "replay_position_shifted"


class RootSelectionOutcome(StrEnum):
    """Closed pure current-root selection outcomes.

    ``ok`` carries the ONE equal maximal root source with ALL its
    compatible maximal originals retained; ``root_content_conflict``
    is explicit conflicting maximal sources with NO selected current
    source (a typed non-ready result, never resource exhaustion);
    ``no_selected_root`` is the honest absence of any authoritative
    root fact; ``refused`` is the fixed typed QUERY failure when the
    input state/scope cannot be positively interpreted (budget,
    foreign scope, unsupported versions, malformed state) -- a
    refusal is never relabelled as a root absence.
    """

    OK = "ok"
    ROOT_CONTENT_CONFLICT = "root_content_conflict"
    NO_SELECTED_ROOT = "no_selected_root"
    REFUSED = "refused"


# --- Discriminated actual root-source provenance -------------------------


class EnvelopeRootProvenance(_GraphFrozen):
    """Bootstrap anchor provenance.

    Binds the ACTUAL retained RootAnchor identity (digest, evidenced
    scope and exact source bytes) of the ONE legitimate effective
    Responses AGENTS envelope accepted at bootstrap.  The anchor's
    private source text is never duplicated here.  Construction is
    not authentication.
    """

    kind: Literal["envelope"] = "envelope"
    root_digest: str
    workspace: str
    source_byte_length: int = Field(ge=0)

    @field_validator("root_digest")
    @classmethod
    def _v_root_digest(cls, value: str) -> str:
        return _check_hex64(value, "root_digest")

    @field_validator("workspace")
    @classmethod
    def _v_workspace(cls, value: str) -> str:
        if not 1 <= len(value) <= 1024 or not value.startswith("/"):
            raise _fixed("workspace must be a 1..1024 absolute POSIX path")
        if any(ord(c) < 0x20 or ord(c) == 0x7F or c.isspace() for c in value):
            raise _fixed("workspace must not contain control characters")
        try:
            value.encode("utf-8")
        except UnicodeEncodeError:
            raise _fixed("workspace must be valid UTF-8") from None
        return value

    def __repr__(self) -> str:  # noqa: D105 - privacy law
        return (
            f"EnvelopeRootProvenance(root_digest={self.root_digest!r}, "
            f"workspace={PRIVATE_ID_PLACEHOLDER}, "
            f"source_byte_length={self.source_byte_length})"
        )

    __str__ = __repr__


class ReadRootProvenance(_GraphFrozen):
    """Retained complete singleton root READ provenance.

    Binds the ACTUAL completed original read: the occurrence/call
    identity, the original endpoint and the original whole-read
    source binding (digest and byte length of the read's exact
    aggregate source) RETAINED FOREVER from the original proof -- H
    never re-hashes source, never rewrites the original binding, and
    never manufactures an envelope around read text.
    """

    kind: Literal["read"] = "read"
    occurrence_id: str
    call_id: str
    endpoint: str
    read_digest: str
    read_byte_length: int = Field(ge=0)

    @field_validator("occurrence_id")
    @classmethod
    def _v_occurrence_id(cls, value: str) -> str:
        return _check_hex64(value, "occurrence_id")

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

    @field_validator("read_digest")
    @classmethod
    def _v_read_digest(cls, value: str) -> str:
        return _check_hex64(value, "read_digest")

    def __repr__(self) -> str:  # noqa: D105 - privacy law
        return (
            f"ReadRootProvenance(occurrence_id={self.occurrence_id!r}, "
            f"call_id={PRIVATE_ID_PLACEHOLDER}, endpoint={self.endpoint!r}, "
            f"read_digest={self.read_digest!r}, "
            f"read_byte_length={self.read_byte_length})"
        )

    __str__ = __repr__


RootLineageProvenance = Annotated[
    EnvelopeRootProvenance | ReadRootProvenance,
    Field(discriminator="kind"),
]


def _provenance_key(provenance: RootLineageProvenance) -> tuple[str, str]:
    """The sorted-deduplicated retention identity of one provenance."""
    if provenance.kind == "envelope":
        return ("envelope", "")
    return ("read", provenance.occurrence_id)


class RootLineageFact(_GraphFrozen):
    """ONE retained root-source fact.

    ``source_digest``/``source_byte_length`` are the ROOT BODY (the
    exact root source bytes) -- comparable across facts (equal
    incomparable witnesses are compatible; differing maximal sources
    conflict).  For a read fact the root body is the read's exact
    aggregate source (a singleton complete root read), and the
    original whole-read binding stays in the READ provenance.

    ``issued`` and ``authority`` are DERIVED flags recomputed by the
    composition on EVERY accepted D transition (the S1 law): a read
    fact is issued when its matching INTERNAL issuance is retained,
    and authoritative only when issued AND its occurrence is
    anchored AND the frozen parent evidence reaches the ORIGINAL
    bootstrap root fact.  The envelope fact is the anchor itself:
    never issued, always authoritative.  Flags are derived state,
    never caller-supplied authority.
    """

    source_digest: str
    source_byte_length: int = Field(ge=0, le=_HARD_ROOT_SOURCE_BYTES)
    provenance: RootLineageProvenance
    issued: bool = False
    authority: bool = False

    @field_validator("source_digest")
    @classmethod
    def _v_source_digest(cls, value: str) -> str:
        return _check_hex64(value, "source_digest")

    @model_validator(mode="after")
    def _v_flags(self) -> RootLineageFact:
        p = self.provenance
        if p.kind == "envelope":
            if self.issued or not self.authority:
                raise _fixed("the bootstrap envelope fact is never issued and always authoritative")
            if (
                self.source_digest != p.root_digest
                or self.source_byte_length != p.source_byte_length
            ):
                raise _fixed("the envelope fact source must equal the anchor provenance binding")
        else:
            if self.authority and not self.issued:
                raise _fixed("a read root fact is authoritative only when issued")
            # A complete singleton root read's root body IS the
            # original whole-read source: the fact source binds the
            # retained original binding, never a re-hashed copy.
            if self.source_digest != p.read_digest or self.source_byte_length != p.read_byte_length:
                raise _fixed("a read fact source must equal the original whole-read binding")
        return self

    def __repr__(self) -> str:  # noqa: D105 - privacy law
        p = self.provenance
        if p.kind == "envelope":
            prov = (
                f"provenance=envelope(root_digest={p.root_digest!r}, "
                f"workspace={PRIVATE_ID_PLACEHOLDER}, "
                f"source_byte_length={p.source_byte_length})"
            )
        else:
            prov = (
                f"provenance=read(occurrence_id={p.occurrence_id!r}, "
                f"call_id={PRIVATE_ID_PLACEHOLDER}, endpoint={p.endpoint!r}, "
                f"read_digest={p.read_digest!r}, read_byte_length={p.read_byte_length})"
            )
        return (
            f"RootLineageFact(source_digest={self.source_digest!r}, "
            f"source_byte_length={self.source_byte_length}, {prov}, "
            f"issued={self.issued}, authority={self.authority})"
        )

    __str__ = __repr__


class RootLineageState(_GraphFrozen):
    """Immutable root-lineage state for one lineage scope.

    ``d_state`` wraps the ACTUAL accepted 018-d state by immutable
    reference (``InstanceOf``: nested revalidation never reruns,
    identity is preserved and dict input is refused); the H revision
    is the NEW composition revision (the bootstrap-accepted state is
    1; every later accepted state change increments exactly once;
    replays and refusals never advance it) and stays in exact 1:1
    with the wrapped D revision.  ``root_facts`` retains the
    complete supported root-source evidence, provenance-
    discriminated, with the DERIVED flags at the last accepted
    transition; sorted and deduplicated by provenance identity.
    """

    lineage_key: str
    revision: int = Field(ge=0, le=MAX_REVISION)
    d_state: InstanceOf[CausalHistoryState]
    root_facts: tuple[RootLineageFact, ...] = Field(default=(), max_length=_HARD_ROOT_FACTS)

    @field_validator("lineage_key")
    @classmethod
    def _v_lineage_key(cls, value: str) -> str:
        return _check_hex64(value, "lineage_key")

    @field_validator("root_facts", mode="before")
    @classmethod
    def _v_root_facts_preflight(cls, value: object) -> object:
        # The hard retention ceiling is prefetched BEFORE any nested
        # fact validation: an overbound collection is refused without
        # validating or sorting a single element.
        if isinstance(value, (list, tuple)) and len(value) > _HARD_ROOT_FACTS:
            raise _fixed("root facts exceed the hard retention ceiling")
        return value

    @model_validator(mode="after")
    def _v_state(self) -> RootLineageState:
        keys = tuple(_provenance_key(f.provenance) for f in self.root_facts)
        if tuple(sorted(keys)) != keys or len(set(keys)) != len(keys):
            raise _fixed("root facts must be sorted and deduplicated by provenance identity")
        envelope_facts = [f for f in self.root_facts if f.provenance.kind == "envelope"]
        anchor = self.d_state.root
        # The root-anchor presence law: the actual retained anchor
        # and the bootstrap envelope fact exist in exact 1:1 (a
        # state with the anchor always carries its envelope fact; a
        # rootless state never does).
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
        # The hard policy ceiling on logical retained root source
        # bytes (stricter effective bounds are the charged kernel's
        # law, never this model's).
        total_source_bytes = 0
        for fact in self.root_facts:
            total_source_bytes += fact.source_byte_length
            if total_source_bytes > _HARD_ROOT_SOURCE_BYTES:
                raise _fixed("retained root source bytes exceed the hard policy ceiling")
        # The composition and the wrapped D state advance in exact
        # 1:1 (every accepted H transition is one accepted D
        # transition; replays/refusals advance neither).
        if self.revision != self.d_state.revision:
            raise _fixed("the H revision must stay in exact 1:1 with the wrapped D revision")
        return self

    def __repr__(self) -> str:  # noqa: D105 - privacy law
        return (
            f"RootLineageState(lineage_key={self.lineage_key!r}, "
            f"revision={self.revision}, d_state={self.d_state!r}, "
            f"root_facts={len(self.root_facts)})"
        )

    __str__ = __repr__


class RootLineageTransition(_GraphFrozen):
    """One bounded root-lineage transition result.

    ``state`` is the state AFTER the transition (the EXACT prior H
    state on every refusal and on replay, by identity); ``outcome``
    is closed; ``diagnostics`` is a sorted, deduplicated closed-enum
    tuple whose length never exceeds the hard diagnostic ceiling.
    ``d_transition`` retains the ACTUAL underlying 018-d transition
    (``None`` only for early H refusals before any D work); the D
    revisions are documented, never treated as a source clock.  An
    ACCEPTED H transition carries the ACTUAL accepted D transition
    and wraps its exact state by identity (the after H state's
    ``d_state`` IS the accepted D candidate state, and the revisions
    stay coherent).  A REPLAYED H transition carries the ACTUAL
    replayed D transition holding the exact prior D state the prior
    H state wraps (identity).  A refused H result may carry an
    ACTUAL accepted D candidate that the H post-D law atomically
    discarded: the prepared candidate is
    retained by identity as evidence, the H state stays the EXACT
    prior state, and the H revisions stay unchanged.
    ``new_root_facts`` lists the facts retained by an accepted
    transition (empty on every refusal and on replay).
    """

    state: InstanceOf[RootLineageState]
    outcome: RootLineageOutcome
    diagnostics: tuple[RootLineageLimitation, ...] = ()
    d_transition: InstanceOf[CausalHistoryTransition] | None = None
    revision_before: int = Field(ge=0)
    revision_after: int = Field(ge=0)
    d_revision_before: int = Field(ge=0)
    d_revision_after: int = Field(ge=0)
    new_root_facts: tuple[RootLineageFact, ...] = Field(default=(), max_length=_HARD_ROOT_FACTS)

    @field_validator("diagnostics", mode="before")
    @classmethod
    def _v_diagnostics_preflight(cls, value: object) -> object:
        # The hard diagnostic ceiling is prefetched BEFORE any nested
        # enum validation, set or sort: an overbound collection is
        # refused without validating or sorting a single element.
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
    def _v_transition(self) -> RootLineageTransition:
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
        new_keys = tuple(_provenance_key(f.provenance) for f in self.new_root_facts)
        if tuple(sorted(new_keys)) != new_keys or len(set(new_keys)) != len(new_keys):
            raise _fixed("new root facts must be sorted and deduplicated by provenance identity")
        if self.outcome is not RootLineageOutcome.ACCEPTED and self.new_root_facts:
            raise _fixed("only an accepted transition retains new root facts")
        if self.d_transition is None:
            if self.outcome is RootLineageOutcome.ACCEPTED:
                raise _fixed("an accepted H transition carries the actual accepted D transition")
            if self.outcome is RootLineageOutcome.REPLAYED:
                raise _fixed("a replayed H transition carries the replayed D transition")
            if self.d_revision_after != self.d_revision_before:
                raise _fixed("no D transition carries no D revision change")
        if self.d_transition is not None:
            d_outcome = self.d_transition.outcome.value
            if self.outcome is RootLineageOutcome.ACCEPTED:
                if d_outcome != "accepted":
                    raise _fixed("an accepted H transition carries an accepted D transition")
                if self.state.d_state is not self.d_transition.state:
                    raise _fixed(
                        "an accepted H transition wraps the exact accepted D candidate state"
                    )
            elif self.outcome is RootLineageOutcome.REPLAYED:
                if d_outcome != "replayed":
                    raise _fixed("a replayed H transition carries a replayed D transition")
                if self.state.d_state is not self.d_transition.state:
                    raise _fixed("a replayed H transition retains the exact prior D state")
            else:
                # A refused H transition carries the ACTUAL prior D
                # refusal or replay -- or the ACTUAL accepted D
                # candidate that the H post-D law (unknown changed
                # envelope, root-fact/byte admission overflow)
                # atomically discarded: that prepared evidence is
                # retained by identity, never relabeled a D failure
                # (the H state remains the EXACT prior state and the
                # H revisions unchanged).
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
                    raise _fixed("a refused H transition carries the actual D transition only")
            if (
                self.d_revision_before != self.d_transition.revision_before
                or self.d_revision_after != self.d_transition.revision_after
            ):
                raise _fixed("the D revisions must match the actual D transition")
        return self

    def __repr__(self) -> str:  # noqa: D105 - privacy law
        return (
            f"RootLineageTransition(outcome={self.outcome.value!r}, "
            f"revision_before={self.revision_before}, "
            f"revision_after={self.revision_after}, "
            f"d_revision_before={self.d_revision_before}, "
            f"d_revision_after={self.d_revision_after}, "
            f"diagnostics={list(self.diagnostics)}, "
            f"new_root_facts={len(self.new_root_facts)}, "
            f"d_transition={'present' if self.d_transition is not None else 'absent'}, "
            f"state={self.state!r})"
        )

    __str__ = __repr__


class RootSelectionResult(_GraphFrozen):
    """One pure current-root selection result.

    ``ok``: the causal maximal authoritative ROOT facts carry ONE
    equal source digest and ALL compatible maximal originals are
    retained in ``witness_facts``.  ``root_content_conflict``:
    differing maximal root sources -- NO selected current source,
    at least two retained maximal witnesses with at least two
    differing source digests (actual maximality is the kernel's
    charged proof; the model enforces the intrinsic shape).
    ``no_selected_root``: no authoritative root fact at all (honest
    absence).  ``refused``: the fixed typed query failure for
    budget/foreign/version/malformed inputs, exposing at least one
    fixed limitation -- never relabelled as a root absence.
    Retained complete but unissued/unanchored root reads are NOT
    selected; their fixed typed limitation is exposed in
    ``limitations``.  Selection never chooses a lexical/receipt
    winner and never advances any revision.

    ``lineage_key``/``revision`` bind the result to the ACTUAL input
    H state's scope and revision at query time: an explicit
    validated ownership association (the result is valid for that
    exact state; any state change requires a fresh query).
    """

    outcome: RootSelectionOutcome
    selected_source_digest: str | None = None
    witness_facts: tuple[InstanceOf[RootLineageFact], ...] = Field(
        default=(), max_length=_HARD_ROOT_FACTS
    )
    limitations: tuple[RootLineageLimitation, ...] = ()
    lineage_key: str
    revision: int = Field(ge=0, le=MAX_REVISION)

    @field_validator("lineage_key")
    @classmethod
    def _v_lineage_key(cls, value: str) -> str:
        return _check_hex64(value, "lineage_key")

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

    @field_validator("selected_source_digest")
    @classmethod
    def _v_selected_digest(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return _check_hex64(value, "selected_source_digest")

    @model_validator(mode="after")
    def _v_result(self) -> RootSelectionResult:
        if tuple(sorted(set(self.limitations))) != self.limitations:
            raise _fixed("limitations must be sorted and deduplicated")
        if len(self.limitations) > _DIAGNOSTIC_CEILING:
            raise _fixed("limitations exceed the hard ceiling")
        keys = tuple(_provenance_key(f.provenance) for f in self.witness_facts)
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
            f"RootSelectionResult(outcome={self.outcome.value!r}, "
            f"selected_source_digest={self.selected_source_digest!r}, "
            f"witness_facts={len(self.witness_facts)}, "
            f"limitations={list(self.limitations)}, "
            f"lineage_key={self.lineage_key!r}, revision={self.revision})"
        )

    __str__ = __repr__


# --- The versioned lineage scope ------------------------------------------

# --- K5 closed scalar-shape fences (before any model_dump) -------------
#
# A forged nested model copy (model_copy/model_construct) can carry an
# unexpected container in a scalar slot; every H model_dump /
# revalidation path would then SERIALIZER-WALK that container before
# the typed refusal.  These O(1) closed fences (actual scalar type plus
# the declared hard cap, no traversal) run BEFORE every such dump.

_HEX_DIGITS = frozenset("0123456789abcdef")


def _hb_int(value: object, lo: int, hi: int) -> bool:
    """O(1) integral (non-bool) closed-int fence for one bounds field."""
    return isinstance(value, int) and not isinstance(value, bool) and lo <= value <= hi


def _hb_str(value: object, lo: int, hi: int) -> bool:
    """O(1) actual-str length fence (a container in a scalar slot is
    malformed, never a serializer traversal)."""
    return isinstance(value, str) and lo <= len(value) <= hi


def _hb_hex64(value: object) -> bool:
    """O(1) 64-hex fence for one opaque key field."""
    return isinstance(value, str) and len(value) == 64 and set(value) <= _HEX_DIGITS


def root_lineage_bounds_shape_ok(bounds: object) -> bool:
    """Closed scalar fence over the NEW H bound set."""
    return (
        isinstance(bounds, RootLineageBounds)
        and _hb_int(bounds.max_root_facts, 1, 1024)
        and _hb_int(bounds.max_retained_root_source_bytes, 1, 16777216)
        and _hb_int(bounds.max_total_work_units, 1, 1048576)
        and _hb_int(bounds.max_diagnostics, 1, 64)
    )


def history_bounds_shape_ok(bounds: object) -> bool:
    """Closed scalar fence over the inherited D history bound set."""
    return (
        isinstance(bounds, HistoryBounds)
        and _hb_int(bounds.max_issuances, 1, 4096)
        and _hb_int(bounds.max_occurrences, 1, 4096)
        and _hb_int(bounds.max_causal_links, 1, 65536)
        and _hb_int(bounds.max_frontier_members, 1, 1024)
        and _hb_int(bounds.max_observed_results, 1, 8192)
        and _hb_int(bounds.max_retained_members, 1, 16384)
        and _hb_int(bounds.max_retained_pieces, 1, 32768)
        and _hb_int(bounds.max_retained_source_bytes, 1, 16777216)
        and _hb_int(bounds.max_argument_bytes, 1, 65536)
        and _hb_int(bounds.max_total_argument_bytes, 1, 4194304)
        and _hb_int(bounds.max_argument_nodes, 1, 4096)
        and _hb_int(bounds.max_argument_depth, 1, 32)
        and _hb_int(bounds.max_work_units, 1, 65536)
        and _hb_int(bounds.max_diagnostics, 1, 64)
    )


def graph_bounds_shape_ok(bounds: object) -> bool:
    """Closed scalar fence over the inherited graph bound set."""
    return (
        isinstance(bounds, GraphBounds)
        and _hb_int(bounds.max_requests, 1, 10_000)
        and _hb_int(bounds.max_documents, 1, 10_000)
        and _hb_int(bounds.max_single_source_bytes, 1, 10_000_000)
        and _hb_int(bounds.max_total_inspected_source_bytes, 1, 16_000_000)
        and _hb_int(bounds.max_reference_candidates_total, 1, 100_000)
        and _hb_int(bounds.max_reference_candidates_per_document, 1, 10_000)
        and _hb_int(bounds.max_nodes, 1, 10_000)
        and _hb_int(bounds.max_edges, 1, 100_000)
        and _hb_int(bounds.max_depth, 1, 10_000)
        and _hb_int(bounds.max_work_units, 1, 10_000_000)
        and _hb_int(bounds.max_diagnostics, 1, 10_000)
        and _hb_int(bounds.max_path_bytes, 1, 65_536)
    )


def proof_bounds_shape_ok(bounds: object) -> bool:
    """Closed scalar fence over the inherited proof bound set."""
    return (
        isinstance(bounds, BundleProofBounds)
        and _hb_int(bounds.max_bundles, 1, 10_000)
        and _hb_int(bounds.max_members, 1, 100_000)
        and _hb_int(bounds.max_segments, 1, 10_000)
        and _hb_int(bounds.max_marker, 2, 65_536)
        and _hb_int(bounds.max_marker_search, 1, 1_073_741_824)
        and _hb_int(bounds.max_diagnostics, 1, 10_000)
    )


def observation_bounds_shape_ok(bounds: object) -> bool:
    """Closed scalar fence over the inherited observation bound set."""
    return (
        isinstance(bounds, ObservationBounds)
        and _hb_int(bounds.max_items, 1, 100_000)
        and _hb_int(bounds.max_item_chars, 1, 10_000_000)
        and _hb_int(bounds.max_label_bytes, 1, 4096)
        and _hb_int(bounds.max_environment_chars, 1, 1_000_000)
        and _hb_int(bounds.max_commands, 1, 10_000)
        and _hb_int(bounds.max_command_chars, 1, 100_000)
        and _hb_int(bounds.max_operands, 1, 1024)
        and _hb_int(bounds.max_path_bytes, 1, 4096)
        and _hb_int(bounds.max_outputs, 1, 10_000)
        and _hb_int(bounds.max_output_chars, 1, 10_000_000)
        and _hb_int(bounds.max_wrapper_header_lines, 1, 64)
        and _hb_int(bounds.max_tools, 1, 10_000)
        and _hb_int(bounds.max_process_sessions, 1, 10_000)
        and _hb_int(bounds.max_process_polls, 1, 10_000)
        and _hb_int(bounds.max_process_pieces, 1, 10_000)
        and _hb_int(bounds.max_process_source_chars, 1, 10_000_000)
        and _hb_int(bounds.max_process_source_bytes, 1, 10_000_000)
        and _hb_int(bounds.max_process_immediate_execs, 1, 10_000)
    )


def admission_bounds_shape_ok(bounds: object) -> bool:
    """Closed scalar fence over the inherited admission bound set."""
    return (
        isinstance(bounds, BundleAdmissionBounds)
        and _hb_int(bounds.max_entries, 1, 128)
        and _hb_int(bounds.max_member_occurrences, 1, 1024)
        and _hb_int(bounds.max_reverse_associations, 1, 4096)
        and _hb_int(bounds.max_diagnostics, 1, 64)
    )


def root_lineage_ns_scalar_shape_ok(ns: object) -> bool:
    """Closed scalar fence over the ACTUAL namespace scalar fields
    (identity, workspace, mode, versions, opaque keys) BEFORE any
    wide revalidation dump can walk an unexpected container."""
    return (
        isinstance(ns, RootLineageNamespace)
        and _hb_str(ns.principal, 1, 256)
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


def _lineage_key(
    history_key: str,
    contract_version: str,
    policy_version: str,
    bounds: RootLineageBounds,
) -> str:
    """The H lineage scope key: the ACTUAL validated D
    ``history_key`` (itself recomputed from every actual D scope
    field) plus the NEW contract/policy versions and the NEW bound
    set.  Binding the actual values, never caller-supplied keys."""
    if not root_lineage_bounds_shape_ok(bounds):
        raise _fixed("the root-lineage bound set must carry actual scalar fields")
    payload = (
        history_key
        + "\0"
        + contract_version
        + "\0"
        + policy_version
        + "\0"
        + json.dumps(
            bounds.model_dump(mode="json", warnings=False),
            sort_keys=True,
            separators=(",", ":"),
        )
    )
    return _sha256_hex(payload.encode("utf-8"))


def _revalidate_root_lineage_bounds(bounds: RootLineageBounds) -> RootLineageBounds:
    if not root_lineage_bounds_shape_ok(bounds):
        raise _fixed("the root-lineage bound set must carry actual scalar fields")
    try:
        return RootLineageBounds.model_validate(bounds.model_dump(warnings=False))
    except Exception:
        raise _fixed("root lineage bounds failed the actual root-lineage validation") from None


class RootLineageNamespace(_GraphFrozen):
    """Explicit trusted INTERNAL root-lineage scope (018-h).

    The scope binds the ACTUAL accepted 018-d causal-history scope
    (its actual fields AND its actual ``history_key`` /
    ``state_scoped_key`` revalidated through the real accepted D
    validators -- the opaque keys alone are not enough) plus the NEW
    root-lineage contract/policy versions and the NEW root-lineage
    bounds.  ``lineage_key`` is recomputed from the actual D
    ``history_key`` and the NEW fields on every construction (factory
    and direct) and a mismatch is refused.

    Object construction is NOT authentication: this is an internal
    trusted boundary, never a public body/header authority path.  No
    anonymous fallback and no cross-scope reuse.  Errors and
    operational reprs suppress all private ID/source/marker/identity
    values.
    """

    principal: str = Field(min_length=1, max_length=256)
    session: str = Field(min_length=1, max_length=256)
    repository: str = Field(min_length=1, max_length=256)
    route: str = Field(min_length=1, max_length=64)
    model_identity: str = Field(min_length=1, max_length=256)
    config_fingerprint: str
    workspace: str
    mode: AdmissionMode
    admission_version: str = ADMISSION_CONTRACT_VERSION
    observation_version: str = OBSERVER_VERSION
    graph_version: str = GRAPH_CONTRACT_VERSION
    reference_version: str = REFERENCE_GRAMMAR
    proof_version: str = BUNDLE_PROOF_CONTRACT_VERSION
    bounds: BundleAdmissionBounds = Field(default_factory=BundleAdmissionBounds)
    proof_bounds: BundleProofBounds = Field(default_factory=BundleProofBounds)
    graph_bounds: GraphBounds = Field(default_factory=GraphBounds)
    observation_bounds: ObservationBounds = Field(default_factory=ObservationBounds)
    admission_namespace_key: str
    admission_scoped_key: str
    lineage_id: str = Field(min_length=1, max_length=128)
    history_version: str = CAUSAL_HISTORY_CONTRACT_VERSION
    arguments_version: str = CAUSAL_ARGUMENTS_JSON_VERSION
    history_bounds: HistoryBounds = Field(default_factory=HistoryBounds)
    history_key: str
    state_scoped_key: str
    contract_version: str = ROOT_LINEAGE_CONTRACT_VERSION
    policy_version: str = ROOT_LINEAGE_POLICY_VERSION
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
    def _v_scope(self) -> RootLineageNamespace:
        # Revalidate the ACTUAL accepted 018-d scope on EVERY
        # construction (factory and direct): the actual D field
        # constraints, the nested bound sets, the admission re-
        # validation and BOTH D 64-hex keys are rerun through the
        # real accepted D validators -- a forged nested model copy
        # carries no acquired authority and the opaque keys alone
        # are not enough.  The closed scalar fences over EVERY
        # nested bound set run BEFORE the nested model_dumps (K5:
        # an unexpected container in a scalar slot is refused
        # without a serializer traversal).
        if (
            not admission_bounds_shape_ok(self.bounds)
            or not proof_bounds_shape_ok(self.proof_bounds)
            or not graph_bounds_shape_ok(self.graph_bounds)
            or not observation_bounds_shape_ok(self.observation_bounds)
            or not history_bounds_shape_ok(self.history_bounds)
            or not root_lineage_bounds_shape_ok(self.root_lineage_bounds)
        ):
            raise _fixed("the nested root-lineage bound sets must carry actual scalar fields")
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
            _revalidate_root_lineage_bounds(self.root_lineage_bounds)
        except Exception:
            raise _fixed("lineage scope failed the actual accepted history validation") from None
        if self.lineage_key != _lineage_key(
            self.history_key,
            self.contract_version,
            self.policy_version,
            self.root_lineage_bounds,
        ):
            raise _fixed("lineage_key does not match the actual scope fields")
        return self

    def __repr__(self) -> str:  # noqa: D105 - privacy law
        return (
            f"RootLineageNamespace(principal={PRIVATE_ID_PLACEHOLDER}, "
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
            f"history_bounds={self.history_bounds!r}, "
            f"bounds={self.bounds!r}, "
            f"proof_bounds={self.proof_bounds!r}, "
            f"graph_bounds={self.graph_bounds!r}, "
            f"observation_bounds={self.observation_bounds!r}, "
            f"admission_namespace_key={self.admission_namespace_key!r}, "
            f"admission_scoped_key={self.admission_scoped_key!r}, "
            f"history_key={self.history_key!r}, "
            f"state_scoped_key={self.state_scoped_key!r}, "
            f"lineage_key={self.lineage_key!r})"
        )

    __str__ = __repr__


def make_root_lineage_namespace(
    admission: BundleAdmissionNamespace,
    lineage_id: str,
    *,
    bounds: RootLineageBounds | None = None,
    history_bounds: HistoryBounds | None = None,
) -> RootLineageNamespace:
    """Factory for a root-lineage scope over the ACTUAL accepted
    018-d causal-history scope.

    The ACTUAL admission namespace is bound through the accepted D
    factory (its actual fields AND both 64-hex keys recomputed); the
    NEW root-lineage versions and bounds are bound into the
    recomputed ``lineage_key``.  A forged, stale or borrowed key
    pair is refused.  Not authentication.
    """
    d_ns = make_causal_history_namespace(admission, lineage_id, bounds=history_bounds)
    effective_bounds = _revalidate_root_lineage_bounds(
        RootLineageBounds() if bounds is None else bounds
    )
    lineage_key = _lineage_key(
        d_ns.history_key,
        ROOT_LINEAGE_CONTRACT_VERSION,
        ROOT_LINEAGE_POLICY_VERSION,
        effective_bounds,
    )
    return RootLineageNamespace(
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

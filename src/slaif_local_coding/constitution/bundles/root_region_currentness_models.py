"""Versioned root-region currentness records (objective 018-q; INERT).

``ROOT_REGION_CURRENTNESS_CONTRACT_VERSION =
"cache-root-region-currentness/v1"``;
``ROOT_REGION_CURRENTNESS_POLICY_VERSION =
"root-region-currentness-policy/v1"``.

This module binds the pure root-CURRENTNESS derivation above the
accepted 018-p root-region producer: the immutable
``RootRegionCurrentnessBounds`` (ONE Q outer work ceiling plus the
own diagnostic ceiling, each default AND hard), the
``RootRegionUncertaintyWitness`` (a bounded immutable reference to a
qualifying complete root-bearing occurrence that P's root source-shape
policy does not mint into a supported governing fact) and the
``RootRegionCurrentnessResult`` (ready / root_currentness_unproven /
root_authority_conflict / typed refusal, retaining the EXACT input P
state by immutable reference on EVERY outcome).

The result carries the ACTUAL same-run P selection result by
reference -- ``None`` until the actual P selection has been computed
(early Q gates refuse without inventing a P result) and, once
computed, the actual P result is retained on EVERY later outcome
(including a Q work refusal after an actual P selection).  When the
actual P validation returns a reason BEFORE selection, the ACTUAL
reason is carried in ``p_validation_problem`` with ``p_selection``
still ``None`` (a P selection is never fabricated).  The P selection's
own fixed limitations stay with the P selection, separate and
unchanged; the result's ``diagnostics`` are the Q-OWN small fixed
closed-enum refusal diagnostics, bounded by the ACTUAL Q
``max_diagnostics`` (never a copy of the P vocabulary, never a global
minimum or an invented P error).

The uncertainty witness retains the ACTUAL retained
``CompletedReadOccurrence`` and its complete owning
``ResultFingerprintRecord`` by immutable reference (the original proof
is reached through the original occurrence, never copied or re-hashed
here); the charged derivation verifies state membership and owner
joins under the work ledger -- the constructor performs only closed
O(1) metadata joins, never an uncharged full proof walk.

The result's stable scope key recomputes from the ACTUAL P lineage
key, the Q contract/policy versions and the ACTUAL Q bounds on every
construction (factory and direct); a stale or forged key is refused.
The state revision is separate carried derivation identity, never a
clock and never part of the stable scope key.  No source copy, cache,
storage, RSS or token limit is introduced: the owned uncertainty
inventory is bounded by the ACTUAL inherited D ``max_occurrences``
(the frontier may additionally contain the one bootstrap witness;
metadata is never counted as logical root source bytes).

Object construction is NOT authentication: this is an internal
trusted boundary, never a public body/header authority path.  Errors
and operational reprs suppress all private ID/source/marker/identity
values.  The derivation itself lives in
``root_region_currentness.py``.
"""

from __future__ import annotations

import hashlib
from enum import StrEnum

from pydantic import Field, InstanceOf, field_validator, model_validator

from .bundle_proof_models import BundleProof
from .causal_history_models import (
    MAX_REVISION,
    CompletedReadOccurrence,
    ResultFingerprintRecord,
)
from .graph_models import _check_hex64, _fixed, _GraphFrozen
from .observation_models import PRIVATE_ID_PLACEHOLDER
from .root_lineage_models import RootLineageLimitation, RootSelectionOutcome
from .root_region_lineage_models import (
    RootRegionLineageState,
    RootRegionSelectionResult,
)

ROOT_REGION_CURRENTNESS_CONTRACT_VERSION = "cache-root-region-currentness/v1"
ROOT_REGION_CURRENTNESS_POLICY_VERSION = "root-region-currentness-policy/v1"

#: ONE Q outer per derivation (default AND hard ceiling).
_HARD_Q_WORK_UNITS = 1048576
#: TOTAL final closed-enum Q diagnostics per result (default AND hard).
_HARD_Q_DIAGNOSTICS = 64
#: Owned uncertainty inventory ceiling: the ACTUAL inherited D
#: max_occurrences hard bound (the one bootstrap witness is NOT an
#: uncertainty witness and never counts against this).
_HARD_Q_WITNESSES = 4096
#: Requested-member walk ceiling: the ACTUAL inherited D
#: max_retained_members hard bound (a root operand count never
#: exceeds the proof's retained member width).
_HARD_Q_ROOT_OPERANDS = 16384
#: Bounded call-ID metadata (the actual retained call-ID law).
_HARD_Q_CALL_ID = 256


def root_region_currentness_scope_key(
    lineage_key: str,
    contract_version: str,
    policy_version: str,
    bounds: RootRegionCurrentnessBounds,
) -> str:
    """The stable Q scope key recipe.

    Binds the ACTUAL P lineage key (which already binds the inherited
    identity/model/workspace/version/bound fields through the real
    P/D/C factories), the Q contract/policy versions and the ACTUAL Q
    bounds.  It does NOT bind the state revision (revision is separate
    carried derivation identity, never a clock or a scope input)."""
    payload = "\x00".join(
        (
            contract_version,
            policy_version,
            lineage_key,
            str(bounds.max_total_work_units),
            str(bounds.max_diagnostics),
        )
    ).encode("utf-8")
    return hashlib.sha256(b"cache-root-region-currentness/v1\x00" + payload).hexdigest()


class RootRegionCurrentnessBounds(_GraphFrozen):
    """NEW finite root-region currentness bounds (objective 018-q).

    ``max_total_work_units`` is the ONE Q outer per derivation covering
    the ENTIRE operation (early gates, the independent P-phase
    delegation reservation, evidence inventory, membership/ancestry,
    maxima/dominance, canonical sorting/dedup and result/model
    construction); the ACTUAL P phase keeps its OWN independent
    root-lineage work ceiling (the Q total is not a global minimum or
    reset budget).  ``max_diagnostics`` is the Q-OWN total final
    closed-enum diagnostic ceiling per result (the P selection's own
    limitations keep the ACTUAL P ceiling, separate and unchanged).
    Stricter positive values are permitted; ANY wider direct
    construction is refused."""

    #: ONE Q outer PER derivation work ledger.
    max_total_work_units: int = Field(default=_HARD_Q_WORK_UNITS, ge=1, le=_HARD_Q_WORK_UNITS)
    #: Q-OWN total final closed-enum diagnostics per result.
    max_diagnostics: int = Field(default=_HARD_Q_DIAGNOSTICS, ge=1, le=_HARD_Q_DIAGNOSTICS)

    def __repr__(self) -> str:  # noqa: D105 - privacy law
        return (
            "RootRegionCurrentnessBounds("
            f"max_total_work_units={self.max_total_work_units}, "
            f"max_diagnostics={self.max_diagnostics})"
        )

    __str__ = __repr__


def root_region_currentness_bounds_shape_ok(bounds: object) -> bool:
    """Closed actual-field fence: both fields are exact positive ints
    within the hard ceilings.  A dumped dict, a MALFORMED
    model_copy-mutated bound (a valid STRICTER model copy is legal) or
    a raw override dictionary fails this BEFORE any serializer visit."""
    return (
        isinstance(bounds, RootRegionCurrentnessBounds)
        and isinstance(bounds.max_total_work_units, int)
        and not isinstance(bounds.max_total_work_units, bool)
        and 1 <= bounds.max_total_work_units <= _HARD_Q_WORK_UNITS
        and isinstance(bounds.max_diagnostics, int)
        and not isinstance(bounds.max_diagnostics, bool)
        and 1 <= bounds.max_diagnostics <= _HARD_Q_DIAGNOSTICS
    )


class RootRegionUncertaintyClass(StrEnum):
    """Fixed closed classification of a qualifying root-bearing
    uncertainty occurrence (the order's evidence-table rows 2/3).

    ``OPAQUE_ROOT_BEARING_GROUP``: a complete root-bearing occurrence
    whose root member ownership/content is UNKNOWN (a boundaryless
    group, isolated or multi-member, with no proven root member
    digest).  Every unknown per-file hash stays unknown; the whole
    aggregate identity is not root identity.

    ``UNSUPPORTED_ROOT_SHAPE``: a complete root-bearing occurrence
    EXCLUDED by the P root source-shape policy (including repeated
    root operands).  Even where individual member bytes are proven the
    missing P authority fact is not minted and the known values are
    not called unknown: this is lack of a usable supported governing
    witness, distinct from unknown ownership."""

    OPAQUE_ROOT_BEARING_GROUP = "opaque_root_bearing_group"
    UNSUPPORTED_ROOT_SHAPE = "unsupported_root_shape"


class RootRegionCurrentnessDiagnostic(StrEnum):
    """Q-OWN small fixed closed-enum refusal diagnostics (018-q).

    These are the Q derivation's own typed refusal reasons, NOT a copy
    of the P diagnostic vocabulary: the actual P selection retains its
    original limitations by reference, and an actual P validation
    reason is carried separately in
    ``RootRegionCurrentnessResult.p_validation_problem``."""

    FOREIGN_SCOPE = "foreign_scope"
    VERSION_UNSUPPORTED = "version_unsupported"
    MALFORMED_BINDING = "malformed_binding"
    WORK_UNITS_OVER_BOUND = "work_units_over_bound"


class RootRegionCurrentnessOutcome(StrEnum):
    """Fixed closed Q outcomes.

    ``ready``: the P selection is OK and no unresolved maximal
    uncertainty witness remains (every qualifying uncertainty
    occurrence is strictly dominated by a genuinely later supported
    authoritative root witness).  ``root_currentness_unproven``: no
    usable selected source (an unresolved maximal uncertainty
    observation after or incomparable with the known root, or no
    authoritative root at all).  ``root_authority_conflict``: the P
    selection is a differing authoritative conflict (no usable
    selected source).  ``refused``: the fixed typed query failure
    (a Q-OWN early gate or work overflow, the actual P validation
    problem, or the actual P selection refusal) -- never relabelled as
    a root absence or an uncertainty result.  Every non-ready result
    forbids a ready graph/admission or bootstrap fallback."""

    READY = "ready"
    ROOT_CURRENTNESS_UNPROVEN = "root_currentness_unproven"
    ROOT_AUTHORITY_CONFLICT = "root_authority_conflict"
    REFUSED = "refused"


class RootRegionUncertaintyWitness(_GraphFrozen):
    """One bounded immutable uncertainty reference (018-q).

    Retains the ACTUAL retained ``CompletedReadOccurrence`` and the
    complete owning ``ResultFingerprintRecord`` by reference (the
    original proof is reached through the original occurrence -- never
    copied or re-hashed here); the charged derivation verifies state
    membership and the owner joins under the work ledger, while the
    constructor performs only closed O(1) metadata joins (no
    uncharged full proof walk).

    ``whole_proof_digest`` / ``whole_proof_byte_length`` duplicate the
    ORIGINAL proof aggregate binding for O(1) cross-checking (distinct
    from any root-member identity, which stays unknown for the opaque
    class).  ``root_operand_count`` is the ACTUAL count of normalized
    requested members equal to the effective root (one for the opaque
    class, two or more for the repeated-root unsupported shape)."""

    occurrence: InstanceOf[CompletedReadOccurrence]
    result_record: InstanceOf[ResultFingerprintRecord]
    occurrence_id: str
    call_id: str
    endpoint: str
    uncertainty_class: RootRegionUncertaintyClass
    whole_proof_digest: str
    whole_proof_byte_length: int = Field(ge=0)
    root_operand_count: int = Field(ge=1, le=_HARD_Q_ROOT_OPERANDS)

    @field_validator("occurrence_id", "whole_proof_digest")
    @classmethod
    def _v_hex64(cls, value: str, info: object) -> str:
        return _check_hex64(value, getattr(info, "field_name", "hex") or "hex")

    @field_validator("call_id")
    @classmethod
    def _v_call_id(cls, value: str) -> str:
        if not 1 <= len(value) <= _HARD_Q_CALL_ID or any(c.isspace() for c in value):
            raise _fixed("call_id must be bounded non-space metadata")
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

    @model_validator(mode="after")
    def _v_class(self) -> RootRegionUncertaintyWitness:
        if (
            self.uncertainty_class is RootRegionUncertaintyClass.UNSUPPORTED_ROOT_SHAPE
            and self.root_operand_count < 2
        ):
            raise _fixed("the unsupported root shape requires repeated root operands")
        if (
            self.uncertainty_class is RootRegionUncertaintyClass.OPAQUE_ROOT_BEARING_GROUP
            and self.root_operand_count != 1
        ):
            raise _fixed("the opaque root-bearing group carries exactly one root operand")
        return self

    @model_validator(mode="after")
    def _v_joins(self) -> RootRegionUncertaintyWitness:
        # Closed O(1) metadata joins against the ACTUAL retained
        # records (the charged derivation re-verifies state membership
        # and owner joins under the work ledger).
        occ = self.occurrence
        res = self.result_record
        if self.occurrence_id != occ.occurrence_id:
            raise _fixed("the witness occurrence ID must match the retained occurrence")
        if self.call_id != occ.call_id:
            raise _fixed("the witness call ID must match the retained occurrence")
        if self.endpoint != occ.endpoint:
            raise _fixed("the witness endpoint must match the retained occurrence")
        if occ.anchored is not True:
            raise _fixed("an uncertainty witness requires an anchored occurrence")
        if res.call_id != occ.call_id:
            raise _fixed("the owning result must match the retained occurrence call")
        if res.endpoint != occ.endpoint:
            raise _fixed("the owning result must match the retained occurrence endpoint")
        if res.complete is not True:
            raise _fixed("an uncertainty witness requires a complete owning result")
        proof = occ.proof
        if not isinstance(proof, BundleProof):
            raise _fixed("the retained occurrence must carry its actual original proof")
        if not isinstance(proof.source_digest, str):
            raise _fixed("the retained proof must carry its actual aggregate digest")
        if (
            not isinstance(proof.source_byte_length, int)
            or isinstance(proof.source_byte_length, bool)
            or proof.source_byte_length < 0
        ):
            raise _fixed("the retained proof must carry its actual aggregate byte length")
        if self.whole_proof_digest != proof.source_digest:
            raise _fixed("the whole proof digest must match the retained occurrence proof")
        if self.whole_proof_byte_length != proof.source_byte_length:
            raise _fixed("the whole proof byte length must match the retained occurrence proof")
        return self

    def __repr__(self) -> str:  # noqa: D105 - privacy law
        return (
            "RootRegionUncertaintyWitness(occurrence_id="
            f"{self.occurrence_id!r}, call_id={PRIVATE_ID_PLACEHOLDER}, "
            f"endpoint={self.endpoint!r}, "
            f"uncertainty_class={self.uncertainty_class!r}, "
            f"whole_proof_digest={self.whole_proof_digest!r}, "
            f"whole_proof_byte_length={self.whole_proof_byte_length}, "
            f"root_operand_count={self.root_operand_count}, "
            f"occurrence={PRIVATE_ID_PLACEHOLDER}, "
            f"result_record={PRIVATE_ID_PLACEHOLDER})"
        )

    __str__ = __repr__


class RootRegionCurrentnessResult(_GraphFrozen):
    """The bounded pure root-currentness derivation result (018-q).

    ``state`` is the EXACT input P state by immutable reference on
    EVERY outcome (no partial positive output, no revision advance);
    ``p_selection`` is the ACTUAL same-run P selection result by
    reference -- ``None`` until the actual P selection is computed and,
    once computed, retained on EVERY later outcome;
    ``p_validation_problem`` carries the ACTUAL P validation reason
    when P validation refused BEFORE selection (with ``p_selection``
    still ``None`` -- a P selection is never fabricated);
    ``usable_selected_source_digest`` is set ONLY on ``ready`` (an
    authority selection carried on a non-ready result MUST NOT be
    labelled usable); ``uncertainty_witnesses`` retains ALL qualifying
    uncertainty occurrences in canonical deterministic metadata order
    (dominated ones included, so no evidence is silently erased);
    ``diagnostics`` are the Q-OWN fixed closed-enum refusal
    diagnostics, bounded by the ACTUAL Q ``max_diagnostics``.  The P
    selection's own fixed limitations stay with the P selection
    (separate and unchanged).  ``revision`` / ``lineage_key`` carry
    the actual P state identity (validated, never trusted)."""

    outcome: RootRegionCurrentnessOutcome
    state: InstanceOf[RootRegionLineageState]
    p_selection: InstanceOf[RootRegionSelectionResult] | None = None
    p_validation_problem: RootLineageLimitation | None = None
    usable_selected_source_digest: str | None = None
    uncertainty_witnesses: tuple[InstanceOf[RootRegionUncertaintyWitness], ...] = Field(
        default=(), max_length=_HARD_Q_WITNESSES
    )
    diagnostics: tuple[RootRegionCurrentnessDiagnostic, ...] = Field(
        default=(), max_length=_HARD_Q_DIAGNOSTICS
    )
    contract_version: str = ROOT_REGION_CURRENTNESS_CONTRACT_VERSION
    policy_version: str = ROOT_REGION_CURRENTNESS_POLICY_VERSION
    bounds: RootRegionCurrentnessBounds = Field(default_factory=RootRegionCurrentnessBounds)
    lineage_key: str
    scope_key: str
    revision: int = Field(ge=0, le=MAX_REVISION)

    @field_validator("lineage_key", "scope_key")
    @classmethod
    def _v_keys(cls, value: str, info: object) -> str:
        return _check_hex64(value, getattr(info, "field_name", "key") or "key")

    @field_validator("usable_selected_source_digest")
    @classmethod
    def _v_usable(cls, value: str | None) -> str | None:
        if value is None:
            return value
        return _check_hex64(value, "usable_selected_source_digest")

    @field_validator("uncertainty_witnesses", mode="before")
    @classmethod
    def _v_witnesses_preflight(cls, value: object) -> object:
        if isinstance(value, (list, tuple)) and len(value) > _HARD_Q_WITNESSES:
            raise _fixed("uncertainty witnesses exceed the inherited ceiling")
        return value

    @field_validator("diagnostics", mode="before")
    @classmethod
    def _v_diagnostics_preflight(cls, value: object) -> object:
        # The hard ceiling is prefetched BEFORE any nested enum
        # validation, set or sort: an overbound collection is refused
        # without validating or sorting a single element.
        if isinstance(value, (list, tuple)) and len(value) > _HARD_Q_DIAGNOSTICS:
            raise _fixed("Q diagnostics exceed the hard ceiling")
        return value

    @field_validator("contract_version", "policy_version")
    @classmethod
    def _v_versions(cls, value: str, info: object) -> str:
        expected = (
            ROOT_REGION_CURRENTNESS_CONTRACT_VERSION
            if getattr(info, "field_name", "") == "contract_version"
            else ROOT_REGION_CURRENTNESS_POLICY_VERSION
        )
        if value != expected:
            raise _fixed("the Q contract/policy versions are the actual fixed tags")
        return value

    @model_validator(mode="before")
    @classmethod
    def _v_diagnostics_cap_preflight(cls, value: object) -> object:
        # FAILFAST BEFORE any diagnostics enum/set/sort visit: a
        # provided bound that is not an actual closed valid
        # RootRegionCurrentnessBounds fails the fixed private
        # validation error first (a missing bound is the honest
        # default; a valid stricter copy is legal), and only then is
        # the ACTUAL stricter Q diagnostic cap an O(1) count gate
        # (the hard ceiling alone is insufficient): an overbound
        # collection is refused without validating a single element.
        if isinstance(value, dict):
            bounds = value.get("bounds")
            if bounds is not None and not root_region_currentness_bounds_shape_ok(bounds):
                raise _fixed("the Q bounds must carry actual scalar fields")
            diags = value.get("diagnostics")
            if (
                isinstance(diags, (list, tuple))
                and isinstance(bounds, RootRegionCurrentnessBounds)
                and len(diags) > bounds.max_diagnostics
            ):
                raise _fixed("Q diagnostics exceed the actual Q bounds")
        return value

    @model_validator(mode="after")
    def _v_result(self) -> RootRegionCurrentnessResult:
        if not root_region_currentness_bounds_shape_ok(self.bounds):
            raise _fixed("the Q bounds must carry actual scalar fields")
        if self.lineage_key != self.state.lineage_key:
            raise _fixed("the result lineage key must equal the actual state key")
        if self.revision != self.state.revision:
            raise _fixed("the result revision must equal the carried state revision")
        if self.scope_key != root_region_currentness_scope_key(
            self.lineage_key,
            self.contract_version,
            self.policy_version,
            self.bounds,
        ):
            raise _fixed("scope_key does not match the actual result scope fields")
        if tuple(sorted(set(self.diagnostics))) != self.diagnostics:
            raise _fixed("Q diagnostics must be sorted and deduplicated")
        if len(self.diagnostics) > self.bounds.max_diagnostics:
            raise _fixed("Q diagnostics exceed the actual Q bounds")
        witness_keys = tuple(
            (w.uncertainty_class.value, w.occurrence_id) for w in self.uncertainty_witnesses
        )
        if tuple(sorted(witness_keys)) != witness_keys or len(set(witness_keys)) != len(
            witness_keys
        ):
            raise _fixed("uncertainty witnesses must be canonical ordered and deduplicated")
        if self.p_selection is not None:
            p_sel = self.p_selection
            if p_sel.lineage_key != self.state.lineage_key:
                raise _fixed("the P selection key must equal the carried state key")
            if p_sel.revision != self.state.revision:
                raise _fixed("the P selection revision must equal the carried state revision")
        if self.p_validation_problem is not None and self.p_selection is not None:
            raise _fixed("a P validation problem precedes selection and carries no P selection")
        p_outcome = self.p_selection.outcome if self.p_selection is not None else None
        if self.outcome is RootRegionCurrentnessOutcome.READY:
            if (
                self.p_selection is None
                or p_outcome is not RootSelectionOutcome.OK
                or self.usable_selected_source_digest is None
                or self.usable_selected_source_digest != self.p_selection.selected_source_digest
            ):
                raise _fixed("ready requires the actual OK P selection and its selected source")
            if self.diagnostics or self.p_validation_problem is not None:
                raise _fixed("ready carries no refusal diagnostics")
        else:
            if self.usable_selected_source_digest is not None:
                raise _fixed("only ready carries a usable selected source")
            if self.outcome in (
                RootRegionCurrentnessOutcome.ROOT_CURRENTNESS_UNPROVEN,
                RootRegionCurrentnessOutcome.ROOT_AUTHORITY_CONFLICT,
            ) and (self.diagnostics or self.p_validation_problem is not None):
                raise _fixed("a positive-interpretation outcome carries no refusal diagnostics")
            if self.outcome is RootRegionCurrentnessOutcome.REFUSED:
                if self.p_selection is None:
                    if bool(self.diagnostics) == (self.p_validation_problem is not None):
                        raise _fixed(
                            "a Q refusal before P selection carries exactly one "
                            "typed reason channel"
                        )
                else:
                    if self.p_validation_problem is not None:
                        raise _fixed(
                            "a Q refusal after P selection carries no P validation problem"
                        )
                    if p_outcome is RootSelectionOutcome.REFUSED and self.diagnostics:
                        raise _fixed("a mapped P selection refusal adds no Q diagnostics")
                    if p_outcome is not RootSelectionOutcome.REFUSED and not self.diagnostics:
                        raise _fixed(
                            "a Q refusal after a non-refused P selection "
                            "exposes its own typed diagnostics"
                        )
            elif self.outcome is RootRegionCurrentnessOutcome.ROOT_AUTHORITY_CONFLICT:
                if p_outcome is not RootSelectionOutcome.ROOT_CONTENT_CONFLICT:
                    raise _fixed("the conflict outcome carries the actual P conflict selection")
            elif (
                self.outcome is RootRegionCurrentnessOutcome.ROOT_CURRENTNESS_UNPROVEN
                and p_outcome
                not in (RootSelectionOutcome.OK, RootSelectionOutcome.NO_SELECTED_ROOT)
            ):
                raise _fixed("the unproven outcome carries an OK or no-root P selection")
        return self

    def __repr__(self) -> str:  # noqa: D105 - privacy law
        p_outcome = self.p_selection.outcome.value if self.p_selection is not None else None
        p_problem = (
            self.p_validation_problem.value if self.p_validation_problem is not None else None
        )
        return (
            "RootRegionCurrentnessResult(outcome="
            f"{self.outcome.value!r}, lineage_key={self.lineage_key!r}, "
            f"scope_key={self.scope_key!r}, revision={self.revision}, "
            f"usable_selected_source_digest="
            f"{self.usable_selected_source_digest!r}, "
            f"uncertainty_witnesses={len(self.uncertainty_witnesses)}, "
            f"diagnostics={list(self.diagnostics)}, "
            f"p_validation_problem={p_problem!r}, "
            f"p_selection_outcome={p_outcome!r})"
        )

    __str__ = __repr__

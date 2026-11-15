"""Pure versioned complete root-region admission consumer result
models (objective 018-t).

This module is the THIRD carrying boundary of the region-compatible
admission consumer: the ``RootRegionAdmissionResult`` data model
carries the EXACT input P state and namespace, the ACTUAL same-run
018-r result by immutable reference (once returned), and the ACTUAL
S admission parent by immutable reference (only on a READY
outcome), together with the NEW versioned consumer bounds, the
closed consumer outcome/diagnostic enums, the stable consumer scope
key and the honest same-run work counters of the actual ledgers.

The result model is a carrying boundary, not a tag wrapper: its
model validator re-runs the ACTUAL local carrying law at the third
parent (the complete S admission-parent law through the actual
``RootRegionAdmission`` re-validation, including the leaf law, the
reverse-index law and the R-result law joins), re-derives the stable
consumer scope key from the actual carried fields, and enforces the
exact input-identity joins (state / namespace / R result /
admission parent / G bounds).  A partial or bypass-copied nested
record, a detached original, a coherent wrong tag or a later
genuine splice refuses with fixed private errors before any unsafe
attribute access, traversal or serialization.

The module is INERT: it wires no runtime, exposes no operation and
claims no admission/compiled-cache/HTTP readiness.  Object
construction is not authentication; the same-run consumer operation
(``root_region_admission``) derives ACTUAL R from ACTUAL P in its
own entire charged operation and supplies the actual carried
records.  All existing C/G/H/O/I/P/Q/R/S public signatures,
defaults, schemas, version tags, recipe bytes and behavior remain
intact.
"""

from __future__ import annotations

import json
from enum import StrEnum
from typing import Any, TypeGuard

from pydantic import Field, InstanceOf, field_validator, model_validator

from .causal_history_models import MAX_REVISION
from .current_admission_models import (
    CURRENT_ADMISSION_CONTRACT_VERSION,
    CURRENT_ADMISSION_POLICY_VERSION,
    CurrentAdmissionBounds,
    CurrentAdmissionLimitation,
    _check_hex64,
    _check_text,
    _sha256_hex,
)
from .current_graph_models import CurrentGraphResult
from .currentness_models import CurrentnessOverlay
from .graph_models import _fixed, _GraphFrozen
from .root_region_admission_models import (
    _S_NS_FIELDS,
    _S_PARENT_FIELDS,
    _S_STATE_FIELDS,
    RootRegionAdmission,
    _s_all_eleven_bound_sets_closed,
    _s_g_bounds_closed,
    _s_six_ns_bound_sets_closed,
)
from .root_region_currentness_models import RootRegionCurrentnessResult
from .root_region_graph_models import (
    _HARD_R_DIAGNOSTICS,
    _R_RESULT_FIELDS,
    ResolvedRootRegionSource,
    RootRegionGraphDiagnostic,
    RootRegionGraphOutcome,
    RootRegionGraphResult,
    _r_fields_present,
    _r_result_carried_closed,
    root_region_graph_bounds_shape_ok,
)
from .root_region_lineage_models import (
    RootRegionLineageNamespace,
    RootRegionLineageState,
)

ROOT_REGION_ADMISSION_CONTRACT_VERSION = "cache-root-region-admission/v1"
ROOT_REGION_ADMISSION_POLICY_VERSION = "root-region-admission-policy/v1"

#: The NEW entire-consumer work domain (default AND hard; a NEW
#: versioned work domain, never a raised old cap and never a
#: source-size reinterpretation).
_HARD_T_WORK_UNITS = 8388608
#: The NEW consumer-own diagnostics ceiling (default AND hard).
_HARD_T_DIAGNOSTICS = 64

#: Fixed private scope-key placeholder for the R / S-model scope
#: keys in results where the actual R result (and therefore the
#: S admission parent) was never RETURNED (an early T fence or a
#: T-level crossing before the R return): honest absence, never a
#: fabricated key and never a default-domain substitution.
_T_R_SCOPE_ABSENT = "absent"
_T_MODEL_SCOPE_ABSENT = "absent"


def _t_int_in(value: object, lo: int, hi: int) -> TypeGuard[int]:
    """Closed non-bool int range fence (BEFORE any serializer
    visit, mirroring the accepted R bound-fence law)."""
    return isinstance(value, int) and not isinstance(value, bool) and lo <= value <= hi


class RootRegionAdmissionBounds(_GraphFrozen):
    """NEW finite entire-consumer bounds (objective 018-t).

    ``max_total_work_units`` is the ONE entire-consumer outer work
    ledger (default AND hard; stricter positive values legal, any
    wider construction refused).  It covers the ENTIRE consumer
    operation: the early T gates/scope/bound/construction work,
    EVERY actual R unit (Q/P/D/B/source/F/E included, coupled
    unit-for-unit through the private R-core seam), the ACTUAL
    G-subtree work -- the F units shared with the R derivation,
    which charge the entire outer exactly ONCE through the R
    coupling, and the admission/root/FILE/association/S-parent
    work of that same G ledger -- plus the full-result parent and
    its rechecks.  The G subtree ledger stays a distinct domain
    with its OWN ceiling running on those same units, and the
    entire outer never double-charges a shared unit.  It is NOT a
    RAM/RSS/token budget, a raised old cap or a reinterpretation
    of a source-size setting.  ``max_diagnostics`` is the
    consumer-OWN closed-enum diagnostics ceiling per result (the
    nested R/G evidence keeps its ACTUAL own ceilings, separate
    and unchanged)."""

    #: ONE entire-consumer outer PER operation work ledger.
    max_total_work_units: int = Field(default=_HARD_T_WORK_UNITS, ge=1, le=_HARD_T_WORK_UNITS)
    #: Consumer-OWN closed-enum diagnostics per result.
    max_diagnostics: int = Field(default=_HARD_T_DIAGNOSTICS, ge=1, le=_HARD_T_DIAGNOSTICS)

    def __repr__(self) -> str:  # noqa: D105 - privacy law
        return (
            "RootRegionAdmissionBounds("
            f"max_total_work_units={self.max_total_work_units}, "
            f"max_diagnostics={self.max_diagnostics})"
        )

    __str__ = __repr__


def root_region_admission_bounds_shape_ok(bounds: object) -> bool:
    """T-PRIVATE closed fence over the NEW consumer bound set (the
    consumer's own preflight boundary): class, field existence,
    exact non-bool ints, NEW hard ceilings, BEFORE any serializer
    visit."""
    return (
        type(bounds) is RootRegionAdmissionBounds
        and hasattr(bounds, "max_total_work_units")
        and hasattr(bounds, "max_diagnostics")
        and _t_int_in(bounds.max_total_work_units, 1, _HARD_T_WORK_UNITS)
        and _t_int_in(bounds.max_diagnostics, 1, _HARD_T_DIAGNOSTICS)
    )


class RootRegionAdmissionDiagnostic(StrEnum):
    """Consumer-OWN small fixed closed-enum refusal diagnostics
    (018-t).

    These are the CONSUMER derivation's own typed refusal reasons.
    The first five names are the 1:1 value-mapped mirrors of the
    ACTUAL R-OWN diagnostics (same strings, distinct enum -- the
    accepted G mapping law over the R vocabulary): a mapped R
    refusal carries the ACTUAL R result by reference, which keeps
    the precise R-level channel, and the consumer mirror names the
    consumer-level refusal domain.  ``admission_over_bound`` is
    the ACTUAL G-subtree/admission-domain crossing (every G-kernel
    overflow maps to it), and ``admission_state_malformed`` is the
    G-kernel closed state-malformed refusal.  The ACTUAL bounded
    G refusal reason is retained on the result in the INHERITED
    G channel (``RootRegionAdmissionResult.g_limitation``, the
    closed ``CurrentAdmissionLimitation`` vocabulary) on every
    G-domain refusal -- the inherited G channel stays DISTINCT
    from this consumer-OWN enum and separately bounded.  A
    mapped Q unproven / authority-conflict outcome carries NO
    consumer diagnostic (the actual Q result keeps the Q
    reasons)."""

    FOREIGN_SCOPE = "foreign_scope"
    VERSION_UNSUPPORTED = "version_unsupported"
    MALFORMED_BINDING = "malformed_binding"
    WORK_UNITS_OVER_BOUND = "work_units_over_bound"
    SOURCE_RESOLUTION_FAILED = "source_resolution_failed"
    ADMISSION_OVER_BOUND = "admission_over_bound"
    ADMISSION_STATE_MALFORMED = "admission_state_malformed"


#: Exact 1:1 value mapping from the ACTUAL R-OWN closed diagnostic
#: names to the consumer-mirror names (same strings, distinct enum).
_R_DIAGNOSTIC_MAP = {
    "foreign_scope": RootRegionAdmissionDiagnostic.FOREIGN_SCOPE,
    "version_unsupported": RootRegionAdmissionDiagnostic.VERSION_UNSUPPORTED,
    "malformed_binding": RootRegionAdmissionDiagnostic.MALFORMED_BINDING,
    "work_units_over_bound": RootRegionAdmissionDiagnostic.WORK_UNITS_OVER_BOUND,
    "source_resolution_failed": RootRegionAdmissionDiagnostic.SOURCE_RESOLUTION_FAILED,
}


class RootRegionAdmissionOutcome(StrEnum):
    """Fixed closed consumer outcomes.

    ``ready``: ONLY the actual same-run R READY, the completed
    actual admission (the S admission parent) AND the full-result
    third-parent checks all hold -- it does NOT mean acquired
    required dependencies, compiled content, cache readiness, HTTP
    readiness or v1 runtime readiness.
    ``root_currentness_unproven`` / ``root_authority_conflict``:
    the ACTUAL same-run R positive-interpretation outcomes mapped
    from the actual Q channel (no usable selected source, no
    admission, no bootstrap fallback; the ACTUAL R result is
    retained).  ``refused``: the fixed typed consumer failure (an
    early T gate, a T-level work crossing -- including a T-OWN
    entire-consumer work crossing AFTER the actual R return, which
    retains the actual R result as bounded evidence -- a mapped R
    refusal or an actual G-subtree/admission-domain refusal) --
    never relabelled as a success and never carrying a usable
    admission.  Every non-ready outcome publishes NO usable
    admission or bootstrap fallback."""

    READY = "ready"
    ROOT_CURRENTNESS_UNPROVEN = "root_currentness_unproven"
    ROOT_AUTHORITY_CONFLICT = "root_authority_conflict"
    REFUSED = "refused"


def _t_scope_key_hex_or_absent(value: str, name: str) -> str:
    """Closed fence for a scope-key payload element: either the
    ACTUAL 64-hex key or the fixed private absence placeholder
    (honest absence, never a fabricated default)."""
    if value == _T_R_SCOPE_ABSENT:
        return value
    return _check_hex64(value, name)


def root_region_admission_scope_key(
    p_lineage_key: str,
    contract_version: str,
    policy_version: str,
    r_scope_key: str,
    model_scope_key: str,
    g_contract_version: str,
    g_policy_version: str,
    bounds: RootRegionAdmissionBounds,
    g_bounds: CurrentAdmissionBounds,
) -> str:
    """The STABLE consumer configuration scope identity.

    Binds the ACTUAL validated P lineage identity (the P
    ``lineage_key``, which does NOT contain the carried revision),
    the NEW consumer contract/policy versions, the ACTUAL re-
    derived R scope key (which itself binds the actual P lineage
    key, the R/Q/F/E contract/policy versions, the actual graph
    version and every effective R/Q/F/E bound), the ACTUAL S-model
    scope key (which binds the S model versions and the ACTUAL G
    contract/policy versions and bounds), the ACTUAL G
    contract/policy versions, and EVERY effective NEW bound set
    (the consumer bounds and the ACTUAL G bounds as closed inner
    dumps).  The carried revision, the selected root digest and
    the actual F/E graph snapshot scopes join SEPARATELY (the
    revision/selected source/graph snapshot joins are never clocks
    and never part of this stable configuration identity, and
    never semantic C key ingredients).  Where the actual R result
    (or therefore the S admission parent) was never returned, the
    fixed private absence placeholder is bound instead -- honest
    absence, never a fabricated or default-domain key."""
    # The closed O(1) preflight runs BEFORE any serialization walk.
    if not isinstance(p_lineage_key, str):
        raise _fixed("the consumer scope key P lineage input must carry closed 64-hex text")
    _check_hex64(p_lineage_key, "p_lineage_key")
    if not isinstance(r_scope_key, str):
        raise _fixed("the consumer scope key R scope input must carry closed text")
    _t_scope_key_hex_or_absent(r_scope_key, "r_scope_key")
    if not isinstance(model_scope_key, str):
        raise _fixed("the consumer scope key model scope input must carry closed text")
    _t_scope_key_hex_or_absent(model_scope_key, "model_scope_key")
    for name, value in (
        ("contract_version", contract_version),
        ("policy_version", policy_version),
        ("g_contract_version", g_contract_version),
        ("g_policy_version", g_policy_version),
    ):
        if not isinstance(value, str):
            raise _fixed("the consumer scope key version inputs must carry closed text")
        _check_text(value, name, 128)
    if not root_region_admission_bounds_shape_ok(bounds):
        raise _fixed("the consumer bounds must be closed under the original class and ranges")
    if not _s_g_bounds_closed(g_bounds):
        raise _fixed("the G admission bounds must be closed under the original class and ranges")
    payload = [
        p_lineage_key,
        contract_version,
        policy_version,
        r_scope_key,
        model_scope_key,
        g_contract_version,
        g_policy_version,
        json.dumps(bounds.model_dump(mode="json"), sort_keys=True, separators=(",", ":")),
        json.dumps(g_bounds.model_dump(mode="json"), sort_keys=True, separators=(",", ":")),
    ]
    return _sha256_hex(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8"))


_T_RESULT_FIELDS = (
    "outcome",
    "state",
    "ns",
    "r_result",
    "admission",
    "diagnostics",
    "contract_version",
    "policy_version",
    "g_contract_version",
    "g_policy_version",
    "bounds",
    "g_bounds",
    "g_limitation",
    "lineage_key",
    "scope_key",
    "revision",
    "work_units",
    "r_work_units",
    "g_work_units",
    "stage_work_units",
    "entry_source_bytes",
)


def _t_r_result_closed(r_result: RootRegionGraphResult) -> None:
    """The closed field-existence and closed-variant class fence
    over the carried R result, run at the THIRD carrying parent
    BEFORE any T-level dereference (a partial, bypass-copied or
    foreign R record is a fixed typed boundary error, never an
    AttributeError).  It closes exactly what this boundary itself
    reads: the closed outcome / diagnostics / revision scalars,
    the closed nested-evidence and resolved-source classes, the
    closed R bounds and the closed key texts.  The COMPLETE R
    result law (scope-key recomputation, the nested Q/P-selection
    / F / E joins and the resolved-source content pass) is re-run
    at the S admission-parent boundary on the READY path; the
    fence here runs on EVERY path that carries an R result,
    including the mapped non-READY outcomes.
    """
    if not isinstance(r_result, RootRegionGraphResult) or not _r_fields_present(
        r_result, _R_RESULT_FIELDS
    ):
        raise _fixed("the carried R result must carry its closed fields")
    if not isinstance(r_result.outcome, RootRegionGraphOutcome):
        raise _fixed("the carried R result outcome must carry the closed outcome class")
    if not isinstance(r_result.state, RootRegionLineageState):
        raise _fixed("the carried R result state must carry the closed state class")
    if r_result.q_result is not None and not isinstance(
        r_result.q_result, RootRegionCurrentnessResult
    ):
        raise _fixed("the carried R q evidence must carry the closed q class")
    if r_result.f_result is not None and not isinstance(r_result.f_result, CurrentGraphResult):
        raise _fixed("the carried R f evidence must carry the closed f class")
    if r_result.e_overlay is not None and not isinstance(r_result.e_overlay, CurrentnessOverlay):
        raise _fixed("the carried R e evidence must carry the closed e class")
    if r_result.resolved_source is not None and not isinstance(
        r_result.resolved_source, ResolvedRootRegionSource
    ):
        raise _fixed("the carried R resolved source must carry the closed source class")
    if not isinstance(r_result.diagnostics, tuple):
        raise _fixed("the carried R diagnostics must carry the closed diagnostic class")
    if len(r_result.diagnostics) > _HARD_R_DIAGNOSTICS:
        raise _fixed("the carried R diagnostics exceed the closed diagnostic ceiling")
    if not all(isinstance(d, RootRegionGraphDiagnostic) for d in r_result.diagnostics):
        raise _fixed("the carried R diagnostics must carry the closed diagnostic class")
    if not _t_int_in(r_result.revision, 0, MAX_REVISION):
        raise _fixed("the carried R revision must carry a closed non-bool revision")
    if not (
        isinstance(r_result.lineage_key, str)
        and isinstance(r_result.scope_key, str)
        and isinstance(r_result.graph_version, str)
    ):
        raise _fixed("the carried R key texts must carry closed text")
    if not root_region_graph_bounds_shape_ok(r_result.bounds):
        raise _fixed("the carried R bounds must be closed under the original class and ranges")


class RootRegionAdmissionResult(_GraphFrozen):
    """The complete region-compatible admission consumer result --
    the THIRD carrying boundary (018-t).

    ``state`` / ``ns`` are the EXACT input P state and namespace by
    immutable reference on EVERY outcome (no partial positive
    output, no revision advance).  ``r_result`` is the ACTUAL
    same-run 018-r result by reference -- present on every outcome
    EXCEPT the early T fences and a T-level crossing before the R
    return (where no R result was ever returned and nothing is
    fabricated); once returned it is retained on EVERY later
    outcome, including a mapped G-domain refusal.  ``admission`` is
    the ACTUAL S admission parent by reference and present ONLY on
    a READY outcome (every refusal exposes no usable admission or
    bootstrap fallback).  ``diagnostics`` are the consumer-OWN
    fixed closed-enum refusal diagnostics (a mapped R refusal
    carries the 1:1 mirror; the actual R evidence keeps the
    precise R channel); a mapped Q unproven / authority-conflict
    carries none.  ``g_limitation`` carries the ACTUAL inherited
    G refusal limitation (the closed
    ``CurrentAdmissionLimitation`` vocabulary) on an actual
    G-domain refusal only -- the inherited G channel stays
    distinct from the consumer-OWN enum and separately bounded;
    every other path carries None.  ``revision`` / ``lineage_key``
    carry the actual P state identity (validated, never
    trusted).  ``work_units`` /
    ``r_work_units`` / ``g_work_units`` / ``stage_work_units`` /
    ``entry_source_bytes`` are the honest same-run counters of the
    ACTUAL ledgers of this operation (the entire T outer, the R
    total, the G subtree, the G admission stage and the cumulative
    owned entry-source bytes): closed O(1) range fences, never
    authenticated re-measurements and never a throughput/RSS/token
    claim.

    At this carrying boundary the ACTUAL local law is re-run, not
    tag equality: the complete S admission-parent law (leaf law,
    canonical rekey, reverse-index law, counter law, S scope key)
    through the actual ``RootRegionAdmission`` re-validation, the
    exact input-identity joins (state to ``r_result.state``, the
    admission parent's state / ns / r_result / g_bounds by
    identity), the closed outcome invariants, the counter fences
    under the ACTUAL effective bound sets, and the stable consumer
    scope key RECOMPUTED from the actual carried fields (a stale
    or forged key refuses, never retained)."""

    outcome: RootRegionAdmissionOutcome
    state: InstanceOf[RootRegionLineageState]
    ns: InstanceOf[RootRegionLineageNamespace]
    r_result: InstanceOf[RootRegionGraphResult] | None = None
    admission: InstanceOf[RootRegionAdmission] | None = None
    diagnostics: tuple[RootRegionAdmissionDiagnostic, ...] = Field(
        default=(), max_length=_HARD_T_DIAGNOSTICS
    )
    contract_version: str = ROOT_REGION_ADMISSION_CONTRACT_VERSION
    policy_version: str = ROOT_REGION_ADMISSION_POLICY_VERSION
    g_contract_version: str = CURRENT_ADMISSION_CONTRACT_VERSION
    g_policy_version: str = CURRENT_ADMISSION_POLICY_VERSION
    bounds: RootRegionAdmissionBounds = Field(default_factory=RootRegionAdmissionBounds)
    g_bounds: InstanceOf[CurrentAdmissionBounds]
    #: The ACTUAL inherited G-channel refusal limitation (the
    #: closed ``CurrentAdmissionLimitation`` vocabulary): present
    #: ONLY on an actual G-domain refusal (the F-phase crossing
    #: before the R return, or the admission-domain crossing
    #: after it); every other path carries None.
    g_limitation: InstanceOf[CurrentAdmissionLimitation] | None = None
    lineage_key: str
    scope_key: str
    revision: int = Field(ge=0, le=MAX_REVISION)
    work_units: int = Field(ge=0)
    r_work_units: int = Field(ge=0)
    g_work_units: int = Field(ge=0)
    stage_work_units: int = Field(ge=0)
    entry_source_bytes: int = Field(ge=0)

    @field_validator("lineage_key", "scope_key")
    @classmethod
    def _v_keys(cls, value: str, info: Any) -> str:
        return _check_hex64(value, getattr(info, "field_name", "key") or "key")

    @field_validator("contract_version", "policy_version")
    @classmethod
    def _v_t_versions(cls, value: str, info: Any) -> str:
        field_name = getattr(info, "field_name", "version") or "version"
        expected = (
            ROOT_REGION_ADMISSION_CONTRACT_VERSION
            if field_name == "contract_version"
            else ROOT_REGION_ADMISSION_POLICY_VERSION
        )
        if value != expected:
            raise _fixed("the consumer contract/policy versions are the actual fixed tags")
        return value

    @field_validator("g_contract_version", "g_policy_version")
    @classmethod
    def _v_g_versions(cls, value: str, info: Any) -> str:
        field_name = getattr(info, "field_name", "version") or "version"
        expected = (
            CURRENT_ADMISSION_CONTRACT_VERSION
            if field_name == "g_contract_version"
            else CURRENT_ADMISSION_POLICY_VERSION
        )
        if value != expected:
            raise _fixed("the carried G contract/policy versions are the actual fixed tags")
        return value

    @model_validator(mode="after")
    def _v_result(self) -> RootRegionAdmissionResult:
        # Phase 0: closed field-existence, closed-variant class
        # and closed non-bool scalar fences BEFORE any
        # dereference (a partial, bypass-copied or foreign record
        # is a fixed typed boundary error, never an attribute or
        # type error); the NEW consumer version tags and the
        # closed bound sets close at the same boundary (at the
        # carrying boundary the field validators do not rerun, so
        # the actual fixed supported identities are re-checked
        # here and a coherently recomputed scope key never
        # re-supports a changed tag).  The carried state /
        # namespace / R result / admission parent close with
        # THEIR closed field fences at the same boundary, before
        # the phase-1 outcome invariants and the phase-2/3/4
        # joins read them; this runs on EVERY outcome, including
        # the mapped non-READY paths.
        if not _r_fields_present(self, _T_RESULT_FIELDS):
            raise _fixed("the consumer result must carry its closed fields")
        if not isinstance(self.outcome, RootRegionAdmissionOutcome):
            raise _fixed("the consumer outcome must carry the closed outcome class")
        if not isinstance(self.diagnostics, tuple):
            raise _fixed("the consumer diagnostics must carry the closed diagnostic class")
        if len(self.diagnostics) > _HARD_T_DIAGNOSTICS:
            raise _fixed("the consumer diagnostics exceed the closed diagnostic ceiling")
        if not all(isinstance(d, RootRegionAdmissionDiagnostic) for d in self.diagnostics):
            raise _fixed("the consumer diagnostics must carry the closed diagnostic class")
        if not _t_int_in(self.revision, 0, MAX_REVISION):
            raise _fixed("the consumer revision must carry a closed non-bool revision")
        for counter in (
            self.work_units,
            self.r_work_units,
            self.g_work_units,
            self.stage_work_units,
            self.entry_source_bytes,
        ):
            if not (type(counter) is int and counter >= 0):
                raise _fixed("the consumer work counters must carry closed non-bool counts")
        for tag, expected in (
            ("contract_version", ROOT_REGION_ADMISSION_CONTRACT_VERSION),
            ("policy_version", ROOT_REGION_ADMISSION_POLICY_VERSION),
        ):
            value = getattr(self, tag)
            if not isinstance(value, str) or value != expected:
                raise _fixed("the consumer contract/policy versions are the actual fixed tags")
        for tag, expected in (
            ("g_contract_version", CURRENT_ADMISSION_CONTRACT_VERSION),
            ("g_policy_version", CURRENT_ADMISSION_POLICY_VERSION),
        ):
            value = getattr(self, tag)
            if not isinstance(value, str) or value != expected:
                raise _fixed("the carried G contract/policy versions are the actual fixed tags")
        if not root_region_admission_bounds_shape_ok(self.bounds):
            raise _fixed("the consumer bounds must be closed under the original class and ranges")
        if not _s_g_bounds_closed(self.g_bounds):
            raise _fixed(
                "the carried G admission bounds must be closed under the original class and ranges"
            )
        if self.g_limitation is not None and not isinstance(
            self.g_limitation, CurrentAdmissionLimitation
        ):
            raise _fixed("the carried G limitation must carry the closed G vocabulary")
        state = self.state
        if not isinstance(state, RootRegionLineageState) or not _r_fields_present(
            state, _S_STATE_FIELDS
        ):
            raise _fixed("the consumer result state must carry its closed fields")
        ns = self.ns
        if not isinstance(ns, RootRegionLineageNamespace) or not _r_fields_present(
            ns, _S_NS_FIELDS
        ):
            raise _fixed("the consumer result namespace must carry its closed fields")
        if self.r_result is not None:
            _t_r_result_closed(self.r_result)
        if self.admission is not None and not (
            isinstance(self.admission, RootRegionAdmission)
            and _r_fields_present(self.admission, _S_PARENT_FIELDS)
        ):
            raise _fixed("the carried admission parent must carry its closed fields")
        # Phase 1: closed outcome invariants.  READY requires the
        # actual R READY AND the completed actual admission AND
        # this full-result check; every mapped R non-ready outcome
        # retains the ACTUAL R result and exposes no admission; a
        # refusal exposes no usable admission or bootstrap
        # fallback.  A mapped Q unproven / authority-conflict
        # carries NO consumer diagnostic (the actual Q channel
        # keeps the reasons).
        r_result = self.r_result
        admission = self.admission
        # The inherited G refusal channel is closed to EVERY
        # outcome except REFUSED (an actual G-domain refusal is
        # always a consumer REFUSED outcome): READY and the mapped
        # non-READY variants globally forbid the field, so a
        # bypass-copied refusal limitation on any other outcome is
        # a fixed typed boundary error, never a silent carry.
        if self.g_limitation is not None and self.outcome is not RootRegionAdmissionOutcome.REFUSED:
            raise _fixed("the G limitation is carried only on the actual G-domain refusal")
        if admission is not None:
            if self.outcome is not RootRegionAdmissionOutcome.READY:
                raise _fixed("an admission parent is carried only on the ready outcome")
            if r_result is None or r_result.outcome is not RootRegionGraphOutcome.READY:
                raise _fixed("a ready admission requires the actual R READY result")
            if self.diagnostics:
                raise _fixed("the ready outcome carries no consumer diagnostics")
        elif self.outcome is RootRegionAdmissionOutcome.READY:
            raise _fixed("the ready outcome requires the completed actual admission")
        elif self.outcome is RootRegionAdmissionOutcome.ROOT_CURRENTNESS_UNPROVEN:
            if (
                r_result is None
                or r_result.outcome is not RootRegionGraphOutcome.ROOT_CURRENTNESS_UNPROVEN
            ):
                raise _fixed("the mapped unproven outcome must retain the actual R result")
            if self.diagnostics:
                raise _fixed("the mapped unproven outcome carries no consumer diagnostic")
        elif self.outcome is RootRegionAdmissionOutcome.ROOT_AUTHORITY_CONFLICT:
            if (
                r_result is None
                or r_result.outcome is not RootRegionGraphOutcome.ROOT_AUTHORITY_CONFLICT
            ):
                raise _fixed(
                    "the mapped authority-conflict outcome must retain the actual R result"
                )
            if self.diagnostics:
                raise _fixed("the mapped authority-conflict outcome carries no consumer diagnostic")
        else:
            # REFUSED: the consumer-OWN diagnostics are closed and
            # bounded; a T-OWN entire-consumer work crossing AFTER
            # the actual R return (admission assembly or full-
            # result construction) names its own work domain and
            # retains the ACTUAL R result as bounded evidence; a
            # mapped ACTUAL R refusal carries the 1:1 mirror of the
            # actual R-OWN diagnostics (same strings, distinct
            # enum) and nothing else is invented.
            if len(self.diagnostics) > 1:
                raise _fixed("the refused outcome carries at most one consumer diagnostic")
            g_limitation = self.g_limitation
            if g_limitation is not None:
                # The inherited G channel is present ONLY on an
                # actual G-domain refusal, and the consumer-OWN
                # diagnostic names that domain consistently with
                # the ACTUAL G limitation (the exact
                # STATE_MALFORMED join; every other G limitation
                # is the over-bound domain).  The pairing reads
                # the FIRST diagnostic, so an empty refusal
                # diagnostic tuple carrying the G channel is a
                # fixed typed boundary error, never an index
                # error.
                if not self.diagnostics:
                    raise _fixed(
                        "the G limitation is carried only with the actual "
                        "G-domain refusal diagnostic"
                    )
                if self.diagnostics[0] is RootRegionAdmissionDiagnostic.ADMISSION_STATE_MALFORMED:
                    if g_limitation is not CurrentAdmissionLimitation.STATE_MALFORMED:
                        raise _fixed(
                            "the G state-malformed diagnostic must carry the actual G limitation"
                        )
                elif self.diagnostics[0] is RootRegionAdmissionDiagnostic.ADMISSION_OVER_BOUND:
                    if g_limitation is CurrentAdmissionLimitation.STATE_MALFORMED:
                        raise _fixed(
                            "the G over-bound diagnostic must not carry the "
                            "state-malformed limitation"
                        )
                else:
                    raise _fixed("the G limitation is carried only on the actual G-domain refusal")
            if r_result is not None:
                if self.diagnostics and self.diagnostics[0] == (
                    RootRegionAdmissionDiagnostic.WORK_UNITS_OVER_BOUND
                ):
                    # A T-OWN entire-consumer work crossing AFTER
                    # the actual R return is legal over ANY actual
                    # R result: the consumer names its own work
                    # domain and retains the actual R result as
                    # bounded evidence (never a usable admission).
                    pass
                elif r_result.outcome is RootRegionGraphOutcome.READY:
                    # A mapped G-domain refusal over an actual R
                    # READY: the consumer diagnostic is the
                    # admission-domain refusal (never an R
                    # mirror, which would invent an R refusal).
                    for diag in self.diagnostics:
                        if diag not in (
                            RootRegionAdmissionDiagnostic.ADMISSION_OVER_BOUND,
                            RootRegionAdmissionDiagnostic.ADMISSION_STATE_MALFORMED,
                        ):
                            raise _fixed(
                                "an actual G-domain refusal carries the closed admission diagnostic"
                            )
                else:
                    expected_mirror = tuple(
                        _R_DIAGNOSTIC_MAP[d.value] for d in r_result.diagnostics
                    )
                    if tuple(self.diagnostics) != expected_mirror:
                        raise _fixed(
                            "the mapped R refusal must mirror the actual R diagnostics exactly"
                        )
            elif self.diagnostics and self.diagnostics[0] in (
                RootRegionAdmissionDiagnostic.ADMISSION_OVER_BOUND,
                RootRegionAdmissionDiagnostic.ADMISSION_STATE_MALFORMED,
            ):
                # A G-domain refusal BEFORE the R return (the
                # F-phase crossing): the ACTUAL G limitation is
                # retained in the inherited G channel.
                if g_limitation is None:
                    raise _fixed(
                        "a G-domain refusal without the R result carries the actual G limitation"
                    )
        # Phase 2: exact input-identity joins (identity, not
        # structural equality): the EXACT input state is retained
        # on every outcome; the actual R result joins the same
        # state / lineage identity; the admission parent joins the
        # same state / namespace / R result / G bounds BY IDENTITY
        # (a detached or value-equal clone refuses).
        if ns.lineage_key != state.lineage_key:
            # The ONLY carrying record with a non-joined
            # namespace is the T-OWN early foreign-scope refusal
            # (the consumer's own O(1) input fence refused the
            # pair before any derivation, so no R result and no
            # admission were ever returned); a foreign namespace
            # with ANY carried derivation evidence is a bypass
            # splice and refuses.
            if not (
                self.outcome is RootRegionAdmissionOutcome.REFUSED
                and self.r_result is None
                and self.admission is None
                and self.g_limitation is None
                and tuple(self.diagnostics) == (RootRegionAdmissionDiagnostic.FOREIGN_SCOPE,)
            ):
                raise _fixed("the consumer namespace must join the exact input state lineage")
        if self.lineage_key != state.lineage_key:
            raise _fixed("the consumer lineage key must join the exact input state")
        if self.revision != state.revision:
            raise _fixed("the consumer revision must join the exact input state")
        if r_result is not None:
            if r_result.state is not state:
                raise _fixed("the actual R result must retain the exact input state by identity")
            if r_result.lineage_key != state.lineage_key or r_result.revision != state.revision:
                raise _fixed("the actual R result must join the exact input state identity")
        if admission is not None:
            if admission.state is not state or admission.ns is not self.ns:
                raise _fixed("the admission parent must retain the exact input state and namespace")
            if r_result is not None and admission.r_result is not r_result:
                raise _fixed("the admission parent must retain the actual R result by identity")
            if admission.g_bounds is not self.g_bounds:
                raise _fixed("the admission parent must retain the actual G bounds by identity")
        # The closed O(1) carried-bound-set gate completes at this
        # carrying boundary BEFORE the consumer scope-key
        # serializer/hash targets (the existing before-serializer
        # carrying-boundary law): the six P-namespace sets on EVERY
        # outcome, and the four R-carried sets plus the actual G set
        # when the ACTUAL R result is carried -- reusing the ACTUAL
        # closed S fences.  The ACTUAL closed source-independent
        # carried R joins follow at the same boundary (the nested
        # Q/F/E bound/header/scope joins and the outcome invariants,
        # including the nested Q result's own bound set, which the
        # flat eleven-set fence does not visit).  The CHARGED R
        # source law (the root-body content pass and the READY
        # association walk) is NOT re-run at this boundary: the
        # terminal refusal record retains the actual R object by
        # reference as bounded evidence without admitting or
        # authorizing its source, and the complete source law
        # stays on the metered R-derivation and S-parent path.
        # The phase-5 S parent re-validation keeps its own
        # carrying boundary; this gate precedes, never replaces,
        # it.
        if r_result is not None:
            if not _s_all_eleven_bound_sets_closed(ns, r_result, self.g_bounds):
                raise _fixed("the actual eleven carried bound sets must be closed scalar sets")
            # A partial, bypass-copied or inconsistent nested record
            # refuses with the ACTUAL R boundary's fixed private
            # errors BEFORE the consumer scope-key serializer
            # targets, never after (source-independent: no root
            # body content pass at this boundary).
            _r_result_carried_closed(r_result)
        elif not _s_six_ns_bound_sets_closed(ns):
            raise _fixed("the carried P namespace bound sets must be closed scalar sets")
        # Phase 3: the stable consumer scope key RECOMPUTED from
        # the actual carried fields (a stale or forged key
        # refuses, never retained).
        expected_scope = root_region_admission_scope_key(
            state.lineage_key,
            self.contract_version,
            self.policy_version,
            r_result.scope_key if r_result is not None else _T_R_SCOPE_ABSENT,
            admission.scope_key if admission is not None else _T_MODEL_SCOPE_ABSENT,
            self.g_contract_version,
            self.g_policy_version,
            self.bounds,
            self.g_bounds,
        )
        if expected_scope != self.scope_key:
            raise _fixed("the consumer scope key must recompute from the actual carried fields")
        # Phase 4: closed counter fences under the ACTUAL
        # effective bound sets (the honest same-run ledgers of
        # THIS operation; O(1) range checks, never re-measurements):
        # the entire T outer is fenced by the consumer total; the
        # R total by the R outer it is coupled into (every R unit
        # charges the T outer exactly once, so it cannot exceed
        # it); the G subtree by the ACTUAL G total; the G
        # admission stage by the ACTUAL inherited graph work
        # ceiling; the cumulative entry-source bytes by the ACTUAL
        # G cumulative ceiling.
        if self.work_units > self.bounds.max_total_work_units:
            raise _fixed("the entire-consumer work counter exceeds the actual consumer total")
        if self.r_work_units > self.work_units:
            raise _fixed("the R work counter cannot exceed the entire-consumer work counter")
        if r_result is not None and self.r_work_units > r_result.bounds.max_total_work_units:
            raise _fixed("the R work counter exceeds the actual R total ceiling")
        if self.g_work_units > self.g_bounds.max_total_work_units:
            raise _fixed("the G subtree work counter exceeds the actual G total ceiling")
        graph_bounds = getattr(self.ns, "graph_bounds", None)
        if graph_bounds is None or not _t_int_in(
            getattr(graph_bounds, "max_work_units", None), 1, 10_000_000
        ):
            raise _fixed("the consumer result namespace must carry the closed graph bounds")
        if self.stage_work_units > graph_bounds.max_work_units:
            raise _fixed("the G stage work counter exceeds the actual inherited stage ceiling")
        if self.entry_source_bytes > self.g_bounds.max_total_entry_source_bytes:
            raise _fixed("the entry-source bytes counter exceeds the actual G cumulative ceiling")
        # Phase 5: the ACTUAL local law re-run at the third
        # carrying parent (not tag equality): the complete S
        # admission-parent law -- the leaf law, the canonical
        # rekey, the reverse-index law, the counter law and the S
        # scope key -- through the actual model re-validation.
        # A partial, bypass-copied or coherently rekeyed nested
        # record refuses here, before any unsafe attribute access,
        # traversal or serialization at this boundary.
        if admission is not None:
            RootRegionAdmission.model_validate(admission)
        return self

    def __repr__(self) -> str:  # noqa: D105 - privacy law
        # Fixed non-echoing rendering: closed enums, counts and
        # metadata only; no root/member source text, no private
        # IDs, no principal/session/repository/route or model
        # identity values cross this surface.
        r_result = self.r_result
        admission = self.admission
        return (
            "RootRegionAdmissionResult("
            f"outcome={self.outcome.value!r}, "
            f"revision={self.revision}, "
            f"diagnostics={tuple(d.value for d in self.diagnostics)!r}, "
            f"g_limitation={self.g_limitation.value if self.g_limitation is not None else None!r}, "
            f"r_outcome={r_result.outcome.value if r_result is not None else None!r}, "
            f"entries_retained={admission.entries_retained if admission is not None else None!r}, "
            f"work_units={self.work_units}, "
            f"r_work_units={self.r_work_units}, "
            f"g_work_units={self.g_work_units}, "
            f"stage_work_units={self.stage_work_units}, "
            f"entry_source_bytes={self.entry_source_bytes})"
        )

    __str__ = __repr__

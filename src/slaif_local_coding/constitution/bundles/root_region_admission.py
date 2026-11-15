"""Pure versioned complete root-region admission consumer
operation (objective 018-t).

This module is the SAME-RUN complete consumer promised by the
accepted 018-r / 018-s slices: the ACTUAL public P input
(state/namespace, never caller-positive R/Q/F/graph/admission
snapshots or verification flags) derives ACTUAL R (including
Q/P/D/B/source/F/E) EXACTLY ONCE in this one charged operation,
the ACTUAL selected-root-aware G assembly consumes R's selected
source, current graph and same-run E overlay, and the complete
new result (the THIRD carrying boundary,
``RootRegionAdmissionResult``) carries the exact input, the
actual R result by immutable reference (once returned, on EVERY
later outcome) and the actual S admission parent by immutable
reference (READY only).

ONE entire operation, independent inherited domains (the
versioned ledger law):

* the NEW entire-consumer outer
  (``RootRegionAdmissionBounds.max_total_work_units``, default
  AND hard 8388608; own diagnostics 64 default AND hard) is
  created BEFORE any derivation work and covers the ENTIRE
  consumer operation:
* EVERY actual R unit (Q/P/D/B/source/F/E included) is coupled
  into it unit-for-unit through the narrow typed R-core seam
  (``_TRTotal``) BEFORE the crossing work runs;
* the ACTUAL G subtree ledger (``_TSubtree``) is created BEFORE
  R's F phase: every actual F unit charges the SAME G ledger
  that the admission phase uses (its independent F-subtree
  ceiling binds during the explicit F phase exactly as in the
  accepted 018-g law); G covers F plus the
  admission/root/FILE/association/S-parent construction and
  validation, and NOT Q/P/selected-source resolution or the
  final full-result parent;
* R covers its actual derivation only; the full-result parent
  and its rechecks charge the NEW entire outer;
* shared work charges each applicable domain ONCE (a unit
  shared with the R derivation never double-charges the entire
  outer);
* the actual inherited Q/P/D/B/E/F/GraphBounds, G,
  graph/admission-stage, diagnostic, source and original-batch
  domains remain independently binding beneath it (no global
  minimum, no reset, no whole-cap reservation, no post-hoc
  initialization, no module-global or context-global budget
  channel, no caller verification flag).

The NEW entire-consumer total is a NEW versioned work domain:
not a raised old cap, not a RAM/RSS/token budget, not a
reinterpretation of a source-size setting.  Conservative
validated structural ceilings cover the genuinely fixed closed
metadata passes (documented below); every variable metadata /
source / serialization pass is reserved by its actual recipe
BEFORE it runs (the accepted S component precharge contracts
included).  The witness region-compatibility term runs under
the T-only tightened actual-owner billing (its owner-domain
walks close at the ACTUAL retained owner population, every one
fenced under the ACTUAL inherited B caps before it feeds the
term), and the carried R metadata joins at the third
boundary run under the derived carried-join ceiling for the
constructor's own re-run (separate from the phase-5 S parent
re-validation's COMPLETE R result law pass, reserved by the
actual S admission-parent precharge) -- two real passes, each
reserved once.

The operation is INERT: no runtime/HTTP wiring, no compiler, no
tokenizer, no RAM/recovery state, no model call, no revision
advance, no authority acquisition and no bootstrap fallback.
READY means only actual R READY AND completed actual admission
AND the full-result third-parent checks -- never acquired
dependencies, compiled content, cache readiness or v1 runtime
readiness.  Q uncertainty/conflict, R/F/G refusal and every
resource crossing expose no usable admission or bootstrap
fallback and retain every already-returned actual evidence
truthfully (never rerun or manufactured after a crossing).
Every old C/G/H/O/I/P/Q/R/S public signature, schema, default,
version, recipe and refusal law stays intact.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ValidationError

from .bundle_admission import _key_canonical
from .bundle_admission_models import (
    BoundaryClass,
    BundleAdmissionNamespace,
    BundleKeyRecord,
    EntryClass,
    MemberClass,
    OwnershipGroup,
)
from .bundle_proof_models import BundleProof
from .causal_history_models import CompletedReadOccurrence
from .current_admission import (
    _assemble_file_entries,
    _GOuter,
    _GOverflow,
    _GStage,
)
from .current_admission_models import (
    CURRENT_ADMISSION_CONTRACT_VERSION,
    CURRENT_ADMISSION_POLICY_VERSION,
    CurrentAdmissionBounds,
    CurrentAdmissionLimitation,
    CurrentAdmissionPathAssociation,
)
from .current_graph import _Malformed, _sorted
from .current_graph_models import (
    CURRENT_GRAPH_CONTRACT_VERSION,
    CURRENT_GRAPH_POLICY_VERSION,
    CurrentGraphBounds,
)
from .currentness import _revalidate_ns
from .currentness_models import (
    CURRENTNESS_CONTRACT_VERSION,
    CURRENTNESS_POLICY_VERSION,
    OPAQUE_GROUP_RECIPE_VERSION,
    CurrentnessBounds,
    CurrentnessGroupRecord,
)
from .graph_models import ROOT_FILENAME, _fixed, _sha256_hex
from .root_region_admission_models import (
    ROOT_REGION_ADMISSION_MODELS_CONTRACT_VERSION,
    ROOT_REGION_ADMISSION_MODELS_POLICY_VERSION,
    RootRegionAdmission,
    RootRegionAdmissionEntry,
    _s_bound_set_json_len,
    _s_canonical_metadata_precharge_closed,
    _s_g_bounds_closed,
    _s_json_string_escaped_ceil,
    _s_parent_precharge_closed,
    _s_region_precharge_closed,
    _s_root_content_precharge_closed,
    _SRegionWorkReserver,
    root_region_admission_model_scope_key,
)
from .root_region_admission_result_models import (
    _HARD_T_WORK_UNITS,
    _R_DIAGNOSTIC_MAP,
    _T_MODEL_SCOPE_ABSENT,
    _T_R_SCOPE_ABSENT,
    ROOT_REGION_ADMISSION_CONTRACT_VERSION,
    ROOT_REGION_ADMISSION_POLICY_VERSION,
    RootRegionAdmissionBounds,
    RootRegionAdmissionDiagnostic,
    RootRegionAdmissionOutcome,
    RootRegionAdmissionResult,
    root_region_admission_bounds_shape_ok,
    root_region_admission_scope_key,
)
from .root_region_currentness import _q_ns_boundary_ok, _q_state_boundary_ok
from .root_region_currentness_models import (
    ROOT_REGION_CURRENTNESS_CONTRACT_VERSION,
    ROOT_REGION_CURRENTNESS_POLICY_VERSION,
    RootRegionCurrentnessBounds,
)
from .root_region_graph import (
    _derive_root_region_graph_core,
    _f_bounds_shape_ok,
    _ROuter,
)
from .root_region_graph_models import (
    _R_E_OVERLAY_FIELDS,
    _R_F_GRAPH_FIELDS,
    _R_RESULT_FIELDS,
    RootRegionGraphBounds,
    RootRegionGraphOutcome,
    RootRegionGraphResult,
    _r_fields_present,
    _r_graph_version_ok,
    root_region_graph_bounds_shape_ok,
)
from .root_region_lineage import (
    _region_d_namespace,
    _region_preflight_ns_shape,
    _region_state_shape,
)
from .root_region_lineage_models import (
    RootRegionLineageNamespace,
    RootRegionLineageState,
)

#: The closed early-gate / bootstrap-cap-read / ledger-
#: construction pass ceiling of the consumer outer (the fixed
#: O(1) state fence and the closed bootstrap shape/cap reads
#: that size the ledgers BEFORE any bound model is constructed,
#: plus the three ledger constructions -- the accepted R
#: base-charge convention as a conservative validated
#: structural ceiling).
_T_BASE_UNITS = 64
#: The closed ceiling over the O(1) input fences that run
#: under the ledger before the bound models are resolved (the
#: closed namespace boundary/shape/version/lineage-join
#: fence): the fixed O(1) field reads as a conservative
#: validated structural ceiling.
_T_NS_FENCE_UNITS = 4
#: The closed ceiling over the default bound-model
#: construction (the fixed closed 2-scalar-field default
#: walk).
_T_BOUNDS_DEFAULT_BUILD_UNITS = 4
#: The closed ceiling over the bound-model model_dump +
#: model_validate re-resolution (the fixed closed 2-scalar-
#: field dump + re-validation walk).
_T_BOUNDS_REVALIDATE_UNITS = 8
#: The closed consumer scope-key single pass (2 bound
#: model_dumps + 2 inner json encodes + 1 payload list + 1
#: outer json + 1 UTF8 encode + 1 sha256, plus the closed
#: input preflight fences).
_T_SCOPE_KEY_UNITS = 18
#: The closed S-model scope-key single pass (1 bound
#: model_dump + 1 inner json + 1 payload list + 1 outer json +
#: 1 UTF8 encode + 1 sha256, plus the closed key/version/bound
#: preflight fences).
_T_S_SCOPE_KEY_UNITS = 12
#: The closed full-result parent build reservation (the T
#: result validator's actual re-run at the third carrying
#: boundary, EXCLUDING the S admission-parent re-validation,
#: which the actual S parent precharge component reserves at
#: the same boundary): the field-presence and closed scalar /
#: version / bound / carried-record fences, the exact identity
#: joins, the consumer scope-key recomputation pass, the
#: counter range fences and the construction itself -- a
#: conservative validated structural ceiling over the closed
#: fixed list.
_T_RESULT_BUILD_UNITS = 256

# The source-independent carried R metadata joins re-run at
# the third carrying boundary inside the result constructor
# are reserved by ``_t_r_carried_join_precharge`` (the closed
# derived ceiling under the cache-root-region-admission/v1
# cost law) BEFORE the constructor target on EVERY outcome
# that carries the R result: the constructor re-runs these
# joins itself, separately from the phase-5 S parent
# re-validation (whose own COMPLETE R result law re-run,
# carried + source, is reserved by the actual S
# admission-parent precharge, READY only) -- two real passes,
# each reserved once.  The CHARGED R source law (the root-body content
# pass and the READY association walk) is NOT part of this
# boundary's work: it stays on the metered R-derivation and
# S-parent path, and the terminal refusal record retains the
# actual R object by reference as bounded evidence without
# authorizing its source.


class _TOverflow(Exception):
    """The ONE entire-consumer outer crossed: a fixed private
    resource fact (the public derivation maps it to the typed
    atomic over-bound refusal preserving every already-returned
    actual evidence)."""

    __slots__ = ()


class _TOuter:
    """The ONE entire-consumer outer work ledger (018-t).

    Charges EVERY unit of the whole consumer operation against
    the ACTUAL ``max_total_work_units`` BEFORE the crossing work
    runs; cumulative and NEVER reset.  A crossing raises the
    fixed private overflow (the caller maps it)."""

    __slots__ = ("work_cap", "work_spent")

    def __init__(self, work_cap: int) -> None:
        self.work_cap = work_cap
        self.work_spent = 0

    def unit(self) -> bool:
        if self.work_spent + 1 > self.work_cap:
            raise _TOverflow()
        self.work_spent += 1
        return True

    def units(self, n: int) -> None:
        for _ in range(n):
            self.unit()


class _TRTotal(_ROuter):
    """The R-total coupling adapter (018-t): EVERY actual R unit
    charges the ACTUAL R domain (INDEPENDENT ceiling from the
    actual effective R bounds) AND the ONE entire-consumer outer
    exactly ONCE, before the crossing work runs.  An R-domain
    crossing raises the fixed private R overflow (mapped by the
    R core itself); an entire-outer crossing raises the fixed
    private T overflow, which the R core propagates unchanged so
    the consumer maps it at its own boundary."""

    __slots__ = ("ttotal",)

    def __init__(self, ttotal: _TOuter, work_cap: int) -> None:
        super().__init__(work_cap)
        self.ttotal = ttotal

    def unit(self) -> bool:
        super().unit()  # R domain first (raises _ROverflow)
        self.ttotal.unit()  # entire consumer outer (raises _TOverflow)
        return True


class _TSubtree(_GOuter):
    """The ACTUAL G subtree ledger (018-t): the ACTUAL G total
    ceiling (and the independent F-subtree ceiling during the
    explicit F phase, exactly as in the accepted 018-g law) on
    EVERY unit, PLUS the ONE entire-consumer outer exactly ONCE
    for every unit that is NOT already charged into it through
    the R coupling.  During the F phase the actual F units flow
    into the entire outer through the ``_TRTotal`` R chain (they
    are charged BEFORE this ledger sees them); after the F phase
    every admission/root/FILE/association/S-parent unit charges
    the G total AND the entire outer once each.  No shared unit
    is ever double-charged into the entire outer.  A G-domain
    crossing raises the fixed private G overflow, which the R
    core propagates unchanged so the consumer maps it at its own
    boundary."""

    __slots__ = ("ttotal",)

    def __init__(
        self,
        f_work_cap: int,
        f_diag_cap: int,
        g_work_cap: int,
        g_diag_cap: int,
        ttotal: _TOuter,
    ) -> None:
        # Bypass the bound-model constructor reads of the public
        # ``_GOuter``: this ledger is sized by the closed O(1)
        # bootstrap cap reads (the actual defaults on any
        # malformed candidate) BEFORE any bound model is
        # constructed; the resolved bound models carry exactly
        # these caps.
        self.work_cap = g_work_cap
        self.work_spent = 0
        self.diag_cap = f_diag_cap
        self.diag_spent = 0
        self.f_work_cap = f_work_cap
        self.f_work_spent = 0
        self.g_diag_cap = g_diag_cap
        self.g_diag_spent = 0
        self._f_phase = False
        self.ttotal = ttotal

    def unit(self) -> bool:
        ok = super().unit()  # G domains first (raises _GOverflow)
        if not self._f_phase:
            self.ttotal.unit()  # entire consumer outer (_TOverflow)
        return ok


class _TMeter:
    """The closed caller-supplied component meter over the T
    entire outer or the G subtree ledger for the versioned S
    component precharge contracts: the typed ``reserve`` call is
    the exact ledger unit charge, so a crossing raises BEFORE
    the caller's actual targets (the leaf law, the constructor,
    the serializer) run.  No unlimited or default meter exists."""

    __slots__ = ("_ledger",)

    def __init__(self, ledger: _TOuter | _TSubtree) -> None:
        self._ledger = ledger

    def reserve(self, units: int) -> None:
        self._ledger.units(units)


def _t_result(
    outcome: RootRegionAdmissionOutcome,
    state: RootRegionLineageState,
    ns: RootRegionLineageNamespace,
    t_bounds: RootRegionAdmissionBounds,
    g_bounds: CurrentAdmissionBounds,
    r_result: RootRegionGraphResult | None,
    admission: RootRegionAdmission | None,
    diagnostics: tuple[RootRegionAdmissionDiagnostic, ...],
    ttotal: _TOuter,
    g_subtree: _TSubtree,
    g_stage: _GStage | None,
    rtotal: _TRTotal,
    entry_source_bytes: int,
    scope_key: str | None = None,
    g_limitation: CurrentAdmissionLimitation | None = None,
) -> RootRegionAdmissionResult:
    """The complete result over the ACTUAL returned evidence:
    the honest same-run ledger counters of THIS operation and
    the stable consumer scope key RECOMPUTED from the actual
    carried fields (never a copied or fabricated key).  The
    charged paths pass the scope key computed under the
    before-work reservation; a crossing refusal path (where the
    crossed ledger can charge no more) builds its refusal result
    under the closed refusal-construction convention (the fixed
    closed recipe, unchargeable by definition)."""
    if scope_key is None:
        scope_key = root_region_admission_scope_key(
            state.lineage_key,
            ROOT_REGION_ADMISSION_CONTRACT_VERSION,
            ROOT_REGION_ADMISSION_POLICY_VERSION,
            r_result.scope_key if r_result is not None else _T_R_SCOPE_ABSENT,
            admission.scope_key if admission is not None else _T_MODEL_SCOPE_ABSENT,
            CURRENT_ADMISSION_CONTRACT_VERSION,
            CURRENT_ADMISSION_POLICY_VERSION,
            t_bounds,
            g_bounds,
        )
    return RootRegionAdmissionResult(
        outcome=outcome,
        state=state,
        ns=ns,
        r_result=r_result,
        admission=admission,
        diagnostics=diagnostics,
        bounds=t_bounds,
        g_bounds=g_bounds,
        g_limitation=g_limitation,
        lineage_key=state.lineage_key,
        scope_key=scope_key,
        revision=state.revision,
        work_units=ttotal.work_spent,
        r_work_units=rtotal.work_spent,
        g_work_units=g_subtree.work_spent,
        stage_work_units=g_stage.work_spent if g_stage is not None else 0,
        entry_source_bytes=entry_source_bytes,
    )


def _t_early_refuse(
    state: RootRegionLineageState,
    ns: RootRegionLineageNamespace,
    t_bounds: RootRegionAdmissionBounds,
    g_bounds: CurrentAdmissionBounds,
    diagnostic: RootRegionAdmissionDiagnostic,
    ttotal: _TOuter,
    g_subtree: _TSubtree,
    rtotal: _TRTotal,
) -> RootRegionAdmissionResult:
    """The CHARGED post-ledger early refusal: the closed
    scope-key and full-result-build reservations are charged
    BEFORE the fixed refusal recipe runs, so the honest same-run
    counters reflect the actual early-gate work (no R result, no
    admission; the actual input state and namespace retained as
    bounded evidence, the stable scope key under the fixed
    private absence placeholders).  A crossing during those
    reservations falls to the closed refusal-construction
    convention (the crossed ledger charges no more; the scope
    key is recomputed from the actual carried fields under the
    fixed closed recipe)."""
    scope_key: str | None
    try:
        ttotal.units(_T_SCOPE_KEY_UNITS)
        scope_key = root_region_admission_scope_key(
            state.lineage_key,
            ROOT_REGION_ADMISSION_CONTRACT_VERSION,
            ROOT_REGION_ADMISSION_POLICY_VERSION,
            _T_R_SCOPE_ABSENT,
            _T_MODEL_SCOPE_ABSENT,
            CURRENT_ADMISSION_CONTRACT_VERSION,
            CURRENT_ADMISSION_POLICY_VERSION,
            t_bounds,
            g_bounds,
        )
        ttotal.units(_T_RESULT_BUILD_UNITS)
    except _TOverflow:
        scope_key = None
    return _t_result(
        RootRegionAdmissionOutcome.REFUSED,
        state,
        ns,
        t_bounds,
        g_bounds,
        None,
        None,
        (diagnostic,),
        ttotal,
        g_subtree,
        None,
        rtotal,
        0,
        scope_key,
        None,
    )


def _t_resolve_t_bounds(
    ttotal: _TOuter,
    shape_ok: bool,
    bounds: RootRegionAdmissionBounds | None,
    charged: bool,
) -> tuple[RootRegionAdmissionBounds, bool]:
    """The closed T bound resolution (the ACTUAL default
    construction or the model_dump + model_validate
    re-resolution targets).  On the metered paths the closed
    reservation is charged BEFORE the target runs (``charged``
    True); on the full-ledger crossing path the fixed closed
    recipe runs under the refusal-construction convention
    (``charged`` False -- the crossed ledger charges no more).
    Returns (the resolved model, whether the candidate was
    malformed)."""
    if bounds is not None and shape_ok:
        if charged:
            ttotal.units(_T_BOUNDS_REVALIDATE_UNITS)
        try:
            return (
                RootRegionAdmissionBounds.model_validate(
                    bounds.model_dump(mode="python", warnings=False)
                ),
                False,
            )
        except Exception:
            pass
    if charged:
        ttotal.units(_T_BOUNDS_DEFAULT_BUILD_UNITS)
    return RootRegionAdmissionBounds(), bounds is not None


def _t_resolve_g_bounds(
    ttotal: _TOuter,
    shape_ok: bool,
    admission_bounds: CurrentAdmissionBounds | None,
    charged: bool,
) -> tuple[CurrentAdmissionBounds, bool]:
    """The closed G bound resolution (the same actual targets
    and the same charged/uncharged law as the T resolution)."""
    if admission_bounds is not None and shape_ok:
        if charged:
            ttotal.units(_T_BOUNDS_REVALIDATE_UNITS)
        try:
            return (
                CurrentAdmissionBounds.model_validate(
                    admission_bounds.model_dump(mode="python", warnings=False)
                ),
                False,
            )
        except Exception:
            pass
    if charged:
        ttotal.units(_T_BOUNDS_DEFAULT_BUILD_UNITS)
    return CurrentAdmissionBounds(), admission_bounds is not None


def _t_r_carried_join_precharge(ttotal: _TOuter, r_result: RootRegionGraphResult) -> None:
    """The closed derived ceiling over the source-independent
    carried R metadata joins re-run at the third carrying
    boundary (the cache-root-region-admission/v1 cost law,
    T-only): reserved on the ENTIRE consumer outer BEFORE the
    result constructor re-runs ``_r_result_carried_closed`` on
    EVERY outcome that carries the R result.  The phase-5 S
    parent re-validation re-runs the COMPLETE R result law
    (carried + source) as its own SEPARATE actual pass, reserved
    by the actual S admission-parent precharge (READY only):
    two real carried-metadata passes, each reserved once, no
    reservation spent twice.  The ceiling is derived from
    the closed fixed metadata field counts, the ACTUAL
    scope-recipe part lengths and the bound-record JSON ceilings
    (the S precharge's established scope work formulas, reused):
    the closed O(1) field-pool / tag / 64-hex-comparison pool,
    the R and Q scope-key recipes, the diagnostic sorted/dedup
    walk at the ACTUAL count, and the E/F JSON-array scope
    recipes with their own ceiling calculation walks reserved
    BEFORE they run.  No root-body content pass and no source or
    history walk at this boundary (they stay on the metered
    R-derivation and S-parent paths).  Over-charges only; every
    reservation precedes its target."""
    q = r_result.q_result
    f_result = r_result.f_result
    f_graph = f_result.overlay if f_result is not None else None
    e_overlay = r_result.e_overlay
    # (1) the closed O(1) pool: the eleven-set carrying fence,
    # the fixed field-presence pools at their ACTUAL closed field
    # counts, the fixed version-tag / class / int /
    # outcome-dispatch visits and the closed 64-hex comparisons
    # at their 1 + 2*64 set-visit counts (eight on the fixed
    # recipe): a conservative validated structural ceiling over
    # the closed fixed recipe.
    ttotal.units(
        128
        + 8 * 129
        + len(_R_RESULT_FIELDS)
        + sum(
            len(type(b).model_fields)
            for b in (r_result.bounds, r_result.q_bounds, r_result.f_bounds, r_result.e_bounds)
        )
        + (10 if q is not None else 0)
        + (5 if q is not None and q.p_selection is not None else 0)
        + (5 if r_result.outcome is RootRegionGraphOutcome.READY else 0)
        + (3 if f_result is not None else 0)
        + (len(_R_F_GRAPH_FIELDS) if f_graph is not None else 0)
        + (
            sum(
                len(type(b).model_fields)
                for b in (f_graph.bounds, f_graph.currentness_bounds, f_graph.graph_bounds)
            )
            if f_graph is not None
            else 0
        )
        + (len(_R_E_OVERLAY_FIELDS) if e_overlay is not None else 0)
        + (len(type(e_overlay.bounds).model_fields) if e_overlay is not None else 0)
        + (64 + 4 * 129 if r_result.resolved_source is not None else 0)
    )
    # (2) the R scope key re-derivation: the 22-part join walk,
    # the payload UTF-8 ceiling (four bytes per character is the
    # structural ceiling) and its domain-prefixed SHA-256.
    r_scope_chars = (
        sum(
            len(part)
            for part in (
                r_result.contract_version,
                r_result.policy_version,
                ROOT_REGION_CURRENTNESS_CONTRACT_VERSION,
                ROOT_REGION_CURRENTNESS_POLICY_VERSION,
                CURRENT_GRAPH_CONTRACT_VERSION,
                CURRENT_GRAPH_POLICY_VERSION,
                CURRENTNESS_CONTRACT_VERSION,
                CURRENTNESS_POLICY_VERSION,
                r_result.state.lineage_key,
            )
        )
        + sum(
            len(str(value))
            for value in (
                r_result.bounds.max_total_work_units,
                r_result.bounds.max_diagnostics,
                r_result.q_bounds.max_total_work_units,
                r_result.q_bounds.max_diagnostics,
                r_result.f_bounds.max_total_work_units,
                r_result.f_bounds.max_diagnostics,
                r_result.e_bounds.max_paths,
                r_result.e_bounds.max_groups,
                r_result.e_bounds.max_witness_memberships,
                r_result.e_bounds.max_relation_pairs,
                r_result.e_bounds.max_work_units,
                r_result.e_bounds.max_diagnostics,
            )
        )
        + len(r_result.graph_version)
        + 23
    )
    ttotal.units(24 + r_scope_chars + 2 * (27 + 4 * r_scope_chars) + 104)
    # (3) the R diagnostic sorted/dedup walk at the ACTUAL count.
    n_rd = len(r_result.diagnostics)
    ttotal.units(n_rd + n_rd * max(1, n_rd.bit_length()) + n_rd)
    # (4) the nested Q scope key re-derivation: the 5-part join
    # walk, its UTF-8 ceiling and its domain-prefixed SHA-256.
    if q is not None:
        q_scope_chars = (
            len(q.contract_version)
            + len(q.policy_version)
            + len(q.state.lineage_key)
            + len(str(q.bounds.max_total_work_units))
            + len(str(q.bounds.max_diagnostics))
            + 4
        )
        ttotal.units(1 + 5 + q_scope_chars + 2 * (33 + 4 * q_scope_chars) + 104)
    # (5) the F graph and E overlay scope re-derivations: the
    # E-recipe (6-element) and F-recipe (15-element) JSON-array
    # scope keys, whose UTF-8 encoding is SHA-256-ed (the
    # ensure_ascii output is pure ASCII, so the closed JSON
    # length ceiling IS the target's byte ceiling).  The
    # precharge's OWN ceiling calculations are charged work,
    # each reserved BEFORE its walk runs, and the target's
    # dump/dumps/encode/SHA passes are reserved BEFORE the
    # target may run them.
    if f_graph is not None or e_overlay is not None:
        _scope_sets: list[BaseModel] = []
        if f_graph is not None:
            _scope_sets.extend((f_graph.currentness_bounds, f_graph.bounds, f_graph.graph_bounds))
        if e_overlay is not None:
            _scope_sets.append(e_overlay.bounds)
        # (a) the dump-meta construction (field counts,
        # per-field bit widths and name lengths) over the
        # DISTINCT carried bound sets, reserved at its closed
        # 6 + 6*n pass per set BEFORE it walks the values (the
        # sets are closed under their original hard ranges, so
        # the bit widths are bounded).
        ttotal.units(sum(6 + 6 * len(type(b).model_fields) for b in _scope_sets))
        _scope_set_meta = tuple(
            (
                len(type(b).model_fields),
                sum(1 + getattr(b, field).bit_length() for field in type(b).model_fields),
                sum(len(field) for field in type(b).model_fields),
            )
            for b in _scope_sets
        )
        # (b) the ensure_ascii escaped-ceiling walks at their
        # carried string lengths, reserved BEFORE they run.
        _scope_texts: list[str] = [CURRENTNESS_CONTRACT_VERSION, OPAQUE_GROUP_RECIPE_VERSION]
        if f_graph is not None:
            _scope_texts.extend(
                (
                    f_graph.currentness_policy_version,
                    f_graph.history_key,
                    f_graph.workspace,
                    f_graph.contract_version,
                    f_graph.policy_version,
                    f_graph.graph_version,
                    f_graph.reference_version,
                    f_graph.proof_version,
                    f_graph.currentness_contract_version,
                    f_graph.currentness_recipe_version,
                    f_graph.root_digest,
                    f_graph.currentness_scope_key,
                )
            )
        if e_overlay is not None:
            _scope_texts.extend(
                (e_overlay.policy_version, e_overlay.history_key, e_overlay.workspace)
            )
        ttotal.units(sum(1 + len(text) for text in _scope_texts))
        _scope_esc = tuple(_s_json_string_escaped_ceil(text) for text in _scope_texts)
        # (c) the exact bound-set JSON length calculations at
        # their closed dump walks, reserved BEFORE they run.
        ttotal.units(sum(1 + 2 * (2 * nf + nc + du) for nf, du, nc in _scope_set_meta))
        _scope_set_lens = tuple(_s_bound_set_json_len(bound) for bound in _scope_sets)
        # (d) the closed JSON-array length ceilings of the
        # actual element recipes, reserved as their own
        # calculation.
        ttotal.units(3 + 6 + 15 + 6)
        _esc_cv = _scope_esc[0]
        _esc_ogr = _scope_esc[1]
        if f_graph is not None:
            # The F currentness scope key: the accepted E
            # recipe (6-element array: the contract version,
            # the graph's own currentness policy version, the
            # opaque recipe version, its history key, its
            # workspace and its currentness bound set as a
            # JSON string).
            fcur_payload_ceil = (
                2
                + 5
                + 2
                + _esc_cv
                + 2
                + _scope_esc[2]
                + 2
                + _esc_ogr
                + 2
                + _scope_esc[3]
                + 2
                + _scope_esc[4]
                + 2
                + _scope_set_lens[0]
                + 2 * _scope_set_meta[0][0]
            )
            # The F graph scope key: the accepted F recipe
            # (15-element array: 12 scope headers plus the
            # graph, currentness and graph-inherited bound
            # sets as JSON strings).
            fgr_payload_ceil = (
                2
                + 14
                + 2
                + _scope_esc[5]
                + 2
                + _scope_esc[6]
                + 2
                + _scope_esc[7]
                + 2
                + _scope_esc[8]
                + 2
                + _scope_esc[9]
                + 2
                + _scope_esc[10]
                + 2
                + _scope_esc[2]
                + 2
                + _scope_esc[11]
                + 2
                + _scope_esc[3]
                + 2
                + _scope_esc[4]
                + 2
                + _scope_esc[12]
                + 2
                + _scope_esc[13]
                + 2
                + _scope_set_lens[1]
                + 2 * _scope_set_meta[1][0]
                + 2
                + _scope_set_lens[0]
                + 2 * _scope_set_meta[0][0]
                + 2
                + _scope_set_lens[2]
                + 2 * _scope_set_meta[2][0]
            )
            # The F currentness scope key target: its bound-set
            # dump, its 6-element array serialization, its
            # UTF-8 encode and its prefix-free SHA-256.
            ttotal.units(
                1
                + 1
                + 2 * (2 * _scope_set_meta[0][0] + _scope_set_meta[0][2] + _scope_set_meta[0][1])
                + fcur_payload_ceil
                + 2 * fcur_payload_ceil
                + 104
                + 1
            )
            # The F graph scope key target: its THREE bound-set
            # dumps, its 15-element array serialization, its
            # UTF-8 encode and its SHA-256, reserved BEFORE the
            # target may re-derive it.
            ttotal.units(
                1
                + sum(1 + 2 * (2 * nf + nc + du) for nf, du, nc in _scope_set_meta[0:3])
                + fgr_payload_ceil
                + 2 * fgr_payload_ceil
                + 104
                + 1
            )
        if e_overlay is not None:
            _e_base = 14 if f_graph is not None else 2
            _e_set = 3 if f_graph is not None else 0
            # The E overlay currentness scope key: the accepted
            # E recipe over the overlay's own history key,
            # workspace, policy version and bound set.
            e_payload_ceil = (
                2
                + 5
                + 2
                + _esc_cv
                + 2
                + _scope_esc[_e_base]
                + 2
                + _esc_ogr
                + 2
                + _scope_esc[_e_base + 1]
                + 2
                + _scope_esc[_e_base + 2]
                + 2
                + _scope_set_lens[_e_set]
                + 2 * _scope_set_meta[_e_set][0]
            )
            ttotal.units(
                1
                + 1
                + 2
                * (
                    2 * _scope_set_meta[_e_set][0]
                    + _scope_set_meta[_e_set][2]
                    + _scope_set_meta[_e_set][1]
                )
                + e_payload_ceil
                + 2 * e_payload_ceil
                + 104
                + 1
            )


def _t_parent_witness_compat_actual_owner(
    reserver: _SRegionWorkReserver,
    entry: RootRegionAdmissionEntry,
    occurrences: tuple[Any, ...],
    s_cap: int,
    m_cap: int,
    n_res: int,
    n_pieces_max: int,
    n_mem_entry: int,
) -> None:
    """The 018-t tightened witness region-compatibility billing
    (the cache-root-region-admission/v1 cost law, T-only): the
    SAME target term the default recipe reserves, but the
    owner-domain walks close at the ACTUAL owner population
    (the retained owner proof's segment/member counts and each
    selected segment's member-position count, every one fenced
    under the ACTUAL inherited B caps BEFORE it feeds the term)
    instead of at the configured-cap product.  The state-level
    join terms (the occurrence lookup plus the three original
    coordinate joins, and the owning-result join at the
    precharged retained piece maximum) stay at the recipe's
    closed values; the billing's own fence and index pass is
    charged before it runs; a witness whose owner is absent or
    malformed falls back to the closed cap-based base term (the
    target then refuses with its own fixed private error).
    Over-charges only; every reservation precedes its target."""
    n_w = len(entry.witnesses)
    if n_w == 0:
        return
    # The billing's own occurrence fence/index pass (the closed
    # identity-field existence fence and the owner-index
    # build), reserved BEFORE it walks.
    reserver.reserve(2 * len(occurrences))
    owner_by_id: dict[str, Any] = {}
    for occurrence in occurrences:
        if not _r_fields_present(occurrence, ("occurrence_id", "proof")):
            raise _fixed("the original occurrence must carry its closed identity fields")
        owner_by_id[occurrence.occurrence_id] = occurrence
    # The state-level join terms, closed at the ACTUAL state
    # population (the occurrence lookup plus the three original
    # coordinate joins, and the owning-result join at the
    # precharged retained piece maximum): identical to the
    # default recipe's per-witness terms, plus the billing's
    # own closed O(1) per-witness fence pass (the witness
    # field-existence fence, the coordinate tuple gate and the
    # owner-index get), reserved before the per-witness loop.
    reserver.reserve(n_w * (6 + 5 + 17 + 17 * n_res + 26 * n_pieces_max))
    for witness in entry.witnesses:
        if not _r_fields_present(witness, ("occurrence_id", "segment_indices")):
            raise _fixed("the file witness must carry its original occurrence join fields")
        if not isinstance(witness.segment_indices, tuple):
            raise _fixed("the file witness must carry its closed segment coordinates")
        owner = owner_by_id.get(witness.occurrence_id)
        s_owner = s_cap
        m_owner = m_cap
        if type(owner) is CompletedReadOccurrence and isinstance(owner.proof, BundleProof):
            if isinstance(owner.proof.segments, tuple) and isinstance(
                owner.proof.requested_members, tuple
            ):
                s_owner = min(len(owner.proof.segments), s_cap)
                m_owner = min(len(owner.proof.requested_members), m_cap)
        # The closed owner-domain term at the CLOSED ACTUAL
        # owner population (the retained owner proof's
        # segment/member counts, each fenced under the ACTUAL
        # inherited B caps BEFORE it feeds the product): the
        # fixed O(1) pool (the two 64-hex walks included),
        # the per-owner-segment fences, the owner member
        # closure, the nested member-position walk at the
        # closed actual owner domain and the entry
        # key-occurrence join.  An absent or malformed owner
        # falls back to the closed cap-based base term (the
        # target then refuses with its own fixed private
        # error).
        reserver.reserve(312 + 23 * s_owner + 21 * m_owner + 13 * s_owner * m_owner + n_mem_entry)


def _t_finish(
    outcome: RootRegionAdmissionOutcome,
    state: RootRegionLineageState,
    ns: RootRegionLineageNamespace,
    t_bounds: RootRegionAdmissionBounds,
    g_bounds: CurrentAdmissionBounds,
    r_result: RootRegionGraphResult | None,
    admission: RootRegionAdmission | None,
    diagnostics: tuple[RootRegionAdmissionDiagnostic, ...],
    ttotal: _TOuter,
    g_subtree: _TSubtree,
    g_stage: _GStage | None,
    rtotal: _TRTotal,
    entry_source_bytes: int,
) -> RootRegionAdmissionResult:
    """The charged full-result parent construction for EVERY
    path that reaches result construction: the actual S
    admission-parent re-validation (the READY path only, via the
    versioned S parent precharge component), the consumer
    scope-key pass and the closed full-result build reservation
    all run BEFORE the actual constructor targets.  A T-own
    entire-consumer crossing maps to the fixed work refusal
    retaining every already-returned actual evidence (never a
    usable admission)."""
    if admission is not None and r_result is None:
        raise _fixed("an admission parent is carried only with the actual R READY result")
    scope_key: str | None = None
    try:
        # The closed source-independent carried R joins re-run
        # at the third carrying boundary inside the result
        # constructor (the nested Q/F/E bound/header/scope joins
        # and the outcome invariants -- never the root-body
        # content pass or the READY association walk, which stay
        # on the metered R-derivation and S-parent path).  The
        # constructor re-runs these joins itself BEFORE the
        # phase-5 S parent re-validation, which re-runs the
        # COMPLETE R result law (carried + source) as its own
        # separate actual pass: the T-gate pass is reserved
        # here on EVERY outcome that carries the R result, and
        # the S-parent pass is reserved by the actual S
        # admission-parent precharge below (READY only) -- two
        # real passes, each reserved once, no S reservation
        # spent twice.
        if r_result is not None:
            _t_r_carried_join_precharge(ttotal, r_result)
        if admission is not None and r_result is not None:
            _s_parent_precharge_closed(
                _TMeter(ttotal),
                state,
                ns,
                r_result,
                g_bounds,
                admission.root_entry,
                admission.entries,
                admission.path_associations,
                admission.admission_reasons,
                witness_compat_billing=_t_parent_witness_compat_actual_owner,
            )
        ttotal.units(_T_SCOPE_KEY_UNITS)
        scope_key = root_region_admission_scope_key(
            state.lineage_key,
            ROOT_REGION_ADMISSION_CONTRACT_VERSION,
            ROOT_REGION_ADMISSION_POLICY_VERSION,
            r_result.scope_key if r_result is not None else _T_R_SCOPE_ABSENT,
            admission.scope_key if admission is not None else _T_MODEL_SCOPE_ABSENT,
            CURRENT_ADMISSION_CONTRACT_VERSION,
            CURRENT_ADMISSION_POLICY_VERSION,
            t_bounds,
            g_bounds,
        )
        ttotal.units(_T_RESULT_BUILD_UNITS)
    except _TOverflow:
        # The closed refusal-construction convention: the
        # crossed ledger charges no more, and the REFUSED result
        # carries NO admission -- so the scope key is RECOMPUTED
        # from the actual carried fields (the actual R result
        # with the absence placeholder), never the READY-context
        # key or the non-hex initializer.
        scope_key = None
        return _t_result(
            RootRegionAdmissionOutcome.REFUSED,
            state,
            ns,
            t_bounds,
            g_bounds,
            r_result,
            None,
            (RootRegionAdmissionDiagnostic.WORK_UNITS_OVER_BOUND,),
            ttotal,
            g_subtree,
            g_stage,
            rtotal,
            entry_source_bytes,
            scope_key,
        )
    return _t_result(
        outcome,
        state,
        ns,
        t_bounds,
        g_bounds,
        r_result,
        admission,
        diagnostics,
        ttotal,
        g_subtree,
        g_stage,
        rtotal,
        entry_source_bytes,
        scope_key,
    )


def _t_file_entry_precharge(
    g_subtree: _TSubtree,
    key_record: BundleKeyRecord,
    proof: BundleProof,
    admitted_segments: tuple[int, ...],
    region_chars: int,
    region_bytes: int,
) -> None:
    """The 018-t FILE entry pre-construction seam (the versioned
    S component precharge contracts reserved on the SAME G
    subtree ledger): the canonical-metadata rekey component and
    the FILE admitted-region owned-pass component are reserved
    BEFORE the entry model constructor runs their actual targets
    (the ``cap`` is the ACTUAL inherited single-source BYTE
    ceiling from the key record's closed graph bound set, never
    a work bound; no owned copy, no per-witness source-body
    walk).  The generic G ``_charge_entry_model`` construction
    cost stays charged separately for the constructor itself;
    these component reservations cover the richer S FILE
    validator's actual component re-runs."""
    meter = _TMeter(g_subtree)
    _s_canonical_metadata_precharge_closed(meter, key_record)
    _s_region_precharge_closed(
        meter,
        proof.source_text,
        proof.segments,
        admitted_segments,
        region_chars,
        region_bytes,
        key_record.graph_bounds.max_single_source_bytes,
        key_record.proof_bounds,
    )


def _t_admission(
    state: RootRegionLineageState,
    ns: RootRegionLineageNamespace,
    r_result: RootRegionGraphResult,
    g_bounds: CurrentAdmissionBounds,
    g_subtree: _TSubtree,
    g_stage: _GStage,
) -> tuple[RootRegionAdmission, int]:
    """The actual selected-root-aware G admission assembly (the
    018-t private preconstruction seam): the ACTUAL G generic
    assembly law over the ACTUAL same-run R evidence -- the
    D-namespace re-derivation and its closed joins, the ACTUAL
    018-c admission namespace, the F-node eligibility, the
    SAME-run E owned groups, the required root entry under the
    ACTUAL selected digest (the ACTUAL R resolved source
    retained by immutable reference, one root body, no owned
    copy), the shared FILE assembly core, the complete reverse
    index and the S admission parent.  EVERY unit is charged on
    the SAME G subtree ledger (and the inherited G admission
    stage) BEFORE the crossing work runs; the versioned S
    component precharge contracts reserve the entry / parent
    validator re-runs before their actual targets.  A malformed
    retained record fails closed with the fixed state-malformed
    overflow; the ledgers' own crossings propagate untouched
    (never swallowed by the fail-closed boundary)."""
    resolved = r_result.resolved_source
    f_result = r_result.f_result
    e_overlay = r_result.e_overlay
    if resolved is None or f_result is None or f_result.overlay is None or e_overlay is None:
        raise _GOverflow(CurrentAdmissionLimitation.STATE_MALFORMED)
    selected = resolved.root_digest
    graph = f_result.overlay
    d_state = state.d_state

    # The actual D-namespace re-derivation is a real (re)validation
    # walk: its closed reservation is charged BEFORE it runs (the
    # same actual R recipe), then the history-key join and the
    # closed re-validation fence (unreachable for a genuine R
    # READY; the closed fences are retained, never removed).
    g_subtree.units(2 * (512 + len(ns.workspace) + len(ns.config_fingerprint)))
    d_ns = _region_d_namespace(ns)
    g_subtree.unit()
    if d_state.history_key != d_ns.history_key:
        raise _GOverflow(CurrentAdmissionLimitation.STATE_MALFORMED)
    g_subtree.unit()
    if not _revalidate_ns(d_ns):
        raise _GOverflow(CurrentAdmissionLimitation.STATE_MALFORMED)

    try:
        # --- The charged assembly region (fails closed) ----------
        g_subtree.units(2)
        g_stage.units(2)  # the ONE workspace byte-length measurement
        workspace_bytes = len(d_ns.workspace.encode("utf-8"))
        g_subtree.unit()
        g_stage.unit()
        # The ns already binds the admission fields AND both 64-hex
        # scope keys; constructing the actual 018-c namespace model
        # re-derives both keys from the actual fields, so an
        # incoherent scope is a fixed closed-boundary refusal,
        # never a silent pass.
        try:
            admission_ns = BundleAdmissionNamespace(
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
                namespace_key=d_ns.admission_namespace_key,
                scoped_key=d_ns.admission_scoped_key,
            )
        except Exception:
            raise _GOverflow(CurrentAdmissionLimitation.STATE_MALFORMED) from None

        # --- Eligibility: every F node is root-reachable (depth) -
        eligible: dict[str, int] = {}
        for node in graph.nodes:
            g_subtree.unit()
            g_stage.unit()
            eligible[node.path] = node.depth

        # --- ACTUAL SAME-run E owned groups per occurrence --------
        groups_by_occ: dict[str, list[CurrentnessGroupRecord]] = {}
        for group in e_overlay.groups:
            g_subtree.unit()
            g_stage.unit()
            groups_by_occ.setdefault(group.occurrence_id, []).append(group)

        # --- The required root entry (the SELECTED root is the
        # only supplier; the canonical 018-c recipe reuses the
        # actual namespace byte-for-byte) --------------------------
        # The ACTUAL G root-entry first-over gates (the unchanged
        # G root-entry law): the ACTUAL selected root byte length
        # against the inherited single-source domain and the NEW
        # cumulative entry-source domain, BEFORE any root-entry
        # charge or construction.
        if resolved.root_byte_length > ns.graph_bounds.max_single_source_bytes:
            raise _GOverflow(CurrentAdmissionLimitation.ENTRY_SOURCE_BYTES_OVER_BOUND)
        if resolved.root_byte_length > g_bounds.max_total_entry_source_bytes:
            raise _GOverflow(CurrentAdmissionLimitation.TOTAL_ENTRY_SOURCE_BYTES_OVER_BOUND)
        g_subtree.units(9)
        g_stage.units(9)  # the _v_group pass for the single root group (3k+6)
        groups = (
            OwnershipGroup(
                group_index=0,
                member_occurrence_indices=(0,),
                boundary_class=BoundaryClass.PROVEN,
                group_digest=selected,
            ),
        )
        g_subtree.units(7)
        g_stage.units(7)  # 1 dict + 3 member passes + 1 group + json + hash
        canonical = _key_canonical(
            admission_ns,
            selected,
            EntryClass.ROOT_ENTRY,
            (ROOT_FILENAME,),
            (MemberClass.ELIGIBLE,),
            selected,
            groups,
        )
        content_key = _sha256_hex(canonical)
        g_subtree.units(48)
        g_stage.units(48)  # the key-record construction pass law
        key_record = BundleKeyRecord(
            mode=admission_ns.mode,
            authority_class=EntryClass.ROOT_ENTRY,
            principal=admission_ns.principal,
            session=admission_ns.session,
            repository=admission_ns.repository,
            route=admission_ns.route,
            config_fingerprint=admission_ns.config_fingerprint,
            model_identity=admission_ns.model_identity,
            workspace=admission_ns.workspace,
            root_digest=selected,
            reference_version=admission_ns.reference_version,
            admission_bounds=admission_ns.bounds,
            proof_bounds=admission_ns.proof_bounds,
            graph_bounds=admission_ns.graph_bounds,
            observation_bounds=admission_ns.observation_bounds,
            member_occurrences=(ROOT_FILENAME,),
            member_classes=(MemberClass.ELIGIBLE,),
            aggregate_source_digest=selected,
            ownership_groups=groups,
            content_key=content_key,
        )
        # The versioned S component precharges reserve the entry
        # validator's actual canonical re-derivation and the
        # closed R root content pass BEFORE the constructor runs
        # them.
        _s_canonical_metadata_precharge_closed(_TMeter(g_subtree), key_record)
        _s_root_content_precharge_closed(
            _TMeter(g_subtree),
            resolved.root_text,
            resolved.root_digest,
            resolved.root_byte_length,
        )
        root_entry = RootRegionAdmissionEntry(
            entry_class=EntryClass.ROOT_ENTRY,
            content_key=content_key,
            key_record=key_record,
            width=1,
            member_classes=(MemberClass.ELIGIBLE,),
            root_digest=selected,
            root_source=resolved,
        )

        # --- Shared assembly core (the ACTUAL G generic law) -----
        def _file_precharge(
            key_record: BundleKeyRecord,
            proof: BundleProof,
            admitted_segments: tuple[int, ...],
            region_chars: int,
            region_bytes: int,
        ) -> None:
            _t_file_entry_precharge(
                g_subtree, key_record, proof, admitted_segments, region_chars, region_bytes
            )

        entries, path_keys, attempts, member_occ_charged, total_entry_bytes, diagnostics = (
            _assemble_file_entries(
                d_state,
                d_ns,
                admission_ns,
                selected,
                g_bounds,
                workspace_bytes,
                content_key,
                resolved.root_byte_length,
                groups_by_occ,
                eligible,
                RootRegionAdmissionEntry,
                g_subtree,
                g_stage,
                selected_root_digest=selected,
                precharge_entry=_file_precharge,
            )
        )

        # --- Reverse-index rows (the ACTUAL G typed rows, charged) -
        path_associations: list[CurrentAdmissionPathAssociation] = []
        for path, keys in _sorted(path_keys.items(), lambda item: item[0], g_subtree, g_stage):
            g_subtree.units(1 + 2 * len(keys))
            g_stage.units(1 + 2 * len(keys))
            # 1 row construction + the content-key validator walk +
            # path/scoped/root-flag checks
            path_associations.append(
                CurrentAdmissionPathAssociation(
                    scoped_key=admission_ns.scoped_key,
                    path=path,
                    content_keys=tuple(_sorted(keys, None, g_subtree, g_stage)),
                    is_root=path == ROOT_FILENAME,
                )
            )
        g_subtree.units(len(path_associations))
        g_stage.units(len(path_associations))  # the list-to-tuple copy
        associations = tuple(path_associations)

        # --- Interned file entries, sorted by distinct content key -
        sorted_keys = _sorted(entries, None, g_subtree, g_stage)
        g_subtree.units(len(sorted_keys))
        g_stage.units(len(sorted_keys))  # the interned entry reference copies
        file_entries = tuple(entries[key] for key in sorted_keys)

        # --- The S-model scope key (the closed pass reservation) --
        g_subtree.units(_T_S_SCOPE_KEY_UNITS)
        g_stage.units(_T_S_SCOPE_KEY_UNITS)
        scope_key = root_region_admission_model_scope_key(
            state.lineage_key,
            ROOT_REGION_ADMISSION_MODELS_CONTRACT_VERSION,
            ROOT_REGION_ADMISSION_MODELS_POLICY_VERSION,
            r_result.scope_key,
            CURRENT_ADMISSION_CONTRACT_VERSION,
            CURRENT_ADMISSION_POLICY_VERSION,
            g_bounds,
        )

        # --- The S admission parent (the ACTUAL complete parent
        # law re-run at construction, reserved by the actual S
        # parent precharge component BEFORE it runs) --------------
        _s_parent_precharge_closed(
            _TMeter(g_subtree),
            state,
            ns,
            r_result,
            g_bounds,
            root_entry,
            file_entries,
            associations,
            tuple(diagnostics),
            witness_compat_billing=_t_parent_witness_compat_actual_owner,
        )
        parent = RootRegionAdmission(
            state=state,
            ns=ns,
            r_result=r_result,
            g_bounds=g_bounds,
            root_entry=root_entry,
            entries=file_entries,
            path_associations=associations,
            scope_key=scope_key,
            entries_retained=1 + len(file_entries),
            member_occurrences_charged=member_occ_charged,
            reverse_association_attempts=attempts,
            emitted_admission_reasons=len(diagnostics),
            admission_reasons=tuple(diagnostics),
        )
        return parent, total_entry_bytes
    except _Malformed:
        raise _GOverflow(CurrentAdmissionLimitation.STATE_MALFORMED) from None
    except (ValidationError, ValueError, TypeError, KeyError, IndexError, AttributeError):
        raise _GOverflow(CurrentAdmissionLimitation.STATE_MALFORMED) from None


def _t_ready(
    state: RootRegionLineageState,
    ns: RootRegionLineageNamespace,
    t_bounds: RootRegionAdmissionBounds,
    g_bounds: CurrentAdmissionBounds,
    r_result: RootRegionGraphResult,
    ttotal: _TOuter,
    g_subtree: _TSubtree,
    rtotal: _TRTotal,
) -> RootRegionAdmissionResult:
    """The READY path: the actual selected-root-aware G assembly
    (the SAME G subtree ledger; the ACTUAL inherited G admission
    stage domain), then the charged full-result third parent.
    Every crossing maps to the fixed typed refusal retaining the
    actual R result as bounded evidence (never a usable
    admission)."""
    g_stage = _GStage(ns.graph_bounds)
    try:
        parent, entry_source_bytes = _t_admission(state, ns, r_result, g_bounds, g_subtree, g_stage)
    except _TOverflow:
        return _t_result(
            RootRegionAdmissionOutcome.REFUSED,
            state,
            ns,
            t_bounds,
            g_bounds,
            r_result,
            None,
            (RootRegionAdmissionDiagnostic.WORK_UNITS_OVER_BOUND,),
            ttotal,
            g_subtree,
            g_stage,
            rtotal,
            0,
        )
    except _GOverflow as overflow:
        diagnostic = (
            RootRegionAdmissionDiagnostic.ADMISSION_STATE_MALFORMED
            if overflow.limitation is CurrentAdmissionLimitation.STATE_MALFORMED
            else RootRegionAdmissionDiagnostic.ADMISSION_OVER_BOUND
        )
        return _t_result(
            RootRegionAdmissionOutcome.REFUSED,
            state,
            ns,
            t_bounds,
            g_bounds,
            r_result,
            None,
            (diagnostic,),
            ttotal,
            g_subtree,
            g_stage,
            rtotal,
            0,
            None,
            overflow.limitation,
        )
    return _t_finish(
        RootRegionAdmissionOutcome.READY,
        state,
        ns,
        t_bounds,
        g_bounds,
        r_result,
        parent,
        (),
        ttotal,
        g_subtree,
        g_stage,
        rtotal,
        entry_source_bytes,
    )


def _t_ns_fence_failed(ns: RootRegionLineageNamespace, state: RootRegionLineageState) -> bool:
    """The closed O(1) namespace fence predicate (the unchanged Q
    law PLUS the T-own exact lineage join), safe on ANY object:
    the closed field-existence fence short-circuits the value
    fences, and the lineage read is reachable only on the joined
    class.  Re-runnable uncharged under the closed refusal-
    construction convention when a crossing hit BEFORE the fence
    itself ran (the legal cap just above the base charge)."""
    return (
        not _q_ns_boundary_ok(ns)
        or not _region_preflight_ns_shape(ns)
        or not _r_graph_version_ok(ns.graph_version)
        or ns.lineage_key != state.lineage_key
    )


def derive_root_region_admission(
    state: RootRegionLineageState,
    ns: RootRegionLineageNamespace,
    bounds: RootRegionAdmissionBounds | None = None,
    *,
    root_region_graph_bounds: RootRegionGraphBounds | None = None,
    root_region_currentness_bounds: RootRegionCurrentnessBounds | None = None,
    current_graph_bounds: CurrentGraphBounds | None = None,
    nonroot_currentness_bounds: CurrentnessBounds | None = None,
    admission_bounds: CurrentAdmissionBounds | None = None,
) -> RootRegionAdmissionResult:
    """The ONE bounded pure complete root-region admission
    consumer (018-t).

    Takes the ACTUAL retained P root-region lineage state and
    namespace (plus the NEW consumer bounds and the explicit
    inherited derivation/admission bounds; defaults when
    omitted).  The input is the ACTUAL public P boundary, never
    a caller-positive R/Q/F/graph/admission snapshot or
    verification flag: object construction is not authentication.

    In ONE entire charged operation the operation derives ACTUAL
    R (including the ACTUAL same-run Q currentness, the selected
    root source and the ACTUAL F/E current graph) EXACTLY ONCE
    through the narrow typed R-core seam, then the ACTUAL
    selected-root-aware G admission assembly (the SAME G
    subtree ledger that the F phase charged), then the complete
    full-result third carrying boundary.  See the module
    docstring for the versioned ledger law.

    Outcomes: READY (actual R READY AND completed actual
    admission AND full-result checks -- never readiness of any
    kind beyond that); root_currentness_unproven /
    root_authority_conflict (the ACTUAL same-run R positive-
    interpretation outcomes mapped from the actual Q channel,
    the actual R result retained, no usable admission, no
    bootstrap fallback); refused (the fixed typed consumer
    failure -- an early T gate, a T-level work crossing, a
    mapped R refusal or an actual G-subtree/admission-domain
    refusal -- with every already-returned actual evidence
    retained and no usable admission or bootstrap fallback).

    The exact input state (with its actual carried revision and
    lineage key) is retained on EVERY valid-input outcome.  All
    inherited public hard ceilings remain unchanged and
    independently binding.  The operation is INERT: no runtime,
    HTTP, model, service or persistent state of any kind.
    """
    # --- O(1) state fence (the unchanged Q law, reused) ----------
    if not _q_state_boundary_ok(state) or not _region_state_shape(state):
        raise _fixed("the region lineage state must carry an actual bounded state record")

    # --- O(1) bootstrap: the closed shape fences and closed cap
    # reads that size the ledgers (NO model construction, NO
    # serializer visit; the actual defaults on any
    # malformed/unusable candidate) -------------------------------
    t_shape_ok = bounds is not None and root_region_admission_bounds_shape_ok(bounds)
    g_shape_ok = admission_bounds is not None and _s_g_bounds_closed(admission_bounds)
    f_shape_ok = current_graph_bounds is not None and _f_bounds_shape_ok(current_graph_bounds)
    r_shape_ok = root_region_graph_bounds is not None and root_region_graph_bounds_shape_ok(
        root_region_graph_bounds
    )
    t_cap = bounds.max_total_work_units if bounds is not None and t_shape_ok else _HARD_T_WORK_UNITS
    g_work_cap = (
        admission_bounds.max_total_work_units
        if admission_bounds is not None and g_shape_ok
        else CurrentAdmissionBounds.model_fields["max_total_work_units"].default
    )
    g_diag_cap = (
        admission_bounds.max_diagnostics
        if admission_bounds is not None and g_shape_ok
        else CurrentAdmissionBounds.model_fields["max_diagnostics"].default
    )
    f_work_cap = (
        current_graph_bounds.max_total_work_units
        if current_graph_bounds is not None and f_shape_ok
        else CurrentGraphBounds.model_fields["max_total_work_units"].default
    )
    f_diag_cap = (
        current_graph_bounds.max_diagnostics
        if current_graph_bounds is not None and f_shape_ok
        else CurrentGraphBounds.model_fields["max_diagnostics"].default
    )
    r_cap = (
        root_region_graph_bounds.max_total_work_units
        if root_region_graph_bounds is not None and r_shape_ok
        else RootRegionGraphBounds.model_fields["max_total_work_units"].default
    )
    # The resolved bound models (constructed AFTER the ledgers,
    # reserved BEFORE they run) carry exactly these caps; the
    # closed O(1) reads above are the only pre-ledger work.

    # --- The ledgers (the entire outer BEFORE any serializer/
    # constructor target; the closed early-pass reservation) -----
    ttotal = _TOuter(t_cap)
    g_subtree = _TSubtree(f_work_cap, f_diag_cap, g_work_cap, g_diag_cap, ttotal)
    rtotal = _TRTotal(ttotal, r_cap)
    try:
        ttotal.units(_T_BASE_UNITS)
    except _TOverflow:
        # The closed refusal-construction convention on the full
        # ledger: the resolved bound models and the scope key are
        # the fixed closed recipe, unchargeable by definition.
        t_bounds, _ = _t_resolve_t_bounds(ttotal, t_shape_ok, bounds, False)
        g_bounds, _ = _t_resolve_g_bounds(ttotal, g_shape_ok, admission_bounds, False)
        # The namespace fence has NOT run yet on this path, so
        # the closed O(1) predicate is re-run uncharged: an
        # unjoined or foreign namespace keeps the exact
        # foreign-scope shape the carrying boundary accepts, a
        # joined one names the work domain.
        if _t_ns_fence_failed(ns, state):
            return _t_early_refuse(
                state,
                ns,
                t_bounds,
                g_bounds,
                RootRegionAdmissionDiagnostic.FOREIGN_SCOPE,
                ttotal,
                g_subtree,
                rtotal,
            )
        return _t_result(
            RootRegionAdmissionOutcome.REFUSED,
            state,
            ns,
            t_bounds,
            g_bounds,
            None,
            None,
            (RootRegionAdmissionDiagnostic.WORK_UNITS_OVER_BOUND,),
            ttotal,
            g_subtree,
            None,
            rtotal,
            0,
        )

    # --- O(1) namespace fence under the ledger (the unchanged Q
    # law PLUS the T-own exact lineage join; the closed fence
    # pass is charged before it runs) AND the closed consumer
    # bound resolution (the ACTUAL serializer/constructor targets
    # -- default construction or model_dump + model_validate
    # re-resolution -- reserved BEFORE they run; the NEW hard
    # ceilings, stricter positives legal).  A T-own entire-
    # consumer crossing in these closed bootstrap passes (the
    # legal cap just above the base charge) maps to the fixed
    # work refusal under the closed refusal-construction
    # convention (the crossed ledger charges no more; the bound
    # models are the fixed closed recipe, unchargeable by
    # definition) -- never a leaked internal overflow.
    try:
        ttotal.units(_T_NS_FENCE_UNITS)
        if _t_ns_fence_failed(ns, state):
            t_bounds, _ = _t_resolve_t_bounds(ttotal, t_shape_ok, bounds, True)
            g_bounds, _ = _t_resolve_g_bounds(ttotal, g_shape_ok, admission_bounds, True)
            return _t_early_refuse(
                state,
                ns,
                t_bounds,
                g_bounds,
                RootRegionAdmissionDiagnostic.FOREIGN_SCOPE,
                ttotal,
                g_subtree,
                rtotal,
            )
        t_bounds, t_malformed = _t_resolve_t_bounds(ttotal, t_shape_ok, bounds, True)
        if t_malformed:
            g_bounds, _g_malformed = _t_resolve_g_bounds(ttotal, g_shape_ok, admission_bounds, True)
            return _t_early_refuse(
                state,
                ns,
                t_bounds,
                g_bounds,
                RootRegionAdmissionDiagnostic.MALFORMED_BINDING,
                ttotal,
                g_subtree,
                rtotal,
            )
        g_bounds, g_malformed = _t_resolve_g_bounds(ttotal, g_shape_ok, admission_bounds, True)
        if g_malformed:
            return _t_early_refuse(
                state,
                ns,
                t_bounds,
                g_bounds,
                RootRegionAdmissionDiagnostic.MALFORMED_BINDING,
                ttotal,
                g_subtree,
                rtotal,
            )
    except _TOverflow:
        t_bounds, _ = _t_resolve_t_bounds(ttotal, t_shape_ok, bounds, False)
        g_bounds, _ = _t_resolve_g_bounds(ttotal, g_shape_ok, admission_bounds, False)
        # The fence has not necessarily RUN when the crossing hit
        # the fence charge: re-run the closed O(1) predicate
        # uncharged so the produced refusal carries the exact
        # diagnostic the carrying boundary accepts for this pair
        # (an unjoined/foreign namespace keeps the fixed
        # foreign-scope shape; a joined one names the work
        # domain).
        if _t_ns_fence_failed(ns, state):
            return _t_early_refuse(
                state,
                ns,
                t_bounds,
                g_bounds,
                RootRegionAdmissionDiagnostic.FOREIGN_SCOPE,
                ttotal,
                g_subtree,
                rtotal,
            )
        return _t_result(
            RootRegionAdmissionOutcome.REFUSED,
            state,
            ns,
            t_bounds,
            g_bounds,
            None,
            None,
            (RootRegionAdmissionDiagnostic.WORK_UNITS_OVER_BOUND,),
            ttotal,
            g_subtree,
            None,
            rtotal,
            0,
        )

    # --- ACTUAL R derivation ONCE (every actual unit coupled into
    # the entire outer BEFORE the crossing work runs; the SAME G
    # subtree ledger that the admission phase uses is the F-phase
    # coupling target) ----------------------------------------------
    try:
        g_subtree.begin_f()
        r_result = _derive_root_region_graph_core(
            state,
            ns,
            root_region_graph_bounds,
            root_region_currentness_bounds=root_region_currentness_bounds,
            current_graph_bounds=current_graph_bounds,
            nonroot_currentness_bounds=nonroot_currentness_bounds,
            rtotal=rtotal,
            f_g_ledger=g_subtree,
        )
    except _TOverflow:
        return _t_result(
            RootRegionAdmissionOutcome.REFUSED,
            state,
            ns,
            t_bounds,
            g_bounds,
            None,
            None,
            (RootRegionAdmissionDiagnostic.WORK_UNITS_OVER_BOUND,),
            ttotal,
            g_subtree,
            None,
            rtotal,
            0,
        )
    except _GOverflow as overflow:
        diagnostic = (
            RootRegionAdmissionDiagnostic.ADMISSION_STATE_MALFORMED
            if overflow.limitation is CurrentAdmissionLimitation.STATE_MALFORMED
            else RootRegionAdmissionDiagnostic.ADMISSION_OVER_BOUND
        )
        return _t_result(
            RootRegionAdmissionOutcome.REFUSED,
            state,
            ns,
            t_bounds,
            g_bounds,
            None,
            None,
            (diagnostic,),
            ttotal,
            g_subtree,
            None,
            rtotal,
            0,
            None,
            overflow.limitation,
        )
    finally:
        g_subtree.end_f()

    # --- Outcome mapping (the ACTUAL R result retained on EVERY
    # later outcome) ---------------------------------------------------
    if r_result.outcome is RootRegionGraphOutcome.READY:
        return _t_ready(state, ns, t_bounds, g_bounds, r_result, ttotal, g_subtree, rtotal)
    if r_result.outcome is RootRegionGraphOutcome.ROOT_CURRENTNESS_UNPROVEN:
        return _t_finish(
            RootRegionAdmissionOutcome.ROOT_CURRENTNESS_UNPROVEN,
            state,
            ns,
            t_bounds,
            g_bounds,
            r_result,
            None,
            (),
            ttotal,
            g_subtree,
            None,
            rtotal,
            0,
        )
    if r_result.outcome is RootRegionGraphOutcome.ROOT_AUTHORITY_CONFLICT:
        return _t_finish(
            RootRegionAdmissionOutcome.ROOT_AUTHORITY_CONFLICT,
            state,
            ns,
            t_bounds,
            g_bounds,
            r_result,
            None,
            (),
            ttotal,
            g_subtree,
            None,
            rtotal,
            0,
        )
    diagnostics = tuple(_R_DIAGNOSTIC_MAP[d.value] for d in r_result.diagnostics)
    return _t_finish(
        RootRegionAdmissionOutcome.REFUSED,
        state,
        ns,
        t_bounds,
        g_bounds,
        r_result,
        None,
        diagnostics,
        ttotal,
        g_subtree,
        None,
        rtotal,
        0,
    )

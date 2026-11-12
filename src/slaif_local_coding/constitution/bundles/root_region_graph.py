"""Pure versioned selected-root-region source + current-graph
derivation (objective 018-r).

``derive_root_region_graph`` is the ONE bounded pure CONSUMER above
the accepted 018-p root-region producer and the 018-q root-region
currentness query: it derives the ACTUAL Q currentness from the
ACTUAL P state in the SAME charged run (the accepted private
shared-ledger Q seam -- no second full public Q/P call under reset
fuel, no pre-reserved whole cap, no global minimum), resolves the
ACTUAL selected envelope / whole-read / mixed-region root source
from the SAME retained state (charged preflights before any owned
slice/encode/hash/copy; character sums, never UTF-8 byte lengths or
carrier offsets; markers excluded; CRLF/Unicode/empty root
preserved; the original ``proof.root_digest`` stays bound to the
immutable bootstrap scope), and derives the ACTUAL accepted F/E
current graph under that selected root through the accepted F
selected-root private seam (fresh least fixed point under the
selected digest, never snapshot-seeded; the selected root is the
ONLY root-text supplier; the actual E currentness/ownership law
preserved).

ONE R outer covers the ENTIRE operation (early gates, bound
resolutions, the actual Q/P/D work, the original source/
provenance resolution, the actual F/E and graph-stage work, and
all association/serialization/construction reservations), while
every nested domain stays independently binding: the ACTUAL Q-local
counter couples every actual unit (its independently bounded P
phase included) into the ONE R total, and the ACTUAL F outer plus
graph-stage ledger do the same (the accepted composition law -- no
ledger reset between stages).  A nested-domain crossing maps to
the ACTUAL nested refusal (retained by reference); an R-total
crossing before R's own result returned publishes NO partial
positive source/graph and retains whatever ACTUAL nested evidence
was already computed with exactly the own work-overflow
diagnostic.

Refusal precedence (explicit and fixed): O(1) state/namespace/
bounds fences (a malformed non-P state fails with a fixed private
ValueError BEFORE result construction; every effective bound set
follows the closed private shape/refusal boundaries with the
default domain); the ACTUAL Q phase under the ONE R total (its
actual independent P domain included); the mapped Q unproven /
authority-conflict / refusal BEFORE any source slicing or F
derivation; the charged selected-source resolution (a fixed typed
source-resolution refusal, no partial source); the actual F/E
phase under its ACTUAL independent F outer and graph-stage ledger
(the D-namespace revalidation fences mirrored); then the READY
result construction.  Closed O(1) counts/scalars precede
element/set/sort/hash/serialization work; candidate attempts count
before dedup; source preflights precede owned copies/encodes/
hashes without a per-witness full original source walk.

The result retains the EXACT input P state by reference on EVERY
outcome, the ACTUAL same-run Q result once returned, and the
ACTUAL F result plus its SAME-run E overlay when returned, without
rederiving under reset fuel or copying full histories.  A
malformed input scope or bounds characterizes the derivation with
the default domain (the unusable input is never partially
trusted).  The query never advances a revision, never mints a root
authority fact and never copies source beyond the ONE
materialized root body.
"""

from __future__ import annotations

from typing import Literal

from . import currentness as _currentness
from .causal_history_models import CausalHistoryState
from .current_graph import (
    _derive_graph,
    _Malformed,
    _OuterLedger,
    _OuterOverflow,
    _refuse,
    _StageLedger,
    _StageOverflow,
)
from .current_graph_models import (
    CurrentGraphBounds,
    CurrentGraphLimitation,
    CurrentGraphOutcome,
    CurrentGraphResult,
)
from .currentness_models import CurrentnessBounds, CurrentnessOverlay
from .graph_models import ROOT_FILENAME, _fixed, _sha256_hex
from .root_lineage_models import EnvelopeRootProvenance, ReadRootProvenance
from .root_region_currentness import (
    _derive_root_region_currentness_core,
    _q_ns_boundary_ok,
    _q_state_boundary_ok,
    _QOuter,
)
from .root_region_currentness_models import (
    ROOT_REGION_CURRENTNESS_CONTRACT_VERSION,
    ROOT_REGION_CURRENTNESS_POLICY_VERSION,
    RootRegionCurrentnessBounds,
    RootRegionCurrentnessOutcome,
    RootRegionCurrentnessResult,
    root_region_currentness_scope_key,
)
from .root_region_graph_models import (
    _R_REJECTION_GRAPH_VERSION,
    ROOT_REGION_GRAPH_CONTRACT_VERSION,
    ROOT_REGION_GRAPH_POLICY_VERSION,
    ResolvedRootRegionSource,
    RootRegionGraphBounds,
    RootRegionGraphDiagnostic,
    RootRegionGraphOutcome,
    RootRegionGraphResult,
    _r_graph_version_ok,
    _r_q_bounds_closed,
    _r_utf8_byte_length_capped,
    root_region_graph_bounds_shape_ok,
    root_region_graph_scope_key,
)
from .root_region_lineage import (
    _region_d_namespace,
    _region_preflight_ns_shape,
    _region_state_shape,
)
from .root_region_lineage_models import (
    RootRegionLineageNamespace,
    RootRegionLineageState,
    RootRegionReadProvenance,
    RootRegionSelectionResult,
    _region_provenance_key,
)

#: Fixed R base charge: the early gates, the four bound
#: resolutions, the two scope-key recomputations and the ledger
#: construction BEFORE the first positive work.
_R_BASE_UNITS = 24
#: One charged R result construction (fixed base + retained
#: reference joins, charged BEFORE the record builds).
_R_RESULT_BUILD_UNITS = 16
#: One charged witness source-resolution attempt (identity
#: membership + provenance key + dispatch, charged BEFORE the
#: work).
_R_WITNESS_ATTEMPT_UNITS = 12


def _r_source_pass_units(root_text: str, byte_length: int) -> int:
    """Honest reservation for ONE actual content pass over the root
    body: the no-copy capped UTF-8 measurement (one unit per
    ACTUAL character), the owned encode (one unit per ACTUAL byte)
    and the sha256 digest recheck (one unit per ACTUAL byte) --
    every real char/byte pass on the SAME R total domain as the
    actual Q/P/F work, never divided, renamed or amortized away."""
    return len(root_text) + 2 * byte_length


class _ROverflow(Exception):
    """The ONE R outer crossed: a fixed private resource fact.

    The public derivation maps it to the typed atomic over-bound
    refusal preserving the EXACT prior state and whatever actual
    nested evidence was already computed."""

    __slots__ = ()


class _RSourceError(Exception):
    """The charged selected-source resolution failed a closed join
    or preflight: a fixed private typed source failure (the public
    derivation maps it to the fixed source-resolution refusal with
    no partial source)."""

    __slots__ = ()


class _ROuter:
    """ONE R outer work ledger over the ENTIRE derivation.

    Charges EVERY unit of the whole operation against the ACTUAL
    ``max_total_work_units`` BEFORE the crossing work runs;
    cumulative and NEVER reset.  A crossing raises the fixed
    private overflow (the caller maps it)."""

    __slots__ = ("work_cap", "work_spent")

    def __init__(self, work_cap: int) -> None:
        self.work_cap = work_cap
        self.work_spent = 0

    def unit(self) -> bool:
        if self.work_spent + 1 > self.work_cap:
            raise _ROverflow()
        self.work_spent += 1
        return True

    def units(self, n: int) -> None:
        for _ in range(n):
            self.unit()


class _RQOuter(_QOuter):
    """The Q-phase coupling adapter: the ACTUAL Q-local ledger
    (INDEPENDENT ceiling from the ACTUAL Q bounds) AND the ONE R
    total on every unit (the accepted composition law -- the R
    total is NOT pre-reserved by the Q ceiling; the ACTUAL Q units
    flow through, the actual independently bounded P phase
    included through the accepted ``_QPAdapter``).  A Q-local
    crossing raises the fixed private Q overflow (mapped by the Q
    core itself); an R-total crossing raises the fixed private R
    overflow (mapped by this derivation)."""

    __slots__ = ("rtotal",)

    def __init__(self, rtotal: _ROuter, work_cap: int) -> None:
        super().__init__(work_cap)
        self.rtotal = rtotal

    def unit(self) -> bool:
        super().unit()  # Q domain first (raises _QOverflow)
        self.rtotal.unit()  # R total (raises _ROverflow)
        return True


class _RFOuter(_OuterLedger):
    """The F-phase coupling adapter: the ACTUAL F outer (INDEPENDENT
    ceiling from the ACTUAL F bounds, its own diagnostic domain
    unchanged) AND the ONE R total on every unit (the accepted
    composition law -- the R total is NOT pre-reserved by the F
    ceiling; the ACTUAL F units flow through, the actual E
    derivation included through the ``charge`` view).  A F-domain
    crossing raises the fixed private F overflow (mapped to the
    ACTUAL F refusal); an R-total crossing raises the fixed private
    R overflow (mapped by this derivation)."""

    __slots__ = ("rtotal",)

    def __init__(self, rtotal: _ROuter, bounds: CurrentGraphBounds) -> None:
        super().__init__(bounds)
        self.rtotal = rtotal

    def unit(self) -> bool:
        super().unit()  # F domain first (raises _OuterOverflow)
        self.rtotal.unit()  # R total (raises _ROverflow)
        return True


def _f_bounds_shape_ok(bounds: object) -> bool:
    """R-PRIVATE closed fence over the actual F bound set (the R
    consumer's own preflight boundary; the F public law is
    unchanged): field existence, exact non-bool ints, actual F
    hard ceilings, BEFORE any serializer visit."""
    from .root_region_graph_models import (
        _HARD_F_DIAGNOSTICS,
        _HARD_F_WORK_UNITS,
        _r_int_in,
    )

    return (
        isinstance(bounds, CurrentGraphBounds)
        and hasattr(bounds, "max_total_work_units")
        and hasattr(bounds, "max_diagnostics")
        and _r_int_in(bounds.max_total_work_units, 1, _HARD_F_WORK_UNITS)
        and _r_int_in(bounds.max_diagnostics, 1, _HARD_F_DIAGNOSTICS)
    )


def _e_bounds_shape_ok(bounds: object) -> bool:
    """R-PRIVATE closed fence over the actual E bound set (the R
    consumer's own preflight boundary; the E public law is
    unchanged): field existence, exact non-bool ints, actual E
    hard ceilings, BEFORE any serializer visit."""
    from .root_region_graph_models import (
        _HARD_E_DIAGNOSTICS,
        _HARD_E_GROUPS,
        _HARD_E_PATHS,
        _HARD_E_RELATION_PAIRS,
        _HARD_E_WITNESS_MEMBERSHIPS,
        _HARD_E_WORK_UNITS,
        _r_int_in,
    )

    return (
        isinstance(bounds, CurrentnessBounds)
        and hasattr(bounds, "max_paths")
        and hasattr(bounds, "max_groups")
        and hasattr(bounds, "max_witness_memberships")
        and hasattr(bounds, "max_relation_pairs")
        and hasattr(bounds, "max_work_units")
        and hasattr(bounds, "max_diagnostics")
        and _r_int_in(bounds.max_paths, 1, _HARD_E_PATHS)
        and _r_int_in(bounds.max_groups, 1, _HARD_E_GROUPS)
        and _r_int_in(bounds.max_witness_memberships, 1, _HARD_E_WITNESS_MEMBERSHIPS)
        and _r_int_in(bounds.max_relation_pairs, 1, _HARD_E_RELATION_PAIRS)
        and _r_int_in(bounds.max_work_units, 1, _HARD_E_WORK_UNITS)
        and _r_int_in(bounds.max_diagnostics, 1, _HARD_E_DIAGNOSTICS)
    )


def _r_resolve_source(
    state: RootRegionLineageState,
    p_sel: RootRegionSelectionResult,
    rtotal: _ROuter,
) -> ResolvedRootRegionSource:
    """The charged selected-source resolution (ONE R total).

    The deterministic FIRST compatible witness in the actual
    canonical witness order is materialized: the selected fact is
    joined to the SAME input state's actual ``root_facts`` by
    identity; the original selected occurrence to the SAME D
    occurrence (membership width precharged, then charged walk);
    the complete owning proof / segment / member coordinates to
    the SAME original objects; the root interval from sums of
    preceding original segment CHARACTER lengths (never UTF-8 byte
    lengths or carrier offsets); byte/character preflights BEFORE
    any owned slice/encode/hash/copy; the digest rechecked from the
    ONE owned encode against the ACTUAL retained provenance
    binding (a repeated integrity check, charged -- the bootstrap
    ``proof.root_digest`` stays bound to the immutable scope).
    Any closed join/preflight failure is the fixed private source
    error (no partial source, no echo of a stored flag)."""
    d_state = state.d_state
    fact = p_sel.witness_facts[0]
    rtotal.units(_R_WITNESS_ATTEMPT_UNITS)
    # Identity-membership width BEFORE the any-loop traversal.
    rtotal.units(len(state.root_facts))
    if not any(f is fact for f in state.root_facts):
        raise _RSourceError()
    kind, occurrence_id = _region_provenance_key(fact.provenance)
    rtotal.unit()
    if (
        not isinstance(fact.source_digest, str)
        or not isinstance(fact.source_byte_length, int)
        or isinstance(fact.source_byte_length, bool)
    ):
        raise _RSourceError()
    if kind == "envelope":
        rtotal.unit()
        anchor = d_state.root
        if anchor is None:
            raise _RSourceError()
        prov = fact.provenance
        rtotal.unit()
        if not isinstance(prov, EnvelopeRootProvenance):
            raise _RSourceError()
        if (
            prov.root_digest != anchor.root_digest
            or prov.workspace != anchor.workspace
            or prov.source_byte_length != anchor.source_byte_length
            or fact.source_digest != anchor.root_digest
            or fact.source_byte_length != anchor.source_byte_length
        ):
            raise _RSourceError()
        rtotal.unit()
        if not isinstance(anchor.root_text, str):
            raise _RSourceError()
        root_text = anchor.root_text
        byte_length = fact.source_byte_length
    else:
        # Charged occurrence lookup by the actual occurrence ID
        # (membership width precharged BEFORE the charged walk).
        rtotal.units(1 + len(d_state.occurrences))
        occurrence = None
        for candidate in d_state.occurrences:
            rtotal.unit()
            if candidate.occurrence_id == occurrence_id:
                occurrence = candidate
                break
        if occurrence is None:
            raise _RSourceError()
        proof = occurrence.proof
        rtotal.unit()
        prov = fact.provenance
        if not isinstance(prov, (ReadRootProvenance, RootRegionReadProvenance)):
            raise _RSourceError()
        if (
            prov.call_id != occurrence.call_id
            or prov.endpoint != occurrence.endpoint
            or not isinstance(proof.source_digest, str)
            or not isinstance(proof.source_text, str)
        ):
            raise _RSourceError()
        if kind == "read":
            rtotal.unit()
            if not isinstance(prov, ReadRootProvenance):
                raise _RSourceError()
            if (
                prov.read_digest != proof.source_digest
                or prov.read_byte_length != proof.source_byte_length
                or proof.root_path != ROOT_FILENAME
                or prov.read_digest != fact.source_digest
            ):
                raise _RSourceError()
            root_text = proof.source_text
            byte_length = prov.read_byte_length
        else:
            rtotal.unit()
            if not isinstance(prov, RootRegionReadProvenance):
                raise _RSourceError()
            if (
                prov.whole_proof_digest != proof.source_digest
                or prov.whole_proof_byte_length != proof.source_byte_length
                or prov.root_member_digest != fact.source_digest
            ):
                raise _RSourceError()
            segments = proof.segments
            rtotal.unit()
            if prov.root_segment_index >= len(segments):
                raise _RSourceError()
            # Charged preceding-segment CHARACTER sum (the root
            # interval start: character lengths, never byte
            # lengths or carrier offsets).
            rtotal.units(prov.root_segment_index)
            start = 0
            for position in range(prov.root_segment_index):
                rtotal.unit()
                start += segments[position].char_length
            segment = segments[prov.root_segment_index]
            rtotal.unit()
            if (
                segment.index != prov.root_segment_index
                or segment.member_digest is None
                or segment.member_digest != prov.root_member_digest
            ):
                raise _RSourceError()
            rtotal.units(1 + len(segment.member_positions))
            if prov.root_member_position not in segment.member_positions:
                raise _RSourceError()
            char_length = segment.char_length
            end = start + char_length
            rtotal.unit()
            # O(1) preflights BEFORE the owned slice: the interval
            # stays inside the actual aggregate source text and
            # bytes are never fewer than characters.
            if (
                end > len(proof.source_text)
                or prov.root_member_byte_length < char_length
                or prov.root_member_byte_length > 16777216
            ):
                raise _RSourceError()
            # The owned slice copy width is reserved BEFORE the
            # copy.
            rtotal.units(char_length)
            root_text = proof.source_text[start:end]
            byte_length = prov.root_member_byte_length
    # Charged content verification: the no-copy capped UTF-8
    # measurement (one unit per ACTUAL character, width
    # precharged with the pass) runs BEFORE any owned encode; the
    # owned encode and the sha256 recheck are charged per ACTUAL
    # byte BEFORE the work; the digest must equal the ACTUAL
    # selected source (the fact root body == the provenance
    # binding, joined above).
    rtotal.units(_r_source_pass_units(root_text, byte_length))
    measured = _r_utf8_byte_length_capped(root_text, byte_length)
    if measured != byte_length:
        raise _RSourceError()
    try:
        actual = root_text.encode("utf-8")
    except UnicodeEncodeError:
        raise _RSourceError() from None
    if len(actual) != byte_length or _sha256_hex(actual) != fact.source_digest:
        raise _RSourceError()
    # The record constructor re-executes the closed content law
    # over the record's own root text (walk + encode + hash):
    # reserve that ACTUAL pass BEFORE the constructor work.
    rtotal.units(_R_RESULT_BUILD_UNITS + _r_source_pass_units(root_text, byte_length))
    if kind == "envelope":
        return ResolvedRootRegionSource(
            kind="envelope",
            fact=fact,
            root_text=root_text,
            root_digest=fact.source_digest,
            root_byte_length=byte_length,
        )
    kind_tag: Literal["read", "read_region"]
    if kind == "read":
        kind_tag = "read"
    else:
        kind_tag = "read_region"
    return ResolvedRootRegionSource(
        kind=kind_tag,
        fact=fact,
        root_text=root_text,
        root_digest=fact.source_digest,
        root_byte_length=byte_length,
        occurrence=occurrence,
        proof=proof,
    )


def _r_result(
    state: RootRegionLineageState,
    r_bounds: RootRegionGraphBounds,
    q_bounds: RootRegionCurrentnessBounds,
    f_bounds: CurrentGraphBounds,
    e_bounds: CurrentnessBounds,
    graph_version: str,
    r_scope_key: str,
    outcome: RootRegionGraphOutcome,
    diagnostics: tuple[RootRegionGraphDiagnostic, ...],
    q_result: RootRegionCurrentnessResult | None = None,
    f_result: CurrentGraphResult | None = None,
    e_overlay: CurrentnessOverlay | None = None,
    resolved_source: ResolvedRootRegionSource | None = None,
) -> RootRegionGraphResult:
    """The closed R result construction (charged by the caller; the
    precomputed scope key is passed in -- the single scope-key
    computation happens once under the charged base, and the result
    constructor re-verifies it under its own reserved build work)."""
    return RootRegionGraphResult(
        outcome=outcome,
        state=state,
        q_result=q_result,
        f_result=f_result,
        e_overlay=e_overlay,
        resolved_source=resolved_source,
        diagnostics=diagnostics,
        bounds=r_bounds,
        q_bounds=q_bounds,
        f_bounds=f_bounds,
        e_bounds=e_bounds,
        lineage_key=state.lineage_key,
        scope_key=r_scope_key,
        revision=state.revision,
        graph_version=graph_version,
    )


def _r_f_refusal(
    rtotal: _ROuter,
    d_state: CausalHistoryState,
    outcome: CurrentGraphOutcome,
    limitations: tuple[CurrentGraphLimitation, ...],
) -> CurrentGraphResult | None:
    """The ACTUAL nested F refusal mapping (its closed limitation
    retained by reference): the refusal construction is charged on
    the ONE R total; an R-total crossing there means no F result
    was ever built (the caller returns the own work-overflow
    refusal retaining the actual Q evidence)."""
    try:
        rtotal.units(_R_RESULT_BUILD_UNITS)
    except _ROverflow:
        return None
    return _refuse(d_state, outcome, limitations)


def derive_root_region_graph(
    state: RootRegionLineageState,
    ns: RootRegionLineageNamespace,
    bounds: RootRegionGraphBounds | None = None,
    *,
    root_region_currentness_bounds: RootRegionCurrentnessBounds | None = None,
    current_graph_bounds: CurrentGraphBounds | None = None,
    nonroot_currentness_bounds: CurrentnessBounds | None = None,
) -> RootRegionGraphResult:
    """The bounded pure selected-root-region source + current-graph
    derivation (objective 018-r).

    ONE R outer covers the ENTIRE operation: the O(1) state/
    namespace/bounds fences, the ACTUAL same-run Q phase (its
    ACTUAL independently bounded P phase included) under the ONE R
    total, the charged selected-source resolution, the ACTUAL F/E
    phase and graph-stage work under the ACTUAL independent F
    outer (its own diagnostic domain unchanged), and all R
    association/serialization/construction reservations.  The
    nested Q-local, P, D, B, E, F and GraphBounds domains keep
    their OWN independent ceilings beneath it (no global minimum,
    no reset ledger, no pre-reserved whole cap).

    The EXACT input P state is retained by reference on EVERY
    outcome; the ACTUAL same-run Q result is retained once
    returned, and the ACTUAL F result plus its SAME-run E overlay
    when returned, without rederiving under reset fuel or copying
    full histories.  A malformed non-P state fails with a fixed
    private ValueError BEFORE result construction; a rejected
    input scope or bounds characterizes the derivation with the
    default domain (the unusable input is never partially
    trusted).  A mapped Q unproven / authority-conflict / refusal
    publishes no source and never runs F; a source-resolution
    failure publishes no partial source; an F failure or an
    R-total crossing publishes no partial positive source/graph
    while retaining the ACTUAL returned nested evidence.  The
    derivation never advances a revision, never mints a root
    authority fact and never copies source beyond the ONE
    materialized root body.
    """
    # --- O(1) state fence (the unchanged Q law, reused) ---------
    if not _q_state_boundary_ok(state) or not _region_state_shape(state):
        raise _fixed("the region lineage state must carry an actual bounded state record")

    r_default = RootRegionGraphBounds()
    q_default = RootRegionCurrentnessBounds()
    f_default = CurrentGraphBounds()
    e_default = CurrentnessBounds()

    def _early_scope_key(
        rb: RootRegionGraphBounds,
        qb: RootRegionCurrentnessBounds,
        fb: CurrentGraphBounds,
        eb: CurrentnessBounds,
    ) -> str:
        """The honest early-refusal R scope: the ACTUAL bound
        locals of the refusing branch (the unusable input is
        never partially trusted) under the fixed R versions and
        the fenced namespace graph version."""
        return root_region_graph_scope_key(
            state.lineage_key,
            ROOT_REGION_GRAPH_CONTRACT_VERSION,
            ROOT_REGION_GRAPH_POLICY_VERSION,
            rb,
            qb,
            fb,
            eb,
            ns.graph_version,
        )

    # --- O(1) namespace fence (the unchanged Q law, reused) -----
    if (
        not _q_ns_boundary_ok(ns)
        or not _region_preflight_ns_shape(ns)
        or not _r_graph_version_ok(ns.graph_version)
    ):
        # The namespace is unusable: the honest safe refusal scope
        # (the fixed rejection graph version -- its actual value
        # cannot be trusted, read or encoded, and an unencodable
        # version is fenced BEFORE any scope-key hash/encode).
        return _r_result(
            state,
            r_default,
            q_default,
            f_default,
            e_default,
            _R_REJECTION_GRAPH_VERSION,
            root_region_graph_scope_key(
                state.lineage_key,
                ROOT_REGION_GRAPH_CONTRACT_VERSION,
                ROOT_REGION_GRAPH_POLICY_VERSION,
                r_default,
                q_default,
                f_default,
                e_default,
                _R_REJECTION_GRAPH_VERSION,
            ),
            RootRegionGraphOutcome.REFUSED,
            (RootRegionGraphDiagnostic.FOREIGN_SCOPE,),
        )

    # --- Closed bound resolutions (default domain on malformed) -
    r_bounds = r_default
    if bounds is not None:
        if not root_region_graph_bounds_shape_ok(bounds):
            return _r_result(
                state,
                r_default,
                q_default,
                f_default,
                e_default,
                ns.graph_version,
                _early_scope_key(r_default, q_default, f_default, e_default),
                RootRegionGraphOutcome.REFUSED,
                (RootRegionGraphDiagnostic.MALFORMED_BINDING,),
            )
        try:
            r_bounds = RootRegionGraphBounds.model_validate(
                bounds.model_dump(mode="python", warnings=False)
            )
        except Exception:
            return _r_result(
                state,
                r_default,
                q_default,
                f_default,
                e_default,
                ns.graph_version,
                _early_scope_key(r_default, q_default, f_default, e_default),
                RootRegionGraphOutcome.REFUSED,
                (RootRegionGraphDiagnostic.MALFORMED_BINDING,),
            )

    q_bounds = q_default
    if root_region_currentness_bounds is not None:
        if not _r_q_bounds_closed(root_region_currentness_bounds):
            return _r_result(
                state,
                r_bounds,
                q_default,
                f_default,
                e_default,
                ns.graph_version,
                _early_scope_key(r_bounds, q_default, f_default, e_default),
                RootRegionGraphOutcome.REFUSED,
                (RootRegionGraphDiagnostic.MALFORMED_BINDING,),
            )
        try:
            q_bounds = RootRegionCurrentnessBounds.model_validate(
                root_region_currentness_bounds.model_dump(mode="python", warnings=False)
            )
        except Exception:
            return _r_result(
                state,
                r_bounds,
                q_default,
                f_default,
                e_default,
                ns.graph_version,
                _early_scope_key(r_bounds, q_default, f_default, e_default),
                RootRegionGraphOutcome.REFUSED,
                (RootRegionGraphDiagnostic.MALFORMED_BINDING,),
            )

    f_bounds = f_default
    if current_graph_bounds is not None:
        if not _f_bounds_shape_ok(current_graph_bounds):
            return _r_result(
                state,
                r_bounds,
                q_bounds,
                f_default,
                e_default,
                ns.graph_version,
                _early_scope_key(r_bounds, q_bounds, f_default, e_default),
                RootRegionGraphOutcome.REFUSED,
                (RootRegionGraphDiagnostic.MALFORMED_BINDING,),
            )
        try:
            f_bounds = CurrentGraphBounds.model_validate(
                current_graph_bounds.model_dump(mode="python", warnings=False)
            )
        except Exception:
            return _r_result(
                state,
                r_bounds,
                q_bounds,
                f_default,
                e_default,
                ns.graph_version,
                _early_scope_key(r_bounds, q_bounds, f_default, e_default),
                RootRegionGraphOutcome.REFUSED,
                (RootRegionGraphDiagnostic.MALFORMED_BINDING,),
            )

    e_bounds = e_default
    if nonroot_currentness_bounds is not None:
        if not _e_bounds_shape_ok(nonroot_currentness_bounds):
            return _r_result(
                state,
                r_bounds,
                q_bounds,
                f_bounds,
                e_default,
                ns.graph_version,
                _early_scope_key(r_bounds, q_bounds, f_bounds, e_default),
                RootRegionGraphOutcome.REFUSED,
                (RootRegionGraphDiagnostic.MALFORMED_BINDING,),
            )
        try:
            e_bounds = CurrentnessBounds.model_validate(
                nonroot_currentness_bounds.model_dump(mode="python", warnings=False)
            )
        except Exception:
            return _r_result(
                state,
                r_bounds,
                q_bounds,
                f_bounds,
                e_default,
                ns.graph_version,
                _early_scope_key(r_bounds, q_bounds, f_bounds, e_default),
                RootRegionGraphOutcome.REFUSED,
                (RootRegionGraphDiagnostic.MALFORMED_BINDING,),
            )

    # --- Scope keys and ledgers (charged base) -------------------
    r_scope_key = root_region_graph_scope_key(
        state.lineage_key,
        ROOT_REGION_GRAPH_CONTRACT_VERSION,
        ROOT_REGION_GRAPH_POLICY_VERSION,
        r_bounds,
        q_bounds,
        f_bounds,
        e_bounds,
        ns.graph_version,
    )
    q_scope_key = root_region_currentness_scope_key(
        state.lineage_key,
        ROOT_REGION_CURRENTNESS_CONTRACT_VERSION,
        ROOT_REGION_CURRENTNESS_POLICY_VERSION,
        q_bounds,
    )
    rtotal = _ROuter(r_bounds.max_total_work_units)

    # --- ACTUAL Q phase (ONE R total; nested domains independent)
    q_result: RootRegionCurrentnessResult | None = None
    f_result: CurrentGraphResult | None = None
    e_overlay: CurrentnessOverlay | None = None
    try:
        rtotal.units(_R_BASE_UNITS)
        q_outer = _RQOuter(rtotal, q_bounds.max_total_work_units)
        q_result = _derive_root_region_currentness_core(state, ns, q_bounds, q_scope_key, q_outer)
    except _ROverflow:
        return _r_result(
            state,
            r_bounds,
            q_bounds,
            f_bounds,
            e_bounds,
            ns.graph_version,
            r_scope_key,
            RootRegionGraphOutcome.REFUSED,
            (RootRegionGraphDiagnostic.WORK_UNITS_OVER_BOUND,),
            q_result=q_result,
        )

    # --- Ordered Q mapping (BEFORE any source slicing or F) ------
    if q_result.outcome is RootRegionCurrentnessOutcome.ROOT_CURRENTNESS_UNPROVEN:
        try:
            rtotal.units(_R_RESULT_BUILD_UNITS)
        except _ROverflow:
            return _r_result(
                state,
                r_bounds,
                q_bounds,
                f_bounds,
                e_bounds,
                ns.graph_version,
                r_scope_key,
                RootRegionGraphOutcome.REFUSED,
                (RootRegionGraphDiagnostic.WORK_UNITS_OVER_BOUND,),
                q_result=q_result,
            )
        return _r_result(
            state,
            r_bounds,
            q_bounds,
            f_bounds,
            e_bounds,
            ns.graph_version,
            r_scope_key,
            RootRegionGraphOutcome.ROOT_CURRENTNESS_UNPROVEN,
            (),
            q_result=q_result,
        )
    if q_result.outcome is RootRegionCurrentnessOutcome.ROOT_AUTHORITY_CONFLICT:
        try:
            rtotal.units(_R_RESULT_BUILD_UNITS)
        except _ROverflow:
            return _r_result(
                state,
                r_bounds,
                q_bounds,
                f_bounds,
                e_bounds,
                ns.graph_version,
                r_scope_key,
                RootRegionGraphOutcome.REFUSED,
                (RootRegionGraphDiagnostic.WORK_UNITS_OVER_BOUND,),
                q_result=q_result,
            )
        return _r_result(
            state,
            r_bounds,
            q_bounds,
            f_bounds,
            e_bounds,
            ns.graph_version,
            r_scope_key,
            RootRegionGraphOutcome.ROOT_AUTHORITY_CONFLICT,
            (),
            q_result=q_result,
        )
    if q_result.outcome is RootRegionCurrentnessOutcome.REFUSED:
        try:
            rtotal.units(_R_RESULT_BUILD_UNITS)
        except _ROverflow:
            return _r_result(
                state,
                r_bounds,
                q_bounds,
                f_bounds,
                e_bounds,
                ns.graph_version,
                r_scope_key,
                RootRegionGraphOutcome.REFUSED,
                (RootRegionGraphDiagnostic.WORK_UNITS_OVER_BOUND,),
                q_result=q_result,
            )
        return _r_result(
            state,
            r_bounds,
            q_bounds,
            f_bounds,
            e_bounds,
            ns.graph_version,
            r_scope_key,
            RootRegionGraphOutcome.REFUSED,
            (),
            q_result=q_result,
        )

    # --- Charged selected-source resolution -----------------------
    p_selection = q_result.p_selection
    if p_selection is None or not p_selection.witness_facts:
        try:
            rtotal.units(_R_RESULT_BUILD_UNITS)
        except _ROverflow:
            return _r_result(
                state,
                r_bounds,
                q_bounds,
                f_bounds,
                e_bounds,
                ns.graph_version,
                r_scope_key,
                RootRegionGraphOutcome.REFUSED,
                (RootRegionGraphDiagnostic.WORK_UNITS_OVER_BOUND,),
                q_result=q_result,
            )
        return _r_result(
            state,
            r_bounds,
            q_bounds,
            f_bounds,
            e_bounds,
            ns.graph_version,
            r_scope_key,
            RootRegionGraphOutcome.REFUSED,
            (RootRegionGraphDiagnostic.SOURCE_RESOLUTION_FAILED,),
            q_result=q_result,
        )
    try:
        resolved = _r_resolve_source(state, p_selection, rtotal)
    except _ROverflow:
        return _r_result(
            state,
            r_bounds,
            q_bounds,
            f_bounds,
            e_bounds,
            ns.graph_version,
            r_scope_key,
            RootRegionGraphOutcome.REFUSED,
            (RootRegionGraphDiagnostic.WORK_UNITS_OVER_BOUND,),
            q_result=q_result,
        )
    except _RSourceError:
        try:
            rtotal.units(_R_RESULT_BUILD_UNITS)
        except _ROverflow:
            return _r_result(
                state,
                r_bounds,
                q_bounds,
                f_bounds,
                e_bounds,
                ns.graph_version,
                r_scope_key,
                RootRegionGraphOutcome.REFUSED,
                (RootRegionGraphDiagnostic.WORK_UNITS_OVER_BOUND,),
                q_result=q_result,
            )
        return _r_result(
            state,
            r_bounds,
            q_bounds,
            f_bounds,
            e_bounds,
            ns.graph_version,
            r_scope_key,
            RootRegionGraphOutcome.REFUSED,
            (RootRegionGraphDiagnostic.SOURCE_RESOLUTION_FAILED,),
            q_result=q_result,
        )

    # --- ACTUAL F/E phase (ONE R total; F domains independent) ---
    d_state = state.d_state
    try:
        # The actual D-namespace derivation is a real (re)validation
        # walk: its closed reservation is charged BEFORE it runs.
        rtotal.units(2 * (512 + len(ns.workspace) + len(ns.config_fingerprint)))
        d_ns = _region_d_namespace(ns)
        rtotal.unit()
        if d_state.history_key != d_ns.history_key:
            rtotal.units(_R_RESULT_BUILD_UNITS)
            return _r_result(
                state,
                r_bounds,
                q_bounds,
                f_bounds,
                e_bounds,
                ns.graph_version,
                r_scope_key,
                RootRegionGraphOutcome.REFUSED,
                (RootRegionGraphDiagnostic.FOREIGN_SCOPE,),
                q_result=q_result,
            )
        rtotal.unit()
        if not _currentness._revalidate_ns(d_ns):
            rtotal.units(_R_RESULT_BUILD_UNITS)
            return _r_result(
                state,
                r_bounds,
                q_bounds,
                f_bounds,
                e_bounds,
                ns.graph_version,
                r_scope_key,
                RootRegionGraphOutcome.REFUSED,
                (RootRegionGraphDiagnostic.VERSION_UNSUPPORTED,),
                q_result=q_result,
            )
        f_outer = _RFOuter(rtotal, f_bounds)
        stage = _StageLedger(d_ns.graph_bounds)
        f_result, e_overlay = _derive_graph(
            d_state,
            d_ns,
            f_bounds,
            e_bounds,
            f_outer,
            stage,
            root_text=resolved.root_text,
            root_digest=resolved.root_digest,
        )
    except _ROverflow:
        return _r_result(
            state,
            r_bounds,
            q_bounds,
            f_bounds,
            e_bounds,
            ns.graph_version,
            r_scope_key,
            RootRegionGraphOutcome.REFUSED,
            (RootRegionGraphDiagnostic.WORK_UNITS_OVER_BOUND,),
            q_result=q_result,
            f_result=f_result,
            e_overlay=e_overlay,
        )
    except _OuterOverflow as overflow:
        f_result = _r_f_refusal(
            rtotal,
            d_state,
            CurrentGraphOutcome.REFUSED_OVER_BOUND,
            (overflow.limitation,),
        )
        if f_result is None:
            return _r_result(
                state,
                r_bounds,
                q_bounds,
                f_bounds,
                e_bounds,
                ns.graph_version,
                r_scope_key,
                RootRegionGraphOutcome.REFUSED,
                (RootRegionGraphDiagnostic.WORK_UNITS_OVER_BOUND,),
                q_result=q_result,
            )
        return _r_result(
            state,
            r_bounds,
            q_bounds,
            f_bounds,
            e_bounds,
            ns.graph_version,
            r_scope_key,
            RootRegionGraphOutcome.REFUSED,
            (),
            q_result=q_result,
            f_result=f_result,
        )
    except _StageOverflow as overflow:
        f_result = _r_f_refusal(
            rtotal,
            d_state,
            CurrentGraphOutcome.REFUSED_OVER_BOUND,
            (overflow.limitation,),
        )
        if f_result is None:
            return _r_result(
                state,
                r_bounds,
                q_bounds,
                f_bounds,
                e_bounds,
                ns.graph_version,
                r_scope_key,
                RootRegionGraphOutcome.REFUSED,
                (RootRegionGraphDiagnostic.WORK_UNITS_OVER_BOUND,),
                q_result=q_result,
            )
        return _r_result(
            state,
            r_bounds,
            q_bounds,
            f_bounds,
            e_bounds,
            ns.graph_version,
            r_scope_key,
            RootRegionGraphOutcome.REFUSED,
            (),
            q_result=q_result,
            f_result=f_result,
        )
    except _Malformed as malformed:
        f_result = _r_f_refusal(
            rtotal,
            d_state,
            CurrentGraphOutcome.REFUSED_STATE_MALFORMED,
            (malformed.limitation,),
        )
        if f_result is None:
            return _r_result(
                state,
                r_bounds,
                q_bounds,
                f_bounds,
                e_bounds,
                ns.graph_version,
                r_scope_key,
                RootRegionGraphOutcome.REFUSED,
                (RootRegionGraphDiagnostic.WORK_UNITS_OVER_BOUND,),
                q_result=q_result,
            )
        return _r_result(
            state,
            r_bounds,
            q_bounds,
            f_bounds,
            e_bounds,
            ns.graph_version,
            r_scope_key,
            RootRegionGraphOutcome.REFUSED,
            (),
            q_result=q_result,
            f_result=f_result,
        )

    # --- Final output (the ACTUAL returned F/E evidence retained)
    if f_result.outcome is CurrentGraphOutcome.OK:
        # The READY result constructor re-verifies the resolved
        # source content (walk + encode + hash over the record's
        # own root text) and re-scans the retained root facts and
        # the selected witness facts (identity membership):
        # reserve those ACTUAL widths separately BEFORE the
        # constructor work.
        try:
            rtotal.units(
                _R_RESULT_BUILD_UNITS
                + _r_source_pass_units(resolved.root_text, resolved.root_byte_length)
                + len(state.root_facts)
                + len(p_selection.witness_facts)
                + 2 * len(state.d_state.occurrences)
            )
        except _ROverflow:
            return _r_result(
                state,
                r_bounds,
                q_bounds,
                f_bounds,
                e_bounds,
                ns.graph_version,
                r_scope_key,
                RootRegionGraphOutcome.REFUSED,
                (RootRegionGraphDiagnostic.WORK_UNITS_OVER_BOUND,),
                q_result=q_result,
                f_result=f_result,
                e_overlay=e_overlay,
            )
        return _r_result(
            state,
            r_bounds,
            q_bounds,
            f_bounds,
            e_bounds,
            ns.graph_version,
            r_scope_key,
            RootRegionGraphOutcome.READY,
            (),
            q_result=q_result,
            f_result=f_result,
            e_overlay=e_overlay,
            resolved_source=resolved,
        )
    try:
        rtotal.units(_R_RESULT_BUILD_UNITS)
    except _ROverflow:
        return _r_result(
            state,
            r_bounds,
            q_bounds,
            f_bounds,
            e_bounds,
            ns.graph_version,
            r_scope_key,
            RootRegionGraphOutcome.REFUSED,
            (RootRegionGraphDiagnostic.WORK_UNITS_OVER_BOUND,),
            q_result=q_result,
            f_result=f_result,
        )
    return _r_result(
        state,
        r_bounds,
        q_bounds,
        f_bounds,
        e_bounds,
        ns.graph_version,
        r_scope_key,
        RootRegionGraphOutcome.REFUSED,
        (),
        q_result=q_result,
        f_result=f_result,
    )

"""Region-compatible admission model boundaries (objective 018-s).

The permanent A-F acceptance matrix for the NEW
``RootRegionAdmissionEntry`` / ``RootRegionAdmission`` data models
and their closed local/admission-parent fences.  Batch 1: the
positive-first genuine public P -> actual R -> S parent construction
and the closed M01 bound-carrier fence (expected ORIGINAL concrete
class and both original hard ranges at every one of the ELEVEN
carriers, plus the early missing-field gates).
"""

from __future__ import annotations

import copy
import hashlib
import inspect
import json
import sys
from types import SimpleNamespace
from typing import Any, ClassVar, SupportsIndex, overload

import pytest
from pydantic import Field, ValidationError, field_validator

from slaif_local_coding.constitution.bundles import bundle_admission_models as bam
from slaif_local_coding.constitution.bundles import current_admission_models as cam
from slaif_local_coding.constitution.bundles import root_region_admission_models as rram
from slaif_local_coding.constitution.bundles.bundle_admission import (
    _key_canonical,
)
from slaif_local_coding.constitution.bundles.bundle_admission_models import (
    AdmissionMode,
    BoundaryClass,
    BundleAdmissionBounds,
    BundleAdmissionNamespace,
    BundleKeyRecord,
    EntryClass,
    MemberClass,
    OwnershipGroup,
    _canonical_namespace_fields,
    make_bundle_admission_namespace,
)
from slaif_local_coding.constitution.bundles.bundle_proof_models import (
    ROOT_FILENAME,
    BundleProof,
    BundleProofBounds,
    BundleSegment,
)
from slaif_local_coding.constitution.bundles.causal_history_models import (
    CAUSAL_ROOT_FACT,
    MAX_REVISION,
    CausalHistoryNamespace,
    HistoryBounds,
    RootAnchor,
)
from slaif_local_coding.constitution.bundles.client_paths import (
    validate_workspace,
)
from slaif_local_coding.constitution.bundles.current_admission import (
    _assemble_file_entries,
    _GOuter,
    _GOverflow,
    _GStage,
)
from slaif_local_coding.constitution.bundles.current_admission_models import (
    CURRENT_ADMISSION_CONTRACT_VERSION,
    CURRENT_ADMISSION_POLICY_VERSION,
    CurrentAdmissionBounds,
    CurrentAdmissionEntry,
    CurrentAdmissionLimitation,
    CurrentAdmissionPathAssociation,
    CurrentAdmissionWitness,
    _canonical_entry_key,
    _entry_admission_namespace,
    _sha256_hex,
)
from slaif_local_coding.constitution.bundles.current_graph_models import (
    CurrentGraphBounds,
    CurrentGraphOutcome,
    current_graph_scope_key,
)
from slaif_local_coding.constitution.bundles.currentness_models import (
    CURRENTNESS_CONTRACT_VERSION,
    CURRENTNESS_POLICY_VERSION,
    OPAQUE_GROUP_RECIPE_VERSION,
    CurrentnessBounds,
    CurrentnessOverlay,
    currentness_scope_key,
)
from slaif_local_coding.constitution.bundles.graph_models import (
    GraphBounds,
)
from slaif_local_coding.constitution.bundles.observation_models import (
    ObservationBounds,
)
from slaif_local_coding.constitution.bundles.root_lineage_models import (
    EnvelopeRootProvenance,
    RootLineageBounds,
    RootLineageLimitation,
    RootLineageOutcome,
    RootSelectionOutcome,
)
from slaif_local_coding.constitution.bundles.root_region_admission_models import (
    ROOT_REGION_ADMISSION_MODELS_CONTRACT_VERSION,
    ROOT_REGION_ADMISSION_MODELS_POLICY_VERSION,
    RootRegionAdmission,
    RootRegionAdmissionEntry,
    _s_all_eleven_bound_sets_closed,
    _s_canonical_metadata_precharge_closed,
    _s_entry_leaf_closed,
    _s_parent_precharge_closed,
    _s_region_precharge_closed,
    _s_root_content_precharge_closed,
    _s_witnesses_sorted_deduplicated,
    root_region_admission_model_scope_key,
)
from slaif_local_coding.constitution.bundles.root_region_currentness_models import (
    RootRegionCurrentnessBounds,
    RootRegionCurrentnessDiagnostic,
    RootRegionCurrentnessOutcome,
    RootRegionCurrentnessResult,
    RootRegionUncertaintyClass,
)
from slaif_local_coding.constitution.bundles.root_region_graph import (
    derive_root_region_graph,
)
from slaif_local_coding.constitution.bundles.root_region_graph_models import (
    _R_ENVELOPE_PROV_FIELDS,
    _R_READ_PROV_FIELDS,
    _R_REGION_PROV_FIELDS,
    RootRegionGraphBounds,
    RootRegionGraphDiagnostic,
    RootRegionGraphOutcome,
    RootRegionGraphResult,
    _r_result_closed,
    root_region_graph_scope_key,
)
from slaif_local_coding.constitution.bundles.root_region_lineage import (
    bootstrap_root_region_lineage,
)
from slaif_local_coding.constitution.bundles.root_region_lineage_models import (
    RootRegionSelectionResult,
    make_root_region_lineage_namespace,
)
from slaif_local_coding.constitution.cache import RequestIdentity
from tests import test_root_region_currentness as qf
from tests.test_causal_history import (
    ENDPOINTS,
    FINGERPRINT,
    IDENTITY,
    MODES,
    ROOT_TEXT,
    WORKSPACE,
    read_request,
    root_request,
)
from tests.test_root_lineage import rooted
from tests.test_root_region_graph import (
    _assert_ready_bindings,
    _mixed_region_state,
    _native_multi_piece_request,
)
from tests.test_root_region_lineage import (
    A_TEXT,
    B_TEXT,
    MARK,
    MIX_CMD,
    V2,
    _host_io_facilities,
    _mixed_body,
    r_bootstrap,
    r_issue,
    r_observe,
)

# --- Shared S helpers (genuine public P -> actual R -> S) -------------


def _s_admission_ns(ns: Any) -> BundleAdmissionNamespace:
    """The ACTUAL 018-c admission namespace coherently reconstructed
    from the P namespace's actual D-scope fields (the accepted G
    derivation's exact construction; its model validator re-derives
    both 64-hex keys from the actual fields)."""
    return BundleAdmissionNamespace(
        principal=ns.principal,
        session=ns.session,
        repository=ns.repository,
        route=ns.route,
        model_identity=ns.model_identity,
        config_fingerprint=ns.config_fingerprint,
        workspace=ns.workspace,
        mode=ns.mode,
        admission_version=ns.admission_version,
        observation_version=ns.observation_version,
        graph_version=ns.graph_version,
        reference_version=ns.reference_version,
        proof_version=ns.proof_version,
        bounds=ns.bounds,
        proof_bounds=ns.proof_bounds,
        graph_bounds=ns.graph_bounds,
        observation_bounds=ns.observation_bounds,
        namespace_key=ns.admission_namespace_key,
        scoped_key=ns.admission_scoped_key,
    )


def _s_root_key_record(ns: Any, state: Any) -> BundleKeyRecord:
    """The canonical C ROOT_ENTRY key record for the actual anchor
    (the UNCHANGED C recipe: ``_key_canonical`` +
    ``BundleKeyRecord``, mirroring the accepted G
    ``_build_root_entry`` descriptor exactly; the sole PROVEN group
    is bound to the actual anchor root digest)."""
    admission_ns = _s_admission_ns(ns)
    anchor = state.d_state.root
    assert anchor is not None
    root_digest = anchor.root_digest
    groups = (
        OwnershipGroup(
            group_index=0,
            member_occurrence_indices=(0,),
            boundary_class=BoundaryClass.PROVEN,
            group_digest=root_digest,
        ),
    )
    canonical = _key_canonical(
        admission_ns,
        root_digest,
        EntryClass.ROOT_ENTRY,
        (ROOT_FILENAME,),
        (MemberClass.ELIGIBLE,),
        root_digest,
        groups,
    )
    return BundleKeyRecord(
        mode=admission_ns.mode,
        authority_class=EntryClass.ROOT_ENTRY,
        principal=admission_ns.principal,
        session=admission_ns.session,
        repository=admission_ns.repository,
        route=admission_ns.route,
        config_fingerprint=admission_ns.config_fingerprint,
        model_identity=admission_ns.model_identity,
        workspace=admission_ns.workspace,
        root_digest=root_digest,
        reference_version=admission_ns.reference_version,
        admission_bounds=admission_ns.bounds,
        proof_bounds=admission_ns.proof_bounds,
        graph_bounds=admission_ns.graph_bounds,
        observation_bounds=admission_ns.observation_bounds,
        member_occurrences=(ROOT_FILENAME,),
        member_classes=(MemberClass.ELIGIBLE,),
        aggregate_source_digest=root_digest,
        ownership_groups=groups,
        content_key=_sha256_hex(canonical),
    )


def _s_parent(
    mode: Any,
    lineage: str,
    g_bounds: CurrentAdmissionBounds | None = None,
    *,
    history_bounds: HistoryBounds | None = None,
    root_body: str | None = None,
) -> tuple[
    Any,
    Any,
    Any,
    CurrentAdmissionBounds,
    BundleKeyRecord,
    RootRegionAdmissionEntry,
    RootRegionAdmission,
]:
    """ONE genuine public P bootstrap -> ACTUAL R READY -> S parent
    (the ENVELOPE source: the P bootstrap is Responses-only by law,
    so the actual read endpoints are earned by the later whole/
    region positives, never a bootstrapped Chat endpoint)."""
    if history_bounds is None:
        ns, s0 = r_bootstrap(mode, lineage, root_body=root_body)
    else:
        ns, s0 = r_bootstrap(mode, lineage, history_bounds=history_bounds, root_body=root_body)
    r = derive_root_region_graph(s0, ns)
    assert r.outcome is RootRegionGraphOutcome.READY
    _assert_ready_bindings(r, s0, root_body if root_body is not None else ROOT_TEXT)
    g = g_bounds if g_bounds is not None else CurrentAdmissionBounds()
    key_record = _s_root_key_record(ns, s0)
    root_entry = RootRegionAdmissionEntry(
        entry_class=EntryClass.ROOT_ENTRY,
        content_key=key_record.content_key,
        key_record=key_record,
        width=1,
        member_classes=(MemberClass.ELIGIBLE,),
        root_digest=key_record.root_digest,
        root_source=r.resolved_source,
    )
    row = CurrentAdmissionPathAssociation(
        scoped_key=ns.admission_scoped_key,
        path=ROOT_FILENAME,
        content_keys=(key_record.content_key,),
        is_root=True,
    )
    scope_key = root_region_admission_model_scope_key(
        s0.lineage_key,
        ROOT_REGION_ADMISSION_MODELS_CONTRACT_VERSION,
        ROOT_REGION_ADMISSION_MODELS_POLICY_VERSION,
        r.scope_key,
        CURRENT_ADMISSION_CONTRACT_VERSION,
        CURRENT_ADMISSION_POLICY_VERSION,
        g,
    )
    parent = RootRegionAdmission(
        state=s0,
        ns=ns,
        r_result=r,
        g_bounds=g,
        root_entry=root_entry,
        path_associations=(row,),
        scope_key=scope_key,
        entries_retained=1,
        member_occurrences_charged=1,
        reverse_association_attempts=1,
        emitted_admission_reasons=0,
    )
    return ns, s0, r, g, key_record, root_entry, parent


# --- B1 positives: the genuine parent construction --------------------


@pytest.mark.parametrize("mode", MODES)
def test_b1_parent_positive(mode: Any) -> None:
    """B1: the genuine public P bootstrap (envelope source,
    Responses-only by law) derives an ACTUAL R READY and the NEW S
    parent accepts it: exact carried references (state / ns / R
    result / resolved source by IDENTITY), the stable model scope
    key re-derived from the actual fields, and the closed counter
    relationships."""
    ns, s0, r, g, key_record, root_entry, parent = _s_parent(mode, "s-b1")
    assert parent.state is s0
    assert parent.ns is ns
    assert parent.r_result is r
    assert parent.g_bounds is g
    assert parent.root_entry is root_entry
    assert parent.root_entry.root_source is r.resolved_source
    assert parent.scope_key == root_region_admission_model_scope_key(
        s0.lineage_key,
        ROOT_REGION_ADMISSION_MODELS_CONTRACT_VERSION,
        ROOT_REGION_ADMISSION_MODELS_POLICY_VERSION,
        r.scope_key,
        CURRENT_ADMISSION_CONTRACT_VERSION,
        CURRENT_ADMISSION_POLICY_VERSION,
        g,
    )
    assert parent.entries_retained == 1
    assert parent.member_occurrences_charged == 1
    assert parent.reverse_association_attempts == 1
    assert parent.emitted_admission_reasons == 0


def test_b1_parent_stricter_g_bounds_positive() -> None:
    """B1: a legitimate STRICTER instance of the ORIGINAL G bound
    class remains legal by value (the class fence is on the class
    and the original ranges, not on the default values)."""
    g = CurrentAdmissionBounds(
        max_total_work_units=512,
        max_total_entry_source_bytes=8192,
        max_diagnostics=8,
    )
    ns, s0, r, actual_g, key_record, root_entry, parent = _s_parent(
        MODES[0], "s-b1-stricter", g_bounds=g
    )
    assert actual_g is g
    assert parent.g_bounds is g


# --- B1 M01: the closed eleven bound-carrier fence --------------------


def test_b1_eleven_carrier_fence() -> None:
    """B1: the ACTUAL eleven bound population is closed for the
    genuine positive (checked FIRST), and the G carrier refuses a
    zero total, a negative entry byte total, the WRONG concrete G
    class and a SHADOW SUBCLASS with redeclared widened ranges
    (dynamic subclass model_fields never define the original
    expected class or hard ranges)."""
    ns, s0, r, g, key_record, root_entry, parent = _s_parent(MODES[0], "s-b1-fence")
    # positive first: the actual carried population is closed
    assert _s_all_eleven_bound_sets_closed(ns, r, g)
    # a zero total under the original floor of 1
    assert not _s_all_eleven_bound_sets_closed(
        ns, r, g.model_copy(update={"max_total_work_units": 0})
    )
    # a negative entry byte total under the original floor of 1
    assert not _s_all_eleven_bound_sets_closed(
        ns, r, g.model_copy(update={"max_total_entry_source_bytes": -1})
    )
    # the WRONG concrete class at the G carrier
    assert not _s_all_eleven_bound_sets_closed(
        ns,
        r,
        RootRegionGraphBounds(),  # type: ignore[arg-type]
    )

    # a shadow subclass redeclaring WIDENED ranges: the exact
    # original-class fence refuses it before its fields are read
    class ShadowG(CurrentAdmissionBounds):
        max_total_work_units: int = Field(default=1, ge=0, le=2097152)

    assert not _s_all_eleven_bound_sets_closed(ns, r, ShadowG(max_total_work_units=0))
    assert not _s_all_eleven_bound_sets_closed(ns, r, ShadowG(max_total_work_units=2097152))


def test_b1_parent_partial_carried_records_refused() -> None:
    """B1: a PARTIAL carried record (model_copy-bypassed missing
    fields) is refused by the parent's early closed field-existence
    fences with a fixed private validation error, never an
    attribute error: the partial state, the partial namespace, the
    partial R result and the partial ROOT entry (either of the two
    fields the phase-4 carrying re-run first dereferences) each
    refuse BEFORE any nested law or root-row dereference runs."""
    ns, s0, r, g, key_record, root_entry, parent = _s_parent(MODES[0], "s-b1-partial")
    row = parent.path_associations[0]
    base_scope = parent.scope_key
    # the partial P state
    with pytest.raises(ValidationError, match="state must carry its closed fields"):
        RootRegionAdmission(
            state=s0.model_construct(revision=s0.revision),
            ns=ns,
            r_result=r,
            g_bounds=g,
            root_entry=root_entry,
            path_associations=(row,),
            scope_key=base_scope,
            entries_retained=1,
            member_occurrences_charged=1,
            reverse_association_attempts=1,
            emitted_admission_reasons=0,
        )
    # the partial P namespace
    with pytest.raises(ValidationError, match="namespace must carry its closed fields"):
        RootRegionAdmission(
            state=s0,
            ns=ns.model_construct(lineage_key=ns.lineage_key),
            r_result=r,
            g_bounds=g,
            root_entry=root_entry,
            path_associations=(row,),
            scope_key=base_scope,
            entries_retained=1,
            member_occurrences_charged=1,
            reverse_association_attempts=1,
            emitted_admission_reasons=0,
        )
    # the partial R result
    with pytest.raises(ValidationError, match="R result must carry its closed fields"):
        RootRegionAdmission(
            state=s0,
            ns=ns,
            r_result=r.model_construct(outcome=r.outcome),
            g_bounds=g,
            root_entry=root_entry,
            path_associations=(row,),
            scope_key=base_scope,
            entries_retained=1,
            member_occurrences_charged=1,
            reverse_association_attempts=1,
            emitted_admission_reasons=0,
        )

    # the partial ROOT entry: the phase-4 carrying re-run must not
    # dereference entry_class or root_source before the closed
    # field-existence fence (a bypassed partial entry is a fixed
    # private validation error, never an AttributeError)
    def _partial_root_entry(missing: str) -> RootRegionAdmissionEntry:
        partial = type(root_entry).model_construct(
            **{
                name: getattr(root_entry, name)
                for name in (
                    "entry_class",
                    "content_key",
                    "key_record",
                    "width",
                    "member_classes",
                    "root_digest",
                    "proof",
                    "admitted_segments",
                    "witnesses",
                    "root_source",
                )
            }
        )
        # the omission is a construction-time never-set field,
        # never a mutation of a validated (frozen) instance
        del partial.__dict__[missing]
        assert not hasattr(partial, missing)
        return partial

    for missing in ("entry_class", "root_source"):
        with pytest.raises(
            ValidationError, match="the admission entry must carry its closed fields"
        ):
            RootRegionAdmission(
                state=s0,
                ns=ns,
                r_result=r,
                g_bounds=g,
                root_entry=_partial_root_entry(missing),
                path_associations=(row,),
                scope_key=base_scope,
                entries_retained=1,
                member_occurrences_charged=1,
                reverse_association_attempts=1,
                emitted_admission_reasons=0,
            )


# --- B2 positives: the ACTUAL G assembly region / whole parents ----------

_D_NS_FIELDS = (
    "principal",
    "session",
    "repository",
    "route",
    "model_identity",
    "config_fingerprint",
    "workspace",
    "mode",
    "admission_version",
    "observation_version",
    "graph_version",
    "reference_version",
    "proof_version",
    "bounds",
    "proof_bounds",
    "graph_bounds",
    "observation_bounds",
    "admission_namespace_key",
    "admission_scoped_key",
    "lineage_id",
    "history_version",
    "arguments_version",
    "history_bounds",
    "history_key",
    "state_scoped_key",
)


def _d_ns(ns: Any) -> CausalHistoryNamespace:
    """The ACTUAL D namespace re-derived through the real accepted D
    validators from the P namespace's own fields (the accepted C/G
    construction; the re-derivation is the coherence proof)."""
    return CausalHistoryNamespace.model_validate({name: getattr(ns, name) for name in _D_NS_FIELDS})


def _s_selected_root_record(ns: Any, selected_digest: str) -> BundleKeyRecord:
    """The canonical C ROOT_ENTRY key record bound to the SELECTED
    governing digest (the UNCHANGED C recipe: ``_key_canonical`` +
    ``BundleKeyRecord``; the sole PROVEN group binds the selected
    digest, not the D anchor)."""
    admission_ns = _s_admission_ns(ns)
    groups = (
        OwnershipGroup(
            group_index=0,
            member_occurrence_indices=(0,),
            boundary_class=BoundaryClass.PROVEN,
            group_digest=selected_digest,
        ),
    )
    canonical = _key_canonical(
        admission_ns,
        selected_digest,
        EntryClass.ROOT_ENTRY,
        (ROOT_FILENAME,),
        (MemberClass.ELIGIBLE,),
        selected_digest,
        groups,
    )
    return BundleKeyRecord(
        mode=admission_ns.mode,
        authority_class=EntryClass.ROOT_ENTRY,
        principal=admission_ns.principal,
        session=admission_ns.session,
        repository=admission_ns.repository,
        route=admission_ns.route,
        config_fingerprint=admission_ns.config_fingerprint,
        model_identity=admission_ns.model_identity,
        workspace=admission_ns.workspace,
        root_digest=selected_digest,
        reference_version=admission_ns.reference_version,
        admission_bounds=admission_ns.bounds,
        proof_bounds=admission_ns.proof_bounds,
        graph_bounds=admission_ns.graph_bounds,
        observation_bounds=admission_ns.observation_bounds,
        member_occurrences=(ROOT_FILENAME,),
        member_classes=(MemberClass.ELIGIBLE,),
        aggregate_source_digest=selected_digest,
        ownership_groups=groups,
        content_key=_sha256_hex(canonical),
    )


def _s_parent_from_assembly(
    ns: Any, state: Any, r: Any, g_bounds: CurrentAdmissionBounds
) -> tuple[Any, ...]:
    """ONE genuine S parent over the ACTUAL G generic FILE assembly
    for the ready R's D state (legitimate component data through the
    unchanged 018-i factored core; the NOT-IMPLEMENTED unified
    operation is never claimed here)."""
    d_ns = _d_ns(ns)
    resolved = r.resolved_source
    assert resolved is not None
    selected = resolved.root_digest
    workspace_bytes = len(ns.workspace.encode("utf-8"))
    admission_ns = _s_admission_ns(ns)
    key_record = _s_selected_root_record(ns, selected)
    root_entry = RootRegionAdmissionEntry(
        entry_class=EntryClass.ROOT_ENTRY,
        content_key=key_record.content_key,
        key_record=key_record,
        width=1,
        member_classes=(MemberClass.ELIGIBLE,),
        root_digest=selected,
        root_source=r.resolved_source,
    )
    graph = r.f_result.overlay
    eligible = {node.path: node.depth for node in graph.nodes}
    groups_by_occ: dict[str, list[Any]] = {}
    for group in r.e_overlay.groups:
        groups_by_occ.setdefault(group.occurrence_id, []).append(group)
    outer = _GOuter(r.f_bounds, g_bounds)
    stage_g = _GStage(d_ns.graph_bounds)
    entries, path_keys, attempts, member_occ_charged, _total_bytes, diagnostics = (
        _assemble_file_entries(
            state.d_state,
            d_ns,
            admission_ns,
            selected,
            g_bounds,
            workspace_bytes,
            key_record.content_key,
            len(resolved.root_text.encode("utf-8")),
            groups_by_occ,
            eligible,
            RootRegionAdmissionEntry,
            outer,
            stage_g,
            selected_root_digest=selected,
        )
    )
    assert diagnostics == (), diagnostics
    rows = tuple(
        CurrentAdmissionPathAssociation(
            scoped_key=ns.admission_scoped_key,
            path=path,
            content_keys=tuple(sorted(path_keys[path])),
            is_root=path == ROOT_FILENAME,
        )
        for path in sorted(path_keys)
    )
    file_entries = tuple(entries[key] for key in sorted(entries))
    scope_key = root_region_admission_model_scope_key(
        state.lineage_key,
        ROOT_REGION_ADMISSION_MODELS_CONTRACT_VERSION,
        ROOT_REGION_ADMISSION_MODELS_POLICY_VERSION,
        r.scope_key,
        CURRENT_ADMISSION_CONTRACT_VERSION,
        CURRENT_ADMISSION_POLICY_VERSION,
        g_bounds,
    )
    parent = RootRegionAdmission(
        state=state,
        ns=ns,
        r_result=r,
        g_bounds=g_bounds,
        root_entry=root_entry,
        entries=file_entries,
        path_associations=rows,
        scope_key=scope_key,
        entries_retained=1 + len(file_entries),
        member_occurrences_charged=member_occ_charged,
        reverse_association_attempts=attempts,
        emitted_admission_reasons=0,
    )
    return key_record, root_entry, file_entries, rows, attempts, member_occ_charged, parent


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_b2_mixed_region_parent_positive(mode: Any, endpoint: str) -> None:
    """B2: the earned mixed-only read_region v2 state (no independent
    singleton) runs the ACTUAL G generic FILE assembly and the S
    parent accepts the result: the exact carried references, the
    selected-digest root binding, the genuine root-bearing FILE row
    (A.md plus the proven root member) with its original witness,
    the complete reverse index and the closed counter
    relationships."""
    ns, s2 = _mixed_region_state(mode, endpoint, f"s-b2-mix-{endpoint}")
    r = derive_root_region_graph(s2, ns)
    assert r.outcome is RootRegionGraphOutcome.READY
    _assert_ready_bindings(r, s2, V2)
    g = CurrentAdmissionBounds()
    key_record, root_entry, file_entries, rows, attempts, member_occ, parent = (
        _s_parent_from_assembly(ns, s2, r, g)
    )
    resolved = r.resolved_source
    assert resolved is not None
    selected = resolved.root_digest
    assert parent.state is s2 and parent.ns is ns and parent.r_result is r
    assert parent.root_entry is root_entry
    assert root_entry.root_source is r.resolved_source
    assert root_entry.root_digest == selected
    assert len(file_entries) == 1
    entry = file_entries[0]
    assert entry.entry_class is EntryClass.FILE_BUNDLE_ENTRY
    assert entry.key_record.member_occurrences == ("A.md", ROOT_FILENAME)
    assert entry.width == 2
    assert entry.root_digest == selected
    assert len(entry.witnesses) == 1
    assert [row.path for row in rows] == ["A.md", ROOT_FILENAME]
    root_row = rows[1]
    assert set(root_row.content_keys) == {root_entry.content_key, entry.content_key}
    assert parent.entries_retained == 2
    assert parent.member_occurrences_charged == member_occ
    assert parent.reverse_association_attempts >= len(rows)


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_b2_whole_read_parent_positive(mode: Any, endpoint: str) -> None:
    """B2: a genuine whole read of the root file (no marker) retains
    the legitimate compatible ROOT-BEARING FILE row (same bytes, FILE
    authority class) alongside the ONE governing ROOT_ENTRY; the
    single reverse row maps the root path to BOTH distinct content
    keys and the entry set law holds."""
    cmd = "cat AGENTS.md"
    ns, s0 = r_bootstrap(mode, f"s-b2-read-{endpoint}")
    t1 = r_issue(s0, ns, "m1", endpoint, (CAUSAL_ROOT_FACT,), cmd)
    assert t1.outcome.value == "accepted", t1.diagnostics
    t2 = r_observe(t1.state, ns, (read_request(endpoint, "m1", V2, cmd),))
    assert t2.outcome.value == "accepted", t2.diagnostics
    r = derive_root_region_graph(t2.state, ns)
    assert r.outcome is RootRegionGraphOutcome.READY
    _assert_ready_bindings(r, t2.state, V2)
    g = CurrentAdmissionBounds()
    key_record, root_entry, file_entries, rows, attempts, member_occ, parent = (
        _s_parent_from_assembly(ns, t2.state, r, g)
    )
    assert len(file_entries) == 1
    entry = file_entries[0]
    assert entry.entry_class is EntryClass.FILE_BUNDLE_ENTRY
    assert entry.key_record.member_occurrences == (ROOT_FILENAME,)
    assert entry.content_key != root_entry.content_key
    assert len(rows) == 1
    row = rows[0]
    assert row.path == ROOT_FILENAME and row.is_root is True
    assert set(row.content_keys) == {root_entry.content_key, entry.content_key}
    assert parent.entries_retained == 2
    assert parent.member_occurrences_charged == member_occ


def _s_component_parent(
    state: Any, ns: Any, g_bounds: CurrentAdmissionBounds | None = None
) -> tuple[Any, ...]:
    """ONE genuine public P state -> ACTUAL R READY -> ACTUAL generic G
    FILE assembly (the unchanged 018-i factored core under the same
    charged ledgers) -> fresh S parent over the legitimate component
    data: the canonical selected-digest root record plus the assembled
    FILE entries, their path associations and the ACTUAL assembly
    counters/reasons (the NOT-IMPLEMENTED unified operation is never
    claimed here)."""
    r = derive_root_region_graph(state, ns)
    assert r.outcome is RootRegionGraphOutcome.READY
    resolved = r.resolved_source
    assert resolved is not None
    selected = resolved.root_digest
    d_ns = _d_ns(ns)
    admission_ns = _s_admission_ns(ns)
    key_record = _s_selected_root_record(ns, selected)
    root_entry = RootRegionAdmissionEntry(
        entry_class=key_record.authority_class,
        content_key=key_record.content_key,
        key_record=key_record,
        width=1,
        member_classes=key_record.member_classes,
        root_digest=selected,
        root_source=resolved,
    )
    f_result = r.f_result
    assert f_result is not None
    f_overlay = f_result.overlay
    assert f_overlay is not None
    e_overlay = r.e_overlay
    assert e_overlay is not None
    eligible = {node.path: node.depth for node in f_overlay.nodes}
    groups_by_occ: dict[str, list[Any]] = {}
    for group in e_overlay.groups:
        groups_by_occ.setdefault(group.occurrence_id, []).append(group)
    g = g_bounds if g_bounds is not None else CurrentAdmissionBounds()
    entries, path_keys, attempts, member_occ_charged, _total_bytes, diagnostics = (
        _assemble_file_entries(
            state.d_state,
            d_ns,
            admission_ns,
            selected,
            g,
            len(ns.workspace.encode("utf-8")),
            key_record.content_key,
            len(resolved.root_text.encode("utf-8")),
            groups_by_occ,
            eligible,
            RootRegionAdmissionEntry,
            _GOuter(r.f_bounds, g),
            _GStage(d_ns.graph_bounds),
            selected_root_digest=selected,
        )
    )
    rows = tuple(
        CurrentAdmissionPathAssociation(
            scoped_key=ns.admission_scoped_key,
            path=path,
            content_keys=tuple(sorted(path_keys[path])),
            is_root=path == ROOT_FILENAME,
        )
        for path in sorted(path_keys)
    )
    file_entries = tuple(entries[key] for key in sorted(entries))
    scope_key = root_region_admission_model_scope_key(
        state.lineage_key,
        ROOT_REGION_ADMISSION_MODELS_CONTRACT_VERSION,
        ROOT_REGION_ADMISSION_MODELS_POLICY_VERSION,
        r.scope_key,
        CURRENT_ADMISSION_CONTRACT_VERSION,
        CURRENT_ADMISSION_POLICY_VERSION,
        g,
    )
    parent = RootRegionAdmission(
        state=state,
        ns=ns,
        r_result=r,
        g_bounds=g,
        root_entry=root_entry,
        entries=file_entries,
        path_associations=rows,
        scope_key=scope_key,
        entries_retained=1 + len(file_entries),
        member_occurrences_charged=member_occ_charged,
        reverse_association_attempts=attempts,
        emitted_admission_reasons=len(diagnostics),
        admission_reasons=diagnostics,
    )
    return r, g, root_entry, file_entries, parent, diagnostics


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_b2_all_compatible_witnesses_different_original_offsets(mode: Any, endpoint: str) -> None:
    """B2: a same-content read at a DIFFERENT original character
    offset inside a DIFFERENT original proof is a compatible witness,
    never a conflicting root or a refused entry: the FIRST compatible
    original proof is retained BY IDENTITY and ALL distinct original
    witness coordinates are retained in canonical full-coordinate
    order (lean keeps both witnesses under the SAME content key;
    greedy interns the mixed occurrence under its own whole-bundle
    key while the standalone entry keeps its witness and the
    background member stays GREEDY_BACKGROUND).  The fresh S parent
    accepts this legitimate actual G component data at the leaf and
    the admission parent (the earlier literal same-span guard
    wrongly refused the cross-proof witness; that regression is
    closed by this positive)."""
    body = "Synthetic shared A.\n"
    ns, state = r_bootstrap(
        mode,
        f"s-b2-offset-{mode.value}-{endpoint}",
        root_body="Read `A.md` before work.",
    )
    t1 = r_issue(state, ns, "off-first-A", endpoint, (CAUSAL_ROOT_FACT,), "cat A.md")
    assert t1.outcome.value == "accepted", t1.diagnostics
    t2 = r_observe(t1.state, ns, (read_request(endpoint, "off-first-A", body, "cat A.md"),))
    assert t2.outcome.value == "accepted", t2.diagnostics
    state = t2.state
    r1, _g1, _root1, files1, parent1, _a1 = _s_component_parent(state, ns)
    assert parent1.state is state and parent1.r_result is r1
    a_entry1 = next(e for e in files1 if e.key_record.member_occurrences == ("A.md",))
    assert len(a_entry1.witnesses) == 1
    first_occ_id = a_entry1.witnesses[0].occurrence_id

    cmd = "cat B.md && echo 'SYNTHETICSEP' && cat A.md"
    t3 = r_issue(state, ns, "off-mixed-BA", endpoint, (CAUSAL_ROOT_FACT,), cmd)
    assert t3.outcome.value == "accepted", t3.diagnostics
    t4 = r_observe(
        t3.state,
        ns,
        (
            read_request(
                endpoint,
                "off-mixed-BA",
                _mixed_body("Synthetic longer unrelated prefix.\n", "SYNTHETICSEP", body),
                cmd,
            ),
        ),
    )
    assert t4.outcome.value == "accepted", t4.diagnostics
    state = t4.state

    r2, _g2, root2, files2, parent2, _a2 = _s_component_parent(state, ns)
    assert parent2.state is state and parent2.r_result is r2
    assert parent2.root_entry is root2
    assert root2.root_source is r2.resolved_source
    assert parent2.entries_retained == 1 + len(files2)
    occ_by_id = {o.occurrence_id: o for o in state.d_state.occurrences}

    a_entry2 = next(e for e in files2 if e.key_record.member_occurrences == ("A.md",))
    witnesses = a_entry2.witnesses
    # the FIRST proof (the earlier singleton occurrence) is retained
    # BY IDENTITY and is one of the witness originals
    assert a_entry2.proof is not None
    owner_ids = {
        o.occurrence_id
        for o in state.d_state.occurrences
        if o.proof is not None and o.proof is a_entry2.proof
    }
    assert owner_ids == {first_occ_id}
    assert first_occ_id in {w.occurrence_id for w in witnesses}
    # canonical full-coordinate order, no duplicate coordinates
    coords = [
        (
            w.occurrence_id,
            w.request_index,
            w.call_position,
            w.result_position,
            w.segment_indices,
        )
        for w in witnesses
    ]
    assert coords == sorted(coords)
    assert len(set(coords)) == len(coords)

    if mode is AdmissionMode.LEAN:
        # lean: the SAME content key retains the FIRST proof and ALL
        # compatible distinct original witnesses at different offsets
        assert len(witnesses) == 2
        start_by_occ: dict[str, int] = {}
        for w in witnesses:
            proof = occ_by_id[w.occurrence_id].proof
            assert proof is not None
            start_by_occ[w.occurrence_id] = sum(
                x.char_length for x in proof.segments[: w.segment_indices[0]]
            )
        # the two originals sit at different CHARACTER offsets
        assert len(set(start_by_occ.values())) == 2
        assert start_by_occ[first_occ_id] == 0
        mixed_w = next(w for w in witnesses if w.occurrence_id != first_occ_id)
        mixed_proof = occ_by_id[mixed_w.occurrence_id].proof
        assert mixed_proof is not None
        # the mixed witness offset is the ACTUAL original
        # preceding-segment CHARACTER sum of its own proof
        expected = sum(x.char_length for x in mixed_proof.segments[: mixed_w.segment_indices[0]])
        assert start_by_occ[mixed_w.occurrence_id] == expected > 0
    else:
        # greedy: the standalone entry keeps its own single witness;
        # the mixed occurrence is interned under its own whole-bundle
        # key with the background member still GREEDY_BACKGROUND
        assert len(witnesses) == 1
        assert witnesses[0].occurrence_id == first_occ_id
        whole = next(e for e in files2 if e.key_record.member_occurrences == ("B.md", "A.md"))
        assert whole.key_record.member_classes == (
            MemberClass.GREEDY_BACKGROUND,
            MemberClass.ELIGIBLE,
        )
        assert whole.admitted_segments == (0, 1)
        assert len(whole.witnesses) == 1
        assert whole.witnesses[0].occurrence_id != first_occ_id
        assert whole.witnesses[0].segment_indices == (0, 1)
        rows = {row.path: row for row in parent2.path_associations}
        a_row = rows["A.md"]
        assert a_row.is_root is False
        assert set(a_row.content_keys) == {a_entry2.content_key, whole.content_key}
        assert set(rows["B.md"].content_keys) == {whole.content_key}


def _s_scope_key(state: Any, r: Any, g: CurrentAdmissionBounds) -> str:
    """The stable model configuration scope key re-derived from the
    ACTUAL fields at the given state point (the UNCHANGED helper
    recipe; never a copied tag)."""
    return root_region_admission_model_scope_key(
        state.lineage_key,
        ROOT_REGION_ADMISSION_MODELS_CONTRACT_VERSION,
        ROOT_REGION_ADMISSION_MODELS_POLICY_VERSION,
        r.scope_key,
        CURRENT_ADMISSION_CONTRACT_VERSION,
        CURRENT_ADMISSION_POLICY_VERSION,
        g,
    )


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_b2_root_key_equivalence_and_stable_scope(mode: Any, endpoint: str) -> None:
    """B2: the SAME actual semantic namespace / mode / selected
    digest / configuration produce BYTE-IDENTICAL C ROOT_ENTRY key
    records through the genuine ENVELOPE, whole-READ and DESCENDANT
    mixed-REGION provenance shapes in ONE namespace (the selected
    governing digest is key material; the forensic provenance and the
    carried revision are not), and the stable model configuration
    scope key is unchanged across the genuine provenance / revision
    changes and a genuine selected-root change at the same namespace /
    configuration.  A FRESH S leaf and parent are constructed from
    the ACTUAL generic G output at every stage (the changed-body
    history may legitimately emit the fixed candidate_unproven reason,
    retained by count in the parent); a genuinely changed root body
    changes the C key while the configuration scope stays stable, and
    a derivation-only R-only or G-only bound change alters the derived
    model scope without changing that same-content C key."""
    g = CurrentAdmissionBounds()
    text_v = "Read `A.md` before work."
    text_v2 = "Read `A.md` for the refresh."
    # ENVELOPE provenance: the bootstrap body itself is the root
    ns, s1 = r_bootstrap(mode, f"s-b2-sb-{mode.value}-{endpoint}", root_body=text_v)
    r_env, g_env, root_env, _files_env, parent_env, _a_env = _s_component_parent(s1, ns, g)
    assert parent_env.state is s1 and parent_env.r_result is r_env
    assert parent_env.root_entry is root_env
    assert root_env.root_source is r_env.resolved_source
    assert r_env.resolved_source.kind == "envelope"
    digest_v = r_env.resolved_source.root_digest
    key_env = _s_selected_root_record(ns, digest_v)
    scope_env = _s_scope_key(s1, r_env, g)
    assert parent_env.scope_key == scope_env
    # WHOLE read provenance: a genuine complete root read of the SAME bytes
    cmd = "cat AGENTS.md"
    t1 = r_issue(s1, ns, "sb-whole", endpoint, (CAUSAL_ROOT_FACT,), cmd)
    assert t1.outcome.value == "accepted", t1.diagnostics
    t2 = r_observe(t1.state, ns, (read_request(endpoint, "sb-whole", text_v, cmd),))
    assert t2.outcome.value == "accepted", t2.diagnostics
    s2 = t2.state
    r_whole, _g2, root_whole, _files2, parent_whole, _a2 = _s_component_parent(s2, ns, g)
    assert parent_whole.state is s2 and parent_whole.r_result is r_whole
    assert root_whole.root_source is r_whole.resolved_source
    assert r_whole.resolved_source.kind == "read"
    assert r_whole.resolved_source.root_digest == digest_v
    key_whole = _s_selected_root_record(ns, r_whole.resolved_source.root_digest)
    # REGION provenance: a genuine DESCENDANT mixed-only region read
    # of the SAME bytes
    mix_cmd = f"cat A.md && echo '{MARK}' && cat AGENTS.md"
    t3 = r_issue(
        s2, ns, "sb-region", endpoint, (s2.d_state.occurrences[-1].occurrence_id,), mix_cmd
    )
    assert t3.outcome.value == "accepted", t3.diagnostics
    t4 = r_observe(
        t3.state,
        ns,
        (read_request(endpoint, "sb-region", _mixed_body(A_TEXT, MARK, text_v), mix_cmd),),
    )
    assert t4.outcome.value == "accepted", t4.diagnostics
    s3 = t4.state
    r_reg, _g3, root_reg, _files3, parent_reg, _a3 = _s_component_parent(s3, ns, g)
    assert parent_reg.state is s3 and parent_reg.r_result is r_reg
    assert root_reg.root_source is r_reg.resolved_source
    assert r_reg.resolved_source.kind == "read_region"
    assert r_reg.resolved_source.root_digest == digest_v
    key_reg = _s_selected_root_record(ns, r_reg.resolved_source.root_digest)
    # BYTE-IDENTICAL C ROOT keys across all three provenance shapes
    # (same namespace / mode / digest / configuration)
    assert key_env == key_whole
    assert key_env == key_reg
    assert key_env.content_key == key_reg.content_key
    # the stable configuration scope is unchanged across the genuine
    # provenance / revision changes (envelope -> read -> read_region)
    assert _s_scope_key(s2, r_whole, g) == scope_env
    assert _s_scope_key(s3, r_reg, g) == scope_env
    assert parent_whole.scope_key == scope_env
    assert parent_reg.scope_key == scope_env
    # a GENUINELY CHANGED root body changes the C key ...
    t5 = r_issue(
        s3, ns, "sb-region2", endpoint, (s3.d_state.occurrences[-1].occurrence_id,), mix_cmd
    )
    assert t5.outcome.value == "accepted", t5.diagnostics
    t6 = r_observe(
        t5.state,
        ns,
        (read_request(endpoint, "sb-region2", _mixed_body(A_TEXT, MARK, text_v2), mix_cmd),),
    )
    assert t6.outcome.value == "accepted", t6.diagnostics
    s4 = t6.state
    r_v2, _g4, root_v2, _files4, parent_v2, diag_v2 = _s_component_parent(s4, ns, g)
    assert parent_v2.state is s4 and parent_v2.r_result is r_v2
    assert root_v2.root_source is r_v2.resolved_source
    assert r_v2.resolved_source.kind == "read_region"
    assert r_v2.resolved_source.root_digest != digest_v
    key_v2 = _s_selected_root_record(ns, r_v2.resolved_source.root_digest)
    assert key_v2.content_key != key_env.content_key
    # ... while the configuration scope stays stable
    assert _s_scope_key(s4, r_v2, g) == scope_env
    assert parent_v2.scope_key == scope_env
    # the changed-body history legitimately emits the fixed
    # candidate_unproven reason (the superseded original occurrence
    # contributes no plan): the fresh parent retains it by count
    assert diag_v2 == (CurrentAdmissionLimitation.CANDIDATE_UNPROVEN,)
    assert parent_v2.emitted_admission_reasons == len(diag_v2)
    assert parent_v2.admission_reasons == diag_v2
    # a DERIVATION-ONLY G bound change changes the derived model scope
    # without changing the same-content C key
    g_strict = CurrentAdmissionBounds(
        max_total_work_units=512,
        max_total_entry_source_bytes=8192,
        max_diagnostics=8,
    )
    assert _s_scope_key(s3, r_reg, g_strict) != scope_env
    assert _s_selected_root_record(ns, digest_v) == key_env
    # a DERIVATION-ONLY R bound change changes the re-derived R scope
    # (and hence the model scope) without changing the C key
    r_strict = derive_root_region_graph(s3, ns, RootRegionGraphBounds(max_total_work_units=1048575))
    assert r_strict.outcome is RootRegionGraphOutcome.READY
    assert r_strict.scope_key != r_reg.scope_key
    assert _s_scope_key(s3, r_strict, g) != scope_env
    assert _s_selected_root_record(ns, digest_v) == key_env


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_b2_ordered_member_keys_and_distinct_path_widths(mode: Any, endpoint: str) -> None:
    """B2: the ordered member tuple is C key material while the width
    counts DISTINCT normalized admitted paths, never repeated
    occurrences: with EQUAL A and B member body bytes the (A,B) and
    (B,A) bundles share the SAME aggregate digest yet their ordered
    member tuples and C keys differ (separate genuine lineages with
    the same C semantic namespace; concurrent boundaryless claims are
    legitimately ownership-ambiguous and are not co-admitted), and
    the repeated-operand (A,A,B) bundle retains its occurrence
    sequence with distinct-path width 2.  Unknown individual member
    hashes stay unknown (boundaryless multi-member segments carry the
    segment digest, never a proven per-member digest).  A fresh S
    parent accepts each legitimate actual G component shape."""
    x = "Synthetic shared member body.\n"

    def one_case(label: str, cmd: str, body: str) -> tuple[Any, ...]:
        ns, state = r_bootstrap(
            mode,
            f"s-b2-ow-{mode.value}-{endpoint}-{label}",
            root_body="Read `A.md` and `B.md` before work.",
        )
        t1 = r_issue(state, ns, "ow-one", endpoint, (CAUSAL_ROOT_FACT,), cmd)
        assert t1.outcome.value == "accepted", t1.diagnostics
        t2 = r_observe(t1.state, ns, (read_request(endpoint, "ow-one", body, cmd),))
        assert t2.outcome.value == "accepted", t2.diagnostics
        state = t2.state
        r, _g, _root, files, parent, _a = _s_component_parent(state, ns)
        assert parent.state is state and parent.r_result is r
        assert parent.entries_retained == 1 + len(files)
        entry = next(e for e in files if e.key_record.member_occurrences != (ROOT_FILENAME,))
        return ns, state, r, files, parent, entry

    ns_ab, _s_ab, _r_ab, _files_ab, _p_ab, e_ab = one_case("ab", "cat A.md && cat B.md", x + x)
    ns_ba, _s_ba, _r_ba, _files_ba, _p_ba, e_ba = one_case("ba", "cat B.md && cat A.md", x + x)
    ns_aab, _s_aab, _r_aab, _files_aab, _p_aab, e_aab = one_case(
        "aab", "cat A.md && cat A.md && cat B.md", x + x + x
    )
    # the ordered member tuples differ ...
    assert e_ab.key_record.member_occurrences == ("A.md", "B.md")
    assert e_ba.key_record.member_occurrences == ("B.md", "A.md")
    assert e_aab.key_record.member_occurrences == ("A.md", "A.md", "B.md")
    # ... with EQUAL A/B body bytes the AB and BA aggregates are the
    # SAME digest, yet the C keys differ (order is key material)
    assert e_ab.key_record.aggregate_source_digest == e_ba.key_record.aggregate_source_digest
    assert e_ab.content_key != e_ba.content_key
    assert e_ab.content_key != e_aab.content_key
    assert e_ba.content_key != e_aab.content_key
    # width counts DISTINCT normalized admitted paths, not occurrences
    assert e_ab.width == 2
    assert e_ba.width == 2
    assert e_aab.width == 2
    assert e_aab.width < len(e_aab.key_record.member_occurrences)
    # every member is independently eligible; the boundaryless
    # multi-member segments carry the segment digest and NO proven
    # per-member digest (unknown individual member hashes stay unknown)
    for entry in (e_ab, e_ba, e_aab):
        assert entry.member_classes == tuple(
            MemberClass.ELIGIBLE for _ in entry.key_record.member_occurrences
        )
        groups = entry.key_record.ownership_groups
        assert len(groups) == 1
        group = groups[0]
        assert group.boundary_class is BoundaryClass.BOUNDARYLESS
        assert group.member_occurrence_indices == tuple(
            range(len(entry.key_record.member_occurrences))
        )
        assert group.group_digest == entry.key_record.aggregate_source_digest
        assert entry.proof is not None
        assert len(entry.proof.segments) == 1
        assert entry.proof.segments[0].member_digest is None


# --- A. Source-shape S-boundary positives (genuine public P -> actual R)


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_a_unicode_nonroot_prefix_parent(mode: Any, endpoint: str) -> None:
    """A: a multi-byte Unicode NONROOT prefix precedes the root member;
    the selected root interval is the sum of preceding original
    segment CHARACTER lengths (never UTF-8 byte lengths or carrier
    offsets), so the exact root body is materialized despite
    bytes != chars, and the fresh S parent accepts the legitimate
    component data with the exact selected-root binding (the root
    fact binds the root-member bytes, not the mixed aggregate)."""
    a_unicode = "Synthetic \u00fcn\u00efcod\u00e9 nonroot \u2713 body.\n"
    assert len(a_unicode.encode("utf-8")) != len(a_unicode)
    ns, s0 = r_bootstrap(mode, f"s-a-uni-{mode.value}-{endpoint}")
    t1 = r_issue(s0, ns, "m1", endpoint, (CAUSAL_ROOT_FACT,), MIX_CMD)
    assert t1.outcome.value == "accepted"
    t2 = r_observe(
        t1.state,
        ns,
        (read_request(endpoint, "m1", _mixed_body(a_unicode, MARK, V2), MIX_CMD),),
    )
    assert t2.outcome.value == "accepted", t2.diagnostics
    s2 = t2.state
    r, _g, _root, files, parent, _diag = _s_component_parent(s2, ns)
    assert parent.state is s2 and parent.r_result is r
    resolved = r.resolved_source
    assert resolved is not None
    # character-sum offset: the exact root body materializes
    assert resolved.root_text == V2
    assert resolved.root_byte_length == len(V2.encode("utf-8"))
    # the nonroot Unicode prefix stays nonroot (root-member bytes only)
    assert resolved.fact.source_byte_length == len(V2.encode("utf-8"))
    assert parent.root_entry.root_source is resolved
    assert parent.root_entry.root_digest == resolved.root_digest
    assert (
        parent.root_entry.content_key
        == _s_selected_root_record(ns, resolved.root_digest).content_key
    )
    assert parent.entries_retained == 1 + len(files)


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
@pytest.mark.parametrize(
    ("tag", "root_body"),
    [
        ("crlf", "Region root with CRLF\r\nsecond line\r\n"),
        ("empty", ""),
    ],
    ids=["crlf", "empty"],
)
def test_a_crlf_and_empty_root_parent(mode: Any, endpoint: str, tag: str, root_body: str) -> None:
    """A: a CRLF root body and a genuinely proven EMPTY root region
    both derive READY with the EXACT root text (CR/LF preserved,
    zero bytes legal) and the fresh S parent accepts the legitimate
    component data with the exact selected-root binding."""
    ns, s0 = r_bootstrap(mode, f"s-a-{tag}-{mode.value}-{endpoint}")
    t1 = r_issue(s0, ns, "m1", endpoint, (CAUSAL_ROOT_FACT,), MIX_CMD)
    assert t1.outcome.value == "accepted"
    t2 = r_observe(
        t1.state,
        ns,
        (read_request(endpoint, "m1", _mixed_body(A_TEXT, MARK, root_body), MIX_CMD),),
    )
    assert t2.outcome.value == "accepted", t2.diagnostics
    s2 = t2.state
    r, _g, _root, files, parent, _diag = _s_component_parent(s2, ns)
    assert parent.state is s2 and parent.r_result is r
    resolved = r.resolved_source
    assert resolved is not None
    assert resolved.root_text == root_body
    assert resolved.root_byte_length == len(root_body.encode("utf-8"))
    assert parent.root_entry.root_source is resolved
    assert parent.root_entry.root_digest == resolved.root_digest
    assert parent.entries_retained == 1 + len(files)


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_a_native_multi_piece_parent(mode: Any, endpoint: str) -> None:
    """A: the genuine native MULTI-PIECE carrier (exec + two polls,
    three pieces, marker split across the exec/poll boundary)
    derives READY with the ACTUAL original exec owner and poll piece
    producers retained by identity; the fresh S parent accepts the
    legitimate component data with the root_source bound to the
    input's OWN original occurrence and retained proof (the INITIAL
    complete exec owning record, the piece-call bindings, the
    FROZEN causal parent frontier and the proven executed operand
    list all stay joined at the S boundary; no client or native
    process starts, the frames are known synthetic literals)."""
    ns, s0 = r_bootstrap(mode, f"s-a-mp-{mode.value}-{endpoint}")
    t1 = r_issue(s0, ns, "m1", endpoint, (CAUSAL_ROOT_FACT,), MIX_CMD)
    assert t1.outcome.value == "accepted"
    t2 = r_observe(t1.state, ns, (_native_multi_piece_request(endpoint),))
    assert t2.outcome.value == "accepted", t2.diagnostics
    s2 = t2.state
    r, _g, _root, files, parent, _diag = _s_component_parent(s2, ns)
    assert parent.state is s2 and parent.r_result is r
    resolved = r.resolved_source
    assert resolved is not None
    proof = resolved.proof
    assert proof is not None
    pieces = proof.pieces
    assert len(pieces) == 3
    # each piece keeps its ACTUAL producing call association
    assert [p.call_id for p in pieces] == ["m1", "p1", "p2"]
    assert (
        (pieces[0].call_position, pieces[0].result_position),
        (pieces[1].call_position, pieces[1].result_position),
        (pieces[2].call_position, pieces[2].result_position),
    ) == ((0, 1), (2, 3), (4, 5))
    # the proof's ORIGINAL exec association owns the whole result
    assert proof.call_id == "m1"
    assert proof.result_position == 1
    # the INITIAL complete exec owning record in the exact input
    # state: every piece joins its producing call through its
    # observed piece-call bindings (never invented)
    ds = s2.d_state
    m1_res = next(x for x in ds.results if x.call_id == "m1")
    assert m1_res.complete is True
    assert [b[0] for b in m1_res.piece_call_bindings] == ["m1", "p1", "p2"]
    for piece, binding in zip(pieces, m1_res.piece_call_bindings, strict=True):
        assert piece.call_id == binding[0]
    # the FROZEN causal parent frontier: the m1 occurrence is
    # parented to the ORIGINAL bootstrap root anchor fact
    m1_occ = next(o for o in ds.occurrences if o.call_id == "m1")
    assert len(ds.parent_links) == 1
    assert ds.parent_links[0].child == m1_occ.occurrence_id
    assert ds.parent_links[0].parent == CAUSAL_ROOT_FACT
    # the resolved source is the input's own original occurrence
    # and retained proof, by identity
    assert resolved.occurrence is m1_occ
    assert resolved.proof is m1_occ.proof
    assert resolved.root_text == V2
    assert proof.proven_executed == ("A.md", "AGENTS.md")
    assert resolved.fact.issued is True and resolved.fact.authority is True
    assert parent.root_entry.root_source is resolved
    assert parent.root_entry.root_digest == resolved.root_digest
    assert parent.entries_retained == 1 + len(files)


# --- C2: the closed key-record O(1) fences (M02) -------------------------


def _forged_record_fields(record: Any, **overrides: Any) -> dict[str, Any]:
    """ALL actual record fields plus overrides (a bypassed
    model_construct keeps the real nested models intact so the
    forged field is isolated)."""
    fields = {name: getattr(record, name) for name in record.model_fields}
    fields.update(overrides)
    return fields


def test_c2_key_record_nonstr_scalars_refused() -> None:
    """C2: a bypassed key record carrying a NON-STR scalar (True) on
    any of the nine text/digest/version fields is a fixed private
    validation error at BOTH boundaries (the leaf entry constructor
    and the admission-parent re-run), never a TypeError from a raw
    text/hex check."""
    ns, s0, r, g, key_record, root_entry, parent = _s_parent(MODES[0], "s-c2")
    hex_fields = ("config_fingerprint", "root_digest", "aggregate_source_digest", "content_key")
    text_fields = ("principal", "session", "repository", "route", "model_identity")
    for field in (*text_fields, *hex_fields):
        suffix = "hex" if field in hex_fields else "text"
        forged = key_record.model_construct(**_forged_record_fields(key_record, **{field: True}))
        with pytest.raises(
            ValidationError, match=f"the key record {field} must carry closed {suffix}"
        ):
            RootRegionAdmissionEntry(
                entry_class=EntryClass.ROOT_ENTRY,
                content_key=key_record.content_key,
                key_record=forged,
                width=1,
                member_classes=(MemberClass.ELIGIBLE,),
                root_digest=key_record.root_digest,
                root_source=r.resolved_source,
            )
    # The admission-parent re-run of the leaf law refuses the same
    # bypassed record carried in an otherwise-genuine root entry
    # (the parent boundary, not only the constructor boundary).
    forged = key_record.model_construct(**_forged_record_fields(key_record, principal=True))
    forged_entry = root_entry.model_construct(
        **{
            **{name: getattr(root_entry, name) for name in root_entry.model_fields},
            "key_record": forged,
        }
    )
    with pytest.raises(ValidationError, match="the key record principal must carry closed text"):
        RootRegionAdmission(
            state=s0,
            ns=ns,
            r_result=r,
            g_bounds=g,
            root_entry=forged_entry,
            path_associations=parent.path_associations,
            scope_key=parent.scope_key,
            entries_retained=1,
            member_occurrences_charged=1,
            reverse_association_attempts=1,
            emitted_admission_reasons=0,
        )


def test_c2_key_record_overbound_members_refused() -> None:
    """C2: a copied key record whose member occurrence count exceeds
    the ACTUAL carried admission cap (1025 under the actual cap
    1024) refuses with the fixed private error BEFORE any element
    visit (alignment with the member classes is not cap
    enforcement)."""
    ns, s0, r, g, key_record, root_entry, parent = _s_parent(MODES[0], "s-c2-count")
    cap = key_record.admission_bounds.max_member_occurrences
    paths = tuple(f"m{i:04d}.md" for i in range(cap + 1))
    groups = (
        OwnershipGroup(
            group_index=0,
            member_occurrence_indices=tuple(range(cap + 1)),
            boundary_class=BoundaryClass.BOUNDARYLESS,
            group_digest="0" * 64,
        ),
    )
    forged = key_record.model_construct(
        **_forged_record_fields(
            key_record,
            member_occurrences=paths,
            member_classes=(MemberClass.ELIGIBLE,) * (cap + 1),
            ownership_groups=groups,
        )
    )
    with pytest.raises(
        ValidationError,
        match="member occurrences exceed the actual carried admission cap",
    ):
        RootRegionAdmissionEntry(
            entry_class=EntryClass.ROOT_ENTRY,
            content_key=key_record.content_key,
            key_record=forged,
            width=1,
            member_classes=(MemberClass.ELIGIBLE,),
            root_digest=key_record.root_digest,
            root_source=r.resolved_source,
        )


def test_c2_key_record_group_index_bool_refused() -> None:
    """C2: a bypassed ownership group with group_index=False
    (False == 0 numeric equality) is refused by the closed non-bool
    dense-ordered fence, never accepted by the int comparison."""
    ns, s0, r, g, key_record, root_entry, parent = _s_parent(MODES[0], "s-c2-bool")
    group = OwnershipGroup.model_construct(
        group_index=False,
        member_occurrence_indices=(0,),
        boundary_class=BoundaryClass.PROVEN,
        group_digest=key_record.root_digest,
    )
    forged = key_record.model_construct(
        **_forged_record_fields(key_record, ownership_groups=(group,))
    )
    with pytest.raises(ValidationError, match="ownership group indices must be dense and ordered"):
        RootRegionAdmissionEntry(
            entry_class=EntryClass.ROOT_ENTRY,
            content_key=key_record.content_key,
            key_record=forged,
            width=1,
            member_classes=(MemberClass.ELIGIBLE,),
            root_digest=key_record.root_digest,
            root_source=r.resolved_source,
        )


# --- C/D: the FILE retained segment population fences (M02/M03) --------


def test_cd_unadmitted_preceding_segment_metadata_closed() -> None:
    """C/D: positive first -- the genuine LEAN state whose root
    declares A and whose read is the UNADMITTED B segment followed
    by the proven A segment assembles ONE FILE entry admitting only
    segment 1, and the S leaf and parent accept it; then a
    NEGATIVE-only copy of the PRECEDING UNADMITTED segment 0
    missing char_length (bypassed model_construct, all other
    original metadata intact) refuses with a fixed private
    validation error at BOTH boundaries BEFORE any character
    offset or source slice is computed (never an attribute error
    in the offset walk)."""
    ns, s0 = r_bootstrap(MODES[0], "s-cd-preceding")
    cmd = f"cat B.md && echo '{MARK}' && cat A.md"
    t1 = r_issue(s0, ns, "m1", "responses", (CAUSAL_ROOT_FACT,), cmd)
    assert t1.outcome.value == "accepted", t1.diagnostics
    t2 = r_observe(
        t1.state,
        ns,
        (read_request("responses", "m1", _mixed_body(B_TEXT, MARK, A_TEXT), cmd),),
    )
    assert t2.outcome.value == "accepted", t2.diagnostics
    r = derive_root_region_graph(t2.state, ns)
    assert r.outcome is RootRegionGraphOutcome.READY
    _assert_ready_bindings(r, t2.state, ROOT_TEXT)
    g = CurrentAdmissionBounds()
    key_record, root_entry, file_entries, rows, attempts, member_occ, parent = (
        _s_parent_from_assembly(ns, t2.state, r, g)
    )
    assert len(file_entries) == 1
    entry = file_entries[0]
    assert entry.admitted_segments == (1,)
    assert entry.key_record.member_occurrences == ("A.md",)
    proof = entry.proof
    assert proof is not None and len(proof.segments) == 2
    assert parent.state is t2.state and parent.entries == file_entries  # positive
    # The NEGATIVE-only preceding unadmitted segment loses char_length
    first = proof.segments[0]
    first_fields = {name: getattr(first, name) for name in BundleSegment.model_fields}
    del first_fields["char_length"]
    bad_first = BundleSegment.model_construct(**first_fields)
    bad_proof = proof.model_copy(update={"segments": (bad_first, *proof.segments[1:])})
    bad_entry = entry.model_copy(update={"proof": bad_proof})
    entry_fields = {name: getattr(entry, name) for name in RootRegionAdmissionEntry.model_fields}
    with pytest.raises(
        ValidationError, match="the retained proof segments must carry their closed metadata"
    ):
        RootRegionAdmissionEntry(**{**entry_fields, "proof": bad_proof})
    with pytest.raises(
        ValidationError, match="the retained proof segments must carry their closed metadata"
    ):
        RootRegionAdmission(
            state=t2.state,
            ns=ns,
            r_result=r,
            g_bounds=g,
            root_entry=root_entry,
            entries=(bad_entry,),
            path_associations=rows,
            scope_key=parent.scope_key,
            entries_retained=2,
            member_occurrences_charged=member_occ,
            reverse_association_attempts=attempts,
            emitted_admission_reasons=0,
        )


# --- C6: the closed reverse-row fences (M06) ------------------------------


def test_c6_partial_reverse_row_refused() -> None:
    """C6: a bypassed reverse row missing its closed fields is a
    fixed private error BEFORE any row.path extraction (never an
    AttributeError at the expected-path map)."""
    ns, s0, r, g, key_record, root_entry, parent = _s_parent(MODES[0], "s-c6")
    partial_row = CurrentAdmissionPathAssociation.model_construct(
        scoped_key=ns.admission_scoped_key
    )
    with pytest.raises(ValidationError, match="the reverse row must carry its closed fields"):
        RootRegionAdmission(
            state=s0,
            ns=ns,
            r_result=r,
            g_bounds=g,
            root_entry=root_entry,
            path_associations=(partial_row,),
            scope_key=parent.scope_key,
            entries_retained=1,
            member_occurrences_charged=1,
            reverse_association_attempts=1,
            emitted_admission_reasons=0,
        )


# --- C7: the carried R result fences (M07) --------------------------------


class _CountingDiagnostics(tuple[Any]):
    """A diagnostic tuple whose element iteration is COUNTED: the
    closed count gate must refuse before any iterator enters the
    shared R law's set/sort walk."""

    iterations = 0

    def __iter__(self) -> Any:
        _CountingDiagnostics.iterations += 1
        return super().__iter__()


def test_c7_carried_r_diagnostics_count_closed_before_walk() -> None:
    """C7: positive first (the genuine parent is accepted), then a
    bypassed R result carrying an OVER-BOUND diagnostic tuple (65
    elements against the actual R cap 64) refuses at the closed O(1)
    container/count gate with ZERO element iterations before the
    shared R law (the old public R recipe stays unchanged)."""
    ns, s0, r, g, key_record, root_entry, parent = _s_parent(MODES[0], "s-c7")
    assert parent.r_result is r  # positive first
    over = _CountingDiagnostics((RootRegionGraphDiagnostic.WORK_UNITS_OVER_BOUND,) * 65)
    forged_r = r.model_copy(update={"diagnostics": over})
    _CountingDiagnostics.iterations = 0
    with pytest.raises(ValidationError, match="exceed the actual R cap before any walk"):
        RootRegionAdmission(
            state=s0,
            ns=ns,
            r_result=forged_r,
            g_bounds=g,
            root_entry=root_entry,
            path_associations=parent.path_associations,
            scope_key=parent.scope_key,
            entries_retained=1,
            member_occurrences_charged=1,
            reverse_association_attempts=1,
            emitted_admission_reasons=0,
        )
    assert _CountingDiagnostics.iterations == 0


# --- C8: the before-parsing constructor gates (M02/M08) ------------------


def test_c8_parent_reasons_count_closed_before_enum() -> None:
    """C8: a DIRECT parent constructor call with a 65-element
    reasons sequence (against the actual cap 64) and otherwise-
    positive kwargs refuses at the BEFORE-pARSING O(1)
    container/count gate: ONE fixed private error, no per-element
    enum error storm, before any element conversion."""
    ns, s0, r, g, key_record, root_entry, parent = _s_parent(MODES[0], "s-c8")
    with pytest.raises(
        ValidationError, match="emitted admission reasons exceed the hard ceiling"
    ) as excinfo:
        RootRegionAdmission(
            state=s0,
            ns=ns,
            r_result=r,
            g_bounds=g,
            root_entry=root_entry,
            path_associations=parent.path_associations,
            scope_key=parent.scope_key,
            entries_retained=1,
            member_occurrences_charged=1,
            reverse_association_attempts=1,
            emitted_admission_reasons=0,
            admission_reasons=("forged-reason",) * 65,  # type: ignore[arg-type]
        )
    errors = excinfo.value.errors()
    assert len(errors) == 1
    assert errors[0]["msg"] == "Value error, emitted admission reasons exceed the hard ceiling"


def test_c8_parent_reasons_actual_g_cap_closed_before_parsing() -> None:
    """C8: positive first -- a genuine fresh parent under an ACTUAL
    stricter G diagnostic cap (max_diagnostics=1, scope recomputed)
    with zero reasons is accepted; then a negative-only two-element
    reasons sequence (under the hard 64, over the actual 1) refuses
    at the BEFORE-pARSING actual-cap gate: ONE fixed private error,
    no per-element enum errors."""
    g = CurrentAdmissionBounds(
        max_total_work_units=1024,
        max_total_entry_source_bytes=65536,
        max_diagnostics=1,
    )
    ns, s0, r, actual_g, key_record, root_entry, parent = _s_parent(MODES[0], "s-c8-g", g_bounds=g)
    assert actual_g is g and parent.g_bounds is g
    with pytest.raises(
        ValidationError, match="exceed the actual diagnostic caps before parsing"
    ) as excinfo:
        RootRegionAdmission(
            state=s0,
            ns=ns,
            r_result=r,
            g_bounds=g,
            root_entry=root_entry,
            path_associations=parent.path_associations,
            scope_key=parent.scope_key,
            entries_retained=1,
            member_occurrences_charged=1,
            reverse_association_attempts=1,
            emitted_admission_reasons=0,
            admission_reasons=("forged-reason",) * 2,  # type: ignore[arg-type]
        )
    assert len(excinfo.value.errors()) == 1


def test_c8_parent_reasons_inherited_cap_closed_before_parsing() -> None:
    """C8: the INHERITED admission diagnostic cap (the P
    namespace's actual BundleAdmissionBounds.max_diagnostics) is
    likewise closed BEFORE element parsing: a genuine namespace
    with the actual stricter inherited cap accepts zero reasons
    first, then a two-element reasons sequence (under the hard 64
    and the default G cap, over the actual inherited 1) is ONE
    fixed private error."""
    # The actual stricter inherited admission cap is bound through
    # the ACTUAL D factory (the P bootstrap's ``bounds`` kwarg is
    # the H bound set, never the inherited admission set):
    admission = make_bundle_admission_namespace(
        IDENTITY,
        model_identity="synthetic-history-model",
        config_fingerprint=FINGERPRINT,
        workspace=WORKSPACE,
        mode=MODES[0],
        bounds=BundleAdmissionBounds(max_diagnostics=1),
    )
    ns = make_root_region_lineage_namespace(admission, "s-c8-inherited")
    boot = bootstrap_root_region_lineage((root_request(),), ns)
    assert boot.outcome is RootLineageOutcome.ACCEPTED
    s0 = boot.state
    r = derive_root_region_graph(s0, ns)
    assert r.outcome is RootRegionGraphOutcome.READY
    g = CurrentAdmissionBounds()
    key_record = _s_root_key_record(ns, s0)
    root_entry = RootRegionAdmissionEntry(
        entry_class=EntryClass.ROOT_ENTRY,
        content_key=key_record.content_key,
        key_record=key_record,
        width=1,
        member_classes=(MemberClass.ELIGIBLE,),
        root_digest=key_record.root_digest,
        root_source=r.resolved_source,
    )
    row = CurrentAdmissionPathAssociation(
        scoped_key=ns.admission_scoped_key,
        path=ROOT_FILENAME,
        content_keys=(key_record.content_key,),
        is_root=True,
    )
    scope_key = root_region_admission_model_scope_key(
        s0.lineage_key,
        ROOT_REGION_ADMISSION_MODELS_CONTRACT_VERSION,
        ROOT_REGION_ADMISSION_MODELS_POLICY_VERSION,
        r.scope_key,
        CURRENT_ADMISSION_CONTRACT_VERSION,
        CURRENT_ADMISSION_POLICY_VERSION,
        g,
    )
    parent = RootRegionAdmission(
        state=s0,
        ns=ns,
        r_result=r,
        g_bounds=g,
        root_entry=root_entry,
        path_associations=(row,),
        scope_key=scope_key,
        entries_retained=1,
        member_occurrences_charged=1,
        reverse_association_attempts=1,
        emitted_admission_reasons=0,
    )
    assert parent.ns is ns and ns.bounds.max_diagnostics == 1  # positive first
    with pytest.raises(
        ValidationError, match="exceed the actual diagnostic caps before parsing"
    ) as excinfo:
        RootRegionAdmission(
            state=s0,
            ns=ns,
            r_result=r,
            g_bounds=g,
            root_entry=root_entry,
            path_associations=(row,),
            scope_key=scope_key,
            entries_retained=1,
            member_occurrences_charged=1,
            reverse_association_attempts=1,
            emitted_admission_reasons=0,
            admission_reasons=("forged-reason",) * 2,  # type: ignore[arg-type]
        )
    assert len(excinfo.value.errors()) == 1


def test_c8_parent_provided_bounds_closed_before_parsing() -> None:
    """C8: positive first -- a genuine fresh parent under an ACTUAL
    stricter G bound copy (the ORIGINAL class and legal values) is
    accepted; then NEGATIVE-only malformed PROVIDED bound records
    refuse at the BEFORE-pARSING closure with their OWN fixed
    private error and ZERO per-element enum errors (a malformed
    provided record is never skipped to a silent valid-cap
    fallback over its valid-looking sibling scalar): the actual G
    copy with max_total_work_units=0 (other original fields, actual
    max_diagnostics=64) and the actual inherited admission bounds
    copy with max_diagnostics=0, each with a two-element reasons
    sequence under the hard 64."""
    ns, s0, r, g, key_record, root_entry, parent = _s_parent(MODES[0], "s-c8-provided")
    strict = CurrentAdmissionBounds(
        max_total_work_units=2048,
        max_total_entry_source_bytes=131072,
        max_diagnostics=16,
    )
    ns2, s02, r2, actual2, key_record2, root_entry2, parent2 = _s_parent(
        MODES[0], "s-c8-provided-strict", g_bounds=strict
    )
    assert actual2 is strict and parent2.g_bounds is strict  # positive first
    bad_g = strict.model_copy(update={"max_total_work_units": 0})
    with pytest.raises(
        ValidationError,
        match="the provided G admission bounds must be closed under the original class and ranges",
    ) as excinfo:
        RootRegionAdmission(
            state=s02,
            ns=ns2,
            r_result=r2,
            g_bounds=bad_g,
            root_entry=root_entry2,
            path_associations=parent2.path_associations,
            scope_key=parent2.scope_key,
            entries_retained=1,
            member_occurrences_charged=1,
            reverse_association_attempts=1,
            emitted_admission_reasons=0,
            admission_reasons=("forged-reason",) * 2,  # type: ignore[arg-type]
        )
    errors = excinfo.value.errors()
    assert len(errors) == 1
    assert (
        errors[0]["msg"] == "Value error, the provided G admission bounds must be closed under the "
        "original class and ranges"
    )
    # The PROVIDED inherited admission bounds close the same way
    # (a MISSING attribute is the field-existence fence's own error,
    # so only a PRESENT malformed record reaches this cap gate).
    bad_ns_bounds = ns2.bounds.model_copy(update={"max_diagnostics": 0})
    bad_ns = ns2.model_copy(update={"bounds": bad_ns_bounds})
    with pytest.raises(
        ValidationError,
        match="the provided inherited admission bounds must be closed under the "
        "original class and ranges",
    ) as excinfo:
        RootRegionAdmission(
            state=s02,
            ns=bad_ns,
            r_result=r2,
            g_bounds=strict,
            root_entry=root_entry2,
            path_associations=parent2.path_associations,
            scope_key=parent2.scope_key,
            entries_retained=1,
            member_occurrences_charged=1,
            reverse_association_attempts=1,
            emitted_admission_reasons=0,
            admission_reasons=("forged-reason",) * 2,  # type: ignore[arg-type]
        )
    assert len(excinfo.value.errors()) == 1


def test_c2_leaf_bypassed_witness_refused() -> None:
    """C2: a bypassed PARTIAL witness (no closed fields) carried
    directly in the entry constructor is a fixed private error
    BEFORE the canonical coordinate sort reads any field (never an
    attribute error in the sorter).  ACTUAL PRECEDENCE: on the
    ROOT row (proof None) the BEFORE-parse witness COUNT gate
    closes the nonempty witness vector FIRST -- the fixed
    "evidenced, never a fabricated read witness" error, ONE error,
    before the witness field validator or the sorter can read the
    partial fields (the original no-attribute-error property, now
    enforced even earlier); the partial-witness FIELD closure under
    a closed FILE proof context is the companion negative in
    ``test_d1_raw_witness_container_and_count_before_parsing``."""
    ns, s0, r, g, key_record, root_entry, parent = _s_parent(MODES[0], "s-c2-witness")
    partial_witness = CurrentAdmissionWitness.model_construct()
    with pytest.raises(
        ValidationError, match="evidenced, never a fabricated read witness"
    ) as excinfo:
        RootRegionAdmissionEntry(
            entry_class=EntryClass.ROOT_ENTRY,
            content_key=key_record.content_key,
            key_record=key_record,
            width=1,
            member_classes=(MemberClass.ELIGIBLE,),
            root_digest=key_record.root_digest,
            root_source=r.resolved_source,
            witnesses=(partial_witness,),
        )
    assert len(excinfo.value.errors()) == 1


# --- C9-C12: context, reverse relation, identity splices, partitions ---


def _offset_component() -> tuple[Any, ...]:
    """The LEAN offset fixture: a standalone A read plus a mixed
    B|A read of the same A bytes at a different original offset
    (the A entry retains the FIRST proof and BOTH witnesses)."""
    mode = AdmissionMode.LEAN
    endpoint = ENDPOINTS[0]
    body = "Synthetic shared A.\n"
    ns, state = r_bootstrap(mode, f"s-c-offset-{endpoint}", root_body="Read `A.md` before work.")
    t1 = r_issue(state, ns, "off-first-A", endpoint, (CAUSAL_ROOT_FACT,), "cat A.md")
    assert t1.outcome.value == "accepted", t1.diagnostics
    t2 = r_observe(t1.state, ns, (read_request(endpoint, "off-first-A", body, "cat A.md"),))
    assert t2.outcome.value == "accepted", t2.diagnostics
    state = t2.state
    cmd = "cat B.md && echo 'SYNTHETICSEP' && cat A.md"
    t3 = r_issue(state, ns, "off-mixed-BA", endpoint, (CAUSAL_ROOT_FACT,), cmd)
    assert t3.outcome.value == "accepted", t3.diagnostics
    t4 = r_observe(
        t3.state,
        ns,
        (
            read_request(
                endpoint,
                "off-mixed-BA",
                _mixed_body("Synthetic longer unrelated prefix.\n", "SYNTHETICSEP", body),
                cmd,
            ),
        ),
    )
    assert t4.outcome.value == "accepted", t4.diagnostics
    state = t4.state
    r, g, root_entry, files, parent, _diag = _s_component_parent(state, ns)
    return ns, state, r, g, root_entry, files, parent


def test_c9_foreign_namespace_context_refused() -> None:
    """C: a copied P namespace carrying a FOREIGN principal, session,
    repository, route, model identity, configuration fingerprint,
    workspace or mode is refused.  The format-legal foreign identity
    fields and mode reach the parent's ACTUAL D-scope re-derivation:
    the reconstructed D namespace with the stale carried scope tags
    fails the actual D validators (the keys recompute from the
    actual fields, so equal copied tags alone prove nothing).  The
    malformed-hex foreign config fingerprint and the non-canonical
    (relative) foreign workspace are the ACTUAL namespace
    scalar/shape gates' fixed private errors BEFORE the shared
    target (the actual new precedence).  A format-legal foreign
    canonical absolute workspace passes those shape gates and is
    refused by the ACTUAL nested envelope-fact workspace join (the
    retained envelope fact still binds the original namespace
    workspace) before the shared target; every original stimulus is
    retained unchanged."""
    ns, s0, r, g, key_record, root_entry, parent = _s_parent(MODES[0], "s-c9")
    other = "foreign-018s-c9"

    def _refused(forged_ns: Any, pattern: str) -> None:
        with pytest.raises(ValidationError, match=pattern):
            RootRegionAdmission(
                state=s0,
                ns=forged_ns,
                r_result=r,
                g_bounds=g,
                root_entry=root_entry,
                path_associations=parent.path_associations,
                scope_key=parent.scope_key,
                entries_retained=parent.entries_retained,
                member_occurrences_charged=parent.member_occurrences_charged,
                reverse_association_attempts=parent.reverse_association_attempts,
                emitted_admission_reasons=parent.emitted_admission_reasons,
            )

    for field, value in (
        ("principal", other),
        ("session", other),
        ("repository", other),
        ("route", other),
        ("model_identity", other),
        ("mode", MODES[1]),
    ):
        _refused(
            ns.model_copy(update={field: value}),
            "the carried namespace must re-derive through the actual D validators",
        )
    # the MALFORMED-HEX foreign config fingerprint and the
    # NON-CANONICAL (relative) foreign workspace are the actual
    # namespace scalar/shape gates' fixed private errors before the
    # shared target (the actual new precedence)
    _refused(
        ns.model_copy(update={"config_fingerprint": other}),
        "the carried namespace config fingerprint must be a 64-hex digest",
    )
    _refused(
        ns.model_copy(update={"workspace": other}),
        "the carried namespace workspace must be the canonical absolute POSIX",
    )
    # a LEGAL foreign canonical absolute workspace passes the
    # namespace scalar/shape gates and is refused by the ACTUAL
    # nested envelope-fact workspace join (the retained envelope
    # fact still binds the ORIGINAL namespace workspace), the
    # actual new precedence before the shared target
    _refused(
        ns.model_copy(update={"workspace": "/" + other}),
        "the envelope fact workspace must equal the actual namespace workspace",
    )


def test_c10_reverse_relation_exactness_refused() -> None:
    """C: the complete reverse relation maps EVERY represented path
    to ALL AND ONLY the actual admitted content keys: an extra
    unowned path, a missing represented path, an extra admitted
    key on a path, a foreign scoped key and a wrong root flag each
    refuse at the admission parent with the exact fixed error."""
    ns, state, r, g, root_entry, files, parent = _offset_component()
    rows = parent.path_associations
    a_row = next(row for row in rows if row.path == "A.md")
    a_key = a_row.content_keys[0]
    root_key = parent.root_entry.content_key

    def _parent_with(new_rows: tuple[Any, ...]) -> None:
        with pytest.raises(
            ValidationError,
            match="the reverse index covers exactly the represented member paths in order",
        ):
            RootRegionAdmission(
                state=state,
                ns=ns,
                r_result=r,
                g_bounds=g,
                root_entry=root_entry,
                entries=files,
                path_associations=new_rows,
                scope_key=parent.scope_key,
                entries_retained=parent.entries_retained,
                member_occurrences_charged=parent.member_occurrences_charged,
                reverse_association_attempts=parent.reverse_association_attempts,
                emitted_admission_reasons=parent.emitted_admission_reasons,
            )

    # an EXTRA unowned path
    extra = CurrentAdmissionPathAssociation(
        scoped_key=ns.admission_scoped_key,
        path="UNOWNED.md",
        content_keys=(a_key,),
        is_root=False,
    )
    _parent_with(tuple(sorted((*rows, extra), key=lambda x: x.path)))
    # a MISSING represented path (the A.md row dropped)
    _parent_with(tuple(row for row in rows if row.path != "A.md"))
    # an EXTRA admitted key on the A.md path (the root key is not
    # admitted for A.md)
    with pytest.raises(
        ValidationError,
        match="the reverse index maps every path to all and only its admitted keys",
    ):
        RootRegionAdmission(
            state=state,
            ns=ns,
            r_result=r,
            g_bounds=g,
            root_entry=root_entry,
            entries=files,
            path_associations=tuple(
                row
                if row.path != "A.md"
                else row.model_copy(update={"content_keys": (a_key, root_key)})
                for row in rows
            ),
            scope_key=parent.scope_key,
            entries_retained=parent.entries_retained,
            member_occurrences_charged=parent.member_occurrences_charged,
            reverse_association_attempts=parent.reverse_association_attempts,
            emitted_admission_reasons=parent.emitted_admission_reasons,
        )
    # a FOREIGN scoped key on a row
    with pytest.raises(
        ValidationError,
        match="every reverse row binds the actual admission scoped key",
    ):
        RootRegionAdmission(
            state=state,
            ns=ns,
            r_result=r,
            g_bounds=g,
            root_entry=root_entry,
            entries=files,
            path_associations=tuple(
                row if row.path != "A.md" else row.model_copy(update={"scoped_key": "0" * 64})
                for row in rows
            ),
            scope_key=parent.scope_key,
            entries_retained=parent.entries_retained,
            member_occurrences_charged=parent.member_occurrences_charged,
            reverse_association_attempts=parent.reverse_association_attempts,
            emitted_admission_reasons=parent.emitted_admission_reasons,
        )
    # a WRONG root flag on the root row
    with pytest.raises(
        ValidationError,
        match="root association flags must match the root path",
    ):
        RootRegionAdmission(
            state=state,
            ns=ns,
            r_result=r,
            g_bounds=g,
            root_entry=root_entry,
            entries=files,
            path_associations=tuple(
                row if row.path != ROOT_FILENAME else row.model_copy(update={"is_root": False})
                for row in rows
            ),
            scope_key=parent.scope_key,
            entries_retained=parent.entries_retained,
            member_occurrences_charged=parent.member_occurrences_charged,
            reverse_association_attempts=parent.reverse_association_attempts,
            emitted_admission_reasons=parent.emitted_admission_reasons,
        )


def test_c11_original_identity_splice_refused() -> None:
    """C: original identity, not value equality: a genuine LATER R
    result (same selected root digest) spliced onto the EARLIER state
    refuses on the exact-state reference law; a DETACHED value-equal
    FILE proof clone, a witness naming a non-original occurrence and
    a witness with altered original coordinates each refuse at the
    admission parent before any source walk."""
    endpoint = ENDPOINTS[0]
    text_v = "Read `A.md` before work."
    ns, s1 = r_bootstrap(MODES[0], f"s-c11-{endpoint}", root_body=text_v)
    t1 = r_issue(s1, ns, "c11-whole", endpoint, (CAUSAL_ROOT_FACT,), "cat AGENTS.md")
    assert t1.outcome.value == "accepted", t1.diagnostics
    t2 = r_observe(
        t1.state,
        ns,
        (read_request(endpoint, "c11-whole", text_v, "cat AGENTS.md"),),
    )
    assert t2.outcome.value == "accepted", t2.diagnostics
    s2 = t2.state
    mix_cmd = f"cat A.md && echo '{MARK}' && cat AGENTS.md"
    t3 = r_issue(
        s2, ns, "c11-region", endpoint, (s2.d_state.occurrences[-1].occurrence_id,), mix_cmd
    )
    assert t3.outcome.value == "accepted", t3.diagnostics
    t4 = r_observe(
        t3.state,
        ns,
        (read_request(endpoint, "c11-region", _mixed_body(A_TEXT, MARK, text_v), mix_cmd),),
    )
    assert t4.outcome.value == "accepted", t4.diagnostics
    s3 = t4.state
    r2 = derive_root_region_graph(s2, ns)
    r3 = derive_root_region_graph(s3, ns)
    assert r2.outcome is RootRegionGraphOutcome.READY
    assert r3.outcome is RootRegionGraphOutcome.READY
    # the SAME selected root digest at both state points
    assert r2.resolved_source is not None and r3.resolved_source is not None
    assert r2.resolved_source.root_digest == r3.resolved_source.root_digest
    r, g, root_entry, _files, parent, _diag = _s_component_parent(s3, ns)
    # (a) the later genuine R result over the earlier state
    with pytest.raises(
        ValidationError,
        match="the R result must carry the EXACT input P state by reference",
    ):
        RootRegionAdmission(
            state=s2,
            ns=ns,
            r_result=r3,
            g_bounds=g,
            root_entry=root_entry,
            path_associations=parent.path_associations,
            scope_key=parent.scope_key,
            entries_retained=parent.entries_retained,
            member_occurrences_charged=parent.member_occurrences_charged,
            reverse_association_attempts=parent.reverse_association_attempts,
            emitted_admission_reasons=parent.emitted_admission_reasons,
        )
    # (b)-(d) the FILE identity forgeries on the offset fixture
    ns_o, state_o, r_o, g_o, root_entry_o, files_o, parent_o = _offset_component()

    def _parent_with_entries(new_entries: tuple[Any, ...]) -> RootRegionAdmission:
        return RootRegionAdmission(
            state=state_o,
            ns=ns_o,
            r_result=r_o,
            g_bounds=g_o,
            root_entry=root_entry_o,
            path_associations=parent_o.path_associations,
            scope_key=parent_o.scope_key,
            entries_retained=parent_o.entries_retained,
            member_occurrences_charged=parent_o.member_occurrences_charged,
            reverse_association_attempts=parent_o.reverse_association_attempts,
            emitted_admission_reasons=parent_o.emitted_admission_reasons,
            entries=new_entries,
        )

    a_entry = next(e for e in files_o if e.key_record.member_occurrences == ("A.md",))
    assert len(a_entry.witnesses) == 2
    # (b) a DETACHED value-equal clone of the retained FILE proof
    import copy as _copy

    forged_entry = a_entry.model_copy(update={"proof": _copy.deepcopy(a_entry.proof)})
    with pytest.raises(
        ValidationError,
        match="the file entry proof must be an original D-state retained proof",
    ):
        _parent_with_entries((forged_entry,))
    # (c) a witness naming a MALFORMED (non-hex) occurrence ID: the
    # closed coordinate shape refuses BEFORE any membership lookup
    # (fixed private channel; the raw value is never echoed)
    forged_w = a_entry.witnesses[1].model_copy(
        update={"occurrence_id": a_entry.witnesses[1].occurrence_id + "-forged"}
    )
    forged_entry = a_entry.model_copy(update={"witnesses": (a_entry.witnesses[0], forged_w)})
    with pytest.raises(
        ValidationError,
        match="occurrence_id must be a 64-hex digest",
    ):
        _parent_with_entries((forged_entry,))
    # (c2) a witness naming a VALID 64-hex occurrence ID that is
    # ABSENT from the input state: the canonical order is preserved
    # (the forged ID strictly exceeds the first witness's ID), so
    # the refusal is the original-membership join, not the shape or
    # order law
    first_id = a_entry.witnesses[0].occurrence_id
    assert first_id[-1] != "f"
    absent_id = first_id[:-1] + chr(ord(first_id[-1]) + 1)
    assert len(absent_id) == 64
    forged_w = a_entry.witnesses[1].model_copy(update={"occurrence_id": absent_id})
    forged_entry = a_entry.model_copy(update={"witnesses": (a_entry.witnesses[0], forged_w)})
    with pytest.raises(
        ValidationError,
        match="the file witness must name an original D-state occurrence",
    ):
        _parent_with_entries((forged_entry,))
    # (d) a witness with ALTERED original coordinates
    forged_w = a_entry.witnesses[1].model_copy(
        update={"call_position": a_entry.witnesses[1].call_position + 1}
    )
    forged_entry = a_entry.model_copy(update={"witnesses": (a_entry.witnesses[0], forged_w)})
    with pytest.raises(
        ValidationError,
        match="the file witness must carry the original occurrence coordinates",
    ):
        _parent_with_entries((forged_entry,))


def test_c12_leaf_partition_forgery_refused() -> None:
    """C: the N retained-content partition law on the admitted FILE
    segments.  This fixture's A entry retains ONE proof segment, so
    the duplicated two-index vector is refused at BOTH boundaries by
    the closed O(1) admitted-count domain gate (the constructor
    BEFORE-parsing gate / the shared leaf law's before-any-walk gate)
    before the AFTER distinctness law can run (changed precedence,
    the preparse proof-context batch); a count-valid duplicate on a
    genuine two-segment proof exercises the AFTER distinctness law
    in test_c12b_file_retained_interval_and_index_laws_positive_first.
    The carried forgery remains a
    bypassed model_copy re-checked by the shared leaf law."""
    ns, state, r, g, root_entry, files, parent = _offset_component()
    a_entry = next(e for e in files if e.key_record.member_occurrences == ("A.md",))

    def _entry_with(admitted_segments: tuple[int, ...]) -> RootRegionAdmissionEntry:
        return RootRegionAdmissionEntry(
            entry_class=a_entry.entry_class,
            content_key=a_entry.content_key,
            key_record=a_entry.key_record,
            width=a_entry.width,
            member_classes=a_entry.member_classes,
            root_digest=a_entry.root_digest,
            proof=a_entry.proof,
            admitted_segments=admitted_segments,
            witnesses=a_entry.witnesses,
        )

    # leaf: non-distinct indices; two indices over the one retained
    # segment hit the closed O(1) count gate before parsing
    with pytest.raises(
        ValidationError,
        match="admitted segments exceed the actual proof segment domain before parsing",
    ):
        _entry_with((0, 0))
    # leaf: a count-valid index outside the retained proof segments
    # (reaches the AFTER index law)
    with pytest.raises(
        ValidationError,
        match="admitted segment indices must index the proof segments",
    ):
        _entry_with((1,))
    # admission parent: the same forgery carried by a bypassed copy;
    # the shared leaf law's O(1) count gate runs before any walk
    with pytest.raises(
        ValidationError,
        match="admitted segments exceed the actual proof segment domain before any walk",
    ):
        RootRegionAdmission(
            state=state,
            ns=ns,
            r_result=r,
            g_bounds=g,
            root_entry=root_entry,
            entries=(a_entry.model_copy(update={"admitted_segments": (0, 0)}),),
            path_associations=parent.path_associations,
            scope_key=parent.scope_key,
            entries_retained=parent.entries_retained,
            member_occurrences_charged=parent.member_occurrences_charged,
            reverse_association_attempts=parent.reverse_association_attempts,
            emitted_admission_reasons=parent.emitted_admission_reasons,
        )


def test_c12b_file_retained_interval_and_index_laws_positive_first() -> None:
    """C12b: the FILE retained-interval and admitted-index laws on a
    GENUINE two-segment B|A proof (the fixture C12 uses retains ONE
    segment, so its duplicate vector hits the earlier O(1) count
    gate; this fixture restores the count-valid AFTER law).  Built
    through the factored core: genuine public P bootstrap -> issued
    mixed region -> actual R READY -> actual generic G FILE
    assembly -> fresh S parent.  The slice statement of the shared
    leaf law is COUNTED, not assumed.  Positive FIRST: the genuine
    entry re-constructed through the direct constructor (proof
    identity retained, one slice) and the fresh S parent
    re-constructed from its own fields (one slice per admitted FILE
    segment).  Then negative-only coherent copies: the count-valid
    duplicated/decreasing index vectors refuse the AFTER
    distinctness law at leaf AND carried parent before any slice,
    the count-valid out-of-range index refuses the AFTER index law,
    and the forged preceding interval (its character length alone
    exceeds the retained source, coherently re-keyed to the empty
    aggregate) refuses the retained partition law at leaf AND
    carried parent before any slice -- exactly the forgery the old
    silent-empty-slice behavior accepted."""
    ns, state = qf.q_bootstrap(MODES[0], "s-file-interval", "Read `A.md` before work.")
    cmd = "cat B.md && echo 'QSEP' && cat A.md"
    state = qf.q_observe(
        qf.q_issue(state, ns, "mixed", "responses", cmd, (CAUSAL_ROOT_FACT,)),
        ns,
        "responses",
        "mixed",
        qf.mixed_body("Unrelated prefix.", qf.MARK, "A body."),
        cmd,
    )
    r, _g, _root, files, parent, _diags = _s_component_parent(state, ns)
    entry = next(
        e
        for e in files
        if e.key_record.member_occurrences == ("A.md",)
        and e.proof is not None
        and len(e.proof.segments) == 2
    )
    proof: BundleProof | None = entry.proof
    assert proof is not None
    assert entry.admitted_segments == (1,)
    assert len(proof.source_text) == proof.segments[0].char_length + proof.segments[1].char_length
    fields = {name: getattr(entry, name) for name in type(entry).model_fields}
    parent_kwargs = {name: getattr(parent, name) for name in type(parent).model_fields}

    # The shared leaf law's ACTUAL slice statement, counted by line
    # (the fixture must keep exactly one such statement).
    lines, first = inspect.getsourcelines(_s_entry_leaf_closed)
    selected = [
        first + i for i, line in enumerate(lines) if "region.append(proof.source_text[" in line
    ]
    assert len(selected) == 1
    slice_line = selected[0]
    slice_hits = 0

    def _slice_trace(frame: Any, event: str, arg: Any) -> Any:
        nonlocal slice_hits
        if (
            frame.f_code is _s_entry_leaf_closed.__code__
            and event == "line"
            and frame.f_lineno == slice_line
        ):
            slice_hits += 1
        return _slice_trace

    saved_trace = sys.gettrace()
    try:
        sys.settrace(_slice_trace)
        # Positive FIRST: the genuine two-segment entry re-built
        # through the direct constructor (proof identity retained,
        # the admitted region actually sliced once).
        rebuilt = RootRegionAdmissionEntry(**fields)
        assert rebuilt.proof is proof
        assert rebuilt.admitted_segments == entry.admitted_segments
        assert slice_hits == 1
        # Positive FIRST: the fresh S parent re-constructed from its
        # own fields re-runs the leaf law per FILE entry (one slice
        # per admitted segment).
        slice_hits = 0
        rebuilt_parent = RootRegionAdmission(**parent_kwargs)
        assert rebuilt_parent.state is state and rebuilt_parent.r_result is r
        expected_slices = sum(
            len(e.admitted_segments) for e in parent.entries if e.proof is not None
        )
        assert slice_hits == expected_slices
        # Negative only: a COUNT-VALID duplicated index vector
        # (two indices over two retained segments) reaches the AFTER
        # distinctness law at the leaf, before any slice.
        slice_hits = 0
        with pytest.raises(
            ValidationError,
            match="admitted segment indices must be distinct and increasing",
        ) as excinfo:
            RootRegionAdmissionEntry(**{**fields, "admitted_segments": (0, 0)})
        assert len(excinfo.value.errors()) == 1
        assert slice_hits == 0
        # Negative only: a COUNT-VALID decreasing vector is the same
        # AFTER law.
        slice_hits = 0
        with pytest.raises(
            ValidationError,
            match="admitted segment indices must be distinct and increasing",
        ):
            RootRegionAdmissionEntry(**{**fields, "admitted_segments": (1, 0)})
        assert slice_hits == 0
        # Negative only: a COUNT-VALID out-of-range index reaches the
        # AFTER index law (the distinctness loop passes, the final
        # index fails).
        slice_hits = 0
        with pytest.raises(
            ValidationError,
            match="admitted segment indices must index the proof segments",
        ):
            RootRegionAdmissionEntry(**{**fields, "admitted_segments": (2,)})
        assert slice_hits == 0
        # Negative only: the SAME duplicated vector carried into the
        # admission parent by a bypassed model_copy is re-refused by
        # the shared leaf law's AFTER distinctness law, before any
        # slice.
        slice_hits = 0
        with pytest.raises(
            ValidationError,
            match="admitted segment indices must be distinct and increasing",
        ) as excinfo:
            RootRegionAdmission(
                **{
                    **parent_kwargs,
                    "entries": (entry.model_copy(update={"admitted_segments": (0, 0)}),),
                }
            )
        assert len(excinfo.value.errors()) == 1
        assert slice_hits == 0
        # Negative only: the SAME decreasing vector carried into the
        # admission parent by a bypassed model_copy is the same
        # shared AFTER distinctness law, before any slice.
        slice_hits = 0
        with pytest.raises(
            ValidationError,
            match="admitted segment indices must be distinct and increasing",
        ) as excinfo:
            RootRegionAdmission(
                **{
                    **parent_kwargs,
                    "entries": (entry.model_copy(update={"admitted_segments": (1, 0)}),),
                }
            )
        assert len(excinfo.value.errors()) == 1
        assert slice_hits == 0
        # Negative only: the forged preceding interval -- its
        # character length ALONE exceeds the retained source -- with
        # the key record coherently re-keyed to the empty aggregate
        # (exactly the forgery the old silent-empty-slice behavior
        # accepted) refuses the retained partition law before any
        # slice.
        outside = len(proof.source_text) + 1
        prefix = proof.segments[0].model_copy(
            update={"char_length": outside, "byte_length": outside}
        )
        bad_proof = proof.model_copy(update={"segments": (prefix, proof.segments[1])})
        empty_digest = hashlib.sha256(b"").hexdigest()
        bad_record = entry.key_record.model_copy(update={"aggregate_source_digest": empty_digest})
        bad_key = _canonical_entry_key(bad_record)
        bad_record = bad_record.model_copy(update={"content_key": bad_key})
        assert bad_proof.segments[1].char_length > 0
        assert outside + bad_proof.segments[1].char_length > len(bad_proof.source_text)
        slice_hits = 0
        with pytest.raises(
            ValidationError,
            match="the retained segment intervals must partition the retained source text",
        ) as excinfo:
            RootRegionAdmissionEntry(
                **{**fields, "proof": bad_proof, "key_record": bad_record, "content_key": bad_key}
            )
        assert len(excinfo.value.errors()) == 1
        assert slice_hits == 0
        # Negative only: the SAME forged interval carried into the
        # admission parent by a bypassed model_copy refuses the
        # retained partition law at the shared leaf law (re-run at
        # the parent) before any slice.
        forged = entry.model_copy(
            update={"proof": bad_proof, "key_record": bad_record, "content_key": bad_key}
        )
        slice_hits = 0
        with pytest.raises(
            ValidationError,
            match="the retained segment intervals must partition the retained source text",
        ) as excinfo:
            RootRegionAdmission(**{**parent_kwargs, "entries": (forged,)})
        assert len(excinfo.value.errors()) == 1
        assert slice_hits == 0
    finally:
        sys.settrace(saved_trace)


# --- C13/C14: the complete bound-carrier matrices (M01/C) --------------


_ELEVEN_CARRIERS: tuple[tuple[str, str | None, str, int, type[Any]], ...] = (
    # (kind, carrier field, first int field, original hard ceiling,
    #  a DIFFERENT concrete bound class)
    ("ns", "bounds", "max_entries", 128, CurrentAdmissionBounds),
    ("ns", "proof_bounds", "max_bundles", 10000, GraphBounds),
    ("ns", "graph_bounds", "max_requests", 10000, ObservationBounds),
    ("ns", "observation_bounds", "max_items", 100000, HistoryBounds),
    ("ns", "history_bounds", "max_issuances", 4096, RootLineageBounds),
    ("ns", "root_lineage_bounds", "max_root_facts", 1024, RootRegionGraphBounds),
    ("r", "bounds", "max_total_work_units", 1048576, CurrentAdmissionBounds),
    ("r", "q_bounds", "max_total_work_units", 1048576, RootRegionGraphBounds),
    ("r", "f_bounds", "max_total_work_units", 1048576, RootRegionGraphBounds),
    ("r", "e_bounds", "max_paths", 16384, CurrentGraphBounds),
    ("g", None, "max_total_work_units", 1048576, RootRegionGraphBounds),
)


def test_c13_eleven_carrier_complete_matrix() -> None:
    """C: the ACTUAL eleven carried bound sets are closed under
    EVERY original concrete-class carrier BEFORE any cap is read or
    serialized: per carrier the wrong concrete class, a zero under
    the original floor of 1, a value over the original hard ceiling,
    a bool scalar and a bypassed missing field each refuse with the
    exact fixed private error (a missing carrier on the carrying NS
    or R record is the phase-0 existence fence; the G carrier's
    missing field is the phase-1 scalar fence).  The genuine
    positive population is checked first."""
    ns, s0, r, g, key_record, root_entry, parent = _s_parent(MODES[0], "s-c13")
    # positive first: the actual carried population is closed
    assert _s_all_eleven_bound_sets_closed(ns, r, g)
    phase1 = "the actual eleven carried bound sets must be closed scalar sets"
    ns_missing = "the admission parent namespace must carry its closed fields"
    r_missing = "the admission parent R result must carry its closed fields"
    bounds_closed = (
        "the provided inherited admission bounds must be closed under the original class and ranges"
    )
    cases: list[tuple[str, Any, Any, Any, str]] = []
    for kind, field, scalar, ceiling, wrong_class in _ELEVEN_CARRIERS:
        if kind == "g":
            assert field is None
            genuine: Any = g
        elif kind == "ns":
            assert field is not None
            genuine = getattr(ns, field)
        else:
            assert field is not None
            genuine = getattr(r, field)
        for label, forged in (
            (f"{kind}:{field}:wrong-class", wrong_class()),
            (f"{kind}:{field}:zero", genuine.model_copy(update={scalar: 0})),
            (f"{kind}:{field}:over", genuine.model_copy(update={scalar: ceiling + 1})),
            (f"{kind}:{field}:bool", genuine.model_copy(update={scalar: True})),
        ):
            if kind == "ns":
                nsp, rp, gp = ns.model_copy(update={field: forged}), r, g
            elif kind == "r":
                nsp, rp, gp = ns, r.model_copy(update={field: forged}), g
            else:
                nsp, rp, gp = ns, r, forged
            msg_case = phase1
            if kind == "ns" and field == "bounds":
                # the parent BEFORE-handler closes the PROVIDED
                # inherited admission bounds before any phase runs:
                # the nested ns.bounds variants carry that fixed
                # private error (the missing ns.bounds CARRIER
                # below stays the closed-fields fence)
                msg_case = bounds_closed
            if kind == "g" and label.endswith(":wrong-class"):
                # the top-level g_bounds field is an InstanceOf fence:
                # a non-subclass wrong concrete class is refused at the
                # FIELD level before any phase runs
                msg_case = "Input should be an instance of CurrentAdmissionBounds"
            cases.append((label, nsp, rp, gp, msg_case))
        # a deliberately missing-field genuine-class copy (the raw
        # instance dict loses the scalar; model_construct would
        # restore the declared default, so the bypass is explicit and
        # verified before the target is exercised)
        fmiss = genuine.model_copy()
        del fmiss.__dict__[scalar]
        assert not hasattr(fmiss, scalar)
        # a missing NESTED scalar is the phase-1 bound-set error at
        # every carrier (the carrier field itself is still present)
        if kind == "ns":
            nsp, rp, gp = ns.model_copy(update={field: fmiss}), r, g
            miss_msg = bounds_closed if field == "bounds" else phase1
            cases.append((f"{kind}:{field}:missing-scalar", nsp, rp, gp, miss_msg))
        elif kind == "r":
            nsp, rp, gp = ns, r.model_copy(update={field: fmiss}), g
            cases.append((f"{kind}:{field}:missing-scalar", nsp, rp, gp, phase1))
        else:
            cases.append((f"{kind}:g:{scalar}:missing-scalar", ns, r, fmiss, phase1))
    # the SEPARATE missing-carrier controls: a bypassed NS/R record
    # missing the bound-set FIELD itself is the phase-0 existence fence
    ns_carrier = ns.model_copy()
    del ns_carrier.__dict__["bounds"]
    assert not hasattr(ns_carrier, "bounds")
    cases.append(("ns:bounds:missing-carrier", ns_carrier, r, g, ns_missing))
    r_carrier = r.model_copy()
    del r_carrier.__dict__["bounds"]
    assert not hasattr(r_carrier, "bounds")
    cases.append(("r:bounds:missing-carrier", ns, r_carrier, g, r_missing))
    assert len(cases) == 57
    for _label, nsp, rp, gp, msg in cases:
        with pytest.raises(ValidationError, match=msg):
            RootRegionAdmission(
                state=s0,
                ns=nsp,
                r_result=rp,
                g_bounds=gp,
                root_entry=root_entry,
                path_associations=parent.path_associations,
                scope_key=parent.scope_key,
                entries_retained=parent.entries_retained,
                member_occurrences_charged=parent.member_occurrences_charged,
                reverse_association_attempts=parent.reverse_association_attempts,
                emitted_admission_reasons=parent.emitted_admission_reasons,
            )


def test_c14_canonical4_key_record_matrix() -> None:
    """C: the FOUR canonical bound sets carried INSIDE the key record
    are closed under their exact ORIGINAL classes BEFORE the
    canonical rekey: per set the wrong concrete class, a zero under
    the original floor, a value over the original hard ceiling, a
    bool scalar and a bypassed missing field each refuse at the LEAF
    entry constructor and, carried by a bypassed root-entry copy, at
    the ADMISSION PARENT (the leaf law re-runs there).  The genuine
    positive parent is checked first."""
    ns, s0, r, g, key_record, root_entry, parent = _s_parent(MODES[0], "s-c14")
    # positive first: the genuine parent carries the closed record
    assert parent.root_entry.key_record is key_record
    msg = "the key record carried bound sets must be closed scalar sets"
    for set_field, scalar, ceiling, wrong_class in (
        ("admission_bounds", "max_entries", 128, CurrentAdmissionBounds),
        ("proof_bounds", "max_bundles", 10000, GraphBounds),
        ("graph_bounds", "max_requests", 10000, ObservationBounds),
        ("observation_bounds", "max_items", 100000, HistoryBounds),
    ):
        genuine = getattr(key_record, set_field)
        for _label, forged in (
            (f"{set_field}:wrong-class", wrong_class()),
            (f"{set_field}:zero", genuine.model_copy(update={scalar: 0})),
            (f"{set_field}:over", genuine.model_copy(update={scalar: ceiling + 1})),
            (f"{set_field}:bool", genuine.model_copy(update={scalar: True})),
        ):
            forged_record = key_record.model_copy(update={set_field: forged})
            # the LEAF constructor
            with pytest.raises(ValidationError, match=msg):
                RootRegionAdmissionEntry(
                    entry_class=EntryClass.ROOT_ENTRY,
                    content_key=key_record.content_key,
                    key_record=forged_record,
                    width=1,
                    member_classes=(MemberClass.ELIGIBLE,),
                    root_digest=key_record.root_digest,
                    root_source=r.resolved_source,
                )
            # the ADMISSION PARENT (bypassed root-entry copy)
            with pytest.raises(ValidationError, match=msg):
                RootRegionAdmission(
                    state=s0,
                    ns=ns,
                    r_result=r,
                    g_bounds=g,
                    root_entry=root_entry.model_copy(update={"key_record": forged_record}),
                    path_associations=parent.path_associations,
                    scope_key=parent.scope_key,
                    entries_retained=parent.entries_retained,
                    member_occurrences_charged=parent.member_occurrences_charged,
                    reverse_association_attempts=parent.reverse_association_attempts,
                    emitted_admission_reasons=parent.emitted_admission_reasons,
                )
        # a bypassed missing field INSIDE the carried set (the raw
        # instance dict loses the scalar; model_construct would
        # restore the declared default, so the bypass is explicit and
        # verified before the target is exercised)
        fmiss = genuine.model_copy()
        del fmiss.__dict__[scalar]
        assert not hasattr(fmiss, scalar)
        forged_record = key_record.model_copy(update={set_field: fmiss})
        with pytest.raises(ValidationError, match=msg):
            RootRegionAdmissionEntry(
                entry_class=EntryClass.ROOT_ENTRY,
                content_key=key_record.content_key,
                key_record=forged_record,
                width=1,
                member_classes=(MemberClass.ELIGIBLE,),
                root_digest=key_record.root_digest,
                root_source=r.resolved_source,
            )
        with pytest.raises(ValidationError, match=msg):
            RootRegionAdmission(
                state=s0,
                ns=ns,
                r_result=r,
                g_bounds=g,
                root_entry=root_entry.model_copy(update={"key_record": forged_record}),
                path_associations=parent.path_associations,
                scope_key=parent.scope_key,
                entries_retained=parent.entries_retained,
                member_occurrences_charged=parent.member_occurrences_charged,
                reverse_association_attempts=parent.reverse_association_attempts,
                emitted_admission_reasons=parent.emitted_admission_reasons,
            )


def test_c15_copied_entry_closure_refused() -> None:
    """C: a carried entry whose actual scalar/enum/tuple shapes were
    bypassed by a model_copy refuses at the admission parent (the
    leaf law re-runs the closed entry shape at leaf AND carrying
    boundary; legitimate direct-constructor normalization remains
    distinct).  The genuine positive parent is accepted FIRST."""
    ns, state, r, g, root_entry, files, parent = _offset_component()
    entry = files[0]
    # positive first: the genuine parent with its closed entries
    assert parent.state is state and parent.root_entry is root_entry
    assert parent.entries == tuple(files) and len(entry.witnesses) == 2
    original_by_id = {o.occurrence_id: o for o in state.d_state.occurrences}
    first_proof_witness = next(
        w for w in entry.witnesses if original_by_id[w.occurrence_id].proof is entry.proof
    )
    width_msg = "the entry width must carry a closed positive integer"
    class_msg = "the entry class must be the actual closed entry class"
    member_msg = "the entry member classes must be the actual closed authority classes"
    member_container_msg = "the entry member classes must carry a nonempty closed tuple"
    witness_container_msg = "the entry witnesses must carry the closed tuple container"
    order_msg = "witnesses must be sorted and deduplicated"
    cases: list[tuple[str, Any, str]] = [
        ("root-width-bool", root_entry.model_copy(update={"width": True}), width_msg),
        ("file-width-bool", entry.model_copy(update={"width": True}), width_msg),
        (
            "file-entry-class-raw-string",
            entry.model_copy(update={"entry_class": entry.entry_class.value}),
            class_msg,
        ),
        (
            "root-member-classes-raw-strings",
            root_entry.model_copy(
                update={"member_classes": tuple(m.value for m in root_entry.member_classes)}
            ),
            member_msg,
        ),
        (
            "file-member-classes-mutable-list",
            entry.model_copy(update={"member_classes": list(entry.member_classes)}),
            member_container_msg,
        ),
        (
            "file-witnesses-mutable-list",
            entry.model_copy(update={"witnesses": list(entry.witnesses)}),
            witness_container_msg,
        ),
        (
            "file-witness-order-reversed",
            entry.model_copy(update={"witnesses": tuple(reversed(entry.witnesses))}),
            order_msg,
        ),
        (
            "file-duplicate-first-proof-witness",
            entry.model_copy(update={"witnesses": (first_proof_witness, first_proof_witness)}),
            order_msg,
        ),
    ]
    assert len(cases) == 8
    for label, forged, msg in cases:
        if label.startswith("root"):
            args = dict(parent.__dict__)
            args["root_entry"] = forged
        else:
            args = dict(parent.__dict__)
            args["entries"] = (forged,)
        with pytest.raises(ValidationError, match=msg):
            RootRegionAdmission(**args)


def test_c16_original_owner_and_witness_scalar_closure_refused() -> None:
    """C: the M04 owner join and the non-bool witness coordinate law
    at the carrying boundary: a coherently rebound copied state/R/Q/F
    chain whose D results are all missing, incomplete or emptied of
    their piece producer association refuses (occurrence/proof
    presence alone is insufficient), and a bypassed bool at an
    actual 0/1 witness coordinate refuses before the canonical sort
    reads it.  The genuine positive parent is accepted FIRST."""
    ns, state, r, g, root_entry, files, parent = _offset_component()
    q_result = r.q_result
    f_result = r.f_result
    assert q_result is not None and f_result is not None
    # positive first: the genuine parent joins its original owners
    assert parent.state is state and parent.r_result is r and len(files) == 1
    owner_cases = [
        (
            "missing-all-owning-results",
            (),
            "the retained occurrence must join its owning result record",
        ),
        (
            "incomplete-owning-results",
            tuple(x.model_copy(update={"complete": False}) for x in state.d_state.results),
            "the retained occurrence must join its complete owning result",
        ),
        (
            "emptied-piece-producer-association",
            tuple(x.model_copy(update={"piece_call_bindings": ()}) for x in state.d_state.results),
            "the owning result retains the exact piece producer association",
        ),
    ]
    # the THREE coherent owner mutations: the owning result's immutable
    # call binding changed TOGETHER with its own piece bindings while
    # the ORIGINAL occurrence stays unchanged (a result-to-own-binding
    # comparison alone would admit these; the join must run against
    # the original occurrence identity).
    for field, binding_index, value in (
        ("argument_fingerprint", 3, "f" * 64),
        ("tool_name", 2, "shell_command"),
        ("endpoint", 1, "/v1/chat/completions"),
    ):
        mutated = tuple(
            x.model_copy(
                update={
                    field: value,
                    "piece_call_bindings": tuple(
                        tuple(
                            value if i == binding_index else part for i, part in enumerate(binding)
                        )
                        for binding in x.piece_call_bindings
                    ),
                }
            )
            for x in state.d_state.results
        )
        owner_cases.append(
            (
                f"coherent-foreign-owner-{field}",
                mutated,
                "the owning result keeps the original call's immutable binding",
            )
        )
    assert len(owner_cases) == 6
    for _label, results, msg in owner_cases:
        d_state = state.d_state.model_copy(update={"results": results})
        p_state = state.model_copy(update={"d_state": d_state})
        neg_r = r.model_copy(
            update={
                "state": p_state,
                "q_result": q_result.model_copy(update={"state": p_state}),
                "f_result": f_result.model_copy(update={"state": d_state}),
            }
        )
        args = dict(parent.__dict__)
        args.update(state=p_state, r_result=neg_r)
        with pytest.raises(ValidationError, match=msg):
            RootRegionAdmission(**args)
    # the six measured bool-coordinate copies at actual 0/1 values
    entry = files[0]
    bool_cases: list[tuple[str, Any]] = []
    for field in ("request_index", "call_position", "result_position"):
        for position, witness in enumerate(entry.witnesses):
            value = getattr(witness, field)
            if value not in (0, 1):
                continue
            bad_witness = witness.model_copy(update={field: bool(value)})
            bad_witnesses = tuple(
                bad_witness if i == position else old for i, old in enumerate(entry.witnesses)
            )
            forged = entry.model_copy(update={"witnesses": bad_witnesses})
            bool_cases.append((f"{field}-{position}-bool", forged))
    assert len(bool_cases) == 6  # measured on this deterministic fixture
    for _label, forged in bool_cases:
        args = dict(parent.__dict__)
        args["entries"] = (forged,)
        with pytest.raises(
            ValidationError,
            match="witness coordinates must carry closed nonnegative integers",
        ):
            RootRegionAdmission(**args)


def test_c17_nonready_rq_carrying_boundary_refused() -> None:
    """C: the carrying-boundary READY outcome invariants: a
    bypassed carried R result whose outcome is any NON-READY
    member refuses the fixed private parent gate BEFORE the shared
    R target (zero hits), and a carried Q result / P selection
    whose outcome is non-READY / non-OK inside the otherwise-ready
    R refuses the ACTUAL shared R ready invariants (the real
    shared target is reached once and then refuses).  The genuine
    public P/R -> fresh S parent positive is accepted FIRST.  No
    old public law, cap or revalidation change."""
    ns, s0, r, g, _kr, _entry, parent = _s_parent(MODES[0], "s-c17")
    q = r.q_result
    assert q is not None
    p = q.p_selection
    assert p is not None
    kwargs: dict[str, Any] = {name: getattr(parent, name) for name in type(parent).model_fields}
    hits = 0
    real_target = _r_result_closed

    def _counting_target(result: RootRegionGraphResult) -> None:
        nonlocal hits
        hits += 1
        real_target(result)

    monkeypatch = pytest.MonkeyPatch()
    try:
        monkeypatch.setattr(rram, "_r_result_closed", _counting_target)
        # Positive FIRST: the genuine fresh parent accepts with
        # the real shared target actually reached once.
        rebuilt = RootRegionAdmission(**kwargs)
        assert rebuilt.state is s0 and rebuilt.r_result is r and rebuilt.ns is ns
        assert hits == 1
        # Negative only: each NON-READY R outcome copy refuses the
        # fixed private parent gate before the shared target.
        for outcome in (
            RootRegionGraphOutcome.ROOT_CURRENTNESS_UNPROVEN,
            RootRegionGraphOutcome.ROOT_AUTHORITY_CONFLICT,
            RootRegionGraphOutcome.REFUSED,
        ):
            hits = 0
            with pytest.raises(
                ValidationError,
                match="a non-ready or refused R cannot describe a ready admission",
            ):
                RootRegionAdmission(
                    **{**kwargs, "r_result": r.model_copy(update={"outcome": outcome})}
                )
            assert hits == 0
        # Negative only: each non-READY Q outcome copy inside the
        # ready R is the ACTUAL shared R ready invariant (the real
        # target is reached once and then refuses).
        for q_outcome in (
            RootRegionCurrentnessOutcome.ROOT_CURRENTNESS_UNPROVEN,
            RootRegionCurrentnessOutcome.ROOT_AUTHORITY_CONFLICT,
            RootRegionCurrentnessOutcome.REFUSED,
        ):
            hits = 0
            bad_q = q.model_copy(update={"outcome": q_outcome})
            bad_r: RootRegionGraphResult = r.model_copy(update={"q_result": bad_q})
            with pytest.raises(
                ValidationError, match="ready requires the actual same-run Q ready result"
            ):
                RootRegionAdmission(**{**kwargs, "r_result": bad_r})
            assert hits == 1
        # Negative only: each non-OK P selection outcome copy
        # inside the ready Q is the ACTUAL shared R ready
        # invariant (the real target is reached once and then
        # refuses).
        for p_outcome in (
            RootSelectionOutcome.ROOT_CONTENT_CONFLICT,
            RootSelectionOutcome.NO_SELECTED_ROOT,
            RootSelectionOutcome.REFUSED,
        ):
            hits = 0
            bad_p = p.model_copy(update={"outcome": p_outcome})
            bad_q2 = q.model_copy(update={"p_selection": bad_p})
            bad_r2: RootRegionGraphResult = r.model_copy(update={"q_result": bad_q2})
            with pytest.raises(
                ValidationError,
                match="ready requires the actual nonNone OK P selection in the same-run Q result",
            ):
                RootRegionAdmission(**{**kwargs, "r_result": bad_r2})
            assert hits == 1
    finally:
        monkeypatch.undo()


def test_c18_public_nonready_r_carrying_boundary_refused() -> None:
    """C18: the carrying-boundary non-ready gate on ACTUAL PUBLIC
    non-ready R results (not copied enum outcomes; the copied
    matrix stays C17).  Genuine public P -> actual R READY ->
    fresh S parent positive FIRST (real shared target reached
    once).  Negative only, each real returned R carried into the
    fresh S parent and refused by the fixed private non-ready
    gate BEFORE the shared R target (zero hits) and before any
    selected-source work: an ACTUAL public R REFUSED derived
    under the strict valid total1 bound (genuine work-unit
    refusal: own diagnostic, the EXACT input state retained by
    reference, no source), and an ACTUAL public R whose same-run
    Q is non-ready, built from the trusted complete opaque-root
    uncertainty state through the public P issuance/observation
    chain (the actual two-branch frontier: actual Q unproven
    with its retained uncertainty witnesses, no source published,
    F never runs, the real returned R/state/ns triple carried).
    No copied positive state, no fake ready snapshot, no P/Q/R
    law change; the claim is scoped to the actual paths reached."""
    ns, s0, r, g, _kr, root_entry, parent = _s_parent(MODES[0], "s-c18")
    kwargs: dict[str, Any] = {name: getattr(parent, name) for name in type(parent).model_fields}
    hits = 0
    real_target = _r_result_closed

    def _counting_target(result: RootRegionGraphResult) -> None:
        nonlocal hits
        hits += 1
        real_target(result)

    monkeypatch = pytest.MonkeyPatch()
    try:
        monkeypatch.setattr(rram, "_r_result_closed", _counting_target)
        # Positive FIRST: the genuine public P/R -> fresh S parent
        # accepts with the real shared target actually reached
        # once.
        rebuilt = RootRegionAdmission(**kwargs)
        assert rebuilt.state is s0 and rebuilt.r_result is r and rebuilt.ns is ns
        assert hits == 1
        # Negative only: an ACTUAL public R REFUSED under the
        # strict valid total1 bound (genuine work-unit refusal:
        # own diagnostic, EXACT input state by reference, no
        # source) carried into the fresh S parent refuses the
        # fixed private non-ready gate before the shared target.
        r_refused = derive_root_region_graph(s0, ns, RootRegionGraphBounds(max_total_work_units=1))
        assert r_refused.outcome is RootRegionGraphOutcome.REFUSED
        assert r_refused.diagnostics == (RootRegionGraphDiagnostic.WORK_UNITS_OVER_BOUND,)
        assert r_refused.state is s0
        assert r_refused.resolved_source is None
        hits = 0
        with pytest.raises(
            ValidationError,
            match="a non-ready or refused R cannot describe a ready admission",
        ) as excinfo:
            RootRegionAdmission(**{**kwargs, "r_result": r_refused})
        assert len(excinfo.value.errors()) == 1
        assert hits == 0
        # Negative only: an ACTUAL public R whose same-run Q is
        # non-ready, built from the trusted complete opaque-root
        # uncertainty state through the public P issuance/
        # observation chain (the actual two-branch frontier):
        # actual Q unproven with its retained uncertainty
        # witnesses, no source published, F never runs.  The real
        # returned R/state/ns triple is carried into the fresh S
        # parent and refuses the same fixed private gate before
        # the shared target.
        ns2, state2, _v2 = qf._frontier_state(MODES[0], ENDPOINTS[0], "s-c18-frontier")
        r2 = derive_root_region_graph(state2, ns2)
        q2 = r2.q_result
        assert r2.outcome is RootRegionGraphOutcome.ROOT_CURRENTNESS_UNPROVEN
        assert r2.diagnostics == ()
        assert r2.resolved_source is None and r2.f_result is None and r2.e_overlay is None
        assert q2 is not None
        assert q2.outcome is RootRegionCurrentnessOutcome.ROOT_CURRENTNESS_UNPROVEN
        assert q2.state is state2
        assert r2.state is state2
        assert len(q2.uncertainty_witnesses) == 2
        assert q2.p_validation_problem is None
        hits = 0
        with pytest.raises(
            ValidationError,
            match="a non-ready or refused R cannot describe a ready admission",
        ) as excinfo:
            RootRegionAdmission(**{**kwargs, "state": state2, "ns": ns2, "r_result": r2})
        assert len(excinfo.value.errors()) == 1
        assert hits == 0
    finally:
        monkeypatch.undo()


# --- D1: the entry count gate (closed cap before parse/member walk) ------


class _CountingMembers(tuple[Any]):
    """A member vector whose element iteration is COUNTED: the closed
    cap gate must refuse before any iterator enters the leaf's
    per-element walk (len is O(1) and legal before the cap read)."""

    iterations = 0

    def __iter__(self) -> Any:
        _CountingMembers.iterations += 1
        return super().__iter__()


class _CountingIter:
    """A raw iterable whose element retrieval is COUNTED: the closed
    raw-sequence-class gate must refuse BEFORE any next() enters
    (Pydantic would otherwise traverse the elements unbounded
    before the after-validator)."""

    def __init__(self, items: Any) -> None:
        self._items = iter(items)
        self.n = 0

    def __iter__(self) -> _CountingIter:
        return self

    def __next__(self) -> Any:
        self.n += 1
        return next(self._items)


def test_d1_entry_count_gate_positive_and_overcount_controls() -> None:
    """D1: the entry member count gate closes the ACTUAL carried
    admission cap, the record-alignment count and the raw sequence
    container class BEFORE element parsing, and the carrying member
    walk, via the shared O(1) record preflight.  The genuine public
    P -> actual R -> fresh S parent positive (plus a legitimate
    direct constructor over raw values) is accepted FIRST; the
    negative copies run only afterwards, each with DELIBERATELY
    INVALID enum strings so that exactly ONE fixed private error
    and ZERO per-element enum errors prove the elements were never
    parsed: the raw over-cap vector, a raw count mismatch under the
    valid one-member record, an unsupported raw container class
    (zero next() on a counting iterator and a small set), and a
    wrong or missing provided record (never defaulted to a valid
    cap, never an enum storm).  A single invalid string at the
    count-valid shape passes the closed gate and reaches the
    ACTUAL enum validator (ONE per-element enum error -- the
    legitimate under-cap normalization path is intact), and a
    bypassed
    MATCHING oversized record/entry pair (1025/1025, alignment
    alone) refuses at the carrying leaf with ZERO member iterator
    visits."""
    ns, s0, r, g, key_record, root_entry, parent = _s_parent(MODES[0], "s-d1-count")
    assert parent.state is s0 and parent.r_result is r  # positive first
    assert key_record.admission_bounds.max_member_occurrences == 1024
    resolved = r.resolved_source
    assert resolved is not None
    # positive: a legitimate direct constructor over the genuine
    # ROOT entry fields with RAW member values (normalization by the
    # field validators after the closed gate is preserved).
    legit = RootRegionAdmissionEntry(
        entry_class=root_entry.entry_class,
        content_key=root_entry.content_key,
        key_record=key_record,
        width=root_entry.width,
        member_classes=[m.value for m in root_entry.member_classes],  # type: ignore[arg-type]
        root_digest=root_entry.root_digest,
        root_source=resolved,
    )
    assert legit.member_classes == root_entry.member_classes
    assert legit.key_record is key_record
    # before parsing: the raw over-cap vector under the VALID record
    # uses DELIBERATELY INVALID enum strings, so exactly ONE fixed
    # private error and ZERO per-element enum errors prove the
    # elements were never parsed (no error storm).
    with pytest.raises(
        ValidationError, match="exceed the actual carried admission cap before parsing"
    ) as excinfo:
        RootRegionAdmissionEntry(
            entry_class=root_entry.entry_class,
            content_key=root_entry.content_key,
            key_record=key_record,
            width=1,
            member_classes=("not-a-member",) * 1025,  # type: ignore[arg-type]
            root_digest=root_entry.root_digest,
            root_source=resolved,
        )
    errors = excinfo.value.errors()
    assert len(errors) == 1
    assert all(error["type"] != "enum" for error in errors)
    # a WRONG provided record class with the same over-cap vector is
    # its OWN fixed private record error BEFORE any element parsing
    # (never a per-element enum storm, never defaulted to a valid
    # cap).
    with pytest.raises(
        ValidationError, match="the entry key record must be the actual canonical record"
    ) as excinfo:
        RootRegionAdmissionEntry(
            entry_class=root_entry.entry_class,
            content_key=root_entry.content_key,
            key_record=key_record.model_dump(),  # type: ignore[arg-type]
            width=1,
            member_classes=("not-a-member",) * 1025,  # type: ignore[arg-type]
            root_digest=root_entry.root_digest,
            root_source=resolved,
        )
    errors = excinfo.value.errors()
    assert len(errors) == 1
    assert all(error["type"] != "enum" for error in errors)
    # a MISSING provided record is likewise closed before parsing
    # (the deliberate malformed dict spread is the negative under
    # test; the single per-call ignore is its precise typing
    # handling).
    missing_kwargs: dict[str, object] = {
        "entry_class": root_entry.entry_class,
        "content_key": root_entry.content_key,
        "width": 1,
        "member_classes": ("not-a-member",) * 1025,
        "root_digest": root_entry.root_digest,
        "root_source": resolved,
    }
    with pytest.raises(
        ValidationError, match="the admission entry must carry its key record"
    ) as excinfo:
        RootRegionAdmissionEntry(**missing_kwargs)  # type: ignore[arg-type]
    errors = excinfo.value.errors()
    assert len(errors) == 1
    assert all(error["type"] != "enum" for error in errors)
    # a raw count MISMATCH under the valid one-member ROOT record
    # (two DELIBERATELY INVALID enum strings are under the cap but
    # cannot align with the record occurrences) is closed BEFORE
    # element conversion: ONE fixed private error, zero enum errors.
    with pytest.raises(
        ValidationError, match="must align with the member occurrences before parsing"
    ) as excinfo:
        RootRegionAdmissionEntry(
            entry_class=root_entry.entry_class,
            content_key=root_entry.content_key,
            key_record=key_record,
            width=1,
            member_classes=("not-a-member",) * 2,  # type: ignore[arg-type]
            root_digest=root_entry.root_digest,
            root_source=resolved,
        )
    errors = excinfo.value.errors()
    assert len(errors) == 1
    assert all(error["type"] != "enum" for error in errors)
    # an UNSUPPORTED raw container class is refused before ANY
    # element retrieval: a counting iterator shows ZERO next() with
    # ONE fixed private error, and a small set likewise refuses
    # without traversal.
    raw_iter = _CountingIter(("eligible",) * 1025)
    with pytest.raises(
        ValidationError, match="must carry a closed list or tuple before parsing"
    ) as excinfo:
        RootRegionAdmissionEntry(
            entry_class=root_entry.entry_class,
            content_key=root_entry.content_key,
            key_record=key_record,
            width=1,
            member_classes=raw_iter,  # type: ignore[arg-type]
            root_digest=root_entry.root_digest,
            root_source=resolved,
        )
    assert len(excinfo.value.errors()) == 1
    assert raw_iter.n == 0
    with pytest.raises(ValidationError, match="must carry a closed list or tuple before parsing"):
        RootRegionAdmissionEntry(
            entry_class=root_entry.entry_class,
            content_key=root_entry.content_key,
            key_record=key_record,
            width=1,
            member_classes={"eligible"},  # type: ignore[arg-type]
            root_digest=root_entry.root_digest,
            root_source=resolved,
        )
    # a single invalid string at the COUNT-VALID one-member shape
    # passes the closed gate and reaches the ACTUAL enum validator:
    # exactly ONE per-element enum error at the exact element
    # location (a companion nonempty-tuple shape error is the
    # field's own min-length law, not the gate).
    with pytest.raises(ValidationError) as excinfo:
        RootRegionAdmissionEntry(
            entry_class=root_entry.entry_class,
            content_key=root_entry.content_key,
            key_record=key_record,
            width=1,
            member_classes=("not-a-member",),  # type: ignore[arg-type]
            root_digest=root_entry.root_digest,
            root_source=resolved,
        )
    # the ACTUAL exact two-error shape: ONE per-element enum error
    # at the element location plus the field's own nonempty-tuple
    # min-length error at the field location (the closed gate let
    # this count-valid shape reach the real validators).
    errors = excinfo.value.errors()
    assert [error["type"] for error in errors] == ["enum", "too_short"]
    assert errors[0]["loc"] == ("member_classes", 0)
    assert errors[1]["loc"] == ("member_classes",)
    # carrying boundary: a model_construct-bypassed MATCHING
    # oversized record/entry vector pair (1025/1025 -- alignment
    # alone) refuses at the shared O(1) preflight BEFORE any member
    # iterator visit, at the leaf AND the admission-parent re-run
    # (real target sentinel: zero visits).
    _CountingMembers.iterations = 0
    big_occ = _CountingMembers((ROOT_FILENAME,) * 1025)
    big_cls = _CountingMembers((MemberClass.ELIGIBLE,) * 1025)
    forged = key_record.model_construct(
        **_forged_record_fields(key_record, member_occurrences=big_occ, member_classes=big_cls)
    )
    forged_entry = root_entry.model_construct(
        **{
            **{name: getattr(root_entry, name) for name in root_entry.model_fields},
            "key_record": forged,
            "member_classes": big_cls,
        }
    )
    with pytest.raises(ValueError, match="exceed the actual carried admission cap"):
        _s_entry_leaf_closed(forged_entry)
    assert _CountingMembers.iterations == 0
    _CountingMembers.iterations = 0
    with pytest.raises(ValidationError, match="exceed the actual carried admission cap"):
        RootRegionAdmission(
            state=s0,
            ns=ns,
            r_result=r,
            g_bounds=g,
            root_entry=forged_entry,
            path_associations=parent.path_associations,
            scope_key=parent.scope_key,
            entries_retained=1,
            member_occurrences_charged=1,
            reverse_association_attempts=1,
            emitted_admission_reasons=0,
        )
    assert _CountingMembers.iterations == 0


def test_d1_entry_preparse_proof_context_gates_positive_first() -> None:
    """D1: the BEFORE-parsing proof-context container/count gates
    close for ALL entry variants before admitted element parsing and
    before the canonical C rekey.  Positive FIRST: the genuine FILE
    entry rebuilt through the direct constructor (proof identity
    retained), the legal ROOT empty raw list normalizing to the exact
    empty tuple (the root admits the root, not proof segments), and a
    genuine BaseModel CLASS parser spy with a pass-through
    before-field counter (inherited original laws unchanged: field
    stage 1, canonical 1).  Then negative-only copies, each proving
    the exact fixed private channel with ZERO canonical rekey visits:
    a partial provided proof (deliberate model_construct missing the
    segment population) plus a nonempty raw admitted vector; a raw
    FILE overcount vector under the closed proof; the same overcount
    carried into the shared leaf law (the admission parent re-runs
    this same shared law; the direct leaf is tested here, not a full
    parent construction); ROOT proof=None plus an unknown raw
    admitted iterable (zero next() visits); and a provided proof
    population over the actual B cap 32 with an aligned 33-element
    raw vector (parser field stage 0 -- the provided len never
    widens the raw index domain).  One LEAN/responses component
    fixture; the spy measures stage entry, not per-element native
    parser visits or allocation proof."""
    ns, state, r, g, root_entry, files, parent = _offset_component()
    entry = next(e for e in files if e.key_record.member_occurrences == ("A.md",))
    proof: BundleProof | None = entry.proof
    assert proof is not None
    fields = {name: getattr(entry, name) for name in type(entry).model_fields}
    root_fields = {name: getattr(root_entry, name) for name in type(root_entry).model_fields}
    assert parent.state is state and parent.r_result is r  # positive first (genuine parent)

    hits = 0
    real_canonical = _canonical_entry_key

    def _counting_canonical(record: Any) -> Any:
        nonlocal hits
        hits += 1
        return real_canonical(record)

    monkeypatch = pytest.MonkeyPatch()
    try:
        monkeypatch.setattr(rram, "_canonical_entry_key", _counting_canonical)
        # positive first: the genuine FILE entry re-constructed
        # through the direct constructor under the closed gates
        # (proof identity retained, canonical recipe visited once).
        rebuilt_file = RootRegionAdmissionEntry(**fields)
        assert rebuilt_file.proof is proof
        assert rebuilt_file.admitted_segments == entry.admitted_segments
        assert hits == 1
        # positive first: the legal ROOT empty raw list normalizes
        # to the exact empty tuple (root source retained by identity,
        # canonical recipe visited once).
        hits = 0
        rebuilt_root = RootRegionAdmissionEntry(**{**root_fields, "admitted_segments": []})
        assert rebuilt_root.root_source is root_entry.root_source
        assert rebuilt_root.admitted_segments == ()
        assert hits == 1

        # positive first: a genuine CLASS parser spy with a
        # pass-through before-field counter (inherited original laws
        # unchanged: the admitted-segment field stage is entered
        # exactly once, canonical recipe visited once).
        class _SpyAdmittedEntry(RootRegionAdmissionEntry):
            field_stage: ClassVar[int] = 0

            @field_validator("admitted_segments", mode="before")
            @classmethod
            def _spy_admitted_stage(cls, value: Any) -> Any:
                _SpyAdmittedEntry.field_stage += 1
                return value

        hits = 0
        _SpyAdmittedEntry.field_stage = 0
        spy_file = _SpyAdmittedEntry(**fields)
        assert spy_file.proof is proof
        assert spy_file.admitted_segments == entry.admitted_segments
        assert _SpyAdmittedEntry.field_stage == 1 and hits == 1
        # negative only: a partial provided proof (deliberate
        # model_construct missing the segment population) plus a
        # nonempty raw admitted vector is the closed proof-population
        # error before any canonical rekey.
        hits = 0
        partial = type(proof).model_construct(
            **{
                name: getattr(proof, name)
                for name in type(proof).model_fields
                if name != "segments"
            }
        )
        with pytest.raises(
            ValidationError,
            match="the entry proof must carry its closed segment population before parsing",
        ) as excinfo:
            RootRegionAdmissionEntry(**{**fields, "proof": partial})
        assert len(excinfo.value.errors()) == 1
        assert hits == 0
        # negative only: a raw FILE overcount vector under the closed
        # proof (one element beyond the retained segment domain) is
        # the fixed preparse domain error before any canonical rekey.
        over = (0,) * (len(proof.segments) + 1)
        hits = 0
        with pytest.raises(
            ValidationError,
            match="admitted segments exceed the actual proof segment domain before parsing",
        ) as excinfo:
            RootRegionAdmissionEntry(**{**fields, "admitted_segments": over})
        assert len(excinfo.value.errors()) == 1
        assert hits == 0
        # negative only: the same overcount carried into the shared
        # leaf law (the admission parent re-runs this same shared
        # law; the direct leaf is tested here, not a full parent
        # construction) refuses before any walk and before any
        # canonical rekey.
        copied = entry.model_copy(update={"admitted_segments": over})
        hits = 0
        with pytest.raises(
            ValueError,
            match="admitted segments exceed the actual proof segment domain before any walk",
        ):
            _s_entry_leaf_closed(copied)
        assert hits == 0
        # negative only: ROOT proof=None plus an unknown raw
        # admitted iterable is refused BEFORE any element retrieval
        # (zero next() visits, no canonical rekey) -- the legal ROOT
        # empty list/tuple positive above is untouched.
        raw_iter = _CountingIter((0, 1))
        hits = 0
        with pytest.raises(
            ValidationError,
            match="admitted segments must carry a closed list or tuple before parsing",
        ) as excinfo:
            RootRegionAdmissionEntry(**{**root_fields, "admitted_segments": raw_iter})
        assert len(excinfo.value.errors()) == 1
        assert raw_iter.n == 0
        assert hits == 0
        # negative only: a provided proof population over the actual
        # B cap (the actual 32) plus an aligned 33-element raw vector
        # is refused at the cap BEFORE the parser field stage (the
        # provided len never widens the raw index domain) and before
        # any canonical rekey.
        bound = entry.key_record.proof_bounds.max_segments
        assert bound == 32
        bad_proof = proof.model_copy(update={"segments": proof.segments * (bound + 1)})
        raw = tuple(range(bound + 1))
        hits = 0
        _SpyAdmittedEntry.field_stage = 0
        with pytest.raises(
            ValidationError, match="the retained proof segments exceed the actual carried proof cap"
        ) as excinfo:
            _SpyAdmittedEntry(**{**fields, "proof": bad_proof, "admitted_segments": raw})
        assert len(excinfo.value.errors()) == 1
        assert _SpyAdmittedEntry.field_stage == 0
        assert hits == 0
    finally:
        monkeypatch.undo()


def test_d1_group_index_count_before_walk() -> None:
    """D1: the ownership-group index COUNT closes O(1) BEFORE any
    index walk or seen extension.  Positive FIRST: the genuine
    one-member ROOT record's sole group (one index, matching the
    one member occurrence) is accepted at the private leaf and the
    fresh admission parent.  Negative only: a copied group carrying
    a two-element COUNTING index tuple (under the one-to-one
    partition law it cannot exceed the one member occurrence)
    spliced into a copied record/entry refuses with ONE fixed
    private count error at the private leaf AND the fresh
    admission parent, with ZERO counting-index iterations (the O(1)
    count closes before the first element visit; the original
    partition predicates are unchanged)."""
    ns, s0, r, g, key_record, root_entry, parent = _s_parent(MODES[0], "s-d1-groupcount")
    group = key_record.ownership_groups[0]
    assert len(group.member_occurrence_indices) == 1
    # positive first: the genuine record/entry is accepted at the
    # private leaf law AND the admission parent (the accepted
    # parent over the SAME genuine record).
    _s_entry_leaf_closed(root_entry)
    assert parent.state is s0 and parent.r_result is r
    # negative only: the SAME group with a two-element COUNTING
    # index tuple, spliced into a copied record/entry.
    _CountingMembers.iterations = 0
    bad_group = group.model_copy(update={"member_occurrence_indices": _CountingMembers((0, 1))})
    forged_record = key_record.model_copy(update={"ownership_groups": (bad_group,)})
    forged_entry = root_entry.model_copy(update={"key_record": forged_record})
    with pytest.raises(ValueError, match="cannot exceed the member occurrence count"):
        _s_entry_leaf_closed(forged_entry)
    assert _CountingMembers.iterations == 0
    _CountingMembers.iterations = 0
    with pytest.raises(ValidationError, match="cannot exceed the member occurrence count"):
        RootRegionAdmission(
            state=s0,
            ns=ns,
            r_result=r,
            g_bounds=g,
            root_entry=forged_entry,
            path_associations=parent.path_associations,
            scope_key=parent.scope_key,
            entries_retained=1,
            member_occurrences_charged=1,
            reverse_association_attempts=1,
            emitted_admission_reasons=0,
        )
    assert _CountingMembers.iterations == 0


def test_d1_retained_proof_member_shape_closed_before_content() -> None:
    """D1: the retained requested-member closure is closed BEFORE
    any member dereference or content work at the shared leaf law
    (re-run at the admission parent): the concrete ORIGINAL member
    class, the closed member metadata and the closed normalized
    variant of EVERY retained requested member.  Positive FIRST:
    the genuine standalone-A FILE entry (one resolved member)
    re-constructed through the direct constructor (one content
    pass; the whole-bundle fast path makes no slice copy) and
    the fresh S parent re-constructed from its own fields (one
    content pass per FILE entry with a proof).  Then negative-only coherent
    copies: a plain object, a matching-namespace object, a partial
    actual member with normalized never set and a bool normalized
    value each refuse with ONE fixed private error at the leaf
    AND the fresh admission parent before any source content pass (the
    legitimate originals and the None-unresolved policy stay
    legal)."""
    ns, state, r, g, _root_entry, files, parent = _offset_component()
    entry = next(e for e in files if e.proof is not None)
    proof: BundleProof | None = entry.proof
    assert proof is not None
    assert entry.admitted_segments == (0,)
    assert len(proof.segments) == 1
    assert len(proof.requested_members) == 1
    member = proof.requested_members[0]
    assert member.normalized == "A.md"
    fields = {name: getattr(entry, name) for name in type(entry).model_fields}
    parent_kwargs = {name: getattr(parent, name) for name in type(parent).model_fields}

    # The shared leaf law's ACTUAL content-verification
    # encode/hash site, counted by line (the fixture must keep
    # exactly one such statement).  The whole-bundle fast path
    # makes no slice copy, but the digest predicate encodes and
    # hashes exactly once per FILE leaf invocation.
    lines, first = inspect.getsourcelines(_s_entry_leaf_closed)
    selected = [first + i for i, line in enumerate(lines) if 'region_text.encode("utf-8")' in line]
    assert len(selected) == 1
    content_line = selected[0]
    content_hits = 0

    def _content_trace(frame: Any, event: str, arg: Any) -> Any:
        nonlocal content_hits
        if (
            frame.f_code is _s_entry_leaf_closed.__code__
            and event == "line"
            and frame.f_lineno == content_line
        ):
            content_hits += 1
        return _content_trace

    saved_trace = sys.gettrace()
    try:
        sys.settrace(_content_trace)
        # Positive FIRST: the genuine member-closed entry re-built
        # through the direct constructor (proof identity retained;
        # the whole-bundle fast path reuses the retained aggregate
        # without a slice copy, and the digest predicate encodes
        # and hashes exactly once).
        rebuilt = RootRegionAdmissionEntry(**fields)
        assert rebuilt.proof is proof
        assert rebuilt.admitted_segments == entry.admitted_segments
        assert content_hits == 1
        # Positive FIRST: the fresh S parent re-constructed from
        # its own fields re-runs the leaf law per FILE entry (one
        # content pass per FILE entry with a proof).
        content_hits = 0
        rebuilt_parent = RootRegionAdmission(**parent_kwargs)
        assert rebuilt_parent.state is state and rebuilt_parent.r_result is r
        expected_content = sum(1 for e in parent.entries if e.proof is not None)
        assert content_hits == expected_content
        # Negative only: a PLAIN OBJECT and a matching-namespace
        # object (the same normalized value, the wrong class) each
        # refuse the concrete-member class gate at the leaf AND the
        # admission parent, before any content pass.
        for bad_member in (object(), SimpleNamespace(normalized="A.md")):
            bad_proof = proof.model_copy(update={"requested_members": (bad_member,)})
            content_hits = 0
            with pytest.raises(
                ValidationError,
                match="the retained proof members must be the actual concrete member records",
            ) as excinfo:
                RootRegionAdmissionEntry(**{**fields, "proof": bad_proof})
            assert len(excinfo.value.errors()) == 1
            assert content_hits == 0
            content_hits = 0
            with pytest.raises(
                ValidationError,
                match="the retained proof members must be the actual concrete member records",
            ) as excinfo:
                RootRegionAdmission(
                    **{
                        **parent_kwargs,
                        "entries": (entry.model_copy(update={"proof": bad_proof}),),
                    }
                )
            assert len(excinfo.value.errors()) == 1
            assert content_hits == 0
        # Negative only: a PARTIAL actual member (the closed
        # metadata fence) -- the same real member with normalized
        # never set refuses before any dereference, at the leaf
        # AND the admission parent, before any content pass.
        partial = type(member).model_construct(
            **{key: value for key, value in vars(member).items() if key != "normalized"}
        )
        del partial.__dict__["normalized"]
        assert not hasattr(partial, "normalized")
        bad_proof = proof.model_copy(update={"requested_members": (partial,)})
        content_hits = 0
        with pytest.raises(
            ValidationError,
            match="the retained proof members must carry their closed metadata",
        ) as excinfo:
            RootRegionAdmissionEntry(**{**fields, "proof": bad_proof})
        assert len(excinfo.value.errors()) == 1
        assert content_hits == 0
        content_hits = 0
        with pytest.raises(
            ValidationError,
            match="the retained proof members must carry their closed metadata",
        ) as excinfo:
            RootRegionAdmission(
                **{
                    **parent_kwargs,
                    "entries": (entry.model_copy(update={"proof": bad_proof}),),
                }
            )
        assert len(excinfo.value.errors()) == 1
        assert content_hits == 0
        # Negative only: a real member whose normalized value is a
        # BOOL (the closed normalized-variant gate; bool is never
        # the closed text, and is distinct from the legal None
        # unresolved state), at the leaf AND the admission parent,
        # before any content pass.
        bad_proof = proof.model_copy(
            update={"requested_members": (member.model_copy(update={"normalized": True}),)}
        )
        content_hits = 0
        with pytest.raises(
            ValidationError,
            match="the retained proof member normalized path must carry closed text",
        ) as excinfo:
            RootRegionAdmissionEntry(**{**fields, "proof": bad_proof})
        assert len(excinfo.value.errors()) == 1
        assert content_hits == 0
        content_hits = 0
        with pytest.raises(
            ValidationError,
            match="the retained proof member normalized path must carry closed text",
        ) as excinfo:
            RootRegionAdmission(
                **{
                    **parent_kwargs,
                    "entries": (entry.model_copy(update={"proof": bad_proof}),),
                }
            )
        assert len(excinfo.value.errors()) == 1
        assert content_hits == 0
    finally:
        sys.settrace(saved_trace)


def test_d1_one_occurrence_multiple_witness_plans_genuine_positive() -> None:
    """D1: the ACTUAL history occurrence count and the compatible
    plan-witness count are DIFFERENT resource domains: a genuine
    public sequence under a legitimate STRICTER
    HistoryBounds(max_occurrences=1) (set through the real
    namespace factory BEFORE bootstrap) retains EXACTLY ONE
    original complete A|offgraphB|sameA occurrence, and the
    actual R derivation, actual generic G FILE assembly and the
    fresh S leaf/parent retain ALL distinct same-key witness
    plans for that ONE occurrence and original proof.  Genuine
    positive only, BOTH modes and BOTH read endpoints: LEAN
    admits ONE A entry (distinct width 1) with TWO original
    witnesses, segment tuples (0,) and (2,), and GREEDY admits
    ONE whole (A,B,A) entry (distinct width 2) with ONE witness
    (0,1,2).  Original references/coordinates are preserved
    (original proof identity, the same occurrence); no positive
    copies, no invented witness cap and no new operation."""
    for mode in MODES:
        for endpoint in ENDPOINTS:
            ns, state = r_bootstrap(
                mode,
                f"s-d1-oneocc-{mode.value}-{endpoint}",
                root_body="Read `A.md` before work.",
                history_bounds=HistoryBounds(max_occurrences=1),
            )
            assert ns.history_bounds.max_occurrences == 1
            cmd = "cat A.md && echo 'SEPONE' && cat B.md && echo 'SEPTWO' && cat A.md"
            t = r_issue(state, ns, "repeatA", endpoint, (CAUSAL_ROOT_FACT,), cmd)
            assert t.outcome.value == "accepted", t.diagnostics
            t = r_observe(
                t.state,
                ns,
                (
                    read_request(
                        endpoint,
                        "repeatA",
                        _mixed_body("Same A.\n", "SEPONE", "Unrelated B.\n", "SEPTWO", "Same A.\n"),
                        cmd,
                    ),
                ),
            )
            assert t.outcome.value == "accepted", t.diagnostics
            state = t.state
            assert len(state.d_state.occurrences) == 1
            r, _g, _root, entries, parent, _reasons = _s_component_parent(state, ns)
            occ = state.d_state.occurrences[0]
            assert parent.state is state and parent.r_result is r
            assert len(entries) == 1
            entry = entries[0]
            assert entry.proof is occ.proof
            assert entry.witnesses and all(
                w.occurrence_id == occ.occurrence_id for w in entry.witnesses
            )
            if mode is AdmissionMode.LEAN:
                assert entry.key_record.member_occurrences == ("A.md",)
                assert entry.width == 1
                assert tuple(w.segment_indices for w in entry.witnesses) == ((0,), (2,))
            else:
                assert entry.key_record.member_occurrences == ("A.md", "B.md", "A.md")
                assert entry.width == 2
                assert tuple(w.segment_indices for w in entry.witnesses) == ((0, 1, 2),)


def test_d1_witness_helper_owner_domain_closed_before_walk() -> None:
    """D1: the shared witness-region helper (the actual parent's
    per-(witness, owner) M04 join) closes the ACTUAL owner
    proof/witness concrete classes and fields, then the ORIGINAL
    carried B segment/member population caps O(1) BEFORE the
    index scalar/plan gates; the retained requested-member
    closure (concrete class, closed metadata, closed normalized
    variant and the closed raw/form/quoted/limitation scalars) is
    re-closed under the OWNER proof BEFORE any member dereference
    or region-join work.  Positive FIRST: the direct helper on
    each genuine (witness, owner proof) pair of the LEAN offset
    fixture (TWO real owner proofs at different original offsets)
    completes the region join, and the genuine parent re-built
    through the direct constructor re-runs the helper for EVERY
    (witness, owner) pair.  Then negative-only coherent copies
    refuse with ONE fixed private error before the ACTUAL
    region/segment walk starts (walk counter 0; earlier index-
    gate visits are not claimed): a wrong owner-proof class, a
    wrong witness class, each strict carried B population cap
    first over (at-cap legal), and each retained member closure
    kind for BOTH real owner proofs (helper-direct boundary; the
    ACTUAL-parent carrying negative for this closure is
    permanently covered by
    test_d1_actual_parent_carried_owner_member_scalar_refused_
    before_region_walk, which reaches this helper with a coherent
    deep-copied parent carrying one corrupted copied owner
    member).  The walk counter asserts
    ACTUAL line-trace events: the region-walk line traces once
    per segment iteration plus once per loop exit, so each
    helper call yields (segments + 1) events.  The leaf scalar
    closure is additionally asserted at the shared leaf law
    (leaf AND fresh parent boundary) on the entry's FIRST
    original proof before any source content pass; the legitimate
    originals, the at-cap shapes and the None-unresolved policy
    stay legal."""
    ns, state, r, g, _root_entry, files, parent = _offset_component()
    entry = next(e for e in files if e.proof is not None)
    proof: BundleProof | None = entry.proof
    assert proof is not None
    assert entry.admitted_segments == (0,)
    assert len(proof.segments) == 1
    assert len(proof.requested_members) == 1
    member = proof.requested_members[0]
    assert member.normalized == "A.md"
    parent_kwargs = {name: getattr(parent, name) for name in type(parent).model_fields}
    fields = {name: getattr(entry, name) for name in type(entry).model_fields}
    occurrences = state.d_state.occurrences
    pairs = [
        (w, next(o for o in occurrences if o.occurrence_id == w.occurrence_id))
        for w in entry.witnesses
    ]
    assert len(pairs) == 2
    assert len({id(o.proof) for _w, o in pairs}) == 2
    lone_w, lone_o = next(p for p in pairs if len(p[1].proof.segments) == 1)
    mixed_w, mixed_o = next(p for p in pairs if len(p[1].proof.segments) == 2)
    assert len(mixed_o.proof.requested_members) == 2
    # The helper's ACTUAL region-walk statement and the shared
    # leaf law's ACTUAL content-verification encode/hash site,
    # each counted by line (one such statement per source).
    lines, first = inspect.getsourcelines(rram._s_witness_region_compatible)
    selected = [
        first + i
        for i, line in enumerate(lines)
        if "for position, segment in enumerate(segments):" in line
    ]
    assert len(selected) == 1
    walk_line = selected[0]
    leaf_lines, leaf_first = inspect.getsourcelines(_s_entry_leaf_closed)
    leaf_selected = [
        leaf_first + i for i, line in enumerate(leaf_lines) if 'region_text.encode("utf-8")' in line
    ]
    assert len(leaf_selected) == 1
    leaf_content_line = leaf_selected[0]
    walk_hits = 0
    leaf_content_hits = 0

    def _count_trace(frame: Any, event: str, arg: Any) -> Any:
        nonlocal walk_hits, leaf_content_hits
        if event != "line":
            return _count_trace
        if (
            frame.f_code is rram._s_witness_region_compatible.__code__
            and frame.f_lineno == walk_line
        ):
            walk_hits += 1
        elif frame.f_code is _s_entry_leaf_closed.__code__ and frame.f_lineno == leaf_content_line:
            leaf_content_hits += 1
        return _count_trace

    saved_trace = sys.gettrace()
    try:
        sys.settrace(_count_trace)
        # Positive FIRST: the direct helper on each genuine
        # (witness, owner proof) pair completes the region join.
        # The region-walk line traces once per ACTUAL segment
        # iteration plus once per loop exit: (segments + 1)
        # line events per helper call.
        for w, owner in pairs:
            rram._s_witness_region_compatible(w, owner.proof, entry.key_record, ns.proof_bounds)
        assert walk_hits == sum(len(owner.proof.segments) + 1 for _w, owner in pairs)
        # Positive FIRST: the genuine parent re-built through the
        # direct constructor re-runs the helper for EVERY
        # (witness, owner) pair of its FILE entries.  The walk
        # counter asserts ACTUAL line-trace events: (segments + 1)
        # per helper call.
        walk_hits = 0
        rebuilt_parent = RootRegionAdmission(**parent_kwargs)
        assert rebuilt_parent.state is state and rebuilt_parent.r_result is r
        expected_walk_events = 0
        for e in parent.entries:
            for w in e.witnesses:
                owner = next(o for o in occurrences if o.occurrence_id == w.occurrence_id)
                expected_walk_events += len(owner.proof.segments) + 1
        assert walk_hits == expected_walk_events
        # Negative only: a WRONG owner-proof class (the same real
        # fields, the wrong class) refuses the concrete-class gate
        # before any walk, for BOTH real owner proofs.
        for w, owner in pairs:
            fake_proof = SimpleNamespace(
                segments=owner.proof.segments,
                requested_members=owner.proof.requested_members,
                source_text=owner.proof.source_text,
                source_digest=owner.proof.source_digest,
            )
            walk_hits = 0
            with pytest.raises(
                ValueError,
                match="the owner retained proof must be the actual concrete proof record",
            ):
                rram._s_witness_region_compatible(
                    w,
                    fake_proof,  # type: ignore[arg-type]
                    entry.key_record,
                    ns.proof_bounds,
                )
            assert walk_hits == 0
        # Negative only: a WRONG witness class (the same segment
        # coordinates, the wrong class) refuses the concrete-class
        # gate before any walk, for BOTH real owner proofs.
        for w, owner in pairs:
            fake_w = SimpleNamespace(segment_indices=w.segment_indices)
            walk_hits = 0
            with pytest.raises(
                ValueError,
                match="the file witness must be the actual concrete witness record",
            ):
                rram._s_witness_region_compatible(
                    fake_w,  # type: ignore[arg-type]
                    owner.proof,
                    entry.key_record,
                    ns.proof_bounds,
                )
            assert walk_hits == 0
        # Negative only: the ORIGINAL B population caps under a
        # STRICT legitimate carried bound -- at-cap legal (the
        # one-segment / one-member owner proof stays a positive),
        # then first over refuses O(1) before any walk.
        strict_segments = BundleProofBounds(max_segments=1)
        rram._s_witness_region_compatible(lone_w, lone_o.proof, entry.key_record, strict_segments)
        assert walk_hits == len(lone_o.proof.segments) + 1
        walk_hits = 0
        with pytest.raises(
            ValueError,
            match="the retained proof segments exceed the actual carried proof cap",
        ):
            rram._s_witness_region_compatible(
                mixed_w, mixed_o.proof, entry.key_record, strict_segments
            )
        assert walk_hits == 0
        strict_members = BundleProofBounds(max_members=1)
        rram._s_witness_region_compatible(lone_w, lone_o.proof, entry.key_record, strict_members)
        assert walk_hits == len(lone_o.proof.segments) + 1
        walk_hits = 0
        with pytest.raises(
            ValueError,
            match="the retained proof members exceed the actual carried proof cap",
        ):
            rram._s_witness_region_compatible(
                mixed_w, mixed_o.proof, entry.key_record, strict_members
            )
        assert walk_hits == 0
        # Negative only: the retained requested-member closure
        # under the OWNER proof -- a plain object, a
        # matching-namespace object, a PARTIAL actual member with
        # normalized never set, a bool normalized value and each
        # raw/form/quoted/limitation scalar variant refuse ONE
        # fixed private error before any walk, for BOTH real
        # owner proofs (helper-direct).
        for w, owner in pairs:
            owner_proof = owner.proof
            members = owner_proof.requested_members
            m0 = members[0]
            partial = type(m0).model_construct(
                **{key: value for key, value in vars(m0).items() if key != "normalized"}
            )
            del partial.__dict__["normalized"]
            assert not hasattr(partial, "normalized")
            variants = (
                (
                    object(),
                    "the retained proof members must be the actual concrete member records",
                ),
                (
                    SimpleNamespace(normalized="A.md"),
                    "the retained proof members must be the actual concrete member records",
                ),
                (
                    partial,
                    "the retained proof members must carry their closed metadata",
                ),
                (
                    m0.model_copy(update={"normalized": True}),
                    "the retained proof member normalized path must carry closed text",
                ),
                (
                    m0.model_copy(update={"raw": True}),
                    "the retained proof member raw path must carry closed text",
                ),
                (
                    m0.model_copy(update={"form": "relative"}),
                    "the retained proof member form must be the actual closed enum",
                ),
                (
                    m0.model_copy(update={"quoted": "true"}),
                    "the retained proof member quoted flag must be an actual boolean",
                ),
                (
                    m0.model_copy(update={"limitation": "limitation_x"}),
                    "the retained proof member limitation must be the actual closed enum",
                ),
            )
            for bad_member, pattern in variants:
                walk_hits = 0
                with pytest.raises(ValueError, match=pattern):
                    rram._s_witness_region_compatible(
                        w,
                        owner_proof.model_copy(
                            update={"requested_members": (bad_member,) + members[1:]}
                        ),
                        entry.key_record,
                        ns.proof_bounds,
                    )
                assert walk_hits == 0
        # Positive FIRST (leaf boundary): the genuine
        # scalar-closed member-closed entry re-built through the
        # direct constructor re-passes the leaf closure (one
        # actual content pass; the whole-bundle fast path makes
        # no slice copy).
        leaf_content_hits = 0
        rebuilt = RootRegionAdmissionEntry(**fields)
        assert rebuilt.proof is proof
        assert leaf_content_hits == 1
        # Negative only (leaf AND fresh parent boundary): each
        # scalar variant refuses ONE fixed private error before
        # any source content pass.
        for update, pattern in (
            ({"raw": True}, "the retained proof member raw path must carry closed text"),
            (
                {"form": "relative"},
                "the retained proof member form must be the actual closed enum",
            ),
            (
                {"quoted": "true"},
                "the retained proof member quoted flag must be an actual boolean",
            ),
            (
                {"limitation": "limitation_x"},
                "the retained proof member limitation must be the actual closed enum",
            ),
        ):
            bad_proof = proof.model_copy(
                update={"requested_members": (member.model_copy(update=update),)}
            )
            leaf_content_hits = 0
            with pytest.raises(ValidationError, match=pattern) as excinfo:
                RootRegionAdmissionEntry(**{**fields, "proof": bad_proof})
            assert len(excinfo.value.errors()) == 1
            assert leaf_content_hits == 0
            leaf_content_hits = 0
            with pytest.raises(ValidationError, match=pattern) as excinfo:
                RootRegionAdmission(
                    **{**parent_kwargs, "entries": (entry.model_copy(update={"proof": bad_proof}),)}
                )
            assert len(excinfo.value.errors()) == 1
            assert leaf_content_hits == 0
    finally:
        sys.settrace(saved_trace)


def test_d1_actual_parent_carried_owner_member_scalar_refused_before_region_walk() -> None:
    """D1: the ACTUAL admission-parent carrying boundary reaches the
    shared witness-region helper with a corrupted COPIED owner
    member (the parent-boundary reachability the helper-direct
    closure test deliberately does not claim there): positive
    FIRST -- the genuine public P/R/G fresh S parent re-built
    through the direct constructor from the LEAN offset component
    is accepted (state/R identity preserved) and the helper
    re-runs for EVERY (witness, owner) pair: the original second
    owner's region-walk line traces (segments + 1) events.  Then
    negative-only: a DEEP copy of the parent kwargs preserves the
    internal R.state / P-state / root_source / proof-owner
    reference joins (a coherent model-data copy, never a copied
    positive), and ONLY the second copied owner's first member
    ``quoted`` flag is corrupted (bool -> invalid string; the
    original actual member stays bool, asserted after).  The
    actual fresh parent refuses with ONE exact private quoted-
    flag ValidationError: the FIRST owner's witness join still
    completes its region walk ((segments + 1) events on the
    copied first proof) while the copied BAD owner's
    region/segment walk never starts (zero line-trace events),
    because the retained member scalar closure closes under the
    owner proof before any walk.  Pure model-data carrying-
    boundary negative; no full consumer/auth/runtime claim, no
    copied positive P/R/Q/source, no old public law change."""
    ns, state, r, _g, _root_entry, _files, parent = _offset_component()
    parent_kwargs = {name: getattr(parent, name) for name in type(parent).model_fields}
    occurrences = state.d_state.occurrences
    file_entry = next(e for e in parent.entries if e.proof is not None)
    first_proof = file_entry.proof
    assert first_proof is not None
    owners = [
        next(o for o in occurrences if o.occurrence_id == w.occurrence_id)
        for w in file_entry.witnesses
    ]
    second_owner = next(o for o in owners if o.proof is not first_proof)
    assert len(second_owner.proof.segments) == 2
    lines, first = inspect.getsourcelines(rram._s_witness_region_compatible)
    walk_lines = [
        first + i
        for i, line in enumerate(lines)
        if "for position, segment in enumerate(segments):" in line
    ]
    assert len(walk_lines) == 1
    walk_line = walk_lines[0]
    saved_trace = sys.gettrace()
    try:
        # Positive FIRST, traced on the original second owner
        # proof.
        second_hits = 0

        def _pos_trace(frame: Any, event: str, arg: Any) -> Any:
            nonlocal second_hits
            if (
                event == "line"
                and frame.f_code is rram._s_witness_region_compatible.__code__
                and frame.f_lineno == walk_line
                and frame.f_locals.get("owner_proof") is second_owner.proof
            ):
                second_hits += 1
            return _pos_trace

        sys.settrace(_pos_trace)
        rebuilt_parent = RootRegionAdmission(**parent_kwargs)
        assert rebuilt_parent.state is state and rebuilt_parent.r_result is r
        assert second_hits == len(second_owner.proof.segments) + 1
        # Negative only: the coherent deep copy (internal aliases
        # preserved) with ONLY the second copied owner's first
        # member quoted flag corrupted.
        negative = copy.deepcopy(parent_kwargs)
        neg_entry = next(e for e in negative["entries"] if e.proof is not None)
        neg_first_proof = neg_entry.proof
        neg_bad_owner = next(
            o for o in negative["state"].d_state.occurrences if o.proof is not neg_first_proof
        )
        assert any(o.proof is neg_first_proof for o in negative["state"].d_state.occurrences)
        assert neg_bad_owner.proof is not neg_first_proof
        assert any(w.occurrence_id == neg_bad_owner.occurrence_id for w in neg_entry.witnesses)
        member = neg_bad_owner.proof.requested_members[0]
        original_member = next(
            o for o in occurrences if o.call_id == neg_bad_owner.call_id
        ).proof.requested_members[0]
        assert member is not original_member and type(original_member.quoted) is bool
        member.__dict__["quoted"] = "invalid-private-flag"
        first_hits = 0
        bad_hits = 0

        def _neg_trace(frame: Any, event: str, arg: Any) -> Any:
            nonlocal first_hits, bad_hits
            if (
                event == "line"
                and frame.f_code is rram._s_witness_region_compatible.__code__
                and frame.f_lineno == walk_line
            ):
                owner_proof = frame.f_locals.get("owner_proof")
                if owner_proof is neg_first_proof:
                    first_hits += 1
                elif owner_proof is neg_bad_owner.proof:
                    bad_hits += 1
            return _neg_trace

        sys.settrace(_neg_trace)
        with pytest.raises(
            ValidationError,
            match="the retained proof member quoted flag must be an actual boolean",
        ) as excinfo:
            RootRegionAdmission(**negative)
        assert len(excinfo.value.errors()) == 1
        assert first_hits == len(neg_first_proof.segments) + 1
        assert bad_hits == 0
        assert type(original_member.quoted) is bool
    finally:
        sys.settrace(saved_trace)


def test_d1_witness_helper_inner_segment_closure_before_walk() -> None:
    """D1: the shared witness-region helper closes the retained
    segment population BEFORE the inner member-position walk, for
    EVERY segment (the ORIGINAL B segment record concrete class,
    the closed fields, the closed member-position tuple container
    and its O(1) count under the ACTUAL requested-occurrence
    domain -- the same fixed private channels as the shared leaf
    law): positive FIRST -- the direct helper on each genuine
    (witness, owner proof) pair of the LEAN offset fixture
    completes the region join (the inner-walk line traces
    (member-positions + 1) events per selected segment); then
    negative-only selected segment copies for BOTH real owner
    proofs refuse ONE fixed private error BEFORE the first
    position element is visited (inner-walk line-trace events 0,
    the counting iterator consumed zero times): a wrong segment
    class carrying the same real fields, a LIST member-position
    container, a finite unknown iterable container, and a
    first-over requested-occurrence count.  Helper-direct
    boundary only (the carried parent re-runs the leaf law, which
    carries the same fences); no full consumer/runtime claim, no
    new cap, no old public law change."""
    ns, state, _r, _g, _root_entry, files, _parent = _offset_component()
    entry = next(e for e in files if e.proof is not None)
    record = entry.key_record
    occurrences = state.d_state.occurrences
    pairs = [
        (w, next(o for o in occurrences if o.occurrence_id == w.occurrence_id))
        for w in entry.witnesses
    ]
    assert len(pairs) == 2
    lines, first = inspect.getsourcelines(rram._s_witness_region_compatible)
    inner_lines = [
        first + i
        for i, line in enumerate(lines)
        if "for member_position in segment.member_positions:" in line
    ]
    assert len(inner_lines) == 1
    inner_line = inner_lines[0]
    inner_hits = 0

    def _inner_trace(frame: Any, event: str, arg: Any) -> Any:
        nonlocal inner_hits
        if (
            event == "line"
            and frame.f_code is rram._s_witness_region_compatible.__code__
            and frame.f_lineno == inner_line
        ):
            inner_hits += 1
        return _inner_trace

    saved_trace = sys.gettrace()
    try:
        sys.settrace(_inner_trace)
        # Positive FIRST: both genuine (witness, owner) pairs
        # complete the region join.
        for w, owner in pairs:
            rram._s_witness_region_compatible(w, owner.proof, record, ns.proof_bounds)
        expected = 0
        for w, owner in pairs:
            selected = set(w.segment_indices)
            for pos, seg in enumerate(owner.proof.segments):
                if pos in selected:
                    expected += len(seg.member_positions) + 1
        assert inner_hits == expected
        # Negative only: a WRONG segment class carrying the same
        # real fields refuses the concrete-class gate before any
        # walk, for BOTH real owner proofs.
        for w, owner in pairs:
            owner_proof = owner.proof
            seg0 = owner_proof.segments[0]
            fake_seg = SimpleNamespace(**vars(seg0))
            inner_hits = 0
            with pytest.raises(
                ValueError,
                match="the retained proof segments must be the actual concrete segment records",
            ):
                rram._s_witness_region_compatible(
                    w,
                    owner_proof.model_copy(
                        update={"segments": (fake_seg,) + owner_proof.segments[1:]}
                    ),
                    record,
                    ns.proof_bounds,
                )
            assert inner_hits == 0
        # Negative only: a LIST member-position container refuses
        # the closed-tuple-container gate before any walk.
        for w, owner in pairs:
            owner_proof = owner.proof
            seg0 = owner_proof.segments[0]
            inner_hits = 0
            with pytest.raises(
                ValueError,
                match="the retained segment member positions must carry the closed tuple container",
            ):
                rram._s_witness_region_compatible(
                    w,
                    owner_proof.model_copy(
                        update={
                            "segments": (
                                seg0.model_copy(
                                    update={"member_positions": list(seg0.member_positions)}
                                ),
                            )
                            + owner_proof.segments[1:]
                        }
                    ),
                    record,
                    ns.proof_bounds,
                )
            assert inner_hits == 0
        # Negative only: a finite UNKNOWN iterable container is
        # refused before it is traversed (zero next calls).
        for w, owner in pairs:
            owner_proof = owner.proof
            seg0 = owner_proof.segments[0]
            pos_iter = _CountingIterator(tuple(seg0.member_positions))
            inner_hits = 0
            with pytest.raises(
                ValueError,
                match="the retained segment member positions must carry the closed tuple container",
            ):
                rram._s_witness_region_compatible(
                    w,
                    owner_proof.model_copy(
                        update={
                            "segments": (seg0.model_copy(update={"member_positions": pos_iter}),)
                            + owner_proof.segments[1:]
                        }
                    ),
                    record,
                    ns.proof_bounds,
                )
            assert pos_iter.nexts == 0
            assert inner_hits == 0
        # Negative only: a FIRST-OVER requested-occurrence count
        # refuses the O(1) domain gate before the first element is
        # visited, for BOTH real owner proofs (the legitimate
        # repeated-operand and under-cap shapes stay legal -- the
        # positives above).
        for w, owner in pairs:
            owner_proof = owner.proof
            seg0 = owner_proof.segments[0]
            over = tuple(range(len(owner_proof.requested_members) + 1))
            inner_hits = 0
            with pytest.raises(
                ValueError,
                match="segment member positions exceed the actual requested "
                "occurrence domain before any walk",
            ):
                rram._s_witness_region_compatible(
                    w,
                    owner_proof.model_copy(
                        update={
                            "segments": (seg0.model_copy(update={"member_positions": over}),)
                            + owner_proof.segments[1:]
                        }
                    ),
                    record,
                    ns.proof_bounds,
                )
            assert inner_hits == 0
    finally:
        sys.settrace(saved_trace)


def test_d1_parent_context_and_counts_before_parsing() -> None:
    """D1: the admission-parent BEFORE-PARSING law closes the
    PROVIDED namespace context (actual class, closed fields,
    closed actual admission bounds) and then the O(1) retained-
    entry / reverse-association counts and raw container class
    BEFORE any entry or row element is parsed -- the same
    pre-parser law the entry applies to its key record.  An
    invalid provided context is its OWN fixed private error here,
    never a silent pass-through that lets Pydantic traverse an
    oversized raw vector, and never an attribute error at the cap
    read.  The genuine public P -> actual R -> fresh S parent
    positive (accepted construction, plus a genuine RAW-LIST
    re-construction of its rows) is accepted FIRST; the negative
    copies run only afterwards, each carrying element values that
    would be per-element errors if parsed -- exactly ONE fixed
    private value_error and zero element errors prove the context
    and counts closed before traversal; a counting iterator
    proves zero retrieval for the container class refusal.
    The 128-raw-entry vector (root included) is FIRST OVER the
    actual cap and gives the single preparse count error; the
    at-cap 127-raw-entry vector is count-valid and reaches the
    ACTUAL per-element InstanceOf parsing (127 element errors,
    a negative full-model/parser control, never a ready
    admission); one invalid under-cap entry or row reaches its
    own actual element validation."""
    ns, s0, r, g, _key_record, root_entry, parent = _s_parent(MODES[0], "s-d1-parentctx")
    # positive first: the accepted genuine parent's actual counts
    # sit under the ACTUAL closed caps.
    assert parent.state is s0 and parent.r_result is r
    assert len(parent.entries) + 1 <= ns.bounds.max_entries
    assert len(parent.path_associations) <= ns.bounds.max_reverse_associations
    # genuine RAW-LIST normalization positive: the same genuine
    # rows in a raw list (entries as an empty raw list) are
    # accepted -- list/tuple normalization is preserved.
    rawlist_parent = RootRegionAdmission(
        state=s0,
        ns=ns,
        r_result=r,
        g_bounds=g,
        root_entry=root_entry,
        entries=[],  # type: ignore[arg-type]
        path_associations=list(parent.path_associations),  # type: ignore[arg-type]
        scope_key=parent.scope_key,
        entries_retained=1,
        member_occurrences_charged=1,
        reverse_association_attempts=1,
        emitted_admission_reasons=0,
    )
    assert rawlist_parent.path_associations == parent.path_associations
    # a MISSING provided namespace context is its OWN fixed private
    # context error BEFORE any element parsing (the oversized
    # invalid vector is never traversed: one value_error, zero
    # element errors).
    missing_ns_kwargs: dict[str, object] = {
        "state": s0,
        "r_result": r,
        "g_bounds": g,
        "root_entry": root_entry,
        "entries": [None] * 129,
        "path_associations": parent.path_associations,
        "scope_key": parent.scope_key,
        "entries_retained": 1,
        "member_occurrences_charged": 1,
        "reverse_association_attempts": 1,
        "emitted_admission_reasons": 0,
    }
    with pytest.raises(ValidationError, match="must carry its actual namespace context") as excinfo:
        RootRegionAdmission(**missing_ns_kwargs)  # type: ignore[arg-type]
    errors = excinfo.value.errors()
    assert len(errors) == 1
    assert errors[0]["type"] == "value_error"
    # a WRONG-CLASS provided namespace is the same fixed context
    # error (again with an oversized invalid vector).
    with pytest.raises(ValidationError, match="must carry its actual namespace context") as excinfo:
        RootRegionAdmission(
            state=s0,
            ns="foreign-context",  # type: ignore[arg-type]
            r_result=r,
            g_bounds=g,
            root_entry=root_entry,
            entries=[None] * 129,  # type: ignore[arg-type]
            path_associations=parent.path_associations,
            scope_key=parent.scope_key,
            entries_retained=1,
            member_occurrences_charged=1,
            reverse_association_attempts=1,
            emitted_admission_reasons=0,
        )
    errors = excinfo.value.errors()
    assert len(errors) == 1
    assert errors[0]["type"] == "value_error"
    # a PARTIAL namespace (deliberately missing the bounds field)
    # is the field-existence fence's OWN fixed error, never an
    # attribute error at the cap read (oversized invalid ROWS
    # vector never traversed).
    partial_ns = ns.model_copy()
    del partial_ns.__dict__["bounds"]
    assert not hasattr(partial_ns, "bounds")
    with pytest.raises(ValidationError, match="namespace must carry its closed fields") as excinfo:
        RootRegionAdmission(
            state=s0,
            ns=partial_ns,
            r_result=r,
            g_bounds=g,
            root_entry=root_entry,
            entries=parent.entries,
            path_associations=[None] * 4097,  # type: ignore[arg-type]
            scope_key=parent.scope_key,
            entries_retained=1,
            member_occurrences_charged=1,
            reverse_association_attempts=1,
            emitted_admission_reasons=0,
        )
    errors = excinfo.value.errors()
    assert len(errors) == 1
    assert errors[0]["type"] == "value_error"
    # a MALFORMED provided admission bound (bool scalar) is the
    # closed-bounds fence's OWN fixed error before any cap read
    # (oversized invalid ENTRIES vector never traversed).
    bad_bounds = ns.bounds.model_construct(**{**ns.bounds.model_dump(), "max_entries": True})
    forged_ns = ns.model_copy(update={"bounds": bad_bounds})
    with pytest.raises(
        ValidationError,
        match="the provided inherited admission bounds must be closed under the ",
    ) as excinfo:
        RootRegionAdmission(
            state=s0,
            ns=forged_ns,
            r_result=r,
            g_bounds=g,
            root_entry=root_entry,
            entries=[None] * 129,  # type: ignore[arg-type]
            path_associations=parent.path_associations,
            scope_key=parent.scope_key,
            entries_retained=1,
            member_occurrences_charged=1,
            reverse_association_attempts=1,
            emitted_admission_reasons=0,
        )
    errors = excinfo.value.errors()
    assert len(errors) == 1
    assert errors[0]["type"] == "value_error"
    # entries over-cap: 129 raw FILE entries plus the root entry
    # (130) over the actual cap 128, with element values that
    # would be per-element InstanceOf errors if parsing ran.
    with pytest.raises(
        ValidationError,
        match="the admission entries exceed the actual carried entry cap before parsing",
    ) as excinfo:
        RootRegionAdmission(
            state=s0,
            ns=ns,
            r_result=r,
            g_bounds=g,
            root_entry=root_entry,
            entries=[None] * 129,  # type: ignore[arg-type]
            path_associations=parent.path_associations,
            scope_key=parent.scope_key,
            entries_retained=1,
            member_occurrences_charged=1,
            reverse_association_attempts=1,
            emitted_admission_reasons=0,
        )
    errors = excinfo.value.errors()
    assert len(errors) == 1
    assert errors[0]["type"] == "value_error"
    # rows over-cap: 4097 raw association rows over the actual cap
    # 4096, likewise with would-be per-element errors.
    with pytest.raises(
        ValidationError,
        match="the path associations exceed the actual carried association cap before parsing",
    ) as excinfo:
        RootRegionAdmission(
            state=s0,
            ns=ns,
            r_result=r,
            g_bounds=g,
            root_entry=root_entry,
            entries=parent.entries,
            path_associations=[None] * 4097,  # type: ignore[arg-type]
            scope_key=parent.scope_key,
            entries_retained=1,
            member_occurrences_charged=1,
            reverse_association_attempts=1,
            emitted_admission_reasons=0,
        )
    errors = excinfo.value.errors()
    assert len(errors) == 1
    assert errors[0]["type"] == "value_error"
    # an unsupported raw container class (counting iterator) is
    # refused before ANY element retrieval.
    raw_iter = _CountingIter([None] * 129)
    with pytest.raises(
        ValidationError,
        match="the admission entries must carry a closed list or tuple before parsing",
    ):
        RootRegionAdmission(
            state=s0,
            ns=ns,
            r_result=r,
            g_bounds=g,
            root_entry=root_entry,
            entries=raw_iter,  # type: ignore[arg-type]
            path_associations=parent.path_associations,
            scope_key=parent.scope_key,
            entries_retained=1,
            member_occurrences_charged=1,
            reverse_association_attempts=1,
            emitted_admission_reasons=0,
        )
    assert raw_iter.n == 0
    # the SAME raw container law on the reverse-association rows:
    # a counting iterator is refused before ANY row retrieval.
    raw_row_iter = _CountingIter([None] * 4097)
    with pytest.raises(
        ValidationError,
        match="the path associations must carry a closed list or tuple before parsing",
    ):
        RootRegionAdmission(
            state=s0,
            ns=ns,
            r_result=r,
            g_bounds=g,
            root_entry=root_entry,
            entries=parent.entries,
            path_associations=raw_row_iter,  # type: ignore[arg-type]
            scope_key=parent.scope_key,
            entries_retained=1,
            member_occurrences_charged=1,
            reverse_association_attempts=1,
            emitted_admission_reasons=0,
        )
    assert raw_row_iter.n == 0
    # 128 raw FILE entries plus the mandatory root entry (129) is
    # FIRST OVER the actual cap 128: the single fixed preparse
    # count error, no element parsing (the 129-raw-None stimulus
    # above is the separate oversized control and stays).
    with pytest.raises(
        ValidationError,
        match="the admission entries exceed the actual carried entry cap before parsing",
    ) as excinfo:
        RootRegionAdmission(
            state=s0,
            ns=ns,
            r_result=r,
            g_bounds=g,
            root_entry=root_entry,
            entries=[None] * 128,  # type: ignore[arg-type]
            path_associations=parent.path_associations,
            scope_key=parent.scope_key,
            entries_retained=1,
            member_occurrences_charged=1,
            reverse_association_attempts=1,
            emitted_admission_reasons=0,
        )
    errors = excinfo.value.errors()
    assert len(errors) == 1
    assert errors[0]["type"] == "value_error"
    # AT CAP: 127 raw entries plus the root entry is exactly the
    # actual cap 128, so the count gate is count-valid and the
    # actual per-element InstanceOf parsing runs on every raw
    # element: exactly 127 element errors (a NEGATIVE full-model/
    # parser control, never a ready admission positive).
    with pytest.raises(
        ValidationError,
        match="Input should be an instance of RootRegionAdmissionEntry",
    ) as excinfo:
        RootRegionAdmission(
            state=s0,
            ns=ns,
            r_result=r,
            g_bounds=g,
            root_entry=root_entry,
            entries=[None] * 127,  # type: ignore[arg-type]
            path_associations=parent.path_associations,
            scope_key=parent.scope_key,
            entries_retained=1,
            member_occurrences_charged=1,
            reverse_association_attempts=1,
            emitted_admission_reasons=0,
        )
    errors = excinfo.value.errors()
    assert len(errors) == 127
    assert all(err["type"] == "is_instance_of" for err in errors)
    assert [err["loc"] for err in errors] == [("entries", i) for i in range(127)]
    # ONE invalid UNDER-CAP entry reaches its own actual element
    # validation (the count gate is count-valid at one raw entry).
    with pytest.raises(
        ValidationError,
        match="Input should be an instance of RootRegionAdmissionEntry",
    ) as excinfo:
        RootRegionAdmission(
            state=s0,
            ns=ns,
            r_result=r,
            g_bounds=g,
            root_entry=root_entry,
            entries=[None],  # type: ignore[arg-type]
            path_associations=parent.path_associations,
            scope_key=parent.scope_key,
            entries_retained=1,
            member_occurrences_charged=1,
            reverse_association_attempts=1,
            emitted_admission_reasons=0,
        )
    errors = excinfo.value.errors()
    assert len(errors) == 1
    assert errors[0]["type"] == "is_instance_of"
    assert errors[0]["loc"] == ("entries", 0)
    # ONE invalid UNDER-CAP row likewise reaches its own actual
    # element validation.
    with pytest.raises(
        ValidationError,
        match="Input should be an instance of CurrentAdmissionPathAssociation",
    ) as excinfo:
        RootRegionAdmission(
            state=s0,
            ns=ns,
            r_result=r,
            g_bounds=g,
            root_entry=root_entry,
            entries=parent.entries,
            path_associations=[None],  # type: ignore[arg-type]
            scope_key=parent.scope_key,
            entries_retained=1,
            member_occurrences_charged=1,
            reverse_association_attempts=1,
            emitted_admission_reasons=0,
        )
    errors = excinfo.value.errors()
    assert len(errors) == 1
    assert errors[0]["type"] == "is_instance_of"
    assert errors[0]["loc"] == ("path_associations", 0)


class _CountingFacts(tuple[Any]):
    iterations: int = 0

    def __iter__(self) -> Any:
        _CountingFacts.iterations += 1
        return super().__iter__()


def test_d1_parent_revision_state_and_rootfacts_before_shared_target() -> None:
    """D1: BEFORE the shared R source validator may walk anything,
    the admission parent closes the EXACT input P state identity,
    the closed non-bool P/D/R revisions under the ORIGINAL
    0..MAX_REVISION range, the original 1:1 P==D and R==P revision
    joins, and the P root-fact container/count under the ACTUAL ns
    root-lineage cap.  Positive FIRST: the genuine fresh parent is
    accepted with the real shared target actually reached (one
    hit).  Negative only: a wrong R.state, a bool revision, a
    coherent out-of-range revision set, valid-range unequal
    revisions and an over-cap / non-tuple COUNTING root-facts
    vector each refuse with their fixed private error BEFORE the
    shared target runs (zero hits) and before any root-fact
    iteration.  No new cap, clock, revision advance or
    derivation; the old R public schemas and the shared body are
    unchanged."""
    ns, s0, r, g, _kr, root_entry, parent = _s_parent(MODES[0], "s-d1-revstate")
    base_kwargs: dict[str, Any] = {
        "state": s0,
        "ns": ns,
        "r_result": r,
        "g_bounds": g,
        "root_entry": root_entry,
        "path_associations": parent.path_associations,
        "scope_key": parent.scope_key,
        "entries_retained": parent.entries_retained,
        "member_occurrences_charged": parent.member_occurrences_charged,
        "reverse_association_attempts": parent.reverse_association_attempts,
        "emitted_admission_reasons": parent.emitted_admission_reasons,
    }
    hits = 0
    real_target = _r_result_closed

    def _counting_target(result: RootRegionGraphResult) -> None:
        nonlocal hits
        hits += 1
        real_target(result)

    monkeypatch = pytest.MonkeyPatch()
    try:
        monkeypatch.setattr(rram, "_r_result_closed", _counting_target)
        # positive FIRST: the genuine fresh parent is accepted and
        # the real shared source target is actually reached once.
        rebuilt = RootRegionAdmission(**base_kwargs)
        assert rebuilt.state is s0 and rebuilt.r_result is r
        assert hits == 1
        # a WRONG R.state (a genuine class copy, not the exact
        # input state object) is the EXACT-state identity error
        # before the target.
        hits = 0
        state_copy = s0.model_copy()
        r_wrong_state = r.model_copy(update={"state": state_copy})
        with pytest.raises(
            ValidationError,
            match="the R result must carry the EXACT input P state by reference",
        ):
            RootRegionAdmission(**{**base_kwargs, "r_result": r_wrong_state})
        assert hits == 0
        # a bool R revision is the closed non-bool revision error
        # before the target.
        hits = 0
        r_bool = r.model_copy(update={"revision": True})
        with pytest.raises(
            ValidationError,
            match="the carried P/D/R revisions must carry closed non-bool integers",
        ):
            RootRegionAdmission(**{**base_kwargs, "r_result": r_bool})
        assert hits == 0
        # a bool P revision (R kept at the genuine carried value)
        # is the same closed non-bool revision error before the
        # target.
        hits = 0
        s_pbool = s0.model_copy(update={"revision": True})
        r_pbool = r.model_copy(update={"state": s_pbool, "revision": s0.revision})
        with pytest.raises(
            ValidationError,
            match="the carried P/D/R revisions must carry closed non-bool integers",
        ):
            RootRegionAdmission(**{**base_kwargs, "state": s_pbool, "r_result": r_pbool})
        assert hits == 0
        # a bool D revision (P/R kept genuine and equal) is the
        # same closed non-bool revision error before the target.
        hits = 0
        d_dbool = s0.d_state.model_copy(update={"revision": True})
        s_dbool = s0.model_copy(update={"d_state": d_dbool})
        r_dbool = r.model_copy(update={"state": s_dbool, "revision": s0.revision})
        with pytest.raises(
            ValidationError,
            match="the carried P/D/R revisions must carry closed non-bool integers",
        ):
            RootRegionAdmission(**{**base_kwargs, "state": s_dbool, "r_result": r_dbool})
        assert hits == 0
        # a COHERENT out-of-range P/D/R revision set (all equal,
        # all over the ORIGINAL MAX_REVISION) is the range error
        # before the 1:1 joins and before the target.
        hits = 0
        d_over = s0.d_state.model_copy(update={"revision": MAX_REVISION + 1})
        s_over = s0.model_copy(update={"d_state": d_over, "revision": MAX_REVISION + 1})
        r_over = r.model_copy(update={"state": s_over, "revision": MAX_REVISION + 1})
        with pytest.raises(
            ValidationError,
            match="the carried P/D/R revisions must sit in the original revision range",
        ):
            RootRegionAdmission(**{**base_kwargs, "state": s_over, "r_result": r_over})
        assert hits == 0
        # valid-range unequal P versus D revisions are the original
        # 1:1 P==D join error before the target.
        hits = 0
        d_unequal = s0.d_state.model_copy(update={"revision": 5})
        s_unequal = s0.model_copy(update={"d_state": d_unequal})
        r_pd = r.model_copy(update={"state": s_unequal, "revision": s0.revision})
        with pytest.raises(
            ValidationError,
            match="the P state revision must equal the wrapped D revision",
        ):
            RootRegionAdmission(**{**base_kwargs, "state": s_unequal, "r_result": r_pd})
        assert hits == 0
        # valid-range unequal R versus P revisions are the original
        # 1:1 R==P join error before the target.
        hits = 0
        r_rp = r.model_copy(update={"revision": s0.revision + 1})
        with pytest.raises(
            ValidationError,
            match="the carried R revision must equal the P state revision",
        ):
            RootRegionAdmission(**{**base_kwargs, "r_result": r_rp})
        assert hits == 0
        # an OVER-CAP COUNTING root-facts vector (coherent genuine
        # state refs, over the ACTUAL ns root-lineage cap) is the
        # count error before any root-fact iteration and before
        # the target.
        hits = 0
        _CountingFacts.iterations = 0
        anchor_fact = s0.root_facts[0]
        cap = ns.root_lineage_bounds.max_root_facts
        big_facts = _CountingFacts((anchor_fact,) * (cap + 1))
        s_big = s0.model_copy(update={"root_facts": big_facts})
        r_big = r.model_copy(update={"state": s_big})
        with pytest.raises(
            ValidationError,
            match="the carried P root facts exceed the actual root-lineage cap before any walk",
        ):
            RootRegionAdmission(**{**base_kwargs, "state": s_big, "r_result": r_big})
        assert hits == 0
        assert _CountingFacts.iterations == 0
        # a NON-TUPLE root-facts container is the container-class
        # error before any iteration and before the target.
        hits = 0
        s_list = s0.model_copy(update={"root_facts": list(s0.root_facts)})
        r_list = r.model_copy(update={"state": s_list})
        with pytest.raises(
            ValidationError,
            match="the carried P root facts must carry the closed tuple container",
        ):
            RootRegionAdmission(**{**base_kwargs, "state": s_list, "r_result": r_list})
        assert hits == 0
    finally:
        monkeypatch.undo()


def test_d1_parent_carried_ns_scalar_enum_key_version_closure_before_shared_target() -> None:
    """D1: BEFORE the shared R law may hash the scope or walk the
    source, the admission parent closes the carried P namespace's
    ACTUAL scalar / enum / key / version fields: the actual
    AdmissionMode class, the original C/D identity-text limits with
    UTF-8 encodability (the length gate FIRST, so an overlong
    unencodable string is the length error, never an encode error),
    the 64-hex configuration fingerprint, the carried opaque 64-hex
    keys, the canonical workspace under the ACTUAL configured path
    bound (the original 1..1024 character preflight and the
    character-count lower bound before the helper), the region
    lineage-id shape and the NINE supported version identities
    (the actual _region_version_pairs reference).  A format-legal
    FOREIGN config fingerprint passes the shape gates, reaches the
    ACTUAL shared target exactly once and is the actual phase-3
    D-scope re-derivation's private refusal (the keys recompute
    from the actual fields; format is never scope authority); a
    format-legal distinct canonical absolute FOREIGN workspace is
    refused earlier, by the nested carried-context workspace
    joins BEFORE the shared target (the envelope fact workspace
    join fires first, before the F-graph/E-overlay joins),
    because the carried envelope fact and F/E context still bind
    the original namespace workspace.
    Positive FIRST: the genuine fresh parent is accepted with the
    real shared target actually reached (one hit).  Negative only:
    each raw-string mode, overlong / lone-surrogate text,
    malformed-hex config / key, over-character-bound or
    non-canonical workspace, spaced lineage-id and unsupported /
    non-string version carries its fixed private error BEFORE the
    shared target runs (zero hits).  No old public P schema or
    accepted C/D recipe change."""
    ns, s0, r, g, _kr, root_entry, parent = _s_parent(MODES[0], "s-d1-nscl")
    base_kwargs: dict[str, Any] = {
        "state": s0,
        "ns": ns,
        "r_result": r,
        "g_bounds": g,
        "root_entry": root_entry,
        "path_associations": parent.path_associations,
        "scope_key": parent.scope_key,
        "entries_retained": parent.entries_retained,
        "member_occurrences_charged": parent.member_occurrences_charged,
        "reverse_association_attempts": parent.reverse_association_attempts,
        "emitted_admission_reasons": parent.emitted_admission_reasons,
    }
    hits = 0
    real_target = _r_result_closed
    ws_hits = 0
    real_ws = validate_workspace

    def _counting_target(result: RootRegionGraphResult) -> None:
        nonlocal hits
        hits += 1
        real_target(result)

    def _counting_ws(label: str, max_bytes: int) -> str | None:
        nonlocal ws_hits
        ws_hits += 1
        return real_ws(label, max_bytes)

    monkeypatch = pytest.MonkeyPatch()
    try:
        monkeypatch.setattr(rram, "_r_result_closed", _counting_target)
        monkeypatch.setattr(rram, "validate_workspace", _counting_ws)
        # positive FIRST: the genuine fresh parent is accepted and
        # the real shared target is actually reached once.
        rebuilt = RootRegionAdmission(**base_kwargs)
        assert rebuilt.state is s0 and rebuilt.r_result is r
        assert rebuilt.ns is ns
        assert rebuilt.ns.mode is MODES[0]
        assert rebuilt.ns.config_fingerprint == ns.config_fingerprint
        assert rebuilt.ns.workspace == ns.workspace
        assert hits == 1
        # The carried ns workspace check is the FIRST
        # validate_workspace call; the parent's re-run leaf law
        # then closes EACH carried key record workspace under the
        # actual graph path bound (the D2 closed-record
        # workspace gate in the shared preflight) -- the leaf
        # law's direct preflight plus the closed record fence's
        # identical re-closure, so TWO calls per entry (the root
        # entry plus each file entry) -- all BEFORE the shared
        # target.
        assert ws_hits == 1 + 2 * (1 + len(parent.entries))
        # a RAW-STRING carried mode (the enum value, not the actual
        # class) is the closed mode-class error before the target.
        hits = 0
        ns_mode = ns.model_copy(update={"mode": "lean"})
        with pytest.raises(
            ValidationError,
            match="the carried namespace mode must be the actual admission mode",
        ):
            RootRegionAdmission(**{**base_kwargs, "ns": ns_mode})
        assert hits == 0
        # an OVERLONG lone-surrogate carried identity is the
        # ORIGINAL length error BEFORE any UTF-8 encode (the
        # ordering control: the length gate precedes the
        # encodability check, so an unencodable overlong string is
        # the length error, never the encode error).
        hits = 0
        ns_over = ns.model_copy(update={"principal": "a" * 256 + "\ud800"})
        with pytest.raises(
            ValidationError,
            match="the carried namespace principal must be 1..256 characters",
        ):
            RootRegionAdmission(**{**base_kwargs, "ns": ns_over})
        assert hits == 0
        # an UNDER-CAP lone-surrogate carried identity is the UTF-8
        # encodability error before the target.
        hits = 0
        ns_surr = ns.model_copy(update={"model_identity": "a\ud800b"})
        with pytest.raises(
            ValidationError,
            match="the carried namespace model_identity must be valid UTF-8",
        ):
            RootRegionAdmission(**{**base_kwargs, "ns": ns_surr})
        assert hits == 0
        # a MALFORMED-HEX carried config fingerprint is the 64-hex
        # error before the target.
        hits = 0
        ns_cfg = ns.model_copy(update={"config_fingerprint": "0" * 63 + "z"})
        with pytest.raises(
            ValidationError,
            match="the carried namespace config fingerprint must be a 64-hex digest",
        ):
            RootRegionAdmission(**{**base_kwargs, "ns": ns_cfg})
        assert hits == 0
        # a MALFORMED-HEX carried opaque key is the 64-hex error
        # before the target.
        hits = 0
        ns_key = ns.model_copy(update={"state_scoped_key": "x" * 63 + "z"})
        with pytest.raises(
            ValidationError,
            match="the carried namespace state_scoped_key must be a 64-hex digest",
        ):
            RootRegionAdmission(**{**base_kwargs, "ns": ns_key})
        assert hits == 0
        # an OVERLONG workspace (1025 characters) is the original
        # 1..1024 character preflight error BEFORE the canonical
        # helper may iterate/encode (the preflight ordering
        # control).
        hits = 0
        ws_hits = 0
        ns_longws = ns.model_copy(update={"workspace": "/" + "a" * 1024})
        with pytest.raises(
            ValidationError,
            match="the carried namespace workspace must be 1..1024 characters",
        ):
            RootRegionAdmission(**{**base_kwargs, "ns": ns_longws})
        assert hits == 0
        assert ws_hits == 0
        # a RELATIVE (non-canonical) workspace is the canonical-
        # form error before the target.
        hits = 0
        ws_hits = 0
        ns_relws = ns.model_copy(update={"workspace": "work"})
        with pytest.raises(
            ValidationError,
            match="the carried namespace workspace must be the canonical absolute POSIX",
        ):
            RootRegionAdmission(**{**base_kwargs, "ns": ns_relws})
        assert hits == 0
        assert ws_hits == 1
        # a workspace over the ACTUAL configured path bound by
        # character count (a lower bound on the UTF-8 byte length)
        # is the path-bound error before the helper call.
        hits = 0
        ws_hits = 0
        ns_strict_ws = ns.model_copy(
            update={
                "workspace": "/" + "b" * 16,
                "graph_bounds": GraphBounds(max_path_bytes=8),
            }
        )
        with pytest.raises(
            ValidationError,
            match="the carried namespace workspace must be the canonical absolute POSIX",
        ):
            RootRegionAdmission(**{**base_kwargs, "ns": ns_strict_ws})
        assert hits == 0
        assert ws_hits == 0
        # a SPACED lineage id is the original 1..128 non-space error
        # before the target.
        hits = 0
        ns_lid = ns.model_copy(update={"lineage_id": "a b"})
        with pytest.raises(
            ValidationError,
            match="the carried namespace lineage id must be 1..128 non-space characters",
        ):
            RootRegionAdmission(**{**base_kwargs, "ns": ns_lid})
        assert hits == 0
        # an UNSUPPORTED version identity is the supported-identity
        # error before the target.
        hits = 0
        ns_v2 = ns.model_copy(update={"history_version": "cache-causal-history/v2"})
        with pytest.raises(
            ValidationError,
            match="the carried namespace must carry the actual supported version identities",
        ):
            RootRegionAdmission(**{**base_kwargs, "ns": ns_v2})
        assert hits == 0
        # a NON-STRING version (the first of the nine supported
        # version identities, so the R/ns graph-version join stays
        # coherent) is the closed-string error before the target.
        hits = 0
        ns_none_v = ns.model_copy(update={"history_version": None})
        with pytest.raises(
            ValidationError,
            match="the carried namespace versions must carry closed strings",
        ):
            RootRegionAdmission(**{**base_kwargs, "ns": ns_none_v})
        assert hits == 0
        # a DISTINCT well-formed 64-hex FOREIGN config fingerprint
        # passes the shape gates, reaches the ACTUAL shared target
        # once and is the ACTUAL phase-3 D-scope re-derivation's
        # refusal (format is never scope authority).
        hits = 0
        foreign_cfg = hashlib.sha256(b"s-d1-nscl-foreign-config").hexdigest()
        assert foreign_cfg != ns.config_fingerprint
        ns_foreign_cfg = ns.model_copy(update={"config_fingerprint": foreign_cfg})
        with pytest.raises(
            ValidationError,
            match="the carried namespace must re-derive through the actual D validators",
        ):
            RootRegionAdmission(**{**base_kwargs, "ns": ns_foreign_cfg})
        assert hits == 1
        # a DISTINCT format-legal canonical absolute FOREIGN
        # workspace passes the ns shape gates (the canonical
        # helper is actually reached once) but is now refused
        # EARLIER than the phase-3 D-scope re-derivation: the
        # carried ENVELOPE FACT still binds the ORIGINAL
        # namespace workspace, so the nested envelope-fact
        # workspace join refuses its fixed private error BEFORE
        # the shared target (and before the F-graph/E-overlay
        # joins) -- zero hits.
        hits = 0
        ws_hits = 0
        ns_foreign_ws = ns.model_copy(update={"workspace": "/foreign-work"})
        with pytest.raises(
            ValidationError,
            match="the envelope fact workspace must equal the actual namespace workspace",
        ):
            RootRegionAdmission(**{**base_kwargs, "ns": ns_foreign_ws})
        assert hits == 0
        assert ws_hits == 1
    finally:
        monkeypatch.undo()


def test_d1_parent_d_state_class_and_populations_before_shared_target() -> None:
    """D1: BEFORE the shared R source validator may walk anything,
    the admission parent closes the ACTUAL wrapped D state class
    and the four D population containers/counts under the ACTUAL
    provided ns.history_bounds domains (issuances over
    max_issuances, occurrences over max_occurrences, results over
    max_observed_results, parent_links over max_causal_links).
    Positive FIRST: the genuine fresh parent is accepted with the
    real shared target actually reached (one hit), at BOTH default
    and genuinely STRICT provided caps (all four population caps 1
    through the public P factory, distinguishing provided caps from
    hard defaults).  Negative only: the class-before-fields
    precedence (a wrong D object with NO D fields and a full-field
    foreign class both get the new class error before the field
    gate and the target; a copied ACTUAL D missing history_key
    still gets the existing missing-D-fields error, target zero),
    each over-cap COUNTING population (two elements under the
    strict caps) and each wrong-container population refuse with
    their fixed private error BEFORE the shared target runs (zero
    hits) and before any population iteration.  P root_facts stays
    the separate already-closed root-lineage domain; no full D
    revalidation, no new cap or derivation; the old R public law
    is unchanged."""
    ns, s0, r, g, _kr, root_entry, parent = _s_parent(MODES[0], "s-d1-dstate")
    base_kwargs: dict[str, Any] = {
        "state": s0,
        "ns": ns,
        "r_result": r,
        "g_bounds": g,
        "root_entry": root_entry,
        "path_associations": parent.path_associations,
        "scope_key": parent.scope_key,
        "entries_retained": parent.entries_retained,
        "member_occurrences_charged": parent.member_occurrences_charged,
        "reverse_association_attempts": parent.reverse_association_attempts,
        "emitted_admission_reasons": parent.emitted_admission_reasons,
    }
    hits = 0
    real_target = _r_result_closed

    def _counting_target(result: RootRegionGraphResult) -> None:
        nonlocal hits
        hits += 1
        real_target(result)

    monkeypatch = pytest.MonkeyPatch()
    try:
        monkeypatch.setattr(rram, "_r_result_closed", _counting_target)
        # positive FIRST: the genuine fresh parent is accepted and
        # the real shared source target is actually reached once.
        rebuilt = RootRegionAdmission(**base_kwargs)
        assert rebuilt.state is s0 and rebuilt.r_result is r
        assert hits == 1
        d0 = s0.d_state
        # class-before-fields precedence: a WRONG D object with NO
        # D fields at all gets the new class error BEFORE the D
        # field-existence gate (no attribute error, no field-gate
        # message) and before the target.
        hits = 0
        s_bare = s0.model_copy(update={"d_state": SimpleNamespace()})
        r_bare = r.model_copy(update={"state": s_bare})
        with pytest.raises(
            ValidationError,
            match="the wrapped D state must be the actual causal-history state",
        ):
            RootRegionAdmission(**{**base_kwargs, "state": s_bare, "r_result": r_bare})
        assert hits == 0
        # a copied ACTUAL D with history_key deliberately removed
        # from its __dict__ passes the class gate and still gets
        # the EXISTING missing-D-fields error, also target zero.
        hits = 0
        d_partial = d0.model_copy()
        del d_partial.__dict__["history_key"]
        assert not hasattr(d_partial, "history_key")
        s_partial = s0.model_copy(update={"d_state": d_partial})
        r_partial = r.model_copy(update={"state": s_partial})
        with pytest.raises(
            ValidationError,
            match="the admission parent D state must carry its closed fields",
        ):
            RootRegionAdmission(**{**base_kwargs, "state": s_partial, "r_result": r_partial})
        assert hits == 0
        # a WRONG D class (a foreign object carrying all the D
        # fields and the matching revision, bound to a copied P
        # and the exact r.state/input state) is the class error
        # before the target.
        hits = 0
        foreign_d = SimpleNamespace(
            history_key=d0.history_key,
            revision=d0.revision,
            root=d0.root,
            issuances=d0.issuances,
            occurrences=d0.occurrences,
            results=d0.results,
            parent_links=d0.parent_links,
        )
        s_foreign = s0.model_copy(update={"d_state": foreign_d})
        r_foreign = r.model_copy(update={"state": s_foreign})
        with pytest.raises(
            ValidationError,
            match="the wrapped D state must be the actual causal-history state",
        ):
            RootRegionAdmission(**{**base_kwargs, "state": s_foreign, "r_result": r_foreign})
        assert hits == 0
        # positive FIRST under the ACTUAL provided STRICT caps
        # (all four population caps 1 through the public P
        # factory, distinguishing provided caps from hard
        # defaults): the genuine fresh parent is accepted with
        # the real shared target actually reached once.
        strict_bounds = HistoryBounds(
            max_issuances=1,
            max_occurrences=1,
            max_observed_results=1,
            max_causal_links=1,
        )
        ns1, s01, r1, g1, _kr1, root_entry1, parent1 = _s_parent(
            MODES[0], "s-d1-dstate-strict", history_bounds=strict_bounds
        )
        base_kwargs1: dict[str, Any] = {
            "state": s01,
            "ns": ns1,
            "r_result": r1,
            "g_bounds": g1,
            "root_entry": root_entry1,
            "path_associations": parent1.path_associations,
            "scope_key": parent1.scope_key,
            "entries_retained": parent1.entries_retained,
            "member_occurrences_charged": parent1.member_occurrences_charged,
            "reverse_association_attempts": parent1.reverse_association_attempts,
            "emitted_admission_reasons": parent1.emitted_admission_reasons,
        }
        hits = 0
        rebuilt1 = RootRegionAdmission(**base_kwargs1)
        assert rebuilt1.state is s01 and rebuilt1.r_result is r1
        assert hits == 1
        caps = {
            "issuances": ns1.history_bounds.max_issuances,
            "occurrences": ns1.history_bounds.max_occurrences,
            "results": ns1.history_bounds.max_observed_results,
            "parent_links": ns1.history_bounds.max_causal_links,
        }
        assert caps == {
            "issuances": 1,
            "occurrences": 1,
            "results": 1,
            "parent_links": 1,
        }
        d01 = s01.d_state
        sentinel = object()
        # each OVER-CAP COUNTING population (coherent genuine
        # state refs, the two-element cap+1 vector under the
        # ACTUAL provided strict cap) is the count error before
        # any iteration and before the target.
        for field, cap in caps.items():
            hits = 0
            _CountingFacts.iterations = 0
            big = _CountingFacts((sentinel,) * (cap + 1))
            d_big = d01.model_copy(update={field: big})
            s_big = s01.model_copy(update={"d_state": d_big})
            r_big = r1.model_copy(update={"state": s_big})
            with pytest.raises(
                ValidationError,
                match=f"the wrapped D {field} exceed the actual history cap before any walk",
            ):
                RootRegionAdmission(**{**base_kwargs1, "state": s_big, "r_result": r_big})
            assert hits == 0
            assert _CountingFacts.iterations == 0
        # each WRONG-CONTAINER population (a list, not the closed
        # tuple) is the container-class error before any iteration
        # and before the target.
        for field in caps:
            hits = 0
            d_list = d01.model_copy(update={field: list(getattr(d01, field))})
            s_list = s01.model_copy(update={"d_state": d_list})
            r_list = r1.model_copy(update={"state": s_list})
            with pytest.raises(
                ValidationError,
                match=f"the wrapped D {field} must carry the closed tuple container",
            ):
                RootRegionAdmission(**{**base_kwargs1, "state": s_list, "r_result": r_list})
            assert hits == 0
    finally:
        monkeypatch.undo()


def test_d1_parent_carried_key_and_version_headers_before_shared_target() -> None:
    """D1: BEFORE the shared R law may walk the carried headers,
    the admission parent closes the carried P lineage key,
    wrapped D history key, carried R lineage key and carried R
    scope key as closed 64-hex shape (str guard FIRST, so a
    bad-SHAPE key with coherent exact state refs is refused
    before any equality join can mask the type fence; the P
    case sets the carried R key to the same bad shape), the
    carried R graph version under the existing closed shape
    fence (wrong type and lone surrogate included) with the
    join to the ACTUAL namespace graph version, and the READY
    R result's OWN diagnostics EMPTY after the existing
    container/count cap gates.  A DISTINCT well-formed 64-hex
    wrong-scope R scope key passes the format gates and reaches
    the ACTUAL shared target once, whose real scope
    recomputation then rejects privately; format is never scope
    authority.  Positive FIRST: the genuine fresh parent
    is accepted with the real shared target actually reached
    (one hit).  Negative only: each bad-shape / malformed-hex /
    over-shape / wrong-join / non-empty-own-diagnostic carried
    header refuses with its fixed private error BEFORE the
    shared target runs (zero hits); the over-cap diagnostics
    tuple keeps the EXISTING cap-error precedence before the
    new empty check.  No old R public schema or recipe change."""
    ns, s0, r, g, _kr, root_entry, parent = _s_parent(MODES[0], "s-d1-keyhdr")
    base_kwargs: dict[str, Any] = {
        "state": s0,
        "ns": ns,
        "r_result": r,
        "g_bounds": g,
        "root_entry": root_entry,
        "path_associations": parent.path_associations,
        "scope_key": parent.scope_key,
        "entries_retained": parent.entries_retained,
        "member_occurrences_charged": parent.member_occurrences_charged,
        "reverse_association_attempts": parent.reverse_association_attempts,
        "emitted_admission_reasons": parent.emitted_admission_reasons,
    }
    hits = 0
    real_target = _r_result_closed

    def _counting_target(result: RootRegionGraphResult) -> None:
        nonlocal hits
        hits += 1
        real_target(result)

    monkeypatch = pytest.MonkeyPatch()
    try:
        monkeypatch.setattr(rram, "_r_result_closed", _counting_target)
        # positive FIRST: the genuine fresh parent is accepted
        # and the real shared source target is actually reached
        # once.
        rebuilt = RootRegionAdmission(**base_kwargs)
        assert rebuilt.state is s0 and rebuilt.r_result is r
        assert rebuilt.r_result.graph_version == ns.graph_version
        assert rebuilt.r_result.diagnostics == ()
        assert hits == 1
        # a BAD-SHAPE carried P lineage key (None, coherent exact
        # state refs) is the closed-string error before the
        # target.
        hits = 0
        s_none = s0.model_copy(update={"lineage_key": None})
        # the carried R key is set to the SAME bad shape so the
        # P type fence cannot be masked by an unequal-key
        # rejection.
        r_none = r.model_copy(update={"state": s_none, "lineage_key": None})
        with pytest.raises(
            ValidationError,
            match="the carried P lineage key must carry a closed string",
        ):
            RootRegionAdmission(**{**base_kwargs, "state": s_none, "r_result": r_none})
        assert hits == 0
        # a BAD-SHAPE wrapped D history key (an int, coherent
        # exact state refs) is the closed-string error before the
        # target.
        hits = 0
        d_int = s0.d_state.model_copy(update={"history_key": 0})
        s_int = s0.model_copy(update={"d_state": d_int})
        r_int = r.model_copy(update={"state": s_int})
        with pytest.raises(
            ValidationError,
            match="the wrapped D history key must carry a closed string",
        ):
            RootRegionAdmission(**{**base_kwargs, "state": s_int, "r_result": r_int})
        assert hits == 0
        # a MALFORMED-HEX carried R lineage key (well-formed
        # string, wrong hex shape) is the 64-hex error before the
        # target.
        hits = 0
        r_z = r.model_copy(update={"lineage_key": "z" * 64})
        with pytest.raises(
            ValidationError,
            match="the carried R lineage key must be a 64-hex digest",
        ):
            RootRegionAdmission(**{**base_kwargs, "r_result": r_z})
        assert hits == 0
        # a MALFORMED-HEX carried R scope key is the 64-hex error
        # before the target.
        hits = 0
        r_x = r.model_copy(update={"scope_key": "x" * 63 + "z"})
        with pytest.raises(
            ValidationError,
            match="the carried R scope key must be a 64-hex digest",
        ):
            RootRegionAdmission(**{**base_kwargs, "r_result": r_x})
        assert hits == 0
        # a DISTINCT well-formed 64-hex carried R scope key
        # (format valid, scope wrong) passes the format gates and
        # reaches the ACTUAL shared target once; the target's
        # REAL scope recomputation then rejects privately
        # (format is never scope authority).
        hits = 0
        wrong_scope_key = hashlib.sha256(b"s-d1-keyhdr-wrong-scope").hexdigest()
        assert wrong_scope_key != r.scope_key
        r_ws = r.model_copy(update={"scope_key": wrong_scope_key})
        with pytest.raises(
            ValidationError,
            match="scope_key does not match the actual result scope fields",
        ):
            RootRegionAdmission(**{**base_kwargs, "r_result": r_ws})
        assert hits == 1
        # an OVER-SHAPE carried R graph version (129 characters)
        # is the closed version-shape error before the target.
        hits = 0
        r_long = r.model_copy(update={"graph_version": "a" * 129})
        with pytest.raises(
            ValidationError,
            match="the carried R graph version must be 1..128 non-space UTF-8 encodable characters",
        ):
            RootRegionAdmission(**{**base_kwargs, "r_result": r_long})
        assert hits == 0
        # a WRONG-TYPE carried R graph version and a LONE-
        # SURROGATE (unencodable) version are the same closed
        # version-shape error before the target.
        for bad_version in (129, "a\ud800b"):
            hits = 0
            r_bad_gv = r.model_copy(update={"graph_version": bad_version})
            with pytest.raises(
                ValidationError,
                match="the carried R graph version must be 1..128 non-space UTF-8 "
                "encodable characters",
            ):
                RootRegionAdmission(**{**base_kwargs, "r_result": r_bad_gv})
            assert hits == 0
        # a WELL-FORMED but DIFFERENT carried R graph version is
        # the actual-namespace join error before the target
        # (format is never scope authority).
        hits = 0
        alt_version = "cache-graph/v2"
        assert alt_version != ns.graph_version
        r_alt = r.model_copy(update={"graph_version": alt_version})
        with pytest.raises(
            ValidationError,
            match="the carried R graph version must equal the actual namespace graph version",
        ):
            RootRegionAdmission(**{**base_kwargs, "r_result": r_alt})
        assert hits == 0
        # an UNDER-CAP NON-EMPTY READY own-diagnostic tuple is
        # the empty-own-diagnostics error before the target.
        hits = 0
        r_diag = r.model_copy(
            update={"diagnostics": (RootRegionGraphDiagnostic.WORK_UNITS_OVER_BOUND,)}
        )
        with pytest.raises(
            ValidationError,
            match="a ready R result carries no own diagnostics",
        ):
            RootRegionAdmission(**{**base_kwargs, "r_result": r_diag})
        assert hits == 0
        # an OVER-CAP own-diagnostic tuple keeps the EXISTING cap
        # error precedence BEFORE the new empty check (the cap
        # gate runs first).
        hits = 0
        r_over = r.model_copy(
            update={"diagnostics": (RootRegionGraphDiagnostic.WORK_UNITS_OVER_BOUND,) * 65}
        )
        with pytest.raises(
            ValidationError,
            match="the carried R diagnostics exceed the actual R cap before any walk",
        ):
            RootRegionAdmission(**{**base_kwargs, "r_result": r_over})
        assert hits == 0
    finally:
        monkeypatch.undo()


def test_d1_parent_own_sg_version_tag_closure_before_shared_target() -> None:
    """D1: at the carrying parent boundary the FOUR S/G OWN version
    tags close under the phase-0 field-existence fence and the
    ACTUAL fixed supported identities BEFORE the shared R target,
    the scope hash or any source work: at model_validate of an
    existing instance the field validators do not rerun, so a
    coherently recomputed scope key must never re-support a changed
    tag.  Positive FIRST: the genuine public P/R -> fresh S parent
    accepts both by direct construction and through the existing-
    instance carrying boundary, the real shared target actually
    reached each time.  Negative only: each OWN tag copied with an
    unsupported value and a COHERENTLY recomputed scope key refuses
    its fixed private channel before the target (zero hits), and an
    explicitly deleted tag field is the fixed closed-field
    existence error.  No old public schema, cap or revalidation
    change."""
    ns, s0, r, g, _kr, root_entry, parent = _s_parent(MODES[0], "s-d1-sgtags")
    hits = 0
    real_target = _r_result_closed

    def _counting_target(result: RootRegionGraphResult) -> None:
        nonlocal hits
        hits += 1
        real_target(result)

    def _coherent_scope(forged: Any) -> str:
        return root_region_admission_model_scope_key(
            s0.lineage_key,
            forged.model_contract_version,
            forged.model_policy_version,
            r.scope_key,
            forged.g_contract_version,
            forged.g_policy_version,
            g,
        )

    monkeypatch = pytest.MonkeyPatch()
    try:
        monkeypatch.setattr(rram, "_r_result_closed", _counting_target)
        # Positive FIRST: the genuine fresh parent accepts directly
        # AND through the existing-instance carrying boundary, each
        # with the real shared target actually reached once.
        rebuilt = RootRegionAdmission(
            state=s0,
            ns=ns,
            r_result=r,
            g_bounds=g,
            root_entry=root_entry,
            path_associations=parent.path_associations,
            scope_key=parent.scope_key,
            entries_retained=parent.entries_retained,
            member_occurrences_charged=parent.member_occurrences_charged,
            reverse_association_attempts=parent.reverse_association_attempts,
            emitted_admission_reasons=parent.emitted_admission_reasons,
        )
        assert rebuilt.state is s0 and rebuilt.r_result is r and rebuilt.ns is ns
        assert hits == 1
        hits = 0
        revalidated = RootRegionAdmission.model_validate(rebuilt)
        assert revalidated.state is s0 and revalidated.r_result is r
        assert revalidated.scope_key == parent.scope_key
        assert hits == 1
        # Negative only: each OWN tag copied with an unsupported
        # value and a COHERENTLY recomputed scope key is refused by
        # its fixed private channel BEFORE the shared target runs
        # (zero hits).
        for tag, forged_value, pattern in (
            (
                "model_contract_version",
                "cache-root-region-admission-models/unsupported",
                "the S model contract/policy versions are the actual fixed tags",
            ),
            (
                "model_policy_version",
                "root-region-admission-models-policy/unsupported",
                "the S model contract/policy versions are the actual fixed tags",
            ),
            (
                "g_contract_version",
                "cache-current-admission/unsupported",
                "the carried G contract/policy versions are the actual fixed tags",
            ),
            (
                "g_policy_version",
                "current-admission-policy/unsupported",
                "the carried G contract/policy versions are the actual fixed tags",
            ),
        ):
            hits = 0
            forged = rebuilt.model_copy(update={tag: forged_value})
            forged = forged.model_copy(update={"scope_key": _coherent_scope(forged)})
            with pytest.raises(ValidationError, match=pattern):
                RootRegionAdmission.model_validate(forged)
            assert hits == 0
        # An explicitly deleted OWN tag field is the fixed
        # closed-field existence error before any target work.
        for tag in ("model_contract_version", "g_policy_version"):
            hits = 0
            partial = rebuilt.model_copy()
            del partial.__dict__[tag]
            assert not hasattr(partial, tag)
            with pytest.raises(
                ValidationError,
                match="the admission parent must carry its closed fields",
            ):
                RootRegionAdmission.model_validate(partial)
            assert hits == 0
    finally:
        monkeypatch.undo()


def test_d1_nested_qpf_e_closing_before_shared_target() -> None:
    """D1: at the carrying admission parent the carried nested
    Q/P/F/E context closes BEFORE the shared R result law may
    hash the scope or walk the source.  Positive FIRST: the
    genuine public P/R -> fresh S parent accepts with the real
    shared target actually reached once, and the genuine
    legitimate non-empty Q/P/G component chain (unissued mixed
    observation, anchored opaque root-bearing read, issued
    supported descendant; ONE dominated uncertainty witness,
    ONE retained P ROOT_SOURCE_UNPROVEN limitation, ONE FILE
    entry) accepts at ALL four mode/endpoint combinations.
    Negative only: the reproduced carried READY-Q own-
    diagnostic copy, the malformed carried Q bounds record,
    the coherent valid-stricter Q bounds differing from the
    actual carried R Q domain, the reproduced COHERENT F/E
    workspace carry (foreign E scope computed first, the F
    graph currentness scope and full scope keys recomputed
    through the ACTUAL original helpers, actual state/ns/
    source/bounds unchanged), and the partial actual F graph
    with a deleted required context field each refuse their
    fixed private channel BEFORE the shared target (zero
    hits).  No old public law, cap or full query re-derivation
    change."""
    ns, s0, r, g, _kr, root_entry, parent = _s_parent(MODES[0], "s-d1-nested")
    base_kwargs: dict[str, Any] = {
        "state": s0,
        "ns": ns,
        "r_result": r,
        "g_bounds": g,
        "root_entry": root_entry,
        "path_associations": parent.path_associations,
        "scope_key": parent.scope_key,
        "entries_retained": parent.entries_retained,
        "member_occurrences_charged": parent.member_occurrences_charged,
        "reverse_association_attempts": parent.reverse_association_attempts,
        "emitted_admission_reasons": parent.emitted_admission_reasons,
    }
    hits = 0
    real_target = _r_result_closed

    def _counting_target(result: RootRegionGraphResult) -> None:
        nonlocal hits
        hits += 1
        real_target(result)

    monkeypatch = pytest.MonkeyPatch()
    try:
        monkeypatch.setattr(rram, "_r_result_closed", _counting_target)
        # Positive FIRST: the genuine fresh parent accepts with
        # the real shared target actually reached once.
        rebuilt = RootRegionAdmission(**base_kwargs)
        assert rebuilt.state is s0 and rebuilt.r_result is r and rebuilt.ns is ns
        assert hits == 1
        # The genuine legitimate non-empty Q/P/G chain accepts
        # at all four mode/endpoint combinations, each fresh S
        # parent actually reaching the real shared target once.
        hits = 0
        for i, (mode, endpoint) in enumerate([(m, e) for m in MODES for e in ENDPOINTS]):
            n2, st = qf.q_bootstrap(mode, f"s-d1-nested-q-{i}", "Initial root.")
            body = qf.mixed_body(qf.A_TEXT, qf.MARK, "Initial root.")
            st = qf.q_observe(st, n2, endpoint, "unissued", body, qf.MIX_CMD)
            st = qf.q_observe(
                qf.q_issue(st, n2, "opaque", endpoint, qf.BOUNDARYLESS_CMD, (CAUSAL_ROOT_FACT,)),
                n2,
                endpoint,
                "opaque",
                qf.OPAQUE_BODY,
                qf.BOUNDARYLESS_CMD,
            )
            opaque = qf.q_occ(st, "opaque")
            st = qf.q_observe(
                qf.q_issue(st, n2, "supported", endpoint, qf.MIX_CMD, (opaque.occurrence_id,)),
                n2,
                endpoint,
                "supported",
                body,
                qf.MIX_CMD,
            )
            r2, _g2, _re2, files2, parent2, _diag2 = _s_component_parent(st, n2)
            q2 = r2.q_result
            assert q2 is not None
            assert q2.outcome is RootRegionCurrentnessOutcome.READY
            assert len(q2.uncertainty_witnesses) == 1
            assert q2.uncertainty_witnesses[0].occurrence is qf.q_occ(st, "opaque")
            p2 = q2.p_selection
            assert p2 is not None
            assert RootLineageLimitation.ROOT_SOURCE_UNPROVEN in p2.limitations
            assert not q2.diagnostics
            assert q2.p_validation_problem is None
            assert len(files2) == 1
            assert parent2.scope_key
        assert hits == 4
        # Negative only: the reproduced carried READY-Q own
        # diagnostic copy refuses the fixed private READY
        # invariant BEFORE the shared target.
        hits = 0
        q_result = r.q_result
        assert q_result is not None
        forged_q = q_result.model_copy(
            update={"diagnostics": (RootRegionCurrentnessDiagnostic.MALFORMED_BINDING,)}
        )
        with pytest.raises(
            ValidationError,
            match="a ready Q result carries no own diagnostics",
        ):
            RootRegionAdmission(
                **{
                    **base_kwargs,
                    "r_result": r.model_copy(update={"q_result": forged_q}),
                }
            )
        assert hits == 0
        # A MALFORMED carried Q bounds record (a below-range
        # scalar) is the closed bounds-record error BEFORE any
        # cap read.
        hits = 0
        forged_q = q_result.model_copy(
            update={"bounds": q_result.bounds.model_copy(update={"max_diagnostics": 0})}
        )
        with pytest.raises(
            ValidationError,
            match="the Q result bounds must be the actual closed Q bound record",
        ):
            RootRegionAdmission(
                **{
                    **base_kwargs,
                    "r_result": r.model_copy(update={"q_result": forged_q}),
                }
            )
        assert hits == 0
        # A valid STRICTER Q bounds copy that differs from the
        # actual carried R Q domain is the value-join refusal
        # (stricter copies stay legal by value in their own
        # domain; they never substitute for the carried domain).
        hits = 0
        forged_q = q_result.model_copy(
            update={"bounds": RootRegionCurrentnessBounds(max_diagnostics=1)}
        )
        with pytest.raises(
            ValidationError,
            match="the Q result bounds must equal the actual carried R Q domain",
        ):
            RootRegionAdmission(
                **{
                    **base_kwargs,
                    "r_result": r.model_copy(update={"q_result": forged_q}),
                }
            )
        assert hits == 0
        # The reproduced COHERENT F/E workspace carry: the
        # foreign E scope is computed FIRST, the F graph
        # currentness scope and full scope keys are recomputed
        # through the ACTUAL original helpers on that foreign
        # E scope, and the actual P state/ns/source/bounds stay
        # unchanged.  The copy is fully self-coherent; the ONLY
        # broken association is the carried F/E context versus
        # the actual namespace workspace, so the fixed private
        # S workspace join must refuse BEFORE the shared
        # target.
        hits = 0
        f_result = r.f_result
        assert f_result is not None
        graph = f_result.overlay
        assert graph is not None
        overlay = r.e_overlay
        assert overlay is not None
        foreign = "/foreign-work"
        e_scope2 = currentness_scope_key(
            overlay.history_key, foreign, overlay.policy_version, overlay.bounds
        )
        overlay2 = overlay.model_copy(update={"workspace": foreign, "scope_key": e_scope2})
        graph2 = graph.model_copy(
            update={
                "workspace": foreign,
                "currentness_scope_key": e_scope2,
                "scope_key": current_graph_scope_key(
                    graph.history_key,
                    foreign,
                    graph.root_digest,
                    graph.contract_version,
                    graph.policy_version,
                    graph.graph_version,
                    graph.reference_version,
                    graph.proof_version,
                    graph.currentness_contract_version,
                    graph.currentness_policy_version,
                    graph.currentness_recipe_version,
                    e_scope2,
                    graph.bounds,
                    graph.currentness_bounds,
                    graph.graph_bounds,
                ),
            }
        )
        with pytest.raises(
            ValidationError,
            match="the F graph workspace must equal the actual namespace workspace",
        ):
            RootRegionAdmission(
                **{
                    **base_kwargs,
                    "r_result": r.model_copy(
                        update={
                            "f_result": f_result.model_copy(update={"overlay": graph2}),
                            "e_overlay": overlay2,
                        }
                    ),
                }
            )
        assert hits == 0
        # A PARTIAL actual F graph (a deleted required context
        # field) is the fixed closed-field existence error --
        # never an AttributeError -- before the shared target.
        hits = 0
        graph_partial = graph.model_copy()
        del graph_partial.__dict__["workspace"]
        assert not hasattr(graph_partial, "workspace")
        with pytest.raises(
            ValidationError,
            match="the F graph must carry its closed context fields",
        ):
            RootRegionAdmission(
                **{
                    **base_kwargs,
                    "r_result": r.model_copy(
                        update={"f_result": f_result.model_copy(update={"overlay": graph_partial})}
                    ),
                }
            )
        assert hits == 0
    finally:
        monkeypatch.undo()


def test_d1_nested_envelope_anchor_workspace_join_before_shared_target() -> None:
    """D1: the ACTUAL envelope-to-context metadata join closes the
    selected envelope fact's workspace against BOTH the actual P
    namespace workspace and the retained D anchor workspace (the
    anchor's concrete class and own workspace field closed before
    any dereference) BEFORE the shared R result law may hash the
    scope or walk the source.  Positive FIRST: the genuine public
    P/R -> fresh S parent accepts with the real shared target
    reached once.  Negative only: the coherent foreign envelope
    workspace (propagated through the copied P state, Q state and
    P-selection, the resolved source and the root entry, actual
    anchor/ns/bounds/scope unchanged), and the foreign,
    field-deleted and wrong-class retained D anchors (each with
    the copied D -> P state and the R.state / Q.state / F.state
    refs carried coherently) each refuse their fixed private
    channel BEFORE the shared target (zero hits).  Local
    workspace/class/field join only; no old public law, cap or
    full P/D re-derivation change."""
    ns, s0, r, g, _kr, root_entry, parent = _s_parent(MODES[0], "s-d1-env-join")
    base_kwargs: dict[str, Any] = {
        "state": s0,
        "ns": ns,
        "r_result": r,
        "g_bounds": g,
        "root_entry": root_entry,
        "path_associations": parent.path_associations,
        "scope_key": parent.scope_key,
        "entries_retained": parent.entries_retained,
        "member_occurrences_charged": parent.member_occurrences_charged,
        "reverse_association_attempts": parent.reverse_association_attempts,
        "emitted_admission_reasons": parent.emitted_admission_reasons,
    }
    hits = 0
    real_target = _r_result_closed

    def _counting_target(result: RootRegionGraphResult) -> None:
        nonlocal hits
        hits += 1
        real_target(result)

    monkeypatch = pytest.MonkeyPatch()
    try:
        monkeypatch.setattr(rram, "_r_result_closed", _counting_target)
        # Positive FIRST: the genuine fresh parent accepts with
        # the real shared target actually reached once.
        rebuilt = RootRegionAdmission(**base_kwargs)
        assert rebuilt.state is s0 and rebuilt.r_result is r and rebuilt.ns is ns
        assert hits == 1
        # The genuine envelope fact's workspace joins the actual
        # namespace and retained anchor workspaces.
        q0 = r.q_result
        assert q0 is not None
        p0 = q0.p_selection
        assert p0 is not None
        assert len(p0.witness_facts) == 1
        env = p0.witness_facts[0]
        assert isinstance(env.provenance, EnvelopeRootProvenance)
        anchor = s0.d_state.root
        assert isinstance(anchor, RootAnchor)
        assert env.provenance.workspace == ns.workspace == anchor.workspace
        # Negative 1: the coherent FOREIGN envelope workspace
        # propagates through the copied P state, the Q state and
        # P-selection, the resolved source and the root entry; the
        # actual anchor, ns, bounds and scopes stay unchanged.
        hits = 0
        prov2 = env.provenance.model_copy(update={"workspace": "/foreign-work"})
        fact2 = env.model_copy(update={"provenance": prov2})
        state2 = s0.model_copy(update={"root_facts": (fact2,)})
        p2 = p0.model_copy(update={"witness_facts": (fact2,)})
        q2 = q0.model_copy(update={"state": state2, "p_selection": p2})
        resolved0 = r.resolved_source
        assert resolved0 is not None
        resolved2 = resolved0.model_copy(update={"fact": fact2})
        r2 = r.model_copy(update={"state": state2, "q_result": q2, "resolved_source": resolved2})
        entry2 = root_entry.model_copy(update={"root_source": resolved2})
        with pytest.raises(
            ValidationError,
            match="the envelope fact workspace must equal the actual namespace workspace",
        ):
            RootRegionAdmission(
                **{**base_kwargs, "state": state2, "r_result": r2, "root_entry": entry2}
            )
        assert hits == 0
        # The foreign carry leaves the configuration scope unchanged.
        assert r2.scope_key == r.scope_key
        rscope2 = root_region_graph_scope_key(
            r2.lineage_key,
            r2.contract_version,
            r2.policy_version,
            r2.bounds,
            r2.q_bounds,
            r2.f_bounds,
            r2.e_bounds,
            r2.graph_version,
        )
        assert rscope2 == r.scope_key
        assert s0.root_facts[0] is env and s0.d_state.root is anchor
        # Negatives 2-4: the foreign / field-deleted / wrong-class
        # retained D anchor, each with the copied D -> P state and
        # the R.state / Q.state / F.state refs carried coherently
        # (the original envelope workspace still equals the
        # namespace, so only the anchor association breaks).
        anchor_missing = s0.d_state.root.model_copy()
        del anchor_missing.__dict__["workspace"]
        assert not hasattr(anchor_missing, "workspace")
        f0 = r.f_result
        assert f0 is not None
        anchor_cases: tuple[tuple[str, Any], ...] = (
            (
                "the envelope fact workspace must equal the retained anchor workspace",
                anchor.model_copy(update={"workspace": "/elsewhere"}),
            ),
            (
                "the retained D anchor must carry its closed workspace field",
                anchor_missing,
            ),
            (
                "the retained D anchor must be the actual closed anchor record",
                None,
            ),
        )
        for pattern, bad_anchor in anchor_cases:
            hits = 0
            d2 = s0.d_state.model_copy(update={"root": bad_anchor})
            state3 = s0.model_copy(update={"d_state": d2})
            q3 = q0.model_copy(update={"state": state3})
            f3 = f0.model_copy(update={"state": d2})
            r3 = r.model_copy(update={"state": state3, "q_result": q3, "f_result": f3})
            with pytest.raises(ValidationError, match=pattern):
                RootRegionAdmission(**{**base_kwargs, "state": state3, "r_result": r3})
            assert hits == 0
        # The original inputs stay untouched by every negative.
        assert s0.root_facts[0] is env and s0.d_state.root is anchor
        assert env.provenance.workspace == ns.workspace == anchor.workspace
    finally:
        monkeypatch.undo()


def test_d1_nested_qp_canonical_duplicates_before_shared_target() -> None:
    """D1: the ACTUAL canonical-order law sorts and deduplicates
    the carried Q uncertainty witnesses by
    (uncertainty_class.value, occurrence_id) and the carried P
    selection witness facts by their actual provenance identity
    key, AFTER the closed metadata/count gates and BEFORE the
    shared R result law.  Positive FIRST: the genuine legitimate
    non-empty Q/P/G component chain (ONE dominated uncertainty
    witness, the retained P facts with the ROOT_SOURCE_UNPROVEN
    limitation) accepts at ALL four mode/endpoint combinations,
    each fresh S parent reaching the real shared target once.
    Negative only: at every combination, a duplicated SAME
    original Q uncertainty witness and a duplicated SAME original
    selected P fact are negative-only coherent copies that each
    refuse their fixed private canonical error BEFORE the shared
    target (zero hits).  No old public law, cap or full query
    re-derivation change."""
    hits = 0
    real_target = _r_result_closed

    def _counting_target(result: RootRegionGraphResult) -> None:
        nonlocal hits
        hits += 1
        real_target(result)

    monkeypatch = pytest.MonkeyPatch()
    try:
        monkeypatch.setattr(rram, "_r_result_closed", _counting_target)
        for i, (mode, endpoint) in enumerate([(m, e) for m in MODES for e in ENDPOINTS]):
            n2, st = qf.q_bootstrap(mode, f"s-d1-qpdupe-{i}", "Initial root.")
            body = qf.mixed_body(qf.A_TEXT, qf.MARK, "Initial root.")
            st = qf.q_observe(st, n2, endpoint, "unissued", body, qf.MIX_CMD)
            st = qf.q_observe(
                qf.q_issue(st, n2, "opaque", endpoint, qf.BOUNDARYLESS_CMD, (CAUSAL_ROOT_FACT,)),
                n2,
                endpoint,
                "opaque",
                qf.OPAQUE_BODY,
                qf.BOUNDARYLESS_CMD,
            )
            st = qf.q_observe(
                qf.q_issue(
                    st,
                    n2,
                    "supported",
                    endpoint,
                    qf.MIX_CMD,
                    (qf.q_occ(st, "opaque").occurrence_id,),
                ),
                n2,
                endpoint,
                "supported",
                body,
                qf.MIX_CMD,
            )
            rq, gq, req, _fq, parentq, _dq = _s_component_parent(st, n2)
            q2 = rq.q_result
            assert q2 is not None
            assert q2.outcome is RootRegionCurrentnessOutcome.READY
            w = q2.uncertainty_witnesses[0]
            p2 = q2.p_selection
            assert p2 is not None
            assert len(p2.witness_facts) >= 1
            assert RootLineageLimitation.ROOT_SOURCE_UNPROVEN in p2.limitations
            assert not q2.diagnostics
            assert q2.p_validation_problem is None
            base_kwargs: dict[str, Any] = {
                "state": st,
                "ns": n2,
                "r_result": rq,
                "g_bounds": gq,
                "root_entry": req,
                "entries": parentq.entries,
                "admission_reasons": parentq.admission_reasons,
                "path_associations": parentq.path_associations,
                "scope_key": parentq.scope_key,
                "entries_retained": parentq.entries_retained,
                "member_occurrences_charged": parentq.member_occurrences_charged,
                "reverse_association_attempts": parentq.reverse_association_attempts,
                "emitted_admission_reasons": parentq.emitted_admission_reasons,
            }
            # Positive FIRST: this genuine component chain accepts
            # with the real shared target actually reached once.
            hits = 0
            rebuilt = RootRegionAdmission(**base_kwargs)
            assert rebuilt.state is st and rebuilt.r_result is rq
            assert rebuilt.ns is n2
            assert hits == 1
            # Negative 1: the duplicated SAME original Q
            # uncertainty witness is the fixed canonical
            # order/dedup error before the shared target.
            hits = 0
            q_dupe = q2.model_copy(update={"uncertainty_witnesses": (w, w)})
            with pytest.raises(
                ValidationError,
                match="the Q uncertainty witnesses must be sorted and deduplicated",
            ):
                RootRegionAdmission(
                    **{
                        **base_kwargs,
                        "r_result": rq.model_copy(update={"q_result": q_dupe}),
                    }
                )
            assert hits == 0
            # Negative 2: the duplicated SAME original selected P
            # fact is the fixed canonical order/dedup error before
            # the shared target.
            hits = 0
            sel_facts = [
                f for f in p2.witness_facts if f.source_digest == p2.selected_source_digest
            ]
            dup_fact = sel_facts[0] if sel_facts else p2.witness_facts[0]
            p_dupe = p2.model_copy(update={"witness_facts": (dup_fact, dup_fact)})
            with pytest.raises(
                ValidationError,
                match="the P selection witness facts must be sorted and deduplicated",
            ):
                RootRegionAdmission(
                    **{
                        **base_kwargs,
                        "r_result": rq.model_copy(
                            update={"q_result": q2.model_copy(update={"p_selection": p_dupe})}
                        ),
                    }
                )
            assert hits == 0
    finally:
        monkeypatch.undo()


def test_d1_nested_q_headers_and_witness_closure_before_shared_target() -> None:
    """D1: the carried Q result's ACTUAL touched scalar/enum/
    header fields and its uncertainty witnesses close under the
    original call-id / endpoint / class-count / join / proof /
    length and canonical-domain gates BEFORE the shared R result
    law may hash the scope or walk the source.  Positive FIRST:
    the genuine legitimate non-empty Q/P/G component chain
    accepts with the real shared target reached once.  Negative
    only: each unsupported-version, malformed-key, non-bool or
    string revision and malformed-digest carry, and each witness
    overlong / spaced call id, unvalidated endpoint, wrong
    class-count relation, unanchored occurrence, unjoined
    occurrence id or result call, unjoined proof digest, bool
    proof length and over-domain witness count, refuses its
    fixed private channel BEFORE the shared target (zero hits).
    No old public law, cap or full query re-derivation change."""
    n2, st = qf.q_bootstrap(MODES[0], "s-d1-qhdr", "Initial root.")
    body = qf.mixed_body(qf.A_TEXT, qf.MARK, "Initial root.")
    st = qf.q_observe(st, n2, ENDPOINTS[0], "unissued", body, qf.MIX_CMD)
    st = qf.q_observe(
        qf.q_issue(st, n2, "opaque", ENDPOINTS[0], qf.BOUNDARYLESS_CMD, (CAUSAL_ROOT_FACT,)),
        n2,
        ENDPOINTS[0],
        "opaque",
        qf.OPAQUE_BODY,
        qf.BOUNDARYLESS_CMD,
    )
    st = qf.q_observe(
        qf.q_issue(
            st,
            n2,
            "supported",
            ENDPOINTS[0],
            qf.MIX_CMD,
            (qf.q_occ(st, "opaque").occurrence_id,),
        ),
        n2,
        ENDPOINTS[0],
        "supported",
        body,
        qf.MIX_CMD,
    )
    rq, gq, req, _fq, parentq, _dq = _s_component_parent(st, n2)
    q2 = rq.q_result
    assert q2 is not None
    assert q2.outcome is RootRegionCurrentnessOutcome.READY
    assert q2.usable_selected_source_digest is not None
    w = q2.uncertainty_witnesses[0]
    assert w.uncertainty_class is RootRegionUncertaintyClass.OPAQUE_ROOT_BEARING_GROUP
    p2 = q2.p_selection
    assert p2 is not None
    assert not q2.diagnostics
    assert q2.p_validation_problem is None
    base_kwargs: dict[str, Any] = {
        "state": st,
        "ns": n2,
        "r_result": rq,
        "g_bounds": gq,
        "root_entry": req,
        "entries": parentq.entries,
        "admission_reasons": parentq.admission_reasons,
        "path_associations": parentq.path_associations,
        "scope_key": parentq.scope_key,
        "entries_retained": parentq.entries_retained,
        "member_occurrences_charged": parentq.member_occurrences_charged,
        "reverse_association_attempts": parentq.reverse_association_attempts,
        "emitted_admission_reasons": parentq.emitted_admission_reasons,
    }
    hits = 0
    real_target = _r_result_closed

    def _counting_target(result: RootRegionGraphResult) -> None:
        nonlocal hits
        hits += 1
        real_target(result)

    def _q(update: dict[str, Any]) -> RootRegionGraphResult:
        forged_q = q2.model_copy(update=update)
        forged_r: RootRegionGraphResult = rq.model_copy(update={"q_result": forged_q})
        return forged_r

    def _witness(update: dict[str, Any]) -> RootRegionGraphResult:
        return _q({"uncertainty_witnesses": (w.model_copy(update=update),)})

    def _witnesses(value: tuple[Any, ...]) -> RootRegionGraphResult:
        return _q({"uncertainty_witnesses": value})

    def _neg(forged: RootRegionGraphResult, match: str) -> None:
        nonlocal hits
        hits = 0
        with pytest.raises(ValidationError, match=match):
            RootRegionAdmission(**{**base_kwargs, "r_result": forged})
        assert hits == 0

    monkeypatch = pytest.MonkeyPatch()
    try:
        monkeypatch.setattr(rram, "_r_result_closed", _counting_target)
        # Positive FIRST: the genuine component chain accepts with
        # the real shared target actually reached once.
        rebuilt = RootRegionAdmission(**base_kwargs)
        assert rebuilt.state is st and rebuilt.r_result is rq and rebuilt.ns is n2
        assert hits == 1
        # Q result scalar/enum/header refusals before the target.
        _neg(
            _q({"contract_version": "cache-root-region-currentness/v2"}),
            "the Q result must carry the actual supported version identities",
        )
        _neg(_q({"lineage_key": "0" * 63}), "lineage_key must be a 64-hex digest")
        _neg(
            _q({"revision": True}),
            "the Q result revision must be a closed non-bool integer",
        )
        _neg(
            _q({"revision": "3"}),
            "the Q result revision must be a closed non-bool integer",
        )
        _neg(
            _q({"usable_selected_source_digest": "zz"}),
            "usable_selected_source_digest must be a 64-hex digest",
        )
        # Q witness call/endpoint/class-count/join/proof/length.
        _neg(
            _witness({"call_id": "x" * 257}),
            "the Q uncertainty witness call id must be bounded non-space metadata",
        )
        _neg(
            _witness({"call_id": "ab cd"}),
            "the Q uncertainty witness call id must be bounded non-space metadata",
        )
        _neg(
            _witness({"endpoint": "bogus"}),
            "the Q uncertainty witness endpoint must be an explicit validated endpoint",
        )
        _neg(
            _witness(
                {
                    "uncertainty_class": RootRegionUncertaintyClass.UNSUPPORTED_ROOT_SHAPE,
                    "root_operand_count": 1,
                }
            ),
            "the Q uncertainty witness unsupported shape requires repeated root operands",
        )
        _neg(
            _witness({"root_operand_count": 2}),
            "the Q uncertainty witness opaque group carries exactly one root operand",
        )
        _neg(
            _witness({"occurrence": w.occurrence.model_copy(update={"anchored": False})}),
            "the Q uncertainty witness requires an anchored retained occurrence",
        )
        _neg(
            _witness({"occurrence_id": "0" * 64}),
            "the Q uncertainty witness occurrence id must join the retained occurrence",
        )
        _neg(
            _witness(
                {"result_record": w.result_record.model_copy(update={"call_id": "call-other"})}
            ),
            "the Q uncertainty witness result must match the retained occurrence call",
        )
        _neg(
            _witness({"whole_proof_digest": "1" * 64}),
            "the Q uncertainty witness whole digest must match the retained proof",
        )
        _neg(
            _witness({"whole_proof_byte_length": True}),
            "the Q uncertainty witness proof length must be a closed non-bool count",
        )
        _neg(
            _witnesses((w,) * 4097),
            "the Q uncertainty witnesses exceed the actual retained occurrence domain",
        )
    finally:
        monkeypatch.undo()


def test_d1_nested_p_fact_variant_metadata_closure_before_shared_target() -> None:
    """D1: the carried P selection's retained witness facts close
    under the per-variant provenance class / own-field / kind /
    flag / binding joins, the fact-level length gate and the
    fact-domain count law BEFORE the shared R result law may hash
    the scope or walk the source.  Positive FIRST per variant:
    THREE genuine selected-source fixtures -- the bootstrap
    envelope, the issued whole read of the root contract file and
    the issued mixed-only region -- each accept with the real
    shared target reached once.  Negative only: each own field
    deleted from the actual provenance copy (including kind), the
    mismatched kind, each bool / below-range / over-hard-limit
    fact length, the unissued-but-authoritative non-envelope fact,
    the issued envelope fact and each broken source binding
    refuses its fixed private channel BEFORE the shared target
    (zero hits).  No old public law, cap or full query
    re-derivation change."""
    fixtures: list[tuple[str, Any, Any, Any, Any, Any, tuple[str, ...]]] = []
    ns_e, state_e, r_e, g_e, _rec_e, _entry_e, parent_e = _s_parent(MODES[0], "s-d1-pfenv")
    fixtures.append(("envelope", ns_e, state_e, r_e, g_e, parent_e, _R_ENVELOPE_PROV_FIELDS))
    ns_r, state_r = r_bootstrap(MODES[0], "s-d1-pfwhole")
    cmd = "cat AGENTS.md"
    t1 = r_issue(state_r, ns_r, "whole", "responses", (CAUSAL_ROOT_FACT,), cmd)
    assert t1.outcome.value == "accepted"
    t2 = r_observe(t1.state, ns_r, (read_request("responses", "whole", V2, cmd),))
    assert t2.outcome.value == "accepted"
    state_r2 = t2.state
    r_r = derive_root_region_graph(state_r2, ns_r)
    assert r_r.outcome is RootRegionGraphOutcome.READY
    g_r = CurrentAdmissionBounds()
    parent_r = _s_parent_from_assembly(ns_r, state_r2, r_r, g_r)[-1]
    fixtures.append(("read", ns_r, state_r2, r_r, g_r, parent_r, _R_READ_PROV_FIELDS))
    ns_g, state_g = _mixed_region_state(MODES[0], "responses", "s-d1-pfregion")
    r_g = derive_root_region_graph(state_g, ns_g)
    assert r_g.outcome is RootRegionGraphOutcome.READY
    g_g = CurrentAdmissionBounds()
    parent_g = _s_parent_from_assembly(ns_g, state_g, r_g, g_g)[-1]
    fixtures.append(
        (
            "read_region",
            ns_g,
            state_g,
            r_g,
            g_g,
            parent_g,
            _R_REGION_PROV_FIELDS,
        )
    )
    hits = 0
    real_target = _r_result_closed

    def _counting_target(result: RootRegionGraphResult) -> None:
        nonlocal hits
        hits += 1
        real_target(result)

    monkeypatch = pytest.MonkeyPatch()
    try:
        monkeypatch.setattr(rram, "_r_result_closed", _counting_target)
        for kind, ns, state, r, g, parent, fields in fixtures:
            kwargs: dict[str, Any] = {
                name: getattr(parent, name) for name in type(parent).model_fields
            }
            # Positive FIRST per variant: the genuine selected-
            # source fixture accepts with the real shared target
            # actually reached once.
            hits = 0
            rebuilt = RootRegionAdmission(**kwargs)
            assert rebuilt.state is state and rebuilt.r_result is r
            assert rebuilt.ns == ns and rebuilt.g_bounds == g
            assert hits == 1
            q = r.q_result
            assert q is not None
            p = q.p_selection
            assert p is not None
            resolved = r.resolved_source
            assert resolved is not None
            selected = resolved.fact
            assert selected.provenance.kind == kind
            assert resolved.kind == kind
            index = next(i for i, fact in enumerate(p.witness_facts) if fact is selected)
            last_q: RootRegionCurrentnessResult | None = q
            last_p: RootRegionSelectionResult | None = p
            last_r: RootRegionGraphResult | None = r
            last_kwargs: dict[str, Any] | None = kwargs

            def _bad_facts(
                fact: Any,
                _p: Any = p,
                _index: int = index,
                _q: Any = q,
                _r: Any = r,
            ) -> RootRegionGraphResult:
                facts = list(_p.witness_facts)
                facts[_index] = fact
                bad_p = _p.model_copy(update={"witness_facts": tuple(facts)})
                bad_q = _q.model_copy(update={"p_selection": bad_p})
                bad_r: RootRegionGraphResult = _r.model_copy(update={"q_result": bad_q})
                return bad_r

            def _neg(
                forged: RootRegionGraphResult,
                match: str,
                _kwargs: dict[str, Any] = kwargs,
            ) -> None:
                nonlocal hits
                hits = 0
                with pytest.raises(ValidationError, match=match):
                    RootRegionAdmission(**{**_kwargs, "r_result": forged})
                assert hits == 0

            # Own-field existence for EVERY variant field (including
            # kind): a deleted own field is the fixed closed-variant-
            # fields error, never an AttributeError.
            for field in fields:
                prov = selected.provenance.model_copy()
                del prov.__dict__[field]
                assert not hasattr(prov, field)
                _neg(
                    _bad_facts(selected.model_copy(update={"provenance": prov})),
                    "the fact provenance must carry its closed variant fields",
                )
            # The kind must match the concrete provenance class.
            wrong_kind = {"envelope": "read", "read": "read_region", "read_region": "envelope"}[
                kind
            ]
            _neg(
                _bad_facts(
                    selected.model_copy(
                        update={
                            "provenance": selected.provenance.model_copy(
                                update={"kind": wrong_kind}
                            )
                        }
                    )
                ),
                "the fact provenance kind must match its concrete class",
            )
            # The fact-level length gate (bool / below-range / over
            # the original hard limit).
            for bad_length in (True, -1, 16777217):
                _neg(
                    _bad_facts(selected.model_copy(update={"source_byte_length": bad_length})),
                    "the P selection witness fact length must be a closed non-bool count",
                )
            # Flag and source-binding joins.
            if kind == "envelope":
                _neg(
                    _bad_facts(selected.model_copy(update={"issued": True})),
                    "the envelope fact is never issued and always authoritative",
                )
                _neg(
                    _bad_facts(selected.model_copy(update={"source_digest": "1" * 64})),
                    "the envelope fact source must equal the anchor binding",
                )
            else:
                flag_error = (
                    "a read fact is authoritative only when issued"
                    if kind == "read"
                    else "a region fact is authoritative only when issued"
                )
                binding_error = (
                    "the read fact source must equal the whole-read binding"
                    if kind == "read"
                    else "the region fact source must equal the root member binding"
                )
                _neg(
                    _bad_facts(selected.model_copy(update={"issued": False, "authority": True})),
                    flag_error,
                )
                _neg(
                    _bad_facts(
                        selected.model_copy(
                            update={"source_byte_length": selected.source_byte_length + 1}
                        )
                    ),
                    binding_error,
                )
        # The fact-domain count gate before any fact walk (the
        # last genuine fixture's closed nested context).
        assert last_q is not None and last_p is not None
        assert last_r is not None and last_kwargs is not None
        hits = 0
        bad_p = last_p.model_copy(
            update={"witness_facts": tuple(last_p.witness_facts[0] for _ in range(1025))}
        )
        bad_q = last_q.model_copy(update={"p_selection": bad_p})
        bad_r: RootRegionGraphResult = last_r.model_copy(update={"q_result": bad_q})
        with pytest.raises(
            ValidationError,
            match="the P selection witness facts exceed the actual retained root fact domain",
        ):
            RootRegionAdmission(**{**last_kwargs, "r_result": bad_r})
        assert hits == 0
    finally:
        monkeypatch.undo()


def test_d1_nested_fe_context_headers_before_shared_target() -> None:
    """D1: at the carrying admission parent the carried F graph /
    E overlay context headers close under the actual class /
    required-field / closed-text / 64-hex / supported-version /
    non-bool revision / namespace-workspace law BEFORE the shared
    R result law may hash the scope or walk the source.
    Positive FIRST: the genuine public P/R -> fresh S parent
    accepts with the real shared target actually reached once.
    Negative only: each bool / none / text / float / negative /
    over-hard actual revision on the F graph AND the E overlay,
    the deleted required revision field, each malformed 63-hex
    identity key, each unsupported version tag and each
    non-text context field refuses its fixed private channel
    BEFORE the shared target (zero hits).  No old public law,
    cap or full policy replay change."""
    ns, s0, r, g, _kr, _entry, parent = _s_parent(MODES[0], "s-d1-fehdr")
    f = r.f_result
    assert f is not None
    graph = f.overlay
    overlay = r.e_overlay
    assert graph is not None and overlay is not None
    kwargs: dict[str, Any] = {name: getattr(parent, name) for name in type(parent).model_fields}
    hits = 0
    real_target = _r_result_closed

    def _counting_target(result: RootRegionGraphResult) -> None:
        nonlocal hits
        hits += 1
        real_target(result)

    def _splice(
        carrier: str,
        update: dict[str, Any] | None = None,
        missing: str = "",
    ) -> RootRegionGraphResult:
        original = overlay if carrier == "e" else graph
        if update is None:
            nested = original.model_copy()
        else:
            nested = original.model_copy(update=update)
        if missing:
            del nested.__dict__[missing]
            assert not hasattr(nested, missing)
        if carrier == "e":
            bad_r: RootRegionGraphResult = r.model_copy(update={"e_overlay": nested})
            return bad_r
        bad_f = f.model_copy(update={"overlay": nested})
        bad_r2: RootRegionGraphResult = r.model_copy(update={"f_result": bad_f})
        return bad_r2

    monkeypatch = pytest.MonkeyPatch()
    try:
        monkeypatch.setattr(rram, "_r_result_closed", _counting_target)
        # Positive FIRST: the genuine fresh parent accepts with
        # the real shared target actually reached once.
        rebuilt = RootRegionAdmission(**kwargs)
        assert rebuilt.state is s0 and rebuilt.r_result is r and rebuilt.ns is ns
        assert hits == 1
        # The closed non-bool revision scalar over the original
        # 0..MAX_REVISION range, on BOTH actual carriers.
        for carrier in ("e", "f"):
            revision_error = (
                "the E overlay revision must be a closed non-bool integer"
                if carrier == "e"
                else "the F graph revision must be a closed non-bool integer"
            )
            fields_error = (
                "the E overlay must carry its closed identity fields"
                if carrier == "e"
                else "the F graph must carry its closed context fields"
            )
            for value in (True, None, "1", 1.0, -1, MAX_REVISION + 1):
                hits = 0
                with pytest.raises(
                    ValidationError,
                    match=revision_error,
                ):
                    RootRegionAdmission(
                        **{**kwargs, "r_result": _splice(carrier, {"revision": value})}
                    )
                assert hits == 0
            # The deleted required revision field is the closed
            # field-existence error, never an attribute error.
            hits = 0
            with pytest.raises(
                ValidationError,
                match=fields_error,
            ):
                RootRegionAdmission(**{**kwargs, "r_result": _splice(carrier, missing="revision")})
            assert hits == 0
        # F graph context headers.
        hits = 0
        with pytest.raises(ValidationError, match="history_key must be a 64-hex digest"):
            RootRegionAdmission(**{**kwargs, "r_result": _splice("f", {"history_key": "0" * 63})})
        assert hits == 0
        hits = 0
        with pytest.raises(
            ValidationError,
            match="the F graph must carry the actual supported version identities",
        ):
            RootRegionAdmission(
                **{
                    **kwargs,
                    "r_result": _splice("f", {"contract_version": "cache-current-graph/v2"}),
                }
            )
        assert hits == 0
        hits = 0
        with pytest.raises(ValidationError, match="the F graph context fields must be closed text"):
            RootRegionAdmission(**{**kwargs, "r_result": _splice("f", {"graph_version": 123})})
        assert hits == 0
        # E overlay context headers.
        hits = 0
        with pytest.raises(
            ValidationError,
            match="the E overlay must carry the actual supported policy identity",
        ):
            RootRegionAdmission(
                **{**kwargs, "r_result": _splice("e", {"policy_version": "currentness-policy/v2"})}
            )
        assert hits == 0
        hits = 0
        with pytest.raises(ValidationError, match="history_key must be a 64-hex digest"):
            RootRegionAdmission(**{**kwargs, "r_result": _splice("e", {"history_key": "0" * 63})})
        assert hits == 0
        hits = 0
        with pytest.raises(
            ValidationError, match="the E overlay context fields must be closed text"
        ):
            RootRegionAdmission(**{**kwargs, "r_result": _splice("e", {"workspace": 123})})
        assert hits == 0
    finally:
        monkeypatch.undo()


def test_d1_nested_r_carried_bound_subclass_closure_before_shared_target() -> None:
    """D1: at the carrying admission parent the FOUR R-carried
    bound sets close under their EXACT ORIGINAL concrete class
    BEFORE the old R shape helpers, any serializer or the shared
    R scope/source law may run.  Positive FIRST: the genuine
    public P/R -> fresh S parent accepts with the real shared
    target reached once, and the genuine public R rebuilt with
    ALL FOUR valid stricter original-class bound copies
    (max_diagnostics 1) accepts with the real shared target
    reached once again (a valid stricter base class copy stays
    legal by value).  Negative only: each of the four carried
    sets as a subclass instance whose original scalar fields
    carry the SAME valid values (recomputed scope unchanged)
    refuses the fixed private eleven-bound error BEFORE the
    shared target (zero hits).  No old public R helper, schema,
    range, cap or serializer change."""
    ns, s0, r, g, _kr, _entry, parent = _s_parent(MODES[0], "s-d1-rbound")
    kwargs: dict[str, Any] = {name: getattr(parent, name) for name in type(parent).model_fields}
    hits = 0
    real_target = _r_result_closed

    def _counting_target(result: RootRegionGraphResult) -> None:
        nonlocal hits
        hits += 1
        real_target(result)

    class ExtraRBounds(RootRegionGraphBounds):
        extra_metadata: tuple[str, ...] = ("synthetic",)

    class ExtraQBounds(RootRegionCurrentnessBounds):
        extra_metadata: tuple[str, ...] = ("synthetic",)

    class ExtraFBounds(CurrentGraphBounds):
        extra_metadata: tuple[str, ...] = ("synthetic",)

    class ExtraEBounds(CurrentnessBounds):
        extra_metadata: tuple[str, ...] = ("synthetic",)

    monkeypatch = pytest.MonkeyPatch()
    try:
        monkeypatch.setattr(rram, "_r_result_closed", _counting_target)
        # Positive FIRST: the genuine fresh parent accepts with
        # the real shared target actually reached once.
        rebuilt = RootRegionAdmission(**kwargs)
        assert rebuilt.state is s0 and rebuilt.r_result is r and rebuilt.ns is ns
        assert hits == 1
        # Genuine public R rebuilt with ALL FOUR valid stricter
        # ORIGINAL-class bound copies: stricter by value stays
        # legal, so the class fence is not a scalar-cap proxy.
        strict = {
            name: getattr(r, name).model_copy(update={"max_diagnostics": 1})
            for name in ("bounds", "q_bounds", "f_bounds", "e_bounds")
        }
        r_strict = derive_root_region_graph(
            s0,
            ns,
            strict["bounds"],
            root_region_currentness_bounds=strict["q_bounds"],
            current_graph_bounds=strict["f_bounds"],
            nonroot_currentness_bounds=strict["e_bounds"],
        )
        assert r_strict.outcome is RootRegionGraphOutcome.READY
        hits = 0
        strict_parent = _s_parent_from_assembly(ns, s0, r_strict, g)[-1]
        assert strict_parent.r_result is r_strict and strict_parent.state is s0
        assert hits == 1
        # Negative only: each carried set as an exact subclass
        # with the SAME valid original scalar values (scope
        # recomputed unchanged) is foreign at the carrying
        # boundary, fixed private, before the shared target.
        for field, extra_cls in (
            ("bounds", ExtraRBounds),
            ("q_bounds", ExtraQBounds),
            ("f_bounds", ExtraFBounds),
            ("e_bounds", ExtraEBounds),
        ):
            original = getattr(r, field)
            extra = extra_cls(**original.model_dump())
            assert type(extra) is not type(original)
            assert all(
                getattr(extra, name) == getattr(original, name)
                for name in type(original).model_fields
            )
            bound_sets = {
                name: getattr(r, name) for name in ("bounds", "q_bounds", "f_bounds", "e_bounds")
            }
            bound_sets[field] = extra
            scope = root_region_graph_scope_key(
                r.lineage_key,
                r.contract_version,
                r.policy_version,
                bound_sets["bounds"],
                bound_sets["q_bounds"],
                bound_sets["f_bounds"],
                bound_sets["e_bounds"],
                r.graph_version,
            )
            assert scope == r.scope_key
            bad_r = r.model_copy(update={field: extra, "scope_key": scope})
            assert _s_all_eleven_bound_sets_closed(ns, bad_r, g) is False
            hits = 0
            with pytest.raises(
                ValidationError,
                match="the actual eleven carried bound sets must be closed scalar sets",
            ):
                RootRegionAdmission(**{**kwargs, "r_result": bad_r})
            assert hits == 0
    finally:
        monkeypatch.undo()


def test_d1_nested_p_selection_headers_and_variant_scalar_closure_before_shared_target() -> None:
    """D1: the carried P selection closes under its ACTUAL
    result / outcome / lineage-hex / non-bool-revision /
    selected-digest headers, the limitation container / enum /
    canonical law and the per-variant provenance scalar / UTF8
    law BEFORE the shared R result law may hash the scope or
    walk the source.  Positive FIRST per variant: the SAME
    THREE genuine selected-source fixtures as the fact-metadata
    group (bootstrap envelope, issued whole read, issued mixed-
    only region) each accept with the real shared target
    reached once.  Negative only: each malformed P selection
    header value on the envelope fixture (wrong-class outcome,
    63-hex / non-text lineage, bool / below-range / over-hard
    revision, 63-hex selected digest, non-tuple facts,
    non-tuple / non-enum / unsorted / duplicate / over-ceiling
    limitations) and each malformed envelope / read /
    read_region provenance scalar (relative / over-long /
    control / non-text / surrogate workspace, zero / over-hard
    / space / non-text / surrogate call id, unsupported
    endpoint, non-text identity, 63-hex ids and digests, bool
    / below-range lengths and indices) refuses its fixed
    private channel BEFORE the shared target (zero hits).  No
    old public law, cap or full query re-derivation change."""
    fixtures: list[tuple[str, Any, Any, Any, Any, Any]] = []
    ns_e, state_e, r_e, g_e, _rec_e, _entry_e, parent_e = _s_parent(MODES[0], "s-d1-pshdr")
    fixtures.append(("envelope", ns_e, state_e, r_e, g_e, parent_e))
    ns_r, state_r = r_bootstrap(MODES[0], "s-d1-pshdrwhole")
    cmd = "cat AGENTS.md"
    t1 = r_issue(state_r, ns_r, "whole", "responses", (CAUSAL_ROOT_FACT,), cmd)
    assert t1.outcome.value == "accepted"
    t2 = r_observe(t1.state, ns_r, (read_request("responses", "whole", V2, cmd),))
    assert t2.outcome.value == "accepted"
    state_r2 = t2.state
    r_r = derive_root_region_graph(state_r2, ns_r)
    assert r_r.outcome is RootRegionGraphOutcome.READY
    g_r = CurrentAdmissionBounds()
    parent_r = _s_parent_from_assembly(ns_r, state_r2, r_r, g_r)[-1]
    fixtures.append(("read", ns_r, state_r2, r_r, g_r, parent_r))
    ns_g, state_g = _mixed_region_state(MODES[0], "responses", "s-d1-pshdrregion")
    r_g = derive_root_region_graph(state_g, ns_g)
    assert r_g.outcome is RootRegionGraphOutcome.READY
    g_g = CurrentAdmissionBounds()
    parent_g = _s_parent_from_assembly(ns_g, state_g, r_g, g_g)[-1]
    fixtures.append(("read_region", ns_g, state_g, r_g, g_g, parent_g))
    hits = 0
    real_target = _r_result_closed

    def _counting_target(result: RootRegionGraphResult) -> None:
        nonlocal hits
        hits += 1
        real_target(result)

    monkeypatch = pytest.MonkeyPatch()
    try:
        monkeypatch.setattr(rram, "_r_result_closed", _counting_target)
        for kind, ns, state, r, g, parent in fixtures:
            kwargs: dict[str, Any] = {
                name: getattr(parent, name) for name in type(parent).model_fields
            }
            # Positive FIRST per variant: the genuine selected-
            # source fixture accepts with the real shared target
            # actually reached once.
            hits = 0
            rebuilt = RootRegionAdmission(**kwargs)
            assert rebuilt.state is state and rebuilt.r_result is r
            assert rebuilt.ns == ns and rebuilt.g_bounds == g
            assert hits == 1
            q = r.q_result
            assert q is not None
            p = q.p_selection
            assert p is not None
            resolved = r.resolved_source
            assert resolved is not None
            selected = resolved.fact
            index = next(i for i, fact in enumerate(p.witness_facts) if fact is selected)

            def _bad_facts(
                fact: Any,
                _p: Any = p,
                _index: int = index,
                _q: Any = q,
                _r: Any = r,
            ) -> RootRegionGraphResult:
                facts = list(_p.witness_facts)
                facts[_index] = fact
                bad_p = _p.model_copy(update={"witness_facts": tuple(facts)})
                bad_q = _q.model_copy(update={"p_selection": bad_p})
                bad_r: RootRegionGraphResult = _r.model_copy(update={"q_result": bad_q})
                return bad_r

            def _bad_p(
                new_p: Any,
                _q: Any = q,
                _r: Any = r,
            ) -> RootRegionGraphResult:
                bad_q = _q.model_copy(update={"p_selection": new_p})
                bad_r: RootRegionGraphResult = _r.model_copy(update={"q_result": bad_q})
                return bad_r

            def _neg(
                forged: RootRegionGraphResult,
                match: str,
                _kwargs: dict[str, Any] = kwargs,
            ) -> None:
                nonlocal hits
                hits = 0
                with pytest.raises(ValidationError, match=match):
                    RootRegionAdmission(**{**_kwargs, "r_result": forged})
                assert hits == 0

            prov = selected.provenance
            if kind == "envelope":
                workspace_path_error = (
                    "the fact provenance workspace must be a closed absolute path"
                )
                for bad_workspace, match in (
                    ("AGENTS.md", workspace_path_error),
                    ("/" + "a" * 1024, workspace_path_error),
                    (
                        "/a\x01b",
                        "the fact provenance workspace must not contain control characters",
                    ),
                    (123, "the fact provenance workspace must be closed text"),
                    ("/a\ud800b", "the fact provenance workspace must be valid UTF-8"),
                ):
                    _neg(
                        _bad_facts(
                            selected.model_copy(
                                update={
                                    "provenance": prov.model_copy(
                                        update={"workspace": bad_workspace}
                                    )
                                }
                            )
                        ),
                        match,
                    )
                _neg(
                    _bad_facts(
                        selected.model_copy(
                            update={"provenance": prov.model_copy(update={"root_digest": "0" * 63})}
                        )
                    ),
                    "root_digest must be a 64-hex digest",
                )
                _neg(
                    _bad_facts(
                        selected.model_copy(
                            update={
                                "provenance": prov.model_copy(update={"source_byte_length": True})
                            }
                        )
                    ),
                    "the fact provenance length must be a closed non-bool count",
                )
                # The P selection header law (variant
                # independent; exercised once on the envelope
                # fixture).
                _neg(
                    _bad_p(p.model_copy(update={"outcome": "ok"})),
                    "the P selection outcome must be the actual closed outcome",
                )
                _neg(
                    _bad_p(p.model_copy(update={"lineage_key": "0" * 63})),
                    "lineage_key must be a 64-hex digest",
                )
                _neg(
                    _bad_p(p.model_copy(update={"lineage_key": None})),
                    "the P selection lineage key must be closed 64-hex text",
                )
                for bad_revision in (True, -1, MAX_REVISION + 1):
                    _neg(
                        _bad_p(p.model_copy(update={"revision": bad_revision})),
                        "the P selection revision must be a closed non-bool integer",
                    )
                _neg(
                    _bad_p(p.model_copy(update={"selected_source_digest": "0" * 63})),
                    "selected_source_digest must be a 64-hex digest",
                )
                _neg(
                    _bad_p(p.model_copy(update={"witness_facts": list(p.witness_facts)})),
                    "the P selection witness facts must carry the closed tuple container",
                )
                _neg(
                    _bad_p(p.model_copy(update={"limitations": list(p.limitations)})),
                    "the P selection limitations must carry the closed tuple container",
                )
                _neg(
                    _bad_p(p.model_copy(update={"limitations": ("root_source_unproven",)})),
                    "the P selection limitations must be closed enum values",
                )
                _neg(
                    _bad_p(
                        p.model_copy(
                            update={
                                "limitations": (
                                    RootLineageLimitation.ROOT_SOURCE_UNPROVEN,
                                    RootLineageLimitation.ENVELOPE_UNPROVEN,
                                )
                            }
                        )
                    ),
                    "the P selection limitations must be sorted and deduplicated",
                )
                _neg(
                    _bad_p(
                        p.model_copy(
                            update={
                                "limitations": (
                                    RootLineageLimitation.ROOT_SOURCE_UNPROVEN,
                                    RootLineageLimitation.ROOT_SOURCE_UNPROVEN,
                                )
                            }
                        )
                    ),
                    "the P selection limitations must be sorted and deduplicated",
                )
                _neg(
                    _bad_p(
                        p.model_copy(
                            update={
                                "limitations": tuple(
                                    [
                                        RootLineageLimitation.ROOT_SOURCE_UNPROVEN,
                                        RootLineageLimitation.ENVELOPE_UNPROVEN,
                                    ]
                                    * 33
                                )
                            }
                        )
                    ),
                    "the P selection limitations exceed the hard ceiling",
                )
            elif kind == "read":
                identity_error = "the fact provenance identity must be closed text"
                bounded_error = "the fact provenance call id must be bounded non-space metadata"
                for bad_call, match in (
                    (123, identity_error),
                    ("", bounded_error),
                    ("c" * 257, bounded_error),
                    ("a b", bounded_error),
                    ("a\ud800", "the fact provenance call id must be valid UTF-8"),
                ):
                    _neg(
                        _bad_facts(
                            selected.model_copy(
                                update={"provenance": prov.model_copy(update={"call_id": bad_call})}
                            )
                        ),
                        match,
                    )
                _neg(
                    _bad_facts(
                        selected.model_copy(
                            update={"provenance": prov.model_copy(update={"endpoint": 123})}
                        )
                    ),
                    identity_error,
                )
                _neg(
                    _bad_facts(
                        selected.model_copy(
                            update={
                                "provenance": prov.model_copy(update={"endpoint": "embeddings"})
                            }
                        )
                    ),
                    "the fact provenance endpoint must be an explicit validated endpoint",
                )
                _neg(
                    _bad_facts(
                        selected.model_copy(
                            update={
                                "provenance": prov.model_copy(update={"occurrence_id": "0" * 63})
                            }
                        )
                    ),
                    "occurrence_id must be a 64-hex digest",
                )
                _neg(
                    _bad_facts(
                        selected.model_copy(
                            update={"provenance": prov.model_copy(update={"read_digest": "0" * 63})}
                        )
                    ),
                    "read_digest must be a 64-hex digest",
                )
                for bad_length in (True, -1):
                    _neg(
                        _bad_facts(
                            selected.model_copy(
                                update={
                                    "provenance": prov.model_copy(
                                        update={"read_byte_length": bad_length}
                                    )
                                }
                            )
                        ),
                        "the fact provenance length must be a closed non-bool count",
                    )
            else:
                identity_error = "the fact provenance identity must be closed text"
                bounded_error = "the fact provenance call id must be bounded non-space metadata"
                for bad_call, match in (
                    (123, identity_error),
                    ("", bounded_error),
                    ("c" * 257, bounded_error),
                    ("a b", bounded_error),
                    ("a\ud800", "the fact provenance call id must be valid UTF-8"),
                ):
                    _neg(
                        _bad_facts(
                            selected.model_copy(
                                update={"provenance": prov.model_copy(update={"call_id": bad_call})}
                            )
                        ),
                        match,
                    )
                _neg(
                    _bad_facts(
                        selected.model_copy(
                            update={"provenance": prov.model_copy(update={"endpoint": 123})}
                        )
                    ),
                    identity_error,
                )
                _neg(
                    _bad_facts(
                        selected.model_copy(
                            update={
                                "provenance": prov.model_copy(update={"endpoint": "embeddings"})
                            }
                        )
                    ),
                    "the fact provenance endpoint must be an explicit validated endpoint",
                )
                _neg(
                    _bad_facts(
                        selected.model_copy(
                            update={
                                "provenance": prov.model_copy(update={"occurrence_id": "0" * 63})
                            }
                        )
                    ),
                    "occurrence_id must be a 64-hex digest",
                )
                _neg(
                    _bad_facts(
                        selected.model_copy(
                            update={
                                "provenance": prov.model_copy(
                                    update={"whole_proof_digest": "0" * 63}
                                )
                            }
                        )
                    ),
                    "whole_proof_digest must be a 64-hex digest",
                )
                _neg(
                    _bad_facts(
                        selected.model_copy(
                            update={
                                "provenance": prov.model_copy(
                                    update={"root_member_digest": "0" * 63}
                                )
                            }
                        )
                    ),
                    "root_member_digest must be a 64-hex digest",
                )
                for bad_length in (True, -1):
                    _neg(
                        _bad_facts(
                            selected.model_copy(
                                update={
                                    "provenance": prov.model_copy(
                                        update={"whole_proof_byte_length": bad_length}
                                    )
                                }
                            )
                        ),
                        "the fact provenance length must be a closed non-bool count",
                    )
                    _neg(
                        _bad_facts(
                            selected.model_copy(
                                update={
                                    "provenance": prov.model_copy(
                                        update={"root_member_byte_length": bad_length}
                                    )
                                }
                            )
                        ),
                        "the fact provenance length must be a closed non-bool count",
                    )
                for bad_index in (True, -1):
                    _neg(
                        _bad_facts(
                            selected.model_copy(
                                update={
                                    "provenance": prov.model_copy(
                                        update={"root_segment_index": bad_index}
                                    )
                                }
                            )
                        ),
                        "the fact provenance index must be a closed non-bool count",
                    )
                    _neg(
                        _bad_facts(
                            selected.model_copy(
                                update={
                                    "provenance": prov.model_copy(
                                        update={"root_member_position": bad_index}
                                    )
                                }
                            )
                        ),
                        "the fact provenance index must be a closed non-bool count",
                    )
    finally:
        monkeypatch.undo()


class _CountingIterator:
    """A finite raw iterable that COUNTS every ``__next__`` visit so
    the before-parse class gate can be proven to refuse it before
    any element traversal (zero-visit evidence, not a tuple
    ``__iter__`` hook)."""

    def __init__(self, values: tuple[Any, ...]) -> None:
        self._values = values
        self._index = 0
        self.nexts = 0

    def __iter__(self) -> _CountingIterator:
        return self

    def __next__(self) -> Any:
        self.nexts += 1
        if self._index >= len(self._values):
            raise StopIteration
        value = self._values[self._index]
        self._index += 1
        return value


def test_d1_raw_witness_container_and_count_before_parsing() -> None:
    """D1: the raw WITNESS container/count gates close BEFORE the
    witness elements can be parsed, at the direct entry
    constructor and the SHARED leaf law (the admission parent
    re-runs that leaf law per entry on the carried path).

    Positive FIRST on the genuine LEAN offset component (a
    standalone A read plus a mixed B|A read of the same A bytes at
    a different original offset; the FILE A entry retains the FIRST
    proof and BOTH original witnesses): an explicit TUPLE witness
    vector and a raw LIST normalization are both accepted with the
    same witness instances retained by identity; then an at-cap
    positive under a genuine STRICTER actual admission record
    (max_reverse_associations=2, coherently rekeyed content key --
    the bound sets are key material) accepts exactly two
    witnesses.

    The witness COUNT is the ACTUAL carried G association-attempt
    domain (a safe upper bound of the real G association law;
    never a new fixed cap, never the history occurrence
    population -- one genuine occurrence may carry multiple
    same-key plan witnesses): a counting iterator is refused by
    the closed list/tuple class gate with ZERO element visits at
    BOTH the FILE and the ROOT row; a nonempty ROOT witness vector
    is the fixed "evidenced, never a fabricated read witness"
    error; under the CLOSED FILE proof context a bypassed partial
    witness is still the fixed closed-fields error (the count gate
    at one witness does not mask the field closure); an over-cap
    FILE witness vector under the stricter
    record is ONE fixed private error BEFORE the dedup/element
    parse (the duplicate third witness would otherwise reach the
    canonical dedup law later).  The carried model_construct
    over-cap entry is refused by the SHARED leaf law's count gate
    (the parent's direct per-entry path).  Direct-entry
    constructor and shared-leaf-law paths only; no whole-operation
    claim, no new cap, no old public law change."""
    ns, _state, _r, _g, root_entry, files, _parent = _offset_component()
    entry = files[0]
    w1, w2 = entry.witnesses
    record = entry.key_record
    file_fields = dict(
        entry_class=entry.entry_class,
        content_key=entry.content_key,
        key_record=entry.key_record,
        width=entry.width,
        member_classes=entry.member_classes,
        root_digest=entry.root_digest,
        proof=entry.proof,
        admitted_segments=entry.admitted_segments,
    )
    root_fields = dict(
        entry_class=root_entry.entry_class,
        content_key=root_entry.content_key,
        key_record=root_entry.key_record,
        width=root_entry.width,
        member_classes=root_entry.member_classes,
        root_digest=root_entry.root_digest,
        root_source=root_entry.root_source,
    )
    # --- positives FIRST ---
    rebuilt = RootRegionAdmissionEntry(**file_fields, witnesses=tuple(entry.witnesses))
    assert rebuilt.witnesses[0] is w1 and rebuilt.witnesses[1] is w2
    raw_witnesses: Any = list(entry.witnesses)
    rebuilt_list = RootRegionAdmissionEntry(**file_fields, witnesses=raw_witnesses)
    assert isinstance(rebuilt_list.witnesses, tuple)
    assert rebuilt_list.witnesses[0] is w1 and rebuilt_list.witnesses[1] is w2
    # The genuine STRICTER actual admission record: the ACTUAL D
    # factory with one changed bound (the identity fields and the
    # other three bound sets are unchanged), and the FILE record's
    # content key coherently rekeyed under it (the bound sets are
    # key material; the recipe is unchanged).
    strict_admission = make_bundle_admission_namespace(
        IDENTITY,
        model_identity="synthetic-history-model",
        config_fingerprint=FINGERPRINT,
        workspace=WORKSPACE,
        mode=ns.mode,
        bounds=BundleAdmissionBounds(max_reverse_associations=2),
    )
    strict_record = BundleKeyRecord(
        **{
            name: getattr(record, name)
            for name in type(record).model_fields
            if name not in ("admission_bounds", "content_key")
        },
        admission_bounds=strict_admission.bounds,
        content_key=_sha256_hex(
            _key_canonical(
                strict_admission,
                record.root_digest,
                record.authority_class,
                record.member_occurrences,
                record.member_classes,
                record.aggregate_source_digest,
                record.ownership_groups,
            )
        ),
    )
    assert strict_record.content_key != record.content_key
    strict_entry = RootRegionAdmissionEntry(
        **{
            name: file_fields[name]
            for name in ("entry_class", "width", "member_classes", "root_digest")
        },
        content_key=strict_record.content_key,
        key_record=strict_record,
        proof=file_fields["proof"],
        admitted_segments=file_fields["admitted_segments"],
        witnesses=(w1, w2),
    )
    assert strict_entry.witnesses == entry.witnesses  # at-cap: 2 == 2
    # --- negative: the raw container class gate, zero visits ---
    file_iter = _CountingIterator((w1, w2))
    with pytest.raises(
        ValidationError,
        match="the entry witnesses must carry a closed list or tuple before parsing",
    ) as excinfo:
        RootRegionAdmissionEntry(**file_fields, witnesses=file_iter)  # type: ignore[arg-type]
    assert file_iter.nexts == 0
    assert len(excinfo.value.errors()) == 1
    root_iter = _CountingIterator((w1,))
    with pytest.raises(
        ValidationError,
        match="the entry witnesses must carry a closed list or tuple before parsing",
    ) as excinfo:
        RootRegionAdmissionEntry(**root_fields, witnesses=root_iter)  # type: ignore[arg-type]
    assert root_iter.nexts == 0
    assert len(excinfo.value.errors()) == 1
    # --- negative: a nonempty ROOT witness vector is fabricated ---
    with pytest.raises(
        ValidationError, match="evidenced, never a fabricated read witness"
    ) as excinfo:
        RootRegionAdmissionEntry(**root_fields, witnesses=[w1])  # type: ignore[arg-type]
    assert len(excinfo.value.errors()) == 1
    # --- negative: under the CLOSED FILE proof context the witness
    # FIELD closure remains (the count gate at one witness does not
    # mask it): a bypassed partial witness is the fixed closed-
    # fields error, never an attribute error in the sorter.
    partial_witness = CurrentAdmissionWitness.model_construct()
    with pytest.raises(
        ValidationError, match="the retained witness must carry its closed fields"
    ) as excinfo:
        RootRegionAdmissionEntry(**file_fields, witnesses=(partial_witness,))
    assert len(excinfo.value.errors()) == 1
    # --- negative: over the ACTUAL stricter cap, before dedup/parse ---
    with pytest.raises(
        ValidationError,
        match="the entry witnesses exceed the actual carried association domain before parsing",
    ) as excinfo:
        RootRegionAdmissionEntry(
            **{
                name: file_fields[name]
                for name in ("entry_class", "width", "member_classes", "root_digest")
            },
            content_key=strict_record.content_key,
            key_record=strict_record,
            proof=file_fields["proof"],
            admitted_segments=file_fields["admitted_segments"],
            witnesses=(w1, w2, w1),
        )
    assert len(excinfo.value.errors()) == 1
    # --- negative: the SHARED leaf law (the parent's carried path)
    over_entry = type(entry).model_construct(
        **{
            name: getattr(entry, name)
            for name in type(entry).model_fields
            if name not in ("key_record", "content_key", "witnesses")
        },
        key_record=strict_record,
        content_key=strict_record.content_key,
        witnesses=(w1, w2, w1),
    )
    with pytest.raises(
        ValueError,
        match="the entry witnesses exceed the actual carried association domain before any walk",
    ):
        _s_entry_leaf_closed(over_entry)


class _WitnessStageSpy(RootRegionAdmissionEntry):
    """A REAL model subclass (the inherited original validators are
    unchanged; the class is never replaced by a function) that
    counts the BEFORE-field stage entries for the witnesses field
    with a pass-through before-field validator: stage entry is
    direct evidence that Pydantic reached the field parsing, not a
    per-element parser/allocation counter."""

    stage: ClassVar[int] = 0

    @field_validator("witnesses", mode="before")
    @classmethod
    def _spy_before_witness(cls, value: Any) -> Any:
        _WitnessStageSpy.stage += 1
        return value


def test_d1_raw_witness_variant_context_before_field_stage() -> None:
    """D1: the raw WITNESS variant-context gates close BEFORE
    Pydantic's field stage (a REAL model subclass spy with a
    pass-through before-field counter proves stage entry, the
    inherited original validators unchanged): positive FIRST --
    the genuine FILE and ROOT entries re-built through the spy
    reach exactly ONE before-field stage entry each (legitimate
    parsing of the closed vectors; the ROOT positive also proves
    the legal omitted/default empty witness tuple stays legal).
    Then negative-only raw updates, each with the EARLIEST fixed
    private refusal and ZERO before-field stage entries: an
    EXPLICIT ``witnesses=None`` on the FILE and the ROOT row
    (a malformed provided None, distinct from the legal omission
    -- never a per-field tuple_type error after stage entry), an
    explicit ``admitted_segments=None`` on the FILE row (the same
    omission/explicit-None law on the other defaulted tuple
    field), and a ROOT row supplied a GENUINE spliced FILE proof
    plus one FILE witness (the invalid ROOT proof context never
    authorizes the FILE witness domain; the closed ROOT count is
    zero, from the raw entry-class variant context, never solely
    from the provided proof isinstance).  The finite unknown-raw
    iterator refusals (fixed container error, zero stage, zero
    next calls) stay closed.  The shared leaf law carries the
    SAME variant-context closure at the carrying boundary (a
    bypassed spliced-proof ROOT row refuses the evidenced
    channel there, before any canonical rekey).  Direct-entry
    preparse boundary only; no full consumer/runtime claim, no
    new cap, no old public law change."""
    ns, state, r, g, root_entry, files, _parent = _offset_component()
    entry = next(e for e in files if e.proof is not None)
    w1 = entry.witnesses[0]
    file_fields = {name: getattr(entry, name) for name in type(entry).model_fields}
    root_fields = {name: getattr(root_entry, name) for name in type(root_entry).model_fields}
    # --- positives FIRST (real-class spy, inherited validators) ---
    _WitnessStageSpy.stage = 0
    file_spy = _WitnessStageSpy(**file_fields)
    assert _WitnessStageSpy.stage == 1
    assert file_spy.witnesses == entry.witnesses
    _WitnessStageSpy.stage = 0
    root_spy = _WitnessStageSpy(**root_fields)
    assert _WitnessStageSpy.stage == 1
    assert root_spy.witnesses == ()
    # --- negative: EXPLICIT None on the defaulted fields ---
    for bad_fields in (file_fields, root_fields):
        _WitnessStageSpy.stage = 0
        with pytest.raises(
            ValidationError,
            match="the entry witnesses must carry a closed list or tuple before parsing",
        ) as excinfo:
            _WitnessStageSpy(**{**bad_fields, "witnesses": None})
        assert _WitnessStageSpy.stage == 0
        assert len(excinfo.value.errors()) == 1
    _WitnessStageSpy.stage = 0
    with pytest.raises(
        ValidationError,
        match="admitted segments must carry a closed list or tuple before parsing",
    ) as excinfo:
        _WitnessStageSpy(**{**file_fields, "admitted_segments": None})
    assert _WitnessStageSpy.stage == 0
    assert len(excinfo.value.errors()) == 1
    # --- negative: ROOT row + genuine spliced FILE proof + witness
    _WitnessStageSpy.stage = 0
    with pytest.raises(
        ValidationError, match="evidenced, never a fabricated read witness"
    ) as excinfo:
        _WitnessStageSpy(**{**root_fields, "proof": entry.proof, "witnesses": (w1,)})
    assert _WitnessStageSpy.stage == 0
    assert len(excinfo.value.errors()) == 1
    # --- negative (regression): finite unknown raw iterables, zero
    # stage entry and zero element retrieval.
    file_unknown = _CountingIterator(entry.witnesses)
    _WitnessStageSpy.stage = 0
    with pytest.raises(
        ValidationError,
        match="the entry witnesses must carry a closed list or tuple before parsing",
    ):
        _WitnessStageSpy(**{**file_fields, "witnesses": file_unknown})
    assert _WitnessStageSpy.stage == 0
    assert file_unknown.nexts == 0
    root_unknown = _CountingIterator(())
    _WitnessStageSpy.stage = 0
    with pytest.raises(
        ValidationError,
        match="the entry witnesses must carry a closed list or tuple before parsing",
    ):
        _WitnessStageSpy(**{**root_fields, "witnesses": root_unknown})
    assert _WitnessStageSpy.stage == 0
    assert root_unknown.nexts == 0
    # --- shared leaf law: the SAME variant-context closure at the
    # carrying boundary (a bypassed spliced-proof ROOT row refuses
    # the evidenced channel before any canonical rekey).
    spliced = type(root_entry).model_construct(
        **{
            name: getattr(root_entry, name)
            for name in type(root_entry).model_fields
            if name not in ("proof", "witnesses")
        },
        proof=entry.proof,
        witnesses=(w1,),
    )
    with pytest.raises(ValueError, match="evidenced, never a fabricated read witness"):
        _s_entry_leaf_closed(spliced)


class _CountingIndexTuple(tuple[int, ...]):
    """A finite tuple that counts every ELEMENT visit (each
    yielded index) so the O(1) population gate can be proven to
    refuse BEFORE the first index element is traversed (the len()
    read is O(1) and never counted)."""

    visits: int

    def __new__(cls, values: tuple[int, ...]) -> _CountingIndexTuple:
        obj = super().__new__(cls, values)
        obj.visits = 0
        return obj

    def __iter__(self) -> Any:
        for value in super().__iter__():
            self.visits += 1
            yield value


def test_d1_witness_segment_index_population_closed_before_first_walk() -> None:
    """D1: the witness segment-index POPULATION closes O(1) under
    the ACTUAL carried original B segment cap BEFORE the first
    index element is traversed, at the entry constructor and the
    shared leaf (the sorter both re-run), while the EXACT
    original-owner segment domain remains the admission parent's
    M04 owner join (never the FIRST retained proof's length for
    all witnesses, never a new fixed cap): positive FIRST -- the
    genuine public P/R/G fresh S parent is accepted (every
    genuine witness index sits under the actual B cap and in its
    own actual owner's segment domain, including the different-
    original-offset owner), and a count EXACTLY at the actual
    carried cap is legal at the sorter tier.  Then negative-only
    nested witness copies (the probe's finite repeated-zero
    tuple, actual max_segments + 1 elements) refuse ONE fixed
    private error at BOTH the entry constructor and the shared
    carried leaf with ZERO index element visits (the counting
    tuple is never traversed); a count-VALID over-owner-domain
    tuple (0, 1 under the one-segment owner) passes the sorter
    tier and is refused by the ACTUAL owner-domain gate --
    helper-direct with zero region-walk events and the actual
    parent M04 join -- pinning the two-tier law.  The genuine
    different-offset / multi-plan positives stay legal (the
    genuine parent is re-accepted); no public G change, no old
    public law change."""
    ns, state, r, g, _root_entry, files, parent = _offset_component()
    entry = next(e for e in files if e.proof is not None)
    parent_kwargs = {name: getattr(parent, name) for name in type(parent).model_fields}
    file_fields = {name: getattr(entry, name) for name in type(entry).model_fields}
    record = entry.key_record
    max_segments = record.proof_bounds.max_segments
    occurrences = state.d_state.occurrences
    owners = {
        w.occurrence_id: next(o for o in occurrences if o.occurrence_id == w.occurrence_id)
        for w in entry.witnesses
    }
    # --- positive FIRST ---
    for w in entry.witnesses:
        owner = owners[w.occurrence_id]
        assert len(w.segment_indices) <= max_segments
        assert all(0 <= i < len(owner.proof.segments) for i in w.segment_indices)
    rebuilt = RootRegionAdmission(**parent_kwargs)
    assert rebuilt.state is state and rebuilt.r_result is r
    # At the sorter tier the ACTUAL carried cap is the domain: a
    # count exactly at the cap is legal here (the exact owner
    # domain is the LATER parent-tier gate, not this one).
    at_cap = entry.witnesses[0].model_copy(update={"segment_indices": tuple(range(max_segments))})
    _s_witnesses_sorted_deduplicated((at_cap,), max_segments)
    # --- negative: population over the ACTUAL carried B cap, zero
    # element visits, at BOTH boundaries (the probe's finite
    # repeated-zero tuple, max_segments + 1 elements) ---
    indices_c = _CountingIndexTuple((0,) * (max_segments + 1))
    bad_w_c = entry.witnesses[0].model_copy(update={"segment_indices": indices_c})
    with pytest.raises(
        ValidationError,
        match="the witness segment indices exceed the actual carried proof cap",
    ) as excinfo:
        RootRegionAdmissionEntry(**{**file_fields, "witnesses": (bad_w_c,)})
    assert len(excinfo.value.errors()) == 1
    assert indices_c.visits == 0
    indices_l = _CountingIndexTuple((0,) * (max_segments + 1))
    bad_w_l = entry.witnesses[0].model_copy(update={"segment_indices": indices_l})
    bypassed = entry.model_copy(update={"witnesses": (bad_w_l,)})
    with pytest.raises(
        ValueError,
        match="the witness segment indices exceed the actual carried proof cap",
    ):
        _s_entry_leaf_closed(bypassed)
    assert indices_l.visits == 0
    # --- negative: count-VALID over the EXACT owner domain (the
    # two-tier law: the sorter tier passes, the ACTUAL owner
    # domain refuses at the parent M04 join) ---
    lone_w = next(w for w in entry.witnesses if len(owners[w.occurrence_id].proof.segments) == 1)
    lone_o = owners[lone_w.occurrence_id]
    over_owner = lone_w.model_copy(update={"segment_indices": (0, 1)})
    assert len(over_owner.segment_indices) <= max_segments
    lines, first = inspect.getsourcelines(rram._s_witness_region_compatible)
    region_lines = [
        first + i
        for i, line in enumerate(lines)
        if "for position, segment in enumerate(segments):" in line
    ]
    assert len(region_lines) == 1
    region_line = region_lines[0]
    region_hits = 0

    def _region_trace(frame: Any, event: str, arg: Any) -> Any:
        nonlocal region_hits
        if (
            event == "line"
            and frame.f_code is rram._s_witness_region_compatible.__code__
            and frame.f_lineno == region_line
        ):
            region_hits += 1
        return _region_trace

    saved_trace = sys.gettrace()
    try:
        sys.settrace(_region_trace)
        region_hits = 0
        with pytest.raises(
            ValueError,
            match="the witness segment indices exceed the original proof segment domain",
        ):
            rram._s_witness_region_compatible(over_owner, lone_o.proof, record, ns.proof_bounds)
        assert region_hits == 0
        # The ACTUAL parent M04 join enforces the same exact owner
        # domain (the sorter tier does not over-close it with the
        # FIRST retained proof's length).
        spliced_witnesses = tuple(over_owner if w is lone_w else w for w in entry.witnesses)
        region_hits = 0
        with pytest.raises(
            ValidationError,
            match="the witness segment indices exceed the original proof segment domain",
        ) as excinfo:
            RootRegionAdmission(
                **{
                    **parent_kwargs,
                    "entries": (entry.model_copy(update={"witnesses": spliced_witnesses}),),
                }
            )
        assert len(excinfo.value.errors()) == 1
        assert region_hits == 0
    finally:
        sys.settrace(saved_trace)


def test_d1_witness_intrinsic_coordinate_closure_at_s_boundaries() -> None:
    """D1: the INTRINSIC closed witness coordinate law is re-run
    at the S boundaries (entry constructor and shared leaf),
    independently of the owner: the ACTUAL concrete witness class
    (the shared leaf never trusts a matching-namespace wrong
    class by shape alone), the original nonempty MINLENGTH, and
    the distinct-and-increasing coordinate law (a duplicate or
    descending index tuple is a fixed private error before the
    canonical sort reads the coordinates).  Positive FIRST -- the
    genuine public P/R/G fresh S parent is accepted (the genuine
    witnesses are concrete-class, nonempty, distinct and
    increasing) and the direct shared sorter re-passes the
    genuine tuple.  Then negative-only nested witness copies,
    each refused with ONE fixed private error at BOTH the entry
    constructor and the shared carried leaf: a wrong concrete
    class (the constructor's ACTUAL element validation refuses
    the non-instance before the field validator; the shared leaf
    refuses the fixed class channel), an empty index tuple, a
    duplicate index pair, and a descending index pair.  The
    EXACT owner membership (index < len(owner.segments)) stays
    the parent M04 join (pinned in the population test); no new
    cap, no public G change, no old public law change."""
    ns, state, r, g, _root_entry, files, parent = _offset_component()
    entry = next(e for e in files if e.proof is not None)
    parent_kwargs = {name: getattr(parent, name) for name in type(parent).model_fields}
    file_fields = {name: getattr(entry, name) for name in type(entry).model_fields}
    record = entry.key_record
    max_segments = record.proof_bounds.max_segments
    w1 = entry.witnesses[0]
    # --- positive FIRST ---
    rebuilt = RootRegionAdmission(**parent_kwargs)
    assert rebuilt.state is state and rebuilt.r_result is r
    _s_witnesses_sorted_deduplicated(entry.witnesses, max_segments)
    # --- negatives, each at BOTH boundaries ---
    cases = (
        (
            SimpleNamespace(
                occurrence_id=w1.occurrence_id,
                request_index=w1.request_index,
                call_position=w1.call_position,
                result_position=w1.result_position,
                segment_indices=w1.segment_indices,
            ),
            "the file witness must be the actual concrete witness record",
            "an instance of",
        ),
        (
            w1.model_copy(update={"segment_indices": ()}),
            "the file witness must carry its original segment coordinates",
            "the file witness must carry its original segment coordinates",
        ),
        (
            w1.model_copy(update={"segment_indices": (0, 0)}),
            "the witness segment indices must index the original proof",
            "the witness segment indices must index the original proof",
        ),
        (
            w1.model_copy(update={"segment_indices": (1, 0)}),
            "the witness segment indices must index the original proof",
            "the witness segment indices must index the original proof",
        ),
    )
    for bad_w, leaf_pattern, ctor_pattern in cases:
        with pytest.raises(ValidationError, match=ctor_pattern) as excinfo:
            RootRegionAdmissionEntry(**{**file_fields, "witnesses": (bad_w,)})
        assert len(excinfo.value.errors()) == 1
        bypassed = entry.model_copy(update={"witnesses": (bad_w,)})
        with pytest.raises(ValueError, match=leaf_pattern):
            _s_entry_leaf_closed(bypassed)


# --- D2 batch 2: region component precharge (whole-source fast
# path) plus the closed admission shape law --------------------------


class _D2Meter:
    """The bounded caller-side WORK meter for the D2 region
    component precharge: a finite nonnegative budget, closed
    nonnegative integer charges only, and immediate exhaustion
    BEFORE the caller's actual targets may run (no unlimited or
    default meter exists in the models; the ordinary constructors
    never receive one)."""

    def __init__(self, limit: int) -> None:
        if isinstance(limit, bool) or not isinstance(limit, int) or limit < 0:
            raise ValueError("the work meter must carry a closed nonnegative budget")
        self.remaining = limit
        self.reserves: list[int] = []

    def reserve(self, units: int) -> None:
        if isinstance(units, bool) or not isinstance(units, int) or units < 0:
            raise ValueError("the work meter must carry closed nonnegative integers")
        if units > self.remaining:
            raise ValueError("the work meter budget is exhausted before the crossing target")
        self.remaining -= units
        self.reserves.append(units)


class _CountingTuple(tuple[Any]):
    """A closed tuple counting ACTUAL element yields AND ACTUAL
    index gets: the helper's metadata element fences, set-build,
    offset-advance and measurement-outer passes consume the
    yields, while the closed admission shape law's index
    comparisons consume the gets, so the counted totals prove the
    actual traversal domain an empty reserve list alone cannot."""

    visits: ClassVar[int] = 0
    index_visits: ClassVar[int] = 0

    def __iter__(self) -> Any:
        for item in super().__iter__():
            _CountingTuple.visits += 1
            yield item

    @overload
    def __getitem__(self, index: SupportsIndex) -> Any: ...
    @overload
    def __getitem__(self, index: slice) -> tuple[Any, ...]: ...
    def __getitem__(self, index: SupportsIndex | slice) -> Any:
        _CountingTuple.index_visits += 1
        return super().__getitem__(index)


def test_d2_region_precharge_reservation_before_crossing_target() -> None:
    """D2 batch 2: the SEPARATE bounded-charger region component
    precharge (``root-region-admission-precharge/v1``) with the
    genuine WHOLE-SOURCE FAST PATH: the ACTUAL guarded caller
    sequences (the region precharge, then the real target only
    after it completes) for BOTH closed admission shapes, each
    with its OWN fresh budget.

    Positive FIRST: (a) the whole-bundle shape (the LEAN offset
    fixture's A entry: one 20-character segment, admitted (0,) ==
    the whole bundle) pays [5, 20, 144] (5 = 1 + n + 2m + n shape
    comparison, matching the THREE counted yields plus one fixed
    fence unit; 20 = the ACTUAL character visits of ONE direct
    source pass; 144 = 2*20 + 104 encode/hash) and its leaf target
    makes NO slice/join copies (zero slice lines, one sha pass,
    the digest byte-identical); (b) the single-group shape (the
    genuine two-segment fixture, admitted (1,), 7 characters)
    pays [5, 2, 7, 2, 14, 118] and keeps the slice/join (one
    slice line, one sha pass).  The fresh S parent re-run is a
    separate boundary.  Exact/one-below budgets cross at the real
    targets BEFORE any target attempt, per shape.  Closed
    boundaries keep the legal at-cap source legal (the cap is a
    SIZE domain, never a work meter), refuse forged metadata,
    partial records, the closed admission shape, and the actual
    carried B segment-domain overcounts BEFORE the first
    reservation or element yield.  The genuine strict-cap32
    public P/R/G FILE stays accepted at its actual 32-byte source
    through the new S constructor."""
    # --- Whole-bundle fixture (the genuine LEAN offset A entry).
    ns, state, r, g, root_entry, files, parent = _offset_component()
    entry = next(e for e in files if e.key_record.member_occurrences == ("A.md",))
    proof = entry.proof
    assert proof is not None
    assert proof.source_text == "Synthetic shared A.\n"
    assert len(proof.segments) == 1
    segment = proof.segments[0]
    assert (segment.char_length, segment.byte_length) == (20, 20)
    assert entry.admitted_segments == (0,)
    text = proof.source_text
    segments = proof.segments
    admitted = entry.admitted_segments
    cap = entry.key_record.graph_bounds.max_single_source_bytes
    assert cap == 1_000_000
    proof_bounds = entry.key_record.proof_bounds
    assert type(proof_bounds) is BundleProofBounds
    assert proof_bounds.max_segments == 32
    helper = rram._s_region_precharge_closed
    leaf = rram._s_entry_leaf_closed

    # --- Single-group fixture (the genuine two-segment admitted
    # (1,) FILE entry from the accepted qf fixture law).
    ns3, state3 = qf.q_bootstrap(MODES[0], "s-d2-single-group", "Read `A.md` before work.")
    cmd3 = "cat B.md && echo 'QSEP' && cat A.md"
    state3 = qf.q_observe(
        qf.q_issue(state3, ns3, "mixed", "responses", cmd3, (CAUSAL_ROOT_FACT,)),
        ns3,
        "responses",
        "mixed",
        qf.mixed_body("Unrelated prefix.", qf.MARK, "A body."),
        cmd3,
    )
    _r3, _g3, _root3, files3, _parent3, _diags3 = _s_component_parent(state3, ns3)
    entry3 = next(e for e in files3 if e.proof is not None and len(e.proof.segments) == 2)
    proof3 = entry3.proof
    assert proof3 is not None
    assert entry3.admitted_segments == (1,)
    assert [s.char_length for s in proof3.segments] == [17, 7]
    assert len(proof3.source_text) == 24
    text3 = proof3.source_text
    segments3 = proof3.segments
    admitted3 = entry3.admitted_segments
    cap3 = entry3.key_record.graph_bounds.max_single_source_bytes
    proof_bounds3 = entry3.key_record.proof_bounds
    sg_chars = proof3.segments[1].char_length
    sg_bytes = proof3.segments[1].byte_length
    assert (sg_chars, sg_bytes) == (7, 7)

    # The shared leaf law's ACTUAL slice statement (the fixture
    # keeps exactly one such statement), counted by line.
    lines, first_line = inspect.getsourcelines(leaf)
    selected = [
        first_line + i for i, line in enumerate(lines) if "region.append(proof.source_text[" in line
    ]
    assert len(selected) == 1
    slice_line = selected[0]

    # Counters measured by the guarded runs (reset per run).  The
    # ord profiling is scoped to the ACTUAL helper frame for the
    # component count; the separate total records the leaf law's
    # own metadata/canonical ord work (full D2 cost evidence).
    leaf_entries = 0
    slice_hits = 0
    hash_hits = 0
    helper_ord_visits = 0
    total_ord_visits = 0

    def _ord_profile(frame: Any, event: str, arg: Any) -> Any:
        nonlocal helper_ord_visits, total_ord_visits
        if event == "c_return" and getattr(arg, "__name__", "") == "ord":
            total_ord_visits += 1
            if frame.f_code is helper.__code__:
                helper_ord_visits += 1
        return None

    def _target_trace(frame: Any, event: str, arg: Any) -> Any:
        nonlocal leaf_entries, slice_hits
        if frame.f_code is leaf.__code__:
            if event == "call":
                leaf_entries += 1
            elif event == "line" and frame.f_lineno == slice_line:
                slice_hits += 1
        return _target_trace

    saved_sha = rram._sha256_hex  # type: ignore[attr-defined]

    def _sha_count(*args: Any, **kwargs: Any) -> str:
        nonlocal hash_hits
        hash_hits += 1
        return saved_sha(*args, **kwargs)

    def _guarded_target(
        kind: str,
        limit: int,
        guarded_entry: Any,
        guarded_text: str,
        guarded_segments: Any,
        guarded_admitted: Any,
        guarded_chars: int,
        guarded_bytes: int,
        guarded_cap: int,
        guarded_bounds: Any,
    ) -> tuple[_D2Meter, bool, dict[str, int]]:
        """The ACTUAL guarded caller sequence, identical for every
        budget: the region precharge first, then the real target
        for ``kind`` (the direct leaf law, or the direct
        constructor re-run) ONLY after a completed precharge -- a
        crossing budget therefore stops before any target attempt
        (no conditional bypass).  Each boundary gets its OWN fresh
        region budget: one full charge covers the REGION COMPONENT
        for that boundary, never repeated leaf/constructor/parent
        work."""
        nonlocal leaf_entries, slice_hits, hash_hits, helper_ord_visits, total_ord_visits
        meter = _D2Meter(limit)
        leaf_entries = 0
        slice_hits = 0
        hash_hits = 0
        helper_ord_visits = 0
        total_ord_visits = 0
        _CountingTuple.visits = 0
        _CountingTuple.index_visits = 0
        fields = {name: getattr(guarded_entry, name) for name in type(guarded_entry).model_fields}
        saved_profile = sys.getprofile()
        saved_trace = sys.gettrace()
        rram._sha256_hex = _sha_count  # type: ignore[attr-defined]
        try:
            sys.settrace(_target_trace)
            sys.setprofile(_ord_profile)
            helper(
                meter,
                guarded_text,
                _CountingTuple(guarded_segments),
                _CountingTuple(guarded_admitted),
                guarded_chars,
                guarded_bytes,
                guarded_cap,
                guarded_bounds,
            )
            if kind == "leaf":
                leaf(guarded_entry)
            elif kind == "constructor":
                rebuilt = RootRegionAdmissionEntry(**fields)
                assert rebuilt.proof is guarded_entry.proof
            else:
                raise AssertionError("unknown closed guarded target kind")
            completed = True
        except ValueError:
            completed = False
        finally:
            sys.settrace(saved_trace)
            sys.setprofile(saved_profile)
            rram._sha256_hex = saved_sha  # type: ignore[attr-defined]
        counts = {
            "leaf_entries": leaf_entries,
            "slice_lines": slice_hits,
            "hash_calls": hash_hits,
            "helper_ord_visits": helper_ord_visits,
            "total_ord_visits": total_ord_visits,
            "yield_visits": _CountingTuple.visits,
            "index_visits": _CountingTuple.index_visits,
        }
        return meter, completed, counts

    # --- Positive FIRST: the whole-bundle fast path (both
    # boundaries, their own fresh budgets).
    meter, completed, counts = _guarded_target(
        "leaf", 169, entry, text, segments, admitted, 20, 20, cap, proof_bounds
    )
    assert completed
    assert meter.reserves == [5, 20, 144]
    assert meter.remaining == 0
    # The metadata reservation matches the ACTUAL counted yields:
    # one fixed fence unit, the segment element fence, the n
    # comparison walk of the shape, the index fence and the set.
    assert counts["yield_visits"] == 3
    assert counts["helper_ord_visits"] == 20
    assert counts["index_visits"] == 1
    # The leaf law's own metadata/canonical UTF-8 pass does ACTUAL
    # extra ord work outside the region component charge (observed
    # total 942 on the whole-bundle fixture at first execution;
    # that full D2 cost stays a pending later batch, so the
    # boundary, not a brittle total, is asserted here).
    assert counts["total_ord_visits"] > counts["helper_ord_visits"]
    # The genuine fast path: NO slice/join copies, one sha pass.
    assert counts["leaf_entries"] == 1
    assert counts["slice_lines"] == 0
    assert counts["hash_calls"] == 1

    meter, completed, counts = _guarded_target(
        "constructor", 169, entry, text, segments, admitted, 20, 20, cap, proof_bounds
    )
    assert completed
    assert meter.reserves == [5, 20, 144]
    assert counts["yield_visits"] == 3
    assert counts["helper_ord_visits"] == 20
    assert counts["index_visits"] == 1
    assert counts["total_ord_visits"] > counts["helper_ord_visits"]
    assert counts["leaf_entries"] == 1
    assert counts["slice_lines"] == 0
    assert counts["hash_calls"] == 1

    # --- Positive FIRST: the single-group shape (both boundaries,
    # their own fresh budgets).
    meter, completed, counts = _guarded_target(
        "leaf", 148, entry3, text3, segments3, admitted3, sg_chars, sg_bytes, cap3, proof_bounds3
    )
    assert completed
    assert meter.reserves == [5, 2, 7, 2, 14, 118]
    assert meter.remaining == 0
    # Yielded passes: the segment element fence (2), the index
    # fence (1), the set (1), the offset advance (2), the
    # measurement outer advance (2).
    assert counts["yield_visits"] == 8
    assert counts["helper_ord_visits"] == 7
    assert counts["index_visits"] == 1
    assert counts["total_ord_visits"] > counts["helper_ord_visits"]
    # The single group KEEPS the slice/join (one slice line).
    assert counts["leaf_entries"] == 1
    assert counts["slice_lines"] == 1
    assert counts["hash_calls"] == 1

    meter, completed, counts = _guarded_target(
        "constructor",
        148,
        entry3,
        text3,
        segments3,
        admitted3,
        sg_chars,
        sg_bytes,
        cap3,
        proof_bounds3,
    )
    assert completed
    assert meter.reserves == [5, 2, 7, 2, 14, 118]
    assert counts["yield_visits"] == 8
    assert counts["helper_ord_visits"] == 7
    assert counts["index_visits"] == 1
    assert counts["total_ord_visits"] > counts["helper_ord_visits"]
    assert counts["leaf_entries"] == 1
    assert counts["slice_lines"] == 1
    assert counts["hash_calls"] == 1

    # The fresh S parent re-run is a SEPARATE boundary (its repeated
    # leaf work is never charged by the component budget): identity
    # retained, no error.
    parent_kwargs = {name: getattr(parent, name) for name in type(parent).model_fields}
    rebuilt_parent = RootRegionAdmission(**parent_kwargs)
    assert rebuilt_parent.state is state and rebuilt_parent.r_result is r

    # --- Exact/one-below crossings at the real reservation
    # targets: the guarded sequence stops BEFORE any target
    # attempt (the expected values are the SUCCESSFUL reserves, the
    # ACTUAL counted yields, the ACTUAL completed helper ord
    # visits and the ACTUAL closed-shape index gets).
    CrossingRow = tuple[int, tuple[int, ...], int, int, int]
    whole_crossings: tuple[CrossingRow, ...] = (
        (4, (), 0, 0, 0),
        (5, (5,), 3, 0, 1),
        (25, (5, 20), 3, 20, 1),
        (168, (5, 20), 3, 20, 1),
    )
    for kind in ("leaf", "constructor"):
        for (
            limit,
            expected_reserves,
            expected_yields,
            expected_ord,
            expected_index,
        ) in whole_crossings:
            meter, completed, counts = _guarded_target(
                kind, limit, entry, text, segments, admitted, 20, 20, cap, proof_bounds
            )
            assert not completed
            assert meter.reserves == list(expected_reserves)
            if limit == 168:
                assert meter.remaining == 143
            assert counts["yield_visits"] == expected_yields
            assert counts["helper_ord_visits"] == expected_ord
            assert counts["index_visits"] == expected_index
            # The target never runs, so no ord work beyond the
            # helper's own (no leaf metadata/canonical pass).
            assert counts["total_ord_visits"] == expected_ord
            assert counts["leaf_entries"] == 0
            assert counts["slice_lines"] == 0
            assert counts["hash_calls"] == 0
    group_crossings: tuple[CrossingRow, ...] = (
        (4, (), 0, 0, 0),
        (5, (5,), 4, 0, 1),
        (7, (5, 2), 6, 0, 1),
        (14, (5, 2, 7), 6, 0, 1),
        (16, (5, 2, 7, 2), 8, 7, 1),
        (147, (5, 2, 7, 2, 14), 8, 7, 1),
    )
    for kind in ("leaf", "constructor"):
        for (
            limit,
            expected_reserves,
            expected_yields,
            expected_ord,
            expected_index,
        ) in group_crossings:
            meter, completed, counts = _guarded_target(
                kind,
                limit,
                entry3,
                text3,
                segments3,
                admitted3,
                sg_chars,
                sg_bytes,
                cap3,
                proof_bounds3,
            )
            assert not completed
            assert meter.reserves == list(expected_reserves)
            if limit == 147:
                assert meter.remaining == 117
            assert counts["yield_visits"] == expected_yields
            assert counts["helper_ord_visits"] == expected_ord
            assert counts["index_visits"] == expected_index
            assert counts["total_ord_visits"] == expected_ord
            assert counts["leaf_entries"] == 0
            assert counts["slice_lines"] == 0
            assert counts["hash_calls"] == 0

    # --- Closed boundaries (negative-only coherent copies at the
    # helper level; the targets are not this law's subject).
    # The legal at-cap source stays legal: the cap is a SIZE domain.
    meter = _D2Meter(169)
    assert helper(meter, text, segments, admitted, 20, 20, 20, proof_bounds) == (0, 144)
    assert meter.reserves == [5, 20, 144]

    meter = _D2Meter(10_000_000)
    with pytest.raises(
        ValueError, match="admitted region exceeds the inherited single-source byte cap"
    ):
        helper(meter, text, segments, admitted, 20, 20, 19, proof_bounds)
    assert meter.reserves == [5, 20]

    for forged_bytes in (600_000, 10):
        meter = _D2Meter(10_000_000)
        with pytest.raises(
            ValueError,
            match=("the retained region byte metadata must equal the measured UTF-8 source length"),
        ):
            helper(meter, text, segments, admitted, 20, forged_bytes, cap, proof_bounds)
        assert meter.reserves == [5, 20]

    meter = _D2Meter(10_000_000)
    with pytest.raises(
        ValueError,
        match=("the retained region character metadata must equal the retained source text"),
    ):
        helper(meter, text, segments, admitted, 0, 20, cap, proof_bounds)
    assert meter.reserves == [5]

    surrogate = text[:19] + "\ud800"
    meter = _D2Meter(10_000_000)
    with pytest.raises(ValueError, match="the retained region source must be closed UTF-8 text"):
        helper(meter, surrogate, segments, admitted, 20, 20, cap, proof_bounds)
    assert meter.reserves == [5, 20]

    for bad_scalar in (True, -1):
        meter = _D2Meter(10_000_000)
        with pytest.raises(
            ValueError,
            match="the region precharge meter must carry closed nonnegative integers",
        ):
            helper(meter, text, segments, admitted, bad_scalar, 20, cap, proof_bounds)
        assert meter.reserves == []

    meter = _D2Meter(10_000_000)
    with pytest.raises(
        ValueError,
        match="the region precharge meter must carry closed nonnegative integers",
    ):
        helper(meter, text, segments, admitted, 20, 20, -1, proof_bounds)
    assert meter.reserves == []

    with pytest.raises(
        ValueError,
        match="the region precharge reserver must carry a typed reserve callback",
    ):
        helper(
            None,  # type: ignore[arg-type]
            text,
            segments,
            admitted,
            20,
            20,
            cap,
            proof_bounds,
        )

    partial_segment = BundleSegment.model_construct()
    assert not hasattr(partial_segment, "char_length")
    meter = _D2Meter(10_000_000)
    with pytest.raises(
        ValueError,
        match="the retained region segments must carry closed original lengths",
    ):
        helper(meter, text, (partial_segment,), admitted, 20, 20, cap, proof_bounds)
    assert meter.reserves == [5]

    meter = _D2Meter(10_000_000)
    with pytest.raises(
        ValueError,
        match="the admitted region segments must be the closed original tuple",
    ):
        helper(meter, text, segments, [0], 20, 20, cap, proof_bounds)  # type: ignore[arg-type]
    assert meter.reserves == []

    # Whole-bundle shape: the forged long single segment's declared
    # character count joins the ACTUAL O(1) source length BEFORE
    # any measurement (the earlier closed gate for this shape).
    long_segment = segment.model_copy(update={"char_length": 25, "byte_length": 25})
    meter = _D2Meter(10_000_000)
    with pytest.raises(
        ValueError,
        match=("the retained region character metadata must equal the retained source text"),
    ):
        helper(meter, text, (long_segment,), admitted, 25, 25, cap, proof_bounds)
    assert meter.reserves == [5]

    # Single-group shape: the forged long admitted segment declares
    # the ACTUAL forged length (25), so the character join passes
    # and the precharged measurement-outer reserve completes
    # BEFORE the ACTUAL interval law fires (the interval's end
    # outruns the retained source).
    long_segment3 = segments3[1].model_copy(update={"char_length": 25, "byte_length": 25})
    meter = _D2Meter(10_000_000)
    with pytest.raises(
        ValueError,
        match="the retained region intervals must stay inside the retained source text",
    ):
        helper(meter, text3, (segments3[0], long_segment3), admitted3, 25, 25, cap3, proof_bounds3)
    assert meter.reserves == [5, 2, 25, 2]

    # --- The closed admission SHAPE (the leaf's whole-bundle law
    # re-fenced before any target: neither the whole bundle nor
    # one in-domain group is a fixed private error, never an
    # out-of-domain target call).
    shape_cases = (
        # (segments, admitted, fixture text/cap/bounds, reserves,
        # counted yields, counted index gets)
        (
            segments,
            (0, 0),
            (text, cap, proof_bounds),
            (6,),
            3,
            0,
        ),
        (
            segments3,
            (1, 0),
            (text3, cap3, proof_bounds3),
            (9,),
            4,
            1,
        ),
        (
            segments3,
            (2,),
            (text3, cap3, proof_bounds3),
            (5,),
            3,
            1,
        ),
        (
            segments,
            (5,),
            (text, cap, proof_bounds),
            (5,),
            2,
            2,
        ),
    )
    for (
        bad_segments,
        bad_admitted,
        fixture,
        expected_reserves,
        expected_yields,
        expected_index,
    ) in shape_cases:
        s_text, s_cap, s_bounds = fixture
        _CountingTuple.visits = 0
        _CountingTuple.index_visits = 0
        meter = _D2Meter(10_000_000)
        with pytest.raises(
            ValueError,
            match="the admitted region must be the whole bundle or one proven group",
        ):
            helper(
                meter,
                s_text,
                _CountingTuple(bad_segments),
                _CountingTuple(bad_admitted),
                0,
                0,
                s_cap,
                s_bounds,
            )
        assert meter.reserves == list(expected_reserves)
        assert _CountingTuple.visits == expected_yields
        assert _CountingTuple.index_visits == expected_index

    # --- The actual carried B segment-domain gate: closed BEFORE
    # the first reservation or element yield (reserves, counted
    # yields and counted index gets all stay empty).
    meter = _D2Meter(10_000_000)
    _CountingTuple.visits = 0
    _CountingTuple.index_visits = 0
    with pytest.raises(
        ValueError,
        match="the retained region segments exceed the actual carried proof segment bound",
    ):
        helper(
            meter,
            text,
            _CountingTuple(segments * 33),
            admitted,
            20,
            20,
            cap,
            proof_bounds,
        )
    assert meter.reserves == []
    assert _CountingTuple.visits == 0
    assert _CountingTuple.index_visits == 0

    meter = _D2Meter(10_000_000)
    _CountingTuple.visits = 0
    _CountingTuple.index_visits = 0
    with pytest.raises(
        ValueError,
        match="the admitted region segment indices exceed the actual carried proof segment bound",
    ):
        helper(
            meter,
            text,
            segments,
            _CountingTuple(tuple(range(33))),
            20,
            20,
            cap,
            proof_bounds,
        )
    assert meter.reserves == []
    assert _CountingTuple.visits == 0
    assert _CountingTuple.index_visits == 0

    meter = _D2Meter(10_000_000)
    with pytest.raises(
        ValueError,
        match="the retained region proof bound context must be the actual concrete record",
    ):
        helper(
            meter,
            text,
            segments,
            admitted,
            20,
            20,
            cap,
            SimpleNamespace(max_segments=32),  # type: ignore[arg-type]
        )
    assert meter.reserves == []

    class _ExtraBounds(BundleProofBounds):
        extra: tuple[int, ...] = ()

    meter = _D2Meter(10_000_000)
    with pytest.raises(
        ValueError,
        match="the retained region proof bound context must be the actual concrete record",
    ):
        helper(meter, text, segments, admitted, 20, 20, cap, _ExtraBounds())
    assert meter.reserves == []

    partial_bounds = BundleProofBounds.model_construct()
    partial_bounds.__dict__.pop("max_segments")
    assert not hasattr(partial_bounds, "max_segments")
    bad_bounds = (
        partial_bounds,
        *(
            BundleProofBounds.model_construct(max_segments=value)
            for value in (True, 32.0, 0, 10_001)
        ),
    )
    for bad_bound in bad_bounds:
        meter = _D2Meter(10_000_000)
        with pytest.raises(
            ValueError,
            match="the retained region proof bound context must carry a closed segment bound",
        ):
            helper(meter, text, segments, admitted, 20, 20, cap, bad_bound)
        assert meter.reserves == []

    # A valid by-value stricter copy is legal: the class fence does
    # not prove identity to the original bound instance.
    strict_bounds = BundleProofBounds(max_segments=1)
    meter = _D2Meter(169)
    assert helper(meter, text, segments, admitted, 20, 20, cap, strict_bounds) == (0, 144)
    assert meter.reserves == [5, 20, 144]

    # --- The genuine strict-cap32 public P/R/G FILE at its actual
    # source-size cap stays legal through the new S constructor
    # (the cap is a SIZE domain, never chosen as a work meter).
    ns2, state2 = r_bootstrap(
        MODES[0],
        "s-d2-cap32",
        root_body="Read `A.md` before work.",
        graph_bounds=GraphBounds(max_single_source_bytes=32),
    )
    cid = "synthetic-d2-cap32-A"
    issued = r_issue(state2, ns2, cid, ENDPOINTS[0], (CAUSAL_ROOT_FACT,), "cat A.md")
    assert issued.outcome.value == "accepted", issued.diagnostics
    observed = r_observe(
        issued.state, ns2, (read_request(ENDPOINTS[0], cid, "a" * 32, "cat A.md"),)
    )
    assert observed.outcome.value == "accepted", observed.diagnostics
    state2 = observed.state
    r2 = derive_root_region_graph(state2, ns2)
    assert r2.outcome.value == "ready"
    resolved2 = r2.resolved_source
    assert (
        resolved2 is not None
        and r2.f_result is not None
        and r2.f_result.overlay is not None
        and r2.e_overlay is not None
    )
    key2 = _s_selected_root_record(ns2, resolved2.root_digest)
    root2 = RootRegionAdmissionEntry(
        entry_class=key2.authority_class,
        content_key=key2.content_key,
        key_record=key2,
        width=1,
        member_classes=key2.member_classes,
        root_digest=key2.root_digest,
        root_source=resolved2,
    )
    assert root2.root_source is resolved2
    groups2: dict[str, list[Any]] = {}
    for group in r2.e_overlay.groups:
        groups2.setdefault(group.occurrence_id, []).append(group)
    g2 = CurrentAdmissionBounds()
    entries2, _p2, _a2, _m2, _t2, _d2 = _assemble_file_entries(
        state2.d_state,
        _d_ns(ns2),
        _s_admission_ns(ns2),
        key2.root_digest,
        g2,
        len(ns2.workspace.encode("utf-8")),
        key2.content_key,
        len(resolved2.root_text.encode("utf-8")),
        groups2,
        {node.path: node.depth for node in r2.f_result.overlay.nodes},
        CurrentAdmissionEntry,
        _GOuter(r2.f_bounds, g2),
        _GStage(ns2.graph_bounds),
        selected_root_digest=key2.root_digest,
    )
    old_entry2 = next(e for e in entries2.values() if e.key_record.member_occurrences == ("A.md",))
    assert old_entry2.proof is not None
    assert len(old_entry2.proof.source_text.encode("utf-8")) == 32
    new_entry2 = RootRegionAdmissionEntry(
        **{
            name: getattr(old_entry2, name)
            for name in (
                "entry_class",
                "content_key",
                "key_record",
                "width",
                "member_classes",
                "root_digest",
                "proof",
                "admitted_segments",
                "witnesses",
            )
        }
    )
    assert new_entry2.proof is old_entry2.proof


# --- D2 batch 2b: canonical/namespace metadata component precharge
# (the ACTUAL C rekey/serializer work) plus the closed key-record
# workspace BEFORE the C serializer -------------------------------


def test_d2_canonical_metadata_precharge_reservation_before_rekey_target() -> None:
    """D2 batch 2b: the SEPARATE bounded-charger canonical
    metadata component precharge (``root-region-admission-
    precharge/v1``, the canonical component) with the guarded
    caller sequence (the precharge, then the real target only
    after it completes), each boundary with its OWN fresh budget.

    Positive FIRST: (a) the leaf rekey pays
    [1825, 4734, 2916, 244, 2916, 244, 551, 4154] (the fence
    walk, the charged ceiling calculation, then the ACTUAL
    recipe order: the namespace payload 2*1406+104, the scoped
    input 2*70+104, the namespace constructor's integrity
    re-run of both, its validator walks, the content-key
    payload 2*2025+104) and its actual ``_canonical_entry_key``
    target performs exactly 5 sha passes and 11 json.dumps (the
    accepted C recipe), the key byte-identical; (b) the
    admission-parent scope join pays the same eight plus the
    join's five reservations and the 301-unit comparison pool,
    and its actual ``_s_entry_scope_joined`` target performs 4
    sha / 10 dumps; (c) a fence-legal non-ASCII/escape record
    completes at its exact total with ceilings that DOMINATE
    the independently measured actual serializer lengths (tight
    here) and an idempotent rekey; the LEGAL at-cap 4096-byte
    workspace stays legal (the cap is a SIZE domain, never a
    work meter).  Exact/one-below budgets cross at every real
    reservation target BEFORE any serializer/hash attempt.
    Closed boundaries (reserver, record class, partial record,
    bypassed ownership container, over-cap (O(1) count and
    mid-walk UTF-8)/noncanonical/doubled-slash/
    lone-surrogate/empty workspace, overlong principal,
    non-str/over-cap member path, wrong parent class) refuse
    with the exact fixed private error and ZERO sha/dumps; the
    walk-based refusals (noncanonical, doubled slash, lone
    surrogate, mid-walk UTF-8 crossing, over-cap member path)
    now pay the FENCE reservation first, and the over-cap
    4097-byte workspace and 257-byte member path additionally
    refuse at the ACTUAL leaf/constructor/parent boundaries
    BEFORE any canonical rekey.  The member path closes under
    the inherited two-cap path ceiling (the smaller of the
    carried graph and observation path-byte caps: 256 here), and
    the LEGAL at-cap 256-byte member path stays legal."""
    ns, state, r, g, root_entry, files, parent = _offset_component()
    entry = next(e for e in files if e.key_record.member_occurrences == ("A.md",))
    record = entry.key_record
    helper = rram._s_canonical_metadata_precharge_closed

    # The ACTUAL C-recipe serializer work, counted where the
    # rekey path resolves it: _sha256_hex in the CAM namespace
    # (the entry namespace + content key) and the BAM namespace
    # (the BundleAdmissionNamespace integrity re-derivation),
    # json.dumps globally.
    saved_sha_cam = cam._sha256_hex
    saved_sha_bam = bam._sha256_hex  # type: ignore[attr-defined]
    saved_dumps = json.dumps
    sha_hits = 0
    dumps_hits = 0

    def _sha_count(*args: Any, **kwargs: Any) -> str:
        nonlocal sha_hits
        sha_hits += 1
        return saved_sha_cam(*args, **kwargs)

    def _dumps_count(*args: Any, **kwargs: Any) -> str:
        nonlocal dumps_hits
        dumps_hits += 1
        return saved_dumps(*args, **kwargs)

    def _guarded_canonical(
        limit: int,
        guarded_record: Any,
        target: Any,
        parent_ns: Any = None,
    ) -> tuple[_D2Meter, bool, dict[str, int], str | None]:
        """The ACTUAL guarded caller sequence, identical for
        every budget: the canonical metadata precharge first,
        then the real target (the canonical rekey, the scope
        join) ONLY after a completed precharge -- a crossing
        budget therefore stops before any serializer/hash
        attempt.  Each boundary gets its OWN fresh budget."""
        nonlocal sha_hits, dumps_hits
        meter = _D2Meter(limit)
        sha_hits = 0
        dumps_hits = 0
        cam._sha256_hex = _sha_count
        bam._sha256_hex = _sha_count  # type: ignore[attr-defined]
        json.dumps = _dumps_count
        error: str | None = None
        completed = False
        try:
            try:
                helper(meter, guarded_record, parent_ns)
            except ValueError as exc:
                error = str(exc)
            else:
                try:
                    target()
                    completed = True
                except ValueError as exc:
                    error = str(exc)
        finally:
            cam._sha256_hex = saved_sha_cam
            bam._sha256_hex = saved_sha_bam  # type: ignore[attr-defined]
            json.dumps = saved_dumps
        return meter, completed, {"sha": sha_hits, "dumps": dumps_hits}, error

    # --- Positive FIRST (a): the leaf rekey, exact total budget.
    meter, completed, _, _ = _guarded_canonical(10_000_000, record, lambda: None)
    leaf_reserves = (1825, 4734, 2916, 244, 2916, 244, 551, 4154)
    assert completed
    assert tuple(meter.reserves) == leaf_reserves
    leaf_total = sum(leaf_reserves)
    # The closed ceilings are TIGHT on the fence-legal ASCII
    # fixture (the recipe-actual serializer lengths).
    x1, s1, x2 = rram._s_canonical_payload_ceils(record)
    assert (x1, s1, x2) == (1406, 70, 2025)
    assert x1 == len(
        _canonical_namespace_fields(
            record.principal,
            record.session,
            record.repository,
            record.route,
            record.model_identity,
            record.config_fingerprint,
            record.admission_version,
            record.graph_version,
            record.reference_version,
            record.proof_version,
            record.observation_version,
            record.mode.value,
            record.admission_bounds,
            record.proof_bounds,
            record.graph_bounds,
            record.observation_bounds,
        )
    )
    assert x2 == len(
        _key_canonical(
            _entry_admission_namespace(record),
            record.root_digest,
            record.authority_class,
            record.member_occurrences,
            record.member_classes,
            record.aggregate_source_digest,
            record.ownership_groups,
        )
    )
    assert s1 == 65 + len(record.workspace.encode("utf-8"))
    rekeyed: list[str] = []
    meter, completed, counts, error = _guarded_canonical(
        leaf_total, record, lambda: rekeyed.append(_canonical_entry_key(record))
    )
    assert completed
    assert error is None
    assert meter.remaining == 0
    assert counts == {"sha": 5, "dumps": 11}
    assert rekeyed == [entry.content_key]

    # --- Positive FIRST (b): the admission-parent scope join
    # (a fresh budget covering the join's own re-derivation).
    meter, completed, _, _ = _guarded_canonical(10_000_000, record, lambda: None, parent.ns)
    join_reserves = (2916, 244, 2916, 244, 551, 301)
    assert completed
    assert tuple(meter.reserves) == leaf_reserves + join_reserves
    parent_total = leaf_total + sum(join_reserves)
    meter, completed, counts, error = _guarded_canonical(
        parent_total,
        record,
        lambda: rram._s_entry_scope_joined(record, parent.ns),
        parent.ns,
    )
    assert completed
    assert error is None
    assert meter.remaining == 0
    assert counts == {"sha": 4, "dumps": 10}

    # --- Positive FIRST (c): a fence-legal non-ASCII/escape
    # record (BMP + astral + quote + backslash): the exact total
    # completes, the ceilings DOMINATE the independently measured
    # actual serializer lengths, and the rekey is idempotent.
    rec_u = record.model_copy(
        update={
            "principal": 'ünïcode-"q\\u201d"-𝕜é',
            "model_identity": 'm-é-𝔞-"x\\y',
            "admission_version": 'v-ø-𝕫-"\\',
        }
    )
    meter, completed, _, _ = _guarded_canonical(10_000_000, rec_u, lambda: None)
    unicode_reserves = (1751, 4734, 2972, 244, 2972, 244, 514, 4208)
    assert completed
    assert tuple(meter.reserves) == unicode_reserves
    x1u, _s1u, x2u = rram._s_canonical_payload_ceils(rec_u)
    assert x1u >= len(
        _canonical_namespace_fields(
            rec_u.principal,
            rec_u.session,
            rec_u.repository,
            rec_u.route,
            rec_u.model_identity,
            rec_u.config_fingerprint,
            rec_u.admission_version,
            rec_u.graph_version,
            rec_u.reference_version,
            rec_u.proof_version,
            rec_u.observation_version,
            rec_u.mode.value,
            rec_u.admission_bounds,
            rec_u.proof_bounds,
            rec_u.graph_bounds,
            rec_u.observation_bounds,
        )
    )
    assert x2u >= len(
        _key_canonical(
            _entry_admission_namespace(rec_u),
            rec_u.root_digest,
            rec_u.authority_class,
            rec_u.member_occurrences,
            rec_u.member_classes,
            rec_u.aggregate_source_digest,
            rec_u.ownership_groups,
        )
    )
    unicode_keys: list[str] = []
    meter, completed, counts, _ = _guarded_canonical(
        sum(unicode_reserves), rec_u, lambda: unicode_keys.append(_canonical_entry_key(rec_u))
    )
    assert completed
    assert meter.remaining == 0
    assert counts == {"sha": 5, "dumps": 11}
    assert unicode_keys and unicode_keys[0] == _canonical_entry_key(rec_u)

    # The LEGAL at-cap 4096-byte workspace stays legal (the cap
    # is a SIZE domain, never a work meter): precharge + actual
    # rekey complete, no refusal.
    ws_at_cap = record.model_copy(update={"workspace": "/" + "a" * 4095})
    cap_keys: list[str] = []
    meter, completed, counts, _ = _guarded_canonical(
        10_000_000, ws_at_cap, lambda: cap_keys.append(_canonical_entry_key(ws_at_cap))
    )
    assert completed
    assert meter.remaining > 0
    assert counts == {"sha": 5, "dumps": 11}
    assert len(cap_keys) == 1

    # --- Exact/one-below crossings at EVERY real reservation
    # target: the guarded sequence stops BEFORE any
    # serializer/hash attempt.
    def _crossing_rows(reserves: tuple[int, ...]) -> tuple[tuple[int, tuple[int, ...]], ...]:
        """Exact and one-below at every reservation target: the
        expected reserves are the SUCCESSFUL prefixes (the meter
        raises at the next charge, so the target never runs)."""
        one_below: list[tuple[int, tuple[int, ...]]] = []
        prefix = 0
        for index in range(len(reserves)):
            one_below.append((prefix + reserves[index] - 1, reserves[:index]))
            prefix += reserves[index]
        exact: list[tuple[int, tuple[int, ...]]] = []
        prefix = 0
        for index in range(len(reserves)):
            prefix += reserves[index]
            exact.append((prefix, reserves[: index + 1]))
        # The FINAL exact row (limit == the full total) is the
        # positive case above: the helper completes there.
        return tuple(one_below + exact[:-1])

    for reserves in (leaf_reserves, leaf_reserves + join_reserves):
        for limit, expected in _crossing_rows(reserves):
            meter, completed, counts, error = _guarded_canonical(
                limit, record, lambda: None, parent.ns if len(reserves) > 8 else None
            )
            assert not completed
            assert error == "the work meter budget is exhausted before the crossing target"
            assert meter.reserves == list(expected)
            assert counts == {"sha": 0, "dumps": 0}

    # --- Closed boundaries (negative-only coherent copies): the
    # exact fixed private errors, the exact reserved prefixes,
    # and ZERO serializer work (the targets never run).
    def _target_never_runs() -> None:
        raise AssertionError("the target must never run on a closed boundary")

    # reserver callback closure
    for bad_reserver in (None, SimpleNamespace()):
        meter = _D2Meter(10_000_000)
        with pytest.raises(
            ValueError,
            match="the canonical metadata precharge reserver must carry a typed reserve callback",
        ):
            helper(bad_reserver, record)  # type: ignore[arg-type]
        assert meter.reserves == []
    # record class closure
    meter = _D2Meter(10_000_000)
    with pytest.raises(ValueError, match="the key record must be the actual canonical record"):
        helper(meter, SimpleNamespace())  # type: ignore[arg-type]
    assert meter.reserves == []
    # partial record (a model_construct field omission)
    rec_partial = BundleKeyRecord.model_construct()
    meter = _D2Meter(10_000_000)
    with pytest.raises(ValueError, match="the entry key record must carry its closed fields"):
        helper(meter, rec_partial)
    assert meter.reserves == []
    # bypassed ownership container (a copied None): the SHARED
    # O(1) shape phase refuses with the fixed private error
    # BEFORE any reservation (the fence's len() can never raise
    # a raw TypeError).
    rec_groups = record.model_copy(update={"ownership_groups": None})
    meter, completed, counts, error = _guarded_canonical(10_000_000, rec_groups, _target_never_runs)
    assert not completed
    assert error == "the key record ownership groups must carry a nonempty closed tuple"
    assert meter.reserves == []
    assert counts == {"sha": 0, "dumps": 0}
    # the RETAINED over-cap workspace regression (the probe
    # finding): 4097 bytes against the actual carried 4096 cap.
    ws_over = record.model_copy(update={"workspace": "/" + "a" * 4096})
    meter, completed, counts, error = _guarded_canonical(10_000_000, ws_over, _target_never_runs)
    assert not completed
    assert error == "the key record workspace exceeds the actual carried graph path bound"
    assert meter.reserves == []
    assert counts == {"sha": 0, "dumps": 0}
    # noncanonical (relative) workspace: the O(1) shape gate
    # passes, the FENCE reservation is paid, and only THEN the
    # bounded walk's canonical equality check refuses.
    ws_rel = record.model_copy(update={"workspace": "work"})
    meter, completed, counts, error = _guarded_canonical(10_000_000, ws_rel, _target_never_runs)
    assert not completed
    assert error == "the key record workspace must be a canonical absolute POSIX path"
    assert meter.reserves == [1821]
    assert counts == {"sha": 0, "dumps": 0}
    # canonical EQUALITY: a valid spelling that normalizes to
    # ANOTHER string (doubled slash) is not the canonical
    # workspace and refuses before any serialization.
    ws_dslash = record.model_copy(update={"workspace": "/work//a"})
    meter, completed, counts, error = _guarded_canonical(10_000_000, ws_dslash, _target_never_runs)
    assert not completed
    assert error == "the key record workspace must be a canonical absolute POSIX path"
    assert meter.reserves == [1837]
    assert counts == {"sha": 0, "dumps": 0}
    # a lone surrogate is not encodable UTF-8: the bounded
    # no-copy check refuses BEFORE any owned encoding.
    ws_surr = record.model_copy(update={"workspace": "/wo\ud800rk"})
    meter, completed, counts, error = _guarded_canonical(10_000_000, ws_surr, _target_never_runs)
    assert not completed
    assert error == "the key record workspace must be valid UTF-8 text"
    assert meter.reserves == [1829]
    assert counts == {"sha": 0, "dumps": 0}
    # a 3-byte character workspace UNDER the O(1) character
    # bound but OVER the actual UTF-8 cap refuses mid-walk
    # (2001 chars, 6001 bytes against the 4096 cap).
    ws_mb = record.model_copy(update={"workspace": "/" + "\u4e2d" * 2000})
    meter, completed, counts, error = _guarded_canonical(10_000_000, ws_mb, _target_never_runs)
    assert not completed
    assert error == "the key record workspace exceeds the actual carried graph path bound"
    assert meter.reserves == [9809]
    assert counts == {"sha": 0, "dumps": 0}
    # empty workspace
    ws_empty = record.model_copy(update={"workspace": ""})
    meter, completed, counts, error = _guarded_canonical(10_000_000, ws_empty, _target_never_runs)
    assert not completed
    assert error == "the key record workspace must carry closed canonical text"
    assert meter.reserves == []
    assert counts == {"sha": 0, "dumps": 0}
    # overlong principal: the fence reserve is paid, THEN the
    # original C text law refuses (the truthful precedence).
    rec_pr = record.model_copy(update={"principal": "p" * 257})
    meter, completed, counts, error = _guarded_canonical(10_000_000, rec_pr, _target_never_runs)
    assert not completed
    assert error == "principal must be 1..256 characters"
    assert meter.reserves == [2285]
    assert counts == {"sha": 0, "dumps": 0}
    # non-str member occurrence (a bypassed element)
    rec_path = record.model_copy(update={"member_occurrences": (5,)})
    meter, completed, counts, error = _guarded_canonical(10_000_000, rec_path, _target_never_runs)
    assert not completed
    assert error == "the key record member occurrences must carry closed paths"
    assert meter.reserves == [1825]
    assert counts == {"sha": 0, "dumps": 0}
    # over-cap member path: a 257-byte relative path passes the
    # O(1) character-count gate (the C shape law carries no byte
    # ceiling of its own), the FENCE reservation is paid, and
    # only THEN the closed fence's per-path domain closure
    # refuses it BEFORE any _check_rel_path pass or serializer.
    # The domain is the inherited two-cap path ceiling (the
    # smaller of the carried graph and observation path-byte
    # caps: 256 on this fixture).
    mp_over = record.model_copy(update={"member_occurrences": ("a" * 257,)})
    meter, completed, counts, error = _guarded_canonical(10_000_000, mp_over, _target_never_runs)
    assert not completed
    assert error == "the key record member occurrences exceed the actual carried path bound"
    assert meter.reserves == [1825]
    assert counts == {"sha": 0, "dumps": 0}
    # mid-walk member path crossing: 129 two-byte characters
    # (258 bytes) pass the O(1) character-count gate (129 <= 256)
    # and refuse at the ACTUAL byte crossing, before any
    # _check_rel_path pass or serializer.
    mp_mb = record.model_copy(update={"member_occurrences": ("\u4e2d" * 129,)})
    meter, completed, counts, error = _guarded_canonical(10_000_000, mp_mb, _target_never_runs)
    assert not completed
    assert error == "the key record member occurrences exceed the actual carried path bound"
    assert meter.reserves == [1825]
    assert counts == {"sha": 0, "dumps": 0}
    # The LEGAL at-cap 256-byte member path stays legal (the cap
    # is a SIZE domain, never a work meter): the precharge plus
    # the actual rekey complete, the content-key ceiling
    # DOMINATES the actual serializer length, no refusal.
    mp_at_cap = record.model_copy(update={"member_occurrences": ("a" * 253 + ".md",)})
    mp_keys: list[str] = []
    meter, completed, counts, _ = _guarded_canonical(
        10_000_000, mp_at_cap, lambda: mp_keys.append(_canonical_entry_key(mp_at_cap))
    )
    assert completed
    assert meter.remaining > 0
    assert counts == {"sha": 5, "dumps": 11}
    assert len(mp_keys) == 1
    _x1_mp, _s1_mp, x2_mp = rram._s_canonical_payload_ceils(mp_at_cap)
    assert x2_mp >= len(
        _key_canonical(
            _entry_admission_namespace(mp_at_cap),
            mp_at_cap.root_digest,
            mp_at_cap.authority_class,
            mp_at_cap.member_occurrences,
            mp_at_cap.member_classes,
            mp_at_cap.aggregate_source_digest,
            mp_at_cap.ownership_groups,
        )
    )
    # wrong parent namespace class (after the leaf reservations)
    meter, completed, counts, error = _guarded_canonical(
        10_000_000, record, _target_never_runs, SimpleNamespace()
    )
    assert not completed
    assert error == "the parent namespace must be the actual closed lineage namespace"
    assert meter.reserves == list(leaf_reserves)
    assert counts == {"sha": 0, "dumps": 0}

    # --- The SAME over-cap workspace regression at the ACTUAL S
    # boundaries (the probe's six targets collapse onto the three
    # S-side gates; zero canonical/sha/dumps at each).
    entry_fields = {name: getattr(entry, name) for name in type(entry).model_fields}
    with pytest.raises(
        ValueError,
        match="the key record workspace exceeds the actual carried graph path bound",
    ):
        rram._s_entry_leaf_closed(entry.model_copy(update={"key_record": ws_over}))
    with pytest.raises(
        ValidationError,
        match="the key record workspace exceeds the actual carried graph path bound",
    ):
        RootRegionAdmissionEntry(**{**entry_fields, "key_record": ws_over})
    parent_fields = {name: getattr(parent, name) for name in type(parent).model_fields}
    parent_fields["entries"] = tuple(
        entry.model_copy(update={"key_record": ws_over})
        if e.key_record.member_occurrences == ("A.md",)
        else e
        for e in parent.entries
    )
    with pytest.raises(
        ValidationError,
        match="the key record workspace exceeds the actual carried graph path bound",
    ):
        RootRegionAdmission(**parent_fields)

    # --- The SAME over-cap (257-byte) member path at the ACTUAL S
    # boundaries (the closed fence's per-path domain closure is
    # shared by the leaf law, the constructor and the parent
    # re-run; zero canonical sha/dumps at each).
    with pytest.raises(
        ValueError,
        match="the key record member occurrences exceed the actual carried path bound",
    ):
        rram._s_entry_leaf_closed(entry.model_copy(update={"key_record": mp_over}))
    with pytest.raises(
        ValidationError,
        match="the key record member occurrences exceed the actual carried path bound",
    ):
        RootRegionAdmissionEntry(**{**entry_fields, "key_record": mp_over})
    parent_fields_mp = {name: getattr(parent, name) for name in type(parent).model_fields}
    parent_fields_mp["entries"] = tuple(
        entry.model_copy(update={"key_record": mp_over})
        if e.key_record.member_occurrences == ("A.md",)
        else e
        for e in parent.entries
    )
    with pytest.raises(
        ValidationError,
        match="the key record member occurrences exceed the actual carried path bound",
    ):
        RootRegionAdmission(**parent_fields_mp)


# --- D2 batch 3: ROOT content component precharge ---------------


def test_d2_root_content_precharge_reservation_before_crossing_target() -> None:
    """D2 batch 3: the SEPARATE bounded-charger ROOT content
    component precharge (``root-region-admission-precharge/v1``),
    mirroring the order of the actual closed R source content law
    (the root branch of the leaf law and the constructor): the
    ACTUAL guarded caller sequence (the precharge first, then the
    real target only after it completes) at BOTH boundaries, each
    with its OWN fresh budget.

    Positive FIRST: (a) the LEAN offset fixture's root entry
    (envelope kind, the 24-character/24-byte retained body) pays
    [145, 24, 145, 24, 152] (145 = one fixed fence unit plus the
    64+16+64 closed 64-hex set visits at the fixed 64 length,
    run once here and repeated by the actual target; 24 = the
    ACTUAL character visits of the no-copy capped UTF-8
    measurement, likewise repeated by the target; 152 =
    2*24+104 encode/hash), the leaf target
    makes exactly ONE R-module content sha pass, and the
    constructor re-run keeps the actual root source identity;
    (b) a genuine public-P UNICODE root (15 characters/22 bytes)
    pays [145, 15, 148] through the same targets; (c) a genuine
    public-P EMPTY root pays [145, 0, 104].  The fresh S parent
    re-run is a separate unmetered identity boundary.  Exact/
    one-below budgets cross at the real reservations BEFORE any
    target attempt, and the closed boundaries keep the legal
    at-length source legal (the actual hard root byte cap is a
    SIZE domain, never a work meter) while refusing forged
    declared lengths, a lone surrogate, a non-hex digest and the
    non-closed scalars before the first walk or reservation.
    This closes the ROOT CONTENT COMPONENT ONLY: the leaf law's
    own metadata/canonical ord work, the parent re-run and the
    whole-operation costs remain pending later batches."""
    from slaif_local_coding.constitution.bundles import (
        root_region_graph_models as rrgm,
    )

    # --- Offset fixture root (the actual retained root source).
    ns, state, r, g, root_entry, _files, parent = _offset_component()
    src = root_entry.root_source
    text = src.root_text
    digest = src.root_digest
    declared = src.root_byte_length
    assert (len(text), declared) == (24, 24)
    helper = rram._s_root_content_precharge_closed
    leaf = rram._s_entry_leaf_closed
    # The ACTUAL target frames whose repeated measurement walk
    # the precharge reserves (the closed content law and its
    # no-copy capped walker).
    target_codes = (
        rrgm._r_source_content_ok.__code__,
        rrgm._r_utf8_byte_length_capped.__code__,
    )

    # Counters measured by the guarded runs (reset per run).  The
    # ord profiling is scoped to the ACTUAL helper frame for the
    # component count; the separate total records the leaf law's
    # own metadata/canonical ord work (full D2 cost evidence).
    leaf_entries = 0
    hash_hits = 0
    helper_ord_visits = 0
    target_ord_visits = 0
    total_ord_visits = 0

    def _ord_profile(frame: Any, event: str, arg: Any) -> Any:
        nonlocal helper_ord_visits, target_ord_visits, total_ord_visits
        if event == "c_return" and getattr(arg, "__name__", "") == "ord":
            total_ord_visits += 1
            if frame.f_code is helper.__code__:
                helper_ord_visits += 1
            elif frame.f_code in target_codes:
                target_ord_visits += 1
        return None

    def _target_trace(frame: Any, event: str, arg: Any) -> Any:
        nonlocal leaf_entries
        if frame.f_code is leaf.__code__ and event == "call":
            leaf_entries += 1
        return _target_trace

    saved_sha = rrgm._sha256_hex  # type: ignore[attr-defined]

    def _sha_count(*args: Any, **kwargs: Any) -> str:
        nonlocal hash_hits
        hash_hits += 1
        return saved_sha(*args, **kwargs)

    def _guarded_target(
        kind: str,
        limit: int,
        guarded_entry: Any,
        guarded_text: Any,
        guarded_digest: Any,
        guarded_declared: Any,
    ) -> tuple[_D2Meter, bool, dict[str, int]]:
        """The ACTUAL guarded caller sequence, identical for every
        budget: the ROOT content precharge first, then the real
        target for ``kind`` (the direct leaf law, or the direct
        constructor re-run) ONLY after a completed precharge -- a
        crossing budget therefore stops before any target attempt
        (no conditional bypass).  Each boundary gets its OWN fresh
        root-content budget: one full charge covers the ROOT
        content component for that boundary, never repeated
        leaf/constructor/parent work."""
        nonlocal leaf_entries, hash_hits, helper_ord_visits, target_ord_visits, total_ord_visits
        meter = _D2Meter(limit)
        leaf_entries = 0
        hash_hits = 0
        helper_ord_visits = 0
        target_ord_visits = 0
        total_ord_visits = 0
        fields = {name: getattr(guarded_entry, name) for name in type(guarded_entry).model_fields}
        saved_profile = sys.getprofile()
        saved_trace = sys.gettrace()
        rrgm._sha256_hex = _sha_count  # type: ignore[attr-defined]
        try:
            sys.settrace(_target_trace)
            sys.setprofile(_ord_profile)
            helper(meter, guarded_text, guarded_digest, guarded_declared)
            if kind == "leaf":
                leaf(guarded_entry)
            elif kind == "constructor":
                rebuilt = RootRegionAdmissionEntry(**fields)
                assert rebuilt.root_source is guarded_entry.root_source
            else:
                raise AssertionError("unknown closed guarded target kind")
            completed = True
        except ValueError:
            completed = False
        finally:
            sys.settrace(saved_trace)
            sys.setprofile(saved_profile)
            rrgm._sha256_hex = saved_sha  # type: ignore[attr-defined]
        counts = {
            "leaf_entries": leaf_entries,
            "hash_calls": hash_hits,
            "helper_ord_visits": helper_ord_visits,
            "target_ord_visits": target_ord_visits,
            "total_ord_visits": total_ord_visits,
        }
        return meter, completed, counts

    # --- Positive FIRST: the offset fixture root, both
    # boundaries with their own fresh budgets.
    meter, completed, counts = _guarded_target("leaf", 490, root_entry, text, digest, declared)
    assert completed
    assert meter.reserves == [145, 24, 145, 24, 152]
    assert meter.remaining == 0
    assert counts["helper_ord_visits"] == 24
    assert counts["target_ord_visits"] == 24
    assert counts["total_ord_visits"] > counts["helper_ord_visits"]
    # The actual content law: ONE R-module sha pass over the owned
    # encode, one leaf entry, no S-module sha.
    # The target's repeated measurement walk is the reserved 24
    # visits (charged before the target ran).
    assert counts["leaf_entries"] == 1
    assert counts["hash_calls"] == 1

    meter, completed, counts = _guarded_target(
        "constructor", 490, root_entry, text, digest, declared
    )
    assert completed
    assert meter.reserves == [145, 24, 145, 24, 152]
    assert counts["helper_ord_visits"] == 24
    assert counts["target_ord_visits"] == 24
    assert counts["total_ord_visits"] > counts["helper_ord_visits"]
    assert counts["leaf_entries"] == 1
    assert counts["hash_calls"] == 1

    # --- Exact/one-below budgets cross at the real
    # reservations, always before any target attempt.
    for limit, expected_reserves, expected_ord in (
        (144, [], 0),
        (145, [145], 0),
        (168, [145], 0),
        (169, [145, 24], 24),
        (313, [145, 24], 24),
        (314, [145, 24, 145], 24),
        (337, [145, 24, 145], 24),
        (338, [145, 24, 145, 24], 24),
        (489, [145, 24, 145, 24], 24),
    ):
        meter, completed, counts = _guarded_target(
            "leaf", limit, root_entry, text, digest, declared
        )
        assert not completed
        assert meter.reserves == expected_reserves
        assert counts["helper_ord_visits"] == expected_ord
        assert counts["target_ord_visits"] == 0
        assert counts["total_ord_visits"] == expected_ord
        assert counts["hash_calls"] == 0
        assert counts["leaf_entries"] == 0

    # --- Positive FIRST: the genuine public-P UNICODE root
    # (multi-byte widths through both the helper walk and the
    # actual encode/hash targets).
    ns_u, state_u = qf.q_bootstrap(
        MODES[0], "s-d2-root-unicode", "R\u00e9gion \u201cA.md\u201d \u2603"
    )
    cmd_u = "cat A.md"
    state_u = qf.q_observe(
        qf.q_issue(state_u, ns_u, "mixed", "responses", cmd_u, (CAUSAL_ROOT_FACT,)),
        ns_u,
        "responses",
        "mixed",
        qf.mixed_body("Unrelated prefix.", qf.MARK, "A body."),
        cmd_u,
    )
    _r_u, _g_u, root_u, _files_u, _parent_u, _diags_u = _s_component_parent(state_u, ns_u)
    src_u = root_u.root_source
    assert (len(src_u.root_text), src_u.root_byte_length) == (15, 22)
    meter, completed, counts = _guarded_target(
        "leaf", 468, root_u, src_u.root_text, src_u.root_digest, src_u.root_byte_length
    )
    assert completed
    assert meter.reserves == [145, 15, 145, 15, 148]
    assert meter.remaining == 0
    assert counts["helper_ord_visits"] == 15
    assert counts["target_ord_visits"] == 15
    assert counts["total_ord_visits"] > counts["helper_ord_visits"]
    assert counts["leaf_entries"] == 1
    assert counts["hash_calls"] == 1
    meter, completed, counts = _guarded_target(
        "leaf", 467, root_u, src_u.root_text, src_u.root_digest, src_u.root_byte_length
    )
    assert not completed
    assert meter.reserves == [145, 15, 145, 15]
    assert counts["helper_ord_visits"] == 15
    assert counts["target_ord_visits"] == 0
    assert counts["hash_calls"] == 0
    assert counts["leaf_entries"] == 0

    # --- Positive FIRST: the genuine public-P EMPTY root (zero
    # character visits; the fixed pad-plus-digest reservation
    # still guards the actual encode/hash targets).
    ns_e, state_e = qf.q_bootstrap(MODES[0], "s-d2-root-empty", "")
    state_e = qf.q_observe(
        qf.q_issue(state_e, ns_e, "mixed", "responses", cmd_u, (CAUSAL_ROOT_FACT,)),
        ns_e,
        "responses",
        "mixed",
        qf.mixed_body("Unrelated prefix.", qf.MARK, "A body."),
        cmd_u,
    )
    _r_e, _g_e, root_e, _files_e, _parent_e, _diags_e = _s_component_parent(state_e, ns_e)
    src_e = root_e.root_source
    assert (len(src_e.root_text), src_e.root_byte_length) == (0, 0)
    meter, completed, counts = _guarded_target(
        "leaf", 394, root_e, src_e.root_text, src_e.root_digest, src_e.root_byte_length
    )
    assert completed
    assert meter.reserves == [145, 0, 145, 0, 104]
    assert meter.remaining == 0
    assert counts["helper_ord_visits"] == 0
    assert counts["target_ord_visits"] == 0
    assert counts["leaf_entries"] == 1
    assert counts["hash_calls"] == 1
    meter, completed, counts = _guarded_target(
        "leaf", 393, root_e, src_e.root_text, src_e.root_digest, src_e.root_byte_length
    )
    assert not completed
    assert meter.reserves == [145, 0, 145, 0]
    assert counts["helper_ord_visits"] == 0
    assert counts["target_ord_visits"] == 0
    assert counts["hash_calls"] == 0
    assert counts["leaf_entries"] == 0

    # --- The fresh S parent re-run is a separate boundary
    # (the unmetered identity check; the parent's costs belong to
    # the next batch).
    parent_fields = {name: getattr(parent, name) for name in type(parent).model_fields}
    rebuilt_parent = RootRegionAdmission(**parent_fields)
    assert rebuilt_parent.state is state
    assert rebuilt_parent.r_result is r

    # --- Closed boundaries (negative only): fixed private
    # errors, never AttributeError/IndexError/
    # UnicodeEncodeError/TypeError, before the actual work; the
    # meter's reserve list proves which closed gate fired.
    def _refuses(
        limit: int,
        bad_text: Any,
        bad_digest: Any,
        bad_declared: Any,
        pattern: str,
        expected_reserves: list[int],
    ) -> None:
        meter = _D2Meter(limit)
        with pytest.raises(ValueError, match=pattern):
            helper(meter, bad_text, bad_digest, bad_declared)
        assert meter.reserves == expected_reserves

    _refuses(
        10**9,
        123,
        digest,
        declared,
        "the retained root source must be closed UTF-8 text",
        [],
    )
    _refuses(
        10**9,
        text,
        b"root digest",
        declared,
        "the retained root digest must be closed hex text",
        [],
    )
    _refuses(
        10**9,
        text,
        digest,
        True,
        "the retained root source byte length must be a closed scalar under the actual hard cap",
        [],
    )
    _refuses(
        10**9,
        text,
        digest,
        16_777_217,
        "the retained root source byte length must be a closed scalar under the actual hard cap",
        [],
    )
    _refuses(
        10**9,
        text,
        digest,
        -1,
        "the retained root source byte length must be a closed scalar under the actual hard cap",
        [],
    )
    _refuses(
        10**9,
        text,
        digest,
        24.5,
        "the retained root source byte length must be a closed scalar under the actual hard cap",
        [],
    )
    _refuses(
        10**9,
        "abc",
        digest,
        2,
        "the retained root source bytes are never fewer than its characters",
        [],
    )
    _refuses(
        10**9,
        text,
        digest[:63],
        declared,
        "the retained root digest must be closed 64-hex text",
        [],
    )
    _refuses(
        10**9,
        text,
        digest + "a",
        declared,
        "the retained root digest must be closed 64-hex text",
        [],
    )
    _refuses(
        10**9,
        text,
        digest[:63] + "z",
        declared,
        "the retained root digest must be closed 64-hex text",
        [145],
    )
    _refuses(
        10**9,
        "\ud800",
        digest,
        1,
        "the retained root source must be closed UTF-8 text",
        [145, 1],
    )
    _refuses(
        10**9,
        "\u00e9" * 20,
        digest,
        24,
        "the retained root source exceeds its declared byte length before any owned encode",
        [145, 20],
    )
    _refuses(
        10**9,
        "abc",
        digest,
        4,
        "the retained root byte metadata must equal the measured UTF-8 root length",
        [145, 3],
    )
    _refuses(
        0,
        text,
        digest,
        declared,
        "the work meter budget is exhausted before the crossing target",
        [],
    )
    with pytest.raises(
        ValueError,
        match="the root content precharge reserver must carry a typed reserve callback",
    ):
        helper(None, text, digest, declared)  # type: ignore[arg-type]
    with pytest.raises(
        ValueError,
        match="the root content precharge reserver must carry a typed reserve callback",
    ):
        helper(object(), text, digest, declared)  # type: ignore[arg-type]


# --- D2 batch 4: parent namespace/scope metadata component
# precharge ----------------------------------------------------------


_U18NS_RESERVES: tuple[int, ...] = (
    1176,
    384,
    4877,
    1062,
    7915,
    446,
    7155,
    78,
    9678,
    361,
    4,
    2,
    1653,
    2,
)


def test_d2_parent_namespace_precharge_reservation_before_crossing_target() -> None:
    """D2 batch 4: the SEPARATE bounded-charger PARENT NAMESPACE
    component precharge (the D-namespace RE-DERIVATION and P
    lineage-key recipe ONLY, the actual ``_v_admission`` phase 3,
    ``root-region-admission-precharge/v1``).

    Positive FIRST: the genuine LEAN offset fixture's ACTUAL P
    namespace pays the pinned 14-reserve list (the closure walks,
    the dump-meta construction, the precharge's own ceiling
    calculations, the outer D block, the nested 018-c block, the
    HistoryBounds re-validation, the REPEATED canonical/2-SHA
    block, the canonical workspace re-check, the history-key
    block, the state-scoped block, the four recomputed-key
    equalities, the two state joins, the lineage recipe and the
    final tag reserve), returns the pinned
    ``(26701, 1655, 2031)`` tuple, and the ACTUAL guarded caller
    target (the 25-key ``CausalHistoryNamespace`` re-derivation,
    the four recomputed-key equalities, the two state joins and
    the ``_lineage_key`` recompute) runs exactly once with the
    bounded per-module sha census (2 nested + 4 outer + 1
    lineage) and the 18 charged ceiling walks.  Exact/one-below
    (total-1) and zero budgets cross BEFORE any target attempt
    with every target spy at 0.  Closed negatives: the reserver
    fence, the foreign class fence and the missing-field fence
    (each 0 reserves), the forged non-hex lineage key (the
    closure-walks reserve once, then the fixed hex refusal), the
    over-cap canonical workspace (0 reserves, the O(1) cap gate)
    and the bool HistoryBounds scalar (0 reserves, the closed
    bound-set fence); the forged lineage tag pays the first 13
    reserves before its fixed refusal at its ACTUAL target
    position.  Component evidence only: no parent/whole-operation
    claim, and no old public D/C recipe or cap changes."""
    from types import SimpleNamespace

    from slaif_local_coding.constitution.bundles import (
        bundle_admission_models as bam,
    )
    from slaif_local_coding.constitution.bundles import causal_history_models as chm
    from slaif_local_coding.constitution.bundles import root_lineage_models as rlm

    helper = rram._s_parent_namespace_precharge_closed
    ns, state, _r, _g, _root_entry, _files, _parent = _offset_component()

    zero_visits = {
        "model_validate": 0,
        "sha_bam": 0,
        "sha_chm": 0,
        "sha_rlm": 0,
        "lineage": 0,
        "esc_ceil": 0,
    }
    visits: dict[str, int] = dict(zero_visits)
    original_mv = CausalHistoryNamespace.model_validate
    original_sha_bam = bam._sha256_hex  # type: ignore[attr-defined]
    original_sha_chm = chm._sha256_hex
    original_sha_rlm = rlm._sha256_hex  # type: ignore[attr-defined]
    original_lineage = rram._lineage_key  # type: ignore[attr-defined]
    original_ceil = rram._s_json_string_escaped_ceil

    def model_validate_spy(*args: Any, **kwargs: Any) -> Any:
        visits["model_validate"] += 1
        return original_mv(*args, **kwargs)

    def sha_spy_bam(data: bytes) -> str:
        visits["sha_bam"] += 1
        return original_sha_bam(data)

    def sha_spy_chm(data: bytes) -> str:
        visits["sha_chm"] += 1
        return original_sha_chm(data)

    def sha_spy_rlm(data: bytes) -> str:
        visits["sha_rlm"] += 1
        return original_sha_rlm(data)

    def lineage_spy(
        history_key: str,
        contract_version: str,
        policy_version: str,
        bounds: RootLineageBounds,
    ) -> str:
        visits["lineage"] += 1
        return original_lineage(history_key, contract_version, policy_version, bounds)

    def ceil_spy(value: str) -> int:
        visits["esc_ceil"] += 1
        return original_ceil(value)

    def actual_target() -> None:
        d_ns = chm.CausalHistoryNamespace.model_validate(
            {
                "principal": ns.principal,
                "session": ns.session,
                "repository": ns.repository,
                "route": ns.route,
                "model_identity": ns.model_identity,
                "config_fingerprint": ns.config_fingerprint,
                "workspace": ns.workspace,
                "mode": ns.mode,
                "admission_version": ns.admission_version,
                "observation_version": ns.observation_version,
                "graph_version": ns.graph_version,
                "reference_version": ns.reference_version,
                "proof_version": ns.proof_version,
                "bounds": ns.bounds,
                "proof_bounds": ns.proof_bounds,
                "graph_bounds": ns.graph_bounds,
                "observation_bounds": ns.observation_bounds,
                "admission_namespace_key": ns.admission_namespace_key,
                "admission_scoped_key": ns.admission_scoped_key,
                "lineage_id": ns.lineage_id,
                "history_version": ns.history_version,
                "arguments_version": ns.arguments_version,
                "history_bounds": ns.history_bounds,
                "history_key": ns.history_key,
                "state_scoped_key": ns.state_scoped_key,
            }
        )
        assert d_ns.history_key == ns.history_key
        assert d_ns.state_scoped_key == ns.state_scoped_key
        assert d_ns.admission_namespace_key == ns.admission_namespace_key
        assert d_ns.admission_scoped_key == ns.admission_scoped_key
        assert ns.history_key == state.d_state.history_key
        assert ns.lineage_key == state.lineage_key
        assert (
            rram._lineage_key(  # type: ignore[attr-defined]
                ns.history_key,
                ns.contract_version,
                ns.policy_version,
                ns.root_lineage_bounds,
            )
            == ns.lineage_key
        )
        assert ns.contract_version == (
            rram.ROOT_REGION_LINEAGE_CONTRACT_VERSION  # type: ignore[attr-defined]
        )
        assert ns.policy_version == (
            rram.ROOT_REGION_LINEAGE_POLICY_VERSION  # type: ignore[attr-defined]
        )

    CausalHistoryNamespace.model_validate = model_validate_spy  # type: ignore[method-assign]
    bam._sha256_hex = sha_spy_bam  # type: ignore[attr-defined]
    chm._sha256_hex = sha_spy_chm
    rlm._sha256_hex = sha_spy_rlm  # type: ignore[attr-defined]
    rram._lineage_key = lineage_spy  # type: ignore[attr-defined]
    rram._s_json_string_escaped_ceil = ceil_spy
    try:
        # --- Positive FIRST: the pinned component reserve list.
        meter = _D2Meter(10_000_000)
        d_units, lineage_units, d_ceil = helper(meter, ns)
        assert meter.reserves == list(_U18NS_RESERVES)
        assert meter.remaining == 10_000_000 - sum(_U18NS_RESERVES)
        assert (d_units, lineage_units, d_ceil) == (26701, 1655, 2031)
        # The ACTUAL guarded target runs only after the helper.
        actual_target()
        assert visits == {
            "model_validate": 1,
            "sha_bam": 2,
            "sha_chm": 4,
            "sha_rlm": 1,
            "lineage": 1,
            "esc_ceil": 18,
        }
        # --- Exact/one-below: total-1 crosses at the FINAL
        # reservation (the charged fence and ceiling-calc phases
        # are permitted by the budget and run exactly as in the
        # positive), before any target attempt.
        visits = dict(zero_visits)
        crossing = _D2Meter(sum(_U18NS_RESERVES) - 1)
        with pytest.raises(
            ValueError,
            match="the work meter budget is exhausted before the crossing target",
        ):
            helper(crossing, ns)
        assert crossing.reserves == list(_U18NS_RESERVES)[:13]
        assert visits["esc_ceil"] == 18
        for name in ("model_validate", "sha_bam", "sha_chm", "sha_rlm", "lineage"):
            assert visits[name] == 0
        # --- Zero budget: the first reserve crosses.
        visits = dict(zero_visits)
        zero = _D2Meter(0)
        with pytest.raises(
            ValueError,
            match="the work meter budget is exhausted before the crossing target",
        ):
            helper(zero, ns)
        assert zero.reserves == []
        assert visits == zero_visits
        # --- Closed negatives (copy-only stimuli, fixed private
        # channels, exact reserve-list positions).
        visits = dict(zero_visits)
        with pytest.raises(
            ValueError,
            match="the admission parent namespace precharge reserver "
            "must carry a typed reserve callback",
        ):
            helper(None, ns)  # type: ignore[arg-type]
        with pytest.raises(
            ValueError,
            match="the admission parent namespace precharge reserver "
            "must carry a typed reserve callback",
        ):
            helper(object(), ns)  # type: ignore[arg-type]
        foreign = SimpleNamespace(**ns.model_dump())
        foreign_meter = _D2Meter(10_000_000)
        with pytest.raises(
            ValueError,
            match="the admission parent namespace must be the actual closed record",
        ):
            helper(foreign_meter, foreign)  # type: ignore[arg-type]
        assert foreign_meter.reserves == []
        field_values = {name: getattr(ns, name) for name in ns.model_fields}
        field_values.pop("principal")
        partial = type(ns).model_construct(**field_values)
        partial_meter = _D2Meter(10_000_000)
        with pytest.raises(
            ValueError,
            match="the admission parent namespace must carry the closed field set",
        ):
            helper(partial_meter, partial)
        assert partial_meter.reserves == []
        forged_key = ns.model_copy(update={"lineage_key": "z" * 64})
        key_meter = _D2Meter(10_000_000)
        with pytest.raises(
            ValueError,
            match="the carried namespace lineage_key must be a 64-hex digest",
        ):
            helper(key_meter, forged_key)
        assert key_meter.reserves == [1176]
        over = ns.model_copy(
            update={
                "graph_bounds": GraphBounds(max_path_bytes=10),
                "workspace": "/work/a/b/c/d",
            }
        )
        over_meter = _D2Meter(10_000_000)
        with pytest.raises(
            ValueError,
            match="the carried namespace workspace must be the canonical "
            "absolute POSIX path under the actual configured path bound",
        ):
            helper(over_meter, over)
        assert over_meter.reserves == []
        bool_hb = type(ns.history_bounds).model_construct(max_issuances=True)
        bool_ns = ns.model_copy(update={"history_bounds": bool_hb})
        bool_meter = _D2Meter(10_000_000)
        with pytest.raises(
            ValueError,
            match="the carried namespace history bound set must be the actual closed record",
        ):
            helper(bool_meter, bool_ns)
        assert bool_meter.reserves == []
        tag_ns = ns.model_copy(update={"contract_version": "cache-root-region-lineage/v9"})
        tag_meter = _D2Meter(10_000_000)
        with pytest.raises(
            ValueError,
            match="the carried namespace must carry the actual fixed lineage tags",
        ):
            helper(tag_meter, tag_ns)
        assert tag_meter.reserves == list(_U18NS_RESERVES)[:13]
        # The forged-tag case runs the charged ceiling-calc phase
        # (18 walks) before its refusal; the target spies stay 0.
        assert visits["esc_ceil"] == 18
        for name in ("model_validate", "sha_bam", "sha_chm", "sha_rlm", "lineage"):
            assert visits[name] == 0
    finally:
        CausalHistoryNamespace.model_validate = original_mv  # type: ignore[method-assign]
        bam._sha256_hex = original_sha_bam  # type: ignore[attr-defined]
        chm._sha256_hex = original_sha_chm
        rlm._sha256_hex = original_sha_rlm  # type: ignore[attr-defined]
        rram._lineage_key = original_lineage  # type: ignore[attr-defined]
        rram._s_json_string_escaped_ceil = original_ceil


# --- D2 u18op: the admission-parent opening fences, the actual
# inherited collection caps and the charged counting walks. ---


# The EXACT 97-reserve list of the full parent precharge on the
# fixture: the 32 pre-block-(8) values, then the ROOT row non-walk
# pool (184), the canonical-metadata component (record shape fence
# 1825, its ceiling calculation 4734, the leaf rekey
# payload/ctor/key blocks 2916/244/551 and 4150, the second
# payload/ctor/key block 2916/244/551 and the parent scope-join
# re-derivation 301), the root-content component (the target's
# repeated 64-hex and no-copy measurement passes 145/24 twice plus
# the owned encode/hash 152), the n_facts + 1 (2), n_occ (2) and
# the once-built FILE originality-index (4) reserves, then the FILE
# row at the 4154 rekey variant of the same canonical component,
# its charged helper walks 1-4 (10/14/5/3: the segment population
# closure with each segment's field/container/member-position-
# count fences before any length feeds the next reserve, the leaf
# closure re-run, the admitted-index closure and the admitted
# region metadata walk), the leaf re-run's remaining actual passes
# at their closed per-element ceilings (55/11/802/18/2/6/5/1/9/2),
# the region component's whole-bundle fast path (5/20/144: the
# closed fences, the charged character visits and the owned
# encode/hash with zero slice/join work), the partition/width
# joins (10/2), the M04 owner/witness joins at the ACTUAL carried
# owner result/piece populations (2/77/5) and the M04 owner/
# witness-join product (897238: the per-witness owner-result join
# plus the region-compatibility ceiling whose nested member-
# position walk over EVERY selected owner segment is closed at
# the carried B domain product under the per-segment count gate),
# and the (9) S-scope tail 4/30/3/817/1235.
_U18OP_RESERVES: tuple[int, ...] = (
    25,
    658,
    85,
    1,
    1758,
    1,
    437,
    20,
    597,
    148,
    323,
    1,
    3431,
    0,
    146,
    24,
    152,
    1454,
    180,
    519,
    1740,
    30,
    1440,
    4325,
    1440,
    1176,
    384,
    4877,
    1062,
    7915,
    446,
    7155,
    78,
    9678,
    361,
    4,
    2,
    1653,
    2,
    184,
    1825,
    4734,
    2916,
    244,
    2916,
    244,
    551,
    4150,
    2916,
    244,
    2916,
    244,
    551,
    301,
    145,
    24,
    145,
    24,
    152,
    2,
    2,
    4,
    1825,
    4734,
    2916,
    244,
    2916,
    244,
    551,
    4154,
    2916,
    244,
    2916,
    244,
    551,
    301,
    10,
    14,
    5,
    3,
    55,
    11,
    802,
    18,
    2,
    6,
    5,
    1,
    9,
    2,
    5,
    20,
    144,
    10,
    2,
    2,
    77,
    5,
    897238,
    4,
    38,
    3,
    817,
    24,
    251,
    1488,
)

# The exact 39 pre-block-(8) reserves (the opening gates, the
# (2)-(6) pools and the (7) namespace component): the ROOT
# row's resolved-source identity fence refuses with exactly
# this prefix.
_U18OP_PRE8: tuple[int, ...] = (
    25,
    658,
    85,
    1,
    1758,
    1,
    437,
    20,
    597,
    148,
    323,
    1,
    3431,
    0,
    146,
    24,
    152,
    1454,
    180,
    519,
    1740,
    30,
    1440,
    4325,
    1440,
    1176,
    384,
    4877,
    1062,
    7915,
    446,
    7155,
    78,
    9678,
    361,
    4,
    2,
    1653,
    2,
)


def test_d2_parent_opening_fences_caps_and_count_walk_precharge() -> None:
    """D2 u18op: the admission-parent precharge OPENING gates on the
    genuine LEAN offset fixture's actual parent components.

    Positive FIRST: the full helper on parent.state/parent.ns/
    parent.r_result/parent.g_bounds/parent.root_entry/parent.entries/
    parent.path_associations/parent.admission_reasons with a bounded
    meter pins the EXACT reserve list (106 closed ceilings; the 0 at
    index 13 is the R diagnostic sorted/dedup walk at n_rd == 0, the
    accepted F empty-input no-work law; the (5) element walks are
    reserved at 1 + 11*n_qw and at the ACTUAL fact/provenance field
    tuple widths BEFORE they run, with every element fenced to its
    actual closed class/fields and each fact provenance to the
    actual closed union before its call id is read; the e_overlay
    re-run is reserved at its ACTUAL six-header/text/64-hex/bound/
    workspace-check recipe with no tuple walk), and the charged
    occurrence counting walk makes exactly n_occ == 2 element visits
    on a negative-only copied occurrences container.  The negative-only
    controls (originals never wrapped or mutated): the zero budget
    exhausts before the first reserve;
    the actual inherited entry/association/piece/member caps at
    stricter carried copies refuse with their exact fixed private
    errors at the actual reserve points (the entry/association O(1)
    gates before the first reservation, the per-proof pieces gate
    after the occurrence-walk reserve, the member-total gate after
    the entry-walk reserve); the field-existence fences and the
    foreign-class fence refuse before any reservation; the corrupted
    nested occurrence consumes the charged walk reserve, then
    refuses after exactly one element visit; the (5) element
    fences and the fact provenance union fence each refuse with
    their exact fixed private error after their charged walk
    reserves, and a negative-only copied E overlay with a None
    workspace text field refuses with the ACTUAL fixed four-text
    shape error BEFORE its own length calculation and
    reservation, and the ROOT row's leaf re-run reuses the
    ACTUAL root-content and canonical-metadata components
    (the resolved-source identity fence first, the record's
    closed O(1) shape gate before any character walk); the
    FILE row reuses the same canonical component at its 4154
    rekey variant, its closed B-domain population caps, its
    entry field-existence fence before any proof dereference,
    its charged helper walks 1-4 (the walk-1 per-segment
    field/container/member-position-count closures before any
    length feeds the walk-2 reservation) and the region
    component's whole-bundle fast path at the entry's own
    carried B domain, with the M04 owner/witness joins and the
    owner/witness-join product closed at the ACTUAL carried
    owner-domain populations and the inherited B segment/member
    ceilings (the region-compatibility nested member-position
    walk over every selected owner segment included under the
    per-segment count gate).  The negative-only (j)-(m)
    controls pin those closures: the FILE entry's missing field
    and the segment's missing or over-domain member positions
    refuse at their exact fixed private channels after exactly
    the charged prefixes, and the exact/one-below budgets at
    the M04 owner/witness-join product crossing stop before the
    first tail reservation.  The F currentness /
    F graph / E currentness scope keys are reserved at
    their ACTUAL JSON-array recipes (brackets, separators,
    quote pairs and the ensure_ascii escaped bodies, the
    embedded bound-set JSON strings with their escaped key
    quotes, and the precharge's own ceiling calculations
    reserved before their walks), the reverse-index footer's
    per-row expected key-set sort at its closed bound and the
    model scope key's inner G-bounds dump at its charged
    dump walk; no whole-operation or public-consumer claim.
    """
    ns, state, r, g, root_entry, _files, parent = _offset_component()
    n_occ = len(state.d_state.occurrences)
    n_e = len(parent.entries)
    n_rows = len(parent.path_associations)
    assert (n_occ, n_e, n_rows) == (2, 1, 2)

    def state_hash() -> str:
        return hashlib.sha256(
            json.dumps(state.model_dump(mode="json"), sort_keys=True).encode("ascii")
        ).hexdigest()

    original_hash = state_hash()

    def call(meter: _D2Meter, **overrides: Any) -> None:
        rram._s_parent_precharge_closed(
            meter,
            overrides.get("state", parent.state),
            overrides.get("ns", parent.ns),
            overrides.get("r_result", parent.r_result),
            overrides.get("g_bounds", parent.g_bounds),
            overrides.get("root_entry", parent.root_entry),
            overrides.get("entries", parent.entries),
            overrides.get("path_associations", parent.path_associations),
            overrides.get("admission_reasons", parent.admission_reasons),
        )

    # --- (a) POSITIVE first: the exact bounded reserve list.
    meter = _D2Meter(10_000_000)
    call(meter)
    assert meter.reserves == list(_U18OP_RESERVES)
    assert sum(meter.reserves) == 1004989
    assert meter.remaining == 10_000_000 - 1004989

    # The charged occurrence counting walk: exactly n_occ element
    # visits on a negative-only copied occurrences container.
    _CountingTuple.visits = 0
    _CountingTuple.index_visits = 0
    d_copy = state.d_state.model_copy(
        update={"occurrences": _CountingTuple(state.d_state.occurrences)}
    )
    st_copy = state.model_copy(update={"d_state": d_copy})
    meter2 = _D2Meter(10_000_000)
    call(meter2, state=st_copy)
    assert meter2.reserves == list(_U18OP_RESERVES)
    assert _CountingTuple.visits == n_occ

    # --- (b) zero budget: exhausts before the first reserve.
    zero = _D2Meter(0)
    with pytest.raises(
        ValueError,
        match="the work meter budget is exhausted before the crossing target",
    ):
        call(zero)
    assert zero.reserves == []

    def refused(
        budget: int,
        expected: str,
        reserves: list[int],
        **overrides: Any,
    ) -> None:
        m = _D2Meter(budget)
        with pytest.raises(ValueError, match=expected):
            call(m, **overrides)
        assert m.reserves == reserves

    # --- (c) the actual inherited caps at stricter carried copies.
    refused(
        0,
        "the retained entry count exceeds the actual inherited entry cap",
        [],
        ns=ns.model_copy(update={"bounds": BundleAdmissionBounds(max_entries=1)}),
    )
    refused(
        0,
        "the retained association count exceeds the actual inherited cap",
        [],
        ns=ns.model_copy(update={"bounds": BundleAdmissionBounds(max_reverse_associations=1)}),
    )
    refused(
        10_000_000,
        "the retained proof piece total exceeds the actual inherited history cap",
        [25],
        ns=ns.model_copy(update={"history_bounds": HistoryBounds(max_retained_pieces=1)}),
    )
    # Per-proof pieces closure: a negative-only 2-piece proof first
    # in the copied occurrence container.
    occ0 = state.d_state.occurrences[0]
    proof0 = copy.deepcopy(occ0.proof)
    proof2 = proof0.model_copy(update={"pieces": proof0.pieces + proof0.pieces[:1]})
    occ2 = copy.deepcopy(occ0).model_copy(update={"proof": proof2})
    d2 = state.d_state.model_copy(update={"occurrences": (occ2,) + state.d_state.occurrences})
    st2 = state.model_copy(update={"d_state": d2})
    refused(
        10_000_000,
        "the retained proof pieces exceed the actual inherited history piece cap",
        [37],
        state=st2,
        ns=ns.model_copy(update={"history_bounds": HistoryBounds(max_retained_pieces=1)}),
    )
    _CountingTuple.visits = 0
    refused(
        10_000_000,
        "the retained member total exceeds the actual inherited member cap",
        [25, 658],
        ns=ns.model_copy(update={"bounds": BundleAdmissionBounds(max_member_occurrences=1)}),
        entries=_CountingTuple(parent.entries),
    )
    assert _CountingTuple.visits == 1
    _CountingTuple.visits = 0

    # --- (d) field-existence fences (0 reserves): a field never
    # set on a real-class copy refuses with the fixed private
    # error before any dereference, count or reservation.
    st3 = copy.deepcopy(state)
    del st3.__dict__["d_state"]
    refused(
        0,
        "the admission parent state must carry the closed field set",
        [],
        state=st3,
    )
    r3 = copy.deepcopy(r)
    del r3.__dict__["resolved_source"]
    refused(
        0,
        "the admission parent R result must carry its closed identity fields",
        [],
        r_result=r3,
    )

    # --- (e) foreign class (0 reserves).
    refused(
        0,
        "the admission parent state must be the actual closed state record",
        [],
        state=SimpleNamespace(d_state=state.d_state, root_facts=state.root_facts),
    )

    # --- (f) corrupted nested occurrence: the charged walk reserve
    # is recorded, then the per-element fence refuses after exactly
    # one element visit.
    _CountingTuple.visits = 0
    d4 = state.d_state.model_copy(
        update={"occurrences": _CountingTuple((SimpleNamespace(proof=None),))}
    )
    st4 = state.model_copy(update={"d_state": d4})
    refused(
        10_000_000,
        "the retained occurrence must be the actual closed record",
        [13],
        state=st4,
    )
    assert _CountingTuple.visits == 1

    # --- (g) exact/one-below at the FIRST-WALK and ENTRY-WALK
    # reserve boundaries, with reset counting tuples on BOTH
    # containers proving which walk actually started: budget 24
    # crosses the first reserve before any walk (0 visits);
    # budget 25 pays the first walk exactly (2 occurrence
    # yields) and then crosses the entry-walk reserve before the
    # entry walk starts (still 2 visits); budget 682 (25 + 658
    # minus one) crosses the entry-walk reserve the same way;
    # budget 683 pays both walks (2 + 1 yields) and crosses the
    # next (phase-2 shape) reserve at 85.
    def boundary(
        budget: int,
        expected_reserves: list[int],
        expected_visits: int,
    ) -> None:
        _CountingTuple.visits = 0
        _CountingTuple.index_visits = 0
        d_b = state.d_state.model_copy(
            update={"occurrences": _CountingTuple(state.d_state.occurrences)}
        )
        st_b = state.model_copy(update={"d_state": d_b})
        m = _D2Meter(budget)
        with pytest.raises(
            ValueError,
            match="the work meter budget is exhausted before the crossing target",
        ):
            call(m, state=st_b, entries=_CountingTuple(parent.entries))
        assert m.reserves == expected_reserves
        assert _CountingTuple.visits == expected_visits

    boundary(24, [], 0)
    boundary(25, [25], 2)
    boundary(682, [25], 2)
    boundary(683, [25, 658], 3)

    # --- (h) the (5) element fences and the fact provenance union
    # fence (negative-only copied R results; originals untouched):
    # a foreign nested witness refuses after the charged
    # witness-walk reserve (1 + 11 over the copied count of one),
    # a foreign nested P fact refuses after the q reserves and the
    # charged fact-walk reserve (the actual fact/provenance widths
    # over the copied count of two, after the one genuine fact was
    # visited), and a foreign or partial fact provenance refuses at
    # the union / variant-field fence after the charged fact-walk
    # reserve, never reaching the call-id read.  A negative-only
    # copied E overlay with a None workspace text field refuses
    # at the ACTUAL four-text shape fence before its length
    # calculation and reservation (the first ten positive
    # reserves, then the fixed error).
    q = parent.r_result.q_result
    psel = q.p_selection
    q_w = q.model_copy(
        update={"uncertainty_witnesses": q.uncertainty_witnesses + (SimpleNamespace(),)}
    )
    refused(
        10_000_000,
        "the retained uncertainty witness must be the actual closed record",
        [25, 658, 85, 1, 1758, 12],
        r_result=r.model_copy(update={"q_result": q_w}),
    )
    psel_f = psel.model_copy(update={"witness_facts": psel.witness_facts + (SimpleNamespace(),)})
    q_f = q.model_copy(update={"p_selection": psel_f})
    refused(
        10_000_000,
        "the retained P selection fact must be the actual closed record",
        [25, 658, 85, 1, 1758, 1, 437, 39],
        r_result=r.model_copy(update={"q_result": q_f}),
    )
    fact0_f = copy.deepcopy(psel.witness_facts[0]).model_copy(
        update={"provenance": SimpleNamespace()}
    )
    psel_p = psel.model_copy(update={"witness_facts": (fact0_f,) + psel.witness_facts[1:]})
    q_p = q.model_copy(update={"p_selection": psel_p})
    refused(
        10_000_000,
        "the retained fact provenance must be the actual closed union",
        [25, 658, 85, 1, 1758, 1, 437, 20],
        r_result=r.model_copy(update={"q_result": q_p}),
    )
    prov0 = psel.witness_facts[0].provenance
    prov_partial = type(prov0).model_construct(kind="envelope")
    fact1 = psel.witness_facts[0].model_copy(update={"provenance": prov_partial})
    psel_p2 = psel.model_copy(update={"witness_facts": (fact1,) + psel.witness_facts[1:]})
    q_p2 = q.model_copy(update={"p_selection": psel_p2})
    refused(
        10_000_000,
        "the retained fact provenance must carry its closed variant fields",
        [25, 658, 85, 1, 1758, 1, 437, 20],
        r_result=r.model_copy(update={"q_result": q_p2}),
    )

    e0 = parent.r_result.e_overlay
    e_neg = e0.model_copy(update={"workspace": None})
    refused(
        10_000_000,
        "the E overlay context fields must be closed text",
        [25, 658, 85, 1, 1758, 1, 437, 20, 597, 148],
        r_result=r.model_copy(update={"e_overlay": e_neg}),
    )

    # --- (i) the ROOT row's resolved-source identity fence:
    # negative-only copied root entries with a missing or
    # foreign (valid by-value, different-instance) resolved
    # source refuse at the ACTUAL target's first root-source
    # gate, before any block-(8) fence-pool reservation or
    # content character walk (exactly the 39 pre-block-(8)
    # reserves, then the fixed error).
    root_none = parent.root_entry.model_copy(update={"root_source": None})
    refused(
        10_000_000,
        "the root entry carries the actual R resolved source by identity",
        list(_U18OP_PRE8),
        root_entry=root_none,
    )
    root_foreign = parent.root_entry.model_copy(
        update={"root_source": parent.r_result.resolved_source.model_copy()}
    )
    refused(
        10_000_000,
        "the root entry carries the actual R resolved source by identity",
        list(_U18OP_PRE8),
        root_entry=root_foreign,
    )

    # --- (j) the FILE entry field-existence fence (the leaf's
    # exact channel): a negative-only real-class entry copy
    # missing one closed field refuses before any proof
    # dereference, after exactly the 62 charged reserves up to
    # the once-built FILE originality index.
    entry_j = copy.deepcopy(_files[0])
    del entry_j.__dict__["witnesses"]
    refused(
        10_000_000,
        "the admission entry must carry its closed fields",
        list(_U18OP_RESERVES[:62]),
        entries=(entry_j,),
    )

    # --- (k) the walk-1 segment field-existence closure: a
    # negative-only segment copy missing member_positions
    # refuses after the charged walk-1 reserve, before any
    # member-position length feeds the walk-2 reservation.
    entry_k = copy.deepcopy(_files[0])
    proof_k = entry_k.proof
    assert proof_k is not None
    segment_k = proof_k.segments[0]
    del segment_k.__dict__["member_positions"]
    refused(
        10_000_000,
        "the retained proof segments must carry their closed metadata",
        list(_U18OP_RESERVES[:77]),
        entries=(entry_k,),
    )

    # --- (l) the walk-1 member-position count closure: a
    # negative-only segment with two member positions against
    # the entry's single requested occurrence refuses before
    # the over-domain length feeds the walk-2 reservation.
    entry_l = copy.deepcopy(_files[0])
    proof_l = entry_l.proof
    assert proof_l is not None
    segment_l = proof_l.segments[0].model_copy(update={"member_positions": (0, 0)})
    entry_l = entry_l.model_copy(
        update={"proof": proof_l.model_copy(update={"segments": (segment_l,)})}
    )
    refused(
        10_000_000,
        "segment member positions exceed the actual requested occurrence domain before any walk",
        list(_U18OP_RESERVES[:77]),
        entries=(entry_l,),
    )

    # --- (m) exact/one-below at the M04 owner/witness-join
    # product: one below the crossing pays every reserve up to
    # the M04 owner-join reserves and refuses at the product
    # itself (no tail reserve runs), while the exact crossing
    # pays the product and refuses at the first tail
    # reservation.
    m04_product = _U18OP_RESERVES[-6]
    pre = sum(_U18OP_RESERVES[:-6])
    m_below = _D2Meter(pre + m04_product - 1)
    with pytest.raises(
        ValueError,
        match="the work meter budget is exhausted before the crossing target",
    ):
        call(m_below)
    assert m_below.reserves == list(_U18OP_RESERVES[:-6])
    m_exact = _D2Meter(pre + m04_product)
    with pytest.raises(
        ValueError,
        match="the work meter budget is exhausted before the crossing target",
    ):
        call(m_exact)
    assert m_exact.reserves == list(_U18OP_RESERVES[:-5])

    # --- (n) the carried Q state's lineage-key field-
    # existence fence: a negative-only real-class state copy
    # with the field never set refuses with the fixed private
    # error before any dereference, count or reservation.
    rq = copy.deepcopy(r)
    st_q = copy.deepcopy(rq.q_result.state)
    del st_q.__dict__["lineage_key"]
    refused(
        0,
        "the carried Q state must carry its closed lineage key field",
        [],
        r_result=rq.model_copy(update={"q_result": rq.q_result.model_copy(update={"state": st_q})}),
    )

    # --- (o) the carried F graph headers close under the
    # ORIGINAL graph length law (workspace 1..1024, version
    # texts 1..128, the 64-hex identity keys exactly 64) at
    # the opening, before the first reservation.
    fg_o = parent.r_result.f_result.overlay
    refused(
        0,
        "the carried F graph workspace must carry closed bounded text",
        [],
        r_result=r.model_copy(
            update={
                "f_result": r.f_result.model_copy(
                    update={"overlay": fg_o.model_copy(update={"workspace": "w" * 1025})}
                )
            }
        ),
    )
    refused(
        0,
        "the carried F graph identity keys must carry closed 64-length text",
        [],
        r_result=r.model_copy(
            update={
                "f_result": r.f_result.model_copy(
                    update={"overlay": fg_o.model_copy(update={"history_key": "ab" * 31})}
                )
            }
        ),
    )
    refused(
        0,
        "the carried F graph scope headers must carry closed bounded text",
        [],
        r_result=r.model_copy(
            update={
                "f_result": r.f_result.model_copy(
                    update={"overlay": fg_o.model_copy(update={"graph_version": "g" * 129})}
                )
            }
        ),
    )

    # --- (p) the carried E overlay headers close under the
    # ORIGINAL overlay caps at the phase-2 fence (after the
    # opening + Q/F pools, before the E reservation).
    eo_p = parent.r_result.e_overlay
    refused(
        10_000_000,
        "the carried E overlay workspace must carry closed bounded text",
        list(_U18OP_RESERVES[:10]),
        r_result=r.model_copy(
            update={"e_overlay": eo_p.model_copy(update={"workspace": "w" * 1025})}
        ),
    )
    refused(
        10_000_000,
        "the carried E overlay policy version must carry closed bounded text",
        list(_U18OP_RESERVES[:10]),
        r_result=r.model_copy(
            update={"e_overlay": eo_p.model_copy(update={"policy_version": "p" * 129})}
        ),
    )
    refused(
        10_000_000,
        "the carried E overlay history key must carry closed 64-length text",
        list(_U18OP_RESERVES[:10]),
        r_result=r.model_copy(
            update={"e_overlay": eo_p.model_copy(update={"history_key": "ab" * 31})}
        ),
    )

    # --- (q) the JSON-array ceiling bounds the ACTUAL
    # ensure_ascii serializer for a genuinely constructed
    # non-BMP/escaped workspace: the astral codepoint escapes
    # at 12 characters (the old four-bytes-per-character
    # ceiling cannot bound it), and the closed 6-element
    # ceiling is at least the actual recipe output.
    assert rram._s_json_string_escaped_ceil("\U0001f600") == 12
    assert rram._s_json_string_escaped_ceil("\u2028") == 6
    assert rram._s_json_string_escaped_ceil('"') == 2
    assert rram._s_json_string_escaped_ceil("\\") == 2
    assert rram._s_json_string_escaped_ceil("a") == 1
    ws_nb = 'w-"\\\u2028\U0001f600".md'
    bounds_nb = CurrentnessBounds()
    hk_nb = "ab" * 32
    sk_nb = currentness_scope_key(hk_nb, ws_nb, CURRENTNESS_POLICY_VERSION, bounds_nb)
    ov_nb = CurrentnessOverlay(
        history_key=hk_nb,
        revision=0,
        workspace=ws_nb,
        policy_version=CURRENTNESS_POLICY_VERSION,
        bounds=bounds_nb,
        scope_key=sk_nb,
        emitted_reasons=0,
    )
    assert ov_nb.scope_key == sk_nb
    # The mixed workspace's escaped body is the exact
    # per-character sum (five plain ASCII, two quotes,
    # one backslash, one BMP, one astral codepoint).
    assert rram._s_json_string_escaped_ceil(ws_nb) == 29
    # An all-astral workspace shows the property the old
    # four-bytes-per-character ceiling misses: the
    # ensure_ascii JSON body is twelve characters per
    # codepoint, beyond any 4 * len(character) bound.
    ws_astral = "\U0001f600" * 4
    assert rram._s_json_string_escaped_ceil(ws_astral) == 48
    assert rram._s_json_string_escaped_ceil(ws_astral) > 4 * len(ws_astral)
    nf_nb = len(CurrentnessBounds.model_fields)
    ceil_nb = (
        2
        + 5
        + 2
        + rram._s_json_string_escaped_ceil(CURRENTNESS_CONTRACT_VERSION)
        + 2
        + rram._s_json_string_escaped_ceil(CURRENTNESS_POLICY_VERSION)
        + 2
        + rram._s_json_string_escaped_ceil(OPAQUE_GROUP_RECIPE_VERSION)
        + 2
        + rram._s_json_string_escaped_ceil(hk_nb)
        + 2
        + rram._s_json_string_escaped_ceil(ws_nb)
        + 2
        + rram._s_bound_set_json_len(bounds_nb)
        + 2 * nf_nb
    )
    actual_nb = len(
        json.dumps(
            [
                CURRENTNESS_CONTRACT_VERSION,
                CURRENTNESS_POLICY_VERSION,
                OPAQUE_GROUP_RECIPE_VERSION,
                hk_nb,
                ws_nb,
                json.dumps(
                    bounds_nb.model_dump(mode="json"),
                    sort_keys=True,
                    separators=(",", ":"),
                ),
            ],
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    )
    assert ceil_nb >= actual_nb

    # The fixture's own F/E target reserves cover at least the
    # target's three length-proportional passes (dumps,
    # encode, SHA read) over the ACTUAL recipe serialization.
    fg_q = parent.r_result.f_result.overlay
    eo_q = parent.r_result.e_overlay
    fcur_actual = len(
        json.dumps(
            [
                CURRENTNESS_CONTRACT_VERSION,
                fg_q.currentness_policy_version,
                OPAQUE_GROUP_RECIPE_VERSION,
                fg_q.history_key,
                fg_q.workspace,
                json.dumps(
                    fg_q.currentness_bounds.model_dump(mode="json"),
                    sort_keys=True,
                    separators=(",", ":"),
                ),
            ],
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    )
    fgr_actual = len(
        json.dumps(
            [
                fg_q.contract_version,
                fg_q.policy_version,
                fg_q.graph_version,
                fg_q.reference_version,
                fg_q.proof_version,
                fg_q.currentness_contract_version,
                fg_q.currentness_policy_version,
                fg_q.currentness_recipe_version,
                fg_q.history_key,
                fg_q.workspace,
                fg_q.root_digest,
                fg_q.currentness_scope_key,
                json.dumps(
                    fg_q.bounds.model_dump(mode="json"),
                    sort_keys=True,
                    separators=(",", ":"),
                ),
                json.dumps(
                    fg_q.currentness_bounds.model_dump(mode="json"),
                    sort_keys=True,
                    separators=(",", ":"),
                ),
                json.dumps(
                    fg_q.graph_bounds.model_dump(mode="json"),
                    sort_keys=True,
                    separators=(",", ":"),
                ),
            ],
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    )
    e_actual = len(
        json.dumps(
            [
                CURRENTNESS_CONTRACT_VERSION,
                eo_q.policy_version,
                OPAQUE_GROUP_RECIPE_VERSION,
                eo_q.history_key,
                eo_q.workspace,
                json.dumps(
                    eo_q.bounds.model_dump(mode="json"),
                    sort_keys=True,
                    separators=(",", ":"),
                ),
            ],
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    )
    assert _U18OP_RESERVES[22] >= 3 * fcur_actual
    assert _U18OP_RESERVES[23] >= 3 * fgr_actual
    assert _U18OP_RESERVES[24] >= 3 * e_actual

    # The exact/one-below budgets at the F currentness
    # scope-key target reserve: one below pays every reserve
    # up to that target and refuses before it (the F graph /
    # E target reservations never run); exact pays it and
    # refuses at the next reservation.
    fcur_target = _U18OP_RESERVES[22]
    fcur_pre = sum(_U18OP_RESERVES[:22])
    fcur_below = _D2Meter(fcur_pre + fcur_target - 1)
    with pytest.raises(
        ValueError,
        match="the work meter budget is exhausted before the crossing target",
    ):
        call(fcur_below)
    assert fcur_below.reserves == list(_U18OP_RESERVES[:22])
    fcur_exact = _D2Meter(fcur_pre + fcur_target)
    with pytest.raises(
        ValueError,
        match="the work meter budget is exhausted before the crossing target",
    ):
        call(fcur_exact)
    assert fcur_exact.reserves == list(_U18OP_RESERVES[:23])

    # The originals stay untouched.
    assert state_hash() == original_hash


# --- E. Independent source-scale component outcome records ------------


# --- E. Independent source-scale component outcome records ------------


def _s_e_component_costs(
    state: Any,
    ns: Any,
    r: Any,
    g: Any,
    root_entry: Any,
    parent: Any,
) -> dict[str, int]:
    """The actually measured S component costs of ONE ready shape,
    each component on its OWN fresh bounded caller meter (the
    separate component precharge contracts): the root-content
    owned passes, the canonical metadata rekey, the FILE
    admitted-span owned passes (the ACTUAL admitted spans, never
    a whole-cap reservation), and the admission-parent re-run.
    The reservations are WORK meters, never size caps; the record
    labels the actual component each total belongs to (no
    whole-operation fit claim)."""
    resolved = r.resolved_source
    assert resolved is not None
    costs: dict[str, int] = {}
    m_root = _D2Meter(10_000_000)
    _s_root_content_precharge_closed(
        m_root, resolved.root_text, resolved.root_digest, resolved.root_byte_length
    )
    assert m_root.reserves
    costs["root_content"] = sum(m_root.reserves)
    m_meta = _D2Meter(10_000_000)
    _s_canonical_metadata_precharge_closed(m_meta, root_entry.key_record, ns)
    assert m_meta.reserves
    costs["canonical_metadata"] = sum(m_meta.reserves)
    file_region_total = 0
    for entry in parent.entries:
        proof = entry.proof
        assert proof is not None
        admitted = set(entry.admitted_segments)
        region_chars = sum(seg.char_length for i, seg in enumerate(proof.segments) if i in admitted)
        region_bytes = sum(seg.byte_length for i, seg in enumerate(proof.segments) if i in admitted)
        m_reg = _D2Meter(10_000_000)
        _s_region_precharge_closed(
            m_reg,
            proof.source_text,
            proof.segments,
            entry.admitted_segments,
            region_chars,
            region_bytes,
            entry.key_record.graph_bounds.max_single_source_bytes,
            entry.key_record.proof_bounds,
        )
        assert m_reg.reserves
        file_region_total += sum(m_reg.reserves)
    costs["file_region_total"] = file_region_total
    m_par = _D2Meter(10_000_000)
    _s_parent_precharge_closed(
        m_par,
        state,
        ns,
        r,
        g,
        root_entry,
        parent.entries,
        parent.path_associations,
        parent.admission_reasons,
    )
    assert m_par.reserves
    costs["parent"] = sum(m_par.reserves)
    return costs


def _s_e_record(
    shape: str,
    mode: Any,
    endpoint: str | None,
    nbytes: int,
    r_outcome: str,
    costs: dict[str, int] | None = None,
    extra: dict[str, Any] | None = None,
) -> None:
    """One honest per-shape outcome record line (size, outcome,
    labeled component costs, domain facts) into the test output."""
    rec: dict[str, Any] = {
        "shape": shape,
        "mode": mode.value,
        "endpoint": endpoint,
        "root_bytes": nbytes,
        "r_outcome": r_outcome,
    }
    if costs is not None:
        rec["component_costs"] = costs
    if extra:
        rec.update(extra)
    print("e-record " + json.dumps(rec, sort_keys=True))


def _s_e_mixed_state(
    mode: Any,
    endpoint: str,
    lineage: str,
    nbytes: int,
    graph_bounds: GraphBounds | None = None,
) -> tuple[Any, Any]:
    """ONE genuine public P mixed-region (no singleton) state whose
    selected root region references A.md (the intended eligibility:
    the root region references the dependency the same batch
    reads), at the given root-member byte scale."""
    header = "Follow `A.md`.\n"
    body = header + "x" * (nbytes - len(header))
    assert len(body.encode("utf-8")) == nbytes
    if graph_bounds is None:
        ns, s0 = r_bootstrap(mode, lineage)
    else:
        ns, s0 = r_bootstrap(mode, lineage, graph_bounds=graph_bounds)
    t1 = r_issue(s0, ns, "m1", endpoint, (CAUSAL_ROOT_FACT,), MIX_CMD)
    assert t1.outcome.value == "accepted", t1.diagnostics
    s_m = r_observe(
        t1.state,
        ns,
        (read_request(endpoint, "m1", _mixed_body(A_TEXT, MARK, body), MIX_CMD),),
    ).state
    return ns, s_m


@pytest.mark.parametrize("mode", MODES)
def test_e_root_only_scale_outcomes_and_costs(mode: Any) -> None:
    """E: the root-only (envelope) scale outcome at 32768/65536/
    131072 UTF-8 bytes (both modes): actual READY at 32768/65536
    with the actual component construction and the measured
    labeled component costs (root content, canonical metadata,
    parent), monotone in the actual source bytes; 131072 is
    recorded HONESTLY as the actual R-total refusal (the F ok
    retained, no usable source, no positive model component
    manufactured).  The original single-source/entry-byte size
    domains are recorded as size domains, never reinterpreted as
    work."""
    costs: dict[int, dict[str, int]] = {}
    for nbytes in (32768, 65536, 131072):
        body = "x" * nbytes
        assert len(body.encode("utf-8")) == nbytes
        if nbytes <= 65536:
            ns, s, r, g, _key_record, root_entry, parent = _s_parent(
                mode, f"s-e-ro-{mode.value}-{nbytes}", root_body=body
            )
            resolved = r.resolved_source
            assert resolved is not None and resolved.kind == "envelope"
            assert resolved.root_byte_length == nbytes
            assert resolved.root_digest == _sha256_hex(body.encode("utf-8"))
            assert parent.state is s and parent.ns is ns and parent.r_result is r
            assert parent.root_entry is root_entry
            # the original size domains in force (never work):
            assert ns.graph_bounds.max_single_source_bytes == 1_000_000
            assert g.max_total_entry_source_bytes == 16_777_216
            assert nbytes <= g.max_total_entry_source_bytes
            measured = _s_e_component_costs(s, ns, r, g, root_entry, parent)
            costs[nbytes] = measured
            _s_e_record(
                "root_only",
                mode,
                None,
                nbytes,
                r.outcome.value,
                measured,
                {
                    "single_source_cap": ns.graph_bounds.max_single_source_bytes,
                    "entry_byte_cap": g.max_total_entry_source_bytes,
                },
            )
        else:
            ns, s = r_bootstrap(mode, f"s-e-ro-{mode.value}-{nbytes}", root_body=body)
            r = derive_root_region_graph(s, ns)
            # honest refusal record: the actual R-total crossing
            # AFTER the F phase; no usable source, no component.
            assert r.state is s
            assert r.outcome is RootRegionGraphOutcome.REFUSED
            assert r.diagnostics == (RootRegionGraphDiagnostic.WORK_UNITS_OVER_BOUND,)
            assert r.resolved_source is None
            assert r.f_result is not None and r.f_result.outcome is CurrentGraphOutcome.OK
            assert r.q_result is not None
            assert r.q_result.outcome is RootRegionCurrentnessOutcome.READY
            _s_e_record(
                "root_only",
                mode,
                None,
                nbytes,
                r.outcome.value,
                None,
                {
                    "single_source_cap": ns.graph_bounds.max_single_source_bytes,
                    "f_retained": "ok",
                    "usable_source": False,
                },
            )
    # measured labeled component costs monotone in actual source
    # bytes (the same shape/mode; the bytes are the measured input):
    assert costs[65536]["root_content"] > costs[32768]["root_content"]
    assert costs[65536]["parent"] > costs[32768]["parent"]
    assert costs[65536]["canonical_metadata"] == costs[32768]["canonical_metadata"]


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_e_mixed_region_no_singleton_scale_outcomes_and_costs(mode: Any, endpoint: str) -> None:
    """E: the mixed-region no-singleton scale outcome at 32768/
    65536/131072 UTF-8 bytes (both modes, BOTH read endpoints),
    the selected root region referencing the same-batch A.md
    read (the intended eligibility in BOTH modes).  The honest
    original-domain record: the source SIZE domains accept the
    scale, but the ORIGINAL default admission stage-work domain
    (GraphBounds.max_work_units 65536) exhausts on the actual
    root-member admitted span (typed refusal, no partial
    component); a LEGAL instance of that original stage domain
    (within the original hard range) carries the component and
    its measured labeled costs are recorded.  131072 is the
    honest actual R-total refusal BEFORE F (no F result
    retained)."""
    legal_stage = GraphBounds(max_work_units=1_048_576)
    costs: dict[int, dict[str, int]] = {}
    for nbytes in (32768, 65536, 131072):
        if nbytes <= 65536:
            # (a) the ORIGINAL default stage-work domain: the
            # actual G assembly refuses before any partial
            # component (the typed stage exhaustion):
            ns, s_m = _s_e_mixed_state(
                mode, endpoint, f"s-e-mx-{mode.value}-{endpoint}-{nbytes}", nbytes
            )
            r = derive_root_region_graph(s_m, ns)
            assert r.state is s_m
            assert r.outcome is RootRegionGraphOutcome.READY
            resolved = r.resolved_source
            assert resolved is not None and resolved.kind == "read_region"
            assert resolved.root_byte_length == nbytes
            assert ns.graph_bounds.max_single_source_bytes == 1_000_000
            assert nbytes <= ns.graph_bounds.max_single_source_bytes
            with pytest.raises(_GOverflow) as excinfo:
                _s_parent_from_assembly(ns, s_m, r, CurrentAdmissionBounds())
            assert excinfo.value.limitation is (
                CurrentAdmissionLimitation.ADMISSION_WORK_UNITS_EXHAUSTED
            )
            _s_e_record(
                "mixed_region",
                mode,
                endpoint,
                nbytes,
                r.outcome.value,
                None,
                {
                    "stage_domain": "default",
                    "stage_cap": ns.graph_bounds.max_work_units,
                    "component_outcome": "admission_work_units_exhausted",
                },
            )
            # (b) the LEGAL instance of the original stage domain
            # (a value inside the original hard range 1..10,000,
            # 000): the component is carried and its actual
            # labeled costs are recorded:
            ns2, s_m2 = _s_e_mixed_state(
                mode,
                endpoint,
                f"s-e-mx-{mode.value}-{endpoint}-{nbytes}-stage",
                nbytes,
                graph_bounds=legal_stage,
            )
            r2 = derive_root_region_graph(s_m2, ns2)
            assert r2.outcome is RootRegionGraphOutcome.READY
            g = CurrentAdmissionBounds()
            key_record, root_entry, file_entries, rows, _attempts, _member_occ, parent = (
                _s_parent_from_assembly(ns2, s_m2, r2, g)
            )
            assert parent.state is s_m2 and parent.ns is ns2 and parent.r_result is r2
            assert len(file_entries) == 1
            assert [row.path for row in rows] == ["A.md", ROOT_FILENAME]
            measured = _s_e_component_costs(s_m2, ns2, r2, g, root_entry, parent)
            costs[nbytes] = measured
            _s_e_record(
                "mixed_region",
                mode,
                endpoint,
                nbytes,
                r2.outcome.value,
                measured,
                {
                    "stage_domain": "legal_instance",
                    "stage_cap": ns2.graph_bounds.max_work_units,
                    "entries_retained": parent.entries_retained,
                    "member_occurrences_charged": parent.member_occurrences_charged,
                    "reverse_association_attempts": parent.reverse_association_attempts,
                },
            )
        else:
            ns, s_m = _s_e_mixed_state(
                mode, endpoint, f"s-e-mx-{mode.value}-{endpoint}-{nbytes}", nbytes
            )
            r = derive_root_region_graph(s_m, ns)
            assert r.outcome is RootRegionGraphOutcome.REFUSED
            assert r.diagnostics == (RootRegionGraphDiagnostic.WORK_UNITS_OVER_BOUND,)
            assert r.resolved_source is None
            assert r.f_result is None
            assert r.q_result is not None
            assert r.q_result.outcome is RootRegionCurrentnessOutcome.READY
            _s_e_record(
                "mixed_region",
                mode,
                endpoint,
                nbytes,
                r.outcome.value,
                None,
                {"f_retained": None, "usable_source": False},
            )
    # measured labeled component costs monotone in actual source
    # bytes (the same shape/mode/endpoint/stage domain):
    assert costs[65536]["root_content"] > costs[32768]["root_content"]
    assert costs[65536]["file_region_total"] > costs[32768]["file_region_total"]
    assert costs[65536]["parent"] > costs[32768]["parent"]


def _s_e_read(state: Any, ns: Any, cid: str, endpoint: str, path: str, body: str) -> Any:
    """One genuine dependency read (issuance then observation) on
    the given endpoint."""
    issued = r_issue(state, ns, cid, endpoint, (CAUSAL_ROOT_FACT,), f"cat {path}")
    assert issued.outcome.value == "accepted", issued.diagnostics
    obs = r_observe(
        issued.state,
        ns,
        (read_request(endpoint, cid, body, f"cat {path}"),),
    )
    assert obs.outcome.value == "accepted", obs.diagnostics
    return obs.state


def _s_e_multi_dep_state(
    mode: Any, endpoint: str, lineage: str, graph_bounds: GraphBounds | None = None
) -> Any:
    """The genuine multi-dependency / version-history shape at the
    32768 root-member byte scale: root v1 references A.md and
    X.md, the dependency reads are genuine, and the
    version-history whole-root read v2 (32768 bytes) is the
    selected newer root."""
    header = "Follow `A.md` and `X.md`.\n"
    v1 = header + "x" * (32768 - len(header))
    v2_header = header + "Version two.\n"
    v2 = v2_header + "x" * (32768 - len(v2_header))
    assert len(v1.encode("utf-8")) == 32768 and len(v2.encode("utf-8")) == 32768
    if graph_bounds is None:
        ns, state = r_bootstrap(mode, lineage, root_body=v1)
    else:
        ns, state = r_bootstrap(mode, lineage, root_body=v1, graph_bounds=graph_bounds)
    state = _s_e_read(state, ns, "a", endpoint, "A.md", "Follow `X.md`.\n")
    state = _s_e_read(state, ns, "x", endpoint, "X.md", "Follow `Target.md`.\n")
    state = _s_e_read(state, ns, "t", endpoint, "Target.md", "Synthetic target governance.\n")
    state = _s_e_read(state, ns, "root2", endpoint, ROOT_FILENAME, v2)
    return ns, state, v2


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_e_multi_dependency_history_scale_outcome(mode: Any, endpoint: str) -> None:
    """E: the multi-dependency / version-history shape at the
    32768 root-member byte scale (both modes, both endpoints):
    the same honest original-domain record as the mixed-region
    shape (the default admission stage-work domain exhausts on
    the actual root-member span; the legal instance of that
    original stage domain carries the component), with the
    admitted dependency rows retained and the measured labeled
    component costs recorded."""
    legal_stage = GraphBounds(max_work_units=1_048_576)
    # (a) the ORIGINAL default stage-work domain record:
    ns, state, v2 = _s_e_multi_dep_state(mode, endpoint, f"s-e-md-{mode.value}-{endpoint}")
    r = derive_root_region_graph(state, ns)
    assert r.outcome is RootRegionGraphOutcome.READY
    assert r.state is state
    resolved = r.resolved_source
    assert resolved is not None
    assert resolved.root_byte_length == 32768
    assert resolved.root_digest == _sha256_hex(v2.encode("utf-8"))
    assert ns.graph_bounds.max_single_source_bytes == 1_000_000
    with pytest.raises(_GOverflow) as excinfo:
        _s_parent_from_assembly(ns, state, r, CurrentAdmissionBounds())
    assert excinfo.value.limitation is (CurrentAdmissionLimitation.ADMISSION_WORK_UNITS_EXHAUSTED)
    _s_e_record(
        "multi_dependency_history",
        mode,
        endpoint,
        32768,
        r.outcome.value,
        None,
        {
            "stage_domain": "default",
            "stage_cap": ns.graph_bounds.max_work_units,
            "component_outcome": "admission_work_units_exhausted",
        },
    )
    # (b) the LEGAL instance of the original stage domain:
    ns2, state2, v2b = _s_e_multi_dep_state(
        mode, endpoint, f"s-e-md-{mode.value}-{endpoint}-stage", graph_bounds=legal_stage
    )
    r2 = derive_root_region_graph(state2, ns2)
    assert r2.outcome is RootRegionGraphOutcome.READY
    assert r2.state is state2
    assert r2.resolved_source is not None
    assert r2.resolved_source.root_byte_length == 32768
    assert r2.resolved_source.root_digest == _sha256_hex(v2b.encode("utf-8"))
    g = CurrentAdmissionBounds()
    key_record, root_entry, file_entries, rows, _attempts, _member_occ, parent = (
        _s_parent_from_assembly(ns2, state2, r2, g)
    )
    assert parent.state is state2 and parent.ns is ns2 and parent.r_result is r2
    dep_paths = {row.path for row in rows if not row.is_root}
    assert {"A.md", "X.md"} <= dep_paths
    assert parent.entries_retained == 1 + len(file_entries)
    measured = _s_e_component_costs(state2, ns2, r2, g, root_entry, parent)
    assert measured["root_content"] > 0 and measured["parent"] > 0
    _s_e_record(
        "multi_dependency_history",
        mode,
        endpoint,
        32768,
        r2.outcome.value,
        measured,
        {
            "stage_domain": "legal_instance",
            "stage_cap": ns2.graph_bounds.max_work_units,
            "entries_retained": parent.entries_retained,
            "member_occurrences_charged": parent.member_occurrences_charged,
            "reverse_association_attempts": parent.reverse_association_attempts,
        },
    )


# --- F. Data preservation, identity, privacy and purity ---------------


@pytest.mark.parametrize("mode", MODES)
def test_f_deterministic_data_preservation_and_identity(mode: Any) -> None:
    """F: deterministic construction: two independent
    constructions from identical actual fields give a
    BYTE-IDENTICAL canonical C payload and the same stable model
    scope key, and the parent retains the exact original
    state/ns/R/result objects by IDENTITY (never a copy, never a
    reconstruction)."""
    ns1, s1, r1, g1, kr1, re1, par1 = _s_parent(mode, "s-f-det")
    ns2, s2, r2, g2, kr2, re2, par2 = _s_parent(mode, "s-f-det")
    # the canonical C payload is byte-identical (the unchanged
    # recipe over the identical actual fields):
    assert kr1.content_key == kr2.content_key
    assert kr1.model_dump(mode="json") == kr2.model_dump(mode="json")
    # the stable configuration scope key:
    assert par1.scope_key == par2.scope_key
    # the exact original references retained by identity:
    assert par1.state is s1 and par1.ns is ns1 and par1.r_result is r1
    assert par1.root_entry is re1
    assert par1.root_entry.root_source is r1.resolved_source
    assert par1.g_bounds is g1
    assert par2.state is s2 and par2.ns is ns2 and par2.r_result is r2
    # the entry never owns a second root body:
    src1 = r1.resolved_source
    assert src1 is not None
    assert re1.root_body_byte_length == src1.root_byte_length


@pytest.mark.parametrize("mode", MODES)
def test_f_private_repr_and_error_canaries(mode: Any) -> None:
    """F: the operational str/repr of every NEW public model
    surface (parent, root entry, FILE entries, path rows) and the
    fixed private constructor error carry NONE of the actual
    retained content, identity or ID values, when the genuine
    fixture actually carries the canaries (region root body,
    bootstrap root body, nonroot member body, call ID, principal /
    session / repository / route, model identity, lineage)."""
    root_canary = "SROOT-CANARY-018S"
    bootstrap_canary = "SBOOT-CANARY-018S"
    nonroot_canary = "SNONROOT-CANARY-018S"
    call_id = "s-f-purity-call"
    lineage = "s-f-purity-018s"
    identity = RequestIdentity(
        principal="s-priv-principal",
        session="s-priv-session",
        repository="s-priv-repository",
        route="s-priv-route",
    )
    cmd = f"cat A.md && echo '{MARK}' && cat AGENTS.md"
    ns, s0 = r_bootstrap(
        mode,
        lineage,
        root_body=f"Synthetic bootstrap root. {bootstrap_canary}",
        identity=identity,
        model_identity="s-priv-model",
    )
    body = _mixed_body(A_TEXT + nonroot_canary, MARK, f"Synthetic region root. {root_canary}")
    t1 = r_issue(s0, ns, call_id, "responses", (CAUSAL_ROOT_FACT,), cmd)
    assert t1.outcome.value == "accepted", t1.diagnostics
    state = r_observe(
        t1.state,
        ns,
        (read_request("responses", call_id, body, cmd),),
    ).state
    r = derive_root_region_graph(state, ns)
    assert r.outcome is RootRegionGraphOutcome.READY
    g = CurrentAdmissionBounds()
    key_record, root_entry, file_entries, rows, attempts, member_occ, parent = (
        _s_parent_from_assembly(ns, state, r, g)
    )
    surfaces = [repr(parent), str(parent), repr(root_entry), str(root_entry)]
    for e in file_entries:
        surfaces += [repr(e), str(e)]
    for row in parent.path_associations:
        surfaces += [repr(row), str(row)]
    canaries = (
        root_canary,
        bootstrap_canary,
        nonroot_canary,
        call_id,
        lineage,
        identity.principal,
        identity.session,
        identity.repository,
        identity.route,
        "s-priv-model",
    )
    for surface in surfaces:
        for canary in canaries:
            assert canary not in surface
    # the fixed private error of the refused copy (a forged scope
    # key over the REAL canary-bearing parent) echoes none of it:
    with pytest.raises(ValidationError, match="scope key must bind the actual") as excinfo:
        RootRegionAdmission(
            state=state,
            ns=ns,
            r_result=r,
            g_bounds=g,
            root_entry=root_entry,
            entries=file_entries,
            path_associations=rows,
            scope_key="ab" * 32,
            entries_retained=1 + len(file_entries),
            member_occurrences_charged=member_occ,
            reverse_association_attempts=attempts,
            emitted_admission_reasons=len(parent.admission_reasons),
        )
    for surface in (str(excinfo.value), repr(excinfo.value)):
        for canary in canaries:
            assert canary not in surface


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_f_no_host_io_on_public_model_paths(
    mode: Any, endpoint: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    """F: no host IO anywhere on the NEW public model/helper
    paths.  Fixture and import setup happen BEFORE the traps
    open; the traps (the closed 24-facility surface) then cover
    the whole construction on the SAME legitimate state: the
    public P bootstrap/issuance/observation, the actual R
    derivation (READY), the canonical key record, the G-assembled
    S parent, the eleven-carrier fence, the leaf law, the scope
    key, the component precharges on fresh bounded meters and the
    fixed private refusal path.  Every str/repr surface is free of
    the canaries and the original request payloads are unchanged."""
    marker = "PURITY-MARKER-018S"
    root_body = "PRIVATE-ROOT-CONTENT-018S. Read `A.md`."
    new_root = "PRIVATE-NEW-CONTENT-018S"
    new_body = f"Ordinary A.\n{marker}\n{new_root}."
    call_id = "s-purity-call"
    identity = RequestIdentity(
        principal="s-purity-principal",
        session="s-purity-session",
        repository="s-purity-repository",
        route="s-purity-route",
    )
    canaries = (
        identity.principal,
        identity.session,
        identity.repository,
        identity.route,
        "s-purity-model",
        "s-purity-lineage",
        call_id,
        marker,
        root_body,
        new_root,
    )
    cmd = f"cat A.md && echo '{marker}' && cat AGENTS.md"
    root = rooted(root_body)
    request = read_request(endpoint, call_id, new_body, cmd)
    originals = [json.dumps(q.payload, sort_keys=True) for q in (root, request)]
    calls: list[str] = []

    def trap(label: str) -> Any:
        def refused(*trap_args: Any, **trap_kwargs: Any) -> Any:
            calls.append(label)
            raise AssertionError("forbidden host IO: " + label)

        return refused

    for module, name in _host_io_facilities():
        monkeypatch.setattr(module, name, trap(module.__name__ + "." + name))

    try:
        admission = make_bundle_admission_namespace(
            identity,
            model_identity="s-purity-model",
            config_fingerprint="c" * 64,
            workspace="/work",
            mode=mode,
        )
        ns = make_root_region_lineage_namespace(admission, "s-purity-lineage")
        t0 = bootstrap_root_region_lineage((root,), ns)
        assert t0.outcome.value == "accepted", t0.diagnostics
        t1 = r_issue(t0.state, ns, call_id, endpoint, (CAUSAL_ROOT_FACT,), cmd)
        assert t1.outcome.value == "accepted", t1.diagnostics
        t2 = r_observe(t1.state, ns, (request,))
        assert t2.outcome.value == "accepted", t2.diagnostics
        state = t2.state
        r = derive_root_region_graph(state, ns)
        assert r.outcome is RootRegionGraphOutcome.READY
        g = CurrentAdmissionBounds()
        # the NEW public S model/helper surface, all under traps:
        key_record, root_entry, file_entries, rows, attempts, member_occ, parent = (
            _s_parent_from_assembly(ns, state, r, g)
        )
        assert _s_all_eleven_bound_sets_closed(ns, r, g)
        _s_entry_leaf_closed(root_entry)
        for e in file_entries:
            _s_entry_leaf_closed(e)
        resolved = r.resolved_source
        assert resolved is not None
        m1 = _D2Meter(10_000_000)
        _s_root_content_precharge_closed(
            m1, resolved.root_text, resolved.root_digest, resolved.root_byte_length
        )
        m2 = _D2Meter(10_000_000)
        _s_parent_precharge_closed(
            m2,
            state,
            ns,
            r,
            g,
            root_entry,
            parent.entries,
            parent.path_associations,
            parent.admission_reasons,
        )
        sk = root_region_admission_model_scope_key(
            state.lineage_key,
            ROOT_REGION_ADMISSION_MODELS_CONTRACT_VERSION,
            ROOT_REGION_ADMISSION_MODELS_POLICY_VERSION,
            r.scope_key,
            CURRENT_ADMISSION_CONTRACT_VERSION,
            CURRENT_ADMISSION_POLICY_VERSION,
            g,
        )
        assert sk == parent.scope_key
        # the fixed private refusal path (a forged scope key) also
        # runs under the traps:
        with pytest.raises(ValidationError, match="scope key must bind the actual"):
            RootRegionAdmission(
                state=state,
                ns=ns,
                r_result=r,
                g_bounds=g,
                root_entry=root_entry,
                entries=file_entries,
                path_associations=rows,
                scope_key="ab" * 32,
                entries_retained=1 + len(file_entries),
                member_occurrences_charged=member_occ,
                reverse_association_attempts=attempts,
                emitted_admission_reasons=len(parent.admission_reasons),
            )
        # privacy on the S surfaces:
        surfaces = [repr(parent), str(parent), repr(root_entry), str(root_entry)]
        for e in file_entries:
            surfaces += [repr(e), str(e)]
        for surface in surfaces:
            for canary in canaries:
                assert canary not in surface
        # the original request payloads are unchanged:
        assert [json.dumps(q.payload, sort_keys=True) for q in (root, request)] == originals
        assert calls == []
    finally:
        # guaranteed trap restore BEFORE any error formatting:
        monkeypatch.undo()

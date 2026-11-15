"""Region-compatible admission models (objective 018-s, MODEL/LOCAL-
BOUNDARY ONLY).

Versioned identities:

``ROOT_REGION_ADMISSION_MODELS_CONTRACT_VERSION =
"cache-root-region-admission-models/v1"``;
``ROOT_REGION_ADMISSION_MODELS_POLICY_VERSION =
"root-region-admission-models-policy/v1"``.

One INERT model slice: the immutable ``RootRegionAdmissionEntry``
(the region-compatible ROOT_ENTRY row plus the FILE rows, constructor-
compatible with the ACTUAL G ``_assemble_file_entries`` typed generic
FILE entry field set) and the ``RootRegionAdmission`` admission-parent
data model, plus the documented
``root_region_admission_model_scope_key`` helper.  This is COMPONENT
DATA, not a derivation: there is no operation result/outcome, no
persistent owner/namespace, no new whole-operation bound set and no
public derive function here.  The later same-018 complete consumer
derives ACTUAL R from ACTUAL P in the same entire charged operation
and must independently earn its own whole-operation budget; no public
API here accepts a caller-positive R/Q/F snapshot as derivation
authority.  Retaining the actual R result by reference is component
data, NOT authority.  Model construction is not cache admission,
compilation, wire delivery or authenticated runtime isolation.
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from typing import Any, Protocol

from pydantic import (
    BaseModel,
    Field,
    InstanceOf,
    ValidationInfo,
    field_validator,
    model_validator,
)

from .bundle_admission_models import (
    ADMISSION_CONTRACT_VERSION,
    AdmissionMode,
    BoundaryClass,
    BundleAdmissionBounds,
    BundleKeyRecord,
    EntryClass,
    MemberClass,
    OwnershipGroup,
)
from .bundle_proof_models import (
    ROOT_FILENAME,
    BundleProof,
    BundleProofBounds,
    BundleSegment,
)
from .causal_history_models import (
    MAX_REVISION,
    CausalHistoryNamespace,
    CausalHistoryState,
    CompletedReadOccurrence,
    HistoryBounds,
    ResultFingerprintRecord,
    RootAnchor,
)
from .client_paths import validate_workspace
from .current_admission_models import (
    CURRENT_ADMISSION_CONTRACT_VERSION,
    CURRENT_ADMISSION_POLICY_VERSION,
    CurrentAdmissionBounds,
    CurrentAdmissionLimitation,
    CurrentAdmissionPathAssociation,
    CurrentAdmissionWitness,
    _canonical_entry_key,
    _check_hex64,
    _check_text,
    _entry_admission_namespace,
    _sha256_hex,
)
from .current_graph_models import (
    CURRENT_GRAPH_CONTRACT_VERSION,
    CURRENT_GRAPH_POLICY_VERSION,
    CurrentGraph,
    CurrentGraphBounds,
    CurrentGraphLimitation,
    CurrentGraphOutcome,
    CurrentGraphResult,
)
from .currentness_models import (
    CURRENTNESS_CONTRACT_VERSION,
    CURRENTNESS_POLICY_VERSION,
    OPAQUE_GROUP_RECIPE_VERSION,
    CurrentnessBounds,
    CurrentnessOverlay,
)
from .graph_models import (
    GraphBounds,
    _check_rel_path,
    _fixed,
    _GraphFrozen,
)
from .observation_models import (
    PRIVATE_ID_PLACEHOLDER,
    Limitation,
    NormalizedPath,
    ObservationBounds,
    PathForm,
)
from .root_lineage_models import (
    _DIAGNOSTIC_CEILING,
    _HARD_ROOT_FACTS,
    _HARD_ROOT_SOURCE_BYTES,
    EnvelopeRootProvenance,
    ReadRootProvenance,
    RootLineageBounds,
    RootLineageLimitation,
    RootSelectionOutcome,
    _lineage_key,
)
from .root_region_currentness_models import (
    _HARD_Q_CALL_ID,
    _HARD_Q_DIAGNOSTICS,
    _HARD_Q_ROOT_OPERANDS,
    _HARD_Q_WITNESSES,
    ROOT_REGION_CURRENTNESS_CONTRACT_VERSION,
    ROOT_REGION_CURRENTNESS_POLICY_VERSION,
    RootRegionCurrentnessBounds,
    RootRegionCurrentnessDiagnostic,
    RootRegionCurrentnessOutcome,
    RootRegionCurrentnessResult,
    RootRegionUncertaintyClass,
    RootRegionUncertaintyWitness,
)
from .root_region_graph_models import (
    _R_E_OVERLAY_FIELDS,
    _R_ENVELOPE_PROV_FIELDS,
    _R_F_GRAPH_FIELDS,
    _R_OCCURRENCE_FIELDS,
    _R_PROOF_FIELDS,
    _R_READ_PROV_FIELDS,
    _R_REGION_PROV_FIELDS,
    _R_RESULT_FIELDS,
    _R_SOURCE_FIELDS,
    ROOT_REGION_GRAPH_CONTRACT_VERSION,
    ROOT_REGION_GRAPH_POLICY_VERSION,
    ResolvedRootRegionSource,
    RootRegionGraphBounds,
    RootRegionGraphOutcome,
    RootRegionGraphResult,
    _r_e_bounds_closed,
    _r_f_bounds_closed,
    _r_fields_present,
    _r_graph_version_ok,
    _r_q_bounds_closed,
    _r_result_closed,
    _r_source_closed,
    root_region_graph_bounds_shape_ok,
)
from .root_region_lineage import _region_version_pairs
from .root_region_lineage_models import (
    ROOT_REGION_LINEAGE_CONTRACT_VERSION,
    ROOT_REGION_LINEAGE_POLICY_VERSION,
    RootRegionLineageFact,
    RootRegionLineageNamespace,
    RootRegionLineageState,
    RootRegionReadProvenance,
    RootRegionSelectionResult,
    _region_provenance_key,
)

ROOT_REGION_ADMISSION_MODELS_CONTRACT_VERSION = "cache-root-region-admission-models/v1"
ROOT_REGION_ADMISSION_MODELS_POLICY_VERSION = "root-region-admission-models-policy/v1"
# The NEW versioned local validation-cost recipe for the FILE
# admitted region's owned encode/hash pass (component precharge
# contract only; the old I/N reservations are unchanged and no
# whole-operation bound set is introduced).
ROOT_REGION_ADMISSION_PRECHARGE_RECIPE_VERSION = "root-region-admission-precharge/v1"

#: Closed field tuples for the existence-before-deref fences.
_S_ENTRY_FIELDS: tuple[str, ...] = (
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
_S_PARENT_FIELDS: tuple[str, ...] = (
    "state",
    "ns",
    "r_result",
    "g_bounds",
    "root_entry",
    "entries",
    "path_associations",
    "entries_retained",
    "member_occurrences_charged",
    "reverse_association_attempts",
    "emitted_admission_reasons",
    "admission_reasons",
    "model_contract_version",
    "model_policy_version",
    "g_contract_version",
    "g_policy_version",
    "scope_key",
)
_S_STATE_FIELDS: tuple[str, ...] = (
    "lineage_key",
    "revision",
    "d_state",
    "root_facts",
)
_S_D_STATE_FIELDS: tuple[str, ...] = (
    "history_key",
    "revision",
    "root",
    "issuances",
    "occurrences",
    "results",
    "parent_links",
)
_S_NS_FIELDS: tuple[str, ...] = (
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
    "contract_version",
    "policy_version",
    "root_lineage_bounds",
    "lineage_key",
)
_S_G_BOUNDS_FIELDS: tuple[str, ...] = (
    "max_total_work_units",
    "max_total_entry_source_bytes",
    "max_diagnostics",
)
_S_SOURCE_KINDS = frozenset({"envelope", "read", "read_region"})


def _s_int_scalar_ok(value: object, lo: int, hi: int) -> bool:
    """Closed non-bool integer scalar under an explicit hard range."""
    return isinstance(value, int) and not isinstance(value, bool) and lo <= value <= hi


def _s_bounds_set_closed(value: object, expected: type[BaseModel]) -> bool:
    """ONE closed O(1) fence for a carried bound SET at ITS carrier:
    the EXPECTED ORIGINAL concrete class first (exact class identity,
    so a subclass that redeclares fields or WIDENED ranges is
    foreign, never a valid copy), and THEN every scalar field
    DECLARED by that original expected class exists on the instance
    as a non-bool integer inside BOTH original hard bounds (the
    ``ge`` lower and ``le`` upper read from the EXPECTED class's own
    field spec, never the instance's dynamic subclass metadata, and
    never a hardcoded copy).  A partial model_copy, a forged scalar
    (including a zero or a negative where the original floor is 1)
    or a foreign/subclassed class refuses BEFORE any cap is read or
    serialized.  A legitimate STRICTER instance of the original
    class remains legal by value.  The bound classes here are all
    scalar-integer sets."""
    if type(value) is not expected:
        return False
    fields = expected.model_fields
    for name, info in fields.items():
        if not hasattr(value, name):
            return False
        if info.annotation is not int:
            continue
        scalar = getattr(value, name)
        if isinstance(scalar, bool) or not isinstance(scalar, int):
            return False
        ge_value: int | None = None
        le_value: int | None = None
        for meta in info.metadata:
            ge_candidate = getattr(meta, "ge", None)
            if ge_candidate is not None:
                ge_value = ge_candidate
            le_candidate = getattr(meta, "le", None)
            if le_candidate is not None:
                le_value = le_candidate
        if ge_value is not None and scalar < ge_value:
            return False
        if le_value is not None and scalar > le_value:
            return False
    return True


def _s_g_bounds_closed(bounds: object) -> bool:
    """Closed fence at the ACTUAL G admission carrier: the exact
    ORIGINAL ``CurrentAdmissionBounds`` class, the closed scalar
    fields and BOTH original lower+upper hard ranges, BEFORE any
    serializer visit (a shadow subclass with redeclared ranges is
    refused by the class fence before its fields are read)."""
    return type(bounds) is CurrentAdmissionBounds and _s_bounds_set_closed(
        bounds, CurrentAdmissionBounds
    )


def _s_all_eleven_bound_sets_closed(
    ns: RootRegionLineageNamespace,
    r_result: RootRegionGraphResult,
    g_bounds: CurrentAdmissionBounds,
) -> bool:
    """The ACTUAL parent bound population: the six P-namespace sets,
    the four R-carried sets and the actual G admission set, each
    fenced under its EXPECTED ORIGINAL concrete class and ITS
    original hard range/class BEFORE any serializer or walk.  The
    R-carried sets reuse the ACTUAL closed R shape helpers (original
    hard ranges); the P-namespace and G sets run the generic closed
    scalar fence at their exact original class carrier.  No annotation-is-int skip, no
    hardcoded copy of a range, no global minimum or silent
    default for a malformed provided record.  The S-only exact
    original-class fence on the FOUR R-carried sets runs BEFORE
    those old R helpers: a subclass instance (even one whose
    original two scalar fields carry the same valid values) is
    foreign at the carrying boundary, while a valid STRICTER base
    class copy stays legal by value.  The old public R helpers,
    schemas, ranges and scopes are unchanged."""
    if (
        type(r_result.bounds) is not RootRegionGraphBounds
        or type(r_result.q_bounds) is not RootRegionCurrentnessBounds
        or type(r_result.f_bounds) is not CurrentGraphBounds
        or type(r_result.e_bounds) is not CurrentnessBounds
    ):
        return False
    if not (
        root_region_graph_bounds_shape_ok(r_result.bounds)
        and _r_q_bounds_closed(r_result.q_bounds)
        and _r_f_bounds_closed(r_result.f_bounds)
        and _r_e_bounds_closed(r_result.e_bounds)
        and _s_bounds_set_closed(ns.bounds, BundleAdmissionBounds)
        and _s_bounds_set_closed(ns.proof_bounds, BundleProofBounds)
        and _s_bounds_set_closed(ns.graph_bounds, GraphBounds)
        and _s_bounds_set_closed(ns.observation_bounds, ObservationBounds)
        and _s_bounds_set_closed(ns.history_bounds, HistoryBounds)
        and _s_bounds_set_closed(ns.root_lineage_bounds, RootLineageBounds)
        and _s_g_bounds_closed(g_bounds)
    ):
        return False
    return True


_S_Q_RESULT_FIELDS: tuple[str, ...] = (
    "outcome",
    "state",
    "p_selection",
    "p_validation_problem",
    "usable_selected_source_digest",
    "uncertainty_witnesses",
    "diagnostics",
    "contract_version",
    "policy_version",
    "bounds",
    "lineage_key",
    "scope_key",
    "revision",
)
_S_Q_WITNESS_FIELDS: tuple[str, ...] = (
    "occurrence",
    "result_record",
    "occurrence_id",
    "call_id",
    "endpoint",
    "uncertainty_class",
    "whole_proof_digest",
    "whole_proof_byte_length",
    "root_operand_count",
)
_S_F_RESULT_FIELDS: tuple[str, ...] = ("outcome", "state", "overlay", "diagnostics")
_S_P_SELECTION_FIELDS: tuple[str, ...] = (
    "outcome",
    "selected_source_digest",
    "witness_facts",
    "limitations",
    "lineage_key",
    "revision",
)
_S_P_FACT_FIELDS: tuple[str, ...] = (
    "source_digest",
    "source_byte_length",
    "provenance",
    "issued",
    "authority",
)
_S_F_GRAPH_FIELDS: tuple[str, ...] = (
    "revision",
    "workspace",
    "graph_version",
    "reference_version",
    "proof_version",
    "graph_bounds",
    "root_path",
)


def _s_nested_qpf_e_closed(r_result: RootRegionGraphResult, ns: RootRegionLineageNamespace) -> None:
    """The carried nested Q/P/F/E context fences, BEFORE the shared
    R result law may hash the scope or walk the source.  The
    shared body does not rerun the separate Q/P/F/E field
    validators: its Q field list omits the P validation problem,
    the own diagnostics and the uncertainty witnesses, its F
    result list omits the own diagnostics, and it has no
    P-namespace parameter for the F graph / E overlay context
    joins.  Here the ACTUAL concrete classes, closed identity
    fields, outcome enums, closed container/count/scalar gates
    and the actual namespace joins close first; the READY
    invariants (no own Q diagnostics, no P validation problem,
    ok-F empty diagnostics) run AFTER those count gates while
    legitimate dominated uncertainty witnesses and P
    limitations remain legal retained evidence.  Bounded
    variable metadata passes only (the closed diagnostic,
    witness and limitation loops); no full P/Q/F/E
    re-derivation, no per-witness source pass, no old public
    law or cap change; the passes are charged by the later
    D2 precharge law."""
    q = r_result.q_result
    if q is not None:
        if not isinstance(q, RootRegionCurrentnessResult):
            raise _fixed("the Q result must be the actual closed result record")
        if not _r_fields_present(q, _S_Q_RESULT_FIELDS):
            raise _fixed("the Q result must carry its closed fields")
        if not isinstance(q.outcome, RootRegionCurrentnessOutcome):
            raise _fixed("the Q result outcome must be the actual closed outcome")
        if q.p_validation_problem is not None and not isinstance(
            q.p_validation_problem, RootLineageLimitation
        ):
            raise _fixed("the Q result P validation problem must be a closed limitation")
        if (
            q.contract_version != ROOT_REGION_CURRENTNESS_CONTRACT_VERSION
            or q.policy_version != ROOT_REGION_CURRENTNESS_POLICY_VERSION
        ):
            raise _fixed("the Q result must carry the actual supported version identities")
        if not isinstance(q.lineage_key, str):
            raise _fixed("the Q result lineage key must be closed 64-hex text")
        _check_hex64(q.lineage_key, "lineage_key")
        if not isinstance(q.scope_key, str):
            raise _fixed("the Q result scope key must be closed 64-hex text")
        _check_hex64(q.scope_key, "scope_key")
        if not _s_int_scalar_ok(q.revision, 0, MAX_REVISION):
            raise _fixed("the Q result revision must be a closed non-bool integer")
        digest = q.usable_selected_source_digest
        if digest is not None:
            if not isinstance(digest, str):
                raise _fixed("the Q result usable digest must be closed 64-hex text")
            _check_hex64(digest, "usable_selected_source_digest")
        if not _r_q_bounds_closed(q.bounds):
            raise _fixed("the Q result bounds must be the actual closed Q bound record")
        if q.bounds != r_result.q_bounds:
            raise _fixed("the Q result bounds must equal the actual carried R Q domain")
        if q.diagnostics is None or not isinstance(q.diagnostics, tuple):
            raise _fixed("the Q result diagnostics must carry the closed tuple container")
        if len(q.diagnostics) > min(q.bounds.max_diagnostics, _HARD_Q_DIAGNOSTICS):
            raise _fixed("the Q result diagnostics exceed the actual Q cap")
        for diagnostic in q.diagnostics:
            if not isinstance(diagnostic, RootRegionCurrentnessDiagnostic):
                raise _fixed("the Q result diagnostics must be closed enum values")
        if tuple(sorted(set(q.diagnostics), key=lambda d: d.value)) != q.diagnostics:
            raise _fixed("the Q result diagnostics must be sorted and deduplicated")
        if q.outcome is RootRegionCurrentnessOutcome.READY:
            if q.diagnostics:
                raise _fixed("a ready Q result carries no own diagnostics")
            if q.p_validation_problem is not None:
                raise _fixed("a ready Q result carries no P validation problem")
        witnesses = q.uncertainty_witnesses
        if witnesses is None or not isinstance(witnesses, tuple):
            raise _fixed("the Q uncertainty witnesses must carry the closed tuple container")
        witness_cap = min(ns.history_bounds.max_occurrences, _HARD_Q_WITNESSES)
        if len(witnesses) > witness_cap:
            raise _fixed("the Q uncertainty witnesses exceed the actual retained occurrence domain")
        for witness in witnesses:
            if not (
                isinstance(witness, RootRegionUncertaintyWitness)
                and _r_fields_present(witness, _S_Q_WITNESS_FIELDS)
            ):
                raise _fixed("the Q uncertainty witness must be the actual closed record")
            if not isinstance(witness.occurrence, CompletedReadOccurrence):
                raise _fixed(
                    "the Q uncertainty witness occurrence must be the actual closed record"
                )
            if not isinstance(witness.result_record, ResultFingerprintRecord):
                raise _fixed(
                    "the Q uncertainty witness result record must be the actual closed record"
                )
            if not isinstance(witness.occurrence_id, str):
                raise _fixed("the Q uncertainty witness occurrence id must be closed 64-hex text")
            _check_hex64(witness.occurrence_id, "occurrence_id")
            if not isinstance(witness.call_id, str):
                raise _fixed("the Q uncertainty witness call id must be closed text")
            if not isinstance(witness.endpoint, str):
                raise _fixed("the Q uncertainty witness endpoint must be closed text")
            if not isinstance(witness.uncertainty_class, RootRegionUncertaintyClass):
                raise _fixed("the Q uncertainty witness class must be the actual closed enum")
            if not isinstance(witness.whole_proof_digest, str):
                raise _fixed("the Q uncertainty witness proof digest must be closed 64-hex text")
            _check_hex64(witness.whole_proof_digest, "whole_proof_digest")
            if isinstance(witness.whole_proof_byte_length, bool) or not isinstance(
                witness.whole_proof_byte_length, int
            ):
                raise _fixed(
                    "the Q uncertainty witness proof length must be a closed non-bool count"
                )
            if witness.whole_proof_byte_length < 0:
                raise _fixed(
                    "the Q uncertainty witness proof length must be a closed non-bool count"
                )
            if isinstance(witness.root_operand_count, bool) or not isinstance(
                witness.root_operand_count, int
            ):
                raise _fixed(
                    "the Q uncertainty witness operand count must be a closed non-bool count"
                )
            if witness.root_operand_count < 1:
                raise _fixed(
                    "the Q uncertainty witness operand count must be a closed non-bool count"
                )
            if witness.root_operand_count > _HARD_Q_ROOT_OPERANDS:
                raise _fixed(
                    "the Q uncertainty witness operand count must be a closed non-bool count"
                )
            if not 1 <= len(witness.call_id) <= _HARD_Q_CALL_ID or any(
                c.isspace() for c in witness.call_id
            ):
                raise _fixed("the Q uncertainty witness call id must be bounded non-space metadata")
            try:
                witness.call_id.encode("utf-8")
            except UnicodeEncodeError:
                raise _fixed("the Q uncertainty witness call id must be valid UTF-8") from None
            if witness.endpoint not in ("responses", "chat"):
                raise _fixed(
                    "the Q uncertainty witness endpoint must be an explicit validated endpoint"
                )
            if (
                witness.uncertainty_class is RootRegionUncertaintyClass.UNSUPPORTED_ROOT_SHAPE
                and witness.root_operand_count < 2
            ):
                raise _fixed(
                    "the Q uncertainty witness unsupported shape requires repeated root operands"
                )
            if (
                witness.uncertainty_class is RootRegionUncertaintyClass.OPAQUE_ROOT_BEARING_GROUP
                and witness.root_operand_count != 1
            ):
                raise _fixed(
                    "the Q uncertainty witness opaque group carries exactly one root operand"
                )
            occurrence = witness.occurrence
            result_record = witness.result_record
            if not (
                _r_fields_present(occurrence, _R_OCCURRENCE_FIELDS)
                and hasattr(occurrence, "anchored")
                and _r_fields_present(result_record, ("call_id", "endpoint", "complete"))
            ):
                raise _fixed(
                    "the Q uncertainty witness retained records must carry their closed fields"
                )
            if witness.occurrence_id != occurrence.occurrence_id:
                raise _fixed(
                    "the Q uncertainty witness occurrence id must join the retained occurrence"
                )
            if witness.call_id != occurrence.call_id:
                raise _fixed("the Q uncertainty witness call id must join the retained occurrence")
            if witness.endpoint != occurrence.endpoint:
                raise _fixed("the Q uncertainty witness endpoint must join the retained occurrence")
            if occurrence.anchored is not True:
                raise _fixed("the Q uncertainty witness requires an anchored retained occurrence")
            if result_record.call_id != occurrence.call_id:
                raise _fixed(
                    "the Q uncertainty witness result must match the retained occurrence call"
                )
            if result_record.endpoint != occurrence.endpoint:
                raise _fixed(
                    "the Q uncertainty witness result must match the retained occurrence endpoint"
                )
            if result_record.complete is not True:
                raise _fixed("the Q uncertainty witness requires a complete owning result")
            proof = occurrence.proof
            if not isinstance(proof, BundleProof) or not _r_fields_present(proof, _R_PROOF_FIELDS):
                raise _fixed(
                    "the Q uncertainty witness occurrence must carry its actual original proof"
                )
            if not isinstance(proof.source_digest, str):
                raise _fixed("the Q uncertainty witness proof digest must be closed 64-hex text")
            if (
                isinstance(proof.source_byte_length, bool)
                or not isinstance(proof.source_byte_length, int)
                or proof.source_byte_length < 0
            ):
                raise _fixed(
                    "the Q uncertainty witness proof length must be a closed non-bool count"
                )
            if witness.whole_proof_digest != proof.source_digest:
                raise _fixed("the Q uncertainty witness whole digest must match the retained proof")
            if witness.whole_proof_byte_length != proof.source_byte_length:
                raise _fixed("the Q uncertainty witness whole length must match the retained proof")
        witness_keys = tuple((w.uncertainty_class.value, w.occurrence_id) for w in witnesses)
        if tuple(sorted(witness_keys)) != witness_keys or len(set(witness_keys)) != len(
            witness_keys
        ):
            raise _fixed(
                "the Q uncertainty witnesses must be sorted and deduplicated by canonical order"
            )
        p_selection = q.p_selection
        if p_selection is not None:
            if not isinstance(p_selection, RootRegionSelectionResult):
                raise _fixed("the P selection must be the actual closed result record")
            if not _r_fields_present(p_selection, _S_P_SELECTION_FIELDS):
                raise _fixed("the P selection must carry its closed fields")
            if not isinstance(p_selection.outcome, RootSelectionOutcome):
                raise _fixed("the P selection outcome must be the actual closed outcome")
            if not isinstance(p_selection.lineage_key, str):
                raise _fixed("the P selection lineage key must be closed 64-hex text")
            _check_hex64(p_selection.lineage_key, "lineage_key")
            if not _s_int_scalar_ok(p_selection.revision, 0, MAX_REVISION):
                raise _fixed("the P selection revision must be a closed non-bool integer")
            selected = p_selection.selected_source_digest
            if selected is not None:
                if not isinstance(selected, str):
                    raise _fixed("the P selection source digest must be closed 64-hex text")
                _check_hex64(selected, "selected_source_digest")
            facts = p_selection.witness_facts
            if facts is None or not isinstance(facts, tuple):
                raise _fixed("the P selection witness facts must carry the closed tuple container")
            fact_cap = min(ns.root_lineage_bounds.max_root_facts, _HARD_ROOT_FACTS)
            if len(facts) > fact_cap:
                raise _fixed(
                    "the P selection witness facts exceed the actual retained root fact domain"
                )
            for fact in facts:
                if not (
                    isinstance(fact, RootRegionLineageFact)
                    and _r_fields_present(fact, _S_P_FACT_FIELDS)
                ):
                    raise _fixed("the P selection witness fact must be the actual closed record")
                if not isinstance(fact.source_digest, str):
                    raise _fixed("the P selection witness fact digest must be closed 64-hex text")
                _check_hex64(fact.source_digest, "source_digest")
                if not _s_int_scalar_ok(fact.source_byte_length, 0, _HARD_ROOT_SOURCE_BYTES):
                    raise _fixed(
                        "the P selection witness fact length must be a closed non-bool count"
                    )
                provenance = fact.provenance
                if isinstance(provenance, EnvelopeRootProvenance):
                    if not _r_fields_present(provenance, _R_ENVELOPE_PROV_FIELDS):
                        raise _fixed("the fact provenance must carry its closed variant fields")
                    if provenance.kind != "envelope":
                        raise _fixed("the fact provenance kind must match its concrete class")
                    if not isinstance(provenance.root_digest, str):
                        raise _fixed("the fact provenance digest must be closed 64-hex text")
                    _check_hex64(provenance.root_digest, "root_digest")
                    if not isinstance(provenance.workspace, str):
                        raise _fixed("the fact provenance workspace must be closed text")
                    if not (
                        1 <= len(provenance.workspace) <= 1024
                        and provenance.workspace.startswith("/")
                    ):
                        raise _fixed("the fact provenance workspace must be a closed absolute path")
                    if any(
                        ord(c) < 0x20 or ord(c) == 0x7F or c.isspace() for c in provenance.workspace
                    ):
                        raise _fixed(
                            "the fact provenance workspace must not contain control characters"
                        )
                    try:
                        provenance.workspace.encode("utf-8")
                    except UnicodeEncodeError:
                        raise _fixed("the fact provenance workspace must be valid UTF-8") from None
                    if not (
                        isinstance(provenance.source_byte_length, int)
                        and not isinstance(provenance.source_byte_length, bool)
                        and provenance.source_byte_length >= 0
                    ):
                        raise _fixed("the fact provenance length must be a closed non-bool count")
                    # The S-only ACTUAL envelope-to-context metadata
                    # join: the selected envelope fact's workspace
                    # must equal BOTH the actual P namespace
                    # workspace and the retained D anchor workspace
                    # (anchor class/field closed BEFORE any
                    # dereference).  The shared R body does not
                    # rerun this carrying join; no full P/D
                    # re-derivation and no source body walk.
                    anchor = r_result.state.d_state.root
                    if not isinstance(anchor, RootAnchor):
                        raise _fixed(
                            "the retained D anchor must be the actual closed anchor record"
                        )
                    if not _r_fields_present(anchor, ("workspace",)):
                        raise _fixed("the retained D anchor must carry its closed workspace field")
                    if provenance.workspace != ns.workspace:
                        raise _fixed(
                            "the envelope fact workspace must equal the actual namespace workspace"
                        )
                    if provenance.workspace != anchor.workspace:
                        raise _fixed(
                            "the envelope fact workspace must equal the retained anchor workspace"
                        )
                elif isinstance(provenance, ReadRootProvenance):
                    if not _r_fields_present(provenance, _R_READ_PROV_FIELDS):
                        raise _fixed("the fact provenance must carry its closed variant fields")
                    if provenance.kind != "read":
                        raise _fixed("the fact provenance kind must match its concrete class")
                    if not isinstance(provenance.occurrence_id, str):
                        raise _fixed("the fact provenance occurrence id must be closed 64-hex text")
                    _check_hex64(provenance.occurrence_id, "occurrence_id")
                    if not isinstance(provenance.call_id, str) or not isinstance(
                        provenance.endpoint, str
                    ):
                        raise _fixed("the fact provenance identity must be closed text")
                    if not 1 <= len(provenance.call_id) <= _HARD_Q_CALL_ID or any(
                        c.isspace() for c in provenance.call_id
                    ):
                        raise _fixed(
                            "the fact provenance call id must be bounded non-space metadata"
                        )
                    try:
                        provenance.call_id.encode("utf-8")
                    except UnicodeEncodeError:
                        raise _fixed("the fact provenance call id must be valid UTF-8") from None
                    if provenance.endpoint not in ("responses", "chat"):
                        raise _fixed(
                            "the fact provenance endpoint must be an explicit validated endpoint"
                        )
                    if not isinstance(provenance.read_digest, str):
                        raise _fixed("the fact provenance digest must be closed 64-hex text")
                    _check_hex64(provenance.read_digest, "read_digest")
                    if not (
                        isinstance(provenance.read_byte_length, int)
                        and not isinstance(provenance.read_byte_length, bool)
                        and provenance.read_byte_length >= 0
                    ):
                        raise _fixed("the fact provenance length must be a closed non-bool count")
                elif isinstance(provenance, RootRegionReadProvenance):
                    if not _r_fields_present(provenance, _R_REGION_PROV_FIELDS):
                        raise _fixed("the fact provenance must carry its closed variant fields")
                    if provenance.kind != "read_region":
                        raise _fixed("the fact provenance kind must match its concrete class")
                    if not isinstance(provenance.occurrence_id, str):
                        raise _fixed("the fact provenance occurrence id must be closed 64-hex text")
                    _check_hex64(provenance.occurrence_id, "occurrence_id")
                    if not isinstance(provenance.call_id, str) or not isinstance(
                        provenance.endpoint, str
                    ):
                        raise _fixed("the fact provenance identity must be closed text")
                    if not 1 <= len(provenance.call_id) <= _HARD_Q_CALL_ID or any(
                        c.isspace() for c in provenance.call_id
                    ):
                        raise _fixed(
                            "the fact provenance call id must be bounded non-space metadata"
                        )
                    try:
                        provenance.call_id.encode("utf-8")
                    except UnicodeEncodeError:
                        raise _fixed("the fact provenance call id must be valid UTF-8") from None
                    if provenance.endpoint not in ("responses", "chat"):
                        raise _fixed(
                            "the fact provenance endpoint must be an explicit validated endpoint"
                        )
                    if not isinstance(provenance.whole_proof_digest, str):
                        raise _fixed("the fact provenance digest must be closed 64-hex text")
                    _check_hex64(provenance.whole_proof_digest, "whole_proof_digest")
                    if not (
                        isinstance(provenance.whole_proof_byte_length, int)
                        and not isinstance(provenance.whole_proof_byte_length, bool)
                        and provenance.whole_proof_byte_length >= 0
                    ):
                        raise _fixed("the fact provenance length must be a closed non-bool count")
                    if not (
                        isinstance(provenance.root_segment_index, int)
                        and not isinstance(provenance.root_segment_index, bool)
                        and provenance.root_segment_index >= 0
                    ):
                        raise _fixed("the fact provenance index must be a closed non-bool count")
                    if not (
                        isinstance(provenance.root_member_position, int)
                        and not isinstance(provenance.root_member_position, bool)
                        and provenance.root_member_position >= 0
                    ):
                        raise _fixed("the fact provenance index must be a closed non-bool count")
                    if not isinstance(provenance.root_member_digest, str):
                        raise _fixed("the fact provenance digest must be closed 64-hex text")
                    _check_hex64(provenance.root_member_digest, "root_member_digest")
                    if not (
                        isinstance(provenance.root_member_byte_length, int)
                        and not isinstance(provenance.root_member_byte_length, bool)
                        and provenance.root_member_byte_length >= 0
                    ):
                        raise _fixed("the fact provenance length must be a closed non-bool count")
                else:
                    raise _fixed(
                        "the P selection witness fact provenance must be the actual closed union"
                    )
                if not isinstance(fact.issued, bool) or not isinstance(fact.authority, bool):
                    raise _fixed("the P selection witness fact flags must be closed booleans")
                if isinstance(provenance, EnvelopeRootProvenance):
                    if fact.issued is not False or fact.authority is not True:
                        raise _fixed("the envelope fact is never issued and always authoritative")
                    if (
                        fact.source_digest != provenance.root_digest
                        or fact.source_byte_length != provenance.source_byte_length
                    ):
                        raise _fixed("the envelope fact source must equal the anchor binding")
                elif isinstance(provenance, ReadRootProvenance):
                    if fact.authority and not fact.issued:
                        raise _fixed("a read fact is authoritative only when issued")
                    if (
                        fact.source_digest != provenance.read_digest
                        or fact.source_byte_length != provenance.read_byte_length
                    ):
                        raise _fixed("the read fact source must equal the whole-read binding")
                else:
                    if fact.authority and not fact.issued:
                        raise _fixed("a region fact is authoritative only when issued")
                    if (
                        fact.source_digest != provenance.root_member_digest
                        or fact.source_byte_length != provenance.root_member_byte_length
                    ):
                        raise _fixed("the region fact source must equal the root member binding")
            fact_keys = tuple(_region_provenance_key(f.provenance) for f in facts)
            if tuple(sorted(fact_keys)) != fact_keys or len(set(fact_keys)) != len(fact_keys):
                raise _fixed("the P selection witness facts must be sorted and deduplicated")
            limitations = p_selection.limitations
            if limitations is None or not isinstance(limitations, tuple):
                raise _fixed("the P selection limitations must carry the closed tuple container")
            if len(limitations) > _DIAGNOSTIC_CEILING:
                raise _fixed("the P selection limitations exceed the hard ceiling")
            for limitation in limitations:
                if not isinstance(limitation, RootLineageLimitation):
                    raise _fixed("the P selection limitations must be closed enum values")
            if tuple(sorted(set(limitations), key=lambda d: d.value)) != limitations:
                raise _fixed("the P selection limitations must be sorted and deduplicated")
    f = r_result.f_result
    if f is not None:
        if not isinstance(f, CurrentGraphResult):
            raise _fixed("the F result must be the actual closed result record")
        if not _r_fields_present(f, _S_F_RESULT_FIELDS):
            raise _fixed("the F result must carry its closed fields")
        if not isinstance(f.outcome, CurrentGraphOutcome):
            raise _fixed("the F result outcome must be the actual closed outcome")
        if f.diagnostics is None or not isinstance(f.diagnostics, tuple):
            raise _fixed("the F result diagnostics must carry the closed tuple container")
        if len(f.diagnostics) > r_result.f_bounds.max_diagnostics:
            raise _fixed("the F result diagnostics exceed the actual F cap")
        for f_diagnostic in f.diagnostics:
            if not isinstance(f_diagnostic, CurrentGraphLimitation):
                raise _fixed("the F result diagnostics must be closed enum values")
        if tuple(sorted(set(f.diagnostics), key=lambda d: d.value)) != f.diagnostics:
            raise _fixed("the F result diagnostics must be sorted and deduplicated")
        if f.outcome is CurrentGraphOutcome.OK and f.diagnostics:
            raise _fixed("an ok F result carries no own diagnostics")
    graph = f.overlay if f is not None else None
    if graph is not None:
        if not isinstance(graph, CurrentGraph):
            raise _fixed("the F graph must be the actual closed graph record")
        if not _r_fields_present(graph, _R_F_GRAPH_FIELDS):
            raise _fixed("the F graph must carry its closed context fields")
        if (
            not isinstance(graph.workspace, str)
            or not isinstance(graph.graph_version, str)
            or not isinstance(graph.reference_version, str)
            or not isinstance(graph.proof_version, str)
            or not isinstance(graph.contract_version, str)
            or not isinstance(graph.policy_version, str)
            or not isinstance(graph.currentness_contract_version, str)
            or not isinstance(graph.currentness_policy_version, str)
            or not isinstance(graph.currentness_recipe_version, str)
            or not isinstance(graph.root_path, str)
        ):
            raise _fixed("the F graph context fields must be closed text")
        if (
            not isinstance(graph.history_key, str)
            or not isinstance(graph.root_digest, str)
            or not isinstance(graph.currentness_scope_key, str)
            or not isinstance(graph.scope_key, str)
        ):
            raise _fixed("the F graph identity fields must be closed 64-hex text")
        _check_hex64(graph.history_key, "history_key")
        _check_hex64(graph.root_digest, "root_digest")
        _check_hex64(graph.currentness_scope_key, "currentness_scope_key")
        _check_hex64(graph.scope_key, "scope_key")
        if (
            graph.contract_version != CURRENT_GRAPH_CONTRACT_VERSION
            or graph.policy_version != CURRENT_GRAPH_POLICY_VERSION
            or graph.currentness_contract_version != CURRENTNESS_CONTRACT_VERSION
            or graph.currentness_policy_version != CURRENTNESS_POLICY_VERSION
            or graph.currentness_recipe_version != OPAQUE_GROUP_RECIPE_VERSION
        ):
            raise _fixed("the F graph must carry the actual supported version identities")
        if not _s_int_scalar_ok(graph.revision, 0, MAX_REVISION):
            raise _fixed("the F graph revision must be a closed non-bool integer")
        if not (
            _s_bounds_set_closed(graph.bounds, CurrentGraphBounds)
            and _s_bounds_set_closed(graph.currentness_bounds, CurrentnessBounds)
            and _s_bounds_set_closed(graph.graph_bounds, GraphBounds)
        ):
            raise _fixed("the F graph bound sets must be the actual closed original sets")
        if graph.workspace != ns.workspace:
            raise _fixed("the F graph workspace must equal the actual namespace workspace")
        if (
            graph.graph_version != ns.graph_version
            or graph.reference_version != ns.reference_version
            or graph.proof_version != ns.proof_version
        ):
            raise _fixed("the F graph versions must equal the actual namespace versions")
        if graph.graph_bounds != ns.graph_bounds:
            raise _fixed("the F graph bounds must equal the actual namespace graph bounds")
        if graph.root_path != ROOT_FILENAME:
            raise _fixed("the F graph root path must be the actual root contract path")
    overlay = r_result.e_overlay
    if overlay is not None:
        if not isinstance(overlay, CurrentnessOverlay):
            raise _fixed("the E overlay must be the actual closed overlay record")
        if not _r_fields_present(overlay, _R_E_OVERLAY_FIELDS):
            raise _fixed("the E overlay must carry its closed identity fields")
        if (
            not isinstance(overlay.workspace, str)
            or not isinstance(overlay.policy_version, str)
            or not isinstance(overlay.history_key, str)
            or not isinstance(overlay.scope_key, str)
        ):
            raise _fixed("the E overlay context fields must be closed text")
        _check_hex64(overlay.history_key, "history_key")
        _check_hex64(overlay.scope_key, "scope_key")
        if overlay.policy_version != CURRENTNESS_POLICY_VERSION:
            raise _fixed("the E overlay must carry the actual supported policy identity")
        if not _s_int_scalar_ok(overlay.revision, 0, MAX_REVISION):
            raise _fixed("the E overlay revision must be a closed non-bool integer")
        if not _s_bounds_set_closed(overlay.bounds, CurrentnessBounds):
            raise _fixed("the E overlay bounds must be the actual closed bound set")
        if overlay.workspace != ns.workspace:
            raise _fixed("the E overlay workspace must equal the actual namespace workspace")


_S_KEY_RECORD_FIELDS: tuple[str, ...] = (
    "admission_version",
    "graph_version",
    "reference_version",
    "proof_version",
    "observation_version",
    "mode",
    "authority_class",
    "principal",
    "session",
    "repository",
    "route",
    "config_fingerprint",
    "model_identity",
    "workspace",
    "root_digest",
    "admission_bounds",
    "proof_bounds",
    "graph_bounds",
    "observation_bounds",
    "member_occurrences",
    "member_classes",
    "aggregate_source_digest",
    "ownership_groups",
    "content_key",
)
_S_GROUP_FIELDS: tuple[str, ...] = (
    "group_index",
    "member_occurrence_indices",
    "boundary_class",
    "group_digest",
)
_S_SEGMENT_FIELDS: tuple[str, ...] = (
    "char_length",
    "byte_length",
    "member_positions",
    "digest",
    "member_digest",
)


def _s_member_path_cap(record: BundleKeyRecord) -> int:
    """The ACTUAL inherited member-path byte ceiling (the accepted
    N law re-fenced at the S boundary): a legal member reference
    is within BOTH the carried graph and the carried observation
    path-byte ceilings, hence within the smaller.  Both bound
    sets close under their exact ORIGINAL classes in the shared
    O(1) shape phase before this is read."""
    return min(record.graph_bounds.max_path_bytes, record.observation_bounds.max_path_bytes)


def _s_key_record_preflight_shape(record: BundleKeyRecord) -> tuple[int, int]:
    """The SHARED O(1) record class/field/bounds/count preflight,
    separated from the record ELEMENT walk: closed field existence,
    the closed member container classes, the FOUR carried bound sets
    under their exact ORIGINAL classes and original hard ranges, the
    ACTUAL member-occurrence cap and the record-level class/
    occurrence alignment, the ownership-groups container/count
    gate, and the workspace's closed nonempty-text and O(1)
    character-count shape under the ACTUAL carried graph path
    bound -- all O(1), BEFORE any element visit, character walk
    or canonical rekey.  Returns the closed (actual member cap,
    actual graph path cap) so the charged precharge can run the
    bounded workspace WALKS only after the reservation that pays
    for them.  Reused by the raw BEFORE-PARSING entry gate and the
    carried leaf check (the closed record fence re-runs the
    identical closure, unchanged); a bypassed record with a
    malformed bound, a missing container or a matching oversized
    vector is a fixed private error, never a TypeError or an
    unbounded element visit."""
    if not _r_fields_present(record, _S_KEY_RECORD_FIELDS):
        raise _fixed("the entry key record must carry its closed fields")
    if not isinstance(record.member_occurrences, tuple) or not record.member_occurrences:
        raise _fixed("the key record member occurrences must carry a nonempty closed tuple")
    if not isinstance(record.member_classes, tuple) or not record.member_classes:
        raise _fixed("the key record member classes must carry a nonempty closed tuple")
    if not (
        _s_bounds_set_closed(record.admission_bounds, BundleAdmissionBounds)
        and _s_bounds_set_closed(record.proof_bounds, BundleProofBounds)
        and _s_bounds_set_closed(record.graph_bounds, GraphBounds)
        and _s_bounds_set_closed(record.observation_bounds, ObservationBounds)
    ):
        raise _fixed("the key record carried bound sets must be closed scalar sets")
    cap = record.admission_bounds.max_member_occurrences
    if len(record.member_occurrences) > cap:
        raise _fixed("the key record member occurrences exceed the actual carried admission cap")
    if len(record.member_classes) != len(record.member_occurrences):
        raise _fixed("the key record member classes must align with the occurrences")
    # The ownership-groups container/count gate (closed in this
    # shared O(1) shape phase, not only in the closed record
    # fence): a bypassed None or an over-occurrence group vector
    # is a fixed private error here, before any element visit,
    # walk or fence len() can raise a raw TypeError.
    if (
        not isinstance(record.ownership_groups, tuple)
        or not record.ownership_groups
        or len(record.ownership_groups) > len(record.member_occurrences)
    ):
        raise _fixed("the key record ownership groups must carry a nonempty closed tuple")
    # The carried workspace closes under the ACTUAL graph path
    # domain BEFORE any cap read, element walk or canonical
    # rekey: every boundary that runs this preflight (the raw
    # BEFORE-PARSING entry gate, the closed record fence, the
    # leaf law, the parent re-run) refuses an over-bound or
    # noncanonical workspace with a fixed private error before
    # the C serializer can serialize it (closed nonempty text
    # first; the exact ACTUAL carried max_path_bytes UTF-8
    # ceiling is the bounded walk's job, and the canonical
    # absolute POSIX form under the accepted C workspace law,
    # including its normalized-form check, is the walk's second
    # step).
    workspace = record.workspace
    if not isinstance(workspace, str) or not workspace:
        raise _fixed("the key record workspace must carry closed canonical text")
    path_cap = record.graph_bounds.max_path_bytes
    # O(1) character-count bound FIRST (UTF-8 bytes are never
    # fewer than characters): a huge malformed workspace refuses
    # before any allocation or walk.
    if len(workspace) > path_cap:
        raise _fixed("the key record workspace exceeds the actual carried graph path bound")
    return cap, path_cap


def _s_key_record_preflight_walk(record: BundleKeyRecord, path_cap: int) -> None:
    """The BOUNDED workspace walks the O(1) shape gate leaves
    uncharged: the no-copy UTF-8 byte-length check (walked once,
    bounded by the closed character count; a lone surrogate is not
    encodable UTF-8 and refuses here, and a mid-walk crossing of
    the ACTUAL carried cap refuses early) and the accepted C
    canonical EQUALITY check (a valid spelling that normalizes to
    ANOTHER string, e.g. a doubled slash, is not the canonical
    workspace and refuses before any serialization).  No owned
    bytes object is allocated before the bound is established, so
    the bounded encodes that follow (this gate's canonical-form
    check, the C recipe's scoped input) are always bounded by the
    closed cap.  The charged precharge runs this only AFTER the
    reservation that pays for it; the uncharged entry/leaf
    boundaries run it through the composite below."""
    workspace = record.workspace
    utf8_length = 0
    for char in workspace:
        code = ord(char)
        if 0xD800 <= code <= 0xDFFF:
            raise _fixed("the key record workspace must be valid UTF-8 text")
        if code < 0x80:
            utf8_length += 1
        elif code < 0x800:
            utf8_length += 2
        elif code < 0x10000:
            utf8_length += 3
        else:
            utf8_length += 4
        if utf8_length > path_cap:
            raise _fixed("the key record workspace exceeds the actual carried graph path bound")
    if validate_workspace(workspace, path_cap) != workspace:
        raise _fixed("the key record workspace must be a canonical absolute POSIX path")


def _s_key_record_preflight(record: BundleKeyRecord) -> int:
    """The SHARED record preflight in its uncharged composite
    form: the O(1) shape gate followed immediately by the bounded
    workspace walks.  The raw BEFORE-PARSING entry gate, the
    closed record fence re-run and the carried leaf check use this
    composite (their boundaries carry no meter); the charged
    precharge helper splits the two parts around its fence
    reservation so no workspace walk runs uncharged.  Returns the
    closed actual cap."""
    cap, path_cap = _s_key_record_preflight_shape(record)
    _s_key_record_preflight_walk(record, path_cap)
    return cap


def _s_key_record_closed(record: BundleKeyRecord) -> None:
    """The CLOSED canonical key-record metadata fence, enforced in
    the accepted precedence (the leaf O(1) law BEFORE any element
    visit, count assumption or canonical rekey): (1) actual field
    existence on the real record; (2) every O(1) class/variant and
    non-bool scalar/hex shape gate, including the record's own
    member/class/container COUNT alignment; (3) the FOUR carried
    bound sets closed under their exact ORIGINAL classes; and only
    THEN (4) the element visits: the per-path and per-member-class
    shape walks and the OWNERSHIP GROUP PARTITION (dense ordered
    unique one-to-one over the entry-local member occurrence
    range).  A partial or detached record is a fixed private error,
    never an attribute error, before the rekey can serialize it."""
    if not _r_fields_present(record, _S_KEY_RECORD_FIELDS):
        raise _fixed("the entry key record must carry its closed fields")
    # (2) O(1) class/variant and non-bool scalar/hex shape gates.
    if not isinstance(record.mode, AdmissionMode):
        raise _fixed("the key record mode must be the actual closed admission mode")
    if not isinstance(record.authority_class, EntryClass):
        raise _fixed("the key record authority class must be the actual closed class")
    for field, limit in (
        ("principal", 256),
        ("session", 256),
        ("repository", 256),
        ("route", 64),
        ("model_identity", 256),
    ):
        value = getattr(record, field)
        if not isinstance(value, str):
            raise _fixed(f"the key record {field} must carry closed text")
        _check_text(value, field, limit)
    for field in (
        "config_fingerprint",
        "root_digest",
        "aggregate_source_digest",
        "content_key",
    ):
        value = getattr(record, field)
        if not isinstance(value, str):
            raise _fixed(f"the key record {field} must carry closed hex")
        _check_hex64(value, field)
    if not isinstance(record.workspace, str):
        raise _fixed("the key record workspace must carry closed text")
    for field in (
        "admission_version",
        "graph_version",
        "reference_version",
        "proof_version",
        "observation_version",
    ):
        value = getattr(record, field)
        if not isinstance(value, str):
            raise _fixed(f"the key record {field} must carry closed text")
        _check_text(value, field, 128)
    # (2 cont.) the SHARED O(1) record preflight (closed container
    # classes, the FOUR carried bound sets under their exact
    # ORIGINAL classes, the ACTUAL member-occurrence cap and the
    # record-level alignment, the ownership-groups container/count
    # gate) runs BEFORE any element visit or rekey.
    _s_key_record_preflight(record)
    # (4) the element visits: per-path and per-member-class
    # shapes.  Each member path first closes under the ACTUAL
    # carried path domain BEFORE its character walk (O(1)
    # character count, then the bounded no-copy UTF-8 byte walk
    # with early exit): the accepted C _check_rel_path shape law
    # carries no byte ceiling of its own, so a copied oversized
    # member path would otherwise be walked -- and later
    # serialized -- beyond the charged bound.  The domain is the
    # inherited N law's ACTUAL two-inherited path-byte ceiling
    # (a legal member reference is within BOTH the graph and the
    # observation caps, hence within the smaller); the gate is
    # S-local and the old C/G/I/N public shape law is unchanged.
    path_cap = _s_member_path_cap(record)
    for path in record.member_occurrences:
        if not isinstance(path, str):
            raise _fixed("the key record member occurrences must carry closed paths")
        if len(path) > path_cap:
            raise _fixed("the key record member occurrences exceed the actual carried path bound")
        path_bytes = 0
        for char in path:
            code = ord(char)
            if 0xD800 <= code <= 0xDFFF:
                raise _fixed("the key record member occurrences must be valid UTF-8 paths")
            if code < 0x80:
                path_bytes += 1
            elif code < 0x800:
                path_bytes += 2
            elif code < 0x10000:
                path_bytes += 3
            else:
                path_bytes += 4
            if path_bytes > path_cap:
                raise _fixed(
                    "the key record member occurrences exceed the actual carried path bound"
                )
        _check_rel_path(path)
    for member_class in record.member_classes:
        if not isinstance(member_class, MemberClass):
            raise _fixed(
                "the key record member classes must be the actual closed authority classes"
            )
    # (4 cont.) the OWNERSHIP GROUP PARTITION: dense ordered unique
    # one-to-one over the entry-local member occurrence range (the
    # accepted C record law, re-run here BEFORE the rekey).
    seen: list[int] = []
    for position, group in enumerate(record.ownership_groups):
        if not isinstance(group, OwnershipGroup):
            raise _fixed("the key record ownership groups must be the actual closed groups")
        if not _r_fields_present(group, _S_GROUP_FIELDS):
            raise _fixed("the key record ownership groups must carry their closed fields")
        if (
            isinstance(group.group_index, bool)
            or not isinstance(group.group_index, int)
            or group.group_index != position
        ):
            raise _fixed("ownership group indices must be dense and ordered")
        indices = group.member_occurrence_indices
        if not isinstance(indices, tuple) or not indices:
            raise _fixed("the group member occurrence indices must be a nonempty closed tuple")
        # O(1) COUNT before any index walk or seen extension: under
        # the one-to-one partition law a group cannot carry more
        # indices than the record has member occurrences.
        if len(indices) > len(record.member_occurrences):
            raise _fixed(
                "the group member occurrence indices cannot exceed the member occurrence count"
            )
        previous = -1
        for index in indices:
            if (
                isinstance(index, bool)
                or not isinstance(index, int)
                or index < 0
                or index <= previous
            ):
                raise _fixed("the group member occurrence indices must be distinct and increasing")
            previous = index
        if not isinstance(group.boundary_class, BoundaryClass):
            raise _fixed("the group boundary class must be the actual closed class")
        if group.group_digest is not None:
            if not isinstance(group.group_digest, str):
                raise _fixed("the group digest must carry closed hex")
            _check_hex64(group.group_digest, "group_digest")
        seen.extend(indices)
    if sorted(seen) != list(range(len(record.member_occurrences))) or len(seen) != len(set(seen)):
        raise _fixed("ownership groups must partition the member occurrences")


def _s_entry_scope_joined(record: BundleKeyRecord, ns: RootRegionLineageNamespace) -> None:
    """The entry key record's ACTUAL admission scope, re-derived
    from the record's own fields through the accepted C recipe,
    must join the parent namespace: principal ... workspace, mode,
    the FIVE versions and the FOUR bound sets field-by-field, and
    BOTH recomputed 64-hex keys equal to the parent's.  Equal
    copied tags alone prove nothing; a foreign
    principal/session/workspace/config on a coherently rekeyed
    record is a fixed private error, never a silent mix."""
    try:
        entry_ns = _entry_admission_namespace(record)
    except Exception:
        raise _fixed("the entry key record must re-derive its actual admission namespace") from None
    if (
        entry_ns.principal != ns.principal
        or entry_ns.session != ns.session
        or entry_ns.repository != ns.repository
        or entry_ns.route != ns.route
        or entry_ns.model_identity != ns.model_identity
        or entry_ns.config_fingerprint != ns.config_fingerprint
        or entry_ns.workspace != ns.workspace
        or entry_ns.mode != ns.mode
        or entry_ns.admission_version != ns.admission_version
        or entry_ns.observation_version != ns.observation_version
        or entry_ns.graph_version != ns.graph_version
        or entry_ns.reference_version != ns.reference_version
        or entry_ns.proof_version != ns.proof_version
        or entry_ns.bounds != ns.bounds
        or entry_ns.proof_bounds != ns.proof_bounds
        or entry_ns.graph_bounds != ns.graph_bounds
        or entry_ns.observation_bounds != ns.observation_bounds
        or entry_ns.namespace_key != ns.admission_namespace_key
        or entry_ns.scoped_key != ns.admission_scoped_key
    ):
        raise _fixed("every entry key record must bind the actual parent admission scope")


class _SRegionWorkReserver(Protocol):
    """The CALLER-SUPPLIED component-local work meter for the FILE
    admitted region precharge (the closed
    ``root-region-admission-precharge/v1`` law).  A bounded meter
    raises immediately when a charge crosses its remaining budget,
    so the caller's actual targets (the leaf law, the constructor)
    never run after a crossing.  The model validators never supply
    one: the ordinary S constructors remain data-validity checks,
    and no unlimited or default meter exists in this module.
    """

    def reserve(self, units: int) -> None: ...


def _s_region_precharge_closed(
    reserver: _SRegionWorkReserver,
    source_text: str,
    segments: tuple[BundleSegment, ...],
    admitted_segments: tuple[int, ...],
    region_chars: int,
    region_bytes: int,
    cap: int,
    proof_bounds: BundleProofBounds,
) -> tuple[int, int]:
    """The closed NEW local validation-cost reservation for the FILE
    admitted region's owned passes (the versioned
    ``root-region-admission-precharge/v1`` recipe).

    This is a SEPARATE component precharge contract: the caller
    supplies the typed bounded meter and invokes the actual targets
    (the leaf law, the constructor) only after this returns.  The
    ordinary model validators never receive a meter, and the
    reservation is a WORK meter, never a source-size limit: the
    actual ``cap`` is only the inherited single-source BYTE ceiling
    measured against the ACTUAL UTF-8 length of the retained source
    (a legal at-cap source stays legal); it is never a bound on the
    work reservation itself.

    The closed admission SHAPE mirrors the leaf's whole-bundle
    law (the admitted region is the whole bundle or one proven
    group).  The WHOLE-BUNDLE shape takes the leaf's genuine
    fast path: the partition closure proves the segments tile the
    source, so the joined region IS the source text itself (no
    slice/join copies; the character total is the O(1) source
    length; the measurement is one direct source pass).  The
    SINGLE-GROUP shape keeps the per-segment offset calculation,
    the per-segment measurement outer advance and the slice/join
    passes.

    Order: (1) close the reserver, the meter scalars and the
    retained container kinds (constant work, no element visit);
    (2) close the carried B segment-domain context -- the actual
    concrete bound record (a class fence only: it does not prove
    identity to the original bound instance, so a valid by-value
    stricter copy is legal), its own required field under the
    original hard range, and the O(1) retained/admitted segment
    population counts against that carried bound (a tuple length
    alone is not that cap) -- BEFORE the metadata reserve or any
    element walk; (3) reserve the ACTUAL closed-stage metadata
    passes BEFORE the stage runs: one fixed unit for the closed
    fences (including the O(1) shape length check), the segment
    element fence, the two admitted-index passes (the element
    fence, the membership set build) and -- only when the O(1)
    length check establishes equal lengths -- the whole-bundle
    shape's single closed n-element comparison walk (no snapshot
    is built, so no pass is hidden or amortized); (4) run the
    closed fences and the closed admission SHAPE detection (the
    leaf's whole-bundle law re-fenced before any walk: the whole
    bundle, every index equal to its own position, or one proven
    group, a single index inside the retained segment domain; a
    partial actual segment, a non-int index or any other shape is
    a fixed private error, never AttributeError or an out-of-
    domain target call); (5) derive the selected interval's
    ACTUAL character count (the O(1) source length for the
    whole-bundle fast path, the precharged offset advance for the
    single-group shape) and join it to the declared character
    metadata BEFORE any measurement (a forged declared count
    cannot authorize the walk); (6) reserve the ACTUAL character
    visits and run the NO-COPY capped UTF-8 measurement (one
    direct source pass for the whole-bundle shape, the
    precharged per-segment outer advance plus the admitted
    intervals for the single-group shape; a lone surrogate or an
    interval past the retained text is a fixed private error
    BEFORE any owned encode; a measured crossing of the actual
    source cap reuses the inherited source-cap refusal and stops
    the walk early); (7) join the declared byte metadata to the
    measured value (forged lengths cannot authorize a copy);
    (8) only after measuring, reserve the actual owned work and
    return it as the closed (character, byte) reservation: the
    character reservation is the slice pass plus the join pass
    (``2 * region_chars``) for the single-group shape and ZERO
    for the whole-bundle fast path (its leaf target reuses the
    source text itself, making no slice/join copies), and the
    byte reservation is the encode output plus one SHA-256 input
    pass plus the fixed 72-byte pad and 32-byte digest
    (``2 * measured + 104``) for both shapes.  No divide-by-
    constant, no amortized-away pass, no per-witness full-source
    walk: the measurement visits exactly the admitted characters.
    This reserves component work for the later whole-operation
    recipe; it earns no whole-operation bound and changes no old
    public law.
    """
    if reserver is None or not callable(getattr(reserver, "reserve", None)):
        raise _fixed("the region precharge reserver must carry a typed reserve callback")
    if (
        isinstance(region_chars, bool)
        or not isinstance(region_chars, int)
        or region_chars < 0
        or isinstance(region_bytes, bool)
        or not isinstance(region_bytes, int)
        or region_bytes < 0
        or isinstance(cap, bool)
        or not isinstance(cap, int)
        or cap < 0
    ):
        raise _fixed("the region precharge meter must carry closed nonnegative integers")
    if not isinstance(source_text, str):
        raise _fixed("the retained region source must be closed UTF-8 text")
    if not isinstance(segments, tuple):
        raise _fixed("the retained region segments must be the closed original tuple")
    if not isinstance(admitted_segments, tuple):
        raise _fixed("the admitted region segments must be the closed original tuple")
    # (2) the carried B segment-domain context, closed O(1)
    # BEFORE the metadata reserve or any element walk: the actual
    # concrete bound record (a class fence only -- it does not
    # prove identity to the original bound instance, so a valid
    # by-value stricter copy is legal), its own required field
    # under the original hard range, and the O(1) segment
    # population counts against that carried bound (a tuple length
    # alone is not that cap).
    if type(proof_bounds) is not BundleProofBounds:
        raise _fixed("the retained region proof bound context must be the actual concrete record")
    if (
        not _r_fields_present(proof_bounds, ("max_segments",))
        or isinstance(proof_bounds.max_segments, bool)
        or not isinstance(proof_bounds.max_segments, int)
        or proof_bounds.max_segments < 1
        or proof_bounds.max_segments > 10_000
    ):
        raise _fixed("the retained region proof bound context must carry a closed segment bound")
    max_segments = proof_bounds.max_segments
    if len(segments) > max_segments:
        raise _fixed("the retained region segments exceed the actual carried proof segment bound")
    if len(admitted_segments) > max_segments:
        raise _fixed(
            "the admitted region segment indices exceed the actual carried proof segment bound"
        )
    n_segments = len(segments)
    n_admitted = len(admitted_segments)
    # (3) the ACTUAL closed-stage metadata passes reserved BEFORE
    # the stage runs: the closed fences (one fixed unit, including
    # the O(1) shape length check), the segment element fence, the
    # two admitted-index passes (the element fence, the membership
    # set build) and -- reserved only when the O(1) length check
    # establishes that the lengths match -- the whole-bundle
    # shape's single closed n-element comparison walk (no snapshot
    # is built, so no pass is hidden or amortized).
    reserver.reserve(
        1 + n_segments + 2 * n_admitted + (n_segments if n_admitted == n_segments else 0)
    )
    for segment in segments:
        if (
            not isinstance(segment, BundleSegment)
            or not _r_fields_present(segment, ("char_length",))
            or isinstance(segment.char_length, bool)
            or not isinstance(segment.char_length, int)
            or segment.char_length < 0
        ):
            raise _fixed("the retained region segments must carry closed original lengths")
    for position in admitted_segments:
        if not isinstance(position, int) or isinstance(position, bool):
            raise _fixed("the admitted region segment indices must be closed integers")
    # (4) the closed admission SHAPE (the leaf's whole-bundle law
    # re-fenced BEFORE any walk so the later target can never be
    # reached with a shape it would refuse or index out of
    # domain): the whole bundle (every index equal to its own
    # position -- one closed comparison walk, no snapshot) or one
    # proven group (a single index inside the retained segment
    # domain).
    if n_admitted == n_segments and all(admitted_segments[i] == i for i in range(n_segments)):
        whole_bundle = True
    elif n_admitted == 1 and 0 <= admitted_segments[0] < n_segments:
        whole_bundle = False
    else:
        raise _fixed("the admitted region must be the whole bundle or one proven group")
    admitted_set = set(admitted_segments)
    # (5) the selected interval's ACTUAL character count: the O(1)
    # source length for the whole-bundle fast path (the partition
    # closure ties the segment lengths to the source), or the
    # precharged single-group offset advance.
    source_length = len(source_text)
    if whole_bundle:
        walk_chars = source_length
    else:
        reserver.reserve(n_segments)
        walk_chars = 0
        for position, segment in enumerate(segments):
            if position in admitted_set:
                walk_chars += segment.char_length
    # (6) the declared character metadata joined to the ACTUAL
    # count BEFORE any measurement (a forged declared count cannot
    # authorize the walk).
    if walk_chars != region_chars:
        raise _fixed("the retained region character metadata must equal the retained source text")
    # (7) the ACTUAL character visits of the no-copy measurement,
    # reserved BEFORE the walk: one direct source pass for the
    # whole-bundle shape, the precharged per-segment outer advance
    # plus the admitted intervals for the single-group shape.
    reserver.reserve(walk_chars)
    measured = 0
    if whole_bundle:
        for index in range(source_length):
            code = ord(source_text[index])
            if 0xD800 <= code <= 0xDFFF:
                raise _fixed("the retained region source must be closed UTF-8 text")
            if code < 0x80:
                measured += 1
            elif code < 0x800:
                measured += 2
            elif code < 0x10000:
                measured += 3
            else:
                measured += 4
            if measured > cap:
                raise _fixed("admitted region exceeds the inherited single-source byte cap")
    else:
        reserver.reserve(n_segments)
        offset = 0
        for position, segment in enumerate(segments):
            char_length = segment.char_length
            if position in admitted_set:
                start = offset
                end = offset + char_length
                if start > source_length or end > source_length:
                    raise _fixed(
                        "the retained region intervals must stay inside the retained source text"
                    )
                for index in range(start, end):
                    code = ord(source_text[index])
                    if 0xD800 <= code <= 0xDFFF:
                        raise _fixed("the retained region source must be closed UTF-8 text")
                    if code < 0x80:
                        measured += 1
                    elif code < 0x800:
                        measured += 2
                    elif code < 0x10000:
                        measured += 3
                    else:
                        measured += 4
                    if measured > cap:
                        raise _fixed("admitted region exceeds the inherited single-source byte cap")
            offset += char_length
    # (8) the declared byte metadata joined to the ACTUAL measured
    # UTF-8 length (forged large OR small lengths cannot authorize
    # a copy; measured bytes are never fewer than characters).
    if measured != region_bytes:
        raise _fixed(
            "the retained region byte metadata must equal the measured UTF-8 source length"
        )
    # (9) the owned work, reserved AFTER measuring and BEFORE the
    # caller's actual allocation/hash: the slice pass plus the
    # join pass (``2 * walk_chars``) exist only for the single-
    # group shape -- the whole-bundle fast path reuses the source
    # text itself, so its character reservation is ZERO -- then
    # the encode output plus one SHA-256 input pass plus the fixed
    # 72-byte pad and 32-byte digest (``2 * measured + 104``) for
    # both shapes.
    if whole_bundle:
        char_units = 0
    else:
        char_units = 2 * walk_chars
        reserver.reserve(char_units)
    byte_units = 2 * measured + 104
    reserver.reserve(byte_units)
    return char_units, byte_units


def _s_root_content_precharge_closed(
    reserver: _SRegionWorkReserver,
    root_text: str,
    root_digest: str,
    root_byte_length: int,
) -> tuple[int, int]:
    """The closed NEW local validation-cost reservation for the
    ROOT content pass (the versioned
    ``root-region-admission-precharge/v1`` recipe, the root branch
    of the actual closed R source law).

    SEPARATE component precharge contract: the caller supplies the
    typed bounded meter and invokes the actual targets (the leaf
    law, the constructor) only after this returns.  The model
    validators never receive a meter, and the reservation is a
    WORK meter, never a source-size limit: the actual hard
    root-source byte ceiling is a scalar domain only, and a legal
    root at its own byte length stays legal (the cap is never a
    bound on the work itself).

    The closed content law mirrors the ACTUAL
    ``_r_source_content_ok`` target in its own order: (1) the
    closed O(1) shape gates BEFORE any walk or reservation (the
    closed text/digest classes, the byte length as a closed
    non-bool scalar under the actual hard root-source byte cap,
    bytes never fewer than characters, the digest length exactly
    64); (2) reserve the bounded 64-hex shape walk (the closed
    set builds and subset probes at the fixed 64 length: 64 + 16
    + 64 element visits plus one fixed fence unit) and then run
    it (a non-hex digest is a fixed private error, never a
    serializer exception); (3) reserve the ACTUAL no-copy capped
    UTF-8 measurement character visits and run the walk (the
    declared byte length is the actual law's cap, so the walk
    exits as soon as it is exceeded; a lone surrogate fails
    closed, never an encoder exception, BEFORE any owned
    encode); (4) join the declared byte metadata to the ACTUAL
    measured length (a forged large OR small length cannot
    authorize a copy); (5) reserve the ACTUAL target's repeated
    passes BEFORE the caller may invoke the target: the closed
    content law (``_r_source_content_ok``) re-runs the 64-hex
    shape check (one fence unit plus the same closed 64-length
    set visits) and the full no-copy capped measurement walk
    over the same text before its owned encode/hash, so the
    guarded caller sequence is fully reserved before any target
    work; (6) only after measuring, reserve the actual owned
    encode plus SHA-256 work and return it: the character
    reservation is ZERO (the materialized root body IS the
    retained text itself, so the target makes no slice/join
    copies, and the owned encode's own per-character pass is
    bounded by the reserved byte domain because bytes are never
    fewer than characters), and the byte reservation is the
    encode output plus one SHA-256 input pass plus the fixed
    72-byte pad and 32-byte digest (``2 * measured + 104``).
    No divide-by-constant, no amortized-away pass, no whole
    original proof/state walk: the measurement visits exactly
    the root characters, twice (once in this precharge, once in
    the target, both reserved).  This reserves component work
    for the later whole-operation recipe; it earns no whole-
    operation bound and changes no old public law.
    """
    if reserver is None or not callable(getattr(reserver, "reserve", None)):
        raise _fixed("the root content precharge reserver must carry a typed reserve callback")
    # (1) the closed O(1) shape gates, BEFORE any walk or
    # reservation.
    if not isinstance(root_text, str):
        raise _fixed("the retained root source must be closed UTF-8 text")
    if not isinstance(root_digest, str):
        raise _fixed("the retained root digest must be closed hex text")
    if not _s_int_scalar_ok(root_byte_length, 0, _HARD_ROOT_SOURCE_BYTES):
        raise _fixed(
            "the retained root source byte length must be a closed scalar under the actual hard cap"
        )
    n_chars = len(root_text)
    if n_chars > root_byte_length:
        raise _fixed("the retained root source bytes are never fewer than its characters")
    if len(root_digest) != 64:
        raise _fixed("the retained root digest must be closed 64-hex text")
    # (2) the bounded 64-hex shape walk, reserved BEFORE it runs:
    # one fixed fence unit plus the set builds and subset probes
    # at the fixed 64 length.
    reserver.reserve(1 + 144)
    if not set(root_digest) <= set("0123456789abcdef"):
        raise _fixed("the retained root digest must be closed 64-hex text")
    # (3) the ACTUAL no-copy capped UTF-8 measurement visits,
    # reserved BEFORE the walk.
    reserver.reserve(n_chars)
    measured = 0
    for ch in root_text:
        cp = ord(ch)
        if 0xD800 <= cp <= 0xDFFF:
            raise _fixed("the retained root source must be closed UTF-8 text")
        if cp < 0x80:
            measured += 1
        elif cp < 0x800:
            measured += 2
        elif cp < 0x10000:
            measured += 3
        else:
            measured += 4
        if measured > root_byte_length:
            raise _fixed(
                "the retained root source exceeds its declared byte length before any owned encode"
            )
    # (4) the declared byte metadata joined to the ACTUAL
    # measured UTF-8 length (forged lengths cannot authorize a
    # copy).
    if measured != root_byte_length:
        raise _fixed("the retained root byte metadata must equal the measured UTF-8 root length")
    # (5) the ACTUAL target's repeated passes, reserved BEFORE
    # the caller invokes the target: the closed content law
    # (``_r_source_content_ok``) re-runs the 64-hex shape check
    # (one fence unit plus the same closed 64-length set visits)
    # and the full no-copy capped measurement walk over the same
    # text before its owned encode/hash, so both repeats are
    # charged here, never left to the target uncharged.
    reserver.reserve(1 + 144)
    reserver.reserve(n_chars)
    # (6) the owned work, reserved AFTER measuring and BEFORE the
    # caller's actual encode/hash: the encode output plus one
    # SHA-256 input pass plus the fixed 72-byte pad and 32-byte
    # digest.
    byte_units = 2 * measured + 104
    reserver.reserve(byte_units)
    return 0, byte_units


def _s_parent_precharge_closed(
    reserver: _SRegionWorkReserver,
    state: RootRegionLineageState,
    ns: RootRegionLineageNamespace,
    r_result: RootRegionGraphResult,
    g_bounds: CurrentAdmissionBounds,
    root_entry: RootRegionAdmissionEntry,
    entries: tuple[RootRegionAdmissionEntry, ...],
    path_associations: tuple[Any, ...],
    admission_reasons: tuple[Any, ...],
) -> None:
    """The closed NEW local validation-cost reservation for the
    ADMISSION PARENT re-run (the versioned
    ``root-region-admission-precharge/v1`` recipe, the complete
    ``_v_admission`` carrying law).

    SEPARATE component precharge contract: the caller supplies
    the typed bounded meter and invokes the actual target (the
    parent constructor re-run) only after this returns.  The
    model validators never receive a meter, and the reservation
    is a WORK meter, never a size limit (a legal record at its
    actual lengths stays legal).

    The OPENING gates run before the first target-cost
    reservation: the closed O(1) class gates, the field-
    existence fences at the ACTUAL constructor field sets
    (the same tuples the model validators fence with), the
    ELEVEN carried bound sets at their original classes and
    hard ranges, the closed container kinds, the O(1) count
    gates with the INHERITED collection caps enforced at
    their ACTUAL carried bound sets (the ROOT + FILE entry
    population against the actual inherited admission entry
    cap, the association rows against the actual inherited
    reverse-association cap), and the helper's own
    occurrence/entry counting walks -- each walk reserved
    at its closed per-element ceiling BEFORE it runs, with
    the per-element class/field/container fences charged as
    work and every counted retained length (each proof
    pieces tuple, each key-record member occurrences
    tuple, and the cumulative member total) closed under
    its ACTUAL inherited or carried domain before it feeds
    any reservation.

    The reservation mirrors the ACTUAL ``_v_admission`` phase
    order and reserves every real pass BEFORE the target may
    run: phase 0/1 (the closed class/field fences and the
    ELEVEN bound sets at their expected-class field counts);
    phase 1b (the closed count gates and the admission-reason
    set/sort/comparison walks); phase 2 (the 64-hex shape
    checks at their closed 64-length set visits, the identity-
    text UTF-8 walks, the workspace/lineage-id walks, the
    version joins, the nested Q/P-selection/F/E evidence re-
    joins at their ACTUAL record counts (the E overlay's four
    closed text shape fences run before its length
    calculation), the F currentness / F graph / E currentness
    scope keys at their ACTUAL JSON-array recipes (brackets,
    separators, quote pairs and ensure_ascii escaped bodies;
    the embedded bound-set JSON strings with their escaped key
    quotes, and the precharge's own ceiling calculations
    reserved before their walks), and the complete
    closed R result law: the R scope key re-derivation (its
    24-element join, its UTF-8 ceiling and its SHA-256), the
    diagnostic sorted walk and the resolved-source content law
    with its bounded content pass); phase 3 (the closed
    D-namespace re-derivation and P lineage-key component:
    its own field/bound closure, its charged ceiling
    calculations and both actual canonical/SHA-256 blocks
    reserved before the target); phase 4/5/6/8 (the leaf law
    re-run and the entry-set/reverse-index/counter walks: the
    ROOT row's leaf re-run reuses the ACTUAL component
    contracts -- the resolved-source identity fence, the
    canonical-metadata component (whose closed O(1) record
    shape gate refuses before any character walk, then the
    leaf rekey plus the parent scope-join
    re-derivation/comparison) and the root-content component
    (whose own fences and charged passes reserve before its
    target may run) -- and the FILE row the same canonical
    component, its closed B-domain population caps before the
    helper's own charged metadata walks, the region component
    at the entry's own carried B domain and the M04 owner/
    witness joins at the ACTUAL inherited owner-domain
    ceilings -- every ceiling can only over-charge the
    target's actual walks, never under-charge them);
    phase 9 (the S model scope key re-derivation at its closed
    canonical ceiling).  Every payload is reserved at a CLOSED
    ceiling derived from the actual record lengths/field
    counts (a ceiling can only over-charge the actual
    serializer, never under-charge it); no divide-by-constant,
    no amortized-away pass, no whole original proof/state body
    walk.  This reserves the parent re-run's component work for
    the later whole-operation recipe; it earns no whole-
    operation bound and changes no old public law.
    """
    if reserver is None or not callable(getattr(reserver, "reserve", None)):
        raise _fixed("the admission parent precharge reserver must carry a typed reserve callback")
    # (1) the closed O(1) class gates, BEFORE any dereference or
    # reservation.
    if type(state) is not RootRegionLineageState:
        raise _fixed("the admission parent state must be the actual closed state record")
    if type(ns) is not RootRegionLineageNamespace:
        raise _fixed("the admission parent namespace must be the actual closed record")
    if type(r_result) is not RootRegionGraphResult:
        raise _fixed("the admission parent R result must be the actual closed record")
    if type(g_bounds) is not CurrentAdmissionBounds:
        raise _fixed("the admission parent G bounds must be the actual closed record")
    if type(root_entry) is not RootRegionAdmissionEntry:
        raise _fixed("the admission parent root entry must be the actual closed record")
    if not isinstance(entries, tuple) or not isinstance(path_associations, tuple):
        raise _fixed("the admission parent entry and association containers must be closed tuples")
    if not isinstance(admission_reasons, tuple):
        raise _fixed("the admission parent reasons must carry the closed tuple container")
    # (1a) the closed field-existence fences at the ACTUAL
    # constructor field sets (the same tuples the model
    # validators fence with): a field never set on a real-
    # class copy refuses with the fixed private error BEFORE
    # any dereference, count or reservation, never an
    # AttributeError.
    if not _r_fields_present(state, _S_STATE_FIELDS):
        raise _fixed("the admission parent state must carry the closed field set")
    d_state = state.d_state
    if type(d_state) is not CausalHistoryState:
        raise _fixed("the wrapped D state must be the actual causal-history state")
    if not _r_fields_present(d_state, _S_D_STATE_FIELDS):
        raise _fixed("the wrapped D state must carry the closed field set")
    if not _r_fields_present(ns, _S_NS_FIELDS):
        raise _fixed("the admission parent namespace must carry the closed field set")
    # The carried namespace identity texts, workspace and
    # lineage id close as closed bounded text BEFORE any
    # len-based reservation calculation below (a bypassed
    # None or over-long copy is a fixed private boundary
    # error, never a TypeError from the precharge's own
    # ceiling arithmetic): the walked control/UTF-8/canonical
    # checks remain the target's charged phase-2 work.
    for _ns_text, _ns_limit in (
        ("principal", 256),
        ("session", 256),
        ("repository", 256),
        ("route", 64),
        ("model_identity", 256),
    ):
        _ns_value = getattr(ns, _ns_text)
        if not isinstance(_ns_value, str) or not 1 <= len(_ns_value) <= _ns_limit:
            raise _fixed(f"the carried namespace {_ns_text} must carry closed bounded text")
    if not isinstance(ns.workspace, str) or not 1 <= len(ns.workspace) <= 1024:
        raise _fixed("the carried namespace workspace must carry closed bounded text")
    if not isinstance(ns.lineage_id, str) or not 1 <= len(ns.lineage_id) <= 128:
        raise _fixed("the carried namespace lineage id must carry closed bounded text")
    if not _r_fields_present(r_result, _R_RESULT_FIELDS):
        raise _fixed("the admission parent R result must carry its closed identity fields")
    source = r_result.resolved_source
    if not isinstance(source, ResolvedRootRegionSource):
        raise _fixed("the ready R result publishes its resolved root source")
    if not _r_fields_present(source, _R_SOURCE_FIELDS):
        raise _fixed("the retained root source must carry its closed fields")
    if not isinstance(source.root_text, str) or not isinstance(source.root_digest, str):
        raise _fixed("the retained root source must be closed UTF-8 text with 64-hex text")
    if not _s_int_scalar_ok(source.root_byte_length, 0, _HARD_ROOT_SOURCE_BYTES):
        raise _fixed(
            "the retained root source byte length must be a closed scalar under the actual hard cap"
        )
    # The carried R version/scope headers that feed the
    # precharge's own phase-2 scope arithmetic close as closed
    # bounded text with their O(1) length bounds BEFORE any
    # len/str work below (a bypassed None is a fixed private
    # boundary error, never a TypeError from the precharge's
    # ceiling calculation): the 64-hex set walks and the
    # version identity joins remain the target's charged
    # phase-2 work.
    for _r_header in (
        r_result.contract_version,
        r_result.policy_version,
        r_result.graph_version,
    ):
        if not isinstance(_r_header, str) or not 1 <= len(_r_header) <= 128:
            raise _fixed("the carried R result headers must carry closed bounded text")
    if not isinstance(r_result.scope_key, str) or len(r_result.scope_key) != 64:
        raise _fixed("the carried R scope key must carry closed 64-length text")
    if not isinstance(state.lineage_key, str) or len(state.lineage_key) != 64:
        raise _fixed("the carried state lineage key must carry closed 64-length text")
    # The ELEVEN carried bound sets at their expected original
    # classes and original hard ranges (the ACTUAL parent
    # constructor fence, reused, including the actual G set):
    # a partial/forged/foreign bound refuses before any cap is
    # read or serialized; a valid stricter copy stays legal by
    # value.
    if not _s_all_eleven_bound_sets_closed(ns, r_result, g_bounds):
        raise _fixed("the admission parent bound sets must carry the actual closed records")
    r = r_result
    q = r.q_result
    p_selection: RootRegionSelectionResult | None = None
    if q is not None:
        if type(q) is not RootRegionCurrentnessResult:
            raise _fixed("the carried Q result must be the actual closed record")
        if not _r_fields_present(q, _S_Q_RESULT_FIELDS):
            raise _fixed("the carried Q result must carry its closed field set")
        if not (
            isinstance(q.uncertainty_witnesses, tuple)
            and isinstance(q.diagnostics, tuple)
            and _r_q_bounds_closed(q.bounds)
        ):
            raise _fixed("the carried Q context must carry closed containers and bound fields")
        # The carried Q headers and its wrapped state close as
        # closed bounded text BEFORE the Q scope arithmetic
        # below (the same D1 boundary as the R headers).
        for _q_header in (q.contract_version, q.policy_version):
            if not isinstance(_q_header, str) or not 1 <= len(_q_header) <= 128:
                raise _fixed("the carried Q result headers must carry closed bounded text")
        if type(q.state) is not RootRegionLineageState:
            raise _fixed("the carried Q result must wrap the actual closed state record")
        if not _r_fields_present(q.state, ("lineage_key",)):
            raise _fixed("the carried Q state must carry its closed lineage key field")
        if not isinstance(q.state.lineage_key, str) or len(q.state.lineage_key) != 64:
            raise _fixed("the carried state lineage key must carry closed 64-length text")
        p_selection = q.p_selection
        if p_selection is not None:
            if type(p_selection) is not RootRegionSelectionResult:
                raise _fixed("the carried P selection must be the actual closed record")
            if not _r_fields_present(p_selection, _S_P_SELECTION_FIELDS):
                raise _fixed("the carried P selection must carry its closed field set")
            if not isinstance(p_selection.witness_facts, tuple):
                raise _fixed("the carried P selection witness container must be a closed tuple")
    f_result = r.f_result
    f_graph: CurrentGraph | None = None
    if f_result is not None:
        if type(f_result) is not CurrentGraphResult:
            raise _fixed("the carried F result must be the actual closed record")
        if not _r_fields_present(f_result, _S_F_RESULT_FIELDS):
            raise _fixed("the carried F result must carry its closed field set")
        f_graph = f_result.overlay
        if f_graph is not None:
            if type(f_graph) is not CurrentGraph:
                raise _fixed("the carried F graph must be the actual closed record")
            if not _r_fields_present(f_graph, _R_F_GRAPH_FIELDS):
                raise _fixed("the carried F graph must carry its closed field set")
            # The carried F graph scope headers and bound sets
            # close as closed text / closed scalar sets BEFORE
            # any len/str scope arithmetic below (the same D1
            # boundary; the version joins and the scope
            # re-derivations remain the target's charged work).
            # The carried F graph scope headers close under the
            # ORIGINAL graph law (workspace 1..1024, the version
            # texts 1..128, the 64-hex identity keys exactly 64,
            # the root path closed nonempty text) BEFORE any
            # length feeds a reservation below (a copied
            # oversized or missing header refuses with the fixed
            # private error, never a charge-sized walk or a raw
            # len() TypeError).
            if not isinstance(f_graph.workspace, str) or not 1 <= len(f_graph.workspace) <= 1024:
                raise _fixed("the carried F graph workspace must carry closed bounded text")
            if not isinstance(f_graph.root_path, str) or not f_graph.root_path:
                raise _fixed("the carried F graph root path must carry closed nonempty text")
            for _f_header in (
                f_graph.graph_version,
                f_graph.reference_version,
                f_graph.proof_version,
                f_graph.currentness_contract_version,
                f_graph.currentness_policy_version,
                f_graph.currentness_recipe_version,
                f_graph.contract_version,
                f_graph.policy_version,
            ):
                if not isinstance(_f_header, str) or not 1 <= len(_f_header) <= 128:
                    raise _fixed("the carried F graph scope headers must carry closed bounded text")
            for _f_key in (
                f_graph.history_key,
                f_graph.root_digest,
                f_graph.currentness_scope_key,
            ):
                if not isinstance(_f_key, str) or len(_f_key) != 64:
                    raise _fixed(
                        "the carried F graph identity keys must carry closed 64-length text"
                    )
            if not (
                _s_bounds_set_closed(f_graph.bounds, CurrentGraphBounds)
                and _s_bounds_set_closed(f_graph.currentness_bounds, CurrentnessBounds)
                and _s_bounds_set_closed(f_graph.graph_bounds, GraphBounds)
            ):
                raise _fixed("the carried F graph bound sets must be the actual closed sets")
    if r.e_overlay is not None:
        if type(r.e_overlay) is not CurrentnessOverlay:
            raise _fixed("the carried E overlay must be the actual closed record")
        if not _r_fields_present(r.e_overlay, _R_E_OVERLAY_FIELDS):
            raise _fixed("the carried E overlay must carry its closed field set")
        if not _s_bounds_set_closed(r.e_overlay.bounds, CurrentnessBounds):
            raise _fixed("the carried E overlay bounds must be the actual closed bound set")
    if not isinstance(d_state.occurrences, tuple) or not isinstance(d_state.results, tuple):
        raise _fixed("the wrapped D occurrence and result containers must be closed tuples")
    if not isinstance(state.root_facts, tuple):
        raise _fixed("the carried root fact container must be a closed tuple")
    if not isinstance(r.diagnostics, tuple):
        raise _fixed("the carried R diagnostic container must be a closed tuple")

    # (1b) the closed O(1) record counts (no element walk) with
    # the INHERITED collection caps enforced at their ACTUAL
    # carried bound sets BEFORE any element walk (the len
    # checks are O(1); a carried stricter cap stays legal by
    # value).
    occurrences = d_state.occurrences
    n_occ = len(occurrences)
    if n_occ > ns.history_bounds.max_occurrences:
        raise _fixed("the retained occurrence count exceeds the actual inherited history cap")
    n_res = len(d_state.results)
    if n_res > ns.history_bounds.max_observed_results:
        raise _fixed("the retained result count exceeds the actual inherited history cap")
    n_facts = len(state.root_facts)
    if n_facts > ns.root_lineage_bounds.max_root_facts:
        raise _fixed("the retained root fact count exceeds the actual inherited root-lineage cap")
    n_e = len(entries)
    # The ROOT + FILE entry population counts against the
    # ACTUAL inherited C admission entry cap (the current
    # admission G bounds carry no entry domain: total work,
    # entry-source bytes and diagnostics only).
    if 1 + n_e > ns.bounds.max_entries:
        raise _fixed("the retained entry count exceeds the actual inherited entry cap")
    n_r = len(admission_reasons)
    if n_r > min(g_bounds.max_diagnostics, ns.bounds.max_diagnostics):
        raise _fixed("the carried admission reason count exceeds the actual closed diagnostic caps")
    n_rows = len(path_associations)
    if n_rows > ns.bounds.max_reverse_associations:
        raise _fixed("the retained association count exceeds the actual inherited cap")
    n_rd = len(r.diagnostics)
    if n_rd > r.bounds.max_diagnostics:
        raise _fixed("the carried R diagnostic count exceeds the actual R bound")
    n_qd = 0
    n_qw = 0
    n_pf = 0
    if q is not None:
        n_qd = len(q.diagnostics)
        if n_qd > q.bounds.max_diagnostics:
            raise _fixed("the carried Q diagnostic count exceeds the actual Q bound")
        n_qw = len(q.uncertainty_witnesses)
        if n_qw > ns.history_bounds.max_occurrences:
            raise _fixed(
                "the carried uncertainty witness count exceeds the actual inherited history cap"
            )
        if p_selection is not None:
            n_pf = len(p_selection.witness_facts)
            if n_pf > ns.root_lineage_bounds.max_root_facts:
                raise _fixed(
                    "the carried P selection fact count exceeds the actual inherited "
                    "root-lineage cap"
                )
    src_chars = len(source.root_text)
    src_bytes = source.root_byte_length
    # The retained piece domain: the O(1) cap read; the
    # per-proof and counted-cumulative closures run inside
    # the precharged counting walk below, before any pieces
    # length feeds a reservation.
    max_retained_pieces = ns.history_bounds.max_retained_pieces
    # (1c) the helper's own COUNTING walks, each reserved at
    # its closed per-element ceiling BEFORE it runs (the
    # per-element class/field/container fences are charged
    # work; a crossing refuses before the first element visit).
    reserver.reserve(1 + 12 * n_occ)
    n_pieces_max = 0
    total_pieces = 0
    for occurrence in occurrences:
        if type(occurrence) is not CompletedReadOccurrence:
            raise _fixed("the retained occurrence must be the actual closed record")
        if not _r_fields_present(occurrence, ("proof",)):
            raise _fixed("the retained occurrence must carry its closed proof field")
        proof = occurrence.proof
        if type(proof) is not BundleProof:
            raise _fixed("the retained proof must be the actual closed record")
        if not _r_fields_present(proof, ("pieces",)):
            raise _fixed("the retained proof must carry its closed piece field")
        pieces = proof.pieces
        if not isinstance(pieces, tuple):
            raise _fixed("the retained proof pieces must carry the closed tuple container")
        n_pieces = len(pieces)
        if n_pieces > max_retained_pieces:
            raise _fixed("the retained proof pieces exceed the actual inherited history piece cap")
        total_pieces += n_pieces
        if total_pieces > max_retained_pieces:
            raise _fixed("the retained proof piece total exceeds the actual inherited history cap")
        n_pieces_max = max(n_pieces_max, n_pieces)
    # The closed per-element ceiling over the entries
    # counting walk: the entry/key-record class+field
    # fences (4), the shared key-record field-presence fence
    # (its actual field count), the member/class container
    # gates at the ACTUAL carried member cap plus alignment
    # (10), the FOUR carried bound sets at their actual
    # int-field and metadata counts, the ownership container
    # gate (5) and the O(1) workspace character bound (4)
    # from the SHARED key-record preflight, plus the
    # member-length accumulation (2); the leading 1 covers
    # the ceiling's own derivation reads.
    entry_fence_ceil = (
        4
        + len(_S_KEY_RECORD_FIELDS)
        + 10
        + sum(
            2
            + sum(
                7 + 4 * len(info.metadata)
                for info in cls.model_fields.values()
                if info.annotation is int
            )
            for cls in (
                BundleAdmissionBounds,
                BundleProofBounds,
                GraphBounds,
                ObservationBounds,
            )
        )
        + 5
        + 4
        + 2
    )
    reserver.reserve(1 + entry_fence_ceil * n_e)
    total_members = 1
    for entry in entries:
        if type(entry) is not RootRegionAdmissionEntry:
            raise _fixed("the admission parent entry must be the actual closed record")
        if not _r_fields_present(entry, ("key_record",)):
            raise _fixed("the admission parent entry must carry its closed key record")
        key_record = entry.key_record
        if type(key_record) is not BundleKeyRecord:
            raise _fixed("the admission parent key record must be the actual closed record")
        # The SHARED O(1) key-record preflight (the existing
        # closure, reused unchanged): field existence, the
        # member/class containers at the ACTUAL carried
        # member-occurrence cap, the FOUR carried bound sets,
        # the ownership container gate and the O(1)
        # workspace character bound -- all BEFORE the member
        # length feeds any reservation.
        _s_key_record_preflight_shape(key_record)
        total_members += len(key_record.member_occurrences)
    if total_members > ns.bounds.max_member_occurrences:
        raise _fixed("the retained member total exceeds the actual inherited member cap")

    # (2) phase 0/1: the closed field fences and the ELEVEN bound
    # sets at their expected-class field counts (the target's
    # per-field range walks).
    reserver.reserve(
        1
        + sum(
            1 + len(cls.model_fields)
            for cls in (
                RootRegionGraphBounds,
                RootRegionCurrentnessBounds,
                CurrentGraphBounds,
                CurrentnessBounds,
                BundleAdmissionBounds,
                BundleProofBounds,
                GraphBounds,
                ObservationBounds,
                HistoryBounds,
                RootLineageBounds,
                CurrentAdmissionBounds,
            )
        )
    )
    # (3) phase 1b: the closed count gates, the counter fences
    # and the admission-reason set/sort/comparison walks.
    reserver.reserve(1 + n_r + n_r * max(1, n_r.bit_length()) + n_r)
    # (4) phase 2: the shape gates -- ten 64-hex checks (the P/D/
    # R keys, the five namespace keys, the config fingerprint) at
    # their closed 64-length set visits, the five identity texts
    # at their check-plus-encode walks, the workspace and
    # lineage-id at their closed walks, the nine version pairs.
    reserver.reserve(
        1
        + 10 * (1 + 144)
        + 2
        * (
            len(ns.principal)
            + len(ns.session)
            + len(ns.repository)
            + len(ns.route)
            + len(ns.model_identity)
        )
        + 1
        + 3 * len(ns.workspace)
        + 1
        + 2 * len(ns.lineage_id)
        + 10
    )
    # (5) phase 2: the nested Q/P-selection/F/E evidence re-joins
    # at their ACTUAL record counts; each element walk is
    # reserved at its closed per-element ceiling BEFORE it runs,
    # and every element is fenced to its ACTUAL closed class and
    # field set before its lengths feed the arithmetic.
    if q is not None:
        reserver.reserve(1 + 11 * n_qw)
        witness_units = 0
        for witness in q.uncertainty_witnesses:
            if type(witness) is not RootRegionUncertaintyWitness:
                raise _fixed("the retained uncertainty witness must be the actual closed record")
            if not _r_fields_present(witness, ("call_id", "occurrence")):
                raise _fixed("the retained uncertainty witness must carry its closed fields")
            witness_call = witness.call_id
            if not isinstance(witness_call, str):
                raise _fixed("the retained uncertainty witness call id must be closed UTF-8 text")
            witness_occurrence = witness.occurrence
            if type(witness_occurrence) is not CompletedReadOccurrence:
                raise _fixed("the retained witness occurrence must be the actual closed record")
            if not _r_fields_present(witness_occurrence, ("call_id",)):
                raise _fixed("the retained witness occurrence must carry its closed call field")
            occurrence_call = witness_occurrence.call_id
            if not isinstance(occurrence_call, str):
                raise _fixed("the retained witness occurrence call id must be closed UTF-8 text")
            # The two 64-hex checks, the call-id check/isspace/
            # encode walks, plus the closed upper bound over the
            # occurrence/result/proof/provenance joins (each
            # provenance variant walks the carried call identity
            # and the namespace workspace).
            witness_units += (
                1
                + 2 * (1 + 144)
                + 3 * len(witness_call)
                + 3 * (1 + 144)
                + 3 * (2 * len(occurrence_call))
                + 2 * len(ns.workspace)
                + 2
            )
        reserver.reserve(
            1
            + 2 * (1 + 144)
            + (1 + 144 if q.usable_selected_source_digest is not None else 0)
            + 1
            + n_qd
            + n_qd
            + n_qd * max(1, n_qd.bit_length())
            + n_qd
            + witness_units
            + 2 * n_qw
            + n_qw
            + n_qw * max(1, n_qw.bit_length())
            + n_qw
            + n_qw
        )
    if p_selection is not None:
        p_facts = p_selection.witness_facts
        # The closed per-fact fence ceiling derived from the
        # ACTUAL field tuple widths: the fact's closed field set
        # plus the WIDEST actual provenance variant field set
        # (the region variant), plus the three dispatch
        # isinstance and the call-id text check (the worst-case
        # region path).
        fact_fence_ceil = (
            len(_S_P_FACT_FIELDS)
            + max(
                len(_R_ENVELOPE_PROV_FIELDS),
                len(_R_READ_PROV_FIELDS),
                len(_R_REGION_PROV_FIELDS),
            )
            + 3
            + 1
        )
        reserver.reserve(1 + fact_fence_ceil * n_pf)
        fact_units = 0
        for fact in p_facts:
            if type(fact) is not RootRegionLineageFact:
                raise _fixed("the retained P selection fact must be the actual closed record")
            if not _r_fields_present(fact, _S_P_FACT_FIELDS):
                raise _fixed("the retained P selection fact must carry its closed field set")
            provenance = fact.provenance
            if isinstance(provenance, EnvelopeRootProvenance):
                if not _r_fields_present(provenance, _R_ENVELOPE_PROV_FIELDS):
                    raise _fixed(
                        "the retained fact provenance must carry its closed variant fields"
                    )
                # Only the actual envelope variant legitimately
                # carries no call id.
                fact_call = ""
            elif isinstance(provenance, ReadRootProvenance):
                if not _r_fields_present(provenance, _R_READ_PROV_FIELDS):
                    raise _fixed(
                        "the retained fact provenance must carry its closed variant fields"
                    )
                fact_call = provenance.call_id
                if not isinstance(fact_call, str):
                    raise _fixed("the retained fact provenance call id must be closed UTF-8 text")
            elif isinstance(provenance, RootRegionReadProvenance):
                if not _r_fields_present(provenance, _R_REGION_PROV_FIELDS):
                    raise _fixed(
                        "the retained fact provenance must carry its closed variant fields"
                    )
                fact_call = provenance.call_id
                if not isinstance(fact_call, str):
                    raise _fixed("the retained fact provenance call id must be closed UTF-8 text")
            else:
                raise _fixed("the retained fact provenance must be the actual closed union")
            # The fact fence, its 64-hex source digest, and the
            # closed upper bound over its provenance variant
            # (one 64-hex check plus the carried call identity and
            # the namespace workspace walks).
            fact_units += (
                1 + (1 + 144) + 1 + (1 + 144) + 2 * (2 * len(fact_call)) + 2 * len(ns.workspace) + 2
            )
        reserver.reserve(
            1
            + (1 + 144)
            + 1
            + (1 + 144 if p_selection.selected_source_digest is not None else 0)
            + fact_units
            + 1
        )
    f_result = r.f_result
    if f_result is not None:
        f_graph = f_result.overlay
        if f_graph is not None:
            reserver.reserve(
                1
                + 1
                + 4
                + 1
                + 2 * len(f_graph.workspace)
                + 2
                * (
                    len(f_graph.graph_version)
                    + len(f_graph.reference_version)
                    + len(f_graph.proof_version)
                )
                + 1
                + len(CurrentGraphBounds.model_fields)
                + 2 * len(f_graph.root_path)
            )
    if r.e_overlay is not None:
        # The ACTUAL four closed text shape fences (the shared
        # nested fence) BEFORE any E length calculation: a
        # malformed copied overlay refuses with the ACTUAL
        # fixed private error, never a raw len() TypeError.
        if (
            not isinstance(r.e_overlay.workspace, str)
            or not isinstance(r.e_overlay.policy_version, str)
            or not isinstance(r.e_overlay.history_key, str)
            or not isinstance(r.e_overlay.scope_key, str)
        ):
            raise _fixed("the E overlay context fields must be closed text")
        # The carried E overlay header lengths close under the
        # ORIGINAL overlay caps (workspace 1..1024, policy
        # version 1..128, the two 64-hex identity keys exactly
        # 64) BEFORE any length feeds the E reservation below
        # (the actual overlay law, reused; a copied oversized
        # header refuses with the fixed private error, never a
        # charge-sized walk).
        if not 1 <= len(r.e_overlay.workspace) <= 1024:
            raise _fixed("the carried E overlay workspace must carry closed bounded text")
        if not 1 <= len(r.e_overlay.policy_version) <= 128:
            raise _fixed("the carried E overlay policy version must carry closed bounded text")
        if len(r.e_overlay.history_key) != 64:
            raise _fixed("the carried E overlay history key must carry closed 64-length text")
        if len(r.e_overlay.scope_key) != 64:
            raise _fixed("the carried E overlay scope key must carry closed 64-length text")
        # The closed E overlay law re-run at its ACTUAL checks
        # (the shared nested fence): the class fence, the SIX
        # carried identity headers, the four closed text fences,
        # the TWO 64-hex identity-key checks at their closed
        # 64-length set visits, the policy identity comparison,
        # the revision scalar fence, the bound-set closure at
        # its actual field count and the namespace workspace
        # join.  No tuple collection is walked at this
        # boundary (the overlay's own validators closed them at
        # construction; the parent re-run performs no tuple-
        # element work here).
        reserver.reserve(
            1
            + len(_R_E_OVERLAY_FIELDS)
            + 4
            + 2 * (1 + 144)
            + 1
            + 2
            + 1
            + len(CurrentnessBounds.model_fields)
            + 2
            + len(r.e_overlay.workspace)
            + len(ns.workspace)
        )
    # (6) phase 2: the COMPLETE closed R result law re-run.
    reserver.reserve(1)
    # The R scope key re-derivation: the 24-element join walk,
    # the payload UTF-8 ceiling (four bytes per character is the
    # structural ceiling) and its domain-prefixed SHA-256.
    r_scope_parts = (
        r.contract_version,
        r.policy_version,
        ROOT_REGION_CURRENTNESS_CONTRACT_VERSION,
        ROOT_REGION_CURRENTNESS_POLICY_VERSION,
        CURRENT_GRAPH_CONTRACT_VERSION,
        CURRENT_GRAPH_POLICY_VERSION,
        CURRENTNESS_CONTRACT_VERSION,
        CURRENTNESS_POLICY_VERSION,
        r.state.lineage_key,
        str(r.bounds.max_total_work_units),
        str(r.bounds.max_diagnostics),
        str(r.q_bounds.max_total_work_units),
        str(r.q_bounds.max_diagnostics),
        str(r.f_bounds.max_total_work_units),
        str(r.f_bounds.max_diagnostics),
        str(r.e_bounds.max_paths),
        str(r.e_bounds.max_groups),
        str(r.e_bounds.max_witness_memberships),
        str(r.e_bounds.max_relation_pairs),
        str(r.e_bounds.max_work_units),
        str(r.e_bounds.max_diagnostics),
        r.graph_version,
    )
    r_scope_chars = sum(len(part) for part in r_scope_parts) + 23
    reserver.reserve(24 + r_scope_chars + 2 * (27 + 4 * r_scope_chars) + 104)
    # The R diagnostic sorted/dedup walk.
    reserver.reserve(n_rd + n_rd * max(1, n_rd.bit_length()) + n_rd)
    # The resolved-source content law re-run: the 64-hex shape
    # walk, the no-copy capped measurement visits and the owned
    # encode/hash (the target's single pass set).
    reserver.reserve(1 + (1 + 144))
    reserver.reserve(src_chars)
    reserver.reserve(2 * src_bytes + 104)
    # The nested Q scope join: the 5-element join walk, its UTF-8
    # ceiling and its domain-prefixed SHA-256.
    if q is not None:
        q_scope_parts = (
            q.contract_version,
            q.policy_version,
            q.state.lineage_key,
            str(q.bounds.max_total_work_units),
            str(q.bounds.max_diagnostics),
        )
        q_scope_chars = sum(len(part) for part in q_scope_parts) + 4
        reserver.reserve(1 + 5 + q_scope_chars + 2 * (33 + 4 * q_scope_chars) + 104)
    # The F graph scope re-derivations over the actual same-run
    # F evidence and the E overlay's own currentness scope: the
    # F currentness scope key (the accepted E recipe), the F
    # graph scope key (its 15-element recipe with the THREE
    # bound sets embedded as JSON strings) and the E overlay
    # currentness scope key (the same E recipe over the
    # overlay's own fields).  The ACTUAL recipes are
    # json.dumps-ed payload arrays with compact separators
    # whose UTF-8 encoding is SHA-256-ed (the ensure_ascii
    # output is pure ASCII, so the closed JSON length ceiling
    # IS the target's byte ceiling): brackets, a separator
    # before every element but the first, a quote pair per
    # element and the ensure_ascii escaped body per element;
    # every bound-set dump enters as a JSON string, so its key
    # quotes escape once more (2 + L + 2 * field count).  The
    # precharge's OWN ceiling calculations are charged work,
    # each reserved BEFORE its walk runs, and the target's
    # dump/dumps/encode/SHA passes are reserved BEFORE the
    # target may run them.
    if f_graph is not None or r.e_overlay is not None:
        _scope_sets: list[BaseModel] = []
        if f_graph is not None:
            _scope_sets.extend((f_graph.currentness_bounds, f_graph.bounds, f_graph.graph_bounds))
        if r.e_overlay is not None:
            _scope_sets.append(r.e_overlay.bounds)
        # (a) the dump-meta construction (field counts,
        # per-field bit widths and name lengths) over the
        # DISTINCT carried bound sets, reserved at its closed
        # 6 + 6*n pass per set BEFORE it walks the values (the
        # sets are closed under their original hard ranges, so
        # the bit widths are bounded).
        reserver.reserve(sum(6 + 6 * len(type(bound).model_fields) for bound in _scope_sets))
        _scope_set_meta = tuple(
            (
                len(type(bound).model_fields),
                sum(1 + getattr(bound, field).bit_length() for field in type(bound).model_fields),
                sum(len(field) for field in type(bound).model_fields),
            )
            for bound in _scope_sets
        )
        # (b) the ensure_ascii escaped-ceiling walks at their
        # carried string lengths (the two recipe version
        # constants plus every carried scope header), reserved
        # BEFORE they run.
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
        if r.e_overlay is not None:
            _scope_texts.extend(
                (
                    r.e_overlay.policy_version,
                    r.e_overlay.history_key,
                    r.e_overlay.workspace,
                )
            )
        reserver.reserve(sum(1 + len(text) for text in _scope_texts))
        _scope_esc = tuple(_s_json_string_escaped_ceil(text) for text in _scope_texts)
        # (c) the exact bound-set JSON length calculations at
        # their closed dump walks, reserved BEFORE they run.
        reserver.reserve(sum(1 + 2 * (2 * nf + nc + du) for nf, du, nc in _scope_set_meta))
        _scope_set_lens = tuple(_s_bound_set_json_len(bound) for bound in _scope_sets)
        # (d) the closed JSON-array length ceilings of the
        # actual element recipes (the bracket/separator/quote
        # counts and the escaped-body sums), reserved as their
        # own calculation.
        reserver.reserve(3 + 6 + 15 + 6)
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
            reserver.reserve(
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
            # F validator may re-derive it.
            reserver.reserve(
                1
                + sum(1 + 2 * (2 * nf + nc + du) for nf, du, nc in _scope_set_meta[0:3])
                + fgr_payload_ceil
                + 2 * fgr_payload_ceil
                + 104
                + 1
            )
        if r.e_overlay is not None:
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
            reserver.reserve(
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
    # (7) phase 3: the closed D-namespace re-derivation and
    # P lineage-key component (its own O(1) field/bound
    # closure, its charged ceiling calculations and the
    # actual D-validator / lineage-key recipe work reserved
    # before the target; the returned canonical ceiling
    # feeds the entry-scope joins below).
    _s_parent_namespace_precharge_closed(reserver, ns)
    # (8) phase 4/5/6/8: the leaf law re-run and the entry-set /
    # reverse-index / counter walks.  BOTH row kinds reuse the
    # ACTUAL component contracts, each reserved before its
    # target may run: the ROOT row's closed entry fence pool,
    # the canonical metadata (whose closed O(1) record shape
    # gate refuses before any character walk, then the leaf
    # rekey plus the parent scope-join re-derivation/comparison)
    # and the root content pass (the 64-hex shape walk, the
    # no-copy capped measurement and the owned encode/hash,
    # including the target's repeated passes); the FILE row the
    # same canonical component, its own closed B-domain
    # population caps BEFORE the helper's metadata walks, the
    # region component at the entry's OWN carried B domain and
    # the M04 owner/witness joins at the ACTUAL inherited
    # owner-domain ceilings (the safe structural upper bounds
    # before any owner lookup -- never the entry's own lengths
    # and never a new fixed cap).
    if not _r_fields_present(root_entry, _S_ENTRY_FIELDS):
        raise _fixed("the admission entry must carry its closed fields")
    # The ROOT row's resolved source is the ACTUAL R resolved
    # source BY IDENTITY (the target's first root-source gate;
    # the source is already class/field/scalar-fenced at the
    # opening): a foreign or partial source refuses before any
    # fence-pool reservation or content character walk, never
    # by an attribute error.
    if root_entry.root_source is not source:
        raise _fixed("the root entry carries the actual R resolved source by identity")
    # The ROOT row's non-walk O(1) pool: the entry scalar/enum
    # re-fences and root-variant empty gates, the content-key
    # 64-hex comparison walk, the record/entry binding and root
    # sole-group checks and the resolved-source local joins
    # (kind/provenance dispatch, the occurrence/call/endpoint
    # joins and the fact root-body equality) -- the walked and
    # rekeyed passes are the components' own charged
    # reservations.
    reserver.reserve(1 + len(_S_ENTRY_FIELDS) + 14 + 64 + 40 + 55)
    _s_canonical_metadata_precharge_closed(reserver, root_entry.key_record, parent_ns=ns)
    _s_root_content_precharge_closed(
        reserver,
        source.root_text,
        source.root_digest,
        source.root_byte_length,
    )
    reserver.reserve(n_facts + 1)
    reserver.reserve(n_occ)
    # The FILE originality index the target builds ONCE before
    # the FILE loop (a hash plus a dict insert per retained
    # occurrence), reserved before the loop runs.
    reserver.reserve(2 * n_occ)
    for entry in entries:
        # The entry field-existence fence (the leaf's exact
        # channel) BEFORE any entry dereference: a partial
        # real-class entry copy refuses with the fixed private
        # error, never an AttributeError.
        if not _r_fields_present(entry, _S_ENTRY_FIELDS):
            raise _fixed("the admission entry must carry its closed fields")
        entry_proof = entry.proof
        if entry_proof is None:
            raise _fixed("a file entry keeps its retained original proof")
        if not isinstance(entry_proof, BundleProof):
            raise _fixed("a file entry keeps its retained original proof")
        if (
            not _r_fields_present(entry_proof, ("segments", "requested_members", "source_text"))
            or not isinstance(entry_proof.segments, tuple)
            or not isinstance(entry_proof.requested_members, tuple)
            or not isinstance(entry_proof.source_text, str)
        ):
            raise _fixed("the retained file proof must carry its closed content fields")
        if not isinstance(entry.admitted_segments, tuple) or not isinstance(entry.witnesses, tuple):
            raise _fixed("the entry admitted segments must carry the closed tuple container")
        n_seg = len(entry_proof.segments)
        n_mem = len(entry_proof.requested_members)
        n_a = len(entry.admitted_segments)
        n_w = len(entry.witnesses)
        # The canonical component's closed O(1) record shape
        # gate (zero units) closes the record's FOUR carried
        # bound sets BEFORE any cap read below; it then reserves
        # and runs the leaf's shared record fence, the canonical
        # rekey and the parent scope-join re-derivation/
        # comparison -- the target's actual passes, reserved
        # before its target may run.
        _s_canonical_metadata_precharge_closed(reserver, entry.key_record, parent_ns=ns)
        # The O(1) B-domain population caps (the entry's OWN
        # retained proof under its ACTUAL carried original B
        # bound sets, the admitted count under the retained
        # segment domain and the witness count under the ACTUAL
        # carried G association domain) close BEFORE the
        # helper's metadata walks and every element traversal.
        if n_seg > entry.key_record.proof_bounds.max_segments:
            raise _fixed("the retained proof segments exceed the actual carried proof cap")
        if n_mem > entry.key_record.proof_bounds.max_members:
            raise _fixed("the retained proof members exceed the actual carried proof cap")
        if n_a > n_seg:
            raise _fixed("admitted segments exceed the actual proof segment domain before any walk")
        if n_w > entry.key_record.admission_bounds.max_reverse_associations:
            raise _fixed(
                "the entry witnesses exceed the actual carried association domain before any walk"
            )
        # The ACTUAL inherited owner-domain upper bounds (the
        # owner proof's segment/member populations are closed
        # under the same carried original B bounds at the M04
        # join): the safe structural upper domain before any
        # owner lookup -- never the entry's own lengths and
        # never a new fixed cap.
        s_cap = ns.proof_bounds.max_segments
        m_cap = ns.proof_bounds.max_members
        # (helper walk 1) the segment population's member-
        # position total, reserved at its closed per-element
        # ceiling BEFORE it runs: the concrete segment class,
        # the closed field existence and the closed nonempty
        # member-position container (the leaf's exact channels)
        # close each element before its len is read, and each
        # member-position length closes under the entry's OWN
        # requested-occurrence domain BEFORE it feeds the next
        # reservation.
        reserver.reserve(10 * n_seg)
        pos_total = 0
        for segment in entry_proof.segments:
            if type(segment) is not BundleSegment:
                raise _fixed(
                    "the retained proof segments must be the actual concrete segment records"
                )
            if not _r_fields_present(segment, _S_SEGMENT_FIELDS):
                raise _fixed("the retained proof segments must carry their closed metadata")
            if not isinstance(segment.member_positions, tuple) or not segment.member_positions:
                raise _fixed("retained segment member positions must carry a closed nonempty tuple")
            if len(segment.member_positions) > n_mem:
                raise _fixed(
                    "segment member positions exceed the actual requested "
                    "occurrence domain before any walk"
                )
            pos_total += len(segment.member_positions)
        # (helper walk 2) the leaf's COMPLETE segment population
        # closure re-run (charged helper work, the leaf's exact
        # channels): the closed nonnegative lengths and the
        # per-position scalar fences (the field existence and
        # the requested-occurrence domain close in walk 1
        # before any length feeds a reservation).
        reserver.reserve(11 * n_seg + 3 * pos_total)
        for segment in entry_proof.segments:
            if (
                isinstance(segment.char_length, bool)
                or not isinstance(segment.char_length, int)
                or segment.char_length < 0
                or isinstance(segment.byte_length, bool)
                or not isinstance(segment.byte_length, int)
                or segment.byte_length < 0
            ):
                raise _fixed("retained segment metadata must carry closed nonnegative lengths")
            for position in segment.member_positions:
                if isinstance(position, bool) or not isinstance(position, int) or position < 0:
                    raise _fixed(
                        "retained segment member positions must carry closed nonnegative indices"
                    )
        # (helper walk 3) the admitted-index closure (the
        # leaf's exact channels and precedence) BEFORE the
        # region metadata dereferences any segment by index.
        reserver.reserve(4 * n_a + 1)
        previous = -1
        for position in entry.admitted_segments:
            if (
                isinstance(position, bool)
                or not isinstance(position, int)
                or position < 0
                or position <= previous
            ):
                raise _fixed("admitted segment indices must be distinct and increasing")
            previous = position
        if previous >= n_seg:
            raise _fixed("admitted segment indices must index the proof segments")
        # (helper walk 4) the admitted region's declared
        # character/byte metadata (three visits per admitted
        # index), reserved before the walk.
        reserver.reserve(3 * n_a)
        region_chars = 0
        region_bytes = 0
        for position in entry.admitted_segments:
            segment = entry_proof.segments[position]
            region_chars += segment.char_length
            region_bytes += segment.byte_length
        n_mem_entry = len(entry.key_record.member_occurrences)
        # The leaf re-run's remaining actual passes, reserved in
        # the target order at their closed per-element ceilings:
        # the entry-level O(1) pool and the member-class vector
        # walks (four visits per member), the retained
        # requested-member closure (eleven shape checks per
        # member), the witness canonical order/dedup re-run (its
        # O(1) pool -- the 64-hex occurrence-id walk -- plus its
        # five-check index traversal bounded by the ACTUAL
        # carried B segment domain), the complete segment
        # population closure (fifteen per segment plus three
        # per member position), the partition total, the region
        # metadata cap joins, the whole-bundle plan gates (the
        # range snapshot build plus comparison and the
        # position-equality walk), the membership set, the leaf
        # region walk (two per segment, six per admitted
        # position, one slice per admitted segment), the
        # admitted-tuple comparison, the group partition join
        # (eight per group plus two per member) and the width
        # set.
        reserver.reserve(1 + len(_S_ENTRY_FIELDS) + 40 + 4 * n_mem)
        reserver.reserve(11 * n_mem)
        reserver.reserve(n_w * (241 + 5 * s_cap))
        reserver.reserve(15 * n_seg + 3 * pos_total)
        reserver.reserve(n_seg + 1)
        reserver.reserve(3 * n_a + 3)
        reserver.reserve(2 + 3 * n_seg)
        reserver.reserve(n_a)
        reserver.reserve(2 * n_seg + 6 * pos_total + n_a)
        reserver.reserve(n_mem + n_mem_entry)
        # The region's owned slice/join/encode/hash passes (and
        # the no-copy capped measurement) through the ACTUAL
        # region component at the entry's OWN carried B domain
        # (the whole-bundle shape takes the genuine fast path:
        # zero slice/join character work).
        _s_region_precharge_closed(
            reserver,
            entry_proof.source_text,
            entry_proof.segments,
            entry.admitted_segments,
            region_chars,
            region_bytes,
            entry.key_record.graph_bounds.max_single_source_bytes,
            entry.key_record.proof_bounds,
        )
        reserver.reserve(8 * n_a + 2 * n_mem)
        reserver.reserve(n_mem + 1)
        # The M04 owner join: the FIRST retained proof's owning
        # occurrence search (one identity visit per retained
        # occurrence), the owner's complete owning-result join
        # (its O(1) pool, the per-result fields/container
        # rebuild and the per-piece producer association at the
        # precharged retained piece maximum), the occurrence-id
        # membership scan, and -- per witness -- the original-
        # occurrence lookup (a dict get plus the three original
        # coordinate joins), the witness owner's owning-result
        # join and the witness region-compatibility re-
        # derivation (its O(1) pool with the two 64-hex walks,
        # the five-check index traversal, the plan gate, the
        # owner member closure, the per-segment metadata fences,
        # the member-position join (its nested per-segment
        # walk bounded by the carried B domain product under
        # the per-segment count gate) and the group partition
        # join, every owner-side population bounded by the
        # ACTUAL carried original B domain before any owner
        # lookup).
        reserver.reserve(n_occ)
        reserver.reserve(17 + 17 * n_res + 26 * n_pieces_max)
        reserver.reserve(1 + 2 * n_w)
        # The witness region-compatibility ceiling at the
        # ACTUAL inherited owner-domain ceilings: the O(1)
        # pool (the two 64-hex walks included), the per-owner-
        # segment fences, the owner member closure, the entry
        # key-occurrence join, and the nested member-position
        # walk over EVERY selected owner segment -- the
        # per-segment count gate bounds each inner walk by
        # m_cap BEFORE it runs, so the closed nested domain is
        # s_cap * m_cap positions (twelve visits per position:
        # the scalar fence, the requested-members get, the
        # resolved-text check and the admitted append, plus
        # one admitted-sequence tuple read per position).
        region_compat_ceil = 312 + 23 * s_cap + 21 * m_cap + 13 * s_cap * m_cap + n_mem_entry
        reserver.reserve(n_w * (5 + 17 + 17 * n_res + 26 * n_pieces_max + region_compat_ceil))
    reserver.reserve(1 + 3 * n_e)
    # The reverse-index footer: the expected key-set build over
    # every member occurrence, the row field/flag fences and the
    # path-order comparison (the sorted path list at its closed
    # n*log(n) bound), the per-row scoped-key/root-flag joins
    # and the per-row expected content-key comparison -- each
    # row's expected set is SORTED before comparison, so the
    # closed per-row sort bound (at most the root key plus every
    # FILE key) is charged with the linear row passes.
    reserver.reserve(
        total_members
        + 2 * n_rows
        + n_rows
        + n_rows * max(1, n_rows.bit_length())
        + 3 * n_rows
        + n_rows * 3 * (1 + n_e)
        + n_rows * (1 + n_e) * max(1, (1 + n_e).bit_length())
    )
    reserver.reserve(1 + total_members)
    # (9) phase 9: the S model scope key re-derivation at its
    # closed canonical ceiling.
    s_scope_strings = (
        state.lineage_key,
        ROOT_REGION_ADMISSION_MODELS_CONTRACT_VERSION,
        ROOT_REGION_ADMISSION_MODELS_POLICY_VERSION,
        r.scope_key,
        CURRENT_ADMISSION_CONTRACT_VERSION,
        CURRENT_ADMISSION_POLICY_VERSION,
    )
    g_fields = len(CurrentAdmissionBounds.model_fields)
    reserver.reserve(
        1
        + 2 * (1 + 144)
        + 2
        * (
            len(ROOT_REGION_ADMISSION_MODELS_CONTRACT_VERSION)
            + len(ROOT_REGION_ADMISSION_MODELS_POLICY_VERSION)
            + len(CURRENT_ADMISSION_CONTRACT_VERSION)
            + len(CURRENT_ADMISSION_POLICY_VERSION)
        )
        + 1
        + g_fields
        + 7
        + sum(len(value) for value in s_scope_strings)
        + g_fields
    )
    # The G-bounds dump-meta (field count, per-field bit width,
    # name lengths), reserved at its closed 6 + 6*n pass BEFORE
    # it walks the values (the set is closed under the original
    # hard ranges, so the bit widths are bounded).
    reserver.reserve(6 + 6 * g_fields)
    g_digit_units = sum(
        1 + getattr(g_bounds, field).bit_length() for field in CurrentAdmissionBounds.model_fields
    )
    g_name_chars = sum(len(field) for field in CurrentAdmissionBounds.model_fields)
    # The exact G-bounds JSON length calculation at its closed
    # dump walk, reserved BEFORE it runs.
    reserver.reserve(1 + 2 * (2 * g_fields + g_name_chars + g_digit_units))
    g_set_len = _s_bound_set_json_len(g_bounds)
    s_scope_ceil = 2 + 6
    for value in s_scope_strings:
        s_scope_ceil += 2 + _s_json_string_escaped_ceil(value)
    s_scope_ceil += 2 + g_set_len + 2 * g_fields
    # The target: its OWN inner G-bounds dump (model_dump plus
    # the compact JSON dumps that becomes the payload's inner
    # JSON string), the outer 7-element array serialization,
    # its UTF-8 encode and its prefix-free SHA-256, plus the
    # equality join.
    reserver.reserve(
        1
        + 1
        + 2 * (2 * g_fields + g_name_chars + g_digit_units)
        + s_scope_ceil
        + 2 * s_scope_ceil
        + 104
        + 1
    )


def _s_parent_namespace_precharge_closed(
    reserver: _SRegionWorkReserver,
    ns: RootRegionLineageNamespace,
) -> tuple[int, int, int]:
    """The closed NEW local reservation for the ADMISSION PARENT's
    D-namespace RE-DERIVATION and P lineage-key recipe ONLY (phase
    3 of the actual ``_v_admission`` carrying law, the versioned
    ``root-region-admission-precharge/v1`` recipe).

    SEPARATE component precharge contract: the caller supplies the
    typed bounded meter; the actual target (the parent constructor
    re-run) invokes the real ``CausalHistoryNamespace`` validators
    and the real ``_lineage_key`` recipe only after this returns.
    This component needs namespace METADATA ONLY: it closes the
    actual D-namespace fields under their inherited bound domains,
    precharges its own ceiling calculations, and reserves the real
    namespace/hash recipe work BEFORE the target.  It performs no
    P state / source / entry / witness traversal and earns no
    whole-operation claim.

    The reservation mirrors the ACTUAL target phase order:

    1.  the closed O(1) class / field-existence fences and the
        inherited-cap closure (the five identity texts, the config
        fingerprint, the FIVE 64-hex scope keys, the workspace
        under the ACTUAL graph path bound in its canonical form,
        the lineage id, the SEVEN D version fields, and the SIX
        bound sets each at its expected original class and its
        original hard ranges);
    2.  the closure WALKS, each reserved BEFORE it runs (the
        precharge's own fences are charged work);
    3.  the precharge's OWN ceiling calculations, each reserved
        BEFORE the walk that computes it: the dump-meta
        construction itself (three field passes per bound set at
        the ACTUAL original class field counts and the closed bit
        width under the ACTUAL original hard caps), the
        ensure_ascii JSON encoding ceiling per carried string,
        the exact compact bound-set JSON length per bound set,
        the ceiling dict assembly and the 16/23-element canonical
        payload ceilings;
    4.  the ACTUAL ``CausalHistoryNamespace`` re-derivation
        through the real D validators in the ACTUAL target order
        at the closed canonical ceilings: the outer field
        validators and the 25-field input assembly; the nested
        018-c admission re-derivation with its field walks, its
        canonical payload and its TWO domain-prefixed SHA-256
        (the FIRST canonical/2-SHA block); the HistoryBounds
        re-validation; the REPEATED canonical payload and its TWO
        recomputed 64-hex keys (the SECOND canonical/2-SHA block,
        the actual validator's key re-check); the validator's
        canonical workspace re-check under the ACTUAL graph path
        bound; the history-key canonical payload (18 strings plus
        the FIVE bound sets as JSON-STRING elements, every
        embedded key quote escaped) and its SHA-256; the
        state-scoped-key SHA-256; and the four recomputed-key and
        two state-join equality checks;
    5.  the ACTUAL ``_lineage_key`` recipe at its closed canonical
        ceiling (the bound-shape check, the target's bound dump
        walk, the domain-prefixed payload, its UTF-8 ceiling and
        its SHA-256) plus its equality check and the fixed
        lineage-tag comparisons at their ACTUAL target position.

    Every payload is reserved at a CLOSED ceiling derived from
    the actual field lengths (a ceiling can only over-charge the
    actual serializer, never under-charge it); no
    divide-by-constant, no amortized-away pass, no whole original
    proof/state body walk.  Returns ``(d_units, lineage_units,
    d_ceil)``: ``d_units`` sums the TARGET-phase reservations
    (the precharge's own fence and calculation reservations are
    observable through the meter, not the tuple), ``lineage_
    units`` covers the recipe and its tag comparisons, and
    ``d_ceil`` is the closed canonical history-payload ceiling
    the later entry-scope joins serialize at.  This reserves the
    parent re-run's component work for the later whole-operation
    recipe; it earns no whole-operation bound and changes no old
    public law.
    """
    if reserver is None or not callable(getattr(reserver, "reserve", None)):
        raise _fixed(
            "the admission parent namespace precharge reserver must carry a typed reserve callback"
        )
    # (1) the closed O(1) class and field-existence fences,
    # BEFORE any dereference or reservation.
    if type(ns) is not RootRegionLineageNamespace:
        raise _fixed("the admission parent namespace must be the actual closed record")
    if not _r_fields_present(ns, _S_NS_FIELDS):
        raise _fixed("the admission parent namespace must carry the closed field set")
    identity_texts = (
        ns.principal,
        ns.session,
        ns.repository,
        ns.route,
        ns.model_identity,
    )
    if any(not isinstance(value, str) for value in identity_texts):
        raise _fixed("the carried namespace identity texts must carry closed strings")
    if not (
        1 <= len(ns.principal) <= 256
        and 1 <= len(ns.session) <= 256
        and 1 <= len(ns.repository) <= 256
        and 1 <= len(ns.route) <= 64
        and 1 <= len(ns.model_identity) <= 256
    ):
        raise _fixed("the carried namespace identity texts must be within the actual closed ranges")
    if not isinstance(ns.config_fingerprint, str):
        raise _fixed("the carried namespace config fingerprint must carry a closed string")
    scope_keys = (
        ns.admission_namespace_key,
        ns.admission_scoped_key,
        ns.history_key,
        ns.state_scoped_key,
        ns.lineage_key,
    )
    if any(not isinstance(value, str) for value in scope_keys):
        raise _fixed("the carried namespace scope keys must carry closed strings")
    workspace = ns.workspace
    if not isinstance(workspace, str) or not 1 <= len(workspace) <= 1024:
        raise _fixed("the carried namespace workspace must be 1..1024 characters")
    lineage_id = ns.lineage_id
    if not isinstance(lineage_id, str) or not 1 <= len(lineage_id) <= 128:
        raise _fixed("the carried namespace lineage id must be 1..128 non-space characters")
    d_versions = (
        ns.admission_version,
        ns.observation_version,
        ns.graph_version,
        ns.reference_version,
        ns.proof_version,
        ns.history_version,
        ns.arguments_version,
    )
    if any(not isinstance(value, str) for value in d_versions):
        raise _fixed("the carried namespace version fields must carry closed strings")
    if any(not 1 <= len(value) <= 128 for value in d_versions):
        raise _fixed("the carried namespace version fields must be 1..128 non-space characters")
    if not isinstance(ns.contract_version, str) or not isinstance(ns.policy_version, str):
        raise _fixed("the carried namespace lineage tags must carry closed strings")
    if not isinstance(ns.mode, AdmissionMode):
        raise _fixed("the carried namespace mode must be the actual closed enum member")
    # The SIX bound sets at their expected original classes and
    # original hard ranges (the accepted closed O(1) bound fence:
    # a partial/forged/foreign copy refuses before any cap is
    # read or serialized; a valid stricter copy stays legal by
    # value).
    if not _s_bounds_set_closed(ns.bounds, BundleAdmissionBounds):
        raise _fixed("the carried namespace admission bound set must be the actual closed record")
    if not _s_bounds_set_closed(ns.proof_bounds, BundleProofBounds):
        raise _fixed("the carried namespace proof bound set must be the actual closed record")
    if not _s_bounds_set_closed(ns.graph_bounds, GraphBounds):
        raise _fixed("the carried namespace graph bound set must be the actual closed record")
    if not _s_bounds_set_closed(ns.observation_bounds, ObservationBounds):
        raise _fixed("the carried namespace observation bound set must be the actual closed record")
    if not _s_bounds_set_closed(ns.history_bounds, HistoryBounds):
        raise _fixed("the carried namespace history bound set must be the actual closed record")
    if not _s_bounds_set_closed(ns.root_lineage_bounds, RootLineageBounds):
        raise _fixed(
            "the carried namespace root-lineage bound set must be the actual closed record"
        )
    if len(workspace) > ns.graph_bounds.max_path_bytes:
        raise _fixed(
            "the carried namespace workspace must be the canonical absolute POSIX "
            "path under the actual configured path bound"
        )
    # (2) the closure WALKS, each reserved BEFORE it runs (the
    # precharge's own fences are charged work): the UTF-8 encode
    # walks, the six 64-hex checks at their closed char visits,
    # the version/lineage-id non-space scans (the lineage id is
    # scanned once for spaces AND encoded, two visits per char)
    # and the canonical workspace walk at its closed ceiling.
    reserver.reserve(
        1
        + sum(len(value) for value in identity_texts)
        + len(workspace)
        + 2 * len(lineage_id)
        + 6 * (1 + 2 * 64)
        + sum(1 + len(value) for value in d_versions)
        + 1
        + 15 * len(workspace)
    )
    for value in identity_texts:
        try:
            value.encode("utf-8")
        except UnicodeEncodeError:
            raise _fixed("the carried namespace identity texts must be valid UTF-8") from None
    _check_hex64(ns.config_fingerprint, "the carried namespace config fingerprint")
    _check_hex64(ns.admission_namespace_key, "the carried namespace admission_namespace_key")
    _check_hex64(ns.admission_scoped_key, "the carried namespace admission_scoped_key")
    _check_hex64(ns.history_key, "the carried namespace history_key")
    _check_hex64(ns.state_scoped_key, "the carried namespace state_scoped_key")
    _check_hex64(ns.lineage_key, "the carried namespace lineage_key")
    try:
        workspace.encode("utf-8")
    except UnicodeEncodeError:
        raise _fixed("the carried namespace workspace must be valid UTF-8") from None
    if validate_workspace(workspace, ns.graph_bounds.max_path_bytes) != workspace:
        raise _fixed(
            "the carried namespace workspace must be the canonical absolute POSIX "
            "path under the actual configured path bound"
        )
    if any(char.isspace() for char in lineage_id):
        raise _fixed("the carried namespace lineage id must be 1..128 non-space characters")
    try:
        lineage_id.encode("utf-8")
    except UnicodeEncodeError:
        raise _fixed("the carried namespace lineage id must be valid UTF-8") from None
    for value in d_versions:
        if any(char.isspace() for char in value):
            raise _fixed("the carried namespace version fields must be 1..128 non-space characters")
    # (3) the precharge's OWN ceiling calculations, each
    # reserved BEFORE the walk that computes it.
    esc_names = (
        "principal",
        "session",
        "repository",
        "route",
        "model_identity",
        "config_fingerprint",
        "workspace",
        "admission_version",
        "observation_version",
        "graph_version",
        "reference_version",
        "proof_version",
        "history_version",
        "arguments_version",
        "lineage_id",
        "admission_namespace_key",
        "admission_scoped_key",
    )
    dump_names = (
        "bounds",
        "proof_bounds",
        "graph_bounds",
        "observation_bounds",
        "history_bounds",
        "root_lineage_bounds",
    )
    dump_field_counts = tuple(
        len(cls.model_fields)
        for cls in (
            BundleAdmissionBounds,
            BundleProofBounds,
            GraphBounds,
            ObservationBounds,
            HistoryBounds,
            RootLineageBounds,
        )
    )
    # The dump_meta CONSTRUCTION itself is charged work,
    # reserved BEFORE the tuple is built: three field passes per
    # bound set (the field count, the bit-length sum, the key-
    # length sum) at the ACTUAL original class field counts (the
    # exact classes are fenced above, so the counts are closed
    # structural facts), plus the per-field bit width under the
    # ACTUAL original hard caps (the largest original ceiling is
    # 1073741824 = 2**30, so at most 31 per fenced value; the
    # per-field pass overhead is closed at 6).
    reserver.reserve(sum(6 + 6 * n_fields for n_fields in dump_field_counts))
    dump_meta = tuple(
        (
            len(type(getattr(ns, name)).model_fields),
            sum(
                1 + getattr(getattr(ns, name), field).bit_length()
                for field in type(getattr(ns, name)).model_fields
            ),
            sum(len(field) for field in type(getattr(ns, name)).model_fields),
        )
        for name in dump_names
    )
    # The ceiling CALCULATION itself is charged work, reserved
    # BEFORE it runs (walk-free closed lengths): the 18
    # ensure_ascii ceiling walks at their carried string lengths
    # (one visit per character, the accepted v1 convention), the
    # six exact bound-set JSON length computations at their
    # closed dump walks, the ceiling dict assembly (18 + 6
    # entries), the 16/23-element payload-ceiling loops and the
    # closed scalar ceiling arithmetic (the unit sums, the
    # lineage ceiling and the reservation expressions; a
    # structural count of the fixed recipe, never a data cap).
    reserver.reserve(
        sum(1 + len(getattr(ns, name)) for name in esc_names)
        + 1
        + len(ns.mode.value)
        + sum(
            1 + 2 * (2 * n_fields + name_chars + digit_units)
            for n_fields, digit_units, name_chars in dump_meta
        )
        + 18
        + 6
        + 16
        + 23
        + 512
    )
    esc_ceilings: dict[str, int] = {
        name: _s_json_string_escaped_ceil(getattr(ns, name)) for name in esc_names
    }
    esc_ceilings["mode"] = _s_json_string_escaped_ceil(ns.mode.value)
    dump_lengths: dict[str, int] = {
        name: _s_bound_set_json_len(getattr(ns, name)) for name in dump_names
    }
    # The closed canonical payload ceilings of the ACTUAL D
    # recipes.  The 16-element admission namespace payload and
    # the 23-element history-key payload are json.dumps-ed
    # arrays: each element carries a quote pair and every
    # element but the last a separator, so the bracket/separator
    # count runs over ALL 16/23 elements, not only the string
    # elements.  The bound sets enter as JSON STRINGS, so every
    # key quote inside their compact dumps escapes once more:
    # the embedded element is 2 + L_i + 2 * (field count), not
    # 2 + L_i.
    adm_string_names = (
        "principal",
        "session",
        "repository",
        "route",
        "model_identity",
        "config_fingerprint",
        "admission_version",
        "graph_version",
        "reference_version",
        "proof_version",
        "observation_version",
        "mode",
    )
    adm_bound_names = ("bounds", "proof_bounds", "graph_bounds", "observation_bounds")
    adm_payload_ceil = 2 + 15
    for name in adm_string_names:
        adm_payload_ceil += 2 + esc_ceilings[name]
    for position, name in enumerate(adm_bound_names):
        adm_payload_ceil += 2 + dump_lengths[name] + 2 * dump_meta[position][0]
    hist_string_names = adm_string_names + (
        "workspace",
        "history_version",
        "arguments_version",
        "lineage_id",
        "admission_namespace_key",
        "admission_scoped_key",
    )
    hist_bound_names = (
        "history_bounds",
        "bounds",
        "proof_bounds",
        "graph_bounds",
        "observation_bounds",
    )
    hist_bound_slots = (4, 0, 1, 2, 3)
    hist_payload_ceil = 2 + 22
    for name in hist_string_names:
        hist_payload_ceil += 2 + esc_ceilings[name]
    for position, name in enumerate(hist_bound_names):
        hist_payload_ceil += 2 + dump_lengths[name] + 2 * dump_meta[hist_bound_slots[position]][0]
    lineage_ceil = (
        67
        + 4 * len(ns.contract_version)
        + 4 * len(ns.policy_version)
        + dump_lengths["root_lineage_bounds"]
    )
    # (4) the ACTUAL CausalHistoryNamespace re-derivation
    # through the real D validators, in the ACTUAL target order,
    # at the closed canonical ceilings.
    identity_units = sum(2 + len(value) for value in identity_texts)
    text_units = 2 * (2 + len(ns.config_fingerprint) + len(workspace))
    d_version_units = sum(2 + len(value) for value in d_versions)
    adm_version_units = sum(
        2 + len(value)
        for value in (
            ns.admission_version,
            ns.observation_version,
            ns.graph_version,
            ns.reference_version,
            ns.proof_version,
        )
    )
    d_set_names = (
        "bounds",
        "proof_bounds",
        "graph_bounds",
        "observation_bounds",
        "history_bounds",
    )
    adm_set_names = ("bounds", "proof_bounds", "graph_bounds", "observation_bounds")
    d_set_units = sum(1 + len(type(getattr(ns, name)).model_fields) for name in d_set_names)
    adm_set_units = sum(1 + len(type(getattr(ns, name)).model_fields) for name in adm_set_names)
    adm_dump_walk = sum(
        1 + 2 * (2 * n_fields + name_chars + digit_units)
        for n_fields, digit_units, name_chars in dump_meta[:4]
    )
    hist_dump_walk = sum(
        1 + 2 * (2 * n_fields + name_chars + digit_units)
        for n_fields, digit_units, name_chars in dump_meta[:5]
    )
    hb_digits = dump_meta[4][1]
    rlb_dump_walk = 1 + 2 * (2 * dump_meta[5][0] + dump_meta[5][2] + dump_meta[5][1])
    scoped_input = 65 + 4 * len(workspace)
    workspace_walk = 1 + 15 * len(workspace)
    # The outer D field validators plus the 25-field input
    # assembly (the target's own dict construction, one unit per
    # carried field reference) and the carried lineage id's
    # closed length check.
    b1 = (
        1
        + 25
        + identity_units
        + text_units
        + 4 * (1 + 2 * 64)
        + d_version_units
        + 1
        + len(ns.lineage_id)
        + 1
        + d_set_units
    )
    reserver.reserve(b1)
    # The nested 018-c admission re-derivation (the FIRST
    # canonical/2-SHA block): its three 64-hex field checks
    # (config fingerprint plus the two carried scope keys), its
    # canonical workspace walk at the nested generic cap, its
    # five version walks, the four bound sets from their dumps,
    # the integrity encode walk, and its canonical payload with
    # TWO domain-prefixed SHA-256 and the two key equalities.
    b2 = (
        1
        + identity_units
        + 3 * (1 + 2 * 64)
        + workspace_walk
        + adm_version_units
        + 1
        + adm_set_units
        + 1
        + len(workspace)
        + adm_dump_walk
        + adm_payload_ceil
        + 2 * adm_payload_ceil
        + 104
        + 1
        + scoped_input
        + 2 * scoped_input
        + 104
        + 2
    )
    reserver.reserve(b2)
    b3 = 2 + 2 * (1 + hb_digits)
    reserver.reserve(b3)
    # The REPEATED canonical/2-SHA block (the SECOND): the real
    # D scope-key validator recomputes the canonical payload and
    # both 64-hex keys separately from the nested constructor,
    # then compares them to the carried tags.
    b2r = (
        1
        + adm_dump_walk
        + adm_payload_ceil
        + 2 * adm_payload_ceil
        + 104
        + 1
        + scoped_input
        + 2 * scoped_input
        + 104
        + 2
    )
    reserver.reserve(b2r)
    # The validator's canonical workspace re-check under the
    # ACTUAL carried graph path bound (the nested constructor's
    # walk ran at its own generic cap; this is a distinct real
    # pass), plus its comparison.
    ws_recheck = 2 + workspace_walk
    reserver.reserve(ws_recheck)
    b4 = 1 + hist_dump_walk + hist_payload_ceil + 2 * hist_payload_ceil + 104 + 1
    reserver.reserve(b4)
    b5 = 1 + scoped_input + 2 * scoped_input + 104 + 1
    reserver.reserve(b5)
    # The four recomputed-key equalities and the two state-join
    # comparisons of the actual parent phase.
    reserver.reserve(4)
    reserver.reserve(2)
    # (5) the ACTUAL _lineage_key recipe at its closed canonical
    # ceiling (the bound-shape check, the target's bound dump
    # walk, the domain-prefixed payload ceiling and its SHA-256,
    # and the equality check), then the fixed lineage-tag
    # comparisons at their ACTUAL target position.
    lineage_units = 1 + rlb_dump_walk + 3 * lineage_ceil + 104 + 1
    reserver.reserve(lineage_units)
    if (
        ns.contract_version != ROOT_REGION_LINEAGE_CONTRACT_VERSION
        or ns.policy_version != ROOT_REGION_LINEAGE_POLICY_VERSION
    ):
        raise _fixed("the carried namespace must carry the actual fixed lineage tags")
    reserver.reserve(2)
    d_total = b1 + b2 + b3 + b2r + ws_recheck + b4 + b5 + 6
    return d_total, lineage_units + 2, hist_payload_ceil


def _s_json_string_escaped_ceil(value: str) -> int:
    """The ensure_ascii JSON ENCODING CEILING for one string body
    (the accepted canonical recipe serializes with ``json.dumps``
    defaults): quote/backslash 2, control 6, astral 12, non-ASCII
    BMP 6, plain ASCII 1 per character.  Fence-legal record text
    is tight under this ceiling; the ceiling calculation itself
    is charged work, reserved before it runs."""
    total = 0
    for char in value:
        code = ord(char)
        if char == '"' or char == "\\":
            total += 2
        elif code < 0x20:
            total += 6
        elif code > 0xFFFF:
            total += 12
        elif code > 0x7E:
            total += 6
        else:
            total += 1
    return total


def _s_bound_set_json_len(bounds: BaseModel) -> int:
    """The EXACT canonical JSON length of one all-int bound set
    under the accepted recipe (``model_dump(mode="json")``,
    ``sort_keys=True``, compact separators): the braces, each
    quoted key, colon, integer value, and the separators."""
    dumped = bounds.model_dump(mode="json")
    total = 2
    for position, key in enumerate(sorted(dumped)):
        if position:
            total += 1
        total += 2 + len(key) + 1 + len(str(dumped[key]))
    return total


def _s_canonical_payload_ceils(record: BundleKeyRecord) -> tuple[int, int, int]:
    """The closed CEILING lengths of the ACTUAL canonical metadata
    payloads one key-record rekey serializes through the accepted
    C recipe (never a new recipe): ``x1`` the 16-element admission
    namespace payload (12 identity/version strings at their
    ensure_ascii ceilings plus the FOUR bound sets at their exact
    compact JSON lengths), ``s1`` the scoped-key SHA input (the
    64-hex namespace key, the NUL separator and the actual
    workspace UTF-8 length) and ``x2`` the 23-key content-key
    payload (16 strings at their ceilings, the FOUR inline bound
    sets at their exact lengths, the occurrence/class lists and
    the ownership-group list).  Every value is a ceiling: fence-
    legal text is tight, and a ceiling can only over-charge the
    actual serializer, never under-charge it.  The caller must
    reserve the charged calculation (and its walks) before
    calling."""
    bound_set_sized = (
        (record.admission_bounds, _s_bound_set_json_len(record.admission_bounds)),
        (record.proof_bounds, _s_bound_set_json_len(record.proof_bounds)),
        (record.graph_bounds, _s_bound_set_json_len(record.graph_bounds)),
        (record.observation_bounds, _s_bound_set_json_len(record.observation_bounds)),
    )
    bound_lens = tuple(bound_len for _, bound_len in bound_set_sized)
    # The FOUR bound sets enter the 16-element namespace payload as
    # JSON STRINGS (the recipe json.dumps-es each set, then embeds
    # it in the outer array): every key quote in the set's compact
    # JSON escapes once more, so the embedded entry is
    # 2 + L_i + 2 * (field count), not 2 + L_i.
    x1 = 2 + 15
    for value in (
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
    ):
        x1 += 2 + _s_json_string_escaped_ceil(value)
    for bounds, bound_len in bound_set_sized:
        x1 += 2 + bound_len + 2 * len(bounds.model_dump(mode="json"))
    s1 = 65 + len(record.workspace.encode("utf-8", errors="surrogatepass"))
    n = len(record.member_occurrences)
    g = len(record.ownership_groups)
    occurrences_len = (
        2
        + sum(2 + _s_json_string_escaped_ceil(path) for path in record.member_occurrences)
        + (n - 1)
    )
    classes_len = (
        2
        + sum(
            2 + _s_json_string_escaped_ceil(member_class.value)
            for member_class in record.member_classes
        )
        + (n - 1)
    )
    group_lens: list[int] = []
    for group in record.ownership_groups:
        indices = group.member_occurrence_indices
        indices_len = 2 + sum(len(str(index)) for index in indices) + (len(indices) - 1)
        digest_len = 4 if group.group_digest is None else 66
        boundary_len = 2 + _s_json_string_escaped_ceil(group.boundary_class.value)
        group_lens.append(
            2
            + (2 + len("member_occurrence_indices") + 1 + indices_len)
            + (2 + len("boundary_class") + 1 + boundary_len)
            + (2 + len("group_digest") + 1 + digest_len)
            + 2
        )
    groups_len = 2 + sum(group_lens) + (g - 1)
    key_entries: tuple[tuple[str, int], ...] = (
        # The recipe pins the admission contract version CONSTANT
        # (never the record's carried field) for this key.
        ("admission_version", 2 + _s_json_string_escaped_ceil(ADMISSION_CONTRACT_VERSION)),
        ("graph_version", 2 + _s_json_string_escaped_ceil(record.graph_version)),
        ("reference_version", 2 + _s_json_string_escaped_ceil(record.reference_version)),
        ("proof_version", 2 + _s_json_string_escaped_ceil(record.proof_version)),
        ("observation_version", 2 + _s_json_string_escaped_ceil(record.observation_version)),
        ("mode", 2 + _s_json_string_escaped_ceil(record.mode.value)),
        ("authority_class", 2 + _s_json_string_escaped_ceil(record.authority_class.value)),
        ("principal", 2 + _s_json_string_escaped_ceil(record.principal)),
        ("session", 2 + _s_json_string_escaped_ceil(record.session)),
        ("repository", 2 + _s_json_string_escaped_ceil(record.repository)),
        ("route", 2 + _s_json_string_escaped_ceil(record.route)),
        ("config_fingerprint", 2 + _s_json_string_escaped_ceil(record.config_fingerprint)),
        ("model_identity", 2 + _s_json_string_escaped_ceil(record.model_identity)),
        ("workspace", 2 + _s_json_string_escaped_ceil(record.workspace)),
        ("root_digest", 2 + _s_json_string_escaped_ceil(record.root_digest)),
        ("admission_bounds", bound_lens[0]),
        ("proof_bounds", bound_lens[1]),
        ("graph_bounds", bound_lens[2]),
        ("observation_bounds", bound_lens[3]),
        ("member_occurrences", occurrences_len),
        ("member_classes", classes_len),
        (
            "aggregate_source_digest",
            2 + _s_json_string_escaped_ceil(record.aggregate_source_digest),
        ),
        ("ownership_groups", groups_len),
    )
    x2 = 2 + 22
    for name, value_len in key_entries:
        x2 += 2 + len(name) + 1 + value_len
    return x1, s1, x2


def _s_canonical_metadata_precharge_closed(
    reserver: _SRegionWorkReserver,
    record: BundleKeyRecord,
    parent_ns: RootRegionLineageNamespace | None = None,
) -> tuple[int, int]:
    """The closed NEW local validation-cost reservation for the
    key record's ACTUAL canonical metadata work (the versioned
    ``root-region-admission-precharge/v1`` recipe, the canonical
    component).

    A SEPARATE component precharge contract, exactly like the
    region component: the caller supplies the typed bounded meter
    and invokes the actual targets (the canonical rekey, the
    scope join) only after this returns, so a crossing budget
    stops before any serializer or hash runs.  The ordinary model
    validators never receive a meter, and no unlimited or default
    meter exists in this module; the reservation is a WORK meter,
    never a size cap (the carried graph path bound is only the
    ACTUAL workspace SIZE domain, re-fenced closed here).

    Order: (1) close the reserver callback; (2) close the record
    class; (3) the SHARED O(1) preflight SHAPE gate -- closed
    fields, the closed containers, the FOUR carried bound sets
    under their exact ORIGINAL classes, the member caps and
    alignment, the workspace closed nonempty text and O(1)
    character shape under the ACTUAL carried path cap -- BEFORE
    any reservation (a partial or over-bound record refuses with
    zero reserved units and zero serializer work); (4) close the
    record scalar/enum element CLASSES (no element walk) so the
    fence reservation below never dereferences a bypassed value;
    (5) reserve the closed fence's ELEMENT-WALK work, computed
    walk-free from the closed O(1) counts and the ACTUAL carried
    domain caps (never a new fixed cap), and only THEN run the
    preflight's bounded workspace WALKS and the closed record
    fence; (6) reserve the CEILING CALCULATION itself
    (walk-free field-cap domain) and run it; (7) reserve the
    ACTUAL rekey work in the exact target order: the namespace
    payload encode plus SHA-256 (``2 * payload + 104``: payload
    bytes, one input pass, the 72-byte pad, the 32-byte digest),
    the scoped input, the namespace constructor's integrity
    re-run of both, its validator walks, and the content-key
    payload; (8) only when the ACTUAL parent namespace is
    supplied (closed O(1) first), reserve the SAME five
    reservations for the scope join's re-derivation plus the
    join comparison pool (13 text/enum comparisons, the FOUR
    bound sets field-by-field, the TWO 64-hex keys).  The
    meter's own ``ValueError`` propagates: a crossing budget
    therefore stops the caller before any target attempt.
    Returns the closed (leaf, join) reservation totals (join
    zero when no parent namespace is supplied).  This reserves
    component work for the later whole-operation recipe; it
    earns no whole-operation bound and changes no old public
    law."""
    if reserver is None or not callable(getattr(reserver, "reserve", None)):
        raise _fixed(
            "the canonical metadata precharge reserver must carry a typed reserve callback"
        )
    if not isinstance(record, BundleKeyRecord):
        raise _fixed("the key record must be the actual canonical record")
    # The SHARED O(1) preflight SHAPE gate (closed containers, the
    # FOUR bound sets, the member caps and alignment, the
    # ownership-groups container/count gate, the workspace closed
    # nonempty text and O(1) character shape under the ACTUAL
    # carried graph path cap) closes BEFORE any reservation; its
    # bounded workspace WALKS are deliberately NOT part of this
    # O(1) step -- they run after the fence reservation that pays
    # for them, so no walked workspace unit is uncharged.
    _, path_cap = _s_key_record_preflight_shape(record)
    # The ACTUAL inherited member-path ceiling for the fence and
    # calc path terms (the accepted N law: the smaller of the
    # carried graph and observation path-byte caps), closed O(1)
    # here from the shape phase's closed bound sets.
    member_path_cap = _s_member_path_cap(record)
    # (4) the scalar/enum element CLASSES close O(1) before the
    # fence reservation (a bypassed non-str scalar must refuse
    # here, never raise from the reservation's len() below; the
    # element WALK itself stays reserved in (5)).
    for field in (
        "principal",
        "session",
        "repository",
        "route",
        "model_identity",
        "config_fingerprint",
        "workspace",
        "root_digest",
        "aggregate_source_digest",
        "admission_version",
        "graph_version",
        "reference_version",
        "proof_version",
        "observation_version",
    ):
        value = getattr(record, field)
        if not isinstance(value, str):
            raise _fixed(f"the key record {field} must carry closed text")
    if not isinstance(record.mode, AdmissionMode):
        raise _fixed("the key record mode must be the actual closed admission mode")
    if not isinstance(record.authority_class, EntryClass):
        raise _fixed("the key record authority class must be the actual closed class")
    n = len(record.member_occurrences)
    g = len(record.ownership_groups)
    identity_lens = (
        len(record.principal),
        len(record.session),
        len(record.repository),
        len(record.route),
        len(record.model_identity),
    )
    version_lens = (
        len(record.admission_version),
        len(record.graph_version),
        len(record.reference_version),
        len(record.proof_version),
        len(record.observation_version),
    )
    # (5) the closed fence's element-walk work, reserved BEFORE
    # the walk and computed walk-free (1 unit per character
    # visit, the accepted v1 convention): the identity/version
    # text passes (two ord visits per character), the per-member-
    # path passes -- FOUR per path, each bounded by the ACTUAL
    # inherited two-cap path ceiling (one bounded domain-closure
    # walk plus the accepted early-exiting _check_rel_path passes:
    # the control scan, the backslash test and the split), the
    # WORKSPACE
    # WALKS of the repeated preflight (this precharge's own walk
    # plus the closed record fence re-run: TWO no-copy UTF-8
    # byte-length walks plus TWO canonical-form check passes per
    # workspace character), the four hex64 pools, the group
    # index/digest walks and the partition closure.
    fence_units = (
        2
        + 2 * sum(identity_lens)
        + 2 * sum(version_lens)
        + 4 * n * member_path_cap
        + 4 * len(record.workspace)
        + 4 * 64
        + n
        + g
        + g * n
        + g * 64
        + 3 * n
        + n * max(1, n.bit_length())
    )
    reserver.reserve(fence_units)
    # The bounded workspace WALKS run only AFTER the reservation
    # that pays for them (every count/scalar already closed in the
    # O(1) shape gate); the closed record fence re-runs the
    # identical preflight, whose second walk pair is included in
    # the charge above.
    _s_key_record_preflight_walk(record, path_cap)
    _s_key_record_closed(record)
    # (6) the ceiling calculation itself is charged work,
    # reserved BEFORE it runs (walk-free field-cap domain: the
    # 12 identity/version strings each ceiling-walked twice, the
    # two digest strings once, the four bound-dump sorted-key
    # loops (at most 20 fields each) and the per-occurrence /
    # per-group ceiling passes under the inherited two-cap path
    # ceiling).
    calc_units = 1 + 2 * 2068 + 128 + 80 + n * (member_path_cap + 33) + g * 97 + 3 * n
    reserver.reserve(calc_units)
    # (7) the charged ceiling calculation (the actual walks).
    x1, s1, x2 = _s_canonical_payload_ceils(record)
    # (8) the ACTUAL rekey work, reserved in the exact target
    # order (the accepted C recipe).
    leaf_total = 0
    for payload in (x1, s1, x1, s1):
        units = 2 * payload + 104
        reserver.reserve(units)
        leaf_total += units
    ctor_units = sum(identity_lens) + 3 * 64 + sum(version_lens) + len(record.workspace) + 2 * 64
    reserver.reserve(ctor_units)
    leaf_total += ctor_units
    key_units = 2 * x2 + 104
    reserver.reserve(key_units)
    leaf_total += key_units
    join_total = 0
    if parent_ns is not None:
        # The ACTUAL parent namespace class closes O(1) BEFORE
        # any join reservation: a wrong parent never authorizes
        # work (a class fence only; a valid by-value copy is the
        # carrier's own law, not this one).
        if not isinstance(parent_ns, RootRegionLineageNamespace):
            raise _fixed("the parent namespace must be the actual closed lineage namespace")
        for payload in (x1, s1, x1, s1):
            units = 2 * payload + 104
            reserver.reserve(units)
            join_total += units
        reserver.reserve(ctor_units)
        join_total += ctor_units
        join_units = 301
        reserver.reserve(join_units)
        join_total += join_units
    return leaf_total, join_total


def _s_entry_leaf_closed(entry: RootRegionAdmissionEntry) -> None:
    """The COMPLETE leaf actual-field/canonical/retained-content law,
    shared by the entry constructor and the admission-parent re-run (a
    parent re-runs the law, it never trusts copied tags).  Closed O(1)
    field/count/shape fences run BEFORE any element walk or
    serialization; the COMPLETE accepted N retained-content law
    (segment preflight, member-position gates, the one-to-one
    segment group partition with the PROVEN single-member /
    BOUNDARYLESS multi-member digest joins) and the ACTUAL closed R
    source law (``_r_source_closed``, including its own bounded
    content pass) are the retained predicates.  A model_copy-bypassed
    or detached record refuses here, not by value equality alone."""
    if not _r_fields_present(entry, _S_ENTRY_FIELDS):
        raise _fixed("the admission entry must carry its closed fields")
    record = entry.key_record
    if not isinstance(record, BundleKeyRecord):
        raise _fixed("the entry key record must be the actual canonical record")
    # The CLOSED entry scalar/enum/container shape runs BEFORE any
    # canonical rekey or element walk, at leaf AND carrying boundary:
    # a bypassed model_copy does not re-run the field validators, so
    # the ACTUAL closed shapes are re-fenced here instead of trusting
    # the copied record (a str-enum raw value is equal to its member,
    # a bool width equals 1, and a mutable list converts silently --
    # every one of those carried objects refuses with a fixed private
    # error; legitimate direct-constructor normalization remains
    # distinct and untouched).
    if not isinstance(entry.entry_class, EntryClass):
        raise _fixed("the entry class must be the actual closed entry class")
    if isinstance(entry.width, bool) or not isinstance(entry.width, int) or entry.width < 1:
        raise _fixed("the entry width must carry a closed positive integer")
    if not isinstance(entry.member_classes, tuple) or not entry.member_classes:
        raise _fixed("the entry member classes must carry a nonempty closed tuple")
    # The SHARED O(1) record preflight (class/field/bounds/cap) and
    # the entry O(1) COUNT alignment close BEFORE any member walk,
    # at leaf AND carrying boundary: a bypassed record with a
    # malformed bound, or a matching oversized record/entry pair
    # (e.g. 1025/1025, where alignment alone passes), is a fixed
    # private error before the first element is inspected.
    _s_key_record_preflight(record)
    if len(entry.member_classes) != len(record.member_occurrences):
        raise _fixed("member_classes must align with the member occurrences")
    for member_class in entry.member_classes:
        if not isinstance(member_class, MemberClass):
            raise _fixed("the entry member classes must be the actual closed authority classes")
    if not isinstance(entry.admitted_segments, tuple):
        raise _fixed("the entry admitted segments must carry the closed tuple container")
    if not isinstance(entry.witnesses, tuple):
        raise _fixed("the entry witnesses must carry the closed tuple container")
    # The PROOF-CONTEXT O(1) population closure runs BEFORE the
    # canonical rekey and every element walk, at leaf AND carrying
    # boundary (the parent re-runs this law DIRECTLY; the
    # constructor BEFORE handler alone does not close that path):
    # the retained proof's closed content containers first (a
    # bypassed model_construct proof missing a field is a fixed
    # private error, never an AttributeError, never a malformed-
    # provided fallback), the population counts under the ACTUAL
    # carried ORIGINAL B (bundle-proof) bound domains, and the
    # admitted index count under the actual retained segment
    # domain (a carried overlong admitted vector is a fixed private
    # error before the canonical C rekey and any slice).  The
    # witness COUNT is a DIFFERENT domain from the admitted
    # segments: it closes under the ACTUAL carried G
    # association-attempt cap (the safe upper bound of the real G
    # association domain -- never a new fixed cap and never the
    # history occurrence population; one genuine occurrence may
    # carry multiple same-key plan witnesses).
    if entry.proof is not None:
        if not isinstance(entry.proof, BundleProof):
            raise _fixed("a file entry keeps its retained original proof")
        if (
            not _r_fields_present(entry.proof, ("segments", "requested_members"))
            or not isinstance(entry.proof.segments, tuple)
            or not isinstance(entry.proof.requested_members, tuple)
        ):
            raise _fixed("the retained file proof must carry its closed content fields")
        if len(entry.proof.segments) > record.proof_bounds.max_segments:
            raise _fixed("the retained proof segments exceed the actual carried proof cap")
        if len(entry.proof.requested_members) > record.proof_bounds.max_members:
            raise _fixed("the retained proof members exceed the actual carried proof cap")
        if len(entry.admitted_segments) > len(entry.proof.segments):
            raise _fixed("admitted segments exceed the actual proof segment domain before any walk")
        if entry.entry_class is EntryClass.ROOT_ENTRY:
            # The ROOT variant context closes O(1) at the carrying
            # boundary too: the closed witness count is zero and a
            # carried spliced FILE proof never authorizes the FILE
            # witness domain (mirroring the constructor BEFORE gate).
            if entry.witnesses:
                raise _fixed("the root entry is evidenced, never a fabricated read witness")
        elif len(entry.witnesses) > record.admission_bounds.max_reverse_associations:
            raise _fixed(
                "the entry witnesses exceed the actual carried association domain before any walk"
            )
    elif entry.entry_class is EntryClass.ROOT_ENTRY:
        # The ROOT variant admits the root, not proof segments, and
        # is evidenced, never a fabricated read witness: the closed
        # count is zero BEFORE the canonical rekey (a carried ROOT
        # row with a nonempty admitted or witness vector is a fixed
        # private error before any hash/serializer visit, mirroring
        # the constructor BEFORE gate).
        if entry.admitted_segments:
            raise _fixed("the root entry admits the root, not proof segments")
        if entry.witnesses:
            raise _fixed("the root entry is evidenced, never a fabricated read witness")
    # The CLOSED record metadata fence (fields/classes/scalars/group
    # partition/four bound sets) runs BEFORE any canonical rekey.
    _s_key_record_closed(record)
    if entry.key_record.authority_class != entry.entry_class:
        raise _fixed("key record authority class must equal the entry class")
    if entry.key_record.root_digest != entry.root_digest:
        raise _fixed("entry root binding must equal the key record root binding")
    if len(entry.member_classes) != len(record.member_occurrences):
        raise _fixed("member_classes must align with the member occurrences")
    if tuple(entry.member_classes) != tuple(record.member_classes):
        raise _fixed("entry authority vector must equal the key record vector")
    if entry.content_key != record.content_key:
        raise _fixed("content key must equal the key record content key")
    if _canonical_entry_key(record) != entry.content_key:
        raise _fixed("content key must bind the actual canonical 018-c recipe")
    if entry.entry_class is EntryClass.ROOT_ENTRY:
        if entry.proof is not None:
            raise _fixed("a root entry never embeds a file-tool proof")
        if entry.admitted_segments:
            raise _fixed("the root entry admits the root, not proof segments")
        if entry.witnesses:
            raise _fixed("the root entry is evidenced, never a fabricated read witness")
        if entry.root_source is None:
            raise _fixed("the region root entry carries the actual resolved root source")
        source = entry.root_source
        # The ACTUAL closed R source law runs here (own bounded
        # content pass included); the S budget recipe charges this
        # invocation separately from any S-own measurement it
        # performs first.
        _r_source_closed(source)
        if source.root_digest != entry.root_digest:
            raise _fixed("the root entry binds the selected governing root digest")
        if record.member_occurrences != (ROOT_FILENAME,):
            raise _fixed("a root entry is one occurrence at the normalized root")
        if record.aggregate_source_digest != entry.root_digest:
            raise _fixed("root aggregate digest must equal the selected root digest")
        if entry.width != 1 or entry.member_classes != (MemberClass.ELIGIBLE,):
            raise _fixed("the region root is one always-eligible root-occurrence member")
        groups = record.ownership_groups
        if len(groups) != 1:
            raise _fixed("the region root entry carries its sole ownership group")
        group = groups[0]
        # The sole root group is PROVEN and bound to the selected
        # root digest (the explicit boundary-class fence: a
        # coherently rekeyed BOUNDARYLESS root group refuses).
        if group.boundary_class is not BoundaryClass.PROVEN:
            raise _fixed("the sole root group is proven with the selected root digest")
        if (
            group.group_index != 0
            or group.member_occurrence_indices != (0,)
            or group.group_digest != entry.root_digest
        ):
            raise _fixed("the sole root group is proven and bound to the selected root digest")
        return
    # --- FILE row: the COMPLETE accepted N retained-content law ---
    if entry.root_source is not None:
        raise _fixed("root-only properties belong to the root entry only")
    proof = entry.proof
    if proof is None:
        raise _fixed("a file entry keeps its retained original proof")
    if not _r_fields_present(proof, ("segments", "requested_members", "source_text")):
        raise _fixed("the retained file proof must carry its closed content fields")
    if not isinstance(proof.source_text, str):
        raise _fixed("the retained file proof must carry its closed source text")
    if not isinstance(proof.segments, tuple) or not proof.segments:
        raise _fixed("the retained file proof must carry its retained segments")
    if not isinstance(proof.requested_members, tuple):
        raise _fixed("the retained file proof must carry its requested occurrences")
    # The retained requested-member closure (the ORIGINAL B
    # member law re-fenced at the carrying boundary, where the
    # field validator does not rerun): the concrete class, the
    # closed metadata and the closed normalized variant of EVERY
    # requested member are closed BEFORE any member dereference,
    # content fetch or admission-region work:
    for member in proof.requested_members:
        if type(member) is not NormalizedPath:
            raise _fixed("the retained proof members must be the actual concrete member records")
        if not _r_fields_present(member, ("raw", "form", "quoted", "normalized", "limitation")):
            raise _fixed("the retained proof members must carry their closed metadata")
        if member.normalized is not None and not isinstance(member.normalized, str):
            raise _fixed("the retained proof member normalized path must carry closed text")
        if not isinstance(member.raw, str):
            raise _fixed("the retained proof member raw path must carry closed text")
        if not isinstance(member.form, PathForm):
            raise _fixed("the retained proof member form must be the actual closed enum")
        if not isinstance(member.quoted, bool):
            raise _fixed("the retained proof member quoted flag must be an actual boolean")
        if member.limitation is not None and not isinstance(member.limitation, Limitation):
            raise _fixed("the retained proof member limitation must be the actual closed enum")
    if not entry.witnesses:
        raise _fixed("a file entry retains its original proof witnesses")
    # The COMPLETE canonical witness-retention order/dedup law re-runs
    # here at leaf AND carrying boundary (the constructor field
    # validator is bypassed by a carried model_copy; a reversed or
    # duplicated carried witness tuple refuses, never re-sorted or
    # repaired).
    _s_witnesses_sorted_deduplicated(entry.witnesses, record.proof_bounds.max_segments)
    if not entry.admitted_segments:
        raise _fixed("a file entry names its admitted segments")
    segments = proof.segments
    previous = -1
    for index in entry.admitted_segments:
        if isinstance(index, bool) or not isinstance(index, int) or index < 0 or index <= previous:
            raise _fixed("admitted segment indices must be distinct and increasing")
        previous = index
    if previous >= len(segments):
        raise _fixed("admitted segment indices must index the proof segments")
    # The COMPLETE retained segment population is closed BEFORE any
    # character offset, source slice or join is computed, INCLUDING
    # the preceding/UNADMITTED segments whose lengths advance the
    # offset (concrete class, closed fields, non-bool nonnegative
    # lengths; the actual metadata walk is charged by the S budget
    # recipe at leaf AND admission parent before work):
    for segment in segments:
        if type(segment) is not BundleSegment:
            raise _fixed("the retained proof segments must be the actual concrete segment records")
        if not _r_fields_present(segment, _S_SEGMENT_FIELDS):
            raise _fixed("the retained proof segments must carry their closed metadata")
        if (
            isinstance(segment.char_length, bool)
            or not isinstance(segment.char_length, int)
            or segment.char_length < 0
            or isinstance(segment.byte_length, bool)
            or not isinstance(segment.byte_length, int)
            or segment.byte_length < 0
        ):
            raise _fixed("retained segment metadata must carry closed nonnegative lengths")
        if not isinstance(segment.member_positions, tuple) or not segment.member_positions:
            raise _fixed("retained segment member positions must carry a closed nonempty tuple")
        if len(segment.member_positions) > len(proof.requested_members):
            raise _fixed(
                "segment member positions exceed the actual requested "
                "occurrence domain before any walk"
            )
        for position in segment.member_positions:
            if isinstance(position, bool) or not isinstance(position, int) or position < 0:
                raise _fixed(
                    "retained segment member positions must carry closed nonnegative indices"
                )
    # The retained segment population PARTITIONS the retained
    # source text (the ORIGINAL B aggregate law re-fenced at the
    # carrying boundary, where the field validator does not rerun:
    # consecutive segments advance the character offset from zero
    # and the final offset IS the source length; an empty segment
    # is legal and contributes zero).  The closed total closes
    # EVERY preceding/UNADMITTED segment whose length advances the
    # offset BEFORE any source slice or hash -- an outside or
    # overlong retained interval refuses here, never as a silent
    # empty Python slice (Unicode character offsets, never bytes):
    total_chars = 0
    for segment in segments:
        total_chars += segment.char_length
    if total_chars != len(proof.source_text):
        raise _fixed("the retained segment intervals must partition the retained source text")
    # Closed count preflight from the retained segment METADATA (no
    # source walk) BEFORE any slice/join/encode: the admitted
    # region's exact byte total against the ACTUAL inherited
    # single-source cap, its char total against that SAME byte cap
    # (a UTF-8 lower bound) and its char total against the retained
    # source length.
    region_chars = 0
    region_bytes = 0
    for position in entry.admitted_segments:
        segment = segments[position]
        region_chars += segment.char_length
        region_bytes += segment.byte_length
    cap = record.graph_bounds.max_single_source_bytes
    if region_bytes > cap:
        raise _fixed("admitted region exceeds the inherited single-source byte cap")
    if region_chars > cap:
        raise _fixed("admitted region exceeds the inherited single-source byte cap")
    if region_chars > len(proof.source_text):
        raise _fixed("admitted region cannot exceed the retained source text")
    if len(entry.admitted_segments) != 1 and entry.admitted_segments != tuple(range(len(segments))):
        raise _fixed("admitted region is the whole bundle or one proven group")
    # The NEW closed D2 region precharge is a SEPARATE component
    # contract: the caller reserves the region's owned passes with
    # its explicit bounded meter (the closed
    # ``root-region-admission-precharge/v1`` law) BEFORE invoking
    # this law or the constructor.  The constructors remain data-
    # validity checks and receive no meter (no unlimited or default
    # meter exists here); the raw-total gates above are the
    # unchanged source-SIZE law and never a work meter.
    # The WHOLE-BUNDLE fast path (the whole-bundle law above):
    # when every segment is admitted, the partition closure
    # proves the segments tile the source, so the joined region
    # IS the source text itself -- no slice/join copies are made
    # (the digest predicate hashes byte-identical content and
    # every other predicate is unchanged).  A single proven group
    # keeps the slice/join.
    whole_bundle = len(entry.admitted_segments) == len(segments) and all(
        entry.admitted_segments[i] == i for i in range(len(segments))
    )
    admitted_set = set(entry.admitted_segments)
    admitted: list[str] = []
    region: list[str] = []
    offset = 0
    for position, segment in enumerate(segments):
        if position in admitted_set:
            for member_position in segment.member_positions:
                # The nested position is an ACTUAL integer indexing
                # the retained requested occurrences, validated
                # BEFORE any fetch (a bypassed proof record cannot
                # IndexError the join or read a foreign occurrence).
                if (
                    not isinstance(member_position, int)
                    or isinstance(member_position, bool)
                    or not 0 <= member_position < len(proof.requested_members)
                ):
                    raise _fixed(
                        "admitted member positions must index the retained requested occurrences"
                    )
                member = proof.requested_members[member_position]
                if member.normalized is None:
                    raise _fixed("admitted members must be resolved paths")
                admitted.append(member.normalized)
            if not whole_bundle:
                region.append(proof.source_text[offset : offset + segment.char_length])
        offset += segment.char_length
    admitted_tuple = tuple(admitted)
    if admitted_tuple != record.member_occurrences:
        raise _fixed("admitted members must equal the key record member occurrences")
    region_text = proof.source_text if whole_bundle else "".join(region)
    if _sha256_hex(region_text.encode("utf-8")) != record.aggregate_source_digest:
        raise _fixed("admitted region digest must equal the key record aggregate")
    # The entry-local group partition is joined ONE-TO-ONE to the
    # ORIGINAL proof segments (the accepted descriptor law): one
    # group per admitted segment, in admitted order, carrying that
    # segment's dense member-index range, its PROVEN / BOUNDARYLESS
    # class and its proven member digest / segment digest.
    groups = record.ownership_groups
    if len(groups) != len(entry.admitted_segments):
        raise _fixed("record groups join the admitted proof segments one-to-one")
    entry_local = 0
    for group, position in zip(groups, entry.admitted_segments, strict=True):
        segment = segments[position]
        n_members = len(segment.member_positions)
        expected = tuple(range(entry_local, entry_local + n_members))
        if group.member_occurrence_indices != expected:
            raise _fixed("record group indices must be the dense segment member range")
        if n_members == 1:
            if segment.member_digest is None:
                raise _fixed("a single-member segment carries its proven digest")
            if (
                group.boundary_class is not BoundaryClass.PROVEN
                or group.group_digest != segment.member_digest
            ):
                raise _fixed("a single-member segment group is proven with the member digest")
        else:
            if (
                group.boundary_class is not BoundaryClass.BOUNDARYLESS
                or group.group_digest != segment.digest
            ):
                raise _fixed("a multi-member segment group is boundaryless with the segment digest")
        entry_local += n_members
    if entry.width != len(set(admitted_tuple)):
        raise _fixed("width must equal the distinct admitted member paths")
    return


def _s_witness_region_compatible(
    witness: CurrentAdmissionWitness,
    owner_proof: BundleProof,
    record: BundleKeyRecord,
    proof_bounds: BundleProofBounds,
) -> None:
    """The witness's ORIGINAL region, under the owner occurrence's
    retained proof, must select the EXACT region bound by THIS
    entry's canonical key -- joined METADATA-ONLY, with no repeated
    source-body pass (the FIRST retained proof's content check in
    the leaf law pins the entry region to the aggregate digest;
    this helper pins each witness region to that SAME aggregate via
    the ORIGINAL observed digest metadata, which is valid across
    DIFFERENT original proofs where the same member content sits at
    different character offsets):

    * the ACTUAL owner proof / witness concrete classes close
      O(1) first (a wrong-class carried record is a fixed private
      error, never an attribute error);
    * the ORIGINAL B segment/member population caps close O(1)
      BEFORE any index or member-element walk (the carried
      population authorizes the raw-index domain);
    * the N plan gate: the witness selects the WHOLE bundle or ONE
      original group (a spliced around-member selection cannot mint
      a different-region witness, even when another genuine entry
      exists for the spliced content);
    * the ordered member sequence of the selected segments equals
      the entry key record member occurrences;
    * the ORIGINAL aggregate binding: the whole owner proof's
      ``source_digest``, or the single selected segment's ``digest``,
      must equal the entry key record aggregate digest (with the
      original hex preflight) -- never a length-only shortcut and
      never a body re-encode;
    * the same one-to-one group partition joins (dense entry-local
      ranges with the PROVEN single-member / BOUNDARYLESS
      multi-member class and digest joins).

    The retained requested-member closure (concrete class, closed
    metadata, closed normalized variant and closed
    raw/form/quoted/limitation scalars) re-closes under the OWNER
    proof BEFORE any member dereference or region-join work (the
    owner proof is a DIFFERENT retained proof than the entry's
    FIRST retained proof, where the same member content may sit at
    different original offsets).  Closed segment metadata fences
    run BEFORE any join; a witness from an unrelated occurrence,
    with foreign or reindexed coordinates, or over different
    content refuses with a fixed private error.  Every walk here
    is charged before work by the S budget recipe."""
    if type(witness) is not CurrentAdmissionWitness:
        raise _fixed("the file witness must be the actual concrete witness record")
    if type(owner_proof) is not BundleProof:
        raise _fixed("the owner retained proof must be the actual concrete proof record")
    if not _r_fields_present(witness, ("segment_indices",)):
        raise _fixed("the file witness must carry its closed segment coordinates")
    if not _r_fields_present(
        owner_proof, ("segments", "requested_members", "source_text", "source_digest")
    ):
        raise _fixed("the owner retained proof must carry its closed content fields")
    if not isinstance(owner_proof.source_text, str):
        raise _fixed("the owner retained proof must carry its closed source text")
    if not isinstance(owner_proof.source_digest, str):
        raise _fixed("the owner retained proof must carry its closed source digest")
    _check_hex64(owner_proof.source_digest, "source_digest")
    if not isinstance(owner_proof.segments, tuple) or not owner_proof.segments:
        raise _fixed("the owner retained proof must carry its retained segments")
    if not isinstance(owner_proof.requested_members, tuple):
        raise _fixed("the owner retained proof must carry its requested occurrences")
    segments = owner_proof.segments
    # The ORIGINAL B segment/member population caps close O(1)
    # BEFORE any index or member-element walk (an oversized
    # carried population cannot widen the raw-index domain; a
    # hoisted postparse cap alone would be too late).
    if len(segments) > proof_bounds.max_segments:
        raise _fixed("the retained proof segments exceed the actual carried proof cap")
    if len(owner_proof.requested_members) > proof_bounds.max_members:
        raise _fixed("the retained proof members exceed the actual carried proof cap")
    indices = witness.segment_indices
    if not isinstance(indices, tuple) or not indices:
        raise _fixed("the file witness must carry its original segment coordinates")
    if len(indices) > len(segments):
        raise _fixed("the witness segment indices exceed the original proof segment domain")
    previous = -1
    for index in indices:
        if (
            isinstance(index, bool)
            or not isinstance(index, int)
            or index < 0
            or index <= previous
            or index >= len(segments)
        ):
            raise _fixed("the witness segment indices must index the original proof")
        previous = index
    # The N plan gate BEFORE any member/offset walk: the witness
    # region is the whole bundle or exactly one original group.
    if len(indices) != 1 and indices != tuple(range(len(segments))):
        raise _fixed("the witness region is the whole bundle or one original group")
    # The retained requested-member closure re-closed under the
    # OWNER proof BEFORE any member dereference or region-join
    # work (the same fixed private channels as the shared leaf
    # law; explicitly NOT hoisted ahead of the O(1) count gates):
    for member in owner_proof.requested_members:
        if type(member) is not NormalizedPath:
            raise _fixed("the retained proof members must be the actual concrete member records")
        if not _r_fields_present(member, ("raw", "form", "quoted", "normalized", "limitation")):
            raise _fixed("the retained proof members must carry their closed metadata")
        if member.normalized is not None and not isinstance(member.normalized, str):
            raise _fixed("the retained proof member normalized path must carry closed text")
        if not isinstance(member.raw, str):
            raise _fixed("the retained proof member raw path must carry closed text")
        if not isinstance(member.form, PathForm):
            raise _fixed("the retained proof member form must be the actual closed enum")
        if not isinstance(member.quoted, bool):
            raise _fixed("the retained proof member quoted flag must be an actual boolean")
        if member.limitation is not None and not isinstance(member.limitation, Limitation):
            raise _fixed("the retained proof member limitation must be the actual closed enum")
    selected_set = set(indices)
    admitted: list[str] = []
    for position, segment in enumerate(segments):
        # The closed segment metadata fences run BEFORE any inner
        # member-position walk or join (the ORIGINAL B segment
        # record concrete class, the closed fields, the closed
        # member-position tuple container and its O(1) count under
        # the ACTUAL requested-occurrence domain -- the same fixed
        # private channels as the shared leaf law, applied to EVERY
        # segment including the preceding/unselected ones; a
        # counting iterator or other raw iterable is refused
        # before it can be traversed, and an over-count refuses
        # before the first element is visited):
        if type(segment) is not BundleSegment:
            raise _fixed("the retained proof segments must be the actual concrete segment records")
        if not _r_fields_present(segment, _S_SEGMENT_FIELDS):
            raise _fixed("the retained proof segments must carry their closed metadata")
        if not isinstance(segment.member_positions, tuple):
            raise _fixed(
                "the retained segment member positions must carry the closed tuple container"
            )
        if len(segment.member_positions) > len(owner_proof.requested_members):
            raise _fixed(
                "segment member positions exceed the actual requested "
                "occurrence domain before any walk"
            )
        if position in selected_set:
            for member_position in segment.member_positions:
                if (
                    not isinstance(member_position, int)
                    or isinstance(member_position, bool)
                    or not 0 <= member_position < len(owner_proof.requested_members)
                ):
                    raise _fixed(
                        "the witness region member positions must index the original occurrences"
                    )
                member = owner_proof.requested_members[member_position]
                if member.normalized is None:
                    raise _fixed("the witness region members must be resolved paths")
                admitted.append(member.normalized)
    if tuple(admitted) != record.member_occurrences:
        raise _fixed("the witness region members must equal the entry key record occurrences")
    # The ORIGINAL aggregate binding (metadata only): the whole
    # proof digest, or the single selected segment digest, must
    # equal the entry key record aggregate.
    if len(indices) == 1:
        segment = segments[indices[0]]
        if not isinstance(segment.digest, str):
            raise _fixed("the selected witness segment must carry its closed digest")
        _check_hex64(segment.digest, "segment_digest")
        if segment.digest != record.aggregate_source_digest:
            raise _fixed("the witness single-segment digest must equal the entry aggregate")
    elif owner_proof.source_digest != record.aggregate_source_digest:
        raise _fixed("the witness whole-proof digest must equal the entry aggregate")
    groups = record.ownership_groups
    if len(groups) != len(indices):
        raise _fixed("the witness region groups must join its admitted segments one-to-one")
    entry_local = 0
    for group, position in zip(groups, indices, strict=True):
        segment = segments[position]
        n_members = len(segment.member_positions)
        if group.member_occurrence_indices != tuple(range(entry_local, entry_local + n_members)):
            raise _fixed("the witness region group indices must be the dense segment member range")
        if n_members == 1:
            if segment.member_digest is None:
                raise _fixed("the witness single-member segment carries its proven digest")
            if (
                group.boundary_class is not BoundaryClass.PROVEN
                or group.group_digest != segment.member_digest
            ):
                raise _fixed("the witness single-member group is proven with the member digest")
        else:
            if (
                group.boundary_class is not BoundaryClass.BOUNDARYLESS
                or group.group_digest != segment.digest
            ):
                raise _fixed(
                    "the witness multi-member group is boundaryless with the segment digest"
                )
        entry_local += n_members


def _s_witnesses_sorted_deduplicated(
    witnesses: tuple[CurrentAdmissionWitness, ...],
    max_segment_indices: int,
) -> None:
    """The ACTUAL concrete witness class, the closed witness
    coordinate shapes (the original occurrence text, the non-bool
    integer request/call/result coordinates, the closed
    segment-index container, the original nonempty MINLENGTH, and
    the distinct-and-increasing coordinate law) and the accepted G
    witness-retention order (canonical full-coordinate tuple, never
    acquisition order), re-run at leaf AND carrying boundary --
    the O(1) class / field / container / nonempty / population
    gates are fenced BEFORE the first index element is traversed
    (a bypassed wrong-class or shape-malformed nested record is a
    fixed private error, never trusted by shape alone; and an
    oversized bypassed index tuple is refused by len before any
    element visit), and the per-index scalar and strict-order
    checks close DURING the bounded one-pass traversal, before the
    full-coordinate sort/comparison (a bypassed bool at an actual
    0/1 coordinate would compare equal to its int twin, so shape
    closure precedes any comparison).  The
    index population domain is the ACTUAL carried original B
    segment population cap (a safe structural upper bound valid
    for EVERY retained owner proof before any owner lookup; it is
    never the FIRST retained proof's length and never a new fixed
    cap -- the EXACT original-owner segment domain, including
    per-index owner membership, is enforced later by the M04
    owner join at the admission parent).  Duplicate coordinate
    tuples are refused before any dedup is needed."""
    previous: tuple[str, int, int, int, tuple[int, ...]] | None = None
    for w in witnesses:
        # The ACTUAL concrete witness class fences FIRST (a
        # matching-namespace wrong-class carried record is a fixed
        # private error, never trusted by shape alone), then the
        # closed field existence:
        if type(w) is not CurrentAdmissionWitness:
            raise _fixed("the file witness must be the actual concrete witness record")
        if not _r_fields_present(
            w,
            (
                "occurrence_id",
                "request_index",
                "call_position",
                "result_position",
                "segment_indices",
            ),
        ):
            raise _fixed("the retained witness must carry its closed fields")
        if not isinstance(w.occurrence_id, str):
            raise _fixed("the witness occurrence must carry closed text")
        _check_hex64(w.occurrence_id, "occurrence_id")
        for field in ("request_index", "call_position", "result_position"):
            value = getattr(w, field)
            if isinstance(value, bool) or not isinstance(value, int) or value < 0:
                raise _fixed("witness coordinates must carry closed nonnegative integers")
        if not isinstance(w.segment_indices, tuple):
            raise _fixed("the witness segment indices must carry the closed tuple container")
        if not w.segment_indices:
            # The ORIGINAL witness minlength law re-run at the S
            # boundary (a bypassed model_copy skips the witness
            # model's own min_length field law): the fixed channel
            # is the same as the M04 owner join's.
            raise _fixed("the file witness must carry its original segment coordinates")
        if len(w.segment_indices) > max_segment_indices:
            raise _fixed("the witness segment indices exceed the actual carried proof cap")
        previous_index = -1
        for index in w.segment_indices:
            if isinstance(index, bool) or not isinstance(index, int) or index < 0:
                raise _fixed("the witness segment indices must carry closed nonnegative integers")
            # The ORIGINAL distinct-and-increasing coordinate law
            # re-run at the S boundary (intrinsic; the EXACT owner
            # membership -- index < len(owner.segments) -- stays
            # the parent M04 join):
            if index <= previous_index:
                raise _fixed("the witness segment indices must index the original proof")
            previous_index = index
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


_S_RESULT_FIELDS: tuple[str, ...] = (
    "call_id",
    "endpoint",
    "tool_name",
    "argument_fingerprint",
    "complete",
    "piece_call_bindings",
    "piece_facts",
    "piece_completion",
)


def _s_occurrence_owning_result_closed(
    occurrence: CompletedReadOccurrence,
    results: tuple[ResultFingerprintRecord, ...],
    history_bounds: HistoryBounds,
) -> None:
    """The M04 owner join at the admission parent (metadata only):
    a retained completed occurrence must join its COMPLETE owning
    result record in the SAME actual D state, keyed by the read's
    own call ID, and that record must retain the EXACT producing-
    call association of the occurrence's RETAINED proof pieces,
    aligned by piece index (the accepted H-PRIVATE 4b/4c builder
    invariant, re-fenced for the carrying boundary -- a charged
    small metadata join, never a full history or source
    rederivation).  A missing or incomplete owning result, an
    emptied or rewritten piece producer association, a mismatched
    initial owner binding, a flipped endpoint family or a
    mismatched piece fact erases the original ownership that the
    retained proof alone cannot re-prove."""
    if not isinstance(results, tuple):
        raise _fixed("the carried D results must carry the closed tuple container")
    # The O(1) ACTUAL domain caps close BEFORE the results index is
    # built or any element walk starts: the results domain is the
    # retained observed-result cap and the pieces domain the retained
    # piece cap of the ACTUAL closed history bounds (a witness or
    # occurrence count is a DIFFERENT domain and is never capped
    # here; one occurrence may legitimately carry multiple distinct
    # same-key plan witnesses).
    if len(results) > history_bounds.max_observed_results:
        raise _fixed("the carried D results exceed the actual retained-result cap")
    result_by_call: dict[str, Any] = {}
    for result in results:
        if not _r_fields_present(result, _S_RESULT_FIELDS):
            raise _fixed("the carried D results must carry their closed fields")
        if (
            not isinstance(result.call_id, str)
            or not isinstance(result.endpoint, str)
            or not isinstance(result.tool_name, str)
            or not isinstance(result.argument_fingerprint, str)
            or not isinstance(result.complete, bool)
            or not isinstance(result.piece_call_bindings, tuple)
            or not isinstance(result.piece_facts, tuple)
            or not isinstance(result.piece_completion, tuple)
        ):
            raise _fixed("the carried D results must carry closed scalar shapes")
        result_by_call[result.call_id] = result
    if not isinstance(occurrence.call_id, str):
        raise _fixed("the retained occurrence must carry its closed call identity")
    owning = result_by_call.get(occurrence.call_id)
    if owning is None:
        raise _fixed("the retained occurrence must join its owning result record")
    if owning.complete is not True:
        raise _fixed("the retained occurrence must join its complete owning result")
    # The owning result's IMMUTABLE call binding must equal the
    # ORIGINAL retained occurrence's call identity/association (the
    # accepted H/D pairing supplied before the 4c join; comparing
    # the record to its OWN co-mutated piece bindings alone would
    # admit a coherently foreign owner).
    if (
        not isinstance(occurrence.endpoint, str)
        or not isinstance(occurrence.tool_name, str)
        or not isinstance(occurrence.argument_fingerprint, str)
    ):
        raise _fixed("the retained occurrence must carry its closed call binding")
    if (
        owning.endpoint != occurrence.endpoint
        or owning.tool_name != occurrence.tool_name
        or owning.argument_fingerprint != occurrence.argument_fingerprint
    ):
        raise _fixed("the owning result keeps the original call's immutable binding")
    pieces = occurrence.proof.pieces
    if not isinstance(pieces, tuple):
        raise _fixed("the retained proof must carry its closed piece carriers")
    if len(pieces) > history_bounds.max_retained_pieces:
        raise _fixed("the retained proof pieces exceed the actual retained-piece cap")
    if (
        len(owning.piece_call_bindings) != len(pieces)
        or len(owning.piece_facts) != len(pieces)
        or len(owning.piece_completion) != len(pieces)
    ):
        raise _fixed("the owning result retains the exact piece producer association")
    for piece_index in range(len(pieces)):
        piece = pieces[piece_index]
        binding = owning.piece_call_bindings[piece_index]
        if (
            not isinstance(binding, tuple)
            or len(binding) != 4
            or not all(isinstance(part, str) for part in binding)
        ):
            raise _fixed("the piece producer binding must carry its closed association")
        if binding[1] != owning.endpoint:
            raise _fixed("the piece producer binding keeps the original endpoint family")
        if not isinstance(piece.call_id, str) or piece.call_id != binding[0]:
            raise _fixed("the piece producer binding names the actual producing call")
        if piece_index == 0:
            if binding[2] != owning.tool_name or binding[3] != owning.argument_fingerprint:
                raise _fixed("the initial piece binds the read's own owner identity")
        pfact = owning.piece_facts[piece_index]
        if (
            not isinstance(pfact, tuple)
            or len(pfact) != 4
            or isinstance(pfact[0], bool)
            or not isinstance(pfact[0], int)
            or isinstance(pfact[1], bool)
            or not isinstance(pfact[1], int)
            or isinstance(pfact[2], bool)
            or not isinstance(pfact[2], int)
        ):
            raise _fixed("the owning result piece facts must carry closed metadata")
        if (
            pfact[0] != piece_index
            or pfact[1] != piece.char_length
            or pfact[2] != piece.byte_length
        ):
            raise _fixed("the owning result piece facts keep the original span metadata")


class RootRegionAdmissionEntry(_GraphFrozen):
    """One region-compatible retained admission entry.

    Constructor-compatible with the ACTUAL G
    ``_assemble_file_entries`` typed generic FILE entry field set
    (``entry_class, content_key, key_record, width, member_classes,
    root_digest, proof, admitted_segments, witnesses``).  The ROOT
    entry additionally carries ``root_source``: the ACTUAL
    ``ResolvedRootRegionSource`` record by immutable reference with
    its explicit envelope / read / read_region provenance (the closed
    R provenance classes; a widened old-I retained-root provenance is
    NOT accepted because its closed old-H validators reject or
    misinterpret region provenance).  The root body is retained by
    immutable reference ONLY (one root body, no duplicate owned root-
    text copy); the read-only properties reference ``root_source``.

    ROOT rows: width 1, one normalized AGENTS.md occurrence,
    ELIGIBLE authority, the sole PROVEN group bound to the SELECTED
    governing root digest, the exact empty root legal, and NO
    fabricated file proof/read witnesses (compatible maximal
    governing witnesses remain in the actual R/Q/P selection).  FILE
    rows retain the FIRST compatible original BundleProof by
    InstanceOf reference, their ORIGINAL admitted segment indices and
    ALL distinct original witness coordinates in canonical order;
    root-only properties are absent.  Legitimate compatible
    root-bearing FILE rows may coexist with the ONE governing root
    entry (a same-bytes proven root-path read is a distinct file
    entry, never a second governing root).  Object construction is
    not authentication: the leaf law re-derives the actual canonical
    018-c key and re-runs the ACTUAL closed R source law (including
    its own bounded content pass), so a copied or detached record is
    refused, not trusted by tag.
    """

    entry_class: EntryClass
    content_key: str = Field(pattern=r"^[0-9a-f]{64}$")
    key_record: InstanceOf[BundleKeyRecord]
    width: int = Field(ge=1)
    member_classes: tuple[MemberClass, ...] = Field(min_length=1)
    root_digest: str = Field(pattern=r"^[0-9a-f]{64}$")
    proof: InstanceOf[BundleProof] | None = None
    admitted_segments: tuple[int, ...] = ()
    witnesses: tuple[InstanceOf[CurrentAdmissionWitness], ...] = ()
    #: The actual resolved root source by immutable reference (ROOT
    #: rows only; explicit envelope/read/read_region provenance).
    root_source: InstanceOf[ResolvedRootRegionSource] | None = None

    @field_validator("content_key", "root_digest")
    @classmethod
    def _v_hex(cls, value: str, info: Any) -> str:
        return _check_hex64(value, getattr(info, "field_name", "key") or "key")

    @field_validator("witnesses")
    @classmethod
    def _v_witnesses(
        cls, value: tuple[CurrentAdmissionWitness, ...], info: Any
    ) -> tuple[CurrentAdmissionWitness, ...]:
        # The copied nested witness record is closed O(1) BEFORE the
        # canonical coordinate sort reads any field (a bypassed
        # partial witness is a fixed private error, never an
        # attribute error in the sorter).
        for witness in value:
            if not _r_fields_present(
                witness,
                (
                    "occurrence_id",
                    "request_index",
                    "call_position",
                    "result_position",
                    "segment_indices",
                ),
            ):
                raise _fixed("the retained witness must carry its closed fields")
        record = info.data.get("key_record")
        if not isinstance(record, BundleKeyRecord):
            # The BEFORE-parse handler guarantees the provided
            # record is a closed canonical record (closed bound
            # sets included) BEFORE any field stage runs; this is
            # the same fixed record channel if that guarantee is
            # ever broken (defense, not the primary gate).
            raise _fixed("the entry key record must be the actual canonical record")
        _s_witnesses_sorted_deduplicated(value, record.proof_bounds.max_segments)
        return tuple(value)

    @model_validator(mode="before")
    @classmethod
    def _v_member_count_before_parsing(cls, data: Any) -> Any:
        # BEFORE-PARSING closed count gate: direct-constructor field
        # parsing visits the raw member-class elements (enum
        # coercion) BEFORE the after-validator, so the ACTUAL carried
        # admission cap on the member occurrence COUNT closes -- via
        # the SHARED O(1) record preflight (the closed provided
        # record/bounds, exact original class and hard range) --
        # before any element is parsed.  The PROVIDED record class
        # closes BEFORE any element parsing: a missing or wrong-class
        # record is its OWN fixed private record error here (never
        # defaulted to a valid cap, never left to a field fence after
        # element parsing); a partial or malformed provided record is
        # refused with the preflight's OWN fixed private errors, never
        # skipped to a silent valid-cap fallback.  The raw member
        # sequence class closes to the admitted list/tuple shapes
        # (any other iterable is refused before Pydantic can traverse
        # unbounded elements), and the O(1) cap and record-alignment
        # counts close before element conversion.  Legitimate
        # normalization of raw values under the cap and aligned with
        # the record proceeds unchanged.
        if isinstance(data, Mapping):
            has_record = "key_record" in data
            record: object = data.get("key_record")
            member_classes: object = data.get("member_classes")
        else:
            has_record = hasattr(data, "key_record")
            record = getattr(data, "key_record", None)
            member_classes = getattr(data, "member_classes", None)
        # The PROVIDED record class closes BEFORE any element
        # parsing: a missing or wrong-class record is its OWN fixed
        # private record error here (a wrong record plus an over-cap
        # raw vector must not produce a per-element enum storm, and
        # a malformed record is never defaulted to a valid cap).
        if not has_record:
            raise _fixed("the admission entry must carry its key record")
        if not isinstance(record, BundleKeyRecord):
            raise _fixed("the entry key record must be the actual canonical record")
        cap = _s_key_record_preflight(record)
        if not isinstance(member_classes, (list, tuple)):
            # Unsupported raw container class (generator, set, dict,
            # string, None, ...): refuse BEFORE any element
            # iteration -- Pydantic would otherwise traverse
            # unbounded elements before the after-validator; the
            # list/tuple normalization path is the only admitted raw
            # sequence shape.
            raise _fixed("member classes must carry a closed list or tuple before parsing")
        if len(member_classes) > cap:
            raise _fixed("member classes exceed the actual carried admission cap before parsing")
        if len(member_classes) != len(record.member_occurrences):
            raise _fixed("member classes must align with the member occurrences before parsing")
        # The PROOF-CONTEXT container/count gates close BEFORE any
        # admitted-segment element parsing, UNCONDITIONALLY for all
        # entry variants (the direct constructor parses the raw
        # admitted-segment elements BEFORE the after-validator, and
        # a wrong or absent provided proof must not authorize an
        # early vector walk by skipping the proof branch).  The raw
        # admitted sequence class closes to the admitted list/tuple
        # shapes (any other iterable is refused before Pydantic can
        # traverse unbounded elements); the variant-specific O(1)
        # count then closes: the FILE context under the ACTUAL
        # retained proof segment population (whose ORIGINAL B
        # population caps close FIRST, so an oversized copied
        # population cannot widen the raw-index domain -- a hoisted
        # postparse cap alone is too late for field parsing), the
        # legal ROOT context (proof None admits the root, not proof
        # segments, so its original allowed count is zero) and a
        # wrong/partial provided proof under NO authorized walk.
        # The witness raw container/count gates close the SAME way
        # for every variant (see the witness block below): any raw
        # iterable that is not the closed list/tuple shape is
        # refused before Pydantic can traverse unbounded witness
        # elements, and the witness COUNT is a DIFFERENT domain
        # from the admitted segments -- it closes under the ACTUAL
        # carried G association-attempt cap (the safe upper bound
        # of the real G association domain; never a new fixed cap
        # and never the history occurrence population, where one
        # genuine occurrence may carry multiple same-key plan
        # witnesses).
        proof: object = (
            data.get("proof") if isinstance(data, Mapping) else getattr(data, "proof", None)
        )
        # The SAME omission/explicit-None distinction closes the
        # other defaulted tuple field: an EXPLICIT provided None is
        # a malformed value distinct from the LEGAL omission (the
        # default empty tuple) and refuses with the fixed
        # container error before the field stage.
        has_admitted = (
            "admitted_segments" in data
            if isinstance(data, Mapping)
            else hasattr(data, "admitted_segments")
        )
        admitted: object = (
            data.get("admitted_segments")
            if isinstance(data, Mapping)
            else getattr(data, "admitted_segments", None)
        )
        if has_admitted and admitted is None:
            raise _fixed("admitted segments must carry a closed list or tuple before parsing")
        if admitted is not None:
            if not isinstance(admitted, (list, tuple)):
                raise _fixed("admitted segments must carry a closed list or tuple before parsing")
            if isinstance(proof, BundleProof):
                # The ACTUAL provided proof's required populations
                # close O(1) BEFORE either len is read (a bypassed
                # model_construct proof missing a field is a fixed
                # private error, never an AttributeError, never a
                # malformed-provided fallback), and the ORIGINAL B
                # segment/member population caps close BEFORE the
                # provided len may authorize raw-index parsing:
                if (
                    not _r_fields_present(proof, ("segments", "requested_members"))
                    or not isinstance(proof.segments, tuple)
                    or not isinstance(proof.requested_members, tuple)
                ):
                    raise _fixed(
                        "the entry proof must carry its closed segment population before parsing"
                    )
                if len(proof.segments) > record.proof_bounds.max_segments:
                    raise _fixed("the retained proof segments exceed the actual carried proof cap")
                if len(proof.requested_members) > record.proof_bounds.max_members:
                    raise _fixed("the retained proof members exceed the actual carried proof cap")
                if len(admitted) > len(proof.segments):
                    raise _fixed(
                        "admitted segments exceed the actual proof segment domain before parsing"
                    )
            elif len(admitted) != 0:
                # proof is None (the legal ROOT variant) or a wrong
                # provided proof: no closed proof context may
                # authorize any admitted vector walk; the root row
                # admits the root, not proof segments, so the
                # original allowed count is zero (legitimate empty
                # list/tuple normalization and ordinary FILE values
                # under a closed proof are untouched).
                raise _fixed(
                    "admitted segments require the closed retained proof context before parsing"
                )
        # The raw WITNESS container/count gates close BEFORE the
        # witness elements can be parsed, for every entry variant
        # (the nested witness records are parsed AFTER this handler;
        # a counting iterator or other unbounded iterable must not
        # be traversed by Pydantic): the raw container class closes
        # to the admitted list/tuple shapes, and the O(1) count then
        # closes under the ACTUAL carried G association-attempt cap
        # whenever the closed retained proof context is present
        # (max_reverse_associations is the actual carried domain --
        # a safe upper bound of the real G association law, never a
        # new fixed cap and never the history occurrence
        # population: one genuine occurrence may carry multiple
        # same-key plan witnesses).  An EXPLICIT provided None is a
        # malformed value distinct from the LEGAL omission (the
        # default empty tuple) and refuses with the same fixed
        # container error before the field stage (never a per-field
        # tuple_type error after stage entry).  A ROOT row is
        # evidenced, never a fabricated read witness: its closed
        # witness count is zero and a malformed ROOT proof context
        # (even a genuine spliced FILE proof) never authorizes the
        # FILE witness domain -- the variant context closes O(1)
        # from the raw entry class, never solely from the provided
        # proof.  Under any other wrong provided proof no closed
        # proof context may authorize the witness walk; legitimate
        # empty list/tuple normalization stays untouched.
        has_witnesses = (
            "witnesses" in data if isinstance(data, Mapping) else hasattr(data, "witnesses")
        )
        witnesses: object = (
            data.get("witnesses") if isinstance(data, Mapping) else getattr(data, "witnesses", None)
        )
        if has_witnesses and witnesses is None:
            raise _fixed("the entry witnesses must carry a closed list or tuple before parsing")
        raw_entry_class: object = (
            data.get("entry_class")
            if isinstance(data, Mapping)
            else getattr(data, "entry_class", None)
        )
        is_root_row = raw_entry_class == EntryClass.ROOT_ENTRY
        if witnesses is not None:
            if not isinstance(witnesses, (list, tuple)):
                raise _fixed("the entry witnesses must carry a closed list or tuple before parsing")
            if is_root_row:
                # The ROOT variant context closes O(1): the closed
                # count is zero and the (possibly spliced) proof
                # never authorizes the FILE witness domain; the
                # legal empty list/tuple stays untouched.
                if len(witnesses) != 0:
                    raise _fixed("the root entry is evidenced, never a fabricated read witness")
            elif isinstance(proof, BundleProof):
                if len(witnesses) > record.admission_bounds.max_reverse_associations:
                    raise _fixed(
                        "the entry witnesses exceed the actual carried association domain "
                        "before parsing"
                    )
            elif len(witnesses) != 0:
                if proof is None:
                    raise _fixed("the root entry is evidenced, never a fabricated read witness")
                raise _fixed(
                    "entry witnesses require the closed retained proof context before parsing"
                )
        return data

    @model_validator(mode="after")
    def _v_entry(self) -> RootRegionAdmissionEntry:
        _s_entry_leaf_closed(self)
        return self

    # --- Read-only convenience properties (reference only; they
    # never copy or own root bytes) -------------------------------
    @property
    def root_source_kind(self) -> str | None:
        """The explicit resolved-source provenance class (closed
        envelope/read/read_region) on a root row, else None."""
        source = self.root_source
        if source is None:
            return None
        if source.kind not in _S_SOURCE_KINDS:
            raise _fixed("the resolved source kind is not a closed variant")
        return source.kind

    @property
    def root_body_byte_length(self) -> int | None:
        """The resolved root body byte length by reference (root rows
        only); no owned copy is made or retained."""
        source = self.root_source
        if source is None:
            return None
        return source.root_byte_length

    def __repr__(self) -> str:  # noqa: D105 - privacy law
        source = self.root_source
        if self.entry_class is EntryClass.ROOT_ENTRY:
            kind = source.kind if source is not None else None
            source_desc = (
                f"<protected root source kind={kind!r} "
                f"{source.root_byte_length if source is not None else 0} bytes>"
            )
        else:
            source_desc = "<proof-carried source>"
        return (
            "RootRegionAdmissionEntry("
            f"entry_class={self.entry_class.value!r}, "
            f"content_key={self.content_key!r}, "
            f"key_record=<canonical record suppressed>, "
            f"width={self.width!r}, "
            f"member_classes={[m.value for m in self.member_classes]!r}, "
            f"root_digest={self.root_digest!r}, "
            f"admitted_segments={self.admitted_segments!r}, "
            f"source={source_desc}, "
            f"root_source={'yes' if source is not None else 'no'}, "
            f"witnesses={len(self.witnesses)})"
        )

    __str__ = __repr__


def root_region_admission_model_scope_key(
    p_lineage_key: str,
    model_contract_version: str,
    model_policy_version: str,
    r_scope_key: str,
    g_contract_version: str,
    g_policy_version: str,
    g_bounds: CurrentAdmissionBounds,
) -> str:
    """The STABLE model configuration scope identity.

    Binds the ACTUAL validated P lineage identity (the P
    ``lineage_key`` recomputed from the actual namespace fields; it is
    the lineage scope identity and does NOT contain the carried
    revision, so the scope is stable across a genuine input revision
    or selected-root change at the same namespace/configuration), the
    ACTUAL re-derived R scope key (which itself binds the actual P
    lineage key, the R/Q/F/E contract/policy versions, the actual
    graph version and every effective R/Q/F/E bound), the NEW model
    contract/policy versions, and the ACTUAL G contract/policy
    versions and bounds.  The actual P/R context already binds the
    P/Q/R/E/F and original inherited versions/bounds through the R
    scope; no copied scope key is ever hashed as a substitute for the
    field re-derivation at the parent.  The carried revision, the
    selected root digest and the actual F/E graph scopes are joined
    separately at the parent and are never part of this stable
    configuration identity (never clocks).  An explicitly named
    derived snapshot identity may bind the revision, but is neither
    this stable configuration identity nor a C semantic content key.
    """
    # The closed O(1) preflight runs BEFORE any serialization walk:
    # the actual 64-hex key inputs, the closed version texts and the
    # exact ORIGINAL G bounds class/scalars (a shadow subclass with
    # redeclared ranges or a partial record refuses here, never
    # inside the dump).
    if not isinstance(p_lineage_key, str):
        raise _fixed("the model scope key P lineage input must carry closed 64-hex text")
    _check_hex64(p_lineage_key, "p_lineage_key")
    if not isinstance(r_scope_key, str):
        raise _fixed("the model scope key R scope input must carry closed 64-hex text")
    _check_hex64(r_scope_key, "r_scope_key")
    for name, value in (
        ("model_contract_version", model_contract_version),
        ("model_policy_version", model_policy_version),
        ("g_contract_version", g_contract_version),
        ("g_policy_version", g_policy_version),
    ):
        if not isinstance(value, str):
            raise _fixed("the model scope key version inputs must carry closed text")
        _check_text(value, name, 128)
    if not _s_g_bounds_closed(g_bounds):
        raise _fixed("the G admission bounds must be closed under the original class and ranges")
    payload = [
        p_lineage_key,
        model_contract_version,
        model_policy_version,
        r_scope_key,
        g_contract_version,
        g_policy_version,
        json.dumps(g_bounds.model_dump(mode="json"), sort_keys=True, separators=(",", ":")),
    ]
    return _sha256_hex(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8"))


class RootRegionAdmission(_GraphFrozen):
    """One region-compatible admission parent (COMPONENT DATA).

    Carries the ACTUAL P input state, the ACTUAL P namespace (a valid
    copy is accepted by VALUE: the namespace's own recomputed
    ``lineage_key`` must equal the state's; the state and proof
    identities promised by this contract are identity, not structural
    equality) and the ACTUAL R result by immutable InstanceOf
    references, the ACTUAL unchanged G ``CurrentAdmissionBounds``,
    the mandatory root entry, the FILE entries, the complete path
    associations (the actual G row model) and the actual bounded
    reason/count/resource metadata required by the accepted G law
    (constructor values are NOT authenticated runtime measurements:
    no model here proves actual G attempts/work or a complete
    same-run consumer).

    At the parent the complete LEAF law is re-run (not tag
    equality), the actual namespace/key/version/bound context is
    re-derived, and the joins run: the exact input state to
    ``r_result.state`` (identity), the P namespace by lineage
    identity, the actual R READY outcome with its resolved source
    joined to ``root_entry.root_source`` BY IDENTITY, the actual
    Q/F/E evidence state/revision/root-digest joins, the original
    selected fact/occurrence/proof membership in the SAME input
    state, and the complete reverse-index law.  A non-ready or
    refused R cannot describe a ready admission; a source or graph
    spliced from a later genuine state refuses even when the
    selected root bytes are equal.  The full closed law of the
    ACTUAL resolved source (including its own bounded content pass)
    runs at the parent as well; the S budget recipe charges every
    actual invocation at leaf AND admission parent, including
    metadata, before work.
    """

    state: InstanceOf[RootRegionLineageState]
    ns: InstanceOf[RootRegionLineageNamespace]
    r_result: InstanceOf[RootRegionGraphResult]
    g_bounds: InstanceOf[CurrentAdmissionBounds]
    root_entry: InstanceOf[RootRegionAdmissionEntry]
    entries: tuple[InstanceOf[RootRegionAdmissionEntry], ...] = ()
    path_associations: tuple[InstanceOf[CurrentAdmissionPathAssociation], ...] = ()
    model_contract_version: str = ROOT_REGION_ADMISSION_MODELS_CONTRACT_VERSION
    model_policy_version: str = ROOT_REGION_ADMISSION_MODELS_POLICY_VERSION
    g_contract_version: str = CURRENT_ADMISSION_CONTRACT_VERSION
    g_policy_version: str = CURRENT_ADMISSION_POLICY_VERSION
    scope_key: str
    entries_retained: int = Field(ge=1)
    member_occurrences_charged: int = Field(ge=1)
    reverse_association_attempts: int = Field(ge=0)
    emitted_admission_reasons: int = Field(ge=0, le=64)
    admission_reasons: tuple[CurrentAdmissionLimitation, ...] = ()

    @model_validator(mode="before")
    @classmethod
    def _v_parent_counts_before_parsing(cls, data: Any) -> Any:
        # BEFORE-PARSING closed context/count gate: direct-
        # constructor field parsing visits the raw entry and
        # association-row elements BEFORE the after-validator, so
        # the PROVIDED namespace context (actual class, closed
        # fields, closed actual admission bounds) closes first, and
        # then under the ACTUAL closed bounds the O(1) retained-
        # entry count (the mandatory root entry is the +1 the
        # accepted G cap counts) and the reverse-association count
        # close before any element is parsed; an unsupported raw
        # container class is refused before Pydantic can traverse
        # unbounded elements.  An invalid provided context raises
        # its OWN fixed private error here, never a silent pass-
        # through that lets Pydantic traverse an oversized raw
        # vector, and never an attribute error at the cap read;
        # the field defaults (empty tuple) remain legitimate.
        # Normalization of raw values under the actual caps
        # proceeds unchanged.
        if isinstance(data, Mapping):
            ns: object = data.get("ns")
            raw_entries: object = data.get("entries", ())
            raw_rows: object = data.get("path_associations", ())
        else:
            ns = getattr(data, "ns", None)
            raw_entries = getattr(data, "entries", ())
            raw_rows = getattr(data, "path_associations", ())
        if not isinstance(ns, RootRegionLineageNamespace):
            raise _fixed("the admission parent must carry its actual namespace context")
        if not _r_fields_present(ns, _S_NS_FIELDS):
            raise _fixed("the admission parent namespace must carry its closed fields")
        if not _s_bounds_set_closed(ns.bounds, BundleAdmissionBounds):
            raise _fixed(
                "the provided inherited admission bounds must be closed under the "
                "original class and ranges"
            )
        if not isinstance(raw_entries, (list, tuple)):
            raise _fixed("the admission entries must carry a closed list or tuple before parsing")
        if len(raw_entries) + 1 > ns.bounds.max_entries:
            raise _fixed("the admission entries exceed the actual carried entry cap before parsing")
        if not isinstance(raw_rows, (list, tuple)):
            raise _fixed("the path associations must carry a closed list or tuple before parsing")
        if len(raw_rows) > ns.bounds.max_reverse_associations:
            raise _fixed(
                "the path associations exceed the actual carried association cap before parsing"
            )
        return data

    @field_validator("scope_key")
    @classmethod
    def _v_scope_key(cls, value: str, info: Any) -> str:
        return _check_hex64(value, getattr(info, "field_name", "scope") or "scope")

    @field_validator("model_contract_version", "model_policy_version")
    @classmethod
    def _v_model_versions(cls, value: str, info: Any) -> str:
        field_name = getattr(info, "field_name", "version") or "version"
        expected = (
            ROOT_REGION_ADMISSION_MODELS_CONTRACT_VERSION
            if field_name == "model_contract_version"
            else ROOT_REGION_ADMISSION_MODELS_POLICY_VERSION
        )
        if value != expected:
            raise _fixed("the S model contract/policy versions are the actual fixed tags")
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

    @field_validator("admission_reasons", mode="before")
    @classmethod
    def _v_admission_reasons_count(cls, value: object, info: ValidationInfo) -> object:
        # BEFORE-PARSING closed container/count gate: the closed
        # sequence container, the hard-64 ceiling and the PROVIDED
        # bound records refuse BEFORE any element enum conversion
        # (no per-element error storm).  The provided G / inherited
        # admission bound records are CLOSED under their exact
        # ORIGINAL classes and hard ranges BEFORE any cap is read
        # (a malformed provided record is its own fixed private
        # boundary error, never skipped to a silent valid-cap
        # fallback over its valid-looking sibling scalar); the
        # actual caps are then read O(1) under the closed fences.
        # A MISSING inherited bounds attribute on a partial
        # namespace is the early field-existence fence's own fixed
        # error, not this cap gate's.  The sorted/dedup walk and
        # the caps under the closed bound fences run in the model
        # validator afterwards (the accepted G diagnostic law).
        if not isinstance(value, (list, tuple)):
            raise _fixed("admission reasons must carry the closed sequence container")
        if len(value) > 64:
            raise _fixed("emitted admission reasons exceed the hard ceiling")
        cap = 64
        g_bounds = info.data.get("g_bounds")
        if g_bounds is not None:
            if not _s_g_bounds_closed(g_bounds):
                raise _fixed(
                    "the provided G admission bounds must be closed under the "
                    "original class and ranges"
                )
            cap = min(cap, g_bounds.max_diagnostics)
        ns = info.data.get("ns")
        ns_bounds = getattr(ns, "bounds", None) if ns is not None else None
        if ns_bounds is not None:
            if not _s_bounds_set_closed(ns_bounds, BundleAdmissionBounds):
                raise _fixed(
                    "the provided inherited admission bounds must be closed under the "
                    "original class and ranges"
                )
            cap = min(cap, ns_bounds.max_diagnostics)
        if len(value) > cap:
            raise _fixed(
                "emitted admission reasons exceed the actual diagnostic caps before parsing"
            )
        return value

    @model_validator(mode="after")
    def _v_admission(self) -> RootRegionAdmission:
        # Phase 0: closed field-existence fences BEFORE any
        # dereference (a partial or foreign parent record is a fixed
        # typed boundary error, never an attribute error): the
        # parent itself, then the ACTUAL carried state / namespace /
        # R result / G bounds records, so no nested attribute can
        # attribute-error before the closed law runs.
        if not _r_fields_present(self, _S_PARENT_FIELDS):
            raise _fixed("the admission parent must carry its closed fields")
        # The S/G OWN carried version tags close at the phase-0
        # boundary, immediately after the closed field-existence
        # fence and BEFORE any nested, hash or source work: at the
        # carrying boundary (model_validate of an existing
        # instance) the field validators do not rerun, so the
        # ACTUAL fixed supported identities are re-checked here and
        # a coherently recomputed scope key never re-supports a
        # changed tag.
        for tag, expected in (
            ("model_contract_version", ROOT_REGION_ADMISSION_MODELS_CONTRACT_VERSION),
            ("model_policy_version", ROOT_REGION_ADMISSION_MODELS_POLICY_VERSION),
        ):
            value = getattr(self, tag)
            if not isinstance(value, str):
                raise _fixed("the admission parent S version tags must carry closed text")
            if value != expected:
                raise _fixed("the S model contract/policy versions are the actual fixed tags")
        for tag, expected in (
            ("g_contract_version", CURRENT_ADMISSION_CONTRACT_VERSION),
            ("g_policy_version", CURRENT_ADMISSION_POLICY_VERSION),
        ):
            value = getattr(self, tag)
            if not isinstance(value, str):
                raise _fixed("the admission parent G version tags must carry closed text")
            if value != expected:
                raise _fixed("the carried G contract/policy versions are the actual fixed tags")
        if not _r_fields_present(self.state, _S_STATE_FIELDS):
            raise _fixed("the admission parent state must carry its closed fields")
        # The ACTUAL wrapped D state class closes at the phase-0
        # boundary BEFORE any D attribute is dereferenced (a
        # copied/foreign class is a fixed private boundary error,
        # never a revalidated substitute; a partial ACTUAL D
        # model still reaches the closed field-existence gate
        # below, never an attribute error).
        if not isinstance(self.state.d_state, CausalHistoryState):
            raise _fixed("the wrapped D state must be the actual causal-history state")
        if not _r_fields_present(self.state.d_state, _S_D_STATE_FIELDS):
            raise _fixed("the admission parent D state must carry its closed fields")
        if not _r_fields_present(self.ns, _S_NS_FIELDS):
            raise _fixed("the admission parent namespace must carry its closed fields")
        if not _r_fields_present(self.r_result, _R_RESULT_FIELDS):
            raise _fixed("the admission parent R result must carry its closed fields")
        # Phase 1: the ACTUAL eleven bound sets fenced under their
        # expected concrete classes and original hard ranges BEFORE
        # any cap is read or any serializer walks (no silent default
        # for a malformed provided record, no cap raise).
        if not _s_all_eleven_bound_sets_closed(self.ns, self.r_result, self.g_bounds):
            raise _fixed("the actual eleven carried bound sets must be closed scalar sets")
        # Phase 1b: closed O(1) COUNT gates under the now-readable
        # actual caps BEFORE any entry/row/reason element traversal
        # (the accepted G parent law: the caps bound the retained
        # containers, and an overbound container refuses before any
        # element work).
        if len(self.entries) + 1 > self.ns.bounds.max_entries:
            raise _fixed("retained entries cannot exceed the actual inherited entry cap")
        if len(self.path_associations) > self.ns.bounds.max_reverse_associations:
            raise _fixed("retained associations cannot exceed the actual inherited cap")
        if (
            len(self.admission_reasons) > self.ns.bounds.max_diagnostics
            or len(self.admission_reasons) > self.g_bounds.max_diagnostics
        ):
            raise _fixed("emitted admission reasons exceed the actual diagnostic caps")
        for counter in (
            self.entries_retained,
            self.member_occurrences_charged,
            self.reverse_association_attempts,
            self.emitted_admission_reasons,
        ):
            if isinstance(counter, bool) or not isinstance(counter, int):
                raise _fixed("the admission counters must carry closed non-bool integers")
        if len(self.path_associations) > self.reverse_association_attempts:
            raise _fixed("reverse association attempts must count every retained association")
        if self.reverse_association_attempts > self.ns.bounds.max_reverse_associations:
            raise _fixed("reverse association attempts cannot exceed the actual inherited cap")
        if (
            tuple(sorted(set(self.admission_reasons), key=lambda r: r.value))
            != self.admission_reasons
        ):
            raise _fixed("admission reasons must be sorted and deduplicated")
        # Phase 2: the actual R result is the SAME-run ready
        # derivation over the EXACT input state (identity where
        # original identity is promised), with its resolved source.
        # The COMPLETE closed R result law re-runs here over the
        # carried (possibly model_copy-bypassed) record: the nested
        # Q/F/E evidence re-joins, the full resolved-source law
        # (including its bounded content pass) and the outcome
        # invariants; the S budget recipe charges this invocation
        # separately from the leaf law's own source invocation.
        r = self.r_result
        if r.outcome is not RootRegionGraphOutcome.READY:
            raise _fixed("a non-ready or refused R cannot describe a ready admission")
        if (
            r.contract_version != ROOT_REGION_GRAPH_CONTRACT_VERSION
            or r.policy_version != ROOT_REGION_GRAPH_POLICY_VERSION
        ):
            raise _fixed("the carried R result must carry the actual fixed graph tags")
        # The copied R result's OWN diagnostic container is closed
        # O(1) BEFORE the shared R law walks it: the shared body is
        # the R AFTER-validator law, whose set/sort walk is closed
        # for GENUINE R records by the R field cap; a bypassed
        # carrying record is not, so the closed container class and
        # the count gate under the actual phase-1-closed cap run
        # here first -- no element iterator may enter before the
        # cap (the old public R recipe stays unchanged).
        if not isinstance(r.diagnostics, tuple):
            raise _fixed("the carried R diagnostics must carry the closed tuple container")
        if len(r.diagnostics) > r.bounds.max_diagnostics:
            raise _fixed("the carried R diagnostics exceed the actual R cap before any walk")
        # The EXACT input P state identity and the closed carried
        # revision / root-fact metadata close BEFORE the shared
        # source validator may walk anything: original identity is
        # identity (never structural equality); the P/D/R
        # revisions are closed non-bool under the ORIGINAL
        # 0..MAX_REVISION range before the original 1:1 P==D and
        # R==P joins (no clock, no revision advance); the P
        # root-fact container/count closes under the ACTUAL ns
        # root-lineage cap before any source/set walk.  The shared
        # body stays the unchanged R AFTER-validator law.
        if r.state is not self.state:
            raise _fixed("the R result must carry the EXACT input P state by reference")
        for revision in (r.state.revision, r.state.d_state.revision, r.revision):
            if isinstance(revision, bool) or not isinstance(revision, int):
                raise _fixed("the carried P/D/R revisions must carry closed non-bool integers")
            if not 0 <= revision <= MAX_REVISION:
                raise _fixed("the carried P/D/R revisions must sit in the original revision range")
        if r.state.revision != r.state.d_state.revision:
            raise _fixed("the P state revision must equal the wrapped D revision")
        if r.revision != r.state.revision:
            raise _fixed("the carried R revision must equal the P state revision")
        root_facts = r.state.root_facts
        if not isinstance(root_facts, tuple):
            raise _fixed("the carried P root facts must carry the closed tuple container")
        if len(root_facts) > self.ns.root_lineage_bounds.max_root_facts:
            raise _fixed(
                "the carried P root facts exceed the actual root-lineage cap before any walk"
            )
        # The four carried D populations close under the ACTUAL
        # ns.history_bounds domains BEFORE the shared R law may
        # walk anything: each population keeps the closed tuple
        # container with its count under the actual inherited cap
        # before any element or set work (the D state class is
        # closed at the phase-0 boundary; P root_facts is the
        # separate root-lineage domain closed above; no full D
        # revalidation is rerun here and no new cap is invented).
        d_state = r.state.d_state
        for name, population, cap in (
            ("issuances", d_state.issuances, self.ns.history_bounds.max_issuances),
            (
                "occurrences",
                d_state.occurrences,
                self.ns.history_bounds.max_occurrences,
            ),
            (
                "results",
                d_state.results,
                self.ns.history_bounds.max_observed_results,
            ),
            (
                "parent_links",
                d_state.parent_links,
                self.ns.history_bounds.max_causal_links,
            ),
        ):
            if not isinstance(population, tuple):
                raise _fixed(f"the wrapped D {name} must carry the closed tuple container")
            if len(population) > cap:
                raise _fixed(f"the wrapped D {name} exceed the actual history cap before any walk")
        # The carried P/D/R lineage keys and the carried R scope
        # key close as closed 64-hex shape BEFORE the shared R law
        # may walk them: a BAD-SHAPE key is refused here with the
        # coherent exact state refs, so later equality joins cannot
        # mask the type fence; a well-formed 64-hex key in the
        # wrong scope is the shared body's actual recomputation
        # and join, never this format gate (format is never scope
        # authority).
        if not isinstance(r.state.lineage_key, str):
            raise _fixed("the carried P lineage key must carry a closed string")
        _check_hex64(r.state.lineage_key, "the carried P lineage key")
        if not isinstance(d_state.history_key, str):
            raise _fixed("the wrapped D history key must carry a closed string")
        _check_hex64(d_state.history_key, "the wrapped D history key")
        if not isinstance(r.lineage_key, str):
            raise _fixed("the carried R lineage key must carry a closed string")
        _check_hex64(r.lineage_key, "the carried R lineage key")
        if not isinstance(r.scope_key, str):
            raise _fixed("the carried R scope key must carry a closed string")
        _check_hex64(r.scope_key, "the carried R scope key")
        # The carried R graph version closes under the EXISTING
        # closed shape fence and joins the ACTUAL namespace graph
        # version BEFORE the shared body.
        if not _r_graph_version_ok(r.graph_version):
            raise _fixed(
                "the carried R graph version must be 1..128 non-space UTF-8 encodable characters"
            )
        if r.graph_version != self.ns.graph_version:
            raise _fixed(
                "the carried R graph version must equal the actual namespace graph version"
            )
        # The READY R result's OWN diagnostics stay EMPTY after the
        # closed container/count cap gates above: the R kernel's
        # own-diagnostic tuple is empty or a singleton on a
        # refusal, and a ready result carries no own diagnostic
        # (the nested Q/F channels are separate evidence, not R
        # diagnostics).
        if r.diagnostics != ():
            raise _fixed("a ready R result carries no own diagnostics")
        # The carried P namespace's ACTUAL scalar / enum / key /
        # version fields close BEFORE the shared R law may hash the
        # scope or walk the source: the ACTUAL admission-mode class,
        # the original C/D identity-text limits with UTF-8
        # encodability, the 64-hex configuration fingerprint, the
        # carried opaque 64-hex keys, the canonical workspace under
        # the ACTUAL configured path bound, the region lineage-id
        # shape and the NINE supported version identities (the
        # actual _region_version_pairs reference) all fence here
        # with fixed private errors.  A format-legal FOREIGN config
        # passes these shape gates and is the ACTUAL
        # phase-3 D-scope re-derivation's refusal, never a silent
        # acceptance (format is never scope authority); a
        # format-legal distinct canonical FOREIGN workspace is
        # refused earlier, by the nested carried-context
        # workspace joins, because the carried context still
        # binds the original namespace workspace (the envelope
        # fact workspace join fires first, then the F-graph/E-
        # overlay joins).  The old
        # public P schema and the accepted C/D recipes stay
        # unchanged.
        if not isinstance(self.ns.mode, AdmissionMode):
            raise _fixed("the carried namespace mode must be the actual admission mode")
        for name, value, limit in (
            ("principal", self.ns.principal, 256),
            ("session", self.ns.session, 256),
            ("repository", self.ns.repository, 256),
            ("route", self.ns.route, 64),
            ("model_identity", self.ns.model_identity, 256),
        ):
            if not isinstance(value, str):
                raise _fixed(f"the carried namespace {name} must carry a closed string")
            _check_text(value, f"the carried namespace {name}", limit)
            try:
                value.encode("utf-8")
            except UnicodeEncodeError:
                raise _fixed(f"the carried namespace {name} must be valid UTF-8") from None
        if not isinstance(self.ns.config_fingerprint, str):
            raise _fixed("the carried namespace config fingerprint must carry a closed string")
        _check_hex64(self.ns.config_fingerprint, "the carried namespace config fingerprint")
        for label, key_value in (
            ("admission_namespace_key", self.ns.admission_namespace_key),
            ("admission_scoped_key", self.ns.admission_scoped_key),
            ("state_scoped_key", self.ns.state_scoped_key),
            ("lineage_key", self.ns.lineage_key),
            ("history_key", self.ns.history_key),
        ):
            if not isinstance(key_value, str):
                raise _fixed(f"the carried namespace {label} must carry a closed string")
            _check_hex64(key_value, f"the carried namespace {label}")
        workspace = self.ns.workspace
        if not isinstance(workspace, str):
            raise _fixed("the carried namespace workspace must carry a closed string")
        if not 1 <= len(workspace) <= 1024:
            raise _fixed("the carried namespace workspace must be 1..1024 characters")
        if len(workspace) > self.ns.graph_bounds.max_path_bytes:
            raise _fixed(
                "the carried namespace workspace must be the canonical absolute POSIX "
                "path under the actual configured path bound"
            )
        if validate_workspace(workspace, self.ns.graph_bounds.max_path_bytes) != workspace:
            raise _fixed(
                "the carried namespace workspace must be the canonical absolute POSIX "
                "path under the actual configured path bound"
            )
        lineage_id = self.ns.lineage_id
        if not isinstance(lineage_id, str):
            raise _fixed("the carried namespace lineage id must carry a closed string")
        if not 1 <= len(lineage_id) <= 128 or any(c.isspace() for c in lineage_id):
            raise _fixed("the carried namespace lineage id must be 1..128 non-space characters")
        try:
            lineage_id.encode("utf-8")
        except UnicodeEncodeError:
            raise _fixed("the carried namespace lineage id must be valid UTF-8") from None
        for actual_version, supported_version in _region_version_pairs(self.ns):
            if not isinstance(actual_version, str):
                raise _fixed("the carried namespace versions must carry closed strings")
            if actual_version != supported_version:
                raise _fixed(
                    "the carried namespace must carry the actual supported version identities"
                )
        _s_nested_qpf_e_closed(r, self.ns)
        _r_result_closed(r)
        selected = r.resolved_source
        if selected is None:
            raise _fixed("the ready R result publishes its resolved root source")
        # Phase 3: the P namespace copy is RE-DERIVED, never trusted:
        # the actual D scope fields revalidate through the real
        # accepted D namespace validators (their recomputed
        # history_key / state_scoped_key / admission keys must equal
        # the carried tags), the lineage key recomputes from the
        # actual namespace fields, the scope describes the EXACT
        # input D history and joins the state's lineage identity;
        # the state/proof identities stay identity, not structural
        # equality.
        try:
            d_ns = CausalHistoryNamespace.model_validate(
                {
                    "principal": self.ns.principal,
                    "session": self.ns.session,
                    "repository": self.ns.repository,
                    "route": self.ns.route,
                    "model_identity": self.ns.model_identity,
                    "config_fingerprint": self.ns.config_fingerprint,
                    "workspace": self.ns.workspace,
                    "mode": self.ns.mode,
                    "admission_version": self.ns.admission_version,
                    "observation_version": self.ns.observation_version,
                    "graph_version": self.ns.graph_version,
                    "reference_version": self.ns.reference_version,
                    "proof_version": self.ns.proof_version,
                    "bounds": self.ns.bounds,
                    "proof_bounds": self.ns.proof_bounds,
                    "graph_bounds": self.ns.graph_bounds,
                    "observation_bounds": self.ns.observation_bounds,
                    "admission_namespace_key": self.ns.admission_namespace_key,
                    "admission_scoped_key": self.ns.admission_scoped_key,
                    "lineage_id": self.ns.lineage_id,
                    "history_version": self.ns.history_version,
                    "arguments_version": self.ns.arguments_version,
                    "history_bounds": self.ns.history_bounds,
                    "history_key": self.ns.history_key,
                    "state_scoped_key": self.ns.state_scoped_key,
                }
            )
        except Exception:
            raise _fixed(
                "the carried namespace must re-derive through the actual D validators"
            ) from None
        if (
            d_ns.history_key != self.ns.history_key
            or d_ns.state_scoped_key != self.ns.state_scoped_key
            or d_ns.admission_namespace_key != self.ns.admission_namespace_key
            or d_ns.admission_scoped_key != self.ns.admission_scoped_key
        ):
            raise _fixed("the carried namespace keys must equal the actual field re-derivation")
        if self.ns.history_key != self.state.d_state.history_key:
            raise _fixed("the carried namespace must describe the exact input D history")
        if self.ns.lineage_key != self.state.lineage_key:
            raise _fixed("the P namespace copy must join the exact state lineage identity")
        if (
            _lineage_key(
                self.ns.history_key,
                self.ns.contract_version,
                self.ns.policy_version,
                self.ns.root_lineage_bounds,
            )
            != self.ns.lineage_key
        ):
            raise _fixed("the carried lineage key must re-derive from the actual namespace fields")
        if (
            self.ns.contract_version != ROOT_REGION_LINEAGE_CONTRACT_VERSION
            or self.ns.policy_version != ROOT_REGION_LINEAGE_POLICY_VERSION
        ):
            raise _fixed("the carried namespace must carry the actual fixed lineage tags")
        # Phase 4: the leaf law is RE-RUN at the admission parent
        # (root row first, then every FILE row); the root row's
        # resolved source is the ACTUAL R resolved source BY
        # IDENTITY, and the selected fact/occurrence/proof are
        # original members of the SAME input state.  The closed
        # field-existence fence runs BEFORE the first root-row
        # dereference (an InstanceOf-carried partial entry is a
        # fixed private error, never an AttributeError), with the
        # identity-before-content ordering preserved.
        if not _r_fields_present(self.root_entry, _S_ENTRY_FIELDS):
            raise _fixed("the admission entry must carry its closed fields")
        if self.root_entry.entry_class is not EntryClass.ROOT_ENTRY:
            raise _fixed("the mandatory root entry is the required ROOT_ENTRY")
        if self.root_entry.root_source is not selected:
            raise _fixed("the root entry carries the actual R resolved source by identity")
        _s_entry_leaf_closed(self.root_entry)
        _s_entry_scope_joined(self.root_entry.key_record, self.ns)
        fact = selected.fact
        # IDENTITY where original identity is promised (value
        # membership is expressly prohibited): the selected fact and
        # its occurrence/proof are ORIGINAL members of the SAME
        # input state (closed bounded metadata scans, never a full
        # source walk).
        if not any(fact is f for f in self.state.root_facts):
            raise _fixed("the selected fact must be an original member of the input state")
        occurrences = self.state.d_state.occurrences
        if selected.occurrence is not None:
            if not any(selected.occurrence is o for o in occurrences):
                raise _fixed(
                    "the selected occurrence must be an original member of the input state"
                )
            if selected.proof is not None and selected.proof is not selected.occurrence.proof:
                raise _fixed("the source proof must be the occurrence's own retained proof")
        # The FILE originality joins (M04): the retained FILE proof
        # is an ORIGINAL retained proof of the SAME input state by
        # identity, and every witness keeps ITS OWN original
        # coordinates of THAT occurrence's retained proof (a
        # detached value-equal clone or a later-genuine splice
        # refuses; one bounded occurrence-id metadata index).
        occurrence_by_id: dict[str, Any] = {}
        for occurrence in occurrences:
            occurrence_by_id[occurrence.occurrence_id] = occurrence
        for entry in self.entries:
            _s_entry_leaf_closed(entry)
            _s_entry_scope_joined(entry.key_record, self.ns)
            proof = entry.proof
            if proof is None:
                raise _fixed("a file entry keeps its retained original proof")
            # The FIRST retained proof is tied to a COMPATIBLE
            # witness: the original occurrence that owns the
            # retained proof must be among the retained witnesses
            # (never an unrelated original occurrence), and every
            # witness's original region must be compatible with
            # THIS entry key (metadata-only; no repeated body
            # passes).
            proof_owner = next((o for o in occurrences if o.proof is proof), None)
            if proof_owner is None:
                raise _fixed("the file entry proof must be an original D-state retained proof")
            # The M04 owner join: the retained proof's ORIGINAL owning
            # occurrence must join its COMPLETE owning result with the
            # exact piece producer association of the retained proof
            # (occurrence/proof presence alone is insufficient).
            _s_occurrence_owning_result_closed(
                proof_owner, self.state.d_state.results, self.ns.history_bounds
            )
            if not any(w.occurrence_id == proof_owner.occurrence_id for w in entry.witnesses):
                raise _fixed("the retained proof must be witnessed by its original occurrence")
            for w in entry.witnesses:
                owner = occurrence_by_id.get(w.occurrence_id)
                if owner is None:
                    raise _fixed("the file witness must name an original D-state occurrence")
                owner_proof = owner.proof
                if (
                    w.request_index != owner_proof.request_index
                    or w.call_position != owner_proof.call_position
                    or w.result_position != owner_proof.result_position
                ):
                    raise _fixed("the file witness must carry the original occurrence coordinates")
                _s_occurrence_owning_result_closed(
                    owner, self.state.d_state.results, self.ns.history_bounds
                )
                _s_witness_region_compatible(w, owner_proof, entry.key_record, self.ns.proof_bounds)
        # Phase 5: the entry set law (accepted G parent law): sorted
        # by distinct content key, the root key never repeated, every
        # row bound to the selected governing root digest.
        keys = [entry.content_key for entry in self.entries]
        for position in range(1, len(keys)):
            if keys[position] <= keys[position - 1]:
                raise _fixed("entries must be sorted by distinct content key")
        if self.root_entry.content_key in keys:
            raise _fixed("the root entry is never repeated among file entries")
        for entry in self.entries:
            if entry.root_digest != selected.root_digest:
                raise _fixed("every row binds the selected governing root digest")
            if entry.key_record.root_digest != selected.root_digest:
                raise _fixed("every row key record binds the selected governing root digest")
        # Phase 6: the complete reverse-index law rechecked at the
        # admission parent: the rows are sorted and deduplicated per
        # path, every row is bound to the ACTUAL C scoped key, the
        # represented paths are EXACTLY the entry member paths and
        # every path maps to ALL AND ONLY its actual admitted
        # content keys (canonical ordered/deduplicated, EXACT
        # equality -- not a subset), and the is_root flag is an
        # actual boolean matching the root path; no extra, missing,
        # unowned or nonmember association.
        expected_paths: dict[str, set[str]] = {}
        for entry in (self.root_entry, *self.entries):
            for path in entry.key_record.member_occurrences:
                expected_paths.setdefault(path, set()).add(entry.content_key)
        for row in self.path_associations:
            if not _r_fields_present(row, ("scoped_key", "path", "content_keys", "is_root")):
                raise _fixed("the reverse row must carry its closed fields")
            if not isinstance(row.is_root, bool):
                raise _fixed("the reverse row root flag must be an actual boolean")
        row_paths = [row.path for row in self.path_associations]
        if row_paths != list(sorted(expected_paths)):
            raise _fixed("the reverse index covers exactly the represented member paths in order")
        for row in self.path_associations:
            if row.scoped_key != self.ns.admission_scoped_key:
                raise _fixed("every reverse row binds the actual admission scoped key")
            if row.is_root != (row.path == ROOT_FILENAME):
                raise _fixed("root association flags must match the root path")
            if row.content_keys != tuple(sorted(expected_paths[row.path])):
                raise _fixed("the reverse index maps every path to all and only its admitted keys")
        # Phase 7: the actual F/E evidence joins run INSIDE the
        # complete closed R result law re-run in phase 2 (the
        # ready-R invariants retain the actual F result / E overlay
        # by reference and re-join their scope/revision/root-digest
        # fields); no duplicated manual F/E asserts here.
        # Phase 8: the closed counter relationships under the
        # ACTUAL inherited caps (counters are constructor values,
        # not authenticated runtime measurements; the accepted G law
        # still bounds them).
        if self.entries_retained != 1 + len(self.entries):
            raise _fixed("entries_retained counts the root entry plus file entries")
        if self.emitted_admission_reasons != len(self.admission_reasons):
            raise _fixed("emitted_admission_reasons must equal the retained reason count")
        if len(self.admission_reasons) > self.g_bounds.max_diagnostics:
            raise _fixed("emitted admission reasons cannot exceed the actual G cap")
        if len(self.admission_reasons) > self.ns.bounds.max_diagnostics:
            raise _fixed("emitted admission reasons cannot exceed the inherited admission cap")
        if len(self.entries) + 1 > self.ns.bounds.max_entries:
            raise _fixed("retained entries cannot exceed the actual inherited entry cap")
        if len(self.path_associations) > self.ns.bounds.max_reverse_associations:
            raise _fixed("retained associations cannot exceed the actual inherited cap")
        member_total = sum(
            len(entry.key_record.member_occurrences) for entry in (self.root_entry, *self.entries)
        )
        if member_total != self.member_occurrences_charged:
            raise _fixed("member_occurrences_charged must equal the retained member total")
        if member_total > self.ns.bounds.max_member_occurrences:
            raise _fixed("retained members cannot exceed the actual inherited member cap")
        # Phase 9: the stable model configuration scope key is
        # RECOMPUTED from the actual fields on every construction (a
        # stale or forged key is refused, never retained).
        expected_scope = root_region_admission_model_scope_key(
            self.state.lineage_key,
            self.model_contract_version,
            self.model_policy_version,
            r.scope_key,
            self.g_contract_version,
            self.g_policy_version,
            self.g_bounds,
        )
        if self.scope_key != expected_scope:
            raise _fixed("scope key must bind the actual P lineage and re-derived R scope")
        return self

    def __repr__(self) -> str:  # noqa: D105 - privacy law
        return (
            "RootRegionAdmission("
            f"lineage_key={self.state.lineage_key!r}, "
            f"revision={self.state.revision!r}, "
            f"workspace={PRIVATE_ID_PLACEHOLDER}, "
            f"selected_root_digest={self.root_entry.root_digest!r}, "
            f"model_contract_version={self.model_contract_version!r}, "
            f"model_policy_version={self.model_policy_version!r}, "
            f"scope_key={self.scope_key!r}, "
            f"root_entry={'yes'}, "
            f"entries={len(self.entries)}, "
            f"path_associations={len(self.path_associations)}, "
            f"entries_retained={self.entries_retained}, "
            f"member_occurrences_charged={self.member_occurrences_charged}, "
            f"reverse_association_attempts={self.reverse_association_attempts}, "
            f"emitted_admission_reasons={self.emitted_admission_reasons}, "
            f"admission_reasons={list(self.admission_reasons)})"
        )

    __str__ = __repr__

"""Versioned root-region graph records (objective 018-r; INERT).

``ROOT_REGION_GRAPH_CONTRACT_VERSION =
"cache-root-region-graph/v1"``;
``ROOT_REGION_GRAPH_POLICY_VERSION =
"root-region-graph-policy/v1"``.

This module binds the pure SELECTED-ROOT-REGION SOURCE + CURRENT-GRAPH
consumer above the accepted 018-p root-region producer and the
018-q root-region currentness query: the immutable
``RootRegionGraphBounds`` (ONE R outer work ceiling plus the own
diagnostic ceiling, each default AND hard), the
``ResolvedRootRegionSource`` (the ONE deterministically
materialized compatible-maximal selected root body with its
ORIGINAL fact/occurrence/proof references and closed local
content law) and the ``RootRegionGraphResult`` (ready / mapped Q
root-currentness-unproven / mapped Q root-authority-conflict /
typed refusal, retaining the EXACT input P state by immutable
reference on EVERY outcome plus the ACTUAL same-run Q result, the
ACTUAL F result and its SAME-run E overlay, when returned, without
rederiving under reset fuel or copying full histories).

The result's ``diagnostics`` are the R-OWN small fixed closed-enum
refusal diagnostics, bounded by the ACTUAL R ``max_diagnostics``
(never a copy of the P/Q/F diagnostic vocabularies, never a global
minimum or an invented error).  The actual Q result retains the
actual P selection (or the exact P validation problem) by
reference, and the actual F result retains its closed F
limitations by reference; an R refusal therefore carries the ACTUAL
returned nested evidence, while a READY result is the ONLY outcome
that publishes a usable resolved source or graph.  A mapped Q
refusal adds no R diagnostics and no F evidence; a mapped F
refusal carries the actual F result with no R diagnostics; an
R-total crossing BEFORE R's own result returned retains whatever
actual Q/F evidence was already computed and exposes exactly the
own work-overflow diagnostic (a positive-interpretation Q outcome
is still mapped to its own R outcome whenever R has fuel for the
mapped result).

Closed scalar/text/class/length fences run BEFORE any serializer
visit, string conversion or serializer work over EVERY effective
bound set and the resolved source records: a deleted actual field
on a real class instance, a MALFORMED model_copy-mutated scalar, a
bool-as-int or a wider value fails the fixed private boundary
first (a valid STRICTER model copy remains legal by value).  The
resolved source's local consistency is ACTUAL content
verification, never a length check: its constructor (and the
result boundary that re-checks it, so a model_copy-bypassed
tampered record is refused at the result boundary too) prefights
the closed text/byte shape and the O(1) character count (bytes are
never fewer than characters, and the recorded byte length is the
hard bound on the owned encode) BEFORE the encode, and then
verifies ``sha256(root_text.encode("utf-8")) == root_digest`` and
``len(encode) == root_byte_length`` over the record's OWN bounded
root text; the charged derivation reserves the matching content
units BEFORE that constructor work and performs its own charged
digest recheck against the actual retained provenance binding.
The content check walks the record's own root text only -- never
the whole original proof/state (the full original-state/proof/
owner traversal stays charged derivation work).

The result's stable scope key recomputes from the ACTUAL P lineage
key (which already binds the inherited D identity/model/workspace/
fields AND the P contract/policy versions through the real P
factory), the R, Q, F and E contract/policy version identities,
EVERY effective R/Q/E/F bound set and the actual inherited graph
version on every construction (factory and direct); a stale or
forged key is refused.  The state revision is separate carried
derivation identity, never a clock and never part of the stable
scope key.  No source copy beyond the ONE materialized root body,
no cache, no storage, no RSS or token limit is introduced.

Object construction is NOT authentication: this is an internal
trusted boundary, never a public body/header authority path.
Errors and operational reprs suppress all private
ID/source/marker/identity values.  The derivation itself lives in
``root_region_graph.py``.
"""

from __future__ import annotations

import hashlib
from enum import StrEnum
from typing import Literal, TypeGuard

from pydantic import Field, InstanceOf, field_validator, model_validator

from .bundle_proof_models import BundleProof
from .causal_history_models import (
    MAX_REVISION,
    CompletedReadOccurrence,
)
from .current_graph_models import (
    CURRENT_GRAPH_CONTRACT_VERSION,
    CURRENT_GRAPH_POLICY_VERSION,
    CurrentGraphBounds,
    CurrentGraphOutcome,
    CurrentGraphResult,
    current_graph_scope_key,
)
from .currentness_models import (
    CURRENTNESS_CONTRACT_VERSION,
    CURRENTNESS_POLICY_VERSION,
    OPAQUE_GROUP_RECIPE_VERSION,
    CurrentnessBounds,
    CurrentnessOverlay,
    currentness_scope_key,
)
from .graph_models import (
    ROOT_FILENAME,
    GraphBounds,
    _check_hex64,
    _fixed,
    _GraphFrozen,
    _sha256_hex,
)
from .observation_models import PRIVATE_ID_PLACEHOLDER
from .root_lineage_models import (
    _HARD_ROOT_FACTS,
    _HARD_ROOT_SOURCE_BYTES,
    EnvelopeRootProvenance,
    ReadRootProvenance,
    RootSelectionOutcome,
)
from .root_region_currentness_models import (
    ROOT_REGION_CURRENTNESS_CONTRACT_VERSION,
    ROOT_REGION_CURRENTNESS_POLICY_VERSION,
    RootRegionCurrentnessBounds,
    RootRegionCurrentnessOutcome,
    RootRegionCurrentnessResult,
    root_region_currentness_scope_key,
)
from .root_region_lineage_models import (
    RootRegionLineageFact,
    RootRegionLineageState,
    RootRegionReadProvenance,
    RootRegionSelectionResult,
)

ROOT_REGION_GRAPH_CONTRACT_VERSION = "cache-root-region-graph/v1"
ROOT_REGION_GRAPH_POLICY_VERSION = "root-region-graph-policy/v1"

_HARD_R_WORK_UNITS = 1048576
_HARD_R_DIAGNOSTICS = 64

#: The actual F bound set hard ceilings (F defaults AND hard, the
#: accepted 018-f law): outer work / own diagnostics.
_HARD_F_WORK_UNITS = 1048576
_HARD_F_DIAGNOSTICS = 64
#: The actual E bound set hard ceilings (E defaults AND hard, the
#: accepted 018-e law).
_HARD_E_PATHS = 16384
_HARD_E_GROUPS = 32768
_HARD_E_WITNESS_MEMBERSHIPS = 65536
_HARD_E_RELATION_PAIRS = 65536
_HARD_E_WORK_UNITS = 1048576
_HARD_E_DIAGNOSTICS = 64


def root_region_graph_scope_key(
    lineage_key: str,
    contract_version: str,
    policy_version: str,
    bounds: RootRegionGraphBounds,
    q_bounds: RootRegionCurrentnessBounds,
    f_bounds: CurrentGraphBounds,
    e_bounds: CurrentnessBounds,
    graph_version: str,
) -> str:
    """The stable R scope key recipe.

    Binds the ACTUAL P lineage key (which already binds the
    inherited identity/model/workspace/version fields through the
    real P/D/C factories AND the P contract/policy versions), the
    R, Q, F and E contract/policy version identities (the actual
    accepted F/E version constants -- the P namespace does NOT
    already bind the separate E/F versions), EVERY effective
    R/Q/E/F bound set and the actual inherited graph version.  It
    does NOT bind the state revision (revision is separate carried
    derivation identity, never a clock or a scope input)."""
    payload = "\x00".join(
        (
            contract_version,
            policy_version,
            ROOT_REGION_CURRENTNESS_CONTRACT_VERSION,
            ROOT_REGION_CURRENTNESS_POLICY_VERSION,
            CURRENT_GRAPH_CONTRACT_VERSION,
            CURRENT_GRAPH_POLICY_VERSION,
            CURRENTNESS_CONTRACT_VERSION,
            CURRENTNESS_POLICY_VERSION,
            lineage_key,
            str(bounds.max_total_work_units),
            str(bounds.max_diagnostics),
            str(q_bounds.max_total_work_units),
            str(q_bounds.max_diagnostics),
            str(f_bounds.max_total_work_units),
            str(f_bounds.max_diagnostics),
            str(e_bounds.max_paths),
            str(e_bounds.max_groups),
            str(e_bounds.max_witness_memberships),
            str(e_bounds.max_relation_pairs),
            str(e_bounds.max_work_units),
            str(e_bounds.max_diagnostics),
            graph_version,
        )
    ).encode("utf-8")
    return hashlib.sha256(b"cache-root-region-graph/v1\x00" + payload).hexdigest()


def _r_int_in(value: object, lo: int, hi: int) -> TypeGuard[int]:
    """Closed scalar fence: exact (non-bool) int in range (a
    type guard: a passed fence narrows the actual value to int)."""
    return isinstance(value, int) and not isinstance(value, bool) and lo <= value <= hi


#: The honest graph-version tag that characterizes the refusal
#: scope when the actual namespace is unusable (its graph version
#: cannot be trusted, read or encoded): a fixed safe value, never
#: the unusable input itself.
_R_REJECTION_GRAPH_VERSION = "unavailable"


def _r_graph_version_ok(value: object) -> bool:
    """Closed version-metadata fence: 1..128 non-space characters
    that ENCODE to UTF-8.  An isolated surrogate or any other
    unencodable actual version metadata fails BEFORE any scope-key
    hash/encode (the derivation maps the unusable namespace to the
    honest safe refusal scope, never an encoder exception)."""
    if not isinstance(value, str):
        return False
    if not 1 <= len(value) <= 128:
        return False
    if any(c.isspace() for c in value):
        return False
    try:
        value.encode("utf-8")
    except UnicodeEncodeError:
        return False
    return True


def root_region_graph_bounds_shape_ok(bounds: object) -> bool:
    """Closed actual-field fence over the OWN bound set: field
    EXISTENCE on the real class instance first (a deleted actual
    field fails closed, never AttributeError), then exact
    non-bool ints within the hard ceilings.  A dumped dict, a
    MALFORMED model_copy-mutated bound (a valid STRICTER model copy
    is legal) or a raw override dictionary fails this BEFORE any
    serializer visit."""
    return (
        isinstance(bounds, RootRegionGraphBounds)
        and hasattr(bounds, "max_total_work_units")
        and hasattr(bounds, "max_diagnostics")
        and _r_int_in(bounds.max_total_work_units, 1, _HARD_R_WORK_UNITS)
        and _r_int_in(bounds.max_diagnostics, 1, _HARD_R_DIAGNOSTICS)
    )


def _r_q_bounds_closed(bounds: object) -> bool:
    """R-PRIVATE closed fence over the actual nested Q bound set
    (field existence, non-bool ints, actual Q hard ceilings)
    BEFORE any cap read or serializer visit."""
    return (
        isinstance(bounds, RootRegionCurrentnessBounds)
        and hasattr(bounds, "max_total_work_units")
        and hasattr(bounds, "max_diagnostics")
        and _r_int_in(bounds.max_total_work_units, 1, _HARD_R_WORK_UNITS)
        and _r_int_in(bounds.max_diagnostics, 1, _HARD_R_DIAGNOSTICS)
    )


def _r_f_bounds_closed(bounds: object) -> bool:
    """R-PRIVATE closed fence over the actual nested F bound set
    (field existence, non-bool ints, actual F hard ceilings)
    BEFORE any cap read or serializer visit."""
    return (
        isinstance(bounds, CurrentGraphBounds)
        and hasattr(bounds, "max_total_work_units")
        and hasattr(bounds, "max_diagnostics")
        and _r_int_in(bounds.max_total_work_units, 1, _HARD_F_WORK_UNITS)
        and _r_int_in(bounds.max_diagnostics, 1, _HARD_F_DIAGNOSTICS)
    )


def _r_e_bounds_closed(bounds: object) -> bool:
    """R-PRIVATE closed fence over the actual nested E bound set
    (field existence, non-bool ints, actual E hard ceilings)
    BEFORE any cap read or serializer visit."""
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


def _r_fields_present(obj: object, names: tuple[str, ...]) -> bool:
    """Narrow closed O(1) field-EXISTENCE fence (the accepted
    O(1) boundary pattern): a partial actual instance (fields
    never set) fails the fixed typed boundary before any
    dereference; no value law is added here."""
    return all(hasattr(obj, name) for name in names)


def _r_p_selection_closed(p_selection: object, lineage_key: str, revision: int) -> bool:
    """The closed O(1) fence over ANY carried non-None P selection
    (constant work only, before outcome dispatch): the actual
    class, the closed identity fields, the lineage/revision join to
    the carried state (exact non-bool bounded revision) and the
    witness container class/count.  No per-witness traversal here
    (the variable association walk stays in its charged READY
    block)."""
    return (
        isinstance(p_selection, RootRegionSelectionResult)
        and _r_fields_present(
            p_selection,
            ("outcome", "selected_source_digest", "witness_facts", "lineage_key", "revision"),
        )
        and p_selection.lineage_key == lineage_key
        and _r_int_in(p_selection.revision, 0, MAX_REVISION)
        and p_selection.revision == revision
        and isinstance(p_selection.witness_facts, tuple)
        and len(p_selection.witness_facts) <= _HARD_ROOT_FACTS
    )


class RootRegionGraphBounds(_GraphFrozen):
    """NEW finite root-region graph bounds (objective 018-r).

    ``max_total_work_units`` is the ONE R outer per derivation
    covering the ENTIRE operation: the O(1) gates and bound
    resolutions, the ACTUAL same-run Q phase (its actual
    independently bounded P phase included), the charged selected-
    source resolution, the ACTUAL F/E phase and graph-stage work,
    and all R association/serialization/construction reservations.
    The ACTUAL Q-local, P, D, B, E, F and GraphBounds domains keep
    their OWN independent ceilings beneath it (the R total is not
    a global minimum, not a reset budget and not a pre-reserved
    whole cap).  ``max_diagnostics`` is the R-OWN total final
    closed-enum diagnostic ceiling per result (the nested Q/F
    results keep their ACTUAL own ceilings, separate and
    unchanged).  Stricter positive values are permitted; ANY wider
    direct construction is refused."""

    #: ONE R outer PER derivation work ledger.
    max_total_work_units: int = Field(default=_HARD_R_WORK_UNITS, ge=1, le=_HARD_R_WORK_UNITS)
    #: R-OWN total final closed-enum diagnostics per result.
    max_diagnostics: int = Field(default=_HARD_R_DIAGNOSTICS, ge=1, le=_HARD_R_DIAGNOSTICS)

    def __repr__(self) -> str:  # noqa: D105 - privacy law
        return (
            "RootRegionGraphBounds("
            f"max_total_work_units={self.max_total_work_units}, "
            f"max_diagnostics={self.max_diagnostics})"
        )

    __str__ = __repr__


class RootRegionGraphDiagnostic(StrEnum):
    """R-OWN small fixed closed-enum refusal diagnostics (018-r).

    These are the R derivation's own typed refusal reasons, NOT a
    copy of the P/Q/F diagnostic vocabularies: a mapped Q refusal
    adds NO R diagnostics (the actual Q result carries the Q
    reasons), a mapped F refusal carries the actual F result (the
    F limitations stay with it), and only the R's own gates /
    work crossings / source-resolution failures emit R
    diagnostics."""

    FOREIGN_SCOPE = "foreign_scope"
    VERSION_UNSUPPORTED = "version_unsupported"
    MALFORMED_BINDING = "malformed_binding"
    WORK_UNITS_OVER_BOUND = "work_units_over_bound"
    SOURCE_RESOLUTION_FAILED = "source_resolution_failed"


class RootRegionGraphOutcome(StrEnum):
    """Fixed closed R outcomes.

    ``ready``: ONLY the actual same-run Q ready, the actual
    selected-source resolution and the actual F graph success all
    hold (it does NOT mean admitted bundles, acquired required
    dependencies, compiled cache, HTTP readiness or v1 runtime).
    ``root_currentness_unproven`` / ``root_authority_conflict``:
    the ACTUAL same-run Q positive-interpretation outcomes mapped
    before any source slicing or F derivation (no usable selected
    source, no graph, no bootstrap fallback).  ``refused``: the
    fixed typed consumer failure (an R-OWN early gate or work
    crossing, a mapped Q refusal, a mapped F refusal, or the
    selected-source resolution failure) -- never relabelled as a
    root absence or a currentness interpretation.  Every non-ready
    result publishes NO usable resolved source or graph (it may
    still retain the ACTUAL returned nested evidence by
    reference)."""

    READY = "ready"
    ROOT_CURRENTNESS_UNPROVEN = "root_currentness_unproven"
    ROOT_AUTHORITY_CONFLICT = "root_authority_conflict"
    REFUSED = "refused"


_R_SOURCE_FIELDS = (
    "kind",
    "fact",
    "root_text",
    "root_digest",
    "root_byte_length",
    "occurrence",
    "proof",
)
_R_SOURCE_KINDS = ("envelope", "read", "read_region")
_R_FACT_FIELDS = ("source_digest", "source_byte_length", "provenance")
# The closed existence fence for a witness fact BEFORE any value
# read: the declared fact fields plus the authority flag actually
# read by the association walk (a deleted field is a fixed typed
# boundary error, never AttributeError).
_R_FACT_WITNESS_FIELDS = _R_FACT_FIELDS + ("authority",)
_R_ENVELOPE_PROV_FIELDS = ("kind", "root_digest", "workspace", "source_byte_length")
_R_READ_PROV_FIELDS = (
    "kind",
    "occurrence_id",
    "call_id",
    "endpoint",
    "read_digest",
    "read_byte_length",
)
_R_REGION_PROV_FIELDS = (
    "kind",
    "occurrence_id",
    "call_id",
    "endpoint",
    "whole_proof_digest",
    "whole_proof_byte_length",
    "root_segment_index",
    "root_member_position",
    "root_member_digest",
    "root_member_byte_length",
)
_R_OCCURRENCE_FIELDS = ("occurrence_id", "call_id", "endpoint", "proof")
_R_PROOF_FIELDS = ("source_digest", "source_byte_length", "root_path")
_R_F_GRAPH_FIELDS = (
    "history_key",
    "revision",
    "workspace",
    "root_path",
    "root_digest",
    "graph_version",
    "reference_version",
    "proof_version",
    "currentness_contract_version",
    "currentness_policy_version",
    "currentness_recipe_version",
    "contract_version",
    "policy_version",
    "bounds",
    "currentness_bounds",
    "graph_bounds",
    "currentness_scope_key",
    "scope_key",
)
_R_E_OVERLAY_FIELDS = (
    "history_key",
    "revision",
    "workspace",
    "policy_version",
    "bounds",
    "scope_key",
)
_R_GRAPH_BOUNDS_FIELDS = (
    "max_requests",
    "max_documents",
    "max_single_source_bytes",
    "max_total_inspected_source_bytes",
    "max_reference_candidates_total",
    "max_reference_candidates_per_document",
    "max_nodes",
    "max_edges",
    "max_depth",
    "max_work_units",
    "max_diagnostics",
    "max_path_bytes",
)


def _r_graph_bounds_closed(bounds: object) -> bool:
    """R-PRIVATE closed fence over the ACTUAL inherited graph bound
    set carried by the F graph (class, field EXISTENCE, exact
    non-bool ints within the actual inherited hard ceilings) BEFORE
    any serializer visit or scope-key rehash: a partial or
    MALFORMED inherited bound is a fixed typed error, never a
    serializer exception or a partial key."""
    return (
        isinstance(bounds, GraphBounds)
        and _r_fields_present(bounds, _R_GRAPH_BOUNDS_FIELDS)
        and _r_int_in(bounds.max_requests, 1, 10_000)
        and _r_int_in(bounds.max_documents, 1, 10_000)
        and _r_int_in(bounds.max_single_source_bytes, 1, 10_000_000)
        and _r_int_in(bounds.max_total_inspected_source_bytes, 1, 16_000_000)
        and _r_int_in(bounds.max_reference_candidates_total, 1, 100_000)
        and _r_int_in(bounds.max_reference_candidates_per_document, 1, 10_000)
        and _r_int_in(bounds.max_nodes, 1, 10_000)
        and _r_int_in(bounds.max_edges, 1, 100_000)
        and _r_int_in(bounds.max_depth, 1, 10_000)
        and _r_int_in(bounds.max_work_units, 1, 10_000_000)
        and _r_int_in(bounds.max_diagnostics, 1, 10_000)
        and _r_int_in(bounds.max_path_bytes, 1, 65_536)
    )


def _r_utf8_byte_length_capped(text: str, cap: int) -> int:
    """No-copy capped UTF-8 byte length over the record's own root
    text (the accepted charged-walk law in miniature): one code
    point at a time, an unencodable isolated surrogate fails
    closed (returns -1) BEFORE any owned encode allocation, and
    the walk exits as soon as the cap is exceeded (returns the
    exceeding count).  The result bounds the later owned encode
    allocation: a declared byte length never authorizes a larger
    actual allocation."""
    total = 0
    for ch in text:
        cp = ord(ch)
        if 0xD800 <= cp <= 0xDFFF:
            return -1
        if cp < 0x80:
            n = 1
        elif cp < 0x800:
            n = 2
        elif cp < 0x10000:
            n = 3
        else:
            n = 4
        total += n
        if total > cap:
            return total
    return total


def _r_source_content_ok(root_text: object, root_digest: object, root_byte_length: object) -> bool:
    """The closed ACTUAL content check over the record's OWN bounded
    root text.  Closed scalar/text/class shape, the O(1) character
    preflight (bytes are never fewer than characters) and the
    NO-COPY capped UTF-8 measurement run BEFORE the owned encode:
    the declared byte length bounds the encode allocation and an
    unencodable or over-length text fails closed without it.  The
    owned encode must then measure exactly the recorded byte
    length and digest to the recorded root digest.  This is
    content verification, never a length-only check, and it walks
    the record's own root text only -- never the whole original
    proof/state."""
    if not isinstance(root_text, str) or not isinstance(root_digest, str):
        return False
    if not _r_int_in(root_byte_length, 0, _HARD_ROOT_SOURCE_BYTES):
        return False
    if not (len(root_digest) == 64 and set(root_digest) <= set("0123456789abcdef")):
        return False
    if len(root_text) > root_byte_length:
        return False
    measured = _r_utf8_byte_length_capped(root_text, root_byte_length)
    if measured != root_byte_length:
        return False
    try:
        actual = root_text.encode("utf-8")
    except UnicodeEncodeError:
        return False
    return len(actual) == root_byte_length and _sha256_hex(actual) == root_digest


def _r_source_closed(src: ResolvedRootRegionSource) -> None:
    """The resolved source closed local joins, shared by the
    source constructor and the R result boundary: the closed
    field-existence fences, the per-kind concrete provenance
    class/tag fences, the whole-proof / root-member /
    occurrence / call / endpoint local joins, the fact
    root-body equality and the ACTUAL content law over the
    record's own bounded root text (a model_copy-bypassed
    tampered record is refused by this law, never trusted by
    reference).  Closed O(1) local checks plus the bounded
    content pass only -- never a whole original proof/state
    traversal."""
    # Closed field-existence fences BEFORE any dereference (a
    # partial or foreign record is a fixed typed boundary error,
    # never an attribute error).
    if not isinstance(src, ResolvedRootRegionSource):
        raise _fixed("the resolved source must be the actual closed record")
    if not _r_fields_present(src, _R_SOURCE_FIELDS):
        raise _fixed("the resolved source must carry its closed fields")
    # The closed kind whitelist runs BEFORE any dispatch or
    # interpolated message, so an unknown variant is refused by a
    # fixed private error and never echoed.
    kind = src.kind
    if kind not in _R_SOURCE_KINDS:
        raise _fixed("the resolved source kind is not a closed variant")
    if not isinstance(src.root_text, str) or not isinstance(src.root_digest, str):
        raise _fixed("the resolved source body must carry closed scalar fields")
    if not _r_int_in(src.root_byte_length, 0, _HARD_ROOT_SOURCE_BYTES):
        raise _fixed("the resolved source body length must be a closed nonnegative scalar")
    if src.occurrence is not None and not isinstance(src.occurrence, CompletedReadOccurrence):
        raise _fixed("the resolved source occurrence must be the actual closed occurrence")
    if src.proof is not None and not isinstance(src.proof, BundleProof):
        raise _fixed("the resolved source proof must be the actual closed proof")
    if not _r_fields_present(src.fact, _R_FACT_FIELDS):
        raise _fixed("the selected fact must carry its closed root body fields")
    p = src.fact.provenance
    if src.kind == "envelope":
        # Class-first fence: the concrete class, the closed
        # field existence (the kind tag included) and only
        # then the kind tag itself must all be the envelope
        # provenance.
        if not isinstance(p, EnvelopeRootProvenance):
            raise _fixed("the envelope source requires the actual envelope provenance")
        if not _r_fields_present(p, _R_ENVELOPE_PROV_FIELDS):
            raise _fixed("the envelope provenance must carry its closed fields")
        if p.kind != "envelope":
            raise _fixed("the envelope provenance kind tag does not match its concrete class")
        if src.occurrence is not None or src.proof is not None:
            raise _fixed("the envelope source carries no occurrence or proof reference")
        if p.root_digest != src.root_digest or p.source_byte_length != src.root_byte_length:
            raise _fixed("the envelope provenance anchor binding must equal the resolved root body")
    else:
        prov_fields = _R_READ_PROV_FIELDS if src.kind == "read" else _R_REGION_PROV_FIELDS
        if not isinstance(
            p, ReadRootProvenance if src.kind == "read" else RootRegionReadProvenance
        ):
            raise _fixed(f"the {src.kind} source requires the actual {src.kind} provenance")
        if not _r_fields_present(p, prov_fields):
            raise _fixed(f"the {src.kind} provenance must carry its closed fields")
        if p.kind != src.kind:
            raise _fixed(f"the {src.kind} provenance kind tag does not match its concrete class")
        if src.occurrence is None or src.proof is None:
            raise _fixed(f"the {src.kind} source carries the actual occurrence and proof")
        if not _r_fields_present(src.occurrence, _R_OCCURRENCE_FIELDS):
            raise _fixed("the occurrence must carry its closed identity fields")
        if not _r_fields_present(src.proof, _R_PROOF_FIELDS):
            raise _fixed("the proof must carry its closed root binding fields")
        if src.kind == "read":
            # Local whole-read joins: the provenance whole-read
            # binding equals the resolved root body AND the
            # actual retained whole proof root binding.
            if not isinstance(p, ReadRootProvenance):
                raise _fixed("the read source requires the actual read provenance")
            if (
                p.read_digest != src.root_digest
                or p.read_byte_length != src.root_byte_length
                or p.read_digest != src.proof.source_digest
                or p.read_byte_length != src.proof.source_byte_length
                or src.proof.root_path != ROOT_FILENAME
            ):
                raise _fixed("the read provenance must join the actual whole proof root binding")
        else:
            # Local whole-proof / root-member joins: the
            # whole-proof aggregate binding joins the actual
            # proof aggregate and the root-member binding
            # equals the resolved root body (the two stay
            # distinct).  Closed scalar metadata first.
            if not isinstance(p, RootRegionReadProvenance):
                raise _fixed("the read_region source requires the actual read_region provenance")
            if not (
                _r_int_in(p.root_segment_index, 0, 2**31 - 1)
                and _r_int_in(p.root_member_position, 0, 2**31 - 1)
            ):
                raise _fixed(
                    "the region provenance coordinates must carry closed nonnegative scalars"
                )
            if (
                p.whole_proof_digest != src.proof.source_digest
                or p.whole_proof_byte_length != src.proof.source_byte_length
                or p.root_member_digest != src.root_digest
                or p.root_member_byte_length != src.root_byte_length
            ):
                raise _fixed(
                    "the region provenance must join the actual proof aggregate and "
                    "root member bindings"
                )
        if src.proof is not src.occurrence.proof:
            raise _fixed("the source proof must be the occurrence's own retained proof")
        if p.occurrence_id != src.occurrence.occurrence_id:
            raise _fixed("the provenance occurrence join must equal the actual occurrence")
        if p.call_id != src.occurrence.call_id or p.endpoint != src.occurrence.endpoint:
            raise _fixed("the provenance call/endpoint joins must equal the actual occurrence")
    # The fact IS the root body record: closed O(1) equality.
    if (
        src.root_digest != src.fact.source_digest
        or src.root_byte_length != src.fact.source_byte_length
    ):
        raise _fixed("the resolved source body must equal the selected fact root body")
    # ACTUAL content law over the record's own bounded root
    # text, AFTER the closed shape preflight (reserved before
    # this constructor work by the charged derivation; a
    # length check alone is NOT content verification).
    if not _r_source_content_ok(src.root_text, src.root_digest, src.root_byte_length):
        raise _fixed("the resolved source text does not match its digest and byte length")


class ResolvedRootRegionSource(_GraphFrozen):
    """The ONE deterministically materialized selected root body
    (objective 018-r).

    ``kind`` is the actual selected provenance class (the concrete
    fact provenance class is fenced against the kind tag BEFORE any
    dispatch, per kind); ``fact`` is the ACTUAL selected
    compatible-maximal P witness fact by immutable reference (its
    ``source_digest``/``source_byte_length`` ARE the root body);
    ``root_text``/``root_digest``/``root_byte_length`` are the
    ACTUAL materialized root body with closed ACTUAL content law
    (constructor and result boundary both verify encode/digest/
    length agreement over the record's own root text after the
    closed shape preflight -- a model_copy-bypassed tampered
    record is refused at the result boundary); ``occurrence``/
    ``proof`` are the ACTUAL original completed occurrence and its
    retained proof by immutable reference (``None`` for the
    envelope kind; for the read/ read_region kinds the concrete
    provenance class AND the whole-proof / root-member digest/
    length local joins are fenced against the actual retained
    proof before the occurrence proof identity and the closed O(1)
    metadata joins bind the provenance to the occurrence).  The
    whole proof aggregate and the selected root member stay
    distinct; no caller flag is echoed as source.  The ORIGINAL
    full-state/proof/owner traversal (segment index/position
    membership, preceding segment sums, the charged slice) stays
    with the charged derivation, not this uncharged constructor."""

    kind: Literal["envelope", "read", "read_region"]
    fact: InstanceOf[RootRegionLineageFact]
    root_text: str
    root_digest: str
    root_byte_length: int = Field(ge=0, le=_HARD_ROOT_SOURCE_BYTES)
    occurrence: InstanceOf[CompletedReadOccurrence] | None = None
    proof: InstanceOf[BundleProof] | None = None

    @field_validator("root_digest")
    @classmethod
    def _v_digest(cls, value: str) -> str:
        return _check_hex64(value, "root_digest")

    @model_validator(mode="after")
    def _v_source(self) -> ResolvedRootRegionSource:
        _r_source_closed(self)
        return self

    def __repr__(self) -> str:  # noqa: D105 - privacy law
        occ = self.occurrence
        return (
            f"ResolvedRootRegionSource(kind={self.kind!r}, "
            f"root_digest={self.root_digest!r}, "
            f"root_byte_length={self.root_byte_length}, "
            f"occurrence_id={occ.occurrence_id if occ is not None else None!r}, "
            f"call_id={PRIVATE_ID_PLACEHOLDER if occ is not None else None!r})"
        )

    __str__ = __repr__


class RootRegionGraphResult(_GraphFrozen):
    """The bounded pure selected-root-region source + current-graph
    derivation result (objective 018-r).

    ``state`` is the EXACT input P state by immutable reference on
    EVERY outcome (no partial positive output, no revision
    advance); ``q_result`` is the ACTUAL same-run Q result by
    reference -- ``None`` until the actual Q phase has returned
    (early R gates and an R-total crossing before the Q return
    carry no fabricated Q evidence) and, once returned, retained on
    EVERY later outcome; ``f_result`` is the ACTUAL F result by
    reference (``None`` until the F phase has returned, including
    a mapped Q refusal that never runs F); ``e_overlay`` is the
    ACTUAL SAME-run E overlay returned by the accepted F seam
    (present exactly when the actual F result is OK, retained as
    bounded evidence on an R-total crossing that happens during
    the final output reservation); ``resolved_source`` is
    published ONLY on ``ready``.  ``diagnostics`` are the R-OWN
    fixed closed-enum refusal diagnostics, bounded by the ACTUAL R
    ``max_diagnostics``; a mapped Q or F refusal adds no R
    diagnostics (the actual nested evidence carries them), and an
    R-total crossing before R's own result returned exposes exactly
    the own work-overflow diagnostic while retaining whatever
    actual Q/F evidence was already computed.  ``revision`` /
    ``lineage_key`` carry the actual P state identity (validated,
    never trusted); ``graph_version`` is the actual inherited
    graph version bound by the scope key.  The closed scalar/
    class/length fences over EVERY effective bound set run BEFORE
    the scope-key recomputation reads any cap or serializes any
    field.  The nested Q/F/E evidence is re-joined at this boundary
    BEFORE any copied tag is trusted: the actual fixed nested
    version tags, the actual closed bound sets equal to the
    effective R-carried domains, and the nested scope keys
    recomputed from the nested records' OWN actual fields (a
    copied, stale or foreign tag is a fixed typed error); the
    READY resolved source re-runs its FULL closed law here, not
    only the content pass."""

    outcome: RootRegionGraphOutcome
    state: InstanceOf[RootRegionLineageState]
    q_result: InstanceOf[RootRegionCurrentnessResult] | None = None
    f_result: InstanceOf[CurrentGraphResult] | None = None
    e_overlay: InstanceOf[CurrentnessOverlay] | None = None
    resolved_source: InstanceOf[ResolvedRootRegionSource] | None = None
    diagnostics: tuple[RootRegionGraphDiagnostic, ...] = Field(
        default=(), max_length=_HARD_R_DIAGNOSTICS
    )
    contract_version: str = ROOT_REGION_GRAPH_CONTRACT_VERSION
    policy_version: str = ROOT_REGION_GRAPH_POLICY_VERSION
    bounds: RootRegionGraphBounds = Field(default_factory=RootRegionGraphBounds)
    q_bounds: RootRegionCurrentnessBounds = Field(default_factory=RootRegionCurrentnessBounds)
    f_bounds: CurrentGraphBounds = Field(default_factory=CurrentGraphBounds)
    e_bounds: CurrentnessBounds = Field(default_factory=CurrentnessBounds)
    lineage_key: str
    scope_key: str
    revision: int = Field(ge=0, le=MAX_REVISION)
    graph_version: str

    @field_validator("lineage_key", "scope_key")
    @classmethod
    def _v_keys(cls, value: str, info: object) -> str:
        return _check_hex64(value, getattr(info, "field_name", "key") or "key")

    @field_validator("graph_version")
    @classmethod
    def _v_graph_version(cls, value: str) -> str:
        if not _r_graph_version_ok(value):
            raise _fixed("graph_version must be 1..128 non-space UTF-8 encodable characters")
        return value

    @field_validator("diagnostics", mode="before")
    @classmethod
    def _v_diagnostics_preflight(cls, value: object) -> object:
        # The hard ceiling is prefetched BEFORE any nested enum
        # validation, set or sort: an overbound collection is
        # refused without validating or sorting a single element.
        if isinstance(value, (list, tuple)) and len(value) > _HARD_R_DIAGNOSTICS:
            raise _fixed("R diagnostics exceed the hard ceiling")
        return value

    @field_validator("contract_version", "policy_version")
    @classmethod
    def _v_versions(cls, value: str, info: object) -> str:
        expected = (
            ROOT_REGION_GRAPH_CONTRACT_VERSION
            if getattr(info, "field_name", "") == "contract_version"
            else ROOT_REGION_GRAPH_POLICY_VERSION
        )
        if value != expected:
            raise _fixed("the R contract/policy versions are the actual fixed tags")
        return value

    @model_validator(mode="before")
    @classmethod
    def _v_diagnostics_cap_preflight(cls, value: object) -> object:
        # FAILFAST BEFORE any nested bound parsing, diagnostics
        # enum/set/sort visit or cap read: a provided bound that is
        # not an actual closed valid instance of ITS set fails the
        # fixed private validation error first (a missing bound is
        # the honest default; a valid stricter copy is legal), and
        # only then is the ACTUAL stricter R diagnostic cap an O(1)
        # count gate (the hard ceiling alone is insufficient).
        if isinstance(value, dict):
            bounds = value.get("bounds")
            if bounds is not None and not root_region_graph_bounds_shape_ok(bounds):
                raise _fixed("the R bounds must carry actual closed scalar fields")
            q_bounds = value.get("q_bounds")
            if q_bounds is not None and not _r_q_bounds_closed(q_bounds):
                raise _fixed("the Q bounds must carry actual closed scalar fields")
            f_bounds = value.get("f_bounds")
            if f_bounds is not None and not _r_f_bounds_closed(f_bounds):
                raise _fixed("the F bounds must carry actual closed scalar fields")
            e_bounds = value.get("e_bounds")
            if e_bounds is not None and not _r_e_bounds_closed(e_bounds):
                raise _fixed("the E bounds must carry actual closed scalar fields")
            diags = value.get("diagnostics")
            if (
                isinstance(diags, (list, tuple))
                and isinstance(bounds, RootRegionGraphBounds)
                and root_region_graph_bounds_shape_ok(bounds)
                and len(diags) > bounds.max_diagnostics
            ):
                raise _fixed("R diagnostics exceed the actual R bounds")
        return value

    @model_validator(mode="after")
    def _v_result(self) -> RootRegionGraphResult:
        # Closed scalar/class/length fences over EVERY effective
        # bound set BEFORE the scope-key recomputation reads any
        # cap or serializes any field (a deleted actual field on a
        # real class instance fails the fixed typed boundary,
        # never AttributeError or a partial string conversion).
        if not (
            root_region_graph_bounds_shape_ok(self.bounds)
            and _r_q_bounds_closed(self.q_bounds)
            and _r_f_bounds_closed(self.f_bounds)
            and _r_e_bounds_closed(self.e_bounds)
        ):
            raise _fixed("the effective R/Q/F/E bound sets must carry actual closed scalar fields")
        if self.lineage_key != self.state.lineage_key:
            raise _fixed("the result lineage key must equal the actual state key")
        if self.revision != self.state.revision:
            raise _fixed("the result revision must equal the carried state revision")
        if self.scope_key != root_region_graph_scope_key(
            self.lineage_key,
            self.contract_version,
            self.policy_version,
            self.bounds,
            self.q_bounds,
            self.f_bounds,
            self.e_bounds,
            self.graph_version,
        ):
            raise _fixed("scope_key does not match the actual result scope fields")
        if tuple(sorted(set(self.diagnostics))) != self.diagnostics:
            raise _fixed("R diagnostics must be sorted and deduplicated")
        if len(self.diagnostics) > self.bounds.max_diagnostics:
            raise _fixed("R diagnostics exceed the actual R bounds")
        # The resolved source closed law runs BEFORE any parent
        # field access on the record (a partial or foreign record
        # is a fixed typed boundary error, never an attribute
        # error or an echoed unknown variant): the closed O(1)
        # own-field/class/scalar/closed-variant fences, the
        # per-kind provenance class/tag fences, the local provenance
        # / occurrence / proof joins and the bounded content pass
        # over the record's own root text only (the charged
        # derivation reserved the build and content-pass units
        # before this constructor work).
        if self.resolved_source is not None:
            _r_source_closed(self.resolved_source)
        # Nested association fences (identity where original
        # identity is promised; O(1) metadata joins otherwise).
        if self.q_result is not None:
            if not isinstance(self.q_result, RootRegionCurrentnessResult):
                raise _fixed("the Q result must be the actual closed result record")
            if not _r_fields_present(
                self.q_result,
                (
                    "state",
                    "outcome",
                    "lineage_key",
                    "revision",
                    "contract_version",
                    "policy_version",
                    "p_selection",
                    "bounds",
                    "scope_key",
                    "usable_selected_source_digest",
                ),
            ):
                raise _fixed("the Q result must carry its closed identity fields")
            if self.q_result.state is not self.state:
                raise _fixed("the Q result must carry the EXACT input P state by reference")
            if self.q_result.lineage_key != self.lineage_key:
                raise _fixed("the Q result lineage key must equal the carried state key")
            if self.q_result.revision != self.revision:
                raise _fixed("the Q result revision must equal the carried state revision")
            if (
                self.q_result.contract_version != ROOT_REGION_CURRENTNESS_CONTRACT_VERSION
                or self.q_result.policy_version != ROOT_REGION_CURRENTNESS_POLICY_VERSION
            ):
                raise _fixed("the Q result must carry the actual fixed Q version tags")
            if not _r_q_bounds_closed(self.q_result.bounds):
                raise _fixed("the Q result bounds must carry actual closed scalar fields")
            if self.q_result.bounds != self.q_bounds:
                raise _fixed("the Q result bounds must equal the effective Q domain")
            if self.q_result.scope_key != root_region_currentness_scope_key(
                self.lineage_key,
                ROOT_REGION_CURRENTNESS_CONTRACT_VERSION,
                ROOT_REGION_CURRENTNESS_POLICY_VERSION,
                self.q_result.bounds,
            ):
                raise _fixed("the Q result scope key must match its actual Q domain fields")
            # The closed O(1) identity/revision/container fences
            # run on ANY carried non-None P selection BEFORE outcome
            # dispatch (every result outcome, constant work only):
            # a copied selection with a foreign revision or lineage
            # key is a fixed typed boundary error, never accepted
            # into the retained evidence of any R result.
            if self.q_result.p_selection is not None and not _r_p_selection_closed(
                self.q_result.p_selection, self.lineage_key, self.revision
            ):
                raise _fixed(
                    "the carried P selection must carry its actual closed identity, "
                    "revision and bounded witness container"
                )
        if self.f_result is not None:
            if not isinstance(self.f_result, CurrentGraphResult):
                raise _fixed("the F result must be the actual closed result record")
            if not _r_fields_present(self.f_result, ("state", "outcome", "overlay")):
                raise _fixed("the F result must carry its closed identity fields")
            if self.f_result.state is not self.state.d_state:
                raise _fixed("the F result must carry the EXACT wrapped D state by reference")
            if (
                self.f_result.outcome is not CurrentGraphOutcome.OK
                and self.f_result.overlay is not None
            ):
                raise _fixed("a non-ok F result carries no graph overlay")
        f_ok = self.f_result is not None and self.f_result.outcome is CurrentGraphOutcome.OK
        if (self.e_overlay is not None) != f_ok:
            raise _fixed("the same-run E overlay is present exactly when the F result is ok")
        f_graph = self.f_result.overlay if self.f_result is not None else None
        if f_graph is not None:
            if not _r_fields_present(f_graph, _R_F_GRAPH_FIELDS):
                raise _fixed("the F graph must carry its closed identity fields")
            if not (
                _r_f_bounds_closed(f_graph.bounds)
                and _r_e_bounds_closed(f_graph.currentness_bounds)
                and _r_graph_bounds_closed(f_graph.graph_bounds)
            ):
                raise _fixed("the F graph bound sets must carry actual closed scalar fields")
            if (
                f_graph.contract_version != CURRENT_GRAPH_CONTRACT_VERSION
                or f_graph.policy_version != CURRENT_GRAPH_POLICY_VERSION
                or f_graph.currentness_contract_version != CURRENTNESS_CONTRACT_VERSION
                or f_graph.currentness_policy_version != CURRENTNESS_POLICY_VERSION
                or f_graph.currentness_recipe_version != OPAQUE_GROUP_RECIPE_VERSION
            ):
                raise _fixed("the F graph must carry the actual fixed version tags")
            if f_graph.bounds != self.f_bounds:
                raise _fixed("the F graph bounds must equal the effective F domain")
            if f_graph.currentness_bounds != self.e_bounds:
                raise _fixed("the F graph currentness bounds must equal the effective E domain")
            if f_graph.history_key != self.state.d_state.history_key:
                raise _fixed("the F graph history key must equal the carried D key")
            # The actual F graph snapshot association: its revision
            # must equal the EXACT carried D revision (a spliced old
            # graph from another D revision is refused; revision is
            # a snapshot association, never a freshness clock).
            if f_graph.revision != self.state.d_state.revision:
                raise _fixed("the F graph revision must equal the carried D revision")
            if f_graph.currentness_scope_key != currentness_scope_key(
                f_graph.history_key,
                f_graph.workspace,
                f_graph.currentness_policy_version,
                f_graph.currentness_bounds,
            ):
                raise _fixed("the F graph currentness scope key must match its actual fields")
            if f_graph.scope_key != current_graph_scope_key(
                f_graph.history_key,
                f_graph.workspace,
                f_graph.root_digest,
                f_graph.contract_version,
                f_graph.policy_version,
                f_graph.graph_version,
                f_graph.reference_version,
                f_graph.proof_version,
                f_graph.currentness_contract_version,
                f_graph.currentness_policy_version,
                f_graph.currentness_recipe_version,
                f_graph.currentness_scope_key,
                f_graph.bounds,
                f_graph.currentness_bounds,
                f_graph.graph_bounds,
            ):
                raise _fixed("the F graph scope key must match its actual fields")
        if self.e_overlay is not None:
            if not _r_fields_present(self.e_overlay, _R_E_OVERLAY_FIELDS):
                raise _fixed("the E overlay must carry its closed identity fields")
            if self.e_overlay.revision != self.state.d_state.revision:
                raise _fixed("the E overlay revision must equal the carried D revision")
            if self.e_overlay.history_key != self.state.d_state.history_key:
                raise _fixed("the E overlay history key must equal the carried D key")
            if self.e_overlay.policy_version != CURRENTNESS_POLICY_VERSION:
                raise _fixed("the E overlay must carry the actual fixed currentness policy tag")
            if not _r_e_bounds_closed(self.e_overlay.bounds):
                raise _fixed("the E overlay bounds must carry actual closed scalar fields")
            if self.e_overlay.bounds != self.e_bounds:
                raise _fixed("the E overlay bounds must equal the effective E domain")
            if self.e_overlay.scope_key != currentness_scope_key(
                self.e_overlay.history_key,
                self.e_overlay.workspace,
                self.e_overlay.policy_version,
                self.e_overlay.bounds,
            ):
                raise _fixed("the E overlay scope key must match its actual fields")
            if f_graph is not None and self.e_overlay.scope_key != f_graph.currentness_scope_key:
                raise _fixed("the E overlay scope key must match the actual F graph join")
        # Outcome invariants (no partial positive output).
        if self.outcome is RootRegionGraphOutcome.READY:
            if (
                self.q_result is None
                or self.q_result.outcome is not RootRegionCurrentnessOutcome.READY
            ):
                raise _fixed("ready requires the actual same-run Q ready result")
            p_selection = self.q_result.p_selection
            if p_selection is not None and not _r_p_selection_closed(
                p_selection, self.lineage_key, self.revision
            ):
                raise _fixed("the P selection must carry its closed identity fields")
            if (
                p_selection is None
                or p_selection.outcome is not RootSelectionOutcome.OK
                or p_selection.selected_source_digest is None
            ):
                raise _fixed(
                    "ready requires the actual nonNone OK P selection in the same-run Q result"
                )
            if self.q_result.usable_selected_source_digest is None or self.resolved_source is None:
                raise _fixed("ready carries the actual selected source")
            if (
                self.resolved_source.root_digest != self.q_result.usable_selected_source_digest
                or self.resolved_source.root_digest != p_selection.selected_source_digest
            ):
                raise _fixed("the resolved source digest must equal the actual P selected source")
            # The variable association work runs ONLY in this
            # charged READY block, as exactly ONE bounded index
            # walk over the retained root facts plus ONE walk over
            # the selected witnesses (the kernel reserved both
            # widths before the constructor work; never a full
            # P/Q re-derivation or source walk).  Every witness is
            # bound BY IDENTITY to the actual state root facts (a
            # value-equal detached clone is foreign), carries the
            # actual authority flag and the selected digest, and
            # the resolved source fact must be among them.
            root_fact_ids = {id(f) for f in self.state.root_facts}
            selected_fact = self.resolved_source.fact
            selected_found = False
            for witness in p_selection.witness_facts:
                if not (
                    isinstance(witness, RootRegionLineageFact)
                    and _r_fields_present(witness, _R_FACT_WITNESS_FIELDS)
                    and witness.authority is True
                ):
                    raise _fixed(
                        "the P selection witnesses must be actual authoritative root facts"
                    )
                if witness.source_digest != p_selection.selected_source_digest:
                    raise _fixed("the P selection witnesses must carry the selected source digest")
                if id(witness) not in root_fact_ids:
                    raise _fixed("the P selection witnesses must be original retained root facts")
                if witness is selected_fact:
                    selected_found = True
            if id(selected_fact) not in root_fact_ids:
                raise _fixed("the resolved source fact must be an actual retained root fact")
            if not selected_found:
                raise _fixed("the resolved source fact must be an actual selected witness")
            if not f_ok or self.f_result is None or self.f_result.overlay is None:
                raise _fixed("ready requires the actual F graph success")
            if self.f_result.overlay.root_digest != self.resolved_source.root_digest:
                raise _fixed("the F graph must be derived under the actual selected root digest")
            if self.diagnostics:
                raise _fixed("ready carries no refusal diagnostics")
            # The resolved source closed law already ran at the top
            # of this validator BEFORE any parent field access (a
            # model_copy-bypassed tampered record was refused there,
            # not trusted by reference); the original D-state
            # occurrence/proof membership scans remain below.
            # The occurrence and its retained proof are ORIGINAL
            # members of the EXACT input D state (closed bounded
            # identity scan over the occurrence metadata, never a
            # full source walk): a cloned pair with matching IDs /
            # content is a foreign source and is refused.
            if self.resolved_source.occurrence is not None:
                if not any(
                    o is self.resolved_source.occurrence for o in self.state.d_state.occurrences
                ):
                    raise _fixed(
                        "the resolved source occurrence must be an original D-state member"
                    )
            if self.resolved_source.proof is not None:
                if not any(
                    o.proof is self.resolved_source.proof for o in self.state.d_state.occurrences
                ):
                    raise _fixed("the resolved source proof must be an original D-state member")
        elif self.outcome in (
            RootRegionGraphOutcome.ROOT_CURRENTNESS_UNPROVEN,
            RootRegionGraphOutcome.ROOT_AUTHORITY_CONFLICT,
        ):
            expected_q = (
                RootRegionCurrentnessOutcome.ROOT_CURRENTNESS_UNPROVEN
                if self.outcome is RootRegionGraphOutcome.ROOT_CURRENTNESS_UNPROVEN
                else RootRegionCurrentnessOutcome.ROOT_AUTHORITY_CONFLICT
            )
            if self.q_result is None or self.q_result.outcome is not expected_q:
                raise _fixed("the mapped Q outcome carries the actual same-run Q result")
            if (
                self.diagnostics
                or self.f_result is not None
                or self.e_overlay is not None
                or self.resolved_source is not None
            ):
                raise _fixed(
                    "a mapped Q positive interpretation publishes no source, graph or R diagnostics"
                )
        else:  # REFUSED
            if self.resolved_source is not None:
                raise _fixed("a refused result publishes no resolved source")
            if self.q_result is None:
                if not self.diagnostics:
                    raise _fixed("an R refusal before Q carries its own typed diagnostics")
                if self.f_result is not None or self.e_overlay is not None:
                    raise _fixed("an R refusal before Q carries no F evidence")
            elif self.diagnostics == (RootRegionGraphDiagnostic.WORK_UNITS_OVER_BOUND,):
                # An R-total crossing BEFORE R's own result
                # returned: retain whatever actual Q/F evidence was
                # already computed (a mapped Q positive
                # interpretation included) and publish no source.
                pass
            elif (
                self.q_result.outcome is RootRegionCurrentnessOutcome.ROOT_CURRENTNESS_UNPROVEN
            ) or (self.q_result.outcome is RootRegionCurrentnessOutcome.ROOT_AUTHORITY_CONFLICT):
                raise _fixed("a positive-interpretation Q outcome maps to its own R outcome")
            elif self.q_result.outcome is RootRegionCurrentnessOutcome.REFUSED:
                if self.diagnostics or self.f_result is not None or self.e_overlay is not None:
                    raise _fixed("a mapped Q refusal adds no R diagnostics or F evidence")
            else:  # actual Q ready
                if self.f_result is None:
                    if (
                        self.diagnostics != (RootRegionGraphDiagnostic.SOURCE_RESOLUTION_FAILED,)
                        or self.e_overlay is not None
                    ):
                        raise _fixed(
                            "a Q-ready refusal without an F result is the "
                            "selected-source resolution failure"
                        )
                elif self.f_result.outcome is not CurrentGraphOutcome.OK:
                    if self.diagnostics or self.e_overlay is not None:
                        raise _fixed("a mapped F refusal carries no R diagnostics or overlay")
                else:
                    raise _fixed("an F-ok refusal is only reachable through an R-total crossing")
        return self

    def __repr__(self) -> str:  # noqa: D105 - privacy law
        src = self.resolved_source
        if src is None:
            resolved = "resolved_source=None"
        else:
            resolved = (
                "resolved_source=(kind="
                f"{src.kind!r}, root_digest={src.root_digest!r}, "
                f"root_byte_length={src.root_byte_length})"
            )
        q_outcome = self.q_result.outcome.value if self.q_result is not None else None
        f_outcome = self.f_result.outcome.value if self.f_result is not None else None
        return (
            "RootRegionGraphResult(outcome="
            f"{self.outcome.value!r}, lineage_key={self.lineage_key!r}, "
            f"scope_key={self.scope_key!r}, revision={self.revision}, "
            f"{resolved}, q_result_outcome={q_outcome!r}, "
            f"f_result_outcome={f_outcome!r}, "
            f"e_overlay={'yes' if self.e_overlay is not None else 'no'}, "
            f"diagnostics={list(self.diagnostics)})"
        )

    __str__ = __repr__

"""Inert current-root graph/admission composition records (018-i).

Versioned identities:

``CURRENT_ROOT_COMPOSITION_CONTRACT_VERSION =
"cache-current-root-composition/v1"``;
``CURRENT_ROOT_COMPOSITION_POLICY_VERSION =
"current-root-composition-policy/v1"``.

One inert pure derivation over the ACTUAL retained 018-h
root-lineage state and its ACTUAL namespace derives, in ONE bounded
charged operation, the ACTUAL 018-h current-root selection AND the
actual selected root source resolution AND the accepted 018-f
current graph over a freshly recomputed least fixed point with the
selected root as the NEW root supplier AND the current admission
entries with the canonical 018-c semantic keys under the selected
governing root digest.  The records here are inert derivation
outputs: they are not runtime session/cache ownership, they create
no compiler object, and they never activate the legacy profile.
Operational reprs suppress private source/ID values (fixed enums,
counts, placeholders only).
"""

from __future__ import annotations

import hashlib
import json
from enum import StrEnum

from pydantic import BaseModel, Field, InstanceOf, field_validator, model_validator

from .bundle_admission_models import (
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
)
from .causal_history_models import (
    MAX_REVISION,
    HistoryBounds,
    _canonical_history_fields,
)
from .current_admission_models import (
    CurrentAdmissionBounds,
    CurrentAdmissionLimitation,
    CurrentAdmissionPathAssociation,
    CurrentAdmissionWitness,
    _canonical_entry_key,
    _entry_admission_namespace,
)
from .current_graph_models import (
    CURRENT_GRAPH_CONTRACT_VERSION,
    CURRENT_GRAPH_POLICY_VERSION,
    CurrentGraph,
    CurrentGraphBounds,
)
from .currentness_models import (
    CURRENTNESS_CONTRACT_VERSION,
    CURRENTNESS_POLICY_VERSION,
    OPAQUE_GROUP_RECIPE_VERSION,
    CurrentnessBounds,
)
from .graph_models import GraphBounds, _check_rel_path, _fixed, _GraphFrozen
from .observation_models import ObservationBounds
from .root_lineage_models import (
    ROOT_LINEAGE_CONTRACT_VERSION,
    ROOT_LINEAGE_POLICY_VERSION,
    EnvelopeRootProvenance,
    ReadRootProvenance,
    RootLineageBounds,
    RootLineageState,
    RootSelectionResult,
)

CURRENT_ROOT_COMPOSITION_CONTRACT_VERSION = "cache-current-root-composition/v1"
CURRENT_ROOT_COMPOSITION_POLICY_VERSION = "current-root-composition-policy/v1"

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


def _utf8_byte_length_capped(text: str, cap: int) -> int:
    """The no-copy UTF-8 byte length with an EARLY EXIT at ``cap``.

    Returns ``cap + 1`` once the running total crosses the cap, so
    an over-bound source refuses without scanning the whole region
    and without any owned encode allocation.  An isolated surrogate
    (unencodable in UTF-8) is a fixed refusal, never an uncaught
    ``UnicodeEncodeError`` (the accepted F domain law)."""
    total = 0
    for code in map(ord, text):
        if 0xD800 <= code <= 0xDFFF:
            raise _fixed("retained root source is not valid UTF-8")
        if code < 0x80:
            total += 1
        elif code < 0x800:
            total += 2
        elif code < 0x10000:
            total += 3
        else:
            total += 4
        if total > cap:
            return cap + 1
    return total


def _closed_bounds_fence(bound: BaseModel, field: str) -> None:
    """The CLOSED int-field shape fence before ANY bound dump.

    Typed model construction does not prove the field shape after a
    model_copy bypass (the accepted H law), so EVERY field is
    rechecked against its declared closed range (non-bool integral,
    within the Ge..Le metadata) BEFORE any serialization can walk
    the field set.  The fence is a closed per-model field walk: no
    attribute discovery beyond the declared fields, no recursion,
    no caller-controlled input.
    """
    model_cls = type(bound)
    for name, model_field in model_cls.model_fields.items():
        actual = getattr(bound, name)
        if not isinstance(actual, int) or isinstance(actual, bool):
            raise _fixed(f"{field}.{name} must be an integral bound")
        low = None
        high = None
        for meta in model_field.metadata:
            meta_name = type(meta).__name__
            if meta_name == "Ge":
                low = meta.ge
            elif meta_name == "Le":
                high = meta.le
        if low is not None and actual < low:
            raise _fixed(f"{field}.{name} is below the closed bound range")
        if high is not None and actual > high:
            raise _fixed(f"{field}.{name} is above the closed bound range")


_KEY_RECORD_BOUND_FIELDS: tuple[tuple[str, type[BaseModel]], ...] = (
    ("admission_bounds", BundleAdmissionBounds),
    ("proof_bounds", BundleProofBounds),
    ("graph_bounds", GraphBounds),
    ("observation_bounds", ObservationBounds),
)
#: The closed fence walk cost per key record: the four isinstance
#: class checks plus two units per declared field of the four
#: carried bound models (the metadata loop and both range
#: comparisons per field).  The kernel reserves exactly this before
#: every model path that can reach the walk (I8).
KEY_RECORD_FENCE_UNITS = 4 + 2 * sum(len(m.model_fields) for _, m in _KEY_RECORD_BOUND_FIELDS)


def _fence_key_record_bounds(key_record: BundleKeyRecord, field: str) -> None:
    """The CLOSED type+scalar fence on a key record's carried bound
    models BEFORE any accepted helper may serialize them (I8).

    The accepted namespace-reconstruction helpers
    (``_entry_admission_namespace`` / ``_canonical_entry_key`` /
    ``_canonical_history_fields``) dump those bound models while
    rebuilding their context (the four ``model_dump`` passes of the
    canonical namespace recipe).  Typed model construction does not
    prove the field shape after a model_copy bypass, so every bound
    must be the ACTUAL expected model with closed scalar fields
    BEFORE the first dump can walk an unexpected container.  A
    fixed private refusal: no serializer traversal, no raw value
    echo, and the closed field walk only touches declared fields.
    """
    for name, model_cls in _KEY_RECORD_BOUND_FIELDS:
        actual = getattr(key_record, name)
        if not isinstance(actual, model_cls):
            raise _fixed(f"{field}.{name} must be the actual bound model")
        _closed_bounds_fence(actual, f"{field}.{name}")


#: The fixed part of the L01 closed entry / key-record metadata
#: fence: the entry scalar / enum / container checks, the key-record
#: scalar / enum / digest / identity / version checks, the per-group
#: closed shape law, the entry / record class / vector / width joins
#: and the ownership partition fixed cost (the O(n) tuple walks are
#: charged separately against the ACTUAL tuple lengths in
#: ``canonical_rekey_units``).  The kernel reserves exactly this
#: (plus the bound-model fence) before every entry model path that
#: can reach the walk.
ENTRY_METADATA_FENCE_UNITS = 48

#: The root entry's key record has exactly ONE occurrence, ONE
#: class and ONE ownership index, so the M01 fence walk term
#: (``5 * (mo + mc + total_indices) + 2 * len(groups)``) is the
#: fixed 17 for it (the root occurrence path is the fixed
#: ``ROOT_FILENAME`` constant, never a walked member path).
ROOT_ENTRY_FENCE_WALK_UNITS = 17

#: The closed ceiling of ``HistoryBounds.max_occurrences`` (the
#: actual retained-occurrence domain).  The leaf entry boundary
#: has no admission to read the ACTUAL inherited cap from, so its
#: witness count gate uses the closed declared ceiling; the parent
#: boundaries always pass the actual inherited cap (M01).
HISTORY_MAX_OCCURRENCES_CEILING = 4096


def _json_metadata_byte_ceiling(value: object) -> int:
    """A closed upper bound on the UTF-8 byte length of the exact
    ``json.dumps(value, sort_keys=True, separators=(",", ":"))``
    serialization of METADATA-only values (str / int / bool / None /
    list / tuple / dict of those) under the DEFAULT ``ensure_ascii``
    recipe.  Strings bound that recipe per character: a plain ASCII
    character one byte, a quote or backslash two (the two-character
    escape), a control or BMP non-ASCII character six (the
    ``\\uXXXX`` escape) and a non-BMP code point twelve (the
    surrogate pair) -- a conservative closed character-count bound
    that honestly bounds the ACTUAL serialization work of every
    legal text, without changing the canonical recipe or
    prohibiting legal Unicode (M02).  Ints bound their digit length
    (a value never exceeds its declared ``le``); booleans bound
    ``true``/``false`` and ``None`` bounds ``null``; each list /
    dict element carries one separator byte and each container its
    two brackets / braces.  A JSON field count is never substituted
    for serialized byte length (L01)."""
    if value is None:
        return 4
    if isinstance(value, bool):
        return 5
    if isinstance(value, int):
        return len(str(abs(value))) + 1
    if isinstance(value, str):
        total = 2
        for code in map(ord, value):
            if code < 0x20 or code >= 0x7F:
                total += 6 if code < 0x10000 else 12
            elif code in (0x22, 0x5C):  # the quote or backslash escape
                total += 2
            else:
                total += 1
        return total
    if isinstance(value, (list, tuple)):
        return 2 + sum(_json_metadata_byte_ceiling(item) + 1 for item in value)
    if isinstance(value, dict):
        return 2 + sum(
            _json_metadata_byte_ceiling(key) + _json_metadata_byte_ceiling(item) + 3
            for key, item in value.items()
        )
    raise TypeError("the closed byte ceiling covers metadata values only")


def _bound_dump_byte_ceiling(model_cls: type[BaseModel]) -> int:
    """The closed JSON byte ceiling of ONE ``model_dump(mode="json")``
    serialization of ``model_cls``: every int field at its declared
    ``le`` (the maximum value carries the maximum digit count) under
    the exact field names, computed once at import time (L01)."""
    ceiling: dict[str, object] = {}
    for name, field_info in model_cls.model_fields.items():
        high = None
        for meta in field_info.metadata:
            candidate = getattr(meta, "le", None)
            if candidate is not None:
                high = candidate
        ceiling[name] = high if high is not None else 0
    return _json_metadata_byte_ceiling(ceiling)


#: ONE dump pass of each carried bound model at its declared
#: ceilings (closed JSON byte lengths, not field counts).
_BOUND_DUMP_CEILINGS: dict[type[BaseModel], int] = {
    model_cls: _bound_dump_byte_ceiling(model_cls) for _, model_cls in _KEY_RECORD_BOUND_FIELDS
}
#: ONE dump pass over the four carried bound models (closed bytes).
BOUND_DUMP_UNITS = sum(_BOUND_DUMP_CEILINGS.values())
#: The exact ``_key_canonical`` canonical dict key names (the
#: accepted 018-c recipe fields; the name bytes are part of the
#: serialized payload and are charged as such).
_KEY_CANONICAL_NAMES: tuple[str, ...] = (
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
)


#: The longest declared member-class enum value (the closed
#: per-value ceiling walk bound for the class vector).
_MEMBER_CLASS_VALUE_CHARS = max(len(member.value) for member in MemberClass)

#: The exact ``_json_metadata_byte_ceiling("x" * n)`` probe-call
#: inventory inside ``canonical_rekey_units`` (the namespace
#: payload: 4 of 256, 2 of 64, 5 of 128, 1 of 16; the key payload:
#: 5 of 128, 2 of 16, 4 of 256, 4 of 64).  Each probe call allocates
#: the n-character string and walks it: the closed work bound per
#: call is 2 (the call and its result) plus 2n (the allocation walk
#: and the per-character ceiling walk).  Computed once at import
#: time (M02).
_S_CALL_INVENTORY: tuple[tuple[int, int], ...] = (
    (4, 256),
    (2, 64),
    (5, 128),
    (1, 16),
    (5, 128),
    (2, 16),
    (4, 256),
    (4, 64),
)
_S_ASCII_WORK_CONSTANT = sum(count * (2 + 2 * length) for count, length in _S_CALL_INVENTORY)

#: The closed ceiling of the ACTUAL trusted-workspace domain (the
#: namespace 1..1024 absolute-path law) for the reserved workspace
#: encode walk plus its byte allocation (M02).
_WORKSPACE_ENCODE_CEILING = 4 * 1024


def entry_fence_walk_units(entry: CurrentRootCompositionEntry) -> int:
    """A closed O(1) bound on the M01 per-entry bounded element
    walks (the charged fence work on the I outer): 5 per member
    occurrence / class / ownership index (the scalar, range,
    distinct, increasing and partition checks per element), the
    per-path no-copy byte-cap early-exit walk per member path of a
    FILE entry (the root occurrence path is the fixed
    ``ROOT_FILENAME`` constant, never walked against the cap), 3 per
    admitted segment, 6 per witness, 4 per witness segment index
    and 2 per ownership group.  No element is visited: every length
    is an O(1) tuple read (M01/M02).  The phase-one O(1) checks are
    the separate fixed ``ENTRY_METADATA_FENCE_UNITS``."""
    kr = entry.key_record
    mo = len(kr.member_occurrences)
    mc = len(kr.member_classes)
    total_indices = sum(len(group.member_occurrence_indices) for group in kr.ownership_groups)
    path_walk = 0
    if entry.entry_class is not EntryClass.ROOT_ENTRY:
        path_cap = min(kr.graph_bounds.max_path_bytes, kr.observation_bounds.max_path_bytes)
        path_walk = mo * (path_cap + 1)
    return (
        5 * (mo + mc + total_indices)
        + path_walk
        + 3 * len(entry.admitted_segments)
        + 6 * len(entry.witnesses)
        + 4 * sum(len(witness.segment_indices) for witness in entry.witnesses)
        + 2 * len(kr.ownership_groups)
    )


def canonical_rekey_calc_units(
    key_record: BundleKeyRecord, entry: CurrentRootCompositionEntry
) -> int:
    """A closed WALK-FREE upper bound on the ACTUAL calculation
    work performed by ``canonical_rekey_units`` for ONE entry (the
    M02 reservation precharge): the fixed statement / dict /
    arithmetic work, the closed probe-string allocations and
    per-character ceiling walks, the reserved workspace encode walk
    plus byte allocation, the per-member-path ceiling walks (each
    path bounded in characters by the ACTUAL two-inherited path
    ceiling -- UTF-8 bytes are never fewer than characters), the
    per-member-class value ceiling walks, the per-index and
    per-group digit, name and digest ceiling walks and the
    per-element iteration / append / length work across every loop
    the reservation performs.  No element is visited: every length
    is an O(1) tuple read and every serialized dimension is bounded
    at its ACTUAL inherited ceiling or at the declared field
    ceiling, never at a field count.  The kernel charges the sum
    over the retained entries BEFORE the reservation calculation
    may encode, allocate or walk (M02)."""
    kr = key_record
    mo = len(kr.member_occurrences)
    mc = len(kr.member_classes)
    group_count = len(kr.ownership_groups)
    total_indices = sum(len(group.member_occurrence_indices) for group in kr.ownership_groups)
    segment_count = len(entry.admitted_segments)
    witness_count = len(entry.witnesses)
    witness_segment_count = sum(len(witness.segment_indices) for witness in entry.witnesses)
    path_cap = min(kr.graph_bounds.max_path_bytes, kr.observation_bounds.max_path_bytes)
    return (
        96  # the fixed statement / dict / arithmetic work
        + _S_ASCII_WORK_CONSTANT  # the closed probe allocation / ceiling walks
        + _WORKSPACE_ENCODE_CEILING  # the workspace encode walk + byte allocation
        + 5 * mo * (path_cap + 1)  # the member-path ceiling walks
        + 4 * mc * _MEMBER_CLASS_VALUE_CHARS  # the member-class value ceiling walks
        + 12 * total_indices  # the per-index digit / name / escape walks
        + 8 * group_count * 64  # the per-group name / boundary / digest walks
        + 6
        * (
            mo
            + mc
            + group_count
            + total_indices
            + segment_count
            + witness_count
            + witness_segment_count
        )  # the per-element iteration / append / length work
    )


def canonical_rekey_units(key_record: BundleKeyRecord, entry: CurrentRootCompositionEntry) -> int:
    """A closed upper bound on the M01 per-entry ACTUAL metadata
    fence plus the K01 per-entry ACTUAL canonical re-derivation
    performed by ``_check_selected_root_binding``.

    The accepted recipe performs exactly: the L01 closed entry /
    key-record / ownership metadata fence (fixed scalar / enum /
    container checks plus the O(n) tuple walks, the distinct-path
    set build and the ownership partition), the two retained
    digest comparisons, the entry / record metadata joins, the
    content-key agreement comparison and then
    ``_canonical_entry_key``, which the accepted helpers execute
    as THREE 4-bound-model dump passes (the two
    ``_canonical_namespace_fields`` builds -- the first in
    ``_entry_admission_namespace`` and the second in the namespace
    model's own bound-integrity re-derivation -- plus the one
    ``_key_canonical`` build), two namespace payload builds, one
    key payload build and FIVE sha256 passes (two over the
    namespace payload, two over the scoped-key payload and one
    over the canonical payload).  Every serialized term is bounded
    at the ACTUAL record length where the length belongs to the
    record (workspace, member occurrence paths, member-class
    values, ownership-group fields) and at the declared field
    ceilings where it does not (identity strings, version tags,
    bound-model ints at their ``le`` values): a field count is
    never a serialized length.  The kernel may therefore charge
    the sum once per planned entry BEFORE the construction that
    performs it: a crossing is refused before the re-derivation
    may serialize or hash, never after a partial pass.
    """
    occurrences = key_record.member_occurrences
    classes = key_record.member_classes
    groups = key_record.ownership_groups

    def s(n: int) -> int:
        # One JSON string element under a declared n-char ceiling.
        return _json_metadata_byte_ceiling("x" * n)

    bound_strings = sum(
        _BOUND_DUMP_CEILINGS[model_cls] + 2 for _, model_cls in _KEY_RECORD_BOUND_FIELDS
    )
    # One ``_canonical_namespace_fields`` payload: the eleven
    # identity / version strings under their declared ceilings plus
    # the short mode value, then the four bound-model JSON dumps as
    # string elements.
    namespace_payload = 2 + (4 * s(256) + 2 * s(64) + 5 * s(128) + s(16) + bound_strings) + 15
    workspace_bytes = len(key_record.workspace.encode("utf-8"))
    # The scoped-key input: the 64-hex namespace key, NUL and the
    # ACTUAL workspace UTF-8 bytes.
    scoped_input = 64 + 1 + workspace_bytes
    one_build = sum(_BOUND_DUMP_CEILINGS.values()) + namespace_payload
    # ``_entry_admission_namespace``: TWO builds, FOUR sha256
    # passes (two over the namespace payload, two over the scoped
    # key), the one workspace encode walk and the namespace model
    # construction.
    namespace_rebuild = (
        2 * one_build
        + 2 * (namespace_payload + 64)
        + 2 * (scoped_input + 64)
        + 1
        + workspace_bytes
        + 40
    )
    # ``_key_canonical``: the four bound dumps, the canonical dict
    # at the ACTUAL member / class / group / workspace lengths and
    # the outer JSON encode.
    member_list = 2 + sum(_json_metadata_byte_ceiling(p) + 1 for p in occurrences)
    class_list = 2 + sum(_json_metadata_byte_ceiling(c.value) + 1 for c in classes)
    group_items: list[int] = []
    for group in groups:
        index_list = 2 + sum(len(str(index)) + 2 for index in group.member_occurrence_indices)
        group_items.append(
            2
            + len("member_occurrence_indices")
            + 3
            + index_list
            + len("boundary_class")
            + 3
            + _json_metadata_byte_ceiling(group.boundary_class.value)
            + len("group_digest")
            + 3
            + (_json_metadata_byte_ceiling(group.group_digest) if group.group_digest else 4)
            + 2
        )
    group_list = 2 + sum(group_items) + (len(group_items) - 1)
    key_names = 2 + sum(len(n) + 3 for n in _KEY_CANONICAL_NAMES) + (len(_KEY_CANONICAL_NAMES) - 1)
    key_payload = (
        key_names
        + 5 * s(128)
        + 2 * s(16)
        + 4 * s(256)
        + s(64)
        + s(64)
        + _json_metadata_byte_ceiling(key_record.workspace)
        + 2 * s(64)
        + bound_strings
        + member_list
        + class_list
        + group_list
    )
    key_build = sum(_BOUND_DUMP_CEILINGS.values()) + key_payload
    # The M01 closed metadata fence: the fixed phase-one checks
    # plus the bounded phase-two element walks at the ACTUAL
    # tuple lengths (``entry_fence_walk_units``).
    fence_walks = ENTRY_METADATA_FENCE_UNITS + entry_fence_walk_units(entry)
    return (
        KEY_RECORD_FENCE_UNITS  # the closed bound-model fence pass
        + fence_walks  # the L01 closed metadata fence
        + 3  # the two digest + the one content-key comparisons
        + namespace_rebuild  # _entry_admission_namespace
        + key_build  # _key_canonical
        + key_payload
        + 64  # the final canonical sha256
    )


def row_shape_units(keys: tuple[str, ...]) -> int:
    """A closed upper bound on the K02 per-row row-shape fence:
    the tuple/scalar closedness check, the non-emptiness check,
    the distinctness set build and the canonical sorted-order
    check (a list copy plus Timsort, upper-bounded by
    n log2(n) + n comparisons)."""
    n = len(keys)
    return 2 + 5 * n + n * n.bit_length()


def _fence_entry_metadata(
    entry: CurrentRootCompositionEntry,
    field: str,
    history_occurrence_cap: int | None = None,
) -> None:
    """The M01 CLOSED actual-field metadata fence for one retained
    entry and its nested key record, BEFORE any accepted helper may
    serialize, hash or walk it.

    Typed model construction does not prove the field shape after a
    model_copy bypass, and the accepted canonical recipe dereferences
    ``mode.value`` / ``member_classes`` / group fields directly: an
    unchecked raw string there is an uncaught ``AttributeError``,
    never a validation refusal.  The fence is closed in three
    phases (M01): FIRST the expected models, the container kinds and
    the O(1) lengths under the ACTUAL inherited caps and alignment,
    BEFORE any element is visited by any iteration, copy, set, sort,
    hash or serialization; THEN the bounded scalar / path / index /
    enum validation of every element dimension (every dimension is
    pre-bounded by phase one, so no operation assumes hashability,
    order or valid UTF-8 before its elements are checked); and ONLY
    THEN the exact entry / record / proof authority, member, width
    and ownership joins, including the accepted C dense group
    ordering and UNIQUE partition membership (a set union alone does
    not prove a partition), the closed branch shape and the source /
    provenance identity.  A forged container or an overcount refuses
    with ONE fixed private error before its elements are touched: no
    serialization traversal, no raw value echo, no invented larger
    cap and no coercion masquerading as an actual enum (the classes
    are StrEnums -- equality alone would accept a raw string).
    The witness count gate uses the ACTUAL inherited
    ``history_bounds.max_occurrences`` at the parent boundaries and
    the closed declared ceiling at the leaf (M01).  Charged bounded
    METADATA work only (reserved by ``ENTRY_METADATA_FENCE_UNITS``
    plus the O(n) terms of ``canonical_rekey_units`` on the I
    outer); no source rewalk.
    """
    # --- Phase 1: expected models, container kinds and O(1) lengths
    # --- under the ACTUAL inherited caps, BEFORE any element visit -
    if not isinstance(entry.entry_class, EntryClass):
        raise _fixed(f"{field}.entry_class must be the actual entry class")
    kr = entry.key_record
    if not isinstance(kr, BundleKeyRecord):
        raise _fixed(f"{field}.key_record must be the actual key record")
    if not isinstance(kr.mode, AdmissionMode):
        raise _fixed(f"{field}.key_record.mode must be the actual admission mode")
    if not isinstance(kr.authority_class, EntryClass):
        raise _fixed(f"{field}.key_record.authority_class must be the actual entry class")
    for name in (
        "admission_version",
        "graph_version",
        "reference_version",
        "proof_version",
        "observation_version",
    ):
        value = getattr(kr, name)
        if not isinstance(value, str) or not 1 <= len(value) <= 128:
            raise _fixed(f"{field}.key_record.{name} must be an actual version tag")
    for name in ("principal", "session", "repository", "model_identity"):
        value = getattr(kr, name)
        if not isinstance(value, str) or not 1 <= len(value) <= 256:
            raise _fixed(f"{field}.key_record.{name} must be an actual identity text")
    route = kr.route
    if not isinstance(route, str) or not 1 <= len(route) <= 64:
        raise _fixed(f"{field}.key_record.route must be an actual route text")
    workspace = kr.workspace
    if not isinstance(workspace, str) or not workspace:
        raise _fixed(f"{field}.key_record.workspace must be an actual nonempty path")
    for name in ("config_fingerprint", "root_digest", "aggregate_source_digest"):
        value = getattr(kr, name)
        if not isinstance(value, str) or len(value) != 64:
            raise _fixed(f"{field}.key_record.{name} must be an actual 64-hex digest")
    # The four carried bound models (closed scalar fence) BEFORE
    # any cap below can be read from them.
    _fence_key_record_bounds(kr, f"{field}.key_record")
    occurrence_cap = history_occurrence_cap
    if occurrence_cap is None:
        occurrence_cap = HISTORY_MAX_OCCURRENCES_CEILING
    if (
        not isinstance(occurrence_cap, int)
        or isinstance(occurrence_cap, bool)
        or not 1 <= occurrence_cap <= HISTORY_MAX_OCCURRENCES_CEILING
    ):
        raise _fixed(f"{field}.key_record.history cap must be an actual retained cap")
    max_member_occurrences = kr.admission_bounds.max_member_occurrences
    max_segments = kr.proof_bounds.max_segments
    max_requests = kr.graph_bounds.max_requests
    max_items = kr.observation_bounds.max_items
    path_cap = min(kr.graph_bounds.max_path_bytes, kr.observation_bounds.max_path_bytes)
    if len(workspace) > 1024:
        raise _fixed(f"{field}.key_record.workspace exceeds the actual trusted workspace cap")
    occurrences = kr.member_occurrences
    if not isinstance(occurrences, tuple):
        raise _fixed(f"{field}.key_record.member_occurrences must be a tuple")
    if not occurrences:
        raise _fixed(f"{field}.key_record.member_occurrences must not be empty")
    if len(occurrences) > max_member_occurrences:
        raise _fixed(f"{field}.key_record.member_occurrences exceed the actual admission cap")
    record_classes = kr.member_classes
    if not isinstance(record_classes, tuple):
        raise _fixed(f"{field}.key_record.member_classes must be a tuple")
    if len(record_classes) != len(occurrences):
        raise _fixed(f"{field}.key_record.member_classes must align with the occurrences")
    groups = kr.ownership_groups
    if not isinstance(groups, tuple) or not groups:
        raise _fixed(f"{field}.key_record.ownership_groups must be a nonempty tuple")
    if len(groups) > len(occurrences):
        raise _fixed(f"{field}.key_record.ownership_groups cannot exceed the occurrences")
    member_classes = entry.member_classes
    if not isinstance(member_classes, tuple):
        raise _fixed(f"{field}.member_classes must be a tuple")
    if not member_classes:
        raise _fixed(f"{field}.member_classes must not be empty")
    if len(member_classes) > max_member_occurrences:
        raise _fixed(f"{field}.member_classes exceed the actual admission cap")
    if len(member_classes) != len(occurrences):
        raise _fixed(f"{field}.member_classes must align with the occurrences")
    width = entry.width
    if not isinstance(width, int) or isinstance(width, bool) or width < 1:
        raise _fixed(f"{field}.width must be an actual positive integer")
    segments = entry.admitted_segments
    if not isinstance(segments, tuple):
        raise _fixed(f"{field}.admitted_segments must be a tuple")
    segment_domain = 0
    if entry.entry_class is EntryClass.ROOT_ENTRY:
        if segments:
            raise _fixed(f"{field}.a root entry admits the root, not proof segments")
        if entry.proof is not None:
            raise _fixed(f"{field}.a root entry never embeds a file-tool proof")
    else:
        proof = entry.proof
        if not isinstance(proof, BundleProof):
            raise _fixed(f"{field}.proof must be the actual retained proof")
        proof_segments = proof.segments
        if not isinstance(proof_segments, tuple) or not proof_segments:
            raise _fixed(f"{field}.proof segments must be a nonempty tuple")
        if len(proof_segments) > max_segments:
            raise _fixed(f"{field}.proof segments exceed the actual proof cap")
        segment_domain = len(proof_segments)
        if len(segments) > segment_domain:
            raise _fixed(f"{field}.admitted_segments cannot exceed the proof segments")
    witnesses = entry.witnesses
    if not isinstance(witnesses, tuple):
        raise _fixed(f"{field}.witnesses must be a tuple")
    if len(witnesses) > occurrence_cap * max(1, max_segments, max_member_occurrences):
        raise _fixed(f"{field}.witnesses exceed the actual retained coordinate domain")
    if entry.root_text is not None and not isinstance(entry.root_text, str):
        raise _fixed(f"{field}.root_text must be str or None")
    length = entry.root_source_byte_length
    if length is not None and (
        not isinstance(length, int) or isinstance(length, bool) or length < 0
    ):
        raise _fixed(f"{field}.root_source_byte_length must be an actual nonnegative integer")
    if entry.root_provenance is not None and not isinstance(
        entry.root_provenance, (EnvelopeRootProvenance, ReadRootProvenance)
    ):
        raise _fixed(f"{field}.root_provenance must be an actual retained provenance")
    if not isinstance(entry.content_key, str) or len(entry.content_key) != 64:
        raise _fixed(f"{field}.content_key must be an actual 64-hex digest")
    if not isinstance(entry.root_digest, str) or len(entry.root_digest) != 64:
        raise _fixed(f"{field}.root_digest must be an actual 64-hex digest")
    # --- Phase 2: the bounded element walks (every dimension is
    # --- pre-bounded by phase one) ----------------------------------
    for path in occurrences:
        if not isinstance(path, str) or not path:
            raise _fixed(f"{field}.key_record.member_occurrences must hold actual paths")
        if entry.entry_class is not EntryClass.ROOT_ENTRY:
            # The ACTUAL member-path domain: the two inherited path
            # ceilings in UTF-8 bytes.  The O(1) char gate precedes
            # the no-copy early-exit byte walk (M01).
            if len(path) > path_cap:
                raise _fixed(f"{field}.key_record.member paths exceed the actual path cap")
            if _utf8_byte_length_capped(path, path_cap) > path_cap:
                raise _fixed(f"{field}.key_record.member paths exceed the actual path cap")
    for value in record_classes:
        if not isinstance(value, MemberClass):
            raise _fixed(f"{field}.key_record.member_classes must hold actual member classes")
    for value in member_classes:
        if not isinstance(value, MemberClass):
            raise _fixed(f"{field}.member_classes must hold actual member classes")
    previous = -1
    for index in segments:
        if not isinstance(index, int) or isinstance(index, bool) or index < 0:
            raise _fixed(f"{field}.admitted_segments must hold actual nonnegative integers")
        if index >= segment_domain or index <= previous:
            raise _fixed(f"{field}.admitted segment indices must be distinct and increasing")
        previous = index
    for witness in witnesses:
        if not isinstance(witness, CurrentAdmissionWitness):
            raise _fixed(f"{field}.witnesses must hold actual witnesses")
        if not isinstance(witness.occurrence_id, str) or len(witness.occurrence_id) != 64:
            raise _fixed(f"{field}.witness occurrence id must be an actual 64-hex digest")
        if (
            not isinstance(witness.request_index, int)
            or isinstance(witness.request_index, bool)
            or not 0 <= witness.request_index < max_requests
        ):
            raise _fixed(f"{field}.witness request index must index the actual request batch")
        if (
            not isinstance(witness.call_position, int)
            or isinstance(witness.call_position, bool)
            or not 0 <= witness.call_position < max_items
        ):
            raise _fixed(f"{field}.witness call position must index the actual observation items")
        if (
            not isinstance(witness.result_position, int)
            or isinstance(witness.result_position, bool)
            or not 0 <= witness.result_position < max_items
        ):
            raise _fixed(f"{field}.witness result position must index the actual observation items")
        wsi = witness.segment_indices
        if not isinstance(wsi, tuple) or not wsi:
            raise _fixed(f"{field}.witness segment indices must be a nonempty tuple")
        if len(wsi) > max_segments:
            raise _fixed(f"{field}.witness segment indices exceed the actual proof cap")
        previous = -1
        for index in wsi:
            if not isinstance(index, int) or isinstance(index, bool) or index < 0:
                raise _fixed(
                    f"{field}.witness segment indices must hold actual nonnegative integers"
                )
            if index >= max_segments or index <= previous:
                raise _fixed(f"{field}.witness segment indices must index the proof segments")
            previous = index
    covered: set[int] = set()
    for position, group in enumerate(groups):
        if not isinstance(group, OwnershipGroup):
            raise _fixed(f"{field}.key_record.ownership_groups must hold actual groups")
        if (
            not isinstance(group.group_index, int)
            or isinstance(group.group_index, bool)
            or group.group_index != position
        ):
            raise _fixed(f"{field}.key_record.group indices must be dense and ordered")
        indices = group.member_occurrence_indices
        if not isinstance(indices, tuple) or not indices:
            raise _fixed(f"{field}.key_record.group indices must be a nonempty tuple")
        if len(indices) > len(occurrences):
            raise _fixed(f"{field}.key_record.group indices cannot exceed the occurrences")
        for index in indices:
            if (
                not isinstance(index, int)
                or isinstance(index, bool)
                or not 0 <= index < len(occurrences)
            ):
                raise _fixed(f"{field}.key_record.group indices must index the occurrences")
        if len(set(indices)) != len(indices):
            raise _fixed(f"{field}.key_record.group indices must be distinct")
        if indices != tuple(sorted(indices)):
            raise _fixed(f"{field}.key_record.group indices must be increasing")
        for index in indices:
            if index in covered:
                raise _fixed(f"{field}.key_record.group partition membership is never repeated")
            covered.add(index)
        if not isinstance(group.boundary_class, BoundaryClass):
            raise _fixed(f"{field}.key_record.group boundary must be the actual boundary class")
        if group.group_digest is not None and (
            not isinstance(group.group_digest, str) or len(group.group_digest) != 64
        ):
            raise _fixed(f"{field}.key_record.group digest must be 64-hex or None")
        if group.boundary_class is BoundaryClass.PROVEN and group.group_digest is None:
            raise _fixed(f"{field}.key_record.a proven group requires its exact digest")
        if group.boundary_class is BoundaryClass.BOUNDARYLESS and len(indices) == 1:
            raise _fixed(f"{field}.key_record.a boundaryless group is never a singleton")
    if covered != set(range(len(occurrences))):
        raise _fixed(f"{field}.key_record.groups must partition the occurrences exactly")
    # --- Phase 3: the closed branch shape (metadata only, no
    # --- source walk; the root segments / proof checks already ran
    # --- as O(1) phase-one gates) -----------------------------------
    if entry.entry_class is EntryClass.ROOT_ENTRY:
        if entry.root_text is None or entry.root_provenance is None:
            raise _fixed(f"{field}.a root entry carries its retained root bytes and provenance")
        if witnesses:
            raise _fixed(f"{field}.a root entry is evidenced, never a fabricated read witness")
        if occurrences != (ROOT_FILENAME,):
            raise _fixed(f"{field}.a root entry is one occurrence at the normalized root")
        if tuple(member_classes) != (MemberClass.ELIGIBLE,):
            raise _fixed(f"{field}.the root is one always-eligible root-occurrence member")
        if kr.aggregate_source_digest != entry.root_digest:
            raise _fixed(f"{field}.the root aggregate digest equals the root digest")
    else:
        if entry.root_text is not None:
            raise _fixed(f"{field}.retained root bytes belong to the root entry only")
        if length is not None:
            raise _fixed(f"{field}.retained root byte length belongs to the root entry only")
        if entry.root_provenance is not None:
            raise _fixed(f"{field}.retained root provenance belongs to the root entry only")
        if not witnesses:
            raise _fixed(f"{field}.a file entry retains its original proof witnesses")


def _check_selected_root_binding(admission: CurrentRootCompositionAdmission) -> None:
    """J01/K01/L01/M01: EVERY retained entry (root entry and file
    entries) must bind the SELECTED governing root digest of the
    admission it lives in, and its ACTUAL canonical key must
    RE-DERIVE from its ACTUAL key record.

    A genuine earlier admission entry for the SAME nonroot source
    under a CHANGED governing root is self-consistent (its key
    record, its canonical key and its namespace all re-derive) but
    carries the OLD governing digest: equal source bytes/provenance
    never make the historical key valid in the new admission.
    Rebounding BOTH the entry's and the key record's digest fields
    while RETAINING the old canonical key is refused by the
    re-derivation (K01): the accepted C recipe is applied to the
    ACTUAL nested key record fields and must reproduce the entry
    key, which must also equal the key record's own content key --
    comparing tags/digests or entry==record key alone is never the
    law.  L01/M01 completes the parent boundary: BEFORE the recipe
    may serialize or hash anything, the TEN carried admission bound
    models are fenced as closed typed scalar models (M01) so no
    cap below is read from a forged bound, then the M01 closed
    metadata fence closes the ACTUAL entry / key-record /
    ownership field shapes (expected models, container kinds and
    O(1) lengths under the ACTUAL inherited caps and alignment
    BEFORE any element visit, the bounded scalar / path / index /
    enum validation, the accepted C dense group ordering and
    unique partition law, and the closed branch shape) with the
    ACTUAL inherited history occurrence cap on the witness count
    gate -- a model_copy-forged raw string or forged container
    yields ONE fixed private refusal, never an uncaught
    AttributeError/TypeError from the recipe's enum dereference or
    a set build over unhashable elements -- and the bounded entry /
    record metadata joins (entry class, authority vector, width
    against the distinct record paths) run BEFORE the
    re-derivation.  Charged METADATA work only (one closed fence +
    re-derivation pass per entry); no source rewalk.  Runs on the
    ACTUAL fields so a model_copy-bypassed nested admission/entry
    cannot be trusted by class membership or by a skipped leaf law.
    """
    _fence_admission_bound_models(admission, "admission")
    history_cap = admission.history_bounds.max_occurrences
    for entry in (admission.root_entry, *admission.entries):
        _fence_entry_metadata(entry, "entry", history_occurrence_cap=history_cap)
        if entry.entry_class is not entry.key_record.authority_class:
            raise _fixed("entry class must equal the key record authority class")
        if tuple(entry.member_classes) != tuple(entry.key_record.member_classes):
            raise _fixed("entry authority vector must equal the key record vector")
        if entry.width != len(set(entry.key_record.member_occurrences)):
            raise _fixed("entry width must equal the distinct key record member paths")
        if entry.root_digest != admission.root_digest:
            raise _fixed("every file entry binds the selected governing root digest")
        if entry.key_record.root_digest != admission.root_digest:
            raise _fixed("every file entry key record binds the selected governing root digest")
        if entry.key_record.content_key != entry.content_key:
            raise _fixed("every entry key record content key agrees with the entry")
        if _canonical_entry_key(entry.key_record) != entry.content_key:
            raise _fixed("every entry canonical key re-derives from its actual key record")


def _check_reverse_member_relation(admission: CurrentRootCompositionAdmission) -> None:
    """J02/K02: the ACTUAL reverse member index must equal EXACTLY the
    represented member-path -> ALL and ONLY admitted content keys
    relation, including the root entry.

    Every row binds the ACTUAL admission scoped key and the exact
    root flags; rows are canonically ordered (strictly increasing
    paths, no duplicates); no row names a path represented by no
    admitted entry (foreign/nonmember pollution); no row carries a
    content key no entry admitted at that path (wrong member-to-key
    edge, unknown key, extraneous association); and no represented
    path lacks its row (missing association).  Legitimate shared
    members (one path, several admitted keys) stay legal: the row
    must hold the COMPLETE key set.  Charged METADATA work only:
    one bounded expected-relation build plus fixed comparisons per
    row; no source rewalk and no graph recomputation.  Runs on the
    ACTUAL fields so a model_copy-bypassed nested admission cannot
    be trusted by class membership alone.
    """
    # K02: the ACTUAL row container/count/scalar shape and the
    # STRICT canonical sorted/distinct key order are validated
    # BEFORE the set comparison can erase duplicate/order facts
    # (a model_copy-bypassed row keeps its raw tuple; the leaf
    # row law alone is not the parent-boundary proof).
    # Charged METADATA work only (bounded per row, precharged by
    # ``row_shape_units`` on the I outer); no source scan or
    # semantic compiler work.
    expected: dict[str, set[str]] = {}
    for entry in (admission.root_entry, *admission.entries):
        for path in entry.key_record.member_occurrences:
            bucket = expected.get(path)
            if bucket is None:
                expected[path] = {entry.content_key}
            else:
                bucket.add(entry.content_key)
    previous_path: str | None = None
    covered: set[str] = set()
    for row in admission.path_associations:
        if previous_path is not None and row.path <= previous_path:
            raise _fixed("reverse index rows must be sorted by distinct path")
        previous_path = row.path
        covered.add(row.path)
        if row.scoped_key != admission.admission_scoped_key:
            raise _fixed("every reverse index row binds the actual admission scoped key")
        if row.path not in expected:
            raise _fixed("the reverse index never names an unrepresented member path")
        keys = row.content_keys
        if not isinstance(keys, tuple) or any(not isinstance(k, str) for k in keys):
            raise _fixed("each reverse index row holds a closed content-key tuple")
        if not keys:
            raise _fixed("each reverse index row names at least one admitted content key")
        if len(set(keys)) != len(keys):
            raise _fixed("each reverse index row holds distinct content keys")
        if list(keys) != sorted(keys):
            raise _fixed("each reverse index row holds canonically sorted content keys")
        if set(keys) != expected[row.path]:
            raise _fixed("each reverse index row holds exactly the admitted content keys")
        if row.is_root != (row.path == admission.root_path):
            raise _fixed("root association flags must match the root path")
    if covered != set(expected):
        raise _fixed("the reverse index covers every represented member path exactly once")


class CurrentRootCompositionOutcome(StrEnum):
    """Closed composition outcomes.

    ``ok`` carries the actual same-run selection, the actual
    selected root source provenance, the fresh current graph over
    the selected root and the canonical admission under the
    selected governing digest.  ``refused_root_conflict`` is the
    authoritative differing-root (or no-selected-root) result: NO
    selected source, NO ready graph/admission output, and NEVER a
    bootstrap fallback.  The remaining names are the fixed typed
    derivation failures (budget/foreign/version/malformed/
    no-root), never relabelled as a root absence or a conflict.
    """

    OK = "ok"
    REFUSED_FOREIGN_SCOPE = "refused_foreign_scope"
    REFUSED_VERSION_CONFLICT = "refused_version_conflict"
    REFUSED_STATE_MALFORMED = "refused_state_malformed"
    REFUSED_NO_ROOT = "refused_no_root"
    REFUSED_OVER_BOUND = "refused_over_bound"
    REFUSED_ROOT_CONFLICT = "refused_root_conflict"


class CurrentRootCompositionLimitation(StrEnum):
    """Closed composition limitation vocabulary.

    The value set is the closed 1:1 union of the accepted 018-h
    root-lineage names (55) and the accepted 018-g
    current-admission names (30, which already carry the 018-f
    graph names 1:1; three names are shared by both) = 82 inherited
    values, plus the NEW composition-level ``root_conflict``
    (83 values total).  Inherited names propagate with their EXACT
    original value (the G value-mapping law): a crossed domain
    yields its ONE fixed name, never a blanket label.  A durable
    test maps EVERY inherited enum value 1:1 against both accepted
    enums (H mapping + G value-map pattern).
    """

    ADMISSION_DIAGNOSTICS_FULL = "admission_diagnostics_full"
    ADMISSION_WORK_UNITS_EXHAUSTED = "admission_work_units_exhausted"
    ARGUMENTS_MALFORMED_UNICODE = "arguments_malformed_unicode"
    ARGUMENTS_OVER_BOUND = "arguments_over_bound"
    ARGUMENTS_UNSUPPORTED = "arguments_unsupported"
    BATCH_OVER_BOUND = "batch_over_bound"
    BUNDLES_OVER_BOUND = "bundles_over_bound"
    CALL_ID_MALFORMED = "call_id_malformed"
    CALL_ID_MISSING = "call_id_missing"
    CANDIDATE_UNPROVEN = "candidate_unproven"
    CAUSAL_LINKS_OVER_BOUND = "causal_links_over_bound"
    COMPETING_ROOTS = "competing_roots"
    CURRENTNESS_DIAGNOSTICS_OVER_BOUND = "currentness_diagnostics_over_bound"
    CURRENTNESS_WORK_UNITS_OVER_BOUND = "currentness_work_units_over_bound"
    DIAGNOSTICS_FULL = "diagnostics_full"
    ENTRIES_OVER_BOUND = "entries_over_bound"
    ENTRY_SOURCE_BYTES_OVER_BOUND = "entry_source_bytes_over_bound"
    ENVELOPE_UNPROVEN = "envelope_unproven"
    FOREIGN_SCOPE = "foreign_scope"
    FRONTIER_CONFLICT = "frontier_conflict"
    FRONTIER_OVER_BOUND = "frontier_over_bound"
    GRAPH_CANDIDATES_OVER_BOUND = "graph_candidates_over_bound"
    GRAPH_DEPTH_OVER_BOUND = "graph_depth_over_bound"
    GRAPH_DIAGNOSTICS_OVER_BOUND = "graph_diagnostics_over_bound"
    GRAPH_DOCUMENTS_OVER_BOUND = "graph_documents_over_bound"
    GRAPH_EDGES_OVER_BOUND = "graph_edges_over_bound"
    GRAPH_NODES_OVER_BOUND = "graph_nodes_over_bound"
    GRAPH_SOURCE_BYTES_OVER_BOUND = "graph_source_bytes_over_bound"
    GRAPH_WORK_UNITS_OVER_BOUND = "graph_work_units_over_bound"
    GROUPS_OVER_BOUND = "groups_over_bound"
    HISTORY_WORK_UNITS_OVER_BOUND = "history_work_units_over_bound"
    ISSUANCE_CONFLICT = "issuance_conflict"
    ISSUANCES_OVER_BOUND = "issuances_over_bound"
    MALFORMED_BINDING = "malformed_binding"
    MARKER_DUPLICATE = "marker_duplicate"
    MARKER_EMPTY = "marker_empty"
    MARKER_MISSING = "marker_missing"
    MARKER_ORDER = "marker_order"
    MARKER_OVER_BOUND = "marker_over_bound"
    MARKER_OVERLAP = "marker_overlap"
    MARKER_SEARCH_OVER_BOUND = "marker_search_over_bound"
    MEMBER_OCCURRENCES_OVER_BOUND = "member_occurrences_over_bound"
    MEMBER_PATH_OVER_BOUND = "member_path_over_bound"
    MEMBER_UNRESOLVED = "member_unresolved"
    MEMBERS_OVER_BOUND = "members_over_bound"
    NO_ROOT = "no_root"
    OCCURRENCES_OVER_BOUND = "occurrences_over_bound"
    OUTPUT_INCONSISTENT = "output_inconsistent"
    PATHS_OVER_BOUND = "paths_over_bound"
    PLAN_UNSUPPORTED = "plan_unsupported"
    RECEIPT_BINDING_MISMATCH = "receipt_binding_mismatch"
    RECEIPT_CYCLE = "receipt_cycle"
    RECEIPT_UNKNOWN_PARENT = "receipt_unknown_parent"
    RELATION_PAIRS_OVER_BOUND = "relation_pairs_over_bound"
    REPLAY_POSITION_SHIFTED = "replay_position_shifted"
    RESULT_CONFLICT = "result_conflict"
    RESULTS_OVER_BOUND = "results_over_bound"
    RETAINED_MEMBERS_OVER_BOUND = "retained_members_over_bound"
    RETAINED_PIECES_OVER_BOUND = "retained_pieces_over_bound"
    RETAINED_SOURCE_BYTES_OVER_BOUND = "retained_source_bytes_over_bound"
    REVERSE_ASSOCIATIONS_OVER_BOUND = "reverse_associations_over_bound"
    REVISION_OVERFLOW = "revision_overflow"
    ROOT_CONFLICT = "root_conflict"
    ROOT_CONTEXT_MISMATCH = "root_context_mismatch"
    ROOT_FACTS_OVER_BOUND = "root_facts_over_bound"
    ROOT_MALFORMED = "root_malformed"
    ROOT_MISSING = "root_missing"
    ROOT_SOURCE_BYTES_OVER_BOUND = "root_source_bytes_over_bound"
    ROOT_SOURCE_UNPROVEN = "root_source_unproven"
    SEAM_CONFLICT = "seam_conflict"
    SEGMENT_UNEXPLAINED = "segment_unexplained"
    SEGMENTS_OVER_BOUND = "segments_over_bound"
    SOURCE_CONFLICT = "source_conflict"
    SOURCE_OVER_BOUND = "source_over_bound"
    STATE_MALFORMED = "state_malformed"
    TOTAL_ENTRY_SOURCE_BYTES_OVER_BOUND = "total_entry_source_bytes_over_bound"
    TOTAL_SOURCE_OVER_BOUND = "total_source_over_bound"
    TOTAL_WORK_UNITS_OVER_BOUND = "total_work_units_over_bound"
    VERSION_UNSUPPORTED = "version_unsupported"
    WITNESS_MEMBERSHIPS_OVER_BOUND = "witness_memberships_over_bound"
    WORK_UNITS_OVER_BOUND = "work_units_over_bound"
    WORKSPACE_MISMATCH = "workspace_mismatch"
    WORKSPACE_UNPROVEN = "workspace_unproven"


class CurrentRootCompositionBounds(_GraphFrozen):
    """New finite per-OPERATION current-root composition bounds.

    The order fixes the defaults AND the hard ceilings exactly:
    stricter positive values are permitted and ANY wider direct
    construction is refused.  These are DERIVED units over ONE pure
    operation (never tokens, cache occupancy or RSS): the total
    outer work ledger covers the ENTIRE operation (H
    namespace/state/selection/source-resolution plus D/E/F/G/
    scanner/closure/key/index/model/source/sort/output work), and
    the diagnostic ceiling bounds the composition-level newly
    emitted limitations (the inherited H/F/G diagnostic domains
    keep their own exact caps and names).
    """

    max_total_work_units: int = Field(default=1048576, ge=1, le=1048576)
    max_diagnostics: int = Field(default=64, ge=1, le=64)


#: The TEN bound models carried by the admission (the NEW-I
#: wrapper domain).  Typed model construction does not prove the
#: field shape after a model_copy bypass, so EVERY field of EVERY
#: carried bound model is rechecked against its declared closed
#: range BEFORE any cap is read from it and before any serializer
#: can walk it (M01).
_ADMISSION_BOUND_MODELS: tuple[tuple[str, type[BaseModel]], ...] = (
    ("bounds", CurrentRootCompositionBounds),
    ("currentness_bounds", CurrentnessBounds),
    ("graph_bounds", CurrentGraphBounds),
    ("admission_bounds", BundleAdmissionBounds),
    ("admission_derivation_bounds", CurrentAdmissionBounds),
    ("proof_bounds", BundleProofBounds),
    ("inherited_graph_bounds", GraphBounds),
    ("observation_bounds", ObservationBounds),
    ("history_bounds", HistoryBounds),
    ("lineage_bounds", RootLineageBounds),
)

#: The closed fence walk cost over the TEN admission bound models:
#: one isinstance class check plus two units per declared field of
#: the carried bound models (the metadata loop and both range
#: comparisons per field).  The kernel reserves exactly this before
#: every admission/result model path that can reach the walk
#: (M01/I8).
ADMISSION_BOUND_FENCE_UNITS = 10 + 2 * sum(len(m.model_fields) for _, m in _ADMISSION_BOUND_MODELS)


def _fence_admission_bound_models(admission: CurrentRootCompositionAdmission, field: str) -> None:
    """The CLOSED type+scalar fence on the TEN carried admission
    bound models BEFORE any cap is read from them or any accepted
    helper may serialize them (M01/I8).

    Typed model construction does not prove the field shape after a
    model_copy bypass, so every bound must be the ACTUAL expected
    model with closed scalar fields BEFORE the first cap read or
    serializer traversal.  A fixed private refusal: no serializer
    traversal, no raw value echo, and the closed field walk only
    touches declared fields.
    """
    for name, model_cls in _ADMISSION_BOUND_MODELS:
        actual = getattr(admission, name)
        if not isinstance(actual, model_cls):
            raise _fixed(f"{field}.{name} must be the actual bound model")
        _closed_bounds_fence(actual, f"{field}.{name}")


class CurrentRootCompositionEntry(_GraphFrozen):
    """One retained CURRENT root-composition admission entry.

    Mirrors the accepted 018-g entry law exactly: the 018-c
    canonical semantic key bytes and ``BundleKeyRecord`` are reused
    for identical semantic inputs (same recipe, same fields), now
    under the SELECTED governing root digest; ``content_key`` must
    equal the key record's own ``content_key`` AND the re-derived
    canonical bytes.  A root entry carries the exact retained
    selected root source bytes (repr-suppressed; the invariants
    bind length and digest; the exact EMPTY root is legal) plus the
    ACTUAL 018-h ENVELOPE or READ root provenance (the accepted
    discriminated variants, unchanged) and NO read witnesses (the
    root entry is evidenced: envelope anchor or retained original
    read binding; the compatible maximal original witness facts are
    retained by the same-run selection record, never fabricated
    here).  A file entry keeps the accepted 018-b ``BundleProof``
    by bounded immutable reference with the admitted segment
    indices separate from entry-local canonical numbering; its
    ``witnesses`` retain ALL relevant maximal current proof/group
    coordinates, each with ITS OWN original occurrence/segment
    coordinates.
    """

    entry_class: EntryClass
    content_key: str = Field(pattern=_HEX64)
    key_record: InstanceOf[BundleKeyRecord]
    width: int = Field(ge=1)
    member_classes: tuple[MemberClass, ...] = Field(min_length=1)
    root_digest: str = Field(pattern=_HEX64)
    #: Exact retained SELECTED root source bytes (root entries
    #: only; the exact empty root is legal).
    root_text: str | None = None
    root_source_byte_length: int | None = Field(default=None, ge=0)
    #: The ACTUAL retained selected-root provenance (root entries
    #: only): the accepted 018-h ENVELOPE or READ variant.
    root_provenance: InstanceOf[EnvelopeRootProvenance] | InstanceOf[ReadRootProvenance] | None = (
        None
    )
    proof: InstanceOf[BundleProof] | None = None
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
    def _v_entry(self) -> CurrentRootCompositionEntry:
        # The L01 closed pre-dump metadata fence: the accepted
        # ``_canonical_entry_key`` re-derivation below serializes the
        # key record's carried bound models and dereferences its
        # enum fields directly, so a model_copy-forged scalar, enum,
        # container or group must refuse HERE -- before the first
        # serializer traversal or element visit, with the fixed
        # private error (the leaf path is fenced exactly like the
        # parent boundaries).
        _fence_entry_metadata(self, "entry")
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
            # Preflight the ACTUAL inherited single-source byte cap
            # BEFORE any owned encode: the O(1) character count
            # (bytes are never fewer than characters) and the
            # no-copy walk with early exit at the cap.
            cap = self.key_record.graph_bounds.max_single_source_bytes
            if len(text) > cap:
                raise _fixed("retained root source exceeds the inherited single-source cap")
            if _utf8_byte_length_capped(text, cap) > cap:
                raise _fixed("retained root source exceeds the inherited single-source cap")
            root_bytes = text.encode("utf-8")  # the ONE owned encode
            if self.root_source_byte_length != len(root_bytes):
                raise _fixed("root source_byte_length must equal the retained bytes")
            if _sha256_hex(root_bytes) != self.root_digest:
                raise _fixed("root digest must equal the retained root bytes")
            if self.key_record.member_occurrences != (ROOT_FILENAME,):
                raise _fixed("a root entry is one occurrence at the normalized root")
            if self.key_record.aggregate_source_digest != self.root_digest:
                raise _fixed("root aggregate digest must equal the root digest")
            if self.width != 1 or self.member_classes != (MemberClass.ELIGIBLE,):
                raise _fixed("the root is one always-eligible root-occurrence member")
            provenance = self.root_provenance
            if provenance.kind == "envelope":
                if provenance.root_digest != self.root_digest:
                    raise _fixed("the envelope root provenance binds the root digest")
                if provenance.source_byte_length != self.root_source_byte_length:
                    raise _fixed("the envelope root provenance binds the root bytes")
            else:
                if provenance.read_digest != self.root_digest:
                    raise _fixed("the read root provenance binds the root digest")
                if provenance.read_byte_length != self.root_source_byte_length:
                    raise _fixed("the read root provenance binds the root bytes")
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
        previous = -1
        for index in self.admitted_segments:
            if index < 0 or index <= previous:
                raise _fixed("admitted segment indices must be distinct and increasing")
            previous = index
        if previous >= len(segments):
            raise _fixed("admitted segment indices must index the proof segments")
        # Closed count prefight from the retained segment METADATA
        # (no source walk) BEFORE any slice/join/encode: the
        # admitted region's exact byte total against the ACTUAL
        # inherited single-source cap, its char total against that
        # SAME byte cap (a UTF-8 lower bound: every code point
        # encodes to at least one byte, so a char span alone already
        # over the cap refuses WITHOUT any owned slice/copy), and its
        # char total against the retained source length.
        region_chars = 0
        region_bytes = 0
        for position in self.admitted_segments:
            segment = segments[position]
            region_chars += segment.char_length
            region_bytes += segment.byte_length
        cap = self.key_record.graph_bounds.max_single_source_bytes
        if region_bytes > cap:
            raise _fixed("admitted region exceeds the inherited single-source byte cap")
        if region_chars > cap:
            raise _fixed("admitted region exceeds the inherited single-source byte cap")
        if region_chars > len(proof.source_text):
            raise _fixed("admitted region cannot exceed the retained source text")
        if len(self.admitted_segments) != 1 and self.admitted_segments != tuple(
            range(len(segments))
        ):
            raise _fixed("admitted region is the whole bundle or one proven group")
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
        provenance = "no"
        if self.root_provenance is not None:
            provenance = self.root_provenance.kind
        return (
            "CurrentRootCompositionEntry("
            f"entry_class={self.entry_class.value!r}, "
            f"content_key={self.content_key!r}, "
            f"key_record=<canonical record suppressed>, "
            f"width={self.width!r}, "
            f"member_classes={[m.value for m in self.member_classes]!r}, "
            f"root_digest={self.root_digest!r}, "
            f"admitted_segments={self.admitted_segments!r}, "
            f"source={source}, "
            f"root_provenance={provenance!r}, "
            f"witnesses={len(self.witnesses)})"
        )

    __str__ = __repr__


def current_root_composition_scope_key(
    history_key: str,
    workspace: str,
    root_digest: str,
    lineage_key: str,
    lineage_id: str,
    revision: int,
    contract_version: str,
    policy_version: str,
    admission_version: str,
    observation_version: str,
    graph_version: str,
    reference_version: str,
    proof_version: str,
    history_version: str,
    arguments_version: str,
    lineage_contract_version: str,
    lineage_policy_version: str,
    currentness_contract_version: str,
    currentness_policy_version: str,
    currentness_recipe_version: str,
    graph_contract_version: str,
    graph_policy_version: str,
    currentness_scope_key: str,
    graph_scope_key: str,
    admission_namespace_key: str,
    admission_scoped_key: str,
    bounds: CurrentRootCompositionBounds,
    currentness_bounds: CurrentnessBounds,
    graph_bounds: CurrentGraphBounds,
    admission_bounds: BundleAdmissionBounds,
    admission_derivation_bounds: CurrentAdmissionBounds,
    proof_bounds: BundleProofBounds,
    inherited_graph_bounds: GraphBounds,
    observation_bounds: ObservationBounds,
    history_bounds: HistoryBounds,
    lineage_bounds: RootLineageBounds,
) -> str:
    """The derived root-composition admission's output scope identity.

    Binds the ACTUAL 018-d history scope, the workspace, the
    SELECTED governing root digest, the ACTUAL 018-h lineage scope,
    the ACTUAL D lineage ID and revision, every ACTUAL inherited
    version, the accepted
    018-e/018-f and 018-h contract/policy/recipe versions, the NEW
    composition contract/policy versions, the validated 018-e and
    018-f scope keys, the ACTUAL 018-c admission namespace and
    scoped keys, and EVERY effective bound set (new composition,
    currentness, current-graph, admission, proof, graph,
    observation, history and root-lineage) — so a caller tag alone
    cannot establish identity and a forged/stale key cannot hide
    different actual version, bound or scope fields.  Recomputed on
    every construction; the key function binds the supplied
    validated facts (the derivation revalidates the actual fields
    first and emits only the supported constants).

    The closed bound-field fences run BEFORE any dump: a
    model_copy bypass cannot smuggle a wrong-shape field into the
    serialization (warnings=False silences serializer diagnostics;
    it is not a validation).
    """
    for field, bound in (
        ("bounds", bounds),
        ("currentness_bounds", currentness_bounds),
        ("graph_bounds", graph_bounds),
        ("admission_bounds", admission_bounds),
        ("admission_derivation_bounds", admission_derivation_bounds),
        ("proof_bounds", proof_bounds),
        ("inherited_graph_bounds", inherited_graph_bounds),
        ("observation_bounds", observation_bounds),
        ("history_bounds", history_bounds),
        ("lineage_bounds", lineage_bounds),
    ):
        _closed_bounds_fence(bound, field)
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
        lineage_contract_version,
        lineage_policy_version,
        currentness_contract_version,
        currentness_policy_version,
        currentness_recipe_version,
        graph_contract_version,
        graph_policy_version,
        history_key,
        workspace,
        root_digest,
        lineage_key,
        lineage_id,
        str(revision),
        currentness_scope_key,
        graph_scope_key,
        admission_namespace_key,
        admission_scoped_key,
        json.dumps(
            bounds.model_dump(mode="json", warnings=False), sort_keys=True, separators=(",", ":")
        ),
        json.dumps(
            currentness_bounds.model_dump(mode="json", warnings=False),
            sort_keys=True,
            separators=(",", ":"),
        ),
        json.dumps(
            graph_bounds.model_dump(mode="json", warnings=False),
            sort_keys=True,
            separators=(",", ":"),
        ),
        json.dumps(
            admission_bounds.model_dump(mode="json", warnings=False),
            sort_keys=True,
            separators=(",", ":"),
        ),
        json.dumps(
            admission_derivation_bounds.model_dump(mode="json", warnings=False),
            sort_keys=True,
            separators=(",", ":"),
        ),
        json.dumps(
            proof_bounds.model_dump(mode="json", warnings=False),
            sort_keys=True,
            separators=(",", ":"),
        ),
        json.dumps(
            inherited_graph_bounds.model_dump(mode="json", warnings=False),
            sort_keys=True,
            separators=(",", ":"),
        ),
        json.dumps(
            observation_bounds.model_dump(mode="json", warnings=False),
            sort_keys=True,
            separators=(",", ":"),
        ),
        json.dumps(
            history_bounds.model_dump(mode="json", warnings=False),
            sort_keys=True,
            separators=(",", ":"),
        ),
        json.dumps(
            lineage_bounds.model_dump(mode="json", warnings=False),
            sort_keys=True,
            separators=(",", ":"),
        ),
    ]
    return _sha256_hex(json.dumps(payload, separators=(",", ":")).encode("utf-8"))


class CurrentRootCompositionAdmission(_GraphFrozen):
    """One derived CURRENT root-composition admission for the EXACT
    input H scope/revision and SELECTED governing root it describes.

    Mirrors the accepted 018-g admission law over the SELECTED
    governing root: the 018-f current graph (fresh least fixed point
    with the selected root as the new root supplier) is carried by
    reference with its own scope/diagnostics; ``root_entry`` is
    always present on an ``ok`` derivation and carries the ACTUAL
    018-h ENVELOPE or READ selected-root provenance (never a
    fabricated anchor, envelope or read occurrence); ``entries``
    are the interned file-bundle entries under the selected
    governing digest; ``path_associations`` is the complete reverse
    member-path index; ``admission_reasons`` is the ACTUAL bounded
    sorted/deduplicated admission-reason tuple with
    ``emitted_admission_reasons`` bound to its length under BOTH
    the NEW and the inherited admission caps in the same domain
    (018-f graph diagnostics stay F output by reference, never
    re-emitted here).  ``lineage_key``/``revision`` bind the
    container to the ACTUAL input H state's lineage scope and
    revision (H revision in exact 1:1 with the wrapped D
    revision).  ``scope_key`` is RECOMPUTED from the actual fields
    on every construction: a stale or forged key is refused, never
    retained.
    """

    history_key: str
    revision: int = Field(ge=0, le=MAX_REVISION)
    workspace: str
    root_path: str = ROOT_FILENAME
    root_digest: str
    lineage_key: str
    #: The ACTUAL 018-d opaque lineage ID of the retained history:
    #: it is the missing link that lets the admission namespace
    #: context RE-DERIVE the actual input history key (I7).
    lineage_id: str
    admission_version: str
    observation_version: str
    graph_version: str
    reference_version: str
    proof_version: str
    history_version: str
    arguments_version: str
    lineage_contract_version: str = ROOT_LINEAGE_CONTRACT_VERSION
    lineage_policy_version: str = ROOT_LINEAGE_POLICY_VERSION
    currentness_contract_version: str = CURRENTNESS_CONTRACT_VERSION
    currentness_policy_version: str = CURRENTNESS_POLICY_VERSION
    currentness_recipe_version: str = OPAQUE_GROUP_RECIPE_VERSION
    graph_contract_version: str = CURRENT_GRAPH_CONTRACT_VERSION
    graph_policy_version: str = CURRENT_GRAPH_POLICY_VERSION
    contract_version: str = CURRENT_ROOT_COMPOSITION_CONTRACT_VERSION
    policy_version: str = CURRENT_ROOT_COMPOSITION_POLICY_VERSION
    bounds: CurrentRootCompositionBounds = Field(default_factory=CurrentRootCompositionBounds)
    currentness_bounds: CurrentnessBounds = Field(default_factory=CurrentnessBounds)
    graph_bounds: CurrentGraphBounds = Field(default_factory=CurrentGraphBounds)
    admission_bounds: BundleAdmissionBounds = Field(default_factory=BundleAdmissionBounds)
    #: The ACTUAL 018-g derivation budget (G total + entry-byte
    #: cumulative ceiling) that produced this admission.
    admission_derivation_bounds: CurrentAdmissionBounds = Field(
        default_factory=CurrentAdmissionBounds
    )
    proof_bounds: BundleProofBounds = Field(default_factory=BundleProofBounds)
    inherited_graph_bounds: GraphBounds = Field(default_factory=GraphBounds)
    observation_bounds: ObservationBounds = Field(default_factory=ObservationBounds)
    history_bounds: HistoryBounds = Field(default_factory=HistoryBounds)
    lineage_bounds: RootLineageBounds = Field(default_factory=RootLineageBounds)
    currentness_scope_key: str
    graph_scope_key: str
    admission_namespace_key: str
    admission_scoped_key: str
    scope_key: str
    root_entry: InstanceOf[CurrentRootCompositionEntry]
    entries: tuple[InstanceOf[CurrentRootCompositionEntry], ...] = ()
    path_associations: tuple[InstanceOf[CurrentAdmissionPathAssociation], ...] = ()
    graph: InstanceOf[CurrentGraph]
    work_units: int = Field(ge=0)
    entry_source_bytes: int = Field(ge=0)
    entries_retained: int = Field(ge=1)
    member_occurrences_charged: int = Field(ge=1)
    reverse_association_attempts: int = Field(ge=0)
    emitted_admission_reasons: int = Field(ge=0, le=64)
    admission_reasons: tuple[CurrentAdmissionLimitation, ...] = ()

    @field_validator(
        "history_key",
        "root_digest",
        "lineage_key",
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
        "lineage_contract_version",
        "lineage_policy_version",
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

    @field_validator("lineage_id")
    @classmethod
    def _v_lineage_id(cls, value: str, info: object) -> str:
        if not 1 <= len(value) <= 128 or any(c.isspace() for c in value):
            raise _fixed("lineage_id must be 1..128 non-space characters")
        return value

    @field_validator("admission_reasons", mode="before")
    @classmethod
    def _preflight_admission_reasons(cls, value: object, info: object) -> tuple[object, ...]:
        """The closed length fence BEFORE any item coercion: a
        hostile over-cap container refuses with ONE fixed private
        error -- never a per-item enum error storm.  The raw length
        is checked under the hard ceiling AND both actual
        admission-domain caps (the inherited admission bounds and
        the NEW derivation bounds) whenever those bound records are
        already validated on this construction; the record-level
        validator re-binds the retained tuple under both caps."""
        if isinstance(value, (str, bytes)) or not isinstance(value, (list, tuple)):
            raise _fixed("admission reasons must be a tuple")
        length = len(value)
        if length > 64:
            raise _fixed("admission reasons exceed the hard ceiling")
        data: dict[str, object] = getattr(info, "data", None) or {}
        for bound in (
            data.get("admission_bounds"),
            data.get("admission_derivation_bounds"),
        ):
            if bound is None:
                continue
            cap = getattr(bound, "max_diagnostics", None)
            if not isinstance(cap, int) or isinstance(cap, bool):
                raise _fixed("admission diagnostics cap must be integral")
            if length > cap:
                raise _fixed("admission reasons exceed the actual admission-domain cap")
        return tuple(value)

    @field_validator("admission_reasons")
    @classmethod
    def _v_admission_reasons(
        cls, value: tuple[CurrentAdmissionLimitation, ...], info: object
    ) -> tuple[CurrentAdmissionLimitation, ...]:
        if len(value) > 64:
            raise _fixed("admission reasons exceed the hard ceiling")
        if tuple(sorted(set(value), key=lambda r: r.value)) != value:
            raise _fixed("admission reasons must be sorted and deduplicated")
        return value

    @model_validator(mode="after")
    def _v_admission(self) -> CurrentRootCompositionAdmission:
        if self.root_entry.entry_class is not EntryClass.ROOT_ENTRY:
            raise _fixed("the root entry is the required ROOT_ENTRY")
        if self.root_entry.root_digest != self.root_digest:
            raise _fixed("the root entry binds the selected governing root digest")
        # J01: EVERY retained file entry (key record + canonical key
        # through the entry law) binds the SELECTED governing digest:
        # the genuine historical entry under the old governing root is
        # refused even though its namespace and proof are genuine and
        # unchanged.
        _check_selected_root_binding(self)
        keys = [entry.content_key for entry in self.entries]
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
            raise _fixed("the carried graph binds the selected governing root digest")
        if self.graph.scope_key != self.graph_scope_key:
            raise _fixed("the carried graph scope key must equal the bound key")
        # ACTUAL carried-context binding (I7): the admission's
        # graph/currentness version, bound and scope tags must equal
        # the ACTUAL carried graph's own context fields -- a detached
        # tag or hash that merely recomputes a coherent scope key
        # never makes a different actual version/bound context valid.
        if (
            self.graph.contract_version != self.graph_contract_version
            or self.graph.policy_version != self.graph_policy_version
            or self.graph.currentness_contract_version != self.currentness_contract_version
            or self.graph.currentness_policy_version != self.currentness_policy_version
            or self.graph.currentness_recipe_version != self.currentness_recipe_version
            or self.graph.currentness_scope_key != self.currentness_scope_key
            or self.graph.bounds != self.graph_bounds
            or self.graph.currentness_bounds != self.currentness_bounds
            or self.graph.graph_bounds != self.inherited_graph_bounds
        ):
            raise _fixed(
                "the carried graph context must bind the actual version/bound/scope fields"
            )
        if self.emitted_admission_reasons != len(self.admission_reasons):
            raise _fixed("emitted_admission_reasons must equal the retained reason count")
        # The retained reason tuple is bound in the SAME domain
        # under BOTH actual admission-domain caps: the NEW derivation
        # cap and the ACTUAL inherited admission cap.  The copied
        # bound scalars are shape-checked before any cap is read
        # (a model_copy bypass cannot smuggle a non-integral cap
        # into the comparison).
        for cap in (
            self.admission_derivation_bounds.max_diagnostics,
            self.admission_bounds.max_diagnostics,
        ):
            if not isinstance(cap, int) or isinstance(cap, bool):
                raise _fixed("admission diagnostics cap must be integral")
        if self.emitted_admission_reasons > self.admission_derivation_bounds.max_diagnostics:
            raise _fixed("emitted admission reasons cannot exceed the derivation admission cap")
        if self.emitted_admission_reasons > self.admission_bounds.max_diagnostics:
            raise _fixed("emitted admission reasons cannot exceed the inherited admission cap")
        # J02: the ACTUAL reverse index equals EXACTLY the represented
        # member-path -> ALL and ONLY admitted content keys relation
        # (root entry included): actual scoped-key binding per row,
        # exact root flags, canonical ordering/dedup, no foreign or
        # nonmember rows, no wrong member-to-key edge or unknown key,
        # and no missing association.  The earlier forward-only
        # coverage check is superseded by the exact relation.
        _check_reverse_member_relation(self)
        # ACTUAL admission-namespace binding (I7): EVERY retained
        # entry's key record re-derives the ACTUAL 018-c admission
        # namespace, and that namespace must be the admission's
        # ACTUAL namespace: equal source bytes/provenance from
        # another principal/session/workspace never make a foreign
        # key record's canonical namespace valid.  The closed
        # pre-dump fence (I8) runs BEFORE the accepted helper
        # serializes each entry's carried bound models: an entry
        # reconstructed after its key record was model_copy-forged
        # must refuse before the first serializer traversal.
        for entry in (self.root_entry, *self.entries):
            _fence_key_record_bounds(entry.key_record, "key_record")
            entry_ns = _entry_admission_namespace(entry.key_record)
            if (
                entry_ns.namespace_key != self.admission_namespace_key
                or entry_ns.scoped_key != self.admission_scoped_key
            ):
                raise _fixed("every entry binds the actual admission namespace")
        # ACTUAL input-namespace D re-derivation (I7): the
        # admission context (the root entry key record's actual
        # identity/bound fields, the ACTUAL record versions, the
        # bound namespace tags, the ACTUAL D lineage ID and the
        # actual bound sets) must RE-DERIVE the ACTUAL input
        # history key.  A coherently rekeyed FOREIGN admission
        # context (another principal/session with matching tags,
        # rows and I scope) inside the actual H/history/graph is
        # refused -- entry-to-detached-tag equality is never the
        # association law.
        kr = self.root_entry.key_record
        expected_history_key = _sha256_hex(
            _canonical_history_fields(
                kr.principal,
                kr.session,
                kr.repository,
                kr.route,
                kr.model_identity,
                kr.config_fingerprint,
                kr.workspace,
                kr.mode.value,
                self.admission_version,
                self.observation_version,
                self.graph_version,
                self.reference_version,
                self.proof_version,
                self.admission_namespace_key,
                self.admission_scoped_key,
                self.lineage_id,
                self.history_version,
                self.arguments_version,
                self.history_bounds,
                kr.admission_bounds,
                kr.proof_bounds,
                kr.graph_bounds,
                kr.observation_bounds,
            )
        )
        if expected_history_key != self.history_key:
            raise _fixed("the admission context must rederive the actual history key")
        expected_scope = current_root_composition_scope_key(
            self.history_key,
            self.workspace,
            self.root_digest,
            self.lineage_key,
            self.lineage_id,
            self.revision,
            self.contract_version,
            self.policy_version,
            self.admission_version,
            self.observation_version,
            self.graph_version,
            self.reference_version,
            self.proof_version,
            self.history_version,
            self.arguments_version,
            self.lineage_contract_version,
            self.lineage_policy_version,
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
            self.admission_derivation_bounds,
            self.proof_bounds,
            self.inherited_graph_bounds,
            self.observation_bounds,
            self.history_bounds,
            self.lineage_bounds,
        )
        if self.scope_key != expected_scope:
            raise _fixed("the scope key must bind the actual fields")
        return self

    def __repr__(self) -> str:  # noqa: D105 - privacy law
        root_provenance = self.root_entry.root_provenance
        return (
            "CurrentRootCompositionAdmission("
            f"history_key={self.history_key!r}, "
            f"revision={self.revision!r}, "
            f"workspace=<private-path>, "
            f"root_digest={self.root_digest!r}, "
            f"lineage_key={self.lineage_key!r}, "
            f"root_provenance={root_provenance.kind if root_provenance is not None else 'none'}, "
            f"entries={len(self.entries)!r}, "
            f"path_associations={len(self.path_associations)!r}, "
            f"admission_reasons={len(self.admission_reasons)!r}, "
            f"scope_key={self.scope_key!r})"
        )

    __str__ = __repr__


class CurrentRootComposition(_GraphFrozen):
    """ONE derived current-root graph/admission composition result.

    Pure derivation output over the EXACT input H state: the input
    is immutable and is never mutated; the ``state`` field is
    ALWAYS the EXACT input ``RootLineageState`` object (identity
    preserved on every outcome).  ``ok`` carries the ACTUAL same-run
    ``RootSelectionResult`` (the causal-maximal current-root
    selection with ALL compatible maximal original witness facts),
    the ACTUAL selected root source provenance (the accepted 018-h
    ENVELOPE or READ variant bound to the actual retained anchor
    fields or the actual retained original read binding), the
    selected source byte length, the freshly recomputed 018-f
    current graph (the selected root as the new root supplier) and
    the canonical admission under the selected governing digest,
    plus the surfaced selection limitations (e.g. the fixed
    ``ROOT_SOURCE_UNPROVEN`` when a known authority coexists with
    retained unproven root source) retained explicitly in
    ``diagnostics`` -- structural derivation, never a claim of
    request readiness, filesystem freshness or runtime policy.
    Every refusal carries the EXACT input state and NO partial
    graph/entries plus its closed reason(s);
    ``refused_root_conflict`` is the authoritative differing-root
    (or no-selected-root) result with NO selected source and NO
    ready graph/admission output, never a bootstrap fallback.
    """

    outcome: CurrentRootCompositionOutcome
    state: InstanceOf[RootLineageState]
    selection: InstanceOf[RootSelectionResult] | None = None
    selected_root_provenance: (
        InstanceOf[EnvelopeRootProvenance] | InstanceOf[ReadRootProvenance] | None
    ) = None
    selected_root_source_byte_length: int | None = Field(default=None, ge=0)
    graph: InstanceOf[CurrentGraph] | None = None
    admission: InstanceOf[CurrentRootCompositionAdmission] | None = None
    diagnostics: tuple[CurrentRootCompositionLimitation, ...] = ()

    @field_validator("diagnostics", mode="before")
    @classmethod
    def _v_diagnostics_preflight(cls, value: object, info: object) -> object:
        if isinstance(value, (list, tuple)) and len(value) > 64:
            raise _fixed("diagnostics exceed the hard ceiling")
        return value

    @field_validator("diagnostics")
    @classmethod
    def _v_diagnostics(
        cls, value: tuple[CurrentRootCompositionLimitation, ...], info: object
    ) -> tuple[CurrentRootCompositionLimitation, ...]:
        if tuple(sorted(set(value), key=lambda r: r.value)) != value:
            raise _fixed("diagnostics must be sorted and deduplicated")
        return value

    @model_validator(mode="after")
    def _v_result(self) -> CurrentRootComposition:
        if self.outcome is CurrentRootCompositionOutcome.OK:
            selection = self.selection
            provenance = self.selected_root_provenance
            graph = self.graph
            admission = self.admission
            if (
                selection is None
                or selection.outcome.value != "ok"
                or provenance is None
                or self.selected_root_source_byte_length is None
                or graph is None
                or admission is None
            ):
                raise _fixed(
                    "an ok composition carries the actual selection, selected "
                    "source provenance, graph and admission"
                )
            if admission.root_digest != graph.root_digest:
                raise _fixed("the admission and graph bind the same selected digest")
            if (
                selection.selected_source_digest is None
                or admission.root_digest != selection.selected_source_digest
            ):
                raise _fixed("the selected source digest binds the graph and admission")
            if provenance.kind == "envelope" and provenance.root_digest != graph.root_digest:
                raise _fixed("the envelope provenance binds the selected digest")
            if provenance.kind == "read" and provenance.read_digest != graph.root_digest:
                raise _fixed("the read provenance binds the selected digest")
            # ACTUAL same-run association joins (I7): the selection,
            # the graph and the admission all bind the EXACT input
            # state/lineage scope; every selected witness is RETAINED
            # by the input state (a structurally valid selection from
            # another state cannot be spliced in); the admission
            # carries the SAME actual graph object and the ACTUAL
            # selected provenance/length; and the retained selection
            # limitation is surfaced exactly.
            state = self.state
            d_state = state.d_state
            if selection.lineage_key != state.lineage_key or selection.revision != state.revision:
                raise _fixed("the selection binds the exact input lineage scope and revision")
            if (
                graph.history_key != d_state.history_key
                or graph.revision != d_state.revision
                or admission.history_key != d_state.history_key
                or admission.revision != d_state.revision
            ):
                raise _fixed(
                    "the graph and admission describe the exact input D scope and revision"
                )
            if admission.lineage_key != state.lineage_key:
                raise _fixed("the admission binds the exact input lineage scope")
            if admission.graph is not graph:
                raise _fixed("the admission carries the same actual graph (reference)")
            if admission.root_entry.root_provenance != provenance:
                raise _fixed("the root entry carries the actual selected root provenance")
            if (
                admission.root_entry.root_source_byte_length
                != self.selected_root_source_byte_length
            ):
                raise _fixed("the root entry binds the actual selected source byte length")
            # J01/J02: the nested admission's ACTUAL association
            # fields are re-checked HERE on the ok path: a
            # model_copy-bypassed nested admission/entry (stale
            # governing digest on a retained file entry, or a
            # polluted/incomplete reverse row) cannot be trusted by
            # class membership or self-consistent detached tags.
            _check_selected_root_binding(admission)
            _check_reverse_member_relation(admission)
            for fact in selection.witness_facts:
                if fact not in state.root_facts:
                    raise _fixed("every selected witness is retained by the input state")
                if fact.source_digest != selection.selected_source_digest:
                    raise _fixed("every retained maximal witness binds the selected source")
                if fact.source_byte_length != self.selected_root_source_byte_length:
                    raise _fixed("the selected source length binds the retained maximal witnesses")
            if not any(fact.provenance == provenance for fact in selection.witness_facts):
                raise _fixed("the selected provenance is a retained maximal witness provenance")
            # ACTUAL input-state proof/witness join (I7): every
            # retained representative proof is the EXACT original
            # proof object retained by the EXACT input D state,
            # every witness coordinate re-binds its OWN occurrence's
            # original proof coordinates, and a READ selected
            # provenance re-binds its retained occurrence.  A later
            # genuine proof/entry/row spliced into an earlier state
            # (where no such occurrence exists) is refused.  The
            # occurrence indexes are built ONCE (charged linearly in
            # the kernel reservation); each entry/witness is a fixed
            # number of metadata comparisons -- no source rewalk.
            d_occurrences = d_state.occurrences
            occ_by_id = {occ.occurrence_id: occ for occ in d_occurrences}
            proof_ids = {id(occ.proof) for occ in d_occurrences}
            if provenance.kind == "read":
                sel_occ = occ_by_id.get(provenance.occurrence_id)
                if (
                    sel_occ is None
                    or sel_occ.call_id != provenance.call_id
                    or sel_occ.endpoint != provenance.endpoint
                ):
                    raise _fixed("the selected read provenance binds a retained occurrence")
            for entry in admission.entries:
                if id(entry.proof) not in proof_ids:
                    raise _fixed("every entry proof is the exact original retained proof")
                for witness in entry.witnesses:
                    w_occ = occ_by_id.get(witness.occurrence_id)
                    if w_occ is None:
                        raise _fixed("every witness binds a retained input occurrence")
                    w_proof = w_occ.proof
                    if (
                        witness.request_index != w_proof.request_index
                        or witness.call_position != w_proof.call_position
                        or witness.result_position != w_proof.result_position
                    ):
                        raise _fixed("every witness rebinds the original proof coordinates")
                    if max(witness.segment_indices) >= len(w_proof.segments):
                        raise _fixed("every witness segment is occurrence-local")
            selection_unproven = "root_source_unproven" in {
                limitation.value for limitation in selection.limitations
            }
            if (
                selection_unproven
                and CurrentRootCompositionLimitation.ROOT_SOURCE_UNPROVEN not in self.diagnostics
            ):
                raise _fixed("the retained selection limitation must be surfaced exactly")
            if not selection_unproven and self.diagnostics:
                raise _fixed("a clean selection surfaces no composition diagnostic")
            if self.diagnostics and any(
                d is not CurrentRootCompositionLimitation.ROOT_SOURCE_UNPROVEN
                for d in self.diagnostics
            ):
                # An ok result surfaces ONLY the fixed retained
                # selection limitation (ROOT_SOURCE_UNPROVEN); every
                # other diagnostic names a refusal.
                raise _fixed("an ok composition surfaces only the retained selection limitation")
            return self
        # COMMON to EVERY refusal, including the authoritative
        # root-conflict result: no partial graph/admission, no
        # selected source provenance or byte length, at least one
        # fixed limitation, and a selection (when actually computed)
        # that binds the exact input state.
        if self.graph is not None or self.admission is not None:
            raise _fixed("a refusal carries no partial graph or admission")
        if self.selected_root_provenance is not None:
            raise _fixed("a refusal has no selected source provenance")
        if self.selected_root_source_byte_length is not None:
            raise _fixed("a refusal carries no selected source byte length")
        if self.selection is not None:
            state = self.state
            if (
                self.selection.lineage_key != state.lineage_key
                or self.selection.revision != state.revision
            ):
                raise _fixed("a refusal selection binds the exact input lineage scope and revision")
        if not self.diagnostics:
            raise _fixed("a refusal exposes at least one fixed limitation")
        if self.outcome is CurrentRootCompositionOutcome.REFUSED_ROOT_CONFLICT:
            if self.selection is None or self.selection.outcome.value not in (
                "root_content_conflict",
                "no_selected_root",
            ):
                raise _fixed("a root-conflict result carries the actual selection outcome")
        return self

    def __repr__(self) -> str:  # noqa: D105 - privacy law
        provenance = (
            self.selected_root_provenance.kind
            if self.selected_root_provenance is not None
            else "none"
        )
        return (
            "CurrentRootComposition("
            f"outcome={self.outcome.value!r}, "
            f"selection={'yes' if self.selection is not None else 'no'}, "
            f"selected_root_provenance={provenance!r}, "
            f"graph={'yes' if self.graph is not None else 'no'}, "
            f"admission={'yes' if self.admission is not None else 'no'}, "
            f"diagnostics={[d.value for d in self.diagnostics]!r})"
        )

    __str__ = __repr__

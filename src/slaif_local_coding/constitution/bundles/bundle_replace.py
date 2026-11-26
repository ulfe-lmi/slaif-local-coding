"""Pure exact-span source-replacement transaction (objective 022-b).

Implements the pure, versioned request transformation of
``docs/CACHE-IMPLEMENTATION-PLAN.md`` policy 12 and
``docs/CACHE-REWORK.md`` section 11 over the accepted 017/018/019/021
records: the edit plan is derived from the actual current decoded
request, the accepted 017 observations, the original 018-p
proof/occurrence records and 018-t admission witnesses, and the actual
019/021 prepared current working set. Edits are planned and applied
atomically without mutating the input; roles, non-source text, wrappers,
prefix/suffix, printed delimiter lines, Unicode/CRLF outside the edits,
images, all tool IDs/names/arguments/status/order and API fields are
preserved. The transaction is pure: no generation, no filesystem IO, no
retention, no upstream or Gateway access.

Marker law: two unambiguously versioned opaque marker kinds (live
reference, non-resolving evidence) are authenticated with a
domain-separated standard HMAC under supplied private per-session key
material and scoped to the complete trusted namespace, the original
role, the exact occurrence or root-source identity, and the segment/
carrier association. The wire format is MAC-only: a marker emits
ONLY the versioned kind tag plus the fixed-length CANONICAL
base64url spelling of the 32-byte HMAC tag; every private identity
input (namespace key, original role, occurrence/root-source
identity, original endpoint/call/result/piece/segment association,
entry class, content key, compiled digest, source digest) stays
INSIDE the HMAC and never appears in the wire bytes. JSON array
indexes remain physical edit coordinates only: marker authority is
bound to the ORIGINAL scope/call/result/segment association, so a
carrier moved in resent history cannot re-authenticate. Verification
re-derives the expected tags from the bounded actual retained
proof/selection and the trusted carrier bindings and
constant-time-compares the tag. Unknown/malformed/forged/stale live
references, moved markers and incompatible carrier use in recognized
source fields reject the transaction. An
accepted replay of the same
marker neither changes its authority nor creates a second edit; a valid
transformed marker never becomes a new raw source proof and retains no
stale compiled payload. Ordinary text outside the marker carriers keeps
its own role and is never recognized as marker authority.

Preparation law: every committed edit is earned by complete
attributable source, the exact current prepared context and the narrow
internal durable-generation handoff (the ACTUAL accepted
``RecoveryPublishResult``/pointer and the EXACT retained
``RamStateSnapshot`` bound by immutable reference). A boolean or a free
generation integer does not establish preparation.

All-or-nothing: a nonusable selection, missing/failed/mismatched
durability, a cross-namespace join, a stale snapshot, an invalid marker
or a conflicting edit returns no transformed payload under the plan-13
typed failure families (503/409/422). Unsupported/nonzero/truncated/
unpaired/uncertain reads with candidate coordinates remain unchanged
under the existing limitation (they earn no proof and no edit).

Privacy law: operational ``str``/``repr`` of every emitted model never
echoes private call IDs, paths, marker key material or raw/compiled
source text: fixed enums, counts, structural locations and digests only;
all validation strings are fixed.
"""

from __future__ import annotations

import base64
import copy
import hashlib
import hmac
import re
from dataclasses import dataclass
from dataclasses import field as dataclass_field
from enum import StrEnum
from typing import Any

from .bundle_admission_models import EntryClass
from .bundle_proof_models import (
    BundlePiece,
    BundleProof,
    BundleProofKind,
    BundleSegment,
    BundleSurface,
)
from .bundle_replace_models import (
    EVIDENCE_MARKER_DOMAIN,
    EVIDENCE_MARKER_TAG,
    LIVE_MARKER_DOMAIN,
    LIVE_MARKER_TAG,
    MARKER_SUFFIX,
    REPLACEMENT_HTTP_STATUS,
    MarkerKind,
    MarkerRecord,
    PreparedGenerationProof,
    ReplacementBounds,
    ReplacementOutcome,
    ReplacementResult,
    SourceEdit,
    UnspliceReplayResult,
)
from .bundle_selection import (
    BundleSelectionDecision,
    SelectionOutcome,
    SelectionReadyEntry,
    SelectionWorkingEntry,
)
from .causal_history import _collect, _RootLineageContext
from .causal_history_models import (
    CausalHistoryOutcome,
    CompletedReadOccurrence,
    HistoryBounds,
    ResultFingerprintRecord,
    RootAnchor,
    canonicalize_tool_arguments,
)
from .current_admission_models import CurrentAdmissionWitness
from .currentness_models import CurrentnessOverlay, CurrentnessReason
from .graph_observation import GraphRequest
from .observation_models import (
    PRIVATE_ID_PLACEHOLDER,
    CharSpan,
    ObservationReport,
    OccurrenceKind,
    ProcessObservation,
    ProcessOutcome,
    ReadObservation,
    ReadOutcome,
    RootOccurrence,
    RootStatus,
)
from .observe import ENDPOINT_CHAT, ENDPOINT_RESPONSES
from .ram_state_models import RamStateSnapshot
from .recovery_store import RecoveryStoreLimitation
from .root_lineage import _HOuter
from .root_lineage_models import ReadRootProvenance, RootSelectionOutcome
from .root_region_currentness_models import (
    RootRegionCurrentnessOutcome,
    RootRegionCurrentnessResult,
)
from .root_region_lineage import _region_d_namespace
from .root_region_lineage_models import (
    RootRegionLineageFact,
    RootRegionReadProvenance,
)


def _durable_guard(
    proof: PreparedGenerationProof,
    current_snapshot: RamStateSnapshot,
) -> None:
    """Fail closed unless the ACTUAL durable generation handoff is sound.

    The narrow typed handoff (``PreparedGenerationProof``) must carry
    the ACTUAL accepted publish outcome, never a claim: the real
    :class:`PreparedGenerationProof.publish` (the actual
    ``RecoveryPublishResult``) has the closed OK limitation, its
    pointer exists with a determinate positive generation that agrees
    with BOTH the published ``generation`` and the store-observed
    ``actual_generation``, and ``proof.snapshot`` is the exact current
    :class:`RamStateSnapshot` by immutable identity. A boolean or a
    free generation integer cannot establish preparation.

    Raises ``_ReplaceRefusal`` with the fixed
    ``CarrierDetail.GENERATION_NOT_DURABLE`` detail (the plan-13 503
    family) on any divergence; no field value is echoed."""
    publish = proof.publish
    if publish.limitation is not RecoveryStoreLimitation.OK:
        raise _refuse(CarrierDetail.GENERATION_NOT_DURABLE)
    pointer = publish.pointer
    if pointer is None:
        raise _refuse(CarrierDetail.GENERATION_NOT_DURABLE)
    generation = publish.generation
    if generation is None or generation < 1:
        raise _refuse(CarrierDetail.GENERATION_NOT_DURABLE)
    if pointer.generation != generation:
        raise _refuse(CarrierDetail.GENERATION_NOT_DURABLE)
    if pointer.generation != publish.actual_generation:
        raise _refuse(CarrierDetail.GENERATION_NOT_DURABLE)
    if proof.snapshot is not current_snapshot:
        raise _refuse(CarrierDetail.GENERATION_NOT_DURABLE)


_ROOT_ENVELOPE_ROLE = "root_envelope"
_TOOL_RESULT_ROLE = "file_tool_result"
_B64URL_ALPHABET = frozenset("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_")


# ---------------------------------------------------------------------------
# Marker codec (domain-separated standard HMAC, MAC-only opaque wire form)
# ---------------------------------------------------------------------------

#: The fixed tag length of the MAC-only wire form: a 32-byte
#: HMAC-SHA256 tag is exactly 43 unpadded base64url characters.
MAC_TAG_B64_LENGTH = 43
MAC_TAG_BYTES = 32


def _field_bytes(*fields: str) -> bytes:
    """The closed MAC-input encoding: one length-prefixed UTF-8 field
    per scoped identity (the fields stay INSIDE the HMAC input and are
    never emitted on the wire)."""
    out = bytearray()
    for value in fields:
        raw = value.encode("utf-8")
        out += len(raw).to_bytes(4, "big") + raw
    return bytes(out)


def _mac(key: bytes, body: bytes) -> bytes:
    return hmac.new(key, body, hashlib.sha256).digest()


def _tag_prefix(kind: MarkerKind) -> str:
    return LIVE_MARKER_TAG if kind is MarkerKind.LIVE_REFERENCE else EVIDENCE_MARKER_TAG


def _encode_tag(mac: bytes, kind: MarkerKind) -> str:
    """The MAC-only wire form: versioned kind tag + fixed-length
    canonical base64url HMAC tag + closing bracket. No private field
    bytes; the spelling is the canonical unpadded form (the final
    symbol's padding bits are zero)."""
    opaque = base64.urlsafe_b64encode(mac).decode("ascii").rstrip("=")
    if len(opaque) != MAC_TAG_B64_LENGTH:
        raise AssertionError("the HMAC tag is not the fixed length")
    return f"{_tag_prefix(kind)}{opaque}{MARKER_SUFFIX}"


def _live_scope_fields(
    namespace_key: str,
    original_role: str,
    occurrence_identity: str,
    endpoint: str,
    call_id: str,
    call_position: int,
    result_position: int,
    piece_index: int,
    segment_index: int,
    entry_class: str,
    content_key: str,
    compiled_digest: str,
    source_digest: str,
) -> bytes:
    """The closed live-reference HMAC scope: the complete trusted
    namespace, the original role, the exact occurrence or root-source
    identity and the ORIGINAL endpoint/call/result/piece/segment
    association, plus the target entry binding (entry class, content
    key, compiled digest, source digest). JSON array indexes of the
    current payload are physical edit coordinates and are deliberately
    NOT part of the authority binding."""
    return _field_bytes(
        LIVE_MARKER_DOMAIN,
        namespace_key,
        original_role,
        occurrence_identity,
        endpoint,
        call_id,
        str(call_position),
        str(result_position),
        str(piece_index),
        str(segment_index),
        entry_class,
        content_key,
        compiled_digest,
        source_digest,
    )


def _evidence_scope_fields(
    namespace_key: str,
    original_role: str,
    occurrence_identity: str,
    endpoint: str,
    call_id: str,
    call_position: int,
    result_position: int,
    piece_index: int,
    segment_index: int,
    source_digest: str,
) -> bytes:
    """The closed evidence-marker HMAC scope: the original namespace,
    the exact occurrence/root-source identity, the ORIGINAL
    endpoint/call/result/piece/segment association and the exact
    original source digest.  The marker is deliberately NOT bound to
    any entry content key: a known positively superseded original may
    be absent from the current admission entirely, and reconstructing
    the old entry key is prohibited — the non-resolving marker
    identifies the exact original occurrence (namespace + occurrence +
    source digest + segment/carrier association), never a current
    entry (a known positively superseded original or an actual
    selection omission of a prepared optional source)."""
    return _field_bytes(
        EVIDENCE_MARKER_DOMAIN,
        namespace_key,
        original_role,
        occurrence_identity,
        endpoint,
        call_id,
        str(call_position),
        str(result_position),
        str(piece_index),
        str(segment_index),
        source_digest,
    )


def make_live_marker(
    key: bytes,
    *,
    namespace_key: str,
    original_role: str,
    occurrence_identity: str,
    endpoint: str,
    call_id: str,
    call_position: int,
    result_position: int,
    piece_index: int,
    segment_index: int,
    entry_class: str,
    content_key: str,
    compiled_digest: str,
    source_digest: str,
) -> str:
    """Build the versioned opaque live-reference marker (kind 1).

    Emits ONLY the versioned kind plus the fixed-length canonical MAC
    tag; the complete trusted namespace, original role,
    occurrence/root-source identity, the original
    endpoint/call/result/piece/segment association and the target
    entry binding are the HMAC inputs, not wire bytes."""
    body = _live_scope_fields(
        namespace_key,
        original_role,
        occurrence_identity,
        endpoint,
        call_id,
        call_position,
        result_position,
        piece_index,
        segment_index,
        entry_class,
        content_key,
        compiled_digest,
        source_digest,
    )
    return _encode_tag(_mac(key, body), MarkerKind.LIVE_REFERENCE)


def make_evidence_marker(
    key: bytes,
    *,
    namespace_key: str,
    original_role: str,
    occurrence_identity: str,
    endpoint: str,
    call_id: str,
    call_position: int,
    result_position: int,
    piece_index: int,
    segment_index: int,
    source_digest: str,
) -> str:
    """Build the versioned opaque non-resolving evidence marker (kind 2).

    Tied to the original namespace, the exact occurrence/root-source
    identity, the original endpoint/call/result/piece/segment
    association and the exact original source digest — never to an
    entry content key (the old entry key of a superseded original is
    never reconstructed); emits ONLY the versioned kind plus the
    fixed-length canonical MAC tag."""
    body = _evidence_scope_fields(
        namespace_key,
        original_role,
        occurrence_identity,
        endpoint,
        call_id,
        call_position,
        result_position,
        piece_index,
        segment_index,
        source_digest,
    )
    return _encode_tag(_mac(key, body), MarkerKind.EVIDENCE)


@dataclass(frozen=True, slots=True)
class ExpectedTag:
    """ONE re-derived expected tag from the bounded actual retained
    proof/selection and a trusted carrier binding.

    ``mac`` is the 32-byte expected HMAC tag (private; never wire
    material, never repr'd); the private occurrence association
    values (``occurrence_identity``, ``call_id``) are exact internal
    bookkeeping and are suppressed from operational representations;
    ``stale`` marks a live tag derived from a retained entry that is
    no longer in the accepted current selection (a stale live
    reference, never current authority). The binding fields describe
    the trusted derivation, not the wire bytes.
    """

    kind: MarkerKind
    mac: bytes = dataclass_field(repr=False)
    marker: str
    occurrence_identity: str = dataclass_field(repr=False)
    endpoint: str
    call_id: str = dataclass_field(repr=False)
    call_position: int
    result_position: int
    piece_index: int
    segment_index: int
    role: str
    source_digest: str
    content_key: str | None
    compiled_digest: str | None
    entry_class: str | None
    stale: bool = False


class MarkerExpectations:
    """The bounded expected-tag table for one transaction run.

    The table is derived ONLY from trusted state (the complete trusted
    namespace, the actual retained proof/occurrence records, the
    accepted selection and the actual trusted carrier bindings); a
    marker's own bytes never contribute to the table. Tags are keyed
    by kind; the ORIGINAL scope/call/result/segment association of the
    matched tag is what the carrier join binds (the current payload's
    JSON array indexes are physical edit coordinates, never the
    authority binding).
    """

    def __init__(self, tags: tuple[ExpectedTag, ...]) -> None:
        self._by_kind: dict[MarkerKind, list[ExpectedTag]] = {}
        for tag in tags:
            self._by_kind.setdefault(tag.kind, []).append(tag)

    def __len__(self) -> int:
        return sum(len(tags) for tags in self._by_kind.values())

    def all_of_kind(self, kind: MarkerKind) -> tuple[ExpectedTag, ...]:
        return tuple(self._by_kind.get(kind, ()))


def derive_live_tag(
    key: bytes,
    *,
    namespace_key: str,
    original_role: str,
    occurrence_identity: str,
    endpoint: str,
    call_id: str,
    call_position: int,
    result_position: int,
    piece_index: int,
    segment_index: int,
    entry_class: str,
    content_key: str,
    compiled_digest: str,
    source_digest: str,
    stale: bool = False,
) -> ExpectedTag:
    """Re-derive ONE expected live tag from trusted derivation inputs
    (the transaction supplies them from the retained proof/selection
    and the trusted carrier binding; ``stale`` for a retained entry
    that is not in the accepted current selection)."""
    body = _live_scope_fields(
        namespace_key,
        original_role,
        occurrence_identity,
        endpoint,
        call_id,
        call_position,
        result_position,
        piece_index,
        segment_index,
        entry_class,
        content_key,
        compiled_digest,
        source_digest,
    )
    mac = _mac(key, body)
    return ExpectedTag(
        kind=MarkerKind.LIVE_REFERENCE,
        mac=mac,
        marker=_encode_tag(mac, MarkerKind.LIVE_REFERENCE),
        occurrence_identity=occurrence_identity,
        endpoint=endpoint,
        call_id=call_id,
        call_position=call_position,
        result_position=result_position,
        piece_index=piece_index,
        segment_index=segment_index,
        role=original_role,
        source_digest=source_digest,
        content_key=content_key,
        compiled_digest=compiled_digest,
        entry_class=entry_class,
        stale=stale,
    )


def derive_evidence_tag(
    key: bytes,
    *,
    namespace_key: str,
    original_role: str,
    occurrence_identity: str,
    endpoint: str,
    call_id: str,
    call_position: int,
    result_position: int,
    piece_index: int,
    segment_index: int,
    source_digest: str,
) -> ExpectedTag:
    """Re-derive ONE expected evidence tag from trusted derivation
    inputs (a known positively superseded original or an actual
    selection omission of a prepared optional source; the scope
    carries no entry content key — see ``_evidence_scope_fields``)."""
    body = _evidence_scope_fields(
        namespace_key,
        original_role,
        occurrence_identity,
        endpoint,
        call_id,
        call_position,
        result_position,
        piece_index,
        segment_index,
        source_digest,
    )
    mac = _mac(key, body)
    return ExpectedTag(
        kind=MarkerKind.EVIDENCE,
        mac=mac,
        marker=_encode_tag(mac, MarkerKind.EVIDENCE),
        occurrence_identity=occurrence_identity,
        endpoint=endpoint,
        call_id=call_id,
        call_position=call_position,
        result_position=result_position,
        piece_index=piece_index,
        segment_index=segment_index,
        role=original_role,
        source_digest=source_digest,
        content_key=None,
        compiled_digest=None,
        entry_class=None,
        stale=False,
    )


@dataclass(frozen=True, slots=True)
class MarkerVerdict:
    """The closed verdict of ONE marker verification.

    ``reason`` is one of: ``ok`` (valid current or evidence
    authority), ``stale`` (a valid live tag for a retained entry no
    longer in the accepted selection), ``forged`` (no expected tag
    match: tampered, unknown key or cross-namespace material),
    ``unknown-kind`` (a marker-like tag of an unrecognized version) or
    ``malformed`` (not the fixed-length CANONICAL MAC-only wire form;
    a final-symbol padding-bit variant of the same tag is malformed,
    never a second spelling of the same authority). Whether the marker
    sits in a trusted carrier for its ORIGINAL association is the
    transaction's carrier join (moved markers and incompatible carrier
    use reject there). The binding fields are populated ONLY from the
    matched re-derived expected tag (trusted state), never from the
    marker bytes; private occurrence association values are suppressed
    from the operational representation.
    """

    valid: bool
    reason: str  # ok | stale | forged | unknown-kind | malformed
    kind: MarkerKind | None = None
    content_key: str | None = None
    compiled_digest: str | None = None
    source_digest: str | None = None
    entry_class: str | None = None
    occurrence_identity: str | None = dataclass_field(default=None, repr=False)
    endpoint: str | None = None
    call_id: str | None = dataclass_field(default=None, repr=False)
    call_position: int | None = None
    result_position: int | None = None
    piece_index: int | None = None
    segment_index: int | None = None
    role: str | None = None
    marker: str | None = None
    marker_start: int = 0
    marker_end: int = 0


def _decode_canonical_tag(opaque: str) -> bytes | None:
    """Decode the fixed-length base64url tag and enforce the CANONICAL
    spelling: the exact length, the closed alphabet and the final
    symbol's padding bits zero (the canonical re-encode round-trip).
    A padding-bit variant decodes to the same bytes but is a
    malformed wire form, never a second accepted spelling."""
    if len(opaque) != MAC_TAG_B64_LENGTH or any(c not in _B64URL_ALPHABET for c in opaque):
        return None
    try:
        mac = base64.urlsafe_b64decode(opaque + "=")
    except Exception:
        return None
    if len(mac) != MAC_TAG_BYTES:
        return None
    if base64.urlsafe_b64encode(mac).decode("ascii").rstrip("=") != opaque:
        return None
    return mac


def verify_marker(
    raw: str,
    start: int,
    *,
    expectations: MarkerExpectations,
) -> MarkerVerdict:
    """Authenticate one marker-shaped candidate by RE-DERIVING the
    expected tags.

    The marker bytes carry only the versioned kind and the fixed
    length canonical MAC tag; the trusted derivation (the bounded
    actual retained proof/selection joined to the trusted carrier
    binding) supplies the expected tags, and the tag is constant-time
    compared. A current match is authority (its ORIGINAL
    scope/call/result/segment association is the matched tag's
    binding); a stale match is a stale live reference; no match is
    forged. The verdict binding comes ONLY from the matched expected
    tag, never from the marker bytes."""
    end = start + len(raw)
    if raw.startswith(LIVE_MARKER_TAG):
        kind = MarkerKind.LIVE_REFERENCE
    elif raw.startswith(EVIDENCE_MARKER_TAG):
        kind = MarkerKind.EVIDENCE
    elif raw.startswith("[slaif-live:v") or raw.startswith("[slaif-evidence:v"):
        return MarkerVerdict(False, "unknown-kind", marker_start=start, marker_end=end)
    else:
        raise AssertionError("unknown marker tag reached the verifier")
    if not raw.endswith(MARKER_SUFFIX):
        return MarkerVerdict(False, "malformed", marker_start=start, marker_end=end)
    opaque = raw[len(_tag_prefix(kind)) : -1]
    mac = _decode_canonical_tag(opaque)
    if mac is None:
        return MarkerVerdict(False, "malformed", kind=kind, marker_start=start, marker_end=end)

    def _verdict(tag: ExpectedTag, reason: str, valid: bool) -> MarkerVerdict:
        return MarkerVerdict(
            valid=valid,
            reason=reason,
            kind=kind,
            content_key=tag.content_key,
            compiled_digest=tag.compiled_digest,
            source_digest=tag.source_digest,
            entry_class=tag.entry_class,
            occurrence_identity=tag.occurrence_identity,
            endpoint=tag.endpoint,
            call_id=tag.call_id,
            call_position=tag.call_position,
            result_position=tag.result_position,
            piece_index=tag.piece_index,
            segment_index=tag.segment_index,
            role=tag.role,
            marker=tag.marker,
            marker_start=start,
            marker_end=end,
        )

    # Current authority first: a non-stale expected tag of this kind.
    for tag in expectations.all_of_kind(kind):
        if not tag.stale and hmac.compare_digest(mac, tag.mac):
            return _verdict(tag, "ok", True)
    # A stale retained-entry live tag is a stale live reference (valid
    # authentication, no current authority).
    for tag in expectations.all_of_kind(kind):
        if tag.stale and hmac.compare_digest(mac, tag.mac):
            return _verdict(tag, "stale", False)
    # No expected tag matches: tampered, unknown key or cross-namespace
    # material. The fixed forged refusal is the only remaining class.
    return MarkerVerdict(False, "forged", kind=kind, marker_start=start, marker_end=end)


def find_markers(text: str) -> tuple[tuple[int, str], ...]:
    """Linear bounded scan for marker candidates in one carrier text.

    Returns ``(start, candidate)`` pairs; a candidate runs from the
    marker-like tag to the FIRST closing bracket (the opaque alphabet
    contains no bracket, so the close is unambiguous). The scan always
    advances past a consumed candidate.
    """
    found: list[tuple[int, str]] = []
    pos = 0
    while pos < len(text):
        live = text.find(LIVE_MARKER_TAG, pos)
        ev = text.find(EVIDENCE_MARKER_TAG, pos)
        # marker-like tags of unknown version/kind must also be consumed
        like = text.find("[slaif-live:v", pos)
        like_ev = text.find("[slaif-evidence:v", pos)
        candidates = [i for i in (live, ev, like, like_ev) if i != -1]
        if not candidates:
            break
        i = min(candidates)
        close = text.find(MARKER_SUFFIX, i)
        if close == -1:
            found.append((i, text[i:]))
            break
        found.append((i, text[i : close + 1]))
        pos = close + 1
    return tuple(found)


# ---------------------------------------------------------------------------
# Carrier lookup and exact span checking (read-only, objective 022-b)
# ---------------------------------------------------------------------------
#
# The edit plan is derived over the ACTUAL current decoded request.  A
# carrier is one exact decoded JSON string (the root ``input_text`` text
# or a tool result output/content field) addressed by its accepted 017
# structural location.  The lookups below are READ-ONLY: they resolve a
# validated location to the payload's own string (never a copy), verify
# the accepted carrier shape and verify the EXACT half-open character
# span against the original retained facts (character length, UTF-8 byte
# length and the SHA-256 of the exact observed bytes).  No payload field
# is ever mutated here; the atomic application layer is a separate saved
# chunk.
#
# Law highlights:
#
# - Only the closed location spellings earn a carrier: the root text
#   carrier is ``$.input[i].content[j]`` (the earned Responses automatic
#   root shape).  Tool carrier shapes are a separate earned surface.
#   Nothing is inferred from unearned shapes; a nonmatching spelling is
#   refused, never guessed.
# - The root carrier shape is the accepted 017 root law: a
#   ``role="user"`` ``input`` item with an ``input_text`` content entry
#   carrying a string ``text``.  Chat root acquisition is NOT earned
#   (there is no Chat root carrier shape in this module).
# - The exact root span is the 017 ``content_span``: the inner source
#   between the versioned delimiters, EXCLUDING the delimiters and the
#   environment tail (which the 017 envelope law preserves separately).
# - Bounds: the carrier text must already be within the supplied bound
#   (the accepted observation bound) before any span work; an over-bound
#   carrier refuses fail-closed (no unbounded copy/parse).
# - Privacy: every refusal carries only the fixed detail code and its
#   typed outcome; carrier text, call IDs and paths never enter errors,
#   operational representations or logs.
class CarrierDetail(StrEnum):
    """Fixed closed detail codes of the carrier/span layer and the
    preparation-durability handoff.

    Stable identifiers that never echo payload text (the privacy law).
    Each code maps to exactly ONE plan-13 typed failure family via
    ``_DETAIL_OUTCOME`` (503 infrastructure/recovery/resource; 409
    version/scope conflict; 422 budget/invalid transform)."""

    #: The location string is not the closed spelling of this carrier
    #: shape (never inferred or re-spelled).
    LOCATION_MALFORMED = "location_malformed"
    #: The location spelling is closed but the payload item/content
    #: shape leaves the accepted carrier shape for that location.
    SHAPE_UNSUPPORTED = "shape_unsupported"
    #: The carrier entry exists in its shape but the string field is
    #: absent or not a string.
    CARRIER_NOT_TEXT = "carrier_not_text"
    #: A well-formed location has no carrier in the actual payload
    #: (the observed coordinates leave the decoded request).
    CARRIER_NOT_FOUND = "carrier_not_found"
    #: A call-identity location is closed but no call record with a
    #: valid string ID sits at that structural position.
    CALL_NOT_FOUND = "call_not_found"
    #: The closed call spelling resolves to a valid call record, but
    #: its ID, tool name or canonical argument fingerprint leaves the
    #: ORIGINAL retained call identity (the observed association and
    #: the actual payload disagree — a reused ID under a different
    #: command or tool is a mismatch, never an edit).
    IDENTITY_MISMATCH = "identity_mismatch"
    #: The location is a closed spelling of the OTHER endpoint domain
    #: (a ``$.input`` coordinate under a Chat selection or a
    #: ``$.messages`` coordinate under a Responses selection): the
    #: actual input endpoint and the supplied coordinate disagree.
    ENDPOINT_MISMATCH = "endpoint_mismatch"
    #: The carrier text or the edit/replacement volume exceeds the
    #: supplied bound (fail closed before unbounded work).
    OVER_BOUND = "over_bound"
    #: A span offset pair leaves the carrier string.
    SPAN_OUT_OF_BOUNDS = "span_out_of_bounds"
    #: The slice character or UTF-8 byte length leaves the original
    #: retained fact.
    SPAN_LENGTH_MISMATCH = "span_length_mismatch"
    #: The slice SHA-256 over the exact observed bytes leaves the
    #: original retained source digest.
    SPAN_DIGEST_MISMATCH = "span_digest_mismatch"
    #: A required piece/segment sub-span is not proven inside the
    #: current carrier (no overlap or the proven region does not cover
    #: it).
    PIECE_NOT_PROVEN = "piece_not_proven"
    #: Two planned edits occupy the same carrier region (overlapping
    #: or identical spans; the same root region is never double-edited).
    EDITS_OVERLAP = "edits_overlap"
    #: The total planned replacement volume exceeds the bound.
    REPLACEMENT_OVER_BOUND = "replacement_over_bound"
    #: The ACTUAL durable-generation handoff leaves the accepted
    #: publish/pointer/generation/snapshot identity law (the plan-13
    #: 503 infrastructure/recovery family).
    GENERATION_NOT_DURABLE = "generation_not_durable"
    #: A retained entry or span cannot be resolved in the ACTUAL
    #: current payload (no usable admission, a detached witness
    #: owner, a root working row with no root carrier): the plan-13
    #: 409 scope-conflict family.
    CARRIER_UNRESOLVED = "carrier_unresolved"
    #: A retained coordinate leaves its owner occurrence or segment
    #: (a spliced / detached retained record): the plan-13 409
    #: scope-conflict family.
    RETAINED_RECORD_MALFORMED = "retained_record_malformed"
    #: A marker in a recognized source field is forged, malformed,
    #: unknown-kind, stale or moved: the plan-13 409 family.
    MARKER_INVALID = "marker_invalid"


#: The closed detail-to-outcome law (plan-13 typed failure families):
#: scope/shape conflicts between the accepted observation coordinates
#: and the actual payload are 409 conflicts; span and piece verification
#: failures are 409 span mismatches; conflicting edits are 409 edit
#: conflicts; bound overruns are 422.
_DETAIL_OUTCOME: dict[CarrierDetail, ReplacementOutcome] = {
    CarrierDetail.LOCATION_MALFORMED: ReplacementOutcome.CROSS_NAMESPACE,
    CarrierDetail.SHAPE_UNSUPPORTED: ReplacementOutcome.CROSS_NAMESPACE,
    CarrierDetail.CARRIER_NOT_TEXT: ReplacementOutcome.CROSS_NAMESPACE,
    CarrierDetail.CARRIER_NOT_FOUND: ReplacementOutcome.CROSS_NAMESPACE,
    CarrierDetail.CALL_NOT_FOUND: ReplacementOutcome.CROSS_NAMESPACE,
    CarrierDetail.IDENTITY_MISMATCH: ReplacementOutcome.CROSS_NAMESPACE,
    CarrierDetail.ENDPOINT_MISMATCH: ReplacementOutcome.CROSS_NAMESPACE,
    CarrierDetail.OVER_BOUND: ReplacementOutcome.OVER_BOUND,
    CarrierDetail.SPAN_OUT_OF_BOUNDS: ReplacementOutcome.SPAN_MISMATCH,
    CarrierDetail.SPAN_LENGTH_MISMATCH: ReplacementOutcome.SPAN_MISMATCH,
    CarrierDetail.SPAN_DIGEST_MISMATCH: ReplacementOutcome.SPAN_MISMATCH,
    CarrierDetail.PIECE_NOT_PROVEN: ReplacementOutcome.SPAN_MISMATCH,
    CarrierDetail.EDITS_OVERLAP: ReplacementOutcome.EDIT_CONFLICT,
    CarrierDetail.REPLACEMENT_OVER_BOUND: ReplacementOutcome.OVER_BOUND,
    CarrierDetail.GENERATION_NOT_DURABLE: ReplacementOutcome.GENERATION_NOT_DURABLE,
    CarrierDetail.CARRIER_UNRESOLVED: ReplacementOutcome.ENTRY_UNRESOLVED,
    CarrierDetail.RETAINED_RECORD_MALFORMED: ReplacementOutcome.CROSS_NAMESPACE,
    CarrierDetail.MARKER_INVALID: ReplacementOutcome.MARKER_INVALID,
}


def _refuse(detail: CarrierDetail) -> _ReplaceRefusal:
    """One fixed internal refusal (typed outcome + closed detail)."""
    return _ReplaceRefusal(_DETAIL_OUTCOME[detail], detail)


class _ReplaceRefusal(Exception):
    """Internal all-or-nothing refusal (fixed outcome + detail, no echo).

    ``outcome`` is the plan-13 typed failure family and ``detail`` the
    closed carrier-layer code; neither ever carries payload text."""

    def __init__(self, outcome: ReplacementOutcome, detail: CarrierDetail) -> None:
        super().__init__(f"{outcome.value}:{detail.value}")
        self.outcome = outcome
        self.detail = detail


@dataclass(frozen=True, slots=True)
class CarrierSlot:
    """One exact decoded string carrier resolved READ-ONLY from the
    ACTUAL current payload.

    ``location`` is the accepted structural JSON-pointer shape and
    ``field`` the exact JSON field holding the string; both are
    observable coordinates (never private content).  ``text`` is the
    payload's own decoded string (no copy is made) and is private
    content: repr-suppressed.  The slot is a view for verification and
    exact-span application; it grants no authority by itself."""

    endpoint: str
    location: str
    field: str
    text: str = dataclass_field(repr=False)

    def __repr__(self) -> str:
        return (
            f"CarrierSlot(endpoint={self.endpoint!r}, "
            f"location={self.location!r}, field={self.field!r}, "
            f"text='<protected {len(self.text)} chars>')"
        )

    __str__ = __repr__


@dataclass(frozen=True, slots=True)
class SpanFacts:
    """The verified EXACT facts of one half-open character span into
    ONE decoded string carrier.

    ``start``/``end`` are character offsets; ``char_length`` the Unicode
    character count; ``byte_length`` the exact UTF-8 byte length;
    ``digest`` the SHA-256 of the exact observed bytes (the digest never
    claims anything about an original filesystem encoding).
    ``byte_start``/``byte_end`` are the UTF-8 byte offsets of the same
    span over the carrier.  All values are observable facts; no source
    text is retained or rendered."""

    start: int
    end: int
    char_length: int
    byte_length: int
    digest: str
    byte_start: int
    byte_end: int


#: The closed root-text-carrier location grammar: exactly
#: ``$.input[i].content[j]`` with canonical nonnegative decimal indexes
#: (the accepted 017 location spelling; no leading zeros, no extra
#: segments, no other endpoint containers).
_ROOT_LOCATION_RE = re.compile(r"^\$\.input\[(\d+)\]\.content\[(\d+)\]$")


def _parse_root_location(location: str) -> tuple[int, int] | None:
    """Parse ONE closed root-location spelling to ``(i, j)`` indexes.

    Returns ``None`` for every nonmatching spelling (tool shapes, other
    containers, padded or negative indexes, extra segments): the caller
    classifies the nonmatch as a malformed root location.  No spelling
    is ever rewritten or inferred."""
    m = _ROOT_LOCATION_RE.match(location)
    if m is None:
        return None
    i_text, j_text = m.groups()
    if i_text != str(int(i_text)) or j_text != str(int(j_text)):
        return None
    return int(i_text), int(j_text)


def lookup_root_carrier(
    payload: dict[str, Any],
    location: str,
    *,
    max_text_chars: int,
) -> CarrierSlot:
    """Resolve ONE validated Responses root location to its exact
    decoded string carrier in the ACTUAL current payload.

    The closed shape (the earned 017 automatic-root law):
    ``$.input[i].content[j]`` where ``input[i]`` is a ``role="user"``
    item with a ``content`` list and ``content[j]`` an ``input_text``
    entry with a string ``text`` field.  The lookup is READ-ONLY: the
    payload is never mutated and the returned slot references the
    payload's own string.  The carrier text must already be within
    ``max_text_chars`` (the accepted observation bound); an over-bound
    carrier refuses before any span work (fail closed).  Chat root
    acquisition is NOT earned: no Chat root carrier shape exists in
    this module, and no non-root spelling is ever inferred.

    Raises ``_ReplaceRefusal`` with the fixed detail:
    LOCATION_MALFORMED (not the closed root spelling),
    SHAPE_UNSUPPORTED (the item/content entry leaves the accepted
    user/input_text shape), CARRIER_NOT_TEXT (the ``text`` field is
    absent or not a string), CARRIER_NOT_FOUND (a well-formed spelling
    with no such carrier in this payload) and OVER_BOUND (the carrier
    text exceeds the bound)."""
    if max_text_chars < 1:
        raise ValueError("max_text_chars must be positive")
    parsed = _parse_root_location(location)
    if parsed is None:
        raise _refuse(CarrierDetail.LOCATION_MALFORMED)
    item_index, entry_index = parsed
    container = payload.get("input")
    if not isinstance(container, list) or not (0 <= item_index < len(container)):
        raise _refuse(CarrierDetail.CARRIER_NOT_FOUND)
    item = container[item_index]
    if not isinstance(item, dict) or item.get("role") != "user":
        raise _refuse(CarrierDetail.SHAPE_UNSUPPORTED)
    content = item.get("content")
    if not isinstance(content, list) or not (0 <= entry_index < len(content)):
        raise _refuse(CarrierDetail.SHAPE_UNSUPPORTED)
    entry = content[entry_index]
    if not isinstance(entry, dict) or entry.get("type") != "input_text":
        raise _refuse(CarrierDetail.SHAPE_UNSUPPORTED)
    text = entry.get("text")
    if not isinstance(text, str):
        raise _refuse(CarrierDetail.CARRIER_NOT_TEXT)
    if len(text) > max_text_chars:
        raise _refuse(CarrierDetail.OVER_BOUND)
    return CarrierSlot(endpoint=ENDPOINT_RESPONSES, location=location, field="text", text=text)


def check_carrier_span(
    slot: CarrierSlot,
    start: int,
    end: int,
    *,
    expected_char_length: int | None = None,
    expected_byte_length: int | None = None,
    expected_digest: str | None = None,
) -> SpanFacts:
    """Verify ONE exact half-open character span against *slot*'s
    decoded string and return the closed :class:`SpanFacts`.

    The span must lie within the carrier (``0 <= start <= end <=
    len(text)``).  When supplied, the expected character length, UTF-8
    byte length and SHA-256 digest (the ORIGINAL retained source facts,
    e.g. the 017 occurrence digest/byte length or the retained root
    entry's exact source facts) must all equal the actual slice facts;
    the digest comparison is constant-time.  A failure refuses with the
    fixed detail (SPAN_OUT_OF_BOUNDS / SPAN_LENGTH_MISMATCH /
    SPAN_DIGEST_MISMATCH) and never echoes any slice text."""
    text = slot.text
    if not (0 <= start <= end <= len(text)):
        raise _refuse(CarrierDetail.SPAN_OUT_OF_BOUNDS)
    char_length = end - start
    if expected_char_length is not None and char_length != expected_char_length:
        raise _refuse(CarrierDetail.SPAN_LENGTH_MISMATCH)
    slice_bytes = text[start:end].encode("utf-8")
    byte_length = len(slice_bytes)
    if expected_byte_length is not None and byte_length != expected_byte_length:
        raise _refuse(CarrierDetail.SPAN_LENGTH_MISMATCH)
    digest = hashlib.sha256(slice_bytes).hexdigest()
    if expected_digest is not None and not hmac.compare_digest(
        digest.encode("ascii"), expected_digest.encode("ascii")
    ):
        raise _refuse(CarrierDetail.SPAN_DIGEST_MISMATCH)
    byte_start = len(text[:start].encode("utf-8"))
    return SpanFacts(
        start=start,
        end=end,
        char_length=char_length,
        byte_length=byte_length,
        digest=digest,
        byte_start=byte_start,
        byte_end=byte_start + byte_length,
    )


def _root_scope_check(occurrence: RootOccurrence, workspace: str) -> None:
    """The ACTUAL scope label of ONE accepted root occurrence must
    equal the prepared trusted namespace workspace (constant-time).

    A same-shaped envelope in a FOREIGN workspace scope is the
    existing scope conflict (``CARRIER_UNRESOLVED``, the plan-13 409
    family), never an edit: the proof bridge has already refused that
    workspace, and byte-identical source in another scope does not
    re-establish the root here; its carrier is never recognized as
    marker authority."""
    label = occurrence.scope_label
    if label is None or not hmac.compare_digest(label.encode("utf-8"), workspace.encode("utf-8")):
        raise _refuse(CarrierDetail.CARRIER_UNRESOLVED)


def join_root_occurrence(
    payload: dict[str, Any],
    occurrence: RootOccurrence,
    *,
    expected_digest: str | None = None,
    expected_char_length: int | None = None,
    expected_byte_length: int | None = None,
    expected_workspace: str | None = None,
    max_text_chars: int,
) -> tuple[CarrierSlot, SpanFacts]:
    """Join ONE accepted 017 root occurrence to its exact CURRENT
    carrier in the actual payload and verify its EXACT content span.

    ``occurrence`` is the accepted 017 classified occurrence
    (``kind`` ROOT, ``status`` OK, its ``location`` the carrier
    spelling and its ``content_span`` the inner source span — the
    delimiters and the environment tail are excluded by the 017
    envelope law).  ``expected_digest`` is the ORIGINAL retained root
    source digest the join must prove; ``expected_char_length`` /
    ``expected_byte_length`` are the original retained exact
    character/UTF-8-byte lengths (checked when supplied).  An omitted
    ``expected_digest`` proves carrier shape and span bounds only — the
    transformed re-join, where the raw bytes left the original and the
    replay scan decides by tag.  The join is
    read-only and returns ``(carrier, span facts)``; a carrier shape
    failure, a span out of bounds or a length/digest mismatch refuses
    with the fixed detail (the observed coordinates or the span leave
    the retained original facts).  ``expected_workspace``, when
    supplied, is the prepared trusted namespace workspace: the
    occurrence's ACTUAL scope label must equal it (a same-shaped
    foreign-workspace envelope refuses the existing scope conflict,
    never an edit).  A non-root or non-OK occurrence is refused as an
    unsupported shape (no root authority is inferred)."""
    if (
        occurrence.kind is not OccurrenceKind.ROOT
        or occurrence.status is not RootStatus.OK
        or occurrence.content_span is None
    ):
        raise _refuse(CarrierDetail.SHAPE_UNSUPPORTED)
    if expected_workspace is not None:
        _root_scope_check(occurrence, expected_workspace)
    slot = lookup_root_carrier(payload, occurrence.location, max_text_chars=max_text_chars)
    span = occurrence.content_span
    facts = check_carrier_span(
        slot,
        span.start,
        span.end,
        expected_char_length=expected_char_length,
        expected_byte_length=expected_byte_length,
        expected_digest=expected_digest,
    )
    return slot, facts


# ---------------------------------------------------------------------------
# Tool carrier lookup (read-only, objective 022-b — saved chunk 1b)
# ---------------------------------------------------------------------------
#
# The two accepted tool read carriers, one per endpoint domain.  Like
# the root carrier, these are resolved READ-ONLY from the ACTUAL current
# payload: the closed location maps to the payload's own decoded string
# (a tool result output/content field), the accepted wire shape is
# verified, and no field is ever mutated.  The call-identity lookup is
# the paired side: it resolves a closed call location to the schema-
# evidenced call ID so the ORIGINAL tool call/result identity can be
# re-joined (the original association the marker authority binds).
#
# Law highlights:
#
# - Responses tool result carrier: ``$.input[i]`` where the item is a
#   ``function_call_output`` with a string ``output``.  Chat tool result
#   carrier: ``$.messages[i]`` where the message is ``role="tool"`` with
#   a string ``content``.  The accepted 017 read law (both surfaces) is
#   the earned shape; nothing is inferred.
# - Call identity: Responses ``$.input[i]`` where the item is a
#   ``function_call`` (or the identity-bookkeeping ``custom_tool_call``
#   family) with a nonempty string ``call_id``; Chat
#   ``$.messages[i].tool_calls[j]`` where the entry is ``type="function"``
#   with a nonempty string ``id``.  A call ID is identity, not text: it
#   is never a carrier and never acquired as source.
# - The location spelling is endpoint-typed: a ``$.input`` coordinate
#   under a Chat selection (or a ``$.messages`` coordinate under a
#   Responses selection) is a closed spelling of the OTHER endpoint
#   domain and refuses ENDPOINT_MISMATCH; any other spelling is
#   LOCATION_MALFORMED (never re-spelled or guessed).
# - Bounds and privacy follow the root carrier law exactly (fail closed
#   before span work; no payload text, call ID or path in refusals or
#   operational representations).
_RESPONSES_ITEM_RE = re.compile(r"^\$\.input\[(\d+)\]$")
_CHAT_MESSAGE_RE = re.compile(r"^\$\.messages\[(\d+)\]$")
_CHAT_TOOLCALL_RE = re.compile(r"^\$\.messages\[(\d+)\]\.tool_calls\[(\d+)\]$")


def _canonical_index(text: str) -> int | None:
    """A canonical nonnegative decimal index (no leading zeros)."""
    if text != str(int(text)):
        return None
    return int(text)


def _require_endpoint(endpoint: str) -> None:
    if endpoint not in (ENDPOINT_RESPONSES, ENDPOINT_CHAT):
        raise ValueError("endpoint must be the explicit validated endpoint")


def lookup_tool_result_carrier(
    payload: dict[str, Any],
    endpoint: str,
    location: str,
    *,
    max_text_chars: int,
) -> CarrierSlot:
    """Resolve ONE validated tool result location to its exact decoded
    string carrier in the ACTUAL current payload.

    The closed shapes (the accepted 017 read law, both surfaces):

    - Responses: ``$.input[i]`` where ``input[i]`` is a
      ``function_call_output`` item with a string ``output`` field.
    - Chat: ``$.messages[i]`` where ``messages[i]`` is a ``role="tool"``
      message with a string ``content`` field.

    The lookup is READ-ONLY (the slot references the payload's own
    string) and the carrier text must already be within
    ``max_text_chars`` (fail closed before span work).  A location that
    is a closed spelling of the OTHER endpoint domain refuses
    ENDPOINT_MISMATCH; any other spelling refuses LOCATION_MALFORMED; a
    well-formed spelling whose item/message leaves the accepted wire
    shape refuses SHAPE_UNSUPPORTED; a missing index refuses
    CARRIER_NOT_FOUND; a nonstring field refuses CARRIER_NOT_TEXT; an
    over-bound carrier refuses OVER_BOUND."""
    _require_endpoint(endpoint)
    if max_text_chars < 1:
        raise ValueError("max_text_chars must be positive")
    if endpoint == ENDPOINT_RESPONSES:
        m = _RESPONSES_ITEM_RE.match(location)
        if m is None:
            if _CHAT_MESSAGE_RE.match(location) is not None:
                raise _refuse(CarrierDetail.ENDPOINT_MISMATCH)
            raise _refuse(CarrierDetail.LOCATION_MALFORMED)
        index = _canonical_index(m.group(1))
        if index is None:
            raise _refuse(CarrierDetail.LOCATION_MALFORMED)
        container = payload.get("input")
        if not isinstance(container, list) or not (0 <= index < len(container)):
            raise _refuse(CarrierDetail.CARRIER_NOT_FOUND)
        item = container[index]
        if not isinstance(item, dict) or item.get("type") != "function_call_output":
            raise _refuse(CarrierDetail.SHAPE_UNSUPPORTED)
        text = item.get("output")
        if not isinstance(text, str):
            raise _refuse(CarrierDetail.CARRIER_NOT_TEXT)
        if len(text) > max_text_chars:
            raise _refuse(CarrierDetail.OVER_BOUND)
        return CarrierSlot(
            endpoint=ENDPOINT_RESPONSES, location=location, field="output", text=text
        )
    # endpoint is ENDPOINT_CHAT
    m = _CHAT_MESSAGE_RE.match(location)
    if m is None:
        if _RESPONSES_ITEM_RE.match(location) is not None:
            raise _refuse(CarrierDetail.ENDPOINT_MISMATCH)
        raise _refuse(CarrierDetail.LOCATION_MALFORMED)
    index = _canonical_index(m.group(1))
    if index is None:
        raise _refuse(CarrierDetail.LOCATION_MALFORMED)
    container = payload.get("messages")
    if not isinstance(container, list) or not (0 <= index < len(container)):
        raise _refuse(CarrierDetail.CARRIER_NOT_FOUND)
    message = container[index]
    if not isinstance(message, dict) or message.get("role") != "tool":
        raise _refuse(CarrierDetail.SHAPE_UNSUPPORTED)
    text = message.get("content")
    if not isinstance(text, str):
        raise _refuse(CarrierDetail.CARRIER_NOT_TEXT)
    if len(text) > max_text_chars:
        raise _refuse(CarrierDetail.OVER_BOUND)
    return CarrierSlot(endpoint=ENDPOINT_CHAT, location=location, field="content", text=text)


@dataclass(frozen=True, slots=True)
class CallIdentity:
    """One schema-evidenced call identity at a closed structural
    position (READ-ONLY view).

    ``call_id`` is the exact observed ID (private association data:
    repr-suppressed); ``wire_family`` is the closed schema family that
    earned the record (observable); ``tool_name`` / ``arguments`` are
    the closed schema function identity of the record (private
    association data: repr-suppressed; ``None`` exactly when the
    closed wire shape carries no function arguments).  The identity is
    a join key for the ORIGINAL tool call/result association, never a
    text carrier and never source authority by itself."""

    endpoint: str
    location: str
    wire_family: str
    call_id: str = dataclass_field(repr=False)
    tool_name: str | None = dataclass_field(default=None, repr=False)
    arguments: str | None = dataclass_field(default=None, repr=False)

    def __repr__(self) -> str:
        return (
            f"CallIdentity(endpoint={self.endpoint!r}, "
            f"location={self.location!r}, wire_family={self.wire_family!r}, "
            f"call_id='{PRIVATE_ID_PLACEHOLDER}')"
        )

    __str__ = __repr__


def lookup_call_identity(
    payload: dict[str, Any],
    endpoint: str,
    location: str,
    *,
    expected_call_id: str | None = None,
) -> CallIdentity:
    """Resolve ONE validated call location to its schema-evidenced call
    identity in the ACTUAL current payload.

    The closed shapes (the accepted 017 call inventory, both surfaces):

    - Responses: ``$.input[i]`` where the item is a ``function_call``
      (or the identity-bookkeeping ``custom_tool_call`` family) with a
      nonempty string ``call_id``.
    - Chat: ``$.messages[i].tool_calls[j]`` where the entry is
      ``type="function"`` with a nonempty string ``id``.

    ``expected_call_id``, when supplied, is the ORIGINAL retained call
    identity the join must re-prove: the actual ID must equal it
    (constant-time) or the lookup refuses IDENTITY_MISMATCH (the
    observed association and the actual payload disagree).  A closed
    spelling of the OTHER endpoint domain refuses ENDPOINT_MISMATCH;
    any other spelling refuses LOCATION_MALFORMED; a well-formed
    spelling whose item/entry leaves the accepted call shape refuses
    SHAPE_UNSUPPORTED; a missing index refuses CARRIER_NOT_FOUND; an
    absent/empty/nonstring ID refuses CALL_NOT_FOUND."""
    _require_endpoint(endpoint)
    if endpoint == ENDPOINT_RESPONSES:
        m = _RESPONSES_ITEM_RE.match(location)
        if m is None:
            if (
                _CHAT_MESSAGE_RE.match(location) is not None
                or _CHAT_TOOLCALL_RE.match(location) is not None
            ):
                raise _refuse(CarrierDetail.ENDPOINT_MISMATCH)
            raise _refuse(CarrierDetail.LOCATION_MALFORMED)
        index = _canonical_index(m.group(1))
        if index is None:
            raise _refuse(CarrierDetail.LOCATION_MALFORMED)
        container = payload.get("input")
        if not isinstance(container, list) or not (0 <= index < len(container)):
            raise _refuse(CarrierDetail.CARRIER_NOT_FOUND)
        item = container[index]
        if not isinstance(item, dict):
            raise _refuse(CarrierDetail.SHAPE_UNSUPPORTED)
        wire_family = item.get("type")
        if wire_family not in ("function_call", "custom_tool_call"):
            raise _refuse(CarrierDetail.SHAPE_UNSUPPORTED)
        call_id = item.get("call_id")
        if not isinstance(call_id, str) or call_id == "":
            raise _refuse(CarrierDetail.CALL_NOT_FOUND)
        if expected_call_id is not None and not hmac.compare_digest(
            call_id.encode("utf-8"), expected_call_id.encode("utf-8")
        ):
            raise _refuse(CarrierDetail.IDENTITY_MISMATCH)
        name = item.get("name") if wire_family == "function_call" else None
        arguments = item.get("arguments") if wire_family == "function_call" else None
        if not isinstance(name, str):
            name = None
        if not isinstance(arguments, str):
            arguments = None
        return CallIdentity(
            endpoint=ENDPOINT_RESPONSES,
            location=location,
            wire_family=wire_family,
            call_id=call_id,
            tool_name=name,
            arguments=arguments,
        )
    # endpoint is ENDPOINT_CHAT
    m = _CHAT_TOOLCALL_RE.match(location)
    if m is None:
        if _RESPONSES_ITEM_RE.match(location) is not None:
            raise _refuse(CarrierDetail.ENDPOINT_MISMATCH)
        raise _refuse(CarrierDetail.LOCATION_MALFORMED)
    message_index = _canonical_index(m.group(1))
    tool_index = _canonical_index(m.group(2))
    if message_index is None or tool_index is None:
        raise _refuse(CarrierDetail.LOCATION_MALFORMED)
    container = payload.get("messages")
    if not isinstance(container, list) or not (0 <= message_index < len(container)):
        raise _refuse(CarrierDetail.CARRIER_NOT_FOUND)
    message = container[message_index]
    if not isinstance(message, dict) or message.get("role") != "assistant":
        raise _refuse(CarrierDetail.SHAPE_UNSUPPORTED)
    tool_calls = message.get("tool_calls")
    if not isinstance(tool_calls, list) or not (0 <= tool_index < len(tool_calls)):
        raise _refuse(CarrierDetail.SHAPE_UNSUPPORTED)
    tool = tool_calls[tool_index]
    if not isinstance(tool, dict) or tool.get("type") != "function":
        raise _refuse(CarrierDetail.SHAPE_UNSUPPORTED)
    call_id = tool.get("id")
    if not isinstance(call_id, str) or call_id == "":
        raise _refuse(CarrierDetail.CALL_NOT_FOUND)
    if expected_call_id is not None and not hmac.compare_digest(
        call_id.encode("utf-8"), expected_call_id.encode("utf-8")
    ):
        raise _refuse(CarrierDetail.IDENTITY_MISMATCH)
    function = tool.get("function")
    name = function.get("name") if isinstance(function, dict) else None
    arguments = function.get("arguments") if isinstance(function, dict) else None
    if not isinstance(name, str):
        name = None
    if not isinstance(arguments, str):
        arguments = None
    return CallIdentity(
        endpoint=ENDPOINT_CHAT,
        location=location,
        wire_family="function",
        call_id=call_id,
        tool_name=name,
        arguments=arguments,
    )


def _verify_call_binding(
    identity: CallIdentity,
    proof_call_id: str,
    piece_index: int,
    results_by_call: dict[str, ResultFingerprintRecord],
    history_bounds: HistoryBounds,
) -> None:
    """The ACTUAL original tool identity of ONE piece's current call.

    The call ID alone is not identity: the retained D result record
    binds the piece's ACTUAL producing call (the read's own call, the
    exec call for the initial process piece, the causally associated
    poll for a poll piece) by tool name and the SAME canonical
    argument fingerprint (the accepted recipe over the observed
    arguments under the retained D scope's argument bounds).  A
    current call that reuses the ID under a different command or tool
    is refused IDENTITY_MISMATCH all-or-nothing.  A missing retained
    record or a missing per-piece binding is a detached retained
    record (RETAINED_RECORD_MALFORMED)."""
    record = results_by_call.get(proof_call_id)
    if record is None or piece_index >= len(record.piece_call_bindings):
        raise _refuse(CarrierDetail.RETAINED_RECORD_MALFORMED)
    _bound_call_id, _bound_endpoint, tool_name, arg_fp = record.piece_call_bindings[piece_index]
    if identity.tool_name is None or not hmac.compare_digest(
        identity.tool_name.encode("utf-8"), tool_name.encode("utf-8")
    ):
        raise _refuse(CarrierDetail.IDENTITY_MISMATCH)
    if identity.arguments is None:
        raise _refuse(CarrierDetail.IDENTITY_MISMATCH)
    fingerprint = canonicalize_tool_arguments(
        identity.tool_name,
        identity.arguments,
        max_argument_bytes=history_bounds.max_argument_bytes,
        max_total_argument_bytes=history_bounds.max_total_argument_bytes,
        max_argument_nodes=history_bounds.max_argument_nodes,
        max_argument_depth=history_bounds.max_argument_depth,
        charge_total=lambda _bytes: True,
        work=lambda: True,
    )
    if fingerprint.fingerprint is None or not hmac.compare_digest(
        fingerprint.fingerprint.encode("ascii"), arg_fp.encode("ascii")
    ):
        raise _refuse(CarrierDetail.IDENTITY_MISMATCH)


# ---------------------------------------------------------------------------
# Retained proof join (objective 022-b — saved chunk 2)
# ---------------------------------------------------------------------------
#
# The join re-derives over the ACTUAL current decoded payload every
# exact original source span that the retained 018-p/018-t record set
# (by immutable reference inside the actual current
# ``RamStateSnapshot``) can still attribute.  Each retained witness is
# joined through ITS OWN original occurrence owner (never the
# representative proof, never reindexed offsets): the witness's
# occurrence identity resolves to the retained completed-read
# occurrence, the witness's original request/call/result positions
# must equal the owner proof's positions, and the witness's
# occurrence-local segment indices index that proof's segments.  A
# segment is REPROVEN only when every piece it overlaps resolves to
# its ACTUAL current carrier (the closed tool result shape; the
# schema-evidenced call identity re-joined constant-time) AND the
# per-piece sub-spans concatenate back to the exact retained segment
# facts (character length, UTF-8 byte length and the SHA-256 of the
# exact observed bytes).  The root span is the earned Responses
# automatic-root content span (delimiters and environment tail
# excluded by the 017 envelope law) verified against the governing
# root digest; a governing root selected through a read keeps its
# carrier a tool result via the selected root's own original
# witness, and the envelope text is never a second edit to the same
# root region.
#
# A well-formed carrier or call that is simply ABSENT from the
# current payload earns no edit and no refusal for its spans; an
# EXISTING carrier that leaves the accepted shape, a detached
# retained record or a span that leaves the retained facts refuses
# all-or-nothing.  No carrier text, call ID or source byte ever
# enters an error or an operational representation; every refusal is
# a fixed detail.
#
# A raw tool edit must join a CURRENT accepted 017 observation bound
# to the SAME original call ID: the current read (outcome COMPLETE)
# or process chain (outcome COMPLETE, same endpoint domain) supplies
# the ACTUAL current call/result carrier locations.  A retained
# result whose bytes still match but whose current wrapper is
# nonzero / truncated / partial / unsupported earns no deletion
# (retained proof and matching bytes alone never do).  A governing
# envelope root absent from the payload earns zero edits (a
# source-absent replay still returns the exact selected context).


@dataclass(frozen=True, slots=True)
class RetainedSpan:
    """One joined exact original source span of ONE retained entry.

    ``role`` is the ORIGINAL API source role of the carrier (root
    envelope versus file tool result); ``occurrence_identity``,
    ``call_id`` and the call/result positions are the ORIGINAL
    association the marker authority binds (private association data:
    the call ID is suppressed from operational representations).
    ``source_digest`` is the exact source digest of the span's owning
    segment (the governing root digest for a root span).
    ``reproven`` is the closed segment re-proof fact: the span's
    exact original bytes were re-proven in the ACTUAL current
    carrier.  ``location`` / ``field`` address the ACTUAL current
    carrier (the current accepted 017 observation's positions); the
    original association stays bound by the call/result positions and
    the marker scope.  ``historical`` marks a span joined through the
    positive-supersession phase from a retained-D nonroot occurrence
    that is ABSENT from the current admission (a known positively
    superseded original): its ``content_key`` is the retained segment's
    source digest (the old entry key is never reconstructed).  A span
    grants no authority by itself."""

    content_key: str
    entry_class: str
    role: str
    endpoint: str
    occurrence_identity: str
    call_id: str = dataclass_field(repr=False)
    call_position: int
    result_position: int
    piece_index: int
    segment_index: int
    location: str
    field: str
    start: int
    end: int
    source_digest: str
    reproven: bool
    #: True ONLY when every overlapping piece carrier was present in
    #: the current payload and the re-proven concatenation left the
    #: exact retained segment facts (a selected span with this fact
    #: refuses SPAN_MISMATCH all-or-nothing; an unselected span
    #: simply earns no edit).
    bytes_mismatch: bool
    #: True ONLY for a span joined through the positive-supersession
    #: phase from a retained-D nonroot occurrence absent from the
    #: current admission (a known positively superseded original).
    historical: bool = False


@dataclass(frozen=True, slots=True)
class _CurrentReadIndex:
    """The ACTUAL current 017 read observations indexed by the
    original call ID (the raw-tool edit join bridge): paired reads by
    their call ID, process chains by their exec call ID."""

    reads_by_call: dict[str, ReadObservation]
    processes_by_exec_call: dict[str, ProcessObservation]


def _current_read_index(observation: ObservationReport) -> _CurrentReadIndex:
    return _CurrentReadIndex(
        reads_by_call={read.call_id: read for read in observation.reads},
        processes_by_exec_call={process.exec_call_id: process for process in observation.processes},
    )


def _current_bridge_proofs(
    payload: dict[str, Any],
    observation: ObservationReport,
    snapshot: RamStateSnapshot,
) -> dict[str, BundleProof]:
    """The ACTUAL current 018-b bundle-proof bridge over THIS payload.

    Reuses the accepted current-carrier proof core through the
    causal-history collection seam: one bounded 017 observation plus
    the shared 018-b proof pass under the ACTUAL retained D scope,
    bound to the SAME retained immutable root anchor (a transformed
    envelope or a rootless payload rebinds to the anchor; the anchor
    is never fabricated and the payload is never altered).  Every
    D-local bound of the retained scope stays binding on the SAME
    shared outer (the retained H ``max_total_work_units``); an
    over-bound crossing (H-outer exhaustion or a D-local bound
    crossing) refuses the typed OVER_BOUND fail closed BEFORE any
    unbounded work, while any other collection or proof refusal
    fails closed to an empty bridge (the affected pieces earn zero
    edits, never a refusal)."""
    d_state = snapshot.state.d_state
    anchor = d_state.root
    if anchor is None:
        return {}
    d_ns = _region_d_namespace(snapshot.namespace)
    known_root_digests = frozenset(
        {anchor.root_digest} | {fact.source_digest for fact in snapshot.state.root_facts}
    )
    outer = _HOuter(snapshot.namespace.root_lineage_bounds.max_total_work_units)
    context = _RootLineageContext(
        known_root_digests=known_root_digests,
        relaxed_envelope_law=True,
        root_read_acquisition=True,
        outer_charge=outer.unit,
    )
    request = GraphRequest(payload=payload, endpoint=observation.endpoint, context=None)
    facts, refusal = _collect((request,), d_ns, d_state, context=context)
    if facts is None:
        if refusal is not None and refusal.outcome is CausalHistoryOutcome.REFUSED_OVER_BOUND:
            raise _refuse(CarrierDetail.OVER_BOUND)
        return {}
    return {bundle.call_id: bundle for bundle in facts.bundles}


def _current_piece_carriers(
    proof: BundleProof,
    piece: BundlePiece,
    index: _CurrentReadIndex,
    bridge_by_call: dict[str, BundleProof],
) -> tuple[str, str] | None:
    """The ACTUAL current call/result carrier locations of ONE
    retained piece, re-joined through the CURRENT accepted 017
    observation bound to the SAME original call ID.

    A raw tool edit joins a current accepted 017 observation: a read
    (``outcome`` COMPLETE, the same endpoint domain) for a whole
    read-surface piece, a PARTITIONED read-surface piece through the
    ACTUAL current 018-b bundle-proof bridge proof for the same
    original call ID (the bare current 017 read never proves an inner
    compound boundary; the bridge must agree on the endpoint and the
    command digest), or a process chain (``outcome`` COMPLETE, the
    same endpoint domain; the initial piece via the exec call, a poll
    piece via its own poll call) for a process-surface piece.
    Returns the current ``(call_location, result_location)`` or
    ``None`` when no accepted current observation or bridge proof
    earns the piece (absent from the payload, re-sent in the other
    endpoint domain, or a nonzero / truncated / partial / unsupported
    current wrapper): retained proof and matching bytes alone never
    earn deletion."""
    if proof.surface is BundleSurface.READ:
        if proof.kind is BundleProofKind.PARTITIONED:
            bridge = bridge_by_call.get(piece.call_id)
            if (
                bridge is None
                or bridge.kind is not BundleProofKind.PARTITIONED
                or bridge.endpoint != proof.endpoint
                or bridge.command_digest != proof.command_digest
            ):
                return None
            return bridge.call_location, bridge.result_location
        read = index.reads_by_call.get(piece.call_id)
        if read is None or read.endpoint != proof.endpoint:
            return None
        if read.outcome is not ReadOutcome.COMPLETE:
            return None
        return read.call_location, read.result_location
    process = index.processes_by_exec_call.get(proof.call_id)
    if process is None or process.endpoint != proof.endpoint:
        return None
    if process.outcome is not ProcessOutcome.COMPLETE:
        return None
    if piece.call_id == proof.call_id:
        return process.exec_call_location, process.initial_result_location
    for poll in process.polls:
        if poll.poll_call_id == piece.call_id:
            return poll.poll_call_location, poll.result_location
    return None


def _current_piece_subspan(
    proof: BundleProof,
    piece: BundlePiece,
    piece_index: int,
    segment: BundleSegment,
    index: _CurrentReadIndex,
    bridge_by_call: dict[str, BundleProof],
) -> CharSpan | None:
    """The ACTUAL current in-carrier sub-span of ONE retained
    piece/segment (the join's current coordinates).

    Every surface re-derives the position from the CURRENT accepted
    proof on the CURRENT decoded string: the process surface from the
    current process observation's own per-piece sub-span (matched by
    the SAME original piece call identity — the retained coordinates
    stay the piece's identity, never its position; a shifted or
    re-parsed current frame leaves the piece uncovered), a whole read
    from the current accepted read's own content span, and a
    partitioned read from the current 018-b bridge segment (the same
    segment index and member positions) per-piece span.  ``None``
    means no current coverage: the piece leaves the segment unproven
    (the zero-edit law is unchanged)."""
    if proof.surface is not BundleSurface.READ:
        process = index.processes_by_exec_call.get(proof.call_id)
        if process is None or process.outcome is not ProcessOutcome.COMPLETE:
            return None
        if piece.call_id == proof.call_id:
            current = next(
                (p for p in process.pieces if p.result_location == process.initial_result_location),
                None,
            )
        else:
            current = next(
                (poll.piece for poll in process.polls if poll.poll_call_id == piece.call_id),
                None,
            )
        if current is None or current.piece_index != piece_index:
            return None
        return current.char_span
    if proof.kind is BundleProofKind.WHOLE:
        read = index.reads_by_call.get(piece.call_id)
        if read is None:
            return None
        return read.content_span
    bridge = bridge_by_call.get(piece.call_id)
    if bridge is None:
        return None
    for bridge_segment in bridge.segments:
        if (
            bridge_segment.index == segment.index
            and bridge_segment.member_positions == segment.member_positions
        ):
            if piece_index >= len(bridge_segment.piece_spans):
                return None
            return bridge_segment.piece_spans[piece_index]
    return None


def _verify_result_call_id(
    payload: dict[str, Any],
    endpoint: str,
    location: str,
    expected_call_id: str,
) -> None:
    """Re-prove the RESULT record's own call ID against the SAME
    original piece call ID (the 017 paired-read law, result side).

    Responses: the ``function_call_output`` item's ``call_id``; Chat:
    the ``role="tool"`` message's ``tool_call_id``.  The carrier shape
    was already earned by the read-only lookup; this check closes the
    pairing: a missing, non-string, empty or diverging result ID
    leaves the ORIGINAL paired association (fixed IDENTITY_MISMATCH
    refusal; constant-time comparison; no ID value is echoed)."""
    if endpoint == ENDPOINT_RESPONSES:
        m = _RESPONSES_ITEM_RE.match(location)
        if m is None:
            raise _refuse(CarrierDetail.IDENTITY_MISMATCH)
        index = _canonical_index(m.group(1))
        if index is None:
            raise _refuse(CarrierDetail.IDENTITY_MISMATCH)
        container = payload.get("input")
        if not isinstance(container, list) or not (0 <= index < len(container)):
            raise _refuse(CarrierDetail.IDENTITY_MISMATCH)
        item = container[index]
        call_id = item.get("call_id") if isinstance(item, dict) else None
    else:
        m = _CHAT_MESSAGE_RE.match(location)
        if m is None:
            raise _refuse(CarrierDetail.IDENTITY_MISMATCH)
        index = _canonical_index(m.group(1))
        if index is None:
            raise _refuse(CarrierDetail.IDENTITY_MISMATCH)
        container = payload.get("messages")
        if not isinstance(container, list) or not (0 <= index < len(container)):
            raise _refuse(CarrierDetail.IDENTITY_MISMATCH)
        message = container[index]
        call_id = message.get("tool_call_id") if isinstance(message, dict) else None
    if not isinstance(call_id, str) or call_id == "":
        raise _refuse(CarrierDetail.IDENTITY_MISMATCH)
    if not hmac.compare_digest(call_id.encode("utf-8"), expected_call_id.encode("utf-8")):
        raise _refuse(CarrierDetail.IDENTITY_MISMATCH)


def _join_segment_spans(
    payload: dict[str, Any],
    proof: BundleProof,
    segment_index: int,
    *,
    max_text_chars: int,
    content_key: str,
    entry_class_value: str,
    role: str,
    occurrence_identity: str,
    root_digest: str | None,
    index: _CurrentReadIndex,
    bridge_by_call: dict[str, BundleProof],
    results_by_call: dict[str, ResultFingerprintRecord],
    history_bounds: HistoryBounds,
    historical: bool = False,
) -> tuple[RetainedSpan, ...]:
    """Join ONE retained original segment of ONE owner proof to its
    ACTUAL current carrier pieces (the shared per-segment join of
    the retained/current proof law).

    ``root_digest``, when supplied (a governing root selected through
    a read), must equal the digest of the governing segment and is
    the span's ``source_digest``.  A segment index that leaves the
    owner proof's segments is a spliced / detached retained record
    (refused all-or-nothing).  A well-formed carrier or call that is
    ABSENT from the current payload earns no edit for its spans (no
    refusal); every other carrier-layer refusal propagates.  The
    segment re-proof runs over ALL pieces the segment overlaps (one
    absent piece carrier leaves the segment unproven, never
    partially proven).  Each resolved piece carrier is ALSO re-proven
    on the result side: the result record's own call ID (the
    Responses ``call_id`` / the Chat ``tool_call_id``) must equal the
    SAME original piece call ID (a divergence is refused
    all-or-nothing).  A segment whose every overlapping piece carrier
    is GENUINELY ABSENT from the current payload earns ZERO edits (no
    refusal): a source-absent replay can still return the exact
    selected context.  A segment that overlaps no carrier piece at
    all is a malformed retained coordinate.  Each piece re-joins its
    ACTUAL current carrier through the CURRENT accepted 017
    observation bound to the SAME original call ID (the current read
    or process chain, outcome COMPLETE, same endpoint domain): a
    piece with no accepted current observation (absent, cross-domain,
    or a nonzero / truncated / partial / unsupported current wrapper)
    earns zero edits for its spans — retained proof and matching
    bytes alone never earn deletion.  A PARTITIONED read-surface
    piece re-joins instead through the ACTUAL current 018-b
    bundle-proof bridge (the bare current 017 read never proves an
    inner compound boundary).  Every piece's current call is also
    re-verified as the ACTUAL original tool identity: the retained D
    result record's per-piece producing-call binding (tool name plus
    canonical argument fingerprint) must equal the current call's
    (a reused call ID under a different command is refused
    IDENTITY_MISMATCH, never an edit).

    ``historical`` marks a span joined through the
    positive-supersession phase (a retained-D nonroot occurrence
    ABSENT from the current admission): its ``content_key`` is the
    retained segment's source digest — the old entry key is never
    reconstructed."""
    if segment_index >= len(proof.segments):
        raise _refuse(CarrierDetail.RETAINED_RECORD_MALFORMED)
    segment = proof.segments[segment_index]
    if root_digest is not None and segment.digest != root_digest:
        raise _refuse(CarrierDetail.RETAINED_RECORD_MALFORMED)
    resolved: list[tuple[BundlePiece, CharSpan, str, str]] = []
    complete = True
    overlapping = 0
    for piece_index, sub in enumerate(segment.piece_spans):
        if sub is None:
            continue
        overlapping += 1
        if piece_index >= len(proof.pieces):
            raise _refuse(CarrierDetail.RETAINED_RECORD_MALFORMED)
        piece = proof.pieces[piece_index]
        carriers = _current_piece_carriers(proof, piece, index, bridge_by_call)
        if carriers is None:
            # No ACCEPTED current 017 observation earns this
            # piece: zero edits for the span, no refusal (a
            # matching-bytes retention on a nonzero / truncated
            # wrapper is never a deletion).
            complete = False
            continue
        call_location, result_location = carriers
        try:
            slot = lookup_tool_result_carrier(
                payload,
                proof.endpoint,
                result_location,
                max_text_chars=max_text_chars,
            )
        except _ReplaceRefusal as refusal:
            if refusal.detail is CarrierDetail.CARRIER_NOT_FOUND:
                complete = False
                continue
            raise
        _verify_result_call_id(payload, proof.endpoint, result_location, piece.call_id)
        try:
            identity = lookup_call_identity(
                payload,
                proof.endpoint,
                call_location,
                expected_call_id=piece.call_id,
            )
        except _ReplaceRefusal as refusal:
            if refusal.detail is CarrierDetail.CALL_NOT_FOUND:
                complete = False
                continue
            raise
        _verify_call_binding(identity, proof.call_id, piece_index, results_by_call, history_bounds)
        cur = _current_piece_subspan(proof, piece, piece_index, segment, index, bridge_by_call)
        if cur is None:
            # No CURRENT coverage of this piece in the segment:
            # the segment stays unproven (zero-edit law below).
            complete = False
            continue
        resolved.append((piece, cur, slot.text, result_location))
    if not resolved:
        if overlapping == 0:
            # A segment that overlaps NO carrier piece at all is a
            # malformed retained coordinate (an empty segment keeps
            # its real zero-width carrier span, never all-None).
            raise _refuse(CarrierDetail.RETAINED_RECORD_MALFORMED)
        # Genuinely absent carriers: the original pieces are no
        # longer carried by the current payload (compaction). The
        # segment earns ZERO edits — no refusal — so a
        # source-absent replay can still return the exact
        # selected context.
        return ()
    reproven = False
    bytes_mismatch = False
    if complete:
        joined_text = "".join(
            text[cur.start : cur.end] for _piece, cur, text, _location in resolved
        )
        joined_bytes = joined_text.encode("utf-8")
        reproven = (
            len(joined_text) == segment.char_length
            and len(joined_bytes) == segment.byte_length
            and hmac.compare_digest(hashlib.sha256(joined_bytes).hexdigest(), segment.digest)
        )
    bytes_mismatch = complete and not reproven
    spans: list[RetainedSpan] = []
    for piece, cur, _text, result_location in resolved:
        spans.append(
            RetainedSpan(
                content_key=content_key,
                entry_class=entry_class_value,
                role=role,
                endpoint=proof.endpoint,
                occurrence_identity=occurrence_identity,
                call_id=piece.call_id,
                call_position=piece.call_position,
                result_position=piece.result_position,
                piece_index=piece.piece_index,
                segment_index=segment_index,
                location=result_location,
                field="output" if proof.endpoint == ENDPOINT_RESPONSES else "content",
                start=cur.start,
                end=cur.end,
                source_digest=root_digest if root_digest is not None else segment.digest,
                reproven=reproven,
                bytes_mismatch=bytes_mismatch,
                historical=historical,
            )
        )
    return tuple(spans)


def _join_file_witness(
    payload: dict[str, Any],
    proof: BundleProof,
    witness: CurrentAdmissionWitness,
    *,
    max_text_chars: int,
    content_key: str,
    entry_class_value: str,
    role: str,
    occurrence_identity: str,
    root_digest: str | None,
    index: _CurrentReadIndex,
    bridge_by_call: dict[str, BundleProof],
    results_by_call: dict[str, ResultFingerprintRecord],
    history_bounds: HistoryBounds,
) -> tuple[RetainedSpan, ...]:
    """Join ONE retained witness of ONE entry through ITS OWN owner
    proof (the per-segment carrier law lives in
    ``_join_segment_spans`` and is inherited unchanged).

    ``root_digest``, when supplied (a governing root selected through
    a read), must equal the digest of every governing segment and is
    the span's ``source_digest``.  A witness whose original
    coordinates leave the owner proof's (request index / call
    position / result position) is a spliced / detached retained
    record (refused all-or-nothing) BEFORE any segment work; a
    segment index the witness leaves its owner proof's segments is
    refused by the per-segment join."""
    if (
        proof.request_index != witness.request_index
        or proof.call_position != witness.call_position
        or proof.result_position != witness.result_position
    ):
        raise _refuse(CarrierDetail.RETAINED_RECORD_MALFORMED)
    spans: list[RetainedSpan] = []
    for segment_index in witness.segment_indices:
        spans.extend(
            _join_segment_spans(
                payload,
                proof,
                segment_index,
                max_text_chars=max_text_chars,
                content_key=content_key,
                entry_class_value=entry_class_value,
                role=role,
                occurrence_identity=occurrence_identity,
                root_digest=root_digest,
                index=index,
                bridge_by_call=bridge_by_call,
                results_by_call=results_by_call,
                history_bounds=history_bounds,
            )
        )
    return tuple(spans)


def _join_superseded_occurrence(
    payload: dict[str, Any],
    owner: CompletedReadOccurrence,
    segment_indices: tuple[int, ...],
    *,
    max_text_chars: int,
    index: _CurrentReadIndex,
    bridge_by_call: dict[str, BundleProof],
    results_by_call: dict[str, ResultFingerprintRecord],
    history_bounds: HistoryBounds,
) -> tuple[RetainedSpan, ...]:
    """Join ONE retained-D nonroot occurrence that is ABSENT from the
    current admission (a known positively superseded original, proven
    by the prepared T result's same-run E overlay group facts)
    through the SAME per-segment carrier join.

    The consistency anchor is the retained D record itself (no
    admission witness exists to fabricate against): the
    occurrence's issuance identity must agree with its verbatim
    retained proof (a spliced or detached record refuses
    RETAINED_RECORD_MALFORMED all-or-nothing) and every named
    segment must exist in that proof.  The span's content identity is
    the retained segment's OWN source digest — the old entry key is
    never reconstructed — under the closed file-bundle entry class
    and the tool-result carrier role (its carrier stays a tool
    result, exactly as an admitted file witness).  The carrier-layer
    law is inherited unchanged from ``_join_segment_spans`` (a
    genuinely absent carrier earns zero edits; every other refusal
    propagates)."""
    proof = owner.proof
    if owner.call_id != proof.call_id or owner.endpoint != proof.endpoint:
        raise _refuse(CarrierDetail.RETAINED_RECORD_MALFORMED)
    if any(s >= len(proof.segments) for s in segment_indices):
        raise _refuse(CarrierDetail.RETAINED_RECORD_MALFORMED)
    spans: list[RetainedSpan] = []
    for segment_index in segment_indices:
        segment = proof.segments[segment_index]
        spans.extend(
            _join_segment_spans(
                payload,
                proof,
                segment_index,
                max_text_chars=max_text_chars,
                content_key=segment.digest,
                entry_class_value=EntryClass.FILE_BUNDLE_ENTRY.value,
                role=_TOOL_RESULT_ROLE,
                occurrence_identity=owner.occurrence_id,
                root_digest=None,
                index=index,
                bridge_by_call=bridge_by_call,
                results_by_call=results_by_call,
                history_bounds=history_bounds,
                historical=True,
            )
        )
    return tuple(spans)


def _join_envelope_root_span(
    spans: list[RetainedSpan],
    payload: dict[str, Any],
    occurrence: RootOccurrence,
    *,
    root_entry: Any,
    root_key: str,
    workspace: str,
    max_text_chars: int,
) -> None:
    """Join ONE accepted envelope-root occurrence to its own
    current carrier (the repeated-envelope join: byte- and
    scope-identical envelopes each earn their own span — one per
    carrier — and the working set still holds the single root
    entry).

    The original retained root digest is the join's proof.  A
    digest or length mismatch is the TRANSFORMED carrier — the
    envelope already carries the accepted marker where the original
    source was — and the re-join proves carrier shape and span
    bounds only (no expected digest) so the raw mismatch cannot
    refuse before the replay scan matches the valid tag at the
    splice start.  A genuinely absent carrier earns zero edits and
    no refusal (a source-absent replay); every other refusal
    propagates all-or-nothing."""
    transformed = False
    try:
        slot, facts = join_root_occurrence(
            payload,
            occurrence,
            expected_digest=root_entry.root_digest,
            expected_workspace=workspace,
            max_text_chars=max_text_chars,
        )
    except _ReplaceRefusal as refusal:
        if refusal.detail is not CarrierDetail.CARRIER_NOT_FOUND:
            if refusal.detail not in (
                CarrierDetail.SPAN_DIGEST_MISMATCH,
                CarrierDetail.SPAN_LENGTH_MISMATCH,
            ):
                raise
            slot, facts = join_root_occurrence(
                payload,
                occurrence,
                expected_digest=None,
                expected_workspace=workspace,
                max_text_chars=max_text_chars,
            )
            transformed = True
        else:
            return
    spans.append(
        RetainedSpan(
            content_key=root_key,
            entry_class=root_entry.entry_class.value,
            role=_ROOT_ENVELOPE_ROLE,
            endpoint=ENDPOINT_RESPONSES,
            occurrence_identity=root_key,
            call_id="",
            call_position=0,
            result_position=0,
            piece_index=0,
            segment_index=0,
            location=slot.location,
            field=slot.field,
            start=facts.start,
            end=facts.end,
            source_digest=root_entry.root_digest,
            reproven=not transformed,
            bytes_mismatch=transformed,
        )
    )


def _join_historical_root_envelopes(
    spans: list[RetainedSpan],
    payload: dict[str, Any],
    observation: ObservationReport,
    *,
    snapshot: RamStateSnapshot,
    root_entry: Any,
    root_key: str,
    evidence: _SupersessionEvidence,
    historical_root_tags: dict[str, ExpectedTag],
    max_text_chars: int,
) -> None:
    """Join each ACTUAL accepted same-scope (ROOT, OK) root occurrence
    whose digest is an ACTUAL AUTHORITATIVE root fact of the
    same-run P state (the bootstrap anchor or an issued fact — a
    retained unissued digest is insufficient) DIFFERENT from the
    governing root digest (the historical old-root anchor — the
    order's evidence law: a known positively superseded root
    original retained in history).

    The anchor earns its NON-RESOLVING evidence splice through the
    historical raw re-join: the original retained OLD digest is the
    join's proof (re-proven against the old bytes at the anchor's own
    content span), and the span's ``source_digest`` is that OLD
    digest with ``historical`` set — the caller classifies it
    through ``_root_span_superseded`` (the actual P/Q lineage) and it
    earns an EVIDENCE edit, never a live reference.  A drifted
    anchor (already transformed) re-joins shape-only (no expected
    digest) so the replay scan decides by tag at the splice start; a
    genuinely absent carrier earns zero edits and no refusal (the
    source-absent law).  The scope law applies before any join work:
    a foreign-workspace anchor claiming a retained old digest is the
    existing scope conflict (all-or-nothing).  The CURRENT envelope
    of the governing digest is NOT joined here — in the
    read/read_region case the read splice is the root's only live
    edit and the current envelope stays separate and untouched.
    Every other refusal propagates all-or-nothing.

    Drifted-anchor law (the already-transformed historical replay):
    an accepted occurrence whose digest is neither the governing
    digest nor a retained old digest is the ALREADY TRANSFORMED old
    anchor (its content span now carries the marker, not the old
    bytes).  It re-joins shape-only, and the marker candidate at its
    ORIGINAL splice start is re-authenticated by MAC against
    ``historical_root_tags`` (the prepared transaction's candidate
    evidence tag per authoritative old digest — the tag identity is
    the OLD source's own digest, so later root changes re-derive the
    same tag — computed by the caller which alone holds the marker
    key): an ``ok`` match on exactly one
    candidate is the anchor's own non-resolving evidence replay — a
    historical span (that candidate's source digest, ``reproven``
    False) that the replay scan accepts without a second edit.  A
    marker matching NO candidate (a stale live form, a forged or
    foreign tag, or a tampered one) or a drifted carrier with no
    marker at the splice start earns the fail-closed shape-only span
    (governing digest, ``historical`` False, ``reproven`` False): the
    recognized source field then refuses all-or-nothing (the marker
    layer's stale/forged refusal, or the selected-span raw gate).
    """
    workspace = snapshot.namespace.workspace
    for occ in observation.roots.roots:
        if occ.kind is not OccurrenceKind.ROOT or occ.status is not RootStatus.OK:
            continue
        if occ.digest == root_entry.root_digest:
            continue  # the current envelope: separate, never joined here
        _root_scope_check(occ, workspace)
        transformed = False
        raw_anchor = occ.digest in evidence.authoritative_root_digests
        try:
            slot, facts = join_root_occurrence(
                payload,
                occ,
                expected_digest=occ.digest if raw_anchor else None,
                expected_workspace=workspace,
                max_text_chars=max_text_chars,
            )
        except _ReplaceRefusal as refusal:
            if refusal.detail is not CarrierDetail.CARRIER_NOT_FOUND:
                if refusal.detail not in (
                    CarrierDetail.SPAN_DIGEST_MISMATCH,
                    CarrierDetail.SPAN_LENGTH_MISMATCH,
                ):
                    raise
                slot, facts = join_root_occurrence(
                    payload,
                    occ,
                    expected_digest=None,
                    expected_workspace=workspace,
                    max_text_chars=max_text_chars,
                )
                transformed = True
            else:
                continue
        occ_digest = occ.digest
        if raw_anchor:
            if occ_digest is None:
                # Membership in the authoritative digest set
                # implies an exact digest; fail closed on the
                # impossible shape.
                raise _refuse(CarrierDetail.RETAINED_RECORD_MALFORMED)
            source_digest = occ_digest
        else:
            source_digest = root_entry.root_digest
        historical = raw_anchor
        if not raw_anchor:
            # The already-transformed anchor: re-authenticate the
            # marker at the ORIGINAL splice start by MAC against the
            # prepared candidate evidence tags (exactly one ok match
            # is the anchor's own non-resolving evidence replay).
            candidate = next(
                (c for s, c in find_markers(slot.text) if s == facts.start),
                None,
            )
            if candidate is not None:
                verdict = verify_marker(
                    candidate,
                    facts.start,
                    expectations=MarkerExpectations(tuple(historical_root_tags.values())),
                )
                if verdict.reason == "ok" and verdict.source_digest is not None:
                    source_digest = verdict.source_digest
                    historical = True
                # A non-ok verdict (stale live form, forged,
                # tampered, unknown kind, malformed) keeps the
                # fail-closed span below: the recognized source
                # field refuses all-or-nothing at the marker layer.
        spans.append(
            RetainedSpan(
                content_key=root_key,
                entry_class=root_entry.entry_class.value,
                role=_ROOT_ENVELOPE_ROLE,
                endpoint=ENDPOINT_RESPONSES,
                # The evidence identity is the OLD source's own
                # digest in the trusted namespace workspace
                # (immutable across later root changes), never the
                # current root entry key.
                occurrence_identity=source_digest,
                call_id="",
                call_position=0,
                result_position=0,
                piece_index=0,
                segment_index=0,
                location=slot.location,
                field=slot.field,
                start=facts.start,
                end=facts.end,
                source_digest=source_digest,
                reproven=not transformed,
                bytes_mismatch=transformed,
                historical=historical,
            )
        )


def _join_historical_read_roots(
    spans: list[RetainedSpan],
    payload: dict[str, Any],
    *,
    snapshot: RamStateSnapshot,
    owners: dict[str, CompletedReadOccurrence],
    root_entry: Any,
    root_read_coords: set[tuple[str, int]],
    index: _CurrentReadIndex,
    bridge_by_call: dict[str, BundleProof],
    results_by_call: dict[str, ResultFingerprintRecord],
    max_text_chars: int,
    history_bounds: HistoryBounds,
) -> None:
    """Join each ACTUAL retained authoritative read/read_region root
    fact DIFFERENT from the governing root digest (the superseded
    authoritative whole-root read / root region -- the 022-c
    section-1 evidence law, the read half of the historical old-root
    anchor law the envelope join covers).

    The facts are enumerated SEPARATELY from the E nonroot groups:
    the same-run P state of the prepared snapshot is the only source,
    and only ACTUAL authoritative facts qualify (the bootstrap
    anchor or an issued fact -- a retained unissued digest is never
    authority and never proves supersession).  The envelope fact is
    the separate envelope anchor, and the governing fact's own
    digest is the current read splice, never a historical join.

    Each fact's exact original occurrence and whole/region segment
    are resolved from the fact's OWN provenance against the SAME
    retained D owner (the consistency anchor -- a spliced or
    detached record refuses all-or-nothing), and a mixed or
    boundaryless read never proves the complete root source (the
    governing join's exact shape law, mirrored).  The span's content
    identity is the OLD source's own digest in the trusted namespace
    (the immutable evidence identity -- the old entry key is never
    reconstructed and the current root entry key never replaces
    it), under the root entry class and the tool-result carrier
    role (the carrier stays a tool result, exactly as the governing
    read splice).  The per-piece carrier law is inherited unchanged
    from ``_join_segment_spans``: a genuinely absent carrier earns
    zero edits (the source-absent law), and a drifted -- already
    transformed -- carrier re-joins through the current content
    span so the replay scan decides by tag at the splice start.
    Each joined coordinate enters ``root_read_coords`` so the same
    root-region bytes can never earn a second edit (the FILE
    witness join and the nonroot positive-supersession phase both
    skip it).
    """
    for fact in snapshot.state.root_facts:
        if not fact.authority:
            continue
        provenance = fact.provenance
        if provenance.kind not in ("read", "read_region"):
            continue
        if fact.source_digest == root_entry.root_digest:
            continue
        occurrence_id = provenance.occurrence_id
        owner = owners.get(occurrence_id)
        if owner is None:
            raise _refuse(CarrierDetail.CARRIER_UNRESOLVED)
        proof = owner.proof
        if isinstance(provenance, ReadRootProvenance):
            # A complete whole singleton: the root member IS the
            # proof's one attributable segment (a boundaryless or
            # multi-member aggregate never proves the complete
            # root source).
            if len(proof.segments) != 1:
                raise _refuse(CarrierDetail.RETAINED_RECORD_MALFORMED)
            segment = proof.segments[0]
            if segment.member_digest != fact.source_digest:
                raise _refuse(CarrierDetail.RETAINED_RECORD_MALFORMED)
            segment_index = segment.index
        else:  # read_region (the kind filter above fences the class)
            if not isinstance(provenance, RootRegionReadProvenance):
                raise AssertionError("unreachable: closed provenance kinds")
            segment_index = provenance.root_segment_index
            if segment_index >= len(proof.segments):
                raise _refuse(CarrierDetail.RETAINED_RECORD_MALFORMED)
            segment = proof.segments[segment_index]
            # The region segment must own exactly the single
            # attributable root member at its proven position (a
            # boundaryless multi-member group leaves the root
            # region's internal boundary unproven; fail closed,
            # never a partial splice).
            if (
                segment.member_digest != fact.source_digest
                or len(segment.member_positions) != 1
                or segment.member_positions[0] != provenance.root_member_position
            ):
                raise _refuse(CarrierDetail.RETAINED_RECORD_MALFORMED)
        spans.extend(
            _join_segment_spans(
                payload,
                proof,
                segment_index,
                max_text_chars=max_text_chars,
                content_key=fact.source_digest,
                entry_class_value=root_entry.entry_class.value,
                role=_TOOL_RESULT_ROLE,
                occurrence_identity=occurrence_id,
                root_digest=fact.source_digest,
                index=index,
                bridge_by_call=bridge_by_call,
                results_by_call=results_by_call,
                history_bounds=history_bounds,
                historical=True,
            )
        )
        root_read_coords.add((occurrence_id, segment_index))


def join_retained_proof(
    payload: dict[str, Any],
    *,
    snapshot: RamStateSnapshot,
    decision: BundleSelectionDecision,
    observation: ObservationReport,
    root_occurrence: RootOccurrence | None,
    max_text_chars: int,
    evidence: _SupersessionEvidence,
    historical_root_tags: dict[str, ExpectedTag],
) -> tuple[RetainedSpan, ...]:
    """Join every retained entry's exact original source spans to the
    ACTUAL current payload (the transaction's trusted carrier
    binding).

    The retained record set is read from ``snapshot`` by immutable
    reference: the actual 018-t admission (its root entry and FILE
    entries with their ORIGINAL witnesses) and the retained original
    occurrence owners in the D state.  The accepted 017
    ``root_occurrence`` (``kind`` ROOT, ``status`` OK, from the
    actual observation of THIS payload) names the payload's
    governing envelope root.  The join coordinates come from the
    observation's ACTUAL accepted occurrences: repeated byte- and
    scope-identical envelopes of the same root are each joined to
    their own carrier and earn their own span (the working set still
    holds the single root entry), and a named location the
    observation does not accept refuses CARRIER_UNRESOLVED
    all-or-nothing.  Every admitted FILE entry is joined — selected,
    omitted and merely retained alike — because a stale live
    reference or an evidence marker may be earned by any of them; the
    caller classifies each span against the accepted selection.
    The root join dispatches on the ACTUAL retained root provenance
    (``root_entry.root_source.kind``): the T root row's ``witnesses``
    stay empty on EVERY provenance (the read provenance lives in the
    resolved source) and are never the dispatch.  An ENVELOPE root
    earns its content span on EACH accepted occurrence (each
    repeated envelope its own carrier, each with its own edit; the
    envelope text is otherwise never edited).  A governing root
    selected through a READ or READ_REGION keeps its carrier a tool
    result with the tool-result carrier role and joins the resolved
    source's ACTUAL original occurrence/proof at its own retained
    coordinates (the read's one attributable complete-singleton
    segment; the region provenance's root segment fenced to the
    single attributable member that IS the governing root digest) —
    that exact (occurrence, segment) coordinate is then skipped by
    the FILE join below so the same root-region bytes can never earn
    a second edit, while a shared entry's other distinct original
    coordinates still join through their own witnesses.
    In the read/read_region case the HISTORICAL old-root anchor is
    joined too: an accepted same-scope root occurrence whose digest
    is an ACTUAL retained root fact DIFFERENT from the governing
    root digest (a known positively superseded root original per the
    order's evidence law) earns its non-resolving evidence splice
    through the historical raw re-join (re-proven against the OLD
    bytes; a drifted — already transformed — anchor re-joins
    shape-only so the replay scan decides by tag), while the
    current envelope of the governing digest stays separate and
    untouched.
    The SUPERSEDED AUTHORITATIVE WHOLE-ROOT READ / ROOT REGION is
    joined the same way through its own retained record: every
    ACTUAL authoritative read/read_region root fact of the same-run
    P state DIFFERENT from the governing root digest is enumerated
    (separately from the E nonroot groups) and re-joins its exact
    original occurrence and whole/region segment through
    ``_join_historical_read_roots`` — historical, tool-result
    carrier role, the OLD source digest as content identity (the
    old entry key is never reconstructed) — and each joined
    coordinate is fenced out of the FILE join so the same
    root-region bytes can never earn a second edit.
    ``historical_root_tags`` are the prepared transaction's
    candidate evidence tags for the drifted-anchor re-authentication
    (one per retained old digest, keyed by that digest; computed by
    the caller, which alone holds the marker key).

    The POSITIVE-SUPERSESSION phase then joins the retained-D
    NONROOT originals ABSENT from the current admission: for each
    group record of the prepared T result's SAME-RUN E overlay
    (``evidence``) that positively proves supersession at an
    (occurrence, group) coordinate the admission carries no witness
    for (``proven_change`` on a path row, no
    ``known_content_conflict`` / ``ownership_ambiguity`` blocker),
    the ACTUAL retained D occurrence is joined through
    ``_join_superseded_occurrence`` — the group index IS the
    occurrence-local segment index, and the span's content identity
    is the retained segment's source digest (the old entry key is
    never reconstructed).  A coordinate covered by any current
    admission witness (root or file) stays with the admission join
    above; a group record with no retained occurrence is detached
    (refused all-or-nothing); an absent overlay proves nothing.

    ``observation`` is the ACTUAL 017 observation of THIS payload and
    is the raw-tool edit bridge: every retained tool piece re-joins
    its ACTUAL current carrier through the current accepted
    read/process observation bound to the SAME original call ID
    (outcome COMPLETE, same endpoint domain).  A governing envelope
    root that is absent from the payload (no accepted root occurrence
    or no root carrier) earns ZERO edits, not a refusal: a
    source-absent replay still returns the exact selected context.

    Raises ``_ReplaceRefusal`` with the fixed detail:
    CARRIER_UNRESOLVED (no usable admission, a detached witness
    owner), RETAINED_RECORD_MALFORMED (a retained coordinate
    leaves its owner occurrence or segment) and the carrier-layer
    details of an EXISTING carrier that leaves the accepted shape
    (all-or-nothing); a well-formed absent carrier or call earns no
    edit and no refusal (a segment whose every overlapping piece
    carrier is genuinely absent earns zero edits)."""
    if max_text_chars < 1:
        raise ValueError("max_text_chars must be positive")
    admission = snapshot.result.admission
    if admission is None:
        raise _refuse(CarrierDetail.CARRIER_UNRESOLVED)
    owners = {o.occurrence_id: o for o in snapshot.state.d_state.occurrences}
    index = _current_read_index(observation)
    bridge_by_call = _current_bridge_proofs(payload, observation, snapshot)
    results_by_call = {record.call_id: record for record in snapshot.state.d_state.results}
    working_keys = {w.content_key for w in decision.working_set}
    spans: list[RetainedSpan] = []
    root_entry = admission.root_entry
    root_key = root_entry.content_key
    # The T root row's ``witnesses`` stay empty on every provenance
    # (the read provenance lives in the resolved source), so the root
    # join dispatches on the ACTUAL retained root provenance kind.
    root_read_coords: set[tuple[str, int]] = set()
    if root_key in working_keys:
        root_source = root_entry.root_source
        if root_source is None:
            raise _refuse(CarrierDetail.CARRIER_UNRESOLVED)
        if root_source.kind == "envelope":
            if root_occurrence is not None:
                # The repeated-root join is scoped: EVERY accepted root
                # occurrence in this payload must carry the prepared
                # trusted namespace workspace (its ACTUAL scope label); a
                # same-shaped foreign-workspace envelope is the existing
                # scope conflict, never an edit or an accepted marker,
                # even when its bytes are identical.
                accepted = [
                    o
                    for o in observation.roots.roots
                    if o.kind is OccurrenceKind.ROOT and o.status is RootStatus.OK
                ]
                for occ in accepted:
                    _root_scope_check(occ, snapshot.namespace.workspace)
                # Repeated byte- and scope-identical envelopes of the same
                # root are idempotent: each ACTUAL accepted occurrence is
                # joined to its own carrier and earns its own span and
                # edit, while the working set still holds the ONE root
                # entry.  The caller names THIS payload's governing
                # envelope root; a named location the observation does not
                # accept is a stale or foreign assertion and fails closed
                # (all-or-nothing).
                if accepted:
                    if root_occurrence.location not in {o.location for o in accepted}:
                        raise _refuse(CarrierDetail.CARRIER_UNRESOLVED)
                    join_occurrences = accepted
                else:
                    # A source-absent replay: the observation reports no
                    # accepted root occurrence (the named carrier is
                    # gone); the join earns zero edits, no refusal, and
                    # the exact selected context is still returned.
                    join_occurrences = [root_occurrence]
                for occ in join_occurrences:
                    _join_envelope_root_span(
                        spans,
                        payload,
                        occ,
                        root_entry=root_entry,
                        root_key=root_key,
                        workspace=snapshot.namespace.workspace,
                        max_text_chars=max_text_chars,
                    )
        else:
            # A governing root selected through a READ or READ_REGION:
            # the root's OWN retained original witness is the splice —
            # its carrier stays a tool result with the tool-result
            # carrier role, and the root authority stays bound by the
            # entry class and the governing root digest.  The join is
            # from the resolved source's ACTUAL original occurrence/
            # proof (the retained D owner, by identity) at its own
            # retained segment coordinate; the historical envelope is
            # a separate concern and is not joined here.
            occurrence = root_source.occurrence
            if occurrence is None or root_source.proof is None:
                raise _refuse(CarrierDetail.RETAINED_RECORD_MALFORMED)
            owner = owners.get(occurrence.occurrence_id)
            if owner is None:
                raise _refuse(CarrierDetail.CARRIER_UNRESOLVED)
            proof = owner.proof
            if proof is not root_source.proof:
                raise _refuse(CarrierDetail.RETAINED_RECORD_MALFORMED)
            if root_source.kind == "read":
                # A complete whole singleton: the root member IS the
                # proof's one attributable segment (a boundaryless or
                # multi-member aggregate never proves the complete
                # root source).
                if len(proof.segments) != 1:
                    raise _refuse(CarrierDetail.RETAINED_RECORD_MALFORMED)
                segment = proof.segments[0]
                if segment.member_digest != root_entry.root_digest:
                    raise _refuse(CarrierDetail.RETAINED_RECORD_MALFORMED)
                segment_index = segment.index
            else:  # read_region
                provenance = root_source.fact.provenance
                if not isinstance(provenance, RootRegionReadProvenance):
                    raise _refuse(CarrierDetail.RETAINED_RECORD_MALFORMED)
                segment_index = provenance.root_segment_index
                if segment_index >= len(proof.segments):
                    raise _refuse(CarrierDetail.RETAINED_RECORD_MALFORMED)
                segment = proof.segments[segment_index]
                # The region segment must own exactly the single
                # attributable root member (its digest IS the
                # governing root digest, at its proven member
                # position); a boundaryless multi-member group leaves
                # the root region's internal boundary unproven (fail
                # closed, never a partial splice).
                if (
                    segment.member_digest != root_entry.root_digest
                    or len(segment.member_positions) != 1
                    or segment.member_positions[0] != provenance.root_member_position
                ):
                    raise _refuse(CarrierDetail.RETAINED_RECORD_MALFORMED)
            root_read_coords = {(occurrence.occurrence_id, segment_index)}
            spans.extend(
                _join_segment_spans(
                    payload,
                    proof,
                    segment_index,
                    max_text_chars=max_text_chars,
                    content_key=root_key,
                    entry_class_value=root_entry.entry_class.value,
                    role=_TOOL_RESULT_ROLE,
                    occurrence_identity=occurrence.occurrence_id,
                    root_digest=root_entry.root_digest,
                    index=index,
                    bridge_by_call=bridge_by_call,
                    results_by_call=results_by_call,
                    history_bounds=snapshot.namespace.history_bounds,
                )
            )
            # The historical old-root anchor (the order's evidence
            # law): a known positively superseded root original
            # present in the payload earns its non-resolving
            # EVIDENCE splice — never a dangling live reference.
            _join_historical_root_envelopes(
                spans,
                payload,
                observation,
                snapshot=snapshot,
                root_entry=root_entry,
                root_key=root_key,
                evidence=evidence,
                historical_root_tags=historical_root_tags,
                max_text_chars=max_text_chars,
            )
        # The superseded authoritative whole-root read / root region
        # (the 022-c section-1 evidence law): every ACTUAL retained
        # authoritative read/read_region root fact DIFFERENT from the
        # governing root digest earns its non-resolving evidence
        # splice, enumerated separately from the E nonroot groups
        # (the bootstrap envelope anchor is the separate envelope
        # join above; the governing fact is the current read splice,
        # never a historical one).
        _join_historical_read_roots(
            spans,
            payload,
            snapshot=snapshot,
            owners=owners,
            root_entry=root_entry,
            root_read_coords=root_read_coords,
            index=index,
            bridge_by_call=bridge_by_call,
            results_by_call=results_by_call,
            max_text_chars=max_text_chars,
            history_bounds=snapshot.namespace.history_bounds,
        )
    for entry in admission.entries:
        for witness in entry.witnesses:
            owner = owners.get(witness.occurrence_id)
            if owner is None:
                raise _refuse(CarrierDetail.CARRIER_UNRESOLVED)
            join_witness = witness
            if root_read_coords:
                # The root's own read splice owns its exact
                # (occurrence, segment) coordinate: the same
                # root-region bytes can never earn a second edit,
                # while a shared entry's OTHER distinct coordinates
                # still join through their own witnesses.
                remaining = tuple(
                    s
                    for s in witness.segment_indices
                    if (witness.occurrence_id, s) not in root_read_coords
                )
                if not remaining:
                    continue
                join_witness = CurrentAdmissionWitness(
                    occurrence_id=witness.occurrence_id,
                    request_index=witness.request_index,
                    call_position=witness.call_position,
                    result_position=witness.result_position,
                    segment_indices=remaining,
                )
            spans.extend(
                _join_file_witness(
                    payload,
                    owner.proof,
                    join_witness,
                    max_text_chars=max_text_chars,
                    content_key=entry.content_key,
                    entry_class_value=entry.entry_class.value,
                    role=_TOOL_RESULT_ROLE,
                    occurrence_identity=witness.occurrence_id,
                    root_digest=None,
                    index=index,
                    bridge_by_call=bridge_by_call,
                    results_by_call=results_by_call,
                    history_bounds=snapshot.namespace.history_bounds,
                )
            )
    # Positive supersession (the order's evidence law): a retained-D
    # NONROOT original absent from the current admission earns its
    # historical spans only when the prepared T result's SAME-RUN E
    # overlay group record positively proves supersession at the
    # (occurrence, group) coordinate (the group index is the
    # occurrence-local segment index).  Granularity is
    # (occurrence, segment): a coordinate covered by ANY current
    # admission witness (root or file) stays with the admission join
    # above (its spans earn their own classification); this phase
    # never re-joins a coordinate the admission already carries.
    # The join is from the ACTUAL retained D occurrence records and
    # the same-run E group facts — the old entry key is never
    # consulted; the span's content identity is the retained
    # segment's source digest.  A group record with no retained
    # occurrence is detached (RETAINED_RECORD_MALFORMED, all-
    # or-nothing); an absent overlay proves nothing (fail closed).
    covered: set[tuple[str, int]] = set()
    covered.update(root_read_coords)
    for entry in (root_entry, *admission.entries):
        for witness in entry.witnesses:
            covered.update((witness.occurrence_id, s) for s in witness.segment_indices)
    overlay = evidence.overlay
    if overlay is not None:
        joined: set[tuple[str, int]] = set()
        for record in overlay.groups:
            coord = (record.occurrence_id, record.group_index)
            if coord in covered or coord in joined:
                continue
            reasons = {reason for row in record.path_rows for reason in row.reasons}
            if (
                CurrentnessReason.PROVEN_CHANGE not in reasons
                or CurrentnessReason.KNOWN_CONTENT_CONFLICT in reasons
                or CurrentnessReason.OWNERSHIP_AMBIGUITY in reasons
            ):
                continue
            owner = owners.get(record.occurrence_id)
            if owner is None:
                raise _refuse(CarrierDetail.RETAINED_RECORD_MALFORMED)
            joined.add(coord)
            spans.extend(
                _join_superseded_occurrence(
                    payload,
                    owner,
                    (record.group_index,),
                    max_text_chars=max_text_chars,
                    index=index,
                    bridge_by_call=bridge_by_call,
                    results_by_call=results_by_call,
                    history_bounds=snapshot.namespace.history_bounds,
                )
            )
    # Refusal-side coverage for recognized INACTIVE source carriers
    # (023-b C06): a retained-D nonroot occurrence whose (occurrence,
    # segment) coordinates NEITHER the admission join above NOR the
    # positive-supersession phase joins — the unproven boundaryless
    # group, staled by currentness UNPROVEN_OWNERSHIP without any
    # proven supersession, so no EVIDENCE splice is earned — is still
    # a recognized source carrier when the current payload presents
    # its call/result.  The currentness contract (section 5) makes
    # such a group earn NEITHER an evidence marker NOR an unsplice:
    # its ordinary raw text stays data when no marker is present,
    # but a marker in its source region is a stale reference the
    # replay gate must catch BEFORE the transition's raw
    # acquisition — the fixed marker-side refusal (the existing
    # typed refusal family), never a transition-conflict fallback.
    # The check scans the source region only: wrapper and ordinary
    # text outside [start, end) stay data, and the transition's own
    # refusal mapping is untouched.
    # Granularity is the (occurrence, segment) coordinate, exactly
    # like the positive-supersession phase: a span earned by ONE
    # segment of a multi-segment proof exempts only that coordinate
    # (a partially handled read never exempts its other source
    # segments).  The existing current-result index is reused first:
    # a segment with NO accepted current carrier at all (genuinely
    # absent from the payload) keeps its raw text as ordinary data
    # and needs no re-join.
    if payload_has_marker_candidates(payload):
        joined_coords = {(s.occurrence_identity, s.segment_index) for s in spans}
        for occurrence_id, owner in owners.items():
            proof = owner.proof
            for segment_index in range(len(proof.segments)):
                if (occurrence_id, segment_index) in joined_coords:
                    continue
                segment = proof.segments[segment_index]
                # Reuse the existing current-result index: count the
                # segment's sub-span pieces exactly as the shared
                # join does and test each for an accepted current
                # observation before any re-join work.
                overlapping = 0
                malformed = False
                has_current_carrier = False
                for piece_index, sub in enumerate(segment.piece_spans):
                    if sub is None:
                        continue
                    overlapping += 1
                    if piece_index >= len(proof.pieces):
                        malformed = True
                        continue
                    if (
                        _current_piece_carriers(
                            proof, proof.pieces[piece_index], index, bridge_by_call
                        )
                        is not None
                    ):
                        has_current_carrier = True
                        break
                if not malformed and overlapping > 0 and not has_current_carrier:
                    # Every piece carrier is genuinely absent from the
                    # current payload (compaction): the shared join
                    # would earn ZERO edits, so the segment's raw text
                    # stays ordinary data (no edit, no refusal here).
                    # A malformed retained coordinate (a sub-span with
                    # no owning piece) falls through to the shared
                    # join, whose closed refusal law applies unchanged.
                    continue
                try:
                    inactive_spans = _join_segment_spans(
                        payload,
                        proof,
                        segment_index,
                        max_text_chars=max_text_chars,
                        content_key=segment.digest,
                        entry_class_value=EntryClass.FILE_BUNDLE_ENTRY.value,
                        role=_TOOL_RESULT_ROLE,
                        occurrence_identity=occurrence_id,
                        root_digest=None,
                        index=index,
                        bridge_by_call=bridge_by_call,
                        results_by_call=results_by_call,
                        history_bounds=snapshot.namespace.history_bounds,
                        historical=True,
                    )
                except _ReplaceRefusal:
                    # The retained segment does not re-prove in the
                    # current payload (a carrier-layer refusal): its
                    # raw text stays ordinary data (no edit, no
                    # refusal here).
                    continue
                for span in inactive_spans:
                    try:
                        slot = lookup_tool_result_carrier(
                            payload,
                            span.endpoint,
                            span.location,
                            max_text_chars=max_text_chars,
                        )
                    except _ReplaceRefusal:
                        continue
                    if find_markers(slot.text[span.start : span.end]):
                        raise _refuse(CarrierDetail.MARKER_INVALID)
    return tuple(spans)


# ---------------------------------------------------------------------------
# Positive supersession by ACTUAL lineage (objective 022-b)
# ---------------------------------------------------------------------------
#
# A retained original that has left the current prepared set is a
# KNOWN POSITIVELY SUPERSEDED original only when the ACTUAL records
# prove it; the proof is re-derived from the actual retained snapshot
# records, never asserted by the caller and never read from the
# current raw bytes:
#
# * FILE spans: the ACTUAL 018-e nonroot currentness decision carried
#   by the accepted same-run R result of the prepared snapshot for
#   the span's OWN witness occurrence and group (the occurrence-local
#   segment order — the span's ``segment_index``), reused by
#   reference, never re-derived.  The group must
#   carry the closed ``proven_change`` reason on one of its path rows
#   (a provably later claim with a KNOWN different digest) and NO
#   ``known_content_conflict`` / ``ownership_ambiguity`` blocker.
#   An ambiguous or conflicting group, an unchanged current version,
#   a later claim without an equality proof, a group the derivation
#   never recorded (a mere omission) or an absent overlay (a mapped
#   refusal or non-ready R outcome) earns no evidence marker (fail
#   closed).
#
# * old root envelopes and superseded authoritative whole-root
#   reads/regions: the ACTUAL P/Q root-region lineage carried by
#   the prepared snapshot's actual same-run 018-q result.  The Q
#   currentness must be ``ready``, the actual P
#   selection must be ``ok`` with a selected source digest DIFFERENT
#   from the retained root digest, and that retained digest must be
#   an ACTUAL retained root fact — a known superseded root original
#   (including a genuine new old-bytes occurrence superseded by a
#   proven descendant).  A superseded authoritative whole-root read
#   or root region (an issued read/read_region root fact different
#   from the governing digest, joined through its OWN retained
#   occurrence and whole/region segment) earns the same marker
#   through the same P/Q lineage.  An absent Q result, any non-ready
#   Q outcome, a differing-root conflict, a no-selected-root or
#   refused P selection, or an unretained digest earns no evidence
#   marker (fail closed).
#
# Mere absence from the prepared set / selection never proves
# historical supersession (that is the separate selection-omission
# basis, not lineage).


@dataclass(frozen=True, slots=True)
class _SupersessionEvidence:
    """The ACTUAL same-run lineage evidence carried by the prepared
    snapshot (reused by reference, never re-derived).

    ``overlay`` is the ACTUAL 018-e nonroot currentness overlay the
    accepted R result derived in the SAME run as the prepared working
    set — ``None`` when the R result carries no E overlay (a mapped
    refusal or non-ready outcome; fail closed: no FILE supersession
    proof).  ``root_currentness`` is the ACTUAL same-run 018-q root
    currentness result with its ACTUAL P selection by reference —
    ``None`` when the R result carries no Q result (fail closed: no
    root supersession proof).  ``authoritative_root_digests`` is the
    closed set of the ACTUAL root source digests carrying ACTUAL
    derived authority in the snapshot's exact same-run P state (the
    bootstrap anchor fact and every issued root fact; a retained
    UNISSUED digest is never authoritative and never proves
    supersession).  A known superseded root original must be one of
    them.  ``admitted_paths`` is the closed set of paths the
    PREPARED admission actually represents in its reverse member
    index (at least one admitted content key) under the approved
    lean/greedy rules of the session: a group whose member paths
    leave that set has no retained admission provenance, so a D
    occurrence plus PROVEN_CHANGE alone never earns an evidence
    splice for it (ordinary off-graph tool output stays intact).
    Nothing advances a revision or mints authority."""

    overlay: CurrentnessOverlay | None
    root_currentness: RootRegionCurrentnessResult | None
    authoritative_root_digests: frozenset[str]
    admitted_paths: frozenset[str]


def _historical_supersession(
    snapshot: RamStateSnapshot,
) -> _SupersessionEvidence:
    """The ACTUAL lineage evidence of the prepared snapshot itself.

    The prepared working set was selected from the accepted R result
    of the EXACT retained state, so the SAME-RUN Q root currentness
    (with its actual P selection) and E nonroot currentness overlay
    carried by that result are the supersession evidence: reused by
    reference, never re-derived (a second derivation could not
    restate the prepared run and would spend a second bounded graph
    pass).  Absent intermediates and non-ready outcomes fail closed
    with no evidence marker."""
    r_result = snapshot.result.r_result
    # The retained admission provenance for the exact group gate:
    # the paths the PREPARED admission actually represents (its
    # reverse member index, at least one admitted content key each)
    # under the approved lean/greedy rules.  A non-READY T result
    # carries no admission — fail closed with the empty set.
    prepared_admission = snapshot.result.admission
    admitted_paths = (
        frozenset()
        if prepared_admission is None
        else frozenset(row.path for row in prepared_admission.path_associations if row.content_keys)
    )
    if r_result is None:
        # The admitted result carries no same-run R result (a
        # mapped T-level refusal before R ran): no same-run Q/E
        # evidence exists — fail closed with no supersession proof.
        return _SupersessionEvidence(
            overlay=None,
            root_currentness=None,
            authoritative_root_digests=frozenset(
                fact.source_digest for fact in snapshot.state.root_facts if fact.authority
            ),
            admitted_paths=admitted_paths,
        )
    return _SupersessionEvidence(
        overlay=r_result.e_overlay,
        root_currentness=r_result.q_result,
        authoritative_root_digests=frozenset(
            fact.source_digest for fact in snapshot.state.root_facts if fact.authority
        ),
        admitted_paths=admitted_paths,
    )


def _file_span_superseded(
    span: RetainedSpan,
    evidence: _SupersessionEvidence,
) -> bool:
    """ACTUAL 018-e group decision for the span's OWN witness
    occurrence and group (see the section law).  A refused
    derivation, no group record for the span's coordinates (a mere
    omission), an ambiguous or conflicting group, a group whose
    member paths leave the PREPARED admission's reverse member
    index (a positively changed path that was never admitted is
    ordinary off-graph tool output — a D occurrence plus
    PROVEN_CHANGE alone never removes it), or a later claim without
    a KNOWN different digest earns no supersession proof."""
    overlay = evidence.overlay
    if overlay is None:
        return False
    record = next(
        (
            group
            for group in overlay.groups
            if group.occurrence_id == span.occurrence_identity
            and group.group_index == span.segment_index
        ),
        None,
    )
    if record is None:
        return False
    # Retained admission provenance for the EXACT group: every
    # nonroot member path must be admitted in the prepared admission
    # (the approved lean/greedy rules already applied there).  The
    # group's occurrence plus PROVEN_CHANGE alone is never enough.
    if not all(row.path in evidence.admitted_paths for row in record.path_rows):
        return False
    reasons = {reason for row in record.path_rows for reason in row.reasons}
    if (
        CurrentnessReason.KNOWN_CONTENT_CONFLICT in reasons
        or CurrentnessReason.OWNERSHIP_AMBIGUITY in reasons
    ):
        return False
    return CurrentnessReason.PROVEN_CHANGE in reasons


def _root_span_superseded(
    span: RetainedSpan,
    evidence: _SupersessionEvidence,
) -> bool:
    """ACTUAL P/Q root lineage for an old root envelope (see the
    section law): the actual same-run Q must be ready, the actual P
    selection ok with a selected digest DIFFERENT from the retained
    root digest, and that digest an ACTUAL AUTHORITATIVE root fact
    of the same-run P state (the bootstrap anchor or an issued fact
    — a retained unissued digest is insufficient; a known
    superseded root original must be one of them)."""
    root = evidence.root_currentness
    if root is None or root.outcome is not RootRegionCurrentnessOutcome.READY:
        return False
    selection = root.p_selection
    if selection is None or selection.outcome is not RootSelectionOutcome.OK:
        return False
    selected = selection.selected_source_digest
    old = span.source_digest
    return selected is not None and selected != old and old in evidence.authoritative_root_digests


def _positively_superseded(
    span: RetainedSpan,
    evidence: _SupersessionEvidence,
) -> bool:
    """A retained span is a known positively superseded original only
    through its ACTUAL lineage proof (see the section law): the
    actual 018-e currentness group decision for a FILE span, the
    actual P/Q root-region lineage for an old root envelope.  Every
    absent, ambiguous or refused record fails closed (no evidence
    marker)."""
    if span.entry_class == EntryClass.ROOT_ENTRY.value:
        return _root_span_superseded(span, evidence)
    if span.entry_class == EntryClass.FILE_BUNDLE_ENTRY.value:
        return _file_span_superseded(span, evidence)
    return False


# ---------------------------------------------------------------------------
# Pure transaction (objective 022-b — saved chunk 3)
# ---------------------------------------------------------------------------
#
# The transaction is the ALL-OR-NOTHING pure exact-span replacement and
# reference pass: no generation, no filesystem IO, no retention, no
# upstream or Gateway access.  The closed gates, in order:
#
# 1. The accepted selection is usable (outcome OK; an OK selection with
#    an empty working set is NO_REPLACEMENT with no transformed payload;
#    every other outcome is SELECTION_NOT_READY).
# 2. The durable generation handoff is sound (``_durable_guard``: the
#    ACTUAL publish outcome, the determinate positive pointer generation
#    and the exact current snapshot by identity).
# 3. The retained proof joins the ACTUAL current payload
#    (``join_retained_proof``: every span through its own owner proof,
#    the current accepted 017 observation, the result-side paired ID and
#    the exact re-proven segment facts).
# 4. The historical supersession evidence is the prepared snapshot's
#    OWN same-run R/Q/E records (``_historical_supersession``: reused
#    by reference, never re-derived; absent or non-ready
#    intermediates fail closed with no evidence marker).
#
# Marker law: every marker in a recognized source field (a joined
# carrier) is verified by RE-DERIVATION against the expectations table.
# Only a CURRENT authority (a current live tag or an evidence tag at
# exactly its own span) enters the replayed set; an accepted replay
# neither changes its authority nor creates a second edit.  A stale
# live reference (a valid live tag for a retained entry that has left
# the accepted selection) ALWAYS refuses — the ``stale`` verdict stays
# the marker layer's internal diagnostic, never a replay — as do
# moved, forged, malformed, unknown-kind or kind-incompatible markers.
# Ordinary text outside the joined carriers is never recognized as
# marker authority.
#
# Edit law: a selected span earns a LIVE edit (or an accepted replay),
# derived from the authorized witnesses INDEPENDENT of the current raw
# bytes — the valid transformed tag is matched BEFORE the raw digest
# mismatch: a selected span whose current bytes leave the retained
# original AND carries no valid transformed tag at its original splice
# start refuses SPAN_MISMATCH all-or-nothing.  An evidence-eligible
# span earns an EVIDENCE edit (or an accepted replay), never a
# dangling live reference: either a current prepared optional source
# actually omitted by the accepted selection (all closed omission
# reasons leave every required content or the exact missing-binding
# guidance in the working set), or a known positively superseded
# original retained in history proven by ACTUAL lineage (the
# accepted 018-e currentness group decision with its proven-change
# reason for a FILE span, or the actual P/Q root-region lineage
# for an old root envelope or a superseded authoritative whole-root
# read/region; mere absence from selection or
# uncertain/conflicting attribution never proves supersession).  A
# merely retained span
# earns no edit (a live tag there is a stale live reference and
# refuses).  A selected span whose carrier is absent or not earned
# earns zero edits (a source-absent replay still returns the exact
# selected context).  Edits obey the closed bounds, never overlap in
# one carrier (never two edits to the same root region) and are
# applied atomically to a deep copy: the input payload is never
# mutated.


@dataclass(frozen=True, slots=True)
class _PlannedEdit:
    """One planned exact-span edit (content-free coordinates + the
    opaque marker to splice in + the closed compiled binding)."""

    span: RetainedSpan
    kind: MarkerKind
    marker: str = dataclass_field(repr=False)
    compiled_digest: str | None


def _failure(outcome: ReplacementOutcome) -> ReplacementResult:
    """The closed all-or-nothing failure result: no transformed
    payload; the typed plan-13 family and its fixed status are
    carried, the outcome repeats in ``diagnostics``."""
    return ReplacementResult(
        outcome=outcome,
        http_status=REPLACEMENT_HTTP_STATUS[outcome],
        diagnostics=(outcome,),
    )


def _binding_key(
    endpoint: str | None,
    call_id: str | None,
    call_position: int | None,
    result_position: int | None,
    piece_index: int | None,
    segment_index: int | None,
    content_key: str | None,
) -> tuple[str, str, int, int, int, int, str]:
    """The closed original-association binding key of ONE expected tag
    (or matched verdict): the endpoint / call identity / call-result
    positions / piece-segment coordinates / content key."""
    return (
        endpoint or "",
        call_id or "",
        call_position or 0,
        result_position or 0,
        piece_index or 0,
        segment_index or 0,
        content_key or "",
    )


def _set_carrier_text(
    payload: dict[str, Any],
    endpoint: str,
    location: str,
    field: str,
    new_text: str,
) -> None:
    """Splice ONE carrier's new exact text into the ALREADY-COPIED
    payload at the closed structural location (the transaction's only
    mutation, on the copy).  A nonmatching closed spelling is an
    internal invariant failure (the location was just earned by the
    closed lookup), never a guess."""
    if endpoint == ENDPOINT_RESPONSES:
        m = _ROOT_LOCATION_RE.match(location)
        if m is not None:
            item_index = _canonical_index(m.group(1))
            entry_index = _canonical_index(m.group(2))
            if item_index is None or entry_index is None:
                raise AssertionError("unreachable: closed root location")
            container = payload["input"]
            item = container[item_index]
            content = item["content"]
            content[entry_index][field] = new_text
            return
        m = _RESPONSES_ITEM_RE.match(location)
        if m is None:
            raise AssertionError("unreachable: closed tool location")
        index = _canonical_index(m.group(1))
        if index is None:
            raise AssertionError("unreachable: closed tool location")
        payload["input"][index][field] = new_text
        return
    m = _CHAT_MESSAGE_RE.match(location)
    if m is None:
        raise AssertionError("unreachable: closed chat tool location")
    index = _canonical_index(m.group(1))
    if index is None:
        raise AssertionError("unreachable: closed chat tool location")
    payload["messages"][index][field] = new_text


def _scan_replayed_markers(
    carriers: dict[tuple[str, str], str],
    expectations: MarkerExpectations,
    binding_of: dict[
        tuple[str, str, int, int, int, int, str],
        tuple[tuple[RetainedSpan, frozenset[str]], ...],
    ],
) -> tuple[dict[tuple[str, str, int], MarkerRecord], dict[tuple[str, str, int], RetainedSpan]]:
    """Verify every marker candidate of the recognized source fields
    (the joined carriers) by RE-DERIVATION and return the ACCEPTED
    replays.

    Closed gate (the order's marker law): only a CURRENT authority
    (verdict ``ok``) may enter the replayed set.  A stale live
    reference — a valid live tag for a retained entry that has left
    the accepted selection — ALWAYS refuses: the ``stale`` verdict
    stays the marker layer's internal diagnostic (``verify_marker``),
    never a replay.  A forged, malformed, unknown-kind, moved (off the
    span's original splice start) or kind-incompatible marker refuses
    the same way.  An accepted replay neither changes its authority
    nor creates a second edit; its record is content-free (the
    coordinates, the kind and the digest/length of the exact wired
    bytes).  The second result maps the SAME keys to the bound
    :class:`RetainedSpan` (the unsplice seam's original-text
    resolution; the transaction plan uses only the records)."""
    replayed: dict[tuple[str, str, int], MarkerRecord] = {}
    replayed_span: dict[tuple[str, str, int], RetainedSpan] = {}
    for (endpoint, location), text in carriers.items():
        for start, candidate in find_markers(text):
            verdict = verify_marker(candidate, start, expectations=expectations)
            if verdict.reason != "ok":
                raise _refuse(CarrierDetail.MARKER_INVALID)
            kind = verdict.kind
            if kind is None:
                raise AssertionError("unreachable: an ok verdict carries its kind")
            required = "live" if kind is MarkerKind.LIVE_REFERENCE else "evidence"
            span: RetainedSpan | None = None
            kinds: frozenset[str] = frozenset()
            entry = binding_of.get(
                _binding_key(
                    verdict.endpoint,
                    verdict.call_id,
                    verdict.call_position,
                    verdict.result_position,
                    verdict.piece_index,
                    verdict.segment_index,
                    verdict.content_key,
                )
            )
            if entry is not None:
                # Full-current-splice position law: the tag must sit
                # at the span's CURRENT proved splice start AND
                # occupy its full proved length — the current proof's
                # splice is the marker's own region once transformed,
                # so a shifted, truncated or residue-bearing tag
                # refuses; the replay stays verified independent of
                # the raw bytes (the retained coordinates are the
                # tag's identity, never its position).  A binding may
                # carry several spans (the repeated root envelope):
                # the span of THIS carrier coordinate is the one the
                # marker binds.
                for cand_span, cand_kinds in entry:
                    if (
                        cand_span.location == location
                        and cand_span.start == start
                        and cand_span.end == start + len(candidate)
                    ):
                        span = cand_span
                        kinds = cand_kinds
                        break
            if span is None or required not in kinds:
                raise _refuse(CarrierDetail.MARKER_INVALID)
            candidate_bytes = candidate.encode("utf-8")
            replayed[(endpoint, location, span.start)] = MarkerRecord(
                carrier_location=location,
                field=span.field,
                start=span.start,
                end=start + len(candidate),
                kind=kind,
                replayed=True,
                marker_sha256=hashlib.sha256(candidate_bytes).hexdigest(),
                marker_bytes=len(candidate_bytes),
                target_content_key=span.content_key,
                source_digest=span.source_digest,
            )
            replayed_span[(endpoint, location, span.start)] = span
    return replayed, replayed_span


# ---------------------------------------------------------------------------
# Replay unsplice (objective 022-c: the marker-shaped source replay is
# detected and authenticated BEFORE any raw state acquisition)
# ---------------------------------------------------------------------------
#
# A client may resend its previously transformed payload: the source
# fields carry the accepted markers in place of the original source
# bytes.  Feeding that payload to the region-lineage transition would
# let the D law see marker bytes as NEW source (a changed root / a new
# file version) -- both the fixed-point refusal and the mixed commit
# of marker text are wrong.  The unsplice is the pure seam that
# restores the ORIGINALS the transition must observe:
#
# - the SAME trusted plan prelude as the transaction runs first (the
#   durable-generation guard, the retained-proof join, the
#   selection-anchored tag expectations and the closed replay scan):
#   any stale / forged / malformed / unknown-kind / moved marker
#   refuses all-or-nothing with the fixed typed marker-side outcome,
#   BEFORE the raw acquisition is committed;
# - every exactly-verified (``ok``) replay is replaced in a shadow
#   payload by its exact retained original source text, re-derived
#   from the trusted state alone (the retained occurrence proof's
#   self-contained segment text, or the bootstrap anchor's retained
#   root body); a marker whose original cannot be exactly re-derived
#   refuses fail-closed -- the unsplice never guesses;
# - ordinary non-source text stays data: the closed-location carrier
#   scan is the only place marker candidates are read, so a
#   marker-shaped string anywhere else in the payload is invisible.


def _proof_span_text(proof: BundleProof, segment_index: int, piece_index: int) -> str:
    """The exact original source text of ONE retained piece/segment
    sub-span.

    The self-contained proof's aggregate text is the ordered segment
    concatenation (model-verified against its own digest), and the
    segment is tiled in piece order by its non-None piece spans --
    the same concatenation law the segment re-proof re-proves against
    the retained digest.  A coordinate that leaves the proof is a
    spliced / detached retained record (refused all-or-nothing)."""
    if segment_index >= len(proof.segments):
        raise _refuse(CarrierDetail.RETAINED_RECORD_MALFORMED)
    segment = proof.segments[segment_index]
    if piece_index >= len(segment.piece_spans):
        raise _refuse(CarrierDetail.RETAINED_RECORD_MALFORMED)
    sub = segment.piece_spans[piece_index]
    if sub is None:
        raise _refuse(CarrierDetail.RETAINED_RECORD_MALFORMED)
    seg_start = sum(seg.char_length for seg in proof.segments[:segment_index])
    seg_text = proof.source_text[seg_start : seg_start + segment.char_length]
    offset = 0
    for position, piece_sub in enumerate(segment.piece_spans):
        if position == piece_index:
            return seg_text[offset : offset + (sub.end - sub.start)]
        if piece_sub is not None:
            offset += piece_sub.end - piece_sub.start
    raise _refuse(CarrierDetail.RETAINED_RECORD_MALFORMED)


def _retained_original_text(
    span: RetainedSpan,
    *,
    owners: dict[str, CompletedReadOccurrence],
    root_anchor: RootAnchor | None,
    root_facts: tuple[RootRegionLineageFact, ...],
) -> str:
    """The exact original source text the replayed marker replaced,
    re-derived from the trusted retained state alone (the unsplice
    fail-closed: a marker whose original cannot be exactly re-derived
    never unsplices -- the marker layer refuses, and the raw
    acquisition is never committed over marker bytes).

    A tool-result-role span is its piece's sub-span of the retained
    occurrence's self-contained proof (the read / read_region / file
    witness / historical joins all carry the actual occurrence
    identity and piece coordinate).  An envelope-role span is the
    bootstrap anchor's retained root body when the span's source
    digest IS the anchor's; a historical read-root anchor presented
    raw resolves its retained occurrence through the same-run P state
    (the whole singleton segment, or the region's root segment -- the
    historical read-root join's own resolution law).  The old entry
    key is never reconstructed and the current root entry key never
    replaces the evidence identity."""
    if span.role == _TOOL_RESULT_ROLE:
        owner = owners.get(span.occurrence_identity)
        if owner is None:
            raise _refuse(CarrierDetail.MARKER_INVALID)
        return _proof_span_text(owner.proof, span.segment_index, span.piece_index)
    if root_anchor is not None and span.source_digest == root_anchor.root_digest:
        # The bootstrap envelope anchor (governing or historical):
        # the anchor's retained root body IS the exact original.
        return root_anchor.root_text
    # A historical read-root anchor presented as a raw envelope:
    # resolve its retained occurrence through the same-run P state.
    for fact in root_facts:
        if (
            not fact.authority
            or fact.source_digest != span.source_digest
            or fact.provenance.kind not in ("read", "read_region")
        ):
            continue
        provenance = fact.provenance
        owner = owners.get(provenance.occurrence_id)
        if owner is None:
            raise _refuse(CarrierDetail.MARKER_INVALID)
        proof = owner.proof
        if provenance.kind == "read":
            if len(proof.segments) != 1 or proof.segments[0].member_digest != fact.source_digest:
                raise _refuse(CarrierDetail.MARKER_INVALID)
            segment_index = 0
        else:
            if not isinstance(provenance, RootRegionReadProvenance):
                raise _refuse(CarrierDetail.MARKER_INVALID)
            segment_index = provenance.root_segment_index
            if segment_index >= len(proof.segments):
                raise _refuse(CarrierDetail.MARKER_INVALID)
            segment = proof.segments[segment_index]
            if (
                segment.member_digest != fact.source_digest
                or len(segment.member_positions) != 1
                or segment.member_positions[0] != provenance.root_member_position
            ):
                raise _refuse(CarrierDetail.MARKER_INVALID)
        # A single attributable member's segment overlaps exactly
        # ONE piece (the whole-singleton / region shape law).
        non_none = [
            i for i, s in enumerate(proof.segments[segment_index].piece_spans) if s is not None
        ]
        if len(non_none) != 1:
            raise _refuse(CarrierDetail.MARKER_INVALID)
        return _proof_span_text(proof, segment_index, non_none[0])
    raise _refuse(CarrierDetail.MARKER_INVALID)


_MARKER_LIKE_PREFIXES: tuple[str, str] = ("[slaif-live:v", "[slaif-evidence:v")


def payload_has_marker_candidates(payload: dict[str, Any]) -> bool:
    """A bounded recursive scan for marker-like tag prefixes anywhere
    in the decoded payload (the cheap replay detector).

    A false positive only costs one pure pre-check: the unsplice's
    closed-location carrier scan is the only place marker candidates
    are read, so a marker-shaped string OUTSIDE a recognized source
    field is ordinary data (ordinary non-source text stays data)."""
    stack: list[Any] = [payload]
    while stack:
        value = stack.pop()
        if isinstance(value, str):
            if any(prefix in value for prefix in _MARKER_LIKE_PREFIXES):
                return True
        elif isinstance(value, dict):
            stack.extend(value.values())
        elif isinstance(value, (list, tuple)):
            stack.extend(value)
    return False


def cold_payload_has_marker_sources(
    payload: dict[str, Any],
    observation: ObservationReport,
    *,
    max_text_chars: int,
) -> bool:
    """The closed COLD marker/source-carrier law (order 022-d
    section 1): a fresh trusted address has NO retained state that
    could authenticate a source marker, so a marker-like candidate
    is judged purely by location: a marker-like prefix inside the
    ACTUAL cold-recognized source span (an accepted root content
    span or a paired read result content span) is a source marker
    with no retained proof, and the cold bootstrap is refused
    BEFORE any raw acquisition, owner allocation or checkpoint.

    The scan is READ-ONLY and closed-location: it resolves only
    the ACTUAL 017-recognized carriers of THIS observation (the
    accepted root occurrences and the paired read results, both
    read endpoints) and reads only the EXACT content span of each
    (the root delimiters / environment tail and the tool wrapper
    stay outside the scan).  A marker-shaped string anywhere else
    (ordinary user text, arguments, call IDs, wrappers) is
    ordinary data: it stays data and never refuses the cold
    start.  A carrier that leaves the accepted 017 shape can no
    longer be recognized as a source carrier at this geometry, so
    it carries no marker authority either (the candidate stays
    ordinary data)."""
    for occurrence in observation.roots.roots:
        span = occurrence.content_span
        if span is None:
            continue
        try:
            slot = lookup_root_carrier(payload, occurrence.location, max_text_chars=max_text_chars)
        except _ReplaceRefusal:
            continue
        text = slot.text[span.start : span.end]
        if any(prefix in text for prefix in _MARKER_LIKE_PREFIXES):
            return True
    for read in observation.reads:
        span = read.content_span
        if span is None:
            continue
        try:
            slot = lookup_tool_result_carrier(
                payload, read.endpoint, read.result_location, max_text_chars=max_text_chars
            )
        except _ReplaceRefusal:
            continue
        text = slot.text[span.start : span.end]
        if any(prefix in text for prefix in _MARKER_LIKE_PREFIXES):
            return True
    return False


@dataclass(slots=True)
class _ReplacePlanPrelude:
    """The shared trusted plan prelude of the pure transaction.

    ONE implementation of the pre-scan law, used by BOTH
    ``replace_sources`` (which then plans and applies the edits) and
    ``unsplice_replayed_markers`` (which then restores the originals
    the transition observes): the durable-generation guard, the
    retained-proof join, the selection-anchored span classification,
    the tag expectations and the closed replay scan over the ACTUAL
    current carriers.  ``owners`` / ``root_anchor`` / ``root_facts``
    are the trusted references the unsplice's original-text
    resolution reads (never re-derived from the payload)."""

    eff_bounds: ReplacementBounds
    namespace_key: str
    spans: tuple[RetainedSpan, ...]
    selected_spans: tuple[RetainedSpan, ...]
    evidence_spans: tuple[RetainedSpan, ...]
    stale_spans: tuple[RetainedSpan, ...]
    expectations: MarkerExpectations
    binding_of: dict[
        tuple[str, str, int, int, int, int, str],
        tuple[tuple[RetainedSpan, frozenset[str]], ...],
    ]
    carriers: dict[tuple[str, str], str]
    replayed: dict[tuple[str, str, int], MarkerRecord]
    replayed_span: dict[tuple[str, str, int], RetainedSpan]
    ready_by_key: dict[str, SelectionReadyEntry]
    working_rows: dict[tuple[str, str], SelectionWorkingEntry]
    omitted_keys: set[str]
    owners: dict[str, CompletedReadOccurrence]
    root_anchor: RootAnchor | None
    root_facts: tuple[RootRegionLineageFact, ...]


def _prepare_replace_plan(
    payload: dict[str, Any],
    *,
    proof: PreparedGenerationProof,
    current_snapshot: RamStateSnapshot,
    ready_entries: tuple[SelectionReadyEntry, ...],
    decision: BundleSelectionDecision,
    observation: ObservationReport,
    root_occurrence: RootOccurrence | None,
    key: bytes,
    bounds: ReplacementBounds | None,
    max_text_chars: int,
) -> _ReplacePlanPrelude:
    """Run the shared trusted plan prelude (see
    :class:`_ReplacePlanPrelude`), refusing all-or-nothing with the
    fixed carrier-layer detail on any carrier / span / marker
    problem (the caller maps the typed outcome)."""
    eff_bounds = bounds if bounds is not None else ReplacementBounds()
    _durable_guard(proof, current_snapshot)
    namespace_key = current_snapshot.namespace.lineage_key
    evidence = _historical_supersession(current_snapshot)
    # The historical old-root anchor's candidate evidence tags:
    # one per ACTUAL authoritative old root digest DIFFERENT from
    # the governing root digest (the bootstrap anchor and every
    # issued root fact of the same-run P state — a retained
    # unissued digest never proves supersession and earns no
    # tag).  The tag identity is the OLD source's own digest in
    # the trusted namespace workspace — immutable across later
    # root changes, so already-issued evidence for the same old
    # anchor keeps verifying (a second genuine root change
    # re-derives the same tag; it does not invalidate the old
    # anchor's evidence).  The drifted — already transformed —
    # old anchor is re-authenticated against these by MAC at its
    # own splice start; a marker matching none refuses.  The old
    # entry key is never reconstructed.
    hist_admission = current_snapshot.result.admission
    historical_root_tags: dict[str, ExpectedTag] = {}
    if hist_admission is not None:
        historical_root_tags = {
            d: derive_evidence_tag(
                key,
                namespace_key=namespace_key,
                original_role=_ROOT_ENVELOPE_ROLE,
                occurrence_identity=d,
                endpoint=ENDPOINT_RESPONSES,
                call_id="",
                call_position=0,
                result_position=0,
                piece_index=0,
                segment_index=0,
                source_digest=d,
            )
            for d in evidence.authoritative_root_digests
            if d != hist_admission.root_entry.root_digest
        }
    spans = join_retained_proof(
        payload,
        snapshot=current_snapshot,
        decision=decision,
        observation=observation,
        root_occurrence=root_occurrence,
        max_text_chars=max_text_chars,
        evidence=evidence,
        historical_root_tags=historical_root_tags,
    )
    ready_by_key = {r.entry.content_key: r for r in ready_entries}
    working_rows = {(row.content_key, row.entry_class.value): row for row in decision.working_set}
    for row_key in working_rows:
        if row_key[0] not in ready_by_key:
            # A selected working row without its prepared compiled
            # index is a broken prepared context (no marker can be
            # re-derived for it).
            raise _refuse(CarrierDetail.CARRIER_UNRESOLVED)
    omitted_keys = {o.content_key for o in decision.omitted}
    selected_spans: list[RetainedSpan] = []
    evidence_spans: list[RetainedSpan] = []
    stale_spans: list[RetainedSpan] = []
    for span in spans:
        if span.historical:
            # A retained-D nonroot original joined through the
            # positive-supersession phase: its (occurrence, group)
            # record positively proved supersession at the join;
            # re-verify through the closed predicate (fail closed:
            # a record that no longer proves earns no edit).  The
            # join is from the ACTUAL retained D occurrence and
            # the prepared T result's same-run E group facts, even
            # though the occurrence is absent from the current
            # admission (the old entry key is never consulted).
            if _positively_superseded(span, evidence):
                evidence_spans.append(span)
            else:
                stale_spans.append(span)
            continue
        if (span.content_key, span.entry_class) in working_rows:
            # Selected spans are NOT raw-gated here: the valid
            # transformed tag at the original splice start is
            # matched BEFORE any raw digest mismatch (the scan
            # below); a selected span without an accepted replay
            # earns SPAN_DIGEST_MISMATCH in the plan.
            selected_spans.append(span)
            continue
        if (
            span.entry_class == EntryClass.FILE_BUNDLE_ENTRY.value
            and span.content_key in omitted_keys
        ) or _positively_superseded(span, evidence):
            # Evidence-eligible: a current prepared optional
            # source actually omitted by the accepted selection
            # (root entries never qualify via omission), or a
            # known positively superseded original proven by
            # ACTUAL lineage.  Eligibility is independent of the
            # raw-byte state; the plan still gates the EVIDENCE
            # edit on the re-proof or an accepted replay.  An
            # EVIDENCE edit or an accepted replay — never a
            # dangling live reference.
            evidence_spans.append(span)
            continue
        # Merely retained (unselected, not omitted, no lineage
        # proof): no edit; a live tag there is a stale live
        # reference and refuses.
        stale_spans.append(span)
    # Expectations (derived INDEPENDENT of the current raw
    # bytes): a current live tag for EVERY selected span (the
    # transformed replay is matched before the raw digest
    # mismatch) PLUS the span's own evidence tag (the
    # app-boundary formatting-pressure omission is decided LATER,
    # in the transaction stage's final budget gate: a selected
    # OPTIONAL that the gate omits earns the non-resolving
    # evidence marker in the outgoing body, so the resend of that
    # own body must verify the marker decision the gate made --
    # the replay validates its own valid marker decision -- before
    # the deterministic re-run re-decides the same omission; the
    # evidence scope carries no entry content key, so the
    # expectation is decision-stable); an evidence tag for EVERY
    # evidence-eligible span (no ready index needed); a stale
    # live tag for every other span whose entry has a ready
    # compiled index (the internal ``stale`` diagnostic keeps an
    # old live reference refusing).
    tags: list[ExpectedTag] = []
    binding_of: dict[
        tuple[str, str, int, int, int, int, str],
        tuple[tuple[RetainedSpan, frozenset[str]], ...],
    ] = {}

    def _note(span: RetainedSpan, tag: ExpectedTag, kind: str) -> None:
        tags.append(tag)
        b = _binding_key(
            tag.endpoint,
            tag.call_id,
            tag.call_position,
            tag.result_position,
            tag.piece_index,
            tag.segment_index,
            tag.content_key,
        )
        entries = list(binding_of.get(b, ()))
        merged = False
        for i, (prev_span, prev_kinds) in enumerate(entries):
            if prev_span is span:
                entries[i] = (prev_span, prev_kinds | frozenset({kind}))
                merged = True
                break
        if not merged:
            # A DISTINCT span may share the ORIGINAL association
            # binding only on a DISTINCT carrier coordinate (the
            # repeated root envelope: the same root source, its own
            # occurrence and carrier).  Two distinct spans on the
            # SAME carrier region are the forbidden double edit.
            for prev_span, _ in entries:
                if (
                    prev_span.endpoint == span.endpoint
                    and prev_span.location == span.location
                    and prev_span.start == span.start
                    and prev_span.end == span.end
                ):
                    raise AssertionError("unreachable: tag binding collision")
            entries.append((span, frozenset({kind})))
        binding_of[b] = tuple(entries)

    for span in selected_spans:
        ready = ready_by_key[span.content_key]
        _note(
            span,
            derive_live_tag(
                key,
                namespace_key=namespace_key,
                original_role=span.role,
                occurrence_identity=span.occurrence_identity,
                endpoint=span.endpoint,
                call_id=span.call_id,
                call_position=span.call_position,
                result_position=span.result_position,
                piece_index=span.piece_index,
                segment_index=span.segment_index,
                entry_class=span.entry_class,
                content_key=span.content_key,
                compiled_digest=ready.index.compile_key,
                source_digest=span.source_digest,
            ),
            "live",
        )
        # The transaction stage's app-boundary budget gate may
        # omit this selected OPTIONAL whole-entry after this plan
        # runs (order 022-f section 3): the outgoing body then
        # carries the span's NON-RESOLVING evidence marker, and
        # the resend of that own body is the legitimate replay
        # that must verify the marker decision the gate made
        # (byte-identical fixed point: the deterministic re-run
        # in the transaction stage re-decides the same omission
        # and re-emits the same marker).  The evidence scope
        # binds the exact occurrence, source digest and carrier
        # association -- never a current entry key -- so this
        # expectation is decision-stable; the adapter never
        # issues an evidence marker for the governing root, so
        # the root span earns no issuable match here.
        _note(
            span,
            derive_evidence_tag(
                key,
                namespace_key=namespace_key,
                original_role=span.role,
                occurrence_identity=span.occurrence_identity,
                endpoint=span.endpoint,
                call_id=span.call_id,
                call_position=span.call_position,
                result_position=span.result_position,
                piece_index=span.piece_index,
                segment_index=span.segment_index,
                source_digest=span.source_digest,
            ),
            "evidence",
        )
    for span in evidence_spans:
        _note(
            span,
            derive_evidence_tag(
                key,
                namespace_key=namespace_key,
                original_role=span.role,
                occurrence_identity=span.occurrence_identity,
                endpoint=span.endpoint,
                call_id=span.call_id,
                call_position=span.call_position,
                result_position=span.result_position,
                piece_index=span.piece_index,
                segment_index=span.segment_index,
                source_digest=span.source_digest,
            ),
            "evidence",
        )
        maybe_ready = ready_by_key.get(span.content_key)
        if maybe_ready is not None:
            _note(
                span,
                derive_live_tag(
                    key,
                    namespace_key=namespace_key,
                    original_role=span.role,
                    occurrence_identity=span.occurrence_identity,
                    endpoint=span.endpoint,
                    call_id=span.call_id,
                    call_position=span.call_position,
                    result_position=span.result_position,
                    piece_index=span.piece_index,
                    segment_index=span.segment_index,
                    entry_class=span.entry_class,
                    content_key=span.content_key,
                    compiled_digest=maybe_ready.index.compile_key,
                    source_digest=span.source_digest,
                    stale=True,
                ),
                "stale",
            )
    for span in stale_spans:
        maybe_ready = ready_by_key.get(span.content_key)
        if maybe_ready is None:
            continue
        _note(
            span,
            derive_live_tag(
                key,
                namespace_key=namespace_key,
                original_role=span.role,
                occurrence_identity=span.occurrence_identity,
                endpoint=span.endpoint,
                call_id=span.call_id,
                call_position=span.call_position,
                result_position=span.result_position,
                piece_index=span.piece_index,
                segment_index=span.segment_index,
                entry_class=span.entry_class,
                content_key=span.content_key,
                compiled_digest=maybe_ready.index.compile_key,
                source_digest=span.source_digest,
                stale=True,
            ),
            "stale",
        )
    expectations = MarkerExpectations(tuple(tags))
    # Scan the recognized source fields (the joined carriers) for
    # marker candidates and verify each by re-derivation.
    carriers: dict[tuple[str, str], str] = {}
    for span in spans:
        carrier_key = (span.endpoint, span.location)
        if carrier_key in carriers:
            continue
        if span.role == _ROOT_ENVELOPE_ROLE:
            slot = lookup_root_carrier(payload, span.location, max_text_chars=max_text_chars)
        else:
            slot = lookup_tool_result_carrier(
                payload, span.endpoint, span.location, max_text_chars=max_text_chars
            )
        carriers[carrier_key] = slot.text
    replayed, replayed_span = _scan_replayed_markers(carriers, expectations, binding_of)
    d_state = current_snapshot.state.d_state
    return _ReplacePlanPrelude(
        eff_bounds=eff_bounds,
        namespace_key=namespace_key,
        spans=tuple(spans),
        selected_spans=tuple(selected_spans),
        evidence_spans=tuple(evidence_spans),
        stale_spans=tuple(stale_spans),
        expectations=expectations,
        binding_of=binding_of,
        carriers=carriers,
        replayed=replayed,
        replayed_span=replayed_span,
        ready_by_key=ready_by_key,
        working_rows=working_rows,
        omitted_keys=omitted_keys,
        owners={o.occurrence_id: o for o in d_state.occurrences},
        root_anchor=d_state.root,
        root_facts=tuple(current_snapshot.state.root_facts),
    )


def replace_sources(
    payload: dict[str, Any],
    *,
    proof: PreparedGenerationProof,
    current_snapshot: RamStateSnapshot,
    ready_entries: tuple[SelectionReadyEntry, ...],
    decision: BundleSelectionDecision,
    observation: ObservationReport,
    root_occurrence: RootOccurrence | None,
    key: bytes,
    bounds: ReplacementBounds | None = None,
    max_text_chars: int,
) -> ReplacementResult:
    """The pure exact-span source-replacement and reference
    transaction (all-or-nothing, see the section law).

    ``proof`` is the narrow durable-generation handoff; the trusted
    state is read from ``current_snapshot`` by immutable reference
    (the guard requires ``proof.snapshot`` to be it by identity).
    ``ready_entries`` is the actual 019/021 prepared current working
    set (every ready admitted entry with its validated compiled
    index — the ``compile_key`` is the marker's compiled binding);
    ``decision`` the accepted 021 selection; ``observation`` the
    ACTUAL 017 observation of THIS payload (the raw-tool edit bridge
    and the root carrier source); ``root_occurrence`` the accepted
    governing root occurrence of this payload; ``key`` the supplied
    private per-session marker key material (never echoed, never
    derived from public data); ``bounds`` the finite transaction
    bounds (the accepted defaults when omitted); ``max_text_chars``
    the accepted observation carrier bound.

    Returns the closed :class:`ReplacementResult`: on ``OK`` the
    transformed payload (a new structure; the input is never
    mutated), the committed edits, every emitted and replayed marker
    (content-free records), the exact selected compiled blocks in
    actual injection order and the actual missing-binding guidance.
    Every failure returns no transformed payload under the typed
    plan-13 family."""
    if max_text_chars < 1:
        raise ValueError("max_text_chars must be positive")
    try:
        if decision.outcome is not SelectionOutcome.OK:
            return _failure(ReplacementOutcome.SELECTION_NOT_READY)
        if not decision.working_set:
            return ReplacementResult(outcome=ReplacementOutcome.NO_REPLACEMENT)
        plan = _prepare_replace_plan(
            payload,
            proof=proof,
            current_snapshot=current_snapshot,
            ready_entries=ready_entries,
            decision=decision,
            observation=observation,
            root_occurrence=root_occurrence,
            key=key,
            bounds=bounds,
            max_text_chars=max_text_chars,
        )
        # Plan (the accepted replay at the original splice start is
        # matched BEFORE the raw digest mismatch): a selected span
        # without a replay whose bytes left the original refuses
        # SPAN_DIGEST_MISMATCH all-or-nothing; a reproven selected
        # span earns a LIVE edit.  An evidence-eligible span without
        # a replay earns an EVIDENCE edit only when reproven (a
        # drifted non-selected carrier is not a recognized source and
        # stays untouched; no ready index is needed — lineage spans
        # are not ready).
        planned: list[_PlannedEdit] = []
        for span in plan.selected_spans:
            if (span.endpoint, span.location, span.start) in plan.replayed:
                continue
            if not span.reproven:
                raise _refuse(CarrierDetail.SPAN_DIGEST_MISMATCH)
            ready = plan.ready_by_key[span.content_key]
            planned.append(
                _PlannedEdit(
                    span=span,
                    kind=MarkerKind.LIVE_REFERENCE,
                    marker=make_live_marker(
                        key,
                        namespace_key=plan.namespace_key,
                        original_role=span.role,
                        occurrence_identity=span.occurrence_identity,
                        endpoint=span.endpoint,
                        call_id=span.call_id,
                        call_position=span.call_position,
                        result_position=span.result_position,
                        piece_index=span.piece_index,
                        segment_index=span.segment_index,
                        entry_class=span.entry_class,
                        content_key=span.content_key,
                        compiled_digest=ready.index.compile_key,
                        source_digest=span.source_digest,
                    ),
                    compiled_digest=ready.index.compile_key,
                )
            )
        for span in plan.evidence_spans:
            if (span.endpoint, span.location, span.start) in plan.replayed:
                continue
            if not span.reproven:
                continue
            planned.append(
                _PlannedEdit(
                    span=span,
                    kind=MarkerKind.EVIDENCE,
                    marker=make_evidence_marker(
                        key,
                        namespace_key=plan.namespace_key,
                        original_role=span.role,
                        occurrence_identity=span.occurrence_identity,
                        endpoint=span.endpoint,
                        call_id=span.call_id,
                        call_position=span.call_position,
                        result_position=span.result_position,
                        piece_index=span.piece_index,
                        segment_index=span.segment_index,
                        source_digest=span.source_digest,
                    ),
                    compiled_digest=None,
                )
            )
        # Closed bounds (fail closed before unbounded work).
        if len(planned) > plan.eff_bounds.max_edits:
            raise _refuse(CarrierDetail.REPLACEMENT_OVER_BOUND)
        replaced_chars = sum(p.span.end - p.span.start for p in planned)
        if replaced_chars > plan.eff_bounds.max_replaced_chars:
            raise _refuse(CarrierDetail.REPLACEMENT_OVER_BOUND)
        for p in planned:
            if len(p.marker.encode("utf-8")) > plan.eff_bounds.max_marker_bytes:
                raise _refuse(CarrierDetail.REPLACEMENT_OVER_BOUND)
        by_carrier: dict[tuple[str, str], list[_PlannedEdit]] = {}
        for p in planned:
            by_carrier.setdefault((p.span.endpoint, p.span.location), []).append(p)
        touched = set(by_carrier)
        touched |= {(endpoint, location) for endpoint, location, _start in plan.replayed}
        if len(touched) > plan.eff_bounds.max_carriers:
            raise _refuse(CarrierDetail.REPLACEMENT_OVER_BOUND)
        # No two edits may occupy the same carrier region (the same
        # root region is never double-edited).
        for edits in by_carrier.values():
            edits.sort(key=lambda p: (p.span.start, p.span.end))
            for prev, cur in zip(edits, edits[1:], strict=False):
                if cur.span.start < prev.span.end:
                    raise _refuse(CarrierDetail.EDITS_OVERLAP)
        # Atomic application on a deep copy: the input is never
        # mutated; outside the edited spans every byte (roles,
        # non-source text, wrappers, prefix/suffix, printed delimiter
        # lines, Unicode/CRLF, images, tool IDs/names/arguments/
        # status/order and API fields) is preserved.
        out = copy.deepcopy(payload)
        source_edits: list[SourceEdit] = []
        marker_records: list[MarkerRecord] = list(plan.replayed.values())
        for (endpoint, location), edits in by_carrier.items():
            field = edits[0].span.field
            text = plan.carriers[(endpoint, location)]
            for p in sorted(edits, key=lambda p: p.span.start, reverse=True):
                text = text[: p.span.start] + p.marker + text[p.span.end :]
            _set_carrier_text(out, endpoint, location, field, text)
            for p in edits:
                source_edits.append(
                    SourceEdit(
                        carrier_location=location,
                        field=field,
                        start=p.span.start,
                        end=p.span.end,
                        kind=p.kind,
                        target_content_key=p.span.content_key,
                        target_entry_class=p.span.entry_class,
                        target_compiled_digest=p.compiled_digest,
                        source_digest=p.span.source_digest,
                        occurrence_identity=p.span.occurrence_identity,
                    )
                )
                marker_bytes = p.marker.encode("utf-8")
                marker_records.append(
                    MarkerRecord(
                        carrier_location=location,
                        field=field,
                        start=p.span.start,
                        end=p.span.end,
                        kind=p.kind,
                        replayed=False,
                        marker_sha256=hashlib.sha256(marker_bytes).hexdigest(),
                        marker_bytes=len(marker_bytes),
                        target_content_key=p.span.content_key,
                        source_digest=p.span.source_digest,
                    )
                )
        return ReplacementResult(
            outcome=ReplacementOutcome.OK,
            transformed_payload=out,
            edits=tuple(source_edits),
            markers=tuple(marker_records),
            compiled_blocks=tuple(row.rendered_block for row in decision.working_set),
            missing_bindings=decision.missing_bindings,
            selected_content_keys=tuple(row.content_key for row in decision.working_set),
            edits_planned=len(planned),
            edits_committed=len(planned),
            markers_emitted=len(planned),
            markers_replayed=len(plan.replayed),
            carriers_touched=len(touched),
            chars_replaced=replaced_chars,
        )
    except _ReplaceRefusal as refusal:
        return _failure(refusal.outcome)


def unsplice_replayed_markers(
    payload: dict[str, Any],
    *,
    proof: PreparedGenerationProof,
    current_snapshot: RamStateSnapshot,
    ready_entries: tuple[SelectionReadyEntry, ...],
    decision: BundleSelectionDecision,
    observation: ObservationReport,
    root_occurrence: RootOccurrence | None,
    key: bytes,
    bounds: ReplacementBounds | None = None,
    max_text_chars: int,
) -> UnspliceReplayResult:
    """The pure replay unsplice (the marker-shaped source replay
    detected and authenticated BEFORE any raw state acquisition).

    Runs the SAME trusted plan prelude as the transaction (the
    durable-generation guard, the retained-proof join, the
    selection-anchored expectations and the closed replay scan): a
    stale / forged / malformed / unknown-kind / moved marker in a
    recognized source field refuses all-or-nothing with the fixed
    typed marker-side outcome (the raw acquisition is never
    committed over marker bytes).  Every exactly-verified (``ok``)
    replay is then replaced in a SHADOW payload by its exact
    retained original source text (re-derived from the trusted state
    alone — the retained occurrence proof's self-contained segment
    text or the bootstrap anchor's retained root body; the old entry
    key is never reconstructed), and the shadow is what the
    region-lineage transition observes.

    On ``OK`` with no marker in any joined carrier the shadow EQUALS
    the input payload (a detector false positive: ordinary non-source
    text stays data; the closed-location scan saw no marker).  The
    input is never mutated."""
    if max_text_chars < 1:
        raise ValueError("max_text_chars must be positive")
    try:
        if decision.outcome is not SelectionOutcome.OK:
            return UnspliceReplayResult(outcome=ReplacementOutcome.SELECTION_NOT_READY)
        plan = _prepare_replace_plan(
            payload,
            proof=proof,
            current_snapshot=current_snapshot,
            ready_entries=ready_entries,
            decision=decision,
            observation=observation,
            root_occurrence=root_occurrence,
            key=key,
            bounds=bounds,
            max_text_chars=max_text_chars,
        )
        if not plan.replayed:
            # No verified marker in any recognized source field: no
            # replay is present; the transition observes the payload
            # as-is (the shadow equals the input; no edit was made).
            return UnspliceReplayResult(
                outcome=ReplacementOutcome.OK,
                shadow_payload=payload,
                markers_replayed=0,
                carriers_unspliced=0,
            )
        # Every replayed marker is exactly verified (the scan
        # refused any non-ok verdict); restore its exact retained
        # original in a deep copy, per carrier, outermost-first.
        by_carrier: dict[tuple[str, str], tuple[str, list[tuple[int, int, str]]]] = {}
        for (endpoint, location, start), record in plan.replayed.items():
            span = plan.replayed_span[(endpoint, location, start)]
            original = _retained_original_text(
                span,
                owners=plan.owners,
                root_anchor=plan.root_anchor,
                root_facts=plan.root_facts,
            )
            entry = by_carrier.get((endpoint, location))
            if entry is None:
                by_carrier[(endpoint, location)] = (span.field, [(start, record.end, original)])
            else:
                entry[1].append((start, record.end, original))
        out = copy.deepcopy(payload)
        carriers_unspliced = 0
        for (endpoint, location), (field, edits) in by_carrier.items():
            text = plan.carriers[(endpoint, location)]
            for start, end, original in sorted(edits, key=lambda e: e[0], reverse=True):
                text = text[:start] + original + text[end:]
            _set_carrier_text(out, endpoint, location, field, text)
            carriers_unspliced += 1
        return UnspliceReplayResult(
            outcome=ReplacementOutcome.OK,
            shadow_payload=out,
            markers_replayed=len(plan.replayed),
            carriers_unspliced=carriers_unspliced,
        )
    except _ReplaceRefusal as refusal:
        return UnspliceReplayResult(outcome=refusal.outcome)

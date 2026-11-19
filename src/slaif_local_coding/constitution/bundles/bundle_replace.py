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
import hashlib
import hmac
import re
from dataclasses import dataclass
from dataclasses import field as dataclass_field
from enum import StrEnum
from typing import Any

from .bundle_replace_models import (
    EVIDENCE_MARKER_DOMAIN,
    EVIDENCE_MARKER_TAG,
    LIVE_MARKER_DOMAIN,
    LIVE_MARKER_TAG,
    MARKER_SUFFIX,
    MarkerKind,
    ReplacementOutcome,
)
from .observation_models import OccurrenceKind, RootOccurrence, RootStatus
from .observe import ENDPOINT_RESPONSES

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
    content_key: str,
) -> bytes:
    """The closed evidence-marker HMAC scope: the original namespace,
    the exact occurrence/root-source identity, the ORIGINAL
    endpoint/call/result/piece/segment association and the prepared
    entry content key (a known positively superseded original or an
    actual selection omission of a prepared optional source)."""
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
        content_key,
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
    content_key: str,
) -> str:
    """Build the versioned opaque non-resolving evidence marker (kind 2).

    Tied to the original namespace, the exact occurrence/root-source
    identity, the original endpoint/call/result/piece/segment
    association and the prepared entry content key; emits ONLY the
    versioned kind plus the fixed-length canonical MAC tag."""
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
        content_key,
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
    content_key: str,
) -> ExpectedTag:
    """Re-derive ONE expected evidence tag from trusted derivation
    inputs (a known positively superseded original or an actual
    selection omission of a prepared optional source)."""
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
        content_key,
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
        content_key=content_key,
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
    """Fixed closed detail codes of the carrier/span layer.

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
    CarrierDetail.OVER_BOUND: ReplacementOutcome.OVER_BOUND,
    CarrierDetail.SPAN_OUT_OF_BOUNDS: ReplacementOutcome.SPAN_MISMATCH,
    CarrierDetail.SPAN_LENGTH_MISMATCH: ReplacementOutcome.SPAN_MISMATCH,
    CarrierDetail.SPAN_DIGEST_MISMATCH: ReplacementOutcome.SPAN_MISMATCH,
    CarrierDetail.PIECE_NOT_PROVEN: ReplacementOutcome.SPAN_MISMATCH,
    CarrierDetail.EDITS_OVERLAP: ReplacementOutcome.EDIT_CONFLICT,
    CarrierDetail.REPLACEMENT_OVER_BOUND: ReplacementOutcome.OVER_BOUND,
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


def join_root_occurrence(
    payload: dict[str, Any],
    occurrence: RootOccurrence,
    *,
    expected_digest: str,
    expected_char_length: int | None = None,
    expected_byte_length: int | None = None,
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
    character/UTF-8-byte lengths (checked when supplied).  The join is
    read-only and returns ``(carrier, span facts)``; a carrier shape
    failure, a span out of bounds or a length/digest mismatch refuses
    with the fixed detail (the observed coordinates or the span leave
    the retained original facts).  A non-root or non-OK occurrence is
    refused as an unsupported shape (no root authority is inferred)."""
    if (
        occurrence.kind is not OccurrenceKind.ROOT
        or occurrence.status is not RootStatus.OK
        or occurrence.content_span is None
    ):
        raise _refuse(CarrierDetail.SHAPE_UNSUPPORTED)
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

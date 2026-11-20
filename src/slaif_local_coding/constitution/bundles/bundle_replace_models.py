"""Pure exact-span source-replacement contract (objective 022-b).

This module defines the closed typed data for the pure source-replacement
transaction required by ``docs/CACHE-IMPLEMENTATION-PLAN.md`` policy 12 and
``docs/CACHE-REWORK.md`` section 11: versioned exact-span edit plans, the
two unambiguously versioned opaque marker kinds (live reference,
non-resolving evidence), the narrow internal durable-generation handoff,
and the pure result that pairs a transformed payload with the exact
selected compiled blocks and actual missing-binding guidance.

Law highlights:

- The transaction is pure: no generation, no filesystem IO, no retention,
  no upstream or Gateway access. The per-session marker key material is
  supplied by the internal prepared context and never derived from public
  digests, body/header assertions, upstream or Gateway credentials.
- Markers are authenticated with a domain-separated standard HMAC
  (separate domain per marker kind) and are scoped to the complete trusted
  namespace, the original role, the exact occurrence or root-source
  identity, and the segment/carrier association. A wired marker exposes
  neither source identities nor credentials.
- Every committed edit is earned by complete attributable source, the
  exact current prepared context and a successful durable generation tied
  to the retained snapshot the edit relies on. A boolean or a free
  generation integer does not establish preparation (the typed
  ``PreparedGenerationProof`` is the narrow handoff).
- All-or-nothing: a nonusable selection, missing/failed/mismatched
  durability, a stale snapshot or a conflicting edit returns no
  transformed payload under the existing typed failure families (plan 13:
  503 infrastructure/recovery/resource; 409 version/scope conflict; 422
  budget/invalid transform).
- Operational ``str``/``repr`` never echo private call IDs, paths, marker
  key material or raw source content: fixed enums, counts, structural
  locations and digests only.
"""

from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, InstanceOf

from .bundle_selection import SelectionMissingBinding
from .ram_state_models import RamStateSnapshot
from .recovery_store import RecoveryPublishResult

BUNDLE_REPLACE_CONTRACT_VERSION = "cache-bundle-replace/v1"
BUNDLE_REPLACE_POLICY_VERSION = "foundation-v1"

#: Marker kind 1: a live reference identifying exact current compiled
#: content actually present in the accepted selection (versioned).
LIVE_MARKER_TAG = "[slaif-live:v1:"
#: Marker kind 2: a distinct non-resolving evidence marker for a known
#: positively superseded original retained in history (versioned).
EVIDENCE_MARKER_TAG = "[slaif-evidence:v1:"
MARKER_SUFFIX = "]"

#: Domain-separated HMAC domains, one per marker kind (standard HMAC-SHA256).
LIVE_MARKER_DOMAIN = "slaif-bundle-replace/live-ref/v1"
EVIDENCE_MARKER_DOMAIN = "slaif-bundle-replace/evidence/v1"

_HEX64 = r"^[0-9a-f]{64}$"


class MarkerKind(StrEnum):
    """The two unambiguously versioned opaque marker kinds."""

    LIVE_REFERENCE = "live-reference"
    EVIDENCE = "evidence"


class ReplacementOutcome(StrEnum):
    """The closed pure-transaction outcome vocabulary.

    ``OK`` commits (possibly zero edits: a source-absent pairing still
    carries the exact selected compiled blocks and guidance).
    ``NO_REPLACEMENT`` means the accepted selection carried no working
    entry, so nothing was earned; no transformed payload is claimed.
    Every failure outcome returns no transformed payload (all-or-nothing).
    """

    OK = "ok"
    NO_REPLACEMENT = "no-replacement"
    SELECTION_NOT_READY = "selection-not-ready"
    GENERATION_NOT_DURABLE = "generation-not-durable"
    CROSS_NAMESPACE = "cross-namespace"
    SPAN_MISMATCH = "span-mismatch"
    MARKER_INVALID = "marker-invalid"
    ENTRY_UNRESOLVED = "entry-unresolved"
    EDIT_CONFLICT = "edit-conflict"
    OVER_BOUND = "over-bound"


# Plan 13 typed failure families: 503 infrastructure/recovery/resource;
# 409 version/scope conflict; 422 budget/invalid transform.
REPLACEMENT_HTTP_STATUS: dict[ReplacementOutcome, int | None] = {
    ReplacementOutcome.OK: None,
    ReplacementOutcome.NO_REPLACEMENT: None,
    ReplacementOutcome.SELECTION_NOT_READY: 422,
    ReplacementOutcome.GENERATION_NOT_DURABLE: 503,
    ReplacementOutcome.CROSS_NAMESPACE: 409,
    ReplacementOutcome.SPAN_MISMATCH: 409,
    ReplacementOutcome.MARKER_INVALID: 409,
    ReplacementOutcome.ENTRY_UNRESOLVED: 409,
    ReplacementOutcome.EDIT_CONFLICT: 409,
    ReplacementOutcome.OVER_BOUND: 422,
}


class _Frozen(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class ReplacementBounds(_Frozen):
    """Finite transaction bounds; adversarial input must terminate.

    The caller reuses the accepted observation/proof bounds for the
    upstream parsers; these bound the transaction's own copy/parse work
    (edit count, carrier count, emitted marker bytes, replaced volume).
    """

    max_edits: int = Field(default=256, ge=1, le=4096)
    max_carriers: int = Field(default=128, ge=1, le=4096)
    max_marker_bytes: int = Field(default=1024, ge=64, le=8192)
    max_replaced_chars: int = Field(default=8_388_608, ge=1, le=2_147_483_647)


class PreparedGenerationProof(_Frozen):
    """The narrow internal handoff for the durable-generation proof.

    Carries the ACTUAL accepted 020 ``RecoveryPublishResult`` (the
    successful durable publication with its pointer) and the EXACT
    retained 019 ``RamStateSnapshot`` by immutable reference. Free
    digest/generation/revision fields alone do not prove the joined
    snapshot: the transaction verifies the real publish outcome, the
    real pointer and the real snapshot object (its immutable namespace,
    revision and epoch), and a boolean or a free generation integer
    cannot construct this record. The pure slice performs no recovery
    IO and no retention; it only checks that every edit it commits
    relies on this proof.
    """

    proof_version: str = "recovery-proof-ref/v1"
    publish: InstanceOf[RecoveryPublishResult]
    snapshot: InstanceOf[RamStateSnapshot]


class SourceEdit(_Frozen):
    """One planned/committed exact-span edit (internal, content-free).

    ``carrier_location`` is the accepted structural location of one decoded
    string carrier (e.g. ``$.input[3].content[0]``, ``$.input[7]``,
    ``$.messages[2]``); ``field`` is the exact JSON field holding the
    string (``text`` / ``output`` / ``content``). ``start``/``end`` are
    half-open character offsets into that exact decoded string. The
    occurrence identity is MAC-bound inside the emitted marker and is
    suppressed from operational representations (it embeds private call
    IDs).
    """

    carrier_location: str = Field(min_length=1)
    field: str = Field(min_length=1, max_length=16)
    start: int = Field(ge=0)
    end: int = Field(ge=0)
    kind: MarkerKind
    target_content_key: str = Field(pattern=_HEX64)
    target_entry_class: str = Field(min_length=1, max_length=32)
    target_compiled_digest: str | None = Field(default=None, pattern=_HEX64)
    source_digest: str = Field(pattern=_HEX64)
    occurrence_identity: str = Field(min_length=1, repr=False)

    @property
    def length(self) -> int:
        return self.end - self.start


class MarkerRecord(_Frozen):
    """One emitted (or replayed) wired marker, recorded content-free."""

    carrier_location: str = Field(min_length=1)
    field: str = Field(min_length=1, max_length=16)
    start: int = Field(ge=0)
    end: int = Field(ge=0)
    kind: MarkerKind
    replayed: bool
    marker_sha256: str = Field(pattern=_HEX64)
    marker_bytes: int = Field(ge=1)
    target_content_key: str = Field(pattern=_HEX64)
    source_digest: str = Field(pattern=_HEX64)


class ReplacementResult(_Frozen):
    """The pure result of one exact-span source-replacement transaction.

    On ``OK`` the exact selected compiled blocks (actual injection order)
    and the actual missing-binding guidance are carried as part of the
    same successful pure result. ``transformed_payload`` is the outgoing
    decoded request (a new structure where edits were applied, the input
    reference otherwise, never the input mutated); on ``NO_REPLACEMENT``
    and every failure it is ``None`` (no transformed payload).
    """

    contract_version: str = BUNDLE_REPLACE_CONTRACT_VERSION
    policy_version: str = BUNDLE_REPLACE_POLICY_VERSION
    outcome: ReplacementOutcome
    http_status: int | None = None
    transformed_payload: dict[str, Any] | None = Field(default=None, repr=False)
    edits: tuple[SourceEdit, ...] = ()
    markers: tuple[MarkerRecord, ...] = ()
    #: The exact selected compiled blocks (actual injection order):
    #: private compiled text, suppressed from operational representations.
    compiled_blocks: tuple[str, ...] = Field(default=(), repr=False)
    #: The actual missing-binding guidance: carries private paths,
    #: suppressed from operational representations.
    missing_bindings: tuple[SelectionMissingBinding, ...] = Field(default=(), repr=False)
    selected_content_keys: tuple[str, ...] = ()
    diagnostics: tuple[ReplacementOutcome, ...] = ()
    edits_planned: int = Field(default=0, ge=0)
    edits_committed: int = Field(default=0, ge=0)
    markers_emitted: int = Field(default=0, ge=0)
    markers_replayed: int = Field(default=0, ge=0)
    carriers_touched: int = Field(default=0, ge=0)
    chars_replaced: int = Field(default=0, ge=0)


class UnspliceReplayResult(_Frozen):
    """The closed result of the pure replay unsplice (objective 022-c).

    ``shadow_payload`` is the payload the region-lineage transition
    observes BEFORE any raw acquisition: every exactly-verified
    current marker of the recognized source fields replaced by its
    retained original source text (the transition sees the originals,
    never marker bytes as source).  On ``OK`` with no marker in any
    joined carrier it EQUALS the INPUT payload (no marker was
    present; no edit was made).  On every failure it is ``None``
    (all-or-nothing; no shadow is claimed).  ``markers_replayed`` is
    the count of exactly-verified markers unspliced and
    ``carriers_unspliced`` the count of carriers whose text changed.
    Content-free: the shadow payload carries the client's own
    previously-observed source and is repr-suppressed."""

    contract_version: str = BUNDLE_REPLACE_CONTRACT_VERSION
    outcome: ReplacementOutcome
    shadow_payload: dict[str, Any] | None = Field(default=None, repr=False)
    markers_replayed: int = Field(default=0, ge=0)
    carriers_unspliced: int = Field(default=0, ge=0)

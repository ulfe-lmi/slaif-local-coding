"""Pure versioned bounded inert RAM state owner models
(objective 019-a, first store slice).

This module carries the versioned data models of the NEW
per-session RAM owner: the explicit ``RamStateBounds`` ceiling
set (the initial documented 128 MiB per-session and 512 MiB
per-process owned-cache occupancy ceilings, closed against a
documented conservative hard ceiling, STRICT raw integers),
the closed ``RamStateOutcome`` / ``RamStateLimitation``
vocabulary, the immutable ``RamStateSnapshot`` of one retained
018 record set (the ACTUAL 018-p ``RootRegionLineageNamespace``
and ``RootRegionLineageState`` plus the ACTUAL 018-t
``RootRegionAdmissionResult`` by reference, the owner CAS
revision, the explicit cache epoch and the charged owned
bytes), and the typed admission / lookup / teardown result
records.

The models are INERT: they wire no runtime, expose no operation
and claim no admission/compiled-cache/HTTP readiness.  Object
construction is not authentication.  The owning component
(``ram_state``) supplies the actual charged store behavior:
the owner base metadata is charged at creation, the retained
record set plus the historical immutable entry catalog are
charged before every commit, the REGISTRY enforces the
process ceiling (an owner session override can never bypass
it), the complete trusted namespace binds by identity, the
closed T result law is re-joined before any charge, a stale
lineage revision is refused as a rollback, and explicit
teardown releases the owned state, the catalog and the
registry reference.  The fixed typed 503 backpressure
contract is declared here (``RAM_HTTP_CAPACITY_STATUS``) and
stays inert until the 022 wiring.  No legacy
``DerivedIndexCache`` / tmpfs / XDG implementation is reused;
the new store is inert and separate from the active legacy
path.  All existing C/D/G/H/O/I/P/Q/R/S/T public signatures,
defaults, schemas, version tags, recipe bytes and behavior
remain intact.
"""

from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import Field, InstanceOf, field_validator, model_validator

from .graph_models import _fixed, _GraphFrozen
from .root_region_admission_models import RootRegionAdmissionEntry
from .root_region_admission_result_models import RootRegionAdmissionResult
from .root_region_lineage_models import (
    RootRegionLineageNamespace,
    RootRegionLineageState,
)

RAM_STATE_CONTRACT_VERSION = "cache-ram-state/v1"
RAM_STATE_POLICY_VERSION = "ram-state-policy/v1"

#: The initial documented per-session owned-cache occupancy
#: ceiling (128 MiB).
RAM_SESSION_MAX_OWNED_BYTES_DEFAULT = 134_217_728

#: The initial documented per-process owned-cache occupancy
#: ceiling (512 MiB).
RAM_PROCESS_MAX_OWNED_BYTES_DEFAULT = 536_870_912

#: The closed conservative hard ceiling on any configured
#: ceiling (1 TiB): a configurable value is validated against
#: this BEFORE any store use; it is a shape bound, not an
#: occupancy promise.
RAM_OWNED_BYTES_HARD_CEILING = 1_099_511_627_776

#: The fixed typed backpressure status declared at this inert
#: boundary for the two capacity refusals (HTTP wiring is 022).
RAM_HTTP_CAPACITY_STATUS = 503


def _ram_int_in(value: object, low: int, high: int) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and low <= value <= high


class RamStateBounds(_GraphFrozen):
    """The explicit configurable owned-cache occupancy ceilings
    (the registry-level configuration record).

    ``session_max_owned_bytes`` is the DEFAULT per-session
    ceiling (an owner may carry a stricter positive value,
    never one above the registry process ceiling);
    ``process_max_owned_bytes`` is the REGISTRY-ENFORCED
    ceiling on the SUM of every live session's owned record
    set in the owning process -- an owner session override can
    never bypass it.  Both are STRICT positive non-bool raw
    integers (bool / float / string inputs refuse before any
    coercion), the session ceiling is no greater than the
    process ceiling, and both stay under the documented
    conservative hard ceiling.  They measure owned-cache
    occupancy, never total process RSS."""

    session_max_owned_bytes: int = Field(
        default=RAM_SESSION_MAX_OWNED_BYTES_DEFAULT,
        ge=1,
        le=RAM_OWNED_BYTES_HARD_CEILING,
        strict=True,
    )
    process_max_owned_bytes: int = Field(
        default=RAM_PROCESS_MAX_OWNED_BYTES_DEFAULT,
        ge=1,
        le=RAM_OWNED_BYTES_HARD_CEILING,
        strict=True,
    )

    @field_validator("session_max_owned_bytes", "process_max_owned_bytes", mode="after")
    @classmethod
    def _v_ceiling_int(cls, value: object, info: Any) -> int:
        # The closed fence runs AFTER the strict raw-integer
        # validation (strict ints refuse bool / float / string
        # BEFORE coercion); this guard keeps the fixed private
        # error on the closed boundary.
        if isinstance(value, bool) or not isinstance(value, int):
            raise _fixed("ram state ceilings must be positive integers")
        return value

    @model_validator(mode="after")
    def _v_session_le_process(self) -> RamStateBounds:
        if self.session_max_owned_bytes > self.process_max_owned_bytes:
            raise _fixed("the session ceiling cannot exceed the process ceiling")
        return self


def ram_state_bounds_shape_ok(bounds: object) -> bool:
    """RAM-PRIVATE closed fence over the registry ceiling set
    (the registry's own preflight boundary): ORIGINAL
    class, field existence, exact non-bool ints under the hard
    ceiling and the session <= process join, BEFORE any
    serializer visit.  Valid stricter original-class instances
    stay legal; shadow subclasses and malformed copies are
    not."""
    return (
        type(bounds) is RamStateBounds
        and hasattr(bounds, "session_max_owned_bytes")
        and hasattr(bounds, "process_max_owned_bytes")
        and _ram_int_in(bounds.session_max_owned_bytes, 1, RAM_OWNED_BYTES_HARD_CEILING)
        and _ram_int_in(bounds.process_max_owned_bytes, 1, RAM_OWNED_BYTES_HARD_CEILING)
        and bounds.session_max_owned_bytes <= bounds.process_max_owned_bytes
    )


class RamStateOutcome(StrEnum):
    """The closed owner-operation outcome vocabulary (019-a)."""

    ADMITTED = "admitted"
    REFUSED = "refused"
    FOUND = "found"
    NOT_FOUND = "not_found"
    TEARDOWN = "teardown"


class RamStateLimitation(StrEnum):
    """The closed owner-limitation vocabulary (019-a).

    ``session_owned_bytes_over_bound`` and
    ``process_owned_bytes_over_bound`` are the two capacity
    refusals that carry the fixed typed 503 backpressure
    contract at this inert boundary (the process ceiling is
    the REGISTRY's).  ``duplicate_owner`` names the
    unsupported multi-worker configuration rejected at the
    component boundary (construction raises the fixed typed
    error).  ``owner_namespace_mismatch``, ``epoch_fenced``,
    ``work_in_flight`` and ``revision_mismatch`` are the
    trusted-namespace / explicit-epoch / work-plane /
    commit-CAS fence refusals, and ``stale_state_revision``
    is the LINEAGE-rollback fence (an older genuine P state
    than the retained one, or a DISTINCT state object at the
    SAME retained P revision -- a divergent lineage fork; the
    state revision is a CAS fence, never an arrival clock; an
    identical retained state replay is separate).
    ``work_in_flight`` names the 019-b work-plane fence on
    the synchronous teardown: while the owner's work plane is
    fenced (the async work teardown is draining) or still
    owns queued / active work, the synchronous teardown
    refuses; the async work teardown releases the store
    owner and the work plane atomically, so no same-epoch
    reset window exists.  ``owner_quarantined`` is the
    ADVERSE-CURRENTNESS QUARANTINE fence (019-c): when a
    genuine NEW state that would INVALIDATE the retained
    current usable rows -- a non-READY ACTUAL T result (an
    unresolved maximal root uncertainty or another refused
    currentness), or a READY result withdrawing / rekeying a
    retained current key (a changed governing root, an
    overlapping changed file) -- cannot be RETAINED under
    the ceilings, the owner can no longer certify currentness
    from the older retained READY state and is bounded to
    the unusable state (a single pre-accounted flag; no
    adverse journal): every later admission refuses with
    this fence and every lookup / work resolve refuses
    with the fixed typed currentness refusal until the
    explicit teardown frees the owner -- no epoch reset,
    no retry, no revival of the old usable state."""

    SESSION_OWNED_BYTES_OVER_BOUND = "session_owned_bytes_over_bound"
    PROCESS_OWNED_BYTES_OVER_BOUND = "process_owned_bytes_over_bound"
    DUPLICATE_OWNER = "duplicate_owner"
    OWNER_NAMESPACE_MISMATCH = "owner_namespace_mismatch"
    EPOCH_FENCED = "epoch_fenced"
    REVISION_MISMATCH = "revision_mismatch"
    STALE_STATE_REVISION = "stale_state_revision"
    WORK_IN_FLIGHT = "work_in_flight"
    OWNER_QUARANTINED = "owner_quarantined"


class RamStateSnapshot(_GraphFrozen):
    """One immutable retained record set for one live owner.

    ``namespace`` / ``state`` / ``result`` are the EXACT 018-p
    namespace and state and the ACTUAL 018-t complete-consumer
    result by immutable reference: the admitted original bundle
    bytes, the carried R/Q/F/E graph evidence and the ACTUAL S
    admission parent (its entries, key records, path
    associations and reverse index) all reach through
    ``result``.  ``revision`` is the owner CAS fence (one per
    committed admission; the serialization/commit fence, never
    a clock).  ``epoch`` is the explicit cache epoch of the
    live owner (the registry allocates DISTINCT epochs to
    fenced successors, so a stale holder of an old epoch can
    never match a re-acquired owner).  ``owned_bytes`` is the
    charged conservative occupancy of the owner's base
    metadata, the retained record set, the historical
    immutable entry catalog and the retained snapshot
    storage itself, under the documented recipe (originals
    AND metadata, retained history included, on ACTUAL
    measured shallow object/container sizes plus identity-
    deduplicated referents; the 018-t
    ``entry_source_bytes`` copy-budget counter is NOT
    occupancy)."""

    namespace: InstanceOf[RootRegionLineageNamespace]
    state: InstanceOf[RootRegionLineageState]
    result: InstanceOf[RootRegionAdmissionResult]
    revision: int = Field(ge=1)
    epoch: int = Field(ge=1)
    owned_bytes: int = Field(ge=0)


class RamStateAdmissionResult(_GraphFrozen):
    """The typed admit() result (019-a).

    ``ADMITTED`` carries the new snapshot and its charged
    bytes.  ``REFUSED`` carries the exact unchanged current
    snapshot (or None on an empty owner), the zero new charge,
    the unchanged occupancy and -- for the two capacity
    refusals only -- the fixed typed 503 backpressure status.
    A refused admission leaves existing entries, the
    historical catalog, revision, graph, indices and
    occupancy unchanged."""

    outcome: RamStateOutcome
    limitation: RamStateLimitation | None = None
    snapshot: RamStateSnapshot | None = None
    charged_bytes: int = Field(ge=0)
    session_owned_bytes: int = Field(ge=0)
    process_owned_bytes: int = Field(ge=0)
    revision: int = Field(ge=0)
    http_status: int | None = None


class RamStateLookupResult(_GraphFrozen):
    """The typed lookup() result (019-a).

    ``FOUND`` carries the ACTUAL matched CURRENT admission row
    by reference (root or FILE row; the first closed row match
    on the stable semantic ``content_key`` -- the historical
    immutable entry catalog is retained and charged but never
    lookup-eligible, current usability stays separate).
    ``NOT_FOUND`` carries the exact fence domain when one
    fired (a foreign trusted namespace, a fenced/stale epoch)
    or None on an empty owner, a non-ready retained result or
    an absent key.  A lookup is a pure memory read: it never
    mutates state, never reads a disk-backed store and never
    re-creates a torn-down owner."""

    outcome: RamStateOutcome
    limitation: RamStateLimitation | None = None
    entry: InstanceOf[RootRegionAdmissionEntry] | None = None
    revision: int = Field(ge=0)
    epoch: int = Field(ge=0)


class RamStateTeardownResult(_GraphFrozen):
    """The typed teardown() result (019-a).

    ``TEARDOWN`` releases exactly this namespace's owned
    record set, the historical catalog, the owner base
    metadata and the registry reference (``freed_bytes``),
    fences the old epoch and preserves every other owner; the
    registry allocates a DISTINCT epoch to an explicit
    re-acquire.  A later operation on the fenced owner
    returns the typed ``EPOCH_FENCED`` refusal; no hidden
    expiry and no auto-recreation through a normal lookup."""

    outcome: RamStateOutcome
    limitation: RamStateLimitation | None = None
    freed_bytes: int = Field(ge=0)
    session_owned_bytes: int = Field(ge=0)
    process_owned_bytes: int = Field(ge=0)

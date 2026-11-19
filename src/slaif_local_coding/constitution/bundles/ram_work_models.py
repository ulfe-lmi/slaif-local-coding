"""Pure versioned bounded inert RAM work (single-flight) models
(objective 019-b, second slice).

This module carries the versioned data models of the NEW bounded
async same-full-key single-flight plane over the accepted 019-a
RAM owner/store foundation: the explicit ``RamWorkBounds``
configuration record (the ONE process-wide active leader is a
closed constant; the configurable positive non-bool values are
the pending distinct-key queue, the waiters-per-key bound, the
prepared-output size bound and the work time bound, all closed
against documented conservative hard limits), the closed
``RamWorkOutcome`` / ``RamWorkAttemptState`` / ``RamWorkLimitation``
vocabulary, the fixed typed backpressure / conflict / budget
status mapping for the work plane, the immutable
``RamWorkPayload`` (a validated bounded prepared payload,
synthetic at this inert boundary -- actual compiler/tokenizer
semantic validation is 021), the immutable ``RamWorkAttempt``
terminal attempt record (the retained, charged, never-evicted
attempt metadata: full key, live epoch, state, outcome,
limitation, actual invocation count and the retained payload on
success), and the typed request / teardown result records.

The models are INERT: they wire no runtime, expose no operation
and claim no actual compiler / cache hit / HTTP readiness.  The
owning component (``ram_work``) supplies the actual bounded
orchestration: the ratified attempt policy (claim / join /
terminal, no retry), the bounded leader / queue / waiter
ownership, the cancellation law, the owner / namespace / epoch /
current-key publication fences and the shared conservative
occupancy charging under the SAME process / session ceilings as
the 019-a store.  All existing 018 and 019-a public signatures,
defaults, schemas, version tags, recipe bytes and behavior
remain intact.
"""

from __future__ import annotations

from enum import StrEnum
from typing import Any, Final, TypeGuard

from pydantic import Field, field_validator

from .graph_models import _fixed, _GraphFrozen
from .ram_state_models import RamStateLimitation

RAM_WORK_CONTRACT_VERSION = "cache-ram-work/v1"
RAM_WORK_POLICY_VERSION = "ram-work-policy/v1"

#: The closed ONE process-wide active leader (a constant, not a
#: configurable value: the default and only active-leader
#: count of the v1 single-flight plane).
RAM_WORK_ACTIVE_LEADERS = 1

#: The documented conservative fixed reservation charged for
#: ONE live dispatch task reference (the runtime task object and
#: its retained work-closure reference are not safely measurable
#: shallow containers; the reservation bounds them).  Its scope
#: explicitly INCLUDES the retained active-key tuple (the
#: (owner, content-key) pair held from dispatch to finalization;
#: the ACTUAL 2-tuple measures 56 bytes on the pinned CPython
#: 3.12 toolchain, inside this reservation) -- no separate
#: charge is made for it.
RAM_WORK_TASK_RESERVATION_BYTES = 4096

#: The documented conservative closed reservation charged for
#: ONE retained QUEUED (owner, content-key) entry of the
#: process-wide queue: the shallow deque charge covers the
#: block allocation only and omits the entry's tuple body.
#: The ACTUAL 2-tuple measures 56 bytes on the pinned
#: CPython 3.12 toolchain; this reservation is the small
#: bounded conservative envelope charged when the entry is
#: retained (at the claim's publication) and released exactly
#: once when the entry leaves the queue (dispatch / fenced
#: finalization / teardown).
RAM_WORK_QUEUE_ENTRY_RESERVATION_BYTES = 64

#: The documented conservative closed reservation for the ONE
#: owned PUMP task (the asyncio task object driving queue
#: dispatch is a runtime object not safely measurable as a
#: shallow container).  It is GLOBAL: charged exactly once
#: into the coordinator base BEFORE any owner or claim (part
#: of the shared coordinator shell charge, alongside the
#: instance / map / queue shells and the retained work-bounds
#: record) and held for the coordinator's whole lifetime --
#: it covers the ONE pump task whenever it is scheduled, so
#: pump creation is never a ceiling decision, is never
#: deferred under pressure, and no claimed queue can be left
#: without its scheduling trigger.
RAM_WORK_PUMP_TASK_RESERVATION_BYTES = 4096

#: The documented conservative fixed reservation charged for
#: ONE retained waiter future reference (the runtime future
#: object is not a safely measurable shallow container).
RAM_WORK_WAITER_RESERVATION_BYTES = 1024

#: The documented conservative closed reservation charged for
#: ONE CLAIMED attempt's MANDATORY terminal record BEFORE the
#: claim is accepted (charged once per attempt, at the
#: claimant's claim; a same-key join never reserves a second
#: terminal slot).  It is an UPPER BOUND on the terminal
#: record's ACTUAL charge under the 019-a measured recipe --
#: the measured worst-case record (64-hex content key, a
#: 2**63 epoch integer, every closed enum / limitation field
#: set, invocations 1) is 1909 bytes on the pinned CPython
#: 3.12 toolchain, with the margin covering build-flag header
#: variance.  The terminal CATALOG's own growth (the reserved
#: slot's tuple key and any dict resize step, which grows
#: with catalog size) is NOT covered by this reservation:
#: the slot is PRE-ALLOCATED at claim time and its actual
#: growth is charged into the same BEFORE-retention
#: recomputation that BOTH ceilings verify.  Together the two
#: make the mandatory terminalization -- the slot's record
#: swap at finalization, or a queued cancellation -- always
#: non-positive in delta, so it can NEVER cross either
#: ceiling at any later resize boundary.  There is no soft-
#: cap exception for terminal metadata.
RAM_WORK_TERMINAL_RESERVATION_BYTES = 2560

#: The default bound on DISTINCT pending keys (queued plus the
#: active key) in the process-wide queue.
RAM_WORK_MAX_PENDING_DISTINCT_KEYS_DEFAULT = 32

#: The default bound on waiters per single key.
RAM_WORK_MAX_WAITERS_PER_KEY_DEFAULT = 8

#: The default bound on ONE prepared payload size (bytes).
RAM_WORK_MAX_OUTPUT_BYTES_DEFAULT = 1_048_576

#: The default bound on ONE admitted work dispatch (seconds).
RAM_WORK_MAX_WORK_SECONDS_DEFAULT = 30.0

#: The closed conservative hard ceiling on the pending distinct
#: key bound.
RAM_WORK_MAX_PENDING_DISTINCT_KEYS_HARD = 4096

#: The closed conservative hard ceiling on the waiters-per-key
#: bound.
RAM_WORK_MAX_WAITERS_PER_KEY_HARD = 1024

#: The closed conservative hard ceiling on the prepared payload
#: size (64 MiB).
RAM_WORK_MAX_OUTPUT_BYTES_HARD = 67_108_864

#: The closed conservative hard ceiling on the work time bound
#: (600 seconds).
RAM_WORK_MAX_WORK_SECONDS_HARD = 600.0


def _ram_work_int_in(value: object, low: int, high: int) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and low <= value <= high


class RamWorkBounds(_GraphFrozen):
    """The explicit configurable single-flight bounds (019-b).

    ``max_pending_distinct_keys`` bounds the DISTINCT pending
    keys (queued plus the active key) in the process-wide queue
    (a same-key join never consumes another distinct-key
    reservation); ``max_waiters_per_key`` bounds the waiters on
    ONE key; ``max_output_bytes`` bounds ONE prepared payload;
    ``max_work_seconds`` bounds ONE admitted dispatch.  All are
    STRICT positive non-bool values (bool / wrong-type inputs
    refuse before any coercion) closed against the documented
    conservative hard ceilings.  The active-leader count is the
    closed constant ``RAM_WORK_ACTIVE_LEADERS`` (ONE), not a
    configurable value."""

    max_pending_distinct_keys: int = Field(
        default=RAM_WORK_MAX_PENDING_DISTINCT_KEYS_DEFAULT,
        ge=1,
        le=RAM_WORK_MAX_PENDING_DISTINCT_KEYS_HARD,
        strict=True,
    )
    max_waiters_per_key: int = Field(
        default=RAM_WORK_MAX_WAITERS_PER_KEY_DEFAULT,
        ge=1,
        le=RAM_WORK_MAX_WAITERS_PER_KEY_HARD,
        strict=True,
    )
    max_output_bytes: int = Field(
        default=RAM_WORK_MAX_OUTPUT_BYTES_DEFAULT,
        ge=1,
        le=RAM_WORK_MAX_OUTPUT_BYTES_HARD,
        strict=True,
    )
    max_work_seconds: float = Field(
        default=RAM_WORK_MAX_WORK_SECONDS_DEFAULT,
        gt=0.0,
        le=RAM_WORK_MAX_WORK_SECONDS_HARD,
    )

    @field_validator(
        "max_pending_distinct_keys", "max_waiters_per_key", "max_output_bytes", mode="after"
    )
    @classmethod
    def _v_work_int(cls, value: object, info: Any) -> int:
        # The closed fence runs AFTER the strict raw-integer
        # validation (strict ints refuse bool / float / string
        # BEFORE coercion); this guard keeps the fixed private
        # error on the closed boundary.
        if isinstance(value, bool) or not isinstance(value, int):
            raise _fixed("the ram work integer bounds must be positive integers")
        return value

    @field_validator("max_work_seconds", mode="before")
    @classmethod
    def _v_work_seconds(cls, value: object, info: Any) -> float:
        # The closed fence runs on the RAW value BEFORE any
        # coercion: bool / string / wrong-type inputs refuse
        # here (a strict float annotation would reject legal
        # integer seconds, so the raw fence is explicit); a
        # legal integer seconds value stays legal.
        if isinstance(value, bool):
            raise _fixed("the ram work time bound must be a positive non-bool number")
        if isinstance(value, int):
            seconds = float(value)
        elif isinstance(value, float):
            seconds = value
        else:
            raise _fixed("the ram work time bound must be a positive non-bool number")
        if not 0.0 < seconds <= RAM_WORK_MAX_WORK_SECONDS_HARD:
            raise _fixed("the ram work time bound is outside the closed bound")
        return seconds


def ram_work_bounds_shape_ok(bounds: object) -> TypeGuard[RamWorkBounds]:
    """RAM-WORK-PRIVATE closed fence over the work bounds
    record (the registry's own preflight boundary): ORIGINAL
    class, field existence, exact non-bool values under the
    hard ceilings, BEFORE any serializer visit.  Valid stricter
    original-class instances stay legal; shadow subclasses and
    malformed copies are not."""
    return (
        type(bounds) is RamWorkBounds
        and hasattr(bounds, "max_pending_distinct_keys")
        and hasattr(bounds, "max_waiters_per_key")
        and hasattr(bounds, "max_output_bytes")
        and hasattr(bounds, "max_work_seconds")
        and _ram_work_int_in(
            bounds.max_pending_distinct_keys, 1, RAM_WORK_MAX_PENDING_DISTINCT_KEYS_HARD
        )
        and _ram_work_int_in(bounds.max_waiters_per_key, 1, RAM_WORK_MAX_WAITERS_PER_KEY_HARD)
        and _ram_work_int_in(bounds.max_output_bytes, 1, RAM_WORK_MAX_OUTPUT_BYTES_HARD)
        and isinstance(bounds.max_work_seconds, (int, float))
        and not isinstance(bounds.max_work_seconds, bool)
        and 0 < float(bounds.max_work_seconds) <= RAM_WORK_MAX_WORK_SECONDS_HARD
    )


class RamWorkOutcome(StrEnum):
    """The closed RAM work outcome vocabulary (019-b).

    Request results use ``HIT`` / ``COMPLETED`` / ``JOINED`` /
    ``REFUSED`` / ``FAILED``; terminal attempt records use
    ``COMPLETED`` / ``FAILED`` / ``CANCELLED``; the teardown
    result uses ``TEARDOWN`` / ``REFUSED``."""

    HIT = "hit"
    COMPLETED = "completed"
    JOINED = "joined"
    REFUSED = "refused"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TEARDOWN = "teardown"


class RamWorkAttemptState(StrEnum):
    """The closed retained attempt state vocabulary (019-b):
    ``QUEUED`` (claimed, not yet dispatched), ``ACTIVE``
    (dispatched under the ONE active leader) and ``TERMINAL``
    (the retained terminal record)."""

    QUEUED = "queued"
    ACTIVE = "active"
    TERMINAL = "terminal"


class RamWorkLimitation(StrEnum):
    """The closed work-plane limitation vocabulary (019-b).

    ``PENDING_KEYS_OVER_BOUND`` and ``WAITERS_PER_KEY_OVER_BOUND``
    are the PRE-CLAIM queue / waiter capacity refusals (fixed
    typed 503, zero invocation, no attempt); ``KEY_NOT_CURRENT``
    is the currentness fence (the full key is not among the
    owner's ACTUAL current admitted keys, or a late completion
    cannot be published because the key ceased to be current --
    fixed 409); ``OWNER_ABSENT`` is the no-live-owner fence
    (fixed 409); ``OWNER_TORN_DOWN`` is the fenced-owner fence
    (fixed 503); ``WORK_FAILED`` / ``WORK_TIMEOUT`` are the
    unclassified-failure / time-bound terminal failures (fixed
    503); ``OUTPUT_OVER_BOUND`` / ``INVALID_OUTPUT`` /
    ``TRUNCATED_OUTPUT`` are the bounded-output shape refusals
    (fixed 422); ``ALL_WAITERS_DEPARTED`` is the
    all-waiters-gone terminal (the owned work is cancelled and
    awaited; the attempt is terminal unsuccessful, fixed 503);
    ``EPOCH_CHANGED`` is the stale-epoch publication fence
    (fixed 409).  The two store capacity fences
    (``session_owned_bytes_over_bound`` /
    ``process_owned_bytes_over_bound`` on
    ``RamStateLimitation``) are shared: the work plane charges
    the SAME ceilings and carries them through with the fixed
    typed 503 backpressure contract.  The store
    ``owner_quarantined`` fence (the 019-c adverse-currentness
    quarantine) is carried through with the fixed typed 409
    currentness refusal: a quarantined owner never serves a
    retained payload, and no new invocation is ever started."""

    PENDING_KEYS_OVER_BOUND = "pending_keys_over_bound"
    WAITERS_PER_KEY_OVER_BOUND = "waiters_per_key_over_bound"
    KEY_NOT_CURRENT = "key_not_current"
    OWNER_ABSENT = "owner_absent"
    OWNER_TORN_DOWN = "owner_torn_down"
    WORK_FAILED = "work_failed"
    WORK_TIMEOUT = "work_timeout"
    OUTPUT_OVER_BOUND = "output_over_bound"
    INVALID_OUTPUT = "invalid_output"
    TRUNCATED_OUTPUT = "truncated_output"
    ALL_WAITERS_DEPARTED = "all_waiters_departed"
    EPOCH_CHANGED = "epoch_changed"
    RECOVERY_IN_FLIGHT = "recovery_in_flight"


#: The closed fixed typed status mapping of the work-plane
#: limitations (HTTP wiring is 022; this declares the contract
#: at the inert boundary).
RAM_WORK_HTTP_STATUS: Final[dict[RamWorkLimitation, int]] = {
    RamWorkLimitation.PENDING_KEYS_OVER_BOUND: 503,
    RamWorkLimitation.WAITERS_PER_KEY_OVER_BOUND: 503,
    RamWorkLimitation.KEY_NOT_CURRENT: 409,
    RamWorkLimitation.OWNER_ABSENT: 409,
    RamWorkLimitation.OWNER_TORN_DOWN: 503,
    RamWorkLimitation.WORK_FAILED: 503,
    RamWorkLimitation.WORK_TIMEOUT: 503,
    RamWorkLimitation.OUTPUT_OVER_BOUND: 422,
    RamWorkLimitation.INVALID_OUTPUT: 422,
    RamWorkLimitation.TRUNCATED_OUTPUT: 422,
    RamWorkLimitation.ALL_WAITERS_DEPARTED: 503,
    RamWorkLimitation.EPOCH_CHANGED: 409,
    RamWorkLimitation.RECOVERY_IN_FLIGHT: 503,
}

#: The closed shared capacity-status mapping for the two store
#: ceiling fences carried through the work plane.
RAM_WORK_CAPACITY_STATUS: Final[dict[RamStateLimitation, int]] = {
    RamStateLimitation.SESSION_OWNED_BYTES_OVER_BOUND: 503,
    RamStateLimitation.PROCESS_OWNED_BYTES_OVER_BOUND: 503,
}


def ram_work_http_status(
    limitation: RamWorkLimitation | RamStateLimitation | None,
) -> int | None:
    """The closed fixed typed status for a work-plane
    limitation (the shared store capacity fences map to the
    fixed 503 backpressure contract)."""
    if limitation is None:
        return None
    if isinstance(limitation, RamWorkLimitation):
        return RAM_WORK_HTTP_STATUS[limitation]
    if limitation is RamStateLimitation.OWNER_QUARANTINED:
        return 409
    return RAM_WORK_CAPACITY_STATUS.get(limitation)


class RamWorkSeamReason(StrEnum):
    """The closed injected-seam typed failure reasons (019-b):
    ``invalid`` (the seam declared its output invalid /
    unparseable) and ``truncated`` (the seam declared its
    output truncated).  Any other exception is the unclassified
    ``WORK_FAILED`` terminal; raw exception content is never
    retained."""

    INVALID = "invalid"
    TRUNCATED = "truncated"


def _content_key_shape_ok(value: object) -> bool:
    if type(value) is not str or len(value) != 64:
        return False
    return all(c in "0123456789abcdef" for c in value)


class RamWorkPayload(_GraphFrozen):
    """ONE retained immutable prepared payload (019-b).

    ``content_key`` is the ACTUAL admitted full semantic content
    key the payload was prepared for; ``data`` is the bounded
    prepared output (the injected seam is synthetic at this
    inert boundary -- the shape and the size bound are validated
    HERE; actual compiler / tokenizer semantic validation is
    021).  A payload is retained by identity in the owner work
    state, charged into occupancy, reusable on a genuinely
    proven compatible revert of the same key / epoch without a
    new invocation, and released only at explicit teardown."""

    content_key: str
    data: bytes

    @field_validator("content_key", mode="before")
    @classmethod
    def _v_payload_key(cls, value: object) -> str:
        if not _content_key_shape_ok(value):
            raise _fixed("the ram work payload content key is malformed")
        return value  # type: ignore[return-value]

    @field_validator("data", mode="before")
    @classmethod
    def _v_payload_data(cls, value: object) -> bytes:
        if type(value) is not bytes:
            raise _fixed("the ram work payload data must be bounded bytes")
        if len(value) > RAM_WORK_MAX_OUTPUT_BYTES_HARD:
            raise _fixed("the ram work payload data exceeds the closed hard ceiling")
        return value


class RamWorkAttempt(_GraphFrozen):
    """The retained TERMINAL attempt record (019-b).

    The full semantic content / configuration key joined to the
    genuine live cache ``epoch`` defines ONE admitted work
    attempt; this record is the retained, charged,
    never-evicted terminal metadata (a terminal failure is
    re-served to a later same-key / epoch request with the SAME
    fixed typed limitation and zero new invocations -- never
    evicted to retry; only an explicit teardown / new ownership
    lifetime or the 020 authenticated restart / recovery creates
    a genuine new epoch).  ``invocations`` is the ACTUAL count
    of the injected work for THIS claimed attempt (zero when the
    dispatch was cancelled before its first execution -- a queued
    cancellation or an unstarted dispatch task -- and one when the
    dispatch actually ran; a pre-claim refusal claims no attempt
    and retains no terminal record).  A ``COMPLETED`` attempt
    retains its payload
    by reference (the payload store retains it independently,
    so a supersession of the current key never destroys a valid
    immutable payload)."""

    content_key: str
    epoch: int = Field(ge=1)
    state: RamWorkAttemptState
    outcome: RamWorkOutcome | None = None
    limitation: RamWorkLimitation | RamStateLimitation | None = None
    invocations: int = Field(ge=0, le=1)
    payload: RamWorkPayload | None = None

    @field_validator("content_key", mode="before")
    @classmethod
    def _v_attempt_key(cls, value: object) -> str:
        if not _content_key_shape_ok(value):
            raise _fixed("the ram work attempt content key is malformed")
        return value  # type: ignore[return-value]


class RamWorkRequestResult(_GraphFrozen):
    """The typed resolve() result (019-b).

    ``HIT`` carries the ACTUAL retained payload (a repeat
    request for a key with a valid retained payload of the same
    epoch: zero new invocations, RAM-only).  ``COMPLETED``
    carries the payload published by THIS request's attempt;
    ``JOINED`` carries the payload published by the SHARED
    attempt another request claimed (zero invocations for this
    request).  ``REFUSED`` is a pre-claim refusal (queue /
    waiter capacity, currentness or owner fence: zero
    invocations, no attempt claimed).  ``FAILED`` is the
    terminal unsuccessful attempt outcome (the SAME fixed typed
    limitation a later same-key / epoch request re-serves).
    ``invocations`` is this request's own count (at most one);
    ``attempt_invocations`` is the shared attempt's actual
    count.  The capacity fences carry the fixed typed 503
    backpressure status."""

    outcome: RamWorkOutcome
    limitation: RamWorkLimitation | RamStateLimitation | None = None
    payload: RamWorkPayload | None = None
    invocations: int = Field(ge=0, le=1)
    attempt_invocations: int = Field(ge=0, le=1)
    epoch: int = Field(ge=0)
    http_status: int | None = None


class RamWorkTeardownResult(_GraphFrozen):
    """The typed async work-teardown result (019-b).

    ``TEARDOWN`` fences the owner's work plane, cancels AND
    awaits its queued / active / shared work (the typed
    outcome re-served to every still-waiting waiter) and then
    releases the store owner AND this owner's work occupancy
    in ONE critical section -- the work plane stays fenced
    until the owner is actually torn down, so no same-epoch
    reset window can mint fresh attempts on the retained
    owner -- preserving every other owner / session
    (``freed_bytes`` is the TOTAL process occupancy released
    by the teardown: store plus work).  ``REFUSED`` carries
    the exact fence domain (no live owner, an already-fenced
    owner / work plane, a foreign trusted namespace) with
    zero release."""

    outcome: RamWorkOutcome
    limitation: RamWorkLimitation | RamStateLimitation | None = None
    freed_bytes: int = Field(ge=0)
    attempts_cancelled: int = Field(ge=0)
    waiters_notified: int = Field(ge=0)
    http_status: int | None = None

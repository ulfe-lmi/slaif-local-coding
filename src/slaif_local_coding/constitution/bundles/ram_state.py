"""Bounded inert RAM state owner and atomic store (objective
019-a, first store slice).

This component implements the inert per-session RAM ownership
and bounded atomic admission/lifecycle foundation over the
accepted 018 immutable graph/bundle/namespace contracts:

- ONE live owner per trusted 018-p namespace; every lookup /
  commit / lifecycle operation is bound to the complete
  trusted namespace/configuration (the ACTUAL trusted
  namespace record, by identity -- a value-equal foreign copy
  cannot operate), the one live owner and the explicit cache
  epoch.  The registry boundary re-runs the COMPLETE 018-p
  namespace law on every acquire / new_owner / get and joins
  a live registration by EXACT record identity: a value-equal
  foreign copy carrying the registered lineage key is refused
  at the registry, never handed the registered owner.  Public
  body/header strings cannot mint ownership.  The unsupported
  multi-worker / duplicate live-owner configuration is
  rejected at the component boundary with the fixed typed
  error; a directly constructed unregistered owner refuses
  every operation with a fixed typed error; the actual
  application startup wiring of a shared process registry is
  022, not yet earned here.

- Retained state is the EXACT 018-p state and the ACTUAL
  018-t complete-consumer result by immutable reference (the
  admitted original bundle bytes, the carried R/Q/F/E graph
  evidence, the ACTUAL S admission parent with its entries,
  key records, path associations and reverse index, and the
  retained P/D history including unreachable, historical and
  not-admitted sources).  Before any commit the ACTUAL
  complete 018-t result law is re-run (the full model
  revalidation including the phase-5 ACTUAL S admission-
  parent revalidation): a bypass-copied or forged result,
  including a forged canonical leaf, a forged retained group
  or a broken reverse/count relation, refuses with the fixed
  sanitized boundary error.  Superseding a current snapshot
  does NOT destroy still-valid historical immutable content:
  every admitted admission row is retained in the owner
  HISTORICAL IMMUTABLE ENTRY CATALOG (identity-deduplicated,
  charged into occupancy, never lookup-eligible -- current
  usability is the current snapshot rows alone).  There is no
  disk-backed normal lookup, no TTL/LRU timer, no automatic
  dormant scan, no capacity eviction and no source
  destruction.

- Conservative explicit accounting charges EVERY owned
  retained component (originals AND metadata, including the
  owner base at creation, the historical catalog tuple and
  the retained snapshot storage) BEFORE admission, on the
  ACTUAL measured shallow object/container sizes (sys.
  getsizeof) plus the ACTUAL identity-deduplicated
  referents, and the atomic session/process ceiling checks
  run on that charge (at-limit accepted, over-limit refused
  with the fixed typed 503 backpressure contract at this
  inert boundary; a refused admission leaves entries,
  catalog, revision, graph, indices and occupancy
  unchanged).  A NEW owner is refused atomically BEFORE
  registration when EITHER ceiling cannot cover its owned
  base metadata.  The PROCESS ceiling is the REGISTRY
  level: an owner session override can never bypass it.
  Shared immutable records are deduplicated by ACTUAL
  identity within one owner charge, while cross-session
  sharing never exempts a session from its own charge.  The
  018-t ``entry_source_bytes`` counter is a copy-budget
  counter, not occupancy; temporary bounded transformation
  work of a later operation is a distinct domain and never
  enters committed occupancy; no total-RSS limit is promised.

- Versioned/expected-revision commit inputs make the
  commit-CAS binding UNAVOIDABLE: the expected owner
  revision is a MANDATORY commit input, a stale concurrent
  commit refuses, and the LINEAGE fence refuses a rollback:
  an older genuine P state than the retained one, or a
  DISTINCT state object at the SAME retained P revision (a
  divergent lineage fork -- the state revision is a CAS
  fence, never an arrival clock), is refused with the fixed
  ``stale_state_revision`` limitation; an identical retained
  state replay is separate.  No lock is held across model IO
  or an SSE response: the short process-registry critical
  section covers the pure-memory fence/charge/ceiling/commit
  sequence and re-checks every precondition after acquiring;
  async task ownership is later 019 work.

- Explicit session teardown releases exactly the owned state
  of that namespace, the historical catalog, the owner base
  metadata and the registry reference, fences the old epoch
  (the registry allocates a DISTINCT epoch to an explicit
  re-acquire, so a stale holder of the old epoch cannot
  match the new owner) and preserves the other owners; no
  hidden expiry and no auto-recreation of a torn-down owner
  through a normal lookup.

The component is INERT: it wires no runtime, exposes no HTTP
and claims no async single-flight/cancellation or actual
compiler/cache hit (C03 remains unearned until its mechanism
and owning compiler layers pass).  All existing 018 public
signatures, defaults, schemas, version tags, recipe bytes and
behavior remain intact.
"""

from __future__ import annotations

import sys
import threading
from typing import TYPE_CHECKING, TypeGuard

from pydantic import BaseModel

if TYPE_CHECKING:
    from .ram_work import RamWorkCoordinator

from .ram_state_models import (
    RAM_HTTP_CAPACITY_STATUS,
    RAM_OWNED_BYTES_HARD_CEILING,
    RamStateAdmissionResult,
    RamStateBounds,
    RamStateLimitation,
    RamStateLookupResult,
    RamStateOutcome,
    RamStateSnapshot,
    RamStateTeardownResult,
    ram_state_bounds_shape_ok,
)
from .root_region_admission_models import RootRegionAdmissionEntry
from .root_region_admission_result_models import (
    RootRegionAdmissionOutcome,
    RootRegionAdmissionResult,
)
from .root_region_lineage_models import (
    RootRegionLineageNamespace,
    RootRegionLineageState,
)


class RamStateError(Exception):
    """Fixed typed RAM-state boundary error base (019-a)."""


class RamStateInputError(RamStateError):
    """A malformed, detached or non-joined input record (or a
    malformed ceiling/revision/epoch input) at the owner
    component boundary (the closed-field law): the operation
    is refused BEFORE any charge, traversal or commit work."""


class RamStateCapacityError(RamStateError):
    """A ceiling (the registry PROCESS ceiling or the owner
    SESSION ceiling) cannot cover the NEW owner owned base
    metadata: the construction is refused atomically BEFORE
    registration with the fixed typed error."""


class RamStateDuplicateOwnerError(RamStateError):
    """An unsupported multi-worker / duplicate live-owner
    configuration for one trusted namespace (component
    boundary)."""

    MESSAGE = (
        "a live owner already exists for this namespace (unsupported multi-worker configuration)"
    )


class RamStateAccountingError(RamStateError):
    """An unaccountable record type or a detached record field
    inside the retained object graph: the closed recipe fails
    closed rather than under-charging."""


# --- The documented conservative occupancy recipe -----------
#
# Closed type allow-list; an unknown retained type raises
# RamStateAccountingError (fail closed).  Each retained object
# is charged ONCE per owner walk, deduplicated by ACTUAL
# object identity (id): a shared immutable record referenced
# by several fields occupies memory once.  The charge is the
# ACTUAL allocated size of the owned shallow object/container
# (sys.getsizeof: the real str/bytes payload, the real
# multi-limb int, the real tuple/list/set item table, the
# real dict table, the real model instance) PLUS the ACTUAL
# referents it retains, walked recursively under the same
# identity deduplication (the pydantic instance field
# container and its fields-set are retained components
# too).  The quantities are platform actuals read at charge
# time; the recipe is deterministic, over-charges only where
# a retained value is a shared singleton, never under-
# charges, never reads a disk store and never promises total-
# RSS.  The owner base metadata (the owner shell), the
# historical catalog tuple and the retained snapshot storage
# are owned components charged with the record set they
# accompany; the shared registry shell (its instance, its
# live-owner map, its critical-section lock, its counters) is
# charged into the process occupancy once at registry
# construction, and the ACTUAL table growth of the shared
# live-owner map is charged as it happens and retained at its
# high water as an explicitly conservative reservation:
# CPython tables do not shrink when owners are removed, and
# a smaller candidate replacement may shrink the ACTUAL
# table while the charge stays (it is retained container
# allocation, never part of any session's freed bytes).

_RAM_MEASURED: dict[str, int] = {}


def _measured_owner_shell() -> int:
    """The ACTUAL measured owner shell size, cached after the
    first read.  The shared live-owner map table is NOT part
    of the per-owner charge: it is charged at the registry as
    actual table growth, retained at high water."""
    if not _RAM_MEASURED:
        _RAM_MEASURED["shell"] = sys.getsizeof(object.__new__(RamStateOwner))
    return _RAM_MEASURED["shell"]


def _charge_object(value: object, seen: set[int]) -> int:
    """Charge ONE retained object: its ACTUAL shallow size
    (sys.getsizeof) plus its ACTUAL retained referents,
    identity-deduplicated within the owner walk."""
    if value is None:
        return 0
    oid = id(value)
    if oid in seen:
        return 0
    seen.add(oid)
    total = sys.getsizeof(value)
    if isinstance(value, (bool, int, float, str, bytes, bytearray, memoryview)):
        return total
    if isinstance(value, (tuple, list, set, frozenset)):
        for item in value:
            total += _charge_object(item, seen)
        return total
    if isinstance(value, dict):
        for key, item in value.items():
            total += _charge_object(key, seen)
            total += _charge_object(item, seen)
        return total
    if isinstance(value, BaseModel):
        field_container = getattr(value, "__dict__", None)
        if field_container is not None:
            total += _charge_object(field_container, seen)
        fields_set = getattr(value, "__pydantic_fields_set__", None)
        if fields_set is not None:
            total += _charge_object(fields_set, seen)
        return total
    raise RamStateAccountingError(f"unaccountable retained record type: {type(value).__name__}")


def ram_owner_base_charge(namespace: RootRegionLineageNamespace) -> int:
    """The conservative occupancy of ONE owner base metadata:
    the ACTUAL measured owner shell and the retained trusted
    namespace record itself (charged at creation, released at
    teardown).  The shared live-owner map table is charged at
    the registry (actual growth, high-water retained) and is
    not part of the per-owner base."""
    seen: set[int] = set()
    return _measured_owner_shell() + _charge_object(namespace, seen)


def ram_retained_owned_bytes(
    namespace: RootRegionLineageNamespace,
    state: RootRegionLineageState,
    result: RootRegionAdmissionResult,
    history: tuple[RootRegionAdmissionEntry, ...] = (),
    snapshot: RamStateSnapshot | None = None,
) -> int:
    """The conservative explicit occupancy charge of ONE
    retained owner record set -- the owner base metadata (the
    measured shell, the retained trusted namespace), the
    (state, result) records, the
    historical immutable entry catalog (its tuple AND its
    retained entry objects) and, when given, the retained
    snapshot storage (its model instance, its field container
    and its scalar fields, the record references identity-
    deduplicated) -- computed under the documented closed
    recipe with ACTUAL-identity deduplication within this one
    owner charge.

    The walk is deterministic (base, then namespace, state,
    result, then the catalog, then the snapshot) and a shared
    immutable record (the exact same object referenced by
    several fields) is charged once here, while every distinct
    retained component -- originals AND metadata, the retained
    P/D history and sources even when unreachable, historical
    or not admitted, the carried R/Q/F/E graphs, the admission
    records and indexes, and the retained historical entry
    objects -- is charged in full.  The 018-t
    ``entry_source_bytes`` counter is a copy-budget counter
    and never stands in for this occupancy.  Temporary bounded
    transformation work of a later operation is a distinct
    domain and never enters committed occupancy; no total-RSS
    limit is promised."""
    seen: set[int] = set()
    total = _measured_owner_shell()
    for record in (namespace, state, result, history):
        total += _charge_object(record, seen)
    if snapshot is not None:
        total += _charge_object(snapshot, seen)
    return total


class RamStateOwner:
    """ONE live per-session RAM owner for one trusted 018-p
    namespace (019-a).

    ``admit`` re-joins the complete trusted namespace and the
    closed T result law (the ACTUAL complete model
    revalidation, including the phase-5 ACTUAL S admission-
    parent revalidation) BEFORE any charge, honors the
    MANDATORY commit-CAS and the lineage-rollback /
    divergent-fork fences, charges the conservative
    occupancy (base + records + historical catalog + snapshot
    storage) and enforces the atomic session ceiling (this
    owner) and process ceiling (the registry) -- all inside
    the short process-registry critical section, with every
    precondition re-checked after acquiring.  ``lookup`` is a
    pure memory read of the CURRENT admission rows only (the
    historical catalog is charged but never lookup-eligible).
    ``teardown`` releases the owned state, catalog, base
    metadata and registry reference and fences the old epoch.
    A directly constructed unregistered owner refuses every
    operation with a fixed typed error.  No lock is held
    across model IO or an SSE response; async task ownership
    is later 019 work."""

    __slots__ = (
        "namespace",
        "session_max_owned_bytes",
        "epoch",
        "epoch_fenced",
        "owned_bytes",
        "_registry",
        "_snapshot",
        "_history",
        "_registration",
        "_quarantined",
    )

    def __init__(
        self,
        namespace: RootRegionLineageNamespace,
        *,
        session_max_owned_bytes: int,
        registry: RamStateOwnerRegistry,
        epoch: int = 1,
    ) -> None:
        self.namespace = namespace
        self.session_max_owned_bytes = session_max_owned_bytes
        self.epoch = epoch
        self.epoch_fenced = False
        self.owned_bytes = 0
        self._registry = registry
        self._snapshot: RamStateSnapshot | None = None
        self._history: tuple[RootRegionAdmissionEntry, ...] = ()
        self._registration: str | None = None
        self._quarantined = False

    def _register(self, key: str, base: int) -> None:
        self._registration = key
        self.owned_bytes = base

    @property
    def snapshot(self) -> RamStateSnapshot | None:
        return self._snapshot

    @property
    def history(self) -> tuple[RootRegionAdmissionEntry, ...]:
        """The HISTORICAL IMMUTABLE ENTRY CATALOG: every
        admitted admission row (root or FILE) retained by
        identity across supersessions.  Charged into
        occupancy, never destroyed by a supersession, and
        never lookup-eligible (current usability is the
        current snapshot rows alone)."""
        return self._history

    @property
    def quarantined(self) -> bool:
        """The ADVERSE-CURRENTNESS QUARANTINE (019-c): True
        once a genuine NEW state that would INVALIDATE the
        retained current usable rows (a non-READY result, or a
        READY result withdrawing / rekeying a retained current
        key) was capacity-refused on this owner.  The
        quarantine is a bounded pre-accounted unusable state
        (this single flag; the refused result is NOT
        retained, so no new bytes are charged): the owner can
        no longer certify currentness from the older retained
        READY state.  While set, every later admission
        refuses with the fixed typed fence and every
        lookup / work resolve refuses with the fixed typed
        currentness refusal; only the explicit teardown frees
        the owner (no epoch reset, no retry, no revival)."""
        return self._quarantined

    @property
    def revision(self) -> int:
        snapshot = self._snapshot
        return snapshot.revision if snapshot is not None else 0

    @property
    def process_owned_bytes(self) -> int:
        return self._registry.process_owned_bytes

    def _fence_trusted_namespace(self, namespace: object) -> None:
        # The complete trusted namespace/configuration binds
        # by IDENTITY: a value-equal foreign copy (even with
        # the same lineage key) is not the trusted namespace
        # record of this owner and cannot operate on it.
        if namespace is not self.namespace:
            raise RamStateInputError(
                "the ram state namespace does not match the owner trusted namespace record"
            )

    def _fence_result_law(
        self,
        state: RootRegionLineageState,
        result: RootRegionAdmissionResult,
    ) -> None:
        """The closed T result header law re-joined at this
        carrying boundary BEFORE the complete model law and
        any charge: exact classes, the exact input-identity
        joins (state / trusted namespace), the carried value
        joins (lineage identity, state revision, scope key)
        and the READY <-> admission-parent invariants.
        Malformed or bypass-copied records -- including a
        PARTIAL bypass copy missing a closed header field --
        raise the fixed typed input error, never a leaked
        AttributeError."""
        try:
            self._fence_result_law_closed(state, result)
        except AttributeError:
            raise RamStateInputError(
                "the ram state result or state record is missing a closed header field"
            ) from None

    def _fence_result_law_closed(
        self,
        state: RootRegionLineageState,
        result: RootRegionAdmissionResult,
    ) -> None:
        ns_key = self.namespace.lineage_key
        if type(state.lineage_key) is not str or state.lineage_key != ns_key:
            raise RamStateInputError(
                "the ram state state does not match the owner trusted lineage identity"
            )
        if result.state is not state or result.ns is not self.namespace:
            raise RamStateInputError(
                "the ram state result is not joined to the owner trusted state and namespace"
            )
        if result.lineage_key != ns_key or result.revision != state.revision:
            raise RamStateInputError(
                "the ram state carried identity or revision does not match the retained state"
            )
        if type(result.scope_key) is not str or len(result.scope_key) != 64:
            raise RamStateInputError("the ram state result must carry the closed scope key")
        if result.outcome is RootRegionAdmissionOutcome.READY:
            admission = result.admission
            if (
                admission is None
                or admission.state is not state
                or admission.ns is not self.namespace
                or admission.r_result is not result.r_result
                or admission.g_bounds is not result.g_bounds
            ):
                raise RamStateInputError(
                    "the ram state READY result must carry the"
                    " actual admission parent joined to the"
                    " trusted state and namespace"
                )
        elif result.admission is not None:
            raise RamStateInputError(
                "the ram state non-READY result must not carry an admission parent"
            )
        if result.r_result is not None and result.r_result.state is not state:
            raise RamStateInputError(
                "the ram state carried R result is not joined to the trusted state"
            )

    def _commit_charge(
        self,
        state: RootRegionLineageState,
        result: RootRegionAdmissionResult,
        history: tuple[RootRegionAdmissionEntry, ...],
    ) -> tuple[int, RamStateSnapshot]:
        """The conservative occupancy of the committed record
        set under the documented closed recipe: the owner base
        metadata (the measured shell, the retained trusted
        namespace), the retained
        records, the HISTORICAL catalog (its tuple AND its
        retained entry objects) and the NEW snapshot storage
        (its model instance, its field container and its
        scalar fields; the record references are identity-
        deduplicated) -- computed BEFORE the ceiling
        decision."""
        seen: set[int] = set()
        total = _measured_owner_shell()
        total += _charge_object(self.namespace, seen)
        total += _charge_object(state, seen)
        total += _charge_object(result, seen)
        total += _charge_object(history, seen)
        zero_charged_before = id(0) in seen
        snapshot = RamStateSnapshot(
            namespace=self.namespace,
            state=state,
            result=result,
            revision=self.revision + 1,
            epoch=self.epoch,
            owned_bytes=0,
        ).model_copy()
        total += _charge_object(snapshot, seen)
        # The committed snapshot must ALWAYS carry the FINAL
        # charge in its owned_bytes field, with the
        # accounting consistent with the representation
        # actually retained: the walk above charges this
        # retained copy-shaped snapshot (the fresh
        # constructor form is transient only), and
        # publishing that value changes exactly the charge
        # of that one int field (its actual size minus the
        # actual size of the zero it replaces, under the
        # current identity dedup).  Solve the fixed point --
        # the hard ceiling keeps the value to at most two
        # int limbs, so the loop closes in bounded steps.
        value = total
        while True:
            delta = (sys.getsizeof(value) if id(value) not in seen else 0) - (
                sys.getsizeof(0) if not zero_charged_before else 0
            )
            final = total + delta
            if final == value:
                break
            value = final
        snapshot = snapshot.model_copy(update={"owned_bytes": value})
        return value, snapshot

    def _quarantine_if_adverse(self, result: RootRegionAdmissionResult) -> None:
        """Set the adverse-currentness quarantine (019-c) when
        the capacity-refused genuine NEW state would INVALIDATE
        the retained current usable rows.  A non-READY result
        carries no current rows at all (an unresolved maximal
        root uncertainty or another refused currentness); a
        READY result is adverse when it WITHDRAWS or REKEYS any
        retained current key (a changed governing root rekeys
        the root and FILE rows; an overlapping changed file
        withdraws its entry).  A READY candidate preserving
        EVERY retained current key is the non-adverse
        additive control: the refusal then preserves the old
        usable state exactly.  The quarantine itself is
        bounded and pre-accounted (this single flag; the
        refused result is NOT retained, so no new bytes are
        charged)."""
        snapshot = self._snapshot
        if snapshot is None:
            return
        old_result = snapshot.result
        if old_result.outcome is not RootRegionAdmissionOutcome.READY:
            return
        old_admission = old_result.admission
        if old_admission is None:
            return
        old_keys = {
            old_admission.root_entry.content_key,
            *(e.content_key for e in old_admission.entries),
        }
        candidate_keys: set[str] = set()
        if result.outcome is RootRegionAdmissionOutcome.READY:
            candidate_admission = result.admission
            if candidate_admission is not None:
                candidate_keys = {
                    candidate_admission.root_entry.content_key,
                    *(e.content_key for e in candidate_admission.entries),
                }
        if old_keys - candidate_keys:
            self._quarantined = True

    def admit(
        self,
        state: object,
        result: object,
        namespace: object,
        *,
        expected_revision: int,
    ) -> RamStateAdmissionResult:
        """Admit ONE retained (state, result) record set for
        the trusted namespace of this owner.  The expected
        owner revision is a MANDATORY commit input (the
        commit-CAS binding is unavoidable: an update computed
        from a retained snapshot must bind the snapshot
        revision, and the empty owner binds zero).  The
        ENTIRE fence / complete-law / charge / ceiling /
        commit sequence runs inside the short process-
        registry critical section (pure memory only -- no
        model IO or SSE), with every precondition re-checked
        after acquiring; the CAS, the lineage-rollback fence
        and the ceilings can therefore never commit a stale
        or interleaved decision.  The session ceiling runs on
        the SAME atomic sum the 019-b work plane honors: the
        owner's store occupancy plus this owner's charged
        work occupancy (zero on a work-disabled registry), so
        neither plane can bypass the other's ceiling."""
        with self._registry._lock:
            work = self._registry._work
            work_extra = work.session_bytes(self.namespace.lineage_key) if work is not None else 0
            session_sum = self.owned_bytes + work_extra
            if self._registration is None and not self.epoch_fenced:
                raise RamStateInputError(
                    "the ram state owner is not registered with a live process registry"
                )
            if self.epoch_fenced:
                return RamStateAdmissionResult(
                    outcome=RamStateOutcome.REFUSED,
                    limitation=RamStateLimitation.EPOCH_FENCED,
                    snapshot=self._snapshot,
                    charged_bytes=0,
                    session_owned_bytes=session_sum,
                    process_owned_bytes=self.process_owned_bytes,
                    revision=self.revision,
                    http_status=None,
                )
            if type(state) is not RootRegionLineageState:
                raise RamStateInputError(
                    "the ram state state must be the original 018-p state record class"
                )
            if type(result) is not RootRegionAdmissionResult:
                raise RamStateInputError(
                    "the ram state result must be the original 018-t result record class"
                )
            if type(expected_revision) is not int or expected_revision < 0:
                raise RamStateInputError("the expected revision must be a non-negative integer")
            self._fence_trusted_namespace(namespace)
            if self._quarantined:
                return RamStateAdmissionResult(
                    outcome=RamStateOutcome.REFUSED,
                    limitation=RamStateLimitation.OWNER_QUARANTINED,
                    snapshot=self._snapshot,
                    charged_bytes=0,
                    session_owned_bytes=session_sum,
                    process_owned_bytes=self.process_owned_bytes,
                    revision=self.revision,
                    http_status=None,
                )
            self._fence_result_law(state, result)
            # The ACTUAL complete 018-t result law re-run at
            # this carrying boundary (the closed-field law):
            # the full model revalidation -- the closed-field
            # fences, the outcome invariants, the identity
            # joins, the carried bound-set gates, the nested R
            # carried law and the phase-5 ACTUAL S admission-
            # parent revalidation (the canonical rekey, the
            # reverse-index law and the counter law) --
            # refuses a bypass-copied or forged record,
            # including a forged canonical leaf, a forged
            # retained group or a broken reverse/count
            # relation, with the fixed sanitized boundary
            # error BEFORE any charge, traversal or commit.
            try:
                RootRegionAdmissionResult.model_validate(result)
            except Exception:
                raise RamStateInputError(
                    "the ram state result does not satisfy the complete 018-t result law"
                ) from None
            if self.revision != expected_revision:
                return RamStateAdmissionResult(
                    outcome=RamStateOutcome.REFUSED,
                    limitation=RamStateLimitation.REVISION_MISMATCH,
                    snapshot=self._snapshot,
                    charged_bytes=0,
                    session_owned_bytes=session_sum,
                    process_owned_bytes=self.process_owned_bytes,
                    revision=self.revision,
                    http_status=None,
                )
            # The LINEAGE fence: the state revision is a CAS
            # fence, never an arrival clock.  An older genuine
            # P state than the retained one is a rollback, and
            # a DISTINCT state object at the SAME retained P
            # revision is a divergent lineage fork; both are
            # refused without any commit (an identical
            # retained state replay is separate).
            snapshot = self._snapshot
            if snapshot is not None:
                if state.revision < snapshot.state.revision:
                    return RamStateAdmissionResult(
                        outcome=RamStateOutcome.REFUSED,
                        limitation=RamStateLimitation.STALE_STATE_REVISION,
                        snapshot=snapshot,
                        charged_bytes=0,
                        session_owned_bytes=session_sum,
                        process_owned_bytes=self.process_owned_bytes,
                        revision=self.revision,
                        http_status=None,
                    )
                if state is not snapshot.state and state.revision == snapshot.state.revision:
                    return RamStateAdmissionResult(
                        outcome=RamStateOutcome.REFUSED,
                        limitation=RamStateLimitation.STALE_STATE_REVISION,
                        snapshot=snapshot,
                        charged_bytes=0,
                        session_owned_bytes=session_sum,
                        process_owned_bytes=self.process_owned_bytes,
                        revision=self.revision,
                        http_status=None,
                    )
            # The HISTORICAL IMMUTABLE ENTRY CATALOG grows by
            # the current snapshot admitted rows (identity-
            # deduplicated; supersession never destroys a
            # retained entry object).
            history = self._history
            if result.outcome is RootRegionAdmissionOutcome.READY:
                admission = result.admission
                if admission is not None:
                    for entry in (admission.root_entry, *admission.entries):
                        if not any(entry is kept for kept in history):
                            history = history + (entry,)
            # The conservative occupancy charge of the owned
            # base + retained records + catalog + snapshot
            # storage is computed BEFORE any commit or ceiling
            # decision.
            charge, new_snapshot = self._commit_charge(state, result, history)
            # The session ceiling bounds the SAME atomic sum
            # the work plane charges against: this commit's
            # store charge plus the owner's current charged
            # work occupancy.
            if charge + work_extra > self.session_max_owned_bytes:
                self._quarantine_if_adverse(result)
                return RamStateAdmissionResult(
                    outcome=RamStateOutcome.REFUSED,
                    limitation=RamStateLimitation.SESSION_OWNED_BYTES_OVER_BOUND,
                    snapshot=snapshot,
                    charged_bytes=charge,
                    session_owned_bytes=session_sum,
                    process_owned_bytes=self.process_owned_bytes,
                    revision=self.revision,
                    http_status=RAM_HTTP_CAPACITY_STATUS,
                )
            # The PROCESS ceiling is the REGISTRY level: an
            # owner session override can never bypass it.
            process_after = self._registry.process_owned_bytes - self.owned_bytes + charge
            if process_after > self._registry.bounds.process_max_owned_bytes:
                self._quarantine_if_adverse(result)
                return RamStateAdmissionResult(
                    outcome=RamStateOutcome.REFUSED,
                    limitation=RamStateLimitation.PROCESS_OWNED_BYTES_OVER_BOUND,
                    snapshot=snapshot,
                    charged_bytes=charge,
                    session_owned_bytes=session_sum,
                    process_owned_bytes=self.process_owned_bytes,
                    revision=self.revision,
                    http_status=RAM_HTTP_CAPACITY_STATUS,
                )
            self._registry._commit_process_delta(charge - self.owned_bytes)
            self._snapshot = new_snapshot
            self._history = history
            self.owned_bytes = charge
            return RamStateAdmissionResult(
                outcome=RamStateOutcome.ADMITTED,
                limitation=None,
                snapshot=new_snapshot,
                charged_bytes=charge,
                session_owned_bytes=self.owned_bytes + work_extra,
                process_owned_bytes=self.process_owned_bytes,
                revision=new_snapshot.revision,
                http_status=None,
            )

    def lookup(
        self,
        content_key: object,
        namespace: object,
        *,
        expected_epoch: int | None = None,
    ) -> RamStateLookupResult:
        """Pure memory read of ONE retained CURRENT admission
        row by its stable semantic ``content_key`` (root or
        FILE row, first closed row match; the historical
        catalog is charged but never lookup-eligible).  Never
        mutates state, never reads a disk-backed store and
        never re-creates a torn-down owner."""
        with self._registry._lock:
            if self._registration is None and not self.epoch_fenced:
                raise RamStateInputError(
                    "the ram state owner is not registered with a live process registry"
                )
            if namespace is not self.namespace:
                return RamStateLookupResult(
                    outcome=RamStateOutcome.NOT_FOUND,
                    limitation=RamStateLimitation.OWNER_NAMESPACE_MISMATCH,
                    entry=None,
                    revision=self.revision,
                    epoch=self.epoch,
                )
            if self.epoch_fenced:
                return RamStateLookupResult(
                    outcome=RamStateOutcome.NOT_FOUND,
                    limitation=RamStateLimitation.EPOCH_FENCED,
                    entry=None,
                    revision=self.revision,
                    epoch=self.epoch,
                )
            if expected_epoch is not None:
                if type(expected_epoch) is not int or expected_epoch < 1:
                    raise RamStateInputError("the expected epoch must be a positive integer")
                if expected_epoch != self.epoch:
                    return RamStateLookupResult(
                        outcome=RamStateOutcome.NOT_FOUND,
                        limitation=RamStateLimitation.EPOCH_FENCED,
                        entry=None,
                        revision=self.revision,
                        epoch=self.epoch,
                    )
            if self._quarantined:
                return RamStateLookupResult(
                    outcome=RamStateOutcome.NOT_FOUND,
                    limitation=RamStateLimitation.OWNER_QUARANTINED,
                    entry=None,
                    revision=self.revision,
                    epoch=self.epoch,
                )
            snapshot = self._snapshot
            if snapshot is None:
                return RamStateLookupResult(
                    outcome=RamStateOutcome.NOT_FOUND,
                    limitation=None,
                    entry=None,
                    revision=0,
                    epoch=self.epoch,
                )
            result = snapshot.result
            if result.outcome is not RootRegionAdmissionOutcome.READY:
                return RamStateLookupResult(
                    outcome=RamStateOutcome.NOT_FOUND,
                    limitation=None,
                    entry=None,
                    revision=snapshot.revision,
                    epoch=snapshot.epoch,
                )
            admission = result.admission
            if admission is None:
                return RamStateLookupResult(
                    outcome=RamStateOutcome.NOT_FOUND,
                    limitation=None,
                    entry=None,
                    revision=snapshot.revision,
                    epoch=snapshot.epoch,
                )
            if type(content_key) is not str:
                raise RamStateInputError(
                    "the ram state lookup key must be the stable semantic content key text"
                )
            for entry in (admission.root_entry, *admission.entries):
                if entry.content_key == content_key:
                    return RamStateLookupResult(
                        outcome=RamStateOutcome.FOUND,
                        limitation=None,
                        entry=entry,
                        revision=snapshot.revision,
                        epoch=snapshot.epoch,
                    )
            return RamStateLookupResult(
                outcome=RamStateOutcome.NOT_FOUND,
                limitation=None,
                entry=None,
                revision=snapshot.revision,
                epoch=snapshot.epoch,
            )

    def _release_locked(self) -> int:
        """Release the owner's store occupancy and registry
        reference and fence the old epoch (the caller holds
        the registry lock and has passed every fence).  The
        async 019-b work teardown reuses this exact internal
        release so that the store owner and the work plane
        die in ONE critical section -- no same-epoch reset
        window can open between them."""
        freed = self.owned_bytes
        key = self._registration
        self._registry._commit_process_delta(-freed)
        self._registry._release(key)
        self._snapshot = None
        self._history = ()
        self.owned_bytes = 0
        self._registration = None
        self.epoch_fenced = True
        return freed

    def teardown(
        self,
        namespace: object,
        *,
        expected_epoch: int | None = None,
    ) -> RamStateTeardownResult:
        """Release exactly the owned state of this namespace,
        the historical catalog, the owner base metadata and
        the registry reference, fence the old epoch and
        preserve the other owners.  A later operation on the
        fenced owner returns the typed ``EPOCH_FENCED``
        refusal; the registry allocates a DISTINCT epoch to
        an explicit re-acquire; no hidden expiry and no auto-
        recreation through a normal lookup.  The 019-b
        work-plane fence (``work_in_flight``): while the
        owner's work plane is fenced (the async work teardown
        is draining) or still owns queued / active work, this
        synchronous teardown refuses; an IDLE work plane
        (no live work, not fenced) is released in the SAME
        critical section as the store release, so the store
        owner and its work plane are never torn down
        separately."""
        with self._registry._lock:
            if self._registration is None and not self.epoch_fenced:
                raise RamStateInputError(
                    "the ram state owner is not registered with a live process registry"
                )
            if namespace is not self.namespace:
                return RamStateTeardownResult(
                    outcome=RamStateOutcome.REFUSED,
                    limitation=RamStateLimitation.OWNER_NAMESPACE_MISMATCH,
                    freed_bytes=0,
                    session_owned_bytes=self.owned_bytes,
                    process_owned_bytes=self.process_owned_bytes,
                )
            if self.epoch_fenced:
                return RamStateTeardownResult(
                    outcome=RamStateOutcome.REFUSED,
                    limitation=RamStateLimitation.EPOCH_FENCED,
                    freed_bytes=0,
                    session_owned_bytes=self.owned_bytes,
                    process_owned_bytes=self.process_owned_bytes,
                )
            if expected_epoch is not None:
                if type(expected_epoch) is not int or expected_epoch < 1:
                    raise RamStateInputError("the expected epoch must be a positive integer")
                if expected_epoch != self.epoch:
                    return RamStateTeardownResult(
                        outcome=RamStateOutcome.REFUSED,
                        limitation=RamStateLimitation.EPOCH_FENCED,
                        freed_bytes=0,
                        session_owned_bytes=self.owned_bytes,
                        process_owned_bytes=self.process_owned_bytes,
                    )
            # The 019-b work-plane fence: a fenced (draining)
            # or still-live work plane refuses the
            # synchronous teardown; only the async work
            # teardown releases the store while it fences.
            work = self._registry._work
            if work is not None and work.owner_work_active(self.namespace.lineage_key):
                return RamStateTeardownResult(
                    outcome=RamStateOutcome.REFUSED,
                    limitation=RamStateLimitation.WORK_IN_FLIGHT,
                    freed_bytes=0,
                    session_owned_bytes=self.owned_bytes,
                    process_owned_bytes=self.process_owned_bytes,
                )
            freed = self._release_locked()
            # An IDLE work plane (no live work, not fenced) is
            # released in the SAME critical section as the
            # store release: its charged occupancy is
            # committed out and its state dropped atomically
            # with the owner release.
            if work is not None:
                work_freed = work.release_idle_owner(self.namespace.lineage_key)
                freed += work_freed
            return RamStateTeardownResult(
                outcome=RamStateOutcome.TEARDOWN,
                limitation=None,
                freed_bytes=freed,
                session_owned_bytes=0,
                process_owned_bytes=self.process_owned_bytes,
            )


class RamStateOwnerRegistry:
    """The explicit process-level owner registry (019-a).

    An explicit process object (the actual application
    startup wiring of a shared registry is 022, not yet
    earned here): it tracks the live owners by trusted
    namespace identity (the actual 018-p ``lineage_key``) and
    ENFORCES the process-wide owned-occupancy ceiling (an
    owner session override can never bypass it).  The
    COMPLETE 018-p namespace law is re-run on every
    acquire / new_owner / get (a bypass-copied or tampered
    namespace record refuses with the fixed typed error),
    and a live registration is joined by EXACT trusted-
    record identity: a value-equal foreign copy carrying the
    registered lineage key is refused at the registry, never
    handed the registered owner.  ``acquire`` is the
    idempotent join for one live owner per namespace (a torn-
    down fenced owner is replaced ONLY by an explicit re-
    acquire with a DISTINCT allocated epoch, never by a
    normal lookup); ``new_owner`` is the strict construction
    path that rejects the unsupported multi-worker /
    duplicate live-owner configuration with the fixed typed
    error.  The shared registry shell is charged into the
    process occupancy once at construction; the ACTUAL table
    growth of the shared live-owner map is charged as it
    happens and retained at high water as an explicitly
    conservative reservation (removing owners never shrinks
    the table; a smaller candidate replacement may shrink
    the ACTUAL table while the charge stays; that charge is
    retained container allocation, never part of any
    session's freed bytes); every owner
    base metadata is charged into the process occupancy at
    creation (refused atomically BEFORE registration when
    EITHER ceiling cannot cover it) and released at teardown;
    the retired registry reference is released (no
    accumulation of torn-down owners).  Body/header strings
    cannot mint ownership: only the actual trusted namespace
    record is accepted.  All construction and mutation runs
    inside the short process-registry critical section (pure
    memory only -- no model IO or SSE)."""

    __slots__ = (
        "_bounds",
        "_lock",
        "_owners",
        "_owners_table_charged",
        "_process_owned_bytes",
        "_epoch_counter",
        "_work",
    )

    def __init__(
        self,
        bounds: RamStateBounds | None = None,
        work_bounds: object = None,
    ) -> None:
        if bounds is None:
            self._bounds = RamStateBounds()
        elif not ram_state_bounds_shape_ok(bounds):
            raise RamStateInputError(
                "the registry bounds must be the closed original bounds record"
            )
        else:
            self._bounds = bounds
        self._lock = threading.Lock()
        self._owners: dict[str, RamStateOwner] = {}
        # The ACTUAL table size of the shared live-owner map
        # as charged: the empty-table size the shell charge
        # below already commits; growth is charged as it
        # happens in _allocate and retained at high water as
        # an explicitly conservative reservation (removals
        # never shrink the table; a smaller candidate
        # replacement may shrink the ACTUAL table while the
        # charge stays).
        self._owners_table_charged = sys.getsizeof(self._owners)
        self._epoch_counter = 0
        self._process_owned_bytes = 0
        # The shared registry shell (the instance, its live-
        # owner map, its critical-section lock, its epoch
        # counter, its occupancy counter and its closed
        # bounds record) is owned retained process metadata:
        # it is charged into the process occupancy once at
        # construction under the ACTUAL measured sizes.
        bounds_shell = _charge_object(self._bounds, set())
        self._process_owned_bytes = (
            sys.getsizeof(self)
            + sys.getsizeof(self._owners)
            + sys.getsizeof(self._lock)
            + sys.getsizeof(self._epoch_counter)
            + sys.getsizeof(self._process_owned_bytes)
            + bounds_shell
        )
        # The 019-b async work plane is OPT-IN: an explicit
        # ``work_bounds`` enables the bounded single-flight
        # coordinator over this registry's owners (the
        # closed original work-bounds record class only).
        # The 019-a default (no work plane) is unchanged.
        # The imports are lazy because the coordinator module
        # imports this store module at top level.  The
        # coordinator shell (including the retained
        # work-bounds record) is committed on top of the
        # registry shell charge ABOVE, so the combined base
        # is accounted before ANY owner allocation can be
        # checked against the process ceiling.
        self._work: RamWorkCoordinator | None = None
        if work_bounds is not None:
            from .ram_work import RamWorkCoordinator
            from .ram_work_models import ram_work_bounds_shape_ok

            if not ram_work_bounds_shape_ok(work_bounds):
                raise RamStateInputError(
                    "the registry work bounds must be the closed original work bounds record"
                )
            self._work = RamWorkCoordinator(self, work_bounds)

    @property
    def bounds(self) -> RamStateBounds:
        return self._bounds

    @property
    def work(self) -> RamWorkCoordinator | None:
        """The opt-in 019-b async work plane coordinator, or
        None when the registry was created without a work
        plane (the 019-a default)."""
        return self._work

    @property
    def process_owned_bytes(self) -> int:
        return self._process_owned_bytes

    def _validate_namespace(self, namespace: object) -> TypeGuard[RootRegionLineageNamespace]:
        if type(namespace) is not RootRegionLineageNamespace:
            raise RamStateInputError(
                "the ram state namespace must be the original 018-p namespace record class"
            )
        # The closed header-field gate is SAFE against a
        # field-less bypass copy: a ``model_construct()``
        # namespace that carries NO fields at all is refused
        # with the fixed boundary error here, before any
        # direct attribute access (never an AttributeError)
        # and before the complete namespace law runs.
        lineage_key = getattr(namespace, "lineage_key", None)
        if type(lineage_key) is not str or len(lineage_key) != 64:
            raise RamStateInputError(
                "the ram state namespace must carry the closed lineage identity field"
            )
        # The COMPLETE 018-p namespace law re-run at the
        # registry boundary (the actual D scope revalidation
        # and the lineage_key recomputation): a bypass-copied
        # or tampered namespace record refuses with the fixed
        # sanitized boundary error BEFORE any owner is
        # returned or allocated.
        try:
            RootRegionLineageNamespace.model_validate(namespace)
        except Exception:
            raise RamStateInputError(
                "the ram state namespace does not satisfy the complete 018-p namespace law"
            ) from None
        return True

    def _validate_session_ceiling(self, value: int | None) -> int:
        if value is None:
            return self._bounds.session_max_owned_bytes
        if (
            type(value) is not int
            or isinstance(value, bool)
            or not 1 <= value <= RAM_OWNED_BYTES_HARD_CEILING
        ):
            raise RamStateInputError("the owner session ceiling must be a positive integer")
        if value > self._bounds.process_max_owned_bytes:
            raise RamStateInputError(
                "the owner session ceiling cannot exceed the registry process ceiling"
            )
        return value

    def _allocate(
        self, namespace: RootRegionLineageNamespace, session_ceiling: int
    ) -> RamStateOwner:
        # The caller holds the lock.  The owner base metadata
        # (the measured shell and the retained trusted
        # namespace record) is charged BEFORE the owner
        # becomes live, and BOTH ceilings are enforced
        # atomically BEFORE any live mutation.  The shared
        # map table's growth is PRE-RESERVED by staging the
        # ACTUAL complete candidate table (the live table
        # plus this entry): CPython table growth depends on
        # the live table's actual state (including removal
        # dummies from churn), so a fresh same-count dict is
        # not a prediction; the candidate's ACTUAL measured
        # post-insertion size is the reservation.  The SAME
        # candidate object is published only after both
        # checks pass; a refused allocation discards the
        # candidate and retains the original table and
        # counters EXACTLY (nothing is retained by a
        # refusal).  The charged table size is retained at
        # high water: removals never shrink the table, and a
        # later smaller candidate replacement retains the
        # charge as an explicit conservative over-charge.
        self._epoch_counter += 1
        owner = RamStateOwner(
            namespace,
            session_max_owned_bytes=session_ceiling,
            registry=self,
            epoch=self._epoch_counter,
        )
        base = ram_owner_base_charge(namespace)
        candidate = {**self._owners, namespace.lineage_key: owner}
        candidate_size = sys.getsizeof(candidate)
        table_growth = max(0, candidate_size - self._owners_table_charged)
        if self._process_owned_bytes + table_growth + base > self._bounds.process_max_owned_bytes:
            raise RamStateCapacityError(
                "the process ceiling cannot cover a new owner owned metadata"
            )
        if base > session_ceiling:
            raise RamStateCapacityError(
                "the session ceiling cannot cover a new owner owned metadata"
            )
        # Publish the SAME candidate object (its measured
        # size was pre-reserved ABOVE, before any live
        # mutation); the accounting commit below is monotone
        # and cannot fail, so the capacity decision and the
        # publication are atomic.  A refused allocation never
        # reaches here: the candidate is simply discarded and
        # the original table and counters are retained
        # EXACTLY.  The charged table size is an explicitly
        # conservative HIGH-WATER reservation, distinct from
        # the actual allocation: when a churned table is
        # replaced by a smaller fresh candidate, the ACTUAL
        # table shrinks but the charge is RETAINED (bounded
        # by the largest table this registry ever actually
        # allocated); it can never under-charge.
        self._owners = candidate
        if candidate_size > self._owners_table_charged:
            self._owners_table_charged = candidate_size
        self._process_owned_bytes += table_growth + base
        owner._register(namespace.lineage_key, base)
        return owner

    def acquire(self, namespace: object) -> RamStateOwner:
        """The idempotent live-owner join: the existing live
        owner for the identity -- only for the EXACT
        registered trusted namespace record (a value-equal
        foreign copy carrying the registered lineage key is
        refused at this boundary, never handed the registered
        owner) -- or a new owner (with the registry default
        session ceiling and a DISTINCT allocated epoch) when
        none exists or the previous one was fenced by an
        explicit teardown. The lookup and the allocation run
        inside ONE critical section, so simultaneous acquires
        of the same namespace yield exactly one owner, one
        base charge and one epoch."""
        if not self._validate_namespace(namespace):
            # Unreachable: the guard raises on every refusal.
            raise RamStateInputError("the ram state namespace failed validation")
        with self._lock:
            owner = self._owners.get(namespace.lineage_key)
            if owner is not None and not owner.epoch_fenced:
                if namespace is not owner.namespace:
                    raise RamStateInputError(
                        "the ram state namespace is not the registered trusted namespace record"
                    )
                return owner
            return self._allocate(namespace, self._bounds.session_max_owned_bytes)

    def new_owner(
        self,
        namespace: object,
        *,
        session_max_owned_bytes: int | None = None,
    ) -> RamStateOwner:
        """The strict construction path: a new owner for the
        identity (optionally with a stricter positive session
        ceiling, never above the registry process ceiling),
        refusing the unsupported multi-worker / duplicate
        LIVE-owner configuration with the fixed typed error.
        A value-equal foreign copy carrying the registered
        lineage key cannot mint a second live owner."""
        if not self._validate_namespace(namespace):
            # Unreachable: the guard raises on every refusal.
            raise RamStateInputError("the ram state namespace failed validation")
        session = self._validate_session_ceiling(session_max_owned_bytes)
        with self._lock:
            existing = self._owners.get(namespace.lineage_key)
            if existing is not None and not existing.epoch_fenced:
                raise RamStateDuplicateOwnerError(RamStateDuplicateOwnerError.MESSAGE)
            return self._allocate(namespace, session)

    def get(self, namespace: object) -> RamStateOwner | None:
        """The registered LIVE owner for this trusted
        namespace identity or None (the retired reference is
        released at teardown).  A value-equal foreign copy
        carrying the registered lineage key is refused at
        this boundary with the fixed typed error, never
        handed the registered owner."""
        if not self._validate_namespace(namespace):
            # Unreachable: the guard raises on every refusal.
            raise RamStateInputError("the ram state namespace failed validation")
        with self._lock:
            owner = self._owners.get(namespace.lineage_key)
            if owner is not None and not owner.epoch_fenced:
                if namespace is not owner.namespace:
                    raise RamStateInputError(
                        "the ram state namespace is not the registered trusted namespace record"
                    )
                return owner
            return None

    def _release(self, key: str | None) -> None:
        # The caller holds the lock.  Releases the retired
        # registry reference (no accumulation of torn-down
        # owners); the process occupancy delta is committed by
        # the owner.  The shared map table's high-water charge
        # is NOT released: removals never shrink the table,
        # and a smaller candidate replacement may shrink the
        # ACTUAL table while the charge stays -- either way it
        # is retained (charged) container metadata, not
        # released session state.
        if key is not None:
            self._owners.pop(key, None)

    def _commit_process_delta(self, delta: int) -> None:
        # The caller holds the lock.
        self._process_owned_bytes += delta
        if self._process_owned_bytes < 0:
            raise RamStateError("the process owned occupancy went negative")

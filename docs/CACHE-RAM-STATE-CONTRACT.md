# Bounded RAM owner and atomic state storage contract (objective 019, slice a)

`RAM_STATE_CONTRACT_VERSION = "cache-ram-state/v1"`.
`RAM_STATE_POLICY_VERSION = "ram-state-policy/v1"`.

This contract binds the INERT bounded RAM owner and atomic state
storage foundation (`src/slaif_local_coding/constitution/bundles/`:
`ram_state` and `ram_state_models`). It is the first slice of
numeric 019 (whole-019: RAM ownership, no normal-path filesystem
content reads, same-key single-flight and cancellation, explicit
process/session occupancy ceilings and 503 backpressure without
TTL/LRU/capacity eviction): per-session immutable RAM ownership
over ACTUAL accepted 018-p state/namespace and 018-t
`RootRegionAdmissionResult` records, with a conservative measured
occupancy accounting recipe, mandatory expected-revision commit
CAS, atomic process/session ceiling checks with the fixed typed
503 backpressure contract, the retained historical entry catalog
and explicit teardown. It is implemented as inert typed modules
(`tests/test_bundle_ram_state.py`) and is ACCEPTED at its
bounded inert RAM owner/store scope WITH PROCESS QUALIFICATIONS
AND IMMUTABLE-REPORT CORRECTIONS (strategic decision
`S/reviews/019-a-decision.md`). Whole objective
018 is ACCEPTED at its complete INERT graph/currentness/admission
scope WITH PROCESS QUALIFICATIONS AND EXPLICIT IMMUTABLE-REPORT
CORRECTIONS (strategic decision `S/reviews/018-t-decision.md`;
merged to main at c5eb299). This slice closes nothing end to end:
no async single-flight, cancellation or pressure closure (later
same-019 work), no recovery (020), no compiler/tokenizer (021),
no wire/HTTP integration (022), no full-stack or actual-model
qualification (023-024); the store is never active in the adapter
request execution path, and no v1 runtime criterion is qualified
by it.

## 1. Public surface and inputs

`RamStateOwnerRegistry(bounds=None, work_bounds=None)` owns at
most one live
`RamStateOwner` per trusted namespace:

- `acquire(namespace) -> RamStateOwner` creates the owner (base
  charge included) under the registry critical section;
- `new_owner(namespace, session_max_owned_bytes=None)` creates the owner with an optional positive per-owner session ceiling (any positive non-bool int not above the registry process ceiling; the registry session ceiling when omitted; the registry process ceiling never weakens);
- `get(namespace) -> RamStateOwner | None` returns the live owner
  or None (after teardown).

`RamStateOwner`:

- `admit(state, result, ns, *, expected_revision) ->
  RamStateAdmissionResult` commits ONE genuine
  `RootRegionLineageState` + `RootRegionAdmissionResult` pair
  under the mandatory expected-revision CAS;
- `lookup(content_key, ns, *, expected_epoch=None) -> RamStateLookupResult` reads the CURRENT rows only (the retained catalog rows are charged but never lookup-eligible);
- `teardown(ns, *, expected_epoch=None) -> RamStateTeardownResult` frees exactly that namespace's owned state and occupancy and fences the old epoch.

The inputs are the ACTUAL 018-p state and the ACTUAL 018-t
complete-consumer result for that state. Object construction is
not authentication: the complete actual
`RootRegionAdmissionResult.model_validate` law is re-run before
commit, the complete trusted namespace is model-validated at every REGISTRY access (acquire/new_owner/get) while the owner operations (admit/lookup/teardown) bind the registered trusted namespace record by identity, and a value-equal foreign copy carrying the registered lineage key is refused: the fixed `RamStateInputError` at registry access and on `admit`, the typed `owner_namespace_mismatch` refusal on `lookup`/`teardown`. Public
body/header strings cannot mint ownership. A refused admission
leaves the retained entries, revision, graph, indices, catalog
and occupancy exactly unchanged; the ONLY possible refusal side
effect is the bounded pre-accounted `owner_quarantined` flag
(section 3), set by a capacity-refused candidate classified
adverse, after which the old usable lookups refuse even though
every retained byte and counter is intact.

## 2. Namespace, owner and epoch law

Every lookup/commit/lifecycle operation is bound to the COMPLETE
trusted `RootRegionLineageNamespace` (principal, session,
repository, route/model and configuration identity), to ONE live
owner and to an explicit cache epoch. New owners get DISTINCT
fenced epochs allocated by the registry (an old epoch is never
reused); a fenced (torn-down) owner refuses all operations with
the fixed `epoch_fenced` limitation. Duplicate live owner
configurations (multi-worker) are rejected at the component
boundary with the fixed typed `RamStateDuplicateOwnerError`;
actual application startup wiring is 022 and not earned here.

## 3. Commit fences

`expected_revision` is MANDATORY on `admit`. The commit fences, in
closed fixed vocabulary (`RamStateLimitation`):

- `revision_mismatch`: the expected-revision CAS fence;
- `stale_state_revision`: the LINEAGE-rollback fence — an OLDER
  genuine P state than the retained one, or a DISTINCT state
  object at the SAME retained P revision (a divergent lineage
  fork); the P state revision is a CAS fence, never an arrival
  clock, and an identical retained state replay is separate;
- `owner_namespace_mismatch`: the trusted-namespace fence on `lookup`/`teardown` (a fixed `RamStateInputError` is raised instead on `admit` and at registry access);
- `epoch_fenced`: the explicit-epoch fence;
- `owner_quarantined`: the ADVERSE-CURRENTNESS QUARANTINE
  (019-c). It is set when a VALIDATED capacity-refused
  candidate would INVALIDATE the retained current usable rows:
  the predicate classifies the candidate as non-READY (carrying
  no current rows) or as a READY result withdrawing / rekeying
  any retained current key (the retained READY snapshot keys
  minus the candidate's READY keys nonempty); it does not
  independently prove source novelty -- it is the compatibility
  check between the retained current keys and the validated
  candidate. A READY candidate preserving EVERY retained
  current key is the non-adverse additive control (the refusal
  then preserves the old usable state exactly). It is a bounded pre-accounted
  unusable state (this single owner-shell scalar; the
  capacity-refused result is NOT retained, so no new bytes are
  charged): while set, every later `admit` refuses with the
  fixed typed fence (checked after the trusted-namespace fence,
  before any result law / CAS / charge), every `lookup` returns
  the fixed typed currentness refusal, and the 019-b work plane
  carries it through as the fixed typed 409 currentness refusal
  with zero invocation; only the explicit `teardown` frees the
  owner (no epoch reset, no retry, no revival of the old usable
  state).

Committed records retain the exact input state/namespace by reference, the ACTUAL 018-t result by immutable reference and the admitted entries; the retained catalog keeps every admitted entry row -- current and superseded -- by identity (supersession retains the prior rows rather than moving them; only CURRENT rows are lookup-eligible, section 7).

## 4. Occupancy accounting recipe

A conservative MEASURED recipe (`ram_retained_owned_bytes`,
`ram_owner_base_charge`, `_charge_object`) charges every retained
owned component before commit: the actual shallow owned objects
and containers (`sys.getsizeof`), with referents deduplicated by
ACTUAL identity within one owner (shared immutable records are
charged once per owner; cross-session sharing never exempts a
session from its own charge), covering the retained
namespace/state/result references, the entry metadata and key
records, the retained P/D history and sources (even when
unreachable, historical or not admitted), the carried
R/Q/F/E graphs, admission records and indexes, the historical
entry catalog and its tuple, the final snapshot storage and the
registry-owned metadata. The shared registry shell is charged
once at construction; the ACTUAL table growth of the shared
live-owner map is charged as it happens and RETAINED AT ITS HIGH
WATER as an explicitly conservative reservation (CPython tables
do not shrink when owners are removed, and a later smaller
candidate replacement may shrink the ACTUAL table while the
charge stays, bounded by the largest table this registry ever
actually allocated; the charge is retained container metadata,
never part of any session's freed bytes). A new owner's
allocation stages the ACTUAL complete candidate table and
pre-reserves its measured size BEFORE both ceilings are checked
atomically, so a refused allocation discards the candidate and
retains the original table and counters EXACTLY. The 019-c
quarantine flag (section 3) is an owned owner-shell scalar
charged within the owner shell; the capacity-refused result
that triggers it is NOT retained, so the quarantine adds no
retained bytes. `entry_source_bytes` is a copy-budget
counter and does not stand in for occupancy. The recipe is a
committed-occupancy measure, NOT a total-RSS promise, and
temporary bounded transformation work is distinct from committed
occupancy. No TTL, LRU, capacity-driven eviction, automatic
dormant scan or disk-backed normal lookup exists in this slice.

## 5. Capacity contract

Explicit configurable ceilings: positive NON-BOOL integers,
session ceiling no greater than process ceiling, defaults
`RAM_SESSION_MAX_OWNED_BYTES_DEFAULT = 134217728` (128 MiB) and
`RAM_PROCESS_MAX_OWNED_BYTES_DEFAULT = 536870912` (512 MiB), hard
ceiling `RAM_OWNED_BYTES_HARD_CEILING = 1099511627776`. The
session ceiling is the OWNER's; the process ceiling is the
REGISTRY's and is enforced for every commit (an owner-level
strict session override never weakens the process ceiling). Both
checks are atomic before commit; a crossing returns the fixed
typed 503 backpressure contract (`RAM_HTTP_CAPACITY_STATUS = 503`,
carried as `http_status` on the capacity refusal) with the
existing state fully preserved in bytes, revision, catalog and
counters; the only capacity-refusal side effect is the bounded
pre-accounted `owner_quarantined` flag (section 3) when the
validated candidate is classified adverse, which fences current
usability without changing any retained state.

## 6. Teardown and lifecycle

`teardown` releases exactly that namespace's owned state and
occupancy, fences the old epoch and releases the registry
reference; other owners are preserved. The shared map
table's high-water charge is registry retained container
metadata, NOT released session state: teardown's freed bytes
cover this namespace's own charge only, never the retained
table reservation. A torn-down owner refuses
all further operations (`epoch_fenced`); no normal lookup
re-creates or auto-recovers a torn-down owner. Configuration
changes and recovery need explicit later contracts (020).

## 7. Retention law

Admitted original bundle bytes, graph/index/current-version state
and entry metadata are retained in memory. Superseding a current entry does NOT destroy the still-valid historical immutable content object: the owner's retained catalog keeps every admitted entry row (current and superseded) by identity, a genuinely new compatible revert may reuse it, and replay cannot reactivate it. Original proof
identities and selected-source versus bootstrap distinctions from
018 are preserved by reference.

## 8. Inert boundary

This store is inert: no async single-flight or cancellation, no
compiler/tokenizer integration, no wire/HTTP wiring (the 503
contract is typed at this boundary; HTTP wiring is 022), no
recovery records (020) and no v1 runtime activation. All
018 public signatures, schemas, defaults, version tags, recipe
bytes and refusal laws stay intact; this slice adds no dependency,
no service, no model/GPU/Gateway/native call and no adapter
activation. 019-c (the whole-019 closure round) extended this
slice's closed fence vocabulary with the bounded
`owner_quarantined` adverse-currentness quarantine (section 3),
an owned owner-shell scalar charged within the occupancy recipe
and exited only by explicit teardown; all 018 law and the
accepted 019-a behavior otherwise stay unchanged. Later same-019 work (single-flight, cancellation,
pressure closure) and 020-024 remain mandatory. The separate
019-b bounded async single-flight work plane (contract
`docs/CACHE-RAM-WORK-CONTRACT.md`) is the later same-019 slice
built OVER this store: it is opt-in via the registry
`work_bounds` (the default work-disabled behavior is unchanged),
charges the SAME process/session ceilings against the SAME
atomic sum (the synchronous `admit` session check adds the
owner's charged work occupancy), and the synchronous store
teardown is fenced with the fixed typed `work_in_flight`
refusal while the work plane is draining or still owns live
work.

## 9. 020 recovery seam (additive, inert)

The 020 recovery component (contract
`docs/CACHE-RECOVERY-CONTRACT.md`) adds, without changing any
accepted 019 law: the COLD initial-load transient reservation on
the trusted resume address (`reserve_recovery_transient_cold`,
held before the load / decode / full validation and released
exactly once on every outcome; a duplicate cold reservation while
a live owner exists refuses before publication) and the LIVE
bounded recovery publication reservation on the registered
namespace BY IDENTITY (`reserve_recovery_transient`: the
namespace identity join FIRST — a value-equal foreign copy is the
fixed `RamStateInputError` — then the SAME-lock work-teardown
fence refusal with the fixed `RamStateWorkTeardownFenceError`
while the work owner's fenced / draining flag is set, BEFORE the
capacity checks — so a draining work teardown can never release
the store under a live recovery reservation); the
session-reserved transient term is part of the SAME atomic
process / session sums (the synchronous `admit` session-ceiling
check and the process ceiling see it, so simultaneous store /
work allocations observe the session reservation); the ONE
process-wide owned store IO slot
(`owned_store_io_acquire` / `owned_store_io_release`, closed
constant 1, the typed busy refusal) that bounds concurrent owned
recovery publications; and the fixed `recovery_in_flight`
refusal on the synchronous store teardown (and on the work
teardown) while recovery IO is live at entry — the held
transient reservation OR a claimed synchronous recovery
operation (020-b: the claim is the ONE registry-held
`_recovery_op_owner` record, admitted only while the caller holds
the ONE process owned store IO slot, so at most ONE operation is
ever claimed; `recovery_op_begin` joins the registered, unfenced
live owner in the SAME critical section as the claim — an
absent / fenced / replaced owner refuses, while an ALREADY-SET
work-teardown fence is NOT a claim refusal (the accepted 020-a
same-lock reservation fence applies to a fenced claim unchanged,
preserving the established `FENCE_REFUSED` / `WRITER_CONFLICT`
results, and a fenced claim can never publish) — and
`recovery_op_end` releases it by identity on every outcome) — so
both teardown paths compose with the 020 recovery owner without an
orphaned writer: a teardown that wins retires the owner and the
claim is a clean typed refusal (no cold reservation, no
publication), while a write that wins its claim keeps the
ownership un-releasable until the operation ends.

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
(`tests/test_bundle_ram_state.py`) and is PENDING strategic
review at its bounded inert RAM owner/store scope. Whole objective
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

`RamStateOwnerRegistry(bounds=None)` owns at most one live
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
leaves existing entries, revision, graph, indices, catalog and
occupancy exactly unchanged.

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
- `epoch_fenced`: the explicit-epoch fence.

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
registry-owned metadata. `entry_source_bytes` is a copy-budget
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
carried as `http_status` on the capacity refusal) with existing
state fully preserved.

## 6. Teardown and lifecycle

`teardown` releases exactly that namespace's owned state and
occupancy, fences the old epoch and releases the registry
reference; other owners are preserved. A torn-down owner refuses
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
activation. Later same-019 work (single-flight, cancellation,
pressure closure) and 020-024 remain mandatory.

# Bounded async single-flight work plane contract (objective 019, slice b)

`RAM_WORK_CONTRACT_VERSION = "cache-ram-work/v1"`.
`RAM_WORK_POLICY_VERSION = "ram-work-policy/v1"`.

This contract binds the INERT bounded async same-full-key
single-flight and attempt-ownership work plane
(`src/slaif_local_coding/constitution/bundles/`: `ram_work` and
`ram_work_models`). It is the second slice of numeric 019, built
over the ACCEPTED 019-a RAM owner/store foundation (strategic
decision `S/reviews/019-a-decision.md`; contract
`docs/CACHE-RAM-STATE-CONTRACT.md`) and the ACTUAL accepted
018-p/018-t records: bounded leader/queue/waiter/attempt
ownership, the ratified no-retry attempt lifecycle, the
cancellation law and the owner/source/epoch publication fences,
with an injected bounded async work seam that proves prepared-work
orchestration only (actual compiler/tokenizer semantic validation
is 021). It is implemented as inert typed modules
(`tests/test_bundle_ram_work.py`) and is PENDING strategic review
at its bounded inert single-flight scope. Whole 019
pressure/source-scale/lifecycle closure remains a following
same-PR round; 020-024 remain mandatory; this slice is never
active in the adapter request execution path and qualifies no v1
runtime criterion.

## 1. Enabling and public surface

The work plane is OPT-IN: `RamStateOwnerRegistry(bounds=None,
work_bounds=None)` creates the `RamWorkCoordinator` only when an
explicit `work_bounds` is supplied (the `registry.work` property
is `None` otherwise, and the 019-a default behavior is
unchanged). The public surface is:

- `RamWorkCoordinator.resolve(namespace, content_key, work) ->
  RamWorkRequestResult` (async) resolves ONE demand for an ACTUAL
  admitted full key with the injected bounded async seam
  (`WorkSeam = Callable[[], Awaitable[bytes]]`): a retained valid
  payload of the same epoch is a RAM-only `HIT` (zero
  invocations); a retained terminal failure of the same key /
  epoch is re-served with the SAME fixed typed limitation (zero
  invocations, no retry); otherwise the demand claims the key (or
  joins the ONE shared attempt) under the bounded queue / waiter /
  capacity fences and awaits the shared outcome.
- `RamWorkCoordinator.teardown_owner(namespace) ->
  RamWorkTeardownResult` (async) is the explicit async session
  teardown of the work plane (section 8).
- `RamWorkCoordinator.session_bytes(lineage_key) -> int` is the
  owner's charged WORK occupancy (the synchronous store `admit`
  session-ceiling check adds this to the store occupancy, so both
  planes bound the SAME atomic sum).

The full semantic content/configuration key (the actual 64-hex
admitted content key) joined to the genuine live cache epoch
defines ONE admitted work attempt; strings alone cannot mint
work. The active-leader count is the closed constant
`RAM_WORK_ACTIVE_LEADERS = 1` (ONE process-wide active leader; a
constant, not a configurable value).

## 2. Namespace, owner and epoch binding

Every request/attempt/task/publication binds to the ACTUAL
registered trusted namespace, the owner identity, the epoch and
the ACTUAL currently admitted full key. The complete trusted
namespace is model-validated at every REGISTRY access (`get` /
`acquire` / `new_owner`): a value-equal foreign copy carrying the
registered lineage key is refused with the fixed
`RamStateInputError` at registry access (and on `admit`), and a
resolve with no live owner returns the fixed typed
`owner_absent` refusal; the owner work-plane operations bind the
registered trusted namespace record by identity. Resolve
currentness is read from the ACTUAL store state: the key must be
among the owner's ACTUAL current admitted keys (pre-claim
`key_not_current`), and publication rechecks it at completion.
Malformed content keys and non-callable seams raise the fixed
`RamWorkInputError`.

## 3. Bounded configuration

`RamWorkBounds` is the explicit positive NON-BOOL bounded
configuration (raw fences before any coercion; bool / wrong-type
inputs refuse; closed against documented conservative hard
ceilings; valid stricter original-class instances stay legal):

| Bound | Default | Hard ceiling |
| --- | --- | --- |
| `max_pending_distinct_keys` (queued plus the active key) | 32 | 4096 |
| `max_waiters_per_key` | 8 | 1024 |
| `max_output_bytes` (ONE prepared payload) | 1048576 | 67108864 |
| `max_work_seconds` (ONE admitted dispatch) | 30.0 | 600.0 |

A same-key join never consumes another distinct-key reservation;
queues are bounded BEFORE retaining tasks, waiters or source
references. The closed output shape (bytes, size) is validated at
this inert work boundary; the injected result proves prepared-work
orchestration only, never actual compiler semantic correctness.

## 4. Ratified attempt policy (claim / join / terminal, no retry)

Pre-admission refusal is separated from the atomic claim: before
a claim, resource/concurrency queue admission may refuse with the
fixed typed 503 and ZERO invocation and NO attempt
(`pending_keys_over_bound`, `waiters_per_key_over_bound`); once
the bounded key reservation is accepted (including a queued
reservation) the attempt is CLAIMED, and cancellation before
dispatch still terminates that admitted attempt with ZERO actual
invocation (no silent release-and-retry loophole). After claim,
concurrent identical demand JOINS the ONE shared operation and
outcome (`JOINED` carries the shared payload with zero invocations
for the joining request). The claim decision runs in ONE short
process-registry critical section (pure memory only -- no model
IO or SSE); the await is outside the lock, and the dispatch task
is owned independently of any first waiter.

A later request ID/nonce, revision, output directory, insertion
pressure or missing valid entry never authorizes retry. There is
no public reset, timed retry, best-of replay or hidden original
fallback. Exception, timeout, invalid / truncated / over-bound
output and cancellation after claim never become valid payloads
or hits; the terminal attempt metadata remains bounded and
charged until explicit teardown and is never evicted to retry. A
genuinely distinct semantic key receives its own attempt, and the
failure of one key never poisons unrelated keys or sessions.

## 5. Terminal records, no-retry law and publication fences

`RamWorkAttempt` is the retained, charged, never-evicted terminal
record (full key, live epoch, state, outcome, limitation, ACTUAL
invocation count -- zero for a CLAIMED attempt whose dispatch was
cancelled before its first execution (a queued cancellation or an
unstarted dispatch task), one when the dispatch actually ran --
and the retained payload on success; a pre-claim refusal claims
no attempt and retains no terminal record). A later same-key / epoch
demand gets the same fixed typed failure WITHOUT another
invocation: infrastructure/resource 503
(`work_failed`, `work_timeout`, `all_waiters_departed`,
`owner_torn_down`, the shared store capacity fences), invalid /
budget 422 (`invalid_output`, `truncated_output`,
`output_over_bound`), currentness conflict 409
(`key_not_current`, `owner_absent`, `epoch_changed`) -- the fixed
mapping is closed in `RAM_WORK_HTTP_STATUS` (HTTP wiring is 022;
this declares the contract at the inert boundary).

Retained valid immutable payloads are separate from permission to
select or publish current output: a valid A1 payload SURVIVES A2
supersession and is reused on a genuinely proven compatible A1
revert WITHOUT a third invocation; for FAILED A1 -> A2 ->
genuinely new A1 revert in the SAME epoch the original failed A1
attempt STILL applies (causal change alone never resets the
identical full key's attempt; replay / equal-byte witnesses never
reset either). Supersession and late completion never make
obsolete content current.

Publication rechecks, in closed order: the fenced owner
(`owner_torn_down`), the epoch (`epoch_changed`), the current
source-key eligibility (`key_not_current`), then the payload
charge under the SAME ceilings (section 6); a late completion of
a superseded key is terminal unsuccessful (fixed 409, the ACTUAL
invocation recorded, the payload NOT published or retained).

## 6. Occupancy and the SAME ceilings

The work plane extends the ACTUAL shared process/session
occupancy: retained pending / active / terminal attempt metadata,
historical successful payloads, task / waiter-owned references
and indexes are charged conservatively BEFORE retention /
publication. The recipe (019-a ACTUAL measured
identity-deduplicated shallow sizes) is complemented by closed
fixed reservations for runtime objects that cannot be safely
measured: `RAM_WORK_TASK_RESERVATION_BYTES = 4096` per live
dispatch task reference (including its retained work-closure
reference), `RAM_WORK_WAITER_RESERVATION_BYTES = 1024` per
retained waiter future, and `RAM_WORK_TERMINAL_RESERVATION_BYTES
= 2560` per CLAIMED attempt, charged ONCE at the claimant's claim
BEFORE the claim is accepted; a closed upper bound on the
terminal record's ACTUAL measured charge -- the focused test in
`tests/test_bundle_ram_work.py` constructs the worst-case record
(64-hex content key, 2**63 epoch, every closed field set, one
invocation) and asserts its charge under the 019-a recipe is at
or below the reservation on the pinned CPython 3.12 toolchain
(measured 1909 bytes in this round's evidence) -- whose slot is
PRE-ALLOCATED at claim time, so the mandatory terminalization is
always
non-positive in delta and can never cross either ceiling at any
later resize boundary; there is NO soft-cap exception for
terminal metadata). The shared coordinator shell (instance, owner
map, queue and retained work-bounds record) is charged into the
process occupancy once at construction.

Aggregate async and store occupancy are atomic under the SAME
019-a ceilings (defaults 512 MiB process / 128 MiB session;
`RAM_OWNED_BYTES_HARD_CEILING`): neither the synchronous `admit`
nor any lifecycle operation may bypass accounting; at pressure
the fixed typed 503 preserves the old committed state, current
lookups, payloads and counters, with no TTL / LRU / eviction /
checkpoint IO or unbounded tombstones. This is a
committed-occupancy measure, NOT a total-RSS promise. Refusals
restore the original containers and charges exactly (staged
candidate containers; delete alone is never claimed as
preservation).

## 7. Cancellation law

A single waiter cancellation DETACHES that waiter only; it never
cancels another live waiter's shared work. ALL waiters gone
cancels AND AWAITS the owned work and leaves the terminal
unsuccessful attempt (`all_waiters_departed`, fixed 503). A
dispatch task cancelled after creation but BEFORE its first
execution is finalized once on the owner side (zero actual
invocation, the active slot released) so unrelated queued work
still progresses. If a teardown task is cancelled during its
drain, the fence is kept and the drain COMPLETES before the
cancellation propagates (no fence outliving the drain, no store
released under live work, no silently orphaned work).

## 8. Teardown and lifecycle

`teardown_owner` fences the owner's work plane, terminates its
queued claims (zero invocations) and cancels AND awaits its
active / shared work (every still-waiting waiter re-served the
typed terminal), then releases the store owner AND this owner's
work occupancy in ONE critical section: the work plane stays
fenced until the owner is actually torn down, so NO same-epoch
reset window can mint fresh attempts on the retained owner; a
later resolve finds no live owner (a new epoch only from an
explicit re-acquire / the 020 restart). `freed_bytes` is the
TOTAL process occupancy released by THIS teardown (store plus
work); prior normal completions are not teardown frees; every
other owner / session is preserved. A live store owner with NO
work plane is still fully torn down in the same critical section.
The 019-a SYNCHRONOUS store teardown is refused with the fixed
typed `work_in_flight` fence while the owner's work plane is
fenced (draining) or still owns queued / active work, so the two
teardown paths compose without orphaned work. Refusals carry the
exact fence domain (no live owner, already fenced, foreign
trusted namespace) with zero release.

## 9. Inert boundary

This plane is inert: the callback seam is synthetic (021 owns the
actual tool-free authenticated compiler and tokenizer
contracts); there is no recovery store (020), no adapter startup
wiring, no service mutation, no v1 activation, no live test and
no actual-model / compiler / client claim. All 018 and 019-a
public signatures, schemas, defaults, version tags, recipe bytes
and refusal laws stay intact. The 019-a work-disabled default
behavior is unchanged; the named 019-b extensions are the opt-in
registry `work_bounds` constructor parameter, the
`work_in_flight` fence on the 019-a synchronous store teardown
while the work plane is fenced / draining or still owns live
work, and the composed store-plus-work release inside the async
teardown critical section (a work-disabled async teardown still
releases the store owner in the same critical section). The work
plane adds no dependency, no configuration key and no adapter
activation. Whole 019
pressure / source-scale / lifecycle closure and 020-024 remain
mandatory.

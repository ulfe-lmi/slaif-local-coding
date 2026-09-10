# Verification contract

Labels are exact: `PASSED`, `FAILED`, `SKIPPED`, `NOT RUN`, `BLOCKED`,
`PENDING`, `MISSING`. Unknown is never pass.

## Static/unit gate

The implementation must establish and keep one locked command set covering:

```text
format check
lint
static typing
unit tests
package/build validation
secret/logging-policy checks
```

## Contract tests with fake upstream

Required behavior:

- byte/semantic preservation for untransformed JSON requests;
- status, safe error envelopes, headers, SSE event order, disconnect, timeout, and
  tool-call passthrough;
- `/v1/responses` and `/v1/chat/completions`;
- no buffering of streaming responses;
- hop-by-hop/internal-header filtering;
- body-size and malformed-JSON behavior;
- compiler requests bypass the public transformation path;
- no raw-payload logging.

Signed gateway identity v1 tests additionally cover service-auth ordering,
canonical bytes/HMAC vectors, case-insensitive duplicate and grammar handling,
timestamp edges, secret separation/rotation, invalid-signature nonce behavior,
atomic replay TTL/LRU bounds, route mismatch before transformations, concurrent
duplicate admission, explicit per-request identity propagation, cache/
rehydration isolation dimensions, header stripping, and secret/raw-content
privacy. The adapter-side vector is
`tests/fixtures/gateway/signed_identity_v1_vectors.json`; gateway emission and
cross-repository acceptance remain `NOT IMPLEMENTED` and `NOT AUTHORIZED`.

## Objective-005 repository-only acceptance harness

The permanent bounded orchestrator is
`scripts/gateway_accounting_rehearsal.py`. It uses one ordered C/D obligation
manifest and the same fail-closed predicates for fake and protected modes.
Fake and conditionally protected modes use a clean detached Gateway at exact
implementation SHA `50dcc3b85d614eb1d0c6196595bf22ef5779f846`,
the Local candidate, synthetic PostgreSQL, a strict loopback fake Qwen, and the
task-controlled Codex 0.149.0 binary with its exact verified checksum. Use a
temporary checkout and run:

```text
PYTHONPATH=<local-repo>:<local-repo>/src:<gateway>\
  <gateway-venv>/bin/python scripts/gateway_accounting_rehearsal.py\
  --gateway-root <gateway> --gateway-python <gateway-venv>/bin/python\
  --provider-target fake --codex <codex-0.149.0>
```

The run has bounded request ordinals, zero retries, independent provider
lifecycle/call observations, strict cleanup, and a machine gate requiring
`missing=[]` and every obligation `PASSED`. Protected mode is available only
after the complete fake machine gate, under the active order's unchanged
credential, service, request, and cleanup limits. It is one bounded
authenticated run against the existing protected vision service; it is not a
cutover or release claim. `PASSED` from a focused test or report prose cannot
replace the machine gate.

The fake provider exposes only bounded classifications. Its function path is
one call with an eight-event lifecycle; its tool-result path is a nine-event
assistant-message lifecycle. Each event is capped at 16 KiB, each stream at
128 KiB, and the runner accepts at most one function call per request. The
final JSON includes ordered obligation results and a projection table with
source observation keys, producer, proving test nodes, and execution status.
`missing=[]` is therefore insufficient: `passed=true` additionally requires
every selected result to be observed, independently related, and `PASSED` with
all projection predicates true.

The 005-q implementation run repaired the recursive fake stream and its
loopback regression passed. The 005-r continuation re-pins the accepted
Gateway Objective-161 implementation and re-runs the complete fake gate,
including actual Codex 0.149 same-session full-image → resumed crop history,
before any protected call. The prior 005-q rejection at C3.1 against
`9d247e7f3d8fd6a588976840c4657181b7486b81` remains historical evidence only.

The 005-r fake run passed the complete selected machine gate: 37/37 C1–C5/D
results were `PASSED`, with no missing result, first failure, or retry, and
temporary-process, listener, database, cache, Codex-home, and secret-free-log
cleanup all passed. The one authorized protected attempt reached the exact
Gateway → Local → existing vision-Qwen path, but protected provider-call and
terminal-lifecycle observations are not available without a provider-side
relay or model-service mutation. It therefore failed closed at the first
protected C1.1 boundary and does not establish protected acceptance. The
harness now stops before later protected inference when that independent
provider boundary is unobserved; no protected retry is authorized.

The 005-s round does not retry protected traffic. Its fake-only observer
qualification uses the existing Local `create_app(settings, transport=...)`
seam and a direct HTTPX transport inside the disposable candidate; it adds no
relay and does not mutate Qwen. The observer records bounded attempted,
dispatched, responded, and completed facts, separates compiler from public
inference, and independently cross-checks fake-provider loopback counters.
Bounded SSE first-byte, event, usage, terminal, closure, overflow, malformed,
cancel, and disconnect facts remain distinct. Missing or lost observer
readiness stops the next dispatch before credentials or inference. The fake
gate binds ordered obligations and projections to candidate source/harness
identity, route policy, Gateway pin/app tree, Codex version/checksum,
implementation SHA, and run provenance; only a report-only child may reuse
that tested implementation.

The 005-t continuation tightens this evidence contract. Responses SSE framing
is incremental and invariant across LF/CRLF, one-byte boundaries, and coalesced
chunks; semantic validity is delegated to the exact pinned Gateway
`ResponsesStreamEventValidator` with its request-scoped Codex route/tool
profile. Unknown event names and fields remain invalid and are projected only
to closed classes. Exact bounded attempted/dispatched/responded/completed and
compiler/inference counters are compared before display buckets, and merged
candidate lifetimes receive unique global ordinals. Any malformed, overflowed,
truncated, cancelled, or validator-failed stream latches observer readiness
false and prevents later dispatch. Evidence-file validation uses an owned
regular-file descriptor and reads only cap-plus-one bytes, with duplicate-key,
non-finite, nested-schema, source-dirty, identity, projection, and negative
result checks failing closed.

The 005-u continuation completes the stream lifecycle contract. Observation
finalization is separate from delegate ownership: normal JSON and SSE
exhaustion, explicit early close, cancellation, timeout, truncation, and
delegate exceptions close the underlying stream exactly once. Repeated response
close is idempotent, close failures cannot replace an original stream error or
cancellation, and abnormal lifecycle state is never terminal-valid. A bounded
loopback server using the real HTTPX `AsyncHTTPTransport` withholds terminal
output until the client has received the first chunk, proving first-byte
streaming, exact bytes/status/headers, connection return, and no extra dispatch.

Responses validator/profile construction is an admission prerequisite before
the delegate can be called. Missing, raising, or invalid factories record an
attempt without a dispatch, latch readiness, and prevent later inference
admission; compiler/health handling remains available without an inference
bypass. The fake-gate tested-source check is round-neutral: it accepts the
tested head or one verified single-parent immutable report-publication child
whose report names that implementation SHA, while dirty relevant source or any
production/harness/config descendant invalidates reuse.

The 005-ag replay-correlation contract takes replay authority only from the
exact injected Gateway validator's `take_replay_reference_candidates()` result
for a successfully validated streamed function/custom-tool item. Terminal
`response.completed` IDs are diagnostic-only: the observer hashes them only to
record a bounded same/different/unknown relationship and never registers them
for continuation. A canonical candidate is registered only after complete
terminal validation and normal close; missing validator capability, ambiguous
or incomplete candidates, unowned summary aliases, and stale or cross-scope
IDs fail closed before the next request. Safe evidence records candidate
availability/count, summary relationship, pending-scope availability, and
continuation/matching classes without retaining IDs, arguments, or payloads.

The 005-ah continuation treats the validated canonical candidate as replay
authority whether the terminal summary has the same identity or an allowed
diagnostic alias. Summary identity remains diagnostic and cannot create
authority when the canonical candidate is missing, empty, out of scope, or
paired with an incomplete or invalid initial stream. Generated results bind
`execution_mode` and `run_provenance` separately for fake,
synthetic-protected, and real-protected execution; a Local observation failure
does not overwrite the actual Codex client-verification status or failure
origin. Run-level evidence publishes accumulator all-lifetime totals and a
separate candidate-readiness snapshot so startup probes are not confused with
the full composed run.

At implementation `45f9d64976b0f2a44f6c3223d767c28f5405e1a`, the fresh fake
machine gate passed 37/37 selected obligations with no missing result, first
failure, or retry. The direct observer independently recorded 23 attempted,
dispatched, responded, completed, and terminal-valid operations: 6 compiler
and 12 inference operations. Six inference operations were SSE streams with
first-byte and normal-close facts; the other six were normal JSON responses.
Fake-provider counters matched exact observer counts;
cleanup and secret-free-log checks passed. This remains fake-only evidence and
does not establish protected inference, cutover, or release readiness.

## Image-policy tests

Cover nested `input_image` and `image_url` items for Responses and Chat:

- zero images unchanged;
- one image unchanged;
- multiple images retain exactly the newest for `retain_newest`;
- text/tool items and ordering otherwise preserved;
- explicit reject policy returns a documented client error;
- policy is route-specific, never global accidental behavior.

## Constitution tests

Cover:

- effective `AGENTS.md` detection from captured/synthetic Codex envelopes;
- deterministic candidate-path extraction;
- separate reference confidence and constitutional priority;
- strict compiler schema and bounded output;
- content-hash cache hit/miss/invalidation;
- missing dependency acquisition state;
- stable bounded injection on every request;
- preservation of normative `MUST`, `MUST NOT`, `NEVER`, exceptions, role and
  source-of-truth rules;
- compiler failure fallback without silent governance loss;
- tenant/session isolation and TTL/LRU limits;
- simulated compaction/new-turn rehydration.

## Live tests on the RTX 3090 host

Use only the authenticated private vLLM endpoint and development adapter port.
Do not restart or reconfigure vLLM.

Minimum live matrix:

1. authenticated `/health` and `/v1/models` upstream;
2. adapter health/readiness and model passthrough;
3. ordinary non-streaming Responses text;
4. ordinary forced and automatic function tool calls with valid JSON arguments;
5. SSE text and SSE function-call streaming;
6. multi-turn `function_call_output` continuation;
7. one-image vision request;
8. two-image history request through adapter succeeds with only newest image
   reaching upstream;
9. constitution compile on first hash and cache hit on repeat;
10. sentinel governance rule obeyed after simulated compaction/request history
    reduction;
11. no raw `<tool_call>` markup in model-visible text;
12. no secret/raw-content leakage in logs or metrics.

Live stress tests must be serialized/bounded and must not starve the active
coding/strategic Codex sessions. Existing evidence showed 50/50 repeated tool
calls and 20/20 multi-turn sequences on the text configuration; new code must
not claim equivalent vision/adapter evidence until rerun.

## End-to-end Codex test

Use a disposable test repository with a long `AGENTS.md`, a sentinel rule near
the end, and referenced constitutional files. Capture only sanitized metadata.
Verify unchanged Codex client behavior, ordinary local tools, image full-view
then crop, adapter-boundary rehydration after history reduction, cache reuse,
and continued compliance. A native Codex compaction trigger is not required and
is not claimed by the accepted Objective-004 evidence.

The real-Codex launcher and historical native workspace-write preflight are
repository-only support in `tests/helpers/e2e_support.py` and
`tests/helpers/sandbox_runtime.py`. They are not importable production modules
and must not appear in the built wheel. The governed launcher uses Codex
0.149.0's global `--dangerously-bypass-approvals-and-sandbox` before `exec`,
records normalized argv/hash plus `codex_under_test_yolo=true`, and contains no
sandbox, permission-profile, or approval CLI flags. The suite covers private
fixture/config modes, bounded subprocess output/time, stdin closure, cleanup,
sanitized lifecycle/provenance facts, sentinel/cache gates, and strict no-model
gating until exact dependency bytes are verified. It does not execute raw
bubblewrap or `unshare` probes.

The following is a historical 004-n snapshot, not current branch status. The
historical raw probe is retained only as the narrower
`raw_bwrap_unshare_all_loopback_bootstrap_failed` audit description. The OAP
parent is host-direct/unsandboxed; that evidence is distinct from the
Codex-under-test policy. The 004-n decision tree records Codex 0.149.0
`:workspace` `true` and, only after that failure, the same binary's
`:danger-full-access` control. Both returned exit status 1 before dependency
bytes crossed the boundary. B2 host-user reconciliation, dependency `cat`,
governed model calls, and cache-reuse E2E were not run. Repository-only support
parameterizes the built-in profile and config source, records normalized
argv/hash and allowlisted effective config facts, and gates all later calls on
the exact decision tree. No raw diagnostics or host configuration are retained
or changed. At that historical round, Objective 004 was recorded at 15% and
branch readiness at approximately 74%; it is not a host-wide capability
conclusion. Current Objective-004 evidence is in the [criterion ledger](docs/OBJECTIVE-004-LEDGER.md)
and [completeness record](oap/COMPLETENESS.md), and these external diagnostics
do not gate 004-s or 004-al acceptance.

The 004-o through 004-r workspace-write and native-helper results are retained
as immutable historical external limitations. They do not gate the 004-s/004-al
acceptance path. The current governed runner keeps raw streams temporary and
reports only hashes, counts, fixed classes, fingerprints, and command status;
the ordered run itself is exactly two global-yolo invocations with no
qualification, retry, alternate prompt, or sandbox control.

## CI and merge

Required GitHub checks for the current PR must all be present and successful.
Green CI is necessary, not sufficient; strategic review also inspects live-test
evidence, scope, security, architecture, and documentation.

## Objective-005-v protected acceptance

The 005-v runner requires a complete fresh fake machine gate before protected
credential access. The fake gate is bound to the exact Local source/harness,
Gateway pin, route policy, Codex version/checksum, and direct HTTPX observer;
its provider-boundary facts are independent of Gateway accounting. The clean
005-v fake qualification passed all 37 selected obligations with zero missing,
first-failure, or retry results, 12/12 terminal-valid inference observations,
exact observer/provider agreement, cleanup, and secret-free logs.

Protected mode resolves only the active vision unit MainPID, reads its unique
nonempty `VLLM_API_KEY` entry in memory, and sends one bounded direct
Gateway-to-Local-to-existing-provider attempt through the observer. The
protected attempt in this round failed with a fixed harness `KeyError` after
observer readiness was lost; it produced no structured protected acceptance
gate. Later protected matrix obligations, cutover, and release readiness are
therefore `NOT RUN`, and no protected retry is authorized. Subsequent local
failure containment was fake-tested only.

## Objective-005-w protected projection and failure retention

005-w keeps fake and protected projection tables separate. Protected selection
now includes an explicit direct `C5.4` fixture projection and a mode-specific
observation schema; missing, duplicate, unknown, and reordered mappings fail
closed before credentials, candidate readiness, or provider dispatch. Fake
server facts are not accepted as protected provider evidence.

The runner retains a bounded payload-free accumulator across preflight,
candidate, Codex, vision, identity, cleanup, and finalization. It records the
mode, candidate/Gateway pins, phase and request ordinal, first fixed failure,
bounded secondary failure classes, exact compiler/inference attempted,
dispatched, responded, and completed counts, observer failure/terminal classes,
and cleanup outcomes before teardown. Finalization is total: a later
projection, serialization, or cleanup error is secondary and cannot replace
the original failure or counts; unavailable observations remain unknown and are
not converted to zero or pass.

Admission-time enforcement covers the existing 900-second wall bound, nine
ordered single-attempt public-operation budgets with zero retries, 16 KiB event
and 128 KiB stream limits, and single-phase concurrency. The synthetic
protected-mode conformance path uses injected fake-only hooks, proves
first-failure stop and post-cleanup row serialization, and performs zero real
credential, model, or protected-service access. This is orchestration evidence,
not protected inference acceptance.

## Objective-005-x runner budget and terminal proof

The observer's run-owned `BudgetController` admits each actual compiler,
inference, or other direct HTTPX dispatch immediately before delegation. It
records exact safe phase/ordinal facts independently of the nine ordered
operation-attempt reservations. Deadline checks run before every dispatch and
between stream chunks; event, aggregate stream, dispatch-count, and active
stream concurrency bounds are enforced without resetting across candidate
lifetime changes. A latched budget or observer failure prevents later delegate
calls while cleanup remains available.

`RunAccumulator` aggregates monotonically within a named observer lifetime and
sums distinct lifetimes without double counting repeated snapshots. It retains
semantic terminal-valid counters and per-ordinal terminal classes separately
from attempted/responded/completed/closed state. Invalid-but-consumed and
truncated/cancelled records are not terminal-valid, and absent semantic records
remain `UNKNOWN`; lifecycle-count equality never upgrades a record to valid.

The actual shared runner can be exercised in tests with explicit
`ProtectedRuntimeHooks`. These hooks are synthetic-only and cover host
preflight, MainPID, credential source, loopback provider target, bounded clock,
dispatch observation, and failure injection. Missing hooks fail closed. The
synthetic run serializes all 29 protected-selected result dispositions, keeps
`protected_acceptance=false`, and performs no `/proc` credential read, protected
Qwen request, or port-18020 mutation. This is orchestration evidence, not
protected inference acceptance.

The fresh exact pinned fake rehearsal at implementation
`63920a4fa1339f013b51e64b22c233917e21f7aa` passed 37/37 selected obligations
and projections. The direct observer recorded 23/23 dispatches, including 6
compiler and 12 inference calls. All 12 inference operations were terminal-
valid transport observations: 6 SSE streams had semantic terminal validation
and 6 normal JSON responses completed normally. Fake-provider counters matched,
all 29 synthetic protected rows serialized, and cleanup passed. This is
fake-only evidence and does not establish protected acceptance.

## Objective-005-z exact pin, operation permits, and protected-branch conformance

005-z keeps logical operation attempts separate from the transport requests
they authorize. The finite plan authorizes 25 slots: 6 compiler, 14
inference, and 5 other requests. A fresh run may consume fewer slots; its
allowance is not a measured request count. Reservation never changes the current
operation. A caller must explicitly activate the exact operation, phase,
ordinal, and lifetime before each logical transition; each actual dispatch then
consumes only that matching kind slot. Missing, exhausted, wrong-kind,
wrong-phase, wrong-ordinal, stale-lifetime, and expired-run permissions fail
closed with zero delegate calls; pre-provider rejection operations have
explicit zero transport slots. The prior 900-second, 64-observation, 16 KiB
frame, 128 KiB stream, and single-active-stream limits remain unchanged.

The Codex two-turn transition is authorized only after the first inference
response is terminal-valid. Candidate readiness records bounded `/healthz` and
`/readyz` statuses separately. A post-dispatch hook failure closes the returned
upstream stream exactly once, preserves the response observation, and releases
the active dispatch slot.

The direct observer applies cumulative byte/deadline checks to network chunks
and the 16 KiB check to each completed SSE frame. Coalesced legal frames remain
valid even when their network chunk is larger than one frame; an oversized
frame or cumulative stream latches failure, closes the stream, and prevents
later dispatch.

The shared protected-mode runner accepts synthetic-only host, PID,
credential-source, clock, loopback-provider, dispatch-completion, projection,
and cleanup seams. Healthy and injected post-dispatch executions retain phase
traces, bounded counters, selected dispositions, failure classes, and cleanup
facts. Results remain explicitly `protected_acceptance=false`; no protected
credential, Qwen request, or port-18020 mutation is implied.

The fresh exact pinned fake qualification completed the full C1–C5/D machine
gate: 37/37 obligations and projections passed, with 23 actual direct
dispatches (6 compiler, 12 inference, 5 other), exact fake-provider agreement,
12/12 inference operations terminal-valid (6 SSE streams and 6 JSON responses),
candidate `/healthz` and `/readyz` both 200, and task-resource cleanup and
secret-free logs passed. The
25-slot plan is an authorization ceiling; it is not reported as 25 measured
requests. The Gateway executable was retrieved at the authorized ancestor
`50dcc3b85d614eb1d0c6196595bf22ef5779f846`, with merged-main ancestry and
app-tree identity verified.

The same run exercised the healthy synthetic protected branch through the
shared runner using only a disposable loopback provider: 6 compiler and 12
inference lifecycle counts, all 29 protected rows serialized, no primary
failure, and all protected fixture invariants unchanged. This remains
orchestration evidence with `protected_acceptance=false`; no protected
credential or Qwen request was made. Injected observer failure stopped after
one compiler dispatch with zero inference dispatches while serializing all 29
rows; combined projection/cleanup failure retained the same primary failure
and bounded secondary classes.

## Objective-005-aa protected predicate and startup-budget closure

Protected conformance is gated by the nested protected `acceptance_gate`, not
merely by serialized row count or an empty accumulator failure. A healthy
synthetic run must have every selected protected obligation and projection
`PASSED`, while `protected_acceptance=false` remains explicit. Protected
provider predicates use normalized boundary observations only for the explicit
disposable loopback synthetic branch; real protected transport counts do not
prove semantic provider behavior. Topology evidence remains separate from
provider semantic evidence.

Candidate startup uses the same direct observer as the candidate lifetime. Its
single `/readyz` upstream health request requires an explicit, one-shot,
lifetime-bound readiness permit; readiness permits accept only `/health`, count
against the shared 64-dispatch ceiling, and are retired after dispatch. Local
`/healthz` listener polling may retry, but readiness/provider health requests do
not retry outside the run controller. Dynamic observers reject missing or
different lifetime contexts before delegation.

The final 005-aa evidence is retained under
`oap/evidence/005-aa/index.json`, bound to tested source
`ee72a19d45a5eaba0329daaddd571742ca81a586` and the evidence-only descendant
`2a7420998e3734d929142f3da0efdcf2664292f9`. The fresh fake gate passed 37/37
obligations and projections with 26/26 direct dispatches (6 compiler, 12
inference, 8 other), including 3/3 consumed readiness permits. The healthy
synthetic protected gate passed 29/29 rows; observer, combined
projection/cleanup, and pre-dispatch cases failed closed with all 29 rows
serialized and bounded primary/secondary failure classes. No real protected
access was made.

## Objective-005-ab shared protected observation path

The shared protected runner now derives provider predicates from the same
direct HTTPX Gateway-to-Local-to-provider observer for both physical and
synthetic execution. The disposable fake provider is an oracle only for the
outer fake qualification; its semantic oracle is disabled for synthetic
protected execution. The direct observer records bounded request classes,
tool classes, optional item-ID presence, matching call-ID relation, approved
fixture hashes, stream-validator lifecycle facts, and endpoint/method-scoped
preflight health/model observations without retaining payloads.

The fresh run at implementation `a127290b172969d0267e11774f5c25c3563a5eac`
passed the complete outer fake machine gate: 37/37 obligations and
projections, 26/26 direct dispatches, 6 compiler, 12 inference, 8 other, and
12/12 terminal-valid inference observations. The healthy synthetic protected
case passed 29/29 rows and projections with 28/28 direct dispatches, including
2 observed `/health` and `/v1/models` preflight requests plus 3 candidate
readiness requests; the fake semantic oracle was unavailable. The standalone
fake id-less regression remains regression evidence only; the protected C1.4
predicate is derived from the admitted direct natural continuation and its
matching call-ID relationship.

The same serial run records three truthful failure cases, each with all 29
rows serialized: observer failure after one compiler and one inference
dispatch (`observer_readiness_lost`, later inference stopped); combined
observer/projection/cleanup failure (cleanup injection retained as a secondary
failure); and genuine pre-dispatch mapping/dependency failure with zero
compiler, inference, and other dispatches, zero credential-hook calls, and no
provider access. All synthetic resources cleaned up, except the deliberately
injected cleanup-failure fact in that case. The protected fixture was not
authenticated or mutated.

## Objective-005-ac fixture-independent acceptance corrections

The protected runner uses one counted, deadline- and 64-dispatch-bounded
health/models preflight and one direct-observer semantic projection whether
synthetic runtime hooks are present or absent. A failed health or observer
boundary stops later model/provider dispatch. Hook seams select only synthetic
resource boundaries, clocks, or explicit failure injection; they do not select
an alternate acceptance predicate. Real protected inference and the protected
matrix remain `NOT RUN` unless separately ordered.

At tested implementation `d49ff680df68c67354cede4c3f5a99dbdaa49d9f`, the
fresh exact-pinned fake run passed all 37/37 outer obligations and projections
with 26/26 direct dispatches (6 compiler, 12 inference, 8 other), 12/12
terminal-valid inference operations, 6 SSE and 6 JSON inference observations,
three consumed readiness permits, exact fake-provider agreement, terminal
accounting, cleanup, and secret-free logs. Its healthy synthetic protected
branch passed 29/29 rows with 28/28 dispatches, including two counted
provider-preflight probes and three readiness probes. The synthetic failure
cases retained their primary/secondary failures and cleanup facts. This is
fake-only and synthetic orchestration evidence; protected acceptance, cutover,
and release readiness remain `NOT RUN`.

Provider call/result evidence is derived from validated returned function-call
items and the admitted continuation in the same phase, session, and observer
lifetime. IDs are transient opaque digests only; ordinary text mentioning an
item type, an unpaired output, a mismatched or reordered ID, and an ID-less
item without the matching call ID do not satisfy the continuation predicate.
The observer retains bounded distinct event categories plus scalar event
counts, so repeated legal SSE deltas do not consume category storage. The
16-KiB event and 128-KiB stream limits, exact Gateway validator, lifecycle
closure rules, and synthetic failure cases remain unchanged.

## Objective-005-ad actual omission companion

The C1.4 id-less predicate is satisfied only by the composed companion inside
the existing `identity_replay` allowance: one streamed initial function call
returned by the Gateway → Local → provider chain followed by one non-streaming
continuation. The continuation supplies the mandatory `call_id` from that
returned call while omitting only its optional item `id`. Direct observer facts
for both requests must share operation, phase, ordinal, lifetime, and session;
both responses must be terminal-valid and the two corresponding accounting
reservations must be finalized with no pending or duplicate request IDs.

The natural unmodified Codex tool shape is recorded separately and cannot
substitute for the companion. The focused fake HTTP regression and present-ID,
missing-ID, mismatched-ID, or wrong-session facts cannot promote C1.4. Negative
correlation cases must stop before provider advancement and leave accounting
non-pending. The companion replaces the two existing `identity_replay`
inference slots; it adds no operation, retry, provider call, or budget ceiling.

The final 005-ad qualification at implementation `c5bdcf08999158521ae149f60f5b7c6bd2d92a1d`
passed the complete fake machine gate: 37/37 obligations and projections,
26/26 direct observer dispatches (6 compiler, 12 inference, 8 other), 12/12
terminal-valid inference observations, and exact fake-provider counter
agreement. The actual `identity_replay` companion passed with a streamed
returned function call, a non-streaming continuation omitting only the
optional item ID, matching the mandatory call ID, same admitted relationship,
terminal accounting, and zero pending/duplicate request IDs. Natural Codex
shape was recorded separately with the item ID present. The healthy synthetic
protected branch, with the fake semantic oracle unavailable, serialized and
passed all 29 selected rows; observer-failure, combined projection/cleanup,
and pre-dispatch mapping cases each serialized all 29 rows and stopped as
designed. Real protected inference remained `NOT RUN`.

## Objective-005-ae qualified framing and source-bound evidence

The direct provider observer accepts the exact Gateway-approved typed Responses
SSE representations with an explicit `event` header, data-only typed frames,
or a bounded mixture of both. An explicit header must match the JSON payload's
`type`; missing, empty, or unknown types, malformed frames, invalid ordering,
terminal/usage errors, duplicate terminals, and abnormal closure remain
fail-closed. Framing stays incremental and bounded at 16 KiB per frame and
128 KiB per stream, with comment handling, LF/CRLF, split/coalesced chunks,
close-once behavior, and the exact injected Gateway validator preserved.

Fresh fake qualification results are source-bound before any protected
credential access. The runner records the exact implementation SHA, a bounded
per-run identifier, hashes for the runner/observer/projection/provider-facts
source files, loaded helper-module paths and hashes, exact fake-manifest row
order/cardinality/status, and direct-observer inference lifecycle records.
The protected fake-gate validator rejects stale source/module hashes, invalid
run identity, missing/extra/reordered rows or projections, inconsistent
observed-field counts, incomplete lifecycle counters, and missing direct
records. Evidence is generated from the runner result; hand-written all-PASS
lists are not accepted. Protected acceptance, cutover, merge, and release
readiness remain separate decisions.

## Objective-005-af same-UID protected acceptance

The 005-af rehearsal runs its fake producer, validator, evidence handling, and
protected harness as the current execution UID. The fake result is an owned
0600 regular file with one link and is validated again under that same UID
before any protected credential resolution. The bounded Docker helper remains
the only privileged boundary; the whole runner is never elevated.

After the actual id-less companion, the fake qualification sends exactly three
additional Responses requests through the Gateway using the existing primary
and second test keys: missing call ID, mismatched call ID, and the valid call ID
under the second key. All must be denied as 4xx before provider dispatch, with
unchanged primary/second-key accounting and zero pending or duplicate request
IDs. These are pre-provider negative checks and add no inference allowance.

The fresh source-bound fake result and four serial synthetic protected cases
remain prerequisites for one newly authorized protected matrix. A protected
failure remains first-boundary evidence only; no protected retry, Qwen/service
mutation, cutover, merge, or release claim is permitted.

The final 005-af run on tested code `ba42a15cd99a13cf487dac687628fc42df31301e`
passed the complete fake gate (`37/37` rows and projections; `26` direct
dispatches: `6` compiler, `12` inference, `8` other; `12/12` inference
terminal-valid), the ownership-negative proof, all four synthetic protected
cases, cleanup, and secret-free logging. The single protected attempt stopped
at `C1.1` because independent provider-boundary acceptance was unavailable;
later protected inference was not run and the protected fixture remained
unchanged.

## Objective-005-ai per-response byte budget and stop evidence

The shared `BudgetController` opens a byte-accounting lifetime only after an
admitted direct HTTP response is returned. `max_stream_bytes` remains the
unchanged 128 KiB per-response cap; sequential responses reset only their
current counter at a valid response start while separately retaining bounded
all-lifetime totals. Dispatch rejection, stale context, concurrency failure,
stream closure, cancellation, and semantic failure cannot reset an active
response or clear the run's stop latch.

The direct observer records exact safe per-response received, accepted, and
rejected byte counts plus rejected-chunk counts. Network-chunk bytes remain
separate from incremental SSE frame bytes and no response is buffered for
qualification. The connected tests use unread asynchronous streams and cover
legal responses whose combined bytes exceed 128 KiB, mixed compiler/inference
lifetimes, exact-bound and single-response overflow, split/coalesced validated
SSE, rejected concurrent admission, timeout/cancellation/close handling, and
zero later dispatch after a latched failure.

`RunAccumulator` retains completed phase checkpoints and freezes the first
runtime failure's bounded phase, operation, ordinal, kind, lifetime, and cause
before cleanup. These facts remain separate from the acceptance manifest's
earliest unsatisfied row. Per-response byte evidence and all-lifetime totals
are retained as counts/classes only; projection or cleanup failures are
secondary and cannot replace the first failure. Objective-005-ai qualification
artifacts, when generated, are source-bound under `oap/evidence/005-ai/`.
The final fake qualification includes five serial synthetic protected cases:
healthy, the existing observer/projection/cleanup/pre-dispatch failures, and
a Codex-complete then first-vision-response stop whose vision context and
earlier Codex checkpoint remain serialized.

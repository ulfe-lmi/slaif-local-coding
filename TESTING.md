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

At implementation `45f9d64976b0f2a44f6c3223d767c28f5405e1a`, the fresh fake
machine gate passed 37/37 selected obligations with no missing result, first
failure, or retry. The direct observer independently recorded 23 attempted,
dispatched, responded, completed, and terminal-valid operations: 6 compiler
and 12 inference operations, with all 12 inference streams having first-byte
and normal-close facts. Fake-provider counters matched exact observer counts;
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
compiler and 12 inference calls, with 12/12 inference streams semantically
terminal-valid; fake-provider counters matched, all 29 synthetic protected
rows serialized, and cleanup passed. This is fake-only evidence and does not
establish protected acceptance.

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

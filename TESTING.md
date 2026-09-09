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

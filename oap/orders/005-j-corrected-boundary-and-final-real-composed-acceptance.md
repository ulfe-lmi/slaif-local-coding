# OAP Work Order — 005-j

## Objective

Amend Local Coding PR #7 with one corrected Local Coding -> protected Qwen A–I
boundary verification and, if green, immediately execute the final real Codex
0.149 -> exact Gateway PR #291 -> Local Coding -> protected Qwen -> Codex
acceptance matrix. Do not repeat the direct-provider control: 005-i already
proved that the exact provider-bound request received `2xx` SSE, valid terminal
`response.completed` usage, and normal close both through Local's outbound
transport and directly. The only unresolved direct-boundary fact is byte-exact,
parseable downstream forwarding after correcting the repository-only evidence
runner's event vocabulary and large-ASGI-chunk handling.

## GitHub and objective state

- Repository: `ulfe-lmi/slaif-local-coding`.
- Round: `005-j`; mode `AMEND_EXISTING_PR`; **NO NEW PR**.
- PR #7: `https://github.com/ulfe-lmi/slaif-local-coding/pull/7`.
- Base/head: `main` / `oap/005-gateway-ingress-integration`.
- Required starting 005-i report head:
  `d3168fa4a0c8e87f9e92567ef4f9283ed6b0f823`.
- Required 005-i implementation parent:
  `3e0eedb42dbb7d54108dc2f93732310aec550129`.
- Local PR is OPEN, non-draft, MERGEABLE/CLEAN; current `test` SUCCESS.

Read-only Gateway dependency:

- Repository: `ulfe-lmi/slaif-api-gateway`.
- PR #291: `https://github.com/ulfe-lmi/slaif-api-gateway/pull/291`.
- Exact current 155-p report head:
  `306ecb186b5c12db991a684e7c04e5c9f174eba2`.
- 155-p report parent:
  `a8a2a7a8a2e84fbe7dd42658173dd6358f709444`.
- Gateway 155-o report/product implementation:
  `c6b33c9d1527d35d987bf10f8276f30797bc892c` /
  `06752b1126545590a2e4232311fb92a52f663b41`.
- Gateway PR is OPEN, non-draft, MERGEABLE/CLEAN; all ten current checks are
  SUCCESS. 155-p contains the byte-restored safe fake/protected artifacts and
  no product change.

Abort before protected traffic if either exact PR head changes, any required
check is non-successful, or report topology is invalid.

## Accepted evidence and exact remaining gap

Accept Gateway 155-o/155-p's `local_qwen_owned` handoff as the historical
composed failure. Accept 005-i's fresh current evidence:

- the provider-bound request after Gateway policy has `POST /v1/responses`,
  model match, `stream=true`, one text input item, no tools/images/reasoning
  field, integer `max_output_tokens=4096`, and a 169-byte canonical synthetic
  body;
- Gateway source injects the reviewed route output default when the client
  omits `max_output_tokens`; this is not a Local diagnostic invention;
- Local outbound body equals the direct control body;
- Local outbound and exact direct-provider control both reached protected Qwen,
  received `2xx` `text/event-stream`, first bytes, `response.created`, valid
  terminal `response.completed` usage, and normal upstream close;
- no Local production code, Gateway product, protected service, or configuration
  was changed;
- direct provider availability/request compatibility is therefore no longer a
  blocker.

005-i cannot be called green because its first evidence run:

1. omitted the observed `response.reasoning_part.added`,
   `response.reasoning_part.done`, `response.reasoning_text.delta`, and
   `response.reasoning_text.done` names from its fixed vocabulary; and
2. marked a large ASGI downstream chunk invalid before splitting its complete
   bounded SSE lines, so stage-I byte equality/parseability was not accepted.

The implementation commit corrected both code paths and pure tests after the
protected run, but the immutable 005-i order prohibited a retry. No Local
production defect is presently proven.

## A. Mandatory zero-inference preflight

Before the one protected request:

1. Verify exact PR/report heads, parents, current checks, clean worktrees, and
   the complete Gateway 155-p safe artifact grammar.
2. Reconcile the exact 005-i diagnostic output only through its immutable safe
   report; do not recover/reopen raw bodies, streams, credentials, temp files,
   or session state.
3. Prove from exact Gateway source and focused pure tests that its resolved
   Codex route injects `max_output_tokens=4096` into the Local-bound request
   when omitted by the 155-o client call. Assert the complete expected
   provider-bound top-level field-name/value-class set and 169-byte canonical
   synthetic fixture shape without persisting raw runtime requests.
4. Prove `SSEFacts.consume()` splits complete CR/LF SSE lines before enforcing
   the per-line/event bound, while the independent total-stream bound remains
   effective. Cover:
   - one ASGI chunk at least 276569 bytes containing many individually bounded
     complete events;
   - the same bytes split across small chunks and arbitrary line boundaries;
   - one genuinely over-bound line/event;
   - total stream exact limit and limit+1;
   - incomplete final event, malformed JSON, duplicate terminal events, error
     event, and normal/abnormal close.
5. Prove the fixed vocabulary includes every event name observed by 005-i and
   the exact Gateway Codex 0.149 stream contract, while unknown names still
   fail the recognized-event stage. Do not make arbitrary events acceptable.
6. Prove stage I independently requires upstream/downstream `2xx`, SSE,
   first bytes, equal total bytes, equal streaming digest, downstream parseable
   terminal lifecycle, and normal close. A parser pass alone cannot substitute
   for byte equality; a digest match cannot substitute for terminal validity.
7. Prove the diagnostic makes exactly one Local protected inference request,
   never calls the direct-provider control or bounded variant, uses production
   `create_app` plus direct `AsyncHTTPTransport`, retains no raw values, and
   always removes its private temporary cache/state.
8. Run focused fake/proxy/SSE/timeout/disconnect/tool/image/constitution/
   identity/privacy tests and lint/type/compile gates required before live use.

Refactor or delete unused/redundant diagnostic code if necessary; do not expand
the 781-line repository-only runner into another instrumentation framework. It
must remain excluded from the wheel and production imports.

## B. Exactly one corrected Local -> protected Qwen verification

After every preflight item passes, run the corrected diagnostic exactly once
against the unchanged protected fixture. No direct-provider control, retry,
single-field variant, or alternate request is authorized.

The request must be the exact 005-i synthetic provider-bound shape and use the
production app/config/auth/route/tool/image/constitution paths with compiler
attempts remaining zero. Record only fixed structural facts and PASS/FAIL/
NOT_REACHED for:

```text
A dispatch begins
B protected request accepted / explicit status
C response headers arrive
D first bytes arrive
E SSE framing parseable
F event vocabulary recognized
G response.created appears
H valid response.completed usage and normal upstream close
I Local forwards byte-equal ordered parseable terminal SSE and normal close
```

Acceptance requires **A through I all PASS**. Also require model/body equality,
integer output-bound class, zero tools/images/compiler calls, `2xx`/SSE,
nonempty first-byte and terminal timing buckets, no transport exception,
one created/one completed lifecycle, equal byte counts/digests, and cleanup.

If any stage fails, stop without a second protected call or production change.
Publish the exact first stage and whether the failure is production-owned or
still evidence-runner-owned. Do not proceed to the composed run.

## C. Immediate real full-stack acceptance on A–I green

If and only if section B is green, run exactly one disposable composed
acceptance using the exact tested Local head and Gateway head
`306ecb186b5c12db991a684e7c04e5c9f174eba2`:

```text
real official Codex CLI 0.149.0 global-yolo
  -> disposable real Gateway PR #291 ASGI service
       temporary PostgreSQL 16 on loopback/tmpfs
       synthetic public keys/owners and local-coding-v1 signed module
  -> Local Coding candidate on 127.0.0.1:18031
       signed identity v1, exact search-tool filter,
       constitution compiler/cache/rehydration enabled
  -> unchanged protected Qwen
  -> valid terminal stream through Local/Gateway back to Codex
```

Reuse the existing Local rehearsal support and exact Gateway product modules/
fixtures. A detached Gateway checkout/venv is allowed; do not vendor, edit,
commit, push, or merge Gateway. Do not depend on either PR merging first. Avoid
the prior Gateway diagnostic relay where it is not product topology; any
evidence recorder must be proven byte-transparent by fake and direct boundary
tests before protected use.

Run one predeclared sequence, stopping at the first product/accounting failure
without retry:

1. Gateway/Local health/readiness and one visible public model.
2. Standard non-stream Responses request completes with provider usage.
3. Standard streaming request returns ordered recognized events,
   `response.created`, valid terminal `response.completed` usage, normal close,
   and official-client completion.
4. One small synthetic image request traverses the one-image route without
   changing protected image policy.
5. Real Codex 0.149.0 global-yolo performs ordinary local tool use, reads the
   exact delegated governance dependency, and receives effective compiled/
   cached/injected binding through Gateway -> Local -> Qwen.
6. Gateway service Bearer, signed body/path/query/route identity, timestamp,
   nonce, and exact request bytes are accepted by Local; disabled
   `tool_search`/`web_search` declarations are absent at Qwen while ordinary
   function/custom/call/result material is preserved.
7. The same owner/key/Codex session/repository zero-root history-reduction
   request rehydrates intended state with zero unnecessary compiler-model call.
8. A distinct Codex session under the same Gateway credential and a second
   owner/key remain isolated and cannot receive the first session's governance.
9. Exact/concurrent replay, body/query/path/route/signature tamper, explicit
   dropped/hosted choice, invalid public key, and over-quota requests reject at
   the correct pre-provider boundary without duplicate effects.
10. Every admitted public request has one reservation and one terminal ledger
    outcome; successes finalize provider-reported usage; no pending/duplicate
    IDs or inconsistent request/token/cost counters remain.
11. Local compiler calls create zero Gateway public ledger/reservation rows;
    no hosted-search fence/hold/fee or execution authority appears.
12. Failure/rollback and cleanup leave no corrupt accounting, replay, identity,
    cache, or provider state.

Fake Qwen, mocks, the direct Local check, and a provider control are not final
acceptance. The real composed path and real Codex response must pass.

## D. Privacy, protected-host, and resource law

Use only synthetic prompts/governance/images/tool fixtures and existing
protected credential references. Never commit, report, print, log, metric-label,
or persist raw bodies, prompts, source, model text, SSE payloads, tool schemas/
results, credentials, credential-source paths, private endpoints, identities,
signatures, nonces, canonical bytes, database URLs, or arbitrary exception
text. Evidence is restricted to fixed classes, PASS/FAIL states, counts,
booleans, safe versions, committed synthetic-fixture hashes, and bounded timing
buckets. Do not include protected endpoint values or credential-source paths in
the immutable report.

Do not stop/restart/change protected Qwen, its unit/config/drop-ins/model/
checkpoint/venv/patches/launch flags, listener, context/image/tool/reasoning
configuration, API-key files, firewall/VPN/network bindings, or active Codex
profiles. Do not start another model. Serialize protected calls and honor the
single-sequence GPU bound. Read-only health/models/process facts and the one
section-B inference plus section-C composed calls are authorized.

Use one uniquely named official `postgres:16` container only if section C runs:
loopback random port, tmpfs, `--rm`, finite health timeout, no privileged/host
network. `sudo` is limited to exact Docker read/pull/run/stop/remove/inspect
commands. No apt, daemon, Redis, Celery, email, admin, TLS, public bind, or
persistent database.

On every outcome remove exact driver-owned candidate/Gateway/PostgreSQL/relay/
fake/temp clone/venv/config/cache/Codex home/workspace/log/artifact/image state.
Prove no task listeners, containers, volumes, solely-pulled images, or processes
remain; both repository worktrees are clean; protected Qwen retains the same
PID/start/restart/listener/config facts; text remains inactive; 18021/18031/
random ports are absent. Direct protected Qwen remains the rollback path.

## E. Tests, documentation, and merge choreography

Run focused diagnostic and complete relevant regression tests, then full frozen
Ruff/format/mypy/pytest/build/wheel/sdist/compileall/shell/diff/secret/raw-log/
package-boundary gates and current Local CI. Skipped/not-run/pending is not pass.

On a complete composed pass, update `docs/SLAIF-GATEWAY-INTEGRATION.md`,
`TESTING.md`, `docs/OAP-RUNBOOK.md`, and Objective-005 completeness/criterion
ledger with exact tested heads, fixture-scoped evidence, cleanup, limitations,
and this deadlock-free merge choreography:

1. strategic review merges Local PR #7 first against the exact tested open
   Gateway head;
2. Gateway strategy updates only its Local dependency pin/audit artifact,
   reruns exact checks against merged Local main, then reviews/merges PR #291;
3. verify both remote default branches; preserve direct-Qwen rollback until a
   separately authorized persistent cutover/release.

No production, certification, compliance, generic model/hardware, multi-worker
replay, or persistent cutover claim follows from the disposable acceptance.

## Explicit non-goals

- No speculative Local production fix, Gateway product/OAP mutation, or
  protected Qwen workaround.
- No new PR, coding-agent merge, auto-merge, persistent deployment, public
  listener, direct-Qwen retirement, or real credential provisioning.
- No direct-provider diagnostic repeat, alternate prompt/request, output-bound
  variant, sandbox/bubblewrap work, broad host inventory, image benchmarking,
  or another diagnostic subsystem.
- No reopening solved Gateway tool, pair, identity/session, signed identity,
  route, fake composition, or accounting behavior absent direct contradiction.

## Publication contract

Amend only Local Coding PR #7. Commit exact activated order and `oap/active`
unchanged with all intended non-report work. Push implementation/tests/docs,
inspect/fix in-scope CI, record the literal implementation head, then atomically
publish exactly one immutable
`oap/reports/005-j-corrected-boundary-and-final-real-composed-acceptance.md`
with literal implementation SHA and `Report publication commit: SELF`. SELF
changes only that report, first parent equals implementation SHA, and it is the
remote PR head before exact response FIFO `OK`. Coding never merges.

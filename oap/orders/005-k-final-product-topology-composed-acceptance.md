# OAP Work Order — 005-k

## Objective

Amend Local Coding Objective-005 PR #7 with the final product-topology composed
acceptance. Accept 005-j's corrected A–I result as a green current
Local Coding -> protected Qwen boundary: one exact request returned valid
terminal SSE and Local forwarded byte/digest-equal ordered terminal bytes.
Do not rerun that protected diagnostic or its direct-provider control. Remove or
fix the disposable evidence relay's pre-traffic readiness failure using only
fake/no-model work, then run exactly one full real Codex 0.149 -> exact Gateway
PR #291 -> Local Coding -> protected Qwen -> Codex acceptance matrix with Local
connected directly to protected Qwen. Correct only directly observed product
defects; do not reopen solved Gateway identity/tool/pair/routing/accounting or
Local provider transport.

## GitHub and OAP state

- Repository: `ulfe-lmi/slaif-local-coding`.
- Round: `005-k`; mode `AMEND_EXISTING_PR`; **NO NEW PR**.
- PR #7: `https://github.com/ulfe-lmi/slaif-local-coding/pull/7`.
- Base/head: `main` / `oap/005-gateway-ingress-integration`.
- Required starting 005-j report head:
  `d634d22e3591e4b6fb2f7f942cfe07c9582682d7`.
- Required 005-j implementation parent:
  `55d5e2c43322fd145af5672bab4e396816a2ff1c`.
- Local PR is OPEN, non-draft, MERGEABLE/CLEAN; current `test` SUCCESS.

Read-only Gateway dependency:

- Repository: `ulfe-lmi/slaif-api-gateway`.
- PR #291: `https://github.com/ulfe-lmi/slaif-api-gateway/pull/291`.
- Exact current 155-p report head:
  `306ecb186b5c12db991a684e7c04e5c9f174eba2`.
- 155-p parent: `a8a2a7a8a2e84fbe7dd42658173dd6358f709444`.
- 155-o report/product head:
  `c6b33c9d1527d35d987bf10f8276f30797bc892c` /
  `06752b1126545590a2e4232311fb92a52f663b41`.
- Gateway PR is OPEN, non-draft, MERGEABLE/CLEAN; all ten current checks
  SUCCESS. 155-p is a zero-traffic artifact restoration with no product change.

Abort before protected traffic if either exact PR head changes, any required
check is not successful, or report topology is invalid.

## Accepted 005-j boundary evidence

Strategic review accepts the product boundary as green despite the report's
missing timing metadata:

- exactly one Local protected dispatch and no direct control/retry/variant;
- exact canonical 169-byte synthetic provider-bound body, model match,
  `stream=true`, integer Gateway route default `max_output_tokens=4096`, zero
  tools/images/compiler attempts;
- stages A–I all PASS;
- protected response `2xx`/SSE, first bytes, fixed vocabulary recognized, one
  `response.created`, one valid `response.completed` with usage, no error or
  duplicate terminal, normal upstream/downstream close;
- Local downstream total bytes and streaming digest equal its protected
  upstream bytes and the downstream lifecycle is parseable/terminal;
- protected Qwen remained active with unchanged PID/start/restart/listener;
- no Local production or Gateway product correction was required.

The missing first-byte/terminal timing buckets are an observability fact to add
without another protected boundary call. They do not negate byte-exact terminal
forwarding.

The 005-j composed attempt is not product evidence: it stopped before Local or
Gateway startup and before public/protected traffic with fixed
`service_ready_timeout` while waiting for a disposable evidence relay. That
relay is not part of the product topology.

## A. Zero-protected-traffic harness closure

Before protected inference:

1. Verify exact heads/reports/checks/worktrees and current protected read-only
   health/model/service facts.
2. Identify which disposable service produced `service_ready_timeout`, its
   exact expected readiness contract, and why it could not become ready. Record
   only a fixed service class and failure class—no endpoint, credential source,
   raw log, or arbitrary exception.
3. Remove the non-product relay from the final topology wherever safe. The
   required product path is Gateway directly to Local and Local directly to
   Qwen. If any recorder remains, prove it is necessary, byte-transparent,
   bounded, ready, and cleanup-safe entirely against fake endpoints first.
4. Reuse/consolidate the existing `gateway_accounting_rehearsal.py`, Gateway
   conformance support, and 005-i/j differential utilities. Do not vendor the
   Gateway verifier, copy Gateway product code, or add another broad diagnostic
   subsystem. Delete dead/redundant relay support rather than accumulating it.
5. Add deterministic timing measurement at the final standard streaming client
   boundary: request start -> response headers, first SSE bytes, terminal
   completion, normal close. Emit only nonempty bounded buckets, never exact
   private timestamps, payloads, IDs, or model text. Prove timing logic with a
   fake delayed stream; do not rerun the direct protected diagnostic.
6. Build one deterministic composed driver with only a provider target mode
   difference: `fake` or protected runtime reference. Both modes use the exact
   same Gateway/Local/PostgreSQL seed, request sequence, signed identity,
   timeouts, and cleanup logic.
7. Run the complete fake-Qwen composed rehearsal until Gateway and Local
   health/readiness, ordinary non-stream, terminal streaming, signed identity,
   safe accounting, and teardown pass. Fake output must use the reviewed Qwen
   Responses lifecycle including reasoning/tool event vocabulary as applicable.
8. Run all focused driver/startup/timeout/SSE/accounting/privacy tests and
   lint/type/compile gates before switching the already-proven driver to the
   protected target.

No protected inference call is allowed during A. Read-only health/models is
allowed once. Do not modify Gateway or protected Qwen to repair the harness.

## B. Exactly one real composed acceptance run

After every section-A gate passes, run the composed driver once in protected
mode. One run may execute the predeclared request matrix below; do not retry the
run, repeat failed model calls, change prompts/limits between attempts, or fall
back to fake results.

Topology:

```text
real official Codex CLI 0.149.0 global-yolo
  -> real disposable Gateway PR #291 ASGI service on loopback
       temporary PostgreSQL 16 on loopback/tmpfs
       synthetic public keys/owners and exact local-coding-v1 signed module
  -> Local Coding candidate on 127.0.0.1:18031
       signed identity v1, exact search-tool filter,
       constitution compiler/cache/rehydration enabled
  -> protected Qwen directly, with no non-product relay
  -> terminal response through Local and Gateway back to Codex
```

Use detached exact checkouts/venvs as needed; neither PR must merge first.
Gateway is read-only and must not be edited/pushed/merged.

Run sequentially and stop at the first product/accounting failure:

1. Local/Gateway health/readiness and one authenticated visible public model.
2. One standard non-stream Responses text request completes with safe
   provider-reported usage.
3. One standard streaming request proves Gateway -> Local -> Qwen request,
   `2xx` SSE headers, nonempty bounded header/first-byte/terminal timing buckets,
   ordered recognized events, one `response.created`, valid terminal
   `response.completed` usage, normal close, byte-transparent Local relay, and
   official-client completion back through Gateway.
4. One small synthetic image request traverses the configured one-image route;
   no image benchmark or full/crop repeat.
5. Real Codex 0.149.0 global-yolo uses ordinary local tools, reads the exact
   delegated governance dependency, and receives effective compiled/cached/
   injected binding through Gateway -> Local -> protected Qwen.
6. Gateway service Bearer and signed body/path/query/route identity are accepted
   by Local; disabled `tool_search`/`web_search` declarations are absent at Qwen
   while ordinary function/custom/call/result content remains intact.
7. Same owner/key/Codex session/repository zero-root history reduction reuses
   intended compiler/cache/rehydration state with zero unnecessary new compiler
   model attempt.
8. A distinct Codex session under the same Gateway credential and a second
   owner/key remain isolated and receive none of the first session's governance.
9. Exact and concurrent replay, body/query/path/route/signature tamper, explicit
   dropped/hosted choice, invalid public key, and over-quota requests reject at
   the correct pre-provider boundary with no duplicate provider/accounting work.
10. Every admitted public request has exactly one reservation and terminal
    ledger outcome; successful requests finalize provider usage; request/token/
    cost counters are consistent and no pending/duplicate ID remains.
11. Local compiler calls create zero Gateway public reservation/ledger rows;
    no hosted search fence/hold/fee or execution authority appears.
12. Controlled failure/rollback and final cleanup leave no corrupt accounting,
    replay, identity, cache, or provider state.

Mocks, fake Qwen, direct Local evidence, or health checks do not substitute for
this real composed pass. If the run fails after traffic begins, publish the
first exact component/stage and direct evidence; do not add diagnostics or retry.

## C. Privacy, protected-host, resource, and cleanup law

Use only synthetic prompts/governance/images/tools and existing protected
credential references. Do not commit, report, print, log, metric-label, or
persist raw bodies, prompts, source, model text, SSE payloads, tool schemas/
results, credentials, credential-source paths, private endpoints, identities,
signatures, nonces, canonical bytes, DB URLs, session values, or arbitrary
exceptions. Evidence is fixed classes, statuses, counts, booleans, safe versions,
committed synthetic-fixture hashes, and bounded timing buckets. The immutable
report must not include protected endpoint values or credential-source paths.

Do not stop/restart/change protected Qwen, its unit/config/drop-ins/model/
checkpoint/venv/patches/launch flags, listener, context/image/tool/reasoning
configuration, API-key files, firewall/VPN/network bindings, or active Codex
profiles. Do not start another model. Serialize protected calls and honor its
single-sequence limit. Read-only health/models and section-B calls only are
authorized.

Use one uniquely named official `postgres:16` container: loopback random port,
tmpfs, `--rm`, finite health timeout, no privileged/host network. `sudo` is
limited to exact Docker read/pull/run/stop/remove/inspect operations. No apt,
daemon, Redis, Celery, email, admin, TLS, public bind, or persistent database.

On every outcome remove exact driver-owned candidate/Gateway/PostgreSQL/fake/
temp clone/venv/config/cache/Codex home/workspace/Node/log/artifact/image state.
Prove no task listeners, containers, volumes, solely-pulled images, or processes
remain; both worktrees are clean; protected Qwen retains the same PID/start/
restart/listener/config facts; text remains inactive; 18021/18031/random ports
are absent. Preserve unrelated ignored Local `.venv`. Direct Qwen remains the
rollback path.

## D. Regression, documentation, and merge choreography

Run focused harness/startup/fake/SSE/timing/auth/tool/image/constitution/cache/
identity/replay/accounting/privacy tests plus full frozen Ruff/format/mypy/
pytest/build/wheel/sdist/compileall/shell/diff/secret/raw-log/package-boundary
gates and current Local CI. `SKIPPED|NOT RUN|BLOCKED|PENDING` is never pass for
an acceptance requirement.

On complete pass update `docs/SLAIF-GATEWAY-INTEGRATION.md`, `TESTING.md`,
`docs/OAP-RUNBOOK.md`, and Objective-005 completeness/criterion ledger with
exact tested heads, fixture-scoped evidence, cleanup, and remaining deployment/
release limitations.

Record deadlock-free merge choreography:

1. strategic review merges Local PR #7 first against exact tested open Gateway
   head `306ecb186b5c12db991a684e7c04e5c9f174eba2`;
2. Gateway strategy updates only its Local dependency pin/audit artifact and
   reruns checks against merged Local main, then reviews/merges Gateway PR #291;
3. verify both default branches; direct-Qwen rollback remains until separately
   authorized persistent cutover/release.

No production, certification, compliance, generic hardware/model,
multi-worker replay, or persistent-cutover claim follows.

## Explicit non-goals

- No additional direct Local/provider diagnostic, protected request-shape
  variant, alternate prompt, or evidence relay experiment.
- No speculative Local production fix, Gateway code/OAP change, protected Qwen
  workaround, service mutation, or new diagnostic framework.
- No new PR, coding merge/auto-merge, persistent service/profile/database,
  public listener, direct-Qwen retirement, or real credential provisioning.
- No reopening solved Gateway tool/pair/identity/session/signed route/fake
  composition/accounting behavior absent direct contradiction.
- No sandbox/bubblewrap work, broad host inventory, image benchmarking, model
  quality evaluation, or release claim.

## Publication contract

Amend only Local Coding PR #7. Commit exact activated order and `oap/active`
unchanged with all intended non-report work. Push support/tests/docs, inspect/
fix in-scope CI, record literal implementation head, then atomically publish
exactly one immutable
`oap/reports/005-k-final-product-topology-composed-acceptance.md` with literal
implementation SHA and `Report publication commit: SELF`. SELF changes only
that report, first parent equals implementation SHA, and it is the remote PR
head before exact response FIFO `OK`. Coding never merges.

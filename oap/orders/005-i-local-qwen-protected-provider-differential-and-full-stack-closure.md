# OAP Work Order — 005-i

## Objective

Amend Local Coding Objective-005 PR #7 with one bounded Local Coding ↔ protected
Qwen provider differential and, once that boundary is green, the final real
Codex 0.149 -> exact Gateway PR #291 -> Local Coding -> protected Qwen -> Codex
acceptance run. Start from the authoritative Gateway 155-o/155-p handoff:
Gateway delivered one request to Local Coding, Local Coding invoked protected
Qwen once, no protected Qwen response was observed, no Local response returned,
and Gateway emitted an error. Localize the first failing transport/SSE stage,
correct only the owning Local layer if directly proven, or publish a precise
external Qwen/provider blocker. Do not reopen solved Gateway identity, tool,
pair, routing, fake-composition, or accounting infrastructure without direct
contradictory evidence.

## GitHub and OAP state

- Repository: `ulfe-lmi/slaif-local-coding`.
- Round: `005-i`; mode: `AMEND_EXISTING_PR`; **NO NEW PR**.
- PR: `https://github.com/ulfe-lmi/slaif-local-coding/pull/7`.
- Base/head: `main` / `oap/005-gateway-ingress-integration`.
- Required starting Local report head / 005-h SELF:
  `6ee2a51aa7b03d4df46e0662d88cc33fd0ef7db8`.
- Required 005-h implementation parent:
  `d2093650ef61200d3ed6ff9516bfd73eb2675182`.
- Local PR is OPEN, non-draft, MERGEABLE/CLEAN; current `test` is SUCCESS.

Gateway dependency, read-only:

- Repository: `ulfe-lmi/slaif-api-gateway`.
- PR #291: `https://github.com/ulfe-lmi/slaif-api-gateway/pull/291`.
- Exact current 155-p report head:
  `306ecb186b5c12db991a684e7c04e5c9f174eba2`.
- 155-p activation/parent:
  `a8a2a7a8a2e84fbe7dd42658173dd6358f709444`.
- Gateway 155-o report head:
  `c6b33c9d1527d35d987bf10f8276f30797bc892c`.
- Gateway 155-o final product/verifier implementation head:
  `06752b1126545590a2e4232311fb92a52f663b41`.
- Gateway PR is OPEN, non-draft, MERGEABLE/CLEAN; all ten current
  CI/CodeQL/PostgreSQL/E2E/Compose/documentation checks are SUCCESS.
- 155-p changes no product path and restores the exact safe fake/protected
  155-o artifacts. Use the exact current head for coordinated execution; never
  edit, push, merge, or create Gateway state.

Abort before protected traffic if either exact PR head changes, any required
check is non-successful, or topology/report-parent verification fails.

## Authoritative handoff and provisional diagnosis

Accept the following 155-p byte-restored protected facts unless new direct
evidence contradicts them:

```text
Gateway -> Local request count: one
Gateway <- Local response count: zero
Local rejected/handler/truncated/downstream-close: all false
Local -> Qwen inference count: one
Qwen upstream response count: zero
Qwen status: unknown
Qwen content expectation: SSE
Qwen terminal/handler/truncated/path-rejection: all false
Gateway error event: true
Gateway protected accounting terminal: false
safe owner classification: local_qwen_owned
```

The exact fake composed path passed through Gateway -> Local Coding -> fake
Qwen -> Local Coding -> Gateway, with valid `response.created` and
`response.completed`, one Gateway-to-Local response, one Qwen response, and
terminal accounting. Gateway made no product correction because protected
evidence did not assign fault to Gateway.

The remaining possibilities are limited to Local outbound construction,
endpoint/model/auth configuration, Local HTTP transport/timeout/cancellation,
Local stream consumption/forwarding, protected Qwen request compatibility or
runtime failure, fake-provider fidelity, or another directly evidenced
Local↔Qwen transport fact. Do not assume which one.

## A. No-model/read-only preflight

Before any inference call:

1. Verify exact Local/Gateway heads, report-only commits, parents, complete
   155-p safe artifact grammar, PR states, and current successful checks.
2. Verify Local checkout clean at the required head; inspect the full Objective
   005 diff and current `app.py`, configuration, tool/image/constitution
   transforms, compiler bypass, upstream credential substitution, HTTPX
   timeouts, streaming iterator, disconnect, and error paths.
3. Verify protected vision Qwen read-only facts: active/running unit, PID/start/
   restart count, private listener, model ID, Responses capability profile,
   context/image limits, and health/models. Do not render the endpoint,
   credential source, credential, or launch-file path in report evidence.
4. Verify port 18031 and every chosen temporary port is free; text Qwen remains
   inactive; no unrelated container/process is in scope.
5. Extract in memory the exact safe structural request used by 155-o composed
   mode and compare it with the Local fake-Qwen request. Record only method,
   path class, model equality, `stream`, top-level field-name set, input/tool/
   image count classes, filtered tool-type counts, presence/value class of
   output/reasoning limits, non-secret header-name classes, body byte length,
   timeout values, and equality booleans. Do not retain raw body or values.
6. Confirm the fake differential can model incremental valid Responses SSE:
   headers, first chunk before completion, `response.created`, optional deltas,
   `response.completed`, usage, normal close, and downstream forwarding. Add
   only the narrow fake fidelity needed for the observed request.

No inference call is allowed until all six preflight items pass.

## B. Smallest direct Local Coding -> protected Qwen diagnostic

Use one repo-owned, bounded, privacy-safe diagnostic. Prefer constructing the
production `create_app` path in process with an `httpx.AsyncHTTPTransport`
delegate wrapped by a repository-only stage recorder, so Local connects
directly to protected Qwen without Gateway or an evidence relay changing the
network path. A temporary candidate on 18031 is allowed only if necessary to
exercise the exact production behavior.

Send exactly one synthetic, signed, composed-equivalent streaming Responses
request through Local Coding. Use the 155-o method/path/model/field classes and
same post-tool/image/constitution behavior. Keep the request bounded and do not
add a semantic field merely to make it succeed before reproducing the exact
shape.

Record PASS/FAIL/NOT_REACHED separately for:

```text
A connection/request dispatch begins
B protected HTTP request is accepted or an explicit status is returned
C response headers arrive
D first response body bytes arrive
E SSE framing is structurally parseable
F Responses event types are recognized
G response.created appears
H response.completed with valid terminal usage appears
I Local forwards the same ordered raw stream and normal close downstream
```

Also retain only fixed facts for method/path class, model match, stream mode,
post-filter tool/image counts, timeout/cancellation class, status class,
content-type class, first-byte/terminal elapsed buckets, normal close,
transport exception class allowlist, and whether an upstream error event/body
or timeout occurred. Do not print or persist raw credentials, endpoints,
headers, bodies, prompts, model text, tool schemas/results, identities, SSE
payload text, private paths, or arbitrary exceptions.

This first request is the only protected Local diagnostic before an ownership
decision. Do not retry it.

## C. Minimum discriminating controls and ownership decision tree

If the exact Local diagnostic succeeds through I, stop diagnosis. Treat the
155-o failure as no longer reproducible in the direct product topology, record
the exact current runtime/config difference if safely knowable, and proceed to
the full composed acceptance in section E without another diagnostic round.

If it fails, use at most one direct provider control with the exact same
synthetic request bytes and relevant non-secret transport configuration,
bypassing Local. Reuse bytes only in memory and close/cancel the failed request
before the control. Classify:

1. **Local request construction** — direct provider accepts the intended
   request, while Local outbound bytes differ in method/path/model/field/tool/
   image/limit structure and the difference explains the failure.
2. **Local provider transport** — exact direct provider succeeds through
   headers/body/terminal, while Local fails before or during headers/body due to
   HTTP client, timeout, cancellation, credential substitution, or connection
   lifetime.
3. **Local SSE forwarding** — protected Qwen produces a valid terminal stream,
   but Local fails at E–I, closes early, reorders/alters bytes, or fails to
   release/cancel correctly.
4. **Protected Qwen/provider** — Local and exact direct provider fail at the
   same stage/status/timeout, or Qwen closes/hangs/errors before a response.
5. **Fake fidelity** — fake accepts a shape or lifecycle materially different
   from protected behavior at the first divergence; correct the fake narrowly,
   then apply ownership above.
6. **Unexpected Gateway ownership** — only if a green direct Local path and a
   controlled composed rerun directly prove Gateway changes/cancels the request
   or response before the Local↔Qwen boundary. Do not infer this from absence.

The 155-o request construction omitted/presented output/reasoning bounds exactly
as observed. If both Local and exact direct-provider requests fail and the only
plausible structural discriminator is an absent output bound, one additional
single-field bounded provider variant is authorized. It must differ only by a
finite `max_output_tokens`, run once, and may prove a verifier/request-contract
or protected-provider behavior difference. It does not authorize Local to
invent a default or rewrite caller intent.

Maximum protected diagnostic inference calls before a fix/handoff: three
(one Local exact, one direct exact if needed, one single-field bounded provider
variant only if needed). Fewer is preferred. No repeated equivalent call.

## D. Owning-layer correction

- If Local construction, transport, or SSE behavior is directly proven wrong,
  implement the smallest production correction and matching faithful fake/live
  regression tests. One post-fix direct Local verification call is allowed.
- If fake behavior is the first divergence, correct only the fake contract and
  tests; do not change production behavior without product evidence.
- If protected Qwen/service/configuration owns the failure, make no Local or
  Gateway workaround and do not mutate the protected service. Publish the
  precise stage/status/request-contract handoff and exact evidence needed to
  resume.
- If direct evidence contradicts 155-o and assigns Gateway ownership, stop
  before Gateway mutation and publish the exact contradiction.

Any Local fix must preserve signed identity, service/provider credential
isolation, replay/idempotency, route-scoped search-tool filtering, ordinary
local tools and call/results, image policy, constitutional observation/compiler
bypass/cache/rehydration, principal/session/repository/route isolation,
failure-closed behavior, raw streaming order, disconnect cancellation, bounded
resources, and no raw-content logging.

Do not manufacture `response.completed`, buffer/reconstruct the whole stream,
swallow upstream errors, weaken timeouts or auth, add unbounded diagnostics, or
special-case the synthetic prompt.

## E. Immediate final composed acceptance after a green boundary

Once direct Local↔protected-Qwen passes (initially or after a proven Local fix),
run exactly one full disposable acceptance using Local PR #7's resulting head
and exact Gateway PR #291 head `306ecb186b5c12db991a684e7c04e5c9f174eba2`:

```text
real Codex CLI 0.149.0 global-yolo
  -> real disposable Gateway PR #291 ASGI service
       temporary PostgreSQL 16, loopback-only, tmpfs
       synthetic public keys/owners, exact local-coding-v1 signed module
  -> Local Coding candidate on 127.0.0.1:18031
       signed identity v1, search-tool filter, constitution/rehydration enabled
  -> protected Qwen runtime
  -> terminal stream back through Local and Gateway to Codex
```

Reuse/harden the existing repository-only rehearsal driver and the exact
Gateway 155-p product contract; do not vendor Gateway or build another broad
diagnostic system. Gateway and Local may run from detached exact checkouts/
venvs. Do not require either PR to merge first.

The one composed run must prove:

1. authenticated model visibility and readiness;
2. ordinary non-stream Responses success;
3. streaming success with headers, first bytes, recognized ordered events,
   `response.created`, valid terminal `response.completed`/usage, normal close,
   and Codex-visible completion;
4. one small synthetic image request preserves route policy;
5. real Codex 0.149 global-yolo uses ordinary local tools, acquires the exact
   delegated governance dependency, and receives effective compiled/injected
   binding through Gateway/Local/Qwen;
6. Gateway-signed Local identity accepted with exact body/path/query binding;
7. same owner/key/Codex session/repository reuses intended Local compiler/cache/
   rehydration state with zero unnecessary new compiler-model attempt;
8. an independent Codex session under the same Gateway credential and a second
   owner/key remain isolated and cannot receive the first session's governance;
9. exact replay, concurrent replay, signature/body/query/path/route tamper,
   explicit dropped/hosted tool choice, invalid public key, and over-quota
   cases reject at the correct pre-provider boundary without duplicate effects;
10. one public admitted request maps to one reservation and one terminal ledger
    outcome; successful requests finalize provider-reported usage; no pending/
    duplicate IDs or inconsistent request/token/cost counters remain;
11. Local compiler calls create no Gateway public reservation/ledger rows and
    no hosted search fence/hold/fee or execution authority appears;
12. errors/rollback leave no corrupt accounting, cache, replay, identity, or
    provider state.

Mocks, fake Qwen, direct curl, and the Local diagnostic are necessary evidence
only; none substitutes for this real composed pass.

## F. Privacy, protected-host, resource, and cleanup law

Use only synthetic prompts/governance/image/tool fixtures and existing protected
credential references. Raw prompts, bodies, source, images, tool output, model
text, identities, signatures, nonces, canonical bytes, credentials, credential-
source paths, private endpoints, database URLs, and arbitrary errors must not
enter committed files, reports, logs, metrics, cache filenames, ledger/audit
metadata, or terminal evidence. Reports use only fixed classes, booleans,
counts, safe versions, hashes of committed synthetic fixtures, and bounded
timing buckets.

Do not stop/restart/change protected Qwen, its user unit/config/drop-ins/model/
checkpoint/venv/patches/launch flags, port 18020, context/image/tool/reasoning
configuration, API-key files, firewall/VPN/network bindings, or active Codex
profiles. Do not start a second model. Serialize protected calls and respect
the one-sequence GPU limit. Read-only health/models/service/process facts and
the bounded authorized inference calls above are allowed.

Use a unique disposable PostgreSQL container with official `postgres:16`,
loopback random port, tmpfs, `--rm`, finite health wait, no privileged/host
network. `sudo` is authorized only for exact Docker read/pull/run/stop/remove/
inspect operations. No apt, daemon, firewall, system network, persistent DB,
Redis, Celery, email, admin, TLS, or public bind.

On every result stop/remove exact candidate/Gateway/PostgreSQL/relay/fake
processes and remove only driver-owned temp clone/venv/config/cache/Codex home/
workspace/log/artifact/image state. Prove no temp listeners, containers,
volumes, images pulled solely for the run, or processes remain; Local/Gateway
worktrees remain clean; protected Qwen remains active with the same PID/start/
restart/listener/config facts; text stays inactive; 18021/18031/random ports are
absent. Direct protected Qwen access remains available as rollback and is not
retired.

## G. Tests, documentation, and completion evidence

Run focused fake/transport/SSE/timeout/disconnect/auth/tool/image/constitution/
cache/identity/replay/privacy tests, the bounded live diagnostic, and—only after
the direct boundary is green—the one full composed run. Run the complete frozen
Ruff/format/mypy/pytest/build/wheel/sdist/compileall/shell/diff/secret/raw-log/
package-boundary checks and current GitHub CI. `SKIPPED|NOT RUN|BLOCKED|PENDING`
is never pass.

On a full pass update `docs/SLAIF-GATEWAY-INTEGRATION.md`, `TESTING.md`, the OAP
runbook, and Objective-005 completeness/criterion ledger with exact tested heads,
fixture-scoped evidence, merge choreography, and remaining persistent deployment/
release limits. Do not claim production, certification, generic provider/model,
or multi-worker replay readiness.

If full acceptance passes, document merge choreography without deadlock:

1. Local PR #7 is reviewed/merged first against exact tested Gateway PR #291
   head while Gateway PR remains open and pinned;
2. Gateway strategy updates only its dependency pin/report as needed, reruns
   exact cross-repository checks against merged Local main, then reviews/merges
   Gateway PR #291;
3. verify both remote default branches and preserve direct-Qwen rollback until
   separate persistent cutover/release authority.

## Explicit non-goals

- No speculative Gateway code/spec/OAP change or Gateway merge.
- No protected Qwen/service/configuration mutation or hidden workaround.
- No new Local PR, Local merge by coding, persistent cutover, direct-Qwen
  retirement, public listener, or real credential provisioning.
- No reopening Codex 0.149 tool envelope, exact pair, Gateway identity/session,
  signed identity, route, or fake composition absent direct contradiction.
- No image benchmarking, model-quality evaluation, sandbox/bubblewrap work,
  broad host inventory, or unlimited diagnostic instrumentation.

## Publication contract

Amend only Local Coding PR #7. Commit the exact activated order and `oap/active`
unchanged with all intended non-report work. Push all implementation/tests/docs/
evidence support, inspect/fix in-scope CI, and record the literal implementation
head. Atomically publish exactly one immutable
`oap/reports/005-i-local-qwen-protected-provider-differential-and-full-stack-closure.md`
with literal implementation SHA and `Report publication commit: SELF`. SELF
changes only that report, its first parent equals the implementation SHA, and it
is the remote PR head before exact response FIFO `OK`. Coding never merges.

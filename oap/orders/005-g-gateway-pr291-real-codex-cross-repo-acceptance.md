# OAP Work Order — 005-g

## Objective

Amend Objective-005 PR #7 with one exact-head, disposable cross-repository
acceptance run using Gateway PR #291's signed `local-coding-v1` server module,
Local Coding PR #7, temporary PostgreSQL, and the active Qwen vision fixture.
Prove real Codex 0.149 text/tool/governance traffic, signed request identity,
route-scoped tool filtering, provider usage, Gateway quota/accounting, identity
isolation, and complete rollback. Do not modify/merge Gateway PR #291 or persist
any service/profile/database/container state.

## GitHub objective state

- Local Coding repository: `ulfe-lmi/slaif-local-coding`.
- Numeric objective / round: `005` / `005-g`.
- PR mode: `AMEND_EXISTING_PR`; **NO NEW PR**.
- Local Coding PR #7:
  `https://github.com/ulfe-lmi/slaif-local-coding/pull/7`.
- Base/head: `main` / `oap/005-gateway-ingress-integration`.
- Current verified Local Coding remote head / 005-f SELF:
  `356be8345dd71d6fddf829278651d18e485731d4`.
- Local Coding implementation parent:
  `d235d1ac3d5b4e99158098b79d280624167efe50`.
- Local PR OPEN/non-draft/MERGEABLE/CLEAN; report-head `test` SUCCESS.

Gateway dependency:

- Repository: `ulfe-lmi/slaif-api-gateway`.
- Gateway main: `7ffce834915b74809109e8b579d8541cdcfa9df7`.
- Gateway PR #291:
  `https://github.com/ulfe-lmi/slaif-api-gateway/pull/291`.
- Exact Gateway PR head / 155-b report commit:
  `c68fa511141a0c21d420e7a94100f717e674553f`.
- Gateway implementation parent:
  `eac9c6354e19fdfa8574dc799fa5f1395382756f`.
- Gateway PR OPEN/non-draft/MERGEABLE/CLEAN; all ten current CI/CodeQL/
  PostgreSQL/E2E/Compose/docs checks SUCCESS.
- Gateway PR explicitly pins Local Coding head `356be834...` and must not merge
  while Local Coding PR #7 remains open.

Use only these exact heads. Abort before setup if either remote head/check state
changes.

## Accepted prior state

Accept Local Coding 005-a/b/e/f service auth, route tool filtering, signed
identity v1, replay protection, request-scoped cache/rehydration identity, and
vectors. Accept Gateway 155-a/b reports only as mocked/pinned fake-Qwen
conformance and containment—not real Codex/Qwen acceptance.

005-c standard text/SSE/image/accounting subset passed against old Gateway main;
real Codex was rejected before reservation. 005-d proved no configuration-only
workaround. Gateway PR #291 is the authorized external implementation intended
to resolve those exact gaps.

## A. No-live exact-head preflight

Before Docker/PostgreSQL/listeners/Qwen:

1. clone/detach Gateway PR #291 at exact `c68fa511...` into a driver-owned
   private temp root; verify clean;
2. verify Local Coding checkout/head exact `356be834...` and clean;
3. verify both conformance fixtures byte-for-byte/provenance against Gateway
   copies:
   - `responses_tool_filter_vectors.json`;
   - `signed_identity_v1_vectors.json`;
4. import actual Gateway `local-coding-v1` module, route contract, identity
   derivation, exact-body transport, provider factory, and request policy;
5. run one no-model Codex 0.149 envelope capture in a fresh driver-owned
   CODEX_HOME and require Gateway PR #291 policy/route preflight accepts the
   exact envelope while Local Coding postcondition removes disabled declarations;
6. verify ordinary function/custom tools remain and explicit hosted execution/
   dropped tool choice still rejects;
7. validate service/signing/derivation secrets are distinct and synthetic;
8. validate path-safety guard rejects host CODEX_HOME/cache/session/history and
   every root outside repo or driver-owned temp.

If any preflight fails, stop before Docker/listeners/Qwen and publish exact fixed
facts. No repair/retry against live services.

## B. Disposable topology

Use the same rollback-proven shape as 005-c, updated for Gateway PR #291:

```text
standard OpenAI client + disposable Codex 0.149 global yolo
  -> Gateway PR #291 app on random loopback port
       temporary PostgreSQL 16 container, loopback random port, tmpfs
       local-coding-v1 signed module
  -> Local Coding PR #7 candidate on 127.0.0.1:18031
       service_bearer_signed_identity_v1
       responses_tool_policy=drop_disabled_codex_search
       fresh private cache, rehydration enabled
  -> protected Qwen vision 127.0.0.1:18020/v1
```

No Redis/Celery/email/admin/TLS/public binding. Use synthetic public keys,
service/signing/derivation/DB secrets and existing protected Qwen env reference.

Docker law:

- record preexisting containers/images;
- exact unique container name with random suffix;
- official `postgres:16`, `--rm`, loopback bind, tmpfs, finite health timeout;
- no privileged/host network;
- remove exact container/volume/image if newly pulled;
- `sudo` only for exact Docker read/pull/run/stop/remove/inspect commands;
- no apt/system daemon/network/firewall changes.

## C. Gateway seed and signed route

Use Gateway migrations and service/repository APIs to seed only synthetic:

- one `openai_compatible` provider selecting static module `local-coding-v1`;
- exact Local Coding `/v1` base URL and service Bearer env reference;
- distinct signed identity derivation/signing secret env references;
- one enabled public model route
  `qwen3.8-27b-vision -> qwen3.8-27b` with exact module/tool/signed-identity
  capability versions;
- responses policy with validated Local Coding repository scope and Codex
  client envelope/tools/streaming capabilities;
- at least two active low-quota synthetic Gateway keys/owners for identity
  isolation proof;
- deterministic EUR pricing sufficient for normal reservation/finalization;
- no production metadata/personal data/real provider secret.

Run actual Gateway ASGI app and Local Coding production `create_app`; access logs
and raw logging disabled.

## D. Bounded traffic sequence

Run sequentially, no retries after a product/accounting failure:

1. Gateway health/readiness and one visible public model.
2. Standard OpenAI client non-stream Responses text through both services.
3. Standard OpenAI client typed SSE with completed provider usage.
4. One small inline synthetic image through the vision route.
5. Real Codex 0.149 global-yolo text/tool/governance invocation through Gateway:
   - disposable persistent CODEX_HOME/workspace/catalog at context 100000;
   - exact current Codex envelope preflight result;
   - ordinary `cat GOVERNANCE-DEPENDENCY.md` once;
   - Gateway admits exact adapter-managed declarations without hosted execution;
   - Gateway exact bytes/signature accepted by Local Coding;
   - Local Coding drops exact disabled search declarations before Qwen;
   - function/custom/local call/result preserved;
   - root/dependency observed/acquired/compiled/injected;
   - effective hidden binding under accepted CR/LF-only law.
6. Same Gateway key/session zero-root simulated history-reduction request proves
   signed same-identity rehydration with zero new compiler-model attempt.
7. Second Gateway key/owner and different session/repository sends zero-root and
   receives isolated miss/no first identity governance.
8. Invalid public key and over-quota request rejected before Local Coding.
9. Explicit `tool_choice` for dropped/hosted search rejected before provider and
   without reservation leak.

No full/crop Codex image rerun is required; Objective 004 already proved it.

## E. Exact identity and transport evidence

Retain only safe booleans/counts/hashes/versions proving:

- Gateway service Bearer, derivation secret, signing secret, public key, and Qwen
  credential roles remain distinct;
- exact body bytes signed by Gateway equal exact body bytes received/verified by
  Local Coding;
- HMAC canonical vector/version, timestamp window, nonce/replay acceptance;
- signed principal/session/repository/route are opaque and absent from logs,
  metrics, errors, cache filenames, ledger metadata, report, and Qwen request;
- same identity cache/rehydration hit; every changed identity dimension isolated;
- concurrent/exact replay rejected according to contract without duplicate
  provider/accounting effect;
- tool filter observed/removed counts and Qwen saw no `tool_search|web_search`;
- no explicit hosted execution authority granted.

Never report raw identities, signatures, nonce, canonical bytes, secrets,
prompts, source, tool output, images, model text, session IDs, or DB URL.

## F. Gateway accounting proof

For every public request, prove via Gateway repository/service APIs or bounded
read-only DB facts:

- one reservation and one terminal ledger outcome;
- successful rows finalized with provider-reported usage through Local Coding;
- no pending/duplicate request IDs;
- used/reserved request/token/cost counters internally consistent;
- Codex public request count equals added Gateway rows;
- Local Coding compiler calls add zero Gateway rows/reservations;
- invalid key, quota, explicit hosted choice, bad signature/replay route tests
  produce expected pre-provider/no-leak accounting behavior;
- no raw content/auth/identity enters ledger/audit metadata.

## G. Cleanup and rollback

On every result:

- stop/remove gateway/candidate/PostgreSQL;
- remove temp clone/venv/database/config/cache/Codex home/workspace/logs;
- remove newly pulled postgres image if absent before;
- prove no temp listeners/containers/images/volumes;
- Gateway and Local Coding Git worktrees clean, SHAs unchanged;
- protected vision PID/start/restart/listener/unit/launcher/profile state unchanged;
- text remains inactive; vision remains running; 18020 present; 18021/18031/temp
  ports absent;
- direct vLLM route remains and is not retired.

This is cross-repository acceptance and cutover rehearsal, not persistent/public
deployment.

## H. Repository support/docs/completeness

Reuse/harden existing repository-only drivers; no broad diagnostics or host cache
searches. Add hermetic tests and exact sanitized facts. Do not vendor Gateway.

On full pass update Objective-005 ledger/completeness to reflect cross-repo
acceptance, with persistent cutover/release limitations. Coding leaves arithmetic
for strategic review; strategy may raise Objective 005 to about 90% and weighted
branch readiness to about 97%.

## Verification

Run exact preflight, exactly one full cross-repo run, focused driver/vector/
identity/tool/privacy tests, full frozen Ruff/format/mypy/pytest/build/wheel/
compileall/shell/diff/secret/raw-log scans and current CI. Skipped/not-run is not
pass.

## Explicit non-goals

- No Gateway code/PR/report/OAP mutation or merge.
- No Local Coding merge in coding role.
- No persistent gateway/database/container/profile/service install.
- No direct-vLLM retirement, public TLS/bind, firewall/VPN/network change.
- No multi-worker/restart-persistent replay, overlapping secret rotation,
  production/certification/release claim.
- No host Codex session/history/cache access.

## Publication contract

Amend only Local Coding PR #7. Push all non-report work, record literal
implementation SHA, then publish exactly one immutable
`oap/reports/005-g-gateway-pr291-real-codex-cross-repo-acceptance.md` with
literal SHA and `Report publication commit: SELF`. SELF changes only report,
parent equals implementation SHA, and is remote head before FIFO `OK`.

# OAP Work Order — 005-p

## Objective

Amend Local Coding Objective-005 PR #7 from immutable 005-o FAILED report head
`c8b978c72c635ef2c80997c6b91f7ce2ccfdadb1`. Correct the repository-only
acceptance harness and evidence model so every remaining Objective-005 real
matrix and ephemeral-cutover criterion is executable, independently observed,
and machine-gated before another protected attempt.

This is a **no-protected-inference** harness-completeness round. Use actual
Codex 0.149.0, exact clean Gateway product code, actual Local candidate code,
synthetic PostgreSQL, and a strict fake Qwen to prove the complete chain and
failure gates. Do not contact protected Qwen beyond read-only unauthenticated
health/service/listener facts; do not retrieve its credential. Do not run or
simulate acceptance by report prose. Do not modify Gateway, Local production
semantics, Qwen, active Codex profiles, or create another PR.

The next protected continuation is not automatic: coding publishes one 005-p
report and returns to strategic review. Coding never merges.

## Exact continuation state

- Repository: `ulfe-lmi/slaif-local-coding`.
- Round: `005-p`; mode `AMEND_EXISTING_PR`; **NO NEW PR**.
- PR #7: `https://github.com/ulfe-lmi/slaif-local-coding/pull/7`.
- Base/head: `main` / `oap/005-gateway-ingress-integration`.
- Remote `main`: `570bd2b24ad4b041a07e0320d5ed44bc73e99ad5`.
- Required starting report head:
  `c8b978c72c635ef2c80997c6b91f7ce2ccfdadb1`.
- Required 005-o implementation parent:
  `ce8f333267effd514a3e9ce8b59262be2e766c08`.
- 005-o report path:
  `oap/reports/005-o-protected-credential-matrix-and-cutover-closure.md`.
- The report commit changes only that report, its first parent is the literal
  implementation SHA, and current report-head `test` is SUCCESS (run
  `34050064115`, job `101531942814`).
- PR #7 is OPEN, non-draft, MERGEABLE/CLEAN and is the only open Local PR.
- Exact clean Gateway executable authority remains implementation
  `9d247e7f3d8fd6a588976840c4657181b7486b81`, merged by
  `910ddaa23763883c07f5d2065662eb1157deb9f1`, report
  `e15008fd0f920aa81ccd5c0d425caf26f7f61b75`, app tree
  `bd536a282362cc549cc0c5518db8e743af667b63`, all ten checks SUCCESS.
- Local's three repository-only Gateway pins already equal `9d247e7f...` and
  must not move.

Abort and report if any exact GitHub/report/tree/check state differs. Commit
the exact activated 005-p order/selector unchanged and amend only PR #7.

## Protected-host baseline and prohibition

At activation on `hinton1`, `qwen-serving-vision.service` is active/running at
PID `23961`, start `Sun 2026-09-06 18:57:26 CEST`, zero restarts, model
`qwen3.8-27b`, context 100000, one sequence/image, port 18020. Text/batch Qwen
is inactive; ports 18021/18030/18031 are free; the Qwen checkout has seven
pre-existing uncommitted entries; active coding profile is
`oap-coding-luna-xhigh`.

This round permits only read-only unit state, listener, PID/start/restart, and
unauthenticated health checks. It prohibits reading any protected credential,
`/proc/<QwenPID>/environ`, protected models endpoint, prompt/inference/vision
traffic, or raw Qwen logs/config. Never stop/restart/switch/edit Qwen, port
18020, unit/config/model/checkpoint/venv/patches/launch/GPU flags, keys,
firewall/VPN/network, or active Codex profiles. Do not start a second model.
Preserve all seven Qwen worktree entries without inspecting raw contents.

## Strategic review correction of 005-o

Preserve immutable 005-o exactly, but record the following correction in the
005-p report and tests. The 005-o protected failure is real; its asserted
`gateway_stream_owned` product ownership is **not established**.

The exact current harness proves only that Gateway emitted a safe error event
after Local recorded upstream HTTP 2xx and zero Local failure-metric delta. It
does not prove that the provider's SSE semantics were valid or that Gateway
rejected a valid event. Specifically:

1. `local_terminal_bytes` is set from
   `local_status_class == "2xx" and local_failure_delta == 0`; it does not
   observe or validate a terminal provider lifecycle.
2. For protected mode `provider_call_count` is assigned from Gateway
   `ledger_delta`, so it is not independent provider-boundary evidence.
3. `_owner_for_failure()` maps a Gateway error to `gateway_stream_owned` from
   those proxies without a validated provider event/lifecycle or safe Gateway
   rejection code.
4. The report omitted already-available bounded `error_field_names`,
   `error_code_class`, and `error_type_class` evidence.

Correct the owner vocabulary and predicates so this historical result is
`gateway_rejected_stream_owner_unresolved`: Gateway emitted the error, but
product defect ownership remains unresolved between valid Gateway rejection
and incorrect Gateway validation. `gateway_product_defect` is permitted only
when the exact rejected provider event/lifecycle independently passes the
exact clean Gateway validator contract and the rejection code/stage conflicts
with it. `local_or_provider_owned`, `acceptance_harness_owned`, and successful
states likewise require independent evidence, not circular counters.

Add focused tests for every owner class, proxy/circular-evidence negative,
unknown/sanitized code behavior, and the exact 005-o bounded snapshot. Do not
rewrite 005-o, weaken Gateway validation, or claim the historical error fixed.

## A. Machine-derived harness gap inventory

Before implementation, encode a source/AST/collection-derived inventory that
must fail if these current gaps silently disappear or are misreported:

- the first protected gate uses a hand-built direct request with text
  `ordinary stream`; actual `run_codex_once()` occurs only after that gate;
- no real/fake full-chain Codex two-turn ID-less function continuation is
  executed by protected/fake `_run_direct_composed_rehearsal()` before success;
- fake mode leaves `codex_facts.status` as `NOT_RUN`;
- protected provider-call count is derived from `ledger_delta`;
- terminal-provider proof is derived from status/failure metrics, not parsed
  upstream terminal lifecycle;
- only one direct full-image request is sent; no later crop/history request is
  present;
- `second_owner_isolated` is returned as literal `True` without an observed
  negative sentinel/state predicate;
- `replay_tamper` is literal `NOT_RUN_NO_REQUEST_RELAY`;
- no complete body/query/path/route/signature/timestamp/nonce/replay matrix is
  executed by the composed runner;
- no exact installed-service/dedicated-profile/rollback implementation or
  dry-run obligation manifest exists;
- the runner can return `PASSED` without meeting the activated 005-n/005-o
  real-matrix and cutover acceptance set.

The 005-p report must reproduce the derived pre-fix inventory, corrected state,
and exact proving test node IDs. Report prose cannot satisfy an obligation.

## B. One permanent bounded acceptance orchestrator

Repair/consolidate the existing repository-only support; do not create a
second diagnostic architecture. The resulting orchestrator must have shared
fake/protected topology and predicate code so the later protected mode cannot
silently skip fake-qualified obligations. It remains outside the wheel and is
not product runtime.

Required properties:

1. A finite ordered manifest enumerates every Section C matrix criterion and
   Section D cutover/rollback criterion with a stable ID, phase, operation,
   expected independent observations, stop dependency, and safe evidence key.
2. The orchestrator emits only a fixed schema of enums/booleans/count classes,
   safe versions, synthetic fixture hashes, relationship classes, and bounded
   timing buckets. Unknowns become `other`; no arbitrary exception/string/raw
   payload escapes.
3. Fake and protected modes use the same exact manifest and assertions.
   Protected mode may add protected boundary observations but may not omit a
   fake-qualified criterion. `missing=[]` is required before protected traffic.
4. Every public request/turn has an explicit maximum and stable ordinal.
   Retry counts are zero. First failure prevents every later protected
   inference while cleanup still runs.
5. Provider-boundary call and lifecycle evidence is observed independently
   from Gateway reservation/ledger evidence. Never infer one from the other.
6. Actual Gateway product modules and compact permanent verifier/validator from
   detached exact `9d247e7f...` are executed/imported where applicable. Never
   copy/reimplement Gateway policy or import historical Objective-155 OAP
   machinery.
7. Actual Local candidate code and exact request pipeline are used. No relay,
   evidence endpoint, mock Local, or bypass may satisfy full-chain predicates.
8. Actual task-controlled Codex 0.149.0 is used in fake full-chain cases with
   checksum
   `bbc3341e44c9ead340ed9570c17be936e37870f570751a941699ffd04d672827`,
   private task home/workspace, global-yolo, no host history/cache/profile read.
9. A strict fake Qwen emits only reviewed permanent Responses lifecycles and
   separately records independent bounded inbound call/image/tool classes. It
   has deterministic function-call, assistant-message, compiler, image, and
   controlled-failure modes; malformed/unknown variants fail closed.
10. Temporary PostgreSQL and every process/listener/file/profile-like fixture
    are task-owned, bounded, and removed in `finally` paths.

Do not add raw stream/body recording, live qualification hooks, public/admin
features, product instrumentation, dependencies, or Gateway/Local production
behavior.

## C. Complete fake full-chain acceptance

Run the permanent orchestrator in fake mode and require all of these measured
outcomes before 005-p can be COMPLETE:

### C1. Real Codex two-turn natural tool lifecycle

- actual Codex -> actual Gateway -> actual Local -> strict fake Qwen;
- exactly two admitted public turns and one provider inference call per turn;
- first turn produces a reviewed natural function lifecycle, one ordinary local
  tool execution, and an adjacent matching result;
- second request naturally omits item ID while retains mandatory call ID;
- exact Gateway same-key call-ID-HMAC resolves ownership without fabricated ID,
  raw-ID persistence, scope downgrade, or hosted-tool authority;
- second turn produces reviewed assistant-message completion;
- valid visible-reasoning/null-encrypted/function/message lifecycle, normal
  close, terminal usage/output, Codex exit 0;
- exactly two reservations/ledgers terminal and zero pending/duplicates.

### C2. Governance, cache/rehydration, and isolation

- long synthetic root and exact delegated dependency are observed through the
  API boundary; one exact byte/hash/length-equal dependency acquisition occurs
  before substantive completion;
- deterministic candidates, compiler miss, validated cache/injection, hidden
  binding, and no raw tool markup are proved;
- same owner/key/session/repository zero-root/history-reduction turn rehydrates
  without an unnecessary compiler call;
- different session under same key, different owner/key, and different
  repository each execute observed negative sentinel/state predicates and do
  not inherit the first context. Literal booleans without source observations
  fail.

### C3. Full-image then crop/history

- actual Codex full-image turn followed by a later crop/history turn through
  Gateway and Local;
- fake Qwen independently records the complete upstream request image counts/
  hashes/classes and proves exactly the newest single image reaches each turn;
- Local observes the later outgoing history multiplicity/removal; governance
  remains effective; both turns terminate;
- content is discarded; report retains only synthetic fixture hashes/counts.

### C4. Identity, replay, tamper, authorization, failure, accounting

- signed identity is independently verified for every admitted Local request;
- same-session continuity and different session/key/owner/repository isolation;
- exact replay and concurrent replay accept at most one with no duplicate
  provider/accounting effect;
- body/query/path/route/signature/timestamp/nonce tamper plus ambiguous/missing
  identity reject before transform/provider;
- unauthorized/hosted/dropped-tool choice, invalid public key, and over-quota
  reject at correct pre-provider boundary without leaked reservation;
- controlled synthetic provider failure produces one normal terminal failure
  accounting outcome and no unrelated provider call;
- one reservation and finalized/released ledger outcome per admitted request,
  consistent usage/request/token/cost counters, zero pending/duplicate IDs;
- Local compiler calls create zero Gateway public rows/fees/fences/authority;
- cancellation/failure cleanup leaves no corrupt replay/cache/identity/provider
  state.

### C5. No-bypass, privacy, cleanup

- process/config/listener/connection facts prove Codex -> Gateway -> Local ->
  fake Qwen only; no direct or alternate route satisfies predicates;
- logs/metrics/errors/evidence/cache/DB contain none of the raw canaries,
  prompts, bodies, source, images, tool data, credentials, identities,
  signatures, nonces, endpoints, or arbitrary errors;
- all task services, DB/container, ports, private Codex home/workspace, cache,
  bytecode, and artifacts are removed;
- protected Qwen has received zero authenticated/model/inference calls in this
  round and retains its exact service/listener/worktree baseline.

## D. Cutover/rollback readiness without installation

Implement and unit/fake-test the exact later ephemeral cutover/rollback plan,
but do not install/start a candidate unit or edit any real Codex config in 005-p.

The machine manifest and tests must cover:

- capture of existence/hash/mode/owner/safe structure for exact allowlisted
  config/unit/env/cache/runtime/profile targets;
- private mode-0700 backup root and mode-0600 files;
- refusal on occupied 18030/18031, target collision, unsafe owner/mode/path,
  active-profile overlap, incomplete backup, or non-provable rollback;
- uniquely named Local 18031 and Gateway 18030 candidate specifications,
  protected env references, signed identity, private PostgreSQL, hardened unit,
  safe logging, restart/backoff, and no public/network/Qwen mutation;
- dedicated profile addition without active-profile/global-default changes;
- representative post-install checklist for tool/ID-less continuation,
  governance/reuse, full-image/crop, isolation, quota/accounting, and no bypass;
- exact reverse-order removal and restoration of bytes/mode/owner/hash/absence;
- post-rollback absence of candidate ports/processes/units/profile/cache/DB and
  unchanged Qwen/network/active profiles;
- injected failure at each installation/rollback phase proving complete exact
  cleanup or deterministic `rollback_incomplete` failure without deleting
  non-task state.

Use fake filesystem/service runners or dependency injection. Do not invoke
systemctl mutation, edit host config, or pretend this proves `CUTOVER ACCEPTED`.

## E. Tests, documentation, and acceptance

Required evidence:

- source-derived gap inventory tests;
- owner-classification and circular/proxy-evidence negatives;
- obligation-manifest enumeration, dependency order, request bounds,
  `missing=[]`, and missing/skip/failure fail-closed tests;
- full exact fake orchestrator including real Codex 0.149.0;
- focused affected unit/integration suites;
- full `uv run --frozen pytest -q`, Ruff check/format, mypy, compileall, shell
  syntax, build, wheel/sdist/package-boundary, diff, stale-pin, secret/raw-log,
  prohibited-hook/historical-dependency scans;
- current Local implementation/report-head required check SUCCESS;
- unchanged protected service PID/start/restarts/listeners, text inactive,
  ports 18021/18030/18031 free, seven Qwen worktree entries, and zero protected
  inference.

Update `TESTING.md` and the integration/runbook documentation only as needed to
state the permanent harness command, fake/protected boundary, obligation gate,
credential non-use in 005-p, and that 005-o ownership is unresolved rather than
a proved Gateway defect. Do not raise Objective-005 completeness or claim real
acceptance/cutover/release.

Lifecycle state in the report must be:

```text
IMPLEMENTED = yes only if the harness is complete
TESTED = exact fake/repository result
REAL-E2E ACCEPTED = no
CUTOVER ACCEPTED = no
MERGED = no
RELEASE-READY = no
```

## Security, resources, and local authority

Use only synthetic fixtures. Never emit/persist raw prompts, bodies, source,
images, model text/SSE, tool arguments/results, credentials, private endpoints,
config content, identities/signatures/nonces/canonical bytes, DB URLs/session
values, or arbitrary errors. Evidence is closed enums/booleans/count classes,
safe versions, synthetic hashes, relationship facts, and bounded timings.

Use official `postgres:16` with unique name, loopback random port, tmpfs,
`--rm`, finite readiness, no privileged/host network. `sudo` only for exact
Docker read/pull/run/stop/remove/inspect. No apt, daemon, Redis/Celery/email/
admin/TLS/public bind, persistent DB, protected credential, or model call.
Preserve Local `.venv` and unrelated state. Cleanup only exact task-owned
validated targets; never broad globs/shared roots.

Coding owns safe routine tools, dependencies, temporary services, commands,
tests, and evidence. Do not recruit human/strategy as terminal operator.

## Explicit non-goals

- No protected authenticated/model/inference/vision call; no real candidate
  installation/cutover; no Gateway, Qwen, Local production, dependency/lockfile,
  network, active-profile, public-deployment, or Objective-006 change.
- No new PR, coding merge/auto-merge, protocol relaxation, qualification hook,
  historical Objective-155 machinery, benchmark, or product feature.

## Publication contract

Amend only PR #7. Commit exact 005-p order/active plus intended repository-only
harness/tests/docs; push all non-report work; inspect/fix in-scope CI; record
literal implementation SHA. Then atomically publish exactly one immutable
`oap/reports/005-p-complete-acceptance-harness-and-correct-ownership.md` with:

```text
Implementation head SHA: <literal pre-report commit>
Report publication commit: SELF
```

SELF changes only that report, its first parent equals the implementation SHA,
and it is remote PR head before response FIFO `OK`. Report exact gap correction,
manifest, every fake criterion/test/check, no-protected proof, cleanup, lifecycle
labels, deviations, and strongest blocker with honest status. Coding never
merges and creates no PR.

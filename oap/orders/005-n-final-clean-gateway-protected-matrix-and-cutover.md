# OAP Work Order — 005-n

## Objective

Amend Local Coding Objective-005 PR #7 from immutable 005-m report head
`4d3ab2fd97d249710f952dd3d2c28936138cc8fa` and complete the deferred real
Codex/Gateway/Local/Qwen acceptance matrix against the final clean Gateway
Objective-160 implementation. This is Local integration acceptance, not
Gateway protocol discovery. Update only Local repository pins, permanent
integration harness/support, tests, evidence, and documentation required by
the result. Do not create another PR, modify Gateway, or mutate protected Qwen.

First prove the exact clean Gateway dependency and all repository/fake gates.
Then run one ordered protected matrix using the active one-image vision Qwen
fixture. Stop on its first protected product/accounting failure without retry
or cross-repository patching. Only if every protected criterion is green,
perform the already-authorized ephemeral candidate installation, dedicated
Codex-profile cutover acceptance, and exact rollback. Publish one immutable
005-n report and return to strategic review; coding never merges.

## Authoritative GitHub and dependency state

Local Coding:

- Repository: `ulfe-lmi/slaif-local-coding`.
- Round: `005-n`; mode `AMEND_EXISTING_PR`; **NO NEW PR**.
- PR #7: `https://github.com/ulfe-lmi/slaif-local-coding/pull/7`.
- Base/head: `main` / `oap/005-gateway-ingress-integration`.
- Remote `main`: `570bd2b24ad4b041a07e0320d5ed44bc73e99ad5`.
- Required starting 005-m report head:
  `4d3ab2fd97d249710f952dd3d2c28936138cc8fa`.
- Required 005-m implementation parent:
  `258ae2ebad39651076937b9f027e60831b8d2786`.
- At publication preflight PR #7 is OPEN, non-draft, MERGEABLE/CLEAN, its sole
  current required `test` check is SUCCESS, and it is the only open Local PR.

Clean Gateway dependency:

- Repository: `ulfe-lmi/slaif-api-gateway`; use a clean detached checkout, not
  an Objective-155/160 feature branch worktree.
- Exact non-report implementation head to execute and pin:
  `9d247e7f3d8fd6a588976840c4657181b7486b81`.
- Merged Gateway `main` containing it:
  `910ddaa23763883c07f5d2065662eb1157deb9f1`.
- Final immutable Objective-160 report head:
  `e15008fd0f920aa81ccd5c0d425caf26f7f61b75`.
- Final report path:
  `oap/reports/160-d-valid-local-service-fixture-and-final-fake.md`.
- The report head changes only that report, has first parent literal
  implementation head `9d247e7f...`, and records `RESULT=PASSED`.
- Exact Gateway `app/` tree:
  `bd536a282362cc549cc0c5518db8e743af667b63`.
- Accepted Objective-155 equivalence implementation authority:
  `acea2af4ca0f4586fc159c91607e1848f53f1107`; its `app/` tree is the same
  `bd536a...` tree.
- Gateway Objective-160 PR #297 is MERGED as `910ddaa...`. All ten required
  checks are SUCCESS on both `9d247e7f...` and `e15008fd...`: unit/lint/
  migration, JavaScript/TypeScript analysis, both Python analysis checks,
  PostgreSQL integration, OpenAI-compatible E2E, Playwright, Docker Compose,
  documentation hygiene, and CodeQL.
- The clean tree contains no `scripts/verify_local_coding_full_stack.py`, no
  `SLAIF_155X_`/Objective-155 qualification-writer production hook, and no app
  dependency on historical Objective-155 OAP artifacts. Permanent generic
  diagnostics and qualification modules remain product code and must not be
  misclassified as historical machinery.

Abort before protected traffic if the Local head changes, the detached Gateway
checkout is not exactly `9d247e7f...`, its reachability/tree/report topology
differs, any required check is non-successful, or rollback preconditions fail.
Do not substitute a branch tip, Gateway report commit, Objective-155 checkout,
or Gateway fake result for this dependency.

## Protected-host baseline and mutation boundary

The human explicitly switched the host to the pre-existing isolated vision
service before activation. At publication preflight:

- host `hinton1`;
- `qwen-serving-vision.service` active/running, PID `23961`, start timestamp
  `Sun 2026-09-06 18:57:26 CEST`, zero restarts;
- vLLM `0.27.1`, served model `qwen3.8-27b`, context `100000`, one sequence,
  `limit_mm_per_prompt={image:1}`, listener `0.0.0.0:18020`;
- authenticated model visibility and one bounded synthetic image request each
  returned HTTP 200 without credential or payload disclosure;
- text/batch `qwen-serving.service` inactive;
- ports 18021, 18030, and 18031 free;
- the Qwen checkout has seven pre-existing uncommitted entries owned outside
  this order; preserve them exactly and never inspect raw secret-bearing
  content, stage, edit, clean, reset, overwrite, or report it;
- the coding loop uses existing profile `oap-coding-luna-xhigh`; active OAP
  profiles are not pointed at candidate ports and must remain untouched.

Re-verify these facts and capture safe before/after identity facts. This order
allows bounded authenticated synthetic calls to the already-running vision
service. It does **not** authorize stopping/restarting/switching/editing Qwen,
port 18020, its unit/config/model/checkpoint/venv/patches/launch flags,
credential source, GPU settings, firewall/VPN/network binding, or active OAP
Codex profiles. Do not start a second model. Candidate Local and Gateway may
use only 127.0.0.1:18031 and 127.0.0.1:18030 respectively after their gates.

If the protected fixture becomes unavailable or differs materially, clean up
only task-owned state, report `BLOCKED|FAILED`, and stop. Do not repair or
switch Qwen in this round.

## Accepted evidence — do not repeat without contradiction

Accept exact-head evidence from Local 005-j through 005-m, Gateway Objective
155, and clean Objective 160:

- direct Local -> protected Qwen stages A–I byte/digest-equal terminal SSE;
- Gateway no-tool protected terminal stream and later Objective-155 two-turn
  protected function/message acceptance;
- Local fake full matrix covering tool filtering, image adaptation,
  constitution/compiler/cache/rehydration, isolation, quota/failure/accounting,
  privacy, and cleanup;
- actual Gateway -> Local -> protected Qwen readiness/model/non-stream success;
- exact official task-controlled Codex 0.149.0 binary/version and prior observed
  SHA-256 `bbc3341e44c9ead340ed9570c17be936e37870f570751a941699ffd04d672827`;
- accepted visible-reasoning, null-encrypted, pair-local strict stream,
  signed-identity grammar, HMAC rotation/no-downgrade, and ID-less tool-call
  replay semantics embodied by exact clean Gateway `app/` tree `bd536a...`;
- Objective-160 compact fake two-turn acceptance with two finalized accounting
  rows and no historical full-stack verifier dependency;
- Local 005-m safe ownership evidence showing its superseded 155-r
  tool-bearing stream failure was Gateway-validator-owned while Local/Qwen
  remained successful.

The Objective-160 run was fake and made no protected Local/Qwen call. It is not
the protected acceptance required below. Do not reopen accepted internals
absent new direct contradictory evidence from this exact clean pair.

## A. Exact-head and no-live repository preflight

Before inference or installation:

1. Verify Local HEAD and remote PR #7 are exactly `4d3ab2f...`, with the
   report-only topology above, exact OAP ancestry, unique open PR, expected
   base/head, and current required check success. After atomic activation, the
   only permitted pre-existing worktree differences are this exact order and
   the exact `005-n` active selector published by strategy.
2. Materialize a task-owned detached clean Gateway checkout at exactly
   `9d247e7f...`; prove reachability from merge `910ddaa...`, exact `app/` tree
   `bd536a...`, report `e15008fd...` topology/PASSED state, Objective-155 app
   equivalence, and absence of historical production hooks/full-stack verifier.
3. Update every Local repository-only Gateway pin/vector/driver constant used
   by acceptance from superseded `2527030f...` to implementation head
   `9d247e7f...`. Record merged main `910ddaa...`, report `e15008fd...`, app tree
   `bd536a...`, and equivalence authority `acea2af4...` as separate typed facts;
   reject moving branch state and unreported commits.
4. Import and exercise actual Gateway product modules and its compact permanent
   verifier from the detached checkout where useful. Never vendor/copy/
   reimplement Gateway policy, client, validator, identity, provider, routing,
   quota, replay, or accounting logic; never import historical Objective-155
   orders/reports/scripts as runtime or acceptance dependencies.
5. Verify the task-controlled Codex binary is exactly 0.149.0 with the expected
   checksum and global-yolo invocation. Use a driver-owned private Codex home
   and workspace; never read host Codex session/history/cache or alter the
   current coding/strategic profiles.
6. Prove the real matrix is one fixed ordered run with per-request bounds,
   zero automatic retry after product/accounting failure, stop-at-first-failure,
   and complete `finally` cleanup.
7. Prove direct topology: Codex -> Gateway -> Local -> protected Qwen. No
   diagnostic/evidence relay or alternate provider may satisfy acceptance.
8. Run all focused/full repository, fake, stream, identity, replay, tool,
   image, constitution, accounting, privacy, package, lint/type/compile gates
   before protected traffic.

No protected inference is allowed until A is fully green.

## B. Required fake and repository gates

Against exact Gateway `9d247e7f...`, execute and prove:

- Local full frozen unit suite, focused integration suites, Ruff check and
  format, mypy, compileall, build, wheel/sdist and package-boundary checks;
- exact Gateway <-> Local signed-identity, route/capability, tool-filter,
  provider, provenance, stale-version/digest/pair, and body-signing vectors;
- complete fake Gateway -> Local -> fake-Qwen composition using permanent
  visible-reasoning, null-encrypted, function/tool, and assistant-message SSE
  lifecycles;
- natural two-turn function continuation whose later item is ID-less and whose
  mandatory call ID is resolved only through Gateway same-key call-ID-HMAC
  ownership; cover function and supported custom-tool behavior;
- exact replay/concurrent replay, body/query/path/route/signature/timestamp/
  nonce tamper, ambiguous/missing identity, distinct session/key/repository
  isolation, invalid public key, quota, explicit hosted/dropped-tool choice,
  provider failure, cancellation, accounting finalization/release, and zero
  pending/duplicate state;
- Local compiler calls create no Gateway public reservation/ledger row or
  hosted-search authority/fence/fee;
- root/dependency observation, deterministic acquisition, compiler miss,
  validated cache/injection, same-session zero-root rehydration without an
  unnecessary compiler call, image newest-only adaptation, and identity
  isolation;
- logs/metrics/errors/artifacts contain no raw content, credential, identity,
  signature, nonce, private endpoint, or unsafe arbitrary value;
- complete fake resource cleanup and unchanged protected fixture facts.

Fake/Qwen stubs, repository tests, Gateway Objective-160 evidence, and earlier
protected evidence do not substitute for B's exact-pair regression gates or C.

## C. One complete real protected acceptance matrix

Run exactly one disposable ordered matrix using real task-controlled Codex
0.149.0, real clean Gateway `9d247e7f...`, the current Local PR candidate,
temporary PostgreSQL 16, and unchanged active vision Qwen:

```text
real Codex 0.149.0 global-yolo
  -> real Gateway 9d247e7f... on private loopback
       temporary PostgreSQL 16, synthetic users/keys/routes/pricing
  -> real Local Coding candidate on 127.0.0.1:18031
       signed identity v1 and exact tool/image/constitution policies
  -> unchanged qwen-serving-vision.service on 18020
  -> valid terminal responses back through Local/Gateway to Codex
```

Use synthetic fixtures and sequential calls. Stop at the first product or
accounting failure; collect only predeclared safe facts; clean up; do not retry,
change prompts/limits, patch another repository, or issue a direct provider
control after failure.

### C1. Readiness, visibility, ordinary text, and tool stream

- Require Local/Gateway readiness, authenticated model visibility, ordinary
  non-streaming success, and one real Codex two-turn tool-bearing stream.
- The tool stream declares exact function/custom tools plus reviewed adapter-
  managed search candidates. Gateway signs/routes it; Local strips only
  `tool_search`/`web_search`; ordinary function/custom/call/result items remain.
- Require process exit 0; `2xx` SSE; recognized ordered visible-reasoning,
  function, and assistant-message lifecycles; one created and valid completed
  event per admitted turn; valid output/usage; normal close; zero Gateway typed
  error/rejection and zero Gateway-induced Local disconnect.
- Prove natural ID-less continuation retains mandatory call ID and Gateway
  resolves ownership through the same-key call-ID-HMAC contract without
  fabricating item IDs or downgrading scope.
- Require one Gateway->Local and one Local->Qwen inference call per public
  model turn, with safe nonempty header/first-byte/terminal/close timing buckets.

### C2. Governed tools, cache reuse, and isolation

- Use a disposable repository with long synthetic `AGENTS.md`, exact delegated
  `GOVERNANCE-DEPENDENCY.md`, distinctive hidden binding, and ordinary local
  shell/function tool work.
- Prove exact dependency byte/hash/length equality locally and one acquisition
  before substantive completion; root/dependency observation; deterministic
  candidates; compiler miss; validated compile/cache/injection; binding
  effectiveness; terminal Codex success; no raw tool markup.
- A second same-principal/key/session/repository zero-root/history-reduction
  request must rehydrate with zero unnecessary compiler-model attempts.
- A distinct Codex session under the same Gateway key, a second Gateway owner/
  key, and a distinct repository scope must not receive the first context.

### C3. Real Codex vision path

- Through the same Gateway/Local chain run the accepted bounded synthetic
  full-image then later crop/history interaction.
- Require Local to observe history multiplicity and active one-image Qwen to
  receive exactly the newest supported image, with successful terminal model
  response and governance still effective.
- Verify image count/modality structurally. Do not benchmark quality or retain/
  report image or model content.

### C4. Replay, tamper, authorization, failure, and accounting

- Exact and concurrent replay accept at most one; duplicates produce no
  duplicate provider or accounting effect.
- Body/query/path/route/signature/timestamp/nonce tamper, ambiguous/missing
  signed context, unauthorized/hosted/dropped-tool choice, invalid key, and
  over-quota requests reject at the correct pre-provider boundary.
- Gateway service bearer and exact HMAC-bound request identity are verified for
  every admitted Local request; public/internal credentials, identity material,
  signatures, and nonces never reach Qwen or retained evidence.
- One controlled synthetic provider failure must follow normal terminal
  accounting without contacting protected Qwen. Do not deliberately fail or
  mutate Qwen.
- Every admitted public request has exactly one reservation and terminal
  finalized or released ledger result. Provider-reported usage and request/
  token/cost counters are consistent; no pending/duplicate request ID remains.
- Local compiler calls create zero public Gateway rows. Failure/cancellation
  leaves no corrupt accounting, replay, cache, identity, or provider state.

### C5. No-bypass and cleanup

- Codex configuration connects only to Gateway; Gateway's Local route connects
  only to Local; Local connects only to protected Qwen. No Codex direct-Local/
  Qwen, Gateway direct-Qwen, evidence relay, or alternate route may satisfy a
  predicate.
- Use process/listener/connection and exact config-relationship facts without
  exposing endpoint values, credentials, or config content.
- Remove the disposable topology completely and prove the pre-existing vision
  Qwen listener/service is the only remaining relevant model state, with the
  same PID/start/restart/unit/config/model/listener facts and all seven
  pre-existing Qwen worktree entries preserved.

Only complete C may be labeled `REAL-E2E ACCEPTED`.

## D. Controlled candidate installation, dedicated-profile cutover, rollback

Run D only after every C criterion is green. The human has already authorized
this ephemeral Local/Gateway/dedicated-Codex-profile acceptance and exact
rollback. It does not authorize persistent production deployment, active OAP
profile mutation, public binding, or any Qwen change.

### D1. Backup and refuse-unsafe preconditions

- Capture content hashes, modes, owners, existence, and safe structural facts
  for the real Codex config/profile file and any pre-existing target Local/
  Gateway unit/config/environment/cache/runtime state.
- Copy exact restorable state into one task-owned mode-0700 root with files
  mode 0600; never print or commit content/path.
- Refuse installation if ports 18030/18031 are occupied, target units conflict,
  exact rollback is not proven, or active OAP profiles cannot be preserved.

### D2. Install candidate chain

- Install/run exact tested Local as a uniquely named hardened user service on
  127.0.0.1:18031 with protected env reference, signed identity, fresh private
  bounded cache, restart/backoff, safe journal logging, and current config.
- Install/run exact Gateway `9d247e7f...` on 127.0.0.1:18030 with private
  temporary PostgreSQL and exact Local route to 18031. No public bind/TLS/
  firewall/network change.
- Add one dedicated real Codex acceptance profile pointing only to Gateway
  18030. Do not edit/remove active OAP profiles or set a new global default.
- Verify health/readiness, model visibility, permissions/unit sandbox, signed
  route, and exact chain before Codex traffic.

### D3. Post-installation representative acceptance

Using only the dedicated profile run real Codex 0.149.0 checks for:

1. terminal text/tool stream and natural ID-less function continuation;
2. delegated governance plus same-session reuse;
3. bounded full-image/crop history transformation;
4. distinct-session/key isolation;
5. safe quota/accounting terminal behavior.

Require the same identity/tool/image/privacy/accounting boundaries as C and
prove profile -> Gateway -> Local -> Qwen only.

### D4. Exact rollback

- Stop/disable/remove only candidate Gateway/Local units/processes, temporary
  PostgreSQL, candidate configs/env/cache/runtime/log artifacts, and dedicated
  Codex profile.
- Restore exact pre-installation Codex bytes/mode/owner/hash, or prior absence.
- Verify ports 18030/18031/temp are absent; no task container/process/unit/
  profile/cache remains; firewall/VPN/network and active OAP profiles are
  unchanged; vision Qwen has identical PID/start/restart/listener/config facts;
  text service remains inactive; original profiles remain structurally valid.
- Perform read-only health/model checks only; no post-rollback inference.

Only complete D1–D4 may be labeled `CUTOVER ACCEPTED`.

## E. Stop law and ownership

If any protected C/D case fails:

- stop immediately, clean only task-owned state, and retain the first bounded
  failure/ownership snapshot;
- change Local only for a direct Local defect, rerun no-model/fake/local tests,
  and return to strategy without another protected attempt;
- do not change Gateway, PR #291, merged Gateway main, or Qwen automatically;
- if exact clean Gateway violates its accepted contract, publish the smallest
  safe reproducible Gateway handoff without accommodating it in Local;
- if Qwen contradicts accepted behavior, preserve it unchanged and report the
  external blocker;
- if harness/installation/rollback owns the issue, repair only task support in
  fake/no-model tests and report; do not repeat protected traffic this round.

No partial later case may be counted as pass. Do not manufacture terminal
events, relax stream/identity/tool/accounting validation, or broaden scope to
finish.

## F. Privacy, resources, documentation, and CI

Never commit, print, report, log, metric-label, or persist raw prompts, bodies,
source, images, model text, SSE, tool schemas/arguments/results, credentials,
credential paths, private endpoints, real config content, identities,
signatures, nonces, canonical bytes, DB URLs, session values, or arbitrary
errors. Evidence is fixed states/enums, booleans, counts, safe versions,
synthetic-fixture hashes, config relationship classes, and bounded timings.

Use official `postgres:16` with unique names, loopback-only ports, tmpfs,
`--rm`, finite readiness, and no privileged/host networking. `sudo` is limited
to exact Docker read/pull/run/stop/remove/inspect needed by this disposable
test. No apt, Docker-daemon change, Redis/Celery/email/admin/TLS/public bind, or
persistent production database. Preserve unrelated ignored Local `.venv`.
Destructive cleanup targets only exact validated task-owned resources; no broad
globs, shared roots, host cache, or unrelated state.

Coding owns routine safe repo-local setup, exact dependency/tool installation,
temporary services, command execution, and evidence collection. Do not recruit
the human or strategic agent as a terminal operator or log courier.

Run focused and full frozen Ruff/format/mypy/pytest/build/wheel/sdist/compileall/
shell/diff/secret/raw-log/package-boundary gates and current Local CI. Missing,
skipped, not-run, pending, cancelled, or unavailable required evidence is not
pass.

Only on complete C+D pass update `docs/SLAIF-GATEWAY-INTEGRATION.md`,
`TESTING.md`, `docs/OAP-RUNBOOK.md`, adapter configuration/installation docs,
and Objective-005 criterion/completeness ledgers with exact clean Gateway and
protected/cutover/rollback evidence. Claims must distinguish:

```text
IMPLEMENTED
TESTED
REAL-E2E ACCEPTED
CUTOVER ACCEPTED
MERGED
RELEASE-READY
```

Coding may set the first four only from evidence and must state `MERGED=no` and
`RELEASE-READY=no`. A successful round stops for strategic review. Gateway is
already merged; after full acceptance, strategy alone may merge Local PR #7
and verify remote Local `main`. Persistent deployment and Objective 006 remain
separate future authority.

## Explicit non-goals

- No new Local objective/PR; no Gateway/PR #291/Gateway-main change; no Qwen
  mutation; no coding merge/auto-merge; no persistent/public deployment;
  no TLS/firewall/VPN/network or active OAP-profile change.
- No new protocol-discovery/qualification system, historical Objective-155
  full-stack machinery, direct Local/provider diagnostic, alternate protected
  stream, benchmark/model-quality work, or speculative product improvement.
- No Objective 006 implementation or release/readiness claim.

## Publication contract

Amend only Local PR #7. Commit the exact activated 005-n order and `oap/active`
bytes unchanged with intended support/tests/docs; push all non-report work to
the same branch; inspect/fix in-scope CI; record the literal 40-hex
implementation head. Then atomically publish exactly one immutable
`oap/reports/005-n-remaining-real-matrix-and-cutover-after-tool-stream.md` with:

```text
Implementation head SHA: <literal pre-report commit>
Report publication commit: SELF
```

The SELF commit must change only that report, its first parent must equal the
literal implementation SHA, and it must be remote PR head before exact response
FIFO `OK`. Report every required command/case/check and lifecycle label with
honest `PASSED|FAILED|SKIPPED|NOT RUN|BLOCKED|PENDING|MISSING` status, exact safe
protected before/after facts, cleanup, deviations, and strongest blocker.
Coding never merges and creates no new PR.

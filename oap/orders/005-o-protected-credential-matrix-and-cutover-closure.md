# OAP Work Order — 005-o

## Objective

Amend Local Coding Objective-005 PR #7 from immutable 005-n report head
`7845d93c8e643f08f65931c533ad65af83662a49`. Resolve only the recoverable
protected-credential delivery blocker identified in 005-n, execute the complete
deferred real Codex -> clean Gateway -> Local -> protected vision-Qwen matrix,
and, only if the matrix is fully green, perform the already-authorized
ephemeral candidate installation, dedicated-profile cutover acceptance, and
exact rollback.

Do not repeat accepted Gateway protocol discovery or exhaustive Local/fake
qualification. Do not create a new PR, modify Gateway, mutate Qwen, alter active
OAP profiles, or merge. Stop at the first protected product/accounting failure,
publish bounded ownership evidence, and return to strategy without retry.

## Exact continuation state

Local Coding:

- Repository `ulfe-lmi/slaif-local-coding`; round `005-o`;
  `AMEND_EXISTING_PR`; **NO NEW PR**.
- PR #7: `https://github.com/ulfe-lmi/slaif-local-coding/pull/7`.
- Base/head: `main` / `oap/005-gateway-ingress-integration`.
- Remote `main`: `570bd2b24ad4b041a07e0320d5ed44bc73e99ad5`.
- Required starting report head:
  `7845d93c8e643f08f65931c533ad65af83662a49`.
- Required literal 005-n implementation parent:
  `3e072a4ec57947fe7ee003bfcffd404d5363768d`.
- 005-n report path:
  `oap/reports/005-n-remaining-real-matrix-and-cutover-after-tool-stream.md`.
- The starting report commit changes only that report, its first parent is the
  literal implementation head, and current report-head `test` is SUCCESS (run
  `34049184663`, job `101529592597`).
- PR #7 is OPEN, non-draft, MERGEABLE/CLEAN and remains the only open Local PR.

Exact clean Gateway authority remains:

- implementation `9d247e7f3d8fd6a588976840c4657181b7486b81`;
- merged main `910ddaa23763883c07f5d2065662eb1157deb9f1`;
- report `e15008fd0f920aa81ccd5c0d425caf26f7f61b75`, report-only with parent
  `9d247e7f...` and `RESULT=PASSED`;
- `app/` tree `bd536a282362cc549cc0c5518db8e743af667b63`;
- Objective-155 equivalence authority
  `acea2af4ca0f4586fc159c91607e1848f53f1107`, with the same app tree;
- all ten required Gateway implementation/report checks SUCCESS;
- no historical Objective-155 production qualification hook or
  `scripts/verify_local_coding_full_stack.py` dependency.

Local 005-n already pins all three repository-only constants to `9d247e7f...`.
Do not repin, use a branch, use a report commit as executable code, or change
Gateway. Abort before protected traffic if any exact state differs.

## Protected vision baseline and credential authority

At activation on `hinton1`:

- `qwen-serving-vision.service` is active/running at PID `23961`, start
  `Sun 2026-09-06 18:57:26 CEST`, zero restarts;
- vLLM `0.27.1`, model `qwen3.8-27b`, context 100000, one sequence,
  one-image limit, listener on port 18020;
- text/batch `qwen-serving.service` inactive;
- ports 18021, 18030, and 18031 free;
- protected health HTTP 200 and authenticated `/v1/models` HTTP 200;
- the Qwen checkout has seven pre-existing uncommitted entries, unchanged;
- coding profile `oap-coding-luna-xhigh` and all active OAP profiles remain
  outside the candidate ports.

The authenticated credential exists as exactly one nonempty `VLLM_API_KEY`
entry in the verified active service MainPID's protected process environment.
This is the explicit authorized credential reference for this round. Coding
may:

1. obtain the current MainPID only from
   `systemctl --user show qwen-serving-vision.service -p MainPID --value`;
2. require it equals the unchanged protected baseline and the unit is active
   with zero restarts;
3. read only the exact `VLLM_API_KEY` entry from `/proc/<MainPID>/environ` into
   process memory;
4. require exactly one nonempty entry without recording its length/hash/value;
5. pass it only as the task-local harness variable `QWEN3090_API_KEY` or direct
   in-memory authorization header to bounded protected calls; and
6. unset it from the controlling shell immediately after task cleanup.

Never print, echo, trace, hash, serialize, copy, write, commit, report, log,
metric-label, or retain the credential or any other process-environment value.
Do not source the Qwen unit environment file: it includes launcher argument
continuations and is not the credential source. Do not inspect unrelated
process environment entries. Disable shell tracing around credential handling.
No credential may enter command-line arguments, evidence, subprocess output,
Codex configuration, cache identity, Gateway ledger/audit metadata, or Qwen
model input.

This order permits bounded authenticated synthetic calls to the existing
vision service. It does not permit stopping/restarting/switching/editing Qwen,
port 18020, units, configs, model/checkpoint/venv/patches/launch/GPU flags,
credential source, firewall/VPN/network binding, or active OAP profiles. Do not
start a second model. If the protected baseline changes, clean up task-owned
state, report `BLOCKED|FAILED`, and stop.

## Accepted 005-n evidence — do not repeat

Accept the exact remote 005-n evidence unless direct contradiction appears:

- clean Gateway reachability/report/app-tree/equivalence/hook-absence proof;
- exact task-controlled Codex 0.149.0 version/checksum/global-yolo preflight;
- Local full frozen suite: 578 passed, 8 skipped;
- focused Local suite: 486 passed, 1 skipped;
- Ruff check/format, mypy, compileall, shell syntax, build, wheel/sdist,
  package-boundary, diff, stale-pin, and raw-log scans;
- exact Gateway product/verifier test subset, tool-policy differential, and
  provider-adapter differential;
- complete exact-head fake Gateway -> Local -> fake-Qwen composition covering
  visible reasoning/null handling, terminal stream, natural tool continuation,
  image policy, constitution/compiler/cache/rehydration, signed identity,
  replay/tamper/isolation/quota/failure/accounting/privacy, and cleanup;
- remote Local implementation/report-head `test` SUCCESS;
- unchanged protected Qwen facts and complete cleanup.

Do not rerun these exhaustive gates merely to consume time or protected calls.
Before real traffic run only focused no-model checks for any new/changed 005-o
harness/support plus fast stale-pin, syntax, diff, privacy, and exact-state
guards. If code changes after a gate, rerun every affected focused/fake gate.
Gateway Objective-160 fake acceptance and Local 005-n fake success remain
necessary but do not substitute for the real matrix below.

## A. Exact preflight and fixed run contract

Before protected inference:

1. Verify Local remote/checkout/report/check topology and the exact Gateway
   authority above. After activation, only this exact order and `005-o` active
   selector may pre-exist as intentional worktree differences.
2. Use a task-owned detached clean Gateway checkout at exactly `9d247e7f...`;
   execute actual product modules and compact permanent verifier only. Never
   import/copy historical Objective-155 OAP machinery.
3. Verify task-controlled Codex 0.149.0 and expected SHA-256
   `bbc3341e44c9ead340ed9570c17be936e37870f570751a941699ffd04d672827`.
   Use a private task-owned Codex home/workspace and global-yolo invocation;
   never access host Codex history/cache or alter existing profiles.
4. Verify one fixed ordered matrix, sequential protected calls, explicit call
   bounds, zero automatic retry after failure, no alternate prompt/limit, no
   direct-provider diagnostic after failure, and complete `finally` cleanup.
5. Verify topology is Codex -> Gateway -> Local -> protected Qwen only. No
   evidence relay, fake, alternate provider, direct Codex-to-Local/Qwen, or
   Gateway-to-Qwen path may satisfy an acceptance predicate.
6. Acquire the credential only by the authorized in-memory contract above;
   prove authenticated model visibility without emitting secret material.
7. Complete focused tests/privacy gates and push any necessary support changes
   before the first inference. No protected inference occurs on uncommitted or
   unpushed acceptance code.

## B. One complete protected matrix

Run one disposable matrix using real Codex 0.149.0, exact clean Gateway
`9d247e7f...`, the current pushed Local candidate on 127.0.0.1:18031,
temporary PostgreSQL 16, and unchanged protected vision Qwen on 18020.

### B1. Readiness, ordinary request, and natural two-turn tool stream

- Require Local/Gateway health/readiness and authenticated model visibility.
- Require ordinary non-streaming terminal success.
- Run real Codex through Gateway with exact function/custom declarations and
  reviewed adapter-managed search candidates. Local must strip only
  `tool_search`/`web_search` before Qwen and preserve ordinary function/custom/
  call/result items.
- Require two `2xx` terminal SSE turns, process exit 0, ordered valid visible-
  reasoning/function/message lifecycles, created/completed events, output and
  usage, normal close, zero Gateway typed error/rejection, and zero Gateway-
  induced Local disconnect.
- The natural continuation must omit the item ID while preserve the mandatory
  call ID; Gateway must resolve ownership using same-key call-ID-HMAC without
  fabricated IDs or scope downgrade.
- Require exactly one Gateway->Local and one Local->Qwen inference call per
  public turn and safe nonempty timing buckets.

### B2. Governance, rehydration, and isolation

- Use a disposable repository with long synthetic `AGENTS.md`, exact delegated
  `GOVERNANCE-DEPENDENCY.md`, distinctive hidden binding, and ordinary local
  shell/function-tool work.
- Prove exact dependency byte/hash/length equality locally, one acquisition
  before substantive completion, root/dependency observation, deterministic
  candidates, compiler miss, validated cache/injection, effective binding,
  terminal success, and no raw tool markup.
- A second same-owner/key/session/repository zero-root/history-reduction turn
  must rehydrate with zero unnecessary compiler-model attempts.
- A distinct session under the same Gateway key, a second owner/key, and a
  distinct repository scope must not receive the first governance state.

### B3. Vision

- Run the accepted bounded synthetic full-image then later crop/history flow
  through the same real Codex/Gateway/Local chain.
- Prove Local observes history multiplicity and Qwen receives exactly the
  newest single image, terminal response succeeds, and governance remains
  effective.
- Retain only structural image count/modality facts. Do not retain content or
  claim visual quality/generic support.

### B4. Replay, tamper, authorization, failure, accounting

- Exact and concurrent replay accept at most one; duplicates create no
  duplicate provider/accounting effect.
- Body/query/path/route/signature/timestamp/nonce tamper, ambiguous/missing
  context, unauthorized/hosted/dropped-tool choice, invalid public key, and
  over-quota requests reject at the correct pre-provider boundary.
- Signed identity is verified on every admitted Local request. Public/internal
  credentials, identities, signatures, and nonces do not reach Qwen or retained
  evidence.
- One controlled **synthetic provider** failure follows normal terminal
  accounting without contacting Qwen. Do not deliberately fail Qwen.
- Every admitted request has one reservation and terminal finalized/released
  ledger outcome; usage and request/token/cost counters are consistent; zero
  pending/duplicate request IDs remain. Local compiler calls create zero public
  Gateway rows or hosted-search fee/fence/authority.
- Failure/cancellation leaves no corrupt accounting, replay, cache, identity,
  or provider state.

### B5. No-bypass and cleanup

- Prove each exact config/process/listener/connection relationship in the
  Codex -> Gateway -> Local -> Qwen chain without disclosing endpoints/config.
- Stop and remove the disposable topology and every task resource. Require only
  the pre-existing vision listener/service remains, with identical PID/start/
  restart/unit/model/config facts; text remains inactive; ports 18021/18030/
  18031 and temp ports are absent; all seven pre-existing Qwen worktree entries
  remain; active profiles/network/firewall/VPN are unchanged.

Only complete B may be `REAL-E2E ACCEPTED`. At the first failure, stop all later
B/D cases, perform cleanup, classify ownership from predeclared bounded facts,
and do not retry.

## C. Ephemeral candidate cutover and rollback — only after B green

This is the already-authorized Local/Gateway/dedicated-profile acceptance from
005-n. It is not persistent deployment or Qwen cutover.

1. Capture hash/mode/owner/existence/safe structure of real Codex config and
   any target Local/Gateway service/config/env/cache/runtime state. Make one
   task-owned private exact backup; never render content/path. Refuse if ports
   18030/18031 are occupied, target conflict exists, active profiles cannot be
   preserved, or exact rollback is not proven.
2. Run exact tested Local as a uniquely named hardened user service on
   127.0.0.1:18031 with protected env reference, signed identity, fresh bounded
   cache, restart/backoff, and safe logs.
3. Run exact Gateway `9d247e7f...` on 127.0.0.1:18030 with private temporary
   PostgreSQL and exact Local route. No public bind/TLS/firewall/network change.
4. Add one dedicated task acceptance profile pointing only to Gateway 18030;
   never edit/remove active OAP profiles or change the global default.
5. Through only that profile run representative real Codex checks: terminal
   natural tool stream/ID-less continuation, delegated governance and reuse,
   one full-image/crop flow, distinct session/key isolation, and safe quota/
   accounting terminal behavior. Require the same B identity/tool/image/
   privacy/accounting/no-bypass boundaries.
6. Stop/disable/remove candidate units/processes/PostgreSQL/config/env/cache/
   runtime/log/profile state; restore exact prior Codex bytes/mode/owner/hash or
   absence. Verify candidate/temp ports and all task resources absent, active
   profiles and network state unchanged, and vision Qwen identical.
7. Perform read-only health/model checks only after rollback; no rollback
   inference.

Only complete C may be `CUTOVER ACCEPTED`.

## D. Stop law and scope

If B or C fails:

- change Local only for a directly proved Local defect, run affected no-model/
  fake tests, and return without another protected attempt;
- do not change Gateway, PR #291/#297, merged Gateway main, or Qwen;
- if clean Gateway contradicts its accepted contract, publish the smallest safe
  handoff; do not accommodate it in Local;
- if Qwen contradicts accepted behavior, preserve it and report the external
  blocker;
- if harness/install/rollback owns the issue, repair only task support under
  no-model/fake tests and report; no protected retry this round.

Do not relax stream/identity/replay/tool/accounting validation, manufacture
events, count partial later cases, or broaden product scope to finish.

## E. Security, resources, documentation, and checks

Use only synthetic fixtures. Never retain or emit raw prompts, bodies, source,
images, model/reasoning text, SSE, tool schemas/arguments/results, credentials,
credential paths, private endpoints, config content, identities, signatures,
nonces, canonical bytes, DB URLs, session values, or arbitrary errors. Evidence
is fixed states/enums, booleans, counts, safe versions, fixture hashes, config
relationship classes, and bounded timing buckets.

Use official `postgres:16` with unique name, loopback-only random port, tmpfs,
`--rm`, finite readiness, no privileged/host network. `sudo` is limited to
exact Docker read/pull/run/stop/remove/inspect. No apt, daemon, Redis/Celery,
email/admin/TLS/public bind, persistent DB, or second model. Preserve unrelated
Local `.venv`, Qwen changes, and all non-task state. Cleanup uses only exact
validated task-owned targets, never broad globs/shared roots.

Coding owns safe routine tooling, temporary services, command execution, and
evidence collection; do not recruit human/strategy as terminal operators.
Run focused tests for changed support plus frozen Ruff/format/mypy/pytest/build/
package/compile/shell/diff/secret/raw-log gates proportionate to changes and
current Local CI. Required skipped/not-run/pending/missing evidence is not pass.

Only on complete B+C pass update integration/testing/runbook/configuration/
installation and Objective-005 criterion/completeness ledgers with exact heads,
protected evidence, cutover, rollback, and limitations. Distinguish exactly:

```text
IMPLEMENTED
TESTED
REAL-E2E ACCEPTED
CUTOVER ACCEPTED
MERGED
RELEASE-READY
```

Coding may set only the first four from evidence and must state `MERGED=no` and
`RELEASE-READY=no`. Gateway is already merged; strategy alone may review/merge
Local PR #7 after full acceptance. Persistent deployment and Objective 006 are
separate.

## Explicit non-goals

- No new Local PR/objective, Gateway/PR #291/#297/main change, Qwen mutation,
  active-profile change, coding merge/auto-merge, persistent/public deployment,
  TLS/firewall/VPN/network change, or Objective 006 work.
- No repeat protocol discovery, historical Objective-155 machinery, direct
  provider diagnostic, alternate protected attempt, benchmark/model-quality
  work, or speculative feature/refactor/dependency change.

## Publication contract

Amend only PR #7. Commit this exact order and `oap/active` unchanged with any
necessary bounded Local support/docs; push all non-report work; inspect/fix
in-scope CI; record literal implementation SHA. Atomically publish exactly one
immutable
`oap/reports/005-o-protected-credential-matrix-and-cutover-closure.md` with:

```text
Implementation head SHA: <literal pre-report commit>
Report publication commit: SELF
```

SELF changes only that report, first parent equals the literal implementation
SHA, and is remote PR head before exact response FIFO `OK`. Report every B/C
case, check, lifecycle label, protected before/after fact, credential-handling
confirmation, cleanup, deviation, and strongest blocker using exact
`PASSED|FAILED|SKIPPED|NOT RUN|BLOCKED|PENDING|MISSING`. Do not expose secrets.
Coding never merges and creates no PR.

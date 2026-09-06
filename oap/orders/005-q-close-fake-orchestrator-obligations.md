# OAP Work Order — 005-q

## Objective

Amend Local Coding Objective-005 PR #7 from immutable 005-p PARTIAL report head
`45616045f7cc5ae06753516ff23853b11a7b0066`. Complete and genuinely execute
the repository-only fake acceptance orchestrator introduced in 005-p. Fix the
independently identified fake function-stream recursion, wire every fake-mode
C1–C5/D obligation to concrete runtime observations, and make the exact real
Codex 0.149.0 -> clean Gateway -> actual Local -> strict fake-Qwen chain pass
with `missing=[]`, no non-pass result, and `passed=true`.

This remains a **no-protected-credential/no-protected-inference** round. Do not
contact authenticated/model/inference/vision routes on protected Qwen. Do not
modify Gateway, Local production behavior, Qwen, active Codex profiles, or
dependencies. Do not create a new PR or merge. Publish one immutable 005-q
report and return to strategy; only strategy may decide whether the harness is
safe for a later single protected attempt.

## Exact continuation state

- Repository `ulfe-lmi/slaif-local-coding`; round `005-q`;
  `AMEND_EXISTING_PR`; **NO NEW PR**.
- PR #7: `https://github.com/ulfe-lmi/slaif-local-coding/pull/7`.
- Base/head: `main` / `oap/005-gateway-ingress-integration`.
- Remote `main`: `570bd2b24ad4b041a07e0320d5ed44bc73e99ad5`.
- Required starting report head:
  `45616045f7cc5ae06753516ff23853b11a7b0066`.
- Required 005-p implementation parent:
  `2b0b4dc1caa5c1a8f2b6e6130f04a5f403e71712`.
- 005-p report path:
  `oap/reports/005-p-complete-acceptance-harness-and-correct-ownership.md`.
- The starting commit changes only that report, its first parent equals the
  literal implementation SHA, and current report-head `test` is SUCCESS (run
  `34052354553`, job `101538108997`).
- PR #7 is OPEN, non-draft, MERGEABLE/CLEAN and remains the only open Local PR.
- Gateway executable authority remains exact clean implementation
  `9d247e7f3d8fd6a588976840c4657181b7486b81`, merged main
  `910ddaa23763883c07f5d2065662eb1157deb9f1`, report
  `e15008fd0f920aa81ccd5c0d425caf26f7f61b75`, app tree
  `bd536a282362cc549cc0c5518db8e743af667b63`, ten checks SUCCESS.
- All three Local Gateway pins remain `9d247e7f...`.

Abort and report on any exact-state discrepancy. Commit the exact 005-q order
and active selector unchanged and amend only PR #7.

## Protected-host prohibition

At activation on `hinton1`, vision Qwen remains active/running at PID `23961`,
start `Sun 2026-09-06 18:57:26 CEST`, zero restarts, model `qwen3.8-27b`,
context 100000, one sequence/image, port 18020. Text Qwen is inactive; ports
18021/18030/18031 are free; the Qwen checkout has seven pre-existing entries;
coding profile is `oap-coding-luna-xhigh`.

Permit only read-only service/PID/start/restart/listener and unauthenticated
health facts. Never read `/proc/<QwenPID>/environ` or any credential; never
call protected models/inference/vision routes; never read raw protected logs/
config. Do not stop/restart/switch/edit Qwen, units, ports, model/checkpoint/
venv/patches/launch/GPU flags, keys, network/firewall/VPN, or active profiles.
Do not start another model. Preserve the seven Qwen entries without inspecting
their raw contents.

## Independently verified defects and evidence gaps

Preserve immutable 005-p. Correct these exact gaps:

1. `scripts/gateway_accounting_rehearsal.py` currently defines
   `_FakeQwenHandler._write_events()` as an unconditional call to itself. The
   first function lifecycle therefore recurses instead of emitting SSE, the
   fake provider request dies, and actual Codex exits at C1.1. Fix the write
   path using bounded reviewed SSE framing/flush behavior; do not bypass the
   actual Gateway/Local stream or switch to a message-only response.
2. Add a direct HTTP/fake-provider regression that exercises the function
   lifecycle through `_function_stream()` and would fail on recursion,
   disconnect, malformed framing, missing terminal output/usage, excess event,
   or unbounded response.
3. `_acceptance_gate()` currently initializes every manifest ID to `NOT RUN`
   and promotes only a small subset from `codex`, `vision`, provider, privacy,
   cleanup, and cutover facts. It has no observation wiring for many required
   C1 accounting/call-ID facts, C2 compile/rehydration/isolation facts, C3 Local
   history facts, C4 identity/replay/tamper/authorization/failure/accounting
   facts, or C5 topology facts.
4. `test_obligation_gate_requires_complete_observed_passes` manufactures one
   `PASSED` result per manifest entry. It tests gate mechanics only; it does not
   prove the orchestrator can observe any obligation. Retain the mechanics test
   but add runtime-projection completeness tests.
5. `StrictFakeQwenObservation`'s two manually recorded unit payloads and the
   injectable fake cutover runner are component tests, not substitutes for an
   actual full-chain orchestrator result.
6. `missing=[]` means only that result records exist. It must never be reported
   as completion when any status is `NOT RUN|SKIPPED|BLOCKED|FAILED|MISSING`,
   any observation is false, any relationship is not the required independent
   relationship, or `passed=false`.

Do not weaken, remove, reorder, or relabel manifest obligations to make the
gate green. Do not classify 005-o as a Gateway product defect; its corrected
state remains `gateway_rejected_stream_owner_unresolved`.

## A. Repair the strict fake stream

Implement and test an exact bounded fake Responses stream writer that:

- emits each event once with `event:` and `data:` framing and a blank delimiter;
- uses deterministic sequence numbers and reviewed permanent Gateway-valid
  visible-reasoning/function/message/terminal usage shapes;
- exposes a natural first function lifecycle with syntactically valid
  non-Codex-prefixed item ID and mandatory call ID;
- accepts the actual second Codex request with omitted item ID and matching call
  ID/result, then emits one terminal assistant-message lifecycle;
- records independent provider inbound call ordinal, request class, tool class,
  function/result adjacency, item-ID presence class, call-ID relation class,
  image count/hash class, compiler/inference class, lifecycle validity, normal
  close, and terminality without retaining raw values;
- has hard event/body/byte/call/time bounds and deterministic failure cleanup;
- fails closed for recursion, disconnect, duplicate/reordered/orphan/mismatched/
  malformed/unknown/overflow lifecycle variants.

Add tests that invoke the handler through an actual loopback HTTP client/server,
not only direct method mocks. Prove the regression would fail against the exact
005-p implementation.

## B. Wire every obligation to runtime evidence

For every manifest item selected by fake mode:

1. identify the exact runtime producer and independent observation fields;
2. calculate its pass only from those fields, never from a literal success,
   report prose, another subsystem's counter, or the obligation ID itself;
3. enforce its declared `stop_dependency` and request budget;
4. emit exactly one bounded result with correct observed/relationship/count/
   timing/version/hash facts; and
5. leave it non-pass when any expected observation is missing.

Add a machine-generated projection table containing obligation ID, source
observation keys, producer function/class, proving test node IDs, and execution
status. A meta-test must prove:

- every fake-selected manifest ID has explicit projection code and at least one
  positive plus one negative test;
- no projection is satisfied by default initialization, `make_result(...
  PASSED...)` loops without observation predicates, `True` constants, or
  fabricated snapshots;
- every source observation exists in the final full-chain result schema;
- result ordering equals manifest ordering, with no duplicate/extra/missing ID;
- `missing=[]` plus all observed independent `PASSED` results is necessary for
  `passed=true`;
- any individual obligation failure stops dependent protected work and makes
  the overall gate false while cleanup/privacy obligations still execute.

At minimum runtime wiring must cover:

- C1 exact two Codex turns, independent fake-provider calls, function/result,
  ID-less mandatory-call-ID HMAC ownership, validated lifecycle, two terminal
  accounting rows and zero pending/duplicate;
- C2 exact root/dependency acquisition, candidates/compiler/cache/injection,
  same-session zero-root rehydration, and independently observed negative
  session/owner/repository isolation;
- C3 actual full-image then later crop/history through Codex/Gateway/Local,
  provider one-image hash/count observations, Local history seen/removed facts,
  terminal governance on both turns;
- C4 identity on every admission, exact/concurrent replay, all seven tamper
  dimensions, invalid key/hosted/dropped/over-quota gates, controlled fake
  provider failure, per-request accounting/counters, compiler zero-public-row,
  and failure cleanup;
- C5 exact no-bypass relationships, privacy scans, and task cleanup;
- D fake cutover/rollback planning, refusal, profile isolation, reverse restore,
  absence, and injected failure cleanup.

## C. Complete exact fake full-chain execution

After focused tests pass, run exactly one final fake acceptance with:

```text
task-controlled real Codex 0.149.0
  -> actual clean Gateway 9d247e7f...
       -> actual Local PR candidate on 127.0.0.1:18031
            -> strict fake Qwen on task-owned random loopback
```

Use the expected Codex SHA-256
`bbc3341e44c9ead340ed9570c17be936e37870f570751a941699ffd04d672827`,
private task home/workspace, global-yolo, zero retries, synthetic PostgreSQL,
and the unchanged finite request budget. Run all C1–C5 operations in manifest
order and the fake D readiness/failure-injection suite. Require:

- actual Codex exit 0 and exact two-turn natural function continuation;
- all real Gateway/Local/fake-provider/accounting/governance/vision/isolation/
  replay/tamper/failure/privacy/no-bypass/cleanup predicates listed in 005-p;
- `missing=[]`, `first_failure=null`, `retry_count=0`, every selected result
  observed with required relationship and `PASSED`, and `passed=true`;
- no report-only/manual evidence used as a predicate;
- no protected credential read or protected authenticated/model/inference call;
- full removal of PostgreSQL, Gateway, Local, fake Qwen, private Codex state,
  caches, ports, processes, files, and logs.

If C fails, retain only the first safe fixed diagnostic class and exact failed
obligation, fix only the fake/harness defect, rerun affected focused tests, and
perform at most one final full fake acceptance after the fix. Never authorize
protected traffic in this round.

## D. Verification and documentation

Required evidence:

- recursion regression and strict function/message stream positive/negative
  HTTP tests;
- projection-table completeness and anti-fabrication tests;
- every manifest obligation positive/negative test and dependency/budget gate;
- exact full fake chain result satisfying all C requirements;
- full `uv run --frozen pytest -q`, focused affected suites, Ruff check/format,
  mypy, compileall, shell syntax, build, wheel/sdist/package boundary, diff,
  stale-pin, secret/raw-log, prohibited-hook/historical-dependency scans;
- current implementation/report-head Local `test` SUCCESS;
- read-only protected before/after identity: same PID/start/restarts/listener,
  text inactive, ports 18021/18030/18031 free, seven Qwen entries, zero
  credential/model/inference access.

Update `TESTING.md` and integration docs only as needed to replace partial
005-p harness claims with exact executable command/schema/limits and fake
result. Preserve limitations: 005-o ownership unresolved; fake is not protected
acceptance; cutover is not accepted; Objective-005 completeness does not rise.

Lifecycle report state:

```text
IMPLEMENTED = yes only if harness/projection complete
TESTED = yes only if exact full fake gate passed
REAL-E2E ACCEPTED = no
CUTOVER ACCEPTED = no
MERGED = no
RELEASE-READY = no
```

## Security, resources, and local authority

Use synthetic fixtures only. Never emit/persist raw prompts, bodies, source,
images, model/SSE text, tool arguments/results, credentials, endpoints, config,
identities/signatures/nonces/canonical bytes, DB URLs/session values, or
arbitrary errors. Evidence stays within fixed enums/booleans/count classes,
safe versions, synthetic hashes, relationships, and timing buckets.

Use official `postgres:16`, unique name, loopback random port, tmpfs, `--rm`,
finite readiness, no privileged/host network. `sudo` only for exact Docker
read/pull/run/stop/remove/inspect. No apt, daemon, Redis/Celery/email/admin/TLS/
public bind, persistent DB, protected credential/model call, or second model.
Preserve Local `.venv`, Qwen entries, and unrelated state. Cleanup exact
task-owned validated targets only, never broad globs/shared roots.

Coding owns safe routine setup/tools/services/tests/evidence; do not recruit
human/strategy as terminal operators.

## Explicit non-goals

- No protected credential/authenticated/model/inference/vision access; no real
  cutover; no Gateway/Qwen/Local-production/dependency/lockfile/network/active-
  profile/public-deployment/Objective-006 change.
- No new PR, coding merge/auto-merge, protocol relaxation, qualification hook,
  historical Objective-155 machinery, benchmark, or product feature.

## Publication contract

Amend only PR #7. Commit exact 005-q order/active with intended repository-only
harness/tests/docs; push all non-report work; fix in-scope CI; record literal
implementation SHA. Atomically publish exactly one immutable
`oap/reports/005-q-close-fake-orchestrator-obligations.md` with:

```text
Implementation head SHA: <literal pre-report commit>
Report publication commit: SELF
```

SELF changes only that report, first parent equals implementation SHA, and is
remote PR head before response FIFO `OK`. Report exact defect correction,
projection table summary, every fake obligation/result, tests/checks, no-live
proof, cleanup, lifecycle labels, deviations, and strongest blocker with honest
status. Coding never merges and creates no PR.

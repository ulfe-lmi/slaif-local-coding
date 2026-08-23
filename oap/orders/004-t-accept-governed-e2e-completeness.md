# OAP Work Order — 004-t

## Objective

Amend objective-004 PR #6 only to record strategic acceptance of the verified
004-s two-invocation global-yolo governed E2E and correct completeness from
objective 004 `15%` / branch `~74%` to objective 004 `40%` / branch `~79%`.
This is documentation/transcript only; change no runtime, helper, test semantics,
dependency, live service, or prior OAP artifact.

## GitHub objective state

- Repository: `ulfe-lmi/slaif-local-coding`
- Numeric objective / round: `004` / `004-t`
- PR mode: `AMEND_EXISTING_PR`
- Existing PR: #6, `https://github.com/ulfe-lmi/slaif-local-coding/pull/6`
- Required base: `main` at `7a2c36a0a40958a6059a765c2f9d5e5bf4ddc161`
- Required head: `oap/004-real-codex-governed-e2e`
- Current verified remote head / `004-s` SELF:
  `e548a56acf366d002000425caa75c7ad2dac8765`
- Prior implementation SHA:
  `7f7b4df04bfa30dce4c45adfb4c255c660af82ad`, verified sole parent of SELF.
- PR state: OPEN/non-draft/MERGEABLE-CLEAN; final report-head `test` SUCCESS.
- Required action: **NO NEW PR**; no coding merge/auto-merge.

## Strategically accepted evidence

Independent review verified:

- report SELF changes only the immutable 004-s report and its parent is the
  literal implementation SHA;
- both Codex-under-test invocations used global
  `--dangerously-bypass-approvals-and-sandbox` before `exec`, with no sandbox,
  permission-profile, or approval flag;
- both completed one successful intended dependency read with zero failures;
- observed dependency bytes/SHA-256/length exactly matched the fixture;
- effective root/dependency observation, acquisition, compilation, and stable
  injection occurred;
- both hidden dependency-derived sentinels passed;
- first invocation recorded dependency cache miss and two compiler-model
  attempts; second recorded cache hit and zero additional compiler-model
  attempts;
- exactly two governed invocations ran, candidate 18031 passed health/readiness
  and stopped afterward, protected 18020/Qwen/Codex state remained unchanged,
  raw/secret leakage checks passed, and current report-head CI is SUCCESS.

## Bounded scope

In `oap/COMPLETENESS.md` only, plus exact activated order/active transcript:

1. Change current authoritative recovery-branch readiness from `~74%` to
   `~79%`.
2. Change objective 004 completeness from `15%` to `40%`.
3. State the accepted 004-s global-yolo two-invocation evidence concisely:
   exact dependency contents, observation/acquisition/compilation/injection,
   hidden sentinel twice, persistent cache reuse, and no unnecessary second
   compiler-model attempt.
4. Preserve explicit remaining gaps: forced/equivalent compaction,
   vision-capable E2E, broader security/observability hardening, and systemd
   candidate proof.
5. Preserve all non-goals and honest limitations: no production, multi-user,
   gateway, cutover, generic sandbox, or vision readiness claim.

## Explicit non-goals

No runtime/helper/test/dependency/config change; no model, adapter, compiler,
cache, sandbox, bubblewrap, vision, or protected-service call; no host/profile/
system mutation; no rewrite of earlier orders/reports.

## Acceptance criteria

1. Completeness arithmetic and evidence text are exactly 40% objective 004 and
   ~79% branch readiness.
2. Remaining gaps and release limitations remain explicit.
3. Implementation commit changes only `oap/COMPLETENESS.md`, exact order, and
   `oap/active`.
4. Required local gates and implementation/report-head GitHub CI pass.

## Required verification

Record lock check, frozen sync, Ruff check/format, mypy, full pytest, build,
compileall, shell syntax, diff check, scoped diff, secret/raw scan, and current
GitHub checks. Live/model/service calls are NOT RUN (not required;
documentation-only). Wait for final report-head CI.

## Publication contract

Push amendments to exact PR #6 branch; never create another PR or merge. Record
literal implementation head after all non-report work is remote. Atomically
publish exactly one immutable
`oap/reports/004-t-accept-governed-e2e-completeness.md`; SELF must be the sole
final commit, its first parent must equal the implementation head, it must change
only that report, and it must be remote PR head before response FIFO `OK`.

# OAP Work Order — 004-z

## Objective

Amend objective-004 PR #6 only to correct the proven external compaction-runner
metrics accessor (`roots` → existing `root_observations`) and rerun the same
mandatory global-yolo Codex-through-Local-Coding governed seed, bounded native
compaction resumes, and post-compaction rehydration acceptance. No environment,
sandbox, catalog, systemd, or product diagnostic expansion.

## GitHub objective state

- Repository: `ulfe-lmi/slaif-local-coding`
- Numeric objective / round: `004` / `004-z`
- PR mode: `AMEND_EXISTING_PR`
- Existing PR: #6, `https://github.com/ulfe-lmi/slaif-local-coding/pull/6`
- Required base: `main` at `7a2c36a0a40958a6059a765c2f9d5e5bf4ddc161`
- Required head: `oap/004-real-codex-governed-e2e`
- Current verified remote head / `004-y` SELF:
  `eb2f2c7954feb2d0422557c6884fc98f20143b71`
- Prior implementation SHA:
  `d122422a334dd2a1d6785452412e22c29913696c`, verified sole parent of SELF.
- PR state: OPEN/non-draft/MERGEABLE-CLEAN; final report-head `test` SUCCESS.
- Required action: **NO NEW PR**; no coding merge/auto-merge.

## Proven state and exact correction

004-y's corrected context-window-only fixture and global-yolo persistent seed
passed through candidate 18031: Codex 0.149.0 exited 0, emitted JSONL events,
completed one exact delegated dependency read, and passed the hidden sentinel.
The external runner then failed before resume 1 because it accessed
`ConstitutionMetricsSnapshot.roots`, while the existing typed field is
`root_observations`.

Correct that accessor only in the private bounded execution driver. If a durable
repo-test helper/script contains the typo, fix that one reference and add one
focused assertion; otherwise make no repository helper/test change. Do not add
fields, dataclasses, wrappers, fallbacks, diagnostics, or alternate triggers.

## Mandatory rerun

Reuse exactly the accepted 004-y setup:

- Codex-under-test 0.149.0 with global
  `--dangerously-bypass-approvals-and-sandbox` before `exec`;
- persistent non-ephemeral disposable CODEX_HOME;
- corrected 24,000 context-window-only catalog with no unsupported explicit
  auto-compaction field;
- one candidate adapter on loopback 18031, fresh private cache, static opaque
  identity, protected upstream 18020;
- one long synthetic governance fixture and hidden dependency sentinel.

Run:

1. one governed seed; stop immediately if seed fails;
2. at most four same-session Codex-native resume turns with bounded synthetic
   filler, stopping when explicit compaction or native reduced-history/root-
   absent request is proven;
3. exactly one post-compaction verification turn.

Require seed exact dependency/observation/acquisition/compiler/injection/
sentinel and populated rehydration. Require compaction proof without inspecting
opaque content. Require same identity, root absent, valid rehydration hit and
injection, hidden sentinel, and zero additional compiler-model attempts on the
post-compaction request.

No hosted compaction, manual history edit, handwritten zero-root, fresh-session
substitution, workspace/bubblewrap/sandbox work, retry after a failed seed,
alternate catalog/prompt, or product change before direct evidence.

## Failure and completion rules

- If Codex-native compaction is not observable within four successful resume
  turns, report the bounded external limitation; objective 004 remains open.
- If compaction is proven and rehydration/injection/sentinel fails, report the
  first genuine Local Coding defect. Do not implement it in this round.
- Candidate 18031 and all temporary fixture/session/cache/config state must be
  removed; protected Qwen/Codex state must remain unchanged. Treat the previously
  observed unrelated `zapit-strategic-sol` profile hash as concurrent external
  state: do not read raw content, mutate, restore, or attribute it to coding;
  separately prove the OAP/Qwen profiles placed in scope are unchanged.

## Acceptance criteria

1. The sole metrics accessor defect is corrected without scope growth.
2. Mandatory global-yolo governed seed passes and emits complete sanitized
   metrics.
3. Actual same-session Codex compaction/reduced history is proven within bounds.
4. Root-absent post-compaction request rehydrates/injects immediately, preserves
   hidden sentinel, and adds zero compiler-model attempts.
5. Privacy, cleanup, protected in-scope host state, exact local gates, and final
   implementation/report-head CI pass.
6. No product change occurs unless a direct product defect is first observed
   (and any such defect is report-only this round).

## Completeness

Objective 004 is currently 80% / branch ~87%. On full compaction/rehydration
success, coding leaves percentages unchanged pending strategic review; strategy
may raise objective 004 to 90% / branch ~89%. Vision-capable E2E remains the
planned external gap. Do not close objective 004 on a negative result.

## Publication contract

Push amendments to exact PR #6 branch; never create another PR or merge. Record
literal implementation head after all non-report work is remote. Atomically
publish exactly one immutable
`oap/reports/004-z-fix-compaction-metrics-accessor.md`; SELF must be the sole
final commit, its first parent must equal the implementation head, it must change
only that report, and it must be remote PR head before response FIFO `OK`.

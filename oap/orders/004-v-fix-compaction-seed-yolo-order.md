# OAP Work Order — 004-v

## Objective

Amend objective-004 PR #6 only to correct the proven global-yolo argv ordering
in the persistent Codex compaction seed, then rerun the exact bounded 004-u
Codex-native compaction/rehydration acceptance sequence. Do not add helper or
product code unless a direct post-compaction Local Coding defect is reached.

## GitHub objective state

- Repository: `ulfe-lmi/slaif-local-coding`
- Numeric objective / round: `004` / `004-v`
- PR mode: `AMEND_EXISTING_PR`
- Existing PR: #6, `https://github.com/ulfe-lmi/slaif-local-coding/pull/6`
- Required base: `main` at `7a2c36a0a40958a6059a765c2f9d5e5bf4ddc161`
- Required head: `oap/004-real-codex-governed-e2e`
- Current verified remote head / `004-u` SELF:
  `e40f86a0a94ebad270abb08604cbf03653ed4355`
- Prior implementation SHA:
  `940c2345e2f20d08a25059ced24d5ec04a1ae1b3`, verified sole parent of SELF.
- PR state: OPEN/non-draft/MERGEABLE-CLEAN; final report-head `test` SUCCESS.
- Required action: **NO NEW PR**; no coding merge/auto-merge.

## Proven harness defect

004-u's seed used the invalid shape:

```text
codex exec --dangerously-bypass-approvals-and-sandbox ...
```

The global flag must precede `exec`, as already proven by accepted 004-s:

```text
codex --dangerously-bypass-approvals-and-sandbox exec ...
```

The failed seed emitted zero events/requests, so the four resume attempts had no
session and are not compaction evidence. This is a harness argv defect, not a
Codex fixture limitation or Local Coding result.

Read-only installed help confirms `codex exec resume` accepts its own
`--dangerously-bypass-approvals-and-sandbox` option. Preserve a supported resume
shape and record normalized seed/resume argv hashes. No alternate flag search.

## Bounded rerun

Reuse the 004-u disposable 24,000-context/16,000-auto-compaction catalog,
persistent private CODEX_HOME, synthetic long governance fixture, candidate
adapter 18031, fresh private cache, static opaque identity, bounded synthetic
history, sanitized event/request facts, and cleanup.

1. Run one corrected global-yolo persistent seed. Stop immediately if it fails;
   record bounded startup/event/request facts and run zero resumes.
2. Require seed exact dependency bytes, observation/acquisition, compilation,
   injection, hidden sentinel, and populated rehydration entry.
3. Run at most four supported same-session resume turns to trigger Codex-native
   compaction; stop as soon as an explicit compaction state/event or Codex-native
   reduced-history request is proven.
4. Run exactly one post-compaction verification turn. Require same identity,
   prior root absent, valid rehydration/injection, hidden sentinel, and zero
   additional compiler-model attempts.

Do not use hosted compaction, raw opaque content, manual rollout/history edits,
handwritten zero-root requests, fresh-session substitution, sandbox diagnostics,
or additional retries. Candidate 18031 is loopback-only and must stop afterward;
protected 18020/Qwen/Codex state remains unchanged.

## Scope and claims

- Expected repository implementation change: exact order/active, outcome docs
  only. No helper/test/product code change is expected.
- If corrected seed succeeds but actual compaction cannot be observed within
  four turns, report the external bounded limitation without product change.
- If actual compaction is proven and rehydration fails, report the first direct
  Local Coding gate without speculative fix.
- Keep objective 004 at 40% / branch ~79% on failure. On full compaction/
  rehydration success, coding leaves percentages unchanged pending strategic
  acceptance; strategy may raise them to 60% / ~83%.

## Acceptance criteria

1. Seed argv places global yolo before `exec`; no seed startup ordering failure.
2. Seed reproduces accepted governed dependency/compiler/injection/sentinel and
   populates rehydration.
3. Codex-native compaction or reduced history is proven within the bounded
   same-session turn budget without inspecting opaque content.
4. Root-absent post-compaction request rehydrates/injects immediately, preserves
   sentinel, and adds zero compiler-model attempts.
5. Privacy, identity/version isolation, child/candidate cleanup, protected-host
   invariants, exact local gates, and final CI pass.
6. No product/helper change occurs before direct product evidence.

## Required verification

Record all exact 004-u verification categories plus corrected seed/resume argv
templates/hashes, seed event/request facts, per-turn compaction evidence, post-
compaction rehydration/compiler/sentinel metrics, strict turn budget, and proof
no resume ran after a failed seed. Wait for report-head CI.

## Publication contract

Push amendments to exact PR #6 branch; never create another PR or merge. Record
literal implementation head after all non-report work is remote. Atomically
publish exactly one immutable
`oap/reports/004-v-fix-compaction-seed-yolo-order.md`; SELF must be the sole
final commit, its first parent must equal the implementation head, it must change
only that report, and it must be remote PR head before response FIFO `OK`.

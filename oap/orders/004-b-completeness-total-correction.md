# OAP Work Order — 004-b

## Objective

Amend objective-004 PR #6 only to correct the completeness arithmetic and
baseline wording made stale by this PR. This is documentation-only; change no
runtime behavior, test semantics, dependency, protected host state, or prior OAP
artifact.

## GitHub objective state

- Repository: `ulfe-lmi/slaif-local-coding`
- Numeric objective / round: `004` / `004-b`
- PR mode: `AMEND_EXISTING_PR`
- Existing PR: #6, `https://github.com/ulfe-lmi/slaif-local-coding/pull/6`
- Required base: `main` at `7a2c36a0a40958a6059a765c2f9d5e5bf4ddc161`
- Required head: `oap/004-real-codex-governed-e2e`
- Current verified remote head / `004-a` SELF:
  `d498563c711b323886a029fba71fc6b540a52798`
- Prior implementation heads: `fcd23b50533ef00e8651f1e177b042445de01cf8`, then
  `3363a50c4ffa830e2aa48e942d76b5297e3d7ba9`; the latter is verified sole parent
  of report SELF.
- PR state: OPEN, non-draft, MERGEABLE/CLEAN; implementation/report-head CI all
  SUCCESS.
- Required action: **NO NEW PR**; no coding merge/auto-merge.

## Verified gap

`oap/COMPLETENESS.md` correctly raises objective 004 from 15% to 35% and its
header says branch readiness ~78%, but the table’s weighted total still says
~74%. The evidence row also says “current merged main readiness before recovery
merge,” which describes the pre-003 main rather than PR #6’s actual base.

## Bounded scope

In `oap/COMPLETENESS.md` only:

1. Change the weighted total from approximately 74% to approximately **78%**,
   consistent with objective weights/completions after this PR.
2. Replace stale baseline wording with a clear statement that PR #6’s base main
   (including accepted objective 003) is approximately 74%, while this branch is
   approximately 78%.
3. Preserve every other assessment value, limitation, and historical statement.
4. Make no unrelated edits or runtime changes.

## Acceptance criteria

1. Weighted table arithmetic matches ~78% on this branch.
2. Base/branch readiness wording accurately describes PR #6’s actual base.
3. Implementation commit changes only `oap/COMPLETENESS.md` plus exact activated
   order/active transcript.
4. Local quality gates and current implementation/report-head GitHub CI pass.

## Required verification

Run exact statuses for lock/frozen sync/Ruff/check/format/mypy/full pytest/build/
compileall/shell syntax and `git diff --check`. No live model calls are required;
label them `NOT RUN (not required; documentation-only)`. Include scoped diff and
secret audits. Wait for final report-head CI; missing/pending/failed checks block.

## Publication contract

Push to exact PR #6 branch; never create another PR or merge. Record literal
implementation head after non-report work is remote. Atomically publish exactly
one immutable `oap/reports/004-b-completeness-total-correction.md`; SELF must be
sole final commit, parent equals implementation head, change only that report,
and be remote PR head before response FIFO `OK`.

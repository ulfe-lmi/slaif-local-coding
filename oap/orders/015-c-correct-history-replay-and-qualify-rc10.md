# OAP ORDER 015-c — Correct the historical regression replay and qualify private RC10

## Objective and PR state

Continue numeric Objective 015 in the existing PR #22. **AMEND_EXISTING_PR**
only; **NO NEW PR**.

Objective 015-b repaired the live read-only registry baseline and produced a
fully qualified private RC9, but strategic review rejects RC9 as the final
handoff candidate. The mandatory regression does not demonstrate its claimed
historical failure mode: replaying the focused coverage test against the
015-a frozen source fails inside its fallback parser before it compares the
archived aliases. Because that test is one of the 131 frozen source inputs,
the correction cannot be made behind RC9 while retaining RC9's source and
provenance binding. Preserve RC9 immutably, correct the regression narrowly,
and produce the collision-safe successor `0.1.0-rc10`.

## Exact independently verified state

- Repository: `ulfe-lmi/slaif-local-coding`.
- Objective/round: `015` / `015-c`.
- PR mode: `AMEND_EXISTING_PR`; existing PR #22:
  https://github.com/ulfe-lmi/slaif-local-coding/pull/22
- Base: `main` at `87ed2cea43a0a8706efe485b9b625dfda7cf75aa`.
- Required branch:
  `oap/015-upstream-diagnostics-compiler-truncation-rc8`.
- Current remote head/report SELF:
  `3b1f417f0584859d42ec8781b7f9507ceb19f0d1`.
- SELF parent/final 015-b implementation head:
  `231fa6e67a3240dbcc986b27fd7b62cf1c479245`.
- The report commit changes only
  `oap/reports/015-b-close-immutable-history-gap-and-qualify-rc9.md` and
  has that exact parent. PR #22 is the sole open PR and remains non-draft.
- Current report-head CodeQL is green; report-head CI was still running at
  strategic reconciliation and is superseded by this source correction.
- Pre-existing untracked paths `Local`, `clean`, and `unchanged` remain outside
  the PR and must not be changed, deleted, or committed.

RC9 immutable identity:

- source `S9`:
  `7f601bf153ef86a567883c0008edf4ce34e79c95`;
- digest `D9`:
  `sha256:54fe19483f00ef6e209b2796786fe27cddd302c6bcf5322821b2192a32884334`;
- aliases: `0.1.0-rc9` and
  `sha-7f601bf153ef86a567883c0008edf4ce34e79c95`;
- wheel `W9`:
  `eb241dda2e079b29190868108c488edaf98261c84119bfd405070dea98b546b9`;
- publication workflow run 36960763079 succeeded;
- final implementation-head CI run 36961356033 and CodeQL run 36961353714
  succeeded, including the actual pulled `D9` qualification;
- genuine Codex 0.149.0 ledger 007 passed VISION/CACHE/BOTH/DIRECT with
  CACHE/BOTH treatment delivery and protected-state preservation.

These are historical RC9 facts. They do not cure the frozen regression defect
below and do not authorize altering RC9.

## Exact strategic review finding

The 015-b order required a deterministic regression that fails against the
015-a frozen source specifically because the archived RC7 aliases are absent
from its read-only workflow baseline.

The current fallback parser in
`tests/test_registry_history_baseline.py::_inline_static_tags` locates a source
slice beginning with `tags = (` and passes the whole assignment to
`ast.literal_eval`. `literal_eval` accepts an expression, not an assignment.
Independent clean replay of only
`test_workflow_baseline_represents_every_archived_pair` against commit
`78822ca8f8c58fbc959495d37bdff32e525eb945` therefore fails first with:

```text
SyntaxError: invalid syntax
  tags = (
       ^
```

It never computes the old tuple and never reports the missing RC7 pair. The
current report's statement that this test fails on the exact RC7 omission is
unsupported. Other replay failures are also not substitutes: the current
pinned inventory intentionally includes the newly archived RC8 and therefore
cannot be expected to match the older source's archive inventory.

The live/current baseline itself did authenticate RC1-RC5, RC7, and RC8 at
their recorded digests, and current-tree tests are green. The defect is the
historical regression contract and its evidence, not the registry state or the
P01/P02 product repair.

## Required narrow correction

1. Fix the old-inline-tuple fallback parser so it parses the tuple expression,
   not the `tags =` assignment, and fails closed on malformed, ambiguous, or
   non-string content. Keep parsing bounded to the exact named workflow step;
   do not execute workflow text.
2. Add focused parser tests for the historical inline shape, including a valid
   multiline tuple and malformed/unbalanced/non-string cases. Preserve the
   current shared-helper path and its fail-closed behavior.
3. Mechanically replay the single coverage assertion against a clean export of
   exact commit `78822ca8f8c58fbc959495d37bdff32e525eb945` using the corrected test.
   It must reach the alias comparison and fail with the exact missing set:

   ```text
   0.1.0-rc7
   sha-ae6271318627703785f42de57d893c9be3b980c9
   ```

   No syntax/parser exception, missing-helper error, current RC8 inventory
   mismatch, or unrelated assertion may be cited as this proof.
4. Prove the same focused assertion passes against the corrected current tree,
   where the baseline is derived from all archived strict records and bound to
   their recorded digests. Keep intentional RC6 absence explicit.
5. Preserve the current live baseline implementation, P01/P02 product code,
   compiler-v3 semantics, metrics, privacy/bounds, and ledgers 006/007 unless a
   concrete regression forces a minimal correction. Do not broaden scope.
6. Correct release/history documentation so RC9 remains accurately recorded as
   published and qualified but rejected as the final handoff because its frozen
   historical replay test was defective. Do not rewrite immutable 015-b report
   or ledger 007.

## RC9 archive and RC10 identity

1. Archive RC9's current `rc_record.json`, `rc_handoff.md`, and published
   provenance byte-identically under `packaging/releases/0.1.0-rc9/`. Verify
   each hash against commit
   `231fa6e67a3240dbcc986b27fd7b62cf1c479245`.
2. Never rewrite, repoint, delete, or reuse either RC9 alias or D9. Preserve all
   earlier archives and registry identities. Do not invent RC6.
3. Advance the current-candidate constants, schemas, publisher guards,
   workflows, focused tests, current record/handoff, and release docs to exactly
   `0.1.0-rc10`.
4. Before any registry write, authenticate and prove both `0.1.0-rc10` and
   `sha-<exact-new-source-commit>` are absent. Fail closed if either is occupied
   or inaccessible. Publish only those two private aliases to one new digest;
   never overwrite an existing identity.

## New freeze and qualification

1. Freeze source commit `S10` only after the parser/test correction, RC9
   archive, RC10 constants/docs, and every source input are final. Generate the
   pre-freeze provenance from a clean tree. Prove clean CPython 3.12.3/3.12.14
   reproducibility and whether `W10 == W9`; equality is expected but must be
   measured.
2. Prove the complete source-input map binds the corrected regression at S10.
   No source input may change after S10; only mechanically excluded derived
   record/evidence/OAP commits may follow.
3. Require fresh source-head CI and CodeQL success before publication. Dispatch
   the guarded private release workflow from exact S10 and verify checkout,
   fresh-wheel binding, both absent aliases before write, one digest D10, and no
   historical identity or visibility change.
4. Add immutable testing ledger 008; do not edit 006 or 007. Repeat bounded
   genuine Codex 0.149.0 qualification (a specifically identified later-version
   fallback remains authorized only if 0.149.0 cannot be established): VISION,
   CACHE with compiler/cache/injection treatment, BOTH with treatment, and
   DIRECT control must all pass. No Gateway and no benchmark.
5. Generate strict current RC10 record/handoff and published provenance with
   S10, D10, both aliases, W10, build/lock/config/source hashes, Codex identity
   and arm facts, `linux/amd64`, private authentication, standalone no-Gateway,
   benchmark-not-run, final-release-false, and cutover-false.
6. Run the complete current local gates: lock/frozen install, Ruff, format,
   mypy, docs consistency, full pytest, artifact policy, fresh noneditable wheel
   smoke, compile/shell checks, PRE/POST record rehearsal, source-map equality,
   P01/P02 focused regressions, and the corrected current/historical registry
   replay tests.
7. Require final implementation-head CI and CodeQL fully green. The published
   Docker job must actually pull D10 without rebuilding and pass registry
   baseline, tag/digest, OCI labels, in-image wheel/lock/inventory, signed
   ingress, fail-closed readiness, hardening, content scan, lifecycle, and
   teardown. Its baseline must show RC7, RC8, and RC9 unchanged at D7/D8/D9 and
   current RC10 at D10.

## Protected host and non-goals

All prior protections remain in force. Only read-only inspection, bounded
authenticated calls, disposable loopback adapter port 18031, and private RC10
publication are authorized. Recheck before/after that PID 23961 alone owns
18020, ports 18021/18031 are otherwise absent, vision/inactive peer units,
command/model, and protected credential hash remain unchanged.

Do not modify benchmark harness/archive 001 or 002, run any benchmark or
Minesweeper attempt, change Codex, Gateway, vLLM, model/checkpoint/quantization/
context/parser/CUDA/GPU/network/service state, cut over a host, make GHCR
public, publish final `v0.1.0`, or create a final GitHub Release. Never expose
raw prompts/source/images/tool content/model output/upstream bodies/messages,
credentials, private identities, or session IDs.

## Acceptance and verdict

Accept only if the corrected historical replay reaches alias comparison and
fails on exact RC7 omission at 78822ca, passes on current source, RC9 remains
immutable, one new private RC10 digest is fully bound and qualified, all local/
CI/CodeQL/pulled-image/real-Codex gates pass, and no excluded work occurs.

Return `BENCHMARK_READY` only if all cumulative 015-a/015-b/015-c criteria are
true. Otherwise return `BENCHMARK_BLOCKED` with the exact remaining product or
release-contract blocker. Strategy alone decides acceptance and merge.

## Immutable report contract

Create exactly one `oap/reports/015-c-*.md`. State PR/base/branch, commits,
literal implementation SHA, changed paths, parser defect and exact before/after
replay evidence, RC9 archive hashes, S10/D10/aliases/W10/build/lock/source
identities, publication and CI URLs/jobs, pulled-image facts, ledger 008 facts,
protected-host before/after, privacy/non-goal audit, and strict verdict.

The final report commit must change only that report, have the literal reported
implementation SHA as its sole parent, state `Report publication commit: SELF`,
and be pushed as the existing PR head. Coding must not merge or enable
auto-merge.

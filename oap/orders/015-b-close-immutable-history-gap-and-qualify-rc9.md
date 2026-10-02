# OAP ORDER 015-b — Close immutable registry-history gap and qualify private RC9

## Objective and current state

Continue numeric Objective 015 in existing PR #22. **AMEND_EXISTING_PR** only;
**NO NEW PR**.

Objective 015-a correctly repaired and qualified P01/P02 and published private
RC8, but its truthful immutable report returned `BENCHMARK_BLOCKED`. Strategic
review independently confirms the one blocker: after archiving RC7, the frozen
CI read-only registry baseline claims to cover the archived RC7 aliases but its
literal immutable-history tuple stops at RC5. `.github/workflows/ci.yml` is a
member of the 130-entry frozen source-input map, so it cannot be corrected after
RC8 publication while retaining RC8's source/provenance binding.

Reject RC8 as the final Objective-015 handoff candidate without altering it.
Make the narrow release-history correction, preserve RC8 permanently, and
produce/qualify the next collision-safe private candidate, `0.1.0-rc9`.

## Exact GitHub and artifact state

- Repository: `ulfe-lmi/slaif-local-coding`.
- Objective/round: `015` / `015-b`.
- PR mode: `AMEND_EXISTING_PR`; PR #22:
  https://github.com/ulfe-lmi/slaif-local-coding/pull/22
- Base: `main` at `87ed2cea43a0a8706efe485b9b625dfda7cf75aa`.
- Required existing branch:
  `oap/015-upstream-diagnostics-compiler-truncation-rc8`.
- Current remote head/report SELF:
  `40771fd2f3453b90264c44c3f06b745edff58c22`.
- SELF parent/final 015-a implementation head:
  `78822ca8f8c58fbc959495d37bdff32e525eb945`.
- The report commit changes only
  `oap/reports/015-a-upstream-diagnostics-compiler-truncation-rc8.md` and has
  that exact parent. PR #22 is the unique open Objective-015 PR and remains
  non-draft. Coding must never merge or enable auto-merge.
- RC8 source `S8`:
  `718fff301bed0a5ba93b29196cde4d0bcc5d711a`.
- RC8 digest `D8`:
  `sha256:50450f4aa26a4da158dc457e0b80b441c69386c201491c6c0150c25d5916e126`.
- RC8 aliases: `0.1.0-rc8` and
  `sha-718fff301bed0a5ba93b29196cde4d0bcc5d711a`.
- RC8 wheel `W8`:
  `eb241dda2e079b29190868108c488edaf98261c84119bfd405070dea98b546b9`.
- RC8 publication run 36954165586 succeeded; published-state CI run
  36955048233 and CodeQL run 36955044768 succeeded; actual pulled-image
  qualification and genuine Codex 0.149.0 ledger 006 passed. These facts prove
  RC8 history but do not cure the frozen CI contract omission.
- Report-head CI may be pending or complete when this order starts; it is
  superseded by implementation changes and cannot substitute for final RC9
  exact-head checks.
- Pre-existing untracked paths `Local`, `clean`, and `unchanged` remain outside
  the PR and must not be modified, deleted, or committed.

## Exact confirmed blocker

The current frozen `.github/workflows/ci.yml` registry tuple contains historical
identities through RC5 but omits:

```text
0.1.0-rc7
sha-ae6271318627703785f42de57d893c9be3b980c9
```

although the same workflow comment claims the archived RC7 pair is covered.
The RC7 record/handoff/provenance archive is byte-identical to the prior current
files, and no evidence indicates RC7 was mutated. The defect is the missing
mechanical read-only assertion, not an RC7 registry mutation or a P01/P02
product failure.

Once RC8 becomes archived, its pair must also enter the immutable-history
baseline:

```text
0.1.0-rc8
sha-718fff301bed0a5ba93b29196cde4d0bcc5d711a
```

The current RC9 pair will continue to be added dynamically from the current
strict record in published-state CI. Do not special-case away an archived
candidate merely because its product gates passed.

## Required correction

1. Add the exact RC7 and RC8 alias pairs to the read-only registry baseline's
   immutable historical set, with accurate comments. The published-state job
   must assert both aliases of each pair remain at their recorded digest. It
   must remain read-only and fail closed on absent, unauthorized, ambiguous, or
   changed registry state.
2. Add a deterministic regression that derives the required historical aliases
   from every archived strict `packaging/releases/*/rc_record.json` that exists
   under the repository convention and proves the workflow baseline represents
   them. Handle the intentional missing RC6 identity explicitly; do not invent
   RC6. The test must fail against the 015-a frozen source for the RC7 omission
   and prevent the same omission when RC8 is archived. Prefer a focused parser
   or single source of truth over brittle prose matching, but avoid redesigning
   the registry workflow.
3. Preserve P01/P02 code, configuration, metrics, privacy, bounds, compiler-v3
   identity, tests, and documentation semantics unless a concrete regression
   forces a minimal correction. Do not expand product scope.
4. Preserve testing ledger 006 and all benchmark archives/ledgers byte-for-byte.
   Do not relabel RC8 as unpublished or erase its successful qualification. Its
   rejection is limited to the frozen release-history contract gap.

## RC8 archive and RC9 identity

1. Archive the current RC8 record, handoff, and published provenance
   byte-identically under `packaging/releases/0.1.0-rc8/` before replacing the
   current pointer. Verify the three archive hashes against commit
   `78822ca8f8c58fbc959495d37bdff32e525eb945`.
2. Never rewrite/repoint/delete either RC8 alias or digest. Preserve RC7 and all
   earlier identities/archives. No RC6 identity may be created.
3. Advance explicit current-candidate constants, schemas, publisher guards,
   workflows, tests, records, handoff, provenance, and focused release docs to
   exactly `0.1.0-rc9`. Do not leave a stale claim that RC8 is the current
   handoff. Historical RC8 facts must stay accurate.
4. Before any registry mutation, authenticate and prove both `0.1.0-rc9` and
   `sha-<exact-new-source-commit>` are absent. Fail closed if either is occupied
   or registry state is ambiguous. Publish exactly those two aliases privately;
   never overwrite an older alias or write final/stable/public identities.

## New freeze, qualification, and evidence

1. Freeze a new source commit `S9` only after the CI-history fix, regression,
   RC9 constants/docs/tests, and every artifact input are final. Regenerate the
   pre-freeze provenance from a clean tree. Because the product wheel is
   expected to be unchanged, prove rather than assume whether `W9 == W8` with
   clean CPython 3.12.3/3.12.14 reproducible builds. A different wheel is
   acceptable only if explained by an authorized in-scope source change.
2. Prove the complete source-input map binds the corrected workflow at `S9` and
   differs from S8 exactly as expected. No artifact input may change after S9;
   only mechanically excluded derived record/evidence/OAP commits may follow.
3. Require fresh source-head CI and CodeQL success before publication. Dispatch
   the guarded release workflow from exact `S9`; verify checkout/head, wheel,
   both absent aliases before write, a single new private digest `D9`, and no
   historical identity/visibility change.
4. Create a new immutable testing ledger 007 for RC9. Do not edit ledger 006.
   Repeat the bounded genuine-Codex qualification with exact 0.149.0 if
   available (one explicitly identified later-version fallback remains
   human-authorized only if 0.149.0 cannot be established): VISION PASS, CACHE
   PASS with compiler/cache/injection treatment evidence, BOTH PASS with
   treatment evidence, DIRECT PASS as contextual control. No Gateway. Use the
   same protected-host, privacy, cleanup, and bounded-attempt rules as 015-a.
5. Generate current strict RC9 record/handoff and published provenance from
   authenticated facts. Include RC9 `S9`, `D9`, aliases, `W9`, build pins, lock
   hash, configuration/source-input hashes, Codex version/hash and arm results,
   platform, private-auth requirement, standalone-no-Gateway, benchmark-not-run,
   final-release-false, and cutover-false.
6. Run all local gates again: lock check, frozen sync, Ruff, format, mypy, docs
   consistency, full pytest, artifact policy, fresh noneditable wheel smoke,
   compileall/shell checks, PRE/POST record rehearsal, source-map equality, and
   focused P01/P02/history regressions.
7. Require final implementation-head CI and CodeQL fully green. The published
   Docker job must actually pull `D9` without rebuilding and pass tag/digest,
   OCI labels, in-image wheel/lock/inventory, noneditable install, signed-ingress,
   fail-closed readiness, hardening, content scan, lifecycle, and teardown. Its
   authenticated baseline must explicitly show RC7 and RC8 pairs unchanged at
   D7/D8 and the current RC9 pair at D9.

## Protected-host and non-goals

All 015-a protections remain in force. Only read-only inspection, bounded
authenticated calls, a disposable loopback adapter on 18031, and private RC9
publication are authorized. Recheck before/after that PID 23961 alone owns
18020, 18021/18031 are absent outside the disposable run, the
`qwen-serving-vision.service`/inactive peer state and command/model are
unchanged, and protected credential-file hashes are unchanged.

Do not modify the benchmark harness or archives, run any benchmark/Minesweeper
attempt, change Codex, Gateway, vLLM, model/checkpoint/quantization/context/
parsers/CUDA/GPU/network/service state, cut over a protected host, make GHCR
public, publish final `v0.1.0`, or create a final GitHub Release. Never expose
raw prompts/source/images/tool content/model output/upstream bodies/messages,
credentials, private identity, or sessions in logs/evidence/metrics.

## Acceptance and verdict

This continuation is acceptable only when:

- the workflow baseline and regression mechanically cover every archived RC
  record, including exact RC7 and RC8 pairs, while preserving intentional RC6
  absence;
- RC8 and all earlier archive/registry bytes remain unchanged;
- one new private RC9 digest exists with both collision-safe aliases and full
  source/wheel/provenance binding;
- all local, exact-head CI, CodeQL, pulled-image, P01/P02, and genuine-Codex
  VISION/CACHE/BOTH/DIRECT gates are green;
- the current record/handoff points to RC9 and contains every handoff field;
- no benchmark, final release, public visibility, Gateway/vLLM mutation, or
  cutover occurred.

Return `BENCHMARK_READY` only if all cumulative 015-a and 015-b criteria are
true. Otherwise return `BENCHMARK_BLOCKED` with the exact remaining product
blocker. Strategy will independently review, merge only a fully accepted PR,
then require fresh post-merge main CI and CodeQL before its final verdict.

## Immutable report contract

Create exactly one report matching `oap/reports/015-b-*.md`. Before the report
commit, push all implementation/evidence/PR metadata. State exact PR/base/branch,
all new commits, literal final implementation SHA, changed paths, correction and
regression evidence, archive hashes, S9/D9/aliases/W9/lock/build identities,
publication and CI job URLs, pulled-image facts, ledger 007/Codex arm facts,
protected-host before/after, privacy/non-goal audit, and strict verdict.

The final report commit must change only that report, have the literal reported
implementation SHA as its sole parent, state `Report publication commit: SELF`,
and be pushed as the existing PR head. Never merge; strategy alone reviews and
merges.

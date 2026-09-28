# OAP Coding-Agent Report — 014-h

## Work order
- Identifier: 014-h; order path: `oap/orders/014-h-restore-published-order-history-and-finalize-rc7-pr.md`; numeric objective 014
- PR mode: AMENDED_EXISTING_PR — PR #19 (the one and only Objective-014 PR); never merged
- Order SHA-256 (014-h, byte-exact, committed unchanged):
  `1fbe56cc52c708675b968a2efdd0a5c61f22c74ccb6309e8091d7b44fc8d458e`
- Restored order SHA-256 (014-d, byte-exact strategic original, committed unchanged):
  `2d0111818e7d9f2e150e09396924f9160597aafc4ad27545ad1756f5d636a2ea`
  (exactly the value the order requires)

## Status
COMPLETE

## Executive summary
OAP continuity repair only. Restored the missing published 014-d order into the
branch history from the strategy byte-exact copy (SHA-256 verified before and
after commit), committed this round's byte-exact order plus the `oap/active`
activation (`014-g` → `014-h`) in exactly one transcript-only implementation
commit (`00d395f9…`), pushed it, and rewrote PR #19's title/body so the
reviewer-facing metadata describes the final RC7 result (exact S7/digest,
genuine-Codex 0.149 VISION/CACHE/BOTH pass, pulled-image qualification,
private/non-final status, explicit no-benchmark/no-cutover boundaries),
removing the stale wording that presented RC4 as the final result. Obtained
fresh exact-head CI (5/5 jobs SUCCESS) and CodeQL (both analyses + aggregate
SUCCESS) with zero open code-scanning alerts. Independently verified that all
RC7 identities, the 127-entry source-input map, the protected host/port state,
and the non-goal boundaries are unchanged. No product source, workflow, test,
schema, configuration, documentation, packaging record, provenance, handoff,
ledger, release identity, or registry state was touched; no RC7 republish and
no protected inference rerun (none was required). No merge, no second PR.

## Authoritative GitHub state
- Repository: `ulfe-lmi/slaif-local-coding`
- PR: #19, OPEN, non-draft, MERGEABLE / merge state CLEAN; base `main` at
  `8c3c6d6cd67a34ba7d427ab255a91bd6a9753bd1`; head branch
  `oap/014-real-codex-compatibility-rc3`
- Starting remote SHA (verified before mutation):
  `30c78447fef68583c984e42a3ae24b297ff2da29` (014-g report-only SELF)
- Implementation head SHA: `00d395f9d163552debb56d1d12357fda8a50fd20`
- Report publication commit: SELF
- Implementation commits pushed before report: exactly one —
  `00d395f9d163552debb56d1d12357fda8a50fd20`
  ("Objective 014-h (transcript): restore published 014-d order history —
  orders 014-d + 014-h + oap/active (byte-exact strategic bytes)")
- PR metadata updated this round: title and body (GitHub REST PATCH at
  2026-09-28T20:34:40Z; body 3748 bytes)
- New PR this round: NO; amended existing PR #19: YES; merge performed: NO

## Changes and files
- `00d395f9` — exactly 3 files, 228 insertions(+), 1 deletion(−), OAP-only:
  - `oap/orders/014-d-reject-rc5-freeze-corrected-gates-and-qualify-private-rc6.md`
    — ADDED (+184 lines), byte-exact strategic original (sha256
    `2d011181…36a2ea`, verified on disk and in the committed blob)
  - `oap/orders/014-h-restore-published-order-history-and-finalize-rc7-pr.md`
    — ADDED (+43 lines), byte-exact (sha256 `1fbe56cc…d458e`)
  - `oap/active` — `014-g` → `014-h` (6 bytes: `014-h\n`)
- Remote `compare 30c78447……00d395f9…` confirms exactly these 3 file changes
- Pre-existing untracked zero-byte files `Local`, `clean`, `unchanged`:
  preserved, not committed, not deleted
- PR #19 metadata (not a repository file):
  - title: "Qualify private RC7 0.1.0-rc7 as the final Objective-014 result
    (predecessors archived; RC6 abandoned)"
  - body: final-state description — RC7 S7
    `ae6271318627703785f42de57d893c9be3b980c9` / D7
    `sha256:a3782915da58a403fd0f7991c57f9954b07bfb9377e4730715c0fb7398f901db`,
    genuine-Codex 0.149 VISION/CACHE/BOTH PASS (ledger 005), pulled-image
    qualification 13/13 at the actual D7, final-head CI/CodeQL facts,
    archived predecessors (RC3/RC4/RC5), RC6 abandonment, 014-h repair note,
    explicit no-benchmark / no-final-release / no-cutover / no-Gateway-mutation
    boundaries. The previous body (presenting RC4 as the PR's result) was
    fully replaced.

## Acceptance evidence
### Criterion 1 — reconciliation before mutation
- `git ls-remote origin`: `main` = `8c3c6d6cd67a34ba7d427ab255a91bd6a9753bd1`
  (exact order value); branch `oap/014-real-codex-compatibility-rc3` =
  `30c78447fef68583c984e42a3ae24b297ff2da29` (exact order value); local HEAD
  equals the remote head
- `gh pr view 19`: OPEN, non-draft, MERGEABLE, base `main`, head
  `30c78447…`; working tree contained only the expected modifications
- PASSED
### Criterion 2 — strategy-restored 014-d order verified, not edited
- File present at `oap/orders/014-d-reject-rc5-freeze-corrected-gates-and-
  qualify-private-rc6.md`; `sha256sum` =
  `2d0111818e7d9f2e150e09396924f9160597aafc4ad27545ad1756f5d636a2ea` = exact
  order-required digest; committed blob re-hashed after commit: identical
- PASSED
### Criterion 3 — exactly the three transcript changes in one commit
- Staged diff contained exactly `M oap/active`, `A oap/orders/014-d-…md`,
  `A oap/orders/014-h-…md` (no `git add -A`; placeholders never staged)
- Commit `00d395f9` parent = `30c78447…`; `git show --stat` = 3 files,
  228(+)/1(−); remote compare API confirms the same 3-file change set
- PASSED
### Criterion 4 — untracked placeholders preserved
- `Local`, `clean`, `unchanged` remain untracked after the commit; not
  committed, not deleted
- PASSED
### Criterion 5 — PR metadata describes the final RC7 result
- Title/body replaced via `gh api …/pulls/19 -X PATCH` (2026-09-28T20:34:40Z);
  verified remote: new title in place, body_len 3748, head unchanged
- Stale RC4-as-final wording removed; final-state facts (S7, D7,
  VISION/CACHE/BOTH, pulled-image 13/13, private/non-final,
  no-benchmark/no-cutover) all present and taken from verified 014-g facts
- PASSED
### Criterion 6 — push + fresh exact-head CI/CodeQL, zero alerts, no republish
- Push `30c7844…→00d395f…` accepted; remote head re-verified
- Fresh CI run `36480067101` at exact head `00d395f9…`: 5/5 jobs SUCCESS
  (test 1439 passed / 27 skipped in 129.76 s; gateway-contract; docker;
  docker-published; operator-session)
- Fresh CodeQL run `36480062961` at exact head: `Analyze (actions)` SUCCESS,
  `Analyze (python)` SUCCESS, aggregate SUCCESS
- Open code-scanning alerts: 0 (`gh api …/code-scanning/alerts?state=open`)
- Only CI + CodeQL ran at the new head (no `release-image` or other workflow
  run): RC7 was NOT republished and no protected inference was rerun; no
  existing mandatory check required it
- PASSED
### Criterion 7 — independent verification
- (a) RC7 identities unchanged: `git diff --name-only B7…00d395f9`
  (`91694097…`) shows only the 014-g report plus this round's 3 transcript
  paths — `packaging/rc_record.json`, `packaging/rc_handoff.md`,
  `packaging/release_provenance_manifest.json`, and
  `oap/evidence/testing-ledger/005/` untouched since B7;
  `sha256sum -c oap/evidence/testing-ledger/005/MANIFEST.sha256` → both files
  OK; record/manifest facts re-read: rc_identifier `0.1.0-rc7`,
  image_source_commit = workflow_head_sha = S7, digest = D7, objective
  `014-e` preserved, 127 source inputs, `final_public_release: false`,
  `cutover_performed: false`; fresh CI `docker-published` (published mode)
  independently re-asserted registry `0.1.0-rc7` → D7 and
  `sha-ae627131…` → D7 (one digest for both) and in-image wheel = W7
- (b) Source-map proof at the NEW implementation head:
  `source_input_map.py --ref 00d395f9d163552debb56d1d12357fda8a50fd20
  --manifest packaging/release_provenance_manifest.json` → "input-map ref
  OK: 00d395f9d163 matches the recorded map"; plus
  `--ab ae627131… 00d395f9…` → "input-map A/B binding OK: ae6271318627 ==
  00d395f9d163 (127 input files)"
- (c) Protected host/ports: baseline (pre-commit, ≈20:31Z) and post-round
  (≈20:43Z) read-only snapshots identical — vLLM PID 23961 started
  2026-09-06 18:57:26 (same full command line), exactly one listener
  `0.0.0.0:18020` (pid 23961), **no listener on 18031**, units
  `qwen-serving-vision.service`=active / `qwen-serving.service`=inactive,
  mtime/mode row-identical (verify.sh 1787080230/755; vision unit
  1787182428/644; main unit 1787088648/644; .bak 1787130863/644; drop-in dir
  1787363185/755; qwen-serving dir 1787184823)
- (d) Non-goal audit: 0 git tags on the remote (unchanged); 0 GitHub Releases
  (no final GitHub Release); unauthenticated GHCR token endpoint → HTTP 401
  (package still private, no visibility change); no registry/tag/release
  mutation performed this round (only the OAP branch push; no
  workflow_dispatch); no benchmark run or benchmark repository access; no
  Gateway-repository mutation; no protected-host cutover (fixture state
  invariant per (c); loopback 18031 absent)
- PASSED

## Verification
- `git ls-remote origin main refs/heads/oap/014-real-codex-compatibility-rc3`:
  PASSED — `8c3c6d6c…` / `30c78447…` at preflight, `00d395f9…` after push
- `gh pr view 19` (state/mergeable/head, before and after): PASSED
- `sha256sum oap/orders/014-d-….md` (pre-commit) and
  `git show HEAD:oap/orders/014-d-….md | sha256sum` (post-commit): PASSED —
  both `2d0111818e7d9f2e150e09396924f9160597aafc4ad27545ad1756f5d636a2ea`
- `sha256sum` 014-h order (disk) vs committed blob: PASSED —
  `1fbe56cc52c708675b968a2efdd0a5c61f22c74ccb6309e8091d7b44fc8d458e`
- `git show :oap/active | xxd` (staged) / `git show HEAD:oap/active`: PASSED —
  exactly `014-h\n`
- `git diff --cached --name-status` / `git show --stat` / GitHub compare API:
  PASSED — exactly the 3 ordered paths
- `uv lock --check`: PASSED
- `uv sync --frozen --extra dev`: PASSED
- `uv run --frozen ruff check .`: PASSED (all checks passed)
- `uv run --frozen ruff format --check .`: PASSED
- `uv run --frozen mypy src tests`: PASSED
- `uv run --frozen python scripts/docs_consistency_check.py`: PASSED (19 claim
  docs checked)
- `uv run --frozen pytest -q` (local, at new head): PASSED — 1440 passed,
  26 skipped, 0 failed (183.54 s); the single delta vs CI (1439/27) is the
  host-pinned protected-preflight test honestly SKIPPED on GitHub runners —
  same documented class as prior rounds
- `uv build`: PASSED — wheel `897ef60568e9521dbb4ea563f297608e4409e02d54109471e789d43ff57dd10d`
  (= W7, byte-identical) and sdist `65527c6f657023d556c3d6cb5b9bf849a8fe4dac8c53d77a8de26d9e76be4579`
  (byte-identical to the S7 frozen builds) — the OAP-only diff leaves W7
  intact
- `uv run --frozen python scripts/artifact_policy_check.py --dist dist --inspect`:
  PASSED (wheel 26 entries, sdist 125 entries, 0 violations)
- `uv run --frozen python scripts/artifact_policy_check.py --dist dist --install-smoke`:
  PASSED (fresh venv, non-editable, 0 violations)
- `uv run --frozen python scripts/source_input_map.py --ref
  00d395f9d163552debb56d1d12357fda8a50fd20 --manifest
  packaging/release_provenance_manifest.json`: PASSED ("input-map ref OK")
- `uv run --frozen python scripts/source_input_map.py --ab
  ae6271318627703785f42de57d893c9be3b980c9
  00d395f9d163552debb56d1d12357fda8a50fd20 --manifest …`: PASSED (127 input
  files, binding OK)
- `sha256sum -c oap/evidence/testing-ledger/005/MANIFEST.sha256`: PASSED
- `ss -ltnp` / `ps` / `systemctl --user is-active` / `stat` (baseline and
  post-round): PASSED — invariant per Criterion 7(c)
- `gh run view 36480067101` / `gh run view 36480062961` /
  `gh api …/code-scanning/alerts?state=open`: PASSED — all SUCCESS, 0 alerts
- Unauthenticated GHCR probe (token endpoint): PASSED as expected — HTTP 401
  (package private, no visibility change)

## Live model/service evidence
- NO live inference in this round: the order forbids republishing RC7 or
  rerunning protected inference unless an existing mandatory check
  unexpectedly requires it; no check required it (fresh CI/CodeQL ran only)
- Read-only protected-fixture facts before (≈20:31Z) and after (≈20:43Z)
  mutation: identical — vLLM PID 23961 (started 2026-09-06 18:57:26, no
  restart), single listener `0.0.0.0:18020`, no `18031` listener at any point
  this round, units `qwen-serving-vision.service`=active /
  `qwen-serving.service`=inactive, unit/drop-in/env/model-file mtimes and
  modes row-identical to the baseline
- No credential use for live endpoints; no secrets printed

## GitHub CI / required checks
- Implementation head `00d395f9d163552debb56d1d12357fda8a50fd20`:
  - CI run `36480067101` (created 2026-09-28T20:33:39Z, completed
    2026-09-28T20:36:15Z), event `pull_request`:
    - `test` SUCCESS (1439 passed, 27 skipped, 129.76 s) —
      https://github.com/ulfe-lmi/slaif-local-coding/actions/runs/36480067101/job/109123231855
    - `gateway-contract` SUCCESS —
      https://github.com/ulfe-lmi/slaif-local-coding/actions/runs/36480067101/job/109123231967
    - `docker` SUCCESS —
      https://github.com/ulfe-lmi/slaif-local-coding/actions/runs/36480067101/job/109123231584
    - `docker-published` SUCCESS (published mode, 13/13 phases; pulled the
      actual D7 with no build; registry `0.1.0-rc7` and `sha-ae627131…` both
      → D7; in-image wheel = W7; signed ingress 200/401/403/409; fail-closed
      503; hardening/labels; teardown absence proof) —
      https://github.com/ulfe-lmi/slaif-local-coding/actions/runs/36480067101/job/109123231791
    - `operator-session` SUCCESS —
      https://github.com/ulfe-lmi/slaif-local-coding/actions/runs/36480067101/job/109123232042
  - CodeQL run `36480062961` (created 2026-09-28T20:33:37Z, completed
    2026-09-28T20:34:39Z), event `dynamic` (PR #19):
    - `Analyze (actions)` SUCCESS —
      https://github.com/ulfe-lmi/slaif-local-coding/actions/runs/36480062961/job/109123225023
    - `Analyze (python)` SUCCESS —
      https://github.com/ulfe-lmi/slaif-local-coding/actions/runs/36480062961/job/109123225466
    - aggregate CodeQL SUCCESS
  - Open code-scanning alerts: **0**
- All required green at drafting: YES. Report-head checks (triggered by the
  report-only push) may be pending; strategy verifies.

## Local setup/dependencies
- Repo venv via `uv` (lock intact; frozen installs); no new packages,
  services, or sudo actions; no human/strategic terminal work recruited
- No host Docker use by the coding agent (Docker phases ran on CI runners)
- Disposable temp files (`/tmp/local-gate-014h*.log`,
  `/tmp/pr19-body-014h.md` mode 0600, `/tmp/ghcr_token_014h.json` — an
  anonymous-scope token response that failed to issue, 401) contain no
  secrets and are outside the repository

## Documentation
- Not changed: the order forbids documentation changes and this round altered
  no behavior, configuration, security property, or limitation — the diff is
  OAP transcript history only. Existing docs (TESTING.md, docs/HISTORY.md,
  docs/RC-HANDOFF.md) already describe the RC7 path and ledgers accurately

## Safety/scope confirmations
- Unrelated files: none touched; untracked zero-byte `Local`/`clean`/
  `unchanged` preserved and uncommitted
- Secrets/raw content: none printed, logged, or committed; no API keys,
  tokens, prompts, or private URLs in this report or in the PR body
- Production/protected resources: protected 18020/Qwen/Codex fixture
  changed: **NO** (Criterion 7(c))
- Required tests skipped/not run: only documented classes (Gateway-peer
  checkout absent locally; host-pinned rehearsal test skipped on CI runners;
  live-test env var classes); no required test skipped locally where its
  fixture exists
- Scope deviation: none; no product/workflow/test/schema/config/doc/packaging
  change; no RC7 republish; no protected inference rerun
- Extra objective PR: NO. Coding merge: NO. Auto-merge: NO
- Active/order edited: NO — the 014-d and 014-h bytes were committed
  unchanged (sha256-verified against the strategic originals); `oap/active`
  changed exactly as ordered (`014-g` → `014-h`)
- Report commit report-only: yes (this commit changes only
  `oap/reports/014-h-restore-published-order-history-and-finalize-rc7-pr.md`)

## Known limitations/blockers
- The local `gh` credential cannot read the private GHCR package (no
  `read:packages`), so local registry truth is limited to unauthenticated
  401 probes; authoritative registry facts for the new head come from the
  fresh CI `docker-published` job's authenticated assertions (both RC7
  aliases → D7, historical digests unchanged, package private)
- Baseline/post snapshot wall times are labeled ≈ (approximate to the minute);
  the invariant facts themselves (PID, start time, listener, unit state,
  mtime/mode rows) are exact

## Verdict
BENCHMARK_READY — the cumulative Objective-014 result remains fully
satisfied at the new head: RC7 identities (S7
`ae6271318627703785f42de57d893c9be3b980c9`, D7
`sha256:a3782915da58a403fd0f7991c57f9954b07bfb9377e4730715c0fb7398f901db`,
both aliases, record/handoff/rc-published manifest, ledger 005) byte-
invariant; 127-entry source-input map proven at the new head; fresh exact-
head CI 5/5 + CodeQL all SUCCESS with 0 open alerts; `docker-published`
re-qualified the actual pulled D7 (13/13); protected fixture and port 18031
invariant; no benchmark, no final public release, no cutover, no visibility
change, no Gateway mutation. The published order history is now complete
(014-d restored byte-exact), and PR #19's metadata describes the final RC7
result. Strategy alone accepts/merges and returns the final verdict.

## Recommended strategic follow-up
- Strategy reviews this round (OAP history restoration + PR metadata
  finalization) and alone decides acceptance/merge of PR #19.
- After merge, RC7 handoff consumers need only the machine record + rendered
  handoff (no source rebuild). A final public release and a protected-host
  cutover remain separate explicit decisions.

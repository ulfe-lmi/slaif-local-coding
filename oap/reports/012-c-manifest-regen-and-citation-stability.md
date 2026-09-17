# OAP Coding-Agent Report — 012-c

## Work order
- Identifier: `012-c`; order path: `oap/orders/012-c-manifest-regen-and-citation-stability.md`; numeric objective `012`
- PR mode: `AMENDED_EXISTING_PR` (PR #14, no new PR)

## Status
COMPLETE

All six bounded scope items (T1–T6) were executed exactly as ordered; the
E3 manifest gate (`test_committed_manifest_matches_regenerated`) passes
locally and in CI at the implementation head; CI is green at the
implementation head; the citation-stability audit is clean; no file outside
T1–T6 plus the 012-c order/active transcripts and this report was changed;
no publication, cutover, or protected-host mutation occurred.

## Executive summary
`packaging/release_provenance_manifest.json` was regenerated with
`scripts/release_provenance_manifest.py` from the FINAL implementation
state: `objective` advances `012-a` -> `012-c` (generator constant and test
expectation updated in T1/T2), `generated_from.git_commit` =
`69e08213eed97bcaa4baea158999e3af0922ab92` (the T1–T5 commit, a strict
ancestor of the implementation head, which the E3 gate explicitly permits),
the wheel record is unchanged
(`fceadc378130dd4ffcc3f75d17b5e098577652914f541245d31247911be23aeb`, 83097
B, 26 entries — proven byte-exact by clean rebuild), and the developer-only
sdist record advances to the final-state clean rebuild
(`72de29c9e60a012425e1c0d0d351ce7ff9c985b1f3b28c3525987a4f70db1c12`,
425885 B, 105 entries). The current-facing docs (T3–T5) no longer cite the
current sdist hash or the current manifest `objective` field: the wheel hash
is cited exactly (stable from here on in this objective), the two historical
records (011-a and 012-a state) are cited explicitly as historical, and the
current manifest is referenced by path + schema name, with the authoritative
current sdist hash defined as the manifest-recorded value mechanically
re-derived by `test_committed_manifest_matches_regenerated`. Local full
pytest is fully green (1087 passed, 26 standing skips) and CI run
`35183999924` at the implementation head is fully green
(`test`/`gateway-contract`/`docker` all `success`).

## Authoritative GitHub state
- Repository: `ulfe-lmi/slaif-local-coding`
- PR: #14 — https://github.com/ulfe-lmi/slaif-local-coding/pull/14 — `OPEN`,
  non-draft, `autoMergeRequest: null`, the only open PR and exactly the
  Objective-012 PR (verified at round start and after push)
- Base: `main` @ `e860e0bff687afded7782fb2687b5b435792459a` (verified
  unchanged on GitHub at round start)
- Branch (unchanged, as required): `oap/012-gateway-peer-repin`
- Head at order time: `1c6c6b39e0d651d784511f9cd0e15101f99e8483` (012-b
  report commit); prior implementation head:
  `c384150cbc83c8c5d463b6b855fe20a5fe11a746`
- Implementation commits pushed before report: exactly two
  - `69e08213eed97bcaa4baea158999e3af0922ab92` (T1–T5 + 012-c transcript), parent `1c6c6b39e0d651d784511f9cd0e15101f99e8483`
  - `283893548881c8e5c3c144540ab7fe0d673d0210` (T6, last implementation commit), parent `69e08213eed97bcaa4baea158999e3af0922ab92`
- Implementation head SHA: 283893548881c8e5c3c144540ab7fe0d673d0210
- Report publication commit: SELF
- New PR this round: no; amended existing: yes (#14); merge performed: NO

## Changes and files
Round commits `69e0821` + `2838935` change exactly 8 files (this round only,
vs the 012-b report head `1c6c6b3`):

| # | File | Change | +/- |
| --- | --- | --- | --- |
| T1 | `scripts/release_provenance_manifest.py` | `OBJECTIVE` constant `012-a` -> `012-c`; no other generator change | 1/1 |
| T2 | `tests/test_release_provenance_manifest.py` | `test_objective_field_records_producing_objective` expectation `012-a` -> `012-c`; E3 gate and all hash cross-checks untouched | 1/1 |
| T3 | `docs/RELEASE-ARTIFACT-POLICY.md` | 012 paragraph made stable: wheel transition statement kept exact; current-sdist-hash citation replaced by the developer-only policy statement; 011-a and 012-a-state records cited as historical only; manifest authority by path + schema | 22/14 |
| T4 | `docs/RELEASE-CUTOVER-RUNBOOK.md` | Preconditions item 2 parenthetical replaced with the stable form (current manifest by path, schema `slaif-release-provenance-v2`, produced by Objective 012); no other runbook change | 6/5 |
| T5 | `docs/IMPLEMENTATION-ROADMAP.md` | "Current state" Objective-012 parenthetical replaced with the stable form (current artifact record = manifest path, wheel hash cited exactly, sdist developer-only/manifest-recorded); no other roadmap change | 6/6 |
| T6 | `packaging/release_provenance_manifest.json` | regenerated at the final state; last implementation commit; diff is exactly 4 lines: sdist `sha256`+`size_bytes`, `generated_from.git_commit`, `objective` | 4/4 |
| — | `oap/active` | transcript (strategic bytes as found: `012-b` -> `012-c`) | 1/1 |
| — | `oap/orders/012-c-manifest-regen-and-citation-stability.md` | transcript (activated order, new file, committed byte-unchanged) | 223/0 |

T6 commit `2838935` touches only the manifest (1 file, 4/4); no build input
changes after regeneration.

## Acceptance evidence

### E1 — Manifest regenerated at final state — MET
- Regenerated with `uv run --frozen python scripts/release_provenance_manifest.py --dist <throwaway> --emit packaging/release_provenance_manifest.json` from the final implementation state (after T1–T5 in place).
- `objective: "012-c"` (verified in the committed file and by the re-run of `test_objective_field_records_producing_objective`).
- `artifacts.wheel` exactly `fceadc378130dd4ffcc3f75d17b5e098577652914f541245d31247911be23aeb` (83097 B, 26 entries) — unchanged.
- `artifacts.sdist` = `72de29c9e60a012425e1c0d0d351ce7ff9c985b1f3b28c3525987a4f70db1c12` (425885 B, 105 entries) = the clean-rebuild hash at the final state (see E2).
- `generated_from.git_commit` = `69e08213eed97bcaa4baea158999e3af0922ab92` (the generating commit = T1–T5 commit; strict ancestor of the implementation head, which `test_committed_git_commit_is_ancestor_of_head` explicitly permits).
- `test_committed_manifest_matches_regenerated`: PASSED locally (within the full-suite run below) and in CI at the implementation head (run `35183999924`, `test` job `105082029464`, 1086 passed, 27 skipped, 0 failed).

### E2 — Wheel invariance proven — MET
- Clean rebuild at the final state (`uv build --out-dir <throwaway>`):
  - wheel `slaif_local_coding-0.1.0-py3-none-any.whl` = `fceadc378130dd4ffcc3f75d17b5e098577652914f541245d31247911be23aeb` (83097 B) — byte-exact match with the required wheel (26 entries, 20 runtime package files).
  - sdist `slaif_local_coding-0.1.0.tar.gz` = `72de29c9e60a012425e1c0d0d351ce7ff9c985b1f3b28c3525987a4f70db1c12` (425885 B, 105 entries).
- Entry-level identity vs the 011 record: the rebuilt wheel is byte-exact
  equal to the `fceadc37…` record of the 011->012 record chain, for which
  the 012-a entry-level diff already proved all 20 wheel runtime files
  byte-identical to the Objective-011 record (only `dist-info/METADATA` and
  `dist-info/RECORD` differ; README-row delta in METADATA long description).
  Byte-equal wheel => identical entry set; re-confirmed by
  `artifact_policy_check.py --inspect` (`ok: true`, `violations: []`, wheel
  26 entries / 20 package files / `fceadc37…` / 83097 B; sdist 105 entries).

### E3 — Citation stability — MET
Exact-phrase audit at the final head `2838935…` (committed tree, current-facing docs = `README.md`, `docs/`, `oap/COMPLETENESS.md`):

```text
objective: "012-a" / objective: "012-c": NONE
910b65db: exactly 1 occurrence — docs/RELEASE-ARTIFACT-POLICY.md:165,
  inside "The historical artifact records, cited as historical only, are the
  Objective-011-a record (wheel `7cede0b8...` / sdist `4ba17680...`) and the
  Objective-012-a-state record (wheel `fceadc37...` / sdist `910b65db...`)";
  explicitly labeled historical
final sdist hash 72de29c9: NONE (no document cites the current sdist hash)
0cf24290 (012-b intermediate CI value): NONE
this PR / pre-merge / open PR: NONE
stale pin 65666f58 outside oap/: exactly the four audited locations
  (docs/SLAIF-GATEWAY-INTEGRATION.md:83 provenance; docs/TOPOLOGY.md:61
  re-pin provenance; docs/TOPOLOGY.md:102 dated 010-era inspection record;
  docs/topology.manifest.json:135 as-of snapshot) — unchanged, none
  presented as current
```

The wheel hash `fceadc378130dd4ffcc3f75d17b5e098577652914f541245d31247911be23aeb`
is cited exactly where current (T3 policy doc, T5 roadmap) and may be cited
exactly per the stable design. T4 and T5 reference the current manifest by
path + schema (`slaif-release-provenance-v2`), never by `objective` field
value. T3 additionally states the stable policy: the sdist is
developer-only, embeds `README.md`/`docs/`/`tests/`, its hash changes with
any in-scope text edit, and the authoritative current sdist hash is the
manifest-recorded one, mechanically re-derived by
`test_committed_manifest_matches_regenerated`.

### E4 — No other file changed — MET
`git diff c384150cbc83c8c5d463b6b855fe20a5fe11a746..283893548881c8e5c3c144540ab7fe0d673d0210 --name-status` = exactly:
`docs/IMPLEMENTATION-ROADMAP.md`, `docs/RELEASE-ARTIFACT-POLICY.md`,
`docs/RELEASE-CUTOVER-RUNBOOK.md`, `oap/active` (M); `oap/orders/012-c-manifest-regen-and-citation-stability.md`
(A); `oap/reports/012-b-artifact-identity-doc-truth.md` (A — added by the
prior round's report commit `1c6c6b3…`, immutable history, not a change of
this round); `packaging/release_provenance_manifest.json`,
`scripts/release_provenance_manifest.py`,
`tests/test_release_provenance_manifest.py` (M). No other path differs.
Restricted-path guard (`src/`, `uv.lock`, `pyproject.toml`, `Dockerfile`,
`compose.yaml`, `.github/`, `docs/topology.manifest.json`,
`tests/fixtures/`, `scripts/cutover_state_machine.py`,
`tests/test_cutover_state_machine.py`, packaging templates): empty diff.
C10 freeze held: `uv.lock` SHA-256
`1237cbd179f71b99984c80f927529549f5e61eb705585ef9cf2ab0fa9e26764a` and
`pyproject.toml` SHA-256
`af91f82283882f1e51ee763d635f94f1ae2534c51585c837aa61cff8a2f7dda2`
(equal to the base values); zero `src/` files changed; no version bump.

### E5 — CI green at the implementation head AND the report head
- Implementation head `283893548881c8e5c3c144540ab7fe0d673d0210`: CI run
  `35183999924` —
  - `test` (job `105082029464`): **SUCCESS** — `1086 passed, 27 skipped in 72.89s`, 0 failed; the E3 gate `test_committed_manifest_matches_regenerated` passes.
  - `gateway-contract` (job `105082029566`): **SUCCESS** (against pinned peer `1fccaa746df6cd44f1ddf8c2ec5cf6ea9f18b1cb`).
  - `docker` (job `105082029583`): **SUCCESS** (wheel-binding to the regenerated manifest `fceadc37…`, label check, content scan, hardening, operations, teardown).
  - No failed/cancelled/pending/missing required check at the implementation head.
- Report head: the CI run is triggered by this report-only commit (SELF). At
  drafting time it had just been triggered (PENDING). Per protocol section 8,
  report-head check states are verified by strategy. The report file is
  under `oap/`, which is excluded from both the wheel and the sdist, so the
  artifacts rebuilt at the report head are byte-equal to the
  implementation-head rebuilds (wheel `fceadc37…`, sdist `72de29c9…`); the
  E3 gate's `git_commit`-ancestor check passes because the committed
  `git_commit` (`69e0821…`) is a strict ancestor of the report head; the
  expected report-head outcome is all three required checks `success`.

### E6 — 012-b/012-a evidence carries at the final head — MET
Criteria remaining satisfied by the (otherwise unchanged) state:
- 012-b: D1 (R1 applied), D2 (R2 applied), D3 (R3 applied) — their
  statements remain in place and are now citation-stable (T3–T5 replace only
  the unstable citations, preserving the exact wheel transition statement
  and the runtime-source byte-identity scoping); D5 (residual false-claim
  scan) — the `byte-identical`/`byte-identity` scan at the final head shows
  zero artifact byte-identity claims about 011-vs-012 (only the runtime-source
  and contract-surface statements, plus historical records); D7 (evidence
  carries) — see re-run set below; D8 (no publication/mutation) — see E7.
- 012-a (as re-adjudicated by strategy): C1 (pin updated, gate green at new
  pin — `gateway-contract` SUCCESS against `1fccaa746…`), C2 (contract-surface
  identity — unchanged, blob-level proof stands), C3 as re-adjudicated (no
  runtime source byte change; wheel runtime files byte-identical per E2;
  build reproducible — clean rebuild wheel hash = manifest hash; regenerated
  Objective-012 manifest is the only future cutover authority; 011-a record
  historical; verified-clean property holds — `artifact_policy_check.py
  --inspect` `ok: true`, `violations: []`), C4 (Dockerfile + state machine
  unchanged — `--self-test` `ok: true`; `docker` CI green), C5 (topology
  manifest byte-identical to base — `e860e0b..2838935` empty diff for that
  path; `--self-test` `ok: true`), C6 (documentation truthfulness — carried
  forward, exact-phrase scans zero matches), C8 (protected host before/after
  identical — table below), C9 (no publication/mutation — E7), C10 (freeze
  held — E4).
- Cheap re-verification re-run at the final head (local, protected host,
  repo venv via `uv`, locked/frozen):
  - `uv run --frozen pytest -q`: PASSED — `1087 passed, 26 skipped in 117.67s`, 0 failed (the E3 gate among the passes). All 26 skips are the standing environment-conditional skips (18 x `SLAIF_GATEWAY_ROOT is required`, 7 x `set SLAIF_LIVE_TEST=1`, 1 x human-activated mutually-exclusive protected vision fixture) — the same standing set as at base. (CI runner records 1086/27 — one additional standing environment-conditional skip there; identical to the last fully-green baseline at `ef79060…`, run `35180803133`.)
  - `uv run --frozen ruff check .`: PASSED (All checks passed!)
  - `uv run --frozen ruff format --check .`: PASSED (349 files already formatted)
  - `uv run --frozen mypy src tests` (CI-equivalent throwaway venv `--extra dev`, mirroring the CI `test` job): PASSED (Success: no issues found in 70 source files)
  - `uv run --frozen python -m compileall -q src tests oap/bin scripts`: PASSED
  - `uv run --frozen python scripts/cutover_state_machine.py --self-test`: PASSED (`{"lan_rollback_points_checked": 8, "ok": true, "pre_final_mutators": 4, "rollback_points_checked": 8, "transitions": 9}`)
  - `uv run --frozen python scripts/topology_qualification.py --self-test`: PASSED (`ok: true`; full decision table, fresh-namespace probe with listener-absent cleanup proof, host-namespace probe, manifest conformance)
  - `uv run --frozen python scripts/artifact_policy_check.py --dist <clean rebuild> --inspect`: PASSED (`ok: true`, `violations: []`; wheel 26 entries / 20 package files / `fceadc37…` / 83097 B; sdist 105 entries / `72de29c9…` / 425885 B)
  - `uv run --frozen python scripts/gateway_contract.py --emit-github-output <out>`: PASSED (`fixture: valid`, 7 fields, `gateway_commit=1fccaa746df6cd44f1ddf8c2ec5cf6ea9f18b1cb`, server `local-coding-v1` v2 `process_local_inclusive_horizon_fail_closed`, client `codex-0149-responses-v1` v4)
  - C6 exact-phrase scan at the final head (`git grep -nE "this PR|pre-merge|open PR" 2838935… -- README.md docs/ oap/COMPLETENESS.md`): PASSED (zero matches)
  - Stale-pin audit at the final head (`git grep -n 65666f58 2838935… -- . ':!oap'`): PASSED — exactly the four audited locations, none presented as current.

### E7 — No publication/mutation — MET (re-verified at report time)
- `git ls-remote --tags origin`: 0 tags; GitHub releases: 0.
- `release-image.yml` (workflow_dispatch-only, push-capable): 0 runs for
  `oap/012-gateway-peer-repin`; no docker push performed locally.
- `ulfe-lmi/slaif-api-gateway` unmodified (read-only queries only):
  default branch `main` = `1fccaa746df6cd44f1ddf8c2ec5cf6ea9f18b1cb` at
  report time — exactly the pinned peer, unchanged.
- No live profile/route/service change: C8 before/after probes identical
  (below).
- `oap/orders/*` and prior `oap/reports/*` byte-identical to the 012-b
  state; the 012-a/012-b reports remain immutable history.

## Verification
Local (protected host, repo venv via `uv`, locked/frozen) — exact commands
and results recorded under E1, E2, E6. Additional:
- GitHub read-only reconciliation at round start: PASSED — PR #14 OPEN
  non-draft, base `main` @ `e860e0b…`, head `1c6c6b3…` (order-time head),
  exactly one open PR.
- GitHub after push: PASSED — PR #14 head advanced to
  `283893548881c8e5c3c144540ab7fe0d673d0210`, `MERGEABLE`, no new PR.
- Clean rebuild (`uv build --out-dir <throwaway>`) at the final state +
  `sha256sum`: wheel `fceadc378130dd4ffcc3f75d17b5e098577652914f541245d31247911be23aeb`
  (83097 B); sdist `72de29c9e60a012425e1c0d0d351ce7ff9c985b1f3b28c3525987a4f70db1c12`
  (425885 B, 105 entries) — recorded in the regenerated manifest and above.

## Live model/service evidence
No Qwen/vLLM inference call of any kind was made. Protected-host read-only
status probes only (before = at round start, after = before report
publication):

| Item | Before | After | Identical |
| --- | --- | --- | --- |
| `qwen-serving-vision.service` ActiveState/SubState | active/running | active/running | yes |
| MainPID | 23961 | 23961 | yes |
| Start (ExecMainStartTimestamp) | Sun 2026-09-06 18:57:26 CEST | Sun 2026-09-06 18:57:26 CEST | yes |
| `127.0.0.1:18020/health` | 200 | 200 | yes |
| listeners on 18020/18021/18031-18034 | only `0.0.0.0:18020` | only `0.0.0.0:18020` | yes |
| `~/.codex/qwen-neumann.config.toml` mode/mtime | 600 / 2026-09-13 11:59:21.852183775 +0200 | 600 / 2026-09-13 11:59:21.852183775 +0200 | yes |
| `Linger` (user janezp) | no | no | yes |
| `docker ps -a` (read-only) | 3 exited containers (2 years old, no published ports): `beautiful_cartwright`, `beautiful_haibt`, `kind_brown` | same 3, same states | yes |
| `docker images` (read-only) | `postgres:16`, `hello-world:latest`, `chrockey/fpt-votenet:v0.1.0` | same 3 | yes |
| slaif-named containers/images | 0 | 0 | yes |

## GitHub CI / required checks
- Implementation head `283893548881c8e5c3c144540ab7fe0d673d0210`: run
  `35183999924` — `test` SUCCESS (job `105082029464`; 1086 passed, 27
  skipped; E3 gate passing), `gateway-contract` SUCCESS (job
  `105082029566`, pinned peer `1fccaa746…`), `docker` SUCCESS (job
  `105082029583`). All required green at drafting: yes (implementation
  head).
- Report head: run triggered by this report-only commit (SELF); at drafting
  time it had just been triggered (PENDING); states verified by strategy
  per protocol section 8 (report-head checks may be pending at signal time).
  Prior heads (historical): `c384150…` run 35182393796 (the 012-b E3-gate
  failure this order resolves), `1c6c6b3…` run 35182846809 (same pattern).

## Local setup/dependencies
- Existing repo venv (Python 3.12.3, uv 0.12.5) used frozen: `uv run
  --frozen …` for all commands.
- Clean rebuild via `uv build --out-dir <throwaway>` into a throwaway
  directory; manifest regenerated against that throwaway dist; no durable
  `dist/` change.
- Throwaway CI-equivalent venv (`UV_PROJECT_ENVIRONMENT=/tmp/slaif-012c-ci-venv`,
  `uv sync --frozen --extra dev`) for mypy parity with the CI `test` job;
  throwaway emit-output file in `/tmp`; no leftover checkouts/containers/
  services of consequence (throwaway dist/venv paths left in `/tmp` as
  non-durable scratch).
- Passwordless sudo used only for the read-only `docker ps -a` /
  `docker images` C8 probes and the topology self-test's fresh-namespace
  probe (both read-only/ephemeral). No durable docs/config changed beyond
  T1–T6.

## Documentation
Updated (exactly the ordered scope): `docs/RELEASE-ARTIFACT-POLICY.md`
(T3), `docs/RELEASE-CUTOVER-RUNBOOK.md` (T4), `docs/IMPLEMENTATION-ROADMAP.md`
(T5), plus the T1/T2 generator/test objective advancement and the T6
regenerated manifest. Not updated (deliberately, per non-goals): fixture,
Dockerfile, state machine, CI workflows, `docs/topology.manifest.json`,
`src/`, `uv.lock`, `pyproject.toml`, and all other docs.

## Safety/scope confirmations
- Unrelated files: pre-existing local modification `oap/runtime.env.example`
  (coding/strategic profile names, set by the strategy operator) and
  untracked zero-byte scratch files `Local`, `clean`, `unchanged` were
  preserved in the working tree and NOT committed; no other unrelated changes.
- Secrets/raw content: none in the diff, PR, or report (SHAs, blob IDs,
  ports, and standard protected-host status values only; no credential
  values, no raw payloads).
- Production/protected resources: no production systems/data touched.
- Protected 18020/Qwen/Codex fixture changed: NO (read-only probes only;
  before/after identical).
- Required tests skipped/not run: only the standing environment-conditional
  skips listed under E6 (identical set to base; CI records one additional
  standing skip there); no required test was skipped to get green.
- Scope deviation: none. Round diff is exactly T1–T6 + 012-c transcripts
  (+ this report).
- Extra objective PR: NO (exactly one PR, #14, amended). Coding merge: NO.
  Auto-merge: not enabled (`autoMergeRequest: null` verified).
- Active/order edited: NO (`oap/active` and the order file committed as
  unchanged strategic bytes; all pre-existing `oap/orders`/`oap/reports`
  files byte-identical to the 012-b state).
- Report commit report-only: yes (this commit stages only
  `oap/reports/012-c-manifest-regen-and-citation-stability.md`).
- This report supersedes the 012-b report as the Objective-012 report of
  record; the 012-a and 012-b reports remain immutable history.

## Known limitations/blockers
- Report-head CI: at drafting time the report-head run had just been
  triggered (PENDING) and its final states are verified by strategy per
  protocol section 8; the expected outcome is all three required checks
  `success` (the report file is under `oap/`, excluded from both artifacts,
  and the E3 `git_commit`-ancestor check passes). No other limitations or
  blockers.

## Recommended strategic follow-up
Factual only; strategy decides:
1. Verify the report-head CI run (triggered by this report commit) is green
   per protocol section 8; no further coding work is indicated by this
   round's evidence.

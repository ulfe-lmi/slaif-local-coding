# OAP Coding-Agent Report — 012-b

## Work order
- Identifier: `012-b`; order path: `oap/orders/012-b-artifact-identity-doc-truth.md`; numeric objective `012`
- PR mode: `AMENDED_EXISTING_PR`

## Status
PARTIAL

Rationale (single blocking fact): the order is internally contradictory between its
explicit non-goals ("NO functional change: … manifest … remain exactly as at
implementation head `ef79060…`"; "NO new artifact build or hash change (the
manifest keeps `fceadc37…` / `910b65db…`)") and D6 (CI `test` job green at the new
implementation head). The ordered R1–R3 doc edits change three files that are build
inputs of the sdist (`docs/` is in the sdist whitelist), so the repository's own E3
regeneration/drift gate (`tests/test_release_provenance_manifest.py::test_committed_manifest_matches_regenerated`)
necessarily fails at the new head while the manifest stays frozen. Every other
acceptance criterion is met with exact evidence below. Regenerating the manifest
(or weakening the gate) was both explicitly prohibited and out of my authority; I
did not silently choose, per the ambiguity rule.

## Executive summary
R1–R3 documentation corrections were executed exactly as ordered and pushed to the
same branch of PR #14 (no new PR): the false 011-vs-012 artifact byte-identity
statements in `docs/RELEASE-ARTIFACT-POLICY.md` and `docs/RELEASE-CUTOVER-RUNBOOK.md`
were replaced with the true, hash-exact statements, and the roadmap "Current state"
paragraph now records Objective 012. All 012-a criteria that rest on the unchanged
implementation state (C1, C2, C4, C5, C6 as carried forward, the adjudicated C3,
C8, C9, C10) remain satisfied — re-verified with the cheap command set at the final
head. The only CI deviation at the new implementation head is exactly one failed
assertion — the E3 manifest gate — caused by the order's own frozen-manifest
non-goal meeting the sdist-carrying doc edits; the `gateway-contract` and `docker`
required checks pass at the implementation head. No merge, no release, no cutover,
no protected-host mutation, no OAP history rewrite.

## Authoritative GitHub state
- Repository: `ulfe-lmi/slaif-local-coding`
- PR: #14 — https://github.com/ulfe-lmi/slaif-local-coding/pull/14 — `OPEN`, non-draft,
  the only open PR and exactly the Objective-012 PR (verified at round start and at push)
- Base: `main` @ `e860e0bff687afded7782fb2687b5b435792459a` (verified unchanged on GitHub at round start)
- Head branch: `oap/012-gateway-peer-repin` (unchanged, as required)
- Head at order time: `91830765c9d8734c3729d21cb686fbb586fc5ad1` (012-a report commit);
  prior implementation head: `ef790602e64c097ae5ed2fe4b341eff608c1cfe7`
- Implementation head SHA: `c384150cbc83c8c5d463b6b855fe20a5fe11a746`
- Report publication commit: SELF
- Implementation commits pushed before report: exactly one —
  `c384150cbc83c8c5d463b6b855fe20a5fe11a746` (R1–R3 + 012-b transcript), parent `91830765c9d8734c3729d21cb686fbb586fc5ad1`
- New PR this round: no; amended existing: yes (#14); merge performed: NO

## Changes and files
Round commit `c384150` (parent `9183076`) changes exactly 5 files:

| File | Change | +/- |
| --- | --- | --- |
| `docs/RELEASE-ARTIFACT-POLICY.md` | R1 — false byte-identity sentence replaced with the true hash-exact statement | 14/4 |
| `docs/RELEASE-CUTOVER-RUNBOOK.md` | R2 — Preconditions item 2 reworded to runtime-source byte-identity with artifact-byte caveat + pointer | 4/2 |
| `docs/IMPLEMENTATION-ROADMAP.md` | R3 — "Current state" paragraph extended with the Objective-012 record | 9/2 |
| `oap/active` | transcript (strategic bytes as found: `012-a` -> `012-b`) | 1/1 |
| `oap/orders/012-b-artifact-identity-doc-truth.md` | transcript (activated order, new file, committed byte-unchanged) | 186/0 |

Diff vs prior implementation head `ef79060…` additionally shows only
`oap/reports/012-a-gateway-peer-repin.md` (added by the prior round's report commit
`9183076…`; immutable history, not a change of this round). No other path differs.

## R1–R3 diff evidence
R1 (`docs/RELEASE-ARTIFACT-POLICY.md`, "Cutover artifact authority and supersession"):
the sentence "…with no runtime package byte change: the cleared rebuild proves the
artifact set is byte-identical to the Objective-011-a record (same wheel and sdist
SHA-256s), and the only OCI build input…" is gone and replaced by: "…with no runtime
source byte change: the entry-level diff of the cleared rebuild proves all 20 wheel
runtime files byte-identical to the Objective-011 record (only `dist-info/METADATA`
and `dist-info/RECORD` differ); the artifact bytes changed ONLY because (a) the
Objective-012-mandated README status-row fix is embedded in the wheel
`dist-info/METADATA` long description (`readme = "README.md"`; wheel
`7cede0b8e930463400a40662248a97aae22f75b0512dcd8151d6122a99157166` ->
`fceadc378130dd4ffcc3f75d17b5e098577652914f541245d31247911be23aeb`, +27 B) and (b)
the sdist carries the in-scope `README.md`/`docs/`/`tests/` text changes (sdist
`4ba17680c55c557494593087f4d632abb6a79f0c595ecab08bb2414abc86f5d6` ->
`910b65db8abe331fb1ad0507697c1e089fd9ea4ede2ec1792b7fac5c8f5c1240`); the only OCI
build input that changes is the Dockerfile `SLAIF_GATEWAY_PEER_SHA` label input;
the regenerated Objective-012 manifest is the **only** future cutover authority, and
the Objective-011-a artifact record (wheel `7cede0b8…` / sdist `4ba17680…`) remains
the accepted Objective-011 record only."

R2 (`docs/RELEASE-CUTOVER-RUNBOOK.md`, Preconditions item 2): "with artifact bytes
proven identical to the Objective-011-a set" replaced by "with runtime source proven
byte-identical to the Objective-011-a set (artifact bytes differ only via the
embedded README METADATA and the sdist-carried in-scope text files; see
RELEASE-ARTIFACT-POLICY.md)". No other runbook change.

R3 (`docs/IMPLEMENTATION-ROADMAP.md`, "Current state (2026-09-17, verified against
GitHub)" paragraph, no new sections): appended before the closing "Cutover NOT
performed; NOT released.": "Objective 012 (2026-09-17) re-pinned the current Gateway
peer to `1fccaa746df6cd44f1ddf8c2ec5cf6ea9f18b1cb` (contract surface byte-identical,
proven at the blob level), regenerated the release provenance manifest
(`objective: "012-a"`; wheel `fceadc378130dd4ffcc3f75d17b5e098577652914f541245d31247911be23aeb`
/ sdist `910b65db8abe331fb1ad0507697c1e089fd9ea4ede2ec1792b7fac5c8f5c1240`; artifact
record per `RELEASE-ARTIFACT-POLICY.md`), and closed the post-011 documentation
drift." No "this PR"/"pre-merge" language; the stale pin `65666f58…` is not
presented as current anywhere (audit below).

## Acceptance evidence

### D1 — R1 applied — MET
The exact false sentence is gone (verified by absence scan). The replacement carries
the four exact hash values (`7cede0b8e930463400a40662248a97aae22f75b0512dcd8151d6122a99157166`,
`fceadc378130dd4ffcc3f75d17b5e098577652914f541245d31247911be23aeb`,
`4ba17680c55c557494593087f4d632abb6a79f0c595ecab08bb2414abc86f5d6`,
`910b65db8abe331fb1ad0507697c1e089fd9ea4ede2ec1792b7fac5c8f5c1240`), the
entry-level-diff proof summary (all 20 wheel runtime files byte-identical to the
Objective-011 record; only `dist-info/METADATA` and `dist-info/RECORD` differ), and
the cutover-authority chain (regenerated Objective-012 manifest = only future
cutover authority; Objective-011-a record = accepted 011 record only).

### D2 — R2 applied — MET
Preconditions item 2 now states runtime-source byte-identity with the artifact-byte
caveat and the pointer to `RELEASE-ARTIFACT-POLICY.md`; no other runbook change
(diff shows only the 2 replaced lines).

### D3 — R3 applied — MET
"Current state" paragraph includes the truthful 012 record (re-pin with current pin
`1fccaa746df6cd44f1ddf8c2ec5cf6ea9f18b1cb`, manifest regeneration with
`objective: "012-a"` and the R1 artifact record, post-011 documentation drift
closed, cutover NOT performed, NOT released). No "this PR"/"pre-merge" language
(exact-phrase scan below: zero matches). No literal stale pin presented as current
(only the four audited provenance/historical/as-of occurrences of `65666f58…` remain,
unchanged from 012-a). Paragraph style/length discipline kept; no new sections.

### D4 — No other file changed — MET
`git diff c384150^..c384150 --name-status` = exactly the 5 files above (R1–R3 +
`oap/active` + the 012-b order transcript). `git diff ef79060..c384150 --name-status`
= those 5 files plus `oap/reports/012-a-gateway-peer-repin.md`, which was committed
in the prior round's report commit `9183076…` (immutable, not a change of this
round). No `src/`, no `uv.lock`, no `pyproject.toml`, no fixture/manifest/Dockerfile/
state-machine/generator/test/CI change (full `ef79060..c384150` name-only diff
restricted to those paths is empty).

### D5 — Residual false-claim scan — MET
Exact-phrase scan at the implementation head (`git grep -n -E
"byte-identical|byte-identity|bytes proven identical" c384150… -- README.md docs/ oap/COMPLETENESS.md`):

```text
README.md:126:byte-identical request-only fixtures; top-level `instructions` was absent and is
docs/DEPLOYMENT.md:278:restored configuration is byte-identical to the backup
docs/IMPLEMENTATION-ROADMAP.md:25:`1fccaa746df6cd44f1ddf8c2ec5cf6ea9f18b1cb` (contract surface byte-identical,
docs/OAP-RUNBOOK.md:96:  only when the existing matching target is byte-identical to source; otherwise
docs/OAP-RUNBOOK.md:146:(byte-identical SHA-256 read-back) and never overwritten; unsafe
docs/RELEASE-ARTIFACT-POLICY.md:130:remained byte-identical**. Objective 010 adds a runtime configuration
docs/RELEASE-ARTIFACT-POLICY.md:133:byte-identical to the Objective-009 wheel and the current manifest records
docs/RELEASE-ARTIFACT-POLICY.md:147:proves all 20 wheel runtime files byte-identical to the Objective-011
docs/RELEASE-CUTOVER-RUNBOOK.md:54:| `gateway.authority_sha` | … the three contract source files are byte-identical between the old and new pins) |
docs/RELEASE-CUTOVER-RUNBOOK.md:86:   `objective: "012-a"`, with runtime source proven byte-identical to the
docs/RELEASE-CUTOVER-RUNBOOK.md:208:   is byte-identical to the live file at backup time.
docs/RELEASE-CUTOVER-RUNBOOK.md:219:profile file from the backup and verify byte-identity.
docs/RELEASE-CUTOVER-RUNBOOK.md:301:- T6⁻¹ (profile restore) is verified byte-identical to the backup;
docs/RELEASE-CUTOVER-RUNBOOK.md:318:verify the restored state equals `S0` (byte-identical profile file,
docs/SLAIF-GATEWAY-INTEGRATION.md:85:  three contract source files the gate validates are byte-identical
docs/TOPOLOGY.md:64:  `gateway-contract` gate validates are byte-identical (GitHub blob SHAs)
docs/TOPOLOGY.md:123:`gateway-contract` gate validates are byte-identical (GitHub blob SHAs)
```

Disposition: zero remaining artifact byte-identity claims about 011-vs-012. The two
new statements (POLICY:147, RUNBOOK:86) are runtime-source scoped; ROADMAP:25 and the
four contract-surface lines (RUNBOOK:54, INTEGRATION:85, TOPOLOGY:64/123) are
contract-source-file scoped; POLICY:130/133 are the historical Objective-009/010
record; all other hits concern fixtures, backups, transcripts, or profile files —
not release artifacts.

### D6 — CI green at new implementation head AND report head — NOT MET (blocking)
- Implementation head `c384150…`: CI run `35182393796` —
  - `test` (job `105077175017`): **FAILURE** — `1 failed, 1085 passed, 27 skipped in 63.09s`; the single failure is `tests/test_release_provenance_manifest.py::test_committed_manifest_matches_regenerated` (E3 regeneration/drift gate): committed sdist hash `910b65db…` vs regenerated `0cf24290…`; wheel matches (`fceadc37…`).
  - `gateway-contract` (check run `105077174882`): SUCCESS (against pinned peer `1fccaa746…`).
  - `docker` (check run `105077175040`): SUCCESS (wheel-binding to the manifest `fceadc37…`, label check, content scan, hardening, operations, teardown).
- The previous green CI baseline at `ef79060…` (run `35180803133`, `test` job) recorded `1086 passed, 27 skipped`; at `c384150…` the only count delta is that single E3 test flipping passed -> failed. The gate fails because R1–R3 edit sdist build inputs while the order's non-goals freeze the manifest's sdist hash; with the manifest frozen, no in-scope repair exists (regenerating the manifest and/or weakening the gate are both prohibited by this order and outside my authority).
- Report-head run: triggered by the report-only commit (SELF); states verified by
  strategy per protocol section 8 (see "GitHub CI / required checks").
- D6 therefore is unattainable under the order as written; see Known limitations.

### D7 — 012-a evidence carries at the unchanged implementation state — MET (with one exact FAILED label in the re-run set)
Criteria of the 012-a report remaining satisfied by the unchanged implementation
state (everything except the three R1–R3 doc files is byte-identical to
`ef79060…`):
- C1 (pin updated, gate green at new pin): MET — fixture/pin unchanged; `gateway-contract` CI job SUCCESS at `c384150…` against `1fccaa746…`; `--emit-github-output` re-run below.
- C2 (contract-surface identity): MET — unchanged; the blob-level proof (three contract source files, identical GitHub blob SHAs at both pins) stands; no re-query needed (no change).
- C4 (Dockerfile + state machine): MET — unchanged; `cutover_state_machine.py --self-test` re-run `ok: true`; `docker` CI job green (wheel-binding to `fceadc37…`).
- C5 (topology manifest untouched): MET — `docs/topology.manifest.json` byte-identical to base (empty diff `e860e0b..c384150` for that path); `topology_qualification.py --self-test` re-run `ok: true`.
- C6 (documentation truthfulness): carried forward — the two false statements this round corrects were the only remaining 011-vs-012 artifact-identity defects (per the order's strategic context); the "this PR"/"pre-merge"/"open PR" exact-phrase scan at the final head returns zero matches (re-run below).
- C3 as re-adjudicated: MET — no runtime source byte change (zero `src/` files in any diff this round; wheel runtime files byte-identical — rebuilt wheel hash equals the 011->012 record chain's runtime set and the manifest's `fceadc37…` exactly); build deterministic/reproducible (clean rebuild wheel hash = manifest hash); regenerated Objective-012 manifest is the only future cutover authority and the 011-a record is historical; verified-clean property holds (re-run below `ok: true`, `violations: []`).
- C8 (protected host before/after identical): MET — re-probed before and after this round; all C8 items identical (table in "Live model/service evidence").
- C9 (no publication/mutation): MET — re-verified at report time (see D8).
- C10 (freeze held): MET — at `c384150…`: `uv.lock` SHA-256 `1237cbd179f71b99984c80f927529549f5e61eb705585ef9cf2ab0fa9e26764a` and `pyproject.toml` SHA-256 `af91f82283882f1e51ee763d635f94f1ae2534c51585c837aa61cff8a2f7dda2` (equal to the base values); zero `src/` files changed; no version bump; `scripts/gateway_contract.py` untouched.

Cheap re-verification re-run at the final head (local, protected host, repo venv via `uv`, locked/frozen):
- `uv run --frozen pytest -q`: FAILED — `1 failed, 1086 passed, 26 skipped in 114.12s`; the single failure is the E3 gate `test_committed_manifest_matches_regenerated` (D6 root cause; committed sdist `910b65db…` vs regenerated `0cf24290…`; wheel `fceadc37…` matches). All 26 skips are the standing environment-conditional skips (18 x `SLAIF_GATEWAY_ROOT is required`, 7 x `set SLAIF_LIVE_TEST=1`, 1 x human-activated mutually-exclusive protected vision fixture) — the same standing set as at base.
- `uv run --frozen ruff check .`: PASSED (All checks passed!)
- `uv run --frozen ruff format --check .`: PASSED (347 files already formatted)
- `uv run --frozen mypy src tests` (CI-equivalent throwaway venv `--extra dev` only, mirroring the CI `test` job): PASSED (Success: no issues found in 70 source files)
- `uv run --frozen python -m compileall -q src tests oap/bin scripts`: PASSED
- `uv run --frozen python scripts/cutover_state_machine.py --self-test`: PASSED (`{"lan_rollback_points_checked": 8, "ok": true, "pre_final_mutators": 4, "rollback_points_checked": 8, "transitions": 9}`)
- `uv run --frozen python scripts/topology_qualification.py --self-test`: PASSED (`ok: true`; full decision table, fresh-namespace probe with listener-absent cleanup proof, host-namespace probe, manifest conformance)
- `uv run --frozen python scripts/artifact_policy_check.py --dist <clean rebuild> --inspect`: PASSED (`ok: true`, `violations: []`; wheel 26 entries / 20 package files / `fceadc37…` / 83097 B; sdist 105 entries / `0cf24290…` / 425800 B)
- `uv run --frozen python scripts/gateway_contract.py --emit-github-output <out>`: PASSED (`fixture: valid`, 7 fields, `gateway_commit=1fccaa746df6cd44f1ddf8c2ec5cf6ea9f18b1cb`, server `local-coding-v1` v2 `process_local_inclusive_horizon_fail_closed`, client `codex-0149-responses-v1` v4)
- C6 exact-phrase scan at the final head (`git grep -nE "this PR|pre-merge|open PR" c384150… -- README.md docs/ oap/COMPLETENESS.md`): PASSED (zero matches)
- Stale-pin audit at the final head (`git grep -n 65666f58 c384150… -- .` excluding `oap/`): PASSED — exactly the four audited locations (INTEGRATION:83 provenance clause; TOPOLOGY:61 re-pin provenance; TOPOLOGY:102 dated 010-era inspection record; topology.manifest.json:135 as-of snapshot), none presented as current.

### D8 — No publication/mutation — MET (re-verified at report time)
- `git ls-remote --tags origin`: 0 tags; GitHub releases: 0.
- `release-image.yml` (workflow_dispatch-only, push-capable): 0 runs for `oap/012-gateway-peer-repin`; no docker push performed locally.
- `ulfe-lmi/slaif-api-gateway` unmodified (read-only queries only): default-branch main = `1fccaa746df6cd44f1ddf8c2ec5cf6ea9f18b1cb` at report time — exactly the new pin, unchanged.
- No live profile/route/service change: C8 before/after probes identical (below).
- `oap/orders/*` and prior `oap/reports/*` byte-identical to base; the 012-a report untouched.

## Verification
Local (protected host, repo venv via `uv`, locked/frozen) — exact commands and
results recorded under D7. Additional:
- Clean rebuild (`uv build --out-dir <throwaway>`) at the final head: PASSED for
  wheel invariance — wheel `fceadc378130dd4ffcc3f75d17b5e098577652914f541245d31247911be23aeb`
  (83097 B) equals the manifest's wheel hash exactly; sdist
  `0cf2429079b9a68e9e9920134b55771c2aa2c7bef53a662e953d7c1b6676fcbe` (425800 B,
  105 entries) reflects the R1–R3 text changes in the sdist-carrying `docs/` files
  (the D6/E3 root cause; manifest deliberately untouched per the order's non-goals).
- GitHub read-only reconciliation at round start: PASSED — PR #14 OPEN non-draft,
  base `main` @ `e860e0b…`, head `9183076…`, exactly one open PR, branch CI runs
  35180569497/35180803133/35181109398 all completed/success.
- GitHub after push: PASSED — PR #14 head advanced to `c384150…`, mergeable, no new PR.

## Live model/service evidence
No Qwen/vLLM inference call of any kind was made. Protected-host read-only status
probes only (before = at round start, after = before report publication):

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

Context (explicitly outside the C8 item list, as in 012-a): `zap-it-lan.service`
was active/running in both probes; its MainPID cycled between probes
(2786501 -> 2789589) consistent with its observed auto-restart behavior and does not
affect any C8 item.

## GitHub CI / required checks
- Implementation head `c384150…`: run `35182393796` — `test` FAILURE (job `105077175017`; single E3-gate assertion; 1 failed, 1085 passed, 27 skipped), `gateway-contract` SUCCESS (check run `105077174882`, pinned peer `1fccaa746…`), `docker` SUCCESS (check run `105077175040`).
- Prior heads (historical, all green): `9a6edc6…` run 35180569497, `ef79060…` run 35180803133 (`test`: 1086 passed, 27 skipped), `9183076…` run 35181109398.
- All required green at drafting: NO — the `test` job fails at the implementation head by the single E3-gate assertion described in D6; no failed/cancelled/missing check beyond it; no in-scope repair exists without violating the order's non-goals.
- Report-head run: triggered by the report-only commit (SELF) that publishes this
  report; at drafting time it had just been triggered and its check states are
  verified by strategy per protocol section 8 (report-head checks may be pending at
  signal time). The report file is under `oap/`, which is excluded from both the
  wheel and the sdist, so the artifacts rebuilt at the report head are byte-equal to
  the implementation-head rebuilds (wheel `fceadc37…`, sdist `0cf24290…`); the
  expected report-head outcome is the same single E3-gate assertion failing in `test`
  with `gateway-contract` and `docker` succeeding.

## Local setup/dependencies
- Existing repo venv (Python 3.12) used frozen: `uv run --frozen …` for all commands; `uv build --out-dir <throwaway>` for the rebuild.
- Throwaway CI-equivalent venv (`UV_PROJECT_ENVIRONMENT=/tmp/slaif-012b-ci-venv`, `uv sync --frozen --extra dev`) for mypy parity with the CI `test` job; removed after use (no durable state).
- Throwaway dist directory and throwaway emit-output file in `/tmp`; no leftover checkouts/containers/services.
- Passwordless sudo used only for the read-only `docker ps -a` / `docker images` C8 probes. No durable docs/config changed beyond R1–R3.

## Documentation
Updated (exactly the ordered scope): `docs/RELEASE-ARTIFACT-POLICY.md` (R1),
`docs/RELEASE-CUTOVER-RUNBOOK.md` (R2), `docs/IMPLEMENTATION-ROADMAP.md` (R3).
Not updated (deliberately, per non-goals): manifest, fixture, Dockerfile, state
machine, generator, tests, CI, `src/`, `uv.lock`, `pyproject.toml`, and all other docs.

## Safety/scope confirmations
- Unrelated files: pre-existing local modification `oap/runtime.env.example` (coding/strategic profile names) and untracked zero-byte scratch files `Local`, `clean`, `unchanged` were preserved in the working tree and NOT committed; no other unrelated changes.
- Secrets/raw content: none in the diff, PR, or report (SHAs, blob IDs, ports, and standard protected-host status values only; no credential values, no raw payloads).
- Production/protected resources: no production systems/data touched.
- Protected 18020/Qwen/Codex fixture changed: NO (read-only probes only; C8 before/after identical).
- Required tests skipped/not run: only the standing environment-conditional skips listed under D7 (identical set to base); no required test was skipped to get green.
- Scope deviation: none. One order contradiction was discovered and is reported (D6); no prohibited action was taken to work around it.
- Extra objective PR: NO (exactly one PR, #14, amended). Coding merge: NO. Auto-merge: not enabled.
- Active/order edited: NO (`oap/active` and the order file committed as unchanged strategic bytes; all pre-existing `oap/orders`/`oap/reports` files byte-identical to base).
- Report commit report-only: yes (this commit stages only `oap/reports/012-b-artifact-identity-doc-truth.md`).
- This report supersedes the 012-a report as the Objective-012 report of record; the 012-a report remains immutable history.

## Known limitations/blockers
- BLOCKING (strategic adjudication required): D6 vs the order's own non-goals. R1–R3
  edit three `docs/` files that are sdist build inputs; with the manifest frozen at
  the 012-a record (sdist `910b65db…`), the E3 gate
  (`test_committed_manifest_matches_regenerated`) fails deterministically at any head
  containing R1–R3 (local: `0cf24290…` rebuilt sdist vs `910b65db…` committed; CI
  `test` job failure observed at `c384150…`). Satisfying D6 requires either
  regenerating the manifest from the new head (prohibited: "NO new artifact build or
  hash change"; the wheel/cutover authority is unaffected — only the developer-only,
  non-authority sdist record would advance) or a build-configuration/gate change
  (also prohibited). The coding agent does not choose between them.
- The `test` job therefore stays red on PR #14 until strategy issues a corrective
  direction; `gateway-contract` and `docker` are green at the implementation head.
- Factual note: at report time `ulfe-lmi/slaif-api-gateway` main =
  `1fccaa746df6cd44f1ddf8c2ec5cf6ea9f18b1cb` (the pinned peer), unchanged.

## Recommended strategic follow-up
Factual only; strategy decides:
1. Adjudicate the D6/non-goal conflict: e.g., authorize a follow-up round to
   regenerate `packaging/release_provenance_manifest.json` from the accepted 012-b
   head (sdist record -> `0cf2429079b9a68e9e9920134b55771c2aa2c7bef53a662e953d7c1b6676fcbe`,
   425800 B, 105 entries; wheel remains `fceadc378130dd4ffcc3f75d17b5e098577652914f541245d31247911be23aeb`;
   the cutover-authority wheel is unchanged), or direct an alternative.
2. No other follow-up is indicated by this round's evidence.


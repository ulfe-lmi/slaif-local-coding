# OAP Coding-Agent Report — 013-b

## Work order
- Identifier: `013-b`; order path: `oap/orders/013-b-repin-peer-and-complete-publication.md`; numeric objective `013`
- PR mode: AMENDED_EXISTING_PR — PR #15 (the single objective PR, created by 013-a); NO NEW PR
- Round state: wrapper-consumed control `OK` at round start; this is the final report of the round
- The 013-a order and 013-a report remain in force and byte-immutable (verified: the 013-b commit chain touches neither `oap/orders/013-a-mvp-release-publication.md` nor `oap/reports/013-a-mvp-release-publication.md`)

## Status
**BLOCKED** — at B8 (release workflow → registry push). Workstreams B1–B7 are
**COMPLETE** with CI fully green at the final implementation head `S''`;
B9/B10 are **NOT RUN** (depend on B8; `P` does not exist); B11 is **PARTIAL**
as written (no `P` to be the parent of). The publication failure is outside
coding authority: the repository's Actions workflow-permission ceiling.

Per workstream (013-b):
- **B1** (gateway `main` re-verification): **PASSED** (round start and report time; `08ca421…`).
- **B2** (peer re-pin): **PASSED** (fixture + one Dockerfile ARG line; contract-surface blob-identical per the order's strategic delta inspection).
- **B3** (generator `OBJECTIVE` + E3 assertion): **PASSED**.
- **B4** (`gateway-contract` gate re-proven against the NEW pin): **PASSED** (CI at `S''` 18/18 network-guard-enabled + local re-run 18/18 at report time).
- **B5** (documentation reconciled to the released truth): **PASSED** per B5's exact semantics (transient-overstatement caveat while publication is blocked: deviation 4).
- **B6** (METADATA-ONLY wheel proof): **PASSED** ((a) clean rebuild reproduces the 012 authority wheel byte-for-byte; (b) 24/26 entries identical, only README-derived METADATA/RECORD diffs; (c) `H_new` bound by CI/manifest/in-image/workflow).
- **B7** (`S''` final implementation head, CI fully green): **PASSED** (run 35208071525, all four jobs SUCCESS).
- **B8** (trigger workflow, capture `D`): **BLOCKED** — two dispatches, both FAILED at the push step: `unauthorized: access token has insufficient scopes`; root cause repo `default_workflow_permissions = "read"` clamping the declared `packages: write`. `D` not captured; registry verified clean.
- **B9** (`P` release-record commit): **NOT RUN** (no `D`; `P` does not exist).
- **B10** (CI at `P` incl. executed `docker-published`): **NOT RUN** (no `P`, no published image).
- **B11** (report `R` = child of `P`): **PARTIAL** — with no `P`, "child of `P`" is unsatisfiable; per the 013-a no-`P` precedent this report is published as the report-only child of the final non-report commit `S''` (first parent = `S''`).
- **B12** (protected-host invariance): **PASSED** (before/intermediate/after read-only probes; no docker build/run/up on the host).
- **B13** (013-a R-criteria re-affirmed at the final head): per-criterion table below (R1 PARTIAL; R2–R4, R6–R10, R14 PASSED; R5 PASSED as amended by the wheel ruling; R11 implementation PASSED / execution NOT SUCCEEDED; R12 BLOCKED; R13 PARTIAL; R15/R16 satisfied by B5 wording; R17 PASSED with caveat; R18/B1 PASSED; R19 PARTIAL — stopped at B8; R20/B12 PASSED).

## Executive summary
The 013-b round completed every pre-publication workstream on the same PR #15:
re-pinned the Gateway peer to the verified contract-identical current `main`
`08ca421…` (fixture `commit` + the single `Dockerfile` ARG line), reconciled
all release-facing documentation to the B5 released-truth semantics under the
strategic METADATA-ONLY wheel ruling, set the generator/E3 objective to
`013-b`, re-proved the strict gateway contract gate against the new pin (18/18
in CI with network guard enabled, 18/18 local), and produced `S''`
(`dfa77fb…`) carrying the not-yet-published schema-v3 manifest `M_S''`
(objective `013-b`, peer `08ca421…`, wheel `H_new` = `879baa3a…`, sdist
`73cc354c…`, `generated_from` = `S''`'s parent `8e3f07e…`). CI at `S''` was
fully green (all four jobs, run 35208071525). The round then stopped at B8:
the release workflow was dispatched at `S''` twice (runs 35208313536,
35209542430) and both runs FAILED at the registry-push step with
`unauthorized: access token has insufficient scopes` — the repository's
`default_workflow_permissions` is `"read"`, which per GitHub semantics clamps
the workflow's declared `packages: write` to the repository ceiling, so the
`GITHUB_TOKEN` issued to the dispatch-only workflow lacks GHCR push scope.
Raising that repository setting is a security-policy decision (strategy/human),
so no publication occurred: no digest `D`, no release-record commit `P`, no
Git tag, no GitHub Release. The registry was re-probed anonymous at report
time: tags `0.1.0` and `sha-dfa77fb…` both `absent` (no orphan-tag cleanup
needed). A latent bug in the frozen `scripts/release_registry_publish.py`
(push reference missing the `ghcr.io/` prefix its own docstring specifies)
was identified and is flagged to strategy (deviation 2); the file was not
modified (frozen by this order). Protected-host fixtures verified invariant
(B12).

### Literal publication facts (as of this report)
- `S''` (image source commit when published): `dfa77fb442a82754bb6af21a2e0fb0af29ddfbab`
- `D` (registry digest): **DOES NOT EXIST** (publication BLOCKED at B8; no digest captured)
- GHCR tag→digest mapping: `0.1.0` → **absent (no digest)**; `sha-dfa77fb442a82754bb6af21a2e0fb0af29ddfbab` → **absent (no digest)** — both registry-verified anonymous at report time via `scripts/ghcr_tag_check.py`
- Release-workflow run ids at `S''`: `35208313536` (2026-09-17T10:01:51Z) and `35209542430` (2026-09-17T10:15:38Z) — both FAILED at the push step
- `published_at`: **DOES NOT EXIST**
- New release wheel `H_new`: `879baa3ad19e0f513090add965d267957d27f7bcd904d1e225586d76126f8b19` (83,352 B; METADATA-ONLY proof in B6)
- 012 authority wheel (reproduced byte-for-byte in the clean rebuild): `fceadc378130dd4ffcc3f75d17b5e098577652914f541245d31247911be23aeb` (83,097 B)
- New sdist: `73cc354cb68cd3b4f9b08f282785628865eb4c6f600a3be18a067eb0a80e66c4` (436,819 B, 107 entries); 012 authority sdist from the clean rebuild: `72de29c9e60a012425e1c0d0d351ce7ff9c985b1f3b28c3525987a4f70db1c12` (425,885 B)
- Gateway peer (pinned and published-in-image when published): `08ca421bee1ddca62078302b910e8be88cf705be`
- `M_S''.generated_from.git_commit`: `8e3f07e2807ff3ee892c0fb48f3daac9cdfdfa44` (= `S''`'s parent); `M_P`: **DOES NOT EXIST** (no `P`)
- PR: #15 — https://github.com/ulfe-lmi/slaif-local-coding/pull/15 (OPEN, non-draft, MERGEABLE, base `main`)

## Authoritative GitHub state
- Repository: `ulfe-lmi/slaif-local-coding` (public)
- PR: **#15** — https://github.com/ulfe-lmi/slaif-local-coding/pull/15 — state `OPEN`, non-draft, `MERGEABLE`, no auto-merge request
- Base: `main` @ `a04693e6792df6a8ad4262acfb46336a0f662202` (order base, unchanged)
- Branch: `oap/013-mvp-release-publication` (required, unchanged)
- Remote branch SHA at report time: `dfa77fb442a82754bb6af21a2e0fb0af29ddfbab` (= `S''`)
- **Implementation head SHA: dfa77fb442a82754bb6af21a2e0fb0af29ddfbab**
- **Report publication commit: SELF** (first parent = the literal implementation SHA above; `P` does not exist, so `S''` is the final non-report commit of the round — 013-a precedent)
- 013-b round implementation commits pushed before this report (single-parent chain atop the 013-a report commit `29356060322329b9aeed83b289f42ecf5bb66647`):
  1. `e1805223d4bd650e7bf13f35f482467fb3b57d7c` — peer re-pin, released-truth docs, objective-013-b generator/E3, activated 013-b order + `oap/active` transcript (C1)
  2. `f389777601db7e668e9f62eaff716d702be92388` — manifest regeneration (superseded; its tree tripped the CI ruff gate) (C2)
  3. `ac91564789d4de4b89e7533193dfb7455499902a` — E501 fix in the wheel-ruling comment of `tests/test_release_provenance_manifest.py` (C3)
  4. `8e3f07e2807ff3ee892c0fb48f3daac9cdfdfa44` — manifest regeneration (superseded: `generated_from` pointed at `f389777…` instead of this commit's parent) (C4)
  5. `dfa77fb442a82754bb6af21a2e0fb0af29ddfbab` — manifest `M_S''` at the final implementation state, `generated_from` = `S''`'s parent (C5 = `S''`)
- (The 013-a base→`S_a` 9-commit chain is recorded in the 013-a report and is unchanged on this branch.)
- New PR this round: **NO**. Amended existing: **yes** (#15). Merge performed: **NO**. Auto-merge: **NO**.

## Changes and files (013-b round; `2935606…` → `S''`)
- `tests/fixtures/gateway/current_peer_authority.json` — `commit` → `08ca421…` (all other fixture fields byte-identical).
- `Dockerfile` — exactly one line changed: `ARG SLAIF_GATEWAY_PEER_SHA=08ca421…` default (line 44).
- `scripts/release_provenance_manifest.py` — `OBJECTIVE` constant → `013-b` (constant + its docstring reference).
- `tests/test_release_provenance_manifest.py` — E3 objective assertion → `013-b`; wheel-ruling comment (E501-clean after C3).
- `README.md` — released-truth reconciliation per B5 (wheel input; METADATA-ONLY consequence — B6).
- `docs/DOCKER-INSTALL.md`, `docs/IMPLEMENTATION-ROADMAP.md`, `oap/COMPLETENESS.md`, `docs/SLAIF-GATEWAY-INTEGRATION.md`, `docs/TOPOLOGY.md`, `docs/RELEASE-CUTOVER-RUNBOOK.md` — released-truth reconciliation per B5's exact semantics: MVP `0.1.0` RELEASED on `ghcr.io/ulfe-lmi/slaif-local-coding` with tags `0.1.0` and `sha-<S''>` (both resolving to one registry digest); the digest and image-source commit are referenced **by path only** (`packaging/release_record.json` + the schema-v3 manifest `oci.image_digest`/`release` section); NO document carries a literal digest, the current sdist hash, or the manifest `objective` field (012-c citation-stability law); the `v0.1.0` Git tag is described as the strategy post-merge act TARGETING `S''` (no document claims the tag/Release objects exist — verified zero Git tags and zero GitHub releases at report time); publication is registry-only: protected-host cutover NOT performed, no real deployment yet evidenced, Docker qualification remains deployment-qualified (disposable/CI environments only), D1 binding law / loopback default / systemd secondary path unchanged; release-ladder language only (no production-ready/certification claims).
- `packaging/release_provenance_manifest.json` — `M_S''` (5,630 B): `objective: "013-b"`; `generated_from.git_commit = 8e3f07e2807ff3ee892c0fb48f3daac9cdfdfa44` (= `S''`'s parent); `gateway_peer.commit = 08ca421…`; `oci.labels["slaif-local-coding.gateway.peer.sha"] = 08ca421…`; `oci.wheel_sha256 = artifacts.wheel.sha256 = 879baa3a…` (83,352 B); `artifacts.sdist.sha256 = 73cc354c…` (436,819 B); `status = {"cutover_performed": false, "deployment_qualified": "disposable-environment-only", "released": false}`; `oci.published: false`; `oci.image_digest: null`; no `release` key; 12 top-level keys.
- `packaging/release_record.json` — **ABSENT** from the `S''` tree (exists only in `P`; `P` was never created).
- Transcript: activated 013-b order file (`oap/orders/013-b-repin-peer-and-complete-publication.md`, 307 lines, strategic-authored bytes committed verbatim in C1) + `oap/active` → `013-b` (one-line change `013-a` → `013-b`).
- No other path was changed in the 013-b chain (verified: `git diff --name-only 2935606…..dfa77fb…` lists exactly the 14 files above). In particular NO frozen file was touched: `compose.yaml`, `compose.build.yaml`, `.github/workflows/release-image.yml`, `.github/workflows/ci.yml`, `scripts/docker_qualification_ci.py`, `scripts/release_registry_publish.py`, `scripts/ghcr_tag_check.py`, `packaging/release_provenance_manifest.schema.json`, and no `src/`, `pyproject.toml`, `uv.lock`, or `config/` path (whole-PR-chain verified for `src/`/`pyproject.toml`/`uv.lock`/`config/`).

## Acceptance evidence

### B1 — PASSED
At round start and re-verified at report time (2026-09-17T10:3xZ), `gh api repos/ulfe-lmi/slaif-api-gateway/commits/main` → `08ca421bee1ddca62078302b910e8be88cf705be` (committer date 2026-09-17T08:30:55Z). Matches the order's strategic re-adjudication exactly; proceed.

### B2 — PASSED
Fixture `commit` = `08ca421…` (all other fields unchanged); `Dockerfile` line 44 `ARG SLAIF_GATEWAY_PEER_SHA=08ca421…` (the only Dockerfile line changed this round); every current-facing doc citation of the old pin as CURRENT updated; historical OAP records and objective-scoped historical statements byte-identical (the 013-b chain diff above). Contract-surface blob-identity at both pins (strategic, recorded in the order): `contract.py` `9e8ae5ef8e1f9d8d48bf3627b9a767d86593a6ac`, `codex_0149.py` `8976c984c4430d65b3d36bad8565062a8c6f955a`, `streaming.py` `73cc9f99e8c3cb2f3eb95173344bfbdc211c71ff`.

### B3 — PASSED
`scripts/release_provenance_manifest.py` `OBJECTIVE = "013-b"`; `tests/test_release_provenance_manifest.py` asserts objective `013-b`; `M_S''.objective = "013-b"`. Manifest module 18/18 green locally at `S''` (re-run at report time) and in CI (run 35208071525, `test` job).

### B4 — PASSED
- CI at `S''` (run 35208071525, `gateway-contract` job 105158654064, SUCCESS): `{"checkout_clean": true, "commit": "08ca421bee1ddca62078302b910e8be88cf705be", "network_guard": "enabled", "repository": "ulfe-lmi/slaif-api-gateway", "tests_collected": 18, "tests_passed": 18, "tests_failed": 0, "tests_errors": 0, "tests_skipped": 0}`.
- Local re-run at report time (disposable clean checkout of the gateway at exactly `08ca421…`, network guard enabled, identical command to CI): identical 18/18 JSON result.

### B5 — PASSED (wording per B5's exact semantics; transient-overstatement caveat: deviation 4)
All current-facing documents reconciled as listed under Changes and files. Verified properties at `S''`: no document carries a literal registry digest; none cites the current sdist hash or the manifest `objective` field; the `v0.1.0` tag/Release objects are described as future (strategy, post-merge) — zero Git tags and zero GitHub releases exist on the repository at report time; `README.md` no longer describes the MVP as unreleased; no production-ready/certification claims; D1 binding law / loopback default / systemd secondary path statements unchanged; publication stated as registry-only with cutover NOT performed and no real deployment yet evidenced.

### B6 — PASSED
(a) Clean rebuild of the 012 authority state (`git archive` of the `a04693e6792df6a8ad4262acfb46336a0f662202` tree + `uv build`, in a disposable `/tmp` directory): wheel SHA-256 = `fceadc378130dd4ffcc3f75d17b5e098577652914f541245d31247911be23aeb` (83,097 B) — the 012 authority wheel reproduced byte-for-byte (sdist `72de29c9e60a012425e1c0d0d351ce7ff9c985b1f3b28c3525987a4f70db1c12`, 425,885 B).
(b) Both wheels unpacked: 26 entries each; **24 byte-identical**; the ONLY differing entries are `slaif_local_coding-0.1.0.dist-info/METADATA` and `slaif_local_coding-0.1.0.dist-info/RECORD`. The METADATA header (all fields through the first blank line) is byte-identical; the full METADATA diff is 4 lines removed / 13 lines added, entirely within the README-derived long description (the released-truth wording); the RECORD diff is exactly one line: the METADATA hash/size entry (41,537 → 42,178 B). Re-verified at report time from the on-disk artifacts.
(c) `H_new = 879baa3ad19e0f513090add965d267957d27f7bcd904d1e225586d76126f8b19` (83,352 B) is the hash bound by: CI `verify_wheel_binding` (fresh `uv build` at `S''` equals the manifest entry — PASSED), `in_image_provenance` (PASSED), `image_content_scan` (PASSED), `hardening_and_labels` `wheel_sha256_label` (PASSED), `M_S''` (`oci.wheel_sha256` + `artifacts.wheel.sha256`), and the release workflow's wheel-binding assertion. `src/`, `pyproject.toml`, `uv.lock` untouched across the whole PR chain (verified by diff).

### B7 — PASSED
`S'' = dfa77fb442a82754bb6af21a2e0fb0af29ddfbab` is a manifest-regeneration commit whose tree contains the peer re-pin, the doc reconciliation, the generator/E3 objective change, and `M_S''` (fields above), and does NOT contain the release record (verified absent from the tree). CI at `S''` FULLY GREEN — run `35208071525`, all four jobs SUCCESS (per-job detail in the CI section below).

### B8 — BLOCKED (the round's blocker)
`gh workflow run release-image.yml` dispatched at `S''` (branch tip = `S''`) at 2026-09-17T10:01:51Z and re-dispatched (deterministic retry) at 2026-09-17T10:15:38Z:
- Run `35208313536` (job `build-and-publish`): **FAILED** at step "Push tags and registry-verify a single digest": `PublishError: docker push ulfe-lmi/slaif-local-coding:sha-dfa77fb442a82754bb6af21a2e0fb0af29ddfbab failed: unauthorized: access token has insufficient scopes`
- Run `35209542430` (job `build-and-publish`, id 105163459953): **FAILED** at the same step with the identical error string.
Root cause (verified via GitHub API at report time): `GET /repos/ulfe-lmi/slaif-local-coding/actions/permissions/workflow` → `{"default_workflow_permissions":"read"}`. GitHub semantics: a workflow's `permissions:` key cannot exceed the repository's default workflow-permission ceiling, so the `GITHUB_TOKEN` issued to the dispatch-only workflow lacks the GHCR `packages: write` scope it declares. Raising the repository's Actions permission ceiling (or otherwise enabling `packages: write` for the token) is a security-policy change → strategy/human authority, not coding. All pre-push workflow steps (build, wheel-binding assert, GHCR login) succeeded in both runs; the failure is confined to the registry push.
Consequences: `D` not captured; no `P`; `docker-published` execution NOT RUN. The registry was re-probed anonymous at report time: `0.1.0` → `absent`, `sha-dfa77fb…` → `absent` (`scripts/ghcr_tag_check.py`), so no tag was written by either run and no orphan-tag cleanup is needed.

### B9 — NOT RUN
No `D` → `packaging/release_record.json` was not written and `P` was not created. The record's fields (schema `slaif-release-record-v1`; `image_source_commit = S''`; `oci_image_digest = sha256:<D>`; `oci_tags = ["0.1.0", "sha-<S''>"]`; `published_at` RFC 3339 UTC; `publication_workflow_run_id`) remain exactly as specified by the order for the round that actually publishes.

### B10 — NOT RUN
No `P` and no published image → the executed `docker-published` job (pull by digest `D` and by both tags, full label-set verification, pull-based compose contract run on canonical port 18031, negative contract cases, missing-secret fail-closed readiness, no-build proof, teardown absence proof) did not run. The gate's correct at-`S''` behavior (explicit not-yet-published skip) is verified in the CI section.

### B11 — PARTIAL (as written: report child of `P`)
`P` does not exist, so "child of `P`" is unsatisfiable. Following the 013-a no-`P` precedent (013-a R19: report published with first parent `S`), this report is published as the report-only child of the final non-report commit `S''`; its first parent equals `S''` (the literal implementation SHA). Pushed and verified as the remote PR head in the report-publication step. CI at the report head may be pending at publication time; strategy verifies.

### B12 — PASSED
Protected-host invariance (read-only probes only; no protected resource was touched):

| Item | Before (2026-09-17T09:31:43Z) | Intermediate (2026-09-17T10:19:39Z) | After (2026-09-17T10:34:13Z) |
|---|---|---|---|
| `qwen-serving-vision.service` | active/running, MainPID=23961 | active/running, MainPID=23961 | active/running, MainPID=23961 |
| `qwen-serving.service` | inactive/dead | inactive/dead | inactive/dead |
| `zap-it-lan.service` | activating/auto-restart | active/running | activating/auto-restart |
| Port 18020 | `LISTEN 0.0.0.0:18020`, owner `vllm pid=23961` only | identical | identical |
| Ports 18031/18033/18034 | closed | closed | closed |
| `docker ps -a` | three pre-existing exited non-slaif containers (`beautiful_cartwright`, `beautiful_haibt` — `chrockey/fpt-votenet:v0.1.0`, Exited 2 years ago; `kind_brown` — `hello-world`, Exited 2 years ago) | identical | identical |
| Codex profile file (active coding profile; path omitted per the order's host-path prohibition) | size=122451, mode=600, mtime=2026-09-15T07:17:50.734803657+02:00 | identical | identical |

Host image list at report time (read-only `docker images`): no slaif image present; only pre-existing non-slaif images (`postgres:16`, `hello-world:latest`, `chrockey/fpt-votenet:v0.1.0`); the diagnostic probe tags (deviation 2) were removed from the daemon before this listing.

Note: `zap-it-lan.service` oscillated between its own `activating/auto-restart` and `active/running` states across the probes — that unit's auto-restart lifecycle, **not** a coding mutation (no systemd, network, or service mutation was performed; every probe was read-only).

### B13 — 013-a R-criteria re-affirmed at the final head
- **R1** (release record + v3 schema) — **PARTIAL**: schema `slaif-release-record-v1` semantics, closed key set, and generator support implemented and unit-tested; the record file itself exists only in `P` — `P` does not exist (B8).
- **R2** (schema v3) — **PASSED** at `S''` (manifest module 18/18 local + CI `test` job).
- **R3** (state-aware generator) — **PASSED** at `S''` (objective now `013-b` in both states; not-yet-published state emitted; published-state branch unit-tested).
- **R4** (state-conditional E3 + cross-consistency) — **PASSED** at `S''` (18/18 local, re-run at report time; CI `test` job green); published-state variants **NOT RUN** (no `P`).
- **R5** (byte-identity law) — **PASSED as amended by 013-b ruling 2**: no commit in the whole PR chain (base→`S''`) touches `src/`, `pyproject.toml`, or `uv.lock` (verified by diff); the wheel hash legitimately changed with the README-derived documentation per the METADATA-ONLY wheel ruling (B6); `H_new` is byte-for-byte reproducible from the `S''` tree (fresh `uv build` at report time) and is bound by CI/manifest/in-image/workflow.
- **R6** (Dockerfile label parameterization) — **PASSED** at `S''`: this round changed only the peer ARG default line; the label parameterization and the 013-a deviation-1 quoted default are untouched; CI `hardening_and_labels` PASSED (`qualification_label: true`, `gateway_peer_label: true`, `wheel_sha256_label: true`, `topology_label: true`).
- **R7** (pull-based canonical `compose.yaml`) — **PASSED** at `S''` (frozen by 013-b; `compose_merge_equivalence` + static gates green).
- **R8** (`compose.build.yaml` + mechanical merge test) — **PASSED** at `S''` (`merged_equals_pre013: true`).
- **R9** (two-file harness, all phases) — **PASSED** at `S''` (all 15 phases, `docker` job, run 35208071525).
- **R10** (static pull-canonical gate) — **PASSED** at `S''` (CI `test` job).
- **R11** (release workflow activation) — **PASSED** (implementation; frozen, untouched this round); execution: the workflow DID run (two dispatches at `S''`) but both runs FAILED at the registry push (B8) — "the run SUCCEEDS" is not met.
- **R12** (trigger workflow at the final head, capture `D`) — **BLOCKED** (see B8): triggered twice; both runs failed at the push step; `D` not captured.
- **R13** (CI `docker-published` gate) — **PARTIAL**: at `S''` it skipped with the explicit line `not yet published (packaging/release_record.json absent) — docker-published skipped` (run 35208071525, job 105158654107); execution with digest/tag pulls etc. is **NOT RUN** (no `P`, no published image).
- **R14** (all existing gates green at the final head) — **PASSED** at `S''` (4/4 jobs, run 35208071525).
- **R15** (DOCKER-INSTALL pull-based primary path) — **satisfied by B5** at `S''` (final published-truth wording present per B5's exact semantics; the 013-a pull-based structure intact).
- **R16** (documentation reconciliation) — **satisfied by B5** at `S''` (all current-facing documents at the released-truth semantics; zero Git tags/Releases exist and the documents say exactly that).
- **R17** (no document above manifest status) — **PASSED with caveat**: `M_S''` correctly states not-yet-published; the documents carry the B5-mandated released-truth wording; while publication is blocked, the documents transiently lead the machine-readable manifest (deviation 4). No document asserts the tag/Release objects exist and none carries a literal digest.
- **R18** (Gateway peer re-verification) — **PASSED** (B1; the strategic re-adjudication is recorded in the order; the re-pin is within this order's closed scope).
- **R19** (exact round sequence) — **PARTIAL**: implementation commits → `S''` with `M_S''` (no release record) → CI at `S''` fully green with the explicit skip → workflow dispatch at `S''` → **STOPPED at B8** (both runs failed at push; no `D`, no `P`, no CI at `P`); report pushed as a child of `S''` (013-a no-`P` precedent).
- **R20** (protected-host invariance) — **PASSED** (B12).

## Verification
Local, at the `S''` tree (all re-run at report time this session):
- `uv run --frozen pytest -q`: **PASSED** — 1098 passed, 26 skipped, 0 failed (80.43s)
- `uv run --frozen ruff check .`: **PASSED** — all checks passed
- `uv run --frozen ruff format --check .`: **PASSED** — 356 files already formatted
- `uv run --frozen mypy src tests`: **PASSED in the CI-equivalent environment** — a fresh throwaway venv synced exactly as CI syncs (`uv sync --frozen --extra dev`, no `gateway-contract` group): "Success: no issues found in 71 source files". Note: the repository's own venv additionally contains the `gateway-contract` dev group (`sqlalchemy`) installed for this round's B4 local gate; with that group present the identical command emits 2 `unused-ignore` diagnostics at `scripts/gateway_accounting_rehearsal.py:2821/3046` (the `# type: ignore[import-not-found]` on the `sqlalchemy` imports is "unused" only because `sqlalchemy` is then locally importable). This is an environment artifact, not a tree defect: that file is a pre-existing 005/008-era script outside 013-b's closed scope and was not modified; the CI `test` job (identical command, without the group) PASSED at `S''`.
- `uv run --frozen python -m compileall -q src tests oap/bin scripts`: **PASSED**
- `uv build` + `sha256sum`: **PASSED** — wheel `879baa3ad19e0f513090add965d267957d27f7bcd904d1e225586d76126f8b19` (83,352 B) and sdist `73cc354cb68cd3b4f9b08f282785628865eb4c6f600a3be18a067eb0a80e66c4` (436,819 B); both equal the `M_S''` entries
- `uv run --frozen python scripts/artifact_policy_check.py --dist <fresh build> --inspect`: **PASSED** — `ok: true, violations: []`
- `uv run --frozen pytest -q tests/test_release_provenance_manifest.py` (E3 gate + cross-consistency, not-yet-published state): **PASSED** — 18/18
- B6(a) clean `git archive` rebuild of `a04693e6792df6a8ad4262acfb46336a0f662202`: **PASSED** — reproduces `fceadc37…` byte-for-byte (see B6)
- B6(b) wheel-vs-wheel entry diff: **PASSED** — 24/26 identical; METADATA header identical; description-only diff 4 removed/13 added; RECORD diff = exactly the METADATA hash line (see B6)
- B4 local strict gate (gateway checkout at `08ca421…`, network guard enabled, CI-identical command): **PASSED** — 18/18
- `docker compose config --quiet` renders (pull file; two-file build combination), with temporary 0-byte env/config files: **PASSED** (render only; NO host docker build/run/up)
- `bash -n` on changed shell scripts: **NOT NEEDED** — this round changed no shell scripts; the CI `bash -n oap/bin/*.sh packaging/*.sh` gate PASSED within the green `test` job at `S''`
- `python3 scripts/ghcr_tag_check.py --repo ulfe-lmi/slaif-local-coding --tag 0.1.0`: **PASSED** — `absent` (anonymous probe, report time)
- `python3 scripts/ghcr_tag_check.py --repo ulfe-lmi/slaif-local-coding --tag sha-dfa77fb442a82754bb6af21a2e0fb0af29ddfbab`: **PASSED** — `absent` (anonymous probe, report time)
- `gh workflow run release-image.yml` at `S''`: **BLOCKED→FAILED at push** (see B8) — 2 dispatches (runs 35208313536, 35209542430)
- Protected-model live matrix (text/tool/SSE/vision/etc.): **NOT RUN** (explicit non-goal of this order: fake/synthetic upstreams only; no protected-model inference anywhere)
- Real Codex E2E: **NOT RUN** (not ordered this round)

## Live model/service evidence
No live model or adapter service was used: this order authorizes fake/synthetic
upstreams only (all CI Docker evidence runs against the disposable fake
upstream on the GitHub runner, canonical port 18031 inside the runner).
Protected-host read-only probes only (B12); the existing vision service state
is unchanged; no request was sent to port 18020.

## GitHub CI / required checks
- Superseded head `f389777…` (C2), run `35207658499`: **FAILED** — `test` job ruff gate, E501 in `tests/test_release_provenance_manifest.py` (a comment line introduced by C1); fixed in C3 (`ac91564…`).
- Intermediate head `8e3f07e…` (C4), run `35207964275`: **SUCCESS** (all four jobs).
- **Final implementation head `S'' = dfa77fb…`, run `35208071525`: all four jobs PASSED**
  - `test` PASSED — job 105158654083
  - `gateway-contract` PASSED (NEW pin `08ca421…`; 18/18; network guard enabled) — job 105158654064
  - `docker` PASSED — job 105158653904; all 15 phases PASSED: `verify_wheel_binding` (fresh `uv build` at `S''` == manifest `H_new`), `compose_rendered_validation` (both compose files scanned, no secret values in rendered output), `compose_merge_equivalence` (`merged_equals_pre013: true`), `image_build`, `fake_upstream_start`, `adapter_stack_up`, `in_image_provenance` (non-editable install at `H_new`), `bridge_positive_signed`, `bridge_negative_contract`, `config_time_rejection`, `fail_closed_readiness`, `image_content_scan` (0 forbidden matches over 6,487 files), `operations_stop_start_recreate_upgrade_rollback`, `hardening_and_labels` (`qualification_label: true`, `gateway_peer_label: true`, `wheel_sha256_label: true`, `topology_label: true`), `teardown_absence_proof`; docker 28.0.4 / compose 2.38.2
  - `docker-published` PASSED-as-skip with the explicit line `not yet published (packaging/release_record.json absent) — docker-published skipped` — job 105158654107
- Release workflow at `S''`: runs `35208313536` and `35209542430` — both **FAILED** (job `build-and-publish`; step "Push tags and registry-verify a single digest"; `PublishError: docker push ulfe-lmi/slaif-local-coding:sha-dfa77fb… failed: unauthorized: access token has insufficient scopes`) — see B8.
- All required green at drafting: **yes** (at `S''`, `ci.yml`).
- CI at `P`: **NOT RUN** (no `P`). Report-head (this commit) checks may be pending at publication; strategy verifies.

## Local setup/dependencies
- Repository-owned venv via `uv` (locked/frozen installs); no new dependencies; no changes to `pyproject.toml`/`uv.lock` (frozen by this order).
- The repository venv additionally holds the `gateway-contract` dev group (installed for the B4 local gate; see the mypy note above).
- Passwordless sudo used only for read-only `docker ps`/`docker images` and render-only `docker compose config` probes (established pattern). No terminal operator recruited.
- Disposable `/tmp` scratch only (outside the repository): the `git archive` rebuild directory (B6a), the gateway checkout at `08ca421…` (B4 local), fresh-build directories, render temp files, and the CI-mirror mypy venv.

## Documentation
Updated as listed under Changes and files (B5, released-truth semantics;
transient-overstatement caveat in deviation 4). Historical OAP orders/reports
and all 009–012 records byte-identical (verified: the 013-b chain diff touches
only the 14 files above). PR #15 body updated at round end with the final
`S''`/peer/`H_new`/B8 facts.

## Safety/scope confirmations
- Unrelated/pre-existing work preserved; the working tree contains only pre-existing untracked junk left untouched (`Local`, `clean`, `unchanged` — not committed) and the pre-existing local `oap/runtime.env.example` edit (intentionally uncommitted, per round convention).
- No secrets, raw prompts, source, images, tool outputs, request/response bodies, or private URLs in the report, commits, CI logs, or artifacts; CI fake credentials follow the 011 pattern (generated, 0600, never printed). The diagnostic registry error-string probes (deviation 2) used throwaway fake credentials only (never real secrets), published nothing (every push was rejected by the registry), and their probe tags were removed from the host daemon (verified by the after-probe image list: pre-existing images only).
- Protected 18020/Qwen/Codex fixture changed: **NO** (B12 invariance above).
- Gateway repository change: **NO** (read-only `gh api` inspection + a disposable read-only checkout in `/tmp` only).
- Dependency change: **NO**. Version: still `0.1.0`.
- Required tests skipped/not run: 26 routine skips in the local suite (Gateway-dependent modes without `SLAIF_GATEWAY_ROOT`, as designed); protected-model matrix and real-Codex E2E NOT RUN (not ordered).
- Extra objective PR: **NO** (exactly one PR, #15; this round amended it). Coding merge: **NO**. Auto-merge: **NO**.
- Active/order edited: **NO** — the activated 013-b order bytes were committed verbatim in C1 and untouched since; the 013-a order/report bytes are unchanged (verified by the 013-b chain diff).
- Report commit report-only: **yes** (staged diff is exactly the one report path; verified before commit).

## Known limitations/blockers
1. **B8 publication failure (the blocker).** The repository's `default_workflow_permissions = "read"` clamps the dispatch-only release workflow's declared `packages: write` (GitHub: a workflow's `permissions:` key cannot exceed the repository ceiling), so the `GITHUB_TOKEN` lacks GHCR push scope. Raising the repository's Actions permission setting is a security-policy change → strategy/human. Both dispatch runs failed at the push step; no tag was written (registry verified `absent` for both candidate tags, anonymous); no orphan-tag cleanup is needed.
2. **`D` not captured; no `P`.** Consequently the release record, the published-state manifest `M_P`, the `v0.1.0` Git tag (strategy post-merge act), the GitHub Release, and the `docker-published` execution at `P` all remain outstanding.
3. **Transient documentation/manifest divergence (deviation 4).** While publication is blocked, the documents at `S''` (B5-mandated released-truth wording) transiently lead the machine-readable manifest (which correctly states not-yet-published); the divergence is resolved at `P`/publication (which regenerates the manifest to the released state without touching documents).

## Deviations (exact justification and status)
1. **`scripts/cutover_state_machine.py` + `tests/test_cutover_state_machine.py` keep the 012-era pin.** These files cite the old peer as snapshot identifiers inside 012-scoped test fixtures and are NOT in 013-b's closed scope list (012-a updated them under its own order; 013-b's scope enumerates exactly the files changed this round). They are not current-facing documents. **Status: intentional, scope-bound.**
2. **Latent bug in the frozen `scripts/release_registry_publish.py` (flagged to strategy; NOT modified).** The script pushes `f"{args.repo}:{tag}"` = `ulfe-lmi/slaif-local-coding:sha-<S''>` — WITHOUT the `ghcr.io/` prefix its own docstring specifies (`ghcr.io/<repo>:sha-<S>`). Empirically (docker 28.0.4 CLI; disposable probe tags; throwaway fake credentials only): that unqualified reference resolves against Docker Hub (`docker.io/…`), whose failures produce `denied: requested access to the resource is denied` / `unauthorized: authentication required` — NOT the observed GHCR string `access token has insufficient scopes` — so the runner's push demonstrably reached GHCR (the runner-side resolution of the same reference under the workflow's login context is not reproducible from this host). The bug is latent behind the permissions blocker: once `packages: write` is granted, the unqualified reference may push to the wrong registry. Fixing it requires unfreezing the script in a later order (e.g., 013-c). **Status: flagged; file frozen by this order.**
3. **The blocker itself deviates from the order's expected B8 outcome ("the run SUCCEEDS"; capture `D`).** Not a coding deviation — a repository-permission condition outside coding authority; published here as the exact evidence per the order's stop-and-report law. **Status: BLOCKED, reported.**
4. **Documents at `S''` carry the B5-mandated released-truth wording while publication is blocked.** B5's semantics require exactly this wording at `S''` (the released-truth documentation state; the digest referenced by path only). Because B8 failed, the registry truth is still "absent", so the documents transiently overstate registry state until `P`/publication completes. No document carries a literal digest or claims the tag/Release objects exist; `M_S''` (machine-readable) correctly states not-yet-published. **Status: consequence of the B8 block plus the B5 mandate; documented.**
5. **Two superseded manifest commits (C2, C4).** `uv build`'s sdist embeds `tests/` + `docs/` + `packaging/`, so any test/docs edit changes the sdist hash and forces a manifest-regeneration commit whose `generated_from` must equal that commit's parent (B7). C2 tripped the CI ruff gate (E501); C4's `generated_from` pointed at C2 instead of its parent (C3); C5 (`S''`) corrected both. All three are mechanical, in-scope, and recorded in the commit chain. **Status: resolved at `S''`.**

## Recommended strategic follow-up
Factual only; strategy decides:
1. Raise the repository's Actions workflow-permission ceiling (e.g., set the repository default workflow permissions to `write`, or otherwise make the dispatch-only `release-image.yml`'s declared `packages: write` effective for the `GITHUB_TOKEN`) — a security-policy change requiring strategy/human.
2. Authorize a follow-up round (e.g., 013-c) to fix the frozen `scripts/release_registry_publish.py` push-reference prefix (deviation 2) so the push target is unambiguously `ghcr.io/ulfe-lmi/slaif-local-coding:…`.
3. Re-dispatch `release-image.yml` at the then-current implementation head. The remaining publication closure from the current green head is then: `D` capture (registry-verified) → `P` (release record + regenerated `M_P`, exactly two files) → CI at `P` fully green including the EXECUTED `docker-published` job → final report; afterwards the `v0.1.0` Git tag (targeting `S''`) and the GitHub Release remain the strategic post-merge acts. No orphan-registry cleanup is needed (verified absent).
4. Verify the report-head CI for this report commit (may still be running at publication time).

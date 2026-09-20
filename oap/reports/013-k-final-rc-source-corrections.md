# OAP Coding-Agent Report — 013-k

## Work order
- Identifier: `013-k`; order path: `oap/orders/013-k-final-rc-source-corrections.md`; numeric objective: 013
- PR mode: AMENDED_EXISTING_PR

## Status
COMPLETE

## Executive summary
All three final RC source corrections (K1–K3) are closed on PR #15 (amended, no
new PR, no merge), with the consequent artifact refresh. The release workflow's
actual two-file Compose build invocation now carries the required nonsecret
build selection (`SLAIF_LOCAL_CODING_IMAGE`) plus the nonsecret temporary
Compose inputs it actually needs, and its exact command+environment is proved
green from a fresh disposable CI checkout with the built image's
source/wheel/RC labels asserted. The transient README
history/current-deployment paragraph is removed (short durable repository
boundary retained), the registry-auth wording is conditional on image
visibility, the vision capability reads "at most one image" with zero-image
requests supported, and the docs gate now catches recurrence of that exact
transient wording via one focused negative fixture. `plan_pre_write` now
requires EXPLICIT verified-absent for both target tags — unknown registry
statuses fail closed with zero Docker mutations, proved by real unknown-status
`main()` cases for each target. Two clean isolated builds are byte-identical
for wheel and sdist; the excluded provenance manifest is regenerated as
derived metadata bound to the exact final source commit; the previous wheel
hash `3c4c36e6...` is not retained. Fresh implementation CI is 5/5 SUCCESS;
`docker-published` is explicit NOT RUN pre-publication (no RC exists; image
source commit NONE). No registry write, dispatch, tag, Release, or visibility
change occurred.

## Authoritative GitHub state
- Repository: `ulfe-lmi/slaif-local-coding`; PR #15 https://github.com/ulfe-lmi/slaif-local-coding/pull/15 (OPEN, non-draft, MERGEABLE, mergeStateStatus CLEAN)
- Base `main` = `a04693e6792df6a8ad4262acfb46336a0f662202`; starting remote head `25720c06dcd55e9433793a7e6068f36d1e5bcb40` (matches order)
- Implementation head SHA: `b3f8d9e1ee46be3e3d453c484af6d8267dbac8d6`
- Report publication commit: SELF
- Implementation commits pushed before report (2, in order):
  - `780d561ba2761643282e7fd41c3eba229a8cd6c6` (A — K1–K3 implementation + exact activated order bytes `oap/orders/013-k-final-rc-source-corrections.md` + `oap/active` → `013-k`; 13 files)
  - `b3f8d9e1ee46be3e3d453c484af6d8267dbac8d6` (B — provenance manifest v5 re-bound to A; derived metadata only)
- Pushed as a single push (remote advanced 25720c0 → b3f8d9e in one operation); no intermediate-head CI run was produced
- New PR this round: NO; amended existing: YES (PR #15); merge performed: NO
- Candidate image source commit: NONE (no image is published this round)

## Changes and files
- K1: `.github/workflows/release-image.yml` (build step exports the nonsecret build selection `SLAIF_LOCAL_CODING_IMAGE=slaif-local-coding:0.1.0-${GITHUB_SHA}` and creates nonsecret temporary `SLAIF_ENV_FILE`/`SLAIF_CONFIG_FILE` inputs the build invocation actually needs to load the project; header procedure comment updated), `compose.build.yaml` (development usage comment now includes the required variable and the per-file-interpolation reason), `docs/DOCKER-INSTALL.md` (build-from-source section documents the same export; same interpolation note), `.github/workflows/ci.yml` (existing `docker` job gains the focused step "Prove the release workflow build command (fresh disposable CI checkout)" — the exact workflow command and environment, asserting `org.opencontainers.image.revision` = head, `slaif-local-coding.wheel.sha256` = manifest wheel, `slaif-local-coding.qualification` = RC candidate label). `compose.yaml` (canonical pull-only, explicit-image requirement) is UNCHANGED.
- K2: `README.md` (transient history/current-deployment paragraph removed, short durable repository boundary retained; registry-auth bullet conditional on package visibility; vision capability "at most one image per request (zero-image requests are supported)"), `scripts/docs_consistency_check.py` (new README pattern "README transient cutover-not-performed paragraph" on the two distinctive clauses of the removed wording; check-8 docstring extended), `tests/test_docs_consistency.py` (one focused negative fixture `test_readme_transient_cutover_paragraph_fails`).
- K3: `scripts/release_registry_publish.py` (`plan_pre_write` requires EXPLICIT verified-absent for both target tags before proceeding; any unknown/unresolved status raises `PublishError` — never treated as absent; docstring corrected to match the strengthened law), `tests/test_release_registry_publish_gate.py` (mocked registry boundary passes unknown statuses through UNCHANGED instead of converting them to DIGEST; 3 new matrix rows; `test_unknown_status_source_tag_zero_mutations` and `test_unknown_status_rc_tag_zero_mutations` each execute `main()` and assert ZERO Docker mutations).
- Artifact refresh: `tests/test_release_provenance_manifest.py` (accepted wheel hash moves to the 013-k identity; objective assertion `013-k`), `scripts/release_provenance_manifest.py` (OBJECTIVE `013-k`; regeneration limitation bullet records the 013-k regeneration on the K1–K3 authorized inputs), `packaging/release_provenance_manifest.json` (regenerated metadata B at commit B).
- Transcript: exact activated order bytes + `oap/active` committed unchanged in A.

## Acceptance evidence
### K1 — actual publication build invocation works
- Result: PASSED. Local reproduction of the defect: `docker compose -f compose.yaml -f compose.build.yaml config` WITHOUT the variable fails with `required variable SLAIF_LOCAL_CODING_IMAGE is missing a value` (compose interpolates each file before merging, so the override's image value does not avoid the error); WITH the nonsecret build selection + temporary nonsecret env/config inputs the merged spec renders the override image `slaif-local-coding:0.1.0-<sha>` with the build args. The same exact command+environment from a fresh disposable CI checkout built the image (run 35526139281, `docker` job step "Prove the release workflow build command (fresh disposable CI checkout)" PASSED): `built image: sha256:d003ad7efb5af327973a9e35e1efe47bc2e7405c26af2af4a530c896f37ffd67`, with all three label assertions passing (revision = head, wheel sha256 = `ad6be6d2...`, qualification = `rc-candidate-0.1.0-rc1; private; not final release`). The pinned Docker design (digest-pinned bases, 6-pin build environment) is unchanged; no registry login/write/dispatch in this round.
### K2 — transient README paragraph removed, wording corrected, gate catches recurrence
- Result: PASSED. The paragraph is gone; the durable boundary retained is exactly "This repository owns the adapter, route capability policies, packaging, tests, and diagnostics. The Gateway remains a separate service." Registry-auth wording is now conditional on package visibility; vision reads "at most one image per request (zero-image requests are supported)". The docs gate (`scripts/docs_consistency_check.py`) fails on a temporary-tree README containing the transient wording (`test_readme_transient_cutover_paragraph_fails` PASSED); the real repo passes (`docs consistency: OK (13 claim docs checked)`). Install links, limitations, credits, and the rest of the landing page are untouched.
### K2 — wheel METADATA rebuild, previous hash not retained
- Result: PASSED. The new wheel hash is `ad6be6d2e8ad0f99eafb4be7b1c78efbcffe6de16e39106182d85db03933ce1e` (75,554 B, 26 entries); sdist `be7b18642c0947a5bf1ef5f0b7d622f34ac3f7db6c8d9142868f89072784b35e` (455,115 B, 117 entries). Two clean isolated builds of A (fresh `git archive` extractions) are byte-identical for wheel AND sdist across Python 3.12.3 (repo venv) and 3.12.14 (uv-managed), uv 0.12.5; the direct checkout `uv build` matches both. The previous wheel hash `3c4c36e666fb67f6a8ed0bbf1a60962e187e46ba1183f314eba03100ce2006af` appears nowhere in current source (test constant, manifest, and workflow binding all carry the new identity).
### K3 — explicit registry-state precondition + real unknown-status cases
- Result: PASSED. `plan_pre_write` returns `proceed` ONLY for explicit `absent`/`absent`; unknown statuses (e.g. `unknown-registry-status`) raise `PublishError` naming the observed states and stating they are never treated as absent. The mocked boundary passes unknown statuses through unchanged. `test_unknown_status_source_tag_zero_mutations` and `test_unknown_status_rc_tag_zero_mutations` execute `main()` per target and assert `docker_calls == []` (both PASSED); the pure matrix gains 3 unknown-status rows (all raise). The full file now collects 31 test cases (was 26).
- Prospective correction (per order; prior report immutable): the 013-j report's J1 evidence named `test_unknown_status_zero_mutations` as existing; no such test existed in the 013-j source, and the 013-j `plan_pre_write` fell through to `proceed` on unknown statuses. The real unknown-status tests added this round are `test_unknown_status_source_tag_zero_mutations` and `test_unknown_status_rc_tag_zero_mutations` (plus 3 matrix parameters); no report claim is reproduced from memory.
### Metadata B — provenance manifest regenerated on exact observed tools + source-input equality
- Result: PASSED. Manifest bound to source A `780d561ba2761643282e7fd41c3eba229a8cd6c6`: objective `013-k`; observed build Pythons exactly `3.12.3` + `3.12.14` (`wheel_patch_independent: true`); uv `0.12.5`; backend `hatchling==1.32.0` with the six exact build pins enforced (unchanged); immutable digest-pinned base identities (unchanged); 119-entry `source_inputs` map; state pre-freeze (`rc_published: false`, `final_public_release: false`, `cutover_performed: false`, `oci.image_digest: null`). `source_input_map.py --ab A B --manifest`: input maps identical (119 files), A..B diff confined to the manifest (derived only); `--ref B` matches the recorded map. No runtime dependency or `uv.lock` churn (`uv lock --check` PASSED).

## Verification
- `uv run --frozen ruff check .`: PASSED (all checks passed, 386 files)
- `uv run --frozen ruff format --check .`: PASSED (386 files already formatted)
- `uv run --frozen mypy src tests`: PASSED (strict; 76 source files)
- `uv run --frozen pytest -q` (local, implementation head): PASSED — 1219 passed, 26 skipped, 0 failed (1245 collected). The 26 skips are the exact conditional set: 18× `SLAIF_GATEWAY_ROOT` unset (gateway contract/162 focused tests — exercised by the dedicated CI job), 7× `SLAIF_LIVE_TEST` unset (live-service tests), 1× protected vision fixture requires human activation
- `uv run --frozen python scripts/docs_consistency_check.py`: PASSED (13 claim docs; new transient-paragraph pattern active)
- Two clean isolated builds of A (fresh `git archive` extractions): PASSED — byte-identical wheel `ad6be6d2e8ad0f99eafb4be7b1c78efbcffe6de16e39106182d85db03933ce1e` (75,554 B, 26 entries) and sdist `be7b18642c0947a5bf1ef5f0b7d622f34ac3f7db6c8d9142868f89072784b35e` (455,115 B, 117 entries) across Python 3.12.3 and 3.12.14, uv 0.12.5
- `uv run --frozen python scripts/artifact_policy_check.py --dist dist --inspect`: PASSED (ok=true, zero violations)
- `uv run --frozen python scripts/artifact_policy_check.py --dist dist --install-smoke`: PASSED (fresh-venv wheel install, version 0.1.0)
- `uv run --frozen python scripts/source_input_map.py --ab 780d561... b3f8d9e... --manifest packaging/release_provenance_manifest.json`: PASSED (119 input files, derived-only diff)
- `uv run --frozen python scripts/source_input_map.py --ref b3f8d9e... --manifest packaging/release_provenance_manifest.json`: PASSED
- `uv lock --check`: PASSED (no lock churn)
- `python3 -m compileall -q src tests oap/bin scripts`: PASSED
- `bash -n oap/bin/*.sh packaging/*.sh`: PASSED
- `docker compose config` (local, CLI-only, no daemon): defect reproduced and fix verified (see K1)

## Live model/service evidence
- No live model or service calls were made (no live call was required by the order). The protected Qwen/vLLM vision service was observed READ-ONLY before and after the round; row-identical fixture (see Safety/scope confirmations).

## GitHub CI / required checks
- Implementation-head run: https://github.com/ulfe-lmi/slaif-local-coding/actions/runs/35526139281 (head `b3f8d9e1ee46be3e3d453c484af6d8267dbac8d6`) — 5/5 SUCCESS:
  - `test` (job 106118501412): SUCCESS — 1218 passed, 27 skipped in 43.50s (local 1219/26 + the same 1 runner-conditional skip as 013-j: `test_fresh_namespace_probe_fails_closed_for_cross_namespace_loopback` skips where no safe namespace mechanism is available; identical total 1245)
  - `gateway-contract` (job 106118501413): SUCCESS — 18/18, 0 failed, 0 skipped, network guard enabled, checkout clean, frozen peer `08ca421bee1ddca62078302b910e8be88cf705be`
  - `docker` (job 106118501287): SUCCESS — new K1 step PASSED (exact release-workflow build command + environment from fresh checkout; built image `sha256:d003ad7e...`; source/wheel/RC label assertions passed) + all 15 qualification phases PASSED (fresh wheel `ad6be6d2...` == manifest; signed-ingress positive/negative, fail-closed readiness 503, hardening/labels, operations, teardown absence proof)
  - `docker-published` (job 106118501383): SUCCESS with explicit pre-publication state `NOT RUN (pre-publication: no RC or final publication record)` — correct and intended (no publication this round); the published-image gate stays explicit NOT RUN until an actual RC exists (no invented RC record or digest)
  - `operator-session` (job 106118501407): SUCCESS — all 19 phases PASSED (documented operator lifecycle, synthetic secrets, fake upstream, local registry stand-in, teardown with absence proof)
- No repair loop was needed: the single implementation-head run was green on first push
- All required green at drafting: YES (docker-published NOT RUN is the explicit, designed pre-publication state, not a pending requirement)
- Report-head checks may be pending; strategy verifies

## Local setup/dependencies
- Repo venv (uv-managed, `uv sync --frozen --extra dev`); uv 0.12.5; Python 3.12.3 (venv) and 3.12.14 (uv-managed) for the clean builds; no new packages, no `uv.lock` churn, no protected-host tooling, no host Docker execution (daemon access denied and not used; K1's local proof used the Compose CLI's `config` interpolation only)

## Documentation
- Updated in the same round as the behavior change: README.md, docs/DOCKER-INSTALL.md, compose.build.yaml (usage comment), release-image.yml (procedure comment), ci.yml (step comments) — per constitution. No general docs rewrite.

## Safety/scope confirmations
- Unrelated/pre-existing work preserved: YES (0-byte untracked root residue `Local`/`clean`/`unchanged` left in place, untracked, excluded from all build inputs; explicit-path staging only, no `git add -A`)
- Secrets/raw content: NONE in commits, CI logs, or this report (CI uses synthetic values; the K1 temporary Compose inputs are empty/placeholder nonsecret files on disposable runners)
- Production/protected resources: NO registry write, NO dispatch, NO tag/Release/visibility/promotion, NO benchmark/telemetry code, NO `src/` runtime change, NO product behavior change, NO uv.lock churn
- Protected 18020/Qwen/Codex fixture changed: NO. Read-only baseline before AND after, row-identical: `qwen-serving-vision.service` active (running) since 2026-09-06 18:57:26 CEST, MainPID 23961 (vllm); `qwen-serving.service` inactive; sole listener `0.0.0.0:18020` (vllm 23961) among 18020/18021/18031/18033/18034 (others closed); `~/.codex/qwen-neumann.config.toml` 924 B, mode 600, mtime 2026-09-18 13:16:48 +0200, sha256 `3aef2d8b819e9a5649c1fb739cd97b885cc69dbdf04eb15db7dcdbf4fac488bb`
- Required tests skipped/not run: only the exact conditional set above (never counted as pass); `docker-published` NOT RUN pre-publication by design; local results are not presented as GitHub checks
- Scope deviation: none — the order's bounded scope only; no speculative fixes, new abstractions, or unrelated cleanup
- Extra objective PR: NO; coding merge: NO; auto-merge: NO
- Active/order edited: NO (exact strategic bytes committed once in A); report commit report-only: YES (to be verified post-push)

## Known limitations/blockers
- None blocking. Notes for strategy: (1) the K1 fix means the release workflow's build step now depends on the nonsecret build selection `SLAIF_LOCAL_CODING_IMAGE` (identical value to the build override's image field; the canonical pull-only `compose.yaml` and its explicit-image requirement are unchanged); (2) no RC exists in the registry — the publication round remains a separate continuation bound to the exact reviewed source S, which will equal the recorded 119-entry input map (verified at `b3f8d9e...`); (3) the 013-j report's nonexistent-test-name claim is corrected prospectively here, as ordered; the prior report's bytes are untouched.

## Recommended strategic follow-up
Factual only; strategy decides. PR #15 is at the implementation head `b3f8d9e1ee46be3e3d453c484af6d8267dbac8d6` with 5/5 green CI (docker-published NOT RUN pre-publication by design) and the full 013-k scope closed. The already-human-authorized private RC publication continuation can proceed from the exact reviewed source S (all 119 artifact inputs byte-equal to the recorded map at this head) under the now-working `release-image.yml` workflow_dispatch-only publisher with the explicit-verified-absent-for-both write gate.

# OAP Coding-Agent Report — 013-n

## Work order
- Identifier: 013-n; order path: `oap/orders/013-n-private-rc-publication-and-handoff.md`; numeric objective 013
- PR mode: AMENDED_EXISTING_PR (PR #15, no new PR)

## Status
COMPLETE

## Executive summary
The human-authorized private `0.1.0-rc1` image was published from the exact
reviewed image source commit S
`4d096e404e14badb78b4f99142bf08ef17f0f8a7` by dispatching the EXISTING
`workflow_dispatch`-only `release-image.yml` while the remote branch was still
exactly S and BEFORE any order/active or derived-metadata push. The run
(35533367286, head SHA verified = S, checkout verified = S, conclusion
success) built the exact S wheel (SHA-256 verified equal to the committed
manifest wheel `ad6be6d2e8ad0f99eafb4be7b1c78efbcffe6de16e39106182d85db03933ce1e`),
recorded authenticated verified-absent for BOTH `sha-<S>` and `0.1.0-rc1`
before ANY mutation, pushed the SAME image under the two RC tag aliases only,
and registry-verified that both tags resolve to the ONE actual digest
`sha256:2dd889c2841d80651eceebb0bd22397f0b9d36c5be41ed476fa2db70510d3361`.
No legacy-tag write, no visibility change (package `private` before and
after), no final tag, no GitHub Release. `packaging/rc_record.json`
(schema `slaif-rc-record-v2`) and the deterministic `packaging/rc_handoff.md`
were generated from those verified facts only; the excluded
`release_provenance_manifest.json` was regenerated in the RC-published state
bound to S (121-entry input map unchanged, mechanically proven equal at S and
at the metadata commit; objective constant kept at `013-m`). Fresh full CI at
the metadata commit R ran the REAL `docker-published` qualification against D
(12/12 phases PASSED: digest/tag pulls, matching registry digests, real
`linux/amd64`, full OCI label set, retained wheel, installed lock closure
18/17/18 at locked versions, non-editable install, no-build pull deployment,
signed-ingress positive/negative, fail-closed readiness, hardening, teardown)
alongside green test/gateway-contract/docker/operator-session. The protected
Qwen/vLLM host was verified read-only before and after, row-identical. No
source, build, docs, lock, config, test, or helper file changed. Benchmark:
NO. Final public release: NO. Protected cutover: NO. No merge.

## Authoritative GitHub state
- Repository: ulfe-lmi/slaif-local-coding; PR #15 OPEN
  https://github.com/ulfe-lmi/slaif-local-coding/pull/15
- Base: main `a04693e6792df6a8ad4262acfb46336a0f662202`; head branch
  `oap/013-mvp-release-publication`
- Starting remote SHA: `4d096e404e14badb78b4f99142bf08ef17f0f8a7` (S; verified
  report-only SELF child of metadata B
  `39f453eb931ddbcfba7a12627b32a77939686688`; fresh CI 35532806219 at S was
  5/5 SUCCESS and CI 35532178837 at B was 5/5 SUCCESS, per the activated
  order's verified baseline)
- Implementation head SHA: 9ccfb782c5e890cac3a6864639f7abd4c2f47609
- Report publication commit: SELF
- Implementation commits pushed before report: `9ccfb782c5e890cac3a6864639f7abd4c2f47609`
  (activated order/active byte-exact + derived metadata only:
  `packaging/rc_record.json`, `packaging/rc_handoff.md`,
  `packaging/release_provenance_manifest.json`)
- New PR this round: NO; amended existing PR #15: YES; merge performed: NO
- PR title/body rewritten around the final RC result and actual validation
  record (stale 013-i/v4/zero-write claims removed)

## Changes and files
- `oap/active` + `oap/orders/013-n-private-rc-publication-and-handoff.md`:
  activated order/active committed byte-exact (order sha256
  `2052ee5f331920278bb9558d28d608340daf8089445c5544a805fc14fa9dbec3`; active
  content `013-n`).
- `packaging/rc_record.json` (NEW, derived, excluded from every build
  input): schema `slaif-rc-record-v2`; `image_source_commit` = S;
  `oci_image_digest` = D; `oci_tags` = [`0.1.0-rc1`,
  `sha-4d096e404e14badb78b4f99142bf08ef17f0f8a7`];
  `published_at` = `2026-09-20T19:46:25Z` (observed successful-publication
  timestamp from the publication run log); `publication_workflow` =
  `release-image.yml`; `publication_workflow_run_id` = 35533367286;
  `workflow_head_sha` = S; `wheel_sha256` = W;
  `dependency_lock_sha256` =
  `1237cbd179f71b99984c80f927529549f5e61eb705585ef9cf2ab0fa9e26764a`
  (recomputed this round, equal to the committed `uv.lock`);
  `gateway_authority_sha` =
  `08ca421bee1ddca62078302b910e8be88cf705be`; build environment
  (hatchling 1.32.0, packaging 26.3, pathspec 1.1.1, pluggy 1.6.0,
  tomlkit 0.15.1, trove-classifiers 2026.6.1.19), toolchain
  (hatchling==1.32.0 / uv 0.12.5 / python 3.12), digest-pinned base images
  from the Dockerfile, platform `linux/amd64`, the 121-entry direct
  source-input hash map, deployment assumptions, and the const-pinned
  `private_registry_auth_required: true`, `final_public_release: false`,
  `cutover_performed: false`.
- `packaging/rc_handoff.md` (NEW, derived): deterministic rendering of the
  machine record only — literal verified identity values, the
  path→sha256 source-input map, private-registry retrieval commands
  (credentials via environment variables, never literal), identity
  verification steps (RepoDigests, OCI label set, in-image wheel hash,
  input-map mechanical verification), and explicit "what this handoff is
  NOT" (no benchmark, no cutover, no final release, no legacy-tag reuse).
- `packaging/release_provenance_manifest.json` (derived regeneration):
  schema `slaif-release-provenance-v5`; `generated_from.git_commit` re-bound
  to S (the image source commit); `objective` constant preserved at
  `013-m` (per order: source generator/test constants not followed by the new
  OAP suffix); `candidate.state: rc_published`, `status.rc_published: true`,
  `final_public_release: false`, `cutover_performed: false`;
  `oci.image_digest` = D, `oci.published: true`, qualification label
  `rc-candidate-0.1.0-rc1; private; not final release`; artifacts
  byte-identical to the qualified identities (wheel
  `ad6be6d2e8ad0f99eafb4be7b1c78efbcffe6de16e39106182d85db03933ce1e`, 26
  entries, 75554 bytes; sdist `4fc43041cc6c5f1fd92590cb24fa260d8ce2dbd8d599393fdad10eaff8a58659`,
  119 entries, 463718 bytes); 121-entry `source_inputs` unchanged;
  `build.python.observed_exact` = [`3.12.14`, `3.12.3`] with
  `wheel_patch_independent: true` (both re-observed this round);
  limitations bullets replaced exactly per the published-state rule.

## Acceptance evidence
### N1 — Publish one image from literal S
- Result: PASSED (published, verified single digest, no legacy write).
- Remote PR head at dispatch time = S (`git fetch` +
  `git rev-parse origin/oap/013-mvp-release-publication` =
  `4d096e404e14badb78b4f99142bf08ef17f0f8a7`); artifact inputs at S equal the
  qualified 121-entry recorded map
  (`python3 scripts/source_input_map.py --ref <S> --manifest ...` →
  "input-map ref OK").
- Dispatch: `gh workflow run release-image.yml --ref
  oap/013-mvp-release-publication` issued 2026-09-20T19:45:56Z while the
  remote branch was still exactly S and before ANY push of this order/active
  or derived metadata (first push of this round occurred after the run
  completed).
- Publication run: id 35533367286,
  https://github.com/ulfe-lmi/slaif-local-coding/actions/runs/35533367286,
  head SHA = S (verified via run API and the explicit
  `fetch +4d096e40…:refs/remotes/origin/oap/013-mvp-release-publication`
  checkout line in the log), conclusion success, job `build-and-publish`.
- Run credential: the existing ephemeral `GITHUB_TOKEN` with declared
  `contents: read` + `packages: write` (run log: "GITHUB_TOKEN Permissions:
  Contents: read / Packages: write"); no new credential or secret.
- Verified-absent precondition (in-run, authenticated): "registry before:
  sha-4d096e404e14badb78b4f99142bf08ef17f0f8a7 = verified absent; 0.1.0-rc1 =
  verified absent" — the ONLY write precondition; no occupied/partial/
  inaccessible state occurred, so no retry/overwrite/repoint was needed.
- In-run wheel binding: "fresh wheel sha256:
  ad6be6d2e8ad0f99eafb4be7b1c78efbcffe6de16e39106182d85db03933ce1e" ==
  "manifest wheel sha256: ad6be6d2e8ad0f99eafb4be7b1c78efbcffe6de16e39106182d85db03933ce1e".
- After-state (in-run, authenticated registry API): "registry after:
  sha-4d096e40… = present at sha256:2dd889c2841d80651eceebb0bd22397f0b9d36c5be41ed476fa2db70510d3361;
  0.1.0-rc1 = present at sha256:2dd889c2841d80651eceebb0bd22397f0b9d36c5be41ed476fa2db70510d3361";
  `SLAIF_PUBLISHED_DIGEST=sha256:2dd889c2841d80651eceebb0bd22397f0b9d36c5be41ed476fa2db70510d3361`;
  per-tag verification lines confirm BOTH tags → the ONE digest D.
- No final Git tag or additional Git tag created; no legacy-tag write
  (publisher refuses `0.1.0`/`latest`/`stable`/`v0.1.0` by construction).
- Independent after-baseline (CI docker-published job at R, authenticated
  ephemeral `packages:read` token, 2026-09-20T19:53:03Z): `0.1.0` →
  `sha256:a5debcb24bb6bbf7cf00dbf80cd17367d57186f6b0d7fadac020b94df53a0011`
  (unchanged), `sha-fe334e87c9f0fc65d1826cf9af7dad7e9f70a94a` → same digest
  (unchanged), `sha-be3c78b2016d5d40ce9155df8f94d14525c43d39` →
  `sha256:15778b30d6a929d01fa42dffccc363f89967d22d92610466bb531cca5027e113`
  (unchanged), `0.1.0-rc1` → digest D, `package visibility → private`.

### N2 — Record actual facts without moving artifact inputs
- Result: PASSED (record + handoff + manifest regeneration from verified
  facts; input maps proven equal).
- `scripts/rc_artifact_record.py` generated both files from S, D, W, run
  head/id, and the observed publication timestamp; no placeholders or
  invented identifiers (every value traceable to the publication run log or
  the committed/qualified inputs).
- Clean source S artifacts rebuilt locally this round (two isolated clean
  builds, `uv build`, uv 0.12.5): Python 3.12.14 → wheel
  `ad6be6d2e8ad0f99eafb4be7b1c78efbcffe6de16e39106182d85db03933ce1e`, sdist
  `4fc43041cc6c5f1fd92590cb24fa260d8ce2dbd8d599393fdad10eaff8a58659`;
  Python 3.12.3 → identical bytes. Both match the qualified identities
  exactly.
- `scripts/release_provenance_manifest.py --source-commit <S> --dist
  <clean build> --observed-build-python 3.12.14 --observed-build-python 3.12.3`
  regenerated the manifest in RC-published state (rc record present →
  `rc_published: true`, digest + published bullets recorded).
- Input-map proof: `scripts/source_input_map.py --ab <S> <R> --manifest ...`
  → "input-map A/B binding OK: 4d096e404e14 == 9ccfb782c5e8 (121 input
  files)" (S..R diff confined to derived metadata/OAP paths; no source
  input moved).
- Image source S, metadata commit R
  `9ccfb782c5e890cac3a6864639f7abd4c2f47609`, and report SELF are recorded
  separately (this report names R literally; SELF is the report commit whose
  first parent is R).
- Source generator/test OBJECTIVE constant preserved at `013-m`; README/docs/
  build files/lock/config/src/helpers/tests untouched (R's diff is exactly
  the five paths listed above). No new source defect demonstrated; no
  re-publication.

### N3 — Qualify the actual pulled digest and publish the reviewable result
- Result: PASSED (published job RAN — not prepublication NOT RUN — and all
  gates green at R).
- Fresh full CI run 35533735646 at R (5/5 SUCCESS; see CI section). The
  `docker-published` job: publication gate printed "publication gate: RC
  published (digest sha256:2dd889c2…, source 4d096e40…)", then executed
  authenticated digest pull, tag pulls with image-ID equality + RepoDigests
  containment of D, strict registry checks (`registry 0.1.0-rc1 ->
  digest:D`, `registry sha-4d096e40… -> digest:D`), "published image label
  set verified" (revision = S, version/`package.version` = 0.1.0, wheel = W,
  gateway peer = frozen pin, qualification + topology labels), and
  `scripts/docker_qualification_ci.py --published` against D with 12/12
  phases PASSED: `verify_wheel_binding`, `compose_rendered_validation`,
  `pull_preexistence_no_build` (image ref `@D`, pulled_before_up=true, no
  build key), `fake_upstream_start`, `adapter_stack_up` (healthy;
  image_id_matches_pull=true; 0.0.0.0:18031 host mode), `in_image_provenance`
  (non_editable=true; version 0.1.0; runtime lock closure pinned=18 /
  applicable=17 / installed=18, ok=true, locked versions exact: anyio
  4.14.2, pydantic 2.13.4, uvicorn 0.52.4, fastapi 0.141.1, httpx 0.28.1,
  starlette 1.6.0, prometheus-client 0.26.0, h11 0.16.0, httpcore 1.0.9,
  click 8.4.2, certifi 2026.7.22, annotated-types 0.8.0, annotated-doc 0.0.5,
  idna 3.19, pydantic-core 2.46.4, typing-extensions 4.16.0,
  typing-inspection 0.4.4, slaif-local-coding 0.1.0), `bridge_positive_signed`
  (chat 200; chat-stream 200, 4 SSE frames + terminal done; models 200;
  tool-roundtrip continuation 200; sentinel match), `bridge_negative_contract`
  (bad signature 403; missing token 401; replay 200→409; cross-namespace
  refused), `config_time_rejection`, `fail_closed_readiness` (readyz 503 with
  upstream unavailable), `image_content_scan` (6484 files, 0 forbidden
  matches), `hardening_and_labels` (image_platform linux/amd64; non-root,
  no_new_privileges, cap_drop_all, read_only_rootfs, no docker socket, no
  repo source bind, all OCI labels present), `teardown_absence_proof`
  (containers/listeners absent; pulled image retained).
- No gate weakened; no redundant local full-suite duplication (unchanged
  runtime covered by the fresh full CI at R).
- PR title/body rewritten around the final RC result and actual validation
  record; stale 013-i/v4/zero-write claims removed; concise reviewer-facing
  description.

## Verification
- `git fetch origin && git rev-parse origin/oap/013-mvp-release-publication`
  (pre-dispatch): PASSED — remote branch exactly S
- `gh pr view 15 --json ...`: PASSED — PR #15 OPEN, base main
  `a04693e6792df6a8ad4262acfb46336a0f662202`, head S, MERGEABLE
- `gh run view 35532806219` (report-head CI at S, baseline): PASSED — 5/5
  SUCCESS; docker-published read-only authenticated baseline at S: legacy
  digests as recorded, `0.1.0-rc1 → absent`, `visibility → private`,
  prepublication gate NOT RUN (pre-state correct)
- `python3 scripts/source_input_map.py --ref <S> --manifest
  packaging/release_provenance_manifest.json`: PASSED — "input-map ref OK:
  4d096e404e14 matches the recorded map" (121 inputs)
- `gh workflow run release-image.yml --ref oap/013-mvp-release-publication`:
  PASSED — run 35533367286 created at S, completed success
- Publication run log review (head SHA, checkout line, wheel binding,
  verified-absent-for-both, before/after registry state, single digest):
  PASSED — all as cited in N1
- `uv build --out-dir <tmp> --python 3.12.14` / `--python 3.12.3` (two
  isolated clean builds of S): PASSED — wheel `ad6be6d2…` and sdist
  `4fc43041…` reproduced byte-identical in both
- `.venv/bin/python scripts/rc_artifact_record.py --source <S> --digest D
  --head-sha <S> --published-at 2026-09-20T19:46:25Z --run-id 35533367286`:
  PASSED — record + handoff written from verified facts
- Handoff determinism re-render + secret/raw-content scan of
  `rc_record.json`/`rc_handoff.md`: PASSED — byte-identical re-render; only
  environment-variable-referencing retrieval commands, no credential values
- `.venv/bin/python scripts/release_provenance_manifest.py --source-commit
  <S> --dist <clean build> --observed-build-python 3.12.14
  --observed-build-python 3.12.3`: PASSED — RC-published manifest written
- `python3 scripts/source_input_map.py --ab <S> <R> --manifest ...`: PASSED —
  "input-map A/B binding OK … (121 input files)"
- `.venv/bin/python -m pytest -q tests/test_release_provenance_manifest.py`:
  PASSED — 21 passed (against the regenerated manifest)
- `.venv/bin/python -m pytest -q tests/test_rc_record.py
  tests/test_docker_qualification_record_gate.py
  tests/test_release_registry_publish_digest.py
  tests/test_release_registry_publish_gate.py`: PASSED — 96 passed
- Fresh full CI at R, run 35533735646 (5 check runs, all SUCCESS — see CI
  section): PASSED
- Local live vLLM matrix / real-Codex E2E: NOT RUN — not ordered this round
  (publication/record round; live matrix not required by 013-n and unchanged
  runtime is covered by fresh full CI)

## Live model/service evidence
- No live model inference performed (none ordered). No host Docker daemon
  use; all Docker qualification ran on disposable GitHub runners.
- Protected baseline verified read-only BEFORE (2026-09-20T19:44Z) and AFTER
  (2026-09-20T19:56Z) the round, row-identical: user unit
  `qwen-serving-vision.service` active (running) since
  `Sun 2026-09-06 18:57:26 CEST`, MainPID 23961 (vllm); only 18020 listening
  among 18020/18021/18031/18033/18034; `qwen-neumann` profile sha256
  `3aef2d8b819e9a5649c1fb739cd97b885cc69dbdf04eb15db7dcdbf4fac488bb`
  unchanged; frozen Gateway authority fixture
  `08ca421bee1ddca62078302b910e8be88cf705be` unchanged (not in any diff).
- Coding provider remains the protected qwen-neumann/qwen-LSI-A100 Responses
  path (http endpoint per environment, model qwen3.8-27b) — untouched; not a
  benchmark VM.
- Registry facts were obtained only through authenticated CI/workflow
  credentials (ephemeral `packages:read`/`packages:write` workflow tokens),
  never printed secrets.

## GitHub CI / required checks
- Implementation head R check state (run 35533735646, created
  2026-09-20T19:52:51Z, completed 2026-09-20T19:54:30Z, all SUCCESS):
  - `test`: SUCCESS — `1277 passed, 27 skipped in 65.09s`; ruff check,
    ruff format --check, mypy src tests, docs consistency gate, `uv build`,
    artifact content policy + fresh-venv install smoke, compileall all
    passed (job success)
  - `gateway-contract`: SUCCESS — frozen peer `08ca421bee1ddca62078302b910e8be88cf705be`,
    `tests_collected: 18, tests_failed: 0, tests_passed: 18, tests_skipped: 0`
  - `docker`: SUCCESS — 15/15 phases PASSED (build mode, same dependency/
    platform gates)
  - `docker-published`: SUCCESS — RAN against D (not prepublication NOT
    RUN); 12/12 phases PASSED (published mode; evidence in N3)
  - `operator-session`: SUCCESS — 19/19 phases PASSED (documented operator
    lifecycle, synthetic registry + fake upstream, teardown with absence
    proof)
- All required green at drafting: yes (5/5 at implementation head R)
- Report-head checks may be pending; strategy verifies

## Local setup/dependencies
- Repo venv (Python 3.12.14), system Python 3.12.3, `uv` 0.12.5 (matching the
  pinned toolchain); no new dependencies, no new services, no sudo actions.
- Temporary build outputs kept in `/tmp` only; nothing added to the
  repository beyond the five committed paths.

## Documentation
- Not modified this round (frozen by order: README/docs/build files/lock/
  config/src/helpers/tests unchanged). The published-state documentation
  surface is carried by the regenerated manifest's truthful
  published-state limitation bullets and by `packaging/rc_handoff.md`
  (consumer-facing retrieval/verification) — both derived, excluded from
  artifact inputs.

## Safety/scope confirmations
- Unrelated files: R's diff is exactly `oap/active`,
  `oap/orders/013-n-private-rc-publication-and-handoff.md`,
  `packaging/rc_record.json`, `packaging/rc_handoff.md`,
  `packaging/release_provenance_manifest.json`; pre-existing untracked
  placeholder files (`Local`, `clean`, `unchanged`) preserved, untouched,
  untracked.
- Secrets/raw content: none in evidence, record, or handoff (secret scan
  performed; only env-var-referencing commands); no credentials in the
  handoff; registry credentials only ephemeral workflow tokens, never
  printed.
- Production/protected resources: no host Docker daemon use; no Qwen test
  inference; no port 18020 / qwen-serving / model / checkpoint / patch /
  venv / systemd / launch / API-key / firewall / VPN / network-binding /
  profile mutation; protected checks read-only before/after, row-identical.
- No benchmark design/code/tasks/judges/controller/ledger/A100 setup/pilot/
  experiment/statistics/telemetry/instrumentation; no
  `experiments/codex_adapter_benchmark`.
- No final `v0.1.0` tag, no GitHub Release, no final release claim, no
  public visibility change, no protected-host cutover, no Gateway routing
  mutation.
- Protected 18020/Qwen/Codex fixture changed: NO.
- Required tests skipped/not run: local live vLLM matrix and real-Codex E2E
  NOT RUN (not ordered this round); everything else required by 013-n ran
  (see Verification).
- Scope deviation: none.
- Extra objective PR: NO. Coding merge: NO. Auto-merge/force-push: NO.
- Active/order edited: NO (committed byte-exact from the strategic files).
- Report commit report-only: YES (staged exactly one path; verified before
  push).

## Known limitations/blockers
- The local `gh` credential (scopes `repo`, `workflow`, `read:org`) cannot
  resolve the private GHCR package (403: "You need at least read:packages
  scope"); local registry truth is therefore `unauthorized` from this
  credential, and registry facts in this round come from the authenticated
  workflow/CI ephemeral credentials (publication-run before/after state and
  the docker-published baseline), consistent with prior rounds. No new
  credential or privilege was introduced.
- Qualification is for `linux/amd64` only (other architectures not
  qualified); deployment assumptions recorded in the RC record.
- Final public release and protected-host cutover remain separate later
  human-authorized acts; nothing in this round claims either.

## Recommended strategic follow-up
Factual only; strategy decides.
- Strategy may review/merge PR #15 at its discretion (merge is NOT
  performed by coding).
- A later human final-release decision can promote the SAME tested digest D
  without rebuilding (recorded in the handoff and manifest).
- If strategy wants local (non-CI) registry verification on this host, a
  credential with `read:packages` for the org would be required; this is a
  privilege decision outside this round's authority.

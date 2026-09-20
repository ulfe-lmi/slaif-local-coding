# OAP Coding-Agent Report — 013-j

## Work order
- Identifier: `013-j`; order path: `oap/orders/013-j-close-rc-source-review-gaps.md`; numeric objective: 013
- PR mode: AMENDED_EXISTING_PR

## Status
COMPLETE

## Executive summary
All six source-review gaps (J1–J6) are closed on PR #15 (amended, no new PR,
no merge). The publisher now enforces verified-absent-for-both as the ONLY
write precondition with zero-mutation proof on every stop case; documentation
is release-state-free and the operator session is coherent and mechanically
proved in disposable CI (new `operator-session` job, 19/19 phases PASSED);
the build environment is fully pinned and mechanically asserted; provenance is
bound to the exact final source commit by a 119-entry input hash map with
derived-only A..HEAD discipline; the RC record is a closed 23-key v2 set with a
deterministic no-OAP-knowledge handoff renderer; and the 013-h
implementation-head/report-parent relationship plus the historical sdist
hash transcription are corrected without touching any historical report or
order bytes. Fresh CI at the implementation head is 5/5 SUCCESS, with
`docker-published` explicitly NOT RUN pre-publication (by design). No registry
write, tag, dispatch, Release, or visibility change occurred this round.

## Authoritative GitHub state
- Repository: `ulfe-lmi/slaif-local-coding`; PR #15 https://github.com/ulfe-lmi/slaif-local-coding/pull/15 (OPEN, non-draft, MERGEABLE)
- Base `main` = `a04693e6792df6a8ad4262acfb46336a0f662202`; starting remote head `fac713577c69c9dff8355f4d8b9070238b514cd5` (matches order)
- Implementation head SHA: `e1ef4970a658e33418b9688b25aeed55f18e6dd9`
- Report publication commit: SELF
- Implementation commits pushed before report (10, in order):
  - `641baa24ae812747fd29a04bd9ad036168a78f3a` (A — J1–J6 implementation, 28 files)
  - `bd1736f0caecb5a5314bac430852001672de17c9` (B — manifest bound to A; superseded)
  - `e30f1b0d5a4255909ecf69262825586be7196a6a` (A′ — E3 regeneration-fixture correction: it now records the exact running interpreter, required by schema v5's non-empty observed scope)
  - `17ab687e5b9d6631d0b04ddeacbb0123df7237bc` (B′ — manifest bound to A′; superseded)
  - `c6a0905044964ee86b4c4e6e173d98b9b07ea544` (CI repair 1 — operator-session verifies protected site perms via the admin channel)
  - `4371af551ca3849a09dca464eb9252d57a283137` (B″ — manifest re-bound to c6a0905; superseded)
  - `cfa979e72628326b059b556e613bb3318e43fa71` (CI repair 2 — bounded wait loops tolerate connection-refused probes)
  - `718e493963cc4faf16e4a910414466378ef4ece8` (B‴ — manifest re-bound to cfa979e; superseded)
  - `5ba727988783cdedde774a64e012ed9f2e3fd6c5` (CI repair 3 — the OPERATOR account owns the 0700 site directory so the Compose client can read the 0600 env file; documented flow corrected in QUICKSTART/INSTALL and mirrored in the CI script)
  - `e1ef4970a658e33418b9688b25aeed55f18e6dd9` (B⁓ — manifest of record, bound to the final source commit 5ba7279)
- The superseded intermediate manifest commits (B, B′, B″, B‴) are retained in history unmodified; the committed manifest at the implementation head is bound to `5ba727988783cdedde774a64e012ed9f2e3fd6c5` and carries the final artifact identities below. The rebinds were forced by the J4 discipline rule (any source-path change after the recorded source commit requires rebinding), triggered by the E3 fixture correction and the scripts/docs CI repairs; each rebind is provably artifact-preserving (below).
- New PR this round: NO; amended existing: YES (PR #15); merge performed: NO
- Candidate image source commit: NONE (no image is published this round; source S will be the exact reviewed workflow checkout in the continuation)

## Changes and files
- J1: `scripts/release_registry_publish.py` (pure `plan_pre_write` gate; authenticated strict tri-state checks of BOTH tags before ANY mutation; immediate pre-write rechecks; explicit expected RC1 identity `0.1.0-rc1` / repository / 40-hex source SHA validated before any Docker mutation; partial-publication (source pushed, candidate absent) reported, never silently completed; malformed digests fail closed), `.github/workflows/release-image.yml` (concurrency group `slaif-rc-publisher`, `cancel-in-progress: false`; verified-absent-for-both law in workflow law comments; `sha-<S>` documented as mutable source alias).
- J2: `README.md` (release-state-free; Release status section + Objective-013 tag history removed, disposition moved to OAP transcript/artifact policy links), `ARCHITECTURE.md` (current-state corrected: R18-hold language replaced with frozen peer `08ca421bee1ddca62078302b910e8be88cf705be` + separate-later-round framing), `docs/RELEASE-CUTOVER-RUNBOOK.md` (013-b attribution corrected; historical prose unmistakably historical), `QUICKSTART.md` + `INSTALL.md` (one exported operator session across ALL compose commands incl. ps/logs/stop/start/restart/down/upgrade/rollback; `linux/amd64` stated; `read:packages` PAT scope distinct from Actions `packages: read`; admin steps = directory creation + the two file-ownership steps; `${SECRET:?}` fail-closed guards; documented docker-health wait (no missing `readyz-wait.sh`); `RepoDigests` digest verification; systemd section links the exact DEPLOYMENT.md signed Gateway-integrated recipes, unsigned dev mode clearly separate; no "stop arbitrary port owners"), `docs/DOCKER-INSTALL.md`, `docs/RC-HANDOFF.md`, `docs/RELEASE-ARTIFACT-POLICY.md`, `docs/TOPOLOGY.md` (mutable source alias terminology), `scripts/docs_consistency_check.py` (concrete regression patterns), `scripts/operator_session_ci.py` (NEW: disposable-CI proof of the documented lifecycle with synthetic secrets + fake upstream), `.github/workflows/ci.yml` (new `operator-session` job; `docker-published` gained `RepoDigests` assertions).
- J3: `pyproject.toml` (`[build-system].requires` = 6 exact `name==version` pins; `packaging/rc_handoff.md` build exclusion), `scripts/release_provenance_manifest.py` (`_assert_build_environment_pins` asserts the recorded build environment equals the enforced 6-pin set on every generation; exact observed interpreter scope `3.12.3` + `3.12.14` with `wheel_patch_independent`).
- J4: `scripts/source_input_map.py` (NEW: 119-entry path→sha256 map of all wheel/sdist/OCI/config inputs incl. README, pyproject, uv.lock, src/, Dockerfile, compose.yaml, compose.build.yaml, .dockerignore, config templates, packaging inputs; explicit exclusions for generated manifests/RC records/handoff and OAP — no self-reference; `--ab` binding check rejects a valid-shaped wrong source, altered/missing/changed inputs, and any non-derived path in A..HEAD even for ancestors), manifest v5 carries the map.
- J5: `scripts/rc_artifact_record.py` + `packaging/rc_artifact_record.schema.json` (closed 23-key v2 record: source input hash map, Compose identity, build-environment pins, base-image identities, platform, product/RC IDs, source, digest/reference, tags, wheel, lock, frozen Gateway authority, private-auth required, `final_public_release=false`, `cutover=false`; deterministic handoff renderer from the same machine facts — literal verified values + retrieval/verification commands, no OAP knowledge, no image rebuild), `scripts/release_provenance_manifest.py` (digest-claim corrected: machine validation cannot authenticate an arbitrary digest; trust boundary documented, real publication bound to run head SHA + authenticated registry digest + pulled-image qualification).
- J6: `oap/README.md` (field-law paragraph corrected with verified parentage; no historical report/order bytes touched), `pyproject.toml` comment (historical sdist full hash corrected).
- Transcript: exact activated order bytes `oap/orders/013-j-close-rc-source-review-gaps.md` + `oap/active` → `013-j` committed unchanged.

## Acceptance evidence
### J1 — reject occupied/unresolved tags BEFORE registry writes
- Result: PASSED. `plan_pre_write` is a pure gate returning "proceed" ONLY for verified-absent-for-both; `main()` performs authenticated strict tri-state checks of BOTH tags, the gate, an immediate pre-write recheck (and a candidate-tag recheck immediately before its write), then source push → digest equality vs registry API → candidate push → final both-tags→one-digest verification. Forbidden final tags, wrong RC identity, and wrong repository fail before any Docker mutation.
- Evidence: 26 tests in `tests/test_release_registry_publish_gate.py` execute the mocked `main()` control flow and assert ZERO tag/push mutations: `test_occupied_source_tag_zero_mutations`, `test_occupied_rc_tag_different_digest_zero_mutations`, `test_occupied_rc_tag_same_digest_zero_mutations`, `test_partial_prior_publication_zero_mutations`, `test_unauthorized_state_zero_mutations`, `test_unknown_status_zero_mutations`, `test_malformed_digest_zero_mutations`, `test_unresolved_registry_error_zero_mutations`, `test_forbidden_final_tag_zero_touch` (4 params), `test_wrong_rc_identity_zero_touch`, `test_wrong_repository_zero_touch`, plus the exact success call sequence (`tag → push → recheck → tag → push`, registry API verification, `GITHUB_OUTPUT` + `SLAIF_PUBLISHED_DIGEST`), the pre-write recheck race (zero push), and partial-stop after source push (exactly one tag + one push). Full tri-state matrix in `test_plan_pre_write_matrix` (10 params).
- Terminology: `sha-<S>` is documented as a mutable source alias everywhere in current prose (release-image.yml law comments, README, RC handoff, TOPOLOGY); the digest remains the content-addressed authoritative identity.

### J2 — durable documentation + executable operator paths
- Result: PASSED. README is release-state-free (docs gate forbids release-state claims on the landing page). QUICKSTART/INSTALL are one coherent exported session; all documented retrieval is self-contained (no missing `readyz-wait.sh`/`curl` prerequisite); admin prerequisites and UID-10001 ownership are coherent (the operator owns the 0700 site directory and the 0600 env file — required because the Compose client reads the env file on the host side — and only the config is chowned to 10001:10001); `read:packages` vs `packages: read` distinguished; `RepoDigests` verification documented; systemd section links DEPLOYMENT.md §4/§12 exact recipes; `linux/amd64` documented.
- Evidence: `scripts/docs_consistency_check.py` PASSED (13 claim docs) with the extended negative fixtures; 28/28 `tests/test_docs_consistency.py` PASSED; the documented primary lifecycle is proven in disposable CI by the new `operator-session` job (run 35523079595, job https://github.com/ulfe-lmi/slaif-local-coding/actions/runs/35523079595/job/106110429674): 19/19 phases PASSED — preflight (protected ports 18020/18021 free; doc-mirror of every executed compose subcommand/export/site-path), manifest-bound wheel build, local `registry:2` on 18040 as private-package stand-in, push digest D, site files (0700 operator-owned / env 0600 operator / toml 0600 owned 10001:10001), synthetic secrets, digest-form `compose pull`, tag-form pull + `RepoDigests` assertion, `up -d`, documented 36×5s health-wait, host `/readyz` 200, `ps`/`logs` with zero-synthetic-secret assertion, `stop`/`start`/`restart` with readiness re-waits, `down`, teardown with absence proof. Local registry digest differs per run (disposable stand-in); the private GHCR package was NOT touched.
- CI repairs landed inside this criterion (truthful sequence): run 35521156031 failed on a non-root `stat` of the 0700 root-managed site (EACCES by design) → admin-channel verification; run 35521784232 failed on a connection-refused probe crashing the fake-upstream wait loop → probes return (0, b"") and bounded waits retry, terminal checks fail closed on 0; run 35522232760 failed `compose up -d` on `open /opt/slaif/adapter.env: permission denied` — a latent defect of the DOCUMENTED flow (root-owned 0700 dir + 0600 env unreadable by the composing operator) → corrected documented flow + mirrored CI script, locally verified (operator reads env; `nobody` denied; modes/owners exact).

### J3 — enforce the build environment provenance claims
- Result: PASSED. `[build-system].requires` now pins the complete resolved build environment exactly: `hatchling==1.32.0, packaging==26.3, pathspec==1.1.1, pluggy==1.6.0, tomlkit==0.15.1, trove-classifiers==2026.6.1.19` (BUILD-time only; no runtime/uv.lock churn — `uv lock --check` PASSED). `_assert_build_environment_pins` fails generation on any drift between the recorded `build.build_environment` and the enforced pins (every requires entry must be exact `name==version` and the sets equal). `build.python` records the EXACT observed interpreters (`3.12.3`, `3.12.14`) and `wheel_patch_independent: true` (two distinct patch versions), never a bare "3.12"; `runtime_requirement: ">=3.12"`.
- Evidence: two isolated clean builds of the same final source tree (fresh `git archive` extractions) are byte-identical for wheel AND sdist; the direct `uv build --wheel` path is byte-identical to the sdist→wheel path (CI wheel binding relies on this).

### J4 — provenance bound to actual source inputs
- Result: PASSED. The committed manifest v5 carries the 119-entry `source_inputs` path→sha256 map and is bound to the exact final source commit `5ba727988783cdedde774a64e012ed9f2e3fd6c5`; `scripts/source_input_map.py --ab` proves the map at the recorded source equals the map at the manifest commit and that the diff touches ONLY derived metadata (this round: exactly `packaging/release_provenance_manifest.json`).
- Evidence: 10/10 `tests/test_source_input_binding.py` PASSED — synthetic-git negative cases (altered README, altered uv.lock, missing config/compose, sibling non-ancestor, wrong recorded map, valid-shaped-but-wrong-source — all unconditional, none relying on pre-publication conditionality) plus the real-repo gate: committed `source_inputs` == `map_from_git_commit(5ba7279)` == `map_from_directory(working tree)`, with 5ba7279..HEAD ⊆ derived metadata.

### J5 — self-contained RC handoff record
- Result: PASSED. The v2 record is a closed 23-key set carrying the exact path→hash source-input map, Compose identity, build-environment pins, digest-pinned base identities, `linux/amd64`, product `0.1.0` / RC `0.1.0-rc1`, source, digest/reference, tags, wheel, lock, frozen Gateway authority `08ca421bee1ddca62078302b910e8be88cf705be`, `private_registry_auth_required: true`, `final_public_release: false`, `cutover_performed: false`. The human-readable handoff is rendered deterministically from the SAME machine facts (no OAP knowledge — asserted by tests; literal verified values and retrieval/verification commands; `rc_handoff.md` excluded from artifact inputs so recording a digest never requires another image). The generator's digest claim is corrected (machine validation cannot authenticate an arbitrary digest; publication binds to the run's exact head SHA + authenticated registry digest + pulled-image qualification).
- Evidence: 26/26 `tests/test_rc_record.py` PASSED (23-key closed set, `--head-sha` law, drift refusal on altered working tree, renderer determinism + literal values + no-OAP assertions, frozen-identity law on record AND handoff, strict-loader roundtrip, no-fake-digest mode).

### J6 — prospective historical explanation corrected without rewriting records
- Result: PASSED. `oap/README.md` field-law paragraph now records the verified parentage (git-verified this round): 013-g SELF `881f1f36...` first parent `fe334e87...` = named implementation head (genuinely equal); 013-h SELF `64068209...` first parent `881f1f36...` while its named implementation head was the UNCHANGED `fe334e87...` (NOT equal — the earlier "coincidence of equal facts" explanation was inaccurate for 013-h); 013-i SELF `fac7135...` first parent `317cc272...` (equal). No historical report or order bytes were touched (all prior artifacts remain immutable).
- Historical sdist hash: the 013-i report's string `5a60cd6ef41764f16871fd0134b6c234409ba2708b31e863fc84e7e520f` is a MALFORMED 59-character transcription; the authoritative 64-hex full hash recorded at 013-g (immutable commit `fe334e8...` and the 013-g report, 3 occurrences) is `5a60cd6ef41764f16871fd0134b6c234409ba2708b3159bdc0863fc84e7e520f` (439,900 B, 108 entries, W6b `fe334e87c9f0fc65d1826cf9af7dad7e9f70a94a`). This is a TRANSCRIPTION CORRECTION of a previously recorded fact (now also recorded in the pyproject build-pin comment), not a new measured build fact.

## Verification
- `uv run --frozen ruff check .`: PASSED (all checks passed, 384 files)
- `uv run --frozen ruff format --check .`: PASSED (384 files already formatted)
- `uv run --frozen mypy src tests`: PASSED (strict; 76 source files)
- `uv run --frozen python -m compileall -q src tests oap/bin scripts`: PASSED
- `bash -n oap/bin/*.sh packaging/*.sh`: PASSED
- `uv run --frozen python scripts/docs_consistency_check.py`: PASSED (13 claim docs)
- `uv run --frozen pytest -q` (local, implementation head): PASSED — 1213 passed, 26 skipped, 0 failed. The 26 skips are the exact conditional set: 18× `SLAIF_GATEWAY_ROOT` unset (gateway contract/162 focused tests — exercised instead by the dedicated CI job), 7× `SLAIF_LIVE_TEST` unset (live-service tests), 1× protected vision fixture requires human activation.
- Two clean builds from the final source commit `5ba7279...` (fresh `git archive` extractions): PASSED — byte-identical wheel `3c4c36e666fb67f6a8ed0bbf1a60962e187e46ba1183f314eba03100ce2006af` (75,651 B, 26 entries) and sdist `036fe275ae50a32cb45355d184033c4df6cd29cc3682c99c61aa584dc53c226a` (453,899 B, 117 entries) across Python 3.12.3 (repo venv) and 3.12.14 (uv-managed), uv 0.12.5; the earlier A/A′ builds were byte-identical for the wheel across all five source commits of this round (docs/scripts-only deltas never touch the wheel; the sdist changed at 5ba7279 because the corrected operator docs ARE sdist inputs — honestly re-recorded in the manifest of record)
- `uv run --frozen python scripts/artifact_policy_check.py --dist <dist> --inspect`: PASSED (ok=true, zero violations; wheel entries = package only)
- `uv run --frozen python scripts/artifact_policy_check.py --dist <dist> --install-smoke`: PASSED (fresh-venv wheel install, version 0.1.0)
- `uv run --frozen python scripts/source_input_map.py --ab 5ba7279... e1ef497... --manifest packaging/release_provenance_manifest.json`: PASSED (119 input files, derived-only diff)
- `uv lock --check`: PASSED (no lock churn)
- Strict frozen Gateway contract (`scripts/gateway_contract.py --gateway-root <depth-1 clone of ulfe-lmi/slaif-api-gateway @ 08ca421bee1ddca62078302b910e8be88cf705be> --run-tests`, isolated venv): PASSED — 18/18, 0 failed, 0 skipped, 0 errors, network guard enabled, checkout clean
- Admin-channel site-permission verification (non-root caller against an equivalent 0700/0600/10001 fixture; direct non-root stat EACCES by design): PASSED

## Live model/service evidence
- No live model or service calls were made this round (no live call was required by the order). The protected Qwen/vLLM vision service was observed READ-ONLY before and after the round (see Safety/scope confirmations); the fixture is unchanged.

## GitHub CI / required checks
- Implementation-head run: https://github.com/ulfe-lmi/slaif-local-coding/actions/runs/35523079595 (head `e1ef4970a658e33418b9688b25aeed55f18e6dd9`) — 5/5 SUCCESS:
  - `test`: SUCCESS — 1212 passed, 27 skipped in 73.77s (the 26 local conditional skips + 1 additional conditional skip on the hosted runner: `test_fresh_namespace_probe_fails_closed_for_cross_namespace_loopback` skips when no safe namespace mechanism is available to the runner; identical total test count 1239)
  - `gateway-contract`: SUCCESS — 18/18 at frozen peer `08ca421bee1ddca62078302b910e8be88cf705be`, network guard enabled
  - `docker`: SUCCESS — all 15 phases PASSED (build with fresh wheel `3c4c36e6...` == manifest wheel; C2–C9 incl. signed-ingress positive/negative, fail-closed readiness 503, hardening/labels, stop/start/recreate/upgrade/rollback, teardown absence proof)
  - `docker-published`: SUCCESS with explicit pre-publication state `NOT RUN (pre-publication: no RC or final publication record)` — correct and intended (no publication this round)
  - `operator-session`: SUCCESS — 19/19 phases PASSED (documented operator lifecycle, synthetic secrets, fake upstream, local registry stand-in)
- Repair-loop runs at earlier heads (truthful record): 35521156031 (head `17ab687...`) operator-session FAILURE (non-root stat EACCES on protected site files) → repair `c6a0905`; 35521511017 (head `c6a0905...`) FAILURE (J4 discipline: scripts/ changed after the recorded source commit) → rebind `4371af5`; 35521784232 (head `4371af5...`) operator-session FAILURE (connection-refused probe crashed the wait loop) → repair `cfa979e`; 35522232760 (head `718e493...`) operator-session FAILURE (`compose up -d`: env file unreadable by the composing operator — documented-flow defect) → repair `5ba7279` + docs correction; 35523079595 (head `e1ef497...`) 5/5 SUCCESS.
- All required green at drafting: YES (docker-published NOT RUN is the explicit, designed pre-publication state, not a pending requirement)
- Report-head checks may be pending; strategy verifies

## Local setup/dependencies
- Repo venv (uv-managed, `uv sync --frozen --extra dev`); uv 0.12.5; Python 3.12.3 (venv) and 3.12.14 (uv-managed) for the clean builds; passwordless sudo used ONLY for the disposable local permission-fixture probes under `/tmp` (created and removed; no `/opt` touch, no protected state). No durable docs/config changed beyond the committed documentation.

## Documentation
- Updated: README.md, QUICKSTART.md, INSTALL.md, ARCHITECTURE.md, docs/DOCKER-INSTALL.md, docs/RC-HANDOFF.md, docs/RELEASE-ARTIFACT-POLICY.md, docs/RELEASE-CUTOVER-RUNBOOK.md, docs/TOPOLOGY.md, oap/README.md (field law), pyproject.toml build-pin comment, release-image.yml + ci.yml comments — same-round as the behavior/config changes, per constitution.

## Safety/scope confirmations
- Unrelated/pre-existing work preserved: YES (the 0-byte untracked root residue `Local`/`clean`/`unchanged` predates this round, was left in place, and is excluded from all build inputs); explicit-path staging only (no `git add -A`)
- Secrets/raw content: NONE in commits, CI logs, or this report (synthetic CI values only; the operator-session job asserts zero synthetic-secret presence in the captured log tail)
- Production/protected resources: NO registry write, NO dispatch, NO final tag/Release/visibility/promotion, NO benchmark/telemetry code, NO protected-host Docker run (the operator lifecycle ran on disposable CI only), NO Qwen inference/service mutation, NO Gateway routing change, NO network/firewall/VPN/profile/key changes, NO `src/` runtime change, NO uv.lock churn
- Protected 18020/Qwen/Codex fixture changed: NO. Read-only baseline, before AND after the round, row-identical: `qwen-serving-vision.service` active (running) since 2026-09-06 18:57:26 CEST, MainPID 23961 (vllm); `qwen-serving.service` inactive; sole listener `0.0.0.0:18020` (vllm 23961) among 18020/18021/18031/18033/18034 (others closed); `~/.codex/qwen-neumann.config.toml` 924 B, mode 600, mtime 2026-09-18 13:16:48 +0200, sha256 `3aef2d8b819e9a5649c1fb739cd97b885cc69dbdf04eb15db7dcdbf4fac488bb`
- Required tests skipped/not run: only the exact conditional set above (never counted as pass); `docker-published` NOT RUN pre-publication by design; local results are not presented as GitHub checks
- Scope deviation: the three CI repairs were in-scope repairs of in-scope new machinery (per the order's "inspect and safely repair in-scope CI failures"); each forced a manifest rebind under the J4 discipline, and the final chain is reported exactly (no force-push, no history rewrite)
- Extra objective PR: NO; coding merge: NO; auto-merge: NO
- Active/order edited: NO (exact bytes committed once); report commit report-only: YES (verified post-push)

## Known limitations/blockers
- None blocking. Notes for strategy: (1) the operator-session job is new and was repaired three times before green — the repaired flow is now documented AND mechanically proved; (2) the CI `test` job's 27th conditional skip (namespace mechanism unavailable on hosted runners) is an environment difference, not a coverage loss (the deterministic structural equivalent is the enforced contract per the test's own skip text); (3) the superseded intermediate manifest commits remain in PR history as the truthful rebind trail; (4) no RC exists in the registry — the publication round remains a separate continuation bound to the exact reviewed source S.

## Recommended strategic follow-up
Factual only; strategy decides. PR #15 is at the implementation head with 5/5 green CI (docker-published NOT RUN pre-publication by design) and the full 013-j scope closed. The next continuation can bind the exact reviewed source S (the reviewed workflow checkout, all artifact inputs identical to `5ba7279...`) for the private RC publication already authorized by the human, under the existing `release-image.yml` workflow_dispatch-only publisher with the J1 verified-absent-for-both gate.

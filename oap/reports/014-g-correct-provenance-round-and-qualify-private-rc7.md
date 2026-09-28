# OAP Coding-Agent Report — 014-g

## Work order
- Identifier: 014-g; order path: `oap/orders/014-g-correct-provenance-round-and-qualify-private-rc7.md`; numeric objective 014
- PR mode: AMENDED_EXISTING_PR — PR #19 (exactly one Objective-014 PR), never merged
- Round character: continuation suffix; the round corrects execution ordering and
  the abandoned 014-f instruction conflict only (manifest objective stays the
  historical producing round `014-e` embedded in retained A7)

## Status
COMPLETE

## Executive summary
Discarded the invalid local-only 014-e freeze commits (`11cec47d…`, message-only
replacement `25d66a6d…`), restored HEAD to the byte-exact retained A7, and
committed this round's activation transcript (immutable 014-f + 014-g orders +
`oap/active=014-g`) as the first 014-g commit. Rebuilt A7 cleanly under both
available CPython 3.12 patch environments (byte-identical wheel/sdist, hashes
exactly as the order requires), generated the pre-freeze manifest with the
historical objective `014-e`, left its bytes UNCOMMITTED, and ran the entire
local gate (including the full pytest suite, the PRE-mode record-present
rehearsal with all tamper cases, and the focused suites) green against those
exact bytes. Only then committed them once as the sole valid S7 freeze,
proving pre-commit/committed byte identity, the A7..S7 derived-only diff, and
127-entry source-input map equality at both refs. Pushed S7, obtained fully
green CI + CodeQL with zero open alerts, verified both target aliases absent
(authenticated strict checks inside the fail-closed publisher, before mutation
and immediately before writes), published exactly the two private RC7 aliases
from exact S7 to one new digest D7, ran a fresh bounded standalone genuine-
Codex 0.149.0 qualification (VISION/CACHE/BOTH + DIRECT all PASS, protected
state unchanged, 18031 torn down), committed the immutable testing ledger 005
plus the record/handoff/rc-published manifest as the only post-freeze material,
and obtained fully green final-head CI/CodeQL with `docker-published` pulling
the actual D7 and passing all 13 phases. No tracked source correction occurred
after S7. No merge, no second PR, no protected-host mutation, no benchmark,
no final public release, no cutover.

## Authoritative GitHub state
- Repository: `ulfe-lmi/slaif-local-coding`
- PR: #19, OPEN, non-draft, MERGEABLE; base `main` at
  `8c3c6d6cd67a34ba7d427ab255a91bd6a9753bd1`; head branch
  `oap/014-real-codex-compatibility-rc3`
- Remote PR head at round start: `6f82b46557b1e99e49fcc9172f702bfc8c11593c`
  (014-c SELF, unchanged at reconciliation)
- Implementation head SHA: `9169409720905a69627c9119fb3258faf0344a43`
- Report publication commit: SELF
- Commit chain pushed this round (oldest → newest, all remote):
  - `bcfb182d9337e8e52d954785f5b5ddd858a216a2` — Objective 014-e transcript
    (previously local-only; 014-e activation commit, byte-exact strategic
    bytes; no report was ever produced for 014-e)
  - `0f999e77b487b757841e288897bc9c74e411a28b` — A7, retained artifact-input
    source (previously local-only)
  - `969bbb2bf6005293095e4ceb363bd3cd16404741` — 014-g activation transcript:
    immutable orders 014-f + 014-g (byte-exact: 014-f
    `9b6a92e1…319569603`, 014-g `6dd4f6c3…2da2aafe86`) + `oap/active=014-g`
  - `ae6271318627703785f42de57d893c9be3b980c9` — S7, sole valid RC7 freeze
  - `9169409720905a69627c9119fb3258faf0344a43` — B7, post-freeze derived
    material only (record, handoff, rc-published manifest, ledger 005)
- Discarded local-only invalid freezes (never remote, never reused):
  `11cec47d1951e3ae67344facbd07e8e4d48e35d8` and its message-only replacement
  `25d66a6d8d54acf624f9bb178b21d3f4b20b90bb` (identical tree
  `3b43b7d67ce0d346b6ab6511fe7d8f0dfeb77411`; A7 tree
  `cc22700b92dfcc652a797e0b0cd26a4934ae552a`); `git reset --hard A7` removed
  them from the branch before the 014-g transcript commit
- New PR this round: NO; amended existing PR #19: YES; merge performed: NO

## Changes and files
- `969bbb2`: `oap/active` (`014-e` → `014-g`), added `oap/orders/014-f-*.md`,
  `oap/orders/014-g-*.md` (strategic bytes committed unchanged; verified
  post-commit against the on-disk originals)
- `ae62713` (S7): `packaging/release_provenance_manifest.json` only —
  objective `014-e` (historical producing round embedded in A7, preserved),
  candidate `0.1.0-rc7` state `pre_freeze`, `generated_from.git_commit` = A7,
  no OCI digest, 127-entry source-input map, freshly reproduced artifact
  hashes (wheel `897ef605…`, sdist `65527c6f…`); byte-identical to the bytes
  the abandoned 014-e worker generated from the same inputs (regenerated
  independently this round and re-tested before commit)
- `9169409` (B7): `packaging/rc_record.json` (slaif-rc-record-v3, all
  source/workflow-head/revision bindings = S7), `packaging/rc_handoff.md`,
  `packaging/release_provenance_manifest.json` re-bound to `rc_published`
  (objective `014-e` and the 127-entry map preserved), `oap/evidence/
  testing-ledger/005/` (README + closed-schema facts + MANIFEST.sha256)
- No other path changed in this round; the stray untracked zero-byte files
  `Local`, `clean`, `unchanged` remain untracked and uncommitted

## Acceptance evidence
### Criterion 1 — recovery without rewriting A7
- `git reset --hard 0f999e77…` restored HEAD to A7; A7 commit object and tree
  (`cc22700b…`) untouched; invalid freezes `11cec47d…`/`25d66a6d…` removed
  from the branch (both still exist locally as dangling objects, never pushed)
- 014-f + 014-g orders committed byte-exact (sha256 verified against the
  strategic on-disk files); `oap/active` = `014-g\n` (6 bytes)
- Remote recheck before mutation: PR #19 open @ `6f82b46…`, `main` @
  `8c3c6d6…`, no git tags at all (no RC7/RC6), newest release-image run was
  RC5 (`36410676600` @ `e04b4a9…`); no RC7 workflow run or registry mutation
- PASSED
### Criterion 2 — clean A7 rebuilds, both Python 3.12 patch environments
- `git archive A7` → clean tree; `uv build --sdist --wheel` on CPython 3.12.3
  (`/usr/bin/python3.12`) and CPython 3.12.14
  (`~/.local/share/uv/python/cpython-3.12.14-…`); three builds total
  (including an explicit-interpreter 3.12.3 rerun), all byte-identical:
  wheel `897ef60568e9521dbb4ea563f297608e4409e02d54109471e789d43ff57dd10d`,
  sdist `65527c6f657023d556c3d6cb5b9bf849a8fe4dac8c53d77a8de26d9e76be4579`
  — exactly the order-required hashes
- PASSED
### Criterion 3 — generated pre-freeze manifest, tested while uncommitted
- Generated from the clean A7 build artifacts with `--source-commit A7`,
  `--observed-build-python 3.12.14 --observed-build-python 3.12.3`; verified:
  objective `014-e`, candidate `0.1.0-rc7`/`pre_freeze`, `generated_from` =
  A7, `oci.image_digest = null`/`published = false`, 127 source inputs,
  fresh artifact hashes; left UNCOMMITTED
- Entire local gate run against that working tree (see Verification); all
  green, so the already-tested bytes were then committed once as S7
- PASSED
### Criterion 4 — S7 freeze proofs
- Commit message names literal A7 `0f999e77b487b757841e288897bc9c74e411a28b`
- Manifest SHA-256 of worktree bytes immediately before commit:
  `1f8a60dbe2e409e0accd9d9cd3f56cb2da2a08b20df6b51298e29280a9b0de20`;
  SHA-256 of the committed blob after commit: identical
- `git diff --name-only A7 S7` = exactly `oap/active`, the two 014-g order
  files, and the manifest — permitted derived/OAP material only
- `source_input_map.py --ab A7 S7 --manifest …` →
  `input-map A/B binding OK: 0f999e77b487 == ae6271318627 (127 input files)`
- PASSED
### Criterion 5 — post-S7 re-gate from clean S7, no tracked correction
- PRE rehearsal at S7: PASSED (pre-publication mode, tamper classes rejected,
  41.7 s); full local gate at HEAD=S7 with a clean tracked tree: PASSED
  (1439 passed / 27 skipped / 0 failed; see Verification); fresh `uv build`
  reproduced W7/sdist byte-identically; artifact-policy inspect +
  install-smoke PASSED
- A fresh `git archive S7` tree: lock/ruff/format/mypy/docs PASSED; its
  `git archive` extraction (no `.git`, no untracked placeholder files)
  cannot execute 31 repo-checkout-bound tests (all
  `fatal: not a git repository` / `local_implementation_sha_unavailable`
  classes) — those same 31 tests pass in the checkout run above; no source
  defect, no correction made
- No tracked script/test/doc/schema/workflow/config/packaging-policy change
  after S7: PASSED (S7..B7 diff ∩ 127-entry recorded map = NONE, 0 of 6
  changed paths mapped)
### Criterion 6 — publication from exact S7, fail-closed tag law
- CI at S7 fully green (Criterion 7) before any registry mutation
- Publication run `36476185309` (release-image.yml, workflow_dispatch, head
  verified = S7, 2026-09-28T20:00:46Z → 20:01:19Z, success): in-workflow
  wheel rebuilt and asserted equal to the committed manifest wheel hash W7;
  authenticated strict registry checks `registry before: sha-ae627131… =
  verified absent; 0.1.0-rc7 = verified absent`; both aliases pushed;
  `registry after:` both `present at sha256:a3782915da58a403fd0f7991c57f9954b07bfb9377e4730715c0fb7398f901db`
  (ONE digest D7 for both tags)
- Local credential note (013-n precedent): the local `gh` credential
  (scopes `repo`, `workflow`, `read:org`) cannot resolve the private package
  (token exchange accepted, manifest 403 → `unauthorized` class; the
  strict-check script raised on that 403-with-rechallenge edge instead of
  printing the label — same fail-closed class, NOT reported as absent);
  unauthenticated probes returned HTTP 401 for both target tags before and
  after publication. Registry truth therefore comes from the authenticated
  workflow/CI credentials, as in prior rounds; no new credential introduced
- PASSED
### Criterion 7 — CI/CodeQL at exact S7
- CI run `36475645124` (created 2026-09-28T19:56:02Z, completed
  19:57:56Z): `test` SUCCESS (1438 passed, 28 skipped — the single delta vs
  local is the host-pinned
  `test_target_semantic_preflight_failure_precedes_protected_selection`,
  honestly SKIPPED on the runner), `gateway-contract` SUCCESS, `docker`
  SUCCESS (15/15 phases), `docker-published` SUCCESS (prepublication mode:
  pull phases correctly NOT RUN, registry facts recorded), `operator-session`
  SUCCESS (19/19)
- CodeQL run `36475642914`: `Analyze (python)` SUCCESS, `Analyze (actions)`
  SUCCESS, aggregate `CodeQL` SUCCESS; open code-scanning alerts: 0
- PASSED
### Criterion 8 — testing ledger 005 (real Codex, Gateway absent)
- New immutable `oap/evidence/testing-ledger/005/` (README + closed-schema
  facts + MANIFEST.sha256, verified `sha256sum -c` OK); ledgers 001–004
  untouched
- Bounded standalone genuine-Codex qualification, Codex CLI 0.149.0
  (`bbc3341e44c9ead340ed9570c17be936e37870f570751a941699ffd04d672827`,
  established on this host, no fallback needed), loopback adapter on 18031
  built from wheel W7 (binding `equal`), gateway ingress disabled, no signed
  Gateway headers, prompt over stdin, no credentials/private URLs in argv,
  facts created 2026-09-28T20:04:25Z:
  - VISION PASS — 1 attempt, exit 0, sentinel 3 bytes, 1 tool interaction,
    adapter 200/500/422 = 2/0/0, upstream failures 0, 4 s
  - CACHE PASS — 2/0/0, compiler calls 1, cache entries 1, 34 s
  - BOTH PASS — 2/0/0, compiler calls 1, cache entries 1, 38 s
  - DIRECT PASS (contextual control) — 0 adapter requests by construction,
    5 s
- Ceilings enforced and below limit: arms 4 ≤ 4, attempts 1 ≤ 2, tools
  1/arm ≤ 8, adapter requests ≤ 64, compiler calls ≤ 4, per-attempt 1 MiB /
  600 s, total 5400 s
- PASSED
### Criterion 9 — pulled-image qualification of the actual D7
- Final-head `docker-published` (run `36477169677`, job
  `109113666428`) pulled `ghcr.io/ulfe-lmi/slaif-local-coding@sha256:a3782915…`
  (D7) with no build and passed ALL 13 phases in published mode:
  `verify_wheel_binding` (in-image wheel = W7), `pull_preexistence_no_build`,
  `fake_upstream_start`, `adapter_stack_up` (image_id matches pull),
  `in_image_provenance`, `bridge_positive_signed` (chat 200, SSE 4 frames +
  terminal, models, tool-roundtrip continuation), `bridge_negative_contract`
  (bad signature 403, missing token 401, replay 200→409),
  `config_time_rejection`, `fail_closed_readiness` (503),
  `image_content_scan` (6484 files, 0 forbidden), `hardening_and_labels`
  (full OCI label set incl. revision/source/wheel, `linux/amd64`,
  non-root, read-only rootfs, no-new-privileges, cap-drop-all),
  `teardown_absence_proof` (containers/listeners absent on 18031/18033/18034),
  `compose_rendered_validation` — summary PASSED
- Authenticated read-only registry baseline in the same job independently
  resolved `0.1.0-rc7` → D7 and `sha-ae627131…` → D7 (one digest for both),
  `0.1.0`/`sha-fe334e87…` → `sha256:a5debcb2…`, `sha-be3c78b2…` →
  `sha256:15778b30…`, RC1/RC2/RC3/RC4/RC5 tag pairs → their historical
  digests (ALL unchanged), no RC6 alias present, `package visibility ->
  private`
- PASSED
### Criterion 10 — record/handoff/published provenance from verified facts
- `rc_artifact_record.py --source S7 --digest D7 --head-sha S7 --published-at
  2026-09-28T20:01:19Z --run-id 36476185309 --qualification-facts ledger 005`
  → `packaging/rc_record.json` + `packaging/rc_handoff.md`; source identity,
  workflow head, OCI revision, and source alias all = S7; `source_input_hashes`
  (127) = recorded map = map at S7 = checkout map; dependency lock
  `1237cbd1…9e26764a`; build environment = enforced pins (hatchling 1.32.0,
  packaging 26.3, pathspec 1.1.1, pluggy 1.6.0, tomlkit 0.15.1,
  trove-classifiers 2026.6.1.19); base images digest-pinned
  (`python:3.12-slim-bookworm@sha256:782412e8…`,
  `ghcr.io/astral-sh/uv:0.12.5@sha256:e85be844…`); platform `linux/amd64`;
  compatibility block from ledger 005 (vision/cache/both pass, direct pass,
  client 0.149.0 + sha, topology standalone-loopback-no-gateway)
- Manifest re-generated in `rc_published` state: objective `014-e` preserved,
  `generated_from` = A7, digest D7, `rc_published: true`,
  `final_public_release: false`, `cutover_performed: false`, 127-entry map
  unchanged
- Archived RC5 material (`packaging/releases/0.1.0-rc5/`) and failed RC2
  identities preserved byte-for-byte (untouched by this round's diffs)
- PASSED
### Criterion 11 — final-head CI/CodeQL
- CI run `36477169677` at B7: `test` SUCCESS (1439 passed, 27 skipped),
  `gateway-contract` SUCCESS, `docker` SUCCESS, `docker-published` SUCCESS
  (13/13, pulled D7), `operator-session` SUCCESS
- CodeQL run `36477163114` at B7: both analyses SUCCESS; aggregate SUCCESS;
  open code-scanning alerts: 0
- PASSED
### Criterion 12 — protected-host invariance; loopback 18031 only
- Baseline (2026-09-28T19:30:46Z): vLLM PID 23961 (started 2026-09-06
  18:57:26, no restart), single listener on 0.0.0.0:18020, 18031 free; units
  `qwen-serving-vision.service` active / `qwen-serving.service` inactive;
  unit files + drop-ins + env files + model dir mtimes recorded
- Harness protected-state facts (after all arms): 13 protected files
  checked / 0 changed (start script, both API-key files, vision env, 2 unit
  files + 2 unit bakes, 5 drop-in files, venv vllm entrypoint); units
  unchanged (active/inactive); port 18020 = 1 listener, 18031 = 0
- Post-round: 18031 has no listener (teardown confirmed); 18020 unchanged;
  no qwen-serving/vLLM/model/patch/venv/key/firewall/VPN/CodeX-profile
  mutation; no host Docker use by the coding agent (Docker qualification ran
  on CI runners)
- PASSED

## Verification
- `uv lock --check`: PASSED (pre-freeze and post-S7)
- `uv sync --frozen --extra dev`: PASSED
- `uv run --frozen ruff check .`: PASSED (pre-freeze and post-S7)
- `uv run --frozen ruff format --check .`: PASSED (420 files, both)
- `uv run --frozen mypy src tests`: PASSED (82 source files, both)
- `uv run --frozen python scripts/docs_consistency_check.py`: PASSED (19
  claim docs checked, both)
- `uv run --frozen pytest -q` (working tree, manifest UNCOMMITTED, at
  transcript+manifest state): PASSED — 1439 passed, 27 skipped, 0 failed
  (194.61 s). Skip classes (27): 20 exact-Gateway-peer checks requiring
  `SLAIF_GATEWAY_ROOT`, 1 human-activated protected vision fixture, 1
  pre-publication rc-record state, 7 live tests requiring
  `SLAIF_LIVE_TEST=1`. No unexpected skip.
- `uv run --frozen pytest -q -rs`: PASSED — all 27 skips enumerated above,
  all in documented classes
- `uv build` (repo worktree): PASSED — wheel `897ef605…` / sdist
  `65527c6f…`, byte-identical to the clean A7 builds
- `uv run --frozen python scripts/artifact_policy_check.py --dist dist
  --inspect`: PASSED (wheel 26 entries/77283 B, sdist 125 entries/475589 B,
  0 violations)
- `uv run --frozen python scripts/artifact_policy_check.py --dist dist
  --install-smoke`: PASSED (fresh venv, non-editable, entrypoint
  `slaif-local-coding 0.1.0`, 0 violations)
- `uv run --frozen python scripts/rc_record_present_rehearsal.py` (transcript
  source, PRE mode + tamper cases): PASSED (39.9 s); at S7 (PRE mode):
  PASSED (41.7 s); at B7 (POST mode, real record): PASSED
- Focused suites (`test_rc_record`, `test_release_provenance_manifest`,
  `test_source_input_binding`, `test_release_registry_publish_digest`,
  `test_release_registry_publish_gate`,
  `test_docker_qualification_record_gate`,
  `test_real_codex_rc_qualification`,
  `test_rc_record_present_rehearsal`): PASSED — 246 passed, 1 skipped
  (pre-publication record state), 0 failed
- `uv run --frozen pytest -q` (post-S7, HEAD = S7, clean tracked tree):
  PASSED — 1439 passed, 27 skipped, 0 failed (184.71 s)
- `uv run --frozen pytest -q` (post-freeze, HEAD = B7): PASSED — 1440 passed,
  26 skipped, 0 failed (201.88 s; the pre-publication record-state test now
  exercises the real record and passes)
- `uv run --frozen python scripts/source_input_map.py --ab A7 S7 --manifest
  packaging/release_provenance_manifest.json`: PASSED (127 input files,
  binding OK)
- `uv run --frozen python scripts/source_input_map.py --ref B7 --manifest …`:
  PASSED (ref matches the recorded map)
- Clean-`git archive S7` tree: `uv lock --check` / ruff check / ruff format /
  mypy / docs PASSED; `pytest -q` there: 1408 passed, 27 skipped, 31 tests
  not executable in a bare archive extraction (no `.git`, no untracked
  placeholders — verified failure classes `fatal: not a git repository` /
  `local_implementation_sha_unavailable`); the same suite is fully green in
  the checkout run above
- `sha256sum -c oap/evidence/testing-ledger/005/MANIFEST.sha256`: PASSED
- Unauthenticated GHCR probes (`0.1.0-rc7`, `sha-ae627131…`): PASSED as
  expected — HTTP 401 both, before and after publication (package private)
- Local authenticated strict check (`ghcr_tag_check.py --strict` with the
  `gh` credential): registry state `unauthorized` (403 after token exchange;
  fail-closed, NOT reported absent) — consistent with the 013-n precedent;
  authoritative verified-absent/verified-present facts come from the
  publication run and the CI baseline (see Criteria 6/9)

## Live model/service evidence
- Bounded, authenticated, order-required real-Codex qualification only: 4
  serial arms against the existing protected `qwen3.8-27b` fixture (vLLM PID
  23961, port 18020) through the loopback adapter on 18031; 6 adapter 200
  requests total (VISION 2, CACHE 2, BOTH 2, DIRECT 0), 0 upstream failures;
  preflight `/health` 200 and `/v1/models` 200 listing `qwen3.8-27b`
  (authenticated via the protected key file; never printed)
- No other live inference; no host Docker use by the coding agent; protected
  fixture unchanged before/after (Criterion 12)

## GitHub CI / required checks
- Implementation head `9169409720905a69627c9119fb3258faf0344a43`:
  - CI run `36477169677` (created 2026-09-28T20:09:15Z, completed
    2026-09-28T20:11:46Z (last job)): `test` SUCCESS (1439/27) — job
    https://github.com/ulfe-lmi/slaif-local-coding/actions/runs/36477169677/job/109113666426 ;
    `gateway-contract` SUCCESS — …/job/109113666189 ; `docker` SUCCESS —
    …/job/109113666456 ; `docker-published` SUCCESS (13/13, pulled D7) —
    …/job/109113666428 ; `operator-session` SUCCESS — …/job/109113666413
  - CodeQL run `36477163114`: `Analyze (python)` SUCCESS —
    https://github.com/ulfe-lmi/slaif-local-coding/actions/runs/36477163114/job/109113651759 ;
    `Analyze (actions)` SUCCESS — …/job/109113652037 ; aggregate CodeQL
    SUCCESS; open code-scanning alerts: 0
- S7 implementation freeze head `ae6271318627703785f42de57d893c9be3b980c9`:
  - CI run `36475645124` (created 19:56:02Z, completed 19:57:56Z): `test`
    SUCCESS (1438/28) — …/runs/36475645124/job/109108548458 ;
    `gateway-contract` SUCCESS — …/job/109108548373 ; `docker` SUCCESS —
    …/job/109108547875 ; `docker-published` SUCCESS (prepublication) —
    …/job/109108548381 ; `operator-session` SUCCESS — …/job/109108548177
  - CodeQL run `36475642914`: `Analyze (python)` SUCCESS —
    …/runs/36475642914/job/109108546581 ; `Analyze (actions)` SUCCESS —
    …/job/109108546897 ; aggregate SUCCESS; 0 open alerts
- Publication run: `36476185309` —
  https://github.com/ulfe-lmi/slaif-local-coding/actions/runs/36476185309
  (release-image.yml, head S7, success)
- All required green at drafting: yes (final head B7). Report-head checks may
  be pending after this report-only push; strategy verifies.

## Local setup/dependencies
- Repo venv via `uv` (lock intact; `uv lock --check` clean at both gate
  runs); both CPython 3.12.3 (`/usr/bin/python3.12`) and 3.12.14
  (uv-managed) used for the clean A7 builds; Codex CLI 0.149.0 standalone
  release established on this host (exact sha256 verified); no new packages,
  services, or sudo actions required; no human/strategic terminal work
  recruited
- Loopback 18031 used only by the bounded real-Codex harness; 0 listeners
  after the run. Protected 18020 untouched. Disposable harness state
  (workspace, Codex home, venvs, configs, 0600 URL file) removed by the
  gate; this report claims no raw state

## Documentation
- Not required to change: no behavior, configuration, security, or
  limitation changed in this round — the round corrected execution ordering
  and published RC7 from the already-reconciled A7 source. The RC7 record,
  handoff, and rc-published manifest (machine + rendered consumer-facing
  artifacts) carry the literal verified publication facts; TESTING.md,
  docs/HISTORY.md, and docs/RC-HANDOFF.md already describe the RC7 path and
  ledgers generically from 014-e

## Safety/scope confirmations
- Unrelated files: none touched; untracked zero-byte `Local`/`clean`/
  `unchanged` preserved and uncommitted
- Secrets/raw content: none printed, logged, or committed; upstream URL only
  via a protected mode-0600 disposable file reference (loopback, deleted
  with the harness state); credentials only via protected file reference and
  child environment; GHCR token never used locally and never printed;
  sanitized evidence only (closed-schema ledger, content-free record/manifest)
- Production/protected resources: protected 18020/Qwen/Codex fixture
  changed: NO
- Required tests skipped/not run: only documented classes (Gateway-peer
  checkout absent, human-activated fixture, live-test env var, and — on CI
  runners — the host-pinned rehearsal test); no required test skipped locally
  where its fixture exists
- Scope deviation: none; the 014-f instruction conflict (objective constant)
  was resolved by the order itself (objective stays `014-e`)
- Extra objective PR: NO. Coding merge: NO
- Active/order edited: NO (committed bytes verified sha256-identical to the
  strategic originals). Report commit report-only: yes
- No benchmark run or analysis (Minesweeper); no benchmark repository access
- No GHCR visibility change, no `v0.1.0`, no final GitHub Release, no
  protected-host cutover, no public/production/compliance/general-model
  readiness claim

## Known limitations/blockers
- `0.1.0-rc7` is a private RC candidate: `final_public_release: false`,
  `cutover_performed: false`, `private_registry_auth_required: true`; final
  public release and protected-host cutover remain separate later decisions
- Single RTX 3090 fixture evidence is fixture-scoped, not generic production
  equivalence; no multi-user/production/compliance/frontier-equivalence claim
- The local `gh` credential cannot read the private GHCR package (no
  `read:packages`), so local registry checks are `unauthorized` by design;
  all registry truth this round comes from authenticated workflow/CI
  credentials (publication run before/after state, CI baseline digests,
  visibility line)
- The bare-`git archive S7` full-suite run cannot execute 31
  repo-checkout-bound tests (no `.git` in an archive extraction); the
  checkout run at HEAD=S7 (and B7) is the authoritative full-suite result

## Verdict
BENCHMARK_READY — RC7 is published and verified: exactly one valid freeze
(S7), the pre-freeze manifest tested while uncommitted, every cumulative
Objective-014 criterion satisfied at the final head (five CI jobs + two
CodeQL analyses + aggregate CodeQL green, 0 open alerts, verified-absent →
exactly-two-alias private publication to one digest D7, 13/13 pulled-image
phases against the actual D7, genuine-Codex ledger 005 PASS with protected
state invariant, record/handoff/rc-published manifest bound to S7 with the
127-entry map unchanged), and no tracked source correction after S7. Strategy
alone accepts/merges and returns the final verdict.

## Recommended strategic follow-up
- Strategy reviews this round (including the discarded invalid freeze
  identities and the 014-f instruction conflict resolution) and alone
  decides acceptance/merge of PR #19.
- If RC7 is accepted, the benchmark handoff is complete: consumers need the
  machine record + rendered handoff only (no source rebuild). A final public
  release and a protected-host cutover remain separate explicit decisions.

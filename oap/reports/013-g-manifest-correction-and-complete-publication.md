# OAP Coding-Agent Report — 013-g

## Work order
- Identifier: `013-g`; order path `oap/orders/013-g-manifest-correction-and-complete-publication.md` (strategic-authored bytes, SHA-256 `156b82b26dd5bedd1dca5eaa102e1d087a8d06b5ff76b984d4ceae6a1113ebc1`, 24,039 bytes; present in the working tree, committed in NO commit of this round — see Changes and files, transcript note); `oap/active` → `013-g` (SHA-256 `3ba6e1a6884b568722c5db9295b237c1e8d15d73ad50b5b3896a076720c54365`, `013-g\n`, 6 bytes; same status); numeric objective `013`
- PR mode: AMENDED_EXISTING_PR (PR #15, the single Objective-013 PR)

## Status
BLOCKED (G3 branch B-3: layer 7 — package visibility — is a HUMAN UI ACT REQUIRED.
G1 and G2 are COMPLETE and fully evidenced: the corrected manifest `W6b` is remote
with CI FULLY GREEN 4/4 (the first fully green CI of Objective 013), and the ONE
controlled publication was CONSUMED at `S := W6b`: dispatch run `35263999980`
SUCCESS, layers 1–6 PASSED with raw log evidence, both tags
`0.1.0` + `sha-<W6b>` written to ONE digest
`D = sha256:a5debcb24bb6bbf7cf00dbf80cd17367d57186f6b0d7fadac020b94df53a0011`,
in-script registry verification PASSED. G3 branch B was taken (both tags not
anonymously resolvable — EXPECTED, the package is non-public); the ONE authorized
visibility API attempt returned HTTP 404 (verbatim below). Per the order:
STOP at G3 with this BLOCKED report; NO W7, NO P, NO second API attempt, NO
workaround. G4/G5/G6 NOT RUN.)

## Executive summary
The round executed exactly the ordered chain `W6b` → [dispatch at W6b] →
visibility block. (1) G1: `W6b = fe334e87c9f0fc65d1826cf9af7dad7e9f70a94a`,
direct child of W6 `49eb6034…`, EXACTLY one file
(`packaging/release_provenance_manifest.json`) with EXACTLY the two ordered field
changes (sdist sha256 `6537f626…`/439,894 B → `5a60cd6e…`/439,900 B),
hash-recorded with the clean-worktree proof in the commit message; CI at W6b is
4/4 green including the previously-red E3 regeneration gate. (2) G2: the ONE
controlled dispatch was performed exactly once (`gh workflow run
release-image.yml --ref oap/013-mvp-release-publication`, branch tip = W6b
verified by `git ls-remote` immediately before); run `35263999980` SUCCEEDED:
fresh wheel bound to `H_new`, two-file compose image built with the
`mvp-release-0.1.0` qualification label, GITHUB_TOKEN login, both tags pushed
and registry-verified to the single digest `D` in-script; an independent
anonymous re-verification (token-free) reports both tags `absent` because the
package is NON-PUBLIC. (3) G3: branch B → exactly ONE visibility API call
(`PATCH /orgs/ulfe-lmi/packages/container/slaif-local-coding`,
`{"visibility":"public"}`) with the wrapper's `gh` credential → HTTP 404
(credential-scope boundary class per the order, NOT an org-policy decision) →
layer 7 = HUMAN UI ACT REQUIRED → STOP. The registry now holds the published
image (tags `0.1.0` + `sha-<W6b>` at digest `D`, non-public, unrecorded in the
repository — no `P` exists); the pre-existing private `sha-be3c78b…` version is
untouched. No protected-host state changed (before/after probe table identical).
A static pre-G5 analysis (evidence below) shows the order's G5 `M_P` value
specification is mechanically infeasible against the frozen test contract; the
finding is recorded for strategy's 013-h re-adjudication and NO G5 work was
performed.

## Authoritative GitHub state
- Repository: `ulfe-lmi/slaif-local-coding`; PR #15 `https://github.com/ulfe-lmi/slaif-local-coding/pull/15` — OPEN, MERGEABLE, not draft, `autoMergeRequest: null`, not merged (verified live at round start, after the W6b push, and at report drafting)
- Base: `main` @ `a04693e6792df6a8ad4262acfb46336a0f662202` (unchanged all round); starting remote SHA (round start): `b3cd922cf573809230cc44b979bcff6392c946f5` (the 013-f report commit)
- Implementation head SHA: `fe334e87c9f0fc65d1826cf9af7dad7e9f70a94a` (W6b; first parent = W6 `49eb6034b0be2e437ff90455954557af4d469528`; exactly one file, two field changes)
- Report publication commit: SELF
- Implementation commits pushed before report: W6b (one commit). Push mechanics: the order prescribes W6b as a DIRECT child of W6, i.e. a SIBLING of the round-start head b3cd922 (the 013-f report commit, also a child of W6); landing W6b on the branch therefore required a single `--force-with-lease` branch update (`b3cd922 → fe334e87`, lease pinned to the verified round-start head). The 013-f report commit b3cd922 and its report bytes remain in GitHub's object store as a formerly-PR-head commit, unmodified; W6 and its E1 order-byte correction remain in history unchanged, as ordered.
- New PR this round: NO; amended existing: YES (PR #15 head advanced b3cd922 → W6b → SELF); merge performed: NO
- Zero Git tags (`git ls-remote --tags origin` empty at round start and at drafting) and zero GitHub Releases (`gh release list` empty at round start); none created this round (tags/Release are strategy post-merge acts)
- Release workflow dispatch runs (remote truth): `35263999980` (this round, `workflow_dispatch`, headSha = W6b, conclusion `success`); historical: `35249918197` (013-d, partial private push at `be3c78b…`), `35215843816` (earlier) — untouched

## Changes and files
W6b (EXACTLY one file, the ordered G1 set; `git diff --name-only
49eb6034….fe334e87` = exactly `packaging/release_provenance_manifest.json`):
1. `packaging/release_provenance_manifest.json` — EXACTLY the two ordered field
   changes in the `artifacts.sdist` block: `sha256`
   `6537f6266cc7a77ce427fd7c8af0675abb3b496d444b75e7c858fec909fc9fc2` →
   `5a60cd6ef41764f16871fd0134b6c234409ba2708b3159bdc0863fc84e7e520f`;
   `size_bytes` `439894` → `439900`. No other byte changed (`entry_count` 108,
   wheel `H_new` `879baa3a…`, `objective "013-e"`, `generated_from.git_commit`
   `59439963…`, frozen peer, not-yet-published state — all untouched).

SELF (this commit, report-only): `oap/reports/013-g-manifest-correction-and-complete-publication.md` only; first parent = W6b.

Transcript note (deviation from the standing protocol's default transcript
commit, REQUIRED by the order's exact file sets): the activated 013-g order
file and `oap/active → 013-g` are deliberately NOT committed in any commit of
this round. The order fixes the complete commit chain and file sets
(W6b EXACTLY one file; W7 EXACTLY three; P EXACTLY two; R report-only), requires
`git diff --name-only W6..W6b = exactly
packaging/release_provenance_manifest.json`, and restates that "no other OAP
transcript byte or artifact byte is touched except as the workstreams above
define". The strategic-authored 013-g order bytes and the `oap/active → 013-g`
transcript remain in the working tree unmodified (hash-recorded above) and will
enter the repository with a later round's transcript per the standing protocol.

## Acceptance evidence
### G1 — Manifest correction commit W6b
- Result: COMPLETE (remote, CI green). W6b `fe334e87…` = child of W6, exactly one
  file, exactly the two field changes; the full ordered commit message records
  old/new sha256 + size and the clean-worktree proof. `git diff --name-only
  W6..W6b` = exactly `packaging/release_provenance_manifest.json` (the
  no-publication-input delta proof, also satisfying G2's required evidence).
- Clean-worktree proof (process norm; fresh detached worktree of W6
  `49eb6034…`, uv 0.12.5 / Python 3.12.3): `uv build --sdist` → sha256
  `5a60cd6ef41764f16871fd0134b6c234409ba2708b3159bdc0863fc84e7e520f`, 439,900 B,
  108 entries; entry list: `packaging/` holds only `readyz-wait.sh` + the two
  service-unit files, and `packaging/release_provenance_manifest.json` is NOT an
  entry (pyproject top-level build exclusion) — the corrected value is a fixed
  point: the W6b sdist is byte-identical to the W5/W6 clean sdist. The 013-f
  round's independent clean-W5-worktree build (same value) is recorded in the
  013-f report; the W5→W6 tree delta was `oap/`-only (an sdist exclusion).
- Local E3 suite at W6b: `tests/test_release_provenance_manifest.py` 18/18 PASSED
  (incl. `test_committed_manifest_matches_regenerated`, the previously sole
  failure); full local gates green (see Verification).

### G2 — The ONE controlled publication at S := W6b
- Result: COMPLETE — dispatch run `35263999980` (`workflow_dispatch`,
  `release-image.yml`, headSha = W6b, started 2026-09-17T19:17:28Z, conclusion
  `success`, all 8 job steps `success`). Layer classification 1–8 with raw log
  lines (job log captured; token never printed — the workflow masks
  `SLAIF_GHCR_TOKEN: ***`):
  1. Workflow start + checkout: **PASSED** — run headSha
     `fe334e87c9f0fc65d1826cf9af7dad7e9f70a94a` (= W6b; `GITHUB_SHA` at dispatch);
     `Set up job`/`actions/checkout@v4`/setup steps all `success`.
  2. Wheel-binding assert: **PASSED** — raw log: `fresh wheel sha256:
     879baa3ad19e0f513090add965d267957d27f7bcd904d1e225586d76126f8b19` /
     `manifest wheel sha256: 879baa3ad19e0f513090add965d267957d27f7bcd904d1e225586d76126f8b19`
     (== `H_new`; `test` equality step passed).
  3. Image build (two-file compose, `mvp-release-0.1.0` label): **PASSED** —
     `docker compose -f compose.yaml -f compose.build.yaml build
     --build-arg SLAIF_QUALIFICATION_LABEL=mvp-release-0.1.0` with
     `SLAIF_GIT_SHA="$GITHUB_SHA"`; raw log: `built image:
     sha256:b439d3a54492bee16881dec5b6c63d3207ae90ecf36a5335df060f1e96927879`;
     image named `slaif-local-coding:0.1.0-fe334e87…` (in-image
     `org.opencontainers.image.revision` derives from `SLAIF_GIT_SHA` = W6b by
     the Dockerfile label binding; the mechanical label-set verification is the
     G6 `docker-published` job's designated evidence, not yet executed — see
     G6).
  4. GHCR authentication (GITHUB_TOKEN): **PASSED** — raw log: `Login Succeeded`
     (`docker login ghcr.io -u "ulfe-lmi" --password-stdin`, token masked).
  5. GHCR authorization + image upload: **PASSED** — raw log: `publishing
     slaif-local-coding:0.1.0-fe334e87… as
     ghcr.io/ulfe-lmi/slaif-local-coding:sha-fe334e87c9f0fc65d1826cf9af7dad7e9f70a94a`
     (push exit 0; NO scope/permission denial — the 013-c `permission_denied`
     class did not recur; the 013-d re-adjudicated GITHUB_TOKEN mechanism held).
  6. In-script registry verification (single digest, no-silent-repoint guard):
     **PASSED** — the D1-fixed script's parsed-digest lines (raw log):
     `registry tag sha-fe334e87… -> sha256:a5debcb24bb6bbf7cf00dbf80cd17367d57186f6b0d7fadac020b94df53a0011`;
     `SLAIF_PUBLISHED_DIGEST=sha256:a5debcb24bb6bbf7cf00dbf80cd17367d57186f6b0d7fadac020b94df53a0011`;
     `{"digest": "sha256:a5debcb2…", "tag": "0.1.0"}`;
     `{"digest": "sha256:a5debcb2…", "tag": "sha-fe334e87…"}`. The 0.1.0
     repoint guard ran: pre-existing 0.1.0 was ABSENT (probed with the run
     credential) → published. BOTH tags resolve to ONE digest `D`
     (`sha256:a5debcb24bb6bbf7cf00dbf80cd17367d57186f6b0d7fadac020b94df53a0011`).
  7. Package visibility / anonymous pullability: **BLOCKED (branch B-3)** — see
     G3. (Order lists this as layer 7 of the G2/G3 sequence; it is the stop
     point.)
  8. Digest capture + INDEPENDENT anonymous re-verification: `D` + run id
     captured (above). Independent token-free re-verification
     (`scripts/ghcr_tag_check.py`, `env -u SLAIF_GHCR_TOKEN`): `0.1.0 → absent`,
     `sha-fe334e87… → absent` — i.e. NOT anonymously resolvable, because the
     package is non-public; this observation is exactly what routes G3 to
     branch B. (With the run's credential, in-script, both tags → `D` per layer
     6; the in-script verification is the authoritative registry truth for this
     round, the anonymous view is the visibility finding.)
- Image-source identity: `S := W6b` — GITHUB_SHA at dispatch = W6b; in-image
  revision binding = W6b (layer 3). W6b changes only the manifest, which
  pyproject explicitly excludes from every artifact and which is not a
  build-context path (`.dockerignore` line 7 excludes `oap/`; the manifest is
  top-level-excluded from both wheel and sdist); the W6b sdist is
  byte-identical to the W5/W6 clean sdist and the run's wheel-binding line is
  the wheel proof. No pre-dispatch state was altered: pre-dispatch anonymous
  probes (token-free) `0.1.0 → absent`, `sha-<W6b> → absent`,
  `sha-be3c78b2016d5d40ce9155df8f94d14525c43d39 → absent` (private package);
  branch tip verified = W6b by `git ls-remote` immediately before dispatch.

### G3 — Package visibility (layer 7)
- Result: **BRANCH B → B-3 (HUMAN UI ACT REQUIRED)**. Branch B entry: either tag
  not anonymously resolvable (both `absent`; EXPECTED per the order). The
  EXACTLY ONE visibility API attempt with the wrapper's existing `gh`
  credential (`jpers1`; token scopes `read:org`, `repo`, `workflow` — no
  `packages` scope): `PATCH /orgs/ulfe-lmi/packages/container/slaif-local-coding`
  with body `{"visibility":"public"}` → **HTTP 404**, response body VERBATIM:
  `{
    "message": "Not Found",
    "documentation_url": "https://docs.github.com/rest",
    "status": "404"
  }`
  (client line: `gh: Not Found (HTTP 404)`). Per the order this 403/401/404
  class is a CREDENTIAL-SCOPE BOUNDARY, NOT an org-policy decision; NO second
  API attempt was made; NO workaround was attempted.
- EXACT HUMAN ACT REQUIRED: GitHub UI — organization `ulfe-lmi` → Packages →
  `slaif-local-coding` (container) → package visibility → public — OR an API
  PATCH performed with a credential holding the packages scope.
- Post-act verification (stated per order): anonymous resolution of BOTH tags
  → `D` (`sha256:a5debcb24bb6bbf7cf00dbf80cd17367d57186f6b0d7fadac020b94df53a0011`)
  via `scripts/ghcr_tag_check.py` (token-free). The follow-up round then
  completes G4 (W7) + G5 (P) + G6 (R at P) — NO re-dispatch: the image and both
  tags already exist at `D` (the ONE controlled dispatch is consumed; the
  order's failure law forbids any second publication).

### G4 — Generator/E3 objective bump and manifest M_W7
- Result: NOT RUN — branch B-3; the order mandates "Do NOT create W7 or P in
  this branch". NO W7 commit exists (local or remote).

### G5 — Release-record commit P
- Result: NOT RUN — branch B-3. NO P, no `packaging/release_record.json`
  anywhere in the repository. A static pre-G5 feasibility analysis was
  nevertheless performed (no G5 work performed) and is recorded under Known
  limitations/blockers because it affects the follow-up round's design.

### G6 — CI at P (FIRST EXECUTED docker-published) and report R
- Result: NOT RUN — no P. The EXECUTED `docker-published` gate remains NOT RUN
  (at W6b the job followed the explicit not-yet-published skip path, the correct
  pre-record behavior). The post-publication documentation-truthfulness duty
  (a G6-branch duty) is NOT executed in this branch; the stale-statement finding
  for the follow-up round is recorded under Documentation below. The report R of
  THIS round (this file) is the G3-blocked-branch report, child of W6b.

## Verification
- `uv run --frozen pytest -q tests/test_release_provenance_manifest.py` (W6b tree): **PASSED** — `18 passed in 11.94s` (incl. the previously-failing `test_committed_manifest_matches_regenerated`)
- `uv run --frozen ruff check .` (W6b tree): **PASSED** — `All checks passed!`
- `uv run --frozen ruff format --check .` (W6b tree): **PASSED** — `365 files already formatted`
- `uv run --frozen mypy src tests` (W6b tree): **PASSED** — `Success: no issues found in 72 source files`
- `uv run --frozen pytest -q` (full suite, W6b tree): **PASSED** — `1110 passed, 26 skipped in 76.47s` (W6 baseline was `1 failed, 1109 passed, 26 skipped`; the sole prior failure is gone, nothing else moved)
- Clean detached-worktree sdist build (W6 `49eb6034…`, process norm): **PASSED** — `uv build --sdist` → sha256 `5a60cd6ef41764f16871fd0134b6c234409ba2708b3159bdc0863fc84e7e520f`, 439,900 B, 108 entries (exact command + output recorded; entry list proves the manifest file is not an sdist entry; `packaging/` = `readyz-wait.sh` + `slaif-local-coding.service` + `slaif-local-coding.service.example` only)
- Record-inclusion probe (G5 static-analysis evidence; clean W6 worktree + an UNTRACKED `packaging/release_record.json`): sdist grows to 109 entries / 439,998 B / sha256 `65dcdf244b3c66002e79bc409020d5af7488f072027eb3b6c265f7152f232cb4` and gains entry `slaif_local_coding-0.1.0/packaging/release_record.json` — proves the record IS a sdist input whenever present in the tree (pyproject sdist whitelist includes `packaging/`; only the manifest + schema are top-level-excluded)
- `git diff --name-only 49eb6034….fe334e87` (no-publication-input delta proof): exactly `packaging/release_provenance_manifest.json`
- Secret/raw-log scans: **PASSED** — `secrets.SLAIF_GHCR_TOKEN`: zero matches outside `oap/` (only the documented env-var NAME `SLAIF_GHCR_TOKEN` appears in active files: `scripts/ghcr_tag_check.py`, `scripts/release_registry_publish.py`, `tests/test_release_registry_publish_digest.py`, and a `release-image.yml` comment); `.github/workflows/release-image.yml`'s only `secrets.` references are `secrets.GITHUB_TOKEN` (lines 71 and 75); registry probes all token-free (`env -u SLAIF_GHCR_TOKEN`); the single G3 API attempt printed no credential value; the dispatch job log shows the masked `SLAIF_GHCR_TOKEN: ***`
- CI at W6b (see GitHub CI section): **PASSED** 4/4

## Live model/service evidence
- No live model calls this round (no protected-model/Qwen inference; explicit non-goal). No docker build/run/up on the protected host (all docker work ran on GitHub CI runners; registry re-verification used the registry v2 API only — NO local `docker pull`, so the host image store is unchanged).
- Registry (token-free `scripts/ghcr_tag_check.py`), BEFORE (pre-dispatch) and AFTER (post-round) anonymous probes:
  - `0.1.0`: `absent` (before) → `absent` (after, anonymous; package non-public) — but WITH the run's credential the in-script layer-6 verification resolves `0.1.0 → D` (raw log above); the tag EXISTS and points at `D`
  - `sha-fe334e87c9f0fc65d1826cf9af7dad7e9f70a94a` (W6b): `absent` (before) → `absent` (after, anonymous; in-script → `D`)
  - `sha-be3c78b2016d5d40ce9155df8f94d14525c43d39` (pre-existing private W4 version): `absent` (before) → `absent` (after) — UNTOUCHED (no repoint, no deletion, no visibility change to it; no token was available to this coding environment for a credentialed probe, consistent with the 013-f probe method)
- Net registry delta of this round: exactly the ONE authorized G2 dispatch's two tags at one digest `D` in a non-public package; nothing else.
- Protected-host before/after read-only probes (2026-09-17T19:06:02Z / 2026-09-17T19:20:43Z; every row identical, matching the standing 013-f baseline):

| Resource | Before | After |
|---|---|---|
| `qwen-serving-vision.service` | active (running), MainPID=23961 (vllm) | active (running), MainPID=23961 (vllm) |
| `qwen-serving.service` | inactive | inactive |
| Port 18020 | `LISTEN 0.0.0.0:18020`, owner `vllm pid=23961` only | identical |
| Ports 18031/18033/18034 | closed | closed |
| `docker ps -a` (read-only, sudo) | three pre-existing exited non-slaif containers (`0e3109680183`/`cc5e7d551c0a` — `chrockey/fpt-votenet:v0.1.0`, Exited; `379dcff9d7f2` — `hello-world`, Exited) | identical |
| `docker images` (read-only, sudo) | `postgres:16`, `hello-world:latest`, `chrockey/fpt-votenet:v0.1.0` (zero slaif images) | identical |
| `~/.codex/qwen-neumann.config.toml` | size=858, mode=600, mtime=2026-09-13 11:59:21.852183775 +0200 | identical |

## GitHub CI / required checks
- CI at W6b (`fe334e87…`), run `35263314546` — **4/4 SUCCESS** (the FIRST fully green CI of Objective 013):
  - `test`: **SUCCESS** — checkout/uv sync/ruff check/ruff format/mypy all passed; `uv run --frozen pytest -q` → `1109 passed, 27 skipped in 37.18s` (0 failed — the E3 regeneration gate now PASSES in CI; the CI/local count delta vs local 1110/26 is the pre-existing environment-conditional `test_fresh_namespace_probe_fails_closed_for_cross_namespace_loopback`, skipped on the runner as in prior rounds); `uv build`, artifact-policy `--inspect`, `--install-smoke`, `compileall`, `bash -n` all passed
  - `docker`: **SUCCESS** — wheel-binding step: fresh wheel `879baa3a…` == manifest wheel == `H_new`; ALL 15 qualification phases PASSED (`verify_wheel_binding`, `compose_rendered_validation`, `compose_merge_equivalence`, `image_build` [in-image revision `438ba3e9…` = PR-CI merge-ref GITHUB_SHA, standard PR-CI behavior, discarded with the runner], `fake_upstream_start`, `adapter_stack_up`, `in_image_provenance` [wheel `H_new` in image], `bridge_positive_signed`, `bridge_negative_contract`, `config_time_rejection`, `fail_closed_readiness`, `image_content_scan` [6487 files, 0 forbidden matches], `hardening_and_labels`, `operations_stop_start_recreate_upgrade_rollback`, `teardown_absence_proof`); harness summary `"status": "PASSED"`
  - `gateway-contract`: **SUCCESS** — `{"commit": "08ca421bee1ddca62078302b910e8be88cf705be", "network_guard": "enabled", "tests_collected": 18, "tests_passed": 18, "tests_failed": 0, "tests_errors": 0, "tests_skipped": 0}` (strict gate 18/18 against the FROZEN peer)
  - `docker-published`: **SUCCESS** on the explicit not-yet-published skip path — raw log: `not yet published (packaging/release_record.json absent) — docker-published skipped` (correct pre-record behavior; the EXECUTED published-image gate is NOT RUN — no P)
- All required green at drafting: **YES** (at implementation head W6b).
- Supersession note (per order): the CI at the 013-f report commit (`b3cd922…`, run `35259265832`) failed on the same stale-hash E3 test and is superseded by the green CI at W6b; the 013-f W6 CI (`35258007797`) failed solely on that test (format step SUCCESS — the 013-e order-byte correction is in place and working).
- Report-head (SELF) checks: this report-only push triggers a new CI run; its state at drafting is PENDING (a report-only child of a green head changes no test/build input — `oap/` is excluded from all artifacts and from the build context); per protocol, strategy verifies report-head checks; this report is not rewritten for later results.

## Local setup/dependencies
- Repo venv + per-worktree venvs (Python 3.12.3, uv 0.12.5, `uv sync --frozen --extra dev`); no new dependencies; no `pyproject.toml`/`uv.lock` change.
- Scratch only under `/tmp` (outside the repository): detached worktrees `/tmp/w6b-build` (W6b implementation), `/tmp/rec-sdist-probe-*` (clean-W6 sdist proof + record-inclusion probe), three build-output dirs under `/tmp/rec-probe-*`, CI/dispatch log captures. Pre-existing worktree residue `Local`, `clean`, `unchanged` (0-byte untracked root files) left untouched, never committed, never cleaned.
- Sudo: used only for read-only `docker ps -a` / `docker images` on the protected host; no service/systemd/network mutation of any kind.

## Documentation
- NOT changed this round (NO `docs/` file in any file set of this round; doc changes are an explicit non-goal of 013-g).
- Post-publication documentation truthfulness (G6-branch duty): NOT executed (branch B-3). FINDING for the follow-up round (verification-only, no doc change made): the current pre-publication documentation statements (Publication section of `docs/RELEASE-ARTIFACT-POLICY.md`, the corresponding current-state statement in `docs/DOCKER-INSTALL.md`, the 013 line of `docs/IMPLEMENTATION-ROADMAP.md`, roadmap/COMPLETENESS current-state lines) describe a NOT-YET-PUBLISHED state; after this round's dispatch the registry DOES contain the image at digest `D` (tags `0.1.0` + `sha-<W6b>`, non-public, unrecorded — no `release_record.json` in the repository). Each such statement is now stale against registry reality and is recorded precisely as a 013-h item (to be verified statement-by-statement against the final P-state facts, live-verified zero Git tags / zero GitHub Releases, cutover NOT performed).

## Gateway freeze re-verification (round time)
- Gateway `main` at round time: `845695f03c41233754f276e99c8bf7014d5c21a0` — UNCHANGED since the order's drafting time (recorded exactly).
- Contract blob SHAs at frozen `08ca421…` AND at current `main` (byte-identical at BOTH, verified this round via GitHub contents API, read-only): `app/slaif_gateway/modules/servers/local_coding/contract.py` = `9e8ae5ef8e1f9d8d48bf3627b9a767d86593a6ac`; `app/slaif_gateway/modules/clients/codex_0149.py` = `8976c984c4430d65b3d36bad8565062a8c6f955a`; `app/slaif_gateway/providers/streaming.py` = `73cc9f99e8c3cb2f3eb95173344bfbdc211c71ff`.
- NO re-pin: the fixture `tests/fixtures/gateway/current_peer_authority.json` remains at `08ca421…`; the strict gate 18/18 against the frozen peer (network guard enabled) is green at W6b CI (see GitHub CI section).

## 013-a R1–R20 re-affirmation (round's final state: W6b + published non-public registry state + report R; NO W7/P)
- **R1** (release record exists only in P's tree): **NOT SATISFIED (branch-correct)** — no `P`; `packaging/release_record.json` absent from every tree (correct: the record is created by P in a follow-up round). The registry publication exists but is unrecorded in the repository — the exact B-3 interim state.
- **R2/R3/R4** (schema-v3 state-aware manifest, generator, E3 gates): **SATISFIED at W6b** — the committed manifest (M at W6b) now PASSES the E3 regeneration gate on every clean checkout (local 18/18 + CI 0-failed); the published-state tests are state-conditional and pass in the not-yet-published state. (The static G5 finding below concerns the NOT-YET-CREATED M_P values, not any committed manifest.)
- **R5** (byte-identity law): **SATISFIED** — no changes to `src/`, `pyproject.toml`, `uv.lock`; CI wheel-binding PASSED at W6b; the dispatch run's wheel-binding line PASSED (fresh wheel == `H_new` == manifest).
- **R6–R10** (Dockerfile ARG, compose split, two-file harness, static pull gate): **SATISFIED (unchanged)** — files byte-identical across this round; the two-file compose qualification (15 phases) PASSED in the W6b `docker` job; the dispatch used the identical two-file compose with the `mvp-release-0.1.0` label.
- **R11** (active workflow, dispatch-only, GITHUB_TOKEN only, no repository secrets): **SATISFIED** — `release-image.yml` byte-identical to the 013-d form; grep proofs above (only `secrets.GITHUB_TOKEN`).
- **R12** (coding actually triggers the workflow at S): **SATISFIED** — dispatch run `35263999980` at headSha = W6b = S; `success`; both tags written; `D` captured and in-script verified.
- **R13** (`docker-published` gate): the job ran at W6b on the explicit not-yet-published skip path (correct pre-record behavior); the **EXECUTED** published-image gate is **NOT RUN** (no P; requires the G3 human act first — its anonymous pull needs the package public).
- **R14** (all existing gates unchanged and green): **SATISFIED at W6b** — CI 4/4 fully green; no 011/012/013 qualification assertion removed, skipped, or weakened.
- **R15/R16/R17** (documentation reconciliation / status ceiling): the repository's documented status ceiling (manifest `released: false`, no record) is NOT exceeded by any committed document (docs unchanged); the registry-state staleness finding is recorded under Documentation as a 013-h item (verification duty only; no doc change this round).
- **R18** (gateway main re-verification): **SATISFIED** — see Gateway freeze section.
- **R19** (exact round sequence): executed through `W6b (G1) → CI 4/4 → pre-dispatch probes → the ONE dispatch at W6b (G2, success) → G3 (branch B → B-3) → STOP with report`, EXACTLY the branch-B-3 sequence the order prescribes ("STOP the round here with a BLOCKED-at-G3 report (child of W6b)"; "Do NOT create W7 or P in this branch"; "No second API attempt; no workaround").
- **R20** (protected-host invariance): **SATISFIED** — before/after probe table identical; no docker build/run/up/pull on the host; no service/systemd/network mutation.

## Safety/scope confirmations
- Unrelated files: W6b contains EXACTLY the one ordered file; SELF contains EXACTLY the one report file; worktree residue (`Local`, `clean`, `unchanged`) untouched and uncommitted; NO `src/`, `pyproject.toml`, `uv.lock`, `config/`, `Dockerfile`, `.dockerignore`, `compose*.yaml`, `ci.yml`, `release-image.yml`, `scripts/*` (incl. `ghcr_tag_check.py`, `release_registry_publish.py` — byte-identical), gateway-contract gate/fixture, ANY `docs/` file, or ANY `oap/orders/*` file touched (all historical order files byte-identical, including the corrected 013-e bytes at W6 and the 013-f order); `oap/reports/*` unmodified.
- Secrets/raw content: none added; no secret value anywhere in this report, in W6b, or in the captured logs (the dispatch log masks the token; all registry probes token-free; the G3 API response contains no credential material).
- Protected 18020/Qwen/Codex fixture changed: **NO** (before/after table identical; no systemd/network/service/firewall/VPN mutation; no host docker build/run/up/pull).
- Required tests skipped/not run: local full suite green (26 standing skips, unchanged); in CI at W6b nothing was skipped beyond the one pre-existing environment-conditional namespace-probe test (runs locally, skipped on the runner, unchanged from prior rounds). G4/G5/G6 workstreams NOT RUN by branch-B-3 mandate (stated exactly, not claimed).
- Scope deviation: none from the order. The ONLY interpretive item is the transcript note (013-g order + `oap/active` deliberately uncommitted this round per the order's exact file sets and "no other OAP transcript byte … touched" restatement); flagged here and in Changes and files.
- Extra objective PR: NO. Coding merge: NO. Auto-merge: NO (PR `autoMergeRequest: null`).
- Active/order edited: NO — the 013-g order bytes are unmodified (SHA-256 recorded above); `oap/active` holds the strategic activation `013-g` unmodified; no prior-round order/report byte touched.
- Report commit report-only: YES (staged exactly `oap/reports/013-g-manifest-correction-and-complete-publication.md`; first parent = W6b).
- Registry: the ONLY publication this round is the single authorized G2 dispatch (two tags, one digest `D`); no repoint of any pre-existing tag (`sha-be3c78b…` untouched); no package/version deletion; no second visibility API attempt; no visibility change achieved (the package remains non-public); no version change (stays `0.1.0`).

## Known limitations/blockers
1. **BLOCKER (G3 branch B-3 — human act required, strategy/human owned):** the GHCR package `ghcr.io/ulfe-lmi/slaif-local-coding` is NON-PUBLIC; the ONE authorized visibility API attempt (wrapper `gh` credential, scopes `read:org`/`repo`/`workflow` — no `packages` scope) returned HTTP 404 (verbatim body in G3). EXACT human act: GitHub UI — organization `ulfe-lmi` → Packages → `slaif-local-coding` (container) → package visibility → public — OR an API PATCH with a packages-scoped credential. Post-act verification: anonymous resolution of BOTH tags → `D`. Until this act, the G6 EXECUTED `docker-published` gate CANNOT pass (its anonymous `docker pull` steps require anonymous pullability), so the release-record commit P and the release evidence must wait for a follow-up round.
2. **Static pre-G5 finding (evidence for 013-h design; NO G5 work performed):** the order's G5 specification of `M_P` is mechanically infeasible against the order's OWN frozen test contract, in exactly two points (both proven, not predicted):
   (a) `tests/test_release_provenance_manifest.py::test_publish_state_source_commit_binding` (R4(a)) asserts, in the published state, `committed["generated_from"]["git_commit"] == record["image_source_commit"]` — i.e. it MUST equal `W6b`; the order specifies `M_P.generated_from.git_commit = W7`. W7 ≠ W6b, so the assertion fails at any P carrying the order-specified value. (The test file is order-frozen to the single W7 objective-assertion change, so the test cannot be amended in-round.)
   (b) `test_committed_manifest_matches_regenerated` (E3) rebuilds the sdist from the P tree, which contains the committed `packaging/release_record.json`; the record-inclusion probe (Verification section) proves the sdist then contains `slaif_local_coding-0.1.0/packaging/release_record.json` (109 entries, not 108), so the order-specified `M_P` sdist value ("= M_W7's sdist hash", the 108-entry build WITHOUT the record) cannot match the P-tree regeneration and the gate fails at P.
   The only `M_P` value set that passes the frozen gates at P is therefore mechanically determined (not a judgment choice): `generated_from.git_commit = W6b` (= record `image_source_commit`, per R4(a)) and `artifacts.sdist` = the fresh record-present build hash (per the E3 gate at P; entry count 109), with the wheel unchanged at `H_new` and all other fields exactly as ordered. Recorded for strategy's re-adjudication in 013-h; coding performs no G5 work this round.
3. **Registry interim state (factual):** `0.1.0` + `sha-<W6b>` now exist at digest `D` in a non-public package, unrecorded in the repository (no P). The ONE controlled dispatch is CONSUMED (run `35263999980`); the order's failure law authorizes no re-dispatch and the follow-up round records the EXISTING `D` (no new image, no new tags, no orphan created).
4. **Documentation staleness (factual, 013-h item):** see Documentation section — the pre-publication statements are now stale against registry reality.
5. Pre-existing state (unchanged by this round): the private `sha-be3c78b…` version (W4 build) remains an unreferenced orphan; orphan cleanup is a strategic act, not authorized here.

## Recommended strategic follow-up
Factual only; strategy decides:
1. Perform (or authorize the credential-holder to perform) the EXACT human act of blocker 1 (package visibility → public), then verify both tags resolve anonymously to `D`.
2. Issue the follow-up round (013-h): G4 (W7) + G5 (P) + G6 (FIRST EXECUTED `docker-published` + pull-based compose on canonical 18031 + documentation-truthfulness statement-by-statement + R at P), with the `M_P` identity binding re-adjudicated per finding 2 (or that finding explicitly confirmed/refuted by strategy). NO new dispatch — record `D = sha256:a5debcb24bb6bbf7cf00dbf80cd17367d57186f6b0d7fadac020b94df53a0011` and run id `35263999980` from this round's remote run; the image-source commit remains `S = W6b = fe334e87c9f0fc65d1826cf9af7dad7e9f70a94a`.
3. Post-merge: Git tag `v0.1.0` → W6b + GitHub Release (strategy acts).
4. Optional orphan cleanup of the private `sha-be3c78b…` version (strategy's choice).
5. Process note (factual): the 013-g order + `oap/active → 013-g` transcript bytes remain in the coding working tree uncommitted per the order's exact file sets; the follow-up round's transcript should commit them (with the follow-up order) per the standing protocol.

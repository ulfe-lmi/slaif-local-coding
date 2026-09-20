# OAP Work Order — 013-g

## Objective

Objective 013, round `013-g` (AMENDS the single Objective-013 PR #15 — NO new
numeric objective, NO new PR): commit the minimal hash correction to the
committed manifest (`W6b`), then complete the ONE controlled GHCR publication
at the new green implementation head `S := W6b`, the visibility layer, and —
if and only if visibility passes with available credentials — the generator
bump `W7`, the release-record commit `P`, the FIRST EXECUTED
`docker-published` gate, and the report `R`.

## Strategic re-adjudication (primary evidence; strategy-verified at drafting time)

- Round 013-f BLOCKED pre-dispatch (report commit
  `b3cd922cf573809230cc44b979bcff6392c946f5`, report-only, parent = W6
  `49eb6034b0be2e437ff90455954557af4d469528`): E1 complete — the corrected
  013-e order bytes are committed at W6 (original
  `028704c4400e3e8003295c752d72e4a6ecdf926a294771c9648d6479120f63be` /
  corrected `4c42a5fe3bd337398750a4cf3c9da6fc6a9f16ef0a183d35baaeb14ecdd0f60c`,
  one blank line at line 134; W6's format step SUCCESS), and W6's CI
  (`35258007797`) was 3/4: `docker` SUCCESS (15/15 phases, wheel bound to
  `H_new`), `gateway-contract` SUCCESS (frozen peer), `docker-published`
  SUCCESS (explicit not-yet-published skip), `test` FAILURE at
  `uv run --frozen pytest -q` on exactly ONE test: the E3 regeneration gate
  `test_committed_manifest_matches_regenerated`. The ONE controlled
  publication was NOT consumed; the registry is unchanged.
- Root cause (independently re-proven by strategy at this order's drafting
  time, clean detached worktree builds): the committed manifest `M_W5`
  (recorded in round 013-e) carries sdist hash
  `6537f6266cc7a77ce427fd7c8af0675abb3b496d444b75e7c858fec909fc9fc2`
  (439,894 B) — NOT reproducible from any clean checkout: a clean detached
  worktree of W5 (`e425987…`) AND of W6 (`49eb603…`) both build the sdist to
  SHA-256 `5a60cd6ef41764f16871fd0134b6c234409ba2708b3159bdc0863fc84e7e520f`
  (439,900 B, 108 entries; entry list and file contents byte-identical
  between the two clean builds). The W5→W6 tree delta is `oap/`-only (an
  sdist exclusion), so the true sdist identity of the W5/W6 trees is
  `5a60cd6e…`. The W5-round hash was recorded from a transient working-tree
  state (the 013-f report's clean-W4 control — which reproduces `M_W4`
  exactly — proves the build pipeline itself is reproducible; the defect is
  the recording, not the pipeline). This is a round-013-e implementation
  defect (artifact-hash mis-recording) caught, as designed, by the E3 gate
  on the first CI in which pytest actually ran.
- **Normative correction (recorded):** the committed manifest is corrected
  at `W6b` with EXACTLY two field changes — `artifacts.sdist.sha256` →
  `5a60cd6ef41764f16871fd0134b6c234409ba2708b3159bdc0863fc84e7e520f` and
  `artifacts.sdist.size_bytes` → `439900` — no other byte of the manifest
  changes (`entry_count` 108, wheel `H_new`, `objective "013-e"`,
  `generated_from.git_commit = 59439963a02e8cd6c341708e606f907ef1e6771d`
  (= R, W5's parent — remains truthful: the manifest is generated from
  W5's tree, whose sdist inputs are byte-identical at W6b), frozen peer,
  not-yet-published state). The W6b commit message records old/new hash +
  size and the clean-worktree proof.
- Process norm (binding for this objective, rounds 013-g onward): any
  manifest artifact hash MUST be computed from a clean detached worktree of
  the relevant committed tree (never from a dirty working tree), and the
  commit message must record the proof.
- Identity re-adjudication: the correction commit `W6b` becomes the new
  image-source commit `S` for the single dispatch (GITHUB_SHA at dispatch,
  in-image `org.opencontainers.image.revision` label, `v0.1.0` tag target,
  and the `M_P` chain all anchor at `W6b`). `W6` and its E1 order-byte
  correction remain in history unchanged. The dispatch precondition
  "CI FULLY GREEN 4/4 before any dispatch" is met at `W6b`.
- Gateway release peer: UNCHANGED, FROZEN at
  `08ca421bee1ddca62078302b910e8be88cf705be` for release 0.1.0 (the 013-d
  freeze rule stands). Strategy re-verified at drafting time: Gateway
  `main` has advanced again to
  `845695f03c41233754f276e99c8bf7014d5c21a0` (unrelated development since
  `1bdbb8bf…`); the three Local contract source blobs are byte-identical at
  the frozen pin AND at `845695f0…`: `contract.py` =
  `9e8ae5ef8e1f9d8d48bf3627b9a767d86593a6ac`; `codex_0149.py` =
  `8976c984c4430d65b3d36bad8565062a8c6f955a`; `streaming.py` =
  `73cc9f99e8c3cb2f3eb95173344bfbdc211c71ff`. NO re-pin. The round must
  re-verify all three blob SHAs at the frozen pin and at current Gateway
  `main` (record the current main SHA if it moved) and run the strict gate
  18/18 against the frozen peer (network guard enabled).

## GitHub objective state

- Objective number: 13; round: `013-g`; PR mode: `AMEND_EXISTING_PR`.
- PR: #15 `https://github.com/ulfe-lmi/slaif-local-coding/pull/15` (the
  single Objective-013 PR; OPEN; MERGEABLE).
- Branch: `oap/013-mvp-release-publication`; base `main` @
  `a04693e6792df6a8ad4262acfb46336a0f662202`.
- Starting remote SHA (at this order's drafting time):
  `b3cd922cf573809230cc44b979bcff6392c946f5` (the 013-f report commit;
  report-only; parent = W6).
- Commit chain for this round: `W6b` (child of W6) → [dispatch at W6b] →
  (visibility pass only) `W7` (child of W6b) → `P` (child of W7, EXACTLY
  two files) → `R` (report-only, child of P). In the visibility-blocked
  branch: `W6b` → `R` (report-only, child of W6b; BLOCKED status).
- Implementation head for publication: `W6b` (= `S`, the image-source
  commit). `W7` exists only after a successful, visibility-passing
  publication and changes NO publication input.

## Bounded scope (workstreams)

### G1 — Manifest correction commit `W6b`

`W6b` = child of `49eb6034b0be2e437ff90455954557af4d469528`, EXACTLY ONE
file: `packaging/release_provenance_manifest.json`, with EXACTLY the two
field changes of the normative correction above (`artifacts.sdist.sha256` →
`5a60cd6ef41764f16871fd0134b6c234409ba2708b3159bdc0863fc84e7e520f`;
`artifacts.sdist.size_bytes` → `439900`). No other byte of the file
changes. Commit message: old/new sha256 + size, "minimal manifest
correction: W5-round sdist hash was recorded from a transient working tree
(clean worktree builds of W5/W6 both yield 5a60cd6e…, 439900 B, 108
entries); E3 gate now reproducible on any clean checkout".
Before pushing: the clean-worktree proof per the process norm (detached
worktree of W6 → `uv build --sdist` → recorded sha256/size must equal the
corrected values; record the command + output; record the sdist entry list
and verify `packaging/release_provenance_manifest.json` is NOT an entry —
`pyproject.toml` top-level build exclusions exclude it from every artifact,
so the corrected value is a fixed point: the W6b sdist is byte-identical to
the W5/W6 clean sdist); local E3 suite
(`tests/test_release_provenance_manifest.py`) green at the W6b tree;
`ruff check .` / `ruff format --check .` green. CI at W6b FULLY GREEN 4/4
(`test` job: full pytest green including the E3 regeneration gate; `docker`
job: 15/15 phases, wheel bound to `H_new`; `gateway-contract` green at the
frozen peer; `docker-published` on the explicit not-yet-published skip
path).

### G2 — The ONE controlled publication at `S := W6b`

Re-specification of 013-f E2 with `W := W6b` (the 013-d/013-e/013-f rounds
never consumed the dispatch):
- Pre-dispatch anonymous registry probe (token NOT in the environment;
  `scripts/ghcr_tag_check.py`): `0.1.0` → record (expect `absent`);
  `sha-<W6b>` → record (expect denied/absent — the package is non-public);
  `sha-be3c78b…` → record (expect denied/absent — the pre-existing private
  version; must remain UNTOUCHED by this round).
- Verify branch tip = W6b (`git ls-remote`) immediately before dispatching.
- EXACTLY ONE dispatch: `gh workflow run release-image.yml --ref
  oap/013-mvp-release-publication` (branch tip = W6b at dispatch time).
- Classify and report EACH layer separately (same eight layers as 013-e
  D3 / 013-f E2): (1) workflow start + checkout; (2) wheel-binding assert
  (fresh wheel == `H_new`); (3) image build (two-file compose,
  `mvp-release-0.1.0` label); (4) GHCR authentication success (GITHUB_TOKEN
  login); (5) GHCR authorization + image upload success (no
  scope/permission denial); (6) in-script registry verification: BOTH tags
  `0.1.0` and `sha-<W6b>` resolve to ONE digest `D` (no-silent-repoint
  guard respected; the 013-e D1 fix prints the parsed digest line — record
  it); (7) package visibility / anonymous pullability per G3; (8) capture
  `D` (`sha256:<64-hex>`) + the workflow run id; then INDEPENDENT anonymous
  re-verification: `0.1.0` → `D` and `sha-<W6b>` → `D`.
- Image-source identity: `S := W6b` (GITHUB_SHA at dispatch = W6b; in-image
  revision label = W6b). W6b changes only the manifest, which
  `pyproject.toml` explicitly excludes from every artifact (top-level build
  exclusion commented "The manifest hashes the artifacts, so it (and its
  schema) stay in git and are never part of any artifact (no self-hash
  fixed point needed)"; verified against the clean W6 sdist: 108 entries,
  `packaging/` holds only `readyz-wait.sh` and the two service-unit files),
  and it is not a build-context path; the W6b sdist is therefore
  BYTE-IDENTICAL to the W5/W6 clean sdist (`5a60cd6e…`, 439,900 B, 108
  entries) and the W6b-built image is wheel- and layer-identical to the
  W5/W6-built image modulo the revision label; the run's wheel-binding line
  is the proof.
- Failure law (inherited verbatim): report the exact failing layer with
  raw log lines; NO re-dispatch for an authorization/permission-class
  failure (strategy re-adjudicates with primary evidence — a genuine
  org-policy boundary is a human decision with ONE precise choice); ONE
  deterministic re-dispatch ONLY for a transient-infrastructure failure
  (runner error before any registry interaction); a second failure of any
  kind → STOP and report. Partial registry state → STOP and report (orphan
  cleanup is a strategic act; no silent repoint).

### G3 — Package visibility (layer 7), ONLY after a successful G2 push

Identical to 013-f E3:
- Branch A (both tags anonymously resolvable to `D`): layer 7 PASSED;
  proceed to G4.
- Branch B (either not anonymously resolvable — EXPECTED): attempt EXACTLY
  ONE visibility API call with the wrapper's existing `gh` credential:
  `PATCH /orgs/ulfe-lmi/packages/container/slaif-local-coding` with body
  `{"visibility":"public"}`; record the HTTP status + body verbatim (no
  credential value anywhere).
  - B-2 (2xx): re-run anonymous probes of BOTH tags; both must resolve to
    `D`; record the state change exactly; proceed to G4.
  - B-3 (403/401/404 — credential-scope boundary, NOT an org-policy
    decision): layer 7 = **HUMAN UI ACT REQUIRED**. STOP the round here
    with a BLOCKED-at-G3 report (child of W6b): capture `D`, the run id,
    layers 1–6 PASSED (raw-log evidence), layer 7 blocked with the verbatim
    API response, and the EXACT human act: GitHub UI — organization
    `ulfe-lmi` → Packages → `slaif-local-coding` (container) → package
    visibility → public — OR an API PATCH performed with a credential
    holding the packages scope. State the post-act verification (anonymous
    resolution of both tags → `D`) and that the follow-up round then
    completes G4 (W7) + G5 (P) + G6 (R at P). Do NOT create W7 or P in
    this branch. No second API attempt; no workaround.

### G4 — Generator/E3 objective bump and manifest `M_W7` — ONLY in G3 branch A/B-2

`W7` = child of W6b, EXACTLY three files:
1. `scripts/release_provenance_manifest.py`: `OBJECTIVE` → `"013-g"` (plus
   the docstring order reference).
2. `tests/test_release_provenance_manifest.py`: E3 objective assertion →
   `"013-g"`.
3. `packaging/release_provenance_manifest.json` → `M_W7` regenerated at W7's
   tree, NOT-YET-PUBLISHED state (the release record does not exist until
   P): `objective "013-g"`; `oci.published: false`; `oci.image_digest:
   null`; no `release` key; `status.released: false`; `gateway_peer.commit
   = 08ca421bee1ddca62078302b910e8be88cf705be` (FROZEN); `artifacts.wheel.
   sha256 = oci.wheel_sha256 = H_new` (unchanged); `artifacts.sdist.sha256`
   = the fresh `uv build` sdist hash at W7's tree, computed per the process
   norm from a CLEAN detached worktree (NEW value — the ONLY sdist-input
   change at W7 is the E3 test-file edit,
   `tests/test_release_provenance_manifest.py`; the generator-script change
   is in `scripts/`, excluded from all artifacts, and the manifest itself is
   likewise excluded);
   `generated_from.git_commit = W6b`.
Local proof at W7: clean-worktree build reproduces `M_W7` hashes
byte-for-byte; `artifact_policy_check.py --inspect` + `--install-smoke` on
the fresh build; the manifest module suite (E3 now asserts `"013-g"`)
green. CI at W7 FULLY GREEN 4/4. W7 changes NO publication input and NO
build-context path; the published image at `S = W6b` is unaffected (the
dispatch already happened at W6b).

### G5 — Release-record commit `P` — ONLY in G3 branch A/B-2

`P` = DIRECT child of W7, EXACTLY two files:
1. `packaging/release_record.json` (schema `slaif-release-record-v1`, per
   the 013-a R1 field set): `git_tag = "v0.1.0"`; `image_source_commit =
   W6b` (= S); `oci_image_digest = "sha256:" + D`; `oci_tags = ["0.1.0",
   "sha-<W6b>"]`; `published_at` = RFC 3339 UTC of the successful G2
   publication run; `publication_workflow_run_id` = the G2 run id; plus the
   remaining schema-required fields per the 013-a contract (unchanged
   semantics).
2. `packaging/release_provenance_manifest.json` → `M_P` regenerated from
   W7's tree with the record present (generator's published state):
   `objective "013-g"`; `oci.published = true`; `oci.image_digest =
   "sha256:" + D`; `status.released = true`; `release.git_tag_target =
   W6b`; `generated_from.git_commit = W7`; `gateway_peer.commit =
   08ca421bee1ddca62078302b910e8be88cf705be` (frozen); artifact hashes
   (wheel `H_new`; sdist = `M_W7`'s sdist hash) UNCHANGED from `M_W7`.
`P` changes NO other file.

### G6 — CI at `P` (FIRST EXECUTED `docker-published`) and report `R` — ONLY in G3 branch A/B-2

- CI at P FULLY GREEN, including the **EXECUTED** `docker-published` job
  (its first-ever execution — a green pre-publication CI where
  `docker-published` follows the explicit not-yet-published skip path is
  NOT release evidence; this execution against the real registry image IS
  the release evidence): pull by digest `D` and by both tags (anonymous —
  this also mechanically re-proves the G3 visibility semantics), each
  resolving to `D`; registry-API cross-check; OCI label set verified
  against the record/manifest (revision == W6b; version `0.1.0`;
  `slaif-local-coding.gateway.peer.sha == 08ca421…`; wheel == `H_new`;
  qualification `mvp-release-0.1.0`; topology unchanged); the PULL-BASED
  compose (primary file only, `SLAIF_LOCAL_CODING_IMAGE` digest-pinned, NO
  `build` key) against the disposable fake upstream on canonical port
  18031: readiness healthy; representative signed request succeeds;
  negative contract cases fail closed; missing-secret readiness
  fail-closed; NO-BUILD proof (image exists locally only via pull; running
  container image ID == pulled image ID); teardown absence proof.
  - **Narrow gate-defect exception (inherited):** ONLY IF the first
    execution fails due to a defect in the never-executed gate itself, a
    MINIMAL fix to `.github/workflows/ci.yml` and/or
    `scripts/docker_qualification_ci.py` is authorized within this round as
    a documented deviation, provided it removes, skips, or weakens NO
    011/012/013 qualification semantics. Any other cause → report and stop.
- Post-publication documentation truthfulness (verification duty ONLY; NO
  doc changes in this round): verify each current-facing release statement
  (Publication section of `docs/RELEASE-ARTIFACT-POLICY.md`, the
  corresponding current-state statement in `docs/DOCKER-INSTALL.md`, the 013
  line of `docs/IMPLEMENTATION-ROADMAP.md`, the roadmap/COMPLETENESS
  current-state lines) against the exact P-state facts (the image published
  at digest `D` by path reference only; `packaging/release_record.json`
  present from P onward; zero Git tags and zero GitHub Releases verified
  live — they are strategy post-merge acts; cutover NOT performed). Record
  the verification in the report; if ANY statement is stale at P, record it
  precisely as a 013-h item — do NOT change documentation in this round.
- `R` = report-only commit, child of P (first parent = P). In the G3
  branch-B-3 case: `R` = report-only commit, child of W6b (first parent =
  W6b), status BLOCKED, and NO W7/P exist.

## Identity bindings (normative)

- S (image-source commit) = W6b — the tree the G2 dispatch builds from
  (GITHUB_SHA = W6b; in-image revision label = W6b).
- D = the single digest BOTH published tags resolve to, captured from the
  successful G2 run and re-verified anonymously (layer 8).
- W7 = the post-publication generator-bump commit (child of W6b); P = the
  release-record commit (DIRECT child of W7); R = the report (child of P or
  of W6b in the blocked branch).
- Git tag `v0.1.0` target (strategy, post-merge) = S = W6b.
- `org.opencontainers.image.revision` label = S = W6b.
- `M_P.generated_from.git_commit = W7` (the parent of the containing
  commit P); `M_W7.generated_from.git_commit = W6b`.
- No circularity: the image is built from S = W6b; the record at P
  describes S + D truthfully; P ≠ S; the tag points at S; the manifest at P
  is generated from W7 (which changed no publication input).

## Explicit non-goals (all 013-a … 013-f non-goals inherited, plus)

- NO changes to: `src/`, `pyproject.toml`, `uv.lock`, `config/`,
  `Dockerfile`, `.dockerignore`, `compose.yaml`, `compose.build.yaml`,
  `.github/workflows/ci.yml` (except the narrow G6 gate-defect exception),
  `.github/workflows/release-image.yml` (BYTE-IDENTICAL),
  `scripts/ghcr_tag_check.py`, the gateway-contract gate/fixture,
  `oap/reports/*` (immutable), ANY `oap/orders/*` file (ALL historical
  order files — including the corrected 013-e bytes at W6 and the 013-f
  order — remain byte-identical in this round), or any `docs/` file (no doc
  changes in this round at all).
- `packaging/release_provenance_manifest.json` is unfrozen ONLY for the G1
  single correction (W6b) and the G4 regeneration (W7); no other manifest
  commit exists in this round.
- `scripts/release_provenance_manifest.py` and
  `tests/test_release_provenance_manifest.py` change ONLY in W7 (the
  objective-constant/docstring bump and the E3 assertion); the 013-e D1
  digest-capture fix in `scripts/release_registry_publish.py` and its test
  file are BYTE-IDENTICAL in this round.
- NO protected-host mutation (Qwen/18020, `qwen-serving` units, model/
  checkpoint/patches/venv/systemd/launch flags, API keys, firewall/VPN/
  network bindings, active Codex profiles); NO docker build/run/up on the
  protected host; NO live cutover; NO Qwen/protected-model inference.
- NO Gateway-repository mutation (read-only verification only; peer remains
  `08ca421…`; the fixture is NOT re-pinned).
- NO Git tag / GitHub Release by coding. NO repository Actions/security
  setting change. NO new credentials; NO re-provisioning of any repository
  secret; NO credential-scope change; NO second visibility API attempt.
- NO registry publication other than the single authorized G2 dispatch
  (which writes `sha-<W6b>` + `0.1.0`); NO repoint of any pre-existing tag
  (in particular `sha-be3c78b…` remains untouched); NO package/version
  deletion. NO re-dispatch except the single transient-infrastructure
  exception of G2. NO version change (stays `0.1.0`).

## Required evidence (report)

- G1: the old/new sdist sha256 + size pair; the clean detached-worktree
  build proof (command + recorded output: sha256 `5a60cd6e…`, 439,900 B,
  108 entries, entry list proving the manifest file is not an sdist
  entry); the exact one-file two-field diff; the local E3 suite
  green; CI at W6b (4/4; the `docker` job 15-phase summary; the E3 pytest
  now passing).
- G2: layer classification 1–8 with raw log lines (at layer 6, the parsed
  digest line as printed by the fixed script); the wheel-binding line; the
  no-publication-input delta proof (`git diff --name-only
  49eb6034b0be2e437ff90455954557af4d469528..W6b` = exactly
  `packaging/release_provenance_manifest.json`).
- G3: the branch taken with verbatim API response (B-2/B-3) or the
  anonymous probe outputs (A); post-act anonymous re-verification for B-2.
- G4 (if run): clean-worktree build reproducing `M_W7` byte-for-byte
  (wheel `H_new`; sdist new hash) + `artifact_policy_check.py --inspect` +
  `--install-smoke`; CI at W7 (4/4).
- G5 (if run): the exact two-file proof + every field value.
- G6 (if run): the EXECUTED `docker-published` phase summary; the
  documentation-truthfulness verification (per statement, live-verified
  zero tags/zero releases).
- Registry state before (pre-dispatch probes) and after (layer-8 +
  post-round probes), token-free; the pre-existing `sha-be3c78b…` version
  untouched (probe record).
- Protected-host before/after read-only probe table (must equal the
  standing baseline; if anything moved, STOP and report).
- Grep proofs: NO `secrets.SLAIF_GHCR_TOKEN` in active files (only the
  immutable OAP transcripts may match); the release workflow's only
  `secrets.` references are `secrets.GITHUB_TOKEN`.
- Gateway freeze re-verification at round time: the three contract blob
  SHAs at `08ca421…` AND at current Gateway `main` (record the current main
  SHA — `845695f03c41233754f276e99c8bf7014d5c21a0` at drafting time, or the
  newer SHA if it moved; blob identity required at both; strict gate 18/18
  against the frozen peer, network guard enabled).
- 013-a R1–R20 re-affirmation at the round's final state (R12 SATISFIED if
  G2 succeeded; R13 by the EXECUTED gate in the G5/G6 branch; R1 at P in
  the G5 branch). Note explicitly: the CI at the 013-f report commit
  (`b3cd922…`, run `35259265832`) failed on the same stale-hash E3 test and
  is superseded by the green CI at W6b; the 013-f W6 CI
  (`35258007797`) failed solely on that test (format step SUCCESS — the
  013-e order-byte correction is in place and working).
- Safety/scope confirmations (standard set), known limitations/blockers,
  and the exact remaining strategic/human acts (visibility human act if G3
  branch B-3; then Git tag `v0.1.0` → W6b + GitHub Release; optional orphan
  cleanup of the private `sha-be3c78b…` version — strategy's choice, not
  authorized here).

## Report contract

- Path: `oap/reports/013-g-manifest-correction-and-complete-publication.md`.
- Report-only SELF commit; first parent = P (G5 branch) or W6b
  (G3-blocked branch); `Implementation head SHA` = W6b in both branches.
- Status: COMPLETE (G5 branch) or BLOCKED (G3 branch B-3, with the exact
  human act) — a G2 run failure is reported with the failing layer per the
  G2 failure law.
- After publishing the report commit and verifying it remotely (PR head = R,
  report-only, parent verified), send exactly two bytes `OK` to
  `response.fifo`.

## Safety/scope (restated)

Routine terminal/setup belongs to coding. The protected live-host boundary
is absolute. No human/strategy recruitment for routine work. No merge by
coding. No auto-merge. One numeric objective = one PR: this round amends PR
#15 only. The single manifest correction of G1 is a hash-recorded
correction of a round-013-e mis-recording (old/new values recorded in this
order, the W6b commit message, and the 013-g report); no other OAP
transcript byte or artifact byte is touched except as the workstreams above
define.

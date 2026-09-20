# OAP Work Order — 013-f

## Objective

Objective 013, round `013-f` (AMENDS the single Objective-013 PR #15 — NO new
numeric objective, NO new PR): commit the strategy-corrected bytes of the
013-e order file (the sole blocker recorded by the 013-e BLOCKED report), then
complete the ONE controlled GHCR publication at the new green implementation
head `W6`, the visibility layer, and — if and only if visibility passes with
available credentials — the generator bump `W7`, the release-record commit
`P`, the FIRST EXECUTED `docker-published` gate, and the report `R`.

## Strategic re-adjudication and normative correction record

- The 013-e round BLOCKED pre-dispatch (report commit `277b8173869b2a5d6563a4f31e3f99e0670cb241`,
  report-only, parent = W5 `e42598775746321630eaa7f9e2d862b1abbec118`): W5's D1
  digest-capture fix (12 unit tests) and D2 manifest `M_W5` (objective 013-e,
  not-yet-published, wheel `H_new` unchanged, new sdist
  `6537f626…`, peer `08ca421…` frozen, generated_from =
  `59439963a02e8cd6c341708e606f907ef1e6771d`) are complete and remote; the CI
  at W5 (`35254602764`) was 3/4 — `gateway-contract` SUCCESS, `docker`
  SUCCESS (all 15 qualification phases PASSED, wheel bound to `H_new`),
  `docker-published` SUCCESS (explicit not-yet-published skip), `test`
  FAILURE at `uv run --frozen ruff format --check .`. The ONE controlled
  publication was NOT consumed (no dispatch); the registry is unchanged
  (`0.1.0` absent; `sha-<W5>` absent; the pre-existing private
  `sha-be3c78b…` version untouched).
- Root cause (primary evidence, strategy-verified at this order's drafting
  time): the pinned formatter `ruff 0.16.4` formats fenced Python code blocks
  inside Markdown files. The CI log shows the single unformatted file as
  `oap/orders/013-e-fix-publish-verification-and-complete-publication.md` —
  the STRATEGIC-AUTHORED order document — with one hunk: insert ONE blank
  line between the blank line following the closing `)` of the
  `PUSH_DIGEST_LINE_RE = re.compile(…)` block and the `def
  extract_push_digest(…)` line (PEP8 two-blank-lines-before-top-level-def).
  362 other files are format-clean. This is a strategic order-authoring
  defect (the order file was published without passing the repository's
  own format gate against its embedded code block); the coding agent
  correctly refused to mutate immutable order bytes or frozen files and
  reported the exact delta.
- **Normative strategic correction (recorded; hash-tracked; NOT a silent
  rewrite):** strategy corrects the 013-e order bytes with EXACTLY ONE
  inserted blank line at that position. Byte identity:
  - original 013-e order bytes (as committed at W5 and executed in round
    013-e): SHA-256 `028704c4400e3e8003295c752d72e4a6ecdf926a294771c9648d6479120f63be`;
  - corrected 013-e order bytes (this round's committed bytes): SHA-256
    `4c42a5fe3bd337398750a4cf3c9da6fc6a9f16ef0a183d35baaeb14ecdd0f60c`.
  The correction changes no normative text of the 013-e order (one blank
  line inside a fenced code-block EXAMPLE). The immutable 013-e report
  remains the valid record of round 013-e; its order-hash reference
  identifies the ORIGINAL bytes as a point-in-time attestation of the round
  as executed. This correction is a recorded strategic act: both byte
  versions are hash-recorded above, in the W6 commit message, and in the
  013-f report; no round's execution facts are re-attributed. Strategy
  process gap recorded: future strategic orders containing fenced Python
  blocks must pass `ruff format --check` on the order file before
  publication.
- Strategic verification of the correction (at this order's drafting time):
  `ruff format --check` on the corrected bytes → "1 file already formatted"
  (exit 0); the diff original→corrected is exactly one inserted blank line.
- Gateway release peer: UNCHANGED, FROZEN at
  `08ca421bee1ddca62078302b910e8be88cf705be` for release 0.1.0 (the 013-d
  freeze rule stands). Strategy re-verified at drafting time: Gateway `main`
  = `1bdbb8bf1534ea0b3217ced136972d1bced9c448` (21 commits beyond the frozen
  pin; unrelated development — main.py, metrics, compose, pyproject, docs,
  Gateway OAP transcripts, one unit test); the three Local contract source
  blobs are byte-identical at `08ca421…` AND `1bdbb8bf…`:
  `contract.py` = `9e8ae5ef8e1f9d8d48bf3627b9a767d86593a6ac`;
  `codex_0149.py` = `8976c984c4430d65b3d36bad8565062a8c6f955a`;
  `streaming.py` = `73cc9f99e8c3cb2f3eb95173344bfbdc211c71ff`. NO re-pin.
  The round must re-verify all three blob SHAs at the frozen pin and at
  current Gateway `main` and record them.

## GitHub objective state

- Objective number: 13; round: `013-f`; PR mode: `AMEND_EXISTING_PR`.
- PR: #15 `https://github.com/ulfe-lmi/slaif-local-coding/pull/15` (the
  single Objective-013 PR; OPEN; MERGEABLE).
- Branch: `oap/013-mvp-release-publication`; base `main` @
  `a04693e6792df6a8ad4262acfb46336a0f662202`.
- Starting remote SHA (at this order's drafting time):
  `277b8173869b2a5d6563a4f31e3f99e0670cb241` (the 013-e report commit R;
  report-only; parent = W5).
- Commit chain for this round: `W6` (child of `277b817…`) → [dispatch at
  W6] → (visibility pass only) `W7` (child of W6) → `P` (child of W7,
  EXACTLY two files) → `R` (report-only, child of P). In the visibility-
  blocked branch: `W6` → `R` (report-only, child of W6; BLOCKED status).
- Implementation head for publication: `W6` (the image-source commit `S`).
  `W7` exists only after a successful, visibility-passing publication and
  changes NO publication input.

## Bounded scope (workstreams)

### E1 — Commit the corrected 013-e order bytes and activate 013-f

`W6` = child of `277b8173869b2a5d6563a4f31e3f99e0670cb241`, EXACTLY three
files (all under `oap/`):
1. `oap/orders/013-e-fix-publish-verification-and-complete-publication.md`
   → the CORRECTED bytes (SHA-256 `4c42a5fe3bd337398750a4cf3c9da6fc6a9f16ef0a183d35baaeb14ecdd0f60c`;
   the exact one-blank-line delta of the correction record above; commit
   message records both SHA-256 values and "strategic correction of the
   013-e order file bytes (format gate); original 013-e round executed on
   the original bytes").
2. `oap/orders/013-f-order-byte-correction-and-complete-publication.md`
   (this order, strategic-authored bytes verbatim).
3. `oap/active` → `013-f`.
No other file. W6 changes NO sdist input (`oap/` is excluded from all
artifacts) and NO build-context path — the wheel stays `H_new =
879baa3ad19e0f513090add965d267957d27f7bcd904d1e225586d76126f8b19` and the
sdist hash stays `M_W5`'s value; `M_W5` remains the current manifest
(no regeneration at W6). BEFORE pushing: local full `ruff format --check .`
MUST be green (this is the gate W5 failed); plus the standard local gates
(`ruff check .`, `mypy` CI-equivalent, full `pytest -q`, compileall) — all
must pass at the W6 tree (the W5 tree passed all of them except the format
step; W6 changes only `oap/` files, so the only gate whose outcome can
change is the format step, which the corrected bytes must make green).
CI at W6 FULLY GREEN 4/4 (the `docker` job must again show all 15
qualification phases PASSED; `docker-published` on the explicit
not-yet-published skip path).

### E2 — The ONE controlled publication at `W6`

Re-specification of 013-e D3 with `W := W6` (the 013-e round's dispatch was
never consumed; the 013-e D3 precondition "CI at W FULLY GREEN 4/4 before
any dispatch" is now met at W6):
- Pre-dispatch anonymous registry probe (token NOT in the environment;
  `scripts/ghcr_tag_check.py`): `0.1.0` → record (expect `absent`);
  `sha-<W6>` → record (expect denied/absent — the package is non-public);
  `sha-be3c78b…` → record (expect denied/absent — the pre-existing private
  version; must remain UNTOUCHED by this round).
- Verify branch tip = W6 (`git ls-remote`) immediately before dispatching.
- EXACTLY ONE dispatch: `gh workflow run release-image.yml --ref
  oap/013-mvp-release-publication` (branch tip = W6 at dispatch time).
- Classify and report EACH layer separately (same eight layers as 013-e
  D3): (1) workflow start + checkout; (2) wheel-binding assert (fresh wheel
  == `H_new`); (3) image build (two-file compose, `mvp-release-0.1.0`
  label); (4) GHCR authentication success (GITHUB_TOKEN login); (5) GHCR
  authorization + image upload success (no scope/permission denial); (6)
  in-script registry verification: BOTH tags `0.1.0` and `sha-<W6>`
  resolve to ONE digest `D` (no-silent-repoint guard respected; with the
  013-e D1 fix, the parsed digest line is now in the run log — record it);
  (7) package visibility / anonymous pullability per E3; (8) capture `D`
  (`sha256:<64-hex>`) + the workflow run id; then INDEPENDENT anonymous
  re-verification: `0.1.0` → `D` and `sha-<W6>` → `D`.
- Image-source identity: `S := W6` (GITHUB_SHA at dispatch = W6; in-image
  `org.opencontainers.image.revision` label = W6). W6 changes only `oap/`
  files (no sdist input, no build context), so the W6-built image is
  wheel- and layer-identical to the W5-built image modulo the revision
  label; record the wheel-binding line as the proof.
- Failure law (inherited verbatim from 013-e D3): report the exact failing
  layer with raw log lines; NO re-dispatch for an authorization/permission-
  class failure (strategy re-adjudicates with primary evidence — a genuine
  org-policy boundary is a human decision with ONE precise choice); ONE
  deterministic re-dispatch ONLY for a transient-infrastructure failure
  (runner error before any registry interaction); a second failure of any
  kind → STOP and report. Partial registry state → STOP and report (orphan
  cleanup is a strategic act; no silent repoint).

### E3 — Package visibility (layer 7), ONLY after a successful E2 push

Identical to 013-e D5:
- Branch A (both tags anonymously resolvable to `D`): layer 7 PASSED;
  proceed to E4.
- Branch B (either not anonymously resolvable — EXPECTED): attempt EXACTLY
  ONE visibility API call with the wrapper's existing `gh` credential:
  `PATCH /orgs/ulfe-lmi/packages/container/slaif-local-coding` with body
  `{"visibility":"public"}`; record the HTTP status + body verbatim (no
  credential value anywhere).
  - B-2 (2xx): re-run anonymous probes of BOTH tags; both must resolve to
    `D`; record the state change exactly; proceed to E4.
  - B-3 (403/401/404 — credential-scope boundary, NOT an org-policy
    decision): layer 7 = **HUMAN UI ACT REQUIRED**. STOP the round here
    with a BLOCKED-at-E3 report (child of W6): capture `D`, the run id,
    layers 1–6 PASSED (raw-log evidence), layer 7 blocked with the verbatim
    API response, and the EXACT human act: GitHub UI — organization
    `ulfe-lmi` → Packages → `slaif-local-coding` (container) → package
    visibility → public — OR an API PATCH performed with a credential
    holding the packages scope. State the post-act verification (anonymous
    resolution of both tags → `D`) and that the follow-up round then
    completes E4 (W7) + E5 (P) + E6 (R at P). Do NOT create W7 or P in this
    branch. No second API attempt; no workaround.

### E4 — Generator/E3 objective bump and manifest `M_W7` — ONLY in E3 branch A/B-2

`W7` = child of W6, EXACTLY three files:
1. `scripts/release_provenance_manifest.py`: `OBJECTIVE` → `"013-f"` (plus
   the docstring order reference).
2. `tests/test_release_provenance_manifest.py`: E3 objective assertion →
   `"013-f"`.
3. `packaging/release_provenance_manifest.json` → `M_W7` regenerated at W7's
   tree, NOT-YET-PUBLISHED state (the release record does not exist until
   P): `objective "013-f"`; `oci.published: false`; `oci.image_digest:
   null`; no `release` key; `status.released: false`; `gateway_peer.commit
   = 08ca421bee1ddca62078302b910e8be88cf705be` (FROZEN); `artifacts.wheel.
   sha256 = oci.wheel_sha256 = H_new` (unchanged); `artifacts.sdist.sha256`
   = the fresh `uv build` sdist hash at W7's tree (NEW value — the E4 test-
   file change is an sdist input); `generated_from.git_commit = W6`.
Local proof at W7: fresh `uv build` reproduces `M_W7` hashes byte-for-byte;
`artifact_policy_check.py --inspect` + `--install-smoke` on the fresh
build; the manifest module suite (E3 now asserts `"013-f"`) green. CI at W7
FULLY GREEN 4/4. (W7 changes NO publication input and NO build-context
path; the published image at `S = W6` is unaffected — the dispatch already
happened at W6.)

### E5 — Release-record commit `P` — ONLY in E3 branch A/B-2

`P` = DIRECT child of W7, EXACTLY two files:
1. `packaging/release_record.json` (schema `slaif-release-record-v1`, per
   the 013-a R1 field set): `git_tag = "v0.1.0"`; `image_source_commit =
   W6` (= S); `oci_image_digest = "sha256:" + D`; `oci_tags = ["0.1.0",
   "sha-<W6>"]`; `published_at` = RFC 3339 UTC of the successful E2
   publication run; `publication_workflow_run_id` = the E2 run id; plus the
   remaining schema-required fields per the 013-a contract (unchanged
   semantics).
2. `packaging/release_provenance_manifest.json` → `M_P` regenerated from
   W7's tree with the record present (generator's published state):
   `objective "013-f"`; `oci.published = true`; `oci.image_digest =
   "sha256:" + D`; `status.released = true`; `release.git_tag_target = W6`;
   `generated_from.git_commit = W7`; `gateway_peer.commit =
   08ca421bee1ddca62078302b910e8be88cf705be` (frozen); artifact hashes
   (wheel `H_new`; sdist = `M_W7`'s sdist hash) UNCHANGED from `M_W7`.
`P` changes NO other file.

### E6 — CI at `P` (FIRST EXECUTED `docker-published`) and report `R` — ONLY in E3 branch A/B-2

- CI at P FULLY GREEN, including the **EXECUTED** `docker-published` job
  (its first-ever execution — a green pre-publication CI where
  `docker-published` follows the explicit not-yet-published skip path is
  NOT release evidence; this execution against the real registry image IS
  the release evidence): pull by digest `D` and by both tags (anonymous —
  this also mechanically re-proves the E3 visibility semantics), each
  resolving to `D`; registry-API cross-check; OCI label set verified
  against the record/manifest (revision == W6; version `0.1.0`;
  `slaif-local-coding.gateway.peer.sha == 08ca421…`; wheel == `H_new`;
  qualification `mvp-release-0.1.0`; topology unchanged); the PULL-BASED
  compose (primary file only, `SLAIF_LOCAL_CODING_IMAGE` digest-pinned, NO
  `build` key) against the disposable fake upstream on canonical port
  18031: readiness healthy; representative signed request succeeds;
  negative contract cases fail closed; missing-secret readiness
  fail-closed; NO-BUILD proof (image exists locally only via pull; running
  container image ID == pulled image ID); teardown absence proof.
  - **Narrow gate-defect exception (inherited from 013-c C8 / 013-d C8 /
    013-e D7):** ONLY IF the first execution fails due to a defect in the
    never-executed gate itself, a MINIMAL fix to
    `.github/workflows/ci.yml` and/or `scripts/docker_qualification_ci.py`
    is authorized within this round as a documented deviation, provided it
    removes, skips, or weakens NO 011/012/013 qualification semantics. Any
    other cause → report and stop.
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
  precisely as a 013-g item — do NOT change documentation in this round.
- `R` = report-only commit, child of P (first parent = P). In the E3
  branch-B-3 case: `R` = report-only commit, child of W6 (first parent =
  W6), status BLOCKED, and NO W7/P exist.

## Identity bindings (normative)

- S (image-source commit) = W6 — the tree the E2 dispatch builds from
  (GITHUB_SHA = W6; in-image revision label = W6).
- D = the single digest BOTH published tags resolve to, captured from the
  successful E2 run and re-verified anonymously (layer 8).
- W7 = the post-publication generator-bump commit (child of W6); P = the
  release-record commit (DIRECT child of W7); R = the report (child of P or
  of W6 in the blocked branch).
- Git tag `v0.1.0` target (strategy, post-merge) = S = W6.
- `org.opencontainers.image.revision` label = S = W6.
- `M_P.generated_from.git_commit = W7` (the parent of the containing
  commit P) — normatively re-stated here because W7 sits between S and P;
  the 013-e D6 coincidence "generated_from == S" is superseded for this
  round by this rule.
- No circularity: the image is built from S = W6; the record at P describes
  S + D truthfully; P ≠ S; the tag points at S; the manifest at P is
  generated from W7 (which changed no publication input).

## Explicit non-goals (all 013-a … 013-e non-goals inherited, plus)

- NO changes to: `src/`, `pyproject.toml`, `uv.lock`, `config/`,
  `Dockerfile`, `.dockerignore`, `compose.yaml`, `compose.build.yaml`,
  `.github/workflows/ci.yml` (except the narrow E6 gate-defect exception),
  `.github/workflows/release-image.yml` (BYTE-IDENTICAL),
  `scripts/ghcr_tag_check.py`, the gateway-contract gate/fixture,
  `oap/reports/*` (immutable), `oap/orders/013-a…013-e files EXCEPT the
  single normative correction to the 013-e order file defined in E1`, or any
  `docs/` file (no doc changes in this round at all).
- NO behavioral change to any script beyond the E4 generator-constant/doc-
  string bump (W7) — the 013-e D1 digest-capture fix in
  `scripts/release_registry_publish.py` and its test file are BYTE-
  IDENTICAL in this round.
- NO protected-host mutation (Qwen/18020, `qwen-serving` units, model/
  checkpoint/patches/venv/systemd/launch flags, API keys, firewall/VPN/
  network bindings, active Codex profiles); NO docker build/run/up on the
  protected host; NO live cutover; NO Qwen/protected-model inference.
- NO Gateway-repository mutation (read-only verification only; peer remains
  `08ca421…`; the fixture is NOT re-pinned).
- NO Git tag / GitHub Release by coding. NO repository Actions/security
  setting change. NO new credentials; NO re-provisioning of any repository
  secret; NO credential-scope change; NO second visibility API attempt.
- NO registry publication other than the single authorized E2 dispatch
  (which writes `sha-<W6>` + `0.1.0`); NO repoint of any pre-existing tag
  (in particular `sha-be3c78b…` remains untouched); NO package/version
  deletion. NO re-dispatch except the single transient-infrastructure
  exception of E2. NO version change (stays `0.1.0`).

## Required evidence (report)

- E1: the two SHA-256 values of the 013-e order file (original/corrected) +
  the one-blank-line diff; the corrected file's `ruff format --check` result;
  the full local `ruff format --check .` green at W6; W6 file set (exactly
  three); CI at W6 (4/4; the `docker` job 15-phase summary).
- E2: layer classification 1–8 with raw log lines (at layer 6, the parsed
  digest line as printed by the fixed script); the wheel-binding line; the
  no-build-context delta proof (`git diff --name-only
  277b8173869b2a5d6563a4f31e3f99e0670cb241..W6` = exactly the three E1
  files, all under `oap/`).
- E3: the branch taken with verbatim API response (B-2/B-3) or the
  anonymous probe outputs (A); post-act anonymous re-verification for B-2.
- E4 (if run): fresh `uv build` at W7 reproducing `M_W7` byte-for-byte
  (wheel `H_new`; sdist new hash) + `artifact_policy_check.py --inspect` +
  `--install-smoke`; CI at W7 (4/4).
- E5 (if run): the exact two-file proof + every field value.
- E6 (if run): the EXECUTED `docker-published` phase summary; the
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
  SHA; blob identity required at both; strict gate 18/18 against the frozen
  peer, network guard enabled).
- 013-a R1–R20 re-affirmation at the round's final state (R12 SATISFIED if
  E2 succeeded; R13 by the EXECUTED gate in the E5/E6 branch; R1 at P in the
  E5 branch). Note explicitly: the CI at the 013-e report commit
  (`277b817…`, run `35255787225`) failed on the same order-file format
  defect and is superseded by the green CI at W6.
- Safety/scope confirmations (standard set), known limitations/blockers,
  and the exact remaining strategic/human acts (visibility human act if E3
  branch B-3; then Git tag `v0.1.0` → W6 + GitHub Release; optional orphan
  cleanup of the private `sha-be3c78b…` version — strategy's choice, not
  authorized here).

## Report contract

- Path: `oap/reports/013-f-order-byte-correction-and-complete-publication.md`.
- Report-only SELF commit; first parent = P (E5 branch) or W6 (E3-blocked
  branch); `Implementation head SHA` = W6 in both branches.
- Status: COMPLETE (E5 branch) or BLOCKED (E3 branch B-3, with the exact
  human act) — an E2 run failure is reported with the failing layer per the
  E2 failure law.
- After publishing the report commit and verifying it remotely (PR head = R,
  report-only, parent verified), send exactly two bytes `OK` to
  `response.fifo`.

## Safety/scope (restated)

Routine terminal/setup belongs to coding. The protected live-host boundary
is absolute. No human/strategy recruitment for routine work. No merge by
coding. No auto-merge. One numeric objective = one PR: this round amends PR
#15 only. The single normative exception to order-byte immutability in this
objective is the hash-recorded strategic correction of the 013-e order file
bytes defined in E1 (both byte versions recorded with SHA-256 in this
order, the W6 commit message, and the 013-f report); no other OAP
transcript byte is touched.

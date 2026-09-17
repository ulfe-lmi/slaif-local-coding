# OAP Work Order — 013-c: Fix release-registry credential and push reference; complete the human-authorized MVP 0.1.0 GHCR publication

## Objective

Complete the human-authorized publication of MVP `0.1.0` to
`ghcr.io/ulfe-lmi/slaif-local-coding` (tags `0.1.0` and `sha-<W>`, one digest
`D`), on PR #15, then close release provenance: release-record commit `P`,
CI fully green including the EXECUTED `docker-published` gate, and the round
report.

The 013-b round completed every pre-publication workstream (B1–B7 verified
green at `S''` = `dfa77fb442a82754bb6af21a2e0fb0af29ddfbab`, CI
35208071525) and was accepted by strategy as BLOCKED at B8 by a verified
repository-authority condition, with two independently confirmed root causes:

1. **Permission ceiling.** Repository
   `default_workflow_permissions = "read"` (API-verified at order time)
   clamps the GITHUB_TOKEN's declared `packages: write`; under the current
   repository policy no GITHUB_TOKEN can push to GHCR. Two deterministic
   failed dispatches: runs `35208313536` and `35209542430`, both failing at
   the push step with the exact line
   `PublishError: docker push ulfe-lmi/slaif-local-coding:sha-dfa77fb… failed:
   unauthorized: access token has insufficient scopes` (log-verified).
2. **Latent push-reference bug** (013-b deviation 2):
   `scripts/release_registry_publish.py` tags and pushes the UNQUALIFIED
   reference `ulfe-lmi/slaif-local-coding:<tag>` (Docker-Hub resolution), not
   the `ghcr.io/…` reference its own docstring specifies.

This order authorizes the minimal-privilege fix for (1) (strategic
re-adjudication 3 below), the deterministic fix for (2), re-publication at the
new final implementation head `W`, capture of `D`, the release-record commit
`P`, green CI including the executed published-image gate, and the report.

## Strategic re-adjudication 3 (recorded; binding on this order)

013-a R11's constraint "NO repository secrets (GITHUB_TOKEN only)" is
WITHDRAWN, limited to the `workflow_dispatch`-only `release-image.yml` and to
this publication mechanism. Rationale:

- The human explicitly authorized MVP release/tag/GHCR publication; the
  verified repository ceiling makes publication with GITHUB_TOKEN impossible.
- The minimal-privilege mechanism available without minting a new interactive
  credential is a **repository secret `SLAIF_GHCR_TOKEN` holding the
  repository-owner classic PAT (scope `repo`)** — the same credential
  identity the coding wrapper already uses for `gh` operations (account
  `jpers1`, classic PAT, scopes `read:org, repo, workflow`, organization
  `ulfe-lmi` member with admin on this repository).
- The secret is loaded ONLY when the release workflow is manually
  dispatched (never on PR/push/branch events); the token is never printed;
  the workflow is frozen except for the exact edits in C2.
- **Explicitly rejected alternative:** raising the repository Actions
  workflow-permission ceiling to `write`. That is a persistent, global
  security-policy broadening affecting every workflow in the repository,
  strictly wider blast radius, and not required. Coding MUST NOT modify the
  repository's Actions settings (or any other repository security setting) in
  any way, in any direction.
- **Accepted residual risk (documented, not a gate):** the stored PAT is a
  broad (repo-scope) credential. The C4 documentation must carry a
  post-release hardening advisory: rotate to a dedicated fine-grained PAT
  scoped to `packages: write` + `contents: read` on this single repository,
  and adopt a rotation procedure. This is post-release advisory, not a
  release prerequisite.
- **Human boundary:** if the PAT-based push is ALSO blocked (organization
  SSO, organization policy, token scope, or any other permission error
  distinct from a fixable in-repo defect), that is a genuine human-authority
  boundary: STOP, do not route around it, do not raise the ceiling, and
  report the exact error evidence (re-adjudication 3, last bullet of the
  013-b order's stop-and-report law applies).

## GitHub objective state

- Numeric objective: `013`; round: `013-c`; mode: `AMEND_EXISTING_PR`
- PR: **#15** — https://github.com/ulfe-lmi/slaif-local-coding/pull/15 — the
  single objective-013 PR; NO new PR
- Branch: `oap/013-mvp-release-publication` (unchanged)
- Base: `main` @ `a04693e6792df6a8ad4262acfb46336a0f662202` (unchanged)
- Head at order time: `b9b90393a4781f80824081f4fd2625c0123b490f` — the 013-b
  report commit (report-only, first parent `dfa77fb…` = `S''`); CI at
  `S''` (35208071525) and at the report head (35212606934) both fully green

## Independently verified current state (strategy, at order time)

- **Registry clean:** anonymous GHCR probes at order time → tag `0.1.0`
  `absent`; tag `sha-dfa77fb442a82754bb6af21a2e0fb0af29ddfbab` `absent`
  (no orphan state to clean; no package object).
- **Ceiling verified:** `GET /repos/ulfe-lmi/slaif-local-coding/actions/
  permissions/workflow` → `{"default_workflow_permissions":"read",
  "can_approve_pull_request_reviews":false}`.
- **Failed runs verified:** 35208313536 and 35209542430, both
  `completed/failure` at the push step, error line as quoted in the
  Objective (strategy read the raw logs).
- **Gateway peer stable:** `ulfe-lmi/slaif-api-gateway` main =
  `08ca421bee1ddca62078302b910e8be88cf705be` (re-verified at order time;
  contract-surface blob-identity at both pins already recorded in the 013-b
  order).
- **Repository owner:** organization `ulfe-lmi`.
- **Protected-host baseline** (read-only probe at order time):
  `qwen-serving-vision.service` active/running (vllm `pid=23961` on
  `0.0.0.0:18020`); ports 18031/18033/18034 closed; `docker ps -a` = three
  pre-existing exited non-slaif containers only;
  `~/.codex/qwen-neumann.config.toml` size 858, mode 600, mtime
  2026-09-13 11:59:21 +02:00.
- **Build-input analysis (strategy):** sdist whitelist (pyproject
  `[tool.hatch.build.targets.sdist]`) = pyproject.toml, uv.lock, README.md,
  LICENSE, NOTICE, THIRD_PARTY_NOTICES.md, CONTRIBUTING.md, src, config,
  packaging, tests, docs, and `.github/workflows/ci.yml` ONLY; top-level
  exclusions remove `scripts/`, `oap/`, and both provenance files from every
  artifact; `release-image.yml` is not in the sdist. The Docker build
  context (Dockerfile + .dockerignore + the COPYed inputs) is untouched by
  this order's file set. Consequences: (i) an image built at the new head `W`
  is LAYER-IDENTICAL to the image built at `S''`, differing only in the
  per-build `org.opencontainers.image.revision` label (design intent);
  (ii) the wheel remains `H_new` =
  `879baa3ad19e0f513090add965d267957d27f7bcd904d1e225586d76126f8b19`
  (83,352 B; README/src unchanged); (iii) the sdist hash CHANGES (docs/ and
  tests/ are sdist inputs) and must be regenerated into the manifest at W2.

## Bounded scope (workstreams)

### C1 — Push-reference fix (unfreezes `scripts/release_registry_publish.py`)

Qualify BOTH registry references in the script as `ghcr.io/<repo>:<tag>`,
i.e. push/tag `ghcr.io/ulfe-lmi/slaif-local-coding:sha-<W>` and
`ghcr.io/ulfe-lmi/slaif-local-coding:0.1.0`, so the code matches the module
docstring. No other behavioral change: the no-silent-repoint guard, digest
capture from the push log, registry-API cross-verification, and the
`SLAIF_PUBLISHED_DIGEST`/`GITHUB_OUTPUT`/JSON-line output contract stay
byte-for-byte as designed. Add a minimal deterministic local proof that the
constructed push references are qualified (e.g. a unit test asserting the
exact reference strings the script builds for a fixture git-sha; NO host
push).

### C2 — Credential mechanism (unfreezes `.github/workflows/release-image.yml`)

Exactly these edits, nothing else (no new steps beyond the fail-fast; no
trigger/job/runner change; the workflow remains `workflow_dispatch`-only):

1. Header comment: replace the "GITHUB_TOKEN ONLY: no repository secrets
   are referenced…" claim with an accurate description of the 013-c
   secret-based mechanism (re-adjudication 3: dispatch-only loading; never
   printed; credential identity class).
2. `permissions:` → `contents: read` ONLY (drop the ceiling-clamped
   `packages: write`; registry authentication uses the secret).
3. NEW fail-fast step immediately after checkout: the run fails early (before
   any build) when the secret is missing or empty
   (`test -n "$SLAIF_GHCR_TOKEN"` with `env: SLAIF_GHCR_TOKEN:
   ${{ secrets.SLAIF_GHCR_TOKEN }}`).
4. Login step: authenticate to `ghcr.io` with the secret:
   `printf '%s' "$SLAIF_GHCR_TOKEN" | docker login ghcr.io -u
   "${{ github.repository_owner }}" --password-stdin` (username form
   unchanged: the org name). Never print the token (no echo, no unmasked
   environment dumps).
5. Push step: keep the existing `SLAIF_GHCR_TOKEN` env (now sourced from the
   secret), keep the publish-script invocation and ALL build/verify steps
   unchanged (wheel-binding assert, two-file compose build with
   `SLAIF_GIT_SHA`/`SLAIF_WHEEL_SHA256`/`SLAIF_QUALIFICATION_LABEL`,
   registry verification).

### C3 — Secret provisioning (the ONLY repository-state mutation authorized this round)

- Coding sets repository secret `SLAIF_GHCR_TOKEN` = the wrapper's own
  classic PAT (exactly the value `gh auth token` returns) via
  `gh secret set SLAIF_GHCR_TOKEN --repo ulfe-lmi/slaif-local-coding`
  (value via stdin/heredoc, never on a visible command line).
- Timing: AFTER W2's CI is fully green, BEFORE the C7 dispatch.
- The report records the credential IDENTITY (account `jpers1`, classic PAT,
  scopes `read:org, repo, workflow`, purpose: GHCR push for the
  dispatch-only release workflow) and the redacted command; NEVER the value.
- Do not create any new token/credential. Do not alter the wrapper's auth.
  Do not touch any other repository secret. Do not modify any repository
  Actions/security setting (the ceiling stays `read` — enforced).

### C4 — Documentation reconciliation (credential mechanism)

Update exactly the three current-facing statements that claim
GITHUB_TOKEN-only publication:

- `docs/RELEASE-ARTIFACT-POLICY.md` (the two "GITHUB_TOKEN only" lines,
  ~35 and ~213 at order time)
- `docs/DOCKER-INSTALL.md` (~331: "GITHUB_TOKEN only; no repository
  secrets — activated but NOT yet…")

to the secret-based mechanism, including: dispatch-only loading of the
secret; never printed; credential identity class (org-member classic PAT,
`repo` scope); the explicit rejection of the repo-ceiling alternative; and
the post-release hardening advisory (dedicated fine-grained
`packages: write` + `contents: read` PAT, rotation procedure). No other
documentation changes. The 013-b B5 released-truth wording (path-only digest
references; no literal digest in any document; the Git tag and GitHub
Release described as strategy post-merge acts that do not yet exist)
remains intact and must still be true when this round completes.

### C5 — Commit sequence and final implementation head `W`

- **W1** (child of `b9b9039…`): C1 + C2 + the activated 013-c order file
  (`oap/orders/013-c-fix-registry-credential-and-complete-publication.md`,
  strategic-authored bytes committed verbatim) + `oap/active` → `013-c`
  (one-line change). No generator/test/manifest/doc changes in W1, so W1's
  tree leaves the sdist inputs and the committed manifest
  (`objective "013-b"`, hashes of the `S''` artifacts) mutually consistent:
  **CI at W1 MUST be fully green (4/4)** (the `oap/` transcript files are
  excluded from every artifact; `scripts/` and `release-image.yml` are not
  sdist inputs).
- **W2** (child of W1): C4 + the generator/test objective bump
  (`scripts/release_provenance_manifest.py` `OBJECTIVE` → `"013-c"` and its
  docstring reference; `tests/test_release_provenance_manifest.py` E3
  objective assertion → `"013-c"`) + the manifest-regeneration commit
  producing `M_W2`: `objective "013-c"`; not-yet-published state
  (`oci.published: false`, `oci.image_digest: null`, no `release` key,
  `status` per the not-yet-published schema); `gateway_peer.commit =
  08ca421…`; `artifacts.wheel.sha256 = oci.wheel_sha256 = H_new` (unchanged);
  `artifacts.sdist.sha256` = the NEW sdist hash (changed, per the
  build-input analysis; must equal a fresh `uv build` at W2);
  `generated_from.git_commit = W1`.
- **`W := W2`** is the new IMAGE-SOURCE HEAD. **CI at W2 MUST be fully
  green (4/4)** including the `docker` job (two-file compose build from W2's
  context; all 15 phases) and `docker-published` explicit-skip (record
  absent).
- **No-image-change proof (required in the report):**
  `git diff --name-only dfa77fb442a82754bb6af21a2e0fb0af29ddfbab..W2`
  touches NO Docker build-context path (Dockerfile, .dockerignore,
  pyproject.toml, uv.lock, LICENSE, NOTICE, README.md, src/) and the exact
  file list is quoted; therefore the W2-built image is layer-identical to
  the S''-built image modulo the `org.opencontainers.image.revision` label.

### C6 — Publication at `W` (the round's deliverable)

- Pre-dispatch registry probe (anonymous): `0.1.0` → `absent`,
  `sha-<W>` → `absent` (record the outputs).
- `gh workflow run release-image.yml --ref <W>`; wait for a **SUCCESS**
  run; capture `D` (`sha256:<64-hex>`) from the run log/outputs and the
  workflow run id; then INDEPENDENTLY re-verify via anonymous
  `scripts/ghcr_tag_check.py`: `0.1.0` → `D` and `sha-<W>` → `D` (one
  digest for both tags).
- If the run FAILS at the push/login step with a permission/credential error
  despite the secret: do NOT re-dispatch; STOP and report the exact error
  (genuine human boundary per re-adjudication 3). If the run fails for a
  non-credential reason (transient infrastructure): ONE deterministic
  re-dispatch is permitted; a second failure → STOP and report.
- If a successful push leaves PARTIAL registry state (one tag written, the
  other not, or a mismatched digest), do NOT re-dispatch; STOP and report
  (orphan cleanup is a strategic act; no silent repoint).

### C7 — Release-record commit `P` (child of `W`)

EXACTLY two files changed:

1. `packaging/release_record.json` (schema `slaif-release-record-v1`, per
   the 013-a R1 field set): `git_tag = "v0.1.0"`;
   `image_source_commit = W`; `oci_image_digest = "sha256:" + D`;
   `oci_tags = ["0.1.0", "sha-<W>"]`; `published_at` = RFC 3339 UTC of the
   successful publication run; `publication_workflow_run_id` = the C6 run id;
   plus the remaining schema-required fields per the 013-a contract.
2. `packaging/release_provenance_manifest.json` → `M_P`: regenerated from W's
   tree with the record present (generator's published state):
   `objective "013-c"`; `oci.published = true`;
   `oci.image_digest = "sha256:" + D`; `status.released = true`;
   `release.git_tag_target = W`; `generated_from.git_commit = W`; artifact
   hashes unchanged from `M_W2`.

`P` changes NO other file (no build input, no docs, no workflows, no OAP
order/active/report bytes).

### C8 — CI at `P` and report `R`

- CI at P FULLY GREEN, including the **EXECUTED** `docker-published` job
  (its first-ever execution: pull by digest `D` and by both tags resolving to
  `D`; registry-API cross-check; OCI label set verified against the record
  and manifest — `org.opencontainers.image.revision == W`,
  `org.opencontainers.image.version == 0.1.0`,
  `slaif-local-coding.package.version == 0.1.0`,
  `slaif-local-coding.gateway.peer.sha == 08ca421…`,
  `slaif-local-coding.wheel.sha256 == H_new`,
  `slaif-local-coding.qualification == mvp-release-0.1.0`,
  `slaif-local-coding.topology.mode` unchanged; the PULL-BASED compose
  (primary file only, `SLAIF_LOCAL_CODING_IMAGE` digest-pinned) against the
  disposable fake upstream on canonical port 18031 — readiness healthy,
  representative signed request succeeds, negative contract cases fail
  closed, missing-secret readiness fail-closed; NO-BUILD proof; teardown
  absence proof).
  - **Narrow gate-defect exception:** the `docker-published` job has never
    executed. ONLY IF its first execution fails due to a defect in the gate
    itself (never-executed code), a MINIMAL fix to
    `.github/workflows/ci.yml` and/or
    `scripts/docker_qualification_ci.py` is authorized within this round as
    a documented deviation, provided it removes, skips, or weakens NO
    011/012/013 qualification semantics. Any other cause → report and stop
    (strategy decides a suffix round).
- `R` = report-only commit, child of `P` (first parent = `P`).

## Identity bindings (normative; 013-a ordering instantiated)

- `S` := `W` = W2 (image-source commit): built on the GitHub runner from
  exactly W's tree; OCI `org.opencontainers.image.revision == W`; registry
  tag `sha-<W>`.
- Git tag `v0.1.0` → target `W`; GitHub Release referencing that tag —
  BOTH are STRATEGIC post-merge acts, NOT part of this round.
- record/manifest `image_source_commit == W == M_P.generated_from.git_commit`.
- `oci_image_digest == D == digest(0.1.0) == digest(sha-<W>)`.
- in-image wheel SHA-256 == `H_new` == manifest `artifacts.wheel.sha256`.
- **NO image rebuild after `D` is recorded.**

## Explicit non-goals (all 013-a/013-b non-goals inherited, plus)

- NO protected-host mutation: Qwen/vLLM (port 18020), `qwen-serving*`
  units, model/checkpoint/patches/venv, active Codex profiles,
  firewall/VPN/network, systemd production state. NO docker build/run/up on
  the protected host (CI runner only). NO live cutover. NO
  protected-model/Qwen inference anywhere.
- NO Gateway-repository mutation (read-only verification only; peer remains
  `08ca421…`).
- NO Git tag and NO GitHub Release by coding (strategic post-merge acts).
- NO modification of the repository Actions workflow-permission ceiling or
  ANY other repository security setting, in any direction.
- NO creation of new credentials (the secret = the wrapper's existing PAT).
- NO changes to `src/`, `pyproject.toml`, `uv.lock`, `config/`, `Dockerfile`,
  `.dockerignore`, `compose.yaml`, `compose.build.yaml`, the
  docker-qualification harness, or `ci.yml` (except the narrow
  C8 gate-defect exception). NO version change (stays `0.1.0`).
- NO byte changes to the 013-a/013-b order or report files. NO
  documentation changes beyond C4.
- NO registry publication other than the two specified tags of the single
  image built at W. No other tags. No repoints.

## Required evidence (report)

- Literals: W1, W2 (= W), P, R; `D`; publication workflow run id; CI run ids
  at W1, W2, P, R; credential identity (identity only, never the value);
  the redacted `gh secret set` command.
- The 013-b B8 failure evidence re-cited (both run ids + exact error line)
  as the blocker this round resolves.
- Pre-dispatch registry probe (both tags `absent`) AND post-publication
  registry probe (both tags → `D`), anonymous, exact outputs.
- The no-image-change proof (C5): exact `git diff --name-only` file list
  `S''..W2` + the build-context-untouched assertion.
- The full 013-a R-criteria table re-affirmed at W/P under 013-c: R11
  satisfied as AMENDED by re-adjudication 3; R12 satisfied by the SUCCESSFUL
  dispatch at W (the 013-b BLOCKED precedent is retired); R13 EXECUTED at P;
  R5/R6–R10, R14–R20 re-stated with the round's evidence; R1 satisfied at P
  (record exists); R15/R16 re-stated (docs now also carry the C4 mechanism
  wording; all other B5 wording intact); R17 satisfied (manifest and docs
  agree in the published state at P).
- Protected-host before/after read-only probe table (B12 pattern; after-probe
  taken at report time).
- Local gate re-runs at W2: full pytest (expect the standing 26 skips), ruff
  check + format, mypy in the CI-equivalent environment, compileall,
  `uv build` (wheel == `H_new`; sdist == `M_W2` sdist hash),
  `artifact_policy_check` clean, manifest module suite (objective `013-c`),
  gateway-contract local re-run 18/18 at `08ca421…` with network guard
  enabled, `docker compose config` render-only (NO host docker run/build),
  `bash -n` on changed shell scripts (if any).
- Confirmations: PR #15 remains the single PR and MERGEABLE; no coding
  merge; no auto-merge; worktree residue untouched.

## Report contract

- Report path: `oap/reports/013-c-fix-registry-credential-and-complete-publication.md`
- The activated order file is committed verbatim in W1 with `oap/active` →
  `013-c` (013-b pattern).
- `R` changes only the report file; first parent = `P`.
- **If blocked at C6** (genuine human boundary): the report is
  BLOCKED-at-C6 with the exact error evidence; the report commit's first
  parent is the final non-report commit of the round; no `P`/`R` beyond the
  facts exist; the registry state (absent or partial) is stated exactly.

## Safety/scope (restated)

Raw secrets never enter reports, commits, or logs: the `gh secret set`
command is redacted in the report; the workflow never echoes the token
(GitHub masks secret references; the script must not print it); the CI fake
credentials follow the established 011 pattern (generated, 0600, never
printed). No host paths beyond established conventions. No protected-fixture
change. The standing 26 routine pytest skips remain as designed.

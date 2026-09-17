# OAP Work Order — 013-d: Correct the registry-failure diagnosis, restore the GITHUB_TOKEN publication mechanism, freeze the 0.1.0 Gateway compatibility authority, and complete the publication on PR #15

## Objective

Complete the human-authorized publication of MVP `0.1.0` to
`ghcr.io/ulfe-lmi/slaif-local-coding` (tags `0.1.0` and `sha-<W>`, one digest
`D`), on PR #15, under the CORRECTED credential mechanism (workflow
`GITHUB_TOKEN` with declared `packages: write`), after removing the 013-c
broad-PAT secret workaround and freezing the 0.1.0 Gateway compatibility
authority at `08ca421bee1ddca62078302b910e8be88cf705be`. This is a
skeptical strategic correction round: the 013-b/013-c diagnosis of the
registry failure is corrected below on primary evidence, and this order
supersedes 013-c's secret-based mechanism (re-adjudication 3) while
preserving 013-c's verified reference fix (C1 of 013-c).

## Diagnostic correction (normative record — supersedes the 013-b/013-c conclusion)

The 013-b report and the 013-c order recorded the conclusion that the
repository's `default_workflow_permissions = "read"` "clamps" the workflow's
declared `packages: write`, making GITHUB_TOKEN publication to GHCR
impossible. **That conclusion is wrong and is retracted on primary evidence:**

1. **The 013-b GITHUB_TOKEN DID have `packages: write`.** Raw logs of BOTH
   013-b dispatch runs, job `build-and-publish`, "Set up job" →
   `GITHUB_TOKEN Permissions`:
   - run `35208313536` (2026-09-17T10:01:55Z): `Contents: read` /
     `Metadata: read` / `Packages: write`
   - run `35209542430` (2026-09-17T10:15:43Z): `Contents: read` /
     `Metadata: read` / `Packages: write`
   (Strategy re-read both raw logs at 013-d order time.)
2. Therefore the repository setting `default_workflow_permissions` is the
   FALLBACK DEFAULT for workflows that declare no `permissions:` key — NOT a
   ceiling on declared permissions. No org-level restriction forced
   read-only for this workflow; the declared `permissions:` block was
   honored, as the same raw logs show.
3. **The 013-b push was a misdirected push, not a failed GHCR
   authorization.** The same raw logs show the publication script pushed the
   UNQUALIFIED reference `ulfe-lmi/slaif-local-coding:sha-dfa77fb…`.
   Unqualified references resolve against the default registry (docker.io)
   — strategy proved this from the host at 013-d order time (a controlled
   push probe printed `The push refers to repository
   [docker.io/ulfe-lmi/slaif-local-coding]` and was rejected, with or
   without a ghcr.io login present). The 013-b failure (a pre-transfer
   authorization error ~1 s after the push started, before any layer
   transfer) is therefore NOT evidence that a `packages: write` GITHUB_TOKEN
   cannot publish to GHCR. The exact error string it produced came from the
   misdirected push's pre-transfer auth stage and is attributed to no GHCR
   decision.
4. **The 013-c failure stands as a separate, valid fact:** the qualified
   `ghcr.io/…` push with the classic PAT (scopes `read:org, repo,
   workflow` — NO `write:packages`) failed at the registry operation layer
   with `denied: permission_denied: The token provided does not match
   expected scopes` (run `35215843816`). Current authoritative GitHub
   documentation (Container registry, "Authenticating to the Container
   registry") confirms the corrected picture:
   - for GitHub Actions workflows publishing the workflow repository's
     packages, the supported and recommended mechanism is the workflow
     `GITHUB_TOKEN` ("this registry supports granular permissions … we
     highly recommend you update your workflow to use the GITHUB_TOKEN");
   - for classic PATs, the required scope is `write:packages` (not the broad
     `repo` scope, which the docs explicitly call "unnecessary and broad …
     we recommend you avoid using for GitHub Actions workflows"); a
     `repo`-scoped classic PAT without `write:packages` does not authorize
     container-registry push;
   - fine-grained PATs are NOT a supported GHCR credential type ("GitHub
     Packages only supports authentication using a personal access token
     (classic)"), so the 013-c documentation's "dedicated fine-grained PAT"
     hardening advisory is itself incorrect and is corrected by C4.
5. **Consequence for this order:** the publication mechanism is the
   GITHUB_TOKEN design (the original 013-a R11 design, which the 013-c
   re-adjudication 3 had withdrawn), COMBINED with 013-c's verified fix of
   the fully qualified `ghcr.io/…` push references. The GITHUB_TOKEN
   mechanism with qualified references has NOT yet been tested end-to-end;
   the single controlled dispatch at C6 is that deterministic test. Do not
   classify a C6 failure as a human-policy blocker without primary evidence
   identifying the actual failing authorization layer.

## GitHub objective state

- Numeric objective: `013`; round: `013-d`; mode: `AMEND_EXISTING_PR`
- PR: **#15** — https://github.com/ulfe-lmi/slaif-local-coding/pull/15 — the
  single objective-013 PR; NO new PR, NO new numeric objective
- Branch: `oap/013-mvp-release-publication` (unchanged)
- Base: `main` @ `a04693e6792df6a8ad4262acfb46336a0f662202` (unchanged)
- Head at order time: `919eafbf2b4a1225079f3b5eda6f5e8d570790ad` (R, the
  013-c report commit; report-only, first parent `W2 =
  9c04669a4fcbb65267fc6cd19f0b8176ec33a5e2`)
- CI: green at W1 `3deb1fb…` (35215178452), W2 `9c04669…` (35215420037), and
  at R `919eafb…` (35216501136 — the `docker` job flake at R was re-run by
  strategy and the run is now fully success)

## Independently verified current state (strategy, at 013-d order time)

- **Registry clean:** anonymous probes → `0.1.0` `absent`;
  `sha-9c04669a4…` `absent`; `sha-dfa77fb…` `absent` (no package object;
  nothing to clean).
- **013-b primary evidence re-verified:** raw logs of runs 35208313536 and
  35209542430 show `Packages: write` in GITHUB_TOKEN Permissions (quoted
  above) and the unqualified push reference.
- **Host probes (strategy, read-only):** unqualified push resolves to
  `docker.io` (banner observed; anonymous rejection); a ghcr.io-logged-in
  replication of the runner state behaves identically; all probe artifacts
  cleaned (logout, probe tags removed, zero slaif images on the host, no
  stored ghcr credential).
- **Gateway drift (diagnosed, handled by the freeze rule below):** Gateway
  `main` advanced to `2b61312e0eb569aa7c6f953f52e35b44e84b91c1` (16 commits
  beyond the pinned `08ca421…`; changed files include
  `app/slaif_gateway/main.py`, `app/slaif_gateway/metrics.py`, both compose
  files, `pyproject.toml`, docs, verification material, and one
  `tests/unit/test_metrics_multiprocess.py`; NONE of the three Local
  contract files). Strategy verified the contract surface BLOB-IDENTICAL at
  `2b61312` vs `08ca421`:
  `app/slaif_gateway/modules/servers/local_coding/contract.py` =
  `9e8ae5ef8e1f9d8d48bf3627b9a767d86593a6ac`;
  `app/slaif_gateway/modules/clients/codex_0149.py` =
  `8976c984c4430d65b3d36bad8565062a8c6f955a`;
  `app/slaif_gateway/providers/streaming.py` =
  `73cc9f99e8c3cb2f3eb95173344bfbdc211c71ff` (all equal at both SHAs).
- **Credential facts:** wrapper PAT scopes `read:org, repo, workflow` (no
  `write:packages`); account `jpers1` is org ADMIN of `ulfe-lmi` and repo
  admin; the repo secret `SLAIF_GHCR_TOKEN` exists (created
  2026-09-17T11:27:42Z, value = the wrapper PAT — the 013-c workaround).
- **Protected-host baseline:** `qwen-serving-vision.service` active (vllm
  `pid=23961` on `0.0.0.0:18020`); 18031/18033/18034 closed; three
  pre-existing exited non-slaif containers;
  `~/.codex/qwen-neumann.config.toml` 858 B / 600 / 2026-09-13 11:59:21.
- **Documentation state:** the 013-c C4 wording (SLAIF_GHCR_TOKEN secret
  mechanism + incorrect fine-grained-PAT advisory + "not yet published …
  R18 hold" prose) exists at `docs/RELEASE-ARTIFACT-POLICY.md` (~L34-46,
  ~L198, ~L214-230) and `docs/DOCKER-INSTALL.md` (~L24, ~L326-335); the
  cutover runbook's `gateway.authority_sha` row (~L54) and the
  `TOPOLOGY`/`SLAIF-GATEWAY-INTEGRATION`/`IMPLEMENTATION-ROADMAP` pin
  history prose need the narrow freeze-rule reconciliation (C4). The
  fixture `tests/fixtures/gateway/current_peer_authority.json`
  (`"purpose": "current_ci_compatibility_authority"`, commit `08ca421…`)
  and `scripts/gateway_contract.py` (`PURPOSE =
  "current_ci_compatibility_authority"`) are the CI development-tracking
  pin and are NOT changed by this round.

## Gateway release-peer freeze rule (normative, effective for release 0.1.0)

- The **release compatibility authority** for Local 0.1.0 is FROZEN at
  Gateway `08ca421bee1ddca62078302b910e8be88cf705be`: the strict Local
  gateway-contract gate passed 18/18 at that pin (CI 35208071525 and the
  013-c local re-run, network guard enabled), the contract surface is
  blob-identical across all pins (`1fccaa74…`, `08ca421…`, `2b61312…` —
  `2b61312…` verified at 013-d order time), and the frozen value is already
  bound in `M_W2`/the Dockerfile ARG/label default and in the image built
  at the 013-d image-source head.
- The **CI fixture** (`current_peer_authority.json`,
  `purpose: current_ci_compatibility_authority`) is a development
  COMPATIBILITY-TRACKING pin: it may follow Gateway `main` through separate,
  deliberately re-qualified re-pin objectives (the 012-a precedent). That
  tracking does NOT change the frozen release authority, does NOT require
  any re-release or re-publication of 0.1.0, and no 013-d work re-pins it
  to `2b61312…`.
- This round's documentation (C4) states this distinction explicitly and
  narrows any wording that implies the release peer must perpetually equal
  Gateway `main`.

## Bounded scope (workstreams)

### C1 — Restore the GITHUB_TOKEN publication mechanism (unfreezes `.github/workflows/release-image.yml`)

From the W2 tree, change EXACTLY:
1. Header comment: the active publication path is `workflow_dispatch`-only;
   the registry credential is the workflow `GITHUB_TOKEN` with declared
   `contents: read` + `packages: write` (the documented mechanism for
   publishing the workflow repository's container package; no long-lived
   credential of any kind is referenced or introduced); a concise
   correction note (the 013-b "permission ceiling" diagnosis was
   retracted on primary log evidence — the run logs show the token was
   granted `Packages: write`; the 013-b failure was the unqualified push
   reference, fixed in 013-c C1; the 013-c secret workaround is withdrawn
   and its broad PAT secret is removed as release-security cleanup).
2. `permissions:` → `contents: read` AND `packages: write` (restored).
3. REMOVE the 013-c fail-fast secret step.
4. Login step: `echo "${{ secrets.GITHUB_TOKEN }}" | docker login ghcr.io
   -u "${{ github.repository_owner }}" --password-stdin` (the 013-b form).
5. Push step: `env: SLAIF_GHCR_TOKEN: ${{ secrets.GITHUB_TOKEN }}` (the
   013-b form; the env name is the publish script's token input for
   registry-API verification — the script itself is unchanged behaviorally).
All other steps byte-identical (wheel-binding assert, two-file compose
build with `SLAIF_GIT_SHA`/`SLAIF_WHEEL_SHA256`/`SLAIF_QUALIFICATION_LABEL`,
publish-script invocation). The workflow remains `workflow_dispatch`-only;
the qualified `ghcr.io/…` push references come from the 013-c C1 script
(which is NOT changed by this round). No `SLAIF_GHCR_TOKEN` repository
secret reference may remain anywhere in the workflow.

### C2 — Script docstring correction (unfreezes `scripts/release_registry_publish.py`, docstring ONLY)

The module docstring's credential line currently describes the 013-c
repository-secret mechanism; correct it to: the registry credential is the
workflow `GITHUB_TOKEN` (declared `packages: write`), passed to the script
via the `SLAIF_GHCR_TOKEN` environment variable, and never printed. NO
behavioral change (the qualified-reference logic, no-silent-repoint guard,
digest capture, registry verification, and output contract remain
byte-for-byte as in W2).

### C3 — Remove the broad PAT secret (release-security cleanup)

- After W4's CI is fully green and BEFORE the C6 dispatch:
  `gh secret remove SLAIF_GHCR_TOKEN --repo ulfe-lmi/slaif-local-coding`;
  verify with `gh secret list` (the name is gone).
- Report records the removal (name + timestamp only; the value is never
  recorded). The wrapper's own PAT (its `gh` auth) is untouched; no other
  secret is touched; NO repository Actions/security setting is modified.
- Rationale: with the GITHUB_TOKEN mechanism, the repository must not retain
  an unnecessary broad `repo`/`workflow`-scoped PAT (the 013-c workaround
  credential).

### C4 — Documentation reconciliation (exact sites)

1. `docs/RELEASE-ARTIFACT-POLICY.md` (~L34-46 and ~L214-230): replace the
   SLAIF_GHCR_TOKEN-secret mechanism wording with the GITHUB_TOKEN
   mechanism (dispatch-only workflow; declared `packages: write`; no
   long-lived credential; cite the current GitHub Container-registry
   authentication guidance). For human/CLI (non-workflow) use, state the
   CORRECT documented option: a classic PAT with at least `write:packages`
   scope (explicitly NOT the broad `repo` scope; enable org SSO if the org
   requires it), and state that fine-grained PATs are not a supported GHCR
   credential type. Remove the 013-c "dedicated fine-grained PAT" hardening
   advisory (unsupported). The ceiling-rejection prose is replaced by the
   correction record (the "ceiling" diagnosis was wrong; no repository
   security setting was ever changed).
2. `docs/RELEASE-ARTIFACT-POLICY.md` (~L198): replace "NOT yet published as
   of this PR's head (publication pending the R18 Gateway-peer hold …)"
   with the 013-d truth: publication is the `workflow_dispatch`-only
   release workflow executed at the final implementation head of this PR
   (order 013-d); the digest `D`, tags, and image source commit `S` are
   recorded in `packaging/release_record.json` (present from the
   release-record commit onward) and the schema-v3 manifest; keep the
   path-only reference discipline (no literal digest in any document).
3. `docs/DOCKER-INSTALL.md` (~L326-335): same GITHUB_TOKEN mechanism
   reconciliation; (~L24): the "re-qualified to the current peer" history
   statement is kept as history but aligned with the freeze rule (the 0.1.0
   release peer is frozen at `08ca421…`; see the RELEASE-ARTIFACT-POLICY
   compatibility-authority section).
4. **Gateway compatibility authority (frozen for 0.1.0)** — add ONE
   authoritative section in `docs/RELEASE-ARTIFACT-POLICY.md` (next to the
   publication section) stating: the 0.1.0 release compatibility authority
   is frozen at Gateway `08ca421bee1ddca62078302b910e8be88cf705be`;
   evidence: strict 18/18 contract gate at that pin, contract surface
   blob-identical across pins (`1fccaa74…`, `08ca421…`, `2b61312…` — the
   16-commit drift to `2b61312…` on 2026-09-17 changes no contract file);
   the CI fixture (`purpose: current_ci_compatibility_authority`) is
   development tracking that may follow Gateway main via separate
   re-qualified objectives; CI tracking never changes the frozen release
   authority or invalidates 0.1.0.
5. `docs/RELEASE-CUTOVER-RUNBOOK.md` (~L54, the
   `gateway.authority_sha` row): the cutover authority is the FROZEN 0.1.0
   release compatibility authority `08ca421…` (pointer to item 4); the
   parenthetical "current pinned peer, re-pinned by Objective 013-b" is
   reworded as history + pointer. In `docs/TOPOLOGY.md`,
   `docs/SLAIF-GATEWAY-INTEGRATION.md`, and `docs/IMPLEMENTATION-ROADMAP.md`,
   make the MINIMAL pointer additions (one line each, where the pin prose
   could be misread as perpetual main-tracking) to the item-4 section; the
   historical 013-b re-pin statements remain as history.
No other documentation changes; the B5 released-truth discipline (path-only
digest references; tag/Release as strategy post-merge acts; no
production-ready claims) stays intact and must be true at this round's
completion.

### C5 — Commit sequence and final implementation head `W`

- **W3** (child of `919eafb…`): C1 + C2 + the activated 013-d order file
  (`oap/orders/013-d-corrected-credential-publication-and-peer-freeze.md`,
  strategic-authored bytes committed verbatim) + `oap/active` → `013-d`.
  No sdist-input changes (the workflow file and `scripts/` are not sdist
  inputs; `oap/` is excluded) → the committed manifest
  (`objective "013-c"`, wheel `879baa3ad19e0f513090add965d267957d27f7bcd904d1e225586d76126f8b19`,
  sdist `8e0298f0ba10b2f633bace7d9369cdb866960d65921493ffc0db613944efbd6e`,
  peer `08ca421…`) stays consistent with W3's tree. **CI at W3 MUST be
  fully green (4/4).**
- **W4** (child of W3): C4 + the generator/test objective bump
  (`scripts/release_provenance_manifest.py` `OBJECTIVE` → `"013-d"` +
  docstring; `tests/test_release_provenance_manifest.py` E3 → `"013-d"`) +
  the manifest-regeneration commit producing `M_W4`: `objective "013-d"`;
  not-yet-published state (`oci.published: false`, `oci.image_digest: null`,
  no `release` key, `status` per the not-yet-published schema);
  `gateway_peer.commit = 08ca421…` (FROZEN release authority — unchanged);
  `artifacts.wheel.sha256 = oci.wheel_sha256 = 879baa3ad19e0f513090add965d267957d27f7bcd904d1e225586d76126f8b19`
  (unchanged; README/src untouched); `artifacts.sdist.sha256` = the NEW sdist
  hash (docs changed; must equal a fresh `uv build` at W4);
  `generated_from.git_commit = W3`.
- **`W := W4`** is the image-source head. **CI at W4 MUST be fully green
  (4/4).** No-image-change proof (required in the report):
  `git diff --name-only 9c04669a4fcbb65267fc6cd19f0b8176ec33a5e2..W4`
  touches NO Docker build-context path (Dockerfile, .dockerignore,
  pyproject.toml, uv.lock, LICENSE, NOTICE, README.md, src/); the image
  built at W4 is layer-identical to the W2-built image modulo the
  `org.opencontainers.image.revision` label.

### C6 — The ONE controlled publication at `W`, with layer classification

- Pre-dispatch anonymous registry probe: `0.1.0` → `absent`; `sha-<W>` →
  `absent` (record outputs).
- EXACTLY ONE dispatch: `gh workflow run release-image.yml --ref
  oap/013-mvp-release-publication` (branch tip = W at dispatch time).
- Classify and report EACH layer separately (do not collapse them):
  1. workflow start + checkout;
  2. wheel-binding assert (fresh wheel == manifest `H_new`);
  3. image build (two-file compose, `mvp-release-0.1.0` label);
  4. GHCR authentication success (login with GITHUB_TOKEN);
  5. GHCR authorization + image upload success (all layers + config
     pushed; no scope/permission denial);
  6. in-script registry verification: BOTH tags `0.1.0` and `sha-<W>`
     resolve to ONE digest `D` (no-silent-repoint guard respected);
  7. **package visibility / anonymous pullability:** the first push
     creates the package; its default visibility is private. The INTENDED
     semantics for this public repository's pull-based MVP (the 013-a
     design, the anonymous CI pull in the `docker-published` job, the
     documented anonymous probes) is a PUBLICLY pullable package. After the
     push, verify anonymous resolution of BOTH tags via
     `scripts/ghcr_tag_check.py` (no token in the environment). If a tag is
     NOT anonymously resolvable (package private by default), set the
     package visibility to public using the wrapper's org-admin authority
     (org `ulfe-lmi` package visibility API for the
     `container`-type package `slaif-local-coding`; if the API route is
     not available with the current credential, STOP and report — the
     visibility change then becomes a human UI act) and re-verify anonymous
     resolution of BOTH tags. Report records the visibility state change
     exactly.
  8. capture `D` (`sha256:<64-hex>`) from the run and the workflow run id;
     then INDEPENDENT anonymous re-verification: `0.1.0` → `D` and
     `sha-<W>` → `D`.
- Failure law: if the run FAILS, report the exact failing layer with the
  raw log lines; do NOT re-dispatch for an authorization/permission-class
  failure (strategy re-adjudicates with the primary evidence — a genuine
  org policy boundary would then be a human decision with ONE precise
  choice); ONE deterministic re-dispatch is permitted ONLY for a
  transient-infrastructure failure (e.g., runner error before any registry
  interaction); a second failure of any kind → STOP and report. Partial
  registry state (tag written, verification failed) → STOP and report
  (orphan cleanup is a strategic act; no silent repoint).

### C7 — Release-record commit `P` (child of `W`)

EXACTLY two files changed:
1. `packaging/release_record.json` (schema `slaif-release-record-v1`, per
   the 013-a R1 field set): `git_tag = "v0.1.0"`;
   `image_source_commit = W`; `oci_image_digest = "sha256:" + D`;
   `oci_tags = ["0.1.0", "sha-<W>"]`; `published_at` = RFC 3339 UTC of the
   successful publication run; `publication_workflow_run_id` = the C6 run
   id; plus the remaining schema-required fields per the 013-a contract.
2. `packaging/release_provenance_manifest.json` → `M_P`: regenerated from W's
   tree with the record present (generator's published state):
   `objective "013-d"`; `oci.published = true`;
   `oci.image_digest = "sha256:" + D`; `status.released = true`;
   `release.git_tag_target = W`; `generated_from.git_commit = W`;
   `gateway_peer.commit = 08ca421…`; artifact hashes unchanged from `M_W4`.
`P` changes NO other file.

### C8 — CI at `P` (including the FIRST EXECUTED `docker-published`) and report `R`

- CI at P FULLY GREEN, including the **EXECUTED** `docker-published` job
  (its first-ever execution — a green pre-publication CI where
  `docker-published` follows the explicit not-yet-published skip path is
  NOT release evidence; this execution against the real registry image is
  the release evidence): pull by digest `D` and by both tags (anonymous —
  this also mechanically proves the C6 visibility semantics), each
  resolving to `D`; registry-API cross-check; OCI label set verified
  against the record/manifest (revision == W; version `0.1.0`;
  `slaif-local-coding.gateway.peer.sha == 08ca421…`; wheel == `H_new`;
  qualification `mvp-release-0.1.0`; topology unchanged); the PULL-BASED
  compose (primary file only, `SLAIF_LOCAL_CODING_IMAGE` digest-pinned,
  NO `build` key) against the disposable fake upstream on canonical port
  18031: readiness healthy; representative signed request succeeds;
  negative contract cases fail closed; missing-secret readiness fail-closed;
  NO-BUILD proof (image exists locally only via pull; running container
  image ID == pulled image ID); teardown absence proof.
  - **Narrow gate-defect exception (inherited from 013-c C8):** ONLY IF the
    first execution fails due to a defect in the never-executed gate
    itself, a MINIMAL fix to `.github/workflows/ci.yml` and/or
    `scripts/docker_qualification_ci.py` is authorized within this round as
    a documented deviation, provided it removes, skips, or weakens NO
    011/012/013 qualification semantics. Any other cause → report and stop.
- `R` = report-only commit, child of `P` (first parent = `P`).

## Identity bindings (normative; 013-a ordering instantiated)

- `S` := `W` = W4 (image-source commit): built on the GitHub runner from
  exactly W's tree; OCI `org.opencontainers.image.revision == W`; registry
  tag `sha-<W>`.
- Git tag `v0.1.0` → target `W`; GitHub Release referencing that tag —
  BOTH are STRATEGIC post-merge acts, NOT part of this round.
- record/manifest `image_source_commit == W == M_P.generated_from.git_commit`.
- `oci_image_digest == D == digest(0.1.0) == digest(sha-<W>)`.
- in-image wheel SHA-256 == `H_new` == manifest `artifacts.wheel.sha256`.
- Frozen release peer: `gateway_peer.commit == 08ca421…` in `M_W4` and
  `M_P`, the Dockerfile ARG default, and the in-image label.
- **NO image rebuild after `D` is recorded.**

## Explicit non-goals (all 013-a/013-b/013-c non-goals inherited, plus)

- NO re-pin of the CI fixture or the release peer to `2b61312…` (or any
  other Gateway main revision): the release authority is FROZEN at
  `08ca421…` per the freeze rule; CI tracking pin changes belong to a
  separate future objective if ever warranted.
- NO Gateway-repository mutation (read-only verification only).
- NO protected-host mutation (Qwen/vLLM 18020, qwen-serving units,
  model/checkpoint/patches/venv, Codex profiles, firewall/VPN/network,
  systemd production state); NO docker build/run/up on the protected host
  (CI runner only); NO live cutover; NO protected-model/Qwen inference
  anywhere.
- NO Git tag and NO GitHub Release by coding (strategic post-merge acts).
- NO modification of any repository Actions/security setting, in any
  direction (the `default_workflow_permissions` setting is NOT touched by
  this round; the correction record explains why no change is needed).
- NO creation of new credentials; the ONLY credential acts are: use of the
  workflow GITHUB_TOKEN (already issued per run) and REMOVAL of the
  `SLAIF_GHCR_TOKEN` secret (C3) plus the C6 package-visibility act
  (org-admin, documented).
- NO changes to `src/`, `pyproject.toml`, `uv.lock`, `config/`,
  `Dockerfile`, `.dockerignore`, `compose.yaml`, `compose.build.yaml`, the
  docker-qualification harness, or `ci.yml` (except the narrow C8
  gate-defect exception); NO behavioral change to
  `scripts/release_registry_publish.py` (C2 is docstring-only); NO version
  change (stays `0.1.0`).
- NO byte changes to the 013-a/013-b/013-c order or report files. NO
  documentation changes beyond C4.
- NO registry publication other than the two specified tags of the single
  image built at W. No other tags. No repoints.

## Required evidence (report)

- The diagnostic-correction record: both 013-b run ids with the exact
  `GITHUB_TOKEN Permissions` log lines; the unqualified push reference
  line; the strategy host probe evidence (docker.io resolution banner);
  the 013-c run id + exact push error; the documentation citations
  (GITHUB_TOKEN recommendation; `write:packages` vs `repo`; fine-grained
  not supported).
- Literals: W3, W4 (= W), P, R; `D`; publication workflow run id; CI run
  ids at W3, W4, P, R; the secret-removal name + timestamp; the package
  visibility state (before/after, and the exact act taken, if any).
- The C6 layer classification (all eight layers, with raw log evidence for
  each).
- Pre-dispatch and post-publication anonymous registry probes (exact
  outputs: pre = both `absent`; post = both → `D`, anonymously).
- The no-image-change proof (C5): exact `git diff --name-only
  9c04669a4…..W4` file list + the build-context-untouched assertion.
- The gateway freeze record: the 16-commit compare summary (changed file
  set), the three contract blob SHAs at `08ca421…` AND `2b61312…`
  (blob-identical), and the strict contract-gate result at the frozen peer
  (18/18 at `08ca421…`, network guard enabled — cite the CI run and, if
  re-run locally this round, the local JSON result).
- The full 013-a R-criteria table re-affirmed at W/P under 013-d: R1
  satisfied at P; R5–R10, R14–R20 re-stated with this round's evidence;
  R11 satisfied as the CORRECTED mechanism (GITHUB_TOKEN + qualified refs,
  per the diagnostic correction); R12 satisfied by the SUCCESSFUL single
  dispatch at W; R13 EXECUTED at P (the executed published-image gate is
  the release evidence — a skip is not); R15/R16 satisfied by the C4
  wording (GITHUB_TOKEN mechanism + freeze rule; all B5 discipline intact);
  R17 satisfied (docs and machine manifest agree at P).
- Protected-host before/after read-only probe table (B12 pattern;
  after-probe at report time).
- Local gate re-runs at W4: full pytest, ruff check + format, mypy
  (CI-equivalent environment), compileall, `uv build` (wheel == `H_new`;
  sdist == `M_W4` sdist hash), `artifact_policy_check` clean, manifest
  module suite (objective `013-d`), gateway-contract local re-run 18/18 at
  `08ca421…` (network guard enabled), `docker compose config` render-only
  (NO host docker build/run), `bash -n` on changed shell scripts (if any),
  and a grep proof that NO `SLAIF_GHCR_TOKEN` repository-secret reference
  remains in the workflow (the env-variable name in the publish script and
  its GITHUB_TOKEN-sourced workflow env are expected and fine; a
  `secrets.SLAIF_GHCR_TOKEN` expression must be absent from the repo).
- Confirmations: PR #15 remains the single PR and MERGEABLE; no coding
  merge; no auto-merge; worktree residue untouched.

## Report contract

- Report path: `oap/reports/013-d-corrected-credential-publication-and-peer-freeze.md`
- The activated order file is committed verbatim in W3 with `oap/active` →
  `013-d` (established pattern).
- `R` changes only the report file; first parent = `P`.
- **If blocked at C6** (any failure class): the report is
  BLOCKED-at-C6 with the exact failing layer + raw log evidence; the
  report commit's first parent is the final non-report commit of the round;
  no `P`/`R` beyond the facts exist; the registry state (absent or
  partial) is stated exactly; the `SLAIF_GHCR_TOKEN` secret state is
  stated exactly (removed or not).

## Safety/scope (restated)

Raw secrets never enter reports, commits, or logs (the removed secret's
value is never recorded; the workflow masks `secrets.GITHUB_TOKEN`
references; the script must not print the token). No host paths beyond
established conventions. No protected-fixture change. The standing routine
pytest skips remain as designed.

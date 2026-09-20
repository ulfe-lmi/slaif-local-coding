# OAP Work Order — 013-a: Publish MVP 0.1.0 to GHCR, make the pull-based Docker install canonical, and close release provenance

## Objective

Turn the Docker-qualified MVP release candidate (Objectives 011/012, merged and
verified) into an actually consumable, immutable MVP release, without any
protected-host mutation:

1. Publish the exact reviewed runtime image to
   `ghcr.io/ulfe-lmi/slaif-local-coding` with tags `0.1.0` and `sha-<S>`
   (both resolving to one registry digest `D`), built on a GitHub runner from
   this round's final implementation commit `S` via the activated
   `.github/workflows/release-image.yml` (workflow_dispatch-only; GITHUB_TOKEN
   only).
2. Make the pull-based path the canonical operator installation (no local
   Docker build, no Python/uv/venv on the install host) while preserving the
   qualified `network_mode: host` / loopback-hop topology law (D1) and the
   Objective-011 container hardening surface unchanged.
3. Close release provenance mechanically: a committed release record plus a
   schema-v3 provenance manifest binding `S` (image source commit, git-tag
   target, OCI revision label), `D` (OCI digest), the release tags, the
   byte-identical wheel, and the pinned Gateway peer — with regeneration and
   cross-consistency gates that fail on any drift.
4. Prove the published-image path in CI (pull by digest and by tag, digest and
   OCI-label verification, full signed-ingress contract run against a
   disposable fake upstream, no-build proof, teardown absence proof) without
   weakening any Objective-011/012 gate.
5. Reconcile all release-facing current documentation from
   "release candidate / not released / build locally" to the exact
   post-publication truth.

The Git tag `v0.1.0` and the GitHub Release are STRATEGIC post-merge acts
(coding never creates either). Their exact semantics are fixed below so that
image, digest, tag, and manifest claims are non-circular and mechanically
checkable.

## GitHub objective state

- Repository: `ulfe-lmi/slaif-local-coding`
- Numeric objective: `013`; round: `013-a`
- PR mode: `CREATE_NEW_PR`
- Base: `main` @ `a04693e6792df6a8ad4262acfb46336a0f662202`
  (merge of PR #14, Objective 012)
- Existing PR: N/A (verified at order time: zero open PRs)
- Branch (required, new): `oap/013-mvp-release-publication`
- Current verified SHA: base head `a04693e6792df6a8ad4262acfb46336a0f662202`
- Verified at order time (strategic, independent `gh`/remote queries,
  2026-09-17):
  - Remote `main` = `a04693e6792df6a8ad4262acfb46336a0f662202`; CI run
    `35185192529` on that commit: `test`, `gateway-contract`, `docker` all
    SUCCESS.
  - Zero Git tags; zero GitHub releases; repository is PUBLIC
    (`private: false`), so anonymous GHCR pull is available to released users
    and to CI.
  - Gateway `main` = `1fccaa746df6cd44f1ddf8c2ec5cf6ea9f18b1cb`
    (2026-09-17T00:44:17Z) — identical to the pinned local peer fixture
    (`tests/fixtures/gateway/current_peer_authority.json`); no re-pin needed.
  - No `013` orders, drafts, branches, or PRs exist anywhere.
  - Accepted authority artifacts (post-012, supersede all older records):
    wheel `slaif_local_coding-0.1.0-py3-none-any.whl`
    `fceadc378130dd4ffcc3f75d17b5e098577652914f541245d31247911be23aeb`
    (83,097 B); sdist
    `72de29c9e60a012425e1c0d0d351ce7ff9c985b1f3b28c3525987a4f70db1c12`
    (425,885 B, developer-only); manifest v2
    `packaging/release_provenance_manifest.json` (objective `012-c`,
    `generated_from.git_commit` `69e08213eed97bcaa4baea158999e3af0922ab92`,
    `oci.image_digest` null, `oci.published` false, `status.released` false).
  - Current Docker surface: `Dockerfile` (digest-pinned bases; non-root
    uid/gid 10001; OCI + project labels; the
    `slaif-local-coding.qualification` label is HARDCODED to
    `disposable-qualification-only; not released`); `compose.yaml`
    (image `slaif-local-coding:0.1.0-${SLAIF_GIT_SHA:-local}` + `build:
    context: .`; host networking; read-only rootfs; no-new-privileges;
    cap_drop ALL; bounded tmpfs; single read-only config volume; env_file;
    `/readyz` healthcheck; restart unless-stopped);
    `.github/workflows/release-image.yml` (INERT: workflow_dispatch-only,
    `packages: write` declared, no push step, no credentials);
    `.github/workflows/ci.yml` (`test`, `gateway-contract`, `docker` jobs;
    the docker job drives `scripts/docker_qualification_ci.py`, which invokes
    bare `docker compose` in the repo root).
  - gh credential available to the coding loop (same host): account with
    `repo` + `workflow` scopes — `gh workflow run` on this repository is
    possible.

## Human authorization (explicit)

The human owner explicitly authorized the MVP release/tag/GHCR publication as
this bounded OAP objective ("I authorize the MVP release/tag/GHCR publication
as the next human-authorized act"). The protected-host cutover is NOT
authorized and remains a separate later human-authorized act. Nothing in this
order authorizes any protected-host mutation, any live cutover, any Gateway
deployment mutation, any Codex profile mutation, or any firewall/VPN/network
mutation.

## Strategic context and independently verified current state

Objectives 011 (PR #13, merge `e860e0b…`) and 012 (PR #14, merge
`a04693e…`) delivered a Docker-qualified, documentation-reconciled MVP
RELEASE CANDIDATE: digest-pinned host-network Compose deployment with the
full signed-ingress contract, D1 LAN-visible binding law, hardening surface,
CI qualification, and a regeneration-gated provenance manifest. Ladder state:
deployment-qualified (disposable/CI environments only) — NOT
release-qualified — NOT released; cutover NOT performed.

Independent inspection this session established the exact gaps between "RC"
and a consumable release:

1. **No image exists in any registry.** The publication workflow is inert by
   design (no push, no credential). The only way to obtain the software as a
   container today is to clone the repository and build locally.
2. **The canonical operator path is build-from-source.** `compose.yaml`
   carries `build: context: .`, and `docs/DOCKER-INSTALL.md` starts from
   cloning + `docker compose build`. A fresh host must run the full build
   chain. The human release decision requires the released-user path to be a
   pull-based installation with no local build and no Python/uv/venv.
3. **Provenance cannot express a published state.** Schema v2 const-asserts
   `oci.published: false` / `image_digest: null` / `status.released: false`;
   the generator hardcodes `objective = "012-c"`, the qualification label,
   the "not released / OCI image not published" limitations, and the
   reserved-reference tag convention. There is no committed record binding a
   published digest to an image-source commit.
4. **The image qualification label is hardcoded** in the Dockerfile, so a
   published image cannot carry a truthful release label without a runtime
   change (and any runtime change would break the byte-identity law of the
   accepted wheel — it must not).
5. **Release-facing documentation** (README, roadmap current-state,
   COMPLETENESS, DEPLOYMENT, TOPOLOGY, RELEASE-CUTOVER-RUNBOOK,
   RELEASE-ARTIFACT-POLICY, DOCKER-INSTALL, ARCHITECTURE) still states
   "NOT released / no registry publication / inert workflow / build locally".

This objective is the publication closure. It does NOT change runtime
behavior: the wheel, the adapter code, the contract implementation, the
templates, and the topology law are all frozen.

## Publication/provenance ordering (normative — no circular claims)

Definitions (literal values recorded in the report):

- `S` := the FINAL IMPLEMENTATION HEAD of this round (40-hex). Its tree
  contains the final Dockerfile, both compose files, the activated release
  workflow, CI, generator, schema, tests, and reconciled documentation, plus
  manifest `M_S` (regenerated; not-yet-published state;
  `generated_from.git_commit` = S's parent). `S`'s tree does NOT contain the
  release record. The release image is built from exactly `S`.
- `D` := the registry digest (`sha256:<64-hex>`) of the published image.
  Tags `0.1.0` and `sha-<S>` must both resolve to `D`, verified against the
  GHCR registry API inside the workflow run and recorded.
- `P` := the RELEASE-RECORD COMMIT, a child of `S`. `P` changes EXACTLY two
  files: adds `packaging/release_record.json` and regenerates
  `packaging/release_provenance_manifest.json` (`M_P`) from `S`'s tree with
  the record present (`M_P.generated_from.git_commit` = `S`). `P` must not
  change any build input (Dockerfile, compose files, .dockerignore, src/,
  pyproject.toml, uv.lock, config templates, tests, docs, workflows) or any
  OAP order/active/report.
- `R` := the report commit, a child of `P`, changing only the report file.
- Git tag `v0.1.0` (created by STRATEGY after merge and independent
  verification) targets `S`. The GitHub Release references that tag.
- Identity bindings (each mechanically tested in-repo and re-verified by
  strategy against the registry/remote):
  - OCI label `org.opencontainers.image.revision` == `S`
  - release record / manifest `image_source_commit` == `S` ==
    `M_P.generated_from.git_commit`
  - git tag `v0.1.0` target == `S` (strategy-verified post-merge)
  - record / manifest `oci_image_digest` == `D` == digest of registry tag
    `0.1.0` == digest of registry tag `sha-<S>`
  - in-image wheel SHA-256 == manifest `artifacts.wheel.sha256` ==
    `fceadc378130dd4ffcc3f75d17b5e098577652914f541245d31247911be23aeb`
    (byte-identical runtime)
- **No image rebuild after `D` is recorded.** If this round fails and is
  redone, previously published tags/images are orphans and MUST be deleted
  from GHCR before any fresh publication (orphan cleanup is in scope for
  strategy; a re-run publication requires a fresh round and fresh digest
  capture).

## Bounded scope (workstreams)

- **A. Release record + provenance v3** — `packaging/release_record.json`
  (exists only in `P`'s tree),
  `packaging/release_provenance_manifest.schema.json` (v3),
  `scripts/release_provenance_manifest.py` (state-aware generator),
  `packaging/release_provenance_manifest.json` (`M_S` in `S`'s tree; `M_P` in
  `P`'s tree), `tests/test_release_provenance_manifest.py` (state-conditional
  gates + new cross-consistency tests).
- **B. Dockerfile label parameterization** — `Dockerfile` only.
- **C. Compose split + qualification update** — `compose.yaml` (pull-based
  canonical), `compose.build.yaml` (new qualification override),
  `scripts/docker_qualification_ci.py` (two-file compose; published-image
  mode).
- **D. Release workflow activation** — `.github/workflows/release-image.yml`.
- **E. CI published-image gate** — `.github/workflows/ci.yml` (new
  `docker-published` job, gated on the release record).
- **F. Documentation reconciliation** — `docs/DOCKER-INSTALL.md` (primary
  restructure), plus corrections in: `README.md`,
  `docs/IMPLEMENTATION-ROADMAP.md`, `oap/COMPLETENESS.md`,
  `docs/DEPLOYMENT.md`, `docs/TOPOLOGY.md`, `docs/RELEASE-CUTOVER-RUNBOOK.md`,
  `docs/RELEASE-ARTIFACT-POLICY.md`, `ARCHITECTURE.md`, and
  `docs/DOCKER-SECURITY-DELTA.md` (only where a stale current-state statement
  is identified). Historical OAP orders/reports and all 009–012 records stay
  byte-identical.

## Explicit non-goals

- NO protected-host mutation of any kind: no Qwen/vLLM stop/restart/rebind,
  no port-18020 change, no model/checkpoint/venv/patch/unit change, no API-key
  file change, no firewall/VPN/network binding change, no Codex profile
  change, no Gateway route/deployment mutation.
- NO docker build/run/up/recreate on the protected host during this objective.
  ALL Docker evidence comes from GitHub CI (runner) and the workflow run.
  Only read-only `docker ps`-class inspection is permitted on the host for
  invariance proof. The host ports 18031/18033/18034 must remain closed
  before/after.
- NO Git tag creation and NO GitHub Release creation by coding (strategic
  post-merge acts).
- NO version bump (version stays `0.1.0`); NO changes to `src/`,
  `pyproject.toml`, or `uv.lock` — the wheel MUST remain byte-identical
  (`fceadc37…`). NO new dependencies (dependency freeze stands).
- NO `slaif-api-gateway` repository change; NO change to the accepted
  Gateway/Codex protocol or contract implementation; NO re-pin unless the
  peer delta check (R18) blocks.
- NO systemd-path changes; NO PyPI or other-registry publication; NO sdist
  publication; NO change to the D1 binding law, the canonical port 18031,
  the compose `name`, or the topology.
- NO broad refactors: `scripts/docker_qualification_ci.py` changes only as
  required by the compose split and the published-image mode. NO OAP
  machinery expansion (no new canary/protocol/role/evidence transport).
- NO protected-model inference anywhere in this objective; fake/synthetic
  upstreams only.

## Acceptance criteria

### A — Release record and provenance v3

- **R1.** `packaging/release_record.json` exists ONLY in `P`'s tree (absent
  from `S`'s tree). Schema `slaif-release-record-v1`, closed key set,
  exactly these fields: `schema` = `slaif-release-record-v1`; `version` =
  `0.1.0`; `git_tag` = `v0.1.0`; `image_source_commit` = `S` (40-hex);
  `oci_image_reference` = `ghcr.io/ulfe-lmi/slaif-local-coding`;
  `oci_image_digest` = `sha256:D`; `oci_tags` = `["0.1.0", "sha-<S>"]`;
  `published_at` (RFC 3339 UTC); `publication_workflow` =
  `release-image.yml`; `publication_workflow_run_id` (integer, or null if
  unrecoverable). No other keys; no host paths, URLs beyond the fixed
  repository/registry references, or any secret-like content.
- **R2.** Schema file becomes `slaif-release-provenance-v3`
  (`$id` + `schema_version` 3): top-level key set remains closed with
  `release` added as OPTIONAL (present iff the release record exists);
  `status.released` becomes enum `[false, true]`; `oci.published` enum
  `[false, true]`; `oci.image_digest` = null or `sha256:<64-hex>`; the
  `release` object is a closed key set: `version`, `git_tag`,
  `git_tag_target`, `image_source_commit`, `oci_image_digest`, `oci_tags`,
  `published_at`, `publication_workflow_run_id`. `additionalProperties:
  false` preserved throughout.
- **R3.** Generator becomes state-aware: when
  `packaging/release_record.json` is present it loads it and emits
  `release` (`git_tag_target` := `image_source_commit`), `status.released =
  true`, `oci.published = true`, `oci.image_digest` = `D`, and
  `oci.labels["slaif-local-coding.qualification"]` = `mvp-release-0.1.0`;
  otherwise it emits the not-yet-published state (null/false/false) with the
  same qualification label as today. In BOTH states the generator's
  `objective` constant records `013-a` (the producing round). In the
  PUBLISHED state, `limitations` replaces exactly the two bullets "not
  released; no registry publication, tag, or release state change" and "OCI
  image not published (oci.image_digest null, oci.published false); the
  container publication path is documented (workflow_dispatch-only, inert)
  and not executed" with truthful published-state bullets recording the
  digest `D`, the tags, the image-source commit `S`, and that publication is
  registry-only (no protected-host cutover, no real deployment yet
  evidenced); ALL other limitation bullets are preserved verbatim. In the
  published state, `oci.tag_convention` states: published reference
  `ghcr.io/ulfe-lmi/slaif-local-coding` tags `0.1.0` + `sha-<full
  image-source SHA>` (digest recorded in this manifest); local qualification
  tags `slaif-local-coding:0.1.0-<sha>` via `compose.build.yaml`. The
  not-yet-published state keeps the reserved-reference wording.
- **R4.** The E3 regeneration/drift gate (existing) is extended to be
  state-conditional (regenerate from the current tree, strip
  `generated_from.git_commit`, compare; ancestor rule unchanged) and NEW
  cross-consistency tests are added (stdlib only, no new dependencies):
  (a) when the record exists: `release.image_source_commit` == record value
  == `generated_from.git_commit`, and it is an ancestor of HEAD; (b) when the
  record exists: for each of `Dockerfile`, `compose.yaml`,
  `compose.build.yaml`, `.dockerignore`, the Git blob at
  `image_source_commit` equals the blob at HEAD (proves no build-input
  change between `S` and the manifest commit, i.e. the recorded image really
  corresponds to the recorded manifest's build inputs); (c) `oci.image_digest`
  == record digest; `oci_tags[1]` == `"sha-" + S`;
  `labels["slaif-local-coding.qualification"]` == `mvp-release-0.1.0`;
  `labels["slaif-local-coding.wheel.sha256"]` == `artifacts.wheel.sha256` ==
  `fceadc37…`; (d) tamper tests: mutating the record digest, the manifest
  `release` section, or a release tag must each fail the gate; (e) the
  objective-field test asserts `013-a`; (f) the status const test is
  state-conditional (not-yet-published: `released false`, `published false`,
  digest null; published: `released true`, `published true`, digest ==
  record).
- **R5.** Byte-identity law holds: no changes to `src/`, `pyproject.toml`,
  `uv.lock`; the CI wheel-binding step (fresh `uv build` wheel SHA-256 ==
  manifest `artifacts.wheel.sha256`) passes at `S` and `P`; the in-image
  provenance proof (wheel inside image == manifest hash) continues to pass
  in both the qualification and the published-image CI runs.

### B — Dockerfile label parameterization

- **R6.** Exactly one new build ARG:
  `ARG SLAIF_QUALIFICATION_LABEL=disposable-qualification-only; not released`
  (default byte-identical to today's hardcoded value), and the LABEL line
  becomes `slaif-local-coding.qualification="${SLAIF_QUALIFICATION_LABEL}"`.
  No other Dockerfile line changes (stages, pins, users, entrypoint, other
  labels all byte-identical). The qualification compose override does NOT set
  this ARG (default applies, so every 011/012 qualification label stays
  `disposable-qualification-only; not released`); the release workflow sets
  it to `mvp-release-0.1.0`.

### C — Compose split (pull-based canonical)

- **R7.** `compose.yaml` becomes the pull-based canonical file: it contains
  NO `build:` key; `image:
  ${SLAIF_LOCAL_CODING_IMAGE:-ghcr.io/ulfe-lmi/slaif-local-coding:0.1.0}`;
  and it preserves the Objective-011 adapter-service hardening EXACTLY:
  `network_mode: host`, `read_only: true`, `security_opt:
  no-new-privileges:true`, `cap_drop: ALL`, tmpfs `/tmp:size=64m` +
  `/dev/shm:size=256m`, the single read-only config volume with the same
  default path, `env_file` with the same default, the identical `/readyz`
  healthcheck (same test/interval/timeout/retries/start_period), `restart:
  unless-stopped`, `environment: SLAIF_HEALTH_ENDPOINT` with the same
  default, `name: slaif-local-coding`, and the same deliberate absences (no
  privilege flag, no Docker socket, no source bind, no published ports).
- **R8.** New `compose.build.yaml` (qualification override): sets the local
  image `slaif-local-coding:0.1.0-${SLAIF_GIT_SHA:-local}` plus `build:`
  (context `.`; args `SLAIF_GIT_SHA`, `SLAIF_WHEEL_SHA256`). A mechanical
  test renders the two-file spec (`docker compose config` or an equivalent
  deterministic render in CI) and asserts the merged adapter service equals
  the pre-013 single-file effective spec for the closed field set: `image`,
  `build.context`, `build.args`, `network_mode`, `read_only`, `security_opt`,
  `cap_drop`, `tmpfs`, `volumes`, `env_file`, `healthcheck` (all sub-fields),
  `restart`, `environment`.
- **R9.** `scripts/docker_qualification_ci.py` runs the canonical stack via
  the two-file compose (`-f compose.yaml -f compose.build.yaml`) for config
  validation, build, up, stop/start/recreate, and down, and ALL existing
  011/012 phases still run and pass with unchanged semantics. The
  rendered-compose content-policy scan covers BOTH compose files (no secret
  material, no secret values in interpolation defaults). The fail-closed
  phase (which renders its own isolated compose file) is unchanged.
- **R10.** Static gate (new stdlib test): `compose.yaml` contains no
  `build:` key; its default pull reference equals the manifest
  `oci.image_reference` + `:0.1.0`; a `SLAIF_LOCAL_CODING_IMAGE` override
  renders into the `image` field verbatim, including a digest-pinned form
  `ghcr.io/ulfe-lmi/slaif-local-coding@sha256:<64-hex>`.

### D — Release workflow activation

- **R11.** `.github/workflows/release-image.yml` becomes the ACTIVE
  publication path, keeping `workflow_dispatch` as the ONLY trigger (it must
  never run on PRs/pushes) and NO repository secrets (GITHUB_TOKEN only).
  Required steps: checkout the dispatched ref; build the wheel with the
  locked backend; assert the fresh wheel SHA-256 equals the manifest
  (`M_S`) `artifacts.wheel.sha256`; build the image via the two-file compose
  with `SLAIF_GIT_SHA` = the full dispatched SHA, `SLAIF_WHEEL_SHA256` = the
  manifest wheel hash, and `SLAIF_QUALIFICATION_LABEL` =
  `mvp-release-0.1.0`; authenticate to GHCR with GITHUB_TOKEN (
  `docker login ghcr.io`); push the SAME built image as
  `ghcr.io/ulfe-lmi/slaif-local-coding:sha-<S>` unconditionally
  (content-addressed) and as `:0.1.0` ONLY after a registry query proves the
  tag is absent or already points at this exact digest (a pre-existing
  different `0.1.0` digest MUST fail the workflow — no silent repoint of the
  release tag); verify via the GHCR registry API that both tags resolve to
  the same digest and emit that digest (`D`) in the run log/outputs.
- **R12.** Coding ACTUALLY triggers the workflow at `S` during this round
  (`gh workflow run release-image.yml --ref <S>`), waits for a successful
  run, captures `D` and the workflow run id from the registry/run, and
  writes them into the release record at `P`. The report records `S`, `D`,
  and the run id literally. (If the coding credential cannot trigger
  workflow_dispatch, this is a genuine BLOCKED fact to report — do not route
  around it.)

### E — CI published-image gate

- **R13.** A new CI job `docker-published` (separate job preferred), gated
  so it runs ONLY when `packaging/release_record.json` exists with a
  non-null digest (before the record exists it must skip with an explicit
  "not yet published" line; at `P` and `R` it MUST run and pass):
  (a) pull `ghcr.io/ulfe-lmi/slaif-local-coding@<D>` by digest;
  (b) pull by tags `0.1.0` and `sha-<S>` and assert each resolves to `D`;
  (c) verify OCI labels: `org.opencontainers.image.revision` == `S`,
  `org.opencontainers.image.version` == `0.1.0`,
  `slaif-local-coding.package.version` == `0.1.0`,
  `slaif-local-coding.gateway.peer.sha` ==
  `1fccaa746df6cd44f1ddf8c2ec5cf6ea9f18b1cb`,
  `slaif-local-coding.wheel.sha256` == `fceadc37…`,
  `slaif-local-coding.qualification` == `mvp-release-0.1.0`,
  `slaif-local-coding.topology.mode` unchanged;
  (d) run the PULL-BASED compose (primary file only,
  `SLAIF_LOCAL_CODING_IMAGE` pinned to the digest) against the disposable
  fake upstream on canonical port 18031: readiness becomes healthy; a
  representative signed request succeeds from the simulated Gateway
  namespace (signed identity v1, same contract evidence class as the 011
  qualification); negative cases (invalid signature, replay, missing
  service credential) fail closed; readiness is fail-closed with the signing
  secret missing;
  (e) NO-BUILD proof: the image exists locally only via pull before `up`;
  the running container's image ID equals the pulled image's ID; the
  compose file used carries no `build` key (static assertion);
  (f) teardown with absence proof (no container, no listener, port released).
  Reusing/extending `scripts/docker_qualification_ci.py` (e.g. an
  `--image`/`--published` mode) is permitted and preferred over a parallel
  copy of the harness.
- **R14.** ALL existing gates remain unchanged and green at `P` (and `R`):
  `test` (ruff check + format, mypy, full pytest, `uv build`, artifact
  content policy, fresh-venv install smoke, compileall, shell `bash -n`),
  `gateway-contract` (pinned peer `1fccaa746…`), and `docker` (the complete
  011/012 qualification of the locally BUILT image via the two-file compose
  at the final head). No 011/012 Docker-qualification assertion may be
  removed, skipped, or weakened.

### F — Documentation reconciliation (post-publication truth)

- **R15.** `docs/DOCKER-INSTALL.md` is restructured so the PRIMARY operator
  path is pull-based: obtain the reviewed release reference (shallow clone /
  checkout of the tag or commit — needed only for `compose.yaml`,
  `compose.build.yaml`'s absence, and the config template — or an
  equivalent documented file set); instantiate the final
  Gateway-integrated template (same three placeholders, same three DISTINCT
  secret roles in the mode-0600 env file: `QWEN3090_API_KEY`,
  `SLAIF_ADAPTER_SERVICE_TOKEN`, `SLAIF_ADAPTER_SIGNING_SECRET`);
  `docker compose pull`; `docker compose up -d`; verify readiness/health;
  stop/restart/status; **upgrade** = pin the next image tag/digest and
  recreate; **rollback** = restore the previous tag/digest and recreate;
  cache purge; uninstall (including removal of the pulled image); and
  digest-pinning (`…@sha256:<D>`) as the exact-reproduction option. The
  host needs no Python, uv, project dependencies, or virtualenv on this
  path (state this explicitly). The build-from-source path (two-file
  compose) is documented as the QUALIFICATION/DEVELOPMENT path, clearly
  labeled as NOT the released-user path. The development-only ingress
  variant and the Gateway-connection section remain truthful.
- **R16.** Every identified current-facing document (workstream F list) is
  reconciled with post-publication truth: MVP `0.1.0` is PUBLISHED to
  `ghcr.io/ulfe-lmi/slaif-local-coding` at digest `D` with tags `0.1.0` and
  `sha-<S>`, image source commit `S`; the Git tag `v0.1.0` TARGETS `S` —
  documents must state this as the release-reference semantics (tag created
  by strategy post-merge; a document must NOT claim the tag/Release objects
  already exist at document time); the GitHub Release follows the tag;
  protected-host cutover is still NOT performed; no real deployment yet
  evidenced; Docker qualification remains deployment-qualified
  (disposable/CI environments only); the D1 binding law, the loopback
  default, and the systemd secondary path are unchanged. All stale
  "NOT released / no registry publication / inert workflow / build locally
  is primary" current-state statements are removed or corrected. Release
  language stays on the accepted ladder: no "production-ready",
  certification, or generic-equivalence claims.
- **R17.** `M_P`'s `limitations`/`status` follow R3 exactly, and no
  current-facing document may assert a status above what the manifest states
  (mechanical spot-check by review, not a new test).

### G — Round mechanics and safety

- **R18.** At round start, coding re-verifies remote gateway `main` ==
  `1fccaa746df6cd44f1ddf8c2ec5cf6ea9f18b1cb`. If it differs: DO NOT
  publish; stop, publish a BLOCKED report with the exact delta (commit +
  subject), and let strategy inspect and deliberately re-qualify. If it
  matches, proceed (and the `gateway-contract` job must pass at `S` and `P`).
- **R19.** Exact round sequence: implementation commits → `S` (manifest
  `M_S` regenerated; NO release record) → CI at `S` fully green
  (`docker-published` an explicit skip) → trigger the release workflow at
  `S` → workflow SUCCESS, `D` captured → `P` (record + `M_P` ONLY) → CI at
  `P` fully green INCLUDING `docker-published` → report `R` (parent `P`)
  pushed and verified as remote PR head. Coding never merges, never creates
  a Git tag, never creates a GitHub Release.
- **R20.** Protected-host invariance, recorded in the report: before/after
  read-only probes showing the Qwen user-scoped service state unchanged
  (`systemctl --user`), the port-18020 listener owner unchanged, ports
  18031/18033/18034 closed, no new or changed `slaif`-related containers, no
  listener changes, and that NO docker build/run/up occurred on the host.

## Verification and evidence (exact)

- **Local (host):** full ordinary test suite (`uv run --frozen pytest -q`),
  ruff/mypy, `uv build`, the manifest E3 gate (not-yet-published state at
  `S`), the static compose gates, `docker compose config` render checks for
  both file combinations (render only — NO docker build/run/up on the host),
  `bash -n` on changed shell, `compileall` on changed Python.
- **CI at `S`:** `test`, `gateway-contract`, `docker` SUCCESS;
  `docker-published` skipped with the explicit not-yet-published line.
- **Release workflow run at `S`:** SUCCESS; both tags pushed; registry-
  verified single digest `D` emitted; no secrets in logs.
- **CI at `P` (and `R`):** all four jobs, with `docker-published` executed:
  digest+tag pulls, label checks, full contract run against fake upstream,
  no-build proof, teardown absence proof.
- **Registry (captured by coding, re-verified independently by strategy):**
  tag `0.1.0` → `D`; tag `sha-<S>` → `D`; image pulled by digest `D`
  carries the asserted labels; anonymous pull works (public repository).

## Documentation and compatibility contracts

- The pinned Gateway contract is UNCHANGED (continuously tested by
  `gateway-contract` at the pinned peer `1fccaa746…`).
- The configuration contract is UNCHANGED: same signed template
  (`config/adapter.gateway-integrated.template.toml`, SHA
  `58ff541b…`), same three placeholders, same three distinct Local-side
  secret roles; `docs/DOCKER-INSTALL.md` documents the pull path against
  that unchanged contract.
- `docs/DOCKER-SECURITY-DELTA.md` remains the release-gate reference for the
  host-network security delta; the published-image CI adds no new platform
  claims (Linux Docker Engine + Compose v2 only).

## Security / privacy / secrets / resource / protected-host constraints

- Registry authentication uses ONLY the runner `GITHUB_TOKEN`; NO new
  long-lived secret of any kind is introduced (repository `secrets`
  untouched).
- No secret value, host path, private identifier, prompt, model output, or
  raw acceptance payload may appear in the image, the workflow, compose
  renders, CI logs, the release record, the manifest, or the report. CI
  fake credentials follow the established 011 pattern (generated, 0600
  files only, never printed, never recorded).
- The published image must pass the same forbidden-content scan as the
  built image (no OAP/orders/reports, no tests, no references, no caches, no
  development artifacts) — asserted in `docker-published`.
- Protected live-host law in full force (read-only probes only; default no
  mutation); NO protected-model inference; bounded resources as in 011.
- A compromised-container threat analysis for host networking remains as
  documented in `docs/DOCKER-SECURITY-DELTA.md` (unchanged by this
  objective); publication does not change the trust boundary.

## Local authority

Coding owns safe repo-local tooling, `uv`/`pytest` execution, static
renders, and the `gh workflow run` dispatch (credential verified present
with `repo`+`workflow` scopes). Human and strategic are not terminal
operators. Anything beyond safe repo-local action stops and reports.

## GitHub publication requirements

- Start from `origin/main` @ `a04693e6792df6a8ad4262acfb46336a0f662202`;
  create fresh branch `oap/013-mvp-release-publication`; create EXACTLY ONE
  PR (title: `Objective 013: publish MVP 0.1.0 to GHCR, pull-based
  installation, and release provenance closure`), body recording the
  S/P/D semantics, the human authorization, and the explicit non-goals.
- Push ALL non-report work before the report; the PR contains every
  activated objective order, `oap/active` (`013-a`), and the final report.
- Inspect and safely repair in-scope CI failures; NEVER merge; never enable
  auto-merge; publish the report-only SELF child (`R`) and verify it is the
  remote PR head with first parent `P`.

## Exact immutable report contract

`oap/reports/013-a-mvp-release-publication.md` (exactly one report for this
ID) containing:

1. `Implementation head SHA: <literal 40-hex P>` and
   `Report publication commit: SELF`.
2. Overall status (`COMPLETE`/`PARTIAL`/`BLOCKED`/`FAILED`) plus per-
   workstream status.
3. Literal facts: `S` (image source commit), `D`
   (`sha256:<64-hex>`), the GHCR tag→digest mapping as registry-verified
   (`0.1.0` → `D`, `sha-<S>` → `D`), the release-workflow run id,
   `published_at`, wheel SHA-256 (must be `fceadc37…`), Gateway peer SHA
   (must be `1fccaa746…`), `M_S.generated_from.git_commit` and
   `M_P.generated_from.git_commit`, PR number/URL.
4. Per-acceptance-criterion evidence for R1–R20 (exact command/phase/CI
   line references; `PASSED|FAILED|SKIPPED|NOT RUN|BLOCKED|PENDING|MISSING`
   labels honest; the `docker-published` skip at `S` and run at `P` both
   evidenced).
5. CI run ids and per-job conclusions at `S`, `P` (and `R` if observable).
6. Protected-host before/after invariance record (R20).
7. Explicit statements: NO Git tag created, NO GitHub Release created, NO
   protected-host mutation, NO docker build/run/up on the protected host,
   NO gateway repository change, NO dependency change.
8. Any deviation from this order with exact justification and status.

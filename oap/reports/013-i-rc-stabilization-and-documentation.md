# OAP Coding-Agent Report — 013-i

## Work order
- Identifier: `013-i`
- Work-order file: `oap/orders/013-i-rc-stabilization-and-documentation.md`
- Numeric objective: `013`
- PR mode: `AMENDED_EXISTING_PR`

## Status
`COMPLETE` (this preparatory round only — source/documentation freeze and
RC-safe publication machinery verified; the immutable RC publication itself
remains PENDING a separate later round bound to the exact reviewed source
commit. `COMPLETE` never means accepted.)

## Executive summary

Round 013-i stabilized and froze the SLAIF Local Coding 0.1.0 release
candidate per the human's private-RC direction (public final release
DEFERRED): (1) the activated 013-i order, `oap/active` (`013-i`), and the
previously uncommitted activated 013-g/013-h orders were committed unchanged
with SHA-256 verification; (2) the user-facing documentation was cleaned up
BEFORE the artifact freeze (README landing page, new QUICKSTART.md and
INSTALL.md, docs index, RC handoff, reconciled engineering docs, compose
switched to explicit image selection with no silent legacy default) with a
scoped mechanical documentation-consistency gate added to normal CI plus
negative fixtures; (3) the historical `hatchling==1.32.0` reproducibility
claim was INDEPENDENTLY PROVEN on clean isolated builds (it exactly
reproduces the historical published wheel/sdist; the unpinned backend
resolved 1.32.3 and produced the exact observed CI drift wheel), the build
backend is now pinned, and double clean builds of the final tree are
byte-identical; (4) provenance evolved to schema v4 with an explicit
pre-freeze candidate state, recorded build toolchain, and a separate
`rc_published` state that can never imply `final_public_release=true`; (5)
the RC artifact record schema/generator (strict, no fake-digest mode) and
the RC-safe publication machinery (explicit private candidate identity
`0.1.0-rc1`, fail-closed authenticated tri-state tag checks before any
mutation, final-tag rejection, before/after registry verification,
least-privilege `packages:read` qualification consuming the RC record with
an explicit NOT RUN pre-publication state) were delivered. This round
performed ZERO registry writes, dispatched no workflow, created no Git tag
or GitHub Release, changed no `src/` behavior, and left the protected
host byte-invariant. CI is freshly green (4/4) at the implementation head.

## Authoritative GitHub state
- Repository: `ulfe-lmi/slaif-local-coding`
- PR number/URL/state: #15, https://github.com/ulfe-lmi/slaif-local-coding/pull/15, OPEN
- Base/head: base `main` `a04693e6792df6a8ad4262acfb46336a0f662202`; head branch `oap/013-mvp-release-publication`
- Starting remote SHA: `6406820912b80f67b6a12d0bafe6ddcd569d9f2e`
- Implementation head SHA: `317cc27232e582e83f4664ed3eceb0dd68c4e2aa`
- Report publication commit: `SELF`
- Candidate image source commit (separate field, when an image is in scope): `NONE` (no image was built for, or published from, this round; the RC image source commit will be bound by the publication-round order and recorded in `packaging/rc_record.json`)
- Implementation commits pushed: `317cc27232e582e83f4664ed3eceb0dd68c4e2aa` (single implementation commit, parent `6406820912b80f67b6a12d0bafe6ddcd569d9f2e`)
- New PR this round: `NO`
- Amended existing PR: `YES` (title/body updated to the RC framing)
- Merge performed: `NO`

## Changes made

- **A (transcript/disposition/authority):** committed the activated
  013-i order + `oap/active` and the previously uncommitted activated
  013-g/013-h orders unchanged (SHA-256 verified: 013-g
  `156b82b26dd5bedd1dca5eaa102e1d087a8d06b5ff76b984d4ceae6a1113ebc1`,
  013-h `3550e417d1fbe4d65a113d09a37c258b291035965aac0834751523ac56a4825f`,
  013-i `1ae43b23ee98e4c4ad30f67768dad9f26d0e96514ff66e522984751281703179`);
  updated the Objective-013 row of `oap/COMPLETENESS.md` to RC
  stabilization/freeze with the public final release DEFERRED and the
  historical private publication explicitly described as never published to
  users; added the prospective field law to `oap/README.md` and
  `oap/templates/REPORT-TEMPLATE.md` (`Implementation head SHA` = literal
  immediate pre-report commit, NOT the image source commit; the image
  source gets its own field) without modifying any historical report or
  order bytes. The untracked `Local`/`clean`/`unchanged` residue was left
  uncommitted and untouched.
- **B (documentation cleanup before freeze):** `README.md` rewritten as a
  concise product landing page (purpose, client -> separate Gateway ->
  adapter -> private Qwen/vLLM topology, capabilities, runtime/deployment
  assumptions, getting started, documentation table, RC release status,
  limitations, Apache-2.0 license/credits including
  `syv-ai/qwen38-27b-rtx3090`, developer gate); new root `QUICKSTART.md`
  (5-10 minute Docker path, zero Python/uv/venv/build tokens) and
  `INSTALL.md` (Docker primary; Python/uv build tokens only after the
  `## Advanced: direct-host (systemd) installation` marker); new
  `docs/README.md` index (operator / architecture-security /
  developer-testing / OAP-history); new `docs/RC-HANDOFF.md` (retrieval +
  identity verification only; explicitly not a benchmark/cutover/final
  release); reconciled `docs/DOCKER-INSTALL.md`, `docs/DEPLOYMENT.md`,
  `docs/RELEASE-ARTIFACT-POLICY.md`, `docs/TOPOLOGY.md`,
  `docs/IMPLEMENTATION-ROADMAP.md` (2026-09-20: RC freeze, final release
  DEFERRED); `compose.yaml` now requires EXPLICIT image selection via
  `${SLAIF_LOCAL_CODING_IMAGE:?...}` (fails closed; the historical private
  `0.1.0` tag is never a default) with no build key; new scoped
  `scripts/docs_consistency_check.py` gate (required docs, README links,
  relative link resolution, stale-claim wording, pull-only primary compose,
  build-token gating) added to the CI `test` job with meaningful negative
  fixtures.
- **C (reproducible build + truthful provenance):** `pyproject.toml`
  `[build-system]` pinned to `hatchling==1.32.0` (evidence recorded below);
  sdist include extended for the new root docs; `packaging/rc_record.json`
  excluded from all build inputs. Provenance schema v4
  (`slaif-release-provenance-v4`): new `build` (backend 1.32.0 + resolved
  build environment + uv 0.12.5 + Python 3.12) and `candidate`
  (`0.1.0-rc1`, `pre_freeze|rc_published`, `private_registry_auth_required:
  true`, `final_public_release: false`, `cutover_performed: false`)
  sections, `oci.candidate_tag`, 4-key `status` (separate `rc_published`
  and `final_public_release`); the final `release` section exists only in
  the final state. New `packaging/rc_artifact_record.schema.json`
  (`slaif-rc-record-v1`, 18 closed keys) and
  `scripts/rc_artifact_record.py` (strict builder from verified facts,
  atomic frozen-identity emitter, NO fake-digest mode). Manifest generator
  rewritten for the three-state model; committed manifest regenerated in
  the `pre_freeze` state (new wheel/sdist identities; old wheel/digest NOT
  reused).
- **D (RC-safe publication machinery):** `scripts/release_registry_publish.py`
  bound to the explicit private candidate identity `0.1.0-rc1`
  (`--release-tag` default; `FORBIDDEN_FINAL_TAGS = {0.1.0, latest, stable,
  v0.1.0}` hard-rejected before any credential/registry access); BEFORE any
  mutation both target tags are tri-state checked with authenticated access
  (`scripts/ghcr_tag_check.py --strict`: `digest:<d>` / `absent` /
  `unauthorized`, fail closed on unauthorized); occupied-different
  candidate tag fails BEFORE the candidate tag is pushed; colliding
  source tag fails after the content-addressed write with the candidate
  tag untouched; idempotent same-digest retries; before/after registry
  states emitted; `GITHUB_OUTPUT published_digest/published_tag`.
  `.github/workflows/release-image.yml` (workflow_dispatch-only) builds the
  wheel bound to the manifest, builds the RC candidate image with the
  qualification label `rc-candidate-0.1.0-rc1; private; not final release`,
  and publishes via the fail-closed law. `.github/workflows/ci.yml`
  `docker-published` job: least-privilege `packages:read`, consumes the RC
  record (else final record, else explicit NOT RUN), authenticates with
  GITHUB_TOKEN, pulls by digest + both tags, registry API strict checks
  must equal the recorded digest, verifies the full OCI label set (from the
  manifest) and then runs the existing signed-ingress/fail-closed/
  readiness/no-build/teardown assertions on the PULLED digest.
  `scripts/docker_qualification_ci.py` gained RC-record dispatch.

## Files changed

36 files in implementation commit `317cc27232e582e83f4664ed3eceb0dd68c4e2aa`
(+4585/-989): `.github/workflows/ci.yml`, `.github/workflows/release-image.yml`,
`README.md`, `compose.yaml`, `INSTALL.md` (new), `QUICKSTART.md` (new),
`docs/README.md` (new), `docs/RC-HANDOFF.md` (new), `docs/DEPLOYMENT.md`,
`docs/DOCKER-INSTALL.md`, `docs/IMPLEMENTATION-ROADMAP.md`,
`docs/RELEASE-ARTIFACT-POLICY.md`, `docs/TOPOLOGY.md`,
`oap/COMPLETENESS.md`, `oap/README.md`, `oap/active`,
`oap/templates/REPORT-TEMPLATE.md`,
`oap/orders/013-g-manifest-correction-and-complete-publication.md` (new,
unchanged bytes), `oap/orders/013-h-release-record-documentation-closure.md`
(new, unchanged bytes),
`oap/orders/013-i-rc-stabilization-and-documentation.md` (new, unchanged
bytes), `packaging/release_provenance_manifest.json` (regenerated,
pre_freeze v4), `packaging/release_provenance_manifest.schema.json` (v4),
`packaging/rc_artifact_record.schema.json` (new), `pyproject.toml`,
`scripts/docker_qualification_ci.py`, `scripts/ghcr_tag_check.py`,
`scripts/release_provenance_manifest.py`, `scripts/release_registry_publish.py`,
`scripts/rc_artifact_record.py` (new), `scripts/docs_consistency_check.py`
(new), `tests/test_compose_pull_canonical.py`,
`tests/test_gateway_integrated_deployment.py`,
`tests/test_release_provenance_manifest.py`,
`tests/test_release_registry_publish_digest.py`,
`tests/test_docs_consistency.py` (new), `tests/test_rc_record.py` (new).

No `src/` file changed (`git diff --stat 6406820..HEAD -- src/` is empty).
Untracked `Local`/`clean`/`unchanged` residue remains uncommitted.

## Acceptance-criteria evidence

### A1 — Commit activated orders + active unchanged; verify SHA-256; preserve history
- Result: `PASSED`
- Evidence: all three order files committed byte-identical (SHA-256:
  013-g `156b82b2…ebc1`, 013-h `3550e417…825f`, 013-i `1ae43b23…0317` —
  exactly the order-verified values); `oap/active` committed as `013-i\n`
  (od-verified); all historical orders/reports preserved (none modified);
  `Local`/`clean`/`unchanged` left untracked; no invented historical report.

### A2 — Objective-013 disposition + PR title/description to RC freeze
- Result: `PASSED`
- Evidence: `oap/COMPLETENESS.md` header (2026-09-20) and Objective-013 row
  now state RC stabilization/freeze, final release DEFERRED, historical
  private tags never published to users, historical evidence kept
  historical; PR #15 retitled "Objective 013: 0.1.0 RC stabilization,
  documentation freeze, and RC-safe publication machinery (final public
  release deferred)" with an RC-framed body (non-goals included).

### A3 — Prospective report-field law without touching historical bytes
- Result: `PASSED`
- Evidence: `oap/README.md` field-law paragraph +
  `oap/templates/REPORT-TEMPLATE.md` field notes added (Implementation head
  SHA = literal immediate pre-report commit; separate "Candidate image
  source commit" field); historical reports/orders unmodified (no
  historical file appears in the commit diff). The 013-g/h "W6b = S"
  coincidence is explained as two facts that happened to be equal.

### B4 — README rewritten as product landing page
- Result: `PASSED`
- Evidence: new README carries purpose, the client -> separate Gateway ->
  adapter -> private Qwen/vLLM topology, capabilities, runtime assumptions,
  getting started, documentation table, RC release status ("no timing is
  promised, and nothing in this repository implies that the final release
  has happened"), limitations, Apache-2.0 license + credits (including
  `syv-ai/qwen38-27b-rtx3090`), and the developer gate; no OAP chronology,
  objective/round/PR/merge-SHA ledgers, or acceptance dumps on the front
  page (the stale-claim gate mechanically enforces this in CI).

### B5 — QUICKSTART.md essential Docker path
- Result: `PASSED`
- Evidence: 5-10 minute Docker path: prerequisites (Docker Engine + Compose
  v2, upstream at loopback, separate Gateway, bounded `packages:read`
  credentials, RC record), obtain compose/config at the recorded image
  source commit, digest-preferred explicit image selection (compose fails
  closed), password-stdin registry login, mode-0700 dir + mode-0600
  config/env with non-root 10001:10001 readability, compose pull/up, bounded
  health/readiness, minimal troubleshooting, links to INSTALL.md/
  DOCKER-INSTALL.md/RC-HANDOFF.md. Machine check: zero
  `uv build|uv venv|uv sync|uv lock|pip install|python -m venv` tokens
  (enforced by the docs gate).

### B6 — INSTALL.md full operator installation
- Result: `PASSED`
- Evidence: Docker primary (platforms/prerequisites incl. "Compose installs
  only the adapter container — not weights, not the Gateway", exact
  matching file retrieval at the recorded source commit, tag vs immutable
  digest selection with "never the historical private 0.1.0 tag", protected
  config/env with password-stdin credentials, pull/start, bounded
  readiness, stop/restart, upgrade, digest-based rollback, cache purge,
  uninstall, honesty note); direct-host systemd path strictly secondary
  under `## Advanced: direct-host (systemd) installation` with its own
  Python 3.12 + uv requirements (machine check: build tokens appear only
  after that marker).

### B7 — Docs reconciliation, index, explicit compose selection
- Result: `PASSED`
- Evidence: `docs/README.md` index separates operator / architecture+
  security / developer+testing / OAP+history; `docs/DOCKER-INSTALL.md`,
  `docs/DEPLOYMENT.md`, `docs/RELEASE-ARTIFACT-POLICY.md`,
  `docs/TOPOLOGY.md`, `docs/IMPLEMENTATION-ROADMAP.md` reconciled to the RC
  framing (historical private `0.1.0` explicitly "legacy unpublished-to-
  users output, NOT the RC benchmark target"); no current claim of a
  final/public 0.1.0 release (mechanically enforced); `compose.yaml` image
  field is `${SLAIF_LOCAL_CODING_IMAGE:?...}` — explicit selection, no
  silent default, no build key (machine-checked by
  `tests/test_compose_pull_canonical.py`).

### B8 — Mechanical documentation consistency gate in normal CI + negative fixtures
- Result: `PASSED`
- Evidence: `scripts/docs_consistency_check.py` (scoped to the 11 current
  user-facing docs; OAP transcripts out of scope) added to the CI `test`
  job between pytest and uv build; checks required files, README ->
  QUICKSTART/INSTALL links, relative link resolution (fence-aware,
  repo-bounded), stale-claim wording (`this PR`, `pre-merge`, `benchmark
  pending`, 0.1.0-non-RC released/available, final-release done/ready —
  with the RC-wording false-positive excluded), pull-only primary compose,
  QUICKSTART build-token ban, INSTALL pre-marker build-token ban. Local +
  CI: `docs consistency: OK (11 scoped docs checked)`. `tests/
  test_docs_consistency.py`: positive real-repo run + 11 negative fixtures
  (broken link, missing required file, missing README link, `this PR`,
  released-claim, RC-wording false-positive control, compose build key,
  quickstart token, pre-marker token, missing marker) all fail as required.

### C9 — Independent hatchling verification + toolchain pin
- Result: `PASSED`
- Evidence (clean isolated checkouts, scratch `/tmp/slaif-013i/`, isolated
  venvs with `hatchling==1.32.0`): building the UNCHANGED historical source
  (clean archive of W6b `fe334e87c9f0fc65d1826cf9af7dad7e9f70a94a`) yields
  wheel `879baa3ad19e0f513090add965d267957d27f7bcd904d1e225586d76126f8b19`
  (83352 B, 26 entries) + sdist
  `5a60cd6ef41764f16871fd0134b6c234409ba2708b31e863fc84e7e520f` (439900 B,
  108) — EXACT match to the historical manifest on BOTH Python 3.12.14 and
  3.12.3 with uv 0.12.5. Build environment of the pinned backend:
  hatchling 1.32.0, packaging 26.3, pathspec 1.1.1, pluggy 1.6.0,
  tomlkit 0.15.1, trove-classifiers 2026.6.1.19 (recorded in the manifest
  `build` section). Counterfactual: unpinned `uv build` (uv 0.12.5)
  resolved hatchling 1.32.3 and produced wheel
  `9bf64a47d5c010d00177b31bd82e2db8ec36f505b2e10d02315789590ee2bd84` —
  exactly the CI drift wheel observed in run 35348409538 — with the sdist
  unchanged. Hypothesis PROVEN; `pyproject.toml` pins
  `requires = ["hatchling==1.32.0"]` and the generator asserts the pin on
  every generation. No runtime dependency or behavior changed.

### C10 — Double clean build of the final source; old wheel/digest not reused
- Result: `PASSED`
- Evidence: after ALL doc/build changes, two clean trees were produced by
  `git archive 317cc27232e582e83f4664ed3eceb0dd68c4e2aa` into independent
  directories with independent `UV_CACHE_DIR`s and output dirs; both
  `uv build` runs produced byte-identical artifacts: wheel
  `5f1bcf7b35b96b3369c5c9e8e015f4254c7904ebe40f617f6d2e7835a5aed849`
  (75784 B, 26 entries) and sdist
  `b92e5938cbbe9618ac805580c2b3a33ab7d533ff889467607bbbbace86cf132d`
  (448747 B, 115 entries), each EQUAL to the committed manifest values
  (the E3 gate re-proves this in CI). The sdelta vs the historical sdist is
  exactly the six authorized new files (QUICKSTART.md, INSTALL.md,
  docs/README.md, docs/RC-HANDOFF.md, packaging/
  rc_artifact_record.schema.json, tests/test_docs_consistency.py), nothing
  removed. The cleaned README changes wheel METADATA identity
  intentionally; the historical wheel `879baa3a…` and the historical
  private registry digest `sha256:a5debcb2…` are explicitly NOT reused for
  the RC. Artifact content policy + fresh-venv install smoke retained and
  green.

### C11 — Provenance schema/generator/tests for explicit candidate state
- Result: `PASSED`
- Evidence: schema v4 separates `candidate.state`
  (`pre_freeze|rc_published`) and `status.rc_published` from
  `status.final_public_release`; `candidate.final_public_release` and
  `cutover_performed` are const `false`; the final `release` section exists
  only with a final record. Strict closed-key validation of both records;
  self-reference exclusion: the manifest, its schema, and the post-
  publication records are all in the pyproject top-level build exclusions
  (verified by the artifact content policy). No fabricated provenance:
  `generated_from.git_commit` = `6406820912b80f67b6a12d0bafe6ddcd569d9f2e`
  (verified ancestor of the implementation head) and the E3 gate
  mechanically proves artifact-input equality by full regeneration. Tests:
  `tests/test_release_provenance_manifest.py` (21 tests) covers v4 shape,
  state-conditional status/labels/digest, accepted wheel hash
  `5f1bcf7b…`, cross-hashes, and tamper rejection (final-record tamper +
  13 RC-record tamper mutations: extra key, schema drift, identifier drift,
  bad digest, wrong tags, `final_public_release: true`,
  `cutover_performed: true`, `private_registry_auth_required: false`, bad
  wheel hash, toolchain drift, bad timestamp, bad workflow, bool run-id).

### C12 — RC artifact record schema/generator + handoff; no fake digest this round
- Result: `PASSED`
- Evidence: `packaging/rc_artifact_record.schema.json`
  (`slaif-rc-record-v1`, 18 closed keys: product 0.1.0 / RC identifier
  `0.1.0-rc1`, exact image-source commit, OCI reference/digest, tag pair,
  published_at, workflow + run id, `private_registry_auth_required: true`,
  `final_public_release: false`, `cutover_performed: false`, wheel SHA-256,
  dependency-lock hash, frozen Gateway authority, pinned build toolchain,
  deployment assumptions). `scripts/rc_artifact_record.py` builds only from
  verified facts (there is NO mode that records an unpublished image as
  published) and the emitter refuses to overwrite a frozen non-identical
  record. `docs/RC-HANDOFF.md` is the human-readable handoff (retrieval +
  identity verification only; not benchmark code or a run ledger). No
  `packaging/rc_record.json` was created this round (no claimed
  publication). `tests/test_rc_record.py` (10 tests): happy path, fact
  binding to manifest+lock, bad source/digest/timestamp/run-id rejection,
  frozen-identity overwrite law, strict-loader round-trip.

### D13 — Explicit candidate identity; fail-closed tag law
- Result: `PASSED` (machinery delivered and unit-tested; NOT dispatched this round)
- Evidence: publisher default candidate tag `0.1.0-rc1` (`--release-tag`);
  `FORBIDDEN_FINAL_TAGS = {0.1.0, latest, stable, v0.1.0}` rejected with
  `PublishError` before any credential/registry access (unit-tested for all
  four tags); before any mutation, `ghcr_tag_check.tag_digest_strict`
  resolves each target tag as `digest:<d>` / `absent` (verified: token
  exchange succeeded, manifest 404) / `unauthorized` (exchange denied —
  fail closed, never reported absent); candidate tag occupied at a
  different digest -> fail BEFORE the candidate tag is pushed; source tag
  collision -> fail after the content-addressed write with the candidate
  tag untouched; same-digest occupation -> idempotent no-op. Collision
  reports name the tags/digests for strategy adjudication (no silent
  re-point, no invented candidate). Digest is authoritative; tags are
  aliases (stated in workflow/compose/docs).

### D14 — Token law, no visibility change, old tags preserved
- Result: `PASSED` (no registry mutation performed this round — strongest form)
- Evidence: publication uses the workflow GITHUB_TOKEN (declared
  `packages: write`), passed only via the `SLAIF_GHCR_TOKEN` environment
  variable, never printed (failure paths redact it — unit-tested);
  qualification uses least-privilege `packages: read`. No repository
  secrets, no long-lived credentials, no visibility change, no
  organization settings introduced. ZERO registry writes/dispatches in
  this round: the historical tags `0.1.0` + `sha-fe334e87…` (digest
  `sha256:a5debcb24bb6bbf7cf00dbf80cd17367d57186f6b0d7fadac020b94df53a0011`,
  private, never published to users) and the orphan `sha-be3c78b2…` are
  preserved byte-for-byte by construction (no registry interaction at all).
  Before/after registry verification is implemented in the publisher
  (emitted pre/post tag states + final both-tags-one-digest check).

### D15 — docker-published qualification consumes the RC record
- Result: `PASSED` (machinery delivered; explicit NOT RUN state verified in CI; actual execution deferred to the publication round)
- Evidence: the CI `docker-published` job (permissions `contents: read` +
  `packages: read`) gate: RC record -> final record -> else explicit
  `docker-published: NOT RUN (pre-publication: no RC or final publication
  record)` with `published=false` (this is what run 35510283615 printed).
  When a record exists it authenticates privately, pulls by digest AND by
  both tags, asserts image-ID equality, requires the registry API strict
  checks to equal `digest:<recorded D>`, verifies the full OCI label set
  from the manifest (incl. the qualification label and
  `org.opencontainers.image.revision` = source), then runs the existing
  signed-ingress/fail-closed/readiness/no-build/teardown assertions on the
  PULLED digest on disposable CI only. Invalid records or inaccessible
  images fail (the loaders are strict closed-key validators; unauthorized
  registry state fails closed). The order's "at final freeze this gate must
  actually execute; a skip is not acceptance" is carried into the
  publication round.

### D16 — Existing gates preserved; freeze discipline; identity distinction
- Result: `PASSED`
- Evidence: all pre-existing gates retained (normal test, Gateway contract,
  Docker qualification, artifact policy, fresh-venv smoke) and green; the
  publication path can freeze only after clean source gates pass (this
  round's CI is the clean-source gate) and will build from the exact
  recorded commit; immutable digest vs mutable tags documented throughout
  (RC-HANDOFF, RELEASE-ARTIFACT-POLICY, compose, workflow header); build-
  time candidate identity vs later human approval documented (RC-HANDOFF
  "Build-time candidate identity vs later human approval"; promotion
  references the SAME tested digest without rebuilding/relabelling). No
  promotion authorized or performed.

### Inherited supersession mapping (prior 013 acceptance requirements)
- Anonymous public package access as acceptance (013-g G3, 013-h G0):
  **SUPERSEDED BY HUMAN RC DIRECTION** — private RC access is acceptable
  and expected; anonymous pull is not a prerequisite.
- Historical `0.1.0` + `sha-fe334e87…` tag publication at digest
  `sha256:a5debcb2…` (013-b..013-g): **RETAINED AS HISTORICAL FACT** —
  private package, never published to users; explicitly NOT the RC
  benchmark target; preserved byte-for-byte.
- Final public release / `v0.1.0` Git tag / GitHub Release (013-a..h):
  **DEFERRED TO A LATER HUMAN DECISION** — no tag, Release, or final
  release claim this round; the RC candidate is the unit of publication.
- `docker-published` gate must actually execute (013 D15 law): **DEFERRED
  TO THE EXACT-SOURCE PUBLICATION ROUND** — now RC-aware; before any RC it
  reports the explicit NOT RUN pre-publication state (verified in CI).
- `release_record.json` + schema-v3 published manifest state: **SUPERSEDED**
  by the schema-v4 `pre_freeze`/`rc_published` candidate model +
  `rc_record.json` (fulfilled here as machinery; final record path retained
  for the later final state).
- Pull-based canonical compose as the operator path (011/013): **RETAINED
  AND STRENGTHENED** — explicit image selection, no silent legacy default.
- Deterministic build + E3 regeneration (013-e): **RETAINED AND
  STRENGTHENED** — `hatchling==1.32.0` pin proven against the historical
  source; v4 `build` section records the toolchain.
- Frozen Gateway peer `08ca421bee1ddca62078302b910e8be88cf705be`:
  **RETAINED** — not re-pinned (gateway main moved to
  `db0bd3aeaaadee71ba40a16ee0dddf7a35e0a4b7`; current main is NOT the
  compatibility authority); contract gate green at the frozen peer.

## Local verification
- `uv sync --frozen --extra dev [--group gateway-contract]`: `PASSED`
- `uv run --frozen ruff check .`: `PASSED` (all checks passed; 378 files)
- `uv run --frozen ruff format --check .`: `PASSED` (378 files)
- `uv run --frozen mypy src tests`: `PASSED` (74 files, CI-equivalent venv
  without the gateway-contract group; two pre-existing `unused-ignore`
  findings appear ONLY when sqlalchemy is locally importable, which CI's
  test job never has)
- `uv run --frozen pytest -q` (local, protected host, gateway-contract
  group present): `PASSED` — 1155 passed, 26 skipped (1181 collected)
- `uv run --frozen python scripts/docs_consistency_check.py`: `PASSED`
  (`OK (11 scoped docs checked)`)
- `uv build` (final working tree): `PASSED` — wheel
  `5f1bcf7b35b96b3369c5c9e8e015f4254c7904ebe40f617f6d2e7835a5aed849`
  (75784 B / 26 entries), sdist
  `b92e5938cbbe9618ac805580c2b3a33ab7d533ff889467607bbbbace86cf132d`
  (115 entries)
- C10 double clean build from `git archive` of the implementation head
  (isolated caches/outputs): `PASSED` — both builds byte-identical to each
  other and equal to the committed manifest values
- `uv run --frozen python scripts/release_provenance_manifest.py`
  (regeneration, pre_freeze state): `PASSED`; E3
  `test_committed_manifest_matches_regenerated`: `PASSED`
- `uv run --frozen python scripts/artifact_policy_check.py --dist <final> --inspect`:
  `PASSED` (ok: true, zero violations; forbidden-content scan included)
- `uv run --frozen python scripts/artifact_policy_check.py --dist <final> --install-smoke`:
  `PASSED` (fresh-venv wheel install + import + CLI smoke)
- `python -m compileall -q src tests oap/bin scripts`: `PASSED`
- `bash -n oap/bin/*.sh packaging/*.sh`: `PASSED`
- `SLAIF_GATEWAY_ROOT=<frozen clone> uv run --frozen python scripts/
  gateway_contract.py --gateway-root <frozen clone> --run-tests`
  (frozen peer `08ca421bee1ddca62078302b910e8be88cf705be`, depth-1 clone):
  `PASSED` — 18/18, network guard enabled, checkout clean
- `python scripts/release_registry_publish.py --self-check-refs`: `PASSED`
  (qualified references + final-tag guard proof)
- C9 historical-source experiments (isolated venvs, Python 3.12.14/3.12.3):
  `PASSED` (evidence in C9 above)
- Live bounded `/health`, `/v1/models`, text/tool/streaming/multi-turn/
  vision/two-image/compiler-cache calls: `NOT RUN` (not required by this
  order; "no model inference needed"; the suite's live tests are
  env-gated and skipped by design)
- Real Codex E2E: `NOT RUN` (not ordered)
- Secret/raw-log scan (artifact + manifest forbidden-content scan): `PASSED`

## Live model/service evidence
- Sanitized endpoint/route: `http://127.0.0.1:18020/v1` (protected
  private Qwen/vLLM fixture; read-only observation only, no inference
  performed this round)
- Exact bounded call/result: none performed (order: "No model inference
  needed")
- Protected fixture mutation: `NO`
- Protected host before/after (read-only, identical):
  - user unit `qwen-serving-vision.service`: `active`/`running`,
    MainPID=23961 (process start `Sun Sep 6 18:57:26 2026`) — unchanged
  - listeners: `0.0.0.0:18020` (vllm, pid 23961) only; no listeners on
    18021/18031/18033/18034
  - `~/.codex/qwen-neumann.config.toml`: 924 B, mode 600, mtime
    2026-09-18 13:16:48 +0200, SHA-256
    `3aef2d8b819e9a5649c1fb739cd97b885cc69dbdf04eb15db7dcdbf4fac488bb`
    (byte-identical to the round-start baseline)
- Registry: ZERO writes/dispatches/probes this round; last-verified
  historical state stands per the 013-g/013-h reports (private package;
  `0.1.0` + `sha-fe334e87…` at `sha256:a5debcb2…`; orphan
  `sha-be3c78b2…`; never published to users).

## GitHub CI / required checks
- Implementation-head state: run 35510283615 at
  `317cc27232e582e83f4664ed3eceb0dd68c4e2aa` — COMPLETED SUCCESS (4/4 jobs)
- test (job 106076867887): `SUCCESS` — ruff check/format, mypy, pytest
  1154 passed / 27 skipped (1181 collected), docs consistency gate OK,
  uv build with fresh-wheel == manifest-wheel binding
  (`5f1bcf7b…` both), artifact policy inspect, fresh-venv install smoke,
  compileall, bash -n. The 1-test skip delta vs the local run (26) is the
  pre-existing host-scoped
  `test_target_semantic_preflight_failure_precedes_protected_selection`
  (skip reason "pinned target qualification dependencies are unavailable";
  its code-level skip condition requires a pinned-target directory and the
  host codex binary that exist only on this host) — honest accounting, not
  a weakened gate.
- gateway-contract (job 106076867718): `SUCCESS` — 18/18 at frozen peer
  `08ca421bee1ddca62078302b910e8be88cf705be`, network guard enabled
- docker (job 106076867803): `SUCCESS` — wheel bound to the manifest
  (`5f1bcf7b…`), full C2-C9 disposable qualification green
- docker-published (job 106076867831): `SUCCESS` via the explicit pre-
  publication state: `docker-published: NOT RUN (pre-publication: no RC or
  final publication record)`, `published=false` (NOT RUN is the correct
  state this round; actual execution is deferred to the publication round
  per D15)
- Check URLs: https://github.com/ulfe-lmi/slaif-local-coding/actions/runs/35510283615
  (jobs: …/job/106076867887 test, …/job/106076867718 gateway-contract,
  …/job/106076867803 docker, …/job/106076867831 docker-published)
- All required green at drafting: `YES`

## Local setup / dependencies
- uv 0.12.5 (pinned in CI), Python 3.12, repo venv via
  `uv sync --frozen --extra dev` (gateway-contract group added only for the
  local pinned Gateway contract gate; pruned again before mypy to mirror
  the CI test job); no new dependencies of any kind (stdlib-only new
  scripts); build backend `hatchling==1.32.0` pinned (order-authorized).

## Documentation
- User-facing: `README.md` (rewritten), `QUICKSTART.md` (new),
  `INSTALL.md` (new), `docs/README.md` (new index), `docs/RC-HANDOFF.md`
  (new), `docs/DOCKER-INSTALL.md`, `docs/DEPLOYMENT.md`,
  `docs/RELEASE-ARTIFACT-POLICY.md`, `docs/TOPOLOGY.md`,
  `docs/IMPLEMENTATION-ROADMAP.md` (reconciled).
- Contracts/mechanism: `compose.yaml` header (explicit selection law),
  `.github/workflows/release-image.yml` header (RC identity + fail-closed
  tag law + token law), `.github/workflows/ci.yml` docker-published header
  (RC record consumption + NOT RUN law), `oap/COMPLETENESS.md`,
  `oap/README.md` (field law), `oap/templates/REPORT-TEMPLATE.md`.
- Consistency enforced mechanically by the new docs gate in normal CI.

## Safety and scope confirmations
- Unrelated files changed: NONE (36 in-scope files; no `src/`; untracked
  `Local`/`clean`/`unchanged` residue untouched)
- Secret/raw customer content exposed: NONE (credential law unchanged;
  redaction unit-tested; no env dumps)
- Production/protected resources accessed or changed: NONE changed
  (read-only protected-host verification only)
- Port 18020 or Qwen/Codex fixture changed: `NO`
- Required tests skipped/not run: live-test suite and Codex E2E not
  required by this order (env-gated skips as designed); one host-scoped
  CI skip documented above; docker-published explicit NOT RUN is the
  correct pre-publication state (not a weakened gate)
- Scope deviation: NONE
- Extra objective PR: `NO`
- Coding-agent merge/auto-merge: `NO`
- Activated order/active edited: `NO` (committed byte-identical)
- Report commit changes only this report: `YES` (by construction — this
  report is the only file in the final commit)

## Known limitations / blockers
- The RC is NOT yet published: no `packaging/rc_record.json`, no RC
  digest, `docker-published` gate in its explicit NOT RUN pre-publication
  state; the RC image identity does not exist yet.
- The wheel/sdist identities are the new authorized ones
  (`5f1bcf7b…`/`b92e5938…`); the historical wheel/digest are not reused.
- Docker qualification and all evidence remain disposable/CI-scoped;
  single RTX 3090 fixture evidence is fixture-scoped, not generic
  production equivalence; no cutover performed; no production deployment
  claimed.
- The sdist is a developer-only source archive.
- The CI test job's skip count (27) legitimately differs from the local
  run (26) by the host-scoped pinned-target test (documented above).

## Recommended strategic follow-up
The exact remaining publication work (strategy-dispatched next
continuation, same PR, bound to the exact reviewed source commit):
1. Review this round's implementation head
   `317cc27232e582e83f4664ed3eceb0dd68c4e2aa` (or the exact reviewed
   commit) and issue the same-PR continuation order for RC publication.
2. Dispatch the `workflow_dispatch`-only `.github/workflows/
   release-image.yml` at that exact source commit S (private package;
   candidate identity `0.1.0-rc1` + content-addressed `sha-<S>`; the
   fail-closed tag law handles any occupation, reporting collisions for
   strategy rather than overwriting).
3. Populate `packaging/rc_record.json` from the verified run via
   `scripts/rc_artifact_record.py` (registry-verified digest; no fake
   digest).
4. Regenerate the provenance manifest in the `rc_published` state (the E3
   gate mechanically proves the binding).
5. Require the `docker-published` gate to ACTUALLY execute and succeed
   against the pushed digest (private auth, least-privilege
   `packages:read`; a skip is not acceptance).
6. Final public release / promotion of the same tested digest remains a
   separate later human decision — not authorized now.

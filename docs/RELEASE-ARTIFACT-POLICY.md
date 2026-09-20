# Release-artifact policy

Order 009-a, workstream B. This is the deliberate, documented artifact policy
for the `slaif-local-coding` package. It replaces the accidental build-backend
defaults that previously produced a wheel containing only the runtime package
and an sdist containing the entire working tree (including OAP transcripts).

## Supported artifacts

- **Wheel (`slaif-local-coding-<version>-py3-none-any.whl`): the single
  supported Python distributable.** It is the only wheel-based artifact used
  for deployment, upgrade, and rollback (see
  [deployment](DEPLOYMENT.md)). Its verified-clean property is that it
  contains exactly the `slaif_local_coding/` runtime package plus
  `*.dist-info/` metadata and license files (`LICENSE`, `NOTICE` under
  `licenses/`).
- **OCI image (publication reference
  `ghcr.io/ulfe-lmi/slaif-local-coding`; RC candidate identity `0.1.0-rc1`
  plus the source ALIAS tag `sha-<full image-source SHA>` (a mutable tag
  naming the image source commit — the content-addressed identity is the
  immutable registry digest);
  local qualification/development tag `slaif-local-coding:0.1.0-<sha>` via
  `compose.build.yaml`):** the supported distribution artifact of the
  **Docker deployment path** (the canonical installation path, order
  011-a; pull-based canonical operator path since order 013-a). The image
  is built **from** the supported wheel;
  the runtime stage installs the built wheel non-editable on top of the
  frozen locked dependencies, so the image content law mirrors this
  artifact policy's exclusions (no `oap/`, no `tests/`, no `references/`,
  no `scripts/`, no `.git`, no caches, no placeholder files, no
  env/secret material, no host-specific paths, no credential values —
  mechanically asserted by the `docker` CI job image content scan, the
  local disposable run, and the `docker-published` CI job for the PULLED
  image). The runtime stage installs the frozen locked dependencies into
  the EXPLICIT runtime venv `/opt/slaif/venv` (a `uv sync --frozen` run
  with `--active` targeting the `VIRTUAL_ENV` environment, order 013-m,
  M1: a plain `uv sync` would create and fill a project `.venv` instead)
  and installs the built wheel with `--no-deps`, so no second dependency
  resolution can drift the runtime from `uv.lock`. The image is bound to
  the committed artifact: the in-image retained wheel hash must equal the
  provenance-manifest wheel hash (B8/C2), and the in-image provenance
  gate additionally compares the ACTUALLY installed runtime distributions
  (observed in-image via `importlib.metadata`) against the frozen lock
  closure exported from the committed `uv.lock` in the build stage plus
  the product wheel — missing, wrong-version, or unexpected
  distributions fail the gate in both the `docker` build qualification
  and the `docker-published` pulled-digest qualification (order 013-m,
  M1). The hardening/label phase asserts the ACTUAL image
  `Os`/`Architecture` from `docker image inspect` (built tag or pulled
  digest) against the supported platform in both modes (order 013-m,
  M2). The publication path is
  ACTIVATED and adapted for the RC candidate (order 013-i): the
  `workflow_dispatch`-only `release-image.yml` publishes the explicit
  candidate identity `0.1.0-rc1` + `sha-<S>` to the **private** GHCR
  package; no code path of the RC workflow may write `0.1.0`, `latest`,
  `stable`, a final `v0.1.0`, or change package visibility (the historical
  private `0.1.0` tag and its orphan `sha-` tag are preserved
  byte-for-byte). Registry credential: the workflow `GITHUB_TOKEN` with
  declared `contents: read` + `packages: write` for publication (the
  documented mechanism for publishing the workflow repository's container
  package; no long-lived credential of any kind is referenced or
  introduced) and least-privilege `packages: read` for the
  published-image qualification job. At RC publication: the tags
  `0.1.0-rc1` + `sha-<S>` resolve to one registry digest `D` recorded in
  `packaging/rc_record.json` (schema `slaif-rc-record-v2`) and the
  provenance manifest (image source commit `S`); the digest is the
  authoritative identity, the tags are aliases; the RC record keeps
  `final_public_release: false` and `cutover_performed: false`. The
  historical Objective-013 private `0.1.0` tag was written to a
  non-public package and was never published to users; it is legacy
  output, NOT the RC benchmark target, and is not a default anywhere in
  the current documentation. Publication is registry-only: no
  protected-host cutover, no real deployment yet evidenced.
- **sdist** (`slaif-local-coding-<version>.tar.gz`): the developer-only
  source archive; not a supported release artifact and never treated as one.
  It carries a deliberate whitelist (code, tests, fixtures, config and
  packaging templates, current docs, CI workflow, project metadata) so that a
  developer can inspect or rebuild the package source without receiving
  orchestration transcripts or host-specific material.

The policy is implemented explicitly in `pyproject.toml`
(`[tool.hatch.build]` top-level exclusions plus per-target
`[tool.hatch.build.targets.wheel]` and `[tool.hatch.build.targets.sdist]`
include/exclude lists). It is not a backend default.

The release provenance manifest
(`packaging/release_provenance_manifest.json`) and its schema are git-only
provenance documents: because the manifest records the artifacts' own
SHA-256 hashes, they are excluded from every artifact (no self-hash cycle).
The manifest remains part of the git checkout and of the deployment
runbook's preconditions. From schema v2 (order 011-a) the manifest covers
**wheel + sdist + OCI build inputs**: the `oci` section records the image
reference, tag convention, base-image name + digest, Dockerfile/compose/
.dockerignore hashes, the cross-referenced wheel hash, the `image_digest`,
the `published` flag, and the image label set. From schema v4 (order 013-i) the manifest is
state-aware over three states: **pre-freeze candidate** (no record: null
digest, `published: false`, `rc_published: false`,
`final_public_release: false`, plus an explicit `candidate` section
recording the RC identity and the recorded build toolchain, and a `build`
section recording the pinned backend and resolved build-environment
dependencies); **RC-published** (with `packaging/rc_record.json` present:
the recorded RC digest `D`, `rc_published: true`, `final_public_release`
REMAINS `false`, the RC qualification label, and the RC tag convention);
and **final-published** (with `packaging/release_record.json` present:
digest `D`, `published: true`, `final_public_release: true`, the
published qualification label, and a closed top-level `release` section
binding the record's identity facts). The post-publication RC record is
excluded from every wheel/sdist/image build input (self-reference
exclusion, order 013-i C11): the manifest records exactly which source
tree was built, and a pre-freeze manifest may reference a verified
ancestor only while the regeneration gate mechanically proves
artifact-input equality.

## What no artifact may contain

Both the wheel and the sdist must be free of:

- orchestration transcripts and OAP state: everything under `oap/`
  (orders, reports, `active`, evidence, `bin`, strategic/coding runtime state,
  `runtime.env`);
- temporary/placeholder files (including the untracked `Local`, `clean`,
  `unchanged` repository-root placeholders);
- caches and virtual environments (`__pycache__`, `*.pyc`, `.venv`,
  `.mypy_cache`, `.pytest_cache`, `.ruff_cache`, `build/`, `dist/`,
  `*.egg-info`);
- host-specific artifacts: paths under `/synology`, hostnames, private LAN
  endpoint addresses, and any file that embeds protected-host deployment
  paths (which is why selected docs, test files, and OAP harness scripts are
  excluded from the sdist; they remain in the git repository, and CI runs from
  the git checkout);
- credentials or key material (upstream API keys, gateway service tokens,
  signing secrets, `*.key`, `*.pem`, `*.env` runtime files), and any file
  whose content embeds them as scanner pattern definitions
  (`tests/test_packaging.py` is excluded for this reason; it remains in the
  git repository and runs in CI);
- model weights, or any Gateway code vendored from the separate
  `slaif-api-gateway` repository.

## Mechanical proof

`scripts/artifact_policy_check.py` is the machine-executable policy check:

```bash
uv run --frozen python scripts/artifact_policy_check.py --dist dist --inspect
```

It fails on any forbidden entry, any missing required entry (wheel runtime
package + metadata + licenses; sdist whitelist), or any forbidden byte pattern
in any artifact file (host paths, hostnames, private LAN endpoints, key
material, credential values). It re-proves the wheel's verified-clean property
and the drift between the built runtime package and the repository source
package on every run.

The check runs:

- in the local gate (this README's "complete local gate" and the pytest gate
  `tests/test_artifact_policy.py`, which builds fresh artifacts and also
  verifies the scanner detects injected violations);
- in CI, after `uv build`, in the `test` job
  (`scripts/artifact_policy_check.py --dist dist --inspect`);
- as part of the disposable operational qualification
  (`scripts/disposable_deployment_qualification.py`) before any install step.

## Fresh-environment install proof (B4)

The wheel must install into a fresh, empty, disposable virtual environment
(venv, not an editable checkout) using only the built wheel:

```bash
uv run --frozen python scripts/artifact_policy_check.py --dist dist --install-smoke
```

The smoke proves: package import, the `slaif-local-coding` console entry point
resolves and runs (`--help`, `--version`), and runtime source provenance
(installed module and dist-info locations are inside the disposable venv, not
the repository checkout; entry point path and SHA-256 are recorded). It runs
in CI on the runner and in the local qualification.

## Cutover artifact authority and supersession (order 010-a, workstream G)

The cutover artifact authority is always the exact wheel recorded in the
current `packaging/release_provenance_manifest.json`, and — for the Docker
path — the exact OCI build inputs (Dockerfile/compose/.dockerignore hashes,
base-image digest, bound wheel hash) recorded in the manifest's `oci`
section. Objective 009's
accepted wheel (0.1.0, SHA-256
`e4759c00e37332998ed92dc5c01fe10be4b11b3a4b1df8c33edc64e176752ee1`, 81462
bytes, 26 entries) was the cutover authority **only while the runtime package
remained byte-identical**. Objective 010 adds a runtime configuration
validator (distinct secret-role environment names, workstream C2), which
changes the runtime package bytes; therefore the cleared rebuild is NOT
byte-identical to the Objective-009 wheel and the current manifest records
the **new** release-candidate artifact set (wheel + sdist hashes, sizes, and
entry counts) generated from the Objective-010 implementation state. That
exact new artifact was the **only** future cutover authority for the
Objective-010 state; the Objective-009 hash remains the accepted
Objective-009 record only (immutable git history) and is no longer the
cutover authority. Objective 011 adds the D1 binding-law validator (workstream
A), which changes the runtime package bytes again: the regenerated Objective-011
artifact set (wheel + sdist + OCI build inputs, manifest schema v2,
`objective: "011-a"`) was the **only** future cutover authority for the
Objective-011 state; the Objective-010-a wheel hash `8678e16b41bd9d73849a956c9d1f25235532eaf52c772fc695718b2063b54472`
remains the accepted Objective-010 record only. Objective 012 re-pins the
Gateway peer and regenerates the manifest with no runtime source byte
change: the entry-level diff of the cleared rebuild proves all 20 wheel
runtime files byte-identical to the Objective-011 record (only
`dist-info/METADATA` and `dist-info/RECORD` differ); the artifact bytes
changed ONLY because (a) the Objective-012-mandated README status-row fix
is embedded in the wheel `dist-info/METADATA` long description
(`readme = "README.md"`; wheel
`7cede0b8e930463400a40662248a97aae22f75b0512dcd8151d6122a99157166` ->
`fceadc378130dd4ffcc3f75d17b5e098577652914f541245d31247911be23aeb`,
+27 B) and (b) the sdist carries in-scope `README.md`/`docs/`/`tests/`
text. The sdist is a developer-only source archive, not a supported
release artifact: it embeds `README.md`, `docs/`, and `tests/`, so its
hash changes with any in-scope text edit, and no current-facing document
cites the current sdist hash — the authoritative current sdist hash is the
one recorded in `packaging/release_provenance_manifest.json` (schema
`slaif-release-provenance-v3`) and mechanically re-derived from the final
state by `test_committed_manifest_matches_regenerated`. The historical
artifact records, cited as historical only, are the Objective-011-a
record (wheel `7cede0b8...` / sdist `4ba17680...`) and the
Objective-012-a-state record (wheel `fceadc37...` / sdist
`910b65db...`); the only OCI build input that changes is the Dockerfile
`SLAIF_GATEWAY_PEER_SHA` label input; the regenerated Objective-012
manifest (producing round recorded in the manifest itself) is the **only**
future cutover authority, and the Objective-011-a artifact record remains
the accepted Objective-011 record only. Objective 013 (historical, PR #15) split
the pull-based canonical `compose.yaml` from the qualification override
`compose.build.yaml` (mechanically proven equivalent for the closed field
set) and parameterized the Dockerfile qualification label ARG (default
byte-identical to the pre-013 label); its round 013-b README status-row
change legitimately changed the wheel METADATA only (wheel
`fceadc37...` -> `879baa3ad19e0f513090add965d267957d27f7bcd904d1e225586d76126f8b19`),
and its publication pushed the historical private tags `0.1.0` and
`sha-<S>` to the non-public package at one digest (registry-only; the
tags were never published to users and the package was never made public —
the round ended BLOCKED at anonymous access verification). Objective
013-i changed the wheel and sdist identity again, on explicitly authorized
inputs only: the README cleanup (the README is the wheel METADATA long
description) and the deterministic build-backend pin (`hatchling==1.32.0`,
proven to reproduce the historical wheel from the clean historical
source); the old wheel and old digest are therefore NOT reused for the RC,
and the cleaned README intentionally produces a new final wheel hash (the
RC candidate source records the new hashes in the regenerated manifest).
Objective 013-j (THIS round) changes the wheel and sdist identity again,
on explicitly authorized inputs only: the hermetic build environment (the
ENTIRE `[build-system].requires` set pinned and recorded from the enforced
resolution — J3), the mechanically verified source-input map and the
truthful A/B source binding (provenance manifest schema v5 — J4), the
self-contained RC record (schema `slaif-rc-record-v2`) with the direct
path->hash source-input map, base-image identities, supported platform,
and publishing-run head SHA (J5), and the RC-safe publisher
verified-absent-for-both write precondition (J1); the recorded artifacts
of the final source input tree are re-frozen in the same round. Any future
objective that changes runtime package bytes or OCI build inputs must
repeat this gate: cleared rebuild (twice, from clean equivalent trees,
with isolated output/cache paths), hash comparison, and manifest
regeneration in the same PR, and a fresh publication round for any new
image.

## Publication (RC candidate machinery)

Registry publication is a **separate, explicitly authorized later round**:
the exact reviewed source commit must first be reviewable, and a
publication round performs registry writes only under its own explicit
authorization — a source round performs zero registry writes by definition.
The machinery (order 013-i; completed by order 013-j, J1) is:

- The `workflow_dispatch`-only `release-image.yml` publishes the explicit
  **RC candidate identity `0.1.0-rc1`** (the EXACT expected identity; the
  publisher never silently allocates a new RC number) plus the source
  ALIAS `sha-<S>` tag to the **private** GHCR package, building the locked
  wheel (bound to the committed manifest), building the image from the
  exact dispatched source commit with the RC candidate qualification
  label, and registry-verifying before and after the mutation.
- **Fail-closed tag law (verified-absent-for-both):** before ANY mutation,
  both target tags are checked with authenticated registry access,
  distinguishing *verified absent* from *unauthorized/inaccessible*, and
  any reported digest must be well-formed. **Verified-absent-for-both is
  the ONLY write precondition:** if EITHER tag is occupied,
  unauthorized/inaccessible, malformed, or unresolved, the run stops
  BEFORE ANY registry mutation (no tag, no push), reports the existing
  digests for strategy adjudication, and never repushes or rebuilds an
  already frozen identity; a crash between the two pushes leaves a
  PARTIAL state that is reported, never silently completed. The target
  state is rechecked immediately before each write, and publication runs
  are serialized by the workflow concurrency group (an in-progress
  publisher is never cancelled).
- **No final-tag path:** no code path of the RC workflow may write
  `0.1.0`, `latest`, `stable`, a final `v0.1.0`, or change package
  visibility; the historical private `0.1.0` and orphan `sha-` tags are
  preserved byte-for-byte.
- **Credentials:** publication uses the ephemeral workflow
  `GITHUB_TOKEN` (`contents: read` + `packages: write`); the
  published-image qualification job uses least-privilege
  `packages: read`. No long-lived write credentials, no repository
  secrets, no visibility changes, no token logging. (Historical record,
  order 013-d: the 013-b "workflow-permission ceiling" diagnosis was wrong
  — the 013-b run logs show the `GITHUB_TOKEN` was granted `Packages:
  write`; the 013-b failure was the unqualified push reference, fixed in
  013-c; no repository security setting was ever changed; the 013-c
  repository-secret workaround was withdrawn and its broad PAT secret
  removed.)
- **Publication record:** the run populates
  `packaging/rc_record.json` (schema `slaif-rc-record-v2`) from verified
  facts only; the record and the regenerated provenance manifest commit
  afterward. A later human-approved final release can reference the SAME
  tested digest without rebuilding or changing embedded labels; promotion
  is a separate later act and is NOT authorized by this machinery.
- **Qualification:** the `docker-published` CI job consumes the RC
  record, authenticates privately, verifies the registry digest, the
  source/wheel/peer/topology labels and configuration identities, and
  exercises the existing signed-ingress / fail-closed / readiness /
  no-build / teardown assertions on the PULLED digest on disposable CI.
  Before the prepublication gate it records a READ-ONLY authenticated
  registry baseline with the same ephemeral `packages: read` token (the
  existing strict resolver: `digest` / verified-`absent` /
  `unauthorized` — inaccessible is never reported as absent) for the
  historical `0.1.0`, the two recorded `sha-` tags, and `0.1.0-rc1`, so a
  source round yields the before state and a published round the after
  evidence (order 013-l, L3); the GHCR package visibility is read via
  the DIRECT container-package endpoint with the same token and an
  explicit supported GitHub API version (the legacy org package-list
  endpoint targets the legacy docker registry and its empty list cannot
  establish GHCR visibility) — the visibility is recorded when the
  package object is returned, otherwise the exact nonsecret status is
  recorded as a limitation (order 013-m, M3). Before an RC exists the
  qualification
  itself reports the explicit pre-publication NOT RUN state; an invalid
  record or an inaccessible recorded image FAILS (it never silently
  skips).
- No other artifact is published by this repository (no PyPI, no sdist
  publication). Publication-adjacent acts remain separate
  human-authorized/strategic acts: any final Git tag, any GitHub Release,
  package visibility, and the protected-host cutover
  (see [the cutover/runbook boundary](RELEASE-CUTOVER-RUNBOOK.md)).

## Gateway compatibility authority (frozen for 0.1.0)

The 0.1.0 **release compatibility authority** is FROZEN at Gateway
`08ca421bee1ddca62078302b910e8be88cf705be`
(`ulfe-lmi/slaif-api-gateway`, `local-coding-v1` module_version 2 with
`process_local_inclusive_horizon_fail_closed`, client module
`codex-0149-responses-v1` module_version 4). Evidence: the strict Local
gateway-contract gate passed 18/18 at that pin (CI run `35208071525` and
the 013-c local re-run, network guard enabled), and the contract surface
is blob-identical (GitHub blob SHAs) across all pins
(`1fccaa746df6cd44f1ddf8c2ec5cf6ea9f18b1cb`,
`08ca421bee1ddca62078302b910e8be88cf705be`, and
`2b61312e0eb569aa7c6f953f52e35b44e84b91c1` — the 16-commit 2026-09-17
drift to `2b61312e0eb569aa7c6f953f52e35b44e84b91c1` changes no contract
file).

The CI fixture (`tests/fixtures/gateway/current_peer_authority.json`,
`purpose: current_ci_compatibility_authority`) is a development
COMPATIBILITY-TRACKING pin: it may follow Gateway `main` through separate,
deliberately re-qualified re-pin objectives (the 012-a precedent). That
tracking never changes the frozen release authority, never requires any
re-release or re-publication of 0.1.0, and no 013-d work re-pins it to
`2b61312e0eb569aa7c6f953f52e35b44e84b91c1` (or any other Gateway `main`
revision). The frozen value is bound in the Dockerfile
`SLAIF_GATEWAY_PEER_SHA` ARG default, the in-image
`slaif-local-coding.gateway.peer.sha` label, and the provenance manifest
`gateway_peer.commit` in every manifest state. Order 013-i re-confirms
this pin for the RC candidate: Gateway `main` has moved past the frozen
commit, but the CURRENT `main` is NOT the frozen compatibility
authority; the RC is contract-tested against the pinned peer, and
support beyond that pin is not claimed until a separate deliberate
re-qualification occurs. No 013-i work re-pins the fixture.

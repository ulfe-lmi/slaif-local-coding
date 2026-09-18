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
  `ghcr.io/ulfe-lmi/slaif-local-coding` with tags `0.1.0` and `sha-<full
  image-source SHA>` — publication PENDING as of this PR's head, order
  013-a R18 Gateway-peer hold; local qualification/development tag
  `slaif-local-coding:0.1.0-<sha>` via `compose.build.yaml`):** the supported distribution artifact of the
  **Docker deployment path** (the canonical MVP installation path, order
  011-a; pull-based canonical operator path since order 013-a). The image is
  built **from** the supported wheel;
  the runtime stage installs the built wheel non-editable on top of the
  frozen locked dependencies, so the image content law mirrors this
  artifact policy's exclusions (no `oap/`, no `tests/`, no `references/`, no
  `scripts/`, no `.git`, no caches, no placeholder files, no env/secret
  material, no host-specific paths, no credential values — mechanically
  asserted by the `docker` CI job image content scan, the local disposable
  run, and the `docker-published` CI job for the PULLED image). The image is
  bound to the committed artifact: the in-image retained wheel hash must
  equal the provenance-manifest wheel hash (B8/C2). The publication path is
  ACTIVATED (`workflow_dispatch`-only `release-image.yml`; registry
  credential is the workflow `GITHUB_TOKEN` with declared `contents: read`
  + `packages: write` — the documented mechanism for publishing the
  workflow repository's container package per the current GitHub
  Container-registry authentication guidance; no long-lived credential of
  any kind is referenced or introduced) and is executed at the final
  implementation head of this PR (order 013-d); the 013-a round had ended
  on the order's R18 hold (the remote Gateway `main` moved off the pinned
  peer; strategy must inspect and deliberately re-qualify; exact delta in
  the OAP report), resolved by the 013-b re-qualification and the 013-d
  frozen 0.1.0 release compatibility authority (see the "Gateway
  compatibility authority (frozen for 0.1.0)" section below). At
  publication:
  tags `0.1.0` + `sha-<S>` will resolve to one registry digest `D` recorded
  in `packaging/release_record.json` and the schema-v3 manifest (image
  source commit `S`); the Git tag `v0.1.0` will target `S` as the release
  reference (a strategic post-merge act). Publication will be
  registry-only: no protected-host cutover, no real deployment yet
  evidenced.
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
the `published` flag, and the image label set. From schema v3 (order 013-a)
the manifest is state-aware: without the release record it records the
not-yet-published state (null digest, `published: false`,
`released: false`, reserved-reference tag convention); with
`packaging/release_record.json` present it records the published state
(digest `D`, `published: true`, `released: true`, the published
qualification label, the published tag convention) plus a closed top-level
`release` section binding the record's identity facts.

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
the accepted Objective-011 record only. Objective 013 (PR #15) changes
no runtime package bytes and no OCI build input semantics: the wheel
remains `fceadc37...` (byte-identical), and the only OCI build-input deltas
are the parameterized qualification label ARG in the Dockerfile (default
byte-identical to the pre-013 label) and the compose split (pull-based
canonical `compose.yaml` + qualification override `compose.build.yaml`,
mechanically proven equivalent for the closed field set). The MVP 0.1.0
image publication is the `workflow_dispatch`-only release workflow
executed at the final implementation head of this PR (order 013-d), to
`ghcr.io/ulfe-lmi/slaif-local-coding` (human-authorized, registry-only,
order 013-a) with tags `0.1.0` and `sha-<S>` resolving to one digest `D`
recorded in `packaging/release_record.json` (present from the
release-record commit onward) and the schema-v3 manifest (image source
commit `S`). Any future objective that changes runtime package bytes or OCI
build inputs must repeat this gate: cleared rebuild, hash comparison, and
manifest regeneration in the same PR, and a fresh publication round for any
new image.

## Publication

The only registry publication of this PR is the MVP 0.1.0 **OCI image**
publication to GHCR (`ghcr.io/ulfe-lmi/slaif-local-coding`, tags `0.1.0` +
`sha-<S>`, registry-verified single digest), a human-authorized act
executed by the `workflow_dispatch`-only `release-image.yml` at the final
implementation head of this PR (order 013-d); the registry credential is
the workflow `GITHUB_TOKEN` with declared `contents: read` + `packages:
write` — the documented mechanism for publishing the workflow repository's
container package per the current GitHub Container-registry
authentication guidance; no long-lived credential of any kind is
referenced or introduced (the token is scoped to the single workflow run,
loaded only on manual dispatch, never on PR/push/branch events, and never
printed). Correction record (order 013-d): the 013-b "repository
workflow-permission ceiling clamps declared permissions" diagnosis was
wrong — the 013-b run logs show the `GITHUB_TOKEN` was granted `Packages:
write`; the 013-b failure was the unqualified push reference (fixed in
013-c); no repository security setting was ever changed; and the 013-c
repository-secret workaround is withdrawn (its broad PAT secret removed).
For human/CLI (non-workflow) publication, the documented option is a
classic PAT with at least the `write:packages` scope — explicitly NOT the
broad `repo` scope (enable org SSO for the PAT if the org requires it);
fine-grained PATs are not a supported GHCR credential type. No other
artifact is published by this repository (no PyPI, no sdist publication). Further publication-adjacent acts remain
separate human-authorized/strategic acts: the Git tag `v0.1.0` (targets the
image source commit `S`; strategic post-merge act), the GitHub Release
(follows that tag), and the protected-host cutover
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
`slaif-local-coding.gateway.peer.sha` label, and the schema-v3 manifest
`gateway_peer.commit` in every 013-d manifest state.

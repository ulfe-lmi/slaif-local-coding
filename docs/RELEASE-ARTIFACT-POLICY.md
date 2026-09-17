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
- **OCI image (`slaif-local-coding:0.1.0-<sha>` locally; reserved publication
  reference `ghcr.io/ulfe-lmi/slaif-local-coding`):** the supported
  distribution artifact of the **Docker deployment path** (the canonical MVP
  installation path, order 011-a). The image is built **from** the supported
  wheel: the runtime stage installs the built wheel non-editable on top of
  the frozen locked dependencies, so the image content law mirrors this
  artifact policy's exclusions (no `oap/`, no `tests/`, no `references/`, no
  `scripts/`, no `.git`, no caches, no placeholder files, no env/secret
  material, no host-specific paths, no credential values — mechanically
  asserted by the `docker` CI job image content scan and by the local
  disposable run). The image is bound to the committed artifact: the in-image
  retained wheel hash must equal the provenance-manifest wheel hash (B8/C2).
  No image is published by this repository (the publication path is
  documented, not executed); no tag or release state exists.
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
.dockerignore hashes, the cross-referenced wheel hash, the reserved
`image_digest` (null until a human publication), `published: false`, and the
image label set.

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
Gateway peer and regenerates the manifest (`objective: "012-a"`) with no
runtime source byte change: the entry-level diff of the cleared rebuild
proves all 20 wheel runtime files byte-identical to the Objective-011
record (only `dist-info/METADATA` and `dist-info/RECORD` differ); the
artifact bytes changed ONLY because (a) the Objective-012-mandated README
status-row fix is embedded in the wheel `dist-info/METADATA` long
description (`readme = "README.md"`; wheel
`7cede0b8e930463400a40662248a97aae22f75b0512dcd8151d6122a99157166` ->
`fceadc378130dd4ffcc3f75d17b5e098577652914f541245d31247911be23aeb`,
+27 B) and (b) the sdist carries the in-scope `README.md`/`docs/`/`tests/`
text changes (sdist `4ba17680c55c557494593087f4d632abb6a79f0c595ecab08bb2414abc86f5d6`
-> `910b65db8abe331fb1ad0507697c1e089fd9ea4ede2ec1792b7fac5c8f5c1240`);
the only OCI build input that changes is the Dockerfile
`SLAIF_GATEWAY_PEER_SHA` label input; the regenerated Objective-012
manifest is the **only** future cutover authority, and the Objective-011-a
artifact record (wheel `7cede0b8...` / sdist `4ba17680...`) remains the
accepted Objective-011 record only. Nothing is
released: no
registry publication, tag, or release state change; no image is pushed. Any
future objective that changes runtime package bytes or OCI build inputs must
repeat this gate: cleared rebuild, hash comparison, and manifest
regeneration in the same PR.

## Publication

No artifact is published to any registry by this repository. A registry
publication, tag, or release state change is a separate human-authorized act
(see [the cutover/runbook boundary](RELEASE-CUTOVER-RUNBOOK.md)).

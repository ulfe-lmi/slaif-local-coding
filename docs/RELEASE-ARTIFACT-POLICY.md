# Release-artifact policy

A release candidate is identified by its exact Git source, wheel SHA-256 and
OCI digest. Build and qualify the final documentation and code together, then
freeze those identities. See [RC-HANDOFF.md](RC-HANDOFF.md) for retrieval.

## Supported artifacts

| Artifact | Purpose |
| --- | --- |
| Wheel | The single supported Python distributable; runtime package, distribution metadata and licenses. |
| OCI image | The distribution artifact for the primary Docker deployment path, built **from** the supported wheel. |
| sdist | A developer-only source archive; not a supported release artifact. |

For Docker, the runtime stage installs the built wheel non-editable into
`/opt/slaif/venv`, on top of the frozen runtime dependency closure. The build
uses `uv sync --frozen --active` for that explicit environment and installs the
wheel with `--no-deps`. Qualification compares the actual installed distributions
with `uv.lock`, checks the retained wheel hash and verifies the real image
platform as `linux/amd64`.

The wheel contains only `slaif_local_coding/` and distribution metadata/licenses.
The sdist has an explicit allowlist in [pyproject.toml](../pyproject.toml).
Neither artifact may contain OAP state, live evidence, credentials, model weights,
caches, virtual environments, host-specific deployment material or vendored
Gateway code. The runtime image also excludes tests, scripts and source checkouts.
[Dockerfile](../Dockerfile) and [.dockerignore](../.dockerignore) define its
stages and context boundary.

## Reproducible builds

The entire `[build-system].requires` set is pinned:

- `hatchling==1.32.0`
- `packaging==26.3`
- `pathspec==1.1.1`
- `pluggy==1.6.0`
- `tomlkit==0.15.1`
- `trove-classifiers==2026.6.1.19`

The build uses uv `0.12.5` and Python `3.12`; the provenance records the observed
Python patch versions. Base images are pinned by digest. Runtime dependencies
come from the committed `uv.lock` with its recorded SHA-256.

Before freezing a candidate:

1. Finish source, configuration and documentation changes. README is embedded in
   wheel `METADATA`, so even a README diagram changes the wheel identity.
2. Build twice from clean equivalent Git trees with separate output/cache paths.
3. Compare wheel and sdist bytes, inspect their contents and verify a fresh
   non-editable wheel installation.
4. Regenerate provenance and prove its source-input map against the reviewed
   source. A derived-metadata commit may name an ancestor only when all artifact
   input hashes are identical.
5. Require fresh CI, Gateway contract, Docker and operator-session gates before
   publishing the candidate.

Developer commands:

```bash
uv build
uv run --frozen python scripts/artifact_policy_check.py --dist dist --inspect
uv run --frozen python scripts/artifact_policy_check.py --dist dist --install-smoke
```

`scripts/artifact_policy_check.py` checks required/forbidden paths, forbidden
content and runtime-source equality. The installation smoke verifies import,
console entry point and installed paths in a fresh disposable environment.
These checks do not replace the two-clean-build comparison.

## Provenance and self-reference

`packaging/release_provenance_manifest.json` uses
`slaif-release-provenance-v5`. It records artifacts, build environment, source
input hashes, OCI inputs and the frozen Gateway authority. Its states distinguish
an unfrozen candidate, a published RC and a separately approved final release.

After publication, `packaging/rc_record.json` (`slaif-rc-record-v2`) and its human
view `packaging/rc_handoff.md` record the actual source, digest, wheel, toolchain,
lock and template hashes, platform, registry access and publication run.
Prior candidate records are retained under `packaging/releases/`.

These derived records are excluded from artifact inputs to avoid a self-hash
cycle. The source commit used to build the image and the later commit adding
its record are distinct. Their artifact input maps must match exactly.
A record with no digest is not evidence of publication.

## Private RC publication

The manually dispatched [release workflow](../.github/workflows/release-image.yml)
publishes the explicitly selected candidate `0.1.0-rc2` and a
`sha-<full-source-commit>` alias. Both must resolve to one recorded OCI digest.
Tags are mutable aliases; `ghcr.io/ulfe-lmi/slaif-local-coding@sha256:<digest>`
is the immutable consumer identity.

Before any registry write, authenticated checks must prove **both target tags
absent**. Unauthorized, inaccessible, malformed, occupied or unresolved states
stop publication. The publisher rechecks before writes and serializes runs.
A partially completed publication requires review; it is never blindly retried
or allowed to overwrite a frozen identity.

Publication uses an ephemeral workflow token with `packages: write`; pulled-image
qualification uses `packages: read`. The package stays private. External readers
use bounded `read:packages` credentials; public visibility is unnecessary.
The RC publisher cannot write final-looking `0.1.0`, `latest`, `stable` or
`v0.1.0` identities or change package visibility. Existing legacy tags remain
untouched and are not recommended installation targets.

After publication, `docker-published` pulls the recorded digest and verifies
tags, labels, platform, retained wheel, installed dependencies, signed ingress,
readiness failures, container hardening, pull-only deployment and teardown.
Before publication that gate explicitly reports `NOT RUN`; an invalid record
or inaccessible recorded image fails. Authenticated read-only registry checks
also record prior tags and package visibility.

Publication is registry-only. Final public release, final Git tag/GitHub Release,
package visibility changes and protected-host cutover require separate human
authorization. If accepted without product changes, final promotion can reference
the same tested digest without rebuilding. This repository does not implement
or execute the independent external benchmark.

## Gateway compatibility authority (frozen for 0.1.0)

The frozen Gateway authority is
`08ca421bee1ddca62078302b910e8be88cf705be` in
`ulfe-lmi/slaif-api-gateway`: server `local-coding-v1` module version 2,
replay mode `process_local_inclusive_horizon_fail_closed`, and client
`codex-0.149-responses-v1` module version 4.

The Dockerfile label input and provenance bind that exact revision. The
[current CI peer fixture](../tests/fixtures/gateway/current_peer_authority.json)
is a separate development compatibility pin. Updating that fixture requires
review and requalification; it does not silently change a frozen artifact's
compatibility authority or claim support for arbitrary Gateway revisions.
Historical artifact identities and qualification records remain available via
[HISTORY.md](HISTORY.md).

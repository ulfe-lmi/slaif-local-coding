# Docker installation (canonical MVP path, order 011-a; pull-based
# canonical operator path since order 013-a)

This is the operator-facing procedure for the **canonical MVP Docker
installation path** of SLAIF Local Coding. The companion systemd user
service remains a supported **secondary direct-host path** (including the
protected-host cutover path); see [DEPLOYMENT.md](DEPLOYMENT.md).

Security boundary: on the LAN-visible surface the request content traverses
the declared trusted private LAN without TLS. Read
[DOCKER-SECURITY-DELTA.md](DOCKER-SECURITY-DELTA.md) before operating a
non-loopback bind. The canonical compose configuration is the final
Gateway-integrated (signed) configuration; the development variant below is
development-only and is **not production**.

**The released-user path is PULL-BASED**. The canonical pull-based compose
is the canonical operator installation path: the reference
`ghcr.io/ulfe-lmi/slaif-local-coding` carries tags `0.1.0` and `sha-<S>`
(both resolving to one registry digest `D`; `S` is the image source commit,
the commit that the Git tag `v0.1.0` targets as the release reference), and
`D` and `S` are recorded in `packaging/release_record.json` and the
schema-v3 provenance manifest (`oci.image_digest`, `release` section). The
publication (Objective 013, round 013-b) was executed from the final
implementation head of PR #15 after the Gateway peer was re-qualified;
that re-qualified pin, `08ca421…`, is the FROZEN 0.1.0 release
compatibility authority (see the "Gateway compatibility authority (frozen
for 0.1.0)" section of
[RELEASE-ARTIFACT-POLICY.md](RELEASE-ARTIFACT-POLICY.md)). The Git tag `v0.1.0` is a strategic post-merge act; the
GitHub Release follows that tag. Publication is registry-only: the
protected-host cutover is NOT performed by publication and no real
deployment is yet evidenced.

## Prerequisites

- A **Linux host** with Docker Engine and the **Compose v2 plugin**
  (`docker compose version`). No other platform is claimed.
- **The host needs NO Python, NO uv, NO project dependencies, and NO project
  virtualenv on this path**: the runtime is the pulled wheel-based container
  image. The host only provides Docker, the mode-0600 site files, and
  outbound registry pull connectivity.
- The host runs the protected **Qwen/vLLM OpenAI-compatible upstream on the
  same host**, reachable at the documented loopback address (for the MVP
  appliance: `http://127.0.0.1:18020/v1`; for evaluation: a disposable fake
  upstream, e.g. `scripts/fake_upstream_server.py`). The host-loopback Qwen
  hop is the reason the container uses `network_mode: host`.
- Outbound connectivity to the registry **at pull time only**. The runtime
  performs no package downloads.
- The supported bind law (D1): loopback is the default; a non-loopback bind
  is accepted **only** under the full signed ingress mode
  (`service_bearer_signed_identity_v1`), which the final Gateway-integrated
  template carries.

## Image identity

- Published reference: `ghcr.io/ulfe-lmi/slaif-local-coding` with tags
  `0.1.0` and `sha-<full image-source SHA>` (one registry digest `D`,
  recorded in `packaging/release_record.json`; the pull-based canonical
  default is the `0.1.0` tag).
- Exact-reproduction option: the digest-pinned form
  `ghcr.io/ulfe-lmi/slaif-local-coding@sha256:<D>` (see "Digest pinning").
- Local qualification/development tag convention (NOT the released-user
  path, `compose.build.yaml` only): `slaif-local-coding:0.1.0-<sha>` where
  `<sha>` is the short or full reviewed Git SHA.
- The image carries OCI labels (`org.opencontainers.image.source`,
  `.revision`, `.version`, `.created`) and project labels (package version,
  pinned Gateway peer SHA, supported topology mode, qualification status
  `mvp-release-0.1.0` for the published release image,
  `disposable-qualification-only; not released` for local qualification
  builds, and the bound wheel SHA-256). Both base images are pinned by
  immutable digest. The published image's label set is mechanically
  verified by the `docker-published` CI job.

## 1. Obtain the release file set

The pull path needs only `compose.yaml` (the build override
`compose.build.yaml` must NOT be part of the operator project — it is the
qualification/development build path) and the config template:

```bash
git clone --depth 1 --branch <reviewed-tag-or-commit> \
    https://github.com/ulfe-lmi/slaif-local-coding.git
cd slaif-local-coding
```

An equivalent documented file set (just `compose.yaml` plus
`config/adapter.gateway-integrated.template.toml`) is equally valid. The
plain `docker compose` command below loads `compose.yaml` only.

## 2. Instantiate the configuration and environment file

Create a private state directory **outside the repository checkout** and
instantiate the **final Gateway-integrated template**, substituting **only**
the documented placeholders (`__LISTEN_HOST__`, `__UPSTREAM_BASE_URL__`,
`__UPSTREAM_MODEL__`):

```bash
install -d -m 0700 /opt/slaif
umask 077

# Mode-0600 environment file: the THREE DISTINCT secret roles by env name
# only. Values are never written into the repository, the image, the compose
# file, logs, or documentation, and are never recorded.
{
  echo "QWEN3090_API_KEY=<protected upstream credential>"
  echo "SLAIF_ADAPTER_SERVICE_TOKEN=<gateway-to-adapter service credential>"
  echo "SLAIF_ADAPTER_SIGNING_SECRET=<gateway-to-adapter signing secret>"
} > /opt/slaif/adapter.env
chmod 0600 /opt/slaif/adapter.env

# Mode-0600 configuration from the final Gateway-integrated template.
# __LISTEN_HOST__: 127.0.0.1 for the loopback (default) bind; 0.0.0.0 or an
# interface IP for the LAN-visible bind (legal only because this template
# carries the full signed ingress mode).
sed -e 's/__LISTEN_HOST__/127.0.0.1/' \
    -e 's/__UPSTREAM_BASE_URL__/http:\/\/127.0.0.1:18020\/v1/' \
    -e 's/__UPSTREAM_MODEL__/qwen3.8-27b/' \
    config/adapter.gateway-integrated.template.toml \
    > /opt/slaif/adapter.toml
chmod 0600 /opt/slaif/adapter.toml

# The container runs as the fixed non-root user created in the image
# (uid:gid 10001). The read-only mounted configuration must be readable by
# that user: hand the file to 10001:10001 (mode 0600 is preserved; only the
# owner changes). chown requires the host admin (root) — the same account
# that manages Docker on the MVP appliance.
chown 10001:10001 /opt/slaif/adapter.toml
```

## 3. Pull the published image

Pulls the published release image:

```bash
SLAIF_CONFIG_FILE=/opt/slaif/adapter.toml \
SLAIF_ENV_FILE=/opt/slaif/adapter.env \
docker compose pull
```

This pulls `ghcr.io/ulfe-lmi/slaif-local-coding:0.1.0` (the canonical
default reference in `compose.yaml`; no local build occurs — the file
carries no build key).

## 4. Start

```bash
SLAIF_CONFIG_FILE=/opt/slaif/adapter.toml \
SLAIF_ENV_FILE=/opt/slaif/adapter.env \
docker compose up -d
```

The service uses `network_mode: host`, so the adapter binds directly on the
host's port `18031` at the `__LISTEN_HOST__` address; no ports are published.

## 5. Verify readiness (bounded, fail-closed)

The compose healthcheck probes `/readyz` inside the container
(`SLAIF_HEALTH_ENDPOINT`, default `127.0.0.1:18031`): 10 s interval, 5 s
timeout, 12 retries, 30 s start period. Wait for `healthy`:

```bash
docker compose ps                                   # expect health: healthy
docker inspect --format '{{.State.Health.Status}}' slaif-local-coding-adapter-1
```

Because host networking makes the container loopback the host loopback, the
loopback readiness poll also works from the host (equivalent of
`packaging/readyz-wait.sh` for the Docker path):

```bash
packaging/readyz-wait.sh
```

Fail-closed: if the bounded wait elapses, do **not** send traffic. A missing
signing secret yields `/readyz` 503 with `gateway_ingress: "unavailable"`
and an unhealthy container; inspect `docker compose logs adapter` for the
sanitized reason.

## 6. Stop / restart / status

```bash
docker compose stop      # stop
docker compose start     # start
docker compose restart   # restart (then re-verify readiness)
docker compose ps        # status
docker compose logs --tail 100 adapter   # bounded sanitized logs
```

## 7. Upgrade

Pin the NEXT published image tag/digest and recreate — no build on the host:

```bash
export SLAIF_LOCAL_CODING_IMAGE=ghcr.io/ulfe-lmi/slaif-local-coding:<next-tag>
# or the exact-reproduction digest form:
# export SLAIF_LOCAL_CODING_IMAGE=ghcr.io/ulfe-lmi/slaif-local-coding@sha256:<next-D>
SLAIF_LOCAL_CODING_IMAGE="$SLAIF_LOCAL_CODING_IMAGE" \
SLAIF_CONFIG_FILE=/opt/slaif/adapter.toml \
SLAIF_ENV_FILE=/opt/slaif/adapter.env \
docker compose pull
SLAIF_LOCAL_CODING_IMAGE="$SLAIF_LOCAL_CODING_IMAGE" \
SLAIF_CONFIG_FILE=/opt/slaif/adapter.toml \
SLAIF_ENV_FILE=/opt/slaif/adapter.env \
docker compose up -d --force-recreate
docker compose ps       # re-verify readiness: health: healthy
```

The mounted configuration file is byte-unchanged by an upgrade; the tmpfs
derived cache is intentionally wiped on recreate (the cache is disposable by
construction; no persistent cache state is claimed).

## 8. Rollback

Same mechanics with the PREVIOUS image tag/digest:

```bash
export SLAIF_LOCAL_CODING_IMAGE=ghcr.io/ulfe-lmi/slaif-local-coding:<previous-tag-or-digest>
SLAIF_LOCAL_CODING_IMAGE="$SLAIF_LOCAL_CODING_IMAGE" \
SLAIF_CONFIG_FILE=/opt/slaif/adapter.toml \
SLAIF_ENV_FILE=/opt/slaif/adapter.env \
docker compose pull
SLAIF_LOCAL_CODING_IMAGE="$SLAIF_LOCAL_CODING_IMAGE" \
SLAIF_CONFIG_FILE=/opt/slaif/adapter.toml \
SLAIF_ENV_FILE=/opt/slaif/adapter.env \
docker compose up -d --force-recreate
docker compose ps       # re-verify readiness: health: healthy
```

## 9. Cache purge

The derived cache lives on the bounded `/dev/shm` tmpfs; purging is a
container recreate (no persistent cache state exists to purge on disk):

```bash
docker compose down
SLAIF_CONFIG_FILE=/opt/slaif/adapter.toml \
SLAIF_ENV_FILE=/opt/slaif/adapter.env \
docker compose up -d
```

## 10. Uninstall

Nothing is persistent by design:

```bash
docker compose down --remove-orphans
# Remove the pulled release image(s) from the local registry cache:
docker image rm ghcr.io/ulfe-lmi/slaif-local-coding:0.1.0 2>/dev/null || true
rm /opt/slaif/adapter.toml /opt/slaif/adapter.env   # only if not explicitly retained
```

Uninstalling must never touch the protected upstream model service, the
Gateway, firewall/VPN/network state, or any Codex profile.

## Digest pinning (exact reproduction)

`compose.yaml` renders `SLAIF_LOCAL_CODING_IMAGE` verbatim, so the
digest-pinned form is a first-class reference:

```bash
export SLAIF_LOCAL_CODING_IMAGE=ghcr.io/ulfe-lmi/slaif-local-coding@sha256:<D>
docker compose pull && docker compose up -d --force-recreate
```

`<D>` is the published registry digest recorded in
`packaging/release_record.json` (`oci_image_digest`) and the schema-v3
provenance manifest (`oci.image_digest`). A digest-pinned
pull can never silently move to different image content.

## Build-from-source (QUALIFICATION/DEVELOPMENT path — NOT the released-user path)

Building the image locally (Dockerfile, `uv`-locked wheel) is the
**qualification/development** path used by CI (`docker` job), the release
workflow (which built and published the reviewed `0.1.0` image), and local
development. It is clearly **NOT** the released-user path and requires the
build chain (Docker build, `uv` in the build stage only). With the two-file
compose:

```bash
export SLAIF_GIT_SHA=<short-sha-of-reviewed-commit>
export SLAIF_WHEEL_SHA256=<wheel sha256 from packaging/release_provenance_manifest.json>
docker compose -f compose.yaml -f compose.build.yaml build
SLAIF_GIT_SHA="$SLAIF_GIT_SHA" \
SLAIF_WHEEL_SHA256="$SLAIF_WHEEL_SHA256" \
SLAIF_CONFIG_FILE=/opt/slaif/adapter.toml \
SLAIF_ENV_FILE=/opt/slaif/adapter.env \
docker compose -f compose.yaml -f compose.build.yaml up -d
```

The build override does NOT set the `SLAIF_QUALIFICATION_LABEL` ARG, so
every local qualification build carries the label
`disposable-qualification-only; not released`. The merged two-file spec is
mechanically asserted to equal the pre-013 single-file effective adapter
spec for the closed field set (CI `docker` job, phase
`compose_merge_equivalence`).

## Connecting the SLAIF API Gateway

The Gateway (separate repository) connects by **configuration only** — no
Gateway source change:

- point the Codex provider route backend `base_url` at the adapter endpoint
  (loopback co-located: `http://127.0.0.1:18031/v1`; bridge-container
  Gateway: the host bridge interface IP, e.g. `http://172.17.0.1:18031/v1`;
  LAN-different-host Gateway/client: the host LAN interface IP at port
  `18031`);
- the Gateway route carries the service credential and the signing secret by
  environment name on the Gateway side and emits the signed identity v1
  contract (continuously tested by the `gateway-contract` CI against the
  pinned peer);
- the three Local-side secret roles (step 2) are the Local-side names for the
  same contract.

## Direct client access (honesty note)

Plain Codex/OpenAI clients cannot mint signed identity requests. The
documented MVP client path is **Codex → SLAIF API Gateway → adapter**.
Direct unsigned client access to the adapter exists only in the loopback
development mode (ingress disabled) and is labeled as such below.

## Development variant (development only, not production)

For local development without a Gateway, the separately labeled development
template `config/adapter.deployment.template.toml` (ingress **disabled**,
loopback bind, static identity) may be used with the same compose file after
instantiating that template instead — this is a **development variant, not
production**: it is never labeled production, it must not be exposed beyond
loopback, and it carries no Gateway signed identity. The canonical compose
path always uses the final Gateway-integrated (signed) configuration.

## Publication and provenance (registry-only)

- The release image is published exclusively by the activated
  `.github/workflows/release-image.yml` (`workflow_dispatch`-only; registry
  credential is the workflow `GITHUB_TOKEN` with declared `contents: read`
  + `packages: write` — the documented mechanism for publishing the
  workflow repository's container package; no long-lived credential of any
  kind is referenced or introduced) — executed at the final implementation
  head of this PR (order 013-d): it builds the locked wheel,
  binds its SHA-256 to the committed manifest, builds the image from the
  dispatched commit `S` via the two-file compose with the
  `mvp-release-0.1.0` qualification label, pushes
  `ghcr.io/ulfe-lmi/slaif-local-coding:sha-<S>` unconditionally (content-
  addressed), pushes `:0.1.0` only if the registry proves the tag absent or
  already at the same digest (a pre-existing different digest fails the
  run), and registry-verifies that both tags resolve to one digest `D`.
- At publication, the release record (`packaging/release_record.json`,
  schema `slaif-release-record-v1`; not present in this PR's tree) and the
  schema-v3 provenance manifest bind `S` (image source commit, git-tag
  target, OCI revision label), `D` (OCI digest), the release tags, the
  byte-identical wheel
  (`fceadc378130dd4ffcc3f75d17b5e098577652914f541245d31247911be23aeb`), and
  the pinned Gateway peer.
- The Git tag `v0.1.0` targets `S` as the release reference (created by
  strategy post-merge — it does not exist at the time this document is
  written); the GitHub Release follows that tag.
- Publication is **registry-only**: no protected-host cutover, no real
  deployment yet evidenced. Once published, the image is continuously
  CI-verified by the `docker-published` job (pull by digest and by both
  tags, exact OCI label set, full signed-ingress contract against a
  disposable fake upstream, no-build proof, teardown absence proof); the
  job is gated on the release record and skips with an explicit line until
  publication.
- The repository is public, so once the package is published, anonymous
  GHCR pull is available to released users and to CI.

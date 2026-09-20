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
is the canonical operator installation path for the reference
`ghcr.io/ulfe-lmi/slaif-local-coding`: the image source commit `S` and the
authoritative registry digest `D` are recorded in the RC artifact record
(`packaging/rc_record.json`, schema `slaif-rc-record-v2`) and the
provenance manifest once the RC is published; the RC tag pair is
`0.1.0-rc2` (explicit candidate) + `sha-<S>` (source alias tag — a mutable
tag naming the image source commit, not a content-addressed identity).
The frozen Gateway compatibility authority is the peer
`08ca421bee1ddca62078302b910e8be88cf705be` (see the "Gateway compatibility
authority (frozen for 0.1.0)" section of
[RELEASE-ARTIFACT-POLICY.md](RELEASE-ARTIFACT-POLICY.md)). Historical
(unmistakably historical, not a current release claim): rounds
013-b..013-g of Objective 013 pushed the private tags `0.1.0` and
`sha-<S>` to the **non-public** package at one digest; that output was
never published to users, is legacy, is NOT the RC benchmark target, and
must not be pulled or reused. The RC publication is a separate later round
bound to the exact reviewed source commit; a final public release (Git tag
`v0.1.0`, GitHub Release) is a separate later human-authorized act.
Publication is registry-only: the protected-host cutover is NOT performed
by publication and no real deployment is yet evidenced.

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
- **Bounded read-only GHCR credentials** for the private image package:
  the EXTERNAL reader scope is `read:packages` (a classic PAT with package
  read access for this package — distinct from the Actions YAML
  `packages: read` keyword); password-stdin, bounded read-only access, no
  request to make the package public.
- Outbound connectivity to the registry **at pull time only**. The runtime
  performs no package downloads.
- The supported bind law (D1): loopback is the default; a non-loopback bind
  is accepted **only** under the full signed ingress mode
  (`service_bearer_signed_identity_v1`), which the final Gateway-integrated
  template carries.

## Image identity

- Explicit selection: `SLAIF_LOCAL_CODING_IMAGE` (REQUIRED by
  `compose.yaml`) set to `ghcr.io/ulfe-lmi/slaif-local-coding:0.1.0-rc2`
  (RC candidate tag alias) or the authoritative digest form
  `ghcr.io/ulfe-lmi/slaif-local-coding@sha256:<D>` once the RC record
  exists (see "Digest pinning"). The historical private `0.1.0` tag is
  never selected by any documented path.
- Local qualification/development tag convention (NOT the released-user
  path, `compose.build.yaml` only): `slaif-local-coding:0.1.0-<sha>` where
  `<sha>` is the short or full reviewed Git SHA.
- The image carries OCI labels (`org.opencontainers.image.source`,
  `.revision`, `.version`, `.created`) and project labels (package version,
  pinned Gateway peer SHA, supported topology mode, qualification status —
  the RC candidate label for the RC image,
  `disposable-qualification-only; not released` for local qualification
  builds, and the bound wheel SHA-256). Both base images are pinned by
  immutable digest. The published image's label set is mechanically
  verified by the `docker-published` CI job (private, authenticated).
- **Digest verification (when pulling by tag):** inspecting the image
  `.Id` alone is NOT proof of the manifest digest. Verify the actual
  registry/OCI digest via `RepoDigests` (the registry manifest digest
  recorded by the pull) — it must contain
  `ghcr.io/ulfe-lmi/slaif-local-coding@sha256:<D>`:

  ```bash
  docker image inspect "ghcr.io/ulfe-lmi/slaif-local-coding:0.1.0-rc2" \
    --format '{{range .RepoDigests}}{{.}}{{end}}'
  ```
- **Supported image OS/architecture:** the image is a Linux multi-stage
  Docker build; the digest-pinned base images carry a multi-architecture
  OCI index, but the RC candidate image is built and qualified on
  `linux/amd64` only — other architectures are not qualified for this
  release.

## Supported platforms (repeated for clarity)

- **Linux host** (`linux/amd64` is the qualified architecture) with
  Docker Engine and the **Compose v2 plugin** (`docker compose version`);
- **Bounded read-only GHCR credentials**: the EXTERNAL reader scope is
  `read:packages` (a classic PAT with package read access for this
  package — distinct from the Actions YAML `packages: read` keyword used
  by this repository's CI); credentials are supplied by password-stdin and
  the access is bounded and read-only (no request to make the package
  public).

## 1. Obtain the release file set

The pull path needs only `compose.yaml` (the build override
`compose.build.yaml` must NOT be part of the operator project — it is the
qualification/development build path) and the config template:

```bash
git clone https://github.com/ulfe-lmi/slaif-local-coding.git
cd slaif-local-coding
git fetch --depth 1 origin <IMAGE_SOURCE_COMMIT>
git checkout --detach FETCH_HEAD
```

`<IMAGE_SOURCE_COMMIT>` is the exact image source commit recorded in the
RC artifact record (see [RC-HANDOFF.md](RC-HANDOFF.md)). An equivalent
documented file set (just `compose.yaml` plus
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

## 3. Set the operator session variables (once)

Every Compose command in this procedure — `pull`, `up`, `ps`, `logs`,
`stop`, `start`, `restart`, `down`, upgrade, rollback — runs in this same
shell with the SAME three exported variables, so no later command ever
resolves a missing or wrong default:

```bash
export SLAIF_LOCAL_CODING_IMAGE=ghcr.io/ulfe-lmi/slaif-local-coding@sha256:<D>
export SLAIF_CONFIG_FILE=/opt/slaif/adapter.toml
export SLAIF_ENV_FILE=/opt/slaif/adapter.env
```

(`SLAIF_LOCAL_CODING_IMAGE` digest form preferred; the tag form is
accepted — see "Image identity". The compose file fails closed when any of
the required variables is absent.)

## 4. Pull the selected image

```bash
docker compose pull
```

This pulls the EXPLICITLY selected reference (digest preferred; tag form
accepted — see "Image identity"); no local build occurs (the file carries
no build key). The private package requires registry login first
(QUICKSTART.md step 3; stdin credentials only).

## 5. Start

```bash
docker compose up -d
```

The service uses `network_mode: host`, so the adapter binds directly on the
host's port `18031` at the `__LISTEN_HOST__` address; no ports are published.

## 6. Verify readiness (bounded, fail-closed)

The compose healthcheck probes `/readyz` inside the container
(`SLAIF_HEALTH_ENDPOINT`, default `127.0.0.1:18031`): 10 s interval, 5 s
timeout, 12 retries, 30 s start period. Wait for `healthy`:

```bash
docker compose ps                                   # expect health: healthy
docker inspect --format '{{.State.Health.Status}}' slaif-local-coding-adapter-1
```

The minimal compose+config retrieval path is self-contained: the bounded
wait below uses only Docker (the compose healthcheck already probes
`/readyz` inside the container), so no extra repository file or `curl`
prerequisite is required:

```bash
STATE=""
for i in $(seq 1 36); do
  STATE="$(docker inspect --format '{{.State.Health.Status}}' slaif-local-coding-adapter-1 2>/dev/null || true)"
  [ "$STATE" = "healthy" ] && break
  sleep 5
done
[ "$STATE" = "healthy" ] || { echo "readyz: not healthy within the bounded wait — fail closed" >&2; exit 1; }
```

Fail-closed: if the bounded wait elapses, do **not** send traffic. A missing
signing secret yields `/readyz` 503 with `gateway_ingress: "unavailable"`
and an unhealthy container; inspect `docker compose logs adapter` for the
sanitized reason.

## 7. Stop / restart / status

```bash
docker compose stop      # stop
docker compose start     # start
docker compose restart   # restart (then re-verify readiness)
docker compose ps        # status
docker compose logs --tail 100 adapter   # bounded sanitized logs
```

## 8. Upgrade

Pin the NEXT published image tag/digest and recreate — no build on the host:

```bash
export SLAIF_LOCAL_CODING_IMAGE=ghcr.io/ulfe-lmi/slaif-local-coding:<next-tag>
# or the exact-reproduction digest form:
# export SLAIF_LOCAL_CODING_IMAGE=ghcr.io/ulfe-lmi/slaif-local-coding@sha256:<next-D>
docker compose pull
docker compose up -d --force-recreate
docker compose ps       # re-verify readiness: health: healthy
```

The mounted configuration file is byte-unchanged by an upgrade; the tmpfs
derived cache is intentionally wiped on recreate (the cache is disposable by
construction; no persistent cache state is claimed).

## 9. Rollback

Same mechanics with the PREVIOUS image tag/digest:

```bash
export SLAIF_LOCAL_CODING_IMAGE=ghcr.io/ulfe-lmi/slaif-local-coding:<previous-tag-or-digest>
docker compose pull
docker compose up -d --force-recreate
docker compose ps       # re-verify readiness: health: healthy
```

## 10. Cache purge

The derived cache lives on the bounded `/dev/shm` tmpfs; purging is a
container recreate (no persistent cache state exists to purge on disk):

```bash
docker compose down
docker compose up -d
```

## 11. Uninstall

Nothing is persistent by design:

```bash
docker compose down --remove-orphans
# Remove the pulled image(s) from the local registry cache:
docker image rm "ghcr.io/ulfe-lmi/slaif-local-coding@sha256:<D>" 2>/dev/null || true
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

`<D>` is the authoritative registry digest recorded in
`packaging/rc_record.json` (`oci_image_digest`) and the provenance
manifest (`oci.image_digest`) for the RC, or in
`packaging/release_record.json` for a later final release. A
digest-pinned pull can never silently move to different image content.

## Build-from-source (QUALIFICATION/DEVELOPMENT path — NOT the released-user path)

Building the image locally (Dockerfile, `uv`-locked wheel) is the
**qualification/development** path used by CI (`docker` job), the release
workflow (which builds and publishes the reviewed RC candidate image; its
historical Objective-013 round built the private `0.1.0` image), and local
development. It is clearly **NOT** the released-user path and requires the
build chain (Docker build, `uv` in the build stage only). With the two-file
compose:

```bash
export SLAIF_GIT_SHA=<short-sha-of-reviewed-commit>
export SLAIF_WHEEL_SHA256=<wheel sha256 from packaging/release_provenance_manifest.json>
export SLAIF_LOCAL_CODING_IMAGE=slaif-local-coding:0.1.0-"$SLAIF_GIT_SHA"
docker compose -f compose.yaml -f compose.build.yaml build
SLAIF_GIT_SHA="$SLAIF_GIT_SHA" \
SLAIF_WHEEL_SHA256="$SLAIF_WHEEL_SHA256" \
SLAIF_CONFIG_FILE=/opt/slaif/adapter.toml \
SLAIF_ENV_FILE=/opt/slaif/adapter.env \
docker compose -f compose.yaml -f compose.build.yaml up -d
```

Compose interpolates each file before merging, so `compose.yaml` requires
`SLAIF_LOCAL_CODING_IMAGE` on this two-file path too (it fails closed when
absent): the export above supplies the nonsecret build selection, and the
build override's image field is what is actually built and tagged.

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

## Publication and provenance (registry-only, RC candidate)

- The RC image is published exclusively by the activated
  `.github/workflows/release-image.yml` (`workflow_dispatch`-only; registry
  credential is the workflow `GITHUB_TOKEN` with declared `contents: read`
  + `packages: write` — the documented mechanism for publishing the
  workflow repository's container package; no long-lived credential of any
  kind is referenced or introduced). The publication round builds the
  locked wheel, binds its SHA-256 to the committed manifest, builds the
  image from the exact dispatched source commit `S` via the two-file
  compose with the RC candidate qualification label, and pushes the
  explicit candidate identity:
  `ghcr.io/ulfe-lmi/slaif-local-coding:sha-<S>` (source ALIAS tag naming
  the full image-source commit — mutable; the content-addressed identity
  is the immutable digest `D`) and `:0.1.0-rc2` (the EXACT expected RC
  identity; the publisher never silently allocates a new RC number).
  Before ANY mutation both target tags are checked with authenticated
  registry access (verified-absent vs unauthorized/inaccessible
  distinguished; any reported digest must be well-formed), and
  VERIFIED-ABSENT-FOR-BOTH is the ONLY write precondition: if EITHER tag
  is occupied, unauthorized/inaccessible, malformed, or unresolved, the
  run stops BEFORE ANY registry mutation, reports the existing digests
  for strategy adjudication, and never repushes or rebuilds an already
  frozen identity (a crash between the two pushes leaves a partial state
  that is reported, never silently completed). The target state is
  rechecked immediately before each write, and publication runs are
  serialized by the workflow concurrency group (an in-progress publisher
  is never cancelled). No code path may write `0.1.0`, `latest`,
  `stable`, a final `v0.1.0`, or change package visibility. The
  historical private `0.1.0` and orphan `sha-` tags are preserved
  byte-for-byte.
- At publication, the RC record (`packaging/rc_record.json`, schema
  `slaif-rc-record-v2`) and the provenance manifest bind `S` (image source
  commit, OCI revision label), `D` (authenticated registry digest,
  authoritative identity), the publishing run head SHA, the RC tag pair,
  the wheel SHA-256, the dependency-lock hash, the frozen Gateway
  authority, the full pinned build environment and toolchain, the
  digest-pinned base images, the supported image platform, and the DIRECT
  path->hash source-input map (config templates, compose identity,
  packaging inputs); the deterministically rendered human-readable
  handoff (`packaging/rc_handoff.md`) is generated from that same machine
  record. The record keeps `final_public_release: false` and
  `cutover_performed: false`.
- A later human-approved final release references the SAME tested digest
  without rebuilding or changing embedded labels; any final Git tag and
  GitHub Release are separate later acts.
- Publication is **registry-only**: no protected-host cutover, no real
  deployment yet evidenced. Once the RC exists, the image is continuously
  CI-verified by the `docker-published` job (private authenticated pull by
  digest and by both tags, exact OCI label set, full signed-ingress
  contract against a disposable fake upstream, no-build proof, teardown
  absence proof); the job reports the explicit pre-publication NOT RUN
  state until the RC record exists, and an invalid record or inaccessible
  image FAILS.
- The package is **private**: pull requires bounded read-only registry
  credentials (the `docker-published` CI job uses least-privilege
  `packages: read`); anonymous pull is not a prerequisite and no
  visibility change is requested.

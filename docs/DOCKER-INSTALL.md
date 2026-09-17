# Docker installation (canonical MVP path, order 011-a)

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

## Prerequisites

- A **Linux host** with Docker Engine and the **Compose v2 plugin**
  (`docker compose version`). No other platform is claimed.
- The host runs the protected **Qwen/vLLM OpenAI-compatible upstream on the
  same host**, reachable at the documented loopback address (for the MVP
  appliance: `http://127.0.0.1:18020/v1`; for evaluation: a disposable fake
  upstream, e.g. `scripts/fake_upstream_server.py`). The host-loopback Qwen
  hop is the reason the container uses `network_mode: host`.
- Outbound connectivity **at build time only** (base image pulls and the
  locked build-backend resolution). The runtime performs no package
  downloads.
- The host **never needs Python, uv, project dependencies, or a project
  virtualenv**: the runtime is the wheel-based container image.
- The supported bind law (D1): loopback is the default; a non-loopback bind
  is accepted **only** under the full signed ingress mode
  (`service_bearer_signed_identity_v1`), which the final Gateway-integrated
  template carries.

## Image identity

- Local tag convention (deterministic): `slaif-local-coding:0.1.0-<sha>`
  where `<sha>` is the short or full reviewed Git SHA
  (`slaif-local-coding:0.1.0-<short-sha>` is the documented form).
- Reserved publication reference (future human release only, **no push in
  this objective**): `ghcr.io/ulfe-lmi/slaif-local-coding`.
- The image carries OCI labels (`org.opencontainers.image.source`,
  `.revision`, `.version`, `.created`) and project labels (package version,
  pinned Gateway peer SHA, supported topology mode, qualification status
  `disposable-qualification-only; not released`, and the bound wheel
  SHA-256). Both base images are pinned by immutable digest.

## 1. Obtain the reviewed commit

```bash
git clone https://github.com/ulfe-lmi/slaif-local-coding.git
cd slaif-local-coding
git checkout <reviewed-commit-sha>
```

## 2. Build the image

Set the image identity from the reviewed commit and the committed
provenance manifest (`packaging/release_provenance_manifest.json`,
`artifacts.wheel.sha256`) so the image is bound to the committed artifact:

```bash
export SLAIF_GIT_SHA=<short-sha-of-reviewed-commit>
export SLAIF_WHEEL_SHA256=<wheel sha256 from the provenance manifest>
docker compose build
```

(Or pull the published image after a human release; see "Container
publication (documented, not executed)" at the end of this document.)

## 3. Instantiate the configuration and environment file

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

## 4. Start

```bash
SLAIF_GIT_SHA="$SLAIF_GIT_SHA" \
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

Check out the new reviewed commit, rebuild under the new tag, and recreate:

```bash
git checkout <new-reviewed-sha>
export SLAIF_GIT_SHA=<new-short-sha>
export SLAIF_WHEEL_SHA256=<new wheel sha256 from the new provenance manifest>
docker compose build
SLAIF_GIT_SHA="$SLAIF_GIT_SHA" \
SLAIF_CONFIG_FILE=/opt/slaif/adapter.toml \
SLAIF_ENV_FILE=/opt/slaif/adapter.env \
docker compose up -d --force-recreate
docker compose ps       # re-verify readiness: health: healthy
```

The mounted configuration file is byte-unchanged by an upgrade; the tmpfs
derived cache is intentionally wiped on recreate (the cache is disposable by
construction; no persistent cache state is claimed).

## 8. Rollback

Same mechanics with the previous reviewed tag:

```bash
export SLAIF_GIT_SHA=<previous-short-sha>
SLAIF_GIT_SHA="$SLAIF_GIT_SHA" \
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
SLAIF_GIT_SHA="$SLAIF_GIT_SHA" \
SLAIF_CONFIG_FILE=/opt/slaif/adapter.toml \
SLAIF_ENV_FILE=/opt/slaif/adapter.env \
docker compose up -d
```

## 10. Uninstall

Nothing is persistent by design:

```bash
docker compose down --remove-orphans
docker image rm slaif-local-coding:0.1.0-"$SLAIF_GIT_SHA"
rm /opt/slaif/adapter.toml /opt/slaif/adapter.env   # only if not explicitly retained
```

Uninstalling must never touch the protected upstream model service, the
Gateway, firewall/VPN/network state, or any Codex profile.

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
- the three Local-side secret roles (step 3) are the Local-side names for the
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

## Container publication (documented, not executed)

No image is pushed by this objective. The future human-authorized
publication procedure is:

1. build the reviewed image (`docker compose build`, step 2);
2. authenticate to the registry and push with the documented tags:
   `ghcr.io/ulfe-lmi/slaif-local-coding:0.1.0` and
   `ghcr.io/ulfe-lmi/slaif-local-coding:sha-<full-sha>`;
3. capture the pushed image digest;
4. a later human-authorized release order fills
   `oci.image_digest` in `packaging/release_provenance_manifest.json` and
   flips `oci.published` to `true` (manifest regeneration discipline of
   objectives 009/010/011).

The committed `.github/workflows/release-image.yml` is inert:
`workflow_dispatch`-only, declares `packages: write`, has no secrets
configured, and cannot run on PRs/pushes. It exists only as the reviewed
publication path and is not executed by this objective.

# Installation

SLAIF Local Coding has one primary and one secondary supported installation
path:

1. **Docker (primary, canonical operator path)** — pull the published
   container image and run it with Compose on a Linux host. The host needs
   no Python toolchain and no local build.
2. **Direct-host systemd user service (secondary, advanced)** — run the
   adapter from a repository virtual environment on the same host. This
   path has its own Python 3.12 + uv requirements, documented in the
   advanced section below; it is clearly distinct from the Docker path.

Both paths serve the same runtime under the same configuration law:
loopback bind by default; a non-loopback bind only under the full
signed-ingress contract; credentials only via a mode-0600 environment file
referenced by name.

## Supported platforms and prerequisites (Docker path)

- **Linux host (`linux/amd64`)** with Docker Engine and the **Compose v2
  plugin** (`docker compose version`). `linux/amd64` is the built and
  qualified image architecture; no other platform or architecture is
  claimed.
- A **private OpenAI-compatible model server** (Qwen/vLLM) running on this
  host at its documented loopback address (MVP appliance default:
  `http://127.0.0.1:18020/v1`, model `qwen3.8-27b`). The container uses
  `network_mode: host` so this hop stays true host loopback.
- The **separate SLAIF API Gateway** deployed for public access. The
  Compose project installs **only the adapter container**: it does not
  install model weights and it does not install or configure the Gateway.
- **Bounded read-only GHCR credentials** for the private image package:
  the EXTERNAL reader scope is `read:packages` (a classic PAT with package
  read access for this package — distinct from the Actions YAML
  `packages: read` keyword), supplied via password-stdin with bounded
  read-only access. No request to make the package public is required or
  made.
- A **host admin account** (root or sudo-authorized) for the two
  `/opt/slaif` file-ownership steps in section 3.
- Outbound connectivity to the registry **at pull time only**; the runtime
  performs no package downloads.

## 1. Obtain the exact matching files at the recorded source commit

The RC artifact record (see [docs/RC-HANDOFF.md](docs/RC-HANDOFF.md))
records the exact image source commit the image was built from. Obtain
`compose.yaml` and the configuration template at that commit:

```bash
git clone https://github.com/ulfe-lmi/slaif-local-coding.git
cd slaif-local-coding
git fetch --depth 1 origin <IMAGE_SOURCE_COMMIT>
git checkout --detach FETCH_HEAD
```

An equivalent documented file set (just `compose.yaml` plus
`config/adapter.gateway-integrated.template.toml`) is equally valid. The
build override `compose.build.yaml` is the qualification/development build
path and must NOT be part of the operator project.

## 2. Select the image: tag vs immutable digest

- **Digest (preferred):**
  `ghcr.io/ulfe-lmi/slaif-local-coding@sha256:<OCI_IMAGE_DIGEST>` — the
  authoritative identity from the RC artifact record; a digest-pinned pull
  can never silently move to different image content.
- **Tag (alias):** `ghcr.io/ulfe-lmi/slaif-local-coding:0.1.0-rc1` —
  convenient, but tags are mutable aliases; verify after the pull that the
  tag resolves to the recorded registry digest (section 4).
- **Never** the historical private `0.1.0` tag: it is legacy Objective-013
  output that was never published to users and is NOT the RC benchmark
  target.

## 3. Prepare protected config/env files (host admin)

Creating files under `/opt` requires the host admin account (root or
sudo-authorized). Run this section as the admin or prefix with `sudo`:

```bash
install -d -m 0700 /opt/slaif
umask 077

# Fail clearly when a required secret is unset or empty in this shell
# (values come from your protected store and are never written into the
# repository, the image, the compose file, logs, or documentation):
: "${QWEN3090_API_KEY:?set QWEN3090_API_KEY in this shell from your protected store before creating the env file}"
: "${SLAIF_ADAPTER_SERVICE_TOKEN:?set SLAIF_ADAPTER_SERVICE_TOKEN in this shell from your protected store before creating the env file}"
: "${SLAIF_ADAPTER_SIGNING_SECRET:?set SLAIF_ADAPTER_SIGNING_SECRET in this shell from your protected store before creating the env file}"

# Mode-0600 environment file: the THREE DISTINCT secret roles by env name:
printf 'QWEN3090_API_KEY=%s\nSLAIF_ADAPTER_SERVICE_TOKEN=%s\nSLAIF_ADAPTER_SIGNING_SECRET=%s\n' \
  "$QWEN3090_API_KEY" "$SLAIF_ADAPTER_SERVICE_TOKEN" "$SLAIF_ADAPTER_SIGNING_SECRET" \
  > /opt/slaif/adapter.env
chmod 0600 /opt/slaif/adapter.env

# Mode-0600 configuration from the final Gateway-integrated template
# (substitute ONLY the documented placeholders, no other manual editing):
sed -e 's/__LISTEN_HOST__/127.0.0.1/' \
    -e 's/__UPSTREAM_BASE_URL__/http:\/\/127.0.0.1:18020\/v1/' \
    -e 's/__UPSTREAM_MODEL__/qwen3.8-27b/' \
    config/adapter.gateway-integrated.template.toml \
    > /opt/slaif/adapter.toml
chmod 0600 /opt/slaif/adapter.toml

# Non-root container config readability: the image runs as the fixed
# non-root user 10001:10001. The read-only mounted configuration must be
# readable by that user: hand the file to 10001:10001 (mode 0600 is
# preserved; only the owner changes). chown requires the host admin (the
# same account that manages Docker):
chown 10001:10001 /opt/slaif/adapter.toml
```

`__LISTEN_HOST__` is `127.0.0.1` for the default loopback bind; set an
interface address only when operating the LAN-visible bind, which is legal
only because the Gateway-integrated template carries the full signed
ingress contract (read [docs/DOCKER-SECURITY-DELTA.md](docs/DOCKER-SECURITY-DELTA.md)
first).

## 4. Set the operator session variables, pull, and verify identity

Every Compose command in this document — `pull`, `up`, `ps`, `logs`,
`stop`, `start`, `restart`, `down`, upgrade, rollback — runs in this same
shell with the SAME three exported variables, so no later command ever
resolves a missing or wrong default:

```bash
export SLAIF_LOCAL_CODING_IMAGE=ghcr.io/ulfe-lmi/slaif-local-coding@sha256:<OCI_IMAGE_DIGEST>
export SLAIF_CONFIG_FILE=/opt/slaif/adapter.toml
export SLAIF_ENV_FILE=/opt/slaif/adapter.env
```

`compose.yaml` fails closed when `SLAIF_LOCAL_CODING_IMAGE` is absent (no
silent default); the config and env file variables have repository-relative
fallbacks, so export the absolute paths as shown. Then pull:

```bash
# Private registry login when needed (stdin only; never literal
# credentials):
echo "$SLAIF_GHCR_TOKEN" | docker login ghcr.io -u "$SLAIF_GHCR_USERNAME" --password-stdin
docker compose pull
```

No build occurs on this path (`compose.yaml` carries no build key). Verify
the pulled image identity — inspecting the image `.Id` alone is NOT proof
of the manifest digest; check `RepoDigests` (the registry manifest digest).
The digest-pinned form is authoritative by construction; when you use the
tag form, the output MUST contain the recorded digest:

```bash
# digest form (authoritative by construction):
docker image inspect "ghcr.io/ulfe-lmi/slaif-local-coding@sha256:<OCI_IMAGE_DIGEST>" \
  --format '{{range .RepoDigests}}{{.}}{{end}}'
# tag form (mutable alias — verify, do not trust):
docker image inspect "ghcr.io/ulfe-lmi/slaif-local-coding:0.1.0-rc1" \
  --format '{{range .RepoDigests}}{{.}}{{end}}'
# must contain ghcr.io/ulfe-lmi/slaif-local-coding@sha256:<OCI_IMAGE_DIGEST>
```

The service uses `network_mode: host`: the adapter binds directly on the
host at the configured `__LISTEN_HOST__` (default `127.0.0.1:18031`); no
ports are published.

## 5. Start and verify readiness (bounded, fail-closed)

```bash
docker compose up -d
```

The compose healthcheck probes `/readyz` inside the container
(`SLAIF_HEALTH_ENDPOINT`, default `127.0.0.1:18031`): 10 s interval,
5 s timeout, 12 retries, 30 s start period. Wait for `healthy` with a
bounded loop that uses only Docker (the minimal compose+config retrieval
path is self-contained; no extra repository file or `curl` prerequisite):

```bash
STATE=""
for i in $(seq 1 36); do
  STATE="$(docker inspect --format '{{.State.Health.Status}}' slaif-local-coding-adapter-1 2>/dev/null || true)"
  [ "$STATE" = "healthy" ] && break
  sleep 5
done
[ "$STATE" = "healthy" ] || { echo "readyz: not healthy within the bounded wait — fail closed" >&2; exit 1; }
docker compose ps   # expect health: healthy
```

Fail-closed: if the bounded wait elapses, do **not** send traffic. A
missing signing secret yields `/readyz` 503 with
`gateway_ingress: "unavailable"` and an unhealthy container; inspect
`docker compose logs adapter` for the sanitized reason.

## 6. Stop / restart / status

All in the same exported session (section 4):

```bash
docker compose stop      # stop
docker compose start     # start
docker compose restart   # restart (then re-verify readiness, section 5 loop)
docker compose ps        # status
docker compose logs --tail 100 adapter   # bounded sanitized logs
```

## 7. Upgrade

In the SAME session, re-export only the image variable with the NEXT
published image digest, then recreate — no build on the host:

```bash
export SLAIF_LOCAL_CODING_IMAGE=ghcr.io/ulfe-lmi/slaif-local-coding@sha256:<NEXT_DIGEST>
docker compose pull
docker compose up -d --force-recreate
docker compose ps   # re-verify readiness: health: healthy (section 5 loop)
```

The mounted configuration file is byte-unchanged by an upgrade; the tmpfs
derived cache is intentionally wiped on recreate (the cache is disposable
by construction; no persistent cache state is claimed).

## 8. Digest-based rollback

Same mechanics with the PREVIOUS recorded digest (tags alone are not a
rollback anchor — they are aliases):

```bash
export SLAIF_LOCAL_CODING_IMAGE=ghcr.io/ulfe-lmi/slaif-local-coding@sha256:<PREVIOUS_DIGEST>
docker compose pull
docker compose up -d --force-recreate
docker compose ps   # re-verify readiness: health: healthy (section 5 loop)
```

## 9. Cache purge

The derived cache lives on the bounded `/dev/shm` tmpfs; purging is a
container recreate:

```bash
docker compose down
docker compose up -d
```

## 10. Uninstall

Nothing is persistent by design:

```bash
docker compose down --remove-orphans
docker image rm "ghcr.io/ulfe-lmi/slaif-local-coding@sha256:<OCI_IMAGE_DIGEST>" 2>/dev/null || true
rm /opt/slaif/adapter.toml /opt/slaif/adapter.env   # only if not explicitly retained
```

Uninstalling must never touch the upstream model service, the Gateway,
firewall/VPN/network state, or any Codex profile.

## External requirements (honesty note)

- The **model server** (weights, vLLM process, its API key) is an external
  prerequisite owned by the site; this installation does not create it.
- The **Gateway** (public endpoint, gateway keys, permissions, quotas,
  accounting, TLS) is a separate repository and service; point its Codex
  provider route at the adapter endpoint (loopback co-located:
  `http://127.0.0.1:18031/v1`; bridge-container Gateway: the host bridge
  interface IP; LAN-different-host: the host LAN interface IP at port
  `18031`). The Gateway route carries the service credential and signing
  secret by environment name on the Gateway side.
- Plain Codex/OpenAI clients cannot mint signed identity requests; the
  documented client path is **Codex -> SLAIF API Gateway -> adapter**.
  Direct unsigned client access exists only in the development template
  (ingress disabled, loopback) and is labeled development-only.

## Advanced: direct-host (systemd) installation

This secondary path runs the adapter as a **systemd user service** on the
local host from the repository virtual environment. It is advanced,
requires a full Python 3.12 toolchain on the host, and is the path used
for the protected-host cutover. It is **not** the canonical operator path.

The supported installation procedure is the EXACT recipe in
[docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) — section 4 (install mechanics)
and section 12 (Gateway-integrated deployment configuration: the **signed
variant**, `config/adapter.gateway-integrated.template.toml`, which is the
only supported configuration for the Gateway-integrated cutover). This
section states the path-specific preconditions; follow those sections for
the exact commands.

Prerequisites (this path only — the Docker path above needs none of them):

- Linux host, systemd user sessions, and the repository checkout owned by
  the service user;
- **Checkout path:** the shipped unit
  `packaging/slaif-local-coding.service` runs
  `ExecStart=%h/codex-work/slaif-local-coding/.venv/bin/slaif-local-coding`
  with `WorkingDirectory=%h/codex-work/slaif-local-coding` — the checkout
  must therefore be at `$HOME/codex-work/slaif-local-coding` (or the unit
  path must be corrected before install);
- **User unit directory:** the unit installs to
  `$HOME/.config/systemd/user/slaif-local-coding.service` (user manager,
  not system manager);
- **Cache path precondition:** the unit grants exactly
  `ReadWritePaths=/dev/shm/slaif-local-coding` (the default protected
  cache). If the configuration instead uses the XDG cache fallback, the
  resolved path must be added to the unit's `ReadWritePaths` before start
  (docs/DEPLOYMENT.md section 6);
- Python 3.12 and `uv` (the locked toolchain);
- the same model server, Gateway, and credential-law prerequisites as the
  Docker path.

The supported configuration is the **signed Gateway-integrated** variant
(docs/DEPLOYMENT.md section 12): three DISTINCT secret roles
(`QWEN3090_API_KEY`, `SLAIF_ADAPTER_SERVICE_TOKEN`,
`SLAIF_ADAPTER_SIGNING_SECRET`) in the mode-0600 environment file, and the
configuration instantiated from
`config/adapter.gateway-integrated.template.toml`.

**Development-only variant (clearly separate, NOT production):**
`config/adapter.deployment.template.toml` (ingress disabled, loopback) is
the development/local candidate used for local qualification only; it must
never be labeled or presented as the production Gateway-integrated
configuration (the distinction is mechanically checked by
`tests/test_gateway_integrated_deployment.py`).

Upgrade/rollback on this path: rebuild or reinstall the wheel from the
recorded source, then restart the unit and re-verify readiness
(docs/DEPLOYMENT.md sections 9 and 10). See also
[docs/RELEASE-CUTOVER-RUNBOOK.md](docs/RELEASE-CUTOVER-RUNBOOK.md) for the
prepare-only cutover/rollback procedure.

## See also

- [QUICKSTART.md](QUICKSTART.md) — the 5–10 minute Docker path;
- [docs/DOCKER-INSTALL.md](docs/DOCKER-INSTALL.md) — the detailed
  canonical Docker procedure;
- [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) — the complete operator
  contract for both paths;
- [docs/RC-HANDOFF.md](docs/RC-HANDOFF.md) — RC artifact retrieval and
  identity verification;
- [docs/ADAPTER-CONFIGURATION.md](docs/ADAPTER-CONFIGURATION.md) — the
  configuration reference.

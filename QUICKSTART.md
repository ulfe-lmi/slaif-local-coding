# Quickstart (Docker, 5–10 minutes)

This is the essential Docker path for SLAIF Local Coding. It assumes the
prerequisites already exist on one Linux host:

1. **Linux host (`linux/amd64`)** with Docker Engine and the **Compose v2
   plugin** (`docker compose version`). `linux/amd64` is the built and
   qualified image architecture; no other platform or architecture is
   claimed. The host needs **no Python, no uv, and no local build** on this
   path — the runtime is the pulled wheel-based container image.
2. A **private OpenAI-compatible model server** (Qwen/vLLM) running on this
   host, reachable at its documented loopback address
   (reference default: `http://127.0.0.1:18020/v1`, model `qwen3.8-27b`).
3. The **separate SLAIF API Gateway** already deployed for public access
   (this product does not install or configure it).
4. **Bounded read-only GHCR credentials** for the private image package:
   the reader scope is `read:packages` (a classic PAT with package
   read access for this package) — distinct from the Actions YAML
   `packages: read` keyword. Credentials are supplied via stdin only, and
   the package can remain private.
5. A **host admin account** (root or a sudo-authorized admin) for the two
   `/opt/slaif` file-ownership steps in section 4; the rest of the path
   runs as your normal account.
6. The **RC artifact record** for the release candidate you were handed
   (see [docs/RC-HANDOFF.md](docs/RC-HANDOFF.md)): it records the image
   source commit, the OCI reference, and the authoritative image digest.

## 1. Obtain the matching compose and configuration

Check out the repository at the **recorded image source commit** from the
RC artifact record (the exact source the image was built from):

```bash
git clone https://github.com/ulfe-lmi/slaif-local-coding.git
cd slaif-local-coding
git fetch --depth 1 origin <IMAGE_SOURCE_COMMIT>
git checkout --detach FETCH_HEAD
```

Keep only `compose.yaml` and
`config/adapter.gateway-integrated.template.toml` for the operator project
(the build override `compose.build.yaml` is the qualification/development
build path and is NOT part of this path). Everything this path runs — the
compose file, the template, and the readiness wait — is present in that
file set; no other repository file or extra `curl` prerequisite is needed.

## 2. Set the operator session variables (once)

Every Compose command in this quickstart — `pull`, `up`, `ps`, `logs` —
runs in this same shell with the same three exported variables, so no
later command ever resolves a missing or wrong default. Tags are aliases;
the immutable digest is the authoritative identity — prefer the
digest-pinned reference from the RC record:

```bash
export SLAIF_LOCAL_CODING_IMAGE=ghcr.io/ulfe-lmi/slaif-local-coding@sha256:<OCI_IMAGE_DIGEST>
# tag form (less exact; verify in section 5 after the pull):
# export SLAIF_LOCAL_CODING_IMAGE=ghcr.io/ulfe-lmi/slaif-local-coding:0.1.0-rc2
export SLAIF_CONFIG_FILE=/opt/slaif/adapter.toml
export SLAIF_ENV_FILE=/opt/slaif/adapter.env
```

`compose.yaml` fails closed if `SLAIF_LOCAL_CODING_IMAGE` is not set
(`:?` guard; no silent default); the config and env file variables have
repository-relative fallbacks, so export the absolute paths as shown.

## 3. Log in to the private registry (when needed)

Credentials are supplied by **stdin only** — never literal in a command or
file:

```bash
echo "$SLAIF_GHCR_TOKEN" | docker login ghcr.io -u "$SLAIF_GHCR_USERNAME" --password-stdin
```

## 4. Prepare the protected configuration

Directory creation and the two file-ownership steps require the host
admin account (root or sudo-authorized); everything else in this section
runs as your normal account.

```bash
# Host admin: create the protected site directory (0700) and hand its
# ownership to the operator account that runs Compose. The Compose client
# reads the env file on the HOST side and resolves the config path, so the
# operator must be able to traverse the directory and read the env file:
sudo install -d -m 0700 /opt/slaif
sudo chown "$USER" /opt/slaif
```

Then, as your normal account (the same shell as section 2):

```bash
umask 077

# Fail clearly when a required secret is unset or empty in this shell
# (values come from your protected store and are never written into the
# repository, the image, the compose file, logs, or this document):
: "${QWEN3090_API_KEY:?set QWEN3090_API_KEY in this shell from your protected store before creating the env file}"
: "${SLAIF_ADAPTER_SERVICE_TOKEN:?set SLAIF_ADAPTER_SERVICE_TOKEN in this shell from your protected store before creating the env file}"
: "${SLAIF_ADAPTER_SIGNING_SECRET:?set SLAIF_ADAPTER_SIGNING_SECRET in this shell from your protected store before creating the env file}"

# Mode-0600 environment file, owned by the operator (the Compose client
# reads it; the three distinct secret roles by env name):
printf 'QWEN3090_API_KEY=%s\nSLAIF_ADAPTER_SERVICE_TOKEN=%s\nSLAIF_ADAPTER_SIGNING_SECRET=%s\n' \
  "$QWEN3090_API_KEY" "$SLAIF_ADAPTER_SERVICE_TOKEN" "$SLAIF_ADAPTER_SIGNING_SECRET" \
  > /opt/slaif/adapter.env
chmod 0600 /opt/slaif/adapter.env

# Mode-0600 configuration from the template: substitute ONLY the documented
# placeholders, no other manual editing:
sed -e 's/__LISTEN_HOST__/127.0.0.1/' \
    -e 's/__UPSTREAM_BASE_URL__/http:\/\/127.0.0.1:18020\/v1/' \
    -e 's/__UPSTREAM_MODEL__/qwen3.8-27b/' \
    config/adapter.gateway-integrated.template.toml \
    > /opt/slaif/adapter.toml
chmod 0600 /opt/slaif/adapter.toml

# The container runs as the fixed non-root user 10001:10001; the read-only
# mounted configuration must be readable by that user (mode 0600 preserved;
# only the owner changes; chown requires the host admin):
sudo chown 10001:10001 /opt/slaif/adapter.toml
```

`__LISTEN_HOST__` stays `127.0.0.1` for the default loopback bind. A
non-loopback bind is legal only under the full signed-ingress contract
carried by this template (see [docs/DOCKER-SECURITY-DELTA.md](docs/DOCKER-SECURITY-DELTA.md)).

## 5. Pull and verify the image identity

```bash
docker compose pull
```

The digest-pinned form is authoritative by construction. When you use the
tag form instead, verify that the pulled tag resolves to the recorded
digest — inspecting the image `.Id` alone is NOT proof of the manifest
digest; check `RepoDigests` (the registry manifest digest):

```bash
docker image inspect ghcr.io/ulfe-lmi/slaif-local-coding:0.1.0-rc2 \
  --format '{{range .RepoDigests}}{{.}}{{end}}'
# must contain ghcr.io/ulfe-lmi/slaif-local-coding@sha256:<OCI_IMAGE_DIGEST>
```

## 6. Start

```bash
docker compose up -d
```

No build occurs: `compose.yaml` carries no build key. The service uses
`network_mode: host`, so the adapter binds directly on the host at the
configured `__LISTEN_HOST__` (default `127.0.0.1:18031`); no ports are
published.

## 7. Health and readiness (bounded, fail-closed)

The compose healthcheck probes `/readyz` inside the container
(`SLAIF_HEALTH_ENDPOINT`, default `127.0.0.1:18031`): 10 s interval,
5 s timeout, 12 retries, 30 s start period. Wait for `healthy` with a
bounded loop that uses only Docker (the minimal file set in section 1 is
self-contained; no extra repository file or `curl` prerequisite):

```bash
docker compose ps
STATE=""
for i in $(seq 1 36); do
  STATE="$(docker inspect --format '{{.State.Health.Status}}' slaif-local-coding-adapter-1 2>/dev/null || true)"
  [ "$STATE" = "healthy" ] && break
  sleep 5
done
[ "$STATE" = "healthy" ] || { echo "readyz: not healthy within the bounded wait — fail closed" >&2; exit 1; }
```

Expect `healthy`. If the bounded wait elapses, do **not** send traffic.

## Minimal troubleshooting

| Symptom | First check |
| --- | --- |
| `docker compose` fails with a `SLAIF_LOCAL_CODING_IMAGE` error | Set the explicit image reference (section 2) before any compose command. |
| Pull fails with an authentication error | Re-run the registry login (section 3); verify the classic PAT has `read:packages` for this package (not the Actions `packages: read` keyword). |
| Container unhealthy, `/readyz` returns 503 `gateway_ingress: unavailable` | The three secret roles in the env file are missing or empty; fix the file and recreate the container. |
| Readiness 503 referring to the upstream | The private model server is not reachable at the configured `__UPSTREAM_BASE_URL__` from the host loopback. |
| Port `18031` already in use | Identify the owner with `ss -ltnp` and reconcile only a service YOU own (stop or reconfigure it, or choose a different adapter port and re-instantiate the configuration). Never stop a service you do not own; if the owner cannot be reconciled, escalate to the site operator. |

Logs are sanitized: `docker compose logs --tail 100 adapter`.

## Next

The full operator contract — upgrade, digest-based rollback, stop/restart,
uninstall, and the advanced direct-host path — is in
[INSTALL.md](INSTALL.md). See also [docs/DOCKER-INSTALL.md](docs/DOCKER-INSTALL.md)
and the RC handoff/identity-verification procedure in
[docs/RC-HANDOFF.md](docs/RC-HANDOFF.md).

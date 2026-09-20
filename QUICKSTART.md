# Quickstart (Docker, 5–10 minutes)

This is the essential Docker path for SLAIF Local Coding. It assumes the
prerequisites already exist on one Linux host:

1. **Docker Engine + the Compose v2 plugin** (`docker compose version`).
   No other platform is claimed.
2. A **private OpenAI-compatible model server** (Qwen/vLLM) running on this
   host, reachable at its documented loopback address
   (MVP appliance default: `http://127.0.0.1:18020/v1`, model `qwen3.8-27b`).
3. The **separate SLAIF API Gateway** already deployed for public access
   (this product does not install or configure it).
4. **Bounded read-only GHCR credentials** for the private image package
   (a token with `packages:read` scope).
5. The **RC artifact record** for the release candidate you were handed
   (see [docs/RC-HANDOFF.md](docs/RC-HANDOFF.md)): it records the image
   source commit, the OCI reference, and the authoritative image digest.

The host needs **no Python, no uv, and no local build** on this path — the
runtime is the pulled wheel-based container image.

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
build path and is NOT part of this path).

## 2. Select the image (digest preferred)

Tags are aliases; the immutable digest is the authoritative identity. Set
the explicit image reference required by `compose.yaml` — prefer the
digest-pinned form from the RC record:

```bash
export SLAIF_LOCAL_CODING_IMAGE=ghcr.io/ulfe-lmi/slaif-local-coding@sha256:<OCI_IMAGE_DIGEST>
# tag form (less exact):
# export SLAIF_LOCAL_CODING_IMAGE=ghcr.io/ulfe-lmi/slaif-local-coding:0.1.0-rc1
```

`compose.yaml` fails closed if `SLAIF_LOCAL_CODING_IMAGE` is not set;
there is deliberately no silent default.

## 3. Log in to the private registry (when needed)

Credentials are supplied by **stdin only** — never literal in a command or
file:

```bash
echo "$SLAIF_GHCR_TOKEN" | docker login ghcr.io -u "$SLAIF_GHCR_USERNAME" --password-stdin
```

## 4. Prepare the protected configuration

Create a private state directory **outside the repository checkout** and
instantiate the Gateway-integrated configuration template, substituting
only its documented placeholders:

```bash
install -d -m 0700 /opt/slaif
umask 077

# Mode-0600 environment file: the THREE DISTINCT secret roles, values from
# your protected store (never written into the repo, image, compose, logs,
# or this document):
#   QWEN3090_API_KEY, SLAIF_ADAPTER_SERVICE_TOKEN, SLAIF_ADAPTER_SIGNING_SECRET
printf 'QWEN3090_API_KEY=%s\nSLAIF_ADAPTER_SERVICE_TOKEN=%s\nSLAIF_ADAPTER_SIGNING_SECRET=%s\n' \
  "$QWEN3090_API_KEY" "$SLAIF_ADAPTER_SERVICE_TOKEN" "$SLAIF_ADAPTER_SIGNING_SECRET" \
  > /opt/slaif/adapter.env
chmod 0600 /opt/slaif/adapter.env

# Mode-0600 configuration from the template:
sed -e 's/__LISTEN_HOST__/127.0.0.1/' \
    -e 's/__UPSTREAM_BASE_URL__/http:\/\/127.0.0.1:18020\/v1/' \
    -e 's/__UPSTREAM_MODEL__/qwen3.8-27b/' \
    config/adapter.gateway-integrated.template.toml \
    > /opt/slaif/adapter.toml
chmod 0600 /opt/slaif/adapter.toml

# The container runs as the fixed non-root user 10001:10001; the read-only
# mounted configuration must be readable by that user (mode 0600 preserved;
# chown requires the host admin):
chown 10001:10001 /opt/slaif/adapter.toml
```

`__LISTEN_HOST__` stays `127.0.0.1` for the default loopback bind. A
non-loopback bind is legal only under the full signed-ingress contract
carried by this template (see [docs/DOCKER-SECURITY-DELTA.md](docs/DOCKER-SECURITY-DELTA.md)).

## 5. Pull and start

```bash
SLAIF_CONFIG_FILE=/opt/slaif/adapter.toml \
SLAIF_ENV_FILE=/opt/slaif/adapter.env \
docker compose pull

SLAIF_CONFIG_FILE=/opt/slaif/adapter.toml \
SLAIF_ENV_FILE=/opt/slaif/adapter.env \
docker compose up -d
```

No build occurs: `compose.yaml` carries no build key. The service uses
`network_mode: host`, so the adapter binds directly on the host at the
configured `__LISTEN_HOST__` (default `127.0.0.1:18031`); no ports are
published.

## 6. Health and readiness (bounded, fail-closed)

```bash
docker compose ps
docker inspect --format '{{.State.Health.Status}}' slaif-local-coding-adapter-1
packaging/readyz-wait.sh
```

Expect `healthy` and a `200` from the bounded loopback `/readyz` wait. If
the bounded wait elapses, do **not** send traffic.

## Minimal troubleshooting

| Symptom | First check |
| --- | --- |
| `docker compose` fails with a `SLAIF_LOCAL_CODING_IMAGE` error | Set the explicit image reference (step 2) before any compose command. |
| Pull fails with an authentication error | Re-run the registry login (step 3); verify the token has `packages:read` for this package. |
| Container unhealthy, `/readyz` returns 503 `gateway_ingress: unavailable` | The three secret roles in the env file are missing or empty; fix the file and recreate the container. |
| Readiness 503 referring to the upstream | The private model server is not reachable at the configured `__UPSTREAM_BASE_URL__` from the host loopback. |
| Port `18031` already in use | Stop whatever owns the port; the adapter uses host networking and does not republish ports. |

Logs are sanitized: `docker compose logs --tail 100 adapter`.

## Next

The full operator contract — upgrade, digest-based rollback, stop/restart,
uninstall, and the advanced direct-host path — is in
[INSTALL.md](INSTALL.md). See also [docs/DOCKER-INSTALL.md](docs/DOCKER-INSTALL.md)
and the RC handoff/identity-verification procedure in
[docs/RC-HANDOFF.md](docs/RC-HANDOFF.md).

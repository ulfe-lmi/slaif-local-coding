# Docker deployment reference

**Start with [QUICKSTART.md](../QUICKSTART.md) or [INSTALL.md](../INSTALL.md).**
INSTALL is the canonical command sequence for image selection, private registry
login, protected files, pull, start, readiness, upgrade, rollback and uninstall.
This reference explains deployment choices and the development-only build override.

## Supported runtime

- Linux Docker Engine with Compose v2; qualified image platform `linux/amd64`.
- A private model server and a separately configured SLAIF API Gateway.
- Host networking, with the model endpoint on true host loopback.
- An explicit image reference in `SLAIF_LOCAL_CODING_IMAGE`; no default image
  or local build in the operator Compose file. Prefer the recorded OCI digest.
- Protected configuration readable by container user `10001:10001` and a
  mode-`0600` environment file readable by the host operator running Compose.
- A free adapter port. Identify any existing owner; do not stop unrelated services.

The install host needs no Python, uv or project virtual environment. A private
GHCR package requires a bounded reader credential with `read:packages`.
The [RC handoff](RC-HANDOFF.md) explains the digest, source and configuration
identities. Existing legacy final-looking tags are not installation defaults.

## Compose behavior

[compose.yaml](../compose.yaml) is pull-based and contains no `build:` key.
Set and retain all three session variables documented in INSTALL:
`SLAIF_LOCAL_CODING_IMAGE`, `SLAIF_CONFIG_FILE` and `SLAIF_ENV_FILE`.
Use the same file set and variables for every lifecycle command.

The container runs non-root with a read-only root filesystem, all capabilities
dropped, `no-new-privileges`, and bounded scratch/cache tmpfs. It has no Docker
socket, repository bind or model weights. Only the configuration is mounted
read-only; Compose reads the protected environment file on the host.

Host networking removes Docker network-namespace isolation. There is no `ports:`
mapping: the configured listener binds directly on the host. Loopback is the
default; a LAN/interface bind requires full signed ingress. Health, readiness
and metrics share that listener. See [TOPOLOGY.md](TOPOLOGY.md) and the
[security comparison](DOCKER-SECURITY-DELTA.md).

## Connecting the Gateway

Configure the Gateway backend with an address reachable from its runtime
namespace. Use service Bearer plus signed identity v1 and the matching route.
A bridge-container Gateway cannot use its own loopback to reach the host adapter.
See [the integration contract](SLAIF-GATEWAY-INTEGRATION.md).

Clients connect through the Gateway. Possessing an adapter service token alone
is insufficient for signed ingress; ordinary clients do not construct this
internal contract themselves.

## Development variant

The development variant is **development only, not production**.
`compose.build.yaml` adds a local build to the canonical Compose definition;
`config/adapter.deployment.template.toml` disables ingress and stays loopback-only.
Use synthetic credentials and a disposable fake upstream. Do not publish a local
qualification tag as an RC identity.

A developer with the locked Python environment and a disposable Docker host can
build and qualify using the commands in [TESTING.md](../TESTING.md). The
[artifact policy](RELEASE-ARTIFACT-POLICY.md) defines clean builds, provenance and
publication. The normal operator never needs this override or source build.

## Troubleshooting and operations

| Symptom | Check |
| --- | --- |
| Pull denied | Registry login, reader scope and access to the private package. |
| Compose reports a missing variable | Restore the same three exported session variables from INSTALL. |
| Configuration unreadable | File is mode `0600`, owned by `10001:10001`; host operator can traverse its parent directory. |
| Container unhealthy | Inspect sanitized logs; verify protected credentials and upstream health. Do not route traffic before readiness succeeds. |
| Gateway cannot connect | Check runtime namespace, host-interface address and adapter bind. |
| Signed request rejected | Verify service/signing roles, clock, route and exact signed body; never log secret values. |

Upgrade and rollback use recorded digests and their matching source/configuration
files. Cache state is disposable. Removing this adapter must leave the model
server, Gateway, unrelated containers and client profiles untouched.

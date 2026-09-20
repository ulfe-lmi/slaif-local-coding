# Docker and systemd security comparison

Docker is the primary installation path. The direct-host systemd unit applies
a different set of restrictions. The two paths are not security-equivalent;
choose with the following limits in mind.

## Containment differences

| Control | Docker Compose | systemd user service |
| --- | --- | --- |
| Network | Host networking; process can reach host interfaces and loopback. | `IPAddressDeny=any` with loopback allow rules, where supported by the host. |
| Listener | Loopback by default; non-loopback requires full signed ingress in application validation. | Supplied unit remains loopback-only. |
| Filesystem | Read-only image root; one read-only configuration bind; bounded `/tmp` and `/dev/shm` tmpfs. | `ProtectSystem=strict`, read-only home, explicit writable cache path and private temporary storage. |
| Process visibility | Own PID namespace; host networking does not give access to host processes through `/proc`. | `ProtectProc=invisible`. |
| Privilege | Non-root `10001:10001`, all capabilities dropped, `no-new-privileges`, no Docker socket or privileged mode. | `NoNewPrivileges`, namespace/SUID/realtime restrictions and no ambient capabilities. |
| Resource limits | Application bounds and tmpfs bounds; Compose defines no explicit memory or PID limit. | `MemoryMax=1G`, `TasksMax=128`, `LimitNOFILE=4096`. |

Host networking deliberately removes network-namespace isolation so the model
hop is true host loopback. Docker's `ports:` publishing is not involved. An
application listener restriction is not a kernel restriction on a compromised
process's outbound connections.

## Shared application protections

- Non-loopback binds require `service_bearer_signed_identity_v1`.
- Service authentication, signed opaque identity and bounded replay checks run
  before transformation or upstream work.
- The upstream, service and signing roles use distinct environment names.
- Signed-mode readiness fails if required ingress credentials are unavailable.
- Bodies, JSON depth, compiler work, cache and injection have finite bounds.
- Raw payload logging is disabled and cannot be enabled by configuration.
- Proxy errors are sanitized; metrics contain fixed states, counts and timings.

The signed ingress requirement protects proxy endpoints. `/healthz`, `/readyz`
and `/metrics` are operator endpoints on the same socket; they are reachable
from the same trusted surface on a LAN bind and must remain private.

## Trust assumptions and residual risks

**Host administrators and Docker operators are trusted.** They can inspect
container environment variables, files and traffic. Mode-`0600` secret files
protect against ordinary unauthorized users, not host root or Docker access.

**A compromised adapter can use its upstream credential.** With host networking
it can reach host loopback and other host-reachable interfaces/services. Dropped
capabilities do not eliminate that network reach. The systemd path's effective
kernel network restrictions provide a stronger boundary when available.

**The supported LAN variant uses a declared trusted private LAN.** Internal
HTTP is not encrypted. Service Bearer, HMAC and replay protection provide
authentication/integrity, not confidentiality. Do not treat RFC1918 addressing
as encryption or expose the adapter directly to the internet. Broader transport
design is outside the qualified deployment contract.

**Resource isolation is incomplete.** Finite application and tmpfs bounds reduce
exhaustion risk, but the supplied Compose configuration has no container-wide
memory/PID ceiling. This is a single-host appliance contract, not a hostile
multi-tenant isolation claim.

## Secret handling

The image uses no credential build arguments or secret-bearing layers. The
configuration references environment variable names; Compose reads credential
values from a protected host environment file and passes them to the container.
The file is not a runtime bind mount, but the resulting environment is visible
to Docker administrators. Avoid sharing `docker inspect` or rendered Compose
output: these tools can expose resolved environment values.

The runtime contains the non-editable wheel and locked dependencies, without
repository source, OAP records, tests, model weights or customer data. Logs and
metrics exclude credentials and raw content. The derived cache still contains
sensitive compiled guidance and uses bounded storage and restricted permissions.

See [SECURITY.md](../SECURITY.md), [INSTALL.md](../INSTALL.md) and
[TOPOLOGY.md](TOPOLOGY.md). CI verifies the actual container configuration,
platform, contents and provenance; tests do not establish production security
certification or authorize protected-host cutover.

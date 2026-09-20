# Runtime topology

The supported deployment keeps the model server and Local Coding adapter on
one Linux host. Clients connect through the separate SLAIF API Gateway. Use
[INSTALL.md](../INSTALL.md) for setup and the
[architecture overview](../ARCHITECTURE.md) for component diagrams.

## Network namespaces matter

`127.0.0.1` always belongs to the process's own network namespace. A bridge
container's loopback is not the host's loopback, and loopback never crosses
hosts. Verify reachability from the **Gateway runtime**, not just its host shell.

The adapter's Docker container uses host networking. Its upstream
`http://127.0.0.1:18020/v1` therefore reaches the host model server. The default
adapter listener is `127.0.0.1:18031`.

## Supported Gateway connections

| Gateway runtime | Adapter address | Required boundary |
| --- | --- | --- |
| Same host network namespace | `127.0.0.1:18031` | True loopback; service Bearer plus signed identity v1. |
| Bridge container on the same host | Reachable host bridge-interface IP, port `18031` | Explicit non-loopback adapter bind, trusted private network and full signed ingress. |
| Another host on the declared trusted private LAN | Adapter host's private interface IP, port `18031` | Explicit non-loopback adapter bind, trusted private LAN and full signed ingress. |

For a colocated loopback deployment, the Gateway runtime must also share the
host network namespace. The Gateway's default bridge deployment needs explicit
deployment configuration; merely setting its backend to `127.0.0.1` will not
work. A bridge Gateway can instead use the supported host-interface variant.
Gateway source changes are not needed for these route settings.

The Gateway edge is the only public entry point. Client keys terminate there.
The Gateway sends service authentication and signed opaque identity to Local;
Local substitutes the private upstream credential for the Qwen/vLLM hop.

## Binding and confidentiality

The default loopback bind is accepted in every ingress mode. Any non-loopback
bind requires `service_bearer_signed_identity_v1`; unknown transport combinations
and incomplete authentication fail closed. Signed-mode readiness fails when
required ingress secrets are unavailable.

HMAC authenticates and protects integrity; it does not encrypt the payload.
The LAN variant assumes a deliberately trusted private LAN and sends internal
HTTP in plaintext. A private RFC1918 address alone is not an encrypted boundary.
Broader multi-host or untrusted-network deployments are outside the qualified
contract and require a separate encrypted-transport design.

`/healthz`, `/readyz` and `/metrics` share the adapter's single listener. The
`metrics_host` setting does not create a second socket or restrict that listener;
on a LAN bind these endpoints are reachable on the same trusted surface.
See the [security comparison](DOCKER-SECURITY-DELTA.md).

## Qualification and operations

[topology.manifest.json](topology.manifest.json) is the machine-readable
companion. [The qualification predicate](../scripts/topology_qualification.py)
rejects cross-namespace loopback, unknown transports and non-loopback binds
without full signed ingress. CI exercises these cases with disposable services.

The Gateway contract is tested against the exact peer in
[current_peer_authority.json](../tests/fixtures/gateway/current_peer_authority.json).
The [artifact policy](RELEASE-ARTIFACT-POLICY.md#gateway-compatibility-authority-frozen-for-010)
records the separate frozen release authority.

A topology description does not prove an installed deployment. Discover current
service, listener, route and client-profile facts before an authorized cutover;
use the [cutover runbook](RELEASE-CUTOVER-RUNBOOK.md) and preserve a complete
rollback baseline. Historical host snapshots are indexed in [HISTORY.md](HISTORY.md).

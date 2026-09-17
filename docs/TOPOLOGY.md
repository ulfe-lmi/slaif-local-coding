# Runtime topology (order 010-a, workstream A; order 011-a G2/F7)

Explicit intended RUNTIME topology for the supported final path and the
supported LAN-visible signed variant. This document supersedes the implicit
topology assumed by earlier runbook drafts and is the normative topology
reference for the cutover runbook, the deployment procedure, and the topology
qualification harness.

Machine-readable companion: [`topology.manifest.json`](topology.manifest.json)
(schema `slaif-topology-manifest-v2`), mechanically checked by
`tests/test_topology_qualification.py` and `scripts/topology_qualification.py`.

## 1. Strictly separate concepts

The topology treats the following as **distinct, non-interchangeable**
concepts. No shared filesystem and no shared localhost is assumed between
repositories or between any two of these concepts:

| Concept | Meaning |
| --- | --- |
| Local/Qwen host | The physical host that runs the protected Qwen/vLLM vision service and the Local Coding adapter. |
| Local process network namespace | The network namespace of the Local adapter process (the host namespace in the supported appliance contract). |
| Gateway host | The host that runs the SLAIF API Gateway deployment (separate repository). |
| Gateway process/container network namespace | The network namespace of the Gateway `api` runtime process or container. |
| Codex client host/profile | The host and Codex client profile that originate requests. |

`127.0.0.1` means "the loopback interface **of the network namespace that
holds the endpoint**". Loopback does not cross host or container network
namespaces. Any topology that routes traffic from a separate namespace to
`127.0.0.1` on another namespace is impossible and is rejected by the
qualification predicate (workstream E negative test).

## 2. Verified live facts (read-only, 2026-09-14, no credential values)

Independently verified by the strategic agent and re-verified read-only by
the coding agent on the Local host; recorded here without credential values:

- **No Gateway deployment exists on the Local host**: no Gateway checkout
  under the home directory, no Gateway listener among all host listeners,
  and the container runtime holds only three stale exited containers (two
  years old, no published ports) with a down link-local bridge interface.
- **Single network interface on the Local host**: one RFC1918 private-LAN
  /24 address (DHCP, unencrypted; no VPN/tunnel software present — no wireguard
  configuration and no tailscale/wireguard binaries), default route via the
  /24 gateway. A private RFC1918 address is **not** an encrypted boundary.
- **Protected vision service**: the user service is active (running) on the
  protected vLLM port `18020`; `GET /health` returns 200. Port `18021` is
  absent; port `18031` is absent (the adapter development port is free).
- **Active Codex profile** (read-only; credential values never recorded):
  provider endpoint `http://maelstrom1.lmi.link:8001/v1` (plain HTTP, no
  TLS), which resolves to an address inside the same RFC1918 /24. The
  `maelstrom1:8001 -> vLLM` mapping is an **unresolved operator fact** that
  the cutover runbook captures in its step-1 baseline; nothing in this
  repository assumes how that endpoint is backed.
- **Gateway peer authority**: the pinned Gateway peer commit
  `08ca421bee1ddca62078302b910e8be88cf705be` (repository
  `ulfe-lmi/slaif-api-gateway`, module `local-coding-v1` v2, client module
  `codex-0.149-responses-v1` v4) is the gateway repository default-branch
  main at the Objective-013-b order time (2026-09-17). The local fixture pin
  was re-pinned by Objective 012 (2026-09-17) from
  `65666f5886832034c52211fdd7604046557e6ada` to
  `1fccaa746df6cd44f1ddf8c2ec5cf6ea9f18b1cb` after gateway PR #302 (Objective 165,
  merged 2026-09-17) advanced Gateway main, and re-pinned again by
  Objective 013-b (2026-09-17) to this commit after gateway PRs #303/#304
  (Objectives 166-a/167-a, merged 2026-09-17) advanced Gateway main
  further; each re-pin is documentation/OAP/doc-check work only, and the
  three contract source files the `gateway-contract` gate validates are
  byte-identical (GitHub blob SHAs) between all pins, so the contract
  surface is unchanged.

## 3. Supported final path

```text
Codex -> Gateway runtime -> [true loopback 127.0.0.1:18031, shared host network
                             namespace, service Bearer + signed identity v1]
                              -> Local Coding adapter -> [true loopback
                              127.0.0.1:18020, protected upstream credential]
                              -> Qwen/vLLM vision service
```

Per-hop facts:

| Hop | Network namespace | Address class | Authentication | Confidentiality boundary | Owning repository/service | Publicly reachable? |
| --- | --- | --- | --- | --- | --- | --- |
| Codex client -> Gateway entry | Codex client host -> Gateway edge (nginx, TLS) | public/edge address, TLS | Gateway key (terminates at the Gateway) | TLS to the Gateway edge; the Gateway key is the outermost credential | `slaif-api-gateway` (nginx + `api`) | The Gateway entry is the only public surface |
| Gateway runtime -> Local Coding | **shared host network namespace** (co-located deployment, see §4) | **loopback** `127.0.0.1:18031` | service Bearer + signed identity v1 (mandatory; fail-closed) | **no network traversal**: loopback only, plus service Bearer + signed identity as the only ingress | `slaif-local-coding` (adapter) + `slaif-api-gateway` (route configuration) | No: loopback-only binding, `IPAddressDeny=any` unit hardening, private `/metrics` |
| Local Coding -> Qwen/vLLM | same host network namespace | **loopback** `127.0.0.1:18020` | protected upstream credential (env name only) | no network traversal (loopback) | `qwen-serving` (protected fixture) | No: the protected service is not publicly routable; no direct public vLLM route exists |

The supported final path contains **no impossible cross-host or
cross-container `127.0.0.1` assumption**: both loopback hops exist inside
one host network namespace.

## 4. Gateway -> Local transport decision (workstream B)

**Decision: co-located single-host shared-namespace deployment.** The
supported final topology is the smallest one that preserves the Local
loopback-only law: the Gateway runtime is deployed on the **same physical
host** as the Local adapter and the protected Qwen service, sharing the
**host network namespace**. The Gateway -> Local hop is then true loopback
(`127.0.0.1:18031`): no Local binding changes, no new network mechanism, and
the confidentiality boundary is loopback (no network traversal) plus service
Bearer plus signed identity, with the Gateway route as the sole authorized
caller.

Pinned-Gateway source inspection (Objective-010-era
commit `65666f5886832034c52211fdd7604046557e6ada`, read-only) established:

- The provider route backend URL is per-provider configuration
  (`ProviderConfig.base_url`) with server-side secret env lookup and
  provider Bearer substitution — so pointing the Codex route at
  `http://127.0.0.1:18031/v1` is Gateway **configuration**, not a Gateway
  source change.
- The signed-identity contract for the Local Coding route
  (`identity_mode = "signed_identity_v1"`, `replay_mode =
  process_local_inclusive_horizon_fail_closed`) is emitted by the pinned
  Gateway server module and is continuously tested against the local
  adapter contract (objective-007 `gateway-contract` CI).
- The pinned Gateway deployment contract (docker-compose stack: postgres,
  redis, mailpit, `api` = gunicorn, celery worker; nginx edge) is
  **bridge-network based** by default: in the production compose, the `api`
  service joins an internal bridge network (plus an egress network) and its
  diagnostic port is published to host loopback only. A bridge-networked
  container's `127.0.0.1` is the container's own loopback, not the host's.

Objective 012 (2026-09-17) re-verified the identical contract surface at
the re-pinned peer `1fccaa746df6cd44f1ddf8c2ec5cf6ea9f18b1cb`: the three contract source files the
`gateway-contract` gate validates are byte-identical (GitHub blob SHAs)
between the 010-era pin above and the pin then current, so these findings
remain valid at the current pin. Objective 013-b (2026-09-17) re-pinned the
peer to `08ca421bee1ddca62078302b910e8be88cf705be`; the contract surface is
byte-identical there as well (GitHub blob SHAs), so these findings remain
valid at the current pin.

Therefore the supported topology is **executable** against the pinned
Gateway deployment contract **with a deployment-level (not source-level)
change performed by the separately authorized cutover order**: the Gateway
`api` runtime must run in the host network namespace — either the
compose-per-service host-networking configuration for the `api` runtime
(with its loopback diagnostic publish removed for that service, the other
services keeping their networks) or an equivalent single-host
shared-namespace runtime deployment. The cutover runbook names this
explicitly in the GATEWAY state and in the step that configures the route.
No Gateway product defect was found; no cross-repository handoff document is
required.

### Supported LAN-visible signed variant (order 011-a, decisions D1/D2/D4)

Objective 011 records a second supported transport variant, mandated by the
human release decision (LAN-visible installation) and bounded by the D1
binding law: **a non-loopback adapter bind is legal if and only if the full
accepted signed ingress contract** (`service_bearer_signed_identity_v1`)
**is in force.** Under the Docker `network_mode: host` deployment the
adapter binds `0.0.0.0:18031` (or a site interface IP) and the per-hop
table extends as follows:

| Hop | Network namespace | Address class | Authentication | Confidentiality boundary | Owning repository/service | Publicly reachable? |
| --- | --- | --- | --- | --- | --- | --- |
| Co-located host-namespace Gateway -> Local | shared host network namespace (unchanged) | loopback `127.0.0.1:18031` | service Bearer + signed identity v1 (mandatory; fail-closed) | loopback only, plus the full signed contract | adapter + Gateway route configuration | No: loopback bind, single socket |
| Bridge-container Gateway -> Local | separate container network namespace -> host namespace | host bridge interface IP `:18031` (e.g. docker0 link-local) | service Bearer + signed identity v1 (mandatory; fail-closed) | declared trusted private LAN (D4), plus the full signed contract; **no anonymous surface** | adapter + Gateway route configuration | No: not publicly routable; reachable only from the host bridge and the declared LAN |
| LAN-different-host Gateway/client -> Local | separate host/network namespace -> host namespace | host LAN interface IP `:18031` (declared trusted private LAN) | service Bearer + signed identity v1 via the Gateway edge (clients never reach the adapter directly; D8) | declared trusted private LAN (D4), plus the full signed contract; **no anonymous surface** | adapter + Gateway route configuration | No: not publicly routable; the Gateway edge is the only public surface |

The impossible cross-namespace loopback (a separate-namespace Gateway
targeting `127.0.0.1:18031`) **remains rejected** in this variant exactly as
in the 010 decision: loopback does not cross network namespaces. Every
non-loopback combination **without** the full signed contract fails closed
(`non_loopback_bind_requires_full_signed_ingress`), and every unknown input
fails closed (`unknown_transport_fails_closed`). The Qwen hop remains true
host loopback (`127.0.0.1:18020`) inside the single container (D2). The
bridge-container Gateway variant is **Gateway configuration only** (route
backend at the host bridge IP); no Gateway source change is required.

**Multi-host topologies beyond the declared trusted single private LAN are
NOT supported in this objective.** Their exact
requirements are recorded so a future human architecture decision can be
made on evidence, not inference:

- An encrypted Gateway -> Local transport (TLS with verified certificates
  on a dedicated channel) **or** a proven encrypted VPN/tunnel between the
  two hosts — "private RFC1918 address" alone is **not** an encrypted
  boundary and never qualifies.
- A corresponding change to the Local binding law (bind address, unit
  `IPAddressAllow`, configuration `listen_host`) — the current D1 binding
  law (in force since Objective 011) is: loopback is the default bind, and
  a non-loopback bind is legal only under the full
  `service_bearer_signed_identity_v1` contract; any further change to the
  binding law requires a human architecture decision.
- Rollback must not leave a forgotten listener, tunnel, or proxy.

The qualification predicate
(`scripts/topology_qualification.py::qualify_transport`) encodes this
decision table mechanically and fails closed on every other combination.

## 5. Transport invariants (workstream B3)

Regardless of mechanism, the documented transport MUST:

1. keep request content off untrusted plaintext networks — re-adjudicated by
   order 011-a (D4) for the LAN-visible variant: the supported non-loopback
   surface is the declared trusted private LAN under the full signed ingress
   contract (service Bearer + HMAC-signed identity v1 + replay protection),
   with **no anonymous endpoint** and fail-closed readiness; a "private
   RFC1918 address" alone (without the full signed contract) still never
   qualifies;
2. keep the Local endpoint non-publicly-reachable (loopback-only binding);
3. keep signed identity + service Bearer mandatory (fail closed on absence);
4. fail closed at startup/readiness when the transport is absent
   (`/readyz` 503 until ingress credentials are available);
5. use an endpoint reachable from the Gateway **RUNTIME** network namespace,
   not merely from its host shell (proven by the namespace qualification,
   workstream E); and
6. rollback without leaving a forgotten listener, tunnel, or proxy.

## 6. What this objective did and did not do

Objective 010 (base): no deployment was created or mutated; no Gateway
deployment, Codex profile, firewall/VPN/network state, or protected service
state was changed.

Objective 011 (PR #13, merged 2026-09-17 as
`e860e0bff687afded7782fb2687b5b435792459a`): extended §4 with the supported
LAN-visible signed variant and its per-hop rows (D1/D2/D4), re-adjudicated §5 invariant 1
(trusted-LAN boundary under the full signed contract, no anonymous surface),
bumped the machine-readable manifest to schema v2
(`lan_visible_variant` section, mechanically checked), and extended the
qualification decision table with the signed-contract dimension (workstream
G2). It changed no live state: no deployment was created or mutated, no
Gateway deployment, Codex profile, firewall/VPN/network state, or protected
service state was changed, and no image was published by objective 011.
Objective 013 (PR #15, open as of this writing) implemented the publication
closure (pull-based canonical operator path, activated
`workflow_dispatch`-only release workflow, `docker-published` CI gate,
schema-v3 provenance) and changed no live state either; its registry
publication of the MVP 0.1.0 image to `ghcr.io/ulfe-lmi/slaif-local-coding`
(registry-only; tags `0.1.0` + `sha-<S>`, image source commit `S`, digest
recorded in `packaging/release_record.json`) is PENDING — the 013-a round
ended before publication on the order's R18 hold (the remote Gateway `main`
moved off the pinned peer; strategy must inspect and deliberately
re-qualify; exact delta in the OAP report). The cutover is still not
performed and no real deployment is yet evidenced; the product is NOT yet
released (the registry reference does not exist as of this PR's head). This
document remains the prepare-only topology authority for the next
human-authorized cutover order; the D1 binding law, the loopback default,
and the topology are unchanged.

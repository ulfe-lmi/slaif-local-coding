# SLAIF API Gateway integration

Clients connect to the separate [SLAIF API Gateway](https://github.com/ulfe-lmi/slaif-api-gateway).
The Gateway authenticates public keys, resolves permissions/routes and handles
quota, accounting, administration and TLS. Local Coding handles private model
compatibility, governance and image policies before inference.

Start with [the topology guide](TOPOLOGY.md) to choose a reachable backend
address. Use [INSTALL.md](../INSTALL.md) and the signed configuration template
for deployment. The adapter does not modify Gateway source or deployment.

## Credentials and configuration

Three distinct Local-side environment variables carry three separate roles:

| Variable | Role |
| --- | --- |
| `QWEN3090_API_KEY` | Private model-server credential. |
| `SLAIF_ADAPTER_SERVICE_TOKEN` | Gateway-to-adapter service Bearer. |
| `SLAIF_ADAPTER_SIGNING_SECRET` | Gateway-to-adapter HMAC signing secret. |

The Gateway's public client keys and identity-derivation secret never belong on
Local. Protect the environment file with mode `0600`; reference secret names
from TOML. Never put values in URLs, shell arguments or logs.

Use `service_bearer_signed_identity_v1` and
`constitution.identity_source = "signed_request"`. Signed mode requires the
compiler, governance integration and an observed/governed route, and forbids
static principal/session/repository fallback. The
[configuration reference](ADAPTER-CONFIGURATION.md) lists validation and bounds.

## Signed identity v1

The exact v1 headers are:

```text
Authorization: Bearer <adapter-service-secret>
X-SLAIF-Identity-Version: v1
X-SLAIF-Principal: <opaque>
X-SLAIF-Session: <opaque>
X-SLAIF-Repository: <opaque>
X-SLAIF-Route: <configured-route-name>
X-SLAIF-Timestamp: <canonical-decimal-unix-seconds>
X-SLAIF-Nonce: <unpadded-base64url-or-lowercase-hex-compatible-value>
X-SLAIF-Signature: v1=<64-lowercase-hex-HMAC-SHA256>
```

The HMAC input is UTF-8 newline-separated, with no trailing newline:
`domain/version`, method, path, SHA-256 of raw query bytes, SHA-256 of the
exact bounded body bytes, principal, session, repository, route, timestamp, and
nonce. Query bytes are not parsed or reordered. The adapter compares the HMAC
constant-time, reserves only a SHA-256 nonce digest in bounded process-local
state, and passes one immutable verified identity explicitly to
compiler/cache/rehydration/injection. The effective retention is
`max(admission_time + replay_ttl_seconds, timestamp + clock_skew_seconds)`;
the timestamp horizon is inclusive, and equality is still protected. Expired
digests are reclaimed only after that effective horizon. A full live store
returns fixed 503 `signed_identity_replay_capacity_unavailable` rather than
evicting a protected digest. A detected wall-clock rollback or non-finite clock
returns fixed 503 `signed_identity_clock_unavailable`. Signed/internal headers
are stripped before Qwen. Fixed 401/403/409/422/503 failures do not expose
identity, nonce, signature, body, or secret data and occur before transformation
work. State is digest-only, bounded, process-local, single-worker, and cleared
on restart; no durable or cross-process replay protection is claimed.

The canonical synthetic vector is
[signed_identity_v1_vectors.json](../tests/fixtures/gateway/signed_identity_v1_vectors.json).
Service authentication and signature/replay validation run before transformations
or upstream work. A configured route mismatch is rejected. Public or unsigned
caller headers never establish trusted identity.

## Other ingress modes

`disabled` is a loopback development mode. `service_bearer_static_identity`
authenticates a single configured local-appliance identity; it does not provide
per-user Gateway isolation. Both remain loopback-only and are unsuitable as a
substitute for signed ingress on a shared public-facing deployment.

## API and accounting boundary

The adapter preserves ordinary function tools, incremental SSE ordering and
provider usage subject to its documented route policies and safe error handling.
Image pruning and constitutional replacement change what the provider tokenizes.
The Gateway owns conservative reservation and final accounting; provider usage
is authoritative when available. Internal compiler calls consume upstream
capacity separately and must not be confused with client-visible main-request
usage. Gateway pricing policy remains a Gateway/operator responsibility.

## Compatibility and verification

[Gateway contract CI](GATEWAY-CONTRACT-CI.md) validates the exact peer in
[current_peer_authority.json](../tests/fixtures/gateway/current_peer_authority.json).
The [artifact policy](RELEASE-ARTIFACT-POLICY.md#gateway-compatibility-authority-frozen-for-010)
records the frozen release authority independently of future development re-pins.
Support for arbitrary Gateway revisions is not implied.

Contract tests use a disposable checkout and deny network activity during tests.
Docker qualification exercises signed requests from a separate simulated Gateway
network namespace, including bad signatures, missing credentials, replay,
readiness failures and unreachable cross-namespace loopback.
These checks do not establish a deployed production service. Actual route or
client-profile changes require the [cutover runbook](RELEASE-CUTOVER-RUNBOOK.md)
and separate authorization. Prior integration investigations and acceptance
reports remain indexed in [HISTORY.md](HISTORY.md).

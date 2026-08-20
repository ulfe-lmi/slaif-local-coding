# SLAIF API Gateway integration contract

Repositories remain separate:

```text
ulfe-lmi/slaif-api-gateway   public access-control/accounting plane
ulfe-lmi/slaif-local-coding model compatibility/context plane
```

Production request path:

```text
client -> SLAIF API Gateway -> SLAIF Local Coding adapter -> vLLM
```

## Gateway owns

- public `sk-slaif-*` keys and authentication;
- endpoint/model permissions;
- quotas, reservations, live-burn, pricing, accounting;
- route selection and operator administration;
- public TLS/edge policy and sanitized audit metadata.

## Adapter owns

- model-specific request normalization;
- image-count enforcement;
- constitutional discovery, compilation, cache, and injection;
- upstream vLLM compatibility;
- internal model/compiler scheduling;
- adapter health/readiness/metrics and safe transformation metadata.

The adapter must not reimplement public users, key issuance, quotas, billing, or
admin UI. The gateway must not contain model-specific constitutional-cache or
image-pruning logic.

## Internal identity

The gateway should terminate the external key and forward signed internal
identity, for example:

```text
Authorization: Bearer <adapter-service-secret>
X-SLAIF-Principal: <opaque stable principal UUID>
X-SLAIF-Session: <opaque session/thread discriminator when available>
X-SLAIF-Route: <resolved route UUID/name>
X-SLAIF-Timestamp: <unix timestamp>
X-SLAIF-Signature: <HMAC over method/path/body-hash/headers>
```

Exact header names are a cross-repository contract and require coordinated PRs.
The adapter rejects caller-supplied spoofed internal headers at the public
boundary and never uses raw gateway keys as cache keys.

## Upstream route

The gateway's local-Qwen route points to the adapter, not vLLM. The adapter
holds the private vLLM credential and calls vLLM on loopback/private network.
Direct vLLM access is restricted to the adapter and controlled operations.

## Accounting

The gateway accounts the external request. Internal compiler calls consume GPU
capacity but are not separate user-visible OpenAI calls. The adapter must report
safe compiler token/latency counters so deployment policy can decide whether to
include that overhead in route pricing or internal capacity planning.

Request transformation may change upstream prompt/image token use. The gateway
must finalize from provider-reported usage when available and must not assume
that pre-transformation estimates exactly equal upstream usage.

## Release workflow

Each repository has its own PR/CI/release. A shared deployment manifest pins:

```text
slaif-api-gateway release/commit
slaif-local-coding release/commit
Qwen/vLLM upstream commit
model/checkpoint revision and checksum manifest
configuration schema version
```

An adapter release is not declared gateway-compatible until cross-repository E2E
passes with ordinary Codex and OpenAI clients.

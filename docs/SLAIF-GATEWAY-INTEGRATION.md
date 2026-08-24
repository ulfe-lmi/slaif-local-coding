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

## Current adapter service-ingress contract

The gateway terminates its public client credential and the existing generic
`openai_compatible` provider substitutes a private adapter service Bearer
credential. Local Coding now has an optional, loopback-only ingress gate:

```toml
[gateway_ingress]
mode = "service_bearer_static_identity"
service_token_env = "SLAIF_ADAPTER_SERVICE_TOKEN"
```

The named environment variable is an example name only; its nonempty secret is
kept in a protected runtime environment file and is never placed in TOML,
tests, vectors, logs, metrics, cache names, or reports. Enabled mode requires
the complete configured `constitution` `principal`, `session`, and `repository`
identity and is explicitly a `single-user local-appliance` route. Configured
and supplied tokens share a visible-ASCII, 4096-byte validator. The adapter
verifies exactly one `Authorization: Bearer` value with constant-time
comparison before reading request JSON or invoking image, constitution,
compiler, cache, or upstream work. Missing/duplicate/malformed/oversized or
wrong-scheme authorization returns fixed 401 with `WWW-Authenticate: Bearer`;
mismatches return fixed 403; an unavailable configured secret returns fixed 503.
The adapter strips service authorization and all caller/internal identity,
forwarding, cookie, and hop-by-hop headers before substituting only the Qwen
upstream credential. `/health`, `/v1/models`, `/v1/responses`, and
`/v1/chat/completions` are protected in enabled mode; `/healthz`, `/readyz`,
and loopback-only `/metrics` remain operator endpoints.

## Trusted identity status

The gateway generic provider currently substitutes one backend credential but
does not provide a proven trusted per-request principal/session/repository
contract to Local Coding. Different public-gateway-user simulations therefore
cannot be represented as isolated adapter principals through this service
contract. They must not be separated with public keys, unsigned `X-SLAIF-*`
headers, IP addresses, request IDs, model strings, forwarding headers, or
cookies. Safe deployment is one explicitly single-user Local Coding route and
identity, or `[constitution.rehydration].enabled = false` until coordinated
trusted identity exists. The disabled mode preserves current-request governance
but loses zero-root/post-compaction rehydration and is not multi-user isolation.

The non-active design sketch for a future coordinated contract is:

```text
Authorization: Bearer <adapter-service-secret>
X-SLAIF-Principal: <opaque stable principal UUID>
X-SLAIF-Session: <opaque session/thread discriminator when available>
X-SLAIF-Route: <resolved route UUID/name>
X-SLAIF-Timestamp: <unix timestamp>
X-SLAIF-Signature: <HMAC over method/path/body-hash/headers>
```

This is design material only. Exact names, signature scope, replay window,
key rotation, and gateway implementation require a separate gateway OAP
objective/PR and explicit human authorization. No signed per-user mechanism is
claimed by this repository.

## Dated cross-repository evidence

Evidence captured at Objective-005 activation on 2026-08-24:

| Boundary | Existing capability/evidence | Local Coding state | Missing or not claimed |
| --- | --- | --- | --- |
| Generic provider | Gateway `main` `8f2813bf745b90221da33a7cfaf40726c5b1b480` has the existing `openai_compatible` provider, exact `/v1` backend validation, server-side secret env lookup, provider Bearer substitution, client-key non-forwarding, and quota/accounting behavior. | A disposable pinned checkout run executes the actual `OpenAICompatibleProviderAdapter` against a Local Coding candidate and fake vLLM for Responses JSON and SSE, proving model/credential/usage/event facts. | No gateway source change, gateway PR, accounting path, or live gateway-service deployment proof was made in this round. |
| Route/profile | Open gateway OAP PR #287 is `oap/152-real-provider-accounting-qualification` at `346cdc13bcc1eb42035fb1d6a3e82c137651f4a4`; the isolated Qwen3.8 vision Codex candidate is unregistered/live-unqualified and records Codex 0.148.0. | Local Coding preserves explicit route/model policy and uses the current adapter contract. | Current Codex is 0.149.0; candidate profile mismatch and live qualification remain unresolved. |
| Host deployment | No gateway checkout or gateway service, PostgreSQL/Redis, or gateway listener was found on hinton1 at activation; protected Qwen vision remains on port 18020 with context 100000 and text remains inactive. | No service, profile, network, or protected Qwen mutation. | Live gateway path and cutover are `NOT RUN`; no production or multi-user claim. |
| Identity | Existing provider has one backend service credential. | Static constitution identity is the only accepted cross-request identity in enabled mode. | Trusted signed per-user principal/session/repository isolation is missing. |

### Pinned gateway capability audit

At gateway SHA `8f2813bf745b90221da33a7cfaf40726c5b1b480`,
`slaif_gateway.schemas.providers.ProviderRequest` has `extra_headers`, but its
fields do not contain client or gateway key material. The pinned
`build_provider_headers` allowlist retains only `Accept`, `Content-Type`,
`Content-Length`, and `X-Request-ID` from extras; authorization, cookie, token,
session, gateway, and identity-like fragments are filtered while the configured
provider Bearer is substituted. The existing Responses service constructs a
`ProviderRequest` without trusted Local Coding principal/session/repository
headers. Configuration alone therefore cannot establish signed per-user
identity. The executable driver records this source evidence and its bounded
JSON/SSE result; it does not invoke PostgreSQL, Redis, quota, or accounting
services.

The bounded 005-b driver run used the pinned checkout and repository-only
`scripts/gateway_provider_driver.py` support. `OpenAICompatibleProviderAdapter`
`forward_response` returned HTTP 200 with total usage count 5 and the fake
upstream observed model `qwen3.8-27b`; `stream_response` returned HTTP 200
equivalent evidence with three events in order:
`response.created`, `response.output_text.delta`, `response.completed`. The
candidate accepted the service credential, the fake vLLM accepted only its
configured synthetic upstream credential, metrics were secret-free, and the
temporary servers/cache were cleaned up. This is direct provider-adapter
compatibility evidence only, not gateway service, quota, ledger, or cutover
evidence.

The repository-owned bounded vectors are in
`tests/fixtures/gateway/openai_compatible_vectors.json`. They contain no
credentials, raw prompts, source, images, tool output, private URLs, or raw
authorization values.

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

## Controlled cutover and rollback gates — preparation only

Objective 005-a does not perform cutover. A later accepted continuation must
prove, in order:

1. a merged/green Local Coding version and pinned gateway commit;
2. exact backups and hashes of gateway route/provider metadata, the Codex
   profile, unit files, environment files, listener/firewall state, and the
   current direct Qwen endpoint;
3. a candidate Local Coding service on loopback port `18031` first;
4. the gateway generic provider points to Local Coding, never directly to
   vLLM;
5. bounded standard OpenAI-client and real Codex text/tool/SSE/vision/
   governance checks through the gateway;
6. exact gateway quota reservation/finalization/ledger facts from provider
   usage, with compiler overhead observed separately;
7. no active coding or strategic turn depends on the endpoint being switched;
8. direct vLLM exposure is retained until gateway-path acceptance and human
   approval;
9. rollback restores the exact prior provider route/profile/unit and health;
10. final listener/firewall/VPN/service state is independently verified.

Because no gateway service is installed or running on hinton1, the actual
cutover and rollback proof are `NOT RUN`. No direct-vLLM retirement, public
listener, TLS, database, Redis, Docker, gateway OAP workflow, or Codex profile
change is authorized by this order.

## Objective-005-c disposable rehearsal result

The bounded 2026-08-24 rehearsal was `FAILED`, not acceptance. The detached
gateway checkout was the exact pinned main commit
`8f2813bf745b90221da33a7cfaf40726c5b1b480`. A temporary PostgreSQL 16
container used loopback-only random port allocation and a tmpfs-only database;
the seed used gateway repositories/services for the provider, route, pricing,
and synthetic public key.

The public `/v1/models`, non-streaming Responses text, one Responses SSE
sequence with completed usage, and one small inline image request reached the
Local Coding candidate and protected Qwen fixture. The candidate used the
synthetic service credential and the Qwen credential remained a candidate-side
environment reference. PostgreSQL rows observed for the completed subset had
one finalized reservation and ledger row per successful public request, no
pending reservation, and provider usage available for finalization.

The real Codex 0.149.0 invocation did not complete: the gateway rejected the
Codex tool envelope before a public reservation was created. No gateway or
adapter policy was weakened to force it through. Temporary listeners,
container, image, cache, gateway process, candidate process, Codex home, and
fixture state were removed; the protected vision PID/start facts and port
18020 listener were unchanged. This remains a failed rehearsal and does not
prove gateway Codex compatibility, accounting completeness for the Codex
portion, production readiness, or cutover safety.

During bounded diagnosis, a read-only search accidentally traversed the host
Codex session cache and exposed sensitive session content to local tool output.
Further live probing was stopped. No session content is retained in this
repository, report, metrics, or driver facts.

## Objective-005-d containment and tool-envelope differential

Objective-005-d records the incident and bounded containment in
[the security-containment record](OBJECTIVE-005D-SECURITY-CONTAINMENT.md).
Repository-only capture support now confines Codex homes, catalogs, output,
and diagnostic paths to driver-owned temporary roots, rejects home-relative or
traversal paths, and requires an explicit subprocess allowlist. No script
constructs a host Codex session/history/cache search. Bounded evidence contains
only validated top-level tool-type counts and fixed policy facts; request
bodies, headers, prompts, schemas, tool names, images, and session identifiers
are discarded immediately.

At pinned gateway SHA `8f2813bf745b90221da33a7cfaf40726c5b1b480`, four
predetermined Codex 0.149.0 global-yolo variants were captured through a
loopback fake Responses provider and fed directly to the gateway's actual
Responses request policy plus the same synthetic route capability metadata used
by 005-c. The variants were: the disposable baseline; `--ignore-user-config`
with `apps`, `browser_use`, and `computer_use` disabled; that variant with
`standalone_web_search` also disabled; and an ignore-user-config disposable
catalog-only search-disabled variant. Each retained ordinary `function`/`custom`
declarations. The first three retained both `tool_search` and `web_search`; the
catalog-only variant removed `tool_search` but retained `web_search` and exposed
`namespace`. All four were rejected by the unchanged policy before route,
rate-limit, or quota reservation with fixed error type
`invalid_request_error`, code `responses_hosted_tool_not_supported`, and fields
`tools[6].type` or `tools[7].type`.

Therefore unchanged-gateway configuration-only compatibility was **not found**.
No gateway code was changed or authorized, no request body was altered, and no
hosted capability was silently stripped. The corrected repository-only 005-c
driver emits a fixed preflight result before any Docker/PostgreSQL/gateway/
adapter/Qwen stage and refuses the full rehearsal when this policy rejection
remains. No full rehearsal was rerun in 005-d. Live gateway, adapter, Qwen,
Docker, PostgreSQL, cutover, and production acceptance remain `NOT RUN`.

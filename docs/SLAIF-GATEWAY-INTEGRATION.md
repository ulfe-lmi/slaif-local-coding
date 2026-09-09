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
does not emit trusted per-request identity to Local Coding. Local Coding now
implements the adapter-side `service_bearer_signed_identity_v1` verifier as a
prepared, disabled-by-default contract. Its configuration requires a separate
visible-ASCII HMAC secret, bounded clock skew/replay TTL/nonce state, and
`constitution.identity_source = "signed_request"`; static identity is forbidden
as a fallback.

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
TTL/LRU state, and passes one immutable verified identity explicitly to
compiler/cache/rehydration/injection. Signed/internal headers are stripped
before Qwen. Fixed 401/403/409/422/503 failures do not expose identity, nonce,
signature, body, or secret data and occur before transformation work.

The exact synthetic conformance vector is
`tests/fixtures/gateway/signed_identity_v1_vectors.json`.
Gateway-side support for this adapter contract is **NOT IMPLEMENTED** and **NOT
AUTHORIZED**: the current gateway's existing provider filter emits no signed identity. A
separate gateway OAP PR, human authorization, key-derivation/rotation design,
route capability, negative/security tests, accounting checks, and
cross-repository conformance review are required before enabling this mode.
Until then, safe deployment remains explicit static single-user identity or
rehydration disabled; unsigned `X-SLAIF-*` headers never establish identity.

## Dated cross-repository evidence

Evidence captured at Objective-005 activation on 2026-08-24:

| Boundary | Existing capability/evidence | Local Coding state | Missing or not claimed |
| --- | --- | --- | --- |
| Generic provider | Gateway `main` `8f2813bf745b90221da33a7cfaf40726c5b1b480` has the existing `openai_compatible` provider, exact `/v1` backend validation, server-side secret env lookup, provider Bearer substitution, client-key non-forwarding, and quota/accounting behavior. | A disposable pinned checkout run executes the actual `OpenAICompatibleProviderAdapter` against a Local Coding candidate and fake vLLM for Responses JSON and SSE, proving model/credential/usage/event facts. | No gateway source change, gateway PR, accounting path, or live gateway-service deployment proof was made in this round. |
| Route/profile | Open gateway OAP PR #287 is `oap/152-real-provider-accounting-qualification` at `346cdc13bcc1eb42035fb1d6a3e82c137651f4a4`; the isolated Qwen3.8 vision Codex candidate is unregistered/live-unqualified and records Codex 0.148.0. | Local Coding preserves explicit route/model policy and uses the current adapter contract. | Current Codex is 0.149.0; candidate profile mismatch and live qualification remain unresolved. |
| Host deployment | No gateway checkout or gateway service, PostgreSQL/Redis, or gateway listener was found on hinton1 at activation; protected Qwen vision remains on port 18020 with context 100000 and text remains inactive. | No service, profile, network, or protected Qwen mutation. | Live gateway path and cutover are `NOT RUN`; no production or multi-user claim. |
| Identity | Existing provider has one backend service credential and emits no trusted Local Coding identity. | Adapter-side signed identity v1 verifier, replay bounds, canonical vector, and request-scoped cache/rehydration propagation are prepared behind explicit mode. | Gateway derivation/emission, key rotation, route capability, cross-repository acceptance, and cutover remain missing/not authorized. |

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

The route-scoped Codex tool-envelope vector is
tests/fixtures/gateway/responses_tool_filter_vectors.json; the non-active
gateway-side proposal is documented in
GATEWAY-ROUTE-SCOPED-CODEX-TOOL-FILTER-PROPOSAL.md. The vector is content-free
and records the exact gateway precondition, adapter postcondition, and
one-public-request accounting contract. It does not authorize gateway changes
or claim that the current gateway accepts the envelope.

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

## Objective-005-p / 005-q harness correction

Objective-005-p repairs the repository-only acceptance harness; it does not
change Gateway or Local product semantics. The permanent runner is
`scripts/gateway_accounting_rehearsal.py`, with the closed C1–C5/D obligation
manifest and predicates in `tests/helpers/acceptance_harness.py`. Fake mode
executes the exact clean Gateway pin, Local candidate, synthetic PostgreSQL,
strict fake Qwen, and task-controlled Codex 0.149.0 in private temporary state.
Every provider call/lifecycle fact is observed at the fake boundary and is
independent of Gateway reservation/ledger counters. The runner fails closed on
missing obligations, retries, skipped stages, unsafe cleanup, or incomplete
rollback evidence.

The 005-q continuation fixes the fake provider's recursive SSE writer,
exercises the function and message lifecycles over loopback HTTP, and adds an
explicit runtime projection for every fake-selected C1–C5/D obligation. The
machine result retains ordered result records and bounded projection metadata;
`missing=[]` is not completion unless every selected result is independently
observed and `PASSED`. The exact full-chain attempt reached C1 and the first
vision turn, then stopped at C3.1: clean Gateway
`9d247e7f3d8fd6a588976840c4657181b7486b81` rejected the prior assistant
`output_text` content in the Codex 0.149 resume request before Local admission.
The fake function-stream repair is tested, but the exact Gateway/Local/fake
vision gate remains `BLOCKED` pending an authorized Gateway compatibility
change; no relay or Gateway source change was introduced here.

005-q does not retrieve the protected Qwen credential or make authenticated,
model, inference, or vision calls. It does not install a candidate, edit a
Codex profile, or mutate the protected service, network, model, or port 18020.
The exact 005-o stream result remains a real protected failure, but its
`gateway_stream_owned` ownership assertion was not established: a Gateway
error after Local HTTP 2xx and zero Local failure delta is classified as
`gateway_rejected_stream_owner_unresolved` unless an independently valid
provider lifecycle and exact clean Gateway-validator conflict prove
`gateway_product_defect`. This correction does not rewrite 005-o or claim
real-matrix, acceptance, cutover, or release readiness.

## Objective-005-r / Gateway Objective-161 continuation

The active 005-r continuation uses the accepted, merged Gateway Objective-161
implementation at exact clean detached SHA
`50dcc3b85d614eb1d0c6196595bf22ef5779f846`. Its separate immutable Gateway
report is `ad1c556a539130c08dc1063b3e9a25a0af2e5a85`, whose first parent is
that implementation SHA; the merged Gateway main authority is
`d142fd7f04c46fac3469b9b9bba1bd2068aabad8`. These are provenance facts, not
Local or Gateway code changes in this repository.

005-r first re-observes the complete repository-only fake C1–C5/D matrix
through actual Codex 0.149.0, Gateway, Local, and the strict fake provider,
including the same-session full-image then resumed crop/history request. Only
an entirely passing fake machine gate permits one bounded protected matrix
against the pre-existing vision service on port 18020. Protected credentials,
model traffic, and service state remain outside the fake phase; no restart,
profile change, cutover, or release is implied. Results and remaining limits
belong to the immutable 005-r report, while the 005-q report and earlier
terminal artifacts remain unchanged historical evidence.

The fresh 005-r fake run completed the exact machine gate with 37/37 selected
C1–C5/D obligations `PASSED`, `missing=[]`, null first failure, zero retries,
and bounded cleanup. The single authorized protected attempt reached the
existing vision-Qwen service through the exact Gateway and Local candidate,
with the protected service identity and listener unchanged. Protected
provider-call and terminal-lifecycle facts could not be observed independently
without a provider relay or protected-service mutation, so protected C1.1
failed closed and the protected matrix is not accepted. The runner now stops
before later protected inference when that boundary is unavailable; no
protected retry, cutover, or release is claimed.

The 005-s runner does not retry protected traffic. Its fake-only qualification
uses the existing Local `create_app(settings, transport=...)` seam with a
direct HTTPX transport observer inside the disposable candidate; it adds no
relay and makes no protected-service mutation. The observer keeps attempted,
dispatched, responded, and completed states separate, classifies compiler and
public inference independently, and parses only bounded event/usage facts
while passing the same request and stream through to the real loopback fake
transport. Its facts are cross-checked with independent fake-server counters
and bound to the exact ordered projection table, candidate source/harness
identity, route policy, Gateway pin/app tree, Codex version/checksum,
implementation SHA, and run provenance. Observer readiness and candidate,
identity, and budget prerequisites are established before any credential read
or provider dispatch; a lost observer stops later dispatches.

## Objective-005-t strict observer and evidence correction

005-t retains the direct Local transport architecture and injects the exact
clean Gateway `50dcc3b85d614eb1d0c6196595bf22ef5779f846` Responses stream
validator plus its request-scoped Codex 0.149 route/tool profile. The Local
observer owns only bounded framing and safe facts: LF/CRLF, split-at-every-byte,
coalesced events, comments, frame/stream caps, payload/event-type agreement,
and fixed error/event classes. It does not retain raw event names, response
IDs, paths, exception types, request bodies, arguments, or credentials.

Semantic validation is not a prefix or display-bucket check. The pinned
Gateway validator enforces the approved event payloads, response-ID and
sequence relationships, lifecycle/item relationships, terminal output, and
usage contract. Exact integer counts are compared against independent fake
provider counters before bounded display classes; merged disposable lifetimes
remap per-lifetime ordinals to unique global ordinals and preserve any prior
failure. Invalid, overflowed, truncated, cancelled, delegated, or abnormally
closed streams latch observer failure and prevent every later dispatch.

The fake-result gate reads an owned regular descriptor with a cap-plus-one
bounded read, rejects duplicate JSON keys/non-finite values and malformed
nested evidence, and permits a report-only descendant only while relevant
source/config state remains clean. Independent negative tests cover missing,
duplicate, reordered, extra, false, stale, skipped, failed, retried, unsafe,
oversized, and mismatched evidence.

The fresh fake run at implementation
`45f9d64976b0f2a44f6c3223d767c28f5405e1a` passed 37/37 selected obligations
with zero missing/first-failure/retry results. Exact observer facts were 23
total operations (6 compiler, 12 inference, and 5 other), all 23 completed
and terminal-valid; all 12 inference operations had first-byte and normal-close
facts. Fake-provider counters matched independently, temporary resources were
cleaned, and logs were secret-free. No protected credential, inference, Qwen,
network, active-profile, or cutover state was accessed or changed in 005-t.

## Objective-005-u stream closure and pre-dispatch proof

005-u keeps the direct Local transport and exact pinned Gateway validator
architecture unchanged while closing two observer safety gaps. Stream
observation finalization is now separate from delegate closure. Normal JSON and
SSE exhaustion, explicit early close, cancellation, timeout, truncation, and
delegate exceptions close the underlying stream exactly once; repeated close is
idempotent, original stream errors/cancellation remain authoritative, and a
cancelled, truncated, or abnormally closed stream is never terminal-valid.

A bounded loopback server and the real HTTPX `AsyncHTTPTransport` test sends a
first SSE frame, waits for the client to receive it, and only then releases the
terminal frames. The test checks first-byte backpressure, exact body bytes,
status/headers, delegate closure/connection return, and the single dispatch.
Framing and semantic unit tests remain bounded, while the existing fake matrix
continues to use the actual pinned Gateway `ResponsesStreamEventValidator` and
request-scoped candidate factory.

Validator/profile construction is an admission prerequisite for Responses
inference and occurs before `delegate.handle_async_request`. Missing, raising,
or invalid factories therefore cause zero upstream dispatch, record the
attempt separately, latch observer readiness, and block subsequent inference
admission. Compiler and health requests retain their non-inference handling;
candidate startup checks that inference capability is actually present.

Fake-gate source reuse is round-neutral and Git-topology checked. A tested head
may be reused directly, or only through one verified single-parent immutable
report-publication child that adds exactly its corresponding report and names
the tested implementation SHA. Dirty relevant source/config state, production
or harness descendants, malformed reports, multi-parent commits, and unrelated
changed paths fail closed. No protected Qwen credential, inference, service,
network, active-profile, or cutover state is authorized in 005-u.

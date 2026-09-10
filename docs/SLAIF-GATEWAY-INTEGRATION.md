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
and terminal-valid; 6 inference operations were SSE streams with first-byte
and normal-close facts, while 6 were normal JSON responses. Fake-provider counters matched independently, temporary resources were
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

## Objective-005-v qualified observer and protected attempt

005-v extends the existing direct Local observer to the one authorized
protected attempt. Protected admission first validates a fresh complete fake
machine gate bound to the exact Local source/harness, Gateway pin, route
policy, Codex version/checksum, and observer. It then verifies the unchanged
vision-service baseline, resolves only the active unit MainPID, and reads only
the unique nonempty `VLLM_API_KEY` entry from that process environment into
memory. The observer remains inside Local; no relay, Qwen instrumentation,
service restart, configuration change, profile change, or network change is
permitted.

The fresh 005-v fake qualification passed 37/37 selected obligations with zero
missing/first-failure/retry results, exact direct-observer/fake-provider
agreement, 12/12 terminal-valid inference operations, cleanup, and
secret-free logs. The single protected attempt reached the candidate/provider
path but ended with fixed harness `KeyError` evidence after observer readiness
was lost, before a structured protected acceptance gate was produced. No
protected retry was made. Later protected matrix obligations, cutover, and
release readiness remain `NOT RUN`; this result is not protected acceptance.

## Objective-005-w protected projection and failure retention

005-w repairs the Local harness evidence boundary using explicit mode-specific
projection tables. Protected mode has a direct `C5.4` fixture projection and a
separate observation schema, so finalization cannot look up a protected row in
the fake table. Coverage, uniqueness, unknown IDs, and ordering are validated
before any credential, candidate-readiness, or provider-dispatch hook. Fake
provider/server facts remain ineligible for protected provider predicates.

The runner's bounded payload-free accumulator preserves mode, candidate/Gateway
pins, phase/ordinal, first fixed failure, exact compiler/public inference
attempted-dispatched-responded-completed counts, observer failure and terminal
classes, and cleanup state before teardown. Finalization is total across normal,
partial, observer-unready, validation, timeout, cancellation, client/parser,
and cleanup-failure exits. A later projection or serialization error is recorded
as a secondary fixed class and cannot overwrite the primary failure or counts;
unknown observations remain `UNKNOWN`/`NOT RUN`, never zero or `PASS`.

Admission control enforces the unchanged 900-second wall bound, ordered
single-attempt/zero-retry public-operation budgets, 16 KiB event cap, 128 KiB
stream cap, and single-phase concurrency before dispatch. The fake-only
synthetic protected-mode conformance path uses injected hooks to verify
protected phase selection, direct-observer requirements, first-failure stop,
cleanup snapshot retention, and serialization of every selected row. It reads
no real credential and makes no protected Qwen call; these facts do not claim
protected inference acceptance, cutover, merge, or release readiness.

## Objective-005-x runner budget and terminal proof

005-x keeps the 005-w observer/app-factory topology and closes its three
repository-only harness gaps. `RunAccumulator` retains exact per-lifetime
compiler/inference lifecycle counts separately from semantic terminal-valid
observations. A terminal-valid class is emitted only from an observer record
validated by the pinned stream validator and the expected terminal relationship;
equal attempted/completed counts alone are insufficient. Invalid-but-consumed,
truncated, cancelled, and absent observations remain distinct fixed classes,
including `UNKNOWN` where no semantic observation exists.

The run-owned `BudgetController` now admits every actual direct observer
dispatch immediately before delegate invocation. Operation-attempt reservations
remain separate from individual compiler, inference, and other request counts;
each dispatch records only its safe phase/ordinal attribution. The same
controller checks the 900-second deadline before dispatch and between stream
chunks, enforces the existing event/stream/64-observation limits, holds
single-phase concurrency for the full response-stream lifetime, and prevents
later delegate calls after a latched failure. Sequential candidate lifetimes
share the controller, so aggregate limits cannot reset when an observer is
recreated.

The actual shared runner exposes explicit synthetic-only protected-boundary
hooks for repository tests: host preflight, MainPID, credential source,
loopback provider selection, bounded clock, dispatch observation, and injected
failure points. Missing hooks fail closed. Synthetic conformance serializes all
29 protected-selected dispositions and is labelled orchestration evidence only;
it cannot read `/proc`, protected credentials, or call port 18020. The healthy
qualification path remains the actual Gateway → Local → strict fake-provider
path. Protected inference acceptance, cutover, merge, and release readiness are
not implied.

The fresh exact pinned fake rehearsal at implementation
`63920a4fa1339f013b51e64b22c233917e21f7aa` passed its machine gate: 37/37
selected obligations and projections, 23/23 direct observer dispatches,
`6` compiler and `12` inference dispatches, `12/12` terminal-valid inference
operations (6 SSE streams and 6 normal JSON responses), exact fake-provider agreement, all 29 synthetic protected
row dispositions, and task-resource cleanup. This remains fake-only evidence;
no protected credential, Qwen request, or port-18020 mutation occurred.

## Objective-005-z exact pin, operation permits, and protected-branch conformance

005-z makes the existing operation/request distinction executable and binds it
to the exact retrieved Gateway ancestor. The repository-only controller has a
finite 25-slot plan (6 compiler, 14 inference, 5 other). A fresh run may
consume fewer slots; the allowance is not a measured request count. Reservation
never advances the current operation: a caller explicitly
activates the exact operation, phase, ordinal, and lifetime, and each request
consumes only the matching kind slot at the direct HTTPX observer immediately
before delegate invocation. Missing, exhausted, wrong-kind, wrong-phase,
wrong-ordinal, stale-lifetime, and expired-run requests fail closed without a
delegate call. The nine logical operations remain maximum-one with zero
retries and retain the prior wall, observation, frame, stream, and concurrency
maxima.

The actual Codex turn transition is authorized only after a terminal-valid
turn-1 inference response. Candidate qualification records bounded `/healthz`
and `/readyz` results separately. If a post-dispatch hook raises after the
delegate returned, the observer closes that returned stream exactly once,
preserves the responded fact, and releases the dispatch slot.

The fresh exact pinned fake qualification passed all 37 C1–C5/D obligations
and projections. It recorded 23 actual direct dispatches (6 compiler, 12
inference, 5 other), 12/12 terminal-valid inference operations (6 SSE
streams and 6 normal JSON responses), exact
fake-provider agreement, candidate `/healthz` and `/readyz` status 200, and
clean disposable resources and secret-free logs. The 25-slot plan is an
authorization ceiling rather than a measured request count. The exact Gateway
executable ancestor `50dcc3b85d614eb1d0c6196595bf22ef5779f846` was retrieved
and verified against merged-main ancestry and app-tree identity.

The healthy synthetic protected branch ran through the same shared runner with
a disposable loopback provider and recorded 6 compiler and 12 inference
operations, all 29 protected dispositions, no primary failure, and unchanged
protected-fixture facts. It remains explicitly non-accepting: no protected
credential, Qwen request, port-18020 mutation, cutover, merge, or release claim
is made. Observer, projection, and cleanup failure injections preserve the
primary failure, serialize all 29 rows, and perform no later inference.

SSE enforcement is split at the correct boundary. Network chunks contribute to
the cumulative stream byte limit; completed frames are checked independently
against the 16 KiB frame limit by the incremental parser. Coalesced legal
frames are not rejected merely because their containing network chunk is larger
than one frame, while an oversized frame or stream stops subsequent dispatch
and closes the delegate.

The shared protected-mode runner supports synthetic-only healthy and
post-dispatch failure/finalization executions through the existing
`ProtectedRuntimeHooks` seam. It records bounded phase traces, exact
compiler/inference lifecycle counts, selected protected dispositions, source
identity classes, primary/secondary failures, and cleanup snapshots. These
executions use only a disposable loopback provider and retain
`protected_acceptance=false`; they are orchestration evidence, not protected
inference acceptance, cutover, merge, or release readiness.

## Objective-005-aa protected predicate and startup-budget closure

The protected synthetic conformance result now qualifies only when its nested
protected `acceptance_gate` has every selected obligation and projection
`PASSED`. Serialized rows and an empty accumulator failure are insufficient;
`protected_acceptance=false` remains explicit. A normalized provider boundary is
used only for the explicit disposable loopback synthetic branch. Real protected
transport counts do not prove provider request classes, tool relationships, or
semantic terminality, and topology evidence remains a separate projection.

Candidate startup uses the same lifetime-bound direct observer as inference.
`/readyz` receives one explicit readiness permit whose only upstream dispatch is
`/health`; it is counted against the shared dispatch ceiling and retired after
use. Local `/healthz` listener polling can retry, but readiness/provider health
requests do not retry outside the run controller. Missing, stale, or different
observer lifetime contexts fail before delegation.

The final 005-aa evidence is retained under
`oap/evidence/005-aa/index.json`, bound to tested source
`ee72a19d45a5eaba0329daaddd571742ca81a586` and the evidence-only descendant
`2a7420998e3734d929142f3da0efdcf2664292f9`. The fresh fake gate passed 37/37
obligations and projections with 26/26 direct dispatches (6 compiler, 12
inference, 8 other), including 3/3 consumed readiness permits. The healthy
synthetic protected gate passed 29/29 rows; observer, combined
projection/cleanup, and pre-dispatch cases failed closed with all 29 rows
serialized and bounded primary/secondary failure classes. No real protected
access was made.

## Objective-005-ab shared protected observation path

The protected synthetic branch now uses the same direct HTTPX observer as the
outer fake qualification to derive provider semantics from actual
Gateway-to-Local-to-provider traffic. Synthetic hooks replace only protected
host, process, credential-source, clock, and physical-provider boundaries. The
fake provider's semantic oracle is disabled in this branch and cannot satisfy
protected predicates. Request classes, tool classes, item-ID presence,
matching call-ID relation, approved fixture hashes, bounded response lifecycle,
and stream terminality are projected from the observer and the accepted
Gateway Responses validator.

Protected preflight performs exactly one explicitly permitted GET `/health`
and one GET `/v1/models` against the disposable physical provider. Both are
endpoint/method-scoped, admission-counted, deadline-bounded, and included with
the three candidate readiness health requests. No retries or unbudgeted
provider probes are available.

The permanent runner records four serial synthetic cases: healthy
oracle-disabled qualification, observer failure after known compiler and
inference dispatch, combined observer/projection/cleanup failure, and genuine
pre-dispatch mapping/dependency failure. Every case emits all 29 protected
rows and fixed counts/classes; the pre-dispatch case proves zero credential
hook and provider dispatches before cleanup. This is repository-only
orchestration evidence and remains `protected_acceptance=false`; it is not
protected inference acceptance, cutover, merge, or release readiness. The
sanitized machine evidence is under `oap/evidence/005-ab/`.

## Objective-005-af same-UID protected acceptance

005-af preserves the exact 005-ae observer, source-bound fake gate, protected
projection, and no-whole-harness-elevation boundary. Fake qualification and
evidence validation run as the current UID against an owned 0600 regular file;
the existing bounded Docker helper remains the only privileged operation.

The composed fake run adds a bounded Gateway-boundary ownership-negative
proof after the real id-less companion. It uses the existing two test keys to
exercise missing-call-ID, mismatched-call-ID, and wrong-key continuation
requests. The generated facts require all three 4xx denials before provider
advancement, unchanged provider and per-key accounting, and zero pending or
duplicate request IDs. No extra inference request or Gateway implementation
change is introduced.

The resulting source-bound evidence is retained under `oap/evidence/005-af/`.
One protected matrix is attempted only after the clean fake gate, all required
checks, unchanged vision-service preflight, and same-UID evidence validation.
Protected acceptance, installed cutover, merge, and release readiness remain
separate decisions.

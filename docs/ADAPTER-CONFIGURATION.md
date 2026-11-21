# Adapter configuration and operations

Start with `config/adapter.gateway-integrated.template.toml` for signed Gateway
ingress, or `config/adapter.example.toml` for loopback development. Unknown fields,
policies, duplicate route names, duplicate `(model, endpoint)` matches,
non-loopback listeners without the full signed ingress contract, invalid
bounds, and routes that do not uniquely match a request fail closed at
settings validation/startup. Application code has
no hard-coded upstream address. The example address is host-specific candidate
configuration, not a public endpoint.

## Listener address (`[server].listen_host`)

The listener is validated according to ingress mode:

- **Always accepted (every ingress mode):** the loopback literals
  `127.0.0.1`, `::1`, and `localhost`. Loopback `127.0.0.1` remains the
  default and remains the only permitted bind when `gateway_ingress` is
  `disabled` or `service_bearer_static_identity`.
- **Accepted only under the full signed ingress contract:** bare IPv4/IPv6
  literals and the all-interfaces literals `0.0.0.0`/`::` are accepted **if
  and only if** `gateway_ingress.mode = "service_bearer_signed_identity_v1"`
  (service Bearer + signed identity v1 + replay protection). A non-loopback
  bind with any other ingress mode is rejected at settings validation
  (fail closed, precise error message).
- **Always rejected:** hostnames, schemes, ports, and malformed values (the
  syntactic validator rejects them in every mode).

The authentication/integrity contract is unchanged and remains mandatory in
every non-loopback configuration; the Qwen hop remains true host loopback.
The configuration matrix is mechanically tested in
`tests/test_config.py` and
`tests/test_gateway_integrated_deployment.py`.

## Metrics host policy (`[observability].metrics_host`)

`metrics_host` is a **configuration-level loopback declaration only**, not a
second network binding: `/healthz`, `/readyz`, and `/metrics` are all served
on the single adapter socket (one uvicorn process) at `listen_host`.
`metrics_host` is constrained to loopback literals by the validators and
documents that the metrics surface never gains an independent bind. On a
LAN-visible adapter bind, `/metrics` is reachable from the same trusted
surface as the rest of the socket and exposes state/counts only (no raw
content); this is accepted and documented in
[DOCKER-SECURITY-DELTA.md](DOCKER-SECURITY-DELTA.md).

The deployment templates are explicitly labeled:
`config/adapter.deployment.template.toml` is the **development/local
candidate (NOT production)** (ingress disabled);
`config/adapter.gateway-integrated.template.toml` is the **final
Gateway-integrated configuration** (signed ingress + signed-request
constitution identity). In the Gateway-integrated configuration,
`[gateway_ingress]` `mode = "service_bearer_signed_identity_v1"` requires
`service_token_env` and `signing_secret_env`, the fixed accepted contract
defaults, and — enforced by the configuration validators — an enabled
constitution integration with `identity_source = "signed_request"` and no
static principal/session/repository labels, an enabled direct compiler, and
at least one route with `observation_enabled` and `constitution_enabled`.
The three Local-side secret roles (`upstream.api_key_env`,
`gateway_ingress.service_token_env`, `gateway_ingress.signing_secret_env`)
must use **three distinct environment names**; any shared name fails closed
at settings validation. With signed ingress, `/readyz`
reports `gateway_ingress = "ready"` only when both ingress credentials are
available (fail closed).

## Credentials and request bounds

The upstream credential is read from the environment variable named by
`api_key_env`. Optional `[gateway_ingress]` service authentication is disabled
by default. In `service_bearer_static_identity` mode, the adapter accepts one
`Authorization: Bearer` credential from the environment variable named by
`service_token_env` on the private proxy endpoints (`/health`, `/v1/models`,
`/v1/responses`, and `/v1/chat/completions`) and verifies it with a
constant-time comparison before reading or transforming request JSON. Missing,
duplicate, malformed, oversized, wrong-scheme, or mismatched credentials are
fixed 401/403 errors; an unavailable configured secret is a fixed 503. The
service credential is never forwarded upstream. This mode requires the complete
enabled static `principal`/`session`/`repository` constitution identity and is
explicitly a single-user local-appliance contract, not per-gateway-key or
multi-user isolation. `/healthz`, `/readyz`, and private `/metrics` remain
operator endpoints; readiness exposes only the fixed `gateway_ingress` state.

Configured and supplied service tokens share one validator: nonempty visible
ASCII bytes (`0x21..0x7e`) with a maximum of 4096 encoded bytes. Authorization
must contain exactly one `Bearer <token>` value; whitespace, controls, Unicode,
extra segments, duplicate headers, and over-limit values fail before body work.

Caller `Authorization`, public gateway credentials, internal identity/debug
headers, and hop-by-hop headers are not reused as trusted upstream credentials
or metadata. Logs and metrics contain bounded endpoint, configured route,
status, timing, stream, failure, and image-count labels only; raw bodies and
secrets are excluded.

`request_body_max_bytes` and `response_body_max_bytes` are independent finite
limits. A non-streaming upstream response over the response cap is closed and
returned as a sanitized 502. Streaming remains incremental and is bounded by
HTTPX/ASGI backpressure and read timeouts. The CLI disables Uvicorn access logs
so opaque query strings are not emitted by the default server logger.

The adapter incrementally consumes each request body and stops once the hard
`request_body_max_bytes` cap is exceeded. It rejects a known oversized
`Content-Length` early but still counts actual streamed bytes when the header is
missing or misleading. Body size and structure are independent resource limits:
before JSON decoding or recursive image work, a string/escape-aware iterative scan
enforces `json_max_nesting_depth`. The example limit is 128 containers, inclusive;
an object or array that would enter depth 129 returns API-shaped HTTP 400 code
`json_nesting_too_deep`, with no upstream call. Parser or transformation recursion
at this narrow boundary receives the same sanitized response. Brackets and braces
inside JSON strings do not count. The setting accepts 1 through 256, so configuration
cannot move recursive application work near interpreter recursion exhaustion.

The `[observation]` table validates conservative finite limits and version labels.
Each `[[routes]]` entry opts in with `observation_enabled`; disabled routes perform
no constitution work. Enabled observation runs after image policy and produces an
ephemeral typed manifest only. It never reads paths, persists source, calls an
internal/model service, caches state, or rewrites/injects governance. An overflow
marks the manifest incomplete with a fixed reason while preserving forwarding
semantics. Metrics expose only endpoint, configured route, fixed evidence/status/
reason labels, counts, and duration—not source paths/content/hashes, identity hints,
tool text, queries, or authorization. Caller-supplied identity/session headers
remain spoofable and are stripped. The service-Bearer gate authenticates the
single configured appliance identity; signed mode instead accepts only the
versioned, replay-protected adapter-side contract described below.

## Signed Gateway identity v1

`service_bearer_signed_identity_v1` requires both `service_token_env` and a
separate `signing_secret_env`. The signing secret uses visible ASCII bytes,
with a 32-byte minimum and a 4096-byte maximum. `clock_skew_seconds` is bounded
to 1–300 seconds; `replay_ttl_seconds` must cover that window and is a minimum
post-admission retention interval. The request-derived inclusive retention
horizon is `timestamp + clock_skew_seconds`, so the effective expiry is
`max(admission_time + replay_ttl_seconds, timestamp + clock_skew_seconds)`.
Nonce entry count and nonce length are bounded; replay-related integer settings
reject booleans and coercible non-integer values. Signed mode requires
`constitution.identity_source = "signed_request"`, enabled compiler and
constitution integration, and an enabled observed/constitutional route. It
forbids configured static principal/session/repository fallback. Disabled and
static modes reject signed-only settings and retain their existing defaults.

After the service Bearer check, the adapter reads the bounded raw body and
requires exactly one case-insensitive value for each of these headers:
`X-SLAIF-Identity-Version`, `X-SLAIF-Principal`, `X-SLAIF-Session`,
`X-SLAIF-Repository`, `X-SLAIF-Route`, `X-SLAIF-Timestamp`, `X-SLAIF-Nonce`,
and `X-SLAIF-Signature`. Opaque fields use the bounded ASCII grammar
`[A-Za-z0-9][A-Za-z0-9_-]{0,255}`; timestamp is canonical decimal Unix seconds;
nonce is unpadded base64url/lowercase-hex-compatible ASCII; and the signature
is `v1=` followed by 64 lowercase hexadecimal characters. Identity values,
nonce text, signatures, and secrets are never logged, cached, or returned.

The exact signing bytes are UTF-8 fields joined by `\n`, with no trailing
newline:

```text
slaif-local-coding-identity-v1
METHOD
PATH
sha256(raw_query_bytes)
sha256(exact_bounded_body_bytes)
principal
session
repository
route
timestamp
nonce
```

The path must be one supported proxy path and the raw query bytes are hashed
without parsing or reordering. HMAC-SHA256 is compared in constant time. The
adapter then reserves only a SHA-256 nonce digest in bounded process-local
state; raw nonce and identity values are not retained. Expiry is strict: an
entry remains live when current time equals its effective horizon. Invalid
signatures do not reserve replay state, concurrent duplicates admit one
request, and a full live store returns fixed 503
`signed_identity_replay_capacity_unavailable` without evicting a digest. A
detected wall-clock rollback or non-finite clock returns fixed 503
`signed_identity_clock_unavailable`. Stale/future, malformed, duplicate,
replayed, and route-mismatched requests fail with fixed 403/409/422/503 errors
before image, tool, constitution, compiler, cache, rehydration, or upstream
work. The resulting immutable
principal/session/repository/route identity is passed explicitly through cache,
compiler, selection, injection, and zero-root rehydration keys. Signed/internal
headers are stripped before Qwen. With the default `TTL=skew=60`, a maximally
future-dated request is retained through two skew intervals: its request horizon
is later than admission by `2 * skew`, so TTL equal to skew cannot shorten it.
The digest store is process-local, bounded, digest-only, and single-worker;
restart clears replay history and no cross-process or durable protection is
claimed.

The canonical synthetic conformance fixture is
`tests/fixtures/gateway/signed_identity_v1_vectors.json`. The
[Gateway contract gate](GATEWAY-CONTRACT-CI.md) tests the exact peer in
`tests/fixtures/gateway/current_peer_authority.json`. Configuration and contract
checks do not authorize service changes or protected-host cutover.

## Governance observation

The bounded compiler prompt requires exact case-sensitive literals in normative
binding statements and evidence to survive derived indexing. This matters for
exact-response directives and hidden sentinel rules: a compiler success that
omits such a literal is not an acceptable governance-preserving index.

Supported evidence is deliberately structural: the captured project marker must
occur exactly once in a top-level user/`input_text` Responses item. Three fresh
Codex 0.149.0 captures reported the actual path `$.input[1].content[0].text` and
produced the same request-only fixture normalized to canonical path
`$.input[0].content[0].text`; optional top-level `instructions` corroboration was
absent in all three. When present it
must match the safe label and exact inner bytes or the project root is rejected.
Synthetic
input files require an explicit `input_file` item in a documented top-level content position; and tool
evidence requires a one-to-one `exec_command` call/output pair. Arbitrary recursive
dictionaries, wrong roles/types/names, malformed arguments, and duplicate call IDs
are ignored. Root labels share one bounded POSIX repository-relative validator;
unsafe root labels produce only fixed `invalid_root_path` incomplete telemetry.
The project marker is a complete envelope, not a detectable prefix: the closing
`</INSTRUCTIONS>` may be followed by no newline, one terminal newline, or the
captured bounded `<environment_context>` structural tail. Tail bytes are excluded
from source hashes and candidates. The newline immediately before the closing delimiter belongs to the
envelope and is not observed content; an additional newline is content. No line
ending, trailing whitespace, Unicode, or other content normalization occurs before
UTF-8 length and SHA-256 calculation. Unsupported prefix/suffix, malformed or
duplicate blocks, any malformed supported marker alongside a valid marker, wrong
parent/role/type, and unsafe labels do not detect. An exact
client-supplied supported envelope intentionally crosses the effective-governance
trust boundary; arbitrary mentions and examples do not.

## Forwarding, errors and metrics

The adapter preserves the complete opaque query string upstream
without exposing query values in logs, errors, or metrics. It removes standard
hop-by-hop headers plus every header nominated by `Connection` in each direction,
replaces caller authorization, and forces `Accept-Encoding: identity`. If an
upstream ignores that preference, raw encoded bytes and safe `Content-Encoding`
are forwarded together. Safe bounded response metadata includes `Content-Type`,
`Content-Encoding`, `Cache-Control`, `OpenAI-Processing-Ms`, `Retry-After`, and
request IDs.

Upstream responses with HTTP status 400 or higher retain their status and safe
retry metadata but receive a fixed OpenAI-shaped error body; upstream error
bodies are never relayed to callers.

Before such an error response is closed, the adapter privately classifies its
cause for observability only. The classification reads at most
`upstream_error_diagnostic_max_bytes` (default 16,384; hard ceiling 65,536)
of the body and for at most `upstream_error_diagnostic_timeout_seconds`
(default 1.0; ceiling 5.0) seconds, using streaming iteration that appends
only the remaining permitted slice, so a single oversized chunk can never
retain more than the allowance and the response is closed immediately at the
bound. Status-derived classification is applied without reading the body:
401/403 map to `authentication`, 429 to `rate_limit`, and 5xx to
`upstream_5xx`. Every other status parses only a bounded complete JSON object
in supported provider shapes and inspects only the fixed allowlisted
locations (the top-level `error` object and its `code`, `type`, `param`, and
`message` fields) through fixed matcher tables. Numeric, null, collection,
unexpected, ambiguous, malformed, incomplete, oversized, or binary evidence
never crashes classification and maps to `unknown`. The closed private reason
is one of `authentication`, `rate_limit`, `image_count_limit`,
`context_length_limit`, `malformed_input`, `upstream_5xx`, and `unknown`.
Provider text, codes, and bodies are never returned, logged, persisted, or
used as metric labels; the result feeds only the dedicated private counter
`slaif_upstream_http_errors_total` with the bounded labels endpoint,
configured route, status class, and closed reason. Timeout, cancellation, or
read error still closes the response immediately and returns the same generic
public error; the client-facing status, generic JSON body, selected safe
headers, transport-failure meaning, and successful/streaming behavior are
unchanged.

`/readyz` reports fixed `config`,
`upstream`, `compiler`, and disposable-cache states; cache degradation remains
ready-but-degraded because original request semantics are preserved.

`slaif_response_header_duration_seconds` measures time until a local outcome or
upstream response headers. `slaif_stream_duration_seconds` separately measures
total downstream stream lifetime through completion or disconnect. Request/status
counters include bounded local rejects and upstream results; `slaif_readiness_state`
reports the most recently observed ready (`1`) or not-ready (`0`) result. These
metrics do not claim request-body or query-value observability.

## Image and tool policies

`retain_newest` recursively walks dictionaries and lists in deterministic order,
recognizes list content items whose type is `input_image` or `image_url`, and
removes the oldest items until the configured maximum remains. Zero/one-image
requests retain their original bytes. `reject` returns an API-shaped 422 before
calling upstream. `passthrough` does not rewrite. A recognized image marker in
an ambiguous non-list position fails closed.

Each route also has a disabled-by-default responses_tool_policy
(responses-tool-policy-v1).
passthrough keeps both Responses and Chat tool envelopes unchanged. The
explicitly selected drop_disabled_codex_search policy applies only to
/v1/responses, after image handling and before constitutional observation. It
removes only top-level tool declarations whose exact type is tool_search or
web_search; function, custom, namespace, unknown, continuation, and tool-result
items remain in their original order and shape. If no declarations remain for
an automatic, none, or absent choice, the adapter omits tools deterministically.
An explicit choice of a removed type/name, or a choice that cannot be satisfied
after removal, returns HTTP 422 with fixed code
responses_disabled_tool_choice before observation, compiler, cache, or upstream
work. Malformed, oversized, or non-list top-level tool structures return fixed
HTTP 422 responses_tool_policy_invalid. Chat never applies this policy, and
compiler calls remain direct/bypassed.

## Optional governance pipeline

Integration remains disabled by every default. Enabling it requires all of:
`compiler.enabled = true`; `constitution.enabled = true`; either complete
nonempty static `principal`, `session`, and `repository` configuration with
`identity_source = "static"`, or signed ingress with
`identity_source = "signed_request"`; at least one route with
both `observation_enabled = true` and `constitution_enabled = true`; supported
schema versions; and all existing finite compiler/cache/selector/injection
bounds. Invalid combinations fail settings validation/startup. Static labels
are never read from caller headers, bodies, models, or source content. Signed
request identity is verified before this pipeline and is not a static fallback.

On an enabled route, work runs after image policy in this order: deterministic
observation with request-scoped exact root/dependency bytes, direct nonrecursive
compiler/cache execution, bounded incremental dependency compilation, working-set
selection, idempotent endpoint-specific injection, then deterministic JSON serialization.

Compiler output handling is typed and bounded. Each attempt sends the
configured initial `max_output_tokens` (default 3,000). The chat-completion
response is parsed for the supported envelope before any content validation:
a top-level object with exactly one choice whose `finish_reason` is a string
and whose `message` is an object. An explicit `finish_reason = "length"`
yields the typed `output_truncated` outcome before content JSON/schema
validation, so a length-finished incomplete body is never `invalid_json` and
is never validated or persisted; a normally completed malformed body remains
a distinct completed invalid-output failure, and a missing or unsupported
envelope shape fails closed under the existing invalid-output category
instead of masquerading as truncation. On explicit truncation, the next
attempt uses `min(previous_allowance * 2, max_output_tokens_ceiling)`
(default ceiling 8,000; range 128–16,000; validated to be at least the
initial allowance), so a known-insufficient allowance is never repeated, and
the loop stops with `output_truncated` when the ceiling or the per-compilation
`max_attempts` bound (default 2, maximum 4) is reached; other completed
validation failures retain the existing bounded retry semantics. Compiler
attempts are per direct upstream compiler request, the attempt bound is per
compilation leader, cache hits use zero attempts, and process counters are
cumulative; the dedicated content-free counter
`slaif_constitution_compiler_truncations_total` records explicit
truncations, separate from attempts, validated successes by cache outcome,
schema failures by reason, timeouts, and transport failures. Both the initial
allowance and the ceiling are bound into the compilation fingerprint, the
persistent cache key, and the rehydration identity, and the compiler behavior
version is `compiler-v3`, so old and new compilation policies cannot be
confused. Only a fully validated index is written to the derived cache or the
rehydration map; a truncated, invalid, or locally overflowed output produces
no cache entry, no rehydration entry, and no injection, and the pipeline
degrades to the post-image-policy request with the precise
`compiler_output_truncated` reason.

Multiple/incomplete roots and compiler/cache/selection/essential-overflow
failures preserve the post-image-policy request; a zero-root request attempts
exact-key process-local rehydration and otherwise preserves that request. Injection conflicts or
unsupported shapes return sanitized HTTP 422 before model forwarding. Dependencies are acquired only from exact `input_file` content or a unique string
output paired by call ID with one supported Responses/Chat local-tool read call.
The observer validates exact declared-path equality, roles/types, repository path
grammar, UTF-8, and byte bounds. Duplicate, mismatched, extra, unsafe, oversized,
or invalid evidence is never acquired; root governance remains injected with a
missing-P1 instruction where applicable. After root compilation, at most
`constitution.max_dependency_acquisitions` (default 4, maximum 16) dependencies is
compiled incrementally. Each result must match path/hash/length/candidates and all
compiler/cache validation before selection.

After a successful governed injection, the pipeline also records the validated
root index, acquired dependency indexes, and dependency inclusion metadata in a
process-local rehydration map. The key includes the complete verified request
identity (principal/route/session/repository), model, root path/hash, compiler/
index/prompt versions and bounds, observation policy/version/bounds, selector/
render policy/version, and all working-set/injection bounds. A later zero-root
request on an enabled route uses that exact key to rerun deterministic selection
and endpoint-specific idempotent injection without a compiler call. Different
identities, models, policies, versions, source hashes, or bounds never cross-hit.

Rehydration state is process-local and intentionally lost on restart; it is not
the persistent derived-index cache and is not a cross-process/session database.
It stores no raw prompts/source/images/tool output/request bodies/secrets/cache
keys. `[constitution.rehydration]` enforces TTL, LRU entry-count, per-entry-byte,
and total-byte limits. Expired, invalid, oversized, or missing state is a safe
miss that preserves the post-image-policy request. Multiple/incomplete roots and
disabled/spoofed-header requests retain their existing semantics. This simulates
new-context/compacted request behavior at the adapter boundary; a native Codex
compaction trigger is not claimed by the fixture acceptance evidence.

`[constitution.rehydration].enabled` defaults to `true`. Set it to `false` for a
shared service-Bearer deployment when the unchanged gateway supplies no trusted
per-user identity: observed roots still receive current-request governance, but
the process-local map is never populated or consulted and zero-root requests
preserve the post-image-policy body. Exact content-addressed compiler-cache
reuse, if enabled, remains disposable derived reuse and is not identity/session
memory; it cannot create zero-root disclosure. This safe degradation loses
post-compaction/zero-root governance survival and is not equivalent to the
accepted single-user path or to multi-user identity/isolation.

Safe observation/pipeline/rehydration metrics use fixed endpoint/route/state/
reason/outcome labels and counts/durations/gauges only—never source paths/
content/hashes, prompts/output, images, identity values, cache keys, model-visible
text, or request-derived high-cardinality data. Rehydration states include
populated, hit, stale/expired, isolated miss, injected, skipped, and failure.

Acquisition instructions name unavailable files but do not fetch them. Arbitrary
tool-output ingestion and recursive fetching remain excluded. Gateway emission
of signed identity, gateway quotas/accounting, generic production readiness, and
cutover remain outside this repository's production boundary. Fixture-specific acceptance is recorded in the
[historical ledger](OBJECTIVE-004-LEDGER.md).

## The `dependency-bundles-v1` profile (022-a configuration, 022-b pure-transaction and 022-c application-transaction slices implemented; the v1 runtime active on opted-in routes at its bounded application scope)

The approved dependency-bundle cache rework ([the handoff](CACHE-REWORK.md),
[the implementation plan](CACHE-IMPLEMENTATION-PLAN.md)) is selected by the
explicit `[context_cache]` configuration. Omitting the section, or
`profile = "legacy"`, keeps the existing legacy behavior and defaults.
`profile = "dependency-bundles-v1"` is accepted only with its closed, typed
configuration; unknown, incompatible or ambiguous settings fail closed. The
criterion-level gates for the profile live in
[the stage ledger](CACHE-REWORK-LEDGER.md).

The configuration is validated, and the 022-c application
transaction wires the v1 runtime on opted-in governed routes:
`create_app` builds the runnable v1 runtime (the process-owned
recovery store, the pinned tokenizer, the RAM registry, the direct
tool-free compiler channel, and the live session table) when the
closed v1 configuration is complete and valid, and refuses at
startup with a fixed typed error (before constructing an HTTP
client) only on a missing or unprepared recovery root or an
unresolvable marker key reference. A settings model or a refused
app does not establish v1 readiness, source replacement,
native-format, streaming or recovery qualification beyond the
bounded 022-c fake-upstream application scope; the later 023-024
stages remain unearned. Legacy remains usable through its existing
entry points.

### The `[context_cache]` keys

- `profile`: `"legacy"` (default) or `"dependency-bundles-v1"`.
- `workers`: strictly `1` (the one-worker policy). Any other integer and any
  boolean, float or string value is a configuration error.
- `admission_mode`: `"lean"` (default) or `"greedy"` (must be explicit);
  v1 only.
- `budget`: the explicit effective-context budget (the accepted 021
  `BundleBudgetConfig`): the effective context `C`, the slot/width/aggregate/
  reserve laws, and the explicit vision contract (`vision_enabled` with
  the per-retained-image reserve and retained capacity) where the
  enabled routes' image policy declares it: a capped vision route
  requires it, a capped text-only route refuses it, and a passthrough
  route (no enforced image limit) is neutral and may use the declared
  vision contract or a text contract. One contract cannot serve mixed
  vision and text-only declarations, and retained capacity must cover
  each route's image limit.
- `compiler`: the explicit bounded compiler policy (the accepted 021
  `BundleCompilerConfig`): declared model, revision and compatibility
  identity, bounded input/output/timeout policies, and a protected
  environment credential reference for the direct upstream channel that may
  share the private upstream environment name but never a Gateway
  credential's environment name.
- `ram`: the explicit bounded process/session RAM ownership (the accepted
  019 `RamStateBounds`).
- `recovery`: the explicit protected-recovery opt-in (`enabled` plus an
  absolute normalized `root`); mandatory for the v1 profile. Configuration
  validation never opens, creates, enumerates or probes the recovery store,
  never resolves a request workspace, never reads credentials and never
  calls an upstream. The operator-prepared directory, retention, deletion
  and encryption obligations are the protected source-recovery contract in
  `SECURITY.md`.
- `route_contracts.<route>`: one explicit model contract per governed route,
  binding the route's declared model to the pinned tokenizer/render
  capability (the pinned upstream revision and render policy version; any
  deviation fails closed) and the configured effective `C`. Orphan or
  missing contracts fail closed; compatible routes may explicitly share a
  contract.
- `marker_key_env`: the distinct application-owned private marker key
  material (022-c) as a PROTECTED ENVIRONMENT REFERENCE (the name of the
  environment variable holding the key bytes), never the key itself;
  mandatory for the v1 profile. The value is resolved once at v1 runtime
  construction, stays in process memory (repr-suppressed) and never
  crosses Git, logs, refs, response fields, test captures or operational
  reprs. It is never a gateway / service credential and never a public
  digest; the stable authenticated session binding stays the MAC-bound
  trusted namespace key (stable across recovery).

### Legacy/v1 migration law

- Under the v1 profile, an explicitly supplied legacy cache/TTL/LRU,
  derived-rehydration, compiler or byte-injection/selector policy is a
  configuration error with a fixed message — even when supplied at its
  default value. A materialized default or an empty policy block alone does
  not conflict.
- The common constitution enablement/identity fields and the route
  observation/constitution flags are shared by both profiles; the legacy
  compiler/selector schema rules apply to the legacy profile only.

### Configuration privacy

Configuration error messages are fixed; validation errors never echo the
raw validation input, and the recovery root never appears in model reprs.

### Illustrative settings excerpt (not a complete configuration document)

The keys below are the current `[context_cache]` contract. The excerpt
is illustrative: it requires the normal surrounding configuration
(`server`, `upstream`, at least one `routes` entry, and the enabled
constitution identity for a v1 profile), and the `model_revision`
placeholder is shown for shape only — a real value must be the pinned
40-hex revision or validation fails closed. A complete valid v1
configuration builds the runnable v1 runtime in this build (022-c);
the `marker_key_env` reference must name a resolvable environment
variable holding the application-owned private marker key.

```toml
[context_cache]
profile = "dependency-bundles-v1"
admission_mode = "lean"       # or "greedy"; must be explicit
marker_key_env = "SLAIF_V1_MARKER_KEY"  # protected env reference, 022-c

[context_cache.budget]
context_tokens = 32768
# the explicit vision contract (vision_enabled / per_image_reserve /
# max_retained_images) only under the enabled route's image policy

[context_cache.compiler]
model = "qwen38-27b"
base_url = "http://127.0.0.1:18020/v1"
model_revision = "<40-hex pinned revision>"
compatibility_identity = "slaif-rtx3090-compat-1"
api_key_env = "SLAIF_V1_COMPILER_KEY"

[context_cache.ram]
session_max_owned_bytes = 134217728
process_max_owned_bytes = 536870912

[context_cache.recovery]
enabled = true
root = "/var/lib/slaif/v1-recovery"   # absolute, normalized, operator-prepared

[context_cache.route_contracts.text]
model = "qwen38-27b"
context_tokens = 32768
# tokenizer_upstream / tokenizer_revision / render_policy_version default to
# the pinned capability; any deviation fails closed
```

The complete operational configuration must additionally set the vision
contract and reserves where the route image policy requires them; they are
never inferred from the abbreviated example or from the server's largest
advertised context.

Component status: the inert component stages of this profile have landed:
whole 019 (the 019-a bounded RAM owner and atomic state storage,
the 019-b bounded async single-flight work plane, and the 019-c
whole-019 closure at the inert injected-work layer) is ACCEPTED at its
bounded inert RAM/work scopes (contract
[the RAM-state contract](CACHE-RAM-STATE-CONTRACT.md), [the RAM-work
contract](CACHE-RAM-WORK-CONTRACT.md)); whole 020 (the protected session
recovery component and its ownership/fault corrections at the inert
recovery-component layer) is ACCEPTED at its bounded inert
recovery-component scope (contract
[the recovery contract](CACHE-RECOVERY-CONTRACT.md)); and whole 021 (the
pinned tokenizer, budgets, direct compiler and selection component)
is ACCEPTED at its bounded inert component scope (PR 29 merged to main
at `144af0bd5e34387afcb8e3f9ddf761eabd56e817`, per the 022 order;
contract [the token-compiler contract](CACHE-TOKEN-COMPILER-CONTRACT.md)).
The 022-a slice is the first same-objective 022 stage: this explicit
configuration contract plus the fixed `create_app` v1 startup refusal,
implemented at the INERT configuration layer (PENDING strategic review).
The 022-b pure exact-span source replacement transaction (policy 12 /
rework section 11; `bundle_replace.py` / `bundle_replace_models.py`;
`tests/test_bundle_replace.py`) is implemented at the INERT pure-
transaction layer (PENDING strategic review at its bounded pure-
transaction scope). The 022-c application transaction (the runnable
governed v1 request path on the actual `create_app` entry point: the
closed historical read-root replay gap, the marker pre-check before the transition's raw acquisition
(the cold bootstrap's gate wired by 022-d), the single outgoing transformed body at the byte-
identical fixed point, the per-request FROZEN represented-frontier
trusted issuance binding over the ACTUAL direct main upstream
response (actual nonstream and split-SSE, never compiler traffic,
never rebased), the pre-forward protected generation with the
retained publish bound to the exact snapshot/epoch it actually
published (a faulted publication keeps the prior bound; the newer
undurable record set is refused on replay, never forwarded under the
stale proof), the fixed typed v1 refusal family with no raw fallback,
and the `marker_key_env` protected environment reference;
`tests/test_app.py`, `tests/test_v1_application.py`) is implemented
at the APPLICATION-TRANSACTION layer, active on opted-in v1 routes
(PENDING strategic review at its bounded fake-upstream application
scope). The 022-d application closure (the closed COLD marker/
source-carrier gate before any cold raw acquisition, owner allocation
or checkpoint — the fixed typed 409 with zero new owner, generation,
compile or main forward, ordinary non-source marker-shaped text
staying data, the cross-namespace cold marker refused and the later
legitimate bootstrap succeeding — correcting the 022-c cold path;
the accepted 020 `admit_with_fence` on both cold and steady-state
transitions with the safe prepublication cleanup, the same-process
fail-closed fenced-epoch retry and the fresh-process idempotent same-
generation orphan re-publication — correcting the 022-c cold admit
plus separate checkpoint; the root-currentness 409 with zero main
forward and no bootstrap fallback; the compiled-context injection at
the endpoint-specific stable placement (Responses `instructions`,
Chat first string-content system message else inserted at the front);
the Chat endpoint evidence (endpoint-in-binding law: a responses-
issued read cannot complete on chat, root authority Responses-only,
actual nonstream and split-SSE chat issuance); the source-change law
at the app boundary (issued re-read: EVIDENCE on the superseded
original's retained carrier, LIVE on the new carrier, the stale OLD
transformed body refused 409 with no forward, the genuine same-digest
revert live again without recompile); the compiler/budget failure law
at the app boundary (the typed fence before retention, the terminal
failure re-served same-epoch with no retry, fresh-process recovery in
a new epoch); stream disconnect closing the upstream; the ungoverned
route forwarded byte-identical; and the fixed typed v1 refusal family
at the app boundary with no raw fallback; `tests/test_app.py`,
`tests/test_v1_application.py`) is implemented at the same
APPLICATION-TRANSACTION layer, active on opted-in v1 routes (PENDING
strategic review at its bounded fake-upstream application scope on
both endpoints). Objectives 023-024 remain the mandatory unearned
runtime stages; the planned mechanism above beyond the 022-d scope
stays unearned.

## Running the adapter

There are two supported deployment paths: the Docker
container, the canonical MVP installation path
([DOCKER-INSTALL.md](DOCKER-INSTALL.md)), and the systemd user service in
`packaging/slaif-local-coding.service`, the secondary direct-host path
(superseding `packaging/slaif-local-coding.service.example`, retained for
continuity), run from the repository `.venv` with the deployed configuration
created from `config/adapter.deployment.template.toml`; see the complete
operator contract in [DEPLOYMENT.md](DEPLOYMENT.md). The unit uses a separate mode-0600
`EnvironmentFile`, loopback-only address-family/IP restrictions, private
temporary storage, read-only system/home protection, bounded tasks/memory/file
descriptors, and explicit SIGTERM/timeout/journal behavior. The configuration
binds `127.0.0.1:18031` and forwards to the separately protected upstream; it
does not load model weights or replace that service. Validate the unit with
`systemd-analyze verify` before use and prefer a unique
`systemd-run --user --collect --unit=...` transient unit for testing. Never put
the credential in `Environment=`, `ExecStart`, or this repository.

For a foreground development test, use an explicitly prepared loopback-only
configuration and run `slaif-local-coding --config /path/to/adapter.toml` from
the installed environment. Stop it with Ctrl-C. Do not select an occupied port
or change an existing service to run the test.

Use [INSTALL.md](../INSTALL.md) for Docker operations and
[DEPLOYMENT.md](DEPLOYMENT.md) for the systemd service. The model server remains
separate. Deployment qualification uses disposable environments and fake
upstreams; protected-host cutover follows the
[separate runbook](RELEASE-CUTOVER-RUNBOOK.md).

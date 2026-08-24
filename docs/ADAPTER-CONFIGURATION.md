# Adapter configuration and operations

`config/adapter.example.toml` is the objective-000 contract. Unknown fields,
policies, duplicate route names, duplicate `(model, endpoint)` matches,
non-loopback listeners, invalid bounds, and routes that do not uniquely match a request fail closed at
settings validation/startup. Application code has
no hard-coded upstream address. The example address is host-specific candidate
configuration, not a public endpoint.

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
multi-user isolation. `/healthz`, `/readyz`, and loopback-only `/metrics` remain
operator endpoints; readiness exposes only the fixed `gateway_ingress` state.

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
single configured appliance identity; a trusted signed per-user identity remains
an unimplemented cross-repository capability.

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
bodies are never relayed to callers. `/readyz` reports fixed `config`,
`upstream`, `compiler`, and disposable-cache states; cache degradation remains
ready-but-degraded because original request semantics are preserved.

`slaif_response_header_duration_seconds` measures time until a local outcome or
upstream response headers. `slaif_stream_duration_seconds` separately measures
total downstream stream lifetime through completion or disconnect. Request/status
counters include bounded local rejects and upstream results; `slaif_readiness_state`
reports the most recently observed ready (`1`) or not-ready (`0`) result. These
metrics do not claim request-body or query-value observability.

`retain_newest` recursively walks dictionaries and lists in deterministic order,
recognizes list content items whose type is `input_image` or `image_url`, and
removes the oldest items until the configured maximum remains. Zero/one-image
requests retain their original bytes. `reject` returns an API-shaped 422 before
calling upstream. `passthrough` does not rewrite. A recognized image marker in
an ambiguous non-list position fails closed.

### Objective-003-b through 003-e optional one-root pipeline

Integration remains disabled by every default. Enabling it requires all of:
`compiler.enabled = true`; `constitution.enabled = true`; complete nonempty
`principal`, `session`, and `repository` configuration; at least one route with
both `observation_enabled = true` and `constitution_enabled = true`; supported
schema versions; and all existing finite compiler/cache/selector/injection
bounds. Invalid combinations fail settings validation/startup. The three identity
values are static local-appliance labels for a private single-user MVP. They are
never read from caller headers, bodies, models, or source content, and they are
not signed multi-user production identity.

On an enabled route, work runs after image policy in this order: deterministic
observation with request-scoped exact root/dependency bytes, direct nonrecursive
compiler/cache execution, bounded incremental dependency compilation, working-set
selection, idempotent endpoint-specific injection, then deterministic JSON serialization.
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
process-local rehydration map. The key includes the complete configured static
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
compaction trigger is not claimed or required by the accepted Objective-004
evidence.

Safe observation/pipeline/rehydration metrics use fixed endpoint/route/state/
reason/outcome labels and counts/durations/gauges only—never source paths/
content/hashes, prompts/output, images, identity values, cache keys, model-visible
text, or request-derived high-cardinality data. Rehydration states include
populated, hit, stale/expired, isolated miss, injected, skipped, and failure.

Acquisition instructions name unavailable files but do not fetch them. Arbitrary
tool-output ingestion and recursive fetching remain excluded. Signed production
identity, gateway quotas/accounting, generic production readiness, and cutover
remain outside this repository's production boundary. Repository-only
Objective-004 support and accepted evidence cover governed real-Codex E2E and
fixture-scoped vision acceptance; see the [criterion ledger](OBJECTIVE-004-LEDGER.md)
and [OAP completeness record](../oap/COMPLETENESS.md).

The user-systemd file in `packaging/` is an uninstalled candidate example. It
uses the repository `.venv`, an explicit repository config path, a separate
mode-0600 `EnvironmentFile`, loopback-only address-family/IP restrictions,
private temporary storage, read-only system/home protection, bounded tasks/
memory/file descriptors, and explicit SIGTERM/timeout/journal behavior. The
example config binds `127.0.0.1:18031` and forwards to the separately protected
upstream; it does not load model weights or replace that service. Validate a
rendered candidate with `systemd-analyze verify` before use and prefer a unique
`systemd-run --user --collect --unit=...` transient unit for testing. Never put
the credential in `Environment=`, `ExecStart`, or this repository.

For a simple foreground candidate test, use the README command on
`127.0.0.1:18031` and stop it with Ctrl-C. If an operator separately installs
the example, stop and remove only that candidate unit and its repo-owned state.
No Qwen/vLLM rollback is required because this candidate neither changes nor
replaces the protected service.

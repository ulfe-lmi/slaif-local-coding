# Adapter configuration and operations

`config/adapter.example.toml` is the objective-000 contract. Unknown fields,
policies, duplicate route names, duplicate `(model, endpoint)` matches,
non-loopback listeners, invalid bounds, and routes that do not uniquely match a request fail closed at
settings validation/startup. Application code has
no hard-coded upstream address. The example address is host-specific candidate
configuration, not a public endpoint.

The credential is read from the environment variable named by `api_key_env`.
Caller `Authorization`, internal identity/debug headers, and hop-by-hop headers
are not reused as trusted upstream credentials or metadata. Logs and metrics
contain bounded endpoint, configured route, status, timing, stream, failure,
and image-count labels only; raw bodies and secrets are excluded.

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
tool text, queries, or authorization. Current external identity/session headers are
spoofable and stripped; signed gateway identity remains future work.

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

### Objective-003-b through 003-d optional one-root pipeline

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
Zero/multiple/incomplete roots and compiler/cache/selection/essential-overflow
failures preserve the post-image-policy request. Injection conflicts or
unsupported shapes return sanitized HTTP 422 before model forwarding. Dependencies are acquired only from exact `input_file` content or a unique string
output paired by call ID with one supported Responses/Chat local-tool read call.
The observer validates exact declared-path equality, roles/types, repository path
grammar, UTF-8, and byte bounds. Duplicate, mismatched, extra, unsafe, oversized,
or invalid evidence is never acquired; root governance remains injected with a
missing-P1 instruction where applicable. After root compilation, at most
`constitution.max_dependency_acquisitions` (default 4, maximum 16) dependencies is
compiled incrementally. Each result must match path/hash/length/candidates and all
compiler/cache validation before selection.

Safe observation/pipeline metrics use fixed endpoint/route/state/reason/outcome
labels and counts/durations only—never source paths/content/hashes,
prompts/output, images, identity values, cache keys, models' visible text, or
request-derived high-cardinality data.

Acquisition instructions name unavailable files but do not fetch them. Arbitrary tool-output ingestion, recursive fetching, compaction rehydration,
signed production identity, gateway integration, vision readiness, real Codex E2E
support, and cutover remain excluded.

The example user unit is not installed or enabled automatically. For candidate
testing, prefer the README foreground command on `127.0.0.1:18031`. Stop it with
Ctrl-C. If an operator separately installs the example, stop and remove only
that candidate unit and its repo-owned state. No Qwen/vLLM rollback is required
because this candidate neither changes nor replaces the protected service.

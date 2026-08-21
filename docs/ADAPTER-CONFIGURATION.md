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

The example user unit is not installed or enabled automatically. For candidate
testing, prefer the README foreground command on `127.0.0.1:18031`. Stop it with
Ctrl-C. If an operator separately installs the example, stop and remove only
that candidate unit and its repo-owned state. No Qwen/vLLM rollback is required
because this candidate neither changes nor replaces the protected service.

# Adapter configuration and operations

`config/adapter.example.toml` is the objective-000 contract. Unknown fields,
policies, duplicate route names, non-loopback listeners, invalid bounds, and
routes that do not uniquely match a request fail closed. Application code has
no hard-coded upstream address. The example address is host-specific candidate
configuration, not a public endpoint.

The credential is read from the environment variable named by `api_key_env`.
Caller `Authorization`, internal identity/debug headers, and hop-by-hop headers
are not reused as trusted upstream credentials or metadata. Logs and metrics
contain bounded endpoint, configured route, status, timing, stream, failure,
and image-count labels only; raw bodies and secrets are excluded.

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

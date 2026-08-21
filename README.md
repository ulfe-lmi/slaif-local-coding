# SLAIF Local Coding

SLAIF Local Coding is a self-hosted model-compatibility and context-
virtualization layer for practical SME coding/chat deployments on constrained
local hardware.

It sits invisibly between the SLAIF API Gateway and a local OpenAI-compatible
model server such as Qwen3.8-27B on vLLM. Ordinary Codex/OpenAI-compatible
clients remain unchanged.

Target capabilities, implemented incrementally through OAP:

- preserve only the newest image when a route physically supports one image;
- detect effective `AGENTS.md` governance in model-bound traffic;
- discover and rank referenced constitutional files;
- compile bounded pseudo-context with a separate internal model call;
- cache compiled constitution by content hash and tenant/session identity;
- inject the compact constitution into later requests, including after Codex
  compaction;
- preserve Responses/Chat Completions streaming and ordinary function tools;
- expose safe internal health/readiness/metrics without logging prompts, code,
  images, or raw request/response bodies.

Deployment boundary:

```text
Codex / OpenAI client
        -> SLAIF API Gateway
        -> SLAIF Local Coding adapter
        -> Qwen/vLLM
```

The API Gateway remains a separate repository and owns public access keys,
quotas, accounting, route permissions, and operator administration. This
repository owns the local-model appliance, compatibility transformations,
packaging, and live-model verification.

Read first:

- `ARCHITECTURE.md` — detailed human-facing design;
- `ARCHITECTURE-for-agents.md` — compact normative implementation law;
- `AGENTS.md` — coding-agent constitution;
- `SECURITY.md` and `TESTING.md`;
- `oap/README.md` — versioned transcript contract;
- `docs/OAP-RUNBOOK.md` — exact two-Codex startup/activation/recovery.

The project is developed through Orchestrated Agentic Programming. The coding
agent never merges. The strategic agent independently reviews GitHub state and
merges only when required CI is green and the objective is satisfactory.

Current status: objective `000` provides a private, loopback-only candidate
adapter. It forwards `/health`, `/v1/models`, `/v1/responses`, and
`/v1/chat/completions`; exposes `/healthz`, `/readyz`, and private `/metrics`;
and applies an explicit per-model image policy.

## Candidate quickstart

Python 3.12 and `uv` are required. The example intentionally obtains the
upstream credential only from `QWEN3090_API_KEY`; never write it into TOML.

```bash
uv sync --frozen --extra dev
uv run --frozen slaif-local-coding --config config/adapter.example.toml
curl --fail http://127.0.0.1:18031/healthz
curl --fail http://127.0.0.1:18031/readyz
```

The candidate never retries proxy requests: once a request could have reached
upstream, replay might duplicate model work or tool calls. Upstream connection
failures are sanitized as 502; timeouts/readiness failures as 503. Responses
marked `stream=true` are forwarded incrementally and the upstream response is
closed on completion or downstream disconnect. The request body is consumed in
chunks and rejected as soon as it exceeds `request_body_max_bytes`; an oversized
declared `Content-Length` is rejected before body consumption, while actual bytes
remain the authoritative byte bound. Independently, POST JSON is scanned iteratively
before decoding and rejected with sanitized HTTP 400 code
`json_nesting_too_deep` when container nesting exceeds
`json_max_nesting_depth` (128 by default). The configured depth itself is allowed;
depth 129 is rejected by the example configuration without an upstream call.

Configuration is strict. Each supported model/endpoint must match exactly one
route with `retain_newest`, `reject`, or `passthrough`. The Qwen vision example
retains the newest supported image content item when more than one occurs.
This supports a full-image followed by crop history, but deliberately does not
preserve the semantics of explicit multi-image comparison.

Proxy requests retain the opaque query string without logging or metric-labeling
its values. Standard hop-by-hop headers and headers named by `Connection` are
removed in both directions. Caller compression preferences are replaced with
`Accept-Encoding: identity`; if upstream still sends an encoded response, its raw
bytes and safe `Content-Encoding` are retained consistently. Bounded compatibility
metadata includes `Content-Type`, `Content-Encoding`, `Cache-Control`,
`OpenAI-Processing-Ms`, `Retry-After`, and request IDs.

Run the complete local gate with:

```bash
uv lock --check
uv sync --frozen --extra dev
uv run --frozen ruff check .
uv run --frozen ruff format --check .
uv run --frozen mypy src tests
uv run --frozen pytest -q
uv build
```

Live checks are opt-in and serial. Start the foreground candidate, then run
`SLAIF_LIVE_TEST=1 uv run --frozen pytest -q tests/test_live.py`. They use only
synthetic prompts and bounded outputs. Stop the foreground process to roll back;
the protected vLLM service, model, network, and Codex profiles are untouched.
The systemd file in `packaging/` is an uninstalled example only. Public service
authentication, signed identity, quotas, and TLS remain the separate gateway's
responsibility.

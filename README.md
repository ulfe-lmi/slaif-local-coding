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
- inject a bounded reconstructed constitution on every enabled governance-bearing
  request;
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

Current status: objectives `000`–`004-a` provide a private, loopback-only candidate
adapter. It forwards `/health`, `/v1/models`, `/v1/responses`, and
`/v1/chat/completions`; exposes `/healthz`, `/readyz`, and private `/metrics`;
applies an explicit per-model image policy; can observe evidenced effective
`AGENTS.md` content and enumerate syntactic repository-file candidates; and can
optionally run one bounded compile/cache/acquire/select/inject pipeline after image
policy. The pipeline remains off by default and requires explicit global,
compiler, observation, route, and complete static local-appliance identity
configuration. It handles exactly one complete root and can rehydrate the last validated
working set for an exact configured identity on a later zero-root request;
multiple/incomplete roots preserve post-image-policy semantics.

The currently verified `hinton1` fixture serves text only and declares zero-image
capacity. Image-policy code is covered by fake-upstream tests and objective 000
historical evidence from the prior vision deployment; it is not live-vision
readiness.

## Request-only constitution observation

Observation is independently enabled on each explicit route and runs after image
policy enforcement. The captured Codex 0.149.0 project shape is accepted only as
one uniquely delimited top-level Responses user/`input_text` item. Three fresh
disposable captures placed that item at the actual path `$.input[1].content[0].text`
and normalized it to the canonical fixture path `$.input[0].content[0].text` with
byte-identical request-only fixtures; top-level `instructions` was absent and is
therefore optional corroboration, not a prerequisite.
Synthetic supplements accept explicit `input_file` items in top-level
Responses/Chat content positions and exact bounded reads from `exec_command` or
Codex 0.149.0 `shell_command` calls paired one-to-one
with output by call ID;
the read grammar is limited to exact `cat`, `head`, `tail`, or bounded `sed -n`.
For the captured shape, a matching parseable `instructions` block adds evidence;
a mismatch, duplicate, or any malformed supported marker makes the observation
incomplete with no project root.
The bounded environment tail is discarded before hashing and candidate extraction.
Wrong roles/types/tool names, metadata, arbitrary nesting, tool descriptions,
assistant claims, ambiguous commands, and duplicate/unpaired IDs do not establish
a root. Every evidence class uses one repository-relative POSIX `AGENTS.md` path
validator; unsafe labels yield only a fixed incomplete status. Exact UTF-8 content
bytes are hashed without normalization; raw content and hashes are not logged or
persisted.

Candidate enumeration is mechanical and precedes any future semantic stage. It
recognizes Markdown links/reference definitions, backticks, quotes, and file-like
paths on lines containing normative neighbor terms. It retains duplicate evidence
in stable first-seen order and reports half-open UTF-8 byte spans. Paths become
normalized POSIX repository-relative labels. Absolute/Windows/UNC paths, URLs and
schemes, traversal, controls, percent/query ambiguity, directories, unsupported
basenames, and overlength paths are rejected without filesystem or network access.
An otherwise valid Markdown fragment is stripped while the raw span remains.

A root-declared dependency is acquired only when its exact content also crosses the
request as an `input_file`, or as one string output uniquely paired by call ID with
one supported read call in Responses or Chat. Exact normalized candidate/path
equality, valid roles/types, UTF-8, and byte bounds are required. Duplicate,
mismatched, extra, unsafe, oversized, or invalid evidence produces a fixed rejection
state, never acquisition or filesystem/network access.

Finite configuration bounds cover roots, bytes per source, candidates, evidence
per candidate, total evidence, path bytes, and per-request dependency acquisitions. Overflow produces a typed incomplete
result and safe fixed-reason metrics; the original governance-bearing request is
still forwarded unchanged except for any earlier authorized image transformation.
An exactly constructed supported user envelope is intentionally evidence because
this is a client-supplied effective-governance trust boundary, not plain prose.
The observation result remains request-only. Client identity and session headers
are stripped and are not trusted reuse keys. Observation itself performs no
compiler call, semantic ranking, acquisition, injection, replacement, or
cross-request state change. Unsupported current/future wire shapes fail
conservatively. Fixture provenance and safe refresh guidance
are in `tests/fixtures/codex/0.149.0/README.md`; fixtures describe tested shapes,
not future wire compatibility.

## Compiler, derived cache, and explicit pipeline (objectives 002–003-d)

A library caller—or the explicitly enabled request pipeline—supplies
exact observed source bytes and metadata plus deterministic candidate references.
The compiler makes a bounded text-only request directly to the configured private
vLLM endpoint—never through this adapter's public listener—and accepts only one
strict JSON index schema. The model may rank/classify each supplied candidate but
cannot omit or invent paths. Reference confidence and constitutional priority
remain separate scores.

The filesystem cache stores only validated indexes. Its logical key includes
opaque principal, route, reliable session/repository discriminators, source path
and SHA-256, model, schema/compiler/prompt-policy versions, reasoning effort,
and source/prompt/output/candidate/nesting bounds. Missing session or repository
identity disables persistent reuse rather than guessing an identity. Startup
accepts only real current-user directories and files (directories mode 0700,
files mode 0600), within a finite scan bound; expired/corrupt derived artifacts
are removed, while excessive unknown state makes the disposable cache
unavailable. Integrity checked, TTL/LRU bounded entries are isolated by every
key dimension. P0/P1 entries have a separate cap. Corruption, expiry, permission
errors, unavailable storage, oversized output, invalid schemas, timeouts,
cancellation, or dropped candidates fail closed to a typed miss/failure; no
valid result is cached. The cache is disposable and never persists raw source,
prompts, images, tool output, bodies, credentials, or customer content.

Compilation still never acquires files, rehydrates history, exposes
compiler/cache endpoints, supports signed multi-user production identity, cuts
over traffic, or alters either OAP Codex profile.

## Explicit one-root working-set pipeline (objective 003-b through 003-e)

The selector accepts only already validated indexes. It deterministically orders
P0 root first, acquired P1 by
path/source hash next, then missing-P1 acquisition instructions by urgency/path.
Acquired P2/P3 entries follow when explicit byte/entry budgets permit, ordered by
constitutional priority descending then path/source hash; P4 is omitted. The
selector never reads files, acquires content, calls models, or touches cache
internals.

Rendering measures UTF-8 bytes against a finite cap and omits optional entries
whole in deterministic priority order. It never truncates normative text. Root
and all known/missing P1 material are essential: if they cannot fit, selection
returns a typed failure instead of unsafe partial law. Dependency states retain
reference confidence separately from constitutional priority. Missing-P1 output
names exact repository-relative paths but never pretends unavailable content was
read. Model-visible text marks reconstructed context as overridable by
repository/Git/GitHub/source authority and contains no cache mechanics,
timestamps, keys, credentials, raw prompts/images/tool output.

Endpoint-specific transforms copy Responses and Chat envelopes. Responses uses
top-level `instructions`, preserving existing instructions deterministically;
Chat inserts one stable system message at the earliest position without moving
or changing existing messages. A versioned marker makes same-version/same-content
injection idempotent. Conflicting, duplicate, malformed, shifted, or ambiguous
markers fail closed before upstream use, as do unsupported message/instruction
shapes. The transforms never inspect, decode, re-encode, remove, or rewrite
image items.

After root compilation, at most the configured number of uniquely observed
dependencies (default four, hard maximum 16) is compiled through the same slot,
cache bounds, identity isolation, and strict index validation. An acquired index
must match its declared path/source hash/length and deterministic candidate set;
failures remain missing-P1 acquisition instructions without blocking ordinary
request forwarding.

After a successful governed injection, the pipeline stores only the validated
root/dependency indexes and inclusion metadata in a process-local rehydration
map keyed by complete static identity/model/source/version/policy/bound data.
On a later zero-root request with the same key, it reruns deterministic selection
and endpoint-specific idempotent injection without a compiler call. The map is
TTL/LRU/byte bounded, isolated by every key dimension, intentionally lost on
restart, and stores no raw prompts/source/images/tool output/bodies/secrets.
Expired/corrupt/oversized or missing state safely preserves the original body.
This is adapter-boundary simulated/new-context rehydration, not real Codex
compaction E2E.

When enabled, the public request order is JSON bounds/route selection, image
policy, deterministic observation with exact in-memory root/dependency handoff,
direct non-recursive compiler/cache execution, bounded incremental dependency
compilation, one-root working-set selection or zero-root rehydration, and
endpoint-specific injection before deterministic serialization. Multiple
or incomplete roots preserve the post-image-policy body, as does unavailable/
invalid rehydration state. Compiler, cache,
selection, and essential-overflow failures also preserve that body. Injection
marker/shape failures return a sanitized 422 without forwarding. The pipeline is
local single-user MVP functionality only: configured principal/session/
repository labels are not signed gateway identity and must never be represented
as multi-user production isolation. Gateway integration, forced/equivalent compaction E2E,
vision readiness, security hardening review, systemd candidate proof, and cutover
remain excluded.

## Isolated real-Codex governed E2E

`slaif_local_coding.e2e` provides a repository-owned launcher for a disposable,
bounded evidence run. It creates a private temporary Git fixture and temporary
`CODEX_HOME`, writes a custom Responses provider at `http://127.0.0.1:18031/v1`,
and never touches `~/.codex`, active profiles, auth files, hooks, or either OAP
agent route. The provider references the protected credential only by environment
name. Runs are serialized with process/output/time budgets; raw events remain in
caller-owned temporary files and are deleted after extraction.

The synthetic long root has one referenced dependency. The helper invokes Codex
CLI 0.149.0 with `workspace-write`, approvals never, JSON events, and the stable
built-in command tool (`--disable unified_exec`). It emits only sanitized facts:
exit/status, duration, byte/count bounds, fixed tool item names, sentinel pass/fail,
and selected adapter counters. A successful two-invocation run demonstrates local
tool use, one-root observation plus dependency acquisition/compilation, sentinel
compliance, then persistent index reuse with no additional compiler model attempts.
For this bounded MVP run the prompt supplies the expected final token so the
constrained model has a deterministic output target; sentinel success therefore
evidences end-to-end CLI/final-message behavior, while adapter counters separately
evidence dependency observation, acquisition, compilation, and reuse.

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
route with `retain_newest`, `reject`, or `passthrough`. The designated Qwen Codex
route retains the newest supported image content item when more than one occurs.
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

Live checks are opt-in and serial. Start the foreground candidate for adapter
checks, then run `SLAIF_LIVE_TEST=1 uv run --frozen pytest -q tests/test_live.py`.
The compiler/cache live case calls the configured private upstream directly and
does not require that foreground adapter. Tests use only synthetic prompts and
bounded outputs. Stop the temporary adapter after testing; protected vLLM
service, model, network, and Codex profiles remain untouched.
The systemd file in `packaging/` is an uninstalled example only. Public service
authentication, signed identity, quotas, and TLS remain the separate gateway's
responsibility.

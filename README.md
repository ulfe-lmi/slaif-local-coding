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
- `docs/DEPLOYMENT.md` — the single supported deployment path and operator contract;
- `docs/RELEASE-ARTIFACT-POLICY.md` — supported-artifact policy (wheel) and
  mechanical artifact proof;
- `docs/RELEASE-CUTOVER-RUNBOOK.md` — final live-cutover/rollback runbook
  (prepare-only; the cutover itself is a separate human-authorized act);
- `oap/README.md` — versioned transcript contract;
- `docs/OAP-RUNBOOK.md` — exact two-Codex startup/activation/recovery.

The project is developed through Orchestrated Agentic Programming. The coding
agent never merges. The strategic agent independently reviews GitHub state and
merges only when required CI is green and the objective is satisfactory.

Current status (verified against merged GitHub truth on 2026-09-14):

| Objective | Merged PR | Merge commit | Accepted state |
| --- | --- | --- | --- |
| 000 adapter foundation and image policy | PR #1 | `91463ae3199dd06e0448a9422a5e713da8ee92df` | implemented and merged |
| 001 AGENTS observation, deterministic candidates | PR #2 | `176bf4d839ae9fa32d0cc3c4279a1b96220c1c61` | implemented and merged |
| 002 constitutional compiler and validated cache | PR #3 | `867ed55e7d115d960c666380ebbc5952d43d97d1` | implemented and merged |
| 003 working-set selection, injection, rehydration | PR #4, #5 | `68f212b5ad316b95fa12ef632e1538b56479081b`, `7a2c36a0a40958a6059a765c2f9d5e5bf4ddc161` | implemented and merged |
| 004 real-Codex governed E2E, security/ops hardening | PR #6 | `570bd2b24ad4b041a07e0320d5ed44bc73e99ad5` | implemented and merged; real-E2E accepted (fixture-scoped) |
| 005 gateway integration and cutover contract | PR #7 | `e3f10e93c1ea84bf4021fd15d566bf577d5a9dcf` | implemented and merged; cross-repository acceptance accepted under its documented composed closure |
| 006 signed-request replay hardening | PR #8 | `efc4dbcd377dd796a670726b16ebc06bd54b6356` | implemented and merged |
| 007 current Gateway contract CI | PR #9 | `2041bddc5a745ef0dd4f3088c24b74b9bceefdb9` | implemented and merged; continuously Gateway-contract tested against the pinned peer |
| 008 durable acceptance evidence | PR #10 | `1a913bf3520e7570042774ef7c8ca5153da7a671` | implemented and merged |
| 009 release candidate and operational closure | this PR | (open) | reproducible package (wheel is the single supported distributable) and deployment-qualified in a disposable environment only |

Across the whole product: **cutover NOT performed** (see the prepare-only
[final cutover/rollback runbook](docs/RELEASE-CUTOVER-RUNBOOK.md)) and **NOT
released** (no tag, no registry publication; see the
[release-artifact policy](docs/RELEASE-ARTIFACT-POLICY.md)). The original
planned meanings formerly associated with numeric objectives 006–008 (for
example "SME package") are historical planning prose, not live objective
identifiers; the original product milestone "reproducible SME package and
honest release evidence" is implemented under the Objective-009 milestone name.
The deployment operator contract is in [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md).

The adapter is a private, loopback-only candidate. It forwards
`/health`, `/v1/models`, `/v1/responses`, and
`/v1/chat/completions`; exposes `/healthz`, `/readyz`, and private `/metrics`;
applies an explicit per-model image policy; can observe evidenced effective
`AGENTS.md` content and enumerate syntactic repository-file candidates; and can
optionally run one bounded compile/cache/acquire/select/inject pipeline after image
policy. The pipeline remains off by default and requires explicit global,
compiler, observation, route, and complete static local-appliance identity
configuration. It handles exactly one complete root and can rehydrate the last validated
working set for an exact configured identity on a later zero-root request;
multiple/incomplete roots preserve post-image-policy semantics.
The Objective-004 criterion state is in the [criterion ledger](docs/OBJECTIVE-004-LEDGER.md)
and the [OAP completeness record](oap/COMPLETENESS.md).

The accepted Objective-004 live fixture is the human-selected Qwen vision service:
it supports one image per request and the repository-only run verified Codex
full/full followed by crop/crop behavior. The mutually exclusive text
configuration declares zero-image capacity. This is fixture-scoped evidence, not
a generic or production vision-readiness claim.

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
compiler/cache endpoints, cuts over traffic, or alters either OAP Codex profile.
The adapter-side signed identity v1 verifier remains behind an explicit
configuration mode. The exact pinned Gateway main used by the Objective-005
acceptance harness emits the signed contract for its reviewed Codex route;
production binding, gateway-service deployment, and cutover remain separate
decisions. Signed nonce protection keeps only bounded SHA-256 digests in
process-local memory. Each admitted request is retained through the inclusive
request horizon (`timestamp + clock_skew_seconds`) and at least the configured
`replay_ttl_seconds`; expired entries are reclaimed first, but a full live store
returns a fixed 503 instead of evicting a protected digest. A detected wall-clock
rollback also fails closed with a fixed 503. Restart clears this replay history,
and it is not durable or shared across workers.

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

`[constitution.rehydration].enabled` defaults to `true`. A shared service-Bearer
deployment without trusted per-user identity can set it to `false`; roots still
govern their current request, while zero-root requests preserve their original
body and lose post-compaction rehydration. Content-addressed compiler-cache
reuse remains derived reuse, never identity/session memory. This is a safe
degradation, not multi-user isolation or equivalent single-user readiness.

When enabled, the public request order is JSON bounds/route selection, image
policy, deterministic observation with exact in-memory root/dependency handoff,
direct non-recursive compiler/cache execution, bounded incremental dependency
compilation, one-root working-set selection or zero-root rehydration, and
endpoint-specific injection before deterministic serialization. Multiple
or incomplete roots preserve the post-image-policy body, as does unavailable/
invalid rehydration state. Compiler, cache,
selection, and essential-overflow failures also preserve that body. Injection
marker/shape failures return a sanitized 422 without forwarding. The pipeline
supports either static local-appliance identity or an explicitly verified
adapter-side signed identity v1; static labels are not multi-user production
isolation. The optional adapter-side ingress contracts are documented in [the
gateway integration contract](docs/SLAIF-GATEWAY-INTEGRATION.md). The
Gateway contract CI (objective 007) continuously tests the adapter-side
service-Bearer and signed-ingress contracts against the exact pinned peer in
`tests/fixtures/gateway/current_peer_authority.json`; the historical
Objective-005 acceptance-harness pin remains immutable evidence and is not the
current capability statement. Gateway quotas/accounting, production cutover,
and generic production readiness remain outside this boundary.
Repository-only Objective-004 evidence separately covers governed
Codex E2E, adapter-boundary rehydration, security/observability review, the
isolated systemd candidate, and fixture-scoped vision acceptance; native Codex
compaction is not claimed or required. See the [criterion ledger](docs/OBJECTIVE-004-LEDGER.md)
and [completeness record](oap/COMPLETENESS.md).

## Repository-only real-Codex governed E2E diagnostics

Real-Codex governed E2E support is repository test support under
`tests/helpers/e2e_support.py` and `tests/helpers/sandbox_runtime.py`; it is
not a `slaif_local_coding` runtime module, import, or console API. The
production adapter therefore has no launcher, sandbox/bubblewrap probe,
temporary credential/config writer, or `e2e.py` payload. A wheel inspection
must show no such installed payload. Source-distribution test support, if
included by the build backend, is explicitly non-runtime and is exercised only
from the repository test suite.

The retained support creates a private synthetic Git fixture and disposable
Codex home, writes a custom Responses provider for the loopback candidate
adapter, and references the protected credential only by environment name. The
governed Codex-under-test launcher uses global
`--dangerously-bypass-approvals-and-sandbox` before `exec`, with fixed JSON/
ephemeral/strict-config argv and disabled `unified_exec`; it records the
normalized argv/hash and `codex_under_test_yolo=true`. Bounded time/event/
diagnostic output, closed stdin, process cleanup, private temporary state, and
sanitized event/lifecycle/provenance facts remain in force. Raw prompts, source,
events, responses, command output, credentials, and private paths stay in
caller-owned temporary storage and are not returned, logged, or reported.
Fixture cleanup is verified by focused tests.

The retained gates cover the synthetic long-root/dependency fixture, successful
dependency-read lifecycle, sentinel attribution, bounded cache/metric
reconciliation, and ordinary Codex command-path diagnostics. The 004-s
acceptance sequence makes exactly two governed Codex invocations through the
loopback candidate on `18031`, with the protected upstream on `18020`, and
requires exact dependency bytes, root/dependency observation, compilation,
injection, sentinel compliance, and persistent cache reuse without a third call
or retry. Raw bubblewrap, `unshare`, sandbox controls, alternate prompts, and
host/profile mutation are not used.

The following paragraph is a historical 004-n snapshot, not current branch status.
The historical raw probe is described narrowly as
`raw_bwrap_unshare_all_loopback_bootstrap_failed`: it observed a handcrafted
all-namespace loopback bootstrap failure. The earlier host/kernel inference was
too broad because that probe was not the acceptance topology. Independently
sanitized evidence establishes that the OAP parent was host-direct/unsandboxed,
so the result was not a nested-outer-sandbox artifact. The immutable 004-o
recorded the original startup placement failure. In the corrected 004-p round,
the ordinary B control reached Codex `0.149.0`, exited `0`, and emitted one
successful shell command whose exact text differed from `/usr/bin/true`.
004-q and 004-r remain immutable historical records of workspace-write
qualification limitations; they are not acceptance prerequisites. The current
implementation records only allowlisted config/environment/argv facts; it does
not retain raw diagnostics or mutate the host configuration. At that historical
round, Objective 004 was recorded at 15% and branch readiness at approximately
74%. Current Objective-004 completion and evidence are recorded in the [criterion
ledger](docs/OBJECTIVE-004-LEDGER.md) and [completeness record](oap/COMPLETENESS.md);
the historical external diagnostics do not gate 004-s or 004-al acceptance.

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
Non-streaming upstream response bodies are also bounded by
`response_body_max_bytes`; oversized or error responses are closed and returned
as fixed sanitized errors.

Configuration is strict. Each supported model/endpoint must match exactly one
route with `retain_newest`, `reject`, or `passthrough`. The designated Qwen Codex
route retains the newest supported image content item when more than one occurs.
This supports a full-image followed by crop history, but deliberately does not
preserve the semantics of explicit multi-image comparison.

Proxy requests retain the opaque query string without logging or metric-labeling
its values. Standard hop-by-hop headers and headers named by `Connection` are
removed in both directions, including cookies, forwarding headers, and the
adapter's internal header families. Caller compression preferences are replaced with
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
uv run --frozen python scripts/artifact_policy_check.py --dist dist --inspect
uv run --frozen python scripts/artifact_policy_check.py --dist dist --install-smoke
```

The artifact policy check mechanically proves the wheel's verified-clean
property and the sdist's developer-only whitelist (see
[docs/RELEASE-ARTIFACT-POLICY.md](docs/RELEASE-ARTIFACT-POLICY.md)); the
install smoke proves the wheel installs into a fresh, empty venv with working
console entry point and in-venv provenance.

Live checks are opt-in and serial. Start the foreground candidate for adapter
checks, then run `SLAIF_LIVE_TEST=1 uv run --frozen pytest -q tests/test_live.py`.
The compiler/cache live case calls the configured private upstream directly and
does not require that foreground adapter. Tests use only synthetic prompts and
bounded outputs. Stop the temporary adapter after testing; protected vLLM
service, model, network, and Codex profiles remain untouched.
Deployment: the single supported path is a systemd **user** service on the
local host running the adapter from the repository venv on loopback port
`18031`; see the complete operator contract in
[docs/DEPLOYMENT.md](docs/DEPLOYMENT.md). The unit
(`packaging/slaif-local-coding.service`) keeps loopback-only networking and all
hardening directives, and reads credential values only from a mode-0600
external environment file — never inline in the unit, argv, examples, or
documentation. The deployment mechanics are qualified in a disposable
environment against fake loopback upstreams only
(`scripts/disposable_deployment_qualification.py`); no persistent unit of the
production host is installed or enabled by this repository, and the live
cutover itself remains the separate human-authorized act in
[docs/RELEASE-CUTOVER-RUNBOOK.md](docs/RELEASE-CUTOVER-RUNBOOK.md). Public
client authentication, gateway-side signed identity emission, quotas, and TLS
remain the separate gateway's responsibility. The signed-identity capability is
continuously contract-tested against the pinned Gateway peer (objective 007)
and does not by itself establish production cutover or release readiness.

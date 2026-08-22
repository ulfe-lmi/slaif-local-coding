# SLAIF Local Coding Architecture

**Status:** Initial architecture for OAP implementation  
**Repository:** `ulfe-lmi/slaif-local-coding`  
**Primary reference deployment:** Qwen3.8-27B on vLLM, one RTX 3090 24 GB  
**Public control plane:** separate `ulfe-lmi/slaif-api-gateway` repository

## 1. Executive summary

SLAIF Local Coding is a private model-compatibility and context-virtualization
layer for running useful “mini ChatGPT” and “mini Codex” services on constrained
local hardware.

The immediate reference deployment family is Qwen3.8-27B served by vLLM on a
single RTX 3090. The prior vision deployment provided a long context window,
OpenAI-compatible Responses traffic, ordinary function tools, streaming, and
one-image vision. As verified on 2026-08-22, the current protected `hinton1`
service is language-model-only and accepts zero images. Two limitations remain
material for the intended real Codex use:

1. Codex compacts long conversations. After compaction, a smaller local model can
   temporarily lose project/governance orientation and spend substantial context
   reconstructing it.
2. The prior vision configuration processed at most one image in a request. Codex
   retains prior “Viewed Image” entries in live conversation history and sends
   an old image again when it later sends a crop, causing the upstream model
   server to receive two images.

Both problems are solved at the same architectural point: immediately before the
request reaches vLLM. The adapter transparently transforms the model-bound
conversation according to the selected route's capabilities.

For governance, it recognizes effective `AGENTS.md` content, finds explicitly
referenced files, asks the model in a separate internal call to compile and rank
constitutional material, caches bounded derived indexes, and reinjects the
result into later requests. For an explicitly configured one-image route, it
enforces the physical limit and retains only the newest image for the designated
Codex workflow. Current-host image behavior remains unavailable unless the
protected fixture is separately changed through an explicitly ordered cutover.

The client remains ordinary Codex or another OpenAI-compatible application. The
client does not install or manage pseudo-context software. The SLAIF API Gateway
remains the only public endpoint and continues to own access keys, quotas,
accounting, and route permissions.

```text
Ordinary Codex/OpenAI client
            |
            | OpenAI-compatible HTTPS + sk-slaif key
            v
SLAIF API Gateway                    [separate repository]
            |
            | authenticated internal request + opaque identity
            v
SLAIF Local Coding Adapter           [this repository]
  - route capability policy
  - image-window adaptation
  - constitutional compiler/cache
  - bounded context injection
  - safe metrics/diagnostics
            |
            | private OpenAI-compatible request
            v
Qwen/vLLM on local GPU
```

The adapter is not a second public gateway. It is a private semantic/model
frontend packaged with the local inference appliance.

## 2. Product proposition

An SME should be able to deploy a private coding/chat service with:

- familiar OpenAI-compatible client configuration;
- gateway-issued user keys rather than upstream model keys;
- local model inference on affordable hardware;
- ordinary Codex file/shell/Git tools executed on the developer workstation;
- long repository governance that remains operational after context compaction;
- working image inspection when an explicitly configured route has a one-image
  physical model limit;
- explicit quotas/accounting through SLAIF API Gateway;
- no silent dependency on a hosted AI control plane;
- reproducible installation, verification, observability, and rollback.

The product does not claim that a 27B local model is equivalent to a frontier
hosted model. It makes the local model substantially more usable and predictable
by compensating for known interface and memory constraints outside the model.

## 3. Scope

### 3.1 In scope

- private OpenAI-compatible adapter in front of vLLM;
- faithful pass-through for `/v1/responses` and `/v1/chat/completions`;
- SSE streaming, ordinary function tools, errors, timeouts, and cancellation;
- model/route-specific request transformation policies;
- newest-image-only enforcement for a route that supports one image;
- detection of effective `AGENTS.md` material in provider-bound traffic;
- deterministic extraction of candidate repository references;
- separate internal model call to compile constitutional rules and rank files;
- bounded disposable cache with content-hash invalidation;
- reinjection of a stable compiled constitution into later requests;
- incremental acquisition/indexing when referenced file content appears in tool
  outputs;
- tenant/session isolation suitable for gateway integration;
- internal health/readiness/metrics and sanitized operational logs;
- systemd and later OCI/Compose packaging;
- live tests against the already-running local vLLM service;
- component/release provenance and upstream attribution.

### 3.2 Explicit non-goals

- replacing SLAIF API Gateway authentication, quota, accounting, admin, or route
  management;
- modifying Codex or requiring a Codex plugin, MCP server, hook, or local proxy;
- direct access from the GPU service to customer repository files;
- uploading or cloning customer repositories into the GPU service by default;
- treating cached summaries as authoritative project truth;
- hiding intentional multi-image comparison semantics without a route policy;
- provider-native hosted tools, web search, computer use, or code interpreter;
- general semantic memory for all conversation content in the first release;
- distributed cache or hostile multi-tenant SaaS claims in the MVP;
- modifying vLLM/model weights/quantization/launch flags as part of ordinary
  adapter development;
- bundling model weights;
- production/compliance/certification claims based only on a successful demo.

## 4. Architectural principles

### 4.1 Client transparency

The ordinary client sends an ordinary OpenAI-compatible request. No client-side
sidecar is required. The only visible endpoint is SLAIF API Gateway in the
packaged deployment.

### 4.2 Semantic preservation before optimization

A transform must preserve the intended request semantics within the declared
route contract. Constitutional optimization must not silently remove governance
when compilation fails. Unsupported image multiplicity is handled according to
an explicit route policy, not an accidental global rewrite.

### 4.3 Git/repository remains authoritative

A compiled constitution is disposable derived state. It helps the model retain
orientation; it never overrides the original `AGENTS.md`, delegated documents,
repository, Git history, pull request, CI, or human/strategic decisions.

### 4.4 Software manages mechanics; the model supplies semantic compression

Deterministic software owns detection, candidate enumeration, hashing, cache
identity, bounds, TTL/LRU, invalidation, request injection, and image limits. A
separate model call supplies semantic classification and compression because
middleware alone cannot reliably decide which instruction or exception is
important.

### 4.5 Model-specific behavior is route policy

The adapter is extensible beyond Qwen. Every capability and transformation is
selected from explicit route/model policy. A future model that supports eight
images must not inherit a one-image rewrite.

### 4.6 Private, bounded, observable

The adapter sees highly sensitive data. Raw content is not logged. Caches are
bounded and isolated. Operators receive metrics and safe metadata sufficient to
diagnose behavior without storing customer prompts, code, or images.

### 4.7 Development must not destroy its own control path

No pre-existing image-cap proxy is assumed on the reference host. Both OAP
agents normally use the default Codex provider. The strategic agent independently
discovers the live Qwen/vLLM service under test. New adapter code runs on
development port 18031 so implementation and live tests cannot disturb the
protected model service.

## 5. Deployment topologies

### 5.1 Reference development topology

All development occurs on the machine that currently hosts Qwen/vLLM.

```text
/synology/homes/janezp/
├── qwen-serving/                         protected live runtime
├── codex-work/slaif-local-coding/        coding-agent repository
└── codex-supervision/slaif-local-coding/ strategic-agent workspace

OAP control plane:
  Strategic Codex -> default Codex provider
  Coding Codex    -> default Codex provider

Protected live system under test:
  Qwen/vLLM text-only service
    -> discover live; currently hinton1 127.0.0.1:18020

New adapter development path:
  tests/curl
    -> 127.0.0.1:18031 development adapter
    -> live Qwen/vLLM service

Internal compiler path:
  development adapter
    -> 127.0.0.1:18020 directly
```

After the host migration, the same-host loopback is the preferred operational
path on `hinton1`. The optional LAN endpoint is `http://10.8.132.75:18020/v1`;
`http://10.8.132.76:18020/v1` is historical provenance, not a current default.

This topology enables real live-model tests while keeping both OAP Codex agents
independent of the constrained local model under test. Objective 000 must verify
the actual current service/process/model facts; historical paths and ports are
not accepted without inspection.

### 5.2 SME packaged topology

A small deployment may colocate all server components on one host or private
network:

```text
Internet/VPN
    |
    v
NGINX/TLS -> SLAIF API Gateway -> Local Coding Adapter -> vLLM/GPU
                 |                       |
              PostgreSQL             cache/metrics
```

Only the gateway is public. The adapter binds loopback or a private service
interface. vLLM accepts traffic only from the adapter/controlled operations.

### 5.3 Separate gateway host

When the gateway is on another host, the adapter may bind a private VPN/service
address. Firewall rules allow only the gateway and controlled operator sources.
The internal request is authenticated and signed. This remains “invisible” to
external clients: there is still one public endpoint and one gateway key.

## 6. Actors and trust boundaries

### 6.1 External user/client

Uses an ordinary OpenAI-compatible SDK or Codex profile. It may send prompts,
tool definitions/results, source fragments, images, and repository governance.
It is not trusted to set internal principal/route headers.

### 6.2 SLAIF API Gateway

Trusted public control plane. It authenticates external keys, resolves allowed
route/model, reserves/finalizes quota, and sends opaque signed identity to the
adapter. It does not understand constitutional semantics or Qwen image-history
quirks.

### 6.3 SLAIF Local Coding Adapter

High-trust private component. It receives the complete model-bound request,
selects route policy, performs transformations, schedules compiler calls, and
streams the upstream response. It must not expose raw content through logs,
metrics, cache names, exceptions, or debug headers.

### 6.4 vLLM/Qwen

Private inference provider. It receives only the transformed request. It does
not know or manage cache mechanics. Internal compiler calls use the same model
but a separate, non-recursive direct channel.

### 6.5 Codex tools and repository

Codex executes file/shell/Git tools on its client workstation. The adapter does
not directly mount or read that filesystem. Referenced constitutional documents
become available only when their content crosses the API boundary in project
instructions, input items, or tool outputs.

### 6.6 Operator

Configures routes, service credentials, cache bounds, and deployments; can view
safe metrics and purge derived cache. Operators should not need to inspect raw
customer payloads for routine diagnosis.

## 7. Component model

### 7.1 ASGI API frontend

Recommended implementation: Python 3.12, FastAPI/Starlette, Uvicorn, HTTPX
async streaming, Pydantic settings/models. The adapter owns:

- `/healthz` — process liveness;
- `/readyz` — configuration/cache/upstream readiness with no secret disclosure;
- `/metrics` — private Prometheus metrics;
- transparent forwarding of `/health`, `/v1/models`, `/v1/responses`,
  `/v1/chat/completions`, and conservatively other configured paths.

The ASGI frontend must stream upstream bytes/events without assembling the full
response. It handles downstream disconnect and cancels/closes upstream work.

### 7.2 Request context builder

Builds immutable metadata for one request:

```text
request ID
endpoint and method
resolved route/model policy
authenticated opaque principal
session/thread discriminator when available
request/body hash
content type and streaming mode
compiler-bypass flag for internal calls
```

Untrusted external headers cannot set compiler bypass or internal identity.

### 7.3 Transformation pipeline

The model-bound JSON pipeline is ordered:

1. parse and validate bounded JSON for transformable endpoints;
2. normalize only enough to locate supported content items;
3. apply route image policy;
4. observe constitutional roots/dependency content and update derived state;
5. obtain/validate cached compiled constitution, synchronously compiling on
   allowed cache miss;
6. inject bounded constitution in the route/API-specific stable location;
7. serialize and forward;
8. stream response unchanged except hop-by-hop transport handling;
9. emit safe metrics.

Transforms return structured internal evidence so tests can assert exact action
without logging payloads.

### 7.4 Route policy registry

A route policy declares physical/semantic capabilities:

```text
route name and model selector
allowed endpoint(s)
max images per request
image overflow policy: retain_newest | reject | passthrough
constitution enabled/disabled
maximum injected bytes
compiler/cache policy
request-body and timeout limits
```

Policy is configuration, validated at startup. Unknown or contradictory policy
fails readiness.

### 7.5 Image-window adapter

The first algorithm is based on the proven compatibility prototype:
recursively collect list elements whose object type is `input_image` or
`image_url`, then remove all but the newest.

The production module must improve the prototype by:

- using a pure deterministic function with exhaustive tests;
- preserving non-image content and relative order;
- supporting Responses and Chat content structures;
- returning counts/locations as internal metadata;
- applying only on a selected route;
- rejecting unsafe/unknown over-limit shapes rather than forwarding a known
  invalid request;
- avoiding an externally visible debug header by default;
- streaming the response through the shared adapter rather than a second proxy.

For the designated Codex workflow, “newest” matches user intent: Codex first
sends a full image and later sends a crop while retaining the prior image in
history. The crop is the current observation. The route documentation must state
that explicit two-image comparison is unsupported on this physical model; a
route intended for comparison should use `reject`, not silent pruning.

### 7.6 Constitution detector

Detection is evidence-based and supports multiple forms:

- Codex-generated project-instruction blocks that identify `AGENTS.md` or an
  effective instruction directory;
- uploaded/input-file items with filename `AGENTS.md`;
- tool results clearly paired with a command/path reading `AGENTS.md`;
- captured version-specific Codex envelopes;
- conservative pattern fallback with confidence and provenance.

It must not classify arbitrary prose mentioning “agents.md” as a root without
sufficient envelope/path evidence. Every detected root records source content
hash and evidence type.

Codex may truncate or combine project instructions before sending them. The
adapter can compile only bytes it receives. If a root identifies missing
constitutional dependencies or likely incomplete content, the injected state
instructs the coding model to acquire the complete files through ordinary local
repository tools before substantive work.

### 7.7 Deterministic reference extractor

Before any model ranking, software enumerates candidate references from the root:

- Markdown links and reference definitions;
- backtick/quoted path-like strings;
- normalized relative paths with known text/config extensions;
- filename references near normative language;
- exact duplicates collapsed while retaining all evidence spans.

It rejects absolute host paths, URLs, traversal outside repository context, and
obvious examples when policy says they are not retrievable repository files.
Candidates are never silently discarded by the model. The compiler may classify
them as low priority/background, but the deterministic manifest preserves that
they were seen.

### 7.8 Constitutional compiler

On a source/compiler cache miss, the adapter sends a separate internal request
directly to vLLM. The compiler receives:

- source type/path label;
- source text within a hard input bound;
- deterministic candidate list and evidence snippets;
- strict task instructions treating content as data;
- strict output schema and output-token limit.

It returns:

```text
source hash and schema/compiler version
bounded constitutional summary
normative rules with strength and evidence
role/authority/source-of-truth boundaries
important exceptions and ordering constraints
candidate dependencies with:
  path
  reference confidence
  constitutional priority
  relationship/class
  evidence
  acquisition urgency
conditions requiring full-source reread
```

Two scores are mandatory:

- `reference_confidence`: likelihood that the text identifies a real repository
  file;
- `constitutional_priority`: authority/importance if it is a file.

A single “constitutionness” score is forbidden because a definitely referenced
example can have low authority, while an ambiguously formatted security policy
can have high potential authority.

Suggested classes:

```text
P0 root constitution
P1 delegated binding constitution/security/protocol
P2 binding procedure/testing/release/operations
P3 architecture/contracts relevant on demand
P4 background/examples
```

The compiler has no tools, network, filesystem, external gateway key, or ability
to mutate cache directly. Its call uses a dedicated HTTPX client to upstream,
not the public adapter URL, preventing recursive transformation.

### 7.9 Compiler scheduler

The reference GPU is memory-constrained. Compiler work is bounded:

- default one concurrent compiler call;
- source-hash deduplication so simultaneous identical misses share one result;
- no compiler call for every normal turn;
- compiler disabled or deferred when upstream health/capacity policy requires;
- short reasoning/output budget;
- text-only compiler input even when the user request contains images;
- explicit timeout and safe fallback.

Initial compilation is synchronous because the first model request needs useful
orientation. Later low-priority dependency compilation may be incremental.

### 7.10 Pseudo-context cache

The cache is semantic virtual memory, not authoritative storage.

Conceptual hierarchy:

```text
L0: tiny injected constitutional manifest, always present
L1: compiled source indexes, selected by priority/task/session
L2: original source text received in request/tool output
L3: repository/Git/GitHub, authoritative and client-side
```

Initial backend:

- bounded filesystem cache under `/dev/shm/slaif-local-coding`;
- permission `0700` directory and `0600` files;
- fallback to protected XDG cache when tmpfs unavailable;
- atomic writes/renames;
- content-addressed entries;
- total and per-entry byte limits;
- TTL plus LRU for unpinned entries;
- P0/P1 entries pinned within a separate bounded budget;
- cache schema/compiler/model/policy version in identity;
- safe purge and complete reconstruction.

No customer raw source text needs long-term cache persistence after compilation.
If retained temporarily for deduplication/debugging, it uses a separate short TTL
and is disabled by default. Derived indexes remain sensitive and are tenant-
isolated.

### 7.11 Session/repository identity

A compiled root must be associated with the correct future requests. Preferred
identity from the gateway:

```text
opaque principal UUID
opaque session/thread ID
resolved route ID
```

Additional discriminators may include Codex `prompt_cache_key`,
`previous_response_id`, conversation identifier, or a root constitution hash.

MVP single-user fallback may use:

```text
principal + route + best available session key + root hash
```

The fallback must never share indexes across different principals. When no
reliable session identity exists, the adapter can inject only content-addressed
root indexes explicitly observed in the current request or require the client to
re-present the root. Production multi-user release requires the signed gateway
identity contract.

### 7.12 Constitution working-set selector

The selector builds a deterministic bounded injection:

1. root P0 index;
2. acquired P1 binding indexes;
3. missing P1 dependencies and acquisition instruction;
4. P2 items relevant to current request keywords/tool paths when space permits;
5. never exceed configured bytes;
6. stable ordering for prefix-cache reuse;
7. include source hash/version and “authoritative source overrides this index”;
8. omit cache mechanics, LRU timestamps, or internal secrets from model-visible
   text.

The model need not know how the cache works. It sees a concise reconstructed
project context marker and the actual rules it needs.

### 7.13 Injection adapter

Responses and Chat Completions have different envelopes. Injection logic is
versioned and contract-tested against captured Codex requests.

Preferred behavior:

- preserve the client's system/developer ordering requirements;
- add one stable private developer/system instruction block in the earliest
  API-valid location;
- do not duplicate the compiled block if already present;
- replace a large observed `AGENTS.md` block only after the compiled output is
  valid and semantic fallback is available;
- otherwise supplement rather than delete original governance;
- preserve tool definitions, `previous_response_id`, metadata, reasoning, and
  streaming fields unless route policy explicitly changes them.

### 7.14 Objective-003-a foundation boundary

The current slice implements the selector and endpoint-scoped transform contracts
as pure libraries. It does not wire either into public handlers, acquire missing
files, recover compacted history, expose admin/cache endpoints, introduce signed
multi-user identity, or change traffic cutover. Its tested ordering is root P0;
acquired P1 by path/source hash; missing-P1 acquisition by urgency/path; then
acquired P2/P3 by independent constitutional priority descending, path, and
source hash while finite UTF-8/entry budgets permit. P4 is omitted. Optional
entries are omitted whole; essential overflow fails typed rather than truncating
law. Injection is idempotent only for identical version/content at the stable
Responses `instructions` field or earliest Chat system location, and any other
marker collision fails closed.

A marker/version enables idempotence and debugging without exposing cache IDs.

### 7.14 Observability

Private metrics should include:

```text
requests by endpoint/route/status/streaming
upstream latency and time to first byte
active upstream/compiler requests
images observed/forwarded/removed/rejected
constitution roots detected by evidence type
compiler cache hits/misses/failures/timeouts/latency/tokens
references discovered by class/priority (counts only)
injected bytes and entries
cache bytes/entries/evictions/expirations
fallback and fail-closed events
```

Logs contain request ID, route, status, counts, durations, hashes truncated or
HMACed where needed, and error class. They do not contain raw bodies, prompts,
source, filenames from private repos unless explicitly safe, images, tool output,
or credentials.

## 8. Request flows

### 8.1 Ordinary text request, cache hit

```text
1. Gateway authenticates and resolves local-Qwen route.
2. Adapter validates internal identity and route.
3. Request contains no images; image transform is a no-op.
4. Session/root maps to a valid compiled working set.
5. Adapter injects stable bounded constitution.
6. Adapter forwards to vLLM.
7. vLLM response/SSE streams through unchanged.
8. Safe metrics record hit, injected bytes, upstream usage/latency.
```

### 8.2 First `AGENTS.md` encounter

```text
1. Detector finds an effective AGENTS.md block and hashes it.
2. Deterministic extractor enumerates all candidate referenced files.
3. Cache miss starts one direct internal compiler call.
4. Compiler returns strict validated rules/dependency ranking.
5. Adapter stores derived index atomically.
6. It injects root rules plus missing high-priority dependencies.
7. Main coding request proceeds to vLLM.
```

If compilation fails, the original governance-bearing request is preserved and
forwarded when upstream limits permit. The optimization may fail; governance
must not disappear.

### 8.3 Referenced file acquisition

```text
AGENTS.md says SECURITY.md is binding.
Compiler marks SECURITY.md P1 required, content missing.
Injected state tells model to read it before substantive mutation.
Qwen emits ordinary shell/file tool call.
Codex reads SECURITY.md locally and returns tool output.
Adapter observes path/content pairing, hashes, compiles, and stores P1 index.
Future requests receive both root and security index.
```

The adapter does not execute the file read itself.

### 8.4 Post-compaction request

Codex may replace detailed conversation history with a compacted summary. The
adapter injects the stable constitutional working set into every model request,
so the next Qwen call receives the critical rules independently of what the
client summary retained.

If Codex computes compaction from its own local estimate, the adapter may not
reduce how often the UI compacts. It still removes the post-compaction blindness.
If Codex uses provider-reported usage, reduced upstream input may additionally
delay compaction. This is an empirical acceptance-test question, not an assumed
claim.

### 8.5 Full image followed by crop

```text
Turn N request contains full image A.
Turn N+1 history contains old A plus new crop B.
Route says max_images=1, retain_newest.
Adapter removes A and forwards B with all text/tool context preserved.
vLLM never receives two images and avoids the hard one-image error.
```

### 8.6 Explicit multi-image comparison

If the selected route cannot support it and policy is `reject`, the adapter
returns a documented error explaining the route limit. The system must not claim
that newest-image-only preserves a true comparison request.

### 8.7 Streaming tool call

The adapter transforms only the request. It then relays SSE event bytes/order,
including reasoning/text/function-call deltas and completed usage. It must not
parse/reconstruct the stream unless a later explicit compatibility policy
requires it. Disconnect closes upstream promptly.

## 9. Data contracts

The implementation should define typed internal models equivalent to the
following.

### 9.1 `RoutePolicy`

```text
name
model selectors
endpoint selectors
max_images_per_request
image_overflow_policy
constitution_enabled
max_injected_bytes
compiler policy
cache policy
timeouts/body limits
```

### 9.2 `ConstitutionSource`

```text
source kind: AGENTS_ROOT | DELEGATED_FILE | OTHER
logical path/label
content hash
observed content length
observation evidence and confidence
principal/session/route context
created/last-seen timestamps
```

### 9.3 `CandidateReference`

```text
normalized relative path
all deterministic evidence spans/types
reference confidence
constitutional priority
relationship/class
acquisition urgency
compiler evidence/reason
state: missing | observed | compiled | stale | invalid
```

### 9.4 `ConstitutionIndex`

```text
schema/compiler/model/policy versions
source identity/hash
purpose
normative rules with strength/evidence
role and source-of-truth boundaries
important exceptions/order constraints
dependencies
full-source reread triggers
bounded rendered form
```

### 9.5 `TransformationResult`

```text
transformed body
images seen/forwarded/removed
constitution detection/cache/compile status
injected bytes/entry counts
fallback/rejection reason
safe metric labels
```

## 10. Cache correctness and invalidation

A source index is valid only when all identity inputs match:

```text
principal isolation key
source content hash
compiler prompt/schema version
compiler model/revision identifier
route/policy version
render format version
```

A changed source hash creates a new entry. The old entry is never silently
attached to the new root. Source mtime is not authoritative because the adapter
normally does not see the client filesystem.

Staleness states:

- `VALID`: all identities match;
- `MISSING`: dependency named, content not yet observed;
- `STALE`: source observed with a different hash;
- `INVALID`: compiler/schema validation failed;
- `EXPIRED`: TTL elapsed;
- `EVICTED`: derived entry removed for budget.

A missing or evicted index is a cache miss, not data loss.

## 11. Image adaptation correctness

The pruning algorithm must define “newest” by traversal order of actual content
items as serialized in the request, with tests for supported envelopes. It must
not use dictionary key order as semantic chronology across unrelated fields
without an endpoint-specific rule.

For Responses, chronology normally follows the ordered input/item arrays. For
Chat Completions, chronology follows messages and each message's ordered content.
The implementation should use explicit endpoint walkers rather than an
unbounded generic recursive delete for production, while retaining a generic
fallback only when proven safe.

Before forwarding, the adapter verifies the resulting image count does not
exceed policy. It does not decode/re-encode image payloads in the MVP; it only
retains/removes complete content items, minimizing CPU/RAM and fidelity risk.

## 12. Resource management on a 24 GB GPU host

The model consumes nearly all GPU memory. The adapter is CPU/network middleware
and must not import torch, load the model, decode images, or reserve GPU memory.

Constraints:

- one compiler call at a time by default;
- bounded request bodies and source/compiler outputs;
- streaming instead of response buffering;
- no copying large image/base64 bodies more than necessary;
- incremental/streaming JSON optimization may be considered after correctness;
- cache tens of megabytes, not gigabytes;
- low-concurrency live tests;
- avoid launching duplicate vLLM servers;
- do not modify the running model service during ordinary tests;
- timeout/backpressure when upstream saturated.

The adapter must remain usable when `/dev/shm` is small or unavailable; the
protected filesystem fallback is required.

## 13. API compatibility

### 13.1 Responses API

The reference Codex path uses `/v1/responses`. The adapter must preserve at least:

- `model`, `input`, `instructions`, `tools`, `tool_choice`;
- function call and `function_call_output` continuation;
- reasoning settings supported by upstream;
- `stream`, SSE typed events, final usage;
- metadata/identifiers needed for session correlation;
- upstream errors and status codes.

The adapter does not claim full OpenAI Responses parity beyond what the selected
vLLM/gateway route supports.

### 13.2 Chat Completions

Support is included because chat clients may use the same appliance and the
existing image prototype covers both endpoint shapes. Transformations remain
route-capability gated.

### 13.3 Other paths

Unknown/configured passthrough paths should be forwarded without JSON
transformation where safe. Internal health/metrics paths are adapter-owned and
must not collide with upstream semantics.

## 14. Failure semantics

### 14.1 Upstream unavailable

Return a sanitized 502/503 according to failure type. Do not expose upstream key,
private address beyond configured operator policy, stack trace, or raw body.
Readiness fails.

### 14.2 Malformed JSON on transformable endpoint

Return an explicit client error; do not silently bypass image limits or attempt
constitutional rewriting on unknown bytes.

### 14.3 Compiler timeout/error/schema failure

Record safe failure metadata. Preserve/forward original governance-bearing
request when within safe limits. Do not cache invalid output as valid. Apply
bounded retry policy only; no recursive or unbounded calls.

### 14.4 Cache unavailable

Operate without optimization using original request semantics. Readiness may be
degraded but not necessarily failed if cache is optional. Image enforcement
continues because it does not depend on cache.

### 14.5 Image over limit

- `retain_newest`: transform, verify count, forward;
- `reject`: return deterministic documented error;
- `passthrough`: allowed only when upstream capability supports the observed
  count; otherwise configuration error/fail closed.

### 14.6 Missing session identity

Never reuse another principal's cache. Use current-request observed content and
content-addressed entries only, or run without cross-turn rehydration. Multi-user
production readiness requires reliable internal identity.

### 14.7 Downstream disconnect

Cancel/close upstream response stream and release concurrency slots. Do not let
orphan compiler/main requests consume the constrained GPU indefinitely.

## 15. Security and privacy architecture

### 15.1 Data minimization

No raw payload logging. Metrics are aggregate counts/timings. Cache stores the
minimum derived text needed for rehydration. Raw source retention is off by
default.

### 15.2 Internal authentication

Production gateway-to-adapter traffic uses a service credential plus signed
opaque principal/session/route metadata. The adapter strips any external attempt
to inject these headers.

### 15.3 Compiler prompt injection boundary

Repository governance may contain adversarial text. The compiler prompt:

- labels the content as data;
- grants no tools;
- asks only for classification/extraction;
- requires strict schema;
- limits output and candidates;
- validates paths/strings after generation;
- never executes or fetches a referenced path.

The main coding model may still be instructed by the repository's genuine
`AGENTS.md`; that is expected. The compiler itself must not perform side effects.

### 15.4 Cache confidentiality

Per-principal namespaces, restricted permissions, unguessable/HMACed identifiers
where exposed to filesystem names, TTL, purge, and no public cache endpoint.

### 15.5 Host protection during development

The current model installation is a protected fixture, not a disposable VM.
Passwordless sudo may be used for safe repository-local dependencies and test
services but not for unrequested changes to qwen-serving, systemd units,
network/firewall/VPN, model files, API keys, or the live Codex endpoint.

## 16. Observability and operator experience

Operator commands should eventually provide:

```text
slaif-local-coding doctor
slaif-local-coding cache status
slaif-local-coding cache purge --principal/--all
slaif-local-coding config check
slaif-local-coding live-test --profile qwen38-vision
```

The first implementation may expose equivalent Python/HTTP commands before a
stable CLI. Diagnostics must show counts, hashes/versions, and failure classes,
not raw governance or prompts.

Example safe event:

```json
{
  "event": "request_transformed",
  "request_id": "...",
  "route": "qwen38-vision-codex",
  "images_seen": 2,
  "images_forwarded": 1,
  "constitution": "cache_hit",
  "injected_bytes": 9120,
  "status": 200,
  "upstream_ms": 1840
}
```

## 17. Packaging and configuration

### 17.1 Python package

Expected structure after implementation:

```text
src/slaif_local_coding/
├── app.py
├── config.py
├── proxy.py
├── routing.py
├── transforms/
│   ├── images.py
│   └── constitution.py
├── constitution/
│   ├── detect.py
│   ├── references.py
│   ├── compiler.py
│   ├── schema.py
│   ├── cache.py
│   ├── select.py
│   └── inject.py
├── security.py
├── telemetry.py
└── cli.py
```

Tests mirror these boundaries and include fake/live/end-to-end layers.

### 17.2 Configuration

Configuration is validated TOML/environment. Secrets come only from protected
environment/service credential files, never committed TOML. Route policy is
explicit and versioned.

### 17.3 systemd

Development service binds `127.0.0.1:18031`. Unit uses a separate repository
venv, protected environment file, restart/backoff, and logs safe metadata only.
It does not replace or reconfigure the existing Qwen/vLLM service or active Codex profile in objective 000.

### 17.4 OCI/Compose

Later packaging can colocate gateway, adapter, and vLLM on a private Compose
network, while retaining separate source repositories/images. Deployment pins
component versions in a manifest.

## 18. SLAIF API Gateway integration

The gateway route resolves user/model permissions before the adapter. The
adapter should receive the resolved route rather than independently guessing
from model strings where possible.

Important accounting consequence: constitutional replacement and image pruning
change what vLLM tokenizes. Gateway pre-reservation remains conservative; final
provider usage is authoritative when available. Internal compiler overhead is a
separate capacity metric and an explicit pricing-policy decision.

Cross-repository changes use coordinated but separate PRs. The adapter can be
built/tested standalone against vLLM first. Gateway integration begins only when
the adapter contract is stable.

## 19. Verification architecture

### 19.1 Unit tests

Pure transforms, schemas, extraction, cache identity/invalidation, budget,
selector, header policy, and fail modes.

### 19.2 Fake-upstream contract tests

An ASGI/mock upstream returns JSON, errors, delayed streams, function-call SSE,
and disconnect scenarios. Tests prove faithful forwarding and no response
buffering.

### 19.3 Live vLLM tests

Use current authenticated private endpoint without changing the service. Verify
text, tools, streaming, vision, image cap, compiler call, cache hit, and sentinel
constitution behavior.

### 19.4 Actual Codex tests

Use a disposable Git repository and the installed Codex profile. Verify local
file/shell tools, long `AGENTS.md`, delegated documents, full image then crop,
compaction/history reduction, and immediate continued compliance.

### 19.5 Security tests

Header spoofing, principal isolation, no raw logs, malformed payloads,
compiler-schema injection, path traversal, cache permissions/limits, secret scan,
and upstream error sanitization.

## 20. Controlled cutover

The accepted development adapter must not automatically replace the current
Codex-to-Qwen/vLLM path.

A separate cutover objective must:

1. verify accepted/merged adapter version and clean CI;
2. capture the current Codex profile/provider endpoint and relevant service config/backup;
3. install adapter on a non-conflicting port first;
4. rerun real Codex text/tool/vision/compaction tests;
5. update gateway/profile to adapter deliberately;
6. verify no direct external vLLM route remains;
7. prove rollback to the prior endpoint;
8. avoid cutting off the active coding agent mid-turn;
9. report exact final service/port/firewall state;
10. require strategic/human acceptance before retiring any superseded compatibility path.

## 21. Licensing and provenance

The project should use Apache-2.0 unless the repository owner decides otherwise.
It must prominently acknowledge `syv-ai/qwen38-27b-rtx3090` and retain upstream
notices for reused code. Prefer pinned upstream checkout/patch integration over
copying the whole repository.

Model/checkpoint terms are independent. The installer records exact model
repository, revision, checksums, and license. No model weights enter Git.

## 22. OAP implementation sequence

The architecture is intentionally sliced into reviewable objectives:

- 000: live contract, pass-through foundation, image policy;
- 001: AGENTS detection and deterministic reference manifest;
- 002: internal compiler and validated cache;
- 003: injection, dependency acquisition, compaction rehydration;
- 004: actual Codex E2E, security/operations hardening;
- 005: gateway integration and controlled cutover;
- 006: reproducible SME package and honest release evidence.

Each numeric objective is one PR. Follow-up letters amend the same PR until the
strategic agent is satisfied and all required CI is green.

## 23. Acceptance definition for the product MVP

The MVP is credible when all of the following are demonstrated on the reference
host without client modification:

1. Codex reaches the adapter through an ordinary OpenAI-compatible profile.
2. Text Responses, ordinary tools, multi-turn continuation, and SSE still work.
3. Full image followed by crop succeeds although upstream accepts one image.
4. A long effective `AGENTS.md` is detected and compiled on first hash.
5. Delegated files are enumerated and ranked with evidence.
6. Repeated requests hit bounded content-addressed cache.
7. A distinctive binding rule remains available after simulated/actual
   compaction.
8. Changed governance content invalidates the old index.
9. Cache state cannot cross test principals/sessions.
10. No raw prompt/code/image/secret appears in logs or metrics.
11. vLLM, firewall, VPN, and current coding endpoint were not unintentionally
    modified.
12. The gateway integration path is documented and tested or explicitly remains
    the next separate milestone.

This is an SME-oriented engineering MVP, not a claim of general semantic memory,
perfect instruction interpretation, unlimited multimodality, or production
certification.

## 24. Open questions to answer empirically

- Exact current Codex request markers for effective `AGENTS.md` and tool-output
  file/path pairing.
- Best stable session discriminator available through current Codex and gateway.
- Whether Codex compaction frequency uses local estimates or provider-reported
  usage after transformation.
- Whether vLLM structured output is reliable enough for the compiler schema or
  requires tolerant parse/retry.
- Appropriate maximum source/injected sizes for latency and rule fidelity.
- Whether the compiler should use the same Qwen route or a smaller dedicated
  local model in larger deployments.
- Current verified zero-image launch/capacity fact and any future vision-mode
  configuration decision remain separate from the route-gated adapter design.
- How compiler GPU overhead should be represented in gateway capacity/pricing.

These are first-class test questions. The implementation must record evidence,
not turn assumptions into architecture claims.

# SLAIF LOCAL CODING — NORMATIVE AGENT ARCHITECTURE (compact)

Read before mutation. Full `ARCHITECTURE.md` is human-facing rationale; this
file is the default complete normative implementation map. Conflict/ambiguity:
stop and return to strategy; never choose weaker law.

## Mission and boundary

Private adapter makes ordinary Codex/OpenAI clients reliable against constrained
local models. Production path:

```text
client -> separate slaif-api-gateway -> this adapter -> private vLLM/Qwen
```

Gateway is separate repo and owns public keys, permissions, quotas, accounting,
routes, admin/TLS. This repo owns model-specific request adaptation,
constitutional compilation/cache/injection, local-model packaging/tests. Never
merge these responsibilities or copy gateway code silently.

## Cache profile scope (normative target)

The human-approved dependency-bundle cache rework is the **normative target**
for governance context state: the opt-in `dependency-bundles-v1` profile.
Requirements: the ten approved rules in `docs/CACHE-REWORK.md`. Resolved
engineering choices: `docs/CACHE-IMPLEMENTATION-PLAN.md`. Delivery and
acceptance state: `docs/CACHE-REWORK-LEDGER.md`.

The currently implemented behavior is the explicitly named **legacy**
profile: evidence-based root detection, root-declared narrow dependency
acquisition, filesystem-backed derived cache (TTL/LRU, content-addressed,
disposable), additive constitution injection, and process-local rehydration.
Legacy remains in effect until the v1 migration is qualified. Laws below that
are marked legacy apply only to it; they do not constrain the v1 profile, and
v1 laws do not retroactively reinterpret legacy settings. Never silently
reinterpret a legacy setting as v1, and never present legacy behavior as v1
delivery. Conflicting legacy cache/TTL/byte-budget settings under v1 are
configuration errors, not silent fallbacks. The profile is independent of
image policy; both profiles preserve every image, Gateway, API and
protected-service law in this file. Until the ledger shows otherwise, all v1
runtime claims are `NOT RUN`.

## Required stack

Python 3.12; `uv` locked/frozen; FastAPI/Starlette ASGI; HTTPX async streaming;
Pydantic settings/contracts; Uvicorn; pytest/pytest-asyncio + fake upstream;
Ruff + mypy; Prometheus-compatible private metrics. Separate repo venv; no torch,
model loading, image decode, or duplicate vLLM process in adapter. The v1
profile adds one pinned CPU-only actual-model tokenizer artifact
(version/digest bound to cache identity) in its tokenizer stage; it adds no
model weights, torch, or image decoding.

## APIs

Own `/healthz`, `/readyz`, private `/metrics`. Faithfully proxy at least
`/health`, `/v1/models`, `/v1/responses`, `/v1/chat/completions`. Preserve
status/errors/ordinary function tools/usage/SSE order/disconnect; no response
buffering. Parse bounded JSON only where transformation applies. Remove
hop-by-hop and spoofed internal headers. No raw payload logging. Upstream
HTTP-error causes are classified privately before close: bounded byte/time
diagnostic read, closed reason enum, status-derived categories without body
read, dedicated low-cardinality counter; the public status, generic body, and
safe headers never change and provider text never crosses the boundary.

## Ordered request pipeline

Legacy implemented pipeline (current behavior):

1. Build trusted request context: request ID, endpoint, route/model, opaque
   principal, session discriminator, streaming, internal compiler-bypass.
2. Select validated explicit route policy.
3. Apply image policy.
4. Observe/compile constitutional state.
5. Select bounded working constitution.
6. Inject idempotently in API-valid stable location.
7. Forward privately to vLLM and stream response.
8. Emit safe count/timing metrics only.

Compiler calls bypass this pipeline and call upstream directly; never recurse.

V1 planned commit order (normative target; not yet implemented):

1. Authenticate; resolve namespace, route, effective context contract and
   admission mode.
2. Apply the unchanged image policy; validate the supported JSON envelope.
3. Locate root/file observations and exact outer source spans; pair tool
   results by call ID.
4. Update the versioned graph; assess bundle admission (lean/greedy).
5. Resolve hits or compile misses into valid RAM entries; invalidate stale
   state.
6. Select a complete in-budget working set; construct the source-replacement
   plan.
7. Commit only when replacements, references, selected content and session
   state agree; serialize and forward the request exactly once.
8. Stream the response unchanged; record actual transform/usage outcomes.

V1 replacement plus required compiled injection is one transaction: the
adapter never deletes the only available governing content and then discovers
that compilation, checkpointing or budget selection failed.

## Image law

Route declares `max_images_per_request` and policy
`retain_newest|reject|passthrough`. For designated Qwen Codex vision route:
max=1, `retain_newest`. Support Responses `input_image` and Chat `image_url`;
zero/one unchanged; multiple retain exactly newest content item and preserve all
other order/content. Verify final count. Unknown over-limit shape fails closed.
Never apply globally. Explicit multi-image comparison is unsupported on this
route; use reject route, never claim semantic equivalence.

Existing localhost proxy is reference/proven behavior only. Integrate its pure
algorithm into shared adapter; no separate client proxy in final topology.
Image policy is ordered before and independent of both cache profiles.

## Constitution law (legacy profile, implemented)

`AGENTS.md` is constitutional root only when envelope/path evidence supports it:
Codex project-instruction marker, input-file filename, or paired file-read tool
result. Arbitrary mention is insufficient. Hash exact observed bytes.

Legacy dependency acquisition is root-declared and narrowly observed:
deterministic candidate enumeration from Markdown links, backticks/quotes/
path-like strings and normative-neighbor text; preserve every
candidate+evidence; reject URL/absolute/traversal. The model may rank,
not silently erase candidates.

On source/compiler cache miss, one bounded text-only internal Qwen call returns
strict validated schema:

```text
source hash/version
compact rules with MUST/MUST_NOT/NEVER strength+evidence
roles/authority/source-of-truth/order/exceptions
candidate path
reference_confidence 0..1
constitutional_priority 0..100
class P0 root | P1 delegated law/security | P2 binding procedure |
      P3 architecture/contract | P4 background/example
relationship/evidence/acquisition urgency
full-source reread triggers
```

Never use one ambiguous score. Compiler has no tools/network/filesystem/gateway
key; treats source as data; max one concurrent call; strict size/time/output;
invalid output never cached valid. Legacy adaptive truncation behavior
(`compiler-v3`: typed `finish_reason="length"` decided before content
validation, `min(prev*2, ceiling)` allowance, fingerprint/cache/rehydration
binding) is legacy-scoped and does not carry over to v1.

Referenced content is unavailable until it crosses API boundary. Missing P0/P1
causes injected instruction to read exact file with ordinary Codex local tools
before substantive mutation. When paired path/content tool output arrives,
hash/compile/update graph incrementally. Adapter never reads client filesystem.

## Dependency-bundle cache law (v1 profile, normative target)

As of stage 017-a (observation proof corrected in 017-b, and the
remaining literal-grammar and actual-endpoint proof in 017-c), the pure
root/read/result/span observation slice (D01-D05) is implemented as inert
typed modules under `src/slaif_local_coding/constitution/bundles/`; they are
not active in the adapter request execution path, the legacy detector is
unchanged, and every other statement below is the approved target contract.

**Root.** The evidenced effective `AGENTS.md` carries a workspace/directory
scope. Detection uses the versioned Codex user-message envelope with exact
content offsets and duplicate/malformed-marker handling; the optional
environment-context tail is excluded from source bytes. Arbitrary text,
assistant claims or tool descriptions never establish a root. Repeated
byte- and scope-identical root envelopes of the same root are idempotent and
deduplicated; distinct competing effective roots or a workspace-scope change
fail explicitly (never choosing one or resetting).

**Recursive graph.** Directed edges are discovered from raw observed source
before semantic compilation: explicit Markdown links, reference definitions,
backticked filenames and supported plain-text `.md` paths under the no-spaces
convention. References resolve relative to the **referring document's**
directory inside the evidenced workspace. Shared nodes, cycles and missing
content are preserved; iteration reaches a fixed point as new raw content
arrives. A reference establishes eligibility, not possession of content;
unread reachable nodes are `DISCOVERED_CONTENT_MISSING`. Lexical normalization
never escapes the evidenced workspace or touches the adapter filesystem;
external URLs are not repository dependencies. Where a boundaryless multi-
directory bundle leaves origin ambiguous, retain an unresolved-origin
candidate; never invent a source file or graph edge.

**Read observation.** Supported file-read tool calls are recognized with a
bounded literal shell-read grammar that is parsed, never executed. Support is
earned per command family and wrapper; complete outer spans and executed
member sets are mandatory, internal A/B boundaries optional. Call/result
pairing uses call IDs and multi-chunk completion proof. Per-command execution
evidence is distinct from the global exit status. Unknown, partial or
truncated output never becomes complete; a typed unsupported observation
preserves the uncertain span and exposes a limitation. Client-workspace
absolute paths normalize to repository-relative form only under proven
workspace context; they never become adapter-host reads. Earned in 017-d
(inert, `literal-read-plan/v1`): finite all-cat / literal-cd `&&` plans
with absolute literal `cd` transitions (per-call workdir takes precedence),
bounded literal `echo` prefix/suffix outer boundaries proven at their exact
positions, whole-plan bounds, and the law that a global nonzero in a chain
proves no per-read completion; loops, wildcards, semicolon and other
non-earned forms remain explicitly typed unsupported. Corrected in 017-e:
quoting does not disable `echo`'s option parser, so option-like dash-leading
quoted literals are implementation-sensitive, typed unsupported, and never
earn a boundary; and every observation produced through the finite-plan
parser carries the actual `literal-read-plan/v1` identity across all
outcomes, while observations the single grammar actually earned keep
`literal-shell-read/v1` (the grammar label never changes outcome or
digests). Earned in 017-f (inert, `literal-loop/v1`): finite literal
`for var in list; do ...; done` loops with the earned `f`/`d` variable
names, clean literal iteration lists, double-quoted one-reference
filename templates, the exact `|| exit 1` guard on each `cat`, and the
whole-loop expanded-operand budget never multiplied per iteration; an
all-success guarded pure-cat loop earns one ordered whole-source bundle
under a wrapper-proven exit-zero/untruncated/present completion,
unguarded or echo-labeled forms stay non-removable with typed
iteration/outer-attribution limitations, and every observation the
loop parser evaluates carries `literal-loop/v1`. Corrected in 017-g:
the unquoted `;` is its own syntactic element (a standalone token),
so a quoted prefix plus a literal suffix touching the list separator
(`for f in "A".md;`) stays one unearned word typed `QUOTED_OPERAND`
— never two members (`A` and `.md`) — with attached and spaced
separator forms observing identically and the plain/whole-word quoted
controls unchanged; the member-digest prose follows the occurrence
law (one member occurrence covering the entire attributable region
proves that file's digest; distinct slot width alone never does).

**Admission.** `lean` admits a whole bundle only when every member is
graph-eligible and may admit an isolated eligible portion when boundaries are
proven; `greedy` admits the whole bundle when at least one member is
graph-eligible. Neither admits an arbitrary unrelated single file. The mode
is explicit, recorded in configuration, cache identity and recovery state,
immutable within a session configuration identity, and defaults to `lean`.
Greedy co-cached members keep background provenance: they cannot acquire root
or system authority by co-occurrence. The explicit reference policy is fixed:
off-graph members do not expand governing reachability until independently
reachable, and no outgoing reference of an off-graph member is followed before
that member is independently graph-eligible. A boundaryless mixed-
eligibility bundle keeps an unknown eligible reference origin whenever
member attribution is unproven — even when the members' directories are
proven equal: a shared directory never identifies which eligible or
off-graph member supplied a reference. Retain an unresolved-origin
candidate set and never assume the common directory.

**Identity, replay and overlap.** An entry identity binds at least:
authenticated principal, stable session, repository/workspace, route/model,
ordered normalized member references, exact bundle-content digest,
parser/evidence/admission versions, graph/root scope, compiler model/revision
and prompt/schema/semantic-policy versions, tokenizer identity,
effective-context/insertion-budget configuration, and render-format versions.
`[A,B]`, `[A]` and `[B]` are independent entries; `[A,B]` and `[B,A]` are
distinct when order differs. Unknown individual member versions stay unknown;
a whole-bundle digest is never labeled as each member's hash. A reverse
member-path index invalidates overlapping entries and versioned graph edges
when a new version arrives. A fresh standalone observation with unknown older bundle-member ownership
invalidates the older boundaryless bundle conservatively: the bundle is marked
stale/conflicting without inventing a proven incompatibility or per-file
hashes; never splice unidentified bytes. Observations
deduplicate at a monotonic session revision; replayed history cannot roll
state back, and a deliberate revert requires a genuinely new observed
occurrence. Repeated file operands do not inflate slot width.

**Insertion budgets.** Effective context `C` is explicitly configured from a
validated route/session contract — never inferred from the serving maximum or
an executor profile. Base slot = `floor(C/32)`; bundle width = number of
distinct represented members; allowance = width × slot. An aggregate injection
limit (initial `floor(C/4)`) plus explicit reserves (generation
`max(4096, floor(C/8))`, tools 2048, uncertainty/template 1024; all
configurable and identity-bound) cap total injected content. Tokens are
counted with the pinned actual model tokenizer over the final rendered block
including references and metadata; byte/character heuristics are diagnostics
only. Per-file slots never authorize unbounded injection; compiled output over
its allowance is invalid for that allowance; required working-set overflow
returns a typed failure, never silent truncation or dangling required
references. Unknown or mismatched tokenizer/context/vision capability rejects
v1 readiness or the request.

**Compilation.** The compiler is a direct authenticated tool-free
non-recursive upstream channel that treats source as data; max one concurrent
compiler leader by default; single-flight per full key. Compile once per
unchanged bundle/version/configuration/live cache epoch. V1 has no automatic
infrastructure/schema/truncation retry: failed, cancelled, truncated or
over-budget results are invalid and explicitly reported; they are never cache
entries, never reported as hits, and never best-of-replayed. Recovery
recompilation is separate work with a new epoch and recorded reason. Compiler
semantic output preserves governing scopes, MUST/MUST_NOT/NEVER strength,
exceptions, conflicts, all deterministic candidates, and separate
reference-confidence from constitutional-priority.

**RAM ownership.** All live graph, index, source-version, compiled-entry,
selection and single-flight state lives in Python memory per session. Normal
hits, rendering, selection and reinjection never read or deserialize
checkpoint content, including files in `/dev/shm`; moving a file cache to
tmpfs does not satisfy this. There is no active-session TTL/LRU or
capacity-driven eviction of stored entries; insertion-budget pressure selects
fewer entries without evicting or forcing recompilation. One service worker
and one live owner per session in v1; unsupported multi-worker configuration
is rejected. Explicit configurable process and per-session safety ceilings
(initial documented recommendations 512 MiB and 128 MiB) bound admission;
they account owned cache state (cache occupancy), not a guarantee of total
process RSS; pressure returns a fixed 503 with existing state preserved. Cleanup happens
only through explicit session teardown or authorized retention cleanup, never
a hidden eviction loop.

**Recovery.** Per-session protected recovery is an explicit configuration
opt-in and is mandatory for an enabled `dependency-bundles-v1` profile (an
enabled v1 profile without recovery is a configuration error, not a supported
mode); it is likewise mandatory for v1 qualification. It retains the exact
extracted source bytes of the admitted original bundles plus the necessary
provenance — never environment-context tails or full transport envelopes — and
not whole conversations, images, transport credentials or unrelated tool
output — in a protected per-session namespace
(directory 0700, file 0600, current owner, no symlink or path escape) with
atomic generation publication, integrity digests, and fsync of file and
directory before committing any request that newly relies on that generation.
A failed checkpoint aborts that transformation. After restart, only a resumed
authenticated session's record is read; full binding/configuration/schema/
integrity validation precedes RAM reconstruction in a new cache epoch. Needed
valid bundles recompile lazily once per epoch under bounded concurrency, and
no main request forwards with unresolved required entries. Recovery originals
are never read on normal hits and never sent to the main model as a hidden
fallback; invalid historical originals remain evidence only. No automatic
dormant-session scan/recompile or automatic timed deletion; retention,
secure storage and any required filesystem encryption are operator-owned and
stated explicitly.

**Transactional replacement.** Source replacement is a pure versioned
exact-span edit plan coordinated with session state: it preserves tool call
IDs/names/arguments/order/status, prefix/suffix, ordinary text, images and API
envelopes; it replaces evidenced root and eligible read-content spans only
after compilation, selection and durable checkpoint preparation succeed; and
opaque namespace-bound references always accompany usable required compiled
content. Original source roles and authority stay explicit in compiled blocks;
off-graph greedy content never becomes system instruction. Unknown, forged,
cross-session or stale references are rejected. Replayed originals are
replaced again using RAM hits; transformed inputs are idempotent. Endpoint-
specific placement (Responses `instructions`, Chat stable system location) is
tested for authority preservation; adding text at a higher API role must not
promote off-graph content.

**Failure contract.** An unsupported or uncertain untransformed source may
pass unchanged with a fixed observable limitation, without claiming
acquisition or replacement. Once an admitted required transformation needs
compilation/checkpoint/state, failure rejects or defers with a sanitized
typed status: 503 (infrastructure/recovery/resource), 409 (version/scope
conflict), 422 (budget/invalid transform). The adapter never forwards dangling
virtual references, silently drops governance, loads disk originals for the
main model, or automatically replays a forwarded request. Disconnect cancels
owned upstream work; single-flight followers never cancel another request's
live leader. Authentication and image policy remain ordered and independent.

**Observability.** Fixed enums, counts and timings; no private filenames,
digests, session values or cache IDs in metric labels. Independently exposed
stages: root recognition, actual content acquisition, graph admission, first
compilation, RAM hit, source replacement, compiled injection, source-absent
injection, actual native compaction, restart recovery, final upstream
acceptance. A compiler-cache hit is never a "rehydration hit". Provider usage
and client cumulative usage are overlapping separate ledgers; compiler and
recovery overhead are separately metered. Protected synthetic evidence may
correlate exact requests/hashes for tests; no private corpus enters the
repository.

## Pseudo-context/cache law

Derived cache is disposable/non-authoritative. Repository/Git/GitHub and full
source override it.

```text
L0 bounded injected manifest
L1 compiled source indexes / compiled bundle entries
L2 observed source text
L3 client repository/Git/GitHub authority
```

Legacy profile: bounded filesystem derived cache at protected
`/dev/shm/slaif-local-coding` with protected XDG fallback; atomic files;
dirs 0700/files 0600; reject symlinks and foreign-owned paths; content-
addressed; hard total/per-entry bytes; bounded startup scan; TTL+LRU;
separate bounded pinned P0/P1; process-local rehydration map. This legacy
storage law applies only while the legacy profile serves.

V1 profile: RAM working entries per the dependency-bundle cache law above; no
TTL/LRU or capacity eviction of live-session state; separate per-session
protected recovery/evidence records. The recovery store is the narrow,
explicitly opted-in exception to the raw-source-persistence prohibition:
protected store only, exact observed original bundles and derived metadata
only, never transport credentials or credential-bearing wrappers, with
restricted ownership/permissions, integrity, explicit retention/deletion and
stated encryption prerequisites. Detectable forbidden credentials cause
typed rejection/quarantine without logging content; the adapter does not
claim complete secret detection and does not silently redact while claiming
exact fidelity.

Identity includes opaque principal, session/repository discriminator, source
hash, compiler/schema/model/policy/render versions, tokenizer and budget
identity, and all deterministic source/prompt/output/candidate/depth/
reasoning bounds. Never cross principals. No raw external key as cache
identity. External caller headers cannot assert trusted principal/route/
compiler-bypass state; production identity comes from authenticated/signed
internal gateway metadata. Raw source persistence off by default: v1 recovery
retention is enabled only by explicit operator configuration.

Working-set order (both profiles): P0 root; acquired P1; missing P1
acquisition list; relevant P2/P3 if budget. Stable deterministic ordering for
prefix cache. Hard injected limit. Marker says reconstructed context, sources
authoritative. Inject on every request, including after compaction. Do not
expose cache mechanics/secrets.

Compiler/cache failure: legacy preserves the original governance-bearing
request when safe; v1 follows its explicit failure contract. Neither profile
silently deletes law. Image enforcement remains independent.

## Identity/security

Production external key terminates at gateway. Adapter accepts service auth plus
signed opaque principal/session/route; strips caller spoofing. Raw external key
never cache key. MVP single-user fallback may use principal+route+best session+
root hash; absent reliable identity means no cross-request reuse beyond current
observed content. Multi-user release requires signed identity contract.
V1 binds every state object to the namespace of authenticated principal,
stable session, repository/workspace, route/model and full parser/compiler/
tokenizer/render/budget configuration identity. Initially one effective
root/workspace scope per v1 namespace; competing effective root
scopes or a workspace transition fail explicitly rather than choosing
or resetting.
Unsigned header identity and anonymous shared cache are not supported.

Never log/store raw prompts, source, images, tool output, bodies, auth, keys,
cookies, private URLs in operational logs/metrics. Metrics only counts/
timings/states with sanitized labels. V1 recovery records follow the
recovery store rules above. Bound request/source/compiler output/
cache/TTL/concurrency (legacy) and RAM ceilings/backpressure (v1).
Cancel upstream on disconnect.

## Live-host protection

Canonical paths:

```text
REPO=/synology/homes/janezp/codex-work/slaif-local-coding
STRATEGIC=/synology/homes/janezp/codex-supervision/slaif-local-coding
QWEN=/synology/homes/janezp/qwen-serving
UPSTREAM=http://127.0.0.1:18020/v1
DEV_ADAPTER=127.0.0.1:18031
```

Verify live facts first; historical docs are evidence only. The canonical value
above is the preferred same-host upstream on `hinton1`; `http://10.8.132.75`
is the optional LAN alternative, while `http://10.8.132.76` is historical
provenance. No pre-existing image proxy or port-18021 service is assumed.
Development/candidate service MUST use
18031 unless a work order explicitly selects another free port. Without explicit
active service-mutation order NEVER stop/change `qwen-serving`, model/checkpoint/
patches, API-key files, systemd units, VPN/firewall/network binding, port 18020,
or launch flags. Passwordless sudo permits safe repo-local tools/services, not protected
fixture mutation. No direct public vLLM.

## Resource law

RTX 3090/24 GB tight: adapter CPU-only; one compiler call default; deduplicate
same misses; bounded live tests; no image decode/re-encode; stream bodies/
responses where possible; no duplicate model; backpressure/
timeout on saturation. Internal compiler overhead separately metered. V1 adds
explicit RAM safety ceilings with fixed 503 backpressure instead of eviction,
a pinned CPU-only tokenizer artifact, and per-session recovery write bounds;
recovery disk use is bounded retention, not a hot path.

## Failure law

- upstream unavailable -> sanitized 502/503, readiness fail;
- malformed transform JSON -> explicit 4xx, no unsafe bypass;
- compiler error -> legacy: original semantics/fallback, no governance
  deletion; v1: typed invalid result, no cache entry, no retry, no hidden
  original fallback;
- cache error -> legacy: operate unoptimized; v1: explicit backpressure or
  typed rejection, no hidden disk hot path;
- over-limit image -> configured transform or deterministic reject;
- missing identity -> no cross-tenant reuse;
- disconnect -> close/cancel upstream;
- unknown policy/capability -> fail startup/readiness, not guess;
- v1 source/version conflict -> affected bundles stale/conflicting, 409;
- v1 budget/overflow -> typed 422, no silent truncation or dangling required
  references;
- v1 RAM exhaustion -> visible fixed 503, state preserved, no eviction churn;
- v1 checkpoint failure -> that transformation aborts; resume validates or
  fails explicitly.

## Verification law

Required layers: pure unit; fake-upstream contract/SSE/errors/disconnect;
image zero/one/multiple; AGENTS detection/candidate evidence/schema/compiler/
cache/invalidation/budget/isolation/injection/failure (legacy profile);
bounded live vLLM text/tool/stream/multiturn/vision/two-image/compiler/cache;
actual Codex long-AGENTS + full-image→crop + compaction/history reduction;
secret/raw-log scans.

Planned v1 layers (gates in `docs/CACHE-REWORK-LEDGER.md`, all `NOT RUN` until
their stage lands): versioned real-format root/read/span fixtures (D);
recursive graph, lean/greedy admission, overlap/replay invalidation (G/C);
RAM ownership, single-flight, capacity/backpressure (C03/M01/M04/M05);
protected recovery positives and corrupt/torn/foreign/config-mismatch
negatives (M02–M04); pinned-tokenizer budget and compiler failure/no-retry/
compile-once behavior (B, C03); transactional replacement with actual
upstream-body proof and idempotence/forgery negatives (R, S02); full-stack
adversarial/lifecycle/isolation/cancellation matrix (S, O); bounded
actual-model and genuine-Codex qualification (O). Full request tests verify
the actual upstream body; counter flags or configuration values alone never
prove original removal or compiled delivery.

Exact status labels; skipped/pending/missing/not-run never pass. Green CI required,
not sufficient. RC10 is the historical baseline for the rework, not a
rework-qualified artifact.

## Packaging/cutover

Initial service on 18031 only. systemd template uses repo venv+protected env,
safe logs. OCI/Compose later. Separate explicit accepted cutover backs up old
unit/profile, tests candidate, switches gateway/profile, proves rollback, never
cuts off active coding turn. Model weights never in Git. Pin/provenance/license
all components; prominently credit Apache-2.0
`syv-ai/qwen38-27b-rtx3090`; preserve notices/modified-file markers. Frozen
published RC records (RC10 and earlier) are immutable: development changes to
artifact inputs require the development-state provenance contract, never a
rewrite of published records.

## Objective boundaries

Merged (verified 2026-09-14): 000 pass-through+image policy/live fixtures
(PR #1); 001 detection+deterministic paths (PR #2); 002 compiler+cache
(PR #3); 003 injection/acquisition/rehydration (PR #4/#5); 004 real
Codex+security/ops (PR #6, real-E2E accepted fixture-scoped); 005 gateway
integration+cutover contract (PR #7; the live cutover itself remains a
separate human-authorized act); 006 signed-request replay hardening (PR #8);
007 current Gateway contract CI (PR #9); 008 durable acceptance evidence
(PR #10). Objectives 009–015 are merged through PR #22 (the release-candidate
line; it concluded with the private RC10 candidate). Cutover NOT
performed; NOT released. Objective 016 (merged PR #24, merge
`96c790423f6f0097a56a0b12bacda8a9b6da6aba`): dependency-bundle cache rework
contracts — handoff, plan, reconciled architecture/law, stage ledger.
Objective 017 is active (017-a published but not accepted; 017-b corrects
its bounded observation-proof findings A-E; 017-c corrects the remaining
literal-grammar and actual-endpoint proof; 017-d corrects the root-domain
prerequisite — root observation scoped to the actual selected Responses
domain, no root minting from unused containers on Chat/mixed/unknown/
invalid selections — and earns the D06/D07/D08 finite read-plan slice in
the inert module `constitution/bundles/compound_reads.py` (all-cat /
literal-cd `&&` plans as one ordered bundle, absolute literal `cd`
transitions with per-call workdir precedence, bounded literal `echo`
outer boundaries, per-read vs global exit evidence, whole-plan bounds);
017-e corrects that slice's echo option semantics and plan-grammar
identity on the same inert surface; 017-f earns the bounded pure
literal-loop slice — the D07 loop criterion, not a blanket D09/D10
completion — in the inert module `constitution/bundles/literal_loops.py`
(grammar `literal-loop/v1`: deterministic requested members, all-
success guarded pure-cat bundles, typed unguarded/labeled/control-flow
forms; 017-g corrects the loop word/separator law — the unquoted `;`
is a standalone token, a quoted prefix plus a literal suffix touching
the separator stays one unearned word, never two members — and the
member-digest prose follows the occurrence law); the remaining D09/D10
multi-chunk process-completion and branch-matrix scope is planned for
a later same-PR suffix (process/chunk association, subject to
review));
objectives 018–024 remain the planned inert draft succession for the v1
implementation stages (see `docs/CACHE-REWORK-LEDGER.md`). The original
planned meanings of numeric 006-008 are historical planning prose, not live
identifiers. Strategy may revise only from verified evidence. One numeric
objective=one PR; coding never merges.

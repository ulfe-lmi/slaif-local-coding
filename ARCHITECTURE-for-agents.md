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
digests). Corrected in 017-m (per-request pairing identity and
causality, section D05 of the observation contract): the relevant
schema-evidenced call identities are inventoried independently of read
eligibility — an unknown/ineligible tool call never acquires a source,
but its ID colliding with an eligible call ID is a typed
`DUPLICATE_CALL_ID` conflict, never filtered away; unrelated unique
unknown calls are neither recorded nor allowed to poison separate
valid chains; arbitrary nested text objects carrying id/name are not
call records; absent/null/empty IDs are typed `MISSING_CALL_ID` and
present non-string IDs `MALFORMED_CALL_ID`, both observable, never
pairing, never inventing an ID — and a result attaches to its
matching call only when its exact numeric structural position follows
the call's (the `input` item index; the Chat `messages` index of the
assistant message carrying the call), never from lexical call IDs,
JSONPath string sorting or JSONPath evaluation; a result before its
matching call keeps its chain typed `PRE_CALL_RESULT` and
non-removable with no bundle/member digest, no source span and no
proven-executed claim, while missing initial calls remain
unsupported. Corrected in 017-n (identity-inventory boundaries,
section D05 of the observation contract): the Responses
`custom_tool_call` identity joins the call inventory alongside
`function_call` — identity bookkeeping only (no custom-tool read
parsing/execution/acquisition, opaque input never reinterpreted, no
generic unknown-family wildcard), so an exact colliding ID makes the
ambiguous eligible chain typed/non-removable with no acquired
digest/span/proven members while a unique unrelated opaque custom
call neither records nor poisons a valid chain; `max_commands`/
`max_outputs` bound the **complete** relevant inventory (unsupported
names, opaque custom records, missing/empty/malformed IDs, invalid
result IDs) before any identity map or diagnostic is retained — a
fixed non-acquiring `OVER_BOUND`, the scan bounded by the existing
item bound, selected-domain scoping under explicit endpoint
selection, mixed bounded across inspected domains; absent/
null/empty and non-string result IDs are fixed typed non-echoing
unpaired limitations (`MISSING_RESULT_ID`/`MALFORMED_RESULT_ID`),
never invented, hashed, attached or acquired. Earned in 017-f
(inert, `literal-loop/v1`): finite literal
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
Objective 017 is active (rounds 017-a through 017-aa reports published; 017-aa integrated the owner-UID fixture path below — software-only, with its recorded process limitations — and 017-ab activated that sealed entry and executed its ONE bounded actual Python-only owner-UID capability qualification (a closed terminal pass whose measured outcome is recorded in the immutable round report; still no native, D09, whole-017 or v1 runtime claim); detailed round history is in `docs/CACHE-REWORK-LEDGER.md` and the immutable OAP transcripts, not restated here). Current earned scope on the inert pure-observation package `src/slaif_local_coding/constitution/bundles/` (never active in the adapter; legacy detector unchanged): the D01-D05 root/path/read/result/span observation, including the 017-m per-request pairing identity/causality law — the schema-evidenced call-ID inventory is eligibility-independent (an unknown/ineligible call never acquires, but a collision with an eligible call ID cannot disappear through filtering; missing/empty/malformed IDs stay observable and are never invented), and a result attaches only when its exact numeric structural position (the `input` item index; the Chat `messages` index of the assistant message carrying the call) follows the matching call's (never lexical call IDs or JSONPath string sorting; a pre-call result is a typed `PRE_CALL_RESULT` non-removable chain with no bundle/member digest, source span or proven-executed claim) — and the 017-n identity-inventory boundaries: the Responses `custom_tool_call` identity joins the call inventory alongside `function_call` (identity bookkeeping only — no custom-tool read parsing/execution/acquisition, opaque input never reinterpreted, no generic unknown-family wildcard — so an exact colliding ID makes the ambiguous eligible chain typed/non-removable with no acquired digest/span/proven members while a unique unrelated opaque custom call neither records nor poisons a valid chain); `max_commands`/`max_outputs` bound the complete relevant inventory (unsupported names, opaque custom records, missing/empty/malformed IDs, invalid result IDs) by a no-retention streaming preflight decided before any record tuple, location string, identity map or diagnostic is retained (fixed non-acquiring `OVER_BOUND`, selected-domain scoping under explicit endpoint selection); absent/null/empty and non-string result IDs are typed `MISSING_RESULT_ID`/`MALFORMED_RESULT_ID` non-echoing unpaired limitations, never invented, hashed, attached or acquired; exact internal call/result IDs stay usable while operational `str`/`repr` of report/read/unpaired objects never echo private ID values (fixed `<private-id>` placeholder for non-empty values; the observable no-ID state, fixed enums, counts, locations and digests remain visible) — plus the D06/D07/D08 finite read plans (`literal-read-plan/v1`), the D07 literal-loop slice (`literal-loop/v1`), and the public D10 composition matrix with the pure D09 unsupported/partial negative matrix (`tests/test_bundle_d10_matrix.py`). Round 017-p enforces the per-nested-container `max_items` scan guard (each inspected assistant `tool_calls` list is O(1) length-tested before it is iterated, parsed or retained; `max_items` is per-container, never a total across lists — an at-limit nested list observes normally) and lands the disposable-CI containment capability (`scripts/cache_native_containment_probe.py` in-container stdlib probe plus `scripts/cache_native_containment_ci.py` host runner, whose entry guard refuses any context that is not both `GITHUB_ACTIONS=true` and `RUNNER_ENVIRONMENT=github-hosted`, with the `cache-native-containment` CI job as the remote proof: digest-pinned fixture image, explicit confinement surface, ordered token-bound parent-death proof, bounded capture with fixed closed failure states, and verified image removal; the first remote job run at the previously published head `ec08a1b` failed `runtime-invalid` and this round corrects the runtime-shape handling — capability qualification `PENDING` strategic review) — capability proof only: no genuine client/model/GPU/gateway activity, no secrets forwarded to the fixture, D09 remains `NOT RUN`, no v1 runtime claim. Round 017-r further lands the serial right-pane native fixture preparation (typed phase/budget model; distinct 21001/21002 confinement fixture image with the immutable 0555 binary PATH entry plus 0444 public LICENSE/NOTICE; ten fresh-container scenarios; one non-resettable host ledger shared with the single run deadline — distinct measured quantities, pre-work worst-case bound checks (no held amount stored), scenario-end measured charges, timed-out captures charged their measured drained total; closed-bound post-teardown /proc scan (over-bound listings rejected, never truncated); exact-owned cleanup with honest unverified states, verified scratch-root destruction and atomic no-overwrite evidence publication) driven by a Python-only disposable-CI `cache-native-fixture` job, where the public pinned 0.164.0 musl artifact is fetched, size+digest-verified, bounded-extracted and statically hashed but never executed; the bounded 017-r fixture preparation is accepted (strategic decision at head `2ce9dcd`, with the recorded wording limitations in `reviews/017-r-decision.md`), the serial foreground handoff itself remains a later separately authorized order, D09 remains `NOT RUN`, no v1 runtime claim. Round 017-s further lands the local fixture preparation and one bounded Python-only local rehearsal (repo-owned stdlib-only `scripts/cache_native_fixture_local.py`): one long-lived non-Codex Python fixture owner (the supervisor) behind the protected bounded prepare/observe/rehearse/finish/abort lifecycle — single RAM run context, one non-resettable 1800 s END anchor plus one bounded 600 s cleanup grace, cumulative ledger across every phase and error, exact CID registered BEFORE start, protected 0700 control root with 0600 socket/state outside the disposable work root, owner-side self-convergence on caller death (no host PID signalling, no worker stop) — and the section-2 verified local endpoint binding (read-only lstat of the documented default unix socket; every run Docker child inherits a frozen once-per-owner environment with DOCKER_HOST pinned to that verified socket and the overriding context selection removed; explicit remote selection refused before any mutation; no endpoint value echoed); the one order-bound rehearsal (ran EXACTLY ONCE, bound to implementation head `2a9c44e2ee327b965828bafdfcaf444abc3a581c` with source inputs `54ef177`, PASSED, with the same reviewed confinement, the Python-only diagnostic/PTY consume and the variant-aware finish (python-rehearsal/unobserved/external, retained summary bound to the decoded payload), leaving no prepared container, supervisor, listener, key file or owned image, `native_started`/`worker_stopped`/`codex_invoked` false throughout, actual measured facts in the immutable round report); the handoff-preparation qualification stays `PENDING` strategic review of the actual outcomes, D09 remains `NOT RUN`, no v1 runtime claim. Round 017-t finalizes the S evidence record and further lands the INERT native-handoff preparation boundary: the typed immutable order/run binding (`scripts/cache_native_fixture_binding.py`) — one explicit opted-in run bound, before any mutation, to the exact active order ID, its unique committed immutable order, the literal committed source head, the repository identity (owner/repo; the origin URL is never retained or echoed, private endpoints refused) and a module-minted run identity; strictly read-only, no GitHub/network call, per-order stable one-attempt namespaces in which a changed head/directory/phase never resets the attempt, and the historical exhausted 017-s record preserved in its exact schema — and the versioned read-only native-handoff preparation contract (`scripts/cache_native_fixture_native_prep.py`, `slaif-native-handoff-prep-v1`) with fixture-owner facts kept separate from external-native facts, the closed subject-identity law (exact registered CID, UID/GID 21002 with the closed group law, argv exactly `codex --yolo --profile early-beta`, pinned binary identity, birth bound, and the expected-PTY provenance — native qualification requires an actually bound, matched, nonzero expected PTY, and an unobserved expectation or a measured tty0 subject is never ready), read-only worker/Bash group facts (bounded membership, separately grouped owned tool sessions, job J never guessed, tty foreground a read-only observation, no signal of any kind), the separately measured stop and restoration phases kept distinct (the recorded stop: worker T, Bash running, G differing from B's group, all observed G members stopped — each listed row tri-stated so only verified-gone churn is ignored and an unreadable still-existing or unprovable entry is a closed refusal — foreground observed back on B's group after Bash reclaimed the TTY; restoration: the same worker running again with the observed foreground back on its own group G, measured against that recorded stop; a refused stop can never later claim restoration), closed verdict composition (unknown/unobserved/incomplete never ready/pass; caller-authored ready/status/flag JSON refused; a historical S-scope owner record decodes and validates as its own scope but can never qualify a native-ready composition — the closed `owner-scope-not-native` refusal; an honest started-but-not-ready native-owner record never becomes ready; and the owner's registered artifact binary must equal the measured subject executable), the native-owner evidence producer (`slaif-native-owner-evidence-v1`) that invokes the owned finish/export/teardown measurement seam, validates the FULL measured export payload with the actual shared export validator, recomputes the export digest itself, and binds the measured teardown to the exact immutable order/source-head/run/CID/image/binary context (closed six-key measured context; incomplete or contradicting contexts are closed refusals; the image id admits only the bare digest or the actual measured `sha256:<digest>` form, the typed fact normalized to the bare digest; the consumer validates the exact closed record key sets, top level and nested, and unknown or missing fields are closed non-echoing refusals), the real owned measurement adapter that reads the completed fixture owner's closed attribute seam and derives the run's native started/ready facts ONLY from the public workflow's measured pre-teardown subject receipt (a caller flag never mints them; a subject with an unbound expected PTY or a measured binary contradicting the owner's registered artifact is honestly started-but-not-ready), and the public prepare/observe/finalize workflow (collects before recording; no CLI; prepopulated records are not evidence; finalize binds a native-owner record to the immutable workflow binding's order, literal source head and run, and the retained subject receipt to that same run); 169 pure/fake plus tiny exact-owned Python child tests (`tests/test_cache_native_fixture_binding.py`, 45; `tests/test_cache_native_fixture_native_prep.py`, 124); no native launch (including help/version), no worker stop, no local Docker operation and no new rehearsal (the S admission stays consumed); the later serial native handoff remains a separately authorized order, D09 remains `NOT RUN`, no v1 runtime claim. Round 017-u completes the complete-inventory law demonstrated in review 11 (a stat-unreadable but positively still-existing PID was silently skipped and minted a complete stop receipt): every listed process row is now tri-stated through the bounded read-only absence seam (its historical verified-absence contract — True verified absent, False exists, None unknown, missing capability stays unknown); only an independently verified-gone entry may be ignored (bounded churn law); an unreadable still-existing or unprovable entry cannot establish nonmembership, a complete group or a complete stop (closed non-echoing refusals, never a silently skipped listing row); a failed initial prepare/observe mints no baseline or admission, and a refused stop can never later claim a recorded stop or restoration; the unchanged four-case group-readability probe passes 4/4 at the repaired source, with the original 13 preparation probes, frozen 21 and installed 27 retaining their earned scope; the S admission remains consumed, D09 remains `NOT RUN`, no v1 runtime claim. Round 017-v materializes the small EXPLICIT public native-owner lifecycle composition (repo-owned stdlib-only `scripts/cache_native_fixture_native_owner.py`, `NativeOwnerRun`): the verified immutable order/run binding selects the authority of its OWN order at the REAL fixture-owner constructor (the S default and the historical S opt-in unchanged; a new-order binding requires a live bound admission in the order's stable one-attempt namespace before adoption and re-validates the real repository context READ-ONLY through the actual resolver; the owner adopts the binding's minted run identity with no second mint or admission; a post-admission constructor failure closes the same run honestly), ONE shared owner, RAM run context, absolute END anchor, ledger and cleanup grace across the bounded public lifecycle (start/prepare/observe/record_stop/register_subject/finish/abort), the public staged subject registration (only after prepare and the separately measured stop; the CURRENT stable-stop predicate re-verified before any identity commit; the frozen W/B baseline unchanged; the registered run immutable; a refused registration commits nothing), the DISTINCT native-scope owner terminal record (`slaif-native-owner-run-evidence-v1` — the S measured facts WITHOUT the historical S whole-run false assertions; the S record is never relabeled), the closed native-run terminal record (`slaif-native-owner-run-v1`) with its consumer's cross-field readiness law and the protected 0600 atomic no-overwrite retention, and the HONEST publication ordering (a terminal fail/aborted finalized honestly at convergence; a converged pass keeps the bound attempt running; the protected native record retained FIRST and the same-order journal finalized ONLY THEN; a failed publication never leaves an admitted pass; the real finalize token retained in RAM only); 12 pure/fake composition tests driving the REAL owner finish/export/teardown code with fake platform operations over ONE coupled fake process world; no actual Docker operation, no native launch (including help/version), no worker stop, no real fixture admission in the real checkout, no host signal, no CLI entry; the later serial native handoff remains a separately authorized order, D09 remains `NOT RUN`, no v1 runtime claim. Round 017-w closes the remaining same-owner coherence gaps (the public staged registration is bound, before any staged receipt commit, to THIS SAME prepared owner's measured registration — the owner's own registered CID and artifact binary must be measured and equal the operator's expectation, a matching foreign expectation/channel or foreign expected + measured binary can never redefine the owner's subject, a refused registration commits nothing and a later matching registration in the same still-valid phase remains possible; the actual repository context at the actual owner construction is compared with the ORIGINAL frozen binding through the complete revalidation seam rather than a fresh resolution whose result is discarded — a post-admission identity drift is refused before owner adoption with the already-won attempt closed terminal `fail` and no external action, and a contradictory `bind_head` argument is refused; and native publication for the completed owner is a ONE-SHOT terminal transition — the ACTUAL bound journal state is read, never assumed, the pass path requires the attempt still running, a pre-retention measurement/validation/serialization/destination failure closes the still-pending attempt truthfully with the primary closed refusal propagating unchanged, the protected record is retained FIRST, and a post-retention unverified or raced finalization is a closed failure preserving the retained bytes and the actual journal facts as-is, with any fresh-path retry refused without a new qualifying record, relabel or journal reset); the composition suite grows to 19 pure/fake tests (7 new); no actual Docker operation, no native launch (including help/version), no worker stop, no real fixture admission in the real checkout, no host signal, no CLI entry; the later serial native handoff remains a separately authorized order, D09 remains `NOT RUN`, no v1 runtime claim. Round 017-x lands the one bounded Python-only actual fixture capability measurement (repo-owned stdlib-only driver `scripts/cache_native_fixture_exec_capability.py`, closed record `slaif-017x-exec-capability-driver-v1`): the SEALED bound child owns resolve+admit ONCE before any external work (the module-minted run identity is admitted in the child's process; the driver only verifies the child's closed protected outputs — it never re-resolves, re-mints, adopts or replaces a run id, and an exhausted running journal is refused, never adopted or reconstructed); startup authority (the fresh protected bootstrap refuses any pre-existing control root, the published owner state is bound to the ACTUAL still-live sealed child PID of this launch, and a foreign prior-owner state — even with a matching run id and head — is never adopted: no child launch, no command, no journal mutation); the prepare->hold->finish lifecycle over ONE shared owner/run/ledger/END issues the ONE closed detached stand-in hold exec (subject UID/GID 21002 on the held prepared exact CID, the issued 32-hex run marker on argv, ONE subject start in the order INCLUDING failed starts); the bounded exact-CID discovery (the owner's OWN guarded `top` inventory is the closed membership authority — every query charges the same ledger/deadline, at most the 96-row fixture pids limit, host /proc NEVER enumerated for membership: the host view is consulted per attested PID only, each attested member verified in-scope through the registered-CID channel before it may be a row, churn counted absent only when the channel independently verifies the PID gone, an existing-but-unreadable or raced member a closed refusal, a host PID outside the attested list never a candidate); the issued-marker kernel-cmdline correlation (the exact closed hold form, FRESH against the pre-launch inventory — a previous attachment never adopted; ambiguous, duplicate or identity-mismatched candidates refused); the scoped current-executable read through the existing unprivileged host CID channel (the order prose `HostCidScopedTable` names that same existing `RealCidScopedTable` channel — a naming clarification, no rename): at most 16 MiB and 10 s, further clamped at MEASUREMENT time against the SAME remaining owner END (cleanup grace is convergence, never fresh measurement) intersected with the issued hold's own finite lifetime, birth-bound, with PID/birth/CID/UID/GID frame checks before AND after (the observed identity capability and the executable capability are distinct closed fields; an unreadable or absent executable is a closed unknown, never an artifact-hash fallback); the subject then exits on its own finite hold and the driver polls the channel's tri-state verified-absence primitive on a bounded window (no signal, no kill, no watchdog — the owner's exact-CID cleanup is the removal path on every outcome; a `verified-gone` observation proves ABSENCE only, never an exit code or termination cause); any capability-phase failure before the finish converges through the owner's OWN bounded abort terminal command (never a host signal; the terminal command is issued first and its issuance tracked, never derived; the owner's retained terminal evidence validated with the reviewed closed validator bound to this exact attempt — a valid foreign record is not this run's evidence); the whole driver budget is the owner's published END anchor plus its one allowed cleanup grace (an expired budget refuses before any blocking wait); and the W-order publication law (on a verified owner PASS: the validated protected owner evidence first, then the driver's own protected capability-record retention — `--record-out` is REQUIRED by the CLI preflight, so the ONE qualification attempt is never admitted without its retention destination, and a destination at or under the work root a closed read-only refusal before any launch — and only then the verified same-attempt terminal finalization; a refusal closes the returned record as fail with no journal pass and no fresh-path retry; an unverified token never returns a qualified success); a driver pass is a closed truthful conclusion in which an unknown or refusal is a USEFUL diagnostic, never readiness or a native-ready/whole-017 claim; 34 focused tests in three distinct layers (the real CLI admission grammar plus the child-owned resolve+admit law; the scripted driver bootstrap over an actual launched Python child; the in-process real public-owner measurements including the scoped read measured BEFORE the owner finish — useful fake proof, not one full sealed-real-owner end-to-end test); the ONE authorized bounded actual Python-only attempt RAN EXACTLY ONCE at literal implementation head `e5215ce1a96b4dbecdcca5157b6a21ef30a6b1da` (run `9fd5cf1d95924a47b8bf53e8624242a5`): a terminal FAIL at prepare-target with `controller-not-ready` and `capability` null — no complete preparation, hold, subject identity or executable result (neither a readable nor an unreadable executable was established); the admission is terminal fail and is never reset, retried or relabeled, and its measured outcome is recorded in the immutable round report; no native launch, no worker stop, no host signal; D09 remains `NOT RUN`, no v1 runtime claim. Round 017-y adds the SECOND explicit sealed entry to the capability driver (order 017-y with record `slaif-017y-exec-capability-driver-v1` paired ONLY with order 017-y; the historical S/X entries, record/order pairs and the consumed X namespace unchanged) and the closed readiness diagnosis: on a nonzero bounded readiness exec ONLY the fixed probe's own exact finite closed failure record refines the original `controller-not-ready` category as `controller-not-ready:<cause>` (the fixed measured causes `uid-not-21001`, `pid1-uid`, `health-unreachable`; a missing, malformed, multiple/duplicate, foreign, over-bound or contradictory output is the fixed unknown, a raw exception or Docker failure is never a measured cause, and no raw output is ever persisted); the readiness failure path records NO readiness-poll count (an unmeasured quantity, never a claim of zero actual readiness polls); the ONE conditional bounded lifecycle query (issued only when the readiness exec produced no closed record: exactly one allowlisted read-only `docker inspect` of the single finite fact `.State.Status` on the SAME registered CID, charged to the SAME owner ledger/END — only the closed line `exited` refines to `controller-not-ready:container-exited`, and any other status, any other output shape and EVERY query failure (including a bounded timeout and a transport failure) stay honestly unknown — query failure is NOT absence); the closed consumer law (a retained capability record is valid ONLY under its canonical sealed entry — a caller-created descriptor or a cross-entry pair is a closed refusal — and the terminal retention/qualification propagates the entry through both the pass and fail paths, the matching record retained FIRST and only then the pass finalization); 10 focused tests added across the three fixture suites (ci 224, local 50, exec_capability 38); the actual outcome of the ONE separately bound 017-y attempt RAN EXACTLY ONCE at literal implementation head `35a3bcd7322535dd4a699efc53c0c1c62d4c942e` (run `fbe526a3290d465298bc8da61ef2a304`): a closed driver PASS with the complete preparation, confinement and Python-PTY phases; the subject uniquely identified and measured from the exact-CID inventory (UID/GID/groups 21002, birth-bound), then observed `verified-gone` after the bounded hold (absence only — never an exit code or termination cause), while the current executable remained the closed UNKNOWN (no digest; not native readiness and no proven kernel/errno cause); the admission is terminal pass and is never reset, retried or relabeled; the measured outcome is recorded in the immutable round report; no native launch, no worker stop, no host signal; D09 remains `NOT RUN`, no v1 runtime claim. Round 017-z lands the inert versioned fixture identity contract (repo-owned stdlib-only `scripts/cache_native_fixture_identity.py`, software-only — no runtime switch, no new admission, no Docker/native work): two closed, explicitly named, immutable identity descriptions distinct from adapter cache profiles — `slaif-fixture-identity-original-v1` (controller 21001/21001, subject 21002/21002, expected groups (21002,); REMAINS the current fixture identity, every old record/schema/constant meaning unchanged) and the INERT `slaif-fixture-identity-owner-uid-v1` candidate (subject UID/GID equal to the captured eligible host owner's real/effective/saved values, each triple's three values equal, nonroot, strict finite Linux IDs 1..4294967294, distinct from the controller identity; expected subject groups exactly the primary GID, never host supplementary groups); the strict closed record `slaif-fixture-identity-record-v1` with a bounded mapping codec (at most 4096 bytes, exactly one mapping, no duplicate keys; malformed/duplicate/over-bound/missing/extra/contradictory input refused with fixed non-echoing reasons) and a deterministic canonical configuration fingerprint (a configuration digest that binds complete profile semantics — never a process hash, trusted identity receipt, admission, cache key or readiness certificate); the bounded READ-ONLY host-owner-ID collector (direct stdlib getresuid/getresgid plus the simple uid/euid/gid/egid getters cross-checked, one collection, explicit unsupported/unavailable outcome; no fs/proc traversal, env/config/profile read, network, subprocess, signal or privilege mutation) behind a narrow fake OS-read seam with raw collection / data validation / derivation kept separate; construction enforces the complete field laws (no mutable alias retained, an oversized group vector refused before any copy, no invalid field can exist in a description); typed objects, decoded JSON/data, a profile name, a fingerprint or caller flags NEVER establish measured authority — a valid closed record may decode into an immutable description (a pure data transformation, not measurement authority; serialization validity does not prove the IDs came from an OS observation), the contract selects no live profile, records no fixture admission and yields no ready/native verdict; the required later sealed-child integration boundary (select a canonical profile, collect/freeze actual owner IDs, bind them to the ORIGINAL verified order/head/run and live admission before external work, revalidate the same context at use) is described, not implemented, and no path is opened through the existing local CLI/defaults/validators; a later profile must preserve private PID/mount/IPC/UTS/network namespaces, no host mounts/devices, rootfs-readonly, cap-drop-ALL/no-new-privileges/seccomp, exact bounded storage/memory/swap/pids/CPU, controller-private paths and EMPIRICAL keyring denial under the matching host UID (matching UID is NOT proof of safe containment), and the later native artifact (308139304 bytes) needs a later justified native-size byte/time measurement bound, not blind reuse of the Python 16 MiB/10 s bound; the helper is repository-only under the existing scripts exclusion (neither wheel nor sdist; dev provenance input map 197 -> 198 with the new test; wheel byte-identical); 19 focused tests (48 collected cases) in `tests/test_cache_native_fixture_identity.py` plus the relevant original fixture suites unchanged; no .oap-local/017-z root, no actual fixture/Docker/admission/native work, no host signal; D09 remains `NOT RUN`, no v1 runtime claim. The offline, opt-in, fail-closed, stdlib-only process-capture utility (`scripts/real_client_capture.py`) is inert (not wired into the adapter runtime), hard-capped, privacy-law enforced in code, actual-client path input-gated (generated startup readiness `not_ready`; caller-supplied `ready`/authorization records can launch the bound stand-in through the public API), with no actual capture, process collector or model call performed and no format or process acquisition earned. Remaining: the D09 actual-trace/multi-chunk process-completion and process/chunk collector gap is `NOT RUN`, planned for a later same-PR suffix (a later exact order may authorize one bounded reviewed actual capture, then the process/chunk collector, subject to review));

Round 017-aa integrates the 017-z inert owner-UID identity contract
through the REAL existing fixture owner, its prepared
image/exec/measurement/control/evidence path and the Python
capability driver.  Software-only: the integrated path stays
input-gated and UNQUALIFIED until a later actual order — no real
local Docker/fixture/owner startup, admission, native/extra Codex,
worker stop, signal, TTY handoff or model/Gateway call in AA, and
the standard existing CI jobs remain under their ORIGINAL default
scope.  The ONE canonical future sealed entry `017-ab` (driver
record `slaif-017ab-owner-uid-exec-capability-v1`, selecting ONLY
`slaif-fixture-identity-owner-uid-v1`) is fixed now but INACTIVE:
AA never creates, activates, admits or launches it, and actual
repository-context validation refuses the entry under AA-active
state before any external fixture work or admission.  When
activated by its own later order: the sealed child keeps sole
resolve+admit ownership; the real owner then collects and freezes
its OWN eligible host IDs (real/effective/saved UID and GID
triples through the Z production collector — each triple equal,
nonroot, 1..4294967294, distinct from controller 21001) after its
ORIGINAL verified order/run wins admission; a post-admission
collection/constructor failure closes the SAME won attempt (no
journal reconstruction, re-mint or re-resolution, and no process
may be started merely to collect host IDs); the ONE immutable
owner context (canonical profile description/fingerprint plus
ORIGINAL verified order/head/run/admission binding) is revalidated
at actual use — compared, never rebased or re-frozen after drift,
and a caller-supplied description/fingerprint/ready flag never
establishes measured origin.  The frozen profile carries through
the owner-profile Dockerfile variant (frozen validated IDs only;
same pinned base, immutable artifact/LICENSE/NOTICE and
confinement; root-owned immutable profile DATA that fails closed
and is never selected from env-var or file presence; original
defaults fixed-21002 unchanged), build arguments, subject
tmpfs/home/workspace ownership, the owner-scoped guarded executor
(the canonical profile's exact INDEPENDENT UID:GID and fixed
Python commands — original guard defaults unchanged), controller
subject accounting, stand-in measurements/PTY, host exact-CID
discovery/frame checks, and the DISTINCT versioned AB records
(`slaif-017ab-owner-state-v1` identity-bearing owner state — the
old 12-key v1 state form is byte-for-byte unchanged and rejects
identity-bearing records; `slaif-017ab-owner-run-evidence-v1`
with the frozen identity substructure and the
exact-CID-membership teardown marker; the AB driver record;
the subject measurement/profile records on the DISTINCT tags
`slaif-fixture-exec-measurement-v2`/`slaif-fixture-profile-v2`
over the shared profile-independent structural core with its
unchanged closed meaning, the strict original identity-v1
wrappers keeping the fixed-21002 law) — the ORIGINAL
identity-bearing v1 tags/consumers stay strictly
fixed-21002 and measured 1001-class facts are never
normalized to 21002; the generic profile-independent
standin/control transport v1 is retained only where its
existing closed meaning is unchanged (no wire-tag
renaming).  Expected
effective groups are exactly the primary GID, never host
supplementary groups.  The owner-UID cleanup proof is exact
registered-CID plus owned PID/birth lifetime membership with
tri-stated post-removal verification: the original global
controller/subject UID teardown scans are NEVER substituted with
the host owner's UID (no UID-only membership or zero-global-UID
claim), and unknown or unreadable still-existing entries stay
unverified.  A post-admission startup refusal (control-root
creation or bounded socket bind) routes through the SAME single
owner convergence as every terminal path: the already-won attempt
closes terminal honestly, the owned partial control root is
disposed through the same exact-ownership law, a pre-existing
foreign control root is never adopted or deleted, and the thin
CLI keeps the same closed startup record and exit code.  The
original S/X/Y entries, sealed pairs, defaults and consumed
namespaces are unchanged.  The detailed normative fixture contract is in section 11j
of `docs/CACHE-OBSERVATION-CONTRACT.md`; the test narration
is in the stage ledger row for 017 and the TESTING.md round
sections.  D09 remains `NOT RUN`; no
native-ready or v1 runtime claim.

Round 017-ab activates that sealed entry and executes
the ONE bounded actual PYTHON-only owner-UID capability
qualification on the same PR25 (no source change — at
the literal attempt head
`cdb6a101ecbd6d687f8ad413b9505c7198000758`, run
`87ee9c006d7f4de98d11af2dfbe5bd5c`, all 17 helper
bytes, the runtime source, the 199-input map and both
artifacts verified identical to qualified AA, and all 10
CI checks green at that head; the existing public
driver ran EXACTLY ONCE, Python-only, over the real
local Docker endpoint): a closed driver PASS in which
the sealed child won the ONE admission; the real owner
collected and froze its OWN eligible host identity
(subject UID/GID 1001/1001, expected groups exactly the
primary GID `[1001]` — measured values, never a caller
flag); the preparation, confinement and Python-PTY
phases completed under unchanged confinement
(controller 21001/21001; 1 GiB/no swap; 1 CPU; pids 96;
empirical keyring denial EPERM under the matching host
UID); the ONE capability-hold subject was uniquely
identified from the exact-CID inventory (pid/birth-
bound, closed argv; pre/post inventory 1/2 rows) and
its current executable was MEASURED through the
existing unprivileged scoped CID channel (sha256
`4dbf3143240288fb2170257ffaa7bd030cdda5d2703d1f5f30b627042267e2e3`
— the first measured executable for this entry class,
distinct from the X null and the Y unknown); the subject
was then observed `verified-gone` after the bounded
hold (absence only — never an exit code, signal, errno,
kernel cause or natural-exit provenance); the exact-CID
cleanup converged (descendants 1 before / 0 after;
container and owned image verified absent; the unrelated
same-UID worker and host sentinel survived); and the
publication ordering held (verified owner evidence
first, driver record second, same-attempt terminal
finalization last — ONE terminal-pass journal entry;
owner exit 0; driver exit 0). The pinned native
artifact was fetched, hashed and baked but NEVER
executed. This is a bounded Python-only diagnostic
capability qualification on the owner-UID profile — NOT
native-ready, NOT whole-017 acceptance, NOT v1 runtime
delivery; full-017
native/current-binary/format/PTY, D09, the required-
syntax audit and ALL 018-024 remain mandatory. The
admission is terminal pass and is never reset, retried
or relabeled; the measured outcome is recorded in the
immutable round report. D09 remains `NOT RUN`; no
native-ready or v1 runtime claim.

objectives 018–024 remain the planned inert draft succession for the v1
implementation stages (see `docs/CACHE-REWORK-LEDGER.md`). The original
planned meanings of numeric 006-008 are historical planning prose, not live
identifiers. Strategy may revise only from verified evidence. One numeric
objective=one PR; coding never merges.

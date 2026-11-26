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
configuration errors, not silent fallbacks. Since 022-a the profile is
selected by the explicit `[context_cache]` configuration: omission or
explicit `legacy` keeps the legacy behavior; `dependency-bundles-v1` is
accepted only with its closed typed configuration (explicit effective-
context budget, bounded compiler policy, explicit RAM ownership bounds,
strict one worker, admission defaulting to `lean`, the explicit protected-
recovery opt-in with configured root, and each governed route's explicit
model contract bound to the pinned tokenizer/render capability and the
configured effective C). The 022-c application
wiring removed the 022-a startup refusal: a valid
selected v1 profile activates the v1 runtime on
opted-in governed routes at the `create_app`
entry point (at its bounded fake-upstream
application scope through the 022-d closure
slice, MERGED to main through PR #30 at
4319049d91428b8995e83db82b1736ed36626a12), while a fixed
startup capability error (`V1RuntimeUnavailableError`)
still refuses before any HTTP client, legacy cache
or recovery owner construction when the
operator-prepared recovery root is missing or
the protected marker-key reference cannot be
resolved within its closed bound; a settings
model alone establishes no v1 readiness, source
replacement, native-format, streaming or recovery
qualification. Legacy remains usable through its
existing entry points. The profile is independent
of
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

V1 commit order (normative target; implemented at the
bounded 022-c/022-d application scope on opted-in
governed routes):

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

Current inert scope: the accepted 017 observation package (D01-D10 at
their bounded scopes; observation contract
`docs/CACHE-OBSERVATION-CONTRACT.md`), the accepted 018-a graph-
foundation slice (contract `docs/CACHE-GRAPH-CONTRACT.md`) and the
accepted 018-b bundle-proof bridge slice (contract
`docs/CACHE-BUNDLE-PROOF-CONTRACT.md`), plus the implemented 018-c
bundle-admission and structural-identity slice ACCEPTED at its
bounded inert scope with process qualifications (contract
`docs/CACHE-BUNDLE-ADMISSION-CONTRACT.md`), the implemented
018-d causal-occurrence-ledger slice ACCEPTED at its bounded inert
causal-occurrence-ledger scope with process qualifications
(contract `docs/CACHE-CAUSAL-HISTORY-CONTRACT.md`) and the
implemented 018-e nonroot currentness-overlay slice ACCEPTED
at its bounded inert currentness/overlap-overlay scope with
process qualifications (strategic decision
`S/reviews/018-e-decision.md` + addendum; contract
`docs/CACHE-CURRENTNESS-CONTRACT.md`), plus the implemented 018-f
current-graph-closure slice ACCEPTED at its bounded inert
current-graph scope with process qualifications (strategic decision
`S/reviews/018-f-decision.md`; contract
`docs/CACHE-CURRENT-GRAPH-CONTRACT.md`), plus the implemented 018-g
current-bundle-admission slice ACCEPTED at its bounded inert scope
with process qualifications (strategic decision
`S/reviews/018-g-decision.md`; contract
`docs/CACHE-CURRENT-ADMISSION-CONTRACT.md`), the implemented
018-h root-authority-lineage slice ACCEPTED at its bounded inert
root-authority-lineage scope with process qualifications
(strategic decision `S/reviews/018-h-decision.md`; contract
`docs/CACHE-ROOT-LINEAGE-CONTRACT.md`) and the implemented 018-i
current-root-composition slice NOT ACCEPTED (strategic decision
`S/reviews/018-i-decision.md`); the bounded 018-j repairs (J01
association closure, J02 exact reverse-index law, J03 independent
budget domains) were delivered truthfully PARTIAL and are NOT
ACCEPTED against the complete J01/J02/J03 criteria (strategic
decision `S/reviews/018-j-decision.md`); the bounded 018-k
repairs (K01 actual nested canonical keys at BOTH parent
boundaries, K02 actual nested row shapes before exact-relation
comparison, K03 genuinely reachable E collection caps with exact
evidence labels) are NOT ACCEPTED against the complete
K01/K02/K03 criteria (strategic decision
`S/reviews/018-k-decision.md`); the bounded 018-l repairs (L01
complete closed nested entry / key-record / ownership metadata
fences at the leaf and BOTH parent boundaries with the entry /
record authority and width joins, L02 independently derived
actual E collection-domain counts with a before-target charge
sentinel) were delivered truthfully PARTIAL and are NOT
ACCEPTED against the complete L01/resource/artifact criteria
(strategic decision `S/reviews/018-l-decision.md`); the bounded
018-m repairs (M01 O(1) count / scalar gates BEFORE any element
/ set / sort / hash / serialization work at the leaf and BOTH
parent boundaries, with the closed TEN admission bound-model
fence and the accepted dense group ordering / unique partition
law; M02 the exact accepted JSON serialization byte ceiling and
the reservation-calculation work precharge on the ONE I outer)
were delivered truthfully PARTIAL and are NOT
ACCEPTED against the complete M01/M02 criteria (strategic
decision `S/reviews/018-m-decision.md`); the bounded 018-n
repairs (N01 the retained-content join at the leaf and BOTH
parent boundaries — the entry-local group partition joined to
the ORIGINAL proof segments and the root group to the retained
root digest — plus N02 the byte-aware closed reservation, the
pre-fetch plan segment precharge and the per-site
reservation-calculation closure) are ACCEPTED at their
bounded inert scope WITH PROCESS QUALIFICATIONS
(strategic decision `S/reviews/018-n-decision.md`); the 018-o
root-aware mixed-observation slice (the new pure
`observe_root_lineage_mixed` operation plus
`ROOT_LINEAGE_MIXED_OBSERVATION_VERSION`; a proven mixed root
member matching an independently authoritative known version
of the same effective root — including an independently
issued complete whole singleton in the SAME batch — acquires
source evidence while a mixed read mints no governing
authority, unresolved foreign digests keep the exact
COMPETING_ROOTS refusal, and the pending-set snapshot is
precharged on the SAME H outer) is implemented and
ACCEPTED at its bounded inert scope WITH PROCESS
QUALIFICATIONS (strategic decision
`S/reviews/018-o-decision.md`; root-lineage contract
section 5a); the 018-p versioned root-region authority
producer (the separate `cache-root-region-lineage/v1`/
`root-region-lineage-policy/v1` contract and the
`read_region` provenance kind: a genuinely issued
complete NEW root region in a mixed-only read acquires
source evidence AND authority with NO independent
singleton, the no-exception read shapes, before-
materialization retention under the unchanged H
ceilings, the ONE new-operation outer, the honest old-I
refusal of the region-version state and the closed host-IO
purity surface) is ACCEPTED at its bounded inert producer
scope WITH PROCESS QUALIFICATIONS (strategic decision
`S/reviews/018-p-decision.md`; root-region contract
`docs/CACHE-ROOT-REGION-LINEAGE-CONTRACT.md`); the
018-q versioned root-region currentness slice (a pure
QUERY over the 018-p state — contract
`docs/CACHE-ROOT-REGION-CURRENTNESS-CONTRACT.md`) is
ACCEPTED at its bounded inert query scope WITH PROCESS
QUALIFICATIONS AND HISTORICAL-REPORT CORRECTIONS
(strategic decision `S/reviews/018-q-decision.md`), and
the 018-r consumer slice (contract
`docs/CACHE-ROOT-REGION-GRAPH-CONTRACT.md`) is ACCEPTED at its bounded inert selected-root source/current-graph scope WITH PROCESS QUALIFICATIONS AND EXPLICIT HISTORICAL-REPORT CORRECTIONS (strategic decision `S/reviews/018-r-decision.md`); the 018-s region-compatible admission-models slice (contract `docs/CACHE-ROOT-REGION-ADMISSION-MODELS-CONTRACT.md`) is ACCEPTED at its bounded inert MODEL/LOCAL-BOUNDARY scope WITH PROCESS QUALIFICATIONS AND EXPLICIT HISTORICAL-REPORT CORRECTIONS (strategic decision `S/reviews/018-s-decision.md`); the 018-t complete root-region admission consumer (contract `docs/CACHE-ROOT-REGION-ADMISSION-CONTRACT.md`) is ACCEPTED at its bounded complete-consumer scope WITH PROCESS QUALIFICATIONS AND EXPLICIT IMMUTABLE-REPORT CORRECTIONS (strategic decision `S/reviews/018-t-decision.md`), and the 019-a bounded RAM owner and atomic state storage slice (contract `docs/CACHE-RAM-STATE-CONTRACT.md`) is ACCEPTED at its bounded inert RAM owner/store scope WITH PROCESS QUALIFICATIONS AND IMMUTABLE-REPORT CORRECTIONS (strategic decision `S/reviews/019-a-decision.md`), the 019-b bounded async single-flight work plane (contract `docs/CACHE-RAM-WORK-CONTRACT.md`) is delivered and NOT ACCEPTED against the complete accounting requirement or whole 019 (strategic decision `S/reviews/019-b-decision.md`), and the 019-c whole-019 closure round (the bounded pre-accounted `owner_quarantined` adverse-currentness fence, aggregate pressure with high-water shared-container retention, substantial-source/accumulated-history over ACTUAL accepted records, cancellation/update/teardown races and the denied-filesystem lifecycle proof; `tests/test_bundle_ram_lifecycle.py`) is implemented at the INERT injected-work layer and PENDING strategic review, all as typed modules under
`src/slaif_local_coding/constitution/bundles/`; the 022-c/022-d
application wiring activates these components on opted-in
governed v1 routes (at its bounded fake-upstream
application scope, MERGED to main through PR #30 at
4319049d91428b8995e83db82b1736ed36626a12) while the
legacy detector and the ungoverned-route path stay
unchanged; the remaining statements below
(compilation, RAM ownership, replacement, recovery,
budgets) are the approved target contract.

**Causal-occurrence ledger (018-d inert, ACCEPTED at its bounded scope).**
The 018-d kernel keeps three identities distinct: the semantic
source/content key (the accepted 018-c structural key), the
completed read occurrence (one retained verbatim original proof
with its FIRST original provenance) and the local revision (a
CAS/serialization fence, never a clock). The frozen SPECIFIC-
request trusted issuance frontiers supply partial-order evidence
only: only actual frozen parent evidence establishes temporal
edges; receipt arrival, new call IDs, HTTP/arrival positions,
equal or different digests, lexical order and registration or
revision numbers never establish source freshness, and no new
clock or ordering source is introduced. Original complete but
unissued history is retained UNANCHORED and adds NO temporal edge
by itself: a known completed unanchored fact may later be named as
a trusted frontier parent and is then BEFORE its descendant (even
before its own late receipt), the same known completed ID is SAME,
distinct known UNCONNECTED events are INCOMPARABLE, and unknown
or incomplete IDs are UNKNOWN (never a SAME shortcut); later
trusted facts, never arrival order, establish edges. A
deliberately new version after an older one needs a genuinely new
completed occurrence with a valid descendant issuance. A native
multi-piece read takes the INITIAL EXEC issuance frontier, and
the native poll's producing call/result stays bound to the
ORIGINAL initial-EXEC owner even when every binding/body/status/
session fact is identical (no session-number clock). The exact
scope, the 14 history bounds with one shared per-transition work
ledger, and the `causal-arguments-json/v1` recipe are versioned in
`docs/CACHE-CAUSAL-HISTORY-CONTRACT.md`; the stage stays inert
and inactive.

**Nonroot currentness overlay (018-e inert, ACCEPTED at its bounded scope).**
The 018-e derivation takes an ACTUAL retained 018-d causal-history
state and its ACTUAL namespace (plus explicit currentness bounds)
and, in ONE pure bounded charged operation, derives which NONROOT
source facts and ownership groups are CURRENT_KNOWN, CURRENT_OPAQUE,
STALE, CONTENT_CONFLICT or OWNERSHIP_AMBIGUITY, with the full
reverse path index: the semantic content key, the retained
occurrence and the local revision stay distinct (the overlay is a
fourth derived identity, never conflated with any of them);
chronology comes only from actual frozen parent edges (frozen
frontiers are partial-order evidence, never a clock; no new clock or
ordering source); an unissued observation adds no edge of its own
(a later trusted child may name it a parent); the versioned
opaque-group recipe binds the group-local semantic ownership shape
plus bound version identities, never principal/session keys; the
six currentness bounds run on one shared per-derivation work ledger
with pre-copy refusals. The exact scope is versioned in
`docs/CACHE-CURRENTNESS-CONTRACT.md`; it earns the C04/C05
currentness/overlap MECHANISM at its bounded scope only and the
stage stays inert and inactive.

**Current graph closure (018-f inert, ACCEPTED at its bounded scope).**
The 018-f derivation takes an ACTUAL 018-d causal-history state
and its ACTUAL namespace (plus explicit current-graph and 018-e
currentness bounds) and, in ONE pure bounded charged operation,
derives the current graph: current source suppliers are selected
BEFORE any scanning from the ACTUAL 018-e per-owned-group
currentness (a blocked opaque group is indivisible and supplies
nothing; a root-bearing group can never supply root text), the
fresh root least fixed point is built from the immutable
RootAnchor only (never seeded from previous eligibility/depth/
edges), version-owned ordinary edges and group certificates carry
owner/witness provenance (removing an owner removes only its own
derivation; a surviving complete alternate keeps the target),
honest per-node availability retains unreachable possession
(`CURRENT_KNOWN`/`CURRENT_EMPTY`/`DISCOVERED_UNACQUIRED`/
`BLOCKED_CONFLICT`/`BLOCKED_AMBIGUITY`), the least complete AND/OR
depth is recomputed after withdrawals and the effective max_depth
is enforced after the fixed point, and the RootAnchor's actual
field shapes and spans are freshly validated under charged source
preflights (never `model_validate` of an existing instance alone).
The 15-field scope key binds the actual validated history
namespace/workspace, the actual root digest, the inherited
graph/reference/proof/currentness versions, all effective bounds
and the NEW versioned current-graph contract/policy; the two new
per-derivation current-graph bounds (outer total work,
diagnostics) run under the ONE shared outer ledger, and
graph-owned collections use charged stable merges (linear
reservations before, every actual comparison and element write
charged). The exact scope is versioned in
`docs/CACHE-CURRENT-GRAPH-CONTRACT.md`; it earns the C04/C05
current graph MECHANISM at its bounded scope only and the stage
stays inert and inactive.

**Current bundle admission (018-g inert, ACCEPTED at its bounded
scope).**
The 018-g derivation takes the ACTUAL retained 018-d state and
namespace (plus the NEW current-admission bounds and the ACTUAL
supplied 018-e/018-f derivation bounds) and, in ONE pure bounded
charged operation, derives the accepted 018-f current graph in the
SAME run AND the current admission entries with the canonical 018-c
semantic keys: the root entry always retains the actual RootAnchor
typed fields (no invented kind/status/envelope; the exact EMPTY
root legal), the per-owned-group currentness truth table excludes
stale, conflicting, ambiguous and root-bearing opaque groups
BEFORE entry planning (no greedy isolation rule; lean admits only
independently CURRENT all-eligible segments; a genuine descendant
singleton conservatively stales an opaque group even when the bytes
equal the old aggregate), entries are interned by distinct content
key retaining the FIRST compatible original proof by identity and
ALL distinct original same-content-compatible witness coordinates
(canonical full-coordinate order, never acquisition order), the
complete reverse member index maps every represented member path to
ALL admitted content keys (attempts charged before dedup), and the
emitted admission reasons are RETAINED as the actual bounded
sorted/deduplicated tuple with the emitted count bound to its
length under BOTH the new and the inherited admission caps in the
same domain (a normal derivation emits at most ONE fixed
candidate_unproven; the public first-over of the diagnostics caps
is unreachable and is closed only by constructor-level controls;
018-f graph diagnostics stay F output by reference). The NEW
per-derivation current-admission bound sets (total work 1048576,
cumulative entry-source bytes 16777216, diagnostics 64) run on ONE
shared outer ledger with the ACTUAL supplied F-subtree ceiling
enforced independently on the same outer (the essential positive:
F cap exactly F's cost, G total above it, full G succeeds); the
stage-level admission work runs under the ACTUAL inherited
GraphBounds work ceiling on the G admission stage; the 28-field
scope key is recomputed from the actual fields on every
construction (derivation-only bound changes bind the new scope key
but NOT the semantic key records). The exact scope is versioned in
`docs/CACHE-CURRENT-ADMISSION-CONTRACT.md`; it earns the whole-018
current-version admission MECHANISM at its bounded scope only and
the stage stays inert and inactive.

**Root-authority lineage (018-h inert, ACCEPTED at its bounded scope).**
The 018-h composition takes the ACTUAL retained 018-d causal-
history state and its ACTUAL namespace (derived into the NEW
versioned root-lineage namespace; the NEW root-lineage bounds on
ONE shared per-operation outer) and, in pure bounded charged
operations, earns genuine supported versions of the SAME effective
root: the bootstrap remains the accepted legitimate effective
Responses AGENTS envelope with exact source bytes, workspace and
first original spans (the exact EMPTY root legal; rootless empty
state cannot bootstrap); a REFRESH SOURCE must be an ACTUAL
accepted complete whole singleton read of the EXACT normalized
root path (one member occurrence, one attributable proven region
covering the complete source; opaque/mixed/repeated/partial/
truncated/nonzero/unsupported reads grant nothing) on EITHER read
endpoint; SOURCE acquisition and AUTHORITY are separate (a
matching INTERNAL trusted issuance/receipt with proven frozen
causal ancestry to the bootstrap root fact; read ID novelty,
receipt arrival, digests, revisions and body flags are never
clocks or trust; the DERIVED issued/authority flags are re-
derived for ALL facts after every accepted D transition, stored
bits never trusted); complete but unissued root reads are
retained as UNPROVEN source, never selected (fixed
ROOT_SOURCE_UNPROVEN limitation); known same-scope root envelopes
are context evidence only (replays are no-ops, no rollback), an
unknown changed envelope without independent same-batch accepted
root-read authority refuses the whole transition with the exact
prior state, and the selected current root is a DISTINCT derived
causal-maximal source fact (causal dominance over frozen parents
only; equal incomparable maximal witnesses ALL retained,
differing maximal sources an explicit ROOT_CONTENT_CONFLICT with
no selected source; a child of one branch cannot causally
dominate the other (equal-byte surviving maximal sources can be
compatible), a genuine child of ALL can; delayed older receipts
never override proven descendants). The original RootAnchor, every
historical proof binding and occurrence ID are preserved by
identity (retained by bounded immutable reference, never copied
per witness); the H state wraps the actual D state (no nested
revalidation) and is NOT authority to pass a forged D state to
public F/G; an H-PRIVATE charged coherence check retains the
accepted builder invariant (every piece producer binding derives
from the SAME original request endpoint, and every completed
occurrence joins its complete owning result record which retains
the exact piece-producer association of the retained proof --
missing/rewritten ownership is refused, the retained proof alone
cannot re-prove it) without changing the old public D
observed-binding law. The NEW bounds (root facts 1024,
retained root source bytes 16777216, total work 1048576 PER
operation, diagnostics 64 PER result; stricter positives allowed)
run on ONE outer per operation coupled to the ACTUAL D work (D-
local domains stay independent; no global min, no resets; the
original-batch max_requests domain preserved). The exact scope is
versioned in `docs/CACHE-ROOT-LINEAGE-CONTRACT.md`; it earns the
explicit same-root refresh/authority-lineage MECHANISM at its
bounded inert scope only (ACCEPTED at its bounded scope with
process qualifications, strategic decision
`S/reviews/018-h-decision.md`), and the stage stays inert and
inactive. The separate 018-p root-region authority
producer (the NEW `read_region` provenance kind under the
NEW `cache-root-region-lineage/v1` contract, documented in
`docs/CACHE-ROOT-REGION-LINEAGE-CONTRACT.md`) is the
mixed-only changed-root acquisition half of this mechanism:
a genuinely issued complete NEW
root region inside an ordinary mixed read (EXACTLY ONE
normalized root occurrence across ALL requested operands
and one proven attributable region) acquires source
evidence AND authority with NO independent singleton (an
unknown mixed root needs none in that NEW contract);
repeated/opaque/partial/truncated/nonzero/unpaired/
unsupported reads gain no exception; fact-count and
root-member-byte retention is preflighted BEFORE
materialization under the unchanged H ceilings; ONE
new-operation outer at the unchanged RootLineageBounds
couples the actual D work with independent inherited
domains; the old H/O law is unchanged and the existing
old I honestly refuses the region-version state; a
genuinely new authoritative region occurrence carrying
old bytes after a later version is a deliberate revert
under the same frozen partial order; the next same-018
consumer round must consume the legitimate new state
into the actual graph/admission. It is ACCEPTED at its
bounded inert producer scope WITH PROCESS QUALIFICATIONS
(strategic decision `S/reviews/018-p-decision.md`;
`tests/test_root_region_lineage.py`).

**Root-region currentness (018-q inert, ACCEPTED at its
bounded scope WITH PROCESS QUALIFICATIONS AND
HISTORICAL-REPORT CORRECTIONS, strategic decision
`S/reviews/018-q-decision.md`).**
The 018-q derivation takes the ACTUAL retained 018-p
root-region lineage state and its ACTUAL namespace (plus
the NEW currentness bounds) and, in ONE pure bounded
charged operation, derives whether the known
authoritative root is CURRENTLY usable: it refuses to
treat a known authoritative root as currently usable
after a trusted complete root-bearing observation whose
governing root cannot be established under P source
policy. It mints no new root authority, changes no P
selection law, never advances a revision, and carries no
CAS input, clock or new persistent state. The COMBINED
evidence frontier (the actual authoritative P facts plus
the eligible uncertainty occurrences on the SAME actual D
state) uses edges from ACTUAL original frozen parent
evidence only: arrival, registration, call-ID, HTTP
position, revision and content equality never add
edges, and all equal/incomparable maximal originals are
retained in canonical deterministic metadata order. An
unresolved MAXIMAL trusted root uncertainty (later or
incomparable to the known root) is what blocks usability;
dominated historical uncertainty is retained as a witness
on the ready result and never permanently blocks. A
maximal uncertainty observation after or incomparable
with a known root makes the known authority unusable
(fixed `root_currentness_unproven`, no selected usable
source, no ready graph/admission and no bootstrap
fallback); a known authoritative differing-root
conflict remains non-ready as
`root_authority_conflict`; readiness follows the
COMBINED maximal frontier, so a single proven
descendant-of-all is SUFFICIENT but NOT required
(compatible known maxima that JOINTLY cover the branches
restore readiness with all original maxima, without
invented edges). A genuinely NEW supported whole/region
root occurrence descended from ALL unresolved maximal
branches restores readiness under ordinary P law; a
child-of-one cannot erase another branch; a deliberately
new old-bytes descendant may restore that version;
historical replay and delayed receipts never roll back
or cause permanent poisoning. The closed evidence/
exclusion table (a qualifying complete root-bearing
opaque group and a P-unsupported root shape are
uncertainty evidence with every unknown per-file hash
staying unknown; unissued/unanchored observations
contribute nothing, a later genuine issuance/receipt
qualifies the SAME original retained occurrence, and
issuance alone does not anchor; unsupported, unpaired,
missing, incomplete, pending, truncated or nonzero
observations gain no new exception; wrong
path/workspace and nonroot-only groups are never root
uncertainty; requesting a root path alone cannot poison
currentness) plus the result law are versioned in
`docs/CACHE-ROOT-REGION-CURRENTNESS-CONTRACT.md`: the
result retains the EXACT input P state by reference on
EVERY outcome with its actual revision and lineage key,
retains the ACTUAL same-run P selection (or the exact
P validation problem when validation refused before
selection), and the stable scope key binds the actual P
lineage key, the Q contract/policy and the actual Q
bounds — NOT the carried revision. The ONE Q outer
covers the ENTIRE operation while the ACTUAL P phase
retains its INDEPENDENT root-lineage work ceiling
(coupled unit-for-unit into the Q total; the D/B-local
domains stay independent; no global min, no reset);
closed O(1) collection/scalar gates precede any
iteration/set/sort/serialization, every candidate
attempt counts before dedup, and source preflights
precede any owned slice/encode/hash/copy without a
per-witness source walk. The 018-q bounds (total work
1048576, diagnostics 64; default AND hard, stricter
positives legal) run on that ONE outer, and the
inherited D collection law stays distinct beneath it.
It closes nothing end to end: the same-018 CONSUMER
round must consume the legitimate new region state into
the actual graph/admission, and whole 018 (plus 019-024)
remains open and mandatory. It is ACCEPTED at its bounded inert query scope WITH
PROCESS QUALIFICATIONS AND HISTORICAL-REPORT CORRECTIONS
(strategic decision `S/reviews/018-q-decision.md`,
preserving every recorded qualification and correction;
`tests/test_root_region_currentness.py`); the stage
stays inert and inactive.

**Root-region selected source and current graph (018-r inert,
ACCEPTED at its bounded inert selected-root
source/current-graph scope WITH PROCESS QUALIFICATIONS
AND EXPLICIT HISTORICAL-REPORT CORRECTIONS, strategic
decision `S/reviews/018-r-decision.md`).**
The separately versioned
`cache-root-region-graph/v1` /
`root-region-graph-policy/v1` operation
`derive_root_region_graph` takes the ACTUAL retained P
root-region lineage state and namespace, derives ACTUAL Q
currentness in the SAME charged run, resolves the usable
selected root source, and derives the ACTUAL accepted F/E
current graph under that selected root. It never takes a
caller-positive Q/F snapshot, converts P state into old H
state, manufactures a singleton or RootAnchor, advances a
revision, adds authority, or creates persistent state.
READY means only actual Q READY, resolved selected source
and actual F graph success. It does not mean acquired
required dependencies, admitted entries, compiled content,
cache readiness, HTTP readiness or v1 runtime readiness.
The contract is
`docs/CACHE-ROOT-REGION-GRAPH-CONTRACT.md`.

Source dispatch is explicit for actual envelope, whole
`read`, and `read_region` provenance. Envelope text comes
only from the actual immutable D RootAnchor when that fact
is selected. A whole read keeps its actual complete
singleton proof. A region joins the selected fact,
occurrence, complete owning result, each original piece
producer, whole-proof binding, segment/member coordinates
and root-member digest/byte length to the SAME original
retained P/D objects. Keep every compatible maximal
original witness through the actual Q/P selection;
materialize only the deterministic first compatible root
body, without a full source walk for each witness. Preserve
original-reference identity where promised; value equality
is not an original association proof. A pure value-equal
valid input is not rejected merely because its top-level
bound object was copied.

`BundleProof.source_text` concatenates SOURCE segments in
order with proven printed marker lines excluded. The
selected region begins at the sum of the preceding
original segment CHARACTER lengths. Carrier piece spans
and UTF-8 byte offsets are not offsets into that
aggregate. Preflight original index, member ownership,
character width and bounded UTF-8 length before an owned
slice, encode, hash or copy. Keep Unicode, CRLF and the
exact empty root. Whole-proof digest/length and selected
root-member digest/length are distinct; original
`proof.root_digest` stays bound to immutable bootstrap
scope even when the selected governing root is newer.
Never rewrite the original proof or anchor to make a join
pass.

Q unproven, authority-conflict and refusal outcomes map
BEFORE selected-source copying or F derivation, with no
usable source/graph and no bootstrap fallback. Derive a
FRESH F least fixed point under the selected root digest,
using that selected root as the only root-text supplier
and the ACTUAL E nonroot currentness/ownership law. Stale,
conflicting or ambiguous groups supply nothing; a
root-bearing opaque group never supplies root text.
Withdraw only the removed version owner's ordinary
edges/certificates, retain surviving complete alternate
suppliers, remove unsupported cycle-only reachability,
retain honest unreachable possession, and recompute least
AND/OR depths and the effective max_depth. Unknown
reference origin remains unknown; greedy co-caching alone
never promotes reachability or authority.

ONE R outer covers the entire derivation: early
scope/bound reservations, actual Q/P/D/B work,
original-source resolution, actual F/E and graph-stage
work, and association/serialization/construction
reservations. The R bounds are total work1048576 and own
diagnostics64, DEFAULT AND HARD, with stricter positive
values legal. They are per-operation domains, not
retained-source, RAM/RSS or token budgets. Each actual
inherited Q/P/D/B/E/F/GraphBounds domain remains
independently binding under that total; couple actual
units through the narrow private kernels, with no global
minimum, cap-sized fake reservation, reset or second
unmetered public derivation. Count candidate attempts
before deduplication. Closed O(1) count/scalar/class/
version gates precede element/set/sort/hash/serializer
work, and precharge real metadata walks, snapshots,
membership widths, reservation calculations, owned content
passes and constructors before work. R-owned
character/byte content reservations do not reinterpret
the accepted F operation counters or its separate
source-byte/stage domains. Original-batch limits stay
distinct from cumulative retention. Constructor checks
enforce closed local shape, scope and associations; they
do not hide an uncharged full original proof/history
traversal.

Every returned R result retains the EXACT input P state
by reference with its actual carried revision and lineage
key. The stable R scope binds the actual P lineage
identity, R/Q/F/E versions, actual graph version and
every effective R/Q/F/E bound; revision is separate.
Keep actual same-run Q once returned, and actual F
result/E overlay only when those intermediates were
actually returned. Never rerun E to populate evidence or
fabricate an unreturned intermediate after an R-total
crossing. Refusals publish no R-ready selected-source/
graph output; already returned nested evidence stays
truthful. In particular, an R-total crossing after F
completed may retain that ACTUAL F OK result as evidence
while R remains REFUSED and exposes no usable resolved
source.
P/Q/F refusal reasons stay in their actual channels,
rather than being invented as R-own diagnostics. Fixed
private repr/errors and the closed host-IO purity law
apply to public ready, non-ready and refusal paths.
Original payload-data serialization is preserved; pure
equality is not HTTP wire proof.

The API remains inert and inactive in adapter execution. The separate same018 admission/full-result consumer (018-t) is now ACCEPTED at its bounded complete-consumer scope (strategic decision `S/reviews/018-t-decision.md`); stages 019-024 remain mandatory. R graph/source-scale results
cannot replace the later complete admission consumer's
own substantial-source and whole-operation resource
evidence. Preserve old H/O/I/P/Q public schemas,
defaults, versions, recipes and supported boundaries,
including honest old-I refusal of region-version state
and all earlier NOT ACCEPTED/PARTIAL decisions.

**Root-region admission models (018-s inert, ACCEPTED at its bounded MODEL/LOCAL-BOUNDARY scope WITH PROCESS QUALIFICATIONS AND EXPLICIT HISTORICAL-REPORT CORRECTIONS, strategic decision `S/reviews/018-s-decision.md`).**
The separately versioned
`cache-root-region-admission-models/v1` /
`root-region-admission-models-policy/v1` slice (contract
`docs/CACHE-ROOT-REGION-ADMISSION-MODELS-CONTRACT.md`;
`tests/test_root_region_admission_models.py`) is a
MODEL/LOCAL-BOUNDARY data-model and local-boundary slice ABOVE the
accepted 018-p state and the ACCEPTED 018-r result as COMPONENT DATA:
the region-compatible `RootRegionAdmissionEntry` data model is
constructor-compatible with the ACTUAL G `_assemble_file_entries`
typed generic FILE entry field set (the ROOT row additionally carries
the ACTUAL `ResolvedRootRegionSource` by immutable reference with its
explicit envelope/read/read_region provenance; one root body by
reference, no owned copy; the FILE rows keep the FIRST compatible
original `BundleProof` by reference, their ORIGINAL admitted segment
indices and ALL distinct original witness coordinates in canonical
order); the `RootRegionAdmission` admission-parent data model carries
the ACTUAL P input state, the ACTUAL P namespace and the ACTUAL R
result by immutable `InstanceOf` references, the ACTUAL unchanged G
`CurrentAdmissionBounds`, the mandatory root entry, the FILE entries,
the complete path associations and the bounded reason/count/resource
metadata. The UNCHANGED canonical 018-c `BundleKeyRecord` /
`_canonical_entry_key` recipe re-derives the actual namespace/key
context at the leaf and the admission parent (the FULL-RESULT third
parent is explicitly deferred, not claimed); the complete reverse
member index law is rechecked at the admission parent; the ELEVEN
carried bound sets (the P namespace six, the R result four and the
actual G `CurrentAdmissionBounds`) are fenced at their expected
original classes and hard ranges under the closed O(1) count/scalar/
class/shape gates BEFORE any element/set/sort/hash/serializer walk,
with fixed private errors for unknown/malformed copies. The NEW
versioned local before-work validation-reservation helpers
(`root-region-admission-precharge/v1`: the region, root-content,
canonical-metadata, parent-namespace and admission-parent components)
are component precharge contracts for the later whole operation: a
real helper calls the typed bounded CALLER-SUPPLIED meter BEFORE
actual calculation/measurement/allocation/hash/constructor targets,
every real repeated pass is charged, the whole-bundle fast path
charges ZERO slice/join work where the partition closure proves the
joined region IS the source, the inherited source-size caps stay the
actual UTF-8 SOURCE SIZE domains (never a work bound), and NO
unlimited or default meter exists. It is MODEL/LOCAL-BOUNDARY ONLY:
no public derive function, no operation result/outcome, no persistent
owner/namespace, no new whole-operation bound set, no runtime wiring,
and retaining the actual R result by reference is component data, NOT
derivation authority; the 018-t complete root-region admission consumer (contract `docs/CACHE-ROOT-REGION-ADMISSION-CONTRACT.md`) derives ACTUAL R from ACTUAL P in its own entire charged operation and independently earns its own source-scale and whole-operation evidence, reusing these models as the closed leaf and admission-parent law. All existing C/G/H/O/I/P/Q/R public law stays unchanged.

**Complete root-region admission consumer (018-t inert, ACCEPTED at its bounded complete-consumer scope WITH PROCESS QUALIFICATIONS AND EXPLICIT IMMUTABLE-REPORT CORRECTIONS (strategic decision `S/reviews/018-t-decision.md`)).**
The separately versioned
`cache-root-region-admission/v1` /
`root-region-admission-policy/v1` operation
`derive_root_region_admission` takes the ACTUAL retained P
root-region lineage state and namespace (never caller-positive
R/Q/F/graph/admission snapshots or verification flags) and, in
ONE pure bounded charged operation, derives the ACTUAL R
(including the ACTUAL same-run Q currentness, P selection,
selected root source and F/E current graph) EXACTLY ONCE
through the narrow typed R-core seam, consumes it with the
ACTUAL selected-root-aware G assembly (the SAME G subtree
ledger the F phase charged) and closes the complete full-
result THIRD carrying boundary (`RootRegionAdmissionResult`):
the exact input state/namespace/revision/lineage retained on
EVERY outcome, the ACTUAL R result by immutable reference
(once returned, on every later outcome, as bounded evidence;
the terminal record stays bounded to metadata and never
re-enters the root BODY content pass), and the ACTUAL S
admission parent by reference (READY only). The NEW
entire-consumer outer (total work 8388608 and own diagnostics
64, DEFAULT AND HARD, stricter positives legal) is created
BEFORE early scope/hash/bound/construction work, couples every
actual R unit (Q/P/D/B/source/F/E included) unit-for-unit
BEFORE the crossing work, creates the actual G subtree ledger
BEFORE R's F phase (every actual F unit charges the SAME G
ledger the admission phase uses; G covers F plus admission and
does NOT cover Q/P/selected-source resolution or the final
full-result parent), and leaves every actual inherited
Q/P/D/B/E/F/GraphBounds, G, graph/admission-stage,
diagnostic, source and original-batch domain independently
binding beneath it (no global minimum, reset, whole-cap
reservation, post-hoc initialization, module/context-global
budget channel or caller verification flag; original-batch
caps are not cumulative retention caps; shared work charges
each applicable domain once). READY means only actual R READY
AND completed actual admission AND the full-result checks --
never acquired dependencies, compiled content, cache
readiness, HTTP or v1 runtime readiness; Q
uncertainty/conflict, R/F/G refusal and every resource
crossing expose no usable admission or bootstrap fallback and
retain every already-returned actual evidence truthfully
(never rerun or manufactured after a crossing). The
32768-byte root-only and mixed-region/no-singleton shapes earn
complete-operation READY at their stated domains (the
mixed/multi-history positive complete-operation data under the genuine
legal 1048576 GraphBounds stage setting, the default-stage
refusals recorded honestly), which is NOT default whole-
consumer readiness and NOT zero allocation. It is the same-018 complete consumer promised by R/S; whole objective 018 is now ACCEPTED at its complete INERT graph/currentness/admission scope (strategic decision `S/reviews/018-t-decision.md`) and stages 019-024 remain mandatory. The exact scope is versioned in `docs/CACHE-ROOT-REGION-ADMISSION-CONTRACT.md` (`tests/test_root_region_admission.py`); the stage stays inert and inactive.

**Bounded RAM owner and atomic state storage (019-a inert, ACCEPTED at its bounded inert RAM owner/store scope WITH PROCESS QUALIFICATIONS AND IMMUTABLE-REPORT CORRECTIONS, strategic decision `S/reviews/019-a-decision.md`).** The separately versioned `cache-ram-state/v1` store (`src/slaif_local_coding/constitution/bundles/ram_state.py` / `ram_state_models.py`; contract `docs/CACHE-RAM-STATE-CONTRACT.md`; `tests/test_bundle_ram_state.py`) implements the first 019 slice: per-session immutable RAM ownership over ACTUAL accepted 018-p/018-t records, bound to the COMPLETE trusted namespace, ONE live owner and explicit cache epochs; a conservative measured occupancy recipe charging every retained owned component before commit (identity-deduplicated within one owner; no total-RSS promise); the mandatory expected-revision commit CAS; atomic process/session ceiling checks (defaults 536870912 bytes/process and 134217728 bytes/session) returning the fixed typed 503 contract with existing state preserved; the retained historical entry catalog (a superseded current entry never destroyed; a genuinely new compatible revert may reuse it, replay cannot reactivate it); explicit teardown freeing only that namespace's occupancy and fencing the old epoch; no TTL/LRU, no capacity eviction, no automatic dormant scan and no disk-backed normal lookup. It is INERT: no compiler or tokenizer integration, no wire integration, no recovery and no v1 runtime activation -- the bounded async single-flight work plane is the separate 019-b slice below, and the 019-c whole-019 closure round (below) supplies the remaining pressure / source-scale / lifecycle evidence at its inert injected-work layer; 020-024 stay mandatory. The stage stays inert and inactive.
**Bounded async single-flight work plane (019-b inert, delivered, NOT ACCEPTED against the complete accounting requirement or whole 019 (strategic decision `S/reviews/019-b-decision.md`)).** The separately versioned `cache-ram-work/v1` work plane (`src/slaif_local_coding/constitution/bundles/ram_work.py` / `ram_work_models.py`; contract `docs/CACHE-RAM-WORK-CONTRACT.md`; `tests/test_bundle_ram_work.py`) is the second 019 slice over the ACTUAL 019-a registry/owners and ACTUAL accepted 018-p/018-t records: opt-in via the registry `work_bounds` (the 019-a default behavior is unchanged), ONE process-wide active leader (closed constant) with a bounded pending distinct-key FIFO and bounded waiters per key (explicit positive non-bool bounds, closed hard ceilings), the ratified claim / join / terminal NO-RETRY attempt policy (pre-claim capacity refusals with zero invocation and no attempt; a claimed attempt terminated by cancellation before dispatch with zero actual invocation; terminal metadata retained and charged until explicit teardown, never evicted to retry; a later request / revision / nonce never authorizes retry), the cancellation law (a single waiter detaches only; all waiters gone cancels AND awaits the owned work; an unstarted dispatch task finalizes once with zero invocation), the owner / namespace / epoch / current-key publication fences (fenced -> epoch -> key-not-current -> capacity; superseded late completion never published) plus the 019-c adverse-currentness `owner_quarantined` fence (a validated adverse store-capacity refusal may set it; carried through with the fixed typed 409 currentness refusal; teardown-only exit), conservative occupancy charging of every retained work component BEFORE retention / publication (identity-deduplicated measured sizes plus the closed fixed task 4096 / queue-entry 64 / waiter 1024 / pre-allocated terminal 2560 / global pump 4096 reservations -- no soft-cap exception, no total-RSS promise) under the SAME 019-a process / session ceilings as the store (at pressure the fixed typed 503 preserves the retained state bytes, counters, lookups and payloads, with the single bounded `owner_quarantined` current-usability exception), valid immutable payload retention separate from current publication (a valid A1 payload survives A2 supersession and is reused on a genuinely proven compatible A1 revert WITHOUT a third invocation; a FAILED A1 attempt still applies after a genuine old-bytes revert; replay / equal-byte witnesses never reset), and the explicit async teardown that fences, cancels and awaits, then releases store and work in ONE critical section (no same-epoch reset window) with the synchronous store teardown fenced `work_in_flight` while work is live. The injected bounded async seam is synthetic: it proves prepared-work orchestration only (actual compiler / tokenizer semantic validation is 021). It is INERT: no wire integration (022), no recovery (020), no v1 runtime activation; the 019-c whole-019 closure round (aggregate pressure with high-water shared-container retention, substantial-source/accumulated-history over ACTUAL accepted records, the quarantine boundary, cancellation/update/teardown races and the denied-filesystem lifecycle proof; `tests/test_bundle_ram_lifecycle.py`) is implemented at the INERT injected-work layer and PENDING strategic review.
**Protected session recovery (020-a/020-b inert, implemented,
PENDING strategic review).** The separately versioned
`cache-recovery-record/v1` / `cache-recovery-resume/v1`
recovery component (`src/slaif_local_coding/constitution/bundles/`:
`recovery_models` / `recovery_codec` / `recovery_store` /
`recovery_resume`; contract
`docs/CACHE-RECOVERY-CONTRACT.md`;
`tests/test_bundle_recovery_codec.py`,
`tests/test_bundle_recovery_store.py`,
`tests/test_bundle_recovery_resume.py`) implements the WHOLE 020
component stage over the ACTUAL accepted 018-p/018-t records and
the accepted 019 RAM owner/work plane: a versioned closed
recovery record retaining the exact extracted original bundles
and derived metadata (never transport credentials or
credential-bearing wrappers; detectable forbidden credentials
cause typed rejection / quarantine without logging content; no
executable deserialization; real accepted P/D validation and T
derivation before a record is restorable); the trusted stable
resume address (principal / session / repository / route plus
configured model / policy context) that locates EXACTLY ONE
record with NO root, source or surviving virtual reference in
the resumed request; the protected per-session store
(operator-prepared existing 0700 current-owner root,
descriptor-relative 0700 / 0600 sessions, no symlink / path
escape, the OS-held exclusive writer, expected-generation CAS,
atomic generation publication with integrity digests, fsync of
file and directory before durable success, the ACTUAL committed
outcome reported on every fault, reused orphan checkpoint bytes
fsynced before publication, and `current_generation`
distinguishing MISSING from corrupt); the bounded shared-RAM
recovery reservations against the SAME 019 process / session
ceilings BEFORE load / serialization / transient allocation (the
cold pre-load `max(4 x committed, 16KiB)`, the bounded
publication `max(24 x (owned + 16KiB), 16KiB)`, the bounded
JSON 6x worst case, and the closed session-reservation term in
the 019 admit sums); the durable epoch binding (a distinct live
epoch strictly above the durably bound prior, re-published on
EVERY resume so the committed generation advances and the prior
epoch advances durably, with NO usage rewrite within an
epoch); the durable fail-closed adverse-quarantine fence (a
validated capacity-quarantined owner can never resume its older
usable bytes; a failed durable fence blocks the unsafe
transition; no automatic unquarantine / retry / epoch reset);
the owned bounded ASYNC store IO (ONE process-wide owned
publication slot with the typed busy refusal, the bounded
transient reserved BEFORE task / thread dispatch,
cancellation / timeout / teardown draining the owned write to
its ACTUAL outcome before the slot / reservation / writer are
released, the teardown admission fence held across the drain,
and the same-lock work-teardown admission close so a draining
work teardown can never release under live recovery IO; 020-b
closes the 020-a ownership / fault corrections at the same inert
scope: the ONE writer-owned session serializes the ENTIRE
generation CAS and publication attempt (a competing same-handle
publication is refused `write_in_flight` before a second CAS or
pointer mutation; a closed session refuses `session_closed`
before IO), an ordinary filesystem read fault is contained at
the store boundary as the typed `io_failure` with the BEST
actual observed generation (never a raw escape past owner
teardown / session close; a failed epoch binding still removes
the partially prepared owner and releases its reservation and
the writer), and the synchronous-operation preemption gap is
closed by the claimed-owner fence (entry check and live-owner
claim are ONE atomic registry step tied to the ONE owned store
IO slot; both direct teardown paths refuse `recovery_in_flight`
while a transient is held OR the operation is claimed; a
teardown that wins makes the claim a clean typed refusal with
no cold reservation or publication)); and
the lazy once-per-epoch rebuild through the ACTUAL 019 work
plane with mechanically denied recovery-content reads and zero
new seam invocations on normal RAM hits. It is INERT: no
wire / HTTP integration (022), no actual compiler / tokenizer
(021), no v1 runtime activation, PENDING strategic review at
its bounded inert recovery-component scope, and 021-024 remain
mandatory. The stage stays inert and inactive.
**Pinned tokenizer, budgets, direct compiler and selection
(021-a inert, ACCEPTED at its bounded inert component scope; whole 021
accepted, PR 29 merged to main at
144af0bd5e34387afcb8e3f9ddf761eabd56e817, per the 022 order).** The
separately versioned `cache-bundle-tokenizer/v1` /
`cache-bundle-budget/v1` / `cache-bundle-compiler/v1` /
`cache-bundle-compile-work/v1` / `cache-bundle-selection/v1`
component (`src/slaif_local_coding/constitution/bundles/`:
`bundle_tokenizer` / `bundle_budget` / `bundle_compiler` /
`bundle_compile_work` / `bundle_selection`; contract
`docs/CACHE-TOKEN-COMPILER-CONTRACT.md`;
`tests/test_bundle_tokenizer.py`,
`tests/test_bundle_budget.py`,
`tests/test_bundle_compiler.py`,
`tests/test_bundle_compile_work.py`,
`tests/test_bundle_selection.py`) implements the 021
component stage (B01-B04 and the compiler half of C03) over
the ACTUAL accepted 018 current P/T records, the accepted 019
RAM owner / single-flight work plane and the whole-020
recovery component: the pinned actual Qwen3.8-27B CPU
tokenizer (the closed digest-pinned four-asset table at the
pinned upstream revision, `tokenizers==0.22.2`,
load-and-validate ONCE with observable load counts and no
hot-hit reloads, the tokenization identity derived from the
verified digests so any asset / template byte change
invalidates it, the documented no-padding render policy, and
no model weights / torch / image decoding / runtime model
download / hosted tokenizer call); the explicit validated
budget contract (configured `C`, slot `floor(C/32)`, width
the distinct represented file count, allowance `width x
slot`, aggregate `floor(C/4)`, reserves generation
`max(4096, floor(C/8))` / tools 2048 / uncertainty-template
1024, real-tokenizer counting of the final rendered compiled
text including references / metadata / separators, the
`qwen3-model-envelope/v1` closed conservative structure
bounds for remaining request / tool / envelope emissions
under explicit finite item limits, independent byte / parse
limits, the caller's requested generation limit respected,
per-retained-image reserves only under the explicit vision
contract after the unchanged image policy, typed required
overflow (422) and whole-entry optional omissions, never
padding or silent truncation); the direct authenticated
tool-free NON-RECURSIVE compiler (ONE actual 018-t admitted
entry, the FULL compile key, distinct bounded identity-bound
policies for input / single-attempt generation / supported
reasoning / JSON overhead / timeout, the protected
environment credential reference, provider truncation typed
BEFORE content validation, the closed invalid / truncated /
over-budget / cancelled vocabulary that never becomes an
entry or a hit, no retry / tools / recursion / Gateway
credential / hidden original fallback, and the separately
metered dispatch / outcome accounting); the
compile-through-RAM composition (the ACTUAL seam over the
accepted 019-b `RamWorkCoordinator`: the configured-policy
fingerprint fence at the claim boundary (fixed 409, zero
invocations), the strict re-validation and full-key /
content-key re-join of EVERY serving retained payload,
`POLICY_STALE` for a differing full key with rebuild only
through a needed NEW epoch, the unchanged 019 single-flight
/ no-retry / capacity / currentness laws, and A1 -> A2 ->
genuinely new compatible A1 reuse of the valid historical
payload WITHOUT a third invocation while replay cannot
reactivate stale state); and the deterministic selection
(complete required governance first — the P0 root plus the
root-scoped P1 binding closure — then optional entries by
ACTUAL P2/P3 priority, narrower eligible coverage and stable
identity, the scoped root / authority envelope, exact
missing-binding read guidance that an opaque reference or
uncertain greedy row never substitutes for or suppresses,
observable whole-entry duplicate-coverage omissions, the
unproven-member-origin provenance line, and the aggregate
limit decided over the EXACT COMBINED final injected text
with the real pinned tokenizer). It is INERT as a
standalone stage: no wire / HTTP integration; the
022-a configuration, 022-b pure-transaction and
022-c application-transaction slices (below) are
the delivered same-objective 022 stages, and
023-024 remain mandatory; the 022-c wiring
activates these components inside the governed
v1 request path (at its bounded fake-upstream
application scope, MERGED to main through
PR #30 at 4319049d91428b8995e83db82b1736ed36626a12).
**Validated opt-in cache configuration (022-a inert,
implemented, MERGED to main through PR #30 at
4319049d91428b8995e83db82b1736ed36626a12, reviewed at its
bounded configuration scope).** The explicit
`[context_cache]` profile selector on the actual `Settings`
and TOML loader (`config.py`): omission or explicit `legacy`
keeps the existing legacy behavior and defaults;
`dependency-bundles-v1` is accepted only with its closed typed
configuration — the explicit effective-context budget reusing
the accepted `BundleBudgetConfig`, the explicit bounded
compiler policy reusing `BundleCompilerConfig` (its protected
environment credential reference may share the private
upstream environment name but never a Gateway credential's),
the explicit bounded process/session RAM ownership reusing
`RamStateBounds`, the strict one-worker policy (any other
count, boolean, float or string fails closed), admission
defaulting to `lean` with `greedy` explicit, the explicit
protected-recovery opt-in with configured absolute normalized
root (validation never opens, creates, enumerates or probes
the store, never resolves a workspace, never reads
credentials and never calls an upstream), and each governed
route's explicit model contract binding its declared model to
the pinned tokenizer/render capability and the configured
effective C (orphan/missing contracts fail closed first; a
changed effective context or compiler compatibility is a
distinct budget/compile policy through the accepted 021
identity recipe). The legacy/v1 migration law: an explicitly
supplied legacy cache/TTL/LRU, derived-rehydration, compiler
or byte-injection/selector policy under v1 is a fixed
configuration error even at its default value, while a
materialized default or an empty policy block alone does not
conflict and the common enablement/identity fields stay
shared. The effective context and 021 budget bounds are
validated against each enabled v1 route's declared
model/vision contract (mixed vision declarations, uncovered
image limits and contract mismatches fail closed; passthrough
routes declare no enforced image limit). Configuration error
messages are fixed, validation errors never echo the raw
input, and the recovery root never appears in reprs. At the
`create_app` entry point a valid selected v1 profile is
refused with the fixed `V1RuntimeUnavailableError` before any
HTTP client, legacy cache or recovery owner construction
(`tests/test_config.py`, `tests/test_app.py`). It is INERT:
no v1 runtime, no source replacement, no wire integration;
the same-022 transaction wiring removes the guard.
**Pure exact-span source replacement
transaction (022-b inert, implemented, MERGED to main
through PR #30 at 4319049d91428b8995e83db82b1736ed36626a12,
reviewed at its bounded pure-transaction scope).** The
separately versioned
`cache-bundle-replace/v1` policy-12 pure exact-span
transaction (`bundle_replace.py` /
`bundle_replace_models.py`) over the ACTUAL
017/018/019/021 records: the edit plan is derived
from the actual current decoded request, the
accepted 017 observations, the original 018-p
proof/occurrence and 018-t admission witnesses and
the actual prepared 021 working set; the root
content span excludes its delimiters and
environment tail, both accepted read endpoints are
joined, and a governing root selected through a
read/read_region keeps its carrier a tool result
with that exact (occurrence, segment) coordinate
skipped by the FILE join (the same root region is
never double-edited); every retained witness
re-joins through ITS OWN owner proof bound to the
SAME original call ID, genuinely absent carriers
earn zero edits, and an unsupported/nonzero/
truncated/unpaired current wrapper earns no proof
and no edit; the two unambiguously versioned
opaque marker kinds (live reference, non-resolving
evidence) are authenticated with a domain-
separated standard HMAC under supplied private
per-session key material, scoped to the complete
trusted namespace, the original role, the exact
occurrence or root-source identity and the
segment/carrier association, the wire form
exposing only the versioned kind tag plus the
fixed-length canonical base64url MAC tag; a known
positively superseded original earns the
non-resolving evidence marker only from the ACTUAL
same-run E overlay group facts (the proven change
on the admitted paths, no conflict or ambiguity
blocker) and the ACTUAL same-run P/Q root lineage
(a retained unissued digest, mere absence from
selection or uncertain attribution never proves),
and an omitted prepared optional source earns the
same marker, never a dangling live reference; all
edits are planned and applied atomically on a deep
copy (the input is never mutated; roles, non-
source text, wrappers, prefix/suffix, printed
delimiters, Unicode/CRLF, images and every tool
ID/name/argument/status/order are preserved);
every committed edit is earned by the narrow
durable-generation handoff (the ACTUAL accepted
`RecoveryPublishResult`/pointer and the EXACT
retained `RamStateSnapshot` by identity); the
closed replay scan gate (an accepted replay at the
original splice start replays content-free at its
shifted coordinates to the fixed point; a stale
live reference, forged, cross-namespace, moved or
kind-incompatible marker always refuses; the
marker claim stays at its earned scope: this
pure round verifies and re-joins the markers
and persists no new observation, and pre-
acquisition wiring into actual lineage/state
belongs to the later application slice); and
the plan-13 typed all-or-nothing
failure families (nonusable selection and over-
bound 422, missing/failed/mismatched durability
503, span/marker/namespace conflicts 409).
`tests/test_bundle_replace.py`. It is INERT: no
wire / HTTP integration, no actual upstream tool
issuance, no recovery IO, no v1 runtime
activation; the same-022 application wiring
lands in 022-c (below), and the 023-024 full
actual-upstream evidence beyond the 022-c
fake-upstream scope remains mandatory (NOT
RUN).
**V1 application transaction (022-c implemented,
active on opted-in v1 routes, MERGED to main through
PR #30 at 4319049d91428b8995e83db82b1736ed36626a12, reviewed
at its bounded fake-upstream scope).** The runnable v1
application
transaction on the ACTUAL `create_app` entry
point (`app.py`, `v1_runtime.py`,
`v1_application.py`): the resumed / steady-
state session join over the ACTUAL
accepted 020 owned/fenced admit/checkpoint
path (no raw writer shortcut; the 022-c cold
bootstrap instead performed raw acquisition
and checkpointing in its first establish call,
before any marker gate and outside the fence
— both closed by the 022-d slice below), the
marker-
shaped source replay detected and
authenticated BEFORE the transition's raw
acquisition (the fixed typed marker-side
refusal on a tampered tag, no raw fallback),
the single outgoing body of the one main
upstream forward (the transformed payload on
OK, the unchanged original on NO_REPLACEMENT)
and the byte-identical transformed-round
fixed point; the historical read-root replay
gap closed (a positively superseded read-
root original joined at its own retained
coordinates through the governing read/
read_region source with its carrier a tool
result, that exact (occurrence, segment)
coordinate skipped by the FILE join, the
historical old-anchor envelope kept
separate, and the stale live format refused
on replay); the per-request FROZEN
represented-frontier trusted issuance
binding (the ACTUAL direct main upstream
response only — actual nonstream and
split-SSE issuance causality, never
compiler traffic — each COMPLETE supported
call registered under the committed-state
CAS against the exact represented
completed-fact frontier of THIS specific
committed request: the represented root fact
plus every selected file entry's witness
provenance and verified raw-carrier join of
this payload, reduced over PROVEN frozen
ancestors only; retention alone never
establishes a parent; the frontier freezes
at this request's commit and is never
rebased on later state, caller items,
result arrival, new call IDs, revisions or
replay metadata — two distinct frozen
frontiers prove no later-fact rebasing);
the pre-forward protected generation
(every committed edit earned by the ACTUAL
successful publication of the exact
snapshot the edits rely on, the retained
successful pointer bound to the exact
snapshot/epoch it actually published: a
faulted publication keeps the prior bound,
the newer undurable record set is refused
on replay and never forwarded under the
stale generation proof, and a replay after
fault refuses until the generation heals);
the fixed typed v1 request refusal family
(422 budget / invalid transform, 409
version / scope conflict including the
marker-side refusal, 503 infrastructure /
recovery / resource) with NO raw fallback
forward; and the application-owned private
marker key as a PROTECTED ENVIRONMENT
REFERENCE resolved once at v1 runtime
construction (repr-suppressed, never a
gateway / service credential, never
persisted or logged). `tests/test_app.py`,
`tests/test_v1_application.py`. Bounded
FAKE-UPSTREAM application scope only
(synthetic identity and fixture sources;
the real app entry point, the actual
forwarding, compiles and recovery content
reads instrumented): the 023 expanded
adversarial/lifecycle/telemetry matrix and
the 024 actual-model/genuine-Codex
qualification remain mandatory (NOT RUN).

**V1 application closure (022-d implemented,
active on opted-in v1 routes, MERGED to main through
PR #30 at 4319049d91428b8995e83db82b1736ed36626a12, reviewed
at its bounded fake-upstream scope).** The closure slice on
the same
ACTUAL `create_app` entry point (`app.py`,
`v1_application.py`, `bundle_replace.py`):
the closed COLD marker/source-carrier law
applied BEFORE any cold raw acquisition,
owner allocation or checkpoint (a fresh
trusted address has no retained state that
could authenticate a source marker, so the
ACTUAL cold-recognized root/result content
spans alone decide: a marker-shaped
candidate inside them is refused with the
fixed typed 409 — zero new owner,
generation, compile or main forward — while
marker-shaped text anywhere else stays
ordinary data; a prior session's marker
presented cold to a different trusted
namespace is refused under its own distinct
namespace-scoped MAC, and the later
legitimate bootstrap succeeds), correcting
the 022-c cold path; the accepted 020
`admit_with_fence` on BOTH the cold and the
steady-state transitions (an adverse durable
fence or checkpoint fault is the fixed typed
503 with zero main forward, the acquired
cold owner/writer is safely cleaned up on
every prepublication failure, the same-
process retry stays fail-closed under its
distinct fenced epoch, and a fresh process
completes the publication through the
store's idempotent same-generation orphan
re-publication), correcting the 022-c cold
path (a direct admit plus a separate
checkpoint, outside the adverse durable
fence); the root-currentness 409 at the app
boundary (actual P/Q/T evidence
`root_currentness_unproven` or an
established root-authority conflict
refuses with the fixed typed 409, zero main
forward, the retained P/Q evidence kept and
no bootstrap fallback, while a genuinely
issued unambiguous descendant preserves the
accepted component lineage); the compiled-
context injection at the endpoint-specific
stable placement (Responses top-level
`instructions`, the caller's own
instructions preserved after the region;
Chat the first string-content system
message, else a system message inserted at
the front, so an opaque marker always
accompanies its usable compiled content and
off-graph content is never promoted to a
higher API role); the Chat endpoint
evidence at the actual entry point (the
endpoint-in-binding law: a read issued on
`responses` cannot complete on `chat` (the
typed issuance conflict), root authority
stays Responses-only (a Chat message
carrying the envelope text stays data), and
the Chat round issues AND completes its own
reads on the chat endpoint — actual
nonstream and split-SSE issuance causality
at the app boundary); the source-change law
at the app boundary (a model-issued re-read
proving the later version marks the
positively superseded original with the
non-resolving EVIDENCE marker at its
retained carrier and the new carrier LIVE,
a stale OLD transformed body refuses with
the fixed 409 marker-side refusal and no
forward, and a genuine same-digest revert
brings the carriers LIVE again reusing the
retained historical payload without
recompile); the compiler/budget failure law
at the app boundary (the typed budget fence
runs inside the compiler seam BEFORE
retention, the terminal failure is re-
served to a later same-key/epoch request
with the same fixed typed 503 refusal and
no retry loophole, recovery is a NEW epoch
in a fresh process, and the selector's 422
fence stays the last line of defense for
forged/retained payloads only, unreachable
through the real compiler channel); stream
disconnect closes the owned upstream on the
v1 path; the ungoverned-route payload
forwards byte-identical with zero compiles
and no session; and the fixed typed v1
refusal family at the app boundary (409
POLICY_STALE / TRANSACTION_CONFLICT
including the cold-marker, marker-side and
root-currentness refusals, 422
SELECTION_REFUSED / TRANSACTION_OVER_BOUND,
503 for the infrastructure/recovery/
resource families) with NO raw fallback
forward. `tests/test_app.py`
(TestV1ApplicationClosure),
`tests/test_v1_application.py`. Bounded
FAKE-UPSTREAM application scope on BOTH
endpoints (synthetic identity and fixture
sources): the 023 expanded
adversarial/lifecycle/telemetry matrix and
the 024 actual-model/genuine-Codex
qualification remain mandatory (NOT RUN).

**V1 stage telemetry and protected synthetic application evidence (023-a implemented,
active on opted-in v1 routes, PENDING strategic review).** The stage-telemetry
slice on the same ACTUAL `create_app` entry point (`v1_telemetry.py`,
`app.py`, `v1_application.py`,
`tests/test_app.py` (TestV1StageTelemetry),
`tests/test_v1_application.py`): the
owned-stage content-free stage facts (recognition, complete
acquisition, the actual same-run graph, admission, compilation,
replacement, compiled injection, source-absent injection,
recovery, main upstream and the closed four-way reuse class) recorded at each
owning stage from the ACTUAL typed results with closed per-stage
outcome and detail vocabularies (content-free by construction: bounded
counts only, never values, source, identifiers, paths, digests or credentials); the closed content-acquisition facts (the complete/partial/unsupported read partition, the observed member and character counts, the absolute-path normalization outcome) and the actual same-run R/F graph facts (the closed honest node-availability partition, the edge count and the candidate count) published through the existing private metrics registry with fixed labels (revision/epoch evidence out of metric labels); the actual final-envelope injection token measurements (governance and request) as histogram samples against the configured aggregate-limit gauge; the send-boundary main-forward classification (the forward fact at the call boundary, provider acceptance only on 2xx, transport errors, refusals and cancellation distinct from acceptance); the backend provider usage ledger independent of client-reported cumulative usage; the closed original-present RAM reuse / source-absent injection / restart-rebuild-new-epoch distinction (genuine client compaction closed but UN-EARNED without a real client event); and the protected synthetic stage evidence assembled by the TEST HARNESS from its own fake-upstream / compiler captures (0700/0600 under the round's private artifact directory; no raw-content persistence surface in the runtime). Bounded FAKE-UPSTREAM application scope only (synthetic identity and fixture sources): the complete 023 negative-path/stress-test matrix and the 024 actual-model/genuine-Codex qualification remain mandatory (NOT RUN).

**Current-root composition (018-i inert, NOT ACCEPTED; 018-j
PARTIAL, NOT ACCEPTED; 018-k NOT ACCEPTED; 018-l PARTIAL,
NOT ACCEPTED; 018-m PARTIAL, NOT ACCEPTED; 018-n repairs
ACCEPTED; 018-o mixed observation ACCEPTED WITH PROCESS
QUALIFICATIONS; 018-p root-region producer ACCEPTED WITH
PROCESS QUALIFICATIONS; 018-q root-region currentness
ACCEPTED WITH PROCESS QUALIFICATIONS AND HISTORICAL-
REPORT CORRECTIONS; 018-r root-region graph ACCEPTED WITH
PROCESS QUALIFICATIONS AND EXPLICIT HISTORICAL-REPORT
CORRECTIONS at its bounded graph-only scope).**
The 018-i composition takes the ACTUAL retained 018-h
root-lineage state and its ACTUAL namespace (plus the NEW
composition bounds and the ACTUAL inherited H/D/E/F/G bound sets)
and, in ONE pure bounded charged operation, derives the ACTUAL
018-h current-root selection AND the actual selected-root source
resolution (the ENVELOPE source from the actual immutable D root
anchor; the READ source by the actual selected witness occurrence
in the SAME retained D state with exact identity/endpoint/digest/
byte-length cross-checks against the retained original proof
binding; ALL compatible maximal witnesses with their original
coordinates) AND the accepted 018-f current graph over a FRESHLY
recomputed least fixed point with the selected root as the NEW
root supplier (never snapshot-seeded; the actual 018-e nonroot
currentness/group-ownership law preserved; cycle-only withdrawal
and restoration from the SAME retained originals; least AND/OR
depths and effective max_depth recomputed) AND the current
admission entries with the ACTUAL 018-c canonical recipe under
the selected governing digest (root compatibility uses the
ACTUAL selected digest, never the bootstrap digest as freshness;
proven root groups filtered against the selected digest BEFORE
entry planning; valid nonroot segments preserved with no new
greedy isolation; ONE first-class root entry with the actual
ENVELOPE/READ provenance, compatible rows never a second
governing root). An authoritative differing-root conflict is a
fixed no-selected-source, no-ready-output result, never a
bootstrap fallback; unissued source never grants governing
authority and the retained ROOT_SOURCE_UNPROVEN limitation
surfaces exactly. The NEW composition bounds (total work 1048576,
diagnostics 64; default AND hard, stricter positives allowed) run
on ONE composition outer covering the ENTIRE operation, with the
accepted G total covering the F+admission subtree only and the
H/D-local/E-local/G-subtree/F-subtree and graph/admission-stage
ceilings independent beneath it (no global min, no resets; the
original-batch max_requests domain preserved; cumulative
retention domains kept distinct). Closed actual-field fences
run before ANY serialization traversal and source
character/UTF-8 lengths are preflighted before any owned
slice/encode/hash/copy; the model association law re-derives the
actual admission namespace, the actual input history key and the
carried graph context on EVERY construction and joins every
entry proof and witness to the EXACT input state by identity
(a later genuine proof/entry/row spliced into an earlier state
is refused even when self-consistent). Documented UNREACHED
limitation: post-refresh NEW-root mixed bundles are refused by
the UNMODIFIED public H acquisition before I (the old H law is
not broadened and no positive is manufactured); the new 018-o
`observe_root_lineage_mixed` operation (root-lineage contract
section 5a) supplies root-aware mixed acquisition at its own
operation scope while this old public path stays unchanged and
the UNREACHED label above applies to it. The exact scope
is versioned in
`docs/CACHE-CURRENT-ROOT-COMPOSITION-CONTRACT.md`; it earns the
root-aware current graph/admission composition MECHANISM at its
bounded inert scope only (NOT ACCEPTED; the bounded 018-j
repairs J01/J02/J03 were delivered truthfully PARTIAL and are
NOT ACCEPTED against the complete J01/J02/J03 criteria,
strategic decision `S/reviews/018-j-decision.md`; the bounded
018-k repairs (K01 actual nested canonical keys at BOTH parent
boundaries, K02 actual nested row shapes before exact-relation
comparison, K03 genuinely reachable E collection caps with exact
evidence labels) are NOT ACCEPTED against the complete
K01/K02/K03 criteria, strategic decision
`S/reviews/018-k-decision.md`; the bounded 018-l repairs (L01
complete closed nested entry / key-record / ownership metadata
fences at the leaf and BOTH parent boundaries with the entry /
record authority and width joins, L02 independently derived
actual E collection-domain counts with a before-target charge
sentinel) were delivered truthfully PARTIAL and are NOT
ACCEPTED against the complete L01/resource/artifact criteria
(strategic decision `S/reviews/018-l-decision.md`); the bounded
018-m repairs (M01 O(1) count / scalar gates BEFORE any element
/ set / sort / hash / serialization work at the leaf and BOTH
parent boundaries, with the closed TEN admission bound-model
fence and the accepted dense group ordering / unique partition
law; M02 the exact accepted JSON serialization byte ceiling and
the reservation-calculation work precharge on the ONE I outer)
were delivered truthfully PARTIAL and are NOT
ACCEPTED against the complete M01/M02 criteria (strategic
decision `S/reviews/018-m-decision.md`); the bounded 018-n
repairs (N01 the retained-content join at the leaf and BOTH
parent boundaries — the entry-local group partition joined to
the ORIGINAL proof segments and the root group to the retained
root digest — plus N02 the byte-aware closed reservation, the
pre-fetch plan segment precharge and the per-site
reservation-calculation closure) are ACCEPTED at their
bounded inert scope WITH PROCESS QUALIFICATIONS
(strategic decision `S/reviews/018-n-decision.md`); the 018-o
root-aware mixed-observation slice (the new pure
`observe_root_lineage_mixed` operation plus
`ROOT_LINEAGE_MIXED_OBSERVATION_VERSION`; a proven mixed root
member matching an independently authoritative known version
of the same effective root — including an independently
issued complete whole singleton in the SAME batch — acquires
source evidence while a mixed read mints no governing
authority, unresolved foreign digests keep the exact
COMPETING_ROOTS refusal, and the pending-set snapshot is
precharged on the SAME H outer) is implemented and
ACCEPTED at its bounded inert scope WITH PROCESS
QUALIFICATIONS (strategic decision
`S/reviews/018-o-decision.md`; root-lineage contract
section 5a); the 018-p versioned root-region authority
producer (the separate `cache-root-region-lineage/v1`/
`root-region-lineage-policy/v1` contract and the
`read_region` provenance kind: a genuinely issued
complete NEW root region in a mixed-only read acquires
source evidence AND authority with NO independent
singleton, the no-exception read shapes, before-
materialization retention under the unchanged H
ceilings, the ONE new-operation outer, the honest old-I
refusal of the region-version state and the closed host-IO
purity surface) is ACCEPTED at its bounded inert producer
scope WITH PROCESS QUALIFICATIONS (strategic decision
`S/reviews/018-p-decision.md`; root-region contract
`docs/CACHE-ROOT-REGION-LINEAGE-CONTRACT.md`); the
018-q root-region currentness query (contract
`docs/CACHE-ROOT-REGION-CURRENTNESS-CONTRACT.md`) is
ACCEPTED at its bounded inert query scope WITH PROCESS
QUALIFICATIONS AND HISTORICAL-REPORT CORRECTIONS
(strategic decision `S/reviews/018-q-decision.md`; the
018-r consumer slice, contract
`docs/CACHE-ROOT-REGION-GRAPH-CONTRACT.md`, is ACCEPTED at its bounded inert selected-root source/current-graph scope WITH PROCESS QUALIFICATIONS AND EXPLICIT HISTORICAL-REPORT CORRECTIONS (strategic decision `S/reviews/018-r-decision.md`)))
and the stage stays inert and inactive.

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
result IDs) by a no-retention preflight decided before any record tuple, location string, identity map or diagnostic is built or retained — a
fixed non-acquiring `OVER_BOUND`, never a silently truncated inventory; each inspected outer `input`/`messages` list AND each assistant `tool_calls` list is individually O(1) length-tested against the existing per-container item bound before iteration, parsing or retention (017-p; `max_items` is never a total across lists, and an at-limit nested list still passes), selected-domain scoping under explicit endpoint
selection, mixed bounded across inspected domains; absent/
null/empty and non-string result IDs are fixed typed non-echoing
unpaired limitations (`MISSING_RESULT_ID`/`MALFORMED_RESULT_ID`),
never invented, hashed, attached or acquired; opaque result families such as `custom_tool_call_output` do not participate in the pairing bookkeeping. The exact internal call/result IDs stay usable for pairing and bookkeeping, while the operational `str`/`repr` of report, read and unpaired objects never echo private ID values (a non-empty `call_id` renders as the fixed `<private-id>` placeholder; the empty no-ID state stays exact; no ID is invented, hashed or re-serialized, and no private value becomes a metric label). Earned in 017-f
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
process RSS; pressure returns a fixed 503 with existing state preserved (the retained bytes and counters stay intact; a validated adverse store-capacity refusal may additionally set the bounded pre-accounted adverse-currentness fence, which refuses the old current usability until explicit teardown -- the 019-c `owner_quarantined`). Cleanup happens
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
separate human-authorized act); 006 signed-request replay hardening
(PR #8); 007 current Gateway contract CI (PR #9); 008 durable acceptance
evidence (PR #10). Objectives 009-015 are merged through PR #22
(release-candidate line; it concluded with the private RC10 candidate).
Cutover NOT performed; NOT released. Objective 016 (merged PR #24, merge
`96c790423f6f0097a56a0b12bacda8a9b6da6aba`): dependency-bundle cache rework
contracts (handoff, plan, reconciled architecture/law, stage ledger).
Objective 017 was ACCEPTED at its bounded pure-observation scope WITH
PROCESS QUALIFICATIONS (017-am decision, `reviews/017-am-decision.md`) and
merged to main at ffaabf4b; objective 018 is ACCEPTED at its complete INERT graph/currentness/admission scope WITH PROCESS QUALIFICATIONS AND EXPLICIT IMMUTABLE-REPORT CORRECTIONS (strategic decision `S/reviews/018-t-decision.md`) and merged to main at c5eb299df822875988867bf34d58de239e82657e (018-a
foundation slice ACCEPTED at its bounded inert graph-foundation
scope with process qualifications; 018-b ACCEPTED at its bounded inert
bundle-proof scope with process qualifications; 018-c implemented inert
bundle-admission/identity slice ACCEPTED at its bounded inert
admission/structural-identity scope with process qualifications
(decision `S/reviews/018-c-decision.md`); 018-d implemented inert
causal-occurrence-ledger slice ACCEPTED at its bounded inert
causal-occurrence-ledger scope with process qualifications (decision
`S/reviews/018-d-decision.md`); 018-e implemented inert nonroot
currentness-overlay slice ACCEPTED at its bounded inert
currentness/overlap-overlay scope with process qualifications
(decision `S/reviews/018-e-decision.md` + addendum); 018-f
implemented inert current-graph-closure slice ACCEPTED at its
bounded inert current-graph scope with process qualifications
(decision `S/reviews/018-f-decision.md`); 018-g implemented inert
current-bundle-admission slice ACCEPTED at its bounded inert scope
with process qualifications (strategic decision
`S/reviews/018-g-decision.md`); 018-h implemented inert
root-authority-lineage slice ACCEPTED at its bounded inert
root-authority-lineage scope with process qualifications
(strategic decision `S/reviews/018-h-decision.md`); 018-i
implemented inert current-root-composition slice NOT ACCEPTED
(strategic decision `S/reviews/018-i-decision.md`); the bounded
018-j repairs (J01/J02/J03) were delivered truthfully PARTIAL
and are NOT ACCEPTED against the complete J01/J02/J03 criteria
(strategic decision `S/reviews/018-j-decision.md`); the bounded
018-k repairs (K01/K02/K03) are NOT ACCEPTED against the
complete K01/K02/K03 criteria (strategic decision
`S/reviews/018-k-decision.md`); the bounded 018-l repairs
(L01/L02) were delivered truthfully PARTIAL and are NOT
ACCEPTED against the complete L01/resource/artifact criteria
(strategic decision `S/reviews/018-l-decision.md`); the bounded
018-m repairs (M01 O(1) count / scalar gates BEFORE any element
/ set / sort / hash / serialization work at the leaf and BOTH
parent boundaries, with the closed TEN admission bound-model
fence and the accepted dense group ordering / unique partition
law; M02 the exact accepted JSON serialization byte ceiling and
the reservation-calculation work precharge on the ONE I outer)
were delivered truthfully PARTIAL and are NOT
ACCEPTED against the complete M01/M02 criteria (strategic
decision `S/reviews/018-m-decision.md`); the bounded 018-n
repairs (N01 the retained-content join at the leaf and BOTH
parent boundaries — the entry-local group partition joined to
the ORIGINAL proof segments and the root group to the retained
root digest — plus N02 the byte-aware closed reservation, the
pre-fetch plan segment precharge and the per-site
reservation-calculation closure) are ACCEPTED at their
bounded inert scope WITH PROCESS QUALIFICATIONS
(strategic decision `S/reviews/018-n-decision.md`); the 018-o
root-aware mixed-observation slice (the new pure
`observe_root_lineage_mixed` operation plus
`ROOT_LINEAGE_MIXED_OBSERVATION_VERSION`; a proven mixed root
member matching an independently authoritative known version
of the same effective root — including an independently
issued complete whole singleton in the SAME batch — acquires
source evidence while a mixed read mints no governing
authority, unresolved foreign digests keep the exact
COMPETING_ROOTS refusal, and the pending-set snapshot is
precharged on the SAME H outer) is implemented and
ACCEPTED at its bounded inert scope WITH PROCESS
QUALIFICATIONS (strategic decision
`S/reviews/018-o-decision.md`; root-lineage contract
section 5a); the 018-p versioned root-region authority
producer (the separate `cache-root-region-lineage/v1`/
`root-region-lineage-policy/v1` contract and the
`read_region` provenance kind: a genuinely issued
complete NEW root region in a mixed-only read acquires
source evidence AND authority with NO independent
singleton, the no-exception read shapes, before-
materialization retention under the unchanged H
ceilings, the ONE new-operation outer, the honest old-I
refusal of the region-version state and the closed host-IO
purity surface) is ACCEPTED at its bounded inert producer
scope WITH PROCESS QUALIFICATIONS (strategic decision
`S/reviews/018-p-decision.md`; root-region contract
`docs/CACHE-ROOT-REGION-LINEAGE-CONTRACT.md`); the
018-q versioned root-region currentness slice (a pure
QUERY over the 018-p state — contract
`docs/CACHE-ROOT-REGION-CURRENTNESS-CONTRACT.md`) is
ACCEPTED at its bounded inert query scope WITH PROCESS
QUALIFICATIONS AND HISTORICAL-REPORT CORRECTIONS
(strategic decision `S/reviews/018-q-decision.md`), and
the 018-r consumer slice (contract
`docs/CACHE-ROOT-REGION-GRAPH-CONTRACT.md`) is ACCEPTED at its bounded inert selected-root source/current-graph scope WITH PROCESS QUALIFICATIONS AND EXPLICIT HISTORICAL-REPORT CORRECTIONS (strategic decision `S/reviews/018-r-decision.md`); the 018-s region-compatible admission-models slice (contract `docs/CACHE-ROOT-REGION-ADMISSION-MODELS-CONTRACT.md`) is ACCEPTED at its bounded inert MODEL/LOCAL-BOUNDARY scope WITH PROCESS QUALIFICATIONS AND EXPLICIT HISTORICAL-REPORT CORRECTIONS (strategic decision `S/reviews/018-s-decision.md`); the 018-t complete root-region admission consumer (contract `docs/CACHE-ROOT-REGION-ADMISSION-CONTRACT.md`) is ACCEPTED at its bounded complete-consumer scope WITH PROCESS QUALIFICATIONS AND EXPLICIT IMMUTABLE-REPORT CORRECTIONS (strategic decision `S/reviews/018-t-decision.md`); objective 019 is active (019-a: ACCEPTED at its bounded inert RAM owner/store scope WITH PROCESS QUALIFICATIONS AND IMMUTABLE-REPORT CORRECTIONS (strategic decision `S/reviews/019-a-decision.md`; contract `docs/CACHE-RAM-STATE-CONTRACT.md`); 019-b: delivered bounded async single-flight work plane, NOT ACCEPTED against the complete accounting requirement or whole 019 (strategic decision `S/reviews/019-b-decision.md`; contract `docs/CACHE-RAM-WORK-CONTRACT.md`); 019-c: whole-019 closure at the INERT injected-work layer (the bounded pre-accounted `owner_quarantined` adverse-currentness fence, aggregate pressure with high-water shared-container retention, substantial-source/accumulated-history over ACTUAL accepted records, cancellation/update/teardown races and the denied-filesystem lifecycle proof; `tests/test_bundle_ram_lifecycle.py`) implemented, PENDING strategic review; 020-a: whole-020 protected session recovery component at the INERT recovery-component layer (the versioned closed recovery record, the trusted address-only resume, the protected per-session store with atomic generation publication and the actual committed-outcome fault law, the bounded shared-RAM recovery reservations against the SAME 019 ceilings, the durable epoch binding republished on every resume, the durable fail-closed adverse-quarantine fence, the owned bounded async store IO with drain-before-release cancellation / timeout / teardown, and the lazy once-per-epoch rebuild through the actual 019 work plane; contract `docs/CACHE-RECOVERY-CONTRACT.md`; `tests/test_bundle_recovery_codec.py`, `tests/test_bundle_recovery_store.py`, `tests/test_bundle_recovery_resume.py`); 020-b: the 020-a ownership / fault corrections at the same inert scope (the single-writer CAS / publication serialization, the typed read-back `io_failure` law with the BEST actual observed generation, and the claimed-owner fence closing the preemption gap on both direct teardown paths) implemented, PENDING strategic review; 021-a: the 021 component stage (the pinned actual Qwen3.8-27B CPU tokenizer with the closed digest-pinned asset table and load-once identity, the explicit validated C/32 slot / width x slot / aggregate floor(C/4) / reserve budgets with real-tokenizer counting, the direct authenticated tool-free non-recursive compiler with the no-retry/compile-once law, the compile-through-RAM composition with the configured-policy fingerprint fence, and the deterministic required-then-optional selection; contract `docs/CACHE-TOKEN-COMPILER-CONTRACT.md`; `tests/test_bundle_tokenizer.py`, `tests/test_bundle_budget.py`, `tests/test_bundle_compiler.py`, `tests/test_bundle_compile_work.py`, `tests/test_bundle_selection.py`) ACCEPTED at its bounded inert component scope (whole 021 accepted, PR 29 merged to main at 144af0bd5e34387afcb8e3f9ddf761eabd56e817, per the 022 order). Objective 022 is active (022-a: the validated opt-in cache configuration slice (the explicit `[context_cache]` profile selector on the actual `Settings` and TOML loader, the closed typed v1 configuration reusing the accepted 021 budget/compiler and 019 RAM types, the strict one-worker policy, the legacy/v1 migration conflict law, the governed-route model contracts and the fixed `create_app` v1 startup refusal; `tests/test_config.py`, `tests/test_app.py`) implemented at the INERT configuration layer, MERGED to main through PR #30 at 4319049d91428b8995e83db82b1736ed36626a12, reviewed at its bounded configuration scope; 022-b: the pure exact-span source replacement
transaction (the versioned
`cache-bundle-replace/v1` policy-12 transaction
over the ACTUAL 017/018/019/021 records: the
retained/current proof join through each retained
witness's own owner proof, the closed root/read
carrier law with the read-root no-double-edit
fence, the two versioned opaque HMAC marker kinds
with the closed replay scan gate, the positive-
supersession evidence law with the eligible-
source constraint, the narrow durable-generation
handoff and the plan-13 typed all-or-nothing
failures; `tests/test_bundle_replace.py`)
implemented at the INERT pure-transaction layer,
MERGED to main through PR #30 at 4319049d91428b8995e83db82b1736ed36626a12, reviewed at its bounded pure-
transaction scope; 022-c: the v1 application
transaction on the ACTUAL `create_app` entry
point (the closed historical read-root replay
gap, the marker pre-check before raw
acquisition, the single outgoing transformed
body at the byte-identical fixed point, the
per-request FROZEN represented-frontier
trusted issuance binding over the ACTUAL
direct main upstream response — actual
nonstream and split-SSE, never compiler
traffic, never rebased — the pre-forward
protected generation with the retained publish
bound to the exact snapshot/epoch it actually
published (a faulted publication keeps the
prior bound; the newer undurable record set is
refused on replay, never forwarded under the
stale proof), the fixed typed v1 refusal family
with no raw fallback, and the application-
owned private marker key as a protected
environment reference resolved once at runtime;
`tests/test_app.py`, `tests/test_v1_application.py`)
implemented at the APPLICATION-TRANSACTION
layer, active on opted-in v1 routes (at its
bounded fake-upstream application scope),
MERGED to main through PR #30 at 4319049d91428b8995e83db82b1736ed36626a12, reviewed; 022-d: the v1
application closure on the same ACTUAL
`create_app` entry point (the closed COLD
marker/source-carrier gate BEFORE any cold
raw acquisition, owner allocation or
checkpoint — the fixed typed 409 with zero
new owner, generation, compile or main
forward, ordinary non-source marker-shaped
text staying data, the cross-namespace
cold marker refused under its own distinct
MAC and the later legitimate bootstrap
succeeding — correcting the 022-c cold path;
the accepted 020 `admit_with_fence` on BOTH
cold and steady-state transitions with the
safe prepublication cleanup, the same-
process fail-closed fenced-epoch retry and
the fresh-process idempotent same-
generation orphan re-publication —
correcting the 022-c cold admit plus
separate checkpoint; the root-currentness
409 with zero main forward and no bootstrap
fallback; the compiled-context injection at
the endpoint-specific stable placement
(Responses `instructions`, Chat first
string-content system message else inserted
at the front); the Chat endpoint evidence
(endpoint-in-binding law: a responses-
issued read cannot complete on chat, root
authority Responses-only, actual nonstream
and split-SSE chat issuance); the source-
change law at the app boundary (issued re-
read: EVIDENCE on the superseded original's
retained carrier, LIVE on the new carrier,
the stale OLD transformed body refused 409
marker-side with no forward, the genuine
same-digest revert live again without
recompile); the compiler/budget failure
law at the app boundary (the typed fence
before retention, the terminal failure
re-served same-epoch with no retry, fresh-
process recovery in a new epoch, the 422
selection fence the last line of defense);
stream disconnect closes the upstream; the
ungoverned route forwards byte-identical;
and the fixed typed v1 refusal family at
the app boundary with no raw fallback;
`tests/test_app.py`, `tests/test_v1_application.py`)
implemented at the same APPLICATION-
TRANSACTION layer, active on opted-in v1
routes (at its bounded fake-upstream
application scope on both endpoints), MERGED to main through PR #30 at 4319049d91428b8995e83db82b1736ed36626a12, reviewed; 022-e: the v1 wire
closure on the same ACTUAL `create_app`
entry point (the placement-ownership law
for the stable compiled-context region:
a prior rendered region is replacement-
eligible only under its verifying
placement-ownership tag bound to this
complete trusted namespace, this endpoint-
specific placement and this exact rendered
payload (the same protected per-session key
material under a separate MAC domain),
literal delimiter-like caller text stays
data preserved byte-identical, the bounded
left-to-right ownership scan across caller
delimiters (an unauthenticated pair —
complete or unmatched — before the
authentic region never hides it), the
legitimate transformed replay is the
byte-identical fixed point and a version
change or reduced history carries exactly
the current compiled working set without
duplicating a verified old region; the
accepted budget on the actual final
outgoing request: the supported endpoint
generation fields (Responses
`max_output_tokens`, Chat `max_tokens`)
honored as-is (a malformed or context-
exceeding value is the fixed typed 422
before any compile or main forward), the
real pinned-tokenizer count of the
remaining text / tools / request structure
and retained images counted ONCE under the
accepted envelope and capacity semantics
(the closed mapper for the supported
Responses and Chat shapes — the typed or
easy message, the plain string input and
the bare content parts as plain user text,
the bare retained image part as a capacity
consumer — any other shape the fixed
typed 422, an explicit null instructions
carrying none) plus the actual final
rendered governance (framing, guides and
metadata) counted once against the
aggregate, the fixed typed 422 before any
main forward, and the deterministic
whole-entry OPTIONAL omission (lowest
priority first, required governance never
omitted, the coherent replacement/
selection re-run with no dangling
proof (accepted signatures reach the
actual v1 path and its fake upstream
under the correct namespace, the signed
route mismatch the fixed 403 before any
v1 work, and distinct similarly-populated
sessions isolated under their own
namespace-scoped markers); `tests/test_app.py`,
`tests/test_v1_application.py`,
`tests/test_bundle_selection.py`)
implemented at the same APPLICATION-
TRANSACTION layer, active on opted-in v1
routes (at its bounded fake-upstream
application scope on both endpoints),
MERGED to main through PR #30 at 4319049d91428b8995e83db82b1736ed36626a12, reviewed; 022-f: the v1 wire
budget and replay completion on the
same ACTUAL `create_app` entry point
(the Chat effective generation field:
a non-null `max_completion_tokens`
takes precedence over `max_tokens`
(null or absent the fallback), the
existing typed 422 and capacity checks
on the effective value before any
compile or main forward, both fields
preserved on the valid request's wire,
and the Responses `max_output_tokens`
behavior retained; the tag-verified
single-pass ownership span (a literal
closing delimiter inside a valid
compiled block cannot bound, split or
duplicate the owned span — the body boundary is
proven by the authenticating MAC, never a
literal footer search — so literal
delimiters anywhere in the rendered
content are data: one region and the
byte-identical fixed-point replay on
both endpoints); and the app-boundary
formatting-pressure whole-entry
OPTIONAL omission (the combined final
blocks fit the aggregate while the
framed region crosses it: the
lowest-priority optional omitted whole
with no dangling reference — the omitted
carrier earns the non-resolving
evidence marker, the root carrier the
live marker, and the omitted compiled
content never reaches the wire — and the
resend of the own transformed body
validates its own valid marker decision
as the byte-identical fixed point with
zero recompile, the selected span's
decision-stable evidence expectation
authenticating the marker decision the
final budget gate made); `tests/test_app.py`)
implemented at the same APPLICATION-
TRANSACTION layer, active on opted-in v1
routes (at its bounded fake-upstream
application scope on both endpoints),
MERGED to main through PR #30 at 4319049d91428b8995e83db82b1736ed36626a12, reviewed; 022-g: the v1 emitted-envelope and deterministic placement frame on the same ACTUAL `create_app` entry point (the emitted-envelope accounting: the transaction counts the remaining request and the actual final rendered governance of the ACTUAL emitted final payload (the final outgoing body after the stable placement) — deriving the ordinary-content view from the final payload and excluding the exact authenticated governance span only, keeping the complete system frame and separators, the byte/token/item bounds and the separate compiled aggregate, tool, image and generation reserves — with actual-app first-over and in-bound controls (equal first/replay disposition and byte-stable output at the accepted message limit, exercising the newly inserted Responses instructions and the Chat system frame) and the accepted whole optional omission replay and v1 failure/status behavior preserved; and the DETERMINISTIC placement frame (the opening delimiter directly carries the fixed-width claim — the zero-padded body CHARACTER length and the closed canonical opaque under the distinct claim purpose of the placement domain on the same protected per-session key material — authenticated IN PLACE before any body copy, the ONE closing position located from the authenticated length, every wire separator verified as the actual newline of the input and the exact body verified by the existing placement-ownership tag over the ACTUAL wire bytes, so an otherwise-valid single emitted frame verifies by construction: the total verification of admitted candidate bodies is charged before the body copy at the conservative UTF-8 byte bound and closed by a cap derived from the actual configured compiled-render budget (the whole framed region's compiled-block byte limit plus the fixed framing skeleton), a field carrying more than one legitimate frame's worth of admitted bodies is the fixed typed over-bound transform refusal (never a silent no-ownership prepend, never a raw forward), a valid frame may follow ordinary caller text, literal delimiter-like caller text stays data preserved byte-identical and the legitimate transformed replay stays the byte-identical fixed point on both endpoints); `tests/test_app.py`) implemented at the same APPLICATION-TRANSACTION layer, active on opted-in v1 routes (at its bounded fake-upstream application scope on both endpoints), MERGED to main through PR #30 at 4319049d91428b8995e83db82b1736ed36626a12, reviewed; 023-a: the v1 stage-telemetry and protected synthetic application evidence slice on the same ACTUAL `create_app` entry point (the owned-stage content-free stage facts (recognition, complete acquisition, the actual same-run graph, admission, compilation, replacement, compiled injection, source-absent injection, recovery, main upstream and the closed four-way reuse class) recorded at each owning stage from the ACTUAL typed results with closed per-stage outcome and detail vocabularies (content-free by construction: bounded counts only, never values, source, identifiers, paths, digests or credentials), the closed acquisition facts (the complete/partial/unsupported read partition, the observed member and character counts, the absolute-path normalization outcome) and the actual same-run R/F graph facts (the closed honest node-availability partition, the edge count and the candidate count) published through the existing private metrics registry with fixed labels (revision/epoch evidence out of metric labels), the actual final-envelope injection token measurements as histogram samples against the configured aggregate-limit gauge, the send-boundary main-forward classification (provider acceptance only on 2xx, transport errors, refusals and cancellation distinct), the backend provider usage ledger independent of client-reported usage, the closed original-present RAM reuse / source-absent injection / restart-rebuild-new-epoch distinction (genuine client compaction closed but UN-EARNED), and the protected synthetic stage evidence assembled by the TEST HARNESS from its own fake-upstream / compiler captures (no raw-content persistence surface in the runtime); `v1_telemetry.py`, `tests/test_app.py`, `tests/test_v1_application.py`) implemented at the same APPLICATION-TRANSACTION layer, active on opted-in v1 routes (at its bounded fake-upstream application scope), PENDING strategic review at its bounded stage-telemetry scope; 023-b: the v1 application content, currentness and authority slice (the 023 negative-path/stress-test matrix content, currentness and authority cases) on the same ACTUAL `create_app` entry point (the G01/G02 recursive nested referring-directory, repeated-reference and cycle closure through actual supported observations (the ACTUAL same-run graph fixed point with repeated edges deduplicated, the separate root/file compiler demands with the ACTUAL source content, and the byte-identical transformed-round fixed point with zero recompile); the O01 missing-P1-binding forwarded read guidance and its disappearance with the acquired binding (the incomplete dependency result even when root compilation succeeds); the G03/G05 mixed-bundle lean refusal and greedy background provenance (no authority escalation, no governing reachability expansion); the G04 unrelated-only refusal in both modes; the C01/C02 singleton and ordered entry identities with repeated membership and the C06 boundaryless-unknown-member-versions law at the app boundary (a genuinely descendant standalone read stales the older boundaryless group as UNPROVEN_OWNERSHIP — the stale group earns NEITHER an evidence marker NOR an unsplice: its raw carrier stays ordinary data while the group block is withdrawn — and a resent OLD transformed body with the stale live reference over that group is the fixed marker-side 409 with no forward, the current body staying the byte-identical fixed point with zero recompile); the D controls at the app boundary (a genuinely issued read the finite grammar cannot earn — the wildcard operand — is typed unsupported and acquires nothing, and a duplicate call ID colliding with an eligible read makes that read typed non-removable with no invented pairing; the endpoint-scope and root-currentness scope conflicts keep the 022-d typed behavior); and the S01 repository-half no-cross-reuse (two apps with distinct repository identities and IDENTICAL filenames/content compile their own working sets independently under their own namespaces; the principal/session halves are the 022-d/022-e isolation controls); `tests/test_app.py` (TestV1ContentCurrentnessMatrix)) implemented at the same APPLICATION-TRANSACTION layer, active on opted-in v1 routes (at its bounded fake-upstream application scope), PENDING strategic review at its bounded application content/currentness/authority scope; 023-c: the v1 application recovery, resource bounds and concurrency slice (the 023 negative-path/stress-test matrix recovery, resource and concurrency cases) on the same ACTUAL `create_app` entry point (the C03/M04 bounded actual concurrency (the simultaneous identical miss with ONE actual compiler dispatch (the leader) while the second is the ACTUAL single-flight subscriber (the closed ``joined`` work outcome, zero invocations), the retained root entry the RAM hit for both, both forward the identical transformed body, ONE live owner and the same-session publication committing the protected generation exactly once, the cancellation case keeping the leader's live work and the affected session's retained entry, and another session's survival while the affected session fails or closes); the M01/M02/O03 real process-boundary restart over the same protected test store (the bounded Python-only harness preparing MORE THAN ONE persisted session in ONE process and a FRESH process resuming ONLY the requested session from its trusted address alone: distinct process IDs, selected-address-only reads, the new epoch and the ACTUAL rebuild compile demand for the persisted dependency absent from the resuming request's own history, the dormant session's COMPLETE file map byte-intact (including the pointer bytes, no additions or deletions), the emitted working set, and the normal hit with the DIRECTLY observed zero recovery-content reads and zero recompile (the recovery-content load and compiler counts unchanged across the request) on the byte-identical fixed point); the M03/M05/B03-B04 app-boundary cases (the corrupt / torn / unsafe-mode (foreign-class) / foreign-record and the configuration-mismatch (the SAME address lineage under a changed accepted compiler-policy configuration -- the compiler-policy fingerprint is an address field, a genuinely distinct session, never a cross-namespace reuse -- over the intact synthetic checkpoint) recovery negatives as the fixed typed `v1_resume_refused` with zero forward, zero new compiler demand and the unchanged committed store state, plus the bounded RAM pressure (the configured per-session ceiling the FIXED typed `v1_publish_refused` with zero forward and zero new compile, the committed protected generation and durable record set preserved, the already-retained other session undisturbed with its live snapshot unchanged and its own transformed body the byte-identical fixed point across the refusal) and the explicit teardown freeing the owned occupancy with both committed protected records intact); the C02 repeated-operand correlation to its one distinct represented path; and the S01 shared-store distinct-repository address-scoped reuse with no cross-repository recovery or source delivery; `tests/test_app.py` (TestV1RecoveryResourceConcurrency), `tests/helpers/v1_restart_harness.py`) implemented at the same APPLICATION-TRANSACTION layer, active on opted-in v1 routes (at its bounded fake-upstream application scope), PENDING strategic review at its bounded application recovery/resource/concurrency scope; 023-d: the v1 whole-objective application acceptance slice (the 023 negative-path/stress-test matrix whole-objective application acceptance) on the same ACTUAL `create_app` entry point (the B01 app-boundary budget evidence for both approved configured contexts (262,144 and 32,768) with one- and two-file admitted entries (the measured 8,192/16,384 and 1,024/2,048 allowances as the ACTUAL working-set bounds: the actual compiler demands carry the exact decoded sources, every emitted compiled block counts within its entry's allowance under the real pinned tokenizer, the raw sources gone from the actual main body, and the byte-identical transformed-round fixed point with zero recompile); the B03 typed request outcomes (the oversized source refused inside the compile attempt BEFORE any provider request — the fixed typed 503 with zero main forward and ZERO compiler provider requests, the bootstrap generation committed with its bound, the same-epoch repeat re-serving the SAME typed refusal with no retry — and the provider truncation typed BEFORE content validation — the fixed typed 503 with zero main forward and exactly ONE compile attempt, the terminal failure re-served same-epoch with no retry, and the fresh app runtime over the same recovery root in a distinct epoch completing the SAME request with exactly one successful compile and the byte-identical fixed point (the separate-process restart is the 023-c evidence); the output-slot half the existing `test_budget_overflow_refuses_then_heals`); the R02 direct forwarded-body evidence on BOTH endpoints (the acquired read carrier with the exact Unicode/CRLF original inside its proven process wrapper the ONLY source span edited — raw original gone, live marker in, wrapper prefix preserved byte-for-byte — the Responses round the retained image (the explicit route behavior) and every other input item dict-equal, the Chat round the user root text data with the assistant tool_calls and the retained image message dict-equal and the stable system placement carrying both compiled entries; the actual compiler demands carry the exact decoded source; the transformed-round replays byte-identical with zero recompile); and the ledger reconciliation binding the B02 final-wire aggregate/whole-entry omission and the B04 changed-config/no-incompatible-reuse claims to the existing named cases; `tests/test_app.py` (TestV1BudgetAndForwardedBodyAcceptance, five cases)) implemented at the same APPLICATION-TRANSACTION layer, active on opted-in v1 routes (at its bounded fake-upstream application scope on both endpoints), PENDING strategic review at its bounded whole-objective application-acceptance scope; R04 native compaction and the 024 actual-model/genuine-Codex stages remain the mandatory unearned v1 implementation stages)). The per-round history (017-a through 017-am) is NOT restated here;
it lives in `docs/CACHE-REWORK-LEDGER.md` and the immutable OAP round
reports `oap/reports/017-*.md`, and the versioned normative contract is
`docs/CACHE-OBSERVATION-CONTRACT.md`.

Current earned scope, inert pure-observation package
`src/slaif_local_coding/constitution/bundles/` (never active in the adapter;
legacy detector unchanged): the D01-D08 root/path/read/result/span observation
slices, plus the D09 process/chunk collector (pure inert slice: the 017-al
collector plus the 017-am already-exited single-final acquisition and the
final-cat execution-evidence contract; observation contract sections 5a and
11q), with the D10 composition matrix and the D09
unsupported/partial negative matrix retained. The binding read-grammar, call/result pairing,
eligibility-independent identity inventory, numeric structural causality,
complete-inventory no-retention preflight bounds and private-ID
representation law is normative in the `Read observation` item of the
`## Dependency-bundle cache law (v1 profile, normative target)` section above,
and is versioned in observation contract section 5 ("Tool call/result pairing
and wrapper (D05)") with the section-8 bound defaults and the section-9
privacy/identity law; the required-syntax acceptance matrix (D01-D10: EARNED /
RECOGNIZED-ONLY / UNSUPPORTED / NOT RUN) is section 11b. The D09 process/
chunk collector is EARNED as a pure inert slice (observation contract section
5a; `tests/test_bundle_process_chunks.py`); the already-exited native
single-final gap is CLOSED at its bounded scope in 017-am (the per-request
count is over completed history, default `max_process_immediate_execs=128`),
and the D09 actual-trace process-completion qualification is qualified AT
BOUNDED SCOPE in 017-am (the original selected AJ frames, hash-verified
record, through the public composition with an explicit carrier conversion,
both endpoints; contract section 11q) — the sleep-bearing stream command
stays a DELIBERATE unearned read grammar (order section 2 requires exactly
this: process completion only, no read acquisition invented for
sleep/sed-style commands), and pinned native frames WITH the token-count
section stay legacy-non-acquiring on the unchanged legacy surface (the
intersection keeps its positive legacy reads for final headers WITHOUT that
section).

Serial native-fixture qualification law (current binding scope; the canonical
per-round normative detail is observation contract sections 11a-11p): one RAM
owner / absolute 1800 s END / cumulative ledger / single 600 s convergence
grace (the grace is convergence, never fresh measurement); the native
current-executable is measured through the existing unprivileged registered-CID
channel as the ACTUAL current bytes with coherent before/after frames and
bounded streaming at exactly 320 MiB (335544320 bytes) / 10 s, clamped at use
to the SAME remaining owner END with no artifact-hash fallback (section 11l;
the original Python 16 MiB / 10 s is section 11h); devpts 96 slave rows /
65536 drained B / 5 s and subject metadata 5 s clamped at use/return, an
expired/equal END refuses (section 11m); sealed-entry canonical-path plus
one-attempt admission, where a changed head/directory/phase never resets the
attempt and the namespace is spent forever (section 11f/11j); the ORIGINAL fixture defaults stay fixed 21001/21002; the owner-UID profile is
selected ONLY by its own verified canonical sealed entries, with strict disjoint
tags and records (disjoint from the original even for equal numeric IDs), and is
never a global switch (each real/effective/saved UID triple internally equal and each GID triple internally equal independently - UID and GID may differ, as in the legal 1001:1002 fake control - with both subject IDs distinct from controller 21001, nonroot 1..4294967294, and expected groups exactly the primary GID), revalidated by comparison at every identity-bound use and never rebased, and no caller flag establishes
measured origin (section 11j); membership is exact registered-CID plus owned
PID/birth lifetimes only (no global host UID/name/argv scan; verified-gone
only; a failed query is not absence; a zero group/session observation is never
authority) (section 11j/11o); confinement is the frozen verified local Unix Docker selection with a frozen per-owner env (the overriding context selection removed, explicit remote selection refused before any mutation), rootfs-readonly private PID/mount/IPC/UTS/network namespaces, no host mounts, cap-drop-ALL / no-new-privileges / seccomp, frozen resource ceilings, and empirical keyring denial under the matching host UID (matching UID is not proof of safe containment) (sections 11a/11j); the expected PTY is a one-shot same-fixture
devpts allocation (never subject-derived / host-devpts / MKDEV) with the node
GID per the measured devpts policy (section 11m); the exact-group stop requires
the measured monitor ON first, `jobs -l` binds the SAME job/birth/Bash/TTY, the
saved TTY attributes are restored TCSANOW with no input flush read back equal,
and physical foreground is separate from a real functional tool-input probe
(section 11p); the native-format selected-capture is a closed own-entry
scenario frozen before startup (at most 8 seed files / 128 KiB whose identity
is retained from the immutable pre-launch seed originals; at most 16 semantic
calls / 20 model POSTs / 16 physical TCP handlers / a 256 KiB TOTAL serialized
outer cap checked before decode/copy); it retains ONLY the exact received
known-synthetic call/result frames byte-verified against those immutable
pre-launch originals (actual IDs, association, wrapper ordering and chunk and
truncation facts), with no reconstruction from digests and no raw unknown
output, no private source, no private-history, no full-request, header, auth,
prompt or schema blob retained; publication keeps the ordered separation (the SAME owner's successful protected retention receipt
FIRST, the protected selected capture record SECOND, the same pending-pass
journal LAST, one-shot, no fresh-path retry; the AJ qualification journal
passes only for an actual cleanup pass + native-ready verdict + strict full
four-case format qualification + protected retention, anything less terminal
FAIL, partial never PASS, a cached finalize never upgrades) (sections
11m-11p). The offline process-capture utility (`scripts/real_client_capture.py`)
is inert and input-gated (no actual capture, collector or model call; section
12.x).

017 current earned/unearned scope and qualified-status lineage (the detailed per-round history, including the software-only observation and native-fixture prerequisite work, is in `docs/CACHE-REWORK-LEDGER.md` and the immutable OAP round reports): the D01-D08 observation slices and the inert native-fixture software (the 17 fixture helpers) are earned at their bounded scopes, with no v1 runtime; the actual native-fixture attempts are at their exact immutable reports - 017-x `oap/reports/017-x-live-python-executable-capability.md` (bounded Python-only capability, closed terminal FAIL), 017-y `oap/reports/017-y-readiness-diagnosis-and-executable-capability.md` (readiness diagnosis, closed PASS, the executable a closed UNKNOWN), 017-ab `oap/reports/017-ab-owner-uid-python-capability-qualification.md` (bounded Python-only capability, closed terminal PASS at diagnostic scope), 017-ad `oap/reports/017-ad-owner-uid-native-handoff-qualification.md` (closed PARTIAL, the ordered native handoff NOT RUN - never PASS, never waived), 017-af `oap/reports/017-af-owner-uid-native-pty-qualification.md` (closed FAILED, one admission spent forever), 017-ah `oap/reports/017-ah-owner-uid-native-pty-requalification.md` (qualified at the bounded diagnostic scope), and 017-aj `oap/reports/017-aj-native-process-format-qualification.md` (qualified the real native format at the bounded reference-fixture scope; the measured native_ready=true verdict is bounded to that attempt); the bounded process qualifications of AH and AJ are preserved by those exact references.  The 017-am round report is `oap/reports/017-am-native-single-and-original-syntax-evidence.md` (whole-objective decision ACCEPTED AT THE BOUNDED PURE-OBSERVATION SCOPE WITH PROCESS QUALIFICATIONS under 017-am, closing numeric 017 for merge; merged to main at ffaabf4b; strategic decision `reviews/017-am-decision.md`); the earlier scoped round decisions (including the AL report `oap/reports/017-al-pure-process-chunk-observation.md`, scoped decision ACCEPTED WITH PROCESS QUALIFICATIONS, all ten SELF checks green) remain binding as recorded.

The D09 actual-trace process-completion qualification is qualified AT
BOUNDED SCOPE in 017-am (contract section 11q; converted carriers, one
qualified record — not an original whole API request and not a new actual
attempt); the sleep-bearing stream command stays a DELIBERATE unearned read
grammar (not a pending requirement); the EACH seven required literal
families and the whole-017 native-single literal audit were concretely
audited in 017-am (families 1-4 earn exact source; families 5/6/7 keep
their exact residual uncertainties, preserved as process qualifications);
no GENERIC native-compatibility or v1 runtime claim is made. Objective
017 is ACCEPTED at the bounded pure-observation scope with process
qualifications and merged to main at ffaabf4b (017-am decision,
`reviews/017-am-decision.md`); objective 018 is ACCEPTED at its complete INERT graph/currentness/admission scope WITH PROCESS QUALIFICATIONS AND EXPLICIT IMMUTABLE-REPORT CORRECTIONS (strategic decision `S/reviews/018-t-decision.md`) and merged to main at c5eb299df822875988867bf34d58de239e82657e (018-a: inert
graph-foundation slice ACCEPTED at its bounded inert
graph-foundation scope with process qualifications, contract
`docs/CACHE-GRAPH-CONTRACT.md`; 018-b: bundle-proof bridge slice
ACCEPTED at its bounded inert bundle-proof scope with process
qualifications, strategic decision `reviews/018-b-decision.md`, contract
`docs/CACHE-BUNDLE-PROOF-CONTRACT.md`; 018-c: implemented inert
bundle-admission and structural-identity slice ACCEPTED at its
bounded inert scope with process qualifications (strategic decision
`S/reviews/018-c-decision.md`, contract
`docs/CACHE-BUNDLE-ADMISSION-CONTRACT.md`); 018-d: implemented inert
causal-occurrence-ledger slice ACCEPTED at its bounded inert
causal-occurrence-ledger scope with process qualifications (strategic
decision `S/reviews/018-d-decision.md`, contract
`docs/CACHE-CAUSAL-HISTORY-CONTRACT.md`); 018-e: implemented inert
nonroot currentness-overlay slice ACCEPTED at its bounded inert
currentness/overlap-overlay scope with process qualifications
(strategic decision `S/reviews/018-e-decision.md` + addendum,
contract `docs/CACHE-CURRENTNESS-CONTRACT.md`); 018-f: implemented
inert current-graph-closure slice ACCEPTED at its bounded inert
current-graph scope with process qualifications (strategic decision
`S/reviews/018-f-decision.md`, contract
`docs/CACHE-CURRENT-GRAPH-CONTRACT.md`); 018-g: implemented inert
current-bundle-admission slice ACCEPTED at its bounded inert scope
with process qualifications (strategic decision
`S/reviews/018-g-decision.md`, contract
`docs/CACHE-CURRENT-ADMISSION-CONTRACT.md`); 018-h: implemented
inert root-authority-lineage slice ACCEPTED at its bounded inert
root-authority-lineage scope with process qualifications
(strategic decision `S/reviews/018-h-decision.md`, contract
`docs/CACHE-ROOT-LINEAGE-CONTRACT.md`); 018-i: implemented inert
current-root-composition slice NOT ACCEPTED (strategic decision
`S/reviews/018-i-decision.md`); the bounded 018-j repairs
(J01/J02/J03) were delivered truthfully PARTIAL and are NOT
ACCEPTED against the complete J01/J02/J03 criteria (strategic
decision `S/reviews/018-j-decision.md`); the bounded 018-k
repairs (K01/K02/K03) are NOT ACCEPTED against the complete
K01/K02/K03 criteria (strategic decision
`S/reviews/018-k-decision.md`); the bounded 018-l repairs
(L01/L02) were delivered truthfully PARTIAL and are NOT
ACCEPTED against the complete L01/resource/artifact criteria
(strategic decision `S/reviews/018-l-decision.md`); the bounded
018-m repairs (M01 O(1) count / scalar gates BEFORE any element
/ set / sort / hash / serialization work at the leaf and BOTH
parent boundaries, with the closed TEN admission bound-model
fence and the accepted dense group ordering / unique partition
law; M02 the exact accepted JSON serialization byte ceiling and
the reservation-calculation work precharge on the ONE I outer)
were delivered truthfully PARTIAL and are NOT
ACCEPTED against the complete M01/M02 criteria (strategic
decision `S/reviews/018-m-decision.md`); the bounded 018-n
repairs (N01 the retained-content join at the leaf and BOTH
parent boundaries — the entry-local group partition joined to
the ORIGINAL proof segments and the root group to the retained
root digest — plus N02 the byte-aware closed reservation, the
pre-fetch plan segment precharge and the per-site
reservation-calculation closure) are ACCEPTED at their
bounded inert scope WITH PROCESS QUALIFICATIONS
(strategic decision `S/reviews/018-n-decision.md`); the 018-o
root-aware mixed-observation slice (the new pure
`observe_root_lineage_mixed` operation plus
`ROOT_LINEAGE_MIXED_OBSERVATION_VERSION`; a proven mixed root
member matching an independently authoritative known version
of the same effective root — including an independently
issued complete whole singleton in the SAME batch — acquires
source evidence while a mixed read mints no governing
authority, unresolved foreign digests keep the exact
COMPETING_ROOTS refusal, and the pending-set snapshot is
precharged on the SAME H outer) is implemented and
ACCEPTED at its bounded inert scope WITH PROCESS
QUALIFICATIONS (strategic decision
`S/reviews/018-o-decision.md`; root-lineage contract
section 5a); the 018-p versioned root-region authority
producer (the separate `cache-root-region-lineage/v1`/
`root-region-lineage-policy/v1` contract and the
`read_region` provenance kind: a genuinely issued
complete NEW root region in a mixed-only read acquires
source evidence AND authority with NO independent
singleton, the no-exception read shapes, before-
materialization retention under the unchanged H
ceilings, the ONE new-operation outer, the honest old-I
refusal of the region-version state and the closed host-IO
purity surface) is ACCEPTED at its bounded inert producer
scope WITH PROCESS QUALIFICATIONS (strategic decision
`S/reviews/018-p-decision.md`; root-region contract
`docs/CACHE-ROOT-REGION-LINEAGE-CONTRACT.md`); the
018-q versioned root-region currentness slice (a pure
QUERY over the 018-p state — contract
`docs/CACHE-ROOT-REGION-CURRENTNESS-CONTRACT.md`) is
ACCEPTED at its bounded inert query scope WITH PROCESS
QUALIFICATIONS AND HISTORICAL-REPORT CORRECTIONS
(strategic decision `S/reviews/018-q-decision.md`), and
the 018-r consumer slice (contract
`docs/CACHE-ROOT-REGION-GRAPH-CONTRACT.md`) is ACCEPTED at its bounded inert selected-root source/current-graph scope WITH PROCESS QUALIFICATIONS AND EXPLICIT HISTORICAL-REPORT CORRECTIONS (strategic decision `S/reviews/018-r-decision.md`); the 018-s region-compatible admission-models slice (contract `docs/CACHE-ROOT-REGION-ADMISSION-MODELS-CONTRACT.md`) is ACCEPTED at its bounded inert MODEL/LOCAL-BOUNDARY scope WITH PROCESS QUALIFICATIONS AND EXPLICIT HISTORICAL-REPORT CORRECTIONS (strategic decision `S/reviews/018-s-decision.md`); the 018-t complete root-region admission consumer (contract `docs/CACHE-ROOT-REGION-ADMISSION-CONTRACT.md`) is ACCEPTED at its bounded complete-consumer scope WITH PROCESS QUALIFICATIONS AND EXPLICIT IMMUTABLE-REPORT CORRECTIONS (strategic decision `S/reviews/018-t-decision.md`); objective 019 is active (019-a: ACCEPTED at its bounded inert RAM owner/store scope WITH PROCESS QUALIFICATIONS AND IMMUTABLE-REPORT CORRECTIONS (strategic decision `S/reviews/019-a-decision.md`; contract `docs/CACHE-RAM-STATE-CONTRACT.md`); 019-b: delivered bounded async single-flight work plane, NOT ACCEPTED against the complete accounting requirement or whole 019 (strategic decision `S/reviews/019-b-decision.md`; contract `docs/CACHE-RAM-WORK-CONTRACT.md`); 019-c: whole-019 closure at the INERT injected-work layer (the bounded pre-accounted `owner_quarantined` adverse-currentness fence, aggregate pressure with high-water shared-container retention, substantial-source/accumulated-history over ACTUAL accepted records, cancellation/update/teardown races and the denied-filesystem lifecycle proof; `tests/test_bundle_ram_lifecycle.py`) implemented, PENDING strategic review; 020-a: whole-020 protected session recovery component at the INERT recovery-component layer (the versioned closed recovery record, the trusted address-only resume, the protected per-session store with atomic generation publication and the actual committed-outcome fault law, the bounded shared-RAM recovery reservations against the SAME 019 ceilings, the durable epoch binding republished on every resume, the durable fail-closed adverse-quarantine fence, the owned bounded async store IO with drain-before-release cancellation / timeout / teardown, and the lazy once-per-epoch rebuild through the actual 019 work plane; contract `docs/CACHE-RECOVERY-CONTRACT.md`; `tests/test_bundle_recovery_codec.py`, `tests/test_bundle_recovery_store.py`, `tests/test_bundle_recovery_resume.py`); 020-b: the 020-a ownership / fault corrections at the same inert scope (the single-writer CAS / publication serialization, the typed read-back `io_failure` law with the BEST actual observed generation, and the claimed-owner fence closing the preemption gap on both direct teardown paths) implemented, PENDING strategic review; 021-a: the 021 component stage (the pinned actual Qwen3.8-27B CPU tokenizer with the closed digest-pinned asset table and load-once identity, the explicit validated C/32 slot / width x slot / aggregate floor(C/4) / reserve budgets with real-tokenizer counting, the direct authenticated tool-free non-recursive compiler with the no-retry/compile-once law, the compile-through-RAM composition with the configured-policy fingerprint fence, and the deterministic required-then-optional selection; contract `docs/CACHE-TOKEN-COMPILER-CONTRACT.md`; `tests/test_bundle_tokenizer.py`, `tests/test_bundle_budget.py`, `tests/test_bundle_compiler.py`, `tests/test_bundle_compile_work.py`, `tests/test_bundle_selection.py`) ACCEPTED at its bounded inert component scope (whole 021 accepted, PR 29 merged to main at 144af0bd5e34387afcb8e3f9ddf761eabd56e817, per the 022 order); objective 022 is active (022-a: the validated opt-in cache configuration slice (the explicit `[context_cache]` profile selector on the actual `Settings` and TOML loader, the closed typed v1 configuration reusing the accepted 021 budget/compiler and 019 RAM types, the strict one-worker policy, the legacy/v1 migration conflict law, the governed-route model contracts and the fixed `create_app` v1 startup refusal; `tests/test_config.py`, `tests/test_app.py`) implemented at the INERT configuration layer, MERGED to main through PR #30 at 4319049d91428b8995e83db82b1736ed36626a12, reviewed at its bounded configuration scope; 022-b: the pure exact-span source replacement transaction (the versioned `cache-bundle-replace/v1` policy-12 transaction over the ACTUAL 017/018/019/021 records: the retained/current proof join through each retained witness's own owner proof, the closed root/read carrier law with the read-root no-double-edit fence, the two versioned opaque HMAC marker kinds with the closed replay scan gate, the positive-supersession evidence law with the eligible-source constraint, the narrow durable-generation handoff and the plan-13 typed all-or-nothing failures; `tests/test_bundle_replace.py`) implemented at the INERT pure-transaction layer, MERGED to main through PR #30 at 4319049d91428b8995e83db82b1736ed36626a12, reviewed at its bounded pure-transaction scope; 022-c: the v1 application transaction on the ACTUAL `create_app` entry point (the closed historical read-root replay gap, the marker pre-check before raw acquisition, the single outgoing transformed body at the byte-identical fixed point, the per-request FROZEN represented-frontier trusted issuance binding over the ACTUAL direct main upstream response — actual nonstream and split-SSE, never compiler traffic, never rebased — the pre-forward protected generation with the retained publish bound to the exact snapshot/epoch it actually published (a faulted publication keeps the prior bound; the newer undurable record set is refused on replay, never forwarded under the stale proof), the fixed typed v1 refusal family with no raw fallback, and the application-owned private marker key as a protected environment reference resolved once at runtime; `tests/test_app.py`, `tests/test_v1_application.py`) implemented at the APPLICATION-TRANSACTION layer, active on opted-in v1 routes (at its bounded fake-upstream application scope), MERGED to main through PR #30 at 4319049d91428b8995e83db82b1736ed36626a12, reviewed; 022-d: the v1 application closure on the same ACTUAL `create_app` entry point (the closed COLD marker/source-carrier gate BEFORE any cold raw acquisition, owner allocation or checkpoint — the fixed typed 409 with zero new owner, generation, compile or main forward, ordinary non-source marker-shaped text staying data, the cross-namespace cold marker refused under its own distinct MAC and the later legitimate bootstrap succeeding — correcting the 022-c cold path; the accepted 020 `admit_with_fence` on BOTH cold and steady-state transitions with the safe prepublication cleanup, the same-process fail-closed fenced-epoch retry and the fresh-process idempotent same-generation orphan re-publication — correcting the 022-c cold admit plus separate checkpoint; the root-currentness 409 with zero main forward and no bootstrap fallback; the compiled-context injection at the endpoint-specific stable placement (Responses `instructions`, Chat first string-content system message else inserted at the front); the Chat endpoint evidence (endpoint-in-binding law: a responses-issued read cannot complete on chat, root authority Responses-only, actual nonstream and split-SSE chat issuance); the source-change law at the app boundary (issued re-read: EVIDENCE on the superseded original's retained carrier, LIVE on the new carrier, the stale OLD transformed body refused 409 marker-side with no forward, the genuine same-digest revert live again without recompile); the compiler/budget failure law at the app boundary (the typed fence before retention, the terminal failure re-served same-epoch with no retry, fresh-process recovery in a new epoch, the 422 selection fence the last line of defense); stream disconnect closes the upstream; the ungoverned route forwards byte-identical; and the fixed typed v1 refusal family at the app boundary with no raw fallback; `tests/test_app.py`, `tests/test_v1_application.py`) implemented at the same APPLICATION-TRANSACTION layer, active on opted-in v1 routes (at its bounded fake-upstream application scope on both endpoints), MERGED to main through PR #30 at 4319049d91428b8995e83db82b1736ed36626a12, reviewed; 022-e: the v1 wire closure on the same ACTUAL `create_app` entry point (the placement-ownership law for the stable compiled-context region: a prior rendered region is replacement-eligible only under its verifying placement-ownership tag bound to this complete trusted namespace, this endpoint-specific placement and this exact rendered payload (the same protected per-session key material under a separate MAC domain), literal delimiter-like caller text stays data preserved byte-identical, the bounded left-to-right ownership scan across caller delimiters (an unauthenticated pair — complete or unmatched — before the authentic region never hides it), the legitimate transformed replay is the byte-identical fixed point and a version change or reduced history carries exactly the current compiled working set without duplicating a verified old region; the accepted budget on the actual final outgoing request: the supported endpoint generation fields (Responses `max_output_tokens`, Chat `max_tokens`) honored as-is (a malformed or context-exceeding value is the fixed typed 422 before any compile or main forward), the real pinned-tokenizer count of the remaining text / tools / request structure and retained images counted ONCE under the accepted envelope and capacity semantics (the closed mapper for the supported Responses and Chat shapes — the typed or easy message, the plain string input and the bare content parts as plain user text, the bare retained image part as a capacity consumer — any other shape the fixed typed 422, an explicit null instructions carrying none) plus the actual final rendered governance (framing, guides and metadata) counted once against the aggregate, the fixed typed 422 before any main forward, and the deterministic whole-entry OPTIONAL omission (lowest priority first, required governance never omitted, the coherent replacement/selection re-run with no dangling reference); and the signed-v1 application proof (accepted signatures reach the actual v1 path and its fake upstream under the correct namespace, the signed route mismatch the fixed 403 before any v1 work, and distinct similarly-populated sessions isolated under their own namespace-scoped markers); `tests/test_app.py`, `tests/test_v1_application.py`, `tests/test_bundle_selection.py`) implemented at the same APPLICATION-TRANSACTION layer, active on opted-in v1 routes (at its bounded fake-upstream application scope on both endpoints), MERGED to main through PR #30 at 4319049d91428b8995e83db82b1736ed36626a12, reviewed; 022-f: the v1 wire budget and replay completion on the same ACTUAL `create_app` entry point (the Chat effective generation field: a non-null `max_completion_tokens` takes precedence over `max_tokens` (null or absent the fallback), the existing typed 422 and capacity checks on the effective value before any compile or main forward, both fields preserved on the valid request's wire, and the Responses `max_output_tokens` behavior retained; the tag-verified single-pass ownership span (a literal closing delimiter inside a valid compiled block cannot bound, split or duplicate the owned span — the body boundary is proven by the authenticating MAC, never a literal footer search — so literal delimiters anywhere in the rendered content are data: one region and the byte-identical fixed-point replay on both endpoints); and the app-boundary formatting-pressure whole-entry OPTIONAL omission (the combined final blocks fit the aggregate while the framed region crosses it: the lowest-priority optional omitted whole with no dangling reference — the omitted carrier earns the non-resolving evidence marker, the root carrier the live marker, and the omitted compiled content never reaches the wire — and the resend of the own transformed body validates its own valid marker decision as the byte-identical fixed point with zero recompile, the selected span's decision-stable evidence expectation authenticating the marker decision the final budget gate made); `tests/test_app.py`) implemented at the same APPLICATION-TRANSACTION layer, active on opted-in v1 routes (at its bounded fake-upstream application scope on both endpoints), MERGED to main through PR #30 at 4319049d91428b8995e83db82b1736ed36626a12, reviewed; 022-g: the v1 emitted-envelope and deterministic placement frame on the same ACTUAL `create_app` entry point (the emitted-envelope accounting: the transaction counts the remaining request and the actual final rendered governance of the ACTUAL emitted final payload (the final outgoing body after the stable placement) — deriving the ordinary-content view from the final payload and excluding the exact authenticated governance span only, keeping the complete system frame and separators, the byte/token/item bounds and the separate compiled aggregate, tool, image and generation reserves — with actual-app first-over and in-bound controls (equal first/replay disposition and byte-stable output at the accepted message limit, exercising the newly inserted Responses instructions and the Chat system frame) and the accepted whole optional omission replay and v1 failure/status behavior preserved; and the DETERMINISTIC placement frame (the opening delimiter directly carries the fixed-width claim — the zero-padded body CHARACTER length and the closed canonical opaque under the distinct claim purpose of the placement domain on the same protected per-session key material — authenticated IN PLACE before any body copy, the ONE closing position located from the authenticated length, every wire separator verified as the actual newline of the input and the exact body verified by the existing placement-ownership tag over the ACTUAL wire bytes, so an otherwise-valid single emitted frame verifies by construction: the total verification of admitted candidate bodies is charged before the body copy at the conservative UTF-8 byte bound and closed by a cap derived from the actual configured compiled-render budget (the whole framed region's compiled-block byte limit plus the fixed framing skeleton), a field carrying more than one legitimate frame's worth of admitted bodies is the fixed typed over-bound transform refusal (never a silent no-ownership prepend, never a raw forward), a valid frame may follow ordinary caller text, literal delimiter-like caller text stays data preserved byte-identical and the legitimate transformed replay stays the byte-identical fixed point on both endpoints); `tests/test_app.py`) implemented at the same APPLICATION-TRANSACTION layer, active on opted-in v1 routes (at its bounded fake-upstream application scope on both endpoints), MERGED to main through PR #30 at 4319049d91428b8995e83db82b1736ed36626a12, reviewed; 023-a: the v1 stage-telemetry and protected synthetic application evidence slice on the same ACTUAL `create_app` entry point (the owned-stage content-free stage facts (recognition, complete acquisition, the actual same-run graph, admission, compilation, replacement, compiled injection, source-absent injection, recovery, main upstream and the closed four-way reuse class) recorded at each owning stage from the ACTUAL typed results with closed per-stage outcome and detail vocabularies (content-free by construction: bounded counts only, never values, source, identifiers, paths, digests or credentials), the closed acquisition facts (the complete/partial/unsupported read partition, the observed member and character counts, the absolute-path normalization outcome) and the actual same-run R/F graph facts (the closed honest node-availability partition, the edge count and the candidate count) published through the existing private metrics registry with fixed labels (revision/epoch evidence out of metric labels), the actual final-envelope injection token measurements as histogram samples against the configured aggregate-limit gauge, the send-boundary main-forward classification (provider acceptance only on 2xx, transport errors, refusals and cancellation distinct), the backend provider usage ledger independent of client-reported usage, the closed original-present RAM reuse / source-absent injection / restart-rebuild-new-epoch distinction (genuine client compaction closed but UN-EARNED), and the protected synthetic stage evidence assembled by the TEST HARNESS from its own fake-upstream / compiler captures (no raw-content persistence surface in the runtime); `v1_telemetry.py`, `tests/test_app.py`, `tests/test_v1_application.py`) implemented at the same APPLICATION-TRANSACTION layer, active on opted-in v1 routes (at its bounded fake-upstream application scope), PENDING strategic review at its bounded stage-telemetry scope; 023-b: the v1 application content, currentness and authority slice (the 023 negative-path/stress-test matrix content, currentness and authority cases) on the same ACTUAL `create_app` entry point (the G01/G02 recursive nested referring-directory, repeated-reference and cycle closure through actual supported observations (the ACTUAL same-run graph fixed point with repeated edges deduplicated, the separate root/file compiler demands with the ACTUAL source content, and the byte-identical transformed-round fixed point with zero recompile); the O01 missing-P1-binding forwarded read guidance and its disappearance with the acquired binding (the incomplete dependency result even when root compilation succeeds); the G03/G05 mixed-bundle lean refusal and greedy background provenance (no authority escalation, no governing reachability expansion); the G04 unrelated-only refusal in both modes; the C01/C02 singleton and ordered entry identities with repeated membership and the C06 boundaryless-unknown-member-versions law at the app boundary (a genuinely descendant standalone read stales the older boundaryless group as UNPROVEN_OWNERSHIP — the stale group earns NEITHER an evidence marker NOR an unsplice: its raw carrier stays ordinary data while the group block is withdrawn — and a resent OLD transformed body with the stale live reference over that group is the fixed marker-side 409 with no forward, the current body staying the byte-identical fixed point with zero recompile); the D controls at the app boundary (a genuinely issued read the finite grammar cannot earn — the wildcard operand — is typed unsupported and acquires nothing, and a duplicate call ID colliding with an eligible read makes that read typed non-removable with no invented pairing; the endpoint-scope and root-currentness scope conflicts keep the 022-d typed behavior); and the S01 repository-half no-cross-reuse (two apps with distinct repository identities and IDENTICAL filenames/content compile their own working sets independently under their own namespaces; the principal/session halves are the 022-d/022-e isolation controls); `tests/test_app.py` (TestV1ContentCurrentnessMatrix)) implemented at the same APPLICATION-TRANSACTION layer, active on opted-in v1 routes (at its bounded fake-upstream application scope), PENDING strategic review at its bounded application content/currentness/authority scope; 023-c: the v1 application recovery, resource bounds and concurrency slice (the 023 negative-path/stress-test matrix recovery, resource and concurrency cases) on the same ACTUAL `create_app` entry point (the C03/M04 bounded actual concurrency (the simultaneous identical miss with ONE actual compiler dispatch (the leader) while the second is the ACTUAL single-flight subscriber (the closed ``joined`` work outcome, zero invocations), the retained root entry the RAM hit for both, both forward the identical transformed body, ONE live owner and the same-session publication committing the protected generation exactly once, the cancellation case keeping the leader's live work and the affected session's retained entry, and another session's survival while the affected session fails or closes); the M01/M02/O03 real process-boundary restart over the same protected test store (the bounded Python-only harness preparing MORE THAN ONE persisted session in ONE process and a FRESH process resuming ONLY the requested session from its trusted address alone: distinct process IDs, selected-address-only reads, the new epoch and the ACTUAL rebuild compile demand for the persisted dependency absent from the resuming request's own history, the dormant session's COMPLETE file map byte-intact (including the pointer bytes, no additions or deletions), the emitted working set, and the normal hit with the DIRECTLY observed zero recovery-content reads and zero recompile (the recovery-content load and compiler counts unchanged across the request) on the byte-identical fixed point); the M03/M05/B03-B04 app-boundary cases (the corrupt / torn / unsafe-mode (foreign-class) / foreign-record and the configuration-mismatch (the SAME address lineage under a changed accepted compiler-policy configuration -- the compiler-policy fingerprint is an address field, a genuinely distinct session, never a cross-namespace reuse -- over the intact synthetic checkpoint) recovery negatives as the fixed typed `v1_resume_refused` with zero forward, zero new compiler demand and the unchanged committed store state, plus the bounded RAM pressure (the configured per-session ceiling the FIXED typed `v1_publish_refused` with zero forward and zero new compile, the committed protected generation and durable record set preserved, the already-retained other session undisturbed with its live snapshot unchanged and its own transformed body the byte-identical fixed point across the refusal) and the explicit teardown freeing the owned occupancy with both committed protected records intact); the C02 repeated-operand correlation to its one distinct represented path; and the S01 shared-store distinct-repository address-scoped reuse with no cross-repository recovery or source delivery; `tests/test_app.py` (TestV1RecoveryResourceConcurrency), `tests/helpers/v1_restart_harness.py`) implemented at the same APPLICATION-TRANSACTION layer, active on opted-in v1 routes (at its bounded fake-upstream application scope), PENDING strategic review at its bounded application recovery/resource/concurrency scope; 023-d: the v1 whole-objective application acceptance slice (the 023 negative-path/stress-test matrix whole-objective application acceptance) on the same ACTUAL `create_app` entry point (the B01 app-boundary budget evidence for both approved configured contexts (262,144 and 32,768) with one- and two-file admitted entries (the measured 8,192/16,384 and 1,024/2,048 allowances as the ACTUAL working-set bounds: the actual compiler demands carry the exact decoded sources, every emitted compiled block counts within its entry's allowance under the real pinned tokenizer, the raw sources gone from the actual main body, and the byte-identical transformed-round fixed point with zero recompile); the B03 typed request outcomes (the oversized source refused inside the compile attempt BEFORE any provider request — the fixed typed 503 with zero main forward and ZERO compiler provider requests, the bootstrap generation committed with its bound, the same-epoch repeat re-serving the SAME typed refusal with no retry — and the provider truncation typed BEFORE content validation — the fixed typed 503 with zero main forward and exactly ONE compile attempt, the terminal failure re-served same-epoch with no retry, and the fresh app runtime over the same recovery root in a distinct epoch completing the SAME request with exactly one successful compile and the byte-identical fixed point (the separate-process restart is the 023-c evidence); the output-slot half the existing `test_budget_overflow_refuses_then_heals`); the R02 direct forwarded-body evidence on BOTH endpoints (the acquired read carrier with the exact Unicode/CRLF original inside its proven process wrapper the ONLY source span edited — raw original gone, live marker in, wrapper prefix preserved byte-for-byte — the Responses round the retained image (the explicit route behavior) and every other input item dict-equal, the Chat round the user root text data with the assistant tool_calls and the retained image message dict-equal and the stable system placement carrying both compiled entries; the actual compiler demands carry the exact decoded source; the transformed-round replays byte-identical with zero recompile); and the ledger reconciliation binding the B02 final-wire aggregate/whole-entry omission and the B04 changed-config/no-incompatible-reuse claims to the existing named cases; `tests/test_app.py` (TestV1BudgetAndForwardedBodyAcceptance, five cases)) implemented at the same APPLICATION-TRANSACTION layer, active on opted-in v1 routes (at its bounded fake-upstream application scope on both endpoints), PENDING strategic review at its bounded whole-objective application-acceptance scope; R04 native compaction and the 024 actual-model/genuine-Codex stages remain the mandatory unearned v1 implementation stages (see `docs/CACHE-REWORK-LEDGER.md`)); the original
planned meanings of numeric 006-008 are historical planning prose, not
live identifiers. Strategy may revise only from verified evidence. One numeric
objective=one PR; coding never merges.

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
`docs/CACHE-ROOT-REGION-GRAPH-CONTRACT.md`) is PENDING
at its bounded graph-only scope, all as
inert typed modules under
`src/slaif_local_coding/constitution/bundles/`; they are not active in
the adapter request execution path, the legacy detector is unchanged,
the v1 runtime remains planned and inactive, and the remaining
statements below (compilation, RAM ownership, replacement, recovery,
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
PENDING strategic review at its bounded graph-only scope).**
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

The API remains inert and inactive in adapter execution.
The separate same018 admission/full-result consumer, all
original whole018 G/C/S and repair criteria, and stages
019-024 remain mandatory. R graph/source-scale results
cannot replace the later complete admission consumer's
own substantial-source and whole-operation resource
evidence. Preserve old H/O/I/P/Q public schemas,
defaults, versions, recipes and supported boundaries,
including honest old-I refusal of region-version state
and all earlier NOT ACCEPTED/PARTIAL decisions.

**Current-root composition (018-i inert, NOT ACCEPTED; 018-j
PARTIAL, NOT ACCEPTED; 018-k NOT ACCEPTED; 018-l PARTIAL,
NOT ACCEPTED; 018-m PARTIAL, NOT ACCEPTED; 018-n repairs
ACCEPTED; 018-o mixed observation ACCEPTED WITH PROCESS
QUALIFICATIONS; 018-p root-region producer ACCEPTED WITH
PROCESS QUALIFICATIONS; 018-q root-region currentness
ACCEPTED WITH PROCESS QUALIFICATIONS AND HISTORICAL-
REPORT CORRECTIONS; 018-r root-region graph PENDING
review at its bounded graph-only scope).**
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
`docs/CACHE-ROOT-REGION-GRAPH-CONTRACT.md`, is PENDING
at its bounded graph-only scope))
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
separate human-authorized act); 006 signed-request replay hardening
(PR #8); 007 current Gateway contract CI (PR #9); 008 durable acceptance
evidence (PR #10). Objectives 009-015 are merged through PR #22
(release-candidate line; it concluded with the private RC10 candidate).
Cutover NOT performed; NOT released. Objective 016 (merged PR #24, merge
`96c790423f6f0097a56a0b12bacda8a9b6da6aba`): dependency-bundle cache rework
contracts (handoff, plan, reconciled architecture/law, stage ledger).
Objective 017 was ACCEPTED at its bounded pure-observation scope WITH
PROCESS QUALIFICATIONS (017-am decision, `reviews/017-am-decision.md`) and
merged to main at ffaabf4b; objective 018 is active (018-a
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
`docs/CACHE-ROOT-REGION-GRAPH-CONTRACT.md`) is PENDING
at its bounded graph-only scope). The
per-round history (017-a through 017-am) is NOT restated here;
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
`reviews/017-am-decision.md`); objective 018 is active (018-a: inert
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
`docs/CACHE-ROOT-REGION-GRAPH-CONTRACT.md`) is PENDING
at its bounded graph-only scope and the
remaining 018 current-version/overlap work beyond this mechanism
(C04/C05 current-version acceptance, version-owned
edge/certificate withdrawal end-to-end acceptance) plus
objectives 019-024 remain the mandatory unearned v1
implementation stages (see
`docs/CACHE-REWORK-LEDGER.md`); the original
planned meanings of numeric 006-008 are historical planning prose, not
live identifiers. Strategy may revise only from verified evidence. One numeric
objective=one PR; coding never merges.

# Root-region admission consumer contract (objective 018, slice t)

`ROOT_REGION_ADMISSION_CONTRACT_VERSION =
"cache-root-region-admission/v1"`.
`ROOT_REGION_ADMISSION_POLICY_VERSION =
"root-region-admission-policy/v1"`.

This contract binds the INERT complete root-region admission
consumer (`src/slaif_local_coding/constitution/bundles/`:
`root_region_admission` and
`root_region_admission_result_models`). It is the SAME-RUN
complete consumer promised by the accepted 018-r and 018-s
slices: the ACTUAL public P input (state/namespace, never
caller-positive R/Q/F/graph/admission snapshots or verification
flags) derives ACTUAL R (including the ACTUAL same-run Q
currentness, P selection, selected root source and F/E current
graph) EXACTLY ONCE in this one charged operation, the ACTUAL
selected-root-aware G assembly consumes R's selected source,
current graph and same-run E overlay, and the complete new
result (`RootRegionAdmissionResult`, the THIRD carrying
boundary) carries the exact input, the actual R result by
immutable reference (once returned, on EVERY later outcome) and
the actual S admission parent by immutable reference (READY
only).

This slice is IMPLEMENTED and PENDING strategic review at its
bounded COMPLETE-CONSUMER scope. The 018-s models slice is
ACCEPTED at its bounded INERT MODEL/LOCAL-BOUNDARY scope WITH
PROCESS QUALIFICATIONS AND EXPLICIT HISTORICAL-REPORT
CORRECTIONS (strategic decision `S/reviews/018-s-decision.md`;
contract `docs/CACHE-ROOT-REGION-ADMISSION-MODELS-CONTRACT.md`);
the 018-r graph half is ACCEPTED at its bounded inert
selected-root source/current-graph scope WITH PROCESS
QUALIFICATIONS AND EXPLICIT HISTORICAL-REPORT CORRECTIONS
(strategic decision `S/reviews/018-r-decision.md`; contract
`docs/CACHE-ROOT-REGION-GRAPH-CONTRACT.md`); the 018-p/q
producer/query are ACCEPTED at their bounded inert scopes. This
slice closes nothing end to end: it is pure, bounded and never
active in the adapter runtime; no v1 runtime criterion is
qualified by it; compiler, authenticated runtime, wire, RAM and
recovery remain with their actual 019-024 owning stages; and
whole-018 acceptance remains with strategy. All existing
C/G/H/O/I/P/Q/R/S public signatures, schemas, defaults, version
tags, recipe bytes and refusal laws stay intact, including the
honest old-I refusal of the region-version state; the narrow
typed private factoring reuses the ACTUAL existing kernels and
predicates without changing old public law.

## 1. Public operation and inputs

`derive_root_region_admission(state, ns, bounds=None, *,
root_region_graph_bounds=None, root_region_currentness_bounds=
None, current_graph_bounds=None,
nonroot_currentness_bounds=None, admission_bounds=None) ->
RootRegionAdmissionResult`.

- The inputs are the ACTUAL retained P root-region lineage state
  and namespace (the closed public P boundary). Object
  construction is not authentication: no caller-positive
  R/Q/F/graph/admission snapshot and no verification flag is
  accepted anywhere in the operation.
- The ACTUAL R derivation happens ONCE through the narrow typed
  private R-core seam (the old public R wrapper is unchanged).
  No P-to-H conversion, no fake anchor/singleton, no
  positive `model_copy`/`model_construct`, no second unmetered
  derivation, no clock, no authority acquisition and no
  revision advance.
- The ACTUAL G assembly reuses the accepted G generic
  kernel: currentness BEFORE planning, lean
  whole/proven-group isolation, greedy whole without new
  isolation/authority, candidate and reverse attempts charged
  BEFORE dedup, exact entry-source/member/entry/reason caps and
  the complete reverse index. Unknown individual member hashes
  stay unknown; no invented reference origins or reachability
  from greedy background.
- Outcomes: READY (actual R READY AND completed actual
  admission AND the full-result third-parent checks -- never
  readiness of any kind beyond that);
  ROOT_CURRENTNESS_UNPROVEN / ROOT_AUTHORITY_CONFLICT (the
  ACTUAL same-run R positive-interpretation outcomes mapped
  from the actual Q channel, the actual R result retained, no
  usable admission, no bootstrap fallback); REFUSED (the fixed
  typed consumer failure -- an early T gate, a T-level work
  crossing, a mapped R refusal or an actual G-subtree/admission
  domain refusal -- with every already-returned actual evidence
  retained and no usable admission or bootstrap fallback).
- The exact input state (with its actual carried revision and
  lineage key) is retained on EVERY valid-input outcome.
  REFUSED results retain the ACTUAL returned R object by
  reference as bounded evidence; the terminal record is
  bounded to metadata and never re-enters the root BODY
  content pass.

## 2. The complete result (third carrying boundary)

`RootRegionAdmissionResult` carries: outcome, the exact input
`state`/`ns` by identity, the resolved consumer bounds
(`RootRegionAdmissionBounds`, the ORIGINAL class, stricter by
value legal), the ACTUAL G `CurrentAdmissionBounds` (original
class), the actual R result (or the fixed honest absence where
R never returned), the actual S admission parent (READY only),
the stable scope key, the honest same-run counters
(`work_units`, `r_work_units`, `g_work_units`,
`stage_work_units`, `entry_source_bytes`), the closed own
diagnostics and the G refusal limitation (REFUSED only, with
the exact diagnostic pairing).

The closed result validator runs, in order: (0) the closed
field-existence/class/tag fences, the bounds-shape fence at the
ORIGINAL classes and hard ranges, the state/namespace field
fences, the closed source-independent carried-R joins and the
admission field fence; (1) the outcome invariants (g_limitation
only on REFUSED with its paired fixed diagnostic; admission
only on READY; at most ONE own diagnostic, closed empty
boundary); (2) the identity joins in their fixed order (the
consumer namespace lineage join with the T-own early
foreign-scope exemption; the self lineage/revision joins; the
R-result state/lineage/revision joins; the admission
state/namespace/R-result/G-bounds joins; the closed O(1)
eleven/six bound-set fences; the closed carried-R metadata
joins BEFORE the dependent consumer scope-key serializer
target); (3) the stable scope-key
recomputation; (4) the counter fences; (5) the COMPLETE actual
S admission-parent re-validation (`RootRegionAdmission.model_validate`
of the carried parent -- the complete READY third-parent
source law at that boundary). A partial or bypass-copied
nested record, foreign/coherently rekeyed namespace, later
genuine proof/source or same-root stale splice is refused by
the actual gate that precedes the DEPENDENT unsafe work
(dependent attribute access, traversal, serialization or
owned source work) -- fences precede their dependent unsafe
work, not every earlier serializer. Promised state/
proof/source identities remain identity, not structural
equality. The operational `repr`/
`str` never echo carried content or private IDs.

The STABLE consumer scope key binds: the ACTUAL P lineage key
(no revision), the NEW consumer contract/policy versions, the
ACTUAL re-derived R scope key, the ACTUAL S-model scope key,
the ACTUAL G contract/policy versions, and EVERY effective
bound set (consumer and G, as closed inner dumps). The carried
revision and the actual graph snapshot scopes join
SEPARATELY -- never clocks, never part of this stable
configuration identity. The selected root digest IS a
semantic C key ingredient (the canonical recipe re-keys the
root entry when the governing root changes); it is a
carried-value join, not a stable-configuration ingredient.
Where the R result or the S admission parent is absent, its
respective fixed private absence placeholder is bound
instead -- even where the R result was returned but the
admission parent is absent (the mapped non-READY and
REFUSED outcomes retain the actual R without an admission) --
honest absence, never a fabricated key.

## 3. ONE entire operation, independent inherited domains

The NEW entire-consumer outer
(`RootRegionAdmissionBounds.max_total_work_units`, default AND
hard 8388608; own diagnostics 64 default AND hard) is a NEW
versioned work domain: NOT a raised old cap, NOT a RAM/RSS or
token budget, NOT a reinterpretation of a source-size setting.
The versioned ledger law:

- The entire ledger is created BEFORE early
  scope/hash/bound/construction work (the closed O(1)
  bootstrap reads size it; the bounded base charge is reserved
  before it runs). A legal cap at or just above the base charge
  maps to the fixed typed refusal (the closed
  refusal-construction convention re-runs the closed O(1)
  namespace fence uncharged, so an unjoined or foreign
  namespace keeps the exact foreign-scope shape even when the
  crossing hits before the fence itself runs).
- EVERY actual R unit (Q/P/D/B/source/F/E included) is coupled
  into it unit-for-unit through the narrow typed R-core seam
  (`_TRTotal`) BEFORE the crossing work runs.
- The ACTUAL G subtree ledger is created BEFORE R's F phase:
  every actual F unit charges the SAME G ledger that the
  admission phase uses (its independent F-subtree ceiling
  binds during the explicit F phase exactly as in the accepted
  018-g law). G covers F plus the admission/root/FILE/
  association/S-parent construction and validation; it does
  NOT cover Q/P/selected-source resolution or the final
  full-result parent.
- R covers its actual derivation only; the full-result parent
  and its rechecks charge the NEW entire outer.
- Shared work charges each applicable domain ONCE (a unit
  shared with the R derivation never double-charges the entire
  outer; a same-boundary reservation is never spent twice).
- The actual inherited Q/P/D/B/E/F/GraphBounds, G,
  graph/admission-stage, diagnostic, source and original-batch
  domains remain independently binding beneath it (no global
  minimum, no reset, no whole-cap reservation, no post-hoc
  initialization, no module-global or context-global budget
  channel, no caller verification flag). Original-batch caps
  are not cumulative retention caps.

Conservative validated structural ceilings cover the genuinely
fixed closed metadata passes (documented per component); every
variable metadata/source/serialization pass is reserved by its
actual recipe BEFORE it runs (the accepted S component
precharge contracts included, reused). The witness
region-compatibility term runs under the T-only tightened
actual-owner billing (its owner-domain walks close at the ACTUAL
retained owner population, fenced under the ACTUAL inherited B
caps before they feed the term); the old S default recipe is
untouched. The carried R metadata joins at the third boundary
run under their own derived ceilings for the constructor's own
re-run, separate from the phase-5 S parent re-validation's
COMPLETE R result law pass (reserved by the actual S
admission-parent precharge) -- two real passes, each reserved
once. Capped UTF-8 is measured without copying before owned
encode/hash/slice/join work is reserved.

## 4. Source dispatch and content law

Explicit dispatch for the ACTUAL envelope, whole `read` and
`read_region` provenance. Envelope text comes only from the
actual immutable D RootAnchor when that fact is selected. A
whole read keeps its actual complete singleton proof. A region
joins the selected fact, occurrence, complete owning result,
each original piece producer, whole-proof binding, segment/
member coordinates and root-member digest/byte length to the
SAME original retained P/D objects. The bootstrap proof scope
stays distinct from the selected governing digest; region
offsets are preceding original segment CHARACTER sums (not
byte/carrier spans). Unicode nonroot prefixes, CRLF, the exact
EMPTY root and printed-marker exclusion are preserved. The
FIRST compatible original proof and ALL distinct compatible
witness coordinates remain intact, without per-witness full
body copies. The actual G selected-root compatibility law is
unchanged (version-owned withdrawal, surviving alternates,
cycles, least AND/OR depths, effective max_depth).

## 5. Work versus source-size domains

The 8388608-unit entire total is a WORK domain. The UTF-8
SOURCE SIZE / retention domains (single-source 1000000,
entry-source 16777216, retained root source bytes) and the
original-batch per-transition COUNT domains (e.g.
max_requests) stay separate from work and from each other,
never work fuel. No zero-allocation claim follows from any
refusal.

## 6. Source-scale and whole-operation evidence (E)

Complete-operation READY is earned independently with at least
32768 UTF-8 root bytes for root-only and mixed-region/
no-singleton, BOTH modes and mixed read endpoints, under the
original single-source 1000000 and entry-source 16777216 byte
domains. The actual per-case records below are the permanent E
test records (the protected focused-run output of
`tests/test_root_region_admission.py`, recorded per shape
with sizes, outcomes and counters -- not inferred from
exploratory probes). The figures cited are the representative
LEAN-mode records of that permanent output (root-only at the
envelope bootstrap endpoint; mixed-region and version-history
at the Responses endpoint); the same run records BOTH modes
and BOTH read endpoints with their own actual counters.

- ROOT-ONLY: 32768 bytes READY at the DEFAULT domains
  (whole 1117765 / R 330173 / G 460593 work units, stage 89,
  entry-source bytes 32768, single ROOT row, zero FILE
  entries, one retained entry); 65536 bytes READY at default
  (whole 2035269 / R 657853 / G 821041); 131072 bytes
  REFUSED with the fixed work-units-over-bound diagnostic
  (the ACTUAL F OK result and the Q READY retained as bounded
  evidence, G 25 work units, stage 0, no usable admission).
- MIXED-REGION (no independent singleton): the default
  GraphBounds stage (65536 work) REFUSES the mixed assembly
  (admission_over_bound with the admission work-units-
  exhausted limitation at stage 65536, the actual R READY
  retained, no usable admission); under a GENUINE namespace
  using the existing LEGAL GraphBounds stage setting 1048576
  (unchanged hard range, identity-bound) the 32768-byte mixed
  shape is READY (whole 1654730 / R 363245 / G 837317, stage
  131530, entry-source bytes 65557, rows A.md:1 +
  AGENTS.md:2, two retained entries, three charged); 65536
  bytes at that stage REFUSES with the G total work-units-
  over-bound at 1048576 (stage 262602); 131072 bytes
  REFUSES before any F phase (no F result, G zero).
- MULTI-DEPENDENCY / VERSION-HISTORY (32768 root member):
  default stage REFUSED; under the legal 1048576 stage READY
  (whole 1864544 / R 363781 / G 968378, stage 132290,
  entry-source bytes 65600, five entries in TOTAL: one ROOT
  row plus four FILE rows A.md, AGENTS.md, Target.md, X.md)
  with the actual v2 body/digest and original proof reference
  selected (the version-history positive asserts the ACTUAL
  selected R source kind/digest/body and original proof
  identity, not length/row coincidence).

These are complete-operation records at stated domains. They
are NOT default whole-consumer readiness, NOT zero allocation,
and NOT wire/cache/runtime qualification. The history scale is
32768 ONLY. The S component counters alone do not satisfy this
criterion; the complete public operation earns it above.

## 7. Independent local-domain discriminators (D)

Real whole-operation/domain discriminators are measured on the
ACTUAL ledger classes (class-preserving constructor wrappers;
real instances, real counters; the targets instrumented, never
replaced by functions):

- WHOLE exact/one-below at the SAME explicit bound/call shape:
  the entire cap at the measured whole cost READYs; one below
  refuses the fixed own diagnostic with the original
  source/context preserved.
- The inherited G-channel law: the G refusal limitation is
  carried ONLY on the actual G-domain REFUSED outcome with the
  exact diagnostic pairing; the closed empty-diagnostics
  boundary holds on every non-G outcome.
- G-subtree below the entire: the genuine G total cap at the
  measured F+admission cost (strictly below the successful
  whole) still READYs the complete derivation (the G work
  completes WITHIN its cap -- the cap's own digit billing
  changes the actual cost, so the actual G cost need not sit
  AT the cap; the entire T domain is independent and larger);
  the G domain channel stays distinct from the consumer-own
  channel.
- F-LOCAL: the genuine F-subtree cap EXACTLY at the measured F
  cost still READYs the full admission (F < G total < whole);
  one below RUNS the F phase and returns its ACTUAL F-domain
  refusal (the typed F over-bound result on f_result, Q READY
  and the actual P selection retained) with no admission work
  (the admission assembly counted, never replaced, with zero
  calls; the F ledger's actual charged work retained, never a
  fabricated zero).
- Q-LOCAL: the genuine Q cap at the measured Q cost READYs;
  one below refuses through the ACTUAL Q channel BEFORE any
  F/admission work (the F phase never runs at all -- the F
  ledgers absent, never a fabricated zero; the typed Q over-
  bound result with the actual P selection retained; no
  consumer-invented diagnostic, no G channel).
- R-TOTAL: the genuine R cap at the measured R cost READYs;
  one below carries the mapped ACTUAL R total crossing,
  retains the actual R result with the intermediates ACTUALLY
  returned (Q READY and the actual F OK as bounded evidence),
  and never reaches the admission assembly (counted, zero
  calls).
- P-LOCAL: on the genuine public-P-built n=40
  eligible-opaque-branch fixture, the strict public-P-built P
  ceiling (the frozen per-operation producer maximum, the
  actual inherited `ns.root_lineage_bounds` domain) bounds the
  ACTUAL P phase of the derivation (measured on the actual
  same-run P-domain ledger) while the successful T whole
  EXCEEDS it -- the discriminating shape a single shared
  min(P ceiling, whole) budget cannot pass. P-first-over is
  NOT attained by this public production sequence (the
  producer maximum exceeds the derivation's P phase, so no
  producible ceiling falls below it); the charging-adapter
  P-crossing mechanism is exercised directly by the accepted
  Q suite's `test_e_p_first_over_adapter_mechanism`, a direct
  mechanism control, NOT public T evidence and NOT a
  universal-unreachability claim. No public P one-below
  positive is invented.
- ORIGINAL-BATCH: with max_requests=1, two SEPARATE
  one-request observations are each legal and BOTH retained
  (per-batch domain, not a cumulative cap) and the complete
  public derivation READYs on the exact retained state; ONE
  two-request batch refuses the exact mapped batch bound
  BEFORE the deliberately malformed second element is
  inspected (count gate precedes element validation), with
  the EXACT prior state and no revision advance, and the
  derivation remains READY on the preserved state.

Unreachable domains use truthful constructor-level negatives;
no full-minimum-minus-one zero-allocation claim is made
anywhere.

## 8. The full-result third-parent carrying boundary (C)

A genuine complete positive (genuine P -> complete R ->
complete admission -> full result) is revalidated FIRST; only
then do negative-only mutations run through the actual
`RootRegionAdmissionResult.model_validate` with real class
spies (counted, never replaced) and fixed private failure
precedence: the leaf/S-parent retained-content/group/key/
reverse-index law at that carrying boundary, malformed/missing
variants and effective bounds, foreign namespace, coherent
wrong tags, detached originals, same bogus canonical content
key (the actual canonical recompute refuses), altered
retained group digest rekeyed with the ACTUAL canonical
recipe (retained-content law refuses against the original
proof segment digest), and actual later/same-root stale
graph splices. The phase-faithful spy distinguishes pre-scope
gates (the consumer scope serializer NOT reached) from
post-scope gates (the complete S parent re-validation). No
predicate, typing or positive factory is weakened.

## 9. Privacy and purity (F)

- Deterministic scope versus revision: two derivations of the
  SAME state agree on the stable scope key; a genuine
  revision-advancing transition on the SAME lineage and bounds
  keeps the scope key while the revision join and the
  admission content move; a derivation-only bounds change
  moves the scope key while the canonical C content key and
  the canonical payload DATA stay byte-identical.
- Canonical payload DATA preservation BEYOND the key-record
  JSON: two complete derivations of the same state produce
  byte-identical full admission JSON, byte-identical root and
  FILE key records, equal honest work counters, while the
  canonical INPUT payload DATA (state/namespace dumps
  snapshotted before any call) is unchanged and every
  retained original proof is the SAME object in both results.
- Exact input/original-reference retention on the complete
  result (identity joins throughout; the FILE proofs joined
  through the ACTUAL witness retained-occurrence IDs, and the
  key-record member_occurrences are PATHS, never occurrence
  IDs).
- No raw root/nonroot/marker/ID/model/identity canary appears
  in ANY tested rendering of the complete result (genuine
  READY and genuine refusal) or in the fixed private bypass-
  copy error, while the canaries genuinely ride the ACTUAL
  carried state (the negative is not vacuous).
- The closed host-IO trap surface is installed AFTER
  fixture/import setup and stays clean on the ready,
  non-ready and refusal paths.
Pure preservation is not HTTP wire, compiler-hit, cache
readiness or authenticated runtime-isolation proof.

## 10. Boundaries and remaining scope

- INERT: never active in the adapter request execution path;
  the legacy detector is unchanged; the v1 runtime remains
  planned and inactive. No runtime/HTTP wiring, compiler,
  tokenizer, RAM/recovery state, model call, service,
  deployment, release, benchmark or cutover.
- READY of this operation never implies acquired required
  dependencies, compiled content, cache readiness, HTTP
  readiness or v1 runtime readiness.
- Whole-018 acceptance (including the original G/C/S
  criterion map and the I/J/K/L/M/N repair-requirement
  lineage) is performed by strategy from the implementation
  and evidence in the existing ledger; nothing here upgrades
  any historical NOT ACCEPTED/PARTIAL decision.
- Stages 019-024 (compiler, authenticated runtime, wire, RAM,
  recovery and their acceptance) remain mandatory and are
  NOT closed by this slice.

## 11. Tests

`tests/test_root_region_admission.py` is the permanent A-G
acceptance-matrix home for the complete consumer: A genuine
public positives (envelope, mixed-only region, both modes and
both read endpoints, provenance key pinning, Unicode/CRLF/
empty source shapes, native multi-piece original-owner
associations, ordered FILE keys, repeated operands/distinct
width, first proof/all witnesses, exact reverse rows); B
version/withdrawal (AB/AC/A overlap, alternate/cycle/depth
withdrawal, deliberate revert versus replay, replay and
authority-conflict no-admission, root-rekey rows); C the
full-result third-parent bypass battery (section 8); D the
local-domain discriminators (section 7); E the source-scale
outcomes and per-case records (section 6); F the purity/scope/
retention/canary/IO-trap and canonical payload DATA laws
(section 9); and the A-G criterion mapping is recorded in the
existing ledger. The S models suite
(`tests/test_root_region_admission_models.py`) and every
older suite remain unchanged in their accepted scope.

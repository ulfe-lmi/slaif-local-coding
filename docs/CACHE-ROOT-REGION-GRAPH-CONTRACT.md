# Root-region selected source and current graph contract
# (objective 018, slice r)

`ROOT_REGION_GRAPH_CONTRACT_VERSION =
"cache-root-region-graph/v1"`.
`ROOT_REGION_GRAPH_POLICY_VERSION =
"root-region-graph-policy/v1"`.

This contract binds the INERT pure selected-root-region source
and current-graph derivation
(`src/slaif_local_coding/constitution/bundles/`:
`root_region_graph_models`, `root_region_graph`, and the public
entry `derive_root_region_graph`, plus the bounds factory
`RootRegionGraphBounds`). It sits ABOVE the accepted 018-q
root-region currentness query
(`docs/CACHE-ROOT-REGION-CURRENTNESS-CONTRACT.md`) as the
CONSUMER half of this round: from the ACTUAL retained 018-p
state and namespace it derives ACTUAL Q in the SAME charged
run, resolves the ONE usable selected root source, and derives
the ACTUAL accepted 018-f/018-e current graph under that
selected root
(`docs/CACHE-CURRENT-GRAPH-CONTRACT.md`,
`docs/CACHE-CURRENTNESS-CONTRACT.md`). It never takes a
caller-positive Q/F snapshot, converts P state into old H
state, manufactures a singleton or RootAnchor, advances a
revision, adds authority or creates persistent state. The
018-p producer is ACCEPTED at its bounded inert producer scope
WITH PROCESS QUALIFICATIONS (strategic decision
`S/reviews/018-p-decision.md`); the 018-q query is ACCEPTED at
its bounded inert query scope WITH PROCESS QUALIFICATIONS AND
HISTORICAL-REPORT CORRECTIONS (strategic decision
`S/reviews/018-q-decision.md`); this 018-r slice is
IMPLEMENTED and PENDING strategic review at its bounded
graph-only scope. It closes nothing end to end: the separate
same-018 admission/full-result consumer, all original whole
018 G/C/S and repair criteria, and stages 019-024 remain
mandatory, and R graph/source-scale results cannot replace the
later consumer's own substantial-source and whole-operation
resource evidence. Like the accepted bounded 018 slices it is
pure, bounded and never active in the adapter runtime: no
command string is executed, no model/native/client/service
facility is started, and no implementation/release/whole-018
status is upgraded by inherited green checks. All existing
H/O/I/P/Q public signatures, defaults, schemas, version tags,
recipe bytes and behavior remain intact; the narrow private
shared-ledger seam extracted into the Q module for this
consumer preserves the public Q wrapper's fences, bounds
resolution and scope-key recomputation unchanged.

## 1. Namespace, scope key and caller trust

- The input is the ACTUAL `RootRegionLineageState` and the
  ACTUAL `RootRegionLineageNamespace` (the original namespace
  fields, bounds and versions bind the derivation scope; a
  stale or forged key is never trusted), plus the optional
  nested bounds overrides (`root_region_currentness_bounds`,
  `current_graph_bounds`, `nonroot_currentness_bounds`). R is
  a derivation: there is NO CAS input, NO new revision and NO
  clock.
- The stable scope key is EXACTLY
  `root_region_graph_scope_key(state.lineage_key, R contract,
  R policy, actual R bounds, actual Q bounds, actual F bounds,
  actual E bounds, ns.graph_version)`, recomputed on every
  construction under closed actual-field fences. It binds the
  ACTUAL P lineage key (which itself, through the real P/D/C
  factories, binds the inherited identity/model/workspace/
  version/bound fields AND the P contract/policy versions),
  the R, Q, F and E contract/policy version identities (the
  ACTUAL accepted F/E version constants — the P namespace does
  NOT already bind the separate E/F versions), EVERY effective
  R/Q/E/F bound field and the actual inherited graph version.
  It does NOT bind the carried state revision: the revision is
  separate carried derivation identity, never a clock and
  never part of the stable scope key (a GENUINE accepted
  transition that advances the carried revision keeps the SAME
  scope key).
- The O(1) boundary fences run FIRST, in this order: a non-P
  object or a PARTIAL actual state instance fails with a FIXED
  private `ValueError` before any result construction
  (consistent with the accepted Q/old-I state boundary); a
  PARTIAL actual namespace instance, a malformed namespace
  shape or an unencodable/malformed graph version (not
  1..128 non-space UTF-8-encodable) is a typed
  `foreign_scope` refusal in the honest safe refusal scope
  (the fixed rejection tag, never the unusable input itself —
  the version is fenced BEFORE any scope-key hash/encode, so a
  malformed version never reaches an encoder exception).
- Every effective bound set — the OWN R bounds and the three
  actual nested Q/F/E bound sets — is fenced for class, field
  EXISTENCE, exact non-bool int and hard-ceiling range BEFORE
  any serializer visit; a raw override dictionary or a
  MALFORMED model_copy mutation refuses `malformed_binding` in
  the default domain (the usable input is never partially
  trusted), while a valid STRICTER model copy is accepted into
  an equivalent effective value (value equality, not
  unpromised input-bound identity) and the absent override
  runs the default domain.
- Object construction is not authentication. Caller-supplied
  positive Q/F snapshots are not authority: a downstream
  consumer MUST derive currentness and the graph from the
  actual state in the same bounded operation.

## 2. Pure API and result law

- `derive_root_region_graph(state, ns, bounds=None, *,
  root_region_currentness_bounds=None, current_graph_bounds=
  None, nonroot_currentness_bounds=None)` returns
  `RootRegionGraphResult`: the outcome, the EXACT state, the
  ACTUAL same-run Q result, the ACTUAL F result, the ACTUAL
  same-run E overlay, the resolved source, the closed R-OWN
  diagnostics, the effective R/Q/F/E bound sets, the contract/
  policy tags, the lineage key, the scope key, the carried
  revision and the actual inherited graph version.
- The result retains the EXACT input P state by `InstanceOf`
  reference on EVERY outcome with its actual revision and
  lineage key. The derivation never advances a revision,
  never mints a root authority fact and never copies source
  beyond the ONE materialized root body.
- `q_result` is `None` until the ACTUAL same-run Q phase has
  returned (early R gates and an R-total crossing before the Q
  return carry no fabricated Q evidence) and, once returned,
  is retained on EVERY later outcome. `f_result` is `None`
  until the ACTUAL F phase has returned (a mapped Q refusal
  never runs F); `e_overlay` is present exactly when the
  actual F result is OK, and is retained as bounded evidence
  even on an R-total crossing during the final output
  reservation. `resolved_source` is published ONLY on
  `ready`.
- Outcomes: `ready` (ONLY the actual same-run Q ready, the
  resolved selected source and the actual F graph success all
  hold — it does NOT mean acquired required dependencies,
  admitted entries, compiled content, cache readiness, HTTP
  readiness or v1 runtime readiness),
  `root_currentness_unproven` and `root_authority_conflict`
  (the ACTUAL same-run Q positive-interpretation outcomes
  mapped before any source slicing or F derivation — no
  usable selected source, no graph, no bootstrap fallback),
  and `refused` with the closed R-OWN diagnostics
  `foreign_scope` / `version_unsupported` /
  `malformed_binding` / `work_units_over_bound` /
  `source_resolution_failed`. Every non-ready result
  publishes NO usable resolved source or graph (it may still
  retain the ACTUAL returned nested evidence by reference).
- The R-OWN diagnostics are the R derivation's own typed
  refusal reasons, NOT a copy of the P/Q/F vocabularies: a
  mapped Q refusal adds NO R diagnostics (the actual Q result
  carries the Q reasons), a mapped F refusal carries the
  actual F result (the F limitations stay with it), and only
  the R's own gates, work crossings and source-resolution
  failures emit R diagnostics. On the actual kernel every
  own-diagnostic tuple is empty or a singleton: when the
  R-total crossing lands in a mapped Q non-ready
  result-construction reservation, the outcome is `refused`
  with exactly ONE `work_units_over_bound` and the actual Q
  result retained (the non-ready outcome is not published
  with the overflow). The >64 own-diagnostic constructor
  ceiling is unreachable through the public API because a
  public R derivation emits at most ONE own fixed diagnostic
  per outcome (the nested Q/F limitation channels are
  separate evidence, not R diagnostics).

## 3. Selected-source resolution (exact intervals and joins)

- `BundleProof.source_text` concatenates the SOURCE segments
  in order with the proven printed marker lines EXCLUDED. The
  selected region begins at the sum of the preceding original
  segment CHARACTER lengths — never UTF-8 byte lengths or
  carrier piece spans/offsets, which are not offsets into that
  aggregate. Unicode, CRLF and the exact empty root are
  preserved; the O(1) interval/byte preflights (the interval
  stays inside the actual aggregate source text, bytes never
  fewer than characters, the retained hard root-source-byte
  ceiling) run BEFORE any owned slice, encode, hash or copy,
  and the owned slice copy width is reserved BEFORE the copy.
- Source dispatch is explicit for the three actual provenance
  classes; the concrete fact provenance class is fenced
  against the kind tag BEFORE any dispatch, per kind (a wrong
  or missing class is the fixed private source error, never an
  echo of a stored flag):
  - `envelope`: text comes only from the actual immutable D
    root anchor when that fact is selected, with the
    anchor/provenance/fact digest, workspace and byte-length
    joins;
  - `read`: a whole read keeps its ACTUAL complete singleton
    proof (read digest/length joined to the whole proof and to
    the fact root body, `root_path` the root file);
  - `read_region`: a region joins the selected fact,
    occurrence, complete owning result, each original piece
    producer, whole-proof binding, segment/member coordinates
    and root-member digest/byte length to the SAME original
    retained P/D objects by identity.
- The deterministic FIRST compatible witness in the actual
  canonical witness order is materialized: the selected fact
  is joined to the SAME input state's actual `root_facts` by
  identity (membership width precharged, then the charged
  walk); the original selected occurrence to the SAME D
  occurrence (ID lookup, membership width precharged); the
  complete owning proof and segment/member coordinates to the
  SAME original objects. Keep EVERY compatible maximal
  original witness through the actual Q/P selection; the
  derivation materializes only the deterministic first
  compatible root body, without a full source walk for each
  witness.
- The whole-proof digest/length and the selected root-member
  digest/length are DISTINCT; the original `proof.root_digest`
  stays bound to the immutable bootstrap scope even when the
  selected governing root is newer. Never rewrite the original
  proof or anchor to make a join pass.
- Preserve original-reference identity where promised: the
  resolved source carries the ACTUAL selected fact, occurrence
  and proof by immutable reference, and a cloned-together
  proof+occurrence pair passes only when BOTH are ORIGINAL
  members of the exact input D state by identity (charged
  bounded metadata/index joins, not a full source walk).
  Value equality is NOT an original association proof; a pure
  value-equal valid input is not rejected merely because its
  top-level bound object was copied.
- Content law: the digest is rechecked from the ONE owned
  encode against the ACTUAL retained provenance binding (a
  repeated integrity check, charged — the capped no-copy UTF-8
  measurement runs BEFORE the owned encode, per ACTUAL
  character, with the width precharged). The READY result
  constructor re-runs the FULL closed content law over the
  record's own root text (walk + encode + hash) after the
  closed shape preflight — a `model_copy`-bypassed tampered
  record is refused at the result boundary; a length-only
  intrinsic check is not content verification, so the local
  consistency boundary checks digest AND length AND text
  together.

## 4. Ordered mapping and refusal precedence

Explicit and tested, in ACTUAL order: (1) the STATE O(1)
shape fence (fixed private `ValueError` before result
construction); (2) the NAMESPACE O(1) boundary, malformed
shape or graph-version fence (honest safe refusal scope);
(3)-(6) the closed OWN R / Q / F / E bound resolutions
(malformed refuses `malformed_binding` in the default domain
before any serializer visit); (7) the scope-key
recomputation and the ONE R outer base charge; (8) the
ACTUAL same-run Q phase under the ONE R total (its ACTUAL
independently bounded P phase included — section 6); (9) the
ordered Q mapping: an actual Q unproven maps to
`root_currentness_unproven`, an actual Q authority conflict to
`root_authority_conflict`, an actual Q refusal to `refused` —
each BEFORE any source slicing or F derivation, each
precharging its OWN bounded result construction before it is
built, publishing no usable source/graph and no bootstrap
fallback; (10) a missing/empty actual P selection maps to
`refused` `source_resolution_failed`; (11) the charged
selected-source resolution (a closed join/preflight failure is
the fixed private source error, no partial source); (12) the
actual D-namespace re-derivation and revalidation joins
(`foreign_scope` on a history-key mismatch,
`version_unsupported` on revalidation refusal) under the
ACTUAL charged reservation; (13) the ACTUAL F/E phase under
the ACTUAL independent F outer (section 5); (14) the final
output reservation and READY construction. P/Q/F refusal
reasons stay in their actual channels; already returned
nested evidence stays truthful — in particular an R-total
crossing AFTER F completed may retain that ACTUAL F OK result
(and its E overlay) as evidence while R remains REFUSED and
exposes no usable resolved source.

## 5. F/E phase and graph semantics

- Derive a FRESH F least fixed point under the selected root
  digest, using that selected root as the ONLY root-text
  supplier and the ACTUAL E nonroot currentness/ownership law
  (`_derive_graph` with the actual F outer and the actual
  graph-stage ledger from the revalidated D namespace).
- The accepted F law is unchanged: stale, conflicting or
  ambiguous groups supply nothing; a root-bearing opaque
  group NEVER supplies root text; withdraw only the removed
  version owner's ordinary edges/certificates; retain
  surviving complete alternate suppliers; remove unsupported
  cycle-only reachability; retain honest unreachable
  possession; recompute least AND/OR depths and the effective
  max_depth; unknown reference origin remains unknown; greedy
  co-caching alone never promotes reachability or authority.
- An F over-bound/stage-overflow/malformed refusal is mapped
  to `refused` carrying the ACTUAL typed F refusal result
  (its limitation stays in the F channel, no R diagnostic is
  invented); an F OK with an R-total crossing in the final
  output reservation is `refused` `work_units_over_bound`
  retaining the ACTUAL F OK result and E overlay.

## 6. ONE R outer and the independent nested domains

- ONE R outer covers the ENTIRE operation: the early
  scope/bound reservations, the actual Q/P/D/B work, the
  original-source resolution, the actual F/E and graph-stage
  work, and the association/serialization/construction
  reservations. The R bounds are total work 1048576 and own
  diagnostics 64, DEFAULT AND HARD, with stricter positive
  values legal. They are per-operation domains, not
  retained-source, RAM/RSS or token budgets.
- Each actual inherited Q-local, P, D, B, E, F and
  GraphBounds domain remains INDEPENDENTLY binding under that
  total: the Q phase runs through the accepted private
  charged-core seam with the Q-local ceiling coupled
  unit-for-unit into the R total (a Q-local crossing refuses
  with the Q fixed over-bound name WITHOUT charging the R
  total for the crossing unit); the ACTUAL P phase retains
  its independent root-lineage ceiling beneath the Q phase
  (the accepted P-adapter composition); the F phase runs
  under the ACTUAL independent F outer (its own diagnostic
  domain unchanged) coupled into the R total, with the
  accepted F graph-stage ledger beneath it. There is NO
  global minimum, NO cap-sized fake reservation, NO reset
  ledger and NO second unmetered public derivation (no second
  full public Q/P/F call with fresh fuel, no entire-cap
  pre-reservation subtracted from the total).
- Precharge-before-work: the closed O(1) count/scalar/class/
  version gates precede element/set/sort/hash/serializer
  work; candidate attempts count before deduplication; real
  metadata walks, snapshots, membership widths, reservation
  calculations, owned content passes and constructors are
  charged BEFORE the work they bound; the source preflights
  precede any owned slice/encode/hash/copy without a
  per-witness source walk. A crossing raises the fixed
  private overflow BEFORE the crossing operation runs.
- R-owned character/byte content reservations are a separate
  new R policy: they do NOT reinterpret or replace the
  accepted F operation counters or the F's separate
  source-byte/stage domains. Original-batch limits stay
  distinct from cumulative retention.

## 7. Bounds and the closed collection ceilings

- `RootRegionGraphBounds`: `max_total_work_units` 1048576 and
  `max_diagnostics` 64, each DEFAULT AND HARD; stricter
  positive values are legal, and the malformed/raw overrides
  refuse before any serializer visit (section 1). The nested
  Q/F/E bound sets are the ACTUAL accepted
  `RootRegionCurrentnessBounds` / `CurrentGraphBounds` /
  `CurrentnessBounds` with their own closed fences and
  ceilings.
- The carried witness/fact/occurrence populations are bounded
  by the ACTUAL inherited D collection and work domains
  (`max_occurrences` 4096 default/hard and the per-operation
  work bounds), which bound the retained occurrence
  population; the final output reservation charges the
  ACTUAL retained widths (root facts, selected witness
  facts, occurrences) before the constructor re-scans them.
  More than the own-diagnostic ceiling is unreachable
  through the public API for the section-2 reason; the
  constructor fences remain the closed intrinsic law before
  any dump/serialization visit.
- Measured domain discrimination (fully public production,
  BOTH admission modes/endpoints): with a real public mixed
  P->R positive, the ACTUAL Q-local cap set one unit below the
  measured Q phase refuses with the inherited Q typed
  refusal (exact state, no source, actual Q channel) while the
  SAME-run R total still fits, and the ACTUAL F-subtree cap
  set below the measured F work refuses with the inherited F
  over-bound result retained; at the exact measured local
  caps the derivation is READY. The pre-slice sentinel
  (line-entry at the ACTUAL slice statement of the charged
  resolver, counted over ALL slice instructions with the
  exact code-object binding) shows the refusal one unit below
  the slice-target cap lands BEFORE the slice statement with
  zero entries and the exact state/Q retained; line entry
  measures statement entry before the builtin slice, not
  completed opcode execution or all allocations. These are
  measured controls, not hardcoded cap tests.
- Measured content-scale baselines (source-pinned moving
  baselines as permanent controls; the source BYTES are the
  measured input, not hardcoded work values; no cap is raised
  and no positive is faked): the root-only bootstrap
  (envelope source; the Responses envelope bootstrap carries
  no read-endpoint parameter) and the mixed-region shape
  (read_region source, no singleton), on BOTH admission modes
  — the mixed and history shapes on BOTH read endpoints —
  derive READY at 32768 and 65536 root-member UTF-8 bytes (the
  resolved source kind, byte length and digest are exact, the
  actual F OK and the exact state are retained); 131072
  bytes refuses the typed R total over-bound with the HONEST
  stage evidence — the root-only crossing lands in the FINAL
  output reservation AFTER the F phase (which counts BOUNDED
  operations in its separate source-byte/stage domain, never
  per-byte), so the actual F OK result is retained, while the
  mixed crossing lands in the CHARGED SELECTED-SOURCE
  RESOLUTION (the source-constructor content-verification
  reservation, after the selected-root slice), so F never runs
  and no F result is published; the actual Q READY and the exact state are
  retained in both cases, with no usable source. The multi-dependency/version-history shape (the
  genuine version-owned withdrawal, surviving alternate,
  cycle-only disappearance and old-bytes revert laws at
  substantial size, with a Unicode nonroot prefix and exactly
  32768-byte root members) holds at every phase with the
  ACTUAL measured R/Q/P/F costs and the declared stage byte
  domain asserted as DISTINCT counters, not a generic
  throughput/runtime claim.

## 8. Actual field/owner joins and identity law

- The resolved source and the result re-join the ACTUAL
  nested evidence at the boundary BEFORE any copied tag is
  trusted: the actual fixed nested version tags, the actual
  closed bound sets equal to the effective R-carried domains,
  and the nested scope keys recomputed from the nested
  records' OWN actual fields (a copied, stale or foreign tag
  is a fixed typed error). The P selection carried in the
  actual Q result is joined to the state: lineage key and
  non-bool revision agreement, closed container/class fences
  over the witness facts, count within the unchanged 1024
  ceiling BEFORE any membership iteration, and EVERY
  retained witness fact bound by identity to the actual state
  `root_facts` (an extra value-equal DETACHED clone is
  refused; a missing authority field is guarded before read).
- The constructors enforce closed local shape, scope and
  association law only — no authentication, and NO uncharged
  full original proof/history traversal is hidden in a
  constructor (closed O(1) actual-field existence/class/
  scalar/count gates precede every dereference of the
  touched nested records, with fixed private validation
  errors).
- The derivation is pure and idempotent for a fixed input:
  fresh result objects with identical canonical serialization
  (pure data evidence, not a wire-byte proof). The stable R
  scope key is unchanged across a GENUINE accepted transition
  that advances the carried revision; a stale copied
  namespace/state key pair is refused by the actual integrity
  law, and a coherent rekeyed unsupported version pair fails
  the version fence (scope identity alone is not version
  support).
- The operational `str`/`repr` of the result, the resolved
  source and every carried nested record is a FIXED
  non-echoing rendering: nested occurrence/owner objects are
  never formatted (fixed placeholders and metadata only).

## 9. Privacy and purity

- Operational representations stay fixed non-echoing: the
  distinct ROOT body canary, the nonroot member canary, the
  marker, the distinct call ID and the identity/model
  canaries are absent from every R str/repr surface (result,
  resolved source, diagnostics, carried Q/F/E evidence). The
  fixed private errors (the closed unknown kind variant, the
  nested field deletions, the detached extra-witness forge,
  the malformed state object) carry NO canary content in
  str/repr on a genuine READY fixture whose retained root
  text and nonroot member actually carry the canaries.
  These canaries are known-synthetic source/ID evidence: they
  prove the tested representation surface on the tested
  paths, NOT a blanket no-secrets claim about untested
  surfaces.
- No host IO anywhere on the R public surface: after
  fixture/import setup, the closed 24-facility filesystem/
  socket/process trap covers the factory, bootstrap,
  issuance, observation (with the ACTUAL prebuilt request
  object passed to the public operation), receipt,
  selection, the F derivation and the R derivation over
  `ready` / `root_currentness_unproven` /
  `root_authority_conflict` (actual public P conflict) /
  `refused` (foreign scope, version, malformed bounds,
  over-bound and source-resolution outcomes) and the
  malformed-state error, on BOTH read endpoints and BOTH
  admission modes; the original request payloads' canonical
  serialization is unchanged afterwards (pure data evidence,
  not a wire-byte proof).

## 10. Limitations

- The API is graph-only and INERT: it is never active in
  adapter execution, earns no admission, no compiled cache,
  no runtime or HTTP readiness, and no v1 profile behavior.
- It is PENDING strategic review at its bounded graph-only
  scope; acceptance of this slice does not accept whole 018,
  the later admission/full-result consumer, or 019-024, all
  of which remain mandatory. R graph/source-scale results
  (including the measured multi-dependency history fixtures)
  are source-pinned baselines, not final acceptance of the
  consumer's own substantial-source and whole-operation
  resource evidence.
- The accepted F law, the accepted Q law and all old H/O/I/P
  public boundaries are unchanged, including the honest old-I
  refusal of region-version state and every earlier NOT
  ACCEPTED/PARTIAL decision.

## 11. Tests

- `tests/test_root_region_graph.py` (210 cases): the durable
  ORIGINAL-API matrix over BOTH read endpoints and BOTH
  admission modes on legitimate state earned through the
  actual public P APIs — A the acquisition and source-shape
  positives (the genuine public P->R READY bootstrap, the
  mixed-region v2 and whole-read READY shapes, the root-
  position variants, the Unicode nonroot prefix, the CRLF and
  exact empty root, the proven multi-member A/root/B
  three-segment carrier, and the real synthetic native
  multi-piece process/chunk positive with the original EXEC
  owning record, frozen causal parents and original piece-
  producer identity); B the graph semantics (the genuine
  old-bytes revert restoring the earlier version under the
  selected root, historical retention, nonroot version change,
  the closed nested version tags, multi-source withdrawal of
  ONLY the removed owner's edges/certificates with surviving
  alternates, cycle-only reachability removal, the selected-
  root-owned opaque certificate withdrawal/restoration with
  same original group/proof refs, and least AND/OR depth and
  max_depth recomputation); C the combined-frontier and
  evidence-law controls (joint frontier unproven with no
  source, child-of-one blocked, joint coverage restoring
  ready with all dominated witnesses retained, dominated-
  opaque restoration, the actual authority conflict mapping,
  nonroot-only opaque ready, delayed results and old-request
  replay without rollback, the P-unsupported COMPLETE root
  shape (repeated root operands are unsupported uncertainty,
  not a positive), the unissued root-bearing nonblocking/late
  receipt versus issuance alone, and the whole AND region
  descendant-of-all restoration, with the target-reach spies
  on the non-ready mapped outcomes); D the malformed/forged/
  coherent-rekey gates (the genuine public READY positive
  first, then the public derivation boundaries, foreign
  scope/stale keys, the stale-version fence and the coherent
  rekeyed unsupported version, the forged source and nested
  joins with the bounded existence-before-dereference fences,
  the 12 numbered public state-level forged channels (the
  fixed typed private state boundary for the bad D record, the
  mapped ACTUAL Q foreign-scope refusal for the forged D
  history key, and the actual P validation problem or mapped
  result conflict for the remaining channels — no P selection,
  no source or F, the exact bad state retained), the source/owner/producer field-deletion
  fences, the P-selection value/count/association fences, the
  native poll producer alias, and the Unicode pre-encode
  path); E the work boundaries (the full-operation cap first-
  over, the ACTUAL independent P-domain and Q-local/F-
  subtree discriminators with measured public positives, the
  source precharge and pre-slice statement-entry sentinels,
  the inherited per-batch and retention-count domains, and
  the honest constructor-only own-diagnostic first-over where
  the public first-over is unreachable); F the measured
  scale and history (the 32768/65536 READY and 131072 honest
  R-total refusal with the actual returned-F difference
  root-only versus mixed, and the multi-dependency/version-
  history shape at 32768 bytes with the measured R/Q/P/F
  costs and stage byte domains as distinct assertions); G the
  invariants, privacy, purity and error surfaces (idempotent
  derivation and stable scope key versus the carried revision
  with a GENUINE accepted transition, the privacy repr
  canaries with the operational-exception and distinct-
  nonroot-source surfaces, the closed host-IO purity surface
  across the actual public outcomes with the actual prebuilt
  request, and the fixed private errors omitting canaries on
  the genuine READY fixture).
- The existing H/O/I/P/Q test suites are unchanged and
  passing; the actual P core and the public Q wrapper
  behavior are unchanged (the narrow private charged-core
  seam is AST-identical to the extracted body); no R
  admission/runtime readiness is claimed.

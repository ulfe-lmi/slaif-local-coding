# Root-authority lineage contract (objective 018, slice h)

`ROOT_LINEAGE_CONTRACT_VERSION = "cache-root-lineage/v1"`.
`ROOT_LINEAGE_POLICY_VERSION = "root-lineage-policy/v1"`.
`ROOT_LINEAGE_MIXED_OBSERVATION_VERSION = "root-lineage-mixed-observation/v1"` (018-o mixed observation, section 5a).

The 018-p root-region authority producer is a SEPARATE explicitly
versioned contract (the `root_region_lineage_models` /
`root_region_lineage` modules), documented in
`docs/CACHE-ROOT-REGION-LINEAGE-CONTRACT.md`; this contract's old
H law is unchanged by it.

This contract binds the INERT root-authority-lineage slice
(`src/slaif_local_coding/constitution/bundles/`:
`root_lineage_models`, `root_lineage`, and the public entries
`bootstrap_root_lineage` / `observe_root_lineage` /
`register_root_issuance` / `register_root_receipt` /
`select_current_root` / `observe_root_lineage_mixed` (018-o, section 5a), plus the standalone charged
`validate_root_lineage_state`). It composes, over bounded ORIGINAL
GraphRequest batches, the accepted 017 observation, the accepted
018-a root/workspace binding law and the accepted 018-d
causal-occurrence ledger (re-derived under the namespace's ACTUAL
effective bounds, through PRIVATE charge seams with unchanged
public behavior) into ONE pure versioned ROOT-LINEAGE state machine
over the immutable `RootLineageState`. The 018-h slice is
IMPLEMENTED and ACCEPTED at its bounded inert scope WITH PROCESS
QUALIFICATIONS (strategic decision
`S/reviews/018-h-decision.md`): like the accepted 017,
018-a..g slices it is pure, bounded and never active
in the adapter runtime; no command string is executed and no
model/native/client/service facility is started. It earns the
explicit same-root REFRESH/AUTHORITY-LINEAGE mechanism at its
bounded scope (genuine versions of the SAME effective root earned
from original complete reads plus trusted causal evidence, with a
derived current-root selection); it does NOT implement
current-root graph/admission composition (a later mandatory
same-018 slice consumes this interface), and no runtime,
compiler-hit, recovery, wire or root-aware-admission claim is made.
The 018-o mixed-observation extension (section 5a: the
`observe_root_lineage_mixed` entry plus
`ROOT_LINEAGE_MIXED_OBSERVATION_VERSION`) is IMPLEMENTED and
ACCEPTED at its bounded inert scope WITH PROCESS QUALIFICATIONS
(strategic decision `S/reviews/018-o-decision.md`); the 018-p
root-region authority producer (separate contract above) is
ACCEPTED at its bounded inert producer scope WITH PROCESS
QUALIFICATIONS (strategic decision `S/reviews/018-p-decision.md`);
the 018-q root-region currentness slice (separate contract
`docs/CACHE-ROOT-REGION-CURRENTNESS-CONTRACT.md`) is the pure
QUERY above the 018-p state — an unresolved MAXIMAL trusted root
uncertainty blocks current-root usability while dominated
historical uncertainty is retained, without minting root
authority or advancing a revision — and is IMPLEMENTED and
PENDING strategic review at its own bounded inert scope; whole
018 remains open (the next same-018 consumer round must consume
the legitimate new region state into the actual graph/admission;
whole-018 review required before merge) and 019-024 remain.

## 1. Namespace, scope keys and caller trust

- `RootLineageNamespace` derives from the ACTUAL accepted
  `CausalHistoryNamespace`: every ACTUAL field (principal/session/
  repository/route, model identity, config fingerprint, workspace,
  mode, lineage_id, BOTH admission scope keys, the ACTUAL D history
  key, the SEVEN actual D version fields, the ACTUAL D bound sets:
  history/proof/graph/observation/admission) plus the two NEW H
  versions and the NEW `RootLineageBounds`. The NEW `lineage_key`
  is recomputed from ALL actual fields on EVERY construction
  (factory AND direct); a forged, stale or borrowed key refuses at
  construction (fixed error). A coherent direct construction with
  recomputed keys but an UNSUPPORTED actual contract/policy version
  is refused by EVERY transition AND the selection query (fail
  closed, no false positive over acquired source).
- Object construction is NOT authentication: this is an internal
  trusted boundary, never a public body/header authority path.
  Errors and operational reprs never expose identity values,
  source, markers or private IDs (fixed placeholders); no
  anonymous fallback, no cross-scope reuse.
- The new state WRAPS the actual D state (`d_state:
  InstanceOf[CausalHistoryState]`, the retained validated instance;
  ZERO nested Pydantic revalidation, dict input refused) and the H
  revision stays in EXACT 1:1 with the wrapped D revision. A new H
  state is NOT authority to pass a forged replaced D state to
  public F/G: the standalone charged validator (section 10)
  recomputes ACTUAL fields before positive use.

## 2. Bootstrap and root anchor law

- `bootstrap_root_lineage` runs the ACTUAL accepted D bootstrap
  under the STRICT old root law: the legitimate effective
  Responses AGENTS envelope with exact source bytes, workspace and
  first original spans; the exact EMPTY root is legal; rootless
  empty state refuses `REFUSED_NO_ROOT`; a competing root read or
  a different root path/directory/workspace inside the bootstrap
  batch keeps the exact old refusal (no relaxed envelope law and
  no refresh acquisition at bootstrap).
- The accepted state is wrapped with the bootstrap ENVELOPE fact
  (ENVELOPE provenance: anchor digest + workspace + source byte
  length; always authoritative, never "issued" in the read sense)
  at H revision 1 (the composition origin). The retained
  `RootAnchor` identity and the original envelope spans are
  preserved by identity forever; no synthetic root message is
  ever inserted.
- One root path `AGENTS.md` in the evidenced workspace;
  rootless continuation reuses the ACTUAL retained immutable
  bootstrap context (no re-inspection, no synthetic request).

## 3. Refresh source law (acquisition)

- A REFRESH SOURCE must be an ACTUAL accepted complete whole
  SINGLETON read of the EXACT normalized root path on EITHER read
  endpoint, using the unchanged earned read grammars: one member
  occurrence, the member's normalized path equal to the root
  filename, ONE attributable proven region covering the COMPLETE
  source (the single segment's `member_digest` is proven, member
  positions exactly `(0,)`). The explicit filter is applied to
  NEW retained occurrences: multi-member complete bundles,
  isolated root segments in larger bundles, repeated-root
  operands, opaque/mixed bundles, partial/truncated/nonzero/
  unpaired/unsupported reads grant NO refresh source.
- SOURCE acquisition and AUTHORITY are separate (section 4):
  acquisition retains the occurrence and its original proof,
  pieces, initial-EXEC owner and positions verbatim in the D
  occurrence; it never mints authority. No special new client
  read command; no caller-supplied proofs, digests, flags, body
  or header trust fields are ever acquisition or anchoring.
- The private seam relaxes ONLY the in-kernel whole-pass
  COMPETING_ROOTS refusal for a context-coupled run (a proven
  singleton root-path member read with a digest different from
  the batch root digest is retained instead of refused); every
  old public caller (plain D, B, C, F, G) keeps the EXACT old
  behavior, interfaces, versions and recipe bytes (no context ->
  no change).

## 4. Authority law

- `issued(fact)` = a retained trusted ISSUANCE exists for the
  fact's read call; `authority(fact)` = issued AND the
  occurrence is anchored (frozen parent links exist) AND
  `CAUSAL_ROOT_FACT` lies in the ACTUAL transitive parent closure
  of the occurrence. Both flags are DERIVED and re-derived for
  ALL root facts after EVERY accepted D transition
  (observation, issuance OR receipt -- including a receipt on a
  NONROOT ancestor that opens a previously unproven descendant's
  bootstrap path) from the actual issuance/parent facts, charged;
  the stored flags are never trusted.
- A trusted read whose frozen parents reach bootstrap but not
  another known concurrent root update is a legitimate BRANCH,
  not automatically latest: maximal selection (section 6) handles
  it as such. An issuance whose ancestors never reach bootstrap
  cannot mint inherited root authority.
- SOURCE acquisition + a matching valid LATE receipt earns
  authority for a complete but unissued retained root read; a
  bad/cyclic/mismatched receipt refuses atomically (accepted D
  receipt laws, exact prior state) and leaves all flags
  untouched. Read ID novelty, receipt arrival, HTTP positions,
  digests, revisions and body flags are never clocks or trust.
- Complete but UNISSUED retained root reads are honest UNPROVEN
  source facts: they are retained, never selected, and expose
  the fixed `ROOT_SOURCE_UNPROVEN` limitation in the selection
  result; they never supersede the governing root and cannot
  justify a known-envelope status.

## 5. Known envelope contexts and replay

- The pre-batch KNOWN root digest set is computed and charged by
  H BEFORE the D core: the bootstrap anchor digest plus the
  actually EARNED authoritative root fact digests (retained
  complete bytes alone never justify an envelope).
- Known historical and known refreshed SAME-SCOPE root envelopes
  are context/source evidence only, never fresh root events:
  their replay (old, shifted, or known-new) is an idempotent no-op
  -- no rollback, no invented competitor, no revision advance.
  Different known source versions may coexist in replayed
  history; no freshness is chosen from message positions.
- An UNKNOWN changed envelope byte set WITHOUT independent
  accepted root-read authority is a fixed whole-transition root-
  authority refusal (`REFUSED_ROOT_AUTHORITY`,
  `ENVELOPE_UNPROVEN`) with the EXACT prior H state: the batch is
  marked envelope-deferred in the private collector, earns its
  source facts, and is atomically verified against
  {pre-batch known} UNION {this batch's NEW eligible singleton
  root-read digests} after the D core returns an accepted
  candidate. A same-batch independently earned authoritative
  root read establishes the matching envelope's known-source
  status atomically; the envelope itself grants NO ordering.
- Foreign scope, malformed envelope, or a competing-root
  bootstrap still refuse (old law). The acquisition context is
  the IMMUTABLE bootstrap anchor, independent of the selected
  governing root: while selection is in conflict (or before any
  root-read facts exist), rootless batches remain fully
  observable, so later child-of-ALL evidence can resolve the
  conflict. `CAUSAL_ROOT_FACT` ALWAYS means the ORIGINAL
  bootstrap, never the selected latest root.

## 5a. Root-aware mixed observation (018-o, inert)

- `observe_root_lineage_mixed(h_state, ns,
  expected_revision, requests)` is a NEW explicitly named PURE
  operation of this module (the 018-o slice, versioned by
  `ROOT_LINEAGE_MIXED_OBSERVATION_VERSION`), taking the SAME
  retained H state and ACTUAL root-lineage namespace as
  `observe_root_lineage` plus an original GraphRequest batch
  (a continuation without a new envelope) and returning the same
  transition evidence shape (the actual
  `RootLineageTransition` fields `state` / `outcome` /
  `diagnostics` / `d_transition` / `new_root_facts`; a refused
  H result over an accepted D candidate carries that ACTUAL
  accepted D candidate by identity in `d_transition` as
  discarded evidence). All existing public B/C/D/E/F/G/H/I
  signatures, defaults, schemas, version tags, recipe bytes,
  behavior and independent cap domains remain intact; this round
  wires no adapter runtime or settings (the operation/version is
  documented for later runtime/recovery configuration identity).
- Gates: the existing namespace preflight, CAS/revision,
  state-shape and version gates and the standalone charged
  validator (section 10) run BEFORE any compatibility
  interpretation, exactly as for `observe_root_lineage`; a
  cross-namespace, stale-revision or malformed H state refuses
  with the EXACT prior state before positive compatibility work.
- Source compatibility: the pre-batch KNOWN root digest set
  (section 5: the bootstrap anchor digest plus the actually
  earned authoritative root-fact digests) may match ANY
  independently authoritative known version of the SAME
  effective root — including HISTORICAL non-bootstrap versions
  retained after a later refresh — as ordinary SOURCE evidence
  (the section 4 acquisition/authority separation is unchanged).
- A foreign-to-bootstrap mixed root member earns the
  source-acquisition exception only with a complete accepted
  proof, EXACTLY ONE normalized root-path occurrence across the
  proof's requested members (charged occurrence count; a second
  root-path operand, proven or opaque, earns no exception) and a
  proven attributable whole-source region for that member (the
  member digest is proven); its member digest must match the
  known set. Repeated root operands and opaque/partial/
  truncated/nonzero/unsupported reads earn NO NEW exception or
  authority here; their exact old acquisition/limitation
  semantics remain unchanged (no read grammar is expanded).
- Provisional pending retention: initially unknown foreign root
  digests are retained ONLY inside this operation (the private
  context's `deferred_mixed_digests`), deferred until the actual
  D observation AND the H singleton-fact/authority derivation
  complete (the established bounded deferred-verification
  pattern, section 5, reused). A pending digest is accepted only
  if an INDEPENDENT authoritative complete whole singleton root
  read establishes that digest in the SAME batch. A mixed proof,
  a changed envelope, an unproven source, a caller-supplied
  digest/header or body flag never self-authorizes; the
  singleton-only governing-fact constructor is preserved.
- Deterministic refusal precedence: the envelope-defer
  verification runs FIRST (an unknown changed envelope without
  independent same-batch authority still refuses
  `REFUSED_ROOT_AUTHORITY` / `ENVELOPE_UNPROVEN` ahead of the
  mixed-pending resolution); then the mixed-pending resolution:
  an unresolved foreign digest yields `REFUSED_ROOT_CONFLICT` /
  `COMPETING_ROOTS` with the EXACT prior H state. An accepted D
  candidate discarded by the H result remains INTERNAL discarded
  evidence (no partial H state publication). A known root
  conflict may retain compatible source evidence while the
  ordinary I consumption of the SAME resulting state still
  returns the explicit conflict with no ready graph/admission.
  Singleton descendant-of-all resolution is preserved.
- Identity preservation: the original requests, the bootstrap
  anchor, the D namespace/history identity, the original proof
  root binding (which stays at the immutable bootstrap), proof
  identity, source spans, occurrence IDs and frozen ancestry are
  all preserved. The proof root binding and the proven member
  digest have different purposes (binding identity versus member
  content). Mixed reads never add or advance governing root
  facts; actual subsequent validation, issuance, observation and
  replay consume the legitimate resulting state, and ordinary I
  consumes that SAME state directly.
- Resource law: root-occurrence counting, candidate/defer
  attempts (counted BEFORE dedup), allocation and final
  authority-membership work are charged on the SAME H outer
  coupled to the ACTUAL D work; the pending-set snapshot (the
  frozenset copy of the retained pending digests) is precharged
  on the SAME H outer BEFORE the copy (closed bound: one unit per
  retained pending digest plus one allocation unit) and then the
  copy runs fully prepaid; pending metadata is bounded by the
  ACTUAL existing B/D candidate/incoming capacities before
  retention. Inherited D-local domains, limits, the
  original-batch domain and the cumulative domain stay distinct
  and unchanged.
- The OLD public `observe_root_lineage` keeps its EXACT
  post-refresh foreign mixed-root refusal with the unchanged
  old behavior, interfaces, versions and recipe bytes for
  every old public caller (the old H accepted-tail source was
  refactored during 018-o without behavior change); only this
  new named operation changes behavior, and only at its own
  scope.

## 6. Partial-order current-root selection

- `select_current_root` is a PURE bounded derived query with its
  OWN one-operation outer ledger; it never advances any revision,
  never mutates state and never manufactures a root.
- AUTHORITATIVE facts = the bootstrap fact plus every fact with
  derived authority. DOMINANCE is causal over ONLY the frozen
  transitive parent evidence: fact B dominates A iff A is the
  bootstrap anchor or A's occurrence is a STRICT ancestor of
  B's occurrence. A child of one conflicting branch cannot
  dominate (remove) the other branch; a genuine child of ALL
  relevant branches dominates all of them.
- CAUSAL dominance and CONTENT compatibility are separate: the
  MAXIMAL authoritative witnesses are compared by ACTUAL source
  digests. ALL maximal witnesses with ONE equal source digest are
  `ok` (the selected source with ALL compatible maximal
  originals retained, e.g. equal incomparable bytes); any
  differing maximal source digests are `root_content_conflict`
  with NO selected current source (at least two retained maximal
  witnesses, at least two differing digests; an accepted state
  change may carry a conflict -- conflict is NOT resource
  exhaustion). No authoritative fact at all is the honest
  `no_selected_root`.
- Delayed older receipts never override a proven descendant
  (frozen edges only; no lexical/receipt-time winner). A new
  genuine descendant revert may reuse old bytes but is a NEW
  event with its own fact. Retained unproven root reads are never
  selected and expose `ROOT_SOURCE_UNPROVEN` in the result.
- Budget/foreign/version/malformed inputs are a fixed typed
  `refused` result exposing the exact limitations -- a refusal is
  never relabelled as a root absence.

## 7. Retained records and provenance law

- The original `RootAnchor` is preserved by identity and every
  historical proof root binding and occurrence ID is preserved
  verbatim (the D state is retained by reference, never
  rewritten). New root source provenance is a discriminated
  ACTUAL READ variant (`occurrence_id` + call identity + endpoint
  + the original whole-read digest/byte-length binding),
  distinct from bootstrap ENVELOPE provenance; a read fact's
  source digest/length MUST equal the retained original binding
  -- fact CONSTRUCTION references that retained binding and
  performs no source re-hash of its own.  This is distinct from
  the bounded integrity RE-validation (section 10, step 5): the
  standalone validator re-checks the retained proof's digest
  from the single charged owned encode under the source cap,
  ONE bounded rehash per retained proof integrity validation
  (the anchor step performs its own bounded anchor rehash),
  before any positive interpretation.
- A `RootOccurrence`/`RootAnchor`/envelope is NEVER fabricated
  around read text; root spans are never rewritten; unchecked
  `model_copy` cannot disguise a variant (the standalone
  validator recomputes); original root messages are never
  deleted or modified to appease the old observer.
- Full original proofs are retained by BOUNDED immutable
  reference (the D occurrence and its verbatim accepted 018-b
  proof), never by a copied whole proof per witness; proof
  references do not authorize hidden repeated source walks.

## 8. H-private result/proof binding coherence and ownership join

- The accepted 017/D result builder derives EVERY piece producer
  binding from the SAME original request: the exec piece carries
  the record's own (endpoint, tool, argument fingerprint) and
  every poll piece carries (SAME request endpoint, the poll's
  tool, the poll's argument fingerprint); the original complete
  proof endpoint corroborates that request endpoint.
- The OLD public D observed-binding validator enforces
  observed-vs-OBSERVED consistency only: a single retained record
  with a flipped piece endpoint has no other retained evidence to
  contradict and is (correctly, for the OLD law) coherent there.
- The NEW H composition therefore carries an H-PRIVATE charged
  cross-record check inside the standalone validator: for EVERY
  retained result record, each piece producer binding's endpoint
  family must equal the record's own endpoint (charged per result
  and per piece on the SAME outer, BEFORE the comparison). A
  flipped piece endpoint is an incoherent result binding
  (`RESULT_CONFLICT`), never a new trust source; a second
  retained chain contradicting the same poll ID is refused by
  the OLD public D validator itself (observed-vs-observed).
  The old public D behavior, schemas, versions and refusals are
  UNCHANGED by this H-private law.
- The SAME H-private seam carries the completed-occurrence/
  result OWNERSHIP JOIN (validator step 4c): the accepted
  017/D builder pairs EVERY completed occurrence with its
  complete owning result record (keyed by the read's own call
  ID), and that record retains the EXACT producing-call
  association of the occurrence's RETAINED proof pieces,
  aligned by piece index -- the complete record's piece facts
  ARE the exact original piece facts of the complete proof
  (piece index, character and byte lengths re-derived), and the
  initial piece is produced by the read's OWN call (its binding
  equals the record's actual known owner endpoint/tool/
  fingerprint binding).  A missing or incomplete owning result
  is an incoherent binding (`MALFORMED_BINDING`); a changed
  piece producer ID, a count mismatch, a mismatched initial
  owner binding or a mismatched piece length is a
  `RESULT_CONFLICT`.  Such an erasure changes nothing in the
  retained proof and no observed-vs-observed D contradiction
  exists there -- the original poll ownership is join evidence,
  and the retained proof alone cannot re-prove it.  The old
  public D behavior is UNCHANGED.
- Ordering: the charged owning-result index is built BEFORE
  the step 5/6 pass, and each occurrence's join is evaluated in
  that pass ONLY after the occurrence's ACTUAL proof integrity
  validation has succeeded -- the proof is walked exactly once
  in its source integrity (ONE source validation per proof; the
  join re-traverses only the charged piece metadata, never the
  source) and malformed proofs keep their typed shape refusals
  instead of reaching the piece fields first.
- The durable repository control (section 12) covers the
  ACTUAL native positive (retained original poll ownership
  complete and proven), the single producer-ID rewrite and the
  result-omission corruptions, each refusing the standalone
  validator, the current-root query, the subsequent genuine
  trusted descendant issuance AND the descendant read that
  would otherwise reuse the original poll ID and mint new root
  authority -- every refusal with the EXACT prior state while
  the OLD public D validator stays None (the H-private gap).

## 9. Bounds and the shared work law

- NEW `RootLineageBounds` (defaults ARE the hard ceilings;
  STRICTER positive values allowed, wider refused at
  construction): `max_root_facts` 1024 (bootstrap + EACH distinct
  retained complete supported root-read candidate, including
  unproven; replay never adds), `max_retained_root_source_bytes`
  16777216 (logical exact UTF-8 source per retained root fact,
  bootstrap once, even when proofs share underlying immutable
  storage), `max_total_work_units` 1048576 PER operation,
  `max_diagnostics` 64 PER result. These are source/work/
  diagnostic units -- never tokens, cache occupancy or RSS.
- ONE outer H ledger per operation (bootstrap, observation,
  issuance, receipt, selection each their own; a supplied query
  override bounds is fresh actual-field validated BEFORE any
  fuel is read from it). The outer is COUPLED to the ACTUAL D
  work through the private charge seams: every actual D
  `work.unit()` debit first debits the H outer (a crossing is an
  H over-bound refusal with the EXACT prior H state) and then
  debits the ACTUAL D ledger. D LOCAL work (`max_work_units`,
  argument bytes, retained source bytes, diagnostics) keeps its
  own INDEPENDENT domain: no global minimum, no per-request/
  group/fact resets, and the original-batch
  `GraphBounds.max_requests` domain (per batch, versus
  cumulative retention) is preserved.
- Charged BEFORE each operation: every request before its 017
  pass (initial and derived re-observation), every root
  occurrence measurement, every inspected candidate and every
  retained bundle in the private collector, every D work unit
  (1:1), every retained root fact (counted BEFORE retention),
  every fact in the pre-batch known-digest walk and the post-
  acceptance flag re-derivation, every parent-link in parent-map
  construction, every edge traversal in every ancestor closure,
  every maximality dominance pair attempt, every output record/
  copy/dedup/sort step (charged stable merges per the accepted
  018-g comparison-charging law; no decision-tree lower bound
  anywhere), and every step of the H-private result/proof
  binding coherence walk.
- Source character/UTF-8 lengths are preflighted BEFORE any
  slicing/encode/hash/copy: the O(1) character count is checked
  against the ACTUAL single-source and retained-root byte caps
  first; the charged no-copy byte walk early-exits at the ACTUAL
  cap (a crossing is the inherited source-domain refusal BEFORE
  any owned encode/hash); retained root facts are counted before
  retention. No nested Pydantic revalidation secretly rewalks
  full historical source per retained reference.
- Every refusal emits no partial selected snapshot and keeps the
  EXACT prior H state (by identity). No TTL/LRU/eviction/
  destructive pruning to fit a bound.

## 10. Atomicity, CAS and the standalone charged validator

- Every transition takes the immutable prior H state plus an
  expected revision (atomic CAS) and returns the new state plus
  fixed outcome evidence. One accepted H state change increments
  the H revision EXACTLY once; REPLAYED/REFUSED preserve the
  EXACT prior H state and revision; revision overflow refuses
  before mutation. Both H and D revision before/after pairs are
  carried by the transition (documented, never treated as a
  source clock).
- The standalone charged validator
  (`validate_root_lineage_state`) is the ONE cross-record law,
  run under the ONE outer BEFORE any positive interpretation in
  every API: (1) the NEW H record shape law (integral revisions
  in exact 1:1 with the wrapped D revision, 64-hex keys, the
  root-facts tuple shape, the sorted/deduplicated provenance
  identity, every fact's intrinsic fields); (2) the effective
  retention bounds (fact count and logical exact UTF-8 root
  source bytes, bootstrap once); (3) the ACTUAL root-anchor
  source integrity (the accepted F anchor law, H-owned: field
  shapes, the O(1) character preflight, the charged no-copy
  byte walk with early exit, the digest re-checked from that
  copy, the workspace compared to the ACTUAL namespace, the
  retained occurrence root bindings re-verified); (4) the
  ACTUAL D cross-record integrity through the real accepted D
  validator in its own bounds domain; (4b) the H-PRIVATE
  retained result/proof binding coherence (section 8); (4c)
  the H-PRIVATE completed-occurrence/result ownership join
  (section 8: the charged owning-result index is built before
  the 5/6 pass and each occurrence's join is evaluated in the
  5/6 pass ONLY after that occurrence's actual proof integrity
  succeeds -- missing/incomplete owning result
  `MALFORMED_BINDING`, producer/count/owner/length mismatches
  `RESULT_CONFLICT`; malformed proofs keep their typed shape
  refusals and the proof's source integrity is validated once
  per proof, the join re-traversing only charged piece
  metadata); (5) the
  ACTUAL earned proof-record integrity for EVERY retained
  occurrence exactly once (proof shape/version/grammar fences,
  scalar/container shape before len/iteration/arithmetic,
  per-snapshot collection prefights, member alignment, carrier
  law, segment/member/span laws, marker shapes with the
  original statement-index domain, the single-source byte cap
  fence before any character inspection, the ordered totals and
  the digest re-checked from the single owned encode); (6) the
  COMPLETE fact inventory (1:1 between eligible singleton
  root-read occurrences and retained H read facts, both
  directions -- an omitted earned fact is an incoherent binding,
  never a silent rollback); (7) the per-read-fact provenance
  binding and the DERIVED flags re-derived from the ACTUAL D
  state (stored flags never trusted).
- Bound-state/factory/direct-construction revalidation thus
  recomputes ACTUAL fields/versions/keys and refuses
  forged/foreign/coherently-unsupported instances and malformed
  records before positive interpretation; there is no global
  mutable registry.

## 11. Privacy and purity

- No host IO after fixture/import setup (no filesystem, socket
  or process facility) on ANY guarded normal or negative path,
  including the trusted issuance/receipt operations, the
  selection query and both read endpoints; the original
  payloads are byte-unchanged.
- The operational `str`/`repr` of every namespace, state, fact,
  provenance, occurrence, result record, transition and
  selection result is free of source text, private IDs, markers
  and identity values (fixed placeholders and lengths/digests
  only); diagnostics are the fixed closed enums plus counts; no
  raw content, prompts, credentials or private URLs in any
  operational output.

## 12. Tests

- `tests/test_root_lineage.py` (209 cases): the
  durable ORIGINAL-API matrix over BOTH read endpoints and BOTH
  admission modes -- A bootstrap (normal/EMPTY root)/idempotent
  envelope/rootless read and v1 -> trusted descendant v2 ->
  genuine descendant v1 revert with rootless continuation after
  each step; B old/shifted and known-new/historical-old envelope
  replays after refresh (FIRST provenance, no revision
  advance/rollback), the unknown changed envelope whole-
  transition refusal and the independent same-batch refresh
  read plus matching new envelope atomic success; C equal
  incomparable witnesses all retained, differing siblings in
  conflict, child-of-one still conflicting (unequal bytes) and
  agreeing on equal surviving bytes, child-of-all resolving,
  delayed older read/receipt never overriding a proven
  descendant, unissued source then matching late receipt,
  unknown-parent/cycle/changed-frontier/same-ID-mutated-binding
  exact refusals; D native initial-EXEC frontier and immutable
  poll owner on pending/poll completion for a root read,
  genuine empty root read, actual Unicode/CRLF source/spans,
  normalized absolute root path versus outside/different-
  directory/workspace (original synthetic frames only, no
  process/client startup); E unrelated/nonroot reads retained
  with their original acquisition binding across refresh, no
  co-occurrence promotion, partial/truncated/nonzero/
  unsupported/mixed/opaque/repeated-root reads granting no
  authority, body/header-like and caller-field trust claims
  cannot mint authority, same-batch known-new envelope binding
  to the ACTUAL bootstrap acquisition; F every NEW bound at-
  limit/first-over with target-reaching pre-copy/iteration
  sentinels, D-local work beneath a larger shared H outer,
  cumulative multi-batch retention versus the preserved
  original batch limit, charged sort/dedup/ancestry/result/model
  validation; G CAS/revision overflow/foreign actual
  namespace/root context/unsupported actual version/forged
  lineage keys or root provenance refusing whole with the EXACT
  prior state, the shared operation-matrix no-host-IO and
  private-repr controls over EVERY exercised success/refusal/
  trusted path (all exercised call IDs and source bodies as
  canaries), the zero-serializer-visit namespace prewalk
  fences, constructor negatives, the retained-native
  owner/binding integrity controls and the retained
  result/proof ownership-erasure join controls (the ACTUAL
  native positive with retained original poll ownership, the
  single poll producer-ID rewrite and the completed-result
  omission, each refusing the standalone validator, the
  current-root query, the subsequent genuine trusted
  descendant issuance and the poll-reusing descendant read with
  the EXACT prior state while the OLD public D validator stays
  None); H full 017 and 018-a..g regressions in the final full
  suite.
- `tests/test_root_lineage_mixed.py` (56 cases over BOTH read
  endpoints and BOTH admission modes): A the known pre-batch
  mixed root member (an independently authoritative known
  version) acquires source evidence with the ordinary-I
  whole-bundle admission and independent original-C canonical
  keys; B the same-batch independent singleton plus mixed read
  across request-order permutations (with the independently
  authorized changed envelope) resolves the pending digest; C
  replay idempotence and equal-byte independent witnesses (the
  final selection facts are the actual facts of the final state;
  cross-state equality only over provenance coordinates and the
  original D occurrence/proof identity); D the known historical
  non-bootstrap mixed source after a later refresh with the
  ordinary-I selected-digest exclusion; E the conflicting known
  authoritative branches (the mixed source matching a known
  branch is retained while I stays explicitly conflicted with no
  ready output; a genuine singleton descendant of all resolves);
  F the unknown-foreign / unissued-singleton-plus-mixed /
  envelope-only / mixed self-authorization refusals with EXACT
  prior state and discarded-evidence semantics (envelope
  precedence first); G1 the boundaryless positive with the
  repeated-root and repeated-opaque-command refusals and the
  nonzero same-cid case; G2 the PLAN_UNSUPPORTED replay
  (REPLAYED with the EXACT prior state) and the
  partial/incomplete/truncated reads ACCEPTED as honest
  incomplete retained result records (no occurrence, no root
  fact; PROCESS_TRUNCATED carried in the D transition
  limitations); H1 the
  cross-namespace / stale-CAS / forged-lineage-key /
  forged-D-history-key / malformed-state gates and the coherent
  unsupported-version (same-D-scope) refusal; H2 the pending-set
  snapshot precharge boundary on the SAME H outer (bootstrap
  state fixture; measured at-boundary success followed by the
  later union refusal, one below refuses before the copy); the
  actual B pending-collection cap at-limit/one-below (measured
  candidate count; below the cap ZERO pending-retention events
  and the exact D refusal mirrored by H); H4 the full mixed-
  operation sequence at the measured minimal cap with the
  crossing step exactly the mixed observation; H5 the privacy
  canary (no source/identity values in any operational output,
  refused paths included).
- The ROOT-executed independent original-API probes (retained-
  native owner/rebinding, late-ancestor, causal selection,
  shape/attribution/byte-cap/K5 prewalk, atomic envelope
  binding, known-envelope replay, D-local outer domain, batch
  cap retention, marker positives, the retained
  proof/result-producer-join negative (and its ordering
  recheck) and the named negative rechecks) retain their EXACT
  recorded source versions and scopes: they are not relabeled
  as final-source broad tests.
  These are ROOT executions, not coding-executed repository
  tests; the durable repository suite above is the in-repo
  regression.

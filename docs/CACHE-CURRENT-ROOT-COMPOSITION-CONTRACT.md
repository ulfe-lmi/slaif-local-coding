# Current-root graph/admission composition contract (objective 018, slice i)

`CURRENT_ROOT_COMPOSITION_CONTRACT_VERSION = "cache-current-root-composition/v1"`.
`CURRENT_ROOT_COMPOSITION_POLICY_VERSION = "current-root-composition-policy/v1"`.

This contract binds the INERT current-root composition slice
(`src/slaif_local_coding/constitution/bundles/`:
`current_root_composition_models`, `current_root_composition`, and
the public entry `derive_current_root_composition`). It takes the
ACTUAL retained 018-h root-lineage state and its ACTUAL namespace
(plus the NEW composition bounds and the ACTUAL inherited H/D/E/F/G
bound sets) and, in ONE pure bounded charged operation, derives the
ACTUAL 018-h current-root selection AND the actual selected-root
source resolution AND the accepted 018-f current graph over a
freshly recomputed least fixed point with the selected root as the
NEW root supplier AND the current admission entries with the
canonical 018-c semantic keys under the selected governing root
digest. This slice is IMPLEMENTED and NOT ACCEPTED (strategic
decision `S/reviews/018-i-decision.md`); the bounded 018-j repairs
(J01 association closure, J02 exact reverse-index law, J03
independent budget domains) were delivered truthfully PARTIAL and
are NOT ACCEPTED against the complete J01/J02/J03 criteria
(strategic decision `S/reviews/018-j-decision.md`); the bounded
018-k repairs (K01 actual nested canonical keys at BOTH parent
boundaries, K02 actual nested row shapes before exact-relation
comparison, K03 genuinely reachable E collection caps with exact
evidence labels) are NOT ACCEPTED against the complete
K01/K02/K03 criteria -- the named 16 probes pass, but the
additional actual nested scalar/authority closure and the E
before-target count evidence remain unmet (strategic decision
`S/reviews/018-k-decision.md`); the bounded 018-l repairs (L01
complete closed nested entry / key-record / ownership metadata
fences at BOTH parent boundaries before any recipe visit, with the
entry / record authority and width joins; L02 independently
derived actual E collection-domain counts with a before-target
charge sentinel) were delivered truthfully PARTIAL and are NOT
ACCEPTED against the complete L01/resource/artifact criteria
(strategic decision `S/reviews/018-l-decision.md`); the bounded
018-m repairs (M01 O(1) count / scalar gates BEFORE any element /
set / sort / hash / serialization work at the leaf and BOTH
parent boundaries, with the closed TEN admission bound-model
fence and the accepted dense group ordering / unique partition
law; M02 the exact accepted JSON serialization byte ceiling and
the reservation-calculation work precharge on the ONE I outer)
were delivered truthfully PARTIAL and are NOT ACCEPTED against
the complete M01/M02 criteria (strategic decision
`S/reviews/018-m-decision.md`); the bounded 018-n repairs
(N01 the retained-content join at the leaf and BOTH parent
boundaries — the entry-local group partition joined to the
ORIGINAL proof segments and the root group to the retained root
digest — plus N02 the byte-aware closed reservation, the
pre-fetch plan segment precharge and the per-site
reservation-calculation closure) are ACCEPTED at their
bounded inert scope WITH PROCESS QUALIFICATIONS (strategic
decision `S/reviews/018-n-decision.md`); the 018-o root-aware
mixed-observation slice (the new pure `observe_root_lineage_
mixed` operation plus `ROOT_LINEAGE_MIXED_OBSERVATION_VERSION`;
a proven mixed root member matching an independently
authoritative known version of the same effective root —
including an independently issued complete whole singleton in
the SAME batch — acquires source evidence while a mixed read
mints no governing authority, unresolved foreign digests keep
the exact COMPETING_ROOTS refusal, and the pending-set snapshot
is precharged on the SAME H outer) is implemented and ACCEPTED
at its bounded inert scope WITH PROCESS QUALIFICATIONS (strategic
decision `S/reviews/018-o-decision.md`; root-lineage contract
section 5a); the 018-p root-region producer adds ONLY the narrow
explicit region-state refusal documented in section 1 (the OLD
composition honestly refuses the NEW 018-p region-version state
before positive work) and is otherwise unchanged (root-region
contract `docs/CACHE-ROOT-REGION-LINEAGE-CONTRACT.md`; the
018-q root-region currentness slice is a separate pure QUERY
over the 018-p state — contract
`docs/CACHE-ROOT-REGION-CURRENTNESS-CONTRACT.md` — that this
composition does not consume; the same-018 consumer round that
must consume the legitimate new region state into the actual
graph/admission is still mandatory). At
its bounded inert scope, like the accepted 017,
018-a..h slices, it is pure, bounded and never active in the
adapter runtime; no
command string is executed and no model/native/client/service
facility is started. It earns the root-aware current
graph/admission composition MECHANISM at its bounded scope (the
current-version/overlap stage of whole 018 that recomputes the root
closure, withdraws/restores entries and canonical root/authority
keys under one outer budget); it does NOT implement compilation,
RAM ownership, replacement, recovery, wire or actual-model
qualification, and 019-024 remain mandatory.

## 1. Inputs, namespace, scope keys and caller trust

- `derive_current_root_composition(state, ns,
  composition_bounds=None, currentness_bounds=None,
  graph_bounds=None, admission_bounds=None,
  lineage_bounds=None)` takes the ACTUAL retained
  `RootLineageState` and its ACTUAL `RootLineageNamespace`; omitted
  bound sets default to the supported defaults. The input is the
  INTERNAL retained-history boundary, never a public supplied
  proof/snapshot/header authority: object construction is not
  authentication, and no caller-supplied selection/current flag
  establishes authority.
- Every supplied override (composition/F/G/E/H) is revalidated
  through FRESH bounded actual-field validation at the NEW I
  boundary BEFORE any fuel is read or any serialization is
  traversed (a `warnings=False` closed serialization of the model
  into a fresh dict through the real validators; a closed
  actual-field shape fence before the first dump). An unvalidated
  or model_copy-mutated bounds record raises a fixed private
  `ValueError`, never interpreted. A private override/pre-graph
  context is validated same-run against the ACTUAL typed context
  and is never public supplied authority.
- The input state is IMMUTABLE and is carried by EXACT identity on
  every outcome: no mutation, no CAS/revision advance, no partial
  graph/entries on refusal.
- The composition scope key is RECOMPUTED from the ACTUAL fields on
  every construction (the exact input D history key and revision,
  the workspace, the selected root digest, the actual H lineage
  scope, the actual lineage ID, every inherited version field, all
  TEN bound sets — the NEW composition bounds, the actual
  currentness bounds, the actual current-graph bounds, the
  inherited graph bounds, the actual admission bounds, the actual
  admission-derivation bounds, the proof bounds, the inherited
  observation bounds, the history bounds and the H lineage bounds —
  plus the contract/policy tags); a stale or forged key is refused,
  never retained. Coherent but UNSUPPORTED actual versions refuse
  `refused_version_conflict` / `VERSION_UNSUPPORTED` before any
  positive interpretation; foreign scope and malformed state
  refuse with the exact prior state.
- Narrow 018-p region-state refusal boundary: the old result
  schema carries an `InstanceOf[RootLineageState]` and cannot
  hold a NEW 018-p `RootRegionLineageState` (the separate
  `cache-root-region-lineage/v1` contract) without broadening the
  old positive law, so the public entry raises a FIXED private
  `ValueError` (a typed fail-closed refusal, tested in
  `tests/test_root_region_lineage.py`) at the first state-shape
  gate BEFORE any old positive work or result construction; all
  old positive behavior, types, schemas, versions and recipes
  remain intact, and no new I graph/admission readiness for the
  region state is claimed in the 018-p producer round.
- Early fences are O(1) in the historical state and precede ANY
  scan or copy; the ACTUAL state history key is compared against
  the ACTUAL namespace history key before any derivation work.

## 2. Selection, source resolution and the new root supplier

- The ACTUAL same-run 018-h selection is derived in the SAME
  operation under the H selection's OWN one-operation outer (the
  H/D-local domains stay independent): causal-maximal authoritative
  witnesses, equal-byte compatibility retaining EVERY compatible
  maximal original witness with its original coordinates, and
  differing maximal sources an explicit selection conflict with NO
  selected current source.
- The ENVELOPE source resolves from the ACTUAL immutable D root
  anchor (the original bootstrap); the READ source resolves by the
  ACTUAL selected witness occurrence in the SAME retained D state,
  cross-checking exact occurrence identity, endpoint, source
  digest and byte length against the retained original
  `proof.source_text` binding. A `RootAnchor`/`RootOccurrence`/
  envelope is NEVER fabricated and no copied replacement D state
  is ever built.
- The selected text becomes the NEW root supplier in a FRESHLY
  recomputed 018-f least fixed point (never seeded from any
  previous snapshot): the ACTUAL 018-e nonroot currentness and
  group-ownership laws are preserved, the selected governing root
  is NOT overridden by 018-e root-path observations (E supplies
  the actual nonroot currentness/ownership law only), and a root
  refresh alone creates no newer nonroot observations.
- Withdrawing the root->A edge withdraws cycle-only A/B
  descendants and their owned edges and certificates; independent
  surviving complete alternates keep reachability. Restoration
  reuses the ACTUAL retained current nonroot originals (no fake
  reread). Availability for unreachable possession is retained and
  the least AND/OR depths and effective max_depth are recomputed
  after withdrawals.
- Root compatibility for admission uses the ACTUAL selected
  governing digest, never the bootstrap digest as freshness:
  proven root groups are filtered against the ACTUAL selected
  digest BEFORE entry planning (a stale old root read never
  escapes as a current root authority or ordinary entry), while
  valid nonroot segments of the same bundle are preserved (the
  accepted G lean isolated rule; no new greedy isolation rule).
  Compatible same-bytes root-path reads of the SELECTED digest
  admit the ordinary AGENTS.md file entry exactly as in the
  accepted G law.

## 3. The root entry and the canonical keys

- Exactly ONE first-class ROOT_ENTRY describes the selected
  governing source with the ACTUAL 018-h ENVELOPE or READ
  provenance (the retained anchor typed fields or the retained
  original read binding, unchanged) and the exact retained root
  bytes (the exact EMPTY root is legal). Compatible bundle rows
  retain canonical authority vectors and cannot become a second
  governing root; a root-bearing opaque region supplies no root
  text.
- EVERY root/file key uses the ACTUAL 018-c canonical recipe with
  the selected root digest and the ACTUAL authority/member/group
  fields. An unchanged nonroot source under a changed governing
  root gets the correct CHANGED governing key. Equal-byte
  source/provenance witness changes, local revisions and
  derivation-only bound changes never invent semantic key
  changes. The FIRST compatible original proof is retained by
  identity plus ALL original compatible witness coordinates, the
  complete reverse member index and the actual bounded admission
  reasons (the accepted G interning/reverse-index/reason law
  unchanged).
- An independent fresh original-C bootstrap at new root bytes is a
  test ORACLE only, never a production implementation; the
  composition never calls public F/G on a forged replacement D
  state.

## 4. Conflict, refusal and the closed result sets

- An authoritative differing-root conflict (or no selected root at
  all) is the fixed `refused_root_conflict` result: NO selected
  source, NO ready graph/admission output, and NEVER a bootstrap
  fallback. Valid equal maxima remain compatible and retain every
  original witness. Unissued source never grants governing
  authority.
- When H selects known authority while exposing the fixed
  `ROOT_SOURCE_UNPROVEN` limitation, the `ok` result retains that
  limitation explicitly in its diagnostics (and completes the
  provenance structurally); structural derivation is never a claim
  of request readiness, filesystem freshness or runtime policy.
  Runtime use/handling of that limitation remains an explicit
  later obligation.
- The closed outcome set is exactly: `ok`,
  `refused_foreign_scope`, `refused_version_conflict`,
  `refused_state_malformed`, `refused_no_root`,
  `refused_over_bound`, `refused_root_conflict`. The closed
  limitation vocabulary is the closed 1:1 union of the accepted
  018-h root-lineage names (55) and the accepted 018-g
  current-admission names (30, which already carry the 018-f graph
  names 1:1; three names are shared) = 82 inherited values, plus
  the NEW composition-level `root_conflict` (83 total). Inherited
  names propagate with their EXACT original value: a crossed
  domain yields its ONE fixed name, never a blanket label; a
  refusal is never relabelled as a root absence or a conflict.
- Every refusal carries the EXACT input state identity and its
  closed reason(s); an `ok` result carries the actual same-run
  selection, the actual selected source provenance and byte
  length, the fresh current graph and the canonical admission.

## 5. Work/resource law

- NEW `CurrentRootCompositionBounds`: `max_total_work_units`
  default AND hard ceiling 1048576, `max_diagnostics` default AND
  hard ceiling 64; stricter positive values are permitted and ANY
  wider direct construction is refused. These are derived
  source/work/diagnostic units over ONE pure operation — never
  tokens, cache occupancy or RSS.
- ONE composition outer per operation charges the ENTIRE operation
  BEFORE attempts: every H namespace/state/selection/
  source-resolution step plus every D/E/F/G scanner/closure/
  key/index/model/source/sort/output step. The actual inherited
  source/entry/count/graph/history/observation/proof/H/G bounds
  keep their original units and domains.
- The accepted G total covers the F+admission subtree EXACTLY as
  in the accepted 018-g law: the new I wrapper / H-fact
  association / scope-namespace / result work belongs to the I
  outer only, OUTSIDE the G/admission stage — the G stage is
  never inflated, reset or renamed by the composition.
- The actual H-selection outer, the D-local, E-local, G-subtree
  total and F-subtree and graph/admission-stage ceilings are all
  enforced INDEPENDENTLY beneath the shared I outer: no global
  minimum, no per-group/per-proof resets, and the original-batch
  `max_requests` domain versus cumulative retention stays
  distinct (a per-proof necessary length preflight may reject a
  single forged proof already wider than any legal original
  snapshot; the cumulative retained members/pieces/source remain
  the actual history domains, and an old valid multi-batch
  history still passes).
- Source character/UTF-8 lengths are preflighted BEFORE any owned
  slicing/encode/hash/copy: the O(1) character count against the
  ACTUAL single-source byte cap first, then the charged no-copy
  byte walk with early exit at the ACTUAL cap. Closed
  actual-field fences run BEFORE any Pydantic serialization
  traversal on every NEW-I constructor/factory/override path
  (warnings-suppressed closed reconstruction; a model_copy-forged
  nested bound refuses before the first serializer visit), and
  the M01 fence (the complete
  L01 fence, M01 closed) runs the nested metadata law at the leaf
  and BOTH parent boundaries in three phases: FIRST the expected
  models, the container kinds and the O(1) lengths under the
  ACTUAL inherited caps and alignment BEFORE any element is
  visited by any iteration, copy, set, sort, hash or
  serialization (the TEN carried admission bound models are
  fenced as closed typed scalar models BEFORE any cap is read
  from them); THEN the bounded scalar / path / index / enum
  validation of every element dimension (every dimension
  pre-bounded by phase one: the member paths under the ACTUAL
  two-inherited path ceiling with the no-copy early-exit byte
  walk, the accepted C dense group ordering, and the UNIQUE
  partition membership -- a set union alone does not prove a
  partition); and ONLY THEN the exact entry / record / proof
  authority, member, width and ownership joins. Every phase
  refuses a forged shape with ONE fixed private error and no raw
  value echo. No hidden Pydantic
  source rewalk and no repeated full-source walk per witness.
- The durable G-matrix evidence covers every new and inherited
  cap at-limit/first-over with target-reaching sentinels, the
  independent phase ceilings beneath a larger whole cost, the
  cumulative/batch scope distinction, the long-workspace
  model/namespace reservations (actual-work bounded in the
  workspace length, never a hidden constant) and the charged
  model/source/compare/copy/sort/index attempts.
- The NEW-I key-record fence (``KEY_RECORD_FENCE_UNITS``, charged
  on the I outer per planned entry and on the root-entry
  reservation) and the L01 closed entry / key-record / ownership
  metadata fence (``ENTRY_METADATA_FENCE_UNITS`` fixed part plus
  the per-member O(n) walk terms: the fixed
  ``ROOT_ENTRY_FENCE_WALK_UNITS`` single-occurrence term for the
  root record (the root occurrence path is the fixed
  ``ROOT_FILENAME`` constant, never a walked member path) and,
  for every planned file entry, the per-dimension coefficients
  against its occurrence's segment member-position counts, the
  ACTUAL member-path byte-cap walk, and the segment / witness /
  group dimensions under the actual inherited caps, bounded by
  the charged O(occurrences) plan walk BEFORE assembly) belong to
  the I outer ONLY: they
  are charged before the entry models exist and never inside the
  G/admission stage, so the G total stays exactly the inherited
  F+admission subtree with no composition fence (J03a). The
  K01/L01 per-entry ACTUAL metadata fence plus canonical
  re-derivation (``canonical_rekey_units``: the closed bound
  fence, the L01 closed metadata fence with its O(n) tuple / set
  / partition walks at the ACTUAL tuple lengths, the retained
  digest/content-key comparisons and the accepted C recipe
  re-derivation with its three bound-model dump passes and five
  sha256 passes, every serialized term bounded at the ACTUAL
  record lengths and the declared field ceilings -- a field
  count is never a serialized length) and the K02 per-row closed
  tuple/scalar/distinct/sorted shape fence (``row_shape_units``)
  are likewise precharged to the I outer ONLY, once per planned
  entry and row BEFORE every construction that performs them
  (both the admission boundary and the result boundary), never
  inside the G/admission stage and never as a wider cap, global
  minimum or reset. The M02 reservation-calculation precharge
  closes the L resource law: the ACTUAL calculation work of
  computing the per-entry canonical re-derivation reservation
  (``canonical_rekey_calc_units``: the closed WALK-FREE bound
  over the probe-string allocations and per-character ceiling
  walks, the reserved workspace encode walk plus byte
  allocation, the per-member-path ceiling walks, the member-
  class value ceiling walks and the per-element iteration /
  append / length work) plus the row-shape sum loop overhead is
  charged on the ONE I outer BEFORE the calculation may encode,
  allocate or walk any element, at BOTH reservation sites (the
  admission boundary and the result boundary); the file-entry
  plan's per-segment planning visit is likewise charged per
  segment BEFORE its bound enters the plan reservation; and the
  M02 JSON ceiling (``_json_metadata_byte_ceiling``) honestly
  bounds the ACTUAL accepted ``json.dumps`` default
  ``ensure_ascii`` recipe per character (ASCII one byte, quote /
  backslash two, control or BMP six, non-BMP twelve, booleans
  five, ``None`` four, ints their digit length) -- the
  canonical recipe and its key bytes are unchanged and no legal
  Unicode is prohibited to fit a formula.
- The 018-n retained-content and reservation closure
  (N01/N02): the retained-content join
  (``_check_entry_retained_content``) runs at the LEAF (the entry
  model validator) and at BOTH parent boundaries over the ACTUAL
  retained original binding: the root entry's ACTUAL bytes are
  preflighted against the ACTUAL inherited single-source cap
  (the O(1) character count, then the no-copy early-exit byte
  walk), the ONE owned encode plus sha256 agrees with the bound
  byte length, the root digest and the retained ENVELOPE / READ
  provenance, and the root's sole PROVEN group joins to the
  retained root digest; the file entry has a nonempty
  admitted-segment tuple, its segment indices distinct and
  increasing, its closed
  byte / char counts sit under the ACTUAL cap BEFORE any owned
  slice, every admitted member position is an ACTUAL integer
  indexed into the retained requested occurrences BEFORE any
  fetch, the admitted members equal the key-record occurrences,
  the region digest equals the aggregate digest, and the
  entry-local group partition joins ONE-TO-ONE to the ORIGINAL
  proof segments (one group per admitted segment: the dense
  member-index range, the PROVEN single-member / BOUNDARYLESS
  multi-member class and the proven member digest / segment
  digest) -- a coherently rekeyed record with a DETACHED
  partition (a changed group digest with the reverse rows
  adjusted) is refused at BOTH parents, at the root and the file
  shapes.  The join's bounded work is charged on the ONE I outer
  BEFORE any encode or hash: at the leaf by the plan's
  per-occurrence AGGREGATE precharge (the accepted G plan admits
  the whole bundle OR one singleton per isolated segment, never
  both; the isolated regions are disjoint, so the source work is
  reserved ONCE per occurrence at the retained source character
  length while the per-entry fixed / traversal / member work is
  reserved at the singleton bound per planned segment, the
  UTF-8 byte work closed at four bytes per code point) and at
  both parents by ``retained_content_join_units`` inside the
  existing reservation charges.  The planner's per-segment
  planning visits are precharged from the VALIDATED segment
  count BEFORE the first segment element is fetched (the M02
  per-segment domain and cost unchanged).  The canonical
  reservation carries no ASCII identity assumption (N02): the
  identity / version / class strings bound at their ACTUAL
  validated character composition under the accepted
  ``ensure_ascii`` recipe, so the closed per-entry reservation
  dominates the ACTUAL measured recipe bytes (two namespace
  builds plus two namespace hashes plus one canonical key build
  and hash) for legal Unicode identities.
- The independent-domain evidence (J03) closes every named domain
  at-limit and first-over at the ACTUAL public-I boundary where
  reachable, and at the named bounded stage/constructor surface
  where the public first-over is structurally unreachable; each
  crossing yields its ONE fixed inherited (or NEW-I) name, never
  a blanket label, with every other budget at its default:

  | domain (actual bound) | entry | at-limit / first-over evidence | fixed name |
  |---|---|---|---|
  | I total work (`max_total_work_units`) | public I | three capped OK runs: the last I charge before each constructor (root-entry fence, first post-entry reservation, result construction) crosses with zero NEW constructions at that stage | `total_work_units_over_bound` |
  | I diagnostics (`max_diagnostics`) | CONSTRUCTOR-ONLY surface, NOT public I (a coherent public derivation never emits over-cap composition diagnostics) | 65 invalid items fenced before item coercion; the at-limit 64 reaches parsing | fixed preflight refusal |
  | G total (inherited admission work) | admission stage inside I | at-limit OK, one-below refused with I headroom intact; the domain-cost observer measures the split at runtime (I outer = G subtree + H domain + strictly positive NEW-I glue) and asserts the G crossing under the exact inherited name | `total_work_units_over_bound` |
  | F subtree (inherited graph work) | F stage | at-limit OK, one-below refused with I headroom intact; the domain-cost observer asserts the F crossing under the exact inherited name (the inherited F regressions remain cited for the unchanged public law, not relabeled) | `total_work_units_over_bound` |
  | H op (inherited H outer) | H phase | unchanged public law: inherited H regressions cited | `work_units_over_bound` |
  | D-local (inherited D-transition work) | public-I first-over STRUCTURALLY UNREACHABLE (the cap is identity-bound into the history key; the transition-final-validation invariant: every accepted D transition revalidates the FINAL state under the same cap) | closed at the actual D-validator stage surface: the lenient larger shared outer is charged, at-limit validates, one-below refuses; the public identity control ISOLATES the bound change (the SAME lineage tag/identity/workspace/config with ONLY the actual HistoryBounds work cap changed, so exactly the bound and its identity-bound keys differ) and refuses foreign scope | `work_units_over_bound` (causal-history name) |
  | E work + diagnostics (inherited `CurrentnessBounds`) | E derivation inside I | each domain at-limit OK / one-below exact name where measurable above the model floor; a sub-floor public first-over is closed at the bounded constructor surface | `currentness_work_units_over_bound` / `currentness_diagnostics_over_bound` |
  | E collections x4 (inherited `CurrentnessBounds`) | E derivation inside I | GENUINELY REACHABLE public first-overs (K03): two distinct nonroot reads cross supported cap1 for paths/groups/witness-memberships and three compatible occurrences for relation-pairs; at-limit OK with every other budget at default, one-below exact name, exact prior state, no partial output; the facade sentinel proves ACTUAL F/E work charged before refusal (more than the zero-work foreign-scope early refusal); the L02 addition derives each domain count INDEPENDENTLY from the retained D metadata (the E charging law re-derived, never a binary search) and a class-identity-preserving ledger sentinel records every collection charge attempt: the at-limit cap equals EXACTLY the derived count (the target charged exactly that many times, no crossing attempt) and one below, the count-th charge is the crossing attempt refused BEFORE the crossing | `paths_over_bound` / `groups_over_bound` / `witness_memberships_over_bound` / `relation_pairs_over_bound` |
  | graph stage (inherited stage reservation) | graph stage inside I | forty-reference root fixture at the measured at-limit (2913 at the recorded pin; the durable control re-measures at runtime), one-below refuses | `graph_work_units_over_bound` |
  | admission stage (inherited stage reservation) | admission stage inside I | repeated-read fixture at the measured at-limit, one-below refuses while the graph stage has headroom | `admission_work_units_exhausted` |
  | single-source char/byte | public I (inherited F law) | at-limit retention / first-over before any owned slice (zero-slice sentinel) | `source_over_bound` |
  | cumulative retention (inherited history domains) | inherited | an old valid multi-batch history still passes; over-retention refuses | history closed names |
  | batch `max_requests` (inherited F domain) | inherited | 2+2 request batches accepted (4 retained), the 3-request batch refuses | `batch_over_bound` |
  | workspace join (admission namespace reconstruction) | public I | work scales with the ACTUAL workspace length; at-limit / first-over | `total_work_units_over_bound` |

  Rows marked "inherited" cite the UNCHANGED public-law regressions
  (the durable F/G/H matrices and the 018-c batch/retention
  controls) for the unchanged inherited behavior; they are not
  relabeled as direct I evidence. The NEW-I rows are exercised by
  the durable J03 controls at the public-I boundary or the named
  stage surface.

## 6. Model association law (constructor-level)

- Object construction is NOT authentication: every
  constructor/factory/`model_copy`/direct-dict path re-derives
  ACTUAL fields before positive use.
- J01/K01: EVERY retained entry -- the root entry and every file
  entry -- binds the SELECTED governing root digest at BOTH its
  actual governing field and its ACTUAL key record's governing
  field, re-checked at the admission boundary AND the result
  boundary (a model_copy-bypassed nested admission cannot escape
  the entry law by construction alone); a genuine EARLIER entry
  for the same nonroot source (old governing digest, old
  canonical key) spliced back into the current admission with
  its reverse-index row remapped is refused at both boundaries
  even though its namespace and retained proof are genuine and
  unchanged. K01 completes the law: at EVERY positive parent
  interpretation the ACTUAL canonical key is RE-DERIVED from
  the ACTUAL nested key record through the accepted C recipe
  (the entry key, the key record's own content key and the
  recomputed key must agree, with the selected governing
  digest), so rebounding BOTH digest fields while retaining the
  old canonical key, or forging either content key, is refused
  at both boundaries -- comparing tags/digests or
  entry==record key alone is never the law. The closed bound
  fence runs BEFORE the recipe may serialize any carried bound
  model; the work is charged bounded METADATA on the I outer
  (no source rewalk per witness). M01 completes the parent
  boundary: BEFORE the recipe may serialize or hash anything,
  the TEN carried admission bound models are fenced as closed
  typed scalar models (no cap is read from a forged bound), and
  the CLOSED entry / key-record / ownership metadata fence
  (phase one: expected models, container kinds and O(1) lengths
  under the ACTUAL inherited caps and alignment; phase two: the
  bounded scalar / path / index / enum walks, the accepted C
  dense group ordering and the UNIQUE partition membership;
  phase three: the closed root/file branch shape) refuses a
  model_copy-forged nested field with ONE fixed private error
  before its elements are visited (the accepted recipe
  dereferences the enum fields directly: an unchecked raw string
  is an uncaught AttributeError, never a validation refusal; an
  unchecked unhashable index is an uncaught TypeError from a set
  build, never a validation refusal);
  the bounded entry / record metadata joins (entry class against
  the record authority class, the entry authority vector against
  the record vector, the entry width against the DISTINCT record
  member paths) then run BEFORE the re-derivation; and the leaf
  entry validator fences the same complete shape, so the parent
  boundaries and the constructor agree.  The entry-level
  scalar/container raw forms are pydantic's ordinary field
  coercion at the flat-dict leaf constructor; their closed fence
  is the parent-boundary law, where a model_copy instance
  reaches the validators un-revalidated.
- J02/K02: the ACTUAL reverse member index equals EXACTLY the
  represented member-path -> ALL-and-ONLY admitted-content-keys
  relation: rows sorted by distinct path, every represented
  member path covered exactly once, no unrepresented path named,
  each row holding exactly the admitted content keys in
  canonical order, the ACTUAL admission scoped key on every row,
  and the root flags equal exactly the root path -- all
  re-derived from the ACTUAL entry key records at both the
  admission boundary and the result boundary. A legitimate SHARED
  member (one path admitted by two distinct proven bundles)
  keeps ONE row with the complete canonical key set. K02
  completes the law: at BOTH parent boundaries the ACTUAL row
  container/count/scalar shape and the STRICT canonical
  sorted/distinct key order are validated BEFORE the set
  comparison (a duplicate or reversed key tuple from a
  model_copy-bypassed row is refused; the set comparison alone
  erases those facts).
- EVERY retained entry's key record re-derives the ACTUAL 018-c
  admission namespace, and that namespace must equal the
  admission's ACTUAL namespace (equal source bytes/provenance from
  another principal/session/workspace never make a foreign key
  record's canonical namespace valid).
- The admission context (the root entry key record's actual
  identity/bound fields, the actual record versions, the bound
  namespace tags, the ACTUAL D lineage ID and the actual bound
  sets) must RE-DERIVE the ACTUAL input history key: a
  coherently rekeyed FOREIGN admission context inside the actual
  H/history/graph is refused; entry-to-detached-tag equality is
  never the association law.
- The carried graph context must bind the ACTUAL carried graph's
  own version/bound/scope fields (a detached tag or hash that
  merely recomputes a coherent scope key never makes a different
  actual context valid).
- The RESULT-level joins bind the exact input state: the
  selection, the graph and the admission bind the EXACT input
  lineage scope/revision/D history key; every selected witness is
  RETAINED by the input state and binds the selected source;
  every retained entry proof is the EXACT original proof object
  retained by the EXACT input D state (identity, not digest
  equality); every witness coordinate re-binds its OWN
  occurrence's original proof coordinates; a READ selected
  provenance re-binds its retained occurrence. A later genuine
  proof/entry/row spliced into an earlier state (where no such
  occurrence exists) is refused even when the admission is
  self-consistent.
- The charged joins run on bounded METADATA (occurrence indexes
  built once, fixed comparison counts per entry/witness); no
  source rewalk.

## 7. Privacy and purity

- No host IO after fixture/import setup on ANY guarded normal or
  negative path (no filesystem, socket or process facility);
  original payloads are byte-unchanged.
- The operational `str`/`repr` of every namespace, state, fact,
  provenance, entry, association, transition and result is free of
  source text, private IDs, markers and identity values (fixed
  placeholders, lengths and digests only); diagnostics are the
  fixed closed enums plus counts; no raw content, prompts,
  credentials or private URLs in any operational output.

## 8. Actual acquisition limitation (documented UNREACHED)

- Four post-refresh NEW-root mixed-bundle controls are UNREACHED
  through the UNMODIFIED public H acquisition: a mixed bundle
  whose root segment carries NEW root bytes (differing from the
  batch root digest and not an actual singleton whole-root
  refresh read) is refused by the old public H/D law
  (`COMPETING_ROOTS` / root-conflict) BEFORE the composition can
  observe it. The I9 selected-digest filter and its durable
  negatives are therefore proven over the reachable stale-root
  (known old bytes) and bootstrap-compatible shapes only; the
  new-root mixed shape is pinned as a whole-018 rework
  implication (the original harness assertion failure and exact
  captures are preserved and are not relabeled). I does NOT
  broaden the old H public refusals to manufacture the positive,
  and no forged state is substituted.
- The new 018-o `observe_root_lineage_mixed` operation (root-
  lineage contract section 5a) supplies root-aware mixed
  acquisition at its NEW operation scope over the SAME retained
  H state and namespace: a proven mixed root member whose member
  digest matches an independently authoritative known version of
  the same effective root — including an independently issued
  complete whole singleton in the SAME batch — acquires ordinary
  source evidence while the mixed read mints no governing
  authority and unresolved foreign digests keep the exact
  COMPETING_ROOTS refusal. The OLD public H acquisition above
  remains UNMODIFIED: the four post-refresh NEW-root
  mixed-bundle controls stay UNREACHED through that unmodified
  public path (the old law is not broadened, no positive is
  manufactured and no forged state is substituted), and ordinary
  I selection/admission behavior is unchanged.

## 9. Private factoring

- Necessary narrow PRIVATE factoring of the accepted kernels is
  authorized and bounded: the H selection is factored through a
  private seam of the unchanged public
  `select_current_root`; the F derivation exposes a private
  `_derive_graph` seam; the G file-entry assembly exposes a
  private seam with the explicit selected-root-digest filter
  (applied only under the I context — every old public caller
  keeps the EXACT old law byte-identically); the canonical 018-c
  recipe is reused unchanged for every I key.
- ALL old public signatures, defaults, schemas, versions and
  refusals are preserved (especially the public F/G
  bootstrap-only laws); there is no weakened observer and no
  unvalidated boolean skip-root switch. Actual repeated work is
  charged; validated same-run internal outputs are reused with
  explicit typed binding, never a caller-asserted snapshot.

## 10. Tests

- `tests/test_current_root_composition.py` (81 test definitions,
  308 cases): the durable ORIGINAL-API matrix over BOTH read
  endpoints and BOTH admission modes — A bootstrap/ENVELOPE
  composition, genuine issued READ refresh, descendant revert,
  rootless continuation and old/known-new/shifted replay no-ops
  with the unknown changed envelope whole refusal; B root edge
  withdrawal with cycle-only loss, independent alternate
  preservation and restoration from the SAME retained originals
  (original proof identity kept); C the I canonical keys versus
  the INDEPENDENT original-C batch oracle (exact root key record,
  file key-record mapping and reverse member index), unchanged
  source under a changed governing root, equal-byte witness
  changes with no false semantic miss; D incompatible/equal
  sibling maxima, child-of-one dominance versus compatible bytes,
  child-of-all resolution, delayed older receipt and a genuine
  late NONROOT ancestor, no partial outputs on conflict and no
  silent bootstrap fallback; E current/staled root reads, proven
  matching root segments, root-bearing boundaryless bundles with
  no promotion, competing root segments refused whole, and the I9
  stale root segment not admitted while the lean nonroot segment
  still admits (greedy no-isolation); F supported native
  initial-EXEC/poll completion, Unicode/CRLF/empty root text with
  proven original spans, and unsupported/unissued evidence with
  typed retained uncertainty and no authority; G every new and
  inherited cap at-limit/first-over with target-reaching
  sentinels, the independent H/G/F phase ceilings beneath a
  larger whole cost, cumulative versus batch scope, the
  long-workspace reservations, and the H-namespace retention cap
  binding the namespace independent of operation overrides; H
  foreign/malformed/coherently-unsupported versions, forged keys
  or provenance, the closed entry bound fences before the first
  serializer dump, the no-host-IO and private-repr controls over
  the exercised success/refusal surfaces, the 1:1 limitation
  mapping, the constructor-only splices (labeled as such), and J
  the 018-j association closure and independent budget domains:
  every entry and its actual key record binding the SELECTED
  governing digest at both boundaries, the historical-governing-
  key splice refused, the entry-vs-key-record governing mismatch
  at the entry law, the exact reverse member relation with the
  shared-member positive and the row-relation mutation refusals,
  the I-only key-record fence, the D-local stage-surface closure
  with the public identity control ISOLATING the bound change
  (K03), the E work/diagnostics domains under I, the graph/
  admission stage domains at the measured at-limit / first-over,
  the domain-cost observer split, and the zero-new-construction
  pre-charge sentinels at the three capped OK runs (extended by
  K01/K02 to assert the canonical-re-derivation and row-shape
  reservations are precharged before the admission and the OK
  result constructions); K the 018-k closure: the stale
  canonical key after both digest rebinds refused at BOTH parents
  (leaf rejection asserted), the key-record content-key mismatch
  variants at both boundaries, the duplicate and reversed
  reverse-row keys refused before the set comparison with the
  shared-member canonical-order positive preserved, and the four
  genuinely reachable E collection caps at-limit/one-below with
  the facade pre-work sentinel over genuinely larger retained
  histories, and L the 018-l closure: the complete closed nested
  entry / key-record / ownership metadata fence at BOTH parent
  boundaries (raw string enums, empty/raw scalars, wrong
  container types, over-cap occurrences, the per-group closed law
  and the exact ownership partition) refusing BEFORE the recipe's
  first element visit (the canonical-helper spy counts exactly
  the one valid root-entry visit), the entry / record authority
  vector and width joins at the leaf and both parents, the
  leaf-constructed fixed refusals for the model_copy-bypassed
  nested record (labeled constructor-only; the entry-level raw
  forms are pydantic's ordinary field coercion at the flat-dict
  constructor), and the four E collection domains bounded by
  INDEPENDENTLY derived actual-domain counts with the
  class-identity-preserving ledger sentinel proving the at-limit
  cap equals exactly the derived count and the one-below
  crossing attempt is the count-th charge refused before the
  crossing), and M the 018-m closure: the M01 before-element
  sentinels (an over-cap entry-class / record-occurrence /
  segment / witness tuple carrying a harmless visit marker
  refuses with ONE fixed private typed error BEFORE any element
  is visited at BOTH parent boundaries, the unhashable and
  mixed-scalar group indices refuse before the set / sort
  operations, and the accepted dense group ordering -- a
  shifted single group and a coherent two-group swap -- refuses
  on the genuinely earned OK whole-bundle composition), the
  closed TEN carried admission bound-model fence (a foreign
  bound class and a forged below-range scalar refuse with the
  closed bound-range error before any cap is read), the M02
  JSON byte ceiling oracle (the per-character bound versus the
  ACTUAL accepted ensure_ascii recipe over ASCII / BMP /
  non-BMP / quote / backslash / control / boolean / None /
  integer / nested values, with the tightness spot checks and
  the long legal Unicode path), the M02 plan-walk identity (the
  measured admission delta equals the independently derived
  node / group / workspace / occurrence / segment counts plus
  the plan fixed and walk terms, and the one-below cap refuses
  with the fixed I name with ZERO entry constructions and the
  ledger stopped exactly at the cap), and the M02
  reservation-calculation precharge (the first canonical rekey
  runs only after the walk-free calculation charge, a cap at
  that charge completes the calculation sum with ZERO rekey
  calls, one below refuses before any calculation or rekey
  call, and the full precharge cap fits exactly with the
  admission-site rekey completing at its own charge before the
  later main-charge crossing); and N the 018-n closure: the
  retained-content join at the leaf and BOTH parents (the
  genuine positive at both parents; the SAME-LENGTH substituted
  root text, the EMPTY admitted region, the out-of-range nested
  member position and — the group-partition join — the
  COHERENTLY REKEYED record with a changed file-group digest or
  a changed ROOT-group digest, each with the canonical recipe
  re-derived and the reverse rows adjusted so ONLY the
  partition join is the bad precondition, refusing at both
  parents with the partition-join message), the byte-aware
  closed reservation (a genuinely non-BMP root and admitted
  regions: the reservation dominates the ACTUAL encoded byte
  work and the full proof-segment traversal, the old
  character-only reservation strictly smaller, the sparse
  one-of-three LEAN region retaining the whole proof identity),
  the LEAF join precharge (the measured admission delta equals
  the independently derived closed plan reservation identity
  with the per-occurrence AGGREGATE join bound — one
  singleton-bound join per planned segment plus the source work
  reserved once — the aggregate dominates the actual leaf joins
  of both isolated entries, the root entry constructed inside
  the root construction before the file assembly, and one unit
  below refusing with ZERO entry constructions and the ledger
  stopped exactly at the cap), the PLAN segment precharge
  (the plan-window charge log holds one contiguous
  units(len(segments)) batch per occurrence immediately after
  the occurrence visit and the final batch equals the
  recomputed closed plan total; the crossing inside the first
  nonempty precharge stops the ledger exactly at the cap with
  no entry construction), the per-site reservation crossing
  (the admission-site crossing with ZERO rekey calls at either
  site and no construction; the RESULT-site crossing with
  exactly the earlier admission rekey calls, ZERO result-site
  rekey calls and no result construction; one below the result
  precharge before even the result calculation call), the zero-
  source multi-member bound control (the per-member terms alone
  dominate the actual element walks with the source allowance at
  zero, tight at the cap) and the actual-identity canonical
  reservation (the ACTUAL recipe-measured namespace and key
  payload bytes for ASCII / BMP / non-BMP / quote-escaped
  identities with the MAX-LENGTH Unicode model identity: the
  closed reservation dominates the two namespace builds plus
  two namespace hashes plus the one canonical key build and
  hash at the measured lengths); constructor and
  reservation-accounting evidence over a valid acquisition, no
  public derivation or runtime claim.
- The ROOT-executed independent probes (public vertical, the
  named I7 namespace/carried-version/joined-context controls, the
  I8 preflight/diagnostic/char-before-copy controls, the I9
  selected-root and preservation controls, the G-wrapper domain
  split, the H-namespace retention cap and the batch-domain
  positive) retain their EXACT recorded source versions and
  scopes: they are ROOT executions, not coding-executed
  repository tests, and are not relabeled as final-source broad
  tests.

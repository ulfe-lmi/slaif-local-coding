# Root-region admission models contract (objective 018, slice s)

`ROOT_REGION_ADMISSION_MODELS_CONTRACT_VERSION =
"cache-root-region-admission-models/v1"`.
`ROOT_REGION_ADMISSION_MODELS_POLICY_VERSION =
"root-region-admission-models-policy/v1"`.
`ROOT_REGION_ADMISSION_PRECHARGE_RECIPE_VERSION =
"root-region-admission-precharge/v1"`.

This contract binds the INERT region-compatible admission-model slice
(`src/slaif_local_coding/constitution/bundles/`:
`root_region_admission_models`, and the public
`RootRegionAdmissionEntry` / `RootRegionAdmission` data models plus the
documented `root_region_admission_model_scope_key` helper and the typed
local before-work validation-reservation helpers). It sits ABOVE the
accepted 018-p state and the 018-r result as COMPONENT DATA: it carries
the ACTUAL retained P state and namespace and the ACTUAL R result by
immutable reference, the exact canonical 018-c key records, the complete
reverse member index and the bounded reason/count/resource metadata, and
it precharges its own closed validation work for the later same-018
consumer. This slice is ACCEPTED at the bounded INERT
MODEL/LOCAL-BOUNDARY scope WITH PROCESS QUALIFICATIONS AND EXPLICIT
HISTORICAL-REPORT CORRECTIONS (strategic decision
`S/reviews/018-s-decision.md`): it is NOT the complete region
consumer. There is no operation result/outcome, no persistent
owner/namespace, no new whole-operation bound set and no public derive
function here; no public API here accepts a caller-positive R/Q/F
snapshot as derivation authority, and retaining the actual R result by
reference is component data, NOT authority. The 018-p producer is
ACCEPTED at its bounded inert producer scope WITH PROCESS
QUALIFICATIONS (strategic decision `S/reviews/018-p-decision.md`); the
018-q query is ACCEPTED at its bounded inert query scope WITH PROCESS
QUALIFICATIONS AND HISTORICAL-REPORT CORRECTIONS (strategic decision
`S/reviews/018-q-decision.md`); the 018-r graph half is ACCEPTED at its
bounded inert selected-root source/current-graph scope WITH PROCESS
QUALIFICATIONS AND EXPLICIT HISTORICAL-REPORT CORRECTIONS (strategic
decision `S/reviews/018-r-decision.md`). It closes nothing end to end:
the separate same-018 complete admission/full-result consumer (which
must derive ACTUAL R from ACTUAL P in its own entire charged operation
and independently earn its own source-scale and whole-operation
evidence), the original whole-018 G/C/S and repair-criteria audit, and
stages 019-024 remain mandatory, and model-only output never waives
them. Like the accepted bounded 018 slices it is pure, bounded and
never active in the adapter runtime: no command string is executed, no
model/native/client/service facility is started, and no
implementation/release/whole-018 status is upgraded by inherited green
checks. All existing C/G/H/O/I/P/Q/R public signatures, defaults,
schemas, version tags, recipe bytes and behavior remain intact,
including the honest old-I refusal of the region-version state; the
narrow typed private helper factoring reuses the ACTUAL existing
predicates and recipes without changing old public law.

## 1. Models and constructor compatibility

- `RootRegionAdmissionEntry` is one region-compatible retained
  admission entry, constructor-compatible with the ACTUAL G
  `_assemble_file_entries` typed generic FILE entry field set
  (`entry_class`, `content_key`, `key_record`, `width`,
  `member_classes`, `root_digest`, `proof`, `admitted_segments`,
  `witnesses`). The ROOT row additionally carries `root_source`: the
  ACTUAL `ResolvedRootRegionSource` record by immutable reference with
  its explicit `envelope` / `read` / `read_region` provenance (the
  closed R provenance classes; a widened old-I retained-root
  provenance is NOT accepted because its closed old-H validators
  reject or misinterpret region provenance). The root body is retained
  by immutable reference ONLY (one root body, no duplicate owned
  root-text copy); the read-only `root_source_kind` /
  `root_body_byte_length` properties reference `root_source` and never
  copy or own root bytes.
- ROOT rows: width 1, one normalized `AGENTS.md` occurrence, ELIGIBLE
  authority, the sole PROVEN group bound to the SELECTED governing root
  digest, the exact EMPTY root legal, and NO fabricated file
  proof/read witnesses (compatible maximal governing witnesses remain
  in the actual R/Q/P selection, not invented as FILE witnesses). FILE
  rows retain the FIRST compatible original `BundleProof` by
  `InstanceOf` reference, their ORIGINAL admitted segment indices and
  ALL distinct original witness coordinates in the canonical
  full-coordinate order; root-only properties are absent on FILE rows.
  Legitimate compatible root-bearing FILE rows may coexist with the
  ONE governing ROOT_ENTRY (a same-bytes proven root-path read is a
  distinct file entry, never a second governing root).
- Object construction is not authentication: the closed leaf law
  (`_s_entry_leaf_closed`) re-derives the ACTUAL canonical 018-c key
  through the accepted C recipe and re-runs the ACTUAL closed R source
  law (including its own bounded content pass), so a copied, detached
  or `model_copy`-bypassed record is refused, not trusted by tag. The
  same law runs at the admission parent (section 4), never as tag
  equality.
- The BEFORE-PARSING entry gate closes, before any raw element is
  parsed by the direct constructor: the PROVIDED key-record class
  (missing or wrong class is its OWN fixed private record error, never
  a silent valid-cap fallback), the closed record preflight (closed
  bound sets, exact original class and hard range) supplying the
  ACTUAL carried member-occurrence cap, the raw `member_classes`
  container class closed to list/tuple (any other iterable is refused
  before Pydantic can traverse unbounded elements), the O(1)
  cap/alignment counts, the UNCONDITIONAL proof-context
  container/count gates (the FILE context under the ACTUAL retained
  proof segment population whose ORIGINAL B population caps close
  FIRST; the legal ROOT context admits no proof segments; a
  wrong/partial provided proof under NO authorized walk), and the
  witness raw container/count gates.
- The closed leaf law runs, in order: the field-existence fence
  (`_S_ENTRY_FIELDS`), the canonical record class, the closed
  entry scalar/enum/container shape (a `model_copy`-bypassed str-enum,
  bool width or mutable list refuses; legitimate direct-constructor
  normalization is distinct and untouched), the shared O(1) record
  preflight plus the member-count alignment, the member-class element
  walk, the proof-context population closure under the ACTUAL carried
  ORIGINAL B (bundle-proof) bound domains (the retained proof's closed
  content containers, the segment population under its original caps,
  the admitted index count under the actual retained segment domain),
  the witness count closed under the ACTUAL carried G
  association-attempt cap (a different domain from the admitted
  segments; a safe structural ceiling, never a new fixed cap), the
  accepted N retained-content law (admitted indices nonempty/distinct/
  increasing, member positions actual, the dense entry-local ONE-TO-ONE
  group partition over ORIGINAL segments with the PROVEN
  single-member / BOUNDARYLESS multi-member digest joins, region digest
  equal to the aggregate digest), and the ACTUAL closed R source law
  for the ROOT row. Unknown individual member hashes stay unknown; the
  whole proof source and the selected admitted region stay distinct.

## 2. The stable model configuration scope key

- `root_region_admission_model_scope_key(p_lineage_key,
  model_contract_version, model_policy_version, r_scope_key,
  g_contract_version, g_policy_version, g_bounds)` is the STABLE model
  configuration scope identity. The closed payload is EXACTLY the
  seven elements `[p_lineage_key, model_contract_version,
  model_policy_version, r_scope_key, g_contract_version,
  g_policy_version, <G-bounds inner dump>]`, where the G-bounds inner
  dump is `json.dumps(g_bounds.model_dump(mode="json"),
  sort_keys=True, separators=(",", ":"))` as a string element; the
  64-hex key is the SHA-256 of the compact sorted `json.dumps` of that
  list.
- The closed O(1) preflight runs BEFORE any serialization walk: the
  two 64-hex key inputs, the four closed version texts (1..128
  nonempty) and the exact ORIGINAL G bounds class and scalars (a shadow
  subclass with redeclared ranges or a partial record refuses at the
  preflight, never inside the dump).
- The key binds the ACTUAL validated P lineage identity (the P
  `lineage_key`, which does NOT contain the carried revision), the
  ACTUAL re-derived R scope key (which itself binds the actual P
  lineage key, the R/Q/F/E contract/policy versions, the actual graph
  version and every effective R/Q/F/E bound), the NEW model
  contract/policy versions, and the ACTUAL G contract/policy versions
  and bounds. The actual P/R context already binds the P/Q/R/E/F and
  original inherited versions/bounds through the R scope; no copied
  scope key is ever hashed as a substitute for the field re-derivation
  at the parent. The carried revision, the selected root digest and
  the actual F/E graph scopes are joined separately at the parent and
  are never part of this stable configuration identity (never
  clocks). An explicitly named derived snapshot identity may bind the
  revision, but is neither this stable configuration identity nor a
  C semantic content key.

## 3. Canonical C identity and selected-source law

- The UNCHANGED accepted C `BundleKeyRecord` / `_key_canonical` /
  `_canonical_entry_key` recipes are reused exactly. Same actual
  semantic namespace/mode, member order/classes, selected governing
  digest and source/configuration produce BYTE-IDENTICAL keys
  regardless of envelope/whole/region forensic provenance, local
  revision or NEW model-derivation bounds; provenance and the NEW
  model versions belong to derived context, not to a new C recipe.
  Root versus FILE authority classes remain distinct; width counts
  DISTINCT normalized admitted paths, not repeated occurrences.
- The actual C admission namespace is RE-DERIVED from the actual
  key-record fields at the leaf and the admission parent (the
  FULL-RESULT third parent is explicitly deferred, not claimed
  here) and bound to the actual P/D/C namespace context (the
  entry-scope join); equal
  copied tags alone prove nothing, and a foreign principal/session/
  workspace/config re-derivation refuses.
- For `root_source` the THREE actual provenance classes are dispatched
  explicitly, binding kind/class, body/digest/byte length, the actual
  selected fact/occurrence/proof and whole-versus-root-member
  metadata: the parent `root_source` is the SAME R resolved source BY
  IDENTITY and belongs to the actual selected compatible-maximal
  originals in the SAME input state (the selected fact and its
  occurrence/proof are original members of the SAME input D state by
  identity; value equality is not an original association proof, and
  a detached value-equal clone refuses). The original
  bootstrap proof/root scope and the selected governing digest stay
  distinct; region offsets are original preceding-segment CHARACTER
  sums, never byte lengths, carrier spans or marker offsets; Unicode,
  CRLF and the exact empty source stay exact.
- The FILE content/partition law retains every N constraint at the
  leaf and the admission parent (section 1, with the FULL-RESULT
  third parent explicitly deferred); the witness's ORIGINAL region
  under its
  owner occurrence's retained proof is joined METADATA-ONLY to the
  SAME aggregate digest (the owner proof is a DIFFERENT retained proof
  where the same member content may sit at different original
  offsets; the ORIGINAL B population caps close O(1) before any index
  or member-element walk; no repeated source-body pass). The M04
  owner/witness joins run at the ACTUAL inherited owner-domain
  ceilings: every witness keeps ITS OWN original coordinates of its
  occurrence's retained proof, and the retained proof's ORIGINAL
  owning occurrence joins its COMPLETE owning result with the exact
  piece-producer association.
- The later actual G planner alone earns admission policy: this slice
  does not invent greedy isolation, off-graph authority, freshness or
  changed-root compatibility from data construction.

## 4. Closed local and admission-parent boundaries

- Enforced at the leaf and the admission parent (the FULL-RESULT
  third parent is explicitly deferred, not claimed): actual field
  EXISTENCE (the closed field tuples), concrete class/closed variant,
  non-bool scalar, UTF-8/hex/version shape, and O(1) per-container
  count gates BEFORE element visits, set/sort/hash/dump/serialization
  or any source copy. Canonical key-record metadata and all FOUR
  carried bound sets close before canonical rekey; groups have valid
  dense ordered unique partitions and authority/width/root joins.
  Unknown/malformed copies/partial actual models refuse with fixed
  private errors, never `AttributeError`/`IndexError` or raw canary
  values; a valid STRICTER bound copy remains legal by value (the
  class fence proves the class and original ranges, not identity to
  the original instance).
- `RootRegionAdmission` carries: the ACTUAL P input state, the ACTUAL
  P namespace (a valid copy is accepted by VALUE: the namespace's own
  recomputed `lineage_key` must equal the state's; the state and
  proof identities promised by this contract are identity, not
  structural equality), the ACTUAL R result by immutable `InstanceOf`
  reference, the ACTUAL unchanged G `CurrentAdmissionBounds`, the
  mandatory root entry, the FILE entries, the complete path
  associations (the actual G row model), the model/G version tags,
  the scope key, and the bounded metadata (`entries_retained`,
  `member_occurrences_charged`, `reverse_association_attempts`,
  `emitted_admission_reasons`, `admission_reasons`). Constructor
  values are NOT authenticated runtime measurements: no model here
  proves actual G attempts/work or a complete same-run consumer.
- The BEFORE-PARSING parent gate closes, before any raw element is
  parsed: the PROVIDED namespace context (actual class, closed fields,
  closed inherited admission bounds), and under the ACTUAL closed
  bounds the O(1) retained-entry count (the mandatory root entry is
  the +1 the accepted G cap counts) and the reverse-association count
  against the actual inherited caps.
- At the admission parent the COMPLETE leaf law is RE-RUN (not tag
  equality) and the closed phase order runs: phase 0 the closed
  class/field-existence fences at the actual constructor field sets
  (the parent itself and its closed fields, the carried state, the
  wrapped D state class and fields, the namespace, the R result and
  its resolved-source field) with the S/G version tags closed at the
  same boundary (the root entry's OWN closed field fence is not
  here; it runs at phase 4); phase 1 the ELEVEN carried bound sets
  at their expected original classes and hard ranges (P namespace `bounds`, `proof_bounds`,
  `graph_bounds`, `observation_bounds`, `history_bounds`,
  `root_lineage_bounds`; R result `bounds`, `q_bounds`, `f_bounds`,
  `e_bounds`; and the actual G `CurrentAdmissionBounds`); phase 1b the
  closed count gates and the admission-reason set/sort/comparison
  walks; phase 2 the complete closed R result law re-run (the
  SAME-run ready derivation over the EXACT input state, the 64-hex
  shape checks, the nested Q/P-selection/F/E evidence re-joins at
  their actual record counts, the F currentness / F graph / E
  currentness scope keys, the full resolved-source law with its
  bounded content pass, the outcome invariants, the exact P state
  identity and the closed revision / root-fact metadata, and the D
  populations under their actual bound domains; the F/E evidence
  joins of source phase 7 run INSIDE this phase-2 R law); phase 3
  the closed D-namespace re-derivation (the carried namespace copy
  re-derived through the actual D validators with equal keys,
  describing the exact input D history and joining the exact state
  lineage identity, the lineage key recomputed from the actual
  namespace fields, and the actual fixed lineage tags) and the P
  lineage-key component; phase 4 the leaf law re-run, opening with
  the root entry's closed field-existence fence BEFORE its first
  dereference (an InstanceOf-carried partial entry is a fixed
  private error, never an AttributeError), with the
  identity-before-content ordering preserved, the root row's
  resolved source the ACTUAL R resolved source BY IDENTITY, the
  selected fact/occurrence/proof original members of the SAME input
  state, and every FILE row's leaf law, scope join and M04
  originality joins; phase 5 the entry-set law (sorted by
  distinct content key, the root key never repeated, every row and
  every row key record bound to the selected governing root
  digest); phase 6 the complete reverse-index law rechecked; phase 8
  the closed counter relationships; phase 9 the stable model scope
  key RECOMPUTED from the actual fields (a stale or forged key
  refuses, never retained).
- The reverse index maps EVERY represented member path (root and FILE
  rows) to ALL AND ONLY the actual admitted content keys: rows sorted
  and deduplicated per path, every row bound to the ACTUAL admission
  scoped key, exact `is_root` boolean matching the root path,
  canonical ordered/deduplicated keys with EXACT equality (not a
  subset); no extra, missing, unowned or nonmember association.
- The closed counter law: `entries_retained` equals the root entry
  plus FILE entries; `emitted_admission_reasons` equals the retained
  reason tuple count under BOTH the actual G and the inherited
  admission diagnostic caps before any enum-error storm; the retained
  entries and member total close under the ACTUAL inherited entry and
  member-occurrence caps; the retained association rows close under
  the ACTUAL inherited reverse-association cap.
- A non-ready or refused R cannot describe a ready admission; a
  source or graph spliced from a later genuine state refuses even
  when the selected root bytes are equal; where original identity is
  promised, identity is used, not `fact in tuple` value membership.
  Intrinsic local checks do not hide uncharged full original-history
  or per-witness full-proof source traversal.

## 5. The NEW local validation reservations
(`root-region-admission-precharge/v1`)

- The reservation law is a SEPARATE component precharge contract: a
  real helper calls the typed bounded CALLER-SUPPLIED meter
  (`reserve(units)`) BEFORE actual calculation/measurement/
  allocation/hash/constructor targets, and the bounded meter raises
  immediately when a charge crosses its remaining budget, so the
  caller's actual targets (the leaf law, the constructor) never run
  after a crossing. The ordinary S constructors remain DATA-validity
  checks and never receive a meter; NO unlimited or default meter
  exists in this module, and no caller-verified flag or snapshot
  exists. The reservation is a WORK meter, never a size limit: the
  inherited source-size caps stay the actual UTF-8 SOURCE SIZE
  domains (section 6). Every real repeated pass is charged unless a
  small closed same-boundary/reference reuse actually removes real
  duplicate work while preserving every predicate; no
  divide-by-constant or amortized-away real pass, no whole-cap fake
  reservation, no per-witness full-source walk. Every payload is
  reserved at a CLOSED ceiling derived from the actual record
  lengths/field counts (a ceiling can only over-charge the actual
  serializer or walk, never under-charge it); documented conservative
  structural ceilings over the actual validated B segment/member
  domains are used where they cover the real target.
- Region component (`_s_region_precharge_closed`): the FILE admitted
  region's owned passes. Order: (1) close the reserver, meter scalars
  and retained container kinds; (2) close the carried B
  segment-domain context (concrete bound record class fence, its
  required field under the original hard range, the O(1)
  retained/admitted population counts against that bound -- a tuple
  length alone is not that cap) BEFORE the metadata reserve or any
  element walk; (3) reserve the ACTUAL closed-stage metadata passes
  (fences, segment element fence, the two admitted-index passes, and
  -- only when the O(1) length check establishes equal lengths -- the
  whole-bundle shape's single closed n-element comparison walk, with
  no snapshot built); (4) run the closed fences and the closed
  admission SHAPE detection (whole bundle, or one proven group;
  partial segments, non-int indices or other shapes are fixed private
  errors); (5) derive the selected interval's ACTUAL character count
  and join it to the declared character metadata BEFORE any
  measurement (a forged declared count cannot authorize the walk);
  (6) reserve the ACTUAL character visits and run the NO-COPY capped
  UTF-8 measurement (a lone surrogate or an interval past the
  retained text is a fixed private error before any owned encode; a
  measured crossing of the actual source cap reuses the inherited
  source-cap refusal and stops the walk early); (7) join the declared
  byte metadata to the measured value; (8) only after measuring,
  reserve the actual owned work: the character reservation is the
  slice pass plus the join pass (`2 * region_chars`) for the
  single-group shape and ZERO for the whole-bundle fast path (the
  partition closure proves the segments tile the source, so the
  joined region IS the source text itself -- no slice/join copies,
  the character total is the O(1) source length, one direct source
  pass), and the byte reservation is the encode output plus one
  SHA-256 input pass plus the fixed 72-byte pad and 32-byte digest
  (`2 * measured + 104`) for both shapes.
- Root-content component (`_s_root_content_precharge_closed`): the
  root branch of the actual closed R source law. It mirrors the
  ACTUAL `_r_source_content_ok` target in its own order: the closed
  O(1) shape gates BEFORE any walk or reservation; the bounded
  64-hex shape walk reserved then run; the ACTUAL no-copy capped
  UTF-8 measurement character visits reserved then run (the declared
  byte length is the actual law's cap, so the walk exits as soon as
  it is exceeded; a lone surrogate fails closed); the declared byte
  metadata joined to the measured length (a forged large OR small
  length cannot authorize a copy); the ACTUAL target's repeated
  passes (the re-run 64-hex shape check and the full no-copy capped
  measurement walk) reserved BEFORE the caller may invoke the target;
  and only after measuring, the owned encode plus SHA-256 work
  reserved: character reservation ZERO (the materialized root body IS
  the retained text; the owned encode's own per-character pass is
  bounded by the reserved byte domain), byte reservation
  `2 * measured + 104`.
- Canonical-metadata component
  (`_s_canonical_metadata_precharge_closed`): the key record's ACTUAL
  canonical metadata work. The shared O(1) preflight SHAPE gate (closed
  fields, closed containers, the FOUR carried bound sets under their
  exact ORIGINAL classes, the member caps and alignment, the
  ownership-groups container/count gate, the workspace closed
  nonempty text and O(1) character shape under the ACTUAL carried
  path cap) closes BEFORE any reservation -- a partial or over-bound
  record refuses with ZERO reserved units and zero serializer work.
  Then the record scalar/enum element CLASSES close O(1); the fence's
  ELEMENT-WALK work is reserved (computed walk-free from the closed
  O(1) counts and the ACTUAL carried domain caps) before the bounded
  workspace walks run; the CEILING CALCULATION itself is reserved
  before it runs; and the ACTUAL rekey work is reserved in the exact
  target order (the namespace payload encode plus SHA-256 at
  `2 * payload + 104`, the scoped input, the namespace constructor's
  integrity re-run of both, its validator walks, and the content-key
  payload). When the ACTUAL parent namespace is supplied (closed O(1)
  first), the SAME five reservations for the scope join's
  re-derivation plus the join comparison pool are reserved.
- Parent-namespace component
  (`_s_parent_namespace_precharge_closed`): phase 3 of the actual
  `_v_admission` carrying law -- the D-namespace RE-DERIVATION and the
  P lineage-key recipe ONLY. It needs namespace METADATA only (no P
  state / source / entry / witness traversal): the closed O(1)
  class/field-existence fences and inherited-cap closure (the five
  identity texts, the config fingerprint, the FIVE 64-hex scope keys,
  the workspace under the ACTUAL graph path bound in its canonical
  form, the lineage id, the SEVEN D version fields, and the SIX bound
  sets at their expected original classes and hard ranges); the
  closure walks each reserved before they run; the precharge's OWN
  ceiling calculations (the dump-meta construction, the ensure_ascii
  JSON encoding ceiling per carried string, the exact compact
  bound-set JSON length, the ceiling dict assembly and the
  16/23-element canonical payload ceilings) each reserved before the
  walk that computes them; the ACTUAL `CausalHistoryNamespace`
  re-derivation through the real D validators at the closed canonical
  ceilings -- including BOTH canonical/2-SHA blocks (the nested 018-c
  admission re-derivation with its domain-prefixed SHA-256 pair, and
  the REPEATED canonical payload with its two recomputed 64-hex keys),
  the validator's canonical workspace re-check, the history-key
  canonical payload (18 strings plus the FIVE bound sets as
  JSON-STRING elements, every embedded key quote escaped) and its
  SHA-256, the state-scoped-key SHA-256, and the recomputed-key and
  state-join equality checks; and the ACTUAL `_lineage_key` recipe at
  its closed canonical ceiling plus its equality check and the fixed
  lineage-tag comparisons at their actual target position.
- Admission parent (`_s_parent_precharge_closed`): the complete
  `_v_admission` carrying law. The OPENING gates run before the first
  target-cost reservation: the closed O(1) class gates, the
  field-existence fences at the actual constructor field sets, the
  ELEVEN carried bound sets at their original classes and hard
  ranges, the closed container kinds, the O(1) count gates with the
  INHERITED collection caps enforced at their actual carried bound
  sets (the ROOT + FILE entry population against the actual inherited
  admission entry cap, the association rows against the actual
  inherited reverse-association cap), and the helper's own
  occurrence/entry counting walks -- each walk reserved at its closed
  per-element ceiling BEFORE it runs, with the per-element class/
  field/container fences charged as work and every counted retained
  length (each proof pieces tuple, each key-record member-occurrences
  tuple, the cumulative member total) closed under its ACTUAL
  inherited or carried domain before it feeds any reservation. The
  reservation then mirrors the ACTUAL `_v_admission` phase order and
  reserves every real pass BEFORE the target may run (phase 0/1 the
  closed class/field fences and the ELEVEN bound sets; phase 1b the
  closed count gates and the admission-reason set/sort/comparison
  walks; phase 2 the 64-hex shape checks, the identity-text UTF-8
  walks, the workspace/lineage-id walks, the version joins, the
  nested Q/P-selection/F/E evidence re-joins, the F currentness / F
  graph / E currentness scope keys at their ACTUAL JSON-array recipes
  (brackets, separators, quote pairs and ensure_ascii escaped bodies;
  the embedded bound-set JSON strings with their escaped key quotes;
  the precharge's own ceiling calculations reserved before their
  walks), and the complete closed R result law; phase 3 via the
  parent-namespace component; phases 4/5/6/8 the leaf law re-run and
  the entry-set/reverse-index/counter walks, where the ROOT row's
  leaf re-run reuses the ACTUAL component contracts (the resolved-
  source identity fence, the canonical-metadata component and the
  root-content component) and each FILE row the same canonical
  component, its closed B-domain population caps before the helper's
  own charged metadata walks, the region component at the entry's own
  carried B domain and the M04 owner/witness joins at the ACTUAL
  inherited owner-domain ceilings; phase 9 the S model scope key
  re-derivation at its closed canonical ceiling).

## 6. Work versus source-size domains

- The inherited single-source and root-source BYTE ceilings govern
  the ACTUAL UTF-8 length of the retained source ONLY: a legal at-
  cap source stays legal, and a measured crossing reuses the
  inherited source-cap refusal. The NEW reservations are WORK
  meters: they never reinterpret a source-size cap as a work bound,
  never borrow work budget from `max_single_source_bytes`, and never
  add a new whole-operation total, cap or setting.
- Forged declared lengths cannot authorize a copy: the declared
  character/byte metadata joins to the ACTUAL measured values before
  any owned encode/hash; surrogate/malformed text is a fixed private
  error, never an encoder exception.

## 7. Deferred full-operation limits and source-scale evidence

- This slice sets NO whole-operation bound set, exposes NO public
  derive function and wires NO runtime. The later same-018 complete
  consumer supplies its REAL cumulative budget callback and domain
  coupling in its own ordered round, derives ACTUAL R from ACTUAL P
  in the same entire charged operation, fences the FULL-RESULT third
  parent, and independently earns its own 32768-byte whole-operation
  readiness, both-parent/full-result joins and independent-domain
  evidence; the component precharges here are contracts for that
  recipe, not a substitute for it.
- The permanent suite records actual model-component source/cost
  outcomes honestly (`e-record` lines in the protected test output):
  under the ORIGINAL default `GraphBounds` (`max_work_units` 65536)
  the root-only 32768/65536-byte shapes carry their component data
  with measured labeled costs (root-content, canonical-metadata,
  file-region, parent) in BOTH admission modes; the mixed-region/
  no-singleton and the multi-dependency/history shapes' ACTUAL G
  assembly REFUSES the default 65536 stage limit with the fixed
  `admission_work_units_exhausted` component outcome (honest refusal,
  not a manufactured positive); the positive component DATA for
  those shapes is recorded under the genuine namespace with the
  EXISTING LEGAL 1048576 stage setting (inside the unchanged original
  hard range, no cap raise); 131072-byte sources yield an honest
  ACTUAL R-total refusal with no usable resolved source and no
  positive model component there. None of this is default whole-
  consumer readiness or a zero-allocation claim.

## 8. Privacy and purity

- The permanent F controls test the operational `str`/`repr` of
  the NEW S public surfaces (the admission parent, the root entry,
  every FILE entry and every path-association row) and the fixed
  private constructor error: on a genuine fixture that actually
  carries the canaries (region root body, bootstrap root body,
  nonroot member body, call ID, principal/session/repository/route,
  model identity, lineage), none of those values appears in any
  tested rendering. The carried records themselves keep the fixed
  non-echoing repr laws of their own contracts (the C key-record,
  the P/D/R records), which the S surfaces render by composition.
  The fixed private errors carry NO canary content.
- No host IO after fixture/import setup on ANY public model or
  helper path: the closed 24-facility filesystem/socket/process trap
  covers the entry constructor, the admission parent, the scope-key
  helper, every precharge component and the refusal paths, and the
  original request payloads' canonical serialization is unchanged
  afterwards (pure data evidence, not a wire-byte proof).
- Deterministic construction/canonical payload DATA preservation: a
  fresh construction from the same actual fields is byte-identical in
  its canonical payload and stable in its scope key, with the exact
  original references retained (identity, not structural equality).

## 9. Boundaries and remaining scope

- The API is MODEL/LOCAL-BOUNDARY ONLY and INERT: it is never active
  in adapter execution, earns no admission, no compiled cache, no
  runtime or HTTP readiness, and no v1 profile behavior. Model
  construction is not cache admission, compilation, wire delivery or
  authenticated runtime isolation.
- It is ACCEPTED at its bounded model/local-boundary scope
  (strategic decision `S/reviews/018-s-decision.md`, preserving
  every recorded qualification and correction); that acceptance
  does not accept whole 018, the later admission/full-result
  consumer (the 018-t complete consumer, `docs/CACHE-ROOT-REGION-
  ADMISSION-CONTRACT.md`), or 019-024, all of which remain
  mandatory. The I/J/K/L/M NOT ACCEPTED history and every
  unique accepted law/qualification are preserved, including the
  honest old-I refusal of the region-version state and the old I/N
  reservations unchanged.
- All existing C/G/H/O/P/Q/R public schemas, defaults, versions,
  recipes and supported boundaries are unchanged; the new module
  reuses their ACTUAL predicates and recipes through typed private
  factoring only.

## 10. Tests

- `tests/test_root_region_admission_models.py` (112 tests): the
  durable ORIGINAL-API matrix -- A the genuine public P bootstrap to
  actual R to NEW model constructor positives (BOTH modes and BOTH
  read endpoints where applicable; envelope, whole and region;
  Unicode NONROOT prefix, CRLF/empty root; original multi-piece
  producer/owner/frontier/proof identity; unchanged canonical C
  factories and actual G generic FILE assembly), B the C identity law
  (identical ROOT_ENTRY keys across provenance/revision/derivation
  bounds; ROOT_ENTRY versus compatible root-bearing FILE rows; member
  ordering; repeated operands/distinct width; lean/proven isolation
  and greedy background; wrong reverse-index edges, extra/missing/
  unowned keys, wrong root flags and foreign scoped rows refused), C
  the positive-first negative-only copy/construct mutations (partial
  actual source/state/ns/R/C key records, variants/versions, all
  ELEVEN bound sets and canonical four, booleans/wider/missing
  fields, stale/coherently rekeyed unsupported tags, foreign
  principal/session/workspace/config, source/member/whole digest/
  length/coordinates, concrete provenance kind/class, original
  owner/piece producer/witness membership, detached same-value
  extras, actual later proof or SAME-root stale graph splices;
  non-ready Q/R evidence is not a ready parent; the FULL-RESULT
  third parent explicitly deferred, not claimed), D the before-
  target resource controls with real positive class/serializer/
  source-walk/owned-encode/hash instrumentation (closed count/
  scalar gates before traversal; the two-phase content reservation
  and the metadata/cost-calculation closure at leaf and admission
  parent; exact/one-below of the component model-precharge meter
  refusing BEFORE the actual crossing target with complete source/
  context shapes preserved; truthful constructor-only controls where
  the public domain is structurally unreachable -- never a new
  public operation's whole-domain proof or zero-allocation at
  full-minimum-minus-one), E the independently recorded actual
  model-component source/cost outcomes per section 7 (labeled
  component costs and counters in protected test output; honest
  default-stage refusals; no full-consumer fit claim), F the
  deterministic construction/canonical payload DATA preservation,
  exact original reference retention, the private ROOT/NONROOT/
  marker/ID/model/identity canaries in str/repr/errors, and the
  closed 24-facility IO traps after fixtures/imports on all new
  public model/helper paths. The existing C/G/I/H/O/P/Q/R suites and
  old schemas/recipes/positive/refusal laws are unchanged.

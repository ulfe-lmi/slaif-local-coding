# Root-region authority producer contract (objective 018, slice p)

`ROOT_REGION_LINEAGE_CONTRACT_VERSION = "cache-root-region-lineage/v1"`.
`ROOT_REGION_LINEAGE_POLICY_VERSION = "root-region-lineage-policy/v1"`.

This contract binds the INERT versioned root-region
producer/validator/authority/selection slice
(`src/slaif_local_coding/constitution/bundles/`:
`root_region_lineage_models`, `root_region_lineage`, and the public
entries `bootstrap_root_region_lineage` /
`observe_root_region_lineage` / `register_root_region_issuance` /
`register_root_region_receipt` / `select_current_root_region` /
`validate_root_region_lineage_state`, plus the namespace factory
`make_root_region_lineage_namespace`). It is the PRODUCER half of
the ordinary mixed-only changed-root acquisition required by the
approved 018 rules 3/8: a genuinely issued, complete, uniquely
attributable NEW root region inside an ordinary mixed read acquires
source evidence AND authority with NO independent singleton. It
closes nothing end to end: the next same-018 CONSUMER round must
consume the SAME legitimate new state into the actual
graph/admission; neither round alone completes whole 018 (the
same-018 018-q slice derives the pure root-currentness QUERY over
this producer's state — contract
`docs/CACHE-ROOT-REGION-CURRENTNESS-CONTRACT.md` — PENDING
strategic review at its bounded inert scope). This slice is
ACCEPTED at its bounded inert producer scope WITH PROCESS
QUALIFICATIONS (strategic decision
`S/reviews/018-p-decision.md`, preserving every recorded
qualification): like the accepted 017 slice and the accepted
bounded 018 slices (018-a..h, 018-n, 018-o, each at its bounded
scope with the recorded process qualifications; the
018-i/j/k/l/m repair chain stays NOT ACCEPTED as recorded in the
stage ledger) it is pure, bounded and never active in the adapter
runtime; no command string is executed and no model/native/
client/service facility is started.
All existing B/C/D/E/F/G/H/O/I public signatures, defaults,
schemas, version tags, recipe bytes and behavior remain intact; the
existing old I honestly refuses a region-version state (section 9).
No adapter/runtime/compiler/recovery wiring, and no new I
graph/admission readiness claim, is made in this producer round.

## 1. Namespace, scope keys and caller trust

- `RootRegionLineageNamespace` derives from the ACTUAL accepted
  018-d CAUSAL-HISTORY scope, bound through the ACTUAL accepted C
  admission namespace (its actual fields AND both 64-hex keys
  recomputed by the actual D factory), plus the NEW
  contract/policy tags, the region `lineage_id` and the ACTUAL
  unchanged `RootLineageBounds` (section 7). It is an explicit
  NEW-version record, not a silently widened old H schema; no old
  H namespace tag is reinterpreted. The `lineage_key` is EXACTLY
  `_lineage_key(history_key, contract_version, policy_version,
  root_lineage_bounds)` (the accepted version-agnostic key recipe
  over the actual D history key): it is STABLE across state
  revisions and does NOT bind the state revision — the state's
  key match is the scope fence, and revision support is the
  separate CAS fence.
- `make_root_region_lineage_namespace(admission, lineage_id,
  bounds=None, history_bounds=None)` revalidates the ACTUAL
  admitted fields under closed actual-field fences BEFORE any
  serialization traversal (a MALFORMED model_copy-mutated or
  dumped-dict bound refuses before the first serializer visit).
  Direct
  construction runs the same closed actual-field bindings; a
  MALFORMED (model_copy-mutated) bound or a wider-than-default
  bound refuses with a fixed private error, while valid stricter
  copies are legal.
- The identity/model fields are canonically hashed into the scope
  key: the operational `str`/`repr` never carries raw identity
  values (section 8). The scope key is RECOMPUTED from the ACTUAL
  fields on every construction (the exact input D history key,
  itself recomputed from every actual D scope field, the actual
  D scope, every inherited version field, the bound sets and the
  contract/policy tags); a stale or forged key is refused, never
  retained.
- The input D state is the INTERNAL retained-history boundary,
  never a public supplied proof/snapshot/header authority: object
  construction is not authentication, and no caller-supplied
  selection/current flag establishes authority.

## 2. Bootstrap law

- `bootstrap_root_region_lineage(requests, ns)` runs the ACTUAL
  accepted D bootstrap (the legitimate effective Responses AGENTS
  envelope with exact source bytes, workspace and first original
  spans; the exact EMPTY root is legal; a rootless batch refuses)
  under the STRICT old root law: no relaxed envelope law and no
  refresh acquisition at bootstrap (a competing root operand
  refuses atomically).
- The accepted bootstrap state carries EXACTLY ONE actual
  immutable anchor fact (the `envelope` provenance; never issued,
  always authoritative), the region revision 1 in exact 1:1 with
  the wrapped D revision, and the ACTUAL D state by immutable
  `InstanceOf` reference (nested revalidation never reruns; dict
  input is refused).
- Every accepted bootstrap must satisfy its OWN exact
  eligible-source inventory: eligible unproven read/region
  candidates present in the bootstrap batch are retained under the
  normal caps/flags (with `ROOT_SOURCE_UNPROVEN`) alongside the
  ONE anchor — a complete root read co-present at bootstrap earns
  its retained fact, and a refused retention keeps the EXACT prior
  (absent) state with no partial publication.
- State atomicity and revision: the region revision stays in
  exact 1:1 with the wrapped actual D revision; an accepted
  transition publishes EXACTLY ONE new state (revision +1), and a
  replay or refusal preserves the EXACT prior state by identity
  with no partial root-fact publication. An actual ACCEPTED D
  candidate discarded by a refused region result is carried only
  as explicitly discarded transition evidence: the transition's
  `d_revision_before`/`d_revision_after` equal the ACTUAL
  `d_transition` revision fields even while the region revision
  is unchanged (the region `revision_before`/`revision_after`
  stay at the exact prior region revision), and
  `new_root_facts` is empty on every non-acceptance. The selection query never advances any
  revision.

## 3. Region-acquisition policy (observation)

- `observe_root_region_lineage(state, ns, expected_revision,
  requests)` runs the fixed O(1) gates FIRST and in the ACTUAL
  order — (1) the lineage-key scope fence (a different lineage_id
  or a different D workspace scope is `refused_foreign_scope`
  with no diagnostics), (2) the CAS/revision fence
  (`refused_cas_mismatch`), (3) the D-history binding fence
  (`refused_foreign_scope`), (4) the actual version-pair fence
  (a coherent unsupported version refuses
  `refused_version_conflict` / `VERSION_UNSUPPORTED`) — then the
  charged full namespace revalidation (a model_copy-mutated or
  forged key pair refuses `refused_foreign_scope`) and the
  charged cross-record state integrity; ALL before any positive
  compatibility work, on BOTH read endpoints and BOTH admission
  modes. Version support follows scope: a stale-key version case
  (a self-INCONSISTENT v2 namespace whose stale v1-recomputed key
  still matches the genuine state's key) PASSES the scope fence
  and is caught by the version fence; a self-CONSISTENT rekeyed
  unsupported namespace over the old state FAILS the scope fence
  first (no version diagnostics); a fully coherent rekeyed
  namespace AND state still fail the version fence (scope
  identity alone is not version support). All three refuse on
  ALL FOUR public operations with the exact prior state and
  `d_transition is None`.
- The actual original-request D observation then runs under a
  PRIVATE region-acquisition policy: a foreign root MEMBER is
  provisionally source-compatible ONLY if the ACTUAL complete
  proof has EXACTLY ONE normalized effective-root occurrence
  across ALL requested operands (the occurrence count is charged
  BEFORE the exception is granted; a second root-path operand,
  proven or hidden inside an opaque multi-member segment, earns
  no exception) AND a single proven complete whole region for it
  (the root segment is attributable, its member digest proven).
- The unknown mixed root source does NOT need an independent
  singleton in this NEW contract (the old H deferred-mixed law is
  deliberately not carried over). Repeated roots, opaque root
  groups, partial/truncated/nonzero/unpaired/unsupported reads
  gain NO NEW exception or authority; their exact old
  acquisition/limitation semantics and source retention remain
  unchanged (no read grammar is expanded).

## 4. Authority law

- After EVERY accepted D transition the issued/authority flags are
  RE-DERIVED over ALL new-version retained facts (the S1 law,
  unchanged in substance): a read/region fact is `issued` when
  its matching trusted INTERNAL issuance is retained and
  `authority` only when it is issued AND anchored AND its frozen
  parent evidence reaches the ORIGINAL bootstrap root fact. The
  envelope anchor is never issued and always authoritative. Flags
  are derived state, never caller-supplied authority; stored
  flags are never trusted.
- Authority requires the ACTUAL trusted INTERNAL issuance, the
  complete original owning result, the anchored original
  occurrence and the frozen ancestry reaching the immutable
  bootstrap. Body flags, caller digests, envelope text, ID
  novelty, equality, arrival order and revisions never establish
  authority or currentness.
- An unissued complete root region retains the fixed
  `ROOT_SOURCE_UNPROVEN` limitation and NO governing authority; a
  genuine later issuance/receipt earns authority on the SAME
  retained state without re-reading the source.
- A changed envelope in the SAME batch may match an INDEPENDENTLY
  earned authoritative root REGION (the deterministic refusal
  precedence is preserved), but an envelope alone cannot authorize
  itself (`refused_root_authority` atomically).
- Partial-order currentness is FROZEN evidence, not a clock: a
  genuinely NEW authoritative region occurrence containing old v1
  bytes AFTER v2 is a DELIBERATE REVERT and selects the old bytes
  (the same frozen partial-order law as a singleton); an old
  replay or a delayed ancestor never rolls back. 018-o's
  source-only mixed-fact suppression is NOT carried into this
  authority contract. Incomparable differing regions conflict
  with NO selection; a genuine region descendant of ALL resolves;
  a child of one branch cannot dominate the other.

## 5. Retention, provenance and binding law

- `RootRegionReadProvenance` (the NEW discriminated kind
  `read_region`) retains: the actual original occurrence/call
  identity and endpoint; the WHOLE original proof digest and byte
  length (the proof AGGREGATE binding, retained verbatim from the
  original proof — never a re-hash); the root segment index into
  the proof's ordered segments and the unique member position of
  the single attributable effective-root member in that segment;
  and the ROOT MEMBER digest and byte length (the actual root
  body). The whole-proof binding and the root-body binding are
  DISTINCT; a zero-length root region is legal when genuinely
  proven.
- The provenance union is the supported original
  `envelope`/`read` shapes plus the explicit `read_region` kind,
  discriminated on `kind` (no envelope fallthrough for the new
  kind). A singleton whole read retains its old whole-read
  provenance (aggregate binding, unchanged old law); only a mixed
  region read uses the new provenance.
- `RootRegionLineageFact.source_digest`/`source_byte_length` are
  the ROOT BODY: the anchor source for an envelope fact, the
  original whole-read aggregate for a read fact, and the ACTUAL
  root member digest/length for a read_region fact. The mixed
  aggregate bytes remain D/B-owned and never become the logical
  root-body size.
- Every eligible source candidate is retained as a root fact;
  fact COUNT and actual root-member BYTES are prefetched BEFORE
  any provenance/fact materialization under the unchanged H
  ceilings (a first-over crossing candidate allocates NEITHER the
  provenance NOR the fact); original proof objects, bootstrap,
  spans, IDs, owner/result association and frozen ancestry are
  preserved, never replaced or re-faked.
- Versioned validation (`validate_root_region_lineage_state`)
  rederives the EXACT eligible inventory, the actual provenance
  joins (occurrence/proof/segment/member, the root group's proven
  digest joined to the retained root digest, the whole-proof and
  root-member bindings), all source/count/scalar shape/byte
  preflights, the actual retained original proof/owner
  association and the actual flags: the proof/owner/inventory
  joins are enforced by the charged validator and the public
  operations, so a coherently rekeyed mutation with a changed
  group digest or merged groups refuses there. The constructors
  enforce intrinsic shape law only — no authentication, and no
  uncharged proof walk is added to a constructor.

## 6. Selection law

- `select_current_root_region(state, ns, bounds=None)` is the
  bounded pure current-root selection query on the NEW contract:
  the O(1) shape preflight, the fixed early scope/D-state-binding/
  version fences, the charged full revalidation and the charged
  cross-record state validation run BEFORE any positive
  interpretation; a malformed state or unsupported version
  refuses `refused` (a fixed typed QUERY failure, never
  relabelled as a root absence).
- `ok` carries the ONE equal maximal root source with ALL its
  compatible maximal originals retained — the ACTUAL retained
  fact objects of that SAME state as witnesses (any supported
  provenance kind); equal-byte witnesses stay genuinely
  incomparable and grow without a false semantic miss; a
  differing authoritative conflict selects NO source
  (`root_content_conflict`); the honest absence of any
  authoritative root fact is `no_selected_root`.

## 7. Bounds and the ONE-outer work law

- The ACTUAL unchanged `RootLineageBounds` apply: 1024 retained
  root facts, 16777216 logical root-source bytes, 1048576 total
  work units per operation and 64 diagnostics; stricter positive
  values are permitted and any wider direct construction is
  refused. These are derived source/work/diagnostic units — never
  tokens, cache occupancy or RSS.
- ONE new-operation outer at that ACTUAL work ceiling covers the
  ENTIRE operation and couples the ACTUAL D work (the D
  observation/retention stages run on the SAME ledger with their
  original units); the D/B-local inherited domains (history
  work, graph batch requests, diagnostics, proof/observation
  bounds) remain INDEPENDENT beneath it — no second full H
  operation under a reset budget, no invented whole-H budget
  layer, no global minimum or per-group/per-proof reset.
- Unique-root operand counting, ALL candidate attempts before
  dedup, pending metadata/allocation, inventory/fact
  construction, snapshots, sorting/unions, membership and
  ancestry are charged BEFORE the work; source bytes/characters
  are prefetched BEFORE any copy/encoding/hashing. The same-run
  validated original proof/metadata is reused: no extra
  full-source traversal per fact/witness to locate its root
  region. The original-batch `max_requests` domain and the
  cumulative retention domains stay distinct.

## 8. Privacy and purity

- The operational `str`/`repr` of every namespace, state, fact,
  provenance, occurrence, result record, transition and
  selection result is free of source text, raw identity values,
  markers and private IDs (fixed placeholders, lengths and
  digests only); diagnostics are the fixed closed enums plus
  counts; malformed-input errors are FIXED private messages that
  never echo the offending value.
- No host IO after fixture/import setup (no filesystem, socket or
  process facility — the closed 24-facility surface) on ANY
  guarded public path: the namespace factory, bootstrap,
  issuance, observation, validation, selection, receipt, replay
  and every fixed refusal on BOTH read endpoints and BOTH
  admission modes; the original request payloads' canonical
  serialization is unchanged afterwards (pure data evidence, not
  a wire-byte proof).

## 9. Old-surface boundary

- The existing old I (current-root composition,
  `docs/CACHE-CURRENT-ROOT-COMPOSITION-CONTRACT.md` section 1)
  CANNOT hold a region state in its old `InstanceOf` result
  schema without broadening the old positive law, so its public
  entry raises a FIXED private `ValueError` at the first
  state-shape gate BEFORE any old positive work or result
  construction — the documented narrow explicit rejection
  boundary, tested typed fail-closed. All old positive behavior,
  types, schemas, versions and recipes remain intact; no old
  state is fabricated to fit a refusal, and no new I
  graph/admission readiness for the region state is claimed in
  this producer round.

## 10. Tests

- `tests/test_root_region_lineage.py` (223 cases): the durable
  ORIGINAL-API matrix over BOTH read endpoints and BOTH
  admission modes — A bootstrap (issued descendant mixed-only
  read with NO independent singleton, root first/middle/last,
  Unicode/CRLF and genuine empty root, same-byte bootstrap
  singleton inventory); B the frozen partial order (equal-byte
  singleton/region witnesses, genuine v1-after-v2 deliberate
  revert, known historical retention, delayed receipts, replay,
  per-pair identity on FINAL-state facts); C issuance/
  authority/receipt, incomparable/child-of-one conflicts,
  descendant-of-all resolution and the envelope-alone
  atomic-refusal precedence; D the no-exception read shapes
  (repeated roots incl. hidden opaque, missing marker, truly
  unsupported grammar, pending/truncated/nonzero/unpaired
  retention with exact old semantics); E the resulting states'
  subsequent operations, original anchor/occurrence/proof
  identity by reference and the honest old-I refusal; F the ONE
  new-operation outer (sequence work cap, bootstrap work cap with
  the MEASURED constructor-entry boundary, fact-count cap across
  BOTH read provenance kinds, logical root bytes with a mixed
  aggregate strictly larger than the cap, the independent
  inherited D/B domains and the diagnostics ceiling) with
  real-class `__init__` counters that preserve class identity;
  G the direct-validator forge matrix (kind tag, stored flags,
  detached occurrence, coherent rekey, segment index, inventory
  gap, phantom fact, unsorted facts, revision mismatch, lineage
  key, fact/source-byte over-bound); H the selection-constructor
  invariants; I the scope/workspace/path and coherent
  unsupported-version namespace/state gates on ALL FOUR
  operations; J the public-operation forge matrix (whole-proof
  digest/length, root-member length/digest, original-proof
  identity, the D-level owning-result omission and producer
  rekey with the old D validator staying None) on BOTH endpoints
  and modes; K the fixed non-echoing privacy law with
  NONROOT-body, ROOT-source and ID-field canaries; L the closed
  host-IO purity surface over the ENTIRE public path with the
  operational-representation canaries.

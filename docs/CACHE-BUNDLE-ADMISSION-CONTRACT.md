# Bundle-admission and structural-identity contract (objective 018, slice c)

`ADMISSION_CONTRACT_VERSION = "cache-bundle-admission/v1"`.

This contract binds the INERT bundle-admission and structural-identity
slice (`src/slaif_local_coding/constitution/bundles/`:
`bundle_admission_models`, `bundle_admission`, and the public entries
`observe_bundle_admission` / `observe_bundle_admission_batch` /
`make_bundle_admission_namespace`). It composes, over a bounded
ORIGINAL GraphRequest batch, the accepted 017 observation (re-derived
under the namespace's ACTUAL effective `ObservationBounds`), the
single evidenced root/workspace binding (the 018-a law, including the
competing-root-path-read refusal), the accepted 018-b bundle-proof pass
(the same shared source ledger) and the NEW bounded AND/OR
raw-reference closure into ONE bounded lean/greedy admission snapshot.
This slice itself is IMPLEMENTED and ACCEPTED at its bounded inert
admission/structural-identity scope WITH process qualifications
(strategic decision `S/reviews/018-c-decision.md`); like 018-a and
018-b (both ACCEPTED at their bounded inert scopes with process
qualifications) it is delivered as inert code on PR 26, which stays
unmerged until the whole numeric 018 is complete. It is pure,
bounded and never active in the adapter runtime; no
command string is executed and no model/native/client/service
facility is started. It earns G03-G05, the structural (not runtime)
C01/C02/C06
slices and the continuing G01/G02/S01 foundation scope on top of the
accepted 018-a (graph foundation) and 018-b (bundle-proof bridge)
slices. Compilation, RAM retention, overlap/replay invalidation,
source replacement and recovery remain later mandatory stages: the
same-018 chronology stages (C04/C05/version/edge-withdrawal and the
remaining G/C/S criteria), then 019 (RAM session ownership, capacity/
backpressure, single-flight, lifecycle), 020 (protected exact-original
recovery checkpoints and lazy restart rebuilding), 021 (pinned
tokenizer and typed bundle compiler: C/32 slots, aggregate/reserves,
compile-once), 022 (transactional source replacement and endpoint
integration), 023 (full-stack adversarial/lifecycle/isolation/
cancellation matrix) and 024 (bounded actual-model/genuine-Codex
qualification); nothing here is a v1 runtime, compiler-hit or recovery
claim. C01 here proves STRUCTURAL entry interning only; later
021/023 actual compile-once/hit qualification stays mandatory.

## 1. Namespace caller trust (R1/R2, 018-a pattern)

- `make_bundle_admission_namespace(identity, *, model_identity,
  config_fingerprint, workspace, mode=LEAN, bounds=None,
  proof_bounds=None, graph_bounds=None, observation_bounds=None)`
  takes an already-verified `RequestIdentity` from the existing
  trusted ingress or a validated standalone configuration. Object
  construction is not itself authentication; the factory validates
  shapes only with fixed messages that never echo the offending value.
- The ACTUAL effective scope is all bound into the two 64-hex keys:
  identity (principal/session/repository/route), model identity,
  opaque configuration fingerprint, the explicit MODE, the FIVE
  version identities (`cache-bundle-admission/v1`,
  `cache-bundle-observation/3`, `cache-graph/v1`,
  `reference-grammar/v1` — the ACTUAL accepted reference-scan grammar
  the closure consumes — and `cache-bundle-proof/v1`) and ALL FOUR
  effective bound sets (the NEW `BundleAdmissionBounds`, the accepted
  `BundleProofBounds`, the ACTUAL effective `GraphBounds` and the
  ACTUAL effective `ObservationBounds`). A bare caller tag cannot hide
  a different mode or effective configuration.
- Direct model construction recomputes BOTH keys from the actual
  fields and refuses (`ValueError`, fixed message) any forged, stale
  or borrowed key; the workspace is additionally enforced against the
  ACTUAL configured `GraphBounds.max_path_bytes` byte length.
  `namespace_key` binds everything above; `scoped_key` additionally
  binds the evidenced workspace (the root scope). Errors and
  operational reprs never expose identity values, source, markers or
  private IDs (fixed `<private-id>` placeholder).

## 2. Original-payload authority and proof reuse

- The public entries consume a bounded ORIGINAL GraphRequest batch
  (legitimate effective Responses root; read evidence on either the
  Responses legacy-framed or the Chat tool-result endpoint) plus one
  explicit trusted admission namespace. Caller-supplied snapshots,
  digests, flags, constructed positive partitions or graph nodes do
  not establish source authority.
- The accepted 018-b proof model, source, span, call-association and
  namespace semantics are reused via the shared private `_proof_pass`
  core (the public 018-b wrapper keeps identical behavior); NO weaker
  observer is written and the 017/018-a/018-b public surfaces and
  regressions are unchanged.
- Root authority is established only by the legitimate effective
  Responses envelope. A file result stays dependency/data provenance
  even when named `AGENTS.md` or containing normative/compiler-like
  text; the inherited 018-a competing-root-path-read refusal is
  preserved (a proven single-occurrence root-path member digest
  differing from the established root digest refuses
  `ROOT_CONFLICT`/`COMPETING_ROOTS` with no retained entries;
  boundaryless/repeated groups never infer a root hash).
- The original payload is never mutated; every retained
  `source_proofs` record is one of the accepted 018-b proof objects
  verbatim (call association, carrier spans, members, exact source
  bytes), separately bounded from the admitted-region semantic facts.

## 3. Shared cumulative preflight (one source ledger)

- The 017 re-observation runs under its OWN ACTUAL effective
  `ObservationBounds`; the bridge-owned cumulative source ledger
  (inherited from the accepted 018-b law) then spans the 018-b proof
  pass and the admission closure/index. New root/group bodies and
  owned reconstructions get NO fresh per-request or per-group budget:
  measured trusted facts are reused where possible, and every
  additional ACTUAL scan or copy (including segment re-exposure from
  an immutable `proof.source_text`, and every owned reconstruction) is
  charged with its measured byte length BEFORE the work/retention, on
  that same ledger. The ledger accounts the additional scans/copies
  charged to it; it is not claimed to account every transient 017
  observation allocation.
- Every raw-source scan counts as a document/source-group under the
  effective `max_documents`; all reference candidates share the
  effective per-source and total candidate ceilings. The ACTUAL
  effective source-byte ceilings (`max_single_source_bytes`,
  `max_total_inspected_source_bytes`) govern the MEASURED source
  bodies/copies (bytes actually inspected or owned), while the ACTUAL
  effective `max_path_bytes` path ceilings govern the workspace and
  the normalized represented member references, all enforced before
  own source/proof copies. At-limit succeeds; the first crossing
  refuses the whole snapshot with its fixed typed reason and NO
  partial admission.

## 4. Eligibility law

- Eligibility is INDEPENDENT root reachability from raw-source
  references before semantic compilation (not model rank): a node is
  eligible when root-reachable through independently attributable
  references, whether or not its content is acquired
  (`DISCOVERED_CONTENT_MISSING` stays a distinct eligible status).
  Acquisition/availability and admission are separate.
- Independently attributable singleton sources expand reachability
  regardless of list/arrival order. Unresolved candidates are
  reconsidered as sources become independently eligible, iterating to
  a bounded fixed point with strict finite improvements; cycles and
  shared nodes are preserved; a reference never invents possession; a
  mixed group cannot bootstrap its own missing eligibility from an
  unattributed reference in that group.
- Off-graph (greedy background) outgoing references are not followed
  before the member is independently graph-eligible, in either mode;
  background text/AGENTS-name/result role never acquires root or
  system authority.

## 5. Lean/greedy truth table

- All eligible: BOTH modes admit the complete whole bundle.
- Mixed eligible/background, boundaryless: lean admits nothing for
  the bundle; greedy admits the whole preserving each member's
  eligible/background classification (background is never upgraded).
- Mixed with separately proven groups: lean admits each independently
  proven group iff every member of that group is eligible;
  consecutive-cat groups remain indivisible internally; A+C is never
  concatenated around background B into a new source (no splice).
  Greedy admits the complete whole bundle if any member is eligible.
- Zero eligible: neither mode admits, including unrelated singleton
  Markdown. Unknown members/unproven regions: typed
  non-acquisition; no admission.

## 6. Group-owned certificates and the AND/OR depth law

- A boundaryless all-eligible reference resolves only when EVERY
  possible supplier is independently eligible and every supplier has
  the same canonical lexical directory (the demonstrably common base).
  The result is a typed GROUP-OWNED `GroupCertificate` binding the
  complete possible-supplier occurrence/path set, the actual reference
  evidence and group source digest, root/scope, resolved target and
  derivation depth — never a fabricated supplying file, file edge or
  shortest file-edge distance. Different-directory or
  mixed-eligibility suppliers remain `UnresolvedOriginRecord`
  evidence; equal directories alone never identify an eligible
  supplier.
- Original occurrence provenance: each certificate/unresolved record
  retains the ACTUAL original group/segment index (`segment_index`),
  request index and carrier location from the accepted proof; two
  separate identical groups on the same carrier keep distinct
  segment indices and never collapse. These coordinates are
  provenance only — never semantic content-key material.
- Derivation depth (explicit AND/OR proof depth, NOT the true
  shortest ordinary file-edge distance): root depth 0; an
  independently attributable file reference adds 1; a group
  certificate adds 1 to the MAXIMUM derivation depth across ALL
  independently eligible possible suppliers; alternative complete
  derivations take the minimum. Cycles cannot create initial
  eligibility; a pending certificate is never its own supplier proof.
- When a better supplier/node derivation appears, retained outgoing
  ordinary relationships AND already-earned certificates are relaxed
  again under the same work ledger; scanned-text caching never
  freezes downstream or certificate depths.
- `max_depth` applies to the target's LEAST complete derivation after
  the bounded fixed point; a known in-budget proof never fails because
  another route is longer. A depth refusal is DEFERRED until
  alternative shorter complete derivations have been considered; a
  target whose only complete derivations exceed `max_depth` causes a
  typed whole-snapshot refusal (`DERIVATION_DEPTH_OVER_BOUND`), never
  silent lost reachability. Root self/back-cycle target depth stays 0.
- The COMBINED number of retained ordinary file-reference
  relationships and group certificates is bounded by the effective
  `GraphBounds.max_edges` (separately typed facts, one bound);
  overflow refuses before the crossing retention.

## 7. Work ledger

- One shared admission-closure work ledger: charge 1 BEFORE each
  queue/candidate reconsideration and 1 BEFORE each possible-supplier
  examination or reverse-index association operation (including
  duplicate/unsupported attempts that reach that stage). No
  per-request/group/pass reset. Work overflow refuses immediately
  before the crossing operation, whole snapshot, no partial
  admission. The ledger is not an RSS guarantee; stage scan/source
  budgets remain separately scoped (section 3).

## 8. First-class root entry

- The effective root is its own typed REQUIRED entry, separate from
  file-tool-result entries: one known source occurrence at normalized
  `AGENTS.md` with exact extracted source bytes/digest and the
  original Responses user-envelope spans/occurrences (bounded
  provenance retained for duplicates). It is always eligible through
  ROOT-ENVELOPE AUTHORITY, independent of lean/greedy file admission.
- The root counts as ONE retained entry, ONE represented member and
  ONE root reverse-index association; duplicate root OCCURRENCES
  consume accepted inspection/candidate budgets before dedup and
  deduplicate to the single represented member charge while their
  bounded original provenance is preserved.
- The root content key is distinct from an identical-byte
  `FILE_TOOL_RESULT` at `AGENTS.md` (authority class is key material).
  Environment-context tails and wrapper bytes are not root source.
  File-admission truth-table assertions count file entries
  separately, so the required root does not turn unrelated singleton
  file reads into admitted dependencies.

## 9. Canonical structural content key

- The explicit canonical key record binds: the scoped actual
  configuration and ALL versions (including the actual reference
  grammar identity), the normalized ordered member OCCURRENCES, the
  exact aggregate source digest, the source/authority class and the
  meaningful source-ownership partition, the ACTUAL principal /
  session / repository / route / model identity / config fingerprint,
  the root digest, the mode and ALL FOUR effective bound sets. Its
  ownership groups use ENTRY-LOCAL occurrence indices and exact group
  digests (known-versus-unknown attribution); entry-local
  renumbering is solely a canonical descriptor — original proof
  `member_positions`, piece spans, IDs and positions are retained
  unchanged in provenance.
- `[A,B]`, `[B,A]`, `[A]`, `[B]` and repeated `A+A` stay independent;
  width (distinct represented paths) never proves per-file
  ownership; unknown member digests stay unknown. A singleton
  isolated from group position 1 and a standalone singleton share
  canonical local group `(0)` — identical keys when original source
  and authority semantics are equivalent.
- Known boundaries are semantic compiler input: `A="a"/B="bc"` and
  `A="ab"/B="c"` have the same aggregate bytes but different known
  ownership, so their keys differ; a boundaryless AB proof also
  differs from a known A|B partition when ownership changes
  compiler-visible attribution. Eligible/governing versus
  greedy-background classification is explicit key material (it
  cannot silently upgrade an old background compilation).
- EXCLUDED (provenance only): incidental call IDs, positions,
  occurrence IDs, parser command-form labels (read/process,
  single/loop/plan), current graph serialization, unrelated
  acquisitions, revisions and causal frontiers. A compatible
  unchanged A keeps the same structural key across a new call, an
  unrelated B acquisition, simple-cat versus earned one-iteration
  guarded-loop, and independently isolated A with equivalent original
  source/authority semantics. Key equality is NEVER labeled a
  compiler hit/compile-once result.

## 10. Reverse member-path index and version observations

- The reverse index maps EVERY represented path (including the root
  row, flagged, and greedy background members) to ALL admitted
  content keys, deduplicated AFTER charging every actual association
  attempt; the admitted-entry bound counts deduplicated semantic
  keys, not attempts.
- Source-version observations are retained INDEPENDENTLY of
  admission: a fresh standalone read may fail admission yet remain
  observation evidence (digest plus the ACTUAL original request index
  and carrier of the accepted proof that proved it) for later
  invalidation of admitted entries. This slice constructs/indexes
  facts, not freshness; no chronology is inferred from IDs, compacted
  positions, arrival counters or hashes, and unknown bytes are never
  spliced.

## 11. Effective admission bounds

- `BundleAdmissionBounds` defaults AND hard ceilings: 128 retained
  distinct entries, 1024 retained represented member occurrences
  (before distinct-path width), 4096 reverse-index association
  attempts, 64 final fixed diagnostics. Integers 1..ceiling; stricter
  settings allowed, WIDER settings refused at construction
  (`ValueError`).
- The ACTUAL accepted `GraphBounds`, `ObservationBounds` and
  `BundleProofBounds` and all their scoped versions/limits stay in
  force (cumulative request/source/member/candidate/marker/search/path
  limits), including BOTH `max_path_bytes` scopes (workspace and
  normalized represented member references).
- Every counter has an explicit pre-copy/retention check: at-limit
  succeeds, first over refuses the whole snapshot (all bound
  refusals return `entries == ()` and `root_entry is None`).

## 12. Scoped diagnostic law

- Each stage enforces its OWN emitted conflicts plus the shared
  observation limitations against that stage's cap; early shared
  root/binding refusals belong to BOTH accepted graph and proof
  surfaces (neither stage bypasses the other's cap). Independent
  stage diagnostics stay distinct — the caps are never globally
  mixed or minimized across unrelated stages.
- The admission TOTAL cap ALWAYS applies to the final emitted output
  (conflicts + admission diagnostics + deduplicated shared
  observation limitations, counted across the closed
  `AdmissionLimitation` and observation `Limitation` vocabularies by
  fixed enum value). A crossing normalizes to
  a single `DIAGNOSTICS_FULL` typed whole-empty refusal with no
  copied observations; at-limit retains the original reasons.
- All diagnostic accounting happens BEFORE work/retention (preflight
  against known limits), so an overflow never partially retains.

## 13. Version refusal

- All FIVE actual version identities bound into the namespace
  (admission, observation, graph, reference-grammar, proof) are
  checked against the actual supported constants; an unsupported
  version — even in a COHERENT direct construction with recomputed
  keys — refuses the whole snapshot with
  `VERSION_CONFLICT`/`VERSION_UNSUPPORTED` and no retained entries.

## 14. Privacy and purity

- No host IO after fixture/import setup; the original payload is
  byte-unchanged; operational `str`/`repr` of every snapshot, entry,
  proof, record and error is free of source text, private IDs,
  markers and identity values.

## 15. Tests

- `tests/test_bundle_admission.py`: original-API truth table (both
  endpoints, both modes), the proven AB|C no-splice partition with
  isolated/standalone key equality, the zero-eligible refusal and the
  acquired-empty successful singleton admission, cycles and missing
  leaves, group-depth preemption and
  descendant/certificate relaxation, the stage-scoped diagnostic
  controls (graph/proof/early-root caps), the complete structural-key
  law (ordered members, known ownership, root-vs-file, duplicate
  idempotence, scope key isolation, direct key forgery refusal), the
  ACTUAL tested bound controls at at-limit/one-over (all four
  admission bounds under narrower effective limits; the selected graph
  bounds `max_edges` (combined ordinary relationships + group
  certificates), `max_documents`, candidates total/per-document,
  `max_work_units`, `max_single_source_bytes`,
  `max_total_inspected_source_bytes`, `max_depth` least-derivation;
  the five actual version refusals), duplicate source-group segment
  provenance with the combined relationship bound, and the
  purity/privacy/unchanged-payload matrix. The full bound matrices of
  the inherited stages remain covered by the accepted 017/018-a/018-b
  regression suites (their named `tests/test_bundle_*.py` modules),
  which this slice does not restate.
- `tests/test_bundle_admission_vectors.py`: the durable 104-case
  known-synthetic original-input matrix (22 original + 66 native +
  8 group-depth-preemption + 8 interning-provenance cases, each in
  lean and greedy) over the VERBATIM S review-target vector files
  retained under `tests/fixtures/cache_admission/v1/` (a separate
  matrix-container provenance from the old
  `tests/fixtures/cache_bundles/v1/` single-observation fixture
  schema; the self-identification test pins each matrix's version,
  `PREPARED_NOT_EXECUTED` status, synthetic authority and case
  counts plus the known SHA256 originals). The accepted-proof
  equality and the canonical LEGACY source-byte oracle run per
  original read call ID independently of native parsing.

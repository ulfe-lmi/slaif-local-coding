# Current bundle admission contract (objective 018, slice g)

`CURRENT_ADMISSION_CONTRACT_VERSION = "cache-current-admission/v1"`.
`CURRENT_ADMISSION_POLICY_VERSION = "current-admission-policy/v1"`.

This contract binds the INERT current-admission slice
(`src/slaif_local_coding/constitution/bundles/`:
`current_admission_models`, `current_admission`, and the ONE public
entry `derive_current_admission`). It takes an ACTUAL accepted 018-d
`CausalHistoryState` and its ACTUAL `CausalHistoryNamespace` (plus
explicit NEW current-admission bounds and the ACTUAL supplied
018-e/018-f derivation bounds) and derives, in ONE pure bounded
operation, the accepted 018-f current graph (SAME run, charged) AND
the current admission entries with the canonical 018-c semantic
keys, the exact retained source/provenance and the complete reverse
member index. It does NOT select compiler targets, compile, inject,
replace, own RAM services, refresh the root, or execute observed
commands. It is delivered as inert code on PR 26 (which stays
unmerged until the whole numeric 018 is complete), IMPLEMENTED and
PENDING strategic acceptance at its bounded inert scope: like the
accepted 017, 018-a, 018-b, 018-c, 018-d, 018-e and the accepted
018-f slices it is pure and never active in the adapter runtime. 018-f
is accepted ONLY at its actual bounded inert current-graph scope WITH
process qualifications (S/reviews/018-f-decision.md); 018-g is PENDING
acceptance at this bounded inert scope. It earns the whole-018
current-version admission MECHANISM at its bounded scope only
(PARTIAL); no runtime stale-injection, compiler activation,
root-refresh or later-stage pass is claimed; 019–024 remain.

## 1. Input, namespace revalidation and caller trust

- `derive_current_admission(state, ns, bounds=None,
  currentness_bounds=None, graph_bounds=None)` takes the ACTUAL
  retained 018-d state and its ACTUAL namespace; omitted bound sets
  default to the supported defaults. The input is the INTERNAL
  retained-history boundary, never a public supplied
  proof/snapshot/header authority: object construction is not
  authentication. No caller-supplied overlay/graph/snapshot/current
  flag establishes anything.
- Early fences are O(1) in the historical state and precede ANY scan
  or copy: the ACTUAL state history key is compared against the
  ACTUAL namespace history key (`REFUSED_FOREIGN_SCOPE` /
  `FOREIGN_SCOPE` on mismatch); the ACTUAL namespace is revalidated
  through the accepted 018-e actual-field law (the SEVEN ACTUAL
  inherited version fields against the supported constants — a
  coherent UNSUPPORTED actual version refuses
  `REFUSED_VERSION_CONFLICT` / `VERSION_UNSUPPORTED` — plus the
  fresh-dict actual history-field shape and the admission/bounds
  rechecks that 018-e defines). Unsupported coherent versions,
  foreign scope and malformed state refuse BEFORE any positive
  interpretation.
- The supplied bound sets are revalidated through FRESH bounded
  actual-field validation (a `warnings=False` serialization of the
  model into a fresh dict through the real validators); an
  unvalidated instance or a mutated bounds record raises a plain
  `ValueError`, never interpreted.
- The ACTUAL 018-c admission namespace is reconstructed from the
  actual fields with BOTH 64-hex scope keys re-derived from them: an
  incoherent scope is a fixed foreign-scope refusal, never a silent
  pass.
- The derived admission describes the EXACT input history scope,
  revision and unchanged actual RootAnchor. It never advances a
  revision, never introduces a clock, and confers no
  compiler-semantic key on any unchanged source beyond the canonical
  018-c identity.

## 2. Root entry and retained root provenance

- The `RootAnchor` is the ONLY root-text supplier and the root entry
  is ALWAYS present on an `ok` derivation (the anchor stays current,
  empty or not). A missing anchor is refused by 018-f before the
  admission phase (`REFUSED_NO_ROOT`).
- The root entry retains the ACTUAL `RootAnchor` typed fields
  exactly: the same `root_text`, `root_source_byte_length`,
  `root_digest` and the typed `RetainedRootProvenance` mirroring the
  anchor's narrow original extraction coordinates
  (`first_request_index`, `location`, `content_span`,
  `envelope_span`, `source_byte_length`, `root_digest`,
  `workspace`). The anchor carries NO original `RootOccurrence`
  kind/status/reasons and NONE are invented; a
  `RootEnvelopeOccurrence` or original transport envelope is never
  fabricated. The exact EMPTY root is legitimate (root authority is
  the evidenced envelope, not nonempty text).
- The root entry is `ROOT_ENTRY`-class, width 1, member
  occurrences `("AGENTS.md",)`, aggregate digest equal to the anchor
  digest, and carries NO witnesses (the anchor is not a read
  occurrence). A changed-bytes root refresh stays a competing
  effective root: 018-d refuses it with the exact state while the
  admission retains the original root row; a SAME-BYTES proven
  root-path read is CONSISTENT with the anchor and admits an
  AGENTS.md file entry whose anchor row keeps its own distinct key.

## 3. The currentness truth table

Admission plans come ONLY from the ACTUAL same-run 018-e
per-owned-group currentness and the accepted 018-f graph
eligibility (every F node is root-reachable, root depth 0); stale,
conflicting and ambiguous groups are excluded BEFORE entry planning
or copying:

- whole admissible (ALL owned groups current and compatible, and NO
  root-owned boundaryless group whose unattributed root bytes can
  never be proven compatible with the `RootAnchor`): all members
  independently eligible → the complete whole bundle in BOTH modes;
  mixed eligible/background → greedy admits the whole iff at least
  one member is independently eligible, lean admits each
  independently proven all-eligible segment as its own contiguous
  entry (never the whole PLUS isolated rows together).
- whole NOT admissible: whole admission is impossible in BOTH modes;
  lean admits each independently CURRENT all-eligible group that is
  not a root-owned opaque region as its own single-segment entry;
  greedy gains NO new isolated-region rule (it admits nothing from
  the proof).
- zero independently eligible members: neither mode admits.

The boundary is per OWNED GROUP: a blocked opaque group is
indivisible and supplies nothing (no member-only splice), a genuine
descendant singleton overlapping an opaque AB conservatively stales
the old AB EVEN IF the singleton bytes equal the old aggregate
(equality does not grant the unknown per-file ownership, and replay
alone adds no freshness), and a root-bearing opaque group can never
prove its root bytes.

## 4. Entry interning, witnesses and proof retention

- File entries are interned by DISTINCT canonical 018-c content key:
  a duplicate-key plan adds witnesses only and re-owns NO source
  bytes (the distinct key counted its bytes once). The descriptor
  mirrors the accepted 018-c `_file_entry` law exactly (ordered
  admitted member occurrences, the per-occurrence
  ELIGIBLE/GREEDY_BACKGROUND authority vector, the entry-local
  ownership partition with PROVEN/BOUNDARYLESS classes, the
  canonical aggregate digest).
- The retained entry `proof` is the FIRST compatible original proof
  in processing order (usually the OLDER occurrence), retained by
  identity — never a newest-only winner and never a re-derived copy.
  Distinct same-byte compatible witnesses at their OWN original
  proof/group coordinates are ALL retained, qualified by the SAME
  content/ownership: a changed child of ONE of two concurrent equal
  claims blocks, and a genuine child of BOTH resolves keeping the
  older compatible changed read AND the newer one ONLY because both
  retained changed reads have equal compatible content/ownership —
  different-source descendants must not retain incompatible old
  entries, and the first processing/retention order is provenance,
  not a temporal newest/oldest claim.
- Witness retention order is the canonical full-coordinate tuple
  `(occurrence_id, request_index, call_position, result_position,
  segment_indices)` — never the acquisition order. Duplicate
  coordinate tuples count BEFORE dedup.
- The newly owned entry-source UTF-8 bytes are counted once per
  DISTINCT interned semantic entry (root included) against the NEW
  cumulative ceiling, with the per-entry cap the ACTUAL inherited
  `GraphBounds.max_single_source_bytes` preflighted BEFORE any
  admission-owned walk or copy. The preflight governs G-owned work
  BEYOND the already-positive F: the entry-cap target control
  compares ZERO ADDITIONAL G touches beyond the positive F's own
  source inspection (the complete G source touch profile — slices,
  index accesses, encodes — equal to the positive F profile), never
  zero touches over the entire derivation.

## 5. The complete reverse member index

`path_associations` is the complete reverse member-path index: every
represented member path maps to ALL currently admitted content keys
(overlaps and greedy background included). Association ATTEMPTS are
charged BEFORE dedup (the root association is one of them) against
the ACTUAL inherited `max_reverse_associations`; rows keep distinct
content keys, the root row is the only root flag, and the model
revalidates that every represented member path of every entry maps
to its content key through a single built key-set index (O(1)
membership, no dense-row re-search per entry).

## 6. Retained admission reasons

- The emitted admission reasons are RETAINED in the overlay as the
  actual bounded sorted/deduplicated `admission_reasons` tuple;
  `emitted_admission_reasons` is bound to its length on every
  construction (a mismatched count is refused).
- A normal derivation emits at most ONE unique reason: the fixed
  `candidate_unproven` when at least one retained occurrence admits
  nothing (including replaced/stale occurrences that contribute no
  plan in this derivation). The count and the tuple are both
  caller-inspectable; the result-level `diagnostics` stay the
  derivation-level refusal reasons (empty on `ok`).
- The cap is enforced in the SAME admission domain jointly: BOTH the
  NEW `CurrentAdmissionBounds.max_diagnostics` and the ACTUAL
  inherited `BundleAdmissionBounds.max_diagnostics` bound the
  retained tuple (each is 1..64). Because a normal derivation emits
  at most ONE unique reason, the PUBLIC first-over of either
  diagnostics cap is unreachable through the original API: the
  first-over controls are DIRECT CONSTRUCTOR-only schema evidence
  (with the coherent recomputed scope key and the strict positive
  at-cap control), distinct from public acquisition evidence.
  018-f graph diagnostics stay F
  output carried by reference (`graph` field with its own scope/
  diagnostics), never re-emitted here; 018-f reason emission keeps
  the ACTUAL supplied current-graph diagnostic ceiling.
- Every emission attempt is charged on the NEW admission diagnostic
  ledger BEFORE the operation; the stage-level admission work domain
  is the ACTUAL inherited `GraphBounds.max_work_units` (a distinct
  stage from the F stage, both under the ONE shared outer).

## 7. Scope key and version binding

- The derivation `scope_key` is RECOMPUTED from the actual fields on
  every construction (a stale or forged key is refused, never
  retained) and binds: the ACTUAL history scope (history key,
  workspace), the ACTUAL root digest, every ACTUAL inherited version
  (admission/observation/graph/reference/proof/history/arguments),
  the accepted 018-e and 018-f contract/policy/recipe versions, the
  NEW current-admission contract/policy versions, the validated
  018-e and 018-f scope keys, the ACTUAL 018-c admission namespace
  and scoped keys, and EVERY effective bound set (new
  current-admission, currentness, current-graph, admission, proof,
  graph and observation).
- The compiler-semantic key records (root and file) bind the
  ACTUAL 018-c namespace identity, mode, root digest, versions and
  INHERITED bounds — NOT the derivation-only 018-e/018-f/018-g
  bounds: changing only successful derivation bounds changes the NEW
  scope key while every semantic key record stays byte-identical.
- The carried graph must describe the EXACT input scope/revision
  with matching root digest and scope key; the root entry binds the
  actual root digest.

## 8. Bounds and the shared work law

- ONE OUTER work ledger (`max_total_work_units`, 1..1048576) covers
  the ENTIRE operation: actual history validation, 018-e
  currentness, 018-f graph, admission planning, source/key
  construction, interning, witness/origin/index and output work, all
  charged BEFORE the crossing operation. The ACTUAL supplied 018-f
  `CurrentGraphBounds.max_total_work_units` ceiling is enforced
  independently on the SAME shared outer (a private chained ledger):
  stricter F subtree work refuses even when the G total still has
  headroom, and no per-group/pass reset occurs. The essential
  positive: the F cap exactly F's cost with the G total above it —
  full G succeeds.
- The stage-level admission work runs under the ACTUAL inherited
  `GraphBounds.max_work_units` on the NEW admission stage
  (`ADMISSION_WORK_UNITS_EXHAUSTED`), distinct from the F stage
  domain which stays preserved.
- The cumulative newly owned entry-source bytes
  (`max_total_entry_source_bytes`, 1..16777216) are per derivation,
  per DISTINCT interned key (root included), never per witness and
  never per segment visit; the per-entry cap is the ACTUAL
  inherited `GraphBounds.max_single_source_bytes`.
- The ACTUAL inherited admission caps keep their admission-output
  domains on the G output: `max_entries` (1..128, deduplicated
  semantic entries including the root), `max_member_occurrences`
  (1..1024, charged before distinct-path width),
  `max_reverse_associations` (1..4096, attempts before dedup).
- Collection law: G-owned graph-owned and admission-owned
  collections use the accepted charged stable merges — linear
  reservations (1+n construction/working copy; 1+2n for dedup sorts
  whose set-walk covers the INPUT length; per-member filter/any
  walks) BEFORE each operation, then one unit on the crossing
  ledgers before EVERY actual comparison and element write, keys
  moving with values through every pass (exact totals
  1+n+n*ceil(log2 n)+comparisons and 1+2n+m*ceil(log2 m)+comparisons
  for the charged merge helper; empty input charges nothing). The
  inherited model validators' own single-pass sorts/copies are
  separately pre-reserved (generated ascending-run checks), and no
  general built-in-sort upper bound is claimed anywhere. The
  witness-retention dedup over the FULL coordinate tuples reserves
  1+2n on BOTH ledgers before the first crossing copy/iteration (an
  exhausted ledger refuses with zero pre-copy reads); the output
  model-validation walk, including the retained reason tuple's
  sorted/dedup walk and count/cap binding, is reserved before
  construction.

## 9. Atomicity and typed refusal

- `ok` carries the derived admission (graph + entries + reverse
  index + retained reasons) and the EXACT input state object by
  identity; every refusal carries the EXACT input state and NO
  partial entries/index/graph plus its closed reason(s):
  `REFUSED_FOREIGN_SCOPE` (foreign history scope, incoherent 018-c
  scope), `REFUSED_VERSION_CONFLICT` (coherent unsupported actual
  version), `REFUSED_NO_ROOT`, `REFUSED_STATE_MALFORMED` (corrupted
  retained occurrences, forged anchor, malformed retained proof),
  `REFUSED_OVER_BOUND` (every resource crossing, with the exact
  G-own or inherited mapped name: outer total, admission stage,
  entry-source per-entry and cumulative, inherited entries/member
  occurrences/reverse associations, and the F-subtree/f-stage
  mappings for upstream F refusals).
- A derivation never advances any revision and never mutates the
  input; the exact old replay restores nothing.

## 10. Privacy and purity

- Operational reprs of every NEW G-owned record (admission, root
  entry, file entries, witnesses, retained-root provenance, reverse
  rows) suppress private source/ID values: fixed enums, counts,
  digests and placeholders only; the actual internal path fields
  stay unchanged.
- No host IO on ANY public path (the `ok` derivation and every
  refusal): no file, socket, subprocess or path facility is touched.
- Unvalidated namespace fields are never serialized through a
  warning-producing path before fresh validation rejects them; the
  returned refusal reprs are private.

## 11. Tests

- `tests/test_current_admission.py`: the ACTUAL original-API matrix
  (criteria A–G of the order) over BOTH read endpoints and BOTH
  admission modes, all fixtures inline known-synthetic original
  GraphRequests with no S runtime dependency: withdrawal/restoration
  through actual complete-empty descendants, alternates and the
  self-supporting certificate cycle; partitioned A|B independence,
  opaque indivisibility, mixed background/conflict and content
  variants; equal known claims (two-frontier child-of-one/child-of-
  all with the older compatible proof retained, the actual E
  frontier versus compatible groups), equal-looking staling,
  delayed/late result and shifted replay; exact canonical 018-c key
  equality/inequality and the old-C batch equality matrix (root/
  whole/isolated/repeated/loop/Unicode/empty-root) under ONE shared
  admission namespace; the root entry typed retention (exact empty
  root, refresh refusal, same-bytes root read, partitioned
  root-compatible whole, root-competing refusal, root-bearing
  opaque plus independently proven nonroot segment); the complete
  reverse index (isolated B segment 1 versus standalone B segment 0
  at their own proof coordinates, first-proof retention, whole
  plus standalone independent entries); every new/inherited cap at
  limit and first over (ONE shared outer plus the independent
  F-subtree ceiling with the essential positive, the per-entry
  inherited single-source cap over the actual partitioned aggregate
  via a coherent stricter-bound diagnostic projection with exact
  source-touch-profile equality, the cumulative entry-source bytes
  counted once per distinct key, the stale-region sentinels, the
  merge-witness reserve-before-copy sentinel, the plan/assembly
  charged-walk thresholds); retained admission reasons (exact
  unadmitted tuple/count, zero-reason control, result-level
  separation, constructor count/cap/schema negatives with the
  coherent recomputed scope key and the strict positive at-cap
  control); derivation-only bound identity (new scope key distinct,
  semantic key records byte-identical); typed
  foreign/version/no-root/malformed refusals with the exact state;
  130 retained observations legal under the default ceilings;
  private operational reprs and no host IO on every public path.
- The original public batch admission, observation/proof/history/
  currentness/current-graph APIs, canonical argument recipe and
  reference laws are unchanged. All 017/018-a/b/c/d/e/f regressions
  are REQUIRED to remain green for acceptance; the verification
  claims here are bound to the ACTUAL observed scope and status at
  this round (the focused suites, the actual original-API controls
  and the recorded ROOT rechecks), NOT to a final qualified gate:
  the expected stale-development-manifest failures on clean source
  are recorded as historical/factual, not observed passes, and no
  exploratory or preview suite is treated as the final clean-B
  qualification.

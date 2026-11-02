# Current graph closure and version-owned withdrawal contract
# (objective 018, slice f)

`CURRENT_GRAPH_CONTRACT_VERSION = "cache-current-graph/v1"`.
`CURRENT_GRAPH_POLICY_VERSION = "current-graph-policy/v1"`.

This contract binds the INERT current graph closure slice
(`src/slaif_local_coding/constitution/bundles/`:
`current_graph_models`, `current_graph`, and the ONE public entry
`derive_current_graph`). It takes an ACTUAL accepted 018-d
`CausalHistoryState` and its ACTUAL `CausalHistoryNamespace` (plus
explicit current-graph and 018-e currentness bounds) and derives, in
ONE pure bounded operation, the current graph over the ACTUAL
currentness facts: the selected current source suppliers, the fresh
least fixed point of root reachability, the version-owned ordinary
edges and group certificates, the honest per-node availability
states, the least complete AND/OR depths, and the retained
unreachable possession. It does NOT select admission entries,
compile, inject, replace, own RAM services, refresh the root, or
execute observed commands. It is delivered as inert code on PR 26
(which stays unmerged until the whole numeric 018 is complete),
IMPLEMENTED and PENDING strategic acceptance at its bounded inert
scope: like the accepted 017, 018-a, 018-b, 018-c, 018-d and 018-e
slices it is pure and never active in the adapter runtime. It earns
the C04/C05 current graph MECHANISM at its bounded scope only
(PARTIAL); current admission/entry planning with canonical 018-c
keys, the explicit root-refresh authority-lineage contract,
stale-injection end-to-end acceptance and the remaining whole-018
acceptance remain later mandatory same-018 work, then 019–024;
nothing here is a v1 runtime, compiler-hit, actual-wire-receipt,
recovery, client or root-refresh claim.

## 1. Input, namespace revalidation and caller trust

- `derive_current_graph(state, ns, bounds=None,
  currentness_bounds=None)` takes the ACTUAL retained 018-d state
  and its ACTUAL namespace; omitted bound sets default to the
  supported defaults. The input is the INTERNAL retained-history
  boundary, never a public supplied positive proof/snapshot/header
  authority: object construction is not authentication. No
  caller-supplied overlay/graph/snapshot/current flags, synthetic
  Root requests or fabricated RootOccurrence records exist.
- Early fences are O(1) in the historical state and precede ANY
  scan or copy: the ACTUAL state history key is compared against
  the ACTUAL namespace history key (`REFUSED_FOREIGN_SCOPE` /
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
  actual-field validation (`warnings=False` serialization of the
  model into a fresh dict through the real validators); an
  unvalidated instance or a mutated bounds record is refused with a
  plain `ValueError`, never interpreted.
- The derived graph describes the EXACT input history scope,
  revision and unchanged actual RootAnchor. It never advances a
  revision, never introduces a clock, and confers no
  compiler-semantic key on any unchanged source. Temporal
  provenance, semantic source identity and graph derivation
  identity remain separate.

## 2. Root anchor law

- The retained `RootAnchor` is the ONLY root-text supplier. A
  missing anchor refuses `REFUSED_NO_ROOT` / `ROOT_MISSING`.
- Every ACTUAL anchor field is freshly validated under charged
  length/source preflights BEFORE any governing use: string
  fields, integer fields and span types (a string where an integer
  coordinate is required is malformed, not coerced), integral
  original coordinates (fractional spans are malformed),
  content-span/envelope-span containment, text/digest/byte-length
  consistency, workspace binding, and UTF-8 decodability. Fresh
  field-shape validation, not `model_validate(existing_instance)`
  alone, establishes the anchor.
- The root region's character count is checked O(1) against the
  effective cap BEFORE any UTF-8 walk, owned copy, encode or hash;
  the walk is bounded with an early exit at
  `cap = min(GraphBounds.max_single_source_bytes,
  GraphBounds.max_total_inspected_source_bytes − stage.bytes_spent)`,
  so an over-count region refuses with ZERO character inspections
  and ZERO encodes. Every field-shape check and every inspection
  step charges BOTH the shared outer work ledger and the inherited
  graph-stage work domain BEFORE the operation.
- A malformed anchor refuses `REFUSED_STATE_MALFORMED` /
  `ROOT_MALFORMED` with the EXACT input state; the anchor is scope,
  not a file supplier with occurrence witnesses. Positive fixtures
  acquire the anchor through original API observation; a coherent
  constructor alone is not source authentication. Root-path
  refresh remains refused by 018-d (COMPETING_ROOTS); this slice
  adds no root authority and no root-refresh contract.

## 3. Supplier selection BEFORE any scan

- Selection consumes the ACTUAL 018-e overlay (derived through the
  private shared-work seam over the same state/namespace): the
  per-OWNED-GROUP currentness rows, not only whole-proof usable
  IDs. A proven A|B proof with a changed descendant A keeps the B
  group current even though the old whole occurrence is unusable;
  B is selected without scanning or copying the stale A region.
- CURRENT_KNOWN singleton groups become SOURCE suppliers keyed by
  the ACTUAL (path, granted digest); the owner/proof metadata is
  interned ONCE (charged on both ledgers), never copied per edge.
  A repeated contributing group retains its OWN original
  proof/group coordinate even when the witness occurrence is
  already present (the association attempt is charged before
  dedup); equal historical bytes are reused only under genuine
  current evidence, and old provenance is never relabeled as a
  fresh event.
- CURRENT_OPAQUE boundaryless groups become GROUP suppliers keyed
  by (versioned opaque identity, aggregate segment digest, ordered
  members): the aggregate region is preflighted, precharged,
  copied and scanned ONCE per distinct key. A root-only group
  supplies NOTHING (no byte work). GROUP suppliers carry no
  per-file path or hash: repeated members do not inflate distinct
  width or invent individual ownership, and no per-file ACQUIRED
  hash is ever spliced out of an opaque aggregate.
- Blocked, stale or ambiguous groups are EXCLUDED before scanning:
  no scan, no copy, no edge, no certificate, no spliced
  pseudo-singleton source. An opaque group with one stale or
  ambiguous member is indivisible.

## 4. Joint least fixed point and ownership law

- Reachability is rebuilt FRESH from the immutable root only. No
  previous eligibility/depth/edge/certificate is seeded; the root
  closure node is charged on the shared outer work ledger and the
  inherited node ceiling BEFORE insertion (no uncharged root
  bypass). Cycles cannot bootstrap eligibility.
- Only CURRENT_KNOWN nodes are scanned for outgoing references;
  CURRENT_EMPTY nodes acquire NO outgoing edges (a completed empty
  source withdraws its prior references); DISCOVERED_UNACQUIRED,
  BLOCKED_CONFLICT and BLOCKED_AMBIGUITY nodes supply nothing.
  Unrelated current sources still supply their own derivations.
- Ordinary edges are version-owned derivations explicitly tied to
  the ACTUAL current semantic source digest (the source node's
  owner) plus original witness provenance: removing an owner
  removes ONLY its derivation; a complete surviving alternate
  keeps the target. An unavailable source cannot supply outgoing
  edges; a new current source returning a reference may restore
  reachability using already-possessed current downstream
  originals — no fabricated new acquisition, and an old replay
  alone restores nothing.
- A possessed source referenced by NO current derivation is
  off-graph: it stays a current supplier, is listed honestly in
  `unreachable_current_paths`, and its outgoing references are
  NEVER scanned or joined. Greedy background co-occurrence is not
  independent eligibility.

## 5. Group certificate law

- A GROUP-OWNED certificate for one candidate of one current
  opaque group is usable only when EVERY non-root possible supplier
  is independently current AND reachable in the joint fixed point
  at the evaluating pass, the candidate is ACCEPTED, and the
  non-root possible suppliers share the SAME canonical lexical
  directory (the accepted common base; convergent absolute
  references to one target from different referring directories
  never compensate). The common directory does not identify the
  supplying member; resolution is per possible supplier.
- A reachability-only block (supplier not yet in the fixed point)
  is TRANSIENT and re-evaluated in later passes; a supplier
  already in R but not current is a PERMANENT block. Root-bearing
  groups carry `ROOT_MEMBER_UNATTRIBUTED` and never certify an
  unproven root compatibility; root members are scope context
  only and are never certificate suppliers. A root-only group
  carries `NO_SUPPLIER`.
- Every closed blocker is retained at once (`NOT_INDEPENDENTLY_
  REACHABLE`, `NO_COMMON_DIRECTORY`, `ROOT_MEMBER_UNATTRIBUTED`,
  `NO_SUPPLIER`); a usable certificate carries its resolved
  target, its derivation depth and NO reasons. An unresolved
  candidate is never an ordinary file edge. Retained candidate
  evidence (typed target-law limitation or non-path target) is
  kept with its supplying owner.
- The COMBINED count of ordinary edges and usable certificates is
  bounded by the ACTUAL inherited `GraphBounds.max_edges`.

## 6. Least complete AND/OR depth

- Node depth is the LEAST complete derivation depth: ordinary
  edges contribute `depth(source) + 1`; a usable certificate
  contributes `1 + MAX` over ALL of its (independent supplier)
  least depths; alternatives take the MIN. The root stays 0 and a
  root self/back-cycle target stays 0.
- Depths are relaxed to the least complete values AFTER the joint
  fixed point, and the effective `GraphBounds.max_depth` is
  enforced AFTER the fixed point (`GRAPH_DEPTH_OVER_BOUND`).
  Repeated members do not inflate the derivation depth. A
  shallower re-visit never deepens a walk.

## 7. Identity, owner, witness and scope-key law

- `ROOT_OWNER = "root-anchor/v1"` is the closed owner label for the
  root node and its owned derivations. A current proven source
  owner is `_owner_source(path, digest)` and a current opaque
  group owner is `_owner_group(identity, group_digest)`: each is
  the sha256 of a domain-separated canonical payload — a bounded
  64-hex identity, observable like a digest, with NO path
  embedding (no arbitrary text cap, no control characters). A
  node's owner must equal the recomputed binding for its exact
  path and digest; free-text owners are refused.
- `witnesses` retain ALL supporting occurrence IDs (first
  provenance, never relabeled; sorted and deduplicated).
  `coordinates` retain the ORIGINAL proof/group coordinates per
  contributing group (occurrence id, group index, request index,
  call position, result position). The group digest is never a
  member hash or namespace authority.
- `current_graph_scope_key` binds, in one sha256 over a
  JSON-canonical payload: the ACTUAL validated history key, the
  workspace, the ACTUAL root digest, the record's ACTUAL
  current-graph contract/policy version fields, the inherited
  graph/reference/proof versions, the currentness contract/policy/
  recipe versions, the validated 018-e scope key, the ACTUAL
  inherited GraphBounds and EVERY new current-graph bound
  (plus the ACTUAL 018-e bounds). A caller tag alone cannot
  establish identity, and a stale/forged key over different
  actual fields refuses at construction. The derivation
  revalidates the actual fields first and emits only the
  supported constants.

## 8. Graph-vs-content completeness

- A typed complete graph derivation is NOT a claim that all
  required source content exists. Every represented node carries
  its honest availability state (`CURRENT_KNOWN`,
  `CURRENT_EMPTY`, `DISCOVERED_UNACQUIRED`, `BLOCKED_CONFLICT`,
  `BLOCKED_AMBIGUITY`); reference establishes eligibility, not
  possession; unavailable/blocked nodes assert no content, owner
  or witnesses.
- `unreachable_current_paths` lists the possessed proven suppliers
  NOT joined by the fresh root closure (honest off-graph
  retention); `emitted_reasons` is the TOTAL newly emitted
  closed-enum reason entries (one per blocked node plus every
  certificate reason) and never exceeds the hard diagnostic
  ceiling. Retained input-state diagnostics are not new
  emissions, and the nested 018-e overlay is not re-exposed as
  output (its validated scope and the selected supplier facts are
  carried instead).

## 9. Bounds and the shared work law

- `CurrentGraphBounds` (defaults AND hard ceilings, stricter
  positive values allowed, wider refused):
  `max_total_work_units = 1048576` — ONE OUTER work ledger over
  the ENTIRE operation: actual currentness and
  history-validation work, group selection/interning,
  source/reference work, closure relaxations and output, all
  charged BEFORE the crossing operation; `max_diagnostics = 64` —
  TOTAL newly emitted graph closed limitation/reason entries,
  charged before each actual emission attempt (duplicates count
  before output dedup).
- The outer ledger is shared through the cohesive PRIVATE
  callback/factoring seam into the accepted 018-e derivation:
  018-e work charges the outer ledger AS WELL AS its own domain;
  graph source/scan/closure/emission charge the outer ledger plus
  the ONE graph-stage ledger (the ACTUAL inherited
  `GraphBounds`: work, nodes, edges, candidates, documents,
  source bytes, diagnostics, depth, path bytes). The old public
  admission entry/member caps are NOT new graph-output caps (this
  slice creates no admission snapshot/entries);
  `GraphBounds.max_requests` bounds ORIGINAL API batches, not
  retained occurrences across many batches.
- Exact charged-unit law: every ACTUAL inspected group/member/
  association/comparison, parent/graph edge visit, owned copy and
  emitted output association (node, edge, certificate, candidate,
  supplier, unreachable path, scope-key computation) is charged on
  the relevant ledger(s) BEFORE the operation, including
  association attempts that dedup to nothing and duplicate
  reason entries that output dedup removes. Owner/proof metadata
  is interned once rather than copying whole proofs per edge.
  Source byte preflights respect the REMAINING total inspected
  allowance, not only the single-source cap. No ledger is reset
  per group/pass/query; no hidden quadratic precursor runs
  before charging; no repeated public-helper call with fresh
  budgets.
- Graph-owned collection reservation law (charged stable merge,
  ACTUAL comparisons): every graph-owned sort over a sized
  iterable (``_sorted``, ``_sort_witnesses``, and the per-record
  output sorts) first charges a LINEAR reservation on BOTH
  ledgers before touching the collection: ``_sorted`` charges
  ``1 + n`` (one construction unit plus one working-copy unit per
  element, which also covers the one-shot key extraction; empty
  input performs no work and charges nothing);
  ``_sort_witnesses`` charges ``1 + 2n`` (construction, a
  membership/hash walk over the INPUT length -- duplicates count
  -- plus the working copy) before the set dedup. Other linear
  walks charge their length before the walk (per-member
  filter/``any`` compounds: ``2n``; output filter walks: ``n``).
  The merge itself is a charged stable bottom-up merge: ONE unit
  on both ledgers before EVERY actual comparison and ONE before
  EVERY element write; the extracted keys MOVE WITH their values
  through every pass, ties keep the earlier element, and element
  writes are exactly ``n * ceil(log2 n)``. Exact totals:
  ``_sorted`` = ``1 + n + n*ceil(log2 n) + comparisons``;
  ``_sort_witnesses`` = ``1 + 2n + m*ceil(log2 m) + comparisons``
  (m = unique count). The comparisons are the ACTUAL merge
  decisions charged as they happen -- not a claimed upper bound
  for the built-in sorter (a decision-tree lower bound and
  sampled measurements are not worst-case proofs for the
  supported domain). The only remaining built-in ``sorted`` is
  the typed-refusal construction, outside the collection-charge
  scope.
- A target-cap test must reach THAT cap with the other caps
  valid (pre-copy sentinels prove the refusal happens before the
  inspection it bounds). Cost assertions are EXACT-FIXTURE/ID
  bound: lexical canonical order can change actual walk cost,
  never chronology.

## 10. Atomicity and typed refusal

- `CurrentGraphResult(outcome, state, overlay, diagnostics)`:
  `state` is ALWAYS the EXACT input state object (identity
  preserved on every outcome; the input is immutable and never
  mutated or re-ordered). `OK` carries the derived graph and no
  diagnostics; every refusal carries the EXACT input state, NO
  partial graph, and its closed diagnostic reasons (sorted and
  deduplicated).
- Closed outcomes: `OK`, `REFUSED_FOREIGN_SCOPE`,
  `REFUSED_VERSION_CONFLICT`, `REFUSED_STATE_MALFORMED`,
  `REFUSED_NO_ROOT`, `REFUSED_OVER_BOUND`. Closed limitation
  vocabulary: `FOREIGN_SCOPE`, `VERSION_UNSUPPORTED`,
  `STATE_MALFORMED`, `ROOT_MISSING`, `ROOT_MALFORMED`,
  `TOTAL_WORK_UNITS_OVER_BOUND`, `DIAGNOSTICS_FULL`,
  `GRAPH_NODES/EDGES/CANDIDATES/DOCUMENTS/SOURCE_BYTES/DEPTH/
  WORK_UNITS/DIAGNOSTICS_OVER_BOUND`, the five 018-e currentness
  domains (surfaced through the private seam with their 018-e
  scope kept) and `HISTORY_WORK_UNITS_OVER_BOUND`. A crossed
  domain yields its ONE fixed limitation; a scanner limitation on
  an inspected current body is a typed whole-result refusal
  (per-document candidate overflow maps to
  `GRAPH_CANDIDATES_OVER_BOUND`; an undecodable retained region is
  corrupted state and fails closed as `STATE_MALFORMED`). An
  unknown currentness pairing fails closed as malformed, never as
  positive evidence.

## 11. Privacy and purity

- Fixed enums/counts/private repr/errors only: workspace path
  VALUES never appear in any operational representation of a
  018-f record (the fixed `<private-path>` placeholder with its
  presence/absence flag; the graph-level repr masks the
  workspace). The retained `ReferenceCandidate` is embedded but
  never interpolated raw: only the fixed-vocabulary summary
  (syntax, status, occurrence index, target LENGTH, spans,
  closed reasons) is emitted. Digests/owners are 64-hex
  observables. No raw prompts/source/tool output/images/
  credentials in logs, metric labels, errors or reprs.
- Pure and inert: no host IO (filesystem, network, subprocess or
  path facilities) on ANY public success or refusal path; no
  pipeline activation, no RAM service/locks, no compiler, no
  disk, no HTTP/SSE observer, no new metrics. Existing source
  history is immutable.

## 12. Tests

- `tests/test_current_graph.py`: the ACTUAL original-API matrix
  (criteria A–J of the order) over BOTH read endpoints and BOTH
  admission modes: withdrawal/restoration through actual
  complete-empty descendants, certificate self-bootstrap
  refusal, singleton-vs-opaque staling (including the
  equal-looking variant and equal-digest reversed AB/BA),
  partitioned per-member independence, boundaryless
  indivisibility, least AND/OR depth (alternatives,
  recompute-after-withdrawal, off-graph non-governance,
  repeated-operand group ownership), equal incomparable
  witnesses (interning, changed child of one, child of all,
  unissued new version, delayed older result, late trusted
  receipt, shifted replay), availability states (pending/
  truncated/nonzero frames, root refresh refusal, root-bearing
  attribution, anchor field-shape/span/Unicode negatives,
  preflight sentinels), the 129-request batch pair control, the
  exact at-limit/first-over resource matrix (outer work, graph
  stage work, diagnostics, all six inherited caps, the charged
  collection reservation law -- output identity against the
  built-in sorted including multi-pass/keyed/stability/duplicate
  forms, the exact accounting totals, and zero-touch
  below-reservation refusals -- foreign/
  malformed/unsupported-actual-version forgeries) and
  no-host-IO/privacy controls.
- `tests/test_current_graph_models.py`: the constructor-level
  record invariants (closed enums, sorted/deduplicated
  containers, owner bindings, bounds ceilings, edge/diagnostic
  ceiling arithmetic, emitted-reason accounting, recomputed
  scope-key binding of the actual version fields, and the
  nested repr/str privacy law). Construction is not
  authentication; the state objects used come from ACTUAL 018-d
  root bootstraps.
- All 017/018-a/b/c/d/e regressions remain green; the original
  public batch admission, observation/proof/history/currentness
  APIs, canonical argument recipe and reference laws are
  unchanged.

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
independent budget domains) are implemented and PENDING strategic
review. At its bounded inert scope, like the accepted 017,
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
  nested bound refuses before the first serializer visit). No
  hidden Pydantic source rewalk and no repeated full-source
  walk per witness.
- The durable G-matrix evidence covers every new and inherited
  cap at-limit/first-over with target-reaching sentinels, the
  independent phase ceilings beneath a larger whole cost, the
  cumulative/batch scope distinction, the long-workspace
  model/namespace reservations (actual-work bounded in the
  workspace length, never a hidden constant) and the charged
  model/source/compare/copy/sort/index attempts.
- The NEW-I key-record fence (``KEY_RECORD_FENCE_UNITS``, charged
  on the I outer per planned entry and on the root-entry
  reservation) belongs to the I outer ONLY: it is charged before
  the entry models exist and never inside the G/admission stage,
  so the G total stays exactly the inherited F+admission subtree
  with no composition fence (J03a).
- The independent-domain evidence (J03) closes every named domain
  at-limit and first-over at the ACTUAL public-I boundary where
  reachable, and at the named bounded stage/constructor surface
  where the public first-over is structurally unreachable; each
  crossing yields its ONE fixed inherited (or NEW-I) name, never
  a blanket label, with every other budget at its default:

  | domain (actual bound) | entry | at-limit / first-over evidence | fixed name |
  |---|---|---|---|
  | I total work (`max_total_work_units`) | public I | three capped OK runs: the last I charge before each constructor (root-entry fence, first post-entry reservation, result construction) crosses with zero NEW constructions at that stage | `total_work_units_over_bound` |
  | I diagnostics (`max_diagnostics`) | public I | 65 invalid items fenced before item coercion; the at-limit 64 reaches parsing | fixed preflight refusal |
  | G total (inherited admission work) | admission stage inside I | at-limit OK, one-below refused with I headroom intact; the domain-cost observer measures the split at runtime (I outer = G subtree + H domain + strictly positive NEW-I glue) | `work_units_over_bound` |
  | F subtree (inherited graph work) | F stage | unchanged public law: inherited F regressions cited, not relabeled as direct I evidence | `graph_work_units_over_bound` |
  | H op (inherited H outer) | H phase | unchanged public law: inherited H regressions cited | `work_units_over_bound` |
  | D-local (inherited D-transition work) | public-I first-over STRUCTURALLY UNREACHABLE (the cap is identity-bound into the history key; every accepted D transition revalidates the FINAL state under the same cap) | closed at the actual D-validator stage surface: the lenient larger shared outer is charged, at-limit validates, one-below refuses; the public identity control refuses foreign scope | `work_units_over_bound` (causal-history name) |
  | E x6 (inherited `CurrentnessBounds`) | E derivation inside I | each domain at-limit OK / one-below exact name; a sub-floor public first-over is closed at the bounded constructor surface | exact `currentness_*` names |
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
- J01: EVERY retained file entry binds the SELECTED governing
  root digest at BOTH its actual governing field and its ACTUAL
  key record's governing field, re-checked at the admission
  boundary AND the result boundary (a model_copy-bypassed nested
  admission cannot escape the entry law by construction alone); a
  genuine EARLIER entry for the same nonroot source (old
  governing digest, old canonical key) spliced back into the
  current admission with its reverse-index row remapped is
  refused at both boundaries even though its namespace and
  retained proof are genuine and unchanged.
- J02: the ACTUAL reverse member index equals EXACTLY the
  represented member-path -> ALL-and-ONLY admitted-content-keys
  relation: rows sorted by distinct path, every represented
  member path covered exactly once, no unrepresented path named,
  each row holding exactly the admitted content keys in
  canonical order, the ACTUAL admission scoped key on every row,
  and the root flags equal exactly the root path -- all
  re-derived from the ACTUAL entry key records at both the
  admission boundary and the result boundary. A legitimate SHARED
  member (one path admitted by two distinct proven bundles)
  keeps ONE row with the complete canonical key set.
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

- `tests/test_current_root_composition.py` (57 test definitions,
  218 cases): the durable ORIGINAL-API matrix over BOTH read
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
  with the public identity control, the six E domains under I,
  the graph/admission stage domains at the measured at-limit /
  first-over, the domain-cost observer split, and the zero-new-
  construction pre-charge sentinels at the three capped OK runs.
- The ROOT-executed independent probes (public vertical, the
  named I7 namespace/carried-version/joined-context controls, the
  I8 preflight/diagnostic/char-before-copy controls, the I9
  selected-root and preservation controls, the G-wrapper domain
  split, the H-namespace retention cap and the batch-domain
  positive) retain their EXACT recorded source versions and
  scopes: they are ROOT executions, not coding-executed
  repository tests, and are not relabeled as final-source broad
  tests.

# Nonroot currentness and overlap-overlay contract (objective 018, slice e)

`CURRENTNESS_CONTRACT_VERSION = "cache-currentness/v1"`.
`CURRENTNESS_POLICY_VERSION = "currentness-policy/v1"`.
`OPAQUE_GROUP_RECIPE_VERSION = "currentness-opaque-group/v1"`.

This contract binds the INERT nonroot currentness overlay slice
(`src/slaif_local_coding/constitution/bundles/`:
`currentness_models`, `currentness`, and the ONE public entry
`derive_currentness_overlay` plus the pure helpers
`opaque_group_identity` / `currentness_scope_key`). It takes an
ACTUAL accepted 018-d `CausalHistoryState` and its ACTUAL
`CausalHistoryNamespace` (plus explicit currentness bounds) and
derives, in ONE pure bounded operation, which NONROOT source facts
and ownership groups are CURRENT_KNOWN, CURRENT_OPAQUE, STALE,
CONTENT_CONFLICT or OWNERSHIP_AMBIGUITY, and indexes the overlapping
represented paths. It does NOT select current graph reachability or
admission, compile, inject, replace, or own RAM services. It is
delivered as inert code on PR 26 (which stays unmerged until the
whole numeric 018 is complete), IMPLEMENTED and PENDING strategic
acceptance at its bounded inert scope: like the accepted 017, 018-a,
018-b, 018-c and 018-d slices it is pure and never active in the
adapter runtime; no command string is executed and no
model/native/client/service facility is started. It earns the
C04/C05 currentness/overlap MECHANISM at its bounded scope only;
current graph reachability/admission integration, version-owned
ordinary-edge and group-certificate withdrawal, stale-injection
end-to-end acceptance and the explicit root-refresh
authority-lineage contract remain later mandatory same-018 work,
then 019 (RAM session ownership, capacity/backpressure,
single-flight, lifecycle), 020 (protected exact-original recovery
checkpoints and lazy restart rebuilding), 021 (pinned tokenizer and
typed bundle compiler), 022 (transactional source replacement and
endpoint integration), 023 (full-stack adversarial/lifecycle/
isolation/cancellation matrix) and 024 (bounded actual-model/
genuine-Codex qualification); nothing here is a v1 runtime,
compiler-hit, actual-receipt, wire or recovery claim.

## 1. Input, namespace revalidation and caller trust

- `derive_currentness_overlay(state, ns, bounds=None)` takes the
  ACTUAL retained 018-d state and its ACTUAL namespace. The input is
  the INTERNAL retained-history boundary, never a public supplied
  positive proof/snapshot/header authority: object construction is
  not authentication.
- Before ANY positive interpretation the ACTUAL namespace is
  revalidated: the SEVEN ACTUAL inherited version fields
  (admission_version, observation_version, graph_version,
  reference_version, proof_version, history_version and
  arguments_version) against the supported constants (a coherent
  UNSUPPORTED actual version refuses with
  `REFUSED_VERSION_CONFLICT`; the currentness contract/policy/
  recipe are this slice's three derived-output versions, not
  inherited namespace fields); the ACTUAL history-namespace field
  shape through a FRESH dict through the real validators (lineage,
  keys, bounds, versions); the underlying admission namespace
  through a fresh bounded actual-field validation; BOTH admission
  keys and BOTH history scope keys recomputed from the actual
  fields and compared (borrowed-key equality, `model_copy`/
  `model_construct` instances carry no authority); the ACTUAL
  history bounds revalidated fresh; the workspace rechecked
  against the evidenced canonical scope. Unsupported coherent
  versions, foreign scope and malformed state refuse BEFORE any
  interpretation.
- The early fences are O(1) in the historical state: they do not
  copy or scan hostile overbound states. Every later validation
  scan is explicitly charged on the shared derivation ledger
  (section 7); bounded charged scans in the normal path are
  legitimate, and the no-old-state-scan law applies to the early
  gates and refusal construction, never as a ban on charged
  scans.
- ALL THREE new version identities are bound into the output scope
  identity (`currentness_scope_key`), which additionally hashes
  the ACTUAL validated history key of the retained state (the key
  function binds the supplied validated key; it cannot recompute
  the actual history fields, which the derivation revalidates
  first), the workspace, the policy version and every one of the
  six bounds; a caller tag cannot establish identity. The output
  overlay records the EXACT history scope and revision it
  describes; it is not a fresh persistent revision or clock.

## 2. Identity separation

- The semantic source/content key (the accepted 018-c structural
  key), the completed read occurrence identity (one retained
  verbatim original proof with its FIRST original provenance) and
  the local CAS revision stay distinct; this derived overlay is a
  fourth identity, never conflated with any of them.
- An unchanged semantic source must not gain a new
  compiler-semantic key from new witnesses, unrelated observations
  or history revisions: unrelated observations leave the affected
  path record and the accepted 018-c content key byte-identical.
- The input history, proof bytes, original first provenance and DAG
  are unchanged on every outcome: the OK result carries the EXACT
  input state object and every refusal carries the exact input
  state with no partial overlay.

## 3. Nonroot path-frontier policy

- A claim comes only from a retained COMPLETE original proof and
  its actual represented normalized member occurrences and
  accepted ownership partition. Repeated operands are retained as
  evidence; width/distinct path is separate. Pending, truncated,
  unsupported or nonzero results are not claims. An empty COMPLETE
  file is a claim with its earned empty digest; it is never
  absence.
- For each represented NONROOT path the overlay retains the
  MAXIMAL completed-occurrence witnesses under the ACTUAL frozen
  partial order: a claim is dominated only by another occurrence
  representing that path with actual BEFORE evidence. No
  incomparable witness is ever dropped and siblings are never
  ordered by registration or arrival.
- Original complete but unissued history remains real UNANCHORED
  claims: an unissued observation adds NO temporal edge by itself;
  a conflicting new unanchored item introduces explicit ambiguity,
  never newest selection and never silent erasure. A known
  completed unanchored fact may LATER be named as a trusted
  frontier parent and is then BEFORE its descendant; the same
  known completed ID is SAME; distinct known UNCONNECTED events
  are INCOMPARABLE until later trusted facts establish edges;
  unknown or incomplete IDs are UNKNOWN (never a SAME shortcut).
  A later valid receipt can resolve chronology; the overlay
  rederives from the actual new DAG and never treats receipt
  arrival as chronology.
- Exact old-call replay (including shifted replay: the same
  original call/result at a shifted position) cannot change the
  frontier. A genuinely descendant new occurrence with the old
  bytes establishes a revert; old equal content may become usable
  again only through the genuine new witness, and no replay is
  reclassified as a fresh witness.
- Equality never manufactures an edge: after incomparable
  same-byte witnesses A1/A2, a changed A3 that descends only from
  A1 remains incomparable with A2 and cannot erase A2. ALL maximal
  witnesses are retained even when their content agrees.
- Known member versions use ONLY earned individual
  hashes/ownership from the accepted proof: a whole-bundle hash is
  never each member's hash and no byte splicing occurs. All
  maximal individually-known claims with ONE exact hash permit
  known-current content while retaining every witness; different
  known hashes yield explicit known-content conflict.
- The ROOT is the immutable accepted 018-d anchor: it is included
  only as unchanged scope context, never as a nonroot contender.
  A completed read of the root path emits no nonroot path record;
  a boundaryless group containing the root member carries rows
  for the nonroot members only. Different root bytes, workspaces
  and root-path refresh remain exactly refused by 018-d; there is
  no root exception here.

## 4. Ownership groups and the opaque-group recipe

- The group boundary class is derived EXACTLY like the accepted
  018-c `_file_entry`: PROVEN only for a segment that actually
  attributes exactly ONE member with its granted digest (group
  digest = that member digest); EVERY other form is BOUNDARYLESS
  with the exact group-bytes digest and unknown per-member
  attribution — including a multi-member segment inside a
  partitioned proof (the outer marker proves the segment boundary,
  never the internal member boundary). Whole-proof kind and outer
  markers are provenance, never boundary class. A singleton
  segment without a granted digest is a typed
  `STATE_MALFORMED` refusal.
- ONE versioned opaque-group equality recipe
  (`currentness-opaque-group/v1`): the sha256 of the
  domain-separated recipe-version encoding over the GROUP-LOCAL
  semantic ownership shape — the boundary class, the ORDERED
  normalized member occurrences (including repeats), the exact
  aggregate group-bytes digest and the actual per-member digest
  shape — plus the bound currentness policy, proof and observation
  version identities. The recipe binds NO principal/session
  namespace keys: namespace isolation comes from the validated
  input/output scope, and the group digest alone is not authority.
  Unrelated group bytes, full-proof kind and global proof
  coordinates are provenance, not false inequality: a standalone
  boundaryless `AB` and the same group isolated after a separate
  proven member carry EQUAL opaque identities. AB and BA are
  DISTINCT ordered group identities even when the aggregate bytes
  happen to match.
- Equal full opaque groups can support the SAME group content
  while retaining every witness, but never invent per-file hashes
  or a temporal edge. A single/equal opaque-group frontier is
  opaque-current, not individually-known. Distinct opaque groups
  overlapping a path, or known versus unattributed claims with no
  actual equality proof, yield ownership ambiguity — never proven
  byte inequality. A common directory never gives per-member
  ownership.

## 5. Candidate currentness, rows and overlap usability

- Per retained occurrence/group, each represented nonroot path
  carries a row computed against the group's OWN relevant claim:
  - a provably later known UNEQUAL version -> STALE with
    PROVEN_CHANGE; a provably later unknown or
    differently-partitioned ownership claim -> STALE with
    UNPROVEN_OWNERSHIP (conservative, never a false inequality);
  - an incomparable different known version ->
    KNOWN_CONTENT_CONFLICT; an incomparable unknown or
    differently-owned version -> OWNERSHIP_AMBIGUITY;
  - EVERY closed blocker that fired against distinct newer or
    incomparable witnesses is retained with its witness set: a
    CONTENT_CONFLICT-status row may carry BOTH
    KNOWN_CONTENT_CONFLICT and OWNERSHIP_AMBIGUITY at once (e.g.
    known A1, known A2 and opaque AB concurrent); stale reasons
    always force the STALE status by worst priority; an
    OWNERSHIP_AMBIGUITY-status row carries exactly
    OWNERSHIP_AMBIGUITY (the ambiguity status cannot carry the
    known-conflict priority, so ambiguity-status-with-known-
    conflict still refuses). There is no last-writer shortcut.
- The GLOBAL per-path record aggregates the MAXIMAL frontier only
  (an antichain; STALE never occurs at this level): all maximal
  claims known with the same single digest -> CURRENT_KNOWN with
  that digest; all maximal claims unattributed within the same
  single opaque identity -> CURRENT_OPAQUE with that identity;
  any two maximal claims both individually known with different
  digests (including repeated same-occurrence claims) ->
  CONTENT_CONFLICT; any known-versus-unattributed mix or
  different opaque identities -> OWNERSHIP_AMBIGUITY. Blocked
  paths assert no single current content (both content fields
  exact None; the witnesses' verbatim retained proofs carry the
  exact bytes). `witnesses` retain ALL maximal occurrence IDs
  (frontier evidence, not a last-writer selection) and
  `overlapping_occurrences` the full reverse path index
  (dominated witnesses included).
- For an older boundaryless `AB` followed by a descendant
  singleton `A`, the AB group's current usability is withdrawn
  even when A's actual bytes happen to match an unknown old
  member (UNPROVEN_OWNERSHIP); AB's exact historical bytes/key
  are retained and old AB replay cannot restore it. A genuinely
  descendant new AB may establish current group content again.
  For a boundary-proven AB whose A is individually known, a later
  equal-known A preserves AB's content currentness and a changed
  A withdraws it; no unsupported substring inference or splice.
- A stale group never stales an unrelated group; in a
  boundary-proven whole proof, component currentness is reported
  separately and the whole occurrence is usable only if all of
  its nonroot rows are current. This overlay does not itself
  admit isolated pieces or construct a new source; later
  graph/admission integration owns that decision under the old
  contract. Different current groups remain independent
  identities; partial proof groups stay independent with no
  spliced pseudo-source or invented per-file hashes.
- The reverse member-path index retains EVERY overlapping
  occurrence (the historical original proof/group facts are
  immutable); no source history is deleted and no old structural
  identity is mutated.

## 6. Relation law

- Chronology comes ONLY from the ACTUAL frozen parent evidence of
  the accepted 018-d DAG: only actual frozen parent edges
  establish temporal relations; receipt arrival, new call IDs,
  HTTP/arrival positions, equal or different digests, lexical
  order, session numbers and registration or revision numbers
  NEVER establish source freshness. The frozen frontiers supply
  partial-order evidence only — never a clock; no new clock or
  ordering source is introduced.
- `BEFORE` means the first argument is the OLDER occurrence (the
  relation cache is orientation-normalized so chronology never
  depends on lexical IDs or query order); the same known ID is
  SAME; distinct known unconnected events are INCOMPARABLE;
  unknown or incomplete IDs are UNKNOWN.
- Repeated public relation calls with fresh budgets do not
  satisfy the shared-work law; the derivation uses ONE shared
  charged traversal and cached reuse is a charged lookup, never a
  fresh walk.

## 7. Bounds and the shared work law

New defaults AND hard ceilings (stricter positive values are
supported; any wider direct construction is refused):

- `max_paths` 16384 — distinct represented NONROOT paths;
- `max_groups` 32768 — retained derived ownership-group facts;
- `max_witness_memberships` 65536 — emitted path/group/witness
  association rows;
- `max_relation_pairs` 65536 — actual attempted occurrence-pair
  comparisons, duplicates included before the memoization lookup;
- `max_work_units` 1048576 — ONE shared ledger over the ENTIRE
  derivation (state validation plus every charged scan);
- `max_diagnostics` 64 — TOTAL emitted closed-enum reason entries
  across all records.

The existing 14 history and the observation/proof/admission bound
sets retain their exact scope/units; no global-min
reinterpretation. The EXACT `max_witness_memberships` unit
formula: one per path-claim association (path <- occurrence group
claim), one per DISTINCT (path, occurrence) emitted into the
reverse path index AND into the frontier witnesses, one per
emitted group path row (group x nonroot path), and one per
DISTINCT (group, path, witness) blocker association — every
association charged BEFORE its retention. Work is charged BEFORE
each inspected input occurrence/member/ownership-piece, path/
group association, witness comparison, causal parent-edge visit
and emitted association; every actual repeated or unsupported
attempt reaching a stage counts. Raw lengths are preflighted
before copy/iteration/retention; no unbounded canonical dump or
uncharged quadratic precomputation. Three distinct charging
facts are named separately. (1) The dominance inner loop
charges one shared work unit per ACTUAL identity comparison
BEFORE the same-occurrence skip, so the N*(N-1) count of the
ONE-occurrence repeated-operand fixture is charged identity-
comparison WORK units (duplicates count), NOT max_relation_pairs
causal queries: the same-occurrence skip avoids the relation
query entirely. (2) A general multi-occurrence dominance scan
may BREAK EARLY as soon as one proven descendant dominates a
claim, before trying the remaining claims, so not every
comparison in a multi-occurrence path is always attempted.
(3) A relation query that IS attempted (differing occurrence
IDs) charges its relation-pair and work units BEFORE any
memoization lookup, and may then avoid its second ancestor
closure (the first already proves the relation) or resolve from
the memoized cache as a charged lookup, never a fresh walk.
Refusals happen before the crossing operation with no
silent truncation/eviction/partial currentness. These are derived
units, not token budgets or total process RSS.

## 8. Atomicity and typed refusal

Closed outcomes: `OK` carries the derived overlay and no
diagnostics; `REFUSED_FOREIGN_SCOPE`,
`REFUSED_VERSION_CONFLICT`, `REFUSED_STATE_MALFORMED` and
`REFUSED_OVER_BOUND` carry their closed limitation, the EXACT
input state object and NO partial overlay. A derivation never
advances any revision.

## 9. Privacy and purity

- The derivation performs no host IO on any public path (success,
  foreign-scope, malformed-state or resource refusal).
- Operational reprs and errors use the closed fixed vocabulary
  and never echo identity values, source text or private IDs
  (private values render as the fixed placeholder); unvalidated
  namespace data is never serialized in a warning-producing
  path before fresh validation rejects it.
- No credential-bearing wrapper, transport envelope or
  environment tail is read or retained; the overlay describes
  retained facts only.

## 10. Tests

- `tests/test_currentness.py` and
  `tests/test_currentness_models.py` are the named pure suites:
  original-API evidence built ONLY through the accepted 017
  observation and 018-d trusted registration APIs (legitimate
  root bootstraps and actual earned positive proof/byte/hash
  preconditions; both read endpoints, both modes), covering the
  version-chain revert and exact replay, unissued ambiguity and
  late receipts, initial forks and reversed registration,
  incomparable same-byte retention, the boundaryless
  AB->A / AB->AC / AB->A->newAB / old-replay laws, AB vs BA with
  equal aggregate bytes, repeated operand work charging, the
  complete-empty and nonzero/pending/truncated non-supersede
  laws, the standalone-vs-isolated opaque equivalence, delayed
  outstanding results and shifted replay, unrelated-B semantic
  stability, mixed simultaneous blockers, the root scope-context
  reads, the six operational bounds at-limit/one-over with
  pre-copy sentinels and the shared parent-edge traversal
  budget, foreign/malformed/unsupported version refusals, no-
  host-IO and input immutability.
- The independent ROOT probes at their recorded source hashes
  (S/reviews/018-e-*) are named-scope evidence, not substitutes
  for these durable tests and not whole-e acceptance.

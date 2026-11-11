# Root-region currentness contract (objective 018, slice q)

`ROOT_REGION_CURRENTNESS_CONTRACT_VERSION =
"cache-root-region-currentness/v1"`.
`ROOT_REGION_CURRENTNESS_POLICY_VERSION =
"root-region-currentness-policy/v1"`.

This contract binds the INERT pure root-currentness derivation
(`src/slaif_local_coding/constitution/bundles/`:
`root_region_currentness_models`, `root_region_currentness`, and
the public entry `derive_root_region_currentness`, plus the bounds
factory `RootRegionCurrentnessBounds`). It sits ABOVE the accepted
018-p root-region producer
(`docs/CACHE-ROOT-REGION-LINEAGE-CONTRACT.md`) as a QUERY: it
derives, from the ACTUAL retained P state and namespace in the
SAME bounded operation, whether a known authoritative root is
CURRENTLY usable — and it refuses to treat a known authoritative
root as currently usable after a trusted complete root-bearing
observation whose governing root cannot be established under P
source policy. It mints no new root authority, changes no P
selection law, never advances a revision and carries no CAS input,
clock or new persistent state. The 018-p producer slice is
ACCEPTED at its bounded inert producer scope WITH PROCESS
QUALIFICATIONS (strategic decision
`S/reviews/018-p-decision.md`, preserving every recorded
qualification, including the failed detached next-control
attempt after the immutable P report and its verified
foreground replacement); this 018-q slice is IMPLEMENTED and
PENDING
strategic review at its bounded inert scope. Neither slice closes
anything end to end: the SAME-018 CONSUMER round must consume the
legitimate new region state into the actual graph/admission, and
whole 018 (plus 019-024) remains open and mandatory. Like the
accepted 017 slice and the accepted bounded 018 slices it is pure,
bounded and never active in the adapter runtime: no command string
is executed, no model/native/client/service facility is started,
and no implementation/release/whole-018 status is upgraded by
inherited green checks. The actual P core is unchanged at the
accepted P head (`root_region_lineage.py` /
`root_region_lineage_models.py` hashes recorded in the 018-p
report); all existing H/O/I/P public signatures, defaults,
schemas, version tags, recipe bytes and behavior remain intact.

## 1. Namespace, scope key and caller trust

- The input is the ACTUAL `RootRegionLineageState` and the ACTUAL
  `RootRegionLineageNamespace` (the original namespace fields,
  bounds and versions bind the derivation scope; a stale or
  forged key is never trusted), plus an optional Q bounds
  override. Q is a query: there is NO CAS input, NO new revision
  and NO clock.
- The stable scope key is EXACTLY
  `root_region_currentness_scope_key(state.lineage_key, Q
  contract, Q policy, actual Q bounds)`, recomputed on every
  construction under closed actual-field fences. It binds the
  ACTUAL P lineage key (which itself, through the real P/D/C
  factories, binds the inherited identity/model/workspace/version/
  bound fields), the Q contract/policy tags and the actual Q
  bounds — and it does NOT bind the carried state revision: the
  revision is a separate carried derivation identity, never a
  clock and never part of the stable namespace key (a GENUINE
  accepted transition that advances the carried revision keeps
  the SAME scope key; a forged revision is refused by the actual
  P integrity law while the scope key is unchanged).
- The O(1) boundary fences run FIRST: a non-P object or a
  PARTIAL actual state instance (a field never set at the exact
  closed top-level/wrapped-D dereference set) fails with a FIXED
  private `ValueError` before any result construction, consistent
  with the explicit P/old-I boundaries; a PARTIAL actual
  namespace instance is a typed foreign-scope refusal in the
  default domain, never an internal error. A shape-VALID state is
  NOT a ValueError: it flows to the actual P validation integrity
  law (e.g. a default-filled empty `root_facts` over the
  anchor-bearing D state is a typed refusal carried on the actual
  P problem channel).
- Object construction is not authentication. Caller-supplied
  positive Q snapshots are not authority: a downstream consumer
  MUST derive currentness from the actual state in the same
  bounded operation.

## 2. Pure API and result law

- `derive_root_region_currentness(state, ns, bounds=None)`
  returns `RootRegionCurrentnessResult`: the outcome, the state,
  the carried P selection, the carried P validation problem, the
  usable selected source digest, the uncertainty witnesses, the
  closed diagnostics, the effective bounds, the lineage key, the
  scope key and the carried revision.
- The result retains the EXACT input P state by `InstanceOf`
  reference on EVERY outcome (accepted, non-ready and refused),
  with its actual revision and lineage key. The query never
  advances a revision, never mints a root authority fact, never
  copies source, and a refused result publishes no partial
  positive output.
- `p_selection` is `None` until the ACTUAL same-run P selection
  is computed, and it is RETAINED afterwards on every later
  outcome (a Q refusal after P completed carries the actual P
  result, including `root_content_conflict` and
  `no_selected_root`); when the actual P validation refused
  BEFORE selection, the exact actual P validation reason is
  carried on `p_validation_problem` with `p_selection` still
  `None` — a P selection is never fabricated.
- Outcomes: `ready` (the actual P selection is OK and no
  undominated maximal uncertainty survives),
  `root_currentness_unproven` (no usable selected source),
  `root_authority_conflict` (no usable selected source) and
  `refused` with the closed diagnostics `foreign_scope` /
  `version_unsupported` /
  `malformed_binding` / `work_units_over_bound`. Every non-ready
  result forbids a ready graph/admission or bootstrap fallback;
  an authority selection carried as evidence on a non-ready
  result MUST NOT be labelled usable. Q is root-only currentness,
  not full bundle/runtime readiness.

## 3. Closed evidence and exclusion table

Every uncertainty candidate requires ALL of: the actual retained
COMPLETED original read; the actual complete original owning
result; the matching trusted INTERNAL issuance; the anchored
original occurrence with frozen ancestry reaching the immutable
bootstrap; and at least one ACTUAL normalized requested member
equal to the effective root. These facts are derived from the
validated actual P/D records — never from stored caller authority
bits, mere request text, ID novelty, global output appearance,
digest equality, arrival or revision.

1. Authoritative supported P envelope/read/read_region facts are
   KNOWN governing-source witnesses under unchanged P law. A P
   read/region fact already represents that completed occurrence;
   no second uncertainty record is added for the same supported
   root source.
2. A qualifying complete root-bearing opaque group with unknown
   individual root ownership/content is uncertainty evidence
   (the `opaque_root_bearing_group` class). Every unknown per-file
   hash stays unknown; the whole aggregate identity is not root
   identity.
3. A qualifying complete root-bearing occurrence excluded by P
   root source-shape policy (including repeated root operands) is
   explicitly `unsupported_root_shape` uncertainty. Even when
   some individual member bytes are proven, the missing P
   authority fact is not minted and those values are not called
   unknown when actually known: this is lack of a usable
   supported governing witness, distinct from unknown ownership,
   not invented opaque hashing.
4. Unissued/unanchored observations contribute no
   uncertainty/currentness authority (row-4 retention). A later
   genuine issuance/receipt may qualify the SAME original
   retained occurrence under unchanged frozen ancestry — issuance
   alone does not anchor; the matching receipt is required — and
   no reread or new clock is invented.
5. Unsupported grammar and unpaired/missing/incomplete/pending/
   truncated/nonzero observations that do not establish an actual
   accepted COMPLETED source occurrence gain no new completion or
   uncertainty exception; their exact existing typed
   limitations/source retention are preserved. Requesting a root
   path alone cannot poison currentness.
6. Wrong normalized root path/workspace, nonroot-only opaque
   groups and unrelated read text do not become root uncertainty.
   A wrong actual namespace/state binding refuses before
   interpretation; a client file's identity is never inferred
   from host filesystem access or synthetic oracle constituent
   snapshots.

The table preserves P authority policy; it does not claim
generic read compatibility and never silently skips uncertain
complete root-bearing source evidence merely because its digest
was previously seen. Every row is tested through actual public
APIs with a supported positive control first, and unreachable
representations are qualified honestly.

## 4. Frozen partial-order currentness

- The COMBINED evidence frontier is built from the actual
  authoritative P facts and the eligible uncertainty occurrences
  on the SAME actual D state. Every edge comes ONLY from actual
  original frozen parent evidence: the bootstrap precedes
  qualified anchored descendants, and strict ancestry alone
  dominates. Arrival, registration order, call-ID order, HTTP
  position, revision and content equality NEVER add edges. All
  equal/incomparable maximal originals are retained in canonical
  deterministic metadata order.
- An uncertainty ancestor dominated by a genuinely later
  supported authoritative root witness cannot displace it;
  dominated uncertainties are retained as witnesses on the
  ready result, never erased.
- A maximal uncertainty observation after or incomparable with a
  known root makes the known authority unusable: fixed
  `root_currentness_unproven`, no selected usable source, no
  ready graph/admission and no bootstrap fallback.
- Readiness follows the COMBINED maximal frontier, not whether
  the first canonical selected witness alone dominates every
  uncertainty: a single proven descendant-of-all is SUFFICIENT
  but NOT required — when compatible known maxima JOINTLY cover
  the branches (neither descending all), the frontier is ready
  with all original maxima, without any invented edge between
  the compatible maxima.
- Restoration: a genuinely NEW supported whole/region root
  occurrence descended from ALL unresolved maximal branches can
  restore readiness under ordinary P authority law (BOTH the P
  whole and region source forms qualify; a later supported known
  witness is never forced into singleton form). A child-of-one
  cannot erase another unresolved branch. A deliberately new
  old-bytes descendant may restore that version (a genuine
  revert); a historical replay and a delayed receipt never roll
  back or cause permanent poisoning.
- Known authoritative differing-root conflict (incomparable
  maximal known roots) remains non-ready as
  `root_authority_conflict`; an uncertain observation cannot
  resolve it merely by dominating known facts without a proven
  source.

## 5. Refusal precedence

Explicit and tested, in ACTUAL order: (1) the STATE O(1) shape
fence — a malformed non-P state object fails with the fixed
private `ValueError` before any result construction; (2) the
NAMESPACE O(1) boundary — a partial actual namespace instance is
a typed `foreign_scope` refusal in the default domain, never an
internal error; (3) the Q BOUNDS validation — an optional
override that is a raw dictionary, a MALFORMED model_copy
mutation or a wider-than-hard value refuses `malformed_binding`
in the default domain BEFORE any serializer visit, while a valid
stricter copy is accepted into an equivalent effective value and
the absent override runs the default domain (the usable input is
never partially trusted); (4) the ONE Q outer is established at
the effective total (its bounded base charge included); (5) the
LINEAGE/History scope fences — the state's actual lineage key
versus the namespace lineage key and the wrapped D history key
versus the namespace history key refuse `foreign_scope` (a
stale or forged key is not trusted); (6) the SUPPORTED-VERSION
fence — the actual namespace version pairs versus the supported
pairs refuse `version_unsupported` (scope precedes version: a
stale-key version case passes the scope fences and fails the
version fence, a coherent rekeyed unsupported namespace over the
genuine state fails scope first, and a fully coherent rekeyed
namespace AND state still fail the version fence — scope
identity alone is not version support); (7) the ACTUAL
independent-P NAMESPACE reservation/revalidation phase, run
under the ACTUAL independent P domain (section 6) — the
charged reservation (a P-domain crossing is the typed
`work_units_over_bound` refusal) and the charged full namespace
revalidation (a forged/mutated key pair refuses `foreign_scope`);
(8) the ACTUAL P validation of the state under the same budget,
whose exact problem is carried on `p_validation_problem` when it
refuses before selection (the actual D-only validation shortcut
is not taken); (9) the ACTUAL P authority selection, whose
refusal/conflict/no-root results map BEFORE any uncertainty
assessment — each mapped early result precharges its OWN bounded
result construction (the carried actual P selection's witness
facts included) before it is built, and on those mapped early
results the uncertainty inventory is NOT computed (the actual P
result is retained; no selection is invented); (10) the charged
uncertainty/currentness assessment before ready interpretation.
P selection's fixed unproven-source limitations are preserved as
separate evidence; an unissued fact is never silently turned
into a currentness blocker, and a malformed state never becomes
an honest no-root/uncertainty result.

## 6. ONE Q outer and the ACTUAL independent P domain

- ONE Q outer covers the ENTIRE operation: the O(1) fences, the
  namespace/key reservations, the ACTUAL P validation/selection,
  the evidence inventory, owner/issuance membership, parent
  maps/ancestry, maxima/dominance, canonical sorting/dedup and
  the final result/model construction. The ACTUAL P phase
  retains its INDEPENDENT root-lineage work ceiling (the actual
  inherited `ns.root_lineage_bounds`), and the D/B-local
  domains stay independent beneath it.
- The P phase runs through the accepted private adapter
  composition: the ACTUAL P-domain ledger (independent ceiling)
  coupled unit-for-unit into the ONE Q total. A P-domain
  crossing refuses with the P fixed over-bound name WITHOUT
  charging the Q total for the crossing unit; a Q-total crossing
  raises the fixed private overflow. There is NO second public
  full-P call with a new ledger, NO pre-reserved P ceiling eaten
  from the Q total, and the Q total is NOT a global minimum or
  reset budget.
- The measured discriminator (n=40 eligible-opaque-branch
  fixture, fully public P production, BOTH admission modes): the
  strict public-P-built P ceiling is the per-operation producer
  maximum 11379, the actual P phase of the derivation is 7943
  units, and the full Q work is 12335 units (gap 956). At the
  DEFAULT Q total the derivation is READY with all 40 original
  dominated witnesses retained by reference; with the Q total set
  to the measured P ceiling (11379) the typed over-bound refusal
  lands in the Q phase AFTER the actual P selection completed
  (the actual P result is retained). A single shared
  min(P ceiling, Q total) budget cannot pass this shape.
- P-first-over (the inherited P ceiling crossing while the Q
  total is untouched) is NOT attained by the 40-branch public
  production sequence (the producer maximum exceeds the P phase,
  so no producible namespace ceiling falls below the P phase);
  it is NOT claimed universally unreachable. The charging-
  adapter mechanism is exercised directly (P crossing reports
  the fixed over-bound without charging the Q total for the
  crossing unit; the Q total stays intact).
- Precharge-before-work: the closed O(1) collection/scalar
  gates precede any iteration, set, sort or serialization
  work; EVERY candidate attempt counts before dedup, not
  merely each retained distinct record; membership width,
  ancestry traversal, sorting/union comparisons and record
  construction (including the per-eligible-witness precharge
  immediately before the witness object is constructed) are
  charged BEFORE the work they bound; source byte/character
  preflights precede any owned slice, encode, hash or copy —
  currentness normally needs metadata only and never walks
  full original source per witness (the same-run validated
  proof/metadata is reused). A crossing raises the fixed
  private overflow (or the P fixed over-bound report in the P
  phase) BEFORE the crossing operation runs.
- The ACTUAL inherited collection law beneath the region
  operations is distinct from cumulative caps: the per-batch
  `max_requests` count gate fires BEFORE any element validation
  (two separate one-request observations at the bound are each
  legal and both retained; the crossing two-request batch
  refuses the exact mapped bound before the deliberately
  malformed second element), and the retention `max_occurrences`
  first-over refuses the exact mapped bound with the ACTUAL
  refused D transition retained (bound precedence before a bad
  element applies at the retention gate as well).

## 7. Bounds and the closed collection ceilings

- `RootRegionCurrentnessBounds`: `max_total_work_units` 1048576
  and `max_diagnostics` 64, each DEFAULT AND HARD; stricter
  positive values are legal (valid stricter model copies are
  accepted into an equivalent effective value under the derived
  key — value equality, not unpromised input-bound identity), and
  a MALFORMED model_copy-mutated bound or a raw override
  dictionary refuses with the fixed `malformed_binding`
  diagnostic BEFORE any serializer visit. The closed two-bound
  shape fence fails fast BEFORE any cap comparison, enum, set,
  sort or serialization work.
- The owned uncertainty inventories are bounded by the ACTUAL
  inherited D `max_occurrences` (4096 default/hard); known facts
  retain the ACTUAL P root-fact caps; the frontier may
  additionally contain the one bootstrap witness — D 4096 plus
  its anchor is not accidentally capped at 4096, and metadata is
  never counted as logical root source bytes. No source
  copy/cache/storage/RSS/token limit is introduced; currentness
  normally needs metadata only and must not walk full original
  source per witness (the same-run validated proof/metadata is
  reused).
- The public first-over of the two constructor-level
  collection ceilings is UNREACHABLE through the charged
  kernel for two separate reasons, qualified honestly (not
  "dedup alone"): (a) more than 4096 uncertainty witnesses
  cannot be retained because the ACTUAL inherited D
  collection and work domains (`max_occurrences` and the
  per-operation work bounds) bound the retained occurrence
  population below the Q witness ceiling; and (b) more
  than 64 OWN Q diagnostics cannot be emitted because a
  public Q derivation emits at most ONE own fixed
  diagnostic per outcome (the carried P selection
  limitations are a separate P evidence channel, not Q
  diagnostics). The constructor fences remain the closed
  intrinsic law before any dump/serialization visit, and
  the model-level actual-bounds cap gate fires before any
  nested diagnostics element is visited.
- Measured boundary controls (no hardcoded caps): the full-Q
  work boundary with ACTUAL eligible dominated uncertainty (the
  n=2 sibling-opaque + descendant-of-all fixture accepts the
  entire derivation at the exact measured cap with both original
  witnesses in canonical order, and refuses one unit below
  retaining the actual P selection); the witness pre-construction
  window (the per-eligible-witness precharge is a genuine
  separately measured crossing: one unit below it the typed
  refusal lands BEFORE any witness construction with zero
  constructor entries and the actual P selection retained, at it
  the construction is reached and the later result-construction
  work still crosses, and at the full accepted cap the single
  original witness completes a genuine positive — measured with
  a real-class `__init__` counting wrapper that preserves class
  identity, with no zero-allocation claim about other
  construction); the zero-eligible-witness full-operation cap
  (the crossing lands after the P phase in the charged
  assessment/result construction).

## 8. Actual field/owner joins and identity law

- An uncertainty witness retains the ACTUAL completed original
  occurrence and the complete original owning result record by
  bounded immutable `InstanceOf` reference (the original
  coordinates, never copied source), plus the closed metadata
  (occurrence/call identity, endpoint, uncertainty class,
  whole-proof digest and byte length, root operand count). The
  CHARGED derivation verifies the state membership and
  owner/issuance joins BEFORE positive use; the constructors
  enforce intrinsic closed shape/count/scalar/scope/result
  consistency law only — no authentication, and NO uncharged
  full-proof walk is added to a constructor (the closed O(1)
  actual `BundleProof`/required-metadata shape fence precedes any
  dereference with a fixed private validation error).
- S1 fact re-derivation law: the issued/authority flags are
  re-derived after every accepted P transition, so a fact/
  occurrence container is NOT promised object identity across P
  transitions that rederive flags; what IS promised is the
  ORIGINAL read/proof/occurrence/owner reference within the
  final retained state (the final witness is the final retained
  occurrence, the original proof and anchor identity are
  retained, and the witness's owning result record is the actual
  complete record of the same state).
- Canonical deterministic order is `(uncertainty class,
  occurrence_id)`; the query is pure and idempotent (fresh
  result objects with identical canonical serialization — pure
  data evidence, not a wire-byte proof).
- The operational `str`/`repr` of the result and every witness
  is a FIXED non-echoing rendering: nested occurrence/owner
  objects are never formatted (fixed placeholders and metadata
  only).

## 9. Privacy and purity

- Operational representations stay fixed non-echoing: the
  distinct ROOT body canary, the opaque body canary, a DISTINCT
  known NONROOT source canary, the marker, the distinct call ID
  and the identity/model canaries are all absent from every Q
  str/repr surface (result, witness, diagnostics, carried P
  selection). The fixed malformed-input operational exception
  carries no canary in str/repr — including when the malformed
  input is a REAL canary-bearing state with an actual O1 field
  malformed. These canaries are known-synthetic source/ID
  evidence: they prove the tested representation surface on the
  tested paths, NOT a blanket no-secrets claim about untested
  surfaces, and no real credential/customer/private-corpus
  exposure is claimed or observed in this slice.
- No host IO anywhere on the Q public surface: after
  fixture/import setup, the closed 24-facility filesystem/
  socket/process trap covers the factory, bootstrap, issuance,
  observation (with the ACTUAL prebuilt request object passed to
  the public operation), receipt, validation, selection and the
  Q derivation over `ready` / `root_currentness_unproven` /
  `root_authority_conflict` (actual public P conflict) /
  `refused` (foreign scope, over-bound, version, malformed
  bounds and actual P validation problem) and the malformed-
  state error, on BOTH read endpoints and BOTH admission modes;
  the original request payloads' canonical serialization is
  unchanged afterwards (pure data evidence, not a wire-byte
  proof).

## 10. Tests

- `tests/test_root_region_currentness.py` (170 cases): the
  durable ORIGINAL-API matrix over BOTH read endpoints and BOTH
  admission modes on the SAME legitimate state earned through
  the actual public P APIs — A the four-case audit scenario with
  original bootstrap/proof/occurrence/owner/frozen-link identity
  and the unchanged P selection contract; B the combined-
  frontier matrix (dominance, joint coverage of compatible
  maxima, child-of-one blocked, the delayed sibling tool result
  after a known child, opposite arrival, forward/reversed two-
  request permutations, replay and equal-byte uncertainty,
  singleton AND mixed-region descendant-of-all restoration
  including the genuine old-bytes revert); C the closed
  evidence-table exclusions with supported positives first
  (including the row-4 activation on the opaque path: unissued
  observation, issuance alone does not anchor, the matching
  receipt activates the SAME retained occurrence); D the
  malformed/forged/coherent-rekey gates (partial actual
  state/namespace O(1) fences, scope-before-version precedence,
  stale copied keys, the 13 public forge joins each preceded by
  the explicit Q positive on the same good fixture, and the Q
  bounds gates); E the work boundaries (the zero-eligible-
  witness full-operation cap, the measured n=40 ACTUAL
  independent-P-domain discriminator with the adapter-level P-
  crossing mechanism, the full-Q cap with eligible dominated
  uncertainty, the witness pre-construction sentinel, the
  inherited per-batch and retention-count domains, the post-
  selection Q overflow and the constructor-level collection
  ceilings); F the invariants (idempotent query and stable scope
  key versus the carried revision with a GENUINE accepted
  transition, the privacy canaries with the operational-
  exception and distinct-nonroot-source surfaces, and the closed
  host-IO purity surface with the actual public conflict /
  version / malformed-bounds / P-validation outcomes and the
  actual prebuilt request).
- The existing H/O/I/P test suites are unchanged and passing;
  the actual P core hashes are unchanged at the accepted P head;
  no Q graph/admission/runtime readiness is claimed.

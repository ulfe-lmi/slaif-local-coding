# Bundle-proof bridge contract (objective 018, slice b)

`BUNDLE_PROOF_CONTRACT_VERSION = "cache-bundle-proof/v1"`.

This contract binds the INERT bundle-proof bridge
(`src/slaif_local_coding/constitution/bundles/`:
`bundle_proof_models`, `bundle_proof`, and the public entry
`observe_bundle_proof` / `observe_bundle_proofs`). It composes the
accepted 017 observation (re-derived under the namespace's ACTUAL
effective `ObservationBounds`) with the single evidenced
root/workspace binding (the 018-a law) and bridge-owned cumulative
source/proof ledgers, earning immutable SELF-CONTAINED whole-bundle
source proofs. The bridge is pure, bounded and never active in the
adapter runtime; no command string is executed and no
model/native/client/service facility is started. Lean/greedy
admission, overlap/replay invalidation, RAM ownership and recovery
remain later 018 stages and are NOT RUN; nothing here is a v1 runtime
claim.

## 1. Namespace caller trust (R1/R2, 018-a pattern)

- `make_bundle_proof_namespace(identity, *, model_identity,
  config_fingerprint, workspace, bounds=None, graph_bounds=None,
  observation_bounds=None)` takes an already-verified
  `RequestIdentity` from the existing trusted ingress
  (`gateway_identity.verify_signed_identity`) or a validated
  standalone configuration. Object construction is not itself
  authentication; the factory validates shapes only and raises plain
  `ValueError` with fixed messages that never echo the offending
  value. No external header, caller field or payload value can assert
  a scope.
- The ACTUAL effective bound sets are all bound into the pre-root
  `namespace_key`: the NEW proof bounds (`BundleProofBounds`), the
  ACTUAL effective `GraphBounds` (batch/path/source budgets) and the
  ACTUAL effective `ObservationBounds` (the 017 ceilings the
  re-observation pass and the command reparse run under), together
  with the three versions. A bare caller fingerprint cannot hide a
  different effective configuration; narrower actual bounds cannot
  hide behind an opaque tag.
- `namespace_key` / `scoped_key` are recomputed from the actual
  identity/config/versions/bounds/workspace on every construction
  (factory and direct model construction); a mismatched or forged key
  pair is refused. `scoped_key = sha256(namespace_key + "\0" +
  workspace)`.
- The workspace is the evidenced root scope; noncanonical spellings
  (double slash, trailing slash, `.`/empty segments) are rejected
  consistently at every entry point, and the workspace byte length is
  checked against the ACTUAL configured graph `max_path_bytes`.

## 2. Root / workspace binding (the 018-a law)

- Root envelope recognition is the accepted 017 law: only a
  Responses `role="user"` `input_text` item whose text starts at
  character 0 with the exact versioned header is a root occurrence.
  A chat user/assistant/tool message NEVER establishes a root; chat
  evidence is bound by the legitimate Responses root of the SAME
  batch (mixed batches are one snapshot).
- The single authoritative root binds the whole batch: repeated
  byte- and scope-identical roots are idempotent; competing digests
  or scopes are `root_conflict` with fixed `COMPETING_ROOTS`; no root
  is `no_root`; an unproven or noncanonical workspace is
  `workspace_unproven`; an explicit path context disagreeing with the
  evidenced workspace is `root_conflict` with `WORKSPACE_MISMATCH` /
  `ROOT_CONTEXT_MISMATCH`.
- A conflicting root-path read (a tool read at the root path with
  different content) is a competing effective root: `root_conflict`
  with the fixed `COMPETING_ROOTS` reason and NO retained bundles
  (no reset/supersession; a tool read never establishes the root).
  Only an independently proven SINGLE-occurrence root-path member
  digest (the segment `member_digest` law: exactly one attributable
  occurrence; compared by normalized path against the established
  root digest) is compared — a boundaryless or repeated group never
  infers a root hash, a nested `AGENTS.md` is a different path, and
  a same-bytes root-path read is consistent.
- When no context is supplied, supported reads are re-observed under
  the derived root workspace (explicit workdir/mismatch rules
  preserved); the derived context never invents authority.

## 3. Candidates

- A read candidate is a 017 read with a proven wrapper output
  (`output_present` and a proven output span); a process candidate is
  a COMPLETE paired native process observation (global exit zero,
  every piece present, untruncated). Every SELECTED candidate —
  duplicates and unsupported candidates included — is counted in
  `candidates_inspected` BEFORE dedup or refusal, never skipped.
- Enumeration is deterministic: reads then processes, request order,
  occurrence order.

## 4. The two proven source forms

- WHOLE: a boundaryless 017-attributed region — the `single` /
  `loop` forms, or a COMPLETE plan — acquires the 017 `content_span`
  region, digest-bound against the 017 `bundle_digest`. A complete
  plan keeps its proven boundary markers; a fully-quoted empty echo
  (`echo ''`) at a prefix/suffix position earns a ONE-character (bare
  LF) marker fact — the only one-character fact that exists.
  These ANCHORED EXTERIOR marker facts sit outside the
  017-attributed region and are byte-verified against the plan
  literals; they are NOT bounded by `max_marker` (that bound
  scopes the NEW partition markers below, never the accepted 017
  anchored exterior proof, empty-exterior LF included).
- PARTITIONED: an incomplete plan (the accepted 017
  `OUTER_BOUNDARY_UNPROVEN` shape) is partitioned ONLY under the NEW
  finite unique-marker law: every statement is clean (no typed
  reasons) with a kind in {cat, cd, echo}; echo literals are present
  and nonempty and pairwise distinct; each marker's UTF-8 byte length
  INCLUDING the emitted LF is within `max_marker` (the bound scopes
  these NEW partition markers only — the accepted 017 anchored
  exterior facts remain governed by the accepted 017
  command/observation bounds rather than `max_marker`, WHOLE
  bullet); at least one cat
  statement exists; every represented member is resolved. Each
  marker literal + LF is located exactly once in the complete
  proven output (missing/duplicate/out-of-order/overlap are fixed
  typed refusals). The full output is split into ALL slots between
  proven markers and the ends; EVERY slot — empty or not — counts
  against `max_segments`. A slot owned by a cat run retains its
  slot bytes as ONE boundaryless segment (a group may contain A+B
  with unknown internal boundaries, never split); a slot WITHOUT a
  cat statement must be EMPTY (`SEGMENT_UNEXPLAINED` otherwise) and
  is omitted from the retained source segments and from
  `source_text`, while still counting against `max_segments`.
  Interior marker facts are strictly nonempty (the collector
  predicate, not the record shape, enforces it).
- `BundleProof.source_text` is the EXACT aggregate source — the
  ordered proven segment bytes concatenated — and the record
  invariants bind `source_char_length` / `source_byte_length` /
  `source_digest` to it: the proof is SELF-CONTAINED and never
  depends on caller payload survival. A bare digest or a metadata-only
  hash is not source proof.
- Requested versus proven-executed stay distinct:
  `requested_members` is the exact original command's requested
  occurrences (order preserved); `proven_executed` is the aligned
  resolved normalized paths proven executed (017 law for whole
  proofs; the bridge all-success law for partitioned proofs).
- The parser surface (`BundleSurface.READ` / `PROCESS`) names the 017
  observation surface only. The ORIGINAL API source-role
  classification is explicit and separate: `endpoint` plus
  `source_role` (closed: `FILE_TOOL_RESULT` — a file tool result is
  dependency candidate text, never root authority).
  `root_path` / `root_digest` are the EFFECTIVE ROOT-AUTHORITY
  BINDING that scopes the batch; they do not confer root authority on
  the bundle's own carrier.
- `BundlePiece` retains the complete original carrier: the exact
  half-open character span into the EXACT decoded JSON string that
  carried it (legacy: the single result carrier; native: one
  original process result carrier per piece, never an imaginary
  concatenated string), plus the ACTUAL exec/poll call association
  (`call_id` / `call_location` / `call_position` from the 017
  observation — never invented from IDs or detached join coordinates)
  and the exact numeric `result_position` (Responses: the result item
  index; Chat: the result (tool) message index, the call position is
  the assistant message index with the exact tool-call pointer;
  native pieces: their own per-piece positions). Provenance is never
  renumbered.
- `BundleSegment.member_digest` is nonempty ONLY when the segment
  owns exactly one attributable member occurrence (equal to the
  segment digest); a distinct-path width of one never earns it.
  `piece_spans` are absolute per-carrier sub-spans aligned with the
  bundle's pieces (`None` = no overlap; a zero-width touch keeps the
  real zero-width carrier span).

## 5. Preflight law (all charges before own copy)

Every inspected source body and owned reconstruction is measured and
accounted BEFORE any bridge-owned copy/retention:

- Source ledger (from the ACTUAL effective `GraphBounds`): the exact
  UTF-8 byte length of every body actually inspected — the root body
  (every occurrence, duplicates included), every read output body,
  every native piece reconstruction (the 017-proven cumulative exact
  total) — charged per body (`max_single_source_bytes`) and
  cumulatively (`max_total_inspected_source_bytes`).
- Marker-search ledger: the explicitly bounded searched window (the
  complete proven output window per marker literal) charged in UTF-8
  bytes, SHARED and CUMULATIVE over the whole snapshot; NEVER reset
  per marker/file/request.
- Member budget: the represented member OCCURRENCES (before
  distinct-slot dedup) charged from ALREADY-PARSED 017 member
  metadata BEFORE any output-carrier fetch (read path) or
  piece/body reconstruction (process path).
- Both ACTUAL path ceilings bound every normalized represented member
  reference BEFORE any member charge or source/proof copy (see
  section 6).

At-limit stays at-limit; the first over-bound is a fixed typed
refusal, never a post-fetch or post-allocation discard. ALL budget
bounds are SNAPSHOT-level refusals (one per bound, `over_bound`,
nothing retained): `BATCH_OVER_BOUND`, `BUNDLES_OVER_BOUND`,
`SOURCE_OVER_BOUND`, `TOTAL_SOURCE_OVER_BOUND`,
`MEMBERS_OVER_BOUND`, `SEGMENTS_OVER_BOUND`, `MARKER_OVER_BOUND`,
`MARKER_SEARCH_OVER_BOUND` — a snapshot-wide budget that is exhausted
stops ALL further candidate work (no unbounded find/search/copy
beyond the bound). A budget bound is never a candidate diagnostic.
Non-budget candidate refusals (plan/marker integrity, consistency,
unresolved members) are candidate-level fixed diagnostics.

## 6. Path bound scope (order 83/84)

Both ACTUAL path ceilings are in UTF-8 bytes, never characters:

- The effective `GraphBounds.max_path_bytes` is the BRIDGE source
  scope: it bounds the namespace workspace AND every normalized
  represented member reference. A member exceeding it is the fixed
  typed `MEMBER_PATH_OVER_BOUND` non-acquisition (a candidate
  diagnostic): no source, digest or proof follows from an over-bound
  reference.
- The effective `ObservationBounds.max_path_bytes` is enforced by the
  accepted 017 normalization (the bridge reparse runs under the
  actual observation bounds and the bridge re-checks both ceilings
  explicitly). A member exceeding the observation ceiling stays the
  017 typed `PATH_TOO_LONG` refusal — surfaced as
  `MEMBER_UNRESOLVED` — never relabeled.

## 7. Same-occurrence consistency law (the seam)

- One call/result occurrence positive on BOTH surfaces (a native
  final without the token line is legacy-read positive AND native-
  process positive over the same carrier) is deduplicated ONLY when
  the full common proof signature agrees BEFORE retention: parent
  request index, parent call identity and location, result location
  and position, ordered normalized requested members, proven
  executed, command digest, source digest, endpoint, source role,
  root binding, proof version, per-piece (index, carrier location,
  span, byte length, call association, result position), per-segment
  (index, member positions, lengths, digests, piece spans) and
  per-marker (index, role, lengths, digest, piece spans). The parser
  surface is deliberately NOT compared (distinct surfaces are not a
  mismatch). Equal records survive once, attributed read-primary.
- A MISMATCHED positive proof (any common fact differing, including
  ownership, carrier intervals, call identity, member order or the
  root binding) is a typed `SEAM_CONFLICT`: the conflicting
  occurrence is retained NOWHERE — no source, no segments, no
  candidates — and the snapshot refuses ready
  (`version_conflict`). A negative or non-acquiring surface alone
  never negates an independently consistent positive proof.
- Same normalized path with different proven single-occurrence
  contents is a typed `SOURCE_CONFLICT`; the conflicting
  single-occurrence bundles are not retained. No version is chosen by
  order, call ID, hash or arrival.

## 8. Bounds and diagnostics

| Constant | Default | Unit / enforcement stage |
| --- | --- | --- |
| `max_bundles` | 128 | selected source candidates, cumulative (counted before dedup/refusal) |
| `max_members` | 1024 | represented member occurrences, cumulative (before distinct-slot dedup) |
| `max_segments` | 32 | source slots per proven bundle (ALL slots, empty included) |
| `max_marker` | 256 | UTF-8 bytes INCLUDING the emitted LF, one NEW partition marker literal (accepted 017 anchored exterior facts remain governed by the accepted 017 command/observation bounds rather than `max_marker`, section 4) |
| `max_marker_search` | 16,777,216 | UTF-8 bytes, cumulative searched windows, whole snapshot, never reset |
| `max_diagnostics` | 64 | total emitted fixed diagnostics on the final public snapshot |

The source budgets are the ACTUAL effective `GraphBounds`
(`max_requests` 128 batch requests; `max_single_source_bytes`
1,000,000 UTF-8 bytes per body; `max_total_inspected_source_bytes`
4,194,304 UTF-8 bytes per batch; `max_path_bytes` 4,096 UTF-8 bytes,
section 6), and the 017 ceilings are the ACTUAL effective
`ObservationBounds` (re-observation pass and command reparse).
Stricter bounds are always permitted; wider bounds are refused
beyond the declared ceilings. These are engineering bounds, never a
product effective-context `C` or a RAM ceiling guarantee.

The TOTAL emitted fixed diagnostics (snapshot conflicts plus
candidate diagnostics plus observation/global limitations, including
early refusals) is bounded by `max_diagnostics` at every public exit
and BEFORE retention/append; overflow is ONE fixed
`DIAGNOSTICS_FULL` refusal, never a truncated or unbounded reason
list (no silent truncation, no governance loss).

## 9. Outcomes and vocabulary

- Outcomes (fixed): `complete`, `no_root`, `workspace_unproven`,
  `root_conflict`, `version_conflict`, `over_bound`.
- `BundleLimitation` is the CLOSED fixed vocabulary for every emitted
  reason (root/workspace binding, version refusal, one per budget
  bound, plan/partition integrity, path bounds, consistency,
  diagnostics). Free-form strings and arbitrary text are rejected by
  validation and never echoed.
- A snapshot's `conflicts` / `diagnostics` /
  `observation_limitations` carry only that vocabulary.

## 10. Privacy

- Operational `str` / `repr` of every record never echo raw source
  content, marker literals or private call/result ID values (fixed
  placeholders; the observable empty no-ID state stays exact); the
  namespace identity values are suppressed in every operational
  representation. Counts, locations, spans, digests, fixed enums and
  scoped keys remain observable.
- Validation errors carry fixed messages without input values (the
  frozen base adds `hide_input_in_errors` to these records; the 017
  base class and the 018-a graph records are not modified).

## 11. Public API

```python
make_bundle_proof_namespace(identity, *, model_identity,
    config_fingerprint, workspace, bounds=None, graph_bounds=None,
    observation_bounds=None) -> BundleProofNamespace
observe_bundle_proof(payload, namespace, *, endpoint,
    context=None, bounds=None) -> BundleProofSnapshot
observe_bundle_proofs(requests, namespace, bounds=None)
    -> BundleProofSnapshot
```

`endpoint` is REQUIRED and explicit (`"responses"` | `"chat"`),
never inferred. The batch takes exactly one namespace (mixed-namespace
batches are structurally impossible) and one bounded request tuple;
`bounds`, when supplied, must equal the namespace's effective proof
bounds. `BundleProofSnapshot` is immutable: namespace, outcome,
effective root binding, bundles, conflicts, diagnostics,
observation limitations, request count, candidates inspected,
measured inspection totals. Inputs are never mutated; the public path
performs no host IO (purity is test-asserted); no command string is
executed.

## 12. Slice boundary

This b-slice earns: the typed namespace, the inert self-contained
whole-bundle source proof records, the bounded public composition over
the accepted 017 observation surfaces (whole and finite
unique-marker partition forms, the same-occurrence consistency law,
the source-conflict law), the bridge-owned preflight ledgers and
their fixed typed refusals, and their typed tests. It does NOT earn:
lean/greedy admission (G03–G05), entry/cache identity and replay/
overlap invalidation (C01/C02/C04–C06), RAM (C03/M0x), recovery,
compilation or replacement. Those remain the mandatory 018-c+ stages
at their NOT RUN/PENDING states in `docs/CACHE-REWORK-LEDGER.md`.
No automatic acceptance follows from this document or from green
focused tests: objective 017 is ACCEPTED at its bounded
pure-observation scope with process qualifications and merged to main
at ffaabf4b (017-am decision); 018-a is ACCEPTED at the bounded
inert graph-foundation scope with process qualifications
(strategic decision `reviews/018-a-decision.md`; PR 26 remains
unmerged until the rest of numeric 018 is complete); 018-b is
ACCEPTED AT THE BOUNDED INERT BUNDLE-PROOF SCOPE WITH PROCESS
QUALIFICATIONS (strategic decision `reviews/018-b-decision.md`); 018-c is
an implemented inert admission/identity slice pending strategic
acceptance (contract `docs/CACHE-BUNDLE-ADMISSION-CONTRACT.md`); the
remaining 018 stages (C04/C05/version/edge-withdrawal chronology and the
remaining G/C/S criteria) and 019–024 remain mandatory.

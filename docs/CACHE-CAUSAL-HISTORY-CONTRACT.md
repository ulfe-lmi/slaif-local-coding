# Causal-occurrence ledger contract (objective 018, slice d)

`CAUSAL_HISTORY_CONTRACT_VERSION = "cache-causal-history/v1"`.
`CAUSAL_ARGUMENTS_JSON_VERSION = "causal-arguments-json/v1"`.

This contract binds the INERT causal-occurrence-ledger slice
(`src/slaif_local_coding/constitution/bundles/`:
`causal_history_models`, `causal_history`, and the public entries
`observe_causal_history` / `register_issuance` / `register_receipt` /
`relation` / `make_causal_history_namespace`). It composes, over a
bounded ORIGINAL GraphRequest batch, the accepted 017 observation
(re-derived under the namespace's ACTUAL effective `ObservationBounds`),
the 018-a root/workspace binding law and the accepted 018-b
`_proof_collect` core (shared ledger state, no weaker observer) into
ONE pure causal-history state machine over the immutable
`CausalHistoryState`. This slice itself is IMPLEMENTED and PENDING
strategic acceptance: like 018-a/018-b/018-c (all ACCEPTED at their
bounded inert scopes with process qualifications) it is delivered as
inert code on PR 26, which stays unmerged until the whole numeric 018
is complete. It is pure, bounded and never active in the adapter
runtime; no command string is executed and no model/native/client/
service facility is started. It earns the C05 CAUSAL MECHANISM at its
bounded scope (replay does not roll state back; new observations are
distinguishable; causality only through frozen parent evidence) and
NOT the current-version/overlap/stale-injection acceptance:
current-version selection, overlap/replay invalidation of live
entries, version-owned ordinary-edge and group-certificate withdrawal
and current reachability/admission integration remain later mandatory
same-018 work, then 019 (RAM session ownership, capacity/backpressure,
single-flight, lifecycle), 020 (protected exact-original recovery
checkpoints and lazy restart rebuilding), 021 (pinned tokenizer and
typed bundle compiler), 022 (transactional source replacement and
endpoint integration), 023 (full-stack adversarial/lifecycle/
isolation/cancellation matrix) and 024 (bounded actual-model/
genuine-Codex qualification); nothing here is a v1 runtime,
compiler-hit, actual-receipt, wire or recovery claim.

## 1. Namespace, scope keys and caller trust

- `make_causal_history_namespace(admission_namespace, lineage_id, *,
  bounds=None)` takes the ACTUAL accepted 018-c
  `BundleAdmissionNamespace` plus one explicit opaque
  history-lineage ID. The factory revalidates the admission
  namespace's ACTUAL identity/config/bounds/versions fields AND its
  BOTH 64-hex keys (`namespace_key` and `scoped_key`), not only the
  opaque scoped key; every ACTUAL field (principal/session/
  repository/route, model identity, config fingerprint, workspace,
  mode, all five accepted versions, all four accepted bound sets) and
  the NEW `HistoryBounds` plus BOTH history versions are recomputed
  into the history scope keys. A caller tag cannot hide a different
  actual field, bound or version.
- Direct model construction recomputes the history keys from the
  actual fields and refuses (`ValueError`, fixed message) any forged,
  stale or borrowed key; a coherent direct construction with
  recomputed keys but an UNSUPPORTED actual policy/version is
  refused by every transition AND the relation query (fail closed,
  no false SAME/UNKNOWN over acquired source).
- Object construction is NOT authentication: this is an internal
  trusted boundary, never a public body/header authority path.
  Errors and operational reprs never expose identity values,
  source, markers or private IDs (fixed placeholder); no anonymous
  fallback and no cross-scope reuse. The history lineage is distinct
  from the future compiler/cache epoch: no source-chronology reset is
  baked into a future cache restart, and history revision/frontier/
  occurrence coordinates are not compiler-semantic inputs.

## 2. Canonical argument recipe (`causal-arguments-json/v1`)

- ONE bounded strict-JSON argument-fingerprint recipe, reusable by
  future 022 (future 022 will hash bounded completed emitted
  arguments using this SAME recipe; that wire mechanism is NOT
  earned here). Strict supported JSON object arguments: canonical
  sorted-key serialization, normal JSON whitespace/escape
  equivalence, EXACT string values (no shell-code normalization), no
  duplicate object keys, no nonfinite numbers, no malformed
  Unicode. Unsupported/over-bound arguments produce fixed
  limitations, never guessed matching.
- Bounds are enforced BEFORE unbounded parse/copy/hash work: input
  and canonical bytes are length-preflighted before any encode/copy,
  and the canonical walk charges each ACTUAL node/key visit (every
  value/container AND every object key counts 1; scalar depth 0)
  before visiting it; the per-argument running canonical-byte total
  AND the shared cumulative input+canonical ledger are both checked
  before the crossing copy/encode. Exhausted budget refuses before
  the crossing operation, never after.
- The fingerprint is the sha256 of the unambiguous domain-separated
  encoding `b"causal-arguments-json/v1\x00" + tool-name UTF-8 +
  b"\x00" + canonical-JSON bytes`; raw arguments are never retained.
  Hashing covers only the selected evidenced tool arguments/name/
  identity, never full requests/prompts/schemas/headers/
  credentials. The recipe is versioned in the encoding prefix.

## 3. Immutable state and records

- `CausalHistoryState` is immutable and binds: `history_key`,
  `revision` (0..2**63-1), the optional `RootAnchor` (the exact
  retained root text/digest, workspace, original envelope location
  and content/envelope spans — no transport envelope or
  environment tail), `issuances` (trusted issued-call bindings),
  `occurrences` (completed read occurrences), `results` (immutable
  per-call result fingerprint records, pending included) and
  `parent_links` (unique immediate parent edges). The EXACT empty
  prior state (no anchor) is representable; a typed bootstrap
  refusal never fabricates an anchor.
- An `IssuedCall` binds the exact call ID, endpoint family, tool
  name, canonical argument fingerprint and the FROZEN parent
  frontier (at least one known fact). A `CompletedReadOccurrence`
  binds the occurrence ID, call identity, the verbatim accepted
  018-b `BundleProof` and an `anchored` flag. A
  `ResultFingerprintRecord` binds the selected evidenced result
  facts plus the per-piece completion fact (the exact exit code, or
  None while the process piece is incomplete) — NEVER
  credential-bearing wrappers:
  per observed piece in causal order the exact original
  output-slice fact `(piece_index, char_length, byte_length,
  digest)` (sha256 of the EXACT original carrier-span bytes,
  measured/hashed before retention; lengths alone are NOT byte
  identity), each piece's ACTUAL producing call's observed
  immutable association (call ID + endpoint + tool name + canonical
  argument fingerprint), the immutable process-session association
  digest (raw session value never retained) and the FIRST original
  request provenance.
- Diagnostics are BOUNDED TRANSITION RESULT output (the final total
  cap applies per emitted transition); the state never carries a
  lifetime-growing diagnostic log. Replay leaves state and revision
  unchanged.

## 4. Original observation transition

- `observe_causal_history(requests, ns, state, expected_revision)`
  consumes a bounded ORIGINAL GraphRequest batch (legitimate
  effective Responses root; read evidence on EITHER read endpoint)
  plus the namespace. Caller-supplied proofs, digests, snapshots,
  flags or body receipt/trust fields are NEVER acquisition or
  anchoring: no header API exists in this pure stage, and a
  fully valid-looking body receipt field is inert payload. Only a
  subsequently paired COMPLETE original read proof creates a
  completed read occurrence.
- Bootstrap requires the legitimate effective Responses envelope.
  Rootless input plus the EXACT empty state refuses
  `REFUSED_NO_ROOT`. Later rootless observations may use the SAME
  lineage's previously acquired immutable root anchor/context (root
  identity object preserved, no synthetic root request inserted, no
  re-inspection); competing roots/workspaces and different
  root-path read bytes keep the existing explicit refusal. Same-
  root refresh/currentness requires a later explicit lineage
  contract; this slice grants no root-authority exception.
- The accepted 017 pass runs under the ACTUAL effective
  `ObservationBounds`; the 018-a root/workspace binding law applies
  exactly; the shared cumulative source/marker/member ledgers are
  created ONCE per transition and the accepted 018-b
  `_proof_collect` core runs over the collected facts with the SAME
  ledger state. The OLD per-path conflict policy is NOT applied:
  every distinct complete NONROOT occurrence is retained as
  evidence (including multiple versions of a nonroot file from
  different real calls); no graph edge, current version,
  compilation or cache admission is created merely by retaining an
  occurrence.
- Exact replays (including SHIFTED outer positions after history
  reduction) do not advance the revision or mutate retained
  evidence: the shifted replay is a pure `REPLAYED` no-op with the
  fixed `REPLAY_POSITION_SHIFTED` diagnostic and FIRST provenance
  intact. A new deliberate v1 after v2 requires a genuinely new
  completed occurrence with a valid descendant issuance; a new ID
  alone stays unanchored/incomparable. Missing/malformed call or
  result IDs stay typed non-acquiring under the accepted 017
  limitation vocabulary (no duplicate observer, no invented IDs).
- The native multi-piece law: a native read uses the INITIAL EXEC
  issuance frontier; later write_stdin polling never makes the
  underlying read newer (a later poll issued under a separate
  completed occurrence records its own frontier only). The native
  poll's producing call/result is bound to the ORIGINAL initial-
  EXEC owner derived from the genuine process association and the
  retained outer exec record: a completed poll never reassigns
  that owner even when the binding/body/status/session facts are
  all identical; same-owner replay and a fresh poll of a genuinely
  new exec with a reused numeric session remain legal (no session-
  number clock). Pending process pieces are tracked with immutable
  per-call/piece facts;
  a genuine 017-accepted poll extension may extend one pending
  record; mutated already-seen bytes, a changed session
  association, a same-ID changed result under a different
  producing call, or an equal-frame-count terminal-status change is
  a typed conflict preserving the EXACT prior state; an exact old
  pending prefix replay (while still running or after completion)
  is an idempotent no-op. A genuine 017 COMPLETE read of a
  genuinely empty source is retained as a completed read
  occurrence (empty source text, zero source bytes, exact empty
  sha256, complete result record) — a retained occurrence, NOT
  a cache admission: no mere occurrence creates a cache entry.
- Unsupported, partial, truncated or nonzero original frames stay
  unacquired through this composition with honest fixed
  limitations (the accepted 017 closed vocabularies) and no
  completed occurrence.

## 5. Trusted issuance and receipt

- `register_issuance(state, ns, call_id, endpoint, tool_name,
  arguments, parent_frontier, expected_revision)` records a bounded
  ISSUED-CALL fact: the exact binding (endpoint family, tool name,
  canonical argument fingerprint — raw arguments never retained)
  plus the frozen parent frontier of known completed
  occurrence/root-anchor facts for the SPECIFIC request that
  generated the call. These are synthetic trusted facts in this
  pure stage: public caller headers/body claims, a new request ID or
  a reflected adapter marker cannot mint them. Issuance is NOT
  source acquisition or execution success.
- A frontier is a bounded set of known facts, not current global
  state: redundant ancestors may remain; any bounded reduction may
  remove only PROVEN ancestors, never incomparable facts; a caller
  antichain is never assumed. The RAW supplied length is preflighted
  against `max_frontier_members` BEFORE any tuple conversion, copy
  or dedup; every member is charged before validation; unknown/
  malformed members refuse with fixed diagnostics. Duplicates are
  canonicalized only AFTER charging the actual attempts.
- A reused call ID with a different immutable binding (name,
  arguments, endpoint family) is a fixed conflict; an exact
  same-issued-call replay (same binding AND same frozen frontier,
  canonical argument equivalence) is a pure `REPLAYED` no-op; a
  changed frontier under the same call is a typed conflict bound to
  the original. An observed call ID is checked against its ACTUAL
  observed binding (endpoint/name/arguments/result facts, including
  pending) even when the call becomes read-ineligible; a unique
  unrelated unknown call remains harmless and non-acquiring.
- `register_receipt(state, ns, call_id, endpoint, tool_name,
  arguments, parent_frontier, expected_revision)` may register a
  trusted receipt AFTER an already observed unanchored complete
  occurrence ONLY if the immutable binding matches and the
  resulting DAG remains valid/acyclic. Unknown/foreign parents,
  cycles (including the self-member case) or conflicting receipts
  refuse atomically with fixed diagnostics and the EXACT prior
  state. There is no blanket late-receipt rebasing to the newest
  frontier, and receipt registration order/revision is never a
  clock.

## 6. Relation query

- `relation(state, ns, a, b)` is a pure bounded query over the
  frozen parent evidence with its OWN per-query work ledger (the
  shared transition ledger is never consulted). `same` holds only
  for the same KNOWN completed occurrence; unknown or incomplete
  IDs are `unknown` (even equal unknown IDs, never a shortcut to
  same); `before`/`after` hold ONLY through bounded transitive
  reachability over the actual frozen parent edges (every
  traversal charged); two known complete unconnected events are
  `incomparable` — siblings are never ordered from list,
  registration or receipt order, and a late older original result
  never becomes AFTER a newer occurrence merely from arrival.
  Foreign scope/lineage and unsupported actual versions refuse with
  an explicit fixed error BEFORE any positive interpretation (no
  false SAME/UNKNOWN); malformed endpoints raise the fixed error.

## 7. Atomic CAS, bounds and work

- Every transition takes an expected revision and the immutable
  prior state and returns the new state + fixed outcome evidence.
  The early scope/CAS/lineage/version fences and the refusal-record
  construction preserve the EXACT old state without scanning or
  copying an over-bound old state; normal kernel validation and
  the required state scans remain charged/bounded under the shared
  work ledger. Every refusal (content/issuance/result/receipt
  conflict, unknown parent, cycle, resource refusal included)
  preserves the EXACT old state. One accepted state-changing
  transition increments the revision exactly once; pure replay/query never does; a revision
  overflow refuses before mutation. No lock across IO, no mutable
  global registry.
- NEW history bounds (defaults AND hard ceilings; stricter values
  allowed, wider refused at construction): `max_issuances` 4096,
  `max_occurrences` 4096, `max_causal_links` 65536,
  `max_frontier_members` 1024 (raw input members BEFORE dedup),
  `max_observed_results` 8192, `max_retained_members` 16384 (before
  distinct-path width), `max_retained_pieces` 32768 (occurrence
  proof pieces plus incomplete result slices),
  `max_retained_source_bytes` 16777216 (root anchor once plus exact
  UTF-8 proof-source bytes per newly retained occurrence),
  `max_argument_bytes` 65536, `max_total_argument_bytes` 4194304
  (cumulative input+canonical per transition, before copies),
  `max_argument_nodes` 4096, `max_argument_depth` 32,
  `max_work_units` 65536 (shared PER-TRANSITION ledger),
  `max_diagnostics` 64 (TOTAL final closed-enum diagnostics across
  lists). Every actual value/version is bound into the scope keys.
  Accepted Graph/Observation/Proof/Admission bounds stay scoped and
  unchanged; no silent reinterpretation or global min across
  independent stage units.
- Work law: charge 1 BEFORE each canonical argument node/key visit,
  identity/result comparison attempt, frontier-member validation,
  parent-link/ancestry edge visit and retained proof member/piece
  association; actual duplicate/unsupported attempts reaching the
  stage count; no per-request/group reset within a transition;
  stop BEFORE the crossing operation. Preflight lengths and
  measured bytes before copies/retention; no quadratic full-state
  canonical dumps or unbounded ancestry scans hidden before the
  ledger; validated immutable facts are reused where legitimate.
  At-limit succeeds; the first crossing refuses atomically with a
  fixed typed resource reason and the EXACT prior state (resource
  exhaustion is never a content conflict).
- Retained caps are cumulative per lineage state, not a fresh
  allowance per batch. The retained piece units counted against
  `max_retained_pieces` are the occurrence proof pieces plus the
  INCOMPLETE result slices; complete-result metadata is not an
  additional piece/span unit and the other caps still apply. A
  pending record is REPLACED (not stacked) when the same call
  upgrades to complete in the SAME transition, so the final-state
  count is path-independent with no transient double charge. No
  TTL/LRU, capacity eviction or destructive deletion to make room.

## 8. Version refusal

- All ACTUAL version identities bound into the namespace (the NEW
  `cache-causal-history/v1` and `causal-arguments-json/v1` plus the
  ACTUAL accepted admission/observation/graph/reference-grammar/
  proof versions) are checked against the actual supported
  constants; an unsupported version — even in a COHERENT direct
  construction with recomputed keys — refuses the transition (or
  the query, with the fixed error) with no retained new facts.

## 9. Privacy and purity

- No host IO after fixture/import setup (no filesystem, socket or
  process facility) on ANY guarded normal or negative path,
  including the trusted registration/receipt/query operations and
  both read endpoints; the original payloads are byte-unchanged;
  operational `str`/`repr` of every namespace, state, record,
  transition and error is free of source text, private IDs,
  markers and identity values.

## 10. Tests

- `tests/test_causal_history_models.py`: the strict argument
  recipe (canonical whitespace/key-order/escape positives;
  duplicate-key/nonfinite/depth/node/byte/Unicode negatives;
  per-key and per-node charging with the shared transition work
  cap; before-copy byte preflight with isolated encode/construction
  sentinels; the stdlib-derived positive canonical oracle where
  recipe semantics match), the namespace/scope-key law (forged,
  stale, borrowed and coherent-unsupported-key refusals; factory
  AND direct construction revalidation; all 14 bounds wider-
  refused at construction), the record/validator integrity law
  (anchored vs unanchored semantics, complete frozen frontier
  validation, conflicting unissued facts, per-frontier preflight,
  charged iterative whole-DAG cycle check) and the long-chain
  scale control (shared-ledger validation within and over the
  work ceiling, matching frontier cycle refusal).
- `tests/test_causal_history.py`: the original-API surface over
  BOTH read endpoints and BOTH namespace modes with legitimate
  root and positive proof/byte preconditions — bootstrap and
  idempotent root, valid prior-root rootless read vs empty/
  forged/foreign-state refusal, body-spoofed receipt flags cannot
  anchor (a fully valid-looking body receipt is inert; the
  legitimate INTERNAL receipt over the same baseline anchors),
  CAS mismatch, same-batch and cross-batch exact replay (FIRST
  provenance; disjoint new/replayed lists) and SHIFTED completed
  replay, same-ID changed args/name/family/result conflicts,
  missing/malformed (including numeric) ID non-acquiring typed
  limitations, the version chain A-v1 -> trusted descendant
  A-v2 -> genuinely descendant NEW A-v1 with old-v1 replay no-op
  and unissued-ID incomparability, initial mixed nonroot
  versions, sibling forks, a late OLDER original result never
  AFTER from arrival, an unrelated B leaving A's retained proof
  byte-exact AND A's actual accepted 018-c content key
  unchanged, the native pending-process per-call byte/session/
  owner law (pending extension, poll-ID reuse, same-batch growth,
  old-prefix replay, same-length mutation, resegmentation,
  terminal-status change, cross-chain changed poll result/
  status/completion), trusted issuance/receipt laws (canonical
  replay, changed binding/frontier, observed-ID rebinding,
  frontier shape/known-fact, receipt mismatch/unknown parent/
  cycle, raw frontier pre-copy refusal, resource-path typed
  refusal), the native initial-EXEC frontier law (a later poll
  issued under a separate completed occurrence never orders the
  underlying read) and the native initial-EXEC owner immutability
  (completed-poll reassignment refused even with identical
  binding/body/status/session facts), the complete-empty source
  retained completed occurrence (NOT a cache admission), ALL 14
  new bounds at-limit/one-over with cumulative
  duplicate/result/member/source/frontier/work accounting and
  pre-copy/retention refusals, revision overflow, input/old-state
  immutability, no-host-IO/private-error purity over both
  endpoints and the trusted operations, and the durable 64-
  control inherited-limit matrix ported from the ROOT
  known-synthetic final-limit probe (actual applicable
  inherited ceilings through the NEW composition, both
  endpoints/modes; graph-node closure OUTSIDE this stage).
- The ROOT-executed independent original-API probes (pending /
  owner / causal-operations / inherited-limit / bootstrap /
  query-version / record-integrity / receipt-work control
  captures under S) pass at the RECORDED source hashes and named
  scopes of each capture, not as a single final-kernel result: the
  96 pending/native, 64 inherited-limit and 60 causal-operations
  controls share the current kernel source (the `5a684aeb`-family
  hash recorded in their captures), and the older named controls
  retain the source hashes of their own captures; the final
  implementation head and the qualified gates do not yet exist at
  drafting time, and no probe is rerun solely for labels. These
  are ROOT executions, not coding-executed repository tests; the
  durable repository suite above is the in-repo regression.

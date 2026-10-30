# Cache graph contract (objective 018, slice a: foundation)

`GRAPH_CONTRACT_VERSION = "cache-graph/v1"`;
`REFERENCE_GRAMMAR = "reference-grammar/v1"`.

This contract binds the INERT graph-foundation modules
(`src/slaif_local_coding/constitution/bundles/`: `graph_models`,
`references`, `graph`, `graph_observation`, and the public batch entry).
They are pure, bounded and never active in the adapter runtime.
Lean/greedy admission, overlap/replay invalidation, RAM ownership and
recovery remain later 018 stages and are NOT RUN; nothing here is a v1
runtime claim.

## 1. Namespace caller trust (R1/R2)

- `GraphNamespace` is an explicit trusted INTERNAL scope. Its identity
  components (principal, session, repository, route, model identity,
  config fingerprint, versions, bounds, workspace) MUST come from the
  existing trusted ingress: the factory accepts an already-verified
  `RequestIdentity` produced by signed ingress
  (`gateway_identity.verify_signed_identity`) or a validated standalone
  configuration. No external header, caller field or payload value can
  assert a scope. Object construction is not itself authentication: the
  factory validates shapes only and performs no authentication, and a
  caller that has not passed that boundary must not treat these records
  as trusted scope.
- A canonical bounded evidenced workspace is REQUIRED: the factory
  explicitly REJECTS noncanonical spellings (double slash, trailing
  slash, `.`/empty segments) and any workspace above the actual
  configured `max_path_bytes` bound (the model-level validator enforces
  the same on direct construction). There is no host resolution and no
  silent canonicalization.
- The effective bounds actually used are computed into the pre-root
  `namespace_key` in addition to the supplied opaque configuration
  fingerprint, so a bare caller tag cannot hide a different effective
  graph configuration. A synthetic fingerprint in tests exercises
  isolation only and does not qualify a real compiler/tokenizer/context.
- `namespace_key` / `scoped_key` are recomputed from the actual
  identity/config/bounds/versions/workspace on every construction and a
  mismatch is refused (direct model construction cannot retain a forged
  or stale key pair).
- `scoped_key` is carried DIRECTLY by every public record (documents,
  edges, candidates, snapshot); the nested `SourceOccurrence` provenance
  is bound through its owning document instead. A record from another
  scope is a `NAMESPACE_MISMATCH`/`WORKSPACE_MISMATCH`/`BOUNDS_MISMATCH`
  refusal, never a merge.

## 2. Root binding

- The effective root is the `AGENTS.md` inside the evidenced workspace
  (the 017 root envelope), never an adapter-host filename. An explicit
  path context must match the evidenced workspace or the root is a
  typed `ROOT_CONTEXT_MISMATCH` conflict.
- When no context is supplied, the root workspace is DERIVED from the
  evidenced root envelope and supported reads are re-observed under that
  derived context (explicit workdir/mismatch rules preserved).
- Repeated identical root versions deduplicate to one node while
  preserving occurrence provenance; a conflicting root-path read (a tool
  read at the root path with different content) or competing root
  digests is the `root_conflict` outcome with the fixed `COMPETING_ROOTS`
  reason. No implicit root supersession from any tool read (a tool read
  never establishes the root).

## 3. Source provenance and the same-occurrence seam law

Sources enter the graph only through the accepted 017 observation
surfaces (legacy read and native process) under one namespace:

- A non-COMPLETE or non-acquiring surface observation NEVER acquires a
  source, edge or candidate. The metadata observation itself runs under
  the accepted 017 package limits (the 017 report retains
  spans/digests/metadata only, never raw source bytes). The graph's own
  cumulative source ledger separately measures the exact UTF-8 byte
  length of every source body it actually inspects — the root body
  (every occurrence, duplicates included), every legacy read content
  body and every proven native process region body, complete and
  unsupported reads with an attributable content span included — BEFORE
  any graph-owned copy/reconstruction/retention. No earned native region
  means no fabricated native body count or copy.
- A single-member positive acquires only with an ACTUAL source proof:
  the earned member digest must equal the hash of the exact observed
  bytes (a metadata-only hash acquires nothing).
- A boundaryless multi-member bundle (e.g. `cat A.md B.md`) retains its
  earned ordered members, the exact whole-bundle digest and the original
  region proof WITHOUT inventing per-file hashes, bytes or edges. It
  contributes ONE unresolved-origin candidate record per deduplicated
  occurrence (possible origins = the resolvable members; candidates from
  the bounded scan of the bundle content).
- Same-occurrence seam law: one call/result occurrence positive on both
  surfaces is deduplicated ONLY when the full proof signature agrees —
  namespace, actual call identity and positions, original carrier
  intervals (occurrences keyed by request index, carrier and piece),
  ordered occurrence members, exact digest/content, and ownership.
  Equal text at DIFFERENT original intervals is not matching proof.
  Read-primary: the equal record survives once, attributed to the read
  surface, with the process occurrences preserved in the node union.
- A MISMATCHED positive proof (differing ordered members, differing
  intervals, or a mixed singleton-versus-whole-bundle member count on
  the same occurrence) is a typed `VERSION_CONFLICT`: the conflicting
  occurrence is pruned and acquires NO source, NO edge and NO candidate
  record from that occurrence; the snapshot refuses ready. A negative
  or non-acquiring surface alone never negates an independently
  consistent positive proof.
- Same path with different contents (or a candidate whose referring
  path/digest does not match the mapped document version) is a typed
  conflict; no version is chosen by tuple order, call ID, hash or
  arrival.

## 4. Reference grammar, origin and closure (reference-grammar/v1)

The bounded scanner (`references.py`) operates on the raw proven
document text before any compiler step. Four mandatory forms, exact
source spans, no dependency/CommonMark engine, no network/filesystem:

1. inline `[label](target)` with optional matching angle brackets and
   an optional bounded title;
2. line-start (indent ≤ 3) `[label]: target` definitions with the same
   bounded destination/title;
3. backtick code spans (matched run) containing one exact no-spaces
   `.md` path;
4. plain no-spaces `.md` tokens at token boundaries, optionally
   surrounded by ordinary quotes/punctuation.

Target law (fixed typed vocabulary, never a silent drop): strict literal
POSIX `.md` shape; the literal Unicode filename law (path characters are
the ASCII set plus any non-ASCII character that is not a space — no
normalization, decoding, expansion or query stripping); scheme/
`//host`/tilde/drive forms are typed EXTERNAL; percent-encoding,
backslash, query, control characters, unsafe prefixes and overlong
targets are typed UNSUPPORTED. The destination allowance is in ACTUAL
UTF-8 bytes (delimiters and labels never consume it); a destination
that provably continues past the allowance is ONE typed
`PATH_TOO_LONG` over the byte-bounded prefix — the no-partial-token law
— and the scan resumes at the proven boundary so independent references
are still found. Malformed markup earns one typed record over the
bounded proven region with no permissive plain fallback inside it.
Repeated explicit occurrences preserve evidence; the same occurrence
under markup/plain overlap deduplicates deterministically.

All scanner search windows are bounded by the declared allowances
(label window, destination byte window, title bound, proven malformed
region): no unbounded tail or backward searches, no quadratic work over
repeated unmatched markers.

Closure (`graph.py`, pure): BFS from the root over the accepted
documents; a candidate resolves against the REFERRING document's
directory (`./` relative) or is an explicit `PATH_TRAVERSAL` /
`PATH_OUTSIDE_WORKSPACE` / `PATH_ABSOLUTE_UNPROVEN` refusal. Reachable
unacquired paths become `DISCOVERED_CONTENT_MISSING` nodes (they never
expand the graph until independently acquired). A complete off-graph
document present among the bounded inputs cannot expand governing
edges until its path is independently reachable; fixed-point
reconsideration re-examines available complete documents without using
arrival order as freshness. Edge ownership deduplicates repeated
references while preserving occurrence evidence.
`GraphEdge.depth` is the target's TRUE shortest root distance
(0 = root self-loop; a shallower re-visit never deepens a walk).
Cycles terminate under the finite budgets. Determinism: node/edge
ordering is canonical; identical inputs yield byte-equal snapshots.
Across reordered batches the semantic topology and version results can
agree, but provenance `request_index` MUST remain the actual supplied
position, so a byte-equal full snapshot after changing request order is
not promised.
Acquired-empty sources keep `EMPTY_SOURCE_SHA256` and acquire no
outgoing edges.

Mixed-origin origin law (a-slice): a shared directory is NOT member
ownership or eligible-origin proof. A boundaryless bundle with mixed
eligible/background members keeps ONE unresolved-origin candidate
record per deduplicated occurrence and no invented edge; in this
a-slice boundaryless bundles remain unresolved, and any later
all-eligible common-base proof/admission is later 018 scope.

## 5. Bounds and diagnostics

Every `GraphBounds` constant has its own fixed typed refusal:

| Constant | Default | Unit / enforcement stage |
| --- | --- | --- |
| `max_requests` | 128 | batch requests (batch preflight) |
| `max_documents` | 128 | inspected source bodies, one snapshot |
| `max_single_source_bytes` | 1,000,000 | UTF-8 bytes, one inspected body |
| `max_total_inspected_source_bytes` | 4,194,304 | UTF-8 bytes, cumulative |
| `max_reference_candidates_total` | 2,048 | candidates, all documents |
| `max_reference_candidates_per_document` | 256 | candidates, one document |
| `max_nodes` | 512 | nodes, checked before each missing-node insertion |
| `max_edges` | 2,048 | graph edges |
| `max_depth` | 64 | TRUE shortest root distance |
| `max_work_units` | 65,536 | queue/edge/candidate-resolution operations |
| `max_diagnostics` | 64 | emitted fixed diagnostics (total) |
| `max_path_bytes` | 4,096 | UTF-8 bytes, destination allowance and workspace |

The source-ledger checks apply BEFORE any graph-owned
copy/reconstruction/retention (the ledger accounts every inspected
source body it measures, duplicates included). The candidate, node,
edge, depth and work-unit bounds are enforced at their respective
operations; the diagnostic cap applies to the emitted total. Over-bound
is an explicit typed refusal, never a success-shaped truncated prefix;
at-limit is at-limit.

The total number of emitted fixed diagnostics on the final public
snapshot (graph conflicts plus observation/global limitations,
including early refusals) is bounded by `max_diagnostics`; overflow is
ONE fixed `DIAGNOSTICS_FULL` refusal, never unbounded copied reasons or
a silent truncation. At-limit is at-limit: exactly-at-bound behavior
carries no limitation.

## 6. Outcomes, conflicts and versions

- Outcomes (fixed): `complete`, `no_root`, `workspace_unproven`,
  `root_conflict`, `version_conflict`, `over_bound`.
- Node statuses (fixed): `acquired`, `acquired_empty`,
  `discovered_content_missing`, `version_conflict`.
- `GraphLimitation` is the CLOSED fixed vocabulary for every emitted
  reason (root/workspace binding, path resolution, target law, markup,
  one per budget, scoped binding, origin/version). Free-form strings
  and arbitrary text are rejected by validation and never echoed.
- A snapshot's `conflicts`/`diagnostics` carry only that vocabulary;
  `str`/`repr` of every public and internal record suppress private ID
  values and raw source bytes (fixed placeholders; counts, locations,
  spans and digests remain observable). Validation errors carry fixed
  messages without input values.

## 7. Public API

```python
make_graph_namespace(identity, *, model_identity, config_fingerprint,
                     workspace, bounds=None) -> GraphNamespace
GraphRequest(payload=..., endpoint="responses", context=None)
    # Pydantic model: keyword construction; endpoint is REQUIRED and
    # explicit ("responses" | "chat"), never inferred
observe_graph(payload, namespace, *, endpoint="responses",
             context=None, bounds=None) -> GraphSnapshot
observe_graph_batch(requests, namespace, bounds=None) -> GraphSnapshot
build_graph(...)  # pure closure used by the observation layer and tests
```

The batch takes exactly one namespace (mixed-namespace batches are
structurally impossible) and one bounded request tuple. `GraphSnapshot`
is immutable: root/workspace binding, nodes, edges, conflicts,
diagnostics, unresolved-origin candidates, measured inspection
totals and version constants. Inputs are never mutated; the public path
performs no host IO (purity is test-asserted). The low-level synthetic
constructors and `build_graph` are unit-test seams over explicitly
constructed typed records; they are NOT independent acquisition
authority — the public composition re-derives the accepted 017 source
proof from the original supplied API payloads.

## 8. Slice boundary

This a-slice earns: the typed namespace, the bounded reference scanner
with its exact grammar/bounds/work law, the pure graph closure, the
bounded public composition over the accepted 017 observation surfaces
(including the whole-bundle seam law and unresolved-origin
representation), and their typed tests. It does NOT earn: lean/greedy
admission (G03–G05), entry/cache identity and replay invalidation
(C01/C02/C04–C06), RAM (C03/M0x), recovery, compilation or replacement.
Those remain the mandatory 018-b/c+ stages at their NOT RUN/PENDING
states in `docs/CACHE-REWORK-LEDGER.md`. No automatic acceptance follows
from this document or from green focused tests: objective 017 is
ACCEPTED at its bounded pure-observation scope with process
qualifications and merged to main at ffaabf4b (017-am decision);
018-a is inert implementation pending strategic review; broader 018
admission/version/replay/overlap and 019–024 remain mandatory.

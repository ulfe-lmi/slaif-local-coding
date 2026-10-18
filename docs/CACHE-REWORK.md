# CACHE rework: dependency-graph acquisition, insertion bundles, and RAM state

**Status:** Human-approved design intent; detailed handoff for maintainer review
and work-order design. **Not implemented or qualified by this document.**

**Prepared:** 2026-10-18. **Owner of implementation:** SLAIF Local Coding.

## 1. Purpose, authority, and reading order

The human approved the ten rules in section 3 after reviewing failures observed
in real Codex benchmark histories. This document makes those rules concrete
enough to revise the architecture, define data contracts, and issue bounded work
orders. It does not itself activate an OAP order, change `oap/active`, amend an
existing order/report, authorize deployment, or claim a product fix is complete.

The immediate product objective is to keep coding aligned with its governing
instructions by preserving useful compiled context across a long session. The
measurable hypothesis is less drift/rework, shorter wall time, fewer model/tool
exchanges, and potentially fewer tokens, at preserved task quality. Benefits
must be measured; more caching or more injections alone do not establish them.

The word **gateway** in the design discussion means the component performing
these context transformations. In this repository, that implementation belongs
to the **Local Coding adapter**. The separate API Gateway continues to own
authentication, authorization, signed identity, routing and public accounting.
Expose `lean`/`greedy` through explicit route/session configuration; any change
to the separate Gateway's configuration contract needs coordinated ownership.

Maintainer reading order:

1. Read the approved rules and the observed failures below.
2. Reconcile the architecture/security changes listed in section 4.
3. Specify the remaining decisions in section 18 before implementation.
4. Use the module map, work packages and acceptance matrix to write orders.
5. Require evidence of dependency content acquisition and actual source
   replacement, not just successful root compilation.

### Repository and evidence provenance

The inspected local checkout was on `oap/005-gateway-ingress-integration` at
`4d3ab2fd97d249710f952dd3d2c28936138cc8fa`, with an initially clean worktree and
active marker `005-m`. Read-only GitHub reconciliation on the preparation date
reported that branch at `e9829d84cc4116f749ddc8bc97b08fa37231e77f` and `main` at
`f3793af9e5f05bdfba19ef800eeaf57177d0ed2b`. Do not assume the inspected local
branch is the implementation starting point. The maintainer must select and
reconcile the appropriate current branch before coding.

Runtime findings below came from immutable RC10:

- Product candidate: `slaif-local-coding` `0.1.0-rc10`.
- OCI digest: `sha256:5a02e0043fcc65e5dc5a78f3e2a8648a16c93620255e904e394c926b18c92960`.
- Image source: `1a04528223445e4249fad6d24a71151fd1dc1a09`.
- Measured Codex client: `0.149.0`.

This is a documentation-only handoff. No product source, runtime, model server,
active OAP artifact, or existing benchmark evidence was changed to prepare it.

## 2. Why the current acquisition/cache design needs rework

### 2.1 Confirmed observations

The investigation found all of the following:

- Codex supplied the complete root `AGENTS.md` as a user `input_text` message
  using its explicit project-instructions wrapper in all 64 coding attempts.
- The coding roots were small: 417 bytes for web and 375 bytes for terminal,
  including final newlines. They referred to fuller Markdown specifications.
- In the 16 CACHE coding attempts, the adapter performed one root compilation
  and one cache write per attempt, but recorded **zero observed dependencies
  and zero included compiled dependencies**. The complete task documents were
  not being cached merely because the root named them.
- Real reads included compound commands, multiple files, absolute workspace
  paths, working-directory changes and loops. The detector's exact single-read
  regex and absolute-path rejection did not accommodate these patterns.
- None of the CACHE coding sessions compacted. In the separate context task,
  the full root instruction block was present in the replacement history after
  all 16 inspected DIRECT compactions and all 16 inspected CACHE compactions.
  Native compaction is therefore not evidence that the root was lost.
- RC10's Responses injector prepended a compiled constitution to top-level
  `instructions` while preserving the original conversation. Successful
  injection did not prove original-source removal or input-token savings.
- The benchmark's derived field named `rehydration_hit` was mapped to generic
  compiler-cache hits. Raw product metrics distinguished observed-root
  injection from zero-root recovery; the generic count must not be used as
  evidence that lost context was recovered.

The private history audit examined 772 loose native files representing 338
distinct sessions. It verified 429 tool outputs containing complete,
nonoverlapping contents of at least two Markdown files, with 2–9 complete files
per output. Another four outputs contained only multi-file partial views. Of
the 429 full-content cases, 150 came from the current preliminary campaign,
including 37 CACHE cases: four web, seven terminal and 26 context. Duplicate
copies and replayed compacted-history material were not counted again.

These are engineering observations, not new formal benchmark outcomes. The
private corpus remains outside this repository. Its audit bundle is named
`markdown-read-audit-20261018-a01`; start with its `REPORT.md`, `SUMMARY.json`,
`INSERTIONS.csv`, `FULL-CONTENT-INSERTIONS.json` and `ARCHIVE-COVERAGE.json`.
Its sealed content digest is
`a6021bb9019f3c4d3136ea90ced1ee727bb983771b2328634faf6b0ab55059df`.
One historical record was malformed and one multi-file read lacked a recorded
result; absent content was not fabricated. Use the corpus privately to derive
sanitized fixtures. Do not commit its original histories, task answers or
customer/source content here.

### 2.2 The behavior that must change

The new design must acquire the actual governing content that crosses the API
boundary, including combined file insertions. It must compile and retain that
content under stable identities, replace eligible original source spans in
model-bound requests, and reconstruct a bounded useful working set from RAM.

Recognizing a root, discovering a filename, observing file bytes, compiling a
bundle, replacing a source span and injecting compiled context are distinct
events. Each must be testable and observable independently.

## 3. Approved mechanism: ten rules

These are the human-approved requirements. Details explicitly marked
**proposed** or **maintainer decision** elsewhere must not be represented as
additional human-approved policy.

1. **Recognize the root.** Detect the explicit Codex `AGENTS.md` envelope and
   extract its complete observed text and directory identity.
2. **Discover dependencies recursively.** Parse explicit `.md` references from
   the root and subsequently observed reachable documents. Resolve references
   against the referring document's directory; track a graph with shared nodes
   and cycles. The agreed filename convention excludes spaces.
3. **Observe actual content insertions.** Recognize supported file-read tool
   calls, pair results by call ID, assess read completion/truncation, and locate
   the content region. Support the actual Codex formats, including combinations.
4. **Configure bundle admission.** `lean` admits a whole bundle only when every
   member is graph-eligible; it may admit an isolated eligible portion when
   boundaries are proven. `greedy` admits the entire bundle when at least one
   member is eligible. Neither mode admits an arbitrary unrelated single file.
5. **Cache insertion bundles independently.** `[A,B]`, `[A]` and `[B]` are distinct
   entries even when their bytes overlap. An eligible single-file read creates
   its own entry even if the file previously appeared inside a bundle. Treat
   storage capacity as effectively unconstrained; duplication is acceptable.
6. **Replace originals only after successful preparation.** Preserve API/tool
   structure, replace the recognized raw-content span with a stable reference,
   and provide the appropriate compiled context. An opaque reference by itself
   is not usable instruction content for the model.
7. **Scale insertion size with effective context.** One file receives a maximum
   allowance of `effective_context_tokens / 32`; an N-file bundle receives N
   allowances. Enforce a separate aggregate injection budget with reserves for
   conversation, tools and generation. Storage size is not this insertion cap.
8. **Compile once per version/configuration.** Reuse a valid compiled entry for
   unchanged content. Source changes invalidate affected overlapping bundles;
   compile updated content when it becomes available. Do not inject stale state.
9. **Retain originals as evidence/recovery material.** Keep exact observed source
   bundles and provenance. Do not routinely return the originals to model input
   or use them as a hidden fallback.
10. **Use RAM for the working cache; recover sessions from disk after restart.**
    Normal lookup/reinjection uses memory. Persist recovery state separately
    per session, including originals and metadata. After restart, load only
    sessions being resumed and rebuild their caches. Recovery recompilation is
    the explicit exception to the normal compile-once rule.

## 4. Reconcile existing architecture before implementing

The approved behavior deliberately changes several existing contracts. Update
both [the human architecture](../ARCHITECTURE.md) and
[the compact agent architecture](../ARCHITECTURE-for-agents.md), plus
[security](../SECURITY.md), [testing](../TESTING.md), [README](../README.md) and
[configuration documentation](ADAPTER-CONFIGURATION.md) through maintainer-owned
orders. Do not leave contradictory old law alongside the new profile.

| Existing design | Required direction |
|---|---|
| Exact single-file shell-read grammar | Evidence-based support for real read commands and whole insertion bundles |
| Reject every absolute observed path | Distinguish a client-workspace absolute path from an outside/unknown path; normalize only with proven workspace context |
| Root-declared, narrowly acquired dependencies | A session graph extended through raw referenced Markdown as it is observed |
| One compiled index identified as one source file | Typed file-version records plus independent single/multi-file bundle entries |
| Filesystem-backed `DerivedIndexCache`, tmpfs/XDG fallback, TTL/LRU | RAM working entries; separate per-session recovery/evidence persistence |
| Small storage limits drive eviction/recompilation | Retain live-session entries without capacity-driven semantic churn; handle real resource exhaustion explicitly |
| Fixed injected UTF-8 byte budget | Token-based per-file/bundle insertion allowances plus an aggregate context budget |
| Primarily additive constitution injection | Transactional replacement of acquired original spans plus bounded compiled injection |
| Originals normally not persisted | Protected, explicitly configured source/evidence and session-recovery records |
| Safe raw-request fallback on compiler/cache errors | A new explicit failure contract compatible with replacement and the no-hidden-original-fallback rule |
| Full-source reread used as a recovery strategy | Repeated incoming source reads resolve to cached compiled content during normal operation; disk originals are recovery/evidence |
| Process-local rehydration map lost on restart | Durable per-session recovery records and an explicit rebuilding state |

"Effectively unlimited" is a product retention assumption, not a promise of
infinite physical RAM. The replacement profile must not silently revert to LRU
eviction, recurring compilation or disk-backed hot lookup when memory is tight.
Resource exhaustion needs an explicit operator-visible state and defined
backpressure/failure handling. Session teardown and explicitly authorized
retention cleanup remain possible.

## 5. Terms and identities

Use different names for the following concepts in code and telemetry:

- **Root:** evidenced effective `AGENTS.md`, with its workspace/directory scope.
- **File node:** a normalized client-repository path in the dependency graph.
- **File version:** observed complete file content plus a content hash, when
  individual file bytes can actually be attributed.
- **Insertion observation:** one occurrence of source-bearing content in a
  request; for a tool read, identified by session, call ID and result location.
- **Bundle:** the complete observed content region belonging to an ordered set
  of files. It may lack reliable boundaries between those individual files.
- **Bundle entry:** one versioned compiled representation of a bundle in RAM.
- **Slot width:** the number of file allowances assigned to that entry; it is
  not the count of separately addressable source fragments.
- **Working set:** compiled entries selected for one outgoing model request.
- **Recovery record:** durable session state used to rebuild RAM after restart.
- **Cache epoch:** one live ownership/lifetime of a session's RAM cache. Recovery
  starts a new epoch and records why recompilation occurred.

Do not equate an insertion observation with a new compilation: the same old
tool result can appear in many subsequent requests. Do not equate a cached
bundle with N independently known file versions when boundaries were unknown.

## 6. Detection and acquisition contract

### 6.1 Automatic root format

Support the observed Codex user-message form, shown here with synthetic content:

```text
# AGENTS.md instructions for /work

<INSTRUCTIONS>
Follow ARCHITECTURE.md and docs/PROCESS.md.
</INSTRUCTIONS>
```

In Responses, this is `role="user"`, `content[].type="input_text"`. It is not
necessarily an `input_file` attachment or top-level `instructions`. An
environment-context item can occur alongside it and is not part of the root
file. Use versioned envelope parsing, exact content offsets and appropriate
duplicate/malformed-marker handling. Arbitrary text, assistant claims or tool
descriptions mentioning `AGENTS.md` do not establish a root.

Hash the exact observed source bytes. Distinguish those bytes from a claim about
the original filesystem encoding if the client normalized text before sending
it. Keep CRLF/Unicode behavior explicit and tested.

### 6.2 Tool read format

Ordinary Markdown reads commonly arrive as a paired tool call and output:

```json
{
  "type": "function_call",
  "name": "exec_command",
  "call_id": "synthetic-read-1",
  "arguments": "{\"cmd\":\"cat /work/A.md /work/B.md\"}"
}
```

```text
function_call_output, call_id = synthetic-read-1
Chunk ID: ...
Wall time: ...
Process exited with code 0
Output:
...A content immediately followed by B content...
```

The result may contain tool-generated wrappers, directory listings, labels,
stdout/stderr, multiple files or a truncated body. Detecting `cat` and a filename
is only the first stage. It does not establish success, completeness, exact
file contents or a removable output span.

Required read families include:

```sh
cat A.md
cat /work/A.md
cd /work && cat A.md B.md
cat A.md && cat B.md
ls -la /work && cat /work/A.md
for f in A.md B.md; do echo "=== $f ==="; cat "$f"; done
for d in alpha beta; do cat "policies/$d/AGENTS.md"; done
```

Support must be earned for each syntax class. Prefer a bounded shell parser and
an explicit read grammar over one increasingly permissive regex. Regex remains
useful for the root envelope, path candidates and known output wrappers.
Never execute observed commands, evaluate command substitutions, expand paths
on the adapter host, or access the client repository to improve detection.

Tests must exclude heredoc/file-writing commands, quoted examples, comments,
redirections to files, and branch alternatives that did not execute. Treat
`head`, `tail`, `sed`, pipes, glob expansions, loops and Python readers according
to their actual evidence; a fragment is not a complete file merely because it
contains a recognizable filename.

### 6.3 Path normalization

Maintain a separate client-workspace path domain. With an evidenced workspace
root `/work`, `/work/docs/A.md` may map to repository-relative `docs/A.md`.
It must never become a filesystem read of the adapter's `/work`.

Resolve explicit `workdir` and supported literal `cd` transitions. Check path
components, not string prefixes: `/work-other/A.md` is outside `/work`. Handle
or reject traversal, ambiguous expansion, unknown roots and alternate path
syntaxes explicitly. A namespace-bound workspace mapping must not be inferred
from arbitrary source prose or a spoofed external identity header.

### 6.4 Read success and complete output

Track separate facts: call/result pairing, requested paths, execution evidence,
returned text, completeness and attribution. A global exit status can be
misleading: `cat A.md B.md; failing_later_command` can return both files in full
with an overall nonzero exit. Conversely, a later successful command can mask
an earlier failed `cat`.

Use per-command evidence when available. Otherwise classify uncertainty instead
of declaring all requested files successfully read. Collect multi-chunk tool
results only when their process/call association and completion are proven.
Recorded truncation or missing output must remain explicit.

### 6.5 Bundle boundaries

Internal A/B boundaries are **not required** when the entire A+B region can be
attributed, admitted and compiled as a unit. Outer boundaries **are required**:
do not remove directory listings, execution diagnostics, unrelated responses or
tool metadata just because they surround a file read.

For a single `cat A.md B.md`, the output region may be one complete bundle.
For mixed commands, require evidence of the appropriate outer spans. Delimiter
strings printed by a command are helpful but are not universally collision-free.
When boundaries or members are uncertain, emit a typed acquisition limitation.
Do not solve the uncertainty by changing successful client commands or coaching
the benchmark subject into a special read style.

The offline audit used saved file snapshots to corroborate exact output bytes.
That is test-oracle assistance. The production adapter cannot assume it has
those snapshots before acquisition. Never import this audit-only shortcut into
runtime detection or claim that every audited case is already production-safe.

## 7. Dependency graph and admission modes

### 7.1 Recursive graph discovery

Construct directed edges from raw observed source before semantic compilation:

```text
AGENTS.md -> ARCHITECTURE.md -> docs/INTERFACES.md
          -> docs/PROCESS.md -> docs/INTERFACES.md
```

Every reachable Markdown node is eligible, regardless of how a compiler later
ranks its usefulness for a particular request. Eligibility for caching and
selection for immediate injection are different decisions. Do not silently
discard reachable files because they were classified as background.

Extract explicit Markdown links, reference definitions, backticked filenames,
and supported plain-text `.md` paths under the no-spaces convention. Preserve
reference evidence and normalized target identity; strip link fragments
according to a documented path grammar. Reject external URLs as repository
file dependencies unless a separately approved policy supports them.

Iterate to a fixed point as new raw content arrives. Track visited versions and
cycles. A reference establishes eligibility, not possession of its contents.
Represent unread reachable nodes as `DISCOVERED_CONTENT_MISSING`; no compiled
entry exists until sufficient content is observed.

References are relative to the **referring file**, not always the repository
root. For a boundaryless multi-directory bundle, reference origin can be
ambiguous. Cache admission can still succeed, but do not invent a source file
or graph edge. Use unambiguous attribution, a common demonstrably applicable
base, or retain an unresolved reference until additional evidence arrives.

### 7.2 Lean/greedy truth table

Let `members(B)` be the known members of bundle B and `eligible(f)` mean that f
is reachable from the evidenced root graph in the relevant session version.

```text
lean:   admit whole B iff every member is eligible
greedy: admit whole B iff at least one member is eligible
```

| Observed insertion | `lean` | `greedy` |
|---|---|---|
| One eligible file A | Cache A | Cache A |
| Two eligible files A+B | Cache A+B | Cache A+B |
| Eligible A + outside-graph B, boundaries known | Isolate/cache A; preserve B | Cache the whole bundle |
| Eligible A + outside-graph B, internal boundary unknown | Leave combined insertion uncached | Cache the whole attributable bundle |
| No eligible member | Do not cache | Do not cache |
| Unknown member list or unproven outer region | Acquisition limitation | Acquisition limitation; greedy does not establish missing evidence |

Record the mode in configuration, cache identity and recovery state. Do not
change it implicitly in response to outcomes. The default remains a maintainer
decision; `lean` is the conservative recommendation, not an additional approved
default.

Keep graph membership, admission reason and co-cached member status separate.
Greedy admission does not itself prove a dependency edge or confer root-level
authority on every co-cached file. The precise policy for following references
from off-graph co-cached members must be resolved explicitly; do not silently
turn co-occurrence into an unrestricted graph-expansion rule.

## 8. Bundle identity, overlap and invalidation

An entry's identity must include at least:

```text
authenticated principal + stable session + repository/workspace + route/model
ordered normalized member references
exact bundle-content digest
parser/evidence format and admission-policy versions
graph/root scope needed to interpret authority
compiler model/revision + prompt/schema/semantic policy versions
tokenizer identity + effective-context/insertion-budget configuration
compiled/render format versions
```

Use opaque identifiers in protocol-visible references. Do not expose credentials,
private filesystem paths, or globally correlatable cross-tenant keys.

`[A,B]` and `[B,A]` are distinct when order differs. `[A,B]`, `[A]` and `[B]` are
independent entries. Do not require splitting an existing bundle to admit a
later singleton. Repeated identical observations hit the existing entry without
another model compilation.

Store a whole-bundle digest even when individual member hashes are unavailable.
Do not label the bundle digest as the hash of each constituent file. Preserve
`member_hash = unknown` and the evidence needed to refine it later.

Maintain a reverse index from member path to affected bundle entries. A proven
new file version invalidates old overlapping entries for future selection.
Where a singleton observation cannot be reconciled with a boundaryless older
bundle, expose a version conflict/stale state; do not fabricate a new A+B by
splicing unidentified bytes. A fresh complete A+B observation can establish its
new version. Keep invalid historical entries as evidence if retention requires,
but never inject them as current authority.

Historical messages reappear in later requests. Deduplicate observations using
session/call/item identities and content fingerprints, with a monotonic session
revision. Replayed old history must not roll current A-v2 back to A-v1 or cause
an endless cycle of invalidation/recompilation. A deliberate later revert to
A-v1 needs a genuinely new observation, not merely an old message being resent.

Graph edges are versioned too. If a root or referring file removes an edge,
recompute reachability and active eligibility; disk evidence may remain, but an
old edge must not silently keep an otherwise ineligible entry active.

## 9. Insertion sizing and context accounting

Let C be the **effective client/session context budget in tokens**, not blindly
the model server's physical maximum. Define:

```text
base_slot_tokens = floor(C / 32)
bundle_slot_width = number of represented distinct file identities
bundle_insertion_allowance = bundle_slot_width * base_slot_tokens
```

| C | One-file allowance | Two-file allowance |
|---:|---:|---:|
| 262,144 | 8,192 | 16,384 |
| 32,768 | 1,024 | 2,048 |
| 40,000 | 1,250 | 2,500 |

These are maximum insertion allowances, not padding or storage allocation.
Specify decimal versus binary K explicitly. Repeated occurrences of the same
file in one read must not inflate its slot width; their actual observed bytes
still belong to the versioned bundle. A greedy bundle's allowance counts all
represented members, not only graph-eligible members.

Use the actual model tokenizer, versioned with the cache entry. Count the final
rendered block, including metadata, separators and references. Character/byte
heuristics may be diagnostics, not the authoritative token gate. Preserve
independent byte/JSON limits for safe transport and parsing.

The aggregate selector must satisfy a relation such as:

```text
remaining ordinary request tokens after source replacement
  + selected compiled blocks and reference overhead
  + required output/tool/uncertainty reserve
  <= effective context budget
```

Also enforce an explicit total injection limit. Per-file slots do not authorize
injecting an entire large cache: 32 full slots would already consume C before
any ordinary conversation or output. Opaque references cannot compensate for
omitting essential instructions that the model actually needs.

Effective C and reserves must come from a validated route/session capability
contract. A client configured for 40K must not receive 8K slots merely because
its physical backend supports 256K. Unknown/mismatched context configuration
needs an explicit state, not a guessed large allocation.

Compiled output that exceeds its allowance is invalid for that allowance.
Never truncate rules silently or let an individual bundle exceed the aggregate
budget. Changing C, tokenizer or compilation budget changes cache identity;
working-set selection alone must not cause routine recompilation of unchanged
entries. The maintainer must specify essential-overflow behavior before coding.

## 10. Compilation and working-set behavior

Compile each admitted content version/configuration once per live cache epoch.
Concurrent misses for the same key share one in-flight compilation. Validate
schema, source digest, deterministic references, member attribution, normative
strength, output completeness and actual rendered token budget before marking
the entry ready.

The compiler receives original source as data on initial acquisition, relevant
provenance, the deterministic graph/reference manifest, and the requested
insertion allowance. It must preserve binding requirements, exceptions,
authority scopes and conflicts. It must not invent per-file attribution for
unsegmented bundles or promote unrelated greedy members to governing rules.

Retain direct nonrecursive internal compiler routing, no tools, bounded
concurrency, cancellation and separate usage accounting. Do not replace stable
cache reuse with a model call on every request to decide what to insert.

Define these states independently:

```text
DISCOVERED_CONTENT_MISSING -> OBSERVED_COMPLETE -> ADMITTED
ADMITTED -> COMPILING -> VALID_RAM
COMPILING -> INVALID / OVER_BUDGET / CANCELLED
VALID_RAM -> STALE when source/graph/configuration changes
checkpoint + resumed session after restart -> REBUILDING -> VALID_RAM
```

A failed/truncated compile is not a cache entry. Automatic retries, if the
maintainer permits any for compiler infrastructure failure, need an explicit
bounded policy and separate counters; they must never be reported as cache hits
or hidden successful compile-once behavior. Never replay an already forwarded
main-model request to obtain a preferred outcome.

Selection for injection is separate from compilation/storage. The human has
approved proportional slot budgets and an aggregate cap, but has not selected
an exact scheduling/ranking algorithm. Specify stable root/scope handling,
current-file relevance, priority, starvation prevention, overlap handling and
essential-entry behavior in the architecture. Cached A and cached A+B may both
exist; storage duplication does not require injecting both simultaneously.

Greedy members may be background data or code. Preserve that provenance; do not
convert every sentence in a co-cached document into a high-priority instruction.
Source authority, scopes, and contradictions must survive compilation.

## 11. Transactional request replacement

Implement source replacement as a pure, versioned request transformation with
structured evidence, coordinated with the session state machine:

1. Authenticate and resolve namespace, route, context budget and mode.
2. Apply the unchanged image policy and validate the supported JSON envelope.
3. Locate root/file observations and exact outer source spans; pair tool results.
4. Update the versioned graph and assess bundle admission.
5. Resolve hits or compile misses into valid RAM entries; invalidate stale state.
6. Select a complete in-budget working set and construct source replacement edits.
7. Commit only when replacements, references, selected content and session state
   agree; then serialize and forward the request once.
8. Stream the response unchanged and record actual transform/usage outcomes.

Preserve call IDs, tool names/arguments, item order, endpoint semantics, ordinary
user text and unaffected prefix/suffix output. Never remove a whole
`function_call_output` merely because some of its text is cacheable. A compiled
reference must identify the relevant entry/version within the current namespace
and be accompanied by usable compiled information according to selection policy.

Replace source spans in automatic root envelopes as well as supported tool
results. Codex can keep originals in its own local history and resend them;
the adapter must replace those observed spans again on outgoing requests using
RAM hits, without recompiling or mutating Codex's native session files.

Idempotence must cover already transformed requests, repeated root envelopes,
tool-history replay and reconstruction after compaction. The output must not
accumulate duplicate compiled blocks or stale references. Forged/mismatched
markers must not resolve to another session's state.

Replacement and required compiled injection are one transaction. Never delete
the only available governing content and then discover that compilation,
checkpointing or budget selection failed. Never forward dangling references
after a process restart. Preserve the source-evidence digest and the exact
locations changed so fake-upstream tests can prove the transformation.

Current Responses injection uses top-level `instructions`; Chat uses a stable
system location. Reuse API-valid placement where appropriate, but explicitly
review role/authority semantics now that full originals will be removed.
Adding text at a higher API role must not give off-graph source content new
authority. The exact marker/reference format is a maintainer-owned contract.

## 12. RAM cache and per-session restart recovery

### 12.1 Normal operation

The active compiled entries, graph, versions, lookup indexes, working-set state
and in-flight compilation map live in RAM. Normal hits, rendering, selection
and reinjection must not read source recovery files or deserialize filesystem
cache entries. Moving a file cache to `/dev/shm` still leaves a file-backed hot
path and does not meet this requirement.

Keep enough in-memory provenance to recognize replay, update graph state and
assess incoming changes. New source observations can be written to session
recovery/evidence state during normal operation; the rule prohibits using those
files as the normal read path. Define checkpoint durability and write latency
explicitly. Security-related metadata checks and initial configuration loading
are not claims that the content hot path reads recovery data.

Retain distinct bundle entries even when they overlap. Ordinary insertion-budget
pressure selects fewer entries; it does not evict stored entries or force later
recompilation. If real RAM limits are reached, backpressure or an explicit
failure/degradation policy must apply. Do not silently reinstate the old small
TTL/LRU cache behavior under the new profile.

### 12.2 Recovery record

Persist one protected namespace per coding session, not a shared flat pool of
customer files. The exact container format is an implementation choice. It must
record enough to rebuild:

```text
checkpoint schema + generation + integrity metadata
authenticated namespace and stable session/repository/route binding
root identities and graph versions, including unresolved references
source observations and their logical order/deduplication fingerprints
exact original file/bundle bytes and whole-bundle digests
ordered membership, known individual versions, unknown-attribution flags
valid/stale/conflicting admission states and lean/greedy mode
compiler/model/tokenizer/prompt/render versions and insertion-budget settings
previous cache epoch and the explicit recovery reason
```

The full original source bundles are the recovery substrate. Persisting live
compiled slots is not required: the agreed restart behavior rebuilds them.
Operational logs must not become this source store. Checkpoints do not need
entire conversations, images, transport authentication or unrelated tool output.

Use atomic generation publication and integrity checks; define handling of a
crash before or after publication. Avoid torn snapshots that bind A-v2 metadata
to A-v1 bytes. Concurrent writes require a clear per-session ownership/locking
model. A session owner may write a new generation, but another worker must not
silently overwrite it with older state.

### 12.3 Restart/resume sequence

On restart, a session is not immediately ready merely because a file exists:

1. Receive an authenticated request to resume an identified session.
2. Read only that session's recovery record; validate binding, integrity,
   schema, revision and compatible configuration.
3. Rebuild the graph and admitted source versions in RAM. Mark unresolved
   conflicts and invalid historical entries explicitly.
4. Compile the needed valid bundles once in the new cache epoch. Rebuild
   eagerly or lazily according to a documented policy, with bounded compiler
   concurrency and no main request forwarded with unresolved required entries.
5. Mark the session ready only when the next request's replacement/injection
   contract can be satisfied.
6. Continue normal RAM-only lookup. Do not reread its recovery files per turn.

Source bytes are read by the adapter during recovery and supplied to the
isolated compiler for rebuilding. That is different from reinserting raw source
into the main coding request. The latter remains disallowed as a hidden fallback.

Do not eagerly read and compile every dormant session at startup. Do not reuse
a stale compiled representation after the tokenizer, context budget, compiler
policy or source version changes. Record recovery-generated model work separately
from first acquisition and ordinary hits.

For multiple service workers, choose explicit session affinity or one session
owner. Independent worker RAM caches behind round-robin routing would otherwise
repeat compilation and produce divergent state. Distributed cache coherence is
not implicitly authorized by the RAM design.

## 13. Proposed data contracts and configuration surface

The names below are **design placeholders**, not current configuration keys or
an already implemented API. The maintainer should map them into typed models
and versioned configuration with migration errors for contradictory legacy keys.

### 13.1 Internal contracts

| Contract | Minimum information |
|---|---|
| `SourceObservation` | Namespace, occurrence/call IDs, source locations, requested members, evidence of execution/completeness, removable outer spans, raw observed bytes/digest |
| `FileNode` | Repository-relative identity, eligibility provenance, root/directory scope, current known generation, version confidence |
| `DependencyEdge` | Referring node or unresolved source set, reference span, normalized target, source generation, resolution status |
| `InsertionBundle` | Ordered members, exact aggregate bytes/digest, known/unknown internal boundaries, admission reason, raw token count, slot width |
| `CompiledBundle` | Bundle identity, compiler/configuration identity, validated semantic representation, rendered token count, version, validity state |
| `SessionCache` | Root graph, file/bundle indexes, reverse membership, replay/version tracking, in-flight map, working-set metadata, epoch |
| `ReplacementPlan` | Exact content edits, references, selected compiled entries, resulting token budget, preservation assertions |
| `SessionRecoveryRecord` | The original-source and metadata snapshot described in section 12, scoped to one session |

Use explicit nullable/unknown fields for per-file hashes or attribution that are
not established. Do not synthesize a filename-to-byte mapping simply because
several filenames were recognized in a command.

### 13.2 Configuration requirements

Specify at least:

- enable/disable the new cache profile, independently of image handling;
- explicit admission mode `lean | greedy`;
- trusted effective context token budget and tokenizer identity;
- base-slot divisor `32` for the agreed initial policy;
- total injection budget and generation/tool/uncertainty reserves;
- validated compiler model, policy, output budget, timeout and concurrency;
- session namespace/ownership and restart-recovery policy;
- protected recovery/evidence location and lifecycle;
- explicit unsupported-read, compile-failure, source-conflict and overflow
  behavior, with no hidden raw-source fallback;
- finite parser/request limits and explicit resource-pressure behavior.

Illustrative vocabulary, **not runnable TOML for the current release**:

```toml
[context_cache]
profile = "dependency-bundles-v1"
admission_mode = "lean"       # or "greedy"; selected explicitly
working_storage = "memory"
effective_context_tokens = 32768
slot_divisor = 32
active_session_retention = "retain_entries"

[context_cache.recovery]
enabled = true
load_policy = "on_session_resume_after_restart"
rebuild_compiled_entries = true
```

The complete operational configuration must additionally set the aggregate
budget/reserves and failure/ownership policies. Do not infer them from this
abbreviated example or silently use the server's largest advertised context.
Persist the resolved configuration identity with each session.

## 14. Security, authority and failure semantics

### 14.1 Scope of the approved persistence change

The current security documents prohibit raw source persistence by default. The
new human-approved design retains exact originals for evidence and session
recovery. This is a deliberate change requiring a narrow documented exception
for the protected store, not blanket permission to log bodies.

Retained source and compiled state are sensitive. Keep session/tenant isolation,
restricted ownership and permissions, integrity protection, explicit retention
and deletion semantics, and any deployment-required encryption. Never include
transport credentials, bearer headers, cookies or upstream keys in cache keys,
compiler prompts, recovery records, metrics or reports. Source material that
violates existing secret-handling policy needs an explicit handling decision;
do not silently redact it and continue claiming exact source fidelity.

`greedy` broadens the content admitted from a read bundle. It does not bypass
authentication, workspace boundaries, credential protections or compiler
instruction/data separation. Document the confidentiality consequences of
retaining co-cached content and the graph-membership policy separately.

Do not directly read the client repository, inspect the adapter filesystem to
resolve a client path, execute supplied shell commands, or fetch arbitrary
referenced URLs. Do not modify Codex, vLLM, model weights or serving flags as
part of implementing this product mechanism.

### 14.2 Define failure policy before replacing sources

The old additive pipeline can preserve the original request on failure. The
new replacement profile must specify its own behavior explicitly:

| Failure | Required invariant |
|---|---|
| Root or read not sufficiently evidenced | Do not invent acquisition or remove the uncertain span |
| A required dependency is named but not observed | Report missing content; never synthesize a compiled version |
| Compiler timeout, invalid schema or truncated output | No valid cache entry, no successful replacement claim |
| Compiled content exceeds its slot | Typed budget failure; no silent truncation of instructions |
| Required working set exceeds aggregate context budget | Resolve through the declared policy before forwarding; no dangling required references |
| Checkpoint unavailable or corrupt during resume | Explicit recovery failure; do not bind another session or silently treat partial state as ready |
| Source/version conflict | Mark affected bundles stale/conflicting; never inject mixed revisions as current |
| RAM exhausted | Visible backpressure/failure; no hidden disk hot path, eviction loop or source loss |
| Main request disconnected or already forwarded | Cancel/clean up correctly; never automatically replay it |

The maintainer must decide whether a never-transformed incoming request may be
explicitly forwarded in an observable unoptimized mode, or whether the new
profile rejects/defers it. That choice must be reconciled with the human's
no-hidden-original-fallback rule and existing governance-preservation law.
It is not permission to load original sources from disk on a normal cache miss
and silently send them to the coding model.

## 15. Observability that proves delivery

Define events/counters for each stage, with fixed reason enums and low-cardinality
labels. Do not put source text, private filenames, hashes, cache IDs or session
values into unbounded/public metric labels. Use a protected per-session evidence
channel for exact identity correlation when explicitly enabled for tests.

Required distinctions:

| Stage | Facts to expose |
|---|---|
| Detection | Root envelopes recognized/rejected; supported read syntax; paired, missing, duplicate and multi-chunk outputs |
| Content acquisition | Complete file/bundle bytes observed; partial/truncated/ambiguous regions; absolute-path normalization outcome |
| Graph | Nodes/edges discovered, reachable/missing/unresolved counts, edge removals and cycles |
| Admission | Lean/greedy decision, bundle width, eligible/co-cached member counts, rejection reason |
| Compilation | Actual model invocations, first acquisition versus recovery, single-flight followers, failures/truncation, input/output tokens |
| Cache | Valid RAM hit/miss, version conflict, stale state, active entries/bytes, no disk-content-read hit path |
| Replacement | Original spans/tokens removed, references inserted, unchanged regions verified, replacements committed |
| Injection | Selected bundles, rendered tokens, allowance/aggregate budget, omission/overflow, injection location |
| Recovery | Session requested, checkpoint read, validated/rejected, rebuild start/complete, new epoch |
| Upstream | Main request forwarded/rejected, outcome, provider usage, cancellation |

Do not call a compiler-cache hit a rehydration hit. Distinguish:

1. reuse while the original source is present in the incoming history;
2. compiled-context injection when that source is absent;
3. reconstruction after actual Codex compaction;
4. rebuilding RAM after process restart.

An injection counter incremented before forwarding does not prove the backend
accepted the request. Correlate replacement and forwarding outcomes. Preserve
client-reported cumulative usage and backend usage as separate overlapping
ledgers; count internal compiler/recovery requests separately where possible.

For a controlled acceptance run, preserve exact synthetic before/after request
bodies, compiler output, source hashes, selected entries and token counts in a
protected test artifact. Production logs remain content-free. Root-only metrics
must never qualify full dependency caching again.

## 16. Implementation map and proposed work packages

### 16.1 Modules to revisit

Paths exist in the inspected checkout and the reconciled `main` tree. Verify
their current implementation on the branch chosen for the work.

| Existing module | Expected work |
|---|---|
| [`constitution/detector.py`](../src/slaif_local_coding/constitution/detector.py) | Separate envelope parsing, shell/read evidence, result pairing, span attribution and bundle observations |
| [`constitution/references.py`](../src/slaif_local_coding/constitution/references.py) | Distinguish trusted workspace normalization from unsafe external paths; support recursive graph provenance |
| [`constitution/models.py`](../src/slaif_local_coding/constitution/models.py) | File, edge, observation, version and bundle contracts with explicit unknowns |
| [`constitution/compiler_models.py`](../src/slaif_local_coding/constitution/compiler_models.py) | Bundle-aware semantic output, attribution limits and token-budget validation |
| [`constitution/compiler.py`](../src/slaif_local_coding/constitution/compiler.py) | One compilation per bundle/version/configuration, single-flight reuse, variable insertion allowances and recovery accounting |
| [`constitution/cache.py`](../src/slaif_local_coding/constitution/cache.py) | Replace the filesystem working-cache path; implement RAM entries and separate session recovery storage/interfaces |
| [`constitution/working_set.py`](../src/slaif_local_coding/constitution/working_set.py) | Token-aware selection/rendering, aggregate reserves, overlap and essential-entry policy |
| [`constitution/injection.py`](../src/slaif_local_coding/constitution/injection.py) | Transactional original-span replacement, stable references and idempotent compiled injection |
| [`constitution/pipeline.py`](../src/slaif_local_coding/constitution/pipeline.py) | Session lifecycle, graph closure, invalidation, ownership, recovery and commit ordering |
| [`config.py`](../src/slaif_local_coding/config.py) | Versioned profile, admission mode, effective-context/tokenizer contract and explicit migration of legacy settings |
| [`app.py`](../src/slaif_local_coding/app.py) | Wire the revised pipeline while preserving authenticated identity, API/SSE behavior and cancellation |

Existing tests in `test_observation.py`, `test_dependency_acquisition.py`,
`test_path_safety.py`, `test_compiler.py`, `test_cache.py`, `test_working_set.py`,
`test_injection.py`, `test_rehydration.py`, `test_pipeline.py`, `test_config.py`
and `test_app.py` are starting points, not sufficient coverage for the new
contract. Preserve useful security and pass-through controls.

### 16.2 Suggested sequence for maintainer-authored orders

These are work packages, not assigned OAP identifiers or activated orders:

1. **Architecture and contracts:** reconcile section 4, choose the decisions in
   section 18, define typed state/configuration and acceptance evidence.
2. **Real-format fixtures and detection:** use the private audit corpus to
   derive synthetic fixtures; implement tested root/read/bundle extraction.
3. **Graph and identity:** recursive raw-reference discovery, lean/greedy
   admission, namespace/version identities and overlapping-bundle invalidation.
4. **RAM and recovery:** hot-path memory store, session ownership, atomic source
   checkpoints and restart/resume rebuilding.
5. **Compiler and budgeting:** token-aware per-file/bundle allowances,
   single-flight compile-once behavior and explicit invalid/overflow states.
6. **Replacement and reconstruction:** endpoint-compatible source-span edits,
   stable references, working-set selection and transactional request commit.
7. **Telemetry and failure tests:** stage-accurate metrics, private synthetic
   provenance, accounting, cancellation and unsupported-state behavior.
8. **Real Codex acceptance:** bounded runs with unmodified ordinary read
   behavior, source changes, compaction and restart recovery. Then prepare an
   immutable product artifact for independent benchmark qualification.

The maintainer may combine or split packages, but tests of later mechanisms
must not be substituted with root-only evidence from earlier packages. Do not
modify the benchmark subject to emit specially convenient tool commands.

## 17. Acceptance and regression matrix

Each substantive mechanism needs positive and negative controls. Use synthetic
content that preserves the recorded command/envelope shape. Importing actual
private benchmark answers or raw histories into public fixtures is prohibited.

| ID | Scenario | Required evidence |
|---|---|---|
| D01 | Valid automatic `AGENTS.md` message plus environment metadata | Exact source extraction; environment excluded; correct directory scope |
| D02 | Fake marker in assistant text/tool description; malformed or duplicate envelope | No false root or arbitrary authority |
| D03 | Single relative/absolute workspace `cat` | Correct normalized path, complete content and removable span |
| D04 | `/work-other`, traversal, unknown root, quoted `cat`, heredoc write | No client-host confusion or false acquisition |
| D05 | `cat A.md B.md` without internal separators | One complete two-member bundle; no fabricated individual hashes |
| D06 | Chained reads with `ls`, labels and unrelated output | Correct outer regions; unrelated output preserved |
| D07 | Literal loop, supported wildcard evidence, explicit `workdir`/`cd` | Proven executed membership; no adapter-host expansion |
| D08 | Read succeeds, later command fails; earlier read fails, later command succeeds | Per-read evidence distinguished from global exit status |
| D09 | Truncation, partial `head`/`sed`, missing output, multi-chunk process | Explicit completeness state; no false full-file cache entry |
| D10 | Duplicate/mismatched call IDs, command substitution, unexecuted branch | No invented pairing/content; unsupported cases observable |
| G01 | Root -> A -> B, repeated links, cycles | Recursive closure, stable identity, termination |
| G02 | Relative link in nested file; ambiguous origin inside a bundle | Correct referring-directory resolution or explicit unresolved edge |
| G03 | Eligible A + unrelated B under both modes | Lean isolates/skips correctly; greedy admits whole attributable bundle |
| G04 | Unrelated file alone; no eligible member | Neither mode admits it merely because it is Markdown |
| G05 | Greedy co-cached source containing commands/claims of authority | No authority escalation or silent graph-membership promotion |
| C01 | A+B, then A alone, then identical A again | Two independent entries; singleton's third observation is a hit |
| C02 | A+B versus B+A; repeated same file in one command | Order/content identity retained; duplicate members do not inflate allowance |
| C03 | Simultaneous identical misses | One actual compiler leader; followers reuse its result |
| C04 | Changed A affecting A, A+B and A+C | Affected state invalidated; no stale/mixed-version injection |
| C05 | Old messages replayed after A-v2; later deliberate revert | Replay does not roll back state; new observations are distinguishable |
| C06 | Unknown member versions in boundaryless bundles | No invented per-file hashes or unsupported byte splicing |
| B01 | Context 262144 and 32768 with one/two-file bundles | Allowances 8192/16384 and 1024/2048, measured with the pinned tokenizer |
| B02 | Small/large files, long metadata, many ready entries | No padding; wrappers counted; aggregate context/reserves respected |
| B03 | Oversized source, truncated compile, output beyond slot | Typed failure; no valid entry or silent instruction truncation |
| B04 | Same content with changed context/tokenizer/compiler policy | Correct new identity; no incompatible compiled reuse |
| R01 | First valid acquisition and repeated original history | Original spans removed; compiled block available; no repeat compilation |
| R02 | Tool-result prefix/suffix, Unicode/CRLF, images and other items | Only intended source spans changed; tool/API/image contract preserved |
| R03 | Already transformed input, duplicate/forged/stale references | Idempotent valid output; no cross-session resolution |
| R04 | Root still present after native compaction | Cache hit/replacement works; not falsely counted as lost-root recovery |
| R05 | Source absent after history reduction, same session | Required compiled working set reconstructed without original-source reinjection |
| M01 | Many hits after initial acquisition | Zero recovery-source content reads on the normal path; zero recompile |
| M02 | Process restart, one of several sessions resumes | Only that session loaded/rebuilt; new epoch and actual compile work recorded |
| M03 | Torn/corrupt/foreign checkpoint and source-digest mismatch | Explicit recovery failure; no dangling references or contamination |
| M04 | Concurrent workers and request races | Session ownership and atomic version/checkpoint behavior hold |
| M05 | RAM pressure and session cleanup | Declared behavior; no hidden disk cache, eviction churn or governance loss |
| S01 | Different principals/sessions/repos with identical filenames/content | No cross-namespace reuse or source disclosure |
| S02 | Signed identity, malformed transforms, stream/disconnect | Existing auth, single-forwarding, SSE and cancellation contracts hold |
| O01 | Root compiled but dependencies absent | Overall dependency-cache acceptance fails or stays incomplete |
| O02 | Actual dependency acquired/compiled/replaced/injected | Exact synthetic source/entry/request evidence proves every stage |
| O03 | Compiler hit, source-absent injection and restart rebuild | Separate counters; none substituted for another |

Full request tests must verify the actual upstream body. Counter flags or
configuration values alone cannot prove removal of original content or delivery
of the correct compiled rules. Real Codex tests should include the same kinds
of compound/absolute/loop reads seen in the corpus; do not force a special
single-relative-`cat` prompt and claim general compatibility.

## 18. Decisions the maintainer must resolve explicitly

The following were not fixed by the human's ten-rule approval. Record the chosen
policies in the architecture and work orders, with tests; do not quietly invent
them in implementation:

| Decision | Constraint supplied by the approved design |
|---|---|
| Default `lean`/`greedy` mode | Both must be configurable and recorded; mode must not drift within a session |
| Working-set selection/ranking and aggregate reserve values | Per-file allowance is C/32; storage retention does not authorize unbounded injection |
| Boundaryless mixed-directory reference resolution | Never fabricate reference origin or per-file byte ownership |
| Off-graph greedy members' outgoing references | Co-caching and root reachability are distinct facts; expansion policy must be explicit |
| First standalone observation versus older unknown-member bundle | Unknown is not equal; preserve provenance and handle conflict conservatively |
| Multiple effective roots or workspace changes in one coding session | Root scope and namespace transitions must be explicit; no silent graph reset |
| Failure before any replacement versus after committed virtualization | No silent governance deletion, dangling references or hidden original-source fallback |
| Compiler infrastructure retry, if any | Bounded, attributable and separate from compile-once reuse; no best-of behavior |
| Checkpoint write/durability policy and recovery rebuild scheduling | RAM normal path; per-session originals retained; reads on restart/resume only |
| Recovery retention/encryption and actual resource-pressure limits | Confidentiality and explicit failure; effectively unlimited logical storage is not infinite RAM |
| Reference/marker wire format and model access to omitted compiled entries | The coding model must receive usable required information within context limits |

Do not reopen the approved points simply to retain the old disk-cache or
root-only implementation. Resolve engineering details within the approved
intent, and identify any genuinely incompatible requirement for human review.

## 19. Handoff and completion criteria

Before describing the rework as ready, the maintainer should deliver:

- reconciled full/compact architecture, security and configuration contracts;
- versioned implemented profile and migration behavior, with complete type/state
  definitions and endpoint support boundaries;
- synthetic real-format regression fixtures and the acceptance matrix results;
- evidence that referenced documents, including their descendants and combined
  insertions, were acquired, compiled, replaced and injected;
- per-session restart/recovery proof and zero normal-path recovery-file reads;
- actual source-change/replay/overlap handling, not only a hash-key unit test;
- stage-accurate telemetry and bounded private synthetic evidence artifacts;
- an immutable product artifact with exact source/image/compiler/tokenizer
  identities for the evaluation agent.

The subsequent benchmark must use matched CACHE-off/CACHE-on conditions with
the same client context, compaction policy, task, image policy and scoring.
Reducing a client window to roughly 40K with compaction near 32K is a proposed
way to create coding pressure, not a product-serving change or a guaranteed
CACHE benefit. Verify actual compactions, what Codex retains itself, the content
that was cached/reconstructed, and post-compaction rework. Do not assume that a
native compaction erased `AGENTS.md` or that a root-cache hit proves recovery of
the full task specifications.

Existing benchmark attempts keep their identities and outcomes. This design
document authorizes no new benchmark dispatch, release, push, publication or
protected service mutation. Its purpose is to give the maintainer the concrete
requirements and evidence needed to design the implementation work.

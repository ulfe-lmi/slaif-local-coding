# Dependency-bundle cache rework — stage ledger

**Status:** Planning ledger for the human-approved dependency-bundle cache
rework. The requirements are the ten approved rules in
[the human handoff](CACHE-REWORK.md); the resolved engineering choices are in
[the strategic implementation plan](CACHE-IMPLEMENTATION-PLAN.md). This ledger
maps every named acceptance criterion to its owning implementation stage and
records implementation/acceptance state.

This objective is the bounded architecture/documentation and
development-state stage. **No v1 runtime mechanism is implemented or
qualified yet; every runtime criterion below is `NOT RUN` (planned).** Do
not read a row in this ledger as delivered behavior. Stage-scoped synthetic
unit/fake tests prove their named mechanisms within the owning stage; they
never substitute for actual-model, genuine-Codex, native-compaction or
artifact qualification.

## Reading this ledger

Three distinct claims are tracked and must never be conflated:

- **Evidence:** the named test or sanitized evidence artifact exists and was
  executed.
- **Implementation:** the mechanism exists in product code behind a planned
  configuration profile.
- **Acceptance:** strategic review verified the evidence against the
  criterion, with current-head checks green and remote state verified.

Criterion state values are `NOT RUN`, `PENDING`, `IN PROGRESS`, `PASSED`,
`FAILED`, or `BLOCKED`. A criterion is `PASSED` only when all three claims are
satisfied for that criterion — that is, only after its own required
evidence layers pass and are reviewed. Pure/unit/fake-upstream criteria may
be proven by their named layers; actual-model, genuine-Codex, native-
compaction and artifact claims require their distinct evidence. A root-only
or counter-only result never passes a dependency criterion (O01/O02 law).
Unit/fake-upstream, actual-model, genuine-Codex, native-compaction and
artifact qualification are distinct evidence layers; none substitutes for
another.

## Acceptance criteria matrix

Owner stages (abbreviations): **OBS** = real-format read/root observation;
**GRAPH** = graph, identity and admission; **RAM** = RAM session state and
ownership; **REC** = per-session recovery; **TOK** = tokenizer, compiler and
budgets; **REP** = transactional source replacement; **ADV** = adversarial
acceptance matrix; **QUAL** = bounded real-model and genuine-Codex
qualification. All states in this stage: `NOT RUN` (planned).

### Detection and acquisition (D)

| ID | Scenario | Owning stage | Required evidence (abridged) | State |
|---|---|---|---|---|
| D01 | Valid automatic `AGENTS.md` message plus environment metadata | OBS | Exact source extraction; environment excluded; correct directory scope | NOT RUN |
| D02 | Fake marker in assistant text/tool description; malformed or duplicate envelope | OBS | No false root or arbitrary authority | NOT RUN |
| D03 | Single relative/absolute workspace `cat` | OBS | Correct normalized path, complete content, removable span | NOT RUN |
| D04 | `/work-other`, traversal, unknown root, quoted `cat`, heredoc write | OBS | No client-host confusion or false acquisition | NOT RUN |
| D05 | `cat A.md B.md` without internal separators | OBS | One complete two-member bundle; no fabricated individual hashes | NOT RUN |
| D06 | Chained reads with `ls`, labels and unrelated output | OBS | Correct outer regions; unrelated output preserved | NOT RUN |
| D07 | Literal loop, supported wildcard evidence, explicit `workdir`/`cd` | OBS | Proven executed membership; no adapter-host expansion | NOT RUN |
| D08 | Read succeeds, later command fails; earlier read fails, later command succeeds | OBS | Per-read evidence distinguished from global exit status | NOT RUN |
| D09 | Truncation, partial `head`/`sed`, missing output, multi-chunk process | OBS | Explicit completeness state; no false full-file cache entry | NOT RUN |
| D10 | Duplicate/mismatched call IDs, command substitution, unexecuted branch | OBS | No invented pairing/content; unsupported cases observable | NOT RUN |

### Graph, admission and identity (G, C)

| ID | Scenario | Owning stage | Required evidence (abridged) | State |
|---|---|---|---|---|
| G01 | Root → A → B, repeated links, cycles | GRAPH | Recursive closure, stable identity, termination | NOT RUN |
| G02 | Relative link in nested file; ambiguous origin inside a bundle | GRAPH | Correct referring-directory resolution or explicit unresolved edge | NOT RUN |
| G03 | Eligible A + unrelated B under both modes | GRAPH | Lean isolates/skips correctly; greedy admits whole attributable bundle | NOT RUN |
| G04 | Unrelated file alone; no eligible member | GRAPH | Neither mode admits it merely because it is Markdown | NOT RUN |
| G05 | Greedy co-cached source containing commands/claims of authority | GRAPH | No authority escalation or silent graph-membership promotion | NOT RUN |
| C01 | A+B, then A alone, then identical A again | GRAPH | Two independent entries; singleton's third observation is a hit | NOT RUN |
| C02 | A+B versus B+A; repeated same file in one command | GRAPH | Order/content identity retained; duplicate members do not inflate allowance | NOT RUN |
| C03 | Simultaneous identical misses | RAM/TOK | One actual compiler leader; followers reuse its result | NOT RUN |
| C04 | Changed A affecting A, A+B and A+C | GRAPH | Affected state invalidated; no stale/mixed-version injection | NOT RUN |
| C05 | Old messages replayed after A-v2; later deliberate revert | GRAPH | Replay does not roll back state; new observations are distinguishable | NOT RUN |
| C06 | Unknown member versions in boundaryless bundles | GRAPH | No invented per-file hashes or unsupported byte splicing | NOT RUN |

### Token budgets (B)

| ID | Scenario | Owning stage | Required evidence (abridged) | State |
|---|---|---|---|---|
| B01 | Context 262144 and 32768 with one/two-file bundles | TOK | Allowances 8192/16384 and 1024/2048, measured with the pinned tokenizer | NOT RUN |
| B02 | Small/large files, long metadata, many ready entries | TOK | No padding; wrappers counted; aggregate context/reserves respected | NOT RUN |
| B03 | Oversized source, truncated compile, output beyond slot | TOK | Typed failure; no valid entry or silent instruction truncation | NOT RUN |
| B04 | Same content with changed context/tokenizer/compiler policy | TOK | Correct new identity; no incompatible compiled reuse | NOT RUN |

### Replacement and reconstruction (R)

| ID | Scenario | Owning stage | Required evidence (abridged) | State |
|---|---|---|---|---|
| R01 | First valid acquisition and repeated original history | REP | Original spans removed; compiled block available; no repeat compilation | NOT RUN |
| R02 | Tool-result prefix/suffix, Unicode/CRLF, images and other items | REP | Only intended source spans changed; tool/API/image contract preserved | NOT RUN |
| R03 | Already transformed input, duplicate/forged/stale references | REP | Idempotent valid output; no cross-session resolution | NOT RUN |
| R04 | Root still present after native compaction | REP | Cache hit/replacement works; not falsely counted as lost-root recovery | NOT RUN |
| R05 | Source absent after history reduction, same session | REP | Required compiled working set reconstructed without original-source reinjection | NOT RUN |

### RAM and recovery (M)

| ID | Scenario | Owning stage | Required evidence (abridged) | State |
|---|---|---|---|---|
| M01 | Many hits after initial acquisition | RAM | Zero recovery-source content reads on the normal path; zero recompile | NOT RUN |
| M02 | Process restart, one of several sessions resumes | REC | Only that session loaded/rebuilt; new epoch and actual compile work recorded | NOT RUN |
| M03 | Torn/corrupt/foreign checkpoint and source-digest mismatch | REC | Explicit recovery failure; no dangling references or contamination | NOT RUN |
| M04 | Concurrent workers and request races | RAM/REC | Session ownership and atomic version/checkpoint behavior hold | NOT RUN |
| M05 | RAM pressure and session cleanup | RAM | Declared behavior; no hidden disk cache, eviction churn or governance loss | NOT RUN |

### Isolation and whole-rework acceptance (S, O)

| ID | Scenario | Owning stage | Required evidence (abridged) | State |
|---|---|---|---|---|
| S01 | Different principals/sessions/repos with identical filenames/content | ADV | No cross-namespace reuse or source disclosure | NOT RUN |
| S02 | Signed identity, malformed transforms, stream/disconnect | ADV | Existing auth, single-forwarding, SSE and cancellation contracts hold | NOT RUN |
| O01 | Root compiled but dependencies absent | ADV/QUAL | Overall dependency-cache acceptance fails or stays incomplete | NOT RUN |
| O02 | Actual dependency acquired/compiled/replaced/injected | ADV/QUAL | Exact synthetic source/entry/request evidence proves every stage | NOT RUN |
| O03 | Compiler hit, source-absent injection and restart rebuild | ADV/QUAL | Separate counters; none substituted for another | NOT RUN |

## Planned objective succession

One numeric objective = one PR. Continuations use the same number/branch/PR and
the next valid suffix (`b..z`, then `aa..zz`). Only after independent strategic
acceptance, all current-head required checks, merge and remote-main
verification may the next objective activate. Future orders remain inert
drafts until activated.

| Objective | PR branch | Deliverable and gate | Status in this round |
|---|---|---|---|
| 016 | `oap/016-cache-rework-contracts` | Commit unchanged human handoff; reconcile both architectures, root/strategic agent law, security/testing/configuration docs; publish the plan and this stage ledger; establish the separate current-development provenance contract (development-state artifact validation under the intact RC10 publication freeze). No adapter-runtime implementation claim. | Continuing (016-b) |
| 017 | `oap/017-cache-read-observation` | Versioned pure root/read/result/span evidence and real-format synthetic fixtures: D01–D10, Unicode/CRLF, bounds, no shell execution. Preserve legacy detector until integration. | Planned (inert draft) |
| 018 | `oap/018-cache-graph-bundles` | Typed namespace/file/edge/bundle versions, recursive graph, lean/greedy admission, overlap/replay invalidation: G01–G05, C01/C02/C04–C06, S01. | Planned (inert draft) |
| 019 | `oap/019-cache-ram-state` | RAM session ownership/indexes, explicit capacity/backpressure, async single-flight and lifecycle: C03, M01/M04/M05; zero filesystem hot lookup. | Planned (inert draft) |
| 020 | `oap/020-cache-session-recovery` | Protected exact-original atomic checkpoints, locks and lazy per-session restart rebuilding: M02–M04, corrupt/torn/foreign/config-mismatch negatives. | Planned (inert draft) |
| 021 | `oap/021-cache-token-compiler` | Pinned actual tokenizer, typed bundle compiler, C/32 slots, aggregate/reserves and deterministic selection: B01–B04, compiler cancellation/failure/no-retry/compile-once. | Planned (inert draft) |
| 022 | `oap/022-cache-source-replacement` | Explicit opt-in config and endpoint/application integration, transactional root/tool source edits, stable references and source-absent reconstruction: R01–R05, S01/S02; upstream-body proof. | Planned (inert draft) |
| 023 | `oap/023-cache-adversarial-acceptance` | Complete stage-accurate telemetry and fake full-stack adversarial/lifecycle/isolation/cancellation matrix; all D/G/C/B/R/M/S/O criteria mapped without substitution; runtime/docs/package regressions. | Planned (inert draft) |
| 024 | `oap/024-cache-real-codex-qualification` | Bounded actual-model and genuine-Codex dependency/bundle/vision/history-reduction/restart acceptance; source-change/replay proof; measured normal-path zero disk reads and overhead; immutable development artifact handoff for independent benchmark. No benchmark dispatch, release, service/profile mutation or deployment. | Planned (inert draft) |

Stage acceptance never substitutes for later delivery. In particular, a
recognized root with absent dependencies fails overall cache-rework
acceptance (O01). Each stage may receive same-PR remediation suffixes. The
final qualification must state exactly which actual compaction behavior was
observed; adapter-boundary history reduction is not native Codex compaction
proof.

## Historical baseline: RC10

The rework is measured against, and deliberately changes, the behavior frozen
in the historical private candidate `0.1.0-rc10` (OCI digest
`sha256:5a02e0043fcc65e5dc5a78f3e2a8648a16c93620255e904e394c926b18c92960`,
image source `1a04528223445e4249fad6d24a71151fd1dc1a09`, measured client
`0.149.0`). RC10 is the **historical baseline only**: its records, tags and
benchmark outcomes are immutable, and none of its evidence is rework
acceptance. The zero-observation/zero-included-dependency CACHE results
described in the handoff are the motivation for this rework, not a rework
result. RC10's additive injection, filesystem-derived cache and
process-local rehydration remain the explicitly named **legacy** behavior
until the v1 migration is qualified.

## Source provenance

The private history audit that motivated this rework is named
`markdown-read-audit-20261018-a01` (sealed content digest
`a6021bb9019f3c4d3136ea90ced1ee727bb983771b2328634faf6b0ab55059df`). The
corpus itself, its task answers and its raw histories remain outside this
repository; only sanitized fixtures derived from its recorded command and
envelope shapes may enter tests.

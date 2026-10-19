# Dependency-bundle cache rework — stage ledger

**Status:** Planning ledger for the human-approved dependency-bundle cache
rework. The requirements are the ten approved rules in
[the human handoff](CACHE-REWORK.md); the resolved engineering choices are in
[the strategic implementation plan](CACHE-IMPLEMENTATION-PLAN.md). This ledger
maps every named acceptance criterion to its owning implementation stage and
records implementation/acceptance state.

This objective is the bounded pure-observation stage (017). **No v1
runtime mechanism is active in the adapter and none is qualified; every
runtime criterion below is still `NOT RUN` (planned).** Stage 017-a has
landed the D01-D05 slice as inert, typed, pure modules under
`src/slaif_local_coding/constitution/bundles/` with the named evidence
recorded below; those rows are `PENDING` strategic acceptance, not
delivered behavior. The 017-a COMPLETE claim was **not accepted**: an
independent synthetic observer probe at the final report head failed 14 of
23 cases (findings A-E: real-format wrapper, read-grammar membership,
per-call cwd, tool/endpoint evidence, Unicode/bounds and parser bounds, plus
the diverging normative compact mirror). Stage 017-b corrects exactly those
bounded defects on the same PR with direct regression tests; it adds no new
read families. The 017-b COMPLETE claim was **not accepted** as completion
of the A-E contract: separate read-only private-clone probes directly at
the final 017-b report head failed 10 of 16 literal-argv-semantics cases
and 3 of 5 actual-endpoint-selection cases (quoted option/terminator/stdin
false membership, NBSP false split, malformed-workdir
`UnicodeEncodeError`, exact member-limit off-by-one, raw helper repr, and
ambiguous mixed containers acquiring content without a proven actual
endpoint). Stage 017-c corrects exactly those bounded defects on the same
PR with direct regression tests; it adds no new read families. The
017-c COMPLETE claim was **not accepted** as endpoint-authority
completion: a separate independent root-context probe at the final 017-c
report head passed 2 of 6 cases (explicit Chat, mixed and invalid
endpoints still minted valid Responses roots from unused input, and a
Responses string input plus a Chat pair was treated as unambiguous Chat).
Stage 017-d first corrects that bounded root-domain prerequisite (root
observation scoped to the actual selected Responses domain; string-input
plus messages is a mixed shape) as an independently committed
prerequisite, then earns the finite read-plan surface D06/D07/D08 (all-
cat / literal-cd `&&` plans, absolute literal `cd` transitions, bounded
literal `echo` outer boundaries, per-read versus global exit evidence,
whole-plan bounds) in the inert module
`src/slaif_local_coding/constitution/bundles/compound_reads.py`
(grammar `literal-read-plan/v1`); it adds no graph/cache/compiler/app
integration. D09/D10 (multi-chunk process completion proof, remaining
truncation matrix) move to a later same-PR suffix (planned 017-e).
Objective 016 (the architecture/documentation and
development-state stage) is accepted and merged as PR #24, merge
`96c790423f6f0097a56a0b12bacda8a9b6da6aba`. Do not read a row in this
ledger as delivered behavior. Stage-scoped synthetic unit/fake tests prove
their named mechanisms within the owning stage; they never substitute for
actual-model, genuine-Codex, native-compaction or artifact qualification.

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
qualification. States in this stage: D01-D05 are `PENDING` (pure observation slice; named evidence below, strategic acceptance outstanding); every other criterion is `NOT RUN` (planned).

### Detection and acquisition (D)

| ID | Scenario | Owning stage | Required evidence (abridged) | State |
|---|---|---|---|---|
| D01 | Valid automatic `AGENTS.md` message plus environment metadata | OBS | Exact source extraction; environment excluded; correct directory scope | 017-a evidence: tests/test_bundle_root_envelopes.py::test_real_format_canonical_fixture_parses_with_exact_bytes, ::test_adjacent_environment_tail, ::test_newline_separated_environment_tail, ::test_separate_item_environment_is_excluded, ::test_crlf_envelope_preserves_crlf_content_bytes; tests/test_bundle_observe.py::test_every_fixture_is_synthetic_and_versioned; 017-b regression: tests/test_bundle_root_envelopes.py::TestLabelByteBound (UTF-8 byte label bound) | PENDING
| D02 | Fake marker in assistant text/tool description; malformed or duplicate envelope | OBS | No false root or arbitrary authority | 017-a evidence: tests/test_bundle_root_envelopes.py::test_assistant_envelope_never_creates_root, ::test_marker_prose_at_later_offset_is_not_a_root, ::test_tool_output_envelope_is_not_a_root, ::test_unclosed_tail_is_typed, ::test_nested_duplicate_opening_marker_is_typed, ::test_duplicate_closing_tag_in_tail_is_typed, ::test_invalid_labels_and_delimiters_are_typed, ::test_valid_root_coexists_with_observable_malformed_occurrence | PENDING
| D03 | Single relative/absolute workspace `cat` | OBS | Correct normalized path, complete content, removable span | 017-a evidence: tests/test_bundle_read_grammar.py::test_single_relative_operand, ::test_dash_dash_separator, ::test_absolute_workspace_operands; tests/test_bundle_client_paths.py::test_relative_against_evidenced_workspace, ::test_simple_absolute_under_workspace, ::test_unicode_path_preserved; tests/test_bundle_tool_results.py::test_single_complete_read, ::test_empty_file_is_complete_empty_version, ::test_unicode_crlf_bytes_are_exact; 017-b regression: tests/test_bundle_read_grammar.py::TestTerminatorMembership, ::TestCallArgumentShapes; tests/test_bundle_tool_results.py::TestPerCallWorkdir; 017-c regression: tests/test_bundle_read_grammar.py::TestQuotedOptionSemantics (quoted option/terminator/stdin), ::TestNonAsciiWhitespaceNotASeparator, ::TestExactOperandLimit, ::TestCallArgumentShapes (repr privacy, documented raw-argument cap), tests/test_bundle_shell_tokens.py (raw spans/cooked values/quoting/operators, repr privacy, no shell facilities), tests/test_bundle_client_paths.py::TestMalformedUnicodeAndSpaces | PENDING
| D04 | `/work-other`, traversal, unknown root, quoted `cat`, heredoc write | OBS | No client-host confusion or false acquisition | 017-a evidence: tests/test_bundle_client_paths.py::test_sibling_prefix_is_outside, ::test_lexical_dotdot_escaping_is_traversal, ::test_outside_absolute_path, ::test_absolute_with_unknown_workspace, ::test_relative_without_workspace_is_unproven, ::test_relative_traversal_escape, ::test_fully_quoted_literal_operand_under_no_spaces_convention, ::test_url_fragment_is_literal_never_stripped, ::test_query_syntax_is_never_mapped_to_the_plain_file, ::test_module_imports_no_filesystem_or_shell_facilities; tests/test_bundle_read_grammar.py::test_unsupported_shapes_are_typed_never_complete, ::test_no_expansion_no_evaluation; tests/test_bundle_observe.py::test_logical_root_scope_never_maps_host_paths, ::test_no_context_at_all_is_unproven; 017-b regression: tests/test_bundle_tool_results.py::TestPerCallWorkdir::test_per_call_workdir_outside_workspace_is_not_complete, ::test_relative_workdir_is_typed_not_complete, ::TestMalformedUnicodeComposition (typed, non-crashing, non-removable); 017-c regression: tests/test_bundle_tool_results.py::TestMalformedWorkdirUnicode (surrogate per-call workdir typed `MALFORMED_UNICODE`, relative and absolute operand variants, no crash/placeholder digest) | PENDING
| D05 | `cat A.md B.md` without internal separators | OBS | One complete two-member bundle; no fabricated individual hashes | 017-a evidence: tests/test_bundle_read_grammar.py::test_two_operands_in_order, ::test_repeated_operand_preserves_order; tests/test_bundle_tool_results.py::test_two_members_without_separators_is_one_ordered_bundle, ::test_reversed_order_changes_observed_member_order, ::test_repeated_operands_do_not_fabricate_files; tests/test_bundle_observation_models.py::test_two_member_bundle_has_unknown_member_digests, ::test_single_member_complete_read_carries_proven_digest, ::test_requested_and_proven_executed_are_distinct; 017-b regression: tests/test_bundle_tool_results.py::TestRealFormatWrapper (handoff `Chunk ID:` + earned variant), ::TestContradictoryWrapperStatus, ::TestWrapperBoundsAndGrammar, ::TestToolEligibilityEvidence, ::TestEndpointScopedPairing; fixture tests/fixtures/cache_bundles/v1/read_handoff_wrapper_format_responses.json; 017-c regression: tests/test_bundle_tool_results.py::TestEndpointSelection (mixed shapes typed non-removable, unambiguous positives, explicit endpoint scoping, global/per-read agreement), tests/test_bundle_observe.py::TestEndpointDomainAtComposition | PENDING
| D06 | Chained reads with `ls`, labels and unrelated output | OBS | Correct outer regions; unrelated output preserved | 017-d evidence: tests/test_bundle_compound_reads.py::TestChainedReadPlans (all-cat `&&` plans, one ordered bundle, order/duplicate preservation), ::TestEchoOuterBoundaries (literal echo prefix/suffix, internal-echo negative), ::TestMixedOutputNegatives (`ls` family exit-zero/nonzero, semicolon chain), ::TestOuterRegionComposition (pure file span exposure, label-inside-source, collision/extra-output typed); outer-region proof in ::TestOuterSourceRegions | PENDING
| D07 | Literal loop, supported wildcard evidence, explicit `workdir`/`cd` | OBS | Proven executed membership; no adapter-host expansion | 017-d evidence (loop/wildcard remain explicitly typed unsupported in this slice): tests/test_bundle_compound_reads.py::TestLiteralCdTransitions (absolute literal `cd` under evidenced workspace, sibling/ancestor/`..`/relative/bare/multi-target negatives, per-call workdir precedence, mid-chain failure), ::TestPlanNegatives (loop/branch/glob/substitution typed, later words never reinterpreted), ::TestWholePlanBounds (whole-plan statement/operand bounds); composition: ::TestChainedPlanComposition::test_cd_then_reads_resolves_against_transition, ::test_per_call_workdir_then_cd_transition | PENDING
| D08 | Read succeeds, later command fails; earlier read fails, later command succeeds | OBS | Per-read evidence distinguished from global exit status | 017-d evidence: tests/test_bundle_compound_reads.py::TestPerReadVersusGlobalExit (nonzero chain proves no read and no digest, requested members preserved, wrapper status recorded; earlier-failure/later-success; truncated chain; process-running; malformed-Unicode content; chat composition; mixed suppression) | PENDING
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
| 016 | `oap/016-cache-rework-contracts` | Commit unchanged human handoff; reconcile both architectures, root/strategic agent law, security/testing/configuration docs; publish the plan and this stage ledger; establish the separate current-development provenance contract (development-state artifact validation under the intact RC10 publication freeze). No adapter-runtime implementation claim. | Merged (PR #24; merge `96c790423f6f0097a56a0b12bacda8a9b6da6aba`; accepted) |
| 017 | `oap/017-cache-read-observation` | Versioned pure root/read/result/span evidence and real-format synthetic fixtures: D01–D10, Unicode/CRLF, bounds, no shell execution. Preserve legacy detector until integration. | In progress (017-a..017-c published but not accepted; 017-b corrected findings A-E; 017-c corrected literal-grammar/endpoint proof; 017-d corrects the root-domain prerequisite as an independent commit and earns D06/D07/D08 finite read plans in the inert module `compound_reads.py`, `PENDING` acceptance; D09/D10 planned for later same-PR suffix 017-e) |
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

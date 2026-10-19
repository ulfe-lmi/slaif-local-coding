# OAP Coding-Agent Report — 017-d

## Work order
- Order: `oap/orders/017-d-root-domain-and-finite-read-plans.md`
  (objective 017, round 017-d, AMEND_EXISTING_PR), SHA256
  `7bda660d4190a226fc11ed82abe5701126af588a30f316f4a01c3aa839a53020`;
  `oap/active` = `017-d` (bytes `017-d\n`, SHA256
  `5194d511f3c9d2e7659bd1e437c66ccac2573e41d4e14f754a5aebe712551632`);
  both committed unchanged with the first implementation commit A1
  (activation bytes preserved, not edited).
- PR mode: AMENDED_EXISTING_PR — exact OPEN PR #25
  https://github.com/ulfe-lmi/slaif-local-coding/pull/25, base `main`,
  head branch `oap/017-cache-read-observation`. NO NEW PR; no coding
  merge or auto-merge.
- Starting remote PR/report head verified before mutation:
  `7abe503f452502da55bd510ebc3dc0967aa7e3b5` (sole parent
  `ad65077e88945e6511410d4395de650403247ed0`); remote `main`
  `96c790423f6f0097a56a0b12bacda8a9b6da6aba` (unchanged); local working
  tree clean at round start.
- Round start baselines (strategic, unchanged):
  `probes/check-bundle-observation.py` 23/23,
  `probes/check-read-option-semantics.py` 16/16,
  `probes/check-endpoint-selection.py` 5/5 at the 017-c final SELF, all
  with valid positive controls; the new
  `probes/check-root-endpoint-context.py` (6 cases) = 2 PASS / 4 FAIL at
  the 017-c final SELF (`reviews/017-c-final-root-context-probes.json`).

## Status
COMPLETE for the bounded 017-d slice (actual endpoint-domain root
gating plus the finite read-plan surface D06/D07/D08 in the inert
`src/slaif_local_coding/constitution/bundles/` package) — a claim for
strategic review, not acceptance. Objective 017 as a whole (D01-D10)
remains open: D09/D10 (literal loops, multi-chunk process pairing and
the remaining truncation matrix) move to the later same-PR suffix
017-e per this order. The bundles modules remain inert: not active in
the adapter, legacy detector unchanged. All v1 runtime criteria remain
NOT RUN.

## Executive summary
1. Actual domain gates (committed first as prerequisite A1 so its proof
   is independently identifiable): only the actual selected Responses
   domain can establish a root from its own user `input_text`
   container; explicit Chat never borrows root authority from ignored
   Responses input; mixed/unknown/invalid actual endpoints yield no
   valid-root occurrence eligible for later graph/cache admission even
   when a root-shaped object sits in an unused field (root-kind
   occurrences are demoted: status unsupported, digest `None`,
   `UNSUPPORTED_ENDPOINT` reason; result `UNSUPPORTED` with
   `UNSUPPORTED_ENDPOINT` in conflicts); string-form Responses input —
   a valid Responses API form — has no item container and yields no
   root occurrence; inference no longer treats input-string plus
   messages as unambiguous Chat (mixed without context is typed); the
   contradictory "root scanning independent of endpoint selection"
   comment/contract is removed; input immutability and valid
   inferred/explicit Responses positives preserved.
2. Finite read plans (D06/D07/D08, commit A2) in the new pure module
   `compound_reads.py` (`literal-read-plan/v1`), built on the corrected
   literal lexer/path normalization and per-call cwd — a finite typed
   plan, no general shell interpreter, no new dependencies:
   - Exact unquoted `&&` separators; `cat` under the shared option law;
     `cd` with exactly one clean literal absolute directory inside the
     evidenced workspace (sibling/ancestor/`..`/relative/bare/
     multi-target forms typed unsupported); `echo` with exactly one
     clean fully-quoted literal. Whole-plan bounds (characters,
     statements, operands) with one shared cat-operand budget — no
     per-segment multiplication loophole.
   - Explicit supported workdir takes precedence over the batch
     default; the literal `cd` transition then affects following reads
     (no host cwd/stat/resolve/eval/glob/environment expansion).
   - A recognized all-cat/literal-cd `&&` plan ending with proven exit
     0 and untruncated complete output proves each required read and
     is one ordered bundle with an exact whole-region digest; member
     digests stay `None` (never fabricated per-file hashes); duplicate
     operand order and distinct slot width preserved; statement/operand
     order (not lexical call IDs) bound.
   - Per-read vs global exit (D07/D08 law): a global nonzero in an
     `&&` chain identifies no failed read and proves no earlier source
     complete; a later success in a semicolon/mixed chain does not
     prove an earlier `cat`; unknown branch/control flow stays typed;
     later command words are never reinterpreted as requested cat
     filenames; nonzero/partial/truncated/unproven source is
     non-removable with no valid bundle digest; original
     wrapper/global status preserved; no per-command exit metadata
     invented or inferred.
   - Outer source regions (D08): the earned positive case uses
     deterministic literal `echo` prefix/suffix output — only the pure
     file-source span is exposed at its proven position and a label
     inside source stays source; where the outer boundary is unproven
     all bytes are retained with a fixed observable limitation
     (`OUTER_BOUNDARY_UNPROVEN` / typed) — listing rows/diagnostics
     are never swallowed into a file bundle and a complete execution
     alone is never an attributable span.
3. All four unchanged strategic probes pass at the implementation head
   `a29d4144098ba289c06d785d258cd48f1e473439`: 23/23, 16/16, 5/5, 6/6
   (50/50; valid positive controls); the root-context probe went from
   2/6 at the 017-c head to 6/6. All four also passed 50/50 at the A1
   prerequisite head (proof recorded before A2 was built).
4. 95 new focused tests (381 total across `tests/test_bundle_*.py`):
   10 root-domain gating cases in `test_bundle_observe.py` (A1) plus
   the new 85-case `tests/test_bundle_compound_reads.py` suite (A2).
   27 standing fixture/live-layer skips honestly reported; full locked
   gate green locally (1924 passed); development artifacts
   byte-reproducible from the clean `git archive` of source commit A2
   in a fresh venv, verified by a fresh non-editable install smoke
   exercising legacy Chat reads, the earned compound plan, and the new
   root-domain gate.
5. Docs/contracts updated in the same PR: observation contract (plan
   grammar, vocabulary, bounds), stage ledger (D06/D07/D08 named tests
   PENDING acceptance), TESTING.md, both architecture maps with the
   byte-identical compact mirror, `ARCHITECTURE.md` stage sentence,
   development provenance manifest B, PR #25 description.

## Authoritative GitHub state
- PR #25: OPEN, mergeable, base `main`, head branch
  `oap/017-cache-read-observation` (reconciled before mutation and
  re-verified after push).
- New PR created: NO. Existing PR amended: YES. Merge/auto-merge: NO.
- Commits published this round (all on PR #25):
  - A1 = `fcfdf4017a46d888e8f74610be3396c9c9e6d240` — "017-d: gate
    root observation on the actual selected endpoint domain" (5 files:
    `observe.py`, `test_bundle_observe.py`,
    `docs/CACHE-OBSERVATION-CONTRACT.md`, activated order +
    `oap/active` with unchanged activation bytes) — the order-required
    independently identifiable prerequisite commit.
  - A2 = `9aeb2e583522476da69e74bcb156a2a4f475b4b8` — "017-d: earn
    finite read plans with outer attribution (D06/D07/D08)" (12 files,
    +1751/-50: 4 source modules + 1 new, 1 new test, contract, ledger,
    TESTING, `ARCHITECTURE.md`, both architecture maps incl.
    byte-identical mirror).
  - B = `a29d4144098ba289c06d785d258cd48f1e473439` — "017-d: refresh
    development provenance manifest" (manifest-only;
    `frozen_publication` and release sections unchanged) — the
    implementation head (source A2 -> manifest B contract).
- Remote branch and PR head both equal B at publication time; remote
  `main` still `96c790423f6f0097a56a0b12bacda8a9b6da6aba`.

Implementation head SHA: a29d4144098ba289c06d785d258cd48f1e473439
Report publication commit: SELF

## Changes and files (A1 +345/-25; A2 +1751/-50; B manifest-only)
Source (`src/slaif_local_coding/constitution/bundles/`):
- `observe.py` (A1): `select_endpoint` — Responses container present
  for both list and string `input`; input-string plus Chat `messages`
  is `mixed`, never unambiguous Chat. Root observation scoped to the
  actual selected domain: only `responses` scans roots; string-form
  Responses input yields `NO_ROOT`/0 scanned; every other selection
  demotes any root-kind `ok` occurrence to unsupported (digest
  `None`, `UNSUPPORTED_ENDPOINT`) with result `UNSUPPORTED` and
  `UNSUPPORTED_ENDPOINT` in conflicts; Chat-only payloads unchanged
  (no occurrences); the contradictory endpoint-independence
  comment/contract removed.
- `compound_reads.py` (A2, new, 508 lines): `READ_PLAN_GRAMMAR =
  "literal-read-plan/v1"`; `PlanStatementKind` / `PlanStatement` /
  `ReadPlanParse`; `parse_read_plan(...)` — exact unquoted `&&`
  separators, `cat` under the shared option law (reusing
  `parse_cat_operands` with `stop_at_operator=True` so later-command
  words are never reinterpreted as cat files), `cd` (exactly one clean
  literal absolute directory inside the evidenced workspace), `echo`
  (exactly one clean fully-quoted literal); whole-plan bounds
  (`max_command_chars` characters, shared cat-operand budget and
  statement count `<= max_operands`); multi-statement
  structurally-mixed plans and internal `echo` are
  `OUTER_BOUNDARY_UNPROVEN`; no `cat` plus no statement reasons is
  `COMMAND_UNSUPPORTED`. `plan_source_region(...)` proves the
  attributable middle span by exact prefix/suffix anchoring
  (`echo` literal + `"\n"` in statement order) with `startswith` /
  `endswith` — collision or unknown boundary is typed, never guessed.
- `read_grammar.py` (A2): extracted
  `parse_cat_operands(..., stop_at_operator=False)`; single-command
  `parse_read_command` behavior unchanged (default `False`); plan call
  sites use `True`.
- `tool_results.py` (A2): `_build_observation` routes an incomplete
  single parse to `parse_read_plan`; plan-incomplete observations are
  UNSUPPORTED with `plan.reasons` and `requested_members =
  plan.requested_members`; a complete clean plan with a proven outer
  region is COMPLETE as one ordered bundle (`content_span` offset into
  the wrapper output region, `bundle_digest` = SHA-256 of the exact
  middle span, single distinct member proves its digest, others
  `None`); unproven wrapper/region keeps NONZERO_EXIT/PARTIAL etc.
  with no proven span and no digest (no per-command exit metadata
  invented).
- `observation_models.py` (A2): `Limitation` additions
  `CD_TARGET_UNSUPPORTED`, `ECHO_TARGET_UNSUPPORTED`,
  `OUTER_BOUNDARY_UNPROVEN`.
- `__init__.py` (A2): exports for the plan API.

Tests (95 new this round):
- `tests/test_bundle_observe.py` (A1, +10): `TestRootDomainGating` —
  inferred/explicit Responses positives preserved; explicit Chat,
  mixed-without-endpoint and invalid-explicit-endpoint cannot mint
  roots from unused input; malformed root in unused container stays
  typed; Chat-only payload root result unchanged; string input plus
  messages is mixed not Chat; string input alone is Responses without
  a root container; input not mutated under root gating.
- `tests/test_bundle_compound_reads.py` (A2, new, 85):
  `TestChainedReadPlans` (all-cat `&&` plans, one ordered bundle,
  order/duplicate preservation, reversed/one-over/exact-limit,
  Unicode/CRLF/empty sources), `TestLiteralCdTransitions` (absolute
  literal `cd` under evidenced workspace, sibling/ancestor/`..`/
  relative/bare/multi-target negatives, per-call workdir precedence,
  mid-chain failure), `TestEchoOuterBoundaries` (literal echo
  prefix/suffix, internal-echo negative), `TestPlanNegatives` (loop/
  branch/glob/substitution/pipe/redirection typed; later words never
  reinterpreted), `TestWholePlanBounds` (whole-plan statement/operand
  bounds), `TestOuterSourceRegions` (prefix/suffix proof by exact
  anchoring, collision/extra-output typed, zero-byte middle),
  `TestChainedPlanComposition` and `TestOuterRegionComposition`
  (public `observe_request` composition incl. cd-then-reads and
  per-call-workdir-then-cd), `TestMixedOutputNegatives` (`ls` family
  exit-zero/nonzero, semicolon chains), `TestPerReadVersusGlobalExit`
  (nonzero chain proves no read and no digest with requested members
  preserved and wrapper status recorded; earlier-failure/later-success;
  truncated chain; process-running; malformed-Unicode content; chat
  composition; mixed suppression).

Docs/contracts:
- `docs/CACHE-OBSERVATION-CONTRACT.md`: status/version table, module
  list, new plan-grammar section (separators, `cat`/`cd`/`echo`
  forms, whole-plan bounds, outer-region attribution law, per-read vs
  global exit law), expanded limitation vocabulary, root-domain law
  (actual selected endpoint scopes root/call/result containers;
  string-form Responses input has no root container), deferred scope
  narrowed to D09/D10 for 017-e.
- `docs/CACHE-REWORK-LEDGER.md`: header 017-d text; D06/D07/D08 rows
  NOT RUN -> PENDING with the exact named test evidence (stage states
  remain PENDING acceptance); 017 succession row updated.
- `TESTING.md`: stage-017 paragraph (focused suite list, umask 022
  note, probe set).
- `ARCHITECTURE.md`: one-sentence 017-d stage qualification
  (root-domain gate + D06-D08 inert; D09-D10 to 017-e).
- `ARCHITECTURE-for-agents.md` + byte-identical mirror
  `oap/strategic-instructions/ARCHITECTURE-for-agents.md` (verified
  with `cmp`): objective boundaries + read-observation bullet.
- `oap/orders/017-d-root-domain-and-finite-read-plans.md` +
  `oap/active` (A1): activated order committed unchanged.
- `packaging/dev_provenance_manifest.json` (B): refreshed development
  manifest bound to source A2 (183 inputs = 181 + `compound_reads.py`
  + its test; frozen-publication constants unchanged).

## Acceptance evidence (order requirement -> behavior -> named
regressions)
| Order requirement | Earned behavior | Named regressions (all PASSED) |
| --- | --- | --- |
| Only actual selected Responses domain establishes roots | `select_endpoint` list-or-string Responses; `observe_request` root scan scoped to selection | `TestRootDomainGating::test_inferred_responses_root_positive_preserved`, `::test_explicit_responses_root_positive_preserved`, `::test_string_input_alone_is_responses_without_root_container` |
| Explicit Chat never borrows root authority | explicit Chat: result UNSUPPORTED, no valid-root occurrence, root-kind demoted (digest None + UNSUPPORTED_ENDPOINT) | `::test_explicit_chat_cannot_mint_root_from_unused_input` |
| Mixed/unknown/invalid yield no admissible root | typed unsupported result, conflicts prepend UNSUPPORTED_ENDPOINT, malformed root in unused container stays typed | `::test_mixed_without_endpoint_cannot_mint_root`, `::test_invalid_explicit_endpoint_cannot_mint_root`, `::test_malformed_root_in_unused_container_stays_typed` |
| String input + messages not unambiguous Chat | inference returns `mixed` without context | `::test_string_input_with_chat_messages_is_mixed_not_chat` |
| Input immutability / Chat-only unchanged | payload not mutated under root gating; Chat-only root result unchanged | `::test_input_not_mutated_under_root_gating`, `::test_chat_only_payload_root_result_unchanged` |
| Earn `cat A && cat B` / `cat A B && cat C` / `cd /work && cat A B` / `cd /work/sub && cat A ../B` under evidenced `/work` | one ordered bundle, exact whole-region digest, member digests None, order/duplicate/slot exact | `TestChainedReadPlans::test_two_cat_statements_are_earned`, `::test_multi_operand_statement_then_single`, `::test_reversed_order_preserves_actual_statement_order`, `::test_repeated_operands_preserve_order`; `TestLiteralCdTransitions::test_cd_workspace_root_then_two_operands`, `::test_cd_subdirectory_then_parent_relative`; `TestChainedPlanComposition::test_two_cat_chain_is_one_complete_ordered_bundle`, `::test_cd_then_reads_resolves_against_transition` |
| Workdir precedence + literal cd affects following reads | per-call workdir then cd transition resolves against the transition | `TestChainedPlanComposition::test_per_call_workdir_then_cd_transition`, `TestLiteralCdTransitions::test_per_call_workdir_precedes_cd_transitions`, `::test_sibling_workspace_cd_is_outside`, `::test_cd_ancestor_of_workspace_is_outside` |
| No host cwd/stat/resolve/eval/glob/expansion; other cd forms typed | absolute literal dirs only; sibling/ancestor/`..`/relative/bare/multi-target typed `CD_TARGET_UNSUPPORTED` | `TestLiteralCdTransitions` (negatives: `::test_relative_cd_is_explicitly_typed`, `::test_bare_cd_is_explicitly_typed`, `::test_multi_target_cd_is_explicitly_typed`, `::test_dotdot_cd_target_is_explicitly_typed`, `::test_cd_with_unknown_workspace_is_typed`); `TestPlanNegatives` (`::test_loop_is_typed_and_words_are_not_reinterpreted`, `::test_branch_is_typed_and_words_are_not_reinterpreted`, `::test_substitution_is_typed_and_stops_member_collection`, `::test_pipe_is_typed_and_later_words_are_not_operands`, `::test_redirection_is_typed`) |
| Whole-plan bound, not per-segment loophole | whole-plan chars/statements/operands with shared cat-operand budget | `TestWholePlanBounds` (`::test_exact_operand_budget_across_statements_is_complete`, `::test_one_over_operand_budget_across_statements_is_typed`, `::test_exact_statement_bound_is_complete`, `::test_one_over_statement_bound_is_typed`) |
| Global nonzero identifies no failed read; later success proves no earlier cat | nonzero/mixed chain: no proven span, no digest, requested members preserved, wrapper/global status recorded, no per-command exit invented | `TestPerReadVersusGlobalExit` (`::test_nonzero_chain_proves_no_read_and_no_digest`, `::test_earlier_failure_later_success_nonzero`, `::test_truncated_chain_is_not_a_bundle`, `::test_process_running_chain_is_deferred`); `TestMixedOutputNegatives` (`::test_ls_family_exit_zero_is_not_support`, `::test_ls_before_read_nonzero_is_not_support`, `::test_semicolon_chain_exit_zero_acquires_nothing`) |
| Later command words never reinterpreted as cat files | `stop_at_operator=True` operand parsing; structurally-mixed plan typed | `TestPlanNegatives::test_pipe_is_typed_and_later_words_are_not_operands`, `::test_attached_semicolon_token_is_not_a_literal_file`, `::test_loop_is_typed_and_words_are_not_reinterpreted`, `::test_branch_is_typed_and_words_are_not_reinterpreted` |
| Earn echo prefix/suffix outer region; label inside source stays source | exact startswith/endswith anchoring of literal + newline in statement order; only pure file span exposed | `TestEchoOuterBoundaries` (`::test_leading_echo_is_earned`, `::test_trailing_echo_is_earned`, `::test_both_echo_boundaries_are_earned`, `::test_internal_echo_is_an_unproven_boundary`); `TestOuterSourceRegions` (`::test_leading_echo_prefix_is_proven_at_exact_position`, `::test_trailing_echo_suffix_is_proven_at_exact_position`, `::test_both_boundaries_expose_only_the_pure_middle`, `::test_collision_shorter_than_boundaries_is_typed`, `::test_extra_output_before_prefix_is_typed`, `::test_mismatched_suffix_is_typed`); `TestOuterRegionComposition::test_echo_prefix_exposes_only_the_pure_file_span`, `::test_label_inside_source_remains_source` |
| Complete execution alone is not an attributable span; unproven boundary retains all bytes | `OUTER_BOUNDARY_UNPROVEN` typed, no bundle digest, non-removable | `TestOuterSourceRegions::test_no_echo_attributes_whole_content`, `::test_incomplete_plan_never_attributes`; `TestOuterRegionComposition::test_boundary_collision_is_typed_not_attributed`, `::test_internal_echo_is_typed_not_attributed` |

Strategic probes (unchanged files, canonical `.venv` Python,
`--head a29d4144098ba289c06d785d258cd48f1e473439`):
- `check-bundle-observation.py`: 23/23 PASS, positive control valid.
- `check-read-option-semantics.py`: 16/16 PASS.
- `check-endpoint-selection.py`: 5/5 PASS.
- `check-root-endpoint-context.py`: 6/6 PASS (017-c baseline 2/6),
  positive control valid.
- All four also passed 50/50 at the A1 prerequisite head
  `fcfdf4017a46d888e8f74610be3396c9c9e6d240` (milestone-1 proof
  recorded before A2 was built; probes not edited).
- Preserved 017-a/b/c positives (source span, empty read, malformed
  root, escape-return, duplicate/missing/mismatched IDs, qualified-tool
  evidence, stdin operand, quoted options, Unicode separators, exact
  operand bound, endpoint selection) still pass inside the 381 focused
  set.

## Verification
All gates ran non-root under process-local umask 022 (host umask 0002
untouched); frozen installs; canonical repo `.venv`.

| Command (exact) | Result |
| --- | --- |
| `uv run --frozen pytest -q tests/test_bundle_*.py` | PASSED — 381 passed (0.96s; 286 retained + 95 new; per-file: client_paths 38, compound_reads 85 (new), observation_models 23, observe 24 (14 + 10 new), read_grammar 89, root_envelopes 32, shell_tokens 13, tool_results 77) |
| `uv run --frozen pytest -q tests/test_observation.py tests/test_dependency_acquisition.py tests/test_pipeline.py tests/test_app.py tests/test_image_policy.py tests/test_tool_policy.py tests/test_dev_provenance.py tests/test_source_input_binding.py` | PASSED — 267 passed (113.53s); the two stale-manifest cases pass at manifest B exactly as in 017-c |
| probes `check-bundle-observation.py` / `check-read-option-semantics.py` / `check-endpoint-selection.py` / `check-root-endpoint-context.py` (unchanged, `--head` = implementation head) | PASSED — 23/23, 16/16, 5/5, 6/6 (50/50); valid positive controls; exit 0 |
| `uv lock --check` | PASSED |
| `uv sync --frozen --extra dev` | PASSED (31 packages) |
| `uv run --frozen ruff check .` | PASSED |
| `uv run --frozen ruff format --check .` | PASSED (496 files already formatted) |
| `uv run --frozen mypy src tests` | PASSED (104 source files) |
| `uv run --frozen python scripts/docs_consistency_check.py` | PASSED (19 claim docs) |
| `uv run --frozen pytest -q` | PASSED — 1924 passed, 27 skipped, 0 failed (322.36s); the 27 skips are the standing explicit optional-fixture/live-layer skips, not passes |
| `uv build` | PASSED — wheel `360e4c5f0a5b108f018b4fc1de931065cca93bf12d2bc89e4aa90ad918cb4a59` (122395 B), sdist `4039d3d2445433447574237e524f7253cff6dd36d2cafcc0f57ead673437fa79` (627350 B); digests equal the development manifest |
| `uv run --frozen python scripts/artifact_policy_check.py --dist dist --inspect` | PASSED (`ok: true`, no violations) |
| `uv run --frozen python scripts/artifact_policy_check.py --dist dist --install-smoke` | PASSED (`ok: true`, no violations) |
| `uv run --frozen python scripts/dev_provenance_manifest.py --verify --dist dist` | PASSED — `development provenance OK: state=development head=a29d4144098b` |
| `python -m compileall -q src tests oap/bin scripts` | PASSED |
| `bash -n` over `oap/bin/*.sh` + `packaging/readyz-wait.sh` | PASSED (4 scripts) |
| `git diff --check 7abe503..HEAD` | PASSED |
| Targeted privacy/credential/raw-log scan over round-added lines | PASSED — 2006 added lines across `src`/`tests`/`docs`/`TESTING.md`/`ARCHITECTURE.md`: no credential patterns, no private URLs/host paths, no protected-fixture references; this report contains hashes/counts/statuses only |
| Byte-identical normative mirror | PASSED — `cmp ARCHITECTURE-for-agents.md oap/strategic-instructions/ARCHITECTURE-for-agents.md` clean |
| Frozen/handoff/prior-OAP invariance | PASSED — `docs/CACHE-REWORK.md` SHA256 `410df5c0b8f90b05220adc32c8e673b143c0cf1fa3da02270d91ac453c886abd` unchanged; `packaging/` delta since round start = development manifest refresh only (no `packaging/releases/` change); 016 and 017-a/b orders and reports unchanged; OAP transcript delta = 017-d order addition + `oap/active` (017-c -> 017-d) + the mandated byte-identical compact mirror; frozen RC10 binding re-proved by the manifest verification above |
| Independent clean `git archive` reproduction | PASSED — `git archive` of source commit A2 into a fresh 0700 temp root, fresh venv (Python 3.12.15) + frozen sync + `uv build`: wheel/sdist SHA256 byte-identical to the manifest digests; fresh non-editable install of the wheel in a second venv (entrypoint help/version OK); `observe_request` smoke: (1) Chat single-read fixture COMPLETE with `endpoint="chat"` and proven `("A.md",)`; (2) `cat A.md && cat B.md` plan with proven exit 0 COMPLETE — one bundle, `bundle_digest` exactly SHA-256 of the middle span, `member_digests == (None, None)`, slot width 2, exact `content_span` slice; (3) explicit Chat with a root-shaped object in the unused Responses `input`: root result UNSUPPORTED, zero valid-root occurrences, Chat read still COMPLETE; no raw body/chunk-id in any output; temp root removed after |

## Live model/service evidence
NOT RUN. The order authorizes no live inference or API calls; no
Qwen/vLLM, qwen-serving, protected Codex profile, or network fixture
was touched.

## GitHub CI / required checks
Check suites at implementation head
`a29d4144098ba289c06d785d258cd48f1e473439` (check-suite IDs
106197824302, 106197831692, 106197924447; workflow run 39190785339
completed/success) — all eight required checks present and SUCCESS
(observed before the report commit):
- `test` — SUCCESS
- `docker` — SUCCESS
- `docker-published` — SUCCESS
- `gateway-contract` — SUCCESS
- `operator-session` — SUCCESS
- `CodeQL` — SUCCESS
- `Analyze (python)` — SUCCESS
- `Analyze (actions)` — SUCCESS

All required green at drafting: yes. The report-only push may trigger
new checks at the report head; strategy verifies.

## Local setup/dependencies
- Host umask 0002; every gate above ran under process-local umask 022
  (verified context; no global/home chmod; no root; no sudo).
- Python 3.12.15 via repo `.venv` (uv 0.12.5, frozen lock); no new
  dependencies; `uv.lock` unchanged.
- Temp roots/files for protected work created 0700/0600 and removed
  after use (archive-repro root mode verified 0700).

## Documentation
- Observation contract, ledger, TESTING.md, both architecture maps and
  the byte-identical compact mirror updated in this PR (same-commit
  docs law); `ARCHITECTURE.md` stage sentence extended for 017-d;
  PR #25 description updated for the 017-d slice (verified
  byte-identical after `PATCH` via `gh api`).
- No cache/runtime capability claims added: modules remain inert and
  all v1 runtime criteria remain NOT RUN.

## Safety/scope confirmations
- Protected live-host boundary: NO change to qwen-serving, its units/
  venv/models, port 18020, API-key files, firewall/VPN/bindings, or
  existing Codex profiles.
- No live inference, no host Docker execution (remote disposable CI
  runners only), no gateway/image-policy/release change.
- No new dependencies; no model weights; no secret or raw customer
  content in any commit, report, or PR text (scan above).
- Activated order/`oap/active` bytes NOT edited after activation;
  prior orders/reports/handoff/plan/frozen publication bytes unchanged;
  strategic probes NOT edited.
- Observed commands were never executed to improve observation; no
  client/adapter filesystem access; the plan parser is data-only
  (no shell execution, no stat/resolve against the adapter host).
- Final commit changes only this report path with the implementation
  head as sole parent (verified below); no merge, no auto-merge, no
  second PR for objective 017.

## Known limitations/blockers
- D09/D10 (literal loops, multi-chunk process pairing and the
  remaining truncation matrix) not implemented this round — planned
  017-e on the same PR; objective 017 stays open until all D01-D10
  are earned and independently reviewed. Literal loops and wildcards
  remain explicitly typed unsupported in this slice (`TestPlanNegatives`).
- All v1 runtime stages (018-024: graph/admission, RAM working state,
  recovery, tokenizer/compiler, source replacement, adversarial
  acceptance, real-model qualification): NOT RUN.
- 27 standing fixture/live-layer skips are reported as skips, never as
  passes; local results do not impersonate the (separately listed)
  GitHub checks.
- COMPLETE here is a claim for strategic review, never acceptance.

## Recommended strategic follow-up (factual, non-directive)
- Independently re-run the four unchanged probes at the report head
  (they pass at the implementation head as evidenced above).
- Verify the report-head CI checks after this report-only push.
- If the 017-d slice is accepted as earned evidence for the root-
  domain gate and D06/D07/D08 finite read-plan behavior, the remaining
  objective-017 scope is D09/D10 on the later same-PR suffix 017-e.

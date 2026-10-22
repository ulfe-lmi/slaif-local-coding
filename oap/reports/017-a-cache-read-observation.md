# OAP Coding-Agent Report — 017-a

## Work order
- Order: `oap/orders/017-a-cache-read-observation.md` (objective 017, round 017-a, CREATE_NEW_PR)
- `oap/active` = `017-a`; both committed unchanged with the implementation.
  - order SHA256 `67e5fda6faf519dbccc86c589b2b178928fefc86a5595ae83ee083fe22e3fe29`
  - active SHA256 `a1837a4fd997503ed7dbb45a69d90c8dc5e7966038b95f43f87ae27beefd4871` (bytes `017-a\n`)

## Status
COMPLETE for the activated slice only: D01-D05 pure root/read/result/span
observation with the simple-call negatives, versioned synthetic fixtures, the
observation contract, docs/ledger status updates, and in-scope CI repair.
This is a claim for strategic review, not acceptance. Objective 017 as a whole
(D01-D10) is NOT complete; D06-D10 remain planned for the same-PR continuation
017-b. The new modules are inert: not active in the adapter, not wired into
the legacy request execution path; the legacy detector is unchanged. All v1
runtime criteria remain NOT RUN.

## Executive summary
1. New inert package `src/slaif_local_coding/constitution/bundles/`
   (`observation_models.py`, `client_paths.py`, `root_envelopes.py`,
   `read_grammar.py`, `tool_results.py`, `observe.py`, `__init__.py`): frozen
   typed results with half-open character spans and exact UTF-8 byte
   conversion, lexical-only literal client-path normalization (no filesystem,
   no shell), the versioned project-instructions envelope contract (D01/D02),
   the bounded literal `cat` grammar with typed negatives (D03/D04), exact
   call-ID pairing plus exec-wrapper facts and ordered whole-bundle
   semantics (D05), and a pure composition entry point `observe_request`.
   Requested vs proven-executed members are distinct; bundle digests are never
   per-file hashes; unknown member digests stay None; fixed limitation
   reasons never echo payloads; no model exposes a principal field and no
   untrusted text is ever derived into identity.
2. 184 focused tests across the six named suites plus 27 self-identifying
   versioned synthetic fixtures (`tests/fixtures/cache_bundles/v1/`) and
   reuse of the canonical sanitized 0.149.0 fixture;
   `docs/CACHE-OBSERVATION-CONTRACT.md` documents the versioned contract.
3. Docs/ledger updated: 016 recorded accepted/merged (PR #24, merge
   `96c790423f6f0097a56a0b12bacda8a9b6da6aba`); D01-D05 `PENDING` with named
   test evidence; D06-D10 and all later stages `NOT RUN`; TESTING.md documents
   the process-local umask 022 prerequisite and the new observation coverage;
   both architecture docs carry the minimal implementation-map qualification.
4. Development provenance manifest refreshed for the new artifact inputs
   (inputs=178; wheel `9315b0c581e0...`, sdist `01e2109fc519...`); the frozen
   RC10 publication bytes are untouched.
5. Two in-scope CI repairs in `scripts/docker_qualification_ci.py` (no
   workflow, release, gateway, or runtime change), both root-caused and
   evidenced below; all eight required checks are SUCCESS at the
   implementation head.

## Authoritative GitHub state
- Repository: `ulfe-lmi/slaif-local-coding`; PR #25
  https://github.com/ulfe-lmi/slaif-local-coding/pull/25 — OPEN, MERGEABLE,
  non-draft, single objective PR (no second PR for objective 017)
- Base `main` = `96c790423f6f0097a56a0b12bacda8a9b6da6aba` (PR #24 merge; the
  order-verified authoritative base)
- Head branch `oap/017-cache-read-observation`
- Implementation head SHA: 95270f241de1dabde06fb9fb45a5ff33af104a9d
- Report publication commit: SELF
- Branch commits over base (all pushed before this report):
  - `48044d5c8f76996e3f2578760e15435d96f4491a` — 017-a: pure D01-D05
    root/read/result/span observation slice (bundles package, 6 test suites,
    27 fixtures + README, observation contract, ledger/TESTING/architecture
    updates, activated order + `oap/active`; 48 files)
  - `2a068e1658e6b7256505c703fbd248c01a0d84ed` — 017-a: refresh development
    provenance manifest (source `48044d5c8f76`, inputs=178)
  - `cb818487da738dce5e2f394b5b2ba916804931ab` — 017-a: state-aware wheel
    binding in docker qualification (in-scope CI repair, build mode)
  - `f4af00bb8a16ce0385b11892a2adecca4208eba1` — 017-a: refresh development
    provenance manifest (source `cb818487da73`)
  - `cebb6ea4986235060c2ac4ec90c1428e6c10f68c` — 017-a: keep published-mode
    wheel binding on the frozen manifest (in-scope CI repair, published mode)
  - `95270f241de1dabde06fb9fb45a5ff33af104a9d` — 017-a: refresh development
    provenance manifest (source `cebb6ea49862`; final source binding)
- Merge performed: NO; auto-merge: never enabled.

## Changes and files
### `48044d5` — pure D01-D05 observation slice (48 files)
- `src/slaif_local_coding/constitution/bundles/` (new, 7 files):
  - `observation_models.py` — frozen Pydantic models (`CharSpan` with
    `to_byte_span`, `RootOccurrence`, `VersionCandidate`, `RootScanResult`,
    `PathContext`, `NormalizedPath`, `ReadCommandParse`, `WrapperFacts`,
    `ReadObservation`, `UnpairedRecord`, `ObservationReport`,
    `ObservationBounds`, closed `Limitation` vocabulary) and constants
    `OBSERVER_VERSION=cache-bundle-observation/1`,
    `ENVELOPE_FORMAT=codex-project-instructions/v1`,
    `READ_GRAMMAR=literal-shell-read/v1`,
    `TOOL_WRAPPER_FORMAT=codex-exec-wrapper/v1`, `EMPTY_SOURCE_SHA256`;
    helpers `sha256_hex`, `contains_lone_surrogates`, `utf8_byte_span`,
    `canonical_payload_fingerprint`.
  - `client_paths.py` — `validate_workspace`, `normalize_read_path`
    (lexical-only; TRAVERSAL vs OUTSIDE_WORKSPACE via the used-dotdot rule;
    URL `#`/`?` are literal filename characters, never stripped;
    fully-quoted literal operands under the no-spaces convention; no
    filesystem or shell imports).
  - `root_envelopes.py` — versioned delimiter contract (LF/CRLF; the closing
    tag's line-start newline is a delimiter, not source); environment-tail
    forms (adjacent / newline-separated / separate-item) excluded from source
    bytes; idempotent repeated same-scope roots; same-scope version
    candidates distinct from competing-scope conflict; assistant/tool/offset
    prose never authoritative; typed malformed/duplicate/nested/over-bound
    outcomes without regex blowup.
  - `read_grammar.py` — literal `cat` / `cat --` / multi-operand only; typed
    negatives (FRAGMENT_COMMAND, PIPE, REDIRECTION, MULTIPLE_COMMANDS,
    COMMAND_SUBSTITUTION, SHELL_ESCAPE, GLOB_UNPROVEN, COMMENT_PRESENT,
    QUOTED_OPERAND, COMMAND_EMPTY, OVER_BOUND); `unwrap_supported_arguments`
    (JSON str/obj `cmd|command`; argv `[bash|sh|zsh, -c|-lc, str]` or
    `[str]`); command syntax is data — never executed, expanded or evaluated.
  - `tool_results.py` — `parse_wrapper` (header lines before a
    newline-terminated `Output:`; `Process exited with code N` (no colon),
    `Truncated: true|false`, `Process is still running`; malformed vs unknown
    completion; missing body distinct from proven empty); exact call-ID
    pairing (duplicate/mismatched/missing typed; namespace names need the
    request's own `tools`-array envelope evidence, never a suffix guess);
    `write_stdin` chunks typed unsupported; single operand → proven member
    digest (exact empty digest for a zero-byte body), ≥2 operands → bundle
    digest only with all member digests None; source after `Output:` never
    redefines wrapper status.
  - `observe.py` — pure composition `observe_request(payload, context,
    bounds)`; `__init__.py` — package exports.
- `tests/test_bundle_observation_models.py` (20),
  `tests/test_bundle_client_paths.py` (26),
  `tests/test_bundle_root_envelopes.py` (25),
  `tests/test_bundle_read_grammar.py` (23),
  `tests/test_bundle_tool_results.py` (35),
  `tests/test_bundle_observe.py` (12) — 181 test functions + parametrize
  cases = 184 executed tests.
- `tests/fixtures/cache_bundles/v1/` — 27 self-identifying synthetic fixtures
  (`_fixture.synthetic=true`, `observed_format_authority` → codex-0.149.0
  record, `parser_versions`, `note`) + README; the canonical sanitized
  `tests/fixtures/codex/0.149.0/project_instructions_responses.json` is
  reused as the D01 real-format input.
- `docs/CACHE-OBSERVATION-CONTRACT.md` (new) — the versioned contract.
- `docs/CACHE-REWORK-LEDGER.md` — 016 merged (PR #24); D01-D05 `PENDING` with
  named test functions; 017 in progress; other criteria unchanged.
- `TESTING.md` — process-local umask 022 prerequisite for the full suite
  (0002 → 12 safe-evidence ordering failures; 077 masks the intentional 0755
  untrusted-cache fixture; at accepted 016, 022 passed the complete gate
  1543/27/0) and the landed D01-D05 observation coverage.
- `ARCHITECTURE-for-agents.md`, `ARCHITECTURE.md` — minimal status
  qualification only (pure D01-D05 slice implemented as inert typed modules,
  not active in the adapter; 016 merged; 017 active); legacy claims and
  normative mirrors preserved; no other law touched.
- `oap/orders/017-a-cache-read-observation.md`, `oap/active` — committed
  unchanged (byte hashes above).

### `2a068e1` — development provenance manifest (source `48044d5c8f76`)
- `packaging/dev_provenance_manifest.json` — inputs=178;
  wheel `9315b0c581e070f0754d2ce82d7a4c28c75837e31e1c70bf39a2b3a44ee9113e`;
  sdist `01e2109fc51929621509d04632b9ed31e65886d00b6ac17ba6786e426dd90b27`;
  `frozen_publication` and `release` sections byte-identical to the base.

### `cb81848` — state-aware wheel binding (in-scope CI repair, build mode)
- `scripts/docker_qualification_ci.py::_do_verify_wheel_binding` — in build
  mode the phase now enforces the same fail-closed state selection as the CI
  build step (`dev_provenance_manifest.emit_state`): frozen release manifest
  in the frozen state, current-development manifest in the development state.
  Root cause: this round's new source modules legitimately change the wheel
  hash (`eb241dda...` → `9315b0c5...`); the phase previously compared only
  against the frozen RC10 release manifest, so it failed at
  `verify_wheel_binding` (`wheel_hash_mismatch`) on run 1 (head `2a068e1`,
  run 39174413732). The 016-c/d development provenance contract is
  unchanged; the frozen RC10 bytes are untouched.

### `f4af00b` — development provenance manifest (source `cb818487da73`)
- `packaging/dev_provenance_manifest.json` — source/qualification-label
  lines only; wheel/sdist hashes unchanged (scripts are not artifact inputs).

### `cebb6ea` — published-mode wheel binding restored (in-scope CI repair)
- `scripts/docker_qualification_ci.py::_do_verify_wheel_binding` — published
  mode verifies the pulled image's wheel against the frozen release
  manifest (the exact hash the CI step passes for the published RC10 image;
  original behavior), while build mode keeps the state-aware selection.
  Root cause: on run 2 (head `f4af00b`, run 39175531036) `docker` passed but
  `docker-published` failed the phase with
  `DevProvenanceError: frozen source commit 255b3f42912e is not an ancestor
  of 3160a0882f30` — the published run's wheel argument refers to the frozen
  RC10 wheel and its shallow checkout cannot run the development-state
  ancestry verification. No workflow change was needed.

### `95270f2` — development provenance manifest (source `cebb6ea49862`)
- `packaging/dev_provenance_manifest.json` — source/qualification-label
  lines only; wheel/sdist hashes unchanged. This is the implementation head;
  the input map is identical from here to the report commit.

## Acceptance evidence
### Criterion A — D01/D02 root envelope recognition
- Command (process-local umask 022):
  `uv run --frozen pytest -q tests/test_bundle_observation_models.py tests/test_bundle_client_paths.py tests/test_bundle_root_envelopes.py tests/test_bundle_read_grammar.py tests/test_bundle_tool_results.py tests/test_bundle_observe.py`
  → 184 passed (also re-run after every later source change: 184 passed).
- Named evidence: `tests/test_bundle_root_envelopes.py` —
  `test_real_format_canonical_fixture_parses_with_exact_bytes` (exact
  reconstruction, byte-identical digest, environment tail excluded and
  preserved, exact char→byte span conversion), `test_adjacent_environment_tail`,
  `test_newline_separated_environment_tail` (closing-tag line-start newline is
  a delimiter, not source), `test_separate_item_environment_is_excluded`,
  `test_crlf_envelope_preserves_crlf_content_bytes`,
  `test_trailing_newline_after_environment_is_typed_malformed`,
  `test_repeated_identical_same_scope_roots_are_idempotent` (all source
  locations preserved), `test_same_scope_differing_content_yields_version_candidates`,
  `test_competing_scopes_are_an_explicit_conflict` (neither silently chosen),
  `test_assistant_envelope_never_creates_root`,
  `test_marker_prose_at_later_offset_is_not_a_root`,
  `test_tool_output_envelope_is_not_a_root`, `test_unclosed_tail_is_typed`,
  `test_nested_duplicate_opening_marker_is_typed`,
  `test_duplicate_closing_tag_in_tail_is_typed`,
  `test_invalid_labels_and_delimiters_are_typed`,
  `test_malformed_environment_tail_is_typed`,
  `test_valid_root_coexists_with_observable_malformed_occurrence`,
  `test_over_bound_item_is_typed_without_scan_explosion`,
  `test_adversarial_huge_item_terminates_deterministically`,
  `test_many_items_over_bound_is_typed`,
  `test_surrogate_fixture_is_rejected_without_crash`,
  `test_chat_endpoint_is_explicitly_unsupported_for_roots`,
  `test_non_string_texts_are_ignored`,
  `test_fixture_self_identifies_and_unknown_keys_are_ignored`.

### Criterion B — D03/D04 literal read paths and grammar
- Named evidence: `tests/test_bundle_client_paths.py` —
  `test_relative_against_evidenced_workspace`, `test_relative_with_explicit_supported_workdir`,
  `test_relative_without_workspace_is_unproven`, `test_relative_traversal_escape`,
  `test_simple_absolute_under_workspace`, `test_lexical_dotdot_staying_inside_is_allowed`,
  `test_lexical_dotdot_escaping_is_traversal`, `test_sibling_prefix_is_outside`
  (`/work-other` never mapped to `/work`), `test_outside_absolute_path`,
  `test_absolute_with_unknown_workspace`, `test_workspace_bound_enforced`,
  `test_workdir_must_be_inside_workspace`,
  `test_logical_scope_is_not_a_posix_workspace`,
  `test_url_fragment_is_literal_never_stripped`,
  `test_query_syntax_is_never_mapped_to_the_plain_file`,
  `test_fully_quoted_literal_operand_under_no_spaces_convention`,
  `test_partial_or_nested_quotes_are_ambiguous`, `test_comment_leading_token_rejected`,
  `test_metacharacters_make_operands_non_literal`, `test_unicode_path_preserved`,
  `test_path_bound_enforced`, `test_nonexistent_client_paths_still_normalize`
  (no filesystem oracle), `test_module_imports_no_filesystem_or_shell_facilities`;
  `tests/test_bundle_read_grammar.py` — `test_single_relative_operand`,
  `test_dash_dash_separator`, `test_two_operands_in_order`,
  `test_repeated_operand_preserves_order`, `test_absolute_workspace_operands`,
  `test_fully_quoted_operands_under_no_spaces_convention`,
  `test_command_digest_and_length_are_recorded`,
  `test_unsupported_shapes_are_typed_never_complete` (pipe, redirection,
  substitution, backticks, heredoc, glob, `head`/`sed`/`tail` fragments),
  `test_comment_terminates_the_command_line`,
  `test_unexecuted_branch_is_not_a_read`, `test_loop_is_not_a_read_in_this_slice`,
  `test_newline_is_a_compound_command`, `test_over_bound_command_is_typed`,
  `test_too_many_operands_is_typed`, `test_literal_whitespace_tokenization`,
  `test_no_expansion_no_evaluation`, `test_json_string_cmd`,
  `test_non_json_string_arguments_are_unsupported`, `test_command_string_alias`,
  `test_argv_single_string`, `test_argv_shell_wrappers`,
  `test_unsupported_argument_shapes`, `test_module_imports_no_shell_facilities`.

### Criterion C — pairing, wrapper facts, completeness
- Named evidence: `tests/test_bundle_tool_results.py` —
  `test_complete_wrapper_facts`, `test_nonzero_exit_is_typed`,
  `test_recorded_truncation_is_typed`, `test_explicit_no_truncation_marker`,
  `test_unknown_completion_for_plain_output`,
  `test_missing_body_is_distinct_from_proven_empty`,
  `test_torn_marker_line_is_malformed`,
  `test_unknown_header_line_after_header_is_malformed`,
  `test_process_running_is_typed`, `test_over_bound_output_is_typed`,
  `test_source_metadata_lookalike_does_not_redefine_wrapper`,
  `test_duplicate_call_ids_are_typed_conflict`, `test_missing_result_is_typed`,
  `test_mismatched_result_is_typed`, `test_multi_chunk_results_are_deferred`,
  `test_unsupported_tool_names_are_not_eligible`,
  `test_namespace_name_without_envelope_evidence_never_suffix_guessed`,
  `test_namespace_name_with_envelope_evidence_is_supported`,
  `test_suffix_resemblance_alone_is_never_evidence`,
  `test_process_running_is_deferred`, `test_write_stdin_is_deferred`,
  `test_empty_file_is_complete_empty_version` (exact empty digest),
  `test_nonzero_exit_is_not_a_bundle`, `test_truncated_output_is_not_a_bundle`,
  `test_missing_body_is_not_a_bundle`,
  `test_substitution_never_executed_or_expanded`,
  `test_fragment_command_is_not_a_whole_file`,
  `test_unnormalized_operand_keeps_read_unsupported`,
  `test_relative_without_context_is_unproven`,
  `test_chat_tool_calls_and_tool_messages_pair` (Chat equivalents).

### Criterion D — D05 ordered whole bundles
- Named evidence: `tests/test_bundle_tool_results.py` —
  `test_single_complete_read` (exact content span, wrapper prefix/suffix
  untouched and reconstructed), `test_two_members_without_separators_is_one_ordered_bundle`
  (member digests `(None, None)`, one bundle digest),
  `test_reversed_order_changes_observed_member_order`,
  `test_repeated_operands_do_not_fabricate_files` (distinct width 1, proven
  order preserved), `test_unicode_crlf_bytes_are_exact`;
  `tests/test_bundle_observation_models.py` —
  `test_two_member_bundle_has_unknown_member_digests`,
  `test_single_member_complete_read_carries_proven_digest`,
  `test_requested_and_proven_executed_are_distinct`,
  `test_sha256_is_over_exact_observed_bytes`.

### Criterion E — provenance and boundedness
- Named evidence: `tests/test_bundle_observe.py` —
  `test_every_fixture_is_synthetic_and_versioned`,
  `test_fixture_files_parse_end_to_end` (all 27 fixtures parse end-to-end),
  `test_root_and_read_are_observed_together`,
  `test_deterministic_repeated_observation`,
  `test_payload_is_unchanged_by_observation` (input immutability),
  `test_raw_content_never_entered_the_report`,
  `test_explicit_validated_context_normalizes_absolute_paths`,
  `test_logical_root_scope_never_maps_host_paths`,
  `test_no_context_at_all_is_unproven`,
  `test_over_bound_request_is_typed_and_finite`, `test_too_many_calls_is_typed`,
  `test_report_versions_record_parser_identity`;
  `tests/test_bundle_observation_models.py` —
  `test_lone_surrogate_detected_without_crashing`,
  `test_surrogate_input_yields_typed_limitation_not_crash`,
  `test_reasons_are_fixed_strings_never_echo_payload`,
  `test_models_are_frozen`, `test_extra_fields_forbidden`,
  `test_no_principal_field_exists_on_any_observation_model`,
  `test_untrusted_identity_text_is_never_derived`,
  `test_ascii_span_byte_conversion`, `test_unicode_span_converts_to_exact_utf8_bytes`,
  `test_crlf_span_length`, `test_invalid_spans_rejected`,
  `test_empty_digest_is_exact_sha256_of_no_bytes`,
  `test_payload_fingerprint_survives_surrogates`,
  `test_fingerprint_is_deterministic_across_call_order`,
  `test_versions_are_stable_identifiers`.
- Targeted privacy/credential/raw-log scan over every changed path (ghp_/sk-/
  bearer/private-URL//synology/api-key patterns): clean; the only matches in
  the whole tree are pre-existing governance lines in
  `ARCHITECTURE-for-agents.md` (protected live-host boundary) which this round
  did not touch.

## Verification
All local gate runs used the process-local umask 022 context (verified
non-root); no global/home permissions changed; no sudo; no root.
- `uv lock --check` — PASSED (no lock changes; the `pydantic_core`
  `core_schema` import uses pydantic 2.13.4's locked direct dependency).
- `uv sync --frozen --extra dev` — PASSED.
- `uv run --frozen ruff check .` — PASSED (at final head).
- `uv run --frozen ruff format --check .` — PASSED (at final head).
- `uv run --frozen mypy src tests` — PASSED (100 source files, at final head).
- `uv run --frozen python scripts/docs_consistency_check.py` — PASSED
  (19 claim docs checked, at final head).
- `uv run --frozen pytest -q` (full suite, final head `95270f2`) —
  PASSED: 1727 passed, 27 skipped, 0 failed (325.83s). The 27 skips are the
  pre-existing explicit optional-fixture/live-layer skips (unchanged set).
- Focused bundle suites (order-mandated set) — PASSED: 184 passed.
- 8-file regression set
  (`tests/test_observation.py tests/test_dependency_acquisition.py
  tests/test_pipeline.py tests/test_app.py tests/test_image_policy.py
  tests/test_tool_policy.py tests/test_dev_provenance.py
  tests/test_source_input_binding.py`) — at commit `48044d5` (before the
  first manifest refresh) 265 passed, 2 failed: the two expected stale-
  manifest failures (`tests/test_dev_provenance.py::test_real_development_state_consistent`,
  `tests/test_source_input_binding.py::test_real_repo_source_inputs_bound_to_committed_source`);
  both PASS in every full-suite run after the refresh (final context included).
- `uv build` — PASSED; wheel
  `9315b0c581e070f0754d2ce82d7a4c28c75837e31e1c70bf39a2b3a44ee9113e`
  (103751 bytes, 34 entries), sdist
  `01e2109fc51929621509d04632b9ed31e65886d00b6ac17ba6786e426dd90b27`
  (588068 bytes, 176 entries).
- `uv run --frozen python scripts/artifact_policy_check.py --dist dist --inspect`
  — PASSED (ok=true, no violations); `--install-smoke` — PASSED.
- `uv run --frozen python scripts/dev_provenance_manifest.py --verify --dist dist`
  — PASSED (`state=development head=95270f241de1`).
- `python -m compileall -q src tests oap/bin scripts` — PASSED.
- `bash -n` over `oap/bin/*.sh` and `packaging/*.sh` — PASSED.
- `git diff --check` — PASSED.
- Unchanged frozen-publication/human-handoff hashes — PASSED:
  `docs/CACHE-REWORK.md` SHA256
  `410df5c0b8f90b05220adc32c8e673b143c0cf1fa3da02270d91ac453c886abd`
  (unchanged); `frozen_publication` and `release` sections of the development
  manifest byte-identical to the base commit.
- Independent clean `git archive` reproduction in a 0700 temp root + fresh
  venv install — PASSED: byte-identical wheel and sdist to the manifest
  digests; fresh Python 3.12 venv non-editable install of the wheel imports
  and executes `observe_request` successfully. (The final-head artifacts are
  byte-identical to this verified build: identical digests, scripts are not
  artifact inputs.)
- Live model/Codex E2E — NOT RUN (the order authorizes none; no live product
  inference/API call was performed).
- Docker/operator/docker-published — remote CI evidence only; no Docker
  activity on this protected host.

## Live model/service evidence
NOT RUN. The order authorizes no live inference or API calls; no Qwen/vLLM,
qwen-serving, protected profile, or network fixture was touched.

## GitHub CI / required checks
Run 39176318482 at head `95270f241de1dabde06fb9fb45a5ff33af104a9d` —
conclusion SUCCESS; all eight required checks present and PASS:
- `test` — PASS (3m39s; full suite on the runner: 1727 passed, 27 skipped)
- `docker` — PASS (1m40s)
- `operator-session` — PASS (1m1s)
- `gateway-contract` — PASS (17s)
- `docker-published` — PASS (1m15s)
- `CodeQL` — PASS (3s)
- `Analyze (python)` — PASS (57s)
- `Analyze (actions)` — PASS (32s)
Repair history (truthful, in-scope): run 1 (head `2a068e1`) — `docker` FAILED
at `verify_wheel_binding` (frozen-manifest-only comparison vs the
development-state wheel); repaired in `cb81848`. Run 2 (head `f4af00b`) —
`docker-published` FAILED (published-mode wheel argument is the frozen RC10
wheel; development-state ancestry verification is not applicable there);
repaired in `cebb6ea`. Run 3 (head `95270f2`) — all eight PASS.

## Local setup/dependencies
- Host umask 0002; all gate runs executed under a process-local umask 022
  (verified context; no global/home chmod; no root).
- Python 3.12 via the repo `.venv` (uv 0.12.5, frozen lock); no new
  dependencies; `uv.lock` unchanged.
- The `pydantic_core.core_schema.FieldValidationInfo` annotation imports a
  locked direct dependency of pydantic 2.13.4 (the top-level
  `pydantic.FieldValidationInfo` export is deprecated and unusable as a mypy
  type in this toolchain).

## Documentation
- `docs/CACHE-OBSERVATION-CONTRACT.md` (new) — versioned contract for the
  slice: modules/versions, coordinate law, delimiter law, grammar, wrapper
  parsing, pairing, bounds, limitation vocabulary.
- `tests/fixtures/cache_bundles/v1/README.md` — synthetic-fixture authority
  and self-identification contract.
- `docs/CACHE-REWORK-LEDGER.md` — 016 accepted/merged (PR #24, merge
  `96c790423f6f0097a56a0b12bacda8a9b6da6aba`); 017 in progress; D01-D05
  `PENDING` with named test functions (coding proposes states; strategic
  acceptance outstanding); D06-D10 and all other criteria `NOT RUN`.
- `TESTING.md` — umask 022 prerequisite with exact prior-context results;
  the landed D01-D05 coverage; inert-not-active statement.
- `ARCHITECTURE-for-agents.md` / `ARCHITECTURE.md` — minimal status
  qualification; legacy claims and exact normative mirrors preserved.
- PR #25 body states the bounded slice and the remaining D06-D10 scope; the
  PR is explicitly not merge-ready until the continuation lands.

## Safety/scope confirmations
- No merge, no auto-merge, no acceptance, no next-objective choice.
- Extra objective PR: NO (PR #25 is the single 017 PR; #23 is the
  pre-existing unrelated README-logo PR, untouched).
- Activated order/active edited after activation: NO (byte hashes verified
  before commit).
- Report commit: report-only (sole path
  `oap/reports/017-a-cache-read-observation.md`), sole parent
  `95270f241de1dabde06fb9fb45a5ff33af104a9d`.
- Protected live fixtures: untouched (no Qwen/vLLM/qwen-serving/systemd/
  model/venv/patch/flag/firewall/VPN/network/API-key/active-profile change;
  no live inference; no Docker activity on this host).
- No new dependencies, no model loading, no image decoding, no registry
  publication, no new RC/tag/version, no deployment/cutover.
- Frozen RC10 publication bytes, human handoff hash, and ordinary
  source-input policy: unchanged.
- No raw customer content, prompts, bodies, or secrets in any artifact, log,
  fixture, or report; fixtures are synthetic and self-identifying.

## Known limitations
- D06-D10 (chained reads, literal loops, per-read vs global exit evidence,
  multi-chunk process pairing, remaining truncation matrix) are NOT
  implemented; planned for the same-PR continuation 017-b.
- All v1 runtime stages (018-024: graph/admission, RAM, recovery,
  tokenizer/compiler, source replacement, adversarial acceptance, real-model
  qualification) remain NOT RUN.
- The bundles package is inert: not wired into the adapter request path; the
  legacy detector and behavior are unchanged. A pure observation result in
  this report claims nothing about active adapter caching or overall rework
  qualification.
- Docker qualification evidence is remote-CI-only (disposable runners); no
  local Docker execution on the protected host.

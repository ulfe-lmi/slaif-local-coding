# OAP Coding-Agent Report — 017-b

## Work order
- Order: `oap/orders/017-b-observation-proof-corrections.md` (objective 017,
  round 017-b, AMEND_EXISTING_PR); `oap/active` = `017-b` (bytes `017-b\n`,
  SHA256 `47a5920b0801379b12229fdc716a0da5eba118202fac053c536f2656d04479b5`),
  committed unchanged with the implementation (order SHA256
  `771f6843272637bc2c99457ac5f7d4fc97f7884efd098e6d32b6743ce454c953`).
- PR mode: AMENDED_EXISTING_PR — exact OPEN PR #25
  https://github.com/ulfe-lmi/slaif-local-coding/pull/25, base `main`, head
  branch `oap/017-cache-read-observation`. NO NEW PR; no coding merge or
  auto-merge.
- Starting remote PR/report head verified before mutation:
  `a833066ae25382bf7a9fdbe18f0dc1f479748de6` (sole parent
  `95270f241de1dabde06fb9fb45a5ff33af104a9d`); remote `main`
  `96c790423f6f0097a56a0b12bacda8a9b6da6aba`; local working tree clean apart
  from the activated order/active.

## Status
COMPLETE for the bounded 017-b correction slice (findings A-E plus the
normative mirror) — a claim for strategic review, not acceptance. Objective
017 as a whole (D01-D10) remains open; the D06-D10 compound/loop/chunk scope
moves to later same-PR suffixes (planned 017-c/d) per this order. The bundles
modules remain inert: not active in the adapter, legacy detector unchanged.
All v1 runtime criteria remain NOT RUN.

## Executive summary
1. All seven bounded 017-a observation defects corrected in
   `src/slaif_local_coding/constitution/bundles/`:
   - Real-format wrapper: handoff 6.2 `Chunk ID:` supported (plus the
     explicitly earned `Chunk Id:` variant); repeated exit/truncation status
     fields (contradictory or identical) are typed `MALFORMED_WRAPPER` with
     no trusted status — never last-field-wins COMPLETE; source after
     `Output:` remains source; exact source span/empty-read behavior
     preserved.
   - Read grammar: option terminator processed once; a later `--` is a
     literal operand kept in the actual complete member list (`cat -- A.md
     -- B.md` → `A.md`, `--`, `B.md`); ordered operands, duplicate-path
     width, unknown member hashes unchanged.
   - Per-call cwd: explicit supported call `workdir` resolves relative
     operands before the batch default; invalid/outside workdir is typed
     (`OUTSIDE_WORKSPACE`/`UNSUPPORTED_TOOL`), never re-resolved elsewhere.
   - Tool/endpoint evidence: eligibility = known executable bare name, or
     namespace-qualified name with known executable leaf plus the request's
     own compatible declaration (a declared unrelated bare function with a
     `cmd` parameter is not exec); pairing is endpoint-scoped, so a Responses
     call and a Chat result are never cross-paired on ID match alone.
   - Unicode/bounds: surrogate commands/outputs rejected with typed
     `MALFORMED_UNICODE` before any UTF-8 hashing (digests explicitly
     absent, never placeholders; observations non-removable, no bundle
     digest); label bound enforced in UTF-8 bytes; bounded argument decoding;
     fixed non-echoing reasons; no broad exception swallowing.
   - Parser bounds: `max_wrapper_header_lines` enforced before frame
     acceptance (typed `OVER_BOUND`); bounded canonical ASCII decimal exit
     grammar (0..255, ≤3 digits, no leading zeros) — `²` and 5000-digit
     fields are typed, never `int()`-converted (no ValueError).
2. Independent immutable probe truthfully re-run at the implementation head
   (same `STRATEGIC/probes/check-bundle-observation.py`, unchanged): 23
   cases, **23 PASS / 0 FAIL**, valid positive control, exit 0 (pre-fix at
   `a833066`: 23 cases, 9 PASS / 14 FAIL — reproduced locally before fixing).
3. Normative compact mirror restored byte-identical
   (`cmp` clean) with the revised same-PR continuation schedule; contract,
   fixture README (per-shape-family honest provenance; new real-format
   fixture), ledger, TESTING.md and the PR body agree on the bounded
   delivered slice and remaining 017 scope.
4. 53 new regression tests (184 → 237 focused tests) cover every retained
   finding through the public composition and the relevant primitive APIs,
   with clean positives and exact preservation of the 017-a preserved
   positives (source span, empty read, malformed root, escape-return).
5. Development provenance manifest refreshed (source A
   `3b97b1547bba455adbd9f7ee99a8704a1da2bacc`, inputs=179); frozen RC10
   publication bytes untouched; all eight required checks SUCCESS at the
   implementation head.

## Authoritative GitHub state
- Repository: `ulfe-lmi/slaif-local-coding`; PR #25
  https://github.com/ulfe-lmi/slaif-local-coding/pull/25 — OPEN, MERGEABLE,
  non-draft, single objective PR (no second PR for objective 017).
- Base `main` = `96c790423f6f0097a56a0b12bacda8a9b6da6aba` (unchanged).
- Starting remote PR/report head: `a833066ae25382bf7a9fdbe18f0dc1f479748de6`.
- Implementation head SHA: c82641574a45e543923c541f6d78e4e2568f25d8
- Report publication commit: SELF
- Implementation commits pushed before this report (over the starting head):
  - `3b97b1547bba455adbd9f7ee99a8704a1da2bacc` — 017-b: correct bounded
    observation proof defects (findings A-E) (38 files: 5 observer modules,
    5 test suites, 19 fixtures + README, contract/ledger/TESTING, both
    architecture docs + byte-identical compact mirror, activated order +
    `oap/active`).
  - `c82641574a45e543923c541f6d78e4e2568f25d8` — 017-b: refresh development
    provenance manifest (source A; manifest-only diff;
    `frozen_publication`/`release` sections byte-identical to the base).
- New PR this round: NO; amended existing: YES (PR #25); merge performed: NO;
  auto-merge: never enabled.

## Changes and files
Source (`src/slaif_local_coding/constitution/bundles/`):
- `tool_results.py` — wrapper: `Chunk ID:` + `Chunk Id:` header set; status
  fields at most once (repetition → `MALFORMED_WRAPPER`, frame carries no
  trusted status); bounded canonical ASCII decimal exit grammar;
  `max_wrapper_header_lines` enforced before frame acceptance (`OVER_BOUND`);
  read-level reasons propagate the wrapper's typed reasons. Eligibility:
  bare supported names / `write_stdin` / namespace-qualified with known
  executable leaf + exact compatible declaration. Endpoint-scoped pairing
  (Responses↔Responses, Chat↔Chat; cross-endpoint ID match typed
  missing/mismatched). Per-call `workdir` context before batch default.
  Surrogate content → typed `MALFORMED_UNICODE`, non-removable, no digest.
- `read_grammar.py` — `UnwrappedCommand` + `unwrap_call_arguments` (command +
  optional `workdir`; bounded JSON-string decode `2*max_command_chars+128`;
  decode errors typed, no broad swallowing); `unwrap_supported_arguments`
  kept as compatibility wrapper; option terminator processed once (later
  `--` is a literal operand); surrogate command → `MALFORMED_UNICODE` with
  explicitly absent digest.
- `observation_models.py` — `ReadCommandParse.command_digest` optional
  (`None` only under the typed malformed/unsupported contract; pattern still
  enforced when present).
- `root_envelopes.py` — scope label bound enforced in UTF-8 bytes.
- `__init__.py` — exports `UnwrappedCommand`, `unwrap_call_arguments`.
- `client_paths.py`, `observe.py` — unchanged (per-call workdir flows through
  the existing `PathContext.workdir` law).

Tests: 53 new tests across the six named suites (237 total) —
`TestRealFormatWrapper`, `TestContradictoryWrapperStatus`,
`TestWrapperBoundsAndGrammar`, `TestPerCallWorkdir`,
`TestToolEligibilityEvidence`, `TestEndpointScopedPairing`,
`TestMalformedUnicodeComposition` (tool results); `TestTerminatorMembership`,
`TestMalformedUnicodeCommand`, `TestCallArgumentShapes` (read grammar);
`TestLabelByteBound` (root envelopes); `TestOptionalCommandDigestContract`
(models); handoff fixture added to the end-to-end fixture expectations
(observe). All 184 pre-existing focused tests unchanged and passing.

Fixtures (`tests/fixtures/cache_bundles/v1/`):
- New `read_handoff_wrapper_format_responses.json` — human-handoff 6.2
  real-format wrapper (`Chunk ID:` + `Wall time:`) with exact source span.
- 18 `read_*` fixtures: `observed_format_authority` corrected to the honest
  per-shape-family provenance (root-only 0.149.0 capture record for root
  shapes; handoff 6.2 documented format + synthetic supplemental values for
  read call/result and wrapper shapes; no fresh-client trace claim). No
  payload bytes changed (authority line only).
- README.md — per-shape-family provenance statement.

Docs/ledger/mirror:
- `docs/CACHE-OBSERVATION-CONTRACT.md` — corrected wrapper/grammar/pairing/
  bounds/fixture law (sections 1, 2, 3, 4, 5, 8, 10, 11); D06-D10 deferred to
  later same-PR suffixes (017-c/d).
- `docs/CACHE-REWORK-LEDGER.md` — 017 status (017-a not accepted; 017-b
  corrects A-E; D06-D10 → 017-c/d); 017-b regression test names appended to
  D01-D05 rows (states remain `PENDING`).
- `TESTING.md` — continuation-schedule sentence corrected (umask 022
  prerequisite and coverage statements unchanged).
- `ARCHITECTURE-for-agents.md` — revised same-PR continuation schedule;
  `oap/strategic-instructions/ARCHITECTURE-for-agents.md` restored to
  **byte-identical** (`cmp` clean; `cmp` had failed at line 157 at
  `95270f2`).
- `ARCHITECTURE.md` — one-sentence status qualification for consistency.
- PR #25 body updated: bounded delivered slice, remaining 017 scope, and the
  actual current-development vs frozen-published Docker correction (CI
  validation correction only — no cache-runtime delivery claimed).

## Acceptance evidence
The seven order items are corrected with direct regression tests; the
independent probe is the cross-check (see Verification). Mapping (evidence
tables, not restated architecture):

| # | Order finding | Corrected behavior | Named regression evidence |
|---|---|---|---|
| 1 | Real-format wrapper | `Chunk ID:` + earned variant complete with exact span; repeated exit/truncation → `MALFORMED_WRAPPER` (no trusted status); source after `Output:` stays source; honest fixture provenance | `test_handoff_chunk_id_frame_is_complete_with_exact_span`, `test_handoff_fixture_parses_end_to_end`, `test_earned_chunk_id_variant_still_supported`, `test_zero_byte_read_under_real_format_stays_exact`, `test_contradictory_exit_headers_are_malformed`, `test_contradictory_exit_headers_not_complete_at_composition`, `test_contradictory_truncation_headers_are_malformed`, `test_repeated_identical_exit_header_is_malformed`, `test_single_status_fields_remain_complete`, `test_source_metadata_lookalike_does_not_redefine_wrapper` (preserved) |
| 2 | Read grammar membership | terminator once; later `--` literal operand kept in complete member list | `test_second_terminator_is_literal_operand`, `test_second_terminator_is_not_classified_as_flag`, `test_terminator_only_command_stays_empty`, `test_second_terminator_alone_is_literal_operand` (+ preserved `test_dash_dash_separator`, `test_two_operands_in_order`) |
| 3 | Per-call cwd | supported call `workdir` before batch default; outside/invalid typed | `test_per_call_workdir_resolves_relative_operands` (`/work/sub` → `sub/A.md`), `test_per_call_workdir_outside_workspace_is_not_complete` (`/work-other` never mapped), `test_per_call_workdir_does_not_shadow_absolute_operands`, `test_relative_workdir_is_typed_not_complete`, `test_control_character_workdir_is_typed_not_crash`, `TestCallArgumentShapes` (workdir shapes) |
| 4 | Tool/endpoint evidence | known executable leaf + compatible declaration; endpoint-scoped pairing | `test_declared_unrelated_bare_cmd_tool_is_not_exec`, `test_namespaced_unknown_leaf_with_declaration_is_not_exec`, `test_namespaced_known_leaf_still_supported_with_declaration` (preserved positive), `test_namespaced_known_leaf_without_declaration_is_not_exec`, `test_responses_call_with_chat_result_is_not_mixed`, `test_chat_call_with_responses_result_is_not_mixed`, `test_same_endpoint_pairing_preserved_for_both_envelopes` |
| 5 | Unicode/bounds | typed `MALFORMED_UNICODE` before hashing (digests absent, non-removable); label bound in UTF-8 bytes | `test_surrogate_command_is_typed_not_crash`, `test_surrogate_output_is_typed_not_crash`, `test_fingerprint_is_stable_for_surrogate_payload`, `TestOptionalCommandDigestContract`, `TestLabelByteBound` (incl. `/éééé` 9 bytes > 8-byte limit), preserved `test_surrogate_fixture_is_rejected_without_crash` |
| 6 | Parser bounds | `max_wrapper_header_lines` before frame acceptance; bounded ASCII numeric grammar | `test_header_line_bound_enforced_before_frame` (9 metadata + exit under limit 8), `test_header_line_bound_exact_limit_is_accepted`, `test_header_line_bound_over_bound_at_composition`, `test_unicode_digit_exit_is_typed_not_crash` (`²`), `test_excessive_numeric_exit_is_typed_not_crash` (5000 digits), `test_three_digit_exit_at_range_edge_is_valid_grammar`, `test_zero_padded_exit_is_not_the_documented_grammar`, `test_over_bound_argument_string_is_unsupported_without_parsing` |
| 7 | Normative mirror | mirror byte-identical; docs/ledger/PR body agree; Docker correction stated | `cmp ARCHITECTURE-for-agents.md oap/strategic-instructions/ARCHITECTURE-for-agents.md` clean (was failing at line 157 at `95270f2`); PR #25 body updated via REST PATCH (verified) |

## Verification
All local gate runs: process-local **umask 022** (verified non-root; host
umask 0002 unchanged), no sudo, no root.
- Independent probe before (reproduced at `a833066`): 23 cases, 9 PASS /
  14 FAIL, valid positive control (matches the strategic review record).
- Independent probe after (same immutable probe, `--head
  c82641574a45e543923c541f6d78e4e2568f25d8`): **23 cases, 23 PASS / 0 FAIL**,
  valid positive control, exit 0 — PASSED.
- `uv lock --check` — PASSED (no lock changes).
- `uv sync --frozen --extra dev` — PASSED (31 packages checked).
- `uv run --frozen ruff check .` — PASSED.
- `uv run --frozen ruff format --check .` — PASSED (after formatting the new
  code with the repo formatter; 488 files clean).
- `uv run --frozen mypy src tests` — PASSED (100 source files).
- `uv run --frozen python scripts/docs_consistency_check.py` — PASSED (19
  claim docs checked).
- Focused six-suite set (order-mandated):
  `uv run --frozen pytest -q tests/test_bundle_observation_models.py
  tests/test_bundle_client_paths.py tests/test_bundle_root_envelopes.py
  tests/test_bundle_read_grammar.py tests/test_bundle_tool_results.py
  tests/test_bundle_observe.py` — PASSED: 237 passed (184 pre-existing + 53
  new) at source A and unchanged at B.
- 8-file legacy/provenance regression set
  (`tests/test_observation.py tests/test_dependency_acquisition.py
  tests/test_pipeline.py tests/test_app.py tests/test_image_policy.py
  tests/test_tool_policy.py tests/test_dev_provenance.py
  tests/test_source_input_binding.py`) — PASSED: 267 passed at B (at A the
  two expected stale-manifest tests failed, as in 017-a, and passed once B
  landed).
- `uv run --frozen pytest -q` (complete locked gate, final source/context B,
  umask 022) — PASSED: **1780 passed, 27 skipped, 0 failed** (326.92s); the
  27 skips are the pre-existing explicit optional-fixture/live-layer skips
  (unchanged set).
- `uv build` — PASSED; wheel
  `dde945dabb8c15bed6a550d102d7dca316b89729dbca70e3fb977462e4991733`
  (107076 bytes, 34 entries), sdist
  `75a3770d7e316e57b8dc6b63224eddb6aa2dc181fb953215481f981a1640f897`
  (598068 bytes, 177 entries) — byte-identical to the refreshed manifest.
- `uv run --frozen python scripts/artifact_policy_check.py --dist dist
  --inspect` — PASSED (ok=true, no violations); `--install-smoke` — PASSED.
- `uv run --frozen python scripts/dev_provenance_manifest.py --verify
  --dist dist` — PASSED (`state=development head=c82641574a45`).
- `python3 -m compileall -q src tests oap/bin scripts` — PASSED.
- `bash -n` over `oap/bin/*.sh` and `packaging/*.sh` — PASSED.
- `git diff --check` (and cached) — PASSED.
- Targeted privacy/credential/raw-log scan over every changed path — clean;
  the only tree matches are the pre-existing protected live-host boundary
  lines in `ARCHITECTURE-for-agents.md` (+ its now byte-identical mirror),
  unchanged by this round.
- Unchanged frozen-publication/human-handoff hashes — PASSED:
  `docs/CACHE-REWORK.md` SHA256
  `410df5c0b8f90b05220adc32c8e673b143c0cf1fa3da02270d91ac453c886abd`;
  `frozen_publication` and `release` sections byte-identical to base
  `96c7904`; 017-a report/order, plan, `packaging/releases/` and the release
  provenance manifest untouched (`git status` clean for all of them).
- Independent clean `git archive` of source A in a 0700 temp root + fresh
  venv non-editable install — PASSED: archive-built wheel/sdist
  byte-identical to the manifest digests; `observe_request` executed in the
  fresh venv (handoff `Chunk ID:` frame + per-call workdir → `sub/A.md`,
  complete).
- Live model/Codex E2E — NOT RUN (the order authorizes none; no live product
  inference/API call was performed).
- Docker/operator/docker-published — remote CI evidence only; no Docker
  activity on this protected host.

## Live model/service evidence
NOT RUN. The order authorizes no live inference or API calls; no Qwen/vLLM,
qwen-serving, protected profile, or network fixture was touched.

## GitHub CI / required checks
Run 39179604878 at implementation head
`c82641574a45e543923c541f6d78e4e2568f25d8` — conclusion SUCCESS; all eight
required checks present and PASS (observed before the report commit):
- `test` — PASS (full suite on the runner: 1780 passed, 27 skipped)
- `docker` — PASS
- `operator-session` — PASS
- `gateway-contract` — PASS
- `docker-published` — PASS
- `CodeQL` — PASS
- `Analyze (python)` — PASS
- `Analyze (actions)` — PASS
All required green at drafting: yes. Report-only push may trigger new
checks at the report head; strategy verifies.

## Local setup/dependencies
- Host umask 0002; all gate runs under process-local umask 022 (verified
  context; no global/home chmod; no root; no sudo).
- Python 3.12 via repo `.venv` (uv 0.12.5, frozen lock); no new
  dependencies; `uv.lock` unchanged.

## Documentation
- Updated (as warranted by the corrections):
  `docs/CACHE-OBSERVATION-CONTRACT.md` (wrapper/grammar/pairing/bounds/
  fixture-provenance law), `docs/CACHE-REWORK-LEDGER.md` (017 status + 017-b
  regression names; states stay `PENDING`), `TESTING.md` (schedule sentence),
  `ARCHITECTURE-for-agents.md` + byte-identical strategic mirror (continuation
  schedule), `ARCHITECTURE.md` (status qualification), fixture README + 19
  fixture files (honest per-shape-family provenance).
- No adapter-active or overall rework-qualification claim anywhere; all v1
  runtime criteria remain `NOT RUN`.

## Safety/scope confirmations
- Unrelated/pre-existing work preserved; nothing reset/cleaned; working tree
  clean before the report commit.
- No secrets, prompts, raw bodies, or customer content in any artifact, log,
  fixture, or report; fixtures are synthetic and self-identifying;
  privacy scan clean.
- No production/protected resource touched: protected 18020/Qwen/Codex
  fixture changed: NO; no live inference; no Docker on this protected host;
  no API-key, firewall, VPN, systemd, model/venv/patch change.
- No new dependencies; no graph/cache/compiler/API integration; no
  registry/RC/publication/tag/version/benchmark/deployment/cutover.
- Required tests skipped/not run: none of the required local sets (the 27
  suite skips are the pre-existing explicit optional-fixture/live-layer
  skips, unchanged); live layers NOT RUN because not authorized.
- Scope deviation: none — exactly the activated 017-b scope; compound/loop/
  chunk D06-D10 explicitly not combined.
- Extra objective PR: NO (single PR #25 for objective 017); coding merge: NO;
  auto-merge: never enabled.
- Activated order/active edited after activation: NO (byte hashes verified
  at the implementation head).
- 017-a report/order and all earlier artifacts: unchanged.
- Report commit: report-only (sole path
  `oap/reports/017-b-observation-proof-corrections.md`), sole parent
  `c82641574a45e543923c541f6d78e4e2568f25d8`.

## Known limitations/blockers
- D06-D10 (chained reads, literal loops/`cd` workdir chains, per-read vs
  global exit evidence, multi-chunk completion proof, remaining truncation
  matrix) are NOT implemented; planned for later same-PR suffixes
  (017-c/d). Objective 017 cannot merge until D01-D10 are earned and
  independently reviewed.
- All v1 runtime stages (018-024) remain NOT RUN; the bundles package is
  inert (not wired into the adapter; legacy detector unchanged). A pure
  observation result claims nothing about active adapter caching or overall
  rework qualification.
- `COMPLETE` here is a claim for strategic review of the 017-b correction
  slice, never acceptance.

## Recommended strategic follow-up
Factual only: (1) independently re-run the immutable observer probe at the
report head (the 017-b implementation head already returns 23/23 with a valid
positive control); (2) review the A-E corrections and the corrected fixture
provenance; (3) choose the next same-PR suffix for the D06-D10
compound/loop/chunk scope (planned 017-c/d).

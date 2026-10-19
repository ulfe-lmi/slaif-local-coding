# OAP Coding-Agent Report — 017-c

## Work order
- Order: `oap/orders/017-c-literal-grammar-and-endpoint-corrections.md`
  (objective 017, round 017-c, AMEND_EXISTING_PR), SHA256
  `c6c44b00774eb45b2537574b39b2c1a9fde5c7aee31009786714bd60db15261d`;
  `oap/active` = `017-c` (bytes `017-c\n`, SHA256
  `47c8132b6ef14e27d4611d810f872eb7a81dcd1680a5ebd0360f25f59d982d34`);
  both committed unchanged with the implementation (activation bytes
  preserved, not edited).
- PR mode: AMENDED_EXISTING_PR — exact OPEN PR #25
  https://github.com/ulfe-lmi/slaif-local-coding/pull/25, base `main`, head
  branch `oap/017-cache-read-observation`. NO NEW PR; no coding merge or
  auto-merge.
- Starting remote PR/report head verified before mutation:
  `12382ee1b735f9ef5814fafb95264524339170e1` (sole parent
  `c82641574a45e543923c541f6d78e4e2568f25d8`); remote `main`
  `96c790423f6f0097a56a0b12bacda8a9b6da6aba` (unchanged); local working
  tree clean.
- Round start baselines (strategic, unchanged):
  `probes/check-read-option-semantics.py` 16 cases = 6 PASS / 10 FAIL
  (`reviews/017-b-final-argv-probes.json`);
  `probes/check-endpoint-selection.py` 5 cases = 2 PASS / 3 FAIL
  (`reviews/017-b-final-endpoint-probes.json`), both probed at the 017-b
  final head with valid positive controls.

## Status
COMPLETE for the bounded 017-c correction slice (literal argv semantics,
actual endpoint selection, bounds/privacy corrections in the inert
observation modules) — a claim for strategic review, not acceptance.
Objective 017 as a whole (D01-D10) remains open: D06-D10 (chained reads,
literal loops, per-read vs global exit evidence, multi-chunk process
pairing, remaining truncation matrix) move to later same-PR suffixes
(planned 017-d/e) per this order. The bundles modules remain inert: not
active in the adapter, legacy detector unchanged. All v1 runtime criteria
remain NOT RUN.

## Executive summary
1. All remaining 017-b probe failures corrected in
   `src/slaif_local_coding/constitution/bundles/` — no new syntax
   families; the simple `cat` families only, still pure, typed, inert:
   - New bounded literal lexer `shell_tokens.py`: raw span / cooked value /
     quoting / operator separation; ASCII whitespace the only separator
     class; no eval/execution/expansion; token repr carries spans/flags
     only, never text.
   - Quoting no longer disables cat's option parser: `cat '-n' A.md`,
     `cat '--number' A.md` are typed `COMMAND_UNSUPPORTED` — no
     option-named file members, no whole-file claims after formatting
     options.
   - Stdin operand `-` (quoted or unquoted, before or after the
     terminator) is typed `STDIN_OPERAND`, never a file member, never
     complete; literal `./-` and absolute paths ending `/-` stay distinct
     path operands.
   - `cat '--' A.md` (quoted terminator) proves only `A`; a later
     quoted/unquoted `--` after an already consumed terminator is a
     literal operand retained in the actual ordered members.
   - Unicode `isspace` (e.g. NBSP) is not a POSIX shell separator:
     `cat A.md<NBSP>B.md` is one ambiguous label, never a fabricated
     two-file read; ASCII tab/CR/control rejections preserved; valid
     Unicode paths still normalize.
   - Exact operand bound: exactly `max_operands` (32) completes; 33 is
     typed unsupported (supersedes the old `>=` off-by-one).
   - Per-call workdir with a lone surrogate returns a fixed typed
     `MALFORMED_UNICODE` read (relative and absolute operand variants)
     before any UTF-8 byte check — no `UnicodeEncodeError`, no
     placeholder digest, no raw exception echo.
   - Actual endpoint selection: `observe_request(..., endpoint=...)`
     accepts an explicit validated endpoint context and processes only its
     own container (absent container / invalid value typed, never
     guessed); unambiguous envelopes still inferred; mixed endpoint
     shapes are typed `ENDPOINT_UNSUPPORTED`, non-removable, with no
     acquisition from either container; global and per-read endpoint
     agree.
   - Bounds/privacy: `UnwrappedCommand` repr carries lengths/presence
     only (no raw command/workdir text); documented finite raw-argument
     cap (12 x `max_argument_chars` + 128) bounds the supported
     JSON-encoding worst case (supersedes the old 2x+128 heuristic).
2. All three unchanged strategic probes pass at the implementation head:
   `check-bundle-observation.py` 23/23, `check-read-option-semantics.py`
   16/16 (was 6/16), `check-endpoint-selection.py` 5/5 (was 2/5); valid
   positive controls; probes not edited.
3. 49 new regression tests (286 focused total); 27 standing
   fixture/live-layer skips honestly reported; full locked gate green
   locally; development artifacts byte-reproducible from the clean
   `git archive` of source commit A in a fresh venv, verified by a fresh
   non-editable install smoke.
4. Docs/contracts updated in the same PR: observation contract, ledger,
   TESTING, both architecture maps with byte-identical compact mirror,
   development provenance manifest B, PR description.

## Authoritative GitHub state
- PR #25: OPEN, mergeable, base `main`, head branch
  `oap/017-cache-read-observation` (reconciled before mutation and re-
  verified after push).
- New PR created: NO. Existing PR amended: YES. Merge/auto-merge: NO.
- Commits published this round (both on PR #25):
  - A = `bc3f6b68b941ab77e84673f40443bfe6b1cb9916` — "017-c: correct
    literal grammar and actual endpoint selection" (20 files: 7 source,
    5 test incl. 1 new, 4 docs + 1 byte-identical mirror, TESTING,
    activated order + `oap/active` with unchanged activation bytes).
  - B = `ad65077e88945e6511410d4395de650403247ed0` — "017-c: refresh
    development provenance manifest" (manifest-only; `frozen_publication`
    and release sections unchanged) — the implementation head.
- Remote branch and PR head both equal B at publication time; remote
  `main` still `96c790423f6f0097a56a0b12bacda8a9b6da6aba`.

Implementation head SHA: ad65077e88945e6511410d4395de650403247ed0
Report publication commit: SELF

## Changes and files (commit A, +1166/-144; commit B manifest-only)
Source (`src/slaif_local_coding/constitution/bundles/`):
- `shell_tokens.py` (new, 150 lines): `LiteralToken` (raw span, cooked
  value, quote state, operator flag) + `tokenize_command`; ASCII
  whitespace-only separators; no shell facilities imported.
- `read_grammar.py`: token-based parse loop; terminator decided by
  cooked value (`cat '--' A.md` proves only `A`); quoted options
  `'-n'`/`'--number'` typed `COMMAND_UNSUPPORTED` and never file members;
  stdin operand `-` (quoted/unquoted, pre/post-terminator) typed
  `STDIN_OPERAND`; literal `./-` / `/-`-suffixed paths distinguished;
  exact operand bound (32 complete / 33 typed); `UnwrappedCommand` repr
  privacy (lengths/presence only); documented raw-argument cap
  `12*max_argument_chars + 128`.
- `client_paths.py`: `validate_workspace` lone-surrogate guard (typed
  `AMBIGUOUS_PATH`-class result, no `UnicodeEncodeError`); token with any
  Unicode whitespace typed ambiguous (NBSP never splits into two files).
- `tool_results.py`: per-call workdir Unicode validated before UTF-8
  checks (relative and absolute operand variants typed
  `MALFORMED_UNICODE`, non-removable, no digest/exception echo);
  `observe_reads(selected_endpoint=..., suppress_acquisition=...)` —
  suppression turns paired reads under a mixed envelope into typed
  `ENDPOINT_UNSUPPORTED` with no members/digest/span; cross-endpoint ID
  typing (missing/mismatched) preserved.
- `observe.py`: `select_endpoint` (explicit validated context or
  unambiguous inference; `mixed`/`unknown` typed);
  `observe_request(..., endpoint=...)` — explicit endpoint scopes to its
  own container only; absent container/invalid value yields an unpaired
  `ENDPOINT_UNSUPPORTED` record with `endpoint="unknown"`; mixed shape is
  bookkeeping-only, no acquisition; root scan unchanged.
- `observation_models.py`: `Limitation.STDIN_OPERAND = "stdin_operand"`.
- `__init__.py`: exports for the new token API.

Tests (49 new; one pre-existing bound test updated to the documented
cap):
- `tests/test_bundle_shell_tokens.py` (new, 13): representation
  (spans/cooked/repr privacy), ASCII-only separators, quoting (clean /
  partial / nested / concatenated / inner metachar), operator
  classification without execution, no shell facilities imported.
- `tests/test_bundle_read_grammar.py` (+20): `TestQuotedOptionSemantics`
  (11), `TestNonAsciiWhitespaceNotASeparator` (5), `TestExactOperandLimit`
  (2), plus repr-privacy and documented-Unicode-cap cases.
- `tests/test_bundle_client_paths.py` (+3):
  `TestMalformedUnicodeAndSpaces`.
- `tests/test_bundle_tool_results.py` (+11):
  `TestMalformedWorkdirUnicode` (3), `TestEndpointSelection` (8).
- `tests/test_bundle_observe.py` (+2):
  `TestEndpointDomainAtComposition`.

Docs/contracts:
- `docs/CACHE-OBSERVATION-CONTRACT.md`: module list, no-spaces-all-
  whitespace rule, malformed-Unicode workdir rule, lexer/option-parser/
  separator semantics, exact operand limit, raw-argument cap, endpoint
  selection law, `stdin_operand` vocabulary, repr-privacy rule, 017-c
  provenance + planned 017-d/e schedule.
- `docs/CACHE-REWORK-LEDGER.md`: 017-b not accepted as A-E completion;
  017-c status recorded; D03/D04/D05 rows extended with 017-c regression
  names (stage states remain PENDING).
- `TESTING.md`: focused suite list + schedule sentence.
- `ARCHITECTURE-for-agents.md` + byte-identical mirror
  `oap/strategic-instructions/ARCHITECTURE-for-agents.md` (verified with
  `cmp`); `ARCHITECTURE.md` one-sentence qualification.
- `oap/orders/017-c-literal-grammar-and-endpoint-corrections.md` +
  `oap/active`: activated order committed unchanged (activation bytes).
- `packaging/dev_provenance_manifest.json` (commit B): refreshed
  development manifest (181 inputs = 179 + `shell_tokens.py` + its test;
  frozen-publication constants unchanged).

## Acceptance evidence (order finding -> corrected behavior -> named
regressions)
| Order finding | Corrected behavior | Named regressions (all PASSED) |
| --- | --- | --- |
| Bounded literal lexer, no eval/expand | `shell_tokens.py` raw/cook/quote/operator separation; ASCII whitespace only | `TestTokenRepresentation` (4), `TestQuoting` (4), `TestOperatorClassification` (5), `TestNoShellExecution` (1) |
| Quoted options are not files | `'-n'`/`'--number'` typed `COMMAND_UNSUPPORTED`, never members | `test_quoted_short_option_is_not_a_file_member`, `test_quoted_long_option_is_not_a_file_member` |
| Stdin operand `-` not a member | typed `STDIN_OPERAND`, never complete (pre/post-terminator, quoted/unquoted) | `test_quoted_stdin_is_not_a_file_member`, `test_unquoted_stdin_is_not_a_file_member`, `test_stdin_after_terminator_is_not_a_file_member` |
| Quoted terminator proves only A | `cat '--' A.md` -> members `(A,)`; no invented `--` file | `test_quoted_terminator_proves_only_the_operand` |
| Later `--` after consumed terminator is literal | ordered members retained, or typed unsupported | `test_second_quoted_terminator_retains_literal_members`, `test_option_like_name_after_terminator_is_literal`, `test_unquoted_terminator_positive_preserved`, `test_quoted_file_positive_preserved` |
| `./-`, `/-` vs special `-` | literal path operands distinguished from stdin | `test_literal_dash_paths_are_distinguished_from_stdin` |
| Unicode isspace is not a separator | NBSP token is one ambiguous label, never two files; tab/CR rejections kept | `test_nbsp_token_is_one_ambiguous_label_not_two_files`, `test_quoted_nbsp_inner_is_typed`, `test_ascii_tab_remains_explicitly_unsupported`, `test_carriage_return_remains_typed`, `test_valid_unicode_path_preserved`, `test_nbsp_path_label_is_typed_ambiguous` |
| Exact operand bound (32/33) | 32 complete, 33 typed unsupported; slot width/unknown hashes exact | `test_exact_limit_is_complete`, `test_one_over_limit_is_typed` |
| Workdir lone surrogate typed, no crash | `MALFORMED_UNICODE` read, no digest/placeholder/exception echo | `test_workspace_label_with_lone_surrogate_never_raises`, `test_relative_operand_with_surrogate_workdir_is_typed_not_crash`, `test_absolute_operand_with_surrogate_workdir_is_typed_not_crash`, `test_valid_unicode_workdir_is_still_proven` |
| Mixed endpoint shapes invent observations | typed `ENDPOINT_UNSUPPORTED`, non-removable, no acquisition either container; explicit endpoint scopes to own container | `test_mixed_complete_pairs_acquire_nothing`, `test_responses_shape_cannot_acquire_chat_pair`, `test_chat_shape_cannot_acquire_responses_pair`, `test_unambiguous_envelopes_still_complete`, `test_explicit_endpoint_scopes_to_its_container`, `test_explicit_endpoint_with_absent_container_is_typed`, `test_invalid_explicit_endpoint_is_typed`, `test_no_container_is_unknown`, `test_mixed_envelope_is_typed_mixed_and_non_removable`, `test_explicit_endpoint_at_composition` |
| repr leaks raw command/workdir | token repr spans/flags only; `UnwrappedCommand` repr lengths/presence only | `test_repr_carries_no_token_text`, `test_repr_omits_raw_command_and_workdir` |
| Raw argument cap not a JSON-encoding bound | documented finite cap `12*max_argument_chars + 128` | `test_unicode_command_within_documented_cap_still_decodes`, updated `test_over_bound_argument_string_is_unsupported_without_parsing` |

Strategic probes (unchanged files, canonical `.venv` Python,
`--head ad65077e88945e6511410d4395de650403247ed0`):
- `check-bundle-observation.py`: 23/23 PASS, positive control valid.
- `check-read-option-semantics.py`: 16/16 PASS (017-b baseline 6/16).
- `check-endpoint-selection.py`: 5/5 PASS (017-b baseline 2/5).
- Preserved 017-a/b positives (source span, empty read, malformed root,
  escape-return, duplicate/missing/mismatched IDs, qualified-tool
  evidence, input immutability) still pass inside the 286 focused set.

## Verification
All gates ran non-root under process-local umask 022 (host umask 0002
untouched); frozen installs; canonical repo `.venv`.

| Command (exact) | Result |
| --- | --- |
| `uv run --frozen pytest -q tests/test_bundle_*.py` | PASSED — 286 passed (0.82s; 237 retained + 49 new; per-file: client_paths 38, observation_models 23, observe 14, read_grammar 89, root_envelopes 32, shell_tokens 13, tool_results 77) |
| `uv run --frozen pytest -q tests/test_observation.py tests/test_dependency_acquisition.py tests/test_pipeline.py tests/test_app.py tests/test_image_policy.py tests/test_tool_policy.py tests/test_dev_provenance.py tests/test_source_input_binding.py` | PASSED — 267 passed (113.32s) |
| probes `check-bundle-observation.py` / `check-read-option-semantics.py` / `check-endpoint-selection.py` (unchanged, `--head` = implementation head) | PASSED — 23/23, 16/16, 5/5; valid positive controls; exit 0 |
| `uv lock --check` | PASSED |
| `uv sync --frozen --extra dev` | PASSED (31 packages) |
| `uv run --frozen ruff check .` | PASSED |
| `uv run --frozen ruff format --check .` | PASSED (492 files already formatted) |
| `uv run --frozen mypy src tests` | PASSED (102 source files) |
| `uv run --frozen python scripts/docs_consistency_check.py` | PASSED (19 claim docs) |
| `uv run --frozen pytest -q` | PASSED — 1829 passed, 27 skipped, 0 failed (326.96s); the 27 skips are the standing explicit optional-fixture/live-layer skips, not passes |
| `uv build` | PASSED — wheel `f31947b0ccedde35fb5c22c1a343f8948d40bf62e17ad7bf69fbc1f80c3a81ad` (113068 B), sdist `47ea52fa99990520fc3183dfcdc831cb4cdd077269d940a8c926670ad11c016d` (609556 B); digests equal the development manifest |
| `uv run --frozen python scripts/artifact_policy_check.py --dist dist --inspect` | PASSED (`ok: true`, no violations) |
| `uv run --frozen python scripts/artifact_policy_check.py --dist dist --install-smoke` | PASSED (`ok: true`, no violations) |
| `uv run --frozen python scripts/dev_provenance_manifest.py --verify --dist dist` | PASSED — `development provenance OK: state=development head=ad65077e8894` |
| `python -m compileall -q src tests oap/bin scripts` | PASSED |
| `bash -n` over `oap/bin/*.sh` + `packaging/readyz-wait.sh` | PASSED (4 scripts) |
| `git diff --check` | PASSED |
| Targeted privacy/credential/raw-log scan over round-added lines | PASSED — no credential patterns, no private URLs/host paths in added `src`/`tests` lines; this report contains hashes/counts/statuses only |
| Byte-identical normative mirror | PASSED — `cmp ARCHITECTURE-for-agents.md oap/strategic-instructions/ARCHITECTURE-for-agents.md` clean |
| Frozen/handoff/prior-OAP invariance | PASSED — `docs/CACHE-REWORK.md` SHA256 `410df5c0b8f90b05220adc32c8e673b143c0cf1fa3da02270d91ac453c886abd` unchanged; `packaging/releases/`, RC record/handoff, 016 and 017-a/b orders and reports unchanged since the round-start head; OAP transcript delta = 017-c order addition + `oap/active` (017-b -> 017-c); frozen RC10 binding re-proved by the manifest verification above |
| Independent clean `git archive` reproduction | PASSED — `git archive` of source commit A into a fresh 0700 temp root, fresh venv (Python 3.12.15) + frozen sync + `uv build`: wheel/sdist SHA256 byte-identical to the manifest digests; fresh non-editable install of the wheel in a second venv; `observe_request` smoke: Chat envelope with handoff 6.2 `Chunk ID:` wrapper frame and per-call workdir `/work` -> `sub/A.md` COMPLETE, `endpoint="chat"`, no raw body/chunk-id in the report dump; temp root removed after |

## Live model/service evidence
NOT RUN. The order authorizes no live inference or API calls; no
Qwen/vLLM, qwen-serving, protected Codex profile, or network fixture was
touched.

## GitHub CI / required checks
Check suites at implementation head
`ad65077e88945e6511410d4395de650403247ed0` (check-suite IDs 106179802287,
106179790857, 106179903904) — all eight required checks present and
SUCCESS (observed before the report commit):
- `test` — SUCCESS
- `docker` — SUCCESS
- `docker-published` — SUCCESS
- `gateway-contract` — SUCCESS
- `operator-session` — SUCCESS
- `CodeQL` — SUCCESS
- `Analyze (python)` — SUCCESS
- `Analyze (actions)` — SUCCESS

All required green at drafting: yes. The report-only push may trigger new
checks at the report head; strategy verifies.

## Local setup/dependencies
- Host umask 0002; every gate above ran under process-local umask 022
  (verified context; no global/home chmod; no root; no sudo).
- Python 3.12.15 via repo `.venv` (uv 0.12.5, frozen lock); no new
  dependencies; `uv.lock` unchanged.
- Temp roots/files for protected work created 0700/0600 and removed
  after use.

## Documentation
- Observation contract, ledger, TESTING.md, both architecture maps and
  the byte-identical compact mirror updated in this PR (same-commit docs
  law); PR #25 description rewritten for the 017-c slice (verified
  byte-identical after `PATCH` via `gh api`).
- No cache/runtime capability claims added: modules remain inert and all
  v1 runtime criteria remain NOT RUN.

## Safety/scope confirmations
- Protected live-host boundary: NO change to qwen-serving, its units/
  venv/models, port 18020, API-key files, firewall/VPN/bindings, or
  existing Codex profiles.
- No live inference, no host Docker execution (remote disposable CI
  runners only), no gateway/image-policy/release change.
- No new dependencies; no model weights; no secret or raw customer
  content in any commit, report, or PR text (scan above).
- Activated order/`oap/active` bytes NOT edited after activation; prior
  orders/reports/handoff/plan/frozen publication bytes unchanged;
  strategic probes NOT edited.
- Final commit changes only this report path with the implementation
  head as sole parent (verified below); no merge, no auto-merge, no
  second PR for objective 017.

## Known limitations/blockers
- D06-D10 (chained reads, literal loops, per-read vs global exit
  evidence, multi-chunk process pairing, remaining truncation matrix)
  not implemented this round — planned 017-d/e on the same PR; objective
  017 stays open until all D01-D10 are earned and independently
  reviewed.
- All v1 runtime stages (018-024: graph/admission, RAM working state,
  recovery, tokenizer/compiler, source replacement, adversarial
  acceptance, real-model qualification): NOT RUN.
- 27 standing fixture/live-layer skips are reported as skips, never as
  passes; local results do not impersonate the (separately listed)
  GitHub checks.
- COMPLETE here is a claim for strategic review, never acceptance.

## Recommended strategic follow-up (factual, non-directive)
- Independently re-run the three unchanged probes at the report head
  (they pass at the implementation head as evidenced above).
- Verify the report-head CI checks after this report-only push.
- If the 017-c slice is accepted as earned evidence for D03/D04/D05
  literal-grammar and endpoint-selection behavior, the remaining
  objective-017 scope is D06-D10 on later same-PR suffixes (017-d/e).

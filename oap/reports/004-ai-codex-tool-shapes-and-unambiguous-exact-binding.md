# OAP Coding-Agent Report — 004-ai

## Work order

- Identifier: `004-ai`
- Order path: `oap/orders/004-ai-codex-tool-shapes-and-unambiguous-exact-binding.md`
- Numeric objective: `004`
- PR mode: `AMENDED_EXISTING_PR`

## Status

FAILED

## Executive summary

The repository-only vision helper now has bounded fixed allowlists for standard
Responses custom/local-shell definitions and call/result item types, fixed
tool-shape diagnostic counts, fixed final-message wrapper classification, and
an explicit no-formatting rule in the synthetic delegated dependency. Focused
tests, Ruff, and configured mypy passed. The one authorized live acceptance
attempt failed with the fixed reasons
`("turn1_exact_sentinel", "turn2_exact_sentinel", "outbound_request_invalid")`.
No retry, alternate prompt, post-failure implementation edit, or protected
service operation was performed. Objective 004 remains at 90%; success-only
ledger/completeness updates were not made.

## Authoritative GitHub state

- Repository: `ulfe-lmi/slaif-local-coding`
- PR: #6 — https://github.com/ulfe-lmi/slaif-local-coding/pull/6 — `OPEN`, non-draft, clean.
- Base/head: `main` / `oap/004-real-codex-governed-e2e`.
- Starting remote SHA: `191673c227a8d0a7de269a949cbc39c4f70d7b54`.
- Implementation head SHA: `38a96467472829180ca773c7ae2bcd477a923687`.
- Report publication commit: SELF.
- Implementation commits pushed before report: `38a96467472829180ca773c7ae2bcd477a923687`.
- New PR this round: no; amended existing PR: yes; merge performed: NO.
- Implementation-head required check: `test` SUCCESS —
  https://github.com/ulfe-lmi/slaif-local-coding/actions/runs/32686756757/job/97313172764.

## Changes and files

- Added bounded structural recognition for definition types `function`,
  `custom`, and `local_shell`.
- Added bounded recursive item recognition for `function_call`,
  `function_call_output`, `custom_tool_call`, `custom_tool_call_output`,
  `local_shell_call`, `local_shell_call_output`, `command_execution`, and
  `exec_command`, with fixed `unexpected` diagnostic buckets and no dynamic
  tool data retention.
- Added fixed final-message labels for the specified wrappers; classification
  is diagnostic only and does not alter exact or terminal-CR/LF-only acceptance.
- Added the explicit no-quotes/no-markup/no-whitespace delegated dependency
  rule without adding the hidden token to prompts, config, or catalog.
- Added focused synthetic positive, negative, privacy, and wrapper tests.
- Committed the exact activated `oap/active` and `004-ai` order bytes unchanged.
- Files changed: `oap/active`,
  `oap/orders/004-ai-codex-tool-shapes-and-unambiguous-exact-binding.md`,
  `tests/helpers/vision_e2e_support.py`, and `tests/test_vision_e2e.py`.

## Acceptance evidence

### Criterion A — bounded Responses/Codex tool shapes

- PASSED focused synthetic coverage for every requested definition/item type,
  mixed recognized forms, nested bounded forms, malformed/empty/over-limit
  forms, unknown-only forms, spoof-shaped metadata, and privacy-safe summaries.
- FAILED live predicate: all four recorded main requests had
  `tool_content_preserved=false`.
- Fixed definition counts for each of the four requests, in category order
  `function`, `custom`, `local_shell`, `unexpected`: `(0, 1, 0, 2)`.
- Fixed item counts by request, in category order
  `function_call`, `function_call_output`, `custom_tool_call`,
  `custom_tool_call_output`, `local_shell_call`, `local_shell_call_output`,
  `command_execution`, `exec_command`, `unexpected`:
  - request 1: `(0, 0, 0, 0, 0, 0, 0, 0, 0)`;
  - request 2: `(1, 1, 0, 0, 0, 0, 0, 0, 0)`;
  - request 3: `(1, 1, 0, 0, 0, 0, 0, 0, 0)`;
  - request 4: `(2, 2, 0, 0, 0, 0, 0, 0, 0)`.

### Criterion B — unambiguous synthetic exact-response rule

- PASSED focused fixture test: the clarification is in the disposable
  delegated dependency; the hidden token is absent from the prompt, config,
  and model catalog.
- Live acceptance remained byte-exact or terminal-CR/LF-only and did not accept
  presentation wrappers.

### Criterion C — fixed wrapper classification

- PASSED focused exhaustive classification/non-acceptance/privacy coverage.
- FAILED live predicate: both event and output-file channels in both turns were
  classified `other_mismatch`, with byte length `39`, `exact_expected=false`,
  `terminal_line_endings_only=false`, and
  `non_whitespace_mismatch=true`. The safe observed SHA-256 was
  `2c7f245f7fb625543ee525b5c2ff799f7fca8b986bf01de02e72bca9db848d76`.

### Criterion E — exactly one live acceptance attempt

- FAILED. The exact ordered command ran once:
  `SLAIF_VISION_ACCEPTANCE=1 uv run --frozen pytest -q tests/test_vision_e2e.py -k live_vision_exec_resume_acceptance`
- Result: `1 failed, 78 deselected in 101.76s`.
- Safe run facts: same session `true`; catalog image capability, original-detail
  disabled, parallel tools disabled, and context `100000` all satisfied; phase
  counts `(2,2)`; image metric deltas `(2,0)` then `(4,2)`; both subprocesses
  exited `0` without timeout; each main request retained one expected image.

## Verification

- `git fetch origin --prune`: PASSED — remote reconciled before mutation.
- `uv run --frozen pytest -q tests/test_vision_e2e.py -k 'fixture_is_deterministic or tool_content or tool_shape or final_binding or fixed_final_message or marker_like or diagnostic_summary'`: PASSED — `49 passed, 30 deselected`.
- `uv run --frozen ruff check .`: PASSED.
- `uv run --frozen ruff format --check .`: PASSED — `174 files already formatted`.
- `uv run --frozen mypy src tests`: PASSED — 40 source files checked.
- `SLAIF_VISION_ACCEPTANCE=1 uv run --frozen pytest -q tests/test_vision_e2e.py -k live_vision_exec_resume_acceptance`: FAILED — exact single live attempt described above.
- Non-live full pytest after live failure: NOT RUN — order required stopping after live failure.
- Build/wheel boundary, compileall, shell syntax, and precise sensitive scans after live failure: NOT RUN — order required stopping after live failure.

## Live model/service evidence

- Read-only preflight: protected vision unit active/running, PID `364444`,
  `NRestarts=0`; text unit inactive; authenticated health/model statuses `200`;
  model `qwen3.8-27b`; context `100000`; image-limit flag present.
- Development port `18031` was free before the disposable candidate.
- No protected unit, model, network binding, key, profile, or service state was
  changed. The bounded candidate/fixture state was temporary and cleaned up by
  the test context before the failure was reported.

## GitHub CI / required checks

- Implementation-head `test`: SUCCESS at
  `38a96467472829180ca773c7ae2bcd477a923687`.
- All required implementation-head checks green at report drafting: yes.
- Report-head checks may be pending after publication; strategy verifies.

## Local setup/dependencies

- Used the existing frozen repository `uv` environment.
- No dependency, lockfile, production service, or persistent local runtime
  configuration changed.

## Documentation

- Success-only `docs/OBJECTIVE-004-LEDGER.md`, `docs/VISION-ACCEPTANCE.md`, and
  `oap/COMPLETENESS.md` were not changed because the live criterion failed;
  objective 004 remains at 90%.

## Safety/scope confirmations

- Unrelated files: preserved; only bounded repository-only helper/tests and the
  exact activation transcript were committed before this report.
- Secrets, raw prompts, source, images, tool output, bodies, credentials, and
  hidden token: not committed or reported.
- Protected 18020/Qwen/Codex fixture changed: NO.
- Second live attempt or post-failure implementation edit: NO.
- Extra objective PR: NO; coding merge/auto-merge: NO.
- Active/order edited by coding: NO; exact strategic bytes were committed.
- Final report commit report-only: yes.

## Known limitations/blockers

- The live fixture did not produce an exact or terminal-CR/LF-only final message
  at either observed boundary in either turn.
- The live recorder observed recognized and unexpected fixed tool categories but
  did not establish tool-content preservation; no raw request was retained, so
  no attribution is made to Local Coding, Codex, or the protected upstream.
- This report is not acceptance, merge, release, production-readiness, or a
  visual-quality claim.

## Recommended strategic follow-up

- Strategy should review the fixed live failure evidence and decide whether a
  later same-PR continuation is warranted. No next suffix is selected here.

# OAP Coding-Agent Report — 004-aj

## Work order

- Identifier: `004-aj`
- Order path: `oap/orders/004-aj-safe-codex-tool-type-capture-and-message-diff.md`
- Numeric objective: `004`
- PR mode: `AMENDED_EXISTING_PR`

## Status

FAILED

## Executive summary

One disposable no-model Codex 0.149.0 capture reached only a temporary
loopback fake Responses provider and retained the validated top-level tool type
labels/counts. The repository-only predicate was updated for the observed
standard categories and bounded privacy tests were added. Final-message
relationship diagnostics were added without changing exact or terminal-CRLF
acceptance.

The exact one authorized live vision acceptance attempt ran once and failed only
the fixed `turn1_exact_sentinel` and `turn2_exact_sentinel` reasons. Image
selection, phase grouping, governance preservation, session, metrics, tool
content, catalog, and protected fixture checks passed. No retry, acceptance-input
edit, protected service operation, or completion/ledger update was performed.

## Authoritative GitHub state

- Repository: `ulfe-lmi/slaif-local-coding`
- PR: #6 — `https://github.com/ulfe-lmi/slaif-local-coding/pull/6` — `OPEN`, non-draft, clean, mergeable.
- Base/head: `main` / `oap/004-real-codex-governed-e2e`.
- Starting remote SHA: `b311ef754fff7266365e5b660b587861e12d22df`.
- Implementation head SHA: `c0bb5b18d3e655e82bd4a871cc95bab07ea25acd`.
- Report publication commit: SELF.
- Implementation commits pushed before report: `c0bb5b18d3e655e82bd4a871cc95bab07ea25acd`.
- New PR this round: no; amended existing PR: yes; merge performed: NO.

## Changes and files

- Added one-request disposable no-model Codex tool-type capture with bounded
  ASCII labels, definition/unique-type limits, fixed error response, temporary
  state, and no raw request logging or result retention.
- Recognized only the observed standard definition categories `function`,
  `custom`, `tool_search`, and `web_search`; retained fixed `local_shell` and
  `unexpected` diagnostic buckets and required all definitions to be recognized.
- Added bounded final-message relation facts to both event and output-file
  evidence and fixed-shape summaries.
- Added positive, negative, bound, privacy, relation, and acceptance-preserving
  tests; documented the safe capture result.
- Files changed: `docs/VISION-ACCEPTANCE.md`, `oap/active`,
  `oap/orders/004-aj-safe-codex-tool-type-capture-and-message-diff.md`,
  `tests/helpers/capture_codex_tool_types.py`,
  `tests/helpers/vision_e2e_support.py`,
  `tests/test_capture_tool_types.py`, and `tests/test_vision_e2e.py`.

## Acceptance evidence

### Criterion A — disposable safe tool-type capture

- PASSED — exactly one Codex 0.149.0 invocation used the disposable synthetic
  fixture, image-capable catalog, global-yolo invocation shape, and loopback fake
  provider; no Local Coding or protected Qwen request was used.
- Safe ordered labels observed:
  `function, function, function, function, custom, function, function, function, function, tool_search, web_search`.
- Exact first-seen type/count tuple:
  `((function, 8), (custom, 1), (tool_search, 1), (web_search, 1))`.
- Only validated type labels/counts crossed the result boundary; names,
  descriptions, schemas, arguments, images, prompts, source, headers, body,
  response, credentials, and session identifiers were discarded.

### Criterion B — evidence-based structural allowlist

- PASSED — the predicate recognizes exactly the four observed standard
  categories above, rejects unobserved `local_shell` definitions, preserves
  fixed category counts and the `unexpected` bucket, and requires every
  top-level definition to be recognized.

### Criterion C — bounded final-message relationship evidence

- PASSED — exact, prefix/suffix/wrapper, missing, repeated, same-length
  unrelated, terminal-line-ending, and privacy cases are covered.
- Exact/terminal-CRLF acceptance remains unchanged; relation facts are
  diagnostic only and cannot set `sentinel_passed=true`.
- In the live failure, both event and output-file channels in both turns had
  byte length `39`, expected content present exactly once at offset `2`,
  `common_prefix_bytes=0`, `common_suffix_bytes=37`,
  `leading_extra_bytes=2`, and `trailing_extra_bytes=0`. Exact and
  terminal-CRLF acceptance were both false.

### Criterion D — one unchanged live vision attempt

- FAILED — the exact ordered command ran once and returned `1 failed, 88
  deselected in 84.00s`.
- Fixed reasons: `turn1_exact_sentinel`, `turn2_exact_sentinel`.
- Same session, catalog image capability, original-detail disabled, context
  `100000`, and parallel-tools disabled all passed.
- Phase counts were `(2, 2)`; image metric deltas were turn 1 `(seen=2,
  removed=0)` and turn 2 `(seen=4, removed=2)`.
- All four outbound main requests passed the bounded image, ordering,
  governance, non-image, and tool-content predicates.
- Live fixed definition categories, in order `function, custom, tool_search,
  web_search, local_shell, unexpected`, were `(0, 1, 1, 1, 0, 0)` for each
  request. Continuation item diagnostics contained only the fixed recognized
  `function_call`/`function_call_output` categories.

## Verification

- `git fetch origin --prune`: PASSED — remote reconciled before mutation.
- `uv run --frozen python -m tests.helpers.capture_codex_tool_types --codex-bin codex`: PASSED — one bounded no-model capture; safe labels/counts recorded above.
- `uv run --frozen pytest -q tests/test_capture_tool_types.py`: PASSED — `10 passed`.
- `uv run --frozen pytest -q tests/test_vision_e2e.py -k 'tool_content or tool_shape or final_binding or fixed_final_message or relationship or marker_like or diagnostic_summary or fixture_is_deterministic'`: PASSED — `59 passed, 40 deselected`.
- `uv run --frozen ruff check tests/helpers/capture_codex_tool_types.py tests/helpers/vision_e2e_support.py tests/test_capture_tool_types.py tests/test_vision_e2e.py`: PASSED.
- `uv run --frozen ruff format --check tests/helpers/capture_codex_tool_types.py tests/helpers/vision_e2e_support.py tests/test_capture_tool_types.py tests/test_vision_e2e.py`: PASSED.
- `uv run --frozen mypy src tests`: PASSED — 42 source files checked.
- `SLAIF_VISION_ACCEPTANCE=1 uv run --frozen pytest -q tests/test_vision_e2e.py -k live_vision_exec_resume_acceptance`: FAILED — exact single authorized attempt; fixed reasons above.
- Non-live full pytest after live failure: NOT RUN — order required stopping after the failed live acceptance.
- Build/wheel boundary, compileall, shell syntax, and precise sensitive scans after live failure: NOT RUN — order required stopping after the failed live acceptance.
- `git diff --check`: PASSED before implementation publication.

## Live model/service evidence

- Read-only preflight and post-attempt state: vision unit active/running at PID
  `364444`, zero restarts; text unit inactive; authenticated health and model
  status codes `200`; model present; process flags showed `qwen3.8-27b`,
  context `100000`, and the one-image limit; development port `18031` free
  afterward.
- The candidate adapter, disposable fixtures, cache, session, and logs were
  temporary and cleaned up by the test context.
- Protected Qwen/vLLM unit, model, port, network, credentials, and Codex
  profiles were not changed.

## GitHub CI / required checks

- Implementation-head `test`: SUCCESS at
  `c0bb5b18d3e655e82bd4a871cc95bab07ea25acd`.
- All required implementation-head checks green at report drafting: yes.
- Report-head checks may be pending after publication; strategy verifies.

## Local setup/dependencies

- Used the existing frozen repository `uv` environment and installed Codex
  0.149.0 binary.
- No dependency, lockfile, production service, or persistent runtime
  configuration changed.

## Documentation

- Updated `docs/VISION-ACCEPTANCE.md` with the bounded capture result and
  structural predicate scope.

## Safety/scope confirmations

- Unrelated files: none changed.
- Secrets/raw content: no raw request, response, prompt, source, image, tool
  data, credential, or private payload was retained or published.
- Production/protected resources: no mutation; protected 18020/Qwen/Codex
  fixture changed: NO.
- Required tests skipped/not run: full pytest, build/wheel, compileall, shell
  syntax, and precise sensitive scans after the live failure are NOT RUN.
- Extra objective PR: NO; coding merge: NO.
- Active/order edited: NO; activated bytes were committed unchanged.
- Report commit report-only: yes.

## Known limitations/blockers

- The live Codex final-message channels remain a fixed non-exact wrapper or
  prefix relationship and therefore do not satisfy the unchanged exact
  sentinel binding.
- No Local Coding product defect was established by the failed acceptance.
- Objective 004 remains at 90%; success-only ledger/completeness updates were
  not made.

## Recommended strategic follow-up

- Review the fixed live final-message relationship evidence and decide the next
  OAP objective; no retry or acceptance relaxation was performed.

# OAP Coding-Agent Report — 004-ah

## Work order

- Identifier: `004-ah`
- Order path: `oap/orders/004-ah-final-binding-provenance-and-tool-envelope.md`
- Numeric objective: `004`
- PR mode: `AMENDED_EXISTING_PR`

## Status

FAILED

## Executive summary

The repository-only acceptance support now recognizes bounded ordinary
top-level function definitions and records exact final-message evidence from
the last completed agent-message event and the output-file boundary. Focused,
static, non-live, packaging, and privacy checks passed. The one authorized live
vision acceptance attempt failed with the fixed reason tuple
`("turn1_exact_sentinel", "turn2_exact_sentinel", "outbound_request_invalid")`.
Both final-message channels were present but mismatched in both turns, and the
live recorder still reported `tool_content_preserved=false` for all four main
requests. No retry, alternate prompt, post-failure edit, or protected-service
operation was performed.

## Authoritative GitHub state

- Repository: `ulfe-lmi/slaif-local-coding`
- PR: #6 — https://github.com/ulfe-lmi/slaif-local-coding/pull/6 — `OPEN`, non-draft, mergeable.
- Base/head: `main` / `oap/004-real-codex-governed-e2e`.
- Starting remote SHA: `de3e041ad3ad8b59ce48df93f575d84f8f35e7c1`.
- Implementation head SHA: `7ef8fe3a306999e53efc1855bba60809d904d3c3`.
- Report publication commit: SELF.
- Implementation commits pushed before report: `7ef8fe3a306999e53efc1855bba60809d904d3c3`.
- New PR this round: no; amended existing PR: yes; merge performed: NO.
- Implementation-head required check: `test` SUCCESS; run/job observed at
  https://github.com/ulfe-lmi/slaif-local-coding/actions/runs/32685902710/job/97310781994.

## Changes and files

- Added bounded structural recognition for a nonempty top-level `tools` list
  containing supported function definitions while retaining actual call/result
  item recognition on continuation requests.
- Added immutable safe event/file final-message evidence with byte length,
  SHA-256, exactness, terminal CR/LF-only normalization, mismatch flags, and a
  fixed provenance label.
- Changed sentinel acceptance to require exact or terminal-CR/LF-only equality
  from the last completed agent message or output-file boundary; substring
  presence cannot pass.
- Added focused synthetic tool-definition, negative-shape, final-binding,
  last-message, and privacy tests.
- Committed the exact activated `oap/active` and `004-ah` order bytes unchanged.
- Files changed: `oap/active`,
  `oap/orders/004-ah-final-binding-provenance-and-tool-envelope.md`,
  `tests/helpers/vision_e2e_support.py`, and `tests/test_vision_e2e.py`.

## Acceptance evidence

### Criterion 1 — real tool-envelope preservation

- PASSED repository-only focused coverage: supported top-level function
  definitions, actual call/result items, empty/malformed/over-limit lists, and
  nested spoof-shaped data were tested without inspecting names, schemas,
  arguments, outputs, or raw tool text.
- FAILED live predicate: all four recorded main requests had
  `tool_content_preserved=false`; the live request body was not retained.

### Criterion 2 — exact final-binding provenance

- PASSED focused coverage for exact event/file values, CR, LF, CRLF, multiple
  terminal line endings, missing channels, earlier-exact/later-wrong messages,
  spaces/tabs, prefixes/suffixes, Markdown fences, marker-plus-sentinel, and
  non-whitespace mismatch.
- FAILED live predicate: both turns had event and output-file channels present,
  `exact_expected=false`, `terminal_line_endings_only=false`, and
  `non_whitespace_mismatch=true`; fixed provenance was `mismatch` for both.
- Safe live channel facts for both turns: byte length `39`; SHA-256
  `c4e74608e07bc56a08636cd29e9d4a4e7627fb257b6e47064171f6630c051107`.
- No sentinel value, final text, prompt, source, tool output, session ID, or
  arbitrary exception was serialized.

### Criterion 3 — exactly one live acceptance attempt

- FAILED. The exact ordered command ran once:
  `SLAIF_VISION_ACCEPTANCE=1 uv run --frozen pytest -q tests/test_vision_e2e.py -k live_vision_exec_resume_acceptance`
- Result: `1 failed, 55 deselected in 102.21s`.
- Safe live facts: same session `true`; catalog image capability, original-detail
  disabled, parallel tools disabled, and context `100000` all `true`; phase
  counts `(2,2)`; metric deltas `(2,0)` then `(4,2)`; both subprocesses exited
  `0` without timeout; four outbound `/v1/responses` requests had one expected
  image each, with full/full then crop/crop labels; image and governance
  preservation remained true.

## Verification

- `git fetch origin --prune`: PASSED — remote reconciled before mutation.
- `uv run --frozen pytest -q tests/test_vision_e2e.py -k 'tool_content or final_binding or marker_like_or_marker_plus_sentinel_output or failure_reasons or diagnostic_summary'`: PASSED — `44 passed, 12 deselected`.
- `uv run --frozen ruff format --check .`: PASSED — 172 files formatted.
- `uv run --frozen ruff check .`: PASSED.
- `uv run --frozen mypy src tests`: PASSED — 40 source files checked.
- `env -u SLAIF_VISION_ACCEPTANCE uv run --frozen pytest -q`: PASSED — `363 passed, 8 skipped`.
- `uv run --frozen python -m build --no-isolation`: FAILED — frozen environment lacked the already-declared `hatchling.build` backend.
- `uv run --frozen --with hatchling --with build python -m build --no-isolation`: PASSED — sdist and wheel built.
- Wheel boundary inspection: PASSED — 23 members, no `tests/`, `oap/`, or
  `.github/` members, and no model-weight extensions.
- `uv run --frozen python -m compileall -q src tests oap/bin`: PASSED.
- `bash -n` over repository shell files: PASSED.
- `git diff --check`: PASSED.
- Precise added-line secret/raw-logging scan: PASSED — zero hits.

## Live model/service evidence

- Read-only preflight and post-attempt checks: protected vision unit active and
  running, PID `364444`, `NRestarts=0`; text unit inactive/dead.
- Protected health status `200`; authenticated model metadata status `200`, model
  `qwen3.8-27b`, context `100000`.
- Development port `18031` was free before and after the disposable candidate.
- Temporary candidate, fixture, cache, and session state were cleaned up by the
  bounded test. Protected vision remained running.

## GitHub CI / required checks

- Implementation-head `test`: SUCCESS at
  `7ef8fe3a306999e53efc1855bba60809d904d3c3`.
- All required implementation-head checks green at report drafting: yes.
- Report-head checks may be pending after publication; strategy verifies them.

## Local setup/dependencies

- Used the existing frozen repository `uv` environment.
- Used transient `--with hatchling --with build` tooling only for the packaging
  check after the frozen environment lacked its declared build backend.
- No lockfile, production dependency, systemd unit, model, key, profile,
  firewall, VPN, or network configuration was changed.

## Documentation

- Success-only `docs/OBJECTIVE-004-LEDGER.md`, `docs/VISION-ACCEPTANCE.md`, and
  `oap/COMPLETENESS.md` were not changed because the live criterion failed;
  objective 004 remains at the prior 90% failure baseline.

## Safety/scope confirmations

- Unrelated files: preserved; only bounded helper/tests and exact activation
  transcript were committed before this report.
- Secrets/raw prompts/source/images/tool output/bodies/credentials/model weights:
  not committed or reported.
- Protected 18020/Qwen/Codex fixture changed: NO.
- Required live retry or additional real image call: NO.
- Extra objective PR: NO; coding merge/auto-merge: NO.
- Active/order edited by coding: NO; exact strategic bytes were committed.
- Final report commit report-only: yes.

## Known limitations/blockers

- The live fixture did not provide an exact or terminal-CR/LF-only final message
  at either observed boundary in either turn.
- The live recorder did not structurally recognize the ordinary tool envelope;
  no raw request was retained, so no attribution is made to Local Coding,
  Codex, or the protected upstream.
- The initial frozen build command remains unavailable without transient build
  backend provisioning; the documented fallback passed.
- This report is not acceptance, merge, release, production-readiness, or a
  visual-quality claim.

## Recommended strategic follow-up

- Strategy should review the fixed live failure evidence and decide whether a
  later same-PR continuation is warranted. No next suffix is selected here.

# OAP Coding-Agent Report — 004-ag

## Work order

- Identifier: `004-ag`
- Order path: `oap/orders/004-ag-safe-field-verdict-and-live-acceptance.md`
- Numeric objective: `004`
- PR mode: `AMENDED_EXISTING_PR`

## Status

FAILED

## Executive summary

The two ordered static failures were repaired, and the repository now emits a
fixed privacy-safe field verdict plus bounded diagnostics for the existing
vision acceptance predicates. The single authorized live acceptance attempt
ran exactly once and failed with the complete fixed reason tuple
`("turn1_exact_sentinel", "turn2_exact_sentinel", "outbound_request_invalid")`.
No retry, alternate prompt, request-cap change, acceptance-predicate change,
or protected-service operation was performed. No Local Coding product defect
is attributed without direct boundary evidence.

## Authoritative GitHub state

- Repository: `ulfe-lmi/slaif-local-coding`
- PR: #6 — https://github.com/ulfe-lmi/slaif-local-coding/pull/6 — `OPEN`, non-draft.
- Base/head: `main` / `oap/004-real-codex-governed-e2e`.
- Starting remote SHA: `425efa5343c0a692b21d0efb93e6f0aa4466cfdf`.
- Implementation head SHA: `8357ebb4b518d360debc18f06060a8af12ae9463`.
- Report publication commit: SELF.
- Implementation commits pushed before report: `8357ebb4b518d360debc18f06060a8af12ae9463`.
- New PR this round: no; amended existing PR: yes; merge performed: NO.
- Implementation-head required check: `test` SUCCESS at the implementation SHA.

## Changes and files

- Repaired only the ordered Ruff formatting and `Literal[1, 2]` typing issues.
- Added repository-only `vision_failure_reasons`, returning the ordered closed
  19-label vocabulary from the order.
- Kept the existing `successful` and `outbound_successful` compatibility views
  on the same aggregate predicate helpers used by the verdict.
- Added bounded diagnostics with fixed event-type buckets, fixed image labels,
  bounded statuses/counts, phase counts, and no raw payload fields.
- Added independent tests for every reason category, aggregate equivalence,
  outbound inclusion, and serialized-diagnostic privacy.
- No production adapter source, image/session/sentinel/metric acceptance rule,
  request bound, prompt, catalog, fixture, model, or service was changed.
- Strategic `oap/active` and the exact activated order were committed unchanged.

## Acceptance evidence

### Criterion 1 — static repair

- PASSED. Ruff formatting and linting passed, and `mypy src tests` passed with no
  issues.

### Criterion 2 — complete privacy-safe verdict

- PASSED. Focused verdict/privacy tests: `20 passed, 14 deselected`.
- PASSED. The focused suite independently forced all 19 closed reason labels;
  empty reasons matched `facts.successful and facts.outbound_successful`.
- PASSED. Serialized diagnostics excluded sentinel/session identifiers, data
  URLs, prompts, source/tool text, credentials, raw response content, and
  unallowlisted event/image strings.

### Criterion 3 — exactly one live acceptance attempt

- FAILED. Exact command ran once:
  `SLAIF_VISION_ACCEPTANCE=1 uv run --frozen pytest -q tests/test_vision_e2e.py -k live_vision_exec_resume_acceptance`
- Result: `1 failed, 33 deselected in 83.11s`.
- Complete fixed reason tuple:
  `("turn1_exact_sentinel", "turn2_exact_sentinel", "outbound_request_invalid")`.
- Sanitized supporting facts: same session `true`; catalog image capability,
  original-detail-disabled, parallel-tools-disabled all `true`; context window
  `100000`; metrics exact `true`; phase counts `(2, 2)`; metric deltas turn 1
  `(seen=2, removed=0)` and turn 2 `(seen=4, removed=2)`.
- Both turns exited `0`, timed out `false`, had event bytes `1044` and `1045`,
  tool calls `2` each, and exact sentinel `false`.
- Outbound evidence had four `/v1/responses` requests: two `full_scene` and two
  `right_crop`, one image seen per request; three requests were accepted. The
  first request had `tool_content_preserved=false`; no raw request or tool
  content was retained or reported.
- No completion ledger or completeness update was made after the failed live
  criterion.

## Verification

- `git fetch --prune origin`: PASSED — starting remote reconciled before mutation.
- `uv sync --frozen --extra dev`: PASSED — lock-frozen environment sync; no lock
  or source dependency mutation.
- `uv run --frozen ruff check .`: PASSED.
- `uv run --frozen ruff format --check .`: PASSED — 170 files already formatted.
- `uv run --frozen mypy src tests`: PASSED — 40 source files checked.
- `uv run --frozen pytest -q tests/test_vision_e2e.py -k 'failure_reasons or diagnostic_summary'`:
  PASSED — `20 passed, 14 deselected`.
- `env -u SLAIF_VISION_ACCEPTANCE uv run --frozen pytest -q tests/test_vision_e2e.py -k 'not live_vision_exec_resume_acceptance'`:
  PASSED — `33 passed, 1 deselected`.
- `env -u SLAIF_VISION_ACCEPTANCE uv run --frozen pytest -q`: PASSED — `341 passed, 8 skipped`.
- `uv run --frozen python -m build --no-isolation`: FAILED — the frozen local
  environment lacked the already-declared `hatchling.build` backend after sync.
- `uv run --frozen --with hatchling --with build python -m build --no-isolation`:
  PASSED — sdist and wheel built.
- Wheel boundary inspection: PASSED — 23 members, no `tests/`, `oap/`, or
  `.github/` members, and no model-weight extensions.
- `uv run --frozen python -m compileall -q src tests oap/bin`: PASSED.
- `bash -n` over repository shell files: PASSED.
- `git diff --check`: PASSED.
- Broad added-line secret heuristic: FAILED — matched an intentional synthetic
  test-only placeholder; no real credential or payload was present.
- Precise added-line secret scan: PASSED — no bearer value, private-key block,
  or long data URL.
- Added-line raw-logging scan: PASSED.

## Live model/service evidence

- Read-only before and after: `qwen-serving-vision.service` active/running,
  PID `364444`, `NRestarts=0`; text unit inactive/dead.
- Protected port `18020` health HTTP `200`; authenticated models HTTP `200`,
  model `qwen3.8-27b`, `max_model_len=100000`.
- Development port `18031` was free before and after the disposable candidate.
- Vision unit/runtime fingerprints were identical before and after; no protected
  unit, launcher, environment, profile, model, key, firewall, VPN, network, or
  vLLM state was changed.
- Temporary candidate, fixture, cache, and session state were cleaned up. No
  raw response, prompt, image, tool output, sentinel, credential, or session
  identifier was retained.

## GitHub CI / required checks

- Implementation-head check: `test` SUCCESS at
  `8357ebb4b518d360debc18f06060a8af12ae9463`.
- Check URL: https://github.com/ulfe-lmi/slaif-local-coding/actions/runs/32685103871/job/97308659060
- All required implementation-head checks green at report drafting: yes.
- Report-head checks may be pending after publication; strategy verifies them
  independently.

## Local setup/dependencies

- Used the existing frozen `uv` environment and disposable test state.
- Used `--with hatchling --with build` only for the repository-local packaging
  check after the frozen environment lacked its declared build backend.
- No lockfile, production dependency, systemd unit, model, key, profile,
  firewall, VPN, or network configuration was changed.

## Documentation

- Documentation updates were not required after a failed live attempt.
- Success-only `docs/OBJECTIVE-004-LEDGER.md`, `docs/VISION-ACCEPTANCE.md`, and
  `oap/COMPLETENESS.md` were not changed; completeness remains at the prior
  failure baseline.

## Safety/scope confirmations

- Unrelated work was preserved; only the exact active/order transcript and
  bounded repository-only test support were staged before the implementation
  commit.
- Secrets, raw prompts/source/images/tool output/bodies, credentials, and model
  weights were not committed or reported.
- Protected 18020/Qwen/Codex fixture changed: NO.
- Required live retry or additional real image call: NO.
- Extra objective PR: NO; coding merge/auto-merge: NO.
- Active/order edited by coding: NO; exact strategic bytes were committed.
- Final report commit report-only: yes.

## Known limitations/blockers

- The live fixture did not satisfy the exact sentinel predicate in either
  bounded invocation, and the first outbound request did not preserve tool
  content according to the existing recorder predicate.
- The broad heuristic scan is not a clean pass because of a synthetic test
  placeholder; the precise secret scan is clean.
- No direct evidence establishes whether the live failure belongs to Local
  Coding, the Codex fixture, or the protected upstream; no attribution is made.
- This report is not acceptance, merge, release, production-readiness, or a
  visual-quality claim.

## Recommended strategic follow-up

- Strategy should review the fixed live verdict and decide whether a later
  same-PR continuation is warranted. No next suffix is selected here.

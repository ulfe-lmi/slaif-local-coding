# OAP Coding-Agent Report — 004-ab

## Work order
- Identifier: `004-ab`; order: `oap/orders/004-ab-wire-live-vision-outbound-evidence.md`
- Numeric objective: `004`
- PR mode: `AMENDED_EXISTING_PR`

## Status
COMPLETE

## Executive summary
Prepared the human-gated vision acceptance path with an acceptance-only HTTPX
transport recorder wired into the real `create_app` path. Focused fake-upstream
tests prove the actual post-transform request contains the full image on turn 1
and only the newest crop on turn 2, while preserving non-image, tool, and
governance content. Live vision was not run; preparation is complete and
Objective 004 remains pending solely on the human-gated live vision criterion.

## Authoritative GitHub state
- Repository: `ulfe-lmi/slaif-local-coding`
- PR: #6 — https://github.com/ulfe-lmi/slaif-local-coding/pull/6 — OPEN
- Base/head: `main` / `oap/004-real-codex-governed-e2e`
- Starting remote SHA: `60e6204067f9e6f4f0cadd1fac8cdbd3536f9dab`
- Implementation head SHA: `28b21112e371e0703cba4cd8177a65b40c56fe6d`
- Report publication commit: SELF
- Implementation commits pushed before report: `28b2111` (`OAP 004-ab: wire vision outbound evidence`)
- New PR this round: NO; amended existing PR: YES; merge performed: NO

## Changes and files
- Added `VisionOutboundRecorder`, which observes only actual outbound
  `/v1/responses` requests, records bounded safe facts, ignores compiler
  `/v1/chat/completions` calls as main image turns, and forwards the same
  HTTPX request object to its configured transport.
- Replaced the handcrafted mapping proof with an actual `create_app` plus
  fake-upstream transport test covering full then newest-crop forwarding,
  content preservation, and metrics.
- Added invalid evidence rejection coverage for zero, duplicate, unknown,
  wrong-order, wrong-type, and mismatched images.
- Wired the same recorder into the future live candidate and strengthened
  exact final-message and direct resumed-session gates.
- Corrected `docs/VISION-ACCEPTANCE.md`; existing completeness remains 90% with
  live vision as the sole Objective-004 gap.

## Acceptance evidence
### Criterion 1
- PASSED: `tests/test_vision_e2e.py::test_outbound_recorder_is_wired_to_create_app_and_proves_newest_crop`
  constructs `create_app` with the recorder as its upstream transport; fake
  upstream receives the forwarded request object.

### Criterion 2
- PASSED: actual fake-upstream requests record `input_image`, exactly one
  expected image, `full_scene` then `right_crop`, expected byte lengths and
  SHA-256 values, preserved non-image/tool/governance facts, and image metric
  deltas `1/0` then `2/1`.
- PASSED: invalid recorder evidence cases are rejected.

### Criterion 3
- PASSED: the human-gated live test uses the same recorder-backed candidate and
  requires ordered full/crop facts, exact metrics, exact final binding, and a
  directly matching resumed thread.
- SKIPPED: live vision request; `SLAIF_VISION_ACCEPTANCE` was not enabled and
  the active order prohibits running the protected vision fixture.

### Criterion 4
- PASSED: no production module/config/API/log/metric behavior changed. No
  protected service, model, profile, network, credential, or port state was
  mutated.

### Criterion 5
- PASSED: frozen dependency, format, lint, typing, focused/full pytest, build,
  wheel/sdist boundary, compileall, shell syntax, diff, and sensitive-content
  checks are recorded below.

### Criterion 6
- PASSED: focused tests leave no candidate state; read-only listener check
  observed no 18021 or 18031 listener. The protected text service remained
  active/enabled and the vision service inactive/disabled.

### Criterion 7
- PASSED: PR #6 is the only objective PR; implementation-head CI `test` is
  SUCCESS; PR is OPEN, MERGEABLE, and CLEAN.

## Verification
- `uv run --frozen pytest -q tests/test_vision_e2e.py`: PASSED — 10 passed, 1 skipped (live gate).
- `uv run --frozen pytest -q`: PASSED — 318 passed, 8 skipped.
- `uv run --frozen ruff format --check .`: PASSED — 160 files already formatted.
- `uv run --frozen ruff check .`: PASSED.
- `uv run --frozen mypy src`: PASSED — 17 source files.
- `uv run --frozen python -m compileall -q src tests`: PASSED.
- `bash -n oap/bin/*.sh`: PASSED.
- `uv build`: PASSED — sdist and wheel built.
- `uv run --frozen python -m build`: BLOCKED — host Python lacks `ensurepip`; equivalent `uv build` succeeded.
- Wheel/sdist boundary scan: PASSED — repository-only support absent from wheel; source distribution retains repository sources/docs.
- `git diff --check`: PASSED.
- Sensitive-content scan over changed implementation/docs: PASSED.
- `SLAIF_VISION_ACCEPTANCE=1 uv run --frozen pytest -q tests/test_vision_e2e.py -k live_vision_exec_resume_acceptance`: SKIPPED by gate; no live vision request was made.

## Live model/service evidence
- Read-only host facts: `qwen-serving.service` active/enabled; `qwen-serving-vision.service` inactive/disabled; listener on port 18020 present; ports 18021 and 18031 absent during final check.
- Live adapter/model/vision calls: NOT RUN by the active order.
- Protected fixture change: NO.

## GitHub CI / required checks
- Implementation head `28b21112e371e0703cba4cd8177a65b40c56fe6d`: `test` SUCCESS — https://github.com/ulfe-lmi/slaif-local-coding/actions/runs/32675179150/job/97281934384
- All required checks green at drafting: YES.
- Report-head checks may be pending; strategy verifies them independently.

## Local setup/dependencies
- Used the existing repository `.venv` with `uv run --frozen`; no dependency or lockfile changes.
- `uv build` used the repository-local build path. No sudo, service, or protected-host setup action was performed.

## Documentation
- Updated `docs/VISION-ACCEPTANCE.md` to describe the actual transport boundary,
  fake readiness, live recorder requirements, exact binding, and session gate.
- No completeness change was required; the activated ledger already records
  90% readiness with live vision as the sole gap.

## Safety/scope confirmations
- Unrelated files: preserved; only order-authorized docs/test support plus the
  unchanged activated order/active transcript were committed.
- Secrets/raw prompts/source/images/tool output/request bodies/model responses:
  not retained in evidence, logs, metrics, Git, or this report.
- Protected 18020/Qwen/Codex fixture changed: NO.
- Required live vision test: SKIPPED by explicit order safety gate.
- Extra objective PR: NO; coding merge: NO.
- Active/order edited: NO; activated bytes were committed unchanged.
- Report commit report-only: YES.

## Known limitations/blockers
- Human-gated live vision remains unrun and is the sole external acceptance gap.
- The isolated `python -m build` command cannot create its environment because
  this host lacks `ensurepip`; `uv build` successfully produced both artifacts.

## Recommended strategic follow-up
- Human performs the documented mutually exclusive vision-unit switch and
  rollback, then runs the gated live test with the protected credential; strategy
  independently reviews the resulting outbound facts and report-head checks.

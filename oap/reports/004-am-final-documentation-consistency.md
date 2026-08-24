# OAP Coding-Agent Report — 004-am

## Work order
- Identifier: `004-am`
- Order path: `oap/orders/004-am-final-documentation-consistency.md`
- Numeric objective: `004`
- PR mode: `AMENDED_EXISTING_PR`

## Status
COMPLETE

## Executive summary

Updated the non-immutable product, architecture, test, operator, vision, and
completeness documentation to reflect accepted 004-s/004-w/004-x/004-aa/004-al
evidence. Historical 004-n percentage and workspace-write limitations remain
visible but are explicitly labeled historical. The existing focused documentation
status test was updated because it enforced the retired text-only wording. No
product, helper, live-test, service, or protected-fixture behavior changed.

## Authoritative GitHub state
- Repository: `ulfe-lmi/slaif-local-coding`
- PR: #6, https://github.com/ulfe-lmi/slaif-local-coding/pull/6
- PR state: OPEN, non-draft, MERGEABLE, CLEAN
- Base/head: `main` / `oap/004-real-codex-governed-e2e`
- Starting remote SHA: `eaf5eed27f550c72e6fb8da33e4cba5977e72b3c`
- Implementation head SHA: `2606de4c8cfc458d564ac8ac76189c706ecfefd6`
- Report publication commit: SELF
- Implementation commits pushed before report: `2606de4c8cfc458d564ac8ac76189c706ecfefd6`
- New PR this round: no; amended existing PR: yes; merge performed: NO

## Changes and files
- Updated `README.md`, `ARCHITECTURE.md`, `TESTING.md`,
  `docs/ADAPTER-CONFIGURATION.md`, `docs/LIVE-TEST-ENVIRONMENT.md`,
  `docs/VISION-ACCEPTANCE.md`, and `oap/COMPLETENESS.md`.
- Updated the existing focused documentation assertion in `tests/test_config.py`.
- Committed the unchanged activated `oap/active` and exact 004-am order.
- No Python product/helper/runtime behavior, live test, systemd unit, model,
  network, or protected service source changed.

## Acceptance evidence

### Criterion 1
- PASSED — repository-wide Markdown stale-claim inventory excluding immutable
  `oap/orders/` and `oap/reports/` found no unqualified current 004 15%/74%,
  vision-unready, native-compaction-proven, exact-binding, byte-exact aggregate,
  150000-vision, or multiple-upstream-image claim. Remaining percentage matches
  are explicitly historical or objective-weight facts.

### Criterion 2
- PASSED — current docs link to `docs/OBJECTIVE-004-LEDGER.md` and
  `oap/COMPLETENESS.md`; accepted fixture-scoped vision, CR/LF-only framing,
  `binding_effective`, `byte_exact_format=false`, one-image limit, native
  compaction non-claim, and gateway/cutover/production limitations are stated.

### Criterion 3
- PASSED — implementation diff is documentation plus the one existing focused
  documentation-contract test and unchanged OAP activation/order transcript.

### Criterion 4
- PASSED — Ruff, format, mypy, full pytest, build, wheel boundary, compileall,
  shell syntax, diff, credential-literal, raw-log, and documentation scans passed.
  Full pytest result: `438 passed, 8 skipped`. The host has no `python` alias,
  so `python -m compileall -q src tests oap/bin` was unavailable; the equivalent
  `python3 -m compileall -q src tests oap/bin` passed.

### Criterion 5
- PASSED — read-only checks reported `qwen-serving-vision.service` active,
  `qwen-serving.service` inactive, port 18020 listening, and ports 18021/18031
  absent. No model call, service operation, protected fixture mutation, or
  Codex-profile change was performed.

## Verification
- `uv run --frozen ruff check .`: PASSED — all checks passed.
- `uv run --frozen ruff format --check .`: PASSED — 184 files already formatted.
- `uv run --frozen mypy src tests`: PASSED — no issues in 42 source files.
- `uv run --frozen pytest -q`: PASSED — 438 passed, 8 skipped.
- `uv build`: PASSED — source distribution and wheel built.
- `python -m compileall -q src tests oap/bin`: NOT RUN — `python` executable is
  unavailable on this host.
- `python3 -m compileall -q src tests oap/bin`: PASSED.
- `for script in oap/bin/*.sh; do bash -n "$script"; done`: PASSED.
- Wheel boundary listing: PASSED — no repository-only tests, OAP transcript, or
  root docs in the wheel.
- `git diff --check`: PASSED.
- Credential-like literal and production raw-content logging scans: PASSED — no
  findings.
- Current-document stale-claim inventory: PASSED — only labeled historical or
  objective-weight percentage matches remain.

## Live model/service evidence

- Read-only unit/listener checks only; no model request was made.
- Vision fixture unit active, text fixture unit inactive, protected port 18020
  listening, and development/reference ports 18021 and 18031 absent.
- Protected Qwen/vLLM installation, model, launch flags, credentials, network
  bindings, and Codex profiles were unchanged.

## GitHub CI / required checks

- Implementation-head `test` check: SUCCESS at `2606de4c8cfc458d564ac8ac76189c706ecfefd6`.
- All required checks green at drafting: yes.
- Report-head checks may run after publication; strategy verifies them.

## Local setup/dependencies

- Used the existing repository-managed `uv` environment and frozen lockfile.
- No new dependency, service, sudo, or host setup was required.

## Documentation

Updated as listed above; no product contract or runtime behavior was changed.

## Safety/scope confirmations

- Unrelated pre-existing work was preserved.
- No secrets, raw prompts, source, images, tool output, credentials, or customer
  content entered the report or repository changes.
- Protected 18020/Qwen/Codex fixture changed: NO.
- Live model calls: none; live behavior tests: not run because the order forbids
  live calls and behavior changes.
- Extra objective PR: NO. Coding merge: NO.
- Active/order edited: NO; exact activated bytes were committed unchanged.
- Report commit report-only: yes.

## Known limitations/blockers

- Native Codex compaction triggering is not claimed or required by the accepted
  Objective-004 evidence; adapter-boundary rehydration is the accepted evidence.
- Vision evidence is limited to the selected Qwen3.8-27B/RTX 3090 fixture with
  100000 context and one upstream image. Gateway integration, production
  identity, cutover, reproducible release, and generic readiness remain later
  scope.
- The host does not provide the `python` command alias; `python3` verification
  passed.

## Recommended strategic follow-up

Review the amended PR and report-head CI through the strategic acceptance path.

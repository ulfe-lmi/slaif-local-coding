# OAP Coding-Agent Report — 004-ac

## Work order

- Identifier: `004-ac`
- Order path: `oap/orders/004-ac-group-vision-tool-loop-requests.md`
- Numeric objective: `004`
- PR mode: `AMENDED_EXISTING_PR`

## Status

COMPLETE

## Executive summary

Amended objective-004 PR #6 with repository-only vision acceptance support that
groups every main `/v1/responses` request inside two explicitly ordered Codex
invocation phases. Each phase is bounded and non-empty; compiler
`/v1/chat/completions` traffic remains ignored. Every recorded request is
validated for the expected full-scene or newest-crop image and preservation
facts. Image metric acceptance now scales from the observed phase counts. No
live vision request or production/protected-service change was made.

## Authoritative GitHub state

- Repository: `ulfe-lmi/slaif-local-coding`
- PR: #6, https://github.com/ulfe-lmi/slaif-local-coding/pull/6
- State: OPEN, non-draft, MERGEABLE/CLEAN
- Base/head: `main` / `oap/004-real-codex-governed-e2e`
- Starting remote SHA: `0dc07bc808ab22f9d47fd7e28048d828f6be8f73`
- Implementation head SHA: `befa201f09775265112ee31f03e57477abf04667`
- Report publication commit: SELF
- Implementation commits pushed before report: `befa201f09775265112ee31f03e57477abf04667`
- New PR this round: no
- Amended existing PR: yes, PR #6
- Merge performed: NO

## Changes and files

- `tests/helpers/vision_e2e_support.py`: added ordered phase lifecycle,
  attribution, finite request bounds, phase counts, scaled metric predicates,
  and all-request outbound acceptance.
- `tests/test_vision_e2e.py`: exercised the real `create_app`/recorder path
  with two main requests per invocation and added lifecycle, bound, ordering,
  compiler-ignore, and partial-invalid negative coverage.
- `docs/VISION-ACCEPTANCE.md`: documented multi-request tool loops, grouped
  phases, per-request validation, and count-scaled metrics.
- `oap/active` and the activated `004-ac` order were committed unchanged.

## Acceptance evidence

### Criterion 1

- PASSED — `VisionOutboundRecorder.begin_phase`/`end_phase` and `run_vision_e2e`
  explicitly bracket invocation 1 and invocation 2. Main traffic outside a
  phase, overlapping/reordered phases, empty phases, and oracle mismatches are
  rejected. Main requests are bounded at four per invocation.

### Criterion 2

- PASSED — fake-upstream `create_app` coverage sends two phase-1 requests and
  two phase-2 requests; all phase-1 facts are `full_scene`, all phase-2 facts
  are `right_crop`, and a partially invalid group is rejected by per-fact
  acceptance.

### Criterion 3

- PASSED — observed phase counts `(n1, n2)` validate `seen/removed` as
  `(n1, 0)` and `(2*n2, n2)`. The focused test proves `(2, 2)` produces
  `(2, 0)` then `(4, 2)` and rejects missing/unbounded counts.

### Criterion 4

- PASSED — focused tests cover out-of-phase, empty, overlapping, reordered,
  interleaved end, excessive, missing-second-phase, compiler-ignore, and
  partially invalid groups.

### Criterion 5

- PASSED — the future live-gated runner invokes the phase API around both real
  Codex subprocesses and requires grouped outbound success, scaled metrics,
  same-session binding, exact final-message binding, model lifecycle facts,
  privacy, and cleanup. Live vision itself was not run in this preparation
  round.

### Criterion 6

- PASSED — repository-only helper/tests/docs changes; no production source or
  protected configuration/API/log/metric behavior change.

### Criterion 7

- PASSED — read-only checks show `qwen-serving.service` loaded,
  active/running/enabled on port 18020; `qwen-serving-vision.service` loaded,
  inactive/dead/disabled; and no listener on 18021 or 18031. Same PR only and
  no merge.

## Verification

- `uv run --frozen pytest -q tests/test_vision_e2e.py`: PASSED — 11 passed, 1 skipped; the skip is the human-gated live vision test.
- `uv run --frozen pytest -q`: PASSED — 319 passed, 8 skipped; gated live suites remained skipped.
- `uv run --frozen ruff check . && uv run --frozen ruff format --check .`: PASSED — all checks; 162 files formatted.
- `uv run --frozen mypy src tests`: PASSED — no issues in 40 source files.
- `uv run --frozen python -m build --no-isolation`: PASSED — sdist and wheel built successfully after repo-local `hatchling` setup.
- `uv run --frozen python -m compileall -q src tests`: PASSED.
- shell syntax scan over repository `*.sh`: PASSED.
- `git diff --check` and added-line secret scan: PASSED.
- `gh pr checks 6 --repo ulfe-lmi/slaif-local-coding --watch --interval 5`: PASSED — GitHub CI `test` SUCCESS at implementation head.

## Live model/service evidence

- Read-only `systemctl --user show` and listener checks only.
- Text Qwen service: loaded, active/running/enabled; port 18020 listening.
- Vision service: loaded, inactive/dead/disabled.
- Ports 18021 and 18031: no listener after tests.
- Live vision acceptance: SKIPPED — explicitly prohibited by `004-ac`; no live
  vision request or protected service switch was made.

## GitHub CI / required checks

- Implementation-head check: `test` — SUCCESS, completed 2026-08-24 at
  `befa201f09775265112ee31f03e57477abf04667`.
- All required checks green at drafting: yes.
- Report-head checks: strategy verifies after publication.

## Local setup/dependencies

- Used the existing repo-local `.venv` and `uv run --frozen` commands.
- Installed missing build backend `hatchling>=1.27` into the repo-local
  environment only so the no-isolation build could run. No system package,
  protected service, model, key, profile, firewall, VPN, or network mutation.

## Documentation

- Updated `docs/VISION-ACCEPTANCE.md` in the same implementation commit.
- Existing objective completeness remains 90%, with live vision the sole
  remaining objective-004 gap.

## Safety/scope confirmations

- Unrelated files: preserved; only the five listed implementation/order paths
  were committed before this report.
- Secrets/raw prompts/source/images/tool output: not retained in code evidence,
  report, logs, or metrics.
- Protected 18020/Qwen/Codex fixture changed: NO.
- Required live vision tests: SKIPPED by order and inactive protected fixture.
- Extra objective PR: NO.
- Coding merge: NO.
- Active/order edited: NO.
- Final report commit report-only: yes.

## Known limitations/blockers

- Live vision full-image/newest-crop behavior remains pending on the
  human-gated protected fixture. Preparation evidence does not claim live
  vision capability or production readiness.
- The default isolated build command could not create its temporary environment
  because host Python lacks `ensurepip`; the repository-local no-isolation build
  passed after installing the declared build backend in `.venv`.

## Recommended strategic follow-up

- Strategy may independently schedule the human-gated live vision run after
  deliberate protected fixture activation and read-only verification.

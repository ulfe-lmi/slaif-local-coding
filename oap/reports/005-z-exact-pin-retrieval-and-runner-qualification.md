# OAP Coding-Agent Report — 005-z

## Work order

- Identifier: `005-z`
- Order: `oap/orders/005-z-exact-pin-retrieval-and-runner-qualification.md`
- Numeric objective: Objective-005
- PR mode: `AMENDED_EXISTING_PR`

## Status

COMPLETE

## Executive summary

Completed the exact Gateway ancestor retrieval, corrected operation/phase/kind/
ordinal/lifetime dispatch attribution, measured candidate readiness, serialized
vision phase transitions, and repaired post-dispatch stream cleanup. The exact
pinned fake C1–C5/D machine gate completed with 37/37 obligations and
projections passed. The fresh run recorded 23 actual direct dispatches: 6
compiler, 12 inference, and 5 other; all 12 inference streams were
terminal-valid and fake-provider counters matched the direct observer.

The healthy synthetic protected branch reached the shared runner with 6
compiler and 12 inference lifecycle counts, all 29 protected dispositions,
zero primary failure, and unchanged protected-fixture facts. It remains
explicitly non-accepting and used only a disposable loopback provider. No
protected credential, authenticated Qwen request, port-18020 mutation, cutover,
merge, or release action occurred.

## Authoritative GitHub state

- Repository: `ulfe-lmi/slaif-local-coding`
- PR: 7 — https://github.com/ulfe-lmi/slaif-local-coding/pull/7
- State: OPEN; draft: NO; merge state: CLEAN; mergeable: MERGEABLE
- Base/head: `main` / `oap/005-gateway-ingress-integration`
- Starting remote SHA: `d56be56d01ccb070594df941810fb2a77b334d33`
- Implementation head SHA: `91cb1b3ac990d10052944d18f5f14e35422f2592`
- Report publication commit: SELF
- Implementation commits pushed before report:
  `db6d3b7`, `98c58f0`, `7f75d66`, `be2357e`, `da1a231`, `14e30d9`,
  `68cdd3c`, `de5d77b`, `1255cc5`, `55de5c3`, `bb485f5`, `91cb1b3`
- New PR this round: NO; amended existing: YES; merge performed: NO

## Changes and files

- `tests/helpers/acceptance_harness.py`: exact operation context and lifetime
  authorization, explicit transitions, bounded plan allocation, and safe
  dispatch evidence.
- `tests/helpers/transport_observer.py`: operation/lifetime recording,
  terminal-response transition seam, serial readiness probe seam, and returned
  stream cleanup when a post-dispatch hook fails.
- `scripts/gateway_accounting_rehearsal.py`: exact candidate readiness,
  Codex/vision operation transitions, serial synthetic protected execution,
  protected fixture fact retention, early-failure projection, and cleanup.
- `tests/helpers/vision_e2e_support.py`: explicit transition between the two
  ordered vision phases.
- `tests/test_acceptance_harness.py`, `tests/test_transport_observer.py`:
  wrong-operation, stale-lifetime, expiry, transition, hook-failure, and
  response-close regressions.
- `TESTING.md`, `docs/SLAIF-GATEWAY-INTEGRATION.md`: measured 25-slot ceiling,
  actual 23-dispatch result, exact pin, readiness, and synthetic limitations.
- `oap/active` and the exact 005-z order: committed byte-for-byte as the
  activated orchestration transcript.

## Acceptance evidence

### Criterion A — exact dependency retrieval

- PASSED — A disposable authenticated Git checkout retrieved executable
  Gateway commit `50dcc3b85d614eb1d0c6196595bf22ef5779f846`.
- PASSED — `merge-base --is-ancestor 50dcc3… d142fd7…` succeeded.
- PASSED — Executable pin and merged-main app tree both resolved to
  `c0204deaff3cfd055a25f29a7f5d8d3c5e161d57`.
- PASSED — Detached Gateway checkout was clean; no Gateway product files,
  PRs, dependencies, or installed services were changed.

### Criterion B — exact operation dispatch permissions

- PASSED — Current context now includes operation, phase, ordinal, and opaque
  lifetime; reservation never advances current context or borrows another
  operation’s allowance.
- PASSED — Regressions cover wrong ordinal, wrong phase, wrong kind, missing or
  exhausted slots, stale lifetime, expiry, explicit turn transition, and
  delegate-call counts before rejection.
- PASSED — Actual final fake run used the observed 23-dispatch shape while the
  authorized plan remains a 25-slot ceiling: 6 compiler, 14 inference, 5
  other.

### Criterion C — synthetic protected runner

- PASSED — Healthy shared-runner synthetic execution reached phases
  `codex`, `vision`, `vision`, `codex`, and finalization with 6 compiler and 12
  inference attempted/dispatched/responded/completed counts; primary failure
  was absent.
- PASSED — All 29 selected protected rows serialized; protected PID, start,
  listener, text-inactive, no-18021, no-18031, and worktree facts remained
  unchanged.
- PASSED — Observer-failure injection stopped after one compiler dispatch with
  zero inference dispatches, preserved `observer_readiness_lost` as primary,
  serialized all 29 rows, and cleaned all task resources.
- PASSED — Combined observer/projection/cleanup failure retained the same
  primary failure, recorded bounded secondary classes, serialized all 29 rows,
  and did not dispatch later inference.
- NOT ACCEPTED BY DESIGN — `protected_acceptance=false`; synthetic loopback
  evidence does not establish protected Qwen inference acceptance.

### Criterion D — exact fake matrix and repository gates

- PASSED — Fresh exact pinned fake C1–C5/D gate: 37/37 obligations and
  projections passed; `missing=[]`; no retry; direct observer/fake-provider
  agreement true; 12/12 inference streams terminal-valid.
- PASSED — Candidate `/healthz` and `/readyz` were both HTTP 200.
- PASSED — Fake cleanup, private disposable resources, and secret-free logs
  passed.
- NOT RUN — Real protected matrix, cutover, merge, and release readiness; all
  are prohibited or unaccepted by this order.

## Verification

- `uv run --frozen pytest -q`: PASSED — 747 passed, 8 skipped; skips remain
  explicit live/host gates.
- `uv run --frozen pytest -q tests/test_acceptance_harness.py tests/test_transport_observer.py tests/test_gateway_accounting_rehearsal.py`: PASSED — 193 passed.
- `uv run --frozen pytest -q tests/test_acceptance_harness.py tests/test_transport_observer.py tests/test_vision_e2e.py tests/test_gateway_accounting_rehearsal.py`: PASSED — 312 passed, 1 skipped.
- `uv run --frozen ruff format --check .`: PASSED — 261 files formatted.
- `uv run --frozen ruff check .`: PASSED.
- `uv run --frozen mypy src tests`: PASSED — 57 files, no issues.
- `uv run --frozen python -m compileall -q scripts tests/helpers src`: PASSED.
- `bash -n oap/bin/*.sh`: PASSED.
- `uv build --wheel --sdist`: PASSED — wheel and sdist built.
- `git diff --check`: PASSED.
- Exact Codex fixture SHA-256: PASSED —
  `bbc3341e44c9ead340ed9570c17be936e37870f570751a941699ffd04d672827`.
- Exact fake rehearsal: PASSED — COMPLETE, 37/37, 23 actual dispatches,
  6/12/5 compiler/inference/other, exact fake-provider agreement, cleanup.
- `gh pr checks 7`: PASSED — `test`, run `34416670243`, job `102682963570`,
  SUCCESS at implementation head.

## Live model/service evidence

- Read-only protected process: PID `23961`, command class `vllm`, start
  `Sun Sep 6 18:57:26 2026`.
- Read-only listener: port `18020` remained bound by PID `23961`; unauthenticated
  `/health` returned HTTP 200 without reading or retaining its body.
- Read-only unit state: `qwen-serving.service` reported
  `ActiveState=inactive`, `SubState=dead`, `MainPID=0`, `NRestarts=0`; this
  known systemd/unit-versus-live-process discrepancy was preserved and not
  normalized.
- Ports `18021`, `18030`, and `18031` were not listening after cleanup.
- Protected credential, `/proc` environment, authenticated/model/compiler/
  inference/vision request, model contents, logs, and service configuration:
  NOT RUN.

## GitHub CI / required checks

- Implementation-head `test`: SUCCESS — run `34416670243`, job `102682963570`.
- All required checks green at report drafting: YES.
- Report-head checks may be pending after the report-only push; strategy
  verifies them independently. No report rewrite is authorized.

## Local setup/dependencies

- Used existing local frozen environment for repository gates.
- Used a disposable detached Gateway checkout and task-owned Gateway venv;
  no Gateway workspace, dependency lock, protected installation, or service
  was mutated.
- Used task-owned temporary PostgreSQL/loopback/fake-provider resources only;
  cleanup passed.

## Documentation

Updated `TESTING.md` and `docs/SLAIF-GATEWAY-INTEGRATION.md` with the measured
dispatch ceiling versus actual run count, exact pin provenance, readiness
predicate, serial candidate lifetime, and protected non-acceptance limits.

## Safety/scope confirmations

- Protected 18020/Qwen/Codex fixture changed: NO.
- Protected model, checkpoint, venv, unit, launch flags, GPU, key, firewall,
  VPN, network binding, and active profile changed: NO.
- Secrets, credentials, raw prompts, source, images, tool output, SSE bodies,
  private URLs, and customer data entered the report/logs: NO.
- Unrelated files/work preserved; only ordered helper, runner, tests, docs,
  active/order transcript, and this report are in scope.
- Extra objective PR: NO; coding merge/auto-merge: NO.
- Active/order edited after activation: NO.
- Report commit report-only: YES; parent must equal the implementation SHA
  above.

## Known limitations/blockers

- Protected inference acceptance, cutover, merge, and release readiness remain
  NOT RUN/unaccepted.
- The systemd unit state and live PID/listener state remain discrepant; no
  remediation was authorized.
- The fake run proves the exact tested Gateway/Codex/Local fixture and does not
  establish production or generic hardware equivalence.

## Recommended strategic follow-up

Review the complete 005-z evidence, the protected non-acceptance boundary, and
current PR checks. Strategy decides acceptance, merge, release, and any next
objective; coding does not infer those decisions.

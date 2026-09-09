# OAP Coding-Agent Report — 005-u

## Work order

- Identifier: `005-u`
- Order: `oap/orders/005-u-close-stream-and-predispatch-proof.md`
- Numeric objective: Objective-005
- PR mode: `AMENDED_EXISTING_PR`

## Status

COMPLETE

## Executive summary

Closed the DirectTransportObserver stream-ownership and inference-admission
safety gaps. Normal and abnormal response lifecycles now close delegates exactly
once with idempotent repeated close, and validator/profile construction happens
before any Responses delegate dispatch. Added real loopback streaming proof,
closure/preflight regressions, round-neutral Git-topology reuse validation, and
updated the current testing/integration documentation. The exact clean fake
qualification passed all selected obligations.

## Authoritative GitHub state

- Repository: `ulfe-lmi/slaif-local-coding`
- PR: #7 — https://github.com/ulfe-lmi/slaif-local-coding/pull/7
- State: OPEN, non-draft, MERGEABLE
- Base/head: `main` / `oap/005-gateway-ingress-integration`
- Starting remote SHA: `c908b6ec1b1a7b5ec93d0184386fb225387bd1de`
- Implementation head SHA: `90460f23ec763b9503ba6ad2c32397def8a1430f`
- Report publication commit: SELF
- Implementation commits pushed before report: `90460f23ec763b9503ba6ad2c32397def8a1430f`
- New PR this round: NO
- Amended existing PR: YES, PR #7
- Merge or auto-merge performed: NO

## Changes and files

- `tests/helpers/transport_observer.py`: separates observation finalization from
  delegate closure; closes delegates once across normal, early, cancellation,
  timeout, truncation, and exception paths; preserves original failures; adds
  inference capability/preflight and accurate attempted/dispatched state.
- `scripts/gateway_accounting_rehearsal.py`: requires observer inference
  capability at candidate startup and validates only a round-neutral,
  single-parent immutable report-only child for tested-source reuse.
- `tests/test_transport_observer.py`: adds JSON/SSE closure regressions, real
  `AsyncHTTPTransport` loopback backpressure, cancellation/timeout/truncation/
  exception coverage, validator admission negatives, and candidate preflight.
- `tests/test_gateway_accounting_rehearsal.py`: adds disposable Git-fixture
  tests for valid report-only reuse, dirty/changed source, malformed paths,
  and multi-parent rejection.
- `TESTING.md` and `docs/SLAIF-GATEWAY-INTEGRATION.md`: document the tested
  lifecycle, pre-dispatch, loopback, validator, and reuse guarantees.
- Activated `oap/active=005-u` and committed the exact `005-u` order unchanged.

## Acceptance evidence

### Criterion A — exact stream closure

- PASSED — JSON and SSE normal exhaustion close the delegate exactly once;
  repeated `response.aclose()` remains idempotent.
- PASSED — Early close, cancellation, timeout, truncation, delegate exception,
  and close-error paths close once, clear abnormal state, preserve the original
  stream error/cancellation, and never mark an abnormal/truncated stream
  terminal-valid.
- PASSED — The real loopback test with actual HTTPX `AsyncHTTPTransport`
  withheld terminal output until the client received the first chunk and then
  verified exact bytes, status/headers, one dispatch, and connection closure.

### Criterion B — pre-dispatch prerequisites

- PASSED — Missing, raising, and invalid validator factories are rejected before
  `delegate.handle_async_request`; the admission record is attempted but not
  dispatched, and the delegate call count remains zero.
- PASSED — Latched readiness blocks later inference admission; compiler handling
  remains available without an inference validator bypass.
- PASSED — Candidate startup checks actual observer inference capability before
  starting the candidate; no protected execution was used.

### Criterion C — validator and source-reuse contract

- PASSED — The clean qualification used the exact pinned Gateway
  `ResponsesStreamEventValidator` and request-scoped factory through the actual
  candidate, with the ordered Gateway/Codex identities.
- PASSED — Disposable Git fixtures verify a round-neutral report-only child is
  accepted only with one parent, one newly added corresponding report,
  implementation-SHA/SELF markers, clean relevant source, and no production or
  harness descendant changes; malformed and multi-parent forms fail closed.

### Criterion D — complete fake qualification

- PASSED — Exact clean fake run: 37/37 selected rows `PASSED`, all projections
  `PASSED`, `missing=[]`, `first_failure=null`, and `retry_count=0`.
- PASSED — Candidate provenance: implementation
  `90460f23ec763b9503ba6ad2c32397def8a1430f`, Gateway
  `50dcc3b85d614eb1d0c6196595bf22ef5779f846`, app tree
  `c0204deaff3cfd055a25f29a7f5d8d3c5e161d57`, Codex `0.149.0`, binary SHA-256
  `bbc3341e44c9ead340ed9570c17be936e37870f570751a941699ffd04d672827`,
  observer `direct-httpx-v2`.
- PASSED — Exact observer facts matched the independent fake provider:
  23 attempted/dispatched/responded/completed/terminal-valid operations,
  including 6 compiler and 12 inference operations; all 12 inference streams
  had first-byte and normal-close facts.
- PASSED — Temporary processes/listeners/database/cache/Codex home/failure
  state cleanup facts were all true; fake protected state was not applicable.

## Verification

- `uv run --frozen pytest -q tests/test_transport_observer.py tests/test_gateway_accounting_rehearsal.py`: PASSED — 75 passed.
- `uv run --frozen pytest -q`: PASSED — 715 passed, 8 skipped; skips remain explicit host/live gates.
- Exact pinned Gateway/Local/Codex/strict fake rehearsal, provider target `fake`: PASSED — complete 37/37 machine gate, zero missing/first-failure/retry, exact observer/provider counts, cleanup true.
- `uv run --frozen ruff check .`: PASSED.
- `uv run --frozen ruff format --check .`: PASSED — 251 files formatted.
- `uv run --frozen mypy src tests`: PASSED — 57 files, no issues.
- `uv run --frozen python -m compileall -q scripts tests/helpers src`: PASSED.
- `bash -n oap/bin/*.sh`: PASSED.
- `uv build --wheel --sdist`: PASSED — wheel and sdist built.
- Wheel boundary scan: PASSED — wheel contains no `tests/` or `scripts/` members.
- Allowlisted diff/path, pin, credential, protected-mutation, privacy/logging, and `git diff --check` scans: PASSED.
- First dirty-worktree rehearsal preflight: BLOCKED before service/model stages as required; clean implementation-head requalification then PASSED.

## Live model/service evidence

- Read-only fixture check: vision process PID `23961`, start `Sun 2026-09-06 18:57:26 CEST`, zero restarts; listener `18020` present.
- The protected `qwen-serving` user unit remained `inactive/dead` with
  `MainPID=0`; candidate ports `18021`, `18030`, and `18031` were unused.
- Bounded unauthenticated health status for listener `18020`: HTTP `200`.
- No protected credential, environment, raw log/config, model listing,
  compiler, inference, image, diagnostic, restart, service, network, firewall,
  VPN, or active-profile operation occurred.

## GitHub CI / required checks

- Implementation-head `test`: SUCCESS — run `34392247645`, job `102603178083`,
  observed on `90460f23ec763b9503ba6ad2c32397def8a1430f`.
- All required checks green at drafting: YES.
- Report-head checks may be pending after publication; strategy verifies.

## Local setup/dependencies

- Used the existing frozen Local environment.
- Used a disposable detached Gateway checkout at the exact ordered SHA and a
  temporary Python 3.12 environment for its runtime/dev dependencies; both
  were task-owned temporary state.
- Used the existing bounded runner's temporary PostgreSQL 16 tmpfs/`--rm`
  state and loopback fake provider; cleanup facts passed.
- No Local dependency, lockfile, Gateway source, model, binary, or installed
  service was changed.

## Documentation

Updated `TESTING.md` and `docs/SLAIF-GATEWAY-INTEGRATION.md` to match the
implemented lifecycle ownership, real loopback streaming proof, validator
admission ordering, and round-neutral source-reuse checks.

## Safety/scope confirmations

- Unrelated files and all prior OAP orders/reports, including 005-q/r/s/t,
  were preserved.
- Secrets, raw prompts/source/images/tool output, credentials, and model
  weights were not committed, logged, or included in evidence.
- Protected 18020/Qwen/Codex fixture changed: NO.
- Required tests skipped/not run: only the 8 pre-existing explicit full-suite
  host/live skips; protected inference and cutover were not authorized or run.
- Extra objective PR: NO; coding merge/auto-merge/acceptance: NO.
- Active/order edited by coding: NO; exact strategic activation bytes were
  committed unchanged.
- Final report commit report-only: YES.

## Known limitations/blockers

- Protected provider-call/terminal-lifecycle observation, real protected
  inference/vision acceptance, installed cutover, and release readiness remain
  unclaimed because 005-u prohibits protected traffic and service mutation.
- Report-head CI may be pending after publication; strategy independently
  verifies it.

## Recommended strategic follow-up

Strategy should independently verify the final report-only commit parent/path/
bytes, current PR head/checks, and the separation between this fake qualification
and any future authorized protected acceptance.

## Lifecycle state at publication

| State | Result |
| --- | --- |
| `IMPLEMENTED` | yes |
| `TESTED` | yes — focused/full repository checks and complete fake gate |
| `REAL-E2E ACCEPTED` | no |
| `CUTOVER ACCEPTED` | no |
| `MERGED` | no |
| `RELEASE-READY` | no |

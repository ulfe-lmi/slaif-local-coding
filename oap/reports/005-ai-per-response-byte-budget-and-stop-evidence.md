# OAP Coding-Agent Report — 005-ai

## Work order

- Identifier: `005-ai`
- Order: `oap/orders/005-ai-per-response-byte-budget-and-stop-evidence.md`
- Numeric objective: `005`, per-response byte budget and stop evidence
- PR mode: `AMENDED_EXISTING_PR`
- Report: `oap/reports/005-ai-per-response-byte-budget-and-stop-evidence.md`

## Status

COMPLETE

## Executive summary

The Local acceptance controller now accounts stream bytes per admitted HTTP
response lifetime while retaining separate all-lifetime totals. Rejected,
concurrent, stale, cancelled, abnormal, and closed lifecycles cannot reset an
active response or clear a latched failure. The observer and accumulator retain
exact bounded byte facts and frozen first-failure context.

The final fake qualification passed 37/37 obligations and projections. The
healthy synthetic protected branch passed 29/29 selected rows; all five
synthetic cases serialized all 29 rows, including a Codex-complete then
first-vision-response stop with preserved earlier phase facts. No protected
credential, Qwen inference, retry, or diagnostic traffic was performed.

## Authoritative GitHub state

- Repository: `ulfe-lmi/slaif-local-coding`
- PR: 7, https://github.com/ulfe-lmi/slaif-local-coding/pull/7
- State: OPEN, non-draft; merge state CLEAN at the implementation head
- Base/head: `main` / `oap/005-gateway-ingress-integration`
- Starting remote SHA: `b43ec3d8932a8fe92dbb62c54411b7df817b8d01`
- Implementation commits pushed before report:
  `f3356c17f8f514fe4d5a07a5d166747908fa9f40`,
  `93a1714730bf32b1a70d469b2d49c0f3cefbbde9`,
  `5d3b0c3dca0a79905a3ac60e611b2b5dbd856d32`,
  `9aca9975b36567208ae7ef3d5f4e4141598fd6d8`
- New PR this round: NO; amended existing PR: YES; merge performed: NO
- Implementation head SHA: `9aca9975b36567208ae7ef3d5f4e4141598fd6d8`
- Report publication commit: SELF

The tested code is `5d3b0c3dca0a79905a3ac60e611b2b5dbd856d32`. The
implementation head is its single-parent descendant containing only the
documentation and generated evidence paths listed below; this is the
docs/evidence-only ancestry attestation required for reuse.

## Changes and files

- `tests/helpers/acceptance_harness.py`: explicit response byte lifetimes,
  separate current/all-lifetime byte totals, rejected-chunk accounting, phase
  checkpoints, and safe first-failure context.
- `tests/helpers/transport_observer.py`: response-lifetime start/finalization
  across normal, abnormal, cancellation, early-close, and delegate-close
  paths; per-response byte fields; contextual stop facts.
- `tests/test_acceptance_harness.py` and
  `tests/test_transport_observer.py`: sequential aggregate-over-limit,
  mixed-lifetime, exact-bound/overflow, admission-race, byte evidence, and
  later-failure regressions.
- `scripts/gateway_accounting_rehearsal.py`: the source-bound synthetic
  later-phase failure checkpoint case.
- `TESTING.md` and `docs/SLAIF-GATEWAY-INTEGRATION.md`: current byte,
  lifecycle, and evidence contracts.
- `oap/evidence/005-ai/`: generated fake, synthetic-protected, explicit
  real-protected-NOT-RUN, and index artifacts.
- `oap/active` and the activated order were committed byte-for-byte unchanged.

No `src/`, dependency, lock, version, binary, Gateway, service, or model file
was changed.

## Acceptance evidence

### Criterion 1 — per-response stream byte lifecycle

- PASSED: two sequential unread asynchronous JSON responses of 70,014 bytes
  each were each accepted under the unchanged 131,072-byte limit; combined
  accepted traffic was 140,028 bytes and did not fail.
- PASSED: exact-bound 131,072-byte responses remain accepted; a single response
  receiving one additional byte records 131,073 received, 131,072 accepted,
  one rejected byte/chunk, and latches
  `budget_stream_limit_exhausted`.
- PASSED: mixed compiler/inference response types, split/coalesced validated
  SSE, frame accounting, concurrency rejection, close/cancel/timeout, and
  zero-later-dispatch behavior are covered by the focused tests.
- PASSED: numeric limits remain unchanged: 16,384-byte event/frame,
  131,072-byte response/stream, 64 observations, 900-second wall bound,
  zero retries, and single active dispatch.

### Criterion 2 — safe failure and phase evidence

- PASSED: all-lifetime fake totals are 6 compiler, 12 inference, and 8 other
  dispatches; 26 total admitted dispatches; 21,664 received and accepted
  response bytes; zero rejected bytes/chunks.
- PASSED: the synthetic `vision_failure_after_codex` case records first
  failure `observer_readiness_lost` at kind `inference`, operation
  `vision_full`, phase `vision`, ordinal 3, lifetime `vision`; one
  completed Codex phase precedes it; all 29 rows and projections serialize;
  cleanup remains true.
- PASSED: projection and cleanup failure injections retain the original
  primary failure and preserve bounded secondary classes.
- PASSED: the acceptance manifest's earliest unsatisfied row remains separate
  from the accumulator's frozen runtime failure context.

### Criterion 3 — full fake qualification and safety

- PASSED: final actual Codex 0.149.0 fake qualification returned
  `COMPLETE`, 37/37 obligations, 37/37 projections, 26/26 direct
  dispatches, exact accounting, cleanup, and secret-free logs.
- PASSED: healthy synthetic protected qualification returned 29/29 selected
  rows and projections with the fake semantic oracle unavailable.
- PASSED: observer failure, projection/cleanup failure, pre-dispatch mapping
  failure, and later vision-phase failure all serialized 29/29 rows and
  stopped as designed.
- PASSED: source-bound artifacts are under
  `oap/evidence/005-ai/`; the index binds tested source/module hashes,
  Gateway/Codex pins, run identity, machine rows, byte totals, checkpoints,
  cleanup, and limitations.

## Verification

- `uv run --frozen pytest -q`: PASSED — 805 passed, 8 skipped in 48.32s.
- `uv run --frozen pytest -q tests/test_acceptance_harness.py tests/test_transport_observer.py`: PASSED — 158 passed.
- `uv run --frozen ruff check .`: PASSED.
- `uv run --frozen ruff format --check .`: PASSED — 279 files.
- `uv run --frozen mypy src tests`: PASSED — 57 source files.
- `uv run --frozen python -m compileall -q src tests scripts oap/bin`: PASSED.
- `bash -n oap/bin/*.sh`: PASSED.
- `uv lock --check`: PASSED.
- `uv pip check --python .venv/bin/python`: PASSED.
- `uv build --wheel --out-dir <private temporary directory>`: PASSED.
- Wheel member boundary check: PASSED — no `tests/` or `scripts/` members.
- `git diff --check` and staged path checks: PASSED.
- `jq empty oap/evidence/005-ai/*.json` plus tested-SHA/source-hash binding: PASSED.
- Evidence credential/payload marker scan: PASSED — no forbidden markers.
- Exact pinned fake rehearsal as UID/EUID 1029: PASSED — 37/37 machine
  rows/projections, five synthetic protected cases, cleanup, and
  secret-free logs.

## Live model/service evidence

- Read-only host: `hinton1`; vision
  `qwen-serving-vision.service` remained active/running at MainPID
  `23961`, start `Sun 2026-09-06 18:57:26 CEST`, zero restarts.
- Port 18020 remained listening; bounded unauthenticated GET
  `http://127.0.0.1:18020/health` returned status 200.
- Text service remained inactive/dead; Qwen worktree changed-path count
  remained 7 before and after.
- No `/v1/models` probe, credential read, environment/config/log/model read,
  authenticated request, compiler/inference/vision request, retry, or
  diagnostic request was made to the protected service.
- Candidate/Gateway/PostgreSQL qualification resources were disposable,
  loopback-bound, and cleaned up. Protected Qwen/vLLM/model/network/firewall/
  Codex-profile mutation: NO.

## GitHub CI / required checks

- Implementation-head `test`: SUCCESS — run `34459974312`, job
  `102815220765`, head
  `9aca9975b36567208ae7ef3d5f4e4141598fd6d8`.
- All required checks at report drafting: YES.
- Report-head checks may be pending after publication; strategy verifies them
  independently.

## Local setup/dependencies

- Used the repository `.venv` and a disposable detached Gateway checkout at
  `50dcc3b85d614eb1d0c6196595bf22ef5779f846` with a temporary Python
  environment.
- Used the existing bounded PostgreSQL 16 loopback/tmpfs/--rm rehearsal path
  and exact Codex 0.149.0 binary verified by the ordered SHA-256.
- No dependency, lockfile, host package, installed service, protected
  environment, credential file, model, or network configuration changed.

## Documentation

Updated `TESTING.md` and `docs/SLAIF-GATEWAY-INTEGRATION.md` with the
per-response byte-lifetime, all-lifetime evidence, frozen failure-context,
phase-checkpoint, synthetic later-phase stop, and source-bound artifact
contract.

## Safety/scope confirmations

- Unrelated files and all prior orders/reports/evidence, including 005-ah,
  005-q, 005-af, and 005-ag scope disclosures, were preserved.
- No secrets, raw IDs/digests, prompts, source, images, tool output, bodies,
  signatures, nonces, private payloads, credentials, or customer data were
 committed or retained.
- Protected 18020/Qwen/Codex fixture changed: NO.
- Required fake/synthetic checks ran; real protected matrix is explicitly
  `NOT RUN` under `oap/evidence/005-ai/protected-matrix.json`.
- Extra objective PR: NO. Coding merge/acceptance: NO.
- Active/order content edited after activation: NO.
- Final report commit report-only: YES.

## Known limitations/blockers

- This order establishes the fake and synthetic remediation contract only. Real
  protected inference and semantic acceptance remain `NOT RUN` because the
  order explicitly prohibits protected credentials, Qwen inference, retry, and
  diagnostic traffic.
- The injected later-phase stop intentionally produces a secondary fixed
  validation/loopback-close class; the primary vision failure and completed
  Codex checkpoint remain authoritative.
- Eight pytest cases were skipped by the repository suite and are not claimed
  as passes.
- Report-head CI may be pending after publication; strategy independently
  verifies its terminal state.

## Recommended strategic follow-up

Review the source-bound 005-ai fake/synthetic evidence and the exact
per-response byte/first-failure facts. Any real protected attempt, cutover,
merge, or release decision requires a separate strategic order and authority.

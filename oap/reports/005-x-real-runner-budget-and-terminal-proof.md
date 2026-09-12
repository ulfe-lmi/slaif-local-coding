# OAP Coding-Agent Report — 005-x

## Work order

- Identifier: `005-x`
- Order: `oap/orders/005-x-real-runner-budget-and-terminal-proof.md`
- Numeric objective: Objective-005
- PR mode: `AMENDED_EXISTING_PR`

## Status

COMPLETE

## Executive summary

Closed the ordered repository-only Local harness gaps for semantic terminal
evidence, actual per-dispatch budget admission, and synthetic protected-mode
runner conformance. The direct observer now uses the same run-owned budget for
each compiler/inference/other dispatch and each streamed chunk. The accumulator
retains exact counts across named observer lifetimes and derives terminal
classes only from semantic per-record observations. The actual shared runner
has explicit synthetic-only protected-boundary hooks; missing dependencies fail
closed and all 29 protected-selected dispositions serialize without defaulting
to acceptance.

The exact pinned fake Gateway → Local → strict loopback provider rehearsal
passed. Real protected credentials, Qwen inference, vision, diagnostic traffic,
cutover, merge, and release acceptance were not run or claimed, as required by
the order.

## Authoritative GitHub state

- Repository: `ulfe-lmi/slaif-local-coding`
- PR: #7 — https://github.com/ulfe-lmi/slaif-local-coding/pull/7 — OPEN,
  non-draft, CLEAN
- Base/head: `main` / `oap/005-gateway-ingress-integration`
- Starting remote SHA: `5512a1e7443727aea1b25b75c0a7bb6078b14d6a`
- Implementation head SHA: `ae5e131ba30664ce503cc903d30a104773e6b331`
- Report publication commit: SELF
- Implementation commits pushed before report:
  `042801752a7aafaef182936675dfb8a4ac53dd08`,
  `dc5b3e802613fd81eee9874a722accbec6aca2fb`,
  `63920a4fa1339f013b51e64b22c233917e21f7aa`,
  `ae5e131ba30664ce503cc903d30a104773e6b331`
- New PR this round: NO
- Amended existing PR: YES, PR #7
- Merge performed: NO

## Changes and files

- `tests/helpers/acceptance_harness.py`: added exact dispatch budgets and
  bounded dispatch facts; made accumulator counts lifetime-aware; retained
  semantic terminal-valid counters/per-ordinal classes, unknown observations,
  primary failure, secondary failures, and cleanup facts.
- `tests/helpers/transport_observer.py`: connected run-owned dispatch admission,
  deadline/byte checks, phase/ordinal attribution, stream-lifetime concurrency,
  and release-on-close/cancel/error behavior.
- `scripts/gateway_accounting_rehearsal.py`: wired observers to the shared
  controller, corrected active post-vision lifetime capture, and added the
  actual shared-runner synthetic protected-boundary entry point and selector.
- `tests/test_acceptance_harness.py`, `tests/test_transport_observer.py`,
  `tests/test_gateway_accounting_rehearsal.py`: regressions for semantic
  terminal states, lifetime aggregation, dispatch/deadline/event/concurrency
  negatives, missing dependencies, protected row serialization, and synthetic
  boundary selection.
- `TESTING.md`, `docs/SLAIF-GATEWAY-INTEGRATION.md`: documented actual coverage,
  budgets, terminal evidence, synthetic-only conformance, and limitations.
- `oap/active` and `oap/orders/005-x-real-runner-budget-and-terminal-proof.md`:
  activated strategic transcript committed byte-for-byte; not edited by
  coding.

## Acceptance evidence

### Criterion A — truthful semantic terminal evidence

- PASSED — The reproduced counterexample retained attempted/responded/
  completed lifecycle facts while semantic `terminal_valid_count` stayed zero;
  `stream_validation_invalid` remained the primary fixed failure and the
  terminal class was `terminal_invalid`, not `terminal_valid`.
- PASSED — Valid, invalid-but-consumed, truncated, absent, zero-dispatch,
  cancelled, and multiple-lifetime regressions passed. Absent semantic records
  remain `unknown`; attempted==completed never upgrades validity.
- PASSED — Lifetime updates are monotonic within a named observer and distinct
  lifetimes aggregate without double counting. Primary failure survives later
  projection/serialization/cleanup classes.

### Criterion B — actual dispatch budget and stream enforcement

- PASSED — Every direct observer request is admitted immediately before
  delegate invocation through the run-owned controller. The final fake run
  recorded 23 attempted and 23 admitted dispatches: 6 compiler, 12 inference,
  and 5 other; no budget failure latched and cleanup returned active counts to
  zero.
- PASSED — Deadline checks run before dispatch and between streamed chunks;
  event and aggregate stream overflow close the delegate and prevent later
  calls. Lower-limit tests passed for extra calls, deadline expiry, event
  overflow, first-failure stop, and overlapping requests with exact delegate
  counts.
- PASSED — The unchanged maxima remain 900 seconds, one attempt/zero retries
  for each of the nine ordered operations, 64 observations, 16 KiB events,
  128 KiB aggregate stream bytes, and single active stream concurrency.

### Criterion C — actual shared-runner synthetic protected conformance

- PASSED — `run_actual_protected_mode_conformance` invokes the shared runner;
  missing synthetic dependencies fail closed, and the injected preflight stop
  serialized all 29 protected-selected result dispositions with
  `protected_acceptance=false`.
- PASSED — The protected selector uses explicit synthetic host preflight,
  MainPID, and credential-source boundaries in the tested order. The selector
  regression performed no `/proc` access and no protected request. Direct
  observer dispatch-hook and accumulator failure-retention tests cover
  observer-readiness and finalization error classes without replacing the
  orchestration with a success oracle.
- PASSED — Synthetic protected evidence is labelled orchestration-only and is
  not treated as protected provider acceptance.

### Criterion D — qualification, documentation, and safety

- PASSED — Exact pinned fake rehearsal at implementation
  `ae5e131ba30664ce503cc903d30a104773e6b331`: 37/37 selected obligations and
  37/37 projections passed; 23/23 observer operations were dispatched,
  responded, completed, and terminal-valid; 12/12 inference streams were
  semantically terminal-valid; independent fake-provider counters matched;
  29/29 synthetic protected dispositions serialized; task resources cleaned.
- PASSED — Documentation reflects fake-only evidence and keeps
  `REAL-E2E ACCEPTED`, `CUTOVER ACCEPTED`, `MERGED`, and `RELEASE-READY` false.
- PASSED — The exact Codex 0.149.0 fixture checksum remained
  `bbc3341e44c9ead340ed9570c17be936e37870f570751a941699ffd04d672827`; the
  Gateway checkout remained at
  `50dcc3b85d614eb1d0c6196595bf22ef5779f846` and clean.

## Verification

- `uv run --frozen pytest -q tests/test_acceptance_harness.py tests/test_transport_observer.py tests/test_gateway_accounting_rehearsal.py`: PASSED — 182 passed.
- `uv run --frozen pytest -q`: PASSED — 736 passed, 8 skipped; skips remain explicit live/host gates.
- Exact pinned fake rehearsal with `--provider-target fake`: PASSED — 37/37 machine rows and projections; 23/23 observer dispatches; 6 compiler, 12 inference, 5 other; 12/12 inference terminal-valid; 29/29 synthetic protected rows; cleanup passed.
- `uv run --frozen ruff check .`: PASSED.
- `uv run --frozen ruff format --check .`: PASSED — 257 files formatted.
- `uv run --frozen mypy src tests`: PASSED — 57 files, no issues.
- `uv run --frozen python -m compileall -q scripts tests/helpers src`: PASSED.
- `bash -n oap/bin/*.sh`: PASSED.
- `uv build --wheel --sdist`: PASSED — wheel and sdist built.
- Wheel boundary scan: PASSED — wheel contained no `tests/` or `scripts/` members.
- `git diff --check 5512a1e7443727aea1b25b75c0a7bb6078b14d6a HEAD`: PASSED.
- Diff privacy scan for bearer-like values, key material, image data, and
  private-key markers: PASSED.
- Scoped-path scan against protected production/config/dependency paths:
  PASSED.

## Live model/service evidence

- Read-only vision-unit facts: PASSED — active/running, MainPID `23961`, start
  `Sun 2026-09-06 18:57:26 CEST`, `NRestarts=0`.
- Read-only text-unit fact: PASSED — inactive, MainPID `0`.
- Listener facts: PASSED — protected listener `18020` present; checked candidate
  ports `18021`, `18030`, and `18031` absent after cleanup.
- Unauthenticated protected health status: PASSED — HTTP 200; response body
  was not read or retained.
- Protected credential, `/proc` environment, model, compiler, inference,
  vision, and diagnostic requests: NOT RUN by this order.
- Protected Qwen/vLLM, port 18020, systemd, model, network, firewall/VPN, and
  active Codex profile state changed: NO.

## GitHub CI / required checks

- Implementation-head check observed at `ae5e131ba30664ce503cc903d30a104773e6b331`:
  `test`: SUCCESS — run `34407297423`, job `102653228821`.
- All required checks green at drafting: YES.
- Report-head checks may be pending after this report-only publication; strategy
  verifies them independently.

## Local setup/dependencies

- Used the existing frozen repository environment; no dependency or lockfile
  changes.
- Used a clean disposable Gateway checkout at the exact ordered executable pin,
  a task-owned PostgreSQL 16 loopback/tmpfs `--rm` container, strict loopback
  fake Qwen, Local candidate, temporary cache/Codex home, and bounded cleanup.
- Used the exact Codex 0.149.0 fixture and checksum listed above. No host
  daemon/package, privileged networking, Qwen installation, or protected
  service mutation occurred.

## Documentation

Updated `TESTING.md` and `docs/SLAIF-GATEWAY-INTEGRATION.md` with measured
terminal evidence, lifetime aggregation, dispatch admission, stream/deadline/
concurrency limits, synthetic protected hooks, exact fake qualification, and
non-acceptance limitations.

## Safety/scope confirmations

- Unrelated files changed: NO.
- Secrets, raw prompts/source/images/tool/SSE output, credentials, private URLs,
  customer data, and model weights exposed: NO.
- Production/protected resources accessed or changed: only ordered read-only
  unit/listener/unauthenticated-health facts were checked; no protected
  credential or inference traffic.
- Port 18020 or Qwen/Codex fixture changed: NO.
- Required tests skipped/not run: real protected matrix and live authenticated
  inference were NOT RUN by explicit order; 8 pytest skips remain explicit.
- Scope deviation: NONE.
- Extra objective PR: NO.
- Coding-agent merge/auto-merge: NO.
- Activated order/active edited: NO; committed unchanged activation bytes.
- Report commit changes only this report: YES.

## Known limitations/blockers

- Real protected provider-boundary, semantic terminal, tool, vision,
  governance, accounting, isolation, and cutover acceptance remain NOT RUN.
- Synthetic protected conformance is orchestration evidence only and retains
  `protected_acceptance=false`.
- Production readiness, multi-user equivalence, installed cutover, merge, and
  release readiness remain unclaimed.

## Recommended strategic follow-up

Independently verify this report-only commit's exact bytes, first parent,
report-only path, remote PR head, and report-head check state; then review the
fake-only completion and decide whether any future protected-testing order is
appropriate.

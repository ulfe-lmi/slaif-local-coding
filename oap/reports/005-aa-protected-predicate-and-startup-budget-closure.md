# OAP Coding-Agent Report — 005-aa

## Work order

- Identifier: `005-aa`
- Order: `oap/orders/005-aa-protected-predicate-and-startup-budget-closure.md`
- Numeric objective: Objective-005
- PR mode: `AMENDED_EXISTING_PR`

## Status

COMPLETE

## Executive summary

Closed the protected synthetic-conformance and startup-dispatch-control gaps
within the existing repository harness. Protected conformance now requires the
nested protected acceptance gate and every selected row/projection to pass;
serialized rows alone cannot qualify it. Direct candidate startup uses the same
observer and a single explicit, bounded, health-only readiness permit. Pending
operation reservations no longer bypass the currently activated context, and
observer lifetimes reject dynamic context inheritance. The final fake gate and
healthy synthetic protected gate passed. Real protected inference, cutover,
merge, and release acceptance remain unperformed and unclaimed.

## Authoritative GitHub state

- Repository: `ulfe-lmi/slaif-local-coding`
- PR: 7 — https://github.com/ulfe-lmi/slaif-local-coding/pull/7
- State: OPEN; draft: NO; merge state: CLEAN
- Base/head: `main` / `oap/005-gateway-ingress-integration`
- Starting remote SHA: `3e2254c0f8ccf1da1f1078a91cf19ba6cd04b5f3`
- Implementation head SHA: `e5a986a85b35e131e7b1da7340688d3510612abf`
- Report publication commit: SELF
- Implementation commits pushed before report: `31ae68820fd218147086f7978861c757373fc353`, `a4c5d2b555a4442880da1a69839909c50639df0a`, `0de8497a36d8d379779c326979a27ac5886b5712`, `04b3febfb6700998ec7209d1e340fd623610dceb`, `ee72a19d45a5eaba0329daaddd571742ca81a586`, `2a7420998e3734d929142f3da0efdcf2664292f9`, `e5a986a85b35e131e7b1da7340688d3510612abf`
- New PR this round: NO; amended existing: YES; merge performed: NO

## Changes and files

- `tests/helpers/acceptance_harness.py`: current-context matching, explicit
  readiness permits, bounded readiness counters, and strict legacy protected
  gate status.
- `tests/helpers/transport_observer.py`: lifetime-bound observer contexts,
  health-only readiness enforcement, and counted other-dispatch facts.
- `scripts/gateway_accounting_rehearsal.py`: budgeted startup readiness,
  synthetic protected provider-boundary mapping, nested gate qualification,
  id-less continuation coverage, and failure-count retention.
- `tests/test_acceptance_harness.py`, `tests/test_transport_observer.py`:
  stale/missing context, lifetime, readiness, and protected-gate regressions.
- `TESTING.md`, `docs/SLAIF-GATEWAY-INTEGRATION.md`: corrected 6-SSE/6-JSON
  accounting and documented the 005-aa contract and evidence.
- `oap/evidence/005-aa/*.json`: bounded sanitized machine evidence only;
  no raw captures.
- `oap/active` and the exact activated 005-aa order were committed unchanged.

## Acceptance evidence

### Criterion A — protected predicates and projections

- PASSED — Final healthy synthetic protected conformance had `gate_passed=true`,
  `healthy_gate_passed=true`, 29/29 selected rows, 29/29 projections, null
  primary failure, and all rows serialized. `protected_acceptance=false`.
- PASSED — Synthetic provider semantics were mapped from the explicit disposable
  loopback boundary; real protected transport-only observations remain unable to
  prove semantic provider classes or terminality.
- PASSED — Topology evidence is independent of provider semantic evidence;
  no fake-server facts are accepted for a real protected run.

### Criterion B — dispatch and startup controls

- PASSED — A stale explicit `codex_turn_2` context was rejected while turn 1
  was active, before delegation.
- PASSED — Missing observer context and an observer inheriting a different
  lifetime were rejected before delegation; delegate-call regressions passed.
- PASSED — Three startup readiness permits were admitted and consumed exactly
  once; none remained pending. Readiness accepted only upstream `/health`, and
  all three counted in the shared dispatch total.
- PASSED — Final fake run measured 26/26 direct dispatches: 6 compiler, 12
  inference, and 8 other, under the 64-dispatch ceiling.

### Criterion C — fresh execution and failure qualification

- PASSED — Final exact-pinned fake machine gate: 37/37 obligations and
  37/37 projections, no missing rows, null first failure, zero retries, and
  exact fake-provider agreement.
- PASSED — Healthy synthetic protected case: 6 compiler and 12 inference
  lifecycle counts, 29/29 rows, no primary failure, and complete cleanup.
- PASSED — Observer-failure case stopped after one compiler dispatch and kept
  `observer_readiness_lost` primary failure; all 29 rows serialized.
- PASSED — Combined observer/projection/cleanup case retained the observer
  primary failure plus bounded secondary classes; all 29 rows serialized.
- PASSED — Pre-dispatch mapping case stopped before compiler/inference
  delegation with `observer_dispatch_hook_error`; all 29 rows serialized.
- NOT RUN — Real protected matrix and authenticated Qwen inference, as
  prohibited by this order.

## Verification

- `./.venv/bin/pytest -q tests/test_acceptance_harness.py tests/test_transport_observer.py tests/test_gateway_accounting_rehearsal.py`: PASSED — 198 passed.
- `uv run --frozen pytest -q`: PASSED — 752 passed, 8 skipped; skips are explicit live/host gates.
- `uv run --frozen ruff check .`: PASSED.
- `uv run --frozen ruff format --check .`: PASSED — 263 files formatted.
- `uv run --frozen mypy src tests`: PASSED — 57 files, no issues.
- `uv run --frozen python -m compileall -q src tests oap/bin`: PASSED.
- `bash -n oap/bin/*.sh`: PASSED.
- `uv build --wheel --sdist`: PASSED — wheel and sdist built.
- `git diff --check`: PASSED.
- `for path in oap/evidence/005-aa/*.json; do uv run --frozen python -m json.tool "$path" >/dev/null || exit 1; done`: PASSED — each evidence JSON validated individually.
- Final fake rehearsal with the exact Gateway/Codex arguments recorded in
  `oap/evidence/005-aa/index.json`: PASSED — 37/37; result SHA-256
  `1e21877080ef3bbccdd4f31ea9801d7f2fb1f291857ae968d8187e69a410dfe7`.
- Separate synthetic protected cases with the same exact pins: PASSED for
  healthy qualification and PASSED as failure qualification for each bounded
  injected-stop case; safe result hashes and row/counter summaries are in the
  evidence files.
- `gh pr checks 7`: PASSED — `test`, run `34420999338`, job `102696177837`,
  SUCCESS at implementation head `e5a986a85b35e131e7b1da7340688d3510612abf`.

## Live model/service evidence

- Read-only `systemctl --user show qwen-serving-vision.service` observed
  `MainPID=23961`, `ActiveState=active`, `SubState=running`, `NRestarts=0`,
  and start `Sun 2026-09-06 18:57:26 CEST`.
- Read-only listener inspection observed port 18020 bound by PID 23961.
- One bounded unauthenticated health-status probe returned HTTP 200; its body
  was discarded.
- Protected credentials, `/proc` environment, model/config/log contents,
  authenticated/model/compiler/inference/vision requests, restart,
  instrumentation, and service/profile/network mutation: NOT RUN.

## GitHub CI / required checks

- Implementation/report-head required `test`: SUCCESS — run `34420999338`,
  job `102696177837`.
- All required checks green at report drafting: YES.
- Merge/auto-merge: NO. Strategy independently owns review, acceptance, and
  merge decisions.

## Local setup/dependencies

- Used the existing repository `.venv`/`uv` frozen environment.
- Used the clean detached Gateway fixture at
  `50dcc3b85d614eb1d0c6196595bf22ef5779f846` and the exact Codex 0.149.0
  binary with the ordered SHA-256.
- Used only disposable loopback fake provider, candidate port 18031, task-owned
  temporary PostgreSQL/tmpfs state, and bounded synthetic hooks.
- No Gateway implementation, dependency lock/version, model, or installed
  service was changed.

## Documentation

Updated `TESTING.md` and `docs/SLAIF-GATEWAY-INTEGRATION.md` with the corrected
6-SSE/6-JSON distinction, 26-dispatch readiness-inclusive totals, nested
protected-gate rule, lifetime-bound startup control, and evidence paths.

## Safety/scope confirmations

- Unrelated pre-existing work was preserved; only the ordered helpers, tests,
  docs, sanitized evidence, transcript, and report are in scope.
- Secrets, raw prompts/source/images/tool output/SSE bodies/customer data were
  not retained in logs, evidence, or report.
- Protected 18020/Qwen/Codex fixture changed: NO.
- Protected model/checkpoint/venv/unit/launch/GPU/key/firewall/VPN/network and
  active profile changed: NO.
- Extra objective PR: NO; coding merge/auto-merge: NO.
- Active/order edited after activation: NO.
- This report commit is report-only: YES; its first parent must equal the
  implementation head above.
- Evidence tested source `ee72a19d45a5eaba0329daaddd571742ca81a586` was reused
  only through the documented evidence-only descendant with relevant source
  unchanged; the final documentation child changed no implementation code.

## Known limitations/blockers

- Real protected inference acceptance, protected matrix, cutover, merge, and
  release readiness remain NOT RUN/unaccepted.
- Synthetic loopback conformance does not establish production or generic
  hardware equivalence.
- The historical systemd/unit-versus-live-process discrepancy was observed in
  prior evidence and not remediated.

## Recommended strategic follow-up

Review the immutable evidence and current PR checks. Strategy decides any
acceptance, merge, release, or subsequent order; coding does not infer those
decisions.

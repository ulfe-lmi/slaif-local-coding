# OAP Coding-Agent Report — 005-n

## Work order

- Identifier: `005-n`
- Order path: `oap/orders/005-n-final-clean-gateway-protected-matrix-and-cutover.md`
- Numeric objective: `005`
- PR mode: `AMENDED_EXISTING_PR`

## Status

BLOCKED

## Executive summary

The exact clean Gateway Objective-160 implementation was verified and pinned in
the three Local repository-only acceptance constants. Local static, unit,
package, exact-Gateway product/verifier, and fake Gateway -> Local -> fake-Qwen
gates passed. The protected matrix could not start authenticated model
visibility: the documented protected credential reference was unavailable to
this process. A bounded unauthenticated health probe returned HTTP 200 while
the protected model-list route correctly returned HTTP 401. No protected
inference, vision request, candidate cutover, or Qwen mutation was performed.

## Authoritative GitHub state

- Repository: `ulfe-lmi/slaif-local-coding`
- PR: [#7](https://github.com/ulfe-lmi/slaif-local-coding/pull/7)
- PR state: OPEN, non-draft, MERGEABLE/CLEAN
- Base/head: `main` / `oap/005-gateway-ingress-integration`
- Starting remote SHA: `4d3ab2fd97d249710f952dd3d2c28936138cc8fa`
- Implementation head SHA: `3e072a4ec57947fe7ee003bfcffd404d5363768d`
- Report publication commit: SELF
- Implementation commits pushed before report: `3e072a4ec57947fe7ee003bfcffd404d5363768d`
- New PR this round: NO
- Amended existing PR: YES, PR #7
- Merge performed: NO

The exact detached Gateway checkout was `9d247e7f3d8fd6a588976840c4657181b7486b81`.
Its merged-main reachability, report topology, and `app/` tree were verified:
merged main `910ddaa23763883c07f5d2065662eb1157deb9f1`, final Objective-160
report head `e15008fd0f920aa81ccd5c0d425caf26f7f61b75`, app tree
`bd536a282362cc549cc0c5518db8e743af667b63`, and accepted Objective-155
equivalence authority `acea2af4ca0f4586fc159c91607e1848f53f1107` with the same
app tree. The ten required Gateway checks at the exact implementation head were
SUCCESS. No Gateway source was changed.

## Changes and files

- Updated the three Local acceptance constants from superseded Gateway
  `2527030f5bbb90a7f0f354eb5347caee333ce4a7` to exact implementation
  `9d247e7f3d8fd6a588976840c4657181b7486b81`:
  `scripts/codex_tool_envelope_differential.py`,
  `tests/helpers/gateway_accounting_rehearsal.py`, and
  `tests/helpers/gateway_provider_driver.py`.
- Committed the exact activated `oap/active` and `005-n` order bytes unchanged.
- No Local production policy, Gateway code, protected model, service, network,
  profile, or persistent deployment was changed.

## Acceptance evidence

### Criterion 1 — exact-head and no-live repository preflight

- PASSED — Local HEAD and PR #7 matched the required 005-m report head before
  implementation; the existing open PR was amended and no second PR was made.
- PASSED — Exactly one matching `005-n` order and no pre-existing `005-n`
  report were present.
- PASSED — Exact clean Gateway head, reachability, report topology, app-tree
  identity, historical-hook absence, and ten required remote check conclusions
  were verified.
- PASSED — The task-controlled Codex binary reported `0.149.0` and matched
  SHA-256 `bbc3341e44c9ead340ed9570c17be936e37870f570751a941699ffd04d672827`.
- PASSED — The fixed direct topology and stop-at-first-failure rules were
  exercised by the permanent fake harness; no relay or alternate provider was
  used.

### Criterion 2 — Local and exact-pair fake gates

- PASSED — Local full frozen unit suite, focused regression suite, Ruff,
  format, mypy, compileall, build, wheel/sdist boundary, shell syntax, stale
  pin, diff, and raw-content logging scans.
- PASSED — Actual exact-head Gateway tool-policy differential.
- PASSED — Actual exact-head Gateway provider adapter differential for bounded
  JSON/SSE, usage, model rewrite, credential/header filtering, and metrics.
- PASSED — Exact-head Gateway product/verifier pytest subset from the detached
  checkout, including Local Coding, route/tool, provider, identity, streaming,
  and Codex verifier modules.
- PASSED — Complete fake Gateway -> Local -> fake-Qwen composition, including
  readiness/model visibility, terminal SSE lifecycle, tool filtering, image
  adaptation, compiler/cache/rehydration, quota/failure/accounting, privacy,
  and cleanup.

### Criterion 3 — one complete real protected acceptance matrix

- BLOCKED — Authenticated protected model visibility could not be attempted
  because the documented protected credential reference was unavailable to the
  coding process. The bounded unauthenticated probes returned health HTTP 200
  and model-list HTTP 401. No protected inference or image request was sent.
- NOT RUN — Real Codex two-turn tool stream, governance/dependency acquisition,
  same-session rehydration, vision full-image/crop, replay/tamper/isolation,
  complete protected accounting, controlled provider failure, and full no-bypass
  acceptance.

### Criterion 4 — controlled candidate cutover and rollback

- NOT RUN — Section D is gated on a fully green protected Section C. No
  candidate Local/Gateway unit, temporary production-style profile, persistent
  configuration, or active OAP profile was installed or switched.

### Criterion 5 — protected fixture and cleanup

- PASSED — Host identity was `hinton1`; the protected vision service remained
  active/running with PID `23961`, start timestamp
  `Sun 2026-09-06 18:57:26 CEST`, and zero restarts before and after the round.
- PASSED — The protected vision listener remained present; text service stayed
  inactive; no listener remained on candidate/alternate ports 18021, 18030, or
  18031.
- PASSED — The Qwen checkout retained seven pre-existing uncommitted entries.
  No protected checkout, service, model, credential source, network binding,
  firewall/VPN state, or active Codex profile was changed.

## Verification

- `uv run --frozen pytest -q`: PASSED — 578 passed, 8 skipped in 42.50s.
- Focused Local regression suite over app/cache/compiler/e2e/gateway/image/
  injection/observation/pipeline/rehydration/tool/vision/working-set tests:
  PASSED — 486 passed, 1 skipped in 42.90s.
- `uv run --frozen ruff check .`: PASSED.
- `uv run --frozen ruff format --check .`: PASSED — 233 files already formatted.
- `uv run --frozen mypy src tests`: PASSED — 53 source files.
- `python3.12 -m compileall -q src tests oap/bin`: PASSED.
- `bash -n oap/bin/*.sh`: PASSED.
- `uv build`: PASSED — wheel and sdist built.
- Wheel package-boundary check: PASSED — no `scripts/`, `tests/`, or
  `references/` package paths.
- Stale accepted-Gateway-pin scan and raw-content logging scan: PASSED.
- Exact Gateway tool-envelope differential with Codex 0.149.0: PASSED.
- Exact Gateway provider-adapter differential: PASSED.
- Exact Gateway product/verifier subset: PASSED; the checkout was clean after
  the run.
- Fake Gateway -> Local -> fake-Qwen accounting rehearsal: PASSED — fake
  terminal stream, cache/rehydration, image/tool policy, quota/failure,
  accounting, privacy, and temporary-resource cleanup facts passed.
- Authenticated protected health/model preflight: BLOCKED — credential
  reference unavailable; unauthenticated health 200 and model-list 401.
- Local implementation-head GitHub CI run `34048965964`, required `test` check:
  PASSED — SUCCESS at `3e072a4ec57947fe7ee003bfcffd404d5363768d`.

## Live model/service evidence

- Bounded read-only fixture observations were made on `hinton1` only.
- Vision service identity before/after: active/running, PID `23961`, the stated
  start timestamp, zero restarts, and unchanged protected listener.
- Text service remained inactive; candidate and alternate listeners were absent.
- No protected model content, prompt, image, response, tool data, credential,
  identity, signature, nonce, or raw SSE was retained or reported.
- Protected C acceptance and all model inference/vision cases were NOT RUN after
  the credential blocker. The protected model service was not restarted,
  reconfigured, replaced, or switched.

## GitHub CI / required checks

- Local implementation-head `test`: SUCCESS at
  `3e072a4ec57947fe7ee003bfcffd404d5363768d` (run `34048965964`, job
  `101529010028`).
- Exact Gateway implementation-head checks: SUCCESS — `Unit, lint, and
  migration head`; `Analyze (javascript-typescript)`; `Analyze Python`;
  `Analyze (python)`; `PostgreSQL integration tests`; `OpenAI-compatible E2E
  tests`; `Playwright browser smoke`; `Docker Compose smoke`; `Documentation
  hygiene`; and `CodeQL`.
- All required checks green at drafting: YES.
- Report-head checks may be pending after publication; strategy verifies them
  independently.

## Local setup/dependencies

- Used the existing ignored Local `.venv` and a task-owned Python 3.12
  environment containing the exact detached Gateway dependencies.
- Used a clean detached Gateway checkout at the exact required head. The fake
  rehearsal used one bounded loopback-only PostgreSQL 16 resource with cleanup;
  no persistent database or model process was started.
- No protected credential was installed, copied, printed, or persisted.

## Documentation

Not updated. The order permits the integration/runbook/configuration and
Objective-005 ledger updates only after complete protected C and D acceptance;
those criteria were blocked before protected inference.

## Lifecycle state at publication

| Label | State |
|---|---|
| `IMPLEMENTED` | yes |
| `TESTED` | yes, Local and fake gates |
| `REAL-E2E ACCEPTED` | no |
| `CUTOVER ACCEPTED` | no |
| `MERGED` | no |
| `RELEASE-READY` | no |

## Safety/scope confirmations

- Unrelated files: none committed.
- Secrets/raw customer content: none committed, logged, or reported.
- Gateway source/PR #297/Gateway main changed: NO.
- Protected 18020/Qwen/Codex fixture changed: NO.
- Active/order edited by coding: NO; exact activated bytes were committed.
- Required protected downstream tests: NOT RUN after the pre-inference
  credential blocker.
- Extra objective PR: NO.
- Coding merge/auto-merge: NO.
- Report commit report-only: YES.

## Known limitations/blockers

- The documented authenticated protected credential reference was unavailable
  to this coding process. Consequently protected model visibility could not be
  established and the order's real C matrix could not begin.
- No protected product/accounting verdict, real Codex governance result,
  vision result, or cutover/rollback claim follows from this round.
- The Local implementation is pinned to the exact clean Gateway head and all
  repository/fake evidence is green, but fake evidence does not substitute for
  the blocked protected matrix.

## Recommended strategic follow-up

Re-establish the authorized protected credential reference for the coding
acceptance process, then issue the appropriate same-PR continuation so strategy
can decide whether to rerun the single ordered protected matrix. Preserve the
unchanged Qwen fixture and do not infer C/D acceptance from this report.

# OAP Coding-Agent Report — 005-m

## Work order

- Identifier: `005-m`
- Order path: `oap/orders/005-m-gateway-155r-real-codex-matrix-and-cutover-closure.md`
- Numeric objective: `005`
- PR mode: `AMENDED_EXISTING_PR`

## Status

FAILED

## Executive summary

The exact accepted Gateway 155-r checkout and the Local repository-only
acceptance harness were pinned and exercised. Local static, unit, package,
identity, tool, fake-composition, and cleanup gates passed. One ordered
protected disposable matrix then reached readiness, model visibility, ordinary
non-streaming text, and the first streaming request. It stopped at the first
Gateway stream-validation error before terminal completion. The protected
Qwen service and all protected host state were preserved. Per the order's stop
law, no protected retry and no candidate cutover were performed.

## Authoritative GitHub state

- Repository: `ulfe-lmi/slaif-local-coding`
- PR: [#7](https://github.com/ulfe-lmi/slaif-local-coding/pull/7)
- PR state: OPEN, non-draft, MERGEABLE/CLEAN
- Base/head: `main` / `oap/005-gateway-ingress-integration`
- Starting remote SHA: `1a87ce1c6628885e567cecc8f4a9e78ce7078341`
- Implementation head SHA: `258ae2ebad39651076937b9f027e60831b8d2786`
- Report publication commit: SELF
- Implementation commits pushed before report: `8dc2f355a73899457d587e690af3016d3a812b6f`, `258ae2ebad39651076937b9f027e60831b8d2786`
- New PR this round: NO
- Amended existing PR: YES, PR #7
- Merge performed: NO

The accepted Gateway dependency was verified at report head
`2527030f5bbb90a7f0f354eb5347caee333ce4a7`, with final implementation parent
`19d9686636b0fbf27ab96d41c610a37dad3c087a`, open/non-draft/mergeable-clean
state, and all ten current checks SUCCESS. Its report commit changes only the
accepted 155-r report path and has the stated implementation parent.

## Changes and files

- Updated all three Local repository-only Gateway acceptance constants from
  the superseded 155-p value to exact accepted 155-r report head
  `2527030f5bbb90a7f0f354eb5347caee333ce4a7`:
  `scripts/codex_tool_envelope_differential.py`,
  `tests/helpers/gateway_accounting_rehearsal.py`, and
  `tests/helpers/gateway_provider_driver.py`.
- Updated the disposable fake provider to emit the exact bounded 155-r
  reasoning and assistant-message lifecycle, including detailed terminal
  usage.
- Configured the disposable vision route with explicit
  `drop_disabled_codex_search`, so hosted `tool_search` and `web_search`
  declarations are removed before the fake provider while ordinary function
  and custom declarations remain:
  `tests/helpers/vision_e2e_support.py`.
- Committed the exact activated `oap/active` and `005-m` order bytes unchanged.

## Acceptance evidence

### Criterion 1 — exact-head preflight, pins, and fake matrix

- PASSED — `oap/active` selected exactly one matching `005-m` order, and the
  existing Local PR #7 was amended. No new objective PR was created.
- PASSED — Gateway PR #291 was verified at exact accepted head
  `2527030f5bbb90a7f0f354eb5347caee333ce4a7`; the detached checkout was clean.
- PASSED — Actual Gateway product provider, header, request-policy, and route
  capability modules were imported and exercised by the repository-only
  differential/provider drivers. No Gateway source was copied or modified.
- PASSED — The separate official Codex binary reported version `0.149.0`; its
  locally observed binary SHA-256 was
  `bbc3341e44c9ead340ed9570c17be936e37870f570751a941699ffd04d672827`.
  The active 0.150.1 installation was not substituted.
- PASSED — Exact Gateway tool-policy differential: four bounded variants were
  accepted while preserving ordinary function/custom declarations; no model
  or Gateway service was started by this check.
- PASSED — Exact provider-adapter differential: non-stream status 200, usage
  total class 5, stream status 200 with three ordered lifecycle events,
  credential/header filtering, model rewrite, and secret-free metrics.
- PASSED — Complete fake Gateway → Local → fake-provider composition with the
  accepted 155-r stream lifecycle: stream contract passed, one created and one
  completed event, one provider call, finalized reservation/ledger, one image
  observed, one compiler attempt, one cache hit, one zero-root rehydration hit,
  ordinary function/custom tools only at the fake provider, quota/failure
  checks, secret-free logs, and complete temporary cleanup.

### Criterion 2 — one protected composed acceptance

- PASSED — The one disposable protected run used exact Gateway 155-r code,
  Local candidate code, temporary PostgreSQL, the official Codex 0.149.0
  binary, and the direct Gateway → Local → protected-Qwen topology.
- PASSED — Protected health/model preflight, Local/Gateway readiness, model
  visibility, and ordinary non-streaming text progressed before the stream gate.
- FAILED — The first protected streaming request returned a 2xx SSE response
  and one provider call, but produced a Gateway-owned `gateway_error_event`
  before terminal completion. Safe stream facts were: one created event, zero
  completed events, recognized vocabulary, normal transport close, Local
  upstream status class `2xx`, Local failure class `none`, Local request delta
  `1`, provider call class `1`, reservation terminal `true`, and ledger
  terminal `false`.
- NOT RUN — No protected retry, alternate stream, alternate prompt, or
  diagnostic control was issued.
- NOT RUN — Real Codex governance/tool/dependency behavior, same-session
  history-reduction rehydration, real Codex vision full-image/crop interaction,
  replay/concurrent replay, tamper, isolation, quota/accounting completion,
  compiler-public separation, controlled provider failure, and full no-bypass
  acceptance after the first stream failure.

### Criterion 3 — cleanup and protected-host preservation

- PASSED — Candidate and Gateway listeners were removed; temporary PostgreSQL,
  cache, Codex, logs, and other task state were cleaned up.
- PASSED — The protected Qwen vision process PID, start fact, restart count,
  and listener fact were unchanged. The protected text service remained
  inactive, and no development/alternate listener remained.
- PASSED — No Qwen service/unit/config/model/checkpoint/launch flag,
  credential source, network binding, firewall/VPN state, or active OAP Codex
  profile was changed.

### Criterion 4 — controlled candidate cutover and rollback

- NOT RUN — Section C was gated on a fully green Section B. No Local/Gateway
  candidate unit, temporary production-style profile, Gateway route, or
  persistent configuration was installed or switched; exact rollback was not
  entered.

## Verification

- `uv run --frozen pytest -q`: PASSED — 578 passed, 8 skipped.
- Focused vision/tool/pipeline suite: PASSED — 153 passed, 1 skipped.
- `uv run --frozen ruff check .`: PASSED.
- `uv run --frozen ruff format --check .`: PASSED — 231 files formatted.
- `uv run --frozen mypy src tests`: PASSED — 53 source files.
- `python3.12 -m compileall -q src tests oap/bin`: PASSED.
- `uv build` wheel and sdist validation: PASSED.
- Wheel package-boundary check: PASSED — no `scripts/`, `tests/`, or
  `references/` paths.
- `git diff --check`: PASSED.
- Stale accepted-Gateway-pin scan: PASSED — superseded 155-p pin absent from
  acceptance drivers/helpers.
- Raw-content logging pattern scan: PASSED — no matching raw-body/prompt/
  source/image/tool/auth logging pattern.
- Exact Gateway/Local tool-policy differential: PASSED.
- Exact Local/Gateway provider-adapter differential: PASSED.
- Fake composed rehearsal: PASSED — accepted stream lifecycle, tool filtering,
  image, constitution/cache/rehydration, quota, accounting, privacy, and
  cleanup facts.
- Protected composed rehearsal: FAILED — first stream gate
  `gateway_error_event`; no retry.
- `gh run watch 33346680306 --repo ulfe-lmi/slaif-local-coding --exit-status`:
  PASSED — implementation-head CI completed successfully.

## Live model/service evidence

- Protected vision Qwen health and model visibility preflight each returned
  HTTP 200 using the existing protected credential reference without exposing
  its value.
- Exactly one protected composed stream request reached the protected Qwen
  path before the Gateway stream gate failed. No image-content, prompt,
  response, tool-output, credential, identity, signature, nonce, or raw SSE
  value was retained.
- Post-run protected facts remained unchanged: vision active/running with the
  same PID/start/restart facts and listener; text inactive; no candidate
  listener.

## GitHub CI / required checks

- Local implementation-head `test`: SUCCESS at
  `258ae2ebad39651076937b9f027e60831b8d2786` (run `33346680306`, job
  `99352017793`).
- Gateway exact accepted 155-r head: all ten SUCCESS — `Unit, lint, and
  migration head`; `Analyze (javascript-typescript)`; `Analyze Python`;
  `Analyze (python)`; `PostgreSQL integration tests`; `OpenAI-compatible E2E
  tests`; `Playwright browser smoke`; `Docker Compose smoke`; `Documentation
  hygiene`; `CodeQL`.
- All required checks green at report drafting: YES.
- Report-head checks may be pending; strategy verifies them independently.

## Local setup/dependencies

- Used a clean detached checkout of exact Gateway 155-r code and a temporary
  Python 3.12 virtual environment with Gateway runtime/development
  dependencies.
- Used one disposable PostgreSQL 16 container with loopback-only random port,
  tmpfs-only data, bounded lifetime, and cleanup. No persistent database or
  model process was started.
- Used the repository's existing ignored Local `.venv`; it was preserved.

## Documentation

Not updated. The order requires integration, runbook, configuration, and
Objective-005 state-ledger updates only after a complete green B+C acceptance;
Section B failed at its first protected stream gate.

## Lifecycle state at publication

| Label | State |
|---|---|
| `IMPLEMENTED` | yes |
| `TESTED` | yes |
| `REAL-E2E ACCEPTED` | no |
| `CUTOVER ACCEPTED` | not yet |
| `MERGED` | no |
| `RELEASE-READY` | no |

## Safety/scope confirmations

- Unrelated files: none committed.
- Secrets/raw customer content: none committed, logged, or reported.
- Gateway PR #291 changed: NO.
- Protected 18020/Qwen/Codex fixture changed: NO.
- Active/order edited by coding: NO; exact activated bytes were committed.
- Required protected downstream tests: NOT RUN after the first stream failure.
- Extra objective PR: NO.
- Coding merge/auto-merge: NO.
- Report commit report-only: YES.

## Known limitations/blockers

- The exact protected composed request failed at the first Gateway stream
  validation gate with safe owner classification `gateway_stream_owned`; no
  terminal stream, real Codex governance, vision, replay/tamper, complete
  accounting, or cutover claim follows.
- The fake harness now matches the accepted 155-r reasoning/message lifecycle
  and explicit Local hosted-tool filtering, but fake success is not a
  substitute for the failed protected matrix.
- Exact cause of the protected stream rejection is not inferred from raw
  payloads and was not pursued with a retry, Gateway modification, or Qwen
  modification.

## Recommended strategic follow-up

Review the bounded `gateway_error_event` result against the accepted Gateway
155-r stream contract and decide whether a same-PR continuation should address
the first failing boundary. Any continuation must re-verify exact heads and
must not mutate protected Qwen or Gateway code without a separately authorized
scope.

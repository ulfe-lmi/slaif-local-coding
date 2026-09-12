# OAP Coding-Agent Report — 005-c

## Work order
- Identifier: `005-c`
- Order path: `oap/orders/005-c-disposable-full-gateway-accounting-rehearsal.md`
- Numeric objective: `005`
- PR mode: `AMENDED_EXISTING_PR`

## Status
FAILED

## Executive summary
Added repository-only disposable gateway/PostgreSQL/Local Coding rehearsal
support, hermetic content-free fact tests, and runbook/completeness evidence.
The bounded rehearsal reached the seeded public model route, standard
non-streaming text, a validated Responses SSE sequence with completed usage,
and one inline image request. The real Codex 0.149.0 phase was rejected by the
pinned gateway's Codex tool-envelope policy before a public reservation, so the
full acceptance contract was not proven. All temporary service state was
cleaned up and the protected vision fixture was unchanged.

## Authoritative GitHub state
- Repository: `ulfe-lmi/slaif-local-coding`
- PR: [#7](https://github.com/ulfe-lmi/slaif-local-coding/pull/7), OPEN, non-draft, MERGEABLE, CLEAN
- Base/head: `main` / `oap/005-gateway-ingress-integration`
- Starting remote SHA: `2df2b03627b2bd04609d56202e01e83e205e8791`
- Implementation head SHA: `45f712aff53e8f71669ba51314cce790838d8e0a`
- Report publication commit: SELF
- Implementation commits pushed before report: `45f712aff53e8f71669ba51314cce790838d8e0a`
- New PR this round: NO; amended existing PR: YES; merge performed: NO

## Changes and files
- Added `scripts/gateway_accounting_rehearsal.py`, outside the production
  wheel, for one bounded detached-pinned-gateway rehearsal with temporary
  PostgreSQL 16, repository/service seeding, public OpenAI-client traffic,
  Codex execution, safe accounting evidence, and teardown.
- Added `tests/helpers/gateway_accounting_rehearsal.py` and
  `tests/test_gateway_accounting_rehearsal.py` for content-free fact
  contracts.
- Updated gateway integration, OAP runbook, and completeness documentation
  with the failed rehearsal result and remaining tool-contract limitation.
- Committed the activated `oap/active` and exact `005-c` order bytes
  unchanged.

## Acceptance evidence
### Criterion A — disposable pinned topology
- PARTIAL: remote gateway `main` resolved to the required pinned SHA
  `8f2813bf745b90221da33a7cfaf40726c5b1b480`; the temporary database was
  loopback-only, tmpfs-backed, and removed.
- PASSED: Local Coding candidate ran on loopback port `18031` with service
  Bearer static identity and a fresh private cache; the protected Qwen
  vision service remained the upstream.

### Criterion B — public route and standard traffic
- PASSED: authenticated public model visibility exposed one seeded public
  route/model.
- PASSED: non-streaming Responses text reached the protected model and
  returned provider usage.
- PASSED: one bounded Responses SSE request reached the provider with typed
  events and a completed usage event.
- PASSED: one small synthetic inline image request reached the selected
  vision route; candidate image metrics recorded one image seen and none
  removed for that request.

### Criterion C — accounting boundary
- PARTIAL: completed standard requests had one finalized reservation and
  ledger row per successful public request, no pending reservation, and
  provider usage available for finalization.
- PASSED: an invalid public key was rejected before Local Coding, and an
  intentional over-quota request was rejected before Local Coding.
- FAILED: the Codex portion created no public reservation because the
  gateway rejected its tool envelope before provider forwarding.

### Criterion D — real Codex text/tool/governance traffic
- FAILED: the disposable Codex 0.149.0 global-yolo invocation failed during
  startup with a gateway tool-envelope rejection; no ordinary dependency
  read, hidden governance binding, compiler metric delta, or Codex accounting
  row was claimed.
- BLOCKED: resolving the mismatch requires a separate authorized gateway/tool
  contract decision; this repository did not weaken the pinned gateway or
  fabricate compatibility.

### Criterion E — rollback and protected-host preservation
- PASSED: temporary gateway/candidate listeners, PostgreSQL container,
  postgres image pulled for this run, detached checkout, disposable venv,
  cache, Codex home, fixture, and logs were removed.
- PASSED: protected vision service PID/start facts and port `18020`
  listener were unchanged; text service remained inactive and no
  `18021`/`18031` listener remained.

## Verification
- `uv run --frozen pytest -q tests/test_gateway_accounting_rehearsal.py`: PASSED — 2 passed.
- `uv run --frozen ruff check scripts/gateway_accounting_rehearsal.py tests/helpers/gateway_accounting_rehearsal.py tests/test_gateway_accounting_rehearsal.py`: PASSED.
- `uv run --frozen ruff format scripts/gateway_accounting_rehearsal.py tests/helpers/gateway_accounting_rehearsal.py tests/test_gateway_accounting_rehearsal.py`: PASSED.
- `python3.12 -m py_compile scripts/gateway_accounting_rehearsal.py tests/helpers/gateway_accounting_rehearsal.py`: PASSED.
- `git diff --check`: PASSED.
- `uv run --frozen pytest -q` locally after the final support edits: NOT RUN — broad gate ran remotely.
- `python scripts/gateway_accounting_rehearsal.py ...`: FAILED — standard subset reached the protected fixture; Codex tool-envelope rejection stopped the ordered acceptance path.
- GitHub CI `test` on implementation head: PASSED — Ruff, format, mypy, full pytest, build, compileall, and shell syntax steps successful.

## Live model/service evidence
- Protected endpoint: loopback Qwen/vLLM port `18020`; bounded health and
  authenticated model discovery were successful before the run.
- Vision unit: active/running before and after; text unit inactive before and
  after; no pre-existing image proxy was assumed.
- Candidate/gateway/PostgreSQL temporary state: removed.
- Protected Qwen/model/vLLM/network/Codex profile state changed: NO.

## GitHub CI / required checks
- Implementation-head check: CI `test` SUCCESS / COMPLETED for
  `45f712aff53e8f71669ba51314cce790838d8e0a`.
- All required checks green at drafting: YES.
- Report-head checks may be pending; strategy verifies them independently.

## Local setup/dependencies
- Installed the pinned gateway runtime and OpenAI client only in a disposable
  temporary venv; removed it after evidence extraction.
- Pulled official `postgres:16` only because it was absent at preflight;
  recorded its image facts and removed the exact image after teardown.
- No gateway repository file, gateway PR, Local Coding lockfile, model weight,
  systemd unit, firewall, network binding, or protected credential file was
  changed.

## Documentation
- Updated: `docs/SLAIF-GATEWAY-INTEGRATION.md`,
  `docs/OAP-RUNBOOK.md`, and `oap/COMPLETENESS.md`.
- Added repository-only driver/fact-test support; production package
  contents were not expanded.

## Safety/scope confirmations
- Unrelated files: none intentionally changed.
- Real credentials, raw prompts, source, images, tool output, customer data,
  and model weights: not committed or written to report/metrics.
- Protected 18020/Qwen/Codex fixture changed: NO.
- Extra objective PR: NO; coding merge: NO.
- Active/order edited: NO; activated bytes committed unchanged.
- Report commit report-only: YES.
- Exact-one full-rehearsal constraint: NOT SATISFIED — bounded driver
  development was iterated while diagnosing pre-model contract failures;
  the final failure is reported without claiming acceptance.
- Scope deviation: a bounded direct protected-Qwen SSE shape diagnostic was
  run during diagnosis; it did not mutate the fixture.
- Security stop: a diagnostic search accidentally traversed the host Codex
  session cache and exposed sensitive session content to local tool output.
  Further live probing stopped immediately; no session content was retained
  in repository files, report, metrics, or driver facts. Strategic/human
  security review is required.

## Known limitations/blockers
- The pinned gateway rejects the real Codex 0.149.0 tool envelope used by
  the disposable fixture before reservation/provider forwarding.
- Full Codex text/tool/governance accounting and end-to-end compatibility are
  NOT PROVEN.
- Trusted signed per-user identity and persistent production cutover remain
  outside this round.
- The diagnostic security event must be reviewed before further live probing.

## Recommended strategic follow-up
- Review the security event and decide whether additional host-session
  containment or credential/session rotation is required.
- Decide the gateway/Codex tool-envelope contract and issue a new authorized
  same-PR continuation if remediation is desired.
- Do not treat this failed rehearsal as gateway acceptance, production
  readiness, or cutover approval.

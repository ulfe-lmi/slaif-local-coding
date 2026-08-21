# OAP Coding-Agent Report — 000-a

## Work order

- Identifier: `000-a`
- Order: `oap/orders/000-a-live-contract-and-adapter-foundation.md`
- Numeric objective: `000`
- PR mode: `CREATED_NEW_PR`

## Status

COMPLETE

## Executive summary

Implemented and live-validated the objective-000 Python 3.12 adapter foundation. The
candidate is loopback-only, proxies the required OpenAI-compatible endpoints with
bounded asynchronous streaming, replaces caller authentication with protected
upstream authentication, exposes private health/readiness/metrics, and enforces an
explicit model/route image policy. The bounded live matrix passed against the existing
vision vLLM. The temporary foreground candidate was stopped, and the protected model
service and configuration were preserved.

## Authoritative GitHub state

- Repository: `ulfe-lmi/slaif-local-coding`
- PR: #1, `https://github.com/ulfe-lmi/slaif-local-coding/pull/1`, OPEN and non-draft
- Base/head: `main` / `oap/000-adapter-foundation`
- Starting remote SHA: `bcdb3542a74a08219496ef29a09fd13b543e954c`
- Implementation head SHA: e49c54da8b3562cc9639d4a095c340ecc4042fb4
- Report publication commit: SELF
- Implementation commits pushed before report: `e49c54da8b3562cc9639d4a095c340ecc4042fb4`
- New PR this round: YES; amended existing PR: NO; merge performed: NO

## Changes and files

- Added locked package/CI foundation: `pyproject.toml`, `uv.lock`, and
  `.github/workflows/ci.yml`.
- Added typed modules under `src/slaif_local_coding/` for strict configuration,
  route-scoped image handling, async proxying, CLI startup, safe metrics, readiness,
  header filtering, bounded bodies/timeouts, and sanitized failures.
- Added fake-upstream, policy, configuration, disconnect, metrics/log, and opt-in live
  tests under `tests/`.
- Added candidate configuration, loopback user-service example, quickstart,
  configuration/operations contract, and dependency-license review.
- Committed the activated `oap/active` and order bytes unchanged.

## Acceptance evidence

### Criterion 1 — one objective PR

- PASSED: GitHub reports exactly PR #1, OPEN, non-draft, title
  `[OAP 000] Add live-tested adapter foundation and image policy`, base `main`, head
  `oap/000-adapter-foundation`. Coding performed no merge.

### Criterion 2 — locked Python and verification baseline

- PASSED: Python 3.12 package, committed lock, frozen CI/local commands, Ruff, mypy,
  pytest, build, compile, shell syntax, and license/provenance documentation exist.

### Criterion 3 — candidate and forwarding

- PASSED: foreground service listened only on `127.0.0.1:18031`; health, readiness,
  model passthrough, Responses, and Chat calls succeeded. It was stopped after tests.

### Criterion 4 — proxy fidelity and disconnect

- PASSED: fake-upstream tests cover status/error body, selected response headers,
  upstream-auth replacement, internal/hop-header filtering, tools, usage,
  `function_call_output`, SSE event/chunk order, timeout sanitation, and upstream close
  after downstream disconnect.

### Criterion 5 — image policies

- PASSED: pure and adapter tests cover zero/one preservation, nested Responses/Chat
  images, deterministic newest retention, non-image relative order, reject without an
  upstream call, passthrough, malformed/ambiguous shapes, and final count enforcement.

### Criterion 6 — explicit route policy

- PASSED: model and endpoint select a validated configured route; no unique match
  returns API-shaped 422. Unknown policy/configuration fails validation.

### Criterion 7 — bounded authenticated live matrix

- PASSED: 5 live tests cover health/models, ordinary Responses text, forced and
  automatic function calls with JSON arguments, SSE text and function-call events,
  multi-turn `function_call_output`, one-image Chat vision, and two-image Chat history
  through the candidate retaining the newest image.

### Criteria 8–10 — bounded load, privacy, documentation

- PASSED: live calls were serial with small output bounds and synthetic inputs. Tests
  prove raw sentinel values do not enter application logs/metrics. Documentation
  records strict routing, no retries, newest-image semantic limits, loopback operation,
  rollback, gateway separation, and no cutover.

### Criterion 11 — protected fixture preservation

- PASSED: after testing, the original vision unit remained active/running with PID
  4174 and its original start timestamp; only `10.8.132.76:18020` was listening, with
  no 18021/18031 listener. The launch command and one-image limit matched preflight.
  Protected launch-config metadata and SHA-256 remained mode 0777, size 285, and
  `affabb5701b67b5fcb7cab2e3ae1835e84e19dc98a7f1eb245cf3e49b76b3b5b`.

### Criterion 12 — OAP transcript

- PASSED through implementation publication. This SELF report is the only final file
  added by its child commit; remote-parent/head verification follows publication.

## Verification

- `uv lock --check`: PASSED — resolved 32 packages.
- `uv sync --frozen --extra dev`: PASSED — checked 31 installed packages.
- `uv run --frozen ruff check .`: PASSED.
- `uv run --frozen ruff format --check .`: PASSED — 38 files formatted.
- `uv run --frozen mypy src tests`: PASSED — 10 source files, no issues.
- `uv run --frozen pytest -q`: PASSED — 14 passed; 5 opt-in live tests SKIPPED in the
  ordinary invocation, then run separately below.
- `SLAIF_LIVE_TEST=1 uv run --frozen pytest -q tests/test_live.py`: PASSED — 5 passed
  in 6.39 seconds.
- `uv build`: PASSED — source distribution and wheel built.
- `python3 -m compileall -q src tests oap/bin`: PASSED.
- `bash -n oap/bin/*.sh`: PASSED.
- `git diff --check`: PASSED.
- credential-pattern and raw-sentinel scans: PASSED — no candidate secret files,
  high-confidence key patterns, or application/docs raw test sentinels found.

## Live model/service evidence

- Upstream: authenticated private vLLM at the configured host/port, model
  `qwen3.8-27b`; no credential value printed or persisted.
- Candidate: foreground `127.0.0.1:18031`, stopped after tests.
- Sanitized results: health/readiness/models/text/tool/SSE/multi-turn/one-image/two-image
  cases all asserted HTTP 200 and expected envelope/event structures.
- Fixture after test: vision unit active/running, PID 4174; launch timestamp unchanged;
  original one-image vLLM command unchanged; only port 18020 listening.

## GitHub CI / required checks

- Implementation-head check `test`: SUCCESS at
  `e49c54da8b3562cc9639d4a095c340ecc4042fb4` (20 seconds, Actions run 32431820800).
- All required checks green at drafting: YES.
- Report-head checks may be pending after publication; strategy verifies them.

## Local setup/dependencies

- Installed `uv 0.12.5` into temporary `/tmp/slaif-uv-tool`; application/test
  dependencies are repo-local in ignored `.venv` and locked by `uv.lock`.
- Used a foreground candidate only. No service installed/enabled and no sudo action.
- Built artifacts are ignored under `dist/`.

## Documentation

- Updated README quickstart/status, example configuration, third-party license review,
  and added `docs/ADAPTER-CONFIGURATION.md` plus an uninstalled candidate systemd
  example.
- Durable architecture files were not changed because the implementation follows the
  activated compact architecture without correction.

## Safety/scope confirmations

- Unrelated files preserved; no production/customer data used.
- Secrets/raw prompts/tool output/images committed or logged: NO. The live image was a
  small synthetic fixture embedded only in test source.
- Protected 18020/Qwen/vLLM/Codex fixture changed: NO.
- The known protected `qwen-serving-vision.env` mode-0777 risk was preserved
  byte-for-byte and not remediated without authority.
- Firewall, VPN, key files, systemd service/unit, model files, Qwen venv, and active
  Codex profile were not modified by this round.
- Required tests skipped/not run: NONE after separate opt-in live execution.
- Scope deviation: NONE. Constitutional/compiler/cache/gateway work not implemented.
- Extra objective PR: NO; coding merge: NO.
- Active/order edited: NO; final report commit report-only: YES by staged/commit/remote
  verification procedure.

## Known limitations/blockers

- The route intentionally cannot preserve explicit multi-image comparison semantics.
- MVP binds loopback and does not implement gateway signed identity/service-auth; that
  remains a later objective.
- The protected launch environment file remains mode 0777; remediation requires a
  separately authorized protected-host order.
- GitHub emitted a non-failing runner annotation that Node.js 20 actions are being
  forced onto Node.js 24; the required `test` check succeeded.

## Recommended strategic follow-up

Independently verify the SELF parent/report-only commit, report-head CI, protected
fixture state, and objective acceptance. Decide separately whether to authorize a
protected-file permission remediation; do not conflate it with this adapter PR.

# OAP Coding-Agent Report — 000-c

## Work order

- Identifier: `000-c`
- Order: `oap/orders/000-c-bound-json-structure-and-fail-closed.md`
- Numeric objective: `000`
- PR mode: `AMENDED_EXISTING_PR`

## Status

COMPLETE

## Executive summary

Added an explicit JSON container nesting contract before JSON decoding and recursive
image work. A string/escape-aware iterative byte scan permits the configured depth
(default 128, validated range 1–256) and returns sanitized API-shaped HTTP 400 code
`json_nesting_too_deep` at depth+1 without contacting upstream. Narrow residual
`RecursionError` handling covers decoding, image counting, deep copy/transformation,
final image verification, and JSON serialization without catching unrelated errors.
The strategic depth-600 reproducer, image-bearing and non-image variants, safe metrics,
ordinary Responses/Chat/tool/image compatibility, full fake suite, authenticated live
suite, packaging gate, and current-head CI all passed. The candidate was stopped and
the protected fixture remained unchanged.

## Authoritative GitHub state

- Repository: `ulfe-lmi/slaif-local-coding`
- PR: #1, `https://github.com/ulfe-lmi/slaif-local-coding/pull/1`, OPEN and non-draft
- Base/head: `main` / `oap/000-adapter-foundation`
- Starting remote SHA: `99f2c651de7b6b9ae83eb7fbc1e8584175eed2b1`
- Implementation head SHA: 9f9739943bf6d763664970b553dd58fd96c481bd
- Report publication commit: SELF
- Implementation commits pushed before report: `9f9739943bf6d763664970b553dd58fd96c481bd`
- New PR this round: NO; amended existing PR: YES; merge performed: NO

## Changes and files

- `src/slaif_local_coding/json_structure.py`: bounded iterative raw-JSON nesting scan
  that tracks string and escape state and counts only structural `{`, `[`, `}`, `]`.
- `src/slaif_local_coding/config.py`, `config/adapter.example.toml`: typed
  `json_max_nesting_depth`, default 128 and validation range 1–256.
- `src/slaif_local_coding/app.py`: pre-decode enforcement and narrow sanitized parser/
  transformation recursion handling; all rejects use existing bounded local metrics.
- `tests/test_json_structure.py`, `tests/test_app.py`, `tests/test_config.py`: pure
  measurement cases, exact bound, depth+1, depth 600, supported image markers, deep
  non-image input, no-upstream and no-leak proof, bounded metric proof, ordinary
  Responses/Chat tool-image compatibility, and configuration validation.
- `README.md`, `docs/ADAPTER-CONFIGURATION.md`: exact depth/status/code/no-upstream
  contract and independence from the existing byte cap.
- Committed the strategic-authored `oap/active` and `000-c` order bytes unchanged.

## Acceptance evidence

### Criterion A — deterministic structural bound

- PASSED: the iterative raw-byte scanner runs before `json.loads`, image traversal,
  `deepcopy`, final image counting, and transformed serialization. Its own call stack
  is constant; body storage remains independently bounded by `request_body_max_bytes`.
- PASSED: pure tests cover arrays, objects, mixed nesting, empty containers, and JSON
  strings containing brackets, braces, backslashes, and escaped quotes. The exact
  configured depth passes and depth+1 rejects.
- PASSED: configuration exposes a conservative default of 128 and refuses values
  outside 1–256, keeping later recursive application work below interpreter limits.

### Criterion B — fail-closed behavior

- PASSED: depth+1 returns HTTP 400 with fixed type `invalid_request_error`, fixed code
  `json_nesting_too_deep`, fixed sanitized message, and zero upstream calls.
- PASSED: the depth-600 nested-list reproducer returns the same 400 rather than an
  exception/500. Both deep non-image and supported-image-marker variants make zero
  upstream calls and cannot bypass image enforcement.
- PASSED: the bounded request counter records only endpoint, configured/fixed route,
  status, and stream labels. Sentinel data and `RecursionError` text are absent from
  response, captured logs, and metrics.
- PASSED: malformed UTF-8/JSON, ambiguous image, unknown route, body size, auth,
  timeout, upstream error, query/header/compression, and image behavior remain covered
  by the cumulative green suite.

### Criterion C — compatibility and exact tests

- PASSED: representative nested Responses and Chat Completions requests containing
  tool schemas and one image preserve their prior semantics and reach fake upstream.
- PASSED: cumulative tests cover byte-boundary and early-consumption behavior,
  synchronized SSE event delivery, disconnect cleanup, route validation, readiness/
  safe metrics, newest-image transformation, tool/usage/error passthrough, and package
  behavior. The ordinary run passed 37 tests; five opt-in tests were skipped there and
  then all five passed in the separate required live invocation.

### Criterion D — documentation and configuration

- PASSED: example configuration, README, and adapter operations contract document the
  exact default/range, inclusive bound, 400 code, no-upstream guarantee, scanner string/
  escape semantics, and independence from the body byte limit.
- PASSED: experimental loopback scope, newest-image limitation, header/query/
  compression fidelity, no retries, gateway separation, rollback, and future-objective
  non-claims remain unchanged.

## Verification

- `uv lock --check`: PASSED — resolved 32 locked packages.
- `uv sync --frozen --extra dev`: PASSED — checked 31 installed packages.
- `uv run --frozen ruff check .`: PASSED.
- `uv run --frozen ruff format --check .`: PASSED — 44 files formatted.
- `uv run --frozen mypy src tests`: PASSED — 12 source files, no issues.
- `uv run --frozen pytest -q`: PASSED — 37 passed; five opt-in live tests SKIPPED in
  this ordinary invocation and then run separately below.
- `SLAIF_LIVE_TEST=1 uv run --frozen pytest -q tests/test_live.py`: PASSED — five
  passed in 6.40 seconds.
- `uv build`: PASSED — sdist and wheel built.
- `python3 -m compileall -q src tests oap/bin`: PASSED.
- `bash -n oap/bin/*.sh`: PASSED.
- `git diff --check bcdb3542a74a08219496ef29a09fd13b543e954c...HEAD`: PASSED at
  implementation head.
- Focused structural/config/image/app suite: PASSED — 37 tests.
- Tracked credential-name/raw-sentinel review and explicit response/log/metric
  assertions: PASSED — no real credential value or raw sentinel leaked.

## Live model/service evidence

- Candidate: foreground `127.0.0.1:18031`; all five ordered live tests passed; process
  stopped cleanly after tests and no 18031 listener remained.
- Upstream: authenticated private vision vLLM on the protected configured host/18020,
  model `qwen3.8-27b`; no credential value was printed or persisted.
- Sanitized matrix: local health/readiness, proxied health/models, Responses text,
  forced/automatic tools, streaming text/tools, multi-turn function output, one-image,
  two-image newest retention, metrics, and Chat calls returned expected HTTP 200 and
  safe envelope/event/count assertions.
- Before/after: `qwen-serving-vision.service` remained active/running at PID 4174 with
  start timestamp `Thu 2026-08-20 23:27:10 CEST`; only `10.8.132.76:18020` listened;
  18021 and 18031 were free at report drafting.
- Required before/after hashes matched: vision env
  `affabb5701b67b5fcb7cab2e3ae1835e84e19dc98a7f1eb245cf3e49b76b3b5b`, vision
  unit `fc88870b4f4afee214c25dc9ec544c4178c300bf4d78092a4d12787a955e2e94`, start
  script `8c87e0104b25c9600235a97555c4b0a1d0ea55d34ccb4094af428c8b4501f89f`, Qwen
  profile `18ead58ac440d29ce2e86addf855c24f471021c6050d4da685320a2cf6eb62eb`, coding
  overlay `cc243c7057f00cb15a06a5be63c6d811f8f473e367d521b1b6ea6207c794509a`, and OAP
  runtime env `22fdefd324d631353f1b9fedad3bad1fc75577073794a882ce2dd57bc5794bf1`.

## GitHub CI / required checks

- Implementation head `9f9739943bf6d763664970b553dd58fd96c481bd`: workflow `CI`, check
  `test`, SUCCESS in 21 seconds (Actions run 32433503856).
- All required checks green at drafting: YES.
- Report-head checks may be pending after publication; strategy verifies them.

## Local setup/dependencies

- Reused temporary `uv 0.12.5` under `/tmp/slaif-uv-tool.l3PWbo`; application/test
  dependencies remain in ignored repo-local `.venv` and committed `uv.lock`.
- Used only a foreground repo candidate. No service was installed/enabled and no sudo
  action was taken.
- No new dependency or lockfile change was required.

## Documentation

- Updated README, example configuration, and adapter configuration/operations contract
  with exact structural-bound behavior and interaction with the independent byte cap.
- Preserved all previously documented experimental, fidelity, safety, gateway,
  limitation, and rollback statements.

## Safety/scope confirmations

- Unrelated files preserved; no production/customer data used.
- Secrets/raw prompts/source/tool output/customer images committed, logged, or metric-
  labeled: NO.
- Protected 18020/Qwen/vLLM/Codex fixture changed: NO.
- Known mode-0777 vision environment file preserved byte-for-byte: YES; not remediated.
- Firewall, VPN, key files, systemd units/services, model/checkpoint/patches/Qwen venv,
  launch flags, network bindings, and Codex profiles changed: NO.
- Required tests skipped/not run: NONE after the separate live invocation.
- Scope deviation: NONE; no constitution/compiler/cache/gateway/cutover work.
- Extra objective PR: NO; coding merge: NO; auto-merge: NO.
- Active/order edited by coding: NO; report commit report-only: YES by publication
  procedure and remote verification.

## Known limitations/blockers

- The designated route intentionally retains only one image and cannot preserve
  explicit multi-image comparison semantics.
- MVP remains loopback-only and lacks later gateway signed identity/service auth,
  quotas, public TLS, constitution compiler/cache, and cutover work.
- The protected vision environment file remains mode 0777 pending separate authority.
- No blocker remains within order `000-c`.

## Recommended strategic follow-up

Independently verify the SELF parent/report-only commit, report-head CI, protected
fixture state, and objective acceptance. Decide any protected-file permission work
under a separate explicitly authorized order.

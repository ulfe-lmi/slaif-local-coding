# OAP Coding-Agent Report — 000-b

## Work order

- Identifier: `000-b`
- Order: `oap/orders/000-b-fix-proxy-bounds-fidelity-and-evidence.md`
- Numeric objective: `000`
- PR mode: `AMENDED_EXISTING_PR`

## Status

COMPLETE

## Executive summary

Repaired the reviewed objective-000 merge blockers on the existing PR. Request bodies
are now consumed incrementally with early and actual-byte bounds; query strings,
dynamic hop-by-hop filtering, compression metadata, and bounded error headers are
faithful; synchronized tests prove prompt SSE forwarding and disconnect cleanup.
Metrics now cover bounded local outcomes, response-header latency, total stream
duration, and readiness state. Duplicate model/endpoint routes fail settings
validation. The complete fake and authenticated live matrices passed. The foreground
candidate was stopped, and every protected fixture hash, process fact, and listener
remained unchanged.

## Authoritative GitHub state

- Repository: `ulfe-lmi/slaif-local-coding`
- PR: #1, `https://github.com/ulfe-lmi/slaif-local-coding/pull/1`, OPEN and non-draft
- Base/head: `main` / `oap/000-adapter-foundation`
- Starting remote SHA: `821be322a9b7500e73f545fe0c87c1e25d6c2f29`
- Implementation head SHA: cd17aaa919caea0e59e65536a3e754aa1df3f01a
- Report publication commit: SELF
- Implementation commits pushed before report: `cd17aaa919caea0e59e65536a3e754aa1df3f01a`
- New PR this round: NO; amended existing PR: YES; merge performed: NO

## Changes and files

- `src/slaif_local_coding/app.py`: incremental request-body reader; early
  `Content-Length` rejection plus actual-byte enforcement; query forwarding; request
  and response `Connection` token filtering; identity compression request with
  consistent raw encoded response forwarding; bounded `Retry-After` and encoding
  metadata; local result metrics; readiness gauge; explicit header and total-stream
  latency; cancellation-driven upstream close.
- `src/slaif_local_coding/config.py`: settings validation rejects duplicate
  `(model, endpoint)` route matches while allowing disjoint endpoint routes.
- `tests/test_app.py`, `tests/test_config.py`: direct multi-chunk ASGI body proof,
  exact limit/limit+1/missing/misleading length and malformed JSON cases, query and
  dynamic header fidelity, gzip stream/non-stream behavior, error metadata, safe
  labels, ready/not-ready metrics, synchronized first-chunk delivery, and
  post-delivery disconnect cleanup.
- `tests/test_live.py`: explicit local/proxied health checks, distinguishable synthetic
  images, and metric-delta proof of three images seen and one removed across the
  one-image and two-image calls.
- `README.md`, `docs/ADAPTER-CONFIGURATION.md`: exact body, query, header,
  compression, route-validation, readiness, and latency contracts.
- Committed the strategic-authored `oap/active` and `000-b` order bytes unchanged.

## Acceptance evidence

### Criterion A — bounded request consumption

- PASSED: a direct ASGI test delivered 40-byte and 25-byte chunks against a 64-byte
  cap, observed 413 after exactly two chunks, proved the remaining tail was not
  consumed, and proved zero upstream calls.
- PASSED: parameterized tests cover exact 43-byte limit (200), limit+1 (413), missing
  length, misleading length smaller than reality, known oversized length, and
  malformed JSON within the limit (400).

### Criterion B — HTTP fidelity

- PASSED: fake upstream asserts the complete opaque query bytes arrive unchanged;
  neither tests nor metrics expose query values.
- PASSED: request `Connection: x-remove-me, upgrade` strips both nominated headers;
  response `Connection: retry-after` strips the otherwise allowed nominated header.
- PASSED: caller authorization is replaced, caller `Accept-Encoding` becomes
  `identity`, internal headers remain stripped, and a standalone bounded
  `Retry-After` is preserved.
- PASSED: gzip tests for streaming and non-streaming responses prove safe
  `Content-Encoding: gzip` accompanies the raw encoded bytes (the downstream HTTPX
  test client decodes them to the asserted original body).
- PASSED: existing tools, usage, status, error body, authentication, and ordinary
  passthrough tests remain green.

### Criterion C — incremental stream and disconnect

- PASSED: synchronized direct ASGI proof blocks upstream after event one, observes
  exactly `data: one\n\n` downstream while the app task is incomplete, releases event
  two, verifies exact concatenated event order, and confirms upstream close.
- PASSED: disconnect proof waits until the first real downstream SSE chunk, then
  sends `http.disconnect` while upstream is indefinitely blocked and confirms the
  upstream byte stream closes promptly.

### Criterion D — observability

- PASSED: `slaif_requests_total` includes bounded endpoint/route/status/stream labels
  for upstream results and local 400/404/413/422/502/503 paths.
- PASSED: `slaif_response_header_duration_seconds` is explicitly time to a local
  outcome or upstream headers; `slaif_stream_duration_seconds` is total downstream
  stream lifetime through completion/disconnect.
- PASSED: `slaif_readiness_state` is exercised at ready `1` and not-ready `0`.
- PASSED: safe-metrics tests exclude raw body markers, malformed data, query values,
  credentials, and attacker-controlled paths; image/failure/disconnect counters are
  bounded enums/configured names only.

### Criterion E — startup route validation

- PASSED: duplicate routes matching the same model and endpoint raise settings
  validation; two same-model routes enabling disjoint Responses and Chat endpoints
  validate successfully. Existing unique-name, policy, and loopback checks remain.

### Criterion F — live evidence

- PASSED: five serial live tests explicitly exercised `/healthz`, `/readyz`, proxied
  `/health`, `/v1/models`, Responses text, forced and automatic tools, streaming text
  and tool events, multi-turn `function_call_output`, one image, and two images.
- PASSED: distinguishable synthetic image data URLs were used. Safe metric deltas
  after the one-image and two-image calls were exactly seen `3` and removed `1`.
  Deterministic pure tests remain the authority for newest identity/order.

## Verification

- `uv lock --check`: PASSED — resolved 32 locked packages.
- `uv sync --frozen --extra dev`: PASSED — checked 31 installed packages.
- `uv run --frozen ruff check .`: PASSED.
- `uv run --frozen ruff format --check .`: PASSED — 40 files formatted.
- `uv run --frozen mypy src tests`: PASSED — 10 source files, no issues.
- `uv run --frozen pytest -q`: PASSED — 24 passed; five opt-in live tests SKIPPED in
  this ordinary invocation and then run separately below.
- `SLAIF_LIVE_TEST=1 uv run --frozen pytest -q tests/test_live.py`: PASSED — five
  passed in 7.25 seconds.
- `uv build`: PASSED — sdist and wheel built.
- `python3 -m compileall -q src tests oap/bin`: PASSED.
- `bash -n oap/bin/*.sh`: PASSED.
- `git diff --check bcdb3542a74a08219496ef29a09fd13b543e954c...HEAD`: PASSED.
- tracked credential-pattern scan and raw-marker metric/log assertions: PASSED — no
  secret value or raw test marker exposed.

## Live model/service evidence

- Candidate: foreground `127.0.0.1:18031`; all ordered live assertions passed; process
  stopped cleanly after tests; no listener remained at report drafting.
- Upstream: authenticated private vision vLLM at the protected configured host/18020,
  model `qwen3.8-27b`; no credential value was printed or persisted.
- Sanitized statuses: local health/readiness, proxied health/models, text, forced/
  automatic/streaming tools, multi-turn, SSE completion, one-image, and two-image
  cases all returned HTTP 200 with expected safe envelope/event/count assertions.
- Before/after: `qwen-serving-vision.service` stayed active/running at PID 4174 with
  start timestamp `Thu 2026-08-20 23:27:10 CEST`; only `10.8.132.76:18020` listened;
  no 18021 or 18031 listener remained.
- All strategic protected hashes matched before and after: vision env
  `affabb5701b67b5fcb7cab2e3ae1835e84e19dc98a7f1eb245cf3e49b76b3b5b`, vision
  unit `fc88870b4f4afee214c25dc9ec544c4178c300bf4d78092a4d12787a955e2e94`, start
  script `8c87e0104b25c9600235a97555c4b0a1d0ea55d34ccb4094af428c8b4501f89f`, Qwen
  profile `18ead58ac440d29ce2e86addf855c24f471021c6050d4da685320a2cf6eb62eb`, coding
  overlay `cc243c7057f00cb15a06a5be63c6d811f8f473e367d521b1b6ea6207c794509a`, and OAP
  runtime env `22fdefd324d631353f1b9fedad3bad1fc75577073794a882ce2dd57bc5794bf1`.

## GitHub CI / required checks

- Implementation head `cd17aaa919caea0e59e65536a3e754aa1df3f01a`: workflow `CI`,
  check `test`, SUCCESS in 19 seconds (Actions run 32432780230).
- All required checks green at drafting: YES.
- Report-head checks may be pending after publication; strategy verifies them.

## Local setup/dependencies

- Installed temporary `uv 0.12.5` under `/tmp/slaif-uv-tool.l3PWbo`; application and
  test dependencies remain in ignored repo-local `.venv` and committed `uv.lock`.
- Used only a foreground repo candidate; no service was installed/enabled and no sudo
  action was taken.
- No new dependency or lockfile change was required.

## Documentation

- Updated README and adapter configuration/operations documentation to state the
  actual hard body bound, query/header/compression policy, startup uniqueness rule,
  safe readiness metric, and distinct header/total-stream latency semantics.
- Preserved newest-image limitation, no-retry policy, gateway separation,
  loopback-only operation, rollback, and experimental scope.

## Safety/scope confirmations

- Unrelated files preserved; no production/customer data used.
- Secrets/raw prompts/source/tool output/customer images committed, logged, or metric-
  labeled: NO.
- Protected 18020/Qwen/vLLM/Codex fixture changed: NO.
- Known mode-0777 vision environment risk preserved byte-for-byte: YES; not remediated.
- Firewall, VPN, key files, systemd units/services, model/checkpoint/patches/Qwen venv,
  launch flags, and Codex profiles changed: NO.
- Required tests skipped/not run: NONE after the separate live invocation.
- Scope deviation: NONE; no constitution/compiler/cache/gateway or cutover work.
- Extra objective PR: NO; coding merge: NO; auto-merge: NO.
- Active/order edited by coding: NO; report commit report-only: YES by publication
  procedure and remote verification.

## Known limitations/blockers

- The designated route intentionally retains only one image and cannot preserve
  explicit multi-image comparison semantics.
- MVP remains loopback-only and lacks later gateway signed identity/service-auth,
  quotas, and public TLS.
- The protected vision environment file remains mode 0777 pending separate authority.
- No blocker remains within order `000-b`.

## Recommended strategic follow-up

Independently verify the SELF parent/report-only commit, report-head CI, protected
fixture state, and objective acceptance. Decide any protected-file permission work
under a separate explicitly authorized order.

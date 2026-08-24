# OAP Coding-Agent Report — 004-w

## Work order

- Identifier: `004-w`; order path: `oap/orders/004-w-security-observability-hardening-review.md`; numeric objective: `004`.
- PR mode: `AMENDED_EXISTING_PR`.

## Status

COMPLETE

## Executive summary

Completed the bounded production security/privacy/observability review of the
adapter, constitutional pipeline, compiler/cache, configuration, and streaming
proxy. Fixed concrete header, error-sanitization, timeout, response-bound,
configuration, cache-integrity, and rehydration-budget defects; added negative
regression evidence; updated operational documentation. No gateway, model,
vision, compaction, sandbox, systemd, profile, or protected-host mutation was
performed.

## Authoritative GitHub state

- Repository: `ulfe-lmi/slaif-local-coding`; PR: [#6](https://github.com/ulfe-lmi/slaif-local-coding/pull/6); state: OPEN, non-draft, MERGEABLE.
- Base/head: `main` / `oap/004-real-codex-governed-e2e`.
- Starting remote SHA: `894c730e6d22371ed7f8d087769c0237871ee085`.
- Implementation head SHA: `36a2bdbaccdcfd8eb28e2a5e2deaafedda1d1c7a`.
- Report publication commit: SELF.
- Implementation commits pushed before report: `36a2bdbaccdcfd8eb28e2a5e2deaafedda1d1c7a` (`OAP 004-w: harden security and observability boundaries`).
- New PR this round: no; amended existing: yes; merge performed: NO.

## Changes and files

- `src/slaif_local_coding/app.py`: strips cookies, forwarding headers, and
  internal header families; sanitizes upstream error bodies; bounds buffered
  upstream responses; honors metrics enablement; reports fixed readiness
  component states; handles malformed transformed JSON safely.
- `src/slaif_local_coding/config.py` and `config/adapter.example.toml`: strict
  observability configuration, bounded response/time/cache/model settings,
  credential-free upstream URL validation, normalized cache paths, and
  consistent image-policy limits.
- `src/slaif_local_coding/cli.py`: disables default Uvicorn access logging.
- `constitution/compiler.py`, `compiler_models.py`, `cache.py`, and
  `pipeline.py`: direct compiler timeout/auth failure handling, cache-key and
  restart-integrity checks, deterministic restart ordering, safe cache purge,
  and preservation of valid rehydration entries under oversized insertion.
- `README.md`, `TESTING.md`, and `docs/ADAPTER-CONFIGURATION.md`: synchronized
  security, error, body-limit, readiness, and operational claims.
- `tests/test_app.py`, `test_cache.py`, `test_compiler.py`, `test_config.py`,
  `test_pipeline.py`, and `test_rehydration.py`: negative regression and
  observability evidence.
- Activated `oap/active` and the exact strategic order were committed byte-for-
  byte as the orchestration transcript; their content was not edited by coding.

## Acceptance evidence

### Criterion 1 — Complete fixed findings matrix

The following matrix covers every A-D review item. `PASS` means the existing
contract and evidence were sufficient; `DEFECT_FIXED` records a concrete defect
fixed in this round.

| Item | Result | Concrete evidence and strongest remaining risk |
|---|---|---|
| A1 principal/session/route/request-ID/compiler-bypass spoofing | DEFECT_FIXED | Header-family stripping and generated request ID in `app.py`; header spoof test passes. No caller identity is used for cache identity. |
| A2 service auth and raw external key handling | DEFECT_FIXED | Caller auth/cookies are stripped; service auth is installed internally; compiler uses its configured service credential only. Runtime metrics/error tests contain no credential material. |
| A3 hop-by-hop and `Connection`-named headers | PASS | Request deny set plus dynamic `Connection` tokens and response allowlist; existing bilateral header tests pass. |
| A4 query/private URL/auth/cookie telemetry | DEFECT_FIXED | Cookie/forwarding-header removal, fixed metric labels, disabled Uvicorn access log, and query-preservation/no-label tests pass. |
| A5 unknown route/policy/capability | DEFECT_FIXED | Strict route/policy validation, unique model/endpoint matching, and sanitized 422 unknown-route behavior; configuration tests pass. |
| B1 raw content in logs/persistence/diagnostics | PASS | No production raw-payload logging; synthetic canary absence from logs, metrics, and errors; wheel contains runtime code only. Remaining risk is deployment-level logging outside this process. |
| B2 raw-source/cache ownership, symlink, traversal, deletion | DEFECT_FIXED | Absolute cache paths, canonical key validation, private modes/owners, symlink rejection, restart integrity validation, bounded inventory, and cache tests pass. Cache remains disposable. |
| B3 malformed/oversized/deep JSON and image shapes | DEFECT_FIXED | Fixed invalid-JSON/depth/size responses, bounded non-stream responses, and route-consistent image policies; app/image/config tests pass. |
| B4 upstream/validation/compiler/cache error sanitization | DEFECT_FIXED | Upstream HTTP error bodies are replaced by a fixed envelope; compiler auth/timeouts and cache failures return typed safe outcomes; canary tests pass. |
| C1 direct compiler isolation and bounds | DEFECT_FIXED | Direct text-only request has no tools/images, one global slot, explicit `wait_for` timeout, bounded source/prompt/output/depth, and no public recursion; compiler tests pass. |
| C2 invalid compiler result and governance fallback | PASS | Strict schema/candidate validation and no-cache-on-failure preserve the original governance-bearing request; existing pipeline/compiler tests pass. |
| C3 deterministic candidate preservation | PASS | Candidate-set equality remains mandatory in compiler validation; existing observation/compiler tests pass. |
| C4 cache/rehydration identity isolation | PASS | Existing identity/version/source/bound dimensions and cross-session tests pass; no caller header identity is accepted. |
| C5 missing identity behavior | PASS | Missing reliable session/repository identity disables persistent reuse; existing compiler test passes. |
| C6 TTL/LRU/bytes/pinned/integrity/permissions/restart bounds | DEFECT_FIXED | Startup payload-integrity validation, deterministic equal-mtime ordering, canonical key check, safe purge, and no-eviction oversized rehydration regression pass. |
| D1 streaming fidelity and no full SSE buffering | PASS | Incremental `aiter_raw` path, event-order/usage/tool coverage, safe status handling, and existing SSE tests pass. |
| D2 disconnect cancellation and closure | PASS | ASGI disconnect test observes upstream closure; cancellation is re-raised after cleanup. |
| D3 timeouts/backpressure/body/JSON/compiler saturation | DEFECT_FIXED | Proxy connect/read/write/pool settings are bounded; compiler timeout is enforced independently; request JSON and buffered response caps are explicit; streaming remains incremental under timeout/backpressure. |
| D4 duplicate model/process, torch/image decode, retry/thread hazards | PASS | Runtime static scan finds no model loading, image decode, process/thread/retry implementation; compiler concurrency is one. |
| D5 fixed low-cardinality metrics and private endpoint | DEFECT_FIXED | Strict observability config, optional metrics endpoint, fixed labels, safe readiness component gauges, and canary scans pass. Loopback deployment remains required for privacy. |
| D6 health/readiness/config/cache/upstream distinction | DEFECT_FIXED | `/healthz` remains process health; `/readyz` reports fixed valid-config, upstream, compiler, and cache states; cache degradation is explicit without exposing internals. |

### Criterion 2 — Defects and negative coverage

All discovered in-scope defects above were fixed with focused regression tests.
No known critical/high defect was silently deferred. Full and focused gates
passed; intentional live/E2E limitations are recorded below.

### Criterion 3 — Secret/raw/private-path scans

Static sensitive-logging, runtime-boundary, and synthetic-canary source scans
passed. Existing runtime tests verify canaries do not appear in captured logs,
metrics, sanitized errors, or derived cache files. No canary values are
included in this report.

### Criterion 4 — Negative security/resource tests

Header spoofing/cookies, upstream error bodies, response bounds, metrics
disablement, strict configuration, cache-key traversal/integrity, compiler
timeout/auth, readiness degradation, disconnect cleanup, identity isolation,
and oversized rehydration insertion all have passing evidence.

### Criterion 5 — Packaging and dependencies

The built wheel contains only `slaif_local_coding` runtime modules and metadata;
no `tests/` or E2E helper files are present. The source distribution retains
repository test support as non-runtime content. `uv.lock` and project
dependencies were unchanged.

### Criterion 6 — Documentation and limitations

Configuration, testing, README, and adapter-operation documentation match the
implemented security/error/readiness behavior. Text-only model capability,
repository-only global-yolo E2E, unproven actual compaction, unproven live
vision, and uninstalled systemd-candidate limitations remain explicit.

### Criterion 7 — Protected state and CI

Protected-host before/after snapshots match. GitHub required check `test` is
SUCCESS for implementation head `36a2bdbaccdcfd8eb28e2a5e2deaafedda1d1c7a`.

## Verification

- `uv lock --check`: PASSED — lock is consistent.
- `uv sync --frozen --extra dev`: PASSED — 31 packages checked.
- `uv run ruff check .`: PASSED.
- `uv run ruff format --check .`: PASSED.
- `uv run mypy src tests`: PASSED — 37 source files.
- `uv run pytest -q tests/test_app.py tests/test_cache.py tests/test_compiler.py tests/test_config.py tests/test_pipeline.py tests/test_rehydration.py`: PASSED — 98 passed.
- `uv run pytest -q`: PASSED — 304 passed, 7 skipped; skipped tests are not claimed as pass.
- `uv run pytest -q tests/test_live.py`: SKIPPED — 7 live tests; candidate live matrix was not required by this order and no candidate adapter was started.
- `uv build`: PASSED — wheel and sdist built.
- Wheel inspection for runtime-only contents: PASSED — no `tests/` or `helpers/` paths in wheel.
- `uv run python -m compileall -q src tests`: PASSED.
- `bash -n oap/bin/*.sh`: PASSED.
- `git diff --check`: PASSED.
- Static sensitive-logging/runtime-boundary/synthetic-canary scans: PASSED.
- Focused header/auth/cache-identity/recursion/bounds/cancellation evidence: PASSED through focused and full suites.
- Dependency/scoped-diff audit: PASSED — no dependency or `uv.lock` change; only listed implementation/docs/tests/OAP transcript files changed.

## Live model/service evidence

- Read-only protected upstream checks on private port `18020`: `/health` returned
  HTTP 200; `/v1/models` returned one served model, `qwen3.8-27b`.
- Live model metadata exposed no capability declaration. The active launcher was
  observed to use `--language-model-only`; this is text-only evidence, not a
  vision-capability claim. The current service, model, port, launcher, systemd
  unit, and Codex profile were not changed.
- Before/after service state remained active/running with the same protected
  listener; no candidate adapter was bound on `18031`.
- No live text/tool/stream/disconnect candidate smoke was needed; it is NOT RUN,
  while fake-upstream coverage is the primary evidence for this order.

## GitHub CI / required checks

- Implementation head `36a2bdbaccdcfd8eb28e2a5e2deaafedda1d1c7a`: `test` SUCCESS
  (GitHub Actions CI).
- All required checks at implementation-head drafting: yes.
- Report-head checks may be pending immediately after publication; they are
  independently verified before the response FIFO signal.

## Local setup/dependencies

Used the repository `.venv` via frozen `uv` sync. No new packages, lockfile,
sudo action, service, temporary candidate, or external runtime was installed.

## Documentation

Updated: `README.md`, `TESTING.md`, `docs/ADAPTER-CONFIGURATION.md`, and
`config/adapter.example.toml` for strict observability, safe errors, body
limits, header privacy, and readiness states. No security certification or
production-equivalence claim was added.

## Safety/scope confirmations

- Unrelated human/strategic work: preserved; no unrelated file was staged.
- Secrets/raw prompts/source/images/tool output/customer data: not printed,
  logged, cached as raw data, or included in this report.
- Protected `18020`/Qwen/Codex fixture changed: NO.
- Required tests skipped/not run: live candidate matrix and actual vision,
  compaction, sandbox, and Codex profile tests; all are order non-goals or
  explicitly not required here.
- Scope deviation: none.
- Extra objective PR: NO; coding merge/auto-merge: NO.
- Active/order edited by coding: NO; activated bytes were committed unchanged.
- Report commit report-only: yes; it will contain only this report path.

## Known limitations/blockers

No blocker remains for this order. Actual Codex compaction, live vision-capable
E2E, and systemd candidate proof remain unverified by design. Streaming is
incremental with backpressure/read timeouts rather than a total-response byte
cap; non-streaming responses have the explicit configured cap. The protected
current model service is text-only and remains outside this round's scope.

## Recommended strategic follow-up

Review and accept/reject this evidence on PR #6. Keep objective-004 and branch
percentages unchanged as ordered; future compaction, vision, and systemd work
requires separate explicit OAP orders.

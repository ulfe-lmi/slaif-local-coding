# OAP Coding-Agent Report — 002-a

## Work order
- Identifier: `002-a`
- Order path: `oap/orders/002-a-constitutional-compiler-cache.md`
- Numeric objective: `002`
- PR mode: CREATED_NEW_PR

## Status
PARTIAL

Objective 002's compiler/cache implementation and local/CI gates are complete. Live
compiler/cache and ordinary adapter behavior passed, but the bounded live image case
was skipped because the current model endpoint declared zero-image capability. The
required vision/two-image service evidence therefore remains missing; protected
service state was not changed.

## Executive summary
Implemented a library-only constitutional compiler, strict validated index contract,
direct bounded upstream scheduling, and an isolated disposable filesystem cache.
Public handlers still make zero compiler calls. Reconciled current loopback migration
documentation/configuration while preserving historical provenance. All requested local
commands passed; the opt-in live suite passed 5 tests and truthfully skipped the image
capability test. PR #3 is open and unmerged.

## Authoritative GitHub state
- Repository: `ulfe-lmi/slaif-local-coding`
- PR number/URL/state: #3, https://github.com/ulfe-lmi/slaif-local-coding/pull/3, OPEN
- Base/head: `main` / `oap/002-constitutional-compiler-cache`
- Starting remote SHA: `176bf4d839ae9fa32d0cc3c4279a1b96220c1c61`
- Implementation head SHA: `62463f1818b33237c1e3992afb00b24dcd8b9575`
- Report publication commit: SELF
- Implementation commits pushed before report: `62463f1818b33237c1e3992afb00b24dcd8b9575`
- New PR this round: yes
- Amended existing PR: no
- Merge performed: NO

## Changes and files
- Added `constitution/compiler_models.py`: strict typed success/failure contracts,
  independent reference confidence and constitutional priority, classes/evidence/
  urgency/reread fields, and safe metrics shapes.
- Added `constitution/compiler.py`: direct text-only `/v1/chat/completions` calls,
  bounded inputs/output/time/attempts, one-slot scheduling, identical-miss deduplication,
  strict JSON/index validation, candidate-set preservation, cancellation handling, and
  bounded safe metrics.
- Added `constitution/cache.py`: content-integrity envelopes, versioned identity keys,
  atomic private filesystem writes, TTL/LRU and byte limits, isolated pinned budget,
  corruption/permission/expiry misses, degraded fallback, and scoped purge/reconstruction.
- Extended configuration validation while keeping public compiler/injection integration
  false-only; updated exports and focused fake-upstream/live tests.
- Updated README, architecture documents, example TOML, and live-environment documentation;
  changed current operational examples to loopback and distinguished optional LAN versus
  historical provenance without changing the reference proxy or merged OAP history.
- Added public-handler regression proving a governed request invokes the compiler zero times.

## Acceptance evidence
### Criterion A — strict compiler success contract
- PASSED — Fake-upstream success preserved exact source hash/length/path, candidate path
  exactly once, separate scores/class/evidence/urgency and required governance fields.
  Bounded live compilation returned a valid two-rule index with one dependency.

### Criterion B — validation fails closed
- PASSED — Compiler/cache focused suite (`32 passed`) covers malformed/truncated/oversized/deep
  output, missing/extra/wrong fields and enums/ranges/types, hash mismatch, omitted/invented/
  duplicate candidates, forbidden combined score, contradictory ranking, and invalid UTF-8.
  Invalid outputs made no valid cache entry.

### Criterion C — direct bounded scheduling
- PASSED — Tests prove direct configured URL, no self-call/tools/images, one slot,
  deduplicated identical miss, attempt budget, timeout/status/transport typed failures,
  cancellation slot release, and sanitized metrics.

### Criterion D — cache isolation and disposal
- PASSED — Cache suite proves modes/atomicity/integrity/hit; principal/route/session/repository/
  source/model/schema/compiler/policy/bound isolation; TTL/corruption/permission misses;
  per-entry/total/LRU/pinned budgets; fallback; privacy; purge/reconstruction; and no reuse
  without reliable session/repository identity.

### Criterion E — public adapter unchanged
- PASSED — Existing fake-upstream proxy/SSE/tool/error/disconnect/image/observation tests
  remained green. New regression observed zero compiler invocations for a governed request.

### Criterion F — bounded live proof
- PARTIAL — Live compiler/cache passed: first call was `miss-persisted`, repeat was `hit`,
  with synthetic source/prompt data only. Live suite passed health/model/text/tool/multiturn/
  SSE cases. One-image request reached the route policy but upstream returned HTTP 400 and
  declared capacity for zero images, so the live vision/two-image assertion was SKIPPED;
  corresponding service evidence is missing.

### Criterion G — migration reconciliation
- PASSED — Current example/tests use preferred loopback; docs distinguish `hinton1`, optional
  LAN `.75`, and historical `.76`. Audit found the historical value retained once in the
  reference prototype and once as explicitly historical compact-architecture prose.

### Criterion H — quality gates and provenance
- PENDING at report drafting — Every named local gate passed and implementation-head GitHub
  check was SUCCESS. The report-only SELF commit did not exist yet, so its required check was
  necessarily pending. No post-publication report mutation was permitted.

## Verification
- `uv lock --check`: PASSED
- `uv sync --frozen --extra dev`: PASSED
- `uv run --frozen ruff check .`: PASSED
- `uv run --frozen ruff format --check .`: PASSED
- `uv run --frozen mypy src tests`: PASSED — 25 source files
- `uv run --frozen pytest -q`: PASSED — 193 passed, 6 skipped (opt-in live tests)
- `SLAIF_LIVE_TEST=1 uv run --frozen pytest -q tests/test_live.py`: PASSED — 5 passed,
  1 explicitly skipped for live zero-image capability
- `uv build`: PASSED — sdist and wheel
- `python3 -m compileall -q src tests oap/bin`: PASSED
- `bash -n oap/bin/*.sh`: PASSED
- `git diff --check 176bf4d839ae9fa32d0cc3c4279a1b96220c1c61...HEAD`: PASSED
- Focused compiler/cache suite: PASSED — 32 tests
- Public-handler zero-compiler regression: PASSED — 1 test
- Secret/raw-content scan across 18 changed/new paths plus runtime cache roots: PASSED —
  no credential/private-key/token findings; no runtime cache files present
- Scoped stale-endpoint audit: PASSED — current loopback present; optional LAN/historical
  labels documented separately; reference provenance unchanged

## Live model/service evidence
- Host/user: `hinton1` / `janezp`; protected Qwen path existed read-only.
- Before: UTC `2026-08-22T05:01:12Z`; port 18020 listener owned by vLLM PID `26028`;
  `qwen-serving.service` active with PID `26028`; vision unit inactive; ports 18021/18031 free.
- Upstream authenticated health/models: HTTP 200 before and after; exactly one model ID
  `qwen3.8-27b`.
- Temporary foreground adapter PID `48649` bound only loopback port 18031 for the live suite,
  then was stopped; after-check showed port 18031 free. Port 18021 remained free.
- After: UTC `2026-08-22T05:43:34Z`; same vLLM PID/unit state; no protected fixture change.
- Compiler proof used preferred same-host loopback, model `qwen3.8-27b`, one synthetic
  137-byte source, one deterministic candidate, about 1941 prompt bytes, timeout 120s, and
  3000-token cap. First validated miss persisted about 1439 derived-index bytes; second
  explicit-identity call hit; elapsed about 19.29 seconds. No raw source/prompt/output was
  persisted.
- Image probe received sanitized HTTP 400/BadRequestError indicating at most zero images;
  no reconfiguration or restart was attempted.

## GitHub CI / required checks
- Implementation head `62463f1818b33237c1e3992afb00b24dcd8b9575`:
  - `test`: SUCCESS
- All required checks green at implementation-head drafting: yes
- Final report-head checks: PENDING when this immutable report was drafted; strategy must
  independently wait/verify them.

## Local setup/dependencies
- Used existing locked Python 3.12/uv environment and dev extras; no dependency lock change.
- Built package artifacts locally through `uv build`; artifacts were not committed.
- Started/stopped only the temporary repository-owned adapter on 18031. No sudo action and no
  persistent service was installed.

## Documentation
- Updated `README.md`, `ARCHITECTURE.md`, `ARCHITECTURE-for-agents.md`,
  `config/adapter.example.toml`, and `docs/LIVE-TEST-ENVIRONMENT.md`.
- Documented compiler/cache bounds, identity requirements, failure/privacy behavior, current/
  LAN/historical endpoints, and explicit objective-002 exclusions.

## Safety/scope confirmations
- Unrelated/pre-existing human work altered: NO
- Secrets/raw prompts/source/images/tool output/response bodies/customer content committed:
  NO
- Production systems/data used: NO
- Protected 18020/Qwen/Codex fixture changed: NO
- Required tests skipped/not run: live image/two-image test SKIPPED because current upstream
  declares zero-image capability; report-head CI PENDING at publication.
- Scope deviation: NO
- Extra objective PR: NO
- Coding merge/auto-merge: NO
- Active/order bytes edited beyond committing activated transcript: NO
- Final commit changes only report: yes

## Known limitations/blockers
- Current endpoint advertises `qwen3.8-27b` but rejects image items with zero-image capacity,
  so vision/two-image adapter behavior lacks new live evidence despite prior order-state
  records describing vision mode.
- Objective 002 deliberately excludes request injection, acquisition, rehydration, signed
  multi-user production identity, gateway integration, cutover, and compiler/cache endpoints.
- Persistent cache reuse intentionally requires both reliable session and repository
  discriminators; otherwise calls remain request-scoped/disabled.

## Recommended strategic follow-up
Factual only: decide whether to obtain corrected live vision-service reconnaissance/order,
continue objective 002 despite the skipped image matrix, or require a remediation slice.
Strategy also owns review of report-head CI and any continuation decision.

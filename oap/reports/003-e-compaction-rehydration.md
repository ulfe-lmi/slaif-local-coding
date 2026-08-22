# OAP Coding-Agent Report — 003-e

## Work order
- Identifier: `003-e`
- Order path: `oap/orders/003-e-compaction-rehydration.md`
- Numeric objective: `003`
- PR mode: `AMENDED_EXISTING_PR`

## Status
COMPLETE

## Executive summary
Objective-003 process-local compaction/new-context rehydration was implemented on PR #5. After a successfully injected governed request, the pipeline stores validated root/dependency indexes and inclusion metadata under a complete static identity/model/source/version/policy/bound key. A later zero-root request reconstructs through the selector and endpoint-specific idempotent injector without a compiler call. TTL, LRU, per-entry-byte, total-byte, corruption, restart, isolation, replacement, conflict, Responses/Chat, and proxy-preservation behaviors are covered by focused fake-upstream tests. Bounded live testing proved the zero-root compiler-call count stayed unchanged and governance injection remained present. Documentation now distinguishes this adapter-boundary simulation from real Codex E2E, which remains objective 004.

## Authoritative GitHub state
- Repository: `ulfe-lmi/slaif-local-coding`
- PR number/URL/state: #5, https://github.com/ulfe-lmi/slaif-local-coding/pull/5, OPEN
- Base/head: `main` / `oap/003-working-set-injection-foundation`
- Starting remote SHA: `dbc8f4947e510bbdc41729a8746ecf3691844e99`
- Implementation head SHA: `2b8824afbe3f64d9c40afe00ec2515748eac195a`
- Report publication commit: SELF
- Implementation commits pushed before report: `2b8824afbe3f64d9c40afe00ec2515748eac195a` — “OAP 003-e: add bounded compaction rehydration”
- New PR this round: NO
- Amended existing PR: YES
- Merge performed: NO

## Changes and files
- Added bounded process-local rehydration state, complete-key matching, validation, occupancy accounting, and post-injection population in `src/slaif_local_coding/constitution/pipeline.py`.
- Added finite `[constitution.rehydration]` settings and cross-entry budget validation in `src/slaif_local_coding/config.py`.
- Passed the selected model into pipeline processing in `src/slaif_local_coding/app.py`.
- Added focused coverage in `tests/test_rehydration.py`; expanded configuration and live coverage in `tests/test_config.py` and `tests/test_live.py`.
- Documented behavior, limits, privacy properties, and objective-004 boundary in `README.md`, `docs/ADAPTER-CONFIGURATION.md`, and `ARCHITECTURE.md`; documented example settings in `config/adapter.example.toml`.
- Updated `oap/COMPLETENESS.md` to record objective 003 at 100% and branch readiness at approximately 74%, while reserving real Codex evidence for objective 004.
- Committed the immutable activated order and changed only `oap/active` from `003-d` to `003-e`.

## Acceptance evidence
### Criterion 1 — populate only after successful injection
- Result: COMPLETE. `_process_observed_root` invokes `_store_rehydration` only after selection/injection succeeds and deterministic serialization completes. `test_root_populates_then_zero_root_rehydrates_without_compiler` verifies populated state after an injected outcome.

### Criterion 2 — zero-root stable injection with zero compiler calls
- Result: COMPLETE. The fake-upstream test compares the observed-root and zero-root instruction bytes and asserts one total compiler call. The live pipeline case captures compiler attempts between the second and third requests and asserts a delta of exactly zero while the third response remains injected.

### Criterion 3 — no cross-hit across differing static dimensions
- Result: COMPLETE. `RehydrationKey` includes principal/route/session/repository, model, root path/hash, index/compiler/prompt versions and bounds, observation policy/version/bounds, selector/render policy/version, and working-set/injection bounds. `test_changed_static_identity_does_not_cross_hit` proves session isolation and restoration; `test_rehydration_key_matches_every_static_dimension` checks every string and numeric dimension changes equality.

### Criterion 4 — expiry, pressure, invalid state, and restart are safe misses
- Result: COMPLETE. Focused tests cover TTL expiry, corrupt/invalid type, oversized/mismatched metadata treated as corrupt, process restart, and total-byte/LRU eviction of the oldest entry. Preservation remains byte-safe and governance is never deleted from the original request.

### Criterion 5 — replacement, ambiguous roots, disabled, and spoofed headers
- Result: COMPLETE. A same-process new-root test replaces the prior working set and uses it for subsequent zero-root injection. Multiple/incomplete roots retain the prior preservation behavior. Existing disabled/spoofed-header passthrough tests remain green.

### Criterion 6 — endpoint idempotence and proxy preservation
- Result: COMPLETE. New Chat coverage proves identical system content on repeated zero-root requests. Existing Responses/Chat marker-conflict, SSE, image-policy, tools, disconnect, error, and header-filtering suites remain green. Zero-root conflicting markers fail closed when valid state exists.

### Criterion 7 — safe bounded observability
- Result: COMPLETE. Rehydration metrics expose fixed endpoint/route/state/reason labels plus entry/byte gauges; they do not include paths, hashes, source, prompts, identities, images, or raw payloads. Focused metrics assertions and secret/raw-content scans found no leakage.

### Criterion 8 — honest documentation and completeness
- Result: COMPLETE. README, configuration operations, architecture, and completeness documentation explicitly identify this as simulated/new-context rehydration, preserve text-only/no-production limits, and move actual Codex long-session/compaction/vision evidence to objective 004.

## Verification
- `uv lock --check`: PASSED — resolved 32 packages, exit 0.
- `uv sync --frozen --extra dev`: PASSED — checked 31 packages, exit 0.
- `uv run --frozen ruff check .`: PASSED — exit 0.
- `uv run --frozen ruff format --check .`: PASSED — 95 files already formatted, exit 0.
- `uv run --frozen mypy src tests`: PASSED — no issues found in 33 source files.
- `uv run --frozen pytest -q`: PASSED — 248 passed, 7 skipped (opt-in live tests) in final local run.
- `SLAIF_LIVE_TEST=1 uv run --frozen pytest -q tests/test_live.py`: PASSED — 6 passed, 1 skipped against temporary loopback adapter.
- `uv build`: PASSED — built source distribution and wheel.
- `python3 -m compileall -q src tests oap/bin`: PASSED — exit 0.
- `bash -n oap/bin/*.sh`: PASSED — exit 0.
- `git diff --check 68f212b5ad316b95fa12ef632e1538b56479081b...HEAD`: PASSED — no whitespace errors after implementation commit.
- Secret/raw scan (`git diff 68f… -- . ':(exclude)tests/*' | grep …`): PASSED — no high-risk credential/private-key pattern or synthetic fixture token outside intentional tests.
- Scoped diff audit: PASSED — implementation commit changed exactly the 13 intended paths listed above; final SELF commit changes only this report.
- Completeness check: PASSED — objective 003 = 100%, branch readiness = ~74%, objective-004 limitation retained.

## Live model/service evidence
- Endpoint/route without secrets: private authenticated upstream `/health` and `/v1/*`; temporary candidate bound only to `127.0.0.1:18031`. Synthetic static labels were used for principal/session/repository; no secrets or private URLs were recorded.
- Final bounded suite result: HTTP live matrix completed once in 79.52 seconds as `6 passed, 1 skipped`. The image case was `SKIPPED` because the verified current fixture is zero-image/text-only.
- Enabled pipeline/rehydration portion made three bounded Responses calls. The first synthetic root compiled; the repeated root used persistent cache; the compacted/zero-root request had compiler-attempt delta exactly zero, emitted a rehydration hit, and remained injected. Temporary adapter logs were 1608 bytes and contained no request/response payload.
- Two pre-service setup attempts failed safely on generated TOML/settings validation before any upstream model call; the generator was corrected, and the final suite passed. No protected service state was altered.
- Protected fixture before snapshot: PID `26028`, listening `0.0.0.0:18020`; user-unit SHA-256 `64b3ccd5bdb64da4e3dcabca660fada8155583c96b6bc11de47536e595df5910`. After snapshot found the same PID/listen address and unit hash. Development port 18031 was free afterward.
- No model, vLLM, systemd, API-key file, firewall, VPN, network binding, or active Codex profile was changed.

## GitHub CI / required checks
- Implementation-head state: `2b8824afbe3f64d9c40afe00ec2515748eac195a`
- Check `CI / test`: SUCCESS — run `32586833908`, job `97064383859`.
- All required green at drafting: YES for implementation head.
- Report-head checks may be pending/newly triggered and are not claimed green; strategy independently verifies the final SELF commit.

## Local setup / dependencies
- Used repository-local Python 3.12 via locked `uv sync --frozen --extra dev`; dependency lock did not change.
- Created temporary `/tmp` configuration/cache/log state for the loopback adapter and removed it after testing. Upstream authentication was read from the running protected process environment only into the temporary adapter environment and was never printed or persisted.
- Started/stopped only the repo-owned temporary adapter on port 18031. No sudo action was required.

## Documentation
- Updated `README.md`, `docs/ADAPTER-CONFIGURATION.md`, `ARCHITECTURE.md`, and `config/adapter.example.toml` for rehydration semantics, bounds, process-restart behavior, privacy, metrics, and explicit non-goals.
- Updated `oap/COMPLETENESS.md` exactly within ordered completion/readiness scope.
- Committed the exact strategic order bytes and advanced only `oap/active` to `003-e`.

## Safety / scope confirmations
- Unrelated files changed: NO.
- Secrets/raw customer content exposed: NO.
- Production systems/data accessed: NO.
- Protected resources changed: NO.
- Port 18020/Qwen/Codex fixture changed: NO.
- Required tests skipped/not run: none. The normal suite's seven opt-in live tests were run explicitly; the live image case honestly skipped for the verified zero-image fixture.
- Scope deviation: NO.
- Extra objective PR created: NO.
- Coding-agent merge/auto-merge performed: NO.
- Activated order edited: NO; exact strategic draft bytes were compared and committed.
- Report commit changes only this report: YES.

## Known limitations / blockers
- Rehydration state is process-local and intentionally lost on restart; there is no persistent or cross-process/session database.
- Static configured local-appliance identity remains MVP-only and does not implement signed gateway multi-user identity.
- This validates adapter-boundary simulated/new-context requests, not real Codex compaction execution.
- Current protected fixture remains text-only/zero-image; no vision, production, gateway, or cutover readiness is claimed.

## Recommended strategic follow-up
- Independently verify report-head CI and review PR #5.
- If accepted, schedule objective 004 for disposable real-Codex E2E, including actual long-session/compaction evidence and security/operations hardening.
- Treat vision capability claims as unavailable until a separately ordered, rollback-aware fixture/cutover change provides a verified vision-capable service.

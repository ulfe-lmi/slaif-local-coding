# OAP Coding-Agent Report — 002-b

## Work order
- Identifier: `002-b`; order path:
  `oap/orders/002-b-harden-cache-and-reconcile-capability.md`; numeric objective: `002`
- PR mode: `AMENDED_EXISTING_PR`

## Status
COMPLETE

## Executive summary
Amended PR #3 only. The derived cache now rejects symlinked, foreign-owned,
wrong-type, and wrong-mode roots/shards/entries, uses a protected user-cache
fallback safely, bounds and reconciles startup state, and includes every
required deterministic compiler bound in its persistent identity. Configuration
now exposes the new finite bounds. Current operational and architecture
documentation now records the verified text-only/zero-image `hinton1` service
while preserving historical vision provenance. Required static, fake-upstream,
packaging, focused live compiler/cache, and current text/tool/stream/multiturn
gates passed; the current live image case was skipped because the protected
service accepts zero images.

## Authoritative GitHub state
- Repository: `ulfe-lmi/slaif-local-coding`
- PR: #3, `https://github.com/ulfe-lmi/slaif-local-coding/pull/3`, OPEN, non-draft
- Base/head: `main` / `oap/002-constitutional-compiler-cache`
- Verified base SHA: `176bf4d839ae9fa32d0cc3c4279a1b96220c1c61`
- Starting remote SHA / `002-a` report SELF:
  `fe936c1bc706207f5c3fb81d6a08d1d1a228fbc9`
- Implementation head SHA: `9192dea62dccdb76801733b958a8bfd5e3f3c63c`
- Report publication commit: SELF
- Implementation commit pushed before report: `9192dea62dccdb76801733b958a8bfd5e3f3c63c`
- New PR this round: NO; amended existing PR #3: YES; merge performed: NO

## Changes and files
- `src/slaif_local_coding/constitution/cache.py`: added current-UID/type/mode
  trust checks for roots, shards, entries, temporary files, and post-rename
  files; rejected symlink adoption; bounded startup discovery; removed expired,
  corrupt, malformed, invalid temporary, and excess derived artifacts; marked
  scan overload unavailable; hardened purge against symlink traversal; advanced
  cache schema to `derived-cache-v2`.
- `src/slaif_local_coding/config.py`: added validated compiler source/candidate/
  JSON-depth bounds, finite cache scan bound, and protected XDG fallback default.
- `src/slaif_local_coding/constitution/compiler.py`: added all required bounds
  and reasoning effort to deduplication fingerprint and persistent cache key;
  used the shared index-schema constant.
- `tests/test_cache.py`, `tests/test_compiler.py`, `tests/test_config.py`,
  `tests/test_live.py`: added cache trust/restart/identity/configuration
  regressions and updated live cache policy.
- `README.md`, `ARCHITECTURE.md`, `ARCHITECTURE-for-agents.md`,
  `docs/LIVE-TEST-ENVIRONMENT.md`, `config/adapter.example.toml`: documented
  cache trust/bounds and corrected current capability/migration facts.
- `oap/active` and exact activated order bytes were committed as transcript only.

## Acceptance evidence
### Criterion A — untrusted cache roots rejected
- PASSED — `test_symlinked_primary_is_rejected_and_protected_fallback_is_used`,
  foreign-owner rejection, bad shard type/mode/owner, bad entry mode, and
  untrusted-fallback tests reject use or remove only the disposable entry.
- A current-user-owned symlink target received no cache entry; an untrusted
  fallback was not adopted.

### Criterion B — bounded disposable restart behavior
- PASSED — restart tests prove valid hit, expired removal, corruption removal,
  malformed-key/temp cleanup, finite scan limit, and whole-cache unavailable on
  overload. Occupancy/eviction regressions remain green.

### Criterion C — complete versioned cache identity
- PASSED — changing reasoning effort, source-byte, prompt-byte, output-token,
  output-byte, candidate-count, or JSON-depth bounds changes the key. Existing
  principal/session/repository/source/model/schema/version isolation tests pass,
  and absent session/repository still disables persistent reuse.

### Criterion D — configuration contract
- PASSED — validated defaults and finite ranges are exposed for cache scan and
  compiler source/candidates/depth bounds; invalid values fail construction.
  The public governed-request zero-compiler-call regression passes and public
  compiler/integration settings remain false-only.

### Criterion E — truthful current capability and migration docs
- PASSED — active documentation distinguishes current loopback-preferred
  text-only/zero-image operation, optional `10.8.132.75` LAN access, historical
  `.76` provenance, and the prior vision deployment. Tests assert these facts;
  merged OAP/reference history was not edited.

### Criterion F — cumulative objective-002 quality
- PASSED — required static/unit/fake/build gates and GitHub implementation-head
  CI passed. Live compiler/cache was rerun after cache-key/code changes and
  passed. Current text/tool/stream/multiturn live cases passed. The live image
  case was truthfully skipped for verified zero-image capability; no current
  vision or production readiness is claimed.

## Verification
- `uv lock --check`: PASSED — lock remained current.
- `uv sync --frozen --extra dev`: PASSED — 31 locked packages checked.
- `uv run --frozen ruff check .`: PASSED.
- `uv run --frozen ruff format --check .`: PASSED — 74 files formatted.
- `uv run --frozen mypy src tests`: PASSED — no issues in 25 source files.
- `uv run --frozen pytest -q`: PASSED — 202 passed, 6 skipped; the six skips are
  opt-in live tests when `SLAIF_LIVE_TEST` is unset.
- `uv run --frozen pytest -q tests/test_cache.py tests/test_config.py tests/test_compiler.py`: PASSED — 46 passed.
- `uv run --frozen pytest -q tests/test_app.py::test_normal_governed_request_makes_zero_compiler_calls`: PASSED.
- `SLAIF_LIVE_TEST=1 uv run --frozen pytest -q tests/test_live.py`: PASSED —
  5 passed, 1 skipped; image skip reason: live model endpoint currently declares
  zero-image capability.
- `uv build`: PASSED — sdist and wheel built.
- `python3 -m compileall -q src tests oap/bin`: PASSED.
- `bash -n oap/bin/*.sh`: PASSED.
- `git diff --check 176bf4d839ae9fa32d0cc3c4279a1b96220c1c61...HEAD`: PASSED.
- Scoped stale-endpoint/current-capability audit: PASSED — active docs contain
  no current vision-service overclaim; `.76` remains only historical provenance.
- Secret/raw-content scan of tracked changes: PASSED — no secret-shaped hit;
  raw-payload logging policy scan produced no hit.
- Real Codex E2E: NOT RUN — not required by this bounded 002-b order.

## Live model/service evidence
- Protected service before and after: user `qwen-serving.service` active/running,
  MainPID `26028`, started `Sat 2026-08-22 05:35:46 CEST`;
  `qwen-serving-vision.service` inactive; listener unchanged on `0.0.0.0:18020`.
- Direct bounded upstream calls: `/health` HTTP 200; `/v1/models` HTTP 200;
  exactly one model ID `qwen3.8-27b`.
- Repository-owned candidate adapter temporarily used loopback `127.0.0.1:18031`
  only, then was stopped; port 18031 was free afterward.
- Adapter live suite: `/healthz`, `/readyz`, `/health`, `/v1/models`, ordinary
  text, forced and automatic tools, multi-turn continuation, SSE text/tool calls,
  and direct compiler/cache all returned successfully. The one-image request was
  rejected by the zero-image fixture and the test skipped; no two-image request
  was sent after that skip.
- No protected model, unit, launch flag, network, profile, or key material was
  changed or printed.

## GitHub CI / required checks
- Implementation head `9192dea62dccdb76801733b958a8bfd5e3f3c63c`: `CI` / `test`
  = SUCCESS.
- All required checks green at drafting: YES.
- The legacy combined commit-status endpoint was PENDING with no statuses while
  the required CheckRun was successful. Report-head checks may be pending;
  strategy verifies them independently.

## Local setup/dependencies
- Used the repository `uv` frozen environment and existing `QWEN3090_API_KEY`
  environment reference; no dependency lock change and no secret persisted.
- Temporarily ran only the repo-owned adapter on loopback port 18031 and stopped
  it after tests.
- No sudo action was required.

## Documentation
- Updated current capability, endpoint migration, cache trust/bounds, identity,
  restart behavior, and example configuration documentation in the same PR.

## Safety/scope confirmations
- Unrelated files changed: NO.
- Secrets or raw prompts/source/images/tool output/request/response bodies
  committed or reported: NO.
- Production systems/data used: NO.
- Protected `18020`/Qwen/Codex fixture changed: NO.
- Required tests skipped/not run: live image case SKIPPED for verified
  zero-image capability; default-suite live tests SKIPPED without opt-in env;
  real Codex E2E NOT RUN because outside this order. All are explicitly labeled
  and not treated as passes.
- Scope deviation: NONE.
- Extra objective PR: NO; coding merge: NO.
- Strategic-authored active/order content edited: NO; exact activation bytes
  committed: YES.
- Report commit report-only: YES.

## Known limitations/blockers
- Current `hinton1` service is text-only/zero-image; image policy is not current
  live-vision evidence.
- Public compiler/cache/injection integration remains disabled by order.
- Persistent cache still requires reliable session/repository identity and does
  not claim signed multi-user production safety.
- Evidence is specific to this single RTX 3090 host and does not establish
  generic hardware, compliance, or frontier-model equivalence.

## Recommended strategic follow-up
- Factual only: review the cache trust/restart implementation and current
  capability documentation; strategy decides any continuation, integration,
  vision-fixture change, cutover, or acceptance separately.

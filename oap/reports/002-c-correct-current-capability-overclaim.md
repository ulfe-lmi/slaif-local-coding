# OAP Coding-Agent Report — 002-c

## Work order
- Identifier: `002-c`
- Order path: `oap/orders/002-c-correct-current-capability-overclaim.md`
- Numeric objective: `002`
- PR mode: AMENDED_EXISTING_PR

## Status
COMPLETE

## Executive summary
Amended objective-002 PR #3 by correcting the current-topology label from an
active vision-service overclaim to an unambiguous text-only service fact. Added
focused documentation regressions for the forbidden exact overclaim, required
current text-only wording, optional-LAN distinction, historical-address
distinction, and retained prior-vision provenance. No runtime, configuration,
dependency, protected-host, or prior-OAP-history behavior was changed.

## Authoritative GitHub state
- Repository: `ulfe-lmi/slaif-local-coding`
- PR number/URL/state: #3,
  https://github.com/ulfe-lmi/slaif-local-coding/pull/3, OPEN non-draft
- Base/head: `main` / `oap/002-constitutional-compiler-cache`
- Starting remote SHA: `fc1b1cffd1f1a7d16976ba19f97952b15ddd703f`
- Required base SHA verified: `176bf4d839ae9fa32d0cc3c4279a1b96220c1c61`
- Implementation head SHA: 1601d5f5258bafebd99dcdf273d21afe70c7e8ca
- Report publication commit: SELF
- Implementation commits pushed before report: `1601d5f5258bafebd99dcdf273d21afe70c7e8ca`
  (first parent `fc1b1cffd1f1a7d16976ba19f97952b15ddd703f`)
- New PR this round: NO
- Amended existing PR: YES
- Merge performed: NO

## Changes and files
- `ARCHITECTURE.md`: changed the “Protected live system under test” topology label
  to `Qwen/vLLM text-only service`; nearby historical/provenance language remained
  unchanged.
- `tests/test_config.py`: extended the existing capability/migration guard to fail
  if `Qwen/vLLM vision service` returns in active architecture, require
  `Qwen/vLLM text-only service`, retain `.75` as optional LAN and `.76` as
  historical, and retain prior-vision/historical-provenance statements.
- `oap/active`: committed unchanged activated bytes selecting `002-c`.
- `oap/orders/002-c-correct-current-capability-overclaim.md`: added unchanged
  activated order bytes.
- No source module, package manifest, lockfile, configuration semantic behavior,
  or other runtime file was modified by this round’s implementation commit.

## Acceptance evidence
### Criterion A — corrected active architecture
- PASSED — implementation commit replaces the sole current-topology occurrence of
  `Qwen/vLLM vision service` with `Qwen/vLLM text-only service`. Existing lines
  continue to identify the current service as language-model-only/zero-image and
  preserve explicitly historical vision deployment references elsewhere.

### Criterion B — regression guard
- PASSED — focused guards assert absence of the exact overclaim, presence of the
  corrected current topology, optional `.75` endpoint, historical `.76`
  distinction, and historical vision provenance. Both focused tests passed.

### Criterion C — unchanged runtime behavior
- PASSED — the new implementation commit changes only `ARCHITECTURE.md`,
  `tests/test_config.py`, and the mandated unchanged `oap/active`/order
  transcript paths. It contains no source/configuration runtime change. The
  cumulative three-dot diff from prior implementation `9192…3c63c` additionally
  displays the immutable `002-b` report already present on this PR; it contains
  no additional runtime path.

### Criterion D — cumulative objective evidence
- PASSED — all ordered local static/unit/fake/build gates passed, and the
  implementation head’s GitHub `test` check was SUCCESS. Runtime code was
  unchanged, so immutable `002-b` compiler/cache and text/tool/stream/multiturn
  live evidence remains valid for cumulative behavior. Its image case remains
  SKIPPED against the verified zero-image fixture and is not counted as vision
  support.

## Verification
- `uv lock --check`: PASSED — resolved 32 packages.
- `uv sync --frozen --extra dev`: PASSED — checked 31 locked packages.
- `uv run --frozen ruff check .`: PASSED.
- `uv run --frozen ruff format --check .`: PASSED — 76 files already formatted.
- `uv run --frozen mypy src tests`: PASSED — no issues in 25 source files.
- `uv run --frozen pytest -q`: PASSED — 202 passed, 6 skipped. The six skips are
  opt-in live-model tests without `SLAIF_LIVE_TEST`; skipped is not treated as
  passing.
- `uv build`: PASSED — sdist and wheel built successfully.
- `python3 -m compileall -q src tests oap/bin`: PASSED.
- `bash -n oap/bin/*.sh`: PASSED.
- `git diff --check 176bf4d839ae9fa32d0cc3c4279a1b96220c1c61...HEAD`: PASSED at
  implementation head.
- Focused documentation/configuration regression:
  `uv run --frozen pytest -q
  tests/test_config.py::test_current_host_capability_is_text_only_with_historical_vision_provenance
  tests/test_config.py::test_current_endpoint_migration_and_historical_provenance`:
  PASSED — 2 passed.
- Credential-bearing syntax scan of staged round diff: PASSED — no API-key/token/
  password/secret assignment, bearer header, cookie header, or private-key block
  matched. An initial broad prose scan matched the order’s own phrase “secret/
  raw-content”; that was identified as policy text, not leaked material.
- Protected-host sanitized snapshot comparison: PASSED — before/after state
  matched after excluding timestamps/event labels.

## Live model/service evidence
- Ordered live model calls this round: NOT RUN (not required; runtime unchanged).
- Read-only reconnaissance confirmed before implementation and again after
  publication preparation: PID `26028` user process `vllm`;
  `qwen-serving.service` MainPID `26028`, active/running/enabled;
  `qwen-serving-vision.service` disabled/inactive; listener `0.0.0.0:18020`
  owned by PID `26028`; ports `18021` and `18031` had no listener. No protected
  service, unit, flag, network binding, key, profile, or host state was mutated.

## GitHub CI / required checks
- Implementation head `1601d5f5258bafebd99dcdf273d21afe70c7e8ca`: check `test`
  SUCCESS (run 32559163689).
- All required checks green at drafting: YES; the observed required set was
  `test`.
- Report-head checks may be pending at drafting; strategy verifies the final
  SELF-head state.

## Local setup/dependencies
- Used the repository’s existing Python 3.12 `uv` frozen environment and dev
  extra. Installed no new dependency. Used no sudo action. Started no adapter
  service.

## Documentation
- Updated active `ARCHITECTURE.md` because its current-topology capability claim
  changed. Documentation regressions were added in the same implementation
  commit. No separate operational contract change was needed.

## Safety/scope confirmations
- Unrelated files changed: NO.
- Secrets/raw prompt/source/image/body/model content exposed: NO.
- Production systems/data used: NO.
- Protected `18020`/Qwen/Codex fixture changed: NO.
- Compiler/cache runtime integration or semantic behavior changed: NO.
- Prior orders/reports/history edited: NO.
- Required tests skipped/not run: six default-suite live tests SKIPPED because
  opt-in live credentials were unset; ordered live model calls were NOT RUN
  because this documentation/test-only round changed no runtime. These states are
  not counted as passes.
- Scope deviation: NONE beyond mandatory inclusion of the activated
  `oap/active` and order transcript bytes.
- Extra objective PR: NO.
- Coding merge/auto-merge: NO.
- Active/order edited: NO.
- Report commit is report-only: YES.

## Known limitations/blockers
- The current protected fixture remains verified as zero-image/text-only. No
  current vision capability or production readiness is claimed.
- Final report-head CI status is externally verifiable after this immutable
  report is pushed; it was intentionally not rewritten after publication.

## Recommended strategic follow-up
- Independently verify final SELF-head CI. No coding-side follow-up is proposed;
  continuation and acceptance remain strategy-owned.

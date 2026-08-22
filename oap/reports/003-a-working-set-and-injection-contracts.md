# OAP Coding-Agent Report — 003-a

## Work order
- Identifier: `003-a`
- Order path: `oap/orders/003-a-working-set-and-injection-contracts.md`
- Numeric objective: `003`
- PR mode: CREATED_NEW_PR

## Status
COMPLETE

## Executive summary
Created objective-003 PR #4 with pure working-set selection/rendering and
endpoint-scoped idempotent injection contracts. The selector deterministically
orders and byte-bounds validated indexes, reports dependency states and missing
P1 acquisition instructions, and fails typed on essential overflow or unsafe
input. Responses and Chat transforms preserve unrelated envelope content and
images while making same-version/content injection idempotent and marker
conflicts fail closed. Public handlers remain disabled from compiler, cache,
selection, and injection integration.

## Authoritative GitHub state
- Repository: `ulfe-lmi/slaif-local-coding`
- PR number/URL/state: #4,
  https://github.com/ulfe-lmi/slaif-local-coding/pull/4, OPEN non-draft
- Base/head: `main` / `oap/003-working-set-injection-foundation`
- Required/verified base SHA: `867ed55e7d115d960c666380ebbc5952d43d97d1`
- Starting remote objective branch: absent
- Implementation head SHA: 47dae670e94afa700aa5fa0f416e28e595cdb91d
- Report publication commit: SELF
- Implementation commits pushed before report:
  `47dae670e94afa700aa5fa0f416e28e595cdb91d`
  (first parent `867ed55e7d115d960c666380ebbc5952d43d97d1`)
- New PR this round: YES
- Amended existing PR: NO
- Merge performed: NO

## Changes and files
- `src/slaif_local_coding/constitution/working_set.py`: added strict, pure,
  versioned selector/render contracts, deterministic ordering, finite UTF-8 and
  entry budgets, typed failures, dependency states, acquisition instructions,
  independent scores, and source-authority marker.
- `src/slaif_local_coding/constitution/injection.py`: added separate Responses
  and Chat transforms with stable insertion, deterministic combination,
  idempotence, bounded marker scanning, fail-closed conflicts/shapes, and safe
  counts.
- `src/slaif_local_coding/config.py`: extended false-only constitution
  configuration with selector/render versions and finite working-set,
  acquisition, entry, traversal-depth, and node bounds.
- `src/slaif_local_coding/constitution/__init__.py`: exported the new typed
  library contracts.
- `tests/test_working_set.py` and `tests/test_injection.py`: added focused
  deterministic, budget, fail-safe, privacy, idempotence, preservation, marker,
  shape, and bounds tests.
- `tests/test_app.py`: expanded the public governed-request regression to assert
  zero compiler/cache-write/selector/injection invocations and unchanged body.
- `tests/test_config.py`: added false-only and finite-bound validation tests.
- `README.md`, `ARCHITECTURE.md`, `docs/ADAPTER-CONFIGURATION.md`, and
  `config/adapter.example.toml`: documented tested foundation behavior, ordering,
  budget/failure/idempotence semantics, privacy boundary, and exclusions.
- `oap/active`: committed unchanged activated bytes selecting `003-a`.
- `oap/orders/003-a-working-set-and-injection-contracts.md`: committed unchanged
  activated order bytes.

## Acceptance evidence
### Criterion A — deterministic working set
- PASSED — repeated synthetic P0/P1/P2/P3/P4 selection is model-equal, content
  SHA-256 is deterministic, root path/hash/version and policy version are stable,
  ordering/statuses are stable, independent confidence and priority are retained,
  missing-P1 instructions contain exact safe paths, and the source-authority
  marker appears in rendered text.

### Criterion B — bounded fail-safe selection
- PASSED — tests prove exact UTF-8 byte accounting, deterministic budget omission
  of P2/P3, P4 omission, whole-entry overflow omission, urgency/path-ordered
  missing-P1 instructions, typed essential overflow without partial law, invalid
  path/key failures, marker-collision failure, dependency-budget failure, and
  absence of cache mechanics/raw-source sentinel in model-visible text.

### Criterion C — idempotent API-specific injection
- PASSED — Responses tests prove insertion, deterministic preservation of
  existing instructions, idempotence, and untouched multiple image items. Chat
  tests prove earliest system insertion, unchanged existing message order/content,
  idempotence, and unchanged image items/counts. Conflicting content, shifted
  marker, duplicate marker, malformed/orphan marker, unsupported instruction or
  message shapes, traversal depth, and node bounds fail closed.

### Criterion D — public handlers remain inert
- PASSED — false-only configuration remains mandatory, and a governed observed
  Responses request forwards unchanged while compiler compile, cache put,
  working-set selector, and both injection functions are asserted to have zero
  invocations.

### Criterion E — quality/documentation
- PASSED — all ordered local gates passed at implementation head, implementation
  GitHub CI was green, and documentation distinguishes the pure foundation from
  pipeline integration, acquisition, rehydration, real Codex E2E, production
  identity, gateway integration, and cutover. Final SELF-head CI is externally
  verifiable after this immutable report push; it was not rewritten later.

## Verification
- `uv lock --check`: PASSED — resolved 32 packages.
- `uv sync --frozen --extra dev`: PASSED — checked 31 locked packages.
- `uv run --frozen ruff check .`: PASSED.
- `uv run --frozen ruff format --check .`: PASSED — 82 files already formatted.
- `uv run --frozen mypy src tests`: PASSED — no issues in 29 source files.
- `uv run --frozen pytest -q`: PASSED — 218 passed, 6 skipped. The six skips are
  opt-in live tests without `SLAIF_LIVE_TEST`; skipped is not treated as passing.
- `uv build`: PASSED — sdist and wheel built successfully.
- `python3 -m compileall -q src tests oap/bin`: PASSED.
- `bash -n oap/bin/*.sh`: PASSED.
- `git diff --check 867ed55e7d115d960c666380ebbc5952d43d97d1...HEAD`: PASSED at
  implementation head.
- Focused selector/injection/config/public-inert regression:
  `uv run --frozen pytest -q tests/test_working_set.py tests/test_injection.py
  tests/test_config.py
  tests/test_app.py::test_normal_governed_request_makes_zero_constitution_pipeline_calls`:
  PASSED — 24 passed.
- Secret/raw-content scan of implementation diff/new files: PASSED — no private
  key block, bearer token, common provider token, or credential assignment
  matched. Tests use only synthetic markers/images/indexes.
- Protected-host sanitized before/after snapshot: PASSED — service identity,
  states, and listeners matched.

## Live model/service evidence
- Ordered live model calls: NOT RUN (not required by 003-a). No upstream request
  was made.
- Read-only reconnaissance before implementation and after publication
  preparation, on host/user `hinton1/janezp`, found `qwen-serving.service`
  MainPID `26028`, active/running, started Sat 2026-08-22 05:35:46 CEST;
  `qwen-serving-vision.service` inactive/dead with MainPID `0`; and listener
  `0.0.0.0:18020` owned by vLLM PID `26028`. Ports `18021` and `18031` had no
  listener. No protected service, unit, model, flag, key, firewall, VPN, network
  binding, or Codex profile was mutated.

## GitHub CI / required checks
- Implementation head `47dae670e94afa700aa5fa0f416e28e595cdb91d`: check `test`
  SUCCESS (run 32561034576).
- All required checks green at drafting: YES; observed required set was `test`.
- Report-head checks may be pending at drafting; strategy verifies the final
  SELF-head state.

## Local setup/dependencies
- Used the repository’s existing Python 3.12 `uv` frozen environment and dev
  extra. Added no dependency or lockfile change. Used no sudo action. Started no
  persistent service or adapter.

## Documentation
- Updated README, active architecture, configuration/operations documentation,
  and the example configuration in the implementation commit. They explicitly
  state that this is objective-003-a library foundation, not end-to-end
  constitution virtualization.

## Safety/scope confirmations
- Unrelated files changed: NO.
- Secrets/raw prompt/source/image/body/model content exposed: NO.
- Production systems/data used: NO.
- Protected `18020`/Qwen/Codex fixture changed: NO.
- Public compiler/cache/injection integration enabled: NO.
- Image policy, proxy fidelity, compiler validation, cache trust, or dependency
  versions altered: NO.
- Prior orders/reports/history edited: NO.
- Required tests skipped/not run: six default-suite live tests SKIPPED because
  opt-in live credentials were unset; all ordered live model calls were NOT RUN
  because 003-a explicitly requires none. Neither state is counted as a pass.
- Scope deviation: NONE beyond mandatory inclusion of activated `oap/active` and
  order transcript bytes.
- Extra objective PR: NO.
- Coding merge/auto-merge: NO.
- Active/order edited: NO.
- Report commit is report-only: YES.

## Known limitations/blockers
- The new contracts are not reachable from public request handlers by design.
- Dependency acquisition, compaction rehydration, signed multi-user identity,
  gateway integration, real Codex E2E support, and cutover remain future work.
- The current protected fixture remains text-only/zero-image; no vision readiness
  is claimed.
- Final report-head CI status is externally verifiable after this immutable
  report is pushed and was intentionally not rewritten after publication.

## Recommended strategic follow-up
- Independently verify final SELF-head CI and review whether 003-b should wire
  the tested contracts into the explicitly ordered request-pipeline slice.

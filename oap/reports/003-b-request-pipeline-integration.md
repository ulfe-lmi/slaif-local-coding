# OAP Coding-Agent Report — 003-b

## Work order
- Identifier: `003-b`
- Order path: `oap/orders/003-b-request-pipeline-integration.md`
- Numeric objective: `003`
- PR mode: AMENDED_EXISTING_PR

## Status
PARTIAL

## Executive summary
Implemented the explicitly enabled one-root constitution pipeline after image
policy, with request-scoped exact source handoff, direct nonrecursive
compiler/cache execution, bounded working-set selection, endpoint-specific
idempotent injection, safe degradation/rejection semantics, and fixed-label
metrics. Defaults remain disabled. All ordered local/static/build gates and the
bounded fresh-cache live suite passed. The objective branch was amended and
pushed, but PR #4 was already merged/closed before activation; GitHub did not
advance its PR head metadata or trigger pull-request CI for the continuation
commit. Creating a replacement PR is prohibited, so required implementation- and
report-head GitHub checks are MISSING and the round is truthfully PARTIAL.

## Authoritative GitHub state
- Repository: `ulfe-lmi/slaif-local-coding`
- PR number/URL/state: #4,
  https://github.com/ulfe-lmi/slaif-local-coding/pull/4, CLOSED and MERGED
- Base/head names: `main` /
  `oap/003-working-set-injection-foundation`
- Required/verified base SHA:
  `867ed55e7d115d960c666380ebbc5952d43d97d1`
- Starting remote head / `003-a` SELF:
  `a2c4cac4425acec04263ae99d34af9ce5371c653`
- Implementation head SHA: 564a400bc9c42a4111f84b3d743b36728f5c2b36
- Report publication commit: SELF
- Implementation commits pushed before report:
  `564a400bc9c42a4111f84b3d743b36728f5c2b36`
  (first parent `a2c4cac4425acec04263ae99d34af9ce5371c653`)
- New PR this round: NO
- Amended existing PR: YES — the required remote branch advanced; GitHub’s
  merged PR object continues to display the merge-time head SHA
- Merge performed by coding: NO

## Changes and files
- `src/slaif_local_coding/config.py`: added explicit global/route integration
  switches, complete static local-appliance identity requirements, compiler
  enablement, supported-version checks, and fail-closed unsafe-combination
  validation. Defaults remain false.
- `src/slaif_local_coding/constitution/detector.py`: added
  `observe_request_with_sources`, returning the public observation manifest plus
  exact request-scoped source bytes keyed by logical path/hash without adding raw
  bytes to serialized contracts.
- `src/slaif_local_coding/constitution/pipeline.py`: added one-root pipeline
  orchestration, static cache/compiler identity, compiler/cache/selection/
  injection execution, post-image-body preservation on safe failures, sanitized
  fail-closed injection rejection, and bounded outcome/duration metrics.
- `src/slaif_local_coding/app.py`: constructed the optional pipeline only when
  globally enabled; ordered JSON/route/image policy, observation/source handoff,
  compiler/cache/selector/injection, deterministic serialization, and upstream
  forwarding; preserved streaming/tools/error paths and lifecycle cleanup.
- `src/slaif_local_coding/constitution/compiler.py` and `compiler_models.py`:
  rejected a P0 dependency (only the supplied root may be P0), strengthened the
  prompt accordingly, and advanced compiler/prompt policy versions to invalidate
  derived artifacts made under the weaker validation.
- Tests and documentation: added fake-upstream pipeline/isolation/failure/
  privacy/stream/image coverage, live pipeline evidence checks, and honest
  single-user MVP limitations and exclusions.
- `oap/active` and the activated order were committed with their exact strategic
  bytes.

## Acceptance evidence
### Criterion A — explicit safe activation
- PASSED — every default remains disabled; enabling requires global
  constitution, direct compiler, complete nonempty configured
  principal/session/repository labels, an enabled route with observation, and
  supported versions. Missing identity, global-without-compiler, global-without-
  enabled-route, and route-without-global/observation combinations fail settings
  validation. Fake tests prove spoofed internal headers cannot activate work.

### Criterion B — correct one-root pipeline
- PASSED — fake-upstream Responses/Chat tests prove one complete root receives a
  stable marker, missing-P1 acquisition text, deterministic transformed upstream
  JSON, preserved model/tools/stream choice and unrelated envelope values, and no
  compilation for zero/multiple/incomplete roots.

### Criterion C — isolation and reuse
- PASSED — identical repeat requests used persistent cache hit; a different
  configured static session caused a second compile. Existing cache tests prove
  every identity/source/model/schema/version/bound dimension isolates keys, and
  absent reliable identity disables persistent reuse. Configuration rejects
  incomplete static identity.

### Criterion D — failure and safety semantics
- PASSED — compiler status failure, ambiguous/incomplete roots, cache
  unavailability, selector failures, and essential overflow preserve the
  post-image governance-bearing body. Conflicting/malformed markers and
  unsupported injection shapes fail closed before model forwarding. Existing
  fake tests preserve SSE/tool/error/disconnect behavior; compiler cancellation
  releases its slot. Image enforcement remains independent and tested.

### Criterion E — observability and privacy
- PASSED — pipeline metrics use fixed endpoint/route/state/reason/outcome labels
  and durations. Tests assert source/candidate/identity sentinels are absent from
  metrics. Repository scan found zero occurrences of the protected credential
  value, and focused source scans found no payload/logging patterns.

### Criterion F — live candidate evidence
- PASSED — on loopback adapter `127.0.0.1:18031`, `/healthz` and `/readyz`
  returned 200, upstream `/health` returned 200, `/v1/models` returned 200 with
  one configured model ID. The final fresh-cache run produced one compiler
  miss-persisted result and one cache hit, two injected pipeline requests, no
  selection/injection failures, ordinary text/tool/SSE successes, and one image
  case SKIPPED because the verified language-model-only fixture rejects images.
  The temporary adapter was stopped and port 18031 was free afterward.

### Criterion G — documentation honesty
- PASSED — README, compact/human architecture, configuration operations, and the
  example describe explicit local single-user identity, ordering, fallback/
  fail-closed behavior, privacy/metrics, and text-only status. They explicitly
  exclude acquisition, tool-output ingestion beyond existing evidence, compaction
  rehydration, signed multi-user identity, real Codex E2E, gateway integration,
  vision readiness, and cutover.

## Verification
- `uv lock --check`: PASSED — resolved 32 packages.
- `uv sync --frozen --extra dev`: PASSED — checked 31 locked packages.
- `uv run --frozen ruff check .`: PASSED.
- `uv run --frozen ruff format --check .`: PASSED — 86 files already formatted.
- `uv run --frozen mypy src tests`: PASSED — no issues in 31 source files.
- `uv run --frozen pytest -q`: PASSED — 229 passed, 7 skipped. Skips are opt-in
  live/image cases and are not counted as passes.
- `SLAIF_LIVE_TEST=1 uv run --frozen pytest -q tests/test_live.py`: PASSED —
  final fresh-cache run completed 6 passed, 1 skipped; the skip was the verified
  zero-image live case.
- `uv build`: PASSED — sdist and wheel built successfully.
- `python3 -m compileall -q src tests oap/bin`: PASSED.
- `bash -n oap/bin/*.sh`: PASSED.
- `git diff --check 867ed55e7d115d960c666380ebbc5952d43d97d1...HEAD`: PASSED at
  implementation head `564a400bc9c42a4111f84b3d743b36728f5c2b36`.
- Focused pipeline/cache/isolation/failure tests: PASSED — the full suite
  included 10 `tests/test_pipeline.py` tests plus compiler/cache/selector/
  injection suites.
- Secret/raw-content scan: PASSED — protected credential value had zero tracked
  or new-file matches; new pipeline had no raw payload logging pattern. Synthetic
  test sentinels are intentionally confined to tests and asserted absent from
  metrics.
- Scoped diff audit: PASSED — only the intended implementation, activated
  transcript, tests, and documentation paths were staged.
- Protected-host before/after snapshot: PASSED — `qwen-serving` MainPID `26028`,
  active/running, same start time; port `18020` remained owned by that vLLM PID;
  ports `18021`/`18031` were free after testing.

## Live model/service evidence
- Host/user: `hinton1` / `janezp`; preferred upstream was loopback port `18020`.
- Read-only reconnaissance found `qwen-serving.service` active/running with the
  same MainPID and start time before and after; launch class is
  `--language-model-only`; ports `18021` and `18031` were free before testing.
- Temporary repo-owned adapter used loopback `18031` only. Bounded health,
  readiness, models, text, forced/automatic tools, multi-turn, SSE, and enabled
  constitution checks passed. Live image request was SKIPPED after rejection by
  the independently verified zero-image fixture; this is not vision support.
- Final fresh-cache metrics recorded one pipeline cache miss persisted, one cache
  hit, two injected Responses requests, and zero selection/injection failures.
  No raw body/source/identity/credential was logged or reported. The temporary
  process was stopped and port 18031 was free.

## GitHub CI / required checks
- Implementation head `564a400bc9c42a4111f84b3d743b36728f5c2b36`: check `test`
  MISSING — the workflow triggers only on pull requests or pushes to `main`, and
  merged PR #4 generated no new pull-request run for this continuation push.
- Prior merge-head `a2c4cac4425acec04263ae99d34af9ce5371c653`: check `test`
  SUCCESS (run 32561181228), but it is not evidence for the new head.
- Report-head checks: MISSING at drafting for the same trigger-state reason.
- All required checks green at drafting: NO. Pending/missing states were not
  treated as pass.

## Local setup/dependencies
- Used the repository’s existing Python 3.12 `uv` frozen environment and dev
  extra. Added no dependency or lockfile change. Used no sudo action. Started and
  stopped only the temporary repo-owned loopback adapter; removed only its
  disposable `/dev/shm` derived-cache directory before the fresh-cache evidence
  run.

## Documentation
- Updated `README.md`, `ARCHITECTURE.md`,
  `docs/ADAPTER-CONFIGURATION.md`, and `config/adapter.example.toml` in the same
  implementation commit.

## Safety/scope confirmations
- Unrelated files changed: NO.
- Secrets/raw prompt/source/image/body/model content committed or reported: NO.
- Production systems/data used: NO.
- Protected `18020`/Qwen/Codex fixture changed: NO.
- Incident disclosure: while attempting to load the protected upstream credential
  for read-only reconnaissance, one shell command sourced a protected key file
  unsafely and the credential value appeared once in the interactive coding
  transcript. The command was stopped immediately. The value was not committed,
  written to repository logs/cache/reports, or printed again; the post-incident
  credential scan returned zero repository matches. Strategy should treat the
  local transcript as exposed and rotate the credential through the protected
  operational process if that exposure boundary is in scope.
- Required tests skipped/not run: local opt-in live tests were SKIPPED in the
  normal suite; the ordered live suite ran and one live image case was SKIPPED
  because the fixture rejects images. No required local command was omitted.
- Scope deviation: NONE in implementation. Protocol/GitHub state prevents the
  ordered “amend PR #4” from producing an OPEN PR or current-head CI because #4
  was merged before activation; no replacement PR was created as required.
- Extra objective PR: NO.
- Coding merge/auto-merge: NO.
- Active/order edited: NO; SHA-256 values were
  `f008bb208a83699a42ea337958902a73e6f91e510b02d904dffe923abc929de0` and
  `f5594ff207e4276c300d3a890bde727caf0b77d939921ed2f4fa30299738e6ff`.
- Report commit is report-only: YES.

## Known limitations/blockers
- PR #4 remains merged/closed; its API head metadata remains the merge-time
  commit rather than continuation head `564a400bc9c42a4111f84b3d743b36728f5c2b36`.
- Required implementation/report-head GitHub CI is MISSING because the existing
  workflow has no branch or manual trigger and a replacement PR is prohibited.
- The pipeline handles exactly one complete observed root; other roots preserve
  post-image semantics with a safe reason.
- Missing dependencies are rendered only as acquisition instructions and are not
  fetched. Paired tool-output ingestion beyond current observation and compaction
  rehydration remain absent.
- Static configured identity is local single-user MVP only and is not signed
  multi-user production identity.
- The current fixture is text-only/zero-image; no vision or production readiness
  is claimed.
- Credential exposure is limited to the interactive coding transcript according
  to the disclosure above, but rotation decision belongs to strategy/human.

## Recommended strategic follow-up
- Independently verify branch commit `564a400bc9c42a4111f84b3d743b36728f5c2b36`,
  this SELF parent/bytes, and the disclosed credential exposure boundary; decide
  whether rotation is required.
- Decide the protocol-compliant GitHub review path for amendments to an already
  merged objective PR or revise workflow/order policy; coding did not create a
  replacement PR.
- If accepted, strategy may plan acquisition/tool-output ingestion, compaction
  rehydration, signed gateway identity, real Codex E2E, gateway integration, and
  cutover as separately ordered work.

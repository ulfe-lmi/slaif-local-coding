# OAP Coding-Agent Report — 007-a

## Work order

- Identifier: `007-a`
- Order path: `oap/orders/007-a-current-gateway-contract-ci.md`
- Numeric objective: Objective007 — current Local↔Gateway contract CI
- PR mode: `CREATED_NEW_PR`

## Status

COMPLETE

## Executive summary

Implemented the current peer-authority fixture, strict exact-checkout verifier,
network-denied pure contract gate, dedicated GitHub Actions job, tests, package
boundary, and documentation. The implementation head is pushed to PR #9. The
fresh exact Gateway checkout gate observed 18/18 tests `PASSED`, zero skips,
zero failures, and zero errors. GitHub `test` and `gateway-contract` both
passed on that implementation head.

## Authoritative GitHub state

- Repository: `ulfe-lmi/slaif-local-coding`
- PR: #9 — https://github.com/ulfe-lmi/slaif-local-coding/pull/9
- PR state: OPEN; base `main`; head `oap/007-current-gateway-contract-ci`
- Starting remote main SHA: `efc4dbcd377dd796a670726b16ebc06bd54b6356`
- Implementation head SHA: `9c2a4840c219bfb5588b786fb8819cdec328e154`
- Report publication commit: SELF
- Implementation commits pushed before report: `9c2a4840c219bfb5588b786fb8819cdec328e154` — Add current Gateway contract CI
- New PR this round: yes; amended existing: no; merge performed: NO

## Changes and files

- Added the sole current peer fixture at `tests/fixtures/gateway/current_peer_authority.json`.
- Added `scripts/gateway_contract.py` for strict fixture parsing, exact Git
  checkout/origin/HEAD/source validation, runtime contract validation, bounded
  GitHub outputs, reentrant network denial, and strict pytest result gating.
- Added runner self-tests and current exact Gateway contract tests, including
  Local-helper-built ID-less continuation, historical-pin separation, no-root
  skip behavior, malformed/incompatible facts, and output-injection rejection.
- Added the separate `gateway-contract` Actions job with runner-local `local/`
  and exact-ref `gateway/` checkouts.
- Added the locked uv `gateway-contract` dependency group; it is not a project
  runtime optional extra and is absent from wheel metadata.
- Updated current testing/integration documentation while retaining historical
  Objective-005 authority and evidence unchanged.
- No `src/` production behavior changed.

## Acceptance evidence

### Criterion 1 — One current peer authority

- `tests/fixtures/gateway/current_peer_authority.json`: `PASSED` — exact keys,
  bounded ASCII grammar, repository `ulfe-lmi/slaif-api-gateway`, Gateway
  commit `65666f5886832034c52211fdd7604046557e6ada`, server
  `local-coding-v1`/`2`/`process_local_inclusive_horizon_fail_closed`, client
  `codex-0.149-responses-v1`/`4`.
- Fixture SHA-256: `b1c968a44dcd6235acee2c8352d96c73fcbdabb83d689c5b45765797442fcc08`.
- Historical regression: `PASSED` — Objective-005
  `GATEWAY_MAIN_SHA` remains exactly
  `5ea38325ef3a3ebc69524b4679b795fab0c52935` and is distinct from the current
  fixture commit.

### Criterion 2 — Strict verifier and contract tests

- Fresh public checkout: `PASSED` — origin identifies the fixture repository,
  `git rev-parse HEAD` equals the fixture commit, checkout is clean, and all
  expected `app/slaif_gateway` paths exist.
- Strict exact-peer gate: `PASSED` — 18 collected, 18 passed, 0 skipped, 0
  failed, 0 errors; network guard enabled.
- Output-injection regression: `PASSED` — CR/LF in repository, commit, nested
  server/client IDs and versions, and replay mode is rejected before writing
  `GITHUB_OUTPUT`.
- Import-path network regression: `PASSED` — an injected DNS attempt during
  Gateway import is stopped as `NetworkAccessDenied`; no connection is made.
  The main runner places exact Gateway inspection/runtime validation and pytest
  under one reentrant denial scope, while local Git probes remain outside it.
- ID-less continuation regression: `PASSED` — uses `_identity_companion_tools`,
  `_idless_companion_initial_body`, and
  `_idless_companion_continuation_body` with a synthetic returned call, then
  feeds that exact Local-produced body to Gateway's replay candidate function.

### Criterion 3 — Dedicated CI

- Workflow job: `PASSED` — ordinary `pull_request` and `main` push triggers,
  read-only contents permission, no `pull_request_target`, no secrets, public
  exact-ref checkout, separate runner directories, locked dependency group,
  strict 18-test gate.
- GitHub Actions run `34753611760`, implementation SHA
  `9c2a4840c219bfb5588b786fb8819cdec328e154`:
  - `test`: SUCCESS, job `103714160187`.
  - `gateway-contract`: SUCCESS, job `103714160290`.

### Criterion 4 — Documentation/package/security boundary

- Documentation: `PASSED` — current peer update sequence, optional fresh
  checkout usage, no-root skip semantics, dependency boundary, historical-pin
  distinction, and limitations documented.
- Wheel inspection: `PASSED` — 20 Local runtime package entries and 2
  LICENSE/NOTICE entries; no Gateway source, peer fixture, workflow, tests, or
  scripts; no `pydantic-settings`/SQLAlchemy runtime metadata or
  `gateway-contract` extra.
- Privacy scan: `PASSED` — implementation diff contains no credential, bearer,
  private-host, or model-service pattern.

### Criterion 5 — Scope and protected-host safety

- Production `src/` behavior: unchanged.
- Qwen/vLLM, port 18020, services, provider/model inference, databases, Redis,
  Codex runtime/profile, credentials, network, firewall/VPN, and protected
  host state: unchanged and not accessed.

## Verification

- `uv run --frozen pytest -q tests/test_gateway_contract_runner.py`: `PASSED` — 21 passed.
- `uv run --frozen python scripts/gateway_contract.py --gateway-root <fresh exact checkout> --run-tests`: `PASSED` — 18/18, zero skips/errors/failures; exact checkout and network guard proven.
- `uv run --frozen pytest -q`: `SKIPPED` — command succeeded with 887 passed and 26 expected Gateway-dependent/live skips; no failure.
- `uv run --frozen ruff check .`: `PASSED`.
- `uv run --frozen ruff format --check .`: `PASSED`.
- `uv run --frozen mypy src tests`: `PASSED` — 60 source files.
- `uv build`: `PASSED`.
- `uv run --frozen python -m compileall -q src tests oap/bin`: `PASSED`.
- `bash -n oap/bin/*.sh`: `PASSED`.
- `git diff --check`: `PASSED`.
- `gh pr checks 9`: `PASSED` — both required checks successful at implementation head.

## Live model/service evidence

- `NOT RUN` — this order is repository-only and forbids Qwen/vLLM, provider,
  service, model, Codex, credential, database, Redis, and protected-host calls.

## GitHub CI / required checks

- Implementation-head run: `34753611760` at
  `9c2a4840c219bfb5588b786fb8819cdec328e154`.
- `test`: SUCCESS; `gateway-contract`: SUCCESS.
- All required checks green at drafting: yes.
- Report-head checks: not applicable until the report-only child is pushed;
  strategy verifies them independently.

## Local setup/dependencies

- Ordinary CI uses the existing locked `dev` project extra.
- Contract CI uses the locked uv `gateway-contract` dependency group with
  `pydantic-settings` and SQLAlchemy only for pure Gateway imports; no full
  Gateway stack is installed or started.
- Fresh Gateway checkout acquisition and package installation were the only
  network-enabled setup operations.

## Documentation

Updated `TESTING.md`, `docs/GATEWAY-CONTRACT-CI.md`, and
`docs/SLAIF-GATEWAY-INTEGRATION.md` for current peer authority, workflow
operation, dependency boundaries, no-root behavior, historical evidence, and
limitations.

## Safety/scope confirmations

- Unrelated files: preserved; pre-existing empty untracked `Local`, `clean`,
  and `unchanged` files remain untouched and uncommitted.
- Secrets/raw content: none committed, logged, or reported.
- Protected 18020/Qwen/Codex fixture changed: NO.
- Required tests skipped/not run: live/service/model tests are `NOT RUN` by
  scope; ordinary no-root Gateway-dependent tests retain expected skips.
- Scope deviation: none.
- Extra objective PR: NO; coding merge: NO.
- Active/order content edited: NO; exact activated bytes committed.
- Report commit report-only: yes.

## Known limitations/blockers

- Current CI proves pure source-contract compatibility only; it does not prove
  Gateway deployment, provider behavior, Qwen/vLLM behavior, cutover, or
  release readiness.
- Ordinary no-root development intentionally skips Gateway-dependent tests.
- GitHub emitted non-blocking Node.js action deprecation annotations; both jobs
  still completed successfully.

## Recommended strategic follow-up

Strategy may independently review the 12-file PR diff, report parent/SELF
invariants, current checks, and the stated non-production limitations. Merge,
acceptance, release, and next-objective choice remain strategic/human authority.

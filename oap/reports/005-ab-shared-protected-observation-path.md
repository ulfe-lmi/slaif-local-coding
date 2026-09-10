# OAP Coding-Agent Report — 005-ab

## Work order

- Identifier: `005-ab`
- Order path: `oap/orders/005-ab-shared-protected-observation-path.md`
- Numeric objective: Objective-005 acceptance
- PR mode: `AMENDED_EXISTING_PR`
- Existing PR: 7, `https://github.com/ulfe-lmi/slaif-local-coding/pull/7`

## Status

COMPLETE

## Executive summary

The Local acceptance harness now uses one direct HTTPX observer to derive
provider request, image, function/call-ID, response-lifecycle, and terminal
facts in fake and synthetic protected execution. Synthetic protected hooks
replace only protected resource boundaries; the disposable fake provider's
semantic oracle is disabled in the protected branch. Explicit bounded
`GET /health` and `GET /v1/models` provider preflight probes are admission and
method/endpoint scoped. Four serial protected cases are retained as sanitized
evidence. Real protected inference, cutover, merge, and release acceptance
were not run or claimed.

## Authoritative GitHub state

- Repository: `ulfe-lmi/slaif-local-coding`
- PR: #7, `https://github.com/ulfe-lmi/slaif-local-coding/pull/7`, OPEN,
  non-draft, MERGEABLE, CLEAN
- Base/head: `main` / `oap/005-gateway-ingress-integration`
- Starting remote SHA: `f09b9a985e93693b413e33d6a33a0fedbab86309`
- Implementation head SHA: `c820a8f752eb49c72658eda60eaaa93bd2a61579`
- Report publication commit: SELF
- Implementation commits pushed before report: `6c55b793`, `003c557127`,
  `caaace3b`, `6b2c527b`, `a127290b`, `c820a8f7`
- Fresh qualification source: `a127290b172969d0267e11774f5c25c3563a5eac`;
  the `c820a8f7` descendant changed only current testing/evidence files.
- New PR this round: NO
- Amended existing PR: YES
- Merge performed: NO

## Changes and files

- Added direct-observer request-fact projection with bounded classes, approved
  fixture hashes, and provider-boundary lifecycle facts.
- Added endpoint/method-scoped, one-shot provider preflight permissions and
  counted `/health` and `/v1/models` observations.
- Disabled fake semantic-oracle use in synthetic protected qualification and
  derived protected predicates from observed Gateway-to-Local-to-provider
  traffic.
- Added genuine pre-dispatch mapping/dependency validation before credential or
  provider access, with known-zero all-kind counters and complete row output.
- Added serial healthy, observer-failure, combined-failure, and pre-dispatch
  evidence cases.
- Updated [TESTING.md](../../TESTING.md),
  [SLAIF-GATEWAY-INTEGRATION.md](../../docs/SLAIF-GATEWAY-INTEGRATION.md), and
  sanitized evidence under `oap/evidence/005-ab/`.

## Acceptance evidence

### Criterion 1 — shared semantic observation path

- PASSED: direct observer facts are used for synthetic protected provider
  predicates; fake provider semantic snapshots are unavailable in that branch.
- PASSED: the admitted natural continuation supplied matching call-ID and
  valid terminal lifecycle facts. The observed item-ID class was `present`;
  the standalone fake id-less HTTP regression remains regression evidence only.
- PASSED: image counts and approved fixture hashes are derived at the direct
  provider boundary; the outer fake gate independently agrees with direct
  dispatch counts.

### Criterion 2 — provider preflight and bounded accounting

- PASSED: synthetic protected healthy case observed exactly one `/health` and
  one `/v1/models`, both HTTP 200, through the direct observer; fake semantic
  oracle availability was `false`.
- PASSED: healthy synthetic case recorded 28 attempted/admitted direct
  dispatches: 6 compiler, 12 inference, 10 other, including 2 provider
  preflight and 3 candidate-readiness requests. All observed operations had
  bounded lifecycle counts and no retry.

### Criterion 3 — failure retention and pre-dispatch safety

- PASSED: healthy synthetic protected gate had 29/29 rows and projections
  `PASSED`.
- PASSED: observer failure stopped after 1 compiler and 1 inference dispatch,
  retained `observer_readiness_lost` plus
  `provider_boundary_unobserved`, and dispatched no later inference.
- PASSED: combined observer/projection/cleanup case retained primary and
  secondary failure classes, including `cleanup_failed`, and all 29 rows.
- PASSED: mapping/dependency failure occurred before credential/provider work;
  compiler, inference, and other counts were all zero, credential-hook calls
  were zero, all 29 rows were serialized, and cleanup had no pending state.

### Criterion 4 — complete ordered rehearsal

- PASSED: outer fake C1–C5/D machine gate was 37/37 obligations and 37/37
  projections, with 26 direct dispatches and 12/12 terminal-valid inference
  observations.
- PASSED: all four synthetic protected cases were serially exercised and
  retained in `oap/evidence/005-ab/` with artifact hashes and fixed statuses.
- PASSED: the protected fixture snapshot remained unchanged: vision service
  active, expected PID/start/restart facts, port 18020 present, ports 18021
  and 18031 absent, seven Qwen worktree changes, and text service inactive.

## Verification

- `.venv/bin/pytest -q tests/test_acceptance_harness.py tests/test_transport_observer.py tests/test_gateway_accounting_rehearsal.py`: PASSED — 202 tests.
- `.venv/bin/pytest -q`: PASSED — 756 passed, 8 skipped; skips remain distinct and are not acceptance passes.
- `.venv/bin/ruff format --check .`: PASSED — 265 files formatted.
- `.venv/bin/ruff check .`: PASSED.
- `.venv/bin/mypy src tests`: PASSED — 57 source files.
- `.venv/bin/python -m compileall -q src scripts tests`: PASSED.
- `PYTHONPATH=<local-repo>:<local-repo>/src:<gateway> <gateway-venv>/bin/python scripts/gateway_accounting_rehearsal.py --gateway-root <gateway> --gateway-python <gateway-venv>/bin/python --provider-target fake --codex <codex-0.149.0>`: PASSED — fresh sanitized outer fake and four serial synthetic protected cases; output SHA-256 `02827b40d3757a66e3cb83ba1d3c5154a05c728249ab2de78e255e3f6ae1da3e`.
- `jq` validation plus SHA-256 validation of `oap/evidence/005-ab/*.json`: PASSED.
- Concrete credential/raw-content scan of `oap/evidence/005-ab`: PASSED.
- `.venv/bin/python -m build --wheel --outdir /tmp/slaif-005-ab-wheel`: FAILED — isolated build frontend could not create a venv because system `ensurepip` is unavailable; no repository state was changed.
- `.venv/bin/python -m hatchling build -t wheel -d /tmp/slaif-005-ab-wheel-local`: PASSED — wheel built; 26-file wheel boundary contains package, license, and notice files only; scripts/tests/OAP evidence excluded. Wheel SHA-256: `14985c8bc29de21defe3b7d625ad05cfc82eb6da2c6620121440a5fdee9ed61e`.
- Read-only protected fixture snapshot via `_protected_snapshot()`: PASSED — expected fixed fixture facts; no authenticated request or protected credential read.
- Required GitHub check `test` on implementation head `c820a8f752eb49c72658eda60eaaa93bd2a61579`: PASSED — run `34424812601`, job `102707668924`.

## Live model/service evidence

- Read-only host/service facts: vision unit active/running, MainPID class
  expected, expected start/restart facts, listener 18020 present, 18021 and
  18031 absent, text unit inactive, Qwen worktree count 7.
- Disposable fake provider: bounded authenticated fake-only calls through the
  temporary Gateway/Local candidate; no protected endpoint was used.
- Real protected `/health`, `/v1/models`, compiler, inference, vision, and
  diagnostic requests: NOT RUN — expressly unauthorized by this order.
- Protected Qwen/model/checkpoint/venv/unit/network state mutation: NO.

## GitHub CI / required checks

- Implementation-head `test`: SUCCESS at report drafting, run
  `34424812601`, job `102707668924`.
- All required checks green at drafting: YES.
- Report-head checks may be newly pending after this report-only push;
  strategy verifies them independently.

## Local setup/dependencies

- Used the existing repository `.venv` with Python 3.12, pytest, Ruff, and
  mypy.
- Installed repo-local build tooling `hatchling==1.32.0` and its build support
  into `.venv` to complete the wheel boundary; `uv.lock` and project
  dependencies were not changed.
- Used the existing exact Gateway fixture at the ordered SHA and Codex 0.149.0
  binary at the ordered SHA. No OAP executor profile or provider profile was
  changed.

## Documentation

Updated `TESTING.md` and `docs/SLAIF-GATEWAY-INTEGRATION.md` with the shared
observer, preflight, failure-case, and non-acceptance evidence boundary.
Added bounded machine evidence under `oap/evidence/005-ab/`.

## Safety/scope confirmations

- Unrelated files: preserved; final non-report work was limited to active
  order scope, code/tests, current docs, and bounded evidence.
- Secrets/raw content: no real keys, credentials, bearer values, prompts,
  source, images, tool output, model content, or raw request/response bodies
  entered the report/evidence.
- Protected 18020/Qwen/Codex fixture changed: NO.
- Required real protected acceptance/cutover tests: NOT RUN by explicit order
  boundary; no production/readiness equivalence claimed.
- Extra objective PR: NO.
- Coding merge/auto-merge: NO.
- Active/order edited after activation: NO; exact activated bytes were
  committed unchanged.
- Report commit report-only: YES; verified after publication below.

## Known limitations/blockers

- The healthy protected case is synthetic orchestration evidence using a
  disposable physical fake provider. It does not establish real protected
  provider semantics or production acceptance.
- The system build frontend remains unavailable on this host without
  `ensurepip`; the repository-local Hatchling wheel build is the successful
  package boundary check.

## Recommended strategic follow-up

Review the immutable evidence and the explicit `protected_acceptance=false`
boundary; independently decide any later real protected acceptance or cutover
order.

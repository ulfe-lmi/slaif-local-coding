# OAP Coding-Agent Report — 005-ac

## Work order

- Identifier: `005-ac`
- Order path: `oap/orders/005-ac-remove-fixture-assumptions-from-acceptance.md`
- Numeric objective: `005`
- PR mode: `AMENDED_EXISTING_PR`

## Status

COMPLETE

## Executive summary

Corrected the four acceptance-harness defects in the activated order. Protected
mode now uses the same counted provider preflight and direct-observer semantic
projection with or without synthetic hooks. Function-call continuation evidence
correlates validated returned call IDs with the admitted continuation inside its
phase, session, and observer lifetime without retaining raw IDs. Repeated legal
SSE event categories no longer exhaust category storage; scalar event and byte
bounds remain enforced.

The fresh exact-pinned fake qualification passed 37/37 outer obligations and
projections and the healthy synthetic protected branch passed 29/29. The three
injected synthetic failure cases remained truthful and serialized. No real
protected inference, credential access, cutover, merge, or release action was
performed.

## Authoritative GitHub state

- Repository: `ulfe-lmi/slaif-local-coding`
- PR: #7, https://github.com/ulfe-lmi/slaif-local-coding/pull/7
- State: OPEN, non-draft; base `main`; head `oap/005-gateway-ingress-integration`
- Starting remote SHA: `3658177c6669b673f5bab0f60d2eff08c4bcfae6`
- Implementation head SHA: `c97429d6f48545485e8b681865ab532819dd5fa3`
- Report publication commit: SELF
- Implementation/evidence commits pushed before report: `d49ff680df68c67354cede4c3f5a99dbdaa49d9f`, `cadc159042b6a9e53a7c0f02b41ccc566e8a5a76`, `57efaa69507176003ddaba7b817f69aeea06602c`, `c97429d6f48545485e8b681865ab532819dd5fa3`
- New PR this round: NO; amended existing PR: YES; merge performed: NO

## Changes and files

- `scripts/gateway_accounting_rehearsal.py`: shared protected preflight/projection, structured request classification, opaque call correlation, and fake-boundary updates.
- `tests/helpers/transport_observer.py`: validated returned-call correlation and distinct bounded SSE category storage.
- `tests/test_transport_observer.py`: long repeated-delta, scope, mismatch, and boundary regressions.
- `tests/test_gateway_accounting_rehearsal.py`: actual returned-call, text-name, preflight-stop, and projection regressions.
- `TESTING.md`: current 005-ac behavior and qualification limitations.
- `oap/evidence/005-ac/*.json`: sanitized machine qualification evidence.
- `oap/active` and the activated order were committed unchanged.

No `src/` production module, dependency, lockfile, Gateway checkout, model,
service, profile, network, or protected-host resource was changed.

## Acceptance evidence

### Criterion 1 — Shared protected request-control and projection path

- Result: PASSED.
- `_protected_provider_preflight` counts `/health` and `/v1/models` under the
  existing observer/budget path and stops before `/v1/models` after a failed
  health or observer boundary.
- Hook-independent direct-observer projection is covered by focused tests and
  the healthy synthetic protected gate. Healthy synthetic dispatches: 28;
  provider probes admitted/consumed: 2/2; readiness probes admitted/consumed:
  3/3.

### Criterion 2 — Actual call-ID relationship and omission handling

- Result: PASSED.
- The observer registers only bounded digests of call IDs from validated
  returned function-call items and matches the admitted continuation by phase,
  session, and lifetime. Initial-owned, matching, missing, mismatched, and
  reordered cases are distinct; ordinary text type names are not classified as
  items.
- ID-less continuation with the matching call ID is observed in the focused
  direct observer regression and the fake qualification C1.4/Codex call-ID
  predicates passed. Raw IDs are absent from safe evidence.

### Criterion 3 — Legal repeated SSE event categories

- Result: PASSED.
- The observer retains bounded distinct event categories plus scalar counts.
  A 48-event legal stream with 46 repeated text deltas passed for both
  coalesced and split network chunks; 16-KiB event and 128-KiB stream bounds
  remain enforced.

### Criterion 4 — Qualification, evidence, and safety

- Result: PASSED.
- Outer fake machine gate: 37/37 obligations and projections, 26/26 direct
  dispatches (6 compiler, 12 inference, 8 other), 12/12 inference terminal
  valid, 6 SSE and 6 JSON inference observations, exact fake-provider
  agreement, terminal accounting, cleanup, and secret-free logs.
- Healthy synthetic protected branch: 29/29 rows/projections, 28/28 direct
  dispatches including 2 provider probes and 3 readiness probes;
  `protected_acceptance=false`.
- Failure cases: observer failure `BLOCKED` with primary
  `observer_readiness_lost`; combined projection/cleanup failure `BLOCKED`
  retaining secondary failures; pre-dispatch mapping failure `BLOCKED` with
  zero credential-hook/provider dispatches.
- Sanitized evidence: `oap/evidence/005-ac/index.json` and its five linked
  machine artifacts. Run output SHA-256:
  `063cd8283ec4edd4387202078dbe305c0e9d39e0d21fcfc701bf357aca833b84`.

## Verification

- `uv run --frozen ruff check .`: PASSED — no findings.
- `uv run --frozen ruff format --check .`: PASSED — 267 files formatted.
- `uv run --frozen mypy src tests`: PASSED — no issues in 57 files.
- `uv run --frozen pytest -q`: PASSED — 765 passed, 8 skipped.
- `uv run --frozen pytest -q tests/test_transport_observer.py tests/test_gateway_accounting_rehearsal.py tests/test_acceptance_harness.py`: PASSED — 211 passed.
- `uv build --wheel --sdist`: PASSED — wheel and source distribution built.
- `python -m compileall -q src scripts tests`: PASSED.
- CI run `34428017656`, check `test`: SUCCESS — Ruff, format, mypy, full
  pytest, `uv build`, compileall, and `bash -n oap/bin/*.sh` all passed.
- `python -m build --wheel --sdist`: FAILED — host isolated-build environment
  lacked `ensurepip`; the supported `uv build` path and required CI build
  passed.
- Evidence privacy scan over `oap/evidence/005-ac`: PASSED — no raw payload,
  credential, bearer, image, or call-ID artifact detected.

## Live model/service evidence

- Read-only fixture snapshot: vision unit active, expected fixed fixture/start
  class, zero restarts, port 18020 present, ports 18021/18031 absent, text unit
  inactive, Qwen worktree count 7.
- Unauthenticated `http://127.0.0.1:18020/health`: HTTP 200.
- Authenticated requests: 0; credential reads: 0; model/compiler/inference/
  vision calls: 0; fixture mutation: NO.
- The real protected matrix and cutover acceptance remain `NOT RUN` by order.

## GitHub CI / required checks

- Implementation-head check observed before report: CI `test` SUCCESS at
  implementation head `c97429d6f48545485e8b681865ab532819dd5fa3`.
- All required checks green at drafting: YES.
- Report-head checks may be pending after the report-only push; strategy
  verifies them independently.

## Local setup/dependencies

- Used the repository locked environment for local checks.
- Used a disposable detached Gateway checkout at the authorized pin
  `50dcc3b85d614eb1d0c6196595bf22ef5779f846` and a temporary Python 3.12
  Gateway environment for the exact fake qualification.
- Used disposable PostgreSQL/tmpfs and loopback fake services only. No host
  daemon, package, privileged network, protected key, or live Qwen mutation.

## Documentation

Updated `TESTING.md` with the shared preflight/projection contract, opaque
continuation evidence, repeated-event bound behavior, qualification results,
and explicit protected/cutover limitations.

## Safety/scope confirmations

- Unrelated files: preserved; no unrelated working-tree changes at publication.
- Secrets/raw content: not committed, printed in evidence, or retained.
- Production/protected resources: unchanged.
- Protected 18020/Qwen/Codex fixture changed: NO.
- Required live protected matrix/cutover tests: NOT RUN by explicit order.
- Extra objective PR: NO; coding merge: NO.
- Active/order edited: NO; committed unchanged.
- Report commit report-only: YES.

## Known limitations/blockers

- No real protected inference or real protected provider semantic acceptance is
  claimed. The synthetic protected branch is orchestration evidence only.
- No cutover, release-readiness, merge, or production-equivalence claim is
  made.
- The standalone `python -m build` command is unavailable on this host because
  its isolated environment cannot use `ensurepip`; `uv build` and CI passed.

## Recommended strategic follow-up

Strategy should independently review the exact 005-ac evidence, report-only
parent/head relation, current PR checks, and the explicit real-protected and
cutover limitations before deciding acceptance or merge.

# OAP Coding-Agent Report — 005-y

## Work order

- Identifier: `005-y`
- Order: `oap/orders/005-y-operation-permits-and-protected-branch-conformance.md`
- Numeric objective: Objective-005
- PR mode: `AMENDED_EXISTING_PR`

## Status

PARTIAL

## Executive summary

Implemented explicit operation/phase/kind transport permissions and connected
them to the direct HTTPX observer. The measured 23-request rehearsal shape is
encoded as bounded slots for 6 compiler, 12 inference, and 5 other requests;
unassigned, exhausted, wrong-kind, wrong-phase, and cross-lifetime dispatches
fail closed before delegate invocation. Network-chunk byte accounting is now
separate from incremental SSE-frame accounting. Synthetic-only protected hooks
now support post-dispatch, projection, and cleanup failure injection with
bounded evidence retention.

The ordered repository-only implementation and CI are green. The complete
shared-runner synthetic protected executions and exact pinned Gateway/Codex
fake matrix are not claimed: the required Gateway execute commit
`50dcc3b85d614eb1d0c6196595bf22ef5779f846` is not reachable from the Gateway
remote, whose current main is `d142fd7f04c46fac3469b9b9bba1bd2068aabad8`.

## Authoritative GitHub state

- Repository: `ulfe-lmi/slaif-local-coding`
- PR: 7 — https://github.com/ulfe-lmi/slaif-local-coding/pull/7
- State: OPEN; draft: NO; merge state: CLEAN
- Base/head: `main` / `oap/005-gateway-ingress-integration`
- Starting remote SHA: `494bfc2992d1da0e6917e95e7e4765f378b2bb82`
- Implementation head SHA: `be8428857b26bc032324b7d9610e23baa458a670`
- Report publication commit: SELF
- Implementation commits pushed before report: `be8428857b26bc032324b7d9610e23baa458a670`
- New PR this round: NO; amended existing: YES; merge performed: NO

## Changes and files

- `tests/helpers/acceptance_harness.py`: added the finite public-operation
  dispatch plan, explicit consumable permissions, safe dispatch facts, and
  separate network-chunk/frame byte accounting.
- `tests/helpers/transport_observer.py`: consumes permissions immediately
  before delegation, checks frames at parser boundaries, and exposes a
  synthetic-only post-dispatch observation seam.
- `scripts/gateway_accounting_rehearsal.py`: maps the existing 23-request
  rehearsal to the explicit plan, wires protected synthetic hooks, and keeps
  primary failure/counts through projection and cleanup failures.
- `tests/test_acceptance_harness.py`, `tests/test_transport_observer.py`:
  permission, wrong-phase, cross-lifetime, split/coalesced-frame, oversized
  frame, stream, concurrency, and post-dispatch-stop regressions.
- `TESTING.md`, `docs/SLAIF-GATEWAY-INTEGRATION.md`: documented measured
  permit/frame behavior and synthetic protected limitations.
- `oap/active` and the exact 005-y order: committed byte-for-byte as the
  activated orchestration transcript.

## Acceptance evidence

### Criterion A — operation permits

- PASSED — The controller requires an admitted operation before any transport
  dispatch and consumes the current plan slot at observer admission.
- PASSED — Missing, exhausted, wrong-kind, wrong-phase, and cross-lifetime
  cases reject before delegate invocation; focused tests count delegate calls.
- PASSED — The frozen nine logical operations remain maximum-one with zero
  retries, while the explicit plan distinguishes macro attempts from actual
  compiler/inference/other requests.

### Criterion B — frame versus network chunk bounds

- PASSED — Connected observer tests accept the same legal SSE wire data when
  coalesced or split into small chunks; per-frame checks do not reject a large
  network chunk containing individually legal frames.
- PASSED — An oversized completed frame and cumulative stream overflow latch
  the budget, close the stream, and prevent later dispatch.
- PASSED — Existing deadline, close, cancellation, concurrency, and response
  byte-preservation regressions remain green.

### Criterion C — synthetic protected runner

- PARTIAL — `ProtectedRuntimeHooks` now carries synthetic-only dispatch
  completion, projection-failure, cleanup-failure, and bounded-clock seams;
  the actual runner preserves safe phase/count/failure/cleanup facts and keeps
  `protected_acceptance=false`.
- PASSED — Existing protected preflight/missing-dependency and direct
  post-dispatch observer regressions prove no real credential or protected
  request is used by those tests.
- NOT RUN — Complete healthy, observer-failure-after-dispatch, combined
  projection/cleanup-failure, and pre-dispatch mapping executions through the
  full Gateway → Local shared runner. The required exact Gateway execute pin
  was unavailable, so no substitute revision was used.

### Criterion D — verification and qualification

- PASSED — Full local pytest and static/package checks listed below.
- PASSED — Required PR CI at implementation head.
- NOT RUN/BLOCKED — Exact pinned Codex 0.149.0 C1–C5/D fake machine matrix;
  the Codex binary checksum was verified, but the exact Gateway execute
  checkout cannot be obtained from the remote.

## Verification

- `uv run --frozen pytest -q tests/test_acceptance_harness.py tests/test_transport_observer.py tests/test_gateway_accounting_rehearsal.py`: PASSED — 188 passed.
- `uv run --frozen pytest -q`: PASSED — 742 passed, 8 skipped; skips remain explicit live/host gates.
- `uv run --frozen ruff check .`: PASSED.
- `uv run --frozen ruff format --check .`: PASSED — 259 files formatted.
- `uv run --frozen mypy src tests`: PASSED — 57 files, no issues.
- `uv run --frozen python -m compileall -q scripts tests/helpers src`: PASSED.
- `bash -n oap/bin/*.sh`: PASSED.
- `uv build --wheel --sdist`: PASSED — wheel and sdist built.
- Wheel boundary scan: PASSED — no `tests/` or `scripts/` members.
- `git diff --check`: PASSED.
- Exact Codex fixture SHA-256: PASSED — `bbc3341e44c9ead340ed9570c17be936e37870f570751a941699ffd04d672827`.
- Exact Gateway execute pin availability: BLOCKED — `50dcc3b85d614eb1d0c6196595bf22ef5779f846` not advertised by the remote.
- `gh pr checks 7`: PASSED — `test`, run `34410885332`, job `102664759464`, SUCCESS at implementation head.

## Live model/service evidence

- Read-only process fact: PID `23961`, start `Sun Sep 6 18:57:26 2026`,
  command class `vllm`.
- Read-only listener fact: port `18020` is listening for PID `23961`; ports
  `18021`, `18030`, and `18031` had no listener.
- Unauthenticated health status only: `http://127.0.0.1:18020/health` returned
  HTTP `200`; response body was not read or retained.
- Read-only Qwen worktree count: 7 modified entries, matching the ordered
  unrelated-change baseline. No Qwen file contents were read.
- `systemctl --user show qwen-serving.service` reported `ActiveState=inactive`
  and `SubState=dead` while the ordered vLLM PID/listener remained present;
  this discrepancy is recorded, not normalized.
- Protected credential, `/proc` environment, model, compiler, inference,
  vision, diagnostic, or authenticated protected request: NOT RUN.

## GitHub CI / required checks

- Implementation-head `test`: SUCCESS — run `34410885332`, job
  `102664759464`.
- All required checks green at drafting: YES.
- Report-head checks: strategy must independently verify any new post-report
  run; no report rewrite is authorized.

## Local setup/dependencies

- Existing repository `.venv` and frozen `uv` environment only.
- No dependency, lockfile, binary, Gateway, service, Docker, or protected
  installation mutation.
- The exact pinned Gateway source was not available locally or at its remote
  execute ref; no alternate pin was installed or used.

## Documentation

Updated `TESTING.md` and `docs/SLAIF-GATEWAY-INTEGRATION.md` with the finite
permit plan, frame/chunk boundary, synthetic hooks, and non-acceptance limits.

## Safety/scope confirmations

- Protected 18020/Qwen/Codex fixture changed: NO.
- Protected model, checkpoint, venv, unit, launch, GPU, key, firewall, VPN,
  network binding, and active profile changed: NO.
- Secrets, credentials, raw prompts, source, images, tool output, SSE bodies,
  private URLs, and customer data entered the report/logs: NO.
- Unrelated pre-existing work: preserved; only the activated order/active and
  listed in-scope rehearsal/docs/tests were committed.
- Extra objective PR: NO; coding merge/auto-merge: NO.
- Active/order edited after activation: NO.
- Report commit report-only: YES; to be verified after SELF publication.

## Known limitations/blockers

- Exact Gateway execute commit `50dcc3b85d614eb1d0c6196595bf22ef5779f846`
  cannot currently be fetched; main advertises `d142fd7f04c46fac3469b9b9bba1bd2068aabad8`.
- Full exact fake C1–C5/D qualification and full shared-runner synthetic
  protected executions are NOT RUN, so this round is PARTIAL.
- No protected acceptance, cutover, merge, release, or production-equivalence
  claim is made.

## Recommended strategic follow-up

Provide or authorize access to the immutable exact Gateway execute checkout,
then rerun the ordered fake matrix and full synthetic protected cases. Strategy
decides any continuation or acceptance; coding does not infer it.

# OAP Coding-Agent Report — 005-t

## Work order

- Identifier: `005-t`
- Order: `oap/orders/005-t-strict-observer-and-exact-safety-evidence.md`
- Numeric objective: Objective-005
- PR mode: `AMENDED_EXISTING_PR`

## Status

COMPLETE

## Executive summary

Corrected the repository-only direct HTTPX observer and fake-evidence gate while
preserving the direct Local transport architecture. Responses SSE framing is
incremental and chunk-invariant, semantic validation is injected from the exact
pinned Gateway validator/profile, evidence is fixed-class and bounded, counts
are exact before bucketing, and every observer failure stops later dispatch.

The final fake rehearsal passed the complete selected machine gate: 37/37
obligations, no missing result, no first failure, and zero retries. The observer
recorded 23 operations (6 compiler, 12 inference, 5 other), with all 23
completed and terminal-valid and all 12 inference operations having first-byte
and normal-close facts. Independent fake-provider counters matched exactly.

## Authoritative GitHub state

- Repository: `ulfe-lmi/slaif-local-coding`
- PR: #7 — https://github.com/ulfe-lmi/slaif-local-coding/pull/7
- PR state before report publication: OPEN, non-draft, MERGEABLE/CLEAN
- Base/head: `main` / `oap/005-gateway-ingress-integration`
- Starting remote SHA: `0a659601ad5d871e007c15b45e029b1bbddf5d8c`
- Implementation head SHA: `4041e80431d732a1d3640417c8031781d8a5d471`
- Report publication commit: SELF
- Implementation commits pushed before report:
  `4dd80c4283c7adbd9146aca0133a0ea559a3d428`,
  `45f9d64976b0f2a44f6c3223d767c28f5405e1a`,
  `4041e80431d732a1d3640417c8031781d8a5d471`
- New PR this round: NO
- Amended existing PR: YES, PR #7
- Merge or auto-merge performed: NO

## Changes and files

- `tests/helpers/transport_observer.py`: incremental LF/CRLF SSE framing,
  comments/data handling, frame/stream caps, payload/event agreement, exact
  Gateway-validator injection, response-ID digest continuity, fixed endpoint
  and exception classes, exact counters, fail-stop readiness, abnormal-close
  handling, and global ordinal remapping across candidate lifetimes.
- `scripts/gateway_accounting_rehearsal.py`: injects the exact Gateway
  `ResponsesStreamEventValidator` and request-scoped Codex route/tool profile;
  validates bounded evidence through an owned descriptor; rejects duplicate or
  non-finite JSON; and requires clean relevant source/config state for tested
  heads and report-only descendants.
- `tests/test_transport_observer.py`: focused framing, semantic, cap,
  cancellation/error, exact-count, readiness, and ordinal regressions.
- `tests/test_gateway_accounting_rehearsal.py`: independent parameterized
  negative evidence matrix for singleton/removed/duplicate/reordered/extra
  results, false/absent observations, wrong relationships, failed projections,
  retries, stale identity/profile, count mismatch, oversized, duplicate-key,
  and non-finite evidence.
- `TESTING.md` and `docs/SLAIF-GATEWAY-INTEGRATION.md`: corrected observer,
  validator, fail-stop, bounded-gate, and fake-only evidence guarantees.
- Activated `oap/active=005-t` and the exact active order were committed
  unchanged; prior OAP orders/reports were not edited.

## Acceptance evidence

### Criterion A — strict observer validity

- PASSED — The final fake run used the clean detached Gateway implementation
  `50dcc3b85d614eb1d0c6196595bf22ef5779f846` and its
  `gateway_responses_stream_validator` source marker. The request-scoped
  profile derives only the exact Gateway Codex 0.149 taxonomy from the bounded
  outbound request; no caller header or all-tools switch supplies authority.
- PASSED — LF, CRLF, one-byte boundaries, coalesced frames, comments, payload /
  event-type agreement, response-ID continuity, terminal output, usage, and
  semantic failures are covered by focused tests and the full fake run.
- PASSED — Unknown events/fields/types project only to fixed `other`/`error`
  classes. Endpoint paths and exception classes are fixed classes; raw paths,
  IDs, exception names/messages, bodies, arguments, and event payloads are not
  retained.
- PASSED — Exact integer counters are compared before display buckets. The
  final observer facts were attempted=23, dispatched=23, responded=23,
  completed=23, terminal-valid=23, compiler attempted/dispatched/completed=6,
  and inference attempted/dispatched/completed/terminal-valid=12.
- PASSED — The 5-versus-50 and related count-collision regressions reject equal
  display buckets when exact counts differ. Merged lifetimes remap ordinals
  uniquely while retaining each per-lifetime ordinal and any prior failure.

### Criterion B — fail-stop and streaming safety

- PASSED — Malformed, overflowed, validator-failed, truncated, cancelled,
  delegated, and abnormal-close streams latch observer failure and prevent
  later dispatch. Cleanup is idempotent and the original response stream is
  still passed through without whole-stream buffering.
- PASSED — Focused tests prove zero later delegate calls after automatic stream
  failure, fixed error evidence, and readiness failure. Candidate readiness is
  checked before candidate startup and every transport admission.
- PASSED — The fake run used direct HTTPX transport inside the actual Local
  `create_app(settings, transport=...)` candidate, with no relay, proxy, or
  provider-side status endpoint.

### Criterion C — bounded private evidence and reuse

- PASSED — Fake evidence is opened with `O_NOFOLLOW`, checked as one owned
  regular file, and read cap-plus-one before JSON parsing. Duplicate keys,
  non-finite values, wrong nested types, unsafe files, and oversized files are
  rejected.
- PASSED — The gate requires complete ordered result/projection/schema
  coverage, true observations, exact relationships, current Gateway/Codex /
  observer identity, and exact transport count fields.
- PASSED — Exact-head and report-only-descendant reuse both reject dirty
  relevant source/config state; only the prior report-only path is permitted in
  a descendant. Independent negative tests exercise each rejection class.

### Criterion D — complete fake matrix

- PASSED — Actual Codex 0.149.0 ran through the exact Gateway, actual Local
  candidate, and strict loopback fake Qwen. Codex binary SHA-256 was
  `bbc3341e44c9ead340ed9570c17be936e37870f570751a941699ffd04d672827`.
- PASSED — The machine gate was `COMPLETE`, `passed=true`, 37/37 selected
  results `PASSED`, `missing=[]`, `first_failure=null`, and `retry_count=0`.
  Same-session full-image/resumed-crop, governance/compiler/cache/rehydration,
  signing/replay/tamper/isolation, tool/call-ID lifecycle, accounting,
  privacy, cleanup, and cutover refusal/rollback rows passed.
- PASSED — Fake-provider and observer exact counters matched; cleanup facts
  for processes, listeners, database, cache, Codex home, replay/identity/
  provider failure state, and secret-free logs were true.
- NOT RUN — Protected Qwen credentials, inference, compiler, image calls, and
  installed cutover. This order expressly prohibits them.

## Verification

- `uv run --frozen pytest -q`: PASSED — 698 passed, 8 skipped. Skips remain
  honest host/live gates and are not counted as passes.
- `uv run --frozen pytest -q tests/test_transport_observer.py tests/test_gateway_accounting_rehearsal.py`:
  PASSED — 58 passed.
- Pinned fake rehearsal through Gateway/Local/Codex/fake Qwen:
  PASSED — final implementation `4041e804…`, 37/37, zero missing/first
  failure/retry, exact direct-observer match, cleanup true.
- `uv run --frozen ruff check .`: PASSED.
- `uv run --frozen ruff format --check .`: PASSED — 249 files formatted.
- `uv run --frozen mypy src tests`: PASSED — 57 files, no issues.
- `uv run --frozen python -m compileall -q scripts tests/helpers src`:
  PASSED.
- `bash -n oap/bin/*.sh`: PASSED.
- `git diff --check`: PASSED.
- `uv build --wheel --sdist`: PASSED — wheel and sdist built.
- Wheel boundary scan: PASSED — built wheel contains no `tests/` or
  `scripts/` members.
- Bounded diff/pin/privacy scan: PASSED — changed paths are limited to the
  active order, selector, observer/runner/tests/docs; no raw-payload logging
  patterns, credential material, model weights, or protected configuration was
  introduced.

## Live model/service evidence

- Only final read-only PID/start/restart/unit/listener facts were checked.
- Vision Qwen remained active with MainPID `23961`, `NRestarts=0`, and start
  `Sun 2026-09-06 18:57:26 CEST`; port 18020 remained the listener.
- `qwen-serving.service` remained inactive/dead with MainPID 0. Candidate
  ports 18021, 18030, and 18031 were absent after cleanup.
- No protected credential/environment/raw-log/config read, model listing,
  compiler call, inference, image call, diagnostic call, service mutation,
  network/firewall/VPN change, or active-profile change occurred.
- The temporary exact Gateway checkout/venv, PostgreSQL tmpfs container,
  candidate processes/listeners, caches, Codex home, logs, and result artifacts
  were removed after the fake run.

## GitHub CI / required checks

- Implementation-head `test`: SUCCESS — run `34389257642`, job
  `102593230787`, observed on implementation SHA
  `4041e80431d732a1d3640417c8031781d8a5d471`.
- All required checks green at drafting: YES.
- Report-head checks may be pending after publication; strategy verifies the
  new PR head.

## Local setup/dependencies

- Used the existing frozen Local environment.
- Used a task-owned disposable detached Gateway checkout at the exact ordered
  SHA and a temporary Python 3.12 environment with Gateway runtime/dev
  dependencies; removed after verification.
- Used the existing bounded runner's disposable PostgreSQL 16 tmpfs/`--rm`
  state and loopback fake provider. No Local dependency, lockfile, binary,
  Gateway source, or persistent service was changed.

## Documentation

Updated `TESTING.md` and `docs/SLAIF-GATEWAY-INTEGRATION.md` with the actual
005-t validator injection, framing/semantic boundaries, exact counters,
fail-stop behavior, bounded evidence gate, and fake-only result. Historical
orders and reports remain unchanged.

## Safety/scope confirmations

- Unrelated files and prior OAP artifacts: preserved.
- Protected 18020/Qwen/Codex fixture changed: NO.
- Protected credentials or inference used: NO.
- Extra objective PR: NO.
- Coding merge/auto-merge/acceptance/release: NO.
- Active/order edited by coding: NO; strategic activation bytes committed
  unchanged.
- Final report commit report-only: YES.

## Known limitations/blockers

- Protected provider-call and terminal-lifecycle observation, real protected
  vision acceptance, installed cutover, and release readiness remain unclaimed
  because this order prohibits protected traffic and service mutation.
- Local skipped tests remain explicitly skipped host/live gates; they do not
  weaken the fake machine gate or become passes through report prose.

## Recommended strategic follow-up

Strategy may independently review the exact PR diff, report-only topology,
current report-head CI, and the separation between this fake observer evidence
and any future authorized protected acceptance.

## Lifecycle state at publication

| State | Result |
| --- | --- |
| `IMPLEMENTED` | yes |
| `TESTED` | yes — full fake gate and repository checks |
| `REAL-E2E ACCEPTED` | no |
| `CUTOVER ACCEPTED` | no |
| `MERGED` | no |
| `RELEASE-READY` | no |

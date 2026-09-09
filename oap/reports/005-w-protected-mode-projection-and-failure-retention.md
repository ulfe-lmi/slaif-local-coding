# OAP Coding-Agent Report — 005-w

## Work order

- Identifier: `005-w`
- Order: `oap/orders/005-w-protected-mode-projection-and-failure-retention.md`
- Numeric objective: Objective-005
- PR mode: `AMENDED_EXISTING_PR`

## Status

COMPLETE

## Executive summary

Repaired the Local acceptance harness's protected-mode projection and
finalization boundary using fake-only execution. Protected mode now has its
own complete projection/schema contract, including direct `C5.4` fixture
evidence. A bounded payload-free accumulator retains primary failure, exact
compiler/inference lifecycle counts, observer classes, phase/ordinal, and
cleanup facts across exits. Admission-time budgets are enforced before the
ordered fake operations. A synthetic protected-mode path proves phase
selection, direct-observer requirements, first-failure stop, cleanup snapshot
retention, and row serialization without reading credentials or calling the
protected service.

The fresh fake qualification passed. Protected inference acceptance, cutover,
merge, and release readiness remain unclaimed and were not run.

## Authoritative GitHub state

- Repository: `ulfe-lmi/slaif-local-coding`
- PR: #7 — https://github.com/ulfe-lmi/slaif-local-coding/pull/7
- State: OPEN, non-draft, MERGEABLE; implementation-head merge state was
  `CLEAN` before the report-only child
- Base/head: `main` / `oap/005-gateway-ingress-integration`
- Starting remote SHA: `10a73962eef93f9a848e80b940fa1f9242476ddd`
- Implementation head SHA: `3bdbc89f330b9c612c94b160703e8c8423714e13`
- Report publication commit: SELF
- Implementation commits pushed before report: `ccc97ba23d6fe65c6c9845440d77cede475b1e08`,
  `3bdbc89f330b9c612c94b160703e8c8423714e13`
- New PR this round: NO
- Amended existing PR: YES, PR #7
- Merge or auto-merge performed: NO

## Changes and files

- `scripts/gateway_accounting_rehearsal.py`: mode-specific projection,
  payload-free accumulator integration, total safe failure result/finalization,
  pre-dispatch operation admission, synthetic protected-mode conformance, and
  protected fixture projection.
- `tests/helpers/acceptance_harness.py`: protected projection/schema contract,
  mapping validation, bounded `BudgetController`, `RunAccumulator`, and
  injected synthetic protected-mode conformance support.
- `tests/test_acceptance_harness.py`: positive/negative mode coverage,
  mapping-shape rejection, budget exhaustion, accumulator retention, and
  credential-hook refusal tests.
- `tests/test_gateway_accounting_rehearsal.py`: protected `C5.4` gate and
  unknown-observation regression coverage.
- `TESTING.md`, `docs/SLAIF-GATEWAY-INTEGRATION.md`: measured 005-w behavior,
  failure-retention, budget, synthetic-conformance, and non-acceptance limits.
- Activated `oap/active` and the exact `005-w` order were committed unchanged.

## Acceptance evidence

### Criterion A — complete mode projection and preflight coverage

- PASSED — Fake and protected projection tables are distinct. The protected
  table contains all 29 protected-selected IDs in manifest order and a direct
  `C5.4` fixture projection; the fake table retains all 37 fake-selected IDs.
- PASSED — Missing, duplicate, unknown, and reordered mapping tests fail
  closed through `validate_projection_contract` before candidate or dispatch
  hooks. The protected gate regression serializes every selected row and does
  not raise the prior `KeyError`.
- PASSED — Protected runtime observations use the protected schema and do not
  fall back to fake-server facts. Unavailable fixture fields remain absent/
  unknown rather than becoming zero or `PASS`.

### Criterion B — primary evidence retention and total finalization

- PASSED — `RunAccumulator` is bounded to fixed failure classes, four secondary
  classes, 16 snapshots, fixed phase names, and exact nonnegative compiler and
  inference attempted/dispatched/responded/completed counts. It retains no raw
  stream, body, request ID, secret, or arbitrary exception.
- PASSED — Observer snapshots are captured before candidate/server teardown;
  cumulative direct-transport counts are retained across disposable observer
  lifetimes. The first failure is retained when a later serialization or
  cleanup class is recorded.
- PASSED — Wrapper and cleanup paths return a fixed safe blocked result for
  preflight, client/parser, timeout, cancellation, observer, and finalization
  failures. The injected negative conformance test stops later dispatch and
  still records cleanup/serialization facts.

### Criterion C — executable budgets and protected-mode synthetic conformance

- PASSED — Admission control enforces the unchanged 900-second wall bound,
  nine ordered public operations with maximum one attempt and zero retries,
  16 KiB event cap, 128 KiB aggregate stream cap, and single-phase
  concurrency. Lower injected limits are exercised by unit tests; production
  maxima are unchanged.
- PASSED — Fresh fake-only synthetic protected conformance selected the
  protected mode, completed phases `preflight`, `candidate`, `dispatch`, and
  `finalize`, serialized all 29 selected projection rows as `NOT RUN`, and
  returned `protected_acceptance=false`. Direct transport was observed,
  fake-only observation was false, cleanup snapshot was available, and
  credential reads were zero.
- PASSED — Injected missing direct transport produced fixed
  `provider_boundary_unobserved`, zero later dispatches, and completed cleanup.
  The conformance path never invokes its optional credential hook.

### Criterion D — fake qualification, documentation, and safety

- PASSED — Fresh exact fake qualification at implementation
  `3bdbc89f330b9c612c94b160703e8c8423714e13` returned `COMPLETE`; all 37
  selected obligation results and all 37 fake projection rows were `PASSED`,
  with `missing=[]`, `first_failure=null`, `retry_count=0`, and zero false
  runtime observations.
- PASSED — Fake direct observer recorded 23 attempted, dispatched, responded,
  and completed operations: 6 compiler and 12 public inference dispatches;
  all 12 inference operations were terminal-valid. Independent fake-provider
  counters matched, with 6 compiler calls, 12 inference calls, and no bad
  authentication.
- PASSED — Documentation was updated in `TESTING.md` and
  `docs/SLAIF-GATEWAY-INTEGRATION.md`. Historical 005-q, 005-r, and 005-v
  unknown/failed protected facts remain unchanged.
- PASSED — Task-owned temporary Gateway, virtual environment, fake output,
  database, candidate, cache, and process state were removed after the run.

## Verification

- `uv run --frozen pytest -q tests/test_acceptance_harness.py tests/test_gateway_accounting_rehearsal.py`: PASSED — 149 passed.
- `uv run --frozen pytest -q`: PASSED — 726 passed, 8 skipped; skips remain explicit live/host gates.
- Fresh exact pinned Gateway/Local/Codex fake rehearsal, `--provider-target fake`: PASSED — 37/37 machine gate, 23/23 observer lifecycle counts, exact fake-provider match, synthetic protected conformance, and cleanup.
- `uv run --frozen ruff check .`: PASSED.
- `uv run --frozen ruff format --check .`: PASSED — 255 files already formatted.
- `uv run --frozen mypy src tests`: PASSED — 57 files, no issues.
- `uv run --frozen python -m compileall -q scripts tests/helpers src`: PASSED.
- `bash -n oap/bin/*.sh`: PASSED.
- `uv build --wheel --sdist`: PASSED.
- Wheel boundary scan: PASSED — built wheel contains no `tests/` or `scripts/` members.
- `git diff --check HEAD~2 HEAD`: PASSED.
- Diff-only privacy scan for bearer-like values, API-key values, and image data: PASSED — no matches in newly added lines.

## Live model/service evidence

- Protected mode: NOT RUN by this order; no protected credential was read and
  no authenticated protected health, models, compiler, inference, vision, or
  diagnostic request was made.
- Read-only post-run host facts matched the ordered baseline: vision unit
  active with the ordered start identity and zero restarts; text unit
  inactive; protected listener `18020` present; candidate listeners `18021`
  and `18031` absent; seven Qwen worktree entries.
- Protected Qwen/model/network/systemd/Codex profile state changed: NO.
- Synthetic protected conformance is orchestration evidence only and is not
  real protected inference acceptance.

## GitHub CI / required checks

- Implementation-head `test`: SUCCESS — run `34401704097`, job
  `102634904810`, observed on implementation head
  `3bdbc89f330b9c612c94b160703e8c8423714e13`.
- All required checks green at drafting: YES.
- Report-head checks may be pending after publication; strategy verifies them.

## Local setup/dependencies

- Used the existing frozen Local environment.
- Used a disposable detached Gateway checkout at exact
  `50dcc3b85d614eb1d0c6196595bf22ef5779f846`, with its temporary Python
  environment and no source mutation.
- Used the ordered Codex `0.149.0` fixture with checksum
  `bbc3341e44c9ead340ed9570c17be936e37870f570751a941699ffd04d672827`.
- Fake qualification used task-owned loopback fake Qwen, temporary PostgreSQL
  16 tmpfs/`--rm`, Local candidate, temporary cache/Codex home, and bounded
  cleanup. No host package, daemon, network, Qwen, or profile mutation.

## Documentation

Updated `TESTING.md` and `docs/SLAIF-GATEWAY-INTEGRATION.md` with the measured
mode-specific projection, accumulator/finalization, budget, synthetic
conformance, fake qualification, and protected non-acceptance contract.

## Safety/scope confirmations

- Historical orders/reports were preserved; active/order bytes were not edited
  by coding.
- No raw prompts, source, images, SSE/tool output, request IDs, credentials,
  private URLs, customer data, or model weights were committed or reported.
- Protected port 18020/Qwen/Codex fixture changed: NO.
- No Gateway source, `src/` production module, dependency lockfile, active
  profile, firewall/VPN/network, relay, service, model, or credential state was
  changed.
- No extra objective PR; coding merge/auto-merge/acceptance: NO.
- Final report commit report-only: YES.

## Known limitations/blockers

- Real protected provider-boundary, semantic, tool, vision, governance,
  accounting, isolation, and terminal acceptance remain `NOT RUN`; no
  protected retry was authorized.
- Synthetic protected rows are deliberately `NOT RUN` and
  `protected_acceptance=false`; they prove orchestration safety only.
- Installed cutover, active-profile changes, merge, release readiness, and
  production/multi-user equivalence remain unclaimed.
- One initial preflight-only fake invocation was rejected because temporary
  output files were inside the disposable Gateway checkout; those files were
  moved outside the checkout, the checkout was restored clean, and the fresh
  qualification then passed. It caused no provider, credential, or protected
  traffic and is not counted as the qualified run.

## Recommended strategic follow-up

Review the repaired protected projection/finalization evidence and decide any
future order for protected testing. Independently verify this report-only
commit's parent, changed path, exact bytes, PR head, and report-head checks.

## Lifecycle state at publication

| State | Result |
| --- | --- |
| `IMPLEMENTED` | yes |
| `TESTED` | yes — focused/full repository checks, exact fake gate, and synthetic protected conformance |
| `REAL-E2E ACCEPTED` | no |
| `CUTOVER ACCEPTED` | no |
| `MERGED` | no |
| `RELEASE-READY` | no |

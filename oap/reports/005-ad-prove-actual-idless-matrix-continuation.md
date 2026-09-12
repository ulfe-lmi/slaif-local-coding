# OAP Coding-Agent Report — 005-ad

## Work order

- Identifier: `005-ad`
- Order: `oap/orders/005-ad-prove-actual-idless-matrix-continuation.md`
- Numeric objective: `005`, omission-proof continuation on PR 7
- PR mode: `AMENDED_EXISTING_PR`

## Status

COMPLETE

## Executive summary

The C1.4 projection now requires an actual composed two-request witness. The
existing `identity_replay` allowance uses one streamed initial function call
returned by the Gateway → Local → disposable provider chain, followed by one
non-streaming continuation that omits only the optional item ID and retains the
matching mandatory call ID. The requests share the admitted operation, phase,
ordinal, lifetime, and session; both are terminal-valid and both accounting
reservations finalize without pending or duplicate request IDs.

Present-only, missing-call-ID, mismatched-call-ID, and unrelated focused facts
cannot promote C1.4. The natural unmodified Codex shape was recorded
separately and supplied the optional item ID. Real protected authenticated
inference was not run, as required by this order.

## Authoritative GitHub state

- Repository: `ulfe-lmi/slaif-local-coding`
- PR: 7, https://github.com/ulfe-lmi/slaif-local-coding/pull/7
- State: OPEN, non-draft; base `main`; head branch
  `oap/005-gateway-ingress-integration`
- Starting remote SHA: `d08baef0029a802ee90dcb85dc93ddbea4e83095`
- Implementation head SHA: `302f11aaaaa4427f469a6cb0a0d5e14d88434bfe`
- Report publication commit: SELF
- Implementation commits pushed before report: `7b2cb05`, `71577e5`,
  `079ce65`, `d6e7403`, `c678489`, `8d4c56e`, `3f2af8b`, `11aef87`,
  `86af179`, `c5bdcf0`, `302f11a`
- New PR this round: NO; amended existing PR: YES; merge performed: NO

## Changes and files

- `scripts/gateway_accounting_rehearsal.py`: strict composed companion
  projection, transient bounded returned-call capture, actual companion
  request mapping, and data-only SSE terminal-frame support.
- `scripts/local_qwen_provider_differential.py`: recognize the valid
  `response.function_call_arguments.done` event.
- `tests/helpers/transport_observer.py`: accept the bounded namespace tool
  class used by the actual companion envelope.
- `tests/helpers/acceptance_harness.py`: identify C1.4 as produced by the
  composed companion rather than the standalone regression.
- `tests/test_gateway_accounting_rehearsal.py` and
  `tests/test_local_qwen_provider_differential.py`: companion, negative,
  split/coalesced SSE, and event-vocabulary coverage.
- `TESTING.md`: 005-ad contract and final qualification facts.
- `oap/evidence/005-ad/slot-plan.json`: immutable pre-execution slot plan;
  `oap/evidence/005-ad/qualification.json`: sanitized final evidence.

## Acceptance evidence

### Criterion 1 — actual omission and same-call relationship

- PASSED: C1.4 was `PASSED` in the fake machine gate with no missing rows.
- Initial request: streamed SSE, 2xx, one returned function call, terminal-valid.
- Continuation: non-streaming JSON, 2xx, optional item ID omitted, mandatory
  call ID classified as matching, terminal-valid.
- Both direct-observer records share `identity_replay` / `codex` / ordinal 5 /
  lifetime `identity` and the same session discriminator.
- Accounting: two terminal reservations, zero pending reservations, zero
  duplicate request IDs.
- Gateway call-ID/HMAC ownership and no-scope-downgrade facts were true for the
  admitted signed route.

### Criterion 2 — negative and natural-shape protection

- PASSED: present-ID, mismatched-call-ID, missing-call-ID, and
  present-only-without-companion cases all failed as positive C1.4 evidence.
- PASSED: natural Codex two-turn shape was independently recorded with item ID
  present and was not used as id-less evidence.
- PASSED: existing identity tamper, replay, isolation, authorization, and
  pre-provider negative matrix remained green.

### Criterion 3 — bounded qualification

- PASSED: fake gate 37/37 obligations and 37/37 projections; `missing=[]`,
  first failure null, zero retries.
- PASSED: direct observer measured 26 dispatches: 6 compiler, 12 inference,
  and 8 other; all 12 inference observations were terminal-valid.
- PASSED: synthetic protected healthy branch serialized and passed 29/29
  selected rows with the fake semantic oracle unavailable.
- PASSED: synthetic observer-failure, combined projection/cleanup-failure,
  and pre-dispatch mapping-failure cases each serialized all 29 rows and
  stopped with their intended bounded failure classes.
- Evidence: `oap/evidence/005-ad/qualification.json`.

## Verification

- `PYTHONPATH=<repo>:<repo>/src:<repo>/scripts:<gateway>/app <gateway-venv>/bin/python scripts/gateway_accounting_rehearsal.py --gateway-root <gateway> --gateway-python <gateway-venv>/bin/python --provider-target fake --codex <codex-0.149.0>`:
  PASSED — fake 37/37 and synthetic protected 29/29; companion passed.
- `./.venv/bin/pytest -q`: PASSED — 774 passed, 8 skipped (live/unavailable
  tests; not counted as passes).
- `uv run --frozen mypy src tests`: PASSED — 57 source files.
- `./.venv/bin/ruff check .`: PASSED.
- `./.venv/bin/ruff format --check .`: PASSED — 269 files.
- `python3.12 -m compileall -q src tests scripts oap/bin`: PASSED.
- `bash -n oap/bin/bootstrap-two-codex-oap.sh oap/bin/launch-coding-agent.sh oap/bin/launch-strategic-agent.sh`:
  PASSED.
- `uv lock --check`: PASSED.
- `uv pip check --python .venv/bin/python`: PASSED.
- `uv build --wheel --out-dir <temporary-directory>`: PASSED — one
  package-only wheel, 26 files, no tests/OAP/rehearsal files.
- `python3.12 -m build --wheel`: BLOCKED — host Python has no `ensurepip`;
  the `uv build` alternative passed.
- JSON validation and evidence privacy scan: PASSED — no raw payloads, call
  IDs, credentials, private URLs, or raw logs retained.
- `gh pr checks 7 --repo ulfe-lmi/slaif-local-coding`: PASSED — `test`
  SUCCESS, run `34434962530`, job `102736176806`, on implementation head.

## Live model/service evidence

- Host: `hinton1`.
- Read-only snapshot: `qwen-serving-vision.service` active/running, MainPID
  `23961`, start `Sun 2026-09-06 18:57:26 CEST`, restarts `0`.
- Port `18020` listener remained present and its unauthenticated health status
  was 200. The text unit remained inactive/MainPID 0; ports 18021, 18030, and
  18031 were free at snapshot time; the Qwen worktree retained 7 pre-existing
  changes.
- Protected authenticated inference, model/compiler traffic, and vision
  acceptance: `NOT RUN`.
- Protected Qwen/vLLM/service/network/profile mutation: NO.

## GitHub CI / required checks

- Implementation-head required check `test`: SUCCESS, run
  `34434962530`, job `102736176806`.
- All required checks at drafting: YES.
- Report-head checks may be newly pending after the report-only push; strategy
  verifies them independently.

## Local setup/dependencies

- Used the existing repository `.venv` for local tests/static checks.
- Used a disposable detached Gateway checkout at
  `50dcc3b85d614eb1d0c6196595bf22ef5779f846` and a disposable Python 3.12
  environment, with a temporary PostgreSQL 16 loopback container.
- Used the exact Codex 0.149.0 binary and verified SHA-256 recorded in the
  evidence artifact.
- No host daemon, package, protected service, model, network, or profile change.

## Documentation

Updated `TESTING.md` with the 005-ad contract and final measured facts.
Sanitized machine evidence is retained under `oap/evidence/005-ad/`.

## Safety/scope confirmations

- Unrelated pre-existing work preserved.
- No secrets, raw bodies, prompts, source, images, tool outputs, call IDs, or
  credentials entered the report/evidence.
- Protected 18020/Qwen/Codex fixture changed: NO.
- Real protected acceptance, cutover acceptance, merge, and release readiness:
  NOT RUN / NOT CLAIMED.
- Extra objective PR: NO. Coding merge: NO.
- Active/order edited: NO.
- Final report commit report-only: YES.

## Known limitations/blockers

- The composed omission witness is a fake-provider/direct-observer and
  synthetic protected-orchestration qualification. It is not real protected
  vLLM semantic acceptance.
- Eight live tests were skipped by the repository suite because their external
  fixtures were unavailable; they are not represented as passed.
- The stdlib `python -m build` path is unavailable on this host because
  `ensurepip` is absent; the frozen `uv build` path passed.

## Recommended strategic follow-up

Review the immutable evidence and separately decide whether any future order
should authorize authenticated protected inference or cutover. This round does
not authorize either action.

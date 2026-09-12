# OAP Coding-Agent Report — 005-an

## Work order

- Identifier: `005-an`
- Order path: `oap/orders/005-an-gateway162-final-protected-acceptance.md`
- Numeric objective: 005, final Gateway162 synchronization and protected acceptance
- PR mode: `AMENDED_EXISTING_PR`

## Status

BLOCKED

## Executive summary

Gateway162 synchronization and zero-argument validator-profile propagation are
implemented and source-bound. The focused Gateway162 suite, full local suite,
static/package gates, and the clean fake 37/37 machine gate passed. The single
authorized protected matrix reached the existing vision-Qwen path and stopped
fail-closed at the first direct `stream_closure_invalid` failure during
identity replay (ordinal 5). No protected retry occurred; later protected
inference remained `NOT RUN`. Protected acceptance, cutover, merge, and release
readiness are not claimed.

## Authoritative GitHub state

- Repository: `ulfe-lmi/slaif-local-coding`
- PR: #7 — https://github.com/ulfe-lmi/slaif-local-coding/pull/7
- State: OPEN; base `main`; head `oap/005-gateway-ingress-integration`
- Starting remote SHA: `0210ae11b53234d85848a61e6ee0a56cbe0cb290`
- Implementation head SHA: `556ca152a589747b5c9adeca3d44de56e61ce08c`
- Report publication commit: SELF
- Implementation commits pushed before report:
  - `8245f1c0270e0a314058f2afa77c9f6e80ace483` — Gateway162 profile/pin implementation and activated transcript
  - `556ca152a589747b5c9adeca3d44de56e61ce08c` — sanitized acceptance evidence and current documentation
- New PR this round: NO
- Amended existing PR: YES
- Merge performed: NO

## Changes and files

- `scripts/gateway_accounting_rehearsal.py`: Gateway v4/app-tree pins and
  request-derived `zero_argument_function_names` propagation into the exact
  Gateway `ResponsesStreamValidationProfile`; no Local `src/` change.
- `tests/helpers/gateway_accounting_rehearsal.py`,
  `tests/helpers/gateway_provider_driver.py`, and
  `scripts/codex_tool_envelope_differential.py`: operative Gateway162 SHA.
- `tests/test_gateway162_validator_factory.py`: bounded positive/negative
  profile and lifecycle coverage.
- `TESTING.md` and `docs/SLAIF-GATEWAY-INTEGRATION.md`: current Gateway162
  contract and actual round result; historical sections preserved.
- `oap/evidence/005-an/index.json`: sanitized source-bound fake/protected
  evidence, row dispositions, budgets, and fixture invariants.
- `oap/active` and the activated `005-an` order were committed byte-for-byte;
  neither was edited by coding.

## Acceptance evidence

### Criterion A — Gateway162 synchronization and exact profile propagation

- Result: PASSED for implementation scope.
- Clean detached Gateway checkout: commit
  `5ea38325ef3a3ebc69524b4679b795fab0c52935`; `app` tree
  `a7b64d35650b61fbba3558ddb519c6e52a627ec9`.
- Accepted Gateway production implementation:
  `732e3bad17d93909f210321b97bedd8e5718fb7b`.
- Complete merged Gateway tree:
  `1ede9cea41c566b141441ad9a3122133d5fc1ff6`.
- Paired client module: `codex-0.149-responses-v1`, version `4`; reviewed
  fixture digest `ca1e03a35de1eaeceb894cec9895af0c154e0d2fa0aa8da87f98716e1567f9ec`.
- The factory calls Gateway's
  `codex_0149_zero_argument_function_names` on the parsed request only when
  the existing streaming-tools gate is active. It does not recreate Gateway's
  schema heuristic or alter canonical argument events.
- Focused Gateway162 tests: `8 passed`, `0 failed`, `0 skipped`.

### Criterion B — qualification and repository gates

- Result: PASSED.
- Clean candidate implementation tested: `8245f1c0270e0a314058f2afa77c9f6e80ace483`.
- Fake gate: `37/37` selected rows and `37/37` projections passed, with
  `missing=[]`, no first failure, and zero retries.
- Fake direct dispatches: `26` total — `6` compiler, `12` inference, `8`
  other; inference terminal-valid `12/12`; fake-provider counters agreed.
- Fake cleanup and `logs_secret_free`: PASSED.
- All fake selected rows: `C1.1`–`C1.6`, `C2.1`–`C2.6`, `C3.1`–`C3.4`,
  `C4.1`–`C4.9`, `C5.1`–`C5.3`, and `D1`–`D9`: all `PASSED`.

### Criterion C — exactly one protected matrix

- Result: BLOCKED at the first direct failure; no retry.
- Protected runner status: `BLOCKED`; protected acceptance: not established.
- First runtime failure: `stream_closure_invalid`.
- Fixed context: inference, operation `identity_replay`, phase `codex`,
  ordinal `5`, lifetime `identity`.
- Secondary fixed classes: `observer_readiness_lost`,
  `provider_lifecycle_invalid`, `observer_readiness_lost`.
- Protected budget: 900-second wall bound, 64 observation/dispatch ceiling,
  one active dispatch, 131072-byte response and frame bounds, zero internal
  retries. Observed dispatches before stop: `16`; provider preflight: `2`;
  readiness: `3`.
- Protected lifetime totals: compiler `4/4/4/4` attempted/dispatched/
  responded/completed; inference `7/7/7/6` with `6` terminal-valid; other
  `5/5/5/5`.
- All 29 protected rows were serialized:

  - `C1.1` `MISSING`
  - `C1.2`–`C1.6` `NOT RUN`
  - `C2.1`–`C2.6` `NOT RUN`
  - `C3.1`–`C3.4` `NOT RUN`
  - `C4.1`–`C4.8` `NOT RUN`
  - `C4.9` `PASSED`
  - `C5.1` `NOT RUN`
  - `C5.2` `PASSED`
  - `C5.3` `PASSED`
  - `C5.4` `PASSED`

- Later protected inference: `NOT RUN`; protected retry count: `0`.

### Criterion D — protected host and credential envelope

- Result: PASSED for preservation/cleanup; protected acceptance remains blocked
  by Criterion C.
- `qwen-serving-vision.service`: active/running, MainPID `23961`, start
  `Sun 2026-09-06 18:57:26 CEST`, restarts `0` before and after.
- Port `18020` remained the sole relevant listener; `18021` and `18031` were
  absent after cleanup. Qwen worktree changed-path count remained `7`.
- Process command-line SHA-256 was unchanged:
  `8463567150873445b1aa8ec25b6a90d22fa340227a476ee3c0b56d9598ea0531`.
- Existing fixture configuration remained Qwen3.8-27B W4A16 AutoRound, vLLM
  0.27.1, RTX 3090, context 100000, max sequences 1, one-image limit.
- The active vision credential was read only inside the qualified protected run,
  used in bounded memory, and not printed, hashed, persisted, or placed in
  argv/metadata. Raw content was not retained.
- Protected cleanup: processes, listeners, database, cache, Codex home,
  failure state, and replay state all `PASSED`.

### Criterion E — closure and status boundaries

- Result: PASSED for truthful closure; report status remains `BLOCKED`.
- PR description was updated remotely to the Gateway162 scope and actual
  blocked acceptance state.
- `IMPLEMENTED`: YES.
- `TESTED`: YES — focused, full local, static/package, fake, and one bounded
  protected attempt are evidenced.
- `REAL-E2E ACCEPTED`: NO.
- `CUTOVER ACCEPTED`: NO; installed deployment/cutover/release: `NOT RUN`.
- `MERGED`: NO; coding never merges.
- `RELEASE-READY`: NO.

## Verification

- `PYTHONPATH=/synology/homes/janezp/codex-work/slaif-local-coding:/synology/homes/janezp/codex-work/slaif-local-coding/src SLAIF_GATEWAY_ROOT=/tmp/slaif-gateway-005-an.R9Lqb9 /tmp/slaif-gateway-venv-005-an.THUKHt/bin/python -m pytest -q tests/test_gateway162_validator_factory.py`: PASSED — 8 passed.
- `uv run --frozen pytest -q`: PASSED — 822 passed, 16 skipped; skips are the documented opt-in live tests and env-gated exact-Gateway focused tests in the primary checkout.
- `uv run --frozen ruff check .`: PASSED.
- `uv run --frozen ruff format --check .`: PASSED — 290 files formatted.
- `uv run --frozen mypy src tests`: PASSED — 58 source files.
- `uv lock --check`: PASSED.
- `uv pip check --python .venv/bin/python`: PASSED.
- `uv build --wheel`: PASSED.
- `uv run --frozen python -m compileall -q src tests scripts oap/bin`: PASSED.
- `bash -n oap/bin/*.sh`: PASSED.
- `git diff --check`: PASSED.
- `uv run --frozen python -m json.tool oap/evidence/005-an/index.json`: PASSED.
- Clean-candidate fake command with Gateway162 and Codex 0.149.0: PASSED —
  machine status `COMPLETE`, 37/37 gate.
- One protected command with the same candidate and fake-gate prerequisite:
  BLOCKED — machine status `BLOCKED`, first failure and row dispositions above;
  process exit `0` is the runner's serialized-result convention, not a pass.
- GitHub required check `test` at implementation head `556ca152a589747b5c9adeca3d44de56e61ce08c`: SUCCESS.

## Live model/service evidence

- Endpoint used by the prepared path: existing private vision Qwen at
  `127.0.0.1:18020`; candidate adapter used `127.0.0.1:18031` and was cleaned
  up. No public binding was used.
- The protected matrix reached the exact Gateway162 → Local candidate → existing
  vision-Qwen composition. It stopped at the fixed stream-closure boundary;
  no ownership claim for Gateway, Local, or provider is made.
- Before/after fixture identity, listener, process, and worktree predicates are
  retained in `oap/evidence/005-an/index.json`.

## GitHub CI / required checks

- Implementation/evidence head `556ca152a589747b5c9adeca3d44de56e61ce08c`:
  required `test` check `SUCCESS`; PR remained OPEN/CLEAN.
- All required checks green at report drafting: YES for the implementation head.
- Report-only push may start a new check run; strategy verifies report-head
  checks independently.

## Local setup/dependencies

- Used a clean detached Local worktree at the tested implementation SHA and a
  clean detached Gateway checkout at `5ea38325...`; the primary checkout's
  unrelated empty untracked `Local`, `clean`, and `unchanged` files were never
  staged, deleted, or cleaned.
- Used a task-local Gateway venv with Gateway runtime requirements and
  `openai==2.41.0` for the repository-owned composed runner. Pulled the scoped
  `postgres:16` image once after the initial absence; all rehearsal containers
  and temporary state were removed.
- No protected Qwen checkout, model, vLLM process, systemd unit, credential
  file, Codex profile, firewall, VPN, network binding, or public service was
  changed.

## Documentation

- Updated `TESTING.md` and `docs/SLAIF-GATEWAY-INTEGRATION.md` with current
  Gateway162 facts and the actual blocked acceptance result.
- Added sanitized source-bound evidence at
  `oap/evidence/005-an/index.json`.

## Safety/scope confirmations

- Unrelated files preserved: YES.
- Secrets/raw content in report/evidence: NO.
- Protected 18020/Qwen/Codex fixture changed: NO.
- Required protected rows skipped/not run after first failure: YES, explicitly
  retained as `NOT RUN`; no skipped state is treated as pass.
- Extra objective PR: NO.
- Coding merge/auto-merge: NO.
- Active/order edited: NO.
- Final report commit report-only: YES.

## Known limitations/blockers

- The protected matrix's first direct failure is `stream_closure_invalid` at
  identity replay. Ownership is unresolved; this report does not convert the
  class into a Gateway/provider defect and does not authorize another attempt.
- Protected acceptance, real-E2E acceptance, installed cutover, deployment,
  merge, and release readiness remain unestablished.
- Report-head CI is a post-publication GitHub state for strategic verification,
  not an implementation-head claim in this report.

## Recommended strategic follow-up

- Review the source-bound fake/protected evidence, the fixed first failure, and
  the unchanged-fixture predicates. Strategy decides whether the blocked result
  is sufficient or whether a future same-PR continuation is authorized; coding
  selects no next order and performs no retry.

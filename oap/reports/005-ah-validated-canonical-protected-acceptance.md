# OAP Coding-Agent Report — 005-ah

## Work order

- Identifier: `005-ah`
- Order: `oap/orders/005-ah-validated-canonical-protected-acceptance.md`
- Numeric objective: `005`, validated canonical replay and one bounded protected matrix
- PR mode: `AMENDED_EXISTING_PR`

## Status

BLOCKED

## Executive summary

The Local companion now accepts a validated canonical replay candidate whether
the terminal summary has the same identity or an allowed diagnostic alias.
Terminal-summary identity remains diagnostic and cannot supply replay authority.
Execution mode/provenance, client verification versus Local observation, and
all-lifetime accumulator totals are now explicit. The fresh fake qualification
passed 37/37 outer rows and projections; the healthy synthetic protected case
passed 29/29 and all synthetic failure cases serialized as required.

The single authorized real protected matrix reached the existing vision-Qwen
path and stopped at the first bounded stream failure, `budget_stream_limit_exhausted`.
The protected acceptance gate serialized 29 rows with first failure `C1.1`;
later protected inference was not admitted and no retry was made. Protected
acceptance, cutover, merge, and release readiness are therefore not established.

## Authoritative GitHub state

- Repository: `ulfe-lmi/slaif-local-coding`
- PR: 7, https://github.com/ulfe-lmi/slaif-local-coding/pull/7
- State: OPEN, non-draft; merge state CLEAN at the implementation head
- Base/head: `main` / `oap/005-gateway-ingress-integration`
- Starting remote SHA: `28a3dc1bd137f64f100e16f46fd1f13f4590a5ec`
- Implementation commits pushed before report:
  `056a557de7819a33a81b62570f40e6ec378f5d84`,
  `db26b0919caa69f45e0433af4e9080a264217370`,
  `15bb50b1e5943c37a6451b0757e4b7af8c4a0472`,
  `6c66ab49ff718c42b9dde095f28f835274db83f0`,
  `0e9c3e7b30ef9111ab9cf56ac65cf991891c6f15`
- New PR this round: NO; amended existing PR: YES; merge performed: NO
- Implementation head SHA: `0e9c3e7b30ef9111ab9cf56ac65cf991891c6f15`
- Report publication commit: SELF

## Changes and files

- `scripts/gateway_accounting_rehearsal.py`: canonical-candidate acceptance
  independent of summary identity; actual fake/synthetic-protected/
  real-protected provenance; separate successful client verification and Local
  observation; candidate-only readiness facts; accumulator totals.
- `tests/helpers/acceptance_harness.py`: lifetime-tagged snapshots and explicit
  all-lifetime/lifetime counts.
- `tests/test_gateway_accounting_rehearsal.py` and
  `tests/test_acceptance_harness.py`: same/different canonical-summary
  regressions, authority negatives, provenance, candidate-only, and count tests.
- `TESTING.md`: 005-ah replay, provenance, and evidence contract.
- `oap/evidence/005-ah/`: source-bound fake, synthetic-protected, and real
  protected-stop evidence.
- `oap/active` and the activated order were committed byte-for-byte unchanged.

## Acceptance evidence

### Criterion 1 — canonical replay authority

- PASSED: canonical replay authority requires an available single validated
  candidate and no longer requires `canonical_summary_relation == different`.
- PASSED: same-summary and different-summary focused cases pass; missing
  candidate, summary-only/unowned alias, mismatched scope, and incomplete
  initial-stream cases fail closed.
- PASSED: the fresh fake composed run observed a different canonical/summary
  diagnostic relation, a validated canonical candidate, a complete initial
  stream, and a matching id-less continuation.

### Criterion 2 — fake and synthetic qualification

- PASSED: fresh fake run at tested code
  `6c66ab49ff718c42b9dde095f28f835274db83f0` returned 37/37 acceptance rows
  and 37/37 projections, with no missing result, first failure, or retry.
- PASSED: fake all-lifetime totals were 6 compiler, 12 inference, and 8 other
  dispatches; inference terminal-valid total was 12. Candidate readiness was
  retained separately as one other readiness observation.
- PASSED: Codex client verification was `PASSED`, exit status 0, sentinel and
  command lifecycle successful, and failure origin `success`; Local observation
  status was recorded separately.
- PASSED: ownership negatives for missing call ID, mismatched call ID, and
  wrong key were all 4xx with unchanged provider/accounting state, zero pending
  reservations, and zero duplicate request IDs.
- PASSED: synthetic protected healthy case serialized/passed 29/29 rows;
  observer-failure, combined projection/cleanup-failure, and pre-dispatch
  mapping-dependency cases each serialized all 29 rows with their primary and
  secondary failure classes retained. Oracle availability was false and no
  real protected credential or Qwen access occurred in the synthetic branch.

### Criterion 3 — one real protected matrix and preservation

- BLOCKED: the one authorized real protected command used the exact pinned
  Codex/Gateway/Local path and reached the existing vision-Qwen provider
  boundary. It stopped on `budget_stream_limit_exhausted`; no later protected
  inference was admitted.
- NOT RUN: accepted protected C1–C5 semantic rows after C1.1, protected
  cutover, merge, and release readiness.
- PASSED: the post-run vision service remained active/running at MainPID
  `23961`, start `Sun 2026-09-06 18:57:26 CEST`, zero restarts, port 18020
  listening, and the Qwen worktree retained seven pre-existing changed paths.

## Verification

- `uv run --frozen pytest -q`: PASSED — 799 passed, 8 skipped.
- `uv run --frozen pytest -q tests/test_gateway_accounting_rehearsal.py tests/test_acceptance_harness.py tests/test_transport_observer.py`: PASSED — 244 passed.
- `uv run --frozen ruff check .`: PASSED.
- `uv run --frozen ruff format --check .`: PASSED — 277 files.
- `uv run --frozen mypy src tests`: PASSED — 57 source files.
- `uv run --frozen python -m compileall -q src tests scripts oap/bin`: PASSED.
- `bash -n oap/bin/*.sh`: PASSED.
- `uv lock --check`: PASSED.
- `uv pip check --python .venv/bin/python`: PASSED.
- `uv build --wheel --out-dir <private temporary directory>`: PASSED; wheel boundary contained no `tests/` or `scripts/` members.
- `git diff --check`: PASSED.
- Evidence JSON parsing, source binding, and secret/raw-content scan: PASSED.
- Exact pinned fake rehearsal as UID/EUID 1029: PASSED — 37/37 outer rows,
  canonical/summary different diagnostic, canonical id-less companion,
  ownership negatives, four synthetic protected cases, cleanup, and
  secret-free logs.
- One exact pinned protected rehearsal as UID/EUID 1029: BLOCKED — first
  failure `budget_stream_limit_exhausted`, protected rows serialized, no retry.
- GitHub implementation-head check `test`: PASSED — run `34452777202`, job
  `102792110406`, head `0e9c3e7b30ef9111ab9cf56ac65cf991891c6f15`.

## Live model/service evidence

- Protected route: existing vision `qwen-serving-vision.service` on private
  port 18020, reached through the disposable pinned Gateway and Local candidate
  on development port 18031. The runner performed its counted health/models
  preflight and then stopped at the bounded stream failure.
- No raw credential value, bearer header, model response, prompt, image, tool
  output, call ID, signature, nonce, or private payload was retained.
- Before/after protected facts: vision PID/start/restart count and 18020
  listener remained `23961` / recorded start / `0` / present; Qwen worktree
  changed-path count remained `7`.
- Protected Qwen/vLLM/model/network/firewall/Codex-profile mutation: NO.

## GitHub CI / required checks

- Implementation-head `test`: SUCCESS, run `34452777202`, job
  `102792110406`, head `0e9c3e7b30ef9111ab9cf56ac65cf991891c6f15`.
- All required checks at report drafting: YES.
- Report-head checks may be pending; strategy verifies them independently.

## Local setup/dependencies

- Used the repository `.venv`, a disposable exact Gateway checkout at
  `50dcc3b85d614eb1d0c6196595bf22ef5779f846`, its disposable Python venv,
  exact Codex `0.149.0`, and bounded PostgreSQL 16 loopback/tmpfs Docker state.
- Temporary Gateway, database, candidate, cache, Codex-home, and log state was
  owned by the run and cleaned up. No host package, lockfile, daemon, protected
  service, model, key file, network, or profile was changed.

## Documentation

Updated `TESTING.md` with canonical-summary diagnostic behavior, execution-mode
provenance, client/local observation separation, and all-lifetime evidence.
Generated source-bound evidence is under `oap/evidence/005-ah/`.

## Safety/scope confirmations

- Unrelated work and all immutable prior orders/reports/evidence were preserved.
- Secrets, raw IDs/digests, prompts, source, images, tool output, bodies,
  signatures, nonces, private URLs, and credentials were not committed or
  retained.
- Protected 18020/Qwen/Codex fixture changed: NO.
- Required fake/synthetic checks ran; real protected acceptance is BLOCKED at
  the first bounded stream failure. Live cutover, merge, and release were NOT
  RUN.
- Extra objective PR: NO. Coding merge/acceptance: NO.
- Active/order content edited after activation: NO.
- Final report commit report-only: YES.

## Known limitations/blockers

- The existing protected provider boundary produced a stream exceeding the
  ordered 128 KiB aggregate stream budget. The runner failed closed and did not
  convert transport observation into semantic acceptance.
- Later protected semantic rows were not run and no protected retry or extra
  diagnostic request is authorized by this order.
- Report-head CI may be pending after publication; strategy independently
  verifies its terminal state.

## Recommended strategic follow-up

Review the source-bound 005-ah evidence and the first protected stream-budget
failure. Any provider-observation/budget policy change or another protected
attempt requires a separate strategic order. This report does not establish
protected acceptance, cutover acceptance, merge, or release readiness.

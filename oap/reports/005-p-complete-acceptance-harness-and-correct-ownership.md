# OAP Coding-Agent Report — 005-p

## Work order

- Identifier: `005-p`
- Order: `oap/orders/005-p-complete-acceptance-harness-and-correct-ownership.md`
- Numeric objective: Objective-005
- PR mode: `AMENDED_EXISTING_PR`

## Status

PARTIAL

## Executive summary

Implemented the repository-only Objective-005 acceptance harness correction.
The harness now has one ordered C1–C5/D obligation manifest, bounded request
budgets, independent strict-fake provider lifecycle observations, source/AST-
derived historical gap checks, fail-closed ownership classification, tamper
matrix contracts, and injectable cutover/rollback dry-run tests. The historical
005-o stream result is classified as
`gateway_rejected_stream_owner_unresolved` unless independently valid provider
lifecycle and exact Gateway-validator conflict evidence prove
`gateway_product_defect`.

The exact fake full-chain rehearsal reached the actual Codex stage but stopped
at the first obligation with sanitized `codex_startup` / `exit_1` evidence.
The machine gate therefore reported `missing=[]`, first failure `C1.1`, and
`passed=false`; no fake acceptance or protected inference is claimed.

## Authoritative GitHub state

- Repository: `ulfe-lmi/slaif-local-coding`
- PR: #7 — https://github.com/ulfe-lmi/slaif-local-coding/pull/7
- PR state: OPEN, non-draft, MERGEABLE/CLEAN
- Base/head: `main` / `oap/005-gateway-ingress-integration`
- Starting remote SHA: `c8b978c72c635ef2c80997c6b91f7ce2ccfdadb1`
- Implementation head SHA: 2b0b4dc1caa5c1a8f2b6e6130f04a5f403e71712
- Report publication commit: SELF
- Implementation commits pushed before report: `2b0b4dc1`
- New PR this round: NO
- Amended existing PR: YES, PR #7
- Merge performed: NO

## Changes and files

- Added `tests/helpers/acceptance_harness.py` with the fixed C1–C5/D manifest,
  request budgets, safe fact schema, gap inventory, provider-boundary ledger,
  tamper matrix, and fake cutover runner.
- Extended `scripts/gateway_accounting_rehearsal.py` to use the exact Codex
  0.149.0 checksum gate, strict fake-provider observations, real Codex-before-
  stream ordering, machine obligation gating, and protected-mode refusal for
  this no-protected-inference order.
- Corrected stream ownership in
  `tests/helpers/gateway_accounting_rehearsal.py`; circular ledger/status
  proxies no longer establish Gateway product ownership.
- Isolated Codex test HOME/TMPDIR for text and vision repository-only runners.
- Added focused harness/ownership tests and `py.typed` for the mypy gate.
- Updated `TESTING.md` and `docs/SLAIF-GATEWAY-INTEGRATION.md` with the
  permanent harness command, boundary, credential non-use, and unresolved
  005-o ownership state.
- Committed the activated `005-p` order and selector unchanged.

## Acceptance evidence

### Criterion A — source-derived gap inventory

- PASSED — Ten activated pre-fix gap IDs are derived from source/AST signals;
  all ten are resolved after the implementation. Test:
  `tests/test_acceptance_harness.py::test_gap_inventory_is_source_derived_and_all_historical_signals_are_resolved`.

### Criterion B — permanent bounded orchestrator contract

- PASSED — Ordered C1–C5/D manifest, stable IDs, dependencies, evidence keys,
  closed status/relationship/count/timing vocabularies, zero-retry request
  budgets, missing-obligation gate, strict fake observations, and injectable
  cutover runner are tested.
- PASSED — Package boundary contains no repository-only `tests/` or `scripts/`
  payload.

### Criterion C — fake full-chain acceptance

- BLOCKED — The exact clean Gateway preflight passed at
  `9d247e7f3d8fd6a588976840c4657181b7486b81`, but the actual Codex 0.149.0
  full-chain turn exited with status class `1`, diagnostic class
  `codex_startup`, event count class `1`, and incomplete dependency lifecycle.
  No raw stream, body, prompt, tool output, or error text was retained.
- NOT RUN — Later C1–C5 public matrix operations were stopped by the first
  failure as required. The machine gate did not pass.

### Criterion D — ephemeral cutover/rollback readiness

- PASSED — Fake filesystem/service injection covers backup permissions,
  candidate-port refusal, candidate specifications, reverse rollback, absence,
  and injected failure at every phase.
- NOT RUN — No real installation, systemd mutation, Codex profile edit, or
  candidate cutover was performed.

## Verification

- `uv run --frozen pytest -q`: PASSED — 594 passed, 8 skipped. Skips are
  existing host/live-gated tests; they are not reported as passes.
- `uv run --frozen pytest -q tests/test_acceptance_harness.py tests/test_gateway_accounting_rehearsal.py tests/test_e2e.py tests/test_vision_e2e.py`: PASSED — 207 passed, 1 skipped.
- `uv run --frozen ruff format --check .`: PASSED — 239 files formatted.
- `uv run --frozen ruff check .`: PASSED.
- `uv run --frozen mypy`: PASSED — 19 source files, no issues.
- `uv run --frozen python -m compileall -q scripts tests/helpers src`: PASSED.
- `bash -n oap/bin/*.sh`: PASSED.
- `uv build --wheel --sdist`: PASSED.
- Wheel package-boundary scan: PASSED — no `tests/` or `scripts/` members.
- `git diff --check`: PASSED.
- Active-code stale Gateway-pin scan: PASSED — zero files.
- Historical Objective-155 hook scan: PASSED — zero active support files.
- Raw-log policy scan with anchored `print`/`logger` patterns: PASSED — zero
  matches.
- Exact Gateway/Codex tool-envelope preflight: PASSED — four bounded variants,
  exact Gateway SHA, Codex 0.149.0.
- Exact fake full-chain orchestrator: BLOCKED — first machine obligation C1.1,
  as described above.

## Live model/service evidence

- Read-only protected service snapshot: PASSED — vision unit active/running,
  PID `23961`, start `Sun 2026-09-06 18:57:26 CEST`, zero restarts, port 18020
  listener present.
- Protected text service state: PASSED — text service remained inactive.
- Protected checkout preservation: PASSED — seven pre-existing worktree entries
  remained; their contents were not inspected.
- Protected authenticated health, models, inference, and vision traffic:
  NOT RUN — explicitly prohibited by 005-p; no protected credential was read.
- Fake task cleanup snapshot: PASSED — ports 18030/18031 free and permitted
  read-only Docker check found zero `slaif-005` task containers.

## GitHub CI / required checks

- Implementation-head `test`: SUCCESS — run `34052153138`, job
  `101537566237`.
- All required checks green at drafting: YES.
- Report-head checks may be pending after publication; strategy verifies the
  new current head.

## Local setup/dependencies

- Used the existing frozen Local environment and temporary detached Gateway
  checkout at the exact required SHA.
- Installed `openai` only into the temporary Gateway rehearsal environment;
  no repository dependency or lockfile changed.
- Used the installed task-controlled Codex 0.149.0 binary with verified
  SHA-256 `bbc3341e44c9ead340ed9570c17be936e37870f570751a941699ffd04d672827`.
- Used temporary synthetic PostgreSQL/fake-Qwen/adapter/Gateway state only;
  no durable service state was changed.

## Documentation

Updated `TESTING.md` and `docs/SLAIF-GATEWAY-INTEGRATION.md` to document the
permanent harness command, fake/protected boundary, credential non-use, machine
gate, and unresolved 005-o ownership. No Gateway production documentation or
semantics were changed.

## Lifecycle state at publication

| State | Result |
| --- | --- |
| `IMPLEMENTED` | yes — harness and gates are implemented |
| `TESTED` | repository checks passed; exact fake chain blocked at C1.1 |
| `REAL-E2E ACCEPTED` | no |
| `CUTOVER ACCEPTED` | no |
| `MERGED` | no |
| `RELEASE-READY` | no |

## Safety/scope confirmations

- Unrelated files: preserved; only order-scoped harness, ownership, tests,
  typing marker, and documentation paths changed.
- Secrets/raw content: no credentials, raw prompts, source, images, tool
  output, request/response bodies, private endpoints, or arbitrary errors were
  committed, logged, or reported.
- Protected 18020/Qwen/Codex fixture changed: NO.
- Protected credential read: NO.
- Protected authenticated/model/inference/vision calls: NO.
- Required fake C1–C5 matrix after C1.1: NOT RUN because the first-failure gate
  stopped it.
- Real cutover/rollback: NOT RUN; only injected fake runner tests ran.
- Extra objective PR: NO.
- Coding merge/auto-merge: NO.
- Active/order edited by coding: NO; activated bytes were committed unchanged.
- Final report commit report-only: YES.

## Known limitations/blockers

- The exact fake full-chain Codex 0.149.0 invocation exits before a tool
  lifecycle is observed. The report deliberately records only fixed diagnostic
  classes; the raw diagnostic is unavailable by design.
- Because C1.1 is the first failure, later fake matrix obligations are
  `NOT RUN`, not pass claims. Protected real acceptance and cutover remain
  unauthorized and unperformed.

## Recommended strategic follow-up

Review the sanitized Codex/Gateway startup blocker and decide whether a new
same-PR continuation is authorized. Re-run the machine-gated fake C1–C5 matrix
only after that blocker is resolved; do not infer protected acceptance from
this partial round.

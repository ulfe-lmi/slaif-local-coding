# OAP Coding-Agent Report — 004-i

## Work order
- Identifier: `004-i`
- Work-order file: `oap/orders/004-i-localize-sandbox-not-found.md`
- Numeric objective: `004`
- PR mode: `AMENDED_EXISTING_PR`

## Status
PARTIAL

## Executive summary

Added a bounded no-model differential matrix that tests fixed `/bin/true`,
`/bin/pwd`, and dependency-read helpers in a stopping order, with an optional
private repo-scratch control only after system-temporary root mapping is proven.
The live 004-i run stopped after one `/bin/true` helper call: local executable
facts were present/regular/executable/non-symlink, while the corrected
`:workspace` helper returned fixed `not_found`/`not_found` evidence. The
deterministic localization is `helper_executable_mapping_failure`. No fixture
correction or governed model call was authorized; completeness remains 35% and
branch readiness remains ~78%.

## Authoritative GitHub state
- Repository: `ulfe-lmi/slaif-local-coding`
- PR number/URL/state: #6, `https://github.com/ulfe-lmi/slaif-local-coding/pull/6`, OPEN, non-draft, MERGEABLE-CLEAN
- Base/head: `main` / `oap/004-real-codex-governed-e2e`
- Starting remote SHA: `1f125fd3255a8911414392a7d692f049720556f5`
- Implementation head SHA: `e176d235d75b2ba956b65af33470dd1a6c89c49f`
- Report publication commit: SELF
- Implementation commits pushed before report: `e176d235d75b2ba956b65af33470dd1a6c89c49f` (`OAP 004-i: localize sandbox helper mapping`)
- New PR this round: NO
- Amended existing PR: YES
- Merge performed: NO

## Changes and files
- `src/slaif_local_coding/e2e.py`: added sanitized executable/root/target probe facts, the bounded differential decision table, private scratch ownership/cleanup, and the conditional governed-run gate.
- `tests/test_e2e.py`: covered every localization outcome, stopping/call bounds, scratch cleanup, and model gating on exact helper byte identity.
- `README.md`: documented the matrix, privacy bounds, exact localization classes, and the 004-i portability result.
- `oap/COMPLETENESS.md`: recorded the truthful 004-i result without raising completeness.
- `oap/active` and `oap/orders/004-i-localize-sandbox-not-found.md`: committed unchanged activated strategic bytes.

## Acceptance evidence

### Criterion 1
- PASSED. Codex CLI `0.149.0` was discovered. The fixed local `/bin/true` facts were exists=true, regular=true, executable=true, symlink=false, resolved-basename class=expected. The helper ran in a `system_tmp` root class and returned process exit 1 with first meaningful stderr class/subclass `not_found`/`not_found`.

### Criterion 2
- PASSED. The live matrix made exactly one no-model helper call and stopped immediately after the executable-mapping failure. `/bin/pwd`, dependency `cat`, and repo-scratch probes were not run. No shell wrapper, network, model, adapter, sudo, raw output, or diagnostic text was retained.

### Criterion 3
- NOT APPLICABLE. The system-temporary result was an executable-mapping failure, not an isolated system-temporary root-mapping failure. No fixture-location correction was made; no scratch residue remained.

### Criterion 4
- PASSED for the failure gate. Governed Codex invocations: 0. Candidate adapter invocations: 0. Protected upstream model calls: 0. Exact `:workspace` dependency byte identity was not obtained, so the governed gate remained closed.

### Criterion 5
- PASSED. Focused tests cover the decision table, stopping, fixed bounds, privacy facts, caller-owned scratch mode/cleanup, classification, and exact-byte model gating.

### Criterion 6
- PASSED. README and completeness documentation state the actual helper-executable localization, unchanged completeness/readiness, and portability limitation. No host repair or broader sandbox claim was added.

### Criterion 7
- PASSED at implementation head. All named local gates passed, and GitHub required check `test` passed for the implementation SHA. Report-head checks are pending until this report-only commit is pushed.

## Verification
- `uv lock --check`: PASSED — lock is resolved without changes.
- `uv sync --frozen --extra dev`: PASSED — frozen environment checked.
- `uv run --frozen ruff check .`: PASSED.
- `uv run --frozen ruff format --check .`: PASSED — 115 files already formatted.
- `uv run --frozen mypy src tests`: PASSED — no issues in 35 source files.
- `uv run --frozen pytest tests/test_e2e.py -q -k 'sandbox or diagnostic or direct_dependency_read or failure_diagnosis or command_event'`: PASSED — 24 passed, 21 deselected.
- `uv run --frozen pytest -q`: PASSED — 294 passed, 7 skipped. The seven established opt-in live-service tests remain SKIPPED, not passes.
- `uv build`: PASSED — source distribution and wheel built.
- `python3 -m compileall -q src tests oap/bin`: PASSED.
- `bash -n oap/bin/*.sh`: PASSED.
- `git diff --check`: PASSED.
- Scoped secret/credential/private-path/raw-payload scan: PASSED — zero added matches in the reviewed implementation/documentation diff.
- Scratch-residue check: PASSED — zero `.slaif-codex-sandbox-*` directories remained.
- `uv run --frozen python -c '...run_localized_command_failure_diagnostic...'`: PASSED — one bounded no-model helper call, deterministic `helper_executable_mapping_failure`, zero governed attempts.
- Implementation-head GitHub check `test`: PASSED — SUCCESS on `e176d235d75b2ba956b65af33470dd1a6c89c49f`.

## Live model/service evidence
- Read-only discovery found Codex CLI `0.149.0`, the existing `qwen38-3090` profile marker, and the protected private Qwen/vLLM service on loopback port `18020`; no profile/config bytes were changed.
- Protected before/after snapshot: `qwen-serving` remained active/running, the 18020 listener remained present, bounded `/health` returned HTTP 200 both times, and the sanitized protected-tree hash remained `a15c9c2b7a0977c51ddba0925329f9b94b396ebcff75a537d0591a667677d460`.
- Candidate adapter port `18031` was not started. No live model, vision, tool, compaction, or upstream request ran this round.

## GitHub CI / required checks
- Implementation-head check: `test` — SUCCESS for `e176d235d75b2ba956b65af33470dd1a6c89c49f`.
- All required checks green at drafting: YES.
- Report-head checks: PENDING until this report-only commit is pushed; strategy verifies the final report-head result.

## Local setup / dependencies
- Used the existing repository frozen `uv` environment; no dependency or lock change.
- No sudo action, candidate adapter, model process, or persistent service was started.

## Documentation
- Updated `README.md` and `oap/COMPLETENESS.md` for the differential matrix, privacy bounds, stopping result, and portability limitation.

## Safety/scope confirmations
- Unrelated files changed: NO.
- Secrets, raw prompts/source/tool output/images, credentials, customer data, private paths, and raw diagnostics exposed or committed: NO.
- Protected resources accessed: read-only service/profile discovery and bounded unauthenticated health probe; changed: NO.
- Protected 18020/Qwen/Codex fixture changed: NO.
- Required tests skipped/not run: seven established opt-in live-service tests SKIPPED by default; governed model proof NOT RUN because exact helper bytes were not obtained. No named local gate was skipped.
- Scope deviation: NO.
- Extra objective PR: NO.
- Coding-agent merge/auto-merge: NO.
- Activated order/active edited by coding: NO; unchanged activated bytes committed: YES.
- Report commit report-only: YES.

## Known limitations/blockers
- The installed corrected helper cannot currently map the fixed `/bin/true` probe inside the system-temporary `:workspace` invocation, producing `not_found`/`not_found`. Because this first boundary is proven, root/target mapping and repo-scratch behavior remain untested by the live matrix.
- No governance-derived sentinel success, ordinary-read lifecycle, compaction, vision E2E, production readiness, or cutover readiness is claimed.

## Recommended strategic follow-up
- Review the fixed executable-mapping evidence and decide whether a separately authorized environment/CLI investigation is warranted. Any later governed proof must rerun the bounded matrix and require exact `:workspace` dependency byte identity first.

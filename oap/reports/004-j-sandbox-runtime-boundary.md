# OAP Coding-Agent Report — 004-j

## Work order
- Identifier: `004-j`
- Work-order file: `oap/orders/004-j-sandbox-runtime-boundary.md`
- Numeric objective: `004`
- PR mode: `AMENDED_EXISTING_PR`

## Status
PARTIAL

## Executive summary

Implemented the final bounded sandbox-runtime split. Installed-layout facts
showed Codex CLI `0.149.0`, an existing executable launcher, existing regular
executable bubblewrap, and regular executable `true`/`cat` candidates. The
corrected resolved executable spelling still returned process exit 1 with fixed
`not_found`/`not_found` evidence. The direct fixed bubblewrap probe used a
read-only root view and isolated namespaces and returned process exit 1 with
fixed `sandbox_denied`/`bwrap_loopback_bootstrap` evidence. The deterministic
outcome is `bubblewrap_kernel_runtime_unsupported`.

The matrix made two bounded no-model probe calls: corrected `true`, then direct
bubblewrap. It stopped before dependency `cat`; governed model calls were zero.
No host, package, Codex profile, bubblewrap, Qwen/vLLM, network, or adapter
mutation was performed. Objective-004 completeness remains 35% and branch
readiness remains ~78%.

## Authoritative GitHub state
- Repository: `ulfe-lmi/slaif-local-coding`
- PR number/URL/state: #6, `https://github.com/ulfe-lmi/slaif-local-coding/pull/6`, OPEN, non-draft, MERGEABLE-CLEAN
- Base/head: `main` / `oap/004-real-codex-governed-e2e`
- Starting remote SHA: `499bb6fdbcde0f824eec87c8dda6225eb9874712`
- Implementation head SHA: `c18280b38f0e268562f614e10d17d1a14fead8f7`
- Report publication commit: SELF
- Implementation commits pushed before report: `c18280b38f0e268562f614e10d17d1a14fead8f7` (`OAP 004-j: classify sandbox runtime boundary`)
- New PR this round: NO
- Amended existing PR: YES
- Merge performed: NO

## Changes and files
- `src/slaif_local_coding/e2e.py`: added sanitized installed-layout facts, resolved executable selection, the fixed direct bubblewrap probe, deterministic five-outcome classification, and exact-byte governed-call gating.
- `tests/test_e2e.py`: added decision-table, fixed-argv, stopping-budget, privacy, and model-gate tests.
- `README.md`: documented the final probe budget, privacy boundary, and actual host result.
- `oap/COMPLETENESS.md`: recorded the unchanged completeness/readiness result.
- `oap/active` and `oap/orders/004-j-sandbox-runtime-boundary.md`: committed unchanged activated strategic bytes.

Net implementation impact: `src/slaif_local_coding/e2e.py` +502 lines net;
`tests/test_e2e.py` +233 lines. The growth is limited to the order-specific
facts/probe/decision/gating contract and focused tests; no general diagnostic
framework or speculative branch was retained.

## Acceptance evidence

### Criterion 1
- PASSED. The bounded layout facts recorded Codex launcher exists/regular/executable/symlink=`true/true/true/true`, resolved basename class `expected`, version `0.149.0`; resolved binary directory exists/directory/symlink=`true/true/false`; fixed companion labels were all absent; bubblewrap exists/regular/executable/symlink=`true/true/true/false`; fixed `true` and `cat` candidates were present, regular, executable, non-symlink, and each `bin`/`usr-bin` same-file result was `true`.
- PASSED. The corrected helper probe returned exit `1`, process `failed`, stderr class/subclass `not_found`/`not_found`, stderr length `294`, and stderr SHA-256 `9fb795dc44139478fb02f19e4d237f9beca9e09e673c77eb933a7550ca4cc151`.
- PASSED. The direct bubblewrap probe returned exit `1`, process `failed`, stderr class/subclass `sandbox_denied`/`bwrap_loopback_bootstrap`, stderr length `61`, and stderr SHA-256 `ed3471f7900377f86150471417911309833a36d664cb5af7409e139103f67ddf`.

### Criterion 2
- PASSED. The fixed decision table produced exactly `bubblewrap_kernel_runtime_unsupported`; only bounded lengths, hashes, booleans, statuses, and allowlisted diagnostic classes were retained or reported. Raw paths, argv, environment, stdout/stderr, and private content were not retained.

### Criterion 3
- NOT APPLICABLE to a successful correction. The resolved executable spelling was attempted but did not return dependency bytes; no command-path correction was claimed and no host/package remediation was performed.

### Criterion 4
- PASSED for the failure gate. Corrected helper byte identity was not obtained, dependency `cat` was not run, governed Codex calls were `0`, candidate adapter calls were `0`, and protected model calls were `0`.

### Criterion 5
- PASSED. Focused tests cover all five outcomes, ambiguous/negative decisions, fixed executable argv safety, bounded stopping, privacy facts, and model gating.

### Criterion 6
- PASSED. The existing bounded stream/probe machinery was reused. Production net growth was +502 lines and test growth +233 lines, limited to the required final boundary facts/probe and focused coverage.

### Criterion 7
- PASSED. README and completeness documentation match the external runtime result and preserve the unchanged completeness/readiness claim.

### Criterion 8
- PASSED at implementation head. All named local gates passed and GitHub `test` is SUCCESS for the implementation SHA. Report-head checks are pending until the report-only commit is pushed.

## Verification
- `uv lock --check`: PASSED — lock resolved without changes.
- `uv sync --frozen --extra dev`: PASSED — frozen repository environment checked.
- `uv run --frozen ruff check .`: PASSED.
- `uv run --frozen ruff format --check .`: PASSED — 117 files formatted.
- `uv run --frozen mypy src tests`: PASSED — no issues in 35 source files.
- `uv run --frozen pytest tests/test_e2e.py -q -k 'sandbox_runtime or sandbox_differential or localized_diagnostic or sandbox_probe or sandbox_diagnostic or direct_dependency_read or failure_diagnosis'`: PASSED — 12 passed, 37 deselected.
- `uv run --frozen pytest -q`: PASSED — 298 passed, 7 skipped. Established opt-in live-service tests remain SKIPPED, not passes.
- `uv build`: PASSED — source distribution and wheel built.
- `python3 -m compileall -q src tests oap/bin`: PASSED.
- `bash -n oap/bin/*.sh`: PASSED.
- `git diff --check`: PASSED.
- Scoped secret/credential/private-path/raw-payload scan: PASSED — no added matches.
- Scratch-residue audit: PASSED — no sandbox scratch directories remained.
- Scoped diff/status audit: PASSED — only order-authorized implementation/docs/transcript paths changed before publication.
- `gh pr checks 6 --repo ulfe-lmi/slaif-local-coding`: PASSED — implementation-head `test` SUCCESS.
- Final bounded runtime diagnostic: PASSED — two probe calls, deterministic fixed outcome, zero governed calls.

## Live model/service evidence
- Protected Qwen/vLLM before/after snapshot matched: `qwen-serving` active, loopback 18020 listener present, bounded `/health` HTTP 200, unauthenticated `/v1/models` HTTP 401, service-unit hash `64b3ccd5bdb64da4e3dcabca660fada8155583c96b6bc11de47536e595df5910`, and active Codex-profile hash `fefea020eae48d2f9821694f7f20376e13361d6649759925bfbd4eb8a23ad1fc`.
- Bounded Codex profile/provider discovery found no active local vision-provider selection. No profile bytes were changed. No pre-existing image proxy was assumed or altered.
- Candidate adapter port 18031 was not started. No authenticated model, tool, compiler, vision, compaction, or governed request ran this round.

## GitHub CI / required checks
- Implementation-head check: `test` — SUCCESS for `c18280b38f0e268562f614e10d17d1a14fead8f7`.
- All required checks green at drafting: YES.
- Report-head checks: PENDING until this report-only commit is pushed; strategy verifies the final report-head result.

## Local setup / dependencies
- Used the existing repository-local frozen `uv` environment.
- No dependency, lockfile, package, service, sudo, profile, or host configuration change.
- No candidate adapter or model process was started.

## Documentation
- Updated `README.md` and `oap/COMPLETENESS.md` with the exact probe budget, privacy limits, external boundary, and unchanged completeness/readiness result.

## Safety/scope confirmations
- Unrelated files changed: NO.
- Secrets, raw prompts/source/tool output/images, credentials, private paths, raw diagnostics, and customer data exposed or committed: NO.
- Protected resources changed: NO; read-only service/profile discovery only.
- Protected 18020/Qwen/vLLM/Codex fixture changed: NO.
- Required tests skipped/not run: seven established opt-in live-service tests SKIPPED by default; governed proof NOT RUN because the corrected helper did not return exact dependency bytes. No named local gate was skipped.
- Scope deviation: NO.
- Extra objective PR: NO.
- Coding-agent merge/auto-merge: NO.
- Activated order/active edited by coding: NO; unchanged activated bytes committed: YES.
- Report commit report-only: YES; this file is the sole report-publication change.

## Known limitations/blockers
- The corrected Codex helper still fails before crossing the dependency boundary with fixed `not_found`/`not_found` evidence.
- The independent read-only bubblewrap probe fails during namespace/bootstrap with fixed `sandbox_denied`/`bwrap_loopback_bootstrap` evidence. This is the exact external boundary authorized by 004-j; no repair or portability claim follows.
- No governance-derived sentinel success, successful ordinary-read lifecycle, compaction, vision E2E, production readiness, or cutover readiness is claimed.

## Recommended strategic follow-up
- Review the independently supported `bubblewrap_kernel_runtime_unsupported` boundary and decide whether a separately authorized host/CLI investigation is warranted. Any later governed proof must rerun the bounded final probe and require exact dependency byte identity first.

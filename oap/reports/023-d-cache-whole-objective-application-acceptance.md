# OAP Coding-Agent Report — 023-d

## Work order
- Identifier: 023-d; order path `oap/orders/023-d-cache-whole-objective-application-acceptance.md`; numeric objective 023
- PR mode: AMENDED_EXISTING_PR

## Status
COMPLETE

## Executive summary
The 023 negative-path/stress-test matrix whole-objective application
acceptance is implemented and tested at the actual `create_app` entry point
on opted-in v1 routes (bounded fake-upstream application scope, trusted
synthetic identities, fake main provider and separate tool-free fake
compiler): five new application cases in `tests/test_app.py`
(TestV1BudgetAndForwardedBodyAcceptance) plus the ledger reconciliation
binding the B02/B04 and R01/R03/R05 (and C01/S01/S02) claims to the existing
named cases with the stale fake-application pending language cleared. The
focused class passed five/five; the 18-file app/v1-transaction/observation/
tokenizer/compiler/selection/compile-work/budget/admission/replacement/RAM/
recovery/config regression passed 993/993; ruff, mypy and the docs
consistency check are clean; the fifteen-command locked gate, the
clean-archive both-artifact proof and the fresh Python 3.12.15 noneditable
install all ran at the exact implementation head; all ten GitHub checks at
the implementation head are green. No live inference, no service or Gateway
work, no protected fixture mutation. R04 native compaction and all 024
actual-model/genuine-client/genuine-compaction stages remain NOT RUN.

## Authoritative GitHub state
- Repository: ulfe-lmi/slaif-local-coding; PR #31 https://github.com/ulfe-lmi/slaif-local-coding/pull/31 (OPEN, MERGEABLE, no auto-merge)
- Base: `main` at 4319049d91428b8995e83db82b1736ed36626a12 (the order-verified base)
- Starting remote SHA: 1c6e0c72823c31424dbd9aa1bd5697f176b5fd42 (the 023-c report head)
- Implementation head SHA: e13258328e91bc84cd35cfce05a066f58156c8c3
- Report publication commit: SELF
- Implementation commits pushed before report:
  - 1b82d87a5ca7bf375620409b13eb4463156b53bf (source C: the five 023-d application cases, the ledger reconciliation and scoped architecture documentation, the unchanged activated order and `oap/active`)
  - e13258328e91bc84cd35cfce05a066f58156c8c3 (manifest-only D: the refreshed 318-input development provenance manifest at C)
- Remote verification: `git ls-remote origin refs/heads/oap/023-cache-negative-path-acceptance` = e13258328e91bc84cd35cfce05a066f58156c8c3; `git ls-remote origin refs/heads/main` = 4319049d91428b8995e83db82b1736ed36626a12
- New PR this round: NO; amended existing PR #31: YES; merge performed: NO

## Changes and files
- `tests/test_app.py` (TestV1BudgetAndForwardedBodyAcceptance, five cases):
  B01 both approved configured contexts (262,144 and 32,768) with one- and
  two-file admitted entries and the measured allowances; B03 the oversized-
  source typed refusal before any provider request and the truncated-compile
  typed refusal with the fresh in-process runtime heal; R02 the direct
  forwarded-body preservation evidence on the Responses and Chat endpoints
  (Unicode/CRLF original, process wrapper, retained image, other items).
- `docs/CACHE-REWORK-LEDGER.md`: the affected State cells updated with the
  earned 023-d scope and exact test references (B01, B03, R02 gained the
  earned application evidence; B02, B04, R01, R03, R05 and C01 cleared of
  the stale 023 fake-application pending language and bound to the existing
  named cases; S01/S02 keep the explicit actual-model/genuine-client 024
  qualification; the 023 objective row carries the 023-d clause). Approved
  criterion wording and prior artifacts preserved.
- `ARCHITECTURE.md`: the scoped 023-d status clause in the existing status
  sections (the rework status heading and body lines; the 022/023 status
  spots extended to list 023-d).
- `ARCHITECTURE-for-agents.md`: the 023-d clause in both restated
  objective-boundaries copies (the 023-d whole-objective application
  acceptance scope with the PENDING strategic review qualifier; R04 native
  compaction and the 024 stages kept the mandatory unearned wording).
- `packaging/dev_provenance_manifest.json`: the development provenance
  manifest refreshed at source C (318 inputs; manifest-only child D).
- `oap/orders/023-d-cache-whole-objective-application-acceptance.md`,
  `oap/active`: the unchanged activated order transcript.
- The operator's local `AGENTS.md` wording update remains UNSTAGED and is
  excluded from every commit (governance, not a development source input).

## Acceptance evidence
### Criterion 1 (B01–B04: remaining application budget evidence)
- PASSED at the 023-d fake-upstream application scope.
- B01 — `tests/test_app.py::TestV1BudgetAndForwardedBodyAcceptance::test_b01_both_configured_contexts_measured_allowances_one_and_two_file`: for BOTH approved configured contexts (262,144 → measured 8,192/16,384; 32,768 → measured 1,024/2,048) with one- and two-file admitted entries, the pinned-tokenizer plan's measured allowances are the ACTUAL working-set bounds: the actual compiler demands carry the exact decoded sources, every emitted compiled block counts within its entry's allowance under the real pinned tokenizer, the raw sources are gone from the actual main body, and the transformed-round fixed point holds byte-identical with zero recompile.
- B03 — `tests/test_app.py::TestV1BudgetAndForwardedBodyAcceptance::test_b03_oversized_source_refuses_typed_before_any_compile_attempt`: the oversized source (133 bytes against the 96-byte configured limit) is the fixed typed `v1_compiler_refused` 503 decided inside the compile attempt BEFORE any provider request — zero main forward and ZERO compiler provider requests; the bootstrap generation commits with its bound; the same-epoch repeat re-serves the SAME typed refusal with no retry. `tests/test_app.py::TestV1BudgetAndForwardedBodyAcceptance::test_b03_truncated_compile_refuses_then_heals`: the provider truncation (`finish_reason: "length"`) is typed BEFORE content validation — the fixed typed 503 with zero main forward and exactly ONE compile attempt; the terminal failure is re-served same-epoch with no retry; the recovery is a FRESH app runtime in the SAME Python process over the same recovery root (distinct epoch) completing the SAME request with exactly one successful compile and the byte-identical fixed point — the separate-process restart remains the 023-c evidence; the output-slot half is the existing `test_budget_overflow_refuses_then_heals` (in the passing regression set). No invalid compiled reuse and no silent truncation in either case.
- B02 — tied to the existing final-wire aggregate and whole-entry omission cases at their proven scopes (the 022-e/022-f/022-g fake-upstream application rows and the 021 component budget rows, all in the passing regression set); the ledger row is reconciled to those exact named cases with the stale 023 fake-application pending language cleared. The actual-upstream and 024 halves stay NOT RUN.
- B04 — bound to the existing exact compile-key identity cases (the 021-a identity recipe and the 023-c configuration-mismatch app-boundary case, both in the passing regression set); the ledger row is reconciled to those exact named cases. The actual-model/024 half stays NOT RUN. These configured fake tests do not establish limits of a live model.

### Criterion 2 (R02: direct forwarded-body preservation evidence)
- PASSED at the 023-d fake-upstream application scope on BOTH endpoints.
- `tests/test_app.py::TestV1BudgetAndForwardedBodyAcceptance::test_r02_responses_unicode_crlf_tool_wrapper_image_and_items_preserved`: on the Responses endpoint (the explicit one-image route behavior), the acquired read carrier carries the exact Unicode/CRLF original (`"Synthetic a content.\r\n" + "ünïcode ✓ tail\r\n"`, byte-identical to the pure-transaction fixture) inside its proven process wrapper — the ONLY source span edited (raw original gone from the wire, live marker in, wrapper prefix preserved byte-for-byte); the retained image item and every other input item are dict-equal before/after; the actual compiler demand carries the exact decoded source; the transformed-round resend is the byte-identical fixed point with zero recompile.
- `tests/test_app.py::TestV1BudgetAndForwardedBodyAcceptance::test_r02_chat_unicode_crlf_tool_wrapper_and_image_preserved`: after the Responses bootstrap, the Chat round issues and completes its own read on the Chat endpoint; the root body stays in the preserved user message (root authority is Responses-only, so no absence is asserted there); the acquired read carrier is edited exactly as on Responses (wrapper prefix preserved, only source span replaced); the assistant tool_calls message (tool_call_id only, no name field) and the retained image message are dict-equal; the stable system placement carries both compiled entries; the transformed-round resend is the byte-identical fixed point with zero recompile.

### Criterion 3 (ledger reconciliation and regression)
- PASSED.
- The existing forty D/G/C/B/R/M/S/O entries were reconciled against direct
  named tests, actual upstream-bound bodies and compiler work or typed
  zero-forward evidence: B01/B03/R02 gained the earned 023-d application
  evidence with exact test names; B02/B04/R01/R03/R05 (and C01) had the
  stale "023 fake-application PENDING" language at the start of their State
  cells replaced by the bound-to-existing-named-cases wording (the 021/
  022-d/022-e/022-f/022-g/023-a/023-b/023-c rows at their actual layers);
  S01/S02 keep the explicit actual-model/genuine-client adversarial
  qualification (024) NOT RUN; R04 native compaction stays NOT RUN; the
  approved criterion wording is untouched.
- The required regression set (the 18-file app/v1-transaction/observation/
  tokenizer/compiler/selection/compile-work/budget/admission/replacement/
  RAM/recovery/config set plus the 023-a/023-b/023-c classes inside
  `tests/test_app.py`) passed 993/993, and the full suite in the locked
  gate passed 7179/7179 with the established 28 honest skips — including
  the auth, legacy, image, error, usage, SSE, cancellation, privacy and
  package regressions. Component, fake-application, actual-model, genuine-
  client and genuine-compaction evidence stay distinct.

### Criterion 4 (documentation scope)
- PASSED. Only the existing ledger and the corresponding architecture
  status sections were updated (criterion text and prior artifacts
  preserved); the gates and this report index the evidence. No other
  documentation or in-scope source surface was touched (source C changes
  exactly the five product/test/doc paths plus the unchanged activated
  order/active; D is manifest-only).

## Verification
- `umask 022 && uv run --frozen pytest -q tests/test_app.py::TestV1BudgetAndForwardedBodyAcceptance`: PASSED — 5 passed, exit 0 (log `oap-023d-work/pytest-logs/focused-class-r6.log`)
- `umask 022 && uv run --frozen pytest -q tests/test_app.py`: PASSED — 116 passed, exit 0 (log `oap-023d-work/pytest-logs/test_app-r1.log`)
- `umask 022 && uv run --frozen pytest -q <18-file set: test_app, test_v1_application, test_bundle_{tokenizer,compiler,compile_work,budget,selection,replace,tool_results,read_grammar,root_envelopes,ram_state,ram_work,ram_lifecycle,recovery_codec,recovery_store,recovery_resume}, test_config>`: PASSED — 993 passed (116 + 19 + 17 + 22 + 18 + 34 + 26 + 97 + 84 + 89 + 32 + 145 + 53 + 55 + 52 + 13 + 21 + 100), exit 0 (logs `oap-023d-work/pytest-logs/`)
- `uv run --frozen ruff check .`: PASSED — exit 0 ("All checks passed!")
- `uv run --frozen ruff format --check .`: PASSED — exit 0 (777 files already formatted)
- `uv run --frozen mypy src tests`: PASSED — exit 0 (207 source files, no issues)
- `uv run --frozen python scripts/docs_consistency_check.py`: PASSED — exit 0 (19 claim docs checked)
- Fifteen-command locked gate at exact head e13258328e91bc84cd35cfce05a066f58156c8c3 (parent 1b82d87a5ca7bf375620409b13eb4463156b53bf; fail-closed head/parent/tree guards tolerating exactly the operator's unstaged `M AGENTS.md`, private capture umask 077, ordinary /tmp fixture scratch for the test suite with capacity/inode headroom recorded before start): PASSED — 15/15 commands rc=0 (captures `oap-023d-work/gate-run1/`, summary and per-command `.out`/`.err`):
  1. `uv lock --check`: PASSED
  2. `uv sync --frozen --extra dev`: PASSED
  3. `uv run --frozen ruff check .`: PASSED — "All checks passed!"
  4. `uv run --frozen ruff format --check .`: PASSED — "777 files already formatted"
  5. `uv run --frozen mypy src tests`: PASSED — "Success: no issues found in 207 source files"
  6. `uv run --frozen python scripts/docs_consistency_check.py`: PASSED — "docs consistency: OK (19 claim docs checked)"
  7. `bash -c 'umask 022; uv run --frozen pytest -q'`: PASSED — "7179 passed, 28 skipped, 16 warnings in 1467.91s (0:24:27)"
  8. `uv build`: PASSED — built `slaif_local_coding-0.1.0.tar.gz` and `slaif_local_coding-0.1.0-py3-none-any.whl`
  9. `uv run --frozen python scripts/artifact_policy_check.py --dist dist --inspect`: PASSED — `ok: true`, no violations
  10. `uv run --frozen python scripts/artifact_policy_check.py --dist dist --install-smoke`: PASSED — `ok: true`, no violations
  11. `uv run --frozen python --version`: PASSED — Python 3.12.15
  12. `uv run --frozen python -m compileall -q src tests oap/bin scripts`: PASSED — no errors
  13. `uv run --frozen python scripts/dev_provenance_manifest.py --verify --dist dist`: PASSED — "development provenance OK: state=development head=e13258328e91"
  14. `bash -n` over `oap/bin/*.sh packaging/*.sh`: PASSED — no syntax errors
  15. `git diff --check 4319049d91428b8995e83db82b1736ed36626a12 HEAD`: PASSED — no whitespace errors
- Clean-archive both-artifact build + full artifact proof at the same exact head, with the fresh NONEDITABLE Python 3.12.15 wheel install: PASSED (captures `oap-023d-work/clean-build-023d-r1/`, proof JSON `clean-build-artifact-proof-023d-r1.json`, proof exit 0):
  - clean git archive of D: 39802880 bytes, 972 extracted files, exit 0 (the operator AGENTS.md update is absent from the git tree; only committed bytes were archived)
  - `uv build` on the extracted clean tree: exit 0; wheel sha256 `e82f5ab8b7fa7833e7fbb5734c7612f81f149d2e6a4aae1e53275004437536d3` (4490190 bytes), sdist sha256 `2c8e9efbc0788ee1f99c24efa2915e440c530aa2b2f5745015384a1bc1c609fd` (6282001 bytes) — both byte-identical to the gate `dist/` artifacts and to the manifest-recorded identities
  - fresh noneditable install of the clean-built wheel into a NEW venv created with the explicit Python 3.12 interpreter: exit 0; import probe records module file, version 0.1.0, dist location and Python 3.12.15 (main, Oct 9 2026); console entry point `slaif-local-coding` present
  - artifact proof: ALL PROOF ASSERTIONS PASSED — the 318 manifest inputs verified against source C, against git D and against the clean tree (318/318/318); 972/972 git-D files verified against the clean archive; sdist 316 entries (315 source entries verified + the one generated PKG-INFO); wheel 90 entries (84 runtime entries verified, 6 dist-info, 89 RECORD entries verified); D verified manifest-only with sole parent C (exactly `packaging/dev_provenance_manifest.json` changed); the sdist/manifest reconciliation residuals are exactly the closed documented set (the untracked `.gitignore`; the build-only `.dockerignore`/`Dockerfile`/`compose*.yaml` exclusions)

## Live model/service evidence
- NOT RUN and not required by this order: no live inference, no live vLLM
  call, no service or Gateway work, no new Codex or model-client startup,
  no benchmark. All application evidence is the bounded fake-upstream scope
  (synthetic identity and fixture sources; the real app entry point, the
  actual forwarding, compiles and recovery content reads instrumented).

## GitHub CI / required checks
- Implementation head e13258328e91bc84cd35cfce05a066f58156c8c3, all ten checks observed (checked via the commit check-runs API after the implementation push, before the report commit):
  - `test`: completed / success
  - `docker`: completed / success
  - `docker-published`: completed / success
  - `gateway-contract`: completed / success
  - `operator-session`: completed / success
  - `cache-native-containment`: completed / success
  - `cache-native-fixture`: completed / success
  - `CodeQL`: completed / success
  - `Analyze (python)`: completed / success
  - `Analyze (actions)`: completed / success
- All required green at drafting: yes (10/10 success at the implementation head)
- Report-head checks may be pending; strategy verifies.

## Local setup/dependencies
- No new dependencies. Repository venv, Python 3.12.15 (linked checkout
  `.venv`; the clean-build fresh-venv probe records the explicit 3.12
  interpreter). `uv` frozen installs only.

## Documentation
- Updated in the same PR: `docs/CACHE-REWORK-LEDGER.md` (the affected State
  cells with the earned 023-d scope and exact test references; the stale
  fake-application pending language cleared; approved criterion wording
  preserved), `ARCHITECTURE.md` (the human-facing 023-d status clause in the
  existing status sections), `ARCHITECTURE-for-agents.md` (the 023-d clause
  in both objective-boundaries restated copies).

## Safety/scope confirmations
- Unrelated files: none staged; the operator's local `AGENTS.md` wording
  update preserved UNSTAGED (verified by the gate/build tree guards).
- Secrets/raw content: none committed, printed or captured; all test
  identities, keys and fixture content are synthetic; stage facts are
  content-free (counts, closed outcome names, match booleans).
- Production/protected resources: protected Qwen/18020, networks, profiles
  and keys unchanged; RC10 and earlier orders/reports untouched.
- Required tests skipped/not run: none of the order-required set was
  skipped; the 28 full-suite skips are the suite's established honest skips
  (fixture-conditional live/owner-UID/Docker cases); R04 native compaction
  and the 024 actual-model/genuine-client/genuine-compaction stages remain
  NOT RUN by design (separate required stages).
- Extra objective PR: NO; coding merge: NO; auto-merge: NO.
- Active/order edited: NO (committed as unchanged activated bytes).
- Report commit report-only: yes (verified after push: the commit changes only `oap/reports/023-d-cache-whole-objective-application-acceptance.md`).

## Known limitations/blockers
- Bounded FAKE-UPSTREAM application scope only (synthetic identity and
  fixture sources): R04 native compaction and all 024 actual-model,
  genuine-client and genuine-compaction stages remain NOT RUN in later
  rounds of the same objective.
- The configured fake budget tests do not establish limits of a live model.

## Recommended strategic follow-up
Factual only: the 023-d slice is pending strategic review at its bounded
whole-objective application-acceptance scope; R04 native compaction and the
024 actual-model/genuine-client/genuine-compaction stages are the unearned
continuations of the same objective.

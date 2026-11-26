# OAP Coding-Agent Report — 023-c

## Work order
- Identifier: 023-c; order path `oap/orders/023-c-cache-recovery-resource-concurrency.md`; numeric objective 023
- PR mode: AMENDED_EXISTING_PR

## Status
COMPLETE

## Executive summary
The 023 negative-path/stress-test matrix recovery, resource and concurrency
cases are implemented and tested at the actual `create_app` entry point on
opted-in v1 routes (bounded fake-upstream application scope, trusted synthetic
identities, separate tool-free fake compiler): seven new application cases in
`tests/test_app.py` (TestV1RecoveryResourceConcurrency) plus the bounded
Python-only real-process-boundary restart harness
(`tests/helpers/v1_restart_harness.py`). The focused class passed seven/seven
and the 13-file app/v1-transaction/admission/replacement/selection/
compile-work/recovery/RAM/config regression passed 868/868; ruff, mypy and the
docs consistency check are clean; the fifteen-command locked gate and the
clean-archive both-artifact proof with the fresh Python 3.12.15 noneditable
install ran at the exact implementation head. No live inference, no service or
Gateway work, no protected fixture mutation. The remaining 023 whole-stage
final criterion reconciliation and all 024 actual-model/genuine-client/
genuine-compaction stages remain NOT RUN.

## Authoritative GitHub state
- Repository: ulfe-lmi/slaif-local-coding; PR #31 https://github.com/ulfe-lmi/slaif-local-coding/pull/31 (OPEN, MERGEABLE, no auto-merge)
- Base: `main` at 4319049d91428b8995e83db82b1736ed36626a12 (the order-verified base)
- Starting remote SHA: 3267ffa7f2b89becf6f57f687bc3f4499d28ab1e (the 023-b report head)
- Implementation head SHA: be0b147aa7b5baa1bf8106245a5dc5daf161c5f3
- Report publication commit: SELF
- Implementation commits pushed before report:
  - 13ab010650ea8fc61b8329e9550f1c56214ad20e (source C: the seven 023-c application cases, the restart harness, the scoped architecture/ledger documentation, the unchanged activated order and `oap/active`)
  - be0b147aa7b5baa1bf8106245a5dc5daf161c5f3 (manifest-only D: the refreshed 318-input development provenance manifest at C)
- Remote verification: `git ls-remote origin refs/heads/oap/023-cache-negative-path-acceptance` = be0b147aa7b5baa1bf8106245a5dc5daf161c5f3; `git ls-remote origin refs/heads/main` = 4319049d91428b8995e83db82b1736ed36626a12
- New PR this round: NO; amended existing PR #31: YES; merge performed: NO

## Changes and files
- `tests/test_app.py` (TestV1RecoveryResourceConcurrency, seven cases):
  C03/M04 concurrent identical miss and cancellation/other-session survival;
  M01/M02/O03 real process-boundary restart; M03 five recovery negatives at
  the app boundary (corrupt / torn / unsafe-mode foreign-class / foreign
  record / configuration-mismatch, the last kept separate); M05 bounded RAM
  pressure and explicit teardown; C02 repeated-operand correlation closure;
  S01 shared-store distinct-repository address-scoped closure.
- `tests/helpers/v1_restart_harness.py` (new): the bounded Python-only
  prepare/resume harness over the same protected test store (fake transports
  only; content-free JSON facts; the recovery-content load counted through
  the store's own load seam with the ordinary before/after deltas).
- `ARCHITECTURE.md`, `ARCHITECTURE-for-agents.md`: the scoped 023-c status
  clauses (existing sections and restated objective-boundaries copies only).
- `docs/CACHE-REWORK-LEDGER.md`: the affected State cells (C02, C03, B03,
  B04, M01, M02, M03, M04, M05, S01, O03, the 023 objective row) updated with
  the earned scope and exact test references; approved criterion text
  preserved.
- `packaging/dev_provenance_manifest.json`: the development provenance
  manifest refreshed at source C (318 inputs; manifest-only child D).
- `oap/orders/023-c-cache-recovery-resource-concurrency.md`, `oap/active`:
  the unchanged activated order transcript.
- The operator's local `AGENTS.md` wording update remains UNSTAGED and is
  excluded from every commit (governance, not a development source input).

## Acceptance evidence
### Criterion 1 (C03 and M04: bounded actual concurrency)
- PASSED at the 023-c fake-upstream application scope.
- `tests/test_app.py::TestV1RecoveryResourceConcurrency::test_concurrent_identical_miss_single_flight_and_stable_state`: two concurrent requests over the SAME new miss take ONE actual compiler dispatch (the leader) while the second is the ACTUAL single-flight subscriber (the closed ``joined`` work outcome, zero invocations); both forward the identical transformed body (two live markers, compiled context present, no source on the wire); the session keeps ONE live owner (a second acquire returns the same registered owner) and the same-session publication commits the protected generation exactly once (generation 3, publish bound 3). The later original-carrier request earns the across-request RAM reuse (all represented entries HIT, zero new compile) and the OWN transformed-body resend earns the separate source-absent reinjection fact, both byte-identical fixed points with the compile count frozen at 2.
- `tests/test_app.py::TestV1RecoveryResourceConcurrency::test_concurrent_cancellation_keeps_leader_and_other_session_survives`: the follower cancelled while the shared miss compiles never cancels the leader's live work (dispatch completes, the affected session stays usable with the retained entry, zero recompile); another session survives while the affected session fails (the injected checkpoint `OSError` is the fixed typed `v1_publish_refused` 503 with zero forward) and after the affected session is explicitly closed (the other session's transformed body stays the byte-identical fixed point with zero recompile).
- Existing component tests continue to cover concurrent writer and teardown fences at their own scope (019/020 suites in the regression set, all passing).

### Criterion 2 (M01, M02 and O03: real process-boundary restart)
- PASSED at the 023-c fake-upstream application scope over a REAL process boundary.
- `tests/test_app.py::TestV1RecoveryResourceConcurrency::test_restart_over_same_store_across_real_process_boundary` + `tests/helpers/v1_restart_harness.py`: the bounded Python-only harness prepares MORE THAN ONE persisted session in ONE process (two sessions, generation 3, two forwards and two compiles each); a FRESH process (distinct PID) resumes ONLY the requested session from its trusted address alone (the counted recovery loads all carry the selected address's lineage key — selected-address-only reads). The resuming request carries NO read of the persisted dependency, yet the compiler demand for it is ACTUAL (root + file entry classes in admission order) — the direct new-epoch rebuild (epoch 2). The emitted working set: one root carrier marker, both compiled blocks (the recovered file included), the region present, sources absent from the wire. The normal hit and the source-absent reinjection are SEPARATE request facts with separate closed reuse-class outcomes (`restart_rebuild_new_epoch` then `source_absent_injection`); the ordered zero-work claim is DIRECT — the recovery-content load and compiler counts captured before and after the normal hit are unchanged (zero recovery-source content reads, zero recompile) on the byte-identical fixed point. The previously dormant session's COMPLETE file map is byte-intact across the fresh process (every file compared, including the pointer bytes; no additions, no deletions); only the resumed session's pointer advanced (the committed generation is 5: the resume's epoch-binding publication plus the rebuild's own committed publication; the normal hit publishes nothing within the epoch; pointers across the store are exactly [3, 5]).

### Criterion 3 (M03, M05 and B03/B04 as applicable)
- PASSED at the 023-c fake-upstream application scope.
- M03: `tests/test_app.py::TestV1RecoveryResourceConcurrency::test_corrupt_torn_unsafe_foreign_record_refused_at_app_boundary` — the CORRUPT (single flipped byte), TORN (truncated checkpoint), UNSAFE foreign-class (session directory 0755, mode preserved, never repaired), FOREIGN RECORD (the same address carrying another session's validly committed record — the direct store read stays the closed `namespace_mismatch`) and CONFIGURATION-MISMATCH (the SAME address lineage — identical principal/session/repository/route/model identity — under a CHANGED accepted compiler-policy configuration; the compiler-policy fingerprint is an address field, a genuinely distinct session, never a cross-namespace reuse; the INTACT synthetic checkpoint of the original lineage offered under the changed address) cases are each the fixed typed `v1_resume_refused` 503 with ZERO forward and NO compile, the previously committed store state UNCHANGED and the refusal STABLE (never repairing, moving or rolling back); the configuration-mismatch case mutates neither directory (the offered checkpoint stays exactly where it was; the changed directory's file set is exactly the graft plus the store's writer lock).
- M05: `tests/test_app.py::TestV1RecoveryResourceConcurrency::test_ram_pressure_refused_typed_and_teardown_frees_without_eviction` — with ONE app and ONE RAM registry (the signed-identity fixture driving two distinct sessions), the configured per-session ceiling is the FIXED typed `v1_publish_refused` 503 with zero forward and zero new compile; the committed protected generation and the durable record set are PRESERVED (no eviction, no disk spill, no governance loss, no raw fallback); the ALREADY-RETAINED other session is undisturbed (owned bytes/revision/last publish unchanged; its own transformed body stays the byte-identical fixed point across the refusal with zero recompile); the refusal is stable; the EXPLICIT teardown frees the owned occupancy (released bytes at least both sessions' occupancy; the residue is the structural process metadata, smaller than either session's occupancy; no live owner remains) while both committed protected records load `ok` from the store.
- B03/B04 reused at their proven scope (the 021-a component evidence, all in the regression set): additionally, the 023-c refusal paths consume ZERO compiler channel (zero forward, zero new compile on every refused transition — the closed typed refusal vocabulary never produces a valid entry, hit or retry), and the configuration-mismatch case is the app-boundary identity law (a changed accepted compiler-policy configuration earns no incompatible compiled reuse of a retained record).

### Criterion 4 (C02 and S01 evidence-gap closures)
- PASSED at the 023-c fake-upstream application scope.
- C02: `tests/test_app.py::TestV1RecoveryResourceConcurrency::test_c02_repeated_operand_correlates_to_one_represented_path` — the repeated operand's ACTUAL observation (the two-operand `cat` receipt) correlates directly to its ONE distinct represented path through the ACTUAL same-run admission: the retained entry carries both occurrences of the one normalized path (`member_occurrences == ("docs/B.md", "docs/B.md")`), the reverse member index maps the entry to exactly that one path (no invented second path), and the working set compiles the entry once (the compiled block count of the emitted body).
- S01: `tests/test_app.py::TestV1RecoveryResourceConcurrency::test_s01_distinct_repository_shared_store_address_scoped` — DISTINCT repository identities with IDENTICAL principal/session and fixture bytes across ONE protected test store: each repository compiles its own working set (four compiles total, no cross-repository reuse), the transformed bodies stay distinct under the namespace-bound markers; the fresh lifecycle of repository alpha resumes ONLY its own session address from the shared store (the selected-address-only read — the only successful resume is alpha's; beta's record is never resumed), rebuilds its own working set, and keeps address-scoped reuse on the next request (the hit recompiles nothing and makes no further resume attempt); the dormant repository's committed bytes stay intact byte-for-byte.
- Signed-identity, legacy, image, API/SSE and cancellation regressions are retained at their existing scopes (all in the passing regression set). The separate whole-023 reconciliation and all 024 actual-model/genuine-client/genuine-compaction cases remain required and NOT RUN.

## Verification
- `umask 022 && uv run --frozen pytest -q tests/test_app.py::TestV1RecoveryResourceConcurrency`: PASSED — 7 passed, exit 0 (log `oap-023c-work/pytest-logs/focus_023c_final.log`)
- `umask 022 && uv run --frozen pytest -q <13-file set: test_app, test_v1_application, test_current_admission, test_bundle_replace, test_bundle_selection, test_bundle_compile_work, test_bundle_recovery_{codec,store,resume}, test_bundle_ram_{state,work,lifecycle}, test_config>`: PASSED — 868 passed, exit 0 (log `oap-023c-work/pytest-logs/regress_023c_final.log`)
- `uv run --frozen ruff check .`: PASSED — exit 0
- `uv run --frozen ruff format --check .`: PASSED — exit 0 (775 files already formatted)
- `uv run --frozen mypy src tests`: PASSED — exit 0 (207 source files, no issues)
- `uv run --frozen python scripts/docs_consistency_check.py`: PASSED — exit 0 (19 claim docs checked)
- Fifteen-command locked gate at exact head be0b147aa7b5baa1bf8106245a5dc5daf161c5f3 (parent 13ab010650ea8fc61b8329e9550f1c56214ad20e; fail-closed head/parent/tree guards, private capture umask 077, ordinary /tmp fixture scratch for the test suite, /tmp capacity and inode headroom recorded before start): PASSED — 15/15 commands rc=0 (captures `oap-023c-work/gate-run1/`, summary and per-command `.out`/`.err`):
  1. `uv lock --check`: PASSED
  2. `uv sync --frozen --extra dev`: PASSED
  3. `uv run --frozen ruff check .`: PASSED — "All checks passed!"
  4. `uv run --frozen ruff format --check .`: PASSED — "775 files already formatted"
  5. `uv run --frozen mypy src tests`: PASSED — "Success: no issues found in 207 source files"
  6. `uv run --frozen python scripts/docs_consistency_check.py`: PASSED — "docs consistency: OK (19 claim docs checked)"
  7. `bash -c 'umask 022; uv run --frozen pytest -q'`: PASSED — "7174 passed, 28 skipped, 16 warnings in 1500.73s (0:25:00)"
  8. `uv build`: PASSED — built `slaif_local_coding-0.1.0.tar.gz` and `slaif_local_coding-0.1.0-py3-none-any.whl`
  9. `uv run --frozen python scripts/artifact_policy_check.py --dist dist --inspect`: PASSED — `ok: true`, no violations
  10. `uv run --frozen python scripts/artifact_policy_check.py --dist dist --install-smoke`: PASSED — `ok: true`, no violations
  11. `uv run --frozen python --version`: PASSED — Python 3.12.15
  12. `uv run --frozen python -m compileall -q src tests oap/bin scripts`: PASSED — no errors
  13. `uv run --frozen python scripts/dev_provenance_manifest.py --verify --dist dist`: PASSED — "development provenance OK: state=development head=be0b147aa7b5"
  14. `bash -n` over `oap/bin/*.sh packaging/*.sh`: PASSED — no syntax errors
  15. `git diff --check 4319049d91428b8995e83db82b1736ed36626a12 HEAD`: PASSED — no whitespace errors
- Clean-archive both-artifact build + full artifact proof at the same exact head, with the fresh NONEDITABLE Python 3.12.15 wheel install: PASSED (captures `oap-023c-work/clean-build-023c-r1/`, proof JSON `oap-023c-work/clean-build-artifact-proof-023c-r1.json`, proof exit 0):
  - clean git archive of D: 39720960 bytes, 970 extracted files, exit 0; archive built with the operator AGENTS.md update absent from the git tree (only the committed bytes were archived)
  - `uv build` on the extracted clean tree: exit 0; wheel sha256 `e82f5ab8b7fa7833e7fbb5734c7612f81f149d2e6a4aae1e53275004437536d3`, sdist sha256 `d163fa7f09533b1624651f172948c841712a630d47d2598727d3eb9e91f1bdf4`
  - fresh noneditable install of the clean-built wheel into a NEW venv created with the explicit Python 3.12 interpreter: exit 0; import probe records module file, version 0.1.0, dist location and Python 3.12.15 (main, Oct 9 2026); console entry point `slaif-local-coding` present
  - artifact proof: ALL PROOF ASSERTIONS PASSED — the 318 manifest inputs verified against source C, against git D and against the clean tree (318/318/318); 970/970 git-D files verified against the clean archive; sdist 316 entries (315 source entries verified + the one generated PKG-INFO); wheel 90 entries (84 runtime entries verified, 6 dist-info, 89 RECORD entries verified); manifest-only parent of D verified; the sdist/manifest reconciliation residuals are exactly the closed documented set (the untracked `.gitignore`; the build-only `.dockerignore`/`Dockerfile`/`compose*.yaml` exclusions)

## Live model/service evidence
- NOT RUN and not required by this order: no live inference, no live vLLM
  call, no service or Gateway work, no new Codex or model-client startup, no
  benchmark. All application evidence is the bounded fake-upstream scope
  (synthetic identity and fixture sources; the real app entry point, the
  actual forwarding, compiles and recovery content reads instrumented).

## GitHub CI / required checks
- Implementation head be0b147aa7b5baa1bf8106245a5dc5daf161c5f3, all ten checks observed (checked via the commit check-runs API after the implementation push, before the report commit):
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
- Updated in the same PR: `ARCHITECTURE.md` (the human-facing 023-c status
  clause and section references), `ARCHITECTURE-for-agents.md` (the 023-c
  clause in both objective-boundaries restated copies; the remaining 023
  phrase corrected to the whole-stage reconciliation), `docs/CACHE-REWORK-LEDGER.md`
  (the twelve affected State cells with the earned scope and exact test
  references; approved criterion text preserved).

## Safety/scope confirmations
- Unrelated files: none staged; the operator's local `AGENTS.md` wording
  update preserved UNSTAGED (verified by the gate/build tree guards).
- Secrets/raw content: none committed, printed or captured; all test
  identities, keys and fixture content are synthetic; harness facts are
  content-free (counts, PIDs, closed outcome names, match booleans).
- Production/protected resources: protected Qwen/18020, networks, profiles
  and keys unchanged; RC10 and earlier orders/reports untouched.
- Required tests skipped/not run: none of the order-required set was
  skipped; the 28 full-suite skips are the suite's established honest skips
  (fixture-conditional live/owner-UID/Docker cases); the 024
  actual-model/genuine-client/genuine-compaction stages remain NOT RUN by
  design (separate required stages).
- Extra objective PR: NO; coding merge: NO; auto-merge: NO.
- Active/order edited: NO (committed as unchanged activated bytes).
- Report commit report-only: yes (verified after push: the commit changes only `oap/reports/023-c-cache-recovery-resource-concurrency.md`).

## Known limitations/blockers
- Bounded FAKE-UPSTREAM application scope only (synthetic identity and
  fixture sources): the complete 023 whole-stage final criterion
  reconciliation and all 024 actual-model, genuine-client and genuine-
  compaction stages remain NOT RUN in later rounds of the same objective.
- The genuine client-compaction half of the closed four-way reuse
  distinction remains UN-EARNED (it requires a real client event).

## Recommended strategic follow-up
Factual only: the 023-c slice is pending strategic review at its bounded
application recovery/resource/concurrency scope; the remaining 023
whole-stage final criterion reconciliation and the 024 stages are the
unearned continuations of the same objective.

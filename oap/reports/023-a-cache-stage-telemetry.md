# OAP Coding-Agent Report — 023-a

## Work order
- Identifier: 023-a; order path `oap/orders/023-a-cache-stage-telemetry.md`;
  numeric objective 023
- PR mode: CREATED_NEW_PR

## Status
COMPLETE (at its bounded fake-upstream stage-telemetry scope)

## Executive summary
The 023-a slice implements the approved handoff section 15 stage telemetry and
protected synthetic application evidence at the ACTUAL `create_app` entry point
on opted-in v1 routes. The runtime records owned-stage content-free stage facts
(recognition, complete acquisition, the actual same-run graph, admission,
compilation, replacement, compiled injection, source-absent injection,
recovery, main upstream and the closed four-way reuse class) at each owning
stage from the ACTUAL typed results, with closed per-stage outcome and detail
vocabularies that carry bounded counts only — never values, source,
identifiers, paths, digests or credentials. The closed content-acquisition
facts (complete/partial/unsupported read partition, observed member and
character counts, absolute-path normalization outcome) and the actual
same-run R/F graph facts (honest node-availability partition, edge count,
candidate count) are published through the existing private metrics registry
with fixed labels, with revision/epoch evidence kept out of metric labels.
The actual final-envelope injection token measurements (governance and
request, counted after the stable placement on the emitted final payload) are
histogram samples against the configured aggregate-limit gauge. The
send-boundary main-forward classification records the forward fact at the
call boundary with provider acceptance only on 2xx, keeping transport
errors, refusals and cancellation distinct from acceptance, and the backend
provider usage ledger is independent of client-reported cumulative usage.
The closed distinction between original-present RAM reuse (bound to a real
across-request HIT), source-absent injection, restart-rebuild-new-epoch and
genuine client compaction (closed but UN-EARNED without a real client event)
is recorded from the fixed compiler outcome labels. The protected synthetic
stage evidence is assembled by the TEST HARNESS from its own fake-upstream /
compiler captures under this round's private artifact directory (0700/0600,
O_EXCL + fsync + rename); the runtime adds no raw-content persistence
surface. All evidence in this report is synthetic fixture evidence at the
bounded fake-upstream application scope; the complete 023
negative-path/stress-test matrix and the 024 actual-model / genuine-Codex
qualification remain NOT RUN in later rounds of the same PR and the separate
024 objective respectively. One GitHub `test` check at the initial manifest
head B failed on the runner (the evidence test's host-specific directory
attempt, 1 of 7158 tests); that case is corrected in this round — the
ordinary suite now writes its protected evidence under the test's own pytest
tmp_path root (no host path), the ordered durable synthetic example is
produced by a separate single-case run into a fresh private
project-contained directory, and the nonstream usage observer additionally
shares the ONE existing bounded response decode with the call extraction
with the token counts closed to a finite range (an unsupported usage leaves
the response unchanged and emits no sample) — all re-verified at the
corrected manifest head D, which is this report's implementation head.

## Authoritative GitHub state
- Repository: ulfe-lmi/slaif-local-coding
- PR: #31 https://github.com/ulfe-lmi/slaif-local-coding/pull/31
  (OPEN, non-draft, mergeable; base `main`, head
  `oap/023-cache-negative-path-acceptance`)
- Starting remote SHA (order-verified main, the PR #30 merge):
  4319049d91428b8995e83db82b1736ed36626a12
- Implementation head SHA: b6b7fb77c95fc26c1a464c48907c87fd80bdd3c4
- Report publication commit: SELF
- Implementation commits pushed before report:
  - 12cf017bdadc2fb424a399c99ed4fd628cf63896 (source A: implementation,
    tests, docs)
  - ad31b2f802074b2e9fdbbf4407c155623bbb4ba4 (manifest-only B: the 317-input
    development provenance manifest at A; one GitHub `test` check failed
    here on the runner — the evidence test's host-specific directory)
  - f57c57c0036f3237c928f5108ca244fb544a8725 (source C: the CI-safe
    stage-evidence location and the bounded provider-usage decode
    correction)
  - b6b7fb77c95fc26c1a464c48907c87fd80bdd3c4 (manifest-only D: the refreshed
    317-input development provenance manifest at C; the remote branch head
    before this report)
- New PR this round: yes (#31); amended existing: no; merge performed: NO

## Changes and files
13 distinct paths (one PR, four implementation commits), all in scope of
order 023-a:

- `src/slaif_local_coding/constitution/bundles/v1_telemetry.py` (NEW, 272L):
  the closed `V1Stage` enum (recognition, acquisition, graph, admission,
  compilation, replacement, injection, recovery, main_upstream,
  reuse_class; `client_compaction` closed but UN-EARNED and excluded from
  all outcomes), the closed per-stage outcome/detail vocabularies, the
  frozen content-free `V1StageEvent` (bounded int counts, fixed error text)
  and `V1StageRecorder` (`.events`, `.begin()`, `.record`,
  `.note_compile_dispatch`, `.request_compile_attribution`).
- `src/slaif_local_coding/app.py`: `create_app(..., v1_stage_observer=None)`;
  the 14 metric families (the original 9 plus
  `slaif_v1_acquisition_facts_total{route,kind}`,
  `slaif_v1_graph_facts_total{route,kind}`,
  `slaif_v1_admission_facts_total{route,kind}`,
  `slaif_v1_injection_tokens` histogram `{route,kind}`
  (governance/request) and
  `slaif_v1_injection_aggregate_limit_tokens` gauge `{route}` set once at
  construction from `budget_plan.aggregate`); the send-boundary
  main-forward classification at the actual client-send boundary
  (forwarded at the call boundary with the pre-send timestamp; provider
  acceptance only on 2xx; transport error, refusal and cancellation
  distinct); the provider usage ledger (Responses `input_tokens` /
  `output_tokens`).
- `src/slaif_local_coding/constitution/bundles/v1_application.py`:
  `_acquisition_facts(observation)` (COMPLETE reads with member/span
  counts; PARTIAL/TRUNCATED/MISSING_BODY partial; otherwise unsupported;
  absolute-path normalization outcome) and `_graph_facts(admission)`
  (via the actual `admission.r_result.f_result.overlay`; the closed
  node-availability partition, edge and candidate counts); acquisition
  facts recorded on all three acquisition outcomes; the GRAPH ready fact
  recorded right after actual admission in `prepare_v1_transaction`.
- `tests/test_app.py`: `TestV1StageTelemetry` (7 tests): the main-flow
  3-round stage events and every metric family; the restart / new-epoch
  run with zero recovery content reads; the cold-marker refusal; the
  stream-disconnect cancellation; the provider usage ledger; the
  content-free label negative; the protected synthetic evidence writer
  (0700/0600 under the round's private artifact directory, O_EXCL + fsync
  + rename, assembled from the harness's own captures).
- `tests/test_v1_application.py` (19 tests): the reuse class bound to the
  closed across-request HIT (first compile, original-present RAM hit,
  source-absent injection arms), with the class-level monkeypatch of the
  slotted `BundleCompileWork.resolve_entry` capturing the real resolver
  first.
- `ARCHITECTURE-for-agents.md` + byte-identical mirror
  `oap/strategic-instructions/ARCHITECTURE-for-agents.md`: the 022-a..g
  lineage recorded MERGED to main through PR #30 at
  4319049d91428b8995e83db82b1736ed36626a12 at their reviewed
  fake-upstream scopes; the new 023-a slice paragraph at its PENDING
  strategic-review scope; the 019-c/020 wording untouched.
- `ARCHITECTURE.md` (human-facing): small targeted updates at the current
  rework status, the short 023-a scope statement, the section heading and
  lineage lines; old round wording preserved.
- `docs/CACHE-REWORK-LEDGER.md`: the 022 row recorded merged; the 023 row
  at the 023-a earned scope with the objective branch
  `oap/023-cache-negative-path-acceptance` and the criterion cell
  "negative-path/stress-test matrix".
- `docs/CACHE-IMPLEMENTATION-PLAN.md`: the objective branch label.
- `oap/orders/023-a-cache-stage-telemetry.md` + `oap/active`: the
  activated order and active file committed unchanged (strategic bytes).
- `packaging/dev_provenance_manifest.json` (manifest-only commits B and D):
  the 317-input development provenance manifest, refreshed at source C for
  the corrected head D (wheel
  `a39b42615b51e9588a3b39aa0fe9e2ce69b008b9158692774d9237326b833b74`,
  sdist
  `6651bae58bc544c62add7773fd013935d59adc77e65c5891c80ffeaf424f0542`); the
  initial B manifest (wheel `0fcf131931ec…`, sdist `eb37577c77c4…`) is
  preserved in the B commit.
- `src/slaif_local_coding/constitution/bundles/v1_application.py` +
  `tests/test_app.py` (commit C, the CI correction): the protected
  synthetic stage evidence test writes under the caller-supplied evidence
  root (the ordinary suite the test's own pytest tmp_path root — no host
  path, CI-safe — and the ordered durable synthetic example is produced by
  a separate single-case run supplying a fresh private project-contained
  root, keeping the 0700/0600 O_EXCL + fsync + rename writer mechanics);
  the nonstream usage observer shares the ONE existing bounded response
  decode (the nesting-bounded strict object) with the call extraction
  instead of a raw pre-parse decode, and the provider-usage extraction is
  closed to the finite token-counter range (2^31-1), so an unsupported
  usage (non-integer, missing or out-of-range) leaves the response
  unchanged and emits no usage sample, covered by the extended existing
  fake-upstream usage ledger test (the beyond-range and non-dict cases).

## Acceptance evidence
### Criterion 1 — stage telemetry facts and fixed-label metrics
- Result: PASSED at the fake-upstream application scope.
- Evidence: `tests/test_app.py::TestV1StageTelemetry` verifies the exact
  stage-event sequence and every metric family across a 3-round main flow
  (bootstrap, dependency read, transformed replay), the restart /
  new-epoch run, the cold-marker refusal, and the stream-disconnect
  cancellation; the content-free label negative asserts that no
  revision/epoch/session/value/identifier/path/digest/credential string
  reaches any metric label. The acquisition facts are the closed
  complete/partial/unsupported read partition with observed member and
  character counts and the absolute-path normalization outcome, recorded
  on all three acquisition outcomes; the graph facts are the closed
  honest node-availability partition plus edge and candidate counts from
  the actual same-run R/F result. The main-forward classification is
  asserted at the send boundary (forwarded at the call boundary,
  provider_accepted only on the 2xx response, transport error / refusal /
  cancellation distinct), and the provider usage ledger is asserted
  independent of the client-reported cumulative usage.
### Criterion 2 — the closed four-way reuse distinction
- Result: PASSED at the fake-upstream application scope.
- Evidence: `tests/test_v1_application.py` (19 tests) binds the reuse
  class to the actual fixed compiler outcome labels: the first request
  that compiles is NOT original-present RAM reuse; original-present RAM
  reuse requires a real across-request HIT of the represented ready entry
  (distinct from JOINED and from work completed elsewhere in the same
  request); source-absent injection is earned by ordinary application
  history reduction; restart rebuilding in a new epoch is earned by an
  actual fresh-process resume with zero normal-hit recovery content
  reads; genuine client compaction stays closed and UN-EARNED without a
  real client event (no synthetic compaction is claimed).
### Criterion 3 — actual create_app entry point with fake upstreams
- Result: PASSED at the bounded fake-upstream application scope.
- Evidence: the app-level cases exercise root-only recognition, a
  separate actual complete dependency acquisition and admission, first
  compilation, original-present RAM reuse, source-absent injection,
  replacement, correct compiled delivery, the actual forwarded body, a
  successful session recovery / new-epoch path with normal RAM reuse and
  no recovery content reads, a refusal (cold marker, fixed typed 409 with
  zero new owner/generation/compile/forward) and a disconnect /
  cancellation, showing the actual compiler and main call counts. The
  protected synthetic evidence writer (test harness only) correlates the
  recorded stages with the exact known-synthetic input/output bodies,
  compiler output, spans and token counts under the round's private
  artifact directory (0700/0600, O_EXCL + fsync + rename); the durable
  captures stay in
  `/home/janezp/codex-supervision/slaif-local-coding/work-artifacts/
  oap-023a-work/evidence` and no raw production corpus, no new public
  evidence API, no telemetry path that reads recovery content and no
  source-bearing default logging exist (the content-free label negative
  and the writer-permission controls assert this).
### Criterion 4 — scoped docs at the exact earned state
- Result: PASSED.
- Evidence: both agent architecture maps (with the byte-identical
  strategic mirror) record 022 as merged at the reviewed fake-upstream
  scope and only the 023-a evidence actually earned (PENDING strategic
  review at its bounded stage-telemetry scope); the human-facing
  rework status/heading/lineage carry the same short 023-a statement with
  the old round wording preserved; the stage ledger's 022 row is merged
  and the 023 row carries the objective branch label with the
  "negative-path/stress-test matrix" criterion; the implementation plan's
  objective branch label is updated. The historical orders/reports, RC10
  and the approved handoff bytes are unchanged (no planning or audit
  documents added); `scripts/docs_consistency_check.py` passes on the
  candidate.

## Verification
- The fifteen-command locked gate (the same gate as 022-g, driver patterns
  adjusted to this checkout and the exact source/manifest heads): run 1 at
  manifest head B (ad31b2f) and run 2 at implementation head D (b6b7fb7,
  parent guard f57c57c) — 15/15 rc=0 in each run
  (`gate-run1/summary.txt`, `gate-run2/summary.txt`; the nonzero-grep is
  empty). Every command PASSED (exit 0) in both runs:
  1. `uv lock --check`
  2. `uv sync --frozen --extra dev`
  3. `uv run --frozen ruff check .`
  4. `uv run --frozen ruff format --check .`
  5. `uv run --frozen mypy src tests`
  6. `uv run --frozen python scripts/docs_consistency_check.py`
  7. `bash -c 'umask 022; uv run --frozen pytest -q'` — full suite PASSED in
     both runs: run 1 7158 passed, 28 skipped, 16 warnings in 1491.35s
     (0:24:51); run 2 (at D) 7158 passed, 28 skipped, 16 warnings in
     1408.96s (0:23:28). The pytest child ran under the process-local umask
     022 (driver umask 077) on the ordinary short OS scratch (/tmp tmpfs
     61G, 44G free, 1450418 free inodes, recorded in
     `gate-run2/startup.txt`; no per-run TMPDIR export).
  8. `uv build`
  9. `uv run --frozen python scripts/artifact_policy_check.py --dist dist --inspect`
  10. `uv run --frozen python scripts/artifact_policy_check.py --dist dist --install-smoke`
  11. `uv run --frozen python --version` (Python 3.12.15)
  12. `uv run --frozen python -m compileall -q src tests oap/bin scripts`
  13. `uv run --frozen python scripts/dev_provenance_manifest.py --verify --dist dist`
  14. `bash -c 'set -e; for path in oap/bin/*.sh packaging/*.sh; do bash -n "$path"; done'`
  15. `git diff --check 4319049d91428b8995e83db82b1736ed36626a12 HEAD`
  The tree guard in each run tolerated exactly the one unstaged operator
  `AGENTS.md` wording update.
- Focused order set (`tests/test_app.py tests/test_v1_application.py
  tests/test_bundle_compile_work.py tests/test_bundle_recovery_codec.py
  tests/test_bundle_recovery_store.py tests/test_bundle_recovery_resume.py
  tests/test_config.py`): PASSED — 411 passed, PYTEST_EXIT=0, at manifest
  head B (534.59s), at the C correction working tree (497.89s) and at the
  exact implementation head D (486.37s).
- Exact clean archive build at D (`build-023a-r2.sh`): PASSED — head/parent
  guards at b6b7fb7/f57c57c, `git archive` of the exact D tree, extract and
  `uv build` all exit 0 (exits retained per step).
- BOTH artifact proof at D (`artifact-proof-023a-r2.py`): PASSED — ALL PROOF
  ASSERTIONS PASSED, exit 0: the clean D archive (965 files) byte-verified
  against the git D tree; the 317 manifest source inputs byte-identical to
  both the source commit C (the manifest's generation source) and the D tree;
  the rebuilt wheel and sdist byte-equal the D manifest
  (sha256/size/entry-count) and the repository gate dist/ artifacts; the
  wheel RECORD fully verified (unique rows, per-entry digest and size);
  sdist PKG-INFO, wheel entry points and LICENSE/NOTICE byte-verified; D is
  the manifest-only child of C; and the clean-built wheel installed
  non-editable into a fresh disposable venv created by the explicit Python
  3.12.15 interpreter (module import and console entry-point probe exit 0).
- Ordered durable synthetic stage-evidence example (separate single-case run
  supplying a fresh private project-contained root
  `oap-023a-work/evidence-durable-023a-corrected`): PASSED — 1 passed in
  2.90s; `023-a-stage-telemetry/stage-telemetry.json` (27977 bytes, file
  0600, directory 0700). The initial B-era capture is preserved intact under
  `oap-023a-work/evidence`.

## Live model/service evidence
- NOT RUN — outside the 023-a scope (no live inference, no service,
  profile, credential, network, Gateway, registry, deployment, cutover or
  benchmark work; the order prohibits it).

## GitHub CI / required checks
- Implementation head D (b6b7fb77c95fc26c1a464c48907c87fd80bdd3c4): all ten
  required checks green at drafting — `test`, `docker`, `docker-published`,
  `gateway-contract`, `operator-session`, `cache-native-containment`,
  `cache-native-fixture`, `CodeQL`, `Analyze (actions)` and
  `Analyze (python)`, every one `completed success` (check-runs queried
  2026-11-26 ~04:00 UTC).
- Run history at D (run 45749142042): the initial run had six jobs succeed
  and the `test` job fail 1 of 7158 tests (7157 passed, 28 skipped,
  814.32s) — `tests/test_cache_native_fixture_local.py::
  test_run_id_mismatch_and_malformed_refused`, a pre-existing 017
  fake-native-fixture case untouched by 023-a (no fixture or timeout change
  was made), whose bounded owner-thread abort did not converge on the
  runner. One operator-authorized rerun of ONLY the failed job at the same
  SHA (`gh run rerun 45749142042 --failed`, exit 0); the rerun `test` job
  (check-run 139677896953) completed `success` and the run completed with
  all ten checks green. The failed-run job log is preserved
  (`oap-023a-work/d-test-job-log.txt`).
- Run history at B (ad31b2f): nine of ten checks green; the `test` job
  failed 1 of 7158 tests — `tests/test_app.py::TestV1StageTelemetry::
  test_protected_synthetic_stage_evidence` (the host-specific directory
  attempt on the runner) — corrected in C/D as listed under Changes and
  files; the initial B captures are preserved intact.
- All required green at drafting (at D): yes. The report-only commit may
  trigger fresh checks at the report head; strategy verifies those
  independently.

## Local setup/dependencies
- Linked checkout
  `/home/janezp/codex-supervision/slaif-local-coding/work-artifacts/
  oap-023a-work/checkout` at exact verified main
  4319049d91428b8995e83db82b1736ed36626a12; venv pinned to Python 3.12.15
  (`uv` frozen installs, `--extra dev`); the fresh artifact-proof venv is
  created by the explicit `/home/janezp/.local/bin/python3.12`
  (3.12.15). No repo-local services, no sudo, no new dependencies. The
  full pytest runs under the process-local umask 022 on the ordinary
  short OS scratch (`/tmp`, 44 GiB free and 1450418 free inodes recorded
  at gate startup); durable captures and build artifacts stay in the
  project work-artifact directory (0700/0600).

## Documentation
- Updated in the same PR: both agent architecture maps + byte-identical
  strategic mirror, the human-facing `ARCHITECTURE.md` (small targeted
  updates preserving the old round wording), `docs/CACHE-REWORK-LEDGER.md`
  and `docs/CACHE-IMPLEMENTATION-PLAN.md`, as listed above. Required
  because behavior, observability, tests and operation changed; no new
  planning or audit documents.

## Safety/scope confirmations
- Unrelated files: none — the PR touches only the 13 in-scope paths; the
  operator's local `AGENTS.md` wording update stays UNSTAGED in both
  checkouts and is not a mapped development source input (no gate command
  consumes it; the tree guard tolerates exactly that one modification).
- Secrets/raw content: none — all fixtures are synthetic; the stage facts
  and metric labels are content-free by construction; the protected
  synthetic evidence contains only this round's synthetic fixture bodies
  under 0700/0600 private captures.
- Production/protected resources: none touched.
- Protected 18020/Qwen/Codex fixture changed: NO.
- Required tests skipped/not run: none of the order-required focused,
  gate, clean-build or check items are skipped; the full 023
  negative-path/stress-test matrix and the 024 actual-model /
  genuine-Codex qualification are NOT RUN by design (later rounds of the
  same PR and the separate 024 objective).
- Scope deviation: none.
- Extra objective PR: NO (PR #31 is the single 023 PR).
- Coding merge: NO (no merge, no auto-merge, no acceptance).
- Active/order edited: NO (committed unchanged strategic bytes).
- Report commit report-only: yes (verified after push).

## Known limitations/blockers
- The complete 023 negative-path/stress-test matrix (all D/G/C/B/R/M/S/O
  criteria mapped without substitution at the fake full stack) remains
  NOT RUN — it is the explicit scope of the later 023 rounds on the same
  PR.
- The 024 actual-model and genuine-Codex qualification remains NOT RUN
  (separate objective).
- `client_compaction` stays closed and UN-EARNED: no real client
  compaction event was observed; no claim is made.
- All v1 runtime claims are bounded to the fake-upstream application
  scope (synthetic identity and fixture sources, the real app entry
  point, actual forwarding, compiles and recovery content reads
  instrumented).

## Recommended strategic follow-up
Factual only: the 023-a slice is published at its bounded
stage-telemetry scope for strategic review; the next 023 continuation on
the same PR would be the remaining negative-path/stress-test matrix
rounds, then criterion reconciliation, per the ledger.

## Process qualifications
- The full governing texts were re-read in the required order after every
  native context compaction in this round (AGENTS.md including the §19
  evidence phrasing law, the coding-agent communication protocol, the
  complete 2312-line compact architecture in bounded chunks including the
  recovered truncated window, SECURITY.md, TESTING.md, the exact 023-a
  order, and the applicable contracts: CACHE-REWORK §15 and
  CACHE-IMPLEMENTATION-PLAN).
- All 023-a environment, branch, source, test, commit and artifact work
  ran in the order-designated linked checkout; the primary checkout was
  left untouched.
- The operator design reviews applied during the round are preserved:
  the content-free runtime stage facts with the protected synthetic
  evidence writer kept in the test harness (no raw-content persistence
  surface in the runtime); the reuse class bound to a real across-request
  HIT; the send-boundary forward classification with 2xx-only provider
  acceptance and the pre-send timestamp; the actual final-envelope
  injection measurements (counted after the stable placement, not
  pre-placement estimates); the acquisition/graph/admission/injection
  budget metric families with revision/epoch evidence out of metric
  labels; and the small scoped doc updates preserving the old round
  wording.
- The full pytest uses the ordinary short OS scratch under /tmp (no
  deep per-round TMPDIR — the preserved 022-g cmd07 failure cause is not
  re-run); /tmp capacity and inode headroom were verified and recorded at
  gate startup.
- All negative-path evidence in this report uses the bounded test voice
  of AGENTS §19; the 023 matrix is named "negative-path/stress-test
  matrix" throughout.

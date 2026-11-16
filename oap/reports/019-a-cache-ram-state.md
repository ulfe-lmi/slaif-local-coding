# OAP Coding-Agent Report — 019-a

## Work order
- Identifier: 019-a; order path `oap/orders/019-a-cache-ram-state.md` (committed
  unchanged, SHA-256 d3f897ed9929287a57f5a6990d3fc70c313bffb8c4fbaf4d9f29ab2bd43a7c04);
  numeric objective 019
- PR mode: CREATED_NEW_PR

## Status
COMPLETE

## Executive summary
Implemented the first 019 slice as inert typed modules: a bounded per-session
RAM owner and atomic state store over ACTUAL accepted 018-p/018-t records
(`src/slaif_local_coding/constitution/bundles/ram_state.py` /
`ram_state_models.py`), with complete trusted-namespace binding, one live
owner per namespace, distinct fenced cache epochs, a conservative measured
occupancy recipe (identity-deduplicated retained components; no total-RSS
promise), the mandatory expected-revision commit CAS with lineage-rollback and
same-revision fork fences, atomic process/session ceiling checks with the
fixed typed 503 backpressure contract, the retained historical entry catalog
(supersession retains; a genuinely new compatible revert may reuse, replay
cannot reactivate), explicit teardown, and no disk-backed normal lookup,
TTL/LRU, dormant scan, capacity eviction or source destruction. 50 scoped RAM
tests. The required FINAL 15-command gate at manifest-only B ran all 15
rc0 (full pytest 6558 passed / 28 skipped / 16 warnings in 773.62s). ONE clean
Git-B archive built BOTH artifacts and the strict A/B/input-map/archive/sdist/
wheel/RECORD/metadata/licenses/entrypoint/repo-dist proof passed every
assertion (native 0). All TEN exact required checks are SUCCESS at the
implementation head. The slice is INERT: no async single-flight,
cancellation, recovery, compiler/tokenizer, wire/HTTP integration or v1
runtime work; C03 remains unearned and 020-024 remain mandatory.

## Authoritative GitHub state
- Repository: ulfe-lmi/slaif-local-coding
- PR: #27 https://github.com/ulfe-lmi/slaif-local-coding/pull/27 (OPEN, non-draft)
- Base: `main` c5eb299df822875988867bf34d58de239e82657e; head branch
  `oap/019-cache-ram-state`
- Starting remote SHA: c5eb299df822875988867bf34d58de239e82657e
- Implementation head SHA: c3cfc79398e6e1cd6d3bc847edf0ca8256ceb5f6
- Report publication commit: SELF
- Implementation commits pushed before report:
  5a505f287a59243c254672e640b422b3c0b05c9b (source A v1, 11 paths),
  47c488aa6c797a05c107fb45b57ad1a41446db62 (intermediate manifest-only child,
  later superseded, preserved in history),
  3d3f79c85d6618206d9ea0d22b9fb9b66b80f3da (configuration/plan documentation
  and T contract status; FINAL source A, 3 paths),
  c3cfc79398e6e1cd6d3bc847edf0ca8256ceb5f6 (manifest-only B, sole parent
  3d3f79c, only `packaging/dev_provenance_manifest.json`, 281 inputs)
- New PR this round: yes (#27); amended existing: no; merge performed: NO

## Changes and files
Fifteen tracked paths total (no `git add -A`; `__init__.py` intentionally
unchanged; direct module imports match the later-018 pattern):
- NEW: `src/slaif_local_coding/constitution/bundles/ram_state.py`,
  `src/slaif_local_coding/constitution/bundles/ram_state_models.py`,
  `tests/test_bundle_ram_state.py`, `docs/CACHE-RAM-STATE-CONTRACT.md`
- MODIFIED: `ARCHITECTURE-for-agents.md`,
  `oap/strategic-instructions/ARCHITECTURE-for-agents.md` (three byte-identical
  compact mirrors, supervision mirror written in place preserving
  inode 10638621 / UID 1001 / 0600), `ARCHITECTURE.md`, `TESTING.md`,
  `docs/ADAPTER-CONFIGURATION.md`, `docs/CACHE-IMPLEMENTATION-PLAN.md`,
  `docs/CACHE-REWORK-LEDGER.md`, `docs/CACHE-ROOT-REGION-ADMISSION-CONTRACT.md`
  (status pointed at the actual 018-t decision; no historical report or
  decision altered), `oap/active`,
  `packaging/dev_provenance_manifest.json`
- NEW committed unchanged: `oap/orders/019-a-cache-ram-state.md`

## Acceptance evidence
Bounded store/owner requirements (order sections 1-8) and meaningful
first-slice evidence, exercised by `tests/test_bundle_ram_state.py` (24 test
functions, 50 scoped cases):
1. Small typed inert store over ACTUAL `RootRegionLineageState` /
   `RootRegionLineageNamespace` and ACTUAL `derive_root_region_admission`
   results (`RootRegionAdmissionResult`); complete actual result law re-run
   before commit; no legacy DerivedIndexCache/tmpfs/XDG reuse; inert and
   separate from the active legacy path.
2. Every operation bound to the complete trusted namespace, ONE live owner,
   explicit cache epoch: registry access (acquire/new_owner/get) model-
   validates the complete namespace; owner operations bind the registered
   trusted record by identity; a value-equal foreign copy carrying the
   registered lineage key is refused (`RamStateInputError` at registry access
   and on `admit`; typed `owner_namespace_mismatch` refusal on
   `lookup`/`teardown`); duplicate/multi-worker owner rejected with the
   fixed typed error; distinct fenced epochs (an old epoch is never reused).
3. Retention in memory of original bundle bytes, graph/index/current-version
   state and entry metadata; independent namespaces with identical
   filenames/content isolated; no disk-backed normal lookup, TTL/LRU timer,
   automatic dormant scan, capacity eviction or source destruction.
4. Conservative measured occupancy before commit: actual shallow owned
   objects/containers with referents identity-deduplicated within one owner
   (cross-session sharing never exempts a session); exact/over-limit
   refusals at BOTH session and process ceilings with the fixed typed 503
   contract (`http_status=503`) and existing state fully preserved;
   existing-key retrieval after refusal.
5. MANDATORY `expected_revision` CAS; `stale_state_revision` fence for an
   OLDER genuine P state and for a DISTINCT state object at the SAME retained
   P revision (divergent fork); a short registry critical section with
   rechecks (no lock held across model IO / SSE); genuine concurrent
   race controls (same-namespace single winner; three-owner process
   ceiling race with all retained bases accounted).
6. Explicit teardown frees exactly that namespace's owned state and
   occupancy, fences the old epoch, preserves other owners; no hidden
   expiry or auto-recreation through normal lookup.
7. Stable semantic keys: a genuine unrelated FILE B admission in the SAME
   session/lineage leaves admitted FILE A's content key and retrieval
   unchanged; supersession retains the prior current rows in the retained
   historical catalog by identity (object-identity retention asserted), a
   genuinely new compatible revert may reuse retained v1, replay cannot
   reactivate it.
8. No new dependencies, service, model/GPU/Gateway/native call, tokenizer,
   checkpoint store or adapter activation; the diff is confined to the 15
   paths above.
First-slice evidence: genuine P bootstrap/issuance/observation fixtures for
state transitions (real `_ready_t` bootstrap through public T; the
bootstrap-only scope is labeled as such), real ledger classes and measured
P/Q/F/G local-domain costs, source/currentness transitions composed with 018,
mechanically denied filesystem content IO after setup across repeated actual
lookup/graph/index operations including traversal of the retained overlay
nodes/edges (24 facility traps; a metric flag or RAM-looking pathname is not
claimed as proof). No async single-flight/cancellation claim; no actual
compiler/cache hit; C03 remains unearned until its mechanism and owning
compiler layers pass.

## Verification
All final-gate commands at manifest-only B c3cfc79398e6e1cd6d3bc847edf0ca8256ceb5f6
(driver 0700, outer umask 077, private per-command stdout/stderr and actual
native exits; full pytest as nonroot child umask 022 under the 077 parent;
driver PID 3200386 / birth 339398260 / UID 1001 / umask 0077, source
SHA-256 607848c0654e80255ef99fb9979d12e4e1310502fc117355f9216d9d24b60e24):
- `uv lock --check`: PASSED (rc0)
- `uv sync --frozen --extra dev`: PASSED (rc0)
- `uv run --frozen ruff check .`: PASSED (rc0, all checks passed)
- `uv run --frozen ruff format --check .`: PASSED (rc0, 713 files)
- `uv run --frozen mypy src tests`: PASSED (rc0, 178 source files)
- `uv run --frozen python scripts/docs_consistency_check.py`: PASSED (rc0, 19 claim docs)
- `{ umask 022; uv run --frozen pytest -q; }`: PASSED (rc0) — 6558 passed,
  28 skipped, 16 warnings in 773.62s
- `uv build`: PASSED (rc0)
- `uv run --frozen python scripts/artifact_policy_check.py --dist dist --inspect`: PASSED (rc0)
- `uv run --frozen python scripts/artifact_policy_check.py --dist dist --install-smoke`: PASSED (rc0, fresh non-editable install)
- `uv run --frozen python --version`: Python 3.12.15 (rc0)
- `uv run --frozen python -m compileall -q src tests oap/bin scripts`: PASSED (rc0)
- `uv run --frozen python scripts/dev_provenance_manifest.py --verify --dist dist`: PASSED (rc0, head=c3cfc79398e6)
- `bash -n` over `oap/bin/*.sh packaging/*.sh`: PASSED (rc0)
- `git diff --check c5eb299df822875988867bf34d58de239e82657e HEAD`: PASSED (rc0)
- Clean-B build: ONE git archive of B built BOTH artifacts (rc0; 902 archive
  files; wheel 69 entries; sdist 279 entries); driver startup recorded before
  work (PID 3242832 / birth 339480076 / UID 1001 / umask 0077).
- Strict proof (one direct read-only execution on the same clean artifacts,
  no rebuild; helper 0600, driver 0700, helper startup with actual
  PID/birth/PPID/UID/umask/sourcehash/aware-UTC BEFORE work): ALL ASSERTIONS
  PASSED, native 0 — 902 clean-archive files byte-identical to Git B; 281
  manifest inputs byte-identical to Git A, Git B and the clean tree; B is
  manifest-only (sole parent A, only the manifest changed); 278 sdist source
  entries + 1 generated PKG-INFO (PKG-INFO bytes == wheel METADATA bytes);
  63 wheel runtime entries byte-identical to Git B `src/` + 6 dist-info;
  all 69 wheel RECORD rows covered (68 non-self sha256 digests and sizes
  verified; self row with empty digest AND empty size); entry_points.txt
  equals pyproject `[project.scripts]` (`slaif-local-coding =
  slaif_local_coding.cli:main`); dist-info LICENSE/NOTICE byte-identical to
  Git B; repo gate `dist/` artifacts byte-identical to the clean artifacts.
  Wheel 646871 B SHA-256 23fe9ba98fa4ee833e2df79e7d57feb90730feb2b418be5b480a7e03f60452a3;
  sdist 2250751 B SHA-256 eeaacf5f4afdb5c7fd6829b6f4ee0e7f58800287a24312cf84a82e97a8ba67c6.
- Focused RAM suite (scoped, at the pre-final-docs source state): PASSED 50/50
  (capture `pytest-ram01-v7.out`); earlier v1-v7 scoped captures preserve the
  actual red/repair history (v1 7 failed/23 passed; v2 D-fixture reds;
  v3 28 passed; v4 5 failed/41 passed; v5 5 failed/45 passed; v6/v7 50
  passed with scoped Ruff/format/mypy green).

## Live model/service evidence
NOT RUN. No live model, Gateway, native-fixture or v1-runtime call; no
protected 18020/Qwen/Codex fixture touched; no benchmark or RC work.

## GitHub CI / required checks
At implementation head c3cfc79398e6e1cd6d3bc847edf0ca8256ceb5f6 all TEN
required checks are SUCCESS: test, Analyze (actions), Analyze (python),
CodeQL, gateway-contract, docker, docker-published, operator-session,
cache-native-containment, cache-native-fixture (commit check-runs total 10).
All required green at drafting: yes. The report-head push may trigger fresh
checks; strategy verifies.
Preserved intermediate-head CI facts: at source head
5a505f287a59243c254672e640b422b3c0b05c9b (run 43767151881) the `docker` and
`operator-session` jobs FAILED at the "Build the locked wheel and bind it to
the committed manifest" step with the exact fail-closed message "development
provenance FAILED: current source differs from the development source commit
(extra=['docs/CACHE-RAM-STATE-CONTRACT.md', 'src/slaif_local_coding/
constitution/bundles/ram_state.py', 'src/slaif_local_coding/constitution/
bundles/ram_state_models.py', 'tests/test_bundle_ram_state.py']
altered=['docs/CACHE-REWORK-LEDGER.md']); every later source change requires
a refreshed development manifest" — the expected state-aware binding failure
while the intermediate source head still carried the 018-t development
manifest. At the intermediate manifest head 47c488aa6c797a05c107fb45b57ad1a41446db62
(run 43767367539) all checks were SUCCESS.

## Local setup/dependencies
No new dependencies (uv lock unchanged); repository venv via `uv sync
--frozen --extra dev`; no services started; no sudo actions; scratch/evidence
under `/home/janezp/codex-supervision/slaif-local-coding/work-artifacts/oap-019a-work`
(0700; files 0600; execution helpers 0700 before execution).

## Documentation
Updated in this PR: `docs/CACHE-RAM-STATE-CONTRACT.md` (new; 8 sections),
both architecture maps with their three byte-identical compact mirrors
(supervision inode 10638621 / UID 1001 / 0600 preserved in place), human
`ARCHITECTURE.md`, `TESTING.md`, `docs/ADAPTER-CONFIGURATION.md` (brief inert
component reference; all application settings and profile activation remain
planned), `docs/CACHE-IMPLEMENTATION-PLAN.md` (brief inert slice status;
remainder of 019 and 020-024 explicit), `docs/CACHE-REWORK-LEDGER.md`
(existing stage ledger), and the 018-t contract status pointed at
`S/reviews/018-t-decision.md` (whole-018 accepted/merged recorded at its
exact scope). No planning/audit document added; no historical chronicle
restated. No active/qualified v1 claim.

## Safety/scope confirmations
- Unrelated files: none (15 tracked paths, all in scope; open PR #23 and all
  other branches untouched).
- Secrets/raw content: none in this report or the PR; protected captures
  contain known-synthetic code/test excerpts and are not universally
  content-free (stated, not claimed otherwise).
- Production/protected resources: protected Qwen/vLLM 18020, profiles,
  auth/credentials, network/firewall/VPN/daemon/service boundaries all
  unchanged (NO).
- Required tests skipped/not run: 28 skips by count only (skip identity set
  not independently re-established); live model/native/v1 runtime NOT RUN;
  C03 and all v1 runtime criteria unearned.
- Scope deviations: only the round-directed corrections (configuration/plan
  documentation, T contract status, RAM contract wording corrections); no
  product validation weakened.
- Extra objective PR: NO. Coding merge: NO.
- Active/order edited: NO (order SHA-256 d3f897ed9929287a57f5a6990d3fc70c313bffb8c4fbaf4d9f29ab2bd43a7c04;
  active bytes `019-a` unchanged; both committed verbatim).
- Report commit report-only: verified after push (single changed path).

## Known limitations/blockers
- Inert scope only: no async single-flight, cancellation or pressure closure
  (remaining same-019 work), no recovery (020), no compiler/tokenizer (021),
  no wire/HTTP integration (022), no full-stack or actual-model/genuine-
  Codex qualification (023-024). The occupancy recipe measures committed
  owned-cache occupancy, not total process RSS. Application startup wiring
  is 022, not earned here.
- Preserved process qualifications (evidence kept, nothing backfilled or
  relabeled): the gate3 run at the SUPERSEDED intermediate head 47c488a was
  interrupted on strategy direction — commands 01-06 rc0, command 07
  (full pytest) interrupted mid-run with rc130 (its own partial line
  "3429 passed in 250.81s" is a PARTIAL interrupted result, not a full-suite
  result), command 08 build output present with its exit not recorded by the
  driver, commands 09-15 NOT RUN; that intermediate-head manifest commit and
  the intermediate all-SUCCESS CI run remain truthful history; the
  clean-build helper was drafted for the intermediate head and rewritten
  before its single execution at the final B; the proof helper received two
  pre-first-run read-only-review corrections (aware-UTC helper start time;
  RECORD self-row empty-size assertion) and its final source hash is
  recorded at proof startup; focused-suite v1-v5 reds, the v2 static-capture
  overwrite and the preserved failed exploratory probes
  (probe-validate-v1/v2/v3) are qualifications, not passes.

## Recommended strategic follow-up
Factual: strategic review of the inert 019-a slice (acceptance and any
corrections); then the remaining same-019 stages (single-flight,
cancellation, pressure closure) and 020-024 under the activated order. No
merge, release, deployment or cutover is authorized or performed by this
round.

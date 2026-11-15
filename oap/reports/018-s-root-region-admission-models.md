# OAP Coding-Agent Report — 018-s

## Work order
- Identifier: 018-s; order path `oap/orders/018-s-root-region-admission-models.md`
  (SHA256 8b3dd876cbd613498344995cb0ca34d0b0aeae14cde81f6ad848b483e21d6937);
  numeric objective 018. `oap/active` exact `018-s` (SHA256
  97d2859c817c2e99f064ade12527706e5280cbbb3245b95e35d5ab7a7c67c1e7), committed
  unchanged in source A.
- PR mode: AMENDED_EXISTING_PR (PR 26, branch `oap/018-cache-graph-bundles`,
  base `main`/ffaabf4b4d9ce3a9cb7a48e12ab7d8847999adef). NO NEW PR.

## Status
COMPLETE

## Executive summary
Delivered the bounded region-compatible admission-models slice of objective
018 as a separately versioned INERT MODEL/LOCAL-BOUNDARY data model: new
`src/slaif_local_coding/constitution/bundles/root_region_admission_models.py`
with the public `RootRegionAdmissionEntry` (ROOT_ENTRY/FILE) and
`RootRegionAdmission` admission-parent models, the documented
`root_region_admission_model_scope_key` helper and the typed local
before-work validation-reservation helpers
(`root-region-admission-precharge/v1`: region, root-content,
canonical-metadata, parent-namespace and admission-parent components);
minimal typed PRIVATE factoring in the existing
`root_region_graph_models.py` preserving every old public predicate; the new
contract `docs/CACHE-ROOT-REGION-ADMISSION-MODELS-CONTRACT.md`; and the
112-test permanent suite `tests/test_root_region_admission_models.py`
(A-F matrix). The models carry the ACTUAL retained P state and namespace and
the ACTUAL R result by immutable reference, re-derive the UNCHANGED
canonical 018-c keys at the leaf and the admission parent, recheck the
complete reverse member index, fence the ELEVEN carried bound sets under
closed O(1) gates before any element/set/sort/hash/serializer walk, and
precharge their own closed validation work through a caller-supplied bounded
meter with NO unlimited or default meter. The source-size caps stay the
actual UTF-8 SOURCE SIZE domains; the reservations are WORK meters. This is
NOT the complete region consumer: no public derive function, no operation
result/outcome, no new whole-operation bound set, no runtime wiring; the
FULL-RESULT third parent is explicitly deferred, not claimed. All existing
C/G/H/O/I/P/Q/R public law is unchanged.

## Authoritative GitHub state
- Repository `ulfe-lmi/slaif-local-coding`; PR 26
  https://github.com/ulfe-lmi/slaif-local-coding/pull/26, state OPEN.
- Base `main` ffaabf4b4d9ce3a9cb7a48e12ab7d8847999adef; head branch
  `oap/018-cache-graph-bundles`; starting remote SHA
  c919d18581f0f3359a30dd97271930300a4041f9 (the immutable R SELF).
- Implementation head SHA: 6eeaa1017efca527e2f151278b39de66e1cfca7a
- Report publication commit: SELF
- Implementation commits pushed before report:
  - Source A 628671d1a3e71c47f8c0ff51ffe5248e946b5b81 (sole parent R SELF
    c919d18581f0f3359a30dd97271930300a4041f9), 15 exact paths, 18387
    insertions / 379 deletions, including the exact activated order and
    `oap/active`.
  - Manifest-only B 6eeaa1017efca527e2f151278b39de66e1cfca7a (sole parent A), changing only
    `packaging/dev_provenance_manifest.json` (273 source inputs; wheel
    `slaif_local_coding-0.1.0-py3-none-any.whl` 601368 B, 65 entries,
    SHA256 13288b9ce0fdf6fe37f64a948a1a02d827d51d3186a76b54eec18555ce97ee6d;
    sdist `slaif_local_coding-0.1.0.tar.gz` 2152783 B, 271 entries,
    SHA256 ebc60785052fa20c25dc297d5ebe0e2202e583bb0092297adad780b2154a8e47).
- New PR this round: no; amended existing PR 26: yes; merge performed: NO.

## Changes and files
- NEW `src/slaif_local_coding/constitution/bundles/root_region_admission_models.py`
  (5746 lines): the region-compatible ROOT_ENTRY/FILE entry and
  admission-parent data models, the closed leaf/parent carrying law, the
  stable model configuration scope key recipe, and the five component
  before-work validation-reservation helpers.
- `src/slaif_local_coding/constitution/bundles/root_region_graph_models.py`:
  small typed PRIVATE helper factoring only (old public signatures/schemas/
  defaults/refusal boundaries/versions unchanged).
- NEW `tests/test_root_region_admission_models.py` (11110 lines, 112 tests):
  the durable A-F matrix.
- NEW `docs/CACHE-ROOT-REGION-ADMISSION-MODELS-CONTRACT.md` (587 lines).
- Brief references/status: `docs/CACHE-BUNDLE-ADMISSION-CONTRACT.md`,
  `docs/CACHE-CURRENT-ADMISSION-CONTRACT.md`,
  `docs/CACHE-CURRENT-ROOT-COMPOSITION-CONTRACT.md`,
  `docs/CACHE-ROOT-REGION-GRAPH-CONTRACT.md`,
  `docs/CACHE-REWORK-LEDGER.md`, `TESTING.md`, `ARCHITECTURE.md` (human),
  and the three compact mirrors (repo-root
  `ARCHITECTURE-for-agents.md`, in-repo mirror
  `oap/strategic-instructions/ARCHITECTURE-for-agents.md`, and the
  supervision mirror at its fixed inode 10638621/UID 1001/0600 preserved in
  place; all three byte-equal, SHA256
  63573acbdae5a99dbca32aaf08e8b281894b8f2c8d97830929291a1dc6fe0480, 95245 B).
  The compact gains ONE normative S section per mirror and records R
  ACCEPTED at its bounded inert selected-root source/current-graph scope
  WITH PROCESS QUALIFICATIONS AND EXPLICIT HISTORICAL-REPORT CORRECTIONS by
  the exact R decision; S itself stays PENDING and MODEL/LOCAL-BOUNDARY
  ONLY everywhere; I/J/K/L/M NOT ACCEPTED history untouched.
- `oap/orders/018-s-root-region-admission-models.md` + `oap/active`: exact
  strategic bytes, committed unchanged.

## Acceptance evidence
### Criterion A — genuine positives
- PASSED. Genuine public P bootstrap -> ACTUAL R -> NEW model constructor
  positives, BOTH admission modes and BOTH read endpoints where applicable;
  envelope, whole and region provenance; Unicode NONROOT prefix, CRLF and
  exact empty root; original multi-piece producer/owner/frontier/proof
  identity; unchanged canonical C factories and actual G generic FILE
  assembly for the component data. Separate component assembly is kept
  distinct from the NOT-IMPLEMENTED unified operation in every claim.

### Criterion B — canonical C identity
- PASSED. Same bytes/configuration/semantic namespace via genuine
  envelope/whole/region witnesses give BYTE-IDENTICAL C ROOT_ENTRY keys;
  revision/provenance/NEW model-derivation bounds do not leak into C keys.
  ROOT_ENTRY versus compatible root-bearing FILE rows, member ordering,
  repeated operands/distinct width, lean/proven isolation and greedy
  background represented under actual G component law; wrong reverse-index
  edges, extra/missing/unowned keys, wrong root flags and foreign scoped
  rows refuse with fixed private errors.

### Criterion C — positive-first negatives
- PASSED. Positive first on the SAME fixture, then negative-only
  copy/construct mutations: partial actual source/state/ns/R/C key records,
  variants/versions, all ELEVEN carried bound sets and canonical four,
  booleans/wider/missing fields, stale/coherently rekeyed unsupported tags,
  foreign principal/session/workspace/config, source/member/whole
  digest/length/coordinates, concrete provenance kind/class, original
  owner/piece producer/witness membership, detached same-value extras,
  actual later proof or SAME-root stale graph splices; non-ready Q/R
  evidence is not a ready parent. Retained source/group partition forgeries
  are exercised at leaf AND admission parent; the FULL-RESULT third parent
  is explicitly deferred, not claimed.

### Criterion D — before-target resource controls
- PASSED. Real positive class/serializer/source-walk/owned-encode/hash
  instrumentation (no class replaced by a function); closed count/scalar
  gates proven before traversal; before-work two-phase content reservation
  and metadata/cost-calculation closure at leaf and admission parent;
  exact/one-below component meter crossings refuse BEFORE the actual
  crossing target (e.g. whole-source fast path exact 169 / one-below 168
  with actual slice/join/encode/hash counts 0/0/0/0 at the crossing;
  isolated region exact 148 / 147; region helper exact 210 / 209 with
  helper-frame ord visits 20 and zero completed ord/zero targets at the
  crossing). This is NOT a new public operation's whole-domain proof and NOT
  a zero-allocation claim at full-minimum-minus-one; structurally
  unreachable public domains use truthful constructor controls.

### Criterion E — recorded model-component source/cost outcomes
- PASSED (honestly qualified). `e-record` lines in protected test output
  (`captures/d1m5u18p19-erecords.out`, 34 records, independently reviewed):
  - root_only at the ORIGINAL default `GraphBounds` stage domain
    (`max_work_units` 65536), BOTH modes, READY with labeled component
    costs: 32768 B `{root_content: 131466, canonical_metadata: 24752
    (lean) / 24772 (greedy), file_region_total: 0, parent: 310251 (lean) /
    310309 (greedy)}`; 65536 B `{root_content: 262538, canonical_metadata:
    24752/24772, file_region_total: 0, parent: 539627 (lean) / 539685
    (greedy)}`.
  - mixed_region/no-singleton and multi_dependency_history shapes: the
    ACTUAL G assembly REFUSES the default 65536 stage limit with the fixed
    `admission_work_units_exhausted` component outcome (honest refusal, not
    a manufactured positive), both modes and BOTH endpoints; the positive
    component DATA is recorded under the genuine namespace with the
    EXISTING LEGAL 1048576 stage setting (inside the unchanged original
    hard range, no cap raise), e.g. mixed_region 32768 B responses/lean
    `{root_content: 131466, canonical_metadata: 24772, file_region_total:
    98480, parent: 885589}` with counters `entries_retained=2,
    member_occurrences_charged=3, reverse_association_attempts=3`;
    multi_dependency_history 32768 B responses/lean `{root_content: 131466,
    canonical_metadata: 24772, file_region_total: 98932, parent: 2308663}`
    with `entries_retained=5, member_occurrences_charged=5,
    reverse_association_attempts=5`.
  - 131072 B: honest ACTUAL R-total refusal, `r_outcome=refused,
    usable_source=false`, no positive model component there (root_only
    retains the actual F OK result as nested evidence per the R law).
  - Exact qualification carried: root-only 32/64 KiB works at default
    domains; mixed and multi-history G assembly refuses the default 65536
    stage limit; positive component DATA uses a genuine namespace with the
    existing legal 1048576 stage setting (hard range unchanged); R refuses
    131072. NONE of this is default whole-consumer readiness and NONE is a
    zero-allocation claim. Single source/fixture scale numbers apply only
    to their measured shape.

### Criterion F — data preservation, privacy, purity
- PASSED. Deterministic construction/canonical payload DATA preservation
  with exact original reference retention (identity, not structural
  equality); private ROOT/NONROOT/marker/ID/model/identity canaries absent
  from str/repr/errors of the actual tested S surfaces (admission parent,
  root entry, every FILE entry, every path-association row) on a genuine
  canary-bearing fixture, with carried records rendered by composition under
  their own contracts' repr laws; the closed 24-facility IO trap holds on
  all new public model/helper paths after fixtures/imports; the existing
  C/G/I/H/O/P/Q/R suites and old schemas/recipes/positive/refusal laws are
  unchanged (full-suite regression green in the gate).

## Verification
- Frozen FIFTEEN-command gate, ONE managed foreground run at exact clean B
  6eeaa1017efca527e2f151278b39de66e1cfca7a (`captures/d1m5u19p25-gate/`): all 15 actual exits 0 (gate-summary.json all_zero=true, count=15; shell driver 2630070/birth 334595330/UID 1001/umask 0077 with startup metadata before any command; driver exit 0).
- Command 7 ran the EXACT `uv run --frozen pytest -q` under the required
  nonroot umask-022 test context; the actual pytest process was measured
  from its own /proc status (Uid real, Umask) and /proc stat (ppid,
  starttime) discovered strictly under the known-owned UV task-thread
  children of the launched wrapper (bounded walk; no global /proc
  enumeration; uid-ownership and birth-lifetime checks):
  actual pytest pid 2630237, ppid 2630234 (the known-owned uv wrapper), comm `pytest`, UID 1001 (nonroot), Umask 0022, ordered venv `pytest -q` argv, birth 334595410 >= wrapper birth 334595408, facts_verified=true (g07-pytest-process.json)..
- Full pytest at B: 6386 passed, 28 skipped, 16 warnings in 724.53s; stderr 0.
- Scoped pre-freeze checks (p22, fresh protected captures; scoped to the
  changed files, recorded separately from the broad final gate):
  `uv run --frozen ruff check` + `uv run --frozen ruff format --check` +
  `uv run --frozen mypy` on the TWO changed source files
  (`root_region_admission_models.py`, `root_region_graph_models.py`) all
  exit 0 ("All checks passed!", "2 files already formatted", "Success: no
  issues found in 2 source files"), and
  `uv run --frozen pytest -q tests/test_root_region_admission_models.py`
  112 passed, 16 warnings in 18.32s, exit 0. The broad final gate
  re-covers the whole tree (gate commands 3-5).
- SEPARATE clean-B Git-archive build + full strict proof (dedicated outer
  drivers `clean-build-s1/build.sh` and `clean-build-s1/proof-driver.sh`,
  fresh protected captures `clean-build-s1/`; startup lifetime/sourcehash
  before execution for each; internal archive/extract/build exits and the
  direct proof exit captured unmasked): ONE clean `git archive` of B
  extracted and built BOTH artifacts; the strict proof verified the FULL
  original-A/B/archive/input-map/sdist/wheel/RECORD/metadata/licenses/
  entrypoint/repo-dist chain with actual NEW counts/hashes:
  890 clean-archive files path/byte-verified vs Git B; 273 manifest source inputs verified against original Git A, Git B and the clean tree; 271 sdist entries (270 source byte-verified + 1 generated PKG-INFO byte-equal to wheel METADATA); 65 wheel entries (59 runtime byte-verified vs Git B src/ + 6 dist-info) with 64 non-self RECORD digest/size checks plus the RECORD self row; entry_points.txt exactly equals pyproject [project.scripts]; dist-info LICENSE/NOTICE byte-identical to Git B; repo gate dist/ artifacts byte-identical to the clean artifacts; wheel/sdist byte-equal to the manifest (13288b9ce0fdf6fe37f64a948a1a02d827d51d3186a76b54eec18555ce97ee6d / ebc60785052fa20c25dc297d5ebe0e2202e583bb0092297adad780b2154a8e47)..
- `docs_consistency_check.py`: 19 claim docs checked, exit 0 (p23/p24).
- All TEN current-B checks SUCCESS (test, Analyze (actions), Analyze (python), CodeQL, gateway-contract, docker, docker-published, operator-session, cache-native-containment, cache-native-fixture — all pass) at exact head B, verified via commit check-runs.

## Live model/service evidence
- NOT RUN / not required by this order: no live model call, no 18020 or
  protected fixture contact, no client/profile/service mutation.

## GitHub CI / required checks
- Implementation-head (B) check state: test, Analyze (actions), Analyze (python), CodeQL, gateway-contract, docker, docker-published, operator-session, cache-native-containment, cache-native-fixture — all pass (10/10, no pending/failed/cancelled/missing).
- All required green at drafting: yes (10/10 at B).
- Report-head checks may be pending after the report-only push; strategy
  verifies.

## Local setup/dependencies
- Repo-owned uv venv (frozen), Python 3.12 toolchain; no new dependencies;
  no sudo; no service.
- Gate artifact commands at exact clean B: `uv build` (g08),
  `artifact_policy_check.py --dist dist --inspect` (g09) and
  `--install-smoke` (g10), and `dev_provenance_manifest.py --verify --dist
  dist` (g13). These are the gate's own artifact checks and are NOT the
  order's separate clean-B Git-archive build and full strict proof; that
  separate step ran after the gate under dedicated outer drivers and is
  recorded under Verification.

## Documentation
- Updated: new S contract (fields/recipes/local joins/reservations,
  constructor-versus-derivation authority, deferred full-operation limits);
  C/G/current-root/ROOT-REGION-GRAPH references; ledger objective-018 row;
  TESTING.md 018 list; human ARCHITECTURE.md both enumerations; all three
  compact mirrors (one normative S section each; R recorded ACCEPTED
  bounded WITH PROCESS QUALIFICATIONS AND EXPLICIT HISTORICAL-REPORT
  CORRECTIONS by the exact R decision). S stated MODEL/LOCAL-BOUNDARY ONLY
  and PENDING; the full same-018 consumer, original whole-018 audit and
  019-024 remain mandatory; I/J/K/L/M NOT ACCEPTED history and every unique
  accepted law/qualification preserved.

## Safety/scope confirmations
- Unrelated files: none changed; `git diff --check` clean (gate command 15).
- Secrets/raw content: none in report, logs or captures.
- Protected 18020/Qwen/Codex fixture changed: NO.
- Required tests skipped/not run: the 28 skipped tests are as actually
  reported by pytest at B; no skip identities are inferred beyond the count.
- Scope deviation: none.
- Extra objective PR: NO; coding merge: NO.
- Active/order edited: NO (exact strategic bytes committed in A).
- Report commit report-only: yes (verified at publication).

## Known limitations/blockers
- The slice is MODEL/LOCAL-BOUNDARY ONLY and INERT: no public derivation,
  no whole-operation bound set, no runtime wiring; retaining the actual R
  result by reference is component data, NOT derivation authority.
- The FULL-RESULT third parent is explicitly deferred, not claimed.
- The later same-018 complete consumer must derive ACTUAL R from ACTUAL P in
  its own entire charged operation and independently earn its own
  32768-byte whole-operation readiness, both-parent/full-result joins and
  independent-domain evidence; the original whole-018 G/C/S and
  repair-criteria audit and objectives 019-024 remain mandatory before
  merge. This report ends the round; it is not acceptance.

## Process qualifications
- Historical 2026-11-13 10:48:34Z compaction: the short-tail monitor missed
  that giant compaction record, and the worker window that followed had NO
  fresh required governance reads (all 20 documents incomplete; only 1
  partial fragment; 26 classified source-read commands). Preserved in
  `S/reviews/018-s-post-104834-compaction-refresh-text-audit-v2.json`
  (controlled native 2; the v1 auditor's shlex failure is retained, not
  relabeled). This gap is a process qualification, not retrospectively
  cured by any later refresh.
- Current window: the round continued across a model handoff (a separate
  language model produced the handoff summary) and native compactions; a
  complete fresh core refresh (AGENTS.md re-read in full after the ROOT
  note, protocol, full compact architecture, SECURITY/TESTING, exact
  active/order, R report + decision, S contract) was performed IN THIS
  window before the source edits of this window. Earlier-window
  refresh audits do not cover this instance.
- Preserved failures/overwrites (no label-only reruns): p12 mypy and p13
  pytest-oracle failures (the current corrections were built on them);
  p21 `ruff format --check` exit 1 (fixed at p22) plus the p21/p22 ruff
  stderr filename typo; the d1m5u19s2 driver first-run anchor-count failure
  preserved at `drafts/d1m5u19s2-failed-anchorcount.py`; the ledger C05 row
  still reads "the 018-q root-region currentness query is implemented and
  PENDING" — a pre-existing per-criterion row description OUT of the
  R-recording scope, deliberately preserved as a historical line.
- Initial full diagnostic (before the correct umask-022 test context and
  before the manifest rebind): 4 failed, 6361 passed, 28 skipped in
  753.95s — two 077-context failures (test_cache.py::
  test_untrusted_fallback_is_never_adopted;
  test_cache_native_containment_ci.py::
  test_work_root_direct_symlink_and_preservation) and two stale-manifest
  failures (test_dev_provenance.py::
  test_real_development_state_consistent; test_source_input_binding.py::
  test_real_repo_source_inputs_bound_to_committed_source). Preserved as
  captured (`captures/d1m5u18b-pytest-full.out`); superseded by the later
  correct-context full runs. No reconstruction or label-only rerun.
- The u18h captures include an overwrite: an earlier u18h capture was
  overwritten by a later u18h run at the same name (original bytes not
  retained, not reconstructed, not relabeled).
- Earlier piped diagnostic commands leave the native exit UNKNOWN behind
  the pipeline (e.g. the baseline focused run captured via `pytest 2>&1 |
  tail -4`: summary observed, pytest native exit UNKNOWN, outer 0 from
  tail). Preserved as recorded; not relabeled.
- The separate clean-B archive/proof step carries these qualifications
  (preserved; NOT rerun, rebuilt, chmod'd or backfilled to repair them):
  the proof helper `artifact-proof-s1.py` is 0600 rather than driver 0700
  (the build/proof shell drivers are 0700); the proof helper's own startup
  record lacks an aware-UTC time field (the proof driver's meta carries
  driver_started_utc/driver_finished_utc); and the outer build/proof
  invocation exits were displayed in the native session outputs
  (cleanbuild_outer_exit=0, proof_outer_exit=0) rather than captured in
  separate fresh outer-exit files (the internal archive/extract/build and
  proof exits are in fresh protected .exit files).
- The p25 gate driver/helper v1 was reviewed BEFORE execution and corrected
  (v1 preserved as `-prev-v1`): v1's command-7 helper globally listed
  /proc, queried umask with `os.umask(0)` without restoring it before
  capture creation, read /proc/stat field 3 (pgrp) as if it were the UID,
  lacked its own birth/source-hash startup, sat at 0600 instead of the
  driver 0700, and the gate startup labeled its embedded python PID as the
  shell driver. v2 (this run) records separate truthful shell/helper
  identities with birth/source hash before work, keeps the helper umask
  077 without any umask mutation, measures the actual pytest only through
  bounded known-owned task-thread children (uid-ownership + birth-lifetime
  checks, status Uid/Umask, own comm), and propagates the actual native
  pytest exit.
- All R decision qualifications 1-9 are preserved by reference; the R
  report is IMMUTABLE and was not edited. R is recorded ACCEPTED at its
  bounded inert selected-root source/current-graph scope WITH PROCESS
  QUALIFICATIONS AND EXPLICIT HISTORICAL-REPORT CORRECTIONS by the exact
  R decision; S is MODEL/LOCAL-BOUNDARY ONLY and PENDING; I/J/K/L/M NOT
  ACCEPTED history preserved. No full-consumer/fit claim is made anywhere.

## Recommended strategic follow-up
Factual only: the next bounded same-018 order per the R decision's planned
succession is the actual same-run complete admission/full-result consumer
with BOTH-parent joins and independent 32768-byte whole-consumer evidence,
then the original whole-018 G/C/S/repair-criteria audit; only accepted
whole-018 merge + remote-main verification permits 019-024. Strategy
decides.

Implementation head SHA: 6eeaa1017efca527e2f151278b39de66e1cfca7a
Report publication commit: SELF

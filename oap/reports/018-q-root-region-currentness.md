# OAP Coding-Agent Report — 018-q

## Work order
- Identifier: 018-q; order path `oap/orders/018-q-root-region-currentness.md`
  (SHA256 1626c504c1c56de3ae801e114c704564ff7d1896cc333779a98800d61551bf33);
  numeric objective 018.
- PR mode: AMENDED_EXISTING_PR (PR 26, branch `oap/018-cache-graph-bundles`,
  base `main`).

## Status
COMPLETE

## Executive summary
Delivered the separately versioned PURE root-region currentness derivation
above the accepted P root-region producer: new modules
`root_region_currentness_models` / `root_region_currentness` under
`src/slaif_local_coding/constitution/bundles/` with the public entry
`derive_root_region_currentness(state, ns, bounds=None)`, the new
`cache-root-region-currentness/v1` / `root-region-currentness-policy/v1`
contract, the new `docs/CACHE-ROOT-REGION-CURRENTNESS-CONTRACT.md` and the
170-test permanent suite. After a trusted complete root-bearing observation
whose governing root cannot be established under P source policy, the
derivation stops reporting the known authoritative root as currently usable:
an unresolved maximal root uncertainty (no usable selected source) yields
`root_currentness_unproven`, and an actual known differing-authority conflict
separately yields `root_authority_conflict` — without minting new root
authority, changing P selection or advancing any revision. The derivation
builds the combined frozen partial-order frontier from actual authoritative
P facts and eligible uncertainty occurrences on the SAME actual D state,
uses only actual original frozen parent edges, retains every original
maximal witness in canonical order, restores readiness through a genuine
descendant-of-all or jointly covering compatible maxima (including a
genuine old-bytes revert), and distinguishes unresolved MAXIMAL uncertainty
(which blocks usability) from dominated historical uncertainty (retained,
never permanently blocking). ONE Q outer covers the entire operation while
the actual P phase keeps its independent root-lineage work ceiling through a
typed private adapter that reuses the actual private P namespace
validation, `validate_root_region_lineage_state` and the P selection kernel
once; closed O(1) gates and precharges precede iteration, sorting,
membership and construction. The old H/O/I/P public surfaces are unchanged
and the accepted P core module hashes are byte-identical at B. The slice is
inert and PENDING strategic review at its bounded inert scope: whole 018
remains open (the same-018 consumer round must consume the legitimate new
state into the actual graph/admission) and 019–024 remain mandatory.

## Authoritative GitHub state
- Repository: `ulfe-lmi/slaif-local-coding`; PR 26
  https://github.com/ulfe-lmi/slaif-local-coding/pull/26 (open)
- Base: `main` at ffaabf4b4d9ce3a9cb7a48e12ab7d8847999adef (unchanged)
- Head branch: `oap/018-cache-graph-bundles`
- Starting remote SHA: d3660b41e9447182d8badab062d28ed59af58ec4 (the 018-p
  SELF, verified live via `git ls-remote` and the GitHub API before mutation)
- Implementation head SHA: 66d9b8cd0b9baa72e9f8ef8db43aa4ff950bdc00
- Report publication commit: SELF
- Implementation commits pushed before report:
  1b8122540f0ac80bb74884bad4123ccd3542a0dd (source A, 14 files) and
  66d9b8cd0b9baa72e9f8ef8db43aa4ff950bdc00 (manifest-only B, 1 file)
- New PR this round: no; amended existing PR: yes; merge performed: NO

## Changes and files
15 non-report paths across the two implementation commits (verified by
`git show --name-status`).

Source commit A `1b812254` (14 files, 4666 insertions, 57 deletions):
- NEW `src/slaif_local_coding/constitution/bundles/root_region_currentness_models.py`
  (typed immutable records `RootRegionCurrentnessBounds`,
  `RootRegionUncertaintyWitness`, `RootRegionCurrentnessResult`, closed small
  Q enums, closed O(1) shape/count/scalar fences, fixed non-echoing
  str/repr; MALFORMED `model_copy`/raw-override bounds refuse before any
  serializer visit while valid stricter copies remain legal).
- NEW `src/slaif_local_coding/constitution/bundles/root_region_currentness.py`
  (public `derive_root_region_currentness`; closed six-row evidence and
  exclusion table; combined frozen partial-order frontier over actual frozen
  parent edges only; explicit refusal precedence matching contract §5:
  state O1 fence -> ns O1 foreign fence -> Q bounds validation/default
  domain -> Q outer base -> lineage/history scope -> supported version ->
  actual independent-P namespace reservation/revalidation -> actual P
  validation -> P selection mapped outcomes -> uncertainty assessment; exact
  input state retained by InstanceOf reference on EVERY outcome; one Q outer
  with the actual P phase under its independent ceiling via the typed
  private adapter).
- NEW `tests/test_root_region_currentness.py` (170 collected tests:
  permanent A–F matrix across both read endpoints and both admission modes
  with ORIGINAL GraphRequests — bootstrap/proof/anchor identity, closed
  evidence table rows, frontier/restoration/revert, late opaque and delayed
  arrival, forgery and malformed-join refusals with the actual carried P
  problem, independent P-phase-versus-Q-total budget discrimination with
  measured 40-branch public-P fixtures, preconstruction/target-reaching
  sentinels, inherited retention boundaries, purity/privacy traps and
  non-echoing canaries).
- NEW `docs/CACHE-ROOT-REGION-CURRENTNESS-CONTRACT.md` (exact table,
  authority/currentness distinction, combined frontier and restoration law,
  scope key, actual-field/owner joins, bounds, precharge-before-work order,
  pure API; records the P acceptance with the failed-detached-next-control /
  verified-foreground-replacement qualification once).
- `docs/CACHE-ROOT-REGION-LINEAGE-CONTRACT.md`,
  `docs/CACHE-ROOT-LINEAGE-CONTRACT.md`,
  `docs/CACHE-CURRENT-ROOT-COMPOSITION-CONTRACT.md` (stale P status
  corrected to accepted-with-qualifications; concise Q cross-reference
  added; old public H/O/I/P boundaries retained).
- `docs/CACHE-REWORK-LEDGER.md` (018-p ACCEPTED bounded inert producer with
  process qualifications and exact decision reference; 018-q clause
  PENDING; 018-o residue reconciled; whole 018 open; consumer/019–024
  mandatory).
- `ARCHITECTURE.md`, `TESTING.md` and the compact mirror
  `oap/strategic-instructions/ARCHITECTURE-for-agents.md` plus the root
  `ARCHITECTURE-for-agents.md`: full Q mechanism once, short cross-
  references at repeated sites, maximal-uncertainty-blocks vs dominated-
  retained wording, status paragraph and contract list.
- `oap/orders/018-q-root-region-currentness.md` (activated order, committed
  unchanged) and `oap/active` (018-q).

Manifest-only commit B `66d9b8cd` (1 file):
- `packaging/dev_provenance_manifest.json` regenerated at clean A (266
  inputs), sole parent A.

## Verification
All at exact clean B `66d9b8cd0b9baa72e9f8ef8db43aa4ff950bdc00` unless
stated otherwise.

- Exact FIFTEEN-command gate, ONE managed foreground run: driver
  `driver-q1.sh` (sha256
  5c712af71d903d9cb19984e20e720bd94daf58582c2d34174ddc2d08ccdcb18c, parent
  umask 077; driver 1884873/birth 303242080/UID 1001) -> cmd07 child (uv
  after exec) 1885044/birth 303242161/UID 1001/umask 022 -> actual pytest
  child 1885058/birth 303242165/PPID 1885044/UID 1001/umask 022, the last
  independently measured by ROOT through two known UV threads (1885044 is
  the uv wrapper, not pytest). All 15 literal command exits 0,
  `gate.exit=pass`; pytest reported **6064 passed, 28 skipped in
  724.37s** with 0 stderr bytes (the 018-p suite is unchanged inside this
  total; +170 is the Q suite).
- Eight independent frozen-B pure probe runs, 50 named controls/cases,
  covering the model-contract, actual-frontier, budget/precedence,
  late-opaque-arrival, partial-field boundary, eligible-frontier domain,
  retention-query and substantial-root baseline: actual child exit 0 and
  0 stderr for every run, clean B before and after each run
  (S/reviews/018-q-frozen-probe-runs-v2.json). The first frozen-probe run
  (v1) failed at ROOT-harness import-path setup and is preserved; v2 (with
  per-child PYTHONPATH) is the passing set.
- ONE clean Git B archive built BOTH artifacts: internal archive/extract/
  build step exits each literal 0 and the whole build driver's own outer
  exit literal 0 captured directly with fresh full stdout/stderr (no
  pipeline/tail/tee masking). Wheel
  83a0791677199a17e4dd68268a8839b2d86ea83a5ecd75a4734e5c8498639e2c (516088
  B) and sdist e48017826cd0f9c0e4af7e476e5c7acbc60936b679368e1eb1a55f52f3219637
  (1919059 B).
- Direct strict artifact proof: actual exit 0, stderr 0,
  `ALL PROOF ASSERTIONS PASSED` — 879 Git/archive files, 266 manifest
  inputs verified against Git A, Git B and the clean extracted tree, 264
  sdist entries (263 source + 1 generated PKG-INFO), 62 wheel entries (56
  runtime + 6 dist-info), all 61 non-RECORD rows, metadata, entry points
  and licenses; rebuilt artifacts byte-identical to the manifest and to the
  repo-gate dist.
- Focused checks at the final source A after all documentation
  corrections: ruff check, ruff format --check, mypy src tests (167
  files) and the docs consistency check all exit 0.
- All TEN current-B CI checks completed SUCCESS at B (total_count 10;
  state refreshed immediately before finalization and independently
  verified at S/reviews/018-q-B-CI-allgreen-v1.json): test (completed
  2026-11-11T18:15:45Z), Analyze (actions) 18:04:41Z, Analyze (python)
  18:05:14Z, CodeQL 18:04:35Z, gateway-contract 18:05:57Z, docker
  18:07:21Z, docker-published 18:06:56Z, operator-session 18:06:45Z,
  cache-native-containment 18:06:19Z, cache-native-fixture 18:07:19Z.
- Stable module hashes at B: Q kernel
  197960b80ab220dbb6d27fcd4c933c5f9c6ec5d87581faf5b6b28192c45e4bec, Q
  models 1474b8cf644568f4da7f8877cba52aede6a62174ec42681c162aa84c4aff6898;
  accepted P core unchanged (root_region_lineage.py
  abc917c4ac040980680140c5a884c1d5ae972cdc74de48378bcc65e527627705,
  root_region_lineage_models.py
  e2e1ba381cd2f24aeba4d6b3a470299538ae2e0bae5cca2c04512d27f7c10990).

## Inert scope and no-claims
The new surface is pure data plus one public query: no adapter pipeline,
runtime, compiler, RAM-state, recovery, wire, model, client or CI-client
change; no graph/admission consumption of the new state; no v1 runtime,
deployment, release or cutover claim. P is accepted at its bounded inert
producer scope WITH process qualifications (S/reviews/018-p-decision.md);
this round does not upgrade any earlier status. The whole 018 consumer
round and 019–024 remain open/mandatory.

## Process qualifications
Recorded truthfully; no rerun or rebuild was used to hide any of them.
- File modes: selected manual captures/helpers were initially created with
  broader modes (default-umask shells; patch-tool creations arrive 0664
  because the creating process itself needs umask 077 before first
  creation). Each was restricted 0600 in place preserving bytes/inode, with
  the initial deviation recorded per file; later helper-creating processes
  used umask 077 before creation, and the actual pytest child alone ran
  022. No blanket perfect-discipline claim: independent ROOT before/after
  audits cover the audited captures; remaining captures rely on the worker
  record.
- q26 process discovery: the discovery step USED a GLOBAL
  /proc/[0-9]*/cmdline scan — used, not required or authorized, and outside
  the exact-owned-PID scope; it occurred and is preserved. Prior q26
  PID/birth ownership proof was not independently retained before the
  scan, and complete protocol compliance is not claimed for that step.
  Forward rule for later helpers (record managed handle plus own
  PID/birth/PPID at startup, inspect only known-owned children): the q27
  startup-lifetime evidence is MISSING / not independently retained and is
  stated, not backfilled.
- Gate lineage sampler methodology error: the owned-lineage sampler read
  the nonexistent /proc/<pid>/children (the correct owned-child path is
  /proc/<pid>/task/<tid>/children) and therefore captured only the driver
  level. The actual pytest lifetime was independently measured by ROOT
  through TWO known UV threads (pytest 1885058/birth 303242165/PPID
  1885044/UID 1001/umask 022; S/reviews/018-q-actual-pytest-process-v2.json);
  the initial ROOT main-thread-only child lookup was a distinct qualified
  miss, then corrected. After the sampler miss a bounded owned sleep-2
  path diagnostic (non-pytest evidence) confirmed the top-level path is
  absent; no gate rerun.
- Capture paths and overwrites: q8/q9/q11 reused capture filenames
  (disclosed where mentioned, never relabeled as preserved full
  originals); the q16 helper arrived 0664 and was corrected 0600, and the
  successful recheck overwrote the failed first invocation's out/err (same
  path), so that failed capture is NOT retained; the q42 docs helper had
  THREE versions under one filename — the first two failed at Python parse
  and their bytes are NOT retained (later same-filename overwrites), the
  surviving third is preserved with its own mirror-propagation check
  failure (no damage, no propagation occurred); the /tmp/none task-prefix
  file was verified against the ROOT before-evidence and relocated to
  W18q/meta at 0600 (cross-filesystem copy, devices 43 -> 2304); its
  pre-creation path state is UNKNOWN and its original event time is UNKNOWN
  (a handwritten future-dated timestamp was corrected to programmatic
  capture time).
- q8 budget-recheck probe: the FIRST invocation failed and its original
  captures were overwritten by the later successful recheck (same
  filenames), so the retained q8 out/err/json reflect the successful
  recheck and the first q8 failure class is not independently retained
  (UNKNOWN).
- Preserved 018-q focused-run outcomes (mixed results kept, never rerun to
  erase): q3/q4 model self-check harness failures (a premature ALL MODEL
  SELF-CHECKS PASSED header printed before a failing assertion; a
  model_copy unexpected-max_diagnostics TypeError); q11 16 failed/48 passed
  (A/B/C fixture-oracle issues across the audit-case, repeated-root-operand,
  unacquired-shapes and unissued-then-delayed-receipt tests); q13 4
  failed/64 passed (audit-case until the boundaryless late-opaque C case
  was added); q19 2 failed (test_d_malformed_non_p_state_refuses_before_
  result — D test-oracle issue: Q validates a fresh copy, so bounds
  identity is not promised); q21/q22 each 2 failed (test_e_constructor_
  collection_ceilings — E draft-fixture issue); q28 2 failed/168 passed
  (test_f_idempotent_query_and_scope_key — F1 helper argument-order error;
  affected rerun q29 exit 0); then q30/q32/q35 170/170/170 passed and the
  q25 regression neighbor run 1018 passed. Early draft lint/type captures
  preserved: ruff-c1 12 errors, ruff-q31 8 errors, mypy-q33 15 errors in 1
  file; the final q44/q45/q46/q47 all exit 0. The q26 measurement helper
  was stopped on ROOT direction with partial 315 B stdout/err 0 preserved.
- Inherited 018-p history (recorded in the 018-p report and decision, NOT
  018-q code repairs): the 018-p focused r4/r6 draft-oracle/fixture
  failures, the r8 missing-import plus old-I boundary defect repaired by
  the explicit guard, and the r15/r16 harness-only failures.
- PR metadata: the first structured PATCH attempt used a nonexistent
  `patch` field, which the GitHub API ignored (the server body was then
  verified byte-identical to the 2891 B pre-Q snapshot — no damage); a
  subsequent `gh pr edit` attempt failed at its GraphQL read stage (classic
  projectCards deprecation reported as an error, rc 1, no mutation); the
  final structured REST JSON PATCH carrying the exact body succeeded and
  the server body was byte-verified equal to the 3408 B corrected candidate
  with the title unchanged. The previous exact body is retained
  byte-identical (mode 0600, owner-writable). The candidate's first draft
  overclaimed the eight-probe coverage (it named purity/privacy and
  causality/forgery domains); the published body names the actual eight
  probe domains and attributes purity/privacy and public forgery/owner-join
  negatives to the 170-test module in the full gate.
- Privacy/purity evidence scope: the 24 trapped
  filesystem/network/process facilities across 4 endpoint/mode runs are the
  permanent purity sections of the 170-test Q module, run under the full
  gate; none of the eight independent frozen probes covers purity/privacy.
  The canaries are known synthetic values over the tested representation
  surface; they prove only the tested surface, NOT a blanket
  no-real-credential, no-customer-data claim anywhere.
- The 28 skipped tests are as actually reported by pytest; no skip
  identities or reasons are inferred from the count.
- Q boundary: the P-first-over Q work boundary was NOT attained by the
  measured 40-branch public production sequence (producer maximum 11379 >
  actual P phase 7943, so no producible namespace ceiling falls below the
  P phase); it is not claimed universally unreachable, and the charging-
  adapter mechanism is exercised directly in the adapter-level control.
- Implementation scope was preserved with the listed process deviations.

## Recommended strategic follow-up
Factual only; strategy decides. Strategic review of 018-q at its bounded
inert scope using this report, the 8 independent frozen-B probes, the
exact-15 gate, the clean build + strict proof and the exact-B CI. If
accepted, activate the same-018 consumer round that consumes the
legitimate new root-region state into the actual graph/admission; whole
018 and 019–024 remain open/mandatory until then.

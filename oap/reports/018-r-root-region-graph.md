# OAP Coding-Agent Report — 018-r

## Work order
- Identifier: 018-r; order path `oap/orders/018-r-root-region-graph.md`
  (SHA256 3572f2804089037dbf538b147f7dfb2b4b06831543220543dee20120961e25b8);
  numeric objective 018.
- PR mode: AMENDED_EXISTING_PR (PR 26, branch `oap/018-cache-graph-bundles`,
  base `main`/ffaabf4b4d9ce3a9cb7a48e12ab7d8847999adef).

## Status
COMPLETE

## Executive summary
Delivered the graph half of the required region-compatible consumer as a
separately versioned PURE derivation: new modules
`root_region_graph_models` / `root_region_graph` under
`src/slaif_local_coding/constitution/bundles/` with the public entry
`derive_root_region_graph(state, ns, bounds=None, *,
root_region_currentness_bounds=None, current_graph_bounds=None,
nonroot_currentness_bounds=None)` and the bounds factory
`RootRegionGraphBounds`; the new
`cache-root-region-graph/v1` / `root-region-graph-policy/v1` contract in
`docs/CACHE-ROOT-REGION-GRAPH-CONTRACT.md`; and the 210-case permanent
suite `tests/test_root_region_graph.py` (A–G matrix). From the ACTUAL
retained 018-p state and namespace the derivation derives ACTUAL 018-q
currentness in the SAME charged operation, resolves the ONE usable
selected root source (envelope from the actual immutable anchor, whole
read with its complete singleton proof, or region joined to the SAME
original retained objects with the root interval from preceding original
segment CHARACTER lengths under closed preflights before any owned
slice/encode/hash/copy), and derives the ACTUAL accepted 018-f/018-e
current graph under that selected root — all under ONE R outer
`max_total_work_units` while every inherited local domain (Q-local, P, D,
B, E, F, GraphBounds) keeps its OWN independent ceiling. Closed outcomes:
`ready` only when actual same-run Q ready, actual selected-source
resolution and actual F graph success all hold (not admission, compiled
content or runtime readiness); `root_currentness_unproven` and
`root_authority_conflict` map the ACTUAL same-run Q outcomes before any
source slicing or F derivation, publishing no usable selected source or
graph while retaining the actual returned nested evidence. The derivation
mints no root authority, advances no revision, creates no persistent
state, and the accepted P/Q/F/E producer/query/graph law and old H/O/I
surfaces are unchanged (typed PRIVATE factoring only, old public
signatures/schemas/defaults/refusal boundaries preserved).

## Source and identity
- FINAL clean source A `6d388e4926062a858496374a844257d81592879d`
  (17 paths, 7811 insertions; sole parent Q SELF
  `c11c3e996c7975f09db6ebc14e3747d437ae2dc0`), including the exact
  activated R order and `oap/active` (verified SHAs above).
- Implementation head (manifest-only B)
  `ab265aa6b08e5078a19e04b407202c8abe4debfa` changes only
  `packaging/dev_provenance_manifest.json` (270 inputs); SOLE parent A.
  Remote PR 26 head verified equal to B.
- All 3 compact mirrors byte-equal (90517 B,
  SHA256 7be3e6a01ace34cea64bfc0077482c5c50c4f36a4925baad797ba0f1771dd71c); supervision compact inode 10638621/UID 1001/0600
  preserved in place.

## Verification (at exact clean B)
- Frozen FIFTEEN-command gate, ONE managed foreground run at B: all 15
  actual exits 0 (`gate-summary.json`), pytest **6,274 passed, 28 skipped
  in 756.99s**, stderr 0. Driver 2739366/birth 306587076/PPID
  2739361/UID 1001/umask 077 with startup metadata written before any
  command. The driver's own child comm/uid fields are qualified by the
  independent actual measurement below.
- Live actual pytest measured independently by ROOT through known owned
  UV task threads: PID 2740047/birth 306587238/PPID 2740044, comm
  `pytest`, all UIDs 1001, Umask 0022, ordered `pytest -q` argv
  (`S/reviews/018-r-actual-pytest-process-v1.json`).
- Focused suites fresh: R 210 passed, P 223 passed, Q 170 passed, all
  actual exit 0/stderr 0. mypy `Success: no issues found in 170 source
  files`; ruff check and format --check exit 0 (also gate g03–g05).
- ONE clean Git-B archive build (invocation exit 0): 885 archive files,
  wheel `1bfef428…` 539123 B and sdist `2826a136…` 1989022 B byte-equal
  to the manifest and the gate dist. Direct strict proof (exit 0): 885
  Git/archive files verified vs B, 270 manifest inputs verified against
  source A, Git B and the clean tree, 268 sdist entries (267 source
  verified + 1 generated), 64 wheel entries, and the wheel's 64-line
  RECORD — the 63 non-self payload rows digest/size-verified, the RECORD
  self-row present — plus metadata, entry points and licenses
  (`S/reviews/018-r-strict-artifact-independent-v1.json`).
- Scale evidence (unchanged caps, no cap raise): the old-I root-only
  baseline accepts 5000 B but refuses 32768/65536/131072 B in both
  modes. Actual R: 32 KiB and 64 KiB multi-dependency shapes READY with
  measured domain work (e.g. 32 KiB shape R total 396936 / Q 67416 /
  P 67359 / F 568); 131072 B yields an honest R-total refusal with stage
  evidence — mixed both modes: crossing at the source-constructor
  content-verification reservation (393232, `_r_resolve_source` line 461,
  after the selected-root slice) with resolver entry 1/return 0, source
  `__init__` 0, F entry 0; root-only both modes: F actually enters and
  returns (F ok retained), crossing at the final result-build
  reservation (393234, line 1142).
- All TEN current-B checks SUCCESS (test, Analyze (actions), Analyze
  (python), CodeQL, gateway-contract, docker, docker-published,
  operator-session, cache-native-containment, cache-native-fixture) at
  exact head B (`S/reviews/018-r-B-allTEN-independent-v1.json`), with
  direct commits/check-runs all at head_sha B and PR 26 OPEN with exact
  base/head before and after.

## Skips
- The 28 skipped tests are as actually reported by pytest; no skip
  identities or reasons are inferred from the count.

## Original failure causes or UNKNOWN
- Focused EFG first run (r1): 6 failed / 24 passed; the active os.stat
  purity trap intercepted pytest's error rendering, so the original
  detailed failing causes are UNKNOWN from that capture (preserved as-is;
  later fresh runs passed).
- mypy iterations (361 → 0): typing-only errors (union-attr, arg-type,
  type-arg, assignment) in new test/module code, resolved with typed
  local guards and assertions; no behavior change. The r-mypy-r3 capture
  overwrote an earlier two-source-file success capture at the same path
  (current-R historical qualification, preserved).
- First gate-driver draft: preflight syntax error before rewrite
  (recorded in the session transcript; original bytes overwritten,
  qualified as not retained).
- No other product-level failure was observed after the focused suites
  turned green; the full gate and all regressions passed.

## Independent-versus-worker audit
- ROOT independent full-gate review: all 15 actual exits 0 and 45
  captures read (`S/reviews/018-r-full-gate-independent-v1.json`).
- ROOT live actual-pytest identity/mask measurement (above).
- ROOT strict artifact/proof independent verification: direct outer and
  internal native exits 0, actual counts/hashes
  (`S/reviews/018-r-strict-artifact-independent-v1.json`).
- ROOT source-A scope/architecture review: A exact 17 paths/sole parent,
  all-3-compact equality, frozen static assertion review confirming the
  863 original predicates preserved (`S/reviews/
  018-r-source-A-scope-and-architecture-review-v1.json`, `S/reviews/
  018-r-final-typing-and-guards-review-v1.json`).
- Bounded moving-source model/kernel/test reviews (R-M01…M11, R-K01…K04,
  D/E/F/G matrix drafts, pre-slice and domain audits) each independently
  reproduced and verified fixed before freeze; these are bounded
  independent evidence, not a substitute for the permanent suites.

## Process qualifications
- The first gate capture directory was created outside umask 077
  (observed 0775, restricted in place to 0700 with before/after facts);
  the gate driver was created private 0600 within umask 077 and then
  restricted to 0700 for the executable-driver requirement.
- The clean-build driver startup recorded its PID and umask but not
  birth/PPID/source hash; the build already ran and was not rerun to
  repair metadata. The proof driver (2847552/birth 306682745/PPID
  2847542/UID 1001/077 with source hash) and proof helper (2847564/birth
  306682748/PPID 2847552) carry complete startup records.
- The re-bound clean-build script header carries a stale 018-q label
  (cosmetic; the run already completed under the exact-B guard and is
  preserved, not relabeled).
- The driver-recorded child comm/uid fields are qualified by the
  independent actual measurement (comm `pytest`, UID 1001, Umask 0022)
  through known owned UV task threads; shell `$$`/uv PID is not the
  actual pytest PID.
- The current R r-mypy-r3 capture overwrote an earlier two-source-file
  success capture; prior-round capture-overwrite and sampler-path
  qualifications remain preserved in the prior reports. No rebuild or
  rerun was used to hide any qualification.

## Boundaries and remaining scope
- R is graph-only/inert and PENDING strategic review; acceptance is not
  claimed. The separate same-018 admission/full-result consumer and the
  complete original-018 criterion audit remain mandatory before merge,
  and objectives 019–024 remain mandatory.
- Q is ACCEPTED at its bounded inert query scope WITH PROCESS
  QUALIFICATIONS AND EXPLICIT HISTORICAL-REPORT CORRECTIONS; P is
  ACCEPTED at its bounded inert producer scope WITH PROCESS
  QUALIFICATIONS; the I/J/K/L/M NOT ACCEPTED history and all unique
  law/qualifications are preserved. No v1 runtime, model/client
  qualification, deployment, release or cutover is claimed or enabled.

Implementation head SHA: ab265aa6b08e5078a19e04b407202c8abe4debfa
Report publication commit: SELF

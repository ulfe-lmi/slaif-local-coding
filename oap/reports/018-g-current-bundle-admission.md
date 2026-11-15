# OAP Coding-Agent Report — 018-g

## Work order
- Identifier 018-g; order `oap/orders/018-g-current-bundle-admission.md`
  (23764 B, sha256 5e26d7bc…b035e); objective 018
- PR mode: AMEND_EXISTING_PR (PR 26, branch `oap/018-cache-graph-bundles`)
- Control OK consumed 2026-11-02T04:09:33.117764+00:00 by managed wait
  80639 (receipt W18f/next-control-wait-018f-receipt.json, exact 4f4b);
  no second FIFO read; no agent startup; ROOT response reader never polled

## Status
COMPLETE (claim, not acceptance) — 018-g delivered as INERT mechanism
evidence, PENDING strategic acceptance; current-version admission
MECHANISM PARTIAL only; no runtime activation

## Executive summary
Implemented ONE pure bounded derivation over the ACTUAL retained 018-d
causal-history state and ACTUAL namespace: the accepted 018-f current
graph in the SAME run (via the private shared-work seam; public F
signature/defaults unchanged) plus the current admission entries with
the canonical 018-c semantic keys — root entry with the typed retained
anchor fields (exact EMPTY root legal), per-owned-group currentness
truth table (root-bearing opaque exclusion; no greedy isolation), entry
interning retaining the FIRST compatible original proof by identity
with the complete original witness coordinates (canonical five-tuple
order, never acquisition), complete reverse member index (attempts
charged before dedup), and the RETAINED bounded admission-reason tuple
whose emitted count is bound to its length under BOTH the new and the
inherited admission caps in one domain. NEW per-derivation
CurrentAdmissionBounds on ONE shared outer ledger with the ACTUAL
supplied F-subtree ceiling enforced independently in its own phase;
G-owned pre-copy reservations over every collection walk and the
charged-comparison stable merge. 017/018-a..f public behavior, the
canonical key recipe and reference grammar unchanged; no runtime
stale-injection or later-stage pass.

## Authoritative GitHub state
- ulfe-lmi/slaif-local-coding; PR 26 OPEN/non-draft; base main
  ffaabf4b4d9ce3a9cb7a48e12ab7d8847999adef
- Starting remote SELF eedb874c480d471ccb3dcef8a97af02f666c0d79
  (018-f, ACCEPTED at its bounded inert current-graph scope WITH
  process qualifications per S/reviews/018-f-decision.md)
- Implementation head SHA: 6bde106d73001104752f8eef9542fc459338847a
- Report publication commit: SELF
- Commits: c5c0c8542f1b1a0532bc91bc4a87a06f123da0bf (source A: kernel/
  models/tests/contract/seam/docs/order+active),
  6bde106d73001104752f8eef9542fc459338847a (manifest B, 249 inputs)
- New PR: no; amended existing: yes; merge: NO

## Changes and files
- NEW (inert product): `bundles/current_admission_models.py`,
  `bundles/current_admission.py`
- `bundles/current_graph.py`: private `_derive_graph` overlay-tuple
  seam (G reuses the SAME-run E overlay instead of repeating a public
  E/F call) plus the mid-phase return-arm repair below
- NEW tests: `tests/test_current_admission.py` (158 cases, criteria
  A-H, BOTH read endpoints x BOTH modes)
- NEW contract: `docs/CACHE-CURRENT-ADMISSION-CONTRACT.md`
- Reconciled: `docs/CACHE-REWORK-LEDGER.md` (C04/C05 + 018 succession;
  C05 duplicated plus018-f/g clause removed, qualified statuses once),
  `ARCHITECTURE.md`, `ARCHITECTURE-for-agents.md` (+ three byte-equal
  compact mirrors SHA 8f127ae9…; S mirror inode 10638621/mode 0600
  preserved in place), `TESTING.md`
- Append-only `oap/REPORT-CORRECTIONS.md` 018-f section (prior 1239 B
  prefix byte-preserved; F report untouched)
- Transcript (strategic bytes unchanged): 018-g order + `oap/active`
  (`018-g`)

## Mid-round review closures (all closed at source A)
ROOT in-scope reviews during the round: dropped admission-reason
retention (retained tuple + count law), nested Pydantic revalidation
(G-owned typed retained references; old B/C/F schemas unchanged),
accounting follow-ups (quadratic membership, N-squared set/sort
reservations, charged-comparison merge with keys moving with values),
durable test-oracle corrections (endpoint-aware repeated-operand
helper, equal-aggregate AB/BA, boundaryless AB->AC, T6 perturbation,
retention 129->actual sequential fix), and the pre-A gate mypy finding:
the private-seam refactoring had left the ordinary-phase
scan-limitation return as a tuple (breaking the `bool |
CurrentGraphResult` loop contract) and the mid-loop passthrough
missing the overlay-tuple element — a latent runtime defect no prior
green suite proved (no durable case reached that branch). Both arms
repaired; the branch is now durable via
`test_g_scanner_candidates_per_document_refusal` (4 cases: coherent
stricter `max_reference_candidates_per_document` projection, at-cap 2
BOTH public F and G OK, cap 1 BOTH refuse exact
GRAPH_CANDIDATES_OVER_BOUND, exact state, no overlay). ROOT's 16
actual original-API controls rechecked AFTER the repair
(S/reviews/018-g-F-scanner-refusal-v1-result.json).

## Verification evidence (all coding-executed, actual exits)
- Focused: `tests/test_current_admission.py` 158 passed (direct child
  exit 0); admission+graph+graph-models+currentness 450 passed
- Background full suite (W18g/full-suite-v1.log): pytest summary
  2 failed / 5092 passed / 28 skipped; the only failures are the two
  known stale-manifest binding tests that manifest B resolves. The
  log's trailing exit-marker line is absent (process qualification
  below); the gate cmd07 is the authoritative full-suite exit evidence
- Qualified exact-15 gate g1 at clean B 6bde106d…: ONE foreground
  managed run, all 15 actual rc=0, gate.exit=pass; parent umask 077
  (driver PID 3758517, UID 1001), cmd07 nonroot child umask 022 (PID
  3758672, PPID 3758517); full-repo pytest 5098 passed, 28 skipped,
  640.09 s; metadata-only aware-UTC rehearsal recorded before launch
  (gate-g1-rehearse.json); no masking pipelines
- Clean git-archive exact-B BOTH build + strict proof
  (W18g/clean-build-g1): archive/extract/build actual exits 0 (842
  files); wheel 473e92e3…0726680 (54 entries) + sdist 6f85f82a…18dbff4
  (247 entries) byte-equal to the B-recorded manifest; proof driver
  PID 3799940, umask 077, actual rc 0; ALL PROOF ASSERTIONS PASSED
  (Git/archive/tree inputs, sdist sources, wheel runtime, unique
  RECORD incl. self-row, raw PKG-INFO==METADATA, licenses/NOTICE/
  entrypoints, repo-gate dist byte-identity)
- GitHub CI at B 6bde106d…: ALL TEN required checks SUCCESS (main run
  41411931682: test, docker, docker-published, operator-session,
  gateway-contract, cache-native-fixture, cache-native-containment;
  security run 41411928169: CodeQL, Analyze (python), Analyze
  (actions)); verified headSha == B

## Process qualifications (honest, no relabeling)
- Executed W18g manual source preservation deviations:
  proto-cd-scenarios-v1.py was EXECUTED then patched repeatedly in
  place at the same v1 path (on-disk 9404 B is the last-patched state,
  sha256 16044a20…; original pre-patch bytes not preserved);
  probe-k1-sites-v1.py patched in place 3200->3539 B (original bytes
  not preserved); measure-g-thresholds-v1.py executed-failed (syntax)
  then edited/fixed in place — the failed-byte captures were NOT
  preserved (on-disk 5792 B sha256 79dec9ad… is the final state; the
  intermediate failed bytes are not independently established).
  Later repairs used fresh vN paths; executed-failing proto-cd-v4/v5
  sources with captures preserved
- baseline-suite-v1.log is 0 B (empty capture; cause not independently
  established); baseline-suite-v2.log: 26 failed / 4938 passed / 28
  skipped (historical pre-final-fix snapshot)
- /tmp facts are inherited via oap/REPORT-CORRECTIONS.md (018-e
  tc_trunc.py; 018-f /tmp/dummy 0 B/0600 with unknown prior
  existence); no new /tmp use this round
- 018-g is INERT mechanism evidence: no admission runtime, no
  compiler hits, no root refresh, no wire/recovery/client claims;
  current graph/admission, owned-edge + certificate withdrawal
  end-to-end and stale-injection remain NOT RUN; 019-024 mandatory.
  F acceptance facts recorded per S/reviews/018-f-decision.md; G is
  PENDING strategic acceptance

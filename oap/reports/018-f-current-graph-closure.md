# OAP Coding-Agent Report — 018-f

## Work order
- Identifier 018-f; order `oap/orders/018-f-current-graph-closure.md`
  (25070 B, sha256 11567420…ddab64); objective 018
- PR mode: AMEND_EXISTING_PR (PR 26, branch `oap/018-cache-graph-bundles`)
- Control OK consumed 2026-11-01T21:35:27.528802+00:00 by wait 20199
  (receipt verified); no second FIFO read; no agent startup

## Status
COMPLETE (claim, not acceptance) — 018-f delivered as INERT mechanism
evidence, PENDING strategic acceptance; graph MECHANISM PARTIAL only

## Executive summary
Implemented the pure current-graph closure and version-owned
withdrawal over the ACTUAL accepted 018-d causal-history state and
ACTUAL 018-e currentness: current source suppliers selected BEFORE
any scanning from the ACTUAL per-owned-group currentness (blocked
opaque groups indivisible, supplying nothing; root-bearing groups
can never supply root text); the fresh root least fixed point
rebuilt from the immutable RootAnchor only (ordinary expansion +
certificates repeated to ONE joint least fixed point until stable);
version-owned ordinary edges and group certificates with
owner/witness provenance (owner removal removes only its own
derivation; surviving alternates keep the target; old replays
restore nothing); honest per-node availability retaining
unreachable possession; least complete AND/OR depth recomputed
after withdrawals with max_depth enforced after the fixed point;
RootAnchor field shapes/spans freshly validated under charged
source preflights (never model_validate of an existing instance);
the 15-field scope key binding actual validated history
namespace/workspace, actual root digest, inherited versions, all
effective bounds and the NEW versioned current-graph contract/
policy; two new per-derivation CurrentGraphBounds under ONE shared
outer ledger via the cohesive private 018-e seam (public
signature/default unchanged); charged stable-merge collection
accounting (linear reservations before; every actual comparison
and element write charged; keys move with values; exact totals
pinned). 017/018-a/b/c/d/e public behavior, the canonical argument
recipe and reference laws unchanged.

## Authoritative GitHub state
- ulfe-lmi/slaif-local-coding; PR 26 OPEN/non-draft; base main
  ffaabf4b4d9ce3a9cb7a48e12ab7d8847999adef
- Starting remote SELF 2e82efc6978139abbd4cd06b58d405f29caa1f98
  (018-e, ACCEPTED at its bounded inert scope with process
  qualifications per S/reviews/018-e-decision.md + addendum)
- Implementation head SHA: 02e0fc9f028fcc2ba74203f5937725cf522ce33c
- Report publication commit: SELF
- Commits: 72151b3… (source A1: kernel/models/tests/contract/docs/
  order+active), c98a7aa… (manifest B1, 245 inputs; FROZEN-B review
  found accounting gaps — superseded, not closed by B1), d8d40b4…
  (source A2: accounting fixes + durable controls + contract
  §9), 02e0fc9… (manifest B2, 245 inputs)
- New PR: no; amended existing: yes; merge: NO

## Changes and files
- NEW (inert product): `bundles/current_graph_models.py`,
  `bundles/current_graph.py`; `bundles/currentness.py` private
  shared-work seam (public API unchanged)
- NEW tests: `tests/test_current_graph.py` (43 fns → 190 cases,
  criteria A–J, BOTH read endpoints × BOTH modes),
  `tests/test_current_graph_models.py` (14 fns → 14 cases)
- NEW contract: `docs/CACHE-CURRENT-GRAPH-CONTRACT.md`
  (cache-current-graph/v1, current-graph-policy/v1)
- Reconciled: `docs/CACHE-REWORK-LEDGER.md` (C04/C05 cells + 018
  succession row), `ARCHITECTURE.md`, `ARCHITECTURE-for-agents.md`
  (+ three byte-equal compact mirrors; S mirror inode 10638621 /
  mode 0600 preserved in place), `TESTING.md`,
  `docs/CACHE-CURRENTNESS-CONTRACT.md` (accepted intro)
- Transcript (strategic bytes unchanged): 018-f order + `oap/active`
  (`018-f`)

## Frozen-B accounting review (closed at A2)
ROOT frozen-B review
(S/reviews/018-f-supplier-interning-accounting-review-v1.json) +
consolidated remainder: uncharged witness membership scans and
in-place sorts in supplier interning, uncharged root-only group
membership scan, depth-table construction, per-member relaxation
inspections, per-supplier usable-depth output walk, coordinate
tuple copies, and per-candidate re-sorts of shared supplier output
metadata. All closed at d8d40b4…: witness dedup/ordering deferred
to the charged output retention over the FULL input length; every
named operation precharged on both ledgers; per-supplier output
metadata interned once per supplier with lazily charged depth base;
contract §9 "actual-operation completeness" law. Durable controls
added both endpoints/modes: root-only group supplies nothing
(actual original-API CURRENT_OPAQUE root-only group) and
repeated-contributor deferred-witness interning (ONE occurrence,
TWO proven singleton groups, same path/digest; deduplicated
witnesses, both coordinates retained), each with outer at-limit/
first-over boundaries. No claim that frozen B1 closes the review;
B1 gate evidence preserved untouched.

## Verification evidence (all coding-executed, actual exits)
- Focused 018-f suites: 204 passed (direct child exit 0).
- Qualified 15 gate f2 at exact clean B 02e0fc9…: ONE foreground
  managed run, all 15 actual rc=0, gate.exit=pass; parent umask
  077 (driver PID 3464543, UID 1001), cmd07 nonroot child umask
  022 (PID 3464705); full-repo pytest 4940 passed, 28 skipped,
  640.36 s; metadata-only aware-UTC rehearsal recorded before
  launch (gate-f2-rehearse.json).
- Frozen-B gate f1 at c98a7aa…: all 15 actual rc=0 (4932 passed,
  28 skipped; driver PID 3413234, cmd07 child 3413389) — preserved
  evidence of the reviewed (superseded) frozen B.
- Clean git-archive exact-B BOTH build + strict proof at B2: exit
  0; wheel 1991df42…a574db2 (52 zip entries) + sdist 70cc77ea…
  b33817a (243 entries); proof driver PID 3506324, umask 077;
  ALL PROOF ASSERTIONS PASSED (repo gate dist byte-equality,
  unique RECORD incl. self-row, raw PKGINFO==METADATA, licenses/
  NOTICE/entrypoints, manifest A-B inputs).
- GitHub CI at B2: ALL TEN required checks SUCCESS (main run
  41384207392: test, docker, docker-published, operator-session,
  gateway-contract, cache-native-fixture, cache-native-containment;
  security run 41384204314: CodeQL, Analyze (python), Analyze
  (actions)). B1's identical TEN SUCCESS at c98a7aa… is
  historical for the superseded frozen B.

## Process qualifications (honest, no relabeling)
- W18f design note and measure sources created 0664 then corrected
  0600 under the 0700 root (origins preserved);
  measure-sort-reservation-v1.py syntax-failed (preserved); v2's
  first run was accidentally on Python 3.14.4, re-run on 3.12.15
  as authoritative — the measurements are HISTORICAL
  qualification only and are NOT cited as the charged-sort law's
  justification (the law is actual comparison/write charging).
- diag-offgraph-v1 (959 B, Hist("lean") bug) failed and is
  preserved; the 0-byte diag-offgraph-v1 deletion was never
  executed; probe-rootonly-v1/v2 failed on import/field-name bugs
  (preserved), v3/v4 succeeded read-only.
- /tmp/tc_trunc.py head-redirection 0664 deviation (known-
  synthetic test source; emptied; no real secret exposure
  identified) preserved as a no-/tmp hygiene deviation.
- mypy-probe-tmp{,2,3}.py (0600, W18f) recorded the mypy 1.20.2
  `Sized & Iterable[T]` rejection that motivated the
  `_ChargedSortable` protocol.
- Stale-source-A CI binding failures between A2 and B2 are
  expected/historical (generator's internal temporary clean-A
  build is approved tool behavior); no label-only reruns.
- 018-f is INERT mechanism evidence: no admission entries, no
  compiler hits, no root refresh, no runtime/wire/recovery/client
  claims; C04/C05 graph MECHANISM PARTIAL at bounded scope;
  current-version acceptance, root-refresh authority-lineage
  contract and 019–024 remain mandatory later work.

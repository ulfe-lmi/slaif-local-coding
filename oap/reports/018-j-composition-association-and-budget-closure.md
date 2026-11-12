# 018-j round report — composition association closure and budget evidence

- Status: PARTIAL
- Implementation head SHA: 0eeb8a74e1153760f696bfd2657d9d3eef4e3d64
- Report publication commit: SELF

## Work order
`oap/orders/018-j-composition-association-and-budget-closure.md` (sha256
`1a31e39426bace38d4c2eb7ee65df840667c95f79ef73fd08e18676eca6b0a10`), AMEND
of PR 26 (same branch, no second PR). 018-i was NOT ACCEPTED (strategic
decision `S/reviews/018-i-decision.md`): two ROOT-reproduced constructor
defects (J01 historical governing-key splice; J02 reverse-index pollution)
plus resource/evidence gaps (J03, incl. the NEW-I key-record fence charged
through facade AND stage_g instead of the I outer only).

## Executive summary
The bounded J repairs are implemented at their delivered scope: J01 binds
EVERY retained entry and its ACTUAL key record to the SELECTED governing
digest at both the admission and the result boundary; J02 makes the ACTUAL
reverse member index equal exactly the represented member-path to
ALL-and-ONLY admitted content keys relation at both boundaries; J03 charges
the NEW-I fence to the I outer only and closes the D-local, E, graph-stage
and admission-stage domains at measured at-limit/first-over (D-local at the
actual D-validator stage surface with the public-I identity control, the
public-I D first-over being structurally unreachable). Both original named
ROOT probes now PASS 4/4 at B. A new immutable ROOT constructor probe at B
exposes two additional nested constructor laws that remain UNMET (below);
A/B are frozen and this report is published truthfully PARTIAL. No public
derivation failure, no runtime activation, no old public law change.

## Authoritative GitHub state
PR 26 open, branch `oap/018-cache-graph-bundles`, base `main`
`ffaabf4b4d9ce3a9cb7a48e12ab7d8847999adef`. Source A
`97f26ce42d8ce41a11ba88075885c1bc4768f3c8`; manifest-only B
`0eeb8a74e1153760f696bfd2657d9d3eef4e3d64` sole parent A; remote head = B.
Delivered source pins: kernel `2039d8047872…2252`, models
`8974c21c515d…3393`, tests `4549074add93…efa11`.

## Changes and files (A)
`current_root_composition.py` (I-only fence domain, wrapper-delta/result
join reservations), `current_root_composition_models.py`
(`_check_selected_root_binding`, `_check_reverse_member_relation` at both
boundaries), `tests/test_current_root_composition.py` (J section: 13 defs /
52 cases; module now 57 defs / 218 cases), I contract (intro status, §5
fence domain + cap/evidence table, §6 J01/J02 laws, §10 counts), TESTING.md,
human ARCHITECTURE.md (both status sites), ALL3 compact mirrors
(byte-equal `bb9245828002…9c88`), ledger (C04/C05/018 cells),
`oap/REPORT-CORRECTIONS.md` (append-only 018-i addendum), unchanged order
file + `oap/active`.

## Acceptance evidence
- J01: `S/reviews/018-j-historical-entry-splice-v1.out` 4/4 PASS, exit
  0/stderr 0 (unchanged immutable ROOT source, fresh J capture).
- J02: `S/reviews/018-j-reverse-index-pollution-v1.out` 4/4 PASS, exit
  0/stderr 0.
- UNMET at B (recorded, continuation expected):
  `S/probes/018-j-nested-canonical-and-row-shape-v1.py` (source sha
  `13c3a2957e65…58af`; captures `S/reviews/018-j-nested-canonical-and-row-
  shape-v1.{out,err,exit}`; 0/8, exit 1/stderr 0/stable pins). Constructor-
  only, no public derivation failure: (1) a nested entry with BOTH entry and
  key-record root digests rebound to the selected digest but RETAINING the
  stale actual canonical key is accepted by the parent admission/result
  constructors (4 modes/endpoints) although the entry leaf reconstruction
  rejects it; (2) a nested reverse-index row duplicating a real content key
  via model_copy is accepted by the parents although the direct row
  reconstruction rejects it. 018-i remains NOT ACCEPTED; 018-j PENDING
  strategic review.

## Verification
- Focused module: 218/218 PASS (7.8 s); affected-file regression
  (composition+admission+lineage): 585/585 PASS. ruff check / ruff format
  --check / mypy src tests / docs_consistency_check: all clean.
- ONE foreground-managed exact-15 at clean B (fresh W18j
  `final-gate-j1/driver.sh` 0700, mechanically re-bound from the verified
  018-h h1 template sha256 `31725eee…c249e`; set -o noclobber): all 15
  literal exits 0 (`gate-cmdNN.exit`). Driver 4054676/PPID 4054666/birth
  292995040/UID 1001/umask 0077/head B/tree clean; cmd07 wrapper 4054832
  (exec uv)/umask 0022; the ACTUAL owned pytest child captured live by a
  bounded owned-tree walk: PID 4054840/PPID 4054832/birth 292995124/UID
  1001/inherited umask 0022 (`gate-cmd07-live-context.json`). cmd07: 5525
  passed / 28 skipped / 662.58 s / stderr 0.
- ONE clean exact-B git-archive BOTH build (archive/extract/build exits 0,
  stderr 0): wheel 458526 B `1a345816645d…19b28c` (58 entries), sdist
  1754263 B `0bfdf590acf6…221d912` (255 entries); full strict proof exit
  0/stderr 0: 856 Git B files, 257 manifest inputs verified vs Git B and
  clean tree, 254 sdist sources + 1 generated (PKG-INFO), 52 wheel runtime
  entries, 57 RECORD rows verified, both artifacts byte-equal the manifest
  and the repo gate dist.
- GitHub CI at B: ALLTEN SUCCESS (test, docker, gateway-contract,
  operator-session, cache-native-containment, cache-native-fixture,
  docker-published, CodeQL, Analyze x2).

## Live model-service evidence
NOT RUN. Inert scope: no command string executed, no model/native/client/
service facility started; the adapter runtime stays inactive.

## Documentation
I contract (intro NOT ACCEPTED + J PENDING review; §5 I-only fence domain
and the compact cap/evidence table distinguishing NEW-I, inherited-regression
and structurally-unreachable evidence; §6 J01/J02 association laws; §10 57
defs/218 cases + J description), TESTING.md 018-i line, human ARCHITECTURE
both status sites reconciled (g/h ACCEPTED, i NOT ACCEPTED + J), ALL3
compact mirrors updated in place and byte-equal, ledger C04/C05/018 cells,
append-only REPORT-CORRECTIONS 018-i section.

## Process qualifications
- (018-i, verbatim) the unauthorized preliminary background full suite
  (2 FAILED/5471 PASSED/28 SKIPPED, exit 1, dirty pre-A source) was never a
  final pass; the manual /tmp PR-body captures were later preserved
  protected; the recorded exec-uv launcher 3909619/birth 292143146/umask
  022 was the LAUNCHER, not the pytest child — no past /proc facts are
  invented, and the actual pytest child is captured live for the first time
  in this J gate.
- (018-j) the first j01/j02 postfix attempt ran under system python3
  (ModuleNotFoundError, exit 1); the subsequent uv rerun overwrote the same
  `.out`/`.err` names, so the first-attempt failed bytes are LOST (disclosed,
  not reconstructed).
- (018-j) two transient ruff stdout files were written to /tmp at the start
  of this session before redirection to protected paths; linter output only,
  no evidence value or content exposure (disclosed per the no-/tmp evidence
  law).
- A/B were frozen by ROOT review after publication; no source mutation or
  duplicate gate/build follows this report.

## Known limitations
- The two UNMET nested constructor laws above (stale actual canonical key
  after both digest fields rebound; nested duplicate row content key).
- The documented UNREACHED post-refresh NEW-root mixed-bundle acquisition
  gap: unmodified old H/D refuse before I; the old H public law is not
  broadened and no positive is manufactured (whole-018 gap, preserved).
- Whole 018 unmerged; v1 runtime criteria NOT RUN; 019-024 remain mandatory.

## Recommended strategic follow-up
A continuation round adding, at both boundaries: (a) re-derivation of the
ACTUAL canonical key from the nested entry's key record (entry.content_key
must equal the re-derived key, not only the two digest fields); (b) the
canonical dedup/order shape of nested reverse-row content keys (sorted,
distinct) in the exact-relation law. Then full J review against the exact
constructor/resource criteria.

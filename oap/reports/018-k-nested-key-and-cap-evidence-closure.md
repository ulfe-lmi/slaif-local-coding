# 018-k round report — nested canonical keys, row shapes, reachable cap evidence

- Status: COMPLETE (bounded K scope implemented and published; K PENDING
  strategic review; no acceptance claim)
- Implementation head SHA: 3d839b00d0eb102273b60ba8f998af3c06ccb567
- Report publication commit: SELF
- Repository: ulfe-lmi/slaif-local-coding
- PR URL: https://github.com/ulfe-lmi/slaif-local-coding/pull/26
- PR mode: AMENDED_EXISTING_PR
- Base: main ffaabf4b4d9ce3a9cb7a48e12ab7d8847999adef
- Head branch: oap/018-cache-graph-bundles

## Work order
`oap/orders/018-k-nested-key-and-cap-evidence-closure.md` (sha256
`69b2ffc587450547acd6714fd51c375c21f96eb70953fcc0f1c3408a24a72e8d`),
AMEND of PR 26 (same branch, no second PR). 018-j was truthfully PARTIAL
and NOT ACCEPTED (`S/reviews/018-j-decision.md`); K closes the two named
nested constructor laws (K01/K02) and the reachable-E/cap-evidence gaps
(K03) within the existing I scope.

## Executive summary
K01 re-derives the ACTUAL 018-c canonical key from the ACTUAL nested key
record at BOTH parent boundaries (entry key, key-record content key and
recomputed key must agree under the selected governing digest); K02
validates actual nested row container/count/scalar shape and strict
canonical sorted/distinct key order BEFORE the set comparison at both
boundaries; K03 adds durable genuinely-reachable E collection cap
controls (paths/groups/witness-memberships/relation-pairs) with a
pre-work facade sentinel, isolates the D-local bound change under the
SAME lineage/identity/config, and corrects the contract cap/evidence
table names/surfaces from the existing exact tests. All new fence/
re-derivation work is precharged to the I outer only (never G). No public
derivation failure, no runtime activation, no old public law change.

## Authoritative GitHub state
PR 26 open, branch `oap/018-cache-graph-bundles`, base `main`
`ffaabf4b4d9ce3a9cb7a48e12ab7d8847999adef`. Source A `0cdbc0e5ec4c85226d6f577c6e437f8401971aaf`;
manifest-only B `3d839b00d0eb102273b60ba8f998af3c06ccb567` sole parent A; remote head = B. Starting
remote SELF `cb4901a209f68902790822f74339384318c981d8` (J).

## Changes and files (A)
`current_root_composition.py` (K precharge terms on the I outer:
`canonical_rekey_units` per planned entry, `row_shape_units` per
association row, on the wrapper-delta and result reservations),
`current_root_composition_models.py` (`_check_selected_root_binding`
canonical re-derivation + key-record closed bound fence;
`_check_reverse_member_relation` closed row-shape/sorted/distinct fence
before set comparison; reservation helpers),
`tests/test_current_root_composition.py` (K section: 5 new definitions /
20 cases; module now 62 defs / 238 cases), I contract (intro +
K PENDING,
§5 fence law + cap/evidence table names/surfaces, §6 K01/K02 association law, §10 62 defs/238 cases + K description), TESTING.md 018 line, human ARCHITECTURE.md both
status sites, ALL3 compact mirrors (byte-equal `14a2f378546a75735912337b6a27b29cb7d84db12806349c3de28fb32123c8d2`, S
inode 10638621/UID 1001/0600 updated in place), ledger
(C04/C05/018 cells), `oap/REPORT-CORRECTIONS.md` (append-only 018-j
section with the five ordered qualifications), unchanged K order file +
`oap/active`.

## Acceptance evidence
- K01/K02 named ROOT probe
  (`S/probes/018-j-nested-canonical-and-row-shape-v1.py`, source sha
  `13c3a295…58af` UNCHANGED): 8/8 PASS, exit 0/stderr 0, stable pins
  (fresh K capture `W18k/k-named-repair-check-v1.out`).
- K03 durable controls: the four E collection caps at-limit OK /
  one-below exact name on genuinely larger retained histories (both
  modes/endpoints), with the `crc._CFacade.unit` pre-work sentinel
  (foreign-scope control = 0 units; crossing > 0 and > foreign);
  D-local public identity control with the SAME lineage tag/identity/
  config and ONLY the HistoryBounds work cap changed (controlled diff
  exactly {history_key, state_scoped_key, lineage_key,
  history_bounds}); contract table names corrected from the existing
  exact tests.
- Original I/J controls preserved: the named I7/I8/I9 constructor
  controls and the J association closures all remain in the durable
  composition module (238/238), and the unchanged accepted H
  matrices (incl. the 44-case proof-shape regression) remain in the
  durable root-lineage module (three-file set 605/605).

## Verification
- Focused module: 238/238 PASS (40.6 s); three-file regression
  (composition + current admission + root lineage): 605/605 PASS.
  ruff check / ruff format --check / mypy src tests /
  docs_consistency_check: clean (pre-freeze).
- ONE foreground-managed exact-15 at clean B (fresh W18k
  `final-gate-k1/driver.sh` 0700, mechanically re-bound from the
  verified 018-h h1 template sha256 `31725eee…c249e`; set -o noclobber):
  all 15 literal exits 0. Driver 4157098/PPID 4157085/
  birth 293537237/UID 1001/umask 0077/head B/tree clean; the ACTUAL
  owned pytest child captured LIVE by a bounded owned-tree walk that
  identifies pytest by comm/exe/script position (not any argv token):
  PID 4157263/PPID 4157255/birth 293537316/UID 1001 with
  LIVE /proc Umask 0022 (kernel 7.0 exposes the field; launcher
  4157255/birth 293537312/umask 0022 kept separate),
  `W18k/final-gate-k1/gate-cmd07-live-context{,-v2}.json`. cmd07:
  5545 passed / 28 skipped / 703.06 s / stderr 0.
- ONE clean exact-B git-archive BOTH build (archive/extract/build
  literal exits) + full strict proof: archive/extract/build literal exits 0, stderr 0; wheel 460484 B `a09e23c4…` (58 entries) and sdist 1760939 B `d2f6cc29…` (255 entries) byte-equal the manifest and the repo gate dist; 858 Git B files, 257 manifest inputs verified vs Git B and the clean tree, 254 sdist sources + 1 generated (PKG-INFO 22728 B), 52 wheel runtime entries, 57 RECORD rows verified.
- GitHub CI at B: all 10 completed/success (test, docker, gateway-contract, operator-session, cache-native-containment, cache-native-fixture, docker-published, CodeQL, Analyze x2).

## Live model-service evidence
NOT RUN. Inert scope: no command string executed, no model/native/
client/service facility started; the adapter runtime stays inactive.

## Process qualifications
- (018-i, verbatim lineage) unauthorized preliminary background full
  suite (2 FAILED/5471 PASSED/28 SKIPPED, exit 1, dirty pre-A) never a
  final pass; /tmp PR-body captures later preserved protected; recorded
  exec-uv launcher 3909619 was the LAUNCHER, not the pytest child.
- (018-j) first system-python probe error captures overwritten by the
  uv rerun (LOST, never reconstructed); two /tmp ruff outputs; missing
  standalone Repository/PR URL fields and the collective build "stderr
  0" inaccuracy corrected in `oap/REPORT-CORRECTIONS.md`
  (archive.err 0/extract.err 0/build.err 281 B ordinary successful
  diagnostics/build.exit 0); ROOT's uv-launcher 4054832 misattribution
  preserved in ROOT's own erratum, worker child 4054840 umask 022
  expressly inherited not live-measured.
- (018-k) one v0 mislaunch of the named probe (no venv,
  ModuleNotFoundError, exit 1) whose brief /tmp capture was preserved
  under `W18k/mislaunch-v0/`; the existing control handle 58868 is no
  longer resolvable after the session handoff — the on-disk receipt
  `W18j/next-control-wait-018j-receipt.json` (control OK
  2026-11-10T13:47:55.136650Z on reader 4109174) is the surviving
  record; no control FIFO re-read occurred.

## Known limitations
- 018-i NOT ACCEPTED; 018-j PARTIAL/NOT ACCEPTED under its exact
  decision; 018-k PENDING strategic review.
- Documented UNREACHED post-refresh NEW-root mixed-bundle acquisition
  gap: unmodified old H/D refuse before I; the old H public law is not
  broadened and no positive is manufactured (whole-018 gap, preserved).
- Whole 018 unmerged; v1 runtime criteria NOT RUN; 019-024 remain
  mandatory.

## Recommended strategic follow-up
Full 018-i/j/k review against the exact constructor/resource criteria;
then the explicit current-root-aware mixed-bundle acquisition
continuation and the whole-018 criterion audit before any merge;
019-024 continue as mandatory.

# OAP Coding-Agent Report — 018-a

## Work order
- 018-a-cache-graph-foundation; oap/orders/018-a-cache-graph-foundation.md; numeric objective 018
- PR mode: CREATED_NEW_PR (PR 26, the one 018 PR)

## Status
COMPLETE for the bounded first slice (a-slice): delivered, verified, inert.
Not acceptance: strategic acceptance PENDING; broader 018 unearned (Known
limitations).

## Executive summary
Implements and verifies the ordered pure immutable graph foundation on
branch oap/018-cache-graph-bundles: trusted graph namespace (S01
isolation), bounded raw reference scanner, pure fixed-point closure with
stable identity/typed conflicts (G01), referring-directory/ambiguous-
origin handling with explicit unresolved-origin records (G02), and
bounded public composition consuming the accepted 017 read/process
observation surfaces (observe_request; legacy reads + native processes;
exact original-carrier spans/digests). All new code is inert: not wired
into any request pipeline; legacy runtime/grammar/settings unchanged; no
service, persistence, or session state. Fifteen-command local gate, 24
probe families, focused tests, clean-archive BOTH-artifact proof and all
ten GitHub checks pass at exact implementation head B2.

## Authoritative GitHub state
- Repository ulfe-lmi/slaif-local-coding; PR 26
  https://github.com/ulfe-lmi/slaif-local-coding/pull/26 — OPEN (not draft)
- Base main; starting remote main ffaabf4b4d9ce3a9cb7a48e12ab7d8847999adef;
  head oap/018-cache-graph-bundles
- Implementation head SHA: 06ca21c5ff477c8cb895a39525f520bad3db288b
- Report publication commit: SELF
- Implementation commits pushed before report (chronology):
  A1 95a2a6f3ea81cf9062b7dfec0a4ac8b39c4749b9 (source+docs, 17 paths) and
  B1 0c6262883dc4f8697fb91d9a5c00b082afd0a53e (manifest only) — historical,
  superseded by publication-review-v1 corrections; then docs-only
  A2 e1a91e2b2ab17803d4d2b7f43f592956108770fb and manifest-only
  B2 06ca21c5ff477c8cb895a39525f520bad3db288b (217 inputs)
- New PR this round: yes (26); amended existing: no; merge performed: NO

## Changes and files
- A1: new inert modules src/slaif_local_coding/constitution/bundles/
  {graph_models,references,graph,graph_observation}.py (+26 exports in
  bundles/__init__.py); four test files (157 tests);
  docs/CACHE-GRAPH-CONTRACT.md (new normative contract);
  docs/CACHE-REWORK-LEDGER.md; ARCHITECTURE-for-agents.md +
  oap/strategic-instructions/ copy (three compact copies byte-equal;
  strategic copy synced in place, inode 10638621/mode 600 preserved);
  ARCHITECTURE.md; TESTING.md (per-invocation umask-022 child rule);
  unchanged activated order + oap/active.
- A2 (publication-review corrections, docs only): CACHE-IMPLEMENTATION-
  PLAN.md (worker baseline marked historical; current human RIGHT-only
  early-beta/xhigh continuity; restart only on true crash in RIGHT with
  exact codex --yolo --profile early-beta; no product-C inference; policy 3
  keeps same-directory mixed-eligibility unknown origin, off-graph no
  expansion, a-slice unresolved-origin vs future all-eligible common-base
  proof) and CACHE-REWORK-LEDGER.md (D-table normalized/escaped, current
  status vs accepted 017, 017/018 succession rows).
- B1/B2: packaging/dev_provenance_manifest.json only (217 inputs). Module
  bytes identical at B1/B2 (A2 docs-only). At B2: wheel
  08aa03b4a7fd4e9c94fbfc8ba33381924c210a8bb4febaa199218e4940b4a5e4
  204321 B/42 entries (unchanged B1->B2); sdist
  53f54c09cb936c5d23103ea04a6dd0925829f81ec8bda4d14c2a4f107868c822
  1218901 B/215 entries.
- Module sha256 at B2: graph_models
  0a31fa2a323bf51e306423cd2a9a192e317c058d81a0eb496908d0292917b314;
  references 2c7a51260ab58e22eb9f4e9f793e74fb05e5491ffb34ccf4088f3d02a2924ad2;
  graph 9a67557b33da42e5b980d6515f43ac83ccd3ee8f6c33b19a71b3b33180877a54;
  graph_observation
  64495071cbc75df88463f80b5dab51722b8b744815295763c45818fdcd3b9a57;
  bundles __init__ 3fcc1ed63bfe62c203c41e8ab7e16236886b2bad79f9a040c5120faf9f35eb77.
- Accepted 017 modules/grammars/regressions unchanged.

## Acceptance evidence
### G01 (recursive closure, cycles, stable identity, termination) — bounded subcriteria proven, inert
Root->A->B distinct-source arrival both orders and root-after-dependencies;
repeated links preserve occurrence evidence, same-occurrence edges
deduped; shared targets/self-cycle (true target depth 0)/multinode
cycles; deterministic stable output at/over EACH budget; typed conflicts
(COMPETING_ROOTS, VERSION_CONFLICT) without forged source/edge;
whole-bundle proof consistency (ordered members + whole digest + original
carrier intervals; no singleton exemption; mixed member counts and
reversed order refuse without retaining source). Evidence:
graph-lowlevel-v2 15/15, root-edge-depth-v2, graph-public-v4 176/176
(both endpoints, root-first/last, explicit+derived contexts, exact
digests/char/UTF-8 lengths), seam-mismatched-positive-v2,
seam-equal-bytes-different-spans-v3, seam-multi-member-v3 2/2,
seam-cross-arity-and-record-privacy-v4 2/2, public-bounds-v2 3/3,
public-diagnostic-total-v2, public-noio (13 entrypoints blocked, 0
attempts); focused tests.
### G02 (referring-directory resolution, ambiguous origins) — bounded subcriteria proven
All four reference forms (inline/angle/title, definitions, backtick,
plain) with exact char/UTF-8 spans; nested referring-directory ./ and
safe ../; workspace lookalike/escape rejected, no filesystem oracle;
Unicode width 2/3/4-byte matrix at/over bound; overlong whole-token typed
refusal (no safe-prefix minting); same-physical-occurrence positives
deduped once; same-directory mixed eligible/background and overlapping
multi-member positives yield explicit unresolved-origin records (no
edges); bounded accounted search work (max window 16 = declared budget;
constant 3-B prefix copy; no exceptions). Evidence: scanner-probe-v6
15/15, scanner-boundaries-v5 8/8, unicode-width 30/30, high-bmp-v4/v5
5/5 each, label-work/all-search-work/repair-regression-v4 bounded
measurements, seam-multi-member-v3,
seam-equal-bytes-different-spans-v3; focused tests.
### S01 (namespace isolation) — bounded subcriteria proven, inert
Namespace component isolation; workspace required, noncanonical
rejected (not silently canonicalized); effective bounds/version binding
recomputed against actual identity/config/bounds/workspace; canary-safe
repr/validation errors preserving 017 base semantics; no cross-namespace
reuse path. Evidence: model-probe-v2 5/5, public-negative 44/44,
graph-result-privacy-v2 3/3; focused tests.
### Observation seam (attributable source through accepted 017 surfaces) — bounded subcriteria proven
Public composition re-derives source proof via accepted 017
observe_request (legacy reads + native processes): pinned-native
WITH-token-line is legacy-NEGATIVE yet independently process-POSITIVE;
WITHOUT-token-line both-positive deduped once; chunked singleton from
original piece carriers; real empty singleton; non-attribution COMPLETE;
partial/truncated/nonzero/running/conflicting/missing-origin surfaces
acquire no source/edges. Evidence: chat-native-chunk-fixture 4/4 (earned
017 known-synthetic fixture; two original carrier occurrences; exact
digest), public-negative 44/44, public-noio.
G01 and the proven G02/S01 subcriteria are implemented/inert, PENDING
strategic acceptance.

## Verification
WAL = /home/janezp/oap-018a-work (protected 0700).
### Current round at clean B2 (final-gate-am2/, clean-build-am2/)
- Fifteen ordered commands, ONE foreground managed driver (2030919,
  ppid 2030917 -> RIGHT 598258; uid 1001; umask 0077 self-logged;
  22:23:37Z-22:33:57Z 2026-10-31); protected separate stdout/stderr/
  actual exit per command; all actual exit 0; gate.exit=pass; managed
  session returned terminal GATE-AM2-EXIT=0 (observed via pane; ROOT
  does not own/poll that handle). Command 07 only: process-local child
  umask 022 (nonroot). Exact live driver->uv->pytest births/UID/umasks
  independently retained in ROOT files reviews/018-a-b2-live-gate-
  observation-v1.json and -uv-children-v1.json.
  1 uv lock --check: PASSED(0); 2 uv sync --frozen --extra dev:
  PASSED(0); 3 ruff check: PASSED(0); 4 ruff format --check: PASSED(0);
  5 mypy src tests: PASSED(0); 6 docs_consistency_check: PASSED(0); 7
  pytest -q: PASSED(0) — 3947 passed, 28 skipped, 609.30s; 8 uv build:
  PASSED(0); 9 artifact_policy_check --inspect: PASSED(0); 10
  artifact_policy_check --install-smoke: PASSED(0); 11 python
  --version: PASSED(0); 12 compileall: PASSED(0); 13
  dev_provenance_manifest --verify: PASSED(0) (state=development
  head=06ca21c5ff47); 14 bash -n oap/bin+packaging scripts: PASSED(0);
  15 git diff --check ffaabf4b HEAD: PASSED(0).
- Focused four test files: PASSED 157/157 in 0.80s
  (W18/focused4-w18-final1.out).
- 24 probe families (W18 *-w18-final1): executed 2026-10-30
  07:26:55-07:27:07Z, PRECOMMIT (A1 07:33:07Z/B1 07:34:30Z); the tested
  source bytes match the final committed modules (module hashes identical
  through B2; A2/B2 docs-only) — sufficient source binding for unchanged
  code, cited with exact source hashes, not relabeled fresh executions.
  Aggregate: 332 rows = 323 passed=true verdicts + 9 booleanless bounded
  measurement rows (4 bounded-search, 2 label-window, 2 prefix-copy, 1
  short-angle/no-exception; two overlong-angle rows carry passed=true
  within the 323); plus 5 single-verdict files, all passed=true. Zero
  failures. Headline: graph-public-v4 176/176, public-negative 44/44,
  unicode-width 30/30, scanner-probe-v6 15/15, graph-lowlevel-v2 15/15,
  boundaries-v5 8/8, high-bmp v4/v5 5/5, model-probe-v2 5/5,
  chat-native-chunk-fixture 4/4, seam families 2/2 each, public-bounds-v2
  3/3, privacy 3/3.
- Clean archive build (clean-build-am2, one run 22:34:44Z; fail-closed
  script pid 2077319 umask 0077, literal exact-B2 guard, refuse
  pre-existing paths): git archive of B2 -> 798 files (archive 17971200
  B) exit 0; extract exit 0; uv build exit 0 (full build.out/build.err
  retained); BOTH artifacts byte-identical to manifest (gate cmd09).
- Artifact proof, two-part (honest):
  (1) Original invocation `python3 ... | tail -30` masked the Python
  exit (echo reported tail's status); original
  clean-build-artifact-proof.json (38530 B; visible assertions passed)
  preserved unchanged; original Python exit UNKNOWN — not claimed.
  (2) ONE direct finite read-only re-verification on the SAME
  already-built artifacts (no rebuild): artifact-proof-direct-v2.py +
  proof-direct-v2-driver.sh (22:37:56-22:37:57Z; driver 2083069; umask
  0077; no pipeline; err 0 B; "ALL PROOF ASSERTIONS PASSED") actual rc 0;
  result clean-build-artifact-proof-direct-v2.json (38654 B): 217/217
  manifest inputs == Git B2 == clean extracted tree (798 files); sdist
  214 source entries == Git B2 + PKG-INFO generated (22728 B,
  6203857c01e28f8449586465b0c775cbce78e793ad726a1f821c104eda297674, raw
  bytes == wheel METADATA); wheel 36 runtime + 6 dist-info entries;
  RECORD 41 entries + self row digest/size verified; entry_points ==
  pyproject [project.scripts]; LICENSE/NOTICE byte-equal;
  reconciliation explicit (sdist adds .gitignore; git-B-minus-sdist:
  .dockerignore, Dockerfile, release-image.yml, compose*.yaml and top-
  level docs — same pattern as the accepted 017 proof).
- Historical (B1 round, preserved, not relabeled): final-gate-am1/
  15/15 (driver 1120303, 07:36:10-07:46:18Z 2026-10-30; 3947/28/
  597.03s) and clean-build-am1/ (07:53Z, pid 1163517; proof JSON at its
  recorded status) at B1 0c626288.
- Development full suite (dirty tree, historical, NOT the gate): 3945
  passed/28 skipped/2 failed in 612.67s; both failures are provenance
  tests refusing DIRTY/UNTRACKED mapped inputs; they pass at committed
  clean B2 (gate cmd07).
- THREE safe-evidence/native-fixture development test failures (two
  safe-evidence + one native) closed as environment diagnosis: every
  pytest invocation needs its own nonroot child umask 022 (TESTING.md
  lines 28-42); fresh explicit child 022 -> exit 0, 3 passed in 0.93s
  (W18/three-tests-umask022-w18.out); no validator/test/helper change.

## Live model/service evidence
NOT RUN. No live model/gateway/protected-service call this round; no
client/model/service startup.

## GitHub CI / required checks (implementation head B2)
test PASS; docker PASS; docker-published PASS; operator-session PASS;
gateway-contract PASS; cache-native-fixture PASS; cache-native-
containment PASS; CodeQL PASS; Analyze(python) PASS; Analyze(actions)
PASS (runs 41247916549/41247912911; queried 2026-10-31 22:47 UTC;
independently re-checked by ROOT reviews/018-a-b2-gate-and-ci-review-
v1.json). All required green at drafting: yes. Report-head checks may be
pending; strategy verifies.

## Local setup/dependencies
uv frozen lock/sync, Python 3.12 repo venv; no new dependencies; no
repo-local service; no sudo.

## Documentation
Updated in the same PR: docs/CACHE-GRAPH-CONTRACT.md (new: namespace
caller trust — canonical workspace required/rejected, source
provenance/overlap dedup, reference grammar/origin/closure, bounds with
real numeric defaults, conflict/version limits, public API);
docs/CACHE-IMPLEMENTATION-PLAN.md (A2); docs/CACHE-REWORK-LEDGER.md
(A1+A2); ARCHITECTURE-for-agents.md (three compact copies byte-equal;
strategic copy in place); ARCHITECTURE.md; TESTING.md (per-invocation
umask-022 child rule, lines 28-42).

## Safety/scope confirmations (product-scope compliance)
- Unrelated files: none. No refactor, workflow, lock, or dependency
  change.
- Tests/evidence intentionally contain known-synthetic payloads; no
  actual private/customer/credential corpus is present in report, tests,
  or evidence.
- Protected 18020/Qwen/Codex fixture changed: NO. No live service
  touched.
- Scope deviation: none. Extra objective PR: NO. Coding merge: NO.
  Active/order edited: NO (order sha256
  1181f46e6f5615e8c8cf542df3fe44db9d392d1a67d4520c7ad616c08adc6441
  30793 B; active 6fcad907fca4575ed70a7713f818b2f07c5f224cf52e2e8eb8743331fae2fff5
  6 B b'018-a\n'; committed unchanged at A1 and locally verified at B2;
  post-push remote verification is the approved procedure to execute,
  not yet performed).
- AT DRAFTING TIME the report publication commit (SELF) had not yet been
  created; on execution after approval, the approved publisher/verifier
  will enforce (in-memory, post-push): report-only change (exactly the
  canonical report path), sole parent B2, report blob sha256 == approved
  draft sha256, order/active byte equality, and remote PR26 head == SELF
  (checks L1-L5/R1-R4).

## Process qualifications (separate from product-scope compliance)
1. am2 original artifact-proof invocation was pipe-masked (python|tail):
   original Python exit UNKNOWN; resolved by one direct read-only proof
   on the same artifacts (actual rc 0, fresh protected captures);
   original script/JSON/output preserved unchanged; no rebuild.
2. driver_boot_ticks empty in both am1 and am2 gate-driver-meta.json
   (awk field-read quirk on /proc directory listing); driver pid/ppid/
   uid/umask self-logged in-file; exact live births/UID/umasks
   independently retained by ROOT (B2 live observation files; am1 by
   live-obs-final.txt /proc descent).
3. Stage-specific live-observer corrections: am1 — a one-off live
   observer misreported the driver as GONE (its own parse bug); driver
   verified alive by direct /proc descent (live-obs-final.txt). am2 —
   the worker's first stat observer indexed the wrong birth field, then
   corrected it while live; ROOT's exact live B2 driver->uv->pytest
   chain is retained independently (B2 live observation files).
4. am1 historical qualification: its prepared build.sh initially carried
   EXPECT_HEAD pointing at a 017 SHA (sed typo during preparation);
   corrected before first execution; single run only.
5. Evidence origin/modes (per-file in inventory v2): W18 probe .py are
   ROOT-authored probe scripts copied to W18 or coding-authored
   development scripts (0664 tool-created or 0600 protected runs);
   result .json O_EXCL 0600 or 0664 tool-created; .out captures are
   shell-redirect 0664; gate/build/proof drivers run umask 077 with
   0600/0700 captures. No blanket all-manual O_EXCL/0600 claim; no
   retroactive mode/history repair.
6. W18 focused/full-suite .out files are development captures, not gate
   evidence.

## Known limitations / NOT RUN / PENDING
- Inert slice: graph foundation is not wired into any request path; no
  v1 runtime delivered; legacy runtime/grammar/settings unchanged.
- NOT RUN (mandatory, later 018 suffixes or other objectives): 018-b/c
  admission (lean/greedy), bundle keys, current version/replay/overlap;
  G03-G05/C01/C02/C04-C06 unearned; 019 RAM/service; 020 recovery; 021
  tokenizer/compiler; 022 transactional wire; 023 full stack; 024
  actual model/genuine client.
- Whole-018 acceptance: PENDING. G01/G02/S01 strategic acceptance:
  PENDING (this report is a claim, not acceptance).
- Probes are synthetic known fixtures: no actual trace, no
  external-exploit or runtime-security claim.

## Recommended strategic follow-up
Factual only: 018-b/c (admission/versions/replay/overlap) on the same
PR, then 019-024 per the roadmap; strategic acceptance decision on the
a-slice G01/G02/S01 subcriteria; whole-018 acceptance remains blocked
by b/c.

# OAP Coding-Agent Report — 018-e

## Work order
- Identifier 018-e; order `oap/orders/018-e-nonroot-currentness-overlay.md`; objective 018
- PR mode: AMENDED_EXISTING_PR (PR 26, branch `oap/018-cache-graph-bundles`)

## Status
COMPLETE

## Executive summary
Implemented the pure nonroot currentness overlay over the ACTUAL retained
018-d causal-history state and namespace: ACTUAL-field revalidation
(SEVEN inherited versions, both admission keys and both history scope keys
recomputed; coherent unsupported versions refuse REFUSED_VERSION_CONFLICT
before interpretation; early fences O(1), later scans charged); per-path
currentness rows (STALE/CURRENT_KNOWN/CURRENT_OPAQUE/CONTENT_CONFLICT/
OWNERSHIP_AMBIGUITY, every closed blocker and witness retained, worst-
priority status, no last-writer shortcut); the MAXIMAL completed-
occurrence frontier under the ACTUAL frozen partial order (chronology only
from frozen parent edges — never a clock; unissued facts add no edge of
their own; replay never reclassifies); the reverse path index retaining
EVERY overlapping occurrence; the versioned opaque-group recipe (group-
local semantic shape plus bound policy/proof/observation versions; never
principal/session keys; full-proof coordinates are provenance, not
inequality); content-key/occurrence/revision identity separation; six bounds on one
shared per-derivation work ledger with pre-copy/retention refusals and
exact-state atomicity. 017/018-a/b/c/d public behavior unchanged. New
contract plus ledger (incl. C04/C05 cells), human ARCH, three byte-equal
mirrors (S inode 10638621/mode 0600 preserved), TESTING and predecessor
intros reconciled (018-c/018-d ACCEPTED WITH process qualifications;
018-e pending; root-refresh authority-lineage contract reserved).

## Authoritative GitHub state
- ulfe-lmi/slaif-local-coding; PR 26 OPEN/non-draft; base `main`
  ffaabf4b4d9ce3a9cb7a48e12ab7d8847999adef
- Starting remote SELF `4959bd27e71d611745576db19a918e07c9fe0c61`
- Implementation head SHA: cdbeb9fc634cbfda014bbd739b7bddd7b8c80d51
- Report publication commit: SELF
- Implementation commits: `3c0039a0…` (kernel/models/tests/contract/
  docs/order+active), `cdbeb9fc…` (manifest-only B, 240 inputs)
- New PR this round: no; amended existing: yes; merge: NO

## Changes and files
- NEW (inert product): `bundles/currentness_models.py`, `bundles/currentness.py`
- NEW tests: `tests/test_currentness.py` (22 fns x 4 = 88), `tests/test_currentness_models.py` (20)
- NEW contract: `docs/CACHE-CURRENTNESS-CONTRACT.md`; reconciled:
  `docs/CACHE-CAUSAL-HISTORY-CONTRACT.md` and `docs/CACHE-BUNDLE-ADMISSION-CONTRACT.md`
  (accepted intros), `docs/CACHE-REWORK-LEDGER.md` (C04/C05 cells + 018 row),
  `ARCHITECTURE.md`, `ARCHITECTURE-for-agents.md` (+ two equal mirrors),
  `TESTING.md`
- TRANSCRIPT (strategic bytes unchanged): 018-e order (20556 B,
  sha256 565f0586…af4b76) and `oap/active` (`018-e\n`)

## Acceptance evidence (order criteria 1-8, all coding-executed)
1. PASSED: singleton v1->v2->genuinely descendant new v1 (replay no-op,
   FIRST provenance); unissued ambiguity; valid late receipt resolves.
2. PASSED: initial multi-version history; forks; delayed older outstanding
   result stays INCOMPARABLE (never latest-wins); reverse arrival — no
   arrival-based currentness.
3. PASSED: incomparable same-byte witnesses retained; descendant of one +
   changed bytes stays conflicting; descendant of BOTH resolves.
4. PASSED: AB->A / AB->AC / AB->A->newAB / old-AB replay; unknown-member
   equality-looking update conservatively STALE; AB vs BA equal aggregate
   bytes (equal group digest, distinct opaque identity); repeated A
   operands (ONE occurrence, two proven segments); boundary-proven vs
   boundaryless; standalone-vs-isolated opaque equivalence.
5. PASSED: complete empty descendant current-empty (not unacquired);
   pending RUNNING / TRUNCATED / nonzero never supersede completed;
   global immutable per-call result/completion/session facts (same-length
   byte, status or resegmentation mutation refuses; old-prefix replay
   no-ops).
6. PASSED: unrelated B leaves A's path record and ACTUAL 018-c content key
   byte-identical; partial proof groups independent; no spliced pseudo-
   source or invented per-file hashes.
7. PASSED: six bounds at-limit/one-over (work 19/47/82 unissued; issued
   chain 84/83 with 3 parent links; relation pairs 4/3; paths 2/1; groups
   2/1; witness memberships 18/17 on 3 forks; diagnostics 4/3), pre-copy
   sentinels, shared ledger, exact-state refusals; malformed/foreign/
   coherent-unsupported version refusals (actual recomputed keys, all 7
   versions); immutable inputs; private reprs; no host IO on public paths.
8. PASSED: focused regression 1663 passed (all test_bundle_*, causal and
   currentness suites, direct actual exit 0); 017/018-a/b/c/d public
   contracts unchanged.
ROOT-executed independent 018-e probes at their recorded hashes (52
original-API, 18 relation, 10 namespace, 56 resource, 84 privacy/purity,
8 duplicate-work, 8 empty/nonzero, 16 version-guard, 20
delayed-outstanding, 9/10/11 record-invariants) are ROOT executions, not
coding-executed; durable in-repo regressions exist.

## Verification
- Qualified 15-command gate (ONE foreground managed run at clean B
  cdbeb9fc): PASSED — all 15 commands rc 0, terminal 0 (20:46:31Z–
  20:57:09Z; real PID/ppid/uid/umask metadata, parent 0077, cmd07 child
  0022, clean tree at B): `uv lock --check`; `uv sync --frozen --extra dev`; `ruff check
  .`; `ruff format --check .`; `mypy src tests` (147 files);
  `docs_consistency_check.py` (19 claim docs); nonroot umask-022
  `pytest -q` = 4736 passed, 28 skipped (625.88s); `uv build`;
  `artifact_policy_check.py --inspect`/`--install-smoke`;
  `python --version`; `compileall -q src tests oap/bin scripts`;
  `dev_provenance_manifest.py --verify --dist dist`; `bash -n` oap/bin +
  packaging *.sh; `git diff --check ffaabf4b… HEAD`.
- Focused (direct actual exits): new suites 108 passed; full focused set
  1663 passed; `ruff check` / `ruff format --check` (640 files) /
  `mypy src tests` (147 files) clean; `docs_consistency_check.py` OK
  (19 claim docs).
- Clean BOTH-artifact proof at exact B: PASSED (actual rc 0, 20:57:54Z–20:57:57Z) — wheel 2f23fca0…/50 + sdist
  1a09009c…/238 byte-identical to manifest AND repo gate dist (829 Git-B
  files; 240/240 manifest inputs vs Git B and clean tree); raw
  PKG-INFO == METADATA (22728 B); strict RECORD (49 rows); sdist
  generated .gitignore + the 4 Docker manifest inputs reconciled; 10/10
  assertion groups.
- Source-A CI (3c0039a0, run 41347044954): test job 3 FAILED / 4733 PASSED
  / 28 SKIPPED — all 3 are stale-development-manifest binding tests;
  operator-session and docker fail the same manifest-binding step.
  Expected at A by the manifest-only-B law; superseded by B; preserved;
  no rerun for labels.

## Live model/service evidence
NOT RUN (none ordered; no live upstream/model/Gateway calls; no facility
started).

## GitHub CI / required checks
All TEN implementation-B checks SUCCESS at cdbeb9fc…: test (8m22s),
docker, docker-published, operator-session, gateway-contract,
cache-native-fixture, cache-native-containment, CodeQL, Analyze (python),
Analyze (actions). All required green at drafting: yes; report-head checks
may re-run — strategy verifies.

## Local setup/dependencies
Repository venv via `uv` (frozen lock; no new dependencies); no sudo, no
services, no network beyond GitHub.

## Documentation
As listed: new versioned currentness contract; ledger C04/C05 cells and
018 row (018-d ACCEPTED, 018-e PARTIAL MECHANISM pending); predecessor
intros; human ARCH + compact e normative map/objective boundaries;
TESTING stage-018 paragraph; 3-way mirror byte-equality.

## Safety/scope confirmations
- Unrelated files preserved; no reset/clean; activated order/active bytes
  committed unchanged; report commit report-only (bound verifier)
- Secrets/raw content: none (hashes/counts/statuses only)
- Protected 18020/Qwen/Codex fixture changed: NO
- Skipped: 28 standard skips (recorded, not failures); no scope deviation
- Extra objective PR: NO; coding merge: NO

## Process qualifications (recorded, not relabeled)
- Actual no-/tmp deviation: `/tmp/tc_trunc.py` created by head redirection
  (0664), later emptied; known-synthetic test source only; no secret
  exposure identified; preserved as the actual fact.
- W18e manual sources exclusive 0600 under 0700 parent; measure-bounds
  lineage preserved as executed (v1 executed-with-syntax-error, 0664->0600
  chmod origin recorded; v2 import-fail; v3/v4 label-off; v5-v7 +
  measure-chain-v1 + measure-relpairs-v5 valid thresholds; debug-chain-
  v1/v2, smoke-rootctx-v1 diagnostics); executed bytes never overwritten.
- Focused runs captured via immediate `PIPESTATUS[0]` or direct
  foreground exit; no echo/tail pipeline status claimed as pytest exit.
- No /tmp PR-body scratch this round (018-d's remains a 018-d fact).
- Docs-only corrections this round (no kernel/test change): five contract
  wording fixes against the actual API (REFUSED_VERSION_CONFLICT name;
  SEVEN inherited vs three derived versions; scope key binds the supplied
  validated history key; opaque recipe binds no principal/session keys;
  N*(N-1) = charged identity-comparison WORK units of the one-occurrence
  fixture, distinct from the early-break dominance scan and from
  relation-query closure/cache shortcuts); the membership/chain docstring
  fix (skipping parent charges lowers the fixture total — not the
  unissued pair cost); ledger C04/C05 cell reconciliation.

## Known limitations/blockers
- 018-e PENDING strategic acceptance; inert; no v1 runtime claim.
- Remaining mandatory 018: current-version/overlap/edge-withdrawal
  (C04/C05 current-version acceptance; version-owned ordinary-edge and
  group-certificate withdrawal; current graph reachability/admission
  integration) plus the root-refresh authority-lineage contract; then
  019-024.

## Recommended strategic follow-up
Factual only: review/accept or refine 018-e at its bounded inert scope;
next numeric-018 rounds for current-version/overlap/edge-withdrawal and
the root-refresh authority-lineage contract; then 019-024.

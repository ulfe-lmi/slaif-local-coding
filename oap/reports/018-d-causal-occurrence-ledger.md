# OAP Coding-Agent Report — 018-d

## Work order
- Identifier 018-d; order `oap/orders/018-d-causal-occurrence-ledger.md`; objective 018
- PR mode: AMENDED_EXISTING_PR (PR 26, branch `oap/018-cache-graph-bundles`)

## Status
COMPLETE

## Executive summary
Implemented the inert original-API causal-occurrence ledger over the
accepted 018-b proof core: causal-history scope over the ACTUAL accepted
admission namespace (factory AND direct construction revalidate actual
fields/keys), the strict `causal-arguments-json/v1` argument-fingerprint
recipe (before-copy byte/node/depth charging), immutable
`CausalHistoryState`, the original-payload observation transition (root
bootstrap; SAME-lineage rootless reuse; every distinct complete nonroot
occurrence retained; exact/shifted replay no-ops with FIRST provenance;
pending process pieces with the initial-EXEC owner law), trusted INTERNAL
issuance/receipt with frozen parent frontiers, the bounded
SAME/BEFORE/AFTER/INCOMPARABLE/UNKNOWN relation query (temporal edges only
from actual frozen parent evidence; unissued facts add no edge of their
own), and 14 history bounds with one shared per-transition work ledger.
017/018-a/b/c public behavior unchanged (private `_proof_collect`/
`_apply_conflict_policy` factoring only). New versioned contract plus
ledger/human-ARCH/three-equal-mirrors/TESTING reconciliation (018-c
accepted; 018-d pending acceptance; root-refresh authority-lineage
contract named as remaining 018 work).

## Authoritative GitHub state
- ulfe-lmi/slaif-local-coding; PR 26 OPEN/non-draft; base `main`
  ffaabf4b4d9ce3a9cb7a48e12ab7d8847999adef
- Starting remote SELF `d976a9a6f121b700cf9e023135cf10896d6f7203`
- Implementation head SHA: a193396281140cdb2a20d704f8706e2586fe0cad
- Report publication commit: SELF
- Implementation commits: `09592ee7…` (kernel/models/tests/order+active
  transcript/docs), `f75f4d34…` (wording precision per strategic review
  v2), `b41990cd…` (ruff-format repair after the first B's CI failure),
  `a1933962…` (manifest-only B, 235 inputs)
- New PR this round: no; amended existing: yes; merge: NO

## Changes and files
- NEW (inert product): `bundles/causal_history_models.py`,
  `bundles/causal_history.py`
- CHANGED (private factoring only; 018-b/c public behavior byte-identical):
  `bundles/bundle_proof.py`
- NEW tests: `tests/test_causal_history.py` (218),
  `tests/test_causal_history_models.py` (116); EXTENDED
  `tests/test_bundle_admission.py` (durable 72-control old-API inherited-
  limit regression port)
- NEW contract: `docs/CACHE-CAUSAL-HISTORY-CONTRACT.md`; reconciled docs:
  `docs/CACHE-REWORK-LEDGER.md`, `docs/CACHE-GRAPH-CONTRACT.md` (s8),
  `ARCHITECTURE.md`, `ARCHITECTURE-for-agents.md` (+ two equal mirrors;
  S mirror inode 10638621/mode 0600 preserved in place), `TESTING.md`
- TRANSCRIPT (strategic bytes unchanged): the 018-d order (24485 B,
  sha256 b4d06675…f7bc) and `oap/active` (`018-d\n`)

## Acceptance evidence (order criteria 1-8, all coding-executed)
1. PASSED: root bootstrap, idempotent root, valid prior-root rootless read
   vs empty/forged/foreign refusals; body-spoofed receipt flags inert,
   legitimate INTERNAL receipt anchors (both endpoints/modes).
2. PASSED: exact replay at shifted positions (`REPLAY_POSITION_SHIFTED`
   no-op, FIRST provenance); same-ID changed args/name/family/result
   conflicts; missing/malformed (incl. numeric) IDs typed non-acquiring;
   known vs equal-unknown relations.
3. PASSED: A-v1 -> trusted descendant A-v2 -> genuinely descendant new
   A-v1 (old-v1 replay no-op); unissued fresh ID unanchored/incomparable;
   initial multi-version history unordered by batch position; unrelated B
   leaves A's proof byte-exact and A's actual 018-c content key unchanged
   under the same actual namespace.
4. PASSED: sibling forks; late older original result never AFTER from
   arrival; valid late receipt vs changed binding/unknown parent/cycle;
   registration order/revision never a clock.
5. PASSED: native chunk and empty complete sources (retained completed
   occurrence, NOT a cache admission); pending->complete polling with
   INITIAL EXEC frontier only; unsupported/truncated/nonzero unacquired;
   global per-poll immutable result/completion facts; old-prefix replay
   no-op; first result provenance.
6. PASSED: all 14 bounds at-limit/one-over; cumulative duplicate/result/
   member/source/frontier/work accounting; pre-copy/retention refusals;
   revision overflow/CAS; input/old-state immutability; private repr/
   errors; no host IO after setup.
7. PASSED: strict canonicalization positives (stdlib-verified where
   semantics match) and duplicate-key/nonfinite/depth/node/byte/Unicode
   negatives with before-copy encode/construction sentinels; hashes not
   raw args.
8. PASSED: all 017/018-a/b/c suites green in the full gate; old conflict
   predicates/statuses and same-occurrence proof identity preserved;
   inherited 72-control matrix (old API) plus 64-control new-composition
   matrix (graph-node closure explicitly outside this stage).
ROOT-executed independent probes (96 pending/native + 64 inherited-limit
+ 60 causal-operations at the 5a684aeb-family kernel hash; older named
scopes at their own recorded hashes) are ROOT executions, not
coding-executed; durable in-repo regressions exist for the named cases.

## Verification
- Qualified 15-command gate (ONE foreground managed run at clean B
  a1933962, real PID/birth/UID/PPID/umask metadata; parent umask 077,
  cmd07 child 022): PASSED — all 15 commands rc 0, terminal 0
  (16:53:57Z-17:04:31Z): `uv lock --check`; `uv sync --frozen --extra
  dev`; `ruff check .`; `ruff format --check .`; `mypy src tests` (143
  files, no issues); `docs_consistency_check.py` (19 claim docs);
  nonroot umask-022 `pytest -q` = 4628 passed, 28 skipped (620.73s);
  `uv build`; `artifact_policy_check.py --inspect` + `--install-smoke`;
  `python --version`; `compileall -q src tests oap/bin scripts`;
  `dev_provenance_manifest.py --verify --dist dist`; `bash -n` over
  oap/bin + packaging *.sh; `git diff --check ffaabf4b… HEAD`.
- Focused (direct actual exits): the two new suites 338 passed (rc 0);
  re-verified after the whitespace repair (rc 0).
- Clean BOTH-artifact proof at exact B: PASSED (actual rc 0) — wheel
  644e2e16…/48 + sdist 45be2f0c…/233 byte-identical to manifest AND repo
  gate dist; 235/235 manifest inputs vs Git B and clean tree; raw
  PKG-INFO == METADATA (22728 B); strict RECORD; 10/10 assertions.
- Superseded B `86a643ea…`: GitHub `test` job FAILED on
  `ruff format --check` (two wrapping lines); preserved as recorded
  failure; repaired at `b41990cd…`; no rerun for labels.

## Live model/service evidence
NOT RUN (none ordered; no live upstream/model/Gateway calls; no model/
native/client/service facility started).

## GitHub CI / required checks
All TEN implementation-B checks SUCCESS at a1933962… (observed before
report): test (7m36s), docker, docker-published, operator-session,
gateway-contract, cache-native-fixture, cache-native-containment, CodeQL,
Analyze (python), Analyze (actions). All required green at drafting: yes;
report-head checks may re-run — strategy verifies.

## Local setup/dependencies
Repository venv via `uv` (frozen lock; no new dependencies); no sudo, no
services, no network beyond GitHub.

## Documentation
Updated as listed under Changes (new versioned contract; ledger G/C rows
and 018 stage row with 018-c accepted status and C05 PARTIAL at the 018-d
bounded scope; graph-contract section 8; human ARCH scope paragraphs and d
summary; compact d normative map and objective boundaries; TESTING stage-
018 paragraph).

## Safety/scope confirmations
- Unrelated files preserved; no reset/clean; activated order/active bytes
  committed unchanged; report commit report-only (verified by the bound
  verifier)
- Secrets/raw content: none (hashes/counts/statuses only)
- Protected 18020/Qwen/Codex fixture changed: NO
- Skipped: 28 standard skips (recorded, not failures); no scope deviation
- Extra objective PR: NO; coding merge: NO

## Known limitations/blockers
- 018-d PENDING strategic acceptance; inert (never active in the
  adapter); no v1 runtime claim.
- Remaining mandatory 018: current-version/overlap/edge-withdrawal
  (C04/C05 current-version acceptance; version-owned ordinary-edge and
  group-certificate withdrawal) plus the explicit root-refresh authority-
  lineage contract; then 019-024.
- The clean-build proof JSON was written under the template-inherited
  filename `clean-build-artifact-proof-c1.json` in the W18d clean-build-d
  root (mechanical naming leftover; content/head are 018-d).

## Recommended strategic follow-up
Factual only: review/accept or refine 018-d at its bounded inert scope;
next numeric-018 rounds for current-version/overlap/edge-withdrawal and
the root-refresh authority-lineage contract; then 019-024.

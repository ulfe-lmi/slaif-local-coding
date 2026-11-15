# OAP Coding-Agent Report — 018-c

## Work order
- Identifier: 018-c; order path: `oap/orders/018-c-bundle-admission-and-identity.md`; numeric objective 018.
- PR mode: AMENDED_EXISTING_PR (PR 26, branch `oap/018-cache-graph-bundles`).

## Status
COMPLETE

## Executive summary
Delivered the inert 018-c bundle-admission and structural-identity slice on PR 26: a pure, bounded original-API composition of the accepted 017 observation, the 018-a root binding and the accepted 018-b bundle-proof bridge into lean/greedy admission with a first-class required root entry, group-owned certificates with least-complete-derivation AND/OR depth, canonical structural content keys and a complete reverse member-path index. All local gates, the 10 exact-B CI checks and one clean BOTH-artifact build+proof are green at head B. The slice is PENDING strategic acceptance; no v1 runtime, compiler-hit or recovery claim.

## Authoritative GitHub state
- Repository: `ulfe-lmi/slaif-local-coding`; PR 26 https://github.com/ulfe-lmi/slaif-local-coding/pull/26 OPEN/non-draft, base `main`.
- Starting remote SHA (018-b SELF): `6b9119f0092a55666b976ec6aa2dcbb66e202348`.
- Implementation head SHA: 8fce0156bfdc3d6acd71fce33923f20190a40385
- Report publication commit: SELF
- Implementation commits pushed before report: A `cd938ea2d3a8d4d72a2ef7a0b942a08f26a915d1` (19 source/doc/transcript files) and B `8fce0156bfdc3d6acd71fce33923f20190a40385` (manifest-only, 230 inputs).
- New PR this round: NO; amended existing: YES; merge performed: NO.

## Changes and files
19 files at A: new `bundles/bundle_admission.py` + `bundle_admission_models.py`; `__init__.py` exports; `bundle_proof.py` cohesive `_proof_pass` factoring (public 018-b wrapper unchanged); new `tests/test_bundle_admission.py` + `tests/test_bundle_admission_vectors.py` (251 tests, including the 208-item 104-case × {lean,greedy} known-synthetic original-input matrix and the matrix self-identification test, over verbatim S vector fixtures retained under `tests/fixtures/cache_admission/v1/`); NEW `docs/CACHE-BUNDLE-ADMISSION-CONTRACT.md` (`cache-bundle-admission/v1`) plus ledger, human ARCH, both compact mirrors, TESTING and the proof-contract stage section reconciled to the actual stage (018-a/018-b ACCEPTED at bounded inert scopes with process qualifications; 018-c implemented, pending strategic acceptance); exact activated order + `oap/active` transcript.

## Acceptance evidence
- G03-G05 (admission): original-API truth table, both endpoints/modes — all-eligible whole both modes; mixed boundaryless lean-refusal/greedy-whole with per-occurrence authority; lean proven-group admission with the no-A+C-splice AB|C control (isolated-C key = standalone-C key); zero-eligible refusal; group-depth preemption and descendant/certificate relaxation — `tests/test_bundle_admission.py`.
- Structural C01/C02/C06: entry interning (AB then A then identical A → two FILE entries + root entry, reused key identity; NOT a compiler hit); ordered A/B/A+A independent keys; same-aggregate/different-ownership inequality; root-vs-file same-byte key inequality; duplicate-root idempotence; unknown-hash/no-splice provenance — both admission test modules.
- Continuing G01/G02/S01: 018-a/018-b regression suites unchanged and green (157 graph + 88 proof tests; whole-017/018 suites in the full gate).
- Bounds (per snapshot): admission defaults AND hard ceilings 128/1024/4096/64, wider construction refused; every bound at-limit succeeds, first-over refuses whole-empty (no partial admission); direct namespace key forgery refused by recomputed keys; five actual version refusals; scoped stage diagnostic law with the admission TOTAL cap; purity/privacy/unchanged-payload asserted — named tests above.

## Verification
- Exact 15-command local gate at B (fresh `W18c/final-gate-c/`; driver 0700, parent umask 077, cmd07 child umask 022, exclusive 0600 captures, no pipe masking): all 15 commands rc 0, actual terminal driver exit 0 — lock check; frozen sync; ruff check; ruff format --check; mypy src tests; docs_consistency_check; nonroot-022 pytest -q; uv build; artifact inspect + install-smoke; python --version; compileall; dev_provenance_manifest --verify --dist dist; bash -n over oap/bin/*.sh packaging/*.sh; git diff --check vs main base. PASSED (evidence: `gate-driver.log`, per-command exit files, `gate-driver-meta.json`).
- `uv run --frozen pytest -q` (gate cmd07, nonroot child umask 022): PASSED — 4286 passed, 28 skipped in 617.18 s (skip count unchanged from the 018-b final gate; per-test skip reasons not individually captured this round, so no categories are claimed).
- One clean git-archive exact-B BOTH-artifact build + direct read-only proof (fresh `W18c/clean-build-c/`; archive/extract/build step exits 0; proof actual exit 0, ALL PROOF ASSERTIONS PASSED): 815 Git-B files; all 230 manifest inputs byte-equal to Git B and the clean tree; sdist 228 entries (227 source + 1 generated PKG-INFO, 22728 B); wheel 46 entries (40 runtime + 6 dist-info, 45 verified RECORD rows); raw PKG-INFO == METADATA; entry points/licenses/NOTICE verified; clean and repo-gate artifacts byte-equal. PASSED.
- Focused suite: both admission modules PASSED (250 passed) at the pre-self-identification-test bytes; the final 251-test modules pass within the full gate at B (4286 passed, 28 skipped). mypy (139 files) and ruff format/check clean at the final bytes.

## Live model/service evidence
None: pure/inert slice; no live model/Gateway/Qwen-vLLM/adapter service call; no protected fixture touched.

## GitHub CI / required checks
All TEN exact implementation-head B checks completed SUCCESS: test, docker, docker-published, operator-session, gateway-contract, cache-native-fixture, cache-native-containment, CodeQL, Analyze (python), Analyze (actions). All required green at drafting: YES. Report-head checks may be pending; strategy verifies.

## Local setup/dependencies
`uv` frozen lock/sync, repo venv, Python 3.12; no new dependencies; no service/port/workflow/settings change.

## Documentation
NEW versioned contract `docs/CACHE-BUNDLE-ADMISSION-CONTRACT.md` (`cache-bundle-admission/v1`); stage ledger, human ARCH, both compact mirrors (byte-equal, strategic inode/mode preserved in-place) and TESTING reconciled to the actual stage; 018-c implemented inert slice pending strategic acceptance; whole-018 remainder and 019-024 mandatory and unearned.

## Safety/scope confirmations
- Unrelated files: none staged (A = 19 intended paths; B = manifest only).
- Secrets/raw content: none in report, commits, logs or evidence (synthetic fixtures only).
- Protected 18020/Qwen/Codex fixture changed: NO.
- Required tests skipped/not run: 28 skips in the full gate (count only, see Verification); no required layer NOT RUN.
- Scope deviation: none.
- Extra objective PR: NO; coding merge: NO; active/order edited: NO; report commit report-only: YES.

## Known limitations/blockers
- `docs/CACHE-GRAPH-CONTRACT.md` section 8 (last edited in 018-a's own round) still reads "018-a is inert implementation pending strategic review" — a stale status line outside this round's ordered documentation list; reported as a factual finding only.
- Process qualifications, this round (evidence preserved under `W18c/`): `regression/vectors-007` failed preparation before pytest ran (noclobber blocked a capture redirect; meta's `pytest_exit=1` spurious); `vectors-008` 249 pass/1 fail (pre-oracle-fix bytes); `full018-002` failed attempt (invented fixture filenames → pytest exit 4, no tests ran); `full018-003` 1211 pass/1 fail (fixture self-identification rule); two earlier helpers (`smoke-model-v3.py`, `factor-proof-pass-v1.py`) were executed then edited in place, so their preserved bytes are RECONSTRUCTED-qualified, not original observed-execution source; the pre-`reference_version` S probes are stale harnesses preserved as-is, the same properties covered correctly by the repository tests; the ROOT-executed independent probe cohorts (104 original-input preconditions, 186 semantic, 34 partition-key, 40 bound, 10 duplicate-group, 5 version, 10 diagnostic-scope, 62/61 segment-boundary, bounded malformed-totals) are ROOT's, never coding-executed; `clean-build-c/__pycache__` is a tool-generated artifact under the protected parent.

## Recommended strategic follow-up
Strategic acceptance decision for 018-c at its bounded inert scope; optional reconciliation of the stale 018-a status line in `docs/CACHE-GRAPH-CONTRACT.md` section 8; remaining same-018 chronology stages (C04/C05/version/edge-withdrawal, overlap/replay invalidation, remaining G/C/S) and objectives 019-024 remain mandatory.

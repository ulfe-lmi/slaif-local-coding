# OAP Coding-Agent Report — 019-c

## Work order
- Identifier: 019-c; order path `oap/orders/019-c-whole-ram-closure.md`; numeric objective 019
- PR mode: AMENDED_EXISTING_PR (PR27, no second PR)

## Status
COMPLETE

## Executive summary
Actual result: the whole-019 closure round is implemented at the
INERT injected-work layer over the ACTUAL accepted 018-p/018-t
records and the actual 019-a/019-b RAM owner/work plane. The
aggregate-pressure accounting (high-water shared-container
retention, staged-candidate atomic refusal, closed global pump
reservation), the bounded pre-accounted `owner_quarantined`
adverse-currentness fence, the substantial-source /
accumulated-history lifecycle over genuine accepted records
(both lean and greedy, both endpoints), the cancellation /
update / teardown races and the denied-filesystem lifecycle proof
are implemented and tested. The final 15-command gate at clean
manifest B passed 15/15 (full pytest 6668 passed / 28 skipped /
16 warnings / 851.46 s), one clean Git-B archive build produced
BOTH artifacts and the full strict artifact proof passed (exit 0),
and all TEN required GitHub checks are SUCCESS at exact B. No v1
runtime criterion is qualified; 020-024 remain mandatory. This is
a claim until strategic review; no acceptance or merge is
claimed.

## Authoritative GitHub state
- Repository: ulfe-lmi/slaif-local-coding; PR 27
  https://github.com/ulfe-lmi/slaif-local-coding/pull/27 (state open)
- Base: main c5eb299df822875988867bf34d58de239e82657e
- Head: oap/019-cache-ram-state 042c32036f65ca99181bcd302dc053edea99e058
- Starting remote report head: c8c606ebcd596481681d0f596511487d3e3a090f
  (019-b SELF)
- Implementation head SHA: 042c32036f65ca99181bcd302dc053edea99e058
- Report publication commit: SELF
- Implementation commits pushed before report:
  A 6da94835ff7fcc2b0e7ae157efb8fc35838e68a3 (clean source, 18
  files) and B 042c32036f65ca99181bcd302dc053edea99e058
  (manifest-only child, sole parent A, 286 manifest inputs)
- New PR this round: NO; amended existing PR27: yes; merge
  performed: NO

## Changes and files
A (vs starting head c8c606e), 18 files:
- `src/slaif_local_coding/constitution/bundles/ram_state.py`,
  `ram_state_models.py` (staged-candidate allocation, high-water
  shared table retention, quarantine fence),
  `ram_work.py`, `ram_work_models.py` (pump global reservation,
  staged candidate containers, quarantine carry-through, composed
  teardown);
- `tests/test_bundle_ram_lifecycle.py` (NEW, 13 tests x 4
  mode/endpoint params = 52 cases), `tests/test_bundle_ram_state.py`,
  `tests/test_bundle_ram_work.py` (focused extensions);
- docs: `docs/CACHE-RAM-STATE-CONTRACT.md`,
  `docs/CACHE-RAM-WORK-CONTRACT.md`, `docs/CACHE-REWORK-LEDGER.md`,
  `ARCHITECTURE-for-agents.md`,
  `oap/strategic-instructions/ARCHITECTURE-for-agents.md` (mirrors
  byte-identical; S mirror preserved in place at its existing
  inode), `ARCHITECTURE.md`, `TESTING.md`,
  `docs/ADAPTER-CONFIGURATION.md`, `docs/CACHE-IMPLEMENTATION-PLAN.md`;
- transcript: `oap/orders/019-c-whole-ram-closure.md` (added,
  unchanged bytes; sha256
  077e20bc8f6dcc5eeb3d30de6d911056808548c95be5c8b9ed888edaf02c3fc5),
  `oap/active` (019-b -> 019-c activated transcript).
B changes only `packaging/dev_provenance_manifest.json`.

## Acceptance evidence
### Criterion 1 (whole-019 composition over ACTUAL accepted records)
- PASSED at inert layer: `tests/test_bundle_ram_lifecycle.py`
  composes actual observation -> P -> T -> RAM owner -> injected
  work over the ACTUAL accepted 018-p/018-t records in both
  lean/greedy and both endpoints (4-param matrix, 52 cases);
  final scoped trio 160 passed (57.64 s), focused Ruff/format/
  mypy green. Ratified 019-b no-retry policy unchanged.
### Criterion 2 (aggregate pressure and lifecycle)
- PASSED at inert layer: every retained component (owners,
  catalogs, history tuples, queued/active tuples, waiters,
  terminal slots, coordinator shell, shared map table, queue) is
  charged before retention; the shared live-owner map table and
  queue charge are retained at their measured high water; new
  owner allocation and claim growth stage the ACTUAL complete
  candidate containers and check BOTH ceilings atomically before
  publication, so a refused admission/claim retains the original
  containers and counters exactly (resize-boundary first-over
  regressions included); exact-at/first-over tests use actual
  measured aggregate peaks with several retained owners; teardown
  reports the actual total process occupancy released by THIS
  teardown only, and unrelated owners/hits are preserved.
### Criterion 3 (substantial-source and accumulated-history usability)
- PASSED at inert layer: genuine complete substantial sources
  (including the accepted 32768-byte root-only shape) with
  accumulated legal history through the actual
  P -> T -> RAM -> work path; changed root/file, genuine
  compatible revert (payload reuse without a third invocation),
  unrelated eligible document, and the actual retained
  source/history sizes are recorded per case. No hard
  work/source ceiling was raised and no association validator
  weakened. Remaining scale limits are reported in the contracts
  (inert layer; not infinite-session readiness).
### Criterion 4 (adverse-currentness RAM boundary)
- PASSED at inert layer: genuine changed-root and changed-file
  adverse evidence -> validated capacity-refused candidate
  classified non-READY or withdrawing/rekeying retained current
  keys sets the bounded pre-accounted `owner_quarantined` flag;
  thereafter the old usable lookups refuse (fixed typed 409 /
  currentness refusal) and source-absent lookup/resolve cannot
  revive old usable state, while every retained byte and counter
  stays intact; the READY additive candidate preserving every
  retained current key is the non-adverse control (old usable
  state preserved exactly); replay cannot unblock; a genuinely
  proven supported recovery/revert restores usability under
  existing causal law; the complete-namespace fence is preserved
  on the new path; teardown is the only exit (no epoch reset, no
  retry, no unbounded journal).
### Criterion 5 (cancellation/update/teardown races)
- PASSED at inert layer: first/follower/all-waiters, queued and
  unstarted-dispatch cancellation (zero-invocation
  finalization), repeated cancellation while a teardown drain is
  held at an actually invoked cleanup barrier (teardown stays
  fenced until drain release, then propagates; no task/charge
  leak), stale/superseded late completion fenced without
  publication, teardown vs admission/resolve, and old owner/
  epoch vs newly acquired owner. ONE active leader, bounded
  queue/waiters, one claimed attempt per full key/epoch; no lock
  held across await.
### Criterion 6 (denied filesystem content IO)
- PASSED at inert layer: with 24 filesystem facilities trapped
  after genuine initial preparation, repeated owner lookups,
  work hits, retained-payload reuse, current selection and
  retained-graph/reverse-index traversal demonstrate zero content
  reads and zero new seam invocations; no recovery
  deserialization on the RAM path. Development diagnostic c25
  (a fixture asserting REFUSED where the actual post-teardown
  lookup law returns NOT_FOUND with EPOCH_FENCED, plus a live
  trap that masked pytest session cleanup) is preserved with its
  truthful native failure and was repaired via a scoped
  patcher; the final L6 cases pass under the repaired harness.
### Criterion 7 (ledger/contracts/mapping)
- DONE: `docs/CACHE-REWORK-LEDGER.md` rows C03/M01/M04/M05 mapped
  to the actual test suites at the inert injected-work layer with
  the TOK/REC/recovery halves NOT RUN at 020/021; both RAM
  contracts updated (high-water accounting, the single bounded
  quarantine exception, precise additive opt-in wording,
  truthful inert status); both architecture maps and the THREE
  compact mirrors updated byte-identically (S mirror inode
  preserved in place); TESTING/ADAPTER-CONFIGURATION/
  CACHE-IMPLEMENTATION-PLAN updated only as needed; new wheel
  RECORD count stated truthfully (71 total rows including the
  self row, 70 nonself digest/size rows); the immutable 019-b
  report was not edited. No new planning/audit document.

## Verification
- `uv run --frozen ruff check .` at B (gate6 cmd03): PASSED rc0
- `uv run --frozen ruff format --check .` at B (gate6 cmd04):
  PASSED rc0
- `uv run --frozen mypy src tests` at B (gate6 cmd05): PASSED rc0
- `uv run --frozen python scripts/docs_consistency_check.py` at B
  (gate6 cmd06): PASSED rc0
- `umask 022; uv run --frozen pytest -q` at clean B (gate6 cmd07):
  PASSED — 6668 passed, 28 skipped, 16 warnings in 851.46 s
- `uv build` at B (gate6 cmd08): PASSED rc0 (output capture lost
  to the driver label defect below; result independently
  verified by cmd10/cmd13 and the clean-B build+proof)
- `artifact_policy_check --dist dist --inspect` at B (gate6
  cmd09): PASSED rc0
- `artifact_policy_check --dist dist --install-smoke` at B (gate6
  cmd10): PASSED rc0 (fresh noneditable smoke, slaif-local-coding
  0.1.0)
- `python --version` (gate6 cmd11): 3.12.15 rc0
- `python -m compileall -q src tests oap/bin scripts` (gate6
  cmd12): rc0
- `dev_provenance_manifest.py --verify --dist dist` (gate6 cmd13):
  rc0 (state=development head=042c32036f65)
- `bash -n` all oap/bin/*.sh and packaging/*.sh (gate6 cmd14):
  rc0
- `git diff --check c5eb299df822875988867bf34d58de239e82657e HEAD`
  (gate6 cmd15): rc0
- Gate 6 (15-command) at frozen B: ALL 15 commands rc=0; private
  capture parent umask 077, actual pytest child umask 022;
  driver startup receipt retained (pid 3527068, birth 342423050,
  ppid 3527058, uid 1001, umask 0077, driver source sha256
  bf57bf7908b25b2efaa40f25bd0a17c3e59be3518b1de193da8061c582cb1bee,
  started 2026-11-16T06:40:12.488430+00:00). Qualification: the
  driver's `printf '%02d'` treated the string IDs 08/09 as
  octal, so both appear as `cmd00` in the summary and the second
  overwrote the first's stdout/stderr capture files; the ordered
  rc sequence is preserved (first `cmd00` row = cmd08 `uv build`,
  second = cmd09 inspect), command 08's output capture is lost,
  and the gate was NOT repeated for labels.
- One clean Git-B archive build (build-ram03.sh, 0700, sha256
  914fb8906b5ee6331b8bbfa43bb9e33c880bd7e92211bc9fbafd4f943f2045ab;
  driver pid 3570562, umask 0077): archive 24268800 bytes, 911
  files extracted, `uv build` rc0; wheel
  slaif_local_coding-0.1.0-py3-none-any.whl (672588 bytes,
  sha256 2310c310488246c6d8440dde08fdf59f209d94f2849e8bf36e52e20f19a1fd4f)
  and sdist slaif_local_coding-0.1.0.tar.gz (2323330 bytes,
  sha256 ad1dfb246039f49f052be3593c112a999af9782db073c93eb557a3450d3dbd97).
- Full strict artifact proof (artifact-proof-ram03.py, 0700,
  sha256 85989b6f667b029275ff26e2545a3782235cee8d06acf89493e9f4b720e1838e;
  helper pid 3570833, birth 342514908, ppid 3570817, uid 1001,
  umask 0077, started 2026-11-16T06:55:31Z): PASSED exit 0 —
  911 clean-archive files byte-identical to Git B; 286 manifest
  source inputs verified against Git A, Git B and the clean
  extracted tree; B verified manifest-only over A; sdist 284
  entries (283 source + 1 generated PKG-INFO); wheel 71 entries
  (65 runtime + 6 dist-info); RECORD full entry set with 70
  nonself digest/size rows verified (71 total RECORD rows
  including the self row with empty digest AND empty size);
  PKG-INFO == METADATA bytes; entry points exact; repo gate
  dist/ byte-identical to the clean artifacts.
- Final scoped RAM trio (state + work + lifecycle): 160 passed
  in 57.64 s; scoped L6 repaired harness: 4 passed in 2.65 s;
  focused Ruff/format/mypy green.

## Live model/service evidence
- NOT RUN — the order requires no live product tests in 019-c;
  no protected fixture touched.

## GitHub CI / required checks
- At implementation head B (042c32036f65ca99181bcd302dc053edea99e058),
  all TEN required checks exist and are SUCCESS: test,
  Analyze (actions), Analyze (python), CodeQL, gateway-contract,
  docker, docker-published, operator-session,
  cache-native-containment, cache-native-fixture.
- All required green at drafting: yes.
- Report-head checks may be pending; strategy verifies.

## Local setup/dependencies
- Python 3.12.15 via repo venv, `uv` lock/sync frozen; no new
  dependencies, services or configuration keys. No sudo needed.

## Documentation
- Updated in-round as listed under Changes and files; no new
  planning/audit document.

## Safety/scope confirmations
- Unrelated files: none touched; pre-existing work preserved.
- Secrets/raw content: none in report/PR/log; evidence uses
  hashes, counts and sanitized fixtures only.
- Protected 18020/Qwen/Codex fixture changed: NO.
- Required tests skipped/not run: 28 honest skips in the full
  suite (live-credential/UID-0/gateway-dependent); all v1
  runtime criteria NOT RUN (planned for 020-024).
- Scope deviations (preserved truthfully): the gate6 driver
  octal-label defect (above); an early in-development full-pytest
  diagnostic (2 failed / 6605 passed / 28 skipped, exit 1) ran on
  mutable source while tests were still being edited and is a
  non-final diagnostic; focused development failures c19 and c25
  are preserved with native exits; a scratch repeated-cancellation
  probe (native exit 143, owned shell ended) has UNKNOWN
  descendant cleanup and was replaced by the bounded in-product
  drain fixture; a brief broad /proc scan on 2026-11-16 ~06:05
  UTC exceeded the owned-lifetime boundary (no unowned process
  was killed; the printed "UID=3506106" was actually the stat
  PID field). No clean-host or no-deviation claim is made.
- Extra objective PR: NO; coding merge: NO; active/order edited:
  NO (order bytes committed unchanged, verified sha256
  077e20bc8f6dcc5eeb3d30de6d911056808548c95be5c8b9ed888edaf02c3fc5);
  report commit report-only: yes (verified at publication).

## Known limitations/blockers
- Inert layer only: no wire/HTTP (022), no recovery (020), no
  compiler/tokenizer semantics (021), no full-stack (023), no
  actual-model/genuine-Codex (024); the injected work seam is
  synthetic. Occupancy is a committed-occupancy measure, not a
  total-RSS promise. Remaining scale limits per the updated
  contracts.

## Recommended strategic review
- Strategic decision on whole 019 (019-b was NOT ACCEPTED against
  the complete accounting requirement per
  `S/reviews/019-b-decision.md`; this round supplies the
  remaining pressure/source-scale/lifecycle evidence at the inert
  injected-work layer). Next mandatory stages per the ledger:
  020 recovery, 021 compiler/tokenizer, 022 wire/transactional
  runtime, 023 full-stack, 024 actual-model/genuine-Codex.

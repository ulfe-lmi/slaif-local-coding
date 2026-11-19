# OAP Coding-Agent Report — 020-b

## Work order
- Identifier: 020-b; order path `oap/orders/020-b-cache-recovery-ownership-and-faults.md`; numeric objective 020
- PR mode: AMENDED_EXISTING_PR (PR 28)

## Status
COMPLETE

## Executive summary
Actual result: the 020-a ownership / fault corrections are closed at
the SAME INERT recovery-component scope on the same PR 28: (1) the ONE
writer-owned `RecoverySession` now serializes the ENTIRE generation CAS
and publication attempt — a competing same-handle publication is
refused `write_in_flight` before a second CAS or pointer mutation; (2)
an ordinary filesystem read fault is contained at the store boundary as
the typed `io_failure` with the BEST actual observed generation (never
a raw escape past owner teardown / session close; a failed epoch
binding removes the partially prepared owner and releases its
reservation and the writer, with the committed generation preserved
after rename); (3) the documented preemption gap between a
synchronous recovery operation's entry check and its claim to reserve /
operate on the live owner is closed by the claimed-owner fence on BOTH
direct teardown paths, with the established 020-a same-lock drain
refusal preserved. Deterministic barrier regressions were added; the
final 15-command gate at clean manifest B passed 15/15 (full pytest
6802 passed / 28 skipped / 16 warnings / 1325.84 s), one clean
Git-B archive build produced BOTH artifacts byte-identical to the gate
dist and manifest, and the full strict artifact proof passed (exit
0); all TEN required GitHub checks are SUCCESS at exact B. No v1
runtime, real-client or model criterion is qualified; 021-024 remain
mandatory. This is a claim until strategic review; no acceptance or
merge is claimed.

## Authoritative GitHub state
- Repository: ulfe-lmi/slaif-local-coding; PR 28
  https://github.com/ulfe-lmi/slaif-local-coding/pull/28 (state open)
- Base: main a62b87ddb9fe96a741aa4ce8932ca40adf6dc0eb (whole 019
  accepted/merged)
- Head: oap/020-cache-session-recovery
  4e4725d6044d46c78aed67421c1a21e93ce7537b
- Starting remote head at round start: 61b946911fea38d3ad32050228d576b51db17738
  (the 020-a report-only child of 0aa6634e3b4afc606090e445a5158ea12123fda8)
- Implementation head SHA: 4e4725d6044d46c78aed67421c1a21e93ce7537b
- Report publication commit: SELF
- Implementation commits pushed before report:
  A 9540a0266e81f365bef5318568ef33bc4756ece6 (source, 14 files) and
  B 4e4725d6044d46c78aed67421c1a21e93ce7537b (manifest-only child,
  sole parent A, 294 manifest inputs)
- New PR this round: NO; amended existing PR 28: YES; merge performed: NO

## Changes and files
A (vs starting head 61b9469), 14 files:
- `src/slaif_local_coding/constitution/bundles/recovery_store.py`:
  the ONE writer-owned `RecoverySession` now serializes the ENTIRE
  generation CAS and publication attempt (`_begin_write` claims the
  in-flight slot BEFORE the CAS read or any pointer-temp touch; a
  competing same-handle publication is refused the closed
  `write_in_flight`; a closed session refuses `session_closed`
  before any IO); ordinary filesystem read faults (raw `os.read` /
  post-open `os.fstat` errors) are contained at the store boundary as
  the closed `io_failure` on every read path (the publication
  read-back fence, the load fence, the pre-publication pointer CAS
  read, the generation probe and the committed-size probe) with the
  descriptor cleaned up; a genuinely torn short read stays the
  `checkpoint_torn` outcome.
- `src/slaif_local_coding/constitution/bundles/recovery_resume.py`:
  the synchronous `checkpoint_current` and `admit_with_fence`
  entry points join the registry through `recovery_op_begin` (the
  exact live-owner claim) and release it through `recovery_op_end`
  on every outcome; a claim refusal is the established typed result
  (`WRITER_CONFLICT` for the checkpoint; `FENCE_REFUSED` with the
  `WRITER_CONFLICT` fence for the fenced admit) — no cold
  reservation, no publication; the composed async teardown drain
  loop now also drains the claimed synchronous operation before the
  RAM ownership is fenced / released and the writer session closed.
- `src/slaif_local_coding/constitution/bundles/ram_state.py`:
  the new `_recovery_op_owner` claim term (ONE registry-held owner
  reference, identity-joined and identity-released; admitted only
  while the caller holds the ONE process owned store IO slot, so at
  most ONE operation is ever claimed), `recovery_op_begin` (the
  entry check and the live-owner claim in ONE critical section:
  absent / epoch-fenced / replaced owner refuses; an ALREADY-SET
  work-teardown fence refuses the claim — the established 020-a
  same-lock drain refusal applies to a fenced claim unchanged and a
  fenced claim can never publish), `recovery_op_end` (identity
  release, no double release), `recovery_op_live` and
  `recovery_io_live` (transient OR claimed can still publish), and
  the synchronous store teardown fence widened to
  `recovery_io_live`.
- `src/slaif_local_coding/constitution/bundles/ram_work.py`: the
  composed work teardown's direct store-release fence widened to
  `recovery_io_live` (from EITHER branch: the fenced-claim case and
  the post-drain release).
- `tests/test_bundle_recovery_store.py`: NEW
  `test_held_write_serializes_same_handle_cas_and_publication`
  (deterministic held-fsync barrier; the competing same-handle
  writer is refused `write_in_flight` with the actual generation
  carried and the pointer untouched; after the held write commits,
  the stale expected generation is refused `generation_mismatch`
  with the ACTUAL committed generation; the on-disk record is the
  held write's).
- `tests/test_bundle_recovery_resume.py`: NEW
  `test_resume_epoch_binding_readback_io_fault_releases_owner_and_writer`
  (real committed checkpoint generation 1; an injected `os.read`
  fault armed at the epoch-binding post-rename directory fsync and
  targeted at the committed generation-2 checkpoint read-back; the
  failure is the typed `io_failure` with generation 2 carried —
  never a raw escape past owner teardown / session close; the
  partially prepared owner is removed, the rebound reservation and
  the writer released, no claimed operation survives; the committed
  generation 2 record is intact; a fresh same-registry resume
  succeeds at generation 3 with a distinct epoch strictly above the
  bound prior) and NEW
  `test_preemption_gap_teardown_wins_claim_refuses_retired_owner`
  (deterministic barrier ON the documented entry gap: the
  synchronous operation is held at its `recovery_op_begin` with the
  slot held and the claim unrun; the 019 work teardown wins the
  race and retires the owner; the released claim targets the RETIRED
  owner and refuses `WRITER_CONFLICT` with the actual generation
  carried, no cold reservation, no publication, the process total
  exactly unchanged; the committed generation stays 2).
- Docs: `docs/CACHE-RECOVERY-CONTRACT.md` (the typed `io_failure`
  read-fault law, the single-writer CAS/publication serialization,
  the claimed-owner fence closing the former residual preemption
  micro-window, the preserved same-lock drain refusal),
  `docs/CACHE-RAM-STATE-CONTRACT.md` (section 9: the claimed-owner
  claim law and the widened fence), `docs/CACHE-RAM-WORK-CONTRACT.md`
  (section 10: the widened work-teardown fence),
  `ARCHITECTURE-for-agents.md` + `oap/strategic-instructions/`
  mirror + the S mirror (THREE compact mirrors byte-identical at
  sha256 6345d4e7b4eda031609b48eab84379be3cec7fea6b0a45d68ceb7c0cc2728847; S mirror preserved in place at
  inode 10638621/UID 1001/0600), `docs/CACHE-REWORK-LEDGER.md`
  (current M03/M04 + 020 rows only).
B changes only `packaging/dev_provenance_manifest.json`.

## Acceptance evidence
### Requirement 1 (single writer-owned session: whole CAS + publication serialized)
- PASSED at inert scope: `test_held_write_serializes_same_handle_cas_and_publication`
  (2 admission/endpoint instances) — a held first publication
  (real fsync barrier) refuses the competing same-handle
  publication `write_in_flight` BEFORE a second CAS or pointer
  mutation (actual observed generation 1 carried, pointer
  untouched); the held write commits to generation 2; the stale
  expected generation is refused `generation_mismatch` with
  actual_generation 2; the ACTUAL on-disk record is the held
  write's (generation 2, record B). Same-descriptor flock,
  close/drain, fixed private outcomes and observed-generation
  semantics unchanged (the full store battery re-passed in the
  294-case rerun).
### Requirement 2 (read-back I/O fault: typed failure, best actual generation, owner/release)
- PASSED at inert scope: `test_resume_epoch_binding_readback_io_fault_releases_owner_and_writer`
  (4 admission/endpoint instances) — with a REAL committed
  checkpoint (generation 1) and the fault armed at the
  epoch-binding post-rename directory fsync targeting the
  generation-2 checkpoint read-back, the resume fails STORE_REFUSED
  with the typed `io_failure` and generation 2 (the committed
  binding pointer — best actual observed, never the assumed prior,
  never None); the partially prepared owner is removed, the rebound
  reservation and the writer are released and no claimed operation
  survives; the committed generation 2 and its record are intact
  after rename; a fresh same-registry resume succeeds (generation 3,
  distinct epoch strictly above the bound prior). Genuinely torn
  bytes keep `checkpoint_torn` and pre-publication failures keep
  their prior outcomes (unchanged 020-a cases re-passed in the
  294-case rerun, including the corrupt/torn/foreign/oversized
  negatives and the actual SIGKILL-during-publication case).
### Requirement 3 (preemption gap closed: entry check and live-owner claim atomic)
- PASSED at inert scope: `test_preemption_gap_teardown_wins_claim_refuses_retired_owner`
  (4 admission/endpoint instances) — the deterministic barrier on
  the documented entry gap holds the synchronous operation at its
  `recovery_op_begin` (slot held, claim unrun, NO live recovery IO
  at teardown entry); the 019 work teardown wins and retires the
  owner; the claim then targets the RETIRED owner and refuses
  cleanly `WRITER_CONFLICT` with the actual generation carried — no
  cold reservation, no publication, process total exactly
  unchanged; the committed generation stays 2. The reverse order
  (the existing
  `test_work_teardown_fence_refuses_new_recovery_reservation_reverse_order`,
  4 instances) re-passed: an ALREADY-SET work-teardown fence makes
  the claim refuse with the established `FENCE_REFUSED` /
  `WRITER_CONFLICT` same-lock drain refusal preserved (this is the
  case whose expectation had regressed pre-fix and whose broad
  suite hang is closed).
- The write-wins side is closed by construction and covered: a
  claimed operation keeps `recovery_io_live` true, so BOTH direct
  teardown paths (the synchronous store teardown and the composed
  work teardown, from either release branch) refuse
  `recovery_in_flight` at entry, and the composed async recovery
  teardown drains the claim (with the store in-flight count) before
  fencing / releasing / closing (the existing entry-fence and
  held-IO drain tests re-passed in the 294-case rerun).

## Verification
- 15-command gate at exact B (`gate-driver-020b.sh`, 0700, sha256
  c2f284065a9974f9cb77c32ab7a5c38fd9acc04aebea3479714714bf36212f45;
  private capture parent umask 077, actual nonroot full-pytest child
  umask 022): ALL 15 commands rc=0 with decimal capture IDs (all 15
  captures distinct). Driver startup receipt: pid 969218, birth
  366255427, ppid 969217, uid 1001, umask 0077, driver source sha256
  c2f284065a9974f9cb77c32ab7a5c38fd9acc04aebea3479714714bf36212f45,
  started 2026-11-19T00:52:16.266083+00:00, head
  4e4725d6044d46c78aed67421c1a21e93ce7537b.
  - cmd01 `uv lock --check` rc0; cmd02 `uv sync --frozen --extra
    dev` rc0; cmd03 `uv run --frozen ruff check .` rc0; cmd04
    `ruff format --check .` rc0; cmd05 `mypy src tests` rc0; cmd06
    `docs_consistency_check.py` rc0 (19 claim docs checked); cmd07
    `umask 022; uv run --frozen pytest -q` rc0 — 6802 passed, 28
    skipped, 16 warnings in 1325.84 s (020-a 6792 + the 10 new 020-b
    cases); cmd08 `uv build` rc0 (fresh dist: wheel
    slaif_local_coding-0.1.0-py3-none-any.whl 717320 B sha256
    920066831c08bc893da97da3880e0a6cff7fd605fa64a533a5d46854af1db0ab;
    sdist slaif_local_coding-0.1.0.tar.gz 2408824 B sha256
    7bd422bbbb3c14d546292482b36aac1005183748faf4478b021caa48141ba09c
    — byte-identical to the manifest record); cmd09
    `artifact_policy_check --inspect` rc0 (no violations); cmd10
    `--install-smoke` rc0 (fresh noneditable smoke, 0.1.0); cmd11
    `python --version` 3.12.15 rc0; cmd12 `compileall` rc0; cmd13
    `dev_provenance_manifest.py --verify --dist dist` rc0
    (state=development head=4e4725d6044d); cmd14 `bash -n` all
    oap/bin/*.sh + packaging/*.sh rc0; cmd15 `git diff --check
    61b946911fea38d3ad32050228d576b51db17738 HEAD` rc0.
- One clean Git-B archive build (`build-020b.sh`, 0700, sha256
  e2122562ccf8caf025849f41d2dffbbff0f848f3fc76b62886077443e0996ba5;
  driver pid 1015432, birth 366391353, ppid 1015413, uid 1001, umask
  0077): git archive 24729600 B, 923 files extracted, `uv build`
  rc0; wheel/sdist byte-identical to the gate dist and the manifest.
  The build run directory was created BEFORE its startup metadata was
  recorded (the 020-a startup-miss qualification does not recur):
  startup.json complete (started 2026-11-19T01:14:55.505931Z,
  literal exact-B/A guards 4e4725d/9540a02, per-step exits
  archive/extract/build all 0).
- Full strict artifact proof (`artifact-proof-020b.py`, 0700, sha256
  79eae2d36f45789f9fccb90e01d0cb6dc08066a6193dfe0e5abe3f69773051b4;
  helper pid 1015682, birth 366393793, ppid 1015681, uid 1001, umask
  0077, started 2026-11-19T01:15:19.942644Z): PASSED exit 0 — 923
  clean-archive files byte-identical to Git B; 294 manifest source
  inputs verified against Git A, Git B and the clean extracted tree;
  B verified manifest-only over A (sole parent); sdist 292 entries
  (291 source + 1 generated PKG-INFO); wheel 75 entries (69 runtime
  + 6 dist-info); RECORD full entry set with 74 nonself
  digest/size rows verified (75 total RECORD rows including the self
  row with empty digest AND empty size); PKG-INFO == METADATA bytes;
  entry points exact; LICENSE/NOTICE byte-identical; repo gate dist/
  byte-identical to the clean artifacts.
- Focused captures (pre-commit development runs;
  `dev-captures-020b.md`, 0600): c01 focused reverse-teardown
  (bounded 240 s, the hang regression target) 4 passed / 16.40 s;
  c02 the ten new 020-b cases 10 passed / 46.65 s; c03 mypy
  189 files clean after the `loaded.record` narrowing fix (before:
  1 union-attr error at
  tests/test_bundle_recovery_resume.py:2093); c04 six-file battery
  294 passed / 496.08 s (`battery-294.out`, 0600 — recorded
  qualification: that file's BATTERY_EXIT line is the TAIL stage exit
  of a no-pipefail pipeline, not the pytest rc; the pass line is the
  recorded result and the authoritative full-suite rc is the gate
  cmd07 direct capture); c05 pre-commit statics (ruff check / ruff
  format --check / docs consistency) all green.

## Live model/service evidence
- NOT RUN — component scope only; no protected fixture touched;
  the suite's 28 skips are the honest live-credential / UID-0 /
  gateway-dependent tests.

## GitHub CI / required checks
- At implementation head B (4e4725d6044d46c78aed67421c1a21e93ce7537b),
  all TEN required checks exist and are completed/success: test,
  Analyze (actions), Analyze (python), CodeQL, gateway-contract,
  docker, docker-published, operator-session,
  cache-native-containment, cache-native-fixture.
- All required green at drafting: yes.
- Independently re-verified by the supervising party before this
  report draft (stated as reported; the check names / statuses above
  are the exact-B observation).

## Local setup/dependencies
- Python 3.12.15 via repo venv, `uv` lock/sync frozen; no new
  dependencies, services or configuration keys. Subprocess test
  children are plain repo-interpreter Python only; NO new
  Codex/client processes.

## Documentation
- Updated in-round as listed under Changes and files: the ONE
  owning recovery contract plus the affected current ledger /
  architecture passages, per the order; no new planning/design/
  audit document.

## Safety/scope confirmations
- Unrelated files: none touched; pre-existing work preserved.
- Secrets/raw content: none in report/PR/log; evidence uses hashes,
  counts and sanitized fixtures only.
- Protected 18020/Qwen/Codex fixture changed: NO.
- Three compact mirrors byte-identical (sha256
  6345d4e7b4eda031609b48eab84379be3cec7fea6b0a45d68ceb7c0cc2728847);
  S mirror preserved in place at inode 10638621/UID 1001/0600.
- Required tests skipped/not run: 28 honest skips in the full suite
  (live-credential/UID-0/gateway-dependent); all v1 runtime and
  real-client halves NOT RUN (planned for 021-024).
- Scope deviations (preserved truthfully):
  - one pre-commit mypy `union-attr` error in the NEW readback test
    (tests/test_bundle_recovery_resume.py:2093, `loaded.record`
    not narrowed) was fixed in the working tree before commit A —
    recorded in the c03 development capture;
  - the pre-commit battery capture (`battery-294.out`) records the
    pipeline TAIL stage exit (no pipefail) rather than the pytest rc
    — recorded above; the gate cmd07 direct capture is the
    authoritative full-suite rc;
  - the pre-commit focused runs (c01/c02/c05) are development
    captures of observed terminal output (not sealed with startup
    receipts); the authoritative statuses are the gate and the
    clean build / proof captures;
  - two manual summary files (`gate-driver-020b.out`,
    `clean-build-020b.out`) were initially created 0664 inside the
    protected 0700 run directory and were normalized to 0600 after
    the fact (no verification rerun);
  - the 020-b control OK was consumed by the existing 020-a-era
    reader (PID 3843198, birth 345679657, original control FIFO
    inode 10648021; exact receipt
    `next-control-wait-020a-receipt-v1.json`) and collected exactly
    once this round — no FIFO replay, no additional reader, no other
    Codex/client startup;
  - no clean-host or no-deviation claim is made.
- Extra objective PR: NO; coding merge: NO; active/order edited:
  NO (order bytes committed unchanged, verified sha256
  ebbd1201768a078ed0e5ee8713f51e07a508ea49e90b47838ae9f7ebbf944256;
  `oap/active` carries only the 020-a -> 020-b activation
  transcript, sha256
  df2312ecfc441fdc47fb04900e92dffc1b0e1757a2d453f9f7d01d15c6cf1bd3);
  report commit report-only: yes (verified at publication).

## Known limitations/blockers
- Inert recovery-component layer only: no wire/HTTP (022), no
  compiler/tokenizer semantics (021), no full-stack (023), no
  actual-model/genuine-Codex (024). Owned store IO is a single-
  slot bounded model; synchronous primitives run off-loop per the
  documented integration contract. Occupancy is a
  committed-occupancy measure, not a total-RSS promise.

## Recommended strategic follow-up
- Strategic decision on 020-b at the same bounded inert
  recovery-component scope (020-a component + the 020-b ownership /
  fault corrections). Next mandatory stages per the ledger: 021
  compiler/tokenizer, 022 wire/transactional runtime, 023
  full-stack, 024 actual-model/genuine-Codex.

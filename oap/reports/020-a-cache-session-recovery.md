# OAP Coding-Agent Report — 020-a

## Work order
- Identifier: 020-a; order path `oap/orders/020-a-cache-session-recovery.md`; numeric objective 020
- PR mode: CREATE_NEW_PR (PR 28)

## Status
COMPLETE

## Executive summary
Actual result: the WHOLE 020 protected session recovery component is
implemented at the INERT recovery-component layer over the ACTUAL
accepted 018-p/018-t records and the accepted 019 RAM owner/work
plane: the versioned closed recovery record/codec (exact extracted
originals, credential refusal, complete P/D/namespace validation +
ACTUAL T derivation before restorable), the trusted address-only
resume (exactly ONE record from its stable address alone, no
source/root/reference, no scan), the protected per-session store
(atomic generation publication with the ACTUAL committed-outcome
fault law, including an actual process crash during publication),
the bounded shared-RAM recovery reservations against the SAME 019
ceilings, the durable epoch binding republished on every resume, the
durable fail-closed adverse-quarantine fence, the owned bounded
async store IO with drain-before-release cancellation/timeout/
teardown, and the lazy once-per-epoch rebuild through the actual 019
work plane with mechanically denied recovery-content reads. The
final 15-command gate at clean manifest B passed 15/15 (full pytest
6792 passed / 28 skipped / 16 warnings / 1243.98 s), one clean
Git-B archive build produced BOTH artifacts and the full strict
artifact proof passed (exit 0), and all TEN required GitHub checks
are SUCCESS at exact B. No v1 runtime, real-client or model
criterion is qualified; 021-024 remain mandatory. This is a claim
until strategic review; no acceptance or merge is claimed.

## Authoritative GitHub state
- Repository: ulfe-lmi/slaif-local-coding; PR 28
  https://github.com/ulfe-lmi/slaif-local-coding/pull/28 (state open)
- Base: main a62b87ddb9fe96a741aa4ce8932ca40adf6dc0eb (whole 019
  accepted/merged)
- Head: oap/020-cache-session-recovery 0aa6634e3b4afc606090e445a5158ea12123fda8
- Starting remote head at branch creation: a62b87d (main; no prior
  020 commits)
- Implementation head SHA: 0aa6634e3b4afc606090e445a5158ea12123fda8
- Report publication commit: SELF
- Implementation commits pushed before report:
  A f22462a26c2b0ce393fffba0c5e620c22562cec1 (clean source, 24
  files) and B 0aa6634e3b4afc606090e445a5158ea12123fda8
  (manifest-only child, sole parent A, 294 manifest inputs)
- New PR this round: yes (PR 28); merge performed: NO

## Changes and files
A (vs starting head a62b87d), 24 files:
- `src/slaif_local_coding/constitution/bundles/recovery_models.py`,
  `recovery_codec.py` (NEW: versioned closed recovery record and
  codec), `recovery_store.py` (NEW: protected per-session store),
  `recovery_resume.py` (NEW: address-only resume coordinator,
  bounded reservations, epoch binding, fence durability, owned
  bounded async IO);
- `ram_state.py`, `ram_state_models.py`, `ram_work.py`,
  `ram_work_models.py` (additive 020 seam: recovery transient
  reservations in the SAME atomic sums, ONE process-wide owned
  store IO slot, identity-join-first then same-lock work-teardown
  fence ordering, `recovery_in_flight` entry fences on both
  teardown paths; accepted 019 laws unchanged);
- `tests/test_bundle_recovery_codec.py`,
  `tests/test_bundle_recovery_store.py`,
  `tests/test_bundle_recovery_resume.py` (NEW);
- docs: NEW `docs/CACHE-RECOVERY-CONTRACT.md`;
  `docs/CACHE-RAM-STATE-CONTRACT.md` (section 9),
  `docs/CACHE-RAM-WORK-CONTRACT.md` (section 10),
  `ARCHITECTURE-for-agents.md`,
  `oap/strategic-instructions/ARCHITECTURE-for-agents.md` and the S
  mirror (THREE mirrors byte-identical at sha256
  01f8d29983af41ba6f251c1ce8bf38a1fe2a24f554ed3355d8a1fd8dc481df35;
  S mirror preserved in place at inode 10638621/UID 1001/0600),
  `ARCHITECTURE.md`, `SECURITY.md`, `TESTING.md`,
  `docs/CACHE-IMPLEMENTATION-PLAN.md`,
  `docs/ADAPTER-CONFIGURATION.md`, `docs/CACHE-REWORK-LEDGER.md`
  (current M01-M05 + 020 rows only; no closed-018 history
  re-audit);
- transcript: `oap/orders/020-a-cache-session-recovery.md` (added,
  unchanged bytes; sha256
  face28ee9368c4f9f043885247986a7e5a657e4be485dd9fcea05c5d8a7aba47),
  `oap/active` (019-c -> 020-a activated transcript).
B changes only `packaging/dev_provenance_manifest.json`.

## Acceptance evidence
### Requirement 1 (versioned closed recovery record, codec, integrity)
- PASSED at inert scope (`tests/test_bundle_recovery_codec.py`):
  exact original-byte round trips (Unicode/CRLF/empty, ordered
  multi-file, unknown hashes retained), retained graph / causal /
  currentness / replay / revert / conflict law; detectable-credential
  refusal BEFORE encode/store and on DECODED values (JSON-escape
  resistant; fixed private errors; no complete-secret claim); no
  executable/pickle deserialization (closed JSON); pre-allocation
  byte bounds (64MiB initial / 256MiB hard; memoryview nbytes
  gated); complete P/D/namespace validation + ACTUAL T derivation
  before a record is restorable, with legitimate non-READY/conflict
  histories restorable as unusable evidence; digest rebind and
  malformed-negative tests reach their intended joins.
### Requirement 2 (trusted address-only resume)
- PASSED at inert scope: the six-field trusted address
  (`recovery_address_key`) locates exactly ONE record even with NO
  root/source/reference in the resumed request context; the
  disappeared workspace/root is not a lookup prerequisite; NO scan
  (universal `listdir`/`scandir` denial during resume, including fd
  arguments, plus refusal of the known forbidden-B directory
  basename in its ACTUAL descriptor-relative open form — proven by
  the trap self-test); full loaded namespace/configuration and
  source/proof consistency validated before any RAM publication;
  a value-equal foreign namespace copy is the fixed
  `RamStateInputError` (019 identity law unchanged).
### Requirement 3 (protected store, atomic publication, fault law)
- PASSED at inert scope (`tests/test_bundle_recovery_store.py`):
  operator-prepared existing 0700 current-owner root (refused if
  missing), descriptor-relative same-descriptor validation
  (regular-file/mode/owner on the opened descriptor, nonblocking
  safe open against FIFO), no symlink/path escape (root symlink and
  symlinked-ancestor `PATH_ESCAPE` refusals), OS-held exclusive
  writer lock (`flock`, no live/stale PID guessing; cross-process
  kernel release proven), expected-generation CAS (stale/competing
  writers refused), atomic publication (checkpoint 0600 + fsync,
  pointer temp + fsync + rename + directory fsync, readback fence,
  pre-write canonical byte-identity re-proof), the ACTUAL
  committed-outcome law: torn/missing/corrupt/foreign/oversized/
  digest/schema/configuration mismatches are typed refusals with no
  partially published RAM state, `current_generation()` distinguishes
  MISSING (0) from corrupt (refusal), orphan same-generation exact
  reuse only after fsync, and an ACTUAL process crash (SIGKILL at
  the post-rename directory-fsync boundary) preserves the committed
  generation with the store fully usable — the actual outcome,
  never a manufactured rollback.
### Requirement 4 (bounded shared-RAM reservations, owned bounded IO)
- PASSED at inert scope: record-byte bounds BEFORE allocation; the
  COLD initial-load reservation (`max(4 x committed, 16384)`) held
  before `session.load` and released exactly once on every outcome;
  the LIVE publication reservation (`max(24 x (owned + 16384),
  16384)`) reserved on the loop BEFORE thread dispatch; the
  session-reservation term is in the SAME atomic 019 process/session
  sums (identity join FIRST, then the same-lock work-teardown fence,
  then capacity — so simultaneous store/work allocations observe it);
  a genuine legal capacity crossing (finite process ceiling,
  measured actual restored baseline, deterministic competing owned
  reservation before real admit) yields the typed 503 with old
  state preserved in bytes/counters; ONE process-wide owned store
  IO slot with typed busy refusal; caller cancellation (repeated,
  held at a controlled barrier) and timeout drain the owned write to
  its ACTUAL outcome before the slot/reservation release and the
  CancelledError/TimeoutError propagate; teardown cannot release or
  propagate while its owned task is live (repeated cancellation of
  the teardown task held; no task/charge leak; unrelated owner
  intact); the work-teardown reverse race is closed under the same
  lock; `recovery_in_flight` entry fences on both direct teardown
  paths.
### Requirement 5 (resume validation, distinct epoch, quarantine durability)
- PASSED at inert scope: schema/integrity/namespace/configuration
  and originals validated first, ACTUAL T derived, registered owner
  reconstructed in a DISTINCT live epoch (`acquire_new_with_epoch_floor`
  once under the registry lock; duplicate live owner rejected); the
  durable epoch binding is republished on EVERY resume (generation
  + 1, prior epoch durably advanced, no usage rewrite within an
  epoch) — proven across FRESH plain-Python processes with fresh
  registries (v1 gen 2 / v2 gen 3, `committed_after` verified);
  a capacity-quarantined owner NEVER resumes old usable governance:
  the durable fail-closed fence precedes the adverse transition,
  the old root lookup/resolve (including replay and source-absent
  requests) stays unusable, and an explicit restart/resume from the
  unchanged older checkpoint is blocked (no automatic
  unquarantine/retry/epoch reset); a failed fence publication blocks
  that transition (pure pre-transition failure keeps the prior
  committed generation valid — stated in the contract); failed
  epoch-binding encode/publish releases the transient BEFORE
  teardown with the actual committed generation reported, no live
  owner/reservation/writer residue (registry absence asserted).
### Requirement 6 (lazy rebuild, no hot reads, retention)
- PASSED at inert scope: the needed current key is prepared exactly
  ONCE per key/epoch through the ACTUAL 019 work plane
  (COMPLETED/1 then HIT/0 — honest first-rebuild vs RAM-hit counts);
  repeated RAM hits perform ZERO recovery-content reads and ZERO new
  seam invocations; no eager dormant-session scan (multiple dormant
  persisted sessions coexist; only the addressed one is read/
  rebuilt); no source originals sent as fallback; checkpoints are
  not rewritten for usage timestamps (generation stable across hits
  within an epoch); operator-owned retention/deletion and deployment
  encryption prerequisites are stated in the contract (no
  automatic timed deletion or silent capacity cleanup); no new
  protected-host configuration.
### M02-M04 at the component/injected-work scope
- M02 (multi-dormant, address-only one-session resume, fresh
  processes, distinct epoch): EARNED at the inert scope — actual
  subprocess restart, 4 passed / 34.27 s / rc 0.
- M03 (fault/crash matrix): EARNED at the inert scope — injected
  fault points, stale/competing writers, orphan reuse, and the
  actual SIGKILL-during-publication case, 2 passed / 9.48 s / rc 0
  plus the store negatives.
- M04 (ownership/races): EARNED at the inert scope — OS-held writer
  ownership, held-IO caller cancellation/deadline/teardown
  drain-before-release races and the work-teardown reverse race,
  8 passed / 44.90 s / rc 0 plus the lock/ownership negatives.
- Final scoped six-file battery (resume + ram_state + codec +
  store + ram_work + ram_lifecycle): 284 passed / 455.86 s / native
  rc 0, with focused Ruff/format/mypy green. Both admission modes
  and both endpoints; actual measured sizes recorded (restored
  baseline differs from the direct owner charge — measured, not
  assumed); no infinite-session claim.

## Verification
- 15-command gate at exact B (`gate-driver.sh`, 0700, sha256
  a402728fe822f33a5afe56866064423d1d8de9e098d147cd1bcbbc009ec32f94;
  private capture parent umask 077, actual nonroot full-pytest
  child umask 022): ALL 15 commands rc=0 with decimal capture IDs
  (the 019-c gate6 octal-label incident is fixed; all 15 captures
  distinct). Driver startup receipt: pid 3790796, birth 345508659,
  ppid 3790779, uid 1001, umask 0077, driver source sha256
  a402728fe822f33a5afe56866064423d1d8de9e098d147cd1bcbbc009ec32f94,
  started 2026-11-16T15:14:28.583017+00:00, head
  0aa6634e3b4afc606090e445a5158ea12123fda8.
  - cmd01 `uv lock --check` rc0; cmd02 `uv sync --frozen --extra
    dev` rc0; cmd03 `uv run --frozen ruff check .` rc0; cmd04
    `ruff format --check .` rc0; cmd05 `mypy src tests` rc0;
    cmd06 `docs_consistency_check.py` rc0 (19 claim docs checked);
    cmd07 `umask 022; uv run --frozen pytest -q` rc0 — 6792
    passed, 28 skipped, 16 warnings in 1243.98 s; cmd08 `uv build`
    rc0 (fresh dist: wheel slaif_local_coding-0.1.0-py3-none-any.whl
    714442 B sha256
    1bf9f6290c1c938da98e6af2d909c14463170592b8bdc971757a6a8f3df69f13;
    sdist slaif_local_coding-0.1.0.tar.gz 2401423 B sha256
    e2faf09bfa8a55591497d738c5046fcd0a322a9a375d0704d54bc8be037b9950
    — byte-identical to the manifest record); cmd09
    `artifact_policy_check --inspect` rc0 (no violations); cmd10
    `--install-smoke` rc0 (fresh noneditable smoke, 0.1.0);
    cmd11 `python --version` 3.12.15 rc0; cmd12 `compileall` rc0;
    cmd13 `dev_provenance_manifest.py --verify --dist dist` rc0
    (state=development head=0aa6634e3b4a); cmd14 `bash -n` all
    oap/bin/*.sh + packaging/*.sh rc0; cmd15 `git diff --check
    a62b87ddb9fe96a741aa4ce8932ca40adf6dc0eb HEAD` rc0.
- One clean Git-B archive build (`build-020a.sh`, 0700, sha256
  2c017caf7f34062e33a23dc4eedea38dc586a8f9a14c349a295b3951e881363c;
  driver pid 3838191, umask 0077): git archive 24668160 B, 921
  files extracted, `uv build` rc0; wheel/sdist byte-identical to
  the gate dist and the manifest. Qualification (preserved
  truthfully): the driver's startup.json write targeted the run
  directory before its `mkdir`, so the JSON startup receipt is
  missing (the redirect error is preserved as the first line of
  the build log); the partial startup receipt (pid 3838191, umask
  0077, head/parent/clean guards) is preserved on the first log
  line; all per-step exits and artifacts are preserved; the build
  was NOT repeated for the receipt.
- Full strict artifact proof (`artifact-proof-020a.py`, 0700,
  sha256 4e28186f00b24dea5fe0cc341856b23d1ece187b033c4f511f59c52e394f2f57;
  helper pid 3838319, birth 345644177, ppid 3838309, uid 1001,
  umask 0077, started 2026-11-16T15:37:03.789175Z): PASSED exit 0
  — 921 clean-archive files byte-identical to Git B; 294 manifest
  source inputs verified against Git A, Git B and the clean
  extracted tree; B verified manifest-only over A (sole parent);
  sdist 292 entries (291 source + 1 generated PKG-INFO); wheel 75
  entries (69 runtime + 6 dist-info); RECORD full entry set with 74
  nonself digest/size rows verified (75 total RECORD rows including
  the self row with empty digest AND empty size); PKG-INFO ==
  METADATA bytes; entry points exact; LICENSE/NOTICE
  byte-identical; repo gate dist/ byte-identical to the clean
  artifacts.
- Focused captures (W20a, 0600): c46 six-file battery 284 passed /
  455.86 s / rc 0; c43 subprocess restart 4 passed / 34.27 s / rc
  0; c45 caller cancel/deadline held-IO 8 passed / 44.90 s / rc 0;
  c45b actual crash during publication 2 passed / 9.48 s / rc 0.

## Live model/service evidence
- NOT RUN — component scope only; no protected fixture touched;
  the suite's 28 skips are the honest live-credential / UID-0 /
  gateway-dependent tests.

## GitHub CI / required checks
- At implementation head B (0aa6634e3b4afc606090e445a5158ea12123fda8),
  all TEN required checks exist and are SUCCESS: test (14m23s),
  Analyze (actions), Analyze (python), CodeQL, gateway-contract,
  docker, docker-published, operator-session,
  cache-native-containment, cache-native-fixture (runs
  43894371356 + 43894184245, both completed success at the exact B
  head).
- All required green at drafting: yes.

## Local setup/dependencies
- Python 3.12.15 via repo venv, `uv` lock/sync frozen; no new
  dependencies, services or configuration keys. Subprocess test
  children are plain repo-interpreter Python only; NO new
  Codex/client processes.

## Documentation
- Updated in-round as listed under Changes and files; the ONE
  owning recovery contract permitted by the order
  (`docs/CACHE-RECOVERY-CONTRACT.md`) is new; no other
  planning/design/audit document.

## Safety/scope confirmations
- Unrelated files: none touched; pre-existing work preserved.
- Secrets/raw content: none in report/PR/log; evidence uses hashes,
  counts and sanitized fixtures only.
- Protected 18020/Qwen/Codex fixture changed: NO.
- Three compact mirrors byte-identical (sha256
  01f8d29983af41ba6f251c1ce8bf38a1fe2a24f554ed3355d8a1fd8dc481df35);
  S mirror inode 10638621/UID 1001/0600 preserved in place.
- Required tests skipped/not run: 28 honest skips in the full
  suite (live-credential/UID-0/gateway-dependent); all v1 runtime
  and real-client halves NOT RUN (planned for 021-024).
- Scope deviations (preserved truthfully):
  - the clean-build driver startup.json miss above (build not
    repeated; partial receipt + all per-step exits preserved);
  - c39 selector incident (zero-select rc5, selector did not match
    saved test names) and the c41 first-run 8 failures (generation
    read after close; high-water fixture assumption 7020 vs 6900 —
    repaired with actual accounting, no ceiling change) are
    preserved in the development captures;
  - c42 is a STALE pre-correction run (v2 generation assertion)
    collected and preserved, not qualification evidence;
  - the c45 invocation passed two `-k` flags; pytest honored the
    last, so only the cancel/deadline cases ran there (crash cases
    ran separately in c45b);
  - a scratch repeated-cancellation experiment (native exit 143,
    owned shell ended) has UNKNOWN descendant cleanup and was
    replaced by the bounded in-product barrier fixture; no
    descendant-cleanup guarantee is claimed;
  - a brief broad /proc scan at ~06:05 UTC exceeded the
    owned-lifetime boundary (no unowned process was killed; the
    printed "UID=3506106" was actually the stat PID field);
  - the charge-stability probe (174670 B direct vs 181132 B
    restored) is an unsealed development diagnostic (no startup /
    umask / hash provenance) used only to estimate the capacity
    fixture ceiling;
  - the capacity fixture uses the disclosed legal non-default
    `L1_LEGAL_STAGE` GraphBounds shape;
  - one residual preemption micro-window in the owned-IO admission
    ordering is documented in the recovery contract (not tested);
  - the synchronous store primitives are covered by the documented
    off-loop integration contract (actual ASGI wiring is 022).
  - No clean-host or no-deviation claim is made.
- Extra objective PR: NO; coding merge: NO; active/order edited:
  NO (order bytes committed unchanged, verified sha256
  face28ee9368c4f9f043885247986a7e5a657e4be485dd9fcea05c5d8a7aba47;
  `oap/active` carries only the 019-c -> 020-a activation
  transcript); report commit report-only: yes (verified at
  publication).

## Known limitations/blockers
- Inert recovery-component layer only: no wire/HTTP (022), no
  compiler/tokenizer semantics (021), no full-stack (023), no
  actual-model/genuine-Codex (024). Owned store IO is a single-
  slot bounded model; synchronous primitives run off-loop per the
  documented integration contract. Occupancy is a
  committed-occupancy measure, not a total-RSS promise. Actual IO
  latency limitations are documented without promising bounded
  kernel fsync latency.

## Recommended strategic review
- Strategic decision on 020-a at its bounded inert
  recovery-component scope (whole 020 component stage; M02-M04 at
  the component scope EARNED; runtime/real-client halves NOT RUN).
  Next mandatory stages per the ledger: 021 compiler/tokenizer,
  022 wire/transactional runtime, 023 full-stack, 024
  actual-model/genuine-Codex.

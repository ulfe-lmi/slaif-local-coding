# OAP Coding-Agent Report — 017-m

## Work order
- Identifier: 017-m; order path: `oap/orders/017-m-observer-pairing-and-causality.md`; numeric objective 017
- PR mode: AMENDED_EXISTING_PR (PR #25, branch `oap/017-cache-read-observation`)

## Status
COMPLETE

## Executive summary
Repaired the per-request pure read-observation identity and causal
pairing in the inert bundle-observation package, and completed the
public D10 adversarial composition matrix plus the pure D09
unsupported/partial negative matrix. Two bounded defects found by
independent review at the 017-l implementation head are fixed:
(a) an unsupported/ineligible call with a colliding ID was removed
before duplicate-ID inventory, hiding a collision with an eligible
call; (b) a result structurally BEFORE its matching future call was
still acquired. Identity conflicts are now inventoried before read
eligibility (an unknown call never acquires, but its ID collision
with an eligible call is a typed `DUPLICATE_CALL_ID` conflict;
missing/empty/non-string IDs are typed observable and never invent
an ID), and results attach to their matching call only when their
exact numeric structural position follows the call's (never lexical
call IDs or JSONPath string sorting); a pre-call result keeps its
chain typed `PRE_CALL_RESULT`, non-removable, with no bundle/member
digest, no source span and no proven-executed claim. The new public
suite `tests/test_bundle_d10_matrix.py` (40 tests) plus the new
frozen probe (8/8 at the final head, 4/8 at the 017-l head) prove
the repaired behavior on Responses and Chat; all 16 frozen probes,
the full local gate (2273 passed / 28 standing skips / 0 failed),
the clean source-A archive reproduction, and the fresh installed-wheel
functional controls (21/21) pass. This is a bounded advancement of
the required observation work: D09 multi-chunk/process association
remains deferred (`NOT RUN` — the D09 partial negatives are not
multi-chunk evidence), and the D10 delivery claim requires
independent strategic acceptance. No capture utility/child
modification, no actual capture, no process collector, no
graph/RAM/recovery/tokenizer/compiler/image/pipeline/Gateway/legacy
change; the observer stays inert; no v1 runtime mechanism is active
or qualified.

## Authoritative GitHub state
- Repository: `ulfe-lmi/slaif-local-coding`; PR #25
  https://github.com/ulfe-lmi/slaif-local-coding/pull/25 — OPEN,
  non-draft, no auto-merge
- Base: `main` @ `96c790423f6f0097a56a0b12bacda8a9b6da6aba`
  (unchanged); head branch `oap/017-cache-read-observation`
- Starting remote SHA: `711b0a269d3fe4fbdef3565ae0fa4d63732c8dab`
  (the 017-l report SELF)
- Implementation head SHA: 5fd23412b8476d4da7df0549676077ce9db56590
- Report publication commit: SELF
- Implementation commits pushed before report:
  - `dd116c115d9d463cfdca941fec43c3875965c1f4` (source A: pairing
    identity/causality repair, D10 matrix + D09 partial-negative
    suite, contract/TESTING/ledger/both architecture maps +
    byte-identical compact mirror, activated order and active
    unchanged)
  - `5fd23412b8476d4da7df0549676077ce9db56590` (manifest B:
    `packaging/dev_provenance_manifest.json` refreshed — source
    `dd116c1…`, 187 inputs, wheel `d2c786177f2b5a94…`, sdist
    `9b851cd4b684a123…`; frozen RC10 publication section untouched)
- New PR this round: NO; amended existing: YES; merge performed: NO
- No reset/clean/rebase/squash/amend/force/force-with-lease; every
  prior published commit preserved (append-only history)

## Changes and files
Round diff (7 starting SHA .. implementation head) is exactly 12
files:
- `src/slaif_local_coding/constitution/bundles/observation_models.py`
  — new closed-vocabulary limitations `MISSING_CALL_ID`,
  `MALFORMED_CALL_ID`, `PRE_CALL_RESULT`.
- `src/slaif_local_coding/constitution/bundles/tool_results.py` —
  eligibility-independent schema-evidenced call-ID inventory
  (`_call_records`); eligible-call derivation with exact numeric
  structural positions (`_call_entries`); results collected with
  positions (`_result_entries`); `_pair_endpoint` rewritten:
  duplicate bookkeeping over the full inventory (every occurrence
  typed, never first-match), missing/empty/non-string ID records
  observable and never pairing, single-result pairing gated on
  `result_position > call_position` (pre-call results built then
  typed `PRE_CALL_RESULT` non-removable with no digest/span/
  proven-executed claim; mixed-endpoint suppression override
  unchanged), orphan/mismatched/missing/multi-chunk typing
  unchanged; module docstring law updated.
- `tests/test_bundle_d10_matrix.py` (new, 40 tests) — public D10
  composition matrix and pure D09 unsupported/partial matrix
  (Requirements 3 and 4; Responses and Chat).
- `docs/CACHE-OBSERVATION-CONTRACT.md` — D05 identity-conflict and
  structural-causality laws, status paragraph, limitation
  vocabulary, deferred-section 017-m paragraph.
- `docs/CACHE-REWORK-LEDGER.md` — 017-m narrative paragraph; D09
  note (pure partial negatives earned, multi-chunk still NOT RUN);
  D10 row `NOT RUN` -> `PENDING` with named 017-m evidence and
  strategic-acceptance-outstanding; objective-017 stage row; state
  summary sentence.
- `TESTING.md` — 017-m round sentence with the named suite and
  boundary statements.
- `ARCHITECTURE.md` and `ARCHITECTURE-for-agents.md` — objective-017
  status/history prose compressed to concise current earned
  observation-grammar scope + offline-utility status + explicit D09
  actual-trace/process-collector gap + ledger/contract links (all
  normative law preserved; detailed round history remains in the
  ledger/immutable OAP); 017-m pairing/causality law added to the
  compact map's read-observation paragraph.
- `oap/strategic-instructions/ARCHITECTURE-for-agents.md` — compact
  mirror, byte-identical to the repo map (`cmp` clean).
- `oap/orders/017-m-observer-pairing-and-causality.md` — activated
  order, exact unchanged strategic bytes.
- `oap/active` — `017-m`, exact unchanged strategic bytes.
- `packaging/dev_provenance_manifest.json` — manifest B refresh only.

## Acceptance evidence
### Criterion 1 — identity conflicts precede read eligibility
- Result: PASS.
- Evidence: frozen probe
  `check-observer-pairing-causality.py` at the final head:
  `responses_unknown_duplicate_does_not_hide_id_conflict` and
  `chat_unknown_duplicate_does_not_hide_id_conflict` PASS (both
  FAILED at the 017-l head) with the positive controls still valid.
  In-suite: `TestIdentityConflictPrecedesEligibility` (14 tests) —
  unknown/ineligible same-ID conflicts typed `DUPLICATE_CALL_ID` at
  every occurrence on Responses and Chat (supported/unsupported
  names, exec/shell families, identical and conflicting duplicate
  calls); unrelated unique unknown calls neither recorded nor
  poisoning separate valid chains (exact earned read plus no
  unpaired record for the unknown call; its orphan result stays
  `MISMATCHED_CALL_ID`); nested text objects carrying id/name are
  not call records; missing (absent key, explicit null, empty
  string) IDs typed `MISSING_CALL_ID` and non-string IDs (int,
  list) typed `MALFORMED_CALL_ID` — observable, never paired,
  never inventing an ID, never acquiring content; exact
  ID/name/arguments association preserved; bounds and non-echoing
  repr asserted.
### Criterion 2 — a result must follow its matching call
- Result: PASS.
- Evidence: frozen probe: `responses_result_before_call_is_not_
  acquired` and `chat_result_before_call_is_not_acquired` PASS
  (both FAILED at the 017-l head). In-suite:
  `TestStructuralCausality` (9 tests) — pre-call results on
  Responses and Chat keep a typed `PRE_CALL_RESULT` observation
  (UNSUPPORTED, non-removable, no bundle/member digest, no source
  span, no proven-executed claim; wrapper facts and
  requested-members preserved); causality from numeric positions
  including the Chat assistant message index; `>=10` structural
  positions with non-monotonic IDs expose lexical/JSONPath-string
  ordering mistakes in both directions (call at index 2 / result at
  index 10 earned; call at index 10 / result at index 2 rejected);
  missing initial calls remain unsupported (`MISMATCHED_CALL_ID`);
  mixed-endpoint pre-call pairs stay `ENDPOINT_UNSUPPORTED`;
  independent valid chains still earn exact span/digest/members/
  width while the ambiguous chain is rejected.
### Criterion 3 — complete public D10 matrix
- Result: PASS (delivery claim requires independent strategic
  acceptance).
- Evidence: `TestD10MatrixComposition` (5 tests) plus the matrix
  classes above — ordinary valid reads amid many unrelated calls
  (exact earned read; only the unrelated orphan result
  bookkept), duplicate same-call results remain
  `MULTI_CHUNK_DEFERRED` (unsupported absent later earned
  process-chain evidence), exact Unicode/CRLF source slices
  (`\r\n` + `é` byte-exact against the content span and digest),
  unchanged inputs (deep-equality before/after every call),
  non-echoing reprs (no raw source/command literal in
  `str`/`repr` of report/observations/records), preserved
  declared bounds (`OVER_BOUND` at `max_commands=1`). Selected
  endpoint, mixed domain and ignored other-domain behavior
  preserve prior law (all pre-existing 017 endpoint tests pass
  unchanged). No constructor-only proof (all cases run through
  public `observe_request`) and no blanket reject-all (positive
  acquisitions asserted in the same payloads).
### Criterion 4 — pure unsupported/partial matrix
- Result: PASS (D09 partial negatives; NOT multi-chunk evidence).
- Evidence: `TestUnsupportedAndPartialMatrix` (12 tests) — command
  substitution (`$(…)` and backticks) typed `COMMAND_SUBSTITUTION`;
  false/conditional/unexecuted branches (`false && cat A.md`,
  `cat A.md && false`, `if [ -f A.md ]; then cat A.md; fi`) typed
  `COMMAND_UNSUPPORTED`; partial readers (`head A.md`, `sed -n
  '1,10p' A.md`) typed `FRAGMENT_COMMAND`; `||`/`;` chains typed
  `PIPE`/`MULTIPLE_COMMANDS`; known truncated (`TRUNCATED`),
  nonzero (`NONZERO_EXIT`), missing-body (`MISSING_BODY`), running
  (`PROCESS_RUNNING`) and unknown-completion (`UNKNOWN_COMPLETION`)
  wrappers never complete — all non-removable, no digest/span/
  proven-executed, contrasted with the exact proven empty
  successful output (COMPLETE, removable, `EMPTY_SOURCE_SHA256`,
  zero-length span). No shell/filesystem/network execution oracle,
  no new grammar family, no invented wrapper; all previously
  earned literal read/plan/loop positives, exact spans, aggregate
  work bounds and occurrence/member-hash/slot-width laws are
  preserved (499 pre-existing observer tests pass unchanged).
  D09 multi-chunk/process association remains deferred, never
  marked delivered.
### Documentation
- Result: PASS.
- Evidence: observation contract (D05 identity/causality laws,
  vocabulary, status, deferred section), TESTING.md round
  sentence, ledger (017-m narrative, D09 note, D10 `PENDING`
  with named evidence, objective-017 row, state summary), both
  architecture maps with 017 prose compressed to concise current
  earned scope + offline-utility status + explicit D09 gap +
  ledger/contract links (normative law preserved; round history
  remains ledger/immutable OAP), compact mirror `cmp`
  byte-identical; PR body updated (017-m round-history entry,
  earned/remaining boundaries, 017-m evidence block). No
  architecture exception; no change to the human handoff, plan,
  frozen releases or prior OAP bytes.

## Verification
- 16 frozen strategic probes, each
  `REPO/.venv/bin/python STRATEGIC_HOME/probes/<script> --head
  5fd23412b8476d4da7df0549676077ce9db56590` (canonical repo venv;
  owned 0700 temp results root outside the strategic workspace):
  PASSED — 23/23, 16/16, 5/5, 6/6, 40/40, 63/63,
  10/10 (observer; 162 quoted-word variants), 12/12, 3/3, 2/2,
  4 checks + 1 memory measurement (not a test), 2/2, 2/2, 8/8,
  5/5 (utility, 38 checks total) and 8/8 (new
  `check-observer-pairing-causality.py`) — every control/check
  passed with `positive_control_valid: true`. Pre-fix baseline at
  the 017-l head (also captured): 15 legacy scripts PASSED, new
  probe 4/8 (the two identity-conflict and two pre-call cases).
  Every script SHA-256 verified against the immutable baseline
  `STRATEGIC_HOME/reviews/017-m-probe-hashes.json` (16/16) before
  running; no script or hash file edited.
- Focused observer suites (all `tests/test_bundle_*.py`
  including the new matrix): `uv run --frozen pytest -q
  tests/test_bundle_observation_models.py tests/test_bundle_
  client_paths.py tests/test_bundle_root_envelopes.py tests/
  test_bundle_read_grammar.py tests/test_bundle_tool_results.py
  tests/test_bundle_observe.py tests/test_bundle_shell_tokens.py
  tests/test_bundle_compound_reads.py tests/test_bundle_literal_
  loops.py tests/test_bundle_d10_matrix.py`: PASSED — 539 passed,
  0 failed, 0 skipped.
- Complete final TESTING gate (process-local umask 022, run once
  after the final source A/manifest B; no deliberate stale-
  manifest failure, no redundant unchanged reruns):
  - `uv lock --check`: PASSED
  - `uv sync --frozen --extra dev`: PASSED
  - `uv run --frozen ruff check .`: PASSED
  - `uv run --frozen ruff format --check .`: PASSED (520 files
    formatted)
  - `uv run --frozen mypy src tests`: PASSED (108 source files,
    no issues)
  - `uv run --frozen python scripts/docs_consistency_check.py`:
    PASSED (19 claim docs checked)
  - `uv run --frozen pytest -q`: PASSED — 2273 passed, 28 skipped
    (27 prior stage skips + exactly one 017-i real-`chown`
    environment skip — never counted passed), 0 failed,
    380.33s
  - `uv build`: PASSED — wheel `d2c786177f2b5a9485b3deec3be60c
    c27c0a4ec43c1090c09e1afe0eaaa46669` / sdist
    `9b851cd4b684a1233668a24a74667ea64c9c3a1574b6f85d5689c58392
    33fc1f`, equal to the manifest digests
  - `uv run --frozen python scripts/artifact_policy_check.py
    --dist dist --inspect`: PASSED (ok, 0 violations)
  - `uv run --frozen python scripts/artifact_policy_check.py
    --dist dist --install-smoke`: PASSED (ok, 0 violations)
  - `uv run --frozen python scripts/dev_provenance_manifest.py
    --verify --dist dist`: PASSED (state=development, head
    `5fd2341…`)
  - `python -m compileall -q src tests oap/bin scripts`: PASSED
- `bash -n` over `oap/bin/bootstrap-two-codex-oap.sh`,
  `oap/bin/launch-coding-agent.sh`,
  `oap/bin/launch-strategic-agent.sh`, `packaging/readyz-wait.sh`
  (no shell script changed this round): PASSED
- `git diff --check origin/main..HEAD`: PASSED (clean)
- Targeted credential/raw-log/privacy scan of the round diff
  (`711b0a2…..5fd2341…`): PASSED — 0 hits for bearer/key-like
  tokens, private/loopback URLs, host references, or API-key
  literals; synthetic fixture values only.
- Invariance: PASSED — frozen `docs/CACHE-REWORK.md` SHA-256
  `410df5c0b8f90b05220adc32c8e673b143c0cf1fa3da02270d91ac453c8
  86abd` unchanged; `docs/RC-HANDOFF.md`,
  `docs/CACHE-IMPLEMENTATION-PLAN.md`, all prior `oap/orders/*`
  and `oap/reports/*`, and `packaging/releases/` byte-unchanged in
  the round diff; compact mirror `cmp` byte-identical; frozen RC10
  baseline re-proved in-suite
  (`test_real_frozen_publication_baseline_holds` within the 2273).
- Clean source-A `git archive` reproduction (owned 0700 temp
  root): PASSED — `git archive dd116c1…` with utility
  `scripts/real_client_capture.py`, fake child
  `scripts/real_client_capture_fake_child.py`,
  `tests/test_real_client_capture.py` and the new
  `tests/test_bundle_d10_matrix.py` present; `uv sync --frozen
  --extra dev` + `uv build` from the clean tree reproduced
  byte-identical wheel `d2c786177f2b…` / sdist `9b851cd4b684…`
  (equal to the manifest digests).
- Fresh non-editable installed-wheel functional controls (fresh
  CPython 3.12.15 venv in an owned 0700 temp root; `uv pip
  install --no-cache-dir` of the built wheel `d2c786177f2b…`;
  package path
  `…/wheelvenv/.venv/lib/python3.12/site-packages/slaif_local_
  coding/__init__.py` proves the installed wheel is used outside
  the repository; version 0.1.0): PASSED — 21/21: the 11 recorded
  017-g observer functional controls re-exercised with actual
  positive/negative behavior assertions (four quoted-prefix/
  suffix defect forms typed `QUOTED_OPERAND` non-removable with
  no digest/span/phantom members; first-position defect typed;
  whole-word double- and single-quoted controls and the plain
  controls earned with exact members; guarded ordered bundle with
  exact digest/slot width/exact content span; unguarded form
  typed with preserved requested members and no digest; repr
  privacy) PLUS all 8 new public pairing/causality cases against
  the installed changed package.

## Live model/service evidence
- N/A: the order authorizes offline pure/synthetic fixtures and
  owned ephemeral loopback tests only. No live inference, no
  actual client session/capture, no model/GPU/product-API/
  Gateway call, no Docker host use, no namespace/tracing
  experiment. **Protected fixture changed: NO** — Qwen/vLLM
  18020, `qwen-serving`, models/venvs/patches/flags, API-key
  files, firewall/VPN/network, active protected Codex profiles/
  auth/config all untouched; no original raw capture read or
  recreated. Unknown startup safety remains NOT READY (no
  handwritten readiness substitution).
- Errata clarification of the immutable 017-l report (L/K
  artifacts NOT rewritten, per the order):
  1. The L report's live-service paragraph ends
     "Protected fixtures (...) unchanged: NO", while its safety
     section correctly states "Protected 18020/Qwen/Codex
     fixture changed: NO". The verified fact, identical for both
     rounds, is **Protected fixture changed: NO** — no protected
     model/profile/service/network fixture was changed in 017-l
     (offline synthetic work only, as the L order and L report's
     safety section state) and none was changed in 017-m (this
     report's verification contains no live call of any kind).
     The "unchanged: NO" wording is a clerical inversion; no
     truly contrary evidence was found, and no live-service/API
     probe or auth/history read was performed merely to confirm
     wording (absence is never inferred from mtimes).
  2. The L report's safety section says "round diff is exactly
     the 11 source-A files plus manifest". The actual verified
     017-l source-A commit `17e09b8…` diff is **10 source-A
     files** (ARCHITECTURE-for-agents.md, ARCHITECTURE.md,
     TESTING.md, docs/CACHE-OBSERVATION-CONTRACT.md,
     docs/CACHE-REWORK-LEDGER.md, oap/active,
     oap/orders/017-l-owned-io-and-original-seeds.md,
     oap/strategic-instructions/ARCHITECTURE-for-agents.md,
     scripts/real_client_capture.py,
     tests/test_real_client_capture.py) **plus 1 manifest file**
     (manifest B `cd9f4fe…`,
     `packaging/dev_provenance_manifest.json`) = 11 files total.
  3. K force-push chronology: the single recorded force-push on
     PR #25 (2026-10-21T05:13:29Z, `ebe454cb…` ->
     `bed32f2…`, per `reviews/017-k-force-push-events.json`)
     happened **during round K, before L activation, not before
     K activation** — K source A `c0db839…` was committed at
     05:12:46Z, the force-push at 05:13:29Z, K's report
     `d11ca86…` at 05:23:41Z, and L's activated order/active
     landed with L source A `17e09b8…` at 05:57:03Z.

## GitHub CI / required checks
- Implementation-head (`5fd2341…`) check state, all 8 required
  checks present and SUCCESS (main workflow run 39559831781;
  CodeQL run 39559827124):
  - `test`: SUCCESS (4m57s)
  - `gateway-contract`: SUCCESS (14s)
  - `docker`: SUCCESS (1m35s)
  - `docker-published`: SUCCESS (1m20s, prepublication NOT RUN
    for image qualification per policy)
  - `operator-session`: SUCCESS (1m9s)
  - `CodeQL`: SUCCESS
  - `Analyze (actions)`: SUCCESS
  - `Analyze (python)`: SUCCESS
- All required green at drafting: YES.
- Report-head checks may be pending; strategy verifies.

## Local setup/dependencies
- Repository-owned `.venv` (Python 3.12.15, uv locked/frozen);
  no new dependency, framework or service; no sudo used.
  Process-local umask 022 for the full repository test gate (the
  verified context per TESTING.md); owned 0700 protected temp
  roots for probe results, the git-archive reproduction, and the
  fresh-wheel venv). Fresh CPython 3.12.15 venv outside the repository for the
  installed-wheel controls (wheel installed non-editable,
  no-cache). No durable docs/config change beyond the listed
  round files.

## Documentation
- Updated: `docs/CACHE-OBSERVATION-CONTRACT.md` (D05 identity/
  causality laws, vocabulary, status, deferred section),
  `TESTING.md` (017-m round sentence),
  `docs/CACHE-REWORK-LEDGER.md` (017-m narrative; D09 note; D10
  `PENDING` with named evidence; objective-017 row; state
  summary), `ARCHITECTURE.md` and `ARCHITECTURE-for-agents.md`
  (017 status prose compressed; 017-m pairing/causality law in
  the compact read-observation paragraph), byte-identical
  compact mirror, PR body. Required: behavior, configuration-
  adjacent contract, tests and limitations all changed.

## Safety/scope confirmations
- Unrelated files: none touched — round diff is exactly the 12
  listed files (11 source-A files plus 1 manifest B file).
- Secrets/raw content: none committed, printed, logged or
  exposed; synthetic fixtures only; targeted scan of the round
  diff clean; reprs non-echoing by law and by test.
- Production/protected resources: no production system or data
  touched. Protected 18020/Qwen/Codex fixture changed: NO.
- Required tests skipped/not run: none beyond the standing
  skips — 27 prior stage skips + exactly one 017-i real-`chown`
  environment skip, never counted passed. D09 multi-chunk/
  process association and all v1 runtime/model/native/restart
  qualification remain NOT RUN (planned for their owning stages).
- Scope deviation: none — no capture utility/child modification,
  no actual capture, no process collector, no graph/RAM/
  recovery/tokenizer/compiler/image/pipeline/Gateway/legacy
  change; existing observer stays inert; no new framework/
  dependency or opportunistic refactor; no architecture
  exception; no change to human handoff/plan/frozen releases/
  prior OAP bytes.
- Extra objective PR: NO. Coding merge: NO. Auto-merge: not
  enabled.
- Active/order edited: NO (exact unchanged strategic bytes
  committed; `oap/active` = `017-m`). Report commit report-only:
  YES (staged path `oap/reports/017-m-observer-pairing-and-
  causality.md` only; sole parent = implementation head).

## Known limitations/blockers
- None blocking. Open items by design (not blockers): D09
  multi-chunk process completion proof and the actual-trace
  process/chunk collector remain deferred to a later same-PR
  suffix (a later exact order may authorize one bounded reviewed
  actual capture, then the collector, subject to review); the
  D10 delivery claim requires independent strategic acceptance;
  whole-017 acceptance and objectives 018-024 remain with
  strategy.

## Recommended strategic follow-up
Factual only; strategy decides. Independent verification of the
017-m head is available: 16 frozen probes (baseline
`reviews/017-m-probe-hashes.json`), the 40-test public matrix
(`tests/test_bundle_d10_matrix.py`), the 8/8 pairing probe at
`5fd2341…`, and the 21/21 fresh-wheel controls. If accepted, the
remaining 017 work is the D09 multi-chunk/process association
(actual-trace capture and process/chunk collector) for a later
same-PR suffix; otherwise the round stands as a bounded
observation-surface repair with D10 `PENDING`.

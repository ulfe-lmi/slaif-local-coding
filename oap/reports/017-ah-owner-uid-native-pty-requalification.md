# 017-ah round report — ONE actual owner-UID native PTY requalification (verified PASS at qualified scope; PARTIAL delivery with the preserved hermetic CI failure)

Status: PARTIAL for delivery, with the ordered single actual attempt a verified actual PASS at its qualified scope: the ONE authorized attempt RAN EXACTLY ONCE at literal attempt head P and produced the measured positive (exact pinned current executable, independently measured expected PTY, ONE visible final answer with no tool call, normal exit, SAME worker restored, owned fixture converged absent-verified). The round is delivered as an accurate PARTIAL solely because of ONE preserved hermetic CI failure — the AG-round test whose real-checkout AH order/admission absence assertions were invalidated by AH activation itself (no production defect or native-readiness failure is proven; the order forbids source/test repair, skip or xfail under AH, so it is preserved, and a later software continuation owns the hermetic repair). NO source/helper/test/lock/workflow change, no retry, re-admission or in-round source repair under AH. AF remains CLOSED FAILED (its ONE admission spent forever). No native-ready, whole-017 or v1 runtime claim is made anywhere in this report.

Implementation head SHA: 3ba0970229cea50c20379fb83cbfab4abc3c08dc
Report publication commit: SELF

## Protocol facts (coding protocol)
- Repository `ulfe-lmi/slaif-local-coding`; PR #25 OPEN at
  https://github.com/ulfe-lmi/slaif-local-coding/pull/25, branch
  `oap/017-cache-read-observation`, base main
  `96c790423f6f0097a56a0b12bacda8a9b6da6aba`. No second PR, no merge,
  no auto-merge (coding law). Standard round-report template as prior
  rounds.
- Round start: AG report-only SELF
  `8712235efc1d45f168c48fffe202ca4eb74ed4d0`. ONE activation control OK
  was delivered to the existing managed wait 19396 and consumed once;
  `oap/active` = `017-ah` selects the unique immutable order
  `oap/orders/017-ah-owner-uid-native-pty-requalification.md`
  (15978 B, SHA-256
  `7c67b2f21773082dc523a4f9e6ea92d7b102d3cc772cd985803c36e1fe71cfa2`),
  committed exactly pre-attempt with `oap/active`
  (7 B, SHA-256
  `caa8cf74f073eec6306bd2dcbb2a6e2572cef8e0155df84bf93c76b3bf6f2e96`)
  as literal attempt head P
  `06806eeeebac76b38f9ab5d6bbcfd2940f8b66a8` (2 paths only — source,
  helpers, tests, lock and workflows unchanged at P).
- After the root-reviewed concrete plan, ONE managed phase-continuation
  control wait was created on the ORIGINAL control FIFO (actual handle
  31222 / Python PID 3833957 / birth 184063503, printed at creation and
  retained; the initial creation line was a parse failure — see process
  qualifications). Coding stayed idle; root ran the ONE reviewed
  finite managed non-Codex operator over the SAME foreground handoff.
  ONE phase-control OK returned the actual outcome to this SAME worker;
  that wait was consumed once.
- Root final-response reader 13825 (Python PID 3815392, birth
  183841473) is separate and blocks on the ORIGINAL response FIFO until
  this canonical SELF is published plus ONE final response OK.
- Commit chain: attempt P (order+active) → docs A
  `a3cd5ae61080cf51cf92671e514320c1d7ac6b8e` (6 tracked doc paths; the
  A-vs-P diff is exactly those six paths) → manifest-only B
  `3ba0970229cea50c20379fb83cbfab4abc3c08dc` (the A..B diff is exactly
  `packaging/dev_provenance_manifest.json`) = literal implementation
  head. This report is the single report-only SELF commit on top of B
  (sole parent B). All 17 helper bytes and the runtime source are
  unchanged P→B (clean archive proof below).
- Setup/privacy/protected fixture: routine repo-local setup only — the
  repo venv (CPython 3.12.15, frozen lock) and protected private AH
  root `/home/janezp/oap-017ah-work` (0700 parents under same-shell
  077; MANUAL files 0600 under the protected parents — tool-created
  archive extraction/artifacts keep actual modes, e.g. the rebuilt
  wheel/sdist are 0644 under the 0700 out parent, not 0600); a fresh
  `uv build` and the prescribed gate ran under it. No system package/venv/sudo/service change, no
  protected Qwen/Codex state change, no real credential/customer
  material observed or retained (the synthetic fixture environment
  carried synthetic values only; retained metadata lists key names and
  the env-file SHA-256, never values).

## The ONE actual attempt (measured; RAN EXACTLY ONCE)
- Binding: run `1bbeeabfb9434ebf965eaa7e1a624a49`; CID
  `0b5d35f07f984d1fe1c3344e6f6f606afb1142bef9c5e740b14f2d2c3e9da1bc`;
  image `sha256:085bb42752808e9eb52192e0486306f9cc5006b6ac44e2c0049071ea63a74997`;
  frozen owner identity 1001:1001, groups exactly [1001]
  (fingerprint `7e5a6432d91bc873c3c3208e384efd48fac7f1bff3e8fe6b93240343cc5387b0`);
  bind head P; order/active hashes as above; ONE owner / RAM context /
  absolute 1800 s END / cumulative ledger / 600 s convergence grace
  (no deadline expired, no backstop).
- Stop (measured): the SAME worker 598258 (birth 150182858, tty 34834,
  pgrp 598258, session 2014146) was stopped exactly ONCE through the
  reviewed exact-group stop issued by root; monitor mode was measured
  ON via `set -o` with NO option name BEFORE any setter (the required
  attach-branch gate; OFF/unknown would have applied the failure law);
  the attach window used `set +m`.
- Attach + discovery (measured): the SAME Bash 2014146 (birth
  95656910) foreground-launched ONE native in the exact owned prepared
  CID with the exact frozen argv `codex --yolo --profile
  early-beta` (argv SHA-256
  `fe2a0aa6027d38a4256d430ac1830a90ce1ca5df72b0aba3bbc7d984d00b9429`)
  and the synthetic environment carried in the explicit attach via the
  owner-created env-file path (key names `CODEX_HOME` /
  `SLAIF_SYNTHETIC_API_KEY` only; file SHA-256
  `b31fdcdafca898e5e72b35e89a860bd4d2dcd9e2497d32493168ecda987f0b75`;
  no key values on argv or retained; never assumed inherited). Native
  v0.164.0 was uniquely discovered from the exact-CID inventory:
  pid 3836555, birth 184083134 (above the launch floor 184080662),
  UID/GID/groups 1001:1001/[1001] equal to the frozen owner identity,
  tty matched.
- Independent expected PTY (measured): devpts baseline ZERO slave rows
  (empty, valid), then ONE fresh owned allocation 136:0 (uid 1001, node
  gid 5, inode 3, mode 400) coherent with the baseline device and
  namespace [1048813, 1] under the MEASURED devpts policy (fstype
  devpts, gid 5, mode 400) — the legal node GID is governed by that
  policy, lawfully distinct from the frozen process GID 1001.
  `expected_tty_nr` 34816 is the proc new-encode of 136:0 (never
  MKDEV); the guarded `-I -S` probe (site/startup isolation verified
  false/false) read only the fixture's OWN devpts.
- Current executable (measured): through the existing unprivileged
  registered-CID channel, the subject current exe equals the pinned
  public 0.164.0 artifact — SHA-256
  `b93f6811d3f653f0fb83be4050d857fb9abbb111dfa2ce160563327daff7f306`
  (308139304 B; archive SHA-256
  `90dd0b03b28afcb7fa733a4f73b413db2916a47347efd43fb669cc1c774ee8e4`;
  tag rust-v0.164.0, commit `6aaac694803004a63c6f393d153c96d22521a6b9`;
  `signature_verification: not-run` in this attempt) —
  `binary_verified: true` in the retained subject frame.
- Diagnostic + COUNT LAW (measured; separate ledgers, never conflated):
  ONE visible final assistant answer ("slaif fixed final text") with no
  tool call, then a normal `/exit` with the SAME Bash prompt.
  Controller wire_requests: 2 at the finish observation (0 / unobserved
  at the prepare observation) — the second POST's cause is UNMEASURED
  (no retained body/status trace; no forensics or rerun authorized, and
  it is never called a second user diagnostic); controller snapshot
  ledger requests: 4 (includes quiesce/export commands); host ledger:
  2 API requests (2 admitted, 0 refused, 0 refusals, 38 docker
  admissions, 25617 B drained and retained); `issued_calls` empty; the
  retained metadata record (`slaif-fixture-metadata-diagnostic-v1`)
  proves endpoint/schema/known-name presence only (endpoint responses;
  10 function names; known `exec_command`/`write_stdin`; 8 unknown
  unsupported; traversal depth 3; raw content NOT retained).
- Quiesce / export / teardown (measured): quiesce closed-pass (active
  0, residual writers 0, handlers/subject/tools stopped, provider
  sockets closed); the 3273-byte export (SHA-256
  `3a1b5bd584414957598a6771b44817873d81bad8579d2fc831d1e6183f403861`,
  exporter uid 21001) was exported BEFORE teardown and revalidated;
  exact-CID teardown converged: descendants 1 → 0; container and image
  independently verified absent (HTTP 404 on the verified default local
  socket); the unrelated same-UID sentinel survived with its birth; the
  owner-removed env file, work/control leaves absent; supervisor
  converged true, backstop false.
- Restoration (measured) + TTY qualification: the SAME stopped worker
  was restored in the SAME Bash — monitor restored to its measured ON
  state, `jobs -l` bound the actual numeric J=1 to the worker group,
  `fg %1`, foreground re-measured 598258, restoration closed
  "restored", worker_state S, worker_stopped false at the terminal
  frame. The physical restoration bool alone does NOT prove a
  functional TUI: after `fg` the TUI remained canonical/echo (a
  continuation Enter became a newline; no model turn started); root
  restored raw/noecho on the exact verified /dev/pts/18 (TCSANOW, no
  inputflush; no signal/restart/profile/service change) before the
  coding input resumed.
- Publication ordering (measured): owner evidence FIRST
  (production-validated), protected native terminal record SECOND
  (one-shot, fail-if-exists), same pending-pass journal finalization
  LAST (journal `slaif-oap-order-admission-v1`: ONE attempt, head P,
  status pass; terminal, never reset). The retained native run record's
  `attempt: "running"` field is the pre-finalization snapshot; the
  actual journal terminal pass was verified separately.

## Process qualifications (disclosed, by immutable reference)
- Validator choice: the original fixed-21002 validator refused the AH
  evidence BEFORE any output/file/resource query; root corrected to the
  explicit `validate_ah_owner_run_evidence`. No record edit, no runtime
  retry (root review `reviews/017-ah-actual-native-result.json`).
- Phase-wait parse: the initial at-creation parse line failed (`cut
  -d') '` rejected the 2-char delimiter; the `COMM=` field actually
  carried state `R`); the wait facts were re-measured from /proc and
  root-verified (PID 3833957, birth 184063503, state S,
  wait_for_partner); the initial line is retained as printed.
- Gate live-context classifier: root's first read-only classifier
  expected argv0 `pytest` but the interpreter launches it; corrected by
  direct known-UV-children — no runtime/test rerun (root review
  `reviews/017-ah-gate-live-context.json`).
- Manual /tmp scratch occurrence: one read of the current PR body was
  temporarily redirected to `/tmp/pr25-body-current.txt` (7396 B, mode
  0600, inode 4865994, containing only the then-current public PR body)
  in breach of the protected-root-only rule; the file is preserved AS
  IS (no cleanup/chmod/rewrite) and is disclosed here rather than
  repaired. All remaining scratch/payload files were created directly
  under the protected AH root.
- Residuals carried by reference: Bash 5.3.9(1) vs static 5.3
  `b8c60bc9` patch delta; Docker termios not statically modeled; the
  measured monitor ON was the attach gate.

## Delivery (docs A, manifest B, gate, CI)
- Docs A (`a3cd5ae`): exactly 6 tracked doc paths — human
  `ARCHITECTURE.md` (new 017-ah paragraph), compact
  `ARCHITECTURE-for-agents.md` plus its tracked
  `oap/strategic-instructions/` copy (all three compact copies
  byte-equal, SHA-256 `d0bf0d62e9af4ee47655d6e4203b9e9916ec22fb4515ecdaeff9b976021cdd4b`;
  the strategic-home third copy synchronized outside Git),
  `docs/CACHE-OBSERVATION-CONTRACT.md` (new section 11p),
  `docs/CACHE-REWORK-LEDGER.md` (017-row 017-ah segment), `TESTING.md`
  (017-ah round paragraph). Every 017-ah text carries the TTY,
  validator-choice and wait-parse qualifications, the count law, the
  not-earned list, and the AF-closed-FAILED / AD-PARTIAL immutable
  references.
- Manifest-only B (`3ba09702`): the A..B diff is exactly the
  development manifest (sdist rebind, qualification label, source
  commit, two changed doc input hashes); the 200-input map, toolchain
  and frozen-publication binding are unchanged in meaning.
- Prescribed locked gate at B, run ONCE (driver umask 077; pytest
  child only umask 022; non-root UID/GID 1001; actual live gate/pytest
  PID+UID+Umask captured by root at observation time): 12/13 steps
  EXIT 0 (lock, sync, ruff, format, mypy, docs, build, inspect, smoke,
  version, compileall, prov); pytest EXIT 1 with exactly the ONE
  preserved hermetic failure below — 1 failed, 3426 passed, 28 skipped
  in 563.90 s. All 39 per-step captures (out/err/exit) + summary
  retained 0600 under `/home/janezp/oap-017ah-work/gate-run-1/`.
- CI at attempt head P (measured): 9 SUCCESS / 1 FAILURE (GitHub run
  40780306145, test job 123140025243): the single failure is
  `tests/test_cache_native_fixture_native_handoff.py::test_ag_ah_refused_under_ag_active_before_admission`
  (lines 3498/3501/3502) — an otherwise synthetic AG-active test that
  ends by asserting the REAL AH order/admission ABSENCE in the
  checkout, a premise AH activation itself invalidated (the order file
  is committed at P; the local admission namespace is consumed, so the
  later two assertions are likewise stale). No production defect or
  native-readiness failure is proven.
- CI at implementation head B (GitHub run 40788148652, measured):
  exactly 10 check-runs completed — 9 SUCCESS (Analyze (actions),
  Analyze (python), CodeQL, cache-native-containment,
  cache-native-fixture, docker, docker-published, gateway-contract,
  operator-session) / 1 FAILURE (`test`, check-run 123166409675): the
  SAME single preserved hermetic failure measured at P and in the
  local B gate. All required green at drafting: NO — the single
  preserved failure keeps delivery PARTIAL; no repair/skip/xfail
  under AH.

## Verification
- Gate (at B): 13 command records as above — lock/sync/ruff/format/
  mypy/docs/build/inspect/smoke/version/compileall/prov EXIT 0;
  pytest EXIT 1 (the single preserved failure; 3426 passed, 28
  skipped).
- Pre-attempt pure harnesses (protected AH root, Python-B):
  `ah_operator_api_check.py` 78/78 checks PASS;
  `ah_operator_behavior_check.py` 46/46 checks PASS; 3/3 operator
  AST parses OK.
- Clean archive at literal A: 200/200 input-map hashes EXACT against
  the extracted `git archive` (tar SHA-256
  `16e512addbaeec56173e571d1670aff6a465532ac7f524e3251c15c42e1c3117`;
  recomputed `git archive` of A byte-equal to the retained tar); all
  17 `scripts/cache_native*` helper bytes equal Git B; A→B changed
  paths = manifest only.
- Clean-archive artifact rebuild (root-directed, bounded): both
  artifacts rebuilt from the clean extracted archive tree into a fresh
  private outdir (`uv build`, uv 0.12.5, exit 0) are byte-identical to
  the B manifest and to the gate-time repo `dist/` builds: wheel
  SHA-256 `1f2ebaff444be1ae90a7f1d863f462abcc82ff28caca448e28c206699fa4b50c`
  (142753 B, byte-identical to the AG-qualified wheel; 37 file
  entries) and sdist SHA-256
  `dd833f2493a0b1f6fa3ad087eaa9fddd77dab4c86e422892e7a5558e2afa4234`
  (1052390 B, 198 file entries). Measured sdist set law: the
  200-entry map contains the 4 container build inputs and excludes
  `.gitignore` and the 2 self-referential manifest files (absent from
  the map); the sdist omits exactly those 4 build inputs
  (.dockerignore, Dockerfile, compose.build.yaml, compose.yaml) and
  adds exactly `.gitignore` (tracked repo source, absent from the map)
  plus generated `PKG-INFO` (absent from Git A). All 197 sdist source
  entries are byte-exact against Git A blobs (197 + 1 generated =
  198). The retained archive-check JSON's
  `sdist_entries_equal_map_minus_exclusions: false` field is the
  expected 6-name consequence of that set difference — preserved AS
  IS, not a mismatch finding. Root independently qualified this
  rebuild (strategic
  `reviews/017-ah-actual-archive-rebuild-review.json`: all 197 sdist
  sources == Git A/extracted archive, 17 actual tar helpers == Git B,
  both rebuilt artifacts == B manifest/repo dist, PKG-INFO == wheel
  METADATA; the actual uv build tool exit 0 verified in the tool
  record, not the constant JSON alone); that review also carries the
  first FALSE-formula checker field and the preserved first verifier
  JSON (archive-recompute step initially ungenerated) qualifications.
- Unchanged-wheel functional evidence: the AG-qualified fresh locked
  install (18 locked distributions), installed27 27/27 functional and
  frozen21 21/21 proofs are referenced at their real head `f6414b85`
  with the measured wheel byte equality above — never relabeled as a
  new run (strategic
  `reviews/017-ag-archive-fresh-frozen-independent-review.json`).
- Suite checkpoints (historical, by reference): the two AG-current
  fixture suites hold 218 collected (native-prep 159 + native-handoff
  59); 835 collected / 835 passed pre-attempt across all eleven
  fixture suites at the historical AG source. No new tests this round.

## Live model/service evidence
- No real model/Gateway call in this round; the fixture synthetic
  loopback provider only (host ledger 2 API requests, admitted).
  Protected Qwen 18020 / qwen-serving / model / checkpoint / patches /
  venv / systemd / keys / profiles / firewall / VPN / network
  bindings: unchanged. The protected 18020 fixture changed: NO.
- No host-wide argv/name/UID candidate discovery in AH. The
  AH-required bounded production W/B-group preflight and at-stop
  measurements DID occur this round (root
  `reviews/017-ah-prelaunch-group-facts.json` and
  `reviews/017-ah-stop-at-use-facts.json`), and the actual public
  lifecycle measurements are the stop/attach/restoration/TTY facts
  above (exact verified /dev/pts/18 termios repair included). The ONE
  ordered production `collect_worker_group(RealProcTable)` check of
  round 017-ag is a separate immutable reference; nothing here implies
  no production collector use in AH.

## Local setup/dependencies
- Repo venv CPython 3.12.15, frozen lock SHA-256
  `1237cbd179f71b99984c80f927529549f5e61eb705585ef9cf2ab0fa9e26764a`
  (uv 0.12.5). Fresh `uv build` from A; prescribed gate under it.
  Protected AH root `/home/janezp/oap-017ah-work` (operator, runbook,
  verify, evidence, logs, gate-run-1, artifact-check, archive-check,
  archive-rebuild, report). No system package/venv/sudo/service change.

## Documentation
- Updated: the six tracked doc paths of docs A (human ARCH, all tracked
  compact copies, observation contract section 11p, ledger 017 row,
  TESTING round paragraph) plus the strategic-home compact copy
  synchronized outside Git — all three compact copies byte-equal.

## Protected evidence inventory (concise)
- `/home/janezp/oap-017ah-work/evidence/ah-owner-evidence.json` — 8842 B, SHA-256 `9009d429dec702da9d5d0957e34ee98d5823ffd75ad105391a09ed5d3e7087f8`, 0600 uid 1001, 0700 parent.
- `/home/janezp/oap-017ah-work/evidence/ah-native-run-record.json` — 3612 B, SHA-256 `044559e998feee1da801a45ed7f2d5283762e609bb835b66b70171ede7ebc937`, 0600 (pre-finalization snapshot; the terminal pass lives in the journal below).
- `/home/janezp/oap-017ah-work/logs/ah-operator-stage.log` — 4971 B, SHA-256 `ac1817da998df57a6e84984de9afc4056c824b3d2ffac8f664066869b09d1a9f`, 0600 (full stage stream s0-preflight → s4-terminal).
- Repo `.oap-local/017-ah/admission.json` — 184 B, SHA-256 `dc317fd606419a53ea956aec817f8b0656c0aa48d479eed40a69dd6fed15becc`, 0600 (journal: ONE attempt, head P, status pass; terminal, never reset).
- Gate: `/home/janezp/oap-017ah-work/gate-run-1/` — the 39 per-step out/err/exit captures (0600) including the pytest step, plus summary.log and driver, 0700 parent.
- Archive results: `/home/janezp/oap-017ah-work/archive-check/ah-archive-check.json` (974 B, its FALSE formula field retained AS IS) and `/home/janezp/oap-017ah-work/archive-rebuild/rebuild-verify.json` (3184 B, PASS) with its preserved first JSON (3185 B, archive-recompute step initially ungenerated); 0700 parents, uv-set 0644 rebuilt artifacts as noted above.
- All entries: uid 1001, 0600 files under 0700 protected parents. No exhaustive old-root index, READY or LAST audit, and no hash cycle is added.

## Safety/scope confirmations
- No secrets or real credentials in report/PR/evidence: the fixture
  environment carried synthetic values; retained metadata lists key
  names and the env-file SHA-256 only. No PRIVATE/customer source,
  prompts, or unrelated output retained; the explicitly approved
  synthetic diagnostic input, the selected test captures and ordinary
  repo test logs DO exist under the protected roots. The diagnostic
  metadata's raw-content-NOT-retained is that metadata's exact scope.
- Protected Qwen/Codex/network/service state: unchanged (above).
- Required tests skipped/not run: none beyond the standing 28 suite
  skips; the single preserved CI failure is recorded, not skipped.
- Software/source scope: unchanged (no source/helper/test/lock/workflow
  change under AH). Process deviations, disclosed above: the manual
  /tmp scratch occurrence and root's additional exact TTY restoration
  on /dev/pts/18 (physical restoration alone did not prove a
  functional TUI). AH had NO source/test repair allowance; the
  hermetic test failure is preserved for the later software
  continuation.
- Extra objective PR: NO. Coding merge: NO. Active/order edited: NO.
  Report commit report-only: yes (parent = literal B).

## Known limitations/blockers
- The ONE preserved hermetic CI failure (exact test, lines, cause and
  law above) keeps this round at PARTIAL delivery; the later software
  continuation owns the hermetic repair (absence/nonmutation proof
  moved wholly into owned hermetic synthetic repositories; stale
  real-checkout assumption removed; no skip/xfail/conditional
  weakening).
- Not earned by this diagnostic: actual tool/read/result formats;
  multichunk/process completion (D09 — NOT RUN); the required-syntax
  audit; whole-017 acceptance; v1 runtime; ALL 018–024. Measured
  startup/request schema only.
- The second POST's cause is unmeasured (no retained body/status
  trace); artifact signature verification not-run in this attempt.
- AF is CLOSED FAILED (preparation FAILED; worker stop NOT RUN; native
  NOT RUN; ONE admission spent forever — report
  `oap/reports/017-af-owner-uid-native-pty-qualification.md`);
  AD remains PARTIAL (report
  `oap/reports/017-ad-owner-uid-native-handoff-qualification.md`); the
  AG decision/qualifications carry by immutable reference
  (`reviews/017-ag-decision.md`).

## Recommended strategic follow-up
- A later software continuation (strategy-chosen) owning the hermetic
  repair of `test_ag_ah_refused_under_ag_active_before_admission`
  (move the absence/nonmutation proof wholly into owned hermetic
  synthetic repositories; preserve the AG-active refusal, the AH-only
  canonical-path law and the no-admission assertions there; remove the
  stale real-checkout absence assumption/comment; no skip/xfail).
- The remaining full-017 requirements stay mandatory and unchanged
  (D09 process/chunk collector, required-syntax audit, whole-017
  acceptance) as does ALL 018–024.

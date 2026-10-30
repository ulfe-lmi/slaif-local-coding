# 017-ae round report — independent native-attach PTY expectation producer (software-only)

Status: COMPLETE for the ordered software scope. The independent
native-attach PTY expectation producer was implemented on the EXISTING
fixture owner / guarded executor / NativeOwnerRun composition, with all
product proof over one coherent coupled fake process world (synthetic
repos, fake Docker/proc/clock). The future 017-af order/namespace is
INERT: no real AF order, namespace, admission or owner was created or
used. No Docker/native/client/subject operation occurred in LOCAL AE
work (the existing disposable CI jobs ran their original-scope
Docker/Python fixture checks; see Verification); no worker stop, device
write, host signal, or ptrace/prctl action occurred. The one bounded
ACTUAL host deviation — a `/dev/pts` inventory read during probe
debugging — is disclosed separately under Deviations, outside all
fake-seam proof. All prescribed local proofs ran at the literal
implementation head B; none is NOT RUN, none waived. GitHub and FIFO
synchronization did occur this round, so no blanket no-transport claim
is made.

Implementation head SHA: 3d7733c1f58e92e0a2552e32db0536862887b7d3
Report publication commit: SELF

## Protocol facts (coding protocol)
- Repository `ulfe-lmi/slaif-local-coding`; PR #25 OPEN at
  https://github.com/ulfe-lmi/slaif-local-coding/pull/25, branch
  `oap/017-cache-read-observation`, base main
  `96c790423f6f0097a56a0b12bacda8a9b6da6aba`. No second PR, no merge, no
  auto-merge (coding law). Standard round-report template as prior rounds.
- Round start: AD report-only SELF
  `8489dce5e2e9d20f321848ecdfd74f589451a19a` (sole parent of A). Source A
  `b7d92b127b0c8257e2d8ecffd2f7a8fd744cf616` (16 paths); manifest-only B
  `3d7733c1f58e92e0a2552e32db0536862887b7d3` is the literal implementation
  head. This report is the single report-only SELF commit on top of B.
  Fresh CI at the report head may be pending after push; strategy verifies
  it. The prepared in-memory post-push remote verifier
  (`verify_self_report_remote_017ae.py`, bound in the private READY) is
  REQUIRED after SELF, is prescribed/pending until the report is
  published, and has NOT yet been run.
- Setup/privacy/protected fixture: routine private setup only — a fresh
  locked venv (`fresh-venv-312-ae-locked`, Python 3.12.15) was created
  under the protected AE root and 18 distributions (including the
  clean-archive B wheel, under the frozen-export constraint) were
  installed into it; a git-archive extraction and `uv build` ran under
  the AE root (`archive-build-3d7733c1`). No system package/venv/sudo/
  service change, no protected Qwen/Codex state change; no real
  credential/customer material observed; the round evidence contains
  public/synthetic/seam notes, not a hashes-only universal claim.

## Measured round facts
- Activation: exact control OK on the existing managed control 98619
  (cat 3221883, direct child 598258) consumed once; `oap/active` =
  `017-ae` selects the unique immutable order
  `oap/orders/017-ae-native-pty-provenance-software.md` (13918 B,
  SHA-256 4ae4737a530f189ad635eb921f492642c99d311e1d32c1d582708c1fae23d1be).
- Implementation-head publication (order step 6): source A changes
  EXACTLY 16 paths — `oap/active` (7 B, `017-ae\n`) + the AE order file +
  six `scripts/cache_native_fixture_*` helpers (binding, ci, local,
  native_owner, native_prep, runtime_profile) + two extended test suites
  (test_cache_native_fixture_native_handoff.py,
  test_cache_native_fixture_native_prep.py) + six round docs
  (ARCHITECTURE.md, ARCHITECTURE-for-agents.md,
  oap/strategic-instructions/ARCHITECTURE-for-agents.md, TESTING.md,
  docs/CACHE-OBSERVATION-CONTRACT.md, docs/CACHE-REWORK-LEDGER.md); sole
  parent `8489dce5e2e9d20f321848ecdfd74f589451a19a`. B is manifest-only
  (development provenance, 200 inputs; the manifest's source binding is
  source A, not B; wheel byte-identical, sdist digest refreshed). Pushed and verified remote: remote branch head == PR25 head
  == B, clean.
- Implementation (software-only, fake seams only):
  - AF runtime-profile entry in the software selection table
    (PROFILE_OWNER_UID); the actual active/order/admission gate refuses
    AF while AE is active (hermetic synthetic repositories only);
  - bounded read-only devpts inventory probe (exact `python3 -I -S -c`
    fixed body; 96 slave rows / 65536 B / 5.0 s per probe clamped to the
    same owner END; measured devpts-policy fact; probe-UID binding to the
    frozen owner identity);
  - strict AF record codecs with DISTINCT identity-bearing tag pairs
    (owner-state / native-handoff-prep / native-owner-evidence /
    attach-binding / native-run / native-owner-run-evidence) — original
    AB/AD/default tags, schemas and guards unchanged;
  - one-shot NON-resettable attach-binding phase in the SAME owner/RAM
    context (measured baseline after prepare + separately measured stable
    stop; second bounded observation may derive an expectation only from
    a unique fresh owned allocation with baseline/device/inode/owner/
    namespace coherence; typed refusal/unknown on churn, multiples,
    malformed/oversized rows, stale stop, expiry — no resampling, no
    second baseline);
  - per-subject metadata seam through
    `/proc/<attested-pid>/root/dev/pts` (attested PID/birth-bound frames,
    5.0 s operation cap clamped to the SAME owner END, expiry checked
    before/after blocking reads, typed unknown/refusal on raced/unreadable
    facts);
  - AF registration through its OWN default exact registered-CID native
    channel (caller channel overrides refused) with namespace/device
    verification at the collect-before-commit boundary (no subject
    receipt/baseline/stop change on refusal);
  - coupled fake-world proof with named layers (pure-data / coupled /
    admission-constructor), unequal 1001:1002 positive, same-UID worker
    survivor, global subject-UID trap, isolated `-I -S` startup canaries
    (tiny owned non-Codex children only), and every started test owner
    reaped in finally before monkeypatch teardown.
- Private delivery proofs under `/home/janezp/oap-017ae-work` (dirs 700 /
  files 600 from creation, SAME-shell 077, Python-B; three current-metadata mode exceptions qualified below):
  - Locked gate at B: 13/13 EXIT=0 (see Verification);
  - Actual clean git archive (literal B tree): 200-input EXACT map against
    the manifest at B, whose source binding (source_commit + source_inputs
    + qualification_label) is source A `b7d92b127b0c8257e2d8ecffd2f7a8fd744cf616`
    (the manifest is excluded from its own inputs; source paths are
    unchanged A == B) — missing/extra/mismatched all 0; ALL 17
    `scripts/cache_native*` helper bytes == Git; wheel `1f2ebaff444be1ae90a7f1d863f462abcc82ff28caca448e28c206699fa4b50c`
    (142753 B / 37 entries) byte-identical to manifest; sdist
    `1e0da1f8f54109b7f00158c3bc23012501981c7f0e65cef714786b6a2717d256`
    (1030069 B / 198 entries) == manifest; wheel/source 30-module bytes
    matched 30/30 (archive-wheel-identity-3d7733c1.json);
  - Fresh LOCKED venv (Python 3.12.15; frozen-export closure
    `uv export --frozen --no-dev --no-emit-project --no-hashes` +
    clean-archive B wheel): 18/18 installed distributions at exact lock
    versions (colorama marker-gated-absent on linux); installed27
    functional cases 27/27 + identity OK; ACTUAL fresh-site-packages
    EXACT 30-module set/bytes == wheel == Git
    (fresh-venv-locked-check-3d7733c1.json,
    fresh-module-identity-3d7733c1-locked.json);
  - frozen21 at literal B: 21/21 rc 0, all checks passed, probe hashes
    and assertions unchanged (baseline
    reviews/017-p-probe-hashes.json), with FULL per-probe
    stdout/stderr/exit retained 0600 (probes-final-3d7733c1.json;
    captures under logs/suite-ae22-frozen21/captures/, 63 files).
- Pre-commit fixture regression (development capture, 11 suites): 818
  passed; post-lint focused run: 205 passed.
- Root independent verifications (evidence reviews, not acceptance):
  all 13 gate records at B (strategic
  reviews/017-ae-gate1-completed-review.json); the original 550 test ASTs
  preserved at literal B; gate live-context capture (strategic
  probes/017-ae-gate1-live-context-review.json); archive/fresh/frozen
  against actual retained bytes — complete 200-input map, 17 helpers,
  both artifact sizes/digests/entry counts, exact site/wheel/Git 30
  modules, actual 18 installed lock versions, installed27, frozen21 exact
  source hashes and all 63 full capture/status files (strategic
  reviews/017-ae-archive-fresh-frozen-independent-review.json, all checks
  true); GitHub independently confirms ALL 10 SUCCESS at B.
- Private deviation checkpoints 1-3 under `checkpoints/` (0600):
  checkpoints 1-2 root-reviewed (strategic
  reviews/017-ae-deviation-checkpoint-first-review/ and
  reviews/017-ae-deviation-checkpoint-second-review/); checkpoint 3
  recorded under the same discipline (see Deviations below).

## Verification (at literal head 3d7733c1)
- Locked gate 13/13 EXIT=0, GATE_DONE: lock/sync, Ruff, format, mypy,
  docs, pytest, build, inspect, smoke, version, compileall, prov (build
  before inspect/smoke; explicit frozen-version and compileall steps);
  pytest 3410 passed / 28 skipped (564.09 s); driver umask 077 with
  pytest child only umask 022; non-root UID/GID 1001; all out/err/exit
  precreated 0600 under the 077 parent. Verification by exact driver and
  hashed captures: gate-run-1/gate.sh and every capture are indexed with
  SHA-256 in gate-run-1/gate-run-1-hash-index.json (41 files; every
  per-step exit file reads EXIT=0; summary.log ends GATE_DONE). Root live
  context: gate bash child of 598258 (umask 0077), pytest via uv (umask
  0022), HEAD B clean. Root's earlier AC-template umask-comparison
  suggestion was retracted after reading the accepted AC gate-run-3 (same
  driver-077 / pytest-022 layout); that correction is retained in
  process qualifications.
- CI: ALL 10 implementation checks SUCCESS at
  `3d7733c1f58e92e0a2552e32db0536862887b7d3` (test, docker,
  docker-published, gateway-contract, operator-session,
  cache-native-fixture, cache-native-containment, Analyze (actions),
  Analyze (python), CodeQL); captured check-runs retained in the private
  publication root; GitHub independently confirmed at B.
- Source A vs AD SELF `8489dce`: exactly the 16 paths above; no src/ or
  dependency change (wheel byte-identical on the measured implementation
  line; scripts/ and oap/ excluded from both artifacts by existing
  policy); sdist refreshed with the changed test inputs.
- Historical only (NOT re-run in this round, cited by immutable
  reference): AC report
  `oap/reports/017-ac-owner-uid-native-handoff-integration.md` (29916 B,
  SHA-256 a3fc3a5fcd956140d1915c308f1f0d0cf4e59549647c263419edf03f388eec91:
  gate 13/13 3351P/28S at ded59417; root-independent 9 AC probes 85/85 +
  36 original/AA controls 253/253; archive/fresh/frozen at ded59417); AD
  report `oap/reports/017-ad-owner-uid-native-handoff-qualification.md`
  (11472 B, SHA-256
  fb075eaf87cbb45241337f3a0ececcb41dae9f6141081cfb9f82fb47957d9717:
  PARTIAL pre-admission return; actual AD attempt NOT RUN).

## Scope boundary (NOT done — never waived, never claimed)
- No real AF order/namespace/admission/owner exists or was created; AF
  refusal under AE-active is tested in hermetic synthetic repositories
  only. The AF entry is software-INERT for later strategic activation.
- No Docker/native/client/subject operation in LOCAL AE work; no local
  fixture/admission/model/Gateway operation, no worker stop/signal, no
  host /dev/pts enumeration in product paths, no device write/TIOCSTI,
  no ptrace/prctl, no privilege change, no profile/key/Qwen18020/network
  mutation. (The existing disposable CI jobs ran Docker/Python fixture
  checks under their original scope; no Codex/native CI.)
- NOT native-ready, NOT whole-017 acceptance, NOT v1-runtime delivery, no
  D09/tool/format claim. The actual AD single attempt remains NOT RUN
  (AD closed PARTIAL). Pure D09 collector, required-syntax audit, and ALL
  018-024 remain required and NOT RUN.
- frozen21 child argv was [PY, probe, --head B] without an explicit child
  `-B` (inherited driver shape; probe bytes/assertions unchanged); full
  stdout/stderr are captured; no child-`-B` or clean-stderr claim is made
  beyond the retained bytes.

## Deviations and honest limits (bounded)
- Checkpoint 1 (017-ae-private-deviation-checkpoint-1.md, 7602 B,
  SHA-256 d24236668a4ab6462fbf3ebb1fc23643b67060ae827246239eeabe9e0141da57):
  (a) ONE bounded ACTUAL host `/dev/pts` devpts-inventory read during
  probe debugging (rc 0, 23 rows, namespace [28,1]) — an actual host
  enumeration outside the ordered fixture-namespace/fake-only scope,
  distinct from every fake-seam proof in this round; observed read-only
  in the retained evidence; the full original invocation and wider
  effects are unverified; a bounded search found no identifiable
  inventory capture — NOT proof that no capture exists; not fixture/
  native qualification, no repeat, no credit. (b) Manual /tmp canary
  objects (/tmp/isol-test, /tmp/isol-test4 and retained facts for
  isol-test2/3) preserved AS IS, with measured first objects. (c) Manual
  Python invocations without `-B` (per-invocation bytecode facts
  unmeasured). (d) The first isolation-test variant used the ambient
  environment (scope described accurately; no credential-leak or
  no-inheritance claim made).
- Checkpoint 2 (017-ae-private-deviation-checkpoint-2.md, 1873 B,
  SHA-256 8368f8a39a266459fd19c1569f047aae4ae77c5593024cbe2e4a57a0617035c4):
  bounded wording corrections to checkpoint 1 (search scope; no
  categorical host-mutation-absence claim).
- Checkpoint 3 (017-ae-private-deviation-checkpoint-3.md, 2894 B,
  SHA-256 1ccc4c9a2cd43b2488e9ff8f896169203a14383aa71ca49cbe10c75308d8e92a):
  manual /tmp PR-body retrieval — created under /tmp (4458 B), then moved
  into the protected publication root and chmod 600; original tmp
  inode/mode unmeasured. Qualifications: the recorded mtime is a content
  timestamp, not proven creation time; ctime may reflect the move/copy/
  chmod; the cross-filesystem copy+unlink characterization is inferred
  from differing device numbers, not measured syscall history; the
  destination filename label "at-8489dce" is inaccurate (the fetch
  occurred at post-push head B; the content is the prior AD-era body);
  the file is preserved AS IS and not renamed. Remaining work uses
  protected AE-root files and structured payloads from creation.
- First-version AE verification drivers (setup failures, preserved as
  patches/*-first.py; no qualification credit): missing docstring
  delimiters (archive/frozen), a corrupted short-prefix SHA (module), and
  a self-referential archive provenance line; corrected versions
  regenerated. Distinctly: (a) the archive/locked/module/wheel helpers
  are mechanical path/round adaptations whose control-flow AST is
  identical to the AC originals modulo constants/docstrings; (b) the
  frozen21 v2 runner DELIBERATELY adds per-probe capture control flow
  (precreated 0600 out/err/exit, partial output retained on timeout) on
  top of the inherited runner — all other launch/parse/aggregation logic
  is unchanged, and the FROZEN probe bytes/assertions and the child argv
  are unchanged (baseline reviews/017-p-probe-hashes.json). Root
  first-review of the defective first versions is preserved (strategic
  reviews/017-ae-verification-drivers-first-review).
- frozen21 v2: the inherited AC runner retained only aggregate counts /
  error-tails in memory; the AE v2 runner retains FULL per-probe
  stdout/stderr/exit; the first aggregate-only AE record is preserved
  (probes-final-3d7733c1-first-aggregate-only.json).
- No blanket no-/tmp or no-retention claim: the disclosed /tmp objects
  exist and are preserved AS IS. No self-cleanup of any preserved
  object; the only /tmp file disposition was the PR-body retrieval
  (checkpoint 3: created under /tmp, then moved into the protected root
  and chmod 600).
- Current-metadata mode exceptions (from root's READY final
  current-metadata review; process qualifications, NOT failed final
  tests; all three preserved AS IS — no chmod/recreate/delete, no gate
  rerun): `gate-run-1/gate.sh` 1412 B, mode 0700, uid 1001, SHA-256
  99f25a9ff1d57140d99f7ade30fbd008895e37fc95008c52ad1e1740f7b783b3
  (matches the ordered-script SHA-256 recorded in the root gate review;
  creation mode/command UNKNOWN — no retained chmod evidence);
  `logs/doccheck.out` 52 B, mode 0644, uid 1001, SHA-256
  cbae678d5a59edf3fba46a9d69531d29ba60146e05b406292e8fe821196c0994 and
  `logs/doccheck.err` 0 B, mode 0644, uid 1001, SHA-256
  e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
  (attribution of both doccheck files UNKNOWN). These narrow the
  private-root "files 600 / dirs 700 from creation" shorthand to all
  manual entries except the three above; no final test is affected.
- No historical-creation/umask claim is made from current lstat; no
  raw-content-free claim where retained public/synthetic source exists.

## Preservation and authority
- Closed AA/AB/AC/AD evidence was not modified by this round; prior
  qualifications are kept by the precise immutable report references
  above (AC report, AD report) and by the root review files under
  strategic `reviews/017-ae-*` / `reviews/017-ad-*`, not by a new
  exhaustive recursive preservation audit. AE checkpoints 1-3 and the
  root-retained copies are preserved.
- FIFO law: original strategic FIFOs (inodes 10648021/10648022, 600, uid
  1001) verified unchanged at strategic home; activation OK consumed
  once; no mid-phase control read was created; terminal readers (AD 57103,
  AC 4857, AB 58547) were never polled or replayed; root's sole AE
  response reader (90650 / PID 3227159) remains LIVE (root-owned); the
  next managed control wait is taken after the report-only SELF push.
- SAME RIGHT worker 598258 (parent Bash 2014146, birth 150182858),
  early-beta/xhigh; provider/endpoint rediscovered read-only with matching
  redacted identity; no profile/service/HTTP mutation, no
  endpoint/credential print.
- Whole 017, native readiness, and v1 runtime remain UNACCEPTED / NOT
  RUN; the pure D09 collector, the required-syntax audit, and ALL 018-024
  remain mandatory before full CACHE rework completion. The later actual
  AF qualification is a separate strategically chosen order; pending
  strategic review of this draft is not acceptance.

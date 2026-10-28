# 017-ad round report — owner-UID native handoff qualification (PARTIAL)

Status: PARTIAL. The ordered actual single-attempt native handoff
qualification was NOT RUN: a pre-admission engineering gap (independent
native expectedPTY producer) was found during the required private
preparation, root accepted the gap findings WITH QUALIFICATION, and this
round returns that truthful state. Unmet qualification and unfinished
prescribed verifications are NOT RUN — never PASS, never waived. No LOCAL
test/fixture operation occurred this round: no admission, no local Docker
build/start, no worker stop/signal, no native launch, no local fixture/model
operation, and no source/helper/test/lock/workflow change. The fresh CI jobs
at P ran the existing Docker/Python fixture checks under their original
scope (they may fetch/bake the public native artifact under that scope; no
native/client execution in CI). GitHub and FIFO synchronization did occur
this round, so no blanket no-transport claim is made.

Implementation head SHA: 6bd535b8a633a14c3ee0301662fd7a53cd57b94a
Report publication commit: SELF

## Protocol facts (coding protocol)
- Repository `ulfe-lmi/slaif-local-coding`; PR #25 OPEN at
  https://github.com/ulfe-lmi/slaif-local-coding/pull/25, branch
  `oap/017-cache-read-observation`, base main
  `96c790423f6f0097a56a0b12bacda8a9b6da6aba`. No second PR, no merge, no
  auto-merge (coding law). This report follows the standard round-report
  template of the prior rounds (title, status, required head/publication
  lines).
- Round start: AC report-only SELF
  `a5caf450dc11e10784899d37dfec5299abd91451` (sole parent of P). Literal
  implementation head P
  `6bd535b8a633a14c3ee0301662fd7a53cd57b94a` (order+active only, order
  step 6).
- This report is the single report-only SELF commit on top of P. Fresh CI
  at the report head may be pending after push; strategy verifies it. The
  prepared in-memory post-push remote verifier
  (`verify_self_report_remote_017ad.py`, bound in the private READY) is
  REQUIRED after SELF and has NOT yet been run.
- Setup/privacy/protected fixture: no package/venv/sudo/service change this
  round; no real credential/customer material observed; the round evidence
  contains public/synthetic/seam notes, not a hashes-only universal claim.

## Measured round facts
- Activation: exact control OK (session 70425) consumed once; `oap/active`
  = `017-ad` selects the unique immutable order
  `oap/orders/017-ad-owner-uid-native-handoff-qualification.md`
  (15159 B, SHA-256
  8426367885a5cdabcb4eb5207349ea85c18a8f1802c56b6760f13d538e89a1f0).
- Attempt-head publication (order step 6): commit
  `6bd535b8a633a14c3ee0301662fd7a53cd57b94a` changes EXACTLY `oap/active`
  (7 B, `017-ad\n`, SHA-256
  a991161ab4f5b747c99c6a65d4553e0c32a5d779f570e4bba67cba147e30fa28) and
  the AD order file; sole parent
  `a5caf450dc11e10784899d37dfec5299abd91451` (AC report-only SELF);
  verified remote and clean.
- Private preparation (order steps 1-7, no local test/fixture work):
  governance, SECURITY, TESTING, AC report/decision, and observation
  contract 11c/11k/11l read completely; live GitHub reconciled (clean
  checkout, remote == local before the commit); exact production API
  verification and the expected-PTY seam review saved under the protected
  AD root `/home/janezp/oap-017ad-work` (dirs 700 / files 600 from
  creation, SAME-shell umask 077, mechanically hashed index):
  - `checkpoint/0001-expected-pty-provenance-review.md` (22443 B,
    SHA-256 3815418ce340101a0ccbfb66dd39b31e1b391cc00c710c82cea1b6f4ccc0663e):
    production API map + expected-PTY review and candidate producer;
  - `checkpoint/0002-expected-pty-correction-gap.md` (6540 B,
    SHA-256 70bd8e43fded99d7f2a68bca04e09f899a4ba71b118f47c70aa7ea6aeff51b35):
    corrections per root first review + gap statement;
  - `checkpoint/0003-encode-decode-formula-correction.md` (3126 B,
    SHA-256 ce6f952b2f12dc59bd06b5bc452c8d6c8a5c3760cf164bede7b840a943f9a409):
    corrected kernel encode/decode pair per root second review;
  - `index.json` covering all versions (mechanically measured).
  Root retained exact copies under strategic
  `reviews/017-ad-checkpoint-first-review/` and
  `reviews/017-ad-checkpoint-second-review/`.

## Checkpoint review outcome (root)
- First review (of 0001): 0001 carried a false MKDEV arithmetic plus
  rejected host delta/input/discovery/scope/digest claims; option A (host
  /dev/pts delta as the expected-PTY producer) REJECTED — kernel devpts
  mounts have independent allocation domains; equal device numbers do not
  prove one mount/allocation; nothing binds the host /dev/pts table to the
  fixture's devpts instance. Four corrections accepted: (1) /proc stat field
  7 is the proc encoding new_encode_dev(tty_dev), not the kernel-internal
  MKDEV layout; (2) writing a terminal slave device produces
  master-directed OUTPUT, so the master-side input route is the existing
  authorized tmux send-keys to the verified RIGHT pane with fresh
  foreground/identity checks; (3) native membership authority is the
  owner's OWN guarded top_pids() exact-CID attestation
  (cache_native_fixture_local.py:2687) with per-attested-PID scoped reads
  only — host /proc is never enumerated for native membership (inventory
  law at cache_native_fixture_exec_capability.py:258/:1217); (4) the
  controller diagnostic step emits one final assistant answer with no tool
  call, so its counts/digests are never full read/result/multi-chunk format
  proof (D09 NOT RUN). The mistyped pinned-artifact digest in 0001 §1.6
  (63 hex chars) was corrected mechanically from the immutable constant
  (308139304 B,
  b93f6811d3f653f0fb83be4050d857fb9abbb111dfa2ce160563327daff7f306) at
  docs/CACHE-OBSERVATION-CONTRACT.md:2871-2872.
- Second review (of 0002): the generic encode/decode pair that 0002
  introduced was WRONG; 0003 corrects it to the kernel pair
  (include/linux/kdev_t.h) with two arithmetic counterexamples (136:256 ->
  1083392, not 35072; encoded 262144 major 1024, not 0), verified by root
  as pure arithmetic against the primary source.
- Final: core PRE-ADMISSION GAP findings ACCEPTED WITH QUALIFICATION
  (never actual-plan approval); the 0003 "20+20 layout" wording is
  omitted here (only MINORBITS 20 is established); no further checkpoint
  revision, no fourth checkpoint; all versions preserved.

## Pre-admission gap (the binding finding)
The required INDEPENDENT native expectedPTY producer — expected-PTY
provenance from the registered/owned attach (NEVER from the subject
itself), represented under the corrected proc encoding and compared
against the measured native tty_nr — remains an engineering gap. The
existing seams cannot prove it: ci.pty_attach_on proves only a separate
completed Python stand-in PTY and returns no reusable native TTY binding;
no existing producer binds the native attach to an expected tty value.
No runnable full operator was written; no actual attempt was made. A
separate continuation (inert candidate design, strategic
`drafts/017-ae-native-PTY-provenance-candidate-planned.md`) may add an
independent fixture-namespace producer through the EXISTING guarded
channel while preserving direct RIGHT startup; that is a separate later
order, not this round.

## NOT RUN (never PASS, never waived)
- Actual single AD attempt: admission/launch, owner preparation, worker
  stop/restore and job provenance, native launch in RIGHT, subject
  registration/measurement (current exe bytes under 320 MiB / 10 s / owner
  END), expected/actual PTY bind and compare, convergence/cleanup/sentinel
  survival, SAME-job restoration, and the publication ordering (native
  owner evidence FIRST / terminal record SECOND / finalization LAST) —
  all NOT RUN.
- The prescribed actual-attempt verifications above are NOT RUN.
- The prescribed local locked gate at the final committed head (lock/sync,
  Ruff, format, mypy, docs, pytest, build, inspect, install-smoke,
  frozen-version, compileall, provenance) and the archive / fresh-install /
  functional / frozen controls are NOT RUN locally in AD; they remain
  required and are never waived. Product docs were not updated because this
  is a pre-admission return with no behavior implementation; the required
  qualification/verification remains incomplete. The historical AC proofs
  below are cited as historical only, and the fresh P CI success above is
  separate from them.

## Source state and CI at literal head 6bd535b
- Source unchanged vs AC SELF: the tracked-tree diff of the AD commit
  against the AC report-only SELF
  `a5caf450dc11e10784899d37dfec5299abd91451` (P's sole parent) changes
  EXACTLY `oap/active` + the AD order file (verified by diff; root
  reproduction in `reviews/017-ad-publication-first-review/facts.json`).
  Against the AC implementation head
  `ded59417dfca91b9d7541a5a17d4b8692729aa28` the same tracked-tree diff
  additionally contains the AC report path added by that SELF commit.
  Product source/docs/tests/helpers/manifest are unchanged vs `ded59417`;
  every other tracked path is identical to AC SELF `a5caf450`.
- CI: ALL 10 implementation checks SUCCESS at
  `6bd535b8a633a14c3ee0301662fd7a53cd57b94a` (test, docker,
  docker-published, gateway-contract, operator-session,
  cache-native-fixture, cache-native-containment, Analyze (actions),
  Analyze (python), CodeQL).
- Historical only (NOT re-run in this round): AC locked gate 13/13
  (3351 passed / 28 skipped at ded59417), root-independent 9 AC probes
  85/85, 36 original X/Y + AA controls 253/253, clean-archive 200-input
  exact map, fresh locked venv 18/18 + installed27 + actual-site 30,
  frozen21 21/21 — see the immutable AC report
  `oap/reports/017-ac-owner-uid-native-handoff-integration.md` (29916 B,
  SHA-256 a3fc3a5fcd956140d1915c308f1f0d0cf4e59549647c263419edf03f388eec91)
  and the AC decision.

## Deviations and honest limits (bounded)
- Checkpoint occurrence attribution: 0001 contained the false MKDEV
  arithmetic and the rejected host delta/input/discovery/scope/digest
  claims; 0002 carried the accepted gap/scope corrections but introduced
  the wrong generic encode/decode pair; 0003 corrected that pair. All
  versions preserved, nothing overwritten; the 0003 "20+20 layout" wording
  is omitted from all final assertions.
- No /tmp or other outside-root manual files were created this round.
- AC closed evidence (actual-audit known-0664 generated archive;
  corrected first-selftest umask inference) remains disclosed in the AC
  report and is not repaired for labels.

## Preservation and authority
- Closed AA/AB/AC evidence was not modified BY THIS ROUND; prior
  qualifications are kept by the precise immutable report references above
  (AA/AB/AC round reports), not by a new exhaustive recursive preservation
  audit. AD checkpoint versions 0001-0003 and the root-retained copies are
  preserved.
- FIFO law: original strategic paths (inodes 10648021/10648022, 600,
  uid 1001); activation OK consumed once; no mid-phase control read was
  created; root's sole AD response reader (57103 / PID 3160821) remains
  blocked until this report.
- Whole 017, native readiness, and v1 runtime remain UNACCEPTED / NOT
  RUN; the pure D09 collector, the required-syntax audit, and ALL
  018-024 remain required. The 017-ae PTY-producer implementation is a
  separate later order.
- One bounded PARTIAL result is not generic native readiness, whole-017
  acceptance, or v1 runtime delivery.
